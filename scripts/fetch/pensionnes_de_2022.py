#!/usr/bin/env python3
"""Les pensionnés du 31 décembre 2022 au périmètre de l'Ageing Report : retraités, invalidité, AAH.

    python scripts/fetch/pensionnes_de_2022.py
    python scripts/fetch/pensionnes_de_2022.py --classeurs part1.xlsx part2.xlsx \\
        --minima minima-sociaux-donnees-nationales.xlsx

POURQUOI CE TÉMOIN. L'Ageing Report de 2024 compte, pour la France, 4,87
millions de pensionnés de moins de 65 ans en 2022, deux fois plus que les
retraités du modèle ; une part ne recule pas avec l'âge légal, que la note du
16 octobre 2026 calait sur l'effet publié de 2022 à 2070 (action 138, étape 3,
« la couverture de 2022-2030 »). Ce témoin la MESURE : ce que l'AWG range
parmi ses pensionnés (fiche France, § 3.1 — les pensions de vieillesse et de
réversion, l'invalidité, que la fiche étend à l'AAH et aux rentes d'accident du
travail ; résidents en France ou non), compté à ses sources, par tranche d'âge
au 31 décembre 2022 : moins de 55 ans, 55-59, 60-61, 62-64, 65 et plus.
``tests/test_pensionnes_de_l_awg.py`` s'y confronte ; il n'alimente aucune
valeur du modèle.

CE QU'ON EN GARDE.

* L'EACR de la DREES, « 62 EACR diffusée », version du 26 mai 2026 (les
  classeurs que ``drees_eacr.py`` lit) : ``C-Droits_directs`` et
  ``D-Droits_dérivés`` (premier classeur), tous régimes — la caisse ``0000``,
  que la DREES tire d'Ancetre —, les retraités de droit direct (``ddir``) et
  les bénéficiaires d'une réversion sans droit direct (``dders``), résidents
  en France ou non, puis résidents seuls ; ``I-Invalidité`` (second
  classeur), les pensionnés d'invalidité de droit direct (``ddir``, stock),
  caisse par caisse ; ``J-Rentes AT-MP``, les rentiers d'accident du travail
  et de maladie professionnelle, tous taux, caisse par caisse. Une caisse de
  l'EACR prend sa campagne la plus récente, comme dans ``drees_eacr.py`` ; les
  régimes de la fonction publique ne rangent parmi leurs retraités que leurs
  invalides de 62 ans et plus, et parmi leurs invalides les plus jeunes. La
  campagne de 2022 ne porte pas l'invalidité de la SNCF ni de la RATP : le
  témoin dit leur effectif de 2021 ;
* la CNAF, data.caf.fr : les bénéficiaires de l'AAH par sexe et par âge, en
  décembre 2022 (``aah_s_sexe_age_1_nat``), dont la somme est le total
  national publié (``s_ben_nat``) ;
* la DREES, « Minima sociaux : données nationales par dispositif », tableau
  2 : les allocataires de l'AAH de la France entière, MSA comprise, au 31
  décembre 2022 ;
* la fiche France de l'Ageing Report de 2024, tableau 12 : les pensionnés de
  2022 rapportés à la population de leur âge, en pour-cent, recopiés de la
  fiche (``TABLEAU_12``).

Le témoin est versionné : les tests le relisent sans réseau. ``--classeurs`` et
``--minima`` lisent les classeurs déjà téléchargés.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ageing_report import FICHE  # noqa: E402
from drees_eacr import BASE, ENTETES, _lignes, _millesime, classeur_portant, classeurs  # noqa: E402
from lecture_xlsx import feuilles  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "tests" / "temoins" / "pensionnes_de_2022.json"

ANNEE = 2022
TRANCHES = ("moins_de_55", "55_59", "60_61", "62_64", "65_et_plus")

FEUILLE_C = "C-Droits_directs"
FEUILLE_D = "D-Droits_dérivés"
FEUILLE_I = "I-Invalidité"
FEUILLE_J = "J-Rentes AT-MP"

CNAF = "https://data.caf.fr/api/explore/v2.1/catalog/datasets"
AAH_PAR_AGE = "aah_s_sexe_age_1_nat"
AAH_NATIONAL = "s_ben_nat"
MINIMA = ("https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog/datasets/"
          "336_minima-sociaux-rsa-et-prime-d-activite/attachments/"
          "minima_sociaux_donnees_nationales_par_dispositif_xlsx")

#: Le tableau 12 de la fiche France de l'Ageing Report de 2024 (p. 32) : les
#: pensionnés de 2022 rapportés à la population de leur âge, en pour-cent.
TABLEAU_12 = {"moins_de_55": 3.1, "55_59": 17.4, "60_64": 64.1}


def tranche(age) -> str:
    """La tranche d'un âge de l'EACR ou de la CNAF : un nombre, « moins de 20 »,
    « plus de 95 », « 18 ans ou moins », « 70 ans ou plus »."""
    trouve = re.search(r"\d+", str(age))
    if not trouve:
        raise ValueError(f"âge illisible : {age!r}")
    valeur = int(trouve.group())
    if valeur < 55:
        return "moins_de_55"
    if valeur < 60:
        return "55_59"
    if valeur < 62:
        return "60_61"
    if valeur < 65:
        return "62_64"
    return "65_et_plus"


def _par_tranche(cellules: list[dict]) -> dict:
    """Les effectifs de cellules d'une même série, par tranche, et le total
    que porte la ligne « Ensemble » quand la feuille en a une."""
    tranches = dict.fromkeys(TRANCHES, 0.0)
    total = None
    for cellule in cellules:
        effectif = cellule.get("effectifs")
        if not isinstance(effectif, float):
            continue
        if cellule.get("AgeQuin") == "Ensemble":
            total = effectif
        elif cellule.get("Age") not in (None, "Ensemble"):
            tranches[tranche(cellule["Age"])] += effectif
    serie = {"tranches": {nom: round(valeur) for nom, valeur in tranches.items()}}
    serie["total"] = round(total if total is not None else sum(tranches.values()))
    return serie


def _annee(cellule: dict) -> int | None:
    try:
        return int(cellule.get("Année", cellule.get("Annee")))
    except (TypeError, ValueError):
        return None


def tous_regimes(contenu: bytes, feuille: str, champ: str) -> dict:
    """Une série tous régimes (caisse ``0000``, Ancetre) de l'année, résidents
    en France ou non, puis résidents seuls."""
    cellules = {"Ensemble": [], "France": []}
    sources = set()
    for cellule in _lignes(feuilles(contenu, (feuille,))[feuille]):
        if (str(cellule.get("CC")) != "0000" or _annee(cellule) != ANNEE
                or cellule.get("Champ") != champ or cellule.get("Sexe") != "Ensemble"
                or cellule.get("Naiss", "Ensemble") != "Ensemble"
                or cellule.get("Liq", "Ensemble") != "Ensemble"
                or cellule.get("StatutSNCF", "Ensemble") != "Ensemble"
                or cellule.get("Resid") not in cellules):
            continue
        cellules[cellule["Resid"]].append(cellule)
        sources.add(str(cellule.get("Source")))
    if len(sources) != 1:
        raise RuntimeError(f"{feuille} : {sorted(sources)} pour {ANNEE}, une source attendue")
    serie = _par_tranche(cellules["Ensemble"])
    serie["residents"] = _par_tranche(cellules["France"])
    serie["feuille"], serie["champ"], serie["source"] = feuille, champ, sources.pop()
    return serie


def par_caisse(contenu: bytes, feuille: str, retenir) -> dict:
    """Une série de l'EACR caisse par caisse, chacune de sa campagne la plus
    récente ; ``retenir`` choisit les cellules. Les caisses qui portent
    l'année d'avant, et non celle-ci, disent leur effectif de l'année d'avant."""
    retenues: dict[tuple[str, int], dict[str, list]] = {}
    libelles: dict[str, str] = {}
    for cellule in _lignes(feuilles(contenu, (feuille,))[feuille]):
        annee = _annee(cellule)
        if annee not in (ANNEE - 1, ANNEE) or cellule.get("Sexe") != "Ensemble":
            continue
        if not retenir(cellule):
            continue
        code = str(cellule["CC"])
        par_source = retenues.setdefault((code, annee), {})
        par_source.setdefault(str(cellule.get("Source") or ""), []).append(cellule)
        libelles.setdefault(code, str(cellule["Caisse"]))
    caisses: dict = {}
    absentes: dict = {}
    for (code, annee), par_source in sorted(retenues.items()):
        source = max(par_source, key=lambda nom: (_millesime(nom), nom))
        serie = _par_tranche(par_source[source])
        if annee == ANNEE:
            caisses[code] = {"caisse": libelles[code], "source": source, **serie}
        elif (code, ANNEE) not in retenues:
            absentes[code] = {"caisse": libelles[code], "total_de_l_annee_precedente":
                              serie["total"]}
    return {"feuille": feuille, "caisses": caisses, "absentes": absentes}


def invalidite(contenu: bytes) -> dict:
    return par_caisse(contenu, FEUILLE_I, lambda cellule: (
        cellule.get("Champ") == "ddir" and cellule.get("Champ_FluxStock") == "stock"))


def rentes_at_mp(contenu: bytes) -> dict:
    return par_caisse(contenu, FEUILLE_J, lambda cellule: (
        cellule.get("Champ") == "ddir" and cellule.get("Taux") == "TOTAL"))


def _cnaf(jeu: str, **parametres) -> dict:
    requete = urllib.parse.urlencode(
        {"where": f"dtreffre=date'{ANNEE}-12-01'", "limit": 100, **parametres})
    demande = urllib.request.Request(f"{CNAF}/{jeu}/records?{requete}", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=120) as reponse:
        return json.loads(reponse.read())


def aah_cnaf() -> dict:
    """Les bénéficiaires de l'AAH de la CNAF en décembre de l'année, par
    tranche d'âge, deux sexes réunis, et le total national publié, qu'ils
    doivent refaire."""
    lignes = _cnaf(AAH_PAR_AGE)["results"] + _cnaf(AAH_PAR_AGE, offset=100)["results"]
    tranches = dict.fromkeys(TRANCHES, 0)
    indetermine = 0
    for ligne in lignes:
        if "indéterminé" in ligne["aah_age_1"]:
            indetermine += ligne["indben_aah"]
        else:
            tranches[tranche(ligne["aah_age_1"])] += ligne["indben_aah"]
    total = _cnaf(AAH_NATIONAL, select="indben_aah")["results"][0]["indben_aah"]
    if sum(tranches.values()) + indetermine != total:
        raise RuntimeError(f"AAH : la somme des âges ne refait pas le total national {total}")
    return {"tranches": tranches, "indetermine": indetermine, "total": total}


def aah_france(contenu: bytes) -> int:
    """Les allocataires de l'AAH au 31 décembre de l'année, France entière
    (tableau 2 des données nationales de la DREES)."""
    grille = feuilles(contenu, ("Tableau 2",))["Tableau 2"]
    colonne = next(c for (ligne, c), valeur in grille.items()
                   if ligne < 5 and valeur == float(ANNEE))
    ligne = next(l for (l, c), valeur in grille.items() if isinstance(valeur, str)
                 and valeur.startswith("Allocation aux adultes handicapés"))
    return round(grille[(ligne, colonne)])


def _telecharger(url: str) -> bytes:
    demande = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=300) as reponse:
        return reponse.read()


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--classeurs", nargs="+", type=Path,
                           help="les classeurs de l'EACR déjà téléchargés")
    analyseur.add_argument("--minima", type=Path,
                           help="les données nationales des minima sociaux, téléchargées")
    arguments = analyseur.parse_args(argv)
    if arguments.classeurs:
        telecharges = [(chemin.name, chemin.read_bytes()) for chemin in arguments.classeurs]
    else:
        telecharges = classeurs()
    titre_1, premier = classeur_portant(telecharges, FEUILLE_C)
    titre_2, second = classeur_portant(telecharges, FEUILLE_I)
    minima = arguments.minima.read_bytes() if arguments.minima else _telecharger(MINIMA)
    aah = aah_cnaf()
    aah["total_france"] = aah_france(minima)
    temoin = {
        "source": {
            "eacr": f"{BASE} — {titre_1}, {titre_2}",
            "aah": f"{CNAF}/{AAH_PAR_AGE} (total : {AAH_NATIONAL}), décembre {ANNEE}",
            "aah_france": f"{MINIMA} — tableau 2, France",
            "ageing_report": f"{FICHE} — tableau 12, p. 32",
            "lu_le": date.today().isoformat(),
        },
        "date": f"{ANNEE}-12-31",
        "tranches": list(TRANCHES),
        "unite": "personnes au 31 décembre ; le tableau 12 en % de la population de l'âge",
        "droit_direct": tous_regimes(premier, FEUILLE_C, "ddir"),
        "reversion_seule": tous_regimes(premier, FEUILLE_D, "dders"),
        "invalidite": invalidite(second),
        "rentes_at_mp": rentes_at_mp(second),
        "aah": aah,
        "ageing_report": {str(ANNEE): TABLEAU_12},
    }
    SORTIE.write_text(json.dumps(temoin, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    print(f"Écrit {SORTIE.relative_to(RACINE)} ({SORTIE.stat().st_size // 1024} Ko)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
