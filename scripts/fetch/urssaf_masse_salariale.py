#!/usr/bin/env python3
"""Masse salariale du secteur privé, chez l'Urssaf qui la produit.

    python scripts/fetch/urssaf_masse_salariale.py

CE QU'ON VIENT CHERCHER, ET POURQUOI C'EST EXACTEMENT CETTE SÉRIE
------------------------------------------------------------------
La cotisation vieillesse DÉPLAFONNÉE de l'article L. 241-3 du code de la
sécurité sociale n'ouvre aucun droit : le salaire annuel de base est borné au
plafond (R. 351-29) et les trimestres à quatre par an (R. 351-9). Elle est
pourtant assise sur la TOTALITÉ de la rémunération, dès le premier euro — et
non, comme on le croit, sur la seule fraction au-dessus du plafond. Cet écart
vaut un facteur dix sur tout chiffrage.

Pour en faire une masse, il faut donc l'assiette déplafonnée elle-même, et non
la masse salariale des comptes nationaux. L'Urssaf la publie, et sa note
méthodologique la DÉFINIT ainsi, mot pour mot : « La masse salariale
correspond à l'assiette déplafonnée des cotisations sociales ». Champ :
secteur privé, régime général, France entière. Profondeur : depuis 1997. La
série est labellisée par l'Autorité de la statistique publique (avis du
14 avril 2020, JORF n° 0095 du 18 avril 2020).

C'est le producteur, au sens du premier critère de `data/sources.yaml` : ce
sont ses propres déclarations sociales qui forment l'assiette. Les comptes
nationaux de l'INSEE (`insee_bdm.py`, poste `salaires_bruts` de
`assiette_activite.csv`) portent une grandeur VOISINE et différente — toute
l'économie, fonction publique comprise, qui ne relève pas de L. 241-3. Les
deux séries ne sont pas interchangeables, et l'écart n'est pas petit : sur
2024, 726 Md€ ici contre environ 1 050 Md€ là.

DEUX ESTIMATIONS, ET L'ON PREND LA PLUS TARDIVE
------------------------------------------------
L'Urssaf publie chaque trimestre deux fois : une estimation précoce à
T+50 jours (Baromètre économique) et une estimation stabilisée à T+60 jours
(Stat'Ur). On retient la seconde partout où elle existe, la première
seulement pour le dernier trimestre publié — c'est le seul endroit où elle
apporte quelque chose, et elle y est signalée par la fiabilité `haute`.

ON NE GARDE QUE LES ANNÉES COMPLÈTES. Une année à trois trimestres n'est pas
une année basse : c'est une année fausse, et rien dans le fichier ne le
dirait. L'année en cours n'entre donc qu'une fois son quatrième trimestre
publié, avec environ deux mois de retard.

Le fichier produit, ``data/brut/urssaf_masse_salariale.json``, est le document
source : il n'est pas lu par le modèle, seulement par
``scripts/verifier_donnees.py``, qui en écrit
``data/reference/macro/masse_salariale_privee.csv``.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "brut" / "urssaf_masse_salariale.json"

#: L'API Opendatasoft de l'Urssaf. Le jeu porte un trimestre par ligne.
JEU = "masse-salariale-du-secteur-prive-france-entiere"
RACINE_API = "https://open.urssaf.fr/api/explore/v2.1/catalog/datasets"

#: L'API plafonne une réponse à cent lignes ; le jeu en porte davantage et
#: s'allonge d'une par trimestre. On pagine plutôt que de supposer une borne.
PAR_PAGE = 100


def _lire(url: str, delai: int = 90) -> dict:
    requete = urllib.request.Request(url, headers={"User-Agent": "retraite-notionnelle"})
    with urllib.request.urlopen(requete, timeout=delai) as reponse:
        return json.loads(reponse.read().decode("utf-8"))


def telecharger(sortie: Path = SORTIE, lire=_lire) -> Path:
    """Récupère tous les trimestres publiés et les écrit tels quels."""
    champs = "annee,trimestre,ms_t_50j_brut,ms_t_60j_brut"
    lignes: list[dict] = []
    decalage, total = 0, None
    while total is None or decalage < total:
        charge = lire(f"{RACINE_API}/{JEU}/records?limit={PAR_PAGE}"
                      f"&offset={decalage}&order_by=annee,trimestre&select={champs}")
        total = charge.get("total_count", 0)
        page = charge.get("results", [])
        if not page:
            break
        lignes.extend(page)
        decalage += len(page)
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(json.dumps({"jeu": JEU, "trimestres": lignes},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    return sortie


def annuel(trimestres: list[dict]) -> dict[int, tuple[float, bool]]:
    """Somme des quatre trimestres, en millions d'euros, par année COMPLÈTE.

    Rend pour chaque année le montant et un drapeau disant si l'une au moins
    de ses valeurs est une estimation précoce — auquel cas la fiabilité de
    l'année entière retombe à `haute`.
    """
    par_annee: dict[int, dict[int, tuple[float, bool]]] = {}
    for ligne in trimestres:
        stabilisee = ligne.get("ms_t_60j_brut")
        precoce = ligne.get("ms_t_50j_brut")
        valeur = stabilisee if stabilisee is not None else precoce
        if valeur is None:
            continue
        par_annee.setdefault(int(ligne["annee"]), {})[int(ligne["trimestre"])] = (
            float(valeur), stabilisee is None)
    return {
        annee: (sum(v for v, _ in q.values()) / 1e6, any(p for _, p in q.values()))
        for annee, q in par_annee.items()
        if set(q) == {1, 2, 3, 4}
    }


def main() -> int:
    try:
        chemin = telecharger()
    except urllib.error.HTTPError as erreur:
        print(f"Erreur HTTP {erreur.code} : {erreur.reason}", file=sys.stderr)
        return 1
    except urllib.error.URLError as erreur:
        print(f"Réseau indisponible : {erreur.reason}", file=sys.stderr)
        return 1

    charge = json.loads(chemin.read_text(encoding="utf-8"))
    annees = annuel(charge["trimestres"])
    if not annees:
        print("aucune année complète : le jeu a changé de forme", file=sys.stderr)
        return 1
    bornes = (min(annees), max(annees))
    print(f"{len(charge['trimestres'])} trimestres écrits dans {chemin} — "
          f"{len(annees)} années complètes ({bornes[0]}-{bornes[1]}), "
          f"{annees[bornes[1]][0] / 1000:.1f} Md€ en {bornes[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
