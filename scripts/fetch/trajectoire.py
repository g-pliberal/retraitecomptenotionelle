#!/usr/bin/env python3
"""Témoin de TRAJECTOiRE (DREES), exécuté à part, sur les cas types du COR.

    python scripts/fetch/trajectoire.py            # refait tests/temoins/trajectoire.json
    python scripts/fetch/trajectoire.py --lister   # les carrières du dépôt, sans rien exécuter
    python scripts/fetch/trajectoire.py --garder   # garde les tables et les sorties de R
    python scripts/fetch/trajectoire.py --sorties DOSSIER   # relit des sorties gardées

À quoi il sert. TRAJECTOiRE est le modèle de microsimulation de la DREES ;
c'est un de ses modules qui calcule les cas types du rapport annuel du Conseil
d'orientation des retraites. Il est au registre (`data/reference/referents.yaml`,
`trajectoire`) comme une seconde implémentation du droit, écrite par d'autres :
ce n'est PAS une source officielle, et un désaccord ne désigne pas d'office le
coupable — le registre lui en a déjà trouvé huit torts à la lecture.

Ce qu'il fait. Deux jeux de cas, une seule exécution de R (`trajectoire.R`) :

* LES CAS TYPES DU COR, que TRAJECTOiRE construit lui-même par le script qu'il
  livre pour cela, sur les générations de `GENERATIONS`, une hypothèse de
  croissance du salaire moyen ; pour chaque cas type et chaque génération, le
  premier âge au taux plein qu'il marque. Ce script en tire la carrière que
  TRAJECTOiRE a calculée — revenu de chaque année, statut, chômage, AVPF,
  primes —, et l'écrit en requête du simulateur du dépôt (`requete_cor`), dans
  la mesure où le formulaire sait la dire : une ligne par année, une part de
  primes pour toute la carrière.
* LES CARRIÈRES DU DÉPÔT : les onze droits directs de `destinie_2.py`, écrits
  en tables d'entrée de TRAJECTOiRE — les mêmes requêtes que le témoin de
  Destinie 2, ce qui confronte trois modèles sur une même carrière.

Il fige les sorties dans `tests/temoins/trajectoire.json`, avec la version, le
commit, la date et la législation ; `tests/test_trajectoire.py` y confronte le
scénario 1, sans R.

Ce qu'il ne fait pas. Le code de TRAJECTOiRE n'entre jamais au dépôt : il est
sous EUPL-1.2, licence à réciprocité, et le copier ferait passer le dépôt sous
sa licence (`docs/architecture.md`, § 3.4). Il s'installe à part — dans la
distribution Ubuntu de la WSL sur le poste du propriétaire —, et seules ses
sorties entrent ici, leur origine et leur licence dites dans le témoin. Aucune
donnée confidentielle : le mode « cas types » se passe de l'EIC et de l'EIR.

LA LÉGISLATION est la plus récente que la version publique porte : la loi du
14 avril 2023 et ses décrets d'août 2023, sans la loi du 30 décembre 2025, qui
suspend la réforme pour les générations 1964 à 1968 (`parametres_age_duree`
dans le témoin). Ses paramètres réglementaires sont réels jusqu'en 2022-2024 et
projetés ensuite, sur les hypothèses du COR : un départ de 2025 ou de 2026 en
porte l'écart (registre).

Installation de TRAJECTOiRE, sur le poste, une fois (voir le témoin pour le
commit) : télécharger sous Windows l'archive du commit par l'API du GitLab de
la DREES (`/api/v4/projects/787/repository/archive.tar.gz?sha=…`), la déposer
dans `~/modeles/trajectoire` de la WSL, puis `R CMD INSTALL` dans la
bibliothèque de l'utilisateur, après les paquets qu'il exige et qu'Ubuntu n'a
pas (data.table ≥ 1.16, logger, icarus, qs — retiré du CRAN, pris dans ses
archives —, arrow), téléchargés sous Windows quand le réseau de la WSL coupe.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RACINE / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import destinie_2  # noqa: E402  (les carrières du dépôt, écrites une fois)
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

SORTIE = RACINE / "tests" / "temoins" / "trajectoire.json"
SCRIPT_R = Path(__file__).resolve().with_suffix(".R")

#: Le modèle, tel qu'il a été téléchargé et installé (voir l'en-tête).
DEPOT_TRAJECTOIRE = "https://git.drees.fr/drees_code_public/modeles/trajectoire"
COMMIT = "0963b5775b3898dc155b78095232f9f5a1d59db0"
#: Le titre du commit dit 1.1.2 ; le fichier DESCRIPTION du paquet, 1.1.1.
VERSION_COMMIT = "trajectoire v1.1.2 (4 avril 2025)"
LICENCE = "EUPL-1.2"

#: Les générations des cas types du COR. Avant 1964, la loi est la même des
#: deux côtés ; 1964 montre l'écart de la loi du 30 décembre 2025, que
#: TRAJECTOiRE n'a pas ; 1970, l'âge de 64 ans et les 172 trimestres que les
#: deux lois partagent. Les départs de 1964 et de 1970 sont futurs : leurs
#: montants reposent sur des projections, et ne se confrontent pas.
GENERATIONS = (1955, 1960, 1963, 1964, 1970)
#: La croissance annuelle du salaire moyen par tête (SMPT), en points : celle
#: que TRAJECTOiRE retient par défaut (`paramModele$hypSmpt`), l'une des quatre
#: du COR. Elle ne joue qu'au-delà des séries observées.
HYP_SMPT = 1.0

#: Les carrières du dépôt : les droits directs de Destinie 2, sans décès —
#: TRAJECTOiRE ne calcule ni réversion ni minimum vieillesse.
CARRIERES = tuple(cas for cas in destinie_2.CAS if cas.assure.deces is None)

#: Les états de TRAJECTOiRE (`passageFormatIdAnCaisse`) des statuts du dépôt,
#: et l'inverse pour les cas types du COR.
ETATS = {
    "salarie_prive_non_cadre": "Salarie du prive non cadre",
    "salarie_prive_cadre": "Salarie du prive cadre",
    "fonctionnaire_etat": "FPE",
    "fonctionnaire_territorial_hospitalier": "FPT ou FPH",
}
CAISSES_FONCTIONNAIRES = {"fonctionnaire_etat": "SRE",
                          "fonctionnaire_territorial_hospitalier": "CNRACL"}
#: Le statut du dépôt d'un état de TRAJECTOiRE, selon la catégorie de la
#: fonction publique que le cas type déclare (`categFonctionPublique`). L'actif
#: de la territoriale ou de l'hospitalière est l'aide-soignante du cas type 9, à
#: qui TRAJECTOiRE sert la majoration de durée des hospitaliers : le statut
#: hospitalier du dépôt, qui la sert aussi (action 138, étape 17).
STATUTS_COR = {
    ("Salarie du prive non cadre", None): "salarie_prive_non_cadre",
    ("Salarie du prive cadre", None): "salarie_prive_cadre",
    ("FPE", "Sedentaire"): "fonctionnaire_etat",
    ("FPE", "Superactif"): "fonctionnaire_etat_super_actif",
    ("FPE", "Actif"): "fonctionnaire_etat_actif",
    ("FPT ou FPH", "Sedentaire"): "fonctionnaire_territorial_hospitalier",
    ("FPT ou FPH", "Actif"): "fonctionnaire_hospitalier_actif",
    ("FPT ou FPH", "Superactif"): "fonctionnaire_territorial_hospitalier_super_actif",
}
#: Les états sans revenu d'activité, et le motif d'interruption du dépôt.
MOTIFS_COR = {"Chômage": "chomage_indemnise", "AVPF": "education_enfant"}

#: Ce que dit chaque cas type du COR (rapport annuel, annexe des cas types).
OBJETS_COR = {
    "1": "cas type 1 du COR : non-cadre puis cadre du privé, carrière complète",
    "2": "cas type 2 du COR : non-cadre du privé, carrière complète",
    "2bis": "cas type 2 bis du COR : le cas 2, au SMIC toute la carrière",
    "3": "cas type 3 du COR : non-cadre du privé, deux périodes de chômage",
    "4": "cas type 4 du COR : non-cadre du privé, deux enfants, interruption sous AVPF",
    "5": "cas type 5 du COR : fonctionnaire de l'État sédentaire, primes variables",
    "5primesConstantes": "cas type 5 du COR, à part de primes constante",
    "6": "cas type 6 du COR : fonctionnaire de l'État de catégorie A",
    "7": "cas type 7 du COR : fonctionnaire de l'État de catégorie A+",
    "8": "cas type 8 du COR : policier, catégorie super-active (bonification du cinquième)",
    "9": "cas type 9 du COR : aide-soignante hospitalière, catégorie active",
    "10": "cas type 10 du COR : non-cadre du privé puis fonctionnaire territorial",
    "11": "cas type 11 du COR : fonctionnaire territorial ou hospitalier sédentaire",
}


# ---------------------------------------------------------------------------
# Les carrières du dépôt, en tables de TRAJECTOiRE
# ---------------------------------------------------------------------------

def _mois(date: str) -> str:
    """« AAAA-MM » d'une date « AAAA-MM-JJ » ou « AAAA-MM »."""
    return date[:7]


