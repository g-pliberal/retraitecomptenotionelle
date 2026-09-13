#!/usr/bin/env python3
"""Récupération des barèmes de l'Ircantec auprès de la Caisse des dépôts.

    python scripts/fetch/cdc_ircantec.py

La Caisse des dépôts **gère** l'Ircantec : elle est le producteur de la donnée,
pas un tiers qui la recopie. Elle publie deux fichiers CSV, discrets mais
propres, sur son site des politiques sociales :

* ``IRC_BAR_02_ValPt_SalRef.csv`` — valeur du point au 31 décembre et salaire de
  référence, chaque année depuis 1971 ;
* ``IRC_BAR_01_txcotis.csv`` — taux théoriques et appelés sur les tranches A et
  B, et le **taux d'appel**, sur la même période. Les trois sont versés : le
  taux d'appel dans ``valeurs_point.csv``, où il entre dans le prix du point ;
  les taux APPELÉS des deux tranches dans la trace, parce qu'ils appartiennent
  à la fiche du régime et non à une série de barème. Ce script ne lisait que le
  premier, et la fiche portait 5,75 % sur toute la période 1971-2008 quand le
  taux appelé de la tranche A valait 2,10 % jusqu'en 1982 — un agent des années
  1970 recevait deux fois et demie les points que le barème lui donnait.

C'est ce qui permet de faire passer l'Ircantec de ``haute`` à ``certifiee`` :
jusqu'ici ses barèmes venaient d'OpenFisca, transcription tierce. Les deux
sources s'accordent sur cinquante des cinquante et une années ; le seul écart
porte sur le taux d'appel de 1991, et c'est le producteur qui tranche.

La convention de date coïncide avec celle du modèle : « valeur du point au 31
décembre » est exactement la valeur en vigueur à la fin de l'année, celle que
``scripts/fetch/openfisca_points.py`` reconstitue pour les autres régimes.

Ne couvre ni l'IPACTE ni l'IGRANTE, les régimes auxquels l'Ircantec a succédé en
1971, ni les années postérieures à 2021 : elles restent transcrites d'OpenFisca.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = "https://politiques-sociales.caissedesdepots.fr/sites/default/files"
VALEURS = "IRC_BAR_02_ValPt_SalRef.csv"
TAUX = "IRC_BAR_01_txcotis.csv"
SORTIE = Path("data/brut/cdc_ircantec.json")


def _nombre(texte: str) -> float:
    """Lit un nombre à la française, avec virgule décimale et signe pourcent."""
    return float(texte.replace(" ", "").replace(" ", "")
                 .replace(",", ".").replace("%", "").strip())


def _telecharger(nom: str) -> list[dict[str, str]]:
    demande = urllib.request.Request(
        f"{RACINE}/{nom}", headers={"User-Agent": "retraite-notionnelle/0.1"}
    )
    with urllib.request.urlopen(demande, timeout=120) as reponse:
        texte = reponse.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(texte), delimiter=";"))


def main() -> int:
    try:
        valeurs = _telecharger(VALEURS)
        taux = _telecharger(TAUX)
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"Caisse des dépôts indisponible : {erreur}", file=sys.stderr)
        return 1

    serie: dict[str, float] = {}
    for ligne in valeurs:
        annee = int(ligne["Annee"])
        serie[f"ircantec|{annee}|valeur_service"] = _nombre(ligne["val_point_31-12"])
        serie[f"ircantec|{annee}|salaire_reference"] = _nombre(ligne["sal_ref"])
    #: Taux APPELÉS des deux tranches, année par année. Ils ne vont pas dans
    #: `valeurs_point.csv` — ce sont des paramètres de fiche, pas un barème de
    #: point — mais ils sont consignés ici, avec leur source, parce que c'est
    #: d'eux que la fiche du régime tire ses `taux_cotisation_retraite`.
    appeles: dict[str, dict[str, float]] = {}
    for ligne in taux:
        annee = int(ligne["Annee"])
        serie[f"ircantec|{annee}|taux_appel"] = _nombre(ligne["taux_appel"]) / 100.0
        appeles[str(annee)] = {
            "tranche_a": _nombre(ligne["tx_cotis_appel_TA"]) / 100.0,
            "tranche_b": _nombre(ligne["tx_cotis_appel_TB"]) / 100.0,
        }

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": f"{RACINE}/{VALEURS}, {RACINE}/{TAUX}",
            "recupere_le": date.today().isoformat(),
            "regle_annuelle": "valeur du point au 31 décembre, telle que publiée",
            "taux_appeles": appeles,
            "serie": dict(sorted(serie.items())),
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    annees = sorted({int(cle.split("|")[1]) for cle in serie})
    print(f"{len(serie)} valeurs écrites dans {SORTIE}")
    print(f"Couverture {annees[0]}-{annees[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
