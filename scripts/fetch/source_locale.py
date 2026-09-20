#!/usr/bin/env python3
"""Lire un document déposé à la main quand la source refuse la session.

    python scripts/fetch/source_locale.py              # les sources bloquées, et où est leur fichier
    python scripts/fetch/source_locale.py --recuperer  # les télécharge depuis leurs miroirs dans data/brut/
    python scripts/fetch/source_locale.py --publier    # (workflow) dépose les documents sans miroir sur la release
    python scripts/fetch/erafp_valeurs_point.py --fichier ~/Téléchargements/RAFP-Evolution-valeurs-point.pdf

Certaines sources ne se laissent pas lire depuis l'environnement où ce dépôt
est construit, et ce n'est pas une panne : ``budget.gouv.fr`` répond 403 aux
adresses de sortie du proxy, la Banque de France refuse ses PDF aux clients qui
ne sont pas un navigateur, Légifrance refuse les requêtes automatisées. Un
navigateur sur un poste ordinaire, lui, passe. Le dépôt ne maquille pas ses
signaux d'automatisation pour forcer un refus (voir
``docs/outillage_interface.md``) ; il prévoit à la place que le document soit
**apporté** : téléchargé ailleurs, déposé dans ``data/brut/``, et lu de là.

**LE MIROIR D'ABORD, ET IL SUFFIT LE PLUS SOUVENT.** Les annexes budgétaires
que ``budget.gouv.fr`` refuse sont déposées au Parlement, et l'Assemblée
nationale sert le même fichier, octet pour octet, à qui le demande : le jaune
pensions et les projets annuels de performances du PLF 2026 s'y téléchargent
depuis une session. Le manifeste porte cette adresse sous ``miroir``, et
l'empreinte SHA-256 du document sous ``sha256`` : ``--recuperer`` télécharge
chaque miroir dans ``data/brut/``, refuse un fichier dont l'empreinte diffère
— une édition qui aurait changé sans le dire —, et un récupérateur qui reçoit
``miroir=`` l'essaie avant l'adresse d'origine. Rien à apporter, personne à
solliciter : c'est le cas qu'on vise, et le reste n'est que le repli.

**SANS MIROIR PUBLIC, LE DÉPÔT SE FAIT SON PROPRE MIROIR.** Le rapport de
l'OPEF n'est servi que par la Banque de France, qui répond 403 à toute
requête qui n'est pas un navigateur, et aucun autre site public ne le
reprend. ``--publier`` est le pas de plus : sur un runner GitHub Actions
(``.github/workflows/documents-apportes.yml``, à la main ou chaque mois), il
télécharge chaque jeu ``blocage: refus`` qui n'a pas de miroir depuis son
adresse de document — ``document`` dans le manifeste quand ``url`` est une
page, sinon ``url`` —, d'abord par une requête simple sous l'identité du
dépôt, puis, si le site la refuse, avec un Chromium Playwright headless
ordinaire, sans rien maquiller (le site veut un navigateur ; en être un
n'est pas se déguiser, voir ``docs/outillage_interface.md``). Il dépose le
fichier sur la release ``documents-apportes`` du dépôt, remplace l'asset du
même nom, et écrit dans le corps de la release une ligne par document avec
son empreinte SHA-256 et sa date. L'adresse de l'asset devient alors le
``miroir`` du jeu, avec son ``sha256``, et ``--recuperer`` le rapporte dans
une session comme n'importe quel miroir. Le jeton d'un workflow a le droit
d'écrire les releases ; celui d'une session ne l'a pas, mais il télécharge
un asset. Un document dont le manifeste porte déjà l'empreinte n'est pas
remplacé par un fichier qui en porte une autre : le site a changé d'édition,
et c'est un écart à lire, pas à propager.

Trois gestes, et le manifeste qui les relie :

* ``data/sources.yaml`` porte un champ ``blocage`` sur chaque jeu qu'une
  session ne peut pas atteindre, avec la nature du refus. Ce script, lancé sans
  argument, en imprime la liste et, pour chacun, le chemin où le fichier est
  attendu.
* ``--recuperer`` télécharge dans ``data/brut/`` tout jeu bloqué qui a un
  ``miroir``, vérifie son empreinte, et ne refait rien pour un fichier déjà là
  et conforme.
* Les récupérateurs qui lisent un document appellent ``lire_ou_telecharger``
  au lieu d'ouvrir l'adresse directement. La fonction lit d'abord le fichier
  passé en ``--fichier``, sinon ``data/brut/<dernier segment de l'adresse>``
  s'il existe, puis le miroir s'il y en a un, et l'adresse d'origine en
  dernier. Le nom attendu est donc celui
  du fichier tel que le site le sert, sans le renommer. Quand l'adresse ne
  nomme pas le fichier — ``file-download/31546``, ``?wpdmdl=263987`` —, le
  récupérateur passe le nom qu'il attend (``nom_local``), et le manifeste le
  déclare sous ``fichier_local``.

``data/brut/`` n'est pas versionné : un document qui y est déposé sert à la
session qui l'a reçu, et à elle seule. Ce que le récupérateur en tire — les
valeurs promues dans ``data/reference/`` — l'est. Une valeur lue depuis un
fichier apporté vaut ce que vaut sa lecture, comme une valeur téléchargée : le
script qui la lit applique les mêmes contrôles, et c'est le manifeste qui dit,
par ``statut_integration``, si un script la revérifie.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit

RACINE = Path(__file__).resolve().parents[2]
BRUT = RACINE / "data" / "brut"
MANIFESTE = RACINE / "data" / "sources.yaml"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: La release du dépôt où ``--publier`` dépose les documents sans miroir, et
#: d'où ``--recuperer`` les rapporte. Même dépôt que l'index DILA.
DEPOT = "g-pliberal/retraitecomptenotionelle"
ETIQUETTE = "documents-apportes"

#: Les codes HTTP par lesquels un site dit « pas vous » à une requête simple,
#: et après lesquels ``--publier`` essaie en navigateur. Un 404 n'en est pas
#: un : le document n'est pas là, un navigateur ne le trouvera pas davantage.
REFUS = {401, 403, 406, 429, 503}

#: Les natures de blocage que le manifeste admet, et ce que chacune veut dire.
#: Un jeu sans champ ``blocage`` est joignable depuis une session.
BLOCAGES = {
    "refus": (
        "le site refuse les requêtes venant d'une session — 403, page "
        "anti-robot, PDF réservé aux navigateurs — alors qu'un navigateur sur "
        "un poste ordinaire passe : le document est à apporter"
    ),
    "reseau": (
        "le site n'est pas joignable depuis l'environnement où le dépôt est "
        "construit ; limite de la machine, pas de la source"
    ),
    "convention": (
        "l'accès demande une clé, un compte ou une convention ; rien à "
        "apporter, la donnée ne peut pas entrer dans le dépôt telle quelle"
    ),
}


def nom_du_document(url: str) -> str | None:
    """Le nom sous lequel un navigateur enregistrerait ce que sert l'adresse.

    Le dernier segment du chemin, décodé, s'il porte une extension ; sinon
    rien — ``file-download/31546`` ou ``documents/?wpdmdl=263987`` ne nomment
    pas leur fichier, et c'est au manifeste de le faire (``fichier_local``).
    """
    nom = unquote(urlsplit(url).path.rstrip("/").rsplit("/", 1)[-1])
    if not nom or "." not in nom or nom.rsplit(".", 1)[-1].isdigit():
        return None
    return nom


def chemin_local(url: str, nom_local: str | None = None) -> Path:
    """Où ``data/brut/`` attend le document servi à cette adresse.

    ``nom_local`` l'emporte quand il est donné ; sinon le nom que l'adresse
    porte, et c'est ce qu'on demande à qui l'apporte — le déposer sous ce
    nom, pas le renommer.
    """
    nom = nom_local or nom_du_document(url)
    if not nom:
        raise ValueError(f"l'adresse ne nomme pas de fichier, et aucun nom "
                         f"local n'est donné : {url}")
    if "/" in nom or nom in (".", ".."):
        raise ValueError(f"un nom local est un nom de fichier, pas un chemin : {nom}")
    return BRUT / nom


def telecharger(url: str) -> bytes:
    """Le téléchargement le plus simple, sous l'identité du dépôt."""
    requete = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=300) as reponse:
        return reponse.read()


