"""La limite d'âge des fonctionnaires, et ses exceptions (action 151, étape 3).

« Le fonctionnaire ne peut être maintenu en fonctions au-delà de l'âge limite
de l'activité dans l'emploi qu'il occupe, sous réserve des exceptions prévues
par les dispositions en vigueur » (L. 556-1 du code général de la fonction
publique) : il est radié des cadres d'office le lendemain de l'anniversaire,
et sa pension est due « du jour de la cessation de l'activité » (L. 90 du code
des pensions). Le modèle gardait en service, traitement, services et surcote
compris, le fonctionnaire dont le départ saisi passait sa limite, jusqu'à
cent dix-neuf ans depuis l'étape 1 de l'action 151.

Décision du propriétaire, le 14 octobre 2026 : la carrière de fonctionnaire
s'arrête à la limite, reculée et prolongée par les exceptions qui
s'appliquent, et la pension de fonctionnaire part de ce jour ; ce qui suit,
jusqu'au départ saisi, n'est plus du service, mais peut être un métier de
plus. Les exceptions, dans l'ordre que la loi leur donne (relation
``plafond_limite_age_fonction_publique``) :

* DE DROIT, les reculs pour enfants (fiche ``recul_limite_age_enfants``) : un
  an par enfant à charge quand la limite est atteinte, trois au plus, ou un an
  pour qui était parent de trois enfants vivants à ses cinquante ans, les deux
  ne se cumulant que pour un enfant invalide, que la saisie ne connaît pas ;
* PRÉSUMÉES DEMANDÉES ET ACCORDÉES autant que le départ saisi les demande
  (présomption ``exceptions_a_la_limite_d_age``) : la prolongation pour
  carrière incomplète, jusqu'à la durée du taux maximum, dix trimestres au
  plus (fiche ``prolongation_activite_carriere_incomplete``) ; celle de
  l'actif, jusqu'à la limite des sédentaires (fiche
  ``prolongation_activite_categorie_active``) ; le maintien du sédentaire
  jusqu'à soixante-dix ans (fiche ``maintien_en_fonctions_jusqu_a_70_ans``) ;
* depuis le 14 juin 2023, leur bénéfice cumulé ne mène pas au-delà de
  soixante-dix ans.

Le militaire, dont la saisie ne connaît ni le grade ni le corps, prend la
limite la plus haute de sa catégorie (fiche ``limite_age_militaires``), sans
recul : la loi de 1936 ne le nomme pas. Les agents contractuels, les ouvriers
de l'État et les régimes spéciaux, qui ont leur propre limite, viendront à
une étape suivante ; les corps particuliers restent hors du modèle tant que
la saisie ne porte pas le corps.

La limite se lit, version par version, au jour où elle est atteinte (date
``age_atteint``) : chaque version porte, dans ses paramètres, la limite de
chaque classe d'emploi — sédentaire, active, police et surveillance
pénitentiaire, non-officier, officier —, ses paliers en cours de version, ou
le relèvement de la loi de 2010, compté depuis l'année où l'ancien âge de
référence est atteint. La radiation tombe le premier jour où l'âge atteint
la limite alors en vigueur.

:func:`radiation` dit la radiation d'une carrière et ce qui la recule ;
:func:`radier` rend la carrière dont les services s'arrêtent à la radiation,
que le scénario 1 liquide, et que l'étape des départs lit
(:mod:`.departs`). Le jumeau de ce module est ``moteur/js/droit/limite_age.js``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from ..noyau import versions
from . import ouvrir
from .commun import periode_de_liquidation

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ScenarioActuel

FICHE_DE_LA_LIMITE = "limite_age_fonction_publique"
FICHE_DES_MILITAIRES = "limite_age_militaires"
FICHE_DES_ENFANTS = "recul_limite_age_enfants"
FICHE_DE_LA_CARRIERE_INCOMPLETE = "prolongation_activite_carriere_incomplete"
FICHE_DE_L_ACTIF = "prolongation_activite_categorie_active"
FICHE_DU_MAINTIEN = "maintien_en_fonctions_jusqu_a_70_ans"
FICHE_DU_PLAFOND = "plafond_limite_age_fonction_publique"
#: Les fiches que le module lit, et que le paquet du site porte
#: (``FichesDatees``).
FICHES = (FICHE_DE_LA_LIMITE, FICHE_DES_MILITAIRES, FICHE_DES_ENFANTS,
          FICHE_DE_LA_CARRIERE_INCOMPLETE, FICHE_DE_L_ACTIF, FICHE_DU_MAINTIEN,
          FICHE_DU_PLAFOND)

#: Les régimes du code des pensions, dont l'agent est radié des cadres : un
#: statut qui y est affilié a une limite d'âge.
REGIMES_RADIES = frozenset({"fonction_publique_etat", "cnracl", "pensions_civiles_1853"})

#: Les classes d'emploi, que les paramètres des fiches nomment.
SEDENTAIRE = "sedentaire"
ACTIVE = "active"
POLICE_PENITENTIAIRE = "police_penitentiaire"
NON_OFFICIER = "non_officier"
OFFICIER = "officier"
#: Les statuts de la police nationale et de la surveillance pénitentiaire,
#: dont la limite est cinquante-sept ans (L. 556-8 et L. 556-9).
STATUTS_DE_POLICE = frozenset({"policier", "fonctionnaire_etat_super_actif"})

#: Ce qui recule ou prolonge la limite.
RECUL_ENFANTS = "recul_enfants_a_charge"
RECUL_PARENT_DE_TROIS = "recul_parent_de_trois_enfants"
CARRIERE_INCOMPLETE = "prolongation_carriere_incomplete"
PROLONGATION_ACTIVE = "prolongation_categorie_active"
MAINTIEN = "maintien_jusqu_a_70_ans"

MOIS_PAR_AN = 12


@dataclass(frozen=True)
class Recul:
    """Une exception qui recule ou prolonge la limite : de quel âge à quel âge
    elle garde l'agent en fonctions, la version de sa fiche, et si le modèle
    la présume demandée et accordée (``presumee``) ou si elle est de droit."""

    nom: str
    fiche: str
    version: str
    depuis: float
    jusqu_a: float
    presumee: bool


@dataclass(frozen=True)
class Radiation:
    """La radiation des cadres par limite d'âge d'une carrière.

    ``date`` est le premier mois de la pension, celui qui suit l'anniversaire ;
    ``limite``, la limite de l'emploi, avant tout recul ; ``reculs``, les
    exceptions qui la reculent jusqu'à la radiation, dans l'ordre de la loi.
    ``forcee`` dit que la radiation précède la fin des services que la saisie
    déclare : les services s'arrêtent là, et la pension part de ce jour ;
    sinon, l'agent quitte le service avant la limite que les exceptions lui
    ouvrent, et la radiation est sa sortie."""

    date: DateMois
    age: float
    limite: float
    classe: str
    affiliation: str
    version: str
    regimes: frozenset[str]
    reculs: tuple[Recul, ...]
    forcee: bool

    @property
    def presumees(self) -> tuple[Recul, ...]:
        """Les exceptions que le modèle présume demandées et accordées."""
        return tuple(recul for recul in self.reculs if recul.presumee)


def _fiche(moteur: ScenarioActuel, nom: str) -> dict | None:
    return moteur.fiches_datees.fiches().get(nom)


def _version(moteur: ScenarioActuel, nom: str, jour: str) -> dict | None:
    fiche = _fiche(moteur, nom)
    return None if fiche is None else versions.applicable(fiche, {"age_atteint": jour})


def _mois(age: float) -> int:
    return round(age * MOIS_PAR_AN)


def _jour(carriere: Carriere, mois: int) -> str:
    """Le jour (AAAA-MM-JJ) où l'assuré atteint cet âge, en mois : son
    anniversaire, qui décide de la version (date ``age_atteint``)."""
    anniversaire = carriere.date_naissance.plus_mois(mois)
    return (f"{anniversaire.annee:04d}-{anniversaire.mois:02d}-"
            f"{min(carriere.jour_de_naissance, 28):02d}")


def _mois_au(carriere: Carriere, jour: str) -> int:
    """L'âge, en mois révolus, à ce jour (AAAA-MM-JJ)."""
    annee, mois, quantieme = (int(x) for x in jour.split("-"))
    naissance = carriere.date_naissance
    ecart = (annee - naissance.annee) * MOIS_PAR_AN + mois - naissance.mois
    return ecart - (1 if quantieme < min(carriere.jour_de_naissance, 28) else 0)


