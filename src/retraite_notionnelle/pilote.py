"""Le pilote (docs/architecture.md, § 7.7) : ce que le droit ne décide pas.

Le moteur ne devine rien : il liquide la demande qu'on lui fait. Hors de lui,
un pilote fixe le reste.

* LES COMPORTEMENTS : partir au taux plein, à l'âge où le droit s'ouvre,
  après une durée de services. :func:`age_de_depart` interroge le moteur, au
  besoin plusieurs fois, jusqu'à un point fixe ; il ne lui faut qu'un âge, et
  il n'interroge donc que l'étape « ouvrir le droit »
  (:func:`~retraite_notionnelle.droit.ouvrir.age_ouverture_droit`,
  :func:`~retraite_notionnelle.droit.ouvrir.age_taux_plein_droit`), sans rien
  liquider. La date qu'il trouve devient celle du départ de la carrière, que
  l'échéancier traite (:mod:`~retraite_notionnelle.echeancier`). Les mêmes
  points fixes datent les trois départs que « Mon estimation retraite »
  chiffre, pour la carrière d'une saisie (:func:`ages_de_l_estimation`), que
  :func:`depart_estime` liquide étage par étage.
* LES POPULATIONS : aujourd'hui les cas types pondérés, que
  :mod:`~retraite_notionnelle.castypes` décrit ; des tirages, des couples et
  des décès simulés demain, sans changer le moteur.
* LES CASCADES de neutralisations, et les paramètres qui dépendent d'une
  population — le coefficient d'équilibre, que la page Coût calcule sans
  l'appliquer — restent dans leurs modules
  (:mod:`~retraite_notionnelle.avantages`, :mod:`~retraite_notionnelle.cout`).

Son jumeau est ``moteur/js/pilote.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable

from .droit import ouvrir
from .remuneration import charger_prelevements

if TYPE_CHECKING:
    from .carriere import Carriere
    from .castypes import CasType
    from .config import Parametres
    from .simulateur import Simulateur


#: Les deux façons de dater le départ d'un cas type.
#:
#: ``droit`` est celle des résultats affichés : chaque génération liquide à
#: l'âge que SON droit lui ouvre. ``absolu`` est l'ancienne, gardée non comme
#: repli mais comme variante — l'âge écrit dans la grille, le même pour toutes
#: les générations, qui faisait partir la génération 1940 à soixante-quatre ans
#: en 2004 alors que la loi ne les lui a jamais demandés.
VARIANTES_LIQUIDATION: tuple[str, ...] = ("droit", "absolu")

#: Nombre de fois que l'âge de liquidation est rapproché de l'âge d'ouverture.
#: Il en faut plus d'une : l'âge qu'une fiche de régime oppose dépend de
#: l'ANNÉE de liquidation — celle de la SNCF et celle des IEG montent d'un
#: trimestre par millésime —, si bien que déplacer l'âge déplace la réponse.
#: Deux passes suffisent partout dans la grille ; les deux autres sont la marge.
PASSES_LIQUIDATION = 4


def age_de_depart(simulateur: Simulateur, cas: CasType, generation: int,
                  variante: str = "droit") -> float:
    """L'âge auquel le cas type ``cas`` liquide, étant née en ``generation``.

    **Pourquoi ce n'est pas un nombre.** Un cas type décrit une carrière,
    pas une date : « le salarié au salaire moyen » n'est pas « celui qui
    part à soixante-quatre ans », c'est celui qui part quand la loi le lui
    permet. Écrire l'âge revenait à faire partir à soixante-quatre ans une
    génération née en 1940 — c'est-à-dire en 2004, sous un droit qui en
    demandait soixante —, et à donner au modèle un stock de retraités trop
    vieux au départ de la projection, donc trop rapide à croître.

    **Comment la réponse est trouvée.** L'âge d'ouverture dépend de la
    carrière, laquelle dépend de l'âge de liquidation : la question tourne
    en rond, et on la résout par un POINT FIXE. On part de l'âge écrit, on
    demande au scénario 1 ce que le droit oppose à cette liquidation-là, on
    recommence. Deux garde-fous : le nombre de passes est borné, et une
    descente n'est retenue que si l'âge plus précoce est lui-même ouvert.
    Le second n'est pas décoratif — la CANCAVA ouvrait à soixante-cinq ans
    jusqu'en 1972 et à soixante à partir de 1973, si bien qu'un artisan né
    en 1910 « ouvre » à soixante ans un droit que son année de départ lui
    refuse. Dans ce cas la règle ne descend pas plus bas que l'âge que ce
    départ-là confirme, et reste où elle est s'il n'y en a pas de plus
    précoce.
    """
    if variante not in VARIANTES_LIQUIDATION:
        raise ValueError(
            f"variante de liquidation inconnue : {variante!r} "
            f"(attendu : {VARIANTES_LIQUIDATION})"
        )
    if variante == "absolu":
        return cas.age_liquidation
    if cas.regle_liquidation == "services":
        return cas.age_debut + cas.ecart_liquidation
    if cas.regle_liquidation not in ("ouverture", "taux_plein"):
        raise ValueError(
            f"règle de liquidation inconnue : {cas.regle_liquidation!r}"
        )
    return point_fixe(cas.age_liquidation,
                      lambda age: age_propose(simulateur, cas, generation, age))


def point_fixe(age: float, proposer: Callable[[float], float | None]) -> float:
    """L'âge que ``proposer`` confirme, en partant de ``age`` : la boucle
    de :func:`age_de_depart`, que :func:`ages_de_l_estimation` emprunte.

    ``proposer(age)`` dit ce que le droit oppose à la carrière liquidée à
    ``age``, ou ``None`` s'il n'oppose rien. Une montée se suit ; une
    descente ne se retient que si l'âge plus précoce se confirme lui-même ;
    le nombre de passes est borné (:data:`PASSES_LIQUIDATION`).
    """
    for _ in range(PASSES_LIQUIDATION):
        propose = proposer(age)
        if propose is None or abs(propose - age) < 1e-9:
            break
        if propose > age:
            age = propose
            continue
        confirme = proposer(propose)
        if confirme is None:
            break
        if confirme > propose + 1e-9:
            # L'âge plus précoce n'est pas ouvert sous SES règles, mais le
            # droit peut s'ouvrir entre les deux : depuis la suspension de
            # 2026, la durée opposable dépend de la date d'effet, et un né
            # en 1965 que la règle de 2027 ferait partir à 60 ans et 9 mois
            # part à 61 ans sous celle de 2026. On essaie donc l'âge que le
            # droit oppose alors, s'il reste plus précoce que l'âge retenu.
            if confirme < age - 1e-9:
                age = confirme
                continue
            break
        age = propose
    return age


#: Les départs que « Mon estimation retraite » chiffre, dans l'ordre de sa
#: synthèse : au plus tôt — l'âge légal, ou la carrière longue qui le
#: devance —, au taux plein, au taux plein automatique.
DEPARTS_DE_L_ESTIMATION: tuple[str, ...] = ("legal", "taux_plein", "automatique")


def ages_de_l_estimation(actuel, batir: Callable[[float], "Carriere"],
                         depart: float) -> dict[str, float] | None:
    """Les trois âges de « Mon estimation retraite », pour la carrière que
    ``batir(age)`` rend liquidée à ``age`` : au plus tôt
    (:func:`~retraite_notionnelle.droit.ouvrir.age_ouverture_droit`), au
    taux plein (:func:`~retraite_notionnelle.droit.ouvrir.age_taux_plein_droit`),
    au taux plein automatique
    (:func:`~retraite_notionnelle.droit.ouvrir.age_annulation_droit`).

    Chacun est un point fixe, comme le départ d'un cas type : la carrière
    dépend de l'âge, et ce que le droit lui oppose dépend de la carrière. Le
    premier part de ``depart``, l'âge que la saisie demande ; chacun des
    suivants part du précédent, et ne le précède jamais. Deux âges peuvent
    se confondre : la page les réunit. ``None`` quand le droit n'oppose
    aucun âge à cette carrière.
    """
    # Les trois règles répondent `None` dans le même cas : aucun régime
    # retenu. Une question suffit donc à le savoir.
    if ouvrir.age_ouverture_droit(actuel, batir(depart)) is None:
        return None
    regles = (ouvrir.age_ouverture_droit, ouvrir.age_taux_plein_droit,
              ouvrir.age_annulation_droit)
    ages: dict[str, float] = {}
    age = depart
    for quoi, regle in zip(DEPARTS_DE_L_ESTIMATION, regles):
        trouve = point_fixe(age, lambda a, regle=regle: regle(actuel, batir(a)))
        age = max(age, trouve) if ages else trouve
        ages[quoi] = age
    return ages


@dataclass(frozen=True)
class DepartEstime:
    """Un départ de « Mon estimation retraite », tel que le scénario 1 le sert.

    Les montants sont bruts, annuels, en euros constants de l'année de
    référence : la page les divise par douze. ``etages`` additionne, étage
    par étage (base, complémentaire, intégré, additionnel), la pension de
    chaque régime, minima compris, et la part qu'il sert de la majoration
    pour enfants. Le minimum vieillesse, qu'aucun régime ne sert et que
    l'estimation ignore, reste à part.
    """

    #: Les âges de :data:`DEPARTS_DE_L_ESTIMATION` que ce départ réunit.
    quoi: tuple[str, ...]
    age: float
    #: Le mois du départ, « AAAA-MM ».
    date: str
    etages: dict[str, float]
    minimum_vieillesse: float
    trimestres: int
    trimestres_requis: int
    motif_ouverture: str
    #: Ce que la cotisation maladie de 1 % frappe dans :attr:`etages` : les
    #: lignes des complémentaires qui la prélèvent, sans leur majoration pour
    #: enfants (``remuneration.assiette_maladie``).
    assiette_maladie: float = 0.0
    #: La pension de base du régime général, qu'un non-résident paie à son
    #: propre taux (L. 131-9 ; D. 242-8).
    assiette_regime_general: float = 0.0

    @property
    def total(self) -> float:
        # De gauche à droite, comme le jumeau : la somme de Python 3.12 est
        # compensée, et différerait au dernier chiffre.
        total = 0.0
        for montant in self.etages.values():
            total += montant
        return total


def depart_estime(simulateur: Simulateur, parametres: Parametres, carriere: Carriere,
                  quoi: str) -> DepartEstime:
    """Le départ ``quoi`` de « Mon estimation retraite » : la carrière liquidée
    à l'âge que :func:`ages_de_l_estimation` a trouvé, chiffrée étage par étage
    en euros constants de l'année de référence. Le site chiffre ainsi chaque
    départ (``departEstime``, ``moteur/js/contexte.js``) ; ici, sans la saisie,
    que le portage seul garde (action 161, étape 6), il ne sert qu'à confronter
    les deux moteurs (``tests/test_estimation_du_site.py``)."""
    resultat = simulateur.echeancier(carriere).au_depart
    passage = simulateur.macro.coefficient_prix(
        carriere.annee_liquidation, parametres.annee_euros_constants)
    etages: dict[str, float] = {}
    prelevements = charger_prelevements(parametres.racine_donnees).pensions
    regimes = prelevements.regimes_maladie
    assiette = generale = 0.0

    def porter(code: str, montant: float) -> None:
        etage = simulateur.catalogue[code].etage
        etages[etage] = etages.get(etage, 0.0) + montant * passage

    for pension in resultat.pensions_par_regime:
        porter(pension.regime, pension.montant)
        if pension.regime in regimes:
            assiette += pension.montant * passage
        if pension.regime in prelevements.regimes_generaux:
            generale += pension.montant * passage
    minimum = 0.0
    for avantage in resultat.avantages_appliques:
        if avantage.code == "majoration_enfants":
            for code, part in avantage.par_regime:
                porter(code, part)
        elif avantage.code == "minimum_vieillesse":
            minimum += avantage.montant
    date = carriere.date_liquidation
    return DepartEstime(
        quoi=(quoi,), age=carriere.age_liquidation,
        date=f"{date.annee:04d}-{date.mois:02d}", etages=etages,
        minimum_vieillesse=minimum * passage,
        trimestres=resultat.trimestres_valides,
        trimestres_requis=resultat.trimestres_requis,
        motif_ouverture=resultat.motif_ouverture,
        assiette_maladie=assiette,
        assiette_regime_general=generale,
    )


def age_propose(simulateur: Simulateur, cas: CasType, generation: int,
                age: float) -> float | None:
    """Ce que la règle du cas type oppose à sa carrière liquidée à ``age``,
    décalé : la seule question que le pilote pose au moteur, à l'étape
    « ouvrir le droit », sans rien liquider."""
    actuel = simulateur.scenario_actuel
    carriere = cas._carriere(simulateur, generation, age)
    reference = (
        ouvrir.age_taux_plein_droit(actuel, carriere)
        if cas.regle_liquidation == "taux_plein"
        else ouvrir.age_ouverture_droit(actuel, carriere)
    )
    return None if reference is None else reference + cas.ecart_liquidation
