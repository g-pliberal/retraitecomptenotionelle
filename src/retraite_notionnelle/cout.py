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
4. **La grille s'arrête à 2,5 fois le salaire moyen.** Le plus haut des cas
   types est la profession libérale ; le simulateur, lui, va jusqu'à dix fois
   le salaire moyen. Une règle qui ne mord qu'au-dessus de la grille ne
   déplace donc RIEN ici, ni en dépense ni en recette — le déplafonnement de
   l'assiette du 20 septembre 2026 a laissé coût, solde et coefficients
   identiques au centime, faute de quelqu'un pour être concerné.
5. **Les recettes réagissent sur deux points, et sur deux seulement.** Le
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

from dataclasses import dataclass, field, replace
from typing import Callable, Sequence

from .castypes import (
    CAS_TYPES,
    VARIANTES_LIQUIDATION,
    CasType,
    calculer_cas_types,
    poids_effectifs,
    poids_egaux,
)
from .config import RevalorisationStock, SituationFoyer
from .donnees.assiette import AssietteActivite
from .donnees.chargement import Fiabilite, SerieAnnuelle
from .donnees.depenses import DepensesRetraite
from .donnees.distribution import DistributionPensions
from .donnees.taux import CourbeTauxSansRisque
from .donnees.equilibre import ORGANISMES, POSTES, ComptesRetraite
from .donnees.population import Population
from .garantie import _manque_moyen, cout_garantie
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

#: Ce que la garantie REGARDE, cas type par cas type : la pension contributive
#: du scénario 6 et la rente du pilier capitalisé, comptées à partir de
#: soixante-cinq ans et revalorisées jusqu'à l'année. Ce n'est ni un système ni
#: une composante, et aucun tableau ne l'affiche : c'est la masse par laquelle
#: la distribution des pensions est DÉPLACÉE avant qu'on lui applique le
#: plancher — voir :class:`GarantieDistribution`.
RESSOURCES_GARANTIE = "ressources_garantie_liberal"

#: Tout ce que la grille des cas types sait calculer : les six systèmes, et
#: les ressources que la garantie regarde.
CLES_CAS_TYPES: tuple[str, ...] = tuple(scenario for scenario, _ in SCENARIOS) + (
    RESSOURCES_GARANTIE,
)

#: Tout ce qui a un RAPPORT à la masse du système actuel : les six systèmes,
#: et la composante. La composante n'est pas calculée sur la grille — une
#: allocation différentielle ne se lit pas sur treize carrières — mais sur la
#: distribution des pensions, et son rapport est écrit après coup.
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
#: ``supprimee`` est la convention du dépôt depuis le 19 septembre 2026, et
#: elle n'est pas un choix de plus : elle est la RÈGLE DÉJÀ APPLIQUÉE aux
#: trente-huit autres lignes. Les scénarios 2 à 6 retirent tous les avantages
#: non contributifs — minimum contributif, trimestres gratuits, majorations
#: pour enfants, départ anticipé —, et l'inventaire du dépôt range la réversion
#: parmi eux depuis toujours : « non contributif au sens strict, la cotisation
#: de l'assuré ayant déjà été rendue par sa propre pension », et « de très
#: loin, la PREMIÈRE dépense non contributive du système ». La servir dans un
#: compte notionnel était donc l'exception non écrite, pas la règle. C'est le
#: chemin de la Suède, où un compte notionnel ne verse qu'à son titulaire.
#:
#: Ce que ces cinq scénarios mesurent est d'ailleurs cela même : ce qu'une
#: retraite composée UNIQUEMENT de part contributive représente. Une pension de
#: réversion n'en est pas.
#:
#: ``servie`` reste calculable, et c'est le chemin de l'Italie, où le capital
#: notionnel du défunt se partage. Elle a été la convention du dépôt pendant
#: quelques heures, le temps que le volet C sépare les deux masses et que le
#: programme tranche ; on la garde pour lire ce qu'elle vaut, comme on garde
#: ``convention_recette="rapport"``.
#:
#: LE SCÉNARIO 1 SERT LA RÉVERSION DANS TOUS LES CAS, et aucune convention ne
#: le touche : il est le droit en vigueur, et le droit en vigueur la sert.
#: ``masse_du_scenario`` l'écrit en premier.
CONVENTION_REVERSION_SERVIE = "servie"
CONVENTION_REVERSION_SUPPRIMEE = "supprimee"
CONVENTIONS_REVERSION: tuple[str, ...] = (
    CONVENTION_REVERSION_SERVIE, CONVENTION_REVERSION_SUPPRIMEE,
)

#: LE BILAN, POSTE PAR POSTE. Le COR publie la structure des ressources du
#: système de retraite en sept lignes — cotisations, contribution d'équilibre,
#: subventions, impôts et taxes, transferts avec leurs « dont », produits
#: financiers, autres produits. ``SoldeAnnuel.postes_ressources`` rend la
#: même chose pour CHAQUE système, en part de PIB, en appliquant à chaque
#: poste la règle que ``ressources_de`` applique au total : les deux se
#: somment exactement, et un test le tient. Les six premiers codes sont ceux
#: de ``equilibre.POSTES`` ; les trois « dont » ventilent le poste des
#: transferts par celui qui paie, et le quatrième l'impôt par ce qu'en verse
#: le fonds de solidarité vieillesse, seule part de ce poste que le modèle
#: sache nommer.
POSTES_RESSOURCES: tuple[str, ...] = tuple(poste.code for poste in POSTES)
DONT_TRANSFERTS: tuple[str, ...] = (
    "transferts_famille", "transferts_chomage", "transferts_autres",
)
DONT_IMPOTS: tuple[str, ...] = ("impots_solidarite", "impots_autres")

