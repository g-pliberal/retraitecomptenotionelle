"""La limite d'âge des agents publics, et ses exceptions (action 151, étapes 3 et 4).

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
recul : la loi de 1936 ne le nomme pas. Les corps particuliers restent hors
du modèle tant que la saisie ne porte pas le corps.

Depuis l'étape 4, trois emplois de plus ont leur limite, chacune dans sa
fiche, dont chaque version dit, par son paramètre ``exceptions``, celles
des exceptions ci-dessus qui jouent pour eux ce jour-là : l'agent contractuel
de droit public (fiche ``limite_age_contractuels``), dont la prolongation
pour carrière incomplète compte la durée d'assurance tous régimes ;
l'ouvrier de l'État (fiche ``limite_age_ouvriers_etat``) ; l'agent du cadre
permanent de la SNCF et de la RATP (fiche ``limite_age_sncf_ratp``). Depuis
l'étape 6, trois de plus : l'agent des industries électriques et gazières
(fiche ``limite_age_ieg``), dont la prolongation pour carrière incomplète va
jusqu'à la durée du taux maximum moins cent cinquante trimestres (paramètre
``incomplete_au_dela_de``) ; le personnel de l'Opéra national de Paris (fiche
``limite_age_opera``) ; l'agent de la SEITA (fiche ``limite_age_seita``). Leur
pension part de la radiation, celle des régimes que l'emploi radié route.
Depuis l'étape 8, l'agent titulaire de la Banque de France (fiche
``limite_age_banque_de_france``), dont la prorogation pour enfants est celle
de son statut (paramètre ``enfants``), et ne se cumule pas avec la
prolongation pour carrière incomplète (paramètre ``sans_cumul``). Depuis
l'étape 9, la limite d'avant 2008 de l'agent des IEG : l'admission d'office à
la retraite du décret n° 54-50, du 18 janvier 1954 au 27 novembre 2007, dont
la version prête à l'agent la classe que le modèle lui présume (paramètre
``classe_presumee``), et ne s'atteint qu'avec des années de services
(``services_requis``), à un âge au plus tard (``a_defaut_des_services``).
Depuis l'étape 10, le mineur (fiche ``limite_age_mines``), dont la limite est
l'âge d'ouverture de sa pension depuis le décret n° 54-51 du 16 janvier 1954,
et qui peut, dans l'intérêt du service, rester en activité au-delà, sans
borne (exception ``interet_du_service``) : présumé maintenu jusqu'au départ
saisi, il n'est jamais radié par sa limite. Les autres régimes spéciaux —
CRPCEN, marins, Comédie-Française, port de Strasbourg — n'ont pas de limite
au modèle : leurs statuts ne sont pas dans l'index, ou n'en fixent pas.

La limite se lit, version par version, au jour où elle est atteinte (date
``age_atteint``) : chaque version porte, dans ses paramètres, la limite de
chaque classe d'emploi — sédentaire, active, police et surveillance
pénitentiaire, non-officier, officier —, ses paliers en cours de version, ou
le relèvement de la loi de 2010, compté depuis l'année où l'ancien âge de
référence est atteint. La radiation tombe le premier jour où l'âge atteint
la limite alors en vigueur : l'anniversaire, ou le premier jour de la
version qui la crée, quand l'agent l'avait déjà passée ; ses exceptions se
lisent ce jour-là, et non à l'anniversaire qui le précède.

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
FICHE_DES_CONTRACTUELS = "limite_age_contractuels"
FICHE_DES_OUVRIERS = "limite_age_ouvriers_etat"
FICHE_SNCF_RATP = "limite_age_sncf_ratp"
FICHE_IEG = "limite_age_ieg"
FICHE_OPERA = "limite_age_opera"
FICHE_SEITA = "limite_age_seita"
FICHE_BANQUE_DE_FRANCE = "limite_age_banque_de_france"
FICHE_MINES = "limite_age_mines"
#: Les fiches que le module lit, et que le paquet du site porte
#: (``FichesDatees``).
FICHES = (FICHE_DE_LA_LIMITE, FICHE_DES_MILITAIRES, FICHE_DES_ENFANTS,
          FICHE_DE_LA_CARRIERE_INCOMPLETE, FICHE_DE_L_ACTIF, FICHE_DU_MAINTIEN,
          FICHE_DU_PLAFOND, FICHE_DES_CONTRACTUELS, FICHE_DES_OUVRIERS,
          FICHE_SNCF_RATP, FICHE_IEG, FICHE_OPERA, FICHE_SEITA,
          FICHE_BANQUE_DE_FRANCE, FICHE_MINES)
#: Les fiches du code des pensions, fonctionnaires et militaires, dont la
#: radiation ouvre les seuls régimes de ``REGIMES_RADIES``.
FICHES_DU_CODE_DES_PENSIONS = frozenset({FICHE_DE_LA_LIMITE, FICHE_DES_MILITAIRES})

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
#: Les statuts d'agent contractuel de droit public (L. 556-11 du code général
#: de la fonction publique), que leurs régimes ne distinguent pas de l'élu
#: local ou du membre du CESE, affiliés eux aussi à l'Ircantec.
STATUTS_CONTRACTUELS = frozenset({"contractuel_public"})
#: Les régimes dont l'emploi a sa propre limite d'âge, et la fiche qui la
#: porte : celui qui ne les route plus, recruté après leur fermeture, n'en a
#: pas.
FICHE_DU_REGIME = {"fspoeie": FICHE_DES_OUVRIERS, "sncf": FICHE_SNCF_RATP,
                   "ratp": FICHE_SNCF_RATP, "ieg": FICHE_IEG,
                   "opera_de_paris": FICHE_OPERA, "seita": FICHE_SEITA,
                   "banque_de_france": FICHE_BANQUE_DE_FRANCE, "mines": FICHE_MINES}
#: Le régime dont la durée d'assurance décide la prolongation du contractuel
#: pour carrière incomplète (article 5 de la loi n° 2003-775).
REGIME_DU_CONTRACTUEL = "regime_general"

#: Ce qui recule ou prolonge la limite.
RECUL_ENFANTS = "recul_enfants_a_charge"
RECUL_PARENT_DE_TROIS = "recul_parent_de_trois_enfants"
CARRIERE_INCOMPLETE = "prolongation_carriere_incomplete"
PROLONGATION_ACTIVE = "prolongation_categorie_active"
MAINTIEN = "maintien_jusqu_a_70_ans"
MAINTIEN_DANS_L_INTERET_DU_SERVICE = "maintien_dans_l_interet_du_service"

#: Les exceptions qu'une version des fiches des contractuels, des ouvriers et
#: de la SNCF et de la RATP nomme dans son paramètre ``exceptions`` ; une
#: version qui ne le porte pas, celles des fonctionnaires, les ouvre toutes.
ENFANTS = "enfants"
INCOMPLETE = "carriere_incomplete"
ACTIF_JUSQU_AUX_SEDENTAIRES = "prolongation_active"
JUSQU_A_70_ANS = "maintien"
PLAFOND = "plafond"
TOUTES = frozenset({ENFANTS, INCOMPLETE, ACTIF_JUSQU_AUX_SEDENTAIRES, JUSQU_A_70_ANS,
                    PLAFOND})
#: Le maintien sans borne du mineur (décret n° 54-51, article 3), qu'une
#: version ouvre en le nommant, et que le fonctionnaire n'a pas.
INTERET_DU_SERVICE = "interet_du_service"

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
    ouvrent, et la radiation est sa sortie. ``fiche`` est celle de la limite :
    la radiation n'arrête que les services de son emploi."""

    date: DateMois
    age: float
    limite: float
    classe: str
    affiliation: str
    version: str
    regimes: frozenset[str]
    reculs: tuple[Recul, ...]
    forcee: bool
    fiche: str = FICHE_DE_LA_LIMITE

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