def classe_de(moteur: ScenarioActuel, affiliation: str, annee: int) -> str | None:
    """La classe d'emploi d'un statut, qui choisit sa limite : celle du
    militaire, ou celle du fonctionnaire civil affilié à un régime du code des
    pensions ; ``None`` pour un statut sans limite d'âge au modèle."""
    militaire = moteur.affiliations.pension_militaire(affiliation)
    if militaire is not None:
        return militaire
    if REGIMES_RADIES.isdisjoint(moteur.affiliations.regimes(affiliation, annee)):
        return None
    if affiliation in STATUTS_DE_POLICE:
        return POLICE_PENITENTIAIRE
    return ACTIVE if moteur.affiliations.categorie_active(affiliation) else SEDENTAIRE


def _age_de_la_version(carriere: Carriere, parametres: dict, classe: str) -> int | None:
    """La limite, en mois, que les paramètres d'une version donnent à cette
    classe : écrite, ou relevée selon l'année où l'âge de référence d'avant
    est atteint (loi n° 2010-1330, articles 28, 31 et 33)."""
    limites = parametres.get("limites") or {}
    if classe in limites:
        return _mois(limites[classe])
    avant = parametres.get("limites_avant") or {}
    if classe not in avant:
        return None
    ancienne = _mois(avant[classe])
    repere = _jour(carriere, ancienne - _mois(parametres.get("ecart_de_reference", 0)))
    plus = 0
    for marche in parametres.get("marche") or []:
        if repere >= marche["depuis"]:
            plus = marche["mois"]
    return ancienne + plus


