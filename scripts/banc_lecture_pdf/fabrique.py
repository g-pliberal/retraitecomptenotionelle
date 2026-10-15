"""Le banc du lecteur PDF : les deux lecteurs sur les vrais documents de la fabrique.

Outil provisoire de l'action 161, étape 4 (le lecteur PDF passe au seul
JavaScript), à retirer avec le cœur Python du lecteur. Il confronte
``scripts/fetch/lecture_pdf.py`` et ``moteur/js/lecture-pdf.js`` tels qu'ils
sont sur le disque, de deux façons :

- **les documents** : chaque PDF que la fabrique télécharge, lu par les deux,
  niveau par niveau — objets, flux dépliés, tables des polices, fragments
  positionnés, lignes, lignes par page — avec, pour chaque écart, s'il tient
  à la seule règle des espaces (le Python tient pour espaces ``\\x1c`` à
  ``\\x1f`` et ``\\x85``, que ``trim`` ignore), la cause des écarts du
  premier temps, alignée depuis : aucun écart n'est plus attendu ;
- **les valeurs** : chaque script de la fabrique qui lit des PDF, lancé avec
  l'un puis l'autre lecteur (``lancer.py``), ses fichiers écrits et sa sortie
  comparés ; et la certification qui lit un PDF (``verifier_donnees``).

Commandes, depuis la racine du dépôt (le réseau sert la première fois ; un
document que l'on ne peut plus télécharger fait échouer son script, à lire
dans ``journaux/``) :

    python -I scripts/banc_lecture_pdf/fabrique.py tout
    python -I scripts/banc_lecture_pdf/fabrique.py preparer [--neuf]
    python -I scripts/banc_lecture_pdf/fabrique.py passer py|js [script…]
    python -I scripts/banc_lecture_pdf/fabrique.py comparer
    python -I scripts/banc_lecture_pdf/fabrique.py documents
    python -I scripts/banc_lecture_pdf/fabrique.py verifier

Le dossier de travail est ``$BANC_LECTURE_PDF`` (``/tmp/banc_lecture_pdf``
par défaut), hors du dépôt ; les scripts de la fabrique y tournent dans une
copie du dépôt faite par ``preparer``, à son dernier commit.
"""
from __future__ import annotations

import filecmp
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
import commun  # noqa: E402

CLE = lambda f: (f[0], f[1], -f[2], f[3])  # noqa: E731
#: Ce que ``trim`` et ``\s`` du JavaScript tiennent pour espaces.
BLANCS_JS = set(" \t\n\r\v\f      　﻿"
                + "".join(chr(c) for c in range(0x2000, 0x200B)))


def preparer(neuf: bool = False) -> None:
    if neuf:
        shutil.rmtree(commun.ARBRE, ignore_errors=True)
    if not commun.ARBRE.exists():
        commun.TRAVAIL.mkdir(parents=True, exist_ok=True)
        subprocess.run(["git", "clone", "-q", str(commun.DEPOT), str(commun.ARBRE)], check=True)
    print(f"copie du dépôt : {commun.ARBRE}")


def passer(lecteur: str, scripts: list[str]) -> None:
    preparer()
    journaux = commun.TRAVAIL / "journaux"
    journaux.mkdir(parents=True, exist_ok=True)
    for script in scripts or commun.SCRIPTS:
        with open(journaux / f"{lecteur}-{script}.txt", "w", encoding="utf-8") as journal:
            subprocess.run([sys.executable, "-I", str(ICI / "lancer.py"), lecteur, script],
                           stdout=journal, stderr=subprocess.STDOUT, timeout=3600)
        bilan = json.loads((commun.RESULTATS / lecteur / script / "_bilan.json").read_text(
            encoding="utf-8"))
        print(f"{lecteur} {script} : code {bilan['code']}, {bilan['duree']} s, "
              f"{len(bilan['ecrits'])} fichier(s), {bilan['appels_node']} appel(s) à node")


def _fichiers(dossier: Path) -> dict[str, Path]:
    return {str(f.relative_to(dossier)): f for f in dossier.rglob("*")
            if f.is_file() and f.name not in ("_bilan.json", "_erreurs.txt")}


#: Les scripts dont l'ordre d'une sortie change d'un lancement à l'autre, quel
#: que soit le lecteur : ``sre_jaune_pensions.py`` range ses incohérences par
#: un ensemble de chaînes, que chaque Python parcourt dans son ordre. Leurs
#: sorties se comparent à l'ordre près : les incohérences triées, les lignes
#: imprimées aussi.
ORDRE_VARIABLE = {"sre_jaune_pensions"}


