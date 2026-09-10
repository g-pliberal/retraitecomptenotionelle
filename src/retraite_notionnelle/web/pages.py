"""Contenu des pages : formulaire, résultats, cas types, méthode, données.

Ce module ne dépend que de la bibliothèque standard et du moteur. Il sert de
référence au portage JavaScript qui fait tourner le site
(``moteur/js/pages.js``) : les deux rendus sont comparés caractère par caractère
par ``tests/js/moteur.test.js``.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from html import escape
from urllib.parse import urlencode

from ..calendrier import MOIS_PAR_AN, en_mois, formater_age
from ..carriere import Metier, bornes_deformation, salaire_moyen_annuel
from ..castypes import CAS_TYPES, GENERATIONS, calculer_cas_types
from ..config import (
    AgeConversionDroitsAcquis,
    PartCotisation,
    ModeAgeReference,
    ModeIndexation,
    Parametres,
    TableConversion,
)
from ..cout import SCENARIOS, calculer_cout
from ..donnees.chargement import DonneeInsuffisante, journal_certification
from ..donnees.depenses import SYSTEMES, DepensesRetraite
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

PROJECTIONS = [
    ("cor_reference", "COR référence — productivité 0,7 %"),
    ("cor_productivite_basse", "COR variante basse — 0,4 %"),
    ("cor_productivite_haute", "COR variante haute — 1,0 %"),
]


#: Les deux façons d'écrire un revenu. Le modèle n'en connaît qu'une — le
#: multiple du salaire moyen, seule qui garde son sens sur quatre-vingts ans —,
#: mais personne ne connaît son salaire dans cette unité-là : c'est l'euro qui
#: est proposé d'abord, et le multiple reste pour qui raisonne en relatif.
UNITES_REVENU = [
    ("euros_mois", "€ bruts par mois"),
    ("moyen", "× le salaire moyen"),
]

#: Ce que porte le champ tant que rien n'a été saisi, dans chaque unité. Un
#: nombre rond proche du salaire moyen plutôt que le salaire moyen exact : le
#: champ est fait pour être remplacé, et « 3 500 » se relit mieux que « 3 475 ».
SALAIRE_DEFAUT = {"euros_mois": 3500.0, "moyen": 1.0}

#: Durée mensuelle de référence du SMIC : 35 heures par semaine ramenées au
#: mois, soit 151,67 heures. Elle ne sert qu'à écrire un repère à l'échelle
#: d'un salaire mensuel.
HEURES_SMIC_PAR_MOIS = 151.67


#: Nombre maximal de métiers d'une carrière, le premier compris. Le formulaire
#: affiche toujours une ligne vide de plus que les métiers saisis : c'est ainsi
#: qu'on en ajoute un, sans une ligne de JavaScript. La borne n'est pas une
#: limite du moteur — il en accepterait autant qu'on veut — mais celle du
#: formulaire : au-delà, ce n'est plus une suite de métiers qu'on décrit, c'est
#: un relevé de carrière année par année, et il se saisit autrement.
METIERS_MAXIMUM = 6

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

#: Rang de chaque métier, tel que le formulaire l'annonce.
RANGS_METIER = ("premier", "deuxième", "troisième", "quatrième", "cinquième",
                "sixième", "septième", "huitième")


#: Mois de naissance. Le droit coupe deux générations en cours d'année — au
#: 1er juillet 1951, au 1er septembre 1961 — et l'âge à la liquidation ne se
#: lit qu'à partir de lui.
MOIS_NAISSANCE = [
    ("1", "janvier"), ("2", "février"), ("3", "mars"), ("4", "avril"),
    ("5", "mai"), ("6", "juin"), ("7", "juillet"), ("8", "août"),
    ("9", "septembre"), ("10", "octobre"), ("11", "novembre"), ("12", "décembre"),
]

#: Mois qui s'ajoutent aux années entières d'un âge.
MOIS_AGE = [(str(m), "0 mois" if m == 0 else f"{m} mois") for m in range(12)]


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
    """Un métier tel que le formulaire le porte : un âge, un statut, un niveau."""

    #: Âge auquel ce métier commence.
    debut: float
    #: Statut d'affiliation sous lequel il est exercé.
    statut: str
    #: Revenu, dans l'unité que ``Saisie.unite_revenu`` désigne : euros bruts
    #: par mois, ou multiple du salaire moyen brut.
    salaire: float


@dataclass
class Saisie:
    """Paramètres d'une simulation, tels que l'utilisateur les a saisis."""

    naissance: int = 1975
    naissance_mois: int = 1
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
        saisie = cls(
            unite_revenu=unite,
            naissance=_entier(parametres, "naissance", defauts.naissance),
            naissance_mois=_entier(
                parametres, "naissance_mois", defauts.naissance_mois
            ),
            sexe="F" if parametres.get("sexe") == "F" else "H",
            statut=statut,
            debut=_age_saisi(parametres, "debut", defauts.debut),
            liquidation=_age_saisi(parametres, "liquidation", defauts.liquidation),
            salaire=salaire,
            metiers=_metiers_saisis(parametres, salaire),
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
        if not 1900 <= self.naissance <= 2020:
            raise ErreurSaisie(
                f"Année de naissance hors du champ du modèle : {self.naissance}. "
                "Attendu entre 1900 et 2020."
            )
        if not 14 <= self.debut <= 40:
            raise ErreurSaisie("Âge de début d'activité attendu entre 14 et 40 ans.")
        if not 40 <= self.liquidation <= 75:
            raise ErreurSaisie("Âge de liquidation attendu entre 40 et 75 ans.")
        if self.liquidation <= self.debut:
            raise ErreurSaisie(
                "L'âge de liquidation doit être postérieur à l'âge de début d'activité."
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
            if not 14 <= metier.debut <= 75:
                raise ErreurSaisie(
                    f"Métier n° {rang} : âge de début attendu entre 14 et 75 ans."
                )
            if metier.debut <= precedent:
                raise ErreurSaisie(
                    f"Métier n° {rang} : il doit commencer après le précédent, "
                    f"qui débute à {_age(precedent)}."
                )
            if metier.debut >= self.liquidation:
                raise ErreurSaisie(
                    f"Métier n° {rang} : il doit commencer avant le départ à la "
                    f"retraite, fixé à {_age(self.liquidation)}."
                )
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
                raise _refus(rang, "Le salaire doit être strictement positif.")
        elif not 0.1 <= valeur <= 10:
            raise _refus(
                rang,
                "Niveau de revenu attendu entre 0,1 et 10 fois le salaire moyen.",
            )

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
        """La carrière comme suite de métiers, le premier compris.

        C'est sous cette forme que le modèle la reçoit ; le formulaire, lui,
        garde le premier métier dans ses champs historiques.
        """
        niveaux = self.niveaux(echelle)
        for rang, niveau in enumerate(niveaux, start=1):
            self._verifier_niveau(niveau, rang, echelle)
        statuts = [self.statut] + [metier.statut for metier in self.metiers]
        debuts = [self.debut] + [metier.debut for metier in self.metiers]
        return [
            Metier(affiliation=statut, age_debut=debut, niveau_salaire=niveau)
            for statut, debut, niveau in zip(statuts, debuts, niveaux)
        ]

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
            f"Ce salaire vaut {g.nombre(niveau, 2)} fois le salaire moyen ; le "
            "modèle en accepte de 0,1 à 10 fois, soit de "
            f"{g.nombre(echelle.mensuel(0.1), 0)} à "
            f"{g.euros(echelle.mensuel(10))} bruts par mois.",
        )

    @property
    def liquidation_mois(self) -> int:
        """Mois qui s'ajoutent aux années entières de l'âge de départ."""
        return en_mois(self.liquidation) % 12

    @property
    def debut_mois(self) -> int:
        return en_mois(self.debut) % 12

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
            scenario_projection=self.projection,
            annee_bascule=self.bascule,
            annee_euros_constants=self.euros,
        )

    def interruptions_analysees(self) -> dict[int, str]:
        """« 1995:1999:education_enfant, 2003:2004:chomage_indemnise » -> dict."""
        plages: dict[int, str] = {}
        for morceau in self.interruptions.replace("\n", ",").split(","):
            morceau = morceau.strip()
            if not morceau:
                continue
            try:
                debut, fin, motif = morceau.split(":")
                for annee in range(int(debut), int(fin) + 1):
                    plages[annee] = motif.strip()
            except ValueError:
                raise ErreurSaisie(
                    f"Interruption mal formée : « {morceau} ». Attendu "
                    "« année_début:année_fin:motif », par exemple "
                    "1995:1999:education_enfant."
                ) from None
        return plages

    def requete(self, **remplacements) -> str:
        champs = {
            "naissance": self.naissance, "naissance_mois": self.naissance_mois,
            "sexe": self.sexe, "statut": self.statut,
            # L'âge s'écrit en années ENTIÈRES et en mois : « 64 ans et sept
            # mois » plutôt que « 64,583333 ». L'adresse reste lisible, et une
            # ancienne adresse portant un âge décimal reste comprise.
            "debut": en_mois(self.debut) // 12, "debut_mois": self.debut_mois,
            "liquidation": en_mois(self.liquidation) // 12,
            "liquidation_mois": self.liquidation_mois,
            "salaire": _nombre(self.salaire), "profil": self.profil,
            "primes": _nombre(self.primes), "enfants": self.enfants,
            "interruptions": self.interruptions, "indexation": self.indexation,
            "lissage": self.lissage,
            "age_reference": self.age_reference, "table": self.table,
            "conversion_acquis": self.conversion_acquis,
            "part_cotisation": self.part_cotisation,
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
            champs[f"metier{rang}_debut"] = _nombre(metier.debut)
            champs[f"metier{rang}_statut"] = metier.statut
            champs[f"metier{rang}_salaire"] = _nombre(metier.salaire)
        champs.update(remplacements)
        return urlencode(champs)


def _metiers_saisis(parametres: dict[str, str],
                    salaire_precedent: float) -> list[MetierSaisi]:
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
                f"Métier n° {rang} : indiquer l'âge auquel il commence, ou "
                "laisser sa ligne entièrement vide."
            )
        if not statut:
            raise ErreurSaisie(
                f"Métier n° {rang} : indiquer le statut d'affiliation."
            )
        salaire_precedent = _reel(
            parametres, f"metier{rang}_salaire", salaire_precedent
        )
        metiers.append(MetierSaisi(
            debut=_reel(parametres, f"metier{rang}_debut", 0.0),
            statut=statut,
            salaire=salaire_precedent,
        ))
    return metiers


def _entier(parametres: dict[str, str], nom: str, defaut: int) -> int:
    valeur = parametres.get(nom)
    if valeur in (None, ""):
        return defaut
    try:
        return int(float(valeur))
    except ValueError:
        raise ErreurSaisie(f"« {nom} » doit être un nombre entier (reçu : {valeur}).") from None


def _reel(parametres: dict[str, str], nom: str, defaut: float) -> float:
    valeur = parametres.get(nom)
    if valeur in (None, ""):
        return defaut
    try:
        return float(str(valeur).replace(",", "."))
    except ValueError:
        raise ErreurSaisie(f"« {nom} » doit être un nombre (reçu : {valeur}).") from None


def _age_saisi(parametres: dict[str, str], nom: str, defaut: float) -> float:
    """Âge lu en années entières plus un nombre de mois.

    Le formulaire envoie deux champs — ``liquidation`` et ``liquidation_mois``
    —, et l'adresse les porte tous deux : « 64 ans et sept mois » s'y lit tel
    quel. Une adresse ancienne ne portant qu'un âge décimal — ``liquidation=64.5``
    — reste valide et vaut ce qu'elle a toujours valu : le champ des mois est
    alors absent, et la partie décimale fait foi.
    """
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
    _population: Population | None = None
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

    def population(self) -> Population:
        if self._population is None:
            self._population = Population(self.base.racine_donnees)
        return self._population

    def cout(self):
        """Le coût agrégé des cinq systèmes — deux secondes de calcul, une fois."""
        if self._cout is None:
            self._cout = calculer_cout(
                self.simulateur(), self.depenses(), self.population())
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
            interruptions=saisie.interruptions_analysees(),
            nombre_enfants=saisie.enfants,
            part_primes=saisie.primes,
            identifiant="assuré",
        )
        return simulateur.simuler(carriere)


#: Titre de chaque page, dans l'ordre de la navigation.
TITRES = {
    "/": "Simuler",
    "/cas-types": "Cas types",
    "/cout": "Coût",
    "/methode": "Méthode",
    "/donnees": "Données",
}


def rendre(contexte: Contexte, chemin: str,
           parametres: dict[str, str] | None = None) -> tuple[str, str]:
    """Contenu d'une page : ``(titre, corps HTML)``.

    Point d'entrée unique du rendu : le navigateur en remplace le contenu de
    ``<main>``. Les erreurs de saisie sont rendues dans la page, jamais levées :
    une adresse mal formée doit afficher un message, pas une trace d'exécution.
    """
    if chemin == "/cas-types":
        return TITRES[chemin], _cas_types(contexte)
    if chemin == "/cout":
        return TITRES[chemin], _cout(contexte)
    if chemin == "/methode":
        return TITRES[chemin], _methode(contexte)
    if chemin == "/donnees":
        return TITRES[chemin], _donnees(contexte)

    try:
        saisie = Saisie.depuis_requete(parametres or {})
    except ErreurSaisie as erreur:
        saisie = Saisie(demandee=False)
        return TITRES["/"], (
            _presentation() + _erreur(str(erreur)) + _formulaire(saisie, contexte)
        )

    corps = _presentation() + _formulaire(saisie, contexte)
    if saisie.demandee:
        try:
            corps += _resultats(contexte, saisie)
        except (ErreurSaisie, DonneeInsuffisante, KeyError, ValueError) as erreur:
            corps += _erreur(str(erreur))
    return TITRES["/"], corps


def statuts(contexte: Contexte) -> list[dict[str, str]]:
    affiliations = contexte.simulateur().affiliations
    return [{"code": code, "libelle": affiliations.libelle(code)}
            for code in affiliations.codes]


# -- fragments ---------------------------------------------------------------


def _erreur(message: str) -> str:
    return f'<div class="erreur"><strong>Saisie refusée.</strong> {escape(message)}</div>'


def _presentation() -> str:
    return f"""
