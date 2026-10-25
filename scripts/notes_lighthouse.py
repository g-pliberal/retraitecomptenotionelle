"""Les notes Lighthouse des dix routes du site, en mobile et au bureau
(feuille de route, action 174).

    python scripts/notes_lighthouse.py              # le site en ligne
    python scripts/notes_lighthouse.py --local      # l'arbre de travail, servi d'ici
    python scripts/notes_lighthouse.py --profils mobile --routes / /cout
    python scripts/notes_lighthouse.py --verifier   # sortie 1 si une note n'est pas pleine

Lighthouse n'est pas une dépendance du dépôt : ``npx`` le tire, à la version
que ``VERSION`` fige, la première fois qu'on le lance, et le garde dans son
cache. Les routes sont celles que ``tests/test_ecrans.py`` visite, et un test
les tient égales. Les audits se suivent un à un : en parallèle, leurs mesures
de performance se gêneraient. Chaque rapport est gardé en JSON sous
``.cache/lighthouse/``, et le résumé dit, par profil et par route, les cinq
notes, les cinq métriques, et les audits qui baissent une note.

Servi d'ici (``--local``), l'arbre se transfère compressé, comme GitHub Pages
le sert, mais en HTTP/1.1 : l'accessibilité, les bonnes pratiques, le SEO,
Agentic et le CLS valent ceux du site en ligne ; le reste de la performance
n'est qu'indicatif.
"""

from __future__ import annotations

import argparse
import contextlib
import dataclasses
import datetime
import functools
import gzip
import http.server
import io
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]

#: La version de Lighthouse que le dépôt fige : ``docs/outillage_interface.md``
#: la cite, et un test les tient d'accord.
VERSION = "13.5.0"

#: Le site en ligne, que la mesure lit sans autre indication.
EN_LIGNE = "https://g-pliberal.github.io/retraitecomptenotionelle/"

#: Les routes que ``tests/test_ecrans.py`` visite, dans son ordre : les neuf
#: pages, et les résultats du formulaire calculé tel qu'il s'ouvre.
RESULTATS = (
    "/simuler?unite_revenu=euros_mois&montants=brut&situation=actif"
    "&saisie_par=revenu&naissance=2000-01-01&liquidation=2064-01-01"
    "&debut=2021-01-01&statut=salarie_prive_non_cadre&salaire=3500"
    "&emploi_retraite_employeur=autre&sexe=H&profil=auto&primes=0&enfants=0"
    "&indexation=masse_salariale&lissage=1&table=unisexe&population=niveau_de_vie"
    "&rattachement=salaire&part_cotisation=salariale&contribution_etat=retraite_seule"
    "&foyer=seul&projection=cor_reference&esperance_vie=centrale&emploi=cor_2026"
    "&stock=prix&frais=paliers&taux=forwards&bascule=2026&euros=2026"
)
ROUTES = ["/", "/simuler", RESULTATS, "/cout", "/risque", "/partager",
          "/saviez-vous", "/cas-types", "/avantages", "/methode"]

#: Les deux profils : le mobile, celui de Lighthouse sans préréglage, et le
#: bureau, son préréglage ``desktop``.
PROFILS = ("mobile", "bureau")

#: Les catégories que Lighthouse note, dans l'ordre du tableau.
CATEGORIES = {"performance": "Perf.", "accessibility": "Access.",
              "best-practices": "B. P.", "seo": "SEO", "agentic-browsing": "Agentic"}

#: Les métriques de la performance, par l'audit qui les mesure.
METRIQUES = {"first-contentful-paint": "FCP", "largest-contentful-paint": "LCP",
             "total-blocking-time": "TBT", "cumulative-layout-shift": "CLS",
             "speed-index": "SI"}


@dataclasses.dataclass
class Releve:
    """Ce qu'un rapport dit d'une route : ses notes sur cent (``None`` quand le
    rapport manque), ses métriques, et les audits qui baissent une note —
    ``(catégorie, audit, élément fautif ou valeur)``."""

    profil: str
    route: str
    notes: dict[str, int | None] | None
    metriques: dict[str, str]
    defauts: list[tuple[str, str, str]]


def nom_de_route(route: str) -> str:
    """Le nom d'une route dans un fichier ou un tableau : ``accueil``,
    ``resultats`` pour le formulaire calculé, sinon son chemin."""
    if route == "/":
        return "accueil"
    if "?" in route:
        return "resultats"
    return route.strip("/")


