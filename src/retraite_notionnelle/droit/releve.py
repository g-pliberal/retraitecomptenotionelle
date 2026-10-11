"""Le relevé des droits (docs/architecture.md, § 7.2 et 7.6).

Pour une demande, les quatre étapes de l'acquisition construisent le relevé
des droits qu'elle fait valoir : :func:`construire` les enchaîne — la
chronologie arrive préparée, puisque la carrière qui en est la vue ne se
construit qu'après (:mod:`.preparer`) —, puis réunit en groupes les régimes où
un droit est acquis. La liquidation du scénario 1 lit ce qu'il rend.

Le relevé se publie en lignes, que le contrat C.5 décrit
(``data/reference/contrats/ligne_releve.yaml``) : :meth:`Releve.lignes`.
Chaque ligne dit la personne qui en bénéficie, le fait de la chronologie qui
l'ouvre et sa date, le droit — une quantité, son unité, son régime et, pour
une durée, son compte —, sa face, et les présomptions qu'elle emploie. Les
lignes sont les crédits, année par année : le plafond d'une année — ses
trimestres civils, toutes activités d'un régime ou d'un groupe réunies — et
celui de la durée qu'un régime rémunère s'appliquent quand on les lit. Une
ligne cite la fiche de la carte qui l'écrit quand la règle en a une, et, si
la fiche est découpée en versions, la version appliquée et le texte qui la
fait naître : les trimestres des enfants, depuis le 27 septembre 2026. Les
autres attendent que leurs fiches le soient : ce sont des manques, que le
tableau de bord compte.

Lu à rebours, il dit aussi le revenu que des points supposent
(:func:`revenu_des_points`) : celui qu'une année d'un statut doit porter pour
que les régimes d'un étage en créditent autant. La lecture d'un relevé de
carrière s'en sert pour les années qu'il ne chiffre qu'en points (action 138,
étape 11).

Son jumeau est ``moteur/js/droit/releve.js``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .. import chronologie as chrono
from ..somme import somme_ordonnee
from . import acquerir as _acquerir
from . import compter as _compter
from . import coordonner as _coordonner
from . import ouvrir as _ouvrir
from .commun import date_d_effet as _date_d_effet
from .commun import ligne_cotisee as _ligne_cotisee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ScenarioActuel
    from .acquerir import Droits
    from .compter import Durees
    from .coordonner import Coordination

#: La version du contrat C.5 que les lignes et l'enveloppe suivent.
SCHEMA_VERSION = 1

#: Les fiches de la carte que certaines lignes appliquent (data/reference/regles/).
FICHE_RETABLISSEMENT = "retablissement_fonction_publique"
FICHE_SERVICES = "services_et_duree_fonction_publique"
FICHE_POINTS_GRATUITS = "rco_points_gratuits"

#: Les présomptions que chaque dispositif pour enfants applique dans le code
#: (data/reference/vocabulaire/valeurs.yaml, liste `presomptions`).
PRESOMPTIONS_ENFANTS = {
    "mda": ("pas_d_accord_des_parents", "enfant_eleve_neuf_ans"),
    "bonifications": ("interruption_d_activite_par_la_mere",),
    "enfants_sncf": (),
    "enfants_ratp": ("interruption_d_activite_par_la_mere",),
    "enfants_ieg": ("interruption_d_activite_par_la_mere",),
    "enfants_crpcen": ("interruption_d_activite_par_la_mere",),
}


@dataclass(frozen=True, eq=False)
class Releve:
    """Le relevé des droits d'une demande : ce que chaque étape a écrit, et
    les régimes que la coordination fait liquider ensemble."""

    coordination: Coordination
    durees: Durees
    droits: Droits
    #: Pour chaque régime d'un groupe d'au moins deux, les membres du groupe,
    #: le premier étant celui qui liquide.
    groupes: dict[str, tuple[str, ...]]
    #: Les régimes dont la liquidation lit les services : ceux de la fonction
    #: publique. Le compte des services se tient pour toute année d'emploi,
    #: mais seules leurs lignes se publient.
    services_lus: frozenset[str] = frozenset()
    #: Les années d'emploi que leur régime valide sans cotisation, régime par
    #: régime : l'activité cultuelle d'avant 1979 (:func:`~.commun.ligne_cotisee`).
    #: Leurs lignes ne sont pas contributives.
    gratuites: frozenset[tuple[str, int]] = frozenset()

    @property
    def carriere(self) -> Carriere:
        """La carrière que la liquidation lit, rétablissement fait."""
        return self.coordination.carriere

    def donnees(self) -> dict:
        """Le relevé, tel que l'enveloppe du contrat C.5 le décrit."""
        carriere = self.carriere
        groupes = list(dict.fromkeys(self.groupes.values()))
        return {
            "schema_version": SCHEMA_VERSION,
            "personne": carriere.personne,
            "date": _date_d_effet(carriere),
            "lignes": self.lignes(),
            "groupes": [{"regimes": list(membres)} for membres in groupes],
        }

    def lignes(self) -> list[dict]:
        """Les lignes du relevé (contrat C.5), dans l'ordre des étapes : les
        durées, compte par compte ; les trimestres des enfants ; les points ;
        les cotisations ; les points gratuits."""
        carriere = self.carriere
        faits = _Faits(carriere)
        lignes: list[dict] = []
        cotisees: set[tuple[str, int]] = set()
        retablies: set[tuple[str, int]] = set()
        for ligne, regimes in zip(carriere.lignes, self.coordination.regimes):
            for code in regimes:
                if ligne.cotise and (code, ligne.annee) not in self.gratuites:
                    cotisees.add((code, ligne.annee))
                if ligne.revenu_retabli > 0:
                    retablies.add((code, ligne.annee))
        for compte in _compter.COMPTES:
            for code, annees in self.durees.par_annee[compte].items():
                if compte == "services" and code not in self.services_lus:
                    continue
                for annee, trimestres in annees.items():
                    fait = faits.de_l_annee(annee, code, self.coordination)
                    fiche = (FICHE_SERVICES if compte == "services"
                             else FICHE_RETABLISSEMENT if (code, annee) in retablies
                             else None)
                    lignes.append(_ligne(
                        f"{compte}_{code}_{annee}", carriere.personne, fait,
                        f"{annee:04d}-01-01",
                        {"quantite": trimestres, "unite": "trimestre", "regime": code,
                         "compte": compte},
                        fiche=fiche,
                        contributive=(code, annee) in cotisees,
                        origine="observee" if faits.observe(fait) else "calculee",
                        presomptions=faits.presomptions(fait),
                        fiabilite=faits.fiabilite(fait)))
        enfants = self.durees.enfants
        for ouvre in enfants.enfants if enfants is not None else ():
            naissance = faits.naissance(ouvre.enfant)
            rang = ouvre.enfant.rpartition("_")[2]
            presomptions = sorted(
                ([naissance["presomption"]] if naissance and naissance.get("presomption")
                 else [])
                + list(PRESOMPTIONS_ENFANTS.get(ouvre.dispositif, ())))
            for compte, trimestres in (("assurance", ouvre.trimestres),
                                       ("services", ouvre.services)):
                if trimestres <= 0 or (compte == "services"
                                       and ouvre.regime not in self.services_lus):
                    continue
                lignes.append(_ligne(
                    f"enfants_{compte}_{ouvre.regime}_{rang}", carriere.personne,
                    naissance["id"] if naissance else None,
                    naissance["debut"] if naissance else None,
                    {"quantite": trimestres, "unite": "trimestre",
                     "regime": ouvre.regime, "compte": compte},
                    fiche=ouvre.fiche, version=ouvre.version, texte=ouvre.texte,
                    contributive=False, presomptions=presomptions,
                    fiabilite=ouvre.fiabilite.name.lower()))
        droits = self.droits
        vus: dict[str, int] = {}
        for code, annee, points, _ in droits.points:
            cle = f"points_{code}_{annee}"
            vus[cle] = vus.get(cle, 0) + 1
            lignes.append(_ligne(
                cle if vus[cle] == 1 else f"{cle}_{vus[cle]}", carriere.personne,
                faits.de_l_annee(annee, code, self.coordination), f"{annee:04d}-01-01",
                {"quantite": points, "unite": "point", "regime": code},
                fiabilite=droits.fiabilite_points[code].name.lower()))
        for code, annee, montant in droits.cotisations:
            cle = f"cotisations_{code}_{annee}"
            vus[cle] = vus.get(cle, 0) + 1
            lignes.append(_ligne(
                cle if vus[cle] == 1 else f"{cle}_{vus[cle]}", carriere.personne,
                faits.de_l_annee(annee, code, self.coordination), f"{annee:04d}-01-01",
                {"quantite": montant, "unite": "euro", "regime": code},
                face="cotisation", fiabilite=None))
        date_d_effet = _date_d_effet(carriere)
        for code, (points, _) in droits.gratuits.items():
            lignes.append(_ligne(
                f"gratuits_{code}", carriere.personne, faits.depart(), date_d_effet,
                {"quantite": points, "unite": "point", "regime": code},
                fiche=FICHE_POINTS_GRATUITS, contributive=False,
                fiabilite=droits.fiabilite_points[code].name.lower()))
        return lignes