<p class="chapeau">Ce simulateur calcule, pour une même carrière, ce que verse le
système de retraite français tel qu'il est, et ce que verserait un système
en <strong>comptes notionnels</strong> — pension strictement proportionnelle aux
cotisations versées, divisée par l'espérance de vie restante à la liquidation —
appliqué de deux façons : <strong>rétroactivement</strong> depuis 1941, ou
seulement <strong>à compter de 2026</strong>.</p>

<p>Les cinq montants qu'il affiche sont ceux de la <strong>première pension</strong>,
au premier mois de retraite : celle de l'année du départ pour qui est déjà
retraité, celle de l'année du départ à venir pour qui est encore en activité.
Jamais la pension d'aujourd'hui d'un retraité parti il y a vingt ans. Chacun est
donné <strong>deux fois</strong> : en euros d'aujourd'hui, et tel qu'il serait
inscrit sur le virement le mois du départ — la conversion n'est ainsi à refaire
de tête ni dans un sens ni dans l'autre.</p>

<div class="note"><strong>À lire avant les chiffres.</strong> Le scénario
rétroactif n'est pas une proposition de réforme : c'est un contrefactuel, qui
mesure ce qu'aurait produit une règle purement contributive appliquée depuis
l'origine de la répartition. L'essentiel de l'écart qu'il affiche vient de la
<a href="{g.lien('/methode', 'indexation')}">règle d'indexation</a>, pas du passage aux comptes
notionnels — le simulateur permet de séparer les deux effets.</div>
"""


def _formulaire(saisie: Saisie, contexte: Contexte) -> str:
    affiliations = contexte.simulateur().affiliations
    statuts = [(code, affiliations.libelle(code)) for code in affiliations.codes]

    identite = "".join([
        g.champ("naissance", "Année de naissance", saisie.naissance,
                type_="number", min="1900", max="2020", step="1"),
        g.liste("naissance_mois", "Mois de naissance", MOIS_NAISSANCE,
                str(saisie.naissance_mois),
                "deux générations sont coupées en cours d'année par les textes"),
        g.liste("sexe", "Sexe", [("H", "Homme"), ("F", "Femme")], saisie.sexe,
                "table de mortalité unisexe par défaut"),
        g.champ("liquidation", "Âge de départ à la retraite",
                en_mois(saisie.liquidation) // 12,
                "effectif si vous êtes déjà retraité, souhaité sinon : "
                "c'est la date à laquelle tout le calcul se place",
                type_="number", min="40", max="75", step="1"),
        g.liste("liquidation_mois", "…et mois", MOIS_AGE,
                str(saisie.liquidation_mois),
                "la pension prend effet le premier du mois"),
    ])

    avance = "".join([
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
                "revalorisation des comptes et des pensions"),
        g.champ("lissage", "Lissage de l'indexation", saisie.lissage,
                "moyenne glissante sur la règle choisie, en années : "
                "1 = aucun, 5 = comme l'Italie",
                type_="number", min="1", max=str(LISSAGE_MAXIMUM), step="1"),
        g.liste("age_reference", "Âge de référence", AGES_REFERENCE, saisie.age_reference),
        g.liste("table", "Table de conversion", TABLES, saisie.table),
        g.liste("part_cotisation", "Part de la cotisation portée au compte",
                PARTS_COTISATION, saisie.part_cotisation,
                "salariale seule, ou salariale et patronale"),
        g.liste("conversion_acquis", "Conversion des droits acquis",
                CONVERSIONS_ACQUIS, saisie.conversion_acquis,
                "âge auquel les droits figés à la bascule sont convertis"),
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
<form class="carte" method="get" action="{g.lien('/')}">
  <h2 style="margin-top:0">Simuler une carrière</h2>
  <div class="grille">{identite}</div>
  <h3>Les métiers exercés</h3>
  <p class="discret">On faisait autrefois le même métier toute sa vie ; c'est
  devenu l'exception. Chaque changement fait passer d'un régime à un autre, donc
  d'un taux de cotisation et d'un barème à un autre — et c'est exactement ce
  qu'un compte notionnel enregistre. Ajouter un métier, c'est remplir la
  dernière ligne ; une carrière d'un seul métier la laisse vide.</p>
  {_choix_unite(saisie)}
  {_metiers(saisie, statuts, contexte.echelle(saisie))}
  <details>
    <summary>Options de modélisation (profil, indexation, âge de référence, projection)</summary>
    <div class="grille">{avance}</div>
  </details>
  <p style="margin-top:1.4rem"><button type="submit">Calculer les cinq scénarios</button></p>
</form>
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
                       min="0.1", max="10", step="0.05")

    aide = ("en euros bruts par mois" if bref else
            "la ligne « brut » de la fiche de paie, avant cotisations et impôt, "
            f"en euros d'aujourd'hui — SMIC {g.euros(echelle.smic)}, moyenne "
            f"{g.euros(echelle.mensuel(1))}, plafond {g.euros(echelle.plafond)}")
    return g.champ(nom, "Salaire brut mensuel", valeur, aide, type_="number",
                   min="0", step="10")


def _aide_profil(profil: str) -> str:
    """Ce que le profil fait du salaire saisi, en toutes lettres.

    Sans elle, saisir « 2 900 € par mois » se lit comme la promesse de gagner
    2 900 € chaque année de sa vie, alors que le salaire saisi est celui du
    milieu de carrière et que le profil le déforme aux deux bouts.
    """
    debut, fin = bornes_deformation(profil)
    if debut == fin:
        return "le salaire saisi vaut pour toutes les années de la carrière"
    return (f"le salaire saisi est celui du milieu de carrière : ×{g.nombre(debut, 2)} "
            f"au premier emploi, ×{g.nombre(fin, 2)} au dernier")


def _choix_unite(saisie: Saisie) -> str:
    """Le menu des deux unités, une fois pour toute la carrière.

    Il précède les métiers plutôt qu'il ne les accompagne : une unité par métier
    n'aurait décrit aucune carrière réelle, et aurait posé six fois la même
    question.
    """
    return '<div class="unite">' + g.liste(
        "unite_revenu", "Salaires saisis en", UNITES_REVENU, saisie.unite_revenu,
    ) + "</div>"


def _metiers(saisie: Saisie, statuts: list[tuple[str, str]],
             echelle: "Echelle") -> str:
    """Une ligne par métier, plus une ligne vide pour en ajouter un.

    C'est ce qui permet d'allonger la carrière sans une ligne de JavaScript :
    la ligne vide est renvoyée avec le reste du formulaire, et devient un métier
    dès qu'on la remplit. Une ligne de plus apparaît alors à sa suite, jusqu'à
    ``METIERS_MAXIMUM``.
    """
    lignes = [_ligne_metier(
        1,
        g.champ("debut", "Âge de début d'activité", en_mois(saisie.debut) // 12,
                type_="number", min="14", max="40", step="1")
        + g.liste("debut_mois", "…et mois", MOIS_AGE, str(saisie.debut_mois),
                  "l'année d'entrée n'est complète que si l'on entre en janvier")
        + g.liste("statut", "Statut d'affiliation", statuts, saisie.statut)
        + _champ_revenu("salaire", saisie, echelle, _nombre(saisie.salaire)),
    )]

    for rang, metier in enumerate(saisie.metiers, start=2):
        lignes.append(_ligne_metier(
            rang, _champs_metier(rang, _nombre(metier.debut), metier.statut,
                                 _nombre(metier.salaire), statuts, saisie,
                                 echelle)))

    # La ligne vide : elle n'existe que tant qu'il reste de la place, et son
    # statut n'est pas présélectionné — un statut choisi par défaut ferait
    # naître un métier que personne n'a demandé.
    rang = len(saisie.metiers) + 2
    if rang <= METIERS_MAXIMUM:
        lignes.append(_ligne_metier(
            rang, _champs_metier(rang, "", "", "", statuts, saisie, echelle),
            vide=True))

    return f'<div class="metiers">{"".join(lignes)}</div>'


def _champs_metier(rang: int, debut: str, statut: str, salaire: str,
                   statuts: list[tuple[str, str]], saisie: Saisie,
                   echelle: "Echelle") -> str:
    """Les trois champs d'un métier qui suit le premier.

    Le mois du changement n'est pas demandé : ce qui se date au mois, c'est
    l'entrée dans la vie active et le départ à la retraite, parce que ces deux
    bornes tronquent une année civile. Un changement de métier, lui, ne fait que
    déplacer des mois d'un statut à l'autre à l'intérieur de la carrière.
    """
    return (
        g.champ(f"metier{rang}_debut", "Âge du changement", debut,
                "âge auquel ce métier commence", type_="number",
                min="14", max="75", step="1")
        + g.liste(f"metier{rang}_statut", "Statut d'affiliation",
                  [("", "— aucun —")] + statuts, statut)
        + _champ_revenu(f"metier{rang}_salaire", saisie, echelle, salaire,
                        bref=True)
    )


def _ligne_metier(rang: int, champs: str, vide: bool = False) -> str:
    titre = (f"{RANGS_METIER[rang - 1].capitalize()} métier" if not vide
             else "Un autre métier ?")
    classe = "metier facultatif" if vide else "metier"
    return (f'<div class="{classe}"><p class="rang">{escape(titre)}</p>'
            f'<div class="grille">{champs}</div></div>')


def _resume_parcours(contexte: Contexte, saisie: Saisie) -> str:
    """La suite des métiers, en une phrase — et la convention qui la borne.

    Muet pour une carrière d'un seul métier : il n'y a rien à récapituler, le
    formulaire juste au-dessus le dit déjà.
    """
    parcours = saisie.parcours(contexte.echelle(saisie))
    if len(parcours) < 2:
        return ""

    affiliations = contexte.simulateur().affiliations
    bornes = [metier.age_debut for metier in parcours] + [saisie.liquidation]
    etapes = [
        f"{escape(affiliations.libelle(metier.affiliation))} de {_age(bornes[rang])} "
        f"à {_age(bornes[rang + 1])}"
        for rang, metier in enumerate(parcours)
    ]
    return (
        f'<p class="discret">Carrière en {len(parcours)} métiers : '
        + ", puis ".join(etapes) + ". L'année d'un changement revient au métier "
        "qui en occupe le plus de mois — les régimes liquident à l'année, et une "
        "année n'a qu'un statut — mais le revenu porté au compte reste la somme "
        "de ce que les deux ont payé.</p>"
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
        f'<p class="discret" style="margin:0 0 1.4rem">Deux fois le même montant, '
        f"dans deux unités : le <strong>grand chiffre</strong> est {valeur} — le "
        "seul qui se compare à un salaire ou à un loyer que vous connaissez ; "
        f"celui d'à côté est {autre}.</p>"
    )


def _lecture_des_montants(comparaison: Comparaison, saisie: Saisie) -> str:
    """À quelle date se rapportent les montants affichés, et en quels euros.

    C'est la première question que pose un lecteur devant les cinq barres :
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

    return f"""
<div class="note"><strong>De quand sont ces chiffres ?</strong> {quand}
{unites}
Ce que compare cette page, ce sont cinq façons de CALCULER une pension de
départ, pas cinq façons de la revaloriser ensuite : le premier mois de retraite
est le seul instant où les cinq scénarios se laissent mettre côte à côte, et
c'est donc à cet instant que tous les cinq sont calculés.</div>
<p class="discret" style="margin-top:1.5rem">Montants <strong>bruts</strong>
mensuels — avant CSG, CRDS et prélèvements sociaux, avant impôt sur le revenu —
comme le salaire saisi plus haut : le <strong>taux de remplacement</strong>, qui
rapporte la pension annuelle au dernier revenu d'activité ramené à l'année
pleine, compare donc un brut à un brut, et il est plus bas qu'un taux calculé
sur des nets, la pension étant moins prélevée que le salaire. Ses deux termes
étant pris dans les euros de leur propre année, il ne dépend pas de l'unité
d'affichage. Le chiffre mis en avant, lui, est en euros constants de
{saisie.euros}, c'est-à-dire au pouvoir d'achat de {saisie.euros} : seule unité
qui permette de comparer des liquidations d'années différentes.
Fiabilité du résultat :
<span class="etiquette-fiabilite">{escape(str(comparaison.fiabilite))}</span></p>"""


