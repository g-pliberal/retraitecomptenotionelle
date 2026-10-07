"""Le bilan des quatre systèmes, figé sous les réglages de référence.

POURQUOI CE FICHIER EXISTE. Le coefficient d'équilibre d'un système est un
rapport de MASSES : ce que le système encaisse une année, sur ce qu'il verse
cette année-là. Le calculer suppose donc la grille entière des cas types
simulée sous chaque système, pondérée par les effectifs de l'INSEE, année par
année jusqu'en 2070 — dix-huit secondes de calcul. C'est le prix de la page
Coût, et elle le paie une fois.

La page des résultats du simulateur ne peut pas le payer : elle est la page
d'entrée du site, elle se recalcule à chaque changement de champ, et elle
tourne dans le navigateur du lecteur. Or elle a besoin du même coefficient —
c'est lui qui dit ce que les comptes financent de la pension qu'elle affiche.
D'où cette table : le bilan est calculé UNE FOIS, par
``scripts/construire_donnees.py``, écrit dans ``data/derive/equilibre.json``,
embarqué dans le paquet que le navigateur charge, et relu à l'identique des
deux côtés du portage.

« Pourquoi changer » et « Partager » la lisent aussi, depuis le 7 octobre 2026.
Elles ne prennent aucun réglage, et refaisaient le coût entier chez le lecteur —
cinq secondes — pour y lire la dépense, la recette et le solde de quelques
années : la table porte donc la dépense et le PIB de chaque année, et les trois
carrières d'exemple de « Pourquoi changer » (:class:`ExempleFige`).

CE QUE LE FIGEAGE COÛTE, ET IL FAUT LE DIRE. La table est calculée sous les
réglages de RÉFÉRENCE — ceux de ``Parametres()``. Le coefficient du système
actuel n'en dépend pas : il est le rapport des ressources aux dépenses que le
COR publie, et aucun réglage du simulateur ne le déplace. Les trois autres, si :
leur dépense est une masse de pensions notionnelles, qui bouge avec la règle
d'indexation ou la table de mortalité. La page le dit en toutes lettres plutôt
que de laisser croire qu'un coefficient suit les cases qu'on coche, et la page
Coût, elle, recalcule tout sous les réglages demandés.

STRUCTURELLEMENT IDENTIQUE À ``cout.Solde``. ``financer`` ne fait aucune
différence entre les deux : mêmes accesseurs, mêmes unités — la part de PIB
partout. C'est délibéré, et c'est ce qui garantit que la table figée et le
calcul complet ne peuvent pas dire deux choses.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class AnneeBilan:
    """Une année du bilan figé, dans l'unité du COR : la part de PIB."""

    annee: int
    #: Le COR projette-t-il cette année plutôt qu'il ne l'observe ?
    projete: bool
    #: Part des ressources assise sur un revenu d'activité — la seule sur
    #: laquelle une hausse de taux ait prise.
    part_contributive: float
    _coefficients: dict[str, float] = field(default_factory=dict)
    _soldes: dict[str, float] = field(default_factory=dict)
    _ressources: dict[str, float] = field(default_factory=dict)
    _depenses: dict[str, float] = field(default_factory=dict)
    #: Le PIB de l'année, en millions d'euros courants, s'il est publié ; zéro
    #: sinon, comme dans ``cout.SoldeAnnuel``.
    pib: float = 0.0

    def coefficient(self, scenario: str) -> float:
        return self._coefficients.get(scenario, 0.0)

    def solde(self, scenario: str) -> float:
        return self._soldes.get(scenario, 0.0)

    def ressources_de(self, scenario: str) -> float:
        return self._ressources.get(scenario, 0.0)

    @property
    def ressources(self) -> float:
        """Ce que le système actuel encaisse : la recette que le COR publie."""
        return self.ressources_de("actuel")

    def depense(self, scenario: str) -> float:
        return self._depenses.get(scenario, 0.0)

    def solde_meur(self, scenario: str) -> float:
        return self.solde(scenario) * self.pib


@dataclass(frozen=True)
class AssietteFigee:
    """L'assiette des revenus d'activité, réduite à ce que ``financer`` en lit."""

    derniere_annee: int
    _part_pib: float

    def part_pib(self, annee: int) -> float:
        return self._part_pib