def emploi_de(moteur: ScenarioActuel, affiliation: str, annee: int,
              entree: DateMois | None = None) -> tuple[str, str] | None:
    """La fiche de la limite d'âge d'un statut cette année, et sa classe
    d'emploi : celle du militaire, de l'agent contractuel, de l'ouvrier de
    l'État, de l'agent de la SNCF ou de la RATP, ou du fonctionnaire civil
    affilié à un régime du code des pensions ; ``None`` pour un statut sans
    limite d'âge au modèle. ``entree``, l'entrée dans le statut, décide du
    régime de qui a été recruté avant sa fermeture."""
    militaire = moteur.affiliations.pension_militaire(affiliation)
    if militaire is not None:
        return FICHE_DES_MILITAIRES, militaire
    if affiliation in STATUTS_CONTRACTUELS:
        return FICHE_DES_CONTRACTUELS, SEDENTAIRE
    regimes = moteur.affiliations.regimes(affiliation, annee, entree)
    active = moteur.affiliations.categorie_active(affiliation)
    propre = next((FICHE_DU_REGIME[code] for code in sorted(regimes)
                   if code in FICHE_DU_REGIME), None)
    if propre is not None:
        return propre, ACTIVE if active else SEDENTAIRE
    if REGIMES_RADIES.isdisjoint(regimes):
        return None
    if affiliation in STATUTS_DE_POLICE:
        return FICHE_DE_LA_LIMITE, POLICE_PENITENTIAIRE
    return FICHE_DE_LA_LIMITE, ACTIVE if active else SEDENTAIRE