def empreinte(octets: bytes) -> str:
    return hashlib.sha256(octets).hexdigest()


def _controler(octets: bytes, sha256: str | None, provenance: str) -> bytes:
    if sha256 and empreinte(octets) != sha256:
        raise ValueError(
            f"{provenance} : empreinte {empreinte(octets)[:12]}…, le manifeste "
            f"attend {sha256[:12]}… — le document a changé, ou ce n'est pas lui")
    return octets


def lire_ou_telecharger(url: str, telecharger: Callable[[str], bytes],
                        fichier: Path | str | None = None, *,
                        nom_local: str | None = None,
                        miroir: str | None = None,
                        sha256: str | None = None,
                        sortie=sys.stderr) -> bytes:
    """Le document : du fichier demandé, sinon de ``data/brut/``, sinon du
    miroir, sinon du site.

    ``telecharger`` n'est appelé que si aucun fichier local ne répond. Le
    chemin lu est écrit sur ``sortie`` pour qu'un journal de récupération
    dise d'où vient ce qu'il a lu. Une adresse qui ne nomme pas son fichier
    et un récupérateur qui ne donne pas ``nom_local`` : rien n'est cherché
    en local, on télécharge. Quand ``sha256`` est donné, ce qui est lu, d'où
    que ce soit, doit le porter.
    """
    if fichier is not None:
        chemin = Path(fichier)
        print(f"lu depuis {chemin}, sans téléchargement : {url}", file=sortie)
        return _controler(chemin.read_bytes(), sha256, str(chemin))
    try:
        local = chemin_local(url, nom_local)
    except ValueError:
        local = None
    if local is not None and local.is_file():
        print(f"lu depuis {local.relative_to(RACINE)}, sans téléchargement : {url}",
              file=sortie)
        return _controler(local.read_bytes(), sha256, str(local.relative_to(RACINE)))
    if miroir:
        print(f"téléchargé depuis le miroir {miroir}", file=sortie)
        return _controler(telecharger(miroir), sha256, miroir)
    return _controler(telecharger(url), sha256, url)


