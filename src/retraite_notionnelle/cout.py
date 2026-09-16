"""Le coût des six systèmes : ce qu'il a été depuis 1959, ce qu'il serait d'ici 2070.

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

CE QUE CHAQUE CAS TYPE PÈSE
---------------------------
Les douze cas types ont longtemps pesé d'un poids ÉGAL, faute de source. Ils ne
décrivent pas la population française — il y a près de cent fois moins de
retraités à la SNCF qu'à la Cnav —, et le biais avait un sens connu : les
départs très précoces, que le notionnel pénalise le plus, étaient
surreprésentés, si bien que l'écart affiché était un plancher. Chaque cas type
porte désormais l'effectif des retraités de sa caisse, publié par la DREES et
lu année par année (``castypes.poids_effectifs``). L'ancienne convention reste
disponible — ``ponderation="egale"`` — pour dire de combien elle déplaçait les
résultats, ce qu'aucun argument ne remplace.

CE QUE CE MODULE NE FAIT TOUJOURS PAS
-------------------------------------
1. **Un effectif de caisse n'est pas un effectif de personnes.** Un
   polypensionné compte dans chacune de ses caisses ; la pondération
   surreprésente donc les régimes dont les affiliés ont typiquement aussi une
   carrière au régime général. Le biais est l'inverse de celui de l'ancienne
   convention, et beaucoup plus petit.
2. **Le taux d'emploi et le taux de couverture sont supposés constants.** Le
   modèle compte des générations, non des cotisants : il suppose que la même
   proportion de chaque génération perçoit une pension, et que la carrière type
   ne change pas. La montée de l'activité féminine, elle, a déjà eu lieu ;
   c'est vers le passé que l'hypothèse est la plus fausse.
3. **Aucune règle de pilotage.** Un système notionnel réel porte un coefficient
   d'équilibre qui ajusterait toutes les pensions par un même facteur. Ce
   module CALCULE désormais ce facteur — voir ci-dessous —, mais il ne
   l'APPLIQUE pas : les courbes de coût restent celles d'un système qui ne se
   pilote pas. Le facteur étant commun, l'appliquer déplacerait les niveaux
   sans toucher aux écarts entre carrières.
4. **Les recettes ne réagissent à rien, sauf sur un point.** Le solde
   ci-dessous confronte le coût de chaque système aux ressources RÉELLEMENT
   encaissées, celles du système actuel. C'est le bon contrefactuel — « à
   prélèvement inchangé, ce système tiendrait-il ? » — et ce n'est pas le
   seul : le scénario 6, qui pose un taux unique de 18 %, changerait aussi les
   recettes, et le coefficient d'équilibre ne le dit pas. Le point où elles
   réagissent : ce que la branche famille et l'assurance chômage versent pour
   des droits que les scénarios notionnels ne servent pas — AVPF, majorations
   pour enfants, points des chômeurs — leur est RETIRÉ, année par année là où
   on le connaît (2013-2024), à part constante des ressources ailleurs. La
   recette suit le droit.

LE SOLDE, ET NON LE COÛT
-------------------------
Un coût n'est pas un solde : un système qui coûterait quatre fois moins
servirait quatre fois moins, ce qui est une autre affaire. Le second terme du
bilan vient du COR, seul à consolider dépenses ET ressources du système de
retraite sur un même périmètre (``donnees/equilibre.py`` dit pourquoi ce n'est
pas la DREES). De là, deux grandeurs par système et par année :

    ressources de S = ressources observées − recette non acquise (S notionnel)
    solde du système S = ressources de S − dépenses du COR × rapport S
    coefficient d'équilibre de S = ressources de S ÷ (dépenses × rapport S)

Le coefficient est le facteur par lequel il faudrait multiplier TOUTES les
pensions du système S pour que l'année tombe juste. Il vaut un quand le système
s'équilibre, moins de un quand il faut rogner. Pour le système actuel, dont le
rapport vaut un par construction et qui encaisse tout, il redonne exactement le
solde publié par le COR : c'est ce qui dit que le raccord ne triche pas. La
recette non acquise est ce que ``donnees/equilibre.py`` appelle ainsi : un
demi-point de PIB que la CNAF et l'Unédic versent pour des droits qu'aucun
scénario notionnel ne sert.

Le périmètre du COR n'est pas celui de la dépense observée plus haut — 13,86 %
du PIB en 2024 contre 13,59 % pour la répartition obligatoire de la DREES. Rien
n'est mélangé pour autant : le RAPPORT du modèle est sans dimension, et c'est
la seule chose qu'on emprunte à une série pour l'appliquer à l'autre.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from .castypes import (
    CAS_TYPES,
    VARIANTES_LIQUIDATION,
    CasType,
    calculer_cas_types,
    poids_effectifs,
    poids_egaux,
)
from .donnees.chargement import Fiabilite
from .donnees.depenses import DepensesRetraite
from .donnees.equilibre import ComptesRetraite
from .donnees.population import Population
from .simulateur import Simulateur

#: Les six systèmes, dans l'ordre du tableau de comparaison. Ce sont les
#: attributs de ``Comparaison`` ; « actuel » est l'étalon et le dénominateur.
SCENARIOS: tuple[tuple[str, str], ...] = (
    ("actuel", "1. Système actuel"),
    ("notionnel_retroactif", "2. Notionnel rétroactif, part salariale"),
    ("notionnel_prospectif", "3. Notionnel dès la bascule, part salariale"),
    ("notionnel_retroactif_employeur", "4. Notionnel rétroactif, avec la part patronale"),
    ("notionnel_prospectif_employeur", "5. Notionnel dès la bascule, avec la part patronale"),
    ("notionnel_liberal", "6. Notionnel rétroactif, 18 % dès la bascule, garantie vieillesse"),
)

#: La part du scénario 6 que l'IMPÔT finance : la garantie vieillesse, portée
#: à part de la pension contributive. Ce n'est pas un système, c'est une
#: composante d'un système — elle a sa masse et son rapport comme les autres,
#: pour que la page puisse dire ce que le scénario 6 demande aux cotisations
#: et ce qu'il demande au contribuable, mais elle n'entre dans aucun tableau
#: de comparaison comme une ligne à part entière.
COMPOSANTE_GARANTIE = "garantie_vieillesse_liberal"

#: Tout ce dont une masse est calculée : les six systèmes, et la composante.
CLES_MASSES: tuple[str, ...] = tuple(scenario for scenario, _ in SCENARIOS) + (
    COMPOSANTE_GARANTIE,
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


#: Les deux pondérations possibles des cas types. ``effectifs`` est celle des
#: résultats affichés ; ``egale`` est l'ancienne convention, gardée pour mesurer
#: ce qu'elle valait.
PONDERATIONS: tuple[str, ...] = ("effectifs", "egale")

#: Les deux façons de dater le départ des cas types, reprises de ``castypes``.
#: ``droit`` est celle des résultats affichés ; ``absolu`` est l'ancienne, où
#: toutes les générations partaient à l'âge écrit dans la grille.
LIQUIDATIONS: tuple[str, ...] = VARIANTES_LIQUIDATION


@dataclass(frozen=True)
class Pensionne:
    """Un couple (cas type, génération), et la pension qu'il perçoit."""

    #: Code du cas type : c'est par lui que le couple reçoit son poids.
    code: str
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
class SoldeAnnuel:
    """Une année du bilan : ce qui rentre, ce que chaque système ferait sortir.

    Tout y est en PART DE PIB — l'unité du COR, et la seule où une recette de
    2002 et une projection de 2070 se comparent sans convention d'actualisation.
    ``pib`` porte le produit intérieur brut en millions d'euros courants quand
    il est PUBLIÉ, et zéro sinon : au-delà, un montant en milliards ne serait
    qu'une hypothèse de croissance déguisée en observation.
    """

    annee: int
    #: Le compte est-il projeté par le COR plutôt qu'observé ?
    projete: bool
    #: Ressources du système de retraite, en part de PIB.
    ressources: float
    #: Dépenses du système de retraite, en part de PIB, système actuel.
    depenses: float
    rapports: dict[str, float]
    #: PIB en millions d'euros courants, ou zéro hors de la fenêtre publiée.
    pib: float
    #: Ce que la branche famille et l'assurance chômage versent pour des droits
    #: que les scénarios notionnels ne servent pas, en part de PIB : une recette
    #: du système actuel, jamais la leur.
    retrait: float = 0.0

    def depense(self, scenario: str) -> float:
        """Ce que le système coûterait cette année-là, en part de PIB."""
        return self.depenses * self.rapports[scenario]

    def ressources_de(self, scenario: str) -> float:
        """Ce qu'un système peut compter comme ressources, en part de PIB.

        Le système actuel encaisse tout. Un scénario notionnel ne sert ni
        l'AVPF, ni les majorations pour enfants, ni rien pendant une année de
        chômage : il ne peut pas compter ce que la CNAF et l'Unédic versent
        pour ces droits-là. LA RECETTE SUIT LE DROIT.
        """
        return self.ressources if scenario == "actuel" else self.ressources - self.retrait

    def solde(self, scenario: str) -> float:
        """Ressources moins dépenses, en part de PIB. Négatif : besoin de financement."""
        return self.ressources_de(scenario) - self.depense(scenario)

    def coefficient(self, scenario: str) -> float:
        """Facteur par lequel multiplier toutes les pensions pour tomber juste.

        Un quand le système s'équilibre, moins de un quand il faut rogner. Zéro
        rendu — plutôt qu'une division par zéro — si le système ne sert rien.
        """
        depense = self.depense(scenario)
        return self.ressources_de(scenario) / depense if depense > 0.0 else 0.0

    def solde_meur(self, scenario: str) -> float:
        """Le même solde en millions d'euros courants, et zéro si le PIB manque."""
        return self.solde(scenario) * self.pib

    def ressources_meur(self) -> float:
        """Ce qui rentre, en millions d'euros courants, et zéro si le PIB manque.

        Une part de PIB ne parle qu'à qui sait ce qu'est le PIB. Les euros, si —
        et c'est en euros que la page ouvre, avant de passer aux parts, qui sont
        la seule unité où 1959 et 2070 se comparent.
        """
        return self.ressources * self.pib

    def depense_meur(self, scenario: str) -> float:
        """Ce qui sort, en millions d'euros courants, et zéro si le PIB manque."""
        return self.depense(scenario) * self.pib


