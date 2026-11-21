"""Les deux filets de la carte de justesse (action 194, étape B) : le
balayage de cohérence et la neutralisation, sur le moteur du jour.

    python scripts/filets.py balayage [--rapide] [--processus 4]
    python scripts/filets.py neutralisation [--processus 4] [--fiches a,b]

Chacun récrit sa moitié du rapport, ``tests/cliquets_de_justesse/
filets_rapport.yaml`` ; ``tests/test_filets.py`` en tient le cliquet. Les
règles sont dans ``noyau/filets.py``. Ni l'un ni l'autre ne tourne dans la
suite : le balayage dure une demi-heure sur quatre cœurs, la neutralisation
une heure.

Le balayage : les treize cas types du coût (``castypes.CAS_TYPES``), écrits
en part du salaire moyen de chaque année, d'un profil plat (le cas au SMIC à
la moitié du salaire moyen) ; les baisses sur les générations 1940 à 1990,
nées en janvier, les sauts de mois en mois sur les mêmes ; chaque âge de
départ par trimestre, de 60 ans (ou deux ans avant l'âge du cas type, quand
un statut ou des services datent son départ) à 70 ans.

La neutralisation : chaque partie mutée dans une copie des données, le paquet
rebâti par la fabrique, les 937 témoins de simulation rejoués quand le paquet
a changé.
"""

from __future__ import annotations

import argparse
import csv
import datetime
import hashlib
import io
import json
import multiprocessing
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle import pont  # noqa: E402
from retraite_notionnelle.castypes import CAS_TYPES, PROFIL_SMIC  # noqa: E402
from retraite_notionnelle.config import RACINE_DONNEES  # noqa: E402
from retraite_notionnelle.donnees.chargement import charger_yaml  # noqa: E402
from retraite_notionnelle.noyau import carte, filets, justesse  # noqa: E402

TEMOINS = RACINE / "tests" / "temoins" / "simulations.json"
GENERATIONS = range(1940, 1991)
#: Le SMIC vaut entre 0,40 et 0,52 du salaire moyen de 1970 à 2024 : le cas
#: au SMIC se balaie à la moitié, d'un profil plat comme les autres.
NIVEAU_DU_SMIC = 0.5


def cas_du_balayage() -> list[dict]:
    sortie = []
    for cas in CAS_TYPES:
        sortie.append({
            "code": cas.code, "statut": cas.affiliation, "debut": int(cas.age_debut),
            "salaire": NIVEAU_DU_SMIC if cas.profil_carriere == PROFIL_SMIC
            else cas.niveau_salaire,
            "primes": cas.part_primes, "sexe": cas.sexe, "enfants": cas.nombre_enfants,
            "interruptions_relatives": list(cas.interruptions_relatives),
            "premier_age": 60 * 12 if cas.regle_liquidation == "taux_plein"
            else int(round((cas.age_liquidation - 2) * 12)),
        })
    return sortie


# --- Le balayage ---------------------------------------------------------------

_PAQUET: bytes | None = None


def _initialiser(paquet: bytes) -> None:
    global _PAQUET
    _PAQUET = paquet


def _simuler_un_lot(requetes: list[dict]) -> list[dict | None]:
    return filets.simuler_par_le_pont(requetes, _PAQUET)


def simulateur_parallele(processus: int, lot: int = 2500):
    paquet = (RACINE / "moteur" / "donnees.json").read_bytes()

    def simuler(requetes):
        lots = [requetes[i:i + lot] for i in range(0, len(requetes), lot)]
        debut = time.time()
        sortie = []
        with multiprocessing.Pool(processus, _initialiser, (paquet,)) as pool:
            for i, rendus in enumerate(pool.imap(_simuler_un_lot, lots)):
                sortie.extend(rendus)
                print(f"  lot {i + 1}/{len(lots)}, {time.time() - debut:.0f} s",
                      file=sys.stderr, flush=True)
        return sortie
    return simuler


