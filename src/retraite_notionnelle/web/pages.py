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
    RACINE_DONNEES,
    AgeConversionDroitsAcquis,
    PartCotisation,
    ModeAgeReference,
    ModeIndexation,
    Parametres,
    RevalorisationStock,
    SituationFoyer,
    TableConversion,
)
from ..avantages import (
    LIBELLES_MOTIFS, LIGNES_LUES, MOTIFS, NEUTRALISATIONS, calculer_avantages,
    charger_avantages,
    inventaire_depuis_paquet,
)
from ..cout import (
    COMPOSANTE_GARANTIE,
    PensionFinancee,
    calculer_cout,
    calculer_dette,
    financer,
    masse_du_scenario,
)
from ..donnees.bilan import BilanFige, charger_bilan
from ..donnees.assiette import AssietteActivite
from ..donnees.distribution import (
    DistributionPensions,
    part_femmes as part_femmes_distribution,
)
from ..garantie import cout_garantie, cout_garantie_par_sexe
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
    Incidence,
    charger_prelevements,
    salaire_brut_depuis_net,
    salaire_net_depuis_brut,
)
from ..restitution import Restitution
from ..simulateur import Comparaison, Simulateur
from . import gabarit as g

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
    ("fixe_apres_bascule", "64 ans à partir de la bascule (défaut)"),
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
    "rattachement", "conversion_acquis", "part_cotisation", "foyer",
    "projection", "emploi", "stock", "reprise", "frais", "taux", "bascule",
    "euros",
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
    profil: str = "auto"
    primes: float = 0.0
    enfants: int = 0
    interruptions: str = ""
    indexation: str = "masse_salariale"
    lissage: int = 1
    age_reference: str = "fixe_apres_bascule"
    table: str = "unisexe"
    population: str = "niveau_de_vie"
    rattachement: str = "salaire"
    conversion_acquis: str = "reference"
    part_cotisation: str = "salariale"
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
            "population": self.population, "rattachement": self.rattachement,
            "conversion_acquis": self.conversion_acquis,
            "part_cotisation": self.part_cotisation,
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


#: Trois points de la courbe publiée, montrés pour en donner la forme. Ce ne
#: sont plus les maturités d'une échelle — le pilier achète celle de son
#: horizon, n'importe laquelle des trente que la BCE cote — mais trois repères
#: de lecture : le court, le milieu, le bout.
MATURITES_MONTREES = (2, 10, 30)


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

    def restitution(self) -> Restitution:
        """Ce que la proposition rend au salaire, et ce qu'elle éteint en dette.

        Mémorisé par jeu de règles et non une fois pour toutes : le partage est
        un RÉGLAGE, et deux contextes n'ont pas forcément le même.
        """
        return self._agregat("restitution", lambda: Restitution(
            self.base.racine_donnees, self.base.part_rendue_aux_salaires))

    def bilan(self) -> BilanFige:
        """Le bilan des quatre systèmes, figé — une DONNÉE, pas un agrégat.

        La page des résultats en a besoin à chaque frappe, et le calculer
        coûte dix-huit secondes : elle lit donc la table que
        ``scripts/construire_donnees.py`` a écrite, celle-là même que le
        navigateur reçoit dans son paquet. ``donnees/bilan.py`` dit ce que ce
        figeage coûte — rien sur le système actuel, dont le coefficient est le
        compte du COR, et une dépendance aux réglages de référence sur les
        trois autres.
        """
        return self._donnee(
            "bilan", lambda: charger_bilan(self.base.racine_donnees))

    def cout(self):
        """Le coût agrégé de tous les systèmes — deux secondes de calcul, une fois.

        Sous les règles de ``base``, et non sous celles par défaut : c'est ce
        qui fait que la page Coût chiffre ce que le simulateur calcule.
        """
        return self._agregat("cout", lambda: calculer_cout(
            self.simulateur(), self.depenses(), self.population(),
            self.comptes(), assiette=self.assiette()))

    def inventaire_avantages(self):
        """L'inventaire des avantages non contributifs — une donnée, pas un calcul."""
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
    "/risque": "Risque",
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
    "/risque": "Votre retraite sera-t-elle payée ? Ce que la recherche "
               "universitaire sait du risque de défaut d'une retraite par "
               "répartition, et ce que les comptes du COR en disent pour la "
               "France.",
    "/avantages": "Tous les avantages non contributifs du système actuel : "
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
        return TITRES[chemin], refus + _agregee(chemin, contexte, reglages,
                                                parametres)
    if chemin == "/risque":
        return TITRES[chemin], _risque(contexte)
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


def _agregee(chemin: str, contexte: Contexte, reglages: Saisie,
             parametres: dict[str, str] | None = None) -> str:
    """Une page qui agrège, calculée sous les règles que l'adresse demande.

    Le corps de la page n'en sait rien : il reçoit un contexte DÉRIVÉ, dont
    ``base`` porte ces règles, et lit ``contexte.base``, ``contexte.cout()`` ou
    ``contexte.simulateur()`` comme il l'a toujours fait. C'est le contexte qui
    sait sous quelles règles on l'interroge, et non chacune des trente lignes
    qui l'interrogent.

    ``parametres`` passe en plus, et ne dit RIEN des règles : il porte ce qu'une
    page REGARDE — l'année que la cascade de Coût décompose — là où les réglages
    disent sous quelles règles elle se calcule. Les deux ne se mélangent pas :
    un réglage change le modèle, et voyage vers toutes les pages ; un regard ne
    change rien, et ne vaut que pour la sienne.
    """
    vues = _VUES_DE_PAGE.get(chemin, ())
    regards = {cle: valeur for cle, valeur in (parametres or {}).items()
               if cle in vues}
    return (
        _avertissement_reglages(reglages, chemin)
        + PAGES_AGREGEES[chemin](contexte.pour(reglages.parametres(contexte.base)),
                                 regards)
        + _reglages(reglages, chemin, regards)
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
  <li><a href="{g.lien("/risque")}">Risque</a> : votre retraite sera-t-elle
  payée, et ce que la recherche en sait.</li>
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
{_programme_restitution(contexte)}
{_programme_transition(contexte)}
{_programme_blocages(contexte)}

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
    volontaire = g.pourcentage(
        base.taux_capitalisation_volontaire_applique, decimales=0)
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
         f"transmettent. Restent {volontaire} rendus : le simulateur montre ce "
         "qu'ils donnent si vous les placez au même endroit, "
         f'<strong class="cle-texte">à effort inchangé</strong>.'),
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
        # Une ligne d'aide, comme sous chaque date : sans elle, l'étiquette
        # était plus courte d'une ligne et le menu partait plus bas que les
        # champs voisins.
        g.liste("statut", "Statut",
                _options_statuts(affiliations, saisie.date_de(saisie.debut)),
                saisie.statut, "celui du premier emploi"),
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
    <div class="action"><button type="submit">Calculer →</button></div>
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
            ["300 € et 300 €", "1 000 €", "1 000 €"],
            ["300 € et 1 500 €", "0 €", "500 €"],
            ["900 € et 900 €", "0 €", "0 €"],
            ["300 € et 5 000 €", "0 €", "500 €"],
            ["Personne seule, 300 €", "750 €", "750 €"],
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
    # Qui vit sous ce plancher AUJOURD'HUI, femmes et hommes à part : la
    # distribution de l'EIR, sans rien emprunter au modèle. Et qui vit seul
    # après 65 ans, lu au recensement.
    simulateur = contexte.simulateur()
    distribution = simulateur.distribution
    millesime = distribution.millesime
    vers_enquete = simulateur.macro.coefficient_prix(
        base.annee_euros_garantie_vieillesse, millesime)
    sous_plancher = {
        sexe: cout_garantie(
            DistributionPensions(base.racine_donnees, sexe=sexe), 1.0,
            plancher_seul * vers_enquete, 1.0)
        for sexe in ("F", "H")
    }
    couple = simulateur.vie_en_couple
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
<p><strong>Une avance, pas un don.</strong> Ce que la garantie verse est une
créance de l'État sur celui qui la reçoit. Elle porte intérêt au taux auquel
l'État emprunte, pour que les finances publiques n'y perdent rien, et elle est
<strong>reprise sur la succession dès le premier euro</strong>, là où l'ASPA
n'est récupérée qu'au-delà d'un seuil d'actif net. Quatre règles l'encadrent
:</p>
<ul class="serree">
  <li>elle ne s'exerce que sur ce que la succession contient : les héritiers
  ne paient jamais de leur poche, et ce que l'actif ne couvre pas est
  abandonné — c'est cette part-là, et elle seule, que l'impôt finance ;</li>
  <li>le logement est repris comme le reste, mais la reprise attend le décès
  du conjoint survivant qui l'occupe, les intérêts courant entre-temps ;</li>
  <li>les donations faites depuis l'ouverture de la garantie, ou dans les dix
  ans qui l'ont précédée, sont réintégrées : la créance se poursuit contre le
  donataire, à hauteur de ce qu'il a reçu et jamais au-delà, comme l'aide
  sociale départementale le fait déjà ; les primes d'assurance-vie versées
  après 65 ans de même, contre leur bénéficiaire ;</li>
  <li>la créance est garantie par une hypothèque légale inscrite dès le
  premier versement, de sorte qu'un bien donné la porte avec lui.</li>
</ul>
<p>Elle se demande, comme l'ASPA, et se refuse : personne ne se voit imposer
une dette. Le programme retient qu'un ayant droit sur deux la réclame, ce que
la DREES observe sur l'ASPA, et chiffre son coût ainsi.</p>
<h3>Le minimum vieillesse est d'abord une affaire de femmes</h3>
<p>L'échantillon interrégimes de retraités de la DREES le mesure. Rapportées
au plancher que nous proposons, les pensions de droit direct de {millesime} se répartissent ainsi
:</p>
{g.tableau(
    ["Retraités", "Pension sous le plancher", "Ce qui leur manque, en moyenne"],
    [["Femmes", g.pourcentage(sous_plancher["F"].part_beneficiaires, decimales=0),
      g.euros(sous_plancher["F"].complement_moyen_mensuel / vers_enquete) + " par mois"],
     ["Hommes", g.pourcentage(sous_plancher["H"].part_beneficiaires, decimales=0),
      g.euros(sous_plancher["H"].complement_moyen_mensuel / vers_enquete) + " par mois"]],
    ["", "nombre", "nombre"],
    titre=f"Pensions de droit direct sous {g.euros(plancher_seul)} par mois, "
          f"retraités de {millesime}",
    entete_de_ligne=True,
)}
<p>Deux femmes retraitées sur cinq touchent aujourd'hui moins que ce plancher,
contre moins d'un homme sur cinq. La raison n'est pas mystérieuse : carrières
interrompues, temps partiels, salaires plus bas. La dernière colonne dit autre
chose, et il faut la lire aussi : l'homme qui tombe sous le plancher tombe en
général plus bas que la femme. Ils sont rares, et ce sont des carrières très
courtes ; chez les femmes, c'est la règle plutôt que l'accident. Et la même
inégalité se
retrouve à la fin de la vie : au recensement de {couple.annee}, {g.pourcentage(couple.part(65, "F"), decimales=0)}
des femmes de 65 ans vivent en couple, et il n'en reste que {g.pourcentage(couple.part(85, "F"), decimales=0)} à
85 ans, quand {g.pourcentage(couple.part(85, "H"), decimales=0)} des hommes du même âge vivent encore avec
quelqu'un. Les femmes vivent plus longtemps, elles épousent des hommes plus
âgés, et elles finissent seules : la <strong>veuve pauvre</strong> est la
figure centrale de ce dispositif, hier comme demain.</p>