def navigateur() -> str | None:
    """Le Chromium que Lighthouse lance : celui de ``CHROME_PATH``, puis celui
    de ``NAVIGATEUR`` (``tests/test_ecrans.py``), puis celui de Playwright que
    les sessions Claude Code préinstallent. Sans aucun, Lighthouse cherche un
    Chrome installé."""
    for variable in ("CHROME_PATH", "NAVIGATEUR"):
        if os.environ.get(variable):
            return os.environ[variable]
    for dossier in (os.environ.get("PLAYWRIGHT_BROWSERS_PATH"), "/opt/pw-browsers"):
        if dossier and Path(dossier).is_dir():
            trouves = sorted(Path(dossier).glob("chromium-*/chrome-linux*/chrome"))
            if trouves:
                return str(trouves[-1])
    return None


def commande(adresse: str, route: str, profil: str, sortie: Path) -> list[str]:
    """La ligne de commande d'un audit, Lighthouse tiré par ``npx`` à sa
    version figée."""
    drapeaux = "--headless=new"
    # Sous root, dans un conteneur, Chromium ne démarre pas dans son bac à sable.
    if getattr(os, "geteuid", lambda: 1)() == 0:
        drapeaux += " --no-sandbox"
    arguments = ["npx", "--yes", f"lighthouse@{VERSION}", f"{adresse}#{route}", "--quiet",
                 "--output=json", f"--output-path={sortie}", f"--chrome-flags={drapeaux}"]
    if profil == "bureau":
        arguments.append("--preset=desktop")
    return arguments


def _texte(valeur) -> str:
    """Une valeur affichée par Lighthouse, ses espaces insécables ordinaires."""
    return str(valeur).replace(" ", " ") if valeur is not None else ""


def _element(details) -> str:
    """Le premier élément fautif que nomment les détails d'un audit, à toute
    profondeur : l'arbre d'accessibilité les range dans des sections."""
    if isinstance(details, dict):
        noeud = details.get("node")
        if isinstance(noeud, dict) and noeud.get("selector"):
            return noeud["selector"]
        valeurs = details.values()
    elif isinstance(details, list):
        valeurs = details
    else:
        return ""
    for valeur in valeurs:
        trouve = _element(valeur)
        if trouve:
            return trouve
    return ""


def relever(rapport: dict, profil: str, route: str) -> Releve:
    """Les notes, les métriques et les audits pondérés en défaut d'un rapport.
    Un audit sans poids, ou sans objet, ne baisse aucune note : il est tu."""
    categories = rapport.get("categories", {})
    audits = rapport.get("audits", {})
    notes = {}
    for categorie in CATEGORIES:
        score = (categories.get(categorie) or {}).get("score")
        notes[categorie] = None if score is None else round(score * 100)
    metriques = {court: _texte(audits.get(audit, {}).get("displayValue")) or "—"
                 for audit, court in METRIQUES.items()}
    defauts = []
    for categorie in CATEGORIES:
        for reference in (categories.get(categorie) or {}).get("auditRefs", []):
            audit = audits.get(reference["id"], {})
            if reference.get("weight", 0) > 0 and audit.get("score") is not None \
                    and audit["score"] < 1:
                detail = _element(audit.get("details")) or _texte(audit.get("displayValue"))
                defauts.append((categorie, reference["id"], detail))
    return Releve(profil, route, notes, metriques, defauts)


def resumer(releves: list[Releve]) -> str:
    """Le tableau des notes, une ligne par profil et par route, puis les audits
    qui baissent une note."""
    entete = ["Profil", "Route", *CATEGORIES.values(), *METRIQUES.values()]
    lignes = ["| " + " | ".join(entete) + " |", "|" + "---|" * len(entete)]
    for releve in releves:
        debut = f"| {releve.profil} | {nom_de_route(releve.route)} |"
        if releve.notes is None:
            lignes.append(f"{debut} pas de rapport |")
            continue
        notes = ["—" if releve.notes[c] is None else str(releve.notes[c]) for c in CATEGORIES]
        mesures = [releve.metriques.get(court, "—") for court in METRIQUES.values()]
        lignes.append(f"{debut} " + " | ".join(notes + mesures) + " |")
    defauts = [f"- {releve.profil} {nom_de_route(releve.route)}, {categorie} : {audit}"
               + (f" ({detail})" if detail else "")
               for releve in releves for categorie, audit, detail in releve.defauts]
    lignes.append("")
    lignes.extend(["Ce qui baisse une note :", *defauts] if defauts
                  else ["Aucun audit pondéré en défaut."])
    return "\n".join(lignes)