def option_fichier(analyseur: argparse.ArgumentParser) -> None:
    """L'option ``--fichier`` d'un récupérateur qui lit un seul document."""
    analyseur.add_argument(
        "--fichier", type=Path, metavar="CHEMIN", default=None,
        help="lire le document depuis ce fichier au lieu de le télécharger "
             "(source apportée à la main ; voir data/sources.yaml, champ blocage)",
    )


def jeux_bloques(manifeste: Path = MANIFESTE) -> list[dict]:
    """Les jeux du manifeste qu'une session ne peut pas atteindre."""
    import yaml

    with manifeste.open(encoding="utf-8") as flux:
        institutions = yaml.safe_load(flux)["institutions"]
    bloques = []
    for cle, institution in institutions.items():
        for jeu in institution.get("jeux", []):
            if "blocage" not in jeu:
                continue
            bloques.append({
                "institution": cle,
                "id": jeu["id"],
                "titre": " ".join(str(jeu.get("titre", "")).split()),
                "url": jeu["url"],
                "blocage": jeu["blocage"],
                "fichier_local": jeu.get("fichier_local"),
                "document": jeu.get("document"),
                "miroir": jeu.get("miroir"),
                "sha256": jeu.get("sha256"),
                "statut_integration": jeu.get("statut_integration"),
                "recuperation": jeu.get("recuperation"),
            })
    return bloques


