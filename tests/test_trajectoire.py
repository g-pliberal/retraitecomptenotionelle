"""Le scénario 1 confronté à TRAJECTOiRE, le modèle de la DREES, exécuté à part.

TRAJECTOiRE est le modèle de microsimulation de la DREES, dont un module
calcule les cas types du Conseil d'orientation des retraites (registre,
`data/reference/referents.yaml`, `trajectoire`). Son code est sous EUPL-1.2 : il
s'exécute À PART, dans R (`scripts/fetch/trajectoire.py` et `trajectoire.R`),
et seules ses sorties entrent au dépôt, figées dans
`tests/temoins/trajectoire.json` avec leur origine, leur licence, le commit, la
législation retenue — la plus récente qu'il porte, la loi du 14 avril 2023,
sans celle du 30 décembre 2025 — et les paramètres qui expliquent ses montants.

Deux jeux de cas. LES CAS TYPES DU COR, que TRAJECTOiRE construit lui-même par
le script qu'il livre, générations 1955, 1960, 1963, 1964 et 1970, au premier
âge du taux plein qu'il marque ; leur carrière est réécrite en requête du
simulateur, dans la mesure où le formulaire sait la dire. LES ONZE DROITS
DIRECTS de Destinie 2, les mêmes requêtes que son témoin : trois modèles sur
une même carrière. Les départs postérieurs à 2026 ne confrontent que les âges,
les durées et les taux : leurs montants reposent, des deux côtés, sur des
projections dont la convention n'est pas tranchée.

**Ce test n'exécute pas TRAJECTOiRE.** Il rejoue chaque requête dans le
scénario 1 et confronte durées, durée requise, âge d'ouverture, carrière
longue, taux, pensions de base et de la fonction publique, salaire annuel
moyen, traitement de référence, points et valeur du point de l'Agirc-Arrco,
RAFP, majorations pour enfants et minima. Chaque quantité concorde à sa
tolérance, ou son écart est DÉCLARÉ avec sa cause et sa borne (`ECARTS`) ; un
écart déclaré qui rentre dans la tolérance fait échouer le test. Trois
mécanismes sont refaits au lieu d'être bornés : le salaire annuel moyen, la
valeur du point et l'acquisition des points.

Ce que la première exécution a montré, le 5 octobre 2026 :

* **Concordent** — les durées, au tiers de trimestre près de la fonction
  publique ; la majoration de durée d'assurance (vingt-quatre trimestres à la
  mère de trois enfants, seize à la mère du cas type 4) ; la durée requise et
  l'âge d'ouverture du droit commun, hors suspension ; la carrière longue, ses
  âges et ses durées (cas types 1, 2, 2 bis, 5 et 10) ; le taux plein ; le
  minimum contributif, à dix centimes par an près sur le régime général (le
  bas salaire de Destinie, le cas type 2 bis) ; les majorations de 10 % ; le taux de la
  majoration pour enfants de l'Arrco ; le RAFP d'une carrière à primes
  constantes ; le salaire annuel moyen du dépôt est celui de la Cnav, au
  millième près, sur chaque départ dont la Cnav publie la colonne.
* **Contre le dépôt** — la valeur de service de l'Agirc-Arrco : le dépôt
  servait celle du 31 décembre de l'année de la liquidation (`valeur_du_point`),
  la caisse et TRAJECTOiRE celle du jour : +0,6 % à un départ de février 2018,
  +5,1 % à un départ de janvier 2022, +4,9 % en octobre 2023, +1,6 % en 2024 ;
  corrigé le jour même (action 138, étape 20 : `valeurs_service_datees.csv`),
  les valeurs du point concordent. La bonification du cinquième des super-actifs et
  la majoration de durée des hospitaliers actifs, absentes (138.17) ; la première
  servie le 7 octobre 2026 (fiche bonification_cinquieme_police_penitentiaire),
  les durées du policier concordent, et sa pension s'écarte de celle de
  TRAJECTOiRE, qui borne la bonification (ci-dessous) ; la seconde le même jour
  (fiche majoration_duree_hospitaliers_actifs), au statut hospitalier qui naît
  avec elle, et le taux de l'aide-soignante concorde.
  L'arrondi des services de la fonction publique, tranché le 8 octobre 2026
  (action 138, étape 17 ; fiche decompte_des_services_fonction_publique) : le
  dépôt arrondissait année par année, le texte une fois, au décompte final
  (R. 26), et la durée d'assurance de la décote pas du tout (Conseil d'État,
  2 février 2010, n° 311495). Le cas type 6 de 1955 — dix mois en 1976, sept
  en 2017 — a 166 trimestres et aucune décote, au lieu de 165 et 1,25 % ; les
  requêtes portent depuis les fractions de trimestre de la fonction publique.
  La référence du minimum garanti, le même jour : 2020 revalorisé de 0,3 % au
  lieu de 1 %, les autres années projetées sur les prix ; elle suit depuis la
  chaîne des revalorisations, qui redonne les montants publiés au centime.
* **Contre TRAJECTOiRE** — ses services de la fonction publique en tiers de
  trimestre, sans l'arrondi de R. 26, et aucune décote pour une fraction de
  trimestre manquante, que L. 14 arrondit à l'entier supérieur. La référence
  de son minimum garanti, 2,3 % sous la chaîne légale de 2015 à 2023. Sa
  chaîne de coefficients du salaire annuel moyen
  (`revaloSam`), qui ne suit pas les colonnes de la Cnav : de −11 % sur les
  salaires de 1980 à +5,8 % sur ceux de 2016 ; le départ de janvier 2022 y
  compte la hausse de juillet 2022. Son script des cas types donne à chaque
  état d'une année partagée le revenu de l'année entière, que son moteur
  compte jusqu'à seize fois dans le même régime ; il multiplie l'AVPF par
  douze ; il range le chômage du cas type 3 hors de la durée du régime
  général (coefficient de proratisation de 0,86). Les âges et les durées des
  emplois super-actifs. Le traitement de référence revalorisé comme les
  pensions. Le plafond de 75 % que les bonifications ne lèvent pas. La
  bonification du cinquième du policier servie en majoration du taux, bornée à
  cinq points et proratisée (`majoreBonifFonc`), et non aux services. Le RAFP
  servi en rente sous 5 125 points. Ses paramètres projetés depuis 2024.
* **Une convention, à trancher** — les taux d'acquisition des points : le
  dépôt les minimaux, TRAJECTOiRE les moyens des entreprises, comme Destinie ;
  refaits, les points du dépôt sont ceux de TRAJECTOiRE aux taux minimaux, à
  0,1 % près.
* **Ouverts** — le RAFP des primes variables, que la requête ne sait pas dire
  année par année, et son coefficient de majoration, au mois au dépôt depuis
  la délibération de l'ERAFP, à l'âge entier chez TRAJECTOiRE.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path

import pytest

from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.saisie import Saisie
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "trajectoire.json"
SCRIPT = RACINE / "scripts" / "fetch" / "trajectoire.py"

#: Les régimes du dépôt de chaque caisse complémentaire de TRAJECTOiRE.
FAMILLES = {
    "Arrco": ("arrco", "arrco_tranche_2"),
    "Agirc": ("agirc", "agirc_tranche_c"),
    "Agirc-Arrco": ("agirc_arrco", "agirc_arrco_tranche_2"),
}
COMPLEMENTAIRES = {r for regimes in FAMILLES.values() for r in regimes}
VALEUR = re.compile(r"([\d,]+(?:\.\d+)?) points × valeur de service ([\d.]+) €")
SALAIRE_DE_REFERENCE = re.compile(r"SR ([\d,]+(?:\.\d+)?) €")
ANNEE_CNAV = re.compile(r"^(\d{4}) Cnav ([\d.]+) € ; trimestres [\d.]+ validés, "
                        r"([\d.]+) cotisés, [\d.]+ gratuits ; AVPF ([\d.]+) €")
#: Au-delà, les deux modèles projettent les paramètres, chacun à sa façon : les
#: montants ne se confrontent pas (la convention de projection n'est pas
#: tranchée), seuls les âges, les durées et les taux.
DERNIERE_ANNEE_DES_MONTANTS = 2026
#: Le nombre d'années du salaire annuel moyen des générations confrontées.
ANNEES_DU_SAM = 25


# ---------------------------------------------------------------------------
# Les mesures des deux côtés
# ---------------------------------------------------------------------------

def _nombre(texte: str) -> float:
    return float(texte.replace(",", ""))


def _mois(date: str) -> int:
    """Le rang du mois d'une date « AAAA-MM[-JJ] »."""
    return int(date[:4]) * 12 + int(date[5:7]) - 1