def classe_de(moteur: ScenarioActuel, affiliation: str, annee: int,
              entree: DateMois | None = None) -> str | None:
    """La classe d'emploi d'un statut, qui choisit sa limite
    (:func:`emploi_de`) ; ``None`` pour un statut sans limite d'âge au
    modèle."""
    emploi = emploi_de(moteur, affiliation, annee, entree)
    return None if emploi is None else emploi[1]


def _emploi(moteur: ScenarioActuel, carriere: Carriere, ligne) -> tuple[str, str] | None:
    """L'emploi d'une ligne de la carrière, à sa date d'entrée dans le statut."""
    return emploi_de(moteur, ligne.affiliation, ligne.annee,
                     carriere.date_entree(ligne.affiliation))


def _regimes(moteur: ScenarioActuel, carriere: Carriere, ligne) -> tuple[str, ...]:
    """Les régimes d'une ligne de la carrière, à sa date d'entrée dans le statut."""
    return moteur.affiliations.regimes(ligne.affiliation, ligne.annee,
                                       carriere.date_entree(ligne.affiliation))


def _exceptions(moteur: ScenarioActuel, nom: str, jour: str) -> frozenset[str]:
    """Les exceptions que la fiche de la limite ouvre ce jour-là : toutes,
    pour le fonctionnaire ; celles que sa version nomme, pour les autres ;
    aucune, sans version."""
    if nom == FICHE_DE_LA_LIMITE:
        return TOUTES
    version = _version(moteur, nom, jour)
    if version is None:
        return frozenset()
    nommees = version["parametres"].get("exceptions")
    return TOUTES if nommees is None else frozenset(nommees)


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


def _au_terme_des_services(moteur: ScenarioActuel, carriere: Carriere, nom: str,
                           mois: int, parametres: dict) -> int:
    """La limite, en mois, d'une version qui demande des années de services
    dans l'emploi (``services_requis``), celle du décret n° 54-50 : l'âge de
    la version, ou, si l'agent réunit ces services plus tard, son âge le mois
    qui suit ; au plus tard l'âge ``a_defaut_des_services``, pour qui ne les
    a pas encore."""
    statuts = set()
    for ligne in carriere.lignes:
        emploi = _emploi(moteur, carriere, ligne)
        if emploi is not None and emploi[0] == nom:
            statuts.add(ligne.affiliation)
    plafond = _mois(parametres["a_defaut_des_services"])
    reunis = carriere.date_de_service(statuts, parametres["services_requis"])
    if reunis is None:
        return plafond
    return min(max(mois, _mois(carriere.age_au(reunis.plus_mois(1)))), plafond)


def _limite(moteur: ScenarioActuel, carriere: Carriere, nom: str, classe: str
            ) -> tuple[int, str, str] | None:
    """La limite d'âge de cette classe, en mois, la version qui la donne, et le
    jour où l'agent l'atteint : le premier jour où l'âge atteint la limite en
    vigueur ce jour-là, son anniversaire, ou le premier jour de la version qui
    la crée quand il l'avait déjà passée. Une version peut prêter à l'agent la
    classe que le modèle lui présume (``classe_presumee``), et ne s'atteindre
    qu'avec des années de services (:func:`_au_terme_des_services`)."""
    fiche = _fiche(moteur, nom)
    if fiche is None:
        return None
    ordre = sorted(fiche["versions"],
                   key=lambda v: (v["bornes"].get("age_atteint") or [None])[0] or "")
    for version in ordre:
        parametres = version["parametres"]
        for debut, fin, mois in _morceaux(carriere, version,
                                          parametres.get("classe_presumee", classe)):
            if "services_requis" in parametres:
                mois = _au_terme_des_services(moteur, carriere, nom, mois, parametres)
            jour = _jour(carriere, mois)
            if debut is not None and jour < debut:
                jour = debut
            if fin is None or jour < fin:
                return max(mois, _mois_au(carriere, jour)), version["id"], jour
    return None