def balayage(arguments) -> dict:
    paquet = filets.paquet_du_depot()
    cas = cas_du_balayage()
    if arguments.cas:
        cas = [c for c in cas if c["code"] in arguments.cas.split(",")]
    rapport_par_cas = []
    for un_cas in cas:
        ages = range(un_cas["premier_age"], 70 * 12 + 1, 3 if not arguments.rapide else 24)
        generations_mois = [annee * 12 + mois for annee in GENERATIONS for mois in range(12)]
        print(f"{un_cas['code']} : {len(ages)} âges", file=sys.stderr, flush=True)
        rapport_par_cas.append(filets.balayer(
            [un_cas], generations_annees=list(GENERATIONS), generations_mois=generations_mois,
            ages_mois=ages, simuler=simulateur_parallele(arguments.processus),
            bornes=filets.bornes_du_paquet(paquet), versions=filets.bornes_de_version(paquet),
            liste=filets.charger_liste()))
    return _fusionner(rapport_par_cas, arguments.rapide)


def _fusionner(rapports: list[dict], rapide: bool) -> dict:
    comptes = {"calculs": 0, "fermees": 0, "sauts": {"admis": 0, "a_expliquer": 0},
               "baisses": {p: {"admis": 0, "a_expliquer": 0} for p in filets.PERTURBATIONS},
               "a_expliquer": 0}
    groupes = []
    for rapport in rapports:
        c = rapport["comptes"]
        for cle in ("calculs", "fermees", "a_expliquer"):
            comptes[cle] += c[cle]
        for cle in ("admis", "a_expliquer"):
            comptes["sauts"][cle] += c["sauts"][cle]
            for p in filets.PERTURBATIONS:
                comptes["baisses"][p][cle] += c["baisses"][p][cle]
        groupes += rapport["a_expliquer"]
    groupes.sort(key=lambda g: (-g["pensions"], g["sorte"], g["cas"], g["point"]))
    saines = [p for r in rapports for p in r["echantillon"]["paires"][
        r["echantillon"]["a_expliquer"]:]]
    echantillon = filets._echantillon(groupes, saines)
    # L'exemple de chaque groupe est dans l'échantillon pour les premiers ; les
    # autres se refont par leur cas type, leur génération et leurs âges.
    groupes = [{k: v for k, v in g.items() if k != "exemple"} for g in groupes]
    return {"le": datetime.date.today().isoformat(), "rapide": rapide,
            "seuil_de_saut": filets.SEUIL_DE_SAUT,
            "perimetre": {"cas_types": len(rapports), "generations": "1940 à 1990",
                          "ages": "de 60 ans (ou deux ans avant l'âge du cas type) à 70 ans, "
                                  "par trimestre"},
            "comptes": comptes, "a_expliquer": groupes, "echantillon": echantillon}


# --- La neutralisation ---------------------------------------------------------

#: Les colonnes qui situent une ligne, et qu'une mutation de la source ne
#: touche pas.
CLES = {"generation", "annee", "date", "date_effet", "debut", "fin", "depuis", "jusqu_a",
        "annee_naissance", "regime", "code", "id"}

_COPIE: Path | None = None
_REQUETES: list[dict] = []
_BASE_DES_FICHES: dict[str, str] = {}


def _sources(fiche: dict) -> list[tuple[Path, set[str]]]:
    texte = (fiche.get("code") or {}).get("parametres")
    sortie = []
    for morceau in str(texte).split(";"):
        if ":" not in morceau:
            continue
        fichiers, colonnes = morceau.split(":", 1)
        noms = {c.strip().split(" ")[0] for c in colonnes.split(",") if c.strip()}
        for fichier in fichiers.split(","):
            fichier = fichier.strip()
            if fichier.endswith((".csv", ".yaml")):
                sortie.append((Path(fichier), noms))
    return sortie


def _muter_nombre_ecrit(texte: str) -> str:
    try:
        return str(int(texte) + 1)
    except ValueError:
        try:
            valeur = float(texte)
        except ValueError:
            return texte
        return repr(valeur * 1.01 if valeur else 0.01)