#: Ce qu'un système verse, en trois lignes que ``masse_du_scenario`` sépare
#: déjà sans les nommer : les pensions de droit direct, la garantie vieillesse
#: — financée par l'impôt, hors du compte des cotisants, et redite ici pour
#: que le tableau la montre —, les pensions de réversion. Les deux premières
#: font la dépense du système ; la garantie s'y ajoute pour mémoire.
POSTES_DEPENSES: tuple[str, ...] = (
    "droits_directs", "droits_derives", "garantie_vieillesse",
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

#: Les deux côtés d'un bilan, et l'effectif qui pèse un cas type de chaque
#: côté : ses RETRAITÉS pour une masse de pensions, ses COTISANTS pour une
#: masse de cotisations. Un même mode de pondération se lit des deux côtés.
COTE_RETRAITES = "retraites"
COTE_COTISANTS = "cotisants"
COTES: tuple[str, ...] = (COTE_RETRAITES, COTE_COTISANTS)

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
    #: Ce que le PILIER CAPITALISÉ de cette carrière encaisse, prélève et
    #: détient, année par année, en euros courants : versement brut, frais sur
    #: versement, frais de gestion, encours de fin d'année. Vide pour qui n'a
    #: pas de pilier.
    pilier: dict[int, tuple[float, float, float, float]] = field(default_factory=dict)
    #: La rente du pilier, en euros courants de la liquidation : brute (le
    #: capital divisé par le diviseur) et nette des frais sur la réserve et
    #: sur arrérages. Le pilier sert une rente nominale constante.
    rente_pilier: tuple[float, float] = (0.0, 0.0)


@dataclass(frozen=True)
class PilierAnnuel:
    """Le pilier capitalisé de TOUS les cotisants, une année, PAR EURO VERSÉ.

    Ce n'est ni une ressource ni une dépense de la répartition : le pilier
    constitue un capital au nom de chacun. Ce qui compte ici est ce que
    l'enveloppe prélève sur l'ensemble des cotisants, et ce qu'elle leur sert,
    sous le régime de frais réglé.

    LA GRILLE NE DONNE QUE DES RAPPORTS, JAMAIS UN NIVEAU : c'est la règle de
    toute la page Coût, et elle vaut ici. Chaque grandeur est rapportée aux
    versements de l'année sur la même grille, en euros courants de la même
    année ; le niveau vient d'ailleurs — les versements du pilier sont les
    cotisations du système 4, ancrées sur le compte du COR, multipliées par le
    rapport des deux taux (10 points contre 18). :meth:`niveaux` fait le
    produit.
    """

    annee: int
    #: Frais sur versement de l'année, par euro versé.
    frais_versement: float
    #: Frais de gestion de l'année, par euro versé.
    frais_gestion: float
    #: Encours de fin d'année, par euro versé dans l'année.
    encours: float
    #: Rentes de l'année avant les frais qui les grèvent, par euro versé.
    rentes_brutes: float
    #: Rentes servies, nettes, par euro versé.
    rentes: float

    @property
    def frais_accumulation(self) -> float:
        return self.frais_versement + self.frais_gestion

    @property
    def frais_rentes(self) -> float:
        return self.rentes_brutes - self.rentes

    @property
    def frais(self) -> float:
        """Tout ce que l'enveloppe prélève dans l'année, par euro versé."""
        return self.frais_accumulation + self.frais_rentes

    @property
    def taux_frais_encours(self) -> float:
        """Les frais de gestion de l'année rapportés à l'encours."""
        return self.frais_gestion / self.encours if self.encours > 0 else 0.0

    def niveaux(self, versements: float) -> dict[str, float]:
        """Chaque grandeur au niveau des ``versements`` donnés, même unité."""
        return {
            "versements": versements,
            "frais_versement": self.frais_versement * versements,
            "frais_gestion": self.frais_gestion * versements,
            "frais_accumulation": self.frais_accumulation * versements,
            "encours": self.encours * versements,
            "rentes_brutes": self.rentes_brutes * versements,
            "rentes": self.rentes * versements,
            "frais_rentes": self.frais_rentes * versements,
            "frais": self.frais * versements,
        }


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
    #: La garantie de l'année, lue sur la distribution des pensions : le
    #: facteur de déplacement et les bénéficiaires, que la page redit.
    garantie: GarantieProjetee | None = None
    #: Les scénarios notionnels reconduisent-ils la réversion ? Non, depuis le
    #: 19 septembre 2026 : elle est un avantage non contributif, et ils les
    #: retirent tous. Voir ``CONVENTIONS_REVERSION``.
    reversion_servie: bool = False
    #: La bascule a-t-elle eu lieu ? Ne sert qu'aux réformes PROSPECTIVES, qui
    #: sont le système actuel avant elle et servent donc sa réversion ;
    #: après, elles ne la servent plus, à personne.
    reforme_en_vigueur: bool = True

    def cout(self, scenario: str) -> float:
        """Coût du système, en millions d'euros courants de l'année."""
        return masse_du_scenario(self.observee, self.part_derives,
                                 self.rapports[scenario], scenario,
                                 self.reversion_servie, self.reforme_en_vigueur)

    def cout_constants(self, scenario: str) -> float:
        return self.cout(scenario) * self.coefficient_constants

    @property
    def observee_constants(self) -> float:
        return self.observee * self.coefficient_constants


def masse_du_scenario(base: float, part_derives: float, rapport: float,
                      scenario: str, reversion_servie: bool = False,
                      reforme_en_vigueur: bool = True) -> float:
    """Applique un rapport de masses à une base, et au seul morceau qu'il décrit.

    LE RAPPORT NE DÉCRIT QUE LES DROITS DIRECTS. Il est le quotient de deux
    masses de pensions calculées sur les treize cas types, qui n'ont ni conjoint
    ni survivant : aucune réversion n'y entre. La base, elle, porte les deux —
    un huitième de réversion en 2010, un dixième en 2024, un dix-huitième en
    2070. Multiplier l'une par l'autre, comme le modèle le faisait jusqu'au
    19 septembre 2026, revenait à réduire la réversion dans la même proportion
    que les pensions propres, sans que rien ne l'ait décidé.

    Le rapport ne multiplie donc que la part DIRECTE de la base. La part
    dérivée, elle, suit la convention du scénario, et la convention du dépôt est
    de ne PAS la servir : une pension de réversion est un avantage non
    contributif, et les scénarios notionnels les retirent tous.
    ``CONVENTIONS_REVERSION`` dit d'où vient cette règle.

    ``reforme_en_vigueur`` ne sert qu'aux réformes PROSPECTIVES, et à une seule
    chose : une réforme qui ne commence qu'à sa bascule ne peut rien avoir
    changé AVANT elle. Les scénarios 3 et 5 sont, par construction, le système
    actuel jusqu'à ce jour-là — ils y recopient ses pensions, et un test tient
    l'égalité de leurs courbes à l'euro près. Ils y servent donc la réversion
    comme lui. À compter de la bascule, ils ne la servent plus, à personne. Les
    réformes RÉTROACTIVES, elles, recalculent tout le monde depuis 1941 : le
    drapeau ne les concerne pas et vaut vrai pour elles.

    DEUX CAS À PART. Le SYSTÈME ACTUEL rend sa base sans rien y toucher : il est
    le droit en vigueur, il sert la réversion, et aucune convention ne le
    touche. Son rapport vaut un et la formule le rendrait de toute façon, mais
    l'écrire évite qu'un arrondi ne fasse mentir l'identité. Et la GARANTIE
    VIEILLESSE n'est pas un système : c'est une allocation différentielle
    calculée, elle aussi, sur les seuls droits directs, et à laquelle on
    n'ajoute donc aucune réversion.
    """
    if scenario == "actuel":
        return base
    directe = base * (1.0 - part_derives) * rapport
    if scenario == COMPOSANTE_GARANTIE:
        return directe
    if reversion_servie:
        return directe + base * part_derives
    if scenario in CLES_PROSPECTIVES and not reforme_en_vigueur:
        return directe + base * part_derives
    return directe


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
    #: La garantie de l'année, lue sur la distribution des pensions.
    garantie: GarantieProjetee | None = None
    #: Rapport de la RECETTE de chaque système à celle du système actuel. Un
    #: partout, sauf pour le scénario 6 à compter de la bascule.
    rapports_recettes: dict[str, float] = field(default_factory=dict)
    #: Part de la masse versée qui est une pension de RÉVERSION, et que le
    #: rapport ne décrit pas — ``masse_du_scenario`` dit pourquoi.
    part_derives: float = 0.0
    #: Les scénarios notionnels reconduisent-ils la réversion ? Non, depuis le
    #: 19 septembre 2026 : elle est un avantage non contributif, et ils les
    #: retirent tous. Voir ``CONVENTIONS_REVERSION``.
    reversion_servie: bool = False
    #: La bascule a-t-elle eu lieu ? Ne sert qu'aux réformes PROSPECTIVES, qui
    #: sont le système actuel avant elle et servent donc sa réversion ;
    #: après, elles ne la servent plus, à personne.
    reforme_en_vigueur: bool = True
    #: Le pilier capitalisé de l'année, tous cotisants, par euro versé ;
    #: ``None`` avant la bascule.
    pilier: PilierAnnuel | None = None

    def cout_constants(self, scenario: str) -> float:
        """Coût du système, en millions d'euros constants de référence."""
        return masse_du_scenario(self.base, self.part_derives,
                                 self.rapports[scenario], scenario,
                                 self.reversion_servie, self.reforme_en_vigueur)

    def cout(self, scenario: str) -> float:
        """Le même coût, ramené aux euros courants de son année."""
        return self.cout_constants(scenario) / self.coefficient_constants

    def part_pib(self, scenario: str) -> float:
        """Part du PIB : deux grandeurs de la même année, donc deux euros courants."""
        return self.cout(scenario) / self.pib if self.pib else 0.0

    def reprises_constants(self) -> float:
        """Ce que les successions rendent de la garantie, en euros constants."""
        return self.garantie.reprises_constants if self.garantie else 0.0

    def reprises(self) -> float:
        """Les mêmes reprises, en euros courants de l'année."""
        return self.reprises_constants() / self.coefficient_constants

    def part_pib_reprises(self) -> float:
        return self.reprises() / self.pib if self.pib else 0.0

    def garantie_nette_constants(self) -> float:
        """La garantie versée moins ce que les successions en rendent."""
        return self.cout_constants(COMPOSANTE_GARANTIE) - self.reprises_constants()


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

    def cumul_reprises(self) -> float:
        """Ce que les successions rendent sur les années projetées, en euros constants."""
        return sum(ligne.reprises_constants() for ligne in self.projetees())


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
    #: Part des ressources qui est un impôt ou une taxe affectés : CSG, taxe
    #: sur les salaires, forfait social, C3S, taxes agricoles. Le scénario 6
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
    #: Les scénarios notionnels reconduisent-ils la réversion ? Non, depuis le
    #: 19 septembre 2026 : elle est un avantage non contributif, et ils les
    #: retirent tous. Voir ``CONVENTIONS_REVERSION``.
    reversion_servie: bool = False
    #: La bascule a-t-elle eu lieu ? Ne sert qu'aux réformes PROSPECTIVES, qui
    #: sont le système actuel avant elle et servent donc sa réversion ;
    #: après, elles ne la servent plus, à personne.
    reforme_en_vigueur: bool = True
    #: Part de chaque poste dans les ressources de l'année, au découpage du
    #: COR (``equilibre.POSTES``). ``part_contributive``, ``part_impots`` et
    #: ``part_subventions`` en sont des sommes ; le détail sert au tableau
    #: poste par poste, et à rien d'autre.
    parts: dict[str, float] = field(default_factory=dict)
    #: ``retrait``, payeur par payeur : ce que la branche famille, l'assurance
    #: chômage et le fonds de solidarité vieillesse versent chacun pour des
    #: droits qu'aucun scénario notionnel ne sert, en part de PIB.
    retraits: dict[str, float] = field(default_factory=dict)

    def depense(self, scenario: str) -> float:
        """Ce que le système coûterait cette année-là, en part de PIB.

        Le rapport ne multiplie que la part des droits DIRECTS de la base : il
        ne décrit qu'eux, et ``masse_du_scenario`` dit pourquoi.
        """
        return masse_du_scenario(self.depenses, self.part_derives,
                                 self.rapports[scenario], scenario,
                                 self.reversion_servie, self.reforme_en_vigueur)

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

    def postes_ressources(self, scenario: str) -> dict[str, float]:
        """Les ressources d'un système, poste par poste, en part de PIB.

        C'est ``ressources_de`` écrit ligne à ligne, au découpage du rapport
        annuel du COR, et les lignes somment exactement au total : la même
        règle est appliquée à chaque poste, jamais une autre. Les postes du
        COR sont rendus sous leur code (``POSTES_RESSOURCES``) ; les « dont »
        (``DONT_TRANSFERTS``, ``DONT_IMPOTS``) ventilent deux d'entre eux et
        ne s'ajoutent pas au total.

        LE SYSTÈME ACTUEL encaisse chaque poste tel que le COR le publie, et
        les « dont » sont ce que la branche famille, l'assurance chômage et le
        fonds de solidarité vieillesse versent réellement — lus chez le payeur
        dans la fenêtre connue, à part constante des ressources ailleurs.

        LA PROPOSITION, à compter de la bascule et sous la convention de
        l'assiette, remplace la ligne des cotisations par 18 % de l'assiette
        des revenus d'activité, et met trois postes à zéro — la contribution
        d'équilibre de l'État, remplacée par ces 18 % appliqués aux
        traitements ; les subventions d'équilibre, dont la fusion des régimes
        supprime l'objet ; les impôts et taxes affectés, qui n'acquièrent de
        droits à personne. Des transferts, elle ne garde que ce qui ne paie
        pas un droit qu'elle a supprimé. ``ressources_de`` dit pourquoi,
        décision par décision.

        LES AUTRES SCÉNARIOS NOTIONNELS, et la proposition avant sa bascule,
        gardent chaque poste à sa valeur, la part cotisée multipliée par le
        rapport de recette, et retranchent chez le payeur ce qu'ils ne peuvent
        pas compter : les deux transferts sur leur ligne, la CSG du fonds de
        solidarité sur celle de l'impôt.
        """
        total = self.ressources
        parts = self.parts
        famille = self.retraits.get("famille", 0.0)
        chomage = self.retraits.get("chomage", 0.0)
        solidarite = self.retraits.get("solidarite", 0.0)
        if scenario == "actuel":
            postes = {code: total * parts.get(code, 0.0) for code in POSTES_RESSOURCES}
            postes["transferts_famille"] = famille
            postes["transferts_chomage"] = chomage
            postes["impots_solidarite"] = solidarite
        elif scenario == "notionnel_liberal" and self.recette_par_assiette:
            postes = {
                "cotisations": total * self.taux_liberal / self.taux_prelevement,
                "contribution_equilibre_etat": 0.0,
                "subventions_equilibre": 0.0,
                "impots_et_taxes": 0.0,
                "transferts": total * parts.get("transferts", 0.0) - famille - chomage,
                "autres_produits": total * parts.get("autres_produits", 0.0),
                "transferts_famille": 0.0,
                "transferts_chomage": 0.0,
                "impots_solidarite": 0.0,
            }
        else:
            rapport = self.rapports_recettes.get(scenario, 1.0)
            postes = {
                "cotisations": total * parts.get("cotisations", 0.0) * rapport,
                "contribution_equilibre_etat":
                    total * parts.get("contribution_equilibre_etat", 0.0) * rapport,
                "subventions_equilibre": total * parts.get("subventions_equilibre", 0.0),
                "impots_et_taxes": total * parts.get("impots_et_taxes", 0.0) - solidarite,
                "transferts": total * parts.get("transferts", 0.0) - famille - chomage,
                "autres_produits": total * parts.get("autres_produits", 0.0),
                "transferts_famille": 0.0,
                "transferts_chomage": 0.0,
                "impots_solidarite": 0.0,
            }
        postes["transferts_autres"] = (postes["transferts"] - postes["transferts_famille"]
                                       - postes["transferts_chomage"])
        postes["impots_autres"] = postes["impots_et_taxes"] - postes["impots_solidarite"]
        return postes

    def postes_depenses(self, scenario: str) -> dict[str, float]:
        """Ce qu'un système verse, en trois lignes et en part de PIB.

        ``droits_directs`` et ``droits_derives`` somment exactement à
        ``depense`` : la première est la part directe de la base multipliée
        par le rapport du système, la seconde est ce que ``masse_du_scenario``
        y ajoute — la réversion entière pour le système actuel, rien pour un
        scénario notionnel qui ne la sert pas. ``garantie_vieillesse`` est la
        composante que l'impôt finance, redite ici pour la proposition et
        nulle pour les autres : elle n'entre pas dans ``depense``, et ce
        tableau ne l'y ajoute pas non plus.
        """
        base = self.depenses
        directe_base = base * (1.0 - self.part_derives)
        if scenario == "actuel":
            return {
                "droits_directs": directe_base,
                "droits_derives": base * self.part_derives,
                "garantie_vieillesse": 0.0,
            }
        directs = directe_base * self.rapports[scenario]
        garantie = (directe_base * self.rapports.get(COMPOSANTE_GARANTIE, 0.0)
                    if scenario == "notionnel_liberal" else 0.0)
        return {
            "droits_directs": directs,
            "droits_derives": self.depense(scenario) - directs,
            "garantie_vieillesse": garantie,
        }


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



@dataclass(frozen=True)
class PensionFinancee:
    """Ce que les comptes financent d'une pension promise, sur la durée du service.

    LE PROBLÈME QUE CETTE CLASSE RÉSOUT. Le site affiche quatre pensions
    calculées sur une même carrière, et la première — le droit en vigueur — se
    lit comme une promesse tenue. Elle ne l'est pas : le système qui la sert
    est en déficit, et le COR projette ce déficit jusqu'en 2070. Un visiteur
    qui partira dans vingt ans lit donc un montant que les comptes de son
    année de départ ne financent pas. Le dire est la seule façon de ne pas
    mentir ; l'écrire en toutes lettres sans le chiffrer serait à peine mieux.

    CE QU'ELLE CALCULE. Le coefficient d'équilibre de ``SoldeAnnuel`` est déjà
    le facteur qui fait tomber une année juste. Il change d'une année à
    l'autre, et une pension se sert vingt ou trente ans : le coefficient de
    l'année du départ FLATTE donc qui part tôt, puisqu'il ignore les années où
    le déficit se creuse. Le coefficient retenu ici est la moyenne des
    coefficients annuels PONDÉRÉE PAR LA SURVIE — ce que le système finance
    sur la durée où la pension est effectivement servie, chaque année comptant
    pour la part des partants encore en vie.

    CE QU'ELLE N'EST PAS. Ce n'est pas une prévision, et le mot « prévision »
    n'a rien à faire ici : rogner toutes les pensions d'un même facteur est
    UNE façon d'équilibrer une année, ce n'est pas celle que le Parlement
    choisira. Les deux autres sont chiffrées à côté — la hausse de cotisation
    qui financerait le même manque, et le déficit laissé tel quel, c'est-à-dire
    emprunté. Aucune des trois n'est plus probable que les autres ; elles
    disent ensemble la TAILLE de l'écart, qui est le seul fait.

    CE QU'ELLE IGNORE. Le quatrième levier — reculer l'âge — ne se chiffre pas
    ici, parce qu'il ne s'applique pas à une pension déjà liquidée : il déplace
    la date du départ, et le simulateur le mesure déjà, en changeant l'âge.
    """

    scenario: str
    #: L'année du départ demandée, telle que la carrière la porte.
    annee_liquidation: int
    #: Première année du service que les comptes du COR couvrent. Elle vaut
    #: ``annee_liquidation`` sauf pour un départ antérieur à ces comptes.
    premiere_annee: int
    #: Dernière année du service couverte : l'horizon du COR, ou la fin de la
    #: courbe de survie quand celle-ci s'éteint avant.
    derniere_annee: int
    #: Coefficient d'équilibre de ``premiere_annee``, le seul qui se vérifie
    #: ligne à ligne dans le tableau de la page Coût.
    coefficient_depart: float
    #: La moyenne pondérée par la survie, sur la fenêtre couverte.
    coefficient: float
    #: Part de la rente — pondérée par la survie, elle aussi — que la fenêtre
    #: couvre. Moins de un quand la pension se sert au-delà de l'horizon du
    #: COR, et la page le dit plutôt que de prolonger une projection.
    part_couverte: float
    #: Le manque de ``premiere_annee``, en part de PIB. Positif quand le
    #: système est en déficit, négatif quand il a une marge.
    manque_pib: float
    #: Le même manque, en points de l'assiette des revenus d'activité.
    points_assiette: float
    #: Le même manque, en hausse relative des ressources cotisées.
    hausse_cotisations: float
    #: L'année de l'assiette qui a servi à convertir le manque en points.
    annee_assiette: int

    @property
    def manque(self) -> float:
        """De combien il faudrait rogner, en part de la pension. Négatif : une marge."""
        return 1.0 - self.coefficient

    @property
    def depart_couvert(self) -> bool:
        """Les comptes couvrent-ils l'année du départ elle-même ?"""
        return self.premiere_annee == self.annee_liquidation

    @property
    def entiere(self) -> bool:
        """La fenêtre couvre-t-elle toute la durée de service de la pension ?"""
        return self.part_couverte >= 0.999

    def servie(self, montant: float, hors_repartition: float = 0.0) -> float:
        """Le montant que les comptes financent, la capitalisation mise à part.

        Le coefficient est celui de la RÉPARTITION : il dit ce que les
        cotisations de l'année paient. Une rente capitalisée sort d'un
        placement déjà constitué, qu'aucun déficit de la répartition
        n'atteint — la multiplier reviendrait à faire porter à l'épargne le
        manque du système qui ne la détient pas.
        """
        return (montant - hors_repartition) * self.coefficient + hors_repartition


def financer(solde: Solde, assiette: AssietteActivite | None, scenario: str,
             annee_liquidation: int,
             poids: Sequence[float]) -> PensionFinancee | None:
    """Ce que les comptes financent de la pension du scénario, à cette date.

    ``poids`` porte, rang par rang à compter de l'année de liquidation, la
    part des partants encore en vie pendant l'année — la courbe de survie de
    la table qui a servi à convertir le capital, prise au milieu de chaque
    année. La pondération ne sort donc pas d'une convention de plus : c'est
    exactement la courbe dont le diviseur a été tiré.

    Rend ``None`` quand aucune année du service n'est couverte par les comptes
    du COR : un départ de 1980 n'a rien à lire dans un bilan qui commence en
    2002, et une page qui afficherait quand même un coefficient inventerait
    une lecture.
    """
    if not solde.annees:
        return None
    debut = max(annee_liquidation, solde.premiere_annee)
    numerateur = 0.0
    couvert = 0.0
    total = 0.0
    for rang, part in enumerate(poids):
        if part <= 0.0:
            continue
        annee = annee_liquidation + rang
        total += part
        ligne = solde.annee(annee)
        if annee < debut or ligne is None:
            continue
        numerateur += part * ligne.coefficient(scenario)
        couvert += part
    if couvert <= 0.0 or total <= 0.0:
        return None
    ligne_depart = solde.annee(debut)
    if ligne_depart is None:
        return None
    manque = -ligne_depart.solde(scenario)
    annee_assiette = assiette.derniere_annee if assiette is not None else 0
    part_assiette = (assiette.part_pib(annee_assiette)
                     if assiette is not None else 0.0)
    cotisees = ligne_depart.ressources_de(scenario) * ligne_depart.part_contributive
    return PensionFinancee(
        scenario=scenario,
        annee_liquidation=annee_liquidation,
        premiere_annee=debut,
        derniere_annee=min(annee_liquidation + len(poids) - 1,
                           solde.derniere_annee),
        coefficient_depart=ligne_depart.coefficient(scenario),
        coefficient=numerateur / couvert,
        part_couverte=couvert / total,
        manque_pib=manque,
        points_assiette=manque / part_assiette if part_assiette > 0.0 else 0.0,
        hausse_cotisations=manque / cotisees if cotisees > 0.0 else 0.0,
        annee_assiette=annee_assiette,
    )

@dataclass
class DetteAnnuelle:
    """Une année du stock : ce que les soldes cumulés depuis le départ pèsent.

    Tout est en PART DE PIB, comme le solde dont elle procède. Un stock POSITIF
    est une dette, un stock NÉGATIF une réserve : le même calcul rend les deux,
    et c'est voulu — un système qui encaisse plus qu'il ne sert accumule autant
    qu'un système qui sert plus qu'il n'encaisse, dans l'autre sens.
    """

    annee: int
    #: Croissance NOMINALE du PIB sur l'année, en fraction : c'est elle qui
    #: érode le stock rapporté au PIB.
    croissance: float
    #: Taux nominal auquel le stock de fin d'année précédente se refinance sur
    #: l'année — ou se place, si c'est une réserve —, en fraction.
    taux: float
    #: Stock en fin d'année, par système, en part de PIB.
    stocks: dict[str, float]
    #: Intérêts de l'année, par système, en part de PIB : ce que le stock de
    #: l'année précédente coûte (ou rapporte, en négatif) avant tout solde.
    interets: dict[str, float]
    #: Le solde de l'année, par système, tel que ``SoldeAnnuel.solde`` le rend.
    soldes: dict[str, float]

    def stock(self, scenario: str) -> float:
        return self.stocks[scenario]

    def interet(self, scenario: str) -> float:
        return self.interets[scenario]

    def solde(self, scenario: str) -> float:
        return self.soldes[scenario]


@dataclass
class Dette:
    """Le stock que les soldes à venir accumulent, de l'année de départ à l'horizon.

    LE SOLDE DIT LE FLUX ; CECI DIT LE STOCK. Un déficit qui se répète devient
    une dette, et une dette porte intérêt : à taux supérieur à la croissance,
    elle grossit d'elle-même, et c'est l'effet « boule de neige » que le solde
    seul ne montre pas. La récurrence est celle de toute dette publique
    rapportée au PIB :

        stock(t) = stock(t−1) × (1 + taux(t)) ÷ (1 + croissance(t)) − solde(t)

    avec, pour que l'identité se vérifie ligne à ligne,

        intérêts(t) = stock(t−1) × taux(t) ÷ (1 + croissance(t))
        stock(t)    = stock(t−1) ÷ (1 + croissance(t)) + intérêts(t) − solde(t)

    LE STOCK PART DE ZÉRO, à la dernière année observée. Ni la dette que le
    système porte aujourd'hui ni les réserves qu'il détient n'y sont : le COR
    les chiffre à part, et les ajouter ferait un stock de deux périmètres. Ce
    que la série dit est donc ce que les soldes À VENIR ajoutent — ou
    retirent —, et rien d'autre.

    LE TAUX EST LU, PAS CHOISI. C'est le taux à un an que la courbe des
    souverains les mieux notés de la zone euro, publiée par la BCE, implique
    pour chaque année : le forward à un an de ``CourbeTauxSansRisque``, celui-là
    même auquel le pilier capitalisé place ses versements. Le pilier et la dette
    lisent ainsi la même courbe, et personne n'a à prévoir un taux. Au-delà de
    la dernière maturité cotée, le taux est prolongé à plat et la fiabilité
    tombe à « estimée ». ``ecart_taux`` déplace ce taux d'un écart constant —
    un point en plus ou en moins —, ce qui est la seule sensibilité que la page
    montre : elle dit ce que le résultat doit à cette lecture.

    LA CROISSANCE EST CELLE DE LA PROJECTION : le PIB nominal de ``Avenir``,
    qui suit les hypothèses du COR composées avec sa trajectoire d'emploi — la
    même série que lit l'indexation des comptes, depuis que la page a cessé de
    se fabriquer un PIB à elle (action 65).

    LA DETTE PUBLIQUE EST POSÉE DESSOUS, PAS MÉLANGÉE. ``dette_publique_observee``
    porte ce que le pays doit déjà, au sens de Maastricht, tel que l'INSEE le
    publie année par année jusqu'au départ ; ``dette_publique`` tient ce
    niveau à plat, en part de PIB, et y ajoute le stock d'un système — comme
    si le reste des administrations publiques maintenait sa dette et que la
    retraite seule la déplaçait. Ce n'est pas une prévision de la dette du
    pays, qui dépend de soldes que ce module ne connaît pas ; c'est l'échelle
    à laquelle le stock d'un système se lit, et la distance entre deux
    systèmes y est exactement la distance entre leurs stocks.
    """

    annees: list[DetteAnnuelle] = field(default_factory=list)
    #: Année de départ, stock nul : la dernière année observée du solde.
    annee_depart: int = 0
    #: Écart appliqué au taux lu sur la courbe, en fraction (0,01 = un point).
    ecart_taux: float = 0.0
    #: Date de la courbe des taux dont le taux est lu.
    date_courbe: str = ""
    #: Dernière année où le taux est lu sur une maturité cotée ; au-delà, il
    #: est prolongé à plat.
    derniere_annee_cotee: int = 0
    #: Niveau du taux : celui de la courbe tant qu'elle est cotée, « estimée »
    #: au-delà. Le stock, lui, n'est jamais mieux qu'estimé.
    fiabilite_taux: Fiabilite = Fiabilite.ESTIMEE
    fiabilite: Fiabilite = Fiabilite.ESTIMEE
    #: La dette des administrations publiques observée, en part de PIB, par
    #: année, jusqu'à l'année de départ incluse. Vide quand la série manque.
    dette_publique_observee: dict[int, float] = field(default_factory=dict)
    #: L'année dont la dette publique observée sert de point de départ :
    #: l'année de départ elle-même, ou la dernière publiée avant elle.
    annee_dette_publique: int = 0

    @property
    def premiere_annee(self) -> int:
        return self.annees[0].annee

    @property
    def dette_publique_depart(self) -> float:
        """Ce que le pays doit au départ, en part de PIB ; zéro sans série."""
        return self.dette_publique_observee.get(self.annee_dette_publique, 0.0)

    def dette_publique(self, scenario: str, millesime: int) -> float:
        """La dette publique de départ, plus ce que le système y a ajouté.

        Le reste des administrations publiques est supposé tenir sa dette à
        plat, en part de PIB : seul le stock du système bouge. À l'année de
        départ, c'est la dette observée ; avant, la fonction ne dit rien de
        plus que ``dette_publique_observee``.
        """
        return self.dette_publique_depart + self.stock(scenario, millesime)

    @property
    def derniere_annee(self) -> int:
        return self.annees[-1].annee

    def annee(self, millesime: int) -> DetteAnnuelle | None:
        for ligne in self.annees:
            if ligne.annee == millesime:
                return ligne
        return None

    def stock(self, scenario: str, millesime: int) -> float:
        """Le stock en fin d'année, et zéro à l'année de départ ou avant."""
        ligne = self.annee(millesime)
        return ligne.stock(scenario) if ligne else 0.0

    def horizon(self, scenario: str) -> float:
        """Le stock à la dernière année, en part de PIB."""
        return self.annees[-1].stock(scenario) if self.annees else 0.0

    def cumul_soldes(self, scenario: str) -> float:
        """Ce que les soldes seuls accumulent, SANS intérêts, en points de PIB.

        Le signe est celui du stock : positif quand les déficits l'emportent.
        C'est le stock qu'on aurait à taux égal à la croissance, et la
        différence avec ``horizon`` est ce que l'effet boule de neige ajoute.
        """
        return -sum(ligne.solde(scenario) for ligne in self.annees)

    def cumul_interets(self, scenario: str) -> float:
        """Les intérêts cumulés sur la période, en points de PIB."""
        return sum(ligne.interet(scenario) for ligne in self.annees)

    def pic(self, scenario: str) -> DetteAnnuelle | None:
        """L'année où le stock est le plus haut, ``None`` s'il n'est jamais positif."""
        haut = None
        for ligne in self.annees:
            if ligne.stock(scenario) > 0.0 and (
                haut is None or ligne.stock(scenario) > haut.stock(scenario)
            ):
                haut = ligne
        return haut

    def premiere_annee_decroissance(self, scenario: str) -> int | None:
        """Première année où une dette positive cesse de croître, ``None`` sinon."""
        precedent = 0.0
        for ligne in self.annees:
            courant = ligne.stock(scenario)
            if precedent > 0.0 and courant < precedent:
                return ligne.annee
            precedent = courant
        return None


def calculer_dette(solde: Solde, avenir: Avenir, courbe: CourbeTauxSansRisque,
                   ecart_taux: float = 0.0,
                   dette_publique: SerieAnnuelle | None = None) -> Dette:
    """Le stock que les soldes projetés accumulent, système par système.

    Rien n'est resimulé : les soldes sont ceux de ``Solde``, le PIB celui de
    ``Avenir``, le taux celui de la courbe. La fonction ne fait que cumuler,
    et c'est ce qui la rend gratuite — et ce qui la borne aux années où le
    solde est PROJETÉ : le passé a été financé, et son stock est ailleurs.

    ``dette_publique`` est la série observée de la dette des administrations
    publiques, en part de PIB. Elle n'entre dans aucun cumul : elle est
    recopiée jusqu'à l'année de départ, et la dernière valeur publiée avant
    ou à cette année devient le point de départ de ``Dette.dette_publique``.
    """
    projetees = solde.projetees()
    if not projetees:
        return Dette()
    scenarios = [scenario for scenario, _ in SCENARIOS]
    stocks = {scenario: 0.0 for scenario in scenarios}
    fiabilite_taux = courbe.fiabilite_publiee
    lignes: list[DetteAnnuelle] = []
    for ligne in projetees:
        precedente = avenir.annee(ligne.annee - 1)
        courante = avenir.annee(ligne.annee)
        if precedente is None or courante is None or precedente.pib <= 0.0:
            break
        croissance = courante.pib / precedente.pib - 1.0
        placement = courbe.placement(ligne.annee - 1, 1)
        taux = placement.taux + ecart_taux
        fiabilite_taux = min(fiabilite_taux, placement.fiabilite)
        interets: dict[str, float] = {}
        soldes: dict[str, float] = {}
        for scenario in scenarios:
            interets[scenario] = stocks[scenario] * taux / (1.0 + croissance)
            soldes[scenario] = ligne.solde(scenario)
            stocks[scenario] = (
                stocks[scenario] / (1.0 + croissance)
                + interets[scenario] - soldes[scenario]
            )
        lignes.append(DetteAnnuelle(
            annee=ligne.annee,
            croissance=croissance,
            taux=taux,
            stocks=dict(stocks),
            interets=interets,
            soldes=soldes,
        ))
    if not lignes:
        return Dette()
    depart = lignes[0].annee - 1
    observee: dict[int, float] = {}
    annee_dette_publique = 0
    if dette_publique is not None:
        for annee in dette_publique.annees():
            if annee <= depart:
                observee[annee] = dette_publique(annee)
                annee_dette_publique = annee
    return Dette(
        annees=lignes,
        annee_depart=depart,
        ecart_taux=ecart_taux,
        date_courbe=courbe.date,
        derniere_annee_cotee=courbe.annee + courbe.maturite_maximale,
        fiabilite_taux=fiabilite_taux,
        fiabilite=Fiabilite.ESTIMEE,
        dette_publique_observee=observee,
        annee_dette_publique=annee_dette_publique,
    )


@dataclass
class Cout:
    """La série complète, et les cumuls qu'on en tire."""

    annees: list[CoutAnnuel] = field(default_factory=list)
    #: La trajectoire de la répartition, passé récent et avenir.
    avenir: Avenir = field(default_factory=Avenir)
    #: Le bilan : ce qui rentre face à ce que chaque système ferait sortir.
    solde: Solde = field(default_factory=Solde)
    #: Le stock que les soldes projetés accumulent, avec intérêts.
    dette: Dette = field(default_factory=Dette)
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
    #: Les mêmes poids du côté de la RECETTE — les cotisants de chaque caisse
    #: et non ses retraités —, la même année. Égaux aux premiers sous
    #: ``ponderation="egale"``.
    poids_cotisants: dict[str, float] = field(default_factory=dict)
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
                # Ce que la garantie regarde : la pension contributive ET la
                # rente du pilier capitalisé, à la liquidation. La grille ne
                # sert plus à chiffrer le complément — elle n'a pas de queue
                # basse —, seulement à dire de combien les pensions du
                # scénario 6 déplacent la distribution observée.
                RESSOURCES_GARANTIE: comparaison.en_euros_constants(
                    comparaison.notionnel_liberal.garantie_vieillesse.ressources
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
            pilier=_flux_pilier(comparaison),
            rente_pilier=_rente_pilier(comparaison),
        )
        for (code, generation), comparaison in grille.resultats.items()
    ]
    motifs: dict[str, int] = {}
    for motif in grille.echecs.values():
        motifs[motif] = motifs.get(motif, 0) + 1
    return pensionnes, motifs