@dataclass
class Solde:
    """Le bilan du système de retraite, de la première année du COR à son horizon."""

    annees: list[SoldeAnnuel] = field(default_factory=list)
    #: Première année que le COR projette plutôt qu'il n'observe.
    premiere_annee_projetee: int = 0
    #: Niveau du COMPTE observé — ce qui rentre et ce qui sort, sans modèle.
    fiabilite_observee: Fiabilite = Fiabilite.ESTIMEE
    #: Niveau de tout ce qui passe par un rapport de masses, c'est-à-dire de
    #: toutes les colonnes des cinq contrefactuels. Jamais mieux qu'estimé :
    #: aucune institution ne publie le solde d'un système qui n'a pas existé.
    fiabilite: Fiabilite = Fiabilite.ESTIMEE

    @property
    def premiere_annee(self) -> int:
        return self.annees[0].annee

    @property
    def derniere_annee(self) -> int:
        return self.annees[-1].annee

    @property
    def derniere_annee_observee(self) -> int:
        return self.premiere_annee_projetee - 1

    def observees(self) -> list[SoldeAnnuel]:
        return [ligne for ligne in self.annees if not ligne.projete]

    def projetees(self) -> list[SoldeAnnuel]:
        return [ligne for ligne in self.annees if ligne.projete]

    def annee(self, millesime: int) -> SoldeAnnuel | None:
        for ligne in self.annees:
            if ligne.annee == millesime:
                return ligne
        return None

    def solde_moyen(self, scenario: str, debut: int, fin: int) -> float:
        """Solde moyen sur une fenêtre, en part de PIB.

        C'est l'indicateur par lequel le COR juge la pérennité financière : un
        solde négatif une année donnée ne dit rien, une moyenne négative sur
        quarante ans dit tout.
        """
        lignes = [l for l in self.annees if debut <= l.annee <= fin]
        if not lignes:
            return 0.0
        return sum(ligne.solde(scenario) for ligne in lignes) / len(lignes)

    def premiere_annee_equilibree(self, scenario: str) -> int | None:
        """Première année PROJETÉE où le système cesse d'être en déficit.

        ``None`` quand il ne l'est jamais sur la fenêtre. La question ne se pose
        que sur l'avenir : le passé est ce qu'il a été.
        """
        for ligne in self.projetees():
            if ligne.solde(scenario) >= 0.0:
                return ligne.annee
        return None