def _resultats(contexte: Contexte, saisie: Saisie) -> str:
    comparaison = contexte.simuler(saisie)
    carriere = comparaison.carriere
    retro = comparaison.notionnel_retroactif
    ecart = retro.ecart_age
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
        <span class="somme">{g.euros(courants[cle] / 12)}</span>
        <span class="unite">par mois, en euros de {annee_depart}</span>
      </span>""" if deux_unites else ""
        return f"""
<div class="scenario">
  <div class="entete">
    <span class="titre">{escape(titre)}</span>
    <span class="montant">
      <span class="chiffre principal">
        <span class="somme">{g.euros(montant / 12)}</span>
        <span class="unite">{unite_reference}</span>
        <span class="annuel">{g.euros(montant)} par an</span>
      </span>{depart}
    </span>
  </div>
  <div class="barre {cle}"><span style="width:{montant / reference * 100:.1f}%"></span></div>
  <div class="glose">{glose} · taux de remplacement
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
    )

    anticipation = (
        f"départ {g.nombre(abs(ecart.ecart), 2).rstrip('0').rstrip(',')} ans "
        + ("plus tôt" if ecart.anticipe else "plus tard")
    )
    fiches = "".join([
        g.fiche("années cotisées", str(len(carriere.annees_cotisees))),
        # La date, et pas seulement l'année : la pension prend effet le premier
        # du mois, et c'est ce mois que l'utilisateur vient de choisir.
        g.fiche("liquidation", f"{_age(carriere.age_liquidation)} "
                f'<span class="discret">en {carriere.date_liquidation}</span>'),
        g.fiche(f"âge de référence — {anticipation}",
                f"{_age(ecart.age_reference)}"),
        # Deux décimales, et non une : le lecteur qui refait la division
        # « capital ÷ coefficient » doit retrouver la pension affichée. À 25,7
        # au lieu de 25,67 il tombait un euro à côté, et doutait du reste.
        g.fiche("coefficient de conversion", g.nombre(conversion.diviseur, 2)),
        # Le capital est un montant de l'année de liquidation, quand les cinq
        # pensions ci-dessous sont mises en avant en euros de l'année de
        # référence : sans l'unité, deux grandeurs de nature différente se
        # touchaient sans que rien ne les distingue.
        g.fiche(f"capital notionnel rétroactif, en euros de {annee_depart}",
                g.euros(retro.capital_notionnel)),
    ])

    capitalisation = ""
    if comparaison.actuel.pension_hors_repartition > 0:
        montant = comparaison.en_euros_constants(
            comparaison.actuel.pension_hors_repartition
        )
        capitalisation = (
            f'<p class="discret">Hors répartition, servi à part : '
            f"{g.euros(montant / 12)} par mois de RAFP, en euros de "
            f"{saisie.euros} comme les cinq montants ci-dessus. Ce régime est "
            "PROVISIONNÉ — sa rente sort d'un placement, non de la cotisation "
            "des actifs —, si bien qu'une réforme de la répartition ne "
            "l'atteint pas. Il est donc retiré des cinq totaux et servi à "
            "l'identique dans les cinq scénarios : c'est la seule façon de "
            "comparer ce qui est comparable.</p>"
        )

    minimum = ""
    if comparaison.actuel.minimum_applique:
        minimum = (
            '<p class="discret">Le minimum contributif s\'applique dans le '
            "scénario 1 ; il est supprimé dans les scénarios 2 à 5.</p>"
        )

    ouverture = ""
    if not comparaison.actuel.liquidation_ouverte:
        age = comparaison.actuel.age_ouverture_opposable
        attente = (f" — il faut attendre {g.nombre(age, 2)} ans"
                   if age is not None else "")
        ouverture = (
            '<p class="note avertissement">Le droit en vigueur <strong>n\'ouvre pas'
            "</strong> cette liquidation à "
            f"{g.nombre(comparaison.carriere.age_liquidation, 2)} ans{attente}. "
            "Ni l'âge légal du régime, ni le départ anticipé pour carrière "
            "longue ne le permettent. Le montant du scénario 1 reste calculé, "
            "parce qu'il faut bien comparer les cinq scénarios sur la même "
            "carrière, mais il ne décrit aucune pension que le système actuel "
            "servirait.</p>"
        )

    return f"""
<h2>Résultats</h2>
<div class="carte">
  <div class="fiches">{fiches}</div>
  {_resume_parcours(contexte, saisie)}
</div>
<div class="carte">
  {_legende_des_unites(comparaison, saisie)}
  {scenarios}
  {_lecture_des_montants(comparaison, saisie)}
  {capitalisation}
  {minimum}
  {ouverture}
</div>
{_fourchette(contexte, saisie, comparaison)}
{_decomposition(contexte, saisie, comparaison)}
{_contribution_employeur(comparaison)}
{_cascade(comparaison, saisie)}
{_detail(contexte, comparaison)}
"""


NATURES_PART_EMPLOYEUR = {
    "appelee": "contribution appelée par décret ou par arrêté",
    "implicite": "taux implicite reconstitué par les documents budgétaires",
    "repli": "aucune série publiée : effort du privé de la même année",
}


#: Les cinq scénarios, dans l'ordre où la page les affiche, avec le libellé
#: court que la fourchette leur donne.
SCENARIOS_AFFICHES = (
    ("actuel", "1. Système actuel"),
    ("notionnel_retroactif", "2. Notionnel rétroactif"),
    ("notionnel_prospectif", "3. Notionnel à la bascule"),
    ("notionnel_retroactif_employeur", "4. Rétroactif, avec le patronal"),
    ("notionnel_prospectif_employeur", "5. Bascule, avec le patronal"),
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
        return f"""
<h2>Ce que l'hypothèse pèse</h2>
<p class="note">Rien, ici : la carrière s'achève en {liquidation}, et les séries
sont observées jusqu'en {derniere_observee}. <strong>Aucune année projetée
n'entre dans ce calcul</strong> — les montants ci-dessus sont identiques dans
les trois scénarios macroéconomiques, parce qu'aucun d'eux ne s'y applique.</p>"""

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
            g.euros(bas / 12),
            g.euros(montants[saisie.projection][scenario] / 12)
            if saisie.projection in montants else "—",
            g.euros(haut / 12),
            g.pourcentage(amplitude),
        ])

    retenu = dict(PROJECTIONS)[saisie.projection]
    reference = comparaison.en_euros_constants(
        comparaison.notionnel_retroactif.pension_annuelle) / 12
    ecart_2 = (haute["notionnel_retroactif"] / basse["notionnel_retroactif"] - 1.0
               if basse["notionnel_retroactif"] > 0 else float("nan"))

    return f"""
<h2>Ce que l'hypothèse pèse</h2>
<p>Le compte est revalorisé chaque année de {debut} à {liquidation}, soit
{total} années — dont <strong>{projetees} après {derniere_observee}</strong>,
la dernière année observée. Ces {g.pourcentage(projetees / total)} du calcul ne
reposent sur aucune mesure : elles reposent sur l'hypothèse de croissance de la
productivité, celle que le Conseil d'orientation des retraites fixe et révise.</p>
<p>La même carrière, rejouée sous les trois hypothèses du COR. Le scénario 2
passe de {g.euros(basse["notionnel_retroactif"] / 12)} à
{g.euros(haute["notionnel_retroactif"] / 12)} par mois, soit
<strong>{g.pourcentage(ecart_2)} d'amplitude</strong> autour des
{g.euros(reference)} affichés plus haut.</p>
{g.tableau(
    ["Scénario", "Productivité 0,4 %", escape(retenu), "Productivité 1,0 %",
     "Amplitude"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
)}
<p class="discret">Montants mensuels bruts, en euros constants de {saisie.euros}.
La fourchette ne fait varier que la <strong>productivité</strong> — 0,4 %, 0,7 %
et 1,0 % par an, le jeu que le COR retient depuis juin 2025. Elle laisse fixes
les autres hypothèses de la projection, et n'est donc pas un intervalle de
confiance : l'inflation y reste à 1,75 %, l'emploi salarié constant, et la
législation inchangée. C'est une mesure de sensibilité à un paramètre, pas une
borne sur l'avenir — l'avenir peut sortir de cette fourchette.</p>"""


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
            ["Sur toute la carrière, en euros courants cumulés", "", "Montant"],
            [
                ["Part salariale", "ce que l'assuré supporte — scénarios 2 et 3",
                 g.euros(employeur.agent)],
                ["Part patronale", "ce que verse l'employeur",
                 g.euros(employeur.employeur)],
                ["Total", "scénarios 4 et 5", g.euros(employeur.total)],
            ],
            ["", "", "nombre"],
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

    return f"""
<h2>Qui verse la cotisation</h2>
<p>Une cotisation retraite a deux parts : ce que l'assuré supporte, et ce que
son employeur verse. Les scénarios 2 et 3 ne portent au compte que la première ;
les scénarios 4 et 5 y ajoutent la seconde, et ne changent rien d'autre.</p>
{partage}{public}"""