def _morceaux(carriere: Carriere, version: dict, classe: str
              ) -> list[tuple[str | None, str | None, int]]:
    """La limite de cette classe sous une version, morceau par morceau : du
    début de la version, puis de chacun de ses paliers."""
    debut, fin = version["bornes"].get("age_atteint") or [None, None]
    parametres = version["parametres"]
    base = _age_de_la_version(carriere, parametres, classe)
    morceaux: list[tuple[str | None, str | None, int | None]] = [(debut, fin, base)]
    for palier in parametres.get("paliers") or []:
        if classe not in palier:
            continue
        precedent = morceaux.pop()
        morceaux.append((precedent[0], palier["depuis"], precedent[2]))
        morceaux.append((palier["depuis"], fin, _mois(palier[classe])))
    return [(d, f, m) for d, f, m in morceaux if m is not None]


def _limite(moteur: ScenarioActuel, carriere: Carriere, nom: str, classe: str
            ) -> tuple[int, str] | None:
    """La limite d'âge de cette classe, en mois, et la version qui la donne :
    le premier jour où l'âge atteint la limite en vigueur ce jour-là."""
    fiche = _fiche(moteur, nom)
    if fiche is None:
        return None
    ordre = sorted(fiche["versions"],
                   key=lambda v: (v["bornes"].get("age_atteint") or [None])[0] or "")
    for version in ordre:
        for debut, fin, mois in _morceaux(carriere, version, classe):
            jour = _jour(carriere, mois)
            if debut is not None and jour < debut:
                jour = debut
            if fin is None or jour < fin:
                return max(mois, _mois_au(carriere, jour)), version["id"]
    return None


def _enfants_a_charge(carriere: Carriere, jour: str, age_a_charge: float) -> int:
    """Les enfants nés au plus tard ce jour, qui n'ont pas encore l'âge où
    cessent les prestations familiales."""
    annees = int(age_a_charge)
    seuil = f"{int(jour[:4]) - annees:04d}{jour[4:]}"
    return len([naissance for _, naissance in carriere.naissances_des_enfants
                if seuil < naissance <= jour])


def _reculs_pour_enfants(moteur: ScenarioActuel, carriere: Carriere, limite: int,
                         classe: str) -> Recul | None:
    """Le recul de droit pour enfants, au jour où la limite est atteinte : un
    an par enfant à charge, trois au plus, ou un an pour le parent de trois
    enfants vivants à cinquante ans — le plus favorable des deux, que la loi ne
    cumule que pour un enfant invalide —, sous les plafonds de la version."""
    if classe in (NON_OFFICIER, OFFICIER):
        return None
    jour = _jour(carriere, limite)
    version = _version(moteur, FICHE_DES_ENFANTS, jour)
    if version is None or not version["parametres"]:
        return None
    parametres = version["parametres"]
    groupe = SEDENTAIRE if classe == SEDENTAIRE else ACTIVE

    def plafonne(recul: int, plafonds: dict | None) -> int:
        plafond = (plafonds or {}).get(groupe)
        return recul if plafond is None else min(recul, max(0, _mois(plafond) - limite))

    a_charge = _enfants_a_charge(carriere, jour, parametres["age_a_charge"])
    par_enfant = plafonne(
        _mois(min(a_charge, parametres["enfants_au_plus"]) * parametres["par_enfant"]),
        parametres.get("plafond_par_enfant"))
    cinquante = _jour(carriere, _mois(parametres["age_du_parent"]))
    nes = len([naissance for _, naissance in carriere.naissances_des_enfants
               if naissance <= cinquante])
    parent = (plafonne(_mois(parametres["parent_de_trois"]), parametres.get("plafond_du_parent"))
              if nes >= parametres["enfants_du_parent"] else 0)
    recul, nom = ((parent, RECUL_PARENT_DE_TROIS) if parent > par_enfant
                  else (par_enfant, RECUL_ENFANTS))
    if recul <= 0:
        return None
    return Recul(nom, FICHE_DES_ENFANTS, version["id"], limite / MOIS_PAR_AN,
                 (limite + recul) / MOIS_PAR_AN, presumee=False)