@dataclass(frozen=True)
class EngagementFige:
    """L'engagement acquis à date, tel que la table le porte.

    Les accesseurs sont ceux de ``cout.EngagementAcquis`` : la page ne sait pas
    lequel des deux elle lit, et c'est ce qui garantit que la table figée et le
    calcul complet ne peuvent pas dire deux choses.
    """

    annee: int
    horizon: int
    retraites: float
    actifs: float
    hors_projection: float
    #: Ce qu'Eurostat publie pour la même année, en part de PIB : le seul
    #: point de comparaison extérieur de cette grandeur.
    publie: float
    _par_scenario: dict[str, float] = field(default_factory=dict)
    _sensibilite: tuple[tuple[float, float], ...] = ()

    def part_pib(self, scenario: str = "actuel") -> float:
        return self._par_scenario.get(scenario, 0.0)

    def sensibilite(self) -> tuple[tuple[float, float], ...]:
        return self._sensibilite

    def ecart_pour(self, cible: float) -> float | None:
        """L'écart de taux qui ramènerait l'engagement à ``cible``."""
        points = self._sensibilite
        for (ecart_bas, valeur_bas), (ecart_haut, valeur_haut) in zip(points, points[1:]):
            if valeur_haut <= cible <= valeur_bas:
                largeur = valeur_bas - valeur_haut
                if largeur <= 0.0:
                    return ecart_bas
                return ecart_bas + (ecart_haut - ecart_bas) * (valeur_bas - cible) / largeur
        return None


@dataclass(frozen=True)
class EcartsFiges:
    """Les écarts médians de la grille des cas types, tels que la table les porte.

    L'accueil dit de combien la proposition baisse les retraites, et il ne
    simule rien : il lit ces trois médianes, que ``castypes.ecarts_medians``
    tire de la grille entière des cas types — des secondes de calcul que la
    première page ouverte ne peut pas faire attendre. Les champs sont ceux de
    ``castypes.EcartsMedians`` : la page ne sait pas lequel des deux elle lit.
    """

    a_venir: float
    a_venir_volontaire: float
    deja_liquidees: float
    cases_a_venir: int
    cases_deja_liquidees: int


@dataclass(frozen=True)
class FicheFigee:
    """La fiche de paie d'un exemple, réduite à ce que la page en lit."""

    annee: int
    brut: float
    net: float
    retraite_totale: float
    retraite_employeur: float


@dataclass(frozen=True)
class ExempleFige:
    """Une carrière d'exemple de « Pourquoi changer », simulée une fois.

    ``saisie`` est la saisie simulée, champ par champ : la page ne lit
    l'exemple que si elle demande exactement celle-là, et simule sinon.
    ``pension_financee`` est la pension du système 3 — le scénario
    ``notionnel_retroactif_employeur`` —, ce que les cotisations de l'assuré
    financeraient au rendement d'équilibre.
    """

    saisie: dict
    fiche: FicheFigee
    coefficient_euros_constants: float
    pension_actuel: float
    pension_financee: float


def exemple_de(saisie: dict, comparaison) -> ExempleFige:
    """Ce que « Pourquoi changer » lit d'une simulation, et rien d'autre."""
    fiche = comparaison.remuneration.reference.droit_en_vigueur
    return ExempleFige(
        saisie=dict(saisie),
        fiche=FicheFigee(
            annee=fiche.annee, brut=fiche.brut, net=fiche.net,
            retraite_totale=fiche.retraite_totale,
            retraite_employeur=fiche.retraite_employeur,
        ),
        coefficient_euros_constants=comparaison.coefficient_euros_constants,
        pension_actuel=comparaison.actuel.pension_annuelle,
        pension_financee=comparaison.notionnel_retroactif_employeur.pension_annuelle,
    )


@dataclass(frozen=True)
class BilanFige:
    """Le bilan des quatre systèmes comparés, tel que la table le porte.

    Les accesseurs sont ceux de ``cout.Solde``, et ``financer`` accepte les
    deux sans le savoir.
    """

    annees: list[AnneeBilan]
    premiere_annee_projetee: int
    assiette: AssietteFigee
    #: Le PIB de la dernière année PUBLIÉE, en millions d'euros courants, et
    #: cette année-là. Un manque de 2070 vaut une part de PIB ; le dire en
    #: euros suppose un PIB, et le seul qu'on ait sans inventer une croissance
    #: est celui d'aujourd'hui. Les pages qui s'en servent l'écrivent.
    pib: float = 0.0
    annee_pib: int = 0
    #: L'engagement acquis à date, à la dernière année qu'Eurostat transmette.
    engagements: EngagementFige | None = None
    #: Les écarts médians de la proposition au système actuel, sur la grille.
    ecarts: EcartsFiges | None = None
    #: Les carrières d'exemple de « Pourquoi changer ».
    exemples: tuple[ExempleFige, ...] = ()
    #: La table porte-t-elle la dépense et le PIB de chaque année ? Une table
    #: écrite avant le 7 octobre 2026 ne les porte pas.
    depenses_figees: bool = False

    def exemple(self, saisie: dict) -> ExempleFige | None:
        """L'exemple de cette saisie exactement, ou rien."""
        for exemple in self.exemples:
            if exemple.saisie == saisie:
                return exemple
        return None

    @property
    def premiere_annee(self) -> int:
        return self.annees[0].annee

    @property
    def derniere_annee(self) -> int:
        return self.annees[-1].annee

    @property
    def derniere_annee_observee(self) -> int:
        return self.premiere_annee_projetee - 1

    def annee(self, millesime: int) -> AnneeBilan | None:
        for ligne in self.annees:
            if ligne.annee == millesime:
                return ligne
        return None