def _decomposition(contexte: Contexte, saisie: Saisie,
                   comparaison: Comparaison) -> str:
    """Sépare l'effet de la règle d'indexation de celui des comptes notionnels.

    Le tableau ne s'affiche que sur la règle par défaut : ailleurs, l'utilisateur
    a lui-même choisi sa ligne de comparaison, et la première ligne du tableau ne
    serait plus celle qu'il regarde. Le défaut est lu sur la saisie, non écrit
    ici : ce test a nommé « triple_lock_inverse » en dur jusqu'à ce que le défaut
    change, et le tableau aurait alors disparu de la page d'accueil.
    """
    if saisie.indexation != Saisie.indexation:
        return ""

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
            g.euros(mensuel),
            g.pourcentage(variante.variation("notionnel_retroactif"), signe=True),
        ])

    return f"""
<h2>D'où vient l'écart</h2>
<p>La même carrière, le même calcul notionnel rétroactif, avec neuf règles de
revalorisation des comptes. La <strong>première ligne est celle que la
simulation applique</strong> : la croissance de la masse salariale, c'est-à-dire
le rendement qu'un système en répartition peut servir sans changer son taux de
cotisation. La deuxième n'est pas une hypothèse mais un relevé : le coefficient
que les arrêtés ont réellement appliqué aux salaires portés au compte, celui-là
même dont le scénario 1 se sert. Les quatre suivantes sont le triple lock
inversé et ses variantes — mêmes trois séries, inflation, salaire moyen,
productivité, seul change ce qu'on en retient. La colonne « rendement » est le
facteur par lequel les cotisations ont été multipliées entre leur versement et
la liquidation.</p>
{g.tableau(
    ["Règle d'indexation", "Rendement cumulé",
     f"Pension mensuelle, en euros de {saisie.euros}",
     "Écart au système actuel"],
    lignes,
    ["", "nombre", "nombre", "nombre"],
)}
<p class="discret">La ligne de repère est la <strong>revalorisation réellement
pratiquée</strong> : c'est celle du droit positif. L'écart entre elle et le
système actuel mesure l'effet propre des comptes notionnels ; tout ce qui sépare
les autres lignes de celle-là mesure l'effet de la règle d'indexation. La ligne
« Prix » ne joue pas ce rôle, contrairement à ce que cette page a longtemps dit :
le régime général ne revalorise sur les prix que depuis 1987, et suivait les
salaires avant. Le triple lock inversé, lui, compare deux taux nominaux
(inflation, salaire moyen) à un taux réel (productivité) : dès que l'inflation
dépasse la productivité — soit presque toute la période 1945-1985 — c'est la
productivité qui l'emporte, et la valeur réelle des comptes s'effondre. Les
lignes « médiane » et « moyenne » gardent ses trois séries et n'en changent que
la statistique.</p>
<p class="discret">La première ligne, la <strong>masse salariale</strong>, est
la seule qui repose sur un argument théorique et non sur un choix : c'est
l'assiette des cotisations, donc le taux de rendement qu'un système en
répartition peut servir sans toucher à son taux de cotisation. C'est pourquoi
elle est le défaut du simulateur. Elle vaut salaire moyen + emploi salarié, et
l'emploi salarié a doublé depuis 1950 : c'est la règle la plus généreuse du
tableau, et de loin. Elle a sa propre incohérence, à
garder en tête : elle crédite le compte du rendement que le système ENTIER
dégage, alors que les scénarios 2 et 3 n'y versent que la part salariale de la
cotisation. C'est aux scénarios 4 et 5, qui portent la cotisation entière,
qu'elle se compare sans biais. La ligne « PIB nominal » est la même idée poussée
à l'assiette la plus large : elle capte le déplacement de la valeur ajoutée vers
les revenus non salariaux, que la masse salariale subit.</p>
<p class="discret">Le <strong>lissage</strong>, dans les options, est
indépendant de la règle : il applique une moyenne glissante au taux que la règle
produit, quelle qu'elle soit, et s'applique donc à toutes les lignes de ce
tableau à la fois. Ce qu'il vise n'est pas le niveau mais la loterie de cohorte :
sur le PIB nominal brut, une cotisation de 1980 vaut ×5,44 à une liquidation de
2019 et ×5,18 en 2020 — attendre un an fait perdre, parce que l'année traversée
s'est mal passée. Lissée sur cinq ans, la même cotisation vaut ×6,64 puis ×6,71,
et le recul disparaît. « PIB nominal » lissé sur cinq ans, c'est la règle
italienne ; le modèle en reprend le taux, pas le reste du système italien.</p>
"""


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
         g.euros(acquis.pension_figee) + " par an"],
        [f"b) × diviseur à {_age(acquis.age_conversion)}",
         f"coefficient de conversion en {saisie.bascule} : "
         f"{g.nombre(acquis.diviseur, 2)}",
         g.euros(acquis.capital_a_la_bascule)],
        [f"c) × revalorisation {saisie.bascule}-{liquidation}",
         f"règle d'indexation retenue : ×"
         f"{g.nombre(acquis.coefficient_revalorisation, 3)}",
         g.euros(acquis.capital)],
        [f"d) + cotisations {saisie.bascule}-{liquidation - 1}",
         "versées au régime unique, revalorisées de même",
         g.euros(capital_apres)],
        ["e) = capital notionnel", "ce que la carrière a effectivement financé",
         g.euros(prospectif.capital_notionnel)],
        [f"f) ÷ diviseur à {_age(age_liquidation)}",
         f"coefficient de conversion en {liquidation} : {g.nombre(diviseur, 2)}",
         g.euros(prospectif.pension_annuelle) + " par an"],
    ]

    part_acquis = acquis.capital / prospectif.capital_notionnel
    neutralite = ""
    if saisie.conversion_acquis == "reference" and acquis.age_conversion > age_liquidation:
        neutralite = (
            f"<p>Ligne b) : les droits déjà ouverts sont convertis au diviseur de "
            f"l'âge de référence ({_age(acquis.age_conversion)}), alors que la "
            f"rente sera servie depuis {_age(age_liquidation)}. L'anticipation "
            f"est donc payée une seconde fois, sur le passé. L'option « conversion "
            f"des droits acquis à l'âge de départ effectif » supprime cet "
            f"abattement, et c'est la convention qu'une réforme réelle "
            f"retiendrait.</p>"
        )

    return f"""
<h2>Du scénario 1 au scénario 3, ligne à ligne</h2>
<p>Le scénario 3 n'est pas le scénario 1 diminué d'un pourcentage : c'est une
autre formule appliquée à la même carrière. Montants en <strong>euros de
{liquidation}</strong>, l'année du départ — la chaîne de calcul est
arithmétique, la convertir ligne à ligne au pouvoir d'achat d'une autre année la
rendrait fausse. {renvoi_cascade}</p>
{g.tableau(
    ["Étape", "Ce qu'elle fait", "Résultat"],
    lignes,
    ["", "", "nombre"],
)}
<p>À comparer aux {g.euros(actuel)} par an du système actuel. L'écart ne vient
d'aucun abattement appliqué au scénario 1 : il vient de ce que le capital
réellement constitué, {g.euros(prospectif.capital_notionnel)}, ne finance pas
les {g.euros(actuel * diviseur)} que le droit en vigueur promet sur
{g.nombre(diviseur, 1)} années de retraite.</p>
{neutralite}
<p class="discret">Les droits acquis avant {saisie.bascule} pèsent
{g.pourcentage(part_acquis)} du capital final. Cette part décroît de génération
en génération : c'est elle qui étale la réforme dans le temps, et non un
dispositif transitoire.</p>
"""


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
    # unité dans laquelle la chaîne de calcul s'additionne. Les cinq blocs du
    # haut, eux, mettent en avant les euros de l'année de référence. Sans dire
    # laquelle est laquelle, la dernière ligne prétendait valoir « le montant
    # de la ligne 1 ci-dessus » en désignant un nombre que la ligne 1
    # n'affichait pas.
    annee = comparaison.carriere.annee_liquidation
    annee_reference = comparaison.parametres.annee_euros_constants
    renvoi = (
        "C'est l'unité de la <em>seconde</em> colonne des cinq scénarios, celle "
        "du virement — pas celle du chiffre mis en avant, qui les ramène au "
        f"pouvoir d'achat de {annee_reference}."
        if annee != annee_reference else
        "Le départ tombant sur l'année de référence, c'est aussi l'unité des "
        "cinq montants affichés plus haut."
    )
    lignes_actuel: list[list[str]] = [
        [escape(nom_regime(pension.regime)), g.euros(pension.montant),
         g.franciser(escape(pension.detail))]
        for pension in pensions
    ]
    if lignes_actuel and actuel.avantages_appliques:
        lignes_actuel.append([
            "<strong>Sous-total contributif</strong>",
            "<strong>" + g.euros(actuel.total_contributif) + "</strong>",
            '<span class="discret">ce que la carrière a ouvert par ses seules '
            "cotisations</span>",
        ])
    for avantage in actuel.avantages_appliques:
        lignes_actuel.append([
            "+ " + escape(avantage.libelle),
            g.euros(avantage.montant),
            f'<span class="discret">{escape(avantage.detail)}</span>',
        ])
    if lignes_actuel:
        lignes_actuel.append([
            "<strong>Pension du système actuel</strong>",
            "<strong>" + g.euros(actuel.pension_annuelle) + "</strong>",
            '<span class="discret">c\'est le scénario 1 ci-dessus, pris '
            "dans les euros de son année de départ</span>",
        ])

    regimes = g.tableau(
        ["Régime, puis avantage", f"Pension annuelle, en euros de {annee}",
         "Calcul"],
        lignes_actuel,
        ["", "nombre", ""],
    ) if lignes_actuel else "<p>Aucun droit liquidé dans le système actuel.</p>"

    part = ""
    if actuel.avantages_appliques and actuel.pension_annuelle > 0:
        gratuit = sum(a.montant for a in actuel.avantages_appliques)
        part = (
            f'<p>Les avantages non contributifs pèsent {g.euros(gratuit)} par an, '
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
             "×" + g.nombre(retro.compte.rendement_cumule, 2)],
            [f"Capital notionnel à la liquidation, en euros de {annee}",
             g.euros(retro.capital_notionnel)],
            ["Divisé par le coefficient de conversion",
             g.nombre(retro.conversion.diviseur, 2)
             + f" ({escape(retro.conversion.table)})"],
            [f"Pension annuelle, en euros de {annee}",
             g.euros(retro.pension_annuelle)],
        ],
        ["", "nombre"],
    )

    return f"""
<h2>Le détail du calcul</h2>
<p class="note">Toute cette section est en <strong>euros de {annee}</strong>,
l'année du départ. {renvoi} C'est la seule unité dans laquelle une chaîne de
calcul s'additionne : convertir chaque ligne au pouvoir d'achat d'une autre
année ferait des totaux faux.</p>
<h3>Scénario 1 — de quoi votre pension actuelle est faite</h3>
<p>Chaque régime d'abord, puis les avantages que le droit en vigueur ajoute
par-dessus. Les lignes s'additionnent exactement : le total est la pension du
scénario 1.</p>
{regimes}
{part}
<h3>Scénario 2 — construction du compte notionnel rétroactif</h3>
{compte}
<details>
  <summary>Les résultats complets en JSON</summary>
  <pre class="json">{escape(json.dumps(comparaison.dictionnaire(), ensure_ascii=False, indent=2))}</pre>
</details>
<p class="discret">L'adresse de cette page contient tous les paramètres :
elle peut être citée ou partagée telle quelle.</p>
"""