@dataclass
class Cout:
    """La série complète, et les cumuls qu'on en tire."""

    annees: list[CoutAnnuel] = field(default_factory=list)
    #: La trajectoire de la répartition, passé récent et avenir.
    avenir: Avenir = field(default_factory=Avenir)
    #: Le bilan : ce qui rentre face à ce que chaque système ferait sortir.
    solde: Solde = field(default_factory=Solde)
    #: Année d'expression des euros constants.
    annee_euros: int = 0
    #: Générations effectivement simulées.
    generations: tuple[int, ...] = ()
    #: Cas types que le modèle a refusé de calculer, par motif.
    echecs: dict[str, int] = field(default_factory=dict)
    #: Pondération appliquée aux cas types : ``effectifs`` ou ``egale``.
    ponderation: str = "effectifs"
    #: Datation du départ des cas types : ``droit`` ou ``absolu``.
    liquidation: str = "droit"
    #: Poids de chaque cas type la DERNIÈRE année observée — ce que la page
    #: affiche pour dire sur quoi ses agrégats reposent.
    poids: dict[str, float] = field(default_factory=dict)
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


def _pensionnes(simulateur: Simulateur, cas_types: tuple[CasType, ...],
                liquidation: str = "droit",
                ) -> tuple[list[Pensionne], dict[str, int]]:
    """Simule la grille et en tire, pour chaque couple, sa pension par système."""
    grille = calculer_cas_types(simulateur, cas_types, generations(), liquidation)
    pensionnes = [
        Pensionne(
            code=code,
            generation=generation,
            annee_liquidation=comparaison.carriere.annee_liquidation,
            pensions={
                **{
                    scenario: comparaison.en_euros_constants(
                        getattr(comparaison, scenario).pension_annuelle
                    )
                    for scenario, _ in SCENARIOS
                },
                COMPOSANTE_GARANTIE: comparaison.en_euros_constants(
                    comparaison.notionnel_liberal.garantie_vieillesse.complement
                ),
            },
        )
        for (code, generation), comparaison in grille.resultats.items()
    ]
    motifs: dict[str, int] = {}
    for motif in grille.echecs.values():
        motifs[motif] = motifs.get(motif, 0) + 1
    return pensionnes, motifs