def depuis_dictionnaire(donnees: dict) -> BilanFige:
    """Reconstruit le bilan depuis la table, JSON du dépôt ou clé du paquet."""
    return BilanFige(
        annees=[
            AnneeBilan(
                annee=int(ligne["annee"]),
                projete=bool(ligne["projete"]),
                part_contributive=float(ligne["part_contributive"]),
                _coefficients={cle: float(valeur)
                               for cle, valeur in ligne["coefficients"].items()},
                _soldes={cle: float(valeur)
                         for cle, valeur in ligne["soldes"].items()},
                _ressources={cle: float(valeur)
                             for cle, valeur in ligne["ressources"].items()},
                _depenses={cle: float(valeur)
                           for cle, valeur in ligne.get("depenses", {}).items()},
                pib=float(ligne.get("pib", 0.0)),
            )
            for ligne in donnees["annees"]
        ],
        premiere_annee_projetee=int(donnees["premiere_annee_projetee"]),
        assiette=AssietteFigee(
            derniere_annee=int(donnees["annee_assiette"]),
            _part_pib=float(donnees["part_pib_assiette"]),
        ),
        pib=float(donnees.get("pib", 0.0)),
        annee_pib=int(donnees.get("annee_pib", 0)),
        engagements=_engagements(donnees.get("engagements")),
        ecarts=_ecarts(donnees.get("ecarts_medians")),
        exemples=tuple(_exemple(brut) for brut in donnees.get("exemples_risque", ())),
        depenses_figees=bool(donnees["annees"]) and all(
            "depenses" in ligne for ligne in donnees["annees"]),
    )


def _exemple(brut: dict) -> ExempleFige:
    fiche = brut["fiche"]
    return ExempleFige(
        saisie=dict(brut["saisie"]),
        fiche=FicheFigee(
            annee=int(fiche["annee"]), brut=float(fiche["brut"]),
            net=float(fiche["net"]),
            retraite_totale=float(fiche["retraite_totale"]),
            retraite_employeur=float(fiche["retraite_employeur"]),
        ),
        coefficient_euros_constants=float(brut["coefficient_euros_constants"]),
        pension_actuel=float(brut["pension_actuel"]),
        pension_financee=float(brut["pension_financee"]),
    )


def _ecarts(brut: dict | None) -> EcartsFiges | None:
    """Les écarts médians, ou rien : une table écrite avant eux n'en porte pas."""
    if not brut:
        return None
    return EcartsFiges(
        a_venir=float(brut["a_venir"]),
        a_venir_volontaire=float(brut["a_venir_volontaire"]),
        deja_liquidees=float(brut["deja_liquidees"]),
        cases_a_venir=int(brut["cases_a_venir"]),
        cases_deja_liquidees=int(brut["cases_deja_liquidees"]),
    )


def _engagements(brut: dict | None) -> EngagementFige | None:
    """L'engagement acquis, ou rien : une table écrite avant lui n'en porte pas."""
    if not brut:
        return None
    return EngagementFige(
        annee=int(brut["annee"]),
        horizon=int(brut["horizon"]),
        retraites=float(brut["retraites"]),
        actifs=float(brut["actifs"]),
        hors_projection=float(brut["hors_projection"]),
        publie=float(brut["publie"]),
        _par_scenario={cle: float(valeur)
                       for cle, valeur in brut["scenarios"].items()},
        _sensibilite=tuple(
            (float(point["ecart"]), float(point["part_pib"]))
            for point in brut["sensibilite"]
        ),
    )


def charger_bilan(racine: Path) -> BilanFige:
    """La table du dépôt. ``scripts/construire_donnees.py`` l'écrit."""
    chemin = Path(racine) / "derive" / "equilibre.json"
    with chemin.open(encoding="utf-8") as fichier:
        return depuis_dictionnaire(json.load(fichier))