def _cas_types(contexte: Contexte) -> str:
    resultat = calculer_cas_types(contexte.simulateur())

    def grille(scenario: str) -> str:
        lignes = []
        for cas in CAS_TYPES:
            cellules: list[str | g.Cellule] = [
                f'<span title="{escape(cas.commentaire)}">{escape(cas.libelle)}</span>'
            ]
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
        )

    echecs = ""
    if resultat.echecs:
        elements = "".join(
            f"<li>{escape(code)} / {generation} : {escape(motif)}</li>"
            for (code, generation), motif in sorted(resultat.echecs.items())
        )
        echecs = f"<h3>Combinaisons non calculées</h3><ul class='serree'>{elements}</ul>"

    return f"""
<h2 style="margin-top:0">Le cas général</h2>
<p class="chapeau">Douze carrières représentatives × sept générations. Chaque
cellule est l'écart de pension par rapport au système actuel, à carrière
identique : négatif = pension plus faible qu'aujourd'hui.</p>

<h3>Scénario 2 — comptes notionnels rétroactifs depuis 1941</h3>
{grille("notionnel_retroactif")}
<p class="discret">Les générations anciennes sont les plus touchées : leurs
cotisations, versées quand l'inflation dépassait la productivité, ont été
revalorisées à un taux très inférieur à la hausse des prix.</p>

<h3>Scénario 3 — comptes notionnels à compter de la bascule</h3>
{grille("notionnel_prospectif")}
<p class="discret">Les générations déjà retraitées sont inchangées : leurs droits
sont intégralement acquis avant la bascule. Les indépendants et professions
libérales progressent parce que le régime unique relève leur taux de cotisation
et déplafonne leur assiette — un effort contributif accru, pas un avantage
accordé.</p>

<h3>Scénario 4 — le scénario 2, part patronale comprise</h3>
{grille("notionnel_retroactif_employeur")}
<p class="discret">Toutes les lignes bougent, sauf celles des non-salariés —
artisan, exploitant agricole, profession libérale — qui n'ont pas d'employeur et
pour qui ce scénario est le scénario 2. Les lignes publiques bougent le plus :
la contribution de leur employeur est un taux d'équilibre, sans commune mesure
avec la part patronale d'un salarié.</p>

<h3>Scénario 5 — le scénario 3, part patronale comprise</h3>
{grille("notionnel_prospectif_employeur")}
<p class="discret">Même lecture, à compter de la bascule : les droits acquis
restent ceux du scénario 3, et seul le flux postérieur change. À compter de la
bascule il n'y a plus qu'un régime, dont la répartition salarié/employeur est
celle du statut pivot privé : les écarts entre statuts s'y referment.</p>
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

#: Couleur de chacun des cinq scénarios — les mêmes que sur la page de
#: résultats, pour qu'un lecteur qui passe de l'une à l'autre les reconnaisse.
COULEURS_SCENARIOS = {
    "actuel": "var(--actuel)",
    "notionnel_retroactif": "var(--retroactif)",
    "notionnel_prospectif": "var(--prospectif)",
    "notionnel_retroactif_employeur": "var(--retroactif-employeur)",
    "notionnel_prospectif_employeur": "var(--prospectif-employeur)",
}


def _milliards(millions: float, decimales: int = 0) -> str:
    """Un montant en millions d'euros, écrit en milliards."""
    return g.nombre(millions / 1000, decimales) + "\u202fMd\u202f\u20ac"