def ou_deposer(jeu: dict) -> Path | None:
    """Le chemin où un jeu bloqué attend son document, s'il en vise un."""
    if jeu["blocage"] == "convention":
        return None
    try:
        return chemin_local(jeu["url"], jeu.get("fichier_local"))
    except ValueError:
        return None


def adresse_du_document(jeu: dict) -> str | None:
    """L'adresse directe du fichier : ``document`` quand le manifeste le
    donne (``url`` est alors la page qui le présente), sinon ``url`` si elle
    nomme un fichier. Rien quand le jeu ne vise pas un fichier."""
    if jeu.get("document"):
        return jeu["document"]
    if nom_du_document(jeu["url"]):
        return jeu["url"]
    return None


def url_publiee(nom: str) -> str:
    """L'asset de la release ``documents-apportes`` qui porte ce nom."""
    return f"https://github.com/{DEPOT}/releases/download/{ETIQUETTE}/{quote(nom)}"


def est_publie_ici(miroir: str | None) -> bool:
    return bool(miroir) and miroir.startswith(url_publiee(""))


def a_publier(jeux: list[dict]) -> list[dict]:
    """Les jeux que ``--publier`` prend en charge : refusés à la session,
    visant un fichier nommé, dont l'adresse de document est connue, et sans
    autre miroir que la release du dépôt."""
    return [
        jeu for jeu in jeux
        if jeu["blocage"] == "refus" and ou_deposer(jeu) is not None
        and adresse_du_document(jeu) is not None
        and (not jeu.get("miroir") or est_publie_ici(jeu["miroir"]))
    ]


class NavigateurRequis(RuntimeError):
    """Le site refuse la requête simple, et aucun navigateur n'est disponible."""


def telecharger_par_navigateur(page: str, document: str) -> bytes:
    """Le document, obtenu comme un navigateur l'obtiendrait.

    Un Chromium Playwright headless ordinaire : rien n'est maquillé, ni le
    User-Agent (qui dit « HeadlessChrome »), ni les signaux d'automatisation.
    Le site veut un navigateur, en voici un. On ouvre d'abord la page qui
    présente le document, pour que le site y pose ce qu'il pose, puis on
    demande le fichier depuis cet onglet — par une requête du contexte,
    qui porte ses cookies, et sinon par une navigation qui devient un
    téléchargement.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        navigateur = pw.chromium.launch()
        contexte = navigateur.new_context(accept_downloads=True)
        onglet = contexte.new_page()
        try:
            if page != document:
                try:
                    onglet.goto(page, wait_until="load", timeout=90_000)
                except Exception as erreur:  # noqa: BLE001 — la page n'est qu'un préalable
                    print(f"page {page} : {erreur.__class__.__name__}, on demande le "
                          "document directement", file=sys.stderr)
            reponse = onglet.request.get(document, timeout=180_000)
            if reponse.ok and not reponse.headers.get("content-type", "").startswith("text/html"):
                return reponse.body()
            print(f"{document} : {reponse.status} à la requête du contexte, on navigue",
                  file=sys.stderr)
            with onglet.expect_download(timeout=180_000) as attente:
                try:
                    onglet.goto(document, timeout=180_000)
                except Exception:  # noqa: BLE001 — Chromium annule la navigation devenue téléchargement
                    pass
            return Path(attente.value.path()).read_bytes()
        finally:
            navigateur.close()


def telecharger_document(jeu: dict, telecharger: Callable[[str], bytes] = telecharger,
                         navigateur: Callable[[str, str], bytes] | None = telecharger_par_navigateur,
                         *, sortie=sys.stderr) -> tuple[bytes, str]:
    """Le document d'un jeu et la voie qui l'a obtenu : ``requête simple``
    sous l'identité du dépôt, ou ``navigateur`` quand le site a refusé la
    première par un code de ``REFUS``. Toute autre erreur remonte telle
    quelle ; un refus sans navigateur lève ``NavigateurRequis``."""
    adresse = adresse_du_document(jeu)
    if adresse is None:
        raise ValueError(f"{jeu['id']} : aucune adresse de document (ni document, ni url nommant un fichier)")
    try:
        return telecharger(adresse), "requête simple"
    except urllib.error.HTTPError as erreur:
        if erreur.code not in REFUS:
            raise
        print(f"{jeu['id']} : {erreur.code} à la requête simple sur {adresse}", file=sortie)
    if navigateur is None:
        raise NavigateurRequis(f"{jeu['id']} : le site veut un navigateur, et il n'y en a pas")
    return navigateur(jeu["url"], adresse), "navigateur"


def _github(methode: str, url: str, jeton: str, donnees=None,
            type_contenu: str = "application/json", longueur: int | None = None):
    """La mécanique de ``dila_index.py``, reprise telle quelle."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import dila_index

    return dila_index._github(methode, url, jeton, donnees, type_contenu, longueur)


