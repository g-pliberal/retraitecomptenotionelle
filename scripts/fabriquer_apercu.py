#!/usr/bin/env python3
"""Dessine l'image d'aperçu de partage, ``moteur/apercu.png``.

    python scripts/fabriquer_apercu.py

Collée dans un réseau social ou une messagerie, l'adresse d'une page du site
s'affiche avec une image : celle-ci, la même pour les neuf pages, que
``moteur/page.html`` nomme en ``og:image`` (``IMAGE_APERCU``, dans
``moteur/js/gabarit.js``). C'est l'affiche de l'accueil, mise au format d'une
grande image d'aperçu, 1 200 × 630 points : le nom du site, le sur-titre et le
titre de l'accueil, la signature du pied de page, lus dans ``index.html`` tels
que la page les porte, avec les polices du dépôt et les couleurs du thème
sombre de ``moteur/style.css``. Rien n'y est écrit qui ne soit déjà sur le site.

L'image n'est pas refaite par ``regenerer.py`` : un PNG redessiné change avec la
version de Chromium et ne se compare pas octet à octet. On la refait à la main
quand le titre de l'accueil change, et ``TEXTE_APERCU``, son texte de
remplacement, avec elle ; ``tests/test_pages_en_dossier.py`` dit quand ce texte
ne porte plus le titre, et quand l'image n'a plus le format des réseaux.

Il ne faut qu'un Chromium ou un Chrome, cherché comme ``tests/test_ecrans.py``
le cherche : il dessine la page en mode sans tête (``--screenshot``), sans
bibliothèque.
"""

from __future__ import annotations

import base64
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
ACCUEIL = RACINE / "index.html"
FEUILLE = RACINE / "moteur" / "style.css"
POLICES = RACINE / "moteur" / "polices"
SORTIE = RACINE / "moteur" / "apercu.png"

#: Le format d'une grande image d'aperçu chez Facebook, LinkedIn et X.
LARGEUR, HAUTEUR = 1200, 630


