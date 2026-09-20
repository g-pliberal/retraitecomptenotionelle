#!/usr/bin/env python3
"""Droits à pension acquis à date, France — tableau supplémentaire du SEC 2010.

    python scripts/fetch/eurostat_engagements_retraite.py

CE QUE CETTE GRANDEUR EST, ET POURQUOI ELLE MANQUAIT
-----------------------------------------------------
Tout ce que le dépôt montre du système de retraite est un FLUX : ce qui rentre
et ce qui sort dans l'année, rapporté au PIB de l'année. C'est la moitié d'un
compte. L'autre moitié est un STOCK — ce que le système doit déjà, au titre des
droits que les vivants ont acquis à ce jour —, et il n'était nulle part dans le
dépôt alors que le modèle est en COMPTES NOTIONNELS, où ce stock est la somme
des capitaux virtuels et se lit sans calcul.

Le règlement (UE) n° 549/2013 le fait publier : son tableau supplémentaire sur
les retraites, dit « tableau 29 », que chaque État membre transmet TOUS LES
TROIS ANS. Le poste ``F63_LE`` en est la ligne centrale — « droits à pension
dans le bilan de clôture », c'est-à-dire les droits acquis à date par les
ménages, tous régimes confondus, actualisés. Pour la France : 368 % du PIB en
2015, 431 % en 2018, 397 % en 2021.

CE QUE CES TROIS NOMBRES DISENT, ET CE QU'ILS NE DISENT PAS
-------------------------------------------------------------
Ils disent l'ordre de grandeur, qui est le seul point qu'on puisse en tirer
sans précaution : **près de quatre années de production**, contre quatorze
pour-cent de PIB de dépense annuelle. Un système de retraite porte un
engagement de l'ordre de trente fois son flux annuel.

Ils ne disent PAS que l'engagement a bondi de soixante-trois points de PIB
entre 2015 et 2018 puis reculé de trente-quatre entre 2018 et 2021. Un droit
acquis à date est une somme ACTUALISÉE : son niveau dépend d'un taux
d'actualisation et d'hypothèses de revalorisation qui bougent d'une
transmission à l'autre, bien davantage que les droits eux-mêmes. C'est la
faiblesse connue de l'exercice, et la raison pour laquelle le tableau 29 est
publié à part des comptes principaux : personne ne le porte au bilan des
administrations publiques. Le dépôt le montre pour ce qu'il est — un ordre de
grandeur, et la démonstration que le niveau d'un tel engagement dépend d'une
convention — et non comme une dette.

CE QUE LE DÉPÔT NE CALCULE PAS, ET QU'IL FAUDRAIT POUR COMPARER
-----------------------------------------------------------------
Le sien. Un scénario notionnel du dépôt produit nativement la moitié de cette
grandeur : le capital virtuel des ACTIFS en est la définition même. L'autre
moitié est celle des retraités — la valeur actualisée des pensions qu'ils
toucheront encore —, qu'un compte notionnel ne porte plus, le capital ayant
été converti en rente à la liquidation. Les additionner demanderait de refaire
ce que le tableau 29 fait, table de mortalité et taux d'actualisation compris,
et le résultat dépendrait de ce taux autant que le fait celui d'Eurostat.

C'est une action ouverte, pas un oubli, et la feuille de route la porte.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

#: ``F63_LE`` : droits à pension dans le bilan de CLÔTURE, en pour-cent du PIB.
#: Le bilan d'ouverture (``F63_LS``) est celui de l'année précédente et
#: n'apporte rien ; les postes de variation (``D61_P``, ``D62_P``, ``D8``…)
#: sont des flux, que le dépôt lit déjà chez la DREES et le COR.
URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
    "nasa_10_pens1?format=JSON&geo=FR&unit=PC_GDP&na_item=F63_LE&lang=fr"
)
SORTIE = Path("data/brut/eurostat_engagements_retraite.json")

#: Les régimes retenus, du code d'Eurostat au code du dépôt. ``S1P`` est le
#: total, ``S13PU`` la part par répartition — la seule que le modèle simule.
#: Les autres postes de la dimension ventilent le privé et les administrations
#: publiques, et la France y déclare zéro ou rien.
REGIMES: tuple[tuple[str, str], ...] = (
    ("S1P", "tous_regimes"),
    ("S13PU", "repartition"),
)


def extraire(charge: dict) -> dict[tuple[int, str], float]:
    """Aplatit la structure JSON-stat en (année, régime) -> part de PIB.

    Eurostat range ses valeurs sous un index PLAT, qu'il faut décoder par les
    tailles de chaque dimension, de la dernière à la première. ``value`` est
    creux : les années sans transmission n'y figurent pas, et c'est ainsi que
    la périodicité triennale se lit.
    """
    dimensions, tailles = charge["id"], charge["size"]
    index = {
        nom: {int(position): code
              for code, position in charge["dimension"][nom]["category"]["index"].items()}
        for nom in dimensions
    }
    codes = dict(REGIMES)
    resultat: dict[tuple[int, str], float] = {}
    for position, valeur in charge["value"].items():
        reste, coordonnees = int(position), {}
        for nom, taille in reversed(list(zip(dimensions, tailles))):
            reste, rang = divmod(reste, taille)
            coordonnees[nom] = index[nom][rang]
        regime = codes.get(coordonnees["penscheme"])
        if regime is None or valeur is None:
            continue
        resultat[(int(coordonnees["time"]), regime)] = valeur / 100.0
    return dict(sorted(resultat.items()))


def main() -> int:
    try:
        demande = urllib.request.Request(
            URL, headers={"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
        )
        with urllib.request.urlopen(demande, timeout=120) as reponse:
            charge = json.loads(reponse.read())
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"Eurostat indisponible : {erreur}", file=sys.stderr)
        return 1

    serie = extraire(charge)
    if not serie:
        print("Aucun droit à pension lu : la dimension a changé", file=sys.stderr)
        return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(
            {
                "source": URL,
                "publication": charge.get("updated"),
                "serie": {f"{annee}|{regime}": part
                          for (annee, regime), part in serie.items()},
            },
            ensure_ascii=False, indent=1,
        ),
        encoding="utf-8",
    )
    annees = sorted({annee for annee, _ in serie})
    print(f"{len(serie)} valeurs écrites dans {SORTIE}")
    print(f"Transmissions : {', '.join(str(a) for a in annees)}")
    for annee in annees:
        part = serie.get((annee, "tous_regimes"))
        if part is not None:
            print(f"  {annee} : {part:.0%} du PIB, tous régimes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
