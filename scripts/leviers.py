#!/usr/bin/env python3
"""Les trois leviers qui équilibreraient chaque système, confrontés à ceux du COR.

    python scripts/leviers.py              # le système actuel contre le COR
    python scripts/leviers.py --systemes   # et les six systèmes

Ce que la pension, le taux de prélèvement ou l'âge devrait faire, seul, pour
équilibrer chaque année, et le pension gap et le tax gap sur les horizons du
COR (``retraite_notionnelle.leviers`` ; action 138, étape 3), contre la
figure 2.24 et le tableau 2.11 du rapport annuel du COR de juin 2026
(``tests/temoins/cor_leviers_2026.json``), sous la référence du COR, celle de
la page Coût. Les tableaux s'écrivent en Markdown.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle import Parametres  # noqa: E402
from retraite_notionnelle.leviers import HORIZONS_COR, leviers_du_modele  # noqa: E402

TEMOIN = RACINE / "tests" / "temoins" / "cor_leviers_2026.json"
ANNEES = (2030, 2040, 2045, 2050, 2060, 2070)


def _nombre(valeur: float | None, decimales: int = 1, signe: bool = True) -> str:
    if valeur is None:
        return "—"
    texte = f"{valeur:+.{decimales}f}" if signe else f"{valeur:.{decimales}f}"
    return texte.replace("-", "−").replace(".", ",")


def cor() -> dict:
    """Les leviers du COR, comme le module les rend : variation relative de
    la pension, relèvement du taux en fraction, recul de l'âge en années."""
    temoin = json.loads(TEMOIN.read_text(encoding="utf-8"))
    leviers, ecarts = temoin["leviers"], temoin["ecarts_sur_horizon"]

    def ecart(nom: str, annee: int, relatif: bool = False) -> float:
        equilibre, spontane = (leviers[nom][serie][str(annee)] for serie in ("equilibre", "spontane"))
        return equilibre / spontane - 1.0 if relatif else equilibre - spontane

    return {
        "annuels": {annee: {"pension": ecart("pension_relative", annee, True),
                            "prelevement": ecart("taux_prelevement", annee),
                            "age": ecart("age", annee)} for annee in ANNEES},
        "horizons": {fin: {"pension_gap": ecarts["pension_gap"][str(fin)],
                           "tax_gap": ecarts["tax_gap"][str(fin)] / 100}
                     for fin in HORIZONS_COR},
        "age_spontane": {annee: leviers["age"]["spontane"][str(annee)] for annee in ANNEES},
    }


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--systemes", action="store_true",
                           help="chiffre aussi les leviers des six systèmes")
    arguments = analyseur.parse_args(argv)

    publie = cor()
    actuel = leviers_du_modele(Parametres(), "actuel")
    print("| Système actuel | " + " | ".join(map(str, ANNEES)) + " |")
    print("|---|" + "---|" * len(ANNEES))
    for nom, libelle, echelle, decimales in (
            ("pension", "Pension, en %", 100, 1),
            ("prelevement", "Taux de prélèvement, en points", 100, 2),
            ("age", "Âge, en années", 1, 2)):
        for source, valeurs in (("modèle", {a: getattr(actuel.annuels[a], nom) for a in ANNEES}),
                                ("COR", {a: publie["annuels"][a][nom] for a in ANNEES})):
            print(f"| {libelle}, {source} | " + " | ".join(
                _nombre(valeurs[a] * echelle, decimales) for a in ANNEES) + " |")
    print("| Âge spontané du COR | " + " | ".join(
        _nombre(publie["age_spontane"][a], 1, signe=False) for a in ANNEES) + " |")
    print()
    print("| Depuis 2026, jusqu'en | " + " | ".join(map(str, HORIZONS_COR)) + " |")
    print("|---|" + "---|" * len(HORIZONS_COR))
    for nom, libelle in (("pension_gap", "Pension gap, en %"), ("tax_gap", "Tax gap, en points")):
        print(f"| {libelle}, modèle | " + " | ".join(
            _nombre(100 * getattr(actuel.horizons[fin], nom), 2) for fin in HORIZONS_COR) + " |")
        print(f"| {libelle}, COR | " + " | ".join(
            _nombre(100 * publie["horizons"][fin][nom], 2) for fin in HORIZONS_COR) + " |")

    if arguments.systemes:
        from retraite_notionnelle.cout import SCENARIOS

        print()
        print("| Les six systèmes | Âge 2045 | Âge 2070 | Pension 2070 | Taux 2070 "
              "| Pension gap 2070 | Tax gap 2070 |")
        print("|---|---|---|---|---|---|---|")
        for scenario, libelle in SCENARIOS:
            systeme = leviers_du_modele(Parametres(), scenario)
            fin = systeme.annuels[2070]
            print(f"| {libelle} | {_nombre(systeme.annuels[2045].age, 2)} | "
                  f"{_nombre(fin.age, 2)} | {_nombre(100 * fin.pension)} | "
                  f"{_nombre(100 * fin.prelevement, 2)} | "
                  f"{_nombre(100 * systeme.horizons[2070].pension_gap)} | "
                  f"{_nombre(100 * systeme.horizons[2070].tax_gap, 2)} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
