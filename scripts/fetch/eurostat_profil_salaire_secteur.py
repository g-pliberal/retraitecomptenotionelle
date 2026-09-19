#!/usr/bin/env python3
"""Profil de salaire par âge et par secteur, enquête européenne sur les salaires.

    python scripts/fetch/eurostat_profil_salaire_secteur.py

CE QU'ON VIENT CHERCHER, ET POURQUOI
-------------------------------------
Les régimes spéciaux — IEG, SNCF, RATP, Banque de France — portaient le profil
salarial des employés du privé, faute de mieux : aucune source française ne
ventile le salaire par âge pour ces populations, et le relevé d'impasses est
sous l'action correspondante de la feuille de route.

L'enquête européenne sur la structure des salaires en donne une approche, et
c'est la seule. Elle ventile le salaire moyen par ÂGE et par SECTION de la
nomenclature d'activités, et deux sections tombent sur le périmètre d'un régime
plutôt qu'à côté :

* ``D`` — production et distribution d'électricité et de gaz : c'est le champ
  du statut des industries électriques et gazières, donc de la CNIEG ;
* ``H`` — transports et entreposage : plus large que la SNCF et la RATP, mais
  c'est là qu'elles sont.

CE QUE CETTE SOURCE N'EST PAS, ET IL FAUT LE LIRE AVANT DE S'EN SERVIR
-----------------------------------------------------------------------
Un profil de carrière. Elle est AGRÉGÉE par secteur : elle mélange l'effet
d'âge et un effet de composition, comme tout profil qui ne croise pas la
profession. Aucune des trois sources du dépôt ne croise les trois dimensions —
vérifié chez Eurostat comme chez l'INSEE : on a âge × secteur, ou
secteur × profession, jamais les deux.

Elle ne sert donc qu'en RELATIF : le rapport de la pente d'un secteur à celle
de l'ensemble de l'économie, appliqué à la forme intra-catégorie. Cela suppose
que ce rapport est le même à l'intérieur des catégories qu'en agrégé, ce que
rien ne démontre. ``docs/limites.md`` le dit.

DEUX VAGUES, ET C'EST CE QUI PERMET DE TRIER
----------------------------------------------
L'enquête est quadriennale. Les millésimes 2018 et 2022 sont les deux que
l'API rend pour la France ; 2010 et 2014 ne répondent pas, 2006 n'a pas la
dimension d'activité. Deux points suffisent à écarter ce qui n'est que du
bruit : le facteur de l'électricité-gaz vaut 1,41 puis 1,35, celui des
transports 0,928 puis 0,931 — mais celui des mines passe de 0,93 à 1,19 et
celui des spectacles de 0,83 à 1,08. Les deux derniers sont de petits secteurs,
et leurs régimes gardent donc le profil du privé.

La France ne publie que trois tranches d'âge à ce niveau : moins de 30 ans,
30-49 ans, 50 ans et plus.

Le fichier produit, ``data/brut/eurostat_profil_salaire_secteur.json``, est le
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

#: Les deux vagues que l'API rend pour la France, sous le nom de leur table.
#: ``indic_se=ERN`` est le salaire brut : sans ce filtre, les primes d'heures
#: supplémentaires occupent les mêmes cellules et écrasent les salaires.
VAGUES = {"2018": "earn_ses18_20", "2022": "earn_ses22_20"}

FILTRES = "format=JSON&geo=FR&sex=T&unit=EUR&indic_se=ERN"

SORTIE = Path("data/brut/eurostat_profil_salaire_secteur.json")


def aplatir(charge: dict) -> dict[str, float]:
    """Aplatit le JSON-stat en « section|tranche » -> salaire mensuel moyen.

    L'ordre est ligne-majeur : le dernier axe varie le plus vite. Les pas se
    recalculent donc depuis la fin, et non depuis le début — les prendre à
    l'envers donne des valeurs plausibles pour les mauvaises cellules, ce qui
    ne se voit pas.
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

    resultat: dict[str, float] = {}
    for position, valeur in charge["value"].items():
        if valeur is None:
            continue
        reste = int(position)
        cellule = {axe: inverse[axe][reste // pas[rang] % tailles[rang]]
                   for rang, axe in enumerate(axes)}
        if cellule.get("indic_se", "ERN") != "ERN":
            continue
        resultat[f"{cellule['nace_r2']}|{cellule['age']}"] = valeur
    return dict(sorted(resultat.items()))


def main() -> int:
    vagues: dict[str, dict[str, float]] = {}
    for millesime, table in VAGUES.items():
        url = f"{BASE}{table}?{FILTRES}"
        try:
            demande = urllib.request.Request(url, headers=ENTETES)
            with urllib.request.urlopen(demande, timeout=120) as reponse:
                charge = json.load(reponse)
        except urllib.error.HTTPError as erreur:
            print(f"Erreur HTTP {erreur.code} sur {table} : {erreur.reason}",
                  file=sys.stderr)
            return 1
        except urllib.error.URLError as erreur:
            print(f"Réseau indisponible : {erreur.reason}", file=sys.stderr)
            return 1
        if "value" not in charge:
            print(f"{table} ne rend aucune donnée pour la France", file=sys.stderr)
            return 1
        vagues[millesime] = aplatir(charge)

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({"tables": VAGUES, "filtres": FILTRES, "vagues": vagues},
                   ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    total = sum(len(v) for v in vagues.values())
    print(f"{total} valeurs écrites dans {SORTIE} "
          f"({', '.join(sorted(vagues))})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