def _fonction_publique(regime: str) -> bool:
    return regime.startswith("fonction_publique") or regime == "cnracl"


def _famille(regime: str) -> str:
    if regime == "regime_general":
        return "regime_general"
    if _fonction_publique(regime):
        return "fonction_publique"
    if regime in COMPLEMENTAIRES:
        return "complementaires"
    return regime


def mesures_du_depot(contexte: Contexte, requete: dict) -> dict:
    """Ce que le scénario 1 sert à la requête du témoin : brut annuel, en euros
    de la liquidation, minimum compris et majoration pour enfants à part ; les
    points et leur valeur, lus dans le détail de chaque pension ; les salaires
    de référence."""
    actuel = contexte.simuler(Saisie.depuis_requete(requete)).actuel
    mesures: dict = {
        "trimestres": float(actuel.trimestres_valides),
        "trimestres_requis": float(actuel.trimestres_requis),
        "taux": actuel.taux_liquidation,
        "motif": actuel.motif_ouverture,
        "age_ouverture": actuel.age_ouverture_opposable,
        "montants": {}, "points": {}, "valeurs": {}, "majorations": {},
        "rafp_en_capital": False, "minimum": False,
    }
    for pension in actuel.pensions_par_regime:
        regime, famille = pension.regime, _famille(pension.regime)
        mesures["montants"][famille] = mesures["montants"].get(famille, 0.0) + pension.montant
        if (reference := SALAIRE_DE_REFERENCE.search(pension.detail)):
            cle = ("salaire_annuel_moyen" if famille == "regime_general"
                   else "traitement_de_reference")
            mesures[cle] = _nombre(reference.group(1))
        if (trouve := VALEUR.search(pension.detail)):
            mesures["points"][regime] = _nombre(trouve.group(1))
            mesures["valeurs"][regime] = float(trouve.group(2))
        if regime == "rafp":
            mesures["rafp_en_capital"] = pension.capital is not None
    for avantage in actuel.avantages_appliques:
        if avantage.code == "majoration_enfants":
            for regime, part in avantage.par_regime:
                famille = _famille(regime)
                mesures["majorations"][famille] = mesures["majorations"].get(famille, 0.0) + part
        elif avantage.code in ("minimum_contributif", "minimum_garanti"):
            mesures["minimum"] = True
    return mesures


#: Les caisses de TRAJECTOiRE, rangées dans les familles du dépôt.
CAISSES = {"Cnav": "regime_general", "SRE": "fonction_publique",
           "CNRACL": "fonction_publique", "Rafp": "rafp", "Arrco": "complementaires",
           "Agirc": "complementaires", "Agirc-Arrco": "complementaires"}


def mesures_de_trajectoire(cas: dict) -> dict:
    """Les mêmes quantités, lues dans les sorties figées : pensions annuelles
    (TRAJECTOiRE les écrit mensuelles), minimum compris, majoration pour
    enfants à part, comme le dépôt les range.

    Le départ anticipé pour carrière longue : TRAJECTOiRE date la première
    liquidation qu'elle ouvre (`dtIdRacl`) ; le départ en relève quand il tombe
    à cette date ou après, et avant l'âge d'ouverture."""
    sortie = cas["trajectoire"]
    liquidation, caisses, bases = sortie["liquidation"], sortie["caisses"], sortie["bases"]
    principale = caisses.get(liquidation["caisse_principale"], {})
    taux_plein = 0.75 if liquidation["caisse_principale"] in ("SRE", "CNRACL") else 0.5
    depart = _mois(liquidation["date"])
    ouverture = _mois(cas["requete"]["naissance"]) + round(12 * float(liquidation["AOD"]))
    racl = liquidation["carriere_longue"]
    mesures: dict = {
        "trimestres": float(liquidation["duree_validee_tous_regimes"]),
        "trimestres_requis": float(liquidation["duree_requise"]),
        "AOD": float(liquidation["AOD"]),
        "carriere_longue": racl is not None and _mois(racl) <= depart < ouverture,
        "taux": (taux_plein * (1 - (principale.get("decote") or 0) / 100)
                 * (1 + (principale.get("surcote") or 0) / 100)),
        "montants": {}, "points": {}, "valeurs": {}, "majorations": {},
        "minimum": bool(liquidation["minimum"]),
    }
    for caisse, valeurs in caisses.items():
        famille = CAISSES[caisse]
        hors_majoration = 12 * (valeurs["pension_mensuelle"] - valeurs["majoration_enfants"])
        mesures["montants"][famille] = mesures["montants"].get(famille, 0.0) + hors_majoration
        if valeurs["majoration_enfants"]:
            mesures["majorations"][famille] = (mesures["majorations"].get(famille, 0.0)
                                               + 12 * valeurs["majoration_enfants"])
        if caisse in sortie["points"] and sortie["points"][caisse]:
            mesures["points"][caisse] = sortie["points"][caisse]
            mesures["valeurs"][caisse] = hors_majoration / sortie["points"][caisse]
    for caisse, base in bases.items():
        if base.get("salaire_reference"):
            cle = "salaire_annuel_moyen" if caisse == "Cnav" else "traitement_de_reference"
            mesures[cle] = base["salaire_reference"]
    return mesures


def _relatif(depot: float, trajectoire: float) -> float:
    if trajectoire == 0:
        return 0.0 if depot == 0 else float("inf")
    return (depot - trajectoire) / trajectoire


def _points_comparables(depot: dict, traj: dict) -> list[tuple[str, float, float, float, float]]:
    """(famille, points et valeur de service du dépôt, de TRAJECTOiRE). Avant
    2019, l'Arrco et l'Agirc à part ; depuis, TRAJECTOiRE convertit les points de
    l'Agirc en points Agirc-Arrco, quand le dépôt garde les siens à leur valeur
    convertie : ils se comptent au prorata des deux valeurs de service."""
    points, valeurs = depot["points"], depot["valeurs"]
    if "Agirc-Arrco" in traj["points"]:
        unifies = FAMILLES["Arrco"] + FAMILLES["Agirc-Arrco"]
        valeur = next((valeurs[r] for r in unifies if r in valeurs), 0.0)
        total = sum(points.get(r, 0.0) for r in unifies)
        total += sum(points[r] * valeurs[r] / valeur
                     for r in FAMILLES["Agirc"] if r in points and valeur)
        return [("agirc_arrco", total, valeur, traj["points"]["Agirc-Arrco"],
                 traj["valeurs"]["Agirc-Arrco"])]
    comparables = []
    for caisse in ("Arrco", "Agirc"):
        if caisse in traj["points"]:
            regimes = FAMILLES[caisse]
            valeur = next((valeurs[r] for r in regimes if r in valeurs), 0.0)
            comparables.append((caisse.lower(), sum(points.get(r, 0.0) for r in regimes),
                                valeur, traj["points"][caisse], traj["valeurs"][caisse]))
    return comparables