def construire(moteur: ScenarioActuel, carriere: Carriere, *,
               avantages_non_contributifs: bool = True,
               points_gratuits: bool = True,
               liquider_successions: bool = True) -> Releve:
    """Le relevé des droits que la demande portée par ``carriere`` fait
    valoir : coordonner les affiliations, compter les durées, acquérir les
    droits, puis réunir les régimes que le droit fait liquider ensemble.

    Les trois drapeaux sont ceux de :meth:`ScenarioActuel.calculer`, qui les
    documente : les trimestres des enfants, les points gratuits, et la
    liquidation ensemble des régimes qui se succèdent.

    Le chômage que le relevé lit cesse d'être indemnisé au taux plein
    (:func:`~retraite_notionnelle.droit.ouvrir.indemnisation_bornee`).
    """
    carriere = _ouvrir.indemnisation_bornee(moteur, carriere)
    coordination = _coordonner.coordonner(moteur, carriere)
    durees = _compter.compter(moteur, coordination, avantages_non_contributifs)
    droits = _acquerir.acquerir(moteur, coordination, durees, points_gratuits)
    # Un régime et celui qui lui succède liquident ensemble, sous les règles
    # de la caisse qui aurait le dossier : les autres membres du groupe
    # sont sautés partout où un régime liquide.
    groupes = (
        _coordonner.groupes_de_succession(
            moteur, droits.codes, coordination.carriere.annee_liquidation,
            droits.derniere_annee_par_regime, coordination.carriere,
        ) if liquider_successions else {}
    )
    services_lus = frozenset(
        code for code in durees.par_annee["services"]
        if moteur.catalogue[code].famille == "fonction_publique")
    gratuites = frozenset(
        (code, ligne.annee)
        for ligne, regimes in zip(coordination.carriere.lignes, coordination.regimes)
        if ligne.cotise and not _ligne_cotisee(moteur, coordination.carriere, ligne)
        for code in regimes)
    return Releve(coordination, durees, droits, groupes, services_lus, gratuites)


