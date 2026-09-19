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
4. **Les recettes réagissent sur deux points, et sur deux seulement.** Le
   solde ci-dessous confronte le coût de chaque système aux ressources du
   système actuel, corrigées de ce que le système en question ne peut pas
   encaisser.

   LA RECETTE SUIT LE DROIT. Ce que la branche famille et l'assurance chômage
   versent pour des droits que les scénarios notionnels ne servent pas — AVPF,
   majorations pour enfants, points des chômeurs — leur est RETIRÉ, année par
   année là où on le connaît (2013-2024), à part constante des ressources
   ailleurs.

   LA RECETTE SUIT LE TAUX. Le scénario 6 remplace tous les taux par 18 % à
   compter de la bascule : sa part COTISÉE des ressources est multipliée par le
   rapport de ce que ce taux prélève sur les carrières de la grille à ce que le
   droit en vigueur y prélève. Ce rapport vaut 0,62 une fois la bascule passée,
   c'est-à-dire un taux moyen de 29 % aujourd'hui, et il ne bouge plus ensuite.
   Aucun autre scénario n'y touche : les scénarios 2 à 5 changent ce qui est
   PORTÉ AU COMPTE, non ce qui est PRÉLEVÉ, et l'employeur verse sa part dans
   tous les cas.

   Ce qui ne réagit toujours pas : les ressources NON cotisées — impôts et
   taxes affectés, subventions d'équilibre, un quart du total — reconduites
   telles quelles faute que le programme dise ce qu'il en ferait, ce qui est
   l'hypothèse la plus favorable au scénario 6 ; et les réserves financières
   des régimes, que le COR chiffre à part, le solde disant le flux et jamais le
   stock.

LE SOLDE, ET NON LE COÛT
-------------------------
Un coût n'est pas un solde : un système qui coûterait quatre fois moins
servirait quatre fois moins, ce qui est une autre affaire. Le second terme du
bilan vient du COR, seul à consolider dépenses ET ressources du système de
retraite sur un même périmètre (``donnees/equilibre.py`` dit pourquoi ce n'est
pas la DREES). De là, deux grandeurs par système et par année :

    ressources de S = ressources cotisées × rapport de recette de S
                      + ressources non cotisées
                      − recette non acquise (S notionnel)
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
from .donnees.assiette import AssietteActivite
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

#: Les deux BARÈMES DE PRÉLÈVEMENT dont une masse de cotisations est calculée.
#: Ils ne sont que deux parce qu'un seul scénario change ce qui est PRÉLEVÉ :
#: le 6, qui remplace tous les taux par 18 % à compter de la bascule. Les
#: scénarios 2 à 5 changent ce qui est PORTÉ AU COMPTE — la part salariale
#: seule, ou les deux parts — et non ce que la paie supporte : l'employeur
#: verse toujours sa part, elle finance toujours le système, et elle n'ouvre
#: simplement plus de droit à celui qui la voit passer. Confondre les deux
#: ferait dire au scénario 2 qu'il encaisse un tiers de moins, ce qui serait
#: faux.
TAUX_REELS = "taux_reels"
CLES_RECETTES: tuple[str, ...] = (TAUX_REELS, "notionnel_liberal")

#: Les deux façons d'établir la recette du scénario 6, et elles ne posent pas
#: la même question.
#:
#: ``assiette`` applique son taux de 18 % à l'ASSIETTE MESURÉE des revenus
#: d'activité, et lui retire les impôts et taxes affectés. C'est la convention
#: du programme, et elle tient en une phrase : un compte notionnel ne crédite
#: que ce qui est assis sur un revenu d'activité, et un impôt affecté n'ouvre
#: de droit à personne.
#:
#: ``rapport`` est l'ancienne convention, gardée pour mesurer ce qu'elle
#: valait : elle multipliait la part cotisée des ressources OBSERVÉES par le
#: rapport de deux taux LÉGAUX, et ne retirait aucun des trois postes non
#: contributifs. Elle est donc, depuis septembre 2026, un repère d'avant les
#: décisions du programme, et non une variante de leur calcul.
CONVENTION_ASSIETTE = "assiette"
CONVENTION_RAPPORT = "rapport"
CONVENTIONS_RECETTE: tuple[str, ...] = (CONVENTION_ASSIETTE, CONVENTION_RAPPORT)

