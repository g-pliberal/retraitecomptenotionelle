"""Le coût des cinq systèmes : ce qu'il a été depuis 1959, ce qu'il serait d'ici 2070.

Le modèle calcule des pensions individuelles. Ce module en tire une grandeur
collective, en deux temps qui n'ont pas le même statut et qu'il ne faut jamais
confondre.

LE PASSÉ — ce qui a été payé, et ce que les autres systèmes auraient coûté
--------------------------------------------------------------------------
    coût du système S en t = dépense OBSERVÉE en t × (masse S / masse actuelle)

La dépense observée vient de la DREES et n'est pas modélisée. Seul le RAPPORT
l'est : la moyenne des écarts de pension entre systèmes, pondérée par le poids
de chaque génération dans la masse de l'année. Un rapport est bien plus robuste
qu'un niveau — les erreurs de niveau du scénario 1, qui est l'étalon, se
retrouvent au dénominateur et s'annulent en grande partie.

L'AVENIR — ce que chaque système coûterait, de 2025 à 2070
-----------------------------------------------------------
La même formule, à un mot près : la dépense observée est remplacée par la
dépense que le modèle produit lui-même, ANCRÉE sur la dernière année publiée.

    coût du système S en t = ancrage × masse S en t
    ancrage = dépense de répartition observée en 2024 ÷ masse actuelle en 2024

Les deux expressions coïncident EXACTEMENT en 2024 — c'est la définition de
l'ancrage —, si bien que les courbes ne sautent pas au passage. Ce qui les fait
bouger après 2024 est ce qui doit les faire bouger : la pyramide des âges de
l'INSEE, et les pensions que chaque génération acquiert sous chaque système.

CE QUI PÈSE COMBIEN
-------------------
Le poids d'une génération une année donnée est son EFFECTIF RÉEL, lu dans les
projections de population de l'INSEE — observées jusqu'en 2023, projetées
ensuite. Le dépôt supposait auparavant toutes les générations de même taille ;
le baby-boom dément cette hypothèse d'un tiers, et elle interdisait toute
projection. Chaque génération de la grille en représente cinq : son poids est
l'effectif des cinq classes d'âge correspondantes.

CE QUE CE MODULE NE FAIT TOUJOURS PAS
-------------------------------------
1. **Les douze cas types pèsent d'un poids égal.** Ils ne décrivent pas la
   population active française — il y a moins d'agents de conduite que de
   salariés au salaire moyen. C'est la convention de la grille des cas types,
   reconduite plutôt que remplacée par une pondération qu'aucune source ne
   fixerait.
2. **Le taux d'emploi et le taux de couverture sont supposés constants.** Le
   modèle compte des générations, non des cotisants : il suppose que la même
   proportion de chaque génération perçoit une pension, et que la carrière type
   ne change pas. La montée de l'activité féminine, elle, a déjà eu lieu ;
   c'est vers le passé que l'hypothèse est la plus fausse.
3. **Aucune règle de pilotage.** Un système notionnel réel porte un coefficient
   d'équilibre qui ajusterait toutes les pensions par un même facteur. Ce
   facteur étant commun, il déplacerait les niveaux sans toucher aux écarts.
4. **Le coût n'est pas le solde.** Ce module dit ce qui est versé, jamais ce
   qui est encaissé.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .castypes import CAS_TYPES, CasType, calculer_cas_types
from .donnees.chargement import Fiabilite
from .donnees.depenses import DepensesRetraite
from .donnees.population import Population
from .simulateur import Simulateur

#: Les cinq systèmes, dans l'ordre du tableau de comparaison. Ce sont les
#: attributs de ``Comparaison`` ; « actuel » est l'étalon et le dénominateur.
SCENARIOS: tuple[tuple[str, str], ...] = (
    ("actuel", "1. Système actuel"),
    ("notionnel_retroactif", "2. Notionnel rétroactif, part salariale"),
    ("notionnel_prospectif", "3. Notionnel dès la bascule, part salariale"),
    ("notionnel_retroactif_employeur", "4. Notionnel rétroactif, avec la part patronale"),
    ("notionnel_prospectif_employeur", "5. Notionnel dès la bascule, avec la part patronale"),
)

#: Première génération dont une liquidation puisse tomber après le début de la
#: répartition (1941) : née en 1880, elle liquide à 61 ans en 1941. En deçà, le
#: modèle refuse — à juste titre — de calculer quoi que ce soit.
PREMIERE_GENERATION = 1880

#: Dernière génération retenue. Née en 2015, elle liquide au plus tôt à 52 ans,
#: soit en 2067 : les suivantes ne serviraient aucune pension avant l'horizon de
#: la projection, et la simulation serait payée pour rien.
DERNIERE_GENERATION = 2015

#: Pas de la grille de générations. Cinq ans suffisent : le rapport varie de
#: moins d'un point d'une génération à la suivante, et le pas commande
#: directement le temps de calcul de la page. Chaque génération retenue
#: représente les cinq classes d'âge qui l'entourent, dont elle porte l'effectif.
PAS_GENERATIONS = 5

#: Dernière année que les projections de population de l'INSEE couvrent. C'est
#: elle qui borne l'avenir, et non une décision du dépôt.
HORIZON = 2070

#: Âge auquel le rapport de dépendance démographique compte les « vieux » —
#: celui de l'INSEE, qui le publie sous cette définition.
AGE_DEPENDANCE = 65


def generations() -> tuple[int, ...]:
    return tuple(range(PREMIERE_GENERATION, DERNIERE_GENERATION + 1, PAS_GENERATIONS))


@dataclass(frozen=True)
class Pensionne:
    """Un couple (cas type, génération), et la pension qu'il perçoit."""

    generation: int
    #: Année de liquidation : avant elle, aucune pension n'est servie.
    annee_liquidation: int
    #: Pension annuelle en euros constants, par scénario.
    pensions: dict[str, float]


