"""La table des références : ce à quoi chaque élément du calcul se confronte.

    python scripts/table_des_references.py           # la table, élément par famille
    python scripts/table_des_references.py --trous   # les cases sans référence

La table est `data/reference/references_par_element.yaml`, écrite à la main.
Ce module relève ce que le dépôt sait déjà, case par case — les fiches qui la
touchent, les exemples officiels et les grilles indépendantes qui la
rejouent, les modèles que ses fiches citent —, et
`tests/test_table_des_references.py` tient la table d'accord avec ce relevé.
Action 137.
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]
REFERENCE = RACINE / "data" / "reference"
TABLE = REFERENCE / "references_par_element.yaml"
REGLES = REFERENCE / "regles"
PREUVES = REFERENCE / "preuves"
INVENTAIRE = REFERENCE / "regimes" / "inventaire.yaml"
AFFILIATIONS = REFERENCE / "legislation" / "affiliations.yaml"
REFERENTS = REFERENCE / "referents.yaml"
VIVIER = RACINE / "data" / "sources_a_explorer.yaml"
EXEMPLES = RACINE / "tests" / "temoins" / "exemples_officiels.yaml"

#: Les familles de régimes de l'inventaire, dans l'ordre où la table les écrit.
FAMILLES = ("base_prive", "complementaire_prive", "fonction_publique", "special",
            "non_salarie", "liberal", "agricole", "additionnel_capitalise")

#: La famille qui porte la pension de base d'une affiliation, quand elle en a
#: plusieurs : la première de cette liste.
PRIORITE_DE_BASE = ("special", "fonction_publique", "liberal", "non_salarie",
                    "agricole", "base_prive")

#: Les sortes de référence. Les deux premières se comptent au dépôt ; les
#: autres se nomment par leur ligne au registre des modèles ou au vivier.
SORTES = ("exemple_officiel", "grille_independante", "simulateur_caisse",
          "page_officielle", "modele")


def _yaml(chemin: Path):
    chargeur = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    with open(chemin, encoding="utf-8") as f:
        return yaml.load(f, Loader=chargeur)


def charger_table(chemin: Path = TABLE) -> dict:
    return _yaml(chemin)


def fiches() -> dict[str, dict]:
    return {p.stem: _yaml(p) for p in sorted(REGLES.glob("*.yaml"))}


def familles_de_regime() -> dict[str, str]:
    return {ligne["code"]: ligne["famille"] for ligne in _yaml(INVENTAIRE)["inventaire"]}


def modeles() -> dict[str, dict]:
    return {m["id"]: m for m in _yaml(REFERENTS)["referents"]}


def sources_a_explorer() -> dict[str, dict]:
    return {s["id"]: s for s in _yaml(VIVIER)["sources"]}


def exemples_officiels() -> list[dict]:
    return _yaml(EXEMPLES)["exemples"]


def preuves() -> list[dict]:
    return [_yaml(p) for p in sorted(PREUVES.glob("*.yaml"))]


def grandeurs_comparees() -> set[str]:
    cas = [*exemples_officiels(), *(c for p in preuves() for c in p.get("cas") or [])]
    return {cle for c in cas for cle in c.get("attendu") or {}}


def element_de_chaque_fiche(table: dict, toutes: dict[str, dict]) -> dict[str, list[str]]:
    """Les éléments de chaque fiche : celui qui la nomme, sinon celui de son domaine."""
    nommees = {}
    for e in table["elements"]:
        for f in e.get("fiches", []):
            nommees.setdefault(f, []).append(e["id"])
    par_domaine = {}
    for e in table["elements"]:
        for d in e.get("domaines", []):
            par_domaine.setdefault(d, []).append(e["id"])
    resultat = {}
    for nom, fiche in toutes.items():
        els = nommees.get(nom) or par_domaine.get(fiche.get("domaine"), [])
        if els:
            resultat[nom] = els
    return resultat


def famille_de_base(affiliation: str, de_regime: dict[str, str],
                    affiliations: dict[str, dict]) -> str | None:
    a = affiliations.get(affiliation)
    if a is None:
        return None
    siennes = {de_regime.get(r) for p in a["periodes"] for r in p["regimes"]}
    return next((f for f in PRIORITE_DE_BASE if f in siennes), None)


def releve(table: dict) -> dict[tuple[str, str], dict[str, set]]:
    """Ce que le dépôt sait de chaque case (élément, famille)."""
    toutes = fiches()
    de_regime = familles_de_regime()
    affiliations = _yaml(AFFILIATIONS)["affiliations"]
    cases = {(e["id"], f): {"fiches": set(), "exemples": set(), "preuves": set(),
                            "referents": set()}
             for e in table["elements"] for f in FAMILLES}
    for nom, els in element_de_chaque_fiche(table, toutes).items():
        fiche = toutes[nom]
        for famille in {de_regime.get(r) for r in fiche.get("regimes") or []}:
            for el in els:
                if (el, famille) in cases:
                    cases[el, famille]["fiches"].add(nom)
                    cases[el, famille]["referents"].update(fiche.get("referents") or {})
    # Une grandeur comparée va à l'élément qui la range, dans la famille que
    # l'élément lui force, sinon dans celle de la pension de base du cas.
    rang = {cle: (e["id"], forcee) for e in table["elements"]
            for cle, forcee in (e.get("attendus") or {}).items()}

    def ranger(cas: dict, cle_releve: str, ident: str) -> None:
        affiliation = (cas.get("carriere") or {}).get("affiliation")
        base = famille_de_base(affiliation, de_regime, affiliations) if affiliation else None
        for cle in cas.get("attendu") or {}:
            if cle not in rang:
                continue
            el, forcee = rang[cle]
            famille = forcee or base
            if (el, famille) in cases:
                cases[el, famille][cle_releve].add(ident)

    for ex in exemples_officiels():
        ranger(ex, "exemples", ex["id"])
    for p in preuves():
        for c in p.get("cas") or []:
            ranger(c, "preuves", p["id"])
    return cases


def etat_de_case(case: dict) -> str:
    if case.get("sans_objet"):
        return "sans objet"
    if case.get("absence"):
        return "absente"
    sortes = {r["sorte"] for r in case.get("references") or []}
    if sortes & {"exemple_officiel", "grille_independante", "simulateur_caisse",
                 "page_officielle"}:
        return "officielle"
    return "modèle seul"


def main(argv: list[str]) -> int:
    table = charger_table()
    trous = "--trous" in argv
    largeur = max(len(e["id"]) for e in table["elements"])
    if not trous:
        print(" " * largeur, *(f[:12].ljust(12) for f in FAMILLES))
    for e in table["elements"]:
        if trous:
            for famille, case in e["cellules"].items():
                if case.get("absence"):
                    print(f"{e['id']}/{famille} : {' '.join(str(case['absence']).split())}")
            continue
        print(e["id"].ljust(largeur),
              *(etat_de_case(e["cellules"][f])[:12].ljust(12) for f in FAMILLES))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
