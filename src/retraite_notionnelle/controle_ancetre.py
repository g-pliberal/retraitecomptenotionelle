"""Le niveau de pension des cas types, contrôlé sur Ancetre, régime principal par régime principal.

CE QUE LA PAGE COÛT NE CONTRÔLAIT PAS. Elle pèse les cas types par les
effectifs de leur caisse et cale la masse de 2024 sur la dépense observée
(l'ancrage de ``cout.py``) : le NIVEAU de pension de chaque cas type n'y
entrait que par ses rapports aux autres, et rien ne le confrontait à la
pension réellement servie. Ancetre, la microsimulation statique de la DREES
calée sur l'EACR, la donne pour des personnes, non des caisses : la pension
brute moyenne de droit direct, tous régimes, selon le régime où le retraité a
fait plus de la moitié de sa carrière, fin 2024, pour tous les retraités et
pour ceux à carrière complète (rapport annuel du COR de juin 2026, tableau
3.2 ; ``tests/temoins/cor_pension_regime_principal_2026.json``,
``scripts/fetch/cor_pension_regime_principal.py``).

LA MESURE. Chaque cas type de la grille sert, en 2024, la pension de ses
cohortes déjà parties — cinq par génération de la grille, du ``-_DEMI_TRANCHE``
au ``+_DEMI_TRANCHE`` —, revalorisée depuis leur liquidation comme les masses
la revalorisent (:func:`~.cout.coefficient_servi`) et portée à leur
complétude ; sa pension moyenne pèse chaque cohorte de son effectif vivant
cette année-là, comme :func:`~.cout._masses_regimes` (:func:`pensions_mensuelles`).
Le scénario 1, en euros de 2024, par mois. Les cas types se rangent ensuite
sous le régime principal de leur caisse (:data:`REGIME_PRINCIPAL`) et s'y
moyennent au poids que la page leur donne la dernière année observée
(:func:`par_regime_principal`).

CE QUE LA CONFRONTATION PEUT DIRE, ET CE QU'ELLE NE PEUT PAS. La grille ne
porte que des carrières entières, sauf la carrière interrompue : la colonne
qui se compare est celle des carrières complètes ; celle de tous les
retraités dit ce que les carrières courtes, que la grille n'a pas, retirent.
Un régime y est représenté par un seul cas type, ou par quatre au régime
général, quand Ancetre moyenne tous ses retraités : un écart dit d'abord
qu'un cas type n'est pas son régime, ce que la population de l'étape 14
corrigera, et seulement ensuite qu'une règle serait fausse. C'est la mesure
du « biais de l'individu moyen » que Pablo chiffre pour l'État (registre,
``pablo``). Les poids sont des têtes de caisse, où un polypensionné compte
deux fois (limite n° 1 de ``cout.py``) ; Ancetre compte des personnes.
Rien de ce module n'entre dans un chiffre de la page.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .somme import somme_ordonnee

#: L'année que le tableau 3.2 du rapport de 2026 décrit.
ANNEE_ANCETRE = 2024

#: Le régime principal de chaque caisse de la grille, sous les clés du témoin.
#: Les artisans et commerçants sont au régime général depuis 2020 (renvoi 1
#: du tableau) ; le contractuel de la fonction publique y est aussi, l'Ircantec
#: n'étant que sa complémentaire ; la SNCF et les IEG sont des « régimes
#: spéciaux » (renvoi 3).
REGIME_PRINCIPAL: dict[str, str] = {
    "cnav": "regime_general",
    "rci_complementaire": "regime_general",
    "ircantec": "regime_general",
    "fonction_publique_etat_civile": "fpe_civils",
    "fonction_publique_etat_militaire": "fpe_militaires",
    "cnracl": "cnracl",
    "sncf": "regimes_speciaux",
    "cnieg": "regimes_speciaux",
    "msa_exploitants": "msa_non_salaries",
    "cnavpl": "professions_liberales",
}

#: La ligne de toute la grille, sous la clé du témoin.
ENSEMBLE = "ensemble"


def pensions_mensuelles(pensionnes, population, revalorisation, vers_euros_annee: float,
                        annee: int = ANNEE_ANCETRE) -> dict[str, float]:
    """La pension mensuelle moyenne de chaque cas type en ``annee``, en euros
    de cette année : ses cohortes déjà liquidées, pesées de leur effectif
    vivant. ``vers_euros_annee`` passe des euros constants du modèle à ceux de
    ``annee``. Un cas type sans cohorte partie est absent."""
    from .cout import _DEMI_TRANCHE, coefficient_servi

    tetes: dict[str, list[float]] = {}
    euros: dict[str, list[float]] = {}
    for pensionne in pensionnes:
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            liquidation = pensionne.annee_liquidation + decalage
            if annee < liquidation:
                continue
            effectif = population.effectif(annee - pensionne.generation - decalage, annee)
            if effectif <= 0.0:
                continue
            pension = (pensionne.pensions["actuel"] * pensionne.completude(decalage)
                       * coefficient_servi(pensionne.parts_regimes, revalorisation,
                                           liquidation, annee))
            tetes.setdefault(pensionne.code, []).append(effectif)
            euros.setdefault(pensionne.code, []).append(effectif * pension)
    return {code: somme_ordonnee(euros[code]) / somme_ordonnee(tetes[code])
            * vers_euros_annee / 12.0
            for code in sorted(tetes)}


def par_regime_principal(pensions: Mapping[str, float], poids: Mapping[str, float],
                         caisses: Mapping[str, str]) -> dict[str, float]:
    """La pension moyenne de chaque régime principal, ses cas types pesés de
    leur poids, et celle de toute la grille sous :data:`ENSEMBLE`. ``caisses``
    donne la caisse de chaque cas type ; une caisse sans régime principal
    connu lève, pour qu'un cas type neuf ne sorte pas du contrôle sans bruit."""
    groupes: dict[str, list[tuple[float, float]]] = {}
    for code, pension in pensions.items():
        part = poids.get(code, 0.0)
        if part <= 0.0:
            continue
        caisse = caisses[code]
        if caisse not in REGIME_PRINCIPAL:
            raise KeyError(f"{code} : la caisse {caisse!r} n'a pas de régime principal")
        for ligne in (REGIME_PRINCIPAL[caisse], ENSEMBLE):
            groupes.setdefault(ligne, []).append((part, pension))
    return {ligne: somme_ordonnee(p * m for p, m in membres) / somme_ordonnee(p for p, _ in membres)
            for ligne, membres in sorted(groupes.items())}


