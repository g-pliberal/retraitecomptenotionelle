#!/usr/bin/env python3
"""Les barèmes de l'IPP sur les retraites, lus dans leur dépôt YAML.

    python scripts/fetch/ipp_baremes_retraites.py              # clone, data/brut/…json
    python scripts/fetch/ipp_baremes_retraites.py --depot DIR  # un clone déjà là

POURQUOI IL EXISTE. Une table qu'aucun contrôle de ``verifier_donnees.py`` ne
recontrôle n'a qu'une lecture : celle de la session qui l'a écrite. Les barèmes
de l'Institut des politiques publiques en sont une seconde, faite par d'autres,
sous Licence Ouverte. ``controle_recoupement_ipp`` les y confronte, date par
date, sans rien certifier : l'IPP transcrit le Journal officiel et les caisses,
il ne produit pas (le registre, ``baremes_ipp``, dit ce qu'il vaut et ses
erreurs connues). Le 19 octobre 2026, ce recoupement a trouvé l'IPP en défaut,
non le dépôt (action 89).

CE QU'IL LIT. Les 155 fichiers de ``parameters/retraites/`` et le salaire
forfaitaire de l'AVPF, dans le dépôt ``baremes-ipp-yaml`` : le site
``baremes.ipp.eu`` est une coquille que le JavaScript remplit, et ses CSV ne
portent pas les références. Le dépôt se clone ; ``--depot`` évite de le refaire.

CE QU'IL ÉCRIT. ``data/brut/ipp_baremes_retraites.json`` : le commit lu, sa date,
et pour chaque paramètre, à son chemin sous ``parameters/``, ses valeurs datées
— une valeur nulle ferme le paramètre —, son unité, et les références que
l'IPP donne à ses dates : celles d'un fichier valent pour tous ses paramètres,
et un tiers seulement des marches des retraites en ont une.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "brut" / "ipp_baremes_retraites.json"
DEPOT = "https://gitlab.com/ipp/partage-public-ipp/baremes-ipp/baremes-ipp-yaml.git"

#: Ce qui se lit sous ``parameters/`` : les retraites, et l'assiette de l'AVPF,
#: que l'IPP range avec le minimum vieillesse.
LUS = ("retraites",
       "prestations_sociales/solidarite_insertion/minimum_vieillesse/avpf/salaire_forfaitaire")

#: Les clés d'un nœud qui ne sont pas des paramètres.
HORS_PARAMETRES = {"description", "metadata", "documentation"}


def _references(metadonnees: dict | None) -> dict[str, list[str]]:
    """Les titres que l'IPP cite, date par date (un ou plusieurs par marche)."""
    references = (metadonnees or {}).get("reference") or {}
    if not isinstance(references, dict):
        return {}
    rendu = {}
    for jour, citees in references.items():
        citees = citees if isinstance(citees, list) else [citees]
        rendu[str(jour)] = [c.get("title", "") if isinstance(c, dict) else str(c)
                            for c in citees]
    return rendu


def _parcourir(noeud, chemin: str, heritees: dict[str, list[str]],
               rendu: dict[str, dict]) -> None:
    if not isinstance(noeud, dict):
        return
    metadonnees = noeud.get("metadata") or {}
    references = {**heritees, **_references(metadonnees)}
    if "values" in noeud:
        rendu[chemin] = {
            "valeurs": {str(jour): (v.get("value") if isinstance(v, dict) else v)
                        for jour, v in (noeud["values"] or {}).items()},
            "unite": metadonnees.get("unit"),
            "references": references,
        }
        return
    for cle, enfant in noeud.items():
        if cle not in HORS_PARAMETRES:
            _parcourir(enfant, f"{chemin}/{cle}", references, rendu)


def feuilles(parametres: Path, lus: tuple[str, ...] = LUS) -> dict[str, dict]:
    """Chaque paramètre des dossiers ``lus`` de ``parametres``, à son chemin."""
    rendu: dict[str, dict] = {}
    for dossier in lus:
        for fichier in sorted((parametres / dossier).rglob("*.yaml")):
            if fichier.name == "index.yaml":
                continue
            chemin = fichier.relative_to(parametres).with_suffix("").as_posix()
            _parcourir(yaml.safe_load(fichier.read_text(encoding="utf-8")),
                       chemin, {}, rendu)
    return rendu


def _git(depot: Path, *arguments: str) -> str:
    return subprocess.run(["git", "-C", str(depot), *arguments], check=True,
                          capture_output=True, text=True).stdout.strip()


def ecrire(depot: Path) -> dict:
    lues = feuilles(depot / "parameters")
    rendu = {
        "source": DEPOT,
        "commit": _git(depot, "rev-parse", "--short", "HEAD"),
        "date": _git(depot, "log", "-1", "--format=%cs"),
        "lu_le": date.today().isoformat(),
        "feuilles": lues,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(rendu, ensure_ascii=False, indent=1, sort_keys=True),
                      encoding="utf-8")
    return rendu


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--depot", type=Path,
                           help="un clone de baremes-ipp-yaml déjà présent")
    arguments = analyseur.parse_args(argv)
    if arguments.depot:
        rendu = ecrire(arguments.depot)
    else:
        with tempfile.TemporaryDirectory() as dossier:
            clone = Path(dossier) / "baremes-ipp-yaml"
            subprocess.run(["git", "clone", "--depth", "1", "--quiet", DEPOT, str(clone)],
                           check=True)
            rendu = ecrire(clone)
    marches = sum(len(f["valeurs"]) for f in rendu["feuilles"].values())
    print(f"{SORTIE.relative_to(RACINE)} : {len(rendu['feuilles'])} paramètres, "
          f"{marches} marches, commit {rendu['commit']} du {rendu['date']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