def _muter_csv(chemin: Path, colonnes: set[str]) -> None:
    texte = chemin.read_text(encoding="utf-8")
    lignes = texte.splitlines(keepends=True)
    entetes_idx = next((i for i, l in enumerate(lignes) if l.strip() and not l.startswith("#")),
                       None)
    if entetes_idx is None:
        return
    lecteur = list(csv.reader(io.StringIO("".join(lignes[entetes_idx:]))))
    entetes = lecteur[0]
    visees = [i for i, nom in enumerate(entetes) if nom in colonnes and nom not in CLES]
    if not visees:
        return
    sortie = io.StringIO()
    ecrivain = csv.writer(sortie, lineterminator="\n")
    ecrivain.writerow(entetes)
    for ligne in lecteur[1:]:
        ecrivain.writerow([_muter_nombre_ecrit(v) if i in visees else v
                           for i, v in enumerate(ligne)])
    chemin.write_text("".join(lignes[:entetes_idx]) + sortie.getvalue(), encoding="utf-8")


def _muter_cles(objet, cles: set[str]):
    if isinstance(objet, dict):
        return {k: (filets.muter_valeurs(v) if k in cles else _muter_cles(v, cles))
                for k, v in objet.items()}
    if isinstance(objet, list):
        return [_muter_cles(v, cles) for v in objet]
    return objet


def _muter_source(fiche: dict, copie: Path) -> list[Path]:
    touches = []
    for relatif, colonnes in _sources(fiche):
        chemin = copie / "reference" / relatif
        if not chemin.exists():
            continue
        touches.append(chemin)
        if chemin.suffix == ".csv":
            _muter_csv(chemin, colonnes)
        else:
            donnees = charger_yaml(chemin)
            chemin.write_text(yaml.safe_dump(_muter_cles(donnees, colonnes),
                                             allow_unicode=True, sort_keys=False),
                              encoding="utf-8")
    return touches


def _initialiser_neutralisation(requetes: list[dict], fiches_ecrites: dict[str, str]) -> None:
    global _COPIE, _REQUETES, _BASE_DES_FICHES
    _COPIE = Path(tempfile.mkdtemp(prefix="filets_")) / "data"
    shutil.copytree(RACINE_DONNEES, _COPIE)
    _REQUETES = requetes
    _BASE_DES_FICHES = fiches_ecrites


def _empreinte(objet) -> str:
    return hashlib.sha256(json.dumps(objet, sort_keys=True).encode()).hexdigest()[:16]


def _rejouer_une_tache(arguments: tuple) -> tuple:
    indice, tache, fiches = arguments
    regles = _COPIE / "reference" / "regles"
    sauvegardes: dict[Path, bytes] = {}
    try:
        for nom, fiche in tache["fiches"].items():
            chemin = regles / f"{nom}.yaml"
            sauvegardes[chemin] = chemin.read_bytes()
            chemin.write_text(yaml.safe_dump(fiche, allow_unicode=True, sort_keys=False),
                              encoding="utf-8")
        if tache["source"] is not None:
            avant = {c: c.read_bytes() for c in (
                _COPIE / "reference" / r for r, _ in _sources(fiches[tache["source"]]))
                if c.exists()}
            sauvegardes.update(avant)
            _muter_source(fiches[tache["source"]], _COPIE)
        try:
            paquet = pont._batir_le_paquet(_COPIE)
        except RuntimeError as erreur:
            return indice, "refus:" + str(erreur)[-200:], None
        empreinte = hashlib.sha256(paquet).hexdigest()[:16]
        if indice != 0 and empreinte == _BASE_PAQUET_EMPREINTE:
            return indice, empreinte, None
        cas = [{"cle": str(i), "requete": q} for i, q in enumerate(_REQUETES)]
        reponse = pont._demander({"simulations": {"cas": cas}}, paquet)
        temoins = {cle: _empreinte(r) for cle, r in reponse["resultats"].items()}
        temoins.update({cle: "refus" for cle in reponse["echecs"]})
        return indice, empreinte, temoins
    finally:
        for chemin, octets in sauvegardes.items():
            chemin.write_bytes(octets)