def _pareils(script: str, a: Path, b: Path) -> bool:
    if filecmp.cmp(a, b, shallow=False):
        return True
    if script not in ORDRE_VARIABLE:
        return False
    if a.suffix == ".json":
        da, db = (json.loads(f.read_text(encoding="utf-8")) for f in (a, b))
        for donnees in (da, db):
            if isinstance(donnees, dict) and isinstance(donnees.get("incoherences"), list):
                donnees["incoherences"] = sorted(donnees["incoherences"])
        return da == db
    return sorted(a.read_text(encoding="utf-8").splitlines()) == sorted(
        b.read_text(encoding="utf-8").splitlines())


def comparer() -> None:
    for script in commun.SCRIPTS:
        py, js = commun.RESULTATS / "py" / script, commun.RESULTATS / "js" / script
        if not (py / "_bilan.json").exists() or not (js / "_bilan.json").exists():
            print(f"—      {script} : pas lu par les deux lecteurs")
            continue
        bp = json.loads((py / "_bilan.json").read_text(encoding="utf-8"))
        bj = json.loads((js / "_bilan.json").read_text(encoding="utf-8"))
        fp, fj = _fichiers(py), _fichiers(js)
        ecarts = sorted(n for n in set(fp) | set(fj)
                        if n not in fp or n not in fj or not _pareils(script, fp[n], fj[n]))
        if bp["code"] != bj["code"]:
            ecarts.append(f"code {bp['code']} ≠ {bj['code']}")
        print(f"{'pareil' if not ecarts else 'ÉCART '} {script} : {len(fp)} fichier(s), sortie "
              f"comprise{', à l’ordre près' if script in ORDRE_VARIABLE else ''} ; "
              f"py {bp['duree']} s, js {bj['duree']} s"
              + (f" ; écarts : {', '.join(ecarts)}" if ecarts else ""))


# -- les documents, niveau par niveau ---------------------------------------------


def _documents() -> dict[str, tuple[str, bytes]]:
    """Les PDF distincts des caches, par empreinte : (provenance, octets)."""
    vus: dict[str, tuple[str, bytes]] = {}
    for corps in sorted(commun.CACHE_RESEAU.glob("*.corps")):
        meta = corps.with_suffix(".json")
        octets = corps.read_bytes()
        if meta.exists() and octets.lstrip()[:5] == b"%PDF-":
            url = json.loads(meta.read_text(encoding="utf-8"))["url"]
            vus.setdefault(hashlib.sha1(octets).hexdigest(), (url, octets))
    for pdf in sorted((commun.ARBRE / "data" / "brut").rglob("*.pdf")):
        octets = pdf.read_bytes()
        vus.setdefault(hashlib.sha1(octets).hexdigest(), (str(pdf.relative_to(commun.ARBRE)), octets))
    return vus


def _table(table) -> dict:
    return {"largeur": table.largeur, "repli": table.repli,
            "codes": sorted([code, lettre] for code, lettre in table.items())}


def _lire_en_python(py, octets: bytes) -> dict:
    simples = {int(m.group(1)): m.group(2)
               for m in re.finditer(rb"(\d+)\s+0\s+obj\b(.*?)\bendobj", octets, re.S)}
    objets = py._objets(octets)
    flux = {n: f for n, f in ((n, py._flux(o)) for n, o in simples.items()) if f is not None}
    fragments = py._fragments(octets)
    tries = sorted(fragments, key=CLE)
    pages: dict[int, list] = {}
    for fragment in tries:
        pages.setdefault(fragment[0], []).append(fragment)
    return {
        "objets": {str(n): hashlib.sha1(o).hexdigest() for n, o in objets.items()},
        "flux": {str(n): hashlib.sha1(f).hexdigest() for n, f in flux.items()},
        "tables": {(str(n), nom.decode("latin-1")): _table(t)
                   for n, tables in py._polices_par_contenu(objets).items()
                   for nom, t in tables.items()},
        "communes": {nom.decode("latin-1"): _table(t) for nom, t in py._polices(octets).items()},
        "fragments": fragments,
        "lignes": py._assembler(tries, 3.0),
        "pages": [py._assembler(pages[p], 3.0) for p in sorted(pages)],
    }


def _regle_python(texte: str) -> str:
    """Ce que le Python fait d'une chaîne qu'il tient pour blanche."""
    if texte.strip() or not texte:
        return texte
    return " " if texte.strip(" \t\r\n\f\v") else " "


