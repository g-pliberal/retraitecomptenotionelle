"""La pension des cas types en 2024, régime principal par régime principal, contre Ancetre.

    python scripts/controle_ancetre.py            # le tableau, en Markdown
    python scripts/controle_ancetre.py --cas      # et chaque cas type

Ce que la grille de la page Coût sert en 2024, sous le scénario 1, en euros
de 2024 par mois, contre la pension brute moyenne de droit direct que le
modèle Ancetre de la DREES publie par régime principal (rapport annuel du COR
de juin 2026, tableau 3.2 ; ``tests/temoins/cor_pension_regime_principal_2026.json``).
Le calcul est dans ``retraite_notionnelle.controle_ancetre``, qui dit ce que
l'écart mesure (action 138, étape 3).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.controle_ancetre import confronter, controle  # noqa: E402

TEMOIN = RACINE / "tests" / "temoins" / "cor_pension_regime_principal_2026.json"
NOMS = {"ensemble": "Ensemble", "regime_general": "Régime général",
        "fpe_civils": "FPE civils", "fpe_militaires": "FPE militaires",
        "cnracl": "CNRACL", "regimes_speciaux": "Régimes spéciaux",
        "msa_non_salaries": "MSA non-salariés",
        "professions_liberales": "Professions libérales"}


def _euros(valeur: float) -> str:
    return f"{valeur:,.0f}".replace(",", " ")


def _pour_cent(rapport: float) -> str:
    return f"{100 * (rapport - 1):+.0f} %".replace("-", "−")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--cas", action="store_true", help="la pension de chaque cas type")
    arguments = analyseur.parse_args(argv)

    pensions, regimes = controle()
    temoin = json.loads(TEMOIN.read_text(encoding="utf-8"))
    print("| Régime principal | Grille | Ancetre, carrières complètes | Écart "
          "| Ancetre, tous | Écart |")
    print("|---|---:|---:|---:|---:|---:|")
    for ecart in confronter(regimes, temoin):
        print(f"| {NOMS.get(ecart.ligne, ecart.ligne)} | {_euros(ecart.modele)} "
              f"| {_euros(ecart.carriere_complete)} | {_pour_cent(ecart.rapport)} "
              f"| {_euros(ecart.tous)} | {_pour_cent(ecart.rapport_tous)} |")
    if arguments.cas:
        print()
        print("| Cas type | Pension de 2024 |")
        print("|---|---:|")
        for code, pension in pensions.items():
            print(f"| {code} | {_euros(pension)} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
