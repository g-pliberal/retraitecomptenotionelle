#!/usr/bin/env python3
"""Fabrique ``data/reference/regimes/inventaire.yaml`` depuis les fichiers de régimes.

Chaque régime, calculé ou non, a son fichier dans ``data/reference/regimes/``,
nommé de son code, et ce fichier porte sa ligne d'inventaire : le bloc
``inventaire``, que ``_schema.yaml`` décrit. L'inventaire en est la vue, tous
les régimes section par section, dans l'ordre de leurs rangs
(docs/architecture.md, § 6.5 et annexe B). Le site, le tableau de bord,
``docs/regimes.md`` et les tests le lisent comme avant ; il ne s'écrit plus à
la main, et un test refuse un inventaire qui ne serait plus celui que ce
script produit.

    python scripts/construire_inventaire.py             # réécrit
    python scripts/construire_inventaire.py --verifier  # échoue s'il est périmé
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.config import RACINE_DONNEES  # noqa: E402
from retraite_notionnelle.donnees.regimes import (  # noqa: E402
    lignes_d_inventaire, sections_d_inventaire)

INVENTAIRE = RACINE_DONNEES / "reference" / "regimes" / "inventaire.yaml"

ENTETE = """\
# Inventaire des régimes de retraite obligatoires français
# ==========================================================
# FABRIQUÉ par scripts/construire_inventaire.py : ne pas le modifier à la main,
# mais le fichier du régime, puis relancer le script. Chaque régime, calculé ou
# non, a son fichier dans ce dossier, et ce fichier porte sa ligne : le bloc
# `inventaire`, que `_schema.yaml` décrit champ par champ. Les champs d'identité
# (nom, famille, population, dates, lignée) sont ceux du régime, sauf le nom et
# la population que le bloc raccourcit.
#
# Le catalogue ne contient que les régimes que le modèle CALCULE. Ce fichier-ci
# les énumère TOUS — ceux qui existent, ceux qui ont existé, ceux qu'on ne
# calculera pas — et dit pour chacun où en est le dépôt. `docs/limites.md`
# écrivait que la liste des régimes manquants n'était « dérivée d'aucun
# fichier, et c'est une limite en soi » : ce fichier est ce fichier, et
# `tests/test_donnees.py` le tient aligné sur le catalogue.
#
# Ancrages de la liste : R. 711-1 du code de la sécurité sociale (les régimes
# spéciaux), D. 643-1 (les sections des professions libérales), L. 921-1 et
# L. 921-4 (les complémentaires obligatoires), le programme 195 des lois de
# finances (les régimes fermés que l'État finance). Tout ce qui est marqué
# « à modéliser » l'est par décision, y compris l'outre-mer et les assemblées.

source_id: legifrance_inventaire_regimes

inventaire:
"""

BANNIERE = "  # " + "-" * 69


class _Ecrivain(yaml.SafeDumper):
    """L'inventaire s'écrit comme on l'écrivait à la main : une liste de
    valeurs simples, ou un texte cité, sur une ligne ; un long texte replié."""


class _EnLigne(dict):
    """Un texte cité — sa référence et son identifiant — tient sur une ligne."""


def _texte(ecrivain: yaml.SafeDumper, valeur: str):
    style = ">" if len(valeur) > 64 else None
    return ecrivain.represent_scalar("tag:yaml.org,2002:str", valeur, style=style)


def _liste(ecrivain: yaml.SafeDumper, valeur: list):
    simple = all(isinstance(v, (str, int, float, bool, type(None))) for v in valeur)
    return ecrivain.represent_sequence("tag:yaml.org,2002:seq", valeur, flow_style=simple)


def _en_ligne(ecrivain: yaml.SafeDumper, valeur: dict):
    return ecrivain.represent_mapping("tag:yaml.org,2002:map", valeur.items(), flow_style=True)


_Ecrivain.add_representer(str, _texte)
_Ecrivain.add_representer(list, _liste)
_Ecrivain.add_representer(_EnLigne, _en_ligne)


def _entree(ligne: dict) -> list[str]:
    ligne = dict(ligne)
    if ligne.get("textes"):
        ligne["textes"] = [_EnLigne(texte) for texte in ligne["textes"]]
    texte = yaml.dump([ligne], Dumper=_Ecrivain, allow_unicode=True, sort_keys=False,
                      width=80, default_flow_style=False)
    return ["  " + l if l else l for l in texte.rstrip("\n").split("\n")]


def produire() -> str:
    titres = sections_d_inventaire(RACINE_DONNEES)
    lignes = [ENTETE.rstrip("\n")]
    section = None
    for sa_section, ligne in lignes_d_inventaire(RACINE_DONNEES):
        if sa_section != section:
            section = sa_section
            lignes += ["", BANNIERE, f"  # {titres[section]}", BANNIERE]
        lignes += [""] + _entree(ligne)
    return "\n".join(lignes) + "\n"


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="ne rien écrire ; échouer si l'inventaire est périmé")
    arguments = analyseur.parse_args()
    nouveau = produire()
    if arguments.verifier:
        if nouveau != INVENTAIRE.read_text(encoding="utf-8"):
            print(f"{INVENTAIRE.relative_to(RACINE)} est périmé : lancer "
                  "python scripts/construire_inventaire.py")
            return 1
        print(f"{INVENTAIRE.relative_to(RACINE)} est à jour")
        return 0
    INVENTAIRE.write_text(nouveau, encoding="utf-8")
    print(f"{INVENTAIRE.relative_to(RACINE)} réécrit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
