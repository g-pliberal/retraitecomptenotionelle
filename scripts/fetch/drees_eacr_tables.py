#!/usr/bin/env python3
"""Les tables H, B et C de l'EACR : les conditions de liquidation, les liquidants et les droits directs par âge.

    python scripts/fetch/drees_eacr_tables.py
    python scripts/fetch/drees_eacr_tables.py --classeurs part1.xlsx part2.xlsx

POURQUOI CE TÉMOIN. La page Coût pèse ses cas types par les effectifs de leur
caisse (``drees_eacr.py``, feuille ``A-Cadrage``) et ne contrôlait ni l'âge
de ses retraités, ni l'âge où ils partent, ni la part qui part avec une décote
ou une surcote. L'EACR les compte, caisse par caisse : ce témoin en garde ce
que ``retraite_notionnelle.controle_eacr`` confronte à la grille de la page et
à la population de l'étape 14 (action 138, étape 3). Il n'alimente aucune
valeur du modèle.

CE QU'ON EN GARDE, de la version du 26 mai 2026 (« 62 EACR diffusée ») :

* ``H-Conditions_liq`` (second classeur) — les retraités partis au taux plein,
  avec une décote, avec une surcote, en flux (les liquidants de l'année) et
  en stock (tous les retraités au 31 décembre), tous motifs de départ et tous
  âges réunis, par sexe et par année, pour les caisses qui la remplissent : la
  Cnav, les deux MSA, l'État civil et militaire (cube du SRE), l'Agirc-Arrco.
  Les trois conditions partitionnent les retraités : la surcote n'est pas
  comptée dans le taux plein ; elle manque à l'Agirc-Arrco, qui n'en sert
  pas, et aux militaires. Le SRE écrit « surcote » en minuscule, et ne
  donne pas la ligne « Ensemble », que la somme refait ;
* ``B-Liquidants`` (premier classeur) — les liquidants de chaque caisse par
  âge, l'année la plus récente, tous sexes, toutes durées, tous motifs (le
  stock par âge, que la feuille porte aussi, est celui de la table C) ;
* ``C-Droits_directs`` (premier classeur) — les retraités de droit direct
  TOUS RÉGIMES (caisse ``0000``, que la DREES tire d'Ancetre), par âge et par
  sexe, avec leur pension mensuelle moyenne : le stock (``ddir``) et les
  nouveaux retraités de l'année (``nl_ddir``), l'année la plus récente.

Une même cellule peut venir de plusieurs campagnes : comme ``drees_eacr.py``,
on retient la plus RÉCENTE, au millésime lu dans le libellé de la source. Les
feuilles font de 60 à 125 Mo de XML : chacune se lit seule.

Le témoin est versionné : les tests le relisent sans réseau. ``--classeurs``
lit les deux classeurs déjà téléchargés.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from drees_eacr import BASE, _lignes, _millesime, classeur_portant, classeurs  # noqa: E402
from lecture_xlsx import feuilles  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "tests" / "temoins" / "drees_eacr_tables_2026.json"

FEUILLE_H = "H-Conditions_liq"
FEUILLE_B = "B-Liquidants"
FEUILLE_C = "C-Droits_directs"

#: Les caisses de la table H : la Cnav (0015 depuis 2020), la MSA salariés et
#: exploitants, l'État civil et militaire, l'Agirc-Arrco.
CAISSES_H = ("0015", "0021", "0022", "0012", "0013", "5600")

#: Les conditions de la table H, sous les noms du témoin.
TAUX = {"Taux plein": "taux_plein", "Décote": "decote", "Surcote": "surcote",
        "surcote": "surcote", "Ensemble": "ensemble"}

#: Les caisses de la table B : celles du témoin H qui la remplissent par âge,
#: la CNRACL, la SSI (RCI complémentaire). La CNAVPL n'y a que son stock.
CAISSES_B = ("0015", "0021", "0022", "0032", "0043")

#: Les champs de la table C : le stock des droits directs, et les nouveaux
#: retraités de droit direct de l'année.
CHAMPS_C = ("ddir", "nl_ddir")

#: Les sexes, sous les noms du dépôt.
SEXES = {"Ensemble": "ensemble", "Femmes": "F", "Hommes": "H"}

#: Le flux et le stock, sous les noms du témoin.
CHAMPS_FS = {"Flux": "flux", "Stock": "stock"}

#: Première année gardée de la table H.
DEPUIS = 2015


def _feuille(contenu: bytes, nom: str):
    return _lignes(feuilles(contenu, (nom,))[nom])


def _retenir(retenues: dict, cle: tuple, source: str, valeur) -> None:
    """La campagne la plus récente l'emporte, comme dans ``drees_eacr.py``."""
    rang = (_millesime(source), source)
    if cle not in retenues or rang > retenues[cle][0]:
        retenues[cle] = (rang, valeur)