@dataclass
class CoutAnnuel:
    """Le coût d'une année, observé puis recalculé pour chaque système."""

    annee: int
    #: Dépense observée, en millions d'euros courants.
    observee: float
    #: Coefficient de passage en euros constants de l'année de référence.
    coefficient_constants: float
    #: Part de la dépense observée dans le PIB de la même année.
    part_pib: float
    #: Rapport de la masse de chaque système à celle du système actuel.
    rapports: dict[str, float]
    #: Nombre de couples (cas type, génération) qui portent l'année.
    pensionnes: int

    def cout(self, scenario: str) -> float:
        """Coût du système, en millions d'euros courants de l'année."""
        return self.observee * self.rapports[scenario]

    def cout_constants(self, scenario: str) -> float:
        return self.cout(scenario) * self.coefficient_constants

    @property
    def observee_constants(self) -> float:
        return self.observee * self.coefficient_constants


@dataclass
class AvenirAnnuel:
    """Une année de la trajectoire de la répartition, observée ou projetée.

    UNITÉ. Contrairement au passé, dont la dépense est publiée en euros
    courants, cette série est tenue en euros CONSTANTS de l'année de référence.
    Ce n'est pas une préférence d'affichage : les pensions dont le modèle tire
    ses masses sont elles-mêmes en euros constants, et mêler les deux unités
    reviendrait à déflater deux fois. Les euros courants s'en déduisent par le
    même coefficient de prix, pris dans l'autre sens.
    """

    annee: int
    #: La base est-elle produite par le modèle plutôt que publiée ?
    projete: bool
    #: Coût du système actuel, en millions d'euros CONSTANTS de référence.
    base: float
    #: Coefficient de passage des euros de l'année aux euros constants.
    coefficient_constants: float
    #: Produit intérieur brut, en millions d'euros courants, observé ou projeté.
    pib: float
    rapports: dict[str, float]
    #: Rapport de dépendance démographique : 65 ans et plus sur 20-64 ans.
    dependance: float

    def cout_constants(self, scenario: str) -> float:
        """Coût du système, en millions d'euros constants de référence."""
        return self.base * self.rapports[scenario]

    def cout(self, scenario: str) -> float:
        """Le même coût, ramené aux euros courants de son année."""
        return self.cout_constants(scenario) / self.coefficient_constants

    def part_pib(self, scenario: str) -> float:
        """Part du PIB : deux grandeurs de la même année, donc deux euros courants."""
        return self.cout(scenario) / self.pib if self.pib else 0.0