<h3>Ce que cela change pour une veuve, et pour ses enfants</h3>
<p>Il faut le dire sans détour, parce que c'est le point où notre proposition
prend le plus. Aujourd'hui, une veuve touche une <strong>pension de
réversion</strong> : une part de la pension de son mari, versée jusqu'à sa
mort, qu'elle ne rembourse jamais, et qui ne touche pas à ce que ses enfants
hériteront. <strong>Notre système ne sert aucune réversion</strong> : chacun
reçoit ce qu'il a cotisé, et rien de plus. Pour une femme dont la pension
propre est petite, ce qui prend la place de la réversion est cette
garantie-là.</p>
<p>Et cette garantie est une avance. La veuve la touche pendant les années où
elle vit seule, la créance s'accumule, et elle est reprise à sa mort sur la
succession. Celle-ci porte le patrimoine du couple, et souvent aussi l'avance
de son mari, que la règle a laissée courir jusque-là. <a
href="{g.lien("/cout")}">La page Coût</a> chiffre ce que cela donne : les
bénéficiaires de la garantie sont aux deux tiers des femmes, une succession
porte en moyenne plus d'une avance, et quand le patrimoine est une maison
modeste, l'héritage y passe en entier. Les héritiers ne paient jamais de leur
poche, la règle le garantit ; mais ils héritent souvent de rien.</p>
<p>C'est un choix, et nous l'assumons pour ce qu'il est : un minimum garanti à
chacun de son vivant, financé d'abord par ce que ce minimum laisse derrière
lui, avant de l'être par le contribuable. Il se refuse, comme l'ASPA se
demande. Ceux qui préfèrent transmettre plutôt que recevoir peuvent ne pas le
réclamer, et le programme retient qu'un ayant droit sur deux fera ce
choix.</p>

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
    volontaire = g.pourcentage(base.taux_capitalisation_volontaire, decimales=0)
    total = g.pourcentage(base.taux_capitalisation_applique, decimales=0)
    repartition_ = g.pourcentage(base.taux_cotisation_liberal, decimales=0)
    impose_ = g.pourcentage(
        base.taux_cotisation_liberal + base.taux_capitalisation_obligatoire,
        decimales=0)
    propose = g.pourcentage(base.taux_retraite_propose, decimales=0)
    return g.depliant(
        f"La part capitalisée : {total} qui vous appartiennent",
        f"""
<p>À compter de {base.annee_debut_capitalisation}, {taux} de votre rémunération
sont prélevés <strong>en plus</strong> des {repartition_} de la répartition, et
placés à votre nom sur des titres sans risque. Ce capital ne passe pas par le
compte notionnel : il vous revient, dans un plan d'épargne retraite, l'enveloppe
qui existe déjà et que des millions de Français détiennent. Les années d'avant
ne changent pas :
elles gardent les taux qui étaient les leurs, et qui a déjà liquidé ne cotise
rien.</p>
<p><strong>À ces {taux} s'ajoutent {volontaire} que personne ne vous
impose.</strong> Le système actuel prélève
{g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)} de la rémunération d'un salarié
du privé pour la retraite ; {repartition_} et {taux} en font {impose_}, et la
proposition vous rend donc les cinq points qui restent. Le site suppose que vous
les remettez au même endroit, sur le même compte, aux mêmes conditions : votre
effort revient alors à {propose}, c'est-à-dire à ce qu'il est déjà aujourd'hui,
et les deux systèmes se comparent enfin <strong>à prix égal</strong>. Vous êtes
libre de ne pas le faire : les montants du simulateur disent aussi ce que vous
toucheriez sans.</p>
<ul class="serree">
  <li><strong>Il vous appartient.</strong> Si vous mourez avant d'avoir liquidé,
  le capital revient à vos héritiers, intégralement. Une pension de répartition,
  elle, s'éteint avec vous sans rien laisser.</li>
  <li><strong>Il ne sort qu'à la retraite.</strong> Pas d'achat de résidence
  principale, pas de sortie anticipée : l'argent n'en sort qu'en rente viagère,
  ou par l'héritage. C'est vrai des {taux} obligatoires comme des {volontaire}
  que vous ajoutez.</li>
  <li><strong>Il est placé sans risque.</strong> Des titres d'État parmi les
  mieux notés de la zone euro, portés jusqu'à leur échéance : longue tant que la
  retraite est loin, courte à l'approche du départ. Aucune action, aucun pari.</li>
  <li><strong>Il ne remplace rien.</strong> La retraite par répartition reste ce
  qu'elle est, et le compte notionnel la calcule sans regarder ce capital. Les
  deux montants sont affichés côte à côte, jamais confondus.</li>
</ul>
<p>Ce que cela coûte est chiffré : l'enveloppe prélève des frais, et le
simulateur les montre euro par euro, comme il montre le rendement qui reste. La
page <a href="{g.lien("/methode/")}">Méthode</a> dit à quels
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
             "Chaque carrière est recalculée depuis sa première cotisation, "
             "y compris celles dont la pension est déjà liquidée : le compte "
             "notionnel remplace la pension du droit en vigueur, et ce qui "
             "n'a pas été cotisé n'est plus servi. Les régimes fusionnent en "
             "un seul."],
            ["3. Le taux unique",
             f"Toute cotisation postérieure à la bascule est prélevée à "
             f"{g.pourcentage(base.taux_cotisation_liberal, decimales=0)} de la "
             "rémunération, parts salariale et patronale additionnées, quel que "
             "soit le statut. Les taux qui dépassaient ce niveau baissent, ceux "
             "qui restaient en deçà montent."],
            ["4. La garantie vieillesse",
             "Elle est le seul plancher du système, et remplace le jour de "
             "la bascule les quatre d'aujourd'hui : l'ASPA, le minimum "
             "contributif, le minimum garanti de la fonction publique et la "
             "pension majorée de référence. Elle passe au budget de l'État, "
             "et aucun minimum ne se calcule plus dans le barème de la "
             "pension."],
            ["5. Le pilotage",
             "Le chiffre qui ramène l'année à zéro est publié et appliqué "
             "chaque année. C'est ce qui remplace les réformes."],
            ["6. Le régime de croisière",
             "La dernière pension dont une part des cotisations a été versée "
             "aux anciens taux est liquidée une quarantaine d'années après la "
             "bascule. D'ici là, chaque compte porte des années cotisées aux "
             "taux réels de son régime et des années au taux unique."],
        ],
        ["", "texte"],
        titre="Du système actuel au régime unique",
        entete_de_ligne=True,
    )
    return g.depliant("Comment on y va, étape par étape", f"""
<p>La bascule recalcule tout, depuis la première cotisation.</p>
{etapes}
<p>Après la bascule, un seul régime : départ possible à
{_age(fusionne.age_ouverture)}, assiette déplafonnée, même taux pour tous.</p>""")


def _programme_restitution(contexte: Contexte) -> str:
    """Les impôts que la proposition supprime, et où va l'argent.

    C'est la question que personne ne pose et que tout le monde devrait poser :
    la proposition cesse d'affecter à la retraite une part importante des
    ressources du système, et il faut dire ce qu'elles deviennent.
    Sans cela, le lecteur suppose — à raison — qu'elles vont combler un
    déficit.

    Le dépliant se tait quand le partage vaut zéro : il n'y a alors rien à
    raconter.
    """
    base = contexte.base
    restitution = contexte.restitution()
    if not restitution or restitution.part_rendue <= 0.0:
        return ""
    comptes = contexte.comptes()
    annee = base.annee_bascule
    part = restitution.annuelle(annee)
    if part.poste_abandonne <= 0.0:
        return ""
    pib = comptes.pib(comptes.pib.derniere_annee)
    poids = comptes.part("impots_et_taxes", annee)
    return g.depliant(
        f"Les impôts que nous supprimons : {_milliards(part.rendu * pib, 0)} "
        f"rendus aux salaires",
        f"""
<p>La retraite est financée à {g.pourcentage(poids, decimales=0)} par des
<strong>impôts</strong> ({_milliards(part.poste_abandonne * pib, 0)} en
{annee}) qui n'ouvrent de droit à personne. Un compte notionnel ne sait pas les porter au crédit de qui que ce
soit : il ne rend que ce qui a été cotisé. <strong>Nous cessons donc de les
affecter à la retraite.</strong></p>
<p><strong>Et nous ne les gardons pas.</strong> Ne rien dire de cette recette
reviendrait à la laisser au budget, c'est-à-dire à la consacrer tout entière au
déficit. Nous la partageons en deux :
<strong>{_milliards(part.rendu * pib, 0)} rendus aux salaires</strong>, autant
pour <strong>éteindre de la dette</strong>.</p>
<ul class="serree">
  <li><strong>La taxe sur les salaires est supprimée</strong>, pour la part qui
  finance la retraite, soit {g.pourcentage(0.5835, decimales=2)} de son produit. La
  paient les employeurs qui ne sont pas assujettis à la TVA : hôpitaux,
  cliniques, banques, assurances, associations.</li>
  <li><strong>Le forfait social est supprimé</strong> : il est assis sur
  l'intéressement, la participation et l'épargne salariale, et son produit va
  en entier à l'assurance vieillesse. Avec la taxe sur les salaires, cela fait
  {_milliards(part.supprime_sur_la_remuneration * pib, 0)}.</li>
  <li><strong>La CSG sur les revenus d'activité baisse de
  {g.nombre(part.points_csg * 100, 2)} point</strong> : c'est le solde de ce que
  nous rendons, et l'assiette la plus large qui porte sur le travail.</li>
</ul>
<p>Un mot d'honnêteté sur ce dernier point, parce que l'intuition dit le
contraire : <strong>la CSG sur les revenus d'activité ne finance aujourd'hui
aucune retraite.</strong> Ses {g.pourcentage(0.092)} vont à la branche famille,
à l'assurance maladie, à la dette sociale, à l'assurance chômage et à
l'autonomie. Nous ne vous rendons donc pas une cotisation : nous supprimons un
impôt, avec de l'argent que la retraite n'encaisse plus.</p>
<p><strong>Les employeurs publics suivent la même règle.</strong> L'État verse
aujourd'hui, pour la retraite de ses fonctionnaires, un taux qui n'est pas un
prix du travail mais le solde qui équilibre le régime. Il cotisera
{g.pourcentage(base.taux_cotisation_liberal, decimales=0)} comme tout
employeur, et la moitié de ce qu'il cesse de verser ira au traitement des
agents ; l'autre moitié paiera les pensions déjà promises, qui restent dues.
C'est la seule augmentation de traitement que ce programme contienne, et elle
n'est pas petite.</p>""")


def _programme_blocages(contexte: Contexte) -> str:
    """Les points de blocage regardés avant de choisir, et ce qu'on en a fait.

    Les chiffres sont DATÉS, et la page le dit : ils viennent de trois scripts
    du dépôt qui refont le solde sous d'autres régimes uniques, sous un autre
    traitement du stock et sous une version prospective de la proposition —
    vingt secondes de calcul chacun, et des points d'entrée que le portage ne
    porte pas. La page d'accueil ne calcule rien, et cette section pas
    davantage : elle cite ce qui a été mesuré, et où.
    """
    points = g.tableau(
        ["Le point", "Ce que nous avons regardé", "Ce que nous en retenons"],
        [
            ["La fusion des régimes",
             "Quatre barèmes possibles pour le régime unique : le taux d'aujourd'hui "
             "déplafonné, le statut du salarié du privé avec ses tranches, le régime "
             "général seul, la moyenne des régimes. Un taux plus bas n'est pas plus "
             "négociable, il est impayable : les pensions déjà acquises sont servies "
             "avec moins de cotisations, et sous les deux derniers barèmes le déficit "
             "dépasse cinq points de PIB par an jusqu'en 2050.",
             "Un régime unique se vote par une loi ordinaire : le projet de 2020 l'a "
             "établi, et le Conseil d'État n'y a vu aucun obstacle de principe, ni "
             "pour les fonctionnaires ni pour les complémentaires. Le taux, lui, est "
             "le nôtre, et son coût est chiffré deux lignes plus bas."],
            ["Les pensions déjà servies, recalculées",
             "C'est le point que le juge constitutionnel regarderait en premier : une "
             "pension liquidée est une situation acquise, et la loi qui la touche doit "
             "le justifier et rester proportionnée. Nous ne retirons que ce qui n'a "
             "pas été cotisé, l'indexation sur les prix est conservée, la garantie est "
             "relevée dans le même texte. L'objection la plus forte, celle de l'assuré "
             "parti à l'âge que sa loi lui ouvrait, a été chiffrée : lui prendre le "
             "diviseur de 64 ans plutôt que celui de son âge coûte un dixième de point "
             "de PIB par an, et plus rien en 2050.",
             "Le recalcul est maintenu. La version qui laisse le stock intact a été "
             "chiffrée et écartée : −3,9 points de PIB par an en moyenne jusqu'en "
             "2070, elle n'est pas finançable."],
            ["Le taux de 18 %",
             "Face au taux d'aujourd'hui, 25,8 % part patronale comprise, les 18 % "
             "coûtent 2,3 points de PIB par an sur 2026-2070, sous les mêmes règles de "
             "recette. Le solde de la proposition est de −1,5 point par an en moyenne "
             "contre −1,1 pour le système actuel, et la dette qu'elle accumule en 2070 "
             "vaut 103 % du PIB contre 66 %.",
             "C'est le prix d'un prélèvement plus bas, et il est écrit sur la page "
             "Coût plutôt que caché. Le pilotage annuel, que ces chiffres n'appliquent "
             "pas, est ce qui le tient : le coefficient d'équilibre de 2070 est de "
             "0,92."],
            ["La garantie vieillesse",
             "Le préambule de 1946 garantit aux vieux travailleurs des moyens "
             "convenables d'existence, et un compte purement contributif y répond mal.",
             "La garantie est relevée par rapport à l'ASPA, individualisée, et portée "
             "dans la même loi que le régime : le juge lira les deux ensemble."],
            ["Le chemin législatif",
             "Une réforme systémique n'entre pas dans une loi de financement de la "
             "sécurité sociale, où le Conseil constitutionnel écarte les cavaliers. Il "
             "faut une loi ordinaire, une étude d'impact que le Conseil d'État lira "
             "ligne à ligne, et une trajectoire qui s'explique devant la procédure "
             "européenne pour déficit excessif.",
             "Nous publions l'étude d'impact avant le texte : c'est ce site, ses "
             "réserves comprises."],
        ],
        ["", "texte", "texte"],
        titre="Cinq points de blocage, regardés avant de choisir",
        entete_de_ligne=True,
    )
    return g.depliant("Ce qui pouvait nous arrêter, et ce que nous en avons fait", f"""
<p>Nous avons cherché ce qui arrêterait cette proposition avant de la défendre. Voici les cinq points, ce que nous avons mesuré, et ce que nous en faisons.</p>
{points}
<p class="discret">Mesures des 20 et 21 septembre 2026, par trois scripts du dépôt : le solde sous quatre régimes uniques, le stock à l'âge légal, la proposition prospective. Cette page ne les recalcule pas ; leur détail, décision par décision, est dans la feuille de route du <a href="{g.DEPOT}/blob/main/docs/feuille_de_route.md">dépôt</a>.</p>""")


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
    "population": ("population de la table de conversion", POPULATIONS),
    "rattachement": ("rattachement au niveau de vie", RATTACHEMENTS),
    "conversion_acquis": ("âge de conversion des droits acquis", CONVERSIONS_ACQUIS),
    "part_cotisation": ("part de la cotisation portée au compte", PARTS_COTISATION),
    "foyer": ("situation de foyer", SITUATIONS_FOYER),
    "projection": ("scénario macroéconomique", PROJECTIONS),
    "emploi": ("emploi projeté", TRAJECTOIRES_EMPLOI),
    "stock": ("pensions en cours à la bascule", REVALORISATIONS_STOCK),
    "reprise": ("part de l'avance couverte par la succession", None),
    "frais": ("frais du pilier capitalisé", REGIMES_FRAIS),
    "taux": ("taux futurs du pilier capitalisé", REGIMES_TAUX),
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


def _reglages(saisie: Saisie, chemin: str,
              regards: dict[str, str] | None = None) -> str:
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
    # Et les regards de la page, pour la même raison : ce que le lecteur
    # regardait, « Recalculer cette page » le lui rendait autrement au défaut.
    caches += "".join(g.cache(cle, valeur)
                      for cle, valeur in sorted((regards or {}).items()))
    change = bool(saisie.requete_modelisation())
    return f"""
<details class="section options reglages"{' open' if change else ''}>
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
        g.liste("population", "Population de la table", POPULATIONS,
                saisie.population,
                complement="Par défaut, le diviseur suit la mortalité du "
                "vingtile de niveau de vie où votre salaire vous place, "
                "d'après les tables de l'INSEE : les 5 % les plus aisés "
                "vivent sept ans de plus à 65 ans que les 5 % les plus "
                "modestes chez les hommes, et une table commune le leur "
                "transférerait. « Population générale » revient à cette "
                "table commune ; les autres imposent une population."),
        g.liste("rattachement", "Rattachement au niveau de vie", RATTACHEMENTS,
                saisie.rattachement,
                complement="Ce qui vous place dans un vingtile : votre "
                "salaire rapporté au salaire moyen, ou le rang de votre "
                "pension parmi les retraités, dans la distribution de la "
                "DREES. Par la pension, le vingtile dépend de la pension qui "
                "dépend du diviseur : le modèle itère jusqu'au point fixe."),
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
        g.liste("emploi", "Emploi projeté", TRAJECTOIRES_EMPLOI, saisie.emploi,
                "systèmes 2 à 6 seulement",
                complement="Au-delà de la dernière observation, la masse des "
                "salaires, qui est le rendement des comptes notionnels, est le "
                "salaire moyen composé avec l'emploi. Par défaut, l'emploi "
                "suit le scénario de référence du COR de juin 2026 : chômage "
                "ramené à 7 % en 2040, population active en hausse jusque "
                "vers 2040 puis en recul. Le système 1 n'en lit rien : il "
                "revalorise sur les prix."),
        g.liste("stock", "Pensions en cours à la bascule", REVALORISATIONS_STOCK,
                saisie.stock, "page Coût seulement",
                complement="Ce que la réforme fait des pensions déjà servies "
                "le jour où elle s'applique. Par défaut elles gardent "
                "l'indice des prix que le droit leur promet, et seuls les "
                "comptes ouverts sous le nouveau régime suivent sa règle : "
                "personne ne reçoit un demi-point par an qu'il n'a pas "
                "cotisé. En variante, la réforme réindexe tout le stock sur "
                "la règle du compte, comme les réformes réelles l'ont fait "
                "pour les prix en 1987 : c'est la bosse de 2026-2040 sur la "
                "page Coût, le stock recevant alors un demi-point par an que "
                "personne n'a cotisé, et rien ne change à l'horizon, où ce "
                "stock est éteint. Le système 1 n'est pas concerné : il est "
                "le droit."),
        g.champ("reprise", "Part de l'avance couverte par la succession",
                "" if saisie.reprise is None else saisie.reprise,
                "page Coût seulement, en pour cent ; vide : calculée",
                type_="number",
                complement="La garantie du système 4 est une avance reprise sur la succession, dès le premier euro et avec intérêts. Ce que les successions en rendent dépend du patrimoine des bénéficiaires. Vide, la part est calculée sur le patrimoine des ménages retraités selon leur revenu (COR, enquête Patrimoine 2018) : les plus petites pensions au quart le plus modeste, les autres à l'ensemble des retraités. Un nombre remplace ce calcul : zéro éteint la reprise, cent suppose que toute avance est remboursée.",
                min="0", max="100"),
        g.liste("frais", "Frais du pilier capitalisé", REGIMES_FRAIS, saisie.frais,
                "système 4 seulement",
                complement="Ce que l'enveloppe du pilier prélève, et comment "
                "cela bouge. Par défaut, les vraies moyennes du marché du PER "
                "en 2025 (1,09 % sur versement, 0,76 % par an sur l'encours, "
                "0,99 % sur arrérages, 0,52 % par an sur la réserve de la "
                "rente), qui baissent ensuite par paliers comme partout où une "
                "épargne retraite obligatoire a mis les gérants sous plafond ou "
                "en concurrence ; chaque versement entre au tarif de son année "
                "et le stock ne rejoint le tarif du jour que de 10 % de l'écart "
                "par an. « Plafond » fait suivre tout le stock d'un coup, "
                "« contrats » lui fait garder son tarif ; « sans baisse » fige "
                "2025 ; « PER vendu » est l'ancien réglage, aux 2,20 % "
                "d'arrérages des seuls assureurs qui facturent. La page Méthode "
                "et les limites disent d'où viennent les paliers."),
        g.liste("taux", "Taux futurs du pilier capitalisé", REGIMES_TAUX,
                saisie.taux, "système 4 seulement",
                complement="À quel taux se placent les versements des années "
                "à venir. Par défaut, aux taux à terme que la courbe du jour "
                "implique déjà : le modèle ne prévoit rien, il lit ce que le "
                "marché cote. Cette hypothèse est arbitrée et explicite, mais "
                "elle ignore la prime de terme, le supplément qu'un prêteur "
                "exige pour immobiliser son argent longtemps, et elle flatte "
                "donc le pilier. Les deux autres réglages la retirent, au "
                "milieu puis au haut de la fourchette que la littérature "
                "retient. Ils font baisser la rente, et c'est le prix de "
                "l'hypothèse. Ils font aussi apparaître ce que l'allocation "
                "des maturités vaut : sous le réglage par défaut, elle ne vaut "
                "rien du tout, et placer chaque versement sur le titre qui "
                "tombe l'année du départ rapporte exactement autant qu'un "
                "roulement à un an. La page Méthode et les limites disent "
                "pourquoi."),
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
                _aide_profil(saisie.profil, saisie.statut)),
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
    # Le libellé suit la bascule : demander un « revenu brut » sous un réglage
    # qui annonce le net ferait taper l'un pour l'autre, et le modèle lirait
    # sans broncher un net comme un brut. Les repères chiffrés de l'aide —
    # SMIC, salaire moyen — sont bruts par nature ; ils sont donc convertis
    # eux aussi, statut par statut, ou tus quand on ne sait pas les convertir.
    # Le plafond de la Sécurité sociale n'en fait plus partie : sous un champ
    # numérique, « plafond 4 005 € » se lit comme le maximum que le champ
    # accepte, et c'est ainsi qu'un lecteur l'a lu. Le repère ne parle qu'à
    # qui connaît la tuyauterie des régimes ; les deux autres parlent à tous.
    en_net = saisie.saisie_en_net
    mot = "net" if en_net else "brut"
    # Le statut dont le dépôt n'a pas les prélèvements hors retraite : le
    # nombre y est lu tel quel. L'aide doit le dire ELLE AUSSI, et non
    # promettre une conversion que l'avertissement, deux lignes plus bas,
    # viendra démentir — le lecteur croirait alors que l'une des deux phrases
    # ne le concerne pas, sans savoir laquelle.
    converti = en_net and echelle.convertit(saisie.statut)
    repere = ((lambda montant: echelle.net_mensuel(montant, saisie.statut))
              if converti else (lambda montant: montant))
    aide = (f"en euros {mot}s par mois" if bref else
            f"Repères : SMIC {g.euros(repere(echelle.smic))}, salaire moyen "
            f"{g.euros(repere(echelle.mensuel(1)))}")
    if converti:
        complement = (
            "En euros d'aujourd'hui, tels qu'ils arrivent sur le compte — pour "
            "un salarié, la ligne « net à payer » de la fiche de paie. Le "
            "modèle remonte au brut par les prélèvements de votre statut, puis "
            "le suit le long du salaire moyen, année après année."
        )
    elif en_net:
        complement = (
            "En euros d'aujourd'hui. Le modèle n'a pas les prélèvements hors "
            "retraite de ce statut : il ne peut pas remonter au brut, et lit "
            "donc le nombre tel quel, puis le suit le long du salaire moyen, "
            "année après année."
        )
    else:
        complement = (
            "En euros d'aujourd'hui, avant cotisations et impôt — pour un "
            "salarié, la ligne « brut » de la fiche de paie. Le modèle le suit "
            "ensuite le long du salaire moyen, année après année."
        )
    return g.champ(nom, f"Revenu {mot} mensuel", valeur, aide, type_="number",
                   complement="" if bref else complement,
                   min="0", step="1")


def _aide_profil(profil: str, affiliation: str | None = None) -> str:
    """Ce que le profil fait du salaire saisi, en toutes lettres.

    Sans elle, saisir « 2 900 € par mois » se lit comme la promesse de gagner
    2 900 € chaque année de sa vie, alors que le revenu saisi est celui du
    milieu de carrière et que le profil le déforme aux deux bouts.
    """
    debut, fin = bornes_deformation(RACINE_DONNEES, profil, affiliation)
    if debut == fin:
        return "le revenu saisi vaut pour toutes les années de la carrière"
    return (f"le revenu saisi est celui du milieu de carrière : ×{g.nombre(debut, 2)} "
            f"au premier emploi, ×{g.nombre(fin, 2)} après une carrière complète")


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
    cible = f"#/simuler?{escape(saisie.requete(**remplacements))}"
    # Le MÊME composant que la bascule des montants, juste au-dessus d'elle.
    # Les deux réglages du formulaire faisaient le même travail et n'avaient
    # pas la même forme : un lien souligné d'un côté, un contrôle de l'autre.
    # L'un des deux se voyait, l'autre pas, et rien ne disait qu'ils étaient de
    # même nature.
    euros, multiple = "€ par mois", "× salaire moyen"
    branches = [(euros, cible if vers_les_euros else "#"),
                (multiple, "#" if vers_les_euros else cible)]
    return g.bascule("Unité", branches, multiple if vers_les_euros else euros)


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

    # La clé de lecture SUIT LE MODE, sous peine de démentir les chiffres
    # qu'elle explique. Elle a dit « montants bruts, avant CSG » au-dessus de
    # montants nets, et « un brut sur un brut, donc plus bas qu'un taux calculé
    # sur des nets » au-dessus d'un taux de remplacement calculé, précisément,
    # sur des nets. Une clé de lecture fausse est pire qu'absente : elle
    # enseigne l'erreur à qui prend la peine de la lire.
    if saisie.en_net:
        prelevements = (
            "Montants <strong>nets</strong> et au centime, tels qu'ils "
            "arrivent sur le compte : après CSG, CRDS et Casa — 9,10 %, le "
            "taux plein, appliqué ici à tout le monde — et avant impôt sur le "
            "revenu, comme le revenu d'activité saisi plus haut. Le "
            "<strong>taux de remplacement</strong> rapporte la pension "
            "annuelle au dernier revenu d'activité ramené à l'année pleine — "
            "un net sur un net, donc plus haut qu'un taux calculé sur des "
            "bruts."
        )
    else:
        prelevements = (
            "Montants <strong>bruts</strong> et au centime, comme la caisse "
            "les verse : avant CSG, CRDS et impôt, comme le revenu d'activité "
            "saisi plus haut. Le <strong>taux de remplacement</strong> "
            "rapporte la pension annuelle au dernier revenu d'activité ramené "
            "à l'année pleine — un brut sur un brut, donc plus bas qu'un taux "
            "calculé sur des nets."
        )

    return g.bulle(
        "De quand sont ces chiffres, et en quels euros",
        f"{quand} {unites} Ce que compare cette page, ce sont quatre façons de "
        "CALCULER une pension de départ, pas quatre façons de la revaloriser "
        f"ensuite. {prelevements}",
    )


def _corps_trajectoire(contexte: Contexte, comparaison: Comparaison,
                       saisie: Saisie, seul: bool = False) -> str:
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
<p>{"Chaque système sert une pension mensuelle ; ce graphique"
     if seul else
     "Les quatre montants du haut sont ceux d'un seul mois, le premier. Ce graphique"}
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
        # `seul` : la page ne montre pas les quatre montants mensuels que le
        # dépliant de Simuler a au-dessus de lui, et sa phrase ne les cite pas.
        corps = _corps_trajectoire(contexte, comparaison, saisie, seul=True)
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
    volontaire = g.pourcentage(
        base.taux_capitalisation_volontaire_applique, decimales=0)
    propose = g.pourcentage(base.taux_retraite_propose, decimales=0)
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
            f"{taux} + {capitalise}",
            "de cotisation retraite, pour tout le monde.",
            f"{g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)} aujourd'hui pour "
            f"un salarié du privé ({g.pourcentage(TAUX_ACTUEL_SALARIAL)} + "
            f"{g.pourcentage(TAUX_ACTUEL_PATRONAL)}). Les {volontaire} rendus "
            f"peuvent aller au même compte : {propose} en tout, comme "
            "aujourd'hui, pour une retraite qui vous appartient.",
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
    {g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)}, {capitalise} capitalisés
    à votre nom et {volontaire} rendus que vous placez où vous voulez, et un
    compte de retraite en euros que chacun peut lire. Vérifiez sur votre
    carrière : {g.ADRESSE_SITE} — {g.SIGNATURE} »</p>
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

    Ces libellés ont été récrits deux fois. « Notionnel rétroactif » ne disait
    rien à qui n'avait pas lu la page Méthode ; « Compte notionnel, part
    salariale seule » nommait bien l'assiette, mais en termes de cotisant, pas
    de lecteur : il fallait savoir qu'un compte notionnel est alimenté par les
    cotisations pour comprendre que la barre 2 montre la pension que rendrait
    CE QU'ON A VERSÉ. Les titres le disent maintenant en toutes lettres — « ce
    que vous avez cotisé », part salariale seule ou les deux parts —, et
    l'écart entre les deux barres se lit alors pour ce qu'il est : ce que
    l'employeur verse.

    Cette formule ne vaut que sur Simuler, où la carrière affichée est celle du
    lecteur. Cas types montre les carrières d'autres gens et Coût une dépense
    nationale : ``LIBELLES_SYSTEMES`` y garde sa forme impersonnelle.

    La glose sous chaque barre porte ce que le titre ne dit pas : depuis quand
    la carrière est recalculée. Sans elle on ne comprendrait pas pourquoi le 2
    donne moins que le 4.
    """
    return (
        ("actuel", "1. Système de répartition actuel"),
        ("notionnel_retroactif",
         "2. Ce que vous avez cotisé, part salariale seule"),
        ("notionnel_retroactif_employeur",
         "3. Ce que vous avez cotisé, part salariale + patronale"),
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


#: Le scénario du modèle derrière chaque barre des résultats. Les clés sont
#: celles des classes CSS, qui ne portent pas les noms du modèle ; elles se
#: rencontrent ici et nulle part ailleurs.
SCENARIOS_DES_BARRES: dict[str, str] = {
    "actuel": "actuel",
    "retroactif": "notionnel_retroactif",
    "retroactif-employeur": "notionnel_retroactif_employeur",
    "liberal": "notionnel_liberal",
}


def _financements(contexte: Contexte,
                  comparaison: Comparaison) -> dict[str, PensionFinancee]:
    """Ce que les comptes financent de chacun des quatre montants affichés.

    Le coefficient d'équilibre ne dépend pas de la carrière — c'est une
    grandeur du SYSTÈME, un rapport de masses. De la carrière, il ne prend que
    deux choses : l'année du départ, et la courbe de survie qui dit combien de
    temps la pension sera servie. C'est donc la même table pour tout le monde,
    lue à des dates différentes.

    Vide quand le départ précède les comptes du COR, qui commencent en 2002 :
    afficher un coefficient tiré d'années postérieures au départ, sous un
    montant qui est celui du premier mois de retraite, ferait dire à la page
    ce qu'aucun compte ne dit.
    """
    carriere = comparaison.carriere
    bilan = contexte.bilan()
    if carriere.annee_liquidation < bilan.premiere_annee:
        return {}
    survie = _survie(contexte, carriere,
                     comparaison.notionnel_retroactif.conversion.table)
    # Le poids d'une année est la part des partants encore en vie EN SON
    # MILIEU : une pension servie du 1er janvier au 31 décembre l'est à une
    # population qui décroît pendant l'année, et prendre la part du 1er
    # janvier la surestimerait d'une demi-année de mortalité.
    poids = tuple(_part_vivante(survie, rang + 0.5)
                  for rang in range(max(len(survie) - 1, 0)))
    financements = {}
    for cle, scenario in SCENARIOS_DES_BARRES.items():
        part = financer(bilan, bilan.assiette, scenario,
                        carriere.annee_liquidation, poids)
        if part is not None:
            financements[cle] = part
    return financements

def _glose_financement(finance: PensionFinancee | None) -> str:
    """La clause que la glose gagne : ce que les comptes en financent.

    Écrite dans les deux sens, parce que le coefficient se lit dans les deux —
    un manque sous un, une marge au-dessus. La marge n'est jamais convertie en
    euros : elle dit qu'un système AURAIT DE QUOI servir davantage, pas qu'il
    servirait davantage, et la différence est tout ce qui sépare un fait d'une
    promesse.
    """
    if finance is None:
        return ""
    if finance.manque > 0.0:
        return (" · les recettes du système n'en paient que "
                f"{g.pourcentage(finance.coefficient, decimales=0)}")
    # « 163 % de marge » ne dit rien à personne ; « couvert 2,6 fois », si.
    return (" · les recettes du système couvrent ce montant "
            f"{g.nombre(finance.coefficient, 1)} fois")


def _financement(contexte: Contexte, comparaison: Comparaison,
                 finances: dict[str, PensionFinancee],
                 montants: "Montants") -> str:
    """Le dépliant qui dit d'où vient le troisième chiffre, et ce qu'il n'est pas.

    C'est le seul endroit du simulateur où le site dit que le montant du
    système 1 est une PROMESSE et non une prévision. Il doit donc dire trois
    choses et les distinguer : ce que les comptes portent, qui est un fait ; ce
    qu'il faudrait faire pour que l'année tombe juste, qui est une arithmétique
    à trois branches dont aucune n'est décidée ; et ce que l'histoire des
    réformes apprend de la branche qu'on choisit, qui est une régularité
    observée, pas une loi.

    IL A ÉTÉ ÉCRIT DEUX FOIS. La première version ouvrait sur le coefficient
    d'équilibre et deux tableaux de nombres sans dimension — 0,90 puis 0,87,
    des points d'assiette, des parts de PIB. Tout y était vrai et rien n'y
    était lisible : un électeur n'a pas de repère pour « 3,5 points
    d'assiette », il en a un pour « 122 € prélevés chaque mois sur un salaire
    moyen ». Les trois leviers sont donc désormais donnés dans les unités où on
    les vit — une pension mensuelle, une fiche de paie, des milliards —, et le
    tableau des coefficients est descendu sous eux, pour qui veut refaire le
    calcul.

    UNE DIFFICULTÉ QU'IL FAUT TENIR PLUTÔT QUE MASQUER. Les leviers sont
    chiffrés à l'année du départ, où ils partagent un seul dénominateur et se
    déduisent l'un de l'autre. Le troisième chiffre des résultats, lui, moyenne
    toute la durée de la retraite, où le manque grandit : il est donc plus
    sévère. La page l'écrit, et ne donne le manque en euros qu'à un seul
    endroit — sous le chiffre — pour que deux sommes voisines ne se disputent
    pas le même rôle.
    """
    if not finances:
        return ""
    bilan = contexte.bilan()
    depart = comparaison.carriere.annee_liquidation
    reference = finances.get("actuel")
    if reference is None:
        return ""
    depart_dit = (f"{depart}, l'année où vous partiriez" if reference.depart_couvert
                  else f"{reference.premiere_annee}, la première année que les "
                       "comptes couvrent")

    # Les trois leviers du système ACTUEL, en unités de la vie courante. Le
    # salaire moyen brut d'aujourd'hui sert d'étalon à la hausse de cotisation :
    # un point d'assiette est un point de revenu d'activité, et l'appliquer à un
    # salaire est exact parce que le prélèvement est proportionnel.
    macro = contexte.simulateur(comparaison.parametres).macro
    salaire_moyen = salaire_moyen_annuel(macro, comparaison.parametres.annee_courante)
    cotisation_mensuelle = reference.points_assiette * salaire_moyen / MOIS_PAR_AN
    # ``_milliards`` attend des MILLIONS : le PIB de la table est dans cette
    # unité, et le manque est une part de lui.
    manque_meur = reference.manque_pib * bilan.pib
    points = reference.points_assiette * 100
    unite_points = "point" if points < 2.0 else "points"

    leviers = f"""
<ul class="leviers">
  <li><strong>Les retraités paient</strong> — toutes les pensions sont rognées
    de {g.pourcentage(1 - reference.coefficient_depart, decimales=0)}, la vôtre
    comme les autres. C'est le levier que le troisième chiffre applique.</li>
  <li><strong>Les actifs paient</strong> — les cotisations montent de
    {g.nombre(points, 1)} {unite_points} de revenu d'activité, soit
    {g.euros(cotisation_mensuelle)} de plus prélevés chaque mois sur un salaire
    moyen
    ({g.euros(salaire_moyen / MOIS_PAR_AN)} brut par mois aujourd'hui).</li>
  <li><strong>Personne ne paie, pour l'instant</strong> — le déficit est
    emprunté : {_milliards(manque_meur, 0)} par an, au PIB d'aujourd'hui, qui s'ajoutent à la dette publique et que rembourseront ceux
    qui viendront après.</li>
</ul>"""

    lignes = []
    for cle, scenario in SCENARIOS_DES_BARRES.items():
        finance = finances.get(cle)
        if finance is None:
            continue
        lignes.append([
            LIBELLES_SYSTEMES[scenario],
            g.pourcentage(finance.coefficient_depart, decimales=0),
            g.pourcentage(finance.coefficient, decimales=0),
            g.nombre(finance.coefficient, 2),
        ])

    horizon = ""
    if not reference.entiere:
        horizon = (
            f"<p><strong>Les comptes s'arrêtent en {bilan.derniere_annee}, et "
            "la page n'invente pas la suite.</strong> Ils couvrent "
            f"{g.pourcentage(reference.part_couverte, decimales=0)} de votre "
            "retraite ; les années d'après ne sont comptées nulle part. Ce "
            "n'est pas une prudence neutre : le manque GRANDISSAIT encore à "
            "cette date — les recettes payaient "
            f"{g.pourcentage(bilan.annee(bilan.derniere_annee_observee).coefficient('actuel'), decimales=0)} "
            f"des pensions en {bilan.derniere_annee_observee} et "
            f"{g.pourcentage(bilan.annee(bilan.derniere_annee).coefficient('actuel'), decimales=0)} "
            f"en {bilan.derniere_annee}. Les années que la page laisse de côté "
            "sont donc les pires, et le chiffre affiché est un maximum.</p>"
        )

    detail = g.depliant("Le détail : le calcul, et les quatre systèmes", f"""
<p>Ce que les recettes d'une année paient des pensions de cette année-là, pour
chacun des quatre systèmes. Au-dessus de 100 %, le système encaisse plus qu'il
ne verse : c'est une marge, et le site ne la convertit jamais en pension plus
élevée, parce que servir une marge est une décision que personne n'a prise.</p>

{g.tableau(
    ["Système", f"En {depart}", "Sur toute votre retraite",
     "Coefficient d'équilibre"],
    lignes,
    ["", "nombre", "nombre", "nombre"],
    titre="Part des pensions que les recettes paient, aux dates de cette carrière",
    entete_de_ligne=True,
)}

<p class="discret">La dernière colonne est le même nombre sous le nom que lui
donnent les économistes : le <strong>coefficient d'équilibre</strong>, facteur
par lequel il faudrait multiplier toutes les pensions d'une année pour que
cette année tombe juste — ressources divisées par dépenses. Les ressources et
les dépenses sont celles que le COR consolide, observées jusqu'en
{bilan.derniere_annee_observee} et projetées ensuite ;
<a href="{g.lien("/cout")}">la page Coût</a> les montre poste par poste. Pour
le système actuel, le coefficient est le rapport de ces deux séries, et aucun
réglage de ce simulateur ne le déplace. Pour les trois autres, la dépense est
une masse de pensions que le modèle calcule et qui dépend des règles : les
coefficients affichés ici sont ceux des réglages de référence, pas de ceux que
vous avez cochés — la page Coût, elle, les recalcule sous les réglages qu'on
lui demande.</p>
""", identifiant="resultats-financement-detail")

    return g.depliant(
        "Le système promet plus qu'il n'encaisse : qui paiera la différence ?",
        f"""
<p class="chapeau">Le système de retraite verse aujourd'hui plus qu'il ne
reçoit, et le Conseil d'orientation des retraites — l'organisme public qui
tient ses comptes — le projette en déficit jusqu'en {bilan.derniere_annee}. Le
montant du système 1 est ce que la loi promet ; il ne dit pas que l'argent
est là.</p>

<p>En {depart_dit}, il manquera
{g.pourcentage(1 - reference.coefficient_depart, decimales=0)} de ce que le
système doit verser. Cette différence, quelqu'un la paiera, et il
n'y a que trois façons de la payer. Aucune n'est décidée ; les voici toutes les
trois, pour la même année :</p>

{leviers}

<p>Le troisième chiffre des résultats applique la première, parce que c'est la
seule des trois qui se lise sur une pension. Il est un peu plus sévère que les
{g.pourcentage(1 - reference.coefficient_depart, decimales=0)} ci-dessus : il
ne s'arrête pas à l'année du départ, il fait la moyenne de toutes vos
années de retraite, où le manque grandit, chaque
année comptant pour le nombre de partants encore en vie. Un quatrième levier
existe — reculer l'âge —, et ce simulateur le mesure déjà : changez l'âge de
liquidation, et les quatre montants bougent.</p>

{horizon}

<p><strong>Sur qui l'ajustement est tombé, les fois précédentes.</strong> Les
réformes des pays du G7 dans les années 1990 ont eu « un impact majeur sur la
valeur actualisée des prestations promises aux travailleurs d'âge moyen et
jeunes », alors que « les prestations des retraités et de ceux proches de la
retraite sont habituellement protégées » (McHale, 1999). Rogner toutes les
pensions du même taux, comme fait le troisième chiffre, est donc la version
DOUCE : dans les réformes observées, ce sont ceux qui n'ont pas encore liquidé
qui ont payé. <a href="{g.lien("/risque")}">La page Risque</a> rassemble ce que
la recherche en sait.</p>

{detail}
""", identifiant="resultats-financement")

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
    # La part de cette rente qui vient des cinq points VOLONTAIRES — ceux que
    # la proposition rend et que le site suppose remis au compte. Elle est
    # nommée à part sous la barre : c'est la seule ligne de la page que
    # personne n'impose, et le lecteur doit pouvoir la retrancher de l'œil.
    capitalise_volontaire = comparaison.en_euros_constants(
        comparaison.notionnel_liberal.rente_capitalisation_volontaire
    )
    reference = max(constants.values()) or 1.0

    # Ce que les comptes du système financent de chacun de ces montants, à la
    # date où celui qui lit partirait. Le montant reste celui de la règle —
    # c'est ce que le système PROMET, et le scénario 1 est le droit en vigueur,
    # rien d'autre ; ce second chiffre est ce que les recettes de ses années de
    # retraite paient. Les afficher l'un sans l'autre serait mentir dans un
    # sens ou dans l'autre.
    finances = _financements(contexte, comparaison)

    montants = Montants.depuis(saisie, comparaison.parametres, comparaison)
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
             taux_remplacement: float, part_capitalisee: float = 0.0,
             part_volontaire: float = 0.0) -> str:
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
        # La barre montre ce que les comptes paient, puis ce qui manque pour
        # tenir la promesse — même couleur, quasi effacée. Un système dont les
        # comptes couvrent la promesse n'a pas de seconde tranche, et sa barre
        # est celle qu'elle a toujours été.
        finance = finances.get(cle)
        manque = (repartition * finance.manque
                  if finance is not None and finance.manque > 0.0 else 0.0)
        barre = ('<span style="width:'
                 f'{(repartition - manque) / reference * 100:.1f}%"></span>')
        if manque > 0.0:
            barre += ('<span class="manque" style="width:'
                      f'{manque / reference * 100:.1f}%"></span>')
        partage = ""
        if part_capitalisee > 0:
            barre += (f'<span class="capitalise" '
                      f'style="width:{part_capitalisee / reference * 100:.1f}%"></span>')
            # Trois montants nommés plutôt que deux dès qu'il y a du
            # volontaire, ET LE PLANCHER ÉCRIT ENTRE LES DEUX : additionner en
            # silence une épargne facultative à une cotisation obligatoire
            # ferait promettre au lecteur un montant qu'il n'aura que s'il la
            # verse. Le grand nombre dit donc « jusqu'à », et cette ligne dit
            # ce qu'il touche sans rien ajouter, puis ce que les cinq points
            # rendus lui ajoutent s'il les place. « Sans risque » n'est pas un
            # argument de vente : c'est le placement du pilier, des titres
            # d'État portés jusqu'à leur échéance, et c'est ce qui autorise le
            # mot « jusqu'à » — le montant du haut s'atteint par une décision,
            # pas par un coup de bourse.
            detail = (
                f"""
        {g.euros_centimes(montants.pension(part_capitalisee - part_volontaire) / 12)}
        de rente capitalisée obligatoire — soit
        {g.euros_centimes(montants.pension(montant - part_volontaire) / 12)} par
        mois sans rien ajouter — et
        {g.euros_centimes(montants.pension(part_volontaire) / 12)} de plus si
        vous placez les cinq points rendus, sans risque"""
                if part_volontaire > 0 else
                f"""
        {g.euros_centimes(montants.pension(part_capitalisee) / 12)} de rente
        capitalisée, par mois"""
            )
            partage = f"""
      <span class="composition">{g.euros_centimes(montants.pension(repartition) / 12)}
        de pension par répartition +{detail}</span>"""
        # Le troisième chiffre n'apparaît QUE là où le coefficient est sous un,
        # c'est-à-dire là où le système promet plus que ses comptes ne
        # rentrent. Au-dessus de un, il dirait « financé : 927 € » sous une
        # pension de 265 € — or un coefficient supérieur à un ne promet aucune
        # pension plus élevée : il dit qu'un système AURAIT DE QUOI servir
        # davantage, ce que personne n'a décidé. La marge est donc écrite en
        # toutes lettres dans la glose, et jamais convertie en euros.
        chiffre_finance = ""
        if finance is not None and finance.manque > 0.0:
            servie = finance.servie(montant, part_capitalisee)
            # Le manque EN EUROS, sous le chiffre, dans l'idiome que le salaire
            # utilise déjà pour son écart. C'est lui que le lecteur retient :
            # « 87 % » est un taux, « il manque 393 € par mois » est une somme
            # qu'on compare à un loyer.
            manque_mensuel = montants.pension(montant - servie) / 12
            chiffre_finance = f"""
      <span class="chiffre finance">
        <span class="categorie">vraiment payé</span>
        <span class="somme">{g.nombre(montants.pension(servie) / 12)}</span>
        <span class="unite">{montants.unite_pension}</span>
        <span class="ecart">il manque {g.euros(manque_mensuel)} par mois</span>
      </span>"""
        return f"""
<div class="scenario">
  <div class="entete">
    <span class="titre">{escape(titre)}</span>
    <span class="montant">{salaire(cle)}
      <span class="chiffre principal">
        <span class="categorie">{"retraite jusqu'à" if part_volontaire > 0
                                 else "retraite"}</span>
        <span class="somme">{g.nombre(montants.pension(montant) / 12)}</span>
        <span class="unite">{montants.unite_pension}</span>
      </span>{chiffre_finance}
    </span>
  </div>{partage}
  <div class="barre {cle}">{barre}</div>
  <div class="glose">{glose} · {g.terme("taux de remplacement")}
    {g.pourcentage(montants.taux_remplacement(taux_remplacement))} ·
    écart au système actuel : {variation_html}{_glose_financement(finance)}</div>
</div>"""

    # La glose porte ce que le titre ne dit plus : DEPUIS QUAND la carrière est
    # recalculée, et à quel taux. C'est ce qui explique l'ordre des montants —
    # sans elle, on ne voit pas pourquoi le 2 donne moins que le 4 alors que
    # tous deux sont des comptes notionnels.
    scenarios = (
        bloc("actuel", "1. Système de répartition actuel",
             "le droit en vigueur, minima et majorations compris",
             None, comparaison.taux_remplacement_actuel)
        + bloc("retroactif", "2. Ce que vous avez cotisé, part salariale seule",
               "toute la carrière recalculée depuis 1941, sur la seule part "
               "salariale — 11,3 % du brut pour un salarié du privé",
               comparaison.variation("notionnel_retroactif"),
               comparaison.taux_remplacement_retroactif)
        + bloc("retroactif-employeur",
               "3. Ce que vous avez cotisé, part salariale + patronale",
               "la même carrière recalculée depuis 1941, les deux parts "
               "comprises — les 28 % prélevés aujourd'hui",
               comparaison.variation("notionnel_retroactif_employeur"),
               comparaison.taux_remplacement("notionnel_retroactif_employeur"))
        + bloc("liberal",
               "4. La proposition du Parti libéral français",
               f"le système 3 jusqu'à {saisie.bascule}, puis "
               f"{g.pourcentage(comparaison.parametres.taux_cotisation_liberal, decimales=0)} "
               "pour tous en répartition, "
               f"{g.pourcentage(comparaison.parametres.taux_capitalisation_obligatoire, decimales=0)} "
               "capitalisés par-dessus et "
               f"{g.pourcentage(comparaison.parametres.taux_capitalisation_volontaire_applique, decimales=0)} "
               f"que vous ajoutez librement pour cotiser autant qu'aujourd'hui "
               f"({g.pourcentage(comparaison.parametres.taux_retraite_propose, decimales=0)} "
               "en tout), les uns comme les autres placés sans risque — plus "
               "une garantie vieillesse payée par l'impôt",
               comparaison.variation_totale("notionnel_liberal"),
               comparaison.taux_remplacement_total("notionnel_liberal"),
               part_capitalisee=capitalise,
               part_volontaire=capitalise_volontaire)
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
        f'<span class="etiquette-fiabilite">{escape(g.fiabilite_en_clair(comparaison.fiabilite))}'
        "</span></p>"
    )
    # La clé de lecture, avant les chiffres. Les six blocs portent des titres
    # exacts ; aucun ne disait qu'il n'y a qu'une carrière, ni que le premier
    # est la référence des cinq autres. Cinq phrases, en clair.
    lecture = f"""
<p class="note resume"><strong>Quatre calculs pour votre carrière.</strong>
Le système 1 applique les règles d'aujourd'hui. C'est la référence.
Les trois autres appliquent chacun d'autres règles à la même carrière.
Trois chiffres par ligne : votre <strong>salaire</strong> pendant que vous
cotisez, la <strong>pension</strong> que le système promet une fois retraité,
et, quand ses recettes n'y suffisent pas, ce qu'elles en paient
<strong>vraiment</strong> — en {montants.mot} tous les trois,
{unite_reference}. Le troisième chiffre n'est pas une prévision : il dit de
combien les comptes du système sont courts, et le dépliant
« <a href="#resultats-financement">Le système promet plus qu'il n'encaisse</a> »
dit qui peut payer la différence.
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
  {_bascule_montants(saisie, contexte.echelle(saisie))}
  {scenarios}
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
{_financement(contexte, comparaison, finances, montants)}
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

    # L'emploi projeté, rejoué sous l'autre trajectoire : il ne déplace que les
    # systèmes 2 à 6, par l'indexation, et le lecteur doit le voir.
    autre_emploi = "constant" if saisie.emploi != "constant" else "cor_2026"
    try:
        sous_autre = contexte.simuler(
            Saisie(**{**saisie.__dict__, "emploi": autre_emploi}))
    except (ErreurSaisie, DonneeInsuffisante, KeyError, ValueError):
        poids_emploi = ""
    else:
        autre_2 = sous_autre.en_euros_constants(
            sous_autre.notionnel_retroactif.pension_annuelle) / 12
        ecart_emploi = autre_2 / reference - 1.0 if reference > 0 else float("nan")
        poids_emploi = f"""
<p>L'emploi projeté pèse à part. Avec un {"emploi constant" if autre_emploi == "constant" else "emploi suivant la trajectoire du COR"}
après {derniere_observee}, au lieu de {"la trajectoire du COR" if autre_emploi == "constant" else "l'emploi constant"} retenu{"e" if autre_emploi == "constant" else ""} ici, le système 2
donnerait {g.euros_centimes(autre_2)} par mois, soit
{g.pourcentage(ecart_emploi, signe=True)}. Le système 1 ne bouge pas : il
revalorise sur les prix et ne lit pas l'emploi.</p>"""

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
    "les autres hypothèses — inflation à 1,75 %, "
    + ("emploi constant" if saisie.emploi == "constant"
       else "emploi suivant la trajectoire du COR")
    + ", législation inchangée : c'est une mesure de sensibilité à un "
    "paramètre, non un intervalle de confiance, et l'avenir peut en sortir.",
)}</p>
{g.tableau(
    ["Système", "Productivité 0,4 %", escape(retenu), "Productivité 1,0 %",
     "Amplitude"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
    titre="Pension mensuelle de chaque système sous les trois hypothèses de "
          "productivité du COR",
    entete_de_ligne=True,
)}{poids_emploi}
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
    ((300.0, 300.0), "300 € et 300 €"),
    ((300.0, 1500.0), "300 € et 1 500 €"),
    ((900.0, 900.0), "900 € et 900 €"),
    ((300.0, 5000.0), "300 € et 5 000 €"),
    ((300.0,), "personne seule, 300 €"),
)



def _pilier_capitalise(comparaison: Comparaison, saisie: Saisie) -> str:
    """Le pilier capitalisé : ce qu'il reçoit, ce qu'il rend, ce qu'il lègue.

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
    taux_impose = g.pourcentage(pilier.taux_cotisation_obligatoire, decimales=0)
    taux_volontaire = g.pourcentage(pilier.taux_cotisation_volontaire, decimales=0)
    avec_volontaire = pilier.taux_cotisation_volontaire > 0
    depart = comparaison.carriere.annee_liquidation

    if not pilier.actif:
        return g.depliant(
            f"Le pilier capitalisé : {taux} placés dès "
            f"{parametres.annee_debut_capitalisation}",
            f"""
<p>Cette carrière ne cotise pas au pilier : elle s'achève en {depart}, et la
cotisation capitalisée n'est due qu'à compter de
{parametres.annee_debut_capitalisation}. La proposition ne demande rien au
passé — ni ce taux, ni un autre —, et qui a liquidé avant la bascule reçoit
donc, du système 4, la seule pension de répartition.</p>""",
        )

    premiere = pilier.annees[0]
    derniere = pilier.annees[-1]

    # Les frais sont des paramètres, et ils bougent : chaque ligne de la
    # cascade dit le tarif de la première année et celui de la dernière, tels
    # que le pilier les a effectivement subis. Changer le barème change la page.
    def fourchette(debut: float, fin: float) -> str:
        if abs(debut - fin) < 5e-7:
            return g.pourcentage(debut, decimales=2)
        return (f"de {g.pourcentage(debut, decimales=2)} à "
                f"{g.pourcentage(fin, decimales=2)}")
    rente_brute = pilier.capital / pilier.conversion.diviseur
    rente_apres_reserve = rente_brute * pilier.facteur_encours_rente

    # Ce que devient un euro versé : la cascade complète, du prélèvement à la
    # rente. Chaque ligne est une opération, et la suivante part du résultat de
    # la précédente — c'est la seule façon de rendre un capital vérifiable.
    cascade = g.tableau(
        ["", "Ce qui se passe", f"Montant, en euros de {depart}"],
        [
            [f"a) Cotisation de {taux}",
             (f"{taux_impose} imposés et {taux_volontaire} volontaires, "
              if avec_volontaire else "")
             + f"prélevés sur la même assiette que la cotisation notionnelle, "
             f"de {premiere.annee} à {derniere.annee}, EN PLUS d'elle",
             g.euros(pilier.versements)],
            ["b) − frais sur versement",
             f"{fourchette(premiere.taux_frais_versement, derniere.taux_frais_versement)} "
             f"de chaque versement, de {premiere.annee} à {derniere.annee}",
             "− " + g.euros(pilier.frais_versement)],
            ["c) + intérêts",
             "placés sur des titres sans risque, à des maturités qui "
             "raccourcissent à l'approche du départ",
             "+ " + g.euros(pilier.interets)],
            ["d) − frais de gestion",
             f"{fourchette(premiere.taux_frais_gestion, derniere.taux_frais_gestion)} "
             "par an sur l'encours, chaque versement gardant le tarif de son année",
             "− " + g.euros(pilier.frais_gestion)],
            ["e) = capital au départ",
             "ce que vaut le compte le jour de la liquidation",
             g.euros(pilier.capital)],
            ["f) ÷ coefficient de conversion",
             f"{g.nombre(pilier.conversion.diviseur, DECIMALES_DIVISEUR)}, la "
             "même table de mortalité que la pension notionnelle",
             g.euros(rente_brute) + " par an"],
            ["g) − frais sur la réserve de rente",
             f"{g.pourcentage(pilier.frais_encours_rente, decimales=2)} par an "
             "sur la réserve qui porte la rente, au tarif de l'année du départ",
             "− " + g.euros(rente_brute - rente_apres_reserve) + " par an"],
            ["h) − frais sur arrérages",
             f"{g.pourcentage(pilier.frais_arrerages, decimales=2)} "
             "de chaque versement de rente, au tarif de l'année du départ",
             "− " + g.euros(rente_apres_reserve - pilier.rente_annuelle) + " par an"],
            ["i) = rente servie", "à vie, et qui s'éteint avec le rentier",
             g.euros_centimes(pilier.rente_annuelle) + " par an"],
        ],
        ["", "texte", "nombre"],
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
        ["", "nombre", "texte"],
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

    # Ce que servent les cinq points volontaires, nommé à part : le pilier est
    # exactement proportionnel à son taux, si bien que la moitié volontaire
    # rend la moitié de la rente. Le lecteur doit pouvoir retrancher cette
    # ligne, qui est la seule de la page que personne ne lui impose.
    partage_volontaire = ""
    if avec_volontaire:
        partage_volontaire = f"""
<p><strong>Sur cette rente, {g.euros_centimes(pilier.rente_volontaire)} par an
viennent des {taux_volontaire} que vous versez librement</strong>, et
{g.euros_centimes(pilier.rente_obligatoire)} des {taux_impose} que la
proposition impose. Le compte ne les distingue nulle part ailleurs : même
assiette, même placement, mêmes frais, même table — la rente se partage donc
dans le rapport exact des deux taux. Si vous ne versez pas ces
{taux_volontaire}, retranchez cette part du total du système 4, et gardez-la
sur votre fiche de paie : c'est le même argent, et c'est vous qui
choisissez.</p>"""

    return g.depliant(
        f"Le pilier capitalisé : {taux} placés dès "
        f"{parametres.annee_debut_capitalisation}",
        f"""
