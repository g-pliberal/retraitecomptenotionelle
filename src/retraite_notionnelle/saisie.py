"""La saisie d'une simulation : ce que l'adresse dit, lu en carrière et en règles.

Une simulation du site s'écrit tout entière dans son adresse — la naissance, le
statut, les dates, les revenus, les réglages — et ces paramètres sont l'entrée
de la surface publique (docs/architecture.md, annexe C.9). Ce module les lit :
il borne chaque champ, refuse ce qui ne décrit aucune carrière
(:class:`ErreurSaisie`, dont le message s'affiche tel quel), et tire de la
saisie la carrière et le jeu de paramètres que le moteur calcule.

Il formait la première moitié de ``web/pages.py``, dont la phase 8 a retiré
le texte du site : celui-ci n'est plus écrit qu'une fois, en JavaScript. La
lecture de la saisie est du calcul, et elle a sa copie dans
``moteur/js/saisie.js`` : les témoins la rejouent des deux côtés.
"""

from __future__ import annotations

import math
import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from urllib.parse import urlencode

from .calendrier import (
    MOIS_PAR_AN, NOMS_DE_MOIS, DateMois, en_mois, formater_age, mois_travailles,
    origine_des_ages,
)
from . import chronologie
from .carriere import LigneRelevee, Metier
from .config import (
    AgeConversionDroitsAcquis,
    ContributionEtat,
    ModeAgeReference,
    ModeIndexation,
    Parametres,
    PartCotisation,
    RevalorisationStock,
    SituationFoyer,
    TableConversion,
)


# -- les nombres des messages --------------------------------------------------
#
# Un refus cite un montant ou une borne, écrits comme la page les écrit. Ces
# deux fonctions sont celles du site, que ``moteur/js/gabarit.js`` porte.


def nombre(valeur: float, decimales: int = 2) -> str:
    """Nombre \u00e0 la fran\u00e7aise : virgule d\u00e9cimale, espace ins\u00e9cable des milliers."""
    return f"{valeur:,.{decimales}f}".replace(",", "\u202f").replace(".", ",")


def euros(montant: float) -> str:
    """Montant en euros, à l'euro près.

    L'unité de tout ce qui n'est pas une pension : capital notionnel,
    cotisations cumulées, salaires portés au compte. Les centimes y seraient du
    bruit — ces grandeurs se lisent par leur ordre de grandeur.
    """
    return nombre(montant, 0) + "\u202f\u20ac"


#: Le profil de carrière se DÉDUIT du statut par défaut : on ne demande pas sa
#: progression de carrière à quelqu'un qui a déjà dit qu'il était fonctionnaire
#: de l'État ou cadre du privé, et le modèle lit chez l'INSEE le profil du
#: groupe correspondant. Les trois autres restent, parce qu'une carrière au
#: SMIC ne progresse pas comme la moyenne de son groupe et que la mesure d'une
#: variante doit rester possible.
PROFILS = [
    ("auto", "Déduit du statut (défaut)"),
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
    ("fixe_apres_bascule", "65 ans à partir de la bascule (défaut)"),
    ("cliquet_legal", "Cliquet légal"),
    ("cliquet_puis_esperance_vie", "Cliquet puis espérance de vie"),
    ("legal_sans_cliquet", "Âge légal, sans cliquet"),
]

TABLES = [("unisexe", "Unisexe (défaut)"), ("par_sexe", "Par sexe")]

#: La population dont la mortalité entre dans le diviseur. « niveau_de_vie »,
#: le défaut, rattache la carrière au vingtile de niveau de vie où son salaire
#: la place (tables de l'INSEE) ; « commune » est la table de population
#: générale, la même pour tout le monde, et désactive la mesure ; les autres
#: clés imposent une population à toute carrière, pour mesurer.
#: Par quoi la carrière est rattachée à son vingtile de niveau de vie.
RATTACHEMENTS = [
    ("salaire", "Par le salaire (défaut)"),
    ("pension", "Par la pension"),
]

POPULATIONS = [
    ("niveau_de_vie", "Par niveau de vie (défaut)"),
    ("commune", "Population générale, la même pour tous"),
    ("fonctionnaires_civils_etat", "Fonctionnaires civils de l'État"),
    ("niveau_de_vie_v01", "Les 5 % les plus modestes (INSEE)"),
    ("niveau_de_vie_v10", "Niveau de vie médian (INSEE)"),
    ("niveau_de_vie_v20", "Les 5 % les plus aisés (INSEE)"),
]

PARTS_COTISATION = [
    ("salariale", "Part salariale seule (défaut)"),
    ("totale", "Salariale et patronale"),
    ("totale_alignee", "Salariale et patronale, public aligné sur le privé"),
]