def _flux_pilier(comparaison) -> dict[int, tuple[float, float, float, float]]:
    """Les flux annuels du pilier capitalisé d'une carrière, en euros courants."""
    pilier = comparaison.notionnel_liberal.capitalisation
    if pilier is None or not pilier.actif:
        return {}
    return {
        annee.annee: (annee.versement_brut, annee.frais_versement,
                      annee.frais_gestion, annee.encours)
        for annee in pilier.annees
    }


def _rente_pilier(comparaison) -> tuple[float, float]:
    """La rente du pilier d'une carrière, brute puis nette de ses frais."""
    pilier = comparaison.notionnel_liberal.capitalisation
    if pilier is None or not pilier.actif:
        return (0.0, 0.0)
    return (pilier.capital / pilier.conversion.diviseur, pilier.rente_annuelle)


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
#: BASCULE. Ce qu'une réforme prospective fait du STOCK — les pensions déjà
#: servies le jour où elle s'applique — est un choix, et il est réglé par
#: ``Parametres.revalorisation_stock`` (voir
#: :meth:`RevalorisationServie.coefficient_stock`). Par défaut, depuis le
#: 20 septembre 2026, le stock garde les prix que le droit lui a promis, et la
#: règle nouvelle ne vaut que pour les pensions liquidées à compter de la
#: bascule. En variante, la réforme fait passer tout le stock à sa règle le
#: jour de la bascule, comme le modèle le faisait jusque-là. Dans les deux
#: cas, elle n'agit jamais AVANT elle-même : une pension servie en 2010 a été
#: revalorisée sur les prix de 2010 à 2025, quoi qu'il advienne en 2026, et un
#: test tient l'égalité des courbes avant la bascule.
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
        #: Le stock à la bascule garde-t-il les prix ? Voir :meth:`coefficient_stock`.
        self.stock_sur_les_prix = (
            simulateur.parametres.revalorisation_stock is RevalorisationStock.PRIX
        )
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

    def coefficient_stock(self, annee_liquidation: int, annee: int,
                          prospectif: bool) -> float:
        """Le même coefficient, avec la règle du STOCK à la bascule.

        Une pension liquidée à compter de la bascule suit la règle du compte
        depuis sa liquidation, dans tous les cas. Une pension liquidée AVANT :

        - sous ``PRIX``, elle garde les prix — coefficient 1 en euros
          constants — à compter de la bascule. Pour une réforme prospective,
          qui n'existait pas avant, c'est 1 depuis toujours ; pour une réforme
          rétroactive, dont le compte fictif a été revalorisé sur sa règle
          jusqu'à la bascule, le coefficient est gelé à sa valeur de la
          bascule ;
        - sous ``REINDEXE``, la réforme prospective la prend à sa règle le jour
          de la bascule (``max(liquidation, bascule)``), et la rétroactive
          l'a toujours revalorisée sur la sienne.
        """
        bascule = self.annee_bascule
        if annee_liquidation >= bascule:
            return self.coefficient(annee_liquidation, annee)
        if self.stock_sur_les_prix:
            if prospectif:
                return 1.0
            return self.coefficient(annee_liquidation, min(annee, bascule))
        if prospectif:
            return self.coefficient(bascule, annee)
        return self.coefficient(annee_liquidation, annee)


