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
from ..cout import COMPOSANTE_GARANTIE, SCENARIOS, calculer_cout
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
    ("cliquet_legal", "Cliquet légal (défaut)"),
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

#: Situation de foyer de la garantie vieillesse du scénario 6. Elle ne joue que
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

#: Un enfant de plus change la pension du scénario 1 par ses majorations. Le
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

#: Les six courbes : attribut du modèle, variable CSS de couleur — la même que
#: la barre du haut, pour qu'une couleur désigne partout le même scénario — et
#: le chiffre posé au bout de la courbe. Ce chiffre n'est pas décoratif : la
#: palette des six scénarios échoue au contrôle de séparation daltonienne
#: (pire paire voisine : ΔE 4,3 sous deutéranopie), et six courbes qui se
#: croisent ne peuvent pas être identifiées par la couleur seule.
TRAJECTOIRE = (
    ("actuel", "--actuel", "1"),
    ("notionnel_retroactif", "--retroactif", "2"),
    ("notionnel_prospectif", "--prospectif", "3"),
    ("notionnel_retroactif_employeur", "--retroactif-employeur", "4"),
    ("notionnel_prospectif_employeur", "--prospectif-employeur", "5"),
    ("notionnel_liberal", "--liberal", "6"),
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
    age_reference: str = "cliquet_legal"
    table: str = "unisexe"
    conversion_acquis: str = "reference"
    part_cotisation: str = "salariale"
    #: Seul ou en couple : la situation de foyer de la garantie vieillesse du
    #: scénario 6. Le défaut est la personne seule, comme pour l'ASPA du
    #: scénario 1, de sorte que les deux planchers se comparent.
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
            demandee=bool(parametres),
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
        saisis = [self.salaire] + [metier.salaire for metier in self.metiers]
        if not self.revenu_en_euros:
            return saisis
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

    def niveau(self, euros_mensuels: float) -> float:
        """Un salaire mensuel brut, en multiples du salaire moyen."""
        return euros_mensuels * MOIS_PAR_AN / self.moyen

    def mensuel(self, niveau: float) -> float:
        """L'opération inverse : un multiple, en euros bruts par mois."""
        return niveau * self.moyen / MOIS_PAR_AN


@dataclass
class Contexte:
    """Simulateurs mémorisés par jeu de paramètres.

    Le chargement des données coûte quelques dixièmes de seconde ; une
    simulation en coûte dix millisecondes. On garde donc une instance par jeu
    de paramètres rencontré.
    """

    base: Parametres = field(default_factory=Parametres)
    _instances: dict[Parametres, Simulateur] = field(default_factory=dict)
    _depenses: DepensesRetraite | None = None
    _comptes: ComptesRetraite | None = None
    _population: Population | None = None
    _distribution: DistributionPensions | None = None
    _cout: object = None

    def simulateur(self, parametres: Parametres | None = None) -> Simulateur:
        parametres = parametres or self.base
        if parametres not in self._instances:
            self._instances[parametres] = Simulateur(parametres)
        return self._instances[parametres]

    def depenses(self) -> DepensesRetraite:
        if self._depenses is None:
            self._depenses = DepensesRetraite(self.base.racine_donnees)
        return self._depenses

    def comptes(self) -> ComptesRetraite:
        """Le second terme du bilan : ce que le système de retraite encaisse."""
        if self._comptes is None:
            self._comptes = ComptesRetraite(self.base.racine_donnees)
        return self._comptes

    def population(self) -> Population:
        if self._population is None:
            self._population = Population(self.base.racine_donnees)
        return self._population

    def distribution(self) -> DistributionPensions:
        """La distribution des pensions — elle seule chiffre un plancher."""
        if self._distribution is None:
            self._distribution = DistributionPensions(self.base.racine_donnees)
        return self._distribution

    def cout(self):
        """Le coût agrégé des six systèmes — deux secondes de calcul, une fois."""
        if self._cout is None:
            self._cout = calculer_cout(
                self.simulateur(), self.depenses(), self.population(),
                self.comptes())
        return self._cout

    def echelle(self, saisie: Saisie) -> Echelle:
        """L'échelle des salaires de l'année courante, pour cette saisie.

        L'année est celle du modèle — on saisit un salaire d'aujourd'hui —, et
        les séries sont CELLES DE LA SAISIE : au-delà de la dernière année
        observée, le salaire moyen dépend du scénario de projection choisi.
        """
        parametres = saisie.parametres(self.base)
        macro = self.simulateur(parametres).macro
        annee = parametres.annee_courante
        return Echelle(
            moyen=salaire_moyen_annuel(macro, annee),
            smic=HEURES_SMIC_PAR_MOIS * macro.smic_horaire(annee),
            plafond=macro.plafond_securite_sociale(annee) / MOIS_PAR_AN,
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
    "/cas-types": "Cas types",
    "/cout": "Coût",
    "/methode": "Méthode",
    "/donnees": "Données",
    # Hors de la barre de navigation, où elle prendrait la place d'une page
    # qu'on vient lire : le pied de page y renvoie depuis toutes les autres,
    # ce que la loi demande — être joignable depuis n'importe où sur le site.
    "/mentions": "Mentions légales",
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
    "/simuler": "Votre carrière calculée de six façons : le système actuel, et "
                "les comptes notionnels appliqués depuis 1941 ou à partir de la "
                "bascule. Tout se calcule dans votre navigateur, rien n'est envoyé.",
    "/cas-types": "Treize carrières types sur sept générations : ce que chaque "
                  "pension deviendrait, par rapport à aujourd'hui, sous la "
                  "proposition et sous quatre contrefactuels.",
    "/cout": "Ce que la retraite coûte, d'où vient l'argent, et ce qui manque, "
             "de 1959 à 2070 — et ce que chacun des six systèmes coûterait.",
    "/methode": "Comment une pension en comptes notionnels se calcule, en trois "
                "opérations, et pourquoi la règle de revalorisation décide de "
                "presque tout.",
    "/donnees": "D'où viennent les chiffres du site, série par série et régime "
                "par régime, et ce qui a été recontrôlé contre sa source.",
    "/mentions": "Mentions légales, données personnelles et accessibilité du "
                 "simulateur de retraite en comptes notionnels.",
}


def rendre(contexte: Contexte, chemin: str,
           parametres: dict[str, str] | None = None) -> tuple[str, str]:
    """Contenu d'une page : ``(titre, corps HTML)``.

    Point d'entrée unique du rendu : le navigateur en remplace le contenu de
    ``<main>``. Les erreurs de saisie sont rendues dans la page, jamais levées :
    une adresse mal formée doit afficher un message, pas une trace d'exécution.

    Seul ``/simuler`` lit ``parametres`` : c'est la seule page que l'adresse
    paramètre. Toute adresse inconnue retombe sur l'accueil, comme le fait le
    routeur d'``index.html``.
    """
    if chemin == "/cas-types":
        return TITRES[chemin], _cas_types(contexte)
    if chemin == "/cout":
        return TITRES[chemin], _cout(contexte)
    if chemin == "/methode":
        return TITRES[chemin], _methode(contexte)
    if chemin == "/donnees":
        return TITRES[chemin], _donnees(contexte)
    if chemin == "/mentions":
        return TITRES[chemin], _mentions()
    if chemin != "/simuler":
        return TITRES["/"], _programme(contexte)

    try:
        saisie = Saisie.depuis_requete(parametres or {})
    except ErreurSaisie as erreur:
        # Le formulaire repart de ses valeurs par défaut — c'est ce qui permet
        # de le réafficher quoi qu'ait porté l'adresse —, mais il garde l'unité
        # de saisie : sans cela, une faute de frappe sur l'année de naissance
        # renverrait en euros quelqu'un qui raisonnait en multiples, avec des
        # nombres de l'autre unité sous les yeux.
        unite = _parmi(parametres or {}, "unite_revenu", UNITES_REVENU,
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
    depenses = contexte.depenses()
    derniere = depenses.derniere_annee
    comptes = contexte.comptes()
    annee_solde = comptes.derniere_annee_observee
    taux = g.pourcentage(base.taux_cotisation_liberal, decimales=0)
    plancher = g.euros(base.garantie_vieillesse_mensuelle)

    reperes = g.fiche(
        "Régimes de retraite en France", str(inventaire),
        "chacun avec ses propres règles",
    ) + g.fiche(
        f"Ce que cela coûte, en {derniere}",
        g.pourcentage(depenses.part_pib(derniere), decimales=1),
        "de tout ce que la France produit",
    ) + g.fiche(
        "Notre proposition", taux,
        "de cotisation, pour tout le monde",
    )

    propositions = g.points([
        ("Un compte, pas des trimestres",
         "Chaque euro cotisé est inscrit sur votre compte. Vous le suivez "
         "toute votre vie, comme un compte en banque. Sauf que rien n'est "
         "placé : c'est toujours la " + g.terme("répartition") + "."),
        ("Le même taux pour tous",
         f"{taux} du salaire, part du salarié et part de l'employeur "
         "additionnées, quel que soit le métier. Aujourd'hui le taux dépend du "
         "statut, et personne ne sait dire pourquoi."),
        (f"Un plancher de {plancher} par personne",
         "Versé à qui n'atteint pas ce montant, à partir de 65 ans, et payé "
         "par l'impôt. Il regarde votre seule pension, pas celle de votre "
         "conjoint."),
        ("Un réglage par an, au lieu d'une réforme tous les huit ans",
         "Un chiffre publié chaque année ramène les comptes à l'équilibre. "
         "Plus besoin de changer la règle en urgence, au détriment de ceux qui "
         "n'ont pas encore liquidé."),
    ])

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
<ul class="serree">
  <li><a href="{g.lien("/simuler")}">Simuler</a> : votre carrière, ou votre
  relevé collé tel quel, sous les six scénarios.</li>
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

    # L'entrée. Le site est un simulateur, et rien sur le premier écran ne le
    # disait : le mot n'était que dans un onglet, et le seul bouton arrivait au
    # troisième écran — au cinquième sur un téléphone. Dans le cadre que le site
    # du parti ouvre sur cette page, le titre du simulateur est masqué par
    # l'hôte, et ce bloc est la seule chose qui dise « simulez ». Deux lignes,
    # pas trois : à la troisième, le bouton passe sous le pli du téléphone.
    entree = f"""
<div class="note entree">
<p><strong>Ce que ça donnerait pour vous ? Simulez votre carrière.</strong><br>
Six montants côte à côte : les règles d'aujourd'hui, et cinq autres.</p>
<p class="actions"><a class="bouton" href="{g.lien("/simuler")}">Simuler ma
retraite</a></p>
</div>"""

    return f"""
<h2 style="margin-top:0">Notre programme pour les retraites</h2>
<p class="chapeau">Un seul régime. Un compte par personne. {taux} de cotisation
pour tout le monde. Et un plancher de {plancher} par mois, payé par l'impôt.</p>
{entree}
<div class="fiches reperes">{reperes}</div>

{propositions}

<h2>Le plancher, concrètement</h2>
<p>Aujourd'hui, l'ASPA regarde les ressources du couple : à 300 € et 1 500 €
de pension, il ne reçoit rien. La garantie regarde chacun. Ce que cela verse,
par mois, à quatre couples et à une personne seule :</p>
{_tableau_garantie()}

<h2>Ce que cela change</h2>
{differences}
<p class="discret">C'est le système de la Suède, de l'Italie, de la Pologne et
de la Lettonie.</p>

<div class="note"><strong>Aucune pension déjà versée ne changerait, et aucun
droit déjà acquis ne serait repris.</strong> C'est pourquoi une réforme des
retraites ne fait rien économiser l'année où elle est votée : il faut attendre
que des carrières entières se déroulent sous la nouvelle règle. Qui promet une
économie immédiate propose autre chose.</div>

<h2>Vérifiez plutôt que de nous croire</h2>
<p>Tout est calculé, sur des données publiques et un modèle ouvert.</p>
<div class="note signee">
<p><strong>Pourquoi ce site.</strong> Nous avons choisi de publier un modèle
plutôt qu'un slogan. Une proposition de retraite se juge sur ce qu'elle verse
à chacun et sur ce qu'elle coûte à tous, et nous voulions que n'importe qui
puisse le vérifier sur sa propre carrière. Nos réserves sont écrites page par page : le modèle reste un modèle, ses
séries d'avant 1950 sont fragiles, et le niveau des pensions notionnelles
dépend d'un réglage annuel qu'il calcule sans l'appliquer. Nous préférons un
chiffre discutable à une promesse qu'on ne peut pas discuter.</p>
<p class="discret">Le Parti libéral français, septembre 2026.</p>
</div>
<p class="actions"><a class="bouton" href="{g.lien("/simuler")}">Calculer ma
retraite</a><a href="{g.lien("/cout")}">Ce que ça coûte, et qui paie</a></p>

<h2>Pour aller plus loin</h2>

{depliant_actuel}

{depliant_calcul}

{_programme_justice(contexte)}
{_programme_garantie(contexte)}
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
<p>La bascule ne reprend aucun droit acquis et ne touche à aucune pension déjà
versée : elle fige ce qui est acquis, le convertit en capital, et applique la
règle nouvelle aux seules années suivantes.</p>
{etapes}
<p>Après la bascule, un seul régime : départ possible à
{_age(fusionne.age_ouverture)}, assiette déplafonnée, même taux pour tous.</p>""")


def _mentions() -> str:
    """Mentions légales, données personnelles, accessibilité.

    Trois obligations distinctes tiennent sur une seule page parce qu'un lecteur
    qui cherche l'une y cherche souvent les autres :

    * la loi pour la confiance dans l'économie numérique (art. 6-III) impose de
      dire qui édite le site et qui l'héberge ;
    * le RGPD impose de dire ce qu'on fait des données — ici, rien, et c'est
      précisément ce qu'il faut écrire, parce qu'un formulaire qui demande une
      année de naissance et un salaire laisse supposer le contraire ;
    * la déclaration d'accessibilité n'est pas obligatoire pour ce site — le
      décret du 24 juillet 2019 vise les personnes publiques et les entreprises
      au-delà de 250 M€ de chiffre d'affaires —, mais un site qui affiche un
      état d'accessibilité mesuré vaut mieux qu'un site qui se tait.

    Les champs que l'éditeur doit renseigner lui-même sont marqués en clair :
    mieux vaut un trou signalé qu'une mention inventée.
    """
    a_completer = ('<em class="a-completer">information à compléter par '
                   "l'éditeur</em>")
    return f"""
<h2 style="margin-top:0">Mentions légales</h2>
<p class="chapeau">Qui publie ce site, qui l'héberge, ce qu'il fait de ce que
vous saisissez — c'est-à-dire rien —, et où il en est de son accessibilité.</p>

<h3>Éditeur</h3>
<p>Parti Libéral Français.</p>
<div class="note avertissement">
  <p><strong>Cette rubrique est incomplète.</strong> Un site édité par une
  personne morale doit afficher sa dénomination exacte, l'adresse de son siège,
  un numéro de téléphone et le nom de son directeur de la publication
  (loi n° 2004-575 du 21 juin 2004, article 6-III-1 ; loi n° 82-652 du
  29 juillet 1982, article 93-2). Manquent ici :</p>
  <ul class="serree">
    <li>dénomination sociale ou statutaire exacte, et forme juridique : {a_completer}</li>
    <li>adresse du siège : {a_completer}</li>
    <li>numéro de téléphone : {a_completer}</li>
    <li>directeur de la publication : {a_completer}</li>
  </ul>
</div>

<h3>Hébergement</h3>
<p>Le site est publié par GitHub Pages. Hébergeur : GitHub, Inc.,
88 Colin P. Kelly Jr. Street, San Francisco, CA 94107, États-Unis —
<a href="https://github.com/contact">github.com/contact</a>.</p>

<h3>Contact</h3>
<p>Pour signaler une erreur de calcul, une source mal citée ou un défaut
d'accessibilité : <a href="{g.DEPOT}/issues">les tickets du dépôt</a>. Une
demande y est publique, ce qui est aussi la façon la plus simple de vérifier
qu'elle a reçu une réponse.</p>

<h3>Ce que ce simulateur n'est pas</h3>
<p>Il n'émane d'aucune caisse de retraite, d'aucune administration, et n'engage
personne. Ce qu'il affiche est le résultat d'un modèle appliqué aux données que
vous saisissez : ce n'est ni un relevé de carrière, ni une estimation de vos
droits, ni un conseil patrimonial ou financier. Vos droits réels ne sont établis
que par vos caisses, dont le service commun est
<a href="https://www.info-retraite.fr/">info-retraite.fr</a>. Les écarts entre
scénarios sont l'objet du modèle ; les niveaux affichés pour une carrière
individuelle en gardent la marge d'incertitude décrite par la
page <a href="{g.lien('/donnees')}">Données</a>.</p>

<h3>Données personnelles</h3>
<p><strong>Ce site ne collecte rien.</strong> Il n'a pas de serveur de calcul :
le modèle, ses tables et ses séries sont téléchargés une fois, puis tout
s'exécute dans votre navigateur. Ce que vous saisissez — date de naissance,
sexe, date de départ, revenu — n'est envoyé nulle part, n'est enregistré nulle
part, et disparaît quand vous fermez l'onglet.</p>
<ul class="serree">
  <li><strong>Aucun cookie, aucun traceur, aucune mesure d'audience.</strong>
  Rien n'est déposé sur votre appareil, et le site ne demande donc aucun
  consentement : il n'a rien à faire consentir.</li>
  <li><strong>Aucune ressource tierce.</strong> Pas de police d'écriture
  distante, pas de carte, pas de bibliothèque appelée à un autre domaine : tout
  ce que la page charge vient de cette adresse. Un contrôle automatique le
  vérifie à chaque modification du dépôt.</li>
  <li><strong>L'adresse de la page contient vos paramètres.</strong> C'est ce
  qui rend une simulation citable et refaisable à l'identique. La partie qui les
  porte suit le signe <code>#</code>, que les navigateurs n'envoient jamais au
  serveur ; elle reste en revanche dans l'historique de votre navigateur, et
  partager le lien, c'est partager ce que vous avez saisi.</li>
  <li><strong>L'hébergeur, lui, voit passer votre visite.</strong> Servir une
  page suppose de recevoir une requête : GitHub, comme tout hébergeur, traite à
  ce titre votre adresse IP, selon sa propre politique de confidentialité.
  L'éditeur de ce site n'y a pas accès.</li>
</ul>
<p>Il n'y a donc, du côté de l'éditeur, aucun traitement de données à caractère
personnel au sens du règlement (UE) 2016/679, et rien sur quoi exercer un droit
d'accès ou d'effacement : il n'existe nulle part de données vous concernant qui
viennent de ce site.</p>

<h3>Accessibilité : conformité partielle</h3>
<p>Ce site n'entre pas dans le champ de l'obligation d'accessibilité de
l'article 47 de la loi n° 2005-102 du 11 février 2005, qui vise les personnes
publiques, les délégataires de service public et les entreprises de plus de
250 millions d'euros de chiffre d'affaires. Il vise néanmoins le
<strong>RGAA 4.1</strong>, c'est-à-dire le niveau AA des WCAG 2.1.</p>
<p><strong>État déclaré : conformité partielle, par auto-évaluation.</strong>
Aucun audit externe n'a été mené, et aucun test n'a été conduit avec des
utilisateurs de technologies d'assistance. Ce qui a été vérifié, et l'est à
chaque modification par les contrôles automatiques du dépôt :</p>
<ul class="serree">
  <li>contrastes de texte au-delà de 4,5:1 et contours de champs au-delà de
  3:1, dans le thème clair comme dans le thème sombre ;</li>
  <li>couleurs des six scénarios séparables autrement que par la teinte, et
  contrôlées pour les visions daltoniennes ;</li>
  <li>tableaux titrés, avec en-têtes de colonne et de ligne ;</li>
  <li>chaque graphique suivi du tableau de ses points, année par année : une
  courbe est une image, et ce tableau en est la description détaillée ;</li>
  <li>formulaire entièrement étiqueté, groupé par métier, utilisable au
  clavier ;</li>
  <li>dates saisies au calendrier du navigateur — celui que le lecteur connaît
  déjà, dans sa langue et au clavier —, et l'âge qu'elles font écrit sous le
  champ, rattaché à lui pour être lu avec ;</li>
  <li>résultat du calcul annoncé aux synthèses vocales, qui ne verraient
  autrement rien changer ;</li>
  <li>lien d'évitement, repères de page, et respect du réglage système
  « animations réduites ».</li>
</ul>
<p><strong>Ce qui reste non conforme, ou non vérifié :</strong></p>
<ul class="serree">
  <li>les graphiques restent du dessin : le tracé lui-même — la forme d'une
  courbe, le moment où deux d'entre elles se croisent — ne se lit qu'à l'œil.
  Le tableau de ses points en donne toutes les valeurs, mais lire une forme
  dans une colonne de nombres demande un effort que voir n'exige pas ;</li>
  <li>certaines grilles — treize cas types sur sept générations, ou les cent onze
  lignes d'un tableau de graphique — restent larges et demandent un défilement
  sur petit écran ;</li>
  <li>le site exige JavaScript : le calcul se fait dans le navigateur, faute de
  serveur pour le faire ailleurs ;</li>
  <li>aucun test n'a été mené sur lecteur d'écran réel (NVDA, JAWS, VoiceOver).</li>
</ul>
<p>Un défaut d'accessibilité peut être signalé par
<a href="{g.DEPOT}/issues">les tickets du dépôt</a>. À défaut de réponse, le
Défenseur des droits peut être saisi :
<a href="https://formulaire.defenseurdesdroits.fr/">formulaire.defenseurdesdroits.fr</a>.</p>

<h3>Code, infographies, données et réutilisation</h3>
<p>Le code du modèle et du site est publié sous
<a href="{g.DEPOT}/blob/main/LICENSE">licence Apache 2.0</a> : réutilisable, y compris
commercialement, à condition d'en conserver la mention. Les pictogrammes
viennent de <a href="https://lucide.dev">Lucide</a> (licence ISC) ; ils sont
recopiés dans le dépôt, et le site ne les charge donc chez personne.</p>
<p>Les infographies, graphiques, tableaux et textes que le site affiche sont
sous licence <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr">Creative
Commons Attribution – Partage dans les mêmes conditions 4.0</a> (CC BY-SA) :
libres de reprise et d'adaptation, à condition de citer ce site et d'en
indiquer l'adresse, de signaler les modifications, et de republier toute version
modifiée sous la même licence. Le nom et le logo du Parti Libéral Français ne
sont couverts par aucune de ces licences.</p>
<p>Les données, elles, ne sont pas la propriété de l'éditeur. Les séries
françaises reprises ici — INSEE, DREES, DILA et Légifrance, Service des
retraites de l'État, caisses — sont des informations publiques, réutilisables
au titre des articles L321-1 et suivants du code des relations entre le public
et l'administration, le plus souvent sous Licence Ouverte (Etalab). Eurostat et
l'OCDE posent leurs propres conditions de réutilisation. Toutes imposent la
citation de la source : chaque valeur du dépôt porte la sienne dans
<a href="{g.DEPOT}/blob/main/data/sources.yaml">data/sources.yaml</a>, et la
page <a href="{g.lien('/donnees')}">Données</a> en donne l'état de
contrôle. Qui reprend un chiffre d'ici cite le producteur, pas ce site.</p>
<p class="discret">Dernière mise à jour de cette page : elle suit le dépôt, dont
l'historique complet est public.</p>
"""


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
    le texte — le chapeau annonçait « à compter de 2026 » quand le scénario 3
    partait de 2035.
    """
    return g.bulle(
        "Ce que ce formulaire calcule",
        "Votre carrière, calculée de six façons : le système actuel, et les "
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
        # unisexe, et les majorations pour enfants — les seules du scénario 1
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
        g.liste("indexation", "Règle d'indexation", INDEXATIONS, saisie.indexation,
                "revalorisation des comptes et des pensions",
                complement=g.GLOSSAIRE["indexation"]),
        g.champ("lissage", "Lissage de l'indexation", saisie.lissage,
                "en années : 1 = aucun",
                complement="Une moyenne glissante appliquée à la règle "
                "choisie, quelle qu'elle soit : 5 ans, c'est la fenêtre "
                "italienne.",
                type_="number", min="1", max=str(LISSAGE_MAXIMUM), step="1"),
        g.liste("age_reference", "Âge de référence", AGES_REFERENCE, saisie.age_reference,
                complement=g.GLOSSAIRE["âge de référence"]),
        g.liste("table", "Table de conversion", TABLES, saisie.table,
                complement=g.GLOSSAIRE["table de conversion"]),
        g.liste("part_cotisation", "Part de la cotisation portée au compte",
                PARTS_COTISATION, saisie.part_cotisation,
                "salariale seule, ou salariale et patronale",
                complement=g.GLOSSAIRE["part patronale"]),
        g.liste("conversion_acquis", "Conversion des droits acquis",
                CONVERSIONS_ACQUIS, saisie.conversion_acquis,
                "âge auquel les droits figés à la bascule sont convertis"),
        g.liste("foyer", "Situation de foyer (scénario 6)",
                SITUATIONS_FOYER, saisie.foyer,
                "scénario 6 seulement",
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
                type_="number", min=str(ANNEE_MINIMALE), max=str(ANNEE_MAXIMALE)),
    ])

    return f"""
<form class="carte" method="get" action="{g.lien('/simuler')}">
  {g.cache("unite_revenu", saisie.unite_revenu)}
  <h2 style="margin-top:0">Simuler une carrière{_bulle_du_titre(saisie)}</h2>
  <p class="chapeau" style="margin-top:0.3rem">L'exemple est déjà rempli.
  Calculez-le tel quel, ou saisissez votre carrière.</p>
  <div class="grille">{identite}</div>
  <h3>La carrière, période par période{_bulle_des_periodes()}</h3>
  {_metiers(saisie, affiliations, echelle)}
  {_bascule_unite(saisie, echelle)}
  {_releve(saisie)}
  <details class="options">
    {g.sommaire("Options de modélisation (sexe, profil, indexation, âge de "
                "référence, projection)")}
    <div class="grille">{avance}</div>
  </details>
  <p style="margin-top:1.4rem"><button type="submit">Calculer les six scénarios</button></p>
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


def _legende_des_unites(comparaison: Comparaison, saisie: Saisie) -> str:
    """Ce que sont les deux nombres qu'affiche chaque scénario.

    Elle se lit AVANT les barres, parce qu'elle répond à ce que le lecteur voit
    d'abord — deux montants là où il en attendait un —, quand le bloc « de quand
    sont ces chiffres ? » qui la suit répond, lui, à la convention de date.
    Muette quand le départ tombe sur l'année de référence : il n'y a alors qu'un
    chiffre, et rien à distinguer.
    """
    annee = comparaison.carriere.annee_liquidation
    if annee == saisie.euros:
        return ""

    valeur = ("ce que la pension vaudrait aujourd'hui"
              if saisie.euros == comparaison.parametres.annee_courante
              else f"ce que la pension vaudrait en euros de {saisie.euros}")
    autre = (
        f"la somme qui serait inscrite sur le virement de "
        f"{escape(str(comparaison.carriere.date_liquidation))}, inflation d'ici "
        "là comprise"
        if annee > saisie.euros else
        f"la somme réellement versée le mois du départ, en euros de l'époque — "
        f"{escape(str(comparaison.carriere.date_liquidation))}"
    )
    return (
        f'<p class="discret" style="margin:0 0 1.4rem">Deux fois le même '
        f"montant : le <strong>grand chiffre</strong> est {valeur}"
        + g.bulle(
            "Les deux unités",
            f"Le grand chiffre est {valeur} — le seul qui se compare à un "
            f"salaire ou à un loyer que vous connaissez ; celui d'à côté est "
            f"{autre}.",
        )
        + "</p>"
    )


def _lecture_des_montants(comparaison: Comparaison, saisie: Saisie) -> str:
    """À quelle date se rapportent les montants affichés, et en quels euros.

    C'est la première question que pose un lecteur devant les six barres :
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
    qu'il a déjà reçues. La seconde convention, elle, n'est plus une convention
    muette : les deux unités sont affichées l'une à côté de l'autre, et ce
    paragraphe n'a qu'à dire laquelle est laquelle.
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
            "Chaque scénario les donne dans deux unités : la somme telle "
            f"qu'elle serait versée en {annee}, l'inflation d'ici là comprise, "
            f"et cette même somme ramenée au pouvoir d'achat de {saisie.euros} "
            "— plus petite, sans rien acheter de moins. C'est ce pouvoir "
            "d'achat, et non le nombre inscrit sur le virement, qui dit ce que "
            "vaut la pension : il est mis en avant pour cette raison."
        )
    elif annee < saisie.euros:
        unites = (
            "Chaque scénario les donne dans deux unités : la somme telle "
            f"qu'elle a été versée en {annee}, en euros de l'époque, et cette "
            f"même somme ramenée au pouvoir d'achat de {saisie.euros} — c'est "
            "celle-là qui est mise en avant, parce qu'elle seule se compare aux "
            "prix que vous connaissez."
        )
    else:
        unites = (
            f"Le départ tombe sur {saisie.euros}, l'année de référence : les "
            "deux unités de la page se confondent, et chaque scénario n'affiche "
            "qu'un chiffre."
        )

    return g.bulle(
        "De quand sont ces chiffres, et en quels euros",
        f"{quand} {unites} Ce que compare cette page, ce sont six façons de "
        "CALCULER une pension de départ, pas six façons de la revaloriser "
        "ensuite. Montants <strong>bruts</strong> et au centime, comme la "
        "caisse les verse : avant CSG, CRDS et impôt, comme le revenu "
        "d'activité saisi plus haut. Le <strong>taux de remplacement</strong> "
        "rapporte la pension annuelle au dernier revenu d'activité ramené à "
        "l'année pleine — un brut sur un brut, donc plus bas qu'un taux calculé "
        "sur des nets.",
    )


def _trajectoire(contexte: Contexte, comparaison: Comparaison,
                 saisie: Saisie) -> str:
    """Le cumul versé par chaque scénario, du départ à 105 ans.

    Les six barres du haut donnent la pension d'UN mois — le premier. Elles ne
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

    # Le scénario 2 passe au-dessus du scénario 1 pour qui a beaucoup cotisé
    # sans que le droit en vigueur le lui rende — un libéral à quatre fois le
    # salaire moyen, par exemple. La phrase disait « l'écart se creuse » en
    # affichant « -45 575 € par an » : un signe moins au milieu d'un texte qui
    # affirmait le contraire.
    ecart = annuel["actuel"] - annuel["notionnel_retroactif"]
    phrase_ecart = (
        f"Le scénario 2 verse {g.euros(abs(ecart))} par an de "
        + ("moins" if ecart >= 0 else "plus")
        + " que le scénario 1 ; l'écart se creuse ici d'autant d'années que la "
        "retraite dure"
    )
    # Unité brève : le libellé est ancré à gauche de l'axe et déborderait du
    # cadre au-delà d'une poignée de caractères — « milliers d'euros de 2026,
    # cumulés » sortait du viewBox par la gauche, et « k€ 2026 » y perdait
    # encore son « k » sur téléphone, où les textes du repère sont grossis. Le
    # texte sous le graphique dit ce que « k€ » désigne, et de quelle année.
    unite = "k€"
    return g.depliant("Ce que chaque scénario finit par verser", f"""
<p>Les six montants du haut sont ceux d'un seul mois, le premier. Ce graphique
les additionne, année après année, à mesure que le retraité vieillit.{g.bulle(
    "Ce que ce graphique ajoute aux six montants",
    "C'est là que la durée entre dans le calcul. Une pension "
    "notionnelle vaut le capital divisé par l'espérance de vie, donc "
    "<strong>vivre plus longtemps que la moyenne, c'est toucher plus que ce "
    "que la carrière a financé</strong> — et mourir avant, moins. Cumuls "
    f"bruts, en milliers d'euros constants de {saisie.euros} : ils supposent "
    "que la pension garde son pouvoir d'achat après le départ, le moteur ne "
    "simulant aucune revalorisation postérieure à la liquidation. Une "
    "indexation qui décrocherait des prix ferait fléchir les six courbes à la "
    "fois, sans changer leur ordre.",
)}</p>
{g.graphique(
    "Cumul versé par chaque scénario, du départ à "
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
""")


def _titres_scenarios(saisie: Saisie) -> tuple[tuple[str, str], ...]:
    """Le libellé de chaque scénario, dans l'ordre des barres."""
    return (
        ("actuel", "1. Système actuel"),
        ("notionnel_retroactif", "2. Notionnel rétroactif"),
        ("notionnel_prospectif", f"3. Notionnel dès {saisie.bascule}"),
        ("notionnel_retroactif_employeur", "4. Rétroactif, avec le patronal"),
        ("notionnel_prospectif_employeur",
         f"5. Dès {saisie.bascule}, avec le patronal"),
        ("notionnel_liberal", f"6. Libéral : 18 % dès {saisie.bascule}, garantie"),
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


def _fiche_age_reference(comparaison, saisie: Saisie) -> str:
    """L'âge de référence, affiché seulement là où il agit.

    Ce chiffre n'entre dans AUCUNE des six pensions par lui-même. Il sert à une
    seule opération : convertir en capital les droits acquis avant la bascule,
    donc les scénarios 3 et 5 et eux seuls. Les scénarios 1, 2, 4 et 6 ne le
    lisent jamais — en comptes notionnels, l'âge de départ est déjà payé par le
    coefficient de conversion et par les années non cotisées.

    Deux conséquences, et c'est pourquoi la fiche ne se contente pas de lire
    ``ecart_age`` :

    * l'âge montré doit être celui de l'année de BASCULE, celui que la
      conversion emploie, et non celui de l'année de liquidation. Les deux ne
      coïncident que depuis 2017, où le cliquet est à 67 ans quelle que soit
      l'année ; une bascule antérieure les sépare, et la fiche affichait alors
      un âge que le calcul n'utilisait pas ;
    * quand rien n'a été acquis avant la bascule, ou que l'utilisateur a
      demandé la conversion à l'âge de départ effectif, l'âge de référence ne
      sert à rien et la fiche disparaît plutôt que d'annoncer un chiffre inerte.
    """
    acquis = comparaison.notionnel_prospectif.droits_acquis
    if acquis is None or saisie.conversion_acquis != "reference":
        return ""
    # L'étiquette est un mot du glossaire : la définition dit ce qu'est cet
    # âge et à quoi il sert. Ce qu'il COÛTE sur cette carrière-ci est dit
    # sous les fiches, par :func:`_note_age_reference`, là où on le lit.
    return g.fiche(
        "âge de référence", _age(acquis.age_conversion),
        "scénarios 3 et 5 seulement",
        definition=g.GLOSSAIRE["âge de référence"],
    )


def _note_age_reference(comparaison, saisie: Saisie) -> str:
    """Ce que l'âge de référence coûte, dit en clair dès qu'il coûte.

    La fiche affichait « 67 ans » sans un mot sur ce que ce chiffre changeait,
    et le lecteur qui partait à 64 ans ne pouvait pas deviner que ses droits
    acquis étaient convertis comme s'il partait à 67 — l'anticipation payée une
    seconde fois, sur le passé. Le réglage qui retire cet écart existe, mais
    dans les options repliées, en bas du formulaire : rien ne le désignait.
    Cette note nomme la pénalité et le réglage, et ne s'affiche que quand
    l'écart existe : à l'âge de référence, il n'y a rien à dire.

    Les DEUX sens sont écrits, comme dans la cascade : c'est un pivot, et un
    départ après l'âge de référence est bonifié par le même mécanisme.
    """
    acquis = comparaison.notionnel_prospectif.droits_acquis
    if acquis is None or saisie.conversion_acquis != "reference":
        return ""
    depart = comparaison.carriere.age_liquidation or 0.0
    reference = acquis.age_conversion
    if reference == depart:
        return ""
    if reference > depart:
        quand = f"{_age(reference - depart)} avant"
        effet = "l'anticipation est payée une seconde fois, sur le passé"
    else:
        quand = f"{_age(depart - reference)} après"
        effet = "le report est récompensé une seconde fois, sur le passé"
    return (
        f'<p class="note"><strong>Vous partez {quand} l\'âge de référence.'
        f"</strong> Dans les scénarios 3 et 5, les droits acquis avant "
        f"{saisie.bascule} sont convertis en capital comme si vous partiez à "
        f"{_age(reference)}, puis servis à partir de {_age(depart)} : {effet}. "
        "Le réglage « Conversion des droits acquis : à l'âge de départ "
        "effectif », dans les options de modélisation du formulaire, retire "
        "cet écart — c'est la convention qu'une réforme réelle retiendrait. "
        "Les scénarios 1, 2, 4 et 6 n'en dépendent pas.</p>"
    )


def _resultats(contexte: Contexte, saisie: Saisie) -> str:
    comparaison = contexte.simuler(saisie)
    carriere = comparaison.carriere
    retro = comparaison.notionnel_retroactif
    conversion = retro.conversion

    # Le moteur ne calcule qu'un montant, en euros de l'année de liquidation.
    # La page en affiche deux : celui-là, tel qu'il tomberait sur le relevé
    # bancaire le mois du départ, et le même ramené au pouvoir d'achat de
    # l'année de référence. Le second est le seul qui se compare à un salaire
    # ou à un loyer que le lecteur connaît ; c'est donc lui qui est mis en
    # avant, l'autre à côté pour que la conversion n'ait pas à être refaite de
    # tête.
    courants = {
        "actuel": comparaison.actuel.pension_annuelle,
        "retroactif": retro.pension_annuelle,
        "prospectif": comparaison.notionnel_prospectif.pension_annuelle,
        "retroactif-employeur":
            comparaison.notionnel_retroactif_employeur.pension_annuelle,
        "prospectif-employeur":
            comparaison.notionnel_prospectif_employeur.pension_annuelle,
        "liberal": comparaison.notionnel_liberal.pension_annuelle,
    }
    constants = {cle: comparaison.en_euros_constants(montant)
                 for cle, montant in courants.items()}
    reference = max(constants.values()) or 1.0

    # Les deux unités ne se distinguent que si le départ tombe ailleurs que sur
    # l'année de référence : sinon le coefficient vaut un, et afficher deux fois
    # le même nombre n'apprendrait rien.
    annee_depart = carriere.annee_liquidation
    deux_unites = annee_depart != saisie.euros
    unite_reference = (
        "par mois, en euros d'aujourd'hui"
        if saisie.euros == comparaison.parametres.annee_courante
        else f"par mois, en euros de {saisie.euros}"
    )

    def bloc(cle: str, titre: str, glose: str, variation: float | None,
             taux_remplacement: float) -> str:
        montant = constants[cle]
        variation_html = (
            '<span class="discret">référence</span>' if variation is None
            else f"<strong>{g.pourcentage(variation, signe=True)}</strong>"
        )
        depart = f"""
      <span class="chiffre depart">
        <span class="somme">{g.euros_centimes(courants[cle] / 12)}</span>
        <span class="unite">par mois, en euros de {annee_depart}</span>
      </span>""" if deux_unites else ""
        return f"""
<div class="scenario">
  <div class="entete">
    <span class="titre">{escape(titre)}</span>
    <span class="montant">
      <span class="chiffre principal">
        <span class="somme">{g.euros_centimes(montant / 12)}</span>
        <span class="unite">{unite_reference}</span>
        <span class="annuel">{g.euros_centimes(montant)} par an</span>
      </span>{depart}
    </span>
  </div>
  <div class="barre {cle}"><span style="width:{montant / reference * 100:.1f}%"></span></div>
  <div class="glose">{glose} · {g.terme("taux de remplacement")}
    {g.pourcentage(taux_remplacement)} · écart au système actuel : {variation_html}</div>
</div>"""

    scenarios = (
        bloc("actuel", "1. Système actuel",
             "droit en vigueur, minima et majorations compris",
             None, comparaison.taux_remplacement_actuel)
        + bloc("retroactif", "2. Comptes notionnels, rétroactifs depuis 1941",
               "toute la carrière recalculée sur la seule part salariale",
               comparaison.variation("notionnel_retroactif"),
               comparaison.taux_remplacement_retroactif)
        + bloc("prospectif", f"3. Comptes notionnels à compter de {saisie.bascule}",
               "droits acquis conservés, règles notionnelles ensuite",
               comparaison.variation("notionnel_prospectif"),
               comparaison.taux_remplacement_prospectif)
        + bloc("retroactif-employeur",
               "4. Comptes notionnels rétroactifs, salariale + patronale",
               "le scénario 2, la part patronale en plus",
               comparaison.variation("notionnel_retroactif_employeur"),
               comparaison.taux_remplacement("notionnel_retroactif_employeur"))
        + bloc("prospectif-employeur",
               f"5. Comptes notionnels à compter de {saisie.bascule}, "
               "salariale + patronale",
               "le scénario 3, la part patronale en plus",
               comparaison.variation("notionnel_prospectif_employeur"),
               comparaison.taux_remplacement("notionnel_prospectif_employeur"))
        + bloc("liberal",
               f"6. Proposition libérale : 18 % pour tous dès {saisie.bascule}, "
               "garantie vieillesse",
               f"le scénario 4 jusqu'à {saisie.bascule}, 18 % pour tous ensuite, "
               "plus une garantie financée par l'impôt",
               comparaison.variation("notionnel_liberal"),
               comparaison.taux_remplacement("notionnel_liberal"))
    )

    fiches = "".join([
        g.fiche("années cotisées", str(len(carriere.annees_cotisees))),
        # La date, et pas seulement l'année : la pension prend effet le premier
        # du mois, et c'est ce mois que l'utilisateur vient de choisir.
        g.fiche("liquidation", f"{_age(carriere.age_liquidation)} "
                f'<span class="discret">en {carriere.date_liquidation}</span>'),
        _fiche_age_reference(comparaison, saisie),
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
            f"{saisie.euros} comme les six montants ci-dessus."
            + g.bulle(
                "Pourquoi le RAFP est servi à part",
                "Ce régime est PROVISIONNÉ — sa rente sort d'un placement, non "
                "de la cotisation des actifs —, si bien qu'une réforme de la "
                "répartition ne l'atteint pas. Il est donc retiré des six "
                "totaux et servi à l'identique dans les six scénarios : c'est "
                "la seule façon de comparer ce qui est comparable.",
            )
            + "</p>"
        )

    minimum = ""
    if comparaison.actuel.minimum_applique:
        minimum = (
            '<p class="discret">Le minimum contributif s\'applique dans le '
            "scénario 1 ; il est supprimé dans les scénarios 2 à 5, et le "
            "scénario 6 lui substitue sa garantie vieillesse.</p>"
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
            "longue ne le permettent. Le montant du scénario 1 reste calculé, "
            "parce qu'il faut bien comparer les six scénarios sur la même "
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
    chiffre = "grand chiffre" if deux_unites else "chiffre"
    lecture = f"""
<p class="note resume"><strong>Six calculs pour votre carrière.</strong>
Le scénario 1 applique les règles d'aujourd'hui. C'est la référence.
Les scénarios 2 à 6 appliquent chacun d'autres règles à la même carrière.
Le {chiffre} : votre pension brute, {unite_reference}.
Le pourcentage en fin de ligne : l'écart avec le scénario 1.</p>"""

    # Les montants d'abord, les repères techniques ensuite. Dans l'autre ordre,
    # un téléphone montrait après le calcul un coefficient de conversion, un
    # capital et une note sur l'âge de référence, et pas un euro de pension.
    return f"""
<h2 id="resultats" tabindex="-1">Résultats\
{_lecture_des_montants(comparaison, saisie)}</h2>
{lecture}
<div class="carte">
  {_legende_des_unites(comparaison, saisie)}
  {scenarios}
  {fiabilite}
  {capitalisation}
  {minimum}
  {ouverture}
</div>
<div class="carte">
  <div class="fiches">{fiches}</div>
  {_note_age_reference(comparaison, saisie)}
  {_resume_parcours(contexte, saisie)}
</div>
<h2>Pour aller plus loin</h2>
<p class="chapeau">Les six montants ci-dessus sont le résultat ; tout ce qui
suit est le détail du calcul, rangé par question. Ouvrez ce que vous voulez
voir.</p>
{_trajectoire(contexte, comparaison, saisie)}
{_fourchette(contexte, saisie, comparaison)}
{_decomposition(contexte, saisie, comparaison)}
{_contribution_employeur(comparaison)}
{_garantie_vieillesse(comparaison, saisie)}
{_cascade(comparaison, saisie)}
{_detail(contexte, comparaison)}
"""


NATURES_PART_EMPLOYEUR = {
    "appelee": "contribution appelée par décret ou par arrêté",
    "implicite": "taux implicite reconstitué par les documents budgétaires",
    "repli": "aucune série publiée : effort du privé de la même année",
}


#: Les six scénarios, dans l'ordre où la page les affiche, avec le libellé
#: court que la fourchette leur donne.
SCENARIOS_AFFICHES = (
    ("actuel", "1. Système actuel"),
    ("notionnel_retroactif", "2. Notionnel rétroactif"),
    ("notionnel_prospectif", "3. Notionnel à la bascule"),
    ("notionnel_retroactif_employeur", "4. Rétroactif, avec le patronal"),
    ("notionnel_prospectif_employeur", "5. Bascule, avec le patronal"),
    ("notionnel_liberal", "6. Libéral : 18 % dès la bascule, garantie"),
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
<p>La même carrière, rejouée sous les trois hypothèses du COR. Le scénario 2
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
    ["Scénario", "Productivité 0,4 %", escape(retenu), "Productivité 1,0 %",
     "Amplitude"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
    titre="Pension mensuelle de chaque scénario sous les trois hypothèses de "
          "productivité du COR",
    entete_de_ligne=True,
)}
<p class="discret">Montants mensuels bruts, en euros constants de
{saisie.euros}.</p>""")


def _contribution_employeur(comparaison: Comparaison) -> str:
    """Qui verse la cotisation : l'assuré, son employeur, dans quelle proportion.

    C'est la mesure directe de ce qui sépare les scénarios 2 et 3 des scénarios
    4 et 5. Le bloc ne s'affiche pas pour un non-salarié, qui n'a pas
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
                ["Part salariale", "ce que l'assuré supporte — scénarios 2 et 3",
                 g.euros(employeur.agent)],
                ["Part patronale", "ce que verse l'employeur",
                 g.euros(employeur.employeur)],
                ["Total", "scénarios 4 et 5", g.euros(employeur.total)],
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
    "Les scénarios 2 et 3 ne portent au compte que la première ; les "
    "scénarios 4 et 5 y ajoutent la seconde, et ne changent rien d'autre.",
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


def _garantie_vieillesse(comparaison: Comparaison, saisie: Saisie) -> str:
    """Ce que le scénario 6 change, et ce que l'impôt y paie.

    Deux choses, et le bloc les sépare. Le taux unique change ce que le compte
    reçoit : il se lit dans le capital, contre celui du scénario 4. La garantie
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
    # compte est celui du scénario 4, et le capital ne s'en écarte pas.
    annees_18 = [c.annee for c in liberal.compte.cotisations
                 if c.annee >= bascule and not c.nulle]
    if annees_18:
        taux_unique = (
            f"Ici, les années {annees_18[0]} à {annees_18[-1]} sont cotisées à "
            f"{{taux}} ; celles d'avant {bascule} le sont aux taux réels, et le "
            f"capital vaut {g.euros(liberal.capital_notionnel)} contre "
            f"{g.euros(capital_4)} pour le scénario 4."
        )
    else:
        taux_unique = (
            f"Ici, la carrière s'achève avant {bascule} : aucune année n'est "
            f"cotisée à {{taux}}, et le compte est exactement celui du "
            f"scénario 4, {g.euros(liberal.capital_notionnel)}."
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
         f"le compte notionnel du scénario 6 — taux réels avant {bascule}, "
         f"{taux} pour tous ensuite — divisé par "
         f"{g.nombre(liberal.conversion.diviseur, DECIMALES_DIVISEUR)}",
         g.euros_centimes(garantie.pension_contributive) + " par an"],
        ["e) Garantie vieillesse servie",
         "max(0, c − d) à partir de 65 ans, financée par l'impôt"
         if garantie.age_atteint else
         "rien : la liquidation a lieu avant 65 ans, l'âge de l'allocation",
         g.euros_centimes(garantie.complement) + " par an"],
        ["f) = pension du scénario 6", "d + e",
         g.euros_centimes(liberal.pension_annuelle) + " par an"],
    ]

    if garantie.servie:
        lecture = (
            f"<p>Ici, la pension contributive de "
            f"{g.euros_centimes(garantie.pension_contributive / 12)} par mois "
            f"reste sous le plancher de {g.euros_centimes(garantie.plancher_annuel / 12)} : "
            f"l'impôt en finance <strong>{g.euros_centimes(garantie.complement / 12)} "
            f"par mois</strong>, soit {g.pourcentage(garantie.complement / liberal.pension_annuelle)} "
            "de ce que le scénario 6 verse.</p>"
        )
    elif not garantie.age_atteint:
        lecture = (
            f"<p>Ici, rien n'est servi : la liquidation a lieu à "
            f"{_age(comparaison.carriere.age_liquidation or 0.0)}, avant les 65 ans "
            "de l'allocation. Le modèle liquide et s'arrête — il ne suit pas "
            "l'assuré jusqu'à 65 ans, où la garantie s'ouvrirait si sa pension "
            "restait sous le plancher. C'est la même réserve que pour l'ASPA du "
            "scénario 1.</p>"
        )
    else:
        lecture = (
            f"<p>Ici, la pension contributive de "
            f"{g.euros_centimes(garantie.pension_contributive / 12)} par mois "
            f"dépasse le plancher de {g.euros_centimes(garantie.plancher_annuel / 12)} : "
            "la garantie ne sert rien, et le scénario 6 est un compte notionnel "
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
        "Le scénario 6 : un taux pour tous, et une garantie payée par l'impôt",
        f"""
<p>La garantie vieillesse, étape par étape, en euros de {annee} — l'année du
départ.{g.bulle(
    "Ce que le scénario 6 change au scénario 4",
    "Il est le scénario 4 — même compte rétroactif, cotisation salariale et "
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
    titre=f"La garantie vieillesse du scénario 6, étape par étape, en euros de {annee}",
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
    "ENTIER dégage, quand les scénarios 2 et 3 n'y versent que la part "
    "salariale ; c'est aux scénarios 4 et 5 qu'elle se compare sans biais. La "
    "deuxième ligne n'est pas une hypothèse mais un relevé — le coefficient "
    "que les arrêtés ont réellement appliqué, celui dont le scénario 1 se "
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


def _cascade(comparaison: Comparaison, saisie: Saisie) -> str:
    """Détaille le passage du scénario 1 au scénario 3, étape par étape.

    C'est la partie du modèle la moins intuitive : le scénario 3 n'est pas le
    scénario 1 diminué d'un pourcentage, c'est une autre formule appliquée à la
    même carrière. Tant qu'on ne voit pas la chaîne de calcul, l'écart affiché
    reste un chiffre à croire.
    """
    prospectif = comparaison.notionnel_prospectif
    acquis = prospectif.droits_acquis
    if acquis is None or prospectif.capital_notionnel <= 0:
        # Rien n'a été cotisé : une cascade de zéros n'explique rien, et le
        # reste de la page dit déjà que le compte est vide.
        return ""

    liquidation = comparaison.carriere.annee_liquidation
    age_liquidation = comparaison.carriere.age_liquidation or 0.0
    diviseur = prospectif.conversion.diviseur
    capital_apres = prospectif.capital_notionnel - acquis.capital
    actuel = comparaison.actuel.pension_annuelle
    renvoi_cascade = (
        "La dernière ligne est donc le scénario 3 tel que la <em>seconde</em> "
        "colonne l'affiche, non le chiffre mis en avant."
        if liquidation != saisie.euros else
        "Le départ tombant sur l'année de référence, la dernière ligne est "
        "exactement le montant du scénario 3 affiché plus haut."
    )

    lignes = [
        [f"a) Droits acquis à {saisie.bascule}",
         "carrière arrêtée à la bascule, règles actuelles, avantages non "
         "contributifs retirés, sans décote",
         g.euros_centimes(acquis.pension_figee) + " par an"],
        [f"b) × diviseur à {_age(acquis.age_conversion)}",
         f"coefficient de conversion en {saisie.bascule} : "
         f"{g.nombre(acquis.diviseur, DECIMALES_DIVISEUR)}",
         g.euros(acquis.capital_a_la_bascule)],
        [f"c) × revalorisation {saisie.bascule}-{liquidation}",
         f"règle d'indexation retenue : ×"
         f"{g.nombre(acquis.coefficient_revalorisation, DECIMALES_FACTEUR)}",
         g.euros(acquis.capital)],
        [f"d) + cotisations {saisie.bascule}-{liquidation - 1}",
         "versées au régime unique, revalorisées de même",
         g.euros(capital_apres)],
        ["e) = capital notionnel", "ce que la carrière a effectivement financé",
         g.euros(prospectif.capital_notionnel)],
        [f"f) ÷ diviseur à {_age(age_liquidation)}",
         f"coefficient de conversion en {liquidation} : "
         f"{g.nombre(diviseur, DECIMALES_DIVISEUR)}",
         g.euros_centimes(prospectif.pension_annuelle) + " par an"],
    ]

    part_acquis = acquis.capital / prospectif.capital_notionnel
    # Le seul endroit du site où l'âge de référence agit, donc le seul où son
    # histoire a sa place : la fiche des résultats se borne à dire ce qu'il est,
    # le budget de lecture de la page ne lui laissant pas davantage.
    #
    # Les DEUX sens sont écrits. La version d'avant ne parlait que de
    # l'anticipation, ce qui laissait croire à une sanction ; c'est un PIVOT, et
    # un départ postérieur à l'âge de référence est bonifié par le même
    # mécanisme. Taire cette moitié-là aurait été présenter une convention de
    # modélisation comme une règle de justice.
    neutralite = ""
    if saisie.conversion_acquis == "reference" and acquis.age_conversion != age_liquidation:
        anticipe = acquis.age_conversion > age_liquidation
        effet = (
            "L'anticipation est donc payée une seconde fois, sur le passé."
            if anticipe else
            "Le report est donc récompensé une seconde fois, sur le passé."
        )
        neutralite = (
            f"<p>Ligne b) : les droits déjà ouverts sont convertis au diviseur de "
            f"l'âge de référence ({_age(acquis.age_conversion)}), alors que la "
            f"rente sera servie depuis {_age(age_liquidation)}. {effet} "
            f"L'option « conversion des droits acquis à l'âge de départ "
            f"effectif » supprime cet écart, et c'est la convention qu'une "
            f"réforme réelle retiendrait.</p>"
            f"<p>D'où vient ce chiffre : {_age(acquis.age_conversion)} est l'âge "
            f"du <strong>taux plein</strong> du régime général, celui auquel la "
            f"décote s'annule quelle que soit la durée cotisée. La loi "
            f"n° 2010-1330 du 9 novembre 2010 l'a porté de 65 à 67 ans par "
            f"paliers, cible atteinte en 2017 ; la réforme du 14 avril 2023 l'y "
            f"a laissé. Le modèle le tient à <strong>cliquet</strong> — il ne "
            f"redescend jamais —, de sorte que l'abaissement à 60 ans de 1982 ne "
            f"le fasse pas baisser et qu'un départ à 60 ans en 1990 se lise bien "
            f"comme une anticipation de cinq ans.</p>"
            f"<p>C'est le <strong>seul</strong> usage de cet âge dans tout le "
            f"site : il n'entre que dans les scénarios 3 et 5, par cette ligne b). "
            f"Les scénarios 1, 2, 4 et 6 ne le lisent jamais — en comptes "
            f"notionnels, partir tôt est déjà payé deux fois, par les années non "
            f"cotisées et par un coefficient de conversion plus élevé. Et c'est "
            f"un <strong>pivot</strong>, non une sanction : partir avant lui "
            f"réduit la part acquise, partir après l'augmente.</p>"
        )

    return g.depliant("Du scénario 1 au scénario 3, ligne à ligne", f"""
<p>Montants en <strong>euros de {liquidation}</strong>, l'année du départ.{g.bulle(
    "Pourquoi cette section est en euros de l'année du départ",
    "Le scénario 3 n'est pas le scénario 1 diminué d'un pourcentage : c'est "
    "une autre formule appliquée à la même carrière, et la chaîne de calcul "
    "est arithmétique — la convertir ligne à ligne au pouvoir d'achat d'une "
    f"autre année la rendrait fausse. {renvoi_cascade}",
)}</p>
{g.tableau(
    ["Étape", "Ce qu'elle fait", "Résultat"],
    lignes,
    ["", "", "nombre"],
    titre=f"Du scénario 1 au scénario 3, étape par étape, en euros de {liquidation}",
    entete_de_ligne=True,
)}
<p>À comparer aux {g.euros_centimes(actuel)} par an du système actuel.{g.bulle(
    "D'où vient l'écart",
    "D'aucun abattement appliqué au scénario 1 : de ce que le capital "
    f"réellement constitué, {g.euros(prospectif.capital_notionnel)}, ne "
    f"finance pas les {g.euros(actuel * diviseur)} que le droit en vigueur "
    f"promet sur {g.nombre(diviseur, 1)} années de retraite.",
)}</p>
{neutralite}
<p class="discret">Les droits acquis avant {saisie.bascule} pèsent
{g.pourcentage(part_acquis)} du capital final.{g.bulle(
    "Ce que cette part devient",
    "Elle décroît de génération en génération : c'est elle qui étale la "
    "réforme dans le temps, et non un dispositif transitoire.",
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
        "C'est l'unité de la <em>seconde</em> colonne des six scénarios, celle "
        "du virement — pas celle du chiffre mis en avant, qui les ramène au "
        f"pouvoir d'achat de {annee_reference}."
        if annee != annee_reference else
        "Le départ tombant sur l'année de référence, c'est aussi l'unité des "
        "six montants affichés plus haut."
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
            '<span class="discret">c\'est le scénario 1 ci-dessus, pris '
            "dans les euros de son année de départ</span>",
        ])
    for pension in provisionnes:
        libelle, montant, detail = ligne(pension)
        lignes_actuel.append([
            "hors total — " + libelle, montant,
            '<span class="discret">régime PROVISIONNÉ, servi à part et retiré '
            "des six scénarios</span> · " + detail,
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
<h4>Scénario 1 — de quoi votre pension actuelle est faite{g.bulle(
    "Comment lire ce tableau",
    "Chaque régime d'abord, puis les avantages que le droit en vigueur ajoute "
    "par-dessus ; le total est la pension du scénario 1. Un minimum est déjà "
    "compris dans la ligne du régime qui le sert : le sous-total contributif "
    "l'en retire, et la ligne suivante le rend visible — c'est la même somme, "
    "comptée une fois.",
)}</h4>
{regimes}
{part}
<h4>Scénario 2 — construction du compte notionnel rétroactif</h4>
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
#: est CELUI QUI S'AFFICHE À L'OUVERTURE — le scénario 6, la proposition que
#: le site existe pour montrer ; les quatre autres sont les contrefactuels
#: qui mesurent ce que chaque ingrédient déplace, dans l'ordre de leur numéro.
GRILLES_CAS_TYPES: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "notionnel_liberal",
        "Scénario 6, la proposition",
        "Scénario 6 — le scénario 4, puis 18 % pour tous et une garantie",
        "Scénario 6, scénario 4 à taux unique dès la bascule et garantie vieillesse",
        "Le même compte rétroactif que le scénario 4 jusqu'à la bascule, puis "
        "un taux unique de 18 % — salariale et patronale confondues —, et une "
        "garantie vieillesse individualisée financée par l'impôt par-dessus. "
        "Les lignes qui cotisaient au-delà de 18 % descendent sous le "
        "scénario 4, celles qui cotisaient en deçà remontent. La garantie ne se "
        "voit que sur les cas dont la pension reste sous le plancher, à partir "
        "de 65 ans.",
    ),
    (
        "notionnel_retroactif",
        "Scénario 2",
        "Scénario 2 — comptes notionnels rétroactifs depuis 1941",
        "Scénario 2, comptes notionnels rétroactifs",
        "Les générations anciennes sont les plus touchées : leurs cotisations, "
        "versées quand l'inflation dépassait la productivité, ont été "
        "revalorisées à un taux très inférieur à la hausse des prix.",
    ),
    (
        "notionnel_prospectif",
        "Scénario 3",
        "Scénario 3 — comptes notionnels dès la bascule, part salariale seule",
        "Scénario 3, comptes notionnels à compter de la bascule",
        "Les générations déjà retraitées sont inchangées : leurs droits sont "
        "intégralement acquis avant la bascule. Les indépendants et professions "
        "libérales progressent parce que le régime unique relève leur taux de "
        "cotisation et déplafonne leur assiette — un effort contributif accru, "
        "pas un avantage accordé.",
    ),
    (
        "notionnel_retroactif_employeur",
        "Scénario 4",
        "Scénario 4 — le scénario 2, part patronale comprise",
        "Scénario 4, scénario 2 part patronale comprise",
        "Toutes les lignes bougent, sauf celles des non-salariés — artisan, "
        "exploitant agricole, profession libérale — qui n'ont pas d'employeur "
        "et pour qui ce scénario est le scénario 2. Les lignes publiques "
        "bougent le plus : la contribution de leur employeur est un taux "
        "d'équilibre, sans commune mesure avec la part patronale d'un salarié.",
    ),
    (
        "notionnel_prospectif_employeur",
        "Scénario 5",
        "Scénario 5 — comptes notionnels dès la bascule, employeur compris",
        "Scénario 5, scénario 3 part patronale comprise",
        "Les droits acquis avant la bascule sont conservés : les générations "
        "déjà retraitées ne bougent pas, et plus une carrière est récente, plus "
        "elle est calculée sous la règle nouvelle. À compter de la bascule il "
        "n'y a plus qu'un régime, et les écarts entre statuts s'y referment.",
    ),
)


def _badge_scenario(scenario: str) -> str:
    """« proposition » sur le scénario 6, « contrefactuel » sur les autres.

    Que les scénarios 2 à 5 soient des exercices et que seul le 6 soit la
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
    montrait cinq à la file, puis une seule — le scénario 5 — avec les quatre
    autres dans un dépliant ; un lecteur pressé s'arrêtait donc sur un
    contrefactuel, et repartait en croyant avoir vu la proposition. Les cinq
    grilles sont désormais derrière des onglets, et l'onglet ouvert est le
    scénario 6 : c'est lui que le site existe pour montrer.

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
                variation = comparaison.variation(scenario)
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
        (comparaison.variation(montre), cas.libelle)
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
            + f" par rapport à aujourd'hui, génération {derniere}, scénario 6",
        ) + g.fiche(
            "La moins bien traitée", escape(bas[1].split(" (")[0]),
            g.pourcentage(bas[0], signe=True, decimales=0)
            + f" par rapport à aujourd'hui, génération {derniere}, scénario 6",
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

    return f"""
<h2 style="margin-top:0">Treize carrières, comparées</h2>
<p class="chapeau">Treize carrières types, sept générations. Chaque case dit ce
que la pension deviendrait, par rapport à aujourd'hui, pour la même carrière.
<strong>Rouge : moins qu'aujourd'hui. Vert : plus.</strong></p>

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

<p class="discret">Le modèle calcule six scénarios. Le <strong>scénario 6</strong>
est <a href="{g.lien("/")}">la proposition</a> ; les scénarios 2 à 5 sont des
contrefactuels, qui mesurent ce que chaque ingrédient déplace : la
rétroactivité, la part patronale, le taux unique.</p>
<fieldset class="onglets"><legend>Scénario affiché</legend>{onglets}</fieldset>
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

#: Couleur de chacun des six scénarios — les mêmes que sur la page de
#: résultats, pour qu'un lecteur qui passe de l'une à l'autre les reconnaisse.
COULEURS_SCENARIOS = {
    "actuel": "var(--actuel)",
    "notionnel_retroactif": "var(--retroactif)",
    "notionnel_prospectif": "var(--prospectif)",
    "notionnel_retroactif_employeur": "var(--retroactif-employeur)",
    "notionnel_prospectif_employeur": "var(--prospectif-employeur)",
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
    # La réforme ne change rien avant sa bascule : sa courbe ne commence donc
    # qu'à l'année observée la plus récente, d'où la décision se prend.
    reforme = "notionnel_prospectif_employeur"
    apres = {ligne.annee: ligne.depense(reforme) * 100
             for ligne in solde.annees if ligne.annee >= obs}

    # L'ordre est celui de la lecture, de gauche à droite : la légende se
    # parcourt alors dans l'ordre où l'œil rencontre les courbes.
    courbes = (
        _serie(f"Avant {solde.premiere_annee}", "var(--serie-1)", avant,
               glose="autre source, périmètre un peu plus large"),
        _serie("Ce qui sort : les pensions versées", "var(--serie-2)", sortie),
        _serie("Ce qui rentre : cotisations et impôts", "var(--serie-5)", entree),
        _serie(f"Ce qui sortirait en comptes notionnels dès {bascule}",
               "var(--serie-4)", apres, tirets=True),
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
    carte_bilan = g.cle(
        "La retraite coûte-t-elle plus qu'elle ne rapporte ?",
        f"""Oui, un peu : {_milliards(abs(manque), 1)} de trop en {obs}.
<strong>L'écart va se creuser</strong> : en {solde.derniere_annee} il
manquerait
{g.pourcentage(abs(horizon.solde("actuel") / horizon.depense("actuel")), decimales=0)}
de la facture. En comptes notionnels dès {bascule}, les comptes se
rééquilibrent en {equilibre or "jamais"}.""",
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
        _cout_detail_poids(contexte),
        _cout_detail_sources(contexte),
        _cout_detail_limites(contexte),
    ])
    plan = g.plan(carte_bilan + carte_provenance + detail, "/cout")

    return f"""
<h2 style="margin-top:0">L'argent de la retraite</h2>
<p class="chapeau">Vos cotisations ne sont pas mises de côté. Elles paient
aussitôt les pensions de ceux qui sont déjà retraités : c'est la
{g.terme("répartition")}. Voici ce qui rentre, ce qui sort, et ce
qui manque.</p>

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
déjà au compte des scénarios 4 et 5, et c'est à ce titre qu'elle est comptée
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
        """Le coefficient qu'on lirait si la recette restait comptée."""
        return ligne.ressources / ligne.depense(scenario)
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
notionnels ne servent pas.</strong> Les scénarios 2 à 6 suppriment l'assurance
vieillesse des parents au foyer et les majorations pour enfants, et ne portent
rien au compte pendant une année de chômage. Ils comptent pourtant, dans les
ressources qu'ils supposent inchangées, les
{_milliards(comptes.transfert_organisme("famille", derniere), 1)} de la branche
famille et les {_milliards(comptes.transfert_organisme("chomage", derniere), 1)}
de l'assurance chômage de {derniere} — {g.pourcentage(supprime, decimales=2)}
du PIB, {g.pourcentage(part_supprimee, decimales=1)} des ressources. <strong>Le
coefficient d'équilibre du dépliant suivant les leur retire</strong> : année
par année là où on les connaît, à part constante des ressources avant et
après, jusqu'à l'horizon du COR. Sans ce retrait, le scénario 3 afficherait
{g.nombre(sans_retrait(horizon, "notionnel_prospectif"), 2)} en
{solde.derniere_annee} au lieu de
{g.nombre(horizon.coefficient("notionnel_prospectif"), 2)}, et le scénario 5
{g.nombre(sans_retrait(horizon, "notionnel_prospectif_employeur"), 2)} au lieu
de {g.nombre(horizon.coefficient("notionnel_prospectif_employeur"), 2)} ; en
{derniere}, où ces deux scénarios servent encore les pensions du système
actuel, l'écart est le même :
{g.nombre(sans_retrait(ligne_solde, "notionnel_prospectif"), 2)} contre
{g.nombre(ligne_solde.coefficient("notionnel_prospectif"), 2)}. Ce que la
branche famille cesserait de verser à la retraite ne disparaît pas : il lui
reste, et ce qu'elle en fait est une décision de programme, pas un résultat de
ce modèle.</div>
""", identifiant="cout-transferts")


def _cout_detail_scenarios(contexte: Contexte) -> str:
    """Les six systèmes : ce qu'ils auraient coûté, ce qu'ils coûteraient."""
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
    numeros = [libelle.split(".")[0] for scenario, libelle in SCENARIOS
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
            tirets=scenario.startswith("notionnel_prospectif"),
            glose=glose_actuel if scenario == "actuel" else "",
        )
        for scenario, libelle in SCENARIOS
        if scenario not in confondus
    )
    reference = cout.cumul("actuel")
    dernier = cout.annee(derniere)
    lignes_passe = []
    for scenario, libelle in SCENARIOS:
        cumul = cout.cumul(scenario)
        lignes_passe.append([
            _nom_scenario(scenario, libelle),
            _milliards(cumul, 0),
            g.pourcentage(cumul / reference - 1, signe=True, decimales=1)
            if scenario != "actuel" else "réf.",
            _milliards(dernier.cout(scenario), 1),
            g.pourcentage(dernier.part_pib * dernier.rapports[scenario], decimales=1),
        ])
    lignes_passe.append([
        "<em>dont garantie vieillesse du 6, financée par l'impôt</em>",
        _milliards(cout.cumul(COMPOSANTE_GARANTIE), 0),
        "—",
        _milliards(dernier.cout(COMPOSANTE_GARANTIE), 1),
        g.pourcentage(dernier.part_pib * dernier.rapports[COMPOSANTE_GARANTIE],
                      decimales=1),
    ])

    horizon = avenir.annee(avenir.derniere_annee)
    depart = avenir.annee(derniere)
    reference_avenir = avenir.cumul("actuel")
    lignes_avenir = []
    for scenario, libelle in SCENARIOS:
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
        "<em>dont garantie vieillesse du 6, financée par l'impôt</em>",
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
            g.pourcentage(ligne.part_pib("notionnel_prospectif"), decimales=1),
            g.pourcentage(ligne.part_pib("notionnel_prospectif_employeur"), decimales=1),
        ])

    return g.depliant("Les six systèmes comparés, du passé jusqu'à 2070", f"""
<p>Le modèle calcule six systèmes pour une même carrière. La carte du haut n'en
montre qu'un, le seul qui décrive une réforme applicable en créditant ce qui
est réellement prélevé. Voici les six, sur le passé puis sur l'avenir. Le
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
    f"Coût annuel des six systèmes, {cout.premiere_annee}-{derniere}, "
    f"en milliards d'euros constants de {euros}",
    annees, courbes, unite=f"Md € {euros}")}

{g.tableau(
    ["Système", f"Cumul {cout.premiere_annee}-{derniere}", "Écart",
     f"Coût {derniere}", f"Part du PIB {derniere}"],
    lignes_passe,
    ["", "nombre", "nombre", "nombre", "nombre"],
    titre=f"Ce que les six systèmes auraient coûté de {cout.premiere_annee} "
          f"à {derniere}",
    entete_de_ligne=True,
)}

<div class="note"><strong>Les scénarios 3 et 5 coûtent exactement ce que coûte
le système actuel, et ce n'est pas un défaut du calcul.</strong> Leur bascule est
fixée à {bascule} : aucune pension servie avant cette date n'en est modifiée,
puisque les droits déjà acquis sont conservés. Une réforme prospective ne fait
rien économiser sur le passé : elle ne commence à compter qu'au premier assuré
qui liquide après elle. C'est vrai de toute réforme des retraites qui respecte
les droits acquis.</div>

<p>Le scénario 2 aurait coûté {_milliards(cout.cumul("notionnel_retroactif"), 0)}
au lieu de {_milliards(reference, 0)}. Cet écart mesure tout autre chose que l'effet des
comptes notionnels. Il mesure deux choses qui n'ont rien à voir avec eux : ce
scénario ne porte au compte que la <strong>part salariale</strong> de la
cotisation, là où le scénario 4 y ajoute la part patronale et coûte
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
constants de {euros}. Les scénarios 2, 4 et 6 restent des contrefactuels et non
des réformes : ils supposent recalculées les pensions de gens qui les perçoivent
depuis trente ans, ce qu'aucun droit ne permettrait. Les scénarios 3 et 5, eux,
décrivent une réforme applicable, droits acquis conservés et règles nouvelles
pour la suite.</p>

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
    obs = solde.derniere_annee_observee
    observe = solde.annee(obs)
    horizon = solde.annee(solde.derniere_annee)
    lignes = []
    for scenario, libelle in SCENARIOS:
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
le raccord ne triche pas. Les cinq autres systèmes ne comptent pas tout ce que
le système actuel encaisse : ce que la branche famille et l'assurance chômage
versent pour des droits qu'ils ne servent pas, soit

{g.pourcentage(observe.retrait, decimales=2)} du PIB en {obs}, leur est
retiré, à part constante des ressources sur les années projetées. C'est
pourquoi les scénarios 3 et 5 sont déjà en déficit en {obs}, alors qu'ils y
servent encore les pensions du système actuel.</p>

<div class="note"><strong>Un coefficient supérieur à un est une marge, et
une marge se sert.</strong> Lire les
{g.nombre(horizon.coefficient("notionnel_prospectif"), 2)} du scénario 3 comme
une économie de {g.pourcentage(
    1 - 1 / horizon.coefficient("notionnel_prospectif"), decimales=0)} serait un
contresens : à prélèvement inchangé, ce système-là servirait autant que le
nôtre, mais autrement réparti entre les carrières. Le modèle calcule ce
facteur ; il ne l'applique jamais, et toutes les courbes de coût de cette page
sont celles d'un système qui ne se pilote pas.</div>
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
        ("Pensions du scénario 6", facteur_contributif),
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
<p>La garantie du scénario 6 est <strong>différentielle</strong> : elle ne verse
que ce qui manque à une pension pour atteindre son plancher. Son coût est donc
tout entier celui de la <strong>queue basse de la distribution</strong> des
pensions, et treize carrières de référence ne décrivent pas une distribution :
le chiffre que le tableau des six scénarios en tire —
{_milliards(cout.cumul(COMPOSANTE_GARANTIE), 0)} sur soixante-six ans — est
faux, et il faut le remplacer.</p>

<p>L'échantillon interrégimes de retraités de la DREES publie, par tranches de
cent euros, combien de retraités touchent combien. Le barème s'y applique
directement, sans passer par aucun cas type. Deux lectures : ce que la garantie
coûterait <strong>aux pensions d'aujourd'hui</strong>, en remplacement de
l'ASPA (un calcul qui ne doit rien au modèle), et ce qu'elle coûterait
<strong>aux pensions du scénario 6</strong>, toute la distribution étant alors
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
ponctuelle. Le déplacement des pensions au rapport du scénario 6 est
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
scénario 6.</div>
""", identifiant="cout-garantie")


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
    return g.depliant("Dix réserves à lire avant de citer ces chiffres",  f"""
<p>Une page de chiffres vaut par ce qu'elle laisse de côté, et cette page en
laisse dix, écrits ici plutôt qu'en note de bas de page.</p>
<ul class="serree">
  <li><strong>Les recettes ne réagissent à rien.</strong> Elles sont celles du
  système actuel, encaissées ou projetées telles quelles : la question posée
  est « à prélèvement inchangé, ce système tiendrait-il ? ». Le scénario 6, qui
  pose un taux unique de 18 % pour tous, déplacerait aussi les recettes, et
  rien ici ne le dit. Une seule recette suit le droit : ce que la branche
  famille et l'assurance chômage versent pour des droits que les scénarios
  notionnels ne servent pas leur est retiré, à part constante des ressources
  sur les années projetées. Le dépliant « Ce que la branche famille et
  l'assurance chômage versent » dit ce que cela vaut.</li>
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
    calcul du compte, la règle d'indexation, le droit que le scénario 1
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

    return f"""
<h2 style="margin-top:0">Comment c'est calculé</h2>
<p class="chapeau">Un compte notionnel est un compte <em>virtuel</em> : rien
n'est placé, les cotisations de l'année paient les pensions de l'année. Ce qui
change, c'est le calcul du droit, en trois opérations.</p>

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
{_methode_droit_positif()}
{_methode_suppressions()}
{_methode_carriere(contexte)}
{_methode_unites()}
{_methode_construction()}
"""


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
appliqué aux salaires portés au compte, celui dont le scénario 1 se sert pour
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
scénarios 2 et 3 ne portent au compte que la part salariale de la cotisation.
C'est aux scénarios 4 et 5 qu'il faut le comparer.</p>

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
    return g.depliant("Ce que le scénario 1 applique du droit en vigueur", f"""
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
<p>Enfin, le scénario dit si le droit <strong>ouvre</strong> la liquidation
demandée : âge légal du régime, ou départ anticipé pour carrière longue. Quand
il ne l'ouvre pas, le montant reste calculé, parce qu'il faut comparer les six
scénarios sur la même carrière, mais la page le signale : il ne décrit alors
aucune pension que le système actuel servirait.</p>""")


def _methode_suppressions() -> str:
    """Ce que les scénarios notionnels retirent, et la seule exception."""
    return g.depliant("Ce que les comptes notionnels suppriment", f"""
<p>Le principe « seules les cotisations comptent » est appliqué sans exception :
ni minimum contributif, ni minimum garanti, ni ASPA, ni majoration pour enfants,
ni majoration de durée d'assurance, ni AVPF, ni bonifications, ni catégorie
active, ni périodes assimilées, ni réversion, ni décote ni surcote. Le scénario
1 les conserve tous, puisqu'il décrit le droit en vigueur.</p>
<p>Une exception : le <strong>scénario 6</strong>, la
<a href="{g.lien("/")}">proposition du Parti libéral français</a>, remet un
plancher, et un seul. C'est le scénario 4, à deux différences près : un taux
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
d'oracle au scénario 1.</p>
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
les cotisations versées, le capital notionnel, les six pensions. « Brut » a ici
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
<p>Vingt-huit institutions sont recensées dans
<a href="{g.DEPOT}/blob/main/data/sources.yaml">data/sources.yaml</a> : INSEE,
COR, Comité de suivi des retraites, DREES, CNAV, Service des retraites de l'État,
Caisse des dépôts, Direction de la Sécurité sociale, Cour des comptes,
Agirc-Arrco, Assemblée nationale, Union Retraite, CCMSA, CNAVPL, CNBF, DGAFP,
Direction du Budget, ERAFP, Ircantec, caisses des régimes spéciaux, Urssaf,
Légifrance, INED, Eurostat, OCDE, OpenFisca-France, IPP, CEPII.</p>
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

    detail = (depliant_series + depliant_fiabilite
              + _inventaire_section(macro.racine, simulateur.catalogue)
              + depliant_sources)

    return f"""
<h2 style="margin-top:0">Ce que valent les chiffres</h2>
<p class="chapeau">Rien ici n'est à croire sur parole. Chaque série est
recontrôlée, automatiquement, contre le fichier de l'institution qui la
produit. Ce qui ne l'est pas est dit.</p>

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