def tables_depot(macro) -> dict[str, list[dict]]:
    """dtId, dtIdAnEtat, dtIdAnCaisseFonctionnaire et dtIdNumeroEnfant.

    Le revenu de chaque année est celui de la requête du dépôt
    (`destinie_2.revenus`), celui de l'année entière, l'année du départ
    comprise quand elle est travaillée : TRAJECTOiRE veut « le revenu annuel,
    même pour la dernière année » (sa documentation, « Premiers pas »), et le
    coupe lui-même au départ, au prorata des mois — ce que la requête du dépôt
    porte. Pour un fonctionnaire, il veut le traitement (`remuneration`) et les
    primes à part ; le dépôt dit la part des primes dans la rémunération.
    """
    dt_id, etats, fonctionnaires, enfants = [], [], [], []
    for cas in CARRIERES:
        assure = cas.assure
        annee_depart = int(cas.depart[:4])
        dt_id.append({
            "id": cas.code, "dateNaissance": _mois(assure.naissance),
            "sexe": "Homme" if assure.sexe == "H" else "Femme",
            # L'âge du décès ne joue que sur les chroniques et les indicateurs
            # de cycle de vie, que la confrontation ne lit pas.
            "ageMort": 85, "nbEnfant": len(cas.enfants), "dateLiq": cas.depart,
        })
        for rang, naissance in enumerate(cas.enfants, start=1):
            enfants.append({"id": cas.code, "numeroEnfant": rang,
                            "agePourEnfant": int(naissance[:4]) - assure.annee})
        for annee, (statut, montant) in destinie_2.revenus(assure, macro).items():
            if annee == annee_depart and not cas.travaille_l_annee_du_depart:
                raise ValueError(f"{cas.code} : {annee} est travaillée, le départ y tombe")
            primes = montant * assure.primes if statut in CAISSES_FONCTIONNAIRES else 0.0
            etats.append({"id": cas.code, "annee": annee, "etatTravail": ETATS[statut],
                          "remuneration": round(montant - primes, 6), "dureeEnMois": 12})
            if statut in CAISSES_FONCTIONNAIRES:
                fonctionnaires.append({"id": cas.code, "annee": annee,
                                       "caisse": CAISSES_FONCTIONNAIRES[statut],
                                       "primes": round(primes, 6)})
    return {"dtId": dt_id, "dtIdAnEtat": etats, "dtIdAnCaisseFonctionnaire": fonctionnaires,
            "dtIdNumeroEnfant": enfants}


