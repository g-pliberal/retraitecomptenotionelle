"""Fait tourner un script de la fabrique avec l'un des deux lecteurs (banc).

    python -I scripts/banc_lecture_pdf/lancer.py py|js <script> [arguments…]

``fabrique.py passer`` l'appelle, un processus par script. Le script tourne
dans la copie du dépôt, le réseau passe par le cache commun, et le lecteur
remplace ``lecture_pdf`` sous ses deux noms ; ce que le script écrit —
fichiers suivis, extraits de ``data/brut/`` — et ce qu'il imprime sont copiés
sous ``resultats/<lecteur>/<script>/``, puis la copie est remise en l'état,
ses caches de documents gardés.
"""
from __future__ import annotations

import json
import os
import runpy
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import commun  # noqa: E402

lecteur, script, *arguments = sys.argv[1:]
urllib.request.urlopen = commun.urlopen
# Le dépôt n'a que PyYAML : sites_institutionnels.py, qui préfère pypdf quand il
# le trouve, doit lire par le lecteur du dépôt, comme sur un poste ordinaire.
sys.modules["pypdf"] = None
if lecteur == "js":
    import lecteur_site as module  # noqa: E402
else:
    module = commun.lecteur_python()
# ``lecture_pdf`` depuis scripts/fetch, ``fetch.lecture_pdf`` depuis scripts
# (ccss_transferts_retraite.py) : les deux noms, ou l'un des scripts lit encore
# par l'autre lecteur.
sys.modules["lecture_pdf"] = sys.modules["fetch.lecture_pdf"] = module


class Copie:
    """Ce que le script imprime, gardé pour être comparé d'un lecteur à l'autre."""

    def __init__(self, flux):
        self.flux, self.lu = flux, []

    def write(self, texte):
        self.lu.append(texte)
        return self.flux.write(texte)

    def flush(self):
        self.flux.flush()

    def __getattr__(self, nom):
        return getattr(self.flux, nom)


sys.stdout, sys.stderr = Copie(sys.stdout), Copie(sys.stderr)
os.chdir(commun.ARBRE)
sys.path.insert(0, str(commun.ARBRE / "scripts" / "fetch"))
sys.argv = [str(commun.ARBRE / "scripts" / "fetch" / f"{script}.py"), *arguments]
debut, horloge = time.time(), time.perf_counter()
try:
    runpy.run_path(sys.argv[0], run_name="__main__")
    code = 0
except SystemExit as fin:
    code = fin.code if isinstance(fin.code, int) else (0 if fin.code is None else 1)
duree = time.perf_counter() - horloge

dest = commun.RESULTATS / lecteur / script
shutil.rmtree(dest, ignore_errors=True)
dest.mkdir(parents=True)
ecrits = []
etat = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True,
                      cwd=commun.ARBRE).stdout.splitlines()
for ligne in etat:
    chemin = ligne[3:].strip('"')
    if (commun.ARBRE / chemin).is_file():
        (dest / chemin).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(commun.ARBRE / chemin, dest / chemin)
        ecrits.append(chemin)
for extrait in sorted((commun.ARBRE / "data" / "brut").rglob("*")):
    if extrait.suffix in (".json", ".txt") and extrait.stat().st_mtime >= debut:
        relatif = extrait.relative_to(commun.ARBRE)
        (dest / relatif).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(extrait, dest / relatif)
        ecrits.append(str(relatif))
subprocess.run(["git", "checkout", "-q", "--", "."], cwd=commun.ARBRE, check=True)
subprocess.run(["git", "clean", "-fdq"], cwd=commun.ARBRE, check=True)
(dest / "_sortie.txt").write_text("".join(sys.stdout.lu), encoding="utf-8")
(dest / "_erreurs.txt").write_text("".join(sys.stderr.lu), encoding="utf-8")
bilan = {"code": code, "duree": round(duree, 1), "ecrits": ecrits,
         "appels_node": len(commun.APPELS)}
(dest / "_bilan.json").write_text(json.dumps(bilan, ensure_ascii=False, indent=1),
                                  encoding="utf-8")