def _prolongation_carriere_incomplete(moteur: ScenarioActuel, carriere: Carriere,
                                      depuis: int, affiliations: frozenset[str],
                                      regime: str | None) -> Recul | None:
    """La prolongation pour carrière incomplète : jusqu'à la durée des services
    du taux maximum (L. 13), dix trimestres au plus, que le modèle compte sur
    les seuls services, sans les bonifications."""
    version = _version(moteur, FICHE_DE_LA_CARRIERE_INCOMPLETE, _jour(carriere, depuis))
    if version is None or not version["parametres"].get("trimestres_au_plus"):
        return None
    if regime is None or regime not in moteur.catalogue:
        return None
    date = carriere.date_de_l_age(depuis / MOIS_PAR_AN)
    periode = periode_de_liquidation(moteur.catalogue[regime], date)
    if periode is None:
        return None
    requis = ouvrir.duree_requise(moteur, periode, carriere.liquidee_au(date))[0]
    services = carriere.duree_de_service_avant(affiliations, date)
    manque = math.ceil((requis / 4 - services) * MOIS_PAR_AN - 1e-9)
    prolongation = min(manque, version["parametres"]["trimestres_au_plus"] * 3)
    if prolongation <= 0:
        return None
    return Recul(CARRIERE_INCOMPLETE, FICHE_DE_LA_CARRIERE_INCOMPLETE, version["id"],
                 depuis / MOIS_PAR_AN, (depuis + prolongation) / MOIS_PAR_AN,
                 presumee=True)


def _jusqu_a_la_limite(moteur: ScenarioActuel, carriere: Carriere, depuis: int,
                       classe: str) -> Recul | None:
    """La prolongation de l'actif jusqu'à la limite des sédentaires, ou le
    maintien du sédentaire jusqu'à soixante-dix ans."""
    jour = _jour(carriere, depuis)
    if classe == SEDENTAIRE:
        version = _version(moteur, FICHE_DU_MAINTIEN, jour)
        age = None if version is None else version["parametres"].get("jusqu_a")
        cible = None if age is None else _mois(age)
        nom, fiche = MAINTIEN, FICHE_DU_MAINTIEN
    else:
        version = _version(moteur, FICHE_DE_L_ACTIF, jour)
        if version is None or version["parametres"].get("jusqu_a") != SEDENTAIRE:
            return None
        lue = _limite(moteur, carriere, FICHE_DE_LA_LIMITE, SEDENTAIRE)
        cible = None if lue is None else lue[0]
        nom, fiche = PROLONGATION_ACTIVE, FICHE_DE_L_ACTIF
    if cible is None or cible <= depuis:
        return None
    return Recul(nom, fiche, version["id"], depuis / MOIS_PAR_AN, cible / MOIS_PAR_AN,
                 presumee=True)


def _lignes_radiees(moteur: ScenarioActuel, carriere: Carriere):
    return [ligne for ligne in carriere.lignes
            if ligne.annee <= carriere.annee_liquidation
            and classe_de(moteur, ligne.affiliation, ligne.annee) is not None]