def _enfants_a_charge(carriere: Carriere, jour: str, age_a_charge: float) -> int:
    """Les enfants nés au plus tard ce jour, qui n'ont pas encore l'âge où
    cessent les prestations familiales."""
    annees = int(age_a_charge)
    seuil = f"{int(jour[:4]) - annees:04d}{jour[4:]}"
    return len([naissance for _, naissance in carriere.naissances_des_enfants
                if seuil < naissance <= jour])


def _prorogation_du_statut(carriere: Carriere, limite: int, nom: str, version: dict,
                           parametres: dict, jour: str) -> Recul | None:
    """La prorogation pour enfants qu'un statut écrit lui-même (paramètre
    ``enfants`` de la version de la limite), celle de la Banque de France :
    tant d'années pour tant d'enfants à charge le jour où la limite est
    atteinte, et tant d'autres élevés jusqu'à l'âge dit, que le modèle compte
    parmi ceux qui ne sont plus à charge, la plus longue qui s'applique, sous
    le plafond de ``au_plus`` années."""
    a_charge = _enfants_a_charge(carriere, jour, parametres["age_a_charge"])
    annees = int(max(parametres["age_a_charge"], parametres["eleves_jusqu_a"]))
    seuil = f"{int(jour[:4]) - annees:04d}{jour[4:]}"
    eleves = len([naissance for _, naissance in carriere.naissances_des_enfants
                  if naissance <= seuil])
    ans = max([p["ans"] for p in parametres["prorogations"]
               if a_charge >= p["a_charge"] and eleves >= p.get("eleves", 0)], default=0)
    recul = _mois(min(ans, parametres["au_plus"]))
    if recul <= 0:
        return None
    return Recul(RECUL_ENFANTS, nom, version["id"], limite / MOIS_PAR_AN,
                 (limite + recul) / MOIS_PAR_AN, presumee=False)


def _reculs_pour_enfants(moteur: ScenarioActuel, carriere: Carriere, limite: int,
                         classe: str, nom: str, jour: str) -> Recul | None:
    """Le recul de droit pour enfants, au jour où la limite est atteinte : un
    an par enfant à charge, trois au plus, ou un an pour le parent de trois
    enfants vivants à cinquante ans — le plus favorable des deux, que la loi ne
    cumule que pour un enfant invalide —, sous les plafonds de la version ;
    celui que le statut écrit lui-même, quand la version de sa limite le
    porte (:func:`_prorogation_du_statut`)."""
    if classe in (NON_OFFICIER, OFFICIER):
        return None
    propre = None if nom in FICHES_DU_CODE_DES_PENSIONS else _version(moteur, nom, jour)
    if propre is not None and propre["parametres"].get("enfants"):
        return _prorogation_du_statut(carriere, limite, nom, propre,
                                      propre["parametres"]["enfants"], jour)
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
                                      regime: str | None, nom: str, jour: str
                                      ) -> Recul | None:
    """La prolongation pour carrière incomplète, lue au jour où l'agent atteint
    l'âge ``depuis`` : jusqu'à la durée des services du taux maximum (L. 13),
    dix trimestres au plus, que le modèle compte sur les seuls services, sans
    les bonifications. La version de la limite qui porte
    ``incomplete_au_dela_de``, celle des industries électriques et gazières,
    la borne à la durée du taux maximum moins ce nombre de trimestres, et la
    prolongation est la sienne."""
    propre = None if nom in FICHES_DU_CODE_DES_PENSIONS else _version(moteur, nom, jour)
    au_dela_de = None if propre is None else propre["parametres"].get("incomplete_au_dela_de")
    if au_dela_de is not None:
        fiche, version = nom, propre
    else:
        fiche, version = (FICHE_DE_LA_CARRIERE_INCOMPLETE,
                          _version(moteur, FICHE_DE_LA_CARRIERE_INCOMPLETE, jour))
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
    au_plus = (requis - au_dela_de if au_dela_de is not None
               else version["parametres"]["trimestres_au_plus"])
    prolongation = min(manque, au_plus * 3)
    if prolongation <= 0:
        return None
    return Recul(CARRIERE_INCOMPLETE, fiche, version["id"],
                 depuis / MOIS_PAR_AN, (depuis + prolongation) / MOIS_PAR_AN,
                 presumee=True)