@dataclass
class Avenir:
    """La trajectoire de la répartition, de 1990 à l'horizon des projections."""

    annees: list[AvenirAnnuel] = field(default_factory=list)
    #: Année à partir de laquelle la base cesse d'être publiée.
    premiere_annee_projetee: int = 0
    #: Année de bascule des scénarios prospectifs.
    annee_bascule: int = 0
    annee_euros: int = 0
    fiabilite: Fiabilite = Fiabilite.ESTIMEE

    @property
    def premiere_annee(self) -> int:
        return self.annees[0].annee

    @property
    def derniere_annee(self) -> int:
        return self.annees[-1].annee

    def projetees(self) -> list[AvenirAnnuel]:
        return [ligne for ligne in self.annees if ligne.projete]

    def cumul(self, scenario: str) -> float:
        """Cumul sur les seules années PROJETÉES, en millions d'euros constants.

        Le passé est déjà cumulé ailleurs, et sur une autre assiette : les
        mélanger dans un même total ferait un chiffre que personne ne saurait
        lire.
        """
        return sum(ligne.cout_constants(scenario) for ligne in self.projetees())

    def annee(self, millesime: int) -> AvenirAnnuel | None:
        for ligne in self.annees:
            if ligne.annee == millesime:
                return ligne
        return None

    def ecart_cumule(self, scenario: str) -> float:
        """Ce que le système ferait économiser (négatif) ou coûter en plus."""
        return self.cumul(scenario) - self.cumul("actuel")


@dataclass
class Cout:
    """La série complète, et les cumuls qu'on en tire."""

    annees: list[CoutAnnuel] = field(default_factory=list)
    #: La trajectoire de la répartition, passé récent et avenir.
    avenir: Avenir = field(default_factory=Avenir)
    #: Année d'expression des euros constants.
    annee_euros: int = 0
    #: Générations effectivement simulées.
    generations: tuple[int, ...] = ()
    #: Cas types que le modèle a refusé de calculer, par motif.
    echecs: dict[str, int] = field(default_factory=dict)
    fiabilite: Fiabilite = Fiabilite.ESTIMEE

    @property
    def premiere_annee(self) -> int:
        return self.annees[0].annee

    @property
    def derniere_annee(self) -> int:
        return self.annees[-1].annee

    def cumul(self, scenario: str) -> float:
        """Cumul depuis la première année, en millions d'euros CONSTANTS.

        Sommer des euros courants de 1959 et de 2024 n'aurait aucun sens : les
        premiers valent une vingtaine de fois les seconds. Le cumul est donc
        celui des montants ramenés à une même unité.
        """
        return sum(annee.cout_constants(scenario) for annee in self.annees)

    def cumul_observe(self) -> float:
        return sum(annee.observee_constants for annee in self.annees)

    def confondus_avec_actuel(self) -> tuple[str, ...]:
        """Scénarios dont le coût ne s'écarte JAMAIS de celui du système actuel.

        Sur la fenêtre observée, ce sont les scénarios prospectifs : leur
        bascule est postérieure à la dernière année publiée, si bien qu'aucune
        pension n'en est modifiée et que le rapport vaut exactement un. L'égalité
        est stricte et non approchée — le scénario prospectif RECOPIE la pension
        du scénario actuel pour qui a liquidé avant la bascule —, et c'est
        pourquoi elle se teste à l'identité.

        Le calcul est fait, et non écrit en dur : une bascule avancée avant la
        dernière année observée séparerait les courbes, et la page le montrerait.
        """
        return tuple(
            scenario for scenario, _ in SCENARIOS
            if scenario != "actuel"
            and all(ligne.rapports[scenario] == 1.0 for ligne in self.annees)
        )

    def annee(self, millesime: int) -> CoutAnnuel | None:
        for ligne in self.annees:
            if ligne.annee == millesime:
                return ligne
        return None