#: Les deux comptes de TÊTES que la grille rend avec ses masses : tous les
#: retraités qu'elle représente, et ceux d'entre eux qui ont atteint l'âge de
#: la garantie. Ils ne pèsent pas des euros mais des personnes — c'est par eux
#: que la distribution des pensions reçoit son effectif et sa pension moyenne.
TETES_TOUTES = "toutes"
TETES_GARANTIE = "garantie"


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
    masses = {cle: 0.0 for cle in CLES_CAS_TYPES}
    tetes = {TETES_TOUTES: 0.0, TETES_GARANTIE: 0.0}
    vivants = 0
    for pensionne in pensionnes:
        part = poids_cas.get(pensionne.code, 0.0)
        if part <= 0.0:
            continue
        poids = 0.0
        poids_garantie = 0.0
        poids_garantie_revalorise = 0.0
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
            poids_revalorise += effectif * revalorisation.coefficient_stock(
                liquidation, annee, prospectif=False
            )
            poids_revalorise_prospectif += effectif * revalorisation.coefficient_stock(
                liquidation, annee, prospectif=True
            )
            # La garantie n'entre qu'à 65 ans, même pour qui est parti plus
            # tôt : avant, on ne touche pas le minimum vieillesse.
            if annee >= pensionne.annee_ouverture_garantie + decalage:
                poids_garantie += effectif
                poids_garantie_revalorise += effectif * revalorisation.coefficient(
                    liquidation, annee
                )
        if poids <= 0.0:
            continue
        vivants += 1
        tetes[TETES_TOUTES] += part * poids
        tetes[TETES_GARANTIE] += part * poids_garantie
        for cle in CLES_CAS_TYPES:
            if cle == RESSOURCES_GARANTIE:
                poids_cle = poids_garantie_revalorise
            elif cle in CLES_PROSPECTIVES:
                poids_cle = poids_revalorise_prospectif
            elif cle in CLES_REVALORISEES:
                poids_cle = poids_revalorise
            else:
                poids_cle = poids
            masses[cle] += part * poids_cle * pensionne.pensions[cle]
    return masses, vivants, tetes


@dataclass(frozen=True)
class GarantieProjetee:
    """La garantie d'une année, chiffrée sur la distribution des pensions."""

    #: Rapport par lequel la distribution observée a été déplacée : la
    #: pension moyenne que la garantie regarde cette année-là, sur la pension
    #: moyenne du système actuel l'année de l'enquête. Un vaut « les pensions
    #: telles qu'elles sont ».
    facteur: float
    #: Retraités auxquels le barème est appliqué : ceux qui ont atteint
    #: soixante-cinq ans, sur l'échelle de l'enquête.
    effectif: float
    #: Ceux d'entre eux qui tombent sous le plancher ET la réclament.
    beneficiaires: float
    #: Coût annuel, en millions d'euros CONSTANTS de l'année de référence,
    #: pour ceux qui la réclament.
    cout_constants: float
    #: Ceux qui tombent sous le plancher, qu'ils la réclament ou non.
    ayants_droit: float = 0.0
    #: Part des ayants droit qui la réclament : ``beneficiaires`` sur
    #: ``ayants_droit``, et le coût dans la même proportion.
    taux_recours: float = 1.0
    #: Les avances que les décès de l'année libèrent, avec leurs intérêts, en
    #: millions d'euros constants : ce que les successions AURAIENT à rendre.
    avances_liberees_constants: float = 0.0
    #: Ce qu'elles rendent : la part ``part_reprise_garantie`` des avances
    #: libérées. Zéro avant la bascule, les avances commençant avec elle.
    reprises_constants: float = 0.0
    #: Les avances en cours en fin d'année, intérêts compris, en millions
    #: d'euros constants : la créance de l'État sur les bénéficiaires vivants.
    stock_avances_constants: float = 0.0
    #: Le taux réel de l'année, lu sur la courbe des taux et déflaté.
    taux_reel: float = 0.0
    #: La part de l'avance que la succession couvre, celle qui a servi :
    #: calculée sur le patrimoine des retraités, ou réglée.
    part_reprise: float = 0.0
    #: La durée moyenne d'une avance : l'espérance de vie à 65 ans de la
    #: population dont la mortalité a servi, en années.
    duree_avances: float = 0.0
    #: Cette population : le vingtile de niveau de vie où la pension moyenne
    #: des bénéficiaires les place, ou ``None`` pour la population générale.
    population_mortalite: str | None = None
    #: La part des femmes parmi les bénéficiaires, qui pèse les deux courbes
    #: de survie : les pensions des femmes sont plus basses, et elles vivent
    #: plus longtemps.
    part_femmes: float = 0.0
    #: Le nombre moyen d'avances qu'une succession porte : un bénéficiaire
    #: seul en laisse une, un couple de deux bénéficiaires en laisse deux sur
    #: la succession du survivant. Un vaut « chacun sa succession ».
    avances_par_succession: float = 1.0