# --------------------------------------------------------------------------
# Le relevé à rebours : le revenu que des points supposent.
# --------------------------------------------------------------------------
#
# Un relevé de carrière porte, pour les années d'un régime qui compte en points
# — le régime de base des libéraux depuis 2004, la retraite proportionnelle des
# exploitants agricoles —, des points et non un revenu ; et, pour une année que
# la base ne chiffre pas, les points de la seule complémentaire. Lues sans
# montant, ces années valaient zéro au compte notionnel, et leurs points étaient
# « lus, et jetés » (action 138, étape 11). Ils disent pourtant le revenu, à la
# résolution du barème près : c'est lui qui les a ouverts.
#
# `revenu_des_points` le retrouve par le relevé des droits lui-même. Il fait
# cotiser une année, sous le statut que le relevé lui donne, à un assuré
# fictif, et cherche par dichotomie le revenu entier le plus bas dont les
# régimes de cet étage — la base, ou la complémentaire — créditent au moins les
# points lus. Le barème n'est pas recopié : c'est celui que la pension du
# scénario 1 applique, tranches, assiettes minimales, paliers et arrondis
# compris, si bien que la pension recalculée du revenu rendu retrouve les
# points du relevé.
#
# LE PLUS BAS, parce que des points ne disent pas toujours un seul revenu : au
# plafond d'un barème, tout revenu plus haut ouvre les mêmes, et sur un palier
# — les trente points des exploitants, de 800 SMIC horaires à deux fois le
# minimum contributif —, tout revenu de la marche. Le revenu rendu est alors le
# seul que les points prouvent ; `RevenuDesPoints.au_plafond` dit le premier
# cas. Des points qu'aucun revenu ne fait varier — les cent points par
# trimestre des libéraux d'avant 2004, ceux qu'ouvre le plancher d'une assiette
# minimale — ne disent aucun revenu, ni ceux qui dépassent le plus haut que le
# barème ouvre : la fonction ne rend rien, et l'année reste sans montant. Ce
# qu'on lui porte au compte notionnel est un choix du programme, qu'elle ne
# fait pas.
#
# L'UNITÉ est celle d'un relevé d'aujourd'hui : les points de l'Arrco d'avant
# 1999 en points de l'Arrco, ceux de la CARMF d'avant 1991 dans son échelle
# d'après, comme l'acquisition les sert à une liquidation lointaine. Ceux de
# l'Agirc d'avant 2019 restent dans l'unité de l'Agirc, celle d'un relevé de
# leur temps : le relevé d'aujourd'hui les fond dans ceux de l'Agirc-Arrco,
# sans plus nommer l'Agirc, et l'année s'y lit en non-cadre.

