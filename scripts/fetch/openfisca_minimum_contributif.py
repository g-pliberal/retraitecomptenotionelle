#!/usr/bin/env python3
"""Montants du minimum contributif, transcrits par OpenFisca-France-Pension.

    python scripts/fetch/openfisca_minimum_contributif.py

À quoi il sert. ``legislation/minimum_contributif.csv`` porte trois grandeurs :
le minimum contributif, le minimum MAJORÉ au titre des périodes cotisées, et le
plafond d'écrêtement de l'article L. 173-2. Les ancres du code — les décrets
qui fixent un montant — sont certifiées depuis la base LEGI ; mais le code
n'est pas réécrit à chaque revalorisation, et les montants réellement servis
entre deux ancres étaient SAISIS depuis des réponses ministérielles et des
publications de la Cnav, sans aucun recoupement machine.

OpenFisca-France-Pension transcrit ces montants circulaire par circulaire —
cinquante dates d'effet depuis 1984 pour le minimum, vingt et une depuis 2004
pour le majoré, et le plafond mensuel depuis 2012. Ce récupérateur les lit
dans son dépôt et les met à la convention du fichier : un montant PAR AN, celui
en vigueur au 1er janvier de chaque année.

Ce qu'il en fait, et ce qu'il n'en fait pas.

* Le vérificateur confronte les lignes SAISIES du fichier à cette série, et
  les verse au niveau ``haute`` quand elles s'y retrouvent : OpenFisca est une
  transcription tierce, jamais le producteur.
* Il ne touche pas aux ancres certifiées depuis le code : la source de ce
  récupérateur s'efface devant elles, comme le plafond ancien s'efface devant
  le *Journal officiel*.
* Il n'ajoute AUCUNE ligne. Le fichier est une table d'ancres — un montant
  n'y entre que s'il change —, et l'ajout d'une année reste une décision.

Unités. OpenFisca porte le minimum en francs jusqu'en 2001 ; la conversion est
celle de la loi, 6,55957 francs pour un euro. Le plafond est mensuel chez lui
et annuel dans le fichier : il est multiplié par douze.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = ("https://raw.githubusercontent.com/openfisca/openfisca-france-pension/"
          "master/openfisca_france_pension/parameters/retraites/secteur_prive/"
          "regime_general_cnav")

#: Mesure du fichier -> (fichier YAML, chemin dans le fichier, facteur annuel).
MESURES = {
    "montant_base": ("montant_mico.yaml", ("minimum_contributif", "annuel"), 1.0),
    "montant_majore": ("montant_mico.yaml", ("minimum_contributif_majore", "annuel"), 1.0),
    "plafond_ecretement": (
        "plafond_mico/minimum_contributif_plafond_mensuel.yaml", (), 12.0),
}

FRANCS_PAR_EURO = 6.55957
DERNIERE_ANNEE_EN_FRANCS = 2001

SORTIE = Path("data/brut/openfisca_minimum_contributif.json")


def _lire(url: str) -> str:
    demande = urllib.request.Request(
        url, headers={"User-Agent": "retraite-notionnelle/0.1"}
    )
    with urllib.request.urlopen(demande, timeout=120) as reponse:
        return reponse.read().decode("utf-8")


def _serie_datee(texte: str, chemin: tuple[str, ...]) -> dict[str, float]:
    """Lit ``values: {date: {value: montant}}`` au bout d'un chemin de clés."""
    import yaml

    noeud = yaml.safe_load(texte)
    for cle in chemin:
        noeud = noeud[cle]
    valeurs = {}
    for cle, contenu in (noeud.get("values") or {}).items():
        montant = (contenu or {}).get("value")
        if montant is not None:
            valeurs[str(cle)] = float(montant)
    return dict(sorted(valeurs.items()))


def annualiser(valeurs: dict[str, float], facteur: float) -> dict[int, float]:
    """Montant EN VIGUEUR AU 1er JANVIER de chaque année, en euros par an."""
    dates = sorted(valeurs)
    if not dates:
        return {}
    resultat: dict[int, float] = {}
    for annee in range(int(dates[0][:4]), date.today().year + 2):
        applicables = [d for d in dates if d <= f"{annee}-01-01"]
        if not applicables:
            continue
        montant = valeurs[applicables[-1]] * facteur
        if int(applicables[-1][:4]) <= DERNIERE_ANNEE_EN_FRANCS:
            montant /= FRANCS_PAR_EURO
        resultat[annee] = round(montant, 2)
    return resultat


def main() -> int:
    series: dict[str, dict[int, float]] = {}
    changements: dict[str, float] = {}
    try:
        for mesure, (fichier, chemin, facteur) in MESURES.items():
            datees = _serie_datee(_lire(f"{RACINE}/{fichier}"), chemin)
            series[mesure] = annualiser(datees, facteur)
            # Chaque date d'effet, telle quelle : c'est ce que le vérificateur
            # oppose à une ANCRE, qui porte l'année où un montant a changé.
            for jour, montant in datees.items():
                montant *= facteur
                if int(jour[:4]) <= DERNIERE_ANNEE_EN_FRANCS:
                    montant /= FRANCS_PAR_EURO
                changements[f"{mesure}|{jour}"] = round(montant, 2)
            print(f"OK      {mesure:<20} {len(series[mesure])} années, "
                  f"{len(datees)} dates d'effet")
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"OpenFisca indisponible : {erreur}", file=sys.stderr)
        return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": RACINE,
            "recupere_le": date.today().isoformat(),
            "unite": "euros par an, montant en vigueur au 1er janvier",
            "serie": {
                f"{mesure}|{annee}": montant
                for mesure, par_annee in series.items()
                for annee, montant in sorted(par_annee.items())
            },
            "changements": dict(sorted(changements.items())),
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"écrit dans {SORTIE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
