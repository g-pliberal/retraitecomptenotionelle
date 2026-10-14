"""Le bilan du compte notionnel, à la manière du bilan annuel suédois.

CE QUE LA PAGE COÛT NE DIT PAS. Elle donne, année par année, un FLUX : ce qui
rentre, ce qui sort, le coefficient qui équilibrerait l'année. Un compte
notionnel se juge aussi sur un STOCK, et la Suède le publie chaque année dans
son rapport orange, que l'indice d'équilibre morde ou non (SFB 58:14-20) :

    actif de cotisation = cotisations de l'année × durée de rotation
    ratio d'équilibre   = (actif de cotisation + réserves) ÷ dette

La DURÉE DE ROTATION (« omsättningstid ») est le temps moyen qu'un euro passe
dans le système, de la cotisation qui l'acquiert à la pension qui le rend :
l'âge moyen des pensions servies, pondéré par leurs montants, moins l'âge
moyen des cotisations versées, pondéré de même — la forme de Settergren et
Mikula (2005), qui vaut en coupe une année donnée. Pensionsmyndigheten en
tire un peu plus de trente ans : un euro cotisé en moyenne à 45 ans est servi
à 76. Multipliée par les cotisations de l'année, elle dit quelle dette la
répartition peut porter sans réserves, à structure par âge inchangée.

D'OÙ VIENT CHAQUE TERME.

- Les PROFILS PAR ÂGE viennent de la grille des cas types, pondérée comme les
  masses (:func:`cout._masses`, :func:`cout._masses_cotisations`) : les
  effectifs de l'INSEE pour les cohortes, ceux des caisses pour les cas types,
  la pension revalorisée selon la règle de chaque système. La durée de
  rotation se lit donc système par système : un départ plus tardif ou une
  pension plus basse aux grands âges la raccourcit.
- Les COTISATIONS sont celles du bilan de la page Coût, en part de PIB
  (:meth:`cout.SoldeAnnuel.postes_ressources`) : les cotisations et la
  contribution d'équilibre de l'État, ce que le compte suédois appelle la
  recette de cotisation. Les impôts affectés et les transferts n'y sont pas :
  un compte notionnel ne crédite que ce qui est assis sur un revenu.
- Les RÉSERVES viennent du COR (``reserves_retraite.csv``) : 8,2 % du PIB fin
  2025, FRR compris. Elles sont les mêmes pour tous les systèmes : le
  programme ne dit pas ce qu'il en ferait.
- La DETTE est l'engagement acquis de la page Coût
  (:func:`cout.calculer_engagements`) : la somme des pensions que les droits
  déjà acquis feront verser, actualisée au rythme du PIB, sous la convention
  du prorata temporis commune aux six systèmes. Le bilan suédois prend les
  comptes des actifs et les pensions multipliées par le diviseur économique ;
  pour un compte revalorisé sur les salaires, c'est la même grandeur à la
  convention d'acquisition près, et la limite le dit.

LE TAUX DE COTISATION D'ÉQUILIBRE est l'autre indicateur que le registre
relève (le modèle de l'OIT, 138.19) : la dépense de l'année rapportée à
l'assiette des revenus d'activité, ``C = d × r``, le rapport de dépendance du
système multiplié par son rapport de remplacement. Le dépôt en donne deux :
le taux qui paierait tout sur l'assiette, et celui qui ne paie que ce que les
autres ressources laissent — le levier du prélèvement de ``leviers.py``
(138.3), limité aux cotisations, et sur l'assiette de l'année.

Rien ici ne se calcule pour le site : c'est un indicateur, que
``scripts/bilan_compte.py`` imprime, et que la table du paquet pourra porter
quand une page le montrera.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Sequence

from .cout import (
    CLES_LIBERALES,
    REGLE_PRIX,
    REGLE_PROSPECTIVE,
    REGLE_STOCK,
    TAUX_REELS,
    Pensionne,
    SoldeAnnuel,
    _DEMI_TRANCHE,
    coefficient_historique,
    coefficient_servi,
    regle_revalorisation,
)
from .donnees.population import AGE_MINIMAL, Population
from .revalorisation import RevalorisationServie
from .somme import somme_ordonnee

#: Les postes de ressources que le compte suédois appelle cotisations : ceux
#: qui sont assis sur un revenu d'activité. La contribution d'équilibre de
#: l'État en est une, le taux employeur de ses agents (``cout.py``).
POSTES_COTISES = ("cotisations", "contribution_equilibre_etat")


@dataclass(frozen=True)
class ProfilParAge:
    """Ce qu'un système encaisse et sert, âge par âge, une année donnée.

    Les montants sont dans l'unité de la grille, et seuls leurs rapports se
    lisent : la durée de rotation est une différence d'âges moyens.
    """

    annee: int
    cotisations: dict[int, float]
    pensions: dict[int, float]

    @property
    def age_cotisations(self) -> float:
        return age_moyen(self.cotisations)

    @property
    def age_pensions(self) -> float:
        return age_moyen(self.pensions)

    @property
    def duree_rotation(self) -> float:
        return self.age_pensions - self.age_cotisations


def age_moyen(masses: dict[int, float]) -> float:
    """L'âge moyen d'une masse, pondéré par ses montants.

    L'âge ``a`` d'une cohorte l'année ``t`` est atteint dans l'année : on lui
    donne le milieu, ``a + ½``, des deux côtés, si bien que le demi s'annule
    dans la durée de rotation.
    """
    total = somme_ordonnee(masses.values())
    if total <= 0.0:
        return 0.0
    return somme_ordonnee((age + 0.5) * masse
                          for age, masse in sorted(masses.items())) / total


def effectif_cotisant(population: Population, age: int, annee: int) -> float:
    """L'effectif d'une classe d'âge, y compris sous 50 ans.

    La pyramide du dépôt commence à 50 ans : elle ne compte que des retraités
    (``population.py``). Un cotisant plus jeune est compté par l'effectif de
    sa génération l'année de ses 50 ans, que l'INSEE projette jusqu'en 2070 :
    la mortalité d'ici là le surestime de 2 à 3 %, le solde migratoire le
    sous-estime d'autant, et la durée de rotation n'en lit que la forme.
    """
    if age >= AGE_MINIMAL:
        return population.effectif(age, annee)
    if age < 0:
        return 0.0
    plus_tard = annee + AGE_MINIMAL - age
    if plus_tard > population.derniere_annee:
        return 0.0
    return population.effectif(AGE_MINIMAL, plus_tard)


def profils_par_age(pensionnes: Sequence[Pensionne], population: Population,
                    annee: int, scenarios: Sequence[str],
                    poids_retraites: dict[str, float],
                    poids_cotisants: dict[str, float],
                    revalorisation: RevalorisationServie) -> dict[str, ProfilParAge]:
    """Les profils par âge de chaque système, l'année ``annee``.

    La même grille que les masses, et les mêmes conventions : chaque
    génération de la grille en représente cinq, chacune pesée par l'effectif
    de sa classe d'âge et par le poids de sa caisse — ses retraités du côté
    des pensions, ses cotisants du côté des cotisations. La cohorte née
    ``decalage`` ans après la grille verse, l'année ``t``, ce que la grille
    versait en ``t − decalage`` — sous 50 ans, la pyramide s'arrêtant là,
    l'effectif est celui de :func:`effectif_cotisant` —, et touche, une fois partie, la pension de la
    grille revalorisée selon la règle du système, comme dans l'engagement.

    Les scénarios 1 à 5 prélèvent ce que prélève le droit en vigueur
    (``TAUX_REELS``) : ils changent ce qui est porté au compte, non ce qui est
    prélevé. Le scénario 6 prélève son taux unique, sur la carrière de son
    volet, que l'âge légal peut allonger.
    """
    cles = list(dict.fromkeys(scenarios))
    regles = {cle: regle_revalorisation(cle) for cle in cles}
    cotisations: dict[str, dict[int, float]] = {cle: {} for cle in cles}
    pensions: dict[str, dict[int, float]] = {cle: {} for cle in cles}
    for pensionne in pensionnes:
        part_retraites = poids_retraites.get(pensionne.code, 0.0)
        part_cotisants = poids_cotisants.get(pensionne.code, 0.0)
        if part_retraites <= 0.0 and part_cotisants <= 0.0:
            continue
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            age = annee - pensionne.generation - decalage
            effectif = effectif_cotisant(population, age, annee)
            if effectif <= 0.0:
                continue
            volet = pensionne.volet(decalage)
            completude = pensionne.completude(decalage)
            for cle in cles:
                liberal = cle in CLES_LIBERALES
                serie = (volet.cotisations if liberal
                         else pensionne.cotisations.get(TAUX_REELS, {}))
                versee = serie.get(annee - decalage, 0.0)
                if versee and part_cotisants > 0.0:
                    cotisations[cle][age] = (cotisations[cle].get(age, 0.0)
                                             + part_cotisants * effectif * versee)
                depart = (volet.annee_liquidation if liberal
                          else pensionne.annee_liquidation) + decalage
                if annee < depart or part_retraites <= 0.0:
                    continue
                montant = volet.pension if liberal else pensionne.pensions.get(cle, 0.0)
                if montant <= 0.0:
                    continue
                coefficient = _coefficient(cle, regles[cle], pensionne,
                                           revalorisation, depart, annee)
                pensions[cle][age] = (pensions[cle].get(age, 0.0) + part_retraites
                                      * effectif * completude * montant * coefficient)
    return {cle: ProfilParAge(annee, cotisations[cle], pensions[cle]) for cle in cles}


def _coefficient(cle: str, regle: str, pensionne: Pensionne,
                 revalorisation: RevalorisationServie, depart: int, annee: int) -> float:
    """Ce qu'est devenue en ``annee`` une pension liquidée en ``depart``, sous
    la règle du système : celle de l'engagement (:func:`cout.calculer_engagements`)."""
    if cle == "actuel":
        return coefficient_servi(pensionne.parts_regimes, revalorisation, depart, annee)
    if regle == REGLE_PRIX:
        return 1.0
    if regle == REGLE_STOCK:
        return revalorisation.coefficient_stock(depart, annee, prospectif=False)
    if regle == REGLE_PROSPECTIVE:
        return (revalorisation.coefficient_stock(depart, annee, prospectif=True)
                * coefficient_historique(pensionne.parts_regimes, revalorisation, depart,
                                         min(annee, revalorisation.annee_bascule)))
    raise ValueError(f"règle de revalorisation inconnue : {regle!r}")