#: Demi-largeur de la tranche d'âges qu'une génération de la grille représente.
_DEMI_TRANCHE = PAS_GENERATIONS // 2


def _masses(pensionnes: list[Pensionne], population: Population, annee: int,
            poids_cas: dict[str, float]) -> tuple[dict[str, float], int]:
    """Masse de pensions par système, une année donnée, et le nombre de couples.

    DEUX pondérations se composent ici, et elles ne disent pas la même chose.
    Celle de la GÉNÉRATION est démographique : chaque génération de la grille en
    représente cinq, parcourues une à une, dont le poids est l'effectif réel de
    la classe d'âge publié par l'INSEE, et chacune liquide sa propre année —
    celle de la génération de la grille, décalée d'autant. Ce décalage n'est pas
    un raffinement gratuit : faire basculer les cinq cohortes le même jour ferait
    entrer cinq classes d'âge d'un coup dans la masse, et la trajectoire avancerait
    par marches de cinq ans au lieu de monter.

    Celle du CAS TYPE est sociologique : elle dit combien de retraités ont eu
    cette carrière-là, et vient des effectifs de caisse de la DREES. Sans elle,
    l'agent de conduite pèserait ce que pèse le salarié au salaire moyen.
    """
    masses = {cle: 0.0 for cle in CLES_MASSES}
    vivants = 0
    for pensionne in pensionnes:
        part = poids_cas.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
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
        for cle in CLES_MASSES:
            masses[cle] += part * poids * pensionne.pensions[cle]
    return masses, vivants


