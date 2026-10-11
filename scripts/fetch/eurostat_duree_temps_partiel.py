#!/usr/bin/env python3
"""Durée habituelle du travail des salariés à temps partiel et à temps complet.

    python scripts/fetch/eurostat_duree_temps_partiel.py

CE QU'ON VIENT CHERCHER, ET POURQUOI
-------------------------------------
La part du temps partiel (``insee_temps_partiel.py``) dit combien de personnes
travaillent à temps partiel, non combien d'heures : un temps partiel de femme
compte 23,5 heures par semaine en 2025, celui d'un homme 22,1, quand un temps
complet en compte 38 à 39. Le rapport des deux, la QUOTITÉ, est ce qui reste
du salaire en équivalent temps plein dans le salaire de l'année, que la pension
compte. La population de la page Coût (action 136, étape 6) en a besoin, sexe
par sexe et âge par âge.

POURQUOI EUROSTAT, ET NON L'INSEE QUI PRODUIT LA DONNÉE
--------------------------------------------------------
L'INSEE mesure la durée dans l'enquête Emploi, mais ne la publie par sexe que
dans le texte de sa fiche « Temps partiel », une année par édition, et sans la
durée d'un temps complet ; aucun jeu de Melodi ne la porte. Eurostat la
rediffuse, de l'enquête française sur les forces de travail, en série depuis
1983 : ``lfsa_ewhuis``, la durée habituelle hebdomadaire dans l'emploi
principal, par statut, temps de travail, âge, sexe et profession. Elle redonne
la fiche de l'INSEE : 23,5 heures pour les femmes en 2025, comme elle, et 22,1
pour les hommes, quand la fiche, qui exclut les apprentis, en dit 21,9.

Le fichier produit, ``data/brut/eurostat_duree_temps_partiel.json``, est le
document source : il n'est pas lu par le modèle, seulement par
``scripts/verifier_donnees.py``.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

TABLE = "lfsa_ewhuis"

#: Les salariés, toutes professions, à temps partiel et à temps complet, des
#: deux sexes et ensemble, tous âges et trois tranches. Sans ces filtres, la
#: table entière ne se sert qu'en différé.
FILTRES = ("format=JSON&geo=FR&isco08=TOTAL&wstatus=SAL&unit=HR"
           "&worktime=PT&worktime=FT&sex=F&sex=M&sex=T"
           "&age=Y15-24&age=Y25-54&age=Y_GE50&age=Y_GE15")

SORTIE = Path("data/brut/eurostat_duree_temps_partiel.json")


def aplatir(charge: dict) -> tuple[dict[str, float], dict[str, str]]:
    """Aplatit le JSON-stat en « temps|âge|sexe|année » -> heures, et les
    drapeaux des mêmes cellules.

    L'ordre est ligne-majeur : le dernier axe varie le plus vite, et les pas se
    recalculent depuis la fin (``eurostat_profil_salaire_secteur.py``).
    """
    axes, tailles = charge["id"], charge["size"]
    inverse = {
        axe: {position: code for code, position
              in charge["dimension"][axe]["category"]["index"].items()}
        for axe in axes
    }
    pas = [1] * len(tailles)
    for rang in range(len(tailles) - 2, -1, -1):
        pas[rang] = pas[rang + 1] * tailles[rang + 1]

    def cle(position: str) -> str:
        reste = int(position)
        cellule = {axe: inverse[axe][reste // pas[rang] % tailles[rang]]
                   for rang, axe in enumerate(axes)}
        return "|".join(cellule[axe] for axe in ("worktime", "age", "sex", "time"))

    heures = {cle(position): valeur for position, valeur in charge["value"].items()
              if valeur is not None}
    drapeaux = {cle(position): drapeau
                for position, drapeau in (charge.get("status") or {}).items()}
    return dict(sorted(heures.items())), dict(sorted(drapeaux.items()))


def main() -> int:
    url = f"{BASE}{TABLE}?{FILTRES}"
    try:
        demande = urllib.request.Request(url, headers=ENTETES)
        with urllib.request.urlopen(demande, timeout=120) as reponse:
            charge = json.load(reponse)
    except urllib.error.HTTPError as erreur:
        print(f"Erreur HTTP {erreur.code} sur {TABLE} : {erreur.reason}",
              file=sys.stderr)
        return 1
    except urllib.error.URLError as erreur:
        print(f"Réseau indisponible : {erreur.reason}", file=sys.stderr)
        return 1
    if "value" not in charge:
        print(f"{TABLE} ne rend aucune donnée pour la France : "
              f"{charge.get('error')}", file=sys.stderr)
        return 1

    heures, drapeaux = aplatir(charge)
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({"table": TABLE, "filtres": FILTRES, "heures": heures,
                    "drapeaux": drapeaux}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    annees = sorted({cle.rsplit("|", 1)[1] for cle in heures})
    print(f"{len(heures)} valeurs écrites dans {SORTIE} ({annees[0]}-{annees[-1]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