def navigateur() -> str | None:
    """Un Chromium ou un Chrome : celui que désigne ``NAVIGATEUR``, celui des
    sessions Claude Code (``PLAYWRIGHT_BROWSERS_PATH``), ou le premier du
    système — la recherche de ``tests/test_ecrans.py``."""
    if os.environ.get("NAVIGATEUR"):
        return os.environ["NAVIGATEUR"]
    for dossier in (os.environ.get("PLAYWRIGHT_BROWSERS_PATH"), "/opt/pw-browsers"):
        if dossier and Path(dossier).is_dir():
            trouves = sorted(Path(dossier).glob("chromium-*/chrome-linux*/chrome"))
            if trouves:
                return str(trouves[-1])
    for nom in ("chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
                "chrome"):
        if shutil.which(nom):
            return shutil.which(nom)
    for chemin in (r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"):
        if Path(chemin).exists():
            return chemin
    return None


def _trouver(motif: str, texte: str, quoi: str) -> re.Match:
    trouve = re.search(motif, texte, re.S)
    if not trouve:
        raise SystemExit(f"{quoi} introuvable dans index.html : refaire les pages d'abord")
    return trouve


def textes() -> dict[str, str]:
    """Ce que l'image écrit, tel que l'accueil le porte : le nom du site, le
    sur-titre et le titre de l'affiche (balises comprises : le mot clé y reste en
    or), et la signature du pied, sans son lien."""
    page = ACCUEIL.read_text(encoding="utf-8")
    nom = _trouver(r'<p class="nom">.*?<span>(.*?)</span>', page, "le nom du site")
    affiche = _trouver(r'<div class="affiche"><p class="surtitre">(.*?)</p><h1>(.*?)</h1>',
                       page, "l'affiche")
    signature = _trouver(r'<p class="retour-site">(.*?)</p>', page, "la signature du pied")
    return {
        "nom": nom.group(1),
        "surtitre": affiche.group(1),
        "titre": affiche.group(2),
        "signature": html.escape(html.unescape(re.sub(r"<[^>]+>", "", signature.group(1)))),
    }


def couleurs() -> dict[str, str]:
    """Les couleurs du thème sombre, celui de l'affiche : le premier ``:root`` de
    la feuille de style."""
    racine = re.search(r":root\s*\{(.*?)\n\}", FEUILLE.read_text(encoding="utf-8"), re.S)
    if not racine:
        raise SystemExit("le premier :root de moteur/style.css est introuvable")
    teintes = {}
    for nom in ("fond", "texte", "texte-doux", "or"):
        trouve = re.search(rf"--{nom}:\s*(#[0-9a-fA-F]{{6}})\s*;", racine.group(1))
        if not trouve:
            raise SystemExit(f"--{nom} introuvable dans le premier :root de moteur/style.css")
        teintes[nom] = trouve.group(1)
    return teintes


def _police(fichier: str) -> str:
    """Une police du dépôt, en adresse ``data:`` : la page de l'image ne charge rien."""
    return "data:font/woff2;base64," + base64.b64encode((POLICES / fichier).read_bytes()).decode()


def page_de_l_image() -> str:
    """Le HTML que Chromium dessine : 1 200 × 630 points, l'affiche au milieu."""
    t, c = textes(), couleurs()
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><style>
@font-face {{ font-family: "Public Sans"; font-weight: 100 900; font-display: block;
  src: url({_police("public-sans-latin.woff2")}) format("woff2"); }}
@font-face {{ font-family: "Instrument Serif"; font-weight: 400; font-display: block;
  src: url({_police("instrument-serif-latin.woff2")}) format("woff2"); }}
html, body {{ margin: 0; width: {LARGEUR}px; height: {HAUTEUR}px; overflow: hidden; }}
body {{
  box-sizing: border-box; padding: 60px 76px 54px;
  display: flex; flex-direction: column; justify-content: space-between;
  background: {c["fond"]}; color: {c["texte"]};
  font-family: "Public Sans", sans-serif;
}}
.nom {{
  margin: 0; display: flex; align-items: center; gap: 14px;
  font-size: 21px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase;
}}
.nom::before {{ content: ""; width: 17px; height: 17px; background: {c["or"]}; }}
.surtitre {{
  margin: 0 0 22px; color: {c["or"]};
  font-size: 23px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase;
}}
h1 {{
  margin: 0; font-size: 96px; line-height: 0.92; font-weight: 900;
  letter-spacing: -0.045em; text-transform: uppercase; text-wrap: balance;
}}
.cle-texte {{ color: {c["or"]}; }}
.signature {{
  margin: 0; color: {c["texte-doux"]};
  font-family: "Instrument Serif", serif; font-size: 32px; line-height: 1;
}}
</style></head><body>
<p class="nom">{t["nom"]}</p>
<div><p class="surtitre">{t["surtitre"]}</p><h1>{t["titre"]}</h1></div>
<p class="signature">{t["signature"]}</p>
</body></html>
"""


def dessiner(sortie: Path = SORTIE) -> Path:
    """Fait dessiner l'image par Chromium, et l'écrit à ``sortie``."""
    chrome = navigateur()
    if chrome is None:
        raise SystemExit("aucun Chromium ni Chrome : NAVIGATEUR=/chemin/vers/chrome")
    with tempfile.TemporaryDirectory() as dossier:
        source = Path(dossier) / "apercu.html"
        source.write_text(page_de_l_image(), encoding="utf-8")
        image = Path(dossier) / "apercu.png"
        commande = [chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                    "--force-device-scale-factor=1", f"--window-size={LARGEUR},{HAUTEUR}",
                    "--virtual-time-budget=5000", f"--screenshot={image}", source.as_uri()]
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            commande.insert(1, "--no-sandbox")   # Chromium refuse root sans lui
        subprocess.run(commande, check=True, capture_output=True, timeout=120)
        sortie.write_bytes(image.read_bytes())
    return sortie


def main() -> int:
    chemin = dessiner()
    print(f"{chemin.relative_to(RACINE)} : {chemin.stat().st_size // 1024} Ko")
    return 0


if __name__ == "__main__":
    sys.exit(main())