@dataclass(frozen=True)
class Ecart:
    """Un régime principal : la pension de la grille et celles d'Ancetre."""

    ligne: str
    modele: float
    carriere_complete: float
    tous: float

    @property
    def rapport(self) -> float:
        """La grille sur Ancetre, carrières complètes."""
        return self.modele / self.carriere_complete

    @property
    def rapport_tous(self) -> float:
        """La grille sur Ancetre, tous les retraités."""
        return self.modele / self.tous


def confronter(modele: Mapping[str, float], temoin: Mapping) -> list[Ecart]:
    """Chaque régime principal que la grille représente, contre le tableau 3.2,
    ensemble des deux sexes ; l'ensemble en tête."""
    publie = temoin["pensions"]
    ordre = [ENSEMBLE] + sorted(ligne for ligne in modele if ligne != ENSEMBLE)
    return [Ecart(ligne, modele[ligne],
                  publie[ligne]["carriere_complete"]["ensemble"],
                  publie[ligne]["tous"]["ensemble"])
            for ligne in ordre if ligne in modele]


def controle(parametres=None) -> tuple[dict[str, float], dict[str, float]]:
    """Sous ces paramètres, sur les données du dépôt : la pension de chaque
    cas type en 2024 et celle de chaque régime principal. La grille et les
    poids sont ceux de la page Coût, que la mémoire des calculs garde."""
    from . import Parametres, memoire
    from . import cout as module
    from .castypes import CAS_TYPES
    from .donnees.population import Population
    from .simulateur import Simulateur

    parametres = parametres if parametres is not None else Parametres()
    simulateur = Simulateur(parametres)
    # La clé de ``memoire.cout`` pour sa grille : la même mémoire sert aux deux.
    pensionnes, _ = memoire.memoriser_pour(
        parametres, ("grille_du_cout", parametres, CAS_TYPES, "droit"),
        lambda: module._pensionnes(simulateur, CAS_TYPES, "droit"))
    cout = memoire.cout(parametres)
    # La règle d'indexation de la page, depuis la plus ancienne liquidation.
    revalorisation = module.RevalorisationServie(
        simulateur.pour_la_projection(),
        min(p.annee_liquidation for p in pensionnes) - module._DEMI_TRANCHE,
        module.HORIZON)
    pensions = pensions_mensuelles(
        pensionnes, Population(parametres.racine_donnees, parametres.hypothese_esperance_vie),
        revalorisation,
        simulateur.macro.coefficient_prix(parametres.annee_euros_constants, ANNEE_ANCETRE))
    caisses = {cas.code: cas.caisses[0] for cas in CAS_TYPES if cas.caisses}
    return pensions, par_regime_principal(pensions, cout.poids, caisses)