def ecarts_du_cas(depot: dict, traj: dict, montants: bool) -> dict[str, float]:
    """Chaque quantité confrontée et son écart : en trimestres pour les durées,
    en années pour l'âge, en points de taux pour la majoration de l'Agirc-Arrco,
    relatif pour le reste ; « carriere_longue » vaut 1 si le dépôt seul ouvre au
    titre de la carrière longue, −1 si TRAJECTOiRE seul ; « minimum » et
    « rafp_en_capital », de même."""
    ecarts = {
        "trimestres": depot["trimestres"] - traj["trimestres"],
        "trimestres_requis": depot["trimestres_requis"] - traj["trimestres_requis"],
        "taux": _relatif(depot["taux"], traj["taux"]),
        "carriere_longue": float((depot["motif"] == "carriere_longue")
                                 - traj["carriere_longue"]),
    }
    if not traj["carriere_longue"] and depot["motif"] != "carriere_longue":
        ecarts["age_ouverture"] = (depot["age_ouverture"] or 0.0) - traj["AOD"]
    if not montants:
        return ecarts
    for famille in ("regime_general", "fonction_publique", "rafp"):
        if depot["montants"].get(famille) or traj["montants"].get(famille):
            ecarts[famille] = _relatif(depot["montants"].get(famille, 0.0),
                                       traj["montants"].get(famille, 0.0))
    for quantite in ("salaire_annuel_moyen", "traitement_de_reference"):
        if quantite in depot and quantite in traj:
            ecarts[quantite] = _relatif(depot[quantite], traj[quantite])
    for famille, points, valeur, points_traj, valeur_traj in _points_comparables(depot, traj):
        ecarts[f"points_{famille}"] = _relatif(points, points_traj)
        ecarts[f"valeur_point_{famille}"] = _relatif(valeur, valeur_traj)
    if "Rafp" in traj["points"]:
        ecarts["points_rafp"] = _relatif(depot["points"].get("rafp", 0.0), traj["points"]["Rafp"])
        ecarts["rafp_en_capital"] = float(depot["rafp_en_capital"])
    for famille in sorted(set(depot["majorations"]) | set(traj["majorations"])):
        if famille == "complementaires":
            # La majoration de l'Agirc-Arrco suit les points, que la convention
            # des taux sépare : on en compare le taux, rapporté à la retraite.
            ecarts["majoration_complementaires"] = (
                depot["majorations"].get(famille, 0.0) / depot["montants"][famille]
                - traj["majorations"].get(famille, 0.0) / traj["montants"][famille])
        else:
            ecarts[f"majoration_{famille}"] = _relatif(depot["majorations"].get(famille, 0.0),
                                                       traj["majorations"].get(famille, 0.0))
    ecarts["minimum"] = float(depot["minimum"]) - float(traj["minimum"])
    return ecarts


def montants_confrontes(cas: dict) -> bool:
    """Les montants d'un départ que les deux modèles calculent sur des valeurs
    connues (ou que l'un projette et l'autre pas : écart déclaré)."""
    return int(cas["trajectoire"]["liquidation"]["date"][:4]) <= DERNIERE_ANNEE_DES_MONTANTS


# ---------------------------------------------------------------------------
# Les tolérances et les écarts déclarés
# ---------------------------------------------------------------------------

#: La tolérance de chaque quantité : en trimestres, en années, relative.
#: Les trimestres : un tiers, la fraction de trimestre que TRAJECTOiRE garde
#: des mois de services de la fonction publique, quand la durée tous régimes du
#: dépôt n'en garde que d'entiers — seules la liquidation et la décote des
#: régimes du code des pensions les lisent au jour. Les montants : 0,5 %, comme
#: la confrontation à Destinie.
TOLERANCES = {
    "trimestres": 0.34, "trimestres_requis": 0.0, "taux": 1e-9, "carriere_longue": 0.0,
    "age_ouverture": 1e-9, "regime_general": 0.005, "salaire_annuel_moyen": 0.005,
    "fonction_publique": 0.005, "traitement_de_reference": 0.005, "rafp": 0.005,
    "points_rafp": 0.005, "rafp_en_capital": 0.0, "valeur_point_arrco": 0.001,
    "valeur_point_agirc": 0.001, "valeur_point_agirc_arrco": 0.001,
    "majoration_regime_general": 0.005, "majoration_fonction_publique": 0.005,
    # Deux dixièmes de point de taux de majoration.
    "majoration_complementaires": 0.002, "minimum": 0.0,
}

#: La convention des taux d'acquisition des points : TRAJECTOiRE les taux
#: contractuels MOYENS des entreprises (`paramCotis`, txCotARRCOsalempl_t1 :
#: 5,42 % de 1962 à 1993, 6,61 % depuis 2016 ; txCotAGIRCsalempl_TB : 13,9 % vers
#: 1980), le dépôt les taux MINIMAUX de l'accord, que TRAJECTOiRE porte aussi
#: (txCotMIN… : 4 %, 6 %, 6,2 % ; 8 % puis 16 %). Le même choix que Destinie :
#: une convention de cas type, que le propriétaire tranchera (registre, 138.13).
#: Refaite, elle explique tout l'écart (`test_les_points_du_depot_sont_ceux_de_
#: trajectoire_aux_taux_minimaux`). Le chômage du cas type 3 y ajoute ses
#: points, que le dépôt sert et TRAJECTOiRE non.
TAUX_CONTRACTUELS = ("TRAJECTOiRE acquiert les points aux taux contractuels moyens des "
                     "entreprises, le dépôt aux taux minimaux de l'accord")
ECARTS_DES_POINTS = {
    "arrco": (-0.27, -0.02),
    "agirc": (-0.21, -0.11),
    "agirc_arrco": (-0.30, 0.03),
}

LOI_2025 = (
    "la loi du 30 décembre 2025 suspend la réforme de 2023, que TRAJECTOiRE n'a pas : "
    "la génération 1964 ouvre ses droits à 62 ans et 9 mois avec 170 trimestres "
    "(age_ouverture_requis.csv, duree_assurance_requise.csv), quand TRAJECTOiRE lui "
    "demande 63 ans et 171 ; l'emploi actif né en janvier 1970, à 57 ans et 9 mois avec "
    "170 trimestres (categorie_active.csv), quand il lui demande 58 ans et 3 mois et "
    "172 ; à son âge du taux plein, le dépôt compte déjà un trimestre de surcote ; "
    "l'écart est celui de la version publique (registre)")
SUPER_ACTIFS = (
    "les emplois super-actifs : le dépôt relève leur âge d'ouverture de 50 à 52 ans pour "
    "les générations du second semestre 1961 à 1965, comme le décret le fait "
    "(categorie_active.csv, fiche categorie_active_super_active) ; TRAJECTOiRE ouvre "
    "encore à 50 ans les générations 1963 et 1964, et à 51 ans et 3 mois la génération "
    "1970, avec un âge d'annulation de la décote plus bas ; l'écart est le sien")