def _pensionnes(simulateur: Simulateur,
                cas_types: tuple[CasType, ...]) -> tuple[list[Pensionne], dict[str, int]]:
    """Simule la grille et en tire, pour chaque couple, sa pension par système."""
    grille = calculer_cas_types(simulateur, cas_types, generations())
    pensionnes = [
        Pensionne(
            generation=generation,
            annee_liquidation=comparaison.carriere.annee_liquidation,
            pensions={
                scenario: comparaison.en_euros_constants(
                    getattr(comparaison, scenario).pension_annuelle
                )
                for scenario, _ in SCENARIOS
            },
        )
        for (_, generation), comparaison in grille.resultats.items()
    ]
    motifs: dict[str, int] = {}
    for motif in grille.echecs.values():
        motifs[motif] = motifs.get(motif, 0) + 1
    return pensionnes, motifs


#: Demi-largeur de la tranche d'âges qu'une génération de la grille représente.
_DEMI_TRANCHE = PAS_GENERATIONS // 2


def _masses(pensionnes: list[Pensionne], population: Population,
            annee: int) -> tuple[dict[str, float], int]:
    """Masse de pensions par système, une année donnée, et le nombre de couples.

    Chaque génération de la grille en représente cinq, et les cinq sont
    parcourues une à une : leur poids est l'effectif RÉEL de leur classe d'âge,
    publié par l'INSEE, et chacune liquide sa propre année — celle de la
    génération de la grille, décalée d'autant.

    Ce décalage n'est pas un raffinement gratuit. Faire basculer les cinq
    cohortes le même jour ferait entrer cinq classes d'âge d'un coup dans la
    masse, et la trajectoire projetée avancerait par marches de cinq ans au lieu
    de monter. Le pas de la grille commande le temps de calcul ; il ne doit pas
    commander la forme du résultat.
    """
    masses = {scenario: 0.0 for scenario, _ in SCENARIOS}
    vivants = 0
    for pensionne in pensionnes:
        poids = 0.0
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            if annee < pensionne.annee_liquidation + decalage:
                continue
            poids += population.effectif(
                annee - pensionne.generation - decalage, annee
            )
        if poids <= 0.0:
            continue
        vivants += 1
        for scenario, _ in SCENARIOS:
            masses[scenario] += poids * pensionne.pensions[scenario]
    return masses, vivants


def _rapports(masses: dict[str, float]) -> dict[str, float]:
    return {
        scenario: masses[scenario] / masses["actuel"] for scenario, _ in SCENARIOS
    }