@dataclass(frozen=True)
class Reserves:
    """Les réserves du système de retraite, fin d'année, que le COR publie.

    ``montant`` en milliards d'euros courants, ``part_pib`` en fraction du PIB
    de l'année, ``None`` quand le COR ne l'écrit pas.
    """

    lignes: dict[tuple[int, str], tuple[float, float | None]]

    @classmethod
    def charger(cls, racine_donnees: Path) -> "Reserves":
        chemin = racine_donnees / "reference" / "macro" / "reserves_retraite.csv"
        with chemin.open(encoding="utf-8") as flux:
            lecteur = csv.DictReader(ligne for ligne in flux if not ligne.startswith("#"))
            lignes = {
                (int(ligne["annee"]), ligne["poste"]): (
                    float(ligne["montant"]),
                    float(ligne["part_pib"]) if ligne["part_pib"] else None,
                )
                for ligne in lecteur
            }
        return cls(lignes)

    def annees(self) -> tuple[int, ...]:
        return tuple(sorted({annee for annee, _ in self.lignes}))

    def montant(self, annee: int, poste: str = "reserves_totales") -> float | None:
        ligne = self.lignes.get((annee, poste))
        return None if ligne is None else ligne[0]

    def part_pib(self, annee: int, poste: str = "reserves_totales") -> float | None:
        ligne = self.lignes.get((annee, poste))
        return None if ligne is None else ligne[1]

    def rendement(self, annee: int) -> float | None:
        """Les produits financiers nets de l'année sur les réserves du début.

        Un rendement COMPTABLE, celui que le solde du COR intègre quand il dit
        « avec les charges et produits financiers » : il ne compte pas les
        plus-values latentes, que la valeur de marché du stock porte.
        """
        produits = self.montant(annee, "produits_financiers_nets")
        debut = self.montant(annee - 1)
        if produits is None or not debut:
            return None
        return produits / debut