DUREE_ACTIFS = (
    "la durée requise des emplois classés nés avant septembre 1966 : celle des "
    "fonctionnaires qui atteignent soixante ans l'année où leur droit s'ouvre (fiche "
    "categorie_active_duree_requise, conforme ; L. 13, III, version de 2014), soit 154 "
    "trimestres au super-actif né en 1955 ; TRAJECTOiRE lui en demande 162 ; l'écart "
    "est le sien")
BONIFICATION_CINQUIEME = (
    "la bonification du cinquième du policier du cas type 8 : vingt trimestres des deux "
    "côtés, mais TRAJECTOiRE la sert en majoration du taux, bornée à cinq points et "
    "multipliée par le coefficient de proratisation (`majoreBonifFonc`), soit 132/166 de "
    "80 % au policier né en 1960, quand la loi la fait entrer « pour la liquidation de "
    "ladite pension » (loi n° 57-444, article 1er) : 152/162 de 75 % au dépôt, sous le "
    "maximum de 75 % (fiche bonification_cinquieme_police_penitentiaire) ; l'écart est "
    "le sien. TRAJECTOiRE porte aussi l'ISS dans l'assiette, que le dépôt n'a pas")
MAJORATION_HOSPITALIERS = (
    "la majoration de durée d'assurance de l'hospitalier de catégorie active (loi "
    "n° 2003-775, art. 78) : quinze trimestres à l'aide-soignante du cas type 9, des deux "
    "côtés, et le taux concorde ; mais le dépôt ne la compte que dans la durée que la "
    "CNRACL oppose à sa décote, « pour l'application des dispositions du I de l'article "
    "L. 14 » (fiche majoration_duree_hospitaliers_actifs), TRAJECTOiRE dans la durée tous "
    "régimes")
ANNEE_PARTAGEE = (
    "l'année partagée entre deux états : le script des cas types de TRAJECTOiRE donne à "
    "chacun le revenu de l'année entière, et son moteur compte une année partagée dans le "
    "même régime jusqu'à seize fois (`passageFormatIdAnCaisse`) ; une année partagée "
    "entre le privé et la fonction publique y valide quatre trimestres au régime général, "
    "pour un mois de privé (cas type 10), quatre et un au chômage (cas type 3), au-delà "
    "des quatre que R. 351-5 permet (fiche un_statut_par_annee) ; le relevé du dépôt n'en "
    "porte qu'une ligne, et l'année d'un mois de privé qui ouvre la carrière du cas type "
    "10, sans trimestre au dépôt, sort de son salaire annuel moyen depuis 2004 (R. 351-29, "
    "fiche salaire_annuel_moyen), quand TRAJECTOiRE l'y garde")
AVPF_PAR_DOUZE = (
    "l'AVPF du cas type 4 : le script des cas types de TRAJECTOiRE la vaut douze fois "
    "l'assiette annuelle (`montantAvpf = dureeEnMois * smicAVPF`, smicAVPF étant déjà "
    "annuel), que le plafond borne : ses années d'AVPF entrent au salaire annuel moyen "
    "au plafond ; le dépôt la vaut au barème de la Cnav, 169 heures par mois au SMIC du "
    "1er juillet précédent (R. 381-3, fiche avpf) ; l'écart est le sien")
CHOMAGE_HORS_PRORATA = (
    "le chômage du cas type 3 : TRAJECTOiRE range ses trimestres dans une caisse « "
    "Chômage » qui n'entre pas dans la durée du régime général, dont le coefficient de "
    "proratisation tombe à 0,86 (144 trimestres sur 167 en 2022) ; ce sont des périodes "
    "d'assurance du régime général (R. 351-12, fiches chomage_non_indemnise et "
    "taux_plein_et_proratisation) ; l'écart est le sien")
CHAINE_SAM = (
    "la chaîne des coefficients du salaire annuel moyen : TRAJECTOiRE enchaîne sa série "
    "annuelle revaloSam jusqu'à l'année de la liquidation comprise (`calculeSam`), qui ne "
    "suit pas les colonnes de la Cnav que le dépôt sert — de −11 % sur un salaire de 1980 "
    "à +5,8 % sur un salaire de 2016, et 4,75 % sur 2022, hausse de juillet comprise, pour "
    "un départ de janvier 2022 ; refaite, elle explique l'écart au millième "
    "(`test_l_ecart_du_salaire_annuel_moyen_est_celui_des_coefficients`) ; l'écart est "
    "le sien")
TRAITEMENT = (
    "le traitement de référence : TRAJECTOiRE prend le traitement de la dernière année "
    "complète, revalorisé jusqu'au départ comme les PENSIONS de la caisse "
    "(`calculeSalaireReferenceFonc`, table revalo : +1,1 % au 1er janvier 2022, +5,3 % au "
    "1er janvier 2024) ; le dépôt, celui de l'année du départ, ou de la dernière année "
    "travaillée ; l'écart suit la hausse de l'année")
VALEURS_PROJETEES = (
    "les paramètres de TRAJECTOiRE sont projetés au-delà de 2023-2024, sur les hypothèses "
    "du COR du programme de stabilité de 2024 (registre) : la valeur de service de "
    "l'Agirc-Arrco de 1,44377 € en novembre 2024 et 1,46658 € en novembre 2025, quand "
    "la fédération l'a fixée à 1,4386 € ; la valeur du point du RAFP de 2024")
PRORATA_80 = (
    "le plafond de la pension civile : TRAJECTOiRE borne la proratisation à 1 même avec la "
    "bonification pour enfants, quand L. 12 porte le pourcentage maximum de cinq points "
    "« du chef des bonifications » (fiche taux_maximum_fonction_publique, conforme) : la "
    "mère de deux enfants a 168/166 au dépôt et chez Destinie, 166/166 chez TRAJECTOiRE ; "
    "l'écart est le sien")
ARRONDI_SERVICES = (
    "les services de la fonction publique : TRAJECTOiRE les garde en tiers de trimestre, "
    "proratise sur eux (171,33/172) et ne fait aucune décote pour une fraction de trimestre "
    "manquante ; le texte arrondit le décompte final des trimestres liquidables, la fraction "
    "de quarante-cinq jours faisant le trimestre (R. 26 ; décret n° 2003-1306, article 16), "
    "et les trimestres manquants à l'entier supérieur (L. 14, I), la décote écartée quand "
    "l'arrondi atteint le pourcentage maximum (Conseil d'État, 2 février 2010, n° 311495 ; "
    "fiche decompte_des_services_fonction_publique) : un mois de trop peu fait une décote, "
    "deux mois de plus un trimestre ; l'écart est le sien")
MINIMUM_GARANTI = (
    "le minimum garanti du cas type 10 : la référence de TRAJECTOiRE, l'indice majoré 227 "
    "revalorisé, est de 2,28 % sous celle que la chaîne des revalorisations des pensions "
    "civiles donne (L. 17 et L. 16), que les montants publiés confirment au centime — "
    "1 130,50 € par mois en février 2015 au lieu de 1 156,90 €, 1 229,59 € en octobre 2023 "
    "au lieu de 1 258,32 € ; en 2025, sa revalorisation projetée de 2,6 % au lieu de 2,2 % "
    "ramène l'écart à 1,90 % ; en 2020, son minimum (1 037,58 €) tombe sous la pension "
    "qu'elle calcule, et elle ne le sert pas, quand celui du dépôt, 1 064,28 €, la relève ; "
    "l'écart est le sien")