def _avenir(pensionnes: list[Pensionne], depenses: DepensesRetraite,
            population: Population, simulateur: Simulateur) -> Avenir:
    """La trajectoire de la répartition, de la première année ventilée à l'horizon.

    Deux régimes, une seule formule. Jusqu'à la dernière année publiée, la base
    est la dépense de répartition OBSERVÉE. Au-delà, elle est celle que le
    modèle produit, mise à l'échelle par un ancrage calculé sur cette même
    dernière année : les deux expressions coïncident exactement à la jonction.
    """
    macro = simulateur.macro
    annee_euros = simulateur.parametres.annee_euros_constants
    derniere_publiee = depenses.derniere_annee

    masses_ancrage, _ = _masses(pensionnes, population, derniere_publiee)
    if masses_ancrage["actuel"] <= 0.0:
        return Avenir()
    # L'ancrage est le prix, en euros constants de référence, d'une unité de la
    # masse du modèle. Les deux termes sont donc mis dans la MÊME unité avant
    # d'être divisés : la dépense publiée, en euros de son année, est ramenée
    # aux euros constants où les pensions du modèle sont déjà exprimées. Les
    # mélanger déflaterait deux fois, et ferait fondre la projection d'un tiers.
    ancrage = (
        depenses.repartition(derniere_publiee)
        * macro.coefficient_prix(derniere_publiee, annee_euros)
        / masses_ancrage["actuel"]
    )

    # Le PIB est publié jusqu'en 2025 ; au-delà il croît au rythme nominal des
    # hypothèses de projection, CORRIGÉ de l'évolution de la population d'âge
    # actif. Sans cette correction, la France de 2070 produirait avec douze pour
    # cent d'actifs qu'aucune projection ne lui donne.
    derniere_pib = depenses.pib.derniere_annee
    pib_projete: dict[int, float] = {}
    courant = depenses.pib(derniere_pib)
    for annee in range(derniere_pib + 1, HORIZON + 1):
        courant *= (1.0 + macro.pib_nominal(annee)) * (
            population.actifs(annee) / population.actifs(annee - 1)
        )
        pib_projete[annee] = courant

    lignes: list[AvenirAnnuel] = []
    for annee in range(depenses.premiere_annee_ventilee, HORIZON + 1):
        masses, _ = _masses(pensionnes, population, annee)
        if masses["actuel"] <= 0.0:
            continue
        projete = annee > derniere_publiee
        coefficient = macro.coefficient_prix(annee, annee_euros)
        base = (
            ancrage * masses["actuel"] if projete
            else depenses.repartition(annee) * coefficient
        )
        actifs = population.actifs(annee)
        lignes.append(AvenirAnnuel(
            annee=annee,
            projete=projete,
            base=base,
            coefficient_constants=coefficient,
            pib=pib_projete.get(annee, depenses.pib(min(annee, derniere_pib))),
            rapports=_rapports(masses),
            dependance=population.effectif_tranche(
                AGE_DEPENDANCE, population.age_maximal, annee) / actifs
            if actifs else 0.0,
        ))

    return Avenir(
        annees=lignes,
        premiere_annee_projetee=derniere_publiee + 1,
        annee_bascule=simulateur.parametres.annee_bascule,
        annee_euros=annee_euros,
        # Une trajectoire ne peut pas valoir mieux qu'estimée : sa démographie
        # est projetée, sa macroéconomie est une hypothèse, et son contrefactuel
        # n'a jamais existé.
        fiabilite=Fiabilite.ESTIMEE,
    )


def calculer_cout(simulateur: Simulateur, depenses: DepensesRetraite,
                  population: Population,
                  cas_types: tuple[CasType, ...] = CAS_TYPES) -> Cout:
    """Le coût observé, les quatre contrefactuels, et la trajectoire jusqu'en 2070.

    Les années où le modèle ne sert AUCUNE pension — celles d'avant la première
    liquidation possible — sont écartées : un rapport y serait une division par
    zéro, et non un résultat.
    """
    pensionnes, echecs = _pensionnes(simulateur, cas_types)
    macro = simulateur.macro
    annee_euros = simulateur.parametres.annee_euros_constants

    lignes: list[CoutAnnuel] = []
    for annee in depenses.annees():
        masses, vivants = _masses(pensionnes, population, annee)
        if masses["actuel"] <= 0.0:
            continue
        lignes.append(CoutAnnuel(
            annee=annee,
            observee=depenses.depense(annee),
            coefficient_constants=macro.coefficient_prix(annee, annee_euros),
            part_pib=depenses.part_pib(annee),
            rapports=_rapports(masses),
            pensionnes=vivants,
        ))

    fiabilite = min(
        (depenses.fiabilite(ligne.annee) for ligne in lignes),
        default=Fiabilite.ESTIMEE,
    )
    return Cout(
        annees=lignes,
        avenir=_avenir(pensionnes, depenses, population, simulateur),
        annee_euros=annee_euros,
        generations=generations(),
        echecs=echecs,
        # Le contrefactuel ne peut jamais valoir mieux qu'« estimé » : la
        # dépense observée est certifiée, le rapport qui la corrige ne l'est
        # pas et ne peut pas l'être — aucune institution ne publie ce qu'un
        # système qui n'a pas existé aurait coûté.
        fiabilite=min(fiabilite, Fiabilite.ESTIMEE),
    )