_BASE_PAQUET_EMPREINTE = hashlib.sha256(b"").hexdigest()[:16]


def neutralisation(arguments) -> dict:
    global _BASE_PAQUET_EMPREINTE
    fiches = carte.fiches()
    if arguments.fiches:
        fiches = {n: f for n, f in fiches.items() if n in arguments.fiches.split(",")}
    temoins = json.loads(TEMOINS.read_text(encoding="utf-8"))
    cles = list(temoins)
    requetes = [temoins[c]["requete"] for c in cles]
    _BASE_PAQUET_EMPREINTE = hashlib.sha256(pont._batir_le_paquet()).hexdigest()[:16]

    def executer(taches):
        debut = time.time()
        rendus: list = [None] * len(taches)
        with multiprocessing.Pool(arguments.processus, _initialiser_neutralisation,
                                  (requetes, {})) as pool:
            for n, (indice, empreinte, rejoues) in enumerate(pool.imap_unordered(
                    _rejouer_une_tache, ((i, t, fiches) for i, t in enumerate(taches)))):
                nommes = None if rejoues is None else {cles[int(i)] if i.isdigit() else i: v
                                                       for i, v in rejoues.items()}
                rendus[indice] = (empreinte, nommes)
                if n % 25 == 0:
                    print(f"  {n + 1}/{len(taches)}, {time.time() - debut:.0f} s",
                          file=sys.stderr, flush=True)
        return rendus

    parties = filets.neutraliser(fiches, executer=executer)
    familles = justesse.familles()
    comptes = {"parties": len(parties), "gardee": 0, "non_gardee": 0, "hors_d_atteinte": 0}
    par_famille: dict[str, dict[str, int]] = {}
    for partie in parties.values():
        comptes[partie["etat"]] += 1
        fiche = fiches[partie["fiche"]]
        famille = next((familles[r] for r in fiche.get("regimes") or [] if r in familles),
                       justesse.SANS_FAMILLE)
        partie["famille"] = famille
        compte = par_famille.setdefault(famille, {"gardee": 0, "non_gardee": 0,
                                                  "hors_d_atteinte": 0})
        compte[partie["etat"]] += 1
    liste = sorted(parties.values(), key=lambda p: (p["etat"], p["famille"], p["fiche"],
                                                    str(p["version"])))
    return {"le": datetime.date.today().isoformat(), "temoins": len(cles),
            "comptes": comptes, "par_famille": dict(sorted(par_famille.items())),
            "parties": [{k: p[k] for k in ("fiche", "version", "famille", "etat", "mutation", "refusee",
                                           "changes")} for p in liste]}


def ecrire(cle: str, contenu: dict) -> None:
    rapport = {}
    if filets.RAPPORT.exists():
        rapport = yaml.safe_load(filets.RAPPORT.read_text(encoding="utf-8")) or {}
    rapport[cle] = contenu
    entete = ("# Le dernier rapport des filets de la carte de justesse (action 194, étape B),\n"
              "# que scripts/filets.py écrit : jamais à la main.\n")
    filets.RAPPORT.write_text(entete + yaml.safe_dump(rapport, allow_unicode=True,
                                                      sort_keys=False, width=100),
                              encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("filet", choices=("balayage", "neutralisation"))
    parser.add_argument("--processus", type=int, default=os.cpu_count() or 4)
    parser.add_argument("--rapide", action="store_true",
                        help="le balayage aux âges de deux ans en deux ans")
    parser.add_argument("--cas", help="les seuls cas types nommés, séparés par des virgules")
    parser.add_argument("--fiches", help="les seules fiches nommées")
    parser.add_argument("--sans-ecrire", action="store_true")
    arguments = parser.parse_args()
    debut = time.time()
    contenu = balayage(arguments) if arguments.filet == "balayage" else neutralisation(arguments)
    contenu["duree_s"] = round(time.time() - debut)
    print(json.dumps(contenu["comptes"], ensure_ascii=False))
    if not arguments.sans_ecrire:
        ecrire(arguments.filet, contenu)


if __name__ == "__main__":
    main()