RAFP_PRIMES = (
    "le RAFP des primes variables : la requête ne dit qu'une part de primes pour toute la "
    "carrière, celle de la dernière année, quand TRAJECTOiRE suit les primes de chaque "
    "année depuis 2005 ; s'y ajoutent, selon les cas, le capital que le dépôt verse sous "
    "5 125 points, la valeur projetée du point et le coefficient de majoration par âge")
RAFP_COEFFICIENT = (
    "le coefficient de majoration du RAFP : au mois au dépôt, entre deux âges entiers du "
    "barème de la date d'effet (délibération de l'ERAFP, fiche rafp_majoration_capital), "
    "à l'âge entier chez TRAJECTOiRE (surcoteRafp)")
RAFP_CAPITAL = (
    "le RAFP sous 5 125 points se verse en capital (décret n° 2004-569, art. 9, fiche "
    "rafp_majoration_capital) : le dépôt le verse, TRAJECTOiRE sert une rente ; l'écart "
    "est le sien")


def _ecarts(cause: str, quantite: str, observes: dict[str, float],
            marge: float) -> dict[tuple[str, str], tuple[float, float, str]]:
    return {(code, quantite): (valeur - marge, valeur + marge, cause)
            for code, valeur in observes.items()}


#: Les écarts déclarés : (cas, quantité) → (bas, haut, cause), autour de la
#: valeur que la première exécution a mesurée.
ECARTS: dict[tuple[str, str], tuple[float, float, str]] = {}
_A_1964 = ("cor_1_1964", "cor_3_1964", "cor_4_1964", "cor_5_1964",
           "cor_5_primes_constantes_1964", "cor_6_1964", "cor_7_1964", "cor_11_1964")
ECARTS.update(_ecarts(LOI_2025, "age_ouverture", {c: -0.25 for c in _A_1964}, 1e-6))
ECARTS.update(_ecarts(LOI_2025, "age_ouverture", {"cor_9_1970": -0.5}, 1e-6))
ECARTS.update(_ecarts(LOI_2025, "trimestres_requis", {c: -1.0 for c in _A_1964}, 1e-6))
ECARTS.update(_ecarts(LOI_2025, "trimestres_requis", {"cor_9_1970": -2.0}, 1e-6))
ECARTS.update(_ecarts(LOI_2025, "taux", {c: 0.0125 for c in (
    "cor_5_1964", "cor_5_primes_constantes_1964", "cor_6_1964", "cor_11_1964")}, 1e-6))
ECARTS.update(_ecarts(SUPER_ACTIFS, "age_ouverture",
                      {"cor_8_1963": 1.17, "cor_8_1964": 1.58, "cor_8_1970": 0.75}, 1e-6))
ECARTS.update(_ecarts(SUPER_ACTIFS, "taux", {"cor_8_1960": -0.0125}, 1e-6))
ECARTS.update(_ecarts(DUREE_ACTIFS, "trimestres_requis", {
    "cor_8_1955": -8.0, "cor_8_1960": -4.0, "cor_8_1963": -2.0, "cor_8_1964": -1.0,
    "cor_8_1970": -1.0, "cor_9_1964": 1.0}, 1e-6))
ECARTS.update(_ecarts(BONIFICATION_CINQUIEME, "fonction_publique", {
    "cor_8_1955": 0.1212, "cor_8_1960": 0.0711, "cor_8_1963": 0.1077,
    "cor_8_1964": 0.0999}, 0.002))
ECARTS.update(_ecarts(MAJORATION_HOSPITALIERS, "trimestres", {
    "cor_9_1955": -15.0, "cor_9_1960": -14.67, "cor_9_1963": -15.0, "cor_9_1964": -15.33,
    "cor_9_1970": -15.0}, 0.01))
ECARTS.update(_ecarts(DUREE_ACTIFS + " ; et " + ARRONDI_SERVICES, "taux",
                      {"cor_9_1964": -0.025}, 1e-6))
ECARTS.update(_ecarts(DUREE_ACTIFS + " ; " + ARRONDI_SERVICES + " ; et " + TRAITEMENT,
                      "fonction_publique", {"cor_9_1964": -0.0368}, 0.002))
ECARTS.update(_ecarts(ARRONDI_SERVICES + " ; et " + TRAITEMENT, "fonction_publique",
                      {"cor_9_1960": 0.0082}, 0.002))
ECARTS.update(_ecarts(ANNEE_PARTAGEE, "trimestres", {"cor_10_1970": -2.0, "cor_3_1964": -1.0},
                      1e-6))
ECARTS.update(_ecarts(ANNEE_PARTAGEE, "carriere_longue", {"cor_10_1970": -1.0}, 1e-6))
ECARTS.update(_ecarts(ANNEE_PARTAGEE, "taux", {"cor_10_1970": -0.025}, 1e-6))
ECARTS.update(_ecarts(ANNEE_PARTAGEE + " ; et " + CHAINE_SAM, "regime_general", {
    "cor_10_1955": 0.0923, "cor_10_1960": -0.0429, "cor_10_1963": -0.0242,
    "cor_10_1964": -0.0323}, 0.002))
ECARTS.update(_ecarts(ANNEE_PARTAGEE + " ; et " + CHAINE_SAM, "salaire_annuel_moyen", {
    "cor_10_1955": 0.0923, "cor_10_1960": 0.0254, "cor_10_1963": -0.0242,
    "cor_10_1964": -0.0323}, 0.002))
ECARTS.update(_ecarts(AVPF_PAR_DOUZE + " ; et " + CHAINE_SAM, "regime_general", {
    "cor_4_1955": -0.0618, "cor_4_1960": -0.0967, "cor_4_1963": -0.1091}, 0.002))
ECARTS.update(_ecarts(AVPF_PAR_DOUZE + " ; et " + CHAINE_SAM, "salaire_annuel_moyen", {
    "cor_4_1955": -0.0618, "cor_4_1960": -0.0967, "cor_4_1963": -0.1091}, 0.002))
ECARTS.update(_ecarts(CHOMAGE_HORS_PRORATA + " ; et " + CHAINE_SAM, "regime_general", {
    "cor_3_1955": 0.0950, "cor_3_1960": 0.1215, "cor_3_1963": 0.0999}, 0.002))
_CHAINE = {
    "cor_1_1955": 0.0134, "cor_1_1960": -0.0339, "cor_1_1963": -0.0389,
    "cor_2_1955": 0.0134, "cor_2_1960": 0.0093, "cor_2_1963": -0.0362, "cor_2_1964": -0.0449,
    "loi_2023_salaire_moyen": -0.0362, "rg_ne_en_octobre": -0.0362,
}
ECARTS.update(_ecarts(CHAINE_SAM, "regime_general", {
    **_CHAINE, "cor_2bis_1960": 0.0093, "cor_2bis_1964": -0.0103}, 0.002))
ECARTS.update(_ecarts(CHAINE_SAM, "salaire_annuel_moyen", {
    **_CHAINE, "cor_2bis_1955": 0.0134, "cor_2bis_1960": 0.0093, "cor_2bis_1963": -0.0362,
    "cor_2bis_1964": -0.0450, "cor_3_1955": 0.0093, "cor_3_1960": -0.0329,
    "cor_3_1963": -0.0424}, 0.002))