def _jusqu_a_la_limite(moteur: ScenarioActuel, carriere: Carriere, depuis: int,
                       classe: str, nom_de_la_limite: str, jour: str) -> Recul | None:
    """La prolongation de l'actif jusqu'à la limite des sédentaires, ou le
    maintien du sédentaire jusqu'à soixante-dix ans, lus au jour où l'agent
    atteint l'âge ``depuis``."""
    if classe == SEDENTAIRE:
        version = _version(moteur, FICHE_DU_MAINTIEN, jour)
        age = None if version is None else version["parametres"].get("jusqu_a")
        cible = None if age is None else _mois(age)
        nom, fiche = MAINTIEN, FICHE_DU_MAINTIEN
    else:
        version = _version(moteur, FICHE_DE_L_ACTIF, jour)
        if version is None or version["parametres"].get("jusqu_a") != SEDENTAIRE:
            return None
        lue = _limite(moteur, carriere, nom_de_la_limite, SEDENTAIRE)
        cible = None if lue is None else lue[0]
        nom, fiche = PROLONGATION_ACTIVE, FICHE_DE_L_ACTIF
    if cible is None or cible <= depuis:
        return None
    return Recul(nom, fiche, version["id"], depuis / MOIS_PAR_AN, cible / MOIS_PAR_AN,
                 presumee=True)


def _memes_emplois(nom: str) -> frozenset[str]:
    """Les fiches dont la radiation arrête les services : celles du code des
    pensions ensemble, le fonctionnaire et le militaire ; la sienne seule
    pour les autres."""
    return FICHES_DU_CODE_DES_PENSIONS if nom in FICHES_DU_CODE_DES_PENSIONS else frozenset({nom})