#: Ce que le compte d'un agent de l'État reçoit de son employeur, là où la
#: part patronale y est portée : le taux versé, ou sa part « retraite ».
CONTRIBUTIONS_ETAT = [
    ("retraite_seule", "Sa part « retraite seule », selon la Cour des comptes (défaut)"),
    ("entiere", "Entière, telle que l'État l'a versée"),
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

#: L'emploi au-delà de la dernière observation. Il ne compose que la masse
#: salariale et le PIB projetés, donc l'indexation des comptes notionnels :
#: les systèmes 2 à 6 le lisent, le système 1 ne lit ni l'une ni l'autre.
TRAJECTOIRES_EMPLOI = [
    ("cor_2026", "Trajectoire du COR — juin 2026 (défaut)"),
    ("constant", "Emploi constant"),
]

#: Les pensions déjà servies à la bascule, sur la page Coût : elles gardent
#: les prix que le droit leur promet, ou la réforme les réindexe sur la règle
#: du compte le jour où elle s'applique. Systèmes 2 à 6 seulement.
REVALORISATIONS_STOCK = [
    ("prix", "Gardent les prix (défaut)"),
    ("reindexe", "Réindexées sur la règle du compte"),
]

#: Les frais du pilier capitalisé du système 4 : ce que l'enveloppe prélève,
#: et comment cela bouge avec le temps. Les codes sont ceux de
#: ``Parametres.sous_regime_frais``, qui dit ce que chacun fait ; l'ordre est
#: celui du menu, du réglage retenu à l'absence de frais.
REGIMES_FRAIS = [
    ("paliers", "Marché 2025, baisse par paliers (défaut)"),
    ("plafond", "Paliers, et tout le stock suit : un plafond"),
    ("contrats", "Paliers, le stock garde son tarif : des contrats"),
    ("figes", "Marché 2025, sans baisse"),
    ("detail", "PER vendu en 2025 : 2,20 % d'arrérages, sans frais de réserve, sans baisse"),
    ("aucun", "Aucun frais"),
]

#: Les taux futurs auxquels le pilier du système 4 place ses versements. Les
#: codes sont ceux de ``Parametres.sous_regime_taux``. Le défaut prend les taux
#: à terme de la courbe du jour ; les deux autres en retirent une prime de
#: terme, au milieu puis au haut de la fourchette de la littérature.
REGIMES_TAUX = [
    ("forwards", "Taux à terme de la courbe (défaut)"),
    ("prime", "Prime de terme retirée : 0,50 point à 30 ans"),
    ("prime_haute", "Prime de terme haute : 1 point à 30 ans"),
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
#: Les bornes du niveau de revenu, en multiples du salaire moyen. Le formulaire
#: les impose au champ, et l'inversion balaie l'intervalle qu'elles ferment :
#: c'est le même domaine, et il n'y en a qu'un.
NIVEAU_MINIMAL = 0.1
NIVEAU_MAXIMAL = 10.0

SALAIRE_DEFAUT = {"euros_mois": 3500.0, "moyen": 1.0}

#: Ce que le formulaire demande : un revenu d'activité, ou une pension.
#:
#: Le simulateur va du revenu à la pension, et c'est le sens du droit : on
#: cotise, puis on liquide. Mais celui qui est déjà à la retraite connaît sa
#: pension au centime et ne se souvient pas de ce qu'il gagnait il y a trente
#: ans — lui demander un revenu, c'est lui demander d'estimer ce que le
#: simulateur sait calculer. Le second mode prend donc la pension et cherche le
#: revenu dont le SCÉNARIO 1 la tire : le droit en vigueur est le seul des
#: quatre systèmes qu'il ait un sens d'inverser, puisque c'est le seul que
#: l'assuré a réellement subi.
#: Où l'on en est de sa vie, et c'est la PREMIÈRE question du formulaire.
#:
#: Elle a remplacé « Je saisis : mon revenu / ma pension », qui était une
#: question de modélisation déguisée en question à l'utilisateur : elle
#: demandait de choisir une entrée du calcul, quand celle-ci se déduit de ce
#: qu'on est. Un actif ne connaît pas sa pension, un retraité ne se souvient
#: pas de son salaire : la situation commande la saisie, et non l'inverse.
#:
#: ELLE N'ENTRE DANS AUCUN CALCUL. Le modèle ne connaît que la date de départ,
#: et c'est elle qui dit, au jour près, si la pension est déjà servie ou non —
#: voir ``_lecture_des_montants``. La situation n'oriente que le formulaire :
#: ce qu'il demande, et comment il le nomme. Deux réglages qui se contrediraient
#: ne peuvent donc pas fausser un chiffre, et le formulaire le signale au lieu
#: de le corriger.
SITUATIONS = [
    ("actif", "en activité"),
    ("retraite", "à la retraite"),
]

#: Ce que chaque situation demande par défaut. Le lien de la bascule porte les
#: deux, si bien que choisir sa situation reconfigure le formulaire d'un coup.
SAISIE_DE_LA_SITUATION = {"actif": "revenu", "retraite": "pension"}

#: Ce que le formulaire demande. Ce n'est plus un choix offert au lecteur mais
#: la conséquence de sa situation : les libellés ont disparu avec la bascule
#: qui les portait, et il ne reste que les deux codes, qui bornent ce qu'une
#: adresse a le droit de dire.
SAISIES = [("revenu", ""), ("pension", "")]

#: Pension mensuelle proposée par défaut, en euros NETS. Voisine de la pension
#: moyenne de droit direct des retraités de droit français, pour que le
#: formulaire s'ouvre sur un cas qui ressemble à celui de qui le lit.
PENSION_DEFAUT = 1500.0

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

#: La réponse qui dit qu'une activité S'AJOUTE à celle en cours. Toute autre
#: réponse que celle-ci ou le vide est refusée.
CUMUL = "oui"


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
#: par l'UNEDIC ou la Sécurité sociale, AVPF, services de la fonction publique. Un test vérifie qu'aucun code
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
    #: Vrai si cette activité S'AJOUTE à celle en cours au lieu de la
    #: remplacer. Faux tant que la personne ne l'a pas dit : rien n'est deviné.
    cumul: bool = False
    #: Âge auquel une activité ajoutée s'arrête ; ``None`` la mène au départ.
    fin: float | None = None


#: Les clés de requête qui décrivent les RÈGLES, et non la carrière.
#:
#: Ce sont exactement les treize que ``Saisie.parametres`` lit pour fabriquer un
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
    "indexation", "lissage", "age_reference", "table", "population",
    "rattachement", "conversion_acquis", "part_cotisation",
    "contribution_etat", "foyer", "projection", "emploi", "stock", "reprise",
    "frais", "taux", "bascule", "euros",
)


@dataclass
class Saisie:
    """Paramètres d'une simulation, tels que l'utilisateur les a saisis."""

    naissance: int = 1975
    naissance_mois: int = 1
    #: Jour de naissance. Il décide du mois d'où les âges se comptent
    #: (:func:`~retraite_notionnelle.calendrier.origine_des_ages`), et donc de
    #: l'âge que vaut une date de carrière ; la génération, elle, se coupe au
    #: mois. Le calendrier du formulaire le demande toujours ; une adresse qui
    #: ne le porte pas — « naissance=1975 », « naissance=1975-03 » — le laisse
    #: à la présomption ``jour_de_naissance`` (§ 5.6), et le dit ci-dessous.
    naissance_jour: int = 1
    #: Vrai quand l'adresse portait la naissance sans son jour, que la
    #: présomption a posé : la carrière le présume alors à son tour, en son nom.
    naissance_jour_presume: bool = False
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
    #: Ce que le formulaire demande : ``revenu`` — ce qu'on gagne en travaillant,
    #: d'où le simulateur tire une pension — ou ``pension`` — ce qu'on touche
    #: déjà, d'où il remonte au revenu. Voir :data:`SAISIES`.
    #: En activité ou à la retraite : la première question du formulaire, et la
    #: seule qui n'entre dans aucun calcul. Voir :data:`SITUATIONS`.
    situation: str = "actif"
    saisie_par: str = "revenu"
    #: La pension mensuelle saisie, quand c'est elle qu'on saisit. Elle est dans
    #: la MÊME convention que les montants affichés : nette ou brute selon
    #: ``montants``, et en euros constants de ``euros``. C'est ce qui la rend
    #: comparable sans rien convertir. Pour un retraité, c'est la pension qu'il
    #: touche AUJOURD'HUI, et le simulateur la compare à sa pension de départ
    #: revalorisée comme le droit l'a fait. Voir ``_champ_pension``.
    pension: float = PENSION_DEFAUT
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
    profil: str = "auto"
    primes: float = 0.0
    enfants: int = 0
    #: Les naissances des premiers enfants, dans l'ordre : « 1995, 1998-06 ».
    #: Celles qui ne sont pas dites sont présumées (docs/architecture.md,
    #: § 5.6) ; celles qui le sont choisissent, enfant par enfant, la version
    #: des règles qui lui accordent des trimestres. Voir
    #: :meth:`naissances_enfants`.
    naissances: str = ""
    #: Le conjoint, pour la réversion (docs/architecture.md, § 5.1) : sa
    #: naissance (AAAA ou AAAA-MM), son sexe — l'autre que celui de l'assuré
    #: s'il n'est pas dit (présomption ``conjoint_de_l_autre_sexe``) —, la date
    #: du mariage, présumée sinon, et ses ressources annuelles, s'il les dit.
    #: Voir :meth:`conjoint_declare`.
    conjoint: str = ""
    conjoint_sexe: str = ""
    mariage: str = ""
    ressources_conjoint: float | None = None
    #: Le décès de l'assuré (AAAA ou AAAA-MM), qui ouvre la réversion de son
    #: conjoint : au départ ou après lui.
    deces: str = ""
    interruptions: str = ""
    indexation: str = "masse_salariale"
    lissage: int = 1
    age_reference: str = "fixe_apres_bascule"
    table: str = "unisexe"
    population: str = "niveau_de_vie"
    rattachement: str = "salaire"
    conversion_acquis: str = "reference"
    part_cotisation: str = "salariale"
    contribution_etat: str = "retraite_seule"
    #: Seul ou en couple : la situation de foyer de la garantie vieillesse du
    #: système 4. Le défaut est la personne seule, comme pour l'ASPA du
    #: système 1, de sorte que les deux planchers se comparent.
    foyer: str = "seul"
    projection: str = "cor_reference"
    #: L'emploi projeté : la trajectoire du COR par défaut, ou constant.
    emploi: str = "cor_2026"
    #: Les pensions déjà servies à la bascule : sur les prix, ou réindexées.
    stock: str = "prix"
    #: Part de l'avance de la garantie que la succession couvre, en pour cent ;
    #: vide, elle est calculée sur le patrimoine des ménages retraités.
    reprise: int | None = None
    #: Les frais du pilier capitalisé : marché 2025 et baisse par paliers, ou
    #: l'une des variantes qui disent ce que chaque hypothèse déplace.
    frais: str = "paliers"
    #: Les taux futurs du pilier : les taux à terme de la courbe, ou l'une des
    #: deux variantes qui en retirent une prime de terme. C'est le seul réglage
    #: sous lequel l'allocation des maturités change quelque chose.
    taux: str = "forwards"
    bascule: int = 2026
    euros: int = 2026
    #: Vrai si la requête portait des paramètres, donc s'il faut calculer.
    demandee: bool = False

    @classmethod
    def depuis_requete(cls, parametres: dict[str, str],
                       tolerante: bool = False,
                       presomptions: dict | None = None) -> "Saisie":
        """``tolerante`` ne sert qu'à REMONTRER une saisie refusée : rien n'y
        est vérifié, et une ligne de métier incomplète arrête la lecture des
        métiers au lieu de la refuser. Une saisie lue ainsi ne se calcule
        jamais — voir :func:`_saisie_refusee`. ``presomptions`` est la table où
        lire le jour de naissance présumé, le vocabulaire à défaut.
        """
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
        situation = _parmi(parametres, "situation", SITUATIONS,
                           defauts.situation)
        naissance = _date_saisie(parametres, "naissance")
        annee_naissance = (naissance[0] if naissance
                           else _entier(parametres, "naissance", defauts.naissance))
        mois_naissance = (naissance[1] if naissance else _entier(
            parametres, "naissance_mois", defauts.naissance_mois
        ))
        # Le jour, s'il est dit ; présumé si l'adresse porte la naissance sans
        # lui ; celui du formulaire vierge si elle ne la porte pas du tout.
        jour_naissance, jour_presume = defauts.naissance_jour, False
        if naissance and naissance[2] is not None:
            jour_naissance = naissance[2]
        elif parametres.get("naissance") not in (None, "") or parametres.get(
                "naissance_mois") not in (None, ""):
            jour_naissance = chronologie.valeur("jour_de_naissance", presomptions)
            jour_presume = True
        mois_de_naissance = DateMois(annee_naissance, mois_naissance)
        saisie = cls(
            unite_revenu=unite,
            montants=_parmi(parametres, "montants", MODES_MONTANT,
                            defauts.montants),
            situation=situation,
            # Ce que la situation demande, SAUF si l'adresse dit autre chose :
            # un retraité peut préférer saisir ce qu'il gagnait, un actif viser
            # une pension. Le défaut suit la situation, l'explicite l'emporte —
            # c'est ce qui fait qu'une adresse réduite à « situation=retraite »
            # ouvre le formulaire sur la pension.
            saisie_par=_parmi(parametres, "saisie_par", SAISIES,
                              SAISIE_DE_LA_SITUATION[situation]),
            pension=_reel(parametres, "pension", defauts.pension),
            naissance=annee_naissance,
            naissance_mois=mois_naissance,
            naissance_jour=jour_naissance,
            naissance_jour_presume=jour_presume,
            sexe="F" if parametres.get("sexe") == "F" else "H",
            statut=statut,
            debut=_age_saisi(parametres, "debut", defauts.debut, mois_de_naissance),
            liquidation=_age_saisi(parametres, "liquidation", defauts.liquidation,
                                   origine_des_ages(mois_de_naissance, jour_naissance)),
            salaire=salaire,
            metiers=_metiers_saisis(parametres, salaire, mois_de_naissance, tolerante),
            releve=(parametres.get("releve") or "").strip(),
            profil=_parmi(parametres, "profil", PROFILS, defauts.profil),
            primes=_reel(parametres, "primes", defauts.primes),
            enfants=_entier(parametres, "enfants", defauts.enfants),
            naissances=(parametres.get("naissances") or "").strip(),
            conjoint=(parametres.get("conjoint") or "").strip(),
            conjoint_sexe=(parametres.get("conjoint_sexe") or "").strip().upper(),
            mariage=(parametres.get("mariage") or "").strip(),
            ressources_conjoint=(None if parametres.get("ressources_conjoint") in (None, "")
                                 else _reel(parametres, "ressources_conjoint", 0.0)),
            deces=(parametres.get("deces") or "").strip(),
            interruptions=(parametres.get("interruptions") or "").strip(),
            indexation=_parmi(parametres, "indexation", INDEXATIONS, defauts.indexation),
            lissage=_entier(parametres, "lissage", defauts.lissage),
            age_reference=_parmi(
                parametres, "age_reference", AGES_REFERENCE, defauts.age_reference
            ),
            table=_parmi(parametres, "table", TABLES, defauts.table),
            population=_parmi(parametres, "population", POPULATIONS, defauts.population),
            rattachement=_parmi(
                parametres, "rattachement", RATTACHEMENTS, defauts.rattachement),
            conversion_acquis=_parmi(
                parametres, "conversion_acquis", CONVERSIONS_ACQUIS,
                defauts.conversion_acquis,
            ),
            part_cotisation=_parmi(
                parametres, "part_cotisation", PARTS_COTISATION,
                defauts.part_cotisation,
            ),
            contribution_etat=_parmi(
                parametres, "contribution_etat", CONTRIBUTIONS_ETAT,
                defauts.contribution_etat,
            ),
            foyer=_parmi(parametres, "foyer", SITUATIONS_FOYER, defauts.foyer),
            projection=_parmi(parametres, "projection", PROJECTIONS, defauts.projection),
            emploi=_parmi(parametres, "emploi", TRAJECTOIRES_EMPLOI, defauts.emploi),
            stock=_parmi(parametres, "stock", REVALORISATIONS_STOCK, defauts.stock),
            reprise=_entier(parametres, "reprise", defauts.reprise),
            frais=_parmi(parametres, "frais", REGIMES_FRAIS, defauts.frais),
            taux=_parmi(parametres, "taux", REGIMES_TAUX, defauts.taux),
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
        if not tolerante:
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
        # Le jour compte désormais : un 31 février, qu'aucun calendrier ne
        # propose mais qu'une adresse peut porter, se refuse ici.
        try:
            date(self.naissance, self.naissance_mois, self.naissance_jour)
        except ValueError:
            raise ErreurSaisie(
                f"Date de naissance impossible : le {self.naissance_jour} "
                f"{NOMS_DE_MOIS[self.naissance_mois - 1]} {self.naissance} "
                "n'existe pas.") from None
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
                f"{self.fenetre(AGE_LIQUIDATION_MINIMAL, AGE_LIQUIDATION_MAXIMAL, True)}."
            )
        depart = self.date_de(self.liquidation, depart=True)
        if depart.rang <= self.date_de(self.debut).rang:
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
        self._verifier_naissances()
        self._verifier_conjoint()
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
        if self.reprise is not None and not 0 <= self.reprise <= 100:
            raise ErreurSaisie(
                "Part de l'avance couverte par la succession attendue entre 0 "
                "et 100."
            )
        if not 1 <= self.lissage <= LISSAGE_MAXIMUM:
            raise ErreurSaisie(
                f"Fenêtre de lissage attendue entre 1 et {LISSAGE_MAXIMUM} ans "
                "(1 = aucun lissage)."
            )
        self._verifier_pension()
        # Les métiers se suivent sans se recouvrir : chacun commence après le
        # précédent et avant le départ à la retraite. C'est la seule chose que
        # le moteur exige, et elle se dit ici plutôt que par une exception
        # remontée du modèle.
        precedent = self.debut
        for rang, metier in enumerate(self.metiers, start=2):
            if metier.cumul:
                self._verifier_cumul(metier, rang)
                continue
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
            if self.date_de(metier.debut).rang >= depart.rang:
                raise ErreurSaisie(
                    f"Métier n° {rang} : il doit commencer avant le départ à la "
                    f"retraite, fixé en {depart}."
                )
            # Une période sans emploi ne porte pas de revenu : elle hérite de
            # celui d'avant, qui n'est pas ce qu'elle paie — elle ne paie
            # rien — mais le salaire de référence sur lequel l'UNEDIC cotise
            # aux régimes complémentaires.
            if not metier.sans_emploi:
                self._verifier_revenu(metier.salaire, rang=rang)
            precedent = metier.debut

    def _verifier_cumul(self, metier: MetierSaisi, rang: int) -> None:
        """Une activité ajoutée : dans la carrière, et payée de son revenu.

        Elle ne suit pas la précédente — elle l'accompagne —, et n'a donc pas
        à commencer après elle ; seulement pendant la carrière. Elle ne se
        décrit pas non plus par la pension : la pension saisie ne dit qu'un
        niveau pour toute la carrière, et le revenu d'une seconde activité ne
        s'en déduit pas.
        """
        if self.par_pension:
            raise ErreurSaisie(
                f"Métier n° {rang} : une activité qui s'ajoute à celle en cours "
                "se décrit par son revenu. La saisie par la pension ne cherche "
                "qu'un niveau pour toute la carrière, et ne dirait rien de "
                "celui de cette activité-là."
            )
        if metier.debut < self.debut:
            raise ErreurSaisie(
                f"Métier n° {rang} : une activité qui s'ajoute commence pendant "
                f"la carrière, qui commence en {self.date_de(self.debut)}."
            )
        depart = self.date_de(self.liquidation, depart=True)
        if self.date_de(metier.debut).rang >= depart.rang:
            raise ErreurSaisie(
                f"Métier n° {rang} : il doit commencer avant le départ à la "
                f"retraite, fixé en {depart}."
            )
        if metier.fin is not None and not (
                metier.debut < metier.fin
                and self.date_de(metier.fin).rang <= depart.rang):
            raise ErreurSaisie(
                f"Métier n° {rang} : il doit s'arrêter après avoir commencé, et "
                f"au plus tard au départ, fixé en {depart}."
            )
        self._verifier_revenu(metier.salaire, rang=rang)

    # -- ce que le formulaire demande ----------------------------------------

    @property
    def par_pension(self) -> bool:
        """Vrai si c'est la pension qui est saisie, et le revenu qui se cherche.

        Le relevé l'emporte sur elle comme il l'emporte sur les revenus : il
        donne la carrière année par année, il n'y a plus rien à inverser.
        """
        return self.saisie_par == "pension" and not self.releve_actif

    def _verifier_pension(self) -> None:
        """La pension saisie, contrôlée avant qu'on cherche ce qu'elle suppose.

        Une borne haute serait un chiffre inventé : c'est le PLAFOND DU STATUT
        qui dit ce qu'une carrière peut acquérir, il se lit sur la courbe, et
        l'inversion le rapporte elle-même. Seul le zéro est refusé ici.
        """
        if self.saisie_par != "pension":
            return
        if self.pension <= 0:
            raise ErreurSaisie("La pension doit être strictement positive.")

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
        elif not NIVEAU_MINIMAL <= valeur <= NIVEAU_MAXIMAL:
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
                                  niveau_salaire=niveau, cumul=ligne.cumul,
                                  age_fin=ligne.fin))
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
        debut, fin = self.date_de(self.debut), self.date_de(self.liquidation, depart=True)
        lignes = self.lignes_carriere
        for rang, ligne in enumerate(lignes):
            if not ligne.sans_emploi:
                continue
            ouverture = self.date_de(ligne.debut)
            # Une activité ajoutée ne clôt pas l'interruption : elle se tient
            # à côté. C'est la période principale suivante qui la clôt.
            suivantes = [autre for autre in lignes[rang + 1:] if not autre.cumul]
            cloture = self.date_de(suivantes[0].debut) if suivantes else fin
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
            f"Ce revenu vaut {nombre(niveau, 2)} fois le salaire moyen ; le "
            "modèle en accepte de 0,1 à 10 fois, soit de "
            f"{nombre(echelle.mensuel(0.1), 0)} à "
            f"{euros(echelle.mensuel(10))} bruts par mois.",
        )

    # -- les dates ------------------------------------------------------------
    #
    # Le formulaire ne demande plus d'âges mais des dates : c'est la même
    # information — un âge est une date rapportée à la naissance —, mais celle
    # que le lecteur connaît sans la calculer. Le modèle, lui, continue de
    # recevoir des âges : la conversion tient dans les méthodes qui suivent, et
    # nulle part ailleurs.
    #
    # DEUX ORIGINES, comme dans le moteur. Un début ou une fin d'activité tombe
    # dans le mois où l'âge est atteint, compté du mois de naissance. Le départ
    # tombe au premier mois où l'âge est révolu (``depart=True``), compté du
    # mois que le jour désigne : né le 15 mars 1962, on part à soixante-quatre
    # ans au 1er avril 2026 (R. 351-37). Un âge de départ et un âge de début
    # ne se comparent donc qu'en dates.

    def date_de(self, age: float, depart: bool = False) -> DateMois:
        """Le mois où la carrière atteint cet âge : celui d'un début
        d'activité, ou, avec ``depart``, celui du départ, comptés comme le
        moteur les compte."""
        origine = (self.origine_des_ages if depart
                   else DateMois(self.naissance, self.naissance_mois))
        return origine.plus_mois(en_mois(age))

    @property
    def jour_declare(self) -> int | None:
        """Le jour de naissance tel que la carrière le reçoit : ``None`` quand
        il est présumé, pour que la chronologie le présume en son nom."""
        return None if self.naissance_jour_presume else self.naissance_jour

    @property
    def origine_des_ages(self) -> DateMois:
        """Le mois d'où les âges se comptent : voir
        :func:`~retraite_notionnelle.calendrier.origine_des_ages`."""
        return origine_des_ages(DateMois(self.naissance, self.naissance_mois),
                                self.naissance_jour)

    def mois_de(self, age: float, depart: bool = False) -> str:
        """Le même mois, tel que l'adresse le porte : « 1996-09 »."""
        date = self.date_de(age, depart)
        return f"{date.annee:04d}-{date.mois:02d}"

    def jour_de(self, age: float, depart: bool = False) -> str:
        """Le même mois au premier jour : ce qu'un champ date, lui, exige."""
        return f"{self.mois_de(age, depart)}-01"

    def fenetre(self, age_minimal: float, age_maximal: float,
                depart: bool = False) -> str:
        """« de septembre 1989 à septembre 2015 » : deux bornes d'âge, en dates.

        Un refus qui ne parlerait que d'âges laisserait au lecteur la
        soustraction à faire, alors que le champ qu'il vient de remplir porte
        une date.
        """
        return (f"de {self.date_de(age_minimal, depart)} "
                f"à {self.date_de(age_maximal, depart)}")

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
        """« le 15 mars 1962 » : la date de naissance, sans ordre à deviner ;
        le jour présumé le dit, quand l'adresse ne le donnait pas."""
        return (f"le {_jour_en_clair(self.naissance_jour)} "
                f"{NOMS_DE_MOIS[self.naissance_mois - 1]} {self.naissance}"
                + (" — jour présumé : l'adresse ne le disait pas"
                   if self.naissance_jour_presume else ""))

    def calcul_de(self, age: float, depart: bool = False) -> str:
        """« en septembre 1984, soit 22 ans et 6 mois » : une date de carrière."""
        if age < 0:
            return f"en {self.date_de(age, depart)}, avant la date de naissance"
        return f"en {self.date_de(age, depart)}, soit {_age(age)}"

    def parametres(self, base: Parametres) -> Parametres:
        return base.avec(
            mode_indexation=ModeIndexation(self.indexation),
            lissage_indexation=self.lissage,
            mode_age_reference=ModeAgeReference(self.age_reference),
            table_conversion=TableConversion(self.table),
            population_conversion=(
                None if self.population == "commune" else self.population
            ),
            rattachement_niveau_de_vie=self.rattachement,
            age_conversion_droits_acquis=AgeConversionDroitsAcquis(
                self.conversion_acquis
            ),
            part_cotisation=PartCotisation(
                self.part_cotisation
            ),
            contribution_etat=ContributionEtat(self.contribution_etat),
            situation_foyer=SituationFoyer(self.foyer),
            scenario_projection=self.projection,
            trajectoire_emploi=self.emploi,
            revalorisation_stock=RevalorisationStock(self.stock),
            part_reprise_garantie=None if self.reprise is None else self.reprise / 100,
            annee_bascule=self.bascule,
            annee_euros_constants=self.euros,
        ).sous_regime_frais(self.frais).sous_regime_taux(self.taux)

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
        return self.date_de(self.liquidation, depart=True)

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

    def naissances_enfants(self) -> list[str]:
        """Les naissances déclarées des premiers enfants, dans l'ordre :
        « 1995, 1998-06 » → ``["1995", "1998-06"]``. Une virgule, un
        point-virgule ou un blanc les sépare."""
        return [morceau for morceau in re.split(r"[\s,;]+", self.naissances) if morceau]

    def _verifier_naissances(self) -> None:
        """Pas plus de naissances que d'enfants ; chacune une année ou un mois,
        après la naissance de l'assuré et avant son départ, où elle ne
        compterait plus pour rien."""
        naissances = self.naissances_enfants()
        if len(naissances) > self.enfants:
            raise ErreurSaisie(
                f"Naissances des enfants : {len(naissances)} déclarée"
                f"{'s' if len(naissances) > 1 else ''} pour {self.enfants} enfant"
                f"{'s' if self.enfants > 1 else ''}."
            )
        for valeur in naissances:
            try:
                jour, _ = chronologie.naissance_declaree(valeur)
            except ValueError:
                raise ErreurSaisie(
                    f"Naissance d'un enfant « {valeur} » : attendue en AAAA ou "
                    "AAAA-MM, par exemple 1995 ou 1995-06."
                ) from None
            if jour <= self.naissance_iso:
                raise ErreurSaisie(
                    f"Naissance d'un enfant « {valeur} » : elle précède la vôtre."
                )
            if jour >= self.jour_de(self.liquidation, depart=True):
                raise ErreurSaisie(
                    f"Naissance d'un enfant « {valeur} » : elle suit le départ à la "
                    f"retraite, fixé en {self.date_de(self.liquidation, depart=True)}."
                )

    def conjoint_declare(self) -> dict | None:
        """Le conjoint que la saisie déclare, tel que la chronologie le reçoit
        (:func:`chronologie._personne`) ; ``None`` sans conjoint."""
        if not self.conjoint:
            return None
        return {"naissance": self.conjoint,
                "sexe": self.conjoint_sexe or ("H" if self.sexe == "F" else "F"),
                "mariage": self.mariage or None,
                "ressources": self.ressources_conjoint}

    def deces_declare(self) -> str | None:
        """Le décès de l'assuré que la saisie déclare, ou ``None``."""
        return self.deces or None

    def _verifier_conjoint(self) -> None:
        """Le conjoint et le décès : des dates lisibles, dans l'ordre de la vie
        — les naissances, le mariage, le décès —, et un décès qui ne précède
        pas le départ : la réversion d'une pension que l'assuré n'a pas encore
        liquidée n'est pas calculée."""
        if not self.conjoint:
            orphelins = [nom for nom, valeur in (
                ("conjoint_sexe", self.conjoint_sexe), ("mariage", self.mariage),
                ("ressources_conjoint", self.ressources_conjoint), ("deces", self.deces))
                if valeur not in ("", None)]
            if orphelins:
                raise ErreurSaisie(
                    f"« {orphelins[0]} » ne sert qu'à la réversion : dites aussi la "
                    "naissance du conjoint (« conjoint »).")
            return
        dates = {}
        for nom, valeur, quoi in (("conjoint", self.conjoint, "la naissance du conjoint"),
                                  ("mariage", self.mariage, "le mariage"),
                                  ("deces", self.deces, "le décès")):
            if not valeur:
                continue
            try:
                dates[nom], _ = chronologie.date_declaree(valeur, quoi)
            except ValueError:
                raise ErreurSaisie(
                    f"{quoi[0].upper()}{quoi[1:]} « {valeur} » : attendu en AAAA ou "
                    "AAAA-MM, par exemple 1962 ou 1962-03.") from None
        if self.conjoint_sexe not in ("", "H", "F"):
            raise ErreurSaisie("Sexe du conjoint : H ou F.")
        if self.ressources_conjoint is not None and self.ressources_conjoint < 0:
            raise ErreurSaisie("Ressources du conjoint : un montant annuel positif.")
        if "mariage" in dates and dates["mariage"] <= max(dates["conjoint"], self.naissance_iso):
            raise ErreurSaisie("Le mariage précède la naissance d'un des époux.")
        if "deces" in dates:
            if "mariage" in dates and dates["mariage"] >= dates["deces"]:
                raise ErreurSaisie("Le mariage suit le décès.")
            if dates["deces"] < self.jour_de(self.liquidation):
                raise ErreurSaisie(
                    f"Décès « {self.deces} » : il précède le départ à la retraite, fixé "
                    f"en {self.date_de(self.liquidation)} ; la réversion d'une pension "
                    "que l'assuré n'a pas encore liquidée n'est pas calculée.")

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
            "liquidation": self.mois_de(self.liquidation, depart=True),
            "salaire": _nombre(self.salaire), "profil": self.profil,
            "releve": self.releve,
            "primes": _nombre(self.primes), "enfants": self.enfants,
            **({"naissances": ",".join(self.naissances_enfants())}
               if self.naissances_enfants() else {}),
            **{nom: valeur for nom, valeur in (
                ("conjoint", self.conjoint), ("conjoint_sexe", self.conjoint_sexe),
                ("mariage", self.mariage),
                ("ressources_conjoint", "" if self.ressources_conjoint is None
                 else _nombre(self.ressources_conjoint)),
                ("deces", self.deces)) if valeur not in ("", None)},
            "interruptions": self.interruptions, "indexation": self.indexation,
            "lissage": self.lissage,
            "age_reference": self.age_reference, "table": self.table,
            "population": self.population, "rattachement": self.rattachement,
            "conversion_acquis": self.conversion_acquis,
            "part_cotisation": self.part_cotisation,
            "contribution_etat": self.contribution_etat,
            "foyer": self.foyer,
            "projection": self.projection, "emploi": self.emploi,
            "stock": self.stock,
            "reprise": "" if self.reprise is None else self.reprise,
            "frais": self.frais, "taux": self.taux,
            "bascule": self.bascule, "euros": self.euros,
        }
        # L'unité s'écrit TOUJOURS, y compris quand c'est celle par défaut :
        # c'est ce qui distingue une adresse neuve d'une adresse d'avant les
        # euros, dont le « salaire » nu est un multiple du salaire moyen.
        champs["unite_revenu"] = self.unite_revenu
        # Le mode s'écrit toujours lui aussi : il gouverne l'interprétation du
        # nombre « salaire », et une adresse partagée qui l'omettrait décrirait
        # une autre carrière que celle qu'on a calculée.
        champs["montants"] = self.montants
        # Ce que le formulaire demande s'écrit toujours, pour la même raison :
        # une adresse qui l'omettrait décrirait une saisie par le revenu, et
        # le nombre « pension » n'y servirait plus à rien.
        champs["situation"] = self.situation
        champs["saisie_par"] = self.saisie_par
        champs["pension"] = _nombre(self.pension)
        # Les métiers qui suivent le premier, un groupe de trois champs chacun.
        # Une ligne vide du formulaire n'en produit aucun : l'adresse ne porte
        # que ce qui a été saisi.
        for rang, metier in enumerate(self.metiers, start=2):
            champs[f"metier{rang}_debut"] = self.mois_de(metier.debut)
            champs[f"metier{rang}_statut"] = metier.statut
            champs[f"metier{rang}_salaire"] = _nombre(metier.salaire)
            if metier.cumul:
                champs[f"metier{rang}_cumul"] = CUMUL
                if metier.fin is not None:
                    champs[f"metier{rang}_fin"] = self.mois_de(metier.fin)
        champs.update(remplacements)
        return urlencode(champs)