#: Les étages dont les points disent un revenu : la base qui compte en points,
#: et la complémentaire. L'additionnel de la fonction publique compte les
#: primes, non la rémunération : ses points n'en diraient qu'une part.
ETAGES_CONVERTIS = ("base", "complementaire")

#: L'assuré fictif qui cotise l'année : quarante ans cette année-là, parti à
#: soixante-sept. Une année au milieu d'une carrière, dont l'acquisition sert
#: les points dans l'unité d'aujourd'hui.
AGE_DANS_L_ANNEE = 40
AGE_DE_DEPART_FICTIF = 67.0

#: La borne haute de la recherche, en plafonds de la Sécurité sociale de
#: l'année : au-delà du plus haut plafond d'assiette — huit à l'Agirc-Arrco et
#: à l'Ircantec —, un barème n'ouvre plus de points.
PLAFONDS_AU_PLUS = 16

#: Ce dont des points lus peuvent dépasser le plus haut que le barème ouvre et
#: s'y lire encore : l'arrondi d'un relevé qui les écrit entiers.
DEMI_POINT = 0.5

#: Le bruit du calcul en virgule flottante, en points.
EPSILON_POINTS = 1e-6


@dataclass(frozen=True)
class RevenuDesPoints:
    """Le revenu que des points supposent."""

    #: Le revenu entier le plus bas, en euros de l'année, dont l'étage crédite
    #: au moins les points lus.
    revenu: int
    #: Les points sont le plus haut que le barème ouvre : tout revenu au-delà
    #: de ``revenu`` aurait ouvert les mêmes, et celui de l'assuré a pu le
    #: dépasser.
    au_plafond: bool


def points_de_l_annee(moteur: ScenarioActuel, statut: str, annee: int, etage: str,
                      revenu: float, trimestres: int | float | None = None) -> float:
    """Les points qu'une année de ``statut``, au revenu ``revenu``, ouvre dans
    les régimes de cet étage que le statut cotise cette année-là.

    Les régimes sont ceux du statut, et non ceux où la coordination route une
    carrière d'un an : un fonctionnaire qui part au bout d'un an est rétabli au
    régime général et à l'Ircantec, et ses points d'Ircantec ne disent rien de
    sa rémunération de fonctionnaire.
    """
    from ..carriere import Carriere, LigneRelevee

    regimes = {code for code in moteur.affiliations.regimes(statut, annee)
               if code in moteur.catalogue and moteur.catalogue[code].etage == etage}
    if not regimes:
        return 0.0
    carriere = Carriere.depuis_releve(
        annee - AGE_DANS_L_ANNEE, "H",
        [LigneRelevee(annee, statut, float(revenu), trimestres)],
        AGE_DE_DEPART_FICTIF, moteur.macro,
        identifiant=f"points de {annee}",
    )
    releve = construire(moteur, carriere, avantages_non_contributifs=False,
                        points_gratuits=False, liquider_successions=False)
    return somme_ordonnee((points for code, an, points, _ in releve.droits.points
                           if an == annee and code in regimes), 0.0)


def revenu_des_points(moteur: ScenarioActuel, statut: str, annee: int, etage: str,
                      points: float, trimestres: int | float | None = None
                      ) -> RevenuDesPoints | None:
    """Le revenu entier le plus bas dont une année de ``statut`` ouvre au moins
    ``points`` dans les régimes de l'étage ``etage`` ; ``None`` quand ces
    points ne disent aucun revenu.

    ``trimestres`` sont ceux que le relevé porte pour l'année : le régime de
    base des libéraux d'avant 2004 compte ses points par trimestre, et c'est
    eux, non le revenu, qui les font.
    """
    if etage not in ETAGES_CONVERTIS or points <= 0:
        return None
    haut = math.ceil(PLAFONDS_AU_PLUS * moteur.macro.plafond_securite_sociale(annee))
    if haut < 2:
        return None
    vus: dict[int, float] = {}

    def acquis(revenu: int) -> float:
        if revenu not in vus:
            vus[revenu] = points_de_l_annee(moteur, statut, annee, etage, revenu,
                                            trimestres)
        return vus[revenu]

    # Le plus petit revenu qui cotise ouvre déjà le plancher : des points qui
    # ne le dépassent pas ne disent pas le revenu, ni ceux d'un barème que le
    # revenu ne fait pas bouger.
    plancher, plus_haut = acquis(1), acquis(haut)
    if (plus_haut <= plancher + EPSILON_POINTS or points <= plancher + EPSILON_POINTS
            or points > plus_haut + DEMI_POINT):
        return None
    cible = min(points, plus_haut) - EPSILON_POINTS
    bas = 1
    while haut - bas > 1:
        milieu = (bas + haut) // 2
        if acquis(milieu) >= cible:
            haut = milieu
        else:
            bas = milieu
    return RevenuDesPoints(haut, plus_haut <= acquis(haut) + EPSILON_POINTS)