def conditions_liquidation(contenu: bytes) -> dict:
    """La table H : ``{caisse: {flux|stock: {sexe: {année: {condition: effectif}}}}}``,
    et la source retenue de chaque cellule."""
    retenues: dict[tuple, tuple] = {}
    libelles: dict[str, str] = {}
    for cellule in _feuille(contenu, FEUILLE_H):
        code = str(cellule.get("CC"))
        if code not in CAISSES_H or cellule.get("Type_depart") != "Ensemble":
            continue
        if cellule.get("Age") != "Ensemble" or cellule.get("Taux") not in TAUX:
            continue
        effectif = cellule.get("effectifs")
        if not isinstance(effectif, float) or effectif <= 0 or cellule.get("Sexe") not in SEXES:
            continue
        annee = int(cellule["Annee"])
        if annee < DEPUIS:
            continue
        cle = (code, CHAMPS_FS[cellule["Champ_FluxStock"]], SEXES[cellule["Sexe"]], annee,
               TAUX[cellule["Taux"]])
        _retenir(retenues, cle, str(cellule.get("Source") or ""), effectif)
        libelles[code] = str(cellule["Caisse"])
    series: dict = {}
    sources: dict = {}
    for (code, champ, sexe, annee, taux), ((_, source), effectif) in sorted(retenues.items()):
        ligne = series.setdefault(code, {}).setdefault(champ, {}).setdefault(sexe, {})
        ligne.setdefault(str(annee), {})[taux] = effectif
        sources.setdefault(code, set()).add(source)
    # Une année n'est gardée que si elle porte le taux plein et la décote ; la
    # surcote manque là où la caisse n'en sert pas (l'Agirc-Arrco) ou ne la
    # compte pas (les militaires du SRE), et la ligne « Ensemble » absente se
    # refait de la somme des conditions présentes.
    for code, champs in series.items():
        for champ, sexes in champs.items():
            for sexe, annees in sexes.items():
                for annee in list(annees):
                    conditions = annees[annee]
                    if not {"taux_plein", "decote"} <= set(conditions):
                        del annees[annee]
                        continue
                    conditions.setdefault("ensemble", sum(
                        conditions.get(t, 0.0) for t in ("taux_plein", "decote", "surcote")))
    return {"feuille": FEUILLE_H, "caisses": dict(sorted(libelles.items())),
            "sources": {code: sorted(s) for code, s in sorted(sources.items())},
            "series": series}


def liquidants_par_age(contenu: bytes) -> dict:
    """La table B, l'année la plus récente : ``{caisse: {âge: effectif}}``, en flux."""
    retenues: dict[tuple, tuple] = {}
    libelles: dict[str, str] = {}
    for cellule in _feuille(contenu, FEUILLE_B):
        code = str(cellule.get("CC"))
        if code not in CAISSES_B or cellule.get("Sexe") != "Ensemble":
            continue
        if cellule.get("Nb_trim") != "Ensemble" or cellule.get("Type_depart") != "Ensemble":
            continue
        effectif = cellule.get("effectifs")
        if (not isinstance(effectif, float) or effectif <= 0
                or cellule.get("Champ_FluxStock") != "Flux"):
            continue
        cle = (int(cellule["Année"]), code, str(cellule["Age"]))
        _retenir(retenues, cle, str(cellule.get("Source") or ""), effectif)
        libelles[code] = str(cellule["Caisse"])
    annee = max(cle[0] for cle in retenues)
    series: dict = {}
    for (an, code, age), (_, effectif) in sorted(retenues.items()):
        if an == annee:
            series.setdefault(code, {})[age] = effectif
    return {"feuille": FEUILLE_B, "annee": annee, "caisses": dict(sorted(libelles.items())),
            "series": series}


def droits_directs_par_age(contenu: bytes) -> dict:
    """La table C, tous régimes, l'année la plus récente :
    ``{champ: {sexe: {âge: [effectif, pension mensuelle moyenne]}}}``."""
    retenues: dict[tuple, tuple] = {}
    for cellule in _feuille(contenu, FEUILLE_C):
        if str(cellule.get("CC")) != "0000" or cellule.get("Champ") not in CHAMPS_C:
            continue
        if any(cellule.get(nom) != "Ensemble" for nom in ("Resid", "Naiss", "Liq", "StatutSNCF")):
            continue
        effectif, montant = cellule.get("effectifs"), cellule.get("m1")
        if not isinstance(effectif, float) or effectif <= 0 or cellule.get("Sexe") not in SEXES:
            continue
        age = str(cellule["Age"])
        if age == "Ensemble" and cellule.get("AgeQuin") != "Ensemble":
            continue
        cle = (int(cellule["Année"]), cellule["Champ"], SEXES[cellule["Sexe"]], age)
        _retenir(retenues, cle, str(cellule.get("Source") or ""),
                 [effectif, montant if isinstance(montant, float) else None])
    annee = max(cle[0] for cle in retenues)
    series: dict = {}
    sources: set[str] = set()
    for (an, champ, sexe, age), ((_, source), valeur) in sorted(retenues.items()):
        if an == annee:
            series.setdefault(champ, {}).setdefault(sexe, {})[age] = valeur
            sources.add(source)
    return {"feuille": FEUILLE_C, "annee": annee, "caisse": "0000",
            "sources": sorted(sources),
            "unite": "retraités, puis euros bruts par mois", "series": series}


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--classeurs", nargs="+", type=Path,
                           help="les classeurs déjà téléchargés")
    arguments = analyseur.parse_args(argv)
    if arguments.classeurs:
        telecharges = [(chemin.name, chemin.read_bytes()) for chemin in arguments.classeurs]
    else:
        telecharges = classeurs()
    titre_1, premier = classeur_portant(telecharges, FEUILLE_B)
    titre_2, second = classeur_portant(telecharges, FEUILLE_H)
    temoin = {
        "source": BASE,
        "fichiers": [titre_1, titre_2],
        "lu_le": date.today().isoformat(),
        "conditions_liquidation": conditions_liquidation(second),
        "liquidants_par_age": liquidants_par_age(premier),
        "droits_directs_par_age": droits_directs_par_age(premier),
    }
    SORTIE.write_text(json.dumps(temoin, ensure_ascii=False, indent=1) + "\n",
                      encoding="utf-8")
    print(f"Écrit {SORTIE.relative_to(RACINE)} ({SORTIE.stat().st_size // 1024} Ko)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