def radiation(moteur: ScenarioActuel, carriere: Carriere) -> Radiation | None:
    """La radiation des cadres par limite d'âge de ``carriere``, ou ``None``
    quand ses services de fonctionnaire ou de militaire finissent avant sa
    limite, ou qu'elle n'en a pas.

    La limite est celle de l'emploi de ses derniers services ; les services
    finissent au départ saisi quand ils durent jusqu'à son année, au 1er
    janvier qui suit leur dernière année sinon (présomption
    ``radiation_au_1er_janvier_suivant``). Chaque exception joue autant que
    ces services la demandent : la radiation tombe à leur fin, ou à la limite
    la plus tardive que les exceptions ouvrent si elle vient avant."""
    if carriere.age_liquidation is None:
        return None
    lignes = [ligne for ligne in _lignes_radiees(moteur, carriere) if ligne.cotise]
    if not lignes:
        return None
    derniere = max(lignes, key=lambda ligne: ligne.annee)
    affiliation = derniere.affiliation
    classe = classe_de(moteur, affiliation, derniere.annee)
    declare = carriere.date_liquidation
    fin = declare if derniere.annee >= declare.annee else DateMois(derniere.annee + 1, 1)
    militaire = classe in (NON_OFFICIER, OFFICIER)
    lue = _limite(moteur, carriere,
                  FICHE_DES_MILITAIRES if militaire else FICHE_DE_LA_LIMITE, classe)
    if lue is None:
        return None
    limite, version = lue
    if carriere.date_de_l_age(limite / MOIS_PAR_AN) >= fin:
        return None
    regimes = frozenset(
        code for ligne in lignes
        for code in moteur.affiliations.regimes(ligne.affiliation, ligne.annee)
        if code in REGIMES_RADIES)
    candidats: list[Recul] = []
    if not militaire:
        civiles = frozenset(ligne.affiliation for ligne in lignes
                            if classe_de(moteur, ligne.affiliation, ligne.annee)
                            not in (NON_OFFICIER, OFFICIER))
        regime = next((code for code in sorted(moteur.affiliations.regimes(
            affiliation, derniere.annee)) if code in REGIMES_RADIES), None)
        atteint = limite
        enfants = _reculs_pour_enfants(moteur, carriere, atteint, classe)
        if enfants is not None:
            candidats.append(enfants)
            atteint = _mois(enfants.jusqu_a)
        incomplete = _prolongation_carriere_incomplete(
            moteur, carriere, atteint, civiles, regime)
        if incomplete is not None:
            candidats.append(incomplete)
            atteint = _mois(incomplete.jusqu_a)
        prolongee = _jusqu_a_la_limite(moteur, carriere, atteint, classe)
        if prolongee is not None:
            candidats.append(prolongee)
            atteint = _mois(prolongee.jusqu_a)
        plafond = _version(moteur, FICHE_DU_PLAFOND, _jour(carriere, atteint))
        maximum = None if plafond is None else plafond["parametres"].get("age_maximal")
        if maximum is not None:
            plafonne = max(_mois(maximum), limite)
            candidats = [Recul(r.nom, r.fiche, r.version, r.depuis,
                               min(r.jusqu_a, plafonne / MOIS_PAR_AN), r.presumee)
                         for r in candidats if _mois(r.depuis) < plafonne]
    ouverte = max([limite] + [_mois(r.jusqu_a) for r in candidats])
    au_plus_tard = carriere.date_de_l_age(ouverte / MOIS_PAR_AN)
    date = min(fin, au_plus_tard)
    age = carriere.age_au(date)
    reculs = tuple(Recul(r.nom, r.fiche, r.version, r.depuis, min(r.jusqu_a, age), r.presumee)
                   for r in candidats
                   if carriere.date_de_l_age(r.depuis) < date)
    return Radiation(date, age, limite / MOIS_PAR_AN, classe, affiliation, version,
                     regimes, reculs, forcee=au_plus_tard <= fin and au_plus_tard < declare)


def radier(moteur: ScenarioActuel, carriere: Carriere) -> Carriere:
    """La carrière dont les services de fonctionnaire ou de militaire
    s'arrêtent à la radiation par limite d'âge, quand elle précède leur fin
    déclarée : les années qui la suivent ne sont plus du service, et la
    carrière n'en garde que les autres métiers. L'année de la radiation reste,
    que la date d'effet de la pension borne. Rendue telle quelle sans
    radiation forcée."""
    radiee = radiation(moteur, carriere)
    if radiee is None or not radiee.forcee:
        return carriere
    derniere = radiee.date.annee - (1 if radiee.date.mois == 1 else 0)
    gardees = [ligne for ligne in carriere.lignes
               if ligne.annee <= derniere
               or classe_de(moteur, ligne.affiliation, ligne.annee) is None]
    if len(gardees) == len(carriere.lignes):
        return carriere
    return carriere.avec_lignes(gardees)