_TRAITEMENTS = {
    "cor_5_1955": 0.0061, "cor_5_1960": -0.0109, "cor_5_1963": -0.0168,
    "cor_5_primes_constantes_1955": 0.0061, "cor_5_primes_constantes_1960": -0.0109,
    "cor_5_primes_constantes_1963": -0.0168, "cor_6_1955": 0.0158, "cor_6_1960": -0.0053,
    "cor_7_1955": 0.0062, "cor_11_1955": 0.0291, "cor_11_1960": -0.0109,
    "loi_2023_fp_etat": -0.0253,
}
ECARTS.update(_ecarts(TRAITEMENT, "traitement_de_reference", {
    **_TRAITEMENTS, "cor_8_1955": -0.0058, "cor_8_1960": -0.0195, "cor_8_1963": 0.0224,
    "cor_8_1964": 0.0255, "cor_9_1955": -0.0104, "cor_9_1960": 0.0060, "cor_9_1963": -0.0100,
    "cor_10_1955": 0.0194, "cor_10_1960": -0.0099, "cor_10_1964": -0.0069}, 0.001))
ECARTS.update(_ecarts(TRAITEMENT, "fonction_publique", {
    k: v for k, v in _TRAITEMENTS.items() if k not in ("cor_6_1955",)} | {
    "cor_5_1963": -0.0149, "cor_5_primes_constantes_1963": -0.0149,
    "cor_6_1960": -0.0053, "cor_9_1955": -0.0104, "cor_9_1963": -0.0100}, 0.002))
ECARTS.update(_ecarts(ARRONDI_SERVICES, "taux", {c: -0.0125 for c in (
    "cor_5_1970", "cor_5_primes_constantes_1970", "cor_7_1970", "cor_11_1970")}, 1e-6))
ECARTS.update(_ecarts(ARRONDI_SERVICES + " ; et " + TRAITEMENT, "fonction_publique",
                      {"cor_6_1955": 0.0199}, 0.002))
ECARTS.update(_ecarts(MINIMUM_GARANTI + " ; et " + ANNEE_PARTAGEE, "fonction_publique", {
    "cor_10_1955": 0.0210, "cor_10_1963": 0.0139, "cor_10_1964": 0.0148}, 0.002))
ECARTS.update(_ecarts(MINIMUM_GARANTI + " ; et " + TRAITEMENT, "fonction_publique",
                      {"cor_10_1960": 0.0124}, 0.002))
ECARTS.update(_ecarts(MINIMUM_GARANTI, "minimum", {"cor_10_1960": 1.0}, 1e-6))
ECARTS.update(_ecarts(PRORATA_80, "fonction_publique", {"fp_mere_deux_enfants": 0.0100},
                      0.002))
ECARTS.update(_ecarts(RAFP_CAPITAL, "rafp_en_capital", {c: 1.0 for c in (
    "cor_8_1955", "cor_8_1960", "cor_9_1955", "cor_9_1960", "cor_10_1955")}, 1e-6))
_RAFP_POINTS = {
    "cor_5_1955": -0.0710, "cor_5_1960": 0.0130, "cor_5_1963": -0.0276,
    "cor_5_primes_constantes_1955": -0.0710, "cor_5_primes_constantes_1960": 0.0130,
    "cor_5_primes_constantes_1963": -0.0276, "cor_6_1955": -0.0190, "cor_6_1960": -0.1350,
    "cor_7_1955": -0.0065, "cor_8_1955": -0.3373, "cor_8_1960": -0.1447, "cor_8_1963": -0.0140,
    "cor_8_1964": -0.0127, "cor_9_1955": -0.1749, "cor_9_1960": -0.0612, "cor_9_1963": -0.0316,
    "cor_9_1964": -0.0265, "cor_10_1955": -0.0799, "cor_10_1960": -0.0673,
    "cor_10_1963": 0.0083, "cor_11_1955": 0.0185, "cor_11_1960": 0.0423, "cor_11_1963": 0.0145,
}
ECARTS.update(_ecarts(RAFP_PRIMES, "points_rafp", _RAFP_POINTS, 0.001))
ECARTS.update(_ecarts(RAFP_PRIMES + " ; " + RAFP_COEFFICIENT, "rafp", {
    "cor_5_1955": -0.0806, "cor_5_1960": -0.0179, "cor_5_1963": 0.0539,
    "cor_5_primes_constantes_1955": -0.0806, "cor_5_primes_constantes_1960": -0.0179,
    "cor_5_primes_constantes_1963": 0.0539, "cor_6_1960": -0.1035, "cor_7_1960": 0.0314,
    "cor_8_1955": -0.4065, "cor_8_1960": -0.2700, "cor_8_1963": -0.1117, "cor_8_1964": -0.1175,
    "cor_9_1955": -0.2279, "cor_9_1960": -0.1775, "cor_9_1963": -0.0972, "cor_9_1964": -0.1112,
    "cor_10_1955": -0.0909, "cor_10_1960": -0.1545, "cor_10_1963": 0.0543,
    "cor_10_1964": 0.0329, "cor_11_1955": 0.0219, "cor_11_1960": 0.0106,
    "cor_11_1963": 0.0923}, 0.002))
ECARTS.update(_ecarts(VALEURS_PROJETEES + " (0,05215 € au lieu de 0,05378 €) ; "
                      + RAFP_COEFFICIENT + " ; les points du RAFP concordent", "rafp",
                      {"loi_2023_fp_etat": 0.0511}, 0.002))
ECARTS.update(_ecarts(VALEURS_PROJETEES, "valeur_point_agirc_arrco", {
    "cor_1_1963": -0.0036, "cor_3_1963": -0.0036, "cor_4_1963": -0.0036,
    "cor_10_1964": -0.0036, "cor_2_1964": -0.0191, "cor_2bis_1964": -0.0191}, 0.0003))


# ---------------------------------------------------------------------------
# Les fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def temoin() -> dict:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


@pytest.fixture(scope="module")
def mesures(temoin, contexte) -> dict[str, tuple[dict, dict]]:
    return {code: (mesures_du_depot(contexte, cas["requete"]), mesures_de_trajectoire(cas))
            for code, cas in temoin["cas"].items()}


@pytest.fixture(scope="module")
def ecarts(temoin, mesures) -> dict[str, dict[str, float]]:
    return {code: ecarts_du_cas(*mesures[code], montants_confrontes(temoin["cas"][code]))
            for code in temoin["cas"]}


def _parametres(temoin) -> dict[int, dict[str, float]]:
    """Les paramètres annuels de TRAJECTOiRE que le témoin recopie."""
    parametres = {}
    for ligne in temoin["parametres_trajectoire"]["annuels"]:
        annee, *champs = ligne.split()
        parametres[int(annee)] = {c.split("=")[0]: float(c.split("=")[1]) for c in champs}
    return parametres


def _annees_cnav(cas: dict) -> list[tuple[int, float, float, float]]:
    """(année, revenu, trimestres cotisés, AVPF) que TRAJECTOiRE a portés au
    compte du régime général."""
    annees = []
    for ligne in cas["trajectoire"]["annees"]:
        if (trouve := ANNEE_CNAV.match(ligne)):
            annees.append((int(trouve.group(1)), float(trouve.group(2)),
                           float(trouve.group(3)), float(trouve.group(4))))
    return annees


def _sam(annees, annee_liquidation: int, plafond, coefficient) -> float:
    """Le salaire annuel moyen de `calculeSam` : les années cotisées avant celle
    de la liquidation, AVPF comprise, au plafond de chacune, revalorisées, les
    vingt-cinq meilleures."""
    valeurs = sorted((min(revenu + avpf, plafond(annee)) * coefficient(annee)
                      for annee, revenu, cotises, avpf in annees
                      if annee < annee_liquidation and cotises > 0), reverse=True)
    retenues = valeurs[:ANNEES_DU_SAM]
    return sum(retenues) / len(retenues)


# ---------------------------------------------------------------------------
# Le témoin
# ---------------------------------------------------------------------------

