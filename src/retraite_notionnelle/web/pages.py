"""Contenu des pages : formulaire, résultats, cas types, méthode, données.

Ce module ne dépend que de la bibliothèque standard et du moteur. Il sert de
référence au portage JavaScript qui fait tourner le site
(``moteur/js/pages.js``) : les deux rendus sont comparés caractère par caractère
par ``tests/js/moteur.test.js``.
"""

from __future__ import annotations

import json
import math
import re
from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from html import escape
from urllib.parse import urlencode

from ..calendrier import (
    MOIS_PAR_AN, NOMS_DE_MOIS, DateMois, en_mois, formater_age, mois_travailles,
)
from ..carriere import (
    FAMILLES_STATUT,
    Affiliations,
    LigneRelevee,
    Metier,
    bornes_deformation,
    formater_borne,
    salaire_moyen_annuel,
)
from ..castypes import CAS_TYPES, GENERATIONS, calculer_cas_types
from ..config import (
    AgeConversionDroitsAcquis,
    PartCotisation,
    ModeAgeReference,
    ModeIndexation,
    Parametres,
    SituationFoyer,
    TableConversion,
)
from ..avantages import (
    LIBELLES_MOTIFS, LIGNES_LUES, MOTIFS, NEUTRALISATIONS, calculer_avantages,
    charger_avantages,
    inventaire_depuis_paquet,
)
from ..cout import COMPOSANTE_GARANTIE, calculer_cout, masse_du_scenario
from ..donnees.assiette import AssietteActivite
from ..donnees.distribution import DistributionPensions
from ..garantie import cout_garantie
from ..donnees.chargement import (
    DonneeInsuffisante,
    charger_periodes_non_travaillees,
    journal_certification,
)
from ..donnees.depenses import SYSTEMES, DepensesRetraite
from ..donnees.equilibre import (
    GROUPES,
    ORGANISMES,
    POSTES,
    POSTES_TRANSFERTS,
    ComptesRetraite,
)
from ..donnees.regimes import charger_inventaire
from ..donnees.population import Population
from ..scenarios.actuel import MinimumVieillesse
from ..remuneration import (
    charger_prelevements,
    salaire_brut_depuis_net,
    salaire_net_depuis_brut,
)
from ..simulateur import Comparaison, Simulateur
from . import gabarit as g

PROFILS = [
    ("plat", "Plat — le salaire suit le salaire moyen"),
    ("ascendant", "Ascendant — profil employé/ouvrier"),
    ("fortement_ascendant", "Fortement ascendant — profil cadre"),
]

#: La règle par défaut vient EN TÊTE : c'est celle que la simulation applique, et
#: donc la première ligne du tableau « D'où vient l'écart ».
INDEXATIONS = [
    ("masse_salariale", "Masse salariale — règle d'équilibre (défaut)"),
    ("revalorisation_portee_au_compte",
     "Revalorisation réellement pratiquée (arrêtés Cnav)"),
    ("triple_lock_inverse", "Triple lock inversé (règle demandée)"),
    ("triple_lock_inverse_nominal", "Triple lock inversé, tout en nominal"),
    ("mediane_trois_taux", "Médiane des trois taux"),
    ("moyenne_trois_taux", "Moyenne des trois taux"),
    ("pib_nominal", "PIB nominal (assiette la plus large)"),
    ("prix", "Prix"),
    ("salaires", "Salaire moyen"),
]

#: Fenêtre de lissage maximale acceptée par le formulaire, en années. Le
#: lissage s'applique au taux que la règle produit, quelle que soit la règle :
#: ce qu'il vise est la loterie de cohorte. La fenêtre se saisit librement — 1
#: pour aucun lissage, 5 pour la règle italienne, ce qu'on veut entre les deux
#: et au-delà. La borne n'est pas une limite du moteur mais un garde-fou de
#: sens : au-delà d'une trentaine d'années, la moyenne couvre presque toute une
#: carrière, tous les millésimes reçoivent à peu près le même taux, et ce n'est
#: plus un lissage mais un taux fixe reconstitué.
LISSAGE_MAXIMUM = 30

AGES_REFERENCE = [
    ("fixe_apres_bascule", "64 ans à partir de la bascule (défaut)"),
    ("cliquet_legal", "Cliquet légal"),
    ("cliquet_puis_esperance_vie", "Cliquet puis espérance de vie"),
    ("legal_sans_cliquet", "Âge légal, sans cliquet"),
]

TABLES = [("unisexe", "Unisexe (défaut)"), ("par_sexe", "Par sexe")]

PARTS_COTISATION = [
    ("salariale", "Part salariale seule (défaut)"),
    ("totale", "Salariale et patronale"),
    ("totale_alignee", "Salariale et patronale, public aligné sur le privé"),
]

CONVERSIONS_ACQUIS = [
    ("reference", "À l'âge de référence (défaut)"),
    ("liquidation", "À l'âge de départ effectif"),
]

#: Situation de foyer de la garantie vieillesse du système 4. Elle ne joue que
#: sur l'allocation d'isolement : la garantie est individualisée, et la pension
#: du conjoint n'entre jamais dans le calcul.
SITUATIONS_FOYER = [
    ("seul", "Personne seule (défaut)"),
    ("couple", "En couple"),
]

PROJECTIONS = [
    ("cor_reference", "COR référence — productivité 0,7 %"),
    ("cor_productivite_basse", "COR variante basse — 0,4 %"),
    ("cor_productivite_haute", "COR variante haute — 1,0 %"),
]


#: Les deux façons d'écrire un revenu. Le modèle n'en connaît qu'une — le
#: multiple du salaire moyen, seule qui garde son sens sur quatre-vingts ans —,
#: mais personne ne connaît son salaire dans cette unité-là : c'est l'euro qui
#: est proposé d'abord, et le multiple reste à un clic pour qui raisonne en
#: relatif. La liste ne s'affiche pas — on passe d'une unité à l'autre par un
#: lien, qui convertit au passage — mais elle borne ce qu'une adresse peut dire.
UNITES_REVENU = [
    ("euros_mois", "€ bruts par mois"),
    ("moyen", "× le salaire moyen"),
]

#: Ce que porte le champ tant que rien n'a été saisi, dans chaque unité. Un
#: nombre rond proche du salaire moyen plutôt que le salaire moyen exact : le
#: champ est fait pour être remplacé, et « 3 500 » se relit mieux que « 3 475 ».
SALAIRE_DEFAUT = {"euros_mois": 3500.0, "moyen": 1.0}

#: Les deux façons de lire tout montant du simulateur — ce qu'on saisit comme
#: ce qu'on affiche. Un seul réglage pour les deux : lire un salaire net et une
#: pension brute sur la même page compare deux grandeurs différentes, et c'est
#: exactement ce que le site faisait avant cette bascule.
#:
#: Le défaut est le NET, parce que c'est ce qu'on touche et ce qu'on connaît de
#: soi. Le brut reste à un clic, et il reste la langue du reste du site : les
#: capitaux, les assiettes et les tableaux de détail sont bruts par nature et
#: ne bougent pas — on ne « nette » pas un capital notionnel.
MODES_MONTANT = [
    ("net", "net — ce qui arrive sur le compte"),
    ("brut", "brut — avant CSG et cotisations"),
]

#: Précision du multiple du salaire moyen, en décimales et en pas. Les deux
#: doivent rester d'accord : le lien de bascule écrit un multiple arrondi à
#: ``DECIMALES_MULTIPLE``, et un navigateur refuse de soumettre un nombre qui
#: ne tombe pas sur le ``step`` déclaré par le champ. Le millième n'est pas
#: gratuit : il vaut trois euros cinquante par mois, ce qui borne la fidélité
#: d'un aller-retour entre les deux unités — au centième, l'écart atteignait
#: vingt euros.
DECIMALES_MULTIPLE = 3
PAS_MULTIPLE = 10 ** -DECIMALES_MULTIPLE

#: Décimales des coefficients qui font une CHAÎNE DE CALCUL affichée : le
#: diviseur de conversion, le coefficient de revalorisation, le rendement
#: cumulé. Elles ne sont pas décoratives — elles sont mesurées, et mesurées SUR
#: LES VALEURS AFFICHÉES : calibrées sur les valeurs exactes du modèle, elles
#: paraissaient suffire une décimale plus tôt, parce que la mesure ignorait
#: l'arrondi des lignes que le lecteur, lui, a sous les yeux.
#:
#: Écart maximal de la ligne reconstituée, sur cinquante-deux carrières :
#:
#:                         4 déc.    5 déc.    6 déc.
#:   a) × diviseur         2,70 €    0,57 €    0,57 €
#:   capital ÷ diviseur    0,10 €    0,02 €    0,02 €
#:   b) × revalorisation  62,27 €    6,47 €    1,23 €
#:   cotisations × rendt  50,92 €    5,09 €    1,07 €
#:
#: Au-delà, le gain s'arrête : ce qui reste vient de ce que les capitaux
#: s'affichent à l'euro, ce qui borne toute reconstitution à un demi-euro par
#: terme, et cette borne-là ne se rachète pas par des décimales.
DECIMALES_DIVISEUR = 5
DECIMALES_FACTEUR = 6

#: Durée mensuelle de référence du SMIC : 35 heures par semaine ramenées au
#: mois, soit 151,67 heures. Elle ne sert qu'à écrire un repère à l'échelle
#: d'un salaire mensuel.
HEURES_SMIC_PAR_MOIS = 151.67


#: Nombre maximal de métiers d'une carrière, le premier compris. Le formulaire
#: affiche toujours une ligne vide de plus que les métiers saisis : c'est ainsi
#: qu'on en ajoute un, sans une ligne de JavaScript. La borne n'est pas une
#: limite du moteur — il en accepterait autant qu'on veut — mais celle du
#: formulaire : au-delà, ce n'est plus une suite de métiers qu'on décrit, c'est
#: un relevé de carrière année par année — et celui-là a son propre champ,
#: borné par ``RELEVE_MAXIMUM``.
METIERS_MAXIMUM = 6

#: Nombre de lignes qu'un relevé de carrière peut porter. Une carrière tient
#: entre quatorze ans — l'âge de début minimal — et soixante-quinze, soit
#: soixante et une années civiles au plus ; la borne laisse deux lignes de
#: marge et ferme surtout la porte que les interruptions avaient ouverte : le
#: calcul se fait chez le lecteur et l'adresse EST la saisie, si bien qu'un
#: relevé de cent mille lignes forgé dans un lien figeait l'onglet de celui qui
#: le suivait.
RELEVE_MAXIMUM = 63

#: Bornes des deux années que l'utilisateur peut choisir : celle de la bascule
#: au régime unique, et celle des euros constants dans lesquels les montants
#: sont exprimés. Elles étaient déclarées sur les champs du formulaire, donc
#: opposables au navigateur seulement : une adresse forgée à la main les
#: franchissait sans rien déclencher, et « ?euros=9999 » faisait afficher au
#: simulateur des pensions à soixante chiffres. La borne se dit ici, une fois,
#: et le formulaire la lit — les deux ne peuvent plus diverger.
ANNEE_MINIMALE = 1941
ANNEE_MAXIMALE = 2070

#: Un enfant de plus change la pension du système 1 par ses majorations. Le
#: champ était borné à douze dans le formulaire et nulle part ailleurs.
ENFANTS_MAXIMUM = 12

#: Bornes de l'année de naissance et des deux âges saisis. Elles étaient
#: écrites deux fois — une fois dans ``verifier``, une fois sur le champ du
#: formulaire —, comme l'étaient les années de bascule avant ``ANNEE_MINIMALE``.
#: Elles se disent ici, une fois, et le formulaire les lit.
NAISSANCE_MINIMALE = 1900
NAISSANCE_MAXIMALE = 2020
AGE_DEBUT_MINIMAL = 14
#: L'année où le routage commence : la première période de tout statut. Un
#: statut dont le régime naît plus tard le dit dans le menu — « (depuis
#: 1977) » —, celui de 1930 n'a rien à dater.
ANNEE_MODELE = 1930
AGE_DEBUT_MAXIMAL = 40
AGE_LIQUIDATION_MINIMAL = 40
AGE_LIQUIDATION_MAXIMAL = 75

#: Toute année qu'une carrière peut couvrir, quel qu'en soit l'auteur : né au
#: plus tôt et entré au plus jeune d'un côté, né au plus tard et parti au plus
#: vieux de l'autre. Sert à borner les interruptions, dont les années étaient
#: reprises telles quelles : « 0:999999999:chomage_indemnise » faisait boucler
#: un milliard de fois et figeait l'onglet. Une plage hors de cette fenêtre ne
#: décrit aucune carrière, et se refuse au lieu de se calculer.
ANNEE_CARRIERE_MINIMALE = NAISSANCE_MINIMALE + AGE_DEBUT_MINIMAL
ANNEE_CARRIERE_MAXIMALE = NAISSANCE_MAXIMALE + AGE_LIQUIDATION_MAXIMAL

#: Âge auquel s'arrête la trajectoire individuelle. Les tables de mortalité du
#: modèle vont jusqu'à 120 ans : ce n'est pas la table qui s'arrête tôt, c'est
#: la MOYENNE par laquelle le capital notionnel est divisé. Un graphique qui
#: s'arrêterait à cette moyenne cacherait justement ce qu'il doit montrer — que
#: la moitié d'une génération lui survit. À 105 ans, le modèle donne encore une
#: personne sur dix vivante parmi celles parties à 64 ans : la borne n'est pas
#: une fantaisie, elle est le bout de la distribution, pas son milieu.
AGE_MAXIMUM_TRAJECTOIRE = 105

#: LES QUATRE SYSTÈMES QUE LE SITE COMPARE, dans l'ordre où il les montre.
#:
#: Le modèle en calcule six, et continue de le faire : ses deux variantes
#: « dès la bascule » — droits acquis convertis en capital, règles notionnelles
#: ensuite — restent dans ``Comparaison``, dans ``cout.SCENARIOS`` et dans les
#: tests du moteur. Ce sont les seules qui lisent l'âge de référence, et c'est
#: ce qui les rendait utiles : elles mesuraient le coût d'une bascule sans
#: rétroactivité.
#:
#: Elles ne sont plus MONTRÉES. Le site ne pose plus la question à laquelle
#: elles répondaient : la proposition du parti est rétroactive, et offrir six
#: comparaisons quand quatre suffisent faisait payer au lecteur le prix d'une
#: hésitation qui n'est plus la nôtre. Retirer leur affichage retire avec elles
#: toute la mécanique de conversion des droits acquis — la fiche de l'âge de
#: référence, son avertissement, le dépliant « ligne à ligne » et deux options
#: du formulaire —, ce qui a été décidé en connaissance de cause.
#:
#: Un seul endroit décide, et tout le site le lit : les barres de Simuler, les
#: courbes de la Trajectoire, les grilles de Cas types, le comparatif de Coût.
SCENARIOS_MONTRES: tuple[str, ...] = (
    "actuel",
    "notionnel_retroactif",
    "notionnel_retroactif_employeur",
    "notionnel_liberal",
)

#: Le libellé de chaque système partout où le site le NOMME — tableaux de la
#: page Coût, légendes des graphiques, en-têtes de ligne. Court, parce qu'il
#: tient dans une cellule ; numéroté de 1 à 4, comme les barres de Simuler.
#:
#: La nomenclature du MODÈLE, elle, ne bouge pas : ``cout.SCENARIOS`` numérote
#: toujours ses six scénarios de 1 à 6, et c'est elle que lisent les tests du
#: moteur et les fichiers de données. Les deux ne se rencontrent jamais —
#: aucune page n'affiche plus un libellé venu du modèle.
LIBELLES_SYSTEMES = {
    "actuel": "1. Système de répartition actuel",
    "notionnel_retroactif": "2. Compte notionnel, part salariale",
    "notionnel_retroactif_employeur": "3. Compte notionnel, les deux parts",
    "notionnel_liberal": "4. La proposition libérale",
}

#: Les mêmes, appariés et dans l'ordre : ce que les boucles de la page Coût
#: parcourent à la place de ``cout.SCENARIOS``.
SCENARIOS_COMPARES = tuple(
    (scenario, LIBELLES_SYSTEMES[scenario]) for scenario in SCENARIOS_MONTRES
)


#: Les quatre courbes : attribut du modèle, variable CSS de couleur — la même
#: que la barre du haut, pour qu'une couleur désigne partout le même système —
#: et le chiffre posé au bout de la courbe. Ce chiffre n'est pas décoratif :
#: quatre courbes qui se croisent ne peuvent pas être identifiées par la
#: couleur seule, une deutéranopie confondant vite deux des quatre teintes.
TRAJECTOIRE = (
    ("actuel", "--actuel", "1"),
    ("notionnel_retroactif", "--retroactif", "2"),
    ("notionnel_retroactif_employeur", "--retroactif-employeur", "3"),
    ("notionnel_liberal", "--liberal", "4"),
)

#: Rang de chaque période, tel que le formulaire l'annonce.
RANGS_METIER = ("premier", "deuxième", "troisième", "quatrième", "cinquième",
                "sixième", "septième", "huitième")


#: Ce qu'une ligne de carrière peut décrire à la place d'un métier.
#:
#: Une carrière n'est pas faite que d'emplois, et le formulaire ne demandait
#: que ceux-là : entre le dernier métier et le départ, il supposait qu'on
#: travaillait. Qui s'arrête à 58 ans pour liquider à 64 voyait donc six années
#: cotisées qu'il n'avait pas vécues. Une ligne dont le statut est l'un de ces
#: motifs dit l'inverse : à partir de cette date, et jusqu'à la ligne suivante
#: ou jusqu'au départ, l'activité s'arrête. La DERNIÈRE ligne dit donc la date
#: de fin d'activité, quand elle est antérieure au départ.
#:
#: Les codes sont ceux de ``legislation/periodes_non_travaillees.csv``, qui dit
#: ce que chacun ouvre — trimestres assimilés, points complémentaires financés
#: par l'UNEDIC ou la Sécurité sociale, AVPF. Un test vérifie qu'aucun code
#: d'ici n'est absent de là-bas : le menu ne peut pas proposer un motif que le
#: moteur traiterait en « sans activité » sans le dire.
#: Les libellés sont des groupes nominaux : le menu les range sous le groupe
#: « Sans emploi », le résumé de carrière les emploie tels quels — « chômage
#: indemnisé de 58 ans à 62 ans ».
SANS_EMPLOI = [
    ("chomage_indemnise", "chômage indemnisé"),
    ("chomage_non_indemnise", "chômage non indemnisé"),
    ("maladie", "arrêt maladie"),
    ("accident_travail", "accident du travail"),
    ("maternite", "congé de maternité"),
    ("invalidite", "invalidité"),
    ("education_enfant", "élever un enfant"),
    ("service_militaire", "service militaire"),
    ("sans_activite", "sans activité, ni chômage"),
]

#: Les seuls codes de ``SANS_EMPLOI``, pour reconnaître une ligne sans emploi.
#:
#: Ces codes ne valent que pour une ligne qui SUIT la première : une carrière
#: commence quand on commence à travailler, et la première ligne ne porte donc
#: qu'une affiliation. « sans_activite » fait exception d'un côté — c'est aussi
#: une affiliation, « Sans activité professionnelle », qui ne route vers aucun
#: régime, et une adresse qui la porte en premier métier décrit quelqu'un qui
#: n'a jamais travaillé. Les deux chemins donnent le même résultat au bit près :
#: une ligne suivante la lit comme un motif, la première comme l'affiliation
#: qu'elle a toujours été.
CODES_SANS_EMPLOI = frozenset(code for code, _ in SANS_EMPLOI)

#: Le libellé d'un motif, pour le résumé de carrière.
LIBELLES_SANS_EMPLOI = dict(SANS_EMPLOI)


class ErreurSaisie(ValueError):
    """Saisie inexploitable, à afficher telle quelle à l'utilisateur."""


def _refus(rang: int, phrase: str) -> ErreurSaisie:
    """Un refus, daté du métier qu'il concerne quand il y en a plusieurs.

    La phrase est écrite une fois, avec sa majuscule ; le rang la fait passer
    au milieu d'une autre, où la majuscule n'a plus lieu d'être. Écrire les
    deux versions à la main les laisserait diverger.
    """
    if rang == 1:
        return ErreurSaisie(phrase)
    return ErreurSaisie(f"Métier n° {rang} : " + phrase[0].lower() + phrase[1:])


@dataclass
class MetierSaisi:
    """Une ligne de carrière : une date, un statut, un niveau de revenu.

    C'est un métier quand le statut est une affiliation, et une période SANS
    EMPLOI quand c'est l'un des motifs de :data:`SANS_EMPLOI` — chômage,
    maladie, élever un enfant, rien du tout. Les deux se décrivent de la même
    façon, parce que ce sont les mêmes renseignements : à partir de quand, et
    quoi.
    """

    #: Âge auquel cette période commence.
    debut: float
    #: Statut d'affiliation, ou motif de :data:`SANS_EMPLOI`.
    statut: str
    #: Revenu, dans l'unité que ``Saisie.unite_revenu`` désigne : euros bruts
    #: par mois, ou multiple du salaire moyen brut. Une période sans emploi
    #: n'en porte pas : elle hérite de celui d'avant, qui est le salaire de
    #: référence sur lequel l'UNEDIC cotise aux complémentaires.
    salaire: float
    #: Vrai si ``statut`` est un motif de :data:`SANS_EMPLOI` et non une
    #: affiliation. Décidé à la LECTURE, et non déduit ici du statut : la
    #: première ligne de la carrière n'est jamais une période sans emploi, et
    #: « sans_activite » y garde le sens d'affiliation qu'il a toujours eu.
    sans_emploi: bool = False


#: Les clés de requête qui décrivent les RÈGLES, et non la carrière.
#:
#: Ce sont exactement les dix que ``Saisie.parametres`` lit pour fabriquer un
#: jeu de :class:`Parametres` : tout le reste — naissance, statut, revenu,
#: enfants, profil, interruptions — décrit un individu, et un individu n'a pas
#: sa place dans un agrégat. C'est cette liste qui permet aux trois pages
#: agrégées de lire une adresse de simulateur sans rien en retenir d'autre que
#: les règles, et aux liens internes de ne porter que ce qui a un sens partout.
#:
#: Le sexe n'en est pas : il ne joue que sur la table de conversion « par sexe »
#: et sur les majorations pour enfants, deux réglages individuels. Les cas types
#: portent le leur.
CLES_MODELISATION = (
    "indexation", "lissage", "age_reference", "table", "conversion_acquis",
    "part_cotisation", "foyer", "projection", "bascule", "euros",
)


@dataclass
class Saisie:
    """Paramètres d'une simulation, tels que l'utilisateur les a saisis."""

    naissance: int = 1975
    naissance_mois: int = 1
    #: Jour de naissance. Il n'entre dans aucun calcul — le modèle compte en
    #: mois, et le droit coupe ses générations au mois. Il est gardé parce que
    #: le calendrier en demande un : sans lui, le formulaire répondrait « 1er
    #: mars » à qui est né le 15, et ferait douter de ce qu'il a compris.
    naissance_jour: int = 1
    sexe: str = "H"
    statut: str = "salarie_prive_non_cadre"
    debut: float = 21
    liquidation: float = 64
    #: Revenu du premier métier, dans l'unité choisie ci-dessous.
    salaire: float = SALAIRE_DEFAUT["euros_mois"]
    #: Unité dans laquelle les revenus sont saisis, pour TOUS les métiers : un
    #: seul choix pour la carrière entière, parce qu'on décrit une même vie de
    #: travail et qu'un changement d'unité en cours de route n'est pas une
    #: information sur la carrière. Les euros sont ceux d'aujourd'hui : on
    #: saisit ce que le métier paie maintenant, et le modèle suit ensuite le
    #: salaire moyen d'une année à l'autre.
    unite_revenu: str = "euros_mois"
    #: Net ou brut : vaut pour TOUT le simulateur, la saisie comprise. En
    #: « net », le salaire tapé est un net mensuel que le modèle convertit en
    #: brut par la fiche de paie du statut, et tous les montants affichés —
    #: salaire, pension, rente — sont nets de ce qui les frappe. Voir
    #: ``MODES_MONTANT``.
    montants: str = "net"
    #: Les métiers exercés APRÈS le premier. Le premier, lui, est décrit par
    #: ``statut``, ``debut`` et ``salaire`` : une adresse d'avant les carrières
    #: multiples reste donc valide, et décrit la carrière d'un seul métier.
    metiers: list[MetierSaisi] = field(default_factory=list)
    #: Le relevé de carrière, une ligne par année : « année:régime:revenu » et,
    #: si le relevé les porte, « :trimestres ». Non vide, il REMPLACE la
    #: carrière paramétrique — les métiers, le profil et le niveau de revenu ne
    #: servent plus à rien : plus rien n'est reconstitué, tout est lu.
    releve: str = ""
    profil: str = "ascendant"
    primes: float = 0.0
    enfants: int = 0
    interruptions: str = ""
    indexation: str = "masse_salariale"
    lissage: int = 1
    age_reference: str = "fixe_apres_bascule"
    table: str = "unisexe"
    conversion_acquis: str = "reference"
    part_cotisation: str = "salariale"
    #: Seul ou en couple : la situation de foyer de la garantie vieillesse du
    #: système 4. Le défaut est la personne seule, comme pour l'ASPA du
    #: système 1, de sorte que les deux planchers se comparent.
    foyer: str = "seul"
    projection: str = "cor_reference"
    bascule: int = 2026
    euros: int = 2026
    #: Vrai si la requête portait des paramètres, donc s'il faut calculer.
    demandee: bool = False

    @classmethod
    def depuis_requete(cls, parametres: dict[str, str]) -> "Saisie":
        defauts = cls()
        # Le premier métier se lit d'abord : les suivants héritent de son niveau
        # de revenu quand ils n'en portent pas.
        statut = parametres.get("statut") or defauts.statut
        # Une adresse d'avant les euros porte « salaire » sans unité, et son
        # nombre est un multiple du salaire moyen : la lire en euros en ferait
        # un salaire d'un euro par mois. Le défaut n'est donc l'euro que pour un
        # formulaire vierge — d'où le fait que ``requete`` écrive TOUJOURS
        # l'unité, ce qui rend la question sans objet pour les adresses neuves.
        ancienne = "unite_revenu" not in parametres and any(
            cle == "salaire" or cle.endswith("_salaire") for cle in parametres
        )
        unite = _parmi(parametres, "unite_revenu", UNITES_REVENU,
                       "moyen" if ancienne else defauts.unite_revenu)
        salaire = _reel(parametres, "salaire", SALAIRE_DEFAUT[unite])
        # La naissance se lit avant tout le reste : les dates de carrière ne
        # valent un âge que rapportées à elle.
        naissance = _date_saisie(parametres, "naissance")
        annee_naissance = (naissance[0] if naissance
                           else _entier(parametres, "naissance", defauts.naissance))
        mois_naissance = (naissance[1] if naissance else _entier(
            parametres, "naissance_mois", defauts.naissance_mois
        ))
        saisie = cls(
            unite_revenu=unite,
            montants=_parmi(parametres, "montants", MODES_MONTANT,
                            defauts.montants),
            naissance=annee_naissance,
            naissance_mois=mois_naissance,
            naissance_jour=naissance[2] if naissance else defauts.naissance_jour,
            sexe="F" if parametres.get("sexe") == "F" else "H",
            statut=statut,
            debut=_age_saisi(parametres, "debut", defauts.debut,
                             annee_naissance, mois_naissance),
            liquidation=_age_saisi(parametres, "liquidation", defauts.liquidation,
                                   annee_naissance, mois_naissance),
            salaire=salaire,
            metiers=_metiers_saisis(parametres, salaire,
                                    annee_naissance, mois_naissance),
            releve=(parametres.get("releve") or "").strip(),
            profil=_parmi(parametres, "profil", PROFILS, defauts.profil),
            primes=_reel(parametres, "primes", defauts.primes),
            enfants=_entier(parametres, "enfants", defauts.enfants),
            interruptions=(parametres.get("interruptions") or "").strip(),
            indexation=_parmi(parametres, "indexation", INDEXATIONS, defauts.indexation),
            lissage=_entier(parametres, "lissage", defauts.lissage),
            age_reference=_parmi(
                parametres, "age_reference", AGES_REFERENCE, defauts.age_reference
            ),
            table=_parmi(parametres, "table", TABLES, defauts.table),
            conversion_acquis=_parmi(
                parametres, "conversion_acquis", CONVERSIONS_ACQUIS,
                defauts.conversion_acquis,
            ),
            part_cotisation=_parmi(
                parametres, "part_cotisation", PARTS_COTISATION,
                defauts.part_cotisation,
            ),
            foyer=_parmi(parametres, "foyer", SITUATIONS_FOYER, defauts.foyer),
            projection=_parmi(parametres, "projection", PROJECTIONS, defauts.projection),
            bascule=_entier(parametres, "bascule", defauts.bascule),
            euros=_entier(parametres, "euros", defauts.euros),
            # Une adresse qui ne porte QUE des réglages de modélisation ne
            # demande pas de calcul : elle règle le modèle. C'est ce qui permet
            # aux liens internes de porter les réglages partout — y compris
            # vers le simulateur — sans que cliquer « Simuler » dans le bandeau
            # ne lance d'office le calcul d'une carrière que personne n'a
            # saisie. Toute adresse portant le moindre champ de carrière
            # demande un calcul, comme avant.
            demandee=any(cle not in CLES_MODELISATION for cle in parametres),
        )
        saisie.verifier()
        return saisie

    def verifier(self) -> None:
        if not 1 <= self.naissance_mois <= 12:
            raise ErreurSaisie("Mois de naissance attendu entre 1 et 12.")
        if not 1 <= self.naissance_jour <= 31:
            raise ErreurSaisie("Jour de naissance attendu entre 1 et 31.")
        if not NAISSANCE_MINIMALE <= self.naissance <= NAISSANCE_MAXIMALE:
            raise ErreurSaisie(
                f"Année de naissance hors du champ du modèle : {self.naissance}. "
                f"Attendu entre {NAISSANCE_MINIMALE} et {NAISSANCE_MAXIMALE}."
            )
        if not AGE_DEBUT_MINIMAL <= self.debut <= AGE_DEBUT_MAXIMAL:
            raise ErreurSaisie(
                "Début d'activité : le modèle l'accepte de "
                f"{AGE_DEBUT_MINIMAL} à {AGE_DEBUT_MAXIMAL} ans, soit "
                f"{self.fenetre(AGE_DEBUT_MINIMAL, AGE_DEBUT_MAXIMAL)}."
            )
        if not AGE_LIQUIDATION_MINIMAL <= self.liquidation <= AGE_LIQUIDATION_MAXIMAL:
            raise ErreurSaisie(
                "Départ à la retraite : le modèle l'accepte de "
                f"{AGE_LIQUIDATION_MINIMAL} à {AGE_LIQUIDATION_MAXIMAL} ans, soit "
                f"{self.fenetre(AGE_LIQUIDATION_MINIMAL, AGE_LIQUIDATION_MAXIMAL)}."
            )
        if self.liquidation <= self.debut:
            raise ErreurSaisie(
                "Le départ à la retraite doit suivre le début d'activité, "
                f"fixé en {self.date_de(self.debut)}."
            )
        self._verifier_revenu(self.salaire, rang=1)
        if not 0 <= self.primes <= 0.6:
            raise ErreurSaisie("Part de primes attendue entre 0 et 0,6.")
        if not 0 <= self.enfants <= ENFANTS_MAXIMUM:
            raise ErreurSaisie(
                f"Nombre d'enfants attendu entre 0 et {ENFANTS_MAXIMUM}."
            )
        if not ANNEE_MINIMALE <= self.bascule <= ANNEE_MAXIMALE:
            raise ErreurSaisie(
                f"Année de bascule attendue entre {ANNEE_MINIMALE} et "
                f"{ANNEE_MAXIMALE}."
            )
        if not ANNEE_MINIMALE <= self.euros <= ANNEE_MAXIMALE:
            raise ErreurSaisie(
                f"Année des euros constants attendue entre {ANNEE_MINIMALE} et "
                f"{ANNEE_MAXIMALE}."
            )
        if not 1 <= self.lissage <= LISSAGE_MAXIMUM:
            raise ErreurSaisie(
                f"Fenêtre de lissage attendue entre 1 et {LISSAGE_MAXIMUM} ans "
                "(1 = aucun lissage)."
            )
        # Les métiers se suivent sans se recouvrir : chacun commence après le
        # précédent et avant le départ à la retraite. C'est la seule chose que
        # le moteur exige, et elle se dit ici plutôt que par une exception
        # remontée du modèle.
        precedent = self.debut
        for rang, metier in enumerate(self.metiers, start=2):
            if not AGE_DEBUT_MINIMAL <= metier.debut <= AGE_LIQUIDATION_MAXIMAL:
                raise ErreurSaisie(
                    f"Métier n° {rang} : il doit commencer "
                    f"{self.fenetre(AGE_DEBUT_MINIMAL, AGE_LIQUIDATION_MAXIMAL)}, "
                    f"soit de {AGE_DEBUT_MINIMAL} à {AGE_LIQUIDATION_MAXIMAL} ans."
                )
            if metier.debut <= precedent:
                raise ErreurSaisie(
                    f"Métier n° {rang} : il doit commencer après le précédent, "
                    f"qui commence en {self.date_de(precedent)}."
                )
            if metier.debut >= self.liquidation:
                raise ErreurSaisie(
                    f"Métier n° {rang} : il doit commencer avant le départ à la "
                    f"retraite, fixé en {self.date_de(self.liquidation)}."
                )
            # Une période sans emploi ne porte pas de revenu : elle hérite de
            # celui d'avant, qui n'est pas ce qu'elle paie — elle ne paie
            # rien — mais le salaire de référence sur lequel l'UNEDIC cotise
            # aux régimes complémentaires.
            if not metier.sans_emploi:
                self._verifier_revenu(metier.salaire, rang=rang)
            precedent = metier.debut

    # -- l'unité des revenus -------------------------------------------------

    @property
    def revenu_en_euros(self) -> bool:
        """Vrai si les revenus sont saisis en euros, faux si c'est un ratio."""
        return self.unite_revenu == "euros_mois"

    @property
    def en_net(self) -> bool:
        """Vrai si tout — saisie et affichage — se lit en net."""
        return self.montants == "net"

    @property
    def saisie_en_net(self) -> bool:
        """Vrai si le nombre saisi est un NET à convertir.

        Le mode net ne change la SAISIE que lorsqu'elle est en euros : un
        multiple du salaire moyen est un rapport entre deux bruts, et le
        convertir n'aurait pas de sens — le salaire moyen publié par l'INSEE
        est brut.
        """
        return self.en_net and self.revenu_en_euros

    def _verifier_revenu(self, valeur: float, rang: int) -> None:
        """Un revenu saisi, contrôlé dans l'unité où il a été écrit.

        Le message parle la langue du champ : refuser « 2 500 € par mois » au
        motif qu'il faut « entre 0,1 et 10 fois le salaire moyen » ne dirait
        rien à qui n'a jamais entendu parler de cette unité.
        """
        if self.revenu_en_euros:
            if valeur <= 0:
                raise _refus(rang, "Le revenu doit être strictement positif.")
        elif not 0.1 <= valeur <= 10:
            raise _refus(
                rang,
                "Niveau de revenu attendu entre 0,1 et 10 fois le salaire moyen.",
            )

    @property
    def lignes_carriere(self) -> list[MetierSaisi]:
        """Toutes les lignes du formulaire, la première comprise.

        Le premier métier vit dans des champs à part — ``statut``, ``debut``,
        ``salaire`` —, parce que l'adresse les portait ainsi avant qu'une
        carrière puisse en compter plusieurs. Il n'y a pourtant aucune raison
        de le traiter autrement que les suivants, et tout ce qui parcourt la
        carrière passe par ici.
        """
        return [MetierSaisi(self.debut, self.statut, self.salaire), *self.metiers]

    def niveaux(self, echelle: "Echelle") -> list[float]:
        """Le revenu de chaque métier, ramené à l'unité du modèle.

        C'est ici, et nulle part ailleurs, que l'euro entre dans le modèle.
        Le moteur ne connaît que le multiple du salaire moyen : il garde son
        sens sur quatre-vingts ans, quand un montant n'en a que rapporté à son
        année.
        """
        lignes = self.lignes_carriere
        saisis = [ligne.salaire for ligne in lignes]
        if not self.revenu_en_euros:
            return saisis
        # En mode net, le nombre saisi n'est pas encore un brut : on remonte
        # d'abord jusqu'à lui, statut par statut, PUIS on ramène à l'unité du
        # modèle. L'ordre compte — le salaire moyen de l'échelle est un brut.
        if self.saisie_en_net:
            saisis = [echelle.brut_mensuel(valeur, ligne.statut)
                      for valeur, ligne in zip(saisis, lignes)]
        return [echelle.niveau(valeur) for valeur in saisis]

    def parcours(self, echelle: "Echelle") -> list[Metier]:
        """La carrière comme suite de MÉTIERS, le premier compris.

        C'est sous cette forme que le modèle la reçoit ; le formulaire, lui,
        garde le premier métier dans ses champs historiques.

        Les périodes sans emploi n'en sont pas : elles ne portent ni régime ni
        cotisation, et le métier qui les précède court, pour le modèle, jusqu'au
        métier suivant. Ce qu'elles changent — l'année ne cotise pas — passe
        par :meth:`interruptions_de_carriere`, qui est le seul chemin que le
        moteur connaisse pour une année non travaillée.
        """
        niveaux = self.niveaux(echelle)
        metiers = []
        for rang, (ligne, niveau) in enumerate(
            zip(self.lignes_carriere, niveaux), start=1,
        ):
            if ligne.sans_emploi:
                continue
            self._verifier_niveau(niveau, rang, echelle)
            metiers.append(Metier(affiliation=ligne.statut, age_debut=ligne.debut,
                                  niveau_salaire=niveau))
        return metiers

    def interruptions_de_carriere(
        self, motifs_connus: Iterable[str] | None = None,
    ) -> dict[int, str]:
        """Les années non cotisées : celles des lignes, et celles du champ.

        Une période sans emploi est bornée au MOIS sur le formulaire ; le
        modèle, lui, ne connaît qu'un statut par année civile — les régimes
        liquident à l'année. L'année où l'activité s'arrête revient donc à ce
        qui en occupe le plus de mois, exactement comme l'année d'un changement
        de métier revient au métier qui en occupe le plus ; à égalité, elle
        reste travaillée.

        Le champ « Interruptions » garde le dernier mot : il désigne des années
        une à une, et c'est l'outil le plus fin des deux.
        """
        annees: dict[int, str] = {}
        debut, fin = self.date_de(self.debut), self.date_de(self.liquidation)
        lignes = self.lignes_carriere
        for rang, ligne in enumerate(lignes):
            if not ligne.sans_emploi:
                continue
            ouverture = self.date_de(ligne.debut)
            cloture = (self.date_de(lignes[rang + 1].debut)
                       if rang + 1 < len(lignes) else fin)
            for annee in range(ouverture.annee, cloture.annee + 1):
                creux = mois_travailles(annee, ouverture, cloture)
                portee = mois_travailles(annee, debut, fin)
                if portee and creux * 2 > portee:
                    annees[annee] = ligne.statut
        annees.update(self.interruptions_analysees(motifs_connus))
        return annees

    def _verifier_niveau(self, niveau: float, rang: int,
                         echelle: "Echelle") -> None:
        """Le salaire converti tient-il dans ce que le modèle sait décrire ?

        Le contrôle ne peut se faire qu'ici : « 0,1 à 10 fois le salaire moyen »
        ne devient un intervalle d'euros qu'une fois la série chargée. Le refus
        redit donc les bornes en euros, faute de quoi il n'indiquerait pas quoi
        corriger.
        """
        if 0.1 <= niveau <= 10:
            return
        if not self.revenu_en_euros:
            raise _refus(
                rang,
                "Niveau de revenu attendu entre 0,1 et 10 fois le salaire moyen.",
            )
        raise _refus(
            rang,
            f"Ce revenu vaut {g.nombre(niveau, 2)} fois le salaire moyen ; le "
            "modèle en accepte de 0,1 à 10 fois, soit de "
            f"{g.nombre(echelle.mensuel(0.1), 0)} à "
            f"{g.euros(echelle.mensuel(10))} bruts par mois.",
        )

    # -- les dates ------------------------------------------------------------
    #
    # Le formulaire ne demande plus d'âges mais des dates : c'est la même
    # information — un âge est une date rapportée à la naissance —, mais celle
    # que le lecteur connaît sans la calculer. Le modèle, lui, continue de
    # recevoir des âges : la conversion tient dans les méthodes qui suivent, et
    # nulle part ailleurs.

    def date_de(self, age: float) -> DateMois:
        """Le mois où la carrière atteint cet âge."""
        return DateMois(self.naissance, self.naissance_mois).plus_mois(en_mois(age))

    def mois_de(self, age: float) -> str:
        """Le même mois, tel que l'adresse le porte : « 1996-09 »."""
        date = self.date_de(age)
        return f"{date.annee:04d}-{date.mois:02d}"

    def jour_de(self, age: float) -> str:
        """Le même mois au premier jour : ce qu'un champ date, lui, exige."""
        return f"{self.mois_de(age)}-01"

    def fenetre(self, age_minimal: float, age_maximal: float) -> str:
        """« de septembre 1989 à septembre 2015 » : deux bornes d'âge, en dates.

        Un refus qui ne parlerait que d'âges laisserait au lecteur la
        soustraction à faire, alors que le champ qu'il vient de remplir porte
        une date.
        """
        return f"de {self.date_de(age_minimal)} à {self.date_de(age_maximal)}"

    @property
    def naissance_iso(self) -> str:
        """La naissance telle qu'un champ date la porte : « 1975-03-15 »."""
        return (f"{self.naissance:04d}-{self.naissance_mois:02d}"
                f"-{self.naissance_jour:02d}")

    # -- ce qu'on écrit sous un calendrier ------------------------------------
    #
    # Un champ date s'affiche dans l'ordre de la langue du NAVIGATEUR, que la
    # page ne choisit pas : « 15/03/1962 » ici, « 03/15/1962 » sur un
    # navigateur anglophone, et rien ne dit lequel des deux nombres est le
    # mois. La date est donc redite en toutes lettres sous le champ, où aucun
    # ordre ne se devine — et, pour une date de carrière, avec l'âge qu'elle
    # fait, qui est ce que le formulaire demandait avant elle.

    @property
    def naissance_en_clair(self) -> str:
        """« le 15 mars 1962 » : la date de naissance, sans ordre à deviner."""
        return f"le {_jour_en_clair(self.naissance_jour)} " \
               f"{NOMS_DE_MOIS[self.naissance_mois - 1]} {self.naissance}"

    def calcul_de(self, age: float) -> str:
        """« en septembre 1984, soit 22 ans et 6 mois » : une date de carrière."""
        if age < 0:
            return f"en {self.date_de(age)}, avant la date de naissance"
        return f"en {self.date_de(age)}, soit {_age(age)}"

    def parametres(self, base: Parametres) -> Parametres:
        return base.avec(
            mode_indexation=ModeIndexation(self.indexation),
            lissage_indexation=self.lissage,
            mode_age_reference=ModeAgeReference(self.age_reference),
            table_conversion=TableConversion(self.table),
            age_conversion_droits_acquis=AgeConversionDroitsAcquis(
                self.conversion_acquis
            ),
            part_cotisation=PartCotisation(
                self.part_cotisation
            ),
            situation_foyer=SituationFoyer(self.foyer),
            scenario_projection=self.projection,
            annee_bascule=self.bascule,
            annee_euros_constants=self.euros,
        )

    @classmethod
    def modelisation(cls, parametres: dict[str, str]) -> "Saisie":
        """La saisie réduite à ses RÈGLES, pour les pages qui agrègent.

        Les pages Cas types, Coût et Avantages ne calculent aucune carrière
        saisie : elles croisent des carrières types avec des générations. Ce
        qu'elles doivent retenir d'une adresse, ce sont les réglages de
        modélisation — et eux seuls. Une adresse de simulateur collée sur la
        page Coût y décrit donc un jeu de règles, jamais un individu : la
        naissance, le statut et le revenu qu'elle porte sont ignorés, et une
        faute dans l'un d'eux ne peut pas faire échouer la page.
        """
        return cls.depuis_requete({
            cle: valeur for cle, valeur in parametres.items()
            if cle in CLES_MODELISATION
        })

    def requete_modelisation(self) -> str:
        """Les réglages qui s'écartent du défaut, écrits comme une requête.

        Vide tant que rien n'a été changé : les adresses du site restent alors
        celles d'avant, au caractère près, et un lien partagé ne porte que ce
        que son auteur a effectivement réglé.
        """
        defauts = Saisie()
        return urlencode({
            cle: getattr(self, cle) for cle in CLES_MODELISATION
            if getattr(self, cle) != getattr(defauts, cle)
        })

    def interruptions_analysees(
        self, motifs_connus: Iterable[str] | None = None,
    ) -> dict[int, str]:
        """« 1995:1999:education_enfant, 2003:2004:chomage_indemnise » -> dict.

        Trois contrôles s'ajoutent à celui de la forme, parce que les trois
        fautes qu'ils attrapent étaient muettes.

        Une plage sans borne bouclait autant de fois qu'elle comptait d'années :
        « 0:999999999:chomage_indemnise » remplissait la mémoire et figeait
        l'onglet. Le calcul se fait chez le lecteur, et l'adresse EST la
        saisie : le lien suffisait donc à figer l'onglet de quelqu'un d'autre.
        Les années sont désormais tenues dans la fenêtre que n'importe quelle
        carrière peut couvrir.

        Une plage à l'envers — « 2004:2003 » — ne décrivait rien : la boucle ne
        tournait pas, et l'interruption saisie n'existait nulle part.

        Un motif mal orthographié, enfin, retombait sur ``sans_activite`` :
        « educaton_enfant » validait zéro trimestre au lieu de quatre et
        changeait la pension affichée, sans un mot. Se tromper de touche ne doit
        pas donner un autre chiffre, mais un refus.

        ``motifs_connus`` est la liste que porte le paquet de données. Une
        saisie ne connaît pas les données : l'appelant la fournit, et le
        contrôle du motif n'a lieu que s'il l'a fait.
        """
        plages: dict[int, str] = {}
        connus = None if motifs_connus is None else sorted(motifs_connus)
        for morceau in self.interruptions.replace("\n", ",").split(","):
            morceau = morceau.strip()
            if not morceau:
                continue
            parties = morceau.split(":")
            if len(parties) != 3 or not all(
                _est_entier(partie) for partie in parties[:2]
            ):
                raise ErreurSaisie(
                    f"Interruption mal formée : « {morceau} ». Attendu "
                    "« année_début:année_fin:motif », par exemple "
                    "1995:1999:education_enfant."
                )
            debut, fin = int(parties[0]), int(parties[1])
            motif = parties[2].strip()
            # L'année est citée TELLE QU'ELLE A ÉTÉ ÉCRITE, et non relue du
            # nombre : « 999999999999999999999 » reste un entier ici et
            # devient « 1e+21 » en JavaScript, si bien que les deux moteurs
            # refusaient la même saisie par deux phrases différentes.
            for texte, annee in ((parties[0], debut), (parties[1], fin)):
                if not ANNEE_CARRIERE_MINIMALE <= annee <= ANNEE_CARRIERE_MAXIMALE:
                    raise ErreurSaisie(
                        f"Interruption « {morceau} » : {texte.strip()} ne tombe "
                        "dans aucune carrière possible. Attendu entre "
                        f"{ANNEE_CARRIERE_MINIMALE} et {ANNEE_CARRIERE_MAXIMALE}."
                    )
            if fin < debut:
                raise ErreurSaisie(
                    f"Interruption « {morceau} » : elle finit ({fin}) avant de "
                    f"commencer ({debut})."
                )
            if connus is not None and motif not in connus:
                raise ErreurSaisie(
                    f"Interruption « {morceau} » : motif inconnu « {motif} ». "
                    "Attendu l'un de : " + ", ".join(connus) + "."
                )
            for annee in range(debut, fin + 1):
                plages[annee] = motif
        return plages

    @property
    def releve_actif(self) -> bool:
        """Vrai si la carrière est LUE plutôt que reconstituée."""
        return bool(self.releve.strip())

    @property
    def date_liquidation(self) -> DateMois:
        """Le mois où la pension prend effet — la borne du relevé.

        La même arithmétique que :attr:`Carriere.date_liquidation`, en amont du
        modèle : le refus d'une année postérieure au départ doit se prononcer
        sur la saisie, avec le vocabulaire du formulaire, et non remonter du
        moteur sous la forme d'une exception.
        """
        return self.date_de(self.liquidation)

    def releve_analyse(
        self, motifs_connus: Iterable[str] | None = None,
    ) -> list[LigneRelevee]:
        """« 2005:salarie_prive_non_cadre:24000:4, … » -> lignes de relevé.

        Le format est celui du relevé lui-même, dans l'ordre où il l'imprime :
        l'année, le régime, le revenu de l'année, les trimestres qu'elle a
        validés. Les trois premiers champs sont exigés ; le quatrième est
        facultatif — sans lui, le modèle déduit les trimestres du montant
        cotisé, comme il le fait d'une carrière paramétrique.

        **Le revenu est celui de l'année, en euros de cette année-là**, et non
        un multiple du salaire moyen ni un montant mensuel : c'est ce que le
        relevé porte, et l'unité du modèle. Un relevé antérieur à 2002 est en
        francs, à diviser par 6,55957.

        **Les années non cotisées** se déclarent dans le champ
        « Interruptions », qui reste lu quand un relevé est saisi : il associe
        une année à un motif, ce que le relevé ne sait pas dire. La ligne de
        l'année garde alors ses trimestres — le relevé fait foi — et son revenu
        devient le salaire de référence d'avant l'interruption.

        Les refus sont ceux qu'``interruptions_analysees`` a appris à
        prononcer : une année hors de toute carrière possible, une ligne mal
        formée, un doublon. S'y ajoute la seule borne que le relevé rende
        nécessaire — le nombre de lignes : le calcul se fait chez le lecteur, et
        un relevé forgé dans un lien figerait l'onglet de celui qui le suit.
        """
        interruptions = self.interruptions_analysees(motifs_connus)
        depart = self.date_liquidation
        # Les lignes sont COMPTÉES avant d'être lues : le refus doit coûter le
        # découpage du texte, et rien de plus. Les analyser d'abord pour les
        # compter ensuite ferait payer au lecteur le relevé de cent mille
        # lignes qu'un lien lui aurait tendu — c'est la faute que les plages
        # d'interruption avaient déjà commise.
        morceaux = [morceau.strip() for morceau
                    in self.releve.replace("\n", ",").replace(";", ",").split(",")]
        morceaux = [morceau for morceau in morceaux if morceau]
        if not morceaux:
            raise ErreurSaisie(
                "Relevé de carrière vide : le laisser entièrement vide pour "
                "décrire la carrière par ses métiers."
            )
        if len(morceaux) > RELEVE_MAXIMUM:
            raise ErreurSaisie(
                f"Relevé de {len(morceaux)} lignes : le modèle en accepte "
                f"{RELEVE_MAXIMUM} au plus, ce qu'aucune carrière ne dépasse."
            )
        lignes: list[LigneRelevee] = []
        vues: set[int] = set()
        for morceau in morceaux:
            parties = [partie.strip() for partie in morceau.split(":")]
            if not 3 <= len(parties) <= 4 or not _est_entier(parties[0]):
                raise ErreurSaisie(
                    f"Ligne de relevé mal formée : « {morceau} ». Attendu "
                    "« année:régime:revenu » ou « année:régime:revenu:trimestres », "
                    "par exemple 2005:salarie_prive_non_cadre:24000:4."
                )
            annee = int(parties[0])
            # L'année est citée TELLE QU'ELLE A ÉTÉ ÉCRITE, comme pour les
            # interruptions : « 999999999999999999999 » reste un entier en
            # Python et devient « 1e+21 » en JavaScript, et les deux moteurs
            # refuseraient la même saisie par deux phrases différentes.
            if not ANNEE_CARRIERE_MINIMALE <= annee <= ANNEE_CARRIERE_MAXIMALE:
                raise ErreurSaisie(
                    f"Relevé « {morceau} » : {parties[0]} ne tombe dans aucune "
                    f"carrière possible. Attendu entre {ANNEE_CARRIERE_MINIMALE} "
                    f"et {ANNEE_CARRIERE_MAXIMALE}."
                )
            if annee in vues:
                raise ErreurSaisie(
                    f"Relevé : l'année {annee} est déclarée deux fois. Une "
                    "année civile ne porte qu'une ligne — les régimes liquident "
                    "à l'année."
                )
            vues.add(annee)
            if annee < self.naissance + AGE_DEBUT_MINIMAL:
                raise ErreurSaisie(
                    f"Relevé « {morceau} » : l'assuré, né en {self.naissance}, "
                    f"n'a pas {AGE_DEBUT_MINIMAL} ans en {annee}."
                )
            if annee > depart.annee or (annee == depart.annee and depart.mois == 1):
                raise ErreurSaisie(
                    f"Relevé « {morceau} » : l'année {annee} est postérieure au "
                    f"départ à la retraite, fixé au {depart}."
                )
            if not parties[1]:
                raise ErreurSaisie(
                    f"Relevé « {morceau} » : indiquer le statut d'affiliation."
                )
            revenu = _vers_flottant(parties[2])
            if revenu is None or revenu < 0:
                raise ErreurSaisie(
                    f"Relevé « {morceau} » : revenu de l'année attendu positif "
                    "ou nul, en euros de cette année-là."
                )
            trimestres = None
            if len(parties) == 4 and parties[3]:
                if not _est_entier(parties[3]) or not 0 <= int(parties[3]) <= 4:
                    raise ErreurSaisie(
                        f"Relevé « {morceau} » : trimestres attendus entre 0 et 4."
                    )
                trimestres = int(parties[3])
            lignes.append(LigneRelevee(
                annee=annee,
                affiliation=parties[1],
                revenu=revenu,
                trimestres=trimestres,
                type_periode=interruptions.get(annee, "emploi"),
            ))
        return lignes

    def requete(self, **remplacements) -> str:
        champs = {
            "naissance": self.naissance_iso,
            "sexe": self.sexe, "statut": self.statut,
            # Les dates remplacent les âges, et l'adresse y perd trois
            # paramètres : « debut=1996-09 » dit d'un coup ce que « debut=21 »
            # et « debut_mois=8 » disaient à deux, sans que personne ait à
            # refaire l'addition. Une adresse d'ancienne forme reste lue — les
            # âges y sont reconnus tels quels, voir ``_age_saisi``.
            "debut": self.mois_de(self.debut),
            "liquidation": self.mois_de(self.liquidation),
            "salaire": _nombre(self.salaire), "profil": self.profil,
            "releve": self.releve,
            "primes": _nombre(self.primes), "enfants": self.enfants,
            "interruptions": self.interruptions, "indexation": self.indexation,
            "lissage": self.lissage,
            "age_reference": self.age_reference, "table": self.table,
            "conversion_acquis": self.conversion_acquis,
            "part_cotisation": self.part_cotisation,
            "foyer": self.foyer,
            "projection": self.projection, "bascule": self.bascule, "euros": self.euros,
        }
        # L'unité s'écrit TOUJOURS, y compris quand c'est celle par défaut :
        # c'est ce qui distingue une adresse neuve d'une adresse d'avant les
        # euros, dont le « salaire » nu est un multiple du salaire moyen.
        champs["unite_revenu"] = self.unite_revenu
        # Le mode s'écrit toujours lui aussi : il gouverne l'interprétation du
        # nombre « salaire », et une adresse partagée qui l'omettrait décrirait
        # une autre carrière que celle qu'on a calculée.
        champs["montants"] = self.montants
        # Les métiers qui suivent le premier, un groupe de trois champs chacun.
        # Une ligne vide du formulaire n'en produit aucun : l'adresse ne porte
        # que ce qui a été saisi.
        for rang, metier in enumerate(self.metiers, start=2):
            champs[f"metier{rang}_debut"] = self.mois_de(metier.debut)
            champs[f"metier{rang}_statut"] = metier.statut
            champs[f"metier{rang}_salaire"] = _nombre(metier.salaire)
        champs.update(remplacements)
        return urlencode(champs)


def _metiers_saisis(parametres: dict[str, str], salaire_precedent: float,
                    naissance: int, naissance_mois: int) -> list[MetierSaisi]:
    """Les métiers qui suivent le premier, lus dans « metier2_… », « metier3_… ».

    Le formulaire affiche toujours une ligne de plus qu'il n'y a de métiers :
    tant qu'elle reste vide, elle ne décrit rien. Une ligne partiellement
    remplie, en revanche, est une intention manquée — elle est refusée, avec ce
    qui lui manque.
    """
    metiers: list[MetierSaisi] = []
    for rang in range(2, METIERS_MAXIMUM + 1):
        debut = (parametres.get(f"metier{rang}_debut") or "").strip()
        statut = (parametres.get(f"metier{rang}_statut") or "").strip()
        salaire = (parametres.get(f"metier{rang}_salaire") or "").strip()
        if not (debut or statut or salaire):
            continue
        if not debut:
            raise ErreurSaisie(
                f"Métier n° {rang} : indiquer la date à laquelle il commence, "
                "ou laisser sa ligne entièrement vide."
            )
        if not statut:
            raise ErreurSaisie(
                f"Métier n° {rang} : indiquer le statut d'affiliation."
            )
        # Une période sans emploi ne lit pas le champ de revenu : elle hérite
        # de celui d'avant, et la ligne suivante en hérite à son tour. Ce n'est
        # pas ce qu'elle paie — elle ne paie rien — mais le salaire de
        # référence sur lequel l'UNEDIC cotise aux complémentaires.
        sans_emploi = statut in CODES_SANS_EMPLOI
        if not sans_emploi:
            salaire_precedent = _reel(
                parametres, f"metier{rang}_salaire", salaire_precedent
            )
        metiers.append(MetierSaisi(
            debut=_age_saisi(parametres, f"metier{rang}_debut", 0.0,
                             naissance, naissance_mois),
            statut=statut,
            salaire=salaire_precedent,
            sans_emploi=sans_emploi,
        ))
    return metiers


#: Ce qu'un nombre saisi a le droit de s'écrire — et rien d'autre. L'expression
#: est celle de ``moteur/js/pages.js``, au caractère près, parce que ``float``
#: et ``Number`` ne lisent pas le même langage : ``float`` accepte « nan »,
#: « inf » et « 1_975 », que ``Number`` refuse. Les deux lectures se seraient
#: séparées sur une adresse forgée, et le témoin ne l'aurait pas vu : personne
#: ne tire « nan » au hasard.
_NOMBRE = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")


#: Un entier saisi, bornes d'une plage d'interruption comprises. Même
#: expression que ``EST_ENTIER`` du portage : « 1995 » oui, « 1995,0 » non.
_ENTIER = re.compile(r"^\s*[+-]?\d+\s*$")

#: Une date de formulaire ou d'adresse : « 1975-03-15 », ou « 1996-09 » quand
#: le jour ne sert à rien. Rien d'autre n'en est une — un âge nu, « 64 », est
#: une adresse d'avant le calendrier, et se lit comme tel.
_DATE = re.compile(r"^\s*(\d{4})-(\d{2})(?:-(\d{2}))?\s*$")


def _est_entier(texte: str) -> bool:
    return bool(_ENTIER.match(str(texte)))


def _vers_flottant(texte: str) -> float | None:
    """Le nombre écrit dans ce texte, ou ``None`` s'il n'y en a pas.

    L'infini n'en est pas un : « 1e400 » passe l'expression ci-dessus et vaut
    ``inf``, que la suite du calcul propage sans jamais échouer — le simulateur
    affichait « Ce revenu vaut inf fois le salaire moyen ». Il se refuse ici,
    là où le nombre entre, plutôt qu'à chacun des contrôles qui le liraient.
    """
    propre = str(texte).strip()
    if not _NOMBRE.match(propre):
        return None
    valeur = float(propre)
    return valeur if math.isfinite(valeur) else None


def _entier(parametres: dict[str, str], nom: str, defaut: int) -> int:
    valeur = parametres.get(nom)
    if valeur in (None, ""):
        return defaut
    flottant = _vers_flottant(valeur)
    if flottant is None:
        raise ErreurSaisie(f"« {nom} » doit être un nombre entier (reçu : {valeur}).")
    return int(flottant)


def _reel(parametres: dict[str, str], nom: str, defaut: float) -> float:
    valeur = parametres.get(nom)
    if valeur in (None, ""):
        return defaut
    flottant = _vers_flottant(str(valeur).replace(",", "."))
    if flottant is None:
        raise ErreurSaisie(f"« {nom} » doit être un nombre (reçu : {valeur}).")
    return flottant


def _date_saisie(parametres: dict[str, str],
                 nom: str) -> tuple[int, int, int] | None:
    """La date écrite dans ce champ, ou ``None`` s'il n'en porte pas.

    Le formulaire envoie « 1975-03-15 » : c'est la forme qu'un ``<input
    type="date">`` renvoie partout, quelle que soit celle — « 15/03/1975 » en
    français — sous laquelle le navigateur l'a affichée. L'adresse, elle, s'en
    tient au mois pour les dates de carrière : « debut=1996-09 », le jour n'y
    ayant aucun rôle.

    Une adresse d'avant le calendrier porte des âges et une année nus —
    « naissance=1975 », « liquidation=64 » : rien ici ne les reconnaît, et
    ``None`` renvoie le lecteur aux champs numériques d'alors.
    """
    brut = parametres.get(nom)
    if brut in (None, ""):
        return None
    trouve = _DATE.match(str(brut))
    if trouve is None:
        return None
    annee, mois = int(trouve.group(1)), int(trouve.group(2))
    jour = int(trouve.group(3) or 1)
    if not 1 <= mois <= 12:
        raise ErreurSaisie(f"« {nom} » : mois attendu entre 01 et 12 (reçu : {brut}).")
    # Le jour n'est borné que grossièrement : il ne sert à aucun calcul, et le
    # refuser au calendrier près — un 31 février — n'épargnerait rien à
    # personne, puisque aucun champ date ne le propose.
    if not 1 <= jour <= 31:
        raise ErreurSaisie(f"« {nom} » : jour attendu entre 01 et 31 (reçu : {brut}).")
    return annee, mois, jour


def _age_saisi(parametres: dict[str, str], nom: str, defaut: float,
               naissance: int, naissance_mois: int) -> float:
    """L'âge qu'une date de carrière vaut, rapportée à la naissance.

    Le formulaire demande une date — celle du premier mois cotisé, celle du
    départ —, parce que c'est ce dont on se souvient ; le modèle, lui, ne
    connaît que des âges. La soustraction se fait ici, en mois, et le résultat
    est l'âge en années décimales que le moteur attend.

    Les adresses d'avant le calendrier continuent d'être lues telles quelles :
    ``liquidation=64`` et ``liquidation_mois=7`` valent soixante-quatre ans et
    sept mois, ``liquidation=64.5`` vaut ce qu'il a toujours valu.
    """
    date = _date_saisie(parametres, nom)
    if date is not None:
        rang = (DateMois(date[0], date[1]).rang
                - DateMois(naissance, naissance_mois).rang)
        return rang / MOIS_PAR_AN
    annees = _reel(parametres, nom, defaut)
    cle = f"{nom}_mois"
    if parametres.get(cle) in (None, ""):
        return annees
    mois = _entier(parametres, cle, 0)
    if not 0 <= mois <= 11:
        raise ErreurSaisie(f"« {cle} » doit être compris entre 0 et 11 mois.")
    return math.floor(annees) + mois / 12


def _parmi(parametres: dict[str, str], nom: str,
           options: list[tuple[str, str]], defaut: str) -> str:
    valeur = parametres.get(nom)
    codes = {code for code, _ in options}
    return valeur if valeur in codes else defaut


def _nombre(valeur: float) -> str:
    """Valeur telle qu'elle est réinjectée dans un champ de formulaire."""
    return f"{valeur:g}"


def _date_en_clair(iso: str) -> str:
    """« 2026-09-13 » -> « 13 septembre 2026 », la date telle qu'on la lit."""
    annee, mois, jour = (int(morceau) for morceau in iso.split("-"))
    return f"{_jour_en_clair(jour)} {NOMS_DE_MOIS[mois - 1]} {annee}"


def _jour_en_clair(jour: int) -> str:
    """Le premier du mois est un ORDINAL en français : « 1er », et non « 1 »."""
    return "1er" if jour == 1 else str(jour)


#: Ce que le COR projette pour le système actuel, en part du PIB : le repère
#: extérieur auquel la page se compare. Rapport annuel de juin 2025, champ
#: « ensemble des régimes légalement obligatoires, y compris FSV, hors RAFP ».
COR_2024 = 0.139
COR_2070 = 0.142


def _age(valeur: float) -> str:
    """Âge à la française, en ans et en mois : « 64 ans », « 64 ans et 9 mois ».

    Le modèle date la liquidation au mois : l'écrire « 64,75 » demanderait au
    lecteur de multiplier par douze pour retrouver ce qu'il a saisi.
    """
    return formater_age(valeur)


# -- fabrique ----------------------------------------------------------------


@dataclass(frozen=True)
class Echelle:
    """L'échelle des salaires d'une année : le repère, et les conversions.

    Le modèle raisonne en multiples du salaire moyen ; le formulaire, en euros.
    Tout le passage de l'un à l'autre tient dans cet objet, construit une fois
    par rendu, pour que la conversion n'existe qu'à un seul endroit et que ce
    qui s'affiche soit exactement ce qui se calcule.
    """

    #: Salaire moyen par tête, en euros BRUTS annuels de l'année de référence.
    moyen: float
    #: SMIC mensuel brut de la même année, sur 151,67 heures.
    smic: float
    #: Plafond mensuel de la Sécurité sociale de la même année.
    plafond: float
    #: Ce qui remonte d'un net mensuel au brut qui le laisse, statut par
    #: statut. ``None`` en mode brut — il n'y a alors rien à convertir — et
    #: dans les pages qui n'ont pas de saisie. Voir
    #: ``remuneration.salaire_brut_depuis_net``.
    vers_brut: object | None = None
    #: Les deux sens, toujours disponibles : ils ne servent qu'à la bascule,
    #: qui doit traduire quel que soit le mode où l'on se trouve.
    vers_net: object | None = None
    vers_brut_direct: object | None = None

    def brut_mensuel(self, montant: float, statut: str) -> float:
        """Le brut mensuel d'un montant saisi, quel que soit le mode.

        En mode brut, c'est le montant lui-même ; en mode net, ce que la fiche
        de paie du statut laisse. Les statuts que le modèle ne sait pas décrire
        rendent le montant inchangé : voir ``convertit``.
        """
        if self.vers_brut is None or montant <= 0:
            return montant
        return self.vers_brut(montant, statut)

    def brut_mensuel_direct(self, net: float, statut: str) -> float:
        """Le net vers le brut, quel que soit le mode courant.

        ``brut_mensuel`` ne convertit qu'en mode net — c'est ce qui le rend sûr
        au milieu du calcul. La bascule, elle, doit convertir depuis le mode où
        l'on est vers celui où l'on va, donc sans condition.
        """
        if self.vers_brut_direct is None or net <= 0:
            return net
        return self.vers_brut_direct(net, statut)

    def net_mensuel(self, brut: float, statut: str) -> float:
        """Le sens direct : ce qu'un brut mensuel laisse, statut par statut.

        Sert à la BASCULE, et non au calcul : passer du brut au net doit
        traduire le nombre saisi, pour que la page revienne en décrivant la
        même carrière.
        """
        if self.vers_net is None or brut <= 0:
            return brut
        return self.vers_net(brut, statut)

    def convertit(self, statut: str) -> bool:
        """La conversion a-t-elle un effet pour ce statut ?

        Faux pour un exploitant agricole, un élu, un ultramarin : le modèle n'a
        pas leurs prélèvements hors retraite, et le nombre saisi est alors lu
        comme un brut. Le formulaire le dit plutôt que de le taire.
        """
        if self.vers_net is None:
            return False
        return self.net_mensuel(1000.0, statut) != 1000.0

    def niveau(self, euros_mensuels: float) -> float:
        """Un salaire mensuel brut, en multiples du salaire moyen."""
        return euros_mensuels * MOIS_PAR_AN / self.moyen

    def mensuel(self, niveau: float) -> float:
        """L'opération inverse : un multiple, en euros bruts par mois."""
        return niveau * self.moyen / MOIS_PAR_AN


#: Combien d'agrégats le contexte garde en mémoire, tous jeux de règles
#: confondus. Deux par jeu — le coût et les avantages —, donc trois jeux de
#: règles : celui par défaut, et les deux derniers essayés.
AGREGATS_MEMORISES = 6


@dataclass
class Contexte:
    """Les données du site, et le jeu de règles sous lequel on les lit.

    Un contexte, c'est deux choses : des données coûteuses à charger, et UN jeu
    de paramètres — ``base`` — sous lequel tout ce que la page demande est
    calculé. ``simulateur()``, ``cout()`` et ``avantages()`` répondent tous
    trois sous ce jeu-là, sans qu'aucune page ait à le leur redire.

    Les trois pages qui AGRÈGENT — Cas types, Coût, Avantages — se rendent donc
    sous un contexte dérivé par :meth:`pour`, portant les réglages que l'adresse
    demande. Le corps des pages n'en sait rien : il lit ``contexte.base`` comme
    il l'a toujours fait, et y trouve les règles en vigueur au lieu des règles
    par défaut. C'est ce qui évite de faire passer un jeu de paramètres à la
    main dans la trentaine d'endroits qui les lisent.

    Les mémoires sont des dictionnaires plutôt qu'un champ par donnée, et c'est
    ce qui fait tenir la dérivation : un dictionnaire passe par référence, si
    bien qu'un contexte dérivé PARTAGE ce que le contexte d'origine a déjà
    chargé. Le chargement des données coûte quelques dixièmes de seconde, une
    simulation en coûte dix, un agrégat deux secondes : rien de tout cela ne
    doit se refaire parce qu'on a changé une règle.
    """

    base: Parametres = field(default_factory=Parametres)
    #: Un simulateur par jeu de paramètres rencontré.
    _instances: dict[Parametres, Simulateur] = field(default_factory=dict)
    #: Ce qui ne dépend d'AUCUN paramètre : dépense observée, comptes du COR,
    #: population, distribution des pensions, assiette, inventaire des
    #: avantages. Ces séries sont lues, jamais calculées : un changement de
    #: règle ne les déplace pas.
    _donnees: dict[str, object] = field(default_factory=dict)
    #: Les agrégats, eux, dépendent des règles : un coût par jeu de paramètres.
    _agregats: dict[tuple[str, Parametres], object] = field(default_factory=dict)

    def pour(self, parametres: Parametres) -> "Contexte":
        """Le même contexte, sous un autre jeu de règles.

        Les mémoires sont partagées, pas recopiées : dériver ne coûte rien, et
        ce que l'un charge, l'autre le trouve chargé.
        """
        if parametres == self.base:
            return self
        return Contexte(base=parametres, _instances=self._instances,
                        _donnees=self._donnees, _agregats=self._agregats)

    def _donnee(self, nom: str, fabrique):
        """Une donnée indépendante des règles, chargée une fois pour toutes."""
        if nom not in self._donnees:
            self._donnees[nom] = fabrique()
        return self._donnees[nom]

    def _agregat(self, nom: str, fabrique):
        """Un agrégat, mémorisé par jeu de règles — et en nombre borné.

        Sans borne, une adresse suffirait à faire enfler la mémoire de l'onglet
        d'un jeu de règles à l'autre : le calcul se fait chez le lecteur, et
        l'adresse EST la saisie. Le plus ancien s'en va ; revenir aux réglages
        par défaut après en avoir essayé trois recalcule, deux secondes.
        """
        cle = (nom, self.base)
        if cle not in self._agregats:
            if len(self._agregats) >= AGREGATS_MEMORISES:
                self._agregats.pop(next(iter(self._agregats)))
            self._agregats[cle] = fabrique()
        return self._agregats[cle]

    def simulateur(self, parametres: Parametres | None = None) -> Simulateur:
        parametres = parametres or self.base
        if parametres not in self._instances:
            self._instances[parametres] = Simulateur(parametres)
        return self._instances[parametres]

    def depenses(self) -> DepensesRetraite:
        return self._donnee(
            "depenses", lambda: DepensesRetraite(self.base.racine_donnees))

    def comptes(self) -> ComptesRetraite:
        """Le second terme du bilan : ce que le système de retraite encaisse."""
        return self._donnee(
            "comptes", lambda: ComptesRetraite(self.base.racine_donnees))

    def population(self) -> Population:
        return self._donnee(
            "population", lambda: Population(self.base.racine_donnees))

    def distribution(self) -> DistributionPensions:
        """La distribution des pensions — elle seule chiffre un plancher."""
        return self._donnee(
            "distribution", lambda: DistributionPensions(self.base.racine_donnees))

    def assiette(self) -> AssietteActivite:
        """Sur quoi l'on prélève : sans elle, un taux ne devient pas une recette."""
        return self._donnee(
            "assiette", lambda: AssietteActivite(self.base.racine_donnees))

    def cout(self):
        """Le coût agrégé de tous les systèmes — deux secondes de calcul, une fois.

        Sous les règles de ``base``, et non sous celles par défaut : c'est ce
        qui fait que la page Coût chiffre ce que le simulateur calcule.
        """
        return self._agregat("cout", lambda: calculer_cout(
            self.simulateur(), self.depenses(), self.population(),
            self.comptes(), assiette=self.assiette()))

    def inventaire_avantages(self):
        """Les trente-neuf avantages non contributifs — une donnée, pas un calcul."""
        return self._donnee(
            "inventaire_avantages",
            lambda: charger_avantages(self.base.racine_donnees))

    def avantages(self):
        """Ce que les avantages non contributifs coûtent — quatre secondes, une fois."""
        return self._agregat("avantages", lambda: calculer_avantages(
            self.simulateur(), self.depenses(), self.population()))

    def echelle(self, saisie: Saisie) -> Echelle:
        """L'échelle des salaires de l'année courante, pour cette saisie.

        L'année est celle du modèle — on saisit un salaire d'aujourd'hui —, et
        les séries sont CELLES DE LA SAISIE : au-delà de la dernière année
        observée, le salaire moyen dépend du scénario de projection choisi.
        """
        parametres = saisie.parametres(self.base)
        macro = self.simulateur(parametres).macro
        annee = parametres.annee_courante
        simulateur = self.simulateur(parametres)

        def vers_brut(net_mensuel: float, statut: str) -> float:
            return salaire_brut_depuis_net(
                parametres.racine_donnees, macro, simulateur.catalogue,
                simulateur.affiliations, statut, annee,
                net_mensuel * MOIS_PAR_AN,
            ) / MOIS_PAR_AN

        def vers_net(brut_mensuel: float, statut: str) -> float:
            return salaire_net_depuis_brut(
                parametres.racine_donnees, macro, simulateur.catalogue,
                simulateur.affiliations, statut, annee,
                brut_mensuel * MOIS_PAR_AN,
            ) / MOIS_PAR_AN

        return Echelle(
            moyen=salaire_moyen_annuel(macro, annee),
            smic=HEURES_SMIC_PAR_MOIS * macro.smic_horaire(annee),
            plafond=macro.plafond_securite_sociale(annee) / MOIS_PAR_AN,
            vers_brut=vers_brut if saisie.saisie_en_net else None,
            vers_net=vers_net,
            vers_brut_direct=vers_brut,
        )

    def simuler(self, saisie: Saisie) -> Comparaison:
        simulateur = self.simulateur(saisie.parametres(self.base))
        # Les motifs viennent des données, pas d'une liste écrite ici : le
        # moteur y lit ce que chaque période ouvre, et une saisie refusée doit
        # l'être sur la même table que celle qui calcule.
        motifs = charger_periodes_non_travaillees(simulateur.macro.racine)
        if saisie.releve_actif:
            return simulateur.simuler(self._carriere_relevee(
                simulateur, saisie, motifs))
        parcours = saisie.parcours(self.echelle(saisie))
        for metier in parcours:
            if metier.affiliation not in simulateur.affiliations:
                raise ErreurSaisie(
                    f"Statut d'affiliation inconnu : « {metier.affiliation} »."
                )
        carriere = simulateur.carriere_parcours(
            annee_naissance=saisie.naissance,
            sexe=saisie.sexe,
            metiers=parcours,
            mois_naissance=saisie.naissance_mois,
            age_liquidation=saisie.liquidation,
            profil_carriere=saisie.profil,
            interruptions=saisie.interruptions_de_carriere(motifs),
            nombre_enfants=saisie.enfants,
            part_primes=saisie.primes,
            identifiant="assuré",
        )
        _verifier_statuts_ouverts(simulateur.affiliations, carriere, parcours)
        return simulateur.simuler(carriere)

    def _carriere_relevee(self, simulateur: Simulateur, saisie: Saisie,
                          motifs) -> "Carriere":
        """La carrière telle que le relevé la donne, sans rien reconstituer.

        Aucune échelle des salaires n'intervient : le relevé est déjà en euros
        de chaque année, quand le formulaire paramétrique saisit un revenu
        d'aujourd'hui que le modèle promène ensuite le long du salaire moyen.
        C'est ce qui fait de ce chemin le plus exact — et le seul où l'euro
        n'est pas converti.
        """
        releve = saisie.releve_analyse(motifs)
        for ligne in releve:
            if ligne.affiliation not in simulateur.affiliations:
                raise ErreurSaisie(
                    f"Relevé, année {ligne.annee} : statut d'affiliation "
                    f"inconnu « {ligne.affiliation} »."
                )
        carriere = simulateur.carriere_releve(
            annee_naissance=saisie.naissance,
            sexe=saisie.sexe,
            releve=releve,
            mois_naissance=saisie.naissance_mois,
            age_liquidation=saisie.liquidation,
            nombre_enfants=saisie.enfants,
            part_primes=saisie.primes,
            identifiant="assuré",
        )
        _verifier_statuts_releve(simulateur.affiliations, carriere)
        return carriere


#: Titre de chaque page, dans l'ordre de la navigation.
TITRES = {
    "/": "Programme",
    "/simuler": "Simuler",
    "/trajectoire": "Trajectoire",
    "/cas-types": "Cas types",
    "/cout": "Coût",
    "/avantages": "Avantages",
    "/methode": "Méthode",
    "/donnees": "Données",
    "/partager": "Partager",
}


#: La description de chaque page, pour la balise ``<meta name="description">``
#: que le routeur d'``index.html`` réécrit à chaque rendu — comme il réécrit le
#: titre. Une phrase par page, qui dit ce qu'on y trouve. Le site tient dans
#: une seule page servie une fois : c'est le navigateur, et non le serveur, qui
#: pose cette description, ce qui vaut pour qui partage ou enregistre la page,
#: et moins pour un robot qui n'exécute pas le script.
DESCRIPTIONS = {
    "/": "Le programme du Parti libéral français pour les retraites : un régime "
         "unique en comptes notionnels, un taux de 18 % pour tous, une garantie "
         "vieillesse individualisée — et le simulateur qui le chiffre, carrière "
         "par carrière, dans votre navigateur.",
    "/simuler": "Votre carrière calculée de quatre façons : le système actuel, et "
                "les comptes notionnels appliqués depuis 1941 ou à partir de la "
                "bascule. Tout se calcule dans votre navigateur, rien n'est envoyé.",
    "/trajectoire": "Ce que chaque système aura versé, du départ à 105 ans : "
                    "le cumul, et non la pension d'un mois — c'est là que la "
                    "durée de la retraite entre dans le calcul.",
    "/cas-types": "Treize carrières types sur sept générations : ce que chaque "
                  "pension deviendrait, par rapport à aujourd'hui, sous la "
                  "proposition et sous quatre contrefactuels.",
    "/cout": "Ce que la retraite coûte, d'où vient l'argent, et ce qui manque, "
             "de 1959 à 2070 — et ce que chacun des quatre systèmes coûterait.",
    "/avantages": "Les trente-neuf avantages non contributifs du système actuel : "
                  "lesquels, depuis quand, et ce que le modèle sait en chiffrer.",
    "/methode": "Comment une pension en comptes notionnels se calcule, en trois "
                "opérations, et pourquoi la règle de revalorisation décide de "
                "presque tout.",
    "/donnees": "D'où viennent les chiffres du site, série par série et régime "
                "par régime, et ce qui a été recontrôlé contre sa source.",
    "/partager": "Les chiffres du programme au format des réseaux sociaux, "
                 "1200 × 675, en filigrane @pliberal : le plancher, le taux, "
                 "le déficit, et l'appel au simulateur.",
}


def rendre(contexte: Contexte, chemin: str,
           parametres: dict[str, str] | None = None) -> tuple[str, str]:
    """Contenu d'une page : ``(titre, corps HTML)``.

    Point d'entrée unique du rendu : le navigateur en remplace le contenu de
    ``<main>``. Les erreurs de saisie sont rendues dans la page, jamais levées :
    une adresse mal formée doit afficher un message, pas une trace d'exécution.

    ``/simuler`` et ``/trajectoire`` lisent ``parametres`` en entier : ce sont
    les deux pages que l'adresse paramètre carrière comprise, et elles portent
    le même formulaire. Les trois pages qui AGRÈGENT — Cas types, Coût,
    Avantages — n'en lisent que les RÈGLES, et se calculent sous elles. Toute
    adresse inconnue retombe sur l'accueil, comme le fait le routeur
    d'``index.html``.

    C'est ici, et nulle part ailleurs, que les réglages sont posés pour les
    liens de la page à venir : ``rendre`` est le point d'entrée unique du
    rendu, et les y poser à chaque appel — fût-ce à vide — garantit qu'aucune
    page n'hérite des réglages de la précédente.
    """
    parametres = parametres or {}
    refus = ""
    try:
        reglages = Saisie.modelisation(parametres)
    except ErreurSaisie as erreur:
        # Un réglage hors bornes ne doit pas emporter la page : elle se rend
        # sous les règles par défaut, précédée de la phrase qui dit pourquoi.
        reglages, refus = Saisie(), _erreur(str(erreur))
    g.poser_options(reglages.requete_modelisation())

    if chemin == "/trajectoire":
        return TITRES[chemin], refus + _page_trajectoire(contexte, parametres)
    if chemin == "/partager":
        return TITRES[chemin], _partager(contexte)
    if chemin in PAGES_AGREGEES:
        return TITRES[chemin], refus + _agregee(chemin, contexte, reglages)
    if chemin == "/methode":
        return TITRES[chemin], _methode(contexte)
    if chemin == "/donnees":
        return TITRES[chemin], _donnees(contexte)
    if chemin != "/simuler":
        return TITRES["/"], _programme(contexte)

    try:
        saisie = Saisie.depuis_requete(parametres)
    except ErreurSaisie as erreur:
        # Le formulaire repart de ses valeurs par défaut — c'est ce qui permet
        # de le réafficher quoi qu'ait porté l'adresse —, mais il garde l'unité
        # de saisie : sans cela, une faute de frappe sur l'année de naissance
        # renverrait en euros quelqu'un qui raisonnait en multiples, avec des
        # nombres de l'autre unité sous les yeux.
        unite = _parmi(parametres, "unite_revenu", UNITES_REVENU,
                       Saisie.unite_revenu)
        saisie = Saisie(demandee=False, unite_revenu=unite,
                        salaire=SALAIRE_DEFAUT[unite])
        return TITRES["/simuler"], (
            _erreur(str(erreur)) + _formulaire(saisie, contexte)
        )

    corps = _formulaire(saisie, contexte)
    if saisie.demandee:
        try:
            corps += _resultats(contexte, saisie)
        except (ErreurSaisie, DonneeInsuffisante, KeyError, ValueError) as erreur:
            corps += _erreur(str(erreur))
    return TITRES["/simuler"], corps


def _agregee(chemin: str, contexte: Contexte, reglages: Saisie) -> str:
    """Une page qui agrège, calculée sous les règles que l'adresse demande.

    Le corps de la page n'en sait rien : il reçoit un contexte DÉRIVÉ, dont
    ``base`` porte ces règles, et lit ``contexte.base``, ``contexte.cout()`` ou
    ``contexte.simulateur()`` comme il l'a toujours fait. C'est le contexte qui
    sait sous quelles règles on l'interroge, et non chacune des trente lignes
    qui l'interrogent.
    """
    return (
        _avertissement_reglages(reglages, chemin)
        + PAGES_AGREGEES[chemin](contexte.pour(reglages.parametres(contexte.base)))
        + _reglages(reglages, chemin)
    )

def _programme(contexte: Contexte) -> str:
    """Le programme du Parti libéral français pour les retraites.

    C'est l'accueil du site, et la seule page qui ne calcule rien pour elle-même :
    elle expose une proposition, et renvoie aux cinq autres pour les chiffres.
    Elle n'appelle donc ni ``contexte.cout()`` ni aucune simulation — deux
    secondes de calcul sur la première page ouverte seraient deux secondes de
    page blanche.

    ELLE SE LIT EN UNE MINUTE. C'est la contrainte, et elle tient à ce qu'est
    cette page : un programme politique, lu par quelqu'un qui n'a pas demandé à
    le lire. Quatre propositions, un tableau qui les oppose terme à terme au
    système actuel, et un lien pour vérifier. Le reste — pourquoi le système
    actuel ne va pas, en quoi c'est plus juste, comment on y va — est replié :
    présent pour qui veut, hors du chemin pour qui n'a que trente secondes.
    """
    base = contexte.base
    simulateur = contexte.simulateur()
    regimes = len(simulateur.catalogue)
    inventaire = len(charger_inventaire(base.racine_donnees))
    comptes = contexte.comptes()
    annee_solde = comptes.derniere_annee_observee
    taux = g.pourcentage(base.taux_cotisation_liberal, decimales=0)
    plancher = g.euros(base.garantie_vieillesse_mensuelle)

    differences = g.tableau(
        ["", "Aujourd'hui", "Avec notre programme"],
        [
            ["Ce qui ouvre un droit",
             f"des {g.terme('trimestres')}, et {regimes} barèmes différents",
             "une cotisation versée, et elle seule"],
            ["Ce qui fait le montant",
             f"vos {g.terme('25 meilleures années', 'salaire de référence')}, "
             "un taux, une durée",
             "votre compte, divisé par votre espérance de vie"],
            ["Partir un an plus tôt",
             f"une {g.terme('décote')}, dont le barème change à chaque réforme",
             "un an de cotisation en moins, un an de pension en plus"],
            ["Changer de métier",
             "changer de régime, et de règle de calcul",
             "rien : le compte est le même"],
            ["Savoir où vous en êtes",
             "un relevé en trimestres et en points",
             "un solde, en euros"],
            ["Tenir l'équilibre",
             "une réforme, tous les huit ans en moyenne",
             "un chiffre publié chaque année"],
            # La transmission est le seul point où les deux systèmes ne
            # promettent pas la même NATURE de droit : une pension s'éteint,
            # un capital se lègue. Le dire ici, et non dans un dépliant, parce
            # que c'est ce que la part capitalisée ajoute et qu'aucune autre
            # ligne du tableau ne porte.
            ["Si vous mourez avant la retraite",
             "vos cotisations restent au système",
             "le capital de la part capitalisée revient à vos héritiers"],
        ],
        ["", "texte", "texte"],
        titre="Le système actuel et notre programme, terme à terme",
        entete_de_ligne=True,
    )

    # Les dépliants sont bâtis à part : leur corps est lui-même un texte à
    # trous, et Python n'accepte pas un bloc entre triples guillemets à
    # l'intérieur d'un autre.
    depliant_actuel = g.depliant("Pourquoi le système actuel ne va pas", f"""
<p>La retraite française ? Un empilement de régimes, plus qu'un système.
Ce site en <a href="{g.lien("/donnees")}">recense {inventaire}</a>, actuels et
disparus, et en calcule {regimes}. Chacun a son âge de départ, son assiette, son
taux, sa durée exigée et son minimum.</p>
<ul class="serree">
  <li><strong>Illisible, d'abord.</strong> Le montant dépend de sept règles qui ne
  se lisent sur aucune fiche de paie. Personne, pas même les caisses, ne sait
  dire à un actif ce qu'il a acquis, autrement qu'en trimestres et en points.</li>
  <li><strong>Inégal, ensuite.</strong> À salaire et à durée égaux, la pension
  change selon le statut, et l'écart ne vient d'aucune différence de cotisation.
  <a href="{g.lien("/cas-types")}">Treize carrières le mesurent</a>.</li>
  <li><strong>Et personne ne le pilote.</strong> L'équilibre se rattrape par
  des réformes (1993, 2003, 2010, 2014, 2023), qui déplacent chaque fois
  l'effort sur ceux qui n'ont pas encore pris leur retraite.
  <a href="{g.lien("/cout")}">Le solde est ici</a>.</li>
</ul>""")

    depliant_calcul = g.depliant("Comment une pension serait calculée", f"""
<p>Un compte notionnel est un compte <em>virtuel</em> : aucun capital n'est
placé, les cotisations de l'année paient les pensions de l'année. C'est toujours
de la répartition. Ce qui change, c'est le calcul du droit.</p>
<ol>
  <li><strong>On inscrit</strong> chaque cotisation versée sur le compte, au
  premier euro et sans plafond.</li>
  <li><strong>On revalorise</strong> le compte chaque année, au rythme auquel
  progresse la masse des salaires, c'est-à-dire au rendement que la
  répartition peut servir sans changer son taux.</li>
  <li><strong>On divise</strong>, au départ en retraite, le solde du compte par
  le nombre d'années qu'il reste statistiquement à vivre, lu sur la table de
  votre propre génération. Le résultat est la pension.</li>
</ol>
<p>Un âge minimum subsiste, on ne part pas à trente ans. Mais il n'y a plus
d'âge du {g.terme("taux plein")}, ni {g.terme("décote")}, ni
{g.terme("surcote")} : partir plus tôt donne une pension
plus faible, partir plus tard une pension plus forte, dans le rapport exact de
ce que l'un et l'autre coûtent.
<a href="{g.lien("/methode")}">Le détail du calcul</a>.</p>""")

    depliant_verifier = g.depliant("Tout vérifier, page par page", f"""
<div class="note signee">
<p><strong>Pourquoi ce site.</strong> Nous avons choisi de publier un modèle
plutôt qu'un slogan. Une proposition de retraite se juge sur ce qu'elle verse
à chacun et sur ce qu'elle coûte à tous, et nous voulions que n'importe qui
puisse le vérifier sur sa propre carrière. Nos réserves sont écrites page par
page : le modèle reste un modèle, ses séries d'avant 1950 sont fragiles, et le
niveau des pensions notionnelles dépend d'un réglage annuel qu'il calcule sans
l'appliquer. Nous préférons un chiffre discutable à une promesse qu'on ne peut
pas discuter.</p>
<p class="discret">Le Parti libéral français, septembre 2026.</p>
</div>
<ul class="serree">
  <li><a href="{g.lien("/simuler")}">Simuler</a> : votre carrière, ou votre
  relevé collé tel quel, sous les quatre systèmes.</li>
  <li><a href="{g.lien("/cas-types")}">Cas types</a> : treize carrières sur sept
  générations.</li>
  <li><a href="{g.lien("/cout")}">Coût</a> : ce qui rentre, ce qui sort, et ce
  qui manque, de 1959 à 2070.</li>
  <li><a href="{g.lien("/methode")}">Méthode</a> : ce que le modèle calcule, et
  ce qu'il supprime.</li>
  <li><a href="{g.lien("/donnees")}">Données</a> : l'état de fiabilité de chaque
  série, source par source.</li>
</ul>
<p class="discret">Le modèle, les données et cette page sont publiés sous
licence libre : <a href="{g.DEPOT}">le dépôt</a>. Solde du système de retraite
en {annee_solde} :
{g.pourcentage(comptes.solde(annee_solde), signe=True, decimales=2)} du PIB.</p>""")

    # Les trois gestes du calcul. Ils étaient au format du texte courant, et se
    # lisaient comme une note de bas de page à côté du tableau qui leur fait
    # face — alors qu'ils pèsent autant. Chiffres de 50 px, texte de 24, un
    # filet entre chacun.
    gestes = "".join(
        f'<li><span class="rang">{rang}</span><span>{texte}</span></li>'
        for rang, texte in enumerate([
            "<strong>On inscrit</strong> chaque cotisation sur votre compte, "
            "au premier euro, sans plafond.",
            "<strong>On revalorise</strong> le compte chaque année, au rythme "
            "des salaires du pays.",
            "<strong>On divise</strong>, au départ, par les années qu'il vous "
            "reste à vivre en moyenne. C'est votre pension.",
        ], start=1)
    )

    tete = g.affiche(
        "Notre programme pour les retraites",
        'La seule retraite qui vous rend <span class="cle-texte">vraiment</span> '
        "ce que vous avez cotisé.",
        '<strong class="cle-texte">Un compte à votre nom, en euros.</strong> '
        "Chaque cotisation y est inscrite ; à la retraite, il devient votre "
        'pension. <strong class="cle-texte">Pas de trimestres, pas de barèmes, '
        "pas de surprise.</strong>",
    )

    return f"""
{tete}

{_simulateur_court(contexte)}

{_engagements(contexte)}

<div class="paire">
  <div>
    <p class="surtitre">Le calcul</p>
    <h2 style="margin-top:0">Comment ça marche, en trois gestes</h2>
    <ol class="gestes">{gestes}</ol>
    <p class="discret">Rien n'est placé : les cotisations de l'année paient
    les pensions de l'année. C'est toujours la {g.terme("répartition")}.</p>
  </div>
  <div class="encadre">
    <h2 class="serif" style="margin-top:0">Le plancher regarde chacun, pas le
    couple</h2>
    <p>Aujourd'hui, l'ASPA regarde les ressources du couple : à 300 € et
    1 500 € de pension, il ne reçoit rien. La garantie regarde chacun :</p>
    {_tableau_garantie()}
  </div>
</div>

<h2>Ce que cela change</h2>
{differences}
<p class="discret">C'est le système de la Suède, de l'Italie, de la Pologne et
de la Lettonie.</p>

<div class="creme">
<p class="surtitre">Vérifiez plutôt que de nous croire</p>
<h2 class="serif" style="margin:0">Tout est chiffré, sur des données publiques
et un modèle ouvert.</h2>
<p class="actions"><a class="bouton" href="{g.lien("/simuler")}">Simuler ma
retraite</a><a href="{g.lien("/cout")}">Ce que ça coûte, et qui paie</a></p>
</div>

<h2>Pour aller plus loin</h2>

{depliant_actuel}

{depliant_calcul}

{_programme_justice(contexte)}
{_programme_garantie(contexte)}
{_programme_capitalisation(contexte)}
{_programme_transition(contexte)}

{depliant_verifier}
"""


def _programme_justice(contexte: Contexte) -> str:
    """En quoi le compte notionnel est plus juste, entre métiers et entre âges.

    Deux questions qu'on pose toujours, et dont les réponses tiennent chacune en
    quatre lignes. Elles sont repliées ensemble parce qu'elles se répondent :
    l'une regarde deux carrières de la même génération, l'autre deux générations
    de la même carrière.
    """
    regimes = len(contexte.simulateur().catalogue)
    return g.depliant("En quoi ce serait plus juste", f"""
<h4>Entre deux personnes</h4>
<ul class="serree">
  <li><strong>À cotisation égale, pension égale.</strong> Un fonctionnaire, un
  artisan et un salarié qui versent la même somme acquièrent le même droit. Les
  {regimes} barèmes disparaissent, et avec eux les comparaisons que personne ne
  sait trancher.</li>
  <li><strong>Une carrière hachée n'est plus punie deux fois.</strong>
  Aujourd'hui, une interruption fait perdre des trimestres, donc le taux plein,
  donc une décote qui s'applique à <em>toute</em> la pension. Avec un compte,
  elle fait perdre les cotisations de ces années-là, et rien de plus.</li>
  <li><strong>La solidarité devient visible.</strong> Ce que la collectivité
  ajoute ne se cache plus dans un barème : c'est une allocation votée, chiffrée
  et financée par l'impôt.</li>
</ul>

<h4>Entre deux générations</h4>
<p>C'est ce que le système actuel tient le plus mal. Une pension y est promise
par une règle et payée par la génération suivante ; quand le compte n'y est pas,
la règle change, toujours au détriment de ceux qui n'ont pas encore
liquidé. Ce qu'un euro cotisé rapporte dépend ainsi de l'année de naissance,
sans que personne ne l'ait voté.</p>
<ul class="serree">
  <li><strong>Le rendement est le même pour tous</strong> : la croissance de la
  masse des salaires, c'est-à-dire exactement ce que la répartition peut payer à
  taux inchangé.</li>
  <li><strong>Chacun est divisé par sa propre espérance de vie.</strong> Vivre
  plus longtemps étale le même capital sur plus d'années, au lieu d'envoyer la
  facture à la génération d'après.</li>
  <li><strong>Le taux ne bouge pas.</strong> Fixé une fois, il retire aux actifs
  d'aujourd'hui le moyen de s'accorder des droits que les actifs de demain
  devraient financer.</li>
  <li><strong>L'écart se solde chaque année</strong>, au lieu de s'accumuler en
  silence jusqu'à la réforme suivante.</li>
</ul>""")


#: Le taux de cotisation retraite d'aujourd'hui, parts salariale et patronale
#: additionnées — la base sur laquelle les 18 % de la proposition se comparent.
#: Ce n'est pas une moyenne inter-régimes : c'est le total du CAS LE PLUS
#: COURANT, un salarié non cadre du privé sous le plafond, décomposé ainsi :
#:
#:     retraite de base plafonnée       6,90 %  +  8,55 %  = 15,45 %
#:     retraite de base déplafonnée     0,40 %  +  2,11 %  =  2,51 %
#:     Agirc-Arrco tranche 1            3,15 %  +  4,72 %  =  7,87 %
#:     CEG                              0,86 %  +  1,29 %  =  2,15 %
#:     -------------------------------------------------------------
#:     total                           11,31 %  + 16,67 %  = 27,98 %
#:
#: Les pages arrondissent à 28 %, 11,3 % et 16,7 %. Tout autre statut cotise
#: autrement, et c'est dit partout où le chiffre paraît : « pour un salarié du
#: privé », jamais « en moyenne ».
TAUX_ACTUEL_SALARIAL = 0.1131
TAUX_ACTUEL_PATRONAL = 0.1667
TAUX_ACTUEL_TOTAL = TAUX_ACTUEL_SALARIAL + TAUX_ACTUEL_PATRONAL


def _engagements(contexte: Contexte) -> str:
    """Les quatre engagements du programme, chiffrés, numérotés 01 à 04.

    C'est la section qui porte le message, et elle a mis trois états à le
    porter. D'abord quatre chiffres nus, qu'on lisait comme des statistiques
    orphelines ; puis les mêmes sous un titre, qui redisait ce que le titre de
    la page disait déjà ; enfin ceux-ci — numérotés, sur trois niveaux nets.

    Les trois niveaux sont le fond de l'affaire. Le CHIFFRE en or attire l'œil ;
    la PROMESSE en serif, en crème plein contraste, porte le message, et c'est
    elle qui se perdait quand les cartes n'avaient que deux niveaux ; le DÉTAIL
    technique, plus discret mais à 18 px — pas 15 —, répond à celui qui veut
    savoir comment.

    Dans chaque carte, un ou deux passages en or, jamais plus : au-delà,
    l'emphase ne désigne plus rien. Ils sont doublés d'un demi-gras, pour
    survivre en niveaux de gris comme en daltonisme.

    Les quatre valeurs sont celles du MODÈLE, et non des nombres écrits ici :
    changer ``garantie_vieillesse_mensuelle`` change la page.
    """
    base = contexte.base
    taux = g.pourcentage(base.taux_cotisation_liberal, decimales=0)
    capitalise = g.pourcentage(base.taux_capitalisation_obligatoire, decimales=0)
    garantie = base.garantie_vieillesse_mensuelle
    isolement = base.allocation_isolement_mensuelle
    # Seul : la garantie plus l'allocation d'isolement. En couple : la garantie
    # pour chacun, et rien de plus — l'isolement ne se verse qu'à qui vit seul.
    # « Une garantie de 800 € » était trompeur : c'est le plancher par personne,
    # pas ce que touche quelqu'un.
    seul = g.euros(garantie + isolement)
    couple = g.euros(2 * garantie)

    cartes = [
        (seul,
         f"par mois au minimum, seul.<br>"
         f'<strong class="cle-texte">{couple}</strong> pour un couple.',
         f'<strong class="cle-texte">{g.euros(garantie)} par personne</strong>, '
         f'plus <strong class="cle-texte">{g.euros(isolement)} d\'allocation '
         f"d'isolement</strong> pour qui vit seul. Payés par l'impôt, dès "
         f"{MinimumVieillesse.AGE_OUVERTURE} ans."),
        (f"{taux} + {capitalise}",
         "de cotisation : la répartition, "
         f'<strong class="cle-texte">plus un capital à votre nom</strong>.',
         f"{taux} au compte de retraite — part salariale et patronale "
         f"additionnées, contre {g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)} "
         f"aujourd'hui ({g.pourcentage(TAUX_ACTUEL_SALARIAL)} + "
         f"{g.pourcentage(TAUX_ACTUEL_PATRONAL)} pour un salarié du privé), "
         f'et <strong class="cle-texte">le même taux pour tout le monde</strong>. '
         f"Par-dessus, {capitalise} placés sur des titres sans risque, "
         '<strong class="cle-texte">qui vous appartiennent</strong> et se '
         "transmettent."),
        ("1 compte",
         '<strong class="cle-texte">en euros</strong>, lisible par tous.',
         "Un compte personnel de retraite : vous voyez "
         '<strong class="cle-texte">votre solde comme sur un relevé '
         "bancaire</strong>."),
        ("100 %",
         "de ce que vous avez cotisé "
         '<strong class="cle-texte">vous revient</strong>.',
         "Partir plus tôt donne moins, plus tard donne plus — "
         '<strong class="cle-texte">dans le rapport exact de ce que ça '
         "coûte</strong>."),
    ]
    corps = "".join(
        f'<div class="engagement"><div class="rang">{rang:02d}</div>'
        f'<div class="chiffre">{chiffre}</div>'
        f'<div class="promesse">{promesse}</div>'
        f'<div class="detail">{detail}</div></div>'
        for rang, (chiffre, promesse, detail) in enumerate(cartes, start=1)
    )
    return (
        '<section class="engagements" aria-label="Nos quatre engagements">'
        f'<div class="grille">{corps}</div></section>'
    )


def _simulateur_court(contexte: Contexte, vers: str = "/simuler") -> str:
    """Le formulaire court de l'accueil : quatre champs, et « Calculer ».

    Le site est un simulateur, et rien du premier écran ne le disait : le mot
    n'était que dans un onglet, et le seul bouton arrivait au troisième écran —
    au cinquième sur un téléphone. Il est maintenant SOUS LE TITRE, sur le
    panneau crème, avant même les engagements : la preuve est mise à hauteur de
    la promesse.

    Quatre champs et non douze. Ce sont ceux qui suffisent à une carrière
    ordinaire ; la page Simuler porte le formulaire entier, et le lien y mène
    pour une carrière hachée. Les noms des champs sont exactement ceux du grand
    formulaire (``naissance``, ``debut``, ``statut``, ``liquidation``), parce
    que c'est la même adresse qui les reçoit — et que l'écoute de soumission
    d'``index.html`` lit l'``action``, sans rien savoir du formulaire.
    """
    saisie = Saisie()
    affiliations = contexte.simulateur().affiliations
    champs = "".join([
        g.champ_date("naissance", "Date de naissance", saisie.naissance_iso,
                     "seul le mois compte", saisie.naissance_en_clair,
                     min=f"{NAISSANCE_MINIMALE}-01-01",
                     max=f"{NAISSANCE_MAXIMALE}-12-31",
                     autocomplete="bday"),
        g.champ_date("debut", "Début de carrière", saisie.jour_de(saisie.debut),
                     "le premier mois cotisé", saisie.calcul_de(saisie.debut),
                     min=saisie.jour_de(AGE_DEBUT_MINIMAL),
                     max=saisie.jour_de(AGE_DEBUT_MAXIMAL)),
        g.liste("statut", "Statut",
                _options_statuts(affiliations, saisie.date_de(saisie.debut)),
                saisie.statut),
        g.champ_date("liquidation", "Départ souhaité",
                     saisie.jour_de(saisie.liquidation), "effectif, ou souhaité",
                     saisie.calcul_de(saisie.liquidation),
                     min=saisie.jour_de(AGE_LIQUIDATION_MINIMAL),
                     max=saisie.jour_de(AGE_LIQUIDATION_MAXIMAL)),
    ])
    return f"""
<form class="creme simulateur-court" method="get" action="{g.route(vers)}">
  <div class="tete">
    <h2 class="serif">Et vous, ça donne combien&nbsp;?</h2>
    <span class="etiquette">Le simulateur</span>
  </div>
  <div class="grille">{champs}
    <button type="submit">Calculer →</button>
  </div>
  <p class="discret" style="margin:0.9rem 0 0">Quatre montants côte à côte :
  les règles d'aujourd'hui, et les nôtres. Tout se calcule dans votre
  navigateur, rien n'est envoyé.</p>
</form>"""


def _tableau_garantie() -> str:
    """Ce que le plancher individualisé change, en cinq lignes.

    Le tableau fait le travail que trois paragraphes faisaient mal. Quatre
    couples, deux colonnes : ce que l'ASPA sert aujourd'hui, ce que la garantie
    servirait. La ligne « 300 € et 1 500 € » dit tout — c'est l'argument le
    plus immédiatement parlant du site, et il est en haut de l'accueil, non
    plus dans un dépliant après trois tableaux denses.
    """
    return g.tableau(
        ["Pensions des deux personnes", "Aujourd'hui (ASPA)", "Avec la garantie"],
        [
            ["300 € et 300 €", "1 000 €", "1 000 €"],
            ["300 € et 1 500 €", "0 €", "500 €"],
            ["900 € et 900 €", "0 €", "0 €"],
            ["300 € et 5 000 €", "0 €", "500 €"],
            ["Personne seule, 300 €", "750 €", "750 €"],
        ],
        ["", "nombre", "nombre"],
        titre="Ce que le plancher individualisé change, par mois",
        entete_de_ligne=True,
    )


def _programme_garantie(contexte: Contexte) -> str:
    """Le plancher, et le seul changement qui compte : il regarde une personne.

    Le tableau, lui, est en haut de page (:func:`_tableau_garantie`) : ce
    dépliant dit ce qu'il remplace et comment il est financé.
    """
    base = contexte.base
    plancher_seul = (base.garantie_vieillesse_mensuelle
                     + base.allocation_isolement_mensuelle)
    return g.depliant("Le plancher, et ce qu'il change pour les petites pensions", f"""
<p>Le système actuel superpose l'ASPA, le minimum contributif, le minimum
garanti de la fonction publique, l'assurance vieillesse des parents au foyer,
les majorations de durée et la majoration pour trois enfants. Chacun a son
barème, son âge et sa condition. Ensemble, ils rendent toute pension modeste
impossible à prévoir.</p>
<p>Nous les remplaçons par <strong>une seule prestation</strong> : différentielle
comme l'ASPA, servie à partir de 65 ans comme elle, financée par l'impôt. Mais
<strong>individualisée</strong>. Chacun est comparé à son propre plancher, sans
que la pension du conjoint entre dans le calcul.</p>
<ul class="serree">
  <li>{g.euros(base.garantie_vieillesse_mensuelle)} par mois et par personne ;</li>
  <li>{g.euros(base.allocation_isolement_mensuelle)} de plus pour qui vit seul,
  soit {g.euros(plancher_seul)} ;</li>
  <li>en euros de {base.annee_euros_garantie_vieillesse}, revalorisés sur les
  prix.</li>
</ul>
<p>Le tableau du haut de page le montre : l'ASPA regarde les ressources du
foyer, et à 300 € et 1 500 € le couple dépasse son plafond et ne reçoit rien.
La garantie regarde chacun, et sert 500 € au premier. C'est ce changement
d'assiette, plus que le montant, qui fait la différence pour les femmes aux
pensions les plus faibles.
<a href="{g.lien("/cout")}">Ce qu'elle coûterait</a> est calculé sur la
distribution réelle des pensions, non sur des cas types.</p>""")



def _programme_capitalisation(contexte: Contexte) -> str:
    """La part capitalisée, expliquée à qui n'a pas ouvert la page Méthode.

    Trois questions, et trois seulement : ce que c'est, ce que cela change pour
    celui qui cotise, et ce que cela ne fait pas. Le détail — la courbe des
    taux, l'échelle de maturités, le barème de frais — est sur la page Méthode ;
    ici, on répond à « qu'est-ce que ça me fait ? ».
    """
    base = contexte.base
    taux = g.pourcentage(base.taux_capitalisation_obligatoire, decimales=0)
    repartition_ = g.pourcentage(base.taux_cotisation_liberal, decimales=0)
    return g.depliant(
        f"La part capitalisée : {taux} qui vous appartiennent",
        f"""
<p>À compter de {base.annee_debut_capitalisation}, {taux} de votre rémunération
sont prélevés <strong>en plus</strong> des {repartition_} de la répartition, et
placés à votre nom sur des titres sans risque. Ce capital ne passe pas par le
compte notionnel : il vous revient, dans un plan d'épargne retraite, l'enveloppe
qui existe déjà et que des millions de Français détiennent. Les années d'avant
ne changent pas :
elles gardent les taux qui étaient les leurs, et qui a déjà liquidé ne cotise
rien.</p>
<ul class="serree">
  <li><strong>Il vous appartient.</strong> Si vous mourez avant d'avoir liquidé,
  le capital revient à vos héritiers, intégralement. Une pension de répartition,
  elle, s'éteint avec vous sans rien laisser.</li>
  <li><strong>Il ne sort qu'à la retraite.</strong> Pas d'achat de résidence
  principale, pas de sortie anticipée : la cotisation est obligatoire, et
  l'argent n'en sort qu'en rente viagère, ou par l'héritage.</li>
  <li><strong>Il est placé sans risque.</strong> Des titres d'État parmi les
  mieux notés de la zone euro, portés jusqu'à leur échéance : longue tant que la
  retraite est loin, courte à l'approche du départ. Aucune action, aucun pari.</li>
  <li><strong>Il ne remplace rien.</strong> La retraite par répartition reste ce
  qu'elle est, et le compte notionnel la calcule sans regarder ce capital. Les
  deux montants sont affichés côte à côte, jamais confondus.</li>
</ul>
<p>Ce que cela coûte est chiffré : l'enveloppe prélève des frais, et le
simulateur les montre euro par euro, comme il montre le rendement qui reste. La
page <a href="{g.lien("/methode/")}#capitalisation">Méthode</a> dit à quels
taux l'argent est placé, d'où ils viennent et ce qu'ils supposent.</p>""",
    )


def _programme_transition(contexte: Contexte) -> str:
    """Les six étapes, et l'année où chacune produit son effet."""
    base = contexte.base
    fusionne = contexte.simulateur().regime_fusionne
    etapes = g.tableau(
        ["Étape", "Ce qu'elle fait"],
        [
            ["1. Le compte unique",
             "Ce que chacun a cotisé est rassemblé sur un compte unique et "
             "converti en euros. Les régimes continuent de liquider selon leurs "
             "règles : rien ne change encore pour personne, mais le relevé de "
             "carrière devient lisible. Les données existent déjà."],
            [f"2. La bascule ({base.annee_bascule})",
             "Les droits déjà acquis sont figés, réduits à leur part "
             "contributive et convertis en capital. Les pensions déjà versées "
             "ne sont pas touchées. Les régimes fusionnent en un seul."],
            ["3. Le taux unique",
             f"Toute cotisation postérieure à la bascule est prélevée à "
             f"{g.pourcentage(base.taux_cotisation_liberal, decimales=0)} de la "
             "rémunération, parts salariale et patronale additionnées, quel que "
             "soit le statut. Les taux qui dépassaient ce niveau baissent, ceux "
             "qui restaient en deçà montent."],
            ["4. La garantie vieillesse",
             "Elle remplace l'ASPA, le minimum contributif et le minimum "
             "garanti le jour de la bascule, et passe au budget de l'État. "
             "Aucun minimum ne se calcule plus dans le barème de la pension."],
            ["5. Le pilotage",
             "Le chiffre qui ramène l'année à zéro est publié et appliqué "
             "chaque année. C'est ce qui remplace les réformes."],
            ["6. Le régime de croisière",
             "La dernière pension calculée en partie sous l'ancien barème est "
             "versée une quarantaine d'années après la bascule. D'ici là, les "
             "deux systèmes coexistent dans chaque pension."],
        ],
        ["", "texte"],
        titre="Du système actuel au régime unique",
        entete_de_ligne=True,
    )
    return g.depliant("Comment on y va, étape par étape", f"""
<p>La bascule fige ce qui est acquis.</p>
{etapes}
<p>Après la bascule, un seul régime : départ possible à
{_age(fusionne.age_ouverture)}, assiette déplafonnée, même taux pour tous.</p>""")


def _verifier_statuts_ouverts(affiliations: Affiliations, carriere,
                              parcours: list[Metier]) -> None:
    """Un statut ne se déclare qu'aux dates où son régime recrutait.

    Un jeune d'aujourd'hui ne peut pas se déclarer mineur : le régime des
    mines est fermé aux recrutés depuis septembre 2010. Le routage le savait
    déjà — il envoyait ce mineur-là au régime général, en silence, et la page
    affichait « Mineur » au-dessus d'une pension de salarié du privé. Le refus
    dit la date, et le statut de droit commun qui porte le même calcul.

    La date opposée est celle de l'ENTRÉE dans le statut, au mois près,
    telle que le parcours l'a datée : un agent entré à la RATP en octobre
    2022 n'y a sa première ligne qu'en 2023, et n'est pas recruté après la
    fermeture pour autant.
    """
    for rang, metier in enumerate(parcours, start=1):
        ferme = _statut_ferme(affiliations, carriere, metier.affiliation)
        if ferme is None:
            continue
        fermeture, entree = ferme
        raise _refus(rang, _phrase_statut_ferme(
            affiliations, metier.affiliation, fermeture,
            f"ce métier commence en {entree}",
        ))


def _verifier_statuts_releve(affiliations: Affiliations, carriere) -> None:
    """Le même refus, opposé à un relevé de carrière.

    Le relevé ne compte pas de métiers : il porte des ANNÉES, dont chacune
    nomme son statut. La date opposée à la fermeture est donc la première
    année déclarée sous ce statut — janvier, faute d'un mois que le relevé ne
    donne pas —, et la phrase le dit plutôt que de parler d'un « métier n° 2 »
    qui n'existe nulle part sur la page.
    """
    for code in carriere.affiliations_utilisees():
        ferme = _statut_ferme(affiliations, carriere, code)
        if ferme is None:
            continue
        fermeture, entree = ferme
        raise ErreurSaisie(_phrase_statut_ferme(
            affiliations, code, fermeture,
            f"la première année déclarée sous ce statut est {entree.annee}",
        ))


def _statut_ferme(affiliations: Affiliations, carriere,
                  code: str) -> tuple[DateMois, DateMois] | None:
    """``(fermeture, entrée)`` si ce statut se déclare trop tard, sinon ``None``."""
    fermeture = affiliations.fermeture_entrants(code)
    if fermeture is None:
        return None
    entree = carriere.date_entree(code)
    if entree is None or entree.rang < fermeture.rang:
        return None
    return fermeture, entree


def _phrase_statut_ferme(affiliations: Affiliations, code: str,
                         fermeture: DateMois, quand: str) -> str:
    """Le refus, écrit une fois pour les deux formes de saisie.

    ``quand`` est la seule chose qui les sépare : un métier commence à un mois,
    une ligne de relevé n'a qu'une année. Écrire les deux phrases en entier les
    laisserait diverger — c'est la raison d'être de ``_refus`` juste au-dessus.
    """
    releve = affiliations.releve_par(code)
    return (
        f"Le statut « {affiliations.libelle(code)} » est fermé aux recrutés "
        f"depuis {formater_borne(fermeture)} ; {quand}. Depuis cette date, "
        f"il relève des mêmes régimes que « {affiliations.libelle(releve)} » : "
        "choisir ce statut."
    )


def _libelle_date(affiliations: Affiliations, code: str) -> str:
    """Le libellé d'un statut, et les dates entre lesquelles il se déclare.

    « (depuis 1977) » pour un régime né après 1930, l'année où le modèle
    commence ; « (recrutés avant septembre 2010) » pour un régime fermé.
    """
    libelle = affiliations.libelle(code)
    ouverture = affiliations.ouverture(code)
    fermeture = affiliations.fermeture_entrants(code)
    precisions = []
    if ouverture > ANNEE_MODELE:
        precisions.append(f"depuis {ouverture}")
    if fermeture is not None:
        precisions.append(f"recrutés avant {formater_borne(fermeture)}")
    if not precisions:
        return libelle
    return f"{libelle} ({', '.join(precisions)})"


def _options_statuts(affiliations: Affiliations, entree: DateMois | None,
                     sans_emploi: bool = False) -> list[tuple]:
    """Les statuts du menu, ceux que la date d'entrée ferme désactivés.

    ``sans_emploi`` ajoute, à la suite des métiers, les motifs de
    :data:`SANS_EMPLOI` : ce sont les lignes qui ne décrivent pas un emploi.
    La première ligne ne les reçoit pas — une carrière commence quand on
    commence à travailler —, et aucune date ne les ferme : on peut être au
    chômage en 1950 comme en 2050.

    ``entree`` est le mois où le métier commence ; sans lui — la ligne vide du
    formulaire —, tout est proposé. Chaque option fermée porte sa date en
    ``data-fermeture`` : c'est ce que la page lit, dans le navigateur, pour
    refaire ce tri quand l'année de naissance ou l'âge de début change sous
    ses yeux, sans attendre le calcul.

    Les statuts sont rendus PAR FAMILLE — un ``<optgroup>`` par valeur de
    :data:`FAMILLES_STATUT`, dans l'ordre de cette table —, parce que
    soixante-deux options à la file ne se parcourent pas : qui cherche
    « SNCF » ou « artisan » devait tout lire. Dans un groupe, l'ordre reste
    celui des codes. Les périodes sans emploi forment le dernier groupe.
    """
    par_famille: dict[str, list[tuple]] = {famille: [] for famille in FAMILLES_STATUT}
    for code in affiliations.codes:
        # « Sans activité professionnelle » est une affiliation, mais c'est la
        # même chose que le motif du même nom : elle rejoint le groupe plutôt
        # que d'y figurer deux fois, sous deux libellés, pour le même résultat.
        if sans_emploi and code in CODES_SANS_EMPLOI:
            continue
        fermeture = affiliations.fermeture_entrants(code)
        disponible = (entree is None or fermeture is None
                      or entree.rang < fermeture.rang)
        attributs = ({} if fermeture is None
                     else {"data-fermeture": f"{fermeture.annee}-{fermeture.mois:02d}"})
        par_famille[affiliations.famille(code)].append(
            (code, _libelle_date(affiliations, code), disponible, attributs)
        )
    groupes = [(libelle, par_famille[famille])
               for famille, libelle in FAMILLES_STATUT.items()
               if par_famille[famille]]
    if sans_emploi:
        groupes.append(("Sans emploi", [(code, libelle) for code, libelle in SANS_EMPLOI]))
    return groupes


def statuts(contexte: Contexte) -> list[dict]:
    affiliations = contexte.simulateur().affiliations
    return [{
        "code": code,
        "libelle": affiliations.libelle(code),
        "ouverture": affiliations.ouverture(code),
        "fermeture_entrants": (
            None if affiliations.fermeture_entrants(code) is None
            else f"{affiliations.fermeture_entrants(code).annee}-"
                 f"{affiliations.fermeture_entrants(code).mois:02d}"
        ),
        "releve_par": affiliations.releve_par(code),
    } for code in affiliations.codes]


# -- fragments ---------------------------------------------------------------


def _erreur(message: str) -> str:
    return f'<div class="erreur"><strong>Saisie refusée.</strong> {escape(message)}</div>'


def _bulle_du_titre(saisie: Saisie) -> str:
    """Ce que le simulateur calcule, sous le titre du formulaire.

    C'était un chapeau, un encadré et un dépliant — quatre-vingt-dix mots avant
    le premier champ. Or on vient ici remplir des champs : tout ce qui s'y
    interpose est du temps pris à quelqu'un qui a déjà décidé, et rien de ce qui
    était écrit là n'est nécessaire pour remplir le formulaire. Ce qui compte
    n'est pas perdu pour autant — il s'ouvre sous le point d'interrogation, et
    les réserves qui pèsent sur un chiffre sont répétées à côté de ce chiffre,
    là où elles servent.

    Les années citées viennent de la saisie, jamais d'une constante écrite dans
    le texte — le chapeau annonçait « à compter de 2026 » quand la bascule
    saisie partait de 2035.
    """
    return g.bulle(
        "Ce que ce formulaire calcule",
        "Votre carrière, calculée de quatre façons : le système actuel, et les "
        f'<a href="{g.lien("/")}">comptes notionnels</a> — appliqués depuis '
        f"1941, ou à partir de {saisie.bascule}. Tout se calcule dans votre "
        "navigateur : rien n'est envoyé nulle part.",
    )


def _bulle_des_periodes() -> str:
    """Ce qu'une ligne de carrière peut décrire, sous le titre de la section.

    Deux paragraphes tenaient là ce que la section montre déjà : des lignes
    qu'on remplit. Ce qui ne se voit pas — qu'une ligne peut n'être pas un
    emploi, et que la dernière dit alors quand l'activité s'arrête — est la
    seule chose qui méritait d'être écrite, et elle est ici.
    """
    return g.bulle(
        "Ce qu'une période peut être",
        "Un métier : chaque changement fait passer d'un régime à un autre, donc "
        "d'un taux et d'un barème à un autre. Ou une période <strong>sans "
        "emploi</strong> — chômage, maladie, élever un enfant, rien du tout —, "
        "qui ne demande pas de revenu : c'est celui d'avant qui sert de "
        "référence là où le droit ouvre malgré tout des points. La dernière "
        "ligne dit donc aussi quand l'activité s'arrête, si elle s'arrête avant "
        "le départ : sans elle, le calcul suppose qu'on a travaillé jusqu'au "
        "dernier mois.",
    )


#: Le nom de chaque réglage en français, et la liste où lire le libellé de sa
#: valeur quand elle en a un. Elle sert à DIRE ce que la page a fait : « la
#: page a été calculée sous d'autres règles » n'apprend rien si l'on ne dit pas
#: lesquelles.
LIBELLES_MODELISATION = {
    "indexation": ("règle d'indexation", INDEXATIONS),
    "lissage": ("lissage de l'indexation, en années", None),
    "age_reference": ("âge de référence", AGES_REFERENCE),
    "table": ("table de conversion", TABLES),
    "conversion_acquis": ("âge de conversion des droits acquis", CONVERSIONS_ACQUIS),
    "part_cotisation": ("part de la cotisation portée au compte", PARTS_COTISATION),
    "foyer": ("situation de foyer", SITUATIONS_FOYER),
    "projection": ("scénario macroéconomique", PROJECTIONS),
    "bascule": ("année de bascule", None),
    "euros": ("euros constants de", None),
}


def _reglages_en_clair(saisie: Saisie) -> str:
    """Ce que le lecteur a changé, écrit en toutes lettres."""
    defauts = Saisie()
    dits = []
    for cle, (nom, choix) in LIBELLES_MODELISATION.items():
        valeur = getattr(saisie, cle)
        if valeur == getattr(defauts, cle):
            continue
        libelle = str(valeur)
        if choix is not None:
            libelle = next((intitule for code, intitule in choix
                            if code == valeur), libelle)
        dits.append(f"{nom} : {libelle}")
    return " ; ".join(dits)


def _avertissement_reglages(saisie: Saisie, chemin: str) -> str:
    """Un encadré, en tête de page, dès que les chiffres ne sont plus ceux du défaut.

    Sans lui, une adresse partagée afficherait des chiffres qui ne sont pas
    ceux du site sans que rien ne le dise — exactement la faute que cette page
    reproche au reste du débat public. Il ne paraît que si quelque chose a été
    changé : tant que tout est au défaut, la page est celle d'avant, au
    caractère près.
    """
    if not saisie.requete_modelisation():
        return ""
    return f"""<div class="encadre">
<p><strong>Ces chiffres ne sont pas ceux des réglages par défaut.</strong>
La page a été calculée sous les règles que vous avez choisies —
{escape(_reglages_en_clair(saisie))}. Tous les liens du site les emportent
tant que vous ne les remettez pas :
<a href="{g.route(chemin)}">revenir aux réglages par défaut</a>.</p>
</div>"""


def _reglages(saisie: Saisie, chemin: str) -> str:
    """Les règles du calcul, et de quoi les changer sans quitter la page.

    C'est le même jeu de champs que les options du simulateur, et c'est le même
    code qui les écrit : une page qui agrège et une page qui simule ne peuvent
    pas proposer deux jeux de règles différents.

    Le formulaire vise la ROUTE et non le lien — voir :func:`gabarit.route` :
    il écrit lui-même sa requête, à partir de ses champs.
    """
    defauts = Saisie()
    # Les deux réglages sans champ voyagent cachés : le formulaire les perdrait,
    # et une adresse qui les portait se retrouverait silencieusement ramenée au
    # défaut au premier « Recalculer ».
    caches = "".join(
        g.cache(cle, str(getattr(saisie, cle)))
        for cle in ("age_reference", "conversion_acquis")
        if getattr(saisie, cle) != getattr(defauts, cle)
    )
    change = bool(saisie.requete_modelisation())
    return f"""
<details class="options reglages"{' open' if change else ''}>
  {g.sommaire("Les règles du calcul (indexation, projection, bascule…)")}
  <p class="discret">Cette page croise des carrières types avec des
  générations : elle ne calcule aucune carrière saisie. Mais elle obéit aux
  mêmes règles que le simulateur, et ces règles se changent ici. La page est
  recalculée, et l'adresse les emporte vers les autres pages.</p>
  <form class="carte" method="get" action="{g.route(chemin)}">
    {caches}
    <div class="grille">{_champs_modelisation(saisie)}</div>
    <p style="margin-top:1.4rem"><button type="submit">Recalculer cette page</button></p>
  </form>
</details>
"""


def _champs_modelisation(saisie: Saisie) -> str:
    """Les huit réglages qui décrivent les RÈGLES, et non la carrière.

    Ils sont écrits ici une fois, et servent deux fois : dans les options du
    simulateur, et dans le bloc de réglages des trois pages agrégées. Les
    écrire deux fois aurait suffi à les faire diverger — un libellé ici, une
    borne là —, et deux pages du même site auraient alors proposé deux jeux de
    règles qui n'en sont qu'un.

    Les deux réglages restants — l'âge de référence et l'âge de conversion des
    droits acquis — n'ont jamais eu de champ : ils ne se règlent que par
    l'adresse. Le bloc de réglages les emporte en champs cachés pour ne pas les
    perdre au passage du formulaire.
    """
    return "".join([
        g.liste("indexation", "Règle d'indexation", INDEXATIONS, saisie.indexation,
                "revalorisation des comptes et des pensions",
                complement=g.GLOSSAIRE["indexation"]),
        g.champ("lissage", "Lissage de l'indexation", saisie.lissage,
                "en années : 1 = aucun",
                complement="Une moyenne glissante appliquée à la règle "
                "choisie, quelle qu'elle soit : 5 ans, c'est la fenêtre "
                "italienne.",
                type_="number", min="1", max=str(LISSAGE_MAXIMUM), step="1"),
        g.liste("table", "Table de conversion", TABLES, saisie.table,
                complement=g.GLOSSAIRE["table de conversion"]),
        g.liste("part_cotisation", "Part de la cotisation portée au compte",
                PARTS_COTISATION, saisie.part_cotisation,
                "salariale seule, ou salariale et patronale",
                complement=g.GLOSSAIRE["part patronale"]),
        g.liste("foyer", "Situation de foyer",
                SITUATIONS_FOYER, saisie.foyer,
                "la proposition libérale seulement",
                complement="Elle ne joue que sur l'allocation d'isolement de "
                "la garantie vieillesse : 1 050 € par mois pour qui vit seul, "
                "800 € par personne à deux."),
        g.liste("projection", "Scénario macroéconomique", PROJECTIONS, saisie.projection,
                "au-delà de la dernière observation"),
        g.champ("bascule", "Année de bascule", saisie.bascule,
                "passage au régime unique", type_="number",
                min=str(ANNEE_MINIMALE), max=str(ANNEE_MAXIMALE)),
        g.champ("euros", "Euros constants de", saisie.euros,
                "l'année dont les montants prennent le pouvoir d'achat",
                type_="number", min=str(ANNEE_MINIMALE), max=str(ANNEE_MAXIMALE))
    ])


def _formulaire(saisie: Saisie, contexte: Contexte) -> str:
    affiliations = contexte.simulateur().affiliations
    echelle = contexte.echelle(saisie)

    # Trois champs là où il en fallait cinq : une date de naissance porte son
    # mois, une date de départ porte l'âge qu'on avait écrit en deux fois. Les
    # bornes des calendriers sont celles du modèle, comptées depuis la
    # naissance saisie ; le script de la page les refait à chaque frappe, sans
    # attendre le calcul.
    identite = "".join([
        # ``autocomplete`` n'est pas là pour épargner une frappe : il donne au
        # navigateur — et aux outils qui s'appuient sur lui, dont les aides à la
        # saisie — le moyen de reconnaître ce que le champ demande.
        g.champ_date("naissance", "Date de naissance", saisie.naissance_iso,
                     "seul le mois compte", saisie.naissance_en_clair,
                     complement="Le calcul n'en retient que le mois : c'est la "
                     "maille du droit, qui coupe deux générations en cours "
                     "d'année — au 1<sup>er</sup> juillet 1951 et au "
                     "1<sup>er</sup> septembre 1961.",
                     min=f"{NAISSANCE_MINIMALE}-01-01",
                     max=f"{NAISSANCE_MAXIMALE}-12-31",
                     autocomplete="bday"),
        g.champ_date("liquidation", "Départ à la retraite",
                     saisie.jour_de(saisie.liquidation),
                     "effectif, ou souhaité",
                     saisie.calcul_de(saisie.liquidation),
                     complement="C'est la date à laquelle tout le calcul se "
                     "place. La pension prend effet le premier du mois, et "
                     "c'est celle du premier mois que vous obtiendrez — jamais "
                     "ce qu'elle devient ensuite.",
                     min=saisie.jour_de(AGE_LIQUIDATION_MINIMAL),
                     max=saisie.jour_de(AGE_LIQUIDATION_MAXIMAL),
                     data_age_min=str(AGE_LIQUIDATION_MINIMAL),
                     data_age_max=str(AGE_LIQUIDATION_MAXIMAL)),
    ])

    avance = "".join([
        # Le sexe ne change RIEN par défaut : la table de conversion est
        # unisexe, et les majorations pour enfants — les seules du système 1
        # qui distinguent le père de la mère — ne jouent qu'à partir d'un
        # enfant. Or ces deux réglages sont ici. Le champ les rejoint : il est
        # sans effet tant qu'on n'y a pas touché, et à côté d'eux dès qu'on y
        # touche.
        g.liste("sexe", "Sexe", [("H", "Homme"), ("F", "Femme")], saisie.sexe,
                "sans effet par défaut",
                complement="Il ne compte que de deux façons, toutes deux "
                "réglées ici : si la table de conversion est « par sexe », et "
                "si la carrière porte des enfants — le système actuel réserve "
                "à la mère la majoration de durée d'assurance.",
                autocomplete="sex"),
        g.liste("profil", "Profil de carrière", PROFILS, saisie.profil,
                _aide_profil(saisie.profil)),
        g.champ("primes", "Part de primes", _nombre(saisie.primes),
                "fonction publique : assiette du RAFP", type_="number",
                min="0", max="0.6", step="0.01"),
        g.champ("enfants", "Nombre d'enfants", saisie.enfants,
                "sans effet notionnel : les majorations sont supprimées",
                type_="number", min="0", max=str(ENFANTS_MAXIMUM), step="1"),
        g.champ("interruptions", "Interruptions", saisie.interruptions,
                "« 1995:1999:education_enfant », séparées par des virgules"),
    ]) + _champs_modelisation(saisie)

    tete = g.affiche(
        "Le simulateur",
        "Votre carrière, calculée "
        '<span class="cle-texte">quatre fois.</span>',
        "Le système actuel, les comptes notionnels appliqués depuis 1941 ou à "
        "partir de la bascule, et notre proposition. Tout se calcule dans "
        "votre navigateur : rien n'est envoyé, rien n'est conservé.",
    )
    return tete + f"""
<form class="carte" method="get" action="{g.route('/simuler')}">
  {g.cache("unite_revenu", saisie.unite_revenu)}
  {g.cache("montants", saisie.montants)}
  <h2 class="serif" style="margin-top:0">Votre carrière{_bulle_du_titre(saisie)}</h2>
  <p style="margin-top:0.3rem">L'exemple est déjà rempli. Calculez-le tel
  quel, ou saisissez la vôtre.</p>
  <div class="grille">{identite}</div>
  <h3>La carrière, période par période{_bulle_des_periodes()}</h3>
  {_metiers(saisie, affiliations, echelle)}
  {_bascule_unite(saisie, echelle)}
  {_bascule_montants(saisie, echelle)}
  {_mention_conversion(saisie, echelle)}
  {_releve(saisie)}
  <details class="options">
    {g.sommaire("Options de modélisation (sexe, profil, indexation, "
                "projection)")}
    <div class="grille">{avance}</div>
  </details>
  <p style="margin-top:1.4rem"><button type="submit">Calculer les quatre systèmes</button></p>
</form>
"""


#: Les trois premières lignes d'un relevé, montrées dans le formulaire. Elles
#: disent le format mieux qu'une phrase : une année, un statut, ce qui a été
#: gagné cette année-là, et les trimestres que le relevé porte en face.
EXEMPLE_RELEVE = (
    "1998:salarie_prive_non_cadre:14200:4\n"
    "1999:salarie_prive_non_cadre:15100:4\n"
    "2000:salarie_prive_cadre:19800:4"
)


def _releve(saisie: Saisie) -> str:
    """Le relevé de carrière : la saisie exacte, celle qui ne suppose rien.

    Elle est repliée sous un dépliant, et non offerte d'emblée : la carrière
    paramétrique reste la porte d'entrée — on la remplit en trente secondes,
    sans rien avoir sous les yeux. Le relevé, lui, demande d'avoir ouvert son
    compte Info-Retraite, et il s'adresse à qui veut confronter le simulateur à
    SON estimation plutôt qu'à une carrière type. Le dépliant s'ouvre de
    lui-même quand un relevé est saisi : sinon, l'adresse porterait une carrière
    que la page ne montrerait pas.
    """
    bulle = g.bulle(
        "Ce que le relevé remplace, et comment il se lit",
        "Sans les trimestres, le modèle les déduit du montant. Le revenu est "
        "celui de l'année entière, en euros de cette année-là ; un relevé "
        "antérieur à 2002 est en francs, à diviser par 6,55957. Les codes de "
        "régime sont ceux du menu ci-dessus. Rempli, ce champ "
        "<strong>remplace</strong> les métiers, le profil et le niveau de "
        "revenu : rien n'est plus reconstitué. Naissance, date de départ, "
        "enfants, primes et interruptions continuent de valoir.",
    )
    return f"""
<details class="releve"{' open' if saisie.releve_actif else ''}>
  {g.sommaire("Coller un relevé de carrière — la saisie exacte")}
  <p class="discret">Une ligne par année : <strong>année:régime:revenu</strong>,
  et <strong>:trimestres</strong> si le relevé les porte.{bulle}</p>
  {g.zone("releve", "Relevé de carrière", saisie.releve,
          f"au plus {RELEVE_MAXIMUM} lignes ; vide, la carrière est celle des "
          "métiers ci-dessus", lignes=10, placeholder=EXEMPLE_RELEVE,
          spellcheck="false")}
</details>
"""


def _champ_revenu(nom: str, saisie: Saisie, echelle: "Echelle", valeur: str,
                  bref: bool = False) -> str:
    """Le champ « combien gagnez-vous », dans l'unité choisie.

    Le libellé porte le mot ``brut`` et l'aide dit où le lire : c'est la
    question qui revenait le plus souvent devant ce formulaire, et elle se règle
    là, sur le champ, plutôt que dans un encadré qu'on lit après avoir répondu.
    """
    if not saisie.revenu_en_euros:
        aide = ("en multiples du salaire moyen brut" if bref else
                f"1 = salaire moyen, soit {g.euros(echelle.mensuel(1))} bruts "
                "par mois")
        return g.champ(nom, "Niveau de revenu", valeur, aide, type_="number",
                       complement="" if bref else
                       "Le modèle raisonne en multiples du salaire moyen par "
                       "tête : c'est l'unité qui garde son sens sur "
                       "quatre-vingts ans, quand un montant n'en a que rapporté "
                       "à son année.",
                       min="0.1", max="10", step=_nombre(PAS_MULTIPLE))

    # « Revenu » et non « salaire » : douze des vingt-deux statuts ne sont pas
    # salariés, et un artisan n'a ni salaire ni fiche de paie. Le brut garde le
    # même sens pour lui — ce sur quoi ses cotisations sont assises —, et la
    # fiche de paie n'est plus donnée que comme l'exemple qu'elle est.
    aide = ("en euros bruts par mois" if bref else
            f"SMIC {g.euros(echelle.smic)}, moyenne "
            f"{g.euros(echelle.mensuel(1))}, plafond {g.euros(echelle.plafond)}")
    return g.champ(nom, "Revenu brut mensuel", valeur, aide, type_="number",
                   complement="" if bref else
                   "En euros d'aujourd'hui, avant cotisations et impôt — pour "
                   "un salarié, la ligne « brut » de la fiche de paie. Le "
                   "modèle le suit ensuite le long du salaire moyen, année "
                   "après année.",
                   min="0", step="1")


def _aide_profil(profil: str) -> str:
    """Ce que le profil fait du salaire saisi, en toutes lettres.

    Sans elle, saisir « 2 900 € par mois » se lit comme la promesse de gagner
    2 900 € chaque année de sa vie, alors que le revenu saisi est celui du
    milieu de carrière et que le profil le déforme aux deux bouts.
    """
    debut, fin = bornes_deformation(profil)
    if debut == fin:
        return "le revenu saisi vaut pour toutes les années de la carrière"
    return (f"le revenu saisi est celui du milieu de carrière : ×{g.nombre(debut, 2)} "
            f"au premier emploi, ×{g.nombre(fin, 2)} au dernier")


def _bascule_unite(saisie: Saisie, echelle: "Echelle") -> str:
    """Le lien qui change l'unité de saisie, montants déjà convertis.

    Un lien, et non un menu : un formulaire HTML ne convertit rien quand on
    change un menu, si bien que le nombre resterait celui de l'ancienne unité —
    « 3 500 » deviendrait 3 500 fois le salaire moyen, et la page refuserait la
    saisie au lieu de la traduire. Le lien, lui, porte l'adresse complète, unité
    ET montants déjà traduits : la page revient dans l'autre unité en décrivant
    exactement la même carrière. C'est la façon dont tout le reste du site
    navigue, et elle ne demande pas une ligne de JavaScript.

    L'unité vaut pour toute la carrière : une unité par métier n'aurait décrit
    aucune carrière réelle, et aurait posé six fois la même question.
    """
    vers_les_euros = not saisie.revenu_en_euros
    autre = "euros_mois" if vers_les_euros else "moyen"
    # ``niveaux`` ramène les montants à l'unité du modèle quelle que soit celle
    # de la saisie : la traduction dans l'autre sens part donc toujours de là.
    valeurs = [
        _nombre(round(echelle.mensuel(niveau)) if vers_les_euros
        else round(niveau, DECIMALES_MULTIPLE))
        for niveau in saisie.niveaux(echelle)
    ]
    remplacements = {"unite_revenu": autre, "salaire": valeurs[0]}
    for rang, valeur in enumerate(valeurs[1:], start=2):
        remplacements[f"metier{rang}_salaire"] = valeur
    libelle = ("Saisir plutôt des euros par mois" if vers_les_euros
               else "Saisir plutôt un multiple du salaire moyen")
    return (f'<p class="discret" style="margin:0.9rem 0 0">'
            f'<a href="#/simuler?{escape(saisie.requete(**remplacements))}">{libelle}</a>'
            "</p>")


def _metiers(saisie: Saisie, affiliations: Affiliations,
             echelle: "Echelle") -> str:
    """Une ligne par période, plus une ligne vide pour en ajouter une.

    C'est ce qui permet d'allonger la carrière sans une ligne de JavaScript :
    la ligne vide est renvoyée avec le reste du formulaire, et devient une
    période dès qu'on la remplit. Une ligne de plus apparaît alors à sa suite,
    jusqu'à ``METIERS_MAXIMUM``.

    Une période est un métier, ou une période sans emploi : le menu de chaque
    ligne suivante propose les deux, et la dernière dit donc, quand elle est
    sans emploi, la date à laquelle l'activité s'arrête.

    Le menu des statuts de chaque ligne est daté de l'entrée dans cette
    période : un statut que le droit ferme avant cette date y est grisé.
    """
    lignes = [_ligne_metier(
        1,
        g.champ_date("debut", "Début d'activité", saisie.jour_de(saisie.debut),
                     "le premier mois cotisé",
                     saisie.calcul_de(saisie.debut),
                     complement="L'année d'entrée n'est complète que si l'on "
                     "entre en janvier : elle est portée au compte au prorata "
                     "de ses mois, comme celle du départ.",
                     min=saisie.jour_de(AGE_DEBUT_MINIMAL),
                     max=saisie.jour_de(AGE_DEBUT_MAXIMAL),
                     data_age_min=str(AGE_DEBUT_MINIMAL),
                     data_age_max=str(AGE_DEBUT_MAXIMAL))
        + g.liste("statut", "Statut d'affiliation",
                  _options_statuts(affiliations, saisie.date_de(saisie.debut)),
                  saisie.statut,
                  "proposé aux seules dates où son régime recrutait",
                  complement=g.GLOSSAIRE["statut d'affiliation"])
        + _champ_revenu("salaire", saisie, echelle, _nombre(saisie.salaire)),
    )]

    for rang, metier in enumerate(saisie.metiers, start=2):
        lignes.append(_ligne_metier(
            rang, _champs_metier(rang, saisie.jour_de(metier.debut),
                                 saisie.calcul_de(metier.debut), metier.statut,
                                 _nombre(metier.salaire),
                                 _options_statuts(affiliations,
                                                  saisie.date_de(metier.debut),
                                                  sans_emploi=True),
                                 saisie, echelle),
            sans_emploi=metier.sans_emploi))

    # La ligne vide : elle n'existe que tant qu'il reste de la place, et son
    # statut n'est pas présélectionné — un statut choisi par défaut ferait
    # naître un métier que personne n'a demandé.
    rang = len(saisie.metiers) + 2
    if rang <= METIERS_MAXIMUM:
        lignes.append(_ligne_metier(
            rang, _champs_metier(rang, "", "", "", "",
                                 _options_statuts(affiliations, None,
                                                  sans_emploi=True),
                                 saisie, echelle),
            vide=True))

    return f'<div class="metiers">{"".join(lignes)}</div>'


def _champs_metier(rang: int, debut: str, calcul: str, statut: str,
                   salaire: str, statuts: list[tuple], saisie: Saisie,
                   echelle: "Echelle") -> str:
    """Les champs d'une période qui suit la première.

    La période se date au mois comme le reste, depuis que le calendrier a
    remplacé les âges : il n'en coûte pas un champ de plus, et une carrière qui
    change de régime en cours d'année se décrit telle qu'elle a eu lieu.

    Une période sans emploi n'a que deux champs : elle ne paie aucun revenu, et
    celui d'avant lui sert de référence là où le droit lui ouvre des points.
    Le champ disparaît donc plutôt que de demander un nombre dont rien ne
    serait fait.
    """
    revenu = "" if statut in CODES_SANS_EMPLOI else _champ_revenu(
        f"metier{rang}_salaire", saisie, echelle, salaire, bref=True,
    )
    return (
        g.champ_date(f"metier{rang}_debut", "Début de cette période", debut,
                     "le mois où elle commence", calcul,
                     min=saisie.jour_de(AGE_DEBUT_MINIMAL),
                     max=saisie.jour_de(AGE_LIQUIDATION_MAXIMAL),
                     data_age_min=str(AGE_DEBUT_MINIMAL),
                     data_age_max=str(AGE_LIQUIDATION_MAXIMAL))
        + g.liste(f"metier{rang}_statut", "Métier, ou période sans emploi",
                  [("", "— aucun —")] + statuts, statut)
        + revenu
    )


def _ligne_metier(rang: int, champs: str, vide: bool = False,
                  sans_emploi: bool = False) -> str:
    """Une période : un ``<fieldset>``, et son rang en ``<legend>``.

    « Revenu brut mensuel » et « Métier, ou période sans emploi » sont les mêmes
    libellés dans chaque bloc ; seul le rang les distingue. Un intertitre
    ordinaire le montrerait à l'œil sans le dire à personne d'autre : la légende
    d'un groupe, elle, est énoncée avec chacun des champs qu'elle couvre.

    La ligne VIDE, elle, est repliée : trois champs offerts à qui n'en veut pas
    occupaient un tiers du formulaire pour la plupart des carrières, qui n'ont
    qu'un métier. Il n'en reste que la demande — « Ajouter une période » —, et
    les champs ne paraissent que si on la suit. Un ``<details>`` plutôt qu'un
    ``<fieldset>`` : c'est le résumé qui nomme le groupe, et le nommer deux fois
    ferait lire deux titres pour une ligne qui n'existe pas encore.
    """
    rangs = RANGS_METIER[rang - 1].capitalize()
    if vide:
        return ('<details class="metier facultatif">'
                + g.sommaire("Ajouter une période — un métier, une "
                             "interruption")
                + f'<div class="grille">{champs}</div></details>')
    titre = f"{rangs} période, sans emploi" if sans_emploi else f"{rangs} métier"
    return (f'<fieldset class="metier"><legend class="rang">{escape(titre)}</legend>'
            f'<div class="grille">{champs}</div></fieldset>')


def _resume_parcours(contexte: Contexte, saisie: Saisie) -> str:
    """La suite des périodes, en une phrase — et la convention qui les borne.

    Muet pour une carrière d'une seule période : il n'y a rien à récapituler,
    le formulaire juste au-dessus le dit déjà.
    """
    if saisie.releve_actif:
        return _resume_releve(contexte, saisie)
    lignes = saisie.lignes_carriere
    if len(lignes) < 2:
        return ""
    # Le parcours est calculé pour ses refus : un revenu hors bornes doit être
    # signalé ici comme il l'est ailleurs, avant que la page ne le résume.
    saisie.parcours(contexte.echelle(saisie))

    affiliations = contexte.simulateur().affiliations
    bornes = [ligne.debut for ligne in lignes] + [saisie.liquidation]
    etapes = [
        (LIBELLES_SANS_EMPLOI[ligne.statut] if ligne.sans_emploi
         else escape(affiliations.libelle(ligne.statut)))
        + f" de {_age(bornes[rang])} à {_age(bornes[rang + 1])}"
        for rang, ligne in enumerate(lignes)
    ]
    creux = any(ligne.sans_emploi for ligne in lignes)
    convention = (
        "L'année d'un changement revient à ce qui en occupe le plus de mois "
        "— les régimes liquident à l'année, et une année n'a qu'un statut — "
        "mais le revenu porté au compte reste la somme de ce qui a été payé."
        if creux else
        "L'année d'un changement revient au métier qui en occupe le plus de "
        "mois — les régimes liquident à l'année, et une année n'a qu'un "
        "statut — mais le revenu porté au compte reste la somme de ce que les "
        "deux ont payé."
    )
    return (
        f'<p class="discret">Carrière en {len(lignes)} périodes : '
        + ", puis ".join(etapes) + ". " + convention + "</p>"
    )


def _resume_releve(contexte: Contexte, saisie: Saisie) -> str:
    """Ce que le relevé a remplacé, et ce qu'il n'a pas remplacé.

    La phrase importe plus que le décompte : les champs du formulaire restent
    affichés au-dessus, avec le statut et le revenu qu'ils portaient, et rien
    ne dirait qu'ils n'ont pas servi. La lecture du relevé se termine donc par
    ce qu'aucun relevé ne donne — le mois d'entrée dans la vie active —, parce
    que c'est la seule approximation que ce chemin conserve.
    """
    releve = saisie.releve_analyse(
        charger_periodes_non_travaillees(contexte.simulateur().macro.racine)
    )
    affiliations = contexte.simulateur().affiliations
    statuts_lus = list(dict.fromkeys(ligne.affiliation for ligne in releve))
    cotisees = [ligne for ligne in releve if ligne.type_periode == "emploi"]
    libelles = ", ".join(
        escape(affiliations.libelle(code)) for code in statuts_lus
    )
    return (
        f'<p class="discret">Carrière <strong>lue sur un relevé</strong> : '
        f"{len(releve)} années de {min(ligne.annee for ligne in releve)} à "
        f"{max(ligne.annee for ligne in releve)}, "
        f"dont {len(cotisees)} cotisées, sous "
        f"{len(statuts_lus)} statut{'s' if len(statuts_lus) > 1 else ''} — "
        f"{libelles}. Les métiers, le profil de carrière et le niveau de revenu "
        "du formulaire n'ont pas servi : aucun revenu n'est reconstitué, ils "
        "sont lus un par un. Une ligne vaut une année civile entière, sauf "
        "celle du départ, que la date de liquidation tronque : le relevé donne "
        "l'année, jamais le mois, et l'année d'entrée dans la vie active reste "
        "donc comptée pour une année pleine.</p>"
    )


def _lecture_des_montants(comparaison: Comparaison, saisie: Saisie) -> str:
    """À quelle date se rapportent les montants affichés, et en quels euros.

    C'est la première question que pose un lecteur devant les quatre barres :
    « ce nombre, c'est celui de quand ? ». Deux conventions y répondent, dont
    aucune ne va de soi. Le moteur ne calcule qu'une pension AU MOMENT DE LA
    LIQUIDATION — il n'existe aucune phase postérieure qu'il revaloriserait —,
    et il l'exprime en euros constants. Autrement dit : jamais la pension
    d'aujourd'hui d'un retraité, toujours celle de son premier mois de
    retraite ; et jamais le montant nominal que porte un relevé bancaire,
    toujours son pouvoir d'achat ramené à une année de référence.

    Les deux conventions se disent différemment selon que le départ est passé
    ou à venir, parce que ce qu'elles écartent n'est pas le même : pour un
    actif, les revalorisations à venir de sa pension ; pour un retraité, celles
    qu'il a déjà reçues. La seconde n'a plus qu'un chiffre à expliquer : la
    page n'affiche que le pouvoir d'achat de l'année de référence, jamais la
    somme nominale du mois du départ, et ce paragraphe dit d'où il vient.
    """
    carriere = comparaison.carriere
    annee = carriere.annee_liquidation
    date = escape(str(carriere.date_liquidation))
    courante = comparaison.parametres.annee_courante

    if annee > courante:
        quand = (
            "Vous n'êtes pas encore à la retraite : ces montants sont ceux de "
            "votre <strong>première pension</strong>, celle du mois où vous "
            f"partiriez — {date} —, et non d'une pension que vous toucheriez "
            "aujourd'hui."
        )
    elif annee < courante:
        quand = (
            "Vous êtes déjà à la retraite : ces montants sont ceux de votre "
            f"pension <strong>au moment du départ</strong> — {date} —, et non "
            f"de celle que vous touchez aujourd'hui. Depuis {annee}, votre "
            "pension a été revalorisée chaque année ; le simulateur s'arrête au "
            "jour de la liquidation et ne suit aucune de ces revalorisations."
        )
    else:
        quand = (
            "Vous liquidez cette année : ces montants sont ceux de votre "
            f"<strong>première pension</strong>, celle de {date}. Le simulateur "
            "s'arrête là et ne suit pas les revalorisations des années "
            "suivantes."
        )

    if annee > saisie.euros:
        unites = (
            f"Ils sont donnés en euros de {saisie.euros}, et dans cette unité "
            "seulement : la somme telle qu'elle serait versée en "
            f"{annee}, l'inflation d'ici là comprise, est ramenée au pouvoir "
            f"d'achat de {saisie.euros} — plus petite, sans rien acheter de "
            "moins. C'est ce pouvoir d'achat, et non le nombre qui sera inscrit "
            "sur le virement, qui dit ce que vaut la pension : le nombre "
            "nominal n'est pas affiché."
        )
    elif annee < saisie.euros:
        unites = (
            f"Ils sont donnés en euros de {saisie.euros}, et dans cette unité "
            f"seulement : la somme telle qu'elle a été versée en {annee}, en "
            "euros de l'époque, est ramenée au pouvoir d'achat de "
            f"{saisie.euros}, le seul qui se compare aux prix que vous "
            "connaissez ; le montant de l'époque n'est pas affiché."
        )
    else:
        unites = (
            f"Le départ tombe sur {saisie.euros}, l'année de référence : les "
            "euros du départ et ceux dans lesquels la page compte sont les "
            "mêmes, et il n'y a rien à convertir."
        )

    return g.bulle(
        "De quand sont ces chiffres, et en quels euros",
        f"{quand} {unites} Ce que compare cette page, ce sont quatre façons de "
        "CALCULER une pension de départ, pas quatre façons de la revaloriser "
        "ensuite. Montants <strong>bruts</strong> et au centime, comme la "
        "caisse les verse : avant CSG, CRDS et impôt, comme le revenu "
        "d'activité saisi plus haut. Le <strong>taux de remplacement</strong> "
        "rapporte la pension annuelle au dernier revenu d'activité ramené à "
        "l'année pleine — un brut sur un brut, donc plus bas qu'un taux calculé "
        "sur des nets.",
    )


def _corps_trajectoire(contexte: Contexte, comparaison: Comparaison,
                       saisie: Saisie) -> str:
    """Le cumul versé par chaque scénario, du départ à 105 ans.

    Renvoie le CORPS seul, sans son enveloppe : la page Simuler le replie sous
    un dépliant (:func:`_trajectoire`), la page Trajectoire le montre ouvert,
    et il n'est calculé qu'une fois de chaque façon. Chaîne vide si la
    carrière ne permet aucun cumul.

    Les quatre barres du haut donnent la pension d'UN mois — le premier. Elles ne
    disent donc rien de ce qu'une retraite finit par verser, ni de ce que la
    durée y change. Or c'est là que la mécanique notionnelle se joue : la
    pension vaut le capital divisé par l'espérance de vie, si bien que vivre
    au-delà de cette moyenne, c'est toucher plus que ce que la carrière a
    financé, et mourir avant, moins. Un graphique arrêté à l'espérance de vie
    cacherait exactement cela ; celui-ci va jusqu'à 105 ans.

    Ce que le cumul suppose, et que la page dit : la pension garde son pouvoir
    d'achat après le départ. Le moteur ne simule aucune revalorisation
    postérieure à la liquidation — additionner en euros constants est la
    convention la plus neutre dont on dispose, ce n'est pas une prévision.
    """
    carriere = comparaison.carriere
    depart = carriere.age_liquidation or 0.0
    if not 0 < depart < AGE_MAXIMUM_TRAJECTOIRE:
        return ""

    annuel = {
        cle: comparaison.en_euros_constants(getattr(comparaison, cle).pension_annuelle)
        for cle, _, _ in TRAJECTOIRE
    }
    if max(annuel.values(), default=0.0) <= 0:
        return ""

    ages = tuple(range(int(math.floor(depart)), AGE_MAXIMUM_TRAJECTOIRE + 1))
    titres = dict(_titres_scenarios(saisie))
    series = tuple(
        g.Serie(
            libelle=titres[cle],
            # En milliers : l'axe monterait sinon à sept chiffres, illisibles
            # dans la marge d'un graphique qui doit tenir sur un téléphone.
            # Rien avant le départ : pour une liquidation en cours d'année,
            # « max(0, âge - départ) » faisait partir la courbe de l'âge entier
            # précédent, soit jusqu'à onze mois de pension qui n'ont pas été
            # versés. La courbe commence maintenant au premier âge atteint.
            valeurs=tuple(
                None if age < depart else annuel[cle] * (age - depart) / 1000
                for age in ages
            ),
            couleur=f"var({couleur})",
        )
        for cle, couleur, _ in TRAJECTOIRE
    )
    etiquettes = tuple(chiffre for _, _, chiffre in TRAJECTOIRE)

    conversion = comparaison.notionnel_retroactif.conversion
    esperance = conversion.esperance_residuelle
    age_esperance = depart + esperance
    survie = _survie(contexte, carriere, conversion.table)

    def vivants(age: float) -> str:
        return g.pourcentage(_part_vivante(survie, age - depart), decimales=0)

    # Le système 2 passe au-dessus du système 1 pour qui a beaucoup cotisé
    # sans que le droit en vigueur le lui rende — un libéral à quatre fois le
    # salaire moyen, par exemple. La phrase disait « l'écart se creuse » en
    # affichant « -45 575 € par an » : un signe moins au milieu d'un texte qui
    # affirmait le contraire.
    ecart = annuel["actuel"] - annuel["notionnel_retroactif"]
    phrase_ecart = (
        f"Le système 2 verse {g.euros(abs(ecart))} par an de "
        + ("moins" if ecart >= 0 else "plus")
        + " que le système 1 ; l'écart se creuse ici d'autant d'années que la "
        "retraite dure"
    )
    # Unité brève : le libellé est ancré à gauche de l'axe et déborderait du
    # cadre au-delà d'une poignée de caractères — « milliers d'euros de 2026,
    # cumulés » sortait du viewBox par la gauche, et « k€ 2026 » y perdait
    # encore son « k » sur téléphone, où les textes du repère sont grossis. Le
    # texte sous le graphique dit ce que « k€ » désigne, et de quelle année.
    unite = "k€"
    return f"""
<p>Les quatre montants du haut sont ceux d'un seul mois, le premier. Ce graphique
les additionne, année après année, à mesure que le retraité vieillit.{g.bulle(
    "Ce que ce graphique ajoute aux quatre montants",
    "C'est là que la durée entre dans le calcul. Une pension "
    "notionnelle vaut le capital divisé par l'espérance de vie, donc "
    "<strong>vivre plus longtemps que la moyenne, c'est toucher plus que ce "
    "que la carrière a financé</strong> — et mourir avant, moins. Cumuls "
    f"bruts, en milliers d'euros constants de {saisie.euros} : ils supposent "
    "que la pension garde son pouvoir d'achat après le départ, le moteur ne "
    "simulant aucune revalorisation postérieure à la liquidation. Une "
    "indexation qui décrocherait des prix ferait fléchir les quatre courbes à la "
    "fois, sans changer leur ordre.",
)}</p>
{g.graphique(
    "Cumul versé par chaque système, du départ à "
    f"{AGE_MAXIMUM_TRAJECTOIRE} ans",
    ages, series,
    unite=unite,
    repere=age_esperance,
    libelle_repere=f"espérance de vie : {g.nombre(age_esperance, 1)} ans",
    etiquettes=etiquettes,
    nom_abscisse="Âge",
)}
<p>Trait vertical : l'espérance de vie à {_age(depart)} —
<strong>{g.nombre(esperance, 1)} ans</strong>, soit {g.nombre(age_esperance, 1)}
ans d'âge, le nombre par lequel le capital notionnel est divisé.
{phrase_ecart}.{g.bulle(
    "Une moyenne, et non une échéance",
    "D'après la même table, "
    f"<strong>{vivants(age_esperance)}</strong> de ceux qui partent à "
    f"{_age(depart)} sont encore en vie à cet âge : ils dépassent donc le "
    "nombre qui a servi à calculer leur pension, et touchent plus que ce que "
    f"leur carrière a financé. Plus loin encore, {vivants(100)} atteignent "
    f"100 ans et {vivants(AGE_MAXIMUM_TRAJECTOIRE)} atteignent "
    f"{AGE_MAXIMUM_TRAJECTOIRE} ans, où le graphique s'arrête — c'est pour eux "
    "qu'il va si loin.",
)}</p>
"""


def _trajectoire(contexte: Contexte, comparaison: Comparaison,
                 saisie: Saisie) -> str:
    """Le même cumul, replié, pour le bas de la page Simuler.

    Là-bas il vient après quatre montants et trois tableaux : le déplier d'office
    ferait un septième bloc à traverser. Il a sa propre page, en revanche, où
    il est le sujet et s'ouvre donc de lui-même.
    """
    corps = _corps_trajectoire(contexte, comparaison, saisie)
    if not corps:
        return ""
    return g.depliant("Ce que chaque système finit par verser", corps)



def _page_trajectoire(contexte: Contexte, parametres: dict[str, str]) -> str:
    """Ce que chaque système vous AURA versé, du départ à 105 ans.

    Cette page existe parce qu'un montant mensuel ne dit rien de la durée. Les
    barres de la page Simuler donnent la pension d'un mois, le premier ; ici
    on additionne, année après année, et c'est là que la mécanique notionnelle
    devient visible — la pension vaut le capital divisé par l'espérance de vie,
    donc vivre au-delà de cette moyenne c'est toucher plus que ce que la
    carrière a financé.

    Elle porte UN graphique, et un seul : c'est la règle du site depuis la
    refonte — le Coût montre la trajectoire du système, Simuler compare les
    scénarios, celle-ci compare les cumuls. Une page, une question.

    Le formulaire est le même que celui de l'accueil, et pointe ici : on change
    la carrière sans quitter la page. Sans paramètres, la carrière d'exemple
    répond — une page qui s'ouvrirait sur un formulaire vide ne montrerait pas
    ce qu'elle a à montrer.
    """
    tete = g.affiche(
        "Trajectoire",
        "Ce que chaque système vous "
        '<span class="cle-texte">aura versé.</span>',
        "La même carrière, suivie année après année depuis le départ. Pas une "
        "pension mensuelle, mais le cumul : ce que vous aurez réellement "
        "touché à 75, à 86, à 95 ans.",
    )
    formulaire = _simulateur_court(contexte, "/trajectoire")

    try:
        saisie = Saisie.depuis_requete(parametres)
    except ErreurSaisie as erreur:
        return tete + formulaire + _erreur(str(erreur))

    try:
        comparaison = contexte.simuler(saisie)
        corps = _corps_trajectoire(contexte, comparaison, saisie)
    except (ErreurSaisie, DonneeInsuffisante, KeyError, ValueError) as erreur:
        return tete + formulaire + _erreur(str(erreur))
    if not corps:
        return tete + formulaire + _erreur(
            "Cette carrière ne verse aucune pension : il n'y a pas de cumul "
            "à tracer."
        )

    # Le graphique est monté en CARTE, et non posé nu : c'est la carte qui lui
    # donne sa question, sa réponse en une phrase, sa source — et sa barre de
    # partage. Sans elle, la Trajectoire aurait été la seule page à graphique
    # dont on ne puisse rien publier, alors que c'est le tracé le plus
    # démonstratif du site.
    carte = g.cle(
        "Au total, combien chaque système aura-t-il versé ?",
        "À âge de départ identique, l'écart entre deux courbes est ce que le "
        "système choisi vous coûte ou vous rapporte, année après année.",
        corps,
        "Cumuls bruts, en euros constants, sur la carrière saisie. "
        "Modèle ouvert : "
        f'<a href="{g.DEPOT}">le dépôt</a>.',
        identifiant="cumul",
    )

    return f"""
{tete}

{formulaire}

{carte}

<div class="paire">
  <div>
    <h2 style="margin-top:0">Pourquoi le cumul, et pas le mois</h2>
    <p>Une pension mensuelle ne dit rien de la durée. Le graphique montre les
    quatre systèmes à âge de départ identique : l'écart entre deux courbes est ce
    que le système choisi vous coûte ou vous rapporte, année après année.</p>
    <p>Les scénarios qui ne portent au compte que la <strong>part
    salariale</strong> restent sous le système actuel ; ceux qui y ajoutent la
    <strong>part patronale</strong> passent au-dessus. <span class="cle-texte">La
    proposition libérale se place entre les deux, avec un taux de
    {g.pourcentage(contexte.base.taux_cotisation_liberal, decimales=0)} au lieu
    de {g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)}.</span></p>
  </div>
  <div class="encadre">
    <h2 class="serif" style="margin-top:0">Le repère de l'espérance de vie</h2>
    <p>C'est la durée que le modèle lit sur la table de la génération
    concernée, et par laquelle le compte notionnel divise. Celui qui vit plus
    longtemps touche davantage que ce qu'il a cotisé, celui qui vit moins
    longtemps touche moins — comme dans tout système par répartition.</p>
    <p class="discret">Le trait vertical du graphique la marque. La courbe
    continue au-delà : c'est là que se lit ce qu'une longue vieillesse
    change.</p>
  </div>
</div>
"""



def _carte_partage(nom: str, surtitre: str, chiffre: str, phrase: str,
                   detail: str, classes: str = "") -> str:
    """Une carte 1200 × 675, au format de X et de LinkedIn.

    Ce que la page montre est l'APERÇU de la carte, réduit à la largeur de sa
    colonne ; ce qui se publie est l'image composée par le bouton, aux vraies
    dimensions. Elle a d'abord été rendue à sa taille réelle dans un cadre qui
    défilait, à charge pour le lecteur d'en faire une capture d'écran : deux
    gestes, un outil de capture, et un recadrage à la main pour une image que
    le site savait composer lui-même.

    Le pied est ce qui compte le plus : une image qui quitte le site n'a plus
    ni barre d'adresse ni page autour, et sans ces deux lignes elle circule
    sans dire d'où elle vient. Le premier qui la republie en devient la source.
    Dans l'image téléchargée, un filigrane le redit en travers du cadre — le
    pied se recadre tout seul, le filigrane coûte la carte.

    ``nom`` est le nom de la carte, lu AVANT elle : c'est ce qui permet de
    choisir laquelle publier sans les regarder toutes.
    """
    boite = f"carte-partage {classes}".strip()
    pied = (f'<div class="pied"><span class="compte">{g.SIGNATURE}</span>'
            f'<span class="adresse">{g.ADRESSE_SITE}</span></div>')
    corps = (f'<div class="{boite}">'
             f'<p class="surtitre">{surtitre}</p>'
             f'<div><div class="chiffre">{chiffre}</div>'
             f'<div class="phrase">{phrase}</div>'
             f'<div class="detail">{detail}</div></div>{pied}</div>')
    return (f'<figure class="carte"><figcaption>{nom}</figcaption>'
            f'<div class="cadre-carte">{corps}</div>{g.barre_partage()}</figure>')


def _partager(contexte: Contexte) -> str:
    """Les chiffres du programme, au format des réseaux sociaux.

    Cette page a failli ne pas exister sous cette forme. Elle a d'abord été LE
    dispositif de partage, et c'était une erreur : « pas grand monde ne va
    l'utiliser à part les militants qui sont au courant qu'elle existe ». Le
    partage est donc descendu sur les pages elles-mêmes — une barre sous chaque
    graphique, qui compose l'image de CE qu'on vient de lire. Ce qui reste ici
    est ce que cette barre ne peut pas donner : les chiffres du programme, qui
    ne sont le résultat d'aucun graphique.

    Elle demandait encore une capture d'écran. Elle n'en demande plus : chaque
    carte porte la MÊME barre que les graphiques du site, et rend la même
    chose — une image et son message.

    Les valeurs viennent du modèle, comme partout ailleurs : changer un
    paramètre change les cartes.
    """
    base = contexte.base
    cout = contexte.cout()
    solde = cout.solde
    horizon = solde.annee(solde.derniere_annee)
    taux = g.pourcentage(base.taux_cotisation_liberal, decimales=0)
    capitalise = g.pourcentage(base.taux_capitalisation_obligatoire, decimales=0)
    garantie = base.garantie_vieillesse_mensuelle
    isolement = base.allocation_isolement_mensuelle
    manque = abs(horizon.solde("actuel"))
    depense = horizon.depense("actuel")

    tete = g.affiche(
        "Partager",
        "Quatre cartes, "
        '<span class="cle-texte">prêtes à publier.</span>',
        "Un bouton par carte : l'image part au format des réseaux sociaux, "
        "avec son message déjà rédigé. "
        f'<strong class="cle-texte">{g.SIGNATURE}</strong> y est posé en '
        "filigrane, en travers de l'image et non dans un coin : le recadrer "
        "revient à recadrer la carte.",
    )

    cartes = "".join([
        _carte_partage(
            "Le plancher",
            "Notre programme pour les retraites",
            g.euros(garantie + isolement),
            "par mois au minimum, pour une personne seule.<br>"
            f"{g.euros(2 * garantie)} pour un couple.",
            f"{g.euros(garantie)} par personne, plus {g.euros(isolement)} "
            "d'allocation d'isolement. Payés par l'impôt, dès "
            f"{MinimumVieillesse.AGE_OUVERTURE} ans.",
        ),
        _carte_partage(
            "Le taux",
            "Baisse des prélèvements",
            taux,
            "de cotisation retraite, pour tout le monde.",
            "Part salariale et patronale additionnées : "
            f"{g.pourcentage(TAUX_ACTUEL_SALARIAL)} + "
            f"{g.pourcentage(TAUX_ACTUEL_PATRONAL)} aujourd'hui pour un "
            "salarié du privé.",
        ),
        _carte_partage(
            "Le déficit",
            "Ce que le système actuel ne paie plus",
            f"{g.nombre(manque * 100, 1)} points de PIB",
            f"c'est l'écart annuel à combler en {solde.derniere_annee}, sans "
            "réforme.",
            f"{g.pourcentage(depense, decimales=1)} du PIB de dépenses contre "
            f"{g.pourcentage(depense - manque, decimales=1)} de ressources. "
            "Source : COR, comptes du système de retraite.",
            classes="deficit",
        ),
        _carte_partage(
            "L'appel au simulateur",
            "Le simulateur",
            "Et vous, ça donne combien ?",
            "Votre carrière, calculée quatre fois : les règles d'aujourd'hui, et "
            "les nôtres.",
            "Modèle ouvert, données publiques. Tout se calcule dans votre "
            "navigateur : rien n'est envoyé.",
            classes="claire appel",
        ),
    ])

    return f"""
{tete}

<div class="cartes">{cartes}</div>

<div class="paire">
  <div>
    <h2 style="margin-top:0">Texte prêt à coller</h2>
    <p>« Un minimum de {g.euros(garantie + isolement)}/mois, {taux} de
    cotisation au lieu de
    {g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)}, et un compte de retraite
    en euros que chacun peut lire. Vérifiez sur votre carrière :
    {g.ADRESSE_SITE} — {g.SIGNATURE} »</p>
    <p class="discret">Le bouton de chaque carte met déjà ce message dans le
    presse-papiers avec l'image.</p>
  </div>
  <div class="encadre">
    <h2 class="serif" style="margin-top:0">Et depuis les pages du site</h2>
    <p>Inutile de repasser par ici pour partager un graphique : sous chacun, la
    même barre <span class="cle-texte">Partager</span> compose l'image de ce
    que vous venez de lire et le message qui va avec. Toutes portent le
    filigrane <span class="cle-texte">{g.SIGNATURE}</span>, en travers du
    cadre.</p>
  </div>
</div>
"""


def _titres_scenarios(saisie: Saisie) -> tuple[tuple[str, str], ...]:
    """Le libellé de chaque système, dans l'ordre des barres.

    Ces libellés ont été récrits : « Notionnel rétroactif » ne disait rien à
    qui n'avait pas lu la page Méthode, et « Rétroactif, avec le patronal » ne
    disait pas ce qui était rétroactif. Ils nomment maintenant ce qui change
    d'un système à l'autre — l'assiette —, et la glose sous chaque barre porte
    ce que le titre a cessé de dire : depuis quand la carrière est recalculée.
    Sans elle on ne comprendrait pas pourquoi le 2 donne moins que le 4.
    """
    return (
        ("actuel", "1. Système de répartition actuel"),
        ("notionnel_retroactif", "2. Compte notionnel, part salariale seule"),
        ("notionnel_retroactif_employeur",
         "3. Compte notionnel, part salariale + patronale"),
        ("notionnel_liberal", "4. La proposition du Parti libéral français"),
    )


def _survie(contexte: Contexte, carriere, table: str) -> tuple[float, ...]:
    """Courbe de survie EXACTEMENT celle dont le coefficient a été tiré.

    Le sexe et le type de table se relisent sur le libellé que porte le
    coefficient, plutôt que d'être recalculés depuis les paramètres : deux
    chemins de décision pour une seule table finiraient par diverger, et le
    graphique annoncerait alors une espérance de vie qui ne serait pas celle
    ayant servi à diviser le capital.
    """
    sexe = None if table.startswith("unisexe") else table.split("_")[0]
    generation = table.endswith("_generation")
    return contexte.simulateur().mortalite.courbe(
        carriere.age_liquidation or 0.0,
        carriere.annee_liquidation + (carriere.mois_liquidation - 1) / 12,
        sexe, generation,
    )


def _part_vivante(survie: tuple[float, ...], duree: float) -> float:
    """Part encore en vie ``duree`` années après la liquidation.

    Conditionnelle au fait d'être vivant AU DÉPART : la courbe part de 1 à
    l'âge de liquidation. Ce n'est donc pas une part de la génération née la
    même année — celle-là a déjà perdu des siens avant la retraite —, et la
    page dit « de ceux qui partent à tel âge », non « de la génération ».

    Interpolée entre deux âges entiers : l'espérance de vie tombe rarement sur
    un anniversaire, et arrondir la durée à l'année déplacerait le chiffre cité
    d'un point ou deux.
    """
    if duree <= 0:
        return 1.0
    rang = int(math.floor(duree))
    if rang + 1 >= len(survie):
        return survie[-1] if survie else 0.0
    fraction = duree - rang
    return survie[rang] * (1 - fraction) + survie[rang + 1] * fraction


def _resultats(contexte: Contexte, saisie: Saisie) -> str:
    comparaison = contexte.simuler(saisie)
    carriere = comparaison.carriere
    retro = comparaison.notionnel_retroactif
    conversion = retro.conversion

    # Le moteur ne calcule qu'un montant, en euros de l'année de liquidation.
    # La page n'en affiche qu'un, et ce n'est pas celui-là : le même ramené au
    # pouvoir d'achat de l'année de référence, seul à se comparer à un salaire
    # ou à un loyer que le lecteur connaît. La somme nominale du mois du départ
    # — des euros d'une année que personne n'a en poche — paraissait à côté :
    # elle doublait chaque ligne d'un second chiffre qu'il fallait une légende
    # pour distinguer du premier.
    courants = {
        "actuel": comparaison.actuel.pension_annuelle,
        "retroactif": retro.pension_annuelle,
        "retroactif-employeur":
            comparaison.notionnel_retroactif_employeur.pension_annuelle,
        # La proposition sert DEUX lignes : la pension de répartition issue du
        # compte notionnel, et la rente du pilier capitalisé obligatoire. Le
        # montant affiché est leur somme — c'est ce qui tombe sur le compte du
        # retraité —, et la barre comme la glose disent aussitôt ce qui vient
        # de l'une et ce qui vient de l'autre. Les confondre ferait passer pour
        # un rendement de la répartition ce qui sort d'un marché obligataire.
        "liberal": comparaison.notionnel_liberal.pension_totale,
    }
    constants = {cle: comparaison.en_euros_constants(montant)
                 for cle, montant in courants.items()}
    capitalise = comparaison.en_euros_constants(
        comparaison.notionnel_liberal.rente_capitalisation_obligatoire
    )
    reference = max(constants.values()) or 1.0

    montants = Montants.depuis(saisie, comparaison.parametres)
    annee_depart = carriere.annee_liquidation
    unite_reference = (
        "par mois, en euros d'aujourd'hui"
        if saisie.euros == comparaison.parametres.annee_courante
        else f"par mois, en euros de {saisie.euros}"
    )

    # Le salaire net que chaque système laisse PENDANT la carrière, à côté de
    # la pension qu'il servira APRÈS. Les trois premiers prélèvent la même
    # chose : le même nombre y paraît donc trois fois, et c'est le propos —
    # seul le système 4 déplace la fiche de paie. Vide quand il n'y a pas de
    # fiche de paie à écrire : un retraité ne cotise plus, et le modèle ne sait
    # écrire que celle d'un salarié du privé.
    remuneration = comparaison.remuneration
    nets = {}
    if remuneration is not None:
        reference_paie = remuneration.reference
        nets = {
            "actuel": montants.salaire(reference_paie.droit_en_vigueur),
            "retroactif": montants.salaire(reference_paie.droit_en_vigueur),
            "retroactif-employeur": montants.salaire(
                reference_paie.droit_en_vigueur),
            "liberal": montants.salaire(reference_paie.proposition),
        }

    def salaire(cle: str) -> str:
        """Le second chiffre de la ligne : ce qu'on touche en travaillant.

        Il est volontairement plus petit que la pension — la page compare des
        pensions, et le salaire est ce qu'on met EN REGARD. L'écart n'est écrit
        que là où il y en a un, pour que les trois premières lignes se lisent
        comme ce qu'elles sont : le même salaire net.
        """
        if cle not in nets:
            return ""
        net = nets[cle]
        ecart = net - nets["actuel"]
        mention = (
            f'<span class="ecart">{_euros_signe(ecart / 12.0)} par mois</span>'
            if abs(ecart) >= 0.005 else ""
        )
        return f"""
      <span class="chiffre salaire">
        <span class="categorie">salaire</span>
        <span class="somme">{g.nombre(net / 12.0)}</span>
        <span class="unite">{montants.unite_salaire}</span>
        {mention}
      </span>"""

    def bloc(cle: str, titre: str, glose: str, variation: float | None,
             taux_remplacement: float, part_capitalisee: float = 0.0) -> str:
        montant = constants[cle]
        variation_html = (
            '<span class="discret">référence</span>' if variation is None
            else f"<strong>{g.pourcentage(variation, signe=True)}</strong>"
        )
        # La barre du système qui porte un pilier capitalisé est coupée en
        # deux : la répartition pleine, la capitalisation hachurée. Même
        # couleur — c'est le même système —, autre texture — ce n'est pas la
        # même promesse. La hachure se voit aussi en noir et blanc et sous une
        # deutéranopie, ce qu'une seconde teinte ne garantirait pas.
        repartition = montant - part_capitalisee
        barre = f'<span style="width:{repartition / reference * 100:.1f}%"></span>'
        partage = ""
        if part_capitalisee > 0:
            barre += (f'<span class="capitalise" '
                      f'style="width:{part_capitalisee / reference * 100:.1f}%"></span>')
            partage = f"""
      <span class="composition">{g.euros_centimes(montants.pension(repartition) / 12)}
        de pension par répartition +
        {g.euros_centimes(montants.pension(part_capitalisee) / 12)} de rente
        capitalisée, par mois</span>"""
        return f"""
<div class="scenario">
  <div class="entete">
    <span class="titre">{escape(titre)}</span>
    <span class="montant">{salaire(cle)}
      <span class="chiffre principal">
        <span class="categorie">retraite</span>
        <span class="somme">{g.nombre(montants.pension(montant) / 12)}</span>
        <span class="unite">{montants.unite_pension}</span>
      </span>
    </span>
  </div>{partage}
  <div class="barre {cle}">{barre}</div>
  <div class="glose">{glose} · {g.terme("taux de remplacement")}
    {g.pourcentage(taux_remplacement)} · écart au système actuel : {variation_html}</div>
</div>"""

    # La glose porte ce que le titre ne dit plus : DEPUIS QUAND la carrière est
    # recalculée, et à quel taux. C'est ce qui explique l'ordre des montants —
    # sans elle, on ne voit pas pourquoi le 2 donne moins que le 4 alors que
    # tous deux sont des comptes notionnels.
    scenarios = (
        bloc("actuel", "1. Système de répartition actuel",
             "le droit en vigueur, minima et majorations compris",
             None, comparaison.taux_remplacement_actuel)
        + bloc("retroactif", "2. Compte notionnel, part salariale seule",
               "toute la carrière recalculée depuis 1941, sur la seule part "
               "salariale — 11,3 % du brut pour un salarié du privé",
               comparaison.variation("notionnel_retroactif"),
               comparaison.taux_remplacement_retroactif)
        + bloc("retroactif-employeur",
               "3. Compte notionnel, part salariale + patronale",
               "la même carrière recalculée depuis 1941, les deux parts "
               "comprises — les 28 % prélevés aujourd'hui",
               comparaison.variation("notionnel_retroactif_employeur"),
               comparaison.taux_remplacement("notionnel_retroactif_employeur"))
        + bloc("liberal",
               "4. La proposition du Parti libéral français",
               f"le système 3 jusqu'à {saisie.bascule}, puis 18 % pour tous en "
               "répartition et "
               f"{g.pourcentage(comparaison.parametres.taux_capitalisation_obligatoire, decimales=0)} "
               "capitalisés par-dessus — plus une garantie vieillesse payée "
               "par l'impôt",
               comparaison.variation_totale("notionnel_liberal"),
               comparaison.taux_remplacement_total("notionnel_liberal"),
               part_capitalisee=capitalise)
    )

    fiches = "".join([
        g.fiche("années cotisées", str(len(carriere.annees_cotisees))),
        # La date, et pas seulement l'année : la pension prend effet le premier
        # du mois, et c'est ce mois que l'utilisateur vient de choisir.
        g.fiche("liquidation", f"{_age(carriere.age_liquidation)} "
                f'<span class="discret">en {carriere.date_liquidation}</span>'),
        # Deux décimales, et non une : le lecteur qui refait la division
        # « capital ÷ coefficient » doit retrouver la pension affichée. À 25,7
        # au lieu de 25,67 il tombait un euro à côté, et doutait du reste.
        g.fiche("coefficient de conversion",
                g.nombre(conversion.diviseur, DECIMALES_DIVISEUR),
                definition=g.GLOSSAIRE["coefficient de conversion"]),
        # Le capital est un montant de l'année de liquidation, quand les six
        # pensions ci-dessous sont mises en avant en euros de l'année de
        # référence : sans l'unité, deux grandeurs de nature différente se
        # touchaient sans que rien ne les distingue.
        g.fiche(f"capital notionnel rétroactif, en euros de {annee_depart}",
                g.euros(retro.capital_notionnel),
                definition=g.GLOSSAIRE["capital notionnel"]),
    ])

    capitalisation = ""
    if comparaison.actuel.pension_hors_repartition > 0:
        montant = comparaison.en_euros_constants(
            comparaison.actuel.pension_hors_repartition
        )
        capitalisation = (
            f'<p class="discret">Hors répartition, servi à part : '
            f"{g.euros_centimes(montant / 12)} par mois de RAFP, en euros de "
            f"{saisie.euros} comme les quatre montants ci-dessus."
            + g.bulle(
                "Pourquoi le RAFP est servi à part",
                "Ce régime est PROVISIONNÉ — sa rente sort d'un placement, non "
                "de la cotisation des actifs —, si bien qu'une réforme de la "
                "répartition ne l'atteint pas. Il est donc retiré des six "
                "totaux et servi à l'identique dans les quatre systèmes : c'est "
                "la seule façon de comparer ce qui est comparable.",
            )
            + "</p>"
        )

    minimum = ""
    if comparaison.actuel.minimum_applique:
        minimum = (
            '<p class="discret">Le minimum contributif s\'applique dans le '
            "système 1 ; il est supprimé dans les systèmes notionnels, et la "
            "proposition lui substitue sa garantie vieillesse.</p>"
        )

    ouverture = ""
    if not comparaison.actuel.liquidation_ouverte:
        age = comparaison.actuel.age_ouverture_opposable
        attente = (f" — il faut attendre {g.nombre(age, 2)} ans"
                   if age is not None else "")
        ouverture = (
            '<p class="note avertissement">'
            + g.icone("triangle-alert", "Avertissement")
            + '<span>Le droit en vigueur <strong>n\'ouvre pas'
            "</strong> cette liquidation à "
            f"{g.nombre(comparaison.carriere.age_liquidation, 2)} ans{attente}. "
            "Ni l'âge légal du régime, ni le départ anticipé pour carrière "
            "longue ne le permettent. Le montant du système 1 reste calculé, "
            "parce qu'il faut bien comparer les quatre systèmes sur la même "
            "carrière, mais il ne décrit aucune pension que le système actuel "
            "servirait.</span></p>"
        )

    fiabilite = (
        '<p class="discret" style="margin-top:1.5rem">Fiabilité du résultat : '
        f'<span class="etiquette-fiabilite">{escape(str(comparaison.fiabilite))}'
        "</span></p>"
    )
    # La clé de lecture, avant les chiffres. Les six blocs portent des titres
    # exacts ; aucun ne disait qu'il n'y a qu'une carrière, ni que le premier
    # est la référence des cinq autres. Cinq phrases, en clair.
    lecture = f"""
<p class="note resume"><strong>Quatre calculs pour votre carrière.</strong>
Le système 1 applique les règles d'aujourd'hui. C'est la référence.
Les trois autres appliquent chacun d'autres règles à la même carrière.
Deux chiffres par ligne : à gauche votre <strong>salaire</strong> pendant que
vous cotisez, à droite votre <strong>pension</strong> une fois retraité — en
{montants.mot}, l'un comme l'autre, {unite_reference}.
{_note_du_mode(montants)}
Le pourcentage en fin de ligne : l'écart avec le système 1.</p>"""

    # Les montants d'abord, les repères techniques ensuite. Dans l'autre ordre,
    # un téléphone montrait après le calcul un coefficient de conversion, un
    # capital et une note sur l'âge de référence, et pas un euro de pension.
    return f"""
<h2 id="resultats" tabindex="-1">Résultats\
{_lecture_des_montants(comparaison, saisie)}</h2>
{lecture}
<div class="carte">
  {scenarios}
  {_bascule_montants(saisie, contexte.echelle(saisie), "#resultats")}
  {fiabilite}
  {capitalisation}
  {minimum}
  {ouverture}
</div>
<div class="carte">
  <div class="fiches">{fiches}</div>
  {_resume_parcours(contexte, saisie)}
</div>
{_salaire_net(comparaison, saisie)}
<h2>Pour aller plus loin</h2>
<p class="chapeau">Les quatre montants ci-dessus sont le résultat ; tout ce qui
suit est le détail du calcul, rangé par question. Ouvrez ce que vous voulez
voir.</p>
{_trajectoire(contexte, comparaison, saisie)}
{_fourchette(contexte, saisie, comparaison)}
{_decomposition(contexte, saisie, comparaison)}
{_contribution_employeur(comparaison)}
{_garantie_vieillesse(comparaison, saisie)}
{_pilier_capitalise(comparaison, saisie)}
{_detail(contexte, comparaison)}
"""


NATURES_PART_EMPLOYEUR = {
    "appelee": "contribution appelée par décret ou par arrêté",
    "implicite": "taux implicite reconstitué par les documents budgétaires",
    "repli": "aucune série publiée : effort du privé de la même année",
}


#: Les quatre systèmes, dans l'ordre où la page les affiche, avec le libellé
#: court que la fourchette leur donne.
SCENARIOS_AFFICHES = tuple(
    (scenario, LIBELLES_SYSTEMES[scenario]) for scenario in SCENARIOS_MONTRES
)


def _fourchette(contexte: Contexte, saisie: Saisie,
                comparaison: Comparaison) -> str:
    """Ce que l'hypothèse de productivité pèse dans le résultat affiché.

    Un montant unique se lit comme une prévision. Il n'en est pas une dès qu'une
    année de la carrière tombe après la dernière observation : il est alors la
    conséquence d'un scénario, et le lecteur doit voir laquelle.

    Le bloc rejoue donc la même carrière sous les trois hypothèses du COR et
    donne l'écart. Quand la liquidation précède la dernière année observée, il
    n'y a rien à faire varier — et c'est la chose la plus utile qu'on puisse
    dire à quelqu'un qui redoute les hypothèses : son chiffre n'en contient
    aucune.
    """
    macro = contexte.simulateur(saisie.parametres(contexte.base)).macro
    derniere_observee = macro.derniere_annee_observee
    carriere = comparaison.carriere
    debut = min(carriere.annees_cotisees, default=carriere.annee_liquidation)
    liquidation = carriere.annee_liquidation
    total = liquidation - debut + 1
    projetees = max(0, liquidation - max(debut - 1, derniere_observee))

    if not projetees:
        return g.depliant("Ce que l'hypothèse pèse", f"""
<p class="note">Rien, ici : la carrière s'achève en {liquidation}, et les séries
sont observées jusqu'en {derniere_observee}. <strong>Aucune année projetée
n'entre dans ce calcul</strong> — les montants ci-dessus sont identiques dans
les trois scénarios macroéconomiques, parce qu'aucun d'eux ne s'y applique.</p>""")

    montants: dict[str, dict[str, float]] = {}
    for code, _ in PROJECTIONS:
        try:
            variante = (comparaison if code == saisie.projection
                        else contexte.simuler(
                            Saisie(**{**saisie.__dict__, "projection": code})))
        except (ErreurSaisie, DonneeInsuffisante, KeyError, ValueError):
            continue
        montants[code] = {
            scenario: variante.en_euros_constants(
                getattr(variante, scenario).pension_annuelle)
            for scenario, _ in SCENARIOS_AFFICHES
        }

    basse = montants.get("cor_productivite_basse", {})
    haute = montants.get("cor_productivite_haute", {})
    if not basse or not haute:
        return ""

    lignes = []
    for scenario, libelle in SCENARIOS_AFFICHES:
        bas, haut = basse[scenario], haute[scenario]
        amplitude = (haut / bas - 1.0) if bas > 0 else float("nan")
        lignes.append([
            escape(libelle),
            g.euros_centimes(bas / 12),
            g.euros_centimes(montants[saisie.projection][scenario] / 12)
            if saisie.projection in montants else "—",
            g.euros_centimes(haut / 12),
            g.pourcentage(amplitude),
        ])

    retenu = dict(PROJECTIONS)[saisie.projection]
    reference = comparaison.en_euros_constants(
        comparaison.notionnel_retroactif.pension_annuelle) / 12
    ecart_2 = (haute["notionnel_retroactif"] / basse["notionnel_retroactif"] - 1.0
               if basse["notionnel_retroactif"] > 0 else float("nan"))

    return g.depliant("Ce que l'hypothèse pèse", f"""
<p>La même carrière, rejouée sous les trois hypothèses du COR. Le système 2
passe de {g.euros_centimes(basse["notionnel_retroactif"] / 12)} à
{g.euros_centimes(haute["notionnel_retroactif"] / 12)} par mois, soit
<strong>{g.pourcentage(ecart_2)} d'amplitude</strong> autour des
{g.euros_centimes(reference)} affichés plus haut.{g.bulle(
    "Ce que la fourchette fait varier, et ce qu'elle laisse fixe",
    f"Le compte est revalorisé chaque année de {debut} à {liquidation}, soit "
    f"{total} années — dont <strong>{projetees} après {derniere_observee}"
    "</strong>, la dernière année observée. Ces "
    f"{g.pourcentage(projetees / total)} du calcul ne reposent sur aucune "
    "mesure, mais sur l'hypothèse de croissance de la productivité que le "
    "Conseil d'orientation des retraites fixe et révise : 0,4 %, 0,7 % et "
    "1,0 % par an, le jeu retenu depuis juin 2025. La fourchette laisse fixes "
    "les autres hypothèses — inflation à 1,75 %, emploi salarié constant, "
    "législation inchangée : c'est une mesure de sensibilité à un paramètre, "
    "non un intervalle de confiance, et l'avenir peut en sortir.",
)}</p>
{g.tableau(
    ["Système", "Productivité 0,4 %", escape(retenu), "Productivité 1,0 %",
     "Amplitude"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
    titre="Pension mensuelle de chaque système sous les trois hypothèses de "
          "productivité du COR",
    entete_de_ligne=True,
)}
<p class="discret">Montants mensuels bruts, en euros constants de
{saisie.euros}.</p>""")


def _contribution_employeur(comparaison: Comparaison) -> str:
    """Qui verse la cotisation : l'assuré, son employeur, dans quelle proportion.

    C'est la mesure directe de ce qui sépare le système 2 du système 3. Le bloc ne s'affiche pas pour un non-salarié, qui n'a pas
    d'employeur et pour qui les quatre scénarios se réduisent à deux.
    """
    employeur = comparaison.contribution_employeur
    if not (employeur.a_un_employeur or employeur.concerne_un_regime_public):
        return ""

    partage = ""
    if employeur.a_un_employeur:
        partage = g.tableau(
            ["Part", "Ce qu'elle recouvre", "Montant"],
            [
                ["Part salariale", "ce que l'assuré supporte — système 2",
                 g.euros(employeur.agent)],
                ["Part patronale", "ce que verse l'employeur",
                 g.euros(employeur.employeur)],
                ["Total", "système 3", g.euros(employeur.total)],
            ],
            ["", "", "nombre"],
            titre="Cotisations versées sur toute la carrière, en euros courants "
                  "cumulés",
            entete_de_ligne=True,
        ) + (
            f"<p>L'employeur verse ici <strong>"
            f"{g.pourcentage(employeur.part)}</strong> du total.</p>"
        )

    # La part patronale d'un agent public n'est dans aucune fiche : elle vient
    # d'une série à part, qui ne couvre pas tous les régimes ni toutes les
    # années. Le dire est le prix de s'en servir.
    public = ""
    if employeur.concerne_un_regime_public:
        origines = "".join(
            f"<li>{escape(NATURES_PART_EMPLOYEUR.get(origine, origine))} — "
            f"{nombre} année{'s' if nombre > 1 else ''}</li>"
            for origine, nombre in sorted(employeur.annees_par_origine.items())
        )
        public = f"""
<p>Les fiches de la fonction publique et des régimes spéciaux ne portent que la
<strong>retenue de l'agent</strong>. La part de l'employeur vient d'une série à
part — reconstituée par les documents budgétaires de 1995 à 2005, appelée par
décret depuis 2006 pour l'État, versée à une caisse depuis 1948 pour la fonction
publique territoriale et hospitalière. Origine, année par année :</p>
<ul class="serree">{origines}</ul>
<p class="discret">Et c'est la limite de ces deux scénarios pour un agent
public. Un taux de 82,28 % ne signifie pas qu'un fonctionnaire acquiert 82 % de
son traitement en droits nouveaux : il est fixé pour que le compte
d'affectation spéciale « Pensions » soit à l'équilibre, donc pour payer les
pensions d'aujourd'hui. Le porter au compte répond à une question précise —
« et si tout ce qui a été consacré aux pensions avait été porté au compte des
actifs ? » — et à elle seule.</p>"""

    return g.depliant("Qui verse la cotisation", f"""
<p>Une cotisation retraite a deux parts : ce que l'assuré supporte, et ce que
son employeur verse.{g.bulle(
    "Ce que les scénarios portent au compte",
    "Le système 2 ne porte au compte que la première ; le système 3 "
    "y ajoute la seconde, et ne change rien d'autre.",
)}</p>
{partage}{public}""")


#: Les couples du tableau de la proposition, en euros mensuels : deux pensions,
#: ou une seule pour une personne seule. La page les recalcule avec la règle
#: que le scénario applique, plutôt que de les recopier.
EXEMPLES_GARANTIE = (
    ((300.0, 300.0), "300 € et 300 €"),
    ((300.0, 1500.0), "300 € et 1 500 €"),
    ((900.0, 900.0), "900 € et 900 €"),
    ((300.0, 5000.0), "300 € et 5 000 €"),
    ((300.0,), "personne seule, 300 €"),
)



def _pilier_capitalise(comparaison: Comparaison, saisie: Saisie) -> str:
    """Le pilier obligatoire : ce qu'il reçoit, ce qu'il rend, ce qu'il lègue.

    C'est la seule ligne de tout le site où de l'argent est réellement placé.
    Le bloc doit donc dire trois choses qu'aucune autre ne dit : où va
    l'argent, ce qu'il coûte, et ce qu'il devient si l'assuré meurt avant
    d'avoir liquidé. La dernière n'est pas un détail de présentation : c'est ce
    que la capitalisation donne et que la répartition ne donne pas, et c'est
    aussi ce qui explique qu'elle rapporte moins à rente égale.
    """
    liberal = comparaison.notionnel_liberal
    pilier = liberal.capitalisation
    if pilier is None:
        return ""

    parametres = comparaison.parametres
    taux = g.pourcentage(pilier.taux_cotisation, decimales=0)
    depart = comparaison.carriere.annee_liquidation

    if not pilier.actif:
        return g.depliant(
            f"Le pilier de capitalisation obligatoire : {taux} placés dès "
            f"{parametres.annee_debut_capitalisation}",
            f"""
<p>Cette carrière ne cotise pas au pilier : elle s'achève en {depart}, et la
cotisation capitalisée n'est due qu'à compter de
{parametres.annee_debut_capitalisation}. La proposition ne demande rien au
passé — ni ce taux, ni un autre —, et qui a liquidé avant la bascule reçoit
donc, du système 4, la seule pension de répartition.</p>""",
        )

    # Les trois frais sont des paramètres : les lire ici, et non les écrire en
    # dur, fait que changer le barème change la page.
    frais = comparaison.parametres
    premiere = pilier.annees[0]
    derniere = pilier.annees[-1]

    # Ce que devient un euro versé : la cascade complète, du prélèvement à la
    # rente. Chaque ligne est une opération, et la suivante part du résultat de
    # la précédente — c'est la seule façon de rendre un capital vérifiable.
    cascade = g.tableau(
        ["", "Ce qui se passe", f"Montant, en euros de {depart}"],
        [
            [f"a) Cotisation de {taux}",
             f"prélevée sur la même assiette que la cotisation notionnelle, "
             f"de {premiere.annee} à {derniere.annee}, EN PLUS d'elle",
             g.euros(pilier.versements)],
            ["b) − frais sur versement",
             f"{g.pourcentage(frais.frais_versement_capitalisation, decimales=2)} "
             "de chaque versement",
             "− " + g.euros(pilier.frais_versement)],
            ["c) + intérêts",
             "placés sur des titres sans risque, à des maturités qui "
             "raccourcissent à l'approche du départ",
             "+ " + g.euros(pilier.interets)],
            ["d) − frais de gestion",
             f"{g.pourcentage(frais.frais_gestion_capitalisation, decimales=2)} "
             "par an sur l'encours",
             "− " + g.euros(pilier.frais_gestion)],
            ["e) = capital au départ",
             "ce que vaut le compte le jour de la liquidation",
             g.euros(pilier.capital)],
            ["f) ÷ coefficient de conversion",
             f"{g.nombre(pilier.conversion.diviseur, DECIMALES_DIVISEUR)}, la "
             "même table de mortalité que la pension notionnelle",
             g.euros(pilier.capital / pilier.conversion.diviseur) + " par an"],
            ["g) − frais sur arrérages",
             f"{g.pourcentage(frais.frais_arrerages_capitalisation, decimales=2)} "
             "de chaque versement de rente",
             "− " + g.euros(pilier.capital / pilier.conversion.diviseur
                            - pilier.rente_annuelle) + " par an"],
            ["h) = rente servie", "à vie, et qui s'éteint avec le rentier",
             g.euros_centimes(pilier.rente_annuelle) + " par an"],
        ],
        ["", "", "nombre"],
        titre="D'un euro cotisé à un euro de rente",
        entete_de_ligne=True,
    )

    # L'échelle de maturités, telle qu'elle a effectivement servi : le premier
    # versement et le dernier. Deux lignes suffisent à montrer le glissement,
    # là où un tableau d'horizons théoriques demanderait au lecteur de croire
    # qu'il décrit sa carrière.
    def placements(annee) -> str:
        if not annee.placements:
            return "gardé disponible : le départ a lieu dans l'année"
        return ", ".join(
            f"{g.pourcentage(part / annee.versement_net)} à "
            f"{maturite} an{'s' if maturite > 1 else ''}"
            for maturite, part in annee.placements
        )

    echelle = g.tableau(
        ["Versement", "Années avant le départ", "Placé"],
        [
            [str(premiere.annee), f"{premiere.horizon}", placements(premiere)],
            [str(derniere.annee), f"{derniere.horizon}", placements(derniere)],
        ],
        ["", "nombre", ""],
        titre="Où va un versement, au début et à la fin de la carrière",
        entete_de_ligne=True,
    )

    transmission = f"""
<p><strong>Ce qui se transmet, et ce qui ne se transmet pas.</strong> Tant que
le compte n'est pas liquidé, il est un capital, et un décès le fait passer aux
héritiers : l'encours de l'année, tel que le relevé le porterait ce jour-là. À
la veille du départ, il vaudrait {g.euros(pilier.capital)}, le capital entier de
la ligne e) ; plus tôt dans la carrière, il vaudrait moins. Vu de
{pilier.annee_ouverture}, l'année où le pilier s'ouvre, la probabilité de mourir
avant d'avoir liquidé est de
{g.pourcentage(pilier.probabilite_deces_avant_liquidation)}, et l'espérance de
ce qui serait alors transmis de
{g.euros(pilier.esperance_capital_transmis)}. Après la liquidation, en revanche,
la rente est viagère : elle s'éteint avec le rentier, et rien n'est transmis.
C'est le prix de son montant, une rente qui se transmettrait étant plus
faible.</p>
<p>Le compte notionnel, lui, ne transmet rien à aucun moment : il n'est pas un
capital, il est un droit. C'est la différence de nature entre les deux lignes
du système 4, et elle ne se lit pas sur les montants.</p>"""

    if pilier.interets > 0:
        rendement = f"""
<p><strong>Ce que le pilier rapporte, frais compris :</strong>
{g.pourcentage(pilier.taux_rendement_annuel, decimales=2)} par an. C'est le
taux qui, appliqué aux versements aux mêmes dates, donnerait le même capital.
Les frais coûtent {g.euros(pilier.cout_des_frais)}, davantage que les
{g.euros(pilier.frais_preleves)} prélevés, parce que ce qui est prélevé ne
produit plus d'intérêts.</p>"""
    else:
        # Une carrière qui s'arrête l'année même de la bascule : le versement
        # est porté tel quel, sans une année devant lui. Parler de rendement
        # n'aurait pas de sens, et le taux affiché serait un artefact.
        rendement = f"""
<p><strong>Ce pilier n'a pas eu d'année pour rapporter :</strong> le seul
versement tombe l'année du départ, et il est porté tel quel. Seuls les
{g.euros(pilier.frais_preleves)} de frais sur versement le grèvent.</p>"""

    return g.depliant(
        f"Le pilier de capitalisation obligatoire : {taux} placés dès "
        f"{parametres.annee_debut_capitalisation}",
        f"""
<p>À compter de {parametres.annee_debut_capitalisation}, {taux} de la
rémunération sont prélevés <strong>en plus</strong> de la cotisation de
répartition, et placés. Ils ne passent pas par le compte notionnel : ils
constituent un capital, au nom du cotisant, dans un plan d'épargne retraite —
l'enveloppe qui existe déjà. Deux choses seulement l'en distinguent : la
cotisation est obligatoire, et l'argent n'en sort qu'à la retraite, sous forme
de rente, ou au décès, par l'héritage.{g.bulle(
    "Pourquoi ce n'est pas la même chose qu'une pension",
    "Une pension de répartition est un droit sur les cotisations des actifs de "
    "demain : elle ne dépend d'aucun marché, elle est revalorisée par une règle "
    "collective, et elle ne se lègue pas. Une rente capitalisée sort d'un "
    "capital réellement placé : elle dépend des taux du jour où l'argent a été "
    "placé, elle supporte des frais, et le capital se transmet tant qu'il n'a "
    "pas été converti en rente. Les deux sont additionnées sur la ligne du "
    "système 4, jamais confondues.")}</p>
{cascade}
{rendement}
{echelle}
{transmission}
<p class="discret">Les taux employés sont ceux de la courbe des titres
souverains les mieux notés de la zone euro, relevée le
{escape(_date_en_clair(pilier.date_courbe))} et publiée par la Banque centrale
européenne ; les versements des années suivantes emploient les taux à terme
que cette même courbe implique. Les trois frais sont les moyennes 2025 des
plans d'épargne retraite individuels, mesurées par l'Observatoire des produits
d'épargne financière. La page <a href="{g.lien("/methode/")}#capitalisation">Méthode</a>
dit ce que ces choix supposent, et la page <a href="{g.lien("/donnees/")}">Données</a>
d'où ils viennent. Fiabilité de ce compartiment :
<span class="etiquette-fiabilite">{escape(str(pilier.fiabilite))}</span>, le
barème de frais étant saisi et non recontrôlé.</p>""",
    )


def _garantie_vieillesse(comparaison: Comparaison, saisie: Saisie) -> str:
    """Ce que le système 4 change, et ce que l'impôt y paie.

    Deux choses, et le bloc les sépare. Le taux unique change ce que le compte
    reçoit : il se lit dans le capital, contre celui du système 3. La garantie
    vieillesse change ce qui est servi par-dessus : différentielle,
    individualisée, financée par l'impôt — et c'est elle que le tableau
    détaille, étape par étape, parce qu'elle est la seule ligne de toute la
    page qui ne vienne pas d'une cotisation.
    """
    liberal = comparaison.notionnel_liberal
    garantie = liberal.garantie_vieillesse
    if garantie is None:
        return ""
    parametres = comparaison.parametres
    annee = comparaison.carriere.annee_liquidation
    bascule = parametres.annee_bascule
    capital_4 = comparaison.notionnel_retroactif_employeur.capital_notionnel
    # Les années cotisées à 18 % : celles de la bascule au départ. Avant, le
    # compte est celui du système 3, et le capital ne s'en écarte pas.
    annees_18 = [c.annee for c in liberal.compte.cotisations
                 if c.annee >= bascule and not c.nulle]
    if annees_18:
        taux_unique = (
            f"Ici, les années {annees_18[0]} à {annees_18[-1]} sont cotisées à "
            f"{{taux}} ; celles d'avant {bascule} le sont aux taux réels, et le "
            f"capital vaut {g.euros(liberal.capital_notionnel)} contre "
            f"{g.euros(capital_4)} pour le système 3."
        )
    else:
        taux_unique = (
            f"Ici, la carrière s'achève avant {bascule} : aucune année n'est "
            f"cotisée à {{taux}}, et le compte est exactement celui du "
            f"système 3, {g.euros(liberal.capital_notionnel)}."
        )
    taux = g.pourcentage(parametres.taux_cotisation_liberal, decimales=0)
    base_mensuelle = parametres.garantie_vieillesse_mensuelle
    isolement_mensuel = parametres.allocation_isolement_mensuelle
    seul = garantie.situation == "seul"
    situation = "une personne seule" if seul else "une personne en couple"

    lignes = [
        ["a) Garantie de base",
         f"{g.euros(base_mensuelle)} par mois en euros de "
         f"{parametres.annee_euros_garantie_vieillesse}, soit "
         f"×{g.nombre(garantie.coefficient_prix, DECIMALES_FACTEUR)} en {annee}",
         g.euros_centimes(garantie.base_annuelle) + " par an"],
        ["b) + allocation d'isolement",
         f"{g.euros(isolement_mensuel)} par mois pour une personne seule, "
         + ("servie ici" if seul else "rien à deux"),
         g.euros_centimes(garantie.isolement_annuel) + " par an"],
        ["c) = plancher",
         f"ce qu'{situation} doit percevoir au minimum",
         g.euros_centimes(garantie.plancher_annuel) + " par an"],
        ["d) Pension contributive",
         f"le compte notionnel du système 4 — taux réels avant {bascule}, "
         f"{taux} pour tous ensuite — divisé par "
         f"{g.nombre(liberal.conversion.diviseur, DECIMALES_DIVISEUR)}",
         g.euros_centimes(garantie.pension_contributive) + " par an"],
        ["e) + rente du pilier obligatoire",
         "les 5 % capitalisés : la garantie regarde l'ensemble de la pension "
         "obligatoire, pas la seule répartition",
         g.euros_centimes(garantie.rente_capitalisee) + " par an"],
        ["f) = ressources examinées", "d + e",
         g.euros_centimes(garantie.ressources) + " par an"],
    ]
    if not garantie.age_atteint:
        lignes.append([
            f"f′) ressources en {garantie.annee_ouverture}",
            "la pension notionnelle est revalorisée sur la masse salariale, le "
            "plancher sur les prix comme l'ASPA : l'écart entre les deux se "
            f"réduit de {g.pourcentage(garantie.revalorisation_differee - 1.0)} "
            "d'ici l'ouverture",
            g.euros_centimes(garantie.ressources_a_l_ouverture) + " par an",
        ])
    reference = "f" if garantie.age_atteint else "f′"
    lignes += [
        ["g) Garantie vieillesse",
         f"max(0, c − {reference}), financée par l'impôt, servie à partir de "
         "65 ans"
         + ("" if garantie.age_atteint
            else f" — soit ici à compter de {garantie.annee_ouverture}"),
         g.euros_centimes(garantie.complement) + " par an"],
        ["h) = pension du système 4",
         "d + g dès le départ" if garantie.age_atteint
         else f"d seul jusqu'à 65 ans, puis d + g à partir de {garantie.annee_ouverture}",
         g.euros_centimes(liberal.pension_annuelle) + " par an"],
    ]

    if garantie.servie_a_la_liquidation:
        lecture = (
            f"<p>Ici, la pension obligatoire de "
            f"{g.euros_centimes(garantie.ressources / 12)} par mois "
            f"reste sous le plancher de {g.euros_centimes(garantie.plancher_annuel / 12)} : "
            f"l'impôt en finance <strong>{g.euros_centimes(garantie.complement / 12)} "
            f"par mois</strong>, soit {g.pourcentage(garantie.complement / liberal.pension_annuelle)} "
            "de ce que le système 4 verse.</p>"
        )
    elif garantie.differee:
        lecture = (
            f"<p>Ici, la liquidation a lieu à "
            f"{_age(comparaison.carriere.age_liquidation or 0.0)}, avant les 65 ans "
            f"de l'allocation : rien n'est servi jusqu'en "
            f"{garantie.annee_ouverture}. À partir de là, la pension "
            f"obligatoire — {g.euros_centimes(garantie.ressources / 12)} par "
            f"mois au départ, "
            f"{g.euros_centimes(garantie.ressources_a_l_ouverture / 12)} à "
            "l'ouverture, parce qu'elle suit la masse salariale quand le "
            "plancher suit les prix — reste sous le plancher de "
            f"{g.euros_centimes(garantie.plancher_annuel / 12)} : l'impôt en "
            f"finance <strong>{g.euros_centimes(garantie.complement / 12)} par "
            "mois</strong>. Le montant affiché plus haut est celui du départ, "
            "sans la garantie.</p>"
        )
    else:
        lecture = (
            f"<p>Ici, la pension obligatoire de "
            f"{g.euros_centimes(garantie.ressources / 12)} par mois "
            f"dépasse le plancher de {g.euros_centimes(garantie.plancher_annuel / 12)} : "
            "la garantie ne sert rien, et le système 4 est un compte notionnel "
            "à taux unique, sans plus.</p>"
        )

    # Le tableau de la proposition, recalculé avec la règle du scénario — en
    # euros mensuels de l'année où la proposition fixe ses montants, sans
    # l'âge : il illustre le mécanisme, pas cette carrière.
    plancher_seul = base_mensuelle + isolement_mensuel
    exemples = []
    for pensions, libelle in EXEMPLES_GARANTIE:
        plancher = plancher_seul if len(pensions) == 1 else base_mensuelle
        aides = [max(0.0, plancher - pension) for pension in pensions]
        detail = " + ".join(g.euros(aide) for aide in aides) if len(aides) > 1 else ""
        exemples.append([
            libelle,
            g.euros(sum(aides)),
            detail if detail else "—",
        ])

    return g.depliant(
        "Le système 4 : un taux pour tous, et une garantie payée par l'impôt",
        f"""
<p>La garantie vieillesse, étape par étape, en euros de {annee} — l'année du
départ.{g.bulle(
    "Ce que le système 4 change au système 3",
    "Il est le système 3 — même compte rétroactif, cotisation salariale et "
    "patronale confondues, mêmes âges, même indexation, même liquidation — à "
    f"deux différences près. La première : à compter de {bascule}, un taux "
    f"unique de {taux}, parts salariale et patronale additionnées, le même "
    "pour tous les statuts, prélevé une fois sur la rémunération. Ce qui a été "
    f"cotisé avant {bascule} reste porté au compte tel qu'il a été prélevé, "
    "aux taux réels de chaque régime : sur ces années-là, le 6 est le 4. "
    + taux_unique.format(taux=taux) +
    " La seconde : une garantie vieillesse qui remplace l'ASPA.",
)}</p>
{g.tableau(
    ["Étape", "Ce qu'elle fait", "Résultat"],
    lignes,
    ["", "", "nombre"],
    titre=f"La garantie vieillesse du système 4, étape par étape, en euros de {annee}",
    entete_de_ligne=True,
)}
{lecture}
<p>Ce que la garantie sert à un foyer, en euros de
{parametres.annee_euros_garantie_vieillesse} et par mois.{g.bulle(
    "Ce qui la sépare de l'ASPA",
    "Un mot : elle est <strong>individualisée</strong>. L'ASPA regarde les "
    "ressources du foyer, et son plafond de couple n'est pas le double de "
    "celui d'une personne seule ; la garantie compare chacun à son propre "
    f"plancher — {g.euros(base_mensuelle)} par mois, plus "
    f"{g.euros(isolement_mensuel)} d'allocation d'isolement pour qui vit seul "
    "— sans jamais regarder la pension du conjoint.",
)}</p>
{g.tableau(
    ["Pensions des deux personnes", "Aide totale du foyer", "Détail"],
    exemples,
    ["", "nombre", ""],
    titre="Ce que la garantie individualisée sert à un foyer, selon les deux pensions",
    entete_de_ligne=True,
)}
<p class="discret">Garantie calculée ici pour {situation}.{g.bulle(
    "Comment la garantie est financée",
    "Par l'<strong>impôt</strong>, non par les cotisations : la page Coût la "
    "sort du compte des cotisants et la compte à part. Elle garde de l'ASPA "
    "son âge — 65 ans — et sa place, une ligne servie en dernier, après la "
    "pension contributive. L'option « situation de foyer » du formulaire ne "
    "change qu'une chose : l'allocation d'isolement.",
)}</p>""")


def _euros_signe(montant: float, centimes: bool = True) -> str:
    """Un montant qui est un ÉCART : il se lit avec son signe, positif compris."""
    signe = "+" if montant > 0 else ""
    ecrit = g.euros_centimes(montant) if centimes else g.euros(montant)
    return f"{signe}{ecrit}"


@dataclass(frozen=True)
class Montants:
    """Le mode net/brut, et ce qu'il fait à chaque montant affiché.

    Un seul objet, construit une fois par rendu, pour que la bascule n'existe
    qu'à un endroit. Deux grandeurs n'ont pas le même barème — un salaire
    supporte des cotisations, une pension n'en supporte plus — et deux autres
    n'ont pas de net du tout : un CAPITAL notionnel et une ASSIETTE de
    cotisation sont bruts par nature, et le site les laisse tels quels.
    """

    net: bool
    #: Ce qui sépare une pension brute de sa nette : CSG 8,30 %, CRDS 0,50 %,
    #: CASA 0,30 %. Voir ``remuneration.PrelevementsPension``.
    taux_pension: float

    @classmethod
    def depuis(cls, saisie: Saisie, base: Parametres) -> "Montants":
        pensions = charger_prelevements(base.racine_donnees).pensions
        return cls(net=saisie.en_net, taux_pension=pensions.taux_total)

    def pension(self, brut: float) -> float:
        """Une pension, une rente, une garantie : tout ce qui se sert après."""
        return brut * (1.0 - self.taux_pension) if self.net else brut

    def salaire(self, fiche) -> float:
        """Un salaire, lu sur la fiche de paie qui porte déjà les deux."""
        return fiche.net if self.net else fiche.brut

    @property
    def mot(self) -> str:
        return "net" if self.net else "brut"

    @property
    def unite_salaire(self) -> str:
        return "€ net/mois" if self.net else "€ brut/mois"

    @property
    def unite_pension(self) -> str:
        return "€ net/mois" if self.net else "€ brut/mois"


def _note_du_mode(montants: "Montants") -> str:
    """Ce que le mode courant suppose, en une phrase, là où il s'applique.

    En NET, c'est la convention de CSG qu'il faut dire : la loi fait dépendre
    le taux du revenu fiscal du foyer, que le simulateur ne demande pas, et le
    dépôt retient le taux plein. En BRUT, c'est le rappel qu'un brut n'est pas
    ce qu'on touche.
    """
    if montants.net:
        return (
            "La pension est nette de "
            f"{g.pourcentage(montants.taux_pension, decimales=1)} : CSG, CRDS "
            "et contribution de solidarité, au <strong>taux plein</strong>. La "
            "loi fait dépendre ce taux du revenu fiscal du foyer, que ce "
            "simulateur ne demande pas : une petite pension, exonérée en "
            "réalité, est donc ici un peu sous-estimée."
        )
    return ("Le brut n'est pas ce qui arrive sur le compte : il reste à en "
            "retirer les cotisations pour un salaire, la CSG pour une pension.")


def _mention_conversion(saisie: Saisie, echelle: "Echelle") -> str:
    """Le statut dont le modèle ne sait pas faire la fiche de paie, s'il y en a.

    L'exploitant agricole relève de la MSA, l'élu touche une indemnité de
    fonction, l'ultramarin a la caisse de sa collectivité : leurs prélèvements
    hors retraite ne sont pas dans le dépôt. Le nombre saisi est alors lu comme
    un brut, et l'affichage reste brut pour la partie salaire. Le taire ferait
    croire à une conversion qui n'a pas eu lieu.
    """
    if not saisie.saisie_en_net:
        return ""
    sans = [ligne.statut for ligne in saisie.lignes_carriere
            if not ligne.sans_emploi and not echelle.convertit(ligne.statut)]
    if not sans:
        return ""
    return ('<p class="note avertissement" style="margin-top:0.6rem">'
            + g.icone("triangle-alert", "Avertissement")
            + "<span>Le modèle ne connaît pas les prélèvements hors retraite "
            "de l'un de vos statuts : pour lui, le montant saisi est lu "
            "<strong>tel quel</strong>, comme un brut. La pension, elle, reste "
            "affichée en net.</span></p>")


def _bascule_montants(saisie: Saisie, echelle: "Echelle",
                      ancre: str = "") -> str:
    """Le lien qui passe de net à brut, et retour — montants déjà traduits.

    Un lien plutôt qu'un menu, pour la même raison que la bascule d'unité : il
    porte l'adresse entière, si bien que l'adresse se partage telle qu'on la
    lit, et cela ne demande pas une ligne de JavaScript.

    LES MONTANTS SAISIS SONT TRADUITS, et c'est tout l'enjeu : en mode net, le
    nombre du formulaire est un net. Le recopier tel quel dans l'autre mode le
    ferait relire comme un brut, et la page reviendrait en décrivant une AUTRE
    carrière — mieux payée d'un quart. Le lien porte donc le montant converti,
    métier par métier, exactement comme le fait la bascule d'unité.
    """
    vers_le_net = not saisie.en_net
    autre = "net" if vers_le_net else "brut"
    remplacements: dict[str, object] = {"montants": autre}
    # Seule la saisie EN EUROS porte un net ou un brut : un multiple du salaire
    # moyen est un rapport entre deux bruts, que le mode ne touche pas.
    if saisie.revenu_en_euros:
        lignes = saisie.lignes_carriere
        traduits = [
            _nombre(round(echelle.net_mensuel(ligne.salaire, ligne.statut)
                          if vers_le_net
                          else echelle.brut_mensuel_direct(ligne.salaire,
                                                           ligne.statut)))
            for ligne in lignes
        ]
        remplacements["salaire"] = traduits[0]
        for rang, valeur in enumerate(traduits[1:], start=2):
            remplacements[f"metier{rang}_salaire"] = valeur
    libelle = ("Voir les montants en net" if vers_le_net
               else "Voir les montants en brut")
    cible = f"#/simuler?{escape(saisie.requete(**remplacements))}"
    if ancre:
        cible += ancre
    return (f'<p class="discret" style="margin:0.9rem 0 0">'
            f'<a href="{cible}">{libelle}</a></p>')


def _salaire_net(comparaison: Comparaison, saisie: Saisie) -> str:
    """Ce qu'un actif touche PENDANT qu'il cotise, dans les deux systèmes.

    Le reste de la page compare des pensions, c'est-à-dire des montants qu'on
    touchera dans trente ans. Ce bloc compare des salaires, c'est-à-dire des
    montants qu'on touche le mois prochain — et c'est la seule ligne du site où
    une réforme des retraites se lit sur une fiche de paie.

    Il ne s'affiche pas pour tout le monde : un retraité ne cotise plus, et
    quatre familles de statut n'ont pas les taux hors retraite du régime général
    — la MSA, l'outre-mer, les élus, et qui n'a pas d'emploi. Hors de ces deux
    cas, il n'y a rien à montrer, et mieux vaut ne rien montrer qu'un net faux.

    QUATRE PROFILS, ET UN LIBELLÉ PAR PROFIL. Ce qui s'écrit « salaire » pour un
    salarié du privé s'écrit « traitement » pour un fonctionnaire et « revenu
    professionnel » pour un indépendant ; et la ligne « coût du travail » ne
    s'affiche que là où ce que verse l'employeur est un prix du travail, non un
    taux d'équilibre. ``remuneration.py`` porte la décision, ce bloc l'écrit.

    TROIS CHIFFRES OUVERTS, LE RESTE REPLIÉ. La page de résultats tient un
    budget de mots et n'ouvre aucun tableau : ce bloc s'y plie. Le net
    d'aujourd'hui, celui de la proposition, l'écart — puis la fiche de paie
    entière, ligne à ligne, pour qui déplie.
    """
    remuneration = comparaison.remuneration
    if remuneration is None:
        return ""
    reference = remuneration.reference
    avant, apres = reference.droit_en_vigueur, reference.proposition
    gain = remuneration.gain_net_mensuel
    net = escape(remuneration.libelle_net.lower())

    ouverture = "".join([
        g.fiche(f"votre {net} en {reference.annee}",
                g.euros_centimes(avant.net / 12.0)),
        g.fiche("avec le système 4", g.euros_centimes(apres.net / 12.0)),
        g.fiche("par mois", _euros_signe(gain)),
    ])
    sens = "de plus" if gain >= 0 else "de MOINS"
    duree = len(remuneration.annees)
    cumul = remuneration.gain_net_cumule
    reste = (
        f" Sur les {duree} années qui vous séparent de la retraite : "
        f"{_euros_signe(cumul, centimes=False)} en euros de {saisie.euros}."
        if duree > 1 else ""
    )
    # Deux hypothèses, et il faut dire laquelle vaut ici : le coût du travail
    # tenu fixe quand l'employeur verse des taux de droit commun, l'assiette
    # tenue fixe quand il verse un taux d'équilibre — ou qu'il n'y en a pas.
    if remuneration.affiche_cout_du_travail:
        sous_quelle_hypothese = "à coût du travail inchangé pour votre employeur"
    else:
        sous_quelle_hypothese = (
            f"à {escape(remuneration.libelle_assiette.lower())} inchangé")
    return f"""
<h2 id="salaire-net">Et pendant que vous cotisez</h2>
<p class="chapeau">Une réforme des retraites ne change pas que votre pension :
elle change ce qui est prélevé sur votre travail, donc ce que vous touchez
chaque mois. Les systèmes 1, 2 et 3 prélèvent la même chose — ils ne changent
que ce qui est porté au compte. Le système 4, lui, y touche.</p>
<div class="carte">
  <div class="fiches">{ouverture}</div>
  <p>Soit <strong>{_euros_signe(gain)} {sens} sur votre fiche de paie</strong>,
  {sous_quelle_hypothese}.{reste}</p>
  {_salaire_net_detail(comparaison, remuneration, saisie)}
</div>"""


def _salaire_net_detail(comparaison: Comparaison, remuneration,
                        saisie: Saisie) -> str:
    """La fiche de paie entière, et ce qu'il faut savoir pour la discuter."""
    reference = remuneration.reference
    avant, apres = reference.droit_en_vigueur, reference.proposition

    def mois(montant: float) -> str:
        return g.euros_centimes(montant / 12.0)

    # TROIS COLONNES, ET NON QUATRE. Une colonne « écart » de plus forçait le
    # tableau à défiler latéralement sur un téléphone, et l'écart qui compte —
    # celui du net — est déjà le chiffre de tête. Les deux autres se lisent
    # sous le tableau, en une phrase.
    #
    # LA PREMIÈRE LIGNE N'EST PAS TOUJOURS LÀ. Le coût du travail suppose de
    # savoir ce que l'employeur verse ; quand ce qu'il verse est un taux
    # d'équilibre — 82,28 % du traitement pour l'État en 2026 —, ce n'est pas un
    # prix du travail, et l'afficher tromperait. Le tableau se réduit alors à ce
    # que l'assuré voit vraiment : son assiette et son net.
    avec_cout = remuneration.affiche_cout_du_travail
    assiette = escape(remuneration.libelle_assiette)
    libelle_net = escape(remuneration.libelle_net)
    lignes = []
    if avec_cout:
        # Le mot s'affiche avec sa capitale, comme les autres intitulés de
        # ligne, mais renvoie à la même entrée du glossaire.
        lignes.append([g.terme("Coût du travail", "coût du travail"),
                       mois(avant.cout_du_travail), mois(apres.cout_du_travail)])
    # Ce qu'on met sous « dont pour la retraite » suit la même logique : les deux
    # parts réunies quand la colonne part d'un coût du travail, la seule part de
    # l'assuré quand elle part de son assiette — sans quoi la ligne compterait
    # une part patronale que le reste du tableau ignore.
    retraite_avant = avant.retraite_totale if avec_cout else avant.retraite_salarie
    retraite_apres = apres.retraite_totale if avec_cout else apres.retraite_salarie
    lignes += [
        [assiette, mois(avant.brut), mois(apres.brut)],
        [f"<strong>{libelle_net}</strong>",
         f"<strong>{mois(avant.net)}</strong>",
         f"<strong>{mois(apres.net)}</strong>"],
        ["Dont pour la retraite" if avec_cout
         else "Dont pour la retraite, à votre charge",
         mois(retraite_avant), mois(retraite_apres)],
        ["Ce qui vous arrive, sur 100 € coûtés" if avec_cout
         else f"Ce qui vous reste, sur 100 € de {assiette.lower()}",
         g.pourcentage(avant.part_qui_arrive if avec_cout
                       else avant.net / avant.brut),
         g.pourcentage(apres.part_qui_arrive if avec_cout
                       else apres.net / apres.brut)],
    ]
    grille = g.tableau(
        ["Par mois", "Systèmes 1 à 3", "Système 4"],
        lignes, ["", "nombre", "nombre"],
        # Pas d'`escape` ici : `g.tableau` échappe déjà son titre. Le doubler
        # ne se voyait pas tant que le seul statut couvert était « Salarié du
        # secteur privé » ; « Fonctionnaire titulaire de l'État » a une
        # apostrophe, et elle sortait en `&amp;#x27;`.
        titre=f"Votre fiche de paie en {reference.annee}, sous les quatre "
              f"systèmes — {remuneration.libelle_statut}",
        entete_de_ligne=True,
    )
    if avec_cout:
        lecture = (
            f"<p>Le coût du travail ne bouge pas : c'est l'hypothèse. Le "
            f"prélèvement retraite, lui, passe de {mois(retraite_avant)} à "
            f"{mois(retraite_apres)} par mois, soit "
            f"<strong>{_euros_signe((retraite_apres - retraite_avant) / 12.0)}"
            f"</strong> ; le salaire brut monte de "
            f"{_euros_signe((apres.brut - avant.brut) / 12.0)}, et le net de "
            f"{_euros_signe((apres.net - avant.net) / 12.0)}.</p>"
        )
    else:
        lecture = (
            f"<p>Le {assiette.lower()} ne bouge pas : c'est l'hypothèse, et ici "
            f"c'est la seule disponible. Ce que vous versez pour votre retraite "
            f"passe de {mois(retraite_avant)} à {mois(retraite_apres)} par mois, "
            f"soit <strong>"
            f"{_euros_signe((retraite_apres - retraite_avant) / 12.0)}</strong> ; "
            f"votre net bouge donc de "
            f"{_euros_signe((apres.net - avant.net) / 12.0)}.</p>"
        )

    alerte = ""
    if remuneration.bute_sur_le_smic:
        alerte = (
            '<p class="note avertissement">'
            + g.icone("triangle-alert", "Avertissement")
            + "<span>À ce niveau de salaire, le calcul ci-dessus suppose un "
            "salaire brut <strong>inférieur au SMIC</strong>, ce que la loi "
            "interdit. Dans la réalité, c'est le coût du travail qui monterait, "
            "et non le salaire qui baisserait : l'emploi coûterait plus cher à "
            "l'employeur, pour un net inchangé.</span></p>"
        )

    return g.depliant("Votre fiche de paie, ligne à ligne", f"""
{grille}
{lecture}
{alerte}
{_salaire_net_epargne(reference.epargne_a_votre_nom / 12.0, remuneration,
                      comparaison.parametres, saisie)}
{_salaire_net_methode(comparaison, remuneration)}""")


def _salaire_net_epargne(epargne: float, remuneration,
                        parametres: Parametres, saisie: Saisie) -> str:
    """Les cinq points capitalisés : prélevés sur le net, mais acquis à l'assuré.

    Les compter dans le gain serait faux — ils ne tombent pas sur le compte en
    banque. Les passer sous silence le serait aussi : contrairement à une
    cotisation, ce que ce prélèvement achète reste au nom de l'assuré et se
    transmet. Ils sont donc à part, et dits.
    """
    if epargne <= 0:
        return ""
    taux = g.pourcentage(parametres.taux_capitalisation_obligatoire, decimales=0)
    repartition = g.pourcentage(parametres.taux_cotisation_liberal, decimales=0)
    return (
        f'<p class="note resume"><strong>{g.euros_centimes(epargne)} par mois '
        "de ce prélèvement est de l'épargne à votre nom.</strong> Le système 4 "
        f"prélève {taux} par-dessus les {repartition} de répartition, et ces "
        "cinq points ne partent pas : ils alimentent un compte qui reste le "
        "vôtre, transmissible à vos héritiers tant qu'il n'est pas liquidé — "
        f"{g.euros(remuneration.epargne_cumulee)} d'ici votre départ, en euros "
        f"de {saisie.euros}. "
        + ("Sans eux, le salaire net monterait à tous les niveaux de salaire ; "
           "avec eux, il baisse au voisinage du SMIC."
           if remuneration.affiche_cout_du_travail
           else "Sans eux, le chiffre du haut remonterait de la part que vous "
                "en supportez : ce que vous perdez en net, vous le retrouvez "
                "sur ce compte.")
        + "</p>"
    )


def _salaire_net_methode(comparaison: Comparaison, remuneration) -> str:
    """Ce qu'il faut savoir pour discuter le chiffre plutôt que le croire.

    Le premier paragraphe est celui qui change d'un profil à l'autre, et c'est
    le plus important : il dit ce que le modèle tient FIXE, et pourquoi il n'a
    pas le choix quand l'employeur verse un taux d'équilibre.
    """
    parametres = comparaison.parametres
    part = parametres.part_salariale_taux_unique
    assiette = escape(remuneration.libelle_assiette.lower())
    return f"""
<h3>Comment ce chiffre est calculé, et ce qu'il suppose</h3>
{_salaire_net_incidence(remuneration, assiette)}
{_salaire_net_partage(remuneration, parametres, part)}
{_salaire_net_allegement(remuneration)}
{_salaire_net_perimetre(remuneration)}
<p class="discret">Taux hors retraite : millésime {remuneration.millesime_bareme},
appliqué tel quel aux années à venir — le modèle ne prévoit pas la prochaine loi
de financement. Fiabilité : {escape(str(remuneration.fiabilite))}. Les taux de
retraite, eux, sont ceux des fiches de régime : la fiche de paie prélève
exactement ce que le compte notionnel encaisse.</p>"""


def _salaire_net_incidence(remuneration, assiette: str) -> str:
    """Ce que le modèle tient fixe — et, pour le public, pourquoi il le doit.

    C'est la décision que ce bloc a demandée, et elle est écrite sur la page
    plutôt que dans un fichier : la contribution d'un employeur public est un
    taux d'ÉQUILIBRE, pas un prix du travail, et l'incidence intégrale posée
    dessus donnerait un gain qui n'existe pas.
    """
    if remuneration.affiche_cout_du_travail:
        return """<p><strong>Le coût du travail est tenu fixe.</strong> C'est ce que votre
employeur a budgété pour votre poste, et aucune réforme des retraites ne le
change. Ce qu'il ne verse plus en cotisations, il le verse en salaire : le brut
monte, et le net avec lui. C'est ce que veut dire « réduire l'écart entre le net
et le brut », et c'est l'hypothèse la plus favorable à une baisse de cotisation
— une cotisation patronale est du salaire différé, mais rien n'oblige un
employeur à le rendre du jour au lendemain.</p>"""
    if remuneration.profil == "independant":
        return f"""<p><strong>Votre {assiette} est tenu fixe, et il n'y a pas de coût du
travail à afficher</strong> : vous n'avez pas d'employeur, et votre cotisation
est intégralement personnelle. Ce qu'une baisse de taux vous rend vous revient
donc en entier, sans qu'il faille supposer qui que ce soit pour le répercuter —
c'est le seul des quatre profils où l'incidence n'est pas une hypothèse.
L'assiette retenue est l'assiette sociale unique : votre revenu professionnel
après l'abattement de 26 %, qui sert depuis 2025 aux cotisations comme à la
CSG.</p>"""
    return f"""<p><strong>Votre {assiette} est tenu fixe, et le site n'affiche pas de
coût du travail pour votre statut.</strong> Ce n'est pas un oubli, c'est un
refus. Ce que verse votre employeur n'est pas le prix de votre travail mais un
<strong>taux d'équilibre</strong> — jusqu'à 82,28 % du traitement pour l'État en
2026 —, fixé pour que le compte « Pensions » tombe juste, c'est-à-dire pour
payer les pensions d'aujourd'hui, et non parce que vous acquerriez 82 % de votre
traitement en droits nouveaux. Le traiter comme un coût du travail et supposer
qu'une baisse vous reviendrait en salaire afficherait une augmentation de
soixante-dix points qui n'existe pas : cette contribution finance une dette de
pensions qui, elle, reste à payer. C'est la page <a href="{g.lien("/cout")}">Coût</a>
qui en traite.</p>
<p>Le chiffre ci-dessus est donc la lecture <strong>prudente</strong> : seule la
part que vous supportez bouge. Il n'est pas comparable, terme à terme, au gain
d'un salarié du privé, dont le site fait remonter la part patronale dans le
brut.</p>"""


def _salaire_net_partage(remuneration, parametres, part: float) -> str:
    """Le partage des 18 %, et ce qu'il pèse — ou ne pèse pas, sans employeur."""
    repartition = g.pourcentage(parametres.taux_cotisation_liberal, decimales=0)
    capitalise = g.pourcentage(
        parametres.taux_capitalisation_obligatoire, decimales=0)
    if remuneration.profil == "independant":
        return f"""<p><strong>Les {repartition} et les {capitalise} capitalisés sont à votre
charge en entier.</strong> La proposition les annonce « salariale et patronale
additionnées » ; vous êtes les deux à la fois, comme vous l'êtes déjà des
vingt-six points que vous versez aujourd'hui. Vous prêter un employeur pour la
moitié de la charge fabriquerait un gain qui n'existe pas.</p>"""
    if not remuneration.affiche_cout_du_travail:
        return f"""<p><strong>Les {repartition} sont partagés moitié-moitié</strong> entre
vous et votre employeur, comme les {capitalise} capitalisés : votre part est
donc de {g.pourcentage(part, decimales=0)} de chacun. La proposition ne dit pas
qui porte quoi, et ce partage commande directement le chiffre ci-dessus —
puisque seule votre part y figure, tout déplacer vers l'employeur ferait
disparaître la hausse, et tout déplacer vers vous la doublerait.</p>"""
    return f"""<p><strong>Les {repartition}
sont partagés moitié-moitié</strong> entre vous et votre employeur, comme les
{capitalise}
capitalisés. La proposition ne dit pas qui porte quoi, et ce partage n'est pas
neutre : la CSG est assise sur le brut, et l'allègement sur les bas salaires ne
porte que sur la part patronale. Tout mettre côté employeur donnerait un gain
bien plus gros, tout mettre côté salarié le rendrait négatif. Le chiffre affiché
est le partage du milieu ({g.pourcentage(part, decimales=0)} pour vous).</p>"""


def _salaire_net_allegement(remuneration) -> str:
    """L'allègement sur les bas salaires — quand il s'applique, et sinon pourquoi."""
    if remuneration.affiche_cout_du_travail:
        return """<p><strong>L'allègement sur les bas salaires est calculé, pas ignoré.</strong>
Depuis 2026, il efface au niveau du SMIC la totalité des cotisations patronales
qu'il vise — son coefficient, 40,21 %, est exactement leur somme — et s'éteint à
trois SMIC. Conséquence, et elle va à contre-courant : <strong>au SMIC, baisser
la cotisation retraite de l'employeur ne rend rien</strong>, puisqu'il n'en
versait déjà plus. La loi fixe ce coefficient « dans la limite de la somme des
taux » du périmètre ; le modèle refait donc l'addition sous la proposition au
lieu de garder le chiffre d'aujourd'hui.</p>"""
    return """<p><strong>L'allègement sur les bas salaires ne joue pas ici.</strong> La
réduction générale de l'article L. 241-13 n'efface que des cotisations
patronales du régime général ; elle ne s'applique ni à la retenue d'un
fonctionnaire, ni aux cotisations personnelles d'un indépendant. C'est pourtant
elle qui commande le résultat d'un salarié du privé, chez qui elle rend nul, au
voisinage du SMIC, le gain d'une baisse de cotisation patronale — une raison de
plus de ne pas comparer les deux chiffres sans précaution.</p>"""


def _salaire_net_perimetre(remuneration) -> str:
    """Ce que la fiche ne porte pas, et qui n'est pas le même selon le profil."""
    if remuneration.profil == "independant":
        return """<p><strong>Ce que la fiche ne porte pas</strong> : la contribution à la
formation professionnelle, qui est un forfait de 0,25 % du plafond et non un
taux, et l'assiette minimale que la loi impose aux très bas revenus — le net
affiché en bas de barème est donc un plafond. Vos cotisations de retraite sont
celles des fiches de régime, qui alignent l'artisan et le commerçant sur le
régime général : c'est la convention du modèle entier, et elle vaut ici comme
pour la pension.</p>"""
    if not remuneration.affiche_cout_du_travail:
        return """<p><strong>Ce que la fiche ne porte pas</strong> : la retraite
additionnelle de la fonction publique, assise sur les PRIMES, que l'assiette de
ce modèle — le traitement indiciaire brut et la nouvelle bonification
indiciaire — exclut par construction. Un agent dont les primes pèsent lourd voit
donc ici une fraction de sa rémunération, et non sa feuille de paie entière. Les
autres prélèvements salariaux sont nuls, et c'est un résultat : la cotisation
maladie salariale a disparu en 2018 comme dans le privé, un titulaire n'est pas
assuré contre le chômage, et la contribution exceptionnelle de solidarité de 1 %
a été supprimée la même année.</p>"""
    return """<p><strong>Ce que la fiche ne porte pas</strong> : la taxe
d'apprentissage, la formation professionnelle, la participation à la
construction, le versement mobilité, la prévoyance et la mutuelle d'entreprise.
Aucune ne bouge d'un système à l'autre, et plusieurs dépendent de la commune ou
de la taille de l'entreprise. Le coût du travail affiché est donc un plancher.
L'employeur type est une entreprise de cinquante salariés et plus.</p>"""


def _decomposition(contexte: Contexte, saisie: Saisie,
                   comparaison: Comparaison) -> str:
    """Sépare l'effet de la règle d'indexation de celui des comptes notionnels.

    Le tableau ne s'affiche que sur la règle par défaut : ailleurs, l'utilisateur
    a lui-même choisi sa ligne de comparaison, et la première ligne du tableau ne
    serait plus celle qu'il regarde. Le défaut est lu sur la saisie, non écrit
    ici : ce test a nommé « triple_lock_inverse » en dur jusqu'à ce que le défaut
    change, et le tableau aurait alors disparu de la page de simulation.
    """
    if saisie.indexation != Saisie.indexation:
        return ""

    loterie = _loterie_de_cohorte(contexte)
    lignes = []
    for code, libelle in INDEXATIONS:
        try:
            variante = (comparaison if code == saisie.indexation
                        else contexte.simuler(Saisie(**{**saisie.__dict__,
                                                        "indexation": code})))
        except (ErreurSaisie, DonneeInsuffisante, KeyError, ValueError):
            continue
        mensuel = variante.en_euros_constants(
            variante.notionnel_retroactif.pension_annuelle
        ) / 12
        lignes.append([
            escape(libelle),
            "×" + g.nombre(variante.notionnel_retroactif.compte.rendement_cumule, 2),
            g.euros_centimes(mensuel),
            g.pourcentage(variante.variation("notionnel_retroactif"), signe=True),
        ])

    return g.depliant("D'où vient l'écart", f"""
<p>La même carrière, le même calcul notionnel rétroactif, sous neuf règles de
revalorisation. La colonne « rendement » est le facteur par lequel les
cotisations ont été multipliées entre leur versement et la liquidation.{g.bulle(
    "Ce que chaque règle de revalorisation vaut",
    "La <strong>première ligne est celle que la simulation applique</strong> : "
    "la croissance de la masse salariale, c'est-à-dire le rendement qu'un "
    "système en répartition peut servir sans changer son taux de cotisation. "
    "C'est la seule règle du tableau qui repose sur un argument théorique et "
    "non sur un choix, et la plus généreuse — elle vaut salaire moyen + emploi "
    "salarié, et l'emploi salarié a doublé depuis 1950. Son incohérence, à "
    "garder en tête : elle crédite le compte du rendement que le système "
    "ENTIER dégage, quand le système 2 n'y verse que la part "
    "salariale ; c'est au système 3 qu'elle se compare sans biais. La "
    "deuxième ligne n'est pas une hypothèse mais un relevé — le coefficient "
    "que les arrêtés ont réellement appliqué, celui dont le système 1 se "
    "sert : l'écart entre elle et le système actuel mesure l'effet propre des "
    "comptes notionnels, et tout ce qui sépare les autres lignes de celle-là "
    "mesure l'effet de la règle. Le triple lock inversé compare deux taux "
    "nominaux à un taux réel : dès que l'inflation dépasse la productivité — "
    "presque toute la période 1945-1985 — c'est la productivité qui l'emporte, "
    "et la valeur réelle des comptes s'effondre.",
)}</p>
{g.tableau(
    ["Règle d'indexation", "Rendement cumulé",
     f"Pension mensuelle, en euros de {saisie.euros}",
     "Écart au système actuel"],
    lignes,
    ["", "nombre", "nombre", "nombre"],
    titre="Ce que la même carrière donne sous chaque règle d'indexation",
    entete_de_ligne=True,
)}
<p class="discret">Le <strong>lissage</strong>, dans les options, s'applique à
toutes ces lignes à la fois.{g.bulle(
    "Ce que le lissage vise",
    "Il applique une moyenne glissante au taux que la règle produit, quelle "
    "qu'elle soit. Ce qu'il vise n'est pas le niveau mais la loterie de "
    "cohorte : sur le PIB nominal brut, une cotisation de "
    f"{ANNEE_COTISATION_LOTERIE} vaut {loterie['1|2019']} à une liquidation de "
    f"2019 et {loterie['1|2020']} en 2020 — attendre un an fait perdre, parce "
    "que l'année traversée s'est mal passée. Lissée sur cinq ans, la même "
    f"cotisation vaut {loterie['5|2019']} puis {loterie['5|2020']}, et le "
    "recul disparaît. « PIB nominal » lissé sur cinq ans, c'est la règle "
    "italienne ; le modèle en reprend le taux, pas le reste du système "
    "italien.",
)}</p>
""")


def _detail(contexte: Contexte, comparaison: Comparaison) -> str:
    retro = comparaison.notionnel_retroactif
    catalogue = contexte.simulateur().catalogue
    pensions = comparaison.actuel.pensions_par_regime

    def nom_regime(code: str) -> str:
        try:
            return catalogue[code].nom
        except KeyError:
            return code

    actuel = comparaison.actuel
    # Tout ce tableau est en euros de l'année de liquidation : c'est la seule
    # unité dans laquelle la chaîne de calcul s'additionne. Les six blocs du
    # haut, eux, mettent en avant les euros de l'année de référence. Sans dire
    # laquelle est laquelle, la dernière ligne prétendait valoir « le montant
    # de la ligne 1 ci-dessus » en désignant un nombre que la ligne 1
    # n'affichait pas.
    annee = comparaison.carriere.annee_liquidation
    annee_reference = comparaison.parametres.annee_euros_constants
    renvoi = (
        "Ce n'est pas l'unité des quatre montants affichés plus haut, qui les "
        f"ramène au pouvoir d'achat de {annee_reference}."
        if annee != annee_reference else
        "Le départ tombant sur l'année de référence, c'est aussi l'unité des "
        "quatre montants affichés plus haut."
    )
    # Les régimes PROVISIONNÉS sont sortis du tableau principal : leur rente ne
    # fait pas partie du total, et une ligne posée au-dessus d'un total qui
    # l'ignore fait un tableau qui ne s'additionne pas — 33 176,69 + 667,12
    # valait 33 176,69 à l'écran, sous une phrase affirmant le contraire. Elle
    # est reportée sous le total, où son exclusion se lit.
    repartis = [p for p in pensions if not catalogue[p.regime].hors_repartition]
    provisionnes = [p for p in pensions if catalogue[p.regime].hors_repartition]

    def ligne(pension) -> list[str]:
        return [escape(nom_regime(pension.regime)),
                g.euros_centimes(pension.montant),
                g.franciser(escape(pension.detail))]

    lignes_actuel: list[list[str]] = [ligne(pension) for pension in repartis]
    if lignes_actuel and actuel.avantages_appliques:
        lignes_actuel.append([
            "<strong>Sous-total contributif</strong>",
            "<strong>" + g.euros_centimes(actuel.total_contributif) + "</strong>",
            '<span class="discret">ce que la carrière a ouvert par ses seules '
            "cotisations</span>",
        ])
    for avantage in actuel.avantages_appliques:
        lignes_actuel.append([
            "+ " + escape(avantage.libelle),
            g.euros_centimes(avantage.montant),
            f'<span class="discret">{escape(avantage.detail)}</span>',
        ])
    if lignes_actuel:
        lignes_actuel.append([
            "<strong>Pension du système actuel</strong>",
            "<strong>" + g.euros_centimes(actuel.pension_annuelle) + "</strong>",
            '<span class="discret">c\'est le système 1 ci-dessus, pris '
            "dans les euros de son année de départ</span>",
        ])
    for pension in provisionnes:
        libelle, montant, detail = ligne(pension)
        lignes_actuel.append([
            "hors total — " + libelle, montant,
            '<span class="discret">régime PROVISIONNÉ, servi à part et retiré '
            "des quatre systèmes</span> · " + detail,
        ])

    regimes = g.tableau(
        ["Régime, puis avantage", f"Pension annuelle, en euros de {annee}",
         "Calcul"],
        lignes_actuel,
        ["", "nombre", ""],
        titre="Pension du système actuel, régime par régime",
        entete_de_ligne=True,
    ) if lignes_actuel else "<p>Aucun droit liquidé dans le système actuel.</p>"

    part = ""
    if actuel.avantages_appliques and actuel.pension_annuelle > 0:
        gratuit = sum(a.montant for a in actuel.avantages_appliques)
        part = (
            f'<p>Les avantages non contributifs pèsent {g.euros_centimes(gratuit)} par an, '
            f"soit {g.pourcentage(gratuit / actuel.pension_annuelle)} de la "
            "pension. C'est exactement ce que les deux scénarios notionnels "
            "retirent : ils ne conservent que le sous-total contributif, et le "
            "recalculent sur les cotisations réellement versées.</p>"
        )

    compte = g.tableau(
        ["Poste", "Montant"],
        [
            ["Cotisations effectivement versées, sommées aux euros de "
             "chaque année",
             g.euros(retro.compte.cotisations_versees)],
            ["Rendement cumulé appliqué à ces cotisations",
             "×" + g.nombre(retro.compte.rendement_cumule, DECIMALES_FACTEUR)],
            [f"Capital notionnel à la liquidation, en euros de {annee}",
             g.euros(retro.capital_notionnel)],
            ["Divisé par le coefficient de conversion",
             g.nombre(retro.conversion.diviseur, DECIMALES_DIVISEUR)
             + f" ({escape(retro.conversion.table)})"],
            [f"Pension annuelle, en euros de {annee}",
             g.euros_centimes(retro.pension_annuelle)],
        ],
        ["", "nombre"],
        titre="Construction du compte notionnel rétroactif, poste par poste",
        entete_de_ligne=True,
    )

    return g.depliant("Le détail du calcul", f"""
<p>Tous les montants de cette section sont en <strong>euros de {annee}</strong>,
l'année du départ.{g.bulle(
    "L'unité de cette section",
    f"{renvoi} C'est la seule unité dans laquelle une chaîne de calcul "
    "s'additionne : convertir chaque ligne au pouvoir d'achat d'une autre "
    "année ferait des totaux faux.",
)}</p>
<h4>Système 1 — de quoi votre pension actuelle est faite{g.bulle(
    "Comment lire ce tableau",
    "Chaque régime d'abord, puis les avantages que le droit en vigueur ajoute "
    "par-dessus ; le total est la pension du système 1. Un minimum est déjà "
    "compris dans la ligne du régime qui le sert : le sous-total contributif "
    "l'en retire, et la ligne suivante le rend visible — c'est la même somme, "
    "comptée une fois.",
)}</h4>
{regimes}
{part}
<h4>Système 2 — construction du compte notionnel rétroactif</h4>
{compte}
<details>
  {g.sommaire("Les résultats complets en JSON")}
  <pre class="json">{escape(json.dumps(comparaison.dictionnaire(), ensure_ascii=False, indent=2))}</pre>
</details>
<p class="discret">L'adresse de cette page contient tous les paramètres :
elle peut être citée ou partagée telle quelle.</p>
""")

#: Les cinq grilles de la page Cas types, dans l'ordre des onglets : le code du
#: scénario, le libellé de son onglet, le titre de sa section, le titre
#: accessible de sa grille, et la phrase qui dit ce qu'on y voit. Le premier
#: est CELUI QUI S'AFFICHE À L'OUVERTURE — le système 4, la proposition que
#: le site existe pour montrer ; les quatre autres sont les contrefactuels
#: qui mesurent ce que chaque ingrédient déplace, dans l'ordre de leur numéro.
GRILLES_CAS_TYPES: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "notionnel_liberal",
        "4. La proposition",
        "La proposition du Parti libéral français, par rapport à aujourd'hui",
        "La proposition libérale : taux unique de 18 % et garantie vieillesse",
        "Le même compte rétroactif que le système 3 jusqu'à la bascule, puis "
        "un taux unique de 18 % — salariale et patronale confondues —, une "
        "cotisation de 5 % capitalisée par-dessus, et une garantie vieillesse "
        "individualisée financée par l'impôt. Les lignes qui cotisaient au-delà "
        "de 18 % descendent sous le système 3, celles qui cotisaient en deçà "
        "remontent. L'écart affiché comprend la rente du pilier capitalisé : "
        "elle ne joue que pour qui cotise après la bascule, et d'autant plus "
        "qu'il lui reste d'années à courir — la page Simuler en donne le "
        "partage, carrière par carrière. La garantie, elle, ne se voit que sur "
        "les cas dont la pension reste sous le plancher, à partir de 65 ans.",
    ),
    (
        "notionnel_retroactif",
        "2. Part salariale seule",
        "Le compte notionnel sur la seule part salariale, par rapport à "
        "aujourd'hui",
        "Compte notionnel, part salariale seule, carrière recalculée depuis 1941",
        "Les générations anciennes sont les plus touchées : leurs cotisations, "
        "versées quand l'inflation dépassait la productivité, ont été "
        "revalorisées à un taux très inférieur à la hausse des prix.",
    ),
    (
        "notionnel_retroactif_employeur",
        "3. Les deux parts",
        "Le compte notionnel sur les deux parts, par rapport à aujourd'hui",
        "Compte notionnel, part salariale et patronale, carrière recalculée "
        "depuis 1941",
        "Toutes les lignes bougent, sauf celles des non-salariés — artisan, "
        "exploitant agricole, profession libérale — qui n'ont pas d'employeur "
        "et pour qui ce système est le système 2. Les lignes publiques "
        "bougent le plus : la contribution de leur employeur est un taux "
        "d'équilibre, sans commune mesure avec la part patronale d'un salarié.",
    ),
)


def _badge_scenario(scenario: str) -> str:
    """« proposition » sur le système 4, « contrefactuel » sur les autres.

    Que les systèmes 2 et 3 soient des exercices et que seul le 4 soit la
    proposition est dit en préambule, mais un tableau se lit sans son
    préambule : le badge le redit là où l'erreur de lecture se produit. Le
    système actuel n'en porte pas — c'est la référence, ni l'un ni l'autre.
    """
    if scenario == "actuel":
        return ""
    if scenario == "notionnel_liberal":
        return '<span class="badge proposition">proposition</span>'
    return '<span class="badge contrefactuel">contrefactuel</span>'



def _nom_scenario(scenario: str, libelle: str) -> str:
    """Le libellé d'un scénario en tête de ligne, avec son badge."""
    badge = _badge_scenario(scenario)
    return escape(libelle) + (f" {badge}" if badge else "")


def _cas_types(contexte: Contexte) -> str:
    """Treize carrières types croisées avec sept générations.

    LA PAGE NE MONTRE QU'UNE GRILLE À LA FOIS, ET C'EST LA PROPOSITION. Elle en
    montrait cinq à la file, puis une seule — un contrefactuel — avec les quatre
    autres dans un dépliant ; un lecteur pressé s'arrêtait donc sur un
    contrefactuel, et repartait en croyant avoir vu la proposition. Les cinq
    grilles sont désormais derrière des onglets, et l'onglet ouvert est le
    système 4 : c'est lui que le site existe pour montrer.

    Les onglets sont des boutons radio, et le panneau suit en CSS (``:has()``)
    : le clavier les parcourt aux flèches comme tout groupe de radios, aucun
    script ne tourne, et l'adresse ne change pas — ce que la route affiche
    reste ce que la route affiche. Les panneaux repliés sont dans la page,
    ``hidden`` : là où ``:has()`` n'existe pas, le premier reste visible et
    les autres restent cachés, ce qui dit moins mais rien de faux.

    CE QU'ELLE DIT EST UN ÉCART ENTRE LIGNES, JAMAIS UN NIVEAU. Le modèle
    calcule ce que chaque carrière acquiert ; il n'applique pas le coefficient
    d'équilibre, qui multiplierait toutes les pensions par un même facteur et
    déplacerait donc toute la grille en bloc. C'est écrit en tête, et non en
    note de bas de page : sans cette phrase, la grille se lit comme une baisse
    générale, ce qu'elle n'est pas.
    """
    simulateur = contexte.simulateur()
    resultat = calculer_cas_types(simulateur)
    montre = GRILLES_CAS_TYPES[0][0]
    # Le solde du système actuel, observé puis projeté par le COR : il est
    # dans les comptes, et ne coûte rien — à la différence du coût agrégé,
    # que cette page ne calcule pas.
    comptes = contexte.comptes()
    obs = comptes.derniere_annee_observee
    horizon = comptes.derniere_annee

    def grille(scenario: str, intitule: str) -> str:
        lignes = []
        for cas in CAS_TYPES:
            # Le libellé seul : ce qu'il recouvre est dit une fois pour toutes
            # sous la grille, et non dans une infobulle de survol que ni le
            # clavier ni le doigt n'ouvrent.
            cellules: list[str | g.Cellule] = [escape(cas.libelle)]
            for generation in GENERATIONS:
                comparaison = resultat.resultats.get((cas.code, generation))
                if comparaison is None:
                    cellules.append("—")
                    continue
                # L'écart porte sur ce que le système SERT, pilier capitalisé
                # compris. Il ne joue que sur le système 4 — les autres n'en
                # ont pas —, et la note sous la grille dit ce qu'il pèse.
                variation = comparaison.variation_totale(scenario)
                cellules.append(g.Cellule(
                    g.pourcentage(variation, signe=True, decimales=0),
                    intensite=variation,
                ))
            lignes.append(cellules)
        return g.tableau(
            ["Cas type"] + [str(generation) for generation in GENERATIONS],
            lignes,
            [""] + ["nombre"] * len(GENERATIONS),
            titre=f"{intitule} : écart de pension au système actuel, par cas "
                  "type et par génération",
            entete_de_ligne=True,
        )

    # Les trois chiffres d'ouverture : l'ÉCART entre les carrières, qui est ce
    # que la grille mesure, et non son niveau, qu'elle ne mesure pas. Ils sont
    # lus sur la dernière génération, la seule dont la carrière entière tombe
    # sous la règle nouvelle, et sur la grille qui s'affiche à l'ouverture.
    derniere = GENERATIONS[-1]
    ecarts = sorted(
        (comparaison.variation_totale(montre), cas.libelle)
        for cas in CAS_TYPES
        for comparaison in [resultat.resultats.get((cas.code, derniere))]
        if comparaison is not None
    )
    reperes = ""
    if ecarts:
        bas, haut = ecarts[0], ecarts[-1]
        reperes = g.fiche(
            "La carrière la mieux traitée", escape(haut[1].split(" (")[0]),
            g.pourcentage(haut[0], signe=True, decimales=0)
            + f" par rapport à aujourd'hui, génération {derniere}, système 4",
        ) + g.fiche(
            "La moins bien traitée", escape(bas[1].split(" (")[0]),
            g.pourcentage(bas[0], signe=True, decimales=0)
            + f" par rapport à aujourd'hui, génération {derniere}, système 4",
        ) + g.fiche(
            "Ce qui les sépare",
            g.nombre((haut[0] - bas[0]) * 100, 0) + " points",
            "à carrière et à durée identiques",
        )

    # Les onglets, puis les panneaux : deux frères, pour que la feuille de
    # style lise l'onglet coché et montre le panneau qui lui répond.
    onglets = "".join(
        f'<input type="radio" name="grille" id="grille-{scenario}"'
        + (" checked" if rang == 0 else "")
        + f'><label for="grille-{scenario}">{escape(onglet)}</label>'
        for rang, (scenario, onglet, _, _, _) in enumerate(GRILLES_CAS_TYPES)
    )
    panneaux = "".join(
        f'<div class="panneau" data-onglet="{scenario}"'
        + ("" if rang == 0 else " hidden") + ">"
        + f"<h3>{escape(titre)} {_badge_scenario(scenario)}</h3>{grille(scenario, alt)}"
        + f'<p class="discret">{escape(lecture)}</p></div>'
        for rang, (scenario, _, titre, alt, lecture) in enumerate(GRILLES_CAS_TYPES)
    )

    ages = g.tableau(
        ["Cas type"] + [str(generation) for generation in GENERATIONS],
        [
            [escape(cas.libelle)] + [
                _age(cas.age_liquidation_pour(simulateur, generation))
                for generation in GENERATIONS
            ]
            for cas in CAS_TYPES
        ],
        [""] + ["nombre"] * len(GENERATIONS),
        titre="Âge de liquidation de chaque cas type, par génération",
        entete_de_ligne=True,
    )

    echecs = ""
    if resultat.echecs:
        elements = "".join(
            f"<li>{escape(code)} / {generation} : {escape(motif)}</li>"
            for (code, generation), motif in sorted(resultat.echecs.items())
        )
        echecs = g.depliant(
            "Combinaisons que le modèle a refusé de calculer",
            f"<ul class='serree'>{elements}</ul>",
        )

    depliant_cas = g.depliant(
        "Qui sont ces treize carrières",
        g.gloses([(cas.libelle, cas.commentaire) for cas in CAS_TYPES]),
    )
    depliant_ages = g.depliant(
        "À quel âge chacun part, et pourquoi ce n'est pas le même",
        '<p class="discret">Un cas type ne porte pas un âge de départ mais une '
        "RÈGLE, et chaque génération liquide donc au sien. La plupart partent "
        "au taux plein, le premier âge auquel la pension est servie entière, "
        "qui dépend à la fois de l'âge légal et de la durée requise de la "
        "génération. Ceux dont un statut commande le départ (catégorie active, agent de conduite, agent des IEG) partent à l'âge que ce statut leur "
        "ouvre. Le militaire, lui, part à une DURÉE de services, pas à un âge.</p>" + ages,
    )

    tete = g.affiche(
        "Cas types",
        'Treize carrières, <span class="cle-texte">sept générations.</span>',
        "Chaque case dit ce que la pension deviendrait, par rapport à "
        "aujourd'hui, pour la même carrière. <strong>Rouge : moins "
        "qu'aujourd'hui. Vert : plus.</strong>",
    )

    return f"""
{tete}

<div class="note"><strong>Ces pourcentages ne sont pas des baisses de
pension.</strong> Chaque case compare deux carrières calculées sous la même
règle, et ce que la grille mesure est l'écart entre ses lignes : ce qu'un
militaire touche de plus ou de moins qu'un artisan, à cotisation égale. Le
niveau général, lui, dépend d'un
{g.terme("réglage annuel", "coefficient d'équilibre")} que le modèle calcule
mais n'applique jamais : il multiplierait toutes les cases par le même facteur.
Pour la proposition, ce facteur est supérieur à un chaque année : à
prélèvement égal, le système aurait de quoi servir davantage que ces cases
n'affichent. <strong>Un coefficient supérieur à un est une marge</strong>,
de quoi relever toutes les cases d'autant.
<a href="{g.lien("/cout")}" data-vers="cout-equilibre">La page Coût le chiffre</a>.</div>

<div class="fiches reperes">{reperes}</div>

<p class="discret">Le <strong>système 4</strong> est
<a href="{g.lien("/")}">la proposition</a> ; les systèmes 2 et 3 sont des
contrefactuels, qui mesurent ce que chaque ingrédient déplace : la part
patronale, puis le taux unique. Le modèle calcule deux variantes de plus —
celles où les droits acquis sont conservés à la bascule —, que le site ne
compare pas.</p>
<fieldset class="onglets"><legend>Système affiché</legend>{onglets}</fieldset>
<div class="panneaux">{panneaux}</div>
<p class="discret">« Aujourd'hui » n'est pas un point fixe. Le système actuel,
colonne de référence de ces grilles, manque déjà de
{g.pourcentage(-comptes.solde(obs), decimales=2)} du PIB en {obs}, et le
Conseil d'orientation des retraites projette qu'il en manquera
{g.pourcentage(-comptes.solde(horizon), decimales=2)} en {horizon}. Le choix
réel se joue entre le notionnel et un système
qui dérive ; le système stable, lui, n'existe pas.</p>

<p class="actions"><a class="bouton" href="{g.lien("/simuler")}">Calculer sur ma
carrière</a><a href="{g.lien("/methode")}">Comment c'est calculé</a></p>

<h2>Pour aller plus loin</h2>

{depliant_cas}
{depliant_ages}
{echecs}
"""


#: Bandes du graphique par système : les six plus lourdes gardent leur couleur,
#: le reste de la répartition est réuni, et ce qui n'en relève pas forme la
#: dernière bande. Huit bandes se lisent ; treize ne se lisent plus.
BANDES_COUT = (
    ("regime_general", "var(--serie-1)"),
    ("agirc_arrco", "var(--serie-2)"),
    ("fonction_publique_etat", "var(--serie-3)"),
    ("regimes_speciaux", "var(--serie-4)"),
    ("exploitants_agricoles", "var(--serie-5)"),
    ("professions_liberales", "var(--serie-6)"),
)

#: Couleur de chacun des quatre systèmes — les mêmes que sur la page de
#: résultats, pour qu'un lecteur qui passe de l'une à l'autre les reconnaisse.
COULEURS_SCENARIOS = {
    "actuel": "var(--actuel)",
    "notionnel_retroactif": "var(--retroactif)",
    "notionnel_retroactif_employeur": "var(--retroactif-employeur)",
    "notionnel_liberal": "var(--liberal)",
}


def _milliards(millions: float, decimales: int = 0) -> str:
    """Un montant en millions d'euros, écrit en milliards."""
    return g.nombre(millions / 1000, decimales) + "\u202fMd\u202f\u20ac"


def _cout(contexte: Contexte) -> str:
    """Ce que la retraite coûte, d'où vient l'argent, et ce qui manque.

    CETTE PAGE S'ADRESSE À QUELQU'UN QUI N'A PAS FAIT D'ÉCONOMIE ET QUI N'A PAS
    LE TEMPS. C'est une contrainte de construction, pas un vœu, et elle décide
    de tout ce qui suit :

    * **Une question par carte, une réponse par carte.** Chaque bloc porte une
      question en français courant, sa réponse en deux phrases courtes, puis le
      tracé qui la montre. Qui s'arrête à la réponse a déjà le résultat. La
      carte se télécharge en image, signée, pour être postée telle quelle.
    * **Deux graphiques, et pas un de plus.** La page en portait sept, puis
      quatre. Les trois qui traçaient une part du PIB dans le temps — l'histoire
      depuis 1959, le bilan jusqu'en 2070, l'effet de la réforme — n'en font
      plus qu'un : ils répondaient à la même question sur trois fenêtres, et
      obligeaient à recomposer de tête ce qu'un seul cadre montre d'un coup.
    * **Tout le reste est replié.** Le détail par régime, les six
      contrefactuels, les périmètres, les limites : rien n'est retiré — une page
      qui ne peut pas se justifier n'est pas honnête —, mais rien n'oblige à le
      traverser pour atteindre le résultat.
    * **Les phrases sont courtes, et les mots de spécialiste portent leur
      définition**, ouvrable sur place sans quitter la phrase.

    LE PÉRIMÈTRE DU GRAPHIQUE DE TÊTE EST CELUI DU COR, et ce n'est pas un
    détail de comptable : c'est le seul jeu de comptes où les dépenses ET les
    ressources du même ensemble de régimes soient publiées sous la même
    convention. Un solde ne se fabrique pas en soustrayant deux périmètres. Le
    modèle du dépôt n'y intervient que par un RAPPORT sans dimension — de
    combien la masse des pensions serait multipliée sous tel autre système —,
    jamais par un niveau.

    LA COURBE D'AVANT 2002 VIENT D'AILLEURS, et c'est pourquoi elle s'arrête là
    où celle du COR commence, au lieu de se prolonger sous elle. Les deux ne se
    raccordent pas : un demi-point de PIB les sépare, celui de la dépendance et
    de l'épargne retraite que la DREES compte et que le COR ne compte pas. Ce
    décrochement est visible sur le tracé, et c'est bien ainsi — le masquer
    reviendrait à coller deux séries qui ne mesurent pas la même chose.
    """
    comptes = contexte.comptes()
    cout = contexte.cout()
    solde = cout.solde
    depenses = contexte.depenses()
    bascule = contexte.base.annee_bascule

    obs = solde.derniere_annee_observee
    observe = solde.annee(obs)
    horizon = solde.annee(solde.derniere_annee)
    effectifs = contexte.simulateur().effectifs
    # La dernière année que la DREES publie, et non celle du compte : le
    # nombre de retraités n'a pas la même fenêtre que les comptes du COR, et
    # inventer un effectif pour l'année manquante ne vaudrait rien.
    annee_effectifs = effectifs.serie("tous_regimes").derniere_annee
    retraites = effectifs.effectif("tous_regimes", annee_effectifs)

    # -- les trois chiffres d'ouverture --------------------------------------
    #
    # Ce qu'on emporte si on ne lit rien d'autre. En EUROS et non en part de
    # PIB : une part de PIB ne parle qu'à qui sait déjà ce qu'est le PIB, et
    # c'est précisément le lecteur que cette page ne suppose pas.
    manque = -observe.solde_meur("actuel")
    part_manquante = -observe.solde("actuel") / observe.depense("actuel")
    reperes = g.fiche(
        f"Versé aux retraités en {obs}",
        _milliards(observe.depense_meur("actuel"), 0),
        f"à {g.nombre(retraites / 1e6, 1)} millions de personnes",
    ) + g.fiche(
        "Encaissé pour le payer",
        _milliards(observe.ressources_meur(), 0),
        "cotisations et impôts",
    ) + g.fiche(
        "Manquant" if manque > 0 else "Reste",
        _milliards(abs(manque), 1),
        g.pourcentage(abs(part_manquante), decimales=1) + " de la facture",
    )

    # -- le graphique de tête : cent onze ans en un seul cadre ----------------
    #
    # Il en remplace trois. Les fenêtres se recouvraient — 1959-2024 pour
    # l'histoire, 2002-2070 pour le bilan, 2025-2070 pour la réforme — et la
    # même grandeur y était tracée trois fois, à trois échelles différentes.
    # Les séries ne se recouvrent pas, elles : chacune vaut `None` hors de la
    # plage que sa source publie, et la courbe s'y interrompt plutôt que de
    # prolonger une mesure que personne n'a faite.
    annees_toutes = tuple(range(cout.premiere_annee, solde.derniere_annee + 1))
    rang = {annee: position for position, annee in enumerate(annees_toutes)}

    def _serie(libelle: str, couleur: str, valeurs: dict[int, float],
               tirets: bool = False, glose: str = "") -> g.Serie:
        colonne: list[float | None] = [None] * len(annees_toutes)
        for annee, valeur in valeurs.items():
            colonne[rang[annee]] = valeur
        return g.Serie(libelle, tuple(colonne), couleur, tirets, glose)

    # Avant 2002, le COR n'a rien : c'est la DREES qui porte l'histoire, sur un
    # périmètre un peu plus large. La courbe s'arrête à 2001, là où l'autre
    # commence, et le décrochement entre les deux se voit — il vaut le
    # demi-point que les deux comptes ne comptent pas pareil.
    avant = {annee: depenses.part_pib(annee) * 100
             for annee in range(cout.premiere_annee, solde.premiere_annee)}
    sortie = {ligne.annee: ligne.depense("actuel") * 100 for ligne in solde.annees}
    entree = {ligne.annee: ligne.ressources * 100 for ligne in solde.annees}
    # La troisième courbe est LA PROPOSITION, et non plus une variante que le
    # site ne compare plus. Elle ne commence qu'à l'année observée la plus
    # récente — non parce qu'elle ne changerait rien avant, elle est
    # rétroactive et change tout, mais parce que c'est de là que la décision se
    # prend. Ce qu'elle aurait coûté sur le passé est dans les tableaux du
    # dépliant, à sa place : celle d'un contrefactuel.
    reforme = "notionnel_liberal"
    apres = {ligne.annee: ligne.depense(reforme) * 100
             for ligne in solde.annees if ligne.annee >= obs}

    # L'ordre est celui de la lecture, de gauche à droite : la légende se
    # parcourt alors dans l'ordre où l'œil rencontre les courbes.
    courbes = (
        _serie(f"Avant {solde.premiere_annee}", "var(--serie-1)", avant,
               glose="autre source, périmètre un peu plus large"),
        _serie("Ce qui sort : les pensions versées", "var(--serie-2)", sortie),
        _serie("Ce qui rentre : cotisations et impôts", "var(--serie-5)", entree),
        _serie(f"Ce que coûterait notre proposition, dès {bascule}",
               "var(--liberal)", apres, tirets=True),
    )
    bilan = g.graphique(
        f"Ce que la retraite verse et ce qu'elle encaisse, de "
        f"{cout.premiere_annee} à {solde.derniere_annee}, en part du PIB",
        annees_toutes, courbes, unite="% du PIB",
        repere=obs, libelle_repere="projection",
        ecart=(2, 1),
        libelle_ecart="L'écart : vert s'il en reste, rouge s'il en manque",
        # L'axe gradue de quatre en quatre ; les chiffres, eux, portent le
        # dixième. Sans lui, l'écart entre les deux courbes — un point et demi
        # de PIB, tout le sujet de la carte — se lirait « 14 » contre « 13 ».
        decimales_donnees=1,
    )
    equilibre = solde.premiere_annee_equilibree(reforme)

    # -- le second graphique : d'où vient l'argent ---------------------------
    annees_ventilees = tuple(comptes.annees_ventilees())
    premiere_ventilee = annees_ventilees[0]
    derniere_ventilee = annees_ventilees[-1]
    bandes = tuple(
        g.Serie(
            groupe.libelle,
            tuple(comptes.ressource_groupe(groupe.code, annee) * 100
                  for annee in annees_ventilees),
            groupe.couleur,
        )
        for groupe in GROUPES
    )
    provenance = g.graphique(
        f"D'où viennent les ressources du système de retraite, de "
        f"{premiere_ventilee} à {derniere_ventilee}, en part du PIB",
        annees_ventilees, bandes, unite="% du PIB", empile=True,
        decimales_donnees=1,
    )
    part_salaires = comptes.part_groupe("salaires", derniere_ventilee)
    part_impots_debut = comptes.part_groupe("impots", premiere_ventilee)
    part_impots_fin = comptes.part_groupe("impots", derniere_ventilee)

    # -- les deux cartes -----------------------------------------------------
    #
    # Bâties à part et non dans le gabarit final : une réponse et une source
    # sont elles-mêmes des textes à trous, et Python n'accepte pas un bloc entre
    # triples guillemets à l'intérieur d'un autre.
    #
    # « en 2043 » et « jamais » ne se branchent pas au même endroit de la
    # phrase : l'un complète le verbe, l'autre le nie, et le repli posé sur le
    # seul millésime donnait « les comptes se rééquilibrent en jamais ».
    retour_equilibre = (
        f"les comptes se rééquilibrent en {equilibre}" if equilibre
        else "les comptes ne se rééquilibrent jamais"
    )
    carte_bilan = g.cle(
        "La retraite coûte-t-elle plus qu'elle ne rapporte ?",
        f"""Oui, un peu : {_milliards(abs(manque), 1)} de trop en {obs}.
<strong>L'écart va se creuser</strong> : en {solde.derniere_annee} il
manquerait
{g.pourcentage(abs(horizon.solde("actuel") / horizon.depense("actuel")), decimales=0)}
de la facture. En comptes notionnels dès {bascule}, {retour_equilibre}.""",
        bilan,
        f"""Sources : DREES jusqu'en {solde.premiere_annee - 1}, Conseil
d'orientation des retraites ensuite — c'est lui qui projette, pas nous. En
{g.terme("part du PIB")} : sur 100 € produits en France, combien vont aux
retraites.""",
        identifiant="cout-bilan",
    )

    carte_provenance = g.cle(
        "Qui paie ?",
        f"""Les salaires, pour {g.pourcentage(part_salaires, decimales=0)} :
c'est ce qui est prélevé sur chaque fiche de paie. Le reste vient surtout de
l'impôt, et <strong>cette part a doublé en vingt ans</strong> :

{g.pourcentage(part_impots_debut, decimales=0)} en {premiere_ventilee},
{g.pourcentage(part_impots_fin, decimales=0)} en {derniere_ventilee}.""",
        provenance + g.depliant(
            "Ce que contient chaque part",
            g.gloses([(groupe.libelle, groupe.explication) for groupe in GROUPES]),
        ),
        f"""Source : Conseil d'orientation des retraites. Ce détail n'est publié
que de {premiere_ventilee} à {derniere_ventilee}.""",
        identifiant="cout-provenance",
    )

    # Le détail est rendu AVANT le gabarit final : c'est de lui, et des deux
    # cartes, que le plan de la page se déduit.
    detail = "".join([
        _cout_detail_depense(contexte),
        _cout_detail_ressources(contexte),
        _cout_detail_transferts(contexte),
        _cout_detail_scenarios(contexte),
        _cout_detail_equilibre(contexte),
        _cout_detail_garantie(contexte),
        _cout_detail_capitalisation(contexte),
        _cout_detail_poids(contexte),
        _cout_detail_sources(contexte),
        _cout_detail_limites(contexte),
    ])
    plan = g.plan(carte_bilan + carte_provenance + detail, "/cout")

    tete = g.affiche(
        "Le coût",
        'Ce qui rentre, ce qui sort, '
        '<span class="cle-texte">ce qui manque.</span>',
        "Vos cotisations ne sont pas mises de côté. Elles paient aussitôt les "
        "pensions de ceux qui sont déjà retraités : c'est la "
        + g.terme("répartition") + ".",
    )

    return f"""
{tete}

<div class="note resume"><strong>En clair.</strong> En {obs}, les retraites
ont coûté un peu plus qu'elles n'ont rapporté : il a manqué
{_milliards(manque, 1)}, soit {g.pourcentage(part_manquante, decimales=1)} de la
facture. L'argent vient des cotisations pour l'essentiel, et de plus en plus
de l'impôt. Sans rien changer, il manquerait en {solde.derniere_annee}
{g.pourcentage(abs(horizon.solde("actuel") / horizon.depense("actuel")), decimales=0)}
de la facture. Un système en comptes notionnels ne dépenserait pas moins : il
servirait le même argent, réparti autrement, et se réglerait chaque année au
lieu d'attendre une réforme.</div>

<div class="fiches reperes">{reperes}</div>

{plan}

{carte_bilan}

{carte_provenance}

<div class="note"><strong>Dépenser moins n'est pas économiser.</strong> Un
système en {g.terme("comptes notionnels", "compte notionnel")} ne laisse pas d'argent
dormir : il remonte les pensions jusqu'à l'équilibre. La courbe en pointillés
ne dit donc pas « on dépenserait moins ». Elle dit : <em>avec le même argent,
on servirait autant, mais réparti autrement entre les carrières</em>.</div>

<h2>Et pour vous ?</h2>
<p>Tout cela est un total national. Ce que chaque règle donne sur votre
carrière se calcule en quelques secondes, dans votre navigateur.</p>
<p class="actions"><a class="bouton" href="{g.lien("/simuler")}">Calculer ma
retraite</a><a href="{g.lien("/cas-types")}">Voir treize carrières types</a></p>

<h2>Pour aller plus loin</h2>
<p class="chapeau">Tout ce que cette page doit pouvoir justifier est ici.</p>

{detail}
"""


#: La couleur de chaque famille de l'inventaire, dans l'ordre où le comptage
#: les empile. Les écarts structurels n'y sont pas : ils ne sont pas des
#: dispositifs, ils ne se comptent pas avec eux, et l'inventaire le dit.
COULEURS_FAMILLES: tuple[tuple[str, str], ...] = (
    ("age_et_bonifications", "var(--serie-2)"),
    ("droits_familiaux", "var(--serie-3)"),
    ("minima_de_pension", "var(--serie-4)"),
    ("droits_derives", "var(--serie-5)"),
    ("periodes_non_cotisees", "var(--serie-6)"),
    ("autres_avantages", "var(--serie-7)"),
)

#: Les couleurs des lignes de coût, dans l'ordre de la légende.
COULEURS_LIGNES: tuple[str, ...] = (
    "var(--serie-2)", "var(--serie-3)", "var(--serie-4)", "var(--serie-5)",
    "var(--serie-6)", "var(--serie-7)", "var(--serie-8)", "var(--serie-9)",
    "var(--serie-1)",
)

#: La couleur de chaque motif de départ anticipé.
COULEURS_MOTIFS: dict[str, str] = {
    "regime_special": "var(--serie-2)",
    "classement": "var(--serie-4)",
    "carriere_longue": "var(--serie-5)",
}

#: Ce que chacun des quatre états du modèle veut dire, en français courant.
LIBELLES_ETATS: dict[str, str] = {
    "chiffre": "chiffré",
    "integre": "servi, chiffré à part",
    "declare": "déclaré, non servi",
    "absent": "absent",
}


def _avantages(contexte: Contexte) -> str:
    """Tous les avantages non contributifs, depuis quand, et ce qu'ils coûtent.

    CETTE PAGE RÉPOND À UNE QUESTION QU'ON POSE SOUVENT SANS Y RÉPONDRE :
    pourquoi les pensions d'aujourd'hui dépassent-elles ce que les gens ont
    cotisé ? Une partie de la réponse tient en une liste, et cette liste
    n'existait nulle part — pas même dans ce dépôt, qui en portait trois
    partielles et discordantes.

    TROIS GRAPHIQUES, ET ILS N'ONT PAS LE MÊME STATUT. C'est la contrainte de
    construction de cette page, et elle décide de l'ordre :

    * **Le premier est une DONNÉE.** Combien de dispositifs non contributifs
      existent chaque année, par famille. Rien n'y est calculé : chaque barre
      est la somme des lignes de l'inventaire dont la date de création est
      passée et la date de fin ne l'est pas. Il est donc exact, et c'est
      pourquoi il mène.
    * **Le deuxième est une MESURE, et un plancher très bas.** Ce que coûtent
      les dispositifs que le modèle sait chiffrer. La grille de cas types n'est
      pas une population — un seul de ses treize cas types a des enfants, aucun
      ne connaît le chômage —, et le chiffre vaut 3 % de la dépense là où le
      COR chiffre les droits de solidarité à « de l'ordre d'un cinquième ». La
      carte le dit avant de montrer la courbe, et non après.
    * **Le troisième mesure autre chose**, et c'est le résultat le moins
      attendu : les annuités servies avant l'âge légal. Un avantage d'âge agit
      deux fois — sur le montant, et sur la durée —, et la seconde pèse quinze
      fois la première. La décote étant plafonnée à vingt trimestres, l'agent
      parti cinq ans trop tôt et l'agent parti à l'heure butent sur le même
      plafond : le montant ne sait pas les distinguer, la durée le sait.

    LA LISTE ENTIÈRE EST DANS LA PAGE, repliée, avec pour chaque ligne sa base
    légale et l'état du modèle à son égard. Une page qui ne peut pas se
    justifier n'est pas honnête, et celle-ci affirme qu'il en existe
    trente-neuf : elle doit pouvoir les nommer.
    """
    inventaire = contexte.inventaire_avantages()
    cout = contexte.avantages()
    derniere = cout.derniere
    chiffres = len(inventaire.chiffres)
    total = len(inventaire.avantages)
    # Combien de périodes du catalogue déclarent la réversion : le chiffre est
    # COMPTÉ et non écrit, pour qu'une fiche ajoutée le déplace.
    declarations = sum(
        1 for regime in contexte.simulateur().catalogue
        for periode in regime.periodes
        if "reversion" in periode.avantages_non_contributifs
    )

    # -- premier graphique : combien existent, et depuis quand ---------------
    #
    # Les bornes sont LUES et non écrites : ajouter à l'inventaire un
    # dispositif plus ancien doit déplacer le bord du cadre, et pas seulement
    # une ligne de tableau.
    dispositifs = tuple(a for a in inventaire.avantages
                        if a.famille != "ecarts_structurels")
    premiere_frise = min(a.creation for a in dispositifs)
    derniere_frise = contexte.base.annee_courante
    annees_frise = tuple(range(premiere_frise, derniere_frise + 1))
    familles = {famille.code: famille.libelle for famille in inventaire.familles}
    bandes = tuple(
        g.Serie(
            familles[code],
            tuple(
                float(sum(1 for a in dispositifs
                          if a.famille == code and a.creation <= annee
                          and (a.fin is None or a.fin >= annee)))
                for annee in annees_frise
            ),
            couleur,
        )
        for code, couleur in COULEURS_FAMILLES
    )
    en_vigueur = sum(int(bande.valeurs[-1]) for bande in bandes)
    frise = g.graphique(
        f"Nombre d'avantages non contributifs en vigueur chaque année, par "
        f"famille, de {premiere_frise} à {derniere_frise}",
        annees_frise, bandes, unite="dispositifs", empile=True,
    )

    # -- les trois chiffres d'ouverture --------------------------------------
    reperes = g.fiche(
        "Avantages non contributifs recensés",
        str(total),
        "du minimum vieillesse à la bonification du cinquième",
    ) + g.fiche(
        "Ce que le modèle sait en chiffrer",
        _milliards(derniere.gratuit, 1),
        f"{chiffres} d'entre eux, en {derniere.annee}",
    ) + g.fiche(
        "Servi avant l'âge légal",
        _milliards(derniere.anticipee, 1),
        g.pourcentage(derniere.anticipee / derniere.observee, decimales=1)
        + " de la dépense",
    )

    # -- deuxième graphique : tout ce qu'on sait chiffrer, en un seul tracé ---
    #
    # LA FENÊTRE EST CELLE OÙ TOUTES LES LIGNES SONT PUBLIÉES, et non celle de
    # la plus ancienne. Les lignes calculées remontent à 1959 ; la réversion,
    # qui est lue et non calculée, commence en 2004. Les empiler sur la fenêtre
    # longue dessinerait une falaise de vingt-cinq milliards cette année-là, et
    # le lecteur y verrait un saut de dépense là où il n'y a qu'un début de
    # publication.
    #
    # Le choix ne coûte d'ailleurs presque rien, et il gagne en cohérence : les
    # POIDS des cas types viennent eux aussi de la DREES, qui ne les publie que
    # de 2004 à 2024 — avant, la répartition du bord est reconduite et la série
    # tombe au niveau « estimée ». La fenêtre commune est donc celle où chaque
    # terme du produit est observé. Ce que les années antérieures montraient —
    # un minimum vieillesse qui pesait le tiers de la dépense en 1960 et qui
    # s'est éteint — est dans `scripts/cout_avantages.py`, qui remonte à 1959.
    annees_cout = tuple(ligne.annee for ligne in cout.annees)
    annees_publiees = tuple(
        ligne.annee for ligne in cout.annees if "reversion" in ligne.lignes
    )
    fenetre = tuple(
        ligne for ligne in cout.annees if ligne.annee in set(annees_publiees)
    )
    couts = tuple(
        g.Serie(
            inventaire.libelle_de_ligne(ligne),
            tuple(annee.lignes.get(ligne, 0.0) / 1000 for annee in fenetre),
            COULEURS_LIGNES[rang % len(COULEURS_LIGNES)],
        )
        for rang, ligne in enumerate(reversed(cout.lignes))
    )
    reversion = derniere.lignes.get("reversion", 0.0)
    courbe_cout = g.graphique(
        f"Coût des avantages non contributifs que l'on sait chiffrer, de "
        f"{annees_publiees[0]} à {annees_publiees[-1]}",
        annees_publiees, couts, unite="Md€ courants", empile=True,
        decimales_donnees=1,
    ) if annees_publiees else ""

    # -- troisième graphique : les annuités servies trop tôt -----------------
    anticipees = tuple(
        g.Serie(
            LIBELLES_MOTIFS[motif],
            tuple(annee.anticipees.get(motif, 0.0) / 1000 for annee in cout.annees),
            COULEURS_MOTIFS[motif],
        )
        for motif in MOTIFS
    )
    courbe_age = g.graphique(
        f"Pensions servies avant l'âge légal, par ce qui ouvre le départ, de "
        f"{annees_cout[0]} à {annees_cout[-1]}",
        annees_cout, anticipees, unite="Md€ courants", empile=True,
        decimales_donnees=1,
    )

    carte_frise = g.cle(
        "Combien le système compte-t-il d'avantages qui ne sont pas cotisés ?",
        f"""<strong>{en_vigueur} aujourd'hui, contre un seul en
{premiere_frise}.</strong> Presque aucun n'a jamais été supprimé : la courbe
monte pendant deux siècles et ne redescend que trois fois.""",
        frise,
        """Source : inventaire du dépôt, base légale lue article par article
dans la base LEGI. Ce graphique ne calcule rien : il compte des lignes.""",
        identifiant="avantages-frise",
    )

    carte_cout = g.cle(
        "Combien coûtent ceux que l'on sait chiffrer ?",
        f"""<strong>{_milliards(derniere.gratuit, 1)} en {derniere.annee}, soit
{g.pourcentage(derniere.gratuit / derniere.observee, decimales=1)} de la
dépense</strong>, dont {_milliards(reversion, 1)} pour la seule
<strong>réversion</strong>. C'est encore un plancher : {chiffres} dispositifs
sur {total} y sont, et le COR chiffre l'ensemble des droits de solidarité à
« de l'ordre d'un cinquième » des retraites.""",
        courbe_cout + g.depliant(
            "Pourquoi ce chiffre est un plancher, et de combien",
            """<p>Deux raisons, et la seconde est la plus gênante.</p>
<p><strong>La réversion est là, mais elle n'est pas calculée : elle est
lue.</strong> Le modèle décrit une carrière, pas un ménage : il n'a ni conjoint,
ni date de décès, ni ressources du survivant, et ne produira donc jamais une
pension de réversion. Son montant vient de l'enquête annuelle de la DREES auprès
des caisses, qui dénombre les bénéficiaires d'un droit dérivé et le montant
mensuel moyen de ce droit-là. C'est, de loin, la ligne la plus sûre du tracé :
elle dénombre 4,4 millions de personnes réelles, là où les autres reposent sur
treize carrières types. Ce qui manque vraiment est ailleurs : les bonifications
de service, et les départs anticipés pour handicap ou inaptitude.</p>
<p><strong>La fenêtre est celle où toutes les lignes sont publiées.</strong> Les
lignes calculées remontent à 1959 ; la réversion commence en 2004, et les poids
des carrières types viennent eux aussi d'une série que la DREES ne publie que
depuis cette année-là. Le tracé s'arrête donc là où chaque terme est observé.
Les années antérieures montraient un minimum vieillesse qui pesait le tiers de
la dépense en 1960 et qui s'est éteint ; le dépôt les calcule toujours, hors du
site.</p>
<p><strong>Et la grille de carrières types n'est pas une population.</strong> Un
seul de ses treize cas types a des enfants (deux, quand le seuil est à trois),
un seul porte des interruptions, aucun ne connaît le chômage. La
majoration de pension pour trois enfants et plus vaut donc zéro toutes les
années de la série, quand la branche famille en rembourse près de six
milliards. Une grille de cas types sert à <em>comparer</em> des systèmes sur une
même carrière, où les erreurs de niveau s'annulent au dénominateur ; le coût
d'un avantage est un compte de <em>population</em>.</p>""",
        ),
        """Sources : décomposition du scénario 1 sur la grille de carrières
types, rapportée à la dépense observée de la DREES — seule la part est
modélisée ; et, pour la réversion, l'enquête annuelle de la DREES auprès des
caisses de retraite, série certifiée de 2004 à 2024.""",
        identifiant="avantages-cout",
    )

    part_classement = (derniere.anticipees.get("classement", 0.0)
                       / derniere.anticipee if derniere.anticipee > 0 else 0.0)
    carte_age = g.cle(
        "Et partir plus tôt, combien cela coûte-t-il ?",
        f"""<strong>{_milliards(derniere.anticipee, 1)} de pensions servies avant
l'âge légal en {derniere.annee}</strong>, soit treize fois ce que les mêmes
dispositifs ajoutent au <em>montant</em> des pensions. Une annuité versée avant
l'âge légal n'est rattrapée par aucune décote.""",
        courbe_age + g.depliant(
            "Pourquoi le montant ne suffit pas à le dire",
            f"""<p>La décote est <strong>plafonnée à vingt trimestres</strong>.
Un agent de catégorie active parti à 57 ans et un agent sédentaire parti le même
jour butent donc tous deux sur le même plafond : leurs pensions ne diffèrent que
de 868 € par an. Le montant ne sait pas distinguer celui qui part cinq ans trop
tôt ; la durée le sait.</p>
<p>Le classement de l'emploi en porte
{g.pourcentage(part_classement, decimales=0)}. Le reste se partage entre les
âges propres des régimes spéciaux et la <strong>carrière longue</strong>, qui
n'apparaît qu'après 2010 : mécaniquement, à mesure que l'âge légal monte
au-dessus de l'âge auquel une carrière commencée tôt réunit sa durée.</p>
<p><strong>Réserve.</strong> Ce sont des annuités <em>anticipées</em>, non un
surcoût <em>net</em> : partir tôt, c'est aussi cotiser moins et mourir plus tôt
en moyenne. C'est exactement l'arbitrage qu'un coefficient de conversion
notionnel rend automatique, et que le droit actuel ne rend nulle part.</p>""",
        ),
        """Source : même décomposition, comparée à l'âge légal de chaque
génération plutôt qu'à un âge fixe, qui compterait comme anticipé un départ que
le droit de l'époque disait à l'heure.""",
        identifiant="avantages-age",
    )

    detail = (_avantages_detail_liste(contexte)
              + _avantages_detail_etats(contexte)
              + _avantages_detail_limites(contexte))
    plan = g.plan(carte_frise + carte_cout + carte_age + detail, "/avantages")

    tete = g.affiche(
        "Les avantages",
        'Ce que la retraite verse <span class="cle-texte">sans que personne '
        "l'ait cotisé.</span>",
        "Un compte notionnel ne sert que ce qui a été versé. Le système actuel "
        "sert bien davantage, et ce qui les sépare porte des noms : minimum "
        "contributif, trimestres gratuits, départ anticipé, réversion.",
    )

    return f"""
{tete}

<div class="note resume"><strong>En clair.</strong> Le système actuel compte
{en_vigueur} dispositifs qui ajoutent à une pension sans qu'aucune cotisation
les ait payés, contre un seul en {premiere_frise}. Le modèle sait en chiffrer
{chiffres} : {_milliards(derniere.gratuit, 1)} en {derniere.annee}, dont
{_milliards(derniere.lignes.get("reversion", 0.0), 1)} de réversion, qui est lue
et non calculée. Il mesure à
part {_milliards(derniere.anticipee, 1)} de pensions servies avant l'âge légal,
que nulle décote ne rattrape. Les deux chiffres sont des planchers, et cette
page dit de combien.</div>

<div class="fiches reperes">{reperes}</div>

{plan}

{carte_frise}

{carte_cout}

{carte_age}

<div class="note"><strong>Aucun de ces dispositifs n'est illégitime.</strong>
Chacun a été voté pour une raison, et plusieurs corrigent de vraies injustices.
Ce qui pose problème est leur opacité. Personne ne reçoit le décompte de ce
qu'il a cotisé puis de ce qu'on lui ajoute. Un compte notionnel ne les interdit
pas : il oblige à les payer par l'impôt, sous leur nom, plutôt que par une
formule que nul ne lit.</div>

<h2>Et pour vous ?</h2>
<p>Ce que ces règles donnent sur votre carrière se calcule en quelques secondes,
dans votre navigateur : la simulation affiche votre part cotisée, puis chaque
avantage, ligne à ligne.</p>
<p class="actions"><a class="bouton" href="{g.lien("/simuler")}">Calculer ma
retraite</a><a href="{g.lien("/cout")}">Voir ce que tout cela coûte</a></p>

<h2>Pour aller plus loin</h2>
<p class="chapeau">La liste entière, et ce que le modèle sait en faire.</p>

{detail}
"""


#: Les trois pages qui AGRÈGENT : elles ne calculent aucune carrière saisie,
#: mais elles obéissent aux mêmes règles que le simulateur. La table est posée
#: ici, après les trois fonctions, et lue par ``rendre`` — voir ``_agregee``.
PAGES_AGREGEES = {
    "/cas-types": _cas_types,
    "/cout": _cout,
    "/avantages": _avantages,
}


def _avantages_detail_liste(contexte: Contexte) -> str:
    """Les trente-neuf, famille par famille, avec leur base légale."""
    inventaire = contexte.inventaire_avantages()
    blocs = []
    for famille in inventaire.familles:
        lignes = [
            [
                avantage.libelle,
                "; ".join(avantage.base_legale) or "—",
                str(avantage.creation),
                "en vigueur" if avantage.fin is None else str(avantage.fin),
                LIBELLES_ETATS[avantage.etat_modele],
            ]
            for avantage in inventaire.par_famille(famille.code)
        ]
        if not lignes:
            continue
        blocs.append(
            f"<h4>{escape(famille.libelle)}</h4><p>{escape(famille.quoi)}</p>"
            + g.tableau(["Dispositif", "Base légale", "Depuis", "Jusqu'à",
                         "Dans le modèle"], lignes,
                        titre=f"{famille.libelle} : {len(lignes)} dispositifs",
                        entete_de_ligne=True)
        )
    return g.depliant(
        f"La liste entière : {len(inventaire.avantages)} dispositifs",
        "".join(blocs),
        identifiant="avantages-liste",
    )


def _avantages_detail_etats(contexte: Contexte) -> str:
    """Ce que le modèle sait de chacun, et ce qu'il n'en sait pas."""
    inventaire = contexte.inventaire_avantages()
    cout = contexte.avantages()
    lignes = [
        ["chiffré", str(inventaire.compte("chiffre")),
         "La cascade du scénario 1 en isole le montant en euros. La somme de "
         "ces lignes vaut exactement la pension moins sa part cotisée."],
        ["servi, chiffré à part", str(inventaire.compte("integre")),
         "Le scénario 1 les sert, mais l'effet passe par un trimestre, un âge "
         f"ou une assiette. {len(NEUTRALISATIONS)} sont mesurés par retrait : on "
         "refait la pension sans l'avantage, et l'écart est le chiffre. Les "
         f"{inventaire.compte('integre') - len(NEUTRALISATIONS)} derniers ne sont "
         "pas des dispositifs, et se lisent ailleurs."],
        ["déclaré, non servi", str(inventaire.compte("declare")),
         "Une fiche de régime les déclare, aucun code ne les sert. La "
         "réversion est de ceux-là : 756 périodes du catalogue l'annoncent, et "
         "le modèle ne la produira jamais, faute de décrire un ménage. Son coût "
         "est donc LU dans l'enquête de la DREES auprès des caisses, et c'est "
         "le chiffre le plus sûr de cette page."],
        ["absent", str(inventaire.compte("absent")),
         "Ni déclarés ni servis : les bonifications de service, les départs "
         "pour handicap ou inaptitude, l'allocation veuvage. C'est un écart au "
         "droit positif, et le dépôt le nomme plutôt que de l'estimer."],
    ]
    refus = "".join(
        f"<p><strong>{escape(ligne)}</strong> — {escape(raison)}</p>"
        for ligne, raison in sorted(cout.refus.items())
    )
    note = (f"<h4>Ce que le modèle a refusé de mesurer</h4><p>Un refus est un "
            f"résultat : il dit qu'une contrefactuelle existe mais ne vaut rien, "
            f"ce qui est plus sûr qu'un chiffre plausible.</p>{refus}"
            if refus else "")
    return g.depliant(
        "Ce que le modèle sait de chacun",
        g.tableau(["État", "Combien", "Ce que cela veut dire"], lignes,
                  titre="Ce que le modèle sait de chaque avantage",
                  entete_de_ligne=True) + note,
        identifiant="avantages-etats",
    )


def _avantages_detail_limites(contexte: Contexte) -> str:
    """Les trois réserves de la page, et pourquoi elles y sont."""
    return g.depliant(
        "Trois choses que ces chiffres ne disent pas",
        """<p><strong>Elle ne dit pas ce que le système économiserait.</strong>
Supprimer un avantage ne rend pas son coût : il faudrait décider ce que
l'assuré aurait fait sans lui — travailler plus longtemps, partir avec moins, ne
pas partir. Le dépôt ne tranche pas à sa place, et ces chiffres disent ce qui
est <em>versé</em>, non ce qui serait <em>épargné</em>.</p>
<p><strong>Elle ne compte pas deux fois la même chose.</strong> Les trois
« écarts structurels » de l'inventaire (une décote qui n'est pas actuarielle,
un rendement supérieur à ce que l'assiette porte, un financement par l'impôt)
ne sont pas des dispositifs et ne figurent donc pas dans le comptage. Ils
portent sur la même pension, vue sous un autre angle, et les additionner serait
un double compte.</p>
<p><strong>Elle ne remplace pas la loi.</strong> Chaque base légale a été lue
dans la base LEGI, version par version ; deux lignes sur trente-neuf portent la
mention « à certifier », parce que leurs textes sont éclatés dans des statuts de
corps qui n'ont pas été lus. Une déduction n'est pas une lecture.</p>""",
        identifiant="avantages-limites",
    )


def _cout_detail_depense(contexte: Contexte) -> str:
    """Le détail de la dépense : en euros, puis système par système."""
    depenses = contexte.depenses()
    cout = contexte.cout()
    euros = cout.annee_euros
    derniere = depenses.derniere_annee
    annees = tuple(ligne.annee for ligne in cout.annees)
    ventilees = tuple(depenses.annees_ventilees())
    premiere_ventilee = ventilees[0]
    total = depenses.depense(derniere)
    repartition = depenses.repartition(derniere)
    autres = {code: depenses.depense_systeme(code, derniere)
              for code in (s.code for s in SYSTEMES if not s.repartition)}

    courbe_constants = g.Serie(
        f"En euros constants de {euros}",
        tuple(ligne.observee_constants / 1000 for ligne in cout.annees),
        "var(--serie-1)",
    )
    courbe_courants = g.Serie(
        "En euros courants de chaque année",
        tuple(ligne.observee / 1000 for ligne in cout.annees),
        "var(--serie-2)", tirets=True,
    )

    reunies = [code for code, _ in BANDES_COUT]
    bandes = [
        g.Serie(
            next(s.libelle for s in SYSTEMES if s.code == code),
            tuple(depenses.depense_systeme(code, annee) / 1000 for annee in ventilees),
            couleur,
        )
        for code, couleur in BANDES_COUT
    ]
    bandes.append(g.Serie(
        "Autres régimes par répartition",
        tuple(
            sum(depenses.depense_systeme(s.code, annee) for s in SYSTEMES
                if s.repartition and s.code not in reunies) / 1000
            for annee in ventilees
        ),
        "var(--serie-7)",
    ))
    bandes.append(g.Serie(
        "Hors répartition obligatoire",
        tuple(
            sum(depenses.depense_systeme(s.code, annee) for s in SYSTEMES
                if not s.repartition) / 1000
            for annee in ventilees
        ),
        "var(--serie-9)",
        glose="capitalisation, dépendance, minimum vieillesse",
    ))

    duree = derniere - premiere_ventilee
    lignes_systemes = []
    for systeme in SYSTEMES:
        debut = depenses.depense_systeme(systeme.code, premiere_ventilee)
        fin = depenses.depense_systeme(systeme.code, derniere)
        coefficient = contexte.simulateur().macro.coefficient_prix(
            premiere_ventilee, derniere)
        croissance = (fin / (debut * coefficient)) ** (1 / duree) - 1 if debut > 0 else 0.0
        cumul = sum(
            depenses.depense_systeme(systeme.code, annee)
            * contexte.simulateur().macro.coefficient_prix(annee, euros)
            for annee in ventilees
        )
        lignes_systemes.append([
            escape(systeme.libelle),
            _milliards(fin, 1),
            g.pourcentage(fin / total, decimales=1),
            _milliards(cumul, 0),
            g.pourcentage(croissance, signe=True, decimales=1),
            "oui" if systeme.repartition else "non",
        ])

    return g.depliant(f"Le détail des dépenses, de {cout.premiere_annee} à {derniere}", f"""
<p>Les {_milliards(total, 1)} de {derniere} sont le risque
<strong>vieillesse-survie tout entier</strong> : les pensions, mais aussi le
minimum vieillesse, l'aide sociale aux personnes âgées et la retraite
supplémentaire par capitalisation. La <strong>répartition obligatoire</strong>
seule en fait {_milliards(repartition, 1)} : c'est cette grandeur-là qu'il faut
rapprocher des quelque 420 milliards que l'on cite d'ordinaire. Le reste est
{_milliards(autres["aide_sociale_locale"], 1)} de dépendance,
{_milliards(autres["supplementaire"], 1)} de capitalisation et
{_milliards(autres["solidarite_etat"], 1)} de solidarité de l'État.</p>

<h4>La même dépense, en euros</h4>
{g.graphique(
    f"Dépenses du risque vieillesse-survie de {cout.premiere_annee} à {derniere}, "
    f"en milliards d'euros",
    annees, (courbe_constants, courbe_courants), unite="Md €")}
<p class="discret">Deux lectures de la même série. En euros courants, la
dépense est multipliée par cent quatre-vingt-treize depuis
{cout.premiere_annee} . Mais les prix aussi ont été multipliés par treize. En
euros constants, la multiplication est par quinze : c'est celle-là qui est
réelle. C'est pour éviter ce genre de piège que les cartes du haut sont en part
du PIB.</p>

<h4>Système par système</h4>
{g.graphique(
    f"Dépenses de vieillesse-survie par système, {premiere_ventilee}-{derniere}, "
    f"en milliards d'euros courants",
    ventilees, tuple(bandes), unite="Md €", empile=True)}
<p class="discret">La ventilation ne commence qu'en {premiere_ventilee} : de 1981
à 1989 la DREES publie une autre nomenclature, dont les périmètres ne se
raccordent pas à ceux-ci, et personne n'a publié le raccord. Le total, lui,
remonte à {cout.premiere_annee}.</p>

{g.tableau(
    ["Système", f"{derniere}", "Part", f"Cumul {premiere_ventilee}-{derniere}",
     "Croissance réelle", "Répartition"],
    lignes_systemes,
    ["", "nombre", "nombre", "nombre", "nombre", ""],
    titre=f"Dépense de vieillesse-survie par système en {derniere}, et cumul "
          f"depuis {premiere_ventilee}",
    entete_de_ligne=True,
)}
{g.gloses([(systeme.libelle, systeme.glose) for systeme in SYSTEMES])}
<p class="discret">Le cumul est en euros constants de {euros} : additionner des
euros de 1990 et de {derniere} n'aurait aucun sens. La croissance réelle est
celle de la dépense annuelle, déflatée, de {premiere_ventilee} à {derniere}.
Deux chiffres se lisent en connaissant le découpage : le régime général absorbe
en 2020 les artisans et les commerçants, dont le régime a été adossé à la Cnav,
et les « régimes spéciaux » de la comptabilité nationale contiennent la CNRACL,
c'est-à-dire la fonction publique territoriale et hospitalière.</p>
""", identifiant="cout-depenses")


def _cout_detail_ressources(contexte: Contexte) -> str:
    """La ventilation des ressources au découpage du COR, poste par poste."""
    comptes = contexte.comptes()
    premiere = comptes.premiere_annee_ventilee
    derniere = comptes.derniere_annee_ventilee
    lignes = [
        [escape(poste.libelle),
         g.pourcentage(comptes.part(poste.code, premiere), decimales=1),
         g.pourcentage(comptes.part(poste.code, derniere), decimales=1),
         "oui" if poste.contributive else "non"]
        for poste in POSTES
    ]
    part_cotisee = comptes.part_contributive(derniere)
    return g.depliant("D'où vient l'argent, poste par poste", f"""
<p>Le graphique du haut regroupe les six postes du COR en quatre parts, parce
qu'un empilement à six bandes ne se lit pas. Les voici tels qu'ils sont
publiés.</p>

{g.tableau(
    ["Poste", f"Part en {premiere}", f"Part en {derniere}", "Cotisée"],
    lignes, ["", "nombre", "nombre", ""],
    titre=f"Structure des ressources du système de retraite, {premiere} et {derniere}",
    entete_de_ligne=True,
)}
{g.gloses([(poste.libelle, poste.glose) for poste in POSTES])}
<p class="discret">La colonne « cotisée » dit si le poste est un prélèvement
assis sur un revenu d'activité — la seule ressource qu'un compte notionnel
sache porter au crédit de quelqu'un. {g.pourcentage(part_cotisee, decimales=0)}
des ressources de {derniere} le sont, en comptant la contribution d'équilibre
que l'État verse au régime de ses propres fonctionnaires : le modèle la porte
déjà au compte du système 3, et c'est à ce titre qu'elle est comptée
ici, malgré un taux fixé pour équilibrer plutôt que pour acquérir. La part
cotisée <em>recule</em> : elle était de
{g.pourcentage(comptes.part_contributive(premiere), decimales=0)} en {premiere}.</p>
""", identifiant="cout-ressources")


def _cout_detail_transferts(contexte: Contexte) -> str:
    """Ce que la branche famille et l'assurance chômage versent, et à qui cela revient.

    Le poste « transferts » de la structure des ressources est un agrégat.
    Ce dépliant le ventile par celui qui paie, et dit la chose que le
    coefficient d'équilibre ne dit pas : les scénarios notionnels suppriment
    les droits que la branche famille finance, et comptent pourtant sa recette.
    """
    comptes = contexte.comptes()
    solde = contexte.cout().solde
    premiere = comptes.premiere_annee_transferts
    # La dernière année où tout est connu : les quatre lignes de transfert,
    # et le compte observé qui leur donne un coefficient.
    derniere = min(comptes.derniere_annee_transferts, solde.derniere_annee_observee)
    ligne_solde = solde.annee(derniere)

    def montant(code: str, annee: int) -> str:
        return _milliards(comptes.transfert(code, annee), 1)

    lignes = []
    for organisme in ORGANISMES:
        for poste in POSTES_TRANSFERTS:
            if poste.organisme != organisme.code:
                continue
            lignes.append([
                escape(poste.libelle), montant(poste.code, premiere),
                montant(poste.code, derniere),
                g.pourcentage(comptes.transfert(poste.code, derniere)
                              / comptes.pib(derniere) / comptes.ressource(derniere),
                              decimales=1),
            ])
        lignes.append([
            f"<strong>{escape(organisme.libelle)}, ensemble</strong>",
            _milliards(comptes.transfert_organisme(organisme.code, premiere), 1),
            _milliards(comptes.transfert_organisme(organisme.code, derniere), 1),
            g.pourcentage(comptes.transfert_part_ressources(organisme.code, derniere),
                          decimales=1),
        ])

    part_poste = comptes.part("transferts", derniere)
    part_ventilee = sum(comptes.transfert_part_ressources(o.code, derniere)
                        for o in ORGANISMES)
    supprime = comptes.transfert_supprime_part_pib(derniere)
    # Ce que la recette vaut en part des ressources, l'année où on la connaît ;
    # retirée à part CONSTANTE, elle multiplie tout coefficient par le même
    # facteur, et c'est la seule façon de la porter jusqu'à l'horizon du COR
    # sans projeter ce que personne ne projette.
    part_supprimee = supprime / ligne_solde.ressources
    horizon = solde.annee(solde.derniere_annee)

    def sans_retrait(ligne, scenario: str) -> float:
        """Le coefficient qu'on lirait si cette recette-là restait comptée.

        Celle-là SEULE : la réaction des recettes au taux de la proposition
        reste en place, sans quoi ce dépliant lui attribuerait un écart qui
        n'est pas le sien.
        """
        return (ligne.ressources_de(scenario) + ligne.retrait) / ligne.depense(scenario)
    return g.depliant("Ce que la branche famille et l'assurance chômage versent", f"""
<p>Le poste « transferts d'organismes extérieurs » du tableau précédent est un
agrégat. Le voici ventilé par celui qui paie, lu dans les rapports à la
Commission des comptes de la Sécurité sociale, du côté de la caisse qui verse.</p>

{g.tableau(
    ["Ce qui est versé", f"En {premiere}", f"En {derniere}",
     f"Part des ressources {derniere}"],
    lignes, ["", "nombre", "nombre", "nombre"],
    titre=f"Ce que d'autres caisses versent à la retraite, {premiere} et {derniere}",
    entete_de_ligne=True,
)}
{g.gloses([(poste.libelle, poste.glose) for poste in POSTES_TRANSFERTS])}
<p class="discret">Les deux caisses expliquent
{g.pourcentage(part_ventilee, decimales=1)} des ressources de {derniere}, sur les
{g.pourcentage(part_poste, decimales=1)} du poste « transferts » ; le reste est
fait de versements plus petits, de l'assurance maladie et de l'État pour
l'essentiel. Le COR ventile ce poste pour la dernière année de chaque rapport
depuis 2023 : son « dont Unédic » est exactement la somme des deux lignes de
l'assurance chômage, son « dont CNAF » s'écarte de quelques pour cent de ce que
la branche famille déclare verser, consolidé du côté des régimes qui
reçoivent.</p>

<div class="note"><strong>Ces recettes financent des droits que les scénarios
notionnels ne servent pas.</strong> Les systèmes notionnels suppriment l'assurance
vieillesse des parents au foyer et les majorations pour enfants, et ne portent
rien au compte pendant une année de chômage. Ils comptent pourtant, dans les
ressources qu'ils supposent inchangées, les
{_milliards(comptes.transfert_organisme("famille", derniere), 1)} de la branche
famille et les {_milliards(comptes.transfert_organisme("chomage", derniere), 1)}
de l'assurance chômage de {derniere} — {g.pourcentage(supprime, decimales=2)}
du PIB, {g.pourcentage(part_supprimee, decimales=1)} des ressources. <strong>Le
coefficient d'équilibre du dépliant suivant les leur retire</strong> : année
par année là où on les connaît, à part constante des ressources avant et
après, jusqu'à l'horizon du COR. Sans ce retrait, la proposition afficherait
{g.nombre(sans_retrait(horizon, "notionnel_liberal"), 2)} en
{solde.derniere_annee} au lieu de
{g.nombre(horizon.coefficient("notionnel_liberal"), 2)}, et le système 2
{g.nombre(sans_retrait(horizon, "notionnel_retroactif"), 2)} au lieu
de {g.nombre(horizon.coefficient("notionnel_retroactif"), 2)} ; en
{derniere}, l'écart est du même ordre :
{g.nombre(sans_retrait(ligne_solde, "notionnel_liberal"), 2)} contre
{g.nombre(ligne_solde.coefficient("notionnel_liberal"), 2)}. Ce que la
branche famille cesserait de verser à la retraite ne disparaît pas : il lui
reste, et ce qu'elle en fait est une décision de programme, pas un résultat de
ce modèle.</div>
""", identifiant="cout-transferts")


def _cout_detail_scenarios(contexte: Contexte) -> str:
    """Les quatre systèmes : ce qu'ils auraient coûté, ce qu'ils coûteraient."""
    cout = contexte.cout()
    avenir = cout.avenir
    solde_actuel = cout.solde
    depenses = contexte.depenses()
    euros = cout.annee_euros
    derniere = depenses.derniere_annee
    annees = tuple(ligne.annee for ligne in cout.annees)
    bascule = contexte.base.annee_bascule

    # Un scénario dont la courbe est exactement celle du système actuel serait
    # tracé PAR-DESSUS elle et la ferait disparaître : le graphique montrerait
    # alors une seule courbe en prétendant en montrer trois. On ne trace donc
    # que les scénarios qui s'en écartent, et la légende nomme les autres.
    confondus = cout.confondus_avec_actuel()
    numeros = [libelle.split(".")[0] for scenario, libelle in SCENARIOS_COMPARES
               if scenario in confondus]
    glose_actuel = (
        f"et les scénarios {' et '.join(numeros)}, qui lui sont confondus"
        if numeros else ""
    )
    courbes = tuple(
        g.Serie(
            libelle,
            tuple(ligne.cout_constants(scenario) / 1000 for ligne in cout.annees),
            COULEURS_SCENARIOS[scenario],
            tirets=scenario == "notionnel_liberal",
            glose=glose_actuel if scenario == "actuel" else "",
        )
        for scenario, libelle in SCENARIOS_COMPARES
        if scenario not in confondus
    )
    reference = cout.cumul("actuel")
    dernier = cout.annee(derniere)
    lignes_passe = []
    for scenario, libelle in SCENARIOS_COMPARES:
        cumul = cout.cumul(scenario)
        lignes_passe.append([
            _nom_scenario(scenario, libelle),
            _milliards(cumul, 0),
            g.pourcentage(cumul / reference - 1, signe=True, decimales=1)
            if scenario != "actuel" else "réf.",
            _milliards(dernier.cout(scenario), 1),
            # La part de PIB suit la même règle que le coût : le rapport ne
            # multiplie que les droits directs de la base.
            g.pourcentage(masse_du_scenario(
                dernier.part_pib, dernier.part_derives,
                dernier.rapports[scenario], scenario,
                dernier.reversion_servie, dernier.reforme_en_vigueur),
                decimales=1),
        ])
    lignes_passe.append([
        "<em>dont garantie vieillesse du système 4, financée par l'impôt</em>",
        _milliards(cout.cumul(COMPOSANTE_GARANTIE), 0),
        "—",
        _milliards(dernier.cout(COMPOSANTE_GARANTIE), 1),
        g.pourcentage(masse_du_scenario(
            dernier.part_pib, dernier.part_derives,
            dernier.rapports[COMPOSANTE_GARANTIE], COMPOSANTE_GARANTIE,
            dernier.reversion_servie), decimales=1),
    ])

    horizon = avenir.annee(avenir.derniere_annee)
    depart = avenir.annee(derniere)
    reference_avenir = avenir.cumul("actuel")
    lignes_avenir = []
    for scenario, libelle in SCENARIOS_COMPARES:
        cumul = avenir.cumul(scenario)
        lignes_avenir.append([
            _nom_scenario(scenario, libelle),
            _milliards(horizon.cout_constants(scenario), 0),
            g.pourcentage(horizon.part_pib(scenario), decimales=1),
            _milliards(cumul, 0),
            "réf." if scenario == "actuel"
            else g.pourcentage(cumul / reference_avenir - 1, signe=True, decimales=1),
            "—" if scenario == "actuel"
            else _milliards(avenir.ecart_cumule(scenario), 0),
        ])
    lignes_avenir.append([
        "<em>dont garantie vieillesse du système 4, financée par l'impôt</em>",
        _milliards(horizon.cout_constants(COMPOSANTE_GARANTIE), 0),
        g.pourcentage(horizon.part_pib(COMPOSANTE_GARANTIE), decimales=1),
        _milliards(avenir.cumul(COMPOSANTE_GARANTIE), 0),
        "—",
        "—",
    ])

    horizons = []
    for millesime in range(2030, avenir.derniere_annee + 1, 10):
        ligne = avenir.annee(millesime)
        if ligne is None:
            continue
        horizons.append([
            str(millesime),
            g.nombre(ligne.dependance, 2),
            g.pourcentage(ligne.part_pib("actuel"), decimales=1),
            g.pourcentage(ligne.part_pib("notionnel_retroactif_employeur"),
                          decimales=1),
            g.pourcentage(ligne.part_pib("notionnel_liberal"), decimales=1),
        ])

    return g.depliant("Les quatre systèmes comparés, du passé jusqu'à 2070", f"""
<p>La carte du haut ne montre que la proposition. Voici les quatre systèmes que
le site compare, sur le passé puis sur l'avenir. Le
« système actuel » de ces tableaux est la ligne de référence, pas un
équilibre : il manque de
{g.pourcentage(-solde_actuel.annee(solde_actuel.derniere_annee_observee).solde("actuel"), decimales=2)}
du PIB en {solde_actuel.derniere_annee_observee}, et de
{g.pourcentage(-solde_actuel.annee(solde_actuel.derniere_annee).solde("actuel"), decimales=2)}
en {solde_actuel.derniere_annee} — comparer un scénario à lui, c'est le
comparer à un système qui dérive.</p>

<h4>Ce qu'ils auraient coûté depuis {cout.premiere_annee}</h4>
<p>La dépense observée n'est pas modélisée : elle est ce qu'elle est. Ce qui est
modélisé, c'est le <strong>rapport</strong> entre ce qui a été versé et ce que
chaque système aurait versé aux mêmes retraités — la moyenne des écarts de
pension, pondérée par le poids de chaque génération dans la masse de l'année.
Les poids sont les effectifs réels de chaque génération, lus dans la pyramide
des âges de l'INSEE ; les écarts viennent des treize cas types croisés avec
{len(cout.generations)} générations, de {cout.generations[0]} à
{cout.generations[-1]}.</p>

{g.graphique(
    f"Coût annuel des quatre systèmes, {cout.premiere_annee}-{derniere}, "
    f"en milliards d'euros constants de {euros}",
    annees, courbes, unite=f"Md € {euros}")}

{g.tableau(
    ["Système", f"Cumul {cout.premiere_annee}-{derniere}", "Écart",
     f"Coût {derniere}", f"Part du PIB {derniere}"],
    lignes_passe,
    ["", "nombre", "nombre", "nombre", "nombre"],
    titre=f"Ce que les quatre systèmes auraient coûté de {cout.premiere_annee} "
          f"à {derniere}",
    entete_de_ligne=True,
)}


<p>Le système 2 aurait coûté {_milliards(cout.cumul("notionnel_retroactif"), 0)}
au lieu de {_milliards(reference, 0)}. Cet écart mesure tout autre chose que l'effet des
comptes notionnels. Il mesure deux choses qui n'ont rien à voir avec eux : ce
scénario ne porte au compte que la <strong>part salariale</strong> de la
cotisation, là où le système 3 y ajoute la part patronale et coûte
{_milliards(cout.cumul("notionnel_retroactif_employeur"), 0)}, et il applique une
<a href="{g.lien("/methode", "indexation")}">règle d'indexation</a> dont la page
Méthode montre qu'elle domine tout le reste.</p>

<h4>Ce qu'ils coûteraient d'ici {avenir.derniere_annee}</h4>
<div class="note vigilance"><strong>Point de vigilance : notre projection
s'écarte de celle du COR.</strong> L'assiette de cette section n'est pas celle
des cartes du haut. Le modèle décrit ici des <strong>pensions de répartition
obligatoire</strong> — {_milliards(depenses.repartition(derniere), 1)} en
{derniere} —, il porte son propre niveau de dépense, et ce niveau s'écarte de
celui du COR : il donne {g.pourcentage(horizon.part_pib("actuel"), decimales=1)} du PIB pour le
système actuel en {avenir.derniere_annee}, quand le COR en projette
{g.pourcentage(COR_2070, decimales=1)}. L'écart est de
{g.nombre((horizon.part_pib("actuel") - COR_2070) * 100, 1)} points, et il n'est
pas flatteur : notre {g.terme("taux de remplacement")} ne recule pas, celui du
COR recule. <a href="{g.DEPOT}/blob/main/docs/limites.md">Le § 5 ter des
limites</a> porte la mesure. C'est pourquoi les cartes
du haut n'utilisent du modèle que son <strong>rapport</strong> entre systèmes,
sans dimension, appliqué aux dépenses du COR.</div>

{g.tableau(
    ["Système", f"Coût {avenir.derniere_annee}", f"Part du PIB {avenir.derniere_annee}",
     f"Cumul {avenir.premiere_annee_projetee}-{avenir.derniere_annee}", "Écart",
     "Dont économie"],
    lignes_avenir,
    ["", "nombre", "nombre", "nombre", "nombre", "nombre"],
    titre=f"Ce que chaque système coûterait d'ici {avenir.derniere_annee}",
    entete_de_ligne=True,
)}
<p class="discret">Le cumul porte sur les seules années projetées, en euros
constants de {euros}. <strong>Les trois systèmes notionnels comparés ici sont
des contrefactuels</strong> : ils supposent
recalculées les pensions de gens qui les perçoivent depuis trente ans, ce
qu'aucun droit ne permettrait. Ils répondent à « qu'aurait donné cette règle
si elle avait toujours été la nôtre ? », pas à « que se passerait-il si on la
votait demain ? ». Le modèle sait aussi calculer la seconde question — des
variantes où les droits acquis sont conservés et la règle nouvelle ne vaut que
pour la suite —, mais le site ne les compare plus : la proposition du parti est
rétroactive, et c'est elle qu'il s'agit de chiffrer.</p>

<h4>Ce qui pousse la dépense, et ce qui la retient</h4>
{g.tableau(
    ["Horizon", "65 ans et plus par 20-64 ans", "Système actuel",
     f"Notionnel dès {bascule}", f"Notionnel dès {bascule}, avec l'employeur"],
    horizons,
    ["", "nombre", "nombre", "nombre", "nombre"],
    titre="Dépendance démographique et part de la dépense dans le PIB, par horizon",
    entete_de_ligne=True,
)}
<p class="discret">La première colonne est le rapport de dépendance
démographique de l'INSEE : {g.nombre(depart.dependance, 2)} personne de 65 ans
ou plus par personne de 20 à 64 ans en {derniere},
{g.nombre(horizon.dependance, 2)} en {avenir.derniere_annee}. C'est lui qui
pousse la dépense, et il n'est l'objet d'aucun choix. Ce qui la retient, dans le
système actuel, est l'indexation sur les prix : elle fait décrocher les pensions
des salaires, génération après génération. Les comptes notionnels font la même
chose autrement, par le diviseur d'espérance de vie, mais ils le font
<em>explicitement</em>, et à l'acquisition plutôt qu'au versement.</p>
""", identifiant="cout-scenarios")


def _cout_detail_equilibre(contexte: Contexte) -> str:
    """Le coefficient d'équilibre : de combien il faudrait rogner, ou pouvoir servir."""
    cout = contexte.cout()
    solde = cout.solde
    assiette = contexte.assiette()
    annee_assiette = assiette.derniere_annee
    obs = solde.derniere_annee_observee
    observe = solde.annee(obs)
    horizon = solde.annee(solde.derniere_annee)
    lignes = []
    for scenario, libelle in SCENARIOS_COMPARES:
        equilibre = solde.premiere_annee_equilibree(scenario)
        lignes.append([
            _nom_scenario(scenario, libelle),
            g.pourcentage(observe.solde(scenario), signe=True, decimales=2),
            g.pourcentage(
                solde.solde_moyen(scenario, solde.premiere_annee_projetee,
                                  solde.derniere_annee),
                signe=True, decimales=2),
            g.nombre(observe.coefficient(scenario), 2),
            g.nombre(horizon.coefficient(scenario), 2),
            str(equilibre) if equilibre else "jamais",
        ])
    return g.depliant(
        "Le coefficient d'équilibre : de combien faudrait-il rogner ?", f"""
<p>Un système en comptes notionnels se pilote par un seul chiffre : le facteur
par lequel il faut multiplier <em>toutes</em> les pensions pour que l'année
tombe juste. Il vaut un quand le système s'équilibre, moins de un quand il faut
rogner, plus de un quand il pourrait servir davantage.</p>

{g.tableau(
    ["Système", f"Solde {obs}",
     f"Solde moyen {solde.premiere_annee_projetee}-{solde.derniere_annee}",
     f"Coefficient {obs}", f"Coefficient {solde.derniere_annee}",
     "Équilibre atteint en"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre", "nombre"],
    titre="Solde et coefficient d'équilibre de chaque système, en part du PIB",
    entete_de_ligne=True,
)}
<p class="discret">Les deux premières colonnes sont en part du PIB. Le
coefficient vaut {g.nombre(observe.coefficient("actuel"), 2)} pour le système
actuel en {obs} (il faudrait rogner de

{g.pourcentage(1 - observe.coefficient("actuel"), decimales=1)}), et
{g.nombre(horizon.coefficient("actuel"), 2)} en {solde.derniere_annee}. La
dernière colonne ne regarde que les années projetées : le passé est ce qu'il a
été. Pour le système actuel, dont le rapport vaut un par construction, ces
colonnes redonnent exactement le solde publié par le COR, ce qui dit que
le raccord ne triche pas. Les trois autres systèmes ne comptent pas tout ce que
le système actuel encaisse : ce que la branche famille et l'assurance chômage
versent pour des droits qu'ils ne servent pas, soit

{g.pourcentage(observe.retrait, decimales=2)} du PIB en {obs}, leur est
retiré, à part constante des ressources sur les années projetées. C'est ce
retrait qui creuse leur solde : un système notionnel qui ne sert plus ces
droits ne peut pas en garder les recettes.</p>

<div class="note"><strong>Dix-huit pour cent de quoi ?</strong> Le système 4
remplace tous les taux de cotisation par un seul, parts salariale et patronale
additionnées, et ce taux s'applique à l'ASSIETTE des revenus d'activité : les
salaires et traitements bruts, plus le revenu mixte des non-salariés, soit
{_milliards(assiette.montant(annee_assiette), 0)} en {annee_assiette},
{g.pourcentage(assiette.part_pib(annee_assiette), decimales=1)} du PIB. Le
système de retraite y prélève aujourd'hui
{g.pourcentage(horizon.taux_prelevement, decimales=1)} de ressources en tout, et
la proposition en prélèverait 18 : c'est le rapport de ces deux nombres qui fait
sa recette. Elle ne touche aucune compensation d'allègement, n'en accordant
aucun, et cela ne lui retire rien ici : cette compensation passe par la TVA, qui
finance la branche maladie et n'apparaît pas au compte de la retraite.</div>

<div class="note"><strong>L'autre lecture, plus sévère d'un point de
PIB.</strong> Le modèle sait aussi appliquer aux 18 % la DÉPERDITION du système
actuel : les allègements généraux et les assiettes réduites font qu'un taux
légal proche de
{g.pourcentage(0.18 / horizon.rapports_recettes["notionnel_liberal"], decimales=0)}
ne rentre pas en entier. Compter ainsi revient à supposer que la proposition
garde la même architecture d'exonérations, ce que son texte ne dit pas. Les deux
lectures se défendent, elles sont toutes deux calculées, et la page a retenu la
première.</div>

<div class="note"><strong>Un coefficient supérieur à un est une marge, et
une marge se sert.</strong> Lire les
{g.nombre(horizon.coefficient("notionnel_liberal"), 2)} de la proposition comme
une économie de {g.pourcentage(
    1 - 1 / horizon.coefficient("notionnel_liberal"), decimales=0)} serait un
contresens : à ces recettes-là, ce système servirait davantage que ce que la
colonne « dépense » lui prête, et autrement réparti entre les carrières. Le
modèle calcule ce facteur ; il ne l'applique jamais, et toutes les courbes de
coût de cette page sont celles d'un système qui ne se pilote pas.</div>
""", identifiant="cout-equilibre")


def _cout_detail_garantie(contexte: Contexte) -> str:
    """Ce que la garantie vieillesse coûterait, lue sur la vraie distribution."""
    cout = contexte.cout()
    distribution = contexte.distribution()
    simulateur = contexte.simulateur()
    effectif_retraites = simulateur.effectifs.effectif(
        "tous_regimes", distribution.millesime)
    vers_enquete = simulateur.macro.coefficient_prix(
        contexte.base.annee_euros_garantie_vieillesse, distribution.millesime)
    rapports_liberal = cout.annee(distribution.millesime).rapports
    facteur_contributif = (
        rapports_liberal["notionnel_liberal"] - rapports_liberal[COMPOSANTE_GARANTIE]
    )
    planchers = (
        ("Plancher de base, 800 € (vie à deux)",
         contexte.base.garantie_vieillesse_mensuelle),
        ("Plancher majoré, 1 050 € (personne seule)",
         contexte.base.garantie_vieillesse_mensuelle
         + contexte.base.allocation_isolement_mensuelle),
    )
    assiettes = (
        (f"Pensions de {distribution.millesime}", 1.0),
        ("Pensions du système 4", facteur_contributif),
    )
    lignes = []
    for titre_assiette, facteur in assiettes:
        for titre_plancher, mensuel in planchers:
            chiffre = cout_garantie(
                distribution, effectif_retraites, mensuel * vers_enquete, facteur)
            lignes.append([
                escape(f"{titre_assiette} — {titre_plancher}"),
                g.pourcentage(chiffre.part_beneficiaires, decimales=1),
                g.nombre(chiffre.beneficiaires / 1e6, 1) + " M",
                g.euros(chiffre.complement_moyen_mensuel / vers_enquete),
                _milliards(chiffre.cout_annuel_meur / vers_enquete, 1),
            ])
    garantie_basse = cout_garantie(
        distribution, effectif_retraites,
        contexte.base.garantie_vieillesse_mensuelle * vers_enquete, 1.0)
    garantie_scenario = cout_garantie(
        distribution, effectif_retraites,
        contexte.base.garantie_vieillesse_mensuelle * vers_enquete,
        facteur_contributif)

    return g.depliant("Ce que coûterait la garantie vieillesse", f"""
<p>La garantie du système 4 est <strong>différentielle</strong> : elle ne verse
que ce qui manque à une pension pour atteindre son plancher. Son coût est donc
tout entier celui de la <strong>queue basse de la distribution</strong> des
pensions, et treize carrières de référence ne décrivent pas une distribution :
le chiffre que le tableau des quatre systèmes en tire —
{_milliards(cout.cumul(COMPOSANTE_GARANTIE), 0)} sur soixante-six ans — est
faux, et il faut le remplacer.</p>

<p>L'échantillon interrégimes de retraités de la DREES publie, par tranches de
cent euros, combien de retraités touchent combien. Le barème s'y applique
directement, sans passer par aucun cas type. Deux lectures : ce que la garantie
coûterait <strong>aux pensions d'aujourd'hui</strong>, en remplacement de
l'ASPA (un calcul qui ne doit rien au modèle), et ce qu'elle coûterait
<strong>aux pensions du système 4</strong>, toute la distribution étant alors
déplacée du rapport {g.pourcentage(facteur_contributif, decimales=0)} que le
modèle donne à sa part contributive. Deux planchers aussi, parce que l'enquête
dit la pension sans dire avec qui l'on vit : le coût réel est entre les deux.</p>

{g.tableau(
    ["Assiette et plancher", "Part des retraités", "Bénéficiaires",
     "Complément moyen",
     f"Coût annuel, milliards d'euros {contexte.base.annee_euros_garantie_vieillesse}"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
    titre=f"Coût annuel de la garantie vieillesse, barème appliqué à la "
          f"distribution des pensions de l'EIR {distribution.millesime}",
    entete_de_ligne=True,
)}

<p class="discret">Pensions <strong>brutes de droit direct</strong>, la seule des
huit distributions publiées qui soit dans la même grandeur que celles du modèle.
Les pensions d'une tranche de cent euros sont supposées y être réparties
uniformément, et la tranche ouverte du haut est traitée comme une masse
ponctuelle. Le déplacement des pensions au rapport du système 4 est
<em>proportionnel et uniforme</em>, alors que le scénario ne déplace pas toutes
les carrières du même rapport : les deux dernières lignes sont un ordre de
grandeur là où les deux premières sont un calcul.</p>

<div class="note"><strong>La garantie n'est pas l'ASPA à un autre
montant.</strong> L'ASPA regarde <em>toutes les ressources du foyer</em> et ne
sert rien à un couple à 300 € et 1 500 € ; la garantie ne regarde que la pension
d'une personne, et sert 500 € au premier. C'est ce changement d'assiette, plus
encore que le montant, qui fait passer d'une allocation servie à quelques
centaines de milliers de personnes à une allocation servie à
{g.nombre(garantie_basse.beneficiaires / 1e6, 1)} millions de retraités aux
pensions d'aujourd'hui, et à
{g.nombre(garantie_scenario.beneficiaires / 1e6, 1)} millions à celles du
système 4.</div>
""", identifiant="cout-garantie")



def _cout_detail_capitalisation(contexte: Contexte) -> str:
    """Le pilier capitalisé n'est pas dans ce bilan, et il faut dire pourquoi.

    Une page qui compte ce qui rentre et ce qui sort d'un système en
    répartition doit dire ce qu'elle fait d'un prélèvement qui n'y entre pas.
    Le pilier ne finance aucune pension d'aujourd'hui : il constitue un capital,
    au nom de celui qui verse. Il ne change donc ni les ressources, ni les
    dépenses, ni le solde d'aucun des quatre systèmes comparés — mais il change
    ce que coûte le travail, et c'est cela qu'il faut chiffrer.
    """
    base = contexte.base
    repartition_ = base.taux_cotisation_liberal
    capitalise = base.taux_capitalisation_obligatoire
    total = repartition_ + capitalise
    return g.depliant(
        "Ce que le pilier capitalisé prélève, et pourquoi il n'est pas dans ce bilan",
        f"""
<p>À compter de {base.annee_debut_capitalisation}, le système 4 prélève
{g.pourcentage(capitalise, decimales=0)} de la rémunération <strong>en plus</strong>
des {g.pourcentage(repartition_, decimales=0)} de la répartition. Ces
{g.pourcentage(capitalise, decimales=0)} ne paient aucune pension : ils
constituent un capital au nom de celui qui verse. Ils ne sont donc ni une
ressource ni une dépense du système de retraite, et <strong>aucun des chiffres
de cette page ne les compte</strong> — le solde du système 4 est celui de sa
répartition, comme celui des trois autres.</p>

{g.tableau(
    ["", "Aujourd'hui", "Système 4"],
    [
        ["Prélevé pour la répartition",
         g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0),
         g.pourcentage(repartition_, decimales=0)],
        ["Prélevé pour la capitalisation", "—",
         g.pourcentage(capitalise, decimales=0)],
        ["Total prélevé sur la rémunération",
         g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0),
         f"<strong>{g.pourcentage(total, decimales=0)}</strong>"],
    ],
    ["", "nombre", "nombre"],
    titre="Ce que coûte la retraite à celui qui travaille, part salariale et "
          "patronale additionnées",
    entete_de_ligne=True,
)}

<p>Le total prélevé <strong>baisse de
{g.nombre((TAUX_ACTUEL_TOTAL - total) * 100, 0)} points</strong> :
{g.pourcentage(total, decimales=0)} contre
{g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)} aujourd'hui pour un salarié du
privé. La part qui finance les pensions des autres passe de
{g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)} à
{g.pourcentage(repartition_, decimales=0)} ; ce qui reste,
{g.pourcentage(capitalise, decimales=0)}, revient à celui qui l'a versé — sous
forme de rente à la retraite, ou de capital à ses héritiers s'il meurt
avant.</p>

<div class="note"><strong>Ce que cela ne dit pas.</strong> Le pilier est neutre
pour les comptes publics au moment où il se remplit, mais il ne l'est pas pour
toujours : les versements sont déductibles à l'entrée et la rente imposable à la
sortie, et le modèle ne calcule aucune fiscalité. Il ne dit rien non plus du
coût de transition : un euro prélevé pour être placé cesse d'être disponible
pour payer les pensions d'aujourd'hui. C'est vrai de toute capitalisation, et
c'est ce que ce prélèvement supplémentaire évite, puisqu'il ne prend rien à la
répartition.</div>""",
        identifiant="cout-capitalisation",
    )


def _cout_detail_poids(contexte: Contexte) -> str:
    """Ce que chaque carrière type pèse dans les agrégats de la page."""
    cout = contexte.cout()
    derniere = contexte.depenses().derniere_annee
    lignes = [
        [escape(cas.libelle),
         ", ".join(caisse.replace("_", " ") for caisse in cas.caisses),
         g.pourcentage(cout.poids.get(cas.code, 0.0), decimales=1),
         g.pourcentage(1 / len(CAS_TYPES), decimales=1)]
        for cas in sorted(CAS_TYPES, key=lambda c: -cout.poids.get(c.code, 0.0))
    ]
    return g.depliant("Ce que chaque carrière type pèse dans ces chiffres", f"""
<p><strong>Deux pondérations se composent.</strong> Celle de la génération est
démographique, et vient de l'INSEE. Celle du <strong>cas type</strong> est
sociologique (combien de retraités ont eu cette carrière-là), et vient des
effectifs que la DREES publie caisse par caisse. La colonne de droite rappelle
ce que valait la convention antérieure, qui les pesait à égalité.</p>

{g.tableau(
    ["Cas type", "Caisse dont il porte les retraités",
     f"Poids en {derniere}", "Ancienne convention"],
    lignes,
    ["", "", "nombre", "nombre"],
    titre=f"Ce que chaque cas type pèse dans les agrégats de cette page, en {derniere}",
    entete_de_ligne=True,
)}
<p class="discret">Une caisse réclamée par plusieurs cas types se partage
également entre eux : la Cnav est celle des quatre carrières du privé, et aucune
source ne dit combien de ses retraités ont été cadres. Hors de la fenêtre que la
DREES publie (2004 à 2024), la répartition du bord est reconduite : la France
de 1960 comptait plus d'exploitants agricoles que ces poids ne le disent.</p>
""", identifiant="cout-poids")


def _cout_detail_sources(contexte: Contexte) -> str:
    """Trois séries, trois périmètres, et pourquoi ils ne se confondent pas."""
    comptes = contexte.comptes()
    depenses = contexte.depenses()
    cout = contexte.cout()
    solde = cout.solde
    derniere = depenses.derniere_annee
    return g.depliant("D'où viennent ces chiffres", f"""
<p>Cette page croise deux producteurs de comptes, et ils ne comptent pas la
même chose. Rien n'est mélangé pour autant : du modèle, les deux premières
cartes n'empruntent qu'un <strong>rapport</strong> entre systèmes, qui est sans
dimension.</p>

<h4>Le compte du système de retraite — Conseil d'orientation des retraites</h4>
<p>Dépenses, ressources et solde du même ensemble de régimes, sous la même
convention, de {solde.premiere_annee} à {solde.derniere_annee}. Champ : régimes
légalement obligatoires, FSV compris, RAFP exclu — ni dépendance, ni
capitalisation. {g.pourcentage(comptes.depense(derniere), decimales=2)} du PIB
en {derniere}. C'est la source des deux premières cartes et de celle sur la
réforme.</p>
<p class="discret">On lui prend les DEUX colonnes, jamais une seule : un solde
ne se fabrique pas en soustrayant deux périmètres. On aurait voulu les
ressources du même producteur que la dépense ci-dessous ; elles n'existent
pas. <strong>Les comptes de la protection sociale ne ventilent pas leurs
ressources par risque</strong> — une « recette du risque vieillesse » est une
donnée sans définition comptable, les cotisations d'un régime polyvalent
n'étant affectées à aucun risque.</p>

<h4>Ce que d'autres caisses versent — rapports à la Commission des comptes de
la Sécurité sociale</h4>
<p>Le poste « transferts » du compte du COR, ventilé par celui qui paie, de
{comptes.premiere_annee_transferts} à {comptes.derniere_annee_transferts} :
la fiche de la CNAF pour l'assurance vieillesse des parents au foyer et les
majorations pour enfants, celles de l'Agirc-Arrco et de l'Ircantec pour les
points des chômeurs que l'Unédic paie. C'est la source du dépliant « Ce que la
branche famille et l'assurance chômage versent ».</p>
<p class="discret">Un rapport n'est lu que pour ses comptes arrêtés, et le
premier qui arrête une année l'emporte. Les rapports d'avant 2013 sont chiffrés
ou compressés d'une façon que le lecteur du dépôt n'ouvre pas : la série
commence là.</p>

<h4>Les comptes de la protection sociale — DREES</h4>
<p>La dépense, risque par risque, depuis {cout.premiere_annee}. Le risque
<strong>vieillesse-survie</strong> entier vaut
{g.pourcentage(depenses.part_pib(derniere), decimales=2)} du PIB en {derniere},
et la <strong>répartition obligatoire</strong> seule
{g.pourcentage(depenses.repartition(derniere) / depenses.pib(derniere), decimales=2)}.
C'est la source de la carte « est-ce que ça a toujours coûté autant ».</p>
<p class="discret">Moins de trois dixièmes de point séparent cette répartition
obligatoire du périmètre du COR : c'est le meilleur recoupement dont ces deux
séries disposent, et un test du dépôt le tient.</p>

<h4>Le modèle du dépôt</h4>
<p>Treize carrières types croisées avec {len(cout.generations)} générations, de
{cout.generations[0]} à {cout.generations[-1]}, pesées par les effectifs réels
de l'INSEE et par les effectifs de retraités que la DREES publie caisse par
caisse. Il ne produit qu'un rapport de masses de pension — jamais un niveau de
dépense dans les cartes du haut.</p>
<p class="discret">Fiabilité : la dépense observée est
<strong>certifiée</strong>, recontrôlée contre l'API de la DREES à chaque
exécution ; le compte du COR est <strong>de niveau haut</strong>, consolidé par
lui depuis les rapports à la Commission des comptes de la Sécurité sociale ; et
tout ce qui passe par un rapport de masses est <strong>estimé</strong>, sans
pouvoir être autre chose — aucune institution ne publie ce qu'aurait coûté un
système qui n'a pas existé. Tout est détaillé sur la page
<a href="{g.lien("/donnees")}">Données</a>.</p>
""", identifiant="cout-sources")


def _cout_detail_limites(contexte: Contexte) -> str:
    """Tout ce que cette page ne dit pas, en une seule liste."""
    cout = contexte.cout()
    solde = cout.solde
    avenir = cout.avenir
    observe = solde.annee(solde.derniere_annee_observee)
    return g.depliant("Douze réserves à lire avant de citer ces chiffres",  f"""
<p>Une page de chiffres vaut par ce qu'elle laisse de côté, et cette page en
laisse douze, écrits ici plutôt qu'en note de bas de page.</p>
<ul class="serree">
  <li><strong>Les recettes réagissent sur trois points, et sur trois
  seulement.</strong> La recette suit le droit : ce que la branche famille,
  l'assurance chômage et le fonds de solidarité vieillesse versent pour des
  droits que les systèmes notionnels ne servent pas leur est retiré, un peu
  plus d'un point de PIB. La recette suit le taux : le système 4, qui pose un
  taux unique de 18 %, prélève ce taux sur l'assiette mesurée des revenus
  d'activité au lieu de la part cotisée des ressources d'aujourd'hui. La
  recette suit enfin le PRINCIPE, et pour le seul système 4 : un compte
  notionnel ne crédite que ce qui est assis sur un revenu d'activité, et ce
  système ne reconduit donc aucune des trois ressources qui n'acquièrent de
  droits à personne. La contribution d'équilibre de l'État s'en va parce que
  les 18 % s'appliquent aussi aux traitements des fonctionnaires, et que la
  reconduire la compterait deux fois. Les subventions d'équilibre aux régimes
  en extinction s'en vont parce que la fusion de tous les régimes supprime la
  catégorie même du retraité sans cotisants. Les impôts et taxes affectés s'en
  vont parce qu'un impôt n'ouvre de droit à personne. Trois postes : 27 % des
  ressources en 2024, 29 % en 2070. Les cinq autres systèmes les encaissent
  tous, faute qu'aucun programme dise ce qu'il en ferait.</li>
  <li><strong>L'assiette est supposée insensible au taux.</strong> Un taux de
  cotisation plus bas déforme l'offre de travail et la structure des
  rémunérations ; aucune élasticité n'est posée ici, et le sens de l'effet
  joue plutôt en faveur du système 4. Au-delà de la dernière année où
  l'assiette est publiée, c'est le TAUX DE PRÉLÈVEMENT qui est reconduit et
  non la part de PIB de l'assiette : celle-ci suit alors les ressources
  projetées par le COR, dont la baisse en part de PIB tient précisément à une
  assiette qui progresse moins vite que le PIB.</li>
  <li><strong>Le coefficient d'équilibre n'est jamais appliqué.</strong>
  L'appliquer changerait toutes les pensions par un même facteur, donc tous les
  niveaux de cette page, sans toucher aux écarts entre carrières, qui sont la
  seule chose que ce site mesure.</li>
  <li><strong>L'année du retour à l'équilibre se lit à quelques années
  près.</strong> Le déficit actuel vaut
  {g.pourcentage(abs(observe.solde("actuel")), decimales=2)} du PIB, c'est-à-dire
  l'ordre de grandeur de l'écart que le pas de la grille des générations
  introduit à lui seul autour de la bascule.</li>
  <li><strong>Les réserves ne sont pas comptées.</strong> Le système de retraite
  détient des réserves financières que le COR chiffre à part ; un solde annuel
  négatif peut être couvert par elles pendant des années. Le solde dit le flux,
  jamais le stock.</li>
  <li><strong>La projection est celle du COR</strong>, scénario de référence,
  avec ses hypothèses : démographie de l'INSEE, productivité, chômage. Ses
  ressources reculent en part de PIB parce que l'assiette des cotisations y
  progresse moins vite que le PIB : cette hypothèse est la sienne, et personne
  ne l'a mesurée. Seize autres scénarios démographiques existent, dont l'écart
  mesurerait l'incertitude ; cette page n'en montre aucun.</li>
  <li><strong>Le taux de couverture est supposé constant.</strong> Le modèle
  compte des générations, non des cotisants : il suppose que la même proportion
  de chaque génération perçoit une pension, et que la carrière type ne change
  pas. Un recul de l'âge de départ, une carrière plus longue ou plus hachée
  déplaceraient la trajectoire.</li>
  <li><strong>Un effectif de caisse n'est pas un effectif de personnes.</strong>
  Un polypensionné compte dans chacune de ses caisses, ce qui gonfle le poids
  des régimes dont les affiliés ont typiquement aussi une carrière au régime
  général.</li>
  <li><strong>Avant 1975, la reconstitution est mince.</strong> La répartition
  ne commence qu'en {contexte.base.annee_debut_repartition} : les générations
  antérieures à {cout.generations[0]} n'ont, dans ce modèle, aucune pension, et
  plusieurs régimes n'existaient pas encore. Les premières années reposent donc
  sur deux ou trois générations et la moitié des cas types.</li>
  <li><strong>La grille échantillonne une génération sur cinq.</strong> Une
  cohorte qui part juste avant la bascule est donc représentée par une
  génération qui part juste après : les courbes de réforme s'écartent d'un ou
  deux dixièmes de point avant même la bascule. Un test borne l'effet à un
  demi-point.</li>
  <li><strong>Seul le système actuel sert la pension de réversion.</strong>
  Une réversion est ce qu'un conjoint survivant reçoit de la carrière d'un
  autre : c'est la première dépense non contributive du système, un dixième
  environ de tout ce qui est versé. Les systèmes notionnels comparés ici
  retirent tous les avantages non contributifs, et celui-là comme les autres :
  ils ne rendent que ce qui a été cotisé, et c'est précisément ce qu'ils
  servent à mesurer. Le système actuel, lui, la sert, puisqu'il est le droit en
  vigueur. Les systèmes qui ne valent que pour l'avenir la servent jusqu'à leur
  bascule, n'étant jusque-là rien d'autre que le système actuel. Ensuite ils ne
  la servent plus, aux veuves d'avant comme à celles d'après.</li>
  <li><strong>Rien de tout cela n'est certifié, et ne peut l'être.</strong> Une
  projection est une hypothèse : celle de l'INSEE pour la démographie, celle du
  COR pour la macroéconomie, celle du modèle pour les pensions — jusqu'en
  {avenir.derniere_annee}, horizon des projections de population, et pas un an
  de plus.</li>
</ul>
<p class="discret">Les limites du modèle dans son ensemble sont dans
<a href="{g.DEPOT}/blob/main/docs/limites.md">docs/limites.md</a>, et la
méthode sur la page <a href="{g.lien("/methode")}">Méthode</a>.</p>
""", identifiant="cout-limites")


#: Les neuf règles que compare la page Méthode, dans l'ordre d'affichage :
#: libellé, mode, fenêtre de lissage. L'ordre n'est pas celui des valeurs — il
#: va de la règle demandée à celle que la théorie désigne, en passant par celle
#: que le droit applique.
REGLES_COMPAREES: tuple[tuple[str, ModeIndexation, int], ...] = (
    ("Triple lock inversé, littéral", ModeIndexation.TRIPLE_LOCK_INVERSE, 1),
    ("Moyenne des trois taux", ModeIndexation.MOYENNE_TROIS_TAUX, 1),
    ("Triple lock inversé, tout en nominal",
     ModeIndexation.TRIPLE_LOCK_INVERSE_NOMINAL, 1),
    ("Indexation sur les prix", ModeIndexation.PRIX, 1),
    ("Médiane des trois taux", ModeIndexation.MEDIANE_TROIS_TAUX, 1),
    ("Revalorisation réellement pratiquée",
     ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE, 1),
    ("Masse salariale (règle d'équilibre)", ModeIndexation.MASSE_SALARIALE, 1),
    ("PIB nominal", ModeIndexation.PIB_NOMINAL, 1),
    ("PIB nominal lissé sur 5 ans (Italie)", ModeIndexation.PIB_NOMINAL, 5),
)

#: Bornes du cumul comparé. Une somme versée en 1940 est revalorisée à partir de
#: l'année SUIVANTE : les taux appliqués sont donc ceux de 1941 à 2025 inclus,
#: ce que l'intitulé de la colonne appelle « appliquée 1941-2025 ».
ANNEE_VERSEMENT_COMPARE = 1940
ANNEE_ARRIVEE_COMPAREE = 2025


#: La cotisation et les deux liquidations qui illustrent la loterie de cohorte.
#: 2020 est l'année du trou ; liquider un an plus tard rapportait alors moins.
ANNEE_COTISATION_LOTERIE = 1980
LIQUIDATIONS_LOTERIE = (2019, 2020)


def _loterie_de_cohorte(contexte: Contexte) -> dict[str, str]:
    """Ce que vaut une même cotisation selon l'année où l'on liquide.

    Quatre coefficients : la cotisation de 1980 portée à 2019 puis à 2020, sans
    lissage puis lissée sur cinq ans. Deux passages du site les citent en toutes
    lettres pour montrer qu'attendre un an pouvait faire perdre — autant qu'ils
    les lisent au même endroit, et que cet endroit soit le modèle.
    """
    from ..moteur.indexation import Indexation

    simulateur = contexte.simulateur()
    valeurs: dict[str, str] = {}
    for lissage in (1, 5):
        parametres = replace(simulateur.parametres,
                             mode_indexation=ModeIndexation.PIB_NOMINAL,
                             lissage_indexation=lissage)
        indexation = Indexation(simulateur.macro, parametres)
        for arrivee in LIQUIDATIONS_LOTERIE:
            coefficient = indexation.coefficient(ANNEE_COTISATION_LOTERIE, arrivee)
            valeurs[f"{lissage}|{arrivee}"] = "×" + g.nombre(coefficient, 2)
    return valeurs


def _cumuls_indexation(contexte: Contexte) -> dict[str, float]:
    """Rendement cumulé de chaque règle comparée, sur 1941-2025.

    Ces neuf nombres étaient écrits à la main dans la page — les seuls du site
    à ne pas sortir du modèle. Ils ne dépendent d'aucune carrière, ce qui les
    rendait faciles à recopier, et l'un d'eux avait fini par mentir de trois
    dixièmes de point. Les calculer coûte quatre millisecondes, soit moins que
    n'importe quelle simulation de cette page.
    """
    from ..moteur.indexation import Indexation

    simulateur = contexte.simulateur()
    cumuls: dict[str, float] = {}
    for libelle, mode, lissage in REGLES_COMPAREES:
        parametres = replace(simulateur.parametres, mode_indexation=mode,
                             lissage_indexation=lissage)
        cumuls[libelle] = Indexation(simulateur.macro, parametres).coefficient(
            ANNEE_VERSEMENT_COMPARE, ANNEE_ARRIVEE_COMPAREE)
    return cumuls

def _methode(contexte: Contexte) -> str:
    """Comment une pension est calculée, et ce qui décide du résultat.

    C'est la page la plus technique du site, et c'est celle qui avait le plus
    besoin d'un ordre de lecture. Elle alignait huit sections de même poids : le
    calcul du compte, la règle d'indexation, le droit que le système 1
    reproduit, ce que les scénarios notionnels suppriment, la fusion, les
    métiers, les unités, le périmètre. Rien n'y disait laquelle compte.

    Une seule compte, et la page le dit maintenant en tête : LA RÈGLE
    D'INDEXATION DOMINE TOUT LE RESTE. C'est elle qui explique l'essentiel de
    l'écart affiché par les scénarios rétroactifs, et non le passage aux comptes
    notionnels — un résultat que la page portait au milieu d'un paragraphe.
    Elle est donc seule visible, sous la forme d'une question et de son tableau ;
    le reste est replié, dans l'ordre où on vient le chercher.
    """
    cumuls = _cumuls_indexation(contexte)
    prix = cumuls["Indexation sur les prix"]
    lignes_indexation = []
    for libelle, _, _ in REGLES_COMPAREES:
        valeur = cumuls[libelle]
        conserve = g.pourcentage(valeur / prix, decimales=1)
        if libelle == REGLES_COMPAREES[0][0]:
            # La règle demandée est celle que la page vient d'annoncer : c'est
            # son chiffre qu'on vient lire, et il est mis en valeur.
            conserve = f"<strong>{conserve}</strong>"
        lignes_indexation.append([
            libelle, "×" + g.nombre(valeur, 1), "×" + g.nombre(prix, 1), conserve,
        ])
    conserve_litteral = g.pourcentage(
        cumuls[REGLES_COMPAREES[0][0]] / prix, decimales=1)
    reval_pratiquee = cumuls["Revalorisation réellement pratiquée"]
    masse_salariale = cumuls["Masse salariale (règle d'équilibre)"]
    loterie = _loterie_de_cohorte(contexte)

    calcul = g.points([
        ("1. On inscrit",
         "Chaque cotisation retraite réellement versée est portée au compte, "
         "au premier euro et sans plafond."),
        ("2. On revalorise",
         "Le solde est augmenté chaque année d'un taux fixé par la règle "
         "collective : par défaut, le rythme auquel progresse la masse des "
         "salaires."),
        ("3. On divise",
         "Au départ, <code>pension = solde ÷ espérance de vie restante</code>, "
         "lue sur la table de votre génération."),
    ])

    tableau_indexation = g.tableau(
        ["Règle appliquée 1941-2025", "Comptes", "Prix",
         "Pouvoir d'achat conservé"],
        lignes_indexation,
        ["", "nombre", "nombre", "nombre"],
        titre="Ce que chaque règle d'indexation aurait conservé du pouvoir "
              "d'achat, 1941-2025",
        entete_de_ligne=True,
    )

    carte = g.cle(
        "Qu'est-ce qui décide du résultat ?",
        f"""La règle de revalorisation, et de très loin. Selon celle qu'on
retient, une cotisation de 1950 conserve {conserve_litteral} de sa valeur, ou
onze fois plus. <strong>C'est de là que vient l'essentiel de l'écart affiché par
les scénarios rétroactifs</strong>, bien plus que du passage aux comptes notionnels.""",
        tableau_indexation,
        """La règle appliquée par défaut est la croissance de la masse des
salaires : ce qu'un système en répartition peut servir sans toucher à son taux.
Les huit autres restent à un clic, dans les options du simulateur.""",
    )

    tete = g.affiche(
        "La méthode",
        "Comment c'est calculé, "
        '<span class="cle-texte">en trois opérations.</span>',
        "Un compte notionnel est un compte <em>virtuel</em> : rien n'est "
        "placé, les cotisations de l'année paient les pensions de l'année. "
        "Ce qui change, c'est le calcul du droit.",
    )

    return f"""
{tete}

<div class="note resume"><strong>En clair.</strong> Votre pension serait votre
compte divisé par le nombre d'années qu'il vous reste à vivre, en moyenne.
Chaque euro cotisé compte, et rien d'autre : ni trimestres, ni minimum, ni
majoration. Le compte grossit chaque année au rythme de la masse des
salaires, c'est-à-dire de ce que la répartition peut promettre sans mentir.
Le système actuel, lui, est recalculé règle par règle sur la même carrière,
pour servir de point de comparaison.</div>

{calcul}

<p>Trois conséquences. La pension est exactement proportionnelle aux
cotisations. Partir tôt coûte deux fois : moins de cotisations, et une pension à
servir plus longtemps. Et aucun droit qu'une cotisation n'a pas financé
n'existe. C'est la règle que <a href="{g.lien("/")}">le programme</a> propose,
et <a href="{g.lien("/cas-types")}">treize carrières types</a> montrent ce
qu'elle déplace, génération par génération.</p>

{carte}

<p class="actions"><a class="bouton" href="{g.lien("/simuler")}">Voir le calcul
sur une carrière</a><a href="{g.DEPOT}/blob/main/docs/methodologie.md">La
méthodologie complète</a></p>

<h2>Pour aller plus loin</h2>

{_methode_indexation(contexte, reval_pratiquee, masse_salariale, loterie)}
{_methode_capitalisation(contexte)}
{_methode_droit_positif()}
{_methode_suppressions()}
{_methode_carriere(contexte)}
{_methode_unites()}
{_methode_construction()}
"""



def _methode_capitalisation(contexte: Contexte) -> str:
    """Le pilier capitalisé : où va l'argent, à quel taux, à quel prix.

    C'est la seule partie du modèle qui place réellement de l'argent, et donc
    la seule qui dépende d'un marché. Elle doit dire trois choses qu'aucune
    autre section n'a à dire : d'où viennent les taux, ce que le placement
    suppose, et ce que la transmission change à la comparaison avec la
    répartition.
    """
    from ..donnees.taux import CourbeTauxSansRisque
    from ..moteur.capitalisation import MATURITES, repartition

    base = contexte.base
    courbe = CourbeTauxSansRisque(base.racine_donnees)
    taux = g.pourcentage(base.taux_capitalisation_obligatoire, decimales=0)

    comptants = g.tableau(
        ["Maturité", "Taux zéro-coupon, en rythme annuel"],
        [[f"{maturite} ans",
          g.pourcentage(courbe.placement(courbe.annee, maturite).taux, decimales=2)]
         for maturite in MATURITES],
        ["", "nombre"],
        titre=f"La courbe employée, au {_date_en_clair(courbe.date)}",
        entete_de_ligne=True,
    )

    # L'allocation, telle que la règle la produit : ce sont les poids que le
    # moteur applique, lus par le même code. Une table écrite à la main
    # pourrait se désaccorder du calcul ; celle-ci ne le peut pas.
    horizons = (40, 30, 20, 10, 5, 2)
    glissement = g.tableau(
        ["Années avant le départ", "Répartition du versement par maturité"],
        [[str(horizon),
          ", ".join(f"{g.pourcentage(poids)} à {maturite} an"
                    f"{'s' if maturite > 1 else ''}"
                    for maturite, poids in repartition(horizon))]
         for horizon in horizons],
        ["nombre", ""],
        titre="Où va un versement selon ce qu'il reste à courir",
        entete_de_ligne=True,
    )

    return g.depliant(
        f"Le pilier capitalisé : {taux} placés, ce que cela suppose",
        f"""
<p>La proposition ajoute, à compter de {base.annee_debut_capitalisation}, une
cotisation de {taux} prélevée sur la même assiette que la cotisation de
répartition, <strong>en plus</strong> d'elle : elle ne s'y substitue pas. Elle
n'entre pas au compte notionnel, elle constitue un capital au nom du cotisant,
dans un plan d'épargne retraite. Les années antérieures gardent les taux qui étaient les
leurs et ne versent rien.</p>

<h3>Où l'argent est placé</h3>
<p>Sur des titres sans risque, portés jusqu'à leur échéance. La courbe retenue
est celle des souverains les mieux notés de la zone euro, que la Banque centrale
européenne publie chaque jour ouvré : c'est la définition opérationnelle du taux
sans risque en euro. L'OAT française rend davantage : une cinquantaine de points
de base au dix ans. Cet écart rémunère un risque de crédit, et un régime
obligatoire qui promet une rente ne peut pas le compter comme un rendement
acquis. Retenir la courbe la mieux notée est donc le choix prudent, et il
réduit la rente affichée.</p>
{comptants}
<p>Les versements des années suivantes ne se placent pas à ces taux-là, mais aux
taux À TERME que cette même courbe implique, ceux que le marché cote déjà pour
une période future. C'est ce qui dispense le modèle d'une prévision de taux :
le forward n'est pas une opinion, il est arbitré. <strong>Ce qu'il suppose</strong>
tient en une phrase : que le taux futur sera, en moyenne, le forward
d'aujourd'hui. C'est l'hypothèse des anticipations pures, et elle ignore la
prime de terme, c'est-à-dire le supplément qu'un prêteur exige pour immobiliser
son argent. Quand la courbe monte, elle flatte donc légèrement le pilier.
Au-delà de trente ans, la courbe ne dit plus rien : le taux est prolongé à plat,
et tout résultat qui en dépend est déclaré « estimé ».</p>

<h3>Selon quelle règle les maturités sont choisies</h3>
<p>Longues tant que le départ est loin, courtes à l'approche : c'est
l'allocation par horizon que toute épargne à échéance pratique. Aucune ligne
n'arrive à échéance après le départ, car il faudrait la vendre avant terme, à un
prix qui n'est plus sans risque ; à l'échéance d'une ligne, son produit est
replacé selon la même règle, pour ce qu'il reste à courir. Aucune maturité
ne dépasse les trois quarts du versement : une épargne obligatoire ne se
concentre pas sur un seul point de la courbe.</p>
{glissement}

<h3>Ce que l'enveloppe coûte</h3>
<p>Trois prélèvements, ceux du plan d'épargne retraite tel qu'il est vendu
aujourd'hui, mesurés par l'Observatoire des produits d'épargne financière sur
les remises de l'ACPR :
{g.pourcentage(base.frais_versement_capitalisation, decimales=2)} sur chaque
versement, {g.pourcentage(base.frais_gestion_capitalisation, decimales=2)} par
an sur l'encours, {g.pourcentage(base.frais_arrerages_capitalisation, decimales=2)}
sur chaque arrérage de rente. Ce sont les frais d'un produit vendu à des
volontaires, contrat par contrat, et la commission du réseau qui le place en est
l'essentiel : elle n'aurait pas d'objet si la cotisation était obligatoire. Les
retenir tels quels est donc une <strong>borne haute</strong>, assumée comme
telle : le modèle dit ce que la proposition coûterait si rien ne bougeait dans
la tarification.</p>

<h3>Comment le capital devient une rente</h3>
<p>Par le mécanisme du plan d'épargne retraite : le capital est divisé par un
coefficient actuariel, puis chaque arrérage supporte ses frais. Le coefficient
est celui du modèle (table de génération, unisexe par défaut), et le taux
technique est nul, comme dans la plupart des contrats. Les deux lignes du
système 4 partagent alors le MÊME diviseur, et deviennent comparables au
centime : à capital égal elles servent le même montant, et tout écart vient
d'ailleurs.</p>

<h3>Ce qui se transmet</h3>
<p>Le capital, intégralement, si le cotisant meurt avant d'avoir liquidé. C'est
la règle du plan d'épargne retraite, et c'est ce que la répartition ne fait
pas : un compte notionnel n'est pas un capital, il est un droit, et il s'éteint
avec son titulaire sans rien laisser. Après la liquidation, la rente est
viagère et ne se transmet pas davantage : une rente réversible ou à annuités
garanties serait plus faible, et le modèle ne la retient pas.</p>

<h3>Ce que le modèle ne fait pas</h3>
<p>Il ne simule aucun risque de marché : le pilier est placé sans risque par
construction, et le seul aléa qui subsiste, celui de taux futurs s'écartant des
forwards d'aujourd'hui, n'est pas chiffré. Il ne calcule aucune fiscalité :
tous les montants du site sont bruts, ici comme ailleurs, alors que les
versements au plan sont déductibles et la rente imposable. Et la garantie
vieillesse ne regarde pas cette rente : elle est servie sur la seule pension
contributive de répartition. Savoir si un pilier capitalisé doit réduire une
allocation différentielle est une question de droit, pas de modèle.</p>""",
        identifiant="capitalisation",
    )


def _methode_indexation(contexte: Contexte, reval_pratiquee: float,
                        masse_salariale: float, loterie: dict[str, str]) -> str:
    """Le détail du tableau d'indexation, ligne par ligne.

    Cinq paragraphes qui ne se lisent qu'une fois qu'on a vu le tableau, et qui
    répondent chacun à une question précise : d'où vient la règle demandée, ce
    qu'est la seule ligne qui ne soit pas une hypothèse, ce que la théorie
    désigne, à quoi sert un lissage, et pourquoi le minimum plutôt qu'autre
    chose.
    """
    return g.depliant("Le détail des neuf règles d'indexation", f"""
<p><strong>Le triple lock inversé</strong> —
<code>min(inflation, croissance du salaire moyen, productivité réelle)</code> —
est la règle qui a donné son cahier des charges à ce simulateur. Prise à la
lettre, elle compare deux taux nominaux à un taux réel, et c'est ce qui la rend
si sévère.</p>

<p><strong>« Revalorisation réellement pratiquée » est la seule ligne qui ne soit
pas une hypothèse</strong> : c'est le coefficient que les arrêtés annuels ont
appliqué aux salaires portés au compte, celui dont le système 1 se sert pour
calculer le {g.terme("salaire de référence")}. Il vaut
<strong>×{g.nombre(reval_pratiquee, 0)}</strong> sur la période, près de cinq
fois les prix, parce que le régime général a revalorisé sur les SALAIRES
jusqu'en 1986 et sur les prix seulement depuis 1987. C'est donc elle, plutôt que
« Indexation sur les prix », qui neutralise la question de l'indexation quand on
veut isoler l'effet propre des comptes notionnels. Sur une carrière
(un salarié du privé non cadre au salaire moyen, entré à 20 ans et parti
à 62), la correction reste modeste : +5,2 points pour la génération 1920,
+0,0 pour 1945, -0,4 pour 1958. Les cotisations se concentrent sur les dernières années, là où
les deux règles coïncident.</p>

<p><strong>« Masse salariale » est ce que la théorie désigne.</strong> En
répartition, le rendement qu'un système peut servir sans changer son taux est la
croissance de son assiette, le salaire moyen multiplié par l'emploi salarié
(Samuelson 1958, Aaron 1966). C'est le taux d'indexation des comptes notionnels
suédois, italiens, polonais et lettons, à des variantes près. Sur 1941-2025 il
vaut ×{g.nombre(masse_salariale, 0)}, onze fois les prix : l'emploi salarié a
doublé depuis 1950, et cette croissance-là s'ajoute chaque année à celle des
salaires. Une réserve : ce rendement est celui du système ENTIER, alors que les
le système 2 ne porte au compte que la part salariale de la cotisation.
C'est au système 3 qu'il faut le comparer.</p>

<p><strong>Le PIB nominal</strong> pousse la même idée à l'assiette la plus
large : il gagne ce que la masse salariale perd quand la valeur ajoutée se
déplace vers les revenus non salariaux. La dernière ligne y ajoute un
<strong>lissage sur cinq ans</strong>, comme le fait l'Italie.</p>

<p><strong>Le lissage est un réglage à part</strong>, qui s'ajoute à n'importe
quelle règle : une moyenne glissante du taux qu'elle produit. Il vise moins
le niveau que la <strong>loterie de
cohorte</strong> : sur le PIB nominal brut, une cotisation de
{ANNEE_COTISATION_LOTERIE} vaut {loterie["1|2019"]} à une liquidation de 2019 et
{loterie["1|2020"]} en 2020 : attendre un an fait <em>perdre</em>, parce que
l'année traversée s'est mal passée. Lissée sur cinq ans, elle vaut
{loterie["5|2019"]} puis {loterie["5|2020"]} : le trou de 2020 est absorbé par
les quatre années qui l'entourent au lieu d'être porté en entier par qui a eu le
tort de liquider cette année-là. Sur 1950-2025, le PIB nominal brut compte deux
années où liquider plus tard rapporte moins ; lissé sur trois ou cinq ans,
aucune.</p>

<p class="discret">Deux réserves pour lire le tableau. Sur quatre-vingts ans, une
moyenne glissante n'est pas neutre : elle mesure la croissance depuis une base
reculée d'environ la moitié de la fenêtre, ce qui gonfle le cumul d'une
vingtaine de pour cent à cinq ans, sans qu'aucune série ait changé ; sur une
carrière, l'écart reste d'un à deux points. Et la règle italienne n'est reprise
ici que par son taux, non par le reste du système italien. Enfin, le minimum
n'est pas la seule statistique possible sur ces trois séries : la
<strong>médiane</strong> est un taux nominal trois années sur quatre, donc elle
suit les prix et cesse d'être une règle d'austérité ; la <strong>moyenne</strong>
est plus sévère que les prix, parce qu'elle incorpore un tiers de productivité
réelle <em>chaque</em> année. Les deux sont dans les options.</p>""")


def _methode_droit_positif() -> str:
    """Ce que l'étalon reproduit du droit en vigueur.

    L'étalon ne vaut que par ce qu'il reproduit : c'est le seul argument qui
    rende lisible un écart de pension, et il tient dans une liste.
    """
    return g.depliant("Ce que le système 1 applique du droit en vigueur", f"""
<p>L'étalon ne vaut que par ce qu'il reproduit. Il applique la
{g.terme("décote")} et la {g.terme("surcote")}, la proratisation par la
{g.terme("durée", "durée d'assurance")}, le {g.terme("salaire de référence")}
de chaque régime (sur ses seules années, jamais sur toute la carrière), et cinq
paramètres lus à la génération plutôt qu'à l'année de liquidation : durée requise,
âge légal, âge d'annulation de la décote, coefficient de minoration, nombre
d'années retenues au salaire de référence.</p>
<p>Il applique aussi, dans l'ordre où le droit les applique, les avantages non
contributifs que la carrière suffit à déterminer :</p>
<ul>
  <li><strong>l'assurance vieillesse des parents au foyer</strong>, qui porte au
  compte un salaire forfaitaire égal au SMIC — c'est ce qui la distingue d'une
  période assimilée, laquelle valide des trimestres sans jamais ajouter de
  salaire ;</li>
  <li><strong>les trimestres accordés au titre des enfants</strong>, datés : la
  majoration de durée d'assurance du régime général et des régimes alignés naît
  en 1972 à un an par enfant, passe à deux ans en 1975 et va à la mère ; la
  fonction publique et les régimes spéciaux servent leur bonification, un an par
  enfant né avant 2004 et deux trimestres pour les enfants nés depuis. Ils sont
  attribués à l'intérieur d'un régime, jamais au-dessus des régimes : ils comptent donc aussi dans
  sa proratisation ;</li>
  <li><strong>le minimum contributif</strong>, réservé aux pensions liquidées au
  taux plein, proratisé par la durée d'assurance acquise dans le régime, et sa
  majoration au titre des périodes cotisées proratisée par la seule durée
  cotisée, puis écrêté quand le total des pensions personnelles dépasse le
  plafond de l'article L. 173-2 ;</li>
  <li><strong>le minimum garanti</strong> de la fonction publique, barème en
  escalier sur la durée de services — 57,5 % de la référence à quinze ans, 95 %
  à trente, la totalité à quarante ;</li>
  <li><strong>la surcote parentale</strong>, créée par la loi du 14 avril 2023 :
  1,25 % par trimestre acquis entre 63 ans et l'âge légal, quatre au plus, à qui
  justifie de la durée requise à 63 ans et détient un trimestre de majoration
  pour enfants. C'est la contrepartie du recul de l'âge légal, et elle se cumule
  avec la surcote ordinaire, qui ne compte qu'au-delà de cet âge ;</li>
  <li><strong>la majoration pour trois enfants</strong>, calculée sur le montant
  déjà relevé par les minima, et plafonnée en euros à la complémentaire ;</li>
  <li><strong>le minimum vieillesse</strong>, allocation différentielle servie à
  partir de 65 ans sous le barème d'une personne seule. Ce n'est pas une
  pension : elle apparaît toujours comme une ligne séparée de la cascade.</li>
</ul>
<p>Deux barèmes propres complètent l'ensemble : la décote de la fonction
publique, dont le coefficient et l'âge d'annulation montent en charge de 2006 à
2020 et dont l'âge d'annulation est la limite d'âge du grade et non 67 ans ; et
la garantie minimale de points de l'Agirc, 120 points par an de 1989 à 2018
même quand la tranche B est nulle.</p>
<p>Enfin, le système dit si le droit <strong>ouvre</strong> la liquidation
demandée : âge légal du régime, ou départ anticipé pour carrière longue. Quand
il ne l'ouvre pas, le montant reste calculé, parce qu'il faut comparer les
quatre systèmes sur la même carrière, mais la page le signale : il ne décrit alors
aucune pension que le système actuel servirait.</p>""")


def _methode_suppressions() -> str:
    """Ce que les scénarios notionnels retirent, et la seule exception."""
    return g.depliant("Ce que les comptes notionnels suppriment", f"""
<p>Le principe « seules les cotisations comptent » est appliqué sans exception :
ni minimum contributif, ni minimum garanti, ni ASPA, ni majoration pour enfants,
ni majoration de durée d'assurance, ni AVPF, ni bonifications, ni catégorie
active, ni périodes assimilées, ni réversion, ni décote ni surcote. Le
système 1 les conserve tous, puisqu'il décrit le droit en vigueur.</p>
<p>Une exception : le <strong>système 4</strong>, la
<a href="{g.lien("/")}">proposition du Parti libéral français</a>, remet un
plancher, et un seul. C'est le système 3, à deux différences près : un taux
unique de 18 % pour tous à compter de la bascule, salariale et patronale
additionnées, les années antérieures restant portées au compte aux taux réels ;
et une garantie vieillesse, différentielle et servie à 65 ans comme l'ASPA, mais
individualisée — 800 € par personne, plus 250 € pour qui vit seul, en euros de
2026 — et financée par l'impôt. La page de simulation en détaille chaque étape,
et la page Coût compte cette part à part.</p>""")


def _methode_carriere(contexte: Contexte) -> str:
    """La fusion des régimes, et comment une carrière se décrit."""
    fusionne = contexte.simulateur().regime_fusionne
    nombre_regimes = len(contexte.simulateur().catalogue)
    return g.depliant("Comment une carrière est décrite", f"""
<h4>La fusion des régimes</h4>
<p>À compter de l'année de bascule, les {nombre_regimes} régimes du catalogue
sont remplacés par un régime unique dont chaque paramètre est le plus
défavorable de l'ensemble : ouverture à {_age(fusionne.age_ouverture)}, taux
plein à {_age(fusionne.age_taux_plein)},
{fusionne.duree_requise_trimestres} trimestres requis, cotisation de
{g.pourcentage(fusionne.taux_cotisation_retraite, decimales=2)} sur assiette
déplafonnée.</p>

<h4>Une carrière, plusieurs métiers</h4>
<p>Une carrière se décrit comme une <strong>suite de métiers</strong> : chacun
porte un statut d'affiliation, un âge de début et un niveau de revenu, et court
jusqu'au début du suivant. Chaque changement fait passer d'un régime à un
autre, donc d'un taux, d'une assiette et d'un barème à un autre.</p>
<p>Deux conventions le bornent, imposées par la maille des données. Le
<strong>profil de carrière</strong> vaut pour la vie active entière : c'est une
progression de carrière, quel que soit l'emploi, et le niveau propre à chaque métier s'y
superpose au lieu de la remettre à zéro. Et une <strong>année civile n'a qu'un
statut</strong> : l'année d'un changement revient au métier qui en occupe le
plus de mois, et à égalité à celui qui l'ouvre, tandis que le revenu porté au
compte reste la somme de ce que les deux ont réellement payé.</p>
<p>Un statut ne se déclare qu'<strong>aux dates où son régime recrutait</strong>.
Le menu date chacun (« depuis 1977 » pour l'artiste-auteur, « recrutés avant
septembre 2010 » pour le mineur) et grise ceux que l'entrée saisie ferme. La
date opposée est celle de l'entrée dans le métier, au mois près : qui est entré
à la RATP en octobre 2022 garde son régime, fermé aux recrutés du
1<sup>er</sup> septembre 2023. C'est la clause du grand-père.</p>""")


def _methode_construction() -> str:
    """Comment ce site est construit, et comment on le vérifie.

    C'est l'argument de confiance d'un public technique — un modèle de
    référence, un portage sans bibliothèque, des témoins comparés au bit
    près —, et il n'était accessible que par le lien GitHub en bas de
    l'accueil. Il est ici, là où le lecteur est déjà dans le détail. Aucun
    nombre de tests ni de témoins n'y est écrit : ils bougent à chaque
    session, et le README les porte, recalculés par un test.
    """
    return g.depliant("Comment ce site est construit, et comment on le vérifie", f"""
<p>Le modèle de référence est écrit en Python, dans
<a href="{g.DEPOT}/tree/main/src">le dossier <code>src/</code> du dépôt</a> : c'est
lui qui fait foi, et c'est lui qui est testé contre les sources — les textes,
les barèmes, et des calculateurs extérieurs comme OpenFisca, qui servent
d'oracle au système 1.</p>
<p>Ce que vous lisez ici est un <strong>portage en JavaScript</strong> de ce
modèle, sans aucune bibliothèque, qui tourne entièrement dans votre navigateur
: rien de ce que vous saisissez n'est envoyé nulle part. Le portage ne s'écarte
pas du modèle, et ce n'est pas une promesse : des centaines de carrières
témoins (chaque statut d'affiliation, à six générations) sont calculées par
les deux, et comparées nombre par nombre ; chaque page du site est rendue par
les deux, et comparée caractère par caractère. Toute divergence fait échouer
les tests.</p>
<p>Les données que le site charge sont produites par un script à partir des
mêmes fichiers que le modèle, et un test refuse un paquet périmé. Les séries
sont recontrôlées contre le fichier de l'institution qui les produit — la
page <a href="{g.lien("/donnees")}">Données</a> dit lesquelles, et à quelle
date.</p>
<p class="discret"><a href="{g.DEPOT}">Le dépôt</a> ·
<a href="{g.DEPOT}/blob/main/README.md">ce qu'il contient, et combien de tests
le tiennent</a> · <a href="{g.DEPOT}/tree/main/tests">les tests</a></p>""")


def _methode_unites() -> str:
    """Brut et pas net, multiples du salaire moyen, et le périmètre."""
    return g.depliant("En quelles unités, et sur quel périmètre", f"""
<h4 id="unites">Brut, et pas net</h4>
<p>Tout ce que le modèle manipule est <strong>brut</strong> : le revenu saisi,
les cotisations versées, le capital notionnel, les quatre pensions. « Brut » a ici
le sens des comptes nationaux : <em>salaires et traitements bruts</em> (D11)
rapportés à l'emploi salarié intérieur. C'est-à-dire <strong>avant</strong>
cotisations salariales, CSG, CRDS et impôt sur le revenu, et <strong>hors</strong>
cotisations patronales. C'est l'assiette sur laquelle les régimes appellent leurs
cotisations, donc la seule grandeur qu'un compte notionnel puisse enregistrer.
Le taux de remplacement affiché rapporte un brut à un brut, et il est
mécaniquement plus bas qu'un taux calculé sur des nets.</p>
<p>Le revenu d'activité se saisit en <strong>euros d'aujourd'hui</strong>. Le
modèle, lui, ne connaît que le <strong>multiple du salaire moyen</strong>, seule
unité qui garde son sens sur quatre-vingts ans. La page fait donc une division,
et une seule : <code>niveau = revenu mensuel × 12 ÷ salaire moyen annuel</code>.
Ce niveau suit ensuite le salaire moyen d'une année à l'autre, déformé par le
profil de carrière : le revenu saisi est celui du milieu de carrière. Un lien
sous les métiers bascule entre les deux unités, montants convertis.</p>
<p>Reste que les comptes nationaux ne publient que des <em>taux de croissance</em>
du salaire moyen. Les niveaux en sont reconstitués à partir d'un point
d'ancrage — <strong>40 000 € bruts annuels en 2024</strong> —, paramètre
documenté et non donnée certifiée. Il déplace proportionnellement tous les
revenus reconstitués, donc toutes les pensions, mais il est sans effet sur les
<strong>rapports</strong> entre scénarios, qui sont l'objet du modèle.</p>

<h4>Périmètre</h4>
<p>Origine 1941 (allocation aux vieux travailleurs salariés), premier dispositif
où les cotisations des actifs financent les prestations des retraités. Les
assurances sociales de 1930, en capitalisation individuelle, et le RAFP sont
isolés dans un compartiment séparé, jamais converti.</p>
<p class="discret"><a href="{g.DEPOT}/blob/main/docs/methodologie.md">Méthodologie
complète</a> · <a href="{g.DEPOT}/blob/main/docs/limites.md">Limites
connues</a></p>""")


#: Libellés des familles de régimes, tels que la page « Données » les affiche.
FAMILLES_INVENTAIRE = {
    "base_prive": "base, privé",
    "complementaire_prive": "complémentaire, privé",
    "fonction_publique": "fonction publique",
    "special": "spécial",
    "non_salarie": "non-salariés",
    "agricole": "agricole",
    "liberal": "libéral",
    "additionnel_capitalise": "additionnel, capitalisé",
}

#: Les quatre niveaux de fiabilité, du meilleur au moins bon, tels que les
#: fiches et les séries les écrivent.
NIVEAUX_FIABILITE = ("certifiee", "haute", "moyenne", "estimee")

#: Les cinq couvertures, dans l'ordre du menu de filtre : la clé de
#: l'inventaire, ce qu'on lit dans la cellule, et le pluriel de la phrase de
#: compte. Une couverture qu'aucune ligne ne porte ne s'affiche nulle part.
COUVERTURES_INVENTAIRE = (
    ("modelise", "modélisé", "modélisés"),
    ("partiel", "partiel", "partiels"),
    ("a_modeliser", "à modéliser", "à modéliser"),
    ("routage", "porté par un statut", "portés par un statut"),
    ("hors_champ", "hors champ", "hors champ"),
)


def _periode_inventaire(creation, fermeture, extinction) -> str:
    if creation is None:
        return "—"
    if extinction is not None:
        return f"{creation}-{extinction}"
    if fermeture is not None:
        return f"depuis {creation}, fermé en {fermeture}"
    return f"depuis {creation}"


def _inventaire_section(racine, catalogue) -> str:
    """Tous les régimes, calculés ou non — la liste qui manquait au dépôt.

    UNE SEULE TABLE, et non cinq : quatre-vingt-neuf lignes en cinq tableaux
    de prose ne se cherchaient qu'au Ctrl+F. La table porte tout ce que
    l'inventaire sait d'un régime — sa famille, ce qu'il est dans le modèle,
    la fiabilité de sa fiche quand il en a une, ses dates, ses statuts, ce qui
    lui manque —, et elle se filtre et se trie sur place : un champ de
    recherche, un menu par famille, un menu par couverture, et chaque en-tête
    de colonne est un bouton de tri. Le comportement est dans ``index.html``,
    en écoute déléguée ; sans lui, la table se lit entière, dans l'ordre du
    fichier, ce qui est exactement ce qu'elle était.

    Deux garde-fous. Un filtre se remet à « tout » d'un geste, et une ligne
    filtrée n'est que masquée : rien de ce que l'inventaire dit ne devient
    inatteignable. Et la table reste dans sa section repliée — c'est une
    annexe, qui ne s'impose pas à qui vient seulement savoir ce que valent
    les chiffres.

    ``catalogue`` donne la fiabilité des fiches calculées : l'inventaire ne la
    connaît pas, le catalogue si, et c'est ici que les deux se rejoignent.
    """
    lignes = charger_inventaire(racine)
    fiabilites = {regime.code: str(regime.fiabilite) for regime in catalogue}
    comptes = {cle: sum(1 for l in lignes if l.couverture == cle)
               for cle, _, _ in COUVERTURES_INVENTAIRE}
    phrase = ", ".join(
        f"{comptes[cle]} {pluriel}" for cle, _, pluriel in COUVERTURES_INVENTAIRE
        if comptes[cle]
    )
    lecture = dict((cle, singulier) for cle, singulier, _ in COUVERTURES_INVENTAIRE)

    def cellule(texte: str) -> str:
        return escape(texte) if texte else "—"

    corps = []
    attributs = []
    for ligne in lignes:
        corps.append([
            escape(ligne.nom),
            escape(FAMILLES_INVENTAIRE[ligne.famille]),
            escape(lecture[ligne.couverture]),
            cellule(fiabilites.get(ligne.code, "")),
            escape(_periode_inventaire(ligne.creation, ligne.fermeture, ligne.extinction)),
            cellule(", ".join(ligne.statuts)),
            cellule(ligne.raison_hors_champ if ligne.couverture == "hors_champ"
                    else ligne.manque),
        ])
        attributs.append({"data-famille": ligne.famille,
                          "data-couverture": ligne.couverture,
                          "data-fiabilite": fiabilites.get(ligne.code, "")})

    filtres = (
        '<div class="filtres" role="group" aria-label="Filtrer les régimes" '
        'data-cible="inventaire">'
        + g.champ("inventaire-recherche", "Chercher un régime", "",
                  "un nom, un statut, une caisse…", type_="search",
                  data_filtre="texte", autocomplete="off")
        + g.liste("inventaire-famille", "Famille",
                  [("", "Toutes")] + list(FAMILLES_INVENTAIRE.items()), "",
                  data_filtre="famille")
        + g.liste("inventaire-couverture", "Dans le modèle",
                  [("", "Tous")] + [(cle, singulier)
                                    for cle, singulier, _ in COUVERTURES_INVENTAIRE
                                    if comptes[cle]], "",
                  data_filtre="couverture")
        + g.liste("inventaire-fiabilite", "Fiabilité de la fiche",
                  [("", "Toutes")] + [(niveau, niveau) for niveau in NIVEAUX_FIABILITE
                                      if niveau in fiabilites.values()], "",
                  data_filtre="fiabilite")
        + "</div>"
        + f'<p class="compte discret" aria-live="polite" data-compte-de="inventaire" '
        f'data-unite="régimes">{len(lignes)} régimes</p>'
    )
    table = g.tableau(
        ["Régime", "Famille", "Dans le modèle", "Fiabilité", "Période", "Statuts",
         "Ce qui manque, ou pourquoi"],
        corps,
        ["", "texte", "texte", "texte", "texte", "texte", "texte"],
        titre=f"Les {len(lignes)} régimes de l'inventaire",
        entete_de_ligne=True,
        attributs_lignes=attributs,
        triable=True,
        identifiant="inventaire",
    )
    return g.depliant(f"Les {len(lignes)} régimes, un par un", f"""
<p>L'inventaire compte {len(lignes)} régimes de retraite obligatoires, actuels
et disparus : {phrase}. Il fait foi dans
<a href="{g.DEPOT}/blob/main/data/reference/regimes/inventaire.yaml">inventaire.yaml</a>,
où chaque ligne cite son texte fondateur, et un test le tient aligné sur le
catalogue : une fiche sans ligne d'inventaire, ou une ligne qui prétend calculer
ce qu'aucune fiche ne calcule, fait échouer les tests. Un régime « partiel » est
calculé, mais un étage, un barème ou une période lui manque, et la dernière
colonne dit lequel ; un régime « à modéliser » n'a pas de fiche ; une ligne
« portée par un statut » n'est pas un régime mais une affiliation (l'élu
local, le micro-entrepreneur), que le statut nommé route vers les régimes du
catalogue. La fiabilité est celle de la fiche du catalogue, quand il y en a
une. Cherchez, filtrez, ou triez en cliquant un en-tête de colonne.</p>
{filtres}
{table}""", identifiant="donnees-inventaire")


def _donnees(contexte: Contexte) -> str:
    """Ce que valent les chiffres du site.

    LA PAGE RÉPOND À UNE SEULE QUESTION, ET ELLE Y RÉPOND EN TROIS CHIFFRES :
    combien de valeurs ont été recontrôlées contre le fichier de l'institution
    qui les produit, combien de régimes sont recensés, et à quelle date. Tout le
    reste est une pièce justificative — la liste des séries certifiées, la
    fiabilité décennie par décennie, les quatre-vingt-neuf régimes un par un —,
    et une pièce justificative se range.

    Elle pesait 5 851 mots et huit tableaux dépliés, davantage que la page Coût
    avant sa refonte. Rien n'en est retiré : ce qui rend un chiffre vérifiable
    doit rester lisible, et l'est, à un clic.
    """
    simulateur = contexte.simulateur()
    macro = simulateur.macro

    periodes = []
    for debut in range(1940, 2030, 10):
        fin = debut + 9
        periodes.append([
            f"{debut}-{fin}",
            escape(str(macro.inflation.fiabilite_minimale_sur(debut, fin))),
            escape(str(macro.salaire_moyen.fiabilite_minimale_sur(debut, fin))),
            escape(str(macro.productivite.fiabilite_minimale_sur(debut, fin))),
            f"<strong>{escape(str(macro.fiabilite_sur(debut, fin)))}</strong>",
        ])

    par_niveau: dict[str, list[str]] = {}
    for regime in simulateur.catalogue:
        par_niveau.setdefault(str(regime.fiabilite), []).append(regime.code)
    regimes = [
        [niveau, str(len(par_niveau[niveau])),
         escape(", ".join(sorted(par_niveau[niveau])))]
        for niveau in ("certifiee", "haute", "moyenne", "estimee")
        if niveau in par_niveau
    ]

    journal = journal_certification(macro.racine)
    series = journal.get("series", {})
    certifications = [
        [escape(nom), f"{trace['valeurs']}", escape(trace.get("niveau", "certifiee")),
         escape(trace["verifiee_le"]), escape(trace["source"])]
        for nom, trace in sorted(series.items())
    ]
    # La table des séries se cherche et se trie comme l'inventaire : c'est
    # une base, pas un article, et quatre-vingts lignes se parcourent mieux
    # par leur niveau ou leur source que dans l'ordre alphabétique.
    niveaux_series = {trace.get("niveau", "certifiee") for trace in series.values()}
    attributs_series = [{"data-niveau": trace.get("niveau", "certifiee")}
                        for _, trace in sorted(series.items())]
    filtres_series = (
        '<div class="filtres" role="group" aria-label="Filtrer les séries" '
        'data-cible="series">'
        + g.champ("series-recherche", "Chercher une série", "",
                  "un nom, une source…", type_="search",
                  data_filtre="texte", autocomplete="off")
        + g.liste("series-niveau", "Niveau",
                  [("", "Tous")] + [(niveau, niveau) for niveau in NIVEAUX_FIABILITE
                                    if niveau in niveaux_series], "",
                  data_filtre="niveau")
        + "</div>"
        + f'<p class="compte discret" aria-live="polite" data-compte-de="series" '
        f'data-unite="séries">{len(certifications)} séries</p>'
    ) if certifications else ""
    valeurs_certifiees = sum(int(trace["valeurs"]) for trace in series.values())
    inventaire = len(charger_inventaire(macro.racine))
    # Ce que les fiches SOUTIENNENT : la plus ancienne relecture et la plus
    # récente. La page dit le minimum — « la vérification la plus ancienne
    # remonte au … » — et non la date du dernier passage, qui ne vaut que pour
    # les séries que ce passage a atteintes.
    dates_verification = sorted(trace["verifiee_le"] for trace in series.values())

    if certifications:
        reperes = g.fiche(
            "Valeurs recontrôlées contre leur source",
            g.nombre(valeurs_certifiees, 0),
            f"sur {len(certifications)} séries ; la vérification la plus ancienne "
            f"remonte au {_date_en_clair(dates_verification[0])}",
        ) + g.fiche(
            "Régimes recensés", str(inventaire),
            f"dont {len(simulateur.catalogue)} calculés",
        ) + g.fiche(
            "Institutions citées", "28",
            "INSEE, COR, DREES, Cnav, Légifrance…",
        )
        bandeau = f"""<div class="note"><strong>Les séries macroéconomiques sont
certifiées de 1950 à 2025</strong>, les tables de mortalité sont celles
réellement observées depuis 1986, et le plafond de la Sécurité sociale remonte à
1931 daté décret par décret. Le tout est recontrôlé contre les sources, série
par série : la vérification la plus ancienne remonte au
{_date_en_clair(dates_verification[0])}, la plus récente au
{_date_en_clair(dates_verification[-1])}. Ce qui précède 1950 et les
paramètres propres à chaque régime restent saisis à la main : les
<em>niveaux</em> de pension des carrières les plus anciennes gardent une marge,
les <em>écarts entre scénarios</em>, qui sont l'objet du modèle, sont plus
robustes encore.</div>"""
    else:
        reperes = g.fiche(
            "Valeurs recontrôlées contre leur source", "0",
            "la certification n'a pas encore été lancée",
        ) + g.fiche(
            "Régimes recensés", str(inventaire),
            f"dont {len(simulateur.catalogue)} calculés",
        ) + g.fiche(
            "Institutions citées", "28",
            "INSEE, COR, DREES, Cnav, Légifrance…",
        )
        bandeau = """<div class="note avertissement"><strong>Aucune série n'a
encore été recontrôlée contre sa source.</strong> Lancer <code>scripts/fetch/</code>
puis <code>scripts/verifier_donnees.py --appliquer</code>.</div>"""

    depliant_series = g.depliant("Quelles séries, et contre quelle source", f"""
{filtres_series}
{g.tableau(["Série", "Valeurs", "Niveau", "Vérifiée le", "Source"], certifications,
           ["", "nombre", "", "texte", "texte"],
           titre="Séries recontrôlées contre la source qui les produit",
           entete_de_ligne=True, attributs_lignes=attributs_series,
           triable=True, identifiant="series")}
<p class="discret">Une valeur n'est « certifiée » que si elle a été confrontée au
fichier téléchargé depuis le <em>producteur</em> de la donnée. Une transcription
tierce, même sourcée et reprise automatiquement, plafonne à « haute ». Hors de
cette liste : les séries d'avant 1950, les taux de cotisation d'avant 1967, le
plafond d'avant 2002 et le point d'indice de la fonction publique, repris
d'OpenFisca, les montants servis du minimum contributif, du minimum garanti et
du minimum vieillesse — transcrits de leur publication, et préférés à toute
projection parce qu'ils disent ce qui a été payé —, et les âges, durées et
coefficients propres à chaque régime, repris des textes.</p>""", identifiant="donnees-series")

    depliant_fiabilite = g.depliant("Ce que vaut chaque décennie, et chaque régime", f"""
<h4>Les séries macroéconomiques, décennie par décennie</h4>
{g.tableau(
    ["Période", "Inflation", "Salaire moyen", "Productivité", "Ensemble"],
    periodes,
    ["", "", "", "", ""],
    titre="Fiabilité des séries macroéconomiques, décennie par décennie",
    entete_de_ligne=True,
)}
<p class="discret">Une projection ne se fait jamais passer pour une observation :
au-delà de la dernière année observée, la fiabilité retombe à « estimée ».</p>

<h4>Les {len(simulateur.catalogue)} régimes calculés</h4>
{g.tableau(["Niveau", "Nombre", "Régimes"], regimes, ["", "nombre", "texte"],
           titre="Nombre de régimes par niveau de fiabilité",
           entete_de_ligne=True)}""", identifiant="donnees-fiabilite")

    depliant_sources = g.depliant("D'où viennent les chiffres, et comment on arbitre", f"""
<p>Trente institutions sont recensées dans
<a href="{g.DEPOT}/blob/main/data/sources.yaml">data/sources.yaml</a> : INSEE,
COR, Comité de suivi des retraites, DREES, CNAV, Service des retraites de l'État,
Caisse des dépôts, Direction de la Sécurité sociale, Cour des comptes,
Agirc-Arrco, Assemblée nationale, Union Retraite, CCMSA, CNAVPL, CNBF, DGAFP,
Direction du Budget, ERAFP, Ircantec, caisses des régimes spéciaux, Urssaf,
Légifrance, INED, Eurostat, OCDE, OpenFisca-France, IPP, CEPII, Banque centrale
européenne, Observatoire des produits d'épargne financière.</p>
<p><strong>Les deux sources du pilier capitalisé.</strong> Les taux auxquels il
place sont la courbe zéro-coupon des souverains les mieux notés de la zone euro,
que la <strong>Banque centrale européenne</strong> publie chaque jour ouvré :
c'est le producteur, la récupération est automatique, et les trente maturités
sont recontrôlées comme n'importe quelle série
(<code>courbe_taux_sans_risque</code> dans le tableau ci-dessus). Les frais de
l'enveloppe sont les moyennes 2025 des plans d'épargne retraite individuels,
mesurées par l'<strong>Observatoire des produits d'épargne financière</strong> —
le CCSF, à la Banque de France — sur les remises de l'ACPR. Ces trois valeurs
sont <code>haute</code> et non <code>certifiee</code> : le rapport est un PDF que
le dépôt ne sait pas récupérer automatiquement, et la règle du manifeste plafonne
à ce niveau ce qui n'a pas été confronté au document du producteur.</p>
<p>Chaque valeur porte son niveau de fiabilité, <code>certifiee</code>,
<code>haute</code>, <code>moyenne</code> ou <code>estimee</code>, et la fiabilité
d'un résultat est celle de son maillon le plus faible.</p>
<p>Quand deux institutions publient le même chiffre, quatre critères disent
laquelle aller chercher : le <strong>producteur</strong> prime sur le repreneur,
l'<strong>observé</strong> sur le projeté, le <strong>montant servi</strong> sur
le montant calculé, le <strong>recontrôlable</strong> sur le saisi. Ce n'est pas
un classement d'institutions mais de natures de données : l'INSEE pour ce qu'il
mesure, le COR pour ce qu'il décide.</p>
<p class="discret"><a href="{g.DEPOT}/blob/main/docs/limites.md">Limites
détaillées</a></p>""", identifiant="donnees-sources")

    # La réutilisation se range ici plutôt que sur une page à elle : qui vient
    # chercher d'où sort un chiffre est celui-là même qui s'apprête à le
    # reprendre, et la règle de citation ne se comprend qu'à côté de la liste
    # des producteurs. Ce n'est pas une mention légale — l'éditeur du site
    # d'accueil porte les siennes —, c'est la licence de ce dépôt.
    depliant_reutilisation = g.depliant("Licences et réutilisation", f"""
<p>Le code du modèle et du site est publié sous
<a href="{g.DEPOT}/blob/main/LICENSE">licence Apache 2.0</a> : réutilisable, y
compris commercialement, à condition d'en conserver la mention. Les pictogrammes
viennent de <a href="https://lucide.dev">Lucide</a> (licence ISC) ; ils sont
recopiés dans le dépôt, et le site ne les charge donc chez personne.</p>
<p>Les infographies, graphiques, tableaux et textes que le site affiche sont
sous licence <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr">Creative
Commons Attribution – Partage dans les mêmes conditions 4.0</a> (CC BY-SA) :
libres de reprise et d'adaptation, à condition de citer ce site et d'en indiquer
l'adresse, de signaler les modifications, et de republier toute version modifiée
sous la même licence. Le nom et le logo du Parti Libéral Français ne sont
couverts par aucune de ces licences.</p>
<p>Les données, elles, ne sont pas la propriété de l'éditeur. Les séries
françaises reprises ici — INSEE, DREES, DILA et Légifrance, Service des
retraites de l'État, caisses — sont des informations publiques, réutilisables
au titre des articles L321-1 et suivants du code des relations entre le public
et l'administration, le plus souvent sous Licence Ouverte (Etalab). Eurostat et
l'OCDE posent leurs propres conditions de réutilisation. Toutes imposent la
citation de la source : chaque valeur du dépôt porte la sienne dans
<a href="{g.DEPOT}/blob/main/data/sources.yaml">data/sources.yaml</a>.
<strong>Qui reprend un chiffre d'ici cite le producteur, pas ce site.</strong></p>""", identifiant="donnees-reutilisation")

    detail = (depliant_series + depliant_fiabilite
              + _inventaire_section(macro.racine, simulateur.catalogue)
              + depliant_sources + depliant_reutilisation)

    tete = g.affiche(
        "Les données",
        "Rien ici n'est "
        '<span class="cle-texte">à croire sur parole.</span>',
        "Chaque série est recontrôlée, automatiquement, contre le fichier de "
        "l'institution qui la produit. Ce qui ne l'est pas est dit.",
    )

    return f"""
{tete}

<div class="note resume"><strong>En clair.</strong> Les chiffres de ce site
viennent des institutions qui les produisent : l'INSEE pour les prix et les
salaires, le Conseil d'orientation des retraites pour les comptes, les caisses
pour leurs barèmes. Un programme les retélécharge et les compare, valeur par
valeur, à ce que le site utilise. Ce qui n'a pas pu être vérifié ainsi est
marqué comme tel, et les règles de chaque régime sont lues dans les textes.
Cette page dit, série par série et régime par régime, ce qui est vérifié et ce
qui ne l'est pas.</div>

<div class="fiches reperes">{reperes}</div>

{g.plan(detail, "/donnees")}

{bandeau}

<h2>Le détail</h2>

{detail}
"""
