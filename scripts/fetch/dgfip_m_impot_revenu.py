#!/usr/bin/env python3
"""L'impôt sur le revenu de 47 foyers, des revenus de 2019 à ceux de 2025, par
le calcul officiel de la DGFiP : son code M, exécuté par Mlang.

    python scripts/fetch/dgfip_m_impot_revenu.py --mlang <clone de Mlang>

À quoi il sert. La DGFiP publie le code de sa calculette de l'impôt sur le
revenu, en langage M, sous CeCILL 2.1 (https://gitlab.adullact.net/dgfip/ir-calcul,
un dossier ``sources<année>m_<version>`` par année de revenus, de 2010 à
2025). Mlang (Inria et DGFiP, https://github.com/MLanguage/mlang), qui passe
les tests privés de la DGFiP pour les revenus de 2018 à 2021, l'exécute. Le
registre des modèles (``data/reference/referents.yaml``, ``calculette_ir_dgfip``)
le range en ``executer_a_part`` : le dépôt n'en garde que les sorties.

Le fichier produit, ``tests/temoins/impot_revenu_dgfip_m.json``, est
VERSIONNÉ : ``tests/test_impot_revenu.py`` confronte au calcul officiel, à
l'euro, le module et le portage, sans installer Mlang. Il remplace OpenFisca
pour les revenus de 2019 et suivants (le 21 novembre 2026, OpenFisca refusait
l'abattement des personnes âgées l'année des 65 ans, et arrondit autrement).

Les foyers. Les zones à risque d'un simulateur de retraites : le retraité seul
et le couple de retraités autour de la décote et des deux seuils de
l'abattement des personnes âgées, l'année des 65 ans, le veuf, le parent
isolé, les couples d'actifs au plafonnement du quotient familial, les
foyers mixtes. Salaires et pensions IMPOSABLES (cases 1AJ, 1BJ, 1AS, 1BS),
l'âge au 31 décembre (cases 0DA, 0DB : l'année de naissance), les enfants
mineurs (0CF), la situation (0AC, 0AM, 0AV) et la case T (0BT).

Chaque année, quand la DGFiP publie le code des revenus de l'année passée :

1. Une fois par poste : ``apt install opam libgmp-dev libmpfr-dev`` ; un
   switch OCaml (``opam switch create mlang ocaml-system``) ;
   ``opam install dune menhir ANSITerminal.0.8.2 cmdliner.1.3.0 re.1.11.0
   ocamlgraph.1.8.8 dune-build-info num mlgmpidl parmap.1.2.3`` ; le clone de
   Mlang, ``ir-calcul`` cloné dans son dossier ``ir-calcul/`` ;
   ``dune build src/main.exe``. Une vingtaine de minutes.
2. ``git pull`` dans les deux clones, ``dune build src/main.exe``.
3. Ajouter la nouvelle année à ``ANNEES`` et lancer le script (trois
   secondes par foyer-année, en parallèle). Mlang doit avoir un dossier
   ``m_ext/<année>`` pour elle ; sinon, attendre qu'il le publie.
4. ``python -m pytest tests/test_impot_revenu.py -k officiel`` : un écart
   est une erreur du dépôt, sauf preuve du contraire par le texte, qui se
   déclare alors dans ``DESACCORDS_DGFIP``.

Deux réglages qu'on ne voit pas. ``--income-year`` doit être l'année des
revenus : par défaut, Mlang prend l'année qui précède l'horloge, et le code
des revenus de 2024 et suivants calcule l'âge sur elle. Les fichiers
``m_ext`` des dernières années visent une version interne du code et citent
quelques variables absentes du code publié, toutes dans la recopie des
montants pour le correctif de l'article 1731 bis, qui ne joue pas au premier
calcul : le script les retire d'une copie de ``m_ext`` (``_reparer``).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

SORTIE = Path(__file__).resolve().parents[2] / "tests" / "temoins" / "impot_revenu_dgfip_m.json"

ANNEES = tuple(range(2019, 2026))

#: Les variables de la calculette relevées : revenu net global, abattement des
#: personnes âgées ou invalides, revenu imposable, revenu fiscal de référence,
#: droits simples après quotient (l'impôt brut), décote, impôt.
GRANDEURS = ("RNG", "ABVIE", "RNI", "REVKIRE", "IDRS3", "IDEC", "IINET")


def _foyers() -> tuple[dict, ...]:
    foyers = []

    def f(code, declarants, enfants=0, statut=None, case_t=False):
        foyers.append({"code": code, "declarants": declarants, "enfants": enfants,
                       "statut": statut or ("marie" if len(declarants) == 2 else "seul"),
                       "case_t": case_t})

    def r(pension, age=75):
        return {"pension": pension, "age": age}

    for p in (12000, 14000, 16000, 17500, 18500, 19500, 20500, 21500, 23000, 26000,
              30000, 31500, 33000, 40000, 60000):
        f(f"retraite_seul_{p}", [r(p)])
    for age in (64, 65):
        f(f"retraite_seul_20000_age_{age}", [r(20000, age)])
    for p1, p2 in ((14000, 8000), (18000, 12000), (22000, 13000), (25000, 15000),
                   (30000, 15000), (35000, 20000), (45000, 25000), (60000, 40000)):
        f(f"couple_retraites_{p1}_{p2}", [r(p1), r(p2, 72)])
    f("couple_retraites_un_seul_65", [r(25000, 70), r(10000, 63)])
    f("couple_retraites_un_seul_revenu", [r(32000, 70), {"age": 70}])
    f("veuf_retraite", [r(25000)], statut="veuf")
    f("veuf_un_enfant", [{"salaire": 40000, "age": 45}], enfants=1, statut="veuf")
    for s in (16000, 19000, 21000, 24000, 28000, 45000, 120000):
        f(f"salarie_seul_{s}", [{"salaire": s, "age": 40}])
    f("parent_isole_1_20000", [{"salaire": 20000, "age": 35}], enfants=1, case_t=True)
    f("parent_isole_2_45000", [{"salaire": 45000, "age": 40}], enfants=2, case_t=True)
    f("parent_isole_1_90000", [{"salaire": 90000, "age": 40}], enfants=1, case_t=True)
    f("couple_2_enfants_50000", [{"salaire": 30000, "age": 40}, {"salaire": 20000, "age": 38}],
      enfants=2)
    f("couple_2_enfants_90000", [{"salaire": 55000, "age": 40}, {"salaire": 35000, "age": 38}],
      enfants=2)
    f("couple_3_enfants_70000", [{"salaire": 45000, "age": 40}, {"salaire": 25000, "age": 38}],
      enfants=3)
    f("couple_3_enfants_160000",
      [{"salaire": 110000, "age": 45}, {"salaire": 50000, "age": 43}], enfants=3)
    f("couple_1_enfant_200000",
      [{"salaire": 150000, "age": 50}, {"salaire": 50000, "age": 48}], enfants=1)
    f("couple_un_salaire_28000", [{"salaire": 28000, "age": 40}, {"age": 40}])
    f("salarie_et_retraite", [{"salaire": 30000, "age": 62}, r(18000, 67)])
    f("retraite_qui_travaille", [{"salaire": 12000, "pension": 15000, "age": 68}])
    return tuple(foyers)


FOYERS = _foyers()


def irj(foyer: dict, annee: int) -> str:
    """Le foyer au format de test de la DGFiP, chaque résultat attendu faux
    (-999) : Mlang rend alors « attendue: -999 - evaluee: <valeur> »."""
    e = [f"ANREV/{annee}", {"seul": "0AC/1", "marie": "0AM/1", "veuf": "0AV/1"}[foyer["statut"]]]
    if foyer["case_t"]:
        e.append("0BT/1")
    if foyer["enfants"]:
        e.append(f"0CF/{foyer['enfants']}")
    for rang, d in enumerate(foyer["declarants"]):
        lettre = "AB"[rang]
        if d.get("age") is not None:
            e.append(f"0D{lettre}/{annee - d['age']}")
        if d.get("salaire"):
            e.append(f"1{lettre}J/{d['salaire']}")
        if d.get("pension"):
            e.append(f"1{lettre}S/{d['pension']}")
    return ("#NOM\n" + foyer["code"] + "\n#ENTREES-PRIMITIF\n" + "\n".join(e)
            + "\n#CONTROLES-PRIMITIF\n#RESULTATS-PRIMITIF\n"
            + "\n".join(f"{g}/-999" for g in GRANDEURS)
            + "\n#ENTREES-CORRECTIF\n#CONTROLES-CORRECTIF\n#RESULTATS-CORRECTIF\n##\n")


def _sources(mlang: Path, annee: int, ext: Path) -> list[str]:
    dossier = sorted((mlang / "ir-calcul").glob(f"sources{annee}m_*"))[-1]
    tous = sorted(dossier.glob("*.m"))
    sources = ([p for p in tous if p.name.startswith("tgv")]
               + [p for p in tous if p.name.startswith("err")]
               + [p for p in tous if not p.name.startswith(("tgv", "err")) and p.name != "cibles.m"])
    if annee >= 2022:
        ordre = ("cibles", "codes_1731", "commence_par_5", "commence_par_7", "commence_par_H",
                 "correctif", "main")
        extensions = [ext / f"{nom}.m" for nom in ordre]
    else:
        extensions = sorted(ext.glob("*.m"))
    return [str(p) for p in sources + extensions]


def _executer(mlang: Path, annee: int, ext: Path, contenu: str) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".irj", delete=False) as fichier:
        fichier.write(contenu)
    try:
        sortie = subprocess.run(
            [str(mlang / "_build" / "default" / "src" / "main.exe"), "-A", "iliad",
             "--precision", "double", f"--income-year={annee}",
             "--mpp_function=enchainement_primitif_interpreteur", f"--run_test={fichier.name}",
             *_sources(mlang, annee, ext)], capture_output=True, text=True)
    finally:
        Path(fichier.name).unlink()
    return re.sub(r"\x1b\[[0-9;]*m", "", sortie.stdout + sortie.stderr)


_INCONNUE = re.compile(r"\[ERROR\] unknown variable\n\s*--> (\S+)\n(?:[^\n]*\n)*?\s*(\d+) \| ")


def _reparer(mlang: Path, annee: int, copie: Path) -> Path:
    """Une copie de ``m_ext/<année>`` dont les lignes de ``codes_1731.m`` qui
    citent une variable absente du code publié sont retirées."""
    shutil.copytree(mlang / "m_ext" / str(annee), copie)
    for _ in range(500):
        texte = _executer(mlang, annee, copie, irj(FOYERS[0], annee))
        trouve = _INCONNUE.search(texte)
        if "KO |" in texte or not trouve:
            return copie
        chemin, ligne = Path(trouve.group(1)), int(trouve.group(2))
        if chemin.name != "codes_1731.m" or copie not in chemin.parents:
            raise RuntimeError(f"variable inconnue hors du correctif : {chemin}:{ligne}")
        lignes = chemin.read_text(encoding="utf-8", errors="replace").split("\n")
        lignes[ligne - 1] = ""
        chemin.write_text("\n".join(lignes), encoding="utf-8")
    raise RuntimeError("trop de variables inconnues")


_VALEUR = re.compile(r"KO \| (\w+) attendue: \S+ - evaluee: (\S+)")


def calculer(mlang: Path, annee: int, ext: Path, foyer: dict) -> list[float]:
    texte = _executer(mlang, annee, ext, irj(foyer, annee))
    lues = {g: float(v) for g, v in _VALEUR.findall(texte)}
    manquantes = [g for g in GRANDEURS if g not in lues]
    if manquantes:
        raise RuntimeError(f"{foyer['code']}, {annee} : {manquantes} non rendues\n{texte[-800:]}")
    return [lues[g] for g in GRANDEURS]


def ecrire(temoin: dict) -> str:
    """Le témoin, une ligne par foyer et par année, comme celui d'OpenFisca."""
    lignes = ["{"]
    for cle in ("source", "version", "recupere_le", "avertissement", "grandeurs"):
        lignes.append(f'  {json.dumps(cle)}: {json.dumps(temoin[cle], ensure_ascii=False)},')
    lignes.append('  "foyers": {')
    foyers = list(temoin["foyers"].items())
    for rang, (code, contenu) in enumerate(foyers):
        lignes.append(f'    {json.dumps(code)}: {{')
        lignes.append(f'      "foyer": {json.dumps(contenu["foyer"], ensure_ascii=False)},')
        lignes.append('      "annees": {')
        annees = list(contenu["annees"].items())
        lignes += [f'        {json.dumps(a)}: {json.dumps(v)}' + ("," if k + 1 < len(annees) else "")
                   for k, (a, v) in enumerate(annees)]
        lignes.append("      }")
        lignes.append("    }" + ("," if rang + 1 < len(foyers) else ""))
    lignes += ["  }", "}"]
    return "\n".join(lignes) + "\n"