COLONNES = {
    "dtId": ["id", "dateNaissance", "sexe", "ageMort", "nbEnfant", "dateLiq"],
    "dtIdAnEtat": ["id", "annee", "etatTravail", "remuneration", "dureeEnMois"],
    "dtIdAnCaisseFonctionnaire": ["id", "annee", "caisse", "primes"],
    "dtIdNumeroEnfant": ["id", "numeroEnfant", "agePourEnfant"],
}


def _ecrire_csv(chemin: Path, lignes: list[dict], colonnes: list[str]) -> None:
    with chemin.open("w", newline="", encoding="utf-8") as flux:
        ecrivain = csv.DictWriter(flux, fieldnames=colonnes, lineterminator="\n")
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


# ---------------------------------------------------------------------------
# L'exécution, dans R
# ---------------------------------------------------------------------------

def _nombre(texte: str):
    if texte in ("", "NA"):
        return None
    if texte in ("TRUE", "FALSE"):
        return texte == "TRUE"
    try:
        valeur = float(texte)
    except ValueError:
        return texte
    return int(valeur) if valeur.is_integer() and "." not in texte else valeur


def _lire_csv(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as flux:
        return [{cle: _nombre(valeur) for cle, valeur in ligne.items()}
                for ligne in csv.DictReader(flux)]


def executer(dossier: Path, distribution: str | None) -> tuple[dict[str, list[dict]], dict]:
    """R, une fois : ses tables de sortie, et les versions."""
    rscript, chemin = destinie_2.commande_r(distribution)
    if distribution:
        # La WSL démarre dans le dossier Windows courant : le dépôt. Le script
        # R s'en va dans un dossier temporaire avant de charger le paquet, mais
        # rien ne doit s'y lancer — `here` y trouverait le dépôt.
        rscript = rscript[:3] + ["--cd", "~"] + rscript[3:]
    sortie = dossier / "sorties"
    commande = rscript + [chemin(SCRIPT_R), chemin(dossier), chemin(sortie)]
    print("TRAJECTOiRE : les cas types du COR et les carrières du dépôt…", flush=True)
    fini = subprocess.run(commande, capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    if fini.returncode != 0:
        raise RuntimeError(f"TRAJECTOiRE a échoué :\n{fini.stdout[-3000:]}\n"
                           f"{fini.stderr[-3000:]}")
    tables = {fichier.stem: _lire_csv(fichier) for fichier in sorted(sortie.glob("*.csv"))}
    versions = json.loads((sortie / "versions.json").read_text(encoding="utf-8"))
    return tables, versions


# ---------------------------------------------------------------------------
# La requête du dépôt d'un cas type du COR
# ---------------------------------------------------------------------------

def _par_id(lignes: list[dict]) -> dict[str, list[dict]]:
    groupes: dict[str, list[dict]] = {}
    for ligne in lignes:
        groupes.setdefault(str(ligne["id"]), []).append(ligne)
    return groupes


def requete_cor(ident: str, tables: dict[str, list[dict]]) -> tuple[dict[str, str], list[str]]:
    """La requête du simulateur du dépôt pour un cas type du COR, et ce qu'elle
    n'a pas pu dire comme TRAJECTOiRE.

    * La naissance au 1er du mois : TRAJECTOiRE compte en mois, son âge
      d'ouverture tombe dans le mois de naissance, comme pour qui est né un 1er
      (`calendrier.origine_des_ages`).
    * Une ligne de relevé par année : le revenu que TRAJECTOiRE a porté au
      compte — le traitement et les primes d'un fonctionnaire réunis —, sous le
      statut de l'année. L'année du départ prend ce que TRAJECTOiRE y a compté
      (sa sortie `annees`, coupée au départ), ou se déclare sans activité.
    * Une année à deux états — le passage au statut de cadre, la fin de
      l'interruption sous AVPF, le passage à la fonction publique — ne s'écrit
      qu'en une ligne : celle de l'état qui a le plus de mois, celui que
      l'année suivante poursuit à égalité. Le script du COR donne à chacun des
      deux états le revenu de l'année entière (sa note : « le COR fournit des
      salaires relatifs déjà proratisés ») : la ligne reprend le revenu de
      l'état retenu. `requete_reserves` dit chacune de ces années.
    * La fonction publique compte ses services au temps : sa ligne porte ses
      trimestres, les mois divisés par trois, la fraction d'au moins un mois
      et demi faisant le trimestre.
    * Le chômage et l'AVPF : le motif dans « Interruptions » ; la ligne d'une
      année de chômage porte le salaire de la dernière année d'emploi, salaire
      de référence des points de l'Agirc-Arrco, celle de l'AVPF un revenu nul ;
      le dépôt en déduit les trimestres assimilés, l'AVPF et les points de
      chômage.
    * Les primes : une part pour toute la carrière, celle de la dernière année
      de fonction publique — c'est elle qui fait le traitement de référence de
      la pension civile ; le RAFP, qui suit les primes de chaque année, en
      garde l'écart.
    """
    entree = _par_id(tables["entrees_cor_id"])[ident][0]
    etats = _par_id(tables["entrees_cor_etats"]).get(ident, [])
    primes = {ligne["annee"]: ligne["primes"]
              for ligne in _par_id(tables["entrees_cor_fonctionnaires"]).get(ident, [])}
    fonctionnaire = _par_id(tables["fonctionnaires_cor"]).get(ident, [])
    categorie = fonctionnaire[0]["categFonctionPublique"] if fonctionnaire else None
    sorties = _par_id(tables["annees_cor"]).get(ident, [])
    annee_depart, mois_depart = (int(x) for x in entree["dateLiq"].split("-"))
    reserves: list[str] = []

    par_annee: dict[int, list[dict]] = {}
    for ligne in etats:
        par_annee.setdefault(int(ligne["annee"]), []).append(ligne)
    lignes, interruptions, primes_part = [], [], None
    for annee in sorted(par_annee):
        if annee > annee_depart or (annee == annee_depart and mois_depart == 1):
            continue
        candidats = par_annee[annee]
        # À égalité de mois, l'état que l'année suivante poursuit.
        suivants = {l["etatTravail"] for l in par_annee.get(annee + 1, [])}
        retenu = max(candidats, key=lambda ligne: (ligne["dureeEnMois"],
                                                   ligne["etatTravail"] in suivants))
        if len(candidats) > 1:
            reserves.append(
                f"{annee} : {' et '.join(c['etatTravail'] for c in candidats)} ; ligne "
                f"« {retenu['etatTravail']} »")
        etat = retenu["etatTravail"]
        if etat in MOTIFS_COR:
            # Une année sans activité : le statut d'affiliation est celui de la
            # dernière ligne d'emploi, le motif dit le reste. Le revenu d'une
            # ligne de chômage est, au relevé du dépôt, le salaire de référence
            # sur lequel l'Agirc-Arrco attribue ses points (`_revenu_reference`) :
            # celui de la dernière année d'emploi ; l'AVPF, le dépôt la calcule.
            emplois = [l for l in lignes if l[2] > 0]
            statut = lignes[-1][1] if lignes else "salarie_prive_non_cadre"
            reference = emplois[-1][2] if emplois and etat == "Chômage" else 0
            lignes.append((annee, statut, reference, None))
            interruptions.append((annee, MOTIFS_COR[etat]))
            continue
        cle = (etat, categorie if etat.startswith("FP") else None)
        statut = STATUTS_COR[cle]
        montant = float(retenu["remuneration"])
        mois = 12 if annee < annee_depart else mois_depart - 1
        mois = min(mois, int(retenu["dureeEnMois"]))
        if etat.startswith("FP"):
            prime = float(primes.get(annee) or 0.0)
            if montant + prime > 0:
                primes_part = prime / (montant + prime)
            montant += prime
        if annee == annee_depart:
            # Ce que TRAJECTOiRE a compté l'année du départ, coupée à lui.
            compte = sum(float(s["remuneration"]) for s in sorties if s["annee"] == annee)
            if etat.startswith("FP"):
                compte *= 1 / (1 - primes_part) if primes_part else 1
            montant = compte
        if montant <= 0 and annee == annee_depart:
            continue
        # La fonction publique compte ses services au temps, pas au revenu : la
        # ligne dit ses trimestres, comme le relevé d'un fonctionnaire, le mois
        # et demi faisant le trimestre (la fraction d'au moins quarante-cinq
        # jours). Le privé valide au revenu, des deux côtés.
        trimestres = (min(4, int(mois / 3 + 0.5)) if etat.startswith("FP") else None)
        lignes.append((annee, statut, round(montant), trimestres))
    if not lignes:
        raise ValueError(f"{ident} : aucune année de carrière")
    demande = {
        "naissance": f"{entree['dateNaissance']}-01",
        "sexe": "F" if entree["sexe"] == "Femme" else "H",
        "liquidation": entree["dateLiq"],
        "releve": ",".join(f"{a}:{s}:{m}" + (f":{t}" if t is not None else "")
                           for a, s, m, t in lignes),
    }
    derniere = lignes[-1][0]
    if mois_depart > 1 and derniere < annee_depart:
        interruptions.append((annee_depart, "sans_activite"))
    if interruptions:
        demande["interruptions"] = ",".join(_plages(interruptions))
    if primes_part:
        demande["primes"] = f"{round(primes_part, 4):g}"
    nombre = int(entree["nbEnfant"] or 0)
    if nombre:
        demande["enfants"] = str(nombre)
        demande["naissances"] = ",".join(_naissances_cor(ident, nombre, tables))
    return demande, reserves


def _plages(interruptions: list[tuple[int, str]]) -> list[str]:
    """« debut:fin:motif » des années consécutives d'un même motif."""
    plages: list[list] = []
    for annee, motif in interruptions:
        if plages and plages[-1][2] == motif and plages[-1][1] == annee - 1:
            plages[-1][1] = annee
        else:
            plages.append([annee, annee, motif])
    return [f"{debut}:{fin}:{motif}" for debut, fin, motif in plages]


def _naissances_cor(ident: str, nombre: int, tables) -> list[str]:
    """Les naissances des enfants du cas type 4, que TRAJECTOiRE ne date pas
    (il met chacun à 25 ans de sa mère, ce qui ne sert qu'à ses majorations de
    durée) : le premier au début de l'interruption sous AVPF, les suivants
    deux ans après chacun. Le dépôt y lit l'âge des enfants que l'AVPF suppose."""
    avpf = sorted(int(l["annee"]) for l in _par_id(tables["entrees_cor_etats"]).get(ident, [])
                  if l["etatTravail"] == "AVPF")
    debut = avpf[0] if avpf else int(_par_id(tables["entrees_cor_id"])[ident][0]["generation"]) + 28
    return [f"{debut + 2 * rang}-01-01" for rang in range(nombre)]


# ---------------------------------------------------------------------------
# Le témoin
# ---------------------------------------------------------------------------

PENSIONNE = {
    "dateLiqCaissePrincipale": "date", "ageLiq": "age", "caissePrincipale": "caisse_principale",
    "typeLiquidation": "type_liquidation", "typeDepart": "type_depart", "AOD": "AOD",
    "AAD": "AAD", "dureeRequise": "duree_requise",
    "dureeValideeTousRegimes": "duree_validee_tous_regimes",
    "aDecoteDansCaissePrincipale": "decote", "aSurcoteDansCaissePrincipale": "surcote",
    "nbTrimDecoteCaissePrincipale": "trimestres_decote",
    "nbTrimSurcoteCaissePrincipale": "trimestres_surcote", "aMinPension": "minimum",
    "categCSG": "categorie_csg",
}
INDICATEURS = ("pensionLiqEurosConstants", "pensionLiqSmpt", "txRemplacementNet",
               "txRemplacementNetSmpt", "txRemplacementCdv", "txRemplacementNetCdv",
               "txAnnuite", "txRecuperation", "txPrestation",
               "dureeRetraiteRelativeDureeCotisation")
CAISSE = {
    "dateLiq": "date", "pension": "pension_mensuelle",
    "pensionAvantMinEtMajo": "avant_minimum_et_majoration",
    "majorationEnfant": "majoration_enfants", "ajoutMinimum": "minimum", "taux": "taux",
    "tauxDecote": "decote", "tauxSurcote": "surcote", "nbTrimDecote": "trimestres_decote",
    "nbTrimSurcote": "trimestres_surcote",
}
BASE = {
    "prorat": "prorat", "dureeValidee": "duree_validee", "dureeCotisee": "duree_cotisee",
    "dureeGratuite": "duree_gratuite", "dureeValideeTousRegimes": "duree_validee_tous_regimes",
    "dureeCotiseTousRegimes": "duree_cotisee_tous_regimes", "dureeRequise": "duree_requise",
    "dureeRequiseProrat": "duree_requise_prorat", "AOD": "AOD", "AAD": "AAD",
    "MDAenfantPourTaux": "mda_taux", "MDAenfantPourProrat": "mda_prorat",
    "nbTrimBonification": "bonification", "typeDepart": "type_depart",
    "dateTauxPlein": "date_taux_plein",
}
FONCTIONNAIRE = {
    "categFonctionPublique": "categorie", "typeBonif": "bonification",
    "typeMDAFonc": "majoration_duree", "primesDansCotiseBase": "primes_dans_la_base",
    "majoBonifFonc": "majoration_pour_bonification",
}


def _arrondi(valeur):
    return round(valeur, 6) if isinstance(valeur, float) else valeur


def _champs(ligne: dict, noms: dict) -> dict:
    return {nouveau: _arrondi(ligne.get(ancien)) for ancien, nouveau in noms.items()
            if ancien in ligne}


def sorties_du_cas(ident: str, tables: dict[str, list[dict]], jeu: str) -> dict:
    """Ce que TRAJECTOiRE a calculé pour un cas : la liquidation, chaque caisse,
    chaque régime de base, les points, et les années portées au compte."""
    def du_cas(nom):
        return _par_id(tables[f"{nom}_{jeu}"]).get(ident, [])

    pensionne, = du_cas("pensionnes")
    racl = du_cas("racl")
    salaires = {l["caisse"]: _arrondi(l["salaireReference"]) for l in du_cas("salaires_reference")}
    bases = {}
    for ligne in du_cas("bases"):
        bases[ligne["caisse"]] = {**_champs(ligne, BASE),
                                  "salaire_reference": salaires.get(ligne["caisse"])}
    points: dict[str, float] = {}
    annuels = []
    for ligne in sorted(du_cas("points"), key=lambda l: (l["annee"], l["caisse"])):
        points[ligne["caisse"]] = points.get(ligne["caisse"], 0) + (ligne["nbPt"] or 0)
        if ligne["nbPt"]:
            annuels.append(f"{ligne['annee']} {ligne['caisse']} {ligne['nbPt']:g} "
                           f"(gratuits {ligne['nbPtGratuit'] or 0:g}, mois {ligne['nbMois']:g})")
    annees = [
        f"{l['annee']} {l['caisse']} {float(l['remuneration'] or 0):.2f} € ; "
        f"trimestres {float(l['nbTrimValide'] or 0):g} validés, "
        f"{float(l['nbTrimCotise'] or 0):g} cotisés, {l['nbTrimGratuit'] or 0:g} gratuits ; "
        f"AVPF {float(l['montantAvpf'] or 0):.2f} €"
        for l in sorted(du_cas("annees"), key=lambda l: (l["annee"], l["caisse"]))]
    sortie = {
        "liquidation": {**_champs(pensionne, PENSIONNE),
                        "carriere_longue": racl[0]["dateLiqRacl"] if racl else None},
        "caisses": {l["caisse"]: _champs(l, CAISSE) for l in du_cas("caisses")},
        "bases": bases,
        "points": {caisse: _arrondi(total) for caisse, total in sorted(points.items())},
        "indicateurs": {cle: _arrondi(pensionne.get(cle)) for cle in INDICATEURS},
        "annees": annees,
        "points_annuels": annuels,
    }
    fonctionnaire = du_cas("fonctionnaires")
    if fonctionnaire:
        sortie["fonctionnaire"] = {l["caisse"]: _champs(l, FONCTIONNAIRE) for l in fonctionnaire}
    modulations = du_cas("modulations")
    if modulations:
        sortie["modulations"] = {l["caisse"]: {"taux": l["taux"], "duree": l["duree"]}
                                 for l in modulations}
    return sortie


def _code_cor(ligne: dict) -> str:
    cas = str(ligne["casType"])
    cas = "5_primes_constantes" if cas == "5primesConstantes" else cas
    return f"cor_{cas}_{ligne['generation']}"


def _age_duree(tables) -> dict[str, list]:
    """L'âge d'ouverture, l'âge d'annulation de la décote et la durée requise
    du droit commun, tels que TRAJECTOiRE les lit : chaque valeur avec le mois
    de naissance à partir duquel elle vaut. C'est la législation qu'il porte, à
    confronter à celle du dépôt."""
    resultat: dict[str, list] = {}
    for grandeur in ("AOD", "AAD", "Duree"):
        lignes = sorted((str(l["dateNaissance"]), _arrondi(l["valeur"]))
                        for l in tables["parametres_age_duree"]
                        if l.get("categorie") == "Droit commun" and l["grandeur"] == grandeur)
        resultat[grandeur] = [f"{date} {valeur:g}" for date, valeur in lignes]
    return resultat


def _parametres(tables) -> dict[str, list[str]]:
    """Les paramètres de TRAJECTOiRE qui expliquent un écart de montant, une
    ligne par année ou par date : de quoi le vérifier sans relancer R."""
    def ligne(debut: str, valeurs: dict) -> str:
        return debut + " " + " ".join(f"{cle}={_arrondi(v):.10g}" for cle, v in valeurs.items()
                                      if v is not None)
    annuels = [ligne(str(l["annee"]), {k: v for k, v in l.items() if k != "annee"})
               for l in sorted(tables["parametres_annuels"], key=lambda l: l["annee"])]
    achat = [ligne(f"{l['annee']} {l['caisse']}", {"valeur_achat": l["valeurPtAcquisition"]})
             for l in sorted(tables["parametres_valeur_achat"],
                             key=lambda l: (l["caisse"], l["annee"]))]
    service = [ligne(f"{l['date']} {l['caisse']}", {"valeur_service": l["valeurPtService"]})
               for l in sorted(tables["parametres_valeur_service"],
                               key=lambda l: (l["caisse"], str(l["date"])))]
    fonction_publique = [ligne(f"{l['date']} {l['caisse']}", {"revalorisation": l["revalo"]})
                         for l in sorted(tables["parametres_revalorisation_fonction_publique"],
                                         key=lambda l: (l["caisse"], str(l["date"])))]
    return {"annuels": annuels, "valeur_achat": achat, "valeur_service": service,
            "revalorisation_fonction_publique": fonction_publique}


def temoin(tables: dict[str, list[dict]], versions: dict) -> dict:
    cas_temoins: dict[str, dict] = {}
    for ligne in sorted(tables["pensionnes_cor"], key=lambda l: (str(l["casType"]),
                                                                   l["generation"])):
        ident = str(ligne["id"])
        requete, reserves = requete_cor(ident, tables)
        cas_temoins[_code_cor(ligne)] = {
            "objet": OBJETS_COR[str(ligne["casType"])],
            "jeu": "cas_types_cor",
            "identifiant_trajectoire": ident,
            "cas_type": str(ligne["casType"]),
            "generation": ligne["generation"],
            "trajectoire": sorties_du_cas(ident, tables, "cor"),
            "requete": requete,
            "requete_reserves": reserves,
        }
    macro = Simulateur().macro
    for cas in CARRIERES:
        cas_temoins[cas.code] = {
            "objet": cas.objet,
            "jeu": "carrieres_du_depot",
            "trajectoire": sorties_du_cas(cas.code, tables, "depot"),
            "requete": destinie_2.requete(cas, macro),
        }
    return {
        "modele": "TRAJECTOiRE",
        "auteur": "DREES, bureau des retraites",
        "code": DEPOT_TRAJECTOIRE,
        "commit": COMMIT,
        "version": f"{versions['trajectoire']} (DESCRIPTION) ; commit « {VERSION_COMMIT} »",
        "licence": LICENCE,
        "origine": (
            "Sorties de TRAJECTOiRE, exécuté à part par scripts/fetch/trajectoire.py et "
            "trajectoire.R ; le code de TRAJECTOiRE n'entre pas au dépôt. Les chiffres "
            "ci-dessous sont ses résultats, publiés sous sa licence, avec leur origine. "
            "Les cas types du COR sont construits par le script que le paquet livre "
            "(inst/scripts/casTypesCOR.R), sur les hypothèses du COR qu'il livre."
        ),
        "execute_le": dt.date.today().isoformat(),
        "environnement": versions,
        "legislation": {
            "dit": ("la plus récente que la version publique porte : la loi du 14 avril "
                    "2023 et ses décrets d'août 2023, sans la loi du 30 décembre 2025 ; "
                    "paramètres réels jusqu'en 2022-2024, projetés ensuite sur les "
                    "hypothèses du COR"),
            "age_duree_droit_commun": _age_duree(tables),
        },
        "options": {
            "generations": list(GENERATIONS),
            "hypSmpt": HYP_SMPT,
            "age_des_cas_types": ("le premier âge au taux plein que le script du COR marque "
                                  "(ageMinTxPlein), carrière longue comprise"),
            "mode": "cas-types (telecharger = FALSE, strategieSauvegarde = 'ram')",
        },
        "conventions": {
            "durees": "en trimestres, fractions de la fonction publique comprises",
            "pensions": ("pension_mensuelle : brute, mensuelle, en euros de la date de "
                         "liquidation de la caisse ; taux en pour cent"),
            "dates": "AAAA-MM",
            "requete": ("cas types du COR : voir requete_cor dans le script ; carrières "
                        "du dépôt : la requête du témoin de Destinie 2"),
            "indicateurs": ("de cycle de vie, que la confrontation ne lit pas (action 138, "
                            "étape 9)"),
            "parametres": ("revaloSam en pour cent par an ; taux d'acquisition des points "
                           "moyens (txCot…) et minimaux (txCotMIN…) ; dates AAAA-MM"),
        },
        "parametres_trajectoire": _parametres(tables),
        "cas": cas_temoins,
    }


def _ecrire(document: dict) -> None:
    texte = json.dumps(document, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_bytes(texte.encode("utf-8"))


def main(arguments: list[str] | None = None) -> int:
    lecteur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    lecteur.add_argument("--wsl", default="Ubuntu", metavar="DISTRIBUTION",
                         help="la distribution de la WSL où R est installé ; "
                              "« aucune » pour lancer Rscript directement")
    lecteur.add_argument("--lister", action="store_true",
                         help="imprime les carrières du dépôt, sans rien exécuter")
    lecteur.add_argument("--garder", action="store_true",
                         help="garde le dossier des tables et des sorties de R")
    lecteur.add_argument("--sorties", type=Path, metavar="DOSSIER",
                         help="relit les sorties d'une exécution gardée, sans relancer R")
    options = lecteur.parse_args(arguments)
    macro = Simulateur().macro
    if options.lister:
        for cas in CARRIERES:
            print(f"{cas.code} : {cas.objet}")
        print(f"cas types du COR : générations {', '.join(map(str, GENERATIONS))}")
        return 0
    if options.sorties:
        tables = {f.stem: _lire_csv(f) for f in sorted(options.sorties.glob("*.csv"))}
        versions = json.loads((options.sorties / "versions.json").read_text(encoding="utf-8"))
        document = temoin(tables, versions)
        _ecrire(document)
        print(f"{SORTIE} : {len(document['cas'])} cas")
        return 0
    distribution = None if options.wsl in ("", "aucune") else options.wsl
    if distribution is None and shutil.which("Rscript") is None:
        print("Rscript est introuvable : installer R et TRAJECTOiRE (voir l'en-tête).",
              file=sys.stderr)
        return 1
    dossier = Path(tempfile.mkdtemp(prefix="trajectoire_"))
    try:
        for nom, lignes in tables_depot(macro).items():
            _ecrire_csv(dossier / f"{nom}.csv", lignes, COLONNES[nom])
        (dossier / "options.json").write_bytes(json.dumps({
            "generations": list(GENERATIONS), "hypSmpt": HYP_SMPT,
        }).encode("utf-8"))
        tables, versions = executer(dossier, distribution)
    finally:
        if options.garder:
            print(f"Tables et sorties gardées dans {dossier}")
        else:
            shutil.rmtree(dossier, ignore_errors=True)
    document = temoin(tables, versions)
    _ecrire(document)
    print(f"{SORTIE} : {len(document['cas'])} cas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