def _ligne_release(nom: str, sha256: str, taille: int, adresse: str, voie: str) -> str:
    return (f"- `{nom}` : sha256 `{sha256}`, {taille / 1e6:.1f} Mo, téléchargé le "
            f"{time.strftime('%Y-%m-%d')} depuis {adresse} ({voie}).")


def publier(jeux: list[dict], telecharger: Callable[[str], bytes] = telecharger,
            navigateur: Callable[[str, str], bytes] | None = telecharger_par_navigateur,
            *, jeton: str | None = None, sortie=sys.stdout) -> dict[str, str]:
    """Dépose sur la release ``documents-apportes`` chaque jeu de ``a_publier``.

    Rend l'état de chaque jeu : ``publie``, ``ecart`` (le manifeste porte une
    empreinte et le site sert autre chose : l'asset n'est pas touché),
    ``navigateur`` (refusé, et aucun navigateur pour insister) ou ``echec``.
    L'asset du même nom est remplacé ; la ligne du corps de la release qui le
    décrit aussi. Il faut un jeton qui écrive les releases : celui d'un
    workflow GitHub Actions.
    """
    jeton = jeton or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not jeton:
        raise RuntimeError("GH_TOKEN ou GITHUB_TOKEN absent : impossible de publier")
    candidats = a_publier(jeux)
    etats: dict[str, str] = {}
    obtenus: list[tuple[dict, bytes, str]] = []
    for jeu in candidats:
        try:
            octets, voie = telecharger_document(jeu, telecharger, navigateur, sortie=sortie)
        except NavigateurRequis as erreur:
            print(f"{jeu['id']} : NAVIGATEUR REQUIS — {erreur}", file=sortie)
            etats[jeu["id"]] = "navigateur"
            continue
        except Exception as erreur:  # noqa: BLE001 — un jeu en échec n'empêche pas les autres
            print(f"{jeu['id']} : ÉCHEC — {erreur.__class__.__name__}: {erreur}", file=sortie)
            etats[jeu["id"]] = "echec"
            continue
        if jeu.get("sha256") and empreinte(octets) != jeu["sha256"]:
            print(f"{jeu['id']} : ÉCART — le site sert {empreinte(octets)[:12]}…, le manifeste "
                  f"attend {jeu['sha256'][:12]}… ; l'asset publié n'est pas remplacé, "
                  "l'édition a changé et c'est à lire", file=sortie)
            etats[jeu["id"]] = "ecart"
            continue
        obtenus.append((jeu, octets, voie))
    if not obtenus:
        return etats

    api = f"https://api.github.com/repos/{DEPOT}"
    try:
        release = _github("GET", f"{api}/releases/tags/{ETIQUETTE}", jeton)
    except urllib.error.HTTPError as erreur:
        if erreur.code != 404:
            raise
        release = _github("POST", f"{api}/releases", jeton, json.dumps({
            "tag_name": ETIQUETTE, "name": "Documents que leur site refuse à une session",
            "body": "Déposés par `scripts/fetch/source_locale.py --publier` depuis le workflow "
                    "`documents-apportes.yml`, tels que le site les sert. Le manifeste "
                    "`data/sources.yaml` les déclare en `miroir` avec leur `sha256` ; "
                    "récupération : `python scripts/fetch/source_locale.py --recuperer`.",
        }).encode())
    corps = release.get("body") or ""
    for jeu, octets, voie in obtenus:
        nom = ou_deposer(jeu).name
        for actif in release.get("assets", []):
            if actif["name"] == nom:
                _github("DELETE", actif["url"], jeton)
        envoi = release["upload_url"].split("{")[0] + f"?name={quote(nom)}"
        type_contenu = mimetypes.guess_type(nom)[0] or "application/octet-stream"
        actif = _github("POST", envoi, jeton, octets, type_contenu, len(octets))
        ligne = _ligne_release(nom, empreinte(octets), len(octets), adresse_du_document(jeu), voie)
        corps = re.sub(rf"\n- `{re.escape(nom)}`[^\n]*", "", "\n" + corps).lstrip("\n")
        corps = corps.rstrip() + "\n" + ligne
        print(f"{jeu['id']} : {nom} publié, {len(octets) / 1e6:.1f} Mo, sha256 "
              f"{empreinte(octets)}, {voie} — {actif.get('browser_download_url') or url_publiee(nom)}",
              file=sortie)
        etats[jeu["id"]] = "publie"
    _github("PATCH", release["url"], jeton, json.dumps({"body": corps}).encode())
    return etats