class GarantieDistribution:
    """Ce que la garantie vieillesse coûte chaque année, lu sur la distribution.

    LE PROBLÈME QU'ELLE RÉSOUT. La garantie du scénario 6 est une allocation
    différentielle : son coût est tout entier celui de la queue basse de la
    distribution des pensions, et treize carrières choisies pour couvrir les
    configurations du système n'ont pas de queue basse. Chiffrée sur les cas
    types, elle valait zéro de 2030 à 2070 avant le 19 septembre 2026, puis un
    ordre de grandeur ; ``limites.md`` disait qu'il fallait la remplacer.
    C'est fait ici : le barème est appliqué à la distribution que l'échantillon
    interrégimes de retraités de la DREES publie par tranches de cent euros —
    :mod:`garantie` sait le faire pour une année —, et la grille ne sert plus
    qu'à dire de combien cette distribution BOUGE d'une année à l'autre.

    DEUX MOUVEMENTS, UN SEUL FACTEUR. Entre l'année de l'enquête et l'année
    ``t``, la distribution des ressources que la garantie regarde se déplace
    pour deux raisons : les pensions du scénario 6 ne sont pas celles du
    système actuel (le rapport contributif, plus la rente du pilier capitalisé
    qu'une allocation différentielle compte aussi), et les pensions montent en
    termes réels avec les salaires. Les deux se composent en un seul nombre,
    la pension moyenne que la garantie regarde en ``t`` sur la pension moyenne
    du système actuel l'année de l'enquête, l'une et l'autre par tête et en
    euros constants, l'une et l'autre lues sur la même grille. Le déplacement
    est proportionnel et uniforme — c'est la convention du module
    :mod:`garantie`, et elle reste un ordre de grandeur là où l'assiette
    observée est un calcul.

    L'EFFECTIF suit les têtes de la grille : les retraités de la DREES l'année
    de l'enquête, multipliés par le rapport des têtes de soixante-cinq ans et
    plus en ``t`` aux têtes de l'enquête. La garantie n'entre qu'à cet âge,
    comme l'ASPA ; qui a liquidé avant l'attend, et la distribution des
    pensions de ceux qui l'attendent est supposée celle de tous.

    LE PLANCHER est celui des paramètres, dans les euros de l'enquête : la
    garantie de base, plus l'allocation d'isolement si le foyer paramétré est
    une personne seule — le même que le simulateur applique à une carrière.
    L'enquête ne dit pas avec qui l'on vit ; la page donne l'autre plancher à
    côté, et le coût réel est entre les deux.

    CE QUI EST FIGÉ. La FORME de la distribution est celle de l'enquête, et
    elle est tenue constante : on la déplace, on ne la déforme pas. Avant
    l'année de l'enquête, le même déplacement est appliqué à rebours, ce qui
    fait du passé une extrapolation au même titre que l'avenir. Une seule
    méthode sur toute la série, plutôt qu'une falaise entre deux.

    LE RECOURS. La garantie se demande, comme l'ASPA, et le programme retient
    l'hypothèse que la DREES mesure sur celle-ci : un ayant droit sur deux la
    réclame (``Parametres.taux_recours_garantie``). Les bénéficiaires et le
    coût sont ceux qui réclament ; ``ayants_droit`` garde le compte de tous
    ceux qui tombent sous le plancher.
    """

    def __init__(self, distribution: DistributionPensions, plancher_mensuel: float,
                 pension_reference: float, effectif_par_tete: float,
                 vers_constants: float, taux_recours: float = 1.0) -> None:
        if not 0.0 < taux_recours <= 1.0:
            raise ValueError("le taux de recours est une part, entre zéro exclu et un")
        self.distribution = distribution
        #: Part des ayants droit qui réclament la garantie.
        self.taux_recours = taux_recours
        #: Le plancher, dans les euros de l'enquête.
        self.plancher_mensuel = plancher_mensuel
        #: Pension moyenne du système actuel l'année de l'enquête, par tête et
        #: en euros constants de référence : le dénominateur du facteur.
        self.pension_reference = pension_reference
        #: Retraités de l'enquête par tête de la grille la même année.
        self.effectif_par_tete = effectif_par_tete
        #: Coefficient des euros de l'enquête aux euros constants de référence.
        self.vers_constants = vers_constants

    def chiffrer(self, masses: dict[str, float], tetes: dict[str, float]) -> GarantieProjetee:
        """La garantie d'une année, d'après les masses et les têtes de la grille."""
        tetes_garantie = tetes[TETES_GARANTIE]
        if tetes_garantie <= 0.0 or self.pension_reference <= 0.0:
            return GarantieProjetee(0.0, 0.0, 0.0, 0.0)
        facteur = masses[RESSOURCES_GARANTIE] / tetes_garantie / self.pension_reference
        if facteur <= 0.0:
            return GarantieProjetee(0.0, 0.0, 0.0, 0.0)
        effectif = self.effectif_par_tete * tetes_garantie
        chiffre = cout_garantie(self.distribution, effectif, self.plancher_mensuel, facteur)
        return GarantieProjetee(
            facteur=facteur,
            effectif=effectif,
            beneficiaires=chiffre.beneficiaires * self.taux_recours,
            cout_constants=chiffre.cout_annuel_meur * self.vers_constants * self.taux_recours,
            ayants_droit=chiffre.beneficiaires,
            taux_recours=self.taux_recours,
        )


def _garantie_distribution(simulateur: Simulateur, pensionnes: list[Pensionne],
                           population: Population,
                           poids: Callable[[int], dict[str, float]],
                           revalorisation: "RevalorisationServie",
                           distribution: DistributionPensions | None = None,
                           ) -> GarantieDistribution:
    """Cale la distribution sur la grille, l'année de l'enquête."""
    if distribution is None:
        distribution = simulateur.distribution
    parametres = simulateur.parametres
    macro = simulateur.macro
    millesime = distribution.millesime
    masses, _, tetes = _masses(pensionnes, population, millesime, poids(millesime),
                               revalorisation)
    plancher = parametres.garantie_vieillesse_mensuelle + (
        parametres.allocation_isolement_mensuelle
        if parametres.situation_foyer is SituationFoyer.SEUL else 0.0
    )
    toutes = tetes[TETES_TOUTES]
    return GarantieDistribution(
        distribution=distribution,
        plancher_mensuel=plancher * macro.coefficient_prix(
            parametres.annee_euros_garantie_vieillesse, millesime),
        pension_reference=masses["actuel"] / toutes if toutes > 0.0 else 0.0,
        effectif_par_tete=(
            simulateur.effectifs.effectif("tous_regimes", millesime) / toutes
            if toutes > 0.0 else 0.0
        ),
        vers_constants=macro.coefficient_prix(
            millesime, parametres.annee_euros_constants),
        taux_recours=parametres.taux_recours_garantie,
    )


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

    Le poids des cas types est celui des COTISANTS de leur caisse, et non de
    ses retraités : ``poids_cas`` vient ici de ``simulateur.cotisants``, la
    série que le COR publie et projette régime par régime. Jusqu'au 20
    septembre 2026, c'étaient les retraités qui servaient, faute d'une série de
    cotisants, et ``limites.md`` disait le biais : les régimes qui s'éteignent
    — dont les taux sont parmi les plus élevés — comptaient leurs retraités
    d'hier au lieu de leurs cotisants de demain, et poussaient le rapport vers
    le bas.
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


def _masses_pilier(pensionnes: list[Pensionne], population: Population,
                   annee: int, poids_cotisants: dict[str, float],
                   poids_retraites: dict[str, float]) -> dict[str, float]:
    """Ce que le pilier capitalisé de TOUS les cotisants encaisse, prélève,
    détient et sert une année donnée, en euros courants.

    Bâti comme :func:`_masses_cotisations`, sur la même grille et les mêmes
    effectifs de classe d'âge, à une différence près : les cinq cohortes
    qu'une génération de la grille représente partagent l'ANNÉE CIVILE de son
    pilier, et non son âge. Une cotisation dépend de l'âge, et la cohorte
    voisine verse en ``t`` ce que la grille versait en ``t − 1`` ; un pilier
    dépend de dates — la bascule, les paliers de frais —, et la cohorte née
    deux ans plus tôt n'a pas deux ans d'encours de plus en 2026, elle en a
    zéro comme tout le monde. Chaque cohorte accumule donc au calendrier de la
    grille jusqu'à sa propre liquidation, décalée d'autant, et touche ensuite
    la rente. Les flux d'accumulation pèsent les cotisants de chaque caisse,
    les rentes pèsent ses retraités, comme les pensions ; la rente est
    nominale et constante, comme le pilier la sert.
    """
    masses = {cle: 0.0 for cle in ("versements", "frais_versement", "frais_gestion",
                                   "encours", "rentes_brutes", "rentes")}
    for pensionne in pensionnes:
        if not pensionne.pilier:
            continue
        part_cotisants = poids_cotisants.get(pensionne.code, 0.0)
        part_retraites = poids_retraites.get(pensionne.code, 0.0)
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            poids = population.effectif(annee - pensionne.generation - decalage, annee)
            if poids <= 0.0:
                continue
            flux = pensionne.pilier.get(annee)
            if (flux is not None and part_cotisants > 0.0
                    and annee <= pensionne.annee_liquidation + decalage):
                versement, frais_v, frais_g, encours = flux
                masses["versements"] += part_cotisants * poids * versement
                masses["frais_versement"] += part_cotisants * poids * frais_v
                masses["frais_gestion"] += part_cotisants * poids * frais_g
                masses["encours"] += part_cotisants * poids * encours
            if annee > pensionne.annee_liquidation + decalage and part_retraites > 0.0:
                brute, nette = pensionne.rente_pilier
                masses["rentes_brutes"] += part_retraites * poids * brute
                masses["rentes"] += part_retraites * poids * nette
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
                 cas_types: tuple[CasType, ...],
                 cote: str = COTE_RETRAITES) -> Callable[[int], dict[str, float]]:
    """Fonction qui rend le poids de chaque cas type une année donnée.

    ``cote`` dit quel effectif pèse : les RETRAITÉS de la caisse, pour une
    masse de pensions, ou ses COTISANTS, pour une masse de cotisations. Les
    deux ne disent pas la même chose, et l'écart est le plus grand là où le
    rapport de recettes mord : la SNCF a 108 000 cotisants et 158 000 retraités
    en 2024, et n'a plus aucun cotisant en 2070.

    Les poids d'effectifs varient d'une année à l'autre — la France de 1960
    comptait plus d'exploitants agricoles que de fonctionnaires —, et chaque
    série a sa fenêtre : 2004-2024 pour les retraités de la DREES, 2010-2070
    pour les cotisants du COR. Hors d'elle, la répartition du bord est
    reconduite, et la série le dit en tombant au niveau ``estimee``.
    """
    if mode not in PONDERATIONS:
        raise ValueError(f"pondération inconnue : {mode!r} (attendu : {PONDERATIONS})")
    if cote not in COTES:
        raise ValueError(f"côté inconnu : {cote!r} (attendu : {COTES})")
    if mode == "egale":
        fixes = poids_egaux(cas_types)
        return lambda annee: fixes
    effectifs = simulateur.cotisants if cote == COTE_COTISANTS else simulateur.effectifs
    memoire: dict[int, dict[str, float]] = {}

    def poids(annee: int) -> dict[str, float]:
        if annee not in memoire:
            memoire[annee] = poids_effectifs(effectifs, annee, cas_types)
        return memoire[annee]

    return poids