def _cout(contexte: Contexte) -> str:
    depenses = contexte.depenses()
    cout = contexte.cout()
    annees = tuple(depenses.annees())
    ventilees = tuple(depenses.annees_ventilees())
    derniere = depenses.derniere_annee
    euros = cout.annee_euros

    total = depenses.depense(derniere)
    repartition = depenses.repartition(derniere)
    autres = {code: depenses.depense_systeme(code, derniere) for code in
              (s.code for s in SYSTEMES if not s.repartition)}

    # -- ce que la dépense a été, en euros courants et constants ------------
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
    courbe_pib = g.Serie(
        "Part du produit intérieur brut",
        tuple(ligne.part_pib * 100 for ligne in cout.annees),
        "var(--serie-3)",
    )

    # -- ce que chaque système pèse ----------------------------------------
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

    premiere_ventilee = ventilees[0]
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
            f'<span title="{escape(systeme.glose)}">{escape(systeme.libelle)}</span>',
            _milliards(fin, 1),
            g.pourcentage(fin / total, decimales=1),
            _milliards(cumul, 0),
            g.pourcentage(croissance, signe=True, decimales=1),
            "oui" if systeme.repartition else "non",
        ])

    # -- ce que les cinq systèmes auraient coûté ---------------------------
    # Un scénario dont la courbe est exactement celle du système actuel serait
    # tracé PAR-DESSUS elle et la ferait disparaître : le graphique montrerait
    # alors une seule courbe en prétendant en montrer trois. On ne trace donc que
    # les scénarios qui s'en écartent, et la légende nomme les autres.
    confondus = cout.confondus_avec_actuel()
    numeros = [libelle.split(".")[0] for scenario, libelle in SCENARIOS
               if scenario in confondus]
    glose_actuel = (
        f"et les scénarios {' et '.join(numeros)}, qui lui sont confondus"
        if numeros else ""
    )
    courbes_scenarios = tuple(
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
    lignes_scenarios = []
    for scenario, libelle in SCENARIOS:
        cumul = cout.cumul(scenario)
        dernier = cout.annee(derniere)
        lignes_scenarios.append([
            escape(libelle),
            _milliards(cumul, 0),
            g.pourcentage(cumul / reference - 1, signe=True, decimales=1)
            if scenario != "actuel" else "réf.",
            _milliards(dernier.cout(scenario), 1),
            g.pourcentage(dernier.part_pib * dernier.rapports[scenario], decimales=1),
        ])

    # -- demain : la trajectoire de la répartition jusqu'à l'horizon INSEE --
    avenir = cout.avenir
    annees_avenir = tuple(ligne.annee for ligne in avenir.annees)
    bascule = contexte.base.annee_bascule
    courbes_avenir = tuple(
        g.Serie(
            libelle,
            tuple(ligne.cout_constants(scenario) / 1000 for ligne in avenir.annees),
            COULEURS_SCENARIOS[scenario],
            tirets=scenario.startswith("notionnel_prospectif"),
        )
        for scenario, libelle in SCENARIOS
    )
    parts_avenir = tuple(
        g.Serie(
            libelle,
            tuple(ligne.part_pib(scenario) * 100 for ligne in avenir.annees),
            COULEURS_SCENARIOS[scenario],
            tirets=scenario.startswith("notionnel_prospectif"),
        )
        for scenario, libelle in SCENARIOS
    )
    horizon = avenir.annee(avenir.derniere_annee)
    depart = avenir.annee(derniere)
    reference_avenir = avenir.cumul("actuel")
    lignes_avenir = []
    for scenario, libelle in SCENARIOS:
        cumul = avenir.cumul(scenario)
        lignes_avenir.append([
            escape(libelle),
            _milliards(horizon.cout_constants(scenario), 0),
            g.pourcentage(horizon.part_pib(scenario), decimales=1),
            _milliards(cumul, 0),
            "réf." if scenario == "actuel"
            else g.pourcentage(cumul / reference_avenir - 1, signe=True, decimales=1),
            "—" if scenario == "actuel"
            else _milliards(avenir.ecart_cumule(scenario), 0),
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

    decennies = []
    for debut in range(1960, derniere + 1, 10):
        fin = min(debut + 9, derniere)
        lignes_decennie = [l for l in cout.annees if debut <= l.annee <= fin]
        if not lignes_decennie:
            continue
        decennies.append([
            f"{debut}-{fin}",
            _milliards(sum(l.observee_constants for l in lignes_decennie), 0),
            g.pourcentage(
                sum(l.part_pib for l in lignes_decennie) / len(lignes_decennie),
                decimales=1,
            ),
            g.pourcentage(
                sum(l.rapports["notionnel_retroactif"] for l in lignes_decennie)
                / len(lignes_decennie),
                decimales=1,
            ),
            g.pourcentage(
                sum(l.rapports["notionnel_retroactif_employeur"] for l in lignes_decennie)
                / len(lignes_decennie),
                decimales=1,
            ),
        ])

    return f"""
<h2 style="margin-top:0">Ce que la retraite a coûté</h2>
<p class="chapeau">Le reste du site calcule des droits : ce qu'une carrière
ouvre. Cette page porte la grandeur inverse — ce qui a été payé, année par année
depuis {cout.premiere_annee}, système par système. Puis elle pose les deux
questions qui suivent : ce que les quatre autres systèmes auraient coûté sur la
même période, et ce qu'ils coûteraient d'ici {avenir.derniere_annee}. On ne
change pas le passé ; c'est la seconde question qui décide de quelque chose.</p>

<div class="fiches">
{g.fiche(f"Dépense {derniere}, risque vieillesse-survie", _milliards(total, 1))}
{g.fiche(f"Dont répartition obligatoire", _milliards(repartition, 1))}
{g.fiche(f"Part du PIB en {derniere}",
         g.pourcentage(depenses.part_pib(derniere), decimales=1))}
{g.fiche(f"Cumul {cout.premiere_annee}-{derniere}, euros de {euros}",
         _milliards(cout.cumul_observe(), 0))}
</div>

<p>Les {_milliards(total, 1)} de {derniere} sont le risque
<strong>vieillesse-survie tout entier</strong> : les pensions, mais aussi le
minimum vieillesse, l'aide sociale aux personnes âgées et la retraite
supplémentaire par capitalisation. La <strong>répartition obligatoire</strong>
seule en fait {_milliards(repartition, 1)} — c'est cette grandeur-là, et non le
total, qu'il faut rapprocher des quelque 420 milliards que l'on cite d'ordinaire
pour l'année en cours. Le reste est
{_milliards(autres["aide_sociale_locale"], 1)} de dépendance,
{_milliards(autres["supplementaire"], 1)} de capitalisation et
{_milliards(autres["solidarite_etat"], 1)} de solidarité de l'État.</p>

<h3>Soixante-six ans de dépense</h3>
{g.graphique(
    f"Dépenses du risque vieillesse-survie de {cout.premiere_annee} à {derniere}, "
    f"en milliards d'euros",
    annees, (courbe_constants, courbe_courants), unite="Md €")}
<p class="discret">Deux lectures de la même série. En euros courants, la
dépense est multipliée par cent quatre-vingt-treize depuis
{cout.premiere_annee} — mais les prix aussi ont été multipliés par treize.
En euros constants, la multiplication est par quinze : c'est celle-là qui est
réelle, et elle reste considérable.</p>

{g.graphique(
    f"Part des dépenses de vieillesse-survie dans le produit intérieur brut, "
    f"{cout.premiere_annee}-{derniere}",
    annees, (courbe_pib,), unite="% du PIB", decimales=1)}
<p class="discret">Rapportée à la richesse produite, la dépense passe de
{g.pourcentage(depenses.part_pib(cout.premiere_annee), decimales=1)} à
{g.pourcentage(depenses.part_pib(derniere), decimales=1)}. La courbe monte par
paliers — chaque crise fait un décrochage du dénominateur avant que le
numérateur ne rattrape — et le palier des années 2020 n'a pas encore été
refermé.</p>

<h3>Système par système</h3>
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
)}
<p class="discret">Le cumul est en euros constants de {euros} : additionner des
euros de 1990 et de {derniere} n'aurait aucun sens. La croissance réelle est
celle de la dépense annuelle, déflatée, de {premiere_ventilee} à {derniere}.
Deux chiffres se lisent en connaissant le découpage : le régime général absorbe
en 2020 les artisans et les commerçants, dont le régime a été adossé à la Cnav,
et les « régimes spéciaux » de la comptabilité nationale contiennent la CNRACL,
c'est-à-dire la fonction publique territoriale et hospitalière.</p>

<h3>Ce que les cinq systèmes auraient coûté</h3>
<p>La dépense observée n'est pas modélisée : elle est ce qu'elle est. Ce qui est
modélisé, c'est le <strong>rapport</strong> entre ce qui a été versé et ce que
chaque système aurait versé aux mêmes retraités — la moyenne des écarts de
pension, pondérée par le poids de chaque génération dans la masse de l'année.
Les poids sont les effectifs réels de chaque génération, lus dans la pyramide
des âges de l'INSEE ; les écarts viennent des douze cas types croisés avec
{len(cout.generations)} générations, de {cout.generations[0]} à
{cout.generations[-1]}.</p>

{g.graphique(
    f"Coût annuel des cinq systèmes, {cout.premiere_annee}-{derniere}, "
    f"en milliards d'euros constants de {euros}",
    annees, courbes_scenarios, unite=f"Md € {euros}")}

{g.tableau(
    ["Système", f"Cumul {cout.premiere_annee}-{derniere}", "Écart",
     f"Coût {derniere}", f"Part du PIB {derniere}"],
    lignes_scenarios,
    ["", "nombre", "nombre", "nombre", "nombre"],
)}

<div class="note"><strong>Les scénarios 3 et 5 coûtent exactement ce que coûte
le système actuel, et ce n'est pas un défaut du calcul.</strong> Leur bascule est
fixée à {contexte.base.annee_bascule} : aucune pension servie avant cette date
n'en est modifiée, puisque les droits déjà acquis sont conservés. Une réforme
prospective ne fait rien économiser sur le passé — elle ne commence à compter
qu'au premier assuré qui liquide après elle. C'est le principal résultat de
cette page, et il est vrai de toute réforme des retraites qui respecte les
droits acquis.</div>

<p>Le scénario 2, lui, aurait coûté {_milliards(cout.cumul("notionnel_retroactif"), 0)}
au lieu de {_milliards(reference, 0)} : la retraite française aurait servi
{g.pourcentage(1 - cout.cumul("notionnel_retroactif") / reference, decimales=0)}
de moins sur soixante-six ans. Cet écart ne mesure PAS l'effet des comptes
notionnels. Il mesure deux choses qui n'ont rien à voir avec eux : ce scénario
ne porte au compte que la <strong>part salariale</strong> de la cotisation — le
scénario 4, qui y ajoute la part patronale, coûte
{_milliards(cout.cumul("notionnel_retroactif_employeur"), 0)}, soit
{g.pourcentage(
    cout.cumul("notionnel_retroactif_employeur")
    / cout.cumul("notionnel_retroactif") - 1, signe=True, decimales=0)}
de plus —, et il applique une <a href="{g.lien("/methode", "indexation")}">règle
d'indexation</a> dont la page Méthode montre qu'elle domine tout le reste.</p>

<h2>Demain : ce que chaque système coûterait d'ici {avenir.derniere_annee}</h2>
<p class="chapeau">On ne change pas le passé. La question qui décide de quelque
chose est celle-ci : à partir d'aujourd'hui, que coûte chaque système ? La
réponse tient à deux choses, et à deux seulement — combien de retraités, et
combien chacun perçoit.</p>

<div class="fiches">
{g.fiche(f"Système actuel en {avenir.derniere_annee}",
         g.pourcentage(horizon.part_pib("actuel"), decimales=1))}
{g.fiche(f"Notionnel dès {bascule} en {avenir.derniere_annee}",
         g.pourcentage(horizon.part_pib("notionnel_prospectif"), decimales=1))}
{g.fiche(f"Écart cumulé {avenir.premiere_annee_projetee}-{avenir.derniere_annee}",
         _milliards(avenir.ecart_cumule("notionnel_prospectif"), 0))}
{g.fiche(f"65 ans et plus par 20-64 ans, en {avenir.derniere_annee}",
         g.nombre(horizon.dependance, 2))}
</div>

<p>La méthode ne change pas d'un mot : le coût d'un système reste la dépense du
système actuel multipliée par le rapport des masses de pension. Ce qui change,
c'est d'où vient cette dépense. Jusqu'en {derniere} elle est <strong>observée</strong> ;
au-delà, c'est le modèle qui la produit, <strong>ancré</strong> sur cette
dernière année publiée — les deux expressions coïncident exactement à la
jonction, si bien qu'aucune courbe ne saute. Ce qui les fait bouger ensuite est
ce qui doit les faire bouger : la <strong>pyramide des âges</strong> de l'INSEE,
et les pensions que chaque génération acquiert sous chaque système.</p>

<div class="note">L'assiette de cette section n'est pas celle de la précédente.
Le modèle décrit des <strong>pensions de répartition obligatoire</strong> —
{_milliards(repartition, 1)} en {derniere} — et non le risque vieillesse-survie
entier, qui porte en plus la dépendance et la capitalisation. C'est donc de la
répartition seule qu'il s'agit ici, de {avenir.premiere_annee} à
{avenir.derniere_annee}.</div>

{g.graphique(
    f"Coût annuel des cinq systèmes de {avenir.premiere_annee} à "
    f"{avenir.derniere_annee}, en milliards d'euros constants de {euros}",
    annees_avenir, courbes_avenir, unite=f"Md € {euros}",
    repere=derniere, libelle_repere="projection")}
<p class="discret">À gauche du trait, la dépense est publiée par la DREES ; à
droite, elle est projetée. Les cinq courbes se suivent jusqu'à la bascule de
{bascule} — les droits déjà acquis sont conservés — puis les deux scénarios
prospectifs s'en détachent, d'abord imperceptiblement, ensuite pour de bon. Une
réforme des retraites met une génération entière à produire son effet, et c'est
là le vrai enseignement de ce graphique : décider en {bascule} n'économise rien
en {bascule}, et beaucoup en {avenir.derniere_annee}.</p>

{g.graphique(
    f"Part du produit intérieur brut, {avenir.premiere_annee}-"
    f"{avenir.derniere_annee}, par système",
    annees_avenir, parts_avenir, unite="% du PIB", decimales=1,
    repere=derniere, libelle_repere="projection")}
<p class="discret">C'est la lecture qui compte, parce qu'elle rapporte la
dépense à ce qui la finance. Le système actuel passe de
{g.pourcentage(depart.part_pib("actuel"), decimales=1)} en {derniere} à
{g.pourcentage(horizon.part_pib("actuel"), decimales=1)} en
{avenir.derniere_annee} : il ne dérape pas, il ne s'allège pas non plus. Le
Conseil d'orientation des retraites, qui projette la même grandeur avec un
modèle de population complet, trouve 13,9 % en 2024 et
<strong>14,2 % en 2070</strong> (rapport annuel de juin 2025) — trois dixièmes
de point sous notre point de départ, six dixièmes sous notre point d'arrivée.
Deux modèles qui n'ont rien en commun, et qui tombent à un demi-point l'un de
l'autre : c'est le meilleur contrôle externe dont cette page dispose.</p>

{g.tableau(
    ["Système", f"Coût {avenir.derniere_annee}", f"Part du PIB {avenir.derniere_annee}",
     f"Cumul {avenir.premiere_annee_projetee}-{avenir.derniere_annee}", "Écart",
     "Dont économie"],
    lignes_avenir,
    ["", "nombre", "nombre", "nombre", "nombre", "nombre"],
)}
<p class="discret">Le cumul porte sur les seules années projetées, en euros
constants de {euros}. Les scénarios 2 et 4 restent des contrefactuels et non des
réformes : ils supposent recalculées les pensions de gens qui les perçoivent
depuis trente ans, ce qu'aucun droit ne permettrait. Les scénarios 3 et 5, eux,
décrivent une réforme applicable — droits acquis conservés, règles nouvelles
pour la suite.</p>

<h3>Ce qui pousse la dépense, et ce qui la retient</h3>
{g.tableau(
    ["Horizon", "65 ans et plus par 20-64 ans", "Système actuel",
     f"Notionnel dès {bascule}", f"Notionnel dès {bascule}, avec l'employeur"],
    horizons,
    ["", "nombre", "nombre", "nombre", "nombre"],
)}
<p class="discret">La première colonne est le rapport de dépendance
démographique de l'INSEE : {g.nombre(depart.dependance, 2)} personne de 65 ans
ou plus par personne de 20 à 64 ans en {derniere},
{g.nombre(horizon.dependance, 2)} en {avenir.derniere_annee}. C'est lui qui
pousse la dépense, et il n'est l'objet d'aucun choix. Ce qui la retient, dans le
système actuel, est l'indexation sur les prix : elle fait décrocher les pensions
des salaires, génération après génération, et c'est ainsi que la dépense reste à
peu près stable dans le PIB pendant que le nombre de retraités augmente de
moitié. Les comptes notionnels font la même chose autrement — par le diviseur
d'espérance de vie —, mais ils le font <em>explicitement</em>, et à
l'acquisition plutôt qu'au versement.</p>

<h3>Ce que cette projection suppose</h3>
<ul class="serree">
  <li><strong>La démographie n'est pas de nous.</strong> Effectifs par âge du
  scénario central des projections de population 2026 de l'INSEE, jusqu'en
  {avenir.derniere_annee} — c'est cet horizon-là, et non une décision du dépôt,
  qui borne la page. Seize autres scénarios existent ; leur écart mesurerait
  l'incertitude démographique, que cette page ne montre pas.</li>
  <li><strong>Le PIB projeté corrige l'emploi.</strong> Il croît au rythme
  nominal des hypothèses du COR — {g.pourcentage(
      contexte.simulateur().macro.projection["pib_nominal"], decimales=2)} par an —,
  corrigé de l'évolution de la population d'âge actif, qui recule de
  {g.pourcentage(
      1 - contexte.population().actifs(avenir.derniere_annee)
      / contexte.population().actifs(derniere), decimales=0)} d'ici
  {avenir.derniere_annee}. Sans cette correction, la France de
  {avenir.derniere_annee} produirait avec des actifs qu'aucune projection ne lui
  donne, et toutes les parts de PIB de cette page seraient flatteuses d'un point.</li>
  <li><strong>La grille échantillonne une génération sur cinq.</strong> Chacune
  en représente cinq, décalées d'un an à deux ans, et chacune de ces cinq
  liquide sa propre année. Une cohorte qui part juste avant la bascule est donc
  représentée par une génération qui part juste après, et hérite de son
  traitement : les courbes prospectives s'écartent de la courbe actuelle d'un
  ou deux dixièmes de pour cent avant même la bascule. C'est le prix du pas de
  la grille, il est mesuré, et un test le borne à un demi-point.</li>
  <li><strong>Le taux de couverture est supposé constant.</strong> Le modèle
  compte des générations, non des cotisants : il suppose que la même proportion
  de chaque génération perçoit une pension, et que la carrière type ne change
  pas. Un recul de l'âge de départ, une carrière plus longue ou plus hachée
  déplaceraient la trajectoire, et la page ne les simule pas.</li>
  <li><strong>Aucune règle de pilotage.</strong> Un système notionnel réel porte
  un coefficient d'équilibre qui ajusterait toutes ses pensions par un même
  facteur, année après année, pour tomber juste. Ce facteur étant commun, il
  déplacerait les niveaux sans toucher aux écarts entre carrières — mais il
  déplacerait bel et bien les courbes de cette page.</li>
  <li><strong>Rien de tout cela n'est certifié, et ne peut l'être.</strong> Une
  projection est une hypothèse : celle de l'INSEE pour la démographie, celle du
  COR pour la macroéconomie, celle du modèle pour les pensions. La page les
  affiche parce qu'un ordre de grandeur documenté vaut mieux qu'un silence — pas
  parce qu'elle saurait de quoi 2070 sera fait.</li>
</ul>

<h3>Décennie par décennie</h3>
{g.tableau(
    ["Décennie", f"Dépense cumulée, euros de {euros}", "Part du PIB",
     "Coût du scénario 2", "Coût du scénario 4"],
    decennies,
    ["", "nombre", "nombre", "nombre", "nombre"],
)}
<p class="discret">Les deux dernières colonnes sont en pourcentage de la dépense
réellement engagée la même décennie. Elles remontent : plus on approche du
présent, plus les carrières prises en compte ont été cotisées sous des règles
proches des règles actuelles, et moins le compte notionnel s'en écarte.</p>

<h3>Ce que cette page ne dit pas</h3>
<ul class="serree">
  <li><strong>Elle ne projette rien.</strong> La série s'arrête à {derniere},
  dernière année publiée par la DREES. Prolonger demanderait une pyramide des
  âges et un taux d'emploi, c'est-à-dire un modèle de population — que ce dépôt
  n'a pas et ne prétend pas avoir.</li>
  <li><strong>Les effectifs de génération sont ceux de l'INSEE</strong>, non
  une hypothèse. Cette page a d'abord supposé toutes les générations de même
  taille, faute de pyramide des âges ; elle porte désormais celle des
  projections de population 2026, observée jusqu'en 2023. L'hypothèse levée
  valait ce qu'on disait qu'elle valait : elle déplaçait l'écart du scénario 2
  de six dixièmes de point sur soixante-six ans.</li>
  <li><strong>Les douze cas types pèsent d'un poids égal.</strong> Il y a moins
  d'agents de conduite que de salariés au salaire moyen. C'est la convention de
  la grille des <a href="{g.lien("/cas-types")}">cas types</a>, reconduite ici
  faute d'une pondération que quelque source fixerait.</li>
  <li><strong>Avant 1975, la reconstitution est mince.</strong> La répartition
  ne commence qu'en {contexte.base.annee_debut_repartition} : les générations
  antérieures à {cout.generations[0]} n'ont, dans ce modèle, aucune pension, et
  plusieurs régimes n'existaient pas encore. Les premières années reposent donc
  sur deux ou trois générations et la moitié des cas types.</li>
  <li><strong>Le coût n'est pas le solde.</strong> Cette page dit ce qui a été
  versé, jamais ce qui a été encaissé. Un système notionnel qui coûterait quatre
  fois moins ne serait pas quatre fois plus « soutenable » : il servirait
  quatre fois moins, ce qui est une autre affaire.</li>
</ul>
<p class="discret">Fiabilité de l'ensemble : la dépense observée est
<strong>certifiée</strong> — recontrôlée contre l'API de la DREES à chaque
exécution —, le rapport qui en tire les quatre contrefactuels est
<strong>estimé</strong>, et ne peut pas être autre chose : aucune institution ne
publie ce qu'aurait coûté un système qui n'a pas existé.</p>
"""


def _methode(contexte: Contexte) -> str:
    fusionne = contexte.simulateur().regime_fusionne
    nombre_regimes = len(contexte.simulateur().catalogue)
    return f"""
<h2 style="margin-top:0">Ce que le modèle calcule</h2>

<h3>Le compte notionnel</h3>
<p>Un compte notionnel est un compte <em>virtuel</em> : aucun capital n'est
placé, les cotisations de l'année financent les pensions de l'année, comme dans
toute répartition. Ce qui change, c'est le calcul du droit.</p>
<ol>
  <li><strong>Accumulation</strong> — la cotisation retraite effectivement
  versée chaque année est inscrite au compte ;</li>
  <li><strong>Revalorisation</strong> — le solde est revalorisé chaque année au
  taux fixé par la règle collective ;</li>
  <li><strong>Liquidation</strong> — pension annuelle = capital notionnel ÷
  espérance de vie résiduelle à l'âge de départ, lue sur une table de
  génération.</li>
</ol>
<p>Trois conséquences : la pension est strictement proportionnelle aux
cotisations ; partir tôt coûte deux fois (moins de cotisations, rente servie
plus longtemps) ; aucun droit non financé par une cotisation n'existe.</p>

<h3 id="indexation">La règle d'indexation, et pourquoi elle domine tout</h3>
<p>La règle retenue par défaut est la croissance de la <strong>masse
salariale</strong> : l'assiette des cotisations, c'est-à-dire le rendement qu'un
système en répartition peut servir sans toucher à son taux de cotisation. C'est
la règle que la théorie désigne, et non celle qui a donné son cahier des charges
au modèle.</p>
<p>Celle-là, le <strong>triple lock inversé</strong> —
<code>min(inflation, croissance du salaire moyen, productivité réelle)</code> —
reste à un clic dans les options, et c'est elle qui a motivé ce simulateur.
Prise à la lettre, elle compare deux taux nominaux à un taux réel, et voici ce
qu'elle produit.</p>
{g.tableau(
    ["Règle appliquée 1941-2025", "Comptes", "Prix", "Pouvoir d'achat conservé"],
    [
        ["Triple lock inversé, littéral", "×4,9", "×322,2", "<strong>1,5 %</strong>"],
        ["Moyenne des trois taux", "×175,7", "×322,2", "54,5 %"],
        ["Triple lock inversé, tout en nominal", "×223,3", "×322,2", "69,3 %"],
        ["Indexation sur les prix", "×322,2", "×322,2", "100 %"],
        ["Médiane des trois taux", "×397,6", "×322,2", "123,4 %"],
        ["Revalorisation réellement pratiquée", "×1 538,2", "×322,2", "477,4 %"],
        ["Masse salariale (règle d'équilibre)", "×3 685,1", "×322,2", "1 143,7 %"],
        ["PIB nominal", "×3 442,3", "×322,2", "1 068,6 %"],
        ["PIB nominal lissé sur 5 ans (Italie)", "×4 152,7", "×322,2", "1 288,8 %"],
    ],
    ["", "nombre", "nombre", "nombre"],
)}
<p>Une cotisation de 1950 ne conserve donc que 1,5 % de sa valeur réelle. C'est
la règle telle qu'énoncée, appliquée sans correctif — et c'est de là que vient
l'essentiel de la baisse affichée par le scénario rétroactif, non du passage aux
comptes notionnels. Le tableau « D'où vient l'écart » de chaque simulation
sépare les deux effets.</p>
<p>La ligne « Revalorisation réellement pratiquée » est la seule qui ne soit pas
une hypothèse : c'est le coefficient que les arrêtés annuels ont réellement
appliqué aux salaires portés au compte, celui dont le scénario 1 se sert pour
calculer le salaire de référence. Il vaut <strong>×1 538</strong> sur la période, soit près de cinq
fois les prix, parce que le régime général a revalorisé sur les SALAIRES
jusqu'en 1986 et sur les prix seulement depuis 1987. C'est donc cette ligne, et
non « Indexation sur les prix », qui neutralise la question de l'indexation
quand on veut isoler l'effet propre des comptes notionnels — cette page a
longtemps désigné la mauvaise. Sur une carrière, la correction reste modeste :
+6,2 points pour la génération 1920, +0,1 pour 1945, et -0,5 pour 1958, dont la
carrière est presque entièrement postérieure à 1987. Les cotisations se
concentrent sur les dernières années, là où les deux règles coïncident.</p>
<p>La dernière ligne est d'une autre nature : elle ne décrit ni une règle
demandée, ni une règle appliquée, mais la règle que la <strong>théorie</strong>
désigne. En répartition, le rendement qu'un système peut servir sans changer son
taux de cotisation est la croissance de son assiette — la masse salariale, soit
le salaire moyen multiplié par l'emploi salarié (Samuelson 1958, Aaron 1966).
C'est le taux d'indexation des comptes notionnels suédois, italiens, polonais et
lettons, à des variantes près. Sur 1941-2025 il vaut ×3 685, onze fois les
prix : l'emploi salarié a doublé depuis 1950, et cette croissance-là s'ajoute
chaque année à celle des salaires. Une réserve : ce rendement est celui du
système ENTIER, alors que les scénarios 2 et 3 ne portent au compte que la part
salariale de la cotisation. C'est aux scénarios 4 et 5 qu'il faut le comparer.</p>
<p>Les deux dernières lignes sont la même idée poussée à l'assiette la plus
large : le <strong>PIB nominal</strong>, qui gagne ce que la masse salariale
perd quand la valeur ajoutée se déplace vers les revenus non salariaux. La
seconde y ajoute un <strong>lissage sur cinq ans</strong>, comme le fait
l'Italie pour ses propres comptes notionnels.</p>
<p>Le lissage n'est pas une règle : c'est un réglage à part, qui applique une
moyenne glissante au taux que la règle produit — n'importe laquelle. Ce qu'il
vise n'est pas le niveau mais la <strong>loterie de cohorte</strong> : sur le PIB
nominal brut, une cotisation de 1980 vaut ×5,44 à une liquidation de 2019 et
×5,18 en 2020 — attendre un an fait <em>perdre</em>, parce que l'année traversée
s'est mal passée. Lissée sur cinq ans, elle vaut ×6,64 puis ×6,71 : le trou de
2020 est absorbé par les quatre années qui l'entourent au lieu d'être porté en
entier par qui a eu le tort de liquider cette année-là. Sur 1950-2025, le PIB
nominal brut compte deux années où liquider plus tard rapporte moins ; lissé sur
trois ou cinq ans, aucune.</p>
<p>Une réserve pour lire le tableau : sur quatre-vingts ans, une moyenne
glissante n'est pas neutre. Elle revient à mesurer la croissance depuis une base
reculée d'environ la moitié de la fenêtre, ce qui gonfle le cumul d'une
vingtaine de pour cent à cinq ans — sans qu'aucune série ait changé. Sur une
carrière, l'écart entre lissé et non lissé reste d'un à deux points. Et la règle
italienne n'est reprise ici que par son taux, pas par le reste du système
italien (décalage de publication de deux ans, coefficients de transformation,
planchers).</p>
<p>Le minimum n'est pas la seule statistique possible sur ces trois séries. Deux
variantes gardent les <em>mêmes</em> termes et ne changent que ce qu'on en
retient : la <strong>médiane</strong> — le taux du milieu — et la
<strong>moyenne</strong>. Le résultat n'est pas celui qu'on attend. La médiane
est l'inflation ou le salaire moyen trois années sur quatre, donc un taux
nominal : elle suit les prix et les dépasse même un peu, et cesse d'être une
règle d'austérité. La moyenne, elle, est plus sévère que les prix, non par
sévérité assumée mais parce qu'elle incorpore un tiers de productivité réelle
<em>chaque</em> année, y compris à vingt points d'inflation — là où le minimum
et la médiane ne retiennent le terme réel que les années où il gagne. Les deux
sont sélectionnables dans les options de modélisation.</p>

<h3>Ce que le scénario 1 applique du droit positif</h3>
<p>L'étalon ne vaut que par ce qu'il reproduit. Il applique la décote et la
surcote, la proratisation par la durée, le salaire de référence de chaque
régime — sur ses seules années, jamais sur toute la carrière —, et cinq
paramètres lus à la GÉNÉRATION et non à l'année de liquidation : durée requise,
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
  attribués DANS un régime et non au-dessus d'eux : ils comptent donc aussi dans
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
demandée — âge légal du régime, ou départ anticipé pour carrière longue. Quand
il ne l'ouvre pas, le montant reste calculé, parce qu'il faut comparer les cinq
scénarios sur la même carrière, mais la page le signale : il ne décrit alors
aucune pension que le système actuel servirait.</p>

<h3>Ce qui est supprimé dans les scénarios notionnels</h3>
<p>Le principe « seules les cotisations comptent » est appliqué sans exception :
ni minimum contributif, ni minimum garanti, ni ASPA, ni majoration pour enfants,
ni majoration de durée d'assurance, ni AVPF, ni bonifications, ni catégorie
active, ni périodes assimilées, ni réversion, ni décote ni surcote. Le scénario
1 les conserve tous, puisqu'il décrit le droit en vigueur.</p>

<h3>La fusion des régimes</h3>
<p>À compter de l'année de bascule, les {nombre_regimes} régimes du catalogue sont remplacés
par un régime unique dont chaque paramètre est le plus défavorable de
l'ensemble : ouverture à {_age(fusionne.age_ouverture)}, taux plein à
{_age(fusionne.age_taux_plein)}, {fusionne.duree_requise_trimestres} trimestres
requis, cotisation de {g.pourcentage(fusionne.taux_cotisation_retraite, decimales=2)}
sur assiette déplafonnée.</p>

<h3>Une carrière, plusieurs métiers</h3>
<p>Une carrière se décrit comme une <strong>suite de métiers</strong> : chacun
porte un statut d'affiliation, un âge de début et un niveau de revenu, et court
jusqu'au début du suivant. On faisait autrefois le même métier toute sa vie ;
c'est devenu l'exception, et chaque changement fait passer d'un régime à un
autre — donc d'un taux de cotisation, d'une assiette et d'un barème à un autre.
C'est précisément ce que les cinq scénarios mesurent.</p>
<p>Deux conventions le bornent, imposées l'une et l'autre par la maille des
données. Le <strong>profil de carrière</strong> vaut pour la vie active entière,
changements compris : c'est une progression de carrière et non d'emploi, et le
niveau propre à chaque métier s'y superpose au lieu de la remettre à zéro. Et
une <strong>année civile n'a qu'un statut</strong> — un salaire est déclaré à
l'année, les régimes liquident à l'année : l'année d'un changement revient au
métier qui en occupe le plus de mois, et à égalité à celui qui l'ouvre, tandis
que le revenu porté au compte reste la somme de ce que les deux ont
réellement payé.</p>

<h3 id="unites">Brut, et pas net</h3>
<p>Tout ce que le modèle manipule est <strong>brut</strong> : le salaire saisi,
les cotisations versées, le capital notionnel, les cinq pensions. « Brut » a ici
le sens des comptes nationaux — <em>salaires et traitements bruts</em> (D11)
rapportés à l'emploi salarié intérieur, ce qui est la définition même du salaire
moyen par tête qui sert d'unité au modèle. C'est-à-dire <strong>avant</strong>
cotisations salariales, CSG, CRDS et impôt sur le revenu, et <strong>hors</strong>
cotisations patronales, qui s'ajoutent au brut sans en faire partie. Ce n'est pas
une commodité : c'est l'assiette sur laquelle les régimes appellent leurs
cotisations, donc la seule grandeur qu'un compte notionnel puisse enregistrer.
Le taux de remplacement affiché rapporte donc un brut à un brut, et il est
mécaniquement plus bas qu'un taux calculé sur des nets — les pensions sont moins
prélevées que les salaires.</p>
<p>Le salaire se saisit en <strong>euros d'aujourd'hui</strong> : ce que le
métier paie maintenant. Le modèle, lui, ne connaît que le
<strong>multiple du salaire moyen</strong>, seule unité qui garde son sens sur
quatre-vingts ans — un montant n'en a que rapporté à son année. La page fait
donc une division, et une seule : <code>niveau = salaire mensuel × 12 ÷ salaire
moyen annuel</code>. Ce niveau, ensuite, suit le salaire moyen d'une année à
l'autre, déformé par le profil de carrière.</p>
<p>Reste que les comptes nationaux ne publient que des <em>taux de croissance</em>
du salaire moyen. Les niveaux en sont reconstitués à partir d'un point
d'ancrage — <strong>40 000 € bruts annuels en 2024</strong> —, paramètre
documenté et non donnée certifiée. Il déplace proportionnellement tous les
revenus reconstitués, donc toutes les pensions, mais il est sans effet sur les
<strong>rapports</strong> entre scénarios, qui sont l'objet du modèle. Il
commande en revanche la traduction d'un salaire en multiple : saisir un montant
en euros, c'est le lire à cette échelle-là.</p>

<h3>Périmètre</h3>
<p>Origine 1941 (allocation aux vieux travailleurs salariés), premier dispositif
où les cotisations des actifs financent les prestations des retraités. Les
assurances sociales de 1930, en capitalisation individuelle, et le RAFP sont
isolés dans un compartiment séparé, jamais converti.</p>

<p><a href="{g.DEPOT}/blob/main/docs/methodologie.md">Méthodologie complète</a> ·
<a href="{g.DEPOT}/blob/main/docs/limites.md">Limites connues</a></p>
"""


def _donnees(contexte: Contexte) -> str:
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
    certifications = [
        [escape(nom), f"{trace['valeurs']}", escape(trace.get("niveau", "certifiee")),
         escape(trace["source"])]
        for nom, trace in sorted(journal.get("series", {}).items())
    ]
    if certifications:
        bandeau = f"""<div class="note"><strong>Les séries macroéconomiques sont
certifiées de 1950 à 2025</strong>, les tables de mortalité sont celles
réellement observées depuis 1986, et le plafond de la Sécurité sociale remonte à
1931 daté décret par décret — le tout recontrôlé automatiquement contre les
sources, le {escape(journal['certifie_le'])}. Ce qui précède 1950 et les
paramètres propres à chaque régime restent saisis à la main : les
<em>niveaux</em> de pension des carrières les plus anciennes gardent une marge,
les <em>écarts entre scénarios</em>, qui sont l'objet du modèle, sont plus
robustes encore.</div>"""
    else:
        bandeau = """<div class="note avertissement"><strong>Aucune série n'a
encore été recontrôlée contre sa source.</strong> Lancer <code>scripts/fetch/</code>
puis <code>scripts/verifier_donnees.py --appliquer</code>.</div>"""

    return f"""
<h2 style="margin-top:0">Ce que valent les chiffres</h2>
{bandeau}

<h3>Ce qui a été recontrôlé contre la source</h3>
{g.tableau(["Série", "Valeurs", "Niveau", "Source"], certifications,
           ["", "nombre", "", ""])}
<p class="discret">Une valeur n'est « certifiée » que si elle a été confrontée au
fichier téléchargé depuis le <em>producteur</em> de la donnée. Une transcription
tierce, même sourcée et reprise automatiquement, plafonne à « haute ». Hors de
cette liste : les séries d'avant 1950, les taux de cotisation d'avant 1967, le
plafond d'avant 2002 et le point d'indice de la fonction publique, repris
d'OpenFisca, les montants servis du minimum contributif, du minimum garanti et
du minimum vieillesse — transcrits de leur publication, et préférés à toute
projection parce qu'ils disent ce qui a été payé —, et les âges, durées et
coefficients propres à chaque régime, repris des textes.</p>

<h3>Fiabilité des séries macroéconomiques, par décennie</h3>
{g.tableau(
    ["Période", "Inflation", "Salaire moyen", "Productivité", "Ensemble"],
    periodes,
    ["", "", "", "", ""],
)}
<p class="discret">Une projection ne se fait jamais passer pour une observation :
au-delà de la dernière année observée, la fiabilité retombe à « estimée ».</p>

<h3>Fiabilité des {len(simulateur.catalogue)} régimes</h3>
{g.tableau(["Niveau", "Nombre", "Régimes"], regimes, ["", "nombre", ""])}

<h3>Sources</h3>
<p>Vingt-six institutions sont recensées dans
<a href="{g.DEPOT}/blob/main/data/sources.yaml">data/sources.yaml</a> : INSEE,
COR, Comité de suivi des retraites, DREES, CNAV, Service des retraites de l'État,
Caisse des dépôts, Direction de la Sécurité sociale, Cour des comptes,
Agirc-Arrco, Assemblée nationale, Union Retraite, CCMSA, CNAVPL, CNBF, DGAFP,
Direction du Budget, ERAFP, Ircantec, caisses des régimes spéciaux, Urssaf,
Légifrance, INED, Eurostat, OCDE, OpenFisca-France.</p>
<p>Chaque valeur porte son niveau de fiabilité — <code>certifiee</code>,
<code>haute</code>, <code>moyenne</code>, <code>estimee</code> — et la fiabilité
d'un résultat est celle de son maillon le plus faible.</p>
<p>Quand deux institutions publient le même chiffre, quatre critères disent
laquelle aller chercher : le <strong>producteur</strong> prime sur le repreneur,
l'<strong>observé</strong> sur le projeté, le <strong>montant servi</strong> sur
le montant calculé, le <strong>recontrôlable</strong> sur le saisi. Ce n'est pas
un classement d'institutions mais de natures de données : l'INSEE pour ce qu'il
mesure, le COR pour ce qu'il décide.</p>
<p><a href="{g.DEPOT}/blob/main/docs/limites.md">Limites détaillées</a></p>
"""