def _confronter(py, octets: bytes) -> dict:
    debut = time.perf_counter()
    p = _lire_en_python(py, octets)
    duree_py = time.perf_counter() - debut
    j = commun.demander(octets, "tout")
    duree_js = commun.APPELS[-1][1]
    j["tables"] = {(c, n): t for c, tables in j.pop("par_contenu").items() for n, t in tables.items()}
    niveaux = {n: p[n] == j[n] for n in ("objets", "flux", "tables", "communes", "lignes", "pages")}
    fj = [(int(a), int(b), float(c), float(d), e) for a, b, c, d, e in j["fragments"]]
    niveaux["fragments"] = p["fragments"] == fj
    blanches, autres, refaits = 0, 0, []
    if len(p["fragments"]) != len(fj):
        autres = abs(len(p["fragments"]) - len(fj)) or 1
    for x, y in zip(p["fragments"], fj):
        if x != y and x[:4] == y[:4] and not all(c in BLANCS_JS for c in y[4]) \
                and _regle_python(y[4]) == x[4]:
            blanches += 1
            y = y[:4] + (x[4],)
        elif x != y:
            autres += 1
        refaits.append(y)
    # Les fragments refaits sous la règle du Python, assemblés par le Python,
    # doivent redonner ses lignes : sinon l'écart a une autre cause.
    if py._assembler(sorted(refaits, key=CLE), 3.0) != p["lignes"]:
        autres += 1
    return {"niveaux": niveaux, "chaines_blanches": blanches, "autres_ecarts": autres,
            "python_s": round(duree_py, 2), "js_s": round(duree_js, 2),
            "pages": len(p["pages"]), "lignes": len(p["lignes"])}


def documents() -> None:
    py = commun.lecteur_python()
    sortie = (commun.TRAVAIL / "documents"
              / f"{commun.empreinte(commun.LECTEUR_PY)}-{commun.empreinte(commun.LECTEUR_JS)}")
    sortie.mkdir(parents=True, exist_ok=True)
    for cle, (provenance, octets) in _documents().items():
        chemin = sortie / f"{cle}.json"
        if not chemin.exists():
            try:
                bilan = _confronter(py, octets)
            except Exception as erreur:  # noqa: BLE001
                bilan = {"erreur": f"{type(erreur).__name__}: {erreur}"}
            bilan.update(provenance=provenance, taille=len(octets))
            chemin.write_text(json.dumps(bilan, ensure_ascii=False, indent=1), encoding="utf-8")
    total = {"documents": 0, "identiques": 0, "blanches": 0, "autres": 0, "py": 0.0, "js": 0.0}
    for chemin in sorted(sortie.glob("*.json")):
        b = json.loads(chemin.read_text(encoding="utf-8"))
        total["documents"] += 1
        if "erreur" in b:
            total["autres"] += 1
            print(f"ERREUR {b['provenance'][-70:]} : {b['erreur']}")
            continue
        differents = [n for n, pareil in b["niveaux"].items() if not pareil]
        total["identiques"] += not differents
        total["blanches"] += b["chaines_blanches"]
        total["autres"] += b["autres_ecarts"]
        total["py"] += b["python_s"]
        total["js"] += b["js_s"]
        print(f"{'pareil' if not differents else 'ÉCART '} {b['taille'] / 1e6:6.1f} Mo "
              f"{b['lignes']:6d} l.  py {b['python_s']:6.2f} s  js {b['js_s']:6.2f} s  "
              f"{b['provenance'][-55:]}"
              + (f"  [{', '.join(differents)} ; {b['chaines_blanches']} chaîne(s) blanche(s), "
                 f"{b['autres_ecarts']} autre(s)]" if differents else ""))
    print(f"{total['identiques']} document(s) identique(s) à tous les niveaux sur "
          f"{total['documents']} ; {total['blanches']} chaîne(s) blanche(s), "
          f"{total['autres']} écart(s) d'une autre cause ; lecture : py {total['py']:.1f} s, "
          f"js {total['js']:.1f} s")


def verifier() -> None:
    """``verifier_donnees.source_taux_avant_1967`` lit un PDF que
    ``sites_institutionnels.py`` a téléchargé dans la copie du dépôt."""
    os.chdir(commun.ARBRE)
    sys.path.insert(0, str(commun.ARBRE / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "verifier_donnees", commun.ARBRE / "scripts" / "verifier_donnees.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["verifier_donnees"] = module
    spec.loader.exec_module(module)
    import lecteur_site
    resultats = []
    for lecteur in (lecteur_site.py, lecteur_site):
        sys.modules["lecture_pdf"] = lecteur
        resultats.append(module.source_taux_avant_1967())
    print(f"verifier_donnees.source_taux_avant_1967 : {len(resultats[0])} valeur(s) en Python, "
          f"{len(resultats[1])} en JavaScript : "
          + ("identiques" if resultats[0] == resultats[1] else "DIFFÉRENTES"))


def main(arguments: list[str]) -> None:
    commande, *reste = arguments or ["tout"]
    if commande == "preparer":
        preparer("--neuf" in reste)
    elif commande == "passer":
        passer(reste[0], reste[1:])
    elif commande == "comparer":
        comparer()
    elif commande == "documents":
        documents()
    elif commande == "verifier":
        verifier()
    elif commande == "tout":
        passer("py", [])
        passer("js", [])
        comparer()
        documents()
        verifier()
    else:
        raise SystemExit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