def _lignes_radiees(moteur: ScenarioActuel, carriere: Carriere):
    return [ligne for ligne in carriere.lignes
            if ligne.annee <= carriere.annee_liquidation
            and _emploi(moteur, carriere, ligne) is not None]


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
    nom, classe = _emploi(moteur, carriere, derniere)
    declare = carriere.date_liquidation
    fin = declare if derniere.annee >= declare.annee else DateMois(derniere.annee + 1, 1)
    militaire = classe in (NON_OFFICIER, OFFICIER)
    lue = _limite(moteur, carriere, nom, classe)
    if lue is None:
        return None
    limite, version, jour_limite = lue
    if carriere.date_de_l_age(limite / MOIS_PAR_AN) >= fin:
        return None

    def au(mois: int) -> str:
        # Le jour où l'agent atteint cet âge, jamais avant celui où il atteint
        # sa limite, qu'une version a pu créer après son anniversaire.
        return max(_jour(carriere, mois), jour_limite)

    # Les services de l'emploi : ceux du code des pensions, fonctionnaire ou
    # militaire, ensemble ; ceux de la même fiche, pour les autres, dont la
    # radiation ouvre tous les régimes que l'emploi route.
    code_des_pensions = nom in FICHES_DU_CODE_DES_PENSIONS
    memes = _memes_emplois(nom)
    services = [ligne for ligne in lignes
                if _emploi(moteur, carriere, ligne)[0] in memes]
    regimes = frozenset(
        code for ligne in services
        for code in _regimes(moteur, carriere, ligne)
        if code in REGIMES_RADIES or not code_des_pensions)
    candidats: list[Recul] = []
    if not militaire:
        if nom == FICHE_DES_CONTRACTUELS:
            # La durée d'assurance tous régimes, que le modèle compte par les
            # années cotisées de toute la carrière, sans les périodes assimilées.
            civiles = frozenset(ligne.affiliation for ligne in carriere.lignes
                                if ligne.cotise)
            regime = REGIME_DU_CONTRACTUEL
        else:
            civiles = frozenset(ligne.affiliation for ligne in services
                                if _emploi(moteur, carriere, ligne)[1]
                                not in (NON_OFFICIER, OFFICIER))
            propres = REGIMES_RADIES if code_des_pensions else FICHE_DU_REGIME
            regime = next((code for code in sorted(_regimes(moteur, carriere, derniere))
                           if code in propres), None)
        atteint = limite
        enfants = (_reculs_pour_enfants(moteur, carriere, atteint, classe, nom, au(atteint))
                   if ENFANTS in _exceptions(moteur, nom, au(atteint)) else None)
        if enfants is not None:
            candidats.append(enfants)
            atteint = _mois(enfants.jusqu_a)
        # Sans cumul (Banque de France, article 242-1), la prolongation part
        # de la limite, et seule la plus longue des deux exceptions reste.
        de_la_limite = None if code_des_pensions else _version(moteur, nom, jour_limite)
        sans_cumul = bool(de_la_limite and de_la_limite["parametres"].get("sans_cumul"))
        depuis = limite if sans_cumul else atteint
        incomplete = (_prolongation_carriere_incomplete(
            moteur, carriere, depuis, civiles, regime, nom, au(depuis))
            if INCOMPLETE in _exceptions(moteur, nom, au(depuis)) else None)
        if incomplete is not None and sans_cumul and enfants is not None:
            if incomplete.jusqu_a > enfants.jusqu_a:
                candidats.remove(enfants)
            else:
                incomplete = None
        if incomplete is not None:
            candidats.append(incomplete)
            atteint = _mois(incomplete.jusqu_a)
        ouvertes = _exceptions(moteur, nom, au(atteint))
        prolongee = (_jusqu_a_la_limite(moteur, carriere, atteint, classe, nom, au(atteint))
                     if (JUSQU_A_70_ANS if classe == SEDENTAIRE
                         else ACTIF_JUSQU_AUX_SEDENTAIRES) in ouvertes else None)
        if prolongee is not None:
            candidats.append(prolongee)
            atteint = _mois(prolongee.jusqu_a)
        # Le maintien dans l'intérêt du service du mineur (décret n° 54-51,
        # article 3), sans borne : présumé accordé jusqu'au départ saisi, il ne
        # laisse jamais la limite radier.
        if INTERET_DU_SERVICE in _exceptions(moteur, nom, au(atteint)):
            jusqu_au_depart = _mois(carriere.age_au(declare))
            if jusqu_au_depart > atteint:
                candidats.append(Recul(MAINTIEN_DANS_L_INTERET_DU_SERVICE, nom,
                                       _version(moteur, nom, au(atteint))["id"],
                                       atteint / MOIS_PAR_AN,
                                       jusqu_au_depart / MOIS_PAR_AN, presumee=True))
                atteint = jusqu_au_depart
        plafond = (_version(moteur, FICHE_DU_PLAFOND, au(atteint))
                   if PLAFOND in _exceptions(moteur, nom, au(atteint)) else None)
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
                     regimes, reculs, forcee=au_plus_tard <= fin and au_plus_tard < declare,
                     fiche=nom)


def radier(moteur: ScenarioActuel, carriere: Carriere) -> Carriere:
    """La carrière dont les services de l'emploi radié s'arrêtent à la
    radiation par limite d'âge, quand elle précède leur fin déclarée : les
    années qui la suivent ne sont plus du service, et la carrière n'en garde
    que les autres métiers. L'année de la radiation reste, que la date
    d'effet de la pension borne. Rendue telle quelle sans radiation forcée."""
    radiee = radiation(moteur, carriere)
    if radiee is None or not radiee.forcee:
        return carriere
    derniere = radiee.date.annee - (1 if radiee.date.mois == 1 else 0)
    memes = _memes_emplois(radiee.fiche)

    def de_l_emploi(ligne) -> bool:
        emploi = _emploi(moteur, carriere, ligne)
        return emploi is not None and emploi[0] in memes

    gardees = [ligne for ligne in carriere.lignes
               if ligne.annee <= derniere or not de_l_emploi(ligne)]
    if len(gardees) == len(carriere.lignes):
        return carriere
    return carriere.avec_lignes(gardees)