@dataclass(frozen=True)
class BilanCompte:
    """Le bilan d'un système, une année, en part du PIB de l'année."""

    annee: int
    scenario: str
    #: Ce qu'il encaisse de cotisations, contribution de l'État comprise.
    cotisations: float
    age_cotisations: float
    age_pensions: float
    #: Ses réserves, fin d'année, FRR compris ; zéro quand le COR ne les
    #: donne pas cette année-là.
    reserves: float
    #: Ce qu'il doit au titre des droits déjà acquis.
    dette: float
    #: Ce qu'il dépense, ce qu'il encaisse en tout, et l'assiette des revenus
    #: d'activité, en part de PIB.
    depense: float
    ressources: float
    assiette: float

    @property
    def duree_rotation(self) -> float:
        return self.age_pensions - self.age_cotisations

    @property
    def actif_cotisation(self) -> float:
        return self.cotisations * self.duree_rotation

    @property
    def actif(self) -> float:
        return self.actif_cotisation + self.reserves

    @property
    def ratio_equilibre(self) -> float:
        """L'indice d'équilibre suédois : un, le système porte sa dette ;
        moins de un, il faudrait rogner les comptes et les pensions d'autant."""
        return self.actif / self.dette if self.dette > 0.0 else 0.0

    @property
    def taux_equilibre(self) -> float:
        """La dépense sur l'assiette : ``C = d × r``, tout payé par l'assiette."""
        return self.depense / self.assiette if self.assiette > 0.0 else 0.0

    @property
    def taux_cotisation(self) -> float:
        """Ce que les cotisations prélèvent aujourd'hui sur l'assiette."""
        return self.cotisations / self.assiette if self.assiette > 0.0 else 0.0

    @property
    def taux_cotisation_equilibre(self) -> float:
        """Le taux de cotisation qui équilibrerait l'année, les autres
        ressources du système — impôts, transferts — gardées telles quelles."""
        if self.assiette <= 0.0:
            return 0.0
        autres = self.ressources - self.cotisations
        return (self.depense - autres) / self.assiette


