"""Le banc du lecteur PDF : ce que ses scripts partagent (action 161, étape 4).

Outil provisoire, à retirer avec le cœur Python du lecteur, à la fin de
l'étape 4 : il confronte ``scripts/fetch/lecture_pdf.py`` et
``moteur/js/lecture-pdf.js`` tels qu'ils sont sur le disque, de sorte qu'un
correctif se mesure avant d'être commité (``fabrique.py`` dit comment).

Tout ce qu'il écrit va dans un dossier de travail hors du dépôt,
``$BANC_LECTURE_PDF`` (``/tmp/banc_lecture_pdf`` par défaut) : une copie du
dépôt où tournent les scripts de la fabrique, le cache des téléchargements,
les réponses de node, les résultats. Aucun document n'entre dans le dépôt :
leurs licences ne permettent pas toutes de les republier.
"""
from __future__ import annotations

import email
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[2]
ICI = Path(__file__).resolve().parent
TRAVAIL = Path(os.environ.get("BANC_LECTURE_PDF", "/tmp/banc_lecture_pdf"))
ARBRE = TRAVAIL / "arbre"
RESULTATS = TRAVAIL / "resultats"
LECTEUR_PY = DEPOT / "scripts" / "fetch" / "lecture_pdf.py"
LECTEUR_JS = DEPOT / "moteur" / "js" / "lecture-pdf.js"

#: Les scripts de la fabrique qui lisent des PDF et ont un ``main``.
#: ``sre_jaune_referents.py`` passe par ``sre_jaune_pensions.py`` ;
#: ``estimation_officielle.py`` lit le relevé d'une personne, que le banc n'a
#: pas ; ``verifier_donnees.py`` a sa commande, ``fabrique.py verifier``.
SCRIPTS = (
    "cnbf_baremes", "contribution_employeur_public", "dgfip_brochure_impot",
    "dgtresor_trajectoires_smic", "pap_plf_2026", "sites_institutionnels",
    "sre_jaune_pensions", "cnavpl_recueils", "ccss_impots_retraite", "ccss_regimes",
    "ccss_transferts_retraite",
)

#: Les fonctions internes du lecteur du site, exportées dans sa copie de banc.
EXPORTS = ("\n// Banc seulement : les fonctions internes, pour les confronter au Python.\n"
           "export { fragments, trier, assembler, lireObjets, polices, policesParContenu };\n")


def empreinte(chemin: Path) -> str:
    return hashlib.sha1(chemin.read_bytes()).hexdigest()[:12]


def lecteur_python():
    """Le lecteur Python tel qu'il est sur le disque, chargé sous un nom à lui."""
    spec = importlib.util.spec_from_file_location("lecture_pdf_du_banc", LECTEUR_PY)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dossier_js() -> Path:
    """La copie de banc du lecteur du site et son pont, une par version du
    lecteur : les réponses gardées en cache ne servent qu'à la version qui
    les a rendues."""
    dossier = TRAVAIL / "js" / empreinte(LECTEUR_JS)
    if not (dossier / "pont.mjs").exists():
        dossier.mkdir(parents=True, exist_ok=True)
        (dossier / "lecture-pdf-banc.mjs").write_text(
            LECTEUR_JS.read_text(encoding="utf-8") + EXPORTS, encoding="utf-8")
        shutil.copy2(ICI / "pont.mjs", dossier / "pont.mjs")
    return dossier


#: Chaque question posée à node : (question, durée de la lecture en secondes).
APPELS: list[tuple[str, float]] = []


def demander(octets: bytes, quoi: str, tolerance: float = 3.0):
    """Ce que le lecteur du site rend d'un PDF (``pont.mjs`` dit les questions)."""
    dossier = dossier_js()
    cle = hashlib.sha1(octets).hexdigest()
    pdf = TRAVAIL / "pdf" / f"{cle}.pdf"
    if not pdf.exists():
        pdf.parent.mkdir(parents=True, exist_ok=True)
        pdf.write_bytes(octets)
    sortie = dossier / "reponses" / f"{cle}-{quoi}-{tolerance}.json"
    if not sortie.exists():
        sortie.parent.mkdir(exist_ok=True)
        subprocess.run(["node", str(dossier / "pont.mjs"), str(pdf), quoi, str(tolerance),
                        str(sortie)], check=True)
    reponse = json.loads(sortie.read_text(encoding="utf-8"))
    APPELS.append((quoi, reponse["duree"]))
    return reponse["rendu"]


# -- le cache des téléchargements ----------------------------------------------

CACHE_RESEAU = TRAVAIL / "cache_reseau"
_URLOPEN = urllib.request.urlopen


class Reponse(io.BytesIO):
    """Une réponse HTTP gardée : ce que les scripts en lisent."""

    def __init__(self, corps: bytes, statut: int, entetes: str, url: str):
        super().__init__(corps)
        self.status = self.code = statut
        self.headers = self.msg = email.message_from_string(entetes)
        self.url = url

    def getcode(self) -> int:
        return self.status

    def geturl(self) -> str:
        return self.url

    def info(self):
        return self.headers


def urlopen(demande, data=None, timeout=None, **options):
    """``urllib.request.urlopen``, dont la première réponse à une adresse — ou
    son erreur HTTP — est gardée, puis rejouée : les deux lecteurs lisent les
    mêmes octets. Une panne du réseau, elle, n'est pas gardée."""
    est_requete = isinstance(demande, urllib.request.Request)
    url = demande.full_url if est_requete else demande
    donnees = demande.data if est_requete else data
    cle = hashlib.sha1((url + "\0" + (donnees or b"").hex()).encode()).hexdigest()
    meta, corps = CACHE_RESEAU / f"{cle}.json", CACHE_RESEAU / f"{cle}.corps"
    if not meta.exists():
        CACHE_RESEAU.mkdir(parents=True, exist_ok=True)
        appel = {"data": data, **options}
        if timeout is not None:
            appel["timeout"] = timeout
        try:
            with _URLOPEN(demande, **appel) as reponse:
                corps.write_bytes(reponse.read())
                meta.write_text(json.dumps({
                    "url": url, "statut": reponse.status, "entetes": str(reponse.headers),
                    "finale": reponse.geturl()}), encoding="utf-8")
        except urllib.error.HTTPError as erreur:
            meta.write_text(json.dumps({"url": url, "erreur": erreur.code,
                                        "raison": str(erreur.reason),
                                        "entetes": str(erreur.headers)}), encoding="utf-8")
    lu = json.loads(meta.read_text(encoding="utf-8"))
    if "erreur" in lu:
        raise urllib.error.HTTPError(url, lu["erreur"], lu["raison"],
                                     email.message_from_string(lu["entetes"]), io.BytesIO(b""))
    return Reponse(corps.read_bytes(), lu["statut"], lu["entetes"], lu["finale"])
