#!/usr/bin/env python3
"""Courbe des taux sans risque de la zone euro, publiée par la BCE.

    python scripts/fetch/bce_courbe_taux.py
    python scripts/verifier_donnees.py --appliquer   # certifie la référence

À QUOI ELLE SERT. Le pilier de capitalisation obligatoire de la proposition
place 5 % de la rémunération sur des titres sans risque, à plusieurs
maturités — longues en début de carrière, courtes à l'approche du départ. Il
faut donc, pour chaque maturité, le taux auquel un versement d'aujourd'hui se
place, et, pour les versements des années suivantes, le taux que le marché
anticipe déjà : ce sont les taux FORWARD, et ils se déduisent de cette même
courbe, sans hypothèse maison.

POURQUOI CETTE COURBE-LÀ. La BCE publie chaque jour ouvré la structure par
terme des titres d'État de la zone euro notés AAA, estimée par le modèle de
Svensson : c'est la définition opérationnelle du taux sans risque en euro, et
c'est le producteur qui la publie. La courbe « tous émetteurs » (``G_A``)
inclut la France et rend davantage — l'écart mesure un risque de crédit, pas un
rendement acquis. Retenir la courbe AAA est donc le choix PRUDENT : un régime
obligatoire qui promet une rente ne peut pas compter sur une prime de risque.
L'écart est documenté dans `docs/methodologie.md` ; ce script relève en regard
le rendement de l'OAT française à dix ans, pour que la note reste chiffrée.

CE QUE LA COURBE PORTE, ET DANS QUELLE UNITÉ. Les taux publiés sont des taux
zéro-coupon à COMPOSITION CONTINUE, exprimés en pourcentage. Le dépôt les garde
tels que la BCE les publie, en fraction, et c'est le modèle qui les ramène en
taux annuels par ``exp(r) - 1`` : convertir à la saisie ferait entrer un calcul
dans une donnée de référence.
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

#: Portail de données de la BCE, service SDMX. ``YC`` est le jeu de la courbe
#: des taux, ``B`` la fréquence quotidienne, ``U2`` la zone euro,
#: ``G_N_A`` les émetteurs souverains notés AAA, ``SV_C_YM`` l'estimation de
#: Svensson en composition continue, ``SR_<n>Y`` le taux zéro-coupon à n ans.
BASE = "https://data-api.ecb.europa.eu/service/data"
MATURITES = tuple(range(1, 31))
URL_COURBE = (
    f"{BASE}/YC/B.U2.EUR.4F.G_N_A.SV_C_YM."
    + "+".join(f"SR_{n}Y" for n in MATURITES)
    + "?lastNObservations=1&format=csvdata&detail=dataonly"
)

#: Rendement de l'emprunt d'État français à dix ans (critère de convergence),
#: mensuel. Ne sert à aucun calcul : il chiffre l'écart entre la courbe AAA
#: retenue et ce que la France emprunte réellement.
URL_OAT = (
    f"{BASE}/IRS/M.FR.L.L40.CI.0000.EUR.N.Z"
    "?lastNObservations=1&format=csvdata&detail=dataonly"
)

SORTIE = Path("data/brut/bce_courbe_taux.json")


def _telecharger(url: str) -> list[dict[str, str]]:
    demande = urllib.request.Request(
        url, headers={"User-Agent": "retraite-notionnelle/0.1"}
    )
    with urllib.request.urlopen(demande, timeout=120) as reponse:
        texte = reponse.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(texte)))


def extraire_courbe(lignes: list[dict[str, str]]) -> tuple[str, dict[int, float]]:
    """Rend la date d'observation et la courbe, maturité -> taux en fraction.

    Toutes les séries sont demandées à leur dernière observation : elles
    tombent normalement le même jour ouvré. Si l'une d'elles retarde, la date
    retenue est la plus récente et la maturité en retard est écartée — une
    courbe qui mêlerait deux jours ne serait cohérente ni en niveau ni en pente.
    """
    observations: dict[int, tuple[str, float]] = {}
    for ligne in lignes:
        maturite = int(ligne["DATA_TYPE_FM"].removeprefix("SR_").removesuffix("Y"))
        observations[maturite] = (ligne["TIME_PERIOD"], float(ligne["OBS_VALUE"]) / 100.0)
    if not observations:
        return "", {}
    date_courbe = max(jour for jour, _ in observations.values())
    return date_courbe, {
        maturite: taux
        for maturite, (jour, taux) in sorted(observations.items())
        if jour == date_courbe
    }


def main() -> int:
    try:
        date_courbe, courbe = extraire_courbe(_telecharger(URL_COURBE))
        oat = _telecharger(URL_OAT)
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"portail de données BCE indisponible : {erreur}", file=sys.stderr)
        return 1

    manquantes = [n for n in MATURITES if n not in courbe]
    if manquantes:
        print(
            f"maturités absentes de la courbe du {date_courbe} : "
            + ", ".join(f"{n} ans" for n in manquantes),
            file=sys.stderr,
        )
        return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(
            {
                "source": URL_COURBE,
                "recupere_le": date.today().isoformat(),
                "date_courbe": date_courbe,
                "producteur": (
                    "Banque centrale européenne, qui estime et publie la courbe "
                    "des taux des titres souverains AAA de la zone euro. "
                    "Producteur de la donnée, non transcription."
                ),
                "unite": (
                    "taux zéro-coupon à composition continue, en fraction "
                    "(la BCE publie en pourcentage ; la division par 100 est "
                    "un changement d'unité, pas un calcul)"
                ),
                "courbe": {
                    f"courbe|{date_courbe}|{maturite}": taux
                    for maturite, taux in courbe.items()
                },
                "oat_10_ans": {
                    ligne["TIME_PERIOD"]: float(ligne["OBS_VALUE"]) / 100.0
                    for ligne in oat
                },
            },
            ensure_ascii=False, indent=2, sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    ecart = ""
    if oat:
        taux_oat = float(oat[-1]["OBS_VALUE"]) / 100.0
        ecart = (
            f" ; OAT 10 ans {taux_oat:.2%} en {oat[-1]['TIME_PERIOD']}, soit "
            f"{(taux_oat - courbe[10]) * 10000:+.0f} points de base au-dessus "
            "de la courbe AAA"
        )
    print(
        f"{SORTIE} : courbe du {date_courbe}, {len(courbe)} maturités — "
        f"1 an {courbe[1]:.2%}, 10 ans {courbe[10]:.2%}, "
        f"30 ans {courbe[30]:.2%}{ecart}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
