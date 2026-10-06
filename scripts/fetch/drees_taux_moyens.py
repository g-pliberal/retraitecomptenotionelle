#!/usr/bin/env python3
"""Les taux de cotisation MOYENS de l'Agirc-Arrco, depuis le modèle Trajectoire.

    python scripts/fetch/drees_taux_moyens.py
    python scripts/fetch/drees_taux_moyens.py --cor Donnees_RA2026_P3_2.xlsx

POURQUOI. Les fiches de l'Arrco et de l'Agirc portent le taux contractuel
MINIMAL de chaque année : 4 % sur la tranche 1 de l'Arrco jusqu'en 1995, 8 %
sur la tranche B de l'Agirc jusqu'en 1993. C'est le plancher que l'accord
imposait, non le taux que les entreprises cotisaient : la plupart cotisaient
au-dessus, et les points acquis suivaient leur taux. Les cas types du COR
cotisent au taux MOYEN — « pour l'Agirc-Arrco, les cotisations sont supposées
prélevées au taux moyen » (rapport de juin 2026, notes des figures 3.3 et 3.4)
—, et la page Coût, qui se lit contre lui, en suit la convention
(``taux_moyens_agirc_arrco.csv``, action 147 de la feuille de route, étape 10).

LA SOURCE. Le COR fait calculer ses cas types par un module du modèle
Trajectoire de la DREES, publié sous licence EUPL 1.2. Ses paramètres de
cotisation (``inst/extdata/trajectoire/paramCotis.csv``) portent, année par
année, le taux contractuel moyen de la tranche 1 et de la tranche 2 de
l'Arrco, de la tranche B et de la tranche C de l'Agirc, hors taux d'appel ;
le module de calcul des cas types en tire les points
(``R/3-points.R`` : ``pmin(remuneration, pss) * txCotARRCOsalempl_t1 /
valeurPtAcquisition``). Le fichier est lu au commit de la version 1.1.2
(avril 2025), la dernière publiée : la même série que le classeur de 2020
dont elle descend (``hypo_taux_cotisation_et_legislation_2020_drees.xlsx``,
colonnes ``TxCot_*`` à côté des minimums ``TxCotMIN_*``).

LE CONTRÔLE. La figure 3.1 du rapport de juin 2026 trace le taux de
cotisation d'un non-cadre sous le plafond, Cnav et Agirc-Arrco, « avec taux
minimum obligatoire » et « avec taux moyen », de 1990 à 2025. Leur écart est
celui des deux taux de la tranche 1, multiplié par le taux d'appel : c'est un
contrôle publié par un autre que la DREES. ``--cor`` en fige les deux lignes
dans ``tests/temoins/cor_taux_cotisation.json`` ; ``tests/test_taux_moyens.py``
y confronte la série.

Le fichier produit, ``data/brut/drees_taux_moyens.json``, est le document
source : le modèle ne le lit pas, ``scripts/verifier_donnees.py`` le confronte
à ``data/reference/regimes/taux_moyens_agirc_arrco.csv``.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_xlsx import feuilles  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
#: Le commit de la version 1.1.2 de Trajectoire : la version n'a pas
#: d'étiquette, et une branche bougerait sous le témoin.
COMMIT = "0963b5775b3898dc155b78095232f9f5a1d59db0"
URL = ("https://git.drees.fr/drees_code_public/modeles/trajectoire/-/raw/"
       f"{COMMIT}/inst/extdata/trajectoire/paramCotis.csv")
URL_COR = ("https://www.cor-retraites.fr/sites/default/files/2026-06/"
           "Donn%C3%A9es_RA2026_P3_2.xlsx")
SORTIE = RACINE / "data" / "brut" / "drees_taux_moyens.json"
TEMOIN_COR = RACINE / "tests" / "temoins" / "cor_taux_cotisation.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Les colonnes de ``paramCotis.csv`` que la série reprend : taux
#: contractuels moyens, hors taux d'appel, salarié et employeur ensemble.
COLONNES = ("txCotARRCOsalempl_t1", "txCotARRCOsalempl_t2",
            "txCotAGIRCsalempl_TB", "txCotAGIRCsalempl_TC")
#: La feuille du classeur du COR, et le titre de ses deux lignes.
FEUILLE_COR = "Fig 3.1"
LIGNES_COR = {"Avec taux minimum obligatoire AGIRC-ARRCO": "minimum",
              "Avec taux moyen AGIRC-ARRCO": "moyen"}


def _telecharger(url: str) -> bytes:
    requete = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=120) as reponse:
        return reponse.read()


def serie(texte: str) -> dict[str, dict[str, float]]:
    """Colonne -> année -> taux, des années où le taux est publié et non nul."""
    valeurs: dict[str, dict[str, float]] = {colonne: {} for colonne in COLONNES}
    for ligne in csv.DictReader(io.StringIO(texte)):
        annee = str(int(float(ligne["annee"])))
        for colonne in COLONNES:
            brut = (ligne.get(colonne) or "").strip()
            if brut in ("", "NA") or float(brut) <= 0.0:
                continue
            valeurs[colonne][annee] = float(brut)
    vides = [colonne for colonne, table in valeurs.items() if not table]
    if vides:
        raise SystemExit(f"paramCotis.csv : colonnes vides ou absentes {vides}")
    return valeurs


def lignes_cor(donnees: bytes) -> dict[str, dict[str, float]]:
    """Les deux lignes de la figure 3.1 : taux total par année, 1990-2025."""
    grille = feuilles(donnees)[FEUILLE_COR]
    rangs = sorted({rang for rang, _ in grille})
    annees: list[int] = []
    lues: dict[str, dict[str, float]] = {}
    for rang in rangs:
        cellules = [grille[(r, c)] for (r, c) in sorted(grille) if r == rang]
        if cellules and all(isinstance(v, float) for v in cellules) and cellules[0] == 1990:
            annees = [int(v) for v in cellules]
            continue
        titre = cellules[0] if cellules and isinstance(cellules[0], str) else None
        if titre in LIGNES_COR and annees:
            lues[LIGNES_COR[titre]] = {
                str(annee): valeur for annee, valeur in zip(annees, cellules[1:])}
    if set(lues) != set(LIGNES_COR.values()):
        raise SystemExit(f"{FEUILLE_COR} : lignes trouvées {sorted(lues)}")
    return lues


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyseur.add_argument("--cor", nargs="?", const="", default=None,
                           help="fige aussi la figure 3.1 du COR (classeur local "
                                "ou, sans chemin, téléchargé)")
    arguments = analyseur.parse_args(argv)
    try:
        texte = _telecharger(URL).decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError) as erreur:
        print(f"échec du téléchargement : {erreur}", file=sys.stderr)
        return 1
    valeurs = serie(texte)
    document = {
        "source": URL,
        "recupere_le": date.today().isoformat(),
        "licence": "EUPL 1.2 (modèle Trajectoire, DREES)",
        "description": ("Taux contractuels moyens de l'Arrco (tranches 1 et 2) "
                        "et de l'Agirc (tranches B et C), hors taux d'appel"),
        "valeurs": valeurs,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(document, ensure_ascii=False, indent=1,
                                 sort_keys=True) + "\n", encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} : "
          + ", ".join(f"{c} {min(t)}-{max(t)}" for c, t in valeurs.items()))
    if arguments.cor is not None:
        donnees = (Path(arguments.cor).read_bytes() if arguments.cor
                   else _telecharger(URL_COR))
        temoin = {
            "source": URL_COR,
            "feuille": FEUILLE_COR,
            "titre": ("Taux de cotisation pour la retraite d'un salarié non-cadre "
                      "du secteur privé, sous le plafond, Cnav et Agirc-Arrco, "
                      "parts salariale et employeur"),
            **lignes_cor(donnees),
        }
        TEMOIN_COR.write_text(json.dumps(temoin, ensure_ascii=False, indent=1,
                                         sort_keys=True) + "\n", encoding="utf-8")
        print(f"{TEMOIN_COR.relative_to(RACINE)} : {len(temoin['moyen'])} années")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