<p>À compter de {parametres.annee_debut_capitalisation}, {taux} de la
rémunération sont prélevés <strong>en plus</strong> de la cotisation de
répartition, et placés. Ils ne passent pas par le compte notionnel : ils
constituent un capital, au nom du cotisant, dans un plan d'épargne retraite —
l'enveloppe qui existe déjà. Deux choses seulement l'en distinguent : {taux_impose}
sont obligatoires, et l'argent n'en sort qu'à la retraite, sous forme
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
{partage_volontaire}
{rendement}
{echelle}
{transmission}
<p class="discret">Les taux employés sont ceux de la courbe des titres
souverains les mieux notés de la zone euro, relevée le
{escape(_date_en_clair(pilier.date_courbe))} et publiée par la Banque centrale
européenne ; les versements des années suivantes emploient les taux à terme
que cette même courbe implique. Les frais partent des moyennes 2025 du marché
des plans d'épargne retraite individuels, mesurées par l'Observatoire des
produits d'épargne financière, et baissent ensuite par paliers. La page <a href="{g.lien("/methode/")}">Méthode</a>
dit ce que ces choix supposent, et la page <a href="{g.lien("/donnees/")}">Données</a>
d'où ils viennent. Fiabilité de ce compartiment :
<span class="etiquette-fiabilite">{escape(g.fiabilite_en_clair(pilier.fiabilite))}</span>, le
barème de frais étant saisi, confronté au rapport à la main et non recontrôlé
automatiquement.</p>""",
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
        ["e) + rente du pilier capitalisé",
         f"les "
         f"{g.pourcentage(parametres.taux_capitalisation_applique, decimales=0)} "
         "capitalisés, volontaires compris : une allocation différentielle "
         "compte les ressources et non leur origine",
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
    ["", "texte", "nombre"],
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
    def depuis(cls, saisie: Saisie, base: Parametres,
               comparaison: Comparaison | None = None) -> "Montants":
        pensions = charger_prelevements(base.racine_donnees).pensions
        # Le rapport net/brut du salaire se lit sur la DERNIÈRE fiche de paie
        # de la carrière, celle de l'année du départ : c'est l'année dont le
        # revenu sert de dénominateur au taux de remplacement.
        rapport = 0.0
        remuneration = getattr(comparaison, "remuneration", None)
        if remuneration is not None:
            derniere = remuneration.annees[-1].droit_en_vigueur
            if derniere.brut > 0:
                rapport = derniere.net / derniere.brut
        return cls(net=saisie.en_net, taux_pension=pensions.taux_total,
                   rapport_net_brut_salaire=rapport)

    def pension(self, brut: float) -> float:
        """Une pension, une rente, une garantie : tout ce qui se sert après."""
        return brut * (1.0 - self.taux_pension) if self.net else brut

    def salaire(self, fiche) -> float:
        """Un salaire, lu sur la fiche de paie qui porte déjà les deux."""
        return fiche.net if self.net else fiche.brut

    def taux_remplacement(self, taux_brut: float) -> float:
        """Le taux de remplacement, dans la langue du mode.

        Le modèle le calcule brut sur brut : une pension brute rapportée au
        dernier revenu d'activité brut. Affiché à côté de montants NETS, il
        deviendrait le seul chiffre de la page à parler l'autre langue — et il
        mentirait dans un sens précis, car un même écart de brut se traduit par
        un écart de net PLUS GRAND : une pension est moins prélevée qu'un
        salaire, 9,1 % contre une vingtaine de points.

        Le taux net vaut donc le taux brut multiplié par le rapport des deux
        prélèvements. C'est un fait connu, et rarement montré : en France, le
        taux de remplacement net dépasse le taux brut de plusieurs points.
        """
        if not self.net or self.rapport_net_brut_salaire <= 0:
            return taux_brut
        return taux_brut * (1.0 - self.taux_pension) / self.rapport_net_brut_salaire

    #: Ce qu'un euro de salaire brut laisse en net, au DERNIER revenu
    #: d'activité — le dénominateur du taux de remplacement. Zéro quand le
    #: statut n'a pas de fiche de paie : le taux reste alors brut, faute de
    #: pouvoir le netter honnêtement.
    rapport_net_brut_salaire: float = 0.0

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


def _bascule_montants(saisie: Saisie, echelle: "Echelle") -> str:
    """Le lien qui passe de net à brut, et retour — montants déjà traduits.

    Un lien plutôt qu'un menu, pour la même raison que la bascule d'unité : il
    porte l'adresse entière, si bien que l'adresse se partage telle qu'on la
    lit, et cela ne demande pas une ligne de JavaScript.

    PAS D'ANCRE AU BOUT DE L'ADRESSE, et c'est un bogue payé. La bascule des
    résultats portait `#resultats`, pour revenir sur les chiffres plutôt qu'en
    haut du formulaire. Mais ici la ROUTE vit déjà dans le fragment : un second
    `#` ne fabrique pas une ancre, il allonge la dernière valeur de la requête.
    `montants=brut#resultats` n'est pas un mode connu, le modèle retombait sur
    son défaut, et la page revenait en net — avec le salaire converti en brut
    relu comme un net, donc une carrière mieux payée d'un quart. Le retour aux
    résultats est déjà assuré sans ancre : `reprendre()` y pose le focus et y
    fait défiler à chaque rendu.

    LES MONTANTS SAISIS SONT TRADUITS, et c'est tout l'enjeu : en mode net, le
    nombre du formulaire est un net. Le recopier tel quel dans l'autre mode le
    ferait relire comme un brut, et la page reviendrait en décrivant une AUTRE
    carrière — mieux payée d'un quart. Le lien porte donc le montant converti,
    métier par métier, exactement comme le fait la bascule d'unité.
    """
    vers_le_net = not saisie.en_net
    remplacements: dict[str, object] = {
        "montants": "net" if vers_le_net else "brut"}
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
    cible = f"#/simuler?{escape(saisie.requete(**remplacements))}"
    # L'état courant n'a pas d'adresse : c'est celle où l'on est déjà.
    branches = [("net", cible if vers_le_net else "#"),
                ("brut", "#" if vers_le_net else cible)]
    return g.bascule("Montants", branches, "net" if saisie.en_net else "brut")


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
    # LE CHIFFRE DU MILIEU EST LE NET PLEIN : ce que la proposition laisse
    # quand elle a prélevé ses 23 points, et rien d'autre. Les cinq points que
    # personne n'impose n'en sont pas retirés — une épargne qu'on décide seul
    # n'est pas une retenue sur salaire —, mais la rente du système 4 affichée
    # plus haut les suppose placés, et il faut le dire dans la même phrase :
    # sans elle, le lecteur croirait cette rente gratuite ; avec le net amputé,
    # il croirait la proposition plus coûteuse qu'elle n'est.
    volontaire = ""
    if remuneration.verse_le_volontaire:
        parametres = comparaison.parametres
        impose = (parametres.taux_retraite_propose
                  - parametres.taux_capitalisation_volontaire_applique)
        reste_apres = remuneration.reference.net_apres_volontaire / 12.0
        ecart_apres = remuneration.gain_net_mensuel_apres_volontaire
        volontaire = (
            f""" C'est votre {net} plein : le système 4 prélève
  {g.pourcentage(impose, decimales=0)} pour la retraite, et rien d'autre. La
  rente qu'il affiche plus haut suppose en plus que vous placez les
  <strong>{g.pourcentage(parametres.taux_capitalisation_volontaire_applique, decimales=0)}
  de capitalisation volontaire</strong> que la proposition vous rend — soit
  {g.euros_centimes(remuneration.epargne_volontaire_mensuelle)} par mois virés
  de votre {net} sur un compte à votre nom, pas une retenue —, pour cotiser
  {g.pourcentage(parametres.taux_retraite_propose, decimales=0)} en tout, comme
  aujourd'hui. Il vous reste alors {g.euros_centimes(reste_apres)} par mois,
  soit {_euros_signe(ecart_apres)} par rapport à aujourd'hui. Si vous ne les
  placez pas, vous gardez le {net} plein, et la rente du système 4 baisse de la
  part nommée « des cinq points volontaires »."""
        )
    # Trois hypothèses, et il faut dire laquelle vaut ici : le coût du travail
    # tenu fixe quand l'employeur verse des taux de droit commun, l'assiette
    # tenue fixe quand il n'y a pas d'employeur, le PARTAGE quand ce qu'il
    # verse est un taux d'équilibre.
    if remuneration.incidence is Incidence.PARTAGEE:
        sous_quelle_hypothese = (
            f"la moitié de ce que votre employeur cesse de verser revenant à "
            f"votre {escape(remuneration.libelle_assiette.lower())}")
    elif remuneration.affiche_cout_du_travail:
        sous_quelle_hypothese = "à coût du travail inchangé pour votre employeur"
    else:
        sous_quelle_hypothese = (
            f"à {escape(remuneration.libelle_assiette.lower())} inchangé")
    rendu = _salaire_net_rendu(remuneration, net)
    return f"""
<h2 id="salaire-net">Et pendant que vous cotisez</h2>
<p class="chapeau">Une réforme des retraites ne change pas que votre pension :
elle change ce qui est prélevé sur votre travail, donc ce que vous touchez
chaque mois. Les systèmes 1, 2 et 3 prélèvent la même chose — ils ne changent
que ce qui est porté au compte. Le système 4, lui, y touche.</p>
<div class="carte">
  <div class="fiches">{ouverture}</div>
  <p>Soit <strong>{_euros_signe(gain)} {sens} sur votre fiche de paie</strong>,
  {sous_quelle_hypothese}.{reste}{volontaire}</p>{rendu}
  {_salaire_net_detail(comparaison, remuneration, saisie)}
</div>"""


def _salaire_net_rendu(remuneration, net: str) -> str:
    """Ce que la proposition REND, et d'où l'argent vient.

    Deux mouvements, et ils n'ont pas la même cause. Il faut donc deux
    paragraphes, et surtout ne pas les fondre en un : le lecteur croirait
    qu'on lui rend ce qu'on lui prenait pour sa retraite, et ce serait faux
    dans les deux cas.

    LA CSG ALLÉGÉE. La proposition cesse d'affecter à la retraite les impôts
    et taxes qui la financent, et n'en garde rien : la moitié est rendue aux
    salaires, la moitié éteint de la dette. Ce qui, dans ces impôts, est assis
    sur une rémunération — la taxe sur les salaires et le forfait social — est
    supprimé ; le solde revient en points de CSG d'activité. Et la phrase qui
    ne doit pas manquer : cette CSG-là ne finance aujourd'hui aucune retraite.

    LE TRAITEMENT D'UN AGENT PUBLIC. Son employeur verse un taux d'ÉQUILIBRE,
    et la proposition le ramène à la part patronale du taux unique. La moitié
    de ce qu'il cesse de verser remonte dans le traitement, l'autre moitié paie
    la dette de pensions déjà promises — qui, elle, reste due.
    """
    morceaux = []
    if remuneration.csg_rendue > 0:
        morceaux.append(f"""
  <p><strong>Votre CSG baisse de
  {g.nombre(remuneration.csg_rendue * 100, 2)} point</strong>, et c'est compris
  dans le chiffre ci-dessus. La proposition cesse d'affecter à la retraite les
  impôts et taxes qui la financent ; elle n'en garde pas la moitié : celle-là
  est rendue aux salaires. Ce qui, dans ces impôts, sort déjà d'une
  rémunération — la taxe sur les salaires et le forfait social — est supprimé,
  et le reste vous revient en points de CSG. <strong>Cette CSG-là ne finance
  aujourd'hui aucune retraite</strong> : ses {g.pourcentage(0.092)} vont à la
  famille, à la maladie, à la dette sociale, au chômage et à l'autonomie, et
  rien à la vieillesse. Ce n'est donc pas une cotisation qu'on vous rend, c'est
  un impôt qu'on supprime. L'autre moitié éteint de la dette.</p>""")
    if (remuneration.incidence is Incidence.PARTAGEE
            and remuneration.contribution_equilibre > 0):
        morceaux.append(f"""
  <p><strong>Votre employeur verse aujourd'hui
  {g.pourcentage(remuneration.contribution_equilibre)} de votre
  {escape(remuneration.libelle_assiette.lower())}</strong> pour votre retraite.
  Ce n'est pas un prix du travail : c'est le taux qui équilibre le régime,
  c'est-à-dire qui paie les pensions d'aujourd'hui. La proposition le ramène à
  la part employeur du taux unique, et la moitié de ce qu'il cesse de verser
  revient à votre {escape(remuneration.libelle_assiette.lower())} — l'autre
  moitié paie la dette de pensions déjà promises, qui reste due. C'est pourquoi
  votre {net} monte de plus que ne le ferait une simple baisse de retenue.</p>""")
    return "".join(morceaux)


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
    ]
    # Le placement que l'assuré décide seul. Il est SOUS le net, et non dans
    # le prélèvement retraite : rien ne l'impose, la fiche ne le retient pas,
    # et le net écrit au-dessus est le net plein. La colonne « Systèmes 1 à 3 »
    # y porte un tiret — il n'existe pas sous le droit en vigueur —, et la
    # ligne suivante dit ce qui reste à qui le fait.
    if reference.epargne_volontaire > 0:
        lignes.append(
            ["Placé volontairement sur un compte à votre nom, les points rendus",
             "—", mois(reference.epargne_volontaire)])
        lignes.append(
            [f"{libelle_net} restant si vous les placez", mois(avant.net),
             mois(reference.net_apres_volontaire)])
    lignes += [
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
    volontaire = g.pourcentage(
        parametres.taux_capitalisation_volontaire_applique, decimales=0)
    repartition = g.pourcentage(parametres.taux_cotisation_liberal, decimales=0)
    total = g.pourcentage(parametres.taux_retraite_propose, decimales=0)
    ajout = ""
    if remuneration.verse_le_volontaire:
        ajout = (
            f" Les {volontaire} <strong>volontaires</strong> n'y sont pas : la "
            "fiche de paie ne les retient pas, personne ne les impose. Ce sont "
            "les points que la proposition vous rend, et que le site suppose "
            "placés sur le même compte, pris sur votre net — soit "
            f"{g.euros_centimes(remuneration.epargne_volontaire_mensuelle)} "
            f"par mois et {g.euros(remuneration.epargne_volontaire_cumulee)} "
            f"d'ici votre départ. Vous cotisez alors {total} en tout, "
            "c'est-à-dire ce que vous versez déjà aujourd'hui — c'est à ce "
            "prix-là que la rente du système 4 est calculée, et la part qui "
            "en vient est nommée à côté d'elle."
        )
    return (
        f'<p class="note resume"><strong>{g.euros_centimes(epargne)} par mois '
        "de ce prélèvement est de l'épargne à votre nom.</strong> Le système 4 "
        f"prélève {taux} par-dessus les {repartition} de répartition, et ces "
        "cinq points ne partent pas : ils alimentent un compte qui reste le "
        "vôtre, transmissible à vos héritiers tant qu'il n'est pas liquidé — "
        f"{g.euros(remuneration.epargne_cumulee)} d'ici votre départ, en euros "
        f"de {saisie.euros}.{ajout} "
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
de financement. Fiabilité : {escape(g.fiabilite_en_clair(remuneration.fiabilite))}. Les taux de
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
    volontaire = g.pourcentage(
        parametres.taux_capitalisation_volontaire_applique, decimales=0)
    # Les cinq points volontaires échappent au partage, et ce n'est pas un
    # détail d'écriture : personne ne cofinance une épargne que l'assuré décide
    # seul. Ils ne sont donc pas sur la fiche — le net affiché est le net plein
    # — et, placés, ils pèsent leur montant entier là où les points imposés
    # n'en coûtent que la moitié.
    hors_partage = ""
    if remuneration.verse_le_volontaire and remuneration.profil != "independant":
        hors_partage = f"""
<p><strong>Les {volontaire} volontaires, eux, ne sont sur la fiche de paie de
personne.</strong> Aucun employeur ne cofinance une épargne que son salarié
décide seul : le site les compte comme un placement pris sur votre net, porté
en entier par vous, et ni le coût du travail, ni le brut, ni le net ne bougent
quand vous le faites. C'est pourquoi, si vous les placez, ils pèsent leur
montant entier, quand les {capitalise} imposés ne vous en coûtent que la
moitié.</p>"""
    if remuneration.profil == "independant":
        return f"""<p><strong>Les {repartition} et les {capitalise} capitalisés sont à votre
charge en entier.</strong> La proposition les annonce « salariale et patronale
additionnées » ; vous êtes les deux à la fois, comme vous l'êtes déjà des
vingt-six points que vous versez aujourd'hui. Vous prêter un employeur pour la
moitié de la charge fabriquerait un gain qui n'existe pas. Les {volontaire}
volontaires, eux, ne sont pas sur la fiche : c'est un placement pris sur votre
revenu net, à votre charge en entier, et pour une autre raison — personne ne
cofinance une épargne qu'on décide seul. Votre profil est le seul où les trois
taux pèsent de la même façon.</p>"""
    total = parametres.taux_cotisation_liberal + parametres.taux_capitalisation_obligatoire
    votre_part = g.pourcentage(total * part, decimales=2)
    part_employeur = g.pourcentage(total * (1.0 - part), decimales=2)
    if not remuneration.affiche_cout_du_travail:
        return f"""<p><strong>Votre part des {repartition} et des {capitalise} capitalisés
est de {votre_part} au total</strong>, contre {part_employeur} pour votre
employeur. La proposition dit « salariale et patronale additionnées » sans dire
qui porte quoi ; le choix est de laisser la part patronale où elle est
aujourd'hui et de faire porter toute la baisse par la vôtre. C'est ce partage
qui commande le chiffre ci-dessus, puisque seule votre part y figure.</p>{hors_partage}"""
    return f"""<p><strong>Sur les {repartition} et les {capitalise} capitalisés, vous
portez {votre_part} et votre employeur {part_employeur}.</strong> La proposition
dit « salariale et patronale additionnées » sans dire qui porte quoi, et le
choix n'est pas neutre : la CSG est assise sur le brut, et l'allègement sur les
bas salaires ne porte que sur la part patronale. Celui-ci laisse à votre
employeur les 16,67 points qu'il verse aujourd'hui et ramène votre retenue de
11,31 à 6,33. Deux raisons, et la première est la plus importante : la baisse
arrive <strong>tout de suite</strong>, sans qu'il faille attendre qu'un
employeur rende son économie ; et elle ne fuit pas, parce que votre brut ne
bouge pas et que ni la CSG ni les autres cotisations ne grossissent avec lui.
Le partage inverse ferait monter votre brut de près de 3 %, donc aussi ce qui
est porté à votre compte, mais des années plus tard et amputé du quart.</p>{hors_partage}"""


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
        ["", "nombre", "texte"],
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


def _reglage_proposition(solde) -> dict:
    """Le coefficient d'équilibre de la proposition, sur les années projetées.

    Les pages Cas types et Coût le lisaient dans une phrase FIXE, écrite un
    soir où il dépassait un sur tout l'horizon ; le modèle de coût a changé le
    lendemain matin, et la phrase est restée : Cas types promettait une marge
    que le tableau de Coût, trois onglets plus loin, chiffrait en manque. Les
    deux pages composent désormais leur lecture à partir de ces nombres, et un
    test vérifie qu'elles disent ce que le solde dit.
    """
    debut, fin = solde.premiere_annee_projetee, solde.derniere_annee
    annees = [(annee, solde.annee(annee).coefficient("notionnel_liberal"))
              for annee in range(debut, fin + 1)]
    annee_minimum, minimum = min(annees, key=lambda couple: couple[1])
    return {
        "debut": debut, "fin": fin,
        "premier": annees[0][1], "dernier": annees[-1][1],
        "minimum": minimum, "annee_minimum": annee_minimum,
        "sous_un": sum(1 for _, coefficient in annees if coefficient < 1.0),
        "total": len(annees),
    }


def _lecture_reglage_proposition(reglage: dict) -> str:
    """La phrase de Cas types : de quel côté de un, et de combien."""
    r = reglage
    if r["sous_un"] == 0:
        return (
            "Pour la proposition, ce facteur est supérieur à un sur chacune "
            f"des années projetées, de {r['debut']} à {r['fin']} : à "
            "prélèvement égal, le système aurait de quoi servir davantage que "
            "ces cases n'affichent. <strong>Un coefficient supérieur à un est "
            "une marge</strong>, de quoi relever toutes les cases d'autant."
        )
    if r["sous_un"] == r["total"]:
        return (
            "Pour la proposition, ce facteur est inférieur à un de "
            f"{r['debut']} à {r['fin']} : {g.nombre(r['minimum'], 2)} au plus "
            f"bas en {r['annee_minimum']}, {g.nombre(r['dernier'], 2)} en "
            f"{r['fin']}. Appliqué, il aurait abaissé les cases d'autant, "
            f"jusqu'à {g.pourcentage(1 - r['minimum'], decimales=0)} en "
            f"{r['annee_minimum']}. <strong>Un coefficient inférieur à un est "
            "un manque</strong>, le coût de la transition au taux unique."
        )
    return (
        f"Pour la proposition, ce facteur est inférieur à un {r['sous_un']} "
        f"années sur {r['total']} entre {r['debut']} et {r['fin']}, au plus "
        f"bas {g.nombre(r['minimum'], 2)} en {r['annee_minimum']}, et "
        "supérieur à un les autres. Au-dessus de un, le système aurait de quoi "
        "relever toutes les cases d'autant ; au-dessous, il aurait fallu les "
        "abaisser, ou financer la différence autrement."
    )


def _note_lecture_coefficient(reglage: dict) -> str:
    """La note de Coût : le coefficient se lit dans les deux sens, jamais en économie."""
    r = reglage
    dernier = g.nombre(r["dernier"], 2)
    if r["dernier"] >= 1.0:
        lecture = (f"Les {dernier} de la proposition en {r['fin']} disent une "
                   f"marge de {g.pourcentage(r['dernier'] - 1, decimales=0)}")
    else:
        lecture = (f"Les {dernier} de la proposition en {r['fin']} disent un "
                   f"manque de {g.pourcentage(1 - r['dernier'], decimales=0)}")
    if r["sous_un"] == r["total"]:
        lecture += (f", et son plus bas, {g.nombre(r['minimum'], 2)} en "
                    f"{r['annee_minimum']}, un manque de "
                    f"{g.pourcentage(1 - r['minimum'], decimales=0)} : le coût "
                    "de transition du taux unique.")
    elif r["minimum"] < 1.0:
        lecture += (f", et son plus bas, {g.nombre(r['minimum'], 2)} en "
                    f"{r['annee_minimum']}, un manque de "
                    f"{g.pourcentage(1 - r['minimum'], decimales=0)}.")
    else:
        lecture += "."
    return f"""<div class="note"><strong>Le coefficient se lit dans les deux sens,
jamais comme une économie.</strong> Au-dessus de un, une marge, et une marge se
sert : à ces recettes-là, le système servirait davantage que ce que la colonne
« dépense » lui prête, autrement réparti entre les carrières. Au-dessous de un,
un manque : il faudrait abaisser toutes les pensions d'autant, ou financer la
différence autrement. {lecture} Le modèle calcule ce facteur ; il ne l'applique
jamais, et toutes les courbes de coût de cette page sont celles d'un système
qui ne se pilote pas. L'appliquer changerait toutes les pensions par un même
facteur, donc tous les niveaux de cette page, sans toucher aux écarts entre carrières,
qui sont la seule chose que ce site mesure.</div>"""


def _deplacement_des_ecarts(resultat, solde, scenario: str) -> tuple[float, int]:
    """De combien les écarts de la grille bougeraient si chaque système était
    ramené à SON équilibre — déplacement médian en points, et cases mesurées.

    LA PHRASE QUE CETTE FONCTION A FALLU ÉCRIRE POUR RÉPARER. La page Cas
    types disait que le coefficient d'équilibre « multiplierait les cases par
    le même facteur », et le catalogue des affirmations la tenait pour
    vérifiée sous un contrôle qui vérifiait tout autre chose — que le
    coefficient n'est pas appliqué. Or la phrase est fausse deux fois. Un même
    facteur appliqué à tous les systèmes laisserait ces cases INCHANGÉES,
    puisqu'une case est déjà un rapport de deux pensions et qu'un facteur
    commun se simplifie. Et il n'y a pas un facteur mais quatre : chaque
    système a son coefficient, et les ramener chacun à son équilibre déplace
    les écarts du RAPPORT de ces coefficients.

    Mesuré plutôt qu'argumenté, donc, et la page écrit le nombre.

    LA MÉDIANE, ET NON LA MOYENNE : le déplacement est énorme sur les
    générations déjà liquidées, où la proposition encaisse deux à trois fois ce
    qu'elle verse parce qu'elle ne verse presque rien, et une moyenne n'y
    dirait que ces cas-là. Médiane basse — l'élément de rang ``n // 2`` — pour
    que le portage JavaScript retrouve le même nombre sans convention de
    départage.
    """
    deplacements = []
    for cas in CAS_TYPES:
        for generation in GENERATIONS:
            comparaison = resultat.resultats.get((cas.code, generation))
            if comparaison is None:
                continue
            ligne = solde.annee(comparaison.carriere.annee_liquidation)
            if ligne is None:
                continue
            reference = ligne.coefficient("actuel")
            if reference <= 0.0:
                continue
            ecart = comparaison.variation_totale(scenario)
            equilibre = (1.0 + ecart) * ligne.coefficient(scenario) / reference - 1.0
            deplacements.append(abs(equilibre - ecart))
    if not deplacements:
        return 0.0, 0
    deplacements.sort()
    return deplacements[len(deplacements) // 2], len(deplacements)


def _cas_types(contexte: Contexte, regards: dict[str, str] | None = None) -> str:
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
    # dans les comptes, et ne coûte rien. Le coût agrégé, lui, coûte deux
    # secondes une fois, et la page le demande pour une seule phrase : celle
    # qui dit de quel côté de un se trouve le réglage de la proposition. Elle
    # était fixe, et fausse ; elle est calculée, et la page Coût la retrouve.
    comptes = contexte.comptes()
    obs = comptes.derniere_annee_observee
    horizon = comptes.derniere_annee
    solde = contexte.cout().solde
    reglage = _reglage_proposition(solde)
    # Ce que la grille ne mesure pas, chiffré plutôt qu'affirmé : de combien
    # ses écarts bougeraient si chaque système était ramené à son équilibre.
    deplacement, cases = _deplacement_des_ecarts(resultat, solde, montre)
    bulle_ecarts = g.bulle(
        "Ce qu'un coefficient appliqué déplacerait",
        f"""Un facteur commun laisserait ces cases inchangées, une case
étant déjà un rapport de deux pensions. Mais il y a quatre coefficients, un par
système : les ramener chacun à SON équilibre déplacerait les écarts, de {g.nombre(deplacement * 100, 0)}
points en médiane sur les {cases} cases de cette grille, et bien plus sur les
générations déjà liquidées, où la proposition encaisse plusieurs fois ce
qu'elle verse. Le simulateur montre, carrière par carrière, ce que les recettes
de chaque système paient de la pension qu'il promet.""")

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
mais n'applique jamais — et <strong>chaque système a le sien</strong>.\
{bulle_ecarts}
{_lecture_reglage_proposition(reglage)}
<a href="{g.lien("/cout")}" data-vers="cout-equilibre">La page Coût le
chiffre</a>.</div>

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