def _metiers_saisis(parametres: dict[str, str], salaire_precedent: float,
                    mois_de_naissance: DateMois,
                    tolerante: bool = False) -> list[MetierSaisi]:
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
        cumul = (parametres.get(f"metier{rang}_cumul") or "").strip()
        fin = (parametres.get(f"metier{rang}_fin") or "").strip()
        if not (debut or statut or salaire or cumul or fin):
            continue
        # Remontrée, la ligne incomplète n'est pas un métier : la lecture s'y
        # arrête, et c'est la ligne vide du formulaire qui la reçoit.
        if tolerante and not (debut and statut):
            break
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
        # LE CUMUL SE DÉCLARE, et ne se déduit de rien : une activité qui ne
        # dit pas s'ajouter à celle en cours la remplace, comme toujours.
        if cumul not in ("", CUMUL):
            raise ErreurSaisie(
                f"Métier n° {rang} : « {cumul} » n'est pas une réponse "
                "possible — l'activité remplace la précédente, ou s'y ajoute."
            )
        if cumul and sans_emploi:
            raise ErreurSaisie(
                f"Métier n° {rang} : une période sans emploi ne s'ajoute pas à "
                "une activité — elle l'interrompt."
            )
        if fin and not cumul:
            raise ErreurSaisie(
                f"Métier n° {rang} : une date de fin ne se donne qu'à une "
                "activité qui s'ajoute à celle en cours ; celle qui la remplace "
                "s'arrête où commence la période suivante."
            )
        # Une activité ajoutée garde son propre revenu, mais n'en passe pas à
        # la ligne suivante : c'est l'activité principale qu'elle continue.
        salaire = salaire_precedent
        if not sans_emploi:
            salaire = _reel(parametres, f"metier{rang}_salaire", salaire_precedent)
            if not cumul:
                salaire_precedent = salaire
        metiers.append(MetierSaisi(
            debut=_age_saisi(parametres, f"metier{rang}_debut", 0.0, mois_de_naissance),
            statut=statut,
            salaire=salaire,
            sans_emploi=sans_emploi,
            cumul=bool(cumul),
            fin=(_age_saisi(parametres, f"metier{rang}_fin", 0.0, mois_de_naissance)
                 if fin else None),
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
                 nom: str) -> tuple[int, int, int | None] | None:
    """La date écrite dans ce champ, ou ``None`` s'il n'en porte pas ; son
    jour est ``None`` quand elle n'en dit pas.

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
    jour = None if trouve.group(3) is None else int(trouve.group(3))
    if not 1 <= mois <= 12:
        raise ErreurSaisie(f"« {nom} » : mois attendu entre 01 et 12 (reçu : {brut}).")
    # Le jour n'est borné ici que grossièrement ; celui de la naissance, le
    # seul qui compte, se contrôle au calendrier près avec elle (``verifier``).
    if jour is not None and not 1 <= jour <= 31:
        raise ErreurSaisie(f"« {nom} » : jour attendu entre 01 et 31 (reçu : {brut}).")
    return annee, mois, jour


def _age_saisi(parametres: dict[str, str], nom: str, defaut: float,
               origine: DateMois) -> float:
    """L'âge qu'une date de carrière vaut, rapportée à la naissance.

    Le formulaire demande une date — celle du premier mois cotisé, celle du
    départ —, parce que c'est ce dont on se souvient ; le modèle, lui, ne
    connaît que des âges. La soustraction se fait ici, en mois, depuis
    ``origine`` — le mois de naissance pour un début ou une fin d'activité,
    celui d'où les âges de départ se comptent pour le départ
    (:func:`origine_des_ages`) —, et le résultat est l'âge en années décimales
    que le moteur attend : le moteur, qui compte de même, retombe sur la date
    saisie.

    Les adresses d'avant le calendrier continuent d'être lues telles quelles :
    ``liquidation=64`` et ``liquidation_mois=7`` valent soixante-quatre ans et
    sept mois, ``liquidation=64.5`` vaut ce qu'il a toujours valu.
    """
    date = _date_saisie(parametres, nom)
    if date is not None:
        return (DateMois(date[0], date[1]).rang - origine.rang) / MOIS_PAR_AN
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


def _jour_en_clair(jour: int) -> str:
    """Le premier du mois est un ORDINAL en français : « 1er », et non « 1 »."""
    return "1er" if jour == 1 else str(jour)


def _age(valeur: float) -> str:
    """Âge à la française, en ans et en mois : « 64 ans », « 64 ans et 9 mois ».

    Le modèle date la liquidation au mois : l'écrire « 64,75 » demanderait au
    lecteur de multiplier par douze pour retrouver ce qu'il a saisi.
    """
    return formater_age(valeur)


# -- l'échelle des salaires ---------------------------------------------------


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