def _commit(depot: Path) -> str:
    return subprocess.run(["git", "-C", str(depot), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def main() -> int:
    lecteur = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    lecteur.add_argument("--mlang", type=Path, required=True,
                         help="le clone de Mlang, compilé, ir-calcul dans son dossier")
    lecteur.add_argument("--processus", type=int, default=8)
    options = lecteur.parse_args()
    mlang = options.mlang.resolve()
    with tempfile.TemporaryDirectory() as provisoire:
        extensions = {}
        for annee in ANNEES:
            ext = mlang / "m_ext" / str(annee)
            if annee >= 2024:
                ext = _reparer(mlang, annee, Path(provisoire) / str(annee))
            extensions[annee] = ext
        travaux = [(annee, foyer) for annee in ANNEES for foyer in FOYERS]
        with ThreadPoolExecutor(options.processus) as pool:
            valeurs = list(pool.map(
                lambda t: calculer(mlang, t[0], extensions[t[0]], t[1]), travaux))
    resultats = {(annee, foyer["code"]): v for (annee, foyer), v in zip(travaux, valeurs)}
    temoin = {
        "source": "Calculette de l'impôt sur le revenu de la DGFiP (code M), exécutée par Mlang",
        "version": (f"ir-calcul {_commit(mlang / 'ir-calcul')}, Mlang {_commit(mlang)}, "
                    + ", ".join(f"{a} : {sorted((mlang / 'ir-calcul').glob(f'sources{a}m_*'))[-1].name}"
                                for a in ANNEES)),
        "recupere_le": date.today().isoformat(),
        "avertissement": ("Le calcul officiel : un écart est une erreur du dépôt, sauf preuve "
                          "du contraire par le texte. Mlang n'apporte pas de garantie juridique."),
        "grandeurs": list(GRANDEURS),
        "foyers": {foyer["code"]: {"foyer": foyer,
                                   "annees": {str(a): resultats[(a, foyer["code"])]
                                              for a in ANNEES}}
                   for foyer in FOYERS},
    }
    SORTIE.write_text(ecrire(temoin), encoding="utf-8")
    print(f"{SORTIE} : {len(FOYERS)} foyers, {len(ANNEES)} années")
    return 0


if __name__ == "__main__":
    sys.exit(main())
