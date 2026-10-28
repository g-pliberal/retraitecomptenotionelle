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
  l'échéancier traite (:mod:`~retraite_notionnelle.echeancier`). Le même
  point fixe, dans le portage, date les trois départs que « Mon estimation
  retraite » chiffre pour la carrière d'une saisie (``agesDeLEstimation``,
  ``moteur/js/pilote.js``) : seul le site les chiffre.
* LES POPULATIONS : aujourd'hui les cas types pondérés, que
  :mod:`~retraite_notionnelle.castypes` décrit ; des tirages, des couples et
  des décès simulés demain, sans changer le moteur.
* LES CASCADES de neutralisations, et les paramètres qui dépendent d'une
  population — le coefficient d'équilibre, que la page Coût calcule sans
  l'appliquer — restent dans leurs modules
  (:mod:`~retraite_notionnelle.avantages`, :mod:`~retraite_notionnelle.cout`).

Son jumeau, ``moteur/js/pilote.js``, ne porte que :func:`point_fixe` : le
départ des cas types, que seul le coût demande, ne tourne qu'ici. Les départs
de l'estimation n'ont que l'exemplaire du portage depuis l'action 161,
étape 6 : leur moitié Python ne servait plus qu'à confronter les deux moteurs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from .droit import ouvrir

if TYPE_CHECKING:
    from .castypes import CasType
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
#: Elles ne suffisent pas à une carrière qui ne valide plus, que
#: :func:`age_de_depart` reprend de l'âge d'annulation de la décote quand elle
#: monte, et d'un an plus tôt quand elle descend (:func:`descendre`).
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
    départ-là confirme ; le point fixe, qui ne sonde que les âges que le
    droit propose, le laissait à soixante-quatre ans, l'âge écrit, et c'est
    la descente d'un an en un an qui trouve 1973, à soixante-trois ans.

    **Le taux plein d'une carrière qui ne valide plus.** Le droit date la
    durée requise comme si la carrière validait encore quatre trimestres par
    an (:func:`~retraite_notionnelle.droit.ouvrir.age_taux_plein_droit`) :
    sans activité, à deux trimestres de sa durée, elle montait d'un semestre
    à chaque passe sans en gagner aucun, et le pilote la laissait au bout des
    siennes avant l'âge d'annulation, avec la décote que sa règle lui refuse
    — un salarié né en 1955 partait à 66 ans au taux de 48,75 %. Quand la
    montée s'arrête sur un âge où la carrière n'a pas le taux plein, la
    recherche reprend donc de l'âge d'annulation de la décote, où le droit le
    sert sans condition de durée
    (:func:`~retraite_notionnelle.droit.ouvrir.age_annulation_droit`), et
    descend comme toute autre jusqu'à l'âge où la carrière a sa durée, s'il
    en est un avant lui (action 138, étape 14).

    **La descente.** Le point fixe ne sonde que les âges que le droit
    propose : il manque le départ plus précoce que le droit ouvre sans le
    proposer. Le droit date la durée cotisée de la carrière longue comme celle
    du taux plein, comme si la carrière cotisait encore
    (:meth:`~retraite_notionnelle.scenarios.actuel.CarriereLongue.age_propose`) :
    sans activité depuis qu'elle a sa durée, liquidée à tout âge, elle la
    réunit à l'âge même du départ, et le point fixe reste là d'où il part — né
    en 1966, entré à seize ans et sans activité depuis ses 59 ans, un salarié
    partait à 64 ans, l'âge écrit, quand la carrière longue lui ouvre 60 ans au
    taux plein ; avec un trimestre de trop, il ne descend que d'un trimestre
    par passe. Et l'âge que le droit propose peut précéder celui où ses
    conditions sont réunies : le super-actif polypensionné de la population,
    entré dans son corps après dix ans de privé, n'a ses services qu'à 59 ans,
    quand le droit lui oppose 57 ans à tout âge plus tardif, et le point fixe
    le laissait à 65 ans. Le point fixe fait, la recherche reprend donc d'un
    an plus tôt tant que le départ s'y ouvre (:func:`descendre`), comme celle
    du premier âge de « Mon estimation retraite » (``agesDeLEstimation``,
    ``moteur/js/pilote.js``).
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
    proposes: dict[float, float | None] = {}

    def proposer(age: float) -> float | None:
        if age not in proposes:
            proposes[age] = age_propose(simulateur, cas, generation, age)
        return proposes[age]

    age = point_fixe(cas.age_liquidation, proposer)
    if cas.regle_liquidation == "taux_plein":
        propose = proposer(age)
        if propose is not None and propose > age + 1e-9:
            annulation = age_annulation(simulateur, cas, generation, age)
            if annulation is not None:
                age = point_fixe(annulation, proposer)
    return descendre(age, proposer)


def descendre(age: float, proposer: Callable[[float], float | None]) -> float:
    """Le départ le plus précoce que ``proposer`` ouvre sous ``age`` : tant
    qu'un départ un an plus tôt s'ouvre — le droit lui oppose un âge qui ne le
    dépasse pas, qu'il se confirme ou non —, la recherche en reprend
    (:func:`point_fixe`). C'est la boucle du premier âge d'``agesDeLEstimation``
    (``moteur/js/pilote.js``), que :func:`age_de_depart` reprend."""
    while True:
        essai = point_fixe(age - 1.0, proposer)
        if essai >= age - 1e-9:
            return age
        confirme = proposer(essai)
        if confirme is None or confirme > essai + 1e-9:
            return age
        age = essai


def point_fixe(age: float, proposer: Callable[[float], float | None]) -> float:
    """L'âge que ``proposer`` confirme, en partant de ``age`` : la boucle
    de :func:`age_de_depart`, que son jumeau, ``pointFixe``, prête dans le
    portage aux départs de « Mon estimation retraite ».

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


def age_annulation(simulateur: Simulateur, cas: CasType, generation: int,
                   age: float) -> float | None:
    """L'âge d'annulation de la décote que le droit oppose à la carrière du
    cas type liquidée à ``age``, décalé comme :func:`age_propose` décale le
    sien : celui d'où :func:`age_de_depart` reprend une montée arrêtée."""
    carriere = cas._carriere(simulateur, generation, age)
    annulation = ouvrir.age_annulation_droit(simulateur.scenario_actuel, carriere)
    return None if annulation is None else annulation + cas.ecart_liquidation