def _rapports(masses: dict[str, float], garantie: GarantieProjetee,
              base_constants: float, part_derives: float) -> dict[str, float]:
    """Le rapport de chaque masse à celle du système actuel, composante comprise.

    Les six systèmes viennent de la grille. La composante vient de la
    distribution, et son rapport est celui qui redonne son coût une fois
    appliqué à la base par ``masse_du_scenario`` — qui ne multiplie que les
    droits directs, la garantie n'ajoutant aucune réversion.
    """
    rapports = {scenario: masses[scenario] / masses["actuel"] for scenario, _ in SCENARIOS}
    directe = base_constants * (1.0 - part_derives)
    rapports[COMPOSANTE_GARANTIE] = (
        garantie.cout_constants / directe if directe > 0.0 else 0.0
    )
    return rapports


def _reprises_successions(lignes: list[AvenirAnnuel], simulateur: Simulateur,
                          garantie: GarantieDistribution) -> None:
    """Les avances de la garantie, leur intérêt, et ce que les successions rendent.

    LA GARANTIE EST UNE AVANCE. Le programme la reprend sur la succession dès
    le premier euro, avec intérêts, dans la limite de ce que la succession
    contient (action 47 de la feuille de route). Chaque euro versé à compter
    de la bascule devient donc une créance, qui court jusqu'au décès du
    bénéficiaire, et le coût net pour l'impôt est le versé moins ce que les
    successions rendent.

    LE TAUX EST LU, PAS CHOISI, comme celui de la dette : le forward à un an
    de la courbe des taux sans risque, déflaté par l'indice des prix de la
    projection — les avances sont tenues en euros constants, et un intérêt
    nominal sur une créance indexée compterait l'inflation deux fois.

    LES AVANCES SONT SUIVIES PAR ÂGE, PAS PAR TÊTE. La grille ne connaît pas
    chaque bénéficiaire ; elle connaît la population des bénéficiaires, et la
    table de mortalité dit comment elle se renouvelle. La population est
    supposée stationnaire sur la courbe de survie à 65 ans de la génération
    de la bascule : à chaque âge, sa part est proportionnelle aux survivants,
    et sa part de décès à ce que la courbe perd d'un âge au suivant. Un
    bénéficiaire d'un âge donné porte les compléments moyens des années
    écoulées depuis la bascule, au plus autant que son âge lui en laisse,
    capitalisés au taux réel. Les décès d'une année LIBÈRENT ces avances ; la
    succession en rend la part ``part_reprise_garantie``, et le reste est
    abandonné — c'est cette part-là que l'impôt finance pour de bon.

    LA COUVERTURE EST CALCULÉE, sauf réglage. Ce qu'une succession couvre de
    l'avance dépend du patrimoine des bénéficiaires, et le patrimoine des
    retraités selon leur PENSION n'est publié nulle part ; ce qui l'est, chez
    le COR sur l'enquête Patrimoine 2018, est le patrimoine des ménages
    retraités selon leur REVENU DISPONIBLE : le quart le plus modeste, et
    l'ensemble (``donnees/patrimoine.py``). La convention est celle-ci, et
    elle est écrite pour être discutée : chaque tranche de pension de
    l'enquête qui tombe sous le plancher reçoit une avance à la mort — son
    complément annuel capitalisé au taux réel moyen sur la durée moyenne d'une
    avance —, et la part que la succession en couvre est celle du quart le
    plus modeste pour les pensions du premier quart des retraités, celle de
    l'ensemble des retraités à partir de la médiane, et le mélange linéaire
    entre les deux ; la couverture retenue est la moyenne de ces parts, pesée
    par les avances. Une part réglée (``part_reprise_garantie``) remplace ce
    calcul.

    LA MORTALITÉ EST CELLE DES BÉNÉFICIAIRES, pas celle de tous : le vingtile
    de niveau de vie où leur pension moyenne les place, par la convention
    qui rattache déjà un cas type à un vingtile (``population_niveau_de_vie``
    du module de mortalité, docs/methodologie.md §5). Les avances sont plus
    courtes, et les décès les libèrent plus tôt. ET CE SONT SURTOUT DES
    FEMMES : leurs pensions sont plus basses, et l'enquête les distribue à
    part. La part des femmes parmi les bénéficiaires est celle des femmes
    sous le plancher, pesée par la part des femmes parmi les 65 ans et plus
    — que les courbes de survie du modèle donnent, en population
    stationnaire, faute d'un effectif de retraités par sexe dans le dépôt —,
    et les deux courbes de survie sont mélangées dans cette proportion, au
    lieu de moitié-moitié. Les femmes vivant plus longtemps, les avances
    s'allongent d'autant.

    DEUX AVANCES SUR UNE SUCCESSION. Le patrimoine du fichier est celui d'un
    MÉNAGE, et une avance est celle d'une PERSONNE : confronter l'une à
    l'autre supposait que chaque bénéficiaire laisse seul sa succession. Or
    la règle reporte la reprise au décès du conjoint survivant, et deux
    bénéficiaires qui vivent ensemble laissent DEUX avances sur UNE
    succession — presque toujours celle de la femme, qui survit. Le modèle
    calcule donc le nombre moyen d'avances par succession : la part des
    bénéficiaires de chaque sexe qui vit en couple (INSEE, recensement 2021,
    ``donnees/vie_en_couple.py``, moyennée sur les années vécues après 65 ans),
    multipliée par la probabilité que le conjoint soit lui aussi sous le
    plancher — celle de l'autre sexe, les pensions du couple étant supposées
    INDÉPENDANTES. Elles ne le sont pas, et la corrélation des revenus dans un
    couple rendrait ce nombre plus grand. C'est l'avance MULTIPLIÉE par ce
    nombre qui est confrontée au patrimoine, et la couverture qui en résulte
    s'applique à toutes.

    CE QUI EST FIGÉ. Le complément moyen tient lieu de chacun, et rien n'est
    repris avant le décès — ni au premier décès d'un couple, ni sur une
    donation : la règle les prévoit, le modèle ne les distingue pas. « Vivre
    en couple » est une cohabitation au sens du recensement, or deux concubins
    ne se succèdent pas l'un à l'autre. Et une veuve n'hérite pas toujours de
    tout : le patrimoine que sa succession porte est celui du ménage tel que
    l'enquête le mesure, ni plus ni moins. Les lignes d'avant la bascule
    restent à zéro.
    """
    parametres = simulateur.parametres
    bascule = parametres.annee_bascule
    annee_euros = parametres.annee_euros_constants
    macro = simulateur.macro
    mortalite = simulateur.mortalite
    projetees = [ligne for ligne in lignes if ligne.annee >= bascule and ligne.garantie is not None]
    if not projetees:
        return

    # 1. Le taux réel de chaque année : le forward à un an, déflaté.
    taux_reels: dict[int, float] = {}
    for ligne in projetees:
        annee = ligne.annee
        nominal = simulateur.courbe_taux.placement(annee - 1, 1).taux
        inflation = (macro.coefficient_prix(annee - 1, annee_euros)
                     / macro.coefficient_prix(annee, annee_euros) - 1.0)
        taux_reels[annee] = (1.0 + nominal) / (1.0 + inflation) - 1.0
    taux_moyen = sum(taux_reels.values()) / len(taux_reels)

    # 2. Les bénéficiaires, tranche par tranche, à l'année de l'enquête : leur
    # poids, leur complément annuel en euros constants, leur pension dans les
    # euros de l'enquête, et leur rang parmi les retraités.
    calage = garantie
    distribution = calage.distribution
    millesime = distribution.millesime
    ligne_enquete = next((ligne for ligne in lignes if ligne.annee == millesime), None)
    deplacement = (
        ligne_enquete.garantie.facteur
        if ligne_enquete is not None and ligne_enquete.garantie is not None
        and ligne_enquete.garantie.facteur > 0.0 else 1.0
    )
    tranches: list[tuple[float, float, float, float]] = []
    for tranche in distribution.tranches:
        superieure = (None if tranche.borne_superieure is None
                      else tranche.borne_superieure * deplacement)
        concernee, manque = _manque_moyen(
            tranche.borne_inferieure * deplacement, superieure, calage.plancher_mensuel)
        if concernee <= 0.0:
            continue
        milieu = (tranche.borne_inferieure if tranche.borne_superieure is None
                  else 0.5 * (tranche.borne_inferieure + tranche.borne_superieure))
        tranches.append((
            tranche.part * concernee,
            manque / concernee * 12.0 * calage.vers_constants,
            milieu * deplacement,
            distribution.part_sous(milieu),
        ))
    poids_total = sum(poids for poids, _, _, _ in tranches)

    # 3. La mortalité des bénéficiaires : le vingtile de niveau de vie le plus
    # proche de leur pension moyenne, dans les euros de l'étude de l'INSEE.
    population = None
    if poids_total > 0.0 and mortalite.annee_niveaux_de_vie is not None:
        pension_moyenne = sum(poids * pension for poids, _, pension, _ in tranches) / poids_total
        population = mortalite.population_niveau_de_vie_euros(
            pension_moyenne * macro.coefficient_prix(millesime, mortalite.annee_niveaux_de_vie))
    # Et les deux sexes, pesés comme ils le sont sous le plancher.
    courbe_h = mortalite.courbe_survie(65, bascule, "H", True, population)
    courbe_f = mortalite.courbe_survie(65, bascule, "F", True, population)
    part_femmes = 0.5
    sous_plancher = {"F": 0.0, "H": 0.0}
    if poids_total > 0.0:
        femmes_65 = sum(courbe_f)
        hommes_65 = sum(courbe_h)
        for sexe in ("F", "H"):
            par_sexe = DistributionPensions(parametres.racine_donnees, sexe=sexe)
            sous_plancher[sexe] = cout_garantie(
                par_sexe, 1.0, calage.plancher_mensuel, deplacement).part_beneficiaires
        beneficiaires_f = femmes_65 * sous_plancher["F"]
        beneficiaires_h = hommes_65 * sous_plancher["H"]
        if beneficiaires_f + beneficiaires_h > 0.0:
            part_femmes = beneficiaires_f / (beneficiaires_f + beneficiaires_h)
    longueur = max(len(courbe_h), len(courbe_f))
    survie = [
        s for s in (
            (1.0 - part_femmes) * (courbe_h[t] if t < len(courbe_h) else 0.0)
            + part_femmes * (courbe_f[t] if t < len(courbe_f) else 0.0)
            for t in range(longueur)
        ) if s > 1e-9
    ]
    if not survie:
        return
    total_survie = sum(survie)
    deces = [survie[k] - (survie[k + 1] if k + 1 < len(survie) else 0.0)
             for k in range(len(survie))]

    # 4. Le nombre moyen d'avances par succession : un bénéficiaire en couple
    # avec un autre bénéficiaire lui en laisse deux, celle du survivant.
    avances_par_succession = 1.0
    if poids_total > 0.0:
        couple = simulateur.vie_en_couple
        parts_sexe = {"F": part_femmes, "H": 1.0 - part_femmes}
        expositions = {"F": courbe_f, "H": courbe_h}
        conjoint = {"F": "H", "H": "F"}
        avances_par_succession += sum(
            parts_sexe[sexe]
            * couple.part_moyenne(sexe, list(expositions[sexe]))
            * sous_plancher[conjoint[sexe]]
            for sexe in ("F", "H")
        )

    # 5. La couverture : calculée sur le patrimoine des retraités, sauf réglage.
    part = parametres.part_reprise_garantie
    if part is None:
        patrimoine = simulateur.patrimoine
        bas = patrimoine.distribution("retraites_q1")
        haut = patrimoine.distribution("retraites")
        vers_bas = macro.coefficient_prix(annee_euros, bas.annee)
        vers_haut = macro.coefficient_prix(annee_euros, haut.annee)
        numerateur = 0.0
        denominateur = 0.0
        for poids, complement, _, rang in tranches:
            avance = (complement * ((1.0 + taux_moyen) ** total_survie - 1.0) / taux_moyen
                      if abs(taux_moyen) > 1e-12 else complement * total_survie)
            # Ce que la succession affronte n'est pas une avance, mais toutes
            # celles qu'elle porte.
            sur_succession = avance * avances_par_succession
            couverture_bas = bas.couverture(sur_succession * vers_bas)
            couverture_haut = haut.couverture(sur_succession * vers_haut)
            if rang <= 0.25:
                couverture = couverture_bas
            elif rang >= 0.5:
                couverture = couverture_haut
            else:
                couverture = couverture_bas + (couverture_haut - couverture_bas) * (rang - 0.25) / 0.25
            numerateur += poids * avance * couverture
            denominateur += poids * avance
        part = numerateur / denominateur if denominateur > 0.0 else 0.0

    # 6. Les avances, année par année.
    complements: dict[int, float] = {}
    croissance: dict[int, float] = {}
    facteur = 1.0
    stock = 0.0
    for ligne in projetees:
        annee = ligne.annee
        taux_reel = taux_reels[annee]
        facteur *= 1.0 + taux_reel
        croissance[annee] = facteur
        garantie = ligne.garantie
        verse = garantie.cout_constants
        complements[annee] = (
            verse / garantie.beneficiaires if garantie.beneficiaires > 0.0 else 0.0
        )
        liberees = 0.0
        for k, part_deces in enumerate(deces):
            avance = 0.0
            for j in range(min(k, annee - bascule) + 1):
                avance += (complements.get(annee - j, 0.0)
                           * facteur / croissance.get(annee - j, facteur))
            liberees += part_deces / total_survie * avance
        liberees *= garantie.beneficiaires
        stock = stock * (1.0 + taux_reel) + verse - liberees
        ligne.garantie = replace(
            garantie,
            avances_liberees_constants=liberees,
            reprises_constants=part * liberees,
            stock_avances_constants=stock,
            taux_reel=taux_reel,
            part_reprise=part,
            duree_avances=total_survie,
            population_mortalite=population,
            part_femmes=part_femmes,
            avances_par_succession=avances_par_succession,
        )