def _cout(contexte: Contexte, regards: dict[str, str] | None = None) -> str:
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
      traverser pour atteindre le résultat. Les cascades de
      ``_cout_detail_cascade`` sont de celles-là : elles font le pont du
      système actuel à la proposition, mesure par mesure, et ce pont est ce
      qu'on vient chercher APRÈS avoir lu le résultat, jamais avant.
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
    # site ne compare plus. Elle ne commence qu'à la bascule — non parce
    # qu'elle ne changerait rien avant, elle est rétroactive et change tout,
    # mais parce que c'est de là que la décision se prend. Ce qu'elle aurait
    # coûté sur le passé est dans les tableaux du dépliant, à sa place : celle
    # d'un contrefactuel. Pas à l'année observée non plus : l'année d'avant la
    # bascule, la proposition n'est pas encore appliquée, son point est celui
    # du système actuel, et la courbe faisait un à-pic qui ne mesurait rien.
    reforme = "notionnel_liberal"
    depart_reforme = max(obs, bascule)
    apres = {ligne.annee: ligne.depense(reforme) * 100
             for ligne in solde.annees if ligne.annee >= depart_reforme}
    # Et ce qu'elle encaisserait : 18 % sur les revenus d'activité, sans la
    # contribution d'équilibre de l'État ni ce que la CNAF et l'Unédic versent
    # pour des droits qu'elle ne sert plus. Deux courbes pour la proposition
    # comme pour le système actuel, sinon on ne voit qu'une moitié de son
    # compte : ce qu'elle coûte, jamais ce qu'elle rapporte.
    encaisse = {ligne.annee: ligne.ressources_de(reforme) * 100
                for ligne in solde.annees if ligne.annee >= depart_reforme}
    taux_liberal = contexte.simulateur().parametres.taux_cotisation_liberal

    # L'ordre est celui de la lecture, de gauche à droite : la légende se
    # parcourt alors dans l'ordre où l'œil rencontre les courbes.
    courbes = (
        _serie(f"Avant {solde.premiere_annee}", "var(--serie-1)", avant,
               glose="autre source, périmètre un peu plus large"),
        _serie("Ce qui sort : les pensions versées", "var(--serie-2)", sortie),
        _serie("Ce qui rentre : cotisations et impôts", "var(--serie-5)", entree),
        # La glose porte ce que la courbe NE porte PAS : la garantie
        # vieillesse est financée par l'impôt, hors du compte des cotisants,
        # et elle est donc absente des deux courbes jaunes comme elle est
        # absente du solde. Un demi-point de PIB que le lecteur doit savoir
        # ajouter — le dépliant des systèmes le chiffre et la cascade l'ajoute.
        _serie(f"Ce que coûterait notre proposition, dès {bascule}",
               "var(--liberal)", apres, tirets=True,
               glose="hors garantie vieillesse"),
        _serie("Ce qu'elle encaisserait", "var(--liberal)", encaisse,
               glose=f"{g.pourcentage(taux_liberal, decimales=0)} sur les "
               "revenus d'activité, sans la contribution de l'État"),
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

    # -- ce que personne n'a cotisé -----------------------------------------
    #
    # UN CHIFFRE, ET SON DÉNOMINATEUR AVEC LUI. La part des avantages non
    # contributifs se lit sur le risque vieillesse-survie des comptes de la
    # protection sociale, à la dernière année que la DREES publie ; les trois
    # chiffres d'ouverture sont ceux du COR, à une autre année, sur un compte
    # plus étroit. Poser 22 % sous « versé aux retraités » ferait un chiffre
    # faux sans qu'une ligne de code soit fautive. La phrase porte donc son
    # propre total, et dit qu'il n'est pas celui des cartes. Le détail par
    # famille est dans le dépliant des dépenses, sur ce même total, et le
    # dispositif par dispositif sur la page Avantages, où chaque case vide dit
    # pourquoi.
    avantages = contexte.avantages().derniere
    non_cotise = ""
    if avantages is not None and avantages.observee > 0:
        non_cotise = f"""
<div class="note"><strong>Ce que personne n'a cotisé.</strong> Réversion,
minima, trimestres pour enfants : {_milliards(avantages.gratuit, 1)} en
{avantages.annee}, soit
{g.pourcentage(avantages.gratuit / avantages.observee, decimales=1)} de la
dépense vieillesse-survie ({_milliards(avantages.observee, 1)}, un périmètre
plus large que les cartes).
<a href="{g.lien("/avantages")}">La page Avantages</a> les détaille.</div>
"""

    # Le détail est rendu AVANT le gabarit final : c'est de lui, et des deux
    # cartes, que le plan de la page se déduit.
    detail = "".join([
        _cout_detail_depense(contexte),
        _cout_detail_ressources(contexte),
        _cout_detail_transferts(contexte),
        _cout_detail_scenarios(contexte),
        _cout_detail_cascade(contexte, regards),
        _cout_detail_equilibre(contexte),
        _cout_detail_postes(contexte),
        _cout_detail_dette(contexte),
        _cout_detail_frise(contexte),
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
{non_cotise}
<div class="note"><strong>Dépenser moins n'est pas économiser.</strong> Un
système en {g.terme("comptes notionnels", "compte notionnel")} ne laisse pas d'argent
dormir : il remonte les pensions jusqu'à l'équilibre. La courbe en pointillés
ne dit donc pas « on dépenserait moins ». Elle dit : <em>avec le même argent,
on servirait autant, mais réparti autrement entre les carrières</em>. La
courbe jaune pleine dit ce qu'elle encaisserait, et l'écart des deux jaunes
est son solde, hors garantie vieillesse.</div>

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


def _avantages(contexte: Contexte, regards: dict[str, str] | None = None) -> str:
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
    plus de quarante : elle doit pouvoir les nommer.
    """
    inventaire = contexte.inventaire_avantages()
    cout = contexte.avantages()
    derniere = cout.derniere
    # CE QUE LA PAGE ANNONCE EST CE QUE SON TABLEAU MONTRE. `inventaire.chiffres`
    # compte les dispositifs que le modèle SAIT chiffrer, ce qui n'est pas la
    # même chose que ceux qui PORTENT un chiffre : un avantage éteint, ou que
    # nul cas type ne porte, se mesure très bien et vaut zéro. Annoncer les
    # premiers au-dessus d'un tableau qui montre les seconds, c'était promettre
    # vingt-deux cases pleines et en donner quinze.
    total = len(inventaire.avantages)
    chiffres = sum(
        1 for avantage in inventaire.avantages
        if cout.derniere
        and cout.derniere.lignes.get(avantage.ligne_cascade or avantage.code)
    )
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
    # LA FENÊTRE EST CELLE OÙ TOUTES LES LIGNES SONT PUBLIÉES, et elle se
    # calcule au lieu de s'écrire. Les lignes que le modèle REFAIT existent dès
    # qu'il sert une pension, en 1959 ; celles qu'il LIT commencent le jour où
    # leur producteur les publie, et pas avant — 2004 pour la réversion, 2020
    # pour les sous-postes des comptes de la protection sociale. Empiler les
    # unes sur les autres hors de leur fenêtre commune dessinerait une falaise
    # de quarante milliards en 2020, et le lecteur y verrait une explosion de
    # la dépense là où il n'y a qu'un début de publication.
    #
    # La fenêtre est donc courte, cinq points, et c'est le prix de l'honnêteté :
    # elle a été calculée sur la seule réversion tant que celle-ci était la
    # seule ligne lue, et elle s'est resserrée d'elle-même le jour où huit
    # postes publiés l'ont rejointe. L'HISTOIRE LONGUE N'EST PAS PERDUE : le
    # premier graphique de la page compte les dispositifs depuis 1800, et la
    # commande d'analyse du dépôt imprime les lignes calculées depuis 1959 —
    # un minimum vieillesse qui pesait le tiers de la dépense en 1960 et qui
    # s'est éteint depuis.
    annees_cout = tuple(ligne.annee for ligne in cout.annees)
    lues = frozenset(LIGNES_LUES) & frozenset(cout.lignes)
    annees_publiees = tuple(
        ligne.annee for ligne in cout.annees if lues <= frozenset(ligne.lignes)
    )
    fenetre = tuple(
        ligne for ligne in cout.annees if ligne.annee in set(annees_publiees)
    )
    # LE TRACÉ EMPILE LES FAMILLES, PAS LES LIGNES. Quinze lignes pour neuf
    # couleurs, c'est six bandes qui portent la couleur d'une autre : une
    # légende qu'on ne peut pas suivre, et les six plus petites tiennent de
    # toute façon dans l'épaisseur du trait. Les familles sont le découpage que
    # l'inventaire porte lui-même, et celui des tableaux qui suivent ; elles
    # sont sept, la palette en a neuf, et le détail ligne à ligne est juste en
    # dessous. Une ligne sans famille — il ne devrait pas y en avoir — serait
    # tue plutôt que rangée au hasard.
    par_famille: dict[str, dict[int, float]] = {}
    for ligne in cout.lignes:
        famille = inventaire.famille_de_ligne(ligne)
        if famille is None:
            continue
        cumul = par_famille.setdefault(famille, {})
        for annee in fenetre:
            cumul[annee.annee] = (cumul.get(annee.annee, 0.0)
                                  + annee.lignes.get(ligne, 0.0))
    ordonnees = sorted(
        (f for f in inventaire.familles if any(par_famille.get(f.code, {}).values())),
        key=lambda f: -par_famille[f.code].get(derniere.annee, 0.0),
    )
    couts = tuple(
        g.Serie(
            famille.libelle,
            tuple(par_famille[famille.code].get(annee.annee, 0.0) / 1000
                  for annee in fenetre),
            COULEURS_LIGNES[rang % len(COULEURS_LIGNES)],
        )
        for rang, famille in enumerate(reversed(ordonnees))
    )
    reversion = derniere.lignes.get("reversion", 0.0)
    courbe_cout = g.graphique(
        f"Coût des avantages non contributifs que l'on sait chiffrer, par "
        f"famille, de {annees_publiees[0]} à {annees_publiees[-1]}",
        annees_publiees, couts, unite="Md€ courants", empile=True,
        decimales_donnees=1,
    ) if annees_publiees else ""

    # -- graphique long : le modèle seul, sur toute sa longueur --------------
    #
    # LE TRACÉ PRÉCÉDENT EST JUSTE MAIS COURT, celui-ci est long mais étroit,
    # et aucun des deux ne peut être les deux à la fois. Les postes publiés
    # donnent le bon NIVEAU sur cinq ans ; le modèle donne la bonne FORME sur
    # soixante-six, parce qu'il calcule la même chose de la même façon depuis
    # la première pension servie. Les mêler dans une seule ligne, c'était le
    # défaut que le minimum vieillesse portait : 0,02 milliard en 2019 par le
    # modèle, 4,01 en 2020 par les comptes.
    #
    # Les deux séries ne s'additionnent donc jamais et ne se comparent pas
    # terme à terme : `modele` porte les lignes calculées, `lignes` le meilleur
    # chiffre disponible. La carte le dit en toutes lettres, parce qu'un
    # lecteur qui verrait 3,1 % ici et 22,1 % au-dessus conclurait que les
    # avantages ont fondu, quand c'est le champ de la mesure qui change.
    annees_modele = tuple(a.annee for a in cout.annees)
    familles_modele: dict[str, dict[int, float]] = {}
    for ligne in cout.lignes_modele:
        famille = inventaire.famille_de_ligne(ligne)
        if famille is None:
            continue
        cumul = familles_modele.setdefault(famille, {})
        for a in cout.annees:
            cumul[a.annee] = cumul.get(a.annee, 0.0) + a.modele.get(ligne, 0.0)
    ordre_modele = sorted(
        (f for f in inventaire.familles if any(familles_modele.get(f.code, {}).values())),
        key=lambda f: -familles_modele[f.code].get(annees_modele[-1], 0.0),
    )
    bandes_modele = tuple(
        g.Serie(
            famille.libelle,
            tuple(familles_modele[famille.code].get(a, 0.0) / 1000
                  for a in annees_modele),
            COULEURS_LIGNES[rang % len(COULEURS_LIGNES)],
        )
        for rang, famille in enumerate(reversed(ordre_modele))
    )
    courbe_longue = g.graphique(
        f"Ce que le modèle reconstitue seul, par famille, de "
        f"{annees_modele[0]} à {annees_modele[-1]}",
        annees_modele, bandes_modele, unite="Md€ courants", empile=True,
        decimales_donnees=1,
    ) if annees_modele else ""
    part_debut_modele = (cout.annees[0].gratuit_modele / cout.annees[0].observee
                         if cout.annees[0].observee else 0.0)
    pic_modele = max(cout.annees, key=lambda a: (a.gratuit_modele / a.observee
                                                 if a.observee else 0.0))
    part_fin_modele = (derniere.gratuit_modele / derniere.observee
                       if derniere.observee else 0.0)

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
<strong>réversion</strong>. Le COR chiffre les droits de solidarité à « de
l'ordre d'un cinquième » des retraites : on y est. {chiffres} des {total}
dispositifs portent un chiffre ; le tableau ci-dessous nomme les autres et dit
ce qui manque à chacun.""",
        courbe_cout
        + "<h3>Et sur soixante-six ans ?</h3>"
        + f"""<p class="chapeau">Le tracé ci-dessus est juste mais court : les
comptes ne détaillent leurs postes que depuis {annees_publiees[0]}. Celui-ci est
long mais étroit. Il porte les {len(ordre_modele)} familles que le modèle
reconstitue seul, de {annees_modele[0]} à {annees_modele[-1]}, calculées de la
même façon d'un bout à l'autre.</p>
<p><strong>Les deux ne s'additionnent pas et ne se comparent pas :</strong>
{g.pourcentage(part_fin_modele, decimales=1)} de la dépense ici,
{g.pourcentage(derniere.gratuit / derniere.observee, decimales=1)} au-dessus.
C'est le champ de la mesure qui change, et ce tracé donne une forme.</p>"""
        + courbe_longue
        + "<h3>Tous les dispositifs, un par un</h3>"
        + f"""<p class="chapeau">Ce que chacun coûte en {derniere.annee}, et,
quand la case est vide, pourquoi elle l'est. La dernière famille ne s'additionne
pas aux autres : elle n'est pas faite de dispositifs.</p>"""
        + _avantages_table_complete(contexte)
        + g.depliant(
            "Pourquoi ce chiffre est un plancher, et de combien",
            f"""<p>Trois choses à savoir avant de citer ce chiffre.</p>
<p><strong>Les plus grosses lignes sont lues, pas calculées.</strong> La
réversion, le minimum vieillesse, la majoration pour enfants, les pensions
d'orphelin, celles servies pour inaptitude ou invalidité : leur montant vient
des comptes de la protection sociale et de l'enquête annuelle de la DREES
auprès des caisses, poste par poste. Ce sont des comptes de personnes réelles,
et ce sont les chiffres les plus sûrs de la page. Le tableau ci-dessus le dit
case par case.</p>
<p><strong>Là où les deux existaient, le poste publié a remplacé la ligne
calculée</strong>, et l'écart entre les deux était énorme. Un seul des treize
cas types de la grille a des enfants (deux, quand le seuil de la majoration
est à trois), et le modèle chiffrait donc à zéro un avantage qui pèse
7,8 milliards. Une grille de cas types sert à <em>comparer</em> des systèmes
sur une même carrière, où les erreurs de niveau s'annulent au dénominateur ; le
coût d'un avantage est un compte de <em>population</em>, et il se lit chez celui
qui compte.</p>
<p><strong>La fenêtre est courte parce que les postes publiés le sont.</strong>
Les lignes calculées remontent à 1959 et la réversion à 2004, mais les
sous-postes des comptes ne sont publiés que depuis 2020 : le tracé s'arrête là
où <em>chaque</em> terme est observé. Les empiler plus tôt dessinerait une
falaise de quarante milliards, qui ne serait qu'un début de publication. Le
premier graphique de la page, lui, remonte à 1800.</p>
<p><strong>Et la forme longue parle.</strong> Le minimum vieillesse faisait
{g.pourcentage(part_debut_modele, decimales=0)} de la dépense en
{cout.annees[0].annee}, quand il y avait peu de pensions et beaucoup de
vieillards sans droits ; il s'est éteint à mesure que les carrières se
complétaient. La courbe remonte ensuite, à partir des années 1980 : les minima
de pension et les périodes assimilées rattrapent des carrières incomplètes là
où l'on secourait des carrières absentes.</p>
<p><strong>Et ce total reste un plancher.</strong> Les bonifications de service
des militaires et des corps actifs, les départs anticipés pour handicap, la
majoration de durée au titre du congé parental ne sont ni calculés par le
modèle ni isolés par les comptes. Le tableau ci-dessus les nomme et dit, pour
chacun, ce qui manque.</p></p>""",
        ),
        """Sources : pour les lignes lues, les comptes de la protection
sociale de la DREES, sous-postes du risque vieillesse-survie, et son enquête
annuelle auprès des caisses de retraite ; pour les lignes calculées,
décomposition du scénario 1 sur la grille de carrières types, rapportée à la
dépense observée, dont seule la part est modélisée. Toutes certifiées, année
par année.""",
        identifiant="avantages-cout",
    )

    part_classement = (derniere.anticipees.get("classement", 0.0)
                       / derniere.anticipee if derniere.anticipee > 0 else 0.0)
    # Ce que les mêmes dispositifs ajoutent au MONTANT des pensions : les
    # lignes d'âge que le modèle calcule — la catégorie active ; la carrière
    # longue et les âges des régimes spéciaux ne se mesurent que par la durée.
    # Le rapport était écrit « treize fois » ; il a valu quinze, puis
    # vingt-sept, sans que la phrase bouge. Il est compté, et le catalogue des
    # affirmations du site le tient.
    montant_age = sum(
        derniere.lignes.get(ligne, 0.0) for ligne in cout.lignes_modele
        if inventaire.famille_de_ligne(ligne) == "age_et_bonifications"
    )
    rapport_age = (
        f", soit {g.nombre(derniere.anticipee / montant_age, 0)} fois ce que "
        "les mêmes dispositifs ajoutent au <em>montant</em> des pensions"
        if montant_age > 0 else ""
    )
    carte_age = g.cle(
        "Et partir plus tôt, combien cela coûte-t-il ?",
        f"""<strong>{_milliards(derniere.anticipee, 1)} de pensions servies avant
l'âge légal en {derniere.annee}</strong>{rapport_age}. Une annuité versée avant
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
<p class="chapeau">Les mêmes dispositifs, avec leurs textes et leurs dates.</p>

{detail}
"""


#: Ce qu'une page REGARDE, page par page — à distinguer des RÉGLAGES, qui
#: disent sous quelles règles le modèle tourne et voyagent vers toutes les
#: pages. Un regard ne change aucun chiffre : il choisit lequel on montre, il
#: ne vaut que pour sa page, et une adresse qui en porte un pour une autre page
#: est ignorée plutôt que subie.
#:
#: ``cascade`` est l'année que la cascade de la page Coût décompose. Il est
#: écrit ici, et non dans ``Saisie`` : une année de lecture n'est pas une règle
#: de calcul, et la mettre parmi les réglages l'aurait fait voyager vers Cas
#: types et Avantages, qui n'ont rien à en faire.
_VUES_DE_PAGE: dict[str, tuple[str, ...]] = {
    "/cout": ("cascade",),
}

#: Les trois pages qui AGRÈGENT : elles ne calculent aucune carrière saisie,
#: mais elles obéissent aux mêmes règles que le simulateur. La table est posée
#: ici, après les trois fonctions, et lue par ``rendre`` — voir ``_agregee``.
PAGES_AGREGEES = {
    "/cas-types": _cas_types,
    "/cout": _cout,
    "/avantages": _avantages,
}


def _avantages_table_complete(contexte: Contexte) -> str:
    """Chaque dispositif sur sa ligne, avec son coût ou la raison qui l'en prive.

    C'EST LE CŒUR DE LA PAGE, et il a longtemps manqué. Les graphiques ne
    portent que ce qui se chiffre ; une page qui affirme qu'il existe
    quarante-deux avantages doit les NOMMER tous, et dire pour chacun ce qu'on en
    sait. Un blanc sans raison est une dette ; une raison écrite est une limite.

    Trois colonnes, et pas une de plus : le dispositif, ce qu'il coûte la
    dernière année publiée, et — quand la case est vide — pourquoi elle l'est.
    Les familles séparent les lignes, parce qu'un avantage d'âge et un minimum
    de pension ne se comparent pas.

    LES MONTANTS NE VIENNENT PAS TOUS DU MÊME ENDROIT, et chaque case le dit :
    un montant LU dans une publication et un montant REFAIT par le modèle ne se
    lisent pas avec la même confiance. Le premier compte des personnes réelles,
    le second treize carrières types.
    """
    inventaire = contexte.inventaire_avantages()
    cout = contexte.avantages()
    derniere = cout.derniere
    montants = derniere.lignes if derniere else {}

    # DEUX DISPOSITIFS PEUVENT PARTAGER UNE LIGNE, et le montant ne doit alors
    # paraître qu'une fois. La MDA du privé et la bonification pour enfants de
    # la fonction publique sont le même trimestre gratuit sous deux textes : la
    # cascade n'en tient qu'une ligne, et l'imprimer deux fois inviterait à
    # l'additionner. Le premier dispositif porte le chiffre, le second dit où
    # il est.
    vues: set[str] = set()

    blocs = []
    for famille in inventaire.familles:
        lignes = []
        for avantage in inventaire.par_famille(famille.code):
            ligne = avantage.ligne_cascade or avantage.code
            montant = montants.get(ligne)
            if montant and ligne in vues:
                porteur = next(a.libelle for a in inventaire.avantages
                               if (a.ligne_cascade or a.code) == ligne)
                lignes.append([
                    avantage.libelle, "—",
                    "le modèle n'en tient qu'une seule ligne, celle de "
                    "« " + escape(porteur) + " » : le chiffre ci-dessus les "
                    "porte toutes les deux",
                ])
            elif montant:
                vues.add(ligne)
                origine = "lu" if ligne in LIGNES_LUES else "calculé"
                lignes.append([
                    avantage.libelle,
                    _milliards(montant, 2),
                    f'<span class="discret">{origine}</span>',
                ])
            else:
                lignes.append([avantage.libelle, "—", escape(avantage.sans_chiffre)])
        if not lignes:
            continue
        blocs.append(
            '<div class="dispositifs">'
            f"<h4>{escape(famille.libelle)}</h4>"
            + g.tableau(
                ["Dispositif", f"Coût en {derniere.annee}",
                 "D'où vient le chiffre, ou pourquoi il manque"],
                lignes, ["", "nombre", "texte"],
                titre=f"{famille.libelle} : {len(lignes)} dispositifs et leur coût",
                entete_de_ligne=True,
            )
            + "</div>"
        )
    return "".join(blocs)


def _avantages_detail_liste(contexte: Contexte) -> str:
    """L'inventaire entier, famille par famille, avec sa base légale."""
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
                        ["", "texte", "nombre", "texte", "texte"],
                        titre=f"{famille.libelle} : {len(lignes)} dispositifs",
                        entete_de_ligne=True)
        )
    return g.depliant(
        f"Les {len(inventaire.avantages)} dispositifs, avec leur base légale et leurs dates",
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
                  ["", "nombre", "texte"],
                  titre="Ce que le modèle sait de chaque avantage",
                  entete_de_ligne=True) + note,
        identifiant="avantages-etats",
    )