def cotisations_de(ligne: SoldeAnnuel, scenario: str) -> float:
    """Les cotisations d'un système, en part de PIB, une ligne du bilan."""
    postes = ligne.postes_ressources(scenario)
    return somme_ordonnee(postes.get(poste, 0.0) for poste in POSTES_COTISES)


def assiette_de(ligne: SoldeAnnuel) -> float:
    """L'assiette des revenus d'activité, en part de PIB : ce que le système
    prélève, divisé par le taux qu'il prélève (``AssietteActivite``)."""
    if ligne.taux_prelevement <= 0.0:
        return 0.0
    return ligne.ressources / ligne.taux_prelevement


def bilan(ligne: SoldeAnnuel, scenario: str, profil: ProfilParAge,
          dette: float, reserves: float) -> BilanCompte:
    """Assemble le bilan d'un système à partir de ses pièces."""
    return BilanCompte(
        annee=ligne.annee,
        scenario=scenario,
        cotisations=cotisations_de(ligne, scenario),
        age_cotisations=profil.age_cotisations,
        age_pensions=profil.age_pensions,
        reserves=reserves,
        dette=dette,
        depense=ligne.depense(scenario),
        ressources=ligne.ressources_de(scenario),
        assiette=assiette_de(ligne),
    )


def calculer_bilans(contexte, annee: int, scenarios: Sequence[str],
                    cas_types=None,
                    engagement: Callable[[str], float] | None = None,
                    ) -> dict[str, BilanCompte]:
    """Le bilan de chaque système, l'année ``annee``, sous les réglages du
    ``contexte`` (:class:`~retraite_notionnelle.contexte.Contexte`).

    ``engagement`` rend la dette d'un système en part de PIB ; par défaut,
    l'engagement acquis de la page Coût à la même date. ``cas_types``
    restreint la grille, pour les tests.
    """
    from .castypes import CAS_TYPES
    from .cout import (
        COTE_COTISANTS,
        _pensionnes,
        _ponderation,
        calculer_engagements,
    )

    cas_types = CAS_TYPES if cas_types is None else cas_types
    simulateur = contexte.simulateur()
    population = contexte.population()
    solde = contexte.cout().solde
    ligne = solde.annee(annee)
    if ligne is None:
        raise ValueError(f"le bilan de la page Coût ne couvre pas {annee}")
    if engagement is None:
        acquis = calculer_engagements(simulateur, contexte.depenses(), population,
                                      annee, scenarios, cas_types=cas_types)
        engagement = acquis.part_pib
    pensionnes, _ = _pensionnes(simulateur, cas_types)
    revalorisation = RevalorisationServie(
        simulateur.pour_la_projection(),
        min((p.annee_liquidation for p in pensionnes), default=annee) - _DEMI_TRANCHE,
        annee,
    )
    poids_retraites = _ponderation(simulateur, "effectifs", cas_types)(annee)
    poids_cotisants = _ponderation(simulateur, "effectifs", cas_types,
                                   COTE_COTISANTS)(annee)
    profils = profils_par_age(pensionnes, population, annee, scenarios,
                              poids_retraites, poids_cotisants, revalorisation)
    reserves = Reserves.charger(simulateur.parametres.racine_donnees)
    stock = reserves.part_pib(annee)
    if stock is None:
        # Le COR ne l'écrit pas toujours en part de PIB : le montant, sur le
        # PIB publié de l'année (en millions d'euros courants), quand il l'est.
        montant = reserves.montant(annee)
        stock = montant * 1000.0 / ligne.pib if montant and ligne.pib > 0.0 else 0.0
    return {cle: bilan(ligne, cle, profils[cle], engagement(cle), stock)
            for cle in profils}