def _avenir(pensionnes: list[Pensionne], depenses: DepensesRetraite,
            population: Population, simulateur: Simulateur,
            poids: Callable[[int], dict[str, float]],
            revalorisation: RevalorisationServie,
            reversion_servie: bool = False,
            poids_cotisants: Callable[[int], dict[str, float]] | None = None,
            garantie: GarantieDistribution | None = None) -> Avenir:
    """La trajectoire de la répartition, de la première année ventilée à l'horizon.

    Deux régimes, une seule formule. Jusqu'à la dernière année publiée, la base
    est la dépense de répartition OBSERVÉE. Au-delà, elle est celle que le
    modèle produit, mise à l'échelle par un ancrage calculé sur cette même
    dernière année : les deux expressions coïncident exactement à la jonction.

    ``poids`` pèse les cas types dans les masses de PENSIONS, ``poids_cotisants``
    dans les masses de COTISATIONS ; sans le second, le premier sert aux deux,
    ce qui est l'ancienne convention.
    """
    if poids_cotisants is None:
        poids_cotisants = poids
    macro = simulateur.macro
    annee_euros = simulateur.parametres.annee_euros_constants
    derniere_publiee = depenses.derniere_annee

    masses_ancrage, _, _ = _masses(pensionnes, population, derniere_publiee,
                                   poids(derniere_publiee), revalorisation)
    if garantie is None:
        garantie = _garantie_distribution(simulateur, pensionnes, population,
                                          poids, revalorisation)
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
    # hypothèses de projection, TRAJECTOIRE D'EMPLOI COMPRISE — c'est-à-dire
    # ``macro.pib_nominal``, la même série que lit l'indexation des comptes, et
    # la convention que le fichier d'hypothèses énonce : « le PIB nominal suit
    # la même convention que la masse salariale ».
    #
    # LA PAGE SE FABRIQUAIT SON PROPRE PIB JUSQU'AU 20 SEPTEMBRE 2026, et le
    # dépôt en portait donc trois : celui-ci, celui de l'indexation, et celui
    # qu'implique le compte du COR. La correction d'ici était la population des
    # 20-64 ans, qui recule de 10 % d'ici 2070 là où l'emploi du scénario de
    # référence du COR recule de 6 % : un proxy inventé par le dépôt, là où la
    # projection existe et qu'il la lit déjà ailleurs. Une part de PIB dont le
    # dénominateur n'est pas celui du reste du dépôt ne se compare à rien — et
    # `limites.md` § 5 ter appelait cette substitution depuis l'action 46.
    derniere_pib = depenses.pib.derniere_annee
    pib_projete: dict[int, float] = {}
    courant = depenses.pib(derniere_pib)
    for annee in range(derniere_pib + 1, HORIZON + 1):
        courant *= 1.0 + macro.pib_nominal(annee)
        pib_projete[annee] = courant

    lignes: list[AvenirAnnuel] = []
    for annee in range(depenses.premiere_annee_ventilee, HORIZON + 1):
        poids_annee = poids(annee)
        masses, _, tetes = _masses(pensionnes, population, annee, poids_annee,
                                   revalorisation)
        if masses["actuel"] <= 0.0:
            continue
        cotisations = _masses_cotisations(pensionnes, population, annee,
                                          poids_cotisants(annee))
        projete = annee > derniere_publiee
        coefficient = macro.coefficient_prix(annee, annee_euros)
        pilier = None
        if annee >= simulateur.parametres.annee_debut_capitalisation:
            flux = _masses_pilier(pensionnes, population, annee,
                                  poids_cotisants(annee), poids_annee)
            if flux["versements"] > 0.0:
                pilier = PilierAnnuel(annee=annee, **{
                    cle: flux[cle] / flux["versements"]
                    for cle in ("frais_versement", "frais_gestion", "encours",
                                "rentes_brutes", "rentes")
                })
        base = (
            ancrage * masses["actuel"] if projete
            else depenses.repartition(annee) * coefficient
        )
        actifs = population.actifs(annee)
        part_derives = depenses.part_droits_derives(annee)
        projetee = garantie.chiffrer(masses, tetes)
        lignes.append(AvenirAnnuel(
            annee=annee,
            projete=projete,
            base=base,
            coefficient_constants=coefficient,
            pib=pib_projete.get(annee, depenses.pib(min(annee, derniere_pib))),
            rapports=_rapports(masses, projetee, base, part_derives),
            garantie=projetee,
            dependance=population.effectif_tranche(
                AGE_DEPENDANCE, population.age_maximal, annee) / actifs
            if actifs else 0.0,
            rapports_recettes=_rapports_recettes(
                cotisations, annee, simulateur.parametres.annee_bascule),
            part_derives=part_derives,
            reversion_servie=reversion_servie,
            reforme_en_vigueur=annee >= simulateur.parametres.annee_bascule,
            pilier=pilier,
        ))
    _reprises_successions(lignes, simulateur, garantie)

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
           reversion_servie: bool = False) -> Solde:
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
        """Le taux de prélèvement de l'année, mesuré puis suivi chez le COR.

        Deux temps, et ils n'ont pas le même statut. Le NIVEAU est mesuré sur
        une année où l'assiette est publiée — c'est tout ce que
        ``AssietteActivite.taux_prelevement`` sait faire, et c'est la seule
        chose que le dépôt certifie. Le PROFIL au-delà est lu chez le COR, qui
        projette ce taux dans la figure des déterminants de ses ressources.

        CE QUE CE SECOND TEMPS A CORRIGÉ. Le dépôt reconduisait le taux du bord
        tel quel, et faisait donc porter tout le recul des ressources à
        l'assiette : 42,5 % du PIB en 2025, 39,3 % en 2070. Il justifiait cette
        convention en disant que « c'est le COR qui tranche ». C'était une
        déduction tirée du total de ses ressources, non une lecture de sa
        projection — et elle le tranchait à l'envers. Le COR projette un taux
        qui BAISSE, de 32,14 % à 30,05 %, et une assiette qui tient sa part de
        PIB à un point près. La convention démentie faisait perdre 0,49 point
        de PIB de recette à la proposition en 2070.
        """
        if assiette is None:
            return 0.0
        reference = assiette.annee_de_reference(annee)
        mesure = assiette.taux_prelevement(comptes.ressource(reference), reference)
        return mesure * comptes.profil_taux(annee, reference)

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
            reforme_en_vigueur=annee >= annee_bascule,
            parts={poste.code: comptes.part(poste.code, annee) for poste in POSTES},
            retraits={
                organisme.code: comptes.recette_non_acquise(
                    annee, organisme=organisme.code)
                for organisme in ORGANISMES if organisme.droit_supprime
            },
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


#: Année jusqu'à laquelle court la somme des flux d'un engagement acquis. Les
#: cohortes de la grille qui portent un droit en 2021 sont nées avant 2004 ;
#: elles y ont quatre-vingt-seize ans, et ce qu'elles touchent encore après ne
#: se compte plus. C'est aussi l'horizon que le fichier d'hypothèses déclare
#: (``annee_fin_projection``) : au-delà, les séries macro ne projettent plus.
HORIZON_ENGAGEMENTS = 2100

#: Les écarts de taux d'actualisation dont la sensibilité est chiffrée, en
#: points au-dessus de la croissance du PIB. Zéro est la convention du COR ;
#: les autres disent de combien le niveau d'un engagement acquis dépend d'un
#: taux que personne n'observe.
ECARTS_ACTUALISATION: tuple[float, ...] = (0.0, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03)


@dataclass(frozen=True)
class EngagementAcquis:
    """Ce que le système doit DÉJÀ, au titre des droits acquis à une date.

    LE STOCK, LÀ OÙ LE RESTE DE CE MODULE EST UN FLUX. Un solde dit ce qui
    manque une année ; ceci dit ce qui est dû pour le passé, que l'avenir
    cotise ou non. C'est la grandeur du tableau supplémentaire du SEC 2010, et
    la seule qu'un modèle en comptes notionnels produise nativement.

    POURQUOI ELLE SE CALCULE SANS CONVENTION DE PLUS. Actualiser demande un
    taux, et un taux est une décision — sauf que le COR en publie un : la note
    de sa figure du solde moyen dit que « le taux d'actualisation est supposé
    égal chaque année à la croissance annuelle du PIB », convention que le
    décret n° 2014-654 relatif au Comité de suivi des retraites encadre.
    Actualiser au rythme du PIB revient à SOMMER les flux exprimés en part de
    PIB : le facteur d'actualisation et le dénominateur se simplifient
    exactement. L'unité de tout le dépôt porte donc déjà l'actualisation, et
    l'engagement est la somme, année par année, de ce que les droits acquis
    feront verser, chacun rapporté au PIB de son année.

    CE QUE ``sensibilite`` SERT À DIRE. Que ce niveau n'est pas un fait. Un
    engagement acquis est une somme actualisée, et le même droit vaut deux
    fois moins sous un taux supérieur de trois points. Eurostat publie 397 %
    du PIB pour 2021 sous la convention du tableau 29 ; le dépôt trouve
    beaucoup plus sous celle du COR, et la différence est un taux, pas un
    droit. La page le montre plutôt que de choisir un chiffre.
    """

    annee: int
    #: Dernière année sommée. Au-delà, les cohortes concernées sont éteintes.
    horizon: int
    _par_scenario: dict[str, float]
    #: La part due à ceux qui ont DÉJÀ liquidé à la date de référence : leur
    #: pension entière est un droit acquis. Le reste est celle des actifs, au
    #: prorata de la carrière déjà faite.
    retraites: float
    actifs: float
    #: La part que le modèle somme APRÈS la dernière année que l'INSEE projette,
    #: où les effectifs ne sont plus lus mais déduits de la table de mortalité.
    #: Elle dit ce que l'extrapolation porte, et donc ce qu'elle risque.
    hors_projection: float
    #: Le même engagement du système actuel sous un taux d'actualisation
    #: SUPÉRIEUR à la croissance du PIB, écart par écart.
    _sensibilite: tuple[tuple[float, float], ...] = ()

    def part_pib(self, scenario: str = "actuel") -> float:
        """L'engagement acquis, en part du PIB de l'année de référence."""
        return self._par_scenario.get(scenario, 0.0)

    def sensibilite(self) -> tuple[tuple[float, float], ...]:
        return self._sensibilite

    def ecart_pour(self, cible: float) -> float | None:
        """L'écart de taux qui ramènerait l'engagement à ``cible``.

        Interpolé linéairement sur la grille chiffrée, et ``None`` si la cible
        est hors de sa portée : c'est ce qui permet à la page de dire de
        combien le taux du tableau 29 diffère de celui du COR sans que
        personne ait à le publier — aucun des deux producteurs ne le fait.
        """
        points = self._sensibilite
        for (ecart_bas, valeur_bas), (ecart_haut, valeur_haut) in zip(points, points[1:]):
            if valeur_haut <= cible <= valeur_bas:
                largeur = valeur_bas - valeur_haut
                if largeur <= 0.0:
                    return ecart_bas
                return ecart_bas + (ecart_haut - ecart_bas) * (valeur_bas - cible) / largeur
        return None