#: CE QUE LES SCÉNARIOS NOTIONNELS FONT DE LA RÉVERSION, et il fallait le dire.
#:
#: Le modèle ne calcule aucune pension de réversion : elle concerne le conjoint
#: survivant et non l'assuré, et ``config.py`` la range depuis toujours parmi
#: les droits que l'étalon lui-même ne sert pas. Le rapport de masses par
#: lequel un scénario fait réagir la dépense ne décrit donc que les droits
#: DIRECTS — et il s'appliquait pourtant à une base qui porte les deux, ce qui
#: revenait à recalculer à la baisse une réversion que personne n'avait
#: recalculée. ``part_droits_derives`` sépare les deux ; reste à dire ce que le
#: scénario fait de la seconde, et c'est une décision, pas un calcul.
#:
#: ``servie`` est celle du dépôt : la réversion est reconduite telle quelle,
#: comme en Italie, où le capital notionnel du défunt se partage. C'est la plus
#: COÛTEUSE des deux pour les scénarios notionnels, et c'est une raison de la
#: prendre par défaut : l'autre serait l'hypothèse flatteuse, et le dépôt n'en
#: prend pas sans qu'un programme l'ait tranchée.
#:
#: ``supprimee`` est l'autre chemin, celui de la Suède, où un compte notionnel
#: ne verse qu'à son titulaire. Elle reste calculable pour qu'on sache ce
#: qu'elle vaut, et elle n'est pas servie par défaut.
CONVENTION_REVERSION_SERVIE = "servie"
CONVENTION_REVERSION_SUPPRIMEE = "supprimee"
CONVENTIONS_REVERSION: tuple[str, ...] = (
    CONVENTION_REVERSION_SERVIE, CONVENTION_REVERSION_SUPPRIMEE,
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
    #: Année où la garantie vieillesse s'ouvre : celle de la liquidation si
    #: elle a lieu à 65 ans ou plus, celle des 65 ans sinon. Avant elle, on ne
    #: touche pas le minimum vieillesse, et la masse de la composante ne porte
    #: donc rien — c'est la seule clé dont la date d'entrée diffère.
    annee_ouverture_garantie: int
    #: Pension annuelle en euros constants, par scénario.
    pensions: dict[str, float]
    #: Ce que cette carrière VERSE, année par année, sous chacun des deux
    #: barèmes de prélèvement. En euros courants de chaque année : seul le
    #: rapport des deux est lu, et il est sans dimension.
    cotisations: dict[str, dict[int, float]] = field(default_factory=dict)


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
    #: Part de la masse versée qui est une pension de RÉVERSION, et que le
    #: rapport ne décrit pas — ``masse_du_scenario`` dit pourquoi.
    part_derives: float = 0.0
    #: Les scénarios notionnels reconduisent-ils la réversion ?
    reversion_servie: bool = True

    def cout(self, scenario: str) -> float:
        """Coût du système, en millions d'euros courants de l'année."""
        return masse_du_scenario(self.observee, self.part_derives,
                                 self.rapports[scenario], scenario,
                                 self.reversion_servie)

    def cout_constants(self, scenario: str) -> float:
        return self.cout(scenario) * self.coefficient_constants

    @property
    def observee_constants(self) -> float:
        return self.observee * self.coefficient_constants


def masse_du_scenario(base: float, part_derives: float, rapport: float,
                      scenario: str, reversion_servie: bool = True) -> float:
    """Applique un rapport de masses à une base, et au seul morceau qu'il décrit.

    LE RAPPORT NE DÉCRIT QUE LES DROITS DIRECTS. Il est le quotient de deux
    masses de pensions calculées sur les treize cas types, qui n'ont ni conjoint
    ni survivant : aucune réversion n'y entre. La base, elle, porte les deux —
    un huitième de réversion en 2010, un dixième en 2024, un dix-huitième en
    2070. Multiplier l'une par l'autre, comme le modèle le faisait jusqu'au
    19 septembre 2026, revenait à réduire la réversion dans la même proportion
    que les pensions propres, sans que rien ne l'ait décidé.

    Le rapport ne multiplie donc que la part DIRECTE de la base, et la part
    dérivée suit la convention du scénario : reconduite telle quelle, ou
    supprimée. ``CONVENTIONS_REVERSION`` dit pourquoi la première est celle du
    dépôt.

    DEUX CAS À PART. Le système actuel rend sa base sans rien y toucher — son
    rapport vaut un, et la formule le rendrait de toute façon, mais l'écrire
    évite qu'un arrondi ne fasse mentir l'identité. Et la GARANTIE VIEILLESSE
    n'est pas un système : c'est une allocation différentielle calculée, elle
    aussi, sur les seuls droits directs, et à laquelle on n'ajoute donc aucune
    réversion.
    """
    if scenario == "actuel":
        return base
    directe = base * (1.0 - part_derives) * rapport
    if scenario == COMPOSANTE_GARANTIE or not reversion_servie:
        return directe
    return directe + base * part_derives


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
    #: Rapport de la RECETTE de chaque système à celle du système actuel. Un
    #: partout, sauf pour le scénario 6 à compter de la bascule.
    rapports_recettes: dict[str, float] = field(default_factory=dict)
    #: Part de la masse versée qui est une pension de RÉVERSION, et que le
    #: rapport ne décrit pas — ``masse_du_scenario`` dit pourquoi.
    part_derives: float = 0.0
    #: Les scénarios notionnels reconduisent-ils la réversion ?
    reversion_servie: bool = True

    def cout_constants(self, scenario: str) -> float:
        """Coût du système, en millions d'euros constants de référence."""
        return masse_du_scenario(self.base, self.part_derives,
                                 self.rapports[scenario], scenario,
                                 self.reversion_servie)

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
    #: Rapport de la recette de chaque système à celle du système actuel. Vide
    #: vaut un partout, c'est-à-dire l'ancienne convention : des recettes qui
    #: ne réagissent à rien.
    rapports_recettes: dict[str, float] = field(default_factory=dict)
    #: Part des ressources qui est une cotisation assise sur un revenu
    #: d'activité, la seule sur laquelle un changement de taux ait prise.
    part_contributive: float = 0.0
    #: Part des ressources qui est un impôt ou une taxe affectés : CSG,
    #: forfait social, taxe sur les salaires, transferts de TVA. Le scénario 6
    #: ne les reconduit pas, et ``ressources_de`` dit pourquoi.
    part_impots: float = 0.0
    #: La part de ``retrait`` dont la recette arrive par l'impôt et non par un
    #: transfert : ce que le fonds de solidarité vieillesse verse aux régimes,
    #: financé par une CSG qui est dans ``part_impots``. Qui retire le poste en
    #: entier doit cesser de retirer cette ligne — sans quoi la même somme
    #: sortirait deux fois.
    retrait_par_impot: float = 0.0
    #: Part des ressources qui est une subvention d'équilibre : ce que le budget
    #: de l'État comble aux régimes dont les cotisants ont disparu avant les
    #: retraités — la SNCF, les mines, les marins. Le scénario 6 ne la reconduit
    #: pas, et ``ressources_de`` dit pourquoi.
    part_subventions: float = 0.0
    #: Ce que le système prélève, rapporté à l'ASSIETTE des revenus d'activité
    #: et non au PIB. Zéro quand l'assiette n'est pas chargée, et la convention
    #: « assiette » se replie alors sur l'ancienne.
    taux_prelevement: float = 0.0
    #: Le taux unique que la proposition substitue à tous les autres.
    taux_liberal: float = 0.0
    #: Année à compter de laquelle ce taux s'applique. Avant elle, le
    #: scénario 6 prélève les taux réels comme tout le monde.
    annee_bascule: int = 0
    #: Comment la recette du scénario 6 est établie : ``assiette``, en
    #: appliquant son taux à l'assiette mesurée, ou ``rapport``, l'ancienne
    #: convention, qui lui appliquait un rapport de taux légaux.
    convention_recette: str = CONVENTION_RAPPORT
    #: Part de la masse versée qui est une pension de RÉVERSION, et que le
    #: rapport ne décrit pas — ``masse_du_scenario`` dit pourquoi.
    part_derives: float = 0.0
    #: Les scénarios notionnels reconduisent-ils la réversion ?
    reversion_servie: bool = True

    def depense(self, scenario: str) -> float:
        """Ce que le système coûterait cette année-là, en part de PIB.

        Le rapport ne multiplie que la part des droits DIRECTS de la base : il
        ne décrit qu'eux, et ``masse_du_scenario`` dit pourquoi.
        """
        return masse_du_scenario(self.depenses, self.part_derives,
                                 self.rapports[scenario], scenario,
                                 self.reversion_servie)

    def ressources_de(self, scenario: str) -> float:
        """Ce qu'un système peut compter comme ressources, en part de PIB.

        Le système actuel encaisse tout. Un scénario notionnel perd deux
        choses, et il faut les distinguer parce qu'elles n'ont pas la même
        cause.

        LA RECETTE SUIT LE DROIT. Aucun scénario notionnel ne sert l'AVPF, les
        majorations pour enfants, ni rien pendant une année de chômage : il ne
        peut pas compter ce que la CNAF et l'Unédic versent pour ces droits-là.
        C'est ``retrait``, et il vaut pour les cinq.

        LA RECETTE SUIT LE TAUX. Le scénario 6 remplace tous les taux par 18 %
        à compter de la bascule ; ce qui est prélevé baisse donc, et la part
        COTISÉE des ressources baisse avec.

        LA CONTRIBUTION D'ÉQUILIBRE DE L'ÉTAT DISPARAÎT, ET L'ÉTAT COTISE À
        18 % COMME TOUT EMPLOYEUR. C'est une décision du Parti libéral, prise
        le 19 septembre 2026, et elle était jusque-là un ACCIDENT DE
        CONSTRUCTION plutôt qu'un choix : ce poste est marqué ``contributive``
        dans ``equilibre.py``, il entre donc dans ``part_contributive`` — 77,3 %
        des ressources, dont 65,6 de cotisations et 11,7 de contribution — et
        se trouve remplacé par les 18 %, sans que rien ne l'écrive. Le raccord
        est juste parce que l'assiette est celle des salaires et traitements de
        TOUTES les branches : les traitements des fonctionnaires y sont, et les
        18 % qu'on leur applique SONT ce que l'État verse désormais. Reconduire
        la contribution en plus la compterait deux fois.

        LES SUBVENTIONS D'ÉQUILIBRE NE SONT PAS RECONDUITES NON PLUS, et
        l'argument n'est pas comptable mais logique. Une subvention d'équilibre
        comble le compte d'un régime dont les cotisants ont disparu avant les
        retraités — la SNCF, les mines, les marins. **Le scénario 6 fusionne
        tous les régimes : cette catégorie cesse d'exister.** Il n'y a plus de
        retraité sans cotisants dès lors qu'il n'y a plus qu'un régime, et donc
        plus rien à équilibrer par le budget. Les pensions de ces régimes-là
        sont servies comme les autres : pour partie recalculées à la baisse par
        le notionnel, pour partie portées par les cotisants du système unifié.
        Décision du Parti libéral, 19 septembre 2026.

        Elle coûte 0,27 point de PIB au scénario 6, et c'est un coût qu'il faut
        se réjouir de payer : reconduire une subvention dont l'objet a disparu
        était l'hypothèse la plus flatteuse du modèle.

        LES IMPÔTS ET TAXES AFFECTÉS NE SONT PAS RECONDUITS — 14,1 % des
        ressources, 57 milliards en 2024. Décision du Parti libéral, 19
        septembre 2026, et il faut dire par quel argument elle NE passe PAS :
        on avait cru un temps que ce poste compensait les allègements généraux
        de cotisations patronales, qu'un système sans exonération ne consent
        pas. C'est faux, et le dépôt l'a établi le 19 septembre 2026 : la TVA
        qui compense ces allègements finance la branche maladie, et le compte
        de la CNAV n'en porte aucune ligne. L'argument qui vaut est celui qui
        vaut pour les 18 % : **un compte notionnel ne crédite que ce qui est
        assis sur un revenu d'activité.** Un impôt affecté n'acquiert de droits
        à personne ; le porter au crédit d'un système qui ne rend que ce qui a
        été cotisé, c'est lui prêter une recette sans contrepartie.

        ET IL FAUT LE RETIRER UNE FOIS, PAS DEUX. Un tiers de ce poste est la
        CSG du fonds de solidarité vieillesse — ce que le fonds verse aux
        régimes, 19,6 des 57 milliards de 2024 —, et elle sortait DÉJÀ par
        ``retrait``, lu du côté de ce versement. Retirer le poste en entier sans toucher au retrait
        la ferait sortir deux fois. ``retrait_par_impot`` est cette somme, et
        elle est rendue au retrait à l'instant où le poste s'en va.
        """
        if scenario == "actuel":
            return self.ressources
        if scenario == "notionnel_liberal" and self.recette_par_assiette:
            # Le taux plein sur l'assiette mesurée. Trois postes ne sont pas
            # reconduits — la contribution d'équilibre, qui est REMPLACÉE par
            # les 18 % appliqués aux traitements ; les subventions, dont la
            # fusion supprime l'objet ; les impôts affectés, qui n'acquièrent
            # de droits à personne. Ce qui reste : les transferts et les autres
            # produits, 7 % des ressources de 2024.
            pleine = self.ressources * self.taux_liberal / self.taux_prelevement
            autres = self.ressources * (1.0 - self.part_contributive
                                        - self.part_subventions
                                        - self.part_impots)
            # La CSG du fonds de solidarité vieillesse vient de sortir avec le
            # poste : la retirer encore ici la retirerait deux fois.
            return pleine + autres - (self.retrait - self.retrait_par_impot)
        rapport = self.rapports_recettes.get(scenario, 1.0)
        cotisees = self.ressources * self.part_contributive
        autres = self.ressources - cotisees
        return cotisees * rapport + autres - self.retrait

    @property
    def recette_par_assiette(self) -> bool:
        """La convention du programme s'applique-t-elle à cette année ?

        Trois conditions, et la moindre manquante fait retomber sur l'ancienne
        convention plutôt que sur une division par zéro : la convention doit
        être demandée, l'assiette doit avoir été chargée, et la bascule doit
        avoir eu lieu — avant elle, le scénario 6 prélève les taux réels comme
        tout le monde.
        """
        return (
            self.convention_recette == CONVENTION_ASSIETTE
            and self.taux_prelevement > 0.0
            and self.taux_liberal > 0.0
            and 0 < self.annee_bascule <= self.annee
        )

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
    #: Convention de recette du scénario 6 : ``assiette`` ou ``rapport``.
    #: ``assiette`` est celle du programme, et celle que la page affiche depuis
    #: le 19 septembre 2026 ; ``rapport`` reste calculable pour dire ce qu'elle
    #: valait, comme ``ponderation="egale"`` garde l'ancienne pondération.
    convention_recette: str = CONVENTION_ASSIETTE
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
    # Ce que le droit en vigueur prélève sur chacune de ces carrières, année par
    # année et sans bascule : le dénominateur du rapport de recettes. Un compte
    # de plus par couple, soit un sixième de calcul en plus sur la grille.
    reels = {
        (code, generation): simulateur.constructeur_employeur.construire(
            comparaison.carriere,
            annee_liquidation=comparaison.carriere.annee_liquidation,
            annee_debut=comparaison.carriere.premiere_annee,
        ).cotisations
        for (code, generation), comparaison in grille.resultats.items()
    }
    pensionnes = [
        Pensionne(
            code=code,
            generation=generation,
            annee_liquidation=comparaison.carriere.annee_liquidation,
            annee_ouverture_garantie=(
                comparaison.notionnel_liberal.garantie_vieillesse.annee_ouverture
            ),
            pensions={
                **{
                    scenario: comparaison.en_euros_constants(
                        getattr(comparaison, scenario).pension_annuelle
                    )
                    for scenario, _ in SCENARIOS
                },
                # Le scénario 6 est ramené à sa part CONTRIBUTIVE : la garantie
                # est financée par l'impôt, elle ne pèse pas sur le compte des
                # cotisants, et la porter dans les deux lignes reviendrait à la
                # faire payer deux fois. C'est la symétrie de ce que la recette
                # fait déjà — la CSG de solidarité sort des ressources.
                "notionnel_liberal": comparaison.en_euros_constants(
                    comparaison.notionnel_liberal.garantie_vieillesse.pension_contributive
                ),
                COMPOSANTE_GARANTIE: comparaison.en_euros_constants(
                    comparaison.notionnel_liberal.garantie_vieillesse.complement
                ),
            },
            cotisations={
                # Le dénominateur ne peut pas être le compte du scénario 4.
                # Celui-là fusionne les régimes à la bascule et prélève ensuite
                # le taux du statut pivot privé pour TOUT LE MONDE : c'est déjà
                # une réforme, et la comparer au scénario 6 reviendrait à
                # comparer deux réformes. Ce qu'il faut est ce que le DROIT EN
                # VIGUEUR prélèverait, régime par régime, sur les mêmes
                # carrières et jusqu'en 2070 — c'est-à-dire le même compte
                # SANS régime fusionné.
                TAUX_REELS: {
                    ligne.annee: ligne.cotisation
                    for ligne in reels[(code, generation)]
                },
                "notionnel_liberal": {
                    ligne.annee: ligne.cotisation
                    for ligne in comparaison.notionnel_liberal.compte.cotisations
                },
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


#: Les masses que la revalorisation des pensions SERVIES atteint : les cinq
#: scénarios notionnels, et eux seuls. Le scénario 1 en est exclu parce que le
#: droit l'indexe sur les prix — article L. 161-23-1 du code de la sécurité
#: sociale, qui renvoie au coefficient de l'article L. 161-25 —, et la garantie
#: vieillesse parce que l'article L. 816-2 renvoie l'ASPA au même coefficient.
#: C'est cette asymétrie qui fait tout : une règle commune se simplifierait
#: dans le rapport de masses, celle-ci ne se simplifie pas.
CLES_REVALORISEES: frozenset[str] = frozenset(
    cle for cle, _ in SCENARIOS if cle != "actuel"
)

#: Les scénarios 3 et 5, dont la règle d'indexation NE COMMENCE QU'À LA
#: BASCULE. Une réforme prospective ne gèle pas l'indexation du stock : elle
#: change la règle pour toutes les pensions à compter du jour où elle
#: s'applique, celles qui étaient déjà servies comprises — c'est ce que font
#: les réformes réelles, et c'est ce que le programme retient. Ce qu'elle ne
#: fait pas, c'est agir AVANT elle-même : une pension servie en 2010 a été
#: revalorisée sur les prix de 2010 à 2025, quoi qu'il advienne en 2026.
#:
#: D'où ``max(liquidation, bascule)`` et non « liquidée après la bascule ».
#: La nuance n'est pas rhétorique : la seconde forme priverait à jamais de la
#: règle nouvelle tous ceux qui étaient déjà retraités, et ferait du scénario 3
#: une réforme qui met cinquante ans à s'appliquer. La première la leur donne
#: le jour de la bascule, et laisse le passé intact — ce qu'un test exige.
CLES_PROSPECTIVES: frozenset[str] = frozenset({
    "notionnel_prospectif", "notionnel_prospectif_employeur",
})


class RevalorisationServie:
    """Ce que devient une pension DÉJÀ LIQUIDÉE, année après année.

    UN SYSTÈME NOTIONNEL A DEUX RÈGLES D'INDEXATION, ET NON UNE. La première
    fait grossir le compte pendant la carrière ; la seconde revalorise la
    pension une fois qu'elle est servie. Les pays qui ont fait ce système les
    règlent séparément : la Suède revalorise le compte sur l'indice des
    salaires et la pension liquidée sur ce même indice diminué de 1,6 point ;
    l'Italie revalorise le compte sur le PIB et la pension liquidée sur les
    prix.

    Le dépôt n'en portait qu'une. Les masses de la page « Coût » figeaient la
    pension en euros constants pour toute la retraite, ce qui est une
    indexation sur les PRIX qui ne disait pas son nom — correcte pour le
    scénario 1, où c'est la loi, fausse pour les cinq autres. Car la seconde
    règle est déjà écrite ailleurs dans le modèle, et depuis toujours : le
    diviseur de conversion vaut l'espérance de vie résiduelle parce que
    ``taux_anticipe_conversion`` est nul, et il ne la vaut QUE si la rente est
    ensuite revalorisée au taux auquel le compte l'a été. Le modèle promettait
    donc une rente indexée sur la masse salariale et en servait une indexée sur
    les prix ; il payait moins que son propre contrat.

    CE QUE REND CETTE CLASSE est le coefficient qui corrige l'écart, en euros
    CONSTANTS puisque c'est l'unité des masses : le produit des taux
    d'indexation depuis la liquidation, déflaté des prix de la même période. Il
    vaut 1 l'année de la liquidation, ×1,15 au bout de vingt ans de projection
    — 2,45 % contre 1,75 % —, et jusqu'à ×3 pour les vingt années qui suivent
    une liquidation de 1960, où la masse salariale progressait de cinq points
    par an au-dessus des prix.

    CE QU'ELLE N'EST PAS. Elle ne choisit pas la règle : elle applique celle
    que ``mode_indexation`` porte déjà, quelle qu'elle soit. Sous le triple
    lock inversé, qui passe sous les prix la plupart des années, son
    coefficient descend en dessous de 1 et la correction joue à la baisse.
    C'est la conséquence logique de la règle, et non un défaut.
    """

    def __init__(self, simulateur: Simulateur,
                 premiere_annee: int, derniere_annee: int) -> None:
        macro = simulateur.macro
        indexation = simulateur.indexation
        #: L'année à partir de laquelle une réforme PROSPECTIVE revalorise ce
        #: qu'elle sert : voir :data:`CLES_PROSPECTIVES`.
        self.annee_bascule = simulateur.parametres.annee_bascule
        self.premiere_annee = premiere_annee
        self.derniere_annee = max(derniere_annee, premiere_annee)
        index = 1.0
        self._index: dict[int, float] = {self.premiere_annee: index}
        for annee in range(self.premiere_annee + 1, self.derniere_annee + 1):
            # Le taux d'indexation est NOMINAL, les masses sont en euros
            # constants : on le déflate année par année, et non en bloc. Un
            # produit de taux nominaux divisé par une inflation cumulée serait
            # la même chose ici, mais cesserait de l'être dès qu'un plancher ou
            # un lissage s'appliquerait à l'un des deux — et il y en a un.
            index *= (1.0 + indexation.taux(annee).taux) * macro.coefficient_prix(
                annee, annee - 1
            )
            self._index[annee] = index

    def _valeur(self, annee: int) -> float:
        borne = min(max(annee, self.premiere_annee), self.derniere_annee)
        return self._index[borne]

    def coefficient(self, annee_liquidation: int, annee: int) -> float:
        """Ce que vaut en ``annee``, en euros constants, un euro de pension
        liquidé en ``annee_liquidation``.

        Vaut exactement 1 l'année de la liquidation et avant elle : une pension
        qui n'est pas encore servie ne se revalorise pas.
        """
        if annee <= annee_liquidation:
            return 1.0
        depart = self._valeur(annee_liquidation)
        return self._valeur(annee) / depart if depart else 1.0


def _masses(pensionnes: list[Pensionne], population: Population, annee: int,
            poids_cas: dict[str, float],
            revalorisation: RevalorisationServie) -> tuple[dict[str, float], int]:
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

    Ces deux-là pèsent des TÊTES. Deux autres pèsent des EUROS :
    ``poids_revalorise`` porte ce que la pension est devenue depuis la
    liquidation sous la règle d'indexation — voir :class:`RevalorisationServie`
    —, et ``poids_revalorise_prospectif`` fait de même en ne comptant que ce
    qui suit la bascule, parce que les scénarios 3 et 5 n'existent pas avant
    elle. Le scénario 1 et la garantie
    vieillesse gardent le poids en têtes, parce que le droit les indexe sur les
    prix et que les masses sont déjà en euros constants.
    """
    masses = {cle: 0.0 for cle in CLES_MASSES}
    vivants = 0
    for pensionne in pensionnes:
        part = poids_cas.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        poids = 0.0
        poids_garantie = 0.0
        poids_revalorise = 0.0
        poids_revalorise_prospectif = 0.0
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            liquidation = pensionne.annee_liquidation + decalage
            if annee < liquidation:
                continue
            effectif = population.effectif(
                annee - pensionne.generation - decalage, annee
            )
            poids += effectif
            # Le troisième poids porte la revalorisation des pensions SERVIES,
            # et il faut qu'il soit à part : le coefficient dépend de l'année
            # de liquidation, qui n'est pas la même pour les cinq cohortes de
            # la tranche. Le sortir de la boucle appliquerait à toutes celui de
            # la génération du milieu, soit deux ans d'indexation en trop d'un
            # côté et en moins de l'autre.
            poids_revalorise += effectif * revalorisation.coefficient(
                liquidation, annee
            )
            poids_revalorise_prospectif += effectif * revalorisation.coefficient(
                max(liquidation, revalorisation.annee_bascule), annee
            )
            # La garantie n'entre qu'à 65 ans, même pour qui est parti plus
            # tôt : avant, on ne touche pas le minimum vieillesse.
            if annee >= pensionne.annee_ouverture_garantie + decalage:
                poids_garantie += effectif
        if poids <= 0.0:
            continue
        vivants += 1
        for cle in CLES_MASSES:
            if cle == COMPOSANTE_GARANTIE:
                poids_cle = poids_garantie
            elif cle in CLES_PROSPECTIVES:
                poids_cle = poids_revalorise_prospectif
            elif cle in CLES_REVALORISEES:
                poids_cle = poids_revalorise
            else:
                poids_cle = poids
            masses[cle] += part * poids_cle * pensionne.pensions[cle]
    return masses, vivants


def _masses_cotisations(pensionnes: list[Pensionne], population: Population,
                        annee: int, poids_cas: dict[str, float]) -> dict[str, float]:
    """Ce que les COTISANTS versent une année donnée, sous les deux barèmes.

    Le pendant de :func:`_masses`, du côté de la recette, et bâti sur la même
    grille : les mêmes carrières, les mêmes poids de cas types, les mêmes
    effectifs de classe d'âge. Une différence, et elle tient à ce qu'une
    cotisation n'est pas une pension. Une pension ne bouge plus après la
    liquidation, si bien que la cohorte voisine sert le même montant décalé
    d'un an ; une cotisation change chaque année de la carrière, et la cohorte
    née un an plus tôt verse, l'année ``t``, ce que la cohorte de la grille
    versait en ``t − 1``. C'est cette année-là qu'on va chercher.

    Le poids des cas types est celui des RETRAITÉS de leur caisse, faute d'une
    série de cotisants : c'est la réserve principale de cette grandeur, et elle
    est écrite dans ``limites.md``. Elle surreprésente les régimes qui
    s'éteignent, dont les taux sont parmi les plus élevés, et pousse donc le
    rapport vers le bas.
    """
    masses = {cle: 0.0 for cle in CLES_RECETTES}
    for pensionne in pensionnes:
        part = poids_cas.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            poids = population.effectif(annee - pensionne.generation - decalage, annee)
            if poids <= 0.0:
                continue
            for cle in CLES_RECETTES:
                versee = pensionne.cotisations.get(cle, {}).get(annee - decalage, 0.0)
                if versee:
                    masses[cle] += part * poids * versee
    return masses


def _rapports_recettes(masses: dict[str, float], annee: int,
                       bascule: int) -> dict[str, float]:
    """Rapport de la recette de chaque système à celle du système actuel.

    Un pour tous, sauf pour le scénario 6. Ce n'est pas une approximation :
    voir ``CLES_RECETTES``. Zéro cotisation au dénominateur — les années
    d'avant la première carrière de la grille — rend un rapport de un, qui est
    la valeur neutre et non un résultat.

    AVANT LA BASCULE, le rapport vaut un PAR CONSTRUCTION, et il est écrit
    plutôt que calculé. La raison est un effet de bord de la grille : chaque
    génération y représente les cinq classes d'âge qui l'entourent, et la
    cohorte née deux ans plus tôt verse, l'année ``t``, ce que la génération de
    la grille verse en ``t + 2``. Deux ans avant la bascule, ce ``t + 2`` est
    déjà à 18 %, et la recette de 2025 baissait alors d'un dixième de point de
    PIB pour une réforme qui n'a pas encore eu lieu. Après la bascule, le même
    décalage joue en sens inverse et s'éteint en deux ans : c'est la marche que
    ``limites.md`` décrit déjà du côté des pensions, et elle est bornée.
    """
    rapports = {scenario: 1.0 for scenario, _ in SCENARIOS}
    reference = masses[TAUX_REELS]
    if annee >= bascule and reference > 0.0:
        rapports["notionnel_liberal"] = masses["notionnel_liberal"] / reference
    return rapports


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
            poids: Callable[[int], dict[str, float]],
            revalorisation: RevalorisationServie,
            reversion_servie: bool = True) -> Avenir:
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
                                poids(derniere_publiee), revalorisation)
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
        poids_annee = poids(annee)
        masses, _ = _masses(pensionnes, population, annee, poids_annee,
                            revalorisation)
        if masses["actuel"] <= 0.0:
            continue
        cotisations = _masses_cotisations(pensionnes, population, annee, poids_annee)
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
            rapports_recettes=_rapports_recettes(
                cotisations, annee, simulateur.parametres.annee_bascule),
            part_derives=depenses.part_droits_derives(annee),
            reversion_servie=reversion_servie,
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
           derniere_annee_pib: int, assiette: AssietteActivite | None,
           taux_liberal: float, annee_bascule: int,
           convention: str, depenses: DepensesRetraite,
           reversion_servie: bool = True) -> Solde:
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

    def taux_prelevement(annee: int) -> float:
        """Le taux de prélèvement de l'année, ou celui de la dernière connue.

        Il faut le calculer sur une année où l'assiette est PUBLIÉE : la
        reconduire au-delà reviendrait à figer un montant en euros courants,
        alors que c'est le taux qui se reconduit. Voir
        ``AssietteActivite.taux_prelevement``.
        """
        if assiette is None:
            return 0.0
        reference = assiette.annee_de_reference(annee)
        return assiette.taux_prelevement(comptes.ressource(reference), reference)

    lignes = [
        SoldeAnnuel(
            annee=annee,
            projete=annee > comptes.derniere_annee_observee,
            ressources=comptes.ressource(annee),
            depenses=comptes.depense(annee),
            rapports=par_annee[annee].rapports,
            pib=par_annee[annee].pib if annee <= derniere_annee_pib else 0.0,
            retrait=comptes.recette_non_acquise(annee),
            rapports_recettes=par_annee[annee].rapports_recettes,
            part_contributive=comptes.part_contributive(annee),
            part_impots=comptes.part("impots_et_taxes", annee),
            retrait_par_impot=comptes.recette_non_acquise(annee, par_impot=True),
            part_subventions=comptes.part("subventions_equilibre", annee),
            taux_prelevement=taux_prelevement(annee),
            taux_liberal=taux_liberal,
            annee_bascule=annee_bascule,
            convention_recette=convention,
            part_derives=depenses.part_droits_derives(annee),
            reversion_servie=reversion_servie,
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
                  liquidation: str = "droit",
                  assiette: AssietteActivite | None = None,
                  convention_recette: str = CONVENTION_ASSIETTE,
                  convention_reversion: str = CONVENTION_REVERSION_SERVIE) -> Cout:
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

    ``convention_reversion`` dit ce que les scénarios notionnels font de la
    RÉVERSION, qu'aucun d'eux ne calcule : ``servie``, reconduite telle quelle
    comme en Italie, ou ``supprimee``, comme en Suède. Ce n'est pas un réglage
    d'affichage : la réversion pèse un dixième de la masse versée, et
    ``CONVENTIONS_REVERSION`` dit pourquoi le dépôt prend la plus coûteuse par
    défaut.

    ``comptes`` porte le second terme du bilan — les ressources. Il est
    facultatif : sans lui, tout ce qui précède est calculé à l'identique et le
    solde reste vide, ce qui est exactement l'état du dépôt avant que ces
    ressources n'existent.
    """
    if convention_recette not in CONVENTIONS_RECETTE:
        raise ValueError(
            f"convention de recette inconnue : {convention_recette!r} "
            f"(attendu : {CONVENTIONS_RECETTE})"
        )
    if convention_reversion not in CONVENTIONS_REVERSION:
        raise ValueError(
            f"convention de réversion inconnue : {convention_reversion!r} "
            f"(attendu : {CONVENTIONS_REVERSION})"
        )
    reversion_servie = convention_reversion == CONVENTION_REVERSION_SERVIE
    pensionnes, echecs = _pensionnes(simulateur, cas_types, liquidation)
    poids = _ponderation(simulateur, ponderation, cas_types)
    macro = simulateur.macro
    annee_euros = simulateur.parametres.annee_euros_constants
    # La seconde règle d'indexation, construite une fois pour les deux régimes
    # de la page — les années publiées et la projection. Elle part de la plus
    # ancienne liquidation de la grille, parce qu'un coefficient ne se rattrape
    # pas : il se cumule depuis le départ en retraite.
    revalorisation = RevalorisationServie(
        simulateur,
        min((p.annee_liquidation for p in pensionnes), default=HORIZON) - _DEMI_TRANCHE,
        HORIZON,
    )

    lignes: list[CoutAnnuel] = []
    for annee in depenses.annees():
        masses, vivants = _masses(pensionnes, population, annee, poids(annee),
                                  revalorisation)
        if masses["actuel"] <= 0.0:
            continue
        lignes.append(CoutAnnuel(
            annee=annee,
            observee=depenses.depense(annee),
            coefficient_constants=macro.coefficient_prix(annee, annee_euros),
            part_pib=depenses.part_pib(annee),
            rapports=_rapports(masses),
            pensionnes=vivants,
            part_derives=depenses.part_droits_derives(annee),
            reversion_servie=reversion_servie,
        ))

    fiabilite = min(
        (depenses.fiabilite(ligne.annee) for ligne in lignes),
        default=Fiabilite.ESTIMEE,
    )
    avenir = _avenir(pensionnes, depenses, population, simulateur, poids,
                     revalorisation, reversion_servie)
    return Cout(
        annees=lignes,
        avenir=avenir,
        solde=_solde(
            avenir, comptes, depenses.pib.derniere_annee, assiette,
            simulateur.parametres.taux_cotisation_liberal,
            simulateur.parametres.annee_bascule, convention_recette,
            depenses, reversion_servie,
        ) if comptes is not None and avenir.annees else Solde(),
        annee_euros=annee_euros,
        generations=generations(),
        echecs=echecs,
        ponderation=ponderation,
        liquidation=liquidation,
        convention_recette=convention_recette,
        poids=poids(depenses.derniere_annee),
        # Le contrefactuel ne peut jamais valoir mieux qu'« estimé » : la
        # dépense observée est certifiée, le rapport qui la corrige ne l'est
        # pas et ne peut pas l'être — aucune institution ne publie ce qu'un
        # système qui n'a pas existé aurait coûté.
        fiabilite=min(fiabilite, Fiabilite.ESTIMEE),
    )