def _ponderation(simulateur: Simulateur, mode: str,
                 cas_types: tuple[CasType, ...]) -> Callable[[int], dict[str, float]]:
    """Fonction qui rend le poids de chaque cas type une année donnée.

    Les poids d'effectifs varient d'une année à l'autre — la France de 1960
    comptait plus d'exploitants agricoles que de fonctionnaires —, et la fenêtre
    publiée par la DREES est 2004-2024 : hors d'elle, la répartition du bord est
    reconduite, et la série le dit en tombant au niveau ``estimee``.
    """
    if mode not in PONDERATIONS:
        raise ValueError(f"pondération inconnue : {mode!r} (attendu : {PONDERATIONS})")
    if mode == "egale":
        fixes = poids_egaux(cas_types)
        return lambda annee: fixes
    effectifs = simulateur.effectifs
    memoire: dict[int, dict[str, float]] = {}

    def poids(annee: int) -> dict[str, float]:
        if annee not in memoire:
            memoire[annee] = poids_effectifs(effectifs, annee, cas_types)
        return memoire[annee]

    return poids


def _rapports(masses: dict[str, float]) -> dict[str, float]:
    return {cle: masses[cle] / masses["actuel"] for cle in CLES_MASSES}


def _avenir(pensionnes: list[Pensionne], depenses: DepensesRetraite,
            population: Population, simulateur: Simulateur,
            poids: Callable[[int], dict[str, float]]) -> Avenir:
    """La trajectoire de la répartition, de la première année ventilée à l'horizon.

    Deux régimes, une seule formule. Jusqu'à la dernière année publiée, la base
    est la dépense de répartition OBSERVÉE. Au-delà, elle est celle que le
    modèle produit, mise à l'échelle par un ancrage calculé sur cette même
    dernière année : les deux expressions coïncident exactement à la jonction.
    """
    macro = simulateur.macro
    annee_euros = simulateur.parametres.annee_euros_constants
    derniere_publiee = depenses.derniere_annee

    masses_ancrage, _ = _masses(pensionnes, population, derniere_publiee,
                                poids(derniere_publiee))
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
        masses, _ = _masses(pensionnes, population, annee, poids(annee))
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