def test_le_temoin_dit_son_origine_sa_licence_et_sa_legislation(temoin):
    """Des sorties d'un code sous EUPL n'entrent au dépôt qu'avec leur origine et
    leur licence (docs/architecture.md, § 3.4) ; une législation sans sa date ne
    dirait pas ce qu'on confronte."""
    assert temoin["code"] == "https://git.drees.fr/drees_code_public/modeles/trajectoire"
    assert re.fullmatch(r"[0-9a-f]{40}", temoin["commit"])
    assert temoin["licence"] == "EUPL-1.2"
    assert "n'entre pas au dépôt" in temoin["origine"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", temoin["execute_le"])
    assert "14 avril 2023" in temoin["legislation"]["dit"]
    assert "30 décembre 2025" in temoin["legislation"]["dit"]
    assert temoin["environnement"]["trajectoire"] in temoin["version"]


def test_la_legislation_de_trajectoire_est_celle_de_2023(temoin):
    """Ce que le registre lisait dans le code (`ageDuree.csv`), l'exécution le
    confirme : la génération 1964 à 63 ans et 171 trimestres, sans la
    suspension ; 64 ans et 172 trimestres à partir de 1968 et 1965."""
    age_duree = temoin["legislation"]["age_duree_droit_commun"]
    assert "1964-01 63" in age_duree["AOD"] and "1968-01 64" in age_duree["AOD"]
    assert "1964-01 171" in age_duree["Duree"] and "1965-01 172" in age_duree["Duree"]


def test_les_scripts_appellent_trajectoire_sans_le_recopier():
    """Le script R du dépôt charge le paquet installé à part et n'appelle que ses
    fonctions et le script qu'il livre : aucune ligne de TRAJECTOiRE, dont chaque
    fichier porte l'en-tête de la DREES, n'y entre."""
    for chemin in (SCRIPT, SCRIPT.with_suffix(".R")):
        texte = chemin.read_text(encoding="utf-8")
        assert "Logiciel elabore par l'État, via la Drees" not in texte, chemin.name
    texte_r = SCRIPT.with_suffix(".R").read_text(encoding="utf-8")
    assert "library(trajectoire)" in texte_r
    assert 'system.file("scripts", "casTypesCOR.R", package = "trajectoire"' in texte_r


def test_chaque_cas_liquide_a_la_date_de_sa_requete(temoin):
    """Les deux modèles partent le même mois."""
    for code, cas in temoin["cas"].items():
        assert cas["trajectoire"]["liquidation"]["date"] == cas["requete"]["liquidation"], code


# ---------------------------------------------------------------------------
# Les mécanismes, refaits
# ---------------------------------------------------------------------------

def test_le_salaire_annuel_moyen_de_trajectoire_se_refait_sur_ses_parametres(temoin):
    """`calculeSam`, refait sur les années que TRAJECTOiRE a portées au compte et
    sur ses propres paramètres (revaloSam, le plafond) : le témoin dit tout ce
    qui fait son salaire annuel moyen."""
    parametres = _parametres(temoin)

    def chaine(annee, liquidation):
        produit = 1.0
        for k in range(annee + 1, liquidation + 1):
            produit *= 1 + parametres[k]["revaloSam"] / 100
        return produit

    refaits = 0
    for code, cas in temoin["cas"].items():
        base = cas["trajectoire"]["bases"].get("Cnav")
        if not base or not base.get("salaire_reference"):
            continue
        liquidation = int(cas["trajectoire"]["liquidation"]["date"][:4])
        refait = _sam(_annees_cnav(cas), liquidation, lambda a: parametres[a]["pss"],
                      lambda a: chaine(a, liquidation))
        assert refait == pytest.approx(base["salaire_reference"], rel=1e-6), code
        refaits += 1
    assert refaits >= 30


def test_l_ecart_du_salaire_annuel_moyen_est_celui_des_coefficients(temoin, mesures):
    """Sur les mêmes années, le salaire annuel moyen refait aux coefficients du
    dépôt (les colonnes de la Cnav, `coefficient_revalorisation_portee_au_compte`)
    et à ceux de TRAJECTOiRE : leur rapport EST l'écart observé, au millième. La
    chaîne des coefficients est donc toute la différence (CHAINE_SAM). Sauf où
    le relevé du dépôt ne porte pas les mêmes années : l'année partagée du cas
    type 10, l'AVPF du cas type 4."""
    parametres = _parametres(temoin)
    macro = Simulateur().macro

    def chaine(annee, liquidation):
        produit = 1.0
        for k in range(annee + 1, liquidation + 1):
            produit *= 1 + parametres[k]["revaloSam"] / 100
        return produit

    verifies = 0
    for code, cas in temoin["cas"].items():
        if code.startswith(("cor_4_", "cor_10_")) or not montants_confrontes(cas):
            continue
        depot, traj = mesures[code]
        if "salaire_annuel_moyen" not in traj or "salaire_annuel_moyen" not in depot:
            continue
        date = cas["trajectoire"]["liquidation"]["date"]
        annee, mois = int(date[:4]), int(date[5:7])
        annees = _annees_cnav(cas)
        plafond = lambda a: parametres[a]["pss"]  # noqa: E731
        au_depot = _sam(annees, annee, plafond,
                        lambda a: macro.coefficient_revalorisation_portee_au_compte(a, annee, mois))
        a_trajectoire = _sam(annees, annee, plafond, lambda a: chaine(a, annee))
        attendu = au_depot / a_trajectoire - 1
        observe = _relatif(depot["salaire_annuel_moyen"], traj["salaire_annuel_moyen"])
        assert observe == pytest.approx(attendu, abs=1e-3), (code, observe, attendu)
        verifies += 1
    assert verifies >= 20


def test_les_points_du_depot_sont_ceux_de_trajectoire_aux_taux_minimaux(temoin, mesures):
    """L'acquisition des points de l'Arrco et de l'Agirc-Arrco, refaite sur les
    revenus que TRAJECTOiRE a portés au compte (`calculePtCotisesComplementaire` :
    le revenu au plafond, fois le taux, divisé par la valeur d'achat de l'année) :
    aux taux MOYENS, ce sont les points de TRAJECTOiRE ; aux taux MINIMAUX, ceux
    du dépôt, à 0,5 % près. L'écart des points n'est donc que la convention des
    taux (TAUX_CONTRACTUELS). Les carrières de non-cadres seules, sans chômage, ni
    AVPF, ni année partagée."""
    parametres = _parametres(temoin)
    achat: dict[str, dict[int, float]] = {}
    for ligne in temoin["parametres_trajectoire"]["valeur_achat"]:
        annee, caisse, valeur = ligne.split()
        achat.setdefault(caisse, {})[int(annee)] = float(valeur.split("=")[1])

    def valeur_achat(caisse: str, annee: int) -> float:
        # Une année sans ligne garde la valeur de la précédente.
        return achat[caisse][max(a for a in achat[caisse] if a <= annee)]

    verifies = 0
    for code, cas in temoin["cas"].items():
        traj = cas["trajectoire"]
        if (set(traj["points"]) - {"Arrco", "Agirc-Arrco"} or not traj["points"]
                or code.startswith(("cor_1_", "cor_3_", "cor_4_", "cor_10_", "rg_cadre"))
                or not montants_confrontes(cas)):
            continue
        moyens = minimaux = 0.0
        for annee, revenu, _, _ in _annees_cnav(cas):
            caisse = "Arrco" if annee < 2019 else "Agirc-Arrco"
            assiette = min(revenu, parametres[annee]["pss"]) / valeur_achat(caisse, annee)
            moyens += assiette * parametres[annee]["txCotARRCOsalempl_t1"]
            minimaux += assiette * parametres[annee]["txCotMIN_ARRCOsalempl_t1"]
        depot, _ = mesures[code]
        points_depot = sum(p for r, p in depot["points"].items() if r in COMPLEMENTAIRES)
        assert sum(traj["points"].values()) == pytest.approx(moyens, rel=5e-3), code
        assert points_depot == pytest.approx(minimaux, rel=5e-3), code
        verifies += 1
    assert verifies >= 12


def test_la_valeur_du_point_de_trajectoire_est_celle_du_jour(temoin, mesures):
    """La valeur de service que TRAJECTOiRE sert est celle que sa table donne au
    mois du départ, comme le dépôt depuis l'étape 138.20 (`valeurs_service_datees.csv`) :
    les deux tables datent les relèvements au même mois, et la confrontation
    des valeurs du point ne garde que les valeurs projetées (VALEURS_PROJETEES)."""
    service: dict[str, list[tuple[str, float]]] = {}
    for ligne in temoin["parametres_trajectoire"]["valeur_service"]:
        date, caisse, valeur = ligne.split()
        service.setdefault(caisse, []).append((date, float(valeur.split("=")[1])))
    for code, cas in temoin["cas"].items():
        _, traj = mesures[code]
        date = cas["trajectoire"]["liquidation"]["date"]
        for caisse, valeur in traj["valeurs"].items():
            if caisse not in ("Arrco", "Agirc", "Agirc-Arrco"):
                continue
            en_vigueur = [v for d, v in service[caisse] if d <= date]
            assert en_vigueur, (code, caisse)
            assert valeur == pytest.approx(en_vigueur[-1], rel=1e-6), (code, caisse)


# ---------------------------------------------------------------------------
# La confrontation
# ---------------------------------------------------------------------------

def _hors_de(quantite: str, ecart: float) -> bool:
    if quantite in ("points_arrco", "points_agirc", "points_agirc_arrco"):
        bas, haut = ECARTS_DES_POINTS[quantite.removeprefix("points_")]
        return not bas <= ecart <= haut
    return abs(ecart) > TOLERANCES[quantite] + 1e-12


def test_le_scenario_1_concorde_avec_trajectoire_ou_son_ecart_est_explique(ecarts):
    """Chaque quantité de chaque cas : à sa tolérance, ou dans la borne de son
    écart déclaré. Les points de l'Agirc-Arrco se bornent par famille
    (`ECARTS_DES_POINTS`, la convention des taux)."""
    ecarts_hors = []
    for code, mesures_ in ecarts.items():
        for quantite, ecart in mesures_.items():
            declare = ECARTS.get((code, quantite))
            if declare is not None:
                bas, haut, cause = declare
                if not bas - 1e-9 <= ecart <= haut + 1e-9:
                    ecarts_hors.append(f"{code}, {quantite} : {ecart:+.4f} hors de "
                                       f"[{bas:+.4f}, {haut:+.4f}] — {cause[:120]}…")
            elif _hors_de(quantite, ecart):
                cause = TAUX_CONTRACTUELS if quantite.startswith("points_") else "non déclaré"
                ecarts_hors.append(f"{code}, {quantite} : {ecart:+.4f}, {cause}")
    assert not ecarts_hors, "\n".join(ecarts_hors)


def test_un_ecart_declare_en_est_un(ecarts):
    """Un écart déclaré qui rentre dans la tolérance n'en est plus un : la
    déclaration se retire, sans quoi elle couvrirait le prochain."""
    for (code, quantite), (_, _, cause) in ECARTS.items():
        assert code in ecarts, f"{code} : cas absent du témoin"
        assert quantite in ecarts[code], f"{code}, {quantite} : quantité non mesurée"
        assert _hors_de(quantite, ecarts[code][quantite]), (
            f"{code}, {quantite} : {ecarts[code][quantite]:+.4f}, dans la tolérance — "
            f"retirer la déclaration ({cause[:80]}…)")


def test_la_carriere_longue_et_le_minimum_contributif_concordent(ecarts):
    """Deux règles que trois modèles calculent : le départ anticipé pour carrière
    longue — âge, durée cotisée, trimestres avant vingt ans — et le minimum
    contributif, à dix centimes par an près sur le régime général."""
    for code in ("cor_1_1955", "cor_2_1955", "cor_2_1960", "cor_2_1963", "cor_2bis_1960",
                 "cor_2bis_1963", "cor_5_1955", "cor_10_1960", "cor_10_1963"):
        assert ecarts[code]["carriere_longue"] == 0.0, code
    for code in ("rg_bas_salaire", "cor_2bis_1955", "cor_2bis_1963"):
        assert abs(ecarts[code]["regime_general"]) < 1e-4, code
        assert ecarts[code]["minimum"] == 0.0, code


def test_trajectoire_garde_le_coefficient_de_solidarite_au_dela_de_2023(temoin):
    """Ce que le registre lisait dans son code (`calculeModulationTemporaire`,
    sans fin), l'exécution le montre : tout départ au premier âge du taux plein
    depuis 2019 reçoit la minoration temporaire de l'Agirc-Arrco, 10 % (5 % au
    taux réduit de CSG) pendant trente-six mois — ceux de 2024 à 2035 compris,
    quand elle est supprimée pour les retraites prenant effet depuis le 1er
    décembre 2023 (registre, `trajectoire`). Le dépôt n'en sert aucune : la
    confrontation lit la pension de TRAJECTOiRE avant elle."""
    modules = {code: cas["trajectoire"].get("modulations", {}).get("Agirc-Arrco")
               for code, cas in temoin["cas"].items()}
    apres = [code for code, cas in temoin["cas"].items()
             if cas["trajectoire"]["liquidation"]["date"] >= "2023-12"
             and "Agirc-Arrco" in cas["trajectoire"]["caisses"]]
    assert len(apres) >= 15
    for code in apres:
        assert modules[code] is not None, code
        assert modules[code]["taux"] in (0.9, 0.95), code


# ---------------------------------------------------------------------------
# TRAJECTOiRE rejoué, seulement sur demande
# ---------------------------------------------------------------------------

def test_trajectoire_rejoue_le_temoin(temoin, tmp_path):
    """Le témoin est ce que TRAJECTOiRE produit : rejoué si R et TRAJECTOiRE sont
    installés et que `TRAJECTOIRE` le demande (« Ubuntu » : par la WSL, « r » :
    Rscript du système). Les sorties figées suffisent à la confrontation."""
    demande = os.environ.get("TRAJECTOIRE")
    if not demande:
        pytest.skip("les sorties figées suffisent : TRAJECTOiRE ne se rejoue que sur "
                    "demande (TRAJECTOIRE=Ubuntu ou TRAJECTOIRE=r), R installé")
    distribution = None if demande.lower() == "r" else demande
    if shutil.which("wsl" if distribution else "Rscript") is None:
        pytest.skip("R introuvable sur ce poste")
    sys.path.insert(0, str(SCRIPT.parent))
    import trajectoire as script  # noqa: E402

    sortie = tmp_path / "trajectoire.json"
    script.SORTIE = sortie
    assert script.main(["--wsl", distribution or "aucune"]) == 0
    rejoue = json.loads(sortie.read_text(encoding="utf-8"))
    sans_date = lambda document: {k: v for k, v in document.items() if k != "execute_le"}
    assert sans_date(rejoue) == sans_date(temoin)