def _courbes_survie(mortalite, cohortes: set[int], depart: int,
                    horizon: int) -> dict[int, tuple[float, ...]]:
    """Survie de chaque cohorte à partir de ``depart``, table unisexe.

    L'INSEE ne projette sa pyramide que jusqu'en 2070, et ``Population`` REFUSE
    au-delà depuis le 20 septembre 2026 : elle recopiait l'année de bord, si
    bien que l'effectif des 85 ans de 2085 était celui des 85 ans de 2070, nés
    quinze ans plus tôt. C'est ici qu'est l'extrapolation juste, et elle est la
    seule : pour une cohorte DÉJÀ NÉE, on prolonge par sa propre survie. La
    table est l'unisexe du dépôt, celle qui sert déjà de diviseur aux comptes
    notionnels, prise en génération.
    """
    courbes: dict[int, tuple[float, ...]] = {}
    for cohorte in cohortes:
        age = depart - cohorte
        courbes[cohorte] = (
            mortalite.courbe(float(age), float(depart), None)
            if 0 <= age else ()
        )
    return courbes


def calculer_engagements(simulateur: Simulateur, depenses: DepensesRetraite,
                         population: Population, annee: int,
                         scenarios: Sequence[str],
                         cas_types: tuple[CasType, ...] = CAS_TYPES,
                         ponderation: str = "effectifs",
                         liquidation: str = "droit") -> EngagementAcquis:
    """L'engagement acquis à ``annee``, système par système, en part de PIB.

    LA CONVENTION D'ACQUISITION EST LE PRORATA TEMPORIS, et il faut la nommer :
    un actif qui a fait les trois quarts de sa carrière a acquis les trois
    quarts de sa pension. C'est la convention que le tableau 29 retient pour
    les régimes à prestations définies, et surtout c'est UNE convention
    appliquée aux six systèmes, ce qui est la condition pour que leurs
    engagements se comparent. Un compte notionnel donnerait la sienne sans
    approximation — le capital virtuel EST le droit acquis —, mais elle ne
    vaudrait que pour cinq des six systèmes, et l'étalon serait hors du
    tableau.

    CE QUE LA SOMME COURT. De ``annee`` à ``HORIZON_ENGAGEMENTS``, pour chaque
    couple (cas type, cohorte) de la grille : la pension qu'il touchera,
    pondérée par l'effectif survivant de sa cohorte et par le poids de sa
    caisse, multipliée par la fraction de carrière déjà faite, et rapportée au
    PIB de l'année. Les effectifs viennent de l'INSEE tant qu'il les projette,
    de la table de mortalité ensuite — ``hors_projection`` dit ce que cette
    seconde moitié pèse, et c'est peu.
    """
    pensionnes, _ = _pensionnes(simulateur, cas_types, liquidation)
    poids = _ponderation(simulateur, ponderation, cas_types)
    macro = simulateur.macro
    annee_euros = simulateur.parametres.annee_euros_constants
    horizon = HORIZON_ENGAGEMENTS
    revalorisation = RevalorisationServie(
        simulateur,
        min((p.annee_liquidation for p in pensionnes), default=horizon) - _DEMI_TRANCHE,
        horizon,
    )

    derniere_publiee = depenses.derniere_annee
    masses_ancrage, _, _ = _masses(pensionnes, population, derniere_publiee,
                                   poids(derniere_publiee), revalorisation)
    if masses_ancrage["actuel"] <= 0.0:
        return EngagementAcquis(annee, horizon, {}, 0.0, 0.0, 0.0)
    # Le prix d'une unité de masse du modèle, en euros constants de référence :
    # le même ancrage que la trajectoire, et pour la même raison.
    ancrage = (
        depenses.repartition(derniere_publiee)
        * macro.coefficient_prix(derniere_publiee, annee_euros)
        / masses_ancrage["actuel"]
    )

    derniere_pib = depenses.pib.derniere_annee
    pib: dict[int, float] = {}
    courant = depenses.pib(derniere_pib)
    for millesime in range(annee, horizon + 1):
        if millesime <= derniere_pib:
            pib[millesime] = depenses.pib(millesime)
        else:
            courant *= 1.0 + macro.pib_nominal(millesime)
            pib[millesime] = courant
    # ``pib`` a été rempli dans l'ordre des années : la récurrence ci-dessus
    # suppose que la dernière année publiée précède la première projetée, ce
    # qui est vrai tant que ``annee`` est une année observée.
    poids_par_annee = {a: poids(a) for a in range(annee, horizon + 1)}

    ages_debut = {cas.code: int(cas.age_debut) for cas in cas_types}
    cohortes = {
        pensionne.generation + decalage
        for pensionne in pensionnes
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1)
    }
    # La frontière est celle de la PYRAMIDE, et non celle du PIB : c'est
    # l'INSEE qui cesse de projeter les effectifs en 2070, quand la série de
    # PIB s'arrête cinq ans plus tôt et se prolonge, elle, par un taux.
    depart_survie = population.derniere_annee
    survies = _courbes_survie(simulateur.mortalite, cohortes, depart_survie, horizon)
    # Les facteurs d'actualisation, une fois par année plutôt qu'une fois par
    # couple : la boucle intérieure en compte des centaines de milliers.
    facteurs = {
        millesime: tuple((1.0 + ecart) ** (annee - millesime)
                         for ecart in ECARTS_ACTUALISATION)
        for millesime in range(annee, horizon + 1)
    }

    cles = list(dict.fromkeys(scenarios))
    totaux = {cle: 0.0 for cle in cles}
    parts = {"retraites": 0.0, "actifs": 0.0, "hors_projection": 0.0}
    sensibilite = {ecart: 0.0 for ecart in ECARTS_ACTUALISATION}

    for pensionne in pensionnes:
        for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
            cohorte = pensionne.generation + decalage
            fin_carriere = pensionne.annee_liquidation + decalage
            debut_carriere = cohorte + ages_debut[pensionne.code]
            if fin_carriere <= debut_carriere:
                continue
            acquis = (annee - debut_carriere) / (fin_carriere - debut_carriere)
            acquis = min(1.0, max(0.0, acquis))
            if acquis <= 0.0:
                continue
            courbe = survies.get(cohorte, ())
            effectif_bord = population.effectif(depart_survie - cohorte, depart_survie)
            for millesime in range(max(annee, fin_carriere), horizon + 1):
                part_caisse = poids_par_annee[millesime].get(pensionne.code, 0.0)
                if part_caisse <= 0.0:
                    continue
                if millesime <= depart_survie:
                    effectif = population.effectif(millesime - cohorte, millesime)
                else:
                    rang = millesime - depart_survie
                    effectif = effectif_bord * (courbe[rang] if rang < len(courbe) else 0.0)
                if effectif <= 0.0:
                    continue
                commun = (
                    acquis * part_caisse * effectif
                    * revalorisation.coefficient_stock(fin_carriere, millesime,
                                                       prospectif=False)
                    * ancrage / macro.coefficient_prix(millesime, annee_euros)
                    / pib[millesime]
                )
                for cle in cles:
                    totaux[cle] += commun * pensionne.pensions[cle]
                valeur = commun * pensionne.pensions["actuel"]
                parts["retraites" if acquis >= 1.0 else "actifs"] += valeur
                if millesime > depart_survie:
                    parts["hors_projection"] += valeur
                for ecart, facteur in zip(ECARTS_ACTUALISATION, facteurs[millesime]):
                    sensibilite[ecart] += valeur * facteur

    return EngagementAcquis(
        annee=annee,
        horizon=horizon,
        _par_scenario=totaux,
        retraites=parts["retraites"],
        actifs=parts["actifs"],
        hors_projection=parts["hors_projection"],
        _sensibilite=tuple((ecart, sensibilite[ecart]) for ecart in ECARTS_ACTUALISATION),
    )


def calculer_cout(simulateur: Simulateur, depenses: DepensesRetraite,
                  population: Population,
                  comptes: ComptesRetraite | None = None,
                  cas_types: tuple[CasType, ...] = CAS_TYPES,
                  ponderation: str = "effectifs",
                  liquidation: str = "droit",
                  assiette: AssietteActivite | None = None,
                  convention_recette: str = CONVENTION_ASSIETTE,
                  convention_reversion: str = CONVENTION_REVERSION_SUPPRIMEE) -> Cout:
    """Le coût observé, les cinq contrefactuels, et la trajectoire jusqu'en 2070.

    Les années où le modèle ne sert AUCUNE pension — celles d'avant la première
    liquidation possible — sont écartées : un rapport y serait une division par
    zéro, et non un résultat.

    ``ponderation`` choisit ce que chaque cas type pèse : ``effectifs``, les
    retraités de sa caisse publiés par la DREES dans les masses de pensions et
    ses cotisants publiés par le COR dans les masses de cotisations, ou
    ``egale``, l'ancienne convention. Le second n'existe que pour mesurer ce
    que le premier a déplacé.

    ``liquidation`` choisit l'âge auquel chaque cas type part : ``droit``,
    celui que le droit de sa génération lui ouvre, ou ``absolu``, l'âge écrit
    dans la grille — le même pour toutes les générations. Le second n'existe,
    lui aussi, que pour mesurer ce que le premier a déplacé : c'est par lui
    qu'on lit, sans argumenter, ce que valait un modèle qui faisait liquider
    la génération 1940 à l'âge légal de 2023.

    ``convention_reversion`` dit ce que les scénarios notionnels font de la
    RÉVERSION, qu'aucun d'eux ne calcule : ``supprimee``, comme en Suède, et
    c'est le défaut parce que la réversion est un avantage non contributif de
    plus ; ou ``servie``, reconduite telle quelle comme en Italie. Le scénario
    1 la sert dans les deux cas. Ce n'est pas un réglage d'affichage : la
    réversion pèse un dixième de la masse versée.

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
    poids_cotisants = _ponderation(simulateur, ponderation, cas_types, COTE_COTISANTS)
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

    # La garantie vieillesse ne se lit pas sur la grille mais sur la
    # distribution des pensions ; la grille dit seulement de combien cette
    # distribution bouge. Calée une fois, l'année de l'enquête.
    garantie = _garantie_distribution(simulateur, pensionnes, population, poids,
                                      revalorisation)

    lignes: list[CoutAnnuel] = []
    for annee in depenses.annees():
        masses, vivants, tetes = _masses(pensionnes, population, annee, poids(annee),
                                         revalorisation)
        if masses["actuel"] <= 0.0:
            continue
        observee = depenses.depense(annee)
        coefficient = macro.coefficient_prix(annee, annee_euros)
        part_derives = depenses.part_droits_derives(annee)
        projetee = garantie.chiffrer(masses, tetes)
        lignes.append(CoutAnnuel(
            annee=annee,
            observee=observee,
            coefficient_constants=coefficient,
            part_pib=depenses.part_pib(annee),
            rapports=_rapports(masses, projetee, observee * coefficient, part_derives),
            garantie=projetee,
            pensionnes=vivants,
            part_derives=part_derives,
            reversion_servie=reversion_servie,
            reforme_en_vigueur=annee >= simulateur.parametres.annee_bascule,
        ))

    fiabilite = min(
        (depenses.fiabilite(ligne.annee) for ligne in lignes),
        default=Fiabilite.ESTIMEE,
    )
    avenir = _avenir(pensionnes, depenses, population, simulateur, poids,
                     revalorisation, reversion_servie, poids_cotisants, garantie)
    solde = _solde(
        avenir, comptes, depenses.pib.derniere_annee, assiette,
        simulateur.parametres.taux_cotisation_liberal,
        simulateur.parametres.annee_bascule, convention_recette,
        depenses, reversion_servie,
    ) if comptes is not None and avenir.annees else Solde()
    return Cout(
        annees=lignes,
        avenir=avenir,
        solde=solde,
        dette=calculer_dette(
            solde, avenir, simulateur.courbe_taux,
            dette_publique=comptes.dette_publique if comptes is not None else None,
        ),
        annee_euros=annee_euros,
        generations=generations(),
        echecs=echecs,
        ponderation=ponderation,
        liquidation=liquidation,
        convention_recette=convention_recette,
        poids=poids(depenses.derniere_annee),
        poids_cotisants=poids_cotisants(depenses.derniere_annee),
        # Le contrefactuel ne peut jamais valoir mieux qu'« estimé » : la
        # dépense observée est certifiée, le rapport qui la corrige ne l'est
        # pas et ne peut pas l'être — aucune institution ne publie ce qu'un
        # système qui n'a pas existé aurait coûté.
        fiabilite=min(fiabilite, Fiabilite.ESTIMEE),
    )