def _solde(avenir: Avenir, comptes: ComptesRetraite,
           derniere_annee_pib: int) -> Solde:
    """Le bilan, obtenu en croisant le compte du COR et les rapports du modèle.

    Aucune pension n'est resimulée ici : les rapports de masses sont ceux que
    ``_avenir`` a déjà calculés, année par année, et cette fonction ne fait que
    les appliquer à une autre série de dépenses. C'est ce qui rend la section
    gratuite en temps de calcul — et c'est aussi ce qui la borne : elle ne
    couvre que les années où les deux fenêtres se recouvrent.

    Le RAPPORT est la seule chose empruntée au modèle. Il est sans dimension,
    et c'est pourquoi on peut l'appliquer à une dépense dont le périmètre n'est
    pas celui sur lequel il a été calculé. La dépense du système actuel, elle,
    reste celle du COR de bout en bout : c'est ce qui fait que le solde du
    scénario 1 est exactement le solde publié, et non une reconstitution.
    """
    par_annee = {ligne.annee: ligne for ligne in avenir.annees}
    lignes = [
        SoldeAnnuel(
            annee=annee,
            projete=annee > comptes.derniere_annee_observee,
            ressources=comptes.ressource(annee),
            depenses=comptes.depense(annee),
            rapports=par_annee[annee].rapports,
            pib=par_annee[annee].pib if annee <= derniere_annee_pib else 0.0,
            retrait=comptes.recette_non_acquise(annee),
        )
        for annee in comptes.annees() if annee in par_annee
    ]
    if not lignes:
        return Solde()
    return Solde(
        annees=lignes,
        premiere_annee_projetee=comptes.derniere_annee_observee + 1,
        fiabilite_observee=min(
            (comptes.fiabilite(ligne.annee) for ligne in lignes if not ligne.projete),
            default=Fiabilite.ESTIMEE,
        ),
        fiabilite=Fiabilite.ESTIMEE,
    )


def calculer_cout(simulateur: Simulateur, depenses: DepensesRetraite,
                  population: Population,
                  comptes: ComptesRetraite | None = None,
                  cas_types: tuple[CasType, ...] = CAS_TYPES,
                  ponderation: str = "effectifs",
                  liquidation: str = "droit") -> Cout:
    """Le coût observé, les cinq contrefactuels, et la trajectoire jusqu'en 2070.

    Les années où le modèle ne sert AUCUNE pension — celles d'avant la première
    liquidation possible — sont écartées : un rapport y serait une division par
    zéro, et non un résultat.

    ``ponderation`` choisit ce que chaque cas type pèse : ``effectifs``, les
    retraités de sa caisse publiés par la DREES, ou ``egale``, l'ancienne
    convention. Le second n'existe que pour mesurer ce que le premier a déplacé.

    ``liquidation`` choisit l'âge auquel chaque cas type part : ``droit``,
    celui que le droit de sa génération lui ouvre, ou ``absolu``, l'âge écrit
    dans la grille — le même pour toutes les générations. Le second n'existe,
    lui aussi, que pour mesurer ce que le premier a déplacé : c'est par lui
    qu'on lit, sans argumenter, ce que valait un modèle qui faisait liquider
    la génération 1940 à l'âge légal de 2023.

    ``comptes`` porte le second terme du bilan — les ressources. Il est
    facultatif : sans lui, tout ce qui précède est calculé à l'identique et le
    solde reste vide, ce qui est exactement l'état du dépôt avant que ces
    ressources n'existent.
    """
    pensionnes, echecs = _pensionnes(simulateur, cas_types, liquidation)
    poids = _ponderation(simulateur, ponderation, cas_types)
    macro = simulateur.macro
    annee_euros = simulateur.parametres.annee_euros_constants

    lignes: list[CoutAnnuel] = []
    for annee in depenses.annees():
        masses, vivants = _masses(pensionnes, population, annee, poids(annee))
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
    avenir = _avenir(pensionnes, depenses, population, simulateur, poids)
    return Cout(
        annees=lignes,
        avenir=avenir,
        solde=_solde(avenir, comptes, depenses.pib.derniere_annee)
        if comptes is not None and avenir.annees else Solde(),
        annee_euros=annee_euros,
        generations=generations(),
        echecs=echecs,
        ponderation=ponderation,
        liquidation=liquidation,
        poids=poids(depenses.derniere_annee),
        # Le contrefactuel ne peut jamais valoir mieux qu'« estimé » : la
        # dépense observée est certifiée, le rapport qui la corrige ne l'est
        # pas et ne peut pas l'être — aucune institution ne publie ce qu'un
        # système qui n'a pas existé aurait coûté.
        fiabilite=min(fiabilite, Fiabilite.ESTIMEE),
    )