def code_de_sortie(releves: list[Releve]) -> int:
    """1 dès qu'une note manque ou n'est pas pleine, sinon 0."""
    pleines = all(releve.notes is not None
                  and all(note == 100 for note in releve.notes.values())
                  for releve in releves)
    return 0 if pleines else 1


def auditer(adresse: str, profils, routes, dossier: Path,
            executer=subprocess.run) -> list[Releve]:
    """Chaque route sous chaque profil, un audit après l'autre ; chaque rapport
    rangé sous son profil, au nom de sa route. Un audit qui n'écrit rien
    laisse sa route sans notes."""
    environnement = dict(os.environ)
    chrome = navigateur()
    if chrome:
        environnement["CHROME_PATH"] = chrome
    releves = []
    for profil in profils:
        (dossier / profil).mkdir(parents=True, exist_ok=True)
        for route in routes:
            sortie = dossier / profil / f"{nom_de_route(route)}.json"
            sortie.unlink(missing_ok=True)
            print(f"{profil} {nom_de_route(route)}", file=sys.stderr, flush=True)
            executer(commande(adresse, route, profil, sortie), env=environnement,
                     capture_output=True, text=True, timeout=600, check=False)
            if sortie.exists():
                rapport = json.loads(sortie.read_text(encoding="utf-8"))
                releves.append(relever(rapport, profil, route))
            else:
                releves.append(Releve(profil, route, None, {}, []))
    return releves


class _Compresse(http.server.SimpleHTTPRequestHandler):
    """Un fichier texte compressé quand le navigateur le demande, comme GitHub
    Pages le sert ; tout le reste, tel quel."""

    COMPRESSIBLES = {".html", ".css", ".js", ".mjs", ".json", ".svg", ".txt", ".md"}

    def log_message(self, *args):
        pass

    def send_head(self):
        chemin = Path(self.translate_path(self.path))
        if chemin.is_dir() and self.path.split("?", 1)[0].endswith("/"):
            chemin = chemin / "index.html"
        if (chemin.suffix in self.COMPRESSIBLES and chemin.is_file()
                and "gzip" in self.headers.get("Accept-Encoding", "")):
            corps = gzip.compress(chemin.read_bytes())
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(str(chemin)))
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", str(len(corps)))
            self.end_headers()
            return io.BytesIO(corps)
        return super().send_head()


@contextlib.contextmanager
def servir(racine: Path):
    """L'arbre ``racine`` servi d'ici, le temps du bloc : rend son adresse."""
    serveur = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(_Compresse, directory=str(racine)))
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{serveur.server_address[1]}/"
    finally:
        serveur.shutdown()
        serveur.server_close()


def main(arguments=None) -> int:
    lecteur = argparse.ArgumentParser(
        description=__doc__.split("\n\n", 1)[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    source = lecteur.add_mutually_exclusive_group()
    source.add_argument("--adresse", default=EN_LIGNE,
                        help="le site à mesurer (sans autre indication : le site en ligne)")
    source.add_argument("--local", action="store_true",
                        help="l'arbre de travail, servi d'ici")
    lecteur.add_argument("--profils", nargs="+", choices=PROFILS, default=list(PROFILS))
    lecteur.add_argument("--routes", nargs="+", default=ROUTES, metavar="ROUTE")
    lecteur.add_argument("--dossier", type=Path,
                         help="où garder les rapports (sans autre indication : "
                              ".cache/lighthouse/<date>)")
    lecteur.add_argument("--verifier", action="store_true",
                         help="sortie 1 si une note manque ou n'est pas pleine")
    options = lecteur.parse_args(arguments)
    dossier = options.dossier or (RACINE / ".cache" / "lighthouse"
                                  / datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S"))
    with (servir(RACINE) if options.local else contextlib.nullcontext(options.adresse)) \
            as adresse:
        releves = auditer(adresse, options.profils, options.routes, dossier)
    print(resumer(releves))
    print(f"\nRapports : {dossier}")
    return code_de_sortie(releves) if options.verifier else 0


if __name__ == "__main__":
    sys.exit(main())