def recuperer(jeux: list[dict], telecharger: Callable[[str], bytes] = telecharger,
              *, sortie=sys.stdout) -> list[Path]:
    """Télécharge dans ``data/brut/`` chaque jeu bloqué qui a un miroir.

    Un fichier déjà présent et conforme à son empreinte n'est pas retéléchargé ;
    un fichier présent dont l'empreinte diffère est remplacé, et le
    remplacement est dit. Un miroir dont le contenu ne porte pas l'empreinte
    attendue n'est pas écrit : on ne dépose pas dans ``data/brut/`` ce qu'on
    ne reconnaît pas. Un jeu que ``--publier`` prend en charge et qui n'a pas
    encore de miroir déclaré est cherché sur la release du dépôt, sans
    empreinte à opposer : ce qui est écrit le dit, avec l'empreinte reçue, à
    inscrire dans le manifeste. Rend les chemins écrits ou confirmés.
    """
    faits: list[Path] = []
    for jeu in jeux:
        cible = ou_deposer(jeu)
        if cible is None:
            continue
        miroir = jeu.get("miroir")
        declare = bool(miroir)
        if not miroir and a_publier([jeu]):
            miroir = url_publiee(cible.name)
        if not miroir:
            continue
        relatif = cible.relative_to(RACINE) if cible.is_relative_to(RACINE) else cible
        if cible.is_file() and (not jeu.get("sha256")
                                or empreinte(cible.read_bytes()) == jeu["sha256"]):
            print(f"{jeu['id']} : {relatif} déjà là, conforme", file=sortie)
            faits.append(cible)
            continue
        try:
            octets = _controler(telecharger(miroir), jeu.get("sha256"), miroir)
        except (OSError, ValueError) as erreur:
            if not declare and isinstance(erreur, urllib.error.HTTPError) and erreur.code == 404:
                print(f"{jeu['id']} : rien sur la release {ETIQUETTE} — lancer le workflow "
                      "documents-apportes.yml (onglet Actions, « Run workflow »)", file=sortie)
            else:
                print(f"{jeu['id']} : ÉCHEC — {erreur}", file=sortie)
            continue
        remplace = cible.is_file()
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_bytes(octets)
        print(f"{jeu['id']} : {relatif} {'remplacé' if remplace else 'écrit'}, "
              f"{len(octets) / 1e6:.1f} Mo depuis {miroir}", file=sortie)
        if not declare:
            print(f"{jeu['id']} : miroir non déclaré — inscrire dans le manifeste "
                  f"miroir: {miroir} et sha256: {empreinte(octets)}", file=sortie)
        faits.append(cible)
    return faits


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    analyseur.add_argument("--recuperer", action="store_true",
                           help="télécharge dans data/brut/ les documents bloqués qui ont un miroir")
    analyseur.add_argument("--publier", action="store_true",
                           help="dépose sur la release documents-apportes les documents refusés "
                                "sans miroir (jeton d'un workflow GitHub Actions)")
    analyseur.add_argument("--sans-navigateur", action="store_true",
                           help="avec --publier : ne pas ouvrir de navigateur ; un site qui "
                                "refuse la requête simple donne le code de sortie 3")
    options = analyseur.parse_args(argv)
    bloques = jeux_bloques()
    if not bloques:
        print("aucune source bloquée dans data/sources.yaml")
        return 0
    if options.publier:
        navigateur = None if options.sans_navigateur else telecharger_par_navigateur
        if navigateur is not None:
            try:
                import playwright  # noqa: F401 — juste savoir s'il est là
            except ImportError:
                print("playwright absent : les sites qui refusent la requête simple "
                      "donneront le code 3", file=sys.stderr)
                navigateur = None
        etats = publier(bloques, navigateur=navigateur)
        candidats = a_publier(bloques)
        print(f"{sum(e == 'publie' for e in etats.values())} document(s) publié(s) "
              f"sur {len(candidats)} à publier")
        if any(e in ("echec", "ecart") for e in etats.values()):
            return 1
        return 3 if any(e == "navigateur" for e in etats.values()) else 0
    if options.recuperer:
        faits = recuperer(bloques)
        attendus = [j for j in bloques if ou_deposer(j) is not None
                    and (j.get("miroir") or a_publier([j]))]
        print(f"{len(faits)} document(s) en place sur {len(attendus)} qui ont un miroir")
        return 0 if len(faits) == len(attendus) else 1
    for jeu in bloques:
        print(f"{jeu['id']}  [{jeu['blocage']}]  {jeu['titre']}")
        print(f"    {jeu['url']}")
        if jeu["blocage"] == "convention":
            print("    rien à apporter : accès sous clé, compte ou convention")
            continue
        attendu = ou_deposer(jeu)
        if attendu is None:
            print("    l'adresse ne nomme pas de document : déclarer fichier_local "
                  "dans le manifeste quand un fichier précis est visé")
        elif attendu.is_file():
            etat = "conforme" if not jeu["sha256"] or empreinte(attendu.read_bytes()) == jeu["sha256"] \
                else "EMPREINTE DIFFÉRENTE"
            print(f"    en place : {attendu.relative_to(RACINE)}, {etat}")
        elif jeu["miroir"]:
            print(f"    miroir : {jeu['miroir']}\n    à récupérer sous "
                  f"{attendu.relative_to(RACINE)} (--recuperer)")
        elif a_publier([jeu]):
            print(f"    aucun miroir déclaré : document {adresse_du_document(jeu)}\n"
                  f"    publiable sur la release {ETIQUETTE} par le workflow "
                  f"documents-apportes.yml (--publier), puis --recuperer")
        else:
            print(f"    aucun miroir connu : à apporter sous {attendu.relative_to(RACINE)}")
        if jeu["recuperation"]:
            print(f"    lu par {jeu['recuperation']}")
        else:
            print(f"    aucun récupérateur ne le lit : {jeu['statut_integration']}, "
                  "à la main")
    print(f"\n{len(bloques)} source(s) bloquée(s). Nature des blocages :")
    for nom, sens in BLOCAGES.items():
        print(f"  {nom:<11} {sens}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
