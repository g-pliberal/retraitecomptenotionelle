#!/usr/bin/env python3
"""Lire un document déposé à la main quand la source refuse la session.

    python scripts/fetch/source_locale.py          # les sources bloquées, et où déposer leur fichier
    python scripts/fetch/erafp_valeurs_point.py --fichier ~/Téléchargements/RAFP-Evolution-valeurs-point.pdf

Certaines sources ne se laissent pas lire depuis l'environnement où ce dépôt
est construit, et ce n'est pas une panne : ``budget.gouv.fr`` répond 403 aux
adresses de sortie du proxy, la Banque de France refuse ses PDF aux clients qui
ne sont pas un navigateur, Légifrance refuse les requêtes automatisées. Un
navigateur sur un poste ordinaire, lui, passe. Le dépôt ne maquille pas ses
signaux d'automatisation pour forcer un refus (voir
``docs/outillage_interface.md``) ; il prévoit à la place que le document soit
**apporté** : téléchargé ailleurs, déposé dans ``data/brut/``, et lu de là.

Deux gestes, et le manifeste qui les relie :

* ``data/sources.yaml`` porte un champ ``blocage`` sur chaque jeu qu'une
  session ne peut pas atteindre, avec la nature du refus. Ce script, lancé sans
  argument, en imprime la liste et, pour chacun, le chemin où le fichier est
  attendu.
* Les récupérateurs qui lisent un document appellent ``lire_ou_telecharger``
  au lieu d'ouvrir l'adresse directement. La fonction lit d'abord le fichier
  passé en ``--fichier``, sinon ``data/brut/<dernier segment de l'adresse>``
  s'il existe, et ne télécharge qu'en dernier. Le nom attendu est donc celui
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
import sys
from collections.abc import Callable
from pathlib import Path
from urllib.parse import unquote, urlsplit

RACINE = Path(__file__).resolve().parents[2]
BRUT = RACINE / "data" / "brut"
MANIFESTE = RACINE / "data" / "sources.yaml"

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


def lire_ou_telecharger(url: str, telecharger: Callable[[str], bytes],
                        fichier: Path | str | None = None, *,
                        nom_local: str | None = None,
                        sortie=sys.stderr) -> bytes:
    """Le document : du fichier demandé, sinon de ``data/brut/``, sinon du site.

    ``telecharger`` n'est appelé que si aucun fichier local ne répond. Le
    chemin lu est écrit sur ``sortie`` pour qu'un journal de récupération
    dise d'où vient ce qu'il a lu. Une adresse qui ne nomme pas son fichier
    et un récupérateur qui ne donne pas ``nom_local`` : rien n'est cherché
    en local, on télécharge.
    """
    if fichier is not None:
        chemin = Path(fichier)
        print(f"lu depuis {chemin}, sans téléchargement : {url}", file=sortie)
        return chemin.read_bytes()
    try:
        local = chemin_local(url, nom_local)
    except ValueError:
        return telecharger(url)
    if local.is_file():
        print(f"lu depuis {local.relative_to(RACINE)}, sans téléchargement : {url}",
              file=sortie)
        return local.read_bytes()
    return telecharger(url)


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


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    analyseur.parse_args(argv)
    bloques = jeux_bloques()
    if not bloques:
        print("aucune source bloquée dans data/sources.yaml")
        return 0
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
        else:
            print(f"    à déposer sous {attendu.relative_to(RACINE)}")
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