def _ligne(ident: str, personne: str, fait: str | None, date: str | None,
           droit: dict, *, fiche: str | None = None, version: str | None = None,
           texte: str | None = None, face: str = "droit",
           contributive: bool = True, origine: str = "calculee",
           presomptions: list[str] | None = None,
           fiabilite: str | None = None) -> dict:
    """Une ligne du contrat C.5. Ce qui n'est pas encore su — la version de
    la fiche et le texte appliqué quand la fiche n'est pas découpée, une
    fiche que la règle n'a pas encore — n'y figure pas : c'est un manque,
    pas une erreur."""
    ligne = {"schema_version": SCHEMA_VERSION, "id": ident, "personne": personne}
    if fait is not None:
        ligne["fait"] = fait
    if date is not None:
        ligne["date"] = date
    if fiche is not None:
        ligne["fiche"] = fiche
    if version is not None:
        ligne["version"] = version
    if texte is not None:
        ligne["texte"] = texte
    ligne |= {"droit": droit, "face": face, "contributive": contributive,
              "nature": "ferme", "origine": origine,
              "presomptions": presomptions or []}
    if fiabilite is not None:
        ligne["fiabilite"] = fiabilite
    return ligne


class _Faits:
    """Les faits de la chronologie qu'une ligne du relevé cite."""

    def __init__(self, carriere: Carriere) -> None:
        chronologie = carriere.chronologie or {"faits": []}
        self.personne = carriere.personne
        self.par_id = {f["id"]: f for f in chronologie.get("faits") or []}
        self.periodes = [f for f in chrono.faits_de(chronologie, carriere.personne)
                         if f["sorte"] in (chrono.EMPLOI, chrono.INTERRUPTION)]
        self.naissances = {f["personne"]: f for f in chronologie.get("faits") or []
                           if f["sorte"] == "naissance"}

    def de_l_annee(self, annee: int, code: str,
                   coordination: Coordination) -> str | None:
        """Le fait qui ouvre ce que ``code`` reçoit en ``annee`` : la période
        qui couvre l'année sous un statut que la coordination y route — une
        interruption, quand l'année en est une —, la première dans l'ordre de
        la chronologie."""
        debut, fin = f"{annee:04d}-01-01", f"{annee + 1:04d}-01-01"
        statuts = {ligne.affiliation
                   for ligne, regimes in zip(coordination.carriere.lignes,
                                             coordination.regimes)
                   if ligne.annee == annee and code in regimes}
        couvrent = [f for f in self.periodes
                    if f["debut"] < fin and (f.get("fin") is None or f["fin"] > debut)]
        for fait in couvrent:
            if fait["sorte"] == chrono.INTERRUPTION and "affiliation" not in fait["attributs"]:
                return fait["id"]
        for fait in couvrent:
            if fait["attributs"].get("affiliation") in statuts:
                return fait["id"]
        return None

    def observe(self, fait: str | None) -> bool:
        """Un fait d'un relevé de carrière déposé fait foi : ses trimestres
        sont observés, non calculés."""
        return fait is not None and fait.startswith("releve_")

    def presomptions(self, fait: str | None) -> list[str]:
        element = self.par_id.get(fait) if fait else None
        return [element["presomption"]] if element and element.get("presomption") else []

    def fiabilite(self, fait: str | None) -> str | None:
        element = self.par_id.get(fait) if fait else None
        return element.get("fiabilite") if element else None

    def naissance(self, personne: str) -> dict | None:
        return self.naissances.get(personne)

    def depart(self) -> str | None:
        fait = f"depart_{self.personne}"
        return fait if fait in self.par_id else None