def _avantages_detail_limites(contexte: Contexte) -> str:
    """Les trois réserves de la page, et pourquoi elles y sont.

    LE COMPTE DES LIGNES « À CERTIFIER » SE CALCULE, et il l'a appris à ses
    dépens : il était écrit en toutes lettres, et la phrase qui le portait
    donnait une raison — « leurs textes sont éclatés dans des statuts de corps »
    — qui n'a cessé d'être vraie que pour la moitié d'entre elles le jour où le
    texte de la police a été lu. Un compte écrit en prose se périme ; une raison
    écrite en prose se périme plus discrètement encore.
    """
    a_certifier = sum(
        1 for avantage in contexte.inventaire_avantages().avantages
        if any("certifier" in texte for texte in avantage.base_legale)
    )
    # ZÉRO EST UN RÉSULTAT, et il demande une autre phrase. Le compte a valu
    # deux pendant tout le chantier, puis un, puis zéro le jour où l'article de
    # l'amiante a été lu. « 0 lignes portent encore la mention » se lirait comme
    # une négligence de gabarit là où c'est l'inventaire qui est allé au bout.
    reserve_legale = (
        f"""{a_certifier} lignes portent encore la mention « à certifier » :
leurs textes vivent dans des statuts de corps ou des lois de circonstance qui
n'ont pas tous été lus. Une déduction n'est pas une lecture."""
        if a_certifier else
        """Aucune ne porte plus la mention « à certifier » : les
bonifications des corps actifs renvoyaient encore, il y a peu, à des « statuts
particuliers » que personne n'avait ouverts. Lire n'est pas appliquer."""
    )
    return g.depliant(
        "Trois choses que ces chiffres ne disent pas",
        f"""<p><strong>Elle ne dit pas ce que le système économiserait.</strong>
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
dans la base LEGI, version par version. {reserve_legale}</p>""",
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

    # -- ce que personne n'a cotisé, par famille ----------------------------
    #
    # MÊME TOTAL QUE LE PREMIER PARAGRAPHE DU DÉPLIANT : `observee` est la
    # dépense du risque vieillesse-survie de l'année, celle-là même que `total`
    # porte. C'est ce qui autorise une part ici, et l'interdit sous les cartes
    # du haut, qui suivent le périmètre du COR à une autre année. Les familles
    # sont celles de l'inventaire, comme sur la page Avantages ; le dispositif
    # par dispositif reste là-bas, où chaque case vide dit pourquoi. Une ligne
    # sans famille — il ne devrait pas y en avoir — compte dans l'ensemble et
    # dans aucune ligne, plutôt que rangée au hasard.
    avantages = contexte.avantages().derniere
    inventaire = contexte.inventaire_avantages()
    non_cotise = ""
    if avantages is not None and avantages.observee > 0:
        par_famille: dict[str, float] = {}
        for ligne, montant in avantages.lignes.items():
            famille = inventaire.famille_de_ligne(ligne)
            if famille is not None:
                par_famille[famille] = par_famille.get(famille, 0.0) + montant
        lignes_familles = [
            [escape(famille.libelle), _milliards(par_famille[famille.code], 1),
             g.pourcentage(par_famille[famille.code] / avantages.observee,
                           decimales=1)]
            for famille in sorted(
                inventaire.familles,
                key=lambda f: (-par_famille.get(f.code, 0.0), f.code))
            if par_famille.get(famille.code, 0.0) > 0.0
        ]
        part_gratuite = g.pourcentage(avantages.gratuit / avantages.observee,
                                      decimales=1)
        lignes_familles.append([
            "<strong>Ensemble des avantages chiffrés</strong>",
            f"<strong>{_milliards(avantages.gratuit, 1)}</strong>",
            f"<strong>{part_gratuite}</strong>",
        ])
        non_cotise = f"""
<h4>Ce que personne n'a cotisé</h4>
<p>Sur ces {_milliards(avantages.observee, 1)} de {avantages.annee},
{_milliards(avantages.gratuit, 1)}, soit {part_gratuite}, servent des droits
qu'aucune cotisation n'a ouverts : la pension du conjoint survivant, les
minima, les trimestres accordés pour un enfant ou une période de chômage, les
départs avant l'âge. La part se lit sur ce total-là, le risque
vieillesse-survie entier. Les cartes du haut suivent un autre compte, celui du
COR, en {cout.solde.derniere_annee_observee} : elle ne s'y rapporte pas.</p>
{g.tableau(
    ["Famille", f"{avantages.annee}", "Part de la dépense"],
    lignes_familles,
    ["", "nombre", "nombre"],
    titre=f"Avantages non contributifs chiffrés en {avantages.annee}, par famille, "
          f"et part de la dépense vieillesse-survie",
    entete_de_ligne=True,
)}
<p class="discret">C'est un plancher : les plus grosses lignes sont lues dans
les comptes de la protection sociale et l'enquête de la DREES auprès des
caisses, les autres calculées sur la grille de cas types, et les dispositifs
que ni l'un ni l'autre ne mesurent restent sans chiffre.
<a href="{g.lien("/avantages")}">La page Avantages</a> les nomme un par un,
dit d'où vient chaque montant et pourquoi une case reste vide.</p>
"""

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
{non_cotise}""", identifiant="cout-depenses")


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
    """Ce que d'autres caisses versent pour des droits non cotisés.

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
    # DEUX SOMMES, ET ELLES N'ARRIVENT PAS PAR LE MÊME POSTE. La branche
    # famille et l'assurance chômage versent un TRANSFERT, qui est dans le
    # poste « transferts » ; le fonds de solidarité vieillesse verse ce qu'une
    # CSG lui donne, et sa recette est dans le poste « impôts et taxes
    # affectés ». Les additionner puis écrire la somme « sur les x % du poste
    # transferts » donnait un sous-ensemble plus grand que son ensemble —
    # 8,5 % sur 4,8 % en 2024.
    part_caisses = sum(comptes.transfert_part_ressources(o.code, derniere)
                       for o in ORGANISMES if not o.recette_par_impot)
    part_par_impot = sum(comptes.transfert_part_ressources(o.code, derniere)
                         for o in ORGANISMES if o.recette_par_impot)
    supprime = comptes.transfert_supprime_part_pib(derniere)
    supprime_caisses = comptes.transfert_supprime_part_pib(derniere, par_impot=False)
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
    return g.depliant("Ce que d'autres caisses versent", f"""
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
{g.pourcentage(part_caisses, decimales=1)} des ressources de {derniere}, sur les
{g.pourcentage(part_poste, decimales=1)} du poste « transferts » ; le reste est
fait de versements plus petits, de l'assurance maladie et de l'État pour
l'essentiel. Le fonds de solidarité vieillesse verse ses
{g.pourcentage(part_par_impot, decimales=1)} de ressources par une CSG, rangée dans le poste
« impôts et taxes affectés » du tableau précédent ; il est ici parce qu'il
paie, comme les deux autres, des droits qu'aucun compte notionnel ne sert. Le COR ventile ce poste pour la dernière année de chaque rapport
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
de l'assurance chômage de {derniere}, soit
{g.pourcentage(supprime_caisses, decimales=2)} du PIB — et, avec les
{_milliards(comptes.transfert_organisme("solidarite", derniere), 1)} que le
fonds de solidarité vieillesse verse pour des trimestres que personne n'a
cotisés, {g.pourcentage(supprime, decimales=2)} du PIB et
{g.pourcentage(part_supprimee, decimales=1)} des ressources en tout. <strong>Le
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
    def _part_pib_passe(scenario: str) -> float:
        """La part de PIB d'un scénario l'année ``derniere``, règle comprise."""
        return masse_du_scenario(
            dernier.part_pib, dernier.part_derives, dernier.rapports[scenario],
            scenario, dernier.reversion_servie, dernier.reforme_en_vigueur)

    # CETTE LIGNE N'EST PAS UN « DONT », et elle l'a dit pendant un jour. La
    # garantie a quitté la masse contributive du scénario 6 le 19 septembre
    # 2026 — elle est financée par l'impôt, hors du compte des cotisants —, si
    # bien que la ligne du système 4 ne la porte plus : elle s'y AJOUTE. Le mot
    # « dont » en faisait une part d'un total qui ne la contenait pas, et la
    # preuve en était sous les yeux du lecteur, les systèmes 3 et 4 affichant
    # le même montant sur un passé où seule la garantie les sépare.
    lignes_passe.append([
        "<em>s'ajoute au système 4 : la garantie vieillesse, financée par "
        "l'impôt</em>",
        _milliards(cout.cumul(COMPOSANTE_GARANTIE), 0),
        "—",
        _milliards(dernier.cout(COMPOSANTE_GARANTIE), 1),
        g.pourcentage(masse_du_scenario(
            dernier.part_pib, dernier.part_derives,
            dernier.rapports[COMPOSANTE_GARANTIE], COMPOSANTE_GARANTIE,
            dernier.reversion_servie), decimales=1),
    ])
    # Et le total, qui est ce que le lecteur vient chercher : additionner deux
    # lignes de tête n'est pas son travail, et la cascade du dépliant suivant
    # arrive au même nombre par un autre chemin.
    cumul_total = cout.cumul("notionnel_liberal") + cout.cumul(COMPOSANTE_GARANTIE)
    lignes_passe.append([
        "<strong>4. La proposition libérale, garantie comprise</strong>",
        _milliards(cumul_total, 0),
        g.pourcentage(cumul_total / reference - 1, signe=True, decimales=1),
        _milliards(dernier.cout("notionnel_liberal")
                   + dernier.cout(COMPOSANTE_GARANTIE), 1),
        g.pourcentage(_part_pib_passe("notionnel_liberal")
                      + _part_pib_passe(COMPOSANTE_GARANTIE), decimales=1),
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
        "<em>s'ajoute au système 4 : la garantie vieillesse, financée par "
        "l'impôt</em>",
        _milliards(horizon.cout_constants(COMPOSANTE_GARANTIE), 0),
        g.pourcentage(horizon.part_pib(COMPOSANTE_GARANTIE), decimales=1),
        _milliards(avenir.cumul(COMPOSANTE_GARANTIE), 0),
        "—",
        "—",
    ])
    # La garantie est une avance : ce que les successions en rendent vient en
    # moins, et la ligne nette est ce que l'impôt finance pour de bon.
    reprises_horizon = horizon.reprises_constants()
    reprises_cumul = avenir.cumul_reprises()
    lignes_avenir.append([
        "<em>dont reprises sur les successions, au décès des bénéficiaires</em>",
        _milliards(-reprises_horizon if reprises_horizon else 0.0, 0),
        g.pourcentage(-horizon.part_pib_reprises() if reprises_horizon else 0.0,
                      decimales=1),
        _milliards(-reprises_cumul if reprises_cumul else 0.0, 0),
        "—",
        "—",
    ])
    lignes_avenir.append([
        "<em>garantie nette des reprises</em>",
        _milliards(horizon.garantie_nette_constants(), 0),
        g.pourcentage(horizon.part_pib(COMPOSANTE_GARANTIE) - horizon.part_pib_reprises(),
                      decimales=1),
        _milliards(avenir.cumul(COMPOSANTE_GARANTIE) - reprises_cumul, 0),
        "—",
        "—",
    ])
    # Le total de la proposition, garantie nette comprise : c'est le nombre
    # auquel la cascade du dépliant suivant aboutit, et celui qu'il faut
    # comparer au système actuel. La ligne « 4 » au-dessus ne porte que les
    # pensions contributives.
    cumul_total_avenir = (avenir.cumul("notionnel_liberal")
                          + avenir.cumul(COMPOSANTE_GARANTIE) - reprises_cumul)
    lignes_avenir.append([
        "<strong>4. La proposition libérale, garantie nette comprise</strong>",
        _milliards(horizon.cout_constants("notionnel_liberal")
                   + horizon.garantie_nette_constants(), 0),
        g.pourcentage(horizon.part_pib("notionnel_liberal")
                      + horizon.part_pib(COMPOSANTE_GARANTIE)
                      - horizon.part_pib_reprises(), decimales=1),
        _milliards(cumul_total_avenir, 0),
        g.pourcentage(cumul_total_avenir / reference_avenir - 1, signe=True,
                      decimales=1),
        _milliards(cumul_total_avenir - reference_avenir, 0),
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


<p class="discret"><strong>La ligne du système 4 ne porte que ses pensions
contributives.</strong> La garantie vieillesse est financée par l'impôt et non
par les cotisations : elle est tenue hors du compte des cotisants, et ne s'y
trouve donc pas comprise. C'est pour cela que les systèmes 3 et 4 affichent le
même montant sur ce passé : avant la bascule ils prélèvent les mêmes taux, et
seule la garantie les sépare. Elle s'y ajoute, ligne suivante, et la dernière
ligne donne le total.</p>

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
constants de {euros}. Comme sur le passé, <strong>la ligne du système 4 ne
porte que ses pensions contributives</strong> : la garantie vieillesse, payée
par l'impôt, s'y ajoute, et la dernière ligne donne le total, net de ce que les
successions rendent. <strong>Les trois systèmes notionnels comparés ici sont
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
     "Compte notionnel, les deux parts", "La proposition libérale"],
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
<p class="discret">Comme dans les deux tableaux du dessus, la colonne de la
proposition ne porte que ses <strong>pensions contributives</strong> : sa
garantie vieillesse y ajoute
{g.pourcentage(horizon.part_pib(COMPOSANTE_GARANTIE), decimales=1)} du PIB en
{avenir.derniere_annee}, ce qui porte son total à
{g.pourcentage(horizon.part_pib("notionnel_liberal")
               + horizon.part_pib(COMPOSANTE_GARANTIE), decimales=1)}, ou
{g.pourcentage(horizon.part_pib("notionnel_liberal")
               + horizon.part_pib(COMPOSANTE_GARANTIE)
               - horizon.part_pib_reprises(), decimales=1)} net des reprises
sur succession.</p>
""", identifiant="cout-scenarios")


#: Ce que chaque système AJOUTE à la cascade par rapport à celui qui le précède
#: dans ``SCENARIOS_MONTRES`` : son étiquette, posée sous la colonne, et ce que
#: l'étiquette ne peut pas dire, redit dans le tableau des chiffres.
#:
#: LA CHAÎNE N'EST PAS ÉCRITE ICI, et c'est tout l'objet de ce dictionnaire.
#: L'ordre des marches est celui de ``SCENARIOS_MONTRES``, qui est le seul
#: endroit du site où les systèmes sont listés ; ce dictionnaire ne fait que
#: NOMMER chacun d'eux. Ajouter un système à la liste ajoute donc sa marche, et
#: ``test_web`` refuse un système qui n'aurait pas son nom ici — c'est la seule
#: chose qu'une main doive écrire.
#:
#: Les accolades sont remplies par ``_libelles_cascade`` : un taux, une année,
#: une part qui change d'une année à l'autre. Aucun nombre n'est écrit en
#: toutes lettres, sous peine qu'un réglage de la page démente son étiquette.
MARCHES_SYSTEMES: dict[str, tuple[str, str]] = {
    "notionnel_retroactif": (
        "Pensions recalculées",
        "la part salariale seule, rendue au franc le franc : diviseur "
        "d'espérance de vie, indexation du capital sur les salaires, et retrait "
        "de tous les autres avantages non contributifs — minimum contributif, "
        "trimestres gratuits, majorations pour enfants, départs anticipés",
    ),
    "notionnel_retroactif_employeur": (
        "Part patronale au compte",
        "ce que l'employeur verse ouvre désormais un droit à celui qui le voit "
        "passer ; c'est la seule chose qui sépare cette marche de la précédente",
    ),
    "notionnel_liberal": (
        "Cotisation unique de {taux}",
        "un taux unique pour tous les statuts, parts salariale et patronale "
        "additionnées, sur les seuls droits acquis à compter de {bascule}",
    ),
}

#: Les trois marches qui ne sont pas des systèmes, et leur place dans la
#: chaîne : la réversion AVANT — le rapport des systèmes ne décrit que les
#: droits directs —, la garantie et les reprises APRÈS, parce qu'elles ne
#: remplacent aucun rapport mais s'ajoutent par-dessus.
MARCHE_REVERSION = "reversion"
MARCHE_REPRISES = "reprises"
MARCHES_HORS_SYSTEMES: dict[str, tuple[str, str]] = {
    MARCHE_REVERSION: (
        "Réversion supprimée",
        "{reversion} de la masse versée cette année-là, et le premier avantage "
        "non contributif du système : les comptes notionnels ne rendent que ce "
        "que l'assuré a cotisé",
    ),
    COMPOSANTE_GARANTIE: (
        "Garantie vieillesse",
        "le plancher individualisé qui remplace l'ASPA, financé par l'impôt et "
        "non par les cotisations : il s'AJOUTE à la dépense",
    ),
    MARCHE_REPRISES: (
        "Reprises sur successions",
        "la garantie est une avance, et le décès du bénéficiaire la rend sur sa "
        "succession : {reprise} de ce qu'elle a versé",
    ),
}


def _libelles_cascade(contexte: Contexte, part_derives: float,
                      part_reprise: float) -> dict[str, str]:
    """Ce que les accolades des étiquettes et des gloses valent cette année-là.

    Tout nombre qu'une étiquette affiche passe par ici. C'est une règle, et
    elle a une raison : le taux de la proposition est un RÉGLAGE de la page —
    l'adresse peut le changer —, et la part de réversion dans la masse versée
    tombe d'un dixième aujourd'hui à un dix-huitième en 2070. Une étiquette qui
    écrirait l'un ou l'autre en toutes lettres mentirait au premier changement,
    sans qu'une ligne de code soit fautive.
    """
    base = contexte.base
    return {
        "taux": g.pourcentage(base.taux_cotisation_liberal, decimales=0),
        "bascule": str(base.annee_bascule),
        "reversion": g.pourcentage(part_derives, decimales=1),
        "reprise": g.pourcentage(part_reprise, decimales=0),
    }


def _marche_cascade(code: str, valeur: float, libelles: dict[str, str]) -> g.Marche:
    """Une marche nommée, ses accolades remplies, son montant en milliards."""
    gabarit, glose = (MARCHES_SYSTEMES.get(code)
                      or MARCHES_HORS_SYSTEMES[code])
    return g.Marche(gabarit.format(**libelles), valeur / 1000,
                    glose=glose.format(**libelles))


def _marches_cascade(base: float, part_derives: float, rapports: dict[str, float],
                     libelles: dict[str, str],
                     part_reprise: float = 0.0) -> list[g.Marche]:
    """Les marches qui vont du système actuel à la proposition, dans l'ordre.

    ELLES SONT EXACTEMENT ADDITIVES, et ce n'est pas un hasard :
    ``masse_du_scenario`` écrit la masse d'un système comme la part DIRECTE de
    la base multipliée par son rapport, plus la réversion s'il la sert. Une
    différence de deux rapports appliquée à la même part directe est donc la
    contribution propre du changement qui les sépare, et leur somme vaut
    l'écart des deux totaux au centime. ``test_web`` le vérifie plutôt que d'en
    croire ce commentaire.

    L'ORDRE EST CELUI DE ``SCENARIOS_MONTRES``, et il n'est écrit nulle part
    ailleurs. C'est ce qui fait que la figure suit le site : le jour où un
    système entre dans la liste ou en sort, la cascade gagne ou perd sa marche
    sans qu'on ait à rouvrir cette fonction.

    ``part_reprise`` est ce que les successions rendent de la garantie, en
    fraction de ce qu'elle a versé. Une FRACTION, et non un montant : le compte
    du COR ne porte pas les reprises, et le seul emprunt qu'on fasse au modèle
    est celui qu'on lui fait partout ailleurs dans cette page — un rapport sans
    dimension, jamais un niveau.
    """
    directe = base * (1.0 - part_derives)
    marches = [_marche_cascade(MARCHE_REVERSION, -base * part_derives, libelles)]
    precedent = 1.0
    for code in SCENARIOS_MONTRES[1:]:
        marches.append(_marche_cascade(code, directe * (rapports[code] - precedent),
                                       libelles))
        precedent = rapports[code]
    # La garantie n'est pas un système : elle ne REMPLACE pas le rapport
    # précédent, elle s'ajoute par-dessus, et le cumul ne repart donc pas
    # d'elle. Les reprises viennent en moins de ce qu'elle a versé.
    garantie = directe * rapports[COMPOSANTE_GARANTIE]
    marches.append(_marche_cascade(COMPOSANTE_GARANTIE, garantie, libelles))
    if part_reprise:
        marches.append(_marche_cascade(MARCHE_REPRISES, -garantie * part_reprise,
                                       libelles))
    return marches


#: Les années que le sélecteur de la cascade propose : l'année mesurée, celle
#: de la bascule, puis les décennies jusqu'à l'horizon. Pas toutes les années
#: du compte — quarante-six liens ne se lisent pas, et rien ne distingue 2043
#: de 2044.
PAS_ANNEES_CASCADE = 10


def _annees_cascade(solde, bascule: int) -> tuple[int, ...]:
    """Les millésimes offerts, dans l'ordre, sans doublon.

    L'année MESURÉE ouvre la liste : c'est la seule qui ne soit pas une
    projection, et c'est d'elle que vient le chiffre que tout le monde cite. La
    BASCULE suit, parce que c'est la première année où la proposition
    s'applique. Le reste est décennal.
    """
    obs = solde.derniere_annee_observee
    fin = solde.derniere_annee
    annees = [obs, max(bascule, obs)]
    debut = (max(bascule, obs) // PAS_ANNEES_CASCADE + 1) * PAS_ANNEES_CASCADE
    annees += list(range(debut, fin + 1, PAS_ANNEES_CASCADE))
    if annees[-1] != fin:
        annees.append(fin)
    vues: list[int] = []
    for annee in annees:
        if annee not in vues and obs <= annee <= fin:
            vues.append(annee)
    return tuple(vues)


def _annee_cascade(solde, bascule: int, regards: dict[str, str] | None) -> int:
    """L'année que l'adresse demande, ou l'année mesurée.

    Une année hors de la liste est RAMENÉE à l'année mesurée plutôt que
    refusée : une adresse partagée puis rejouée après que le compte a avancé
    d'un millésime ne doit pas afficher une erreur, elle doit afficher la
    cascade.
    """
    offertes = _annees_cascade(solde, bascule)
    demandee = (regards or {}).get("cascade", "")
    if _est_entier(demandee) and int(demandee) in offertes:
        return int(demandee)
    return offertes[0]


def _pib_cascade(contexte: Contexte, annee: int) -> tuple[float, bool]:
    """Le PIB qui convertit une part en milliards, et s'il est publié.

    LE COMPTE DU COR TIENT SES DEUX BOUTS EN PART DU PIB, de 2002 à 2070 ; il
    ne publie un PIB en euros que jusqu'à l'année mesurée. Au-delà, c'est le
    modèle qui en projette un — le même que la trajectoire emploie pour ses
    propres parts —, et les deux coïncident exactement à l'année mesurée, si
    bien que la suite des milliards ne saute pas au passage.

    Le second terme du couple dit lequel des deux on a pris, et la page l'écrit
    sous la figure : un milliard de 2060 est une part du PIB multipliée par un
    PIB supposé, et cela ne se devine pas.
    """
    ligne = contexte.cout().solde.annee(annee)
    if ligne is not None and ligne.pib:
        return ligne.pib, True
    projete = contexte.cout().avenir.annee(annee)
    return (projete.pib if projete else 0.0), False


def _cout_detail_cascade(contexte: Contexte,
                         regards: dict[str, str] | None = None) -> str:
    """De la dépense d'une année à celle de la proposition, mesure par mesure.

    CE QUE CETTE SECTION AJOUTE AUX TABLEAUX QUI LA PRÉCÈDENT, c'est le
    CHEMIN. Les quatre systèmes y sont comparés deux à deux, ce qui dit de
    combien ils s'écartent et jamais par quoi ; le lecteur doit soustraire de
    tête quatre fois pour savoir laquelle des décisions du programme pèse. Une
    cascade le montre d'un coup, et elle porte en plus une vérification que le
    tableau n'a pas : les marches somment exactement à l'écart des deux totaux,
    ou la dernière barre ne retombe pas où elle devrait.

    L'ANNÉE SE CHOISIT, et il le fallait. À l'année mesurée, la cotisation
    unique ne déplace rien : elle ne vaut que pour les droits acquis à compter
    de la bascule, et aucun retraité de cette année-là n'en a acquis un seul
    sous elle. Une cascade figée sur cette année montrerait donc la mesure
    centrale du programme à zéro, sans rien dire. Une cascade figée sur
    l'horizon perdrait le chiffre que tout le monde cite. Le sélecteur rend les
    deux, et les quarante-cinq années entre elles.

    UN SEUL PÉRIMÈTRE, DE BOUT EN BOUT : le compte du COR, qui tient ses deux
    bouts de 2002 à 2070. La page portait deux cascades sur deux périmètres,
    dont l'une empruntait son niveau à la trajectoire du modèle ; il n'en reste
    qu'une, et rien ne traverse plus d'une série à l'autre. Ce qu'on emprunte
    encore au modèle est ce qu'on lui emprunte partout ailleurs sur cette page :
    des RAPPORTS sans dimension — les masses relatives des systèmes, et la part
    de la garantie que les successions rendent.

    ``regards`` porte l'année demandée. C'est une VUE et non un réglage :
    elle ne change aucun chiffre, elle choisit lequel on montre, et elle ne
    voyage pas vers les autres pages — voir ``_VUES_DE_PAGE``.
    """
    cout = contexte.cout()
    solde = cout.solde
    avenir = cout.avenir
    base = contexte.base
    bascule = base.annee_bascule

    obs = solde.derniere_annee_observee
    offertes = _annees_cascade(solde, bascule)
    annee = _annee_cascade(solde, bascule, regards)
    ligne = solde.annee(annee)
    pib, publie = _pib_cascade(contexte, annee)

    # La dépense de l'année, en millions : une part du PIB multipliée par le
    # PIB. À l'année mesurée, cela redonne exactement ce que le COR publie.
    depense = ligne.depense("actuel") * pib
    part_directe = depense * (1.0 - ligne.part_derives)
    arrivee_meur = (
        part_directe * (ligne.rapports["notionnel_liberal"]
                        + ligne.rapports[COMPOSANTE_GARANTIE])
    )
    # Ce que les successions rendent de la garantie, en fraction de ce qu'elle
    # a versé : un rapport, seule chose que le compte du COR ne porte pas et
    # qu'on aille chercher dans la trajectoire.
    projetee = avenir.annee(annee)
    garantie_modele = (projetee.cout_constants(COMPOSANTE_GARANTIE)
                       if projetee else 0.0)
    part_reprise = ((projetee.reprises_constants() / garantie_modele)
                    if projetee and garantie_modele else 0.0)
    arrivee_meur -= part_directe * ligne.rapports[COMPOSANTE_GARANTIE] * part_reprise

    libelles = _libelles_cascade(contexte, ligne.part_derives, part_reprise)
    marches = (
        [g.Marche("Système actuel", depense / 1000, total=True,
                  couleur="var(--actuel)",
                  glose=f"{_sans_numero(LIBELLES_SYSTEMES['actuel'])} : la "
                        f"dépense de retraite "
                        + (f"mesurée en {annee}" if publie
                           else f"que le compte du COR projette pour {annee}"))]
        + _marches_cascade(depense, ligne.part_derives, ligne.rapports,
                           libelles, part_reprise)
        + [g.Marche("La proposition", arrivee_meur / 1000, total=True,
                    couleur="var(--liberal)",
                    glose=f"{_sans_numero(LIBELLES_SYSTEMES['notionnel_liberal'])}"
                          " : pensions contributives et garantie vieillesse, "
                          "nette de ce que les successions en rendent")]
    )
    figure = g.cascade(
        f"De la dépense du système actuel à celle de la proposition en "
        f"{annee}, mesure par mesure, en milliards d'euros",
        tuple(marches), unite=f"Md € {annee}", decimales=1,
        libelle_marche="Mesure",
    )

    ecart = (depense - arrivee_meur) / 1000
    choix = g.bascule(
        "Année décomposée",
        [(str(millesime), _lien_cascade(millesime)) for millesime in offertes],
        str(annee),
    )
    # La phrase sur la cotisation unique ne vaut que tant qu'elle ne déplace
    # rien, c'est-à-dire avant la bascule. L'écrire en toutes années aurait
    # démenti la figure dès le premier clic sur le sélecteur.
    note_bascule = ""
    if annee < bascule:
        note_bascule = f"""
<div class="note vigilance"><strong>La cotisation unique ne déplace rien en
{annee}, et c'est normal.</strong> Elle ne vaut que pour les droits acquis à
compter de la bascule, en {bascule} : aucun retraité de {annee} n'en a acquis un
seul sous elle, et sa marche est donc plate. Le chiffre a été calculé, et il
vaut zéro. C'est la mesure centrale du programme : pour la voir peser, prenez
une année plus tardive dans le sélecteur ci-dessus. Les reprises sur
successions sont dans le même cas.</div>
"""
    source_pib = (
        f"Le compte du COR publie un PIB en euros jusqu'en {obs} ; au-delà, la "
        f"part du PIB est multipliée par le PIB que le modèle projette, celui-là "
        f"même dont la trajectoire se sert. Les deux coïncident en {obs}, si "
        f"bien que la suite des milliards ne saute pas au passage."
        if not publie else
        f"Les milliards sont ceux du PIB que le COR publie pour {annee}."
    )
    return g.depliant(
        f"De {_milliards(depense, 0)} à {_milliards(arrivee_meur, 0)} : "
        f"ce que chaque mesure déplace", f"""
<p>Les tableaux du dessus comparent quatre systèmes deux à deux. Ils disent de
combien ils s'écartent ; ils ne disent pas <em>par quoi</em>. Voici le chemin :
on part de la dépense du système actuel, on applique les mesures de la
proposition l'une après l'autre, et l'on arrive à la sienne. Une barre rouge
ajoute à la dépense, une barre verte l'en retire, et la somme des marches vaut
exactement l'écart des deux totaux : sans cela, la dernière barre ne retomberait
pas où elle retombe.</p>

{choix}

<p>En {annee}, la dépense passe de {_milliards(depense, 0)} à
{_milliards(arrivee_meur, 0)}, soit {_milliards(ecart * 1000, 0)} de moins,
{g.pourcentage(ecart * 1000 / depense, decimales=0)} de la facture. Tout est
pris sur le compte du <a href="{g.lien("/donnees")}">Conseil d'orientation des
retraites</a>, le même que les cartes du haut, et il tient ses deux bouts
jusqu'en {solde.derniere_annee}.</p>

{figure}
{note_bascule}
<p class="discret">{source_pib} Une année antérieure à {obs} n'est pas offerte :
ce que chaque système aurait coûté sur le passé est dans le dépliant précédent,
à sa place, celle d'un contrefactuel.</p>

<div class="note"><strong>Une décomposition est séquentielle, et l'ordre
compte.</strong> Chaque marche est l'effet de sa mesure <em>sachant celles qui
la précèdent</em>, jamais son effet prise seule : la part patronale portée au
compte pèse d'autant plus que la part salariale a déjà été recalculée, et la
garantie d'autant moins que les pensions contributives sont plus hautes. Un
autre ordre donnerait d'autres marches, jamais un autre total. L'ordre retenu
est celui de la construction du compte : on retire ce que le système ne sert
plus, on recalcule ce qu'il sert, on dit avec quelles cotisations, puis on pose
le plancher par-dessus.</div>

<div class="note"><strong>Une dépense n'est pas un solde.</strong> Cette
cascade ne montre qu'un côté du compte : ce qui sort. La proposition change
aussi ce qui rentre : {g.pourcentage(base.taux_cotisation_liberal, decimales=0)}
sur l'assiette des revenus d'activité, sans les impôts affectés ni les
transferts qui payaient des droits supprimés. Et un système qui coûterait
moitié moins servirait moitié moins, ce qui est une autre affaire. Le dépliant
« recettes et dépenses, poste par poste » porte les deux côtés, et celui du
coefficient d'équilibre dit ce qui manque.</div>
""", identifiant="cout-cascade")


def _lien_cascade(annee: int) -> str:
    """L'adresse de la page Coût, cascade posée sur cette année-là.

    Les réglages de modélisation que ``g.lien`` porte déjà sont conservés : le
    sélecteur change ce qu'on REGARDE, jamais sous quelles règles la page se
    calcule.
    """
    adresse = g.lien("/cout")
    return adresse + ("&" if "?" in adresse else "?") + f"cascade={annee}"


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
    # La dernière note SUIT LE SIGNE du coefficient, sous peine de démentir le
    # nombre qu'elle commente. Elle ne connaissait qu'une marge, et le jour où
    # la recette de la proposition est devenue ses 18 % sur l'assiette, le
    # facteur est passé sous un : la page lisait « une économie de −9 % »
    # au-dessus d'un 0,92. Le catalogue des affirmations du site le tient.
    coefficient = horizon.coefficient("notionnel_liberal")
    if coefficient >= 1.0:
        lecture_coefficient = (
            "<strong>Un coefficient supérieur à un est une marge, et une "
            f"marge se sert.</strong> Lire les {g.nombre(coefficient, 2)} de la "
            "proposition comme une économie de "
            f"{g.pourcentage(1 - 1 / coefficient, decimales=0)} serait un "
            "contresens : à ces recettes-là, ce système servirait davantage que "
            "ce que la colonne « dépense » lui prête, et autrement réparti entre "
            "les carrières."
        )
    else:
        lecture_coefficient = (
            "<strong>Un coefficient inférieur à un est un manque, et un manque "
            f"se règle.</strong> Les {g.nombre(coefficient, 2)} de la proposition "
            f"en {solde.derniere_annee} disent qu'à ses recettes, "
            f"{g.pourcentage(horizon.taux_liberal, decimales=0)} appliqués à "
            "l'assiette des revenus d'activité, sans les impôts affectés ni les "
            "transferts qui payaient des droits supprimés, le système servirait "
            f"{g.pourcentage(coefficient, decimales=0)} de ce que la colonne "
            "« dépense » lui prête. Il faudrait rogner de "
            f"{g.pourcentage(1 - coefficient, decimales=0)}, relever le taux, ou "
            "financer autrement. C'est au réglage annuel du programme de "
            "l'absorber, et il déplacerait toutes les pensions du même facteur."
        )
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
le système actuel encaisse : ce que la branche famille, l'assurance chômage et
le fonds de solidarité vieillesse versent pour des droits qu'ils ne servent
pas, soit

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
système de retraite y prélève
{g.pourcentage(observe.taux_prelevement, decimales=1)} de ressources en tout en
{obs}, et {g.pourcentage(horizon.taux_prelevement, decimales=1)} en
{solde.derniere_annee} là où le COR projette son propre taux ; la proposition en
prélèverait 18 : c'est le rapport de ces deux nombres, année par année, qui fait
sa recette. Elle ne touche aucune compensation d'allègement, n'en accordant
aucun, et cela ne lui retire rien ici : cette compensation passe par la TVA, qui
finance la branche maladie et n'apparaît pas au compte de la retraite.</div>

<div class="note"><strong>L'autre lecture, plus généreuse d'un point de
PIB.</strong> Le modèle sait aussi appliquer aux 18 % la DÉPERDITION du système
actuel : les allègements généraux et les assiettes réduites font qu'un taux
légal proche de
{g.pourcentage(0.18 / horizon.rapports_recettes["notionnel_liberal"], decimales=0)}
ne rentre pas en entier. Compter ainsi revient à supposer que la proposition
garde la même architecture d'exonérations, ce que son texte ne dit pas, et à
lui laisser du même mouvement les impôts affectés et les subventions
d'équilibre que la lecture retenue ne reconduit pas. Son solde moyen projeté
est meilleur d'environ un point de PIB. Les deux lectures se défendent, elles
sont toutes deux calculées, et la page a retenu la plus sévère.</div>

{_note_lecture_coefficient(_reglage_proposition(solde))}
""", identifiant="cout-equilibre")


#: Les lignes du tableau poste par poste, dans l'ordre du tableau 2.2 du
#: rapport annuel du COR — « Structure des ressources du système de retraite » —,
#: puis les dépenses en face, que le COR publie ailleurs et que ce tableau
#: réunit. Chaque ligne porte son code dans ``SoldeAnnuel.postes_ressources``
#: ou ``postes_depenses``, son libellé, et son rang : ``poste`` s'ajoute au
#: total, ``dont`` ventile la ligne du dessus, ``total`` est le total.
LIGNES_RECETTES: tuple[tuple[str, str, str], ...] = (
    ("cotisations", "Cotisations sociales", "poste"),
    ("contribution_equilibre_etat", "Contribution d'équilibre de l'État", "poste"),
    ("subventions_equilibre", "Subventions d'équilibre aux régimes spéciaux", "poste"),
    ("impots_et_taxes", "Impôts et taxes affectés, dont CSG", "poste"),
    ("impots_solidarite", "Dont fonds de solidarité vieillesse", "dont"),
    ("transferts", "Transferts d'organismes extérieurs", "poste"),
    ("transferts_famille", "Dont branche famille", "dont"),
    ("transferts_chomage", "Dont assurance chômage", "dont"),
    ("transferts_autres", "Dont autres transferts", "dont"),
    ("autres_produits", "Autres produits", "poste"),
)
LIGNES_DEPENSES: tuple[tuple[str, str, str], ...] = (
    ("droits_directs", "Pensions de droit direct", "poste"),
    ("droits_derives", "Pensions de réversion (droit dérivé)", "poste"),
)


def _cout_note_restitution(contexte: Contexte, annee: int, pib: float,
                           annee_pib: int) -> str:
    """Où va l'argent que la proposition n'encaisse plus.

    C'est la question que le tableau du dessus pose sans y répondre : trois
    postes s'en vont, et le lecteur en déduit naturellement que l'État les
    garde — c'est-à-dire qu'ils comblent un déficit. La décision du
    20 septembre 2026 dit le contraire, et cette note l'écrit avec ses
    chiffres : la moitié est rendue aux salaires, la moitié éteint de la dette.

    Le partage est un RÉGLAGE, et la note se tait quand il vaut zéro : il n'y
    a alors rien à raconter, la recette retourne au budget comme avant.
    """
    restitution = contexte.restitution()
    if not restitution or restitution.part_rendue <= 0.0:
        return ""
    part = restitution.annuelle(annee)
    if part.poste_abandonne <= 0.0:
        return ""
    return f"""
<div class="note"><strong>Ce que la proposition n'encaisse plus, elle ne le
garde pas.</strong> Les impôts et taxes affectés valent
{g.pourcentage(part.poste_abandonne, decimales=2)} du PIB en {annee}, soit
{_milliards(part.poste_abandonne * pib, 0)} au point de PIB de {annee_pib}.
Ne rien dire de cette recette reviendrait à la laisser au budget, c'est-à-dire
à la consacrer tout entière au déficit. La proposition la partage en deux :
<strong>{_milliards(part.rendu * pib, 0)} sont rendus aux salaires</strong>,
autant <strong>éteint de la dette</strong>, à commencer par celle que le
système de retraite porte. Ce qui est rendu l'est dans l'ordre que le droit
impose : on supprime d'abord les deux impôts du poste qui sortent d'une
rémunération — la taxe sur les salaires, dont l'article L. 131-8, 1° du code de
la sécurité sociale verse {g.pourcentage(0.5835, decimales=2)} à la branche
vieillesse, et le forfait social, que l'article L. 241-3, 1° lui donne en
entier, ensemble {_milliards(part.supprime_sur_la_remuneration * pib, 0)} —,
puis le solde revient par une baisse de
{g.nombre(part.points_csg * 100, 2)} point de la CSG sur les revenus
d'activité. Cette CSG-là ne finance aujourd'hui <em>aucune</em> retraite : ses
{g.pourcentage(0.092)} vont à la famille, à l'assurance maladie, à la dette
sociale, à l'Unédic et à l'autonomie, et rien à la vieillesse (L. 131-8, 3°).
La baisse n'est donc pas la restitution d'un prélèvement retraite, c'est un
impôt supprimé. <strong>Rien de tout cela ne change le solde ci-dessus</strong> :
ces recettes étaient déjà sorties du compte de la retraite, et ce que cette
note ajoute est ce qu'il en advient dans le budget de l'État et sur les fiches
de paie.</div>"""


def _sans_numero(libelle: str) -> str:
    """« 4. La proposition libérale » → « La proposition libérale ».

    Le numéro des systèmes est celui des barres de Simuler ; dans un en-tête
    de colonne, il ne dit rien, et la majuscule reste celle du libellé.
    """
    return libelle.split(". ", 1)[1] if ". " in libelle else libelle


def _cout_detail_postes(contexte: Contexte) -> str:
    """Recettes et dépenses poste par poste, le système actuel et la proposition.

    C'est le tableau 2.2 du rapport annuel du COR — la structure des
    ressources, en milliards et en pourcentage du total — refait pour DEUX
    systèmes, la même année, avec les dépenses en face et le solde en bas.
    Tout ce qu'il contient est déjà dans le bilan de la page : ``ressources_de``
    et ``depense`` y sont simplement écrits ligne à ligne, et les lignes
    somment au total. Rien n'y est calculé qui ne le soit ailleurs ; ce qui est
    nouveau, c'est qu'on VOIT ce que chaque décision de la proposition retire
    ou remplace, poste par poste, au lieu de le lire dans une note.

    L'année est celle de la bascule : c'est la première où la proposition
    s'applique, et c'est de là que la décision se prend. Le compte du COR y est
    projeté, et le PIB n'y est pas publié ; les milliards sont donc ceux d'un
    point de PIB de la dernière année publiée, ce que le tableau dit.
    """
    comptes = contexte.comptes()
    cout = contexte.cout()
    solde = cout.solde
    base = contexte.base
    annee = min(max(base.annee_bascule, solde.premiere_annee), solde.derniere_annee)
    ligne = solde.annee(annee)
    annee_pib = comptes.pib.derniere_annee
    pib = comptes.pib(annee_pib)
    derniere_ventilee = comptes.derniere_annee_ventilee
    systemes = ("actuel", "notionnel_liberal")
    recettes = {s: ligne.postes_ressources(s) for s in systemes}
    depenses_ = {s: ligne.postes_depenses(s) for s in systemes}
    total_recettes = {s: ligne.ressources_de(s) for s in systemes}
    total_depenses = {s: ligne.depense(s) for s in systemes}

    # La garantie vieillesse, lue sur la vraie distribution des pensions comme
    # le fait le dépliant qui lui est consacré — jamais sur les cas types, dont
    # ce dépliant dit pourquoi le chiffre est faux. Plancher de base, pensions
    # de la proposition : la lecture la plus basse des deux qu'il donne.
    distribution = contexte.distribution()
    simulateur = contexte.simulateur()
    vers_enquete = simulateur.macro.coefficient_prix(
        base.annee_euros_garantie_vieillesse, distribution.millesime)
    # Le facteur est celui de la trajectoire : la pension moyenne que la
    # garantie regarde, sur celle du système actuel l'année de l'enquête —
    # voir ``GarantieDistribution``. Le même que le dépliant de la garantie.
    annee_enquete = cout.annee(distribution.millesime)
    facteur_contributif = annee_enquete.garantie.facteur if annee_enquete.garantie else 1.0
    garantie = cout_garantie(
        distribution,
        simulateur.effectifs.effectif("tous_regimes", distribution.millesime),
        base.garantie_vieillesse_mensuelle * vers_enquete, facteur_contributif,
    )
    # Un ayant droit sur deux réclame : le même recours que le dépliant.
    garantie_meur = garantie.cout_annuel_meur * base.taux_recours_garantie / vers_enquete
    # Le pilier capitalisé : 5 % de la même assiette que les 18 %, donc les
    # cotisations de la proposition multipliées par le rapport des deux taux.
    capitalise = (
        recettes["notionnel_liberal"]["cotisations"]
        * base.taux_capitalisation_obligatoire / base.taux_cotisation_liberal
        if ligne.recette_par_assiette else 0.0
    )

    def cellules(valeur: float, total: float, absent: bool = False) -> list[str]:
        """Milliards, part de PIB, part du total — ou trois tirets."""
        if absent:
            return ["—", "—", "—"]
        return [
            _milliards(valeur * pib, 1),
            g.pourcentage(valeur, decimales=2),
            g.pourcentage(valeur / total, decimales=1) if total else "—",
        ]

    def rangee(libelle: str, rang: str, valeurs: dict[str, float],
               totaux: dict[str, float]) -> list[str]:
        if rang == "total":
            texte = f"<strong>{escape(libelle)}</strong>"
        elif rang == "dont":
            texte = f'<span class="dont">{escape(libelle)}</span>'
        else:
            texte = escape(libelle)
        cellules_ = [texte]
        for s in systemes:
            # Un poste que la proposition ne reconduit pas se lit comme absent,
            # et non comme un zéro : la note dit pourquoi il est parti.
            cellules_ += cellules(valeurs[s], totaux[s],
                                  absent=(rang != "total" and valeurs[s] == 0.0))
        return cellules_

    lignes: list[list[str]] = []
    for code, libelle, rang in LIGNES_RECETTES:
        lignes.append(rangee(libelle, rang, {s: recettes[s][code] for s in systemes},
                             total_recettes))
    lignes.append(rangee("Total des ressources", "total", total_recettes, total_recettes))
    for code, libelle, rang in LIGNES_DEPENSES:
        lignes.append(rangee(libelle, rang, {s: depenses_[s][code] for s in systemes},
                             total_depenses))
    lignes.append(rangee("Total des dépenses", "total", total_depenses, total_depenses))
    lignes.append(
        ["<strong>Solde</strong>"]
        + sum(([_milliards(ligne.solde(s) * pib, 1),
                g.pourcentage(ligne.solde(s), signe=True, decimales=2), "—"]
               for s in systemes), [])
    )
    lignes.append(
        ['<span class="dont">Pour mémoire, hors du compte : garantie vieillesse, '
         "financée par l'impôt</span>", "—", "—", "—",
         _milliards(garantie_meur, 1),
         g.pourcentage(garantie_meur / pib, decimales=2), "—"]
    )
    lignes.append(
        ['<span class="dont">Pour mémoire, hors du système : pilier capitalisé '
         "obligatoire</span>", "—", "—", "—"]
        + (cellules(capitalise, 0.0) if capitalise else ["—", "—", "—"])
    )

    return g.depliant(
        "Recettes et dépenses, poste par poste", f"""
<p>Le Conseil d'orientation des retraites publie chaque année la structure des
ressources du système de retraite : sept lignes, en milliards d'euros et en
pourcentage du total. Voici le même tableau pour le système actuel et pour la
proposition, en {annee}, l'année de la bascule, avec les dépenses en face et le
solde en bas. Chaque ligne applique à son poste la règle que le bilan du haut
applique au total : les lignes somment aux totaux, et les totaux sont ceux des
courbes.</p>

{g.tableau(
    ["Poste", f"{_sans_numero(LIBELLES_SYSTEMES['actuel'])}, Md €", "% du PIB", "Part",
     f"{_sans_numero(LIBELLES_SYSTEMES['notionnel_liberal'])}, Md €", "% du PIB", "Part"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre", "nombre", "nombre"],
    titre=f"Ressources et dépenses du système de retraite en {annee}, système "
          f"actuel et proposition, en milliards d'euros et en part du PIB",
    entete_de_ligne=True,
)}

<p class="discret">Les parts de PIB sont celles du compte du COR pour {annee},
année projetée. Le PIB de {annee} n'est pas publié : les milliards sont ceux
d'un point de PIB de {annee_pib}, dernière année connue
({_milliards(pib, 0)}), et donnent l'ordre de grandeur, pas la valeur de
{annee}. La structure des ressources du système actuel est celle de
{derniere_ventilee}, dernière année que le COR ventile, reconduite ; les
« dont » sont ce que chaque payeur a réellement versé la dernière année connue,
à part constante des ressources. « Part » rapporte chaque ligne au total des
ressources, ou des dépenses, de son système. Un tiret est un poste que le
système ne compte pas.</p>

<div class="note"><strong>Ce que la proposition change, ligne à ligne.</strong>
Les cotisations deviennent
{g.pourcentage(base.taux_cotisation_liberal, decimales=0)} de l'assiette des
revenus d'activité, parts salariale et patronale additionnées, pour tous les
statuts. Trois postes disparaissent : la contribution d'équilibre de l'État,
remplacée par ces {g.pourcentage(base.taux_cotisation_liberal, decimales=0)}
appliqués aux traitements des fonctionnaires ; les subventions d'équilibre,
dont la fusion des régimes supprime l'objet ; les impôts et taxes affectés, qui
n'acquièrent de droits à personne. Des transferts, seule reste la part qui ne
paie pas un droit supprimé : la branche famille et l'assurance chômage
financent des droits que le compte notionnel ne sert plus. Côté dépenses, les
pensions sont recalculées au franc le franc des cotisations, et la réversion
n'est plus servie, ce que la dernière note détaille. La garantie vieillesse qui remplace l'ASPA est financée par l'impôt,
hors du compte des cotisants ; le dépliant qui lui est consacré en donne
quatre lectures, et la ligne pour mémoire porte la plus basse. Le pilier
capitalisé ne passe pas par les caisses et n'est ni une ressource ni une
dépense du système : il est rappelé pour que rien ne manque.</div>

<div class="note"><strong>La recette réagit sur trois points, et sur trois
seulement.</strong> Elle suit le droit : ce que la branche famille, l'assurance
chômage et le fonds de solidarité vieillesse versent pour des droits que les
systèmes notionnels ne servent pas leur est retiré, un peu plus d'un point de
PIB. Elle suit le taux : le système 4 prélève ses {g.pourcentage(base.taux_cotisation_liberal, decimales=0)} sur
l'assiette mesurée des revenus d'activité au lieu de la part cotisée des
ressources d'aujourd'hui. Elle suit enfin le principe, et pour le seul
système 4 : un compte notionnel ne crédite que ce qui est assis sur un revenu
d'activité, et ce système ne reconduit donc aucune des trois ressources qui
n'acquièrent de droits à personne, celles que la note du dessus nomme. Trois
postes : 27 % des ressources en 2024, 29 % en 2070. Les cinq autres systèmes
les encaissent tous, faute qu'aucun programme dise ce qu'il en ferait.</div>

{_cout_note_restitution(contexte, annee, pib, annee_pib)}

<div class="note"><strong>Seul le système actuel sert la pension de
réversion.</strong> Une réversion est ce qu'un conjoint survivant reçoit de la
carrière d'un autre : la première dépense non contributive du système, un
dixième environ de tout ce qui est versé. Les systèmes notionnels comparés ici
retirent tous les avantages non contributifs, et celui-là comme les autres :
ils ne rendent que ce qui a été cotisé, et c'est précisément ce qu'ils servent
à mesurer. Le système actuel, lui, la sert, puisqu'il est le droit en vigueur.
Les systèmes qui ne valent que pour l'avenir la servent jusqu'à leur bascule,
n'étant jusque-là rien d'autre que le système actuel. Ensuite ils ne la
servent plus, aux veuves d'avant comme à celles d'après.</div>
""", identifiant="cout-postes")


#: L'écart de taux de la sensibilité, en fraction : un point de plus, un de
#: moins. Le seul réglage que la section montre, parce que le taux est la seule
#: chose qu'elle LIT au lieu de la calculer.
ECART_TAUX_DETTE = 0.01

#: Les systèmes que le graphique de la dette publique trace : le droit en
#: vigueur et la proposition, ceux entre lesquels la décision se prend. Les
#: deux notionnels « à droits constants » n'y sont pas — non qu'ils soient
#: cachés, leur stock est dans le graphique et le tableau du dessus, mais une
#: réserve de cinq fois le PIB posée sous une dette de 116 % dessine un pays
#: qui aurait remboursé quatre fois sa dette, ce qu'aucun système notionnel ne
#: ferait, le coefficient d'équilibre rendant cette marge aux pensions ; et
#: l'échelle qu'elle imposerait écraserait l'écart qui compte.
SYSTEMES_DETTE_PUBLIQUE: tuple[str, ...] = ("actuel", "notionnel_liberal")


def _cout_detail_dette(contexte: Contexte) -> str:
    """Ce que le déficit accumule : la dette, si rien ne s'ajuste.

    LE SOLDE DIT LE FLUX, CETTE SECTION DIT LE STOCK. La section précédente
    donne, année par année, ce qui manque ou ce qui reste ; celle-ci cumule,
    avec intérêts, et rapporte le cumul à un PIB qui grandit. C'est la
    récurrence de toute dette publique, et elle ajoute une chose que le solde
    ne montre pas : l'effet boule de neige, quand le taux dépasse la
    croissance.

    ELLE PART DE ZÉRO, à la dernière année observée, et ne compte donc ni la
    dette ni les réserves que le système porte aujourd'hui : elle dit ce que
    les soldes À VENIR ajoutent, jamais ce que le système détient.

    UN STOCK NÉGATIF EST UNE RÉSERVE, et le graphique descend sous l'axe pour
    le montrer — c'est le seul du site à le faire. Les deux systèmes notionnels
    « à droits constants » encaissent plus qu'ils ne servent : leur courbe
    plonge, et ce n'est pas une économie mais la marge que le coefficient
    d'équilibre aurait à distribuer, comme la section précédente le dit du
    coefficient lui-même.

    LE TAUX EST LU, PAS CHOISI : le forward à un an de la courbe sans risque de
    la BCE, celui-là même auquel le pilier capitalisé du système 4 place ses
    versements. La seule sensibilité montrée est donc celle-là — un point de
    taux en plus ou en moins —, en deux colonnes de plus dans le tableau.

    PUIS LA DETTE DU PAYS, POUR L'ÉCHELLE. Un second graphique pose la dette
    des administrations publiques, telle que l'INSEE la publie depuis 1995,
    et la prolonge à plat, en part de PIB, en y ajoutant le seul stock du
    système de retraite : le droit en vigueur d'un côté, la proposition de
    l'autre. Ce n'est pas une prévision de la dette publique — le reste du
    budget n'est pas modélisé —, c'est ce qui permet de lire un stock de
    soixante points de PIB à l'échelle des cent seize que le pays porte déjà,
    et de voir, d'un coup d'œil, si la proposition fait mieux ou moins bien
    que le système actuel.
    """
    cout = contexte.cout()
    dette = cout.dette
    if not dette.annees:
        return ""
    solde = cout.solde
    avenir = cout.avenir
    courbe = contexte.simulateur().courbe_taux
    depart = dette.annee_depart
    fin = dette.derniere_annee
    moins = calculer_dette(solde, avenir, courbe, -ECART_TAUX_DETTE)
    plus = calculer_dette(solde, avenir, courbe, ECART_TAUX_DETTE)
    annees = tuple(range(depart, fin + 1))
    series = tuple(
        g.Serie(
            libelle,
            tuple(dette.stock(scenario, annee) * 100 for annee in annees),
            COULEURS_SCENARIOS[scenario],
            scenario == "notionnel_liberal",
        )
        for scenario, libelle in SCENARIOS_COMPARES
    )
    trace = g.graphique(
        f"Ce que le solde de chaque système accumule de {depart} à {fin}, "
        "en part du PIB — une dette au-dessus de l'axe, une réserve en dessous",
        annees, series, "% du PIB", False, 0, True, None, "",
        tuple(libelle.split(".")[0] for _, libelle in SCENARIOS_COMPARES),
        "Année", None, "", 1,
    )
    lignes = []
    for scenario, libelle in SCENARIOS_COMPARES:
        lignes.append([
            _nom_scenario(scenario, libelle),
            g.pourcentage(dette.horizon(scenario), signe=True, decimales=0),
            g.pourcentage(dette.annees[-1].interet(scenario), signe=True,
                          decimales=1),
            g.pourcentage(moins.horizon(scenario), signe=True, decimales=0),
            g.pourcentage(plus.horizon(scenario), signe=True, decimales=0),
        ])
    premiere = dette.annees[0]
    cotee = dette.annee(dette.derniere_annee_cotee) or dette.annees[-1]
    publique = _cout_dette_publique(dette, fin)
    return g.depliant(
        "Ce que le déficit accumule : la dette, si rien ne s'ajuste", f"""
<p>Un solde est un flux : ce qui manque une année, ou ce qui reste. Un déficit
qui se répète devient un <strong>stock</strong>, et un stock porte intérêt.
Cette section cumule, à compter de {depart}, le solde de chaque système :
chaque année, ce qui manque est emprunté et ce qui reste est placé, au taux à
un an que la courbe des taux sans risque de la zone euro cote pour cette
année-là ; le stock est rapporté au PIB, qui grandit au rythme de la
projection. Il part de zéro. Ni la dette ni les réserves que le système porte
aujourd'hui n'y sont : la courbe dit ce que les soldes à venir ajoutent, jamais
ce que le système détient.</p>

{trace}

<p><strong>Les déficits du système actuel, simplement additionnés de
{premiere.annee} à {fin}, font
{g.pourcentage(dette.cumul_soldes("actuel"), decimales=0)} du PIB.</strong>
Avec les intérêts, et une fois le tout rapporté à un PIB qui grandit, la dette
atteint {g.pourcentage(dette.horizon("actuel"), decimales=0)} du PIB en {fin},
et ses seuls intérêts coûtent cette année-là
{g.pourcentage(dette.annees[-1].interet("actuel"), decimales=1)} du PIB. Elle
s'ajouterait à celle que le pays porte déjà, que le second graphique pose
dessous. La proposition, qui fixe le taux à 18 % et ne fixe pas les pensions,
en accumule {g.pourcentage(dette.horizon("notionnel_liberal"), decimales=0)} du
PIB au même horizon.</p>

{g.tableau(
    ["Système", f"Dette en {fin}", f"Intérêts de l'année {fin}",
     "Taux un point plus bas", "Taux un point plus haut"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
    titre=f"Stock accumulé par chaque système en {fin}, en part du PIB, "
    "et ce qu'un point de taux y change",
    entete_de_ligne=True,
)}
<p class="discret">Tout est en part du PIB. Un chiffre négatif est une
réserve : le système a encaissé plus qu'il n'a servi, et le stock lui rapporte
au lieu de lui coûter. Les deux dernières colonnes refont le calcul avec un
taux plus bas, puis plus haut, d'un point sur toute la période.</p>

<div class="note"><strong>Un système notionnel n'accumule ni cette dette ni
cette réserve.</strong> Il se règle chaque année par le coefficient
d'équilibre, que la section précédente calcule et que cette page n'applique
jamais. La courbe d'un système qui plonge sous l'axe mesure la marge que ce
coefficient aurait à distribuer, celle d'un système qui monte mesure ce qu'il
faudrait rogner, ou financer autrement. Le système actuel, lui, ne se règle
pas : il attend une réforme, et la courbe dit ce que coûte l'attente.</div>
{publique}
<div class="note"><strong>Le taux est lu, pas choisi.</strong> C'est le taux à
un an que la courbe des souverains les mieux notés de la zone euro, publiée par
la Banque centrale européenne le {_date_en_clair(dette.date_courbe)}, implique pour
chaque année : {g.pourcentage(premiere.taux, decimales=1)} en
{premiere.annee}, {g.pourcentage(cotee.taux, decimales=1)} en {cotee.annee}, la
dernière année que la courbe cote ; au-delà, il est prolongé à plat. C'est la
même courbe qui fait le rendement du pilier capitalisé du système 4 : la dette
et le pilier lisent le même marché, et personne n'a eu à prévoir un taux. Un
point de plus ou de moins déplace la dette du système actuel en {fin} de
{g.pourcentage(moins.horizon("actuel"), decimales=0)} à
{g.pourcentage(plus.horizon("actuel"), decimales=0)} du PIB.</div>
""",
        identifiant="cout-dette",
    )


def _cout_dette_publique(dette, fin: int) -> str:
    """La dette du pays, et ce que chaque système y ajoute : l'échelle du stock.

    LA DETTE OBSERVÉE D'ABORD, telle que l'INSEE la publie au sens de
    Maastricht — toutes administrations publiques, brute, consolidée — depuis
    1995 et jusqu'à l'année de départ ; PUIS, à compter de là, cette dette
    tenue à plat en part de PIB, à laquelle chaque système ajoute son seul
    stock. Deux systèmes, ceux entre lesquels la décision se prend ; les deux
    autres sont dans le graphique et le tableau du dessus, et la constante
    ``SYSTEMES_DETTE_PUBLIQUE`` dit pourquoi ils ne sont pas ici.

    L'HYPOTHÈSE EST DITE, PAS CACHÉE : le reste des administrations publiques
    a son propre solde, que le site ne modélise pas. Une dette qui monterait
    pour d'autres raisons décalerait les courbes d'un même bloc sans changer
    leur écart, et c'est cet écart — ce que la proposition ajoute ou retire
    par rapport au droit en vigueur — que le graphique donne à lire.
    """
    observee = dette.dette_publique_observee
    if not observee:
        return ""
    depart = dette.annee_depart
    annee_dette = dette.annee_dette_publique
    premiere_observee = min(observee)
    annees = tuple(range(premiere_observee, fin + 1))
    courbes = [g.Serie(
        "Dette publique observée, toutes administrations",
        tuple(observee[annee] * 100 if annee in observee else None
              for annee in annees),
        "var(--serie-1)",
        glose="INSEE, au sens de Maastricht",
    )]
    for scenario in SYSTEMES_DETTE_PUBLIQUE:
        courbes.append(g.Serie(
            LIBELLES_SYSTEMES[scenario],
            tuple(dette.dette_publique(scenario, annee) * 100
                  if annee >= depart else None for annee in annees),
            COULEURS_SCENARIOS[scenario],
            scenario == "notionnel_liberal",
            glose="la dette tenue à plat, plus le stock du système",
        ))
    trace = g.graphique(
        f"La dette publique de {premiere_observee} à {annee_dette}, puis ce "
        f"que le système actuel et la proposition y ajoutent jusqu'en {fin}, "
        "en part du PIB",
        annees, tuple(courbes), "% du PIB", False, 0, True, depart,
        "projection",
        ("",) + tuple(LIBELLES_SYSTEMES[scenario].split(".")[0]
                      for scenario in SYSTEMES_DETTE_PUBLIQUE),
        "Année", None, "", 0,
    )
    actuel = dette.dette_publique("actuel", fin)
    proposition = dette.dette_publique("notionnel_liberal", fin)
    ecart = proposition - actuel
    if abs(ecart) < 0.005:
        lecture = "la proposition et le système actuel laissent le pays au même point"
    elif ecart > 0:
        lecture = (
            f"la proposition laisse le pays {g.pourcentage(ecart, decimales=0)} "
            "du PIB plus endetté que le système actuel"
        )
    else:
        lecture = (
            f"la proposition laisse le pays {g.pourcentage(-ecart, decimales=0)} "
            "du PIB moins endetté que le système actuel"
        )
    return f"""
<p>Ce stock ne part pas de rien : le pays porte déjà une dette. Le graphique
suivant la pose dessous. D'abord la dette des administrations publiques au
sens de Maastricht (État, collectivités, Sécurité sociale), telle que
l'INSEE la publie de {premiere_observee} à {annee_dette} ; puis, à compter de
{depart}, cette dette tenue à son niveau de {annee_dette} en part du PIB, à
laquelle chaque système ajoute son seul stock, tel que le graphique du dessus
le cumule. C'est l'échelle qui manquait : ce que le système de retraite
ajoute se lit à côté de ce que le pays doit déjà.</p>

{trace}

<p><strong>La dette publique faisait
{g.pourcentage(dette.dette_publique_depart, decimales=0)} du PIB fin
{annee_dette}.</strong> Si rien d'autre ne bougeait, le système actuel la
porterait à {g.pourcentage(actuel, decimales=0)} du PIB en {fin}, et la
proposition à {g.pourcentage(proposition, decimales=0)} : {lecture}. L'écart
entre les deux courbes est exactement l'écart entre les deux stocks du
graphique précédent, et c'est lui qui se lit ici, à l'échelle du pays.</p>

<div class="note"><strong>Ce n'est pas une prévision de la dette
publique.</strong> Le reste des administrations publiques (l'État hors
retraite, les collectivités, l'assurance maladie) a son propre solde, que ce
site ne modélise pas. La dette est donc tenue à plat, en part du PIB, à son
niveau de {annee_dette}, et seule la retraite la déplace. Une dette qui
monterait, ou baisserait, pour d'autres raisons décalerait les deux courbes
d'un même bloc sans changer leur écart. Les systèmes 2 et 3 ne sont pas
tracés : leur réserve, posée sous cette dette, dessinerait un pays qui l'a
remboursée plusieurs fois, ce qu'aucun système notionnel ne ferait puisque le
coefficient d'équilibre rend cette marge aux pensions ; et son échelle
écraserait l'écart qui compte. Leur stock est dans le tableau.</div>
"""


def _cout_detail_frise(contexte: Contexte) -> str:
    """La frise des flux : chaque année, ce qui rentre, ce qui sort, ce qui reste.

    LA SECTION PRÉCÉDENTE DONNE LA COURBE ; CELLE-CI DONNE LE REGISTRE. Une
    colonne par année et par système, où l'on voit passer l'argent : ce qui
    rentre dans la caisse, ce qui en sort, et le pied de la caisse — emprunté
    quand il manque, placé quand il reste — qui va grossir ou réduire le stock
    écrit dessous. Le stock au 1er janvier est celui du 31 décembre précédent,
    rapporté au PIB de l'année : c'est ce qui fait que chaque colonne tombe
    juste, au dixième près, avec les mêmes nombres que la courbe.

    Un système à la fois, par les mêmes onglets que les grilles de Cas types :
    quatre frises rendues, une seule visible, et le premier onglet reste
    visible là où ``:has()`` n'existe pas.
    """
    cout = contexte.cout()
    dette = cout.dette
    if not dette.annees:
        return ""
    solde = cout.solde
    depart = dette.annee_depart
    fin = dette.derniere_annee

    def frise(scenario: str, libelle: str) -> str:
        lignes = []
        precedent = 0.0
        for ligne in dette.annees:
            bilan = solde.annee(ligne.annee)
            lignes.append(g.AnneeFrise(
                ligne.annee,
                bilan.ressources_de(scenario) * 100,
                bilan.depense(scenario) * 100,
                ligne.interet(scenario) * 100,
                precedent / (1.0 + ligne.croissance) * 100,
                ligne.stock(scenario) * 100,
                ligne.croissance,
            ))
            precedent = ligne.stock(scenario)
        return g.frise_flux(
            f"Ce qui rentre, ce qui sort et ce qui s'accumule chaque année de "
            f"{dette.premiere_annee} à {fin}, {libelle}",
            tuple(lignes),
        )

    onglets = "".join(
        f'<input type="radio" name="grille" id="grille-{scenario}"'
        + (" checked" if rang == 0 else "")
        + f'><label for="grille-{scenario}">{escape(libelle.split(". ", 1)[1])}</label>'
        for rang, (scenario, libelle) in enumerate(SCENARIOS_COMPARES)
    )
    panneaux = "".join(
        f'<div class="panneau" data-onglet="{scenario}"'
        + ("" if rang == 0 else " hidden") + ">"
        + f"<h3>{escape(libelle)} {_badge_scenario(scenario)}</h3>"
        + frise(scenario, libelle.split(". ", 1)[1].lower()) + "</div>"
        for rang, (scenario, libelle) in enumerate(SCENARIOS_COMPARES)
    )
    return g.depliant(
        "La frise des flux : chaque année, ce qui rentre, ce qui sort, ce qui reste", f"""
<p>La courbe de la section précédente se lit ici colonne par colonne, une par
année, comme un registre. À gauche <strong>ce qui rentre</strong> dans la
caisse, à droite <strong>ce qui sort</strong>, au milieu la caisse elle-même,
aussi haute que le plus grand des deux : son pied est rouge quand il manque de
l'argent, et cet argent est emprunté ; vert quand il en reste, et cet argent
est placé. Dessous, en chiffres, le stock : ce qu'il était au 1er janvier,
les intérêts de l'année, l'emprunt ou le placement, et ce qu'il est au 31
décembre. Chaque colonne tombe juste : le 31 décembre d'une année, rapporté au
PIB de la suivante, est son 1er janvier.</p>
<p class="discret">Tout est en part du PIB de l'année, comme sur la courbe. Le
stock n'est pas dessiné à l'échelle des flux, dont il vaut jusqu'à cinquante
fois la hauteur : il est écrit. Un stock négatif est une réserve, et ses intérêts lui
rapportent au lieu de lui coûter. La frise défile de {depart + 1} à {fin} ;
ses chiffres sont redits, ligne par ligne, dans le tableau replié dessous.</p>
<fieldset class="onglets"><legend>Système affiché</legend>{onglets}</fieldset>
<div class="panneaux">{panneaux}</div>
""",
        identifiant="cout-frise",
    )


def _cout_detail_garantie(contexte: Contexte) -> str:
    """Ce que la garantie vieillesse coûte, lue sur la vraie distribution.

    La trajectoire de la page la porte déjà : c'est la ligne « s'ajoute au
    système 4 » des deux tableaux. Ce dépliant dit d'où elle vient — la distribution des
    pensions de l'EIR, déplacée année par année par la grille —, ce qu'elle
    coûterait à pensions inchangées, et ce qu'elle REMPLACE : quatre minima
    que l'impôt et les caisses paient déjà, dont le premier est réclamé par la
    moitié seulement de ceux qui y ont droit.

    Les quatre y sont, minimum garanti de la fonction publique compris. Ce
    tableau montre le SYSTÈME ACTUEL, plancher par plancher, et ce que la
    garantie met à leur place : le programme n'en laisse qu'un. Qui paie
    aujourd'hui — l'impôt pour l'ASPA, les régimes pour les deux minima de
    pension — ne change pas ce que le lecteur veut savoir, qui est ce que
    l'ensemble coûte avant et après.
    """
    cout = contexte.cout()
    distribution = contexte.distribution()
    simulateur = contexte.simulateur()
    base = contexte.base
    millesime = distribution.millesime
    effectif_retraites = simulateur.effectifs.effectif("tous_regimes", millesime)
    vers_enquete = simulateur.macro.coefficient_prix(
        base.annee_euros_garantie_vieillesse, millesime)
    annee_enquete = cout.annee(millesime)
    facteur = annee_enquete.garantie.facteur if annee_enquete.garantie else 1.0
    taux = base.taux_recours_garantie
    seul = base.situation_foyer is SituationFoyer.SEUL
    planchers = (
        ("Plancher de base, 800 € (vie à deux)", base.garantie_vieillesse_mensuelle),
        ("Plancher majoré, 1 050 € (personne seule)",
         base.garantie_vieillesse_mensuelle + base.allocation_isolement_mensuelle),
    )
    # CE QUE LE DÉPLACEMENT UNIFORME CACHE, chiffré plutôt qu'affirmé. Aucun
    # nombre n'est écrit en toutes lettres dans la note : les deux lectures
    # sont calculées ici, sous le facteur et le plancher de la page.
    plancher_seul = (base.garantie_vieillesse_mensuelle
                     + base.allocation_isolement_mensuelle) * vers_enquete
    caracteristiques = simulateur.caracteristiques
    rapport_mesure = caracteristiques.rapport_deplacement()
    par_sexe = {
        rapport: cout_garantie_par_sexe(
            simulateur.distributions_par_sexe["F"],
            simulateur.distributions_par_sexe["H"],
            caracteristiques.part_femmes, effectif_retraites, plancher_seul,
            facteur, rapport)
        for rapport in (1.0, rapport_mesure)
    }
    # CE QUE LES MINIMA APPORTERAIENT À CE RAPPORT, chiffré plutôt que nommé.
    # Les effectifs de bénéficiaires sont lus ; la masse vient du modèle, qui
    # l'isole dans la cascade du scénario 1, faute qu'aucune série ne la
    # publie — c'est pourquoi ce terme est chiffré et non retenu dans ``r``.
    annee_enquete_avantages = next(
        (ligne for ligne in contexte.avantages().annees
         if ligne.annee == millesime), None)
    masse_minima = sum(
        annee_enquete_avantages.lignes.get(cle, 0.0)
        for cle in ("minimum_contributif", "minimum_garanti")
    ) if annee_enquete_avantages is not None else 0.0
    beneficiaires_minima = {
        sexe: caracteristiques.beneficiaires_minimum(sexe) * 1e3
        for sexe in ("F", "H")
    }
    total_minima = sum(beneficiaires_minima.values())
    montant_minima = masse_minima * 1e6 / total_minima if total_minima else 0.0
    part_minima = {
        sexe: beneficiaires_minima[sexe] * montant_minima / (
            caracteristiques.valeur("effectifs", sexe) * 1e3
            * caracteristiques.valeur("pension_droit_direct", sexe) * 12.0)
        for sexe in ("F", "H")
    }
    rapport_minima = (1.0 - part_minima["F"]) / (1.0 - part_minima["H"])
    par_sexe[rapport_mesure * rapport_minima] = cout_garantie_par_sexe(
        simulateur.distributions_par_sexe["F"],
        simulateur.distributions_par_sexe["H"],
        caracteristiques.part_femmes, effectif_retraites, plancher_seul,
        facteur, rapport_mesure * rapport_minima,
    )
    cout_uniforme = par_sexe[1.0].cout_annuel_meur
    ecart_mesure = (
        par_sexe[rapport_mesure].cout_annuel_meur / cout_uniforme - 1.0
        if cout_uniforme > 0.0 else 0.0
    )

    def _cout_par_sexe(rapport: float) -> str:
        return _milliards(
            par_sexe[rapport].cout_annuel_meur * taux / vers_enquete, 1)

    assiettes = (
        (f"Pensions de {millesime}", 1.0),
        (f"Pensions du système 4 en {millesime}", facteur),
    )
    lignes = []
    for titre_assiette, facteur_assiette in assiettes:
        for titre_plancher, mensuel in planchers:
            chiffre = cout_garantie(
                distribution, effectif_retraites, mensuel * vers_enquete, facteur_assiette)
            lignes.append([
                escape(f"{titre_assiette} — {titre_plancher}"),
                g.pourcentage(chiffre.part_beneficiaires, decimales=1),
                g.nombre(chiffre.beneficiaires * taux / 1e6, 1) + " M",
                g.euros(chiffre.complement_moyen_mensuel / vers_enquete),
                _milliards(chiffre.cout_annuel_meur * taux / vers_enquete, 1),
            ])
    garantie_basse = cout_garantie(
        distribution, effectif_retraites,
        base.garantie_vieillesse_mensuelle * vers_enquete, 1.0)
    garantie_scenario = cout_garantie(
        distribution, effectif_retraites,
        base.garantie_vieillesse_mensuelle * vers_enquete, facteur)

    # La trajectoire, à quelques dates : ce que la ligne « s'ajoute au
    # système 4 » des tableaux du haut contient, et pourquoi elle décroît.
    derniere = contexte.depenses().derniere_annee
    etapes = []
    for millesime_etape in (millesime, derniere, 2030, 2050, cout.avenir.derniere_annee):
        ligne = cout.avenir.annee(millesime_etape)
        if ligne is None or ligne.garantie is None or millesime_etape in [e[0] for e in etapes]:
            continue
        etapes.append((millesime_etape, ligne))
    lignes_etapes = [
        [str(annee),
         g.nombre(ligne.garantie.facteur, 2),
         g.nombre(ligne.garantie.effectif / 1e6, 1) + " M",
         g.nombre(ligne.garantie.ayants_droit / 1e6, 1) + " M",
         g.nombre(ligne.garantie.beneficiaires / 1e6, 1) + " M",
         _milliards(ligne.cout_constants(COMPOSANTE_GARANTIE), 1),
         g.pourcentage(ligne.part_pib(COMPOSANTE_GARANTIE), decimales=2)]
        for annee, ligne in etapes
    ]

    # La reprise sur succession, année par année : les avances que la garantie
    # constitue à compter de la bascule, ce que les décès libèrent, ce que les
    # successions rendent, et ce qui reste à l'impôt.
    etapes_reprises = []
    for millesime_etape in (base.annee_bascule, 2030, 2040, 2050, 2060,
                            cout.avenir.derniere_annee):
        ligne = cout.avenir.annee(millesime_etape)
        if (ligne is None or ligne.garantie is None
                or millesime_etape < base.annee_bascule
                or millesime_etape in [e[0] for e in etapes_reprises]):
            continue
        etapes_reprises.append((millesime_etape, ligne))
    lignes_reprises = [
        [str(annee),
         _milliards(ligne.cout_constants(COMPOSANTE_GARANTIE), 1),
         _milliards(ligne.garantie.avances_liberees_constants, 1),
         _milliards(ligne.reprises_constants(), 1),
         _milliards(ligne.garantie_nette_constants(), 1),
         g.pourcentage(ligne.part_pib(COMPOSANTE_GARANTIE) - ligne.part_pib_reprises(),
                       decimales=2),
         _milliards(ligne.garantie.stock_avances_constants, 0)]
        for annee, ligne in etapes_reprises
    ]
    # La part que la succession couvre, telle que la trajectoire l'a retenue :
    # calculée sur le patrimoine des retraités, ou réglée.
    ligne_bascule = cout.avenir.annee(base.annee_bascule)
    garantie_bascule = ligne_bascule.garantie if ligne_bascule is not None else None
    part_reprise = garantie_bascule.part_reprise if garantie_bascule else 0.0
    duree_avances = garantie_bascule.duree_avances if garantie_bascule else 0.0
    part_femmes = garantie_bascule.part_femmes if garantie_bascule else 0.0
    avances_succession = (garantie_bascule.avances_par_succession
                          if garantie_bascule else 1.0)
    reprise_calculee = base.part_reprise_garantie is None
    origine_reprise = (
        "calculés sur le patrimoine des ménages retraités selon leur revenu"
        if reprise_calculee
        else "le réglage « Part de l'avance couverte par la succession »"
    )
    patrimoine = simulateur.patrimoine
    modestes = patrimoine.statistiques("retraites_q1")
    retraites = patrimoine.statistiques("retraites")
    # Le temps passé en couple après 65 ans, sur la table du vingtile des
    # bénéficiaires : ce qui regroupe deux avances sur une succession.
    vie_en_couple = simulateur.vie_en_couple
    population_garantie = (garantie_bascule.population_mortalite
                           if garantie_bascule else None)
    couple_h = vie_en_couple.part_moyenne(
        "H", list(simulateur.mortalite.courbe_survie(
            65, base.annee_bascule, "H", True, population_garantie)))
    couple_f = vie_en_couple.part_moyenne(
        "F", list(simulateur.mortalite.courbe_survie(
            65, base.annee_bascule, "F", True, population_garantie)))

    # Ce que la garantie remplace : les quatre minima, tels qu'ils coûtent la
    # dernière année observée. Le minimum vieillesse est LU dans les comptes,
    # les deux suivants sont calculés par le modèle sur la grille, le dernier
    # n'est pas chiffré — et la page le dit ligne par ligne. Les quatre sont
    # ceux du système actuel : le programme les supprime tous et n'en laisse
    # qu'un, la garantie.
    avantages = contexte.avantages().derniere
    montants = avantages.lignes if avantages else {}
    annee_minima = avantages.annee if avantages else derniere
    remplaces = (
        ("Minimum vieillesse (ASPA)", "minimum_vieillesse", "lu dans les comptes"),
        ("Minimum contributif", "minimum_contributif", "calculé sur la grille"),
        ("Minimum garanti de la fonction publique", "minimum_garanti",
         "calculé sur la grille"),
        ("Pension majorée de référence des exploitants", "pension_majoree_reference",
         "non chiffrée"),
    )
    total_remplace = sum(montants.get(code, 0.0) for _, code, _ in remplaces)
    lignes_remplaces = [
        [libelle, source,
         _milliards(montants[code], 2) if montants.get(code) else "—"]
        for libelle, code, source in remplaces
    ]
    garantie_brute = cout.annee(annee_minima).cout(COMPOSANTE_GARANTIE)
    lignes_remplaces.append(["<strong>Ce que ces quatre minima coûtent</strong>", "",
                             f"<strong>{_milliards(total_remplace, 1)}</strong>"])
    lignes_remplaces.append([f"Garantie vieillesse, aux pensions du système 4 en {annee_minima}",
                             "distribution, ci-dessus",
                             _milliards(garantie_brute, 1)])
    lignes_remplaces.append(["<strong>Ce que l'impôt paierait en plus</strong>", "",
                             f"<strong>{_milliards(garantie_brute - total_remplace, 1)}</strong>"])

    return g.depliant("Ce que coûte la garantie vieillesse", f"""
<p>La garantie du système 4 est <strong>différentielle</strong> : elle ne verse
que ce qui manque à une pension pour atteindre son plancher. Son coût est donc
tout entier celui de la <strong>queue basse de la distribution</strong> des
pensions, et treize carrières de référence ne décrivent pas une distribution.
La ligne « garantie vieillesse » des deux tableaux du haut n'est donc pas
tirée des cas types : elle est lue sur la distribution que l'échantillon
interrégimes de retraités de la DREES publie, par tranches de cent euros, pour
{millesime}. Les cas types ne servent qu'à dire <em>de combien cette
distribution bouge</em> d'une année à l'autre : la pension moyenne que la
garantie regarde (le compte notionnel plus la rente du pilier capitalisé, à
partir de 65 ans), rapportée à la pension moyenne du système actuel en
{millesime}. Ce facteur vaut {g.nombre(facteur, 2)} en {millesime} : les
pensions du système 4 y sont plus basses que celles servies, parce que le
compte rétroactif ne rend que ce qui a été cotisé. Il monte ensuite avec les
salaires, face à un plancher indexé sur les prix, et la garantie décroît.</p>

{g.tableau(
    ["Année", "Facteur de déplacement", "Retraités de 65 ans et plus",
     "Sous le plancher", "Bénéficiaires",
     "Coût annuel, milliards d'euros " + str(cout.annee_euros),
     "Part du PIB"],
    lignes_etapes,
    ["nombre", "nombre", "nombre", "nombre", "nombre", "nombre", "nombre"],
    titre=f"La garantie vieillesse dans la trajectoire, plancher "
          f"{'majoré (personne seule)' if seul else 'de base (vie à deux)'}",
    entete_de_ligne=True,
)}

<p><strong>Ce que les successions rendent.</strong> La garantie est une
avance : chaque euro versé depuis la bascule porte intérêt au taux réel que la
courbe des taux sans risque implique, une fois l'inflation retirée, et devient
une créance sur la succession. Le modèle suit ces avances par âge et les
libère au décès, avec la mortalité du vingtile de niveau de vie où la pension
moyenne des bénéficiaires les place, les deux sexes pesés comme ils le sont
sous le plancher, {g.pourcentage(part_femmes, decimales=0)} de femmes : une
avance dure {g.nombre(duree_avances, 1)} ans en moyenne.
La succession en couvre {g.pourcentage(part_reprise, decimales=0)}, {origine_reprise}. Ce que la succession ne couvre pas
est abandonné : c'est cette part-là, et elle seule, que l'impôt finance pour
de bon. Les lignes « dont reprises » et « garantie nette » des tableaux du
haut en viennent.</p>

<p class="discret">Le patrimoine des retraités selon leur pension n'est publié
nulle part. Le COR a publié, sur l'enquête Histoire de vie et Patrimoine 2018,
le patrimoine brut des ménages retraités selon leur revenu disponible : une
médiane de {g.euros(modestes['mediane'])} pour le quart le plus modeste, de {g.euros(retraites['mediane'])} pour
l'ensemble. Chaque tranche de pension sous le plancher reçoit l'avance qu'elle
constituerait, et la part que la succession en couvre est celle du quart le
plus modeste pour le premier quart des retraités, celle de l'ensemble à partir
de la médiane, et le mélange entre les deux ; la part retenue est la moyenne,
pesée par les avances.</p>

<p class="discret"><strong>Une succession porte {g.nombre(avances_succession, 2)} avances</strong>, et
c'est presque toujours celle de la femme. La règle reporte la reprise au décès
du conjoint survivant ; or un homme de 65 ans vit en couple {g.pourcentage(couple_h, decimales=0)} du
temps qui lui reste, une femme {g.pourcentage(couple_f, decimales=0)}, et le conjoint est lui aussi sous
le plancher assez souvent pour que les deux avances se retrouvent sur la même
succession. Le patrimoine du fichier étant celui d'un ménage, c'est bien ce
total-là qu'il affronte, et une avance deux fois plus grosse est moins bien
couverte, non mieux. Les pensions des deux conjoints sont supposées
indépendantes, ce qu'elles ne sont pas : la corrélation des revenus dans un
couple rendrait ce nombre plus grand. Deux choses que le calcul ne voit
toujours pas, faute du fichier individuel de l'enquête : une femme dont la
pension est basse vit souvent dans un ménage qui ne l'est pas — le calcul le
sait pour son espérance de vie, non pour son patrimoine —, et deux concubins
ne se succèdent pas l'un à l'autre, alors que le recensement les compte en
couple. Le réglage « Part de l'avance couverte par la succession » remplace
tout ce calcul par un nombre.</p>

{g.tableau(
    ["Année", "Versé", "Avances libérées par les décès", "Reprises",
     "Garantie nette", "Net en part du PIB", "Avances en cours"],
    lignes_reprises,
    ["nombre", "nombre", "nombre", "nombre", "nombre", "nombre", "nombre"],
    titre=f"La reprise sur succession dans la trajectoire, milliards d'euros "
          f"{cout.annee_euros}",
    entete_de_ligne=True,
)}

<p>Deux lectures à la date de l'enquête, et deux planchers. Ce que la garantie
coûterait <strong>aux pensions d'aujourd'hui</strong>, en remplacement de
l'ASPA, est un calcul qui ne doit rien au modèle ; ce qu'elle coûterait
<strong>aux pensions du système 4</strong> déplace toute la distribution du
facteur ci-dessus. Le plancher de base vaut pour qui vit à deux, le plancher
majoré pour qui vit seul, et l'enquête ne dit pas avec qui l'on vit : le coût
réel est entre les deux. La trajectoire retient
{'le plancher majoré' if seul else 'le plancher de base'}, celui que le
simulateur applique.</p>

<p><strong>Un ayant droit sur deux réclame.</strong> La garantie se demande,
comme l'ASPA, et le programme retient l'hypothèse que la DREES mesure sur
celle-ci : une personne seule éligible sur deux ne la réclame pas, la crainte
de la reprise sur succession étant le premier motif donné. Une avance reprise
dès le premier euro ne se réclamera pas davantage. Les bénéficiaires et les
coûts de ce dépliant, la ligne « s'ajoute au système 4 » des tableaux du haut et le
tableau poste par poste comptent donc {g.pourcentage(taux, decimales=0)} des ayants droit ; la part des
retraités sous le plancher, elle, est donnée entière. Le paramètre
<code>taux_recours_garantie</code> porte cette hypothèse, et un rend le recours
complet.</p>

{g.tableau(
    ["Assiette et plancher", "Sous le plancher", "Bénéficiaires",
     "Complément moyen",
     f"Coût annuel, milliards d'euros {base.annee_euros_garantie_vieillesse}"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
    titre=f"Coût annuel de la garantie vieillesse, barème appliqué à la "
          f"distribution des pensions de l'EIR {millesime}",
    entete_de_ligne=True,
)}

<p class="discret">Pensions <strong>brutes de droit direct</strong>, la seule des
huit distributions publiées qui soit dans la même grandeur que celles du modèle.
Les pensions d'une tranche de cent euros sont supposées y être réparties
uniformément, et la tranche ouverte du haut est traitée comme une masse
ponctuelle. Le déplacement est <em>proportionnel et uniforme</em>, alors que le
scénario ne déplace pas toutes les carrières du même rapport ; la forme de la
distribution est celle de {millesime}, tenue constante sur toute la série, le
passé comme l'avenir. Ce tableau applique le barème à tous les retraités de
{millesime} ; la trajectoire ne l'applique qu'à ceux de 65 ans et plus, d'où un
coût plus bas la même année.</p>

<div class="note"><strong>Les pensions des femmes tombent plus que celles des
hommes, et le modèle le mesure.</strong> Le système 4 retire les droits non
cotisés : assurance vieillesse des parents au foyer, chômage, maladie,
majorations de durée. Un compte notionnel ne crédite que ce qui a été cotisé,
or l'enquête dit quelle part de la carrière ne l'a pas été :
{g.pourcentage(caracteristiques.part_non_cotisee("F"), decimales=1)} chez les
femmes contre
{g.pourcentage(caracteristiques.part_non_cotisee("H"), decimales=1)} chez les
hommes. La majoration pour enfants corrige dans l'autre sens, étant
proportionnelle à la pension et donc un peu plus lourde chez les hommes
({g.pourcentage(caracteristiques.part_majorations("H"), decimales=1)} contre
{g.pourcentage(caracteristiques.part_majorations("F"), decimales=1)}). Reste un
rapport de {g.nombre(rapport_mesure, 3)} : les pensions des femmes tombent d'un
sixième de plus. Le tableau les déplace donc chacune du sien, la moyenne
d'ensemble restant déplacée du facteur que la grille donne. La convention
uniforme, celle d'avant le 21 septembre 2026, valait
{_cout_par_sexe(1.0)} là où celle-ci donne {_cout_par_sexe(rapport_mesure)} :
elle sous-estimait de {g.pourcentage(ecart_mesure, decimales=0)}. Les minima de
pension n'entrent pas dans ce rapport, et c'est le seul terme qui manque :
l'enquête en publie la part des bénéficiaires,
{g.pourcentage(caracteristiques.part_minimum_pension("F"), decimales=0)} des
femmes contre
{g.pourcentage(caracteristiques.part_minimum_pension("H"), decimales=0)} des
hommes, mais jamais ce qu'ils apportent, qu'il faut prendre au modèle. Ce
qu'ils pèsent est chiffré : {g.pourcentage(part_minima["F"], decimales=1)} de
la pension des femmes contre
{g.pourcentage(part_minima["H"], decimales=1)} de celle des hommes, ce qui
mènerait ce tableau à {_cout_par_sexe(rapport_mesure * rapport_minima)}. Moins
d'un pour cent de plus, et le minimum vieillesse ne fait rien du tout : il est
sur une ligne à part de la pension de droit direct, que ce barème déplace.</div>

<p><strong>Ce qu'elle remplace.</strong> <strong>La garantie est le seul
plancher du système 4</strong>, et c'est tout ce qu'il y a à retenir : elle
succède à l'ASPA, et le minimum contributif, le minimum garanti de la fonction
publique et la pension majorée de référence disparaissent avec elle. Quatre
planchers aujourd'hui, un seul demain. Le minimum garanti n'est gardé dans ce
tableau que pour montrer le système actuel : un fonctionnaire le perçoit, la
proposition le supprime comme les trois autres. Ce que l'impôt paierait
<em>en plus</em> est la garantie moins ces quatre-là.</p>

{g.tableau(
    ["Ligne", "D'où vient le chiffre", f"En {annee_minima}"],
    lignes_remplaces,
    ["", "texte", "nombre"],
    titre=f"Ce que la garantie vieillesse remplace, en {annee_minima}",
    entete_de_ligne=True,
)}

<p class="discret">Le minimum vieillesse est le poste des comptes de la
protection sociale ; les deux minima de pension sont calculés sur la grille des
cas types, qui n'est pas une population et les sous-estime : le minimum
contributif est réclamé par des carrières courtes que la grille ne compte
guère. La pension majorée de référence n'est pas chiffrée, aucun code du
moteur ne la servant. Le total est donc une borne basse, et l'écart une borne
haute.</p>

<div class="note"><strong>Deux corrections, et les deux sont dans la
page.</strong> L'ASPA est réclamée par <strong>une personne seule éligible
sur deux</strong> : fin 2016, 321 200 personnes vivaient sous son plafond sans
la demander, pour 790 millions d'euros non versés, soit 59 % des sommes servies
(DREES, <em>Les dossiers de la DREES</em> n° 97, mai 2022). Le tableau applique
le même recours à la garantie, un ayant droit sur deux : ce qu'elle coûte en
plus est compté ainsi, et le recours complet le doublerait. Dans le même sens,
la garantie est une <strong>avance reprise sur la succession</strong>, dès le
premier euro et avec intérêts, là où l'ASPA n'est récupérée qu'au-delà d'un
seuil d'actif net : le Fonds de solidarité vieillesse en a retiré 108,7
millions d'euros en 2024 (143,9 en 2023, avant le relèvement du seuil), deux
pour cent de ce qu'elle verse. La garantie touche une population bien plus
large, et souvent propriétaire : la trajectoire suit ces avances et ce que
les successions en rendent, au taux de couverture du réglage, qui est une
hypothèse et non une donnée. La ligne « s'ajoute au système 4 » reste
<strong>brute, avant reprise</strong> ; les lignes « dont reprises » et
« garantie nette » disent le reste.</div>

<div class="note"><strong>La garantie n'est pas l'ASPA à un autre
montant.</strong> L'ASPA regarde <em>toutes les ressources du foyer</em> et ne
sert rien à un couple à 300 € et 1 500 € ; la garantie ne regarde que la pension
d'une personne, et sert 500 € au premier. C'est ce changement d'assiette, plus
encore que le montant, qui fait passer d'une allocation servie à quelques
centaines de milliers de personnes à une allocation ouverte à
{g.nombre(garantie_basse.beneficiaires / 1e6, 1)} millions de retraités aux
pensions d'aujourd'hui, et à
{g.nombre(garantie_scenario.beneficiaires / 1e6, 1)} millions à celles du
système 4, dont la moitié la réclamerait.</div>
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
    volontaire = base.taux_capitalisation_volontaire_applique
    impose = repartition_ + capitalise
    total = impose + volontaire
    # La ligne volontaire ne paraît que si elle existe : la retirer des
    # paramètres doit rendre au tableau la forme qu'il avait à deux lignes.
    ligne_volontaire = (
        [["Placé volontairement, les points rendus", "—",
          g.pourcentage(volontaire, decimales=0)]] if volontaire else []
    )
    trajectoire = _cout_pilier_trajectoire(contexte)
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
répartition, comme celui des trois autres. Il en va de même des
{g.pourcentage(volontaire, decimales=0)} que le cotisant peut ajouter de
lui-même : ils ne passent pas davantage par les caisses.</p>

{g.tableau(
    ["", "Aujourd'hui", "Système 4"],
    [
        ["Prélevé pour la répartition",
         g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0),
         g.pourcentage(repartition_, decimales=0)],
        ["Prélevé pour la capitalisation, obligatoire", "—",
         g.pourcentage(capitalise, decimales=0)],
    ] + ligne_volontaire + [
        ["Total imposé", g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0),
         g.pourcentage(impose, decimales=0)],
        ["Total versé si les points rendus sont replacés",
         g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0),
         f"<strong>{g.pourcentage(total, decimales=0)}</strong>"],
    ],
    ["", "nombre", "nombre"],
    titre="Ce que coûte la retraite à celui qui travaille, part salariale et "
          "patronale additionnées",
    entete_de_ligne=True,
)}

<p>Ce qui est <strong>imposé</strong> baisse de
{g.nombre((TAUX_ACTUEL_TOTAL - impose) * 100, 0)} points :
{g.pourcentage(impose, decimales=0)} contre
{g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)} aujourd'hui pour un salarié du
privé. La part qui finance les pensions des autres passe de
{g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)} à
{g.pourcentage(repartition_, decimales=0)} ; ce qui reste,
{g.pourcentage(capitalise, decimales=0)}, revient à celui qui l'a versé — sous
forme de rente à la retraite, ou de capital à ses héritiers s'il meurt
avant.</p>

<p><strong>Le simulateur, lui, montre la seconde ligne du total.</strong> Les
{g.nombre((TAUX_ACTUEL_TOTAL - impose) * 100, 0)} points rendus, il les suppose
remis au même compte, et l'effort revient alors à
{g.pourcentage(total, decimales=0)}, ce qu'il est déjà. C'est la seule façon de
comparer deux systèmes sans comparer en même temps deux niveaux d'effort : à ce
prix-là, {g.pourcentage(base.taux_capitalisation_applique, decimales=0)} des
{g.pourcentage(total, decimales=0)} appartiennent au cotisant et se
transmettent, contre rien aujourd'hui. Qui préfère garder ces points les garde,
et sa rente baisse de ce qu'ils auraient rapporté : la page de résultats écrit
les deux montants.</p>

{trajectoire}

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


#: Les années où la trajectoire du pilier est lue : la bascule, puis tous les
#: dix ans jusqu'à l'horizon.
_ETAPES_PILIER = (0, 4, 14, 24, 34, 44)


def _cout_pilier_trajectoire(contexte: Contexte) -> str:
    """Ce que le pilier de TOUS les cotisants collecte, prélève, détient et
    sert, année par année, sous le régime de frais réglé.

    LE NIVEAU VIENT DU COMPTE DU COR, PAS DE LA GRILLE. Les versements du
    pilier sont les cotisations du système 4 — 18 % de l'assiette, ancrés sur
    les ressources publiées — multipliées par le rapport des deux taux ; la
    grille ne fournit que des rapports par euro versé : frais, encours,
    rentes. C'est la règle de toute la page, et le pilier ne la contourne pas.
    """
    base = contexte.base
    cout = contexte.cout()
    avenir, solde = cout.avenir, cout.solde
    taux_liberal = base.taux_cotisation_liberal
    if not avenir.annees or not solde.annees or taux_liberal <= 0:
        return ""
    facteur = base.taux_capitalisation_applique / taux_liberal
    if facteur <= 0:
        return ""

    def niveaux(ligne):
        """Les grandeurs de l'année en millions d'euros constants, et la part
        de PIB des versements ; ``None`` si l'année n'a pas de pilier."""
        bilan = solde.annee(ligne.annee)
        if ligne.pilier is None or bilan is None or ligne.pib <= 0:
            return None
        part = bilan.postes_ressources("notionnel_liberal")["cotisations"] * facteur
        montants = ligne.pilier.niveaux(part * ligne.pib * ligne.coefficient_constants)
        montants["part_pib_versements"] = part
        montants["part_pib_encours"] = part * ligne.pilier.encours
        return montants

    bascule = base.annee_debut_capitalisation
    lignes = []
    for ecart in _ETAPES_PILIER:
        ligne = avenir.annee(bascule + ecart)
        montants = niveaux(ligne) if ligne is not None else None
        if montants is None:
            continue
        lignes.append([
            str(ligne.annee),
            _milliards(montants["versements"], 0),
            _milliards(montants["frais"], 1),
            g.pourcentage(ligne.pilier.taux_frais_encours, decimales=2),
            _milliards(montants["encours"], 0)
            + f" ({g.pourcentage(montants['part_pib_encours'], decimales=0)} du PIB)",
            _milliards(montants["rentes"], 0),
        ])
    cumuls = {"versements": 0.0, "frais": 0.0, "frais_accumulation": 0.0,
              "frais_rentes": 0.0, "rentes": 0.0}
    for ligne in avenir.projetees():
        montants = niveaux(ligne)
        if montants is None:
            continue
        for cle in cumuls:
            cumuls[cle] += montants[cle]
    if not lignes or cumuls["versements"] <= 0:
        return ""
    derniere = avenir.derniere_annee
    part_frais = cumuls["frais"] / cumuls["versements"]
    return f"""
<p><strong>Ce que le pilier collecte, ce que l'enveloppe prélève, ce qu'il
sert.</strong> Ce dépliant, lui, compte le pilier : pas dans le solde, qui
reste celui de la répartition, mais pour lui-même. Les versements sont les
cotisations du système 4 telles que le compte du COR les ancre, multipliées par
le rapport des deux taux ({g.pourcentage(base.taux_capitalisation_applique, decimales=0)}
contre {g.pourcentage(taux_liberal, decimales=0)}) ; frais, encours et rentes
viennent des carrières types, par euro versé, sous le réglage « Frais du
pilier capitalisé » de cette page : chaque versement entre au tarif de son
année, les paliers font baisser les tarifs, et la rente garde les frais de
l'année où elle est souscrite.</p>

{g.tableau(
    ["Année", "Versements", "Frais prélevés dans l'année", "Frais de gestion, en part de l'encours", "Encours", "Rentes servies"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre", "nombre"],
    titre=f"Le pilier de tous les cotisants, milliards d'euros de {cout.annee_euros}",
    entete_de_ligne=True,
)}

<p>De {avenir.premiere_annee_projetee} à {derniere}, le pilier collecte
{_milliards(cumuls["versements"], 0)} et l'enveloppe en prélève
{_milliards(cumuls["frais"], 0)}, soit
{g.pourcentage(part_frais, decimales=1)} des versements :
{_milliards(cumuls["frais_accumulation"], 0)} pendant l'accumulation, sur les
versements et sur l'encours, et {_milliards(cumuls["frais_rentes"], 0)} sur les
rentes, qui totalisent {_milliards(cumuls["rentes"], 0)} servis. Le taux de
frais rapporté à l'encours baisse au fil du tableau : c'est la trajectoire des
frais, et la part du stock qui la suit. Changer le réglage change ce tableau,
et lui seul sur cette page.</p>"""


def _cout_detail_poids(contexte: Contexte) -> str:
    """Ce que chaque carrière type pèse dans les agrégats de la page."""
    cout = contexte.cout()
    derniere = contexte.depenses().derniere_annee
    lignes = [
        [escape(cas.libelle),
         ", ".join(caisse.replace("_", " ") for caisse in cas.caisses),
         g.pourcentage(cout.poids.get(cas.code, 0.0), decimales=1),
         g.pourcentage(cout.poids_cotisants.get(cas.code, 0.0), decimales=1),
         g.pourcentage(1 / len(CAS_TYPES), decimales=1)]
        for cas in sorted(CAS_TYPES, key=lambda c: -cout.poids.get(c.code, 0.0))
    ]
    return g.depliant("Ce que chaque carrière type pèse dans ces chiffres", f"""
<p><strong>Deux pondérations se composent.</strong> Celle de la génération est
démographique, et vient de l'INSEE. Celle du <strong>cas type</strong> est
sociologique, et elle se lit des deux côtés du bilan : dans les
<strong>dépenses</strong>, un cas type pèse les retraités de sa caisse (combien
ont eu cette carrière-là), publiés par la DREES ; dans les
<strong>recettes</strong>, il pèse ses cotisants, publiés et projetés par le
COR. La colonne de droite rappelle ce que valait la convention antérieure, qui
les pesait à égalité.</p>

{g.tableau(
    ["Cas type", "Caisse dont il porte les effectifs",
     f"Retraités en {derniere}", f"Cotisants en {derniere}", "Ancienne convention"],
    lignes,
    ["", "texte", "nombre", "nombre", "nombre"],
    titre=f"Ce que chaque cas type pèse dans les agrégats de cette page, en {derniere}",
    entete_de_ligne=True,
)}
<p class="discret">Une caisse réclamée par plusieurs cas types se partage
également entre eux : la Cnav est celle des quatre carrières du privé, et aucune
source ne dit combien de ses retraités ont été cadres. Hors de la fenêtre que la
DREES publie (2004 à 2024), la répartition du bord est reconduite : la France
de 1960 comptait plus d'exploitants agricoles que ces poids ne le disent. Les
cotisants, eux, sont projetés jusqu'en 2070, et les régimes fermés s'y
éteignent : la SNCF n'en a plus aucun à cette date. La fonction publique d'État
n'y est publiée que d'un seul tenant, et se partage entre civils et militaires
à la clé du jaune budgétaire « Pensions », tenue constante.</p>
""", identifiant="cout-poids")


def _cout_detail_sources(contexte: Contexte) -> str:
    """Trois séries, trois périmètres, et pourquoi ils ne se confondent pas."""
    comptes = contexte.comptes()
    depenses = contexte.depenses()
    cout = contexte.cout()
    solde = cout.solde
    derniere = depenses.derniere_annee
    # La dernière année que les DEUX conventions portent : le bloc
    # complémentaire du COR s'arrête un an avant le compte principal, et
    # comparer deux années différentes ne dirait rien.
    annee_eec = min(comptes.derniere_annee_eec, comptes.derniere_annee)
    # L'année où l'effort figé passe au-dessus du besoin. Elle est ce qui
    # empêche de lire l'écart entre conventions comme un biais constant, et
    # elle se calcule : l'écrire en dur, c'est promettre le rapport de 2026.
    ecarts = {annee: comptes.solde_eec(annee) - comptes.solde(annee)
              for annee in range(comptes.premiere_annee_eec, annee_eec + 1)}
    croisement = next((a for a in sorted(ecarts) if ecarts[a] >= 0), annee_eec)
    # Le brut et le net, à l'échelle du compte. La masse des pensions est
    # celle que la DREES ventile en droit direct et droit dérivé : le total du
    # compte est plus large — frais de gestion, action sociale —, et la CSG ne
    # porte que sur ce qui est versé à quelqu'un.
    pensions_nettes = charger_prelevements(contexte.base.racine_donnees).pensions
    annee_masse = min(depenses.pensions_droits["direct"].derniere_annee, derniere)
    pib_masse = depenses.pib(annee_masse)
    masse_pensions = sum(depenses.pensions_droit(categorie, annee_masse)
                         for categorie in ("direct", "derive"))
    masse_brute = masse_pensions / pib_masse
    masse_nette = masse_brute * (1.0 - pensions_nettes.taux_total)
    masse_circulaire = masse_pensions * pensions_nettes.csg_affectee_vieillesse
    # Le stock, à côté des flux : les droits acquis à date du tableau
    # supplémentaire du SEC 2010. Les années sont lues et non déduites — une
    # transmission tous les trois ans, et rien entre les deux.
    annees_engagements = comptes.annees_engagements()
    annee_engagements = annees_engagements[-1]
    engagements_dernier = comptes.engagements(annee_engagements)
    engagements_serie = ", ".join(
        f"{g.pourcentage(comptes.engagements(annee), decimales=0)} en {annee}"
        for annee in annees_engagements
    )
    # Le nôtre, figé sous les réglages de référence comme le reste du bilan :
    # sommer quatre-vingts années de flux chez le lecteur n'est pas possible.
    engagement = contexte.bilan().engagements
    ecart_publie = engagement.ecart_pour(engagement.publie) if engagement else None
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
<p class="discret"><strong>Et sous une convention, qui est une hypothèse.</strong>
Le compte est tenu en « équilibre permanent des régimes » : ce que l'État verse
au régime de ses fonctionnaires et aux régimes spéciaux y suit, année par
année, ce qu'il faut pour les équilibrer. Ces régimes ne montrent donc jamais
de déficit, et le {g.pourcentage(comptes.solde(annee_eec), signe=True, decimales=1)}
du PIB affiché pour {annee_eec} est un déficit APRÈS ce bouclage, non avant. Le
COR publie aussi l'autre convention, où l'effort de l'État est figé en part de
PIB : le solde y serait de
{g.pourcentage(comptes.solde_eec(annee_eec), signe=True, decimales=1)}. L'écart
change de signe : l'effort figé est SOUS le besoin jusqu'en {croisement}, et
au-dessus ensuite. Aucune des deux ne flatte ; elles déplacent
le déficit dans le temps, et l'État n'a promis ni l'une ni l'autre.</p>
<p class="discret"><strong>Et en BRUT, des deux côtés.</strong> Les pensions
comptées ici sont celles qui sont versées, avant la contribution sociale
généralisée, la CRDS et la CASA. Au taux plein, ces trois-là prélèvent
{g.pourcentage(pensions_nettes.taux_total, decimales=1)} d'une pension : la
masse nette vaut donc au plus
{g.pourcentage(masse_nette, decimales=2)} du PIB en {annee_masse}, contre
{g.pourcentage(masse_brute, decimales=2)} en brut. « Au plus », parce que les
pensions modestes en sont exonérées ou au taux réduit, et que le dépôt ne sait
pas dire combien le sont : il faudrait le revenu fiscal du foyer, que personne
ne publie par tranche de pension.</p>
<p class="discret"><strong>Et une part de la recette est prélevée sur la
dépense.</strong> L'article L. 131-8 du code de la sécurité sociale reverse
{g.nombre(pensions_nettes.csg_affectee_vieillesse * 100, 2)} des
{g.nombre(pensions_nettes.csg_taux_plein * 100, 2)} points de CSG d'une pension
à la branche vieillesse : un tiers de ce qu'une pension paie revient au système
qui la verse. Au taux plein, cela fait au plus
{_milliards(masse_circulaire)} en {annee_masse}, soit
{g.pourcentage(masse_circulaire / pib_masse, decimales=2)} du PIB et le
cinquième des impôts et taxes que le compte encaisse. Le COR ne se trompe pas
en les comptant tous les deux, un compte d'encaissements le doit ; mais qui lit
« dépenses » et « ressources » comme deux grandeurs indépendantes se trompe de
cette somme-là.</p>
<p class="discret"><strong>Et tout cela est un FLUX.</strong> Ce qui rentre et
ce qui sort dans l'année. L'autre moitié d'un compte est ce que le système doit
DÉJÀ, au titre des droits que les vivants ont acquis : le règlement européen sur
les comptes nationaux le fait publier tous les trois ans, et pour la France il
vaut {g.pourcentage(engagements_dernier, decimales=0)} du PIB en
{annee_engagements}, presque tout par répartition : <strong>près de quatre
années de production</strong>, contre quatorze pour-cent de dépense annuelle. Ce n'est pas une
dette : un droit acquis à date est une somme actualisée, et les trois
transmissions donnent {engagements_serie}. Soixante points de PIB d'écart sans
qu'aucun droit ait changé : c'est le taux qui les actualise qui a bougé. L'ordre de
grandeur est tout ce qu'on en retient.</p>
<p class="discret"><strong>Et le dépôt calcule le sien.</strong> Sous la
convention du COR, dont la note dit que « le taux d'actualisation est supposé
égal chaque année à la croissance annuelle du PIB », actualiser revient à
sommer les flux en part de PIB : le modèle porte donc l'engagement sans
convention de plus. Il trouve
{g.pourcentage(engagement.part_pib(), decimales=0)} du PIB en {engagement.annee}
pour le système actuel, dont
{g.pourcentage(engagement.retraites, decimales=0)} déjà liquidés et
{g.pourcentage(engagement.actifs, decimales=0)} au prorata des carrières en
cours. La proposition en doit
{g.pourcentage(engagement.part_pib("notionnel_liberal"), decimales=0)} : elle
promet moins, elle doit moins.</p>
<p class="discret"><strong>Et l'écart avec les
{g.pourcentage(engagement.publie, decimales=0)} publiés est un TAUX, pas un
droit.</strong> Les mêmes droits, actualisés
{g.nombre(ecart_publie * 100, 1)} point{"s" if ecart_publie * 100 >= 2 else ""} de plus par an, valent exactement ce
que le tableau européen publie. Ni l'un ni l'autre n'est faux : un engagement
acquis n'a pas de niveau propre, il a un taux. C'est pourquoi le dépôt affiche
les deux et ne choisit pas.</p>

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


def part_reprise_bascule(contexte: Contexte) -> float:
    """La part de l'avance que la succession couvre, telle que la trajectoire
    l'a retenue l'année de la bascule — calculée ou réglée."""
    ligne = contexte.cout().avenir.annee(contexte.base.annee_bascule)
    return ligne.garantie.part_reprise if ligne is not None and ligne.garantie else 0.0


def _cout_detail_limites(contexte: Contexte) -> str:
    """Ce que cette page laisse de côté, et que le lecteur ne peut ni régler ni
    lire ailleurs. Ce qui se règle est dit sous son réglage, ce qui décrit un
    système est dans le dépliant de ce système ; un test plafonne la liste,
    pour que la prochaine réserve en fusionne une plutôt que d'en ajouter une.
    Le titre ne compte plus : à quatorze, le compteur était devenu un aveu."""
    cout = contexte.cout()
    solde = cout.solde
    avenir = cout.avenir
    observe = solde.annee(solde.derniere_annee_observee)
    return g.depliant("À lire avant de citer ces chiffres", f"""
<p>Une page de chiffres vaut par ce qu'elle laisse de côté. Rien de ce qui
suit n'est certifié, et ne peut l'être : une projection est une hypothèse,
celle de l'INSEE pour la démographie, celle du COR pour la macroéconomie,
celle du modèle pour les pensions, jusqu'en {avenir.derniere_annee}, horizon des
projections de population, et pas un an de plus. Ce qui se règle est dit sous
son réglage : les pensions en cours à la bascule, la part de l'avance que la
succession couvre. Ce qui décrit un système est dans le dépliant de ce
système : ce que la recette suit, à qui la réversion est servie, ce que le
coefficient d'équilibre ferait. Restent ici les réserves que le lecteur ne
peut ni changer ni lire ailleurs.</p>
<ul class="serree">
  <li><strong>La projection est celle du COR</strong>, scénario de référence,
  avec ses hypothèses : démographie de l'INSEE, productivité, chômage. Ses
  ressources reculent en part de PIB parce que l'assiette des cotisations y
  progresse moins vite que le PIB : cette hypothèse est la sienne, et personne
  ne l'a mesurée. Seize autres scénarios démographiques existent, dont l'écart
  mesurerait l'incertitude ; cette page n'en montre aucun.</li>
  <li><strong>Les réserves d'aujourd'hui ne sont pas comptées.</strong> Le
  système de retraite détient des réserves financières que le COR chiffre à
  part ; un solde annuel négatif peut être couvert par elles pendant des
  années. La dette de la section « ce que le déficit accumule » part de zéro à
  {solde.derniere_annee_observee} : elle dit ce que les soldes à venir
  ajoutent, jamais ce que le système détient.</li>
  <li><strong>L'assiette est supposée insensible au taux.</strong> Un taux de
  cotisation plus bas déforme l'offre de travail et la structure des
  rémunérations ; aucune élasticité n'est posée ici, et le sens de l'effet
  joue plutôt en faveur du système 4. Au-delà de la dernière année où
  l'assiette est publiée, c'est le TAUX DE PRÉLÈVEMENT qui est reconduit et
  non la part de PIB de l'assiette : celle-ci suit alors les ressources
  projetées par le COR, dont la baisse en part de PIB tient précisément à une
  assiette qui progresse moins vite que le PIB.</li>
  <li><strong>La grille échantillonne une génération sur cinq, et l'année du
  retour à l'équilibre se lit à quelques années près.</strong> Une cohorte qui
  part juste avant la bascule est représentée par une génération qui part
  juste après : les courbes de réforme s'écartent d'un ou deux dixièmes de
  point avant même la bascule, et un test borne l'effet à un demi-point. Le
  déficit actuel vaut {g.pourcentage(abs(observe.solde("actuel")), decimales=2)} du PIB, c'est-à-dire
  l'ordre de grandeur de l'écart que ce pas introduit à lui seul autour de la
  bascule : l'année où une courbe repasse zéro en dépend.</li>
  <li><strong>Le modèle compte des générations, non des personnes.</strong> Il
  suppose que la même proportion de chaque génération perçoit une pension, et
  que la carrière type ne change pas : un recul de l'âge de départ, une
  carrière plus longue ou plus hachée déplaceraient la trajectoire. Ses
  effectifs sont ceux des caisses, où un polypensionné compte dans chacune des
  siennes, ce qui gonfle le poids des régimes dont les affiliés ont
  typiquement aussi une carrière au régime général. Et avant 1975 la
  reconstitution est mince : la répartition ne commence qu'en
  {contexte.base.annee_debut_repartition} ; les générations antérieures à
  {cout.generations[0]} n'ont, dans ce modèle, aucune pension, plusieurs
  régimes n'existaient pas encore, et les premières années reposent sur deux
  ou trois générations et la moitié des cas types.</li>
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

#: Les trois niveaux de salaire de la page Risque, sur une même carrière de
#: référence : un salarié du privé né en 1990, entré à 22 ans, qui part à 64.
#: Ce n'est pas un cas type de la page Coût — elle ne pèse dans aucun agrégat —,
#: c'est un EXEMPLE, et la page le dit. Qui veut le sien a le simulateur.
NIVEAUX_RISQUE: tuple[tuple[str, float], ...] = (
    ("Au SMIC", 0.55),
    ("Au salaire moyen", 1.0),
    ("À deux fois le salaire moyen", 2.0),
)

NAISSANCE_RISQUE = 1990
DEBUT_RISQUE = 22
LIQUIDATION_RISQUE = 64


def _risque_exemple(contexte: Contexte, niveau: float) -> Comparaison:
    """La carrière de référence de la page Risque, à un niveau de salaire."""
    return contexte.simuler(Saisie(
        naissance=NAISSANCE_RISQUE, statut="salarie_prive_non_cadre",
        debut=DEBUT_RISQUE, liquidation=LIQUIDATION_RISQUE,
        salaire=niveau, unite_revenu="moyen", demandee=True,
    ))


def _risque(contexte: Contexte) -> str:
    """Ce que la répartition prélève, et ce qu'elle ne rendra pas.

    C'EST LE PREMIER ARGUMENT DE LA PROPOSITION, et le site ne le regardait
    pas : il chiffrait ce que chaque système verse et ce qu'il coûte, jamais ce
    que le système en place prend, ni à qui, ni ce qu'il ne tiendra pas. La
    page pose les deux questions dans l'ordre où un électeur les pose — combien
    on me prélève, et est-ce que je le reverrai — puis range sous des dépliants
    ce que la recherche établit, référence par référence.

    ELLE S'ADRESSE À QUELQU'UN QUI N'A PAS FAIT D'ÉCONOMIE, comme la page Coût,
    et obéit aux mêmes règles : une question par carte, sa réponse en deux
    phrases, le tableau qui la montre ; les mots de spécialiste portent leur
    définition ; tout le reste est replié.

    TROIS CHIFFRES VIENNENT DU MODÈLE plutôt que d'une source extérieure : ce
    qu'un salarié verse chaque mois pour sa retraite, à trois niveaux de
    salaire ; ce que ces cotisations financeraient au rendement qu'une
    répartition peut servir sans changer son taux ; et le solde du système, lu
    dans les comptes du COR comme sur la page Coût.

    LE RESTE EST CITÉ, ET LA PLUPART DU TEMPS CITÉ DU COR. C'est la règle de
    construction de la section qui répond au « il n'y a pas de problème » : à
    chaque fois qu'un chiffre du Conseil d'orientation des retraites suffit, il
    est préféré à un travail académique, parce qu'on ne peut pas le récuser
    comme partisan. La bibliographie entière est dans
    ``docs/risque_de_defaut.md``.

    CE QUE LA PAGE NE FAIT PAS : elle ne calcule aucune probabilité de défaut.
    La recherche n'en connaît pas, et le dire vaut mieux que d'en inventer une.
    """
    solde = contexte.cout().solde
    obs = solde.derniere_annee_observee
    observe = solde.annee(obs)
    fin = solde.derniere_annee
    horizon = solde.annee(fin)
    part_horizon = -horizon.solde("actuel") / horizon.depense("actuel")
    manque = -observe.solde_meur("actuel")

    # -- ce qu'un salarié verse, à trois niveaux de salaire -------------------
    exemples = [(libelle, _risque_exemple(contexte, niveau))
                for libelle, niveau in NIVEAUX_RISQUE]
    moyen = exemples[1][1]
    fiche_moyen = moyen.remuneration.reference.droit_en_vigueur
    verse_mensuel = fiche_moyen.retraite_totale / MOIS_PAR_AN

    # Ce que la promesse doit à quelqu'un d'autre : l'écart entre ce que le
    # droit promet à cet assuré et ce que ses propres cotisations financeraient
    # au rendement d'équilibre. C'est le système 4 du site, sous la règle par
    # défaut, et l'écart se lit dans les deux sens : une promesse plus élevée
    # que son financement est une promesse dont quelqu'un d'autre répond.
    constants = moyen.coefficient_euros_constants
    promis = moyen.actuel.pension_annuelle * constants / MOIS_PAR_AN
    finance = (moyen.notionnel_retroactif_employeur.pension_annuelle
               * constants / MOIS_PAR_AN)
    part_promise = 1.0 - finance / promis

    lignes_salaires = []
    for libelle, comparaison in exemples:
        fiche = comparaison.remuneration.reference.droit_en_vigueur
        lignes_salaires.append([
            libelle,
            g.euros(fiche.brut / MOIS_PAR_AN),
            g.euros(fiche.retraite_totale / MOIS_PAR_AN),
            g.pourcentage(fiche.retraite_totale / fiche.brut, decimales=1),
            g.euros(fiche.net / MOIS_PAR_AN),
        ])
    tableau_salaires = g.tableau(
        ["Niveau de salaire", "Salaire brut", "Prélevé pour la retraite",
         "Part du brut", "Net touché"],
        lignes_salaires,
        ["", "nombre", "nombre", "nombre", "nombre"],
        titre=f"Ce que la retraite prélève chaque mois sur un salarié du privé "
              f"en {fiche_moyen.annee}, {g.terme('part patronale')} comprise",
        entete_de_ligne=True,
    )

    jalons = [annee for annee in (obs, 2035, 2045, 2055, fin)
              if solde.annee(annee)]
    lignes_soldes = []
    for annee in jalons:
        ligne = solde.annee(annee)
        lignes_soldes.append([
            str(annee) + ("" if ligne.projete else " (observé)"),
            g.pourcentage(ligne.depense("actuel"), decimales=1),
            g.pourcentage(ligne.ressources, decimales=1),
            g.pourcentage(-ligne.solde("actuel") / ligne.depense("actuel"),
                          decimales=1),
        ])
    tableau_soldes = g.tableau(
        ["Année", "Pensions versées", "Recettes", "Part non financée"],
        lignes_soldes,
        ["", "nombre", "nombre", "nombre"],
        titre=f"Ce que le système verse et ce qu'il encaisse, en "
              f"{g.terme('part du PIB')}, de {obs} à {fin}",
        entete_de_ligne=True,
    )

    reperes = g.fiche(
        "Prélevé chaque mois sur un salaire moyen",
        g.euros(verse_mensuel),
        "cotisation salariale et patronale réunies",
    ) + g.fiche(
        "Promis au-delà de ce que VOS cotisations achèteraient",
        g.pourcentage(part_promise, decimales=0),
        "de VOTRE pension, à la charge de quelqu'un d'autre",
    ) + g.fiche(
        f"Que les recettes du SYSTÈME ne couvriront pas en {fin}",
        g.pourcentage(part_horizon, decimales=0),
        "des pensions dues cette année-là",
    )

    bulle_parts = g.bulle(
        "Pourquoi ces deux parts diffèrent",
        """La première est une question de justice : ce que cet assuré
reçoit au-delà de ce que ses propres cotisations achèteraient. La seconde est
une question de solvabilité : ce que le système doit verser au-delà de ce
qu'il encaisse, une année donnée. La première est la plus grosse parce qu'elle
ne compte que les cotisations, quand la seconde compte tout ce que le système
encaisse, impôts affectés compris.""")

    carte_prelevement = g.cle(
        "Combien la retraite vous prend-elle chaque mois ?",
        f"""<strong>{g.euros(verse_mensuel)} sur un salaire moyen</strong>, en
comptant ce que verse l'employeur. C'est le premier poste de votre fiche de
paie, avant l'impôt sur le revenu, avant la maladie. Sur une carrière entière,
au salaire moyen, cela fait plus de quatre cent mille euros.""",
        tableau_salaires,
        f"""Calcul du modèle sur une carrière de référence : un salarié du
privé né en {NAISSANCE_RISQUE}, entré à {DEBUT_RISQUE} ans. Les taux sont ceux
de {fiche_moyen.annee}, allègements généraux compris, ce qui explique le taux
plus faible au SMIC. <a href="{g.lien("/simuler")}">Le calcul sur votre propre
salaire</a> est à un clic.""",
        identifiant="risque-prelevement",
    )

    carte_promesse = g.cle(
        "Est-ce que vous le reverrez ?",
        f"""Pas en entier. Au rendement qu'une répartition peut servir sans
toucher à son taux, ces cotisations financent
<strong>{g.pourcentage(1 - part_promise, decimales=0)}</strong> de la pension
promise. Le reste attend des cotisants qui ne sont pas nés, et il manque déjà
{_milliards(manque, 1)} par an.""",
        tableau_soldes,
        f"""Sources : le modèle du site pour la part financée, les comptes du
Conseil d'orientation des retraites pour le solde, observés puis projetés dans
son scénario de référence. Le détail année par année est sur la page
<a href="{g.lien("/cout")}">Coût</a>. Ce que les recettes paient de VOTRE
pension, à VOTRE date de départ, est sur
<a href="{g.lien("/simuler")}">le simulateur</a>.""",
        identifiant="risque-promesse",
    )

    detail = "".join([
        _risque_salaire(contexte),
        _risque_croissance(),
        _risque_pauvres(),
        _risque_jeunes(),
        _risque_evince(),
        _risque_deja_eu_lieu(),
        _risque_objections(contexte),
        _risque_ailleurs(),
        _risque_droit(),
        _risque_sources(),
    ])
    plan = g.plan(carte_prelevement + carte_promesse + detail, "/risque")

    tete = g.affiche(
        "Le risque",
        'Ce que la retraite vous prend, '
        '<span class="cle-texte">et ce qu\'elle ne rendra pas.</span>',
        f"{g.euros(verse_mensuel)} par mois prélevés sur un salaire moyen, "
        "pour une promesse que la loi révise à la baisse depuis trente ans.",
    )

    return f"""
{tete}

<div class="note resume"><strong>En clair.</strong> La retraite est le premier
prélèvement de votre fiche de paie. Elle ne met rien de côté : elle verse
aussitôt ce qu'elle encaisse, et votre pension attendra les cotisations de vos
enfants. Or ils seront moins nombreux, et ce qu'on leur promet dépasse déjà ce
que vos cotisations financent. Le système ne s'arrêtera pas de payer. Il
paiera moins, comme il le fait depuis trente ans sans le dire, en revalorisant
les pensions moins vite que les salaires.</div>

<div class="fiches reperes">{reperes}</div>

<p class="discret"><strong>Ces deux pourcentages ne s'additionnent
pas.</strong> Les {g.pourcentage(part_promise, decimales=0)} comparent une
pension aux cotisations de cet assuré ; les
{g.pourcentage(part_horizon, decimales=0)}, les dépenses du système à ses
recettes.{bulle_parts}</p>

{plan}

{carte_prelevement}

{carte_promesse}

<div class="note"><strong>Ce que nous proposons d'en faire.</strong> Un
{g.terme("compte notionnel")} ne crée pas d'argent. Il fait trois choses que
le système actuel ne fait pas : il inscrit chaque euro versé sur un compte à
votre nom, il ramène le prélèvement de 28 % à 18 %, et il règle l'écart chaque
année par un {g.terme("coefficient d'équilibre")} que tout le monde peut lire,
au lieu d'attendre une réforme qui tombe sur une génération.
<a href="{g.lien("/")}">La proposition</a> est chiffrée carrière par
carrière.</div>

<h2>Pour aller plus loin</h2>
<p class="chapeau">Ce que la recherche établit, et ce qu'il faut répondre à
ceux qui assurent qu'il n'y a pas de problème.</p>

{detail}
"""


def _risque_salaire(contexte: Contexte) -> str:
    """L'incidence : la cotisation retraite est prise sur le salaire.

    C'est le résultat le moins connu du public et le mieux établi de la
    littérature récente, et il tient à une distinction que le débat français
    ignore : ce qui décide de qui paie n'est pas le partage légal, c'est la
    force du lien entre la cotisation et le droit qu'elle ouvre. La retraite
    est la cotisation la plus contributive du barème, donc celle qui est la
    plus intégralement prise sur le salaire.
    """
    moyen = _risque_exemple(contexte, 1.0)
    fiche = moyen.remuneration.reference.droit_en_vigueur
    employeur = fiche.retraite_employeur / MOIS_PAR_AN
    return g.depliant(
        "Ces cotisations sont votre salaire, y compris celles de l'employeur",
        f"""
<p>Sur la fiche de paie, la retraite se partage en deux lignes : celle que le
salarié voit retirée de son brut, et celle que l'employeur verse par-dessus.
La seconde passe pour un cadeau. Elle n'en est pas un : au salaire moyen, elle
vaut {g.euros(employeur)} par mois, et la recherche montre qu'elle est payée
par le salarié, sous forme de salaire qu'il ne touche pas.</p>

<p><strong>Le résultat est récent, français, et il est net.</strong> Antoine
Bozio, Thomas Breda, Julien Grenet et Arthur Guillouzouic
(<em>Review of Economic Studies</em>, 2026) ont comparé trois réformes
françaises qui ont déplacé des cotisations au-dessus du plafond de la sécurité
sociale, en suivant les salariés jusqu'à huit ans après. Quand la cotisation
ouvre un droit visible, elle est reportée sur le salaire à hauteur de
<strong>100 %</strong> : c'est le cas de la hausse des cotisations de retraite
complémentaire entre 2000 et 2005. Quand elle n'ouvre aucun droit individuel,
le report tombe à 21 % pour la famille et à 6 % pour la maladie, sans que ces
chiffres se distinguent de zéro. Leur méta-analyse de vingt et une estimations
internationales donne le même partage : <strong>103 % de report pour les
cotisations liées à un droit, 15 % pour les autres</strong>.</p>

<p>Le cas chilien avait montré la même chose en sens inverse. Jonathan Gruber
(<em>Journal of Labor Economics</em>, 1997) a suivi la chute du taux de
cotisation patronale de 30 % à 5 % après la réforme de 1981 : les salaires ont
absorbé la baisse presque exactement, et l'emploi n'a pas bougé. Sur
l'ensemble des cotisations, la méta-analyse d'Ángel Melguizo et José Manuel
González-Páramo (<em>SERIEs</em>, 2013), qui porte sur cinquante-deux travaux,
conclut que le salarié en supporte environ deux tiers à long terme en Europe
continentale.</p>

<p><strong>La conséquence est celle que personne ne dit.</strong> Augmenter les
cotisations retraite d'un point ne coûte pas un point aux entreprises : cela
coûte un point de salaire, avec un délai de quelques années. Et puisque la
retraite est de toutes les cotisations la plus contributive, c'est elle dont
le report est le plus complet. Chaque fois qu'on relève le taux pour tenir la
promesse, le salaire net des générations suivantes en paie le prix.</p>

<p class="discret">Réserve de méthode, qu'il faut connaître pour discuter le
chiffre : cette littérature mesure le report d'une <em>variation</em> de taux,
plutôt que la part du niveau actuel supportée par le salarié. Le passage de l'un à
l'autre est une inférence.</p>""",
        identifiant="risque-salaire",
    )


def _risque_croissance() -> str:
    """Ce que le financement de la répartition coûte à la croissance.

    L'argument n'a pas besoin d'un travail contesté : le COR le porte
    lui-même, sur trois modèles indépendants, et il nomme les dépenses que
    l'effet récessif met en difficulté. Le reste de la section suit l'ordre de
    la solidité des résultats, du plus établi au plus discuté, et le dit.
    """
    return g.depliant(
        "Ce que le financement coûte à la croissance, dit par le COR lui-même",
        f"""
<p>Le Conseil d'orientation des retraites a fait chiffrer par trois équipes
indépendantes, la direction générale du Trésor, l'OFCE et une équipe de
l'École d'économie de Paris, l'effet macroéconomique des quatre façons de
rétablir l'équilibre. Son rapport de juin 2026 écrit :</p>

<blockquote><p>« Quel que soit le modèle retenu, trois des quatre leviers
étudiés – baisse relative des pensions, hausse des cotisations salariales et
hausse des cotisations employeurs – présentent un caractère récessif. »</p></blockquote>

<p>Et il dit à qui la facture est transmise :</p>

<blockquote><p>« Les trois premiers leviers ont toutefois un impact récessif,
qui pèse sur les recettes publiques et dégrade le solde hors retraites : ils
renforcent les difficultés à financer les dépenses publiques autres que les
retraites, à l'instar de l'école, la santé ou la sécurité. »</p></blockquote>

<p><strong>Financer la promesse par les cotisations réduit donc l'activité, et
réduit l'argent disponible pour l'école et l'hôpital.</strong> Le COR ajoute
que les ajustements devront en pratique être plus forts que ses propres
calculs ne le laissent croire, pour tenir compte de ce caractère récessif
« qui conduit à abaisser le PIB par habitant ».</p>

<h3>D'où l'on part</h3>
<p>La France prélève déjà sur le travail plus que presque personne. Dans
<em>Taxing Wages 2026</em>, l'OCDE mesure le coin socio-fiscal d'un célibataire
au salaire moyen à <strong>47,2 %</strong> du {g.terme("coût du travail")} en
2025, contre <strong>35,1 %</strong> en moyenne dans l'OCDE : douze points
d'écart, et le troisième rang sur trente-huit pays. Pour un couple avec un
seul salaire et deux enfants, la France est deuxième, à 39,1 % contre 26,2 %.
La particularité française tient à la part patronale, dont le premier poste
est la retraite : 27,98 points de salaire brut en 2026 sur la première
tranche, cotisations salariale et patronale réunies.</p>

<h3>Ce que le système fait travailler moins</h3>
<p>C'est le résultat le plus solide de toute cette littérature, parce qu'il
repose sur des réformes traitées comme des expériences. Jonathan Gruber et
David Wise, dans l'enquête de référence du Bureau national de la recherche
économique américain (1999), ont mesuré ce qu'un assuré perd à travailler une
année de plus. <strong>En France, cette taxation implicite atteignait 80 % de
l'année travaillée</strong>, l'une des plus élevées des onze pays étudiés, et
les hommes de 55 à 65 ans y laissaient inemployés <strong>60 % de leur
capacité productive</strong>, contre 37 % aux États-Unis et 48 % en Allemagne.
Un système qui prend quatre cinquièmes d'une année de travail supplémentaire
n'a pas besoin d'autre explication pour faire partir tôt.</p>
<p>Les réformes françaises l'ont vérifié dans l'autre sens, et elles montrent
aussi la limite de l'exercice. Antoine Bozio (INSEE, 2011) mesure que la
réforme de 1993 a reporté le départ de neuf mois par année de durée exigée
chez les hommes. Yves Dubois et Malik Koubi (INSEE, 2016) trouvent, pour la
réforme de 2010, un taux d'activité à 60 ans en hausse de vingt-quatre points
chez les hommes, <strong>mais un taux de chômage en hausse de sept
points</strong> : entre un tiers et la moitié de ce que la retraite ne verse
plus part ailleurs, en chômage ou en invalidité. Simon Rabaté et Julie Rochut
(2020) concluent de même.</p>

<h3>Ce que le système n'épargne pas</h3>
<p>Un régime qui ne met rien de côté ne finance aucun investissement, et il
décourage ceux qui voudraient le faire à sa place. L'ordre de grandeur admis
est qu'<strong>un euro de droits à retraite se substitue à vingt à cinquante
centimes d'épargne privée</strong> : c'est la fourchette du Congressional
Budget Office américain (1998), retrouvée par Rob Alessie, Viola Angelini et
Peter van Santen sur données européennes (2013) et par Marta Lachowska et
Michał Myck sur la réforme polonaise (2018). Orazio Attanasio et Susann
Rohwedder (2003) ajoutent une précision qui vise directement un régime
contributif : c'est la partie proportionnelle au salaire qui évince l'épargne,
le socle forfaitaire ne l'évince pas.</p>
<p>Le résultat le plus net est ailleurs. David Bloom et ses coauteurs (2007)
montrent que l'allongement de la vie pousse partout les ménages à épargner
davantage, <strong>sauf dans les pays dotés d'une répartition généreuse, où
cet effet disparaît</strong>. Vivre plus longtemps n'y conduit plus à mettre
de côté.</p>
<p class="discret">Deux bornes d'honnêteté. Martin Feldstein chiffrait en 1996
la perte à un point de PIB par an à perpétuité, soit un cinquième des
cotisations ; son travail fondateur de 1974 portait une erreur de
programmation révélée par Dean Leimer et Selig Lesnoy en 1982, et son
estimation est restée discutée depuis. Hans-Werner Sinn (2000) objecte qu'en
valeur actuelle rien ne se gagne à une transition, puisqu'il faut de toute
façon payer les retraités en place. Notre argument ne repose sur aucun des
deux.</p>

<h3>Ce qu'un compte notionnel y change</h3>
<p>Feldstein et Jeffrey Liebman l'ont chiffré (2002) : rendre le lien visible
entre ce qu'on verse et ce qu'on touchera <strong>divise par trois le taux de
prélèvement ressenti comme une taxe</strong>, et il resterait à 71 % même si le
rendement du système était nul. Un compte notionnel ne crée pas d'épargne, et
les auteurs le disent ; il supprime la part du prélèvement que personne ne
compte aujourd'hui comme un droit.</p>""",
        identifiant="risque-croissance",
    )


def _risque_pauvres() -> str:
    """Qui paie le plus, rapporté à ce qu'il en retire."""
    return g.depliant(
        "Ce sont les plus pauvres qui y perdent le plus",
        """
<p><strong>Ils meurent plus tôt, et touchent donc moins longtemps.</strong>
L'INSEE mesure, sur la période 2020-2024, un écart d'espérance de vie de
<strong>13,0 ans entre les 5 % d'hommes les plus aisés et les 5 % les plus
modestes</strong>, et de 8,7 ans chez les femmes. L'écart s'est creusé depuis
2012-2016, l'espérance de vie des 25 % les plus modestes stagnant ou reculant.
Autour de mille euros de niveau de vie, cent euros de plus par mois valent
neuf mois d'espérance de vie chez les hommes.</p>

<p>Un régime qui ouvre les droits au même âge pour tous transforme cet écart en
transfert. Yves Dubois et Anthony Marino (INSEE, 2015) l'ont mesuré sur le
rendement des cotisations : chez les hommes, le rendement passe de 1,53 % pour
ceux qui ont fini leurs études le plus tôt à 0,98 % pour les plus diplômés. En
neutralisant la mortalité différentielle, l'écart se creuserait jusqu'à 0,65 %.
<strong>La mort prématurée des uns rend donc au sommet de la distribution
environ un tiers de ce que les règles lui reprennent.</strong> Le système
redistribue encore, mais beaucoup moins qu'il n'en a l'air.</p>

<p><strong>Ils paient aussi le chômage.</strong> Le coût du travail le plus
élevé de l'OCDE se paie d'abord sur les emplois les moins qualifiés. En 2024,
le taux de chômage français atteint 13,8 % chez ceux qui ont au plus le
brevet, contre 5,0 % chez les diplômés du supérieur. L'État en a tiré la
conséquence sans jamais le dire ainsi : il consacre <strong>75 milliards
d'euros par an</strong>, 2,7 points de PIB, à effacer ces cotisations sur les
bas salaires, et le rapport d'Antoine Bozio et Étienne Wasmer au Premier
ministre (2024) estime que leur suppression détruirait
<strong>980 000 emplois</strong>. Le barème est devenu si lourd qu'il faut le
neutraliser pour que les moins qualifiés aient un emploi.</p>

<p><strong>Et la pauvreté n'est plus là où on la cherche.</strong> En 2023,
10,5 % des retraités vivent sous le seuil de pauvreté, contre 15,4 % de
l'ensemble de la population et <strong>21,9 % des moins de dix-huit ans</strong>.
Le filet de sécurité le dit mieux que tout : l'allocation de solidarité aux
personnes âgées atteint 77 % du seuil de pauvreté, le revenu de solidarité
active 42 %.</p>""",
        identifiant="risque-pauvres",
    )


def _risque_jeunes() -> str:
    """Ce que les jeunes versent, et ce qu'ils récupèrent."""
    return g.depliant(
        "Les jeunes cotisent plus pour recevoir moins",
        """
<p><strong>Le taux monte, le rendement descend.</strong> Yves Dubois et
Anthony Marino (INSEE, <em>Économie et Statistique</em>, 2015) ont calculé ce
que chaque génération retire de ses cotisations. Le rendement interne vaut
environ <strong>2,5 % pour la génération 1950</strong>, puis tombe à
<strong>1,75 % à partir de la génération 1970</strong> et s'y stabilise. Sur
la même période, le taux de prélèvement supporté passe de 24 % pour la
génération 1950 à 28 % pour la génération 1985. La seule réforme de 1993
retire 0,4 point de rendement aux générations 1950 à 1985.</p>

<p>Le COR poursuit le calcul sur une carrière type de salarié du privé : le
rendement de la <strong>génération 2000 serait de 0,8 %</strong> par an, et de
0,5 % si les gains d'espérance de vie sont plus faibles que prévu. Un placement
sans risque fait mieux : sur cent vingt-six ans, les obligations d'État
américaines ont rendu 1,6 % par an en termes réels, les actions 6,6 %
(Dimson, Marsh et Staunton, 2026). Les deux grandeurs ne se mesurent pas de la
même façon, et la comparaison ne vaut que par son ordre de grandeur. Il est
d'un facteur deux à huit.</p>

<p><strong>Ce qu'ils touchent recule aussi.</strong> Le COR projette la pension
moyenne rapportée au revenu d'activité moyen de <strong>54,6 % en 2025 à
45,3 % en 2070</strong>, et le niveau de vie relatif des retraités de 100,2 %
en 2023 à 90,3 % en 2070. Les pensions progresseraient de 0,2 % par an en
euros constants quand les salaires progresseraient de 0,7 %.</p>

<p><strong>Et le patrimoine, lui, ne bouge pas.</strong> Début 2021, un ménage
dont la personne de référence a moins de trente ans détient un patrimoine
médian de 20 400 €, contre 232 800 € entre soixante et soixante-neuf ans. Les
ménages retraités sont 38,4 % des ménages et détiennent 40 % du patrimoine
brut. L'âge moyen auquel on hérite est passé de trente ans au début du siècle
dernier à environ <strong>cinquante ans</strong> aujourd'hui, pendant que le
flux successoral annuel passait de moins de 5 % à plus de 15 % du revenu
national (Conseil d'analyse économique, 2021).</p>

<p class="discret">Deux réserves, parce qu'elles seront opposées. Hippolyte
d'Albis et Ikpidi Badji (INSEE, 2017) montrent que, sur les cohortes nées entre
1901 et 1979, aucune génération n'a vécu moins bien que celles qui l'ont
précédée ; leurs données s'arrêtent en 2011. Et les comptes de transferts
nationaux montrent que la part publique du financement de la consommation des
plus de soixante ans a reculé depuis 1979. Le problème est dans la pente, non
dans un pillage.</p>""",
        identifiant="risque-jeunes",
    )


def _risque_evince() -> str:
    """Le premier poste de la dépense publique, et ce qui recule à côté."""
    return g.depliant(
        "Le premier poste du budget, et ce qui recule à côté",
        """
<p>En 2025, la retraite a coûté <strong>422 milliards d'euros, 14,1 % du PIB
et 24,3 % de l'ensemble des dépenses publiques</strong>. Le COR écrit que
l'évolution de cette dépense « explique à elle seule une grande partie de la
progression des dépenses publiques depuis une vingtaine d'années ». Rapportée
au PIB, la France y consacre le deuxième montant de l'OCDE, derrière l'Italie,
et quatre points de plus que l'Allemagne.</p>

<p>Pendant que ce poste montait, d'autres reculaient. La dépense d'éducation
est passée de <strong>7,8 % du PIB en 1995 à 6,7 % en 2023</strong>. La France
dépense aujourd'hui 13 % de moins que la moyenne de l'OCDE par élève du
primaire, tout en dépensant 24 % de plus par lycéen. Ses résultats en
mathématiques à l'enquête PISA de 2022 comptent parmi les plus bas jamais
mesurés, et la baisse récente y est qualifiée de sans précédent. L'effort de
recherche plafonne à 2,18 % du PIB, pour un objectif de 3 % et une Allemagne à
3,1 %.</p>

<p class="discret">Ce rapprochement décrit un arbitrage, il ne démontre pas un
mécanisme : aucun travail n'établit que la dépense de retraite cause le recul
de la dépense d'éducation, et nous ne l'affirmons pas. Ce qui est établi, et
que le COR écrit lui-même, c'est que les hausses de cotisations et les baisses
de pensions « renforcent les difficultés à financer les dépenses publiques
autres que les retraites, à l'instar de l'école, la santé ou la sécurité ».</p>""",
        identifiant="risque-evince",
    )


def _risque_deja_eu_lieu() -> str:
    """Le défaut silencieux : ce que les réformes ont déjà retiré."""
    return g.depliant(
        "La promesse a déjà été rompue : 1993, 2003, 2010, 2014, 2023",
        """
<p>La France n'a jamais baissé une pension en euros courants. Elle a fait
autre chose, à cinq reprises. En 1993, le régime général passe des dix aux
vingt-cinq meilleures années et revalorise les salaires portés au compte sur
les prix plutôt que sur les salaires. En 2003, la durée requise s'allonge avec
l'espérance de vie. En 2010, l'âge légal passe de 60 à 62 ans. En 2014, la
durée monte à 43 ans. En 2023, l'âge passe à 64 ans, avant d'être suspendu fin
2025 pour trois générations.</p>

<p><strong>Ce que ces réformes ont retiré se mesure.</strong> L'INSEE a
calculé que sans elles, les dépenses de retraite seraient supérieures de
3,7 points de PIB en 2018 et de <strong>6,3 points en 2070</strong>, dont 2,6
pour la seule revalorisation sur les prix. Sur les pensions déjà versées, la
Caisse nationale d'assurance vieillesse a mesuré l'effet de la réforme de
1993 : six retraités sur dix touchés, 6 % de moins en moyenne, et jusqu'à 20 %
sur vingt-cinq ans de retraite. Patrick Aubert et Simon Rabaté (2014) ont
chiffré l'autre bout : sans les réformes de 2003, 2010 et 2014, les trois
quarts des gains d'espérance de vie seraient allés à la retraite ; il en reste
un tiers.</p>

<p><strong>Les pensions déjà servies ont été touchées aussi.</strong> De 2014
à 2017, l'Agirc et l'Arrco, qui versent près d'un tiers de la retraite d'un
salarié du privé, n'ont pas revalorisé leur point une seule fois ; l'accord de
2015 a fixé pour trois ans une revalorisation inférieure d'un point à
l'inflation, et les générations nées à partir de 1957 reçoivent 10 % de moins
pendant trois ans si elles partent dès le taux plein. Personne n'a parlé de
rupture de promesse : la mesure était négociée, et elle est passée.</p>""",
        identifiant="risque-deja",
    )


def _risque_objections(contexte: Contexte) -> str:
    """Le cœur de la page : ce qu'on répond au « il n'y a pas de problème ».

    Chaque objection est citée dans les termes de ceux qui la portent, et la
    réponse est tirée du COR partout où c'est possible : une source qu'on ne
    peut pas récuser comme partisane, et qui se trouve dire, chiffres à
    l'appui, l'inverse de ce qu'on lui fait porter.
    """
    solde = contexte.cout().solde
    fin = solde.derniere_annee
    return g.depliant(
        "« Il n'y a pas de problème » : ce qu'on vous répondra, et ce qui suit",
        f"""
<h3>« Le déficit est faible : un demi-point de PIB »</h3>
<p>Vrai jusqu'en 2030, faux ensuite. Le COR projette −0,2 point de PIB en 2030,
<strong>−0,9 en 2045 et −2,4 en {fin}</strong>. L'argument tire sa force d'un
horizon qui s'arrête là où la courbe part. Henri Sterdyniak, qui le porte,
écrit d'ailleurs dans la même note que la stabilité des dépenses « ne
proviendrait que de l'hypothèse d'une nette baisse à l'avenir du rapport
retraite/salaire », et nomme la chose : « l'acceptation de la paupérisation
progressive des retraités ».</p>

<h3>« Le déficit vient du désengagement de l'État, pas du système »</h3>
<p>Le COR a calculé le solde sous la convention qui annule exactement ce
désengagement, en figeant la contribution de l'État en part de PIB. Le besoin
de financement reste de <strong>1,5 point de PIB</strong> en 2070. Le retrait
de l'État explique 0,9 point sur 2,4. Il est une partie du problème, il n'est
pas le problème.</p>

<h3>« La part des retraites dans le PIB est stable »</h3>
<p>Elle l'est, et le COR dit pourquoi dans la phrase qui suit : cette stabilité
est « freinée par la baisse de la pension moyenne relative au revenu d'activité
moyen qui passerait de <strong>54,6 % en 2025 à 45,3 % en 2070</strong> ».
Présenter cette stabilité comme une preuve de bonne santé revient à prendre
l'ajustement pour la preuve qu'il n'y a rien à ajuster.</p>

<h3>« Il suffit d'un point de cotisation »</h3>
<p>Les propositions chiffrées demandent trois points et demi, environ vingt-cinq
milliards par an. Le coin socio-fiscal français est déjà le troisième de
l'OCDE, douze points au-dessus de la moyenne. Et le COR a fait mesurer l'effet
par trois équipes : une hausse de cotisations est récessive, elle dégrade les
recettes publiques et « renforce les difficultés à financer les dépenses
publiques autres que les retraites ».</p>

<h3>« Le problème, c'est le chômage »</h3>
<p>Le COR a chiffré la variante. Un chômage ramené à 5 % améliorerait le solde
de 2070 de <strong>0,2 point sur les 2,4 qui manquent</strong>, soit un
douzième. La France n'est pas passée sous 7 % depuis 1982. Une productivité
haute laisserait encore 1,7 point de déficit, et le COR conclut que « le
système de retraite demeurerait durablement en besoin de financement dans
l'ensemble des scénarios considérés ».</p>

<h3>« Les retraités sont pauvres »</h3>
<p>Leur niveau de vie vaut 100,2 % de celui de l'ensemble de la population en
2023, et 106,5 % en comptant le logement dont ils sont propriétaires. Leur
taux de pauvreté est de 10,5 %, contre 15,4 % pour l'ensemble et 21,9 % pour
les moins de dix-huit ans. La France a l'un des trois taux de pauvreté des
plus de soixante-cinq ans les plus bas de l'OCDE. Un retraité sur dix vit
pourtant sous le seuil, et cela justifie un minimum, pas le refus de tout
ajustement.</p>

<h3>« La capitalisation, c'est le casino »</h3>
<p>La répartition a son rendement, et le COR le calcule : <strong>0,8 % par
an</strong> pour une carrière type de la génération 2000. Un placement sans
risque a fait mieux sur cent vingt-six ans. La question n'est pas le risque
contre la sécurité, elle est de savoir quel risque on porte : celui d'un
marché, ou celui de la démographie et d'un vote.</p>

<h3>« Les réformes passées ont réglé le problème »</h3>
<p>La réforme de 2023 devait rapporter 17,7 milliards en 2030 et équilibrer le
système. Elle a été suspendue moins de trois ans après son adoption, pour un
coût de 1,8 milliard par an jusqu'en 2032, et le système est projeté en
déficit sur tout l'horizon. C'est l'argument qui résiste le moins : la
trajectoire le dément toute seule.</p>""",
        identifiant="risque-objections",
    )


def _risque_ailleurs() -> str:
    """Ce qui arrive aux pays qui attendent trop."""
    return g.depliant(
        "Ce qui arrive quand on attend trop longtemps",
        """
<p><strong>Un régime public ne cesse pas de payer, sauf si l'État s'effondre.</strong>
Le seul cas documenté est russe : entre 1996 et 1998, quatorze millions de
pensionnés sur trente-neuf n'ont rien reçu pendant des mois, l'État ne
recouvrant plus les cotisations. Robert Jensen et Kaspar Richter
(<em>Journal of Public Economics</em>, 2004) en ont mesuré les conséquences sur
les enquêtes de ménages : un dixième de nourriture en moins, des soins
abandonnés, et pour les hommes des ménages touchés une probabilité de décès
accrue de cinq points en deux ans.</p>

<p><strong>Ce qui arrive, ailleurs, c'est la coupe.</strong> La Grèce a réduit
ses pensions dix fois entre 2010 et 2013, pour un cumul allant de 14 % sur les
petites pensions à près de 50 % sur les grandes. Platon Tinios (2016) en tire
la leçon : couper des pensions déjà servies « a fait sauter le plancher de la
promesse ». Aux États-Unis, la réserve de la Social Security s'épuise en 2033,
et les cotisations ne couvriront alors que 77 % des pensions dues. La Suède,
qui règle son régime par une formule automatique, a baissé ses pensions de
3,0 %, 4,3 % et 2,7 % en 2010, 2011 et 2014.</p>

<p>Le point commun de ces épisodes est le calendrier. Aucun pays n'a ajusté
tant qu'il pouvait attendre ; tous ont ajusté quand ils ne pouvaient plus, et
l'ajustement a été d'autant plus brutal qu'il avait été différé. Les pays qui
ont inscrit la règle d'ajustement dans la loi avant la crise ont baissé de
quelques pour cent ; ceux qui ont attendu la tutelle de leurs créanciers ont
baissé de moitié.</p>""",
        identifiant="risque-ailleurs",
    )


def _risque_droit() -> str:
    """Ce que le droit garantit, et ce qu'il ne garantit pas."""
    return g.depliant(
        "Ce que la loi ne vous garantit pas",
        """
<p>Un relevé de carrière ressemble à un contrat. Il n'en est pas un. Une
pension de répartition est une règle de calcul votée, que le Parlement peut
changer, et les trimestres inscrits n'engagent personne sur le montant qu'ils
vaudront. La Cour suprême des États-Unis l'a jugé dès 1960 dans l'affaire
<em>Flemming v. Nestor</em> : le bénéficiaire n'a pas de droit de propriété sur
sa prestation future. Aucune juridiction française n'a jamais reconnu un tel
droit non plus.</p>

<p>La recherche a donc renoncé à parler de défaut, et travaille avec une
échelle. John McHale (1999) l'a posée en comparant les pays du G7 : tout en
haut le non-paiement, puis la baisse en euros courants d'une pension déjà
servie, puis le gel, puis le recul de l'âge et le recalcul des droits en cours
d'acquisition. Son résultat tient toujours : les réformes réduisent surtout ce
que toucheront les actifs, et protègent ceux qui sont déjà partis.</p>

<p>La Banque mondiale (Holzmann, Palacios et Zviniene, 2004) a cherché les cas
de défaut complet sur des engagements de retraite et n'en a trouvé
« que peu, même dans des situations extrêmes ». Le défaut partiel, lui, est la
règle : le Royaume-Uni, le Japon, l'Allemagne, les États-Unis, la France et
l'Italie ont tous révisé à la baisse ce qu'ils serviront aux générations
suivantes. La phrase des auteurs mérite d'être retenue : il est peut-être plus
facile de faire défaut sur une promesse de retraite que sur une obligation,
« mais ni l'un ni l'autre n'est sans coût ».</p>""",
        identifiant="risque-droit",
    )


def _risque_sources() -> str:
    """Les références citées, telles qu'elles ont été lues."""
    return g.depliant("Sources", f"""
<p>Chaque chiffre de cette page vient d'un texte lu, cité avec son année. La
bibliographie complète, avec ce qui a été lu dans le texte et ce qui n'a pu
l'être qu'en résumé, est dans
<a href="{g.DEPOT}/blob/main/docs/risque_de_defaut.md">le dépôt</a>. Les
principales :</p>
<ul class="serree">
  <li><strong>Conseil d'orientation des retraites</strong>, rapport annuel de
  juin 2026 : le solde, la pension relative, le niveau de vie, la sensibilité
  au chômage et à la productivité, le rendement par génération, l'effet
  macroéconomique des leviers, et la convention comptable.</li>
  <li>Bozio, A., Breda, T., Grenet, J. et Guillouzouic, A. (2026),
  <em>Review of Economic Studies</em> 93(3) ; Gruber, J. (1997),
  <em>Journal of Labor Economics</em> 15(3) ; Melguizo, Á. et
  González-Páramo, J. M. (2013), <em>SERIEs</em> 4(3) — l'incidence des
  cotisations.</li>
  <li>OCDE, <em>Taxing Wages 2026</em> ; Bozio, A. et Wasmer, É. (2024),
  rapport au Premier ministre sur les exonérations de cotisations.</li>
  <li>Dubois, Y. et Marino, A. (2015), <em>Économie et Statistique</em>
  481-482 ; Aubert, P. et Bachelet, M. (2012), INSEE ; Aubert, P. et
  Rabaté, S. (2014), <em>Économie et Statistique</em> 474.</li>
  <li>INSEE, <em>Insee Première</em> 2085 sur l'espérance de vie par niveau de
  vie, 2063 sur la pauvreté, Focus 287 sur le patrimoine ; Conseil d'analyse
  économique, note 69, <em>Repenser l'héritage</em> (2021).</li>
  <li>Chabaud, M. et Rubin, J. (2025), INSEE, sur ce que les règles
  d'indexation ont retiré ; Bridenne, I. et Brossard, C. (2008),
  <em>Retraite et société</em>, sur la réforme de 1993.</li>
  <li>DEPP, compte de l'éducation 2024 ; OCDE, <em>Regards sur l'éducation
  2025</em> et <em>PISA 2022</em>.</li>
  <li>Jensen, R. et Richter, K. (2004), <em>Journal of Public Economics</em>
  88 ; Tinios, P. (2016), LSE Hellenic Observatory ; McHale, J. (1999),
  NBER 7031 ; Holzmann, R., Palacios, R. et Zviniene, A. (2004), Banque
  mondiale ; <em>Flemming v. Nestor</em>, 363 U.S. 603 (1960).</li>
  <li>Feldstein, M. (1974, 1996) et sa réfutation par Leimer, D. et
  Lesnoy, S. (1982), <em>Journal of Political Economy</em> — l'effet sur
  l'épargne, cité comme un ordre de grandeur discuté.</li>
  <li>Dimson, E., Marsh, P. et Staunton, M. (2026),
  <em>Global Investment Returns Yearbook</em> ; d'Albis, H. et Badji, I.
  (2017), <em>Économie et Statistique</em> 491-492, cité contre notre propre
  thèse.</li>
</ul>""", identifiant="risque-sources")


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
    from ..moteur.capitalisation import repartition

    base = contexte.base
    courbe = CourbeTauxSansRisque(base.racine_donnees, base.prime_terme_trente_ans)
    taux = g.pourcentage(base.taux_capitalisation_obligatoire, decimales=0)
    volontaire = g.pourcentage(
        base.taux_capitalisation_volontaire_applique, decimales=0)
    total_capitalise = g.pourcentage(
        base.taux_capitalisation_applique, decimales=0)

    comptants = g.tableau(
        ["Maturité", "Taux zéro-coupon, en rythme annuel"],
        [[f"{maturite} ans",
          g.pourcentage(courbe.placement(courbe.annee, maturite).taux, decimales=2)]
         for maturite in MATURITES_MONTREES],
        ["", "nombre"],
        titre=f"La courbe employée, au {_date_en_clair(courbe.date)}",
        entete_de_ligne=True,
    )

    # L'allocation, telle que la règle la produit : ce sont les maturités que
    # le moteur achète, lues par le même code. Une table écrite à la main
    # pourrait se désaccorder du calcul ; celle-ci ne le peut pas.
    def achat(horizon: int) -> str:
        lignes = repartition(horizon)
        if not lignes:
            return "rien : le départ a lieu dans l'année"
        maturite = lignes[0][0]
        titre = f"{maturite} an{'s' if maturite > 1 else ''}"
        if maturite == horizon:
            return f"{titre}, qui tombe l'année du départ"
        return f"{titre}, puis {horizon - maturite} ans à l'échéance"

    horizons = (40, 30, 20, 10, 5, 2)
    glissement = g.tableau(
        ["Années avant le départ", "Maturité achetée"],
        [[str(horizon), achat(horizon)] for horizon in horizons],
        ["nombre", ""],
        titre="Ce qu'un versement achète selon ce qu'il reste à courir",
        entete_de_ligne=True,
    )

    return g.depliant(
        f"Le pilier capitalisé : {total_capitalise} placés, ce que cela suppose",
        f"""
<p>La proposition ajoute, à compter de {base.annee_debut_capitalisation}, une
cotisation de {taux} prélevée sur la même assiette que la cotisation de
répartition, <strong>en plus</strong> d'elle : elle ne s'y substitue pas. Elle
n'entre pas au compte notionnel, elle constitue un capital au nom du cotisant,
dans un plan d'épargne retraite. Les années antérieures gardent les taux qui étaient les
leurs et ne versent rien.</p>

<h3>Les {volontaire} qui ne sont imposés par personne</h3>
<p>{g.pourcentage(base.taux_cotisation_liberal, decimales=0)} de répartition et
{taux} capitalisés font
{g.pourcentage(base.taux_cotisation_liberal + base.taux_capitalisation_obligatoire, decimales=0)},
quand le système actuel en prélève
{g.pourcentage(TAUX_ACTUEL_TOTAL, decimales=0)} pour un salarié du privé. La
proposition rend donc {volontaire}, et le modèle suppose qu'ils sont
<strong>replacés sur le même compte</strong>, aux mêmes conditions : le pilier
reçoit {total_capitalise} en tout, et l'effort de retraite revient à
{g.pourcentage(base.taux_retraite_propose, decimales=0)}, exactement celui
d'aujourd'hui. Le modèle ne prétend pas prévoir que les cotisants le feront : il
pose une <strong>convention de comparaison</strong>. Sans elle, le site
opposerait deux systèmes qui ne coûtent pas le même prix, et l'écart de pension
se lirait pour partie comme un effet des règles alors qu'il viendrait d'un
effort moindre.</p>
<p>Le compartiment ne distingue ces points nulle part ailleurs qu'en proportion
— même assiette, même maturité, mêmes frais, même table de
mortalité —, si bien que la rente se partage dans le rapport exact des deux
taux. Deux endroits les séparent, et deux seulement. Sur la <strong>fiche de
paie</strong>, les {volontaire} volontaires sont portés en entier par l'assuré,
là où les {taux} imposés sont partagés avec l'employeur : personne ne cofinance
une épargne qu'on décide seul, et le coût du travail ne bouge pas quand on la
verse. Dans les <strong>résultats</strong>, la rente qu'ils servent est écrite
sur sa propre ligne, pour que le lecteur qui ne les verserait pas puisse la
retrancher.</p>
<p>Un troisième endroit aurait pu les séparer, et ne les sépare pas : la
<strong>garantie vieillesse</strong>. Elle est différentielle, elle compte les
ressources et non leur origine, et cette rente-là en est une. Une épargne que
personne n'oblige réduit donc l'allocation, exactement comme une pension
personnelle réduit l'ASPA d'aujourd'hui. Pour qui reste sous le plancher après
avoir versé, ces cinq points ne rapportent <strong>rien du tout</strong> en
pension : la garantie les reprend euro pour euro. Il leur reste ce que la
répartition ne donne à personne, un capital qui se transmet.</p>

<h3>Où l'argent est placé</h3>
<p>Sur des titres sans risque, portés jusqu'à leur échéance, et choisis pour
tomber le jour du départ. La courbe retenue
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
son argent. Quand la courbe monte, elle flatte donc légèrement le pilier, et
c'est sous elle que les chiffres de ce site sont publiés. Elle a un second
effet, moins visible : elle rend le choix des maturités
<strong>sans conséquence</strong>, puisque c'est l'arbitrage qui détermine le
forward. Le réglage <strong>« Taux futurs du pilier capitalisé »</strong> la
retire, au milieu puis au haut de la fourchette de la littérature : la rente
baisse, et c'est seulement alors que l'allocation se met à peser. Au-delà de trente ans, la courbe ne dit plus rien : le taux est
prolongé à plat, et tout résultat qui en dépend est déclaré « estimé ».</p>

<h3>Selon quelle règle les maturités sont choisies</h3>
<p><strong>Chaque versement achète le titre qui arrive à échéance l'année du
départ</strong>, et rien d'autre. Le compte doit un capital à une
<strong>date</strong> ; le placement sans risque d'une dette datée est celui qui
tombe ce jour-là. Aucune ligne n'arrive à échéance après le départ, car il
faudrait la vendre avant terme, à un prix qui n'est plus sans risque ; aucune
non plus avant lui, tant que la courbe va jusque-là. Il n'y a donc rien à
replacer, et aucun taux futur à deviner. Au-delà de trente ans la courbe ne cote plus rien, et un versement
fait si tôt se couvre en deux temps : trente ans, puis le reste à
l'échéance.</p>
{glissement}
<p>Le pilier a longtemps fait autrement, et il vaut mieux le dire que de
l'effacer : une échelle de trois maturités (deux, dix et trente ans) glissant
du long vers le court à l'approche du départ, comme les fonds à échéance
l'affichent. Deux choses l'ont fait tomber. La première est qu'elle
<strong>ne changeait rien</strong> : tant que les taux futurs sont pris pour
ceux que la courbe implique déjà, enchaîner des placements courts ou bloquer un
long rapporte exactement la même chose, et le capital final était le même au
centime, quelle que soit l'échelle. La seconde est qu'elle raccourcissait
au nom d'une prudence qui n'était pas la bonne. Raccourcir protège d'un prix de
vente incertain, et ce compte ne vend rien : il attend une date. Ce dont il
avait à se protéger était l'inverse, le taux auquel chaque échéance serait
replacée, et c'est l'échelle elle-même qui le créait.</p>
<p><strong>Ce que l'adossement rapporte se lit au réglage des taux futurs.</strong>
Sous le réglage par défaut, rien : les deux règles donnent le même euro, et
l'adossement ne se justifie que par le risque qu'il supprime. En retirant une
prime de terme de 0,50 point à trente ans, sur une carrière de trente-six ans
partant en 2060, il rend 1,6 % de capital de plus que l'échelle glissante, soit
7 € de rente par mois, et 6,2 % de plus qu'un roulement à un an. Le même
réglage retire par ailleurs 4,8 % au pilier, soit 23 € par mois : la prime de
terme coûte trois fois ce que la meilleure allocation rapporte, et c'est dans
cet ordre qu'il faut le lire.</p>

<h3>Ce que l'enveloppe coûte</h3>
<p>Quatre prélèvements, aux <strong>vraies moyennes du marché</strong> du plan
d'épargne retraite individuel en 2025, mesurées par l'Observatoire des
produits d'épargne financière sur les remises de l'ACPR :
{g.pourcentage(base.frais_versement_capitalisation, decimales=2)} sur chaque
versement, {g.pourcentage(base.frais_gestion_capitalisation, decimales=2)} par
an sur l'encours, {g.pourcentage(base.frais_arrerages_capitalisation, decimales=2)}
sur chaque arrérage de rente, moyenne sur tous les assureurs et non sur les
seuls neuf sur vingt qui facturent, et
{g.pourcentage(base.frais_encours_rente_capitalisation, decimales=2)} par an
sur la réserve qui porte la rente, un frais que l'Observatoire ne mesure pas et
que le CCSF relevait sur vingt-deux contrats sur trente-quatre.</p>

<p><strong>Ils baissent ensuite, par paliers.</strong> Partout où une épargne
retraite obligatoire existe, la concurrence ou la règle ont fait tomber les
frais bien au-dessous de ceux d'un produit vendu au détail, et par à-coups : un
plafond au Royaume-Uni, un appel d'offres tous les deux ans au Chili, une
remise imposée aux gérants en Suède ; et là où seule la concurrence joue, aux
États-Unis, une baisse de 3,3 % par an pendant trente ans. Le modèle fait
suivre ce rythme au frais de gestion, par marches de dix ans, jusqu'à
{g.pourcentage(base.frais_gestion_paliers[-1][1], decimales=2)} en
{base.frais_gestion_paliers[-1][0]} ; le frais sur versement rejoint
l'assurance-vie, puis le contrat de capitalisation, puis
{g.pourcentage(base.frais_versement_paliers[-1][1], decimales=2)} en
{base.frais_versement_paliers[-1][0]} ; le frais sur arrérages s'éteint en
{base.frais_arrerages_paliers[-1][0]}. <strong>La baisse porte surtout sur
les nouveaux dépôts</strong> : chaque versement entre au tarif de son année et
le garde, et ne se rapproche du tarif du jour que de
{g.pourcentage(base.convergence_frais_stock, decimales=0)} de l'écart par an.
La rente garde les frais de l'année où elle est souscrite. Les sources de
chaque palier, et ce que d'autres trajectoires déplaceraient, sont dans les
limites du modèle.</p>

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
forwards d'aujourd'hui, n'est pas chiffré. L'adossement le réduit sans le
supprimer : il ne porte plus que sur les versements à venir et, au-delà de
trente ans d'horizon, sur le replacement du bout de courbe. Les versements
déjà faits, eux, sont bloqués jusqu'au départ. Il ne calcule aucune fiscalité :
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
à 62), la correction reste modeste : +5,0 points pour la génération 1920,
+0,0 pour 1945, -0,5 pour 1958. Les cotisations se concentrent sur les dernières années, là où
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
Le simulateur sait néanmoins AFFICHER des nets : une bascule convertit les
pensions et les salaires au moment de les écrire, le calcul restant brut de bout
en bout. Le taux de remplacement suit cette bascule — un brut sur un brut, plus
bas qu'un taux calculé sur des nets, ou un net sur un net.</p>
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
            cellule(g.fiabilite_en_clair(fiabilites.get(ligne.code, ""))),
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
                  [("", "Toutes")] + [(niveau, g.fiabilite_en_clair(niveau))
                                      for niveau in NIVEAUX_FIABILITE
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
        ["", "texte", "texte", "texte", "texte", "texte", "texte long"],
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
            escape(g.fiabilite_en_clair(macro.inflation.fiabilite_minimale_sur(debut, fin))),
            escape(g.fiabilite_en_clair(macro.salaire_moyen.fiabilite_minimale_sur(debut, fin))),
            escape(g.fiabilite_en_clair(macro.productivite.fiabilite_minimale_sur(debut, fin))),
            f"<strong>{escape(g.fiabilite_en_clair(macro.fiabilite_sur(debut, fin)))}</strong>",
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
        [escape(nom), f"{trace['valeurs']}",
         escape(g.fiabilite_en_clair(trace.get("niveau", "certifiee"))),
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
                  [("", "Tous")] + [(niveau, g.fiabilite_en_clair(niveau))
                                    for niveau in NIVEAUX_FIABILITE
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
           ["", "nombre", "", "texte date", "texte"],
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
