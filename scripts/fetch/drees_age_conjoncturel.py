#!/usr/bin/env python3
"""L'âge conjoncturel de départ à la retraite, publié par la DREES.

    python scripts/fetch/drees_age_conjoncturel.py

POURQUOI CETTE SOURCE
---------------------
``docs/limites.md`` § 5 ter écrit, à propos de la grille de cas types : « les
âges d'entrée des cas types restent ceux de la grille — vingt-quatre ans pour
l'artisan, vingt-sept pour le libéral —, ce qui suffit à les faire partir à
soixante-sept ans une fois la durée requise opposée. La grille part donc, en
moyenne, un peu plus tard que la France réelle ; l'âge conjoncturel de départ
que publie la DREES permettrait de le chiffrer, et il n'est pas dans le
dépôt. »

Il y est. C'est la série que ce récupérateur dépose, et
``scripts/age_conjoncturel.py`` est la mesure qu'elle permet.

CE QU'EST UN ÂGE CONJONCTUREL, ET CE QU'IL N'EST PAS
-----------------------------------------------------
Ce n'est PAS l'âge moyen des personnes qui ont liquidé dans l'année : celui-là
suit la taille des générations qui se présentent, et monte d'une année sur
l'autre pour la seule raison qu'une classe creuse arrive à l'âge de partir.
C'est un indicateur SYNTHÉTIQUE, construit comme un indice conjoncturel de
fécondité : on applique à une génération fictive les taux de liquidation par
âge observés dans l'année, et l'on en tire l'âge moyen de départ de cette
génération-là. Il ne dépend donc que des comportements et des règles de
l'année, non de la pyramide des âges — c'est précisément ce qui le rend
comparable à l'âge de départ d'une grille de cas types, qui n'a pas de
pyramide non plus.

La DREES le publie par sexe depuis 2004, dans le panorama « Les retraités et
les retraites », et en open data sur le portail que ``drees_eacr.py`` et
``drees_caracteristiques_retraites.py`` interrogent déjà.

LE JEU EST RETROUVÉ PAR SON TITRE, NON PAR SON IDENTIFIANT
------------------------------------------------------------
L'identifiant du jeu porte la trace de son origine — une FIGURE du panorama,
« Retraite_Graphique-1-… », tronquée à soixante-dix caractères par le portail.
Une édition qui renumérote ses graphiques change donc l'identifiant sans que
la série change. Le récupérateur cherche par le TITRE, qui nomme la grandeur,
et vérifie que le jeu trouvé porte bien les quatre colonnes attendues.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = (
    "https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog"
)
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/drees_age_conjoncturel.json")

#: Ce qu'on cherche dans le titre des jeux du portail. Un seul mot suffit :
#: « conjoncturel » ne qualifie qu'une grandeur dans tout le catalogue retraite.
MOT_DU_TITRE = "conjoncturel"

#: Les colonnes attendues, sous le code que le dépôt leur donne. Elles servent
#: à RECONNAÎTRE le jeu autant qu'à le lire : un jeu qui ne les porte pas
#: toutes n'est pas celui-là, quel que soit son titre.
COLONNES: dict[str, str] = {"femmes": "F", "hommes": "H", "ensemble": "ensemble"}

#: Bornes de vraisemblance. L'âge conjoncturel français tient dans cette
#: fourchette depuis que la DREES le publie ; en sortir signale une colonne
#: lue de travers, non une réforme.
AGE_MINIMAL, AGE_MAXIMAL = 55.0, 70.0


def _lire(url: str, parametres: dict[str, str]) -> dict:
    demande = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(parametres)}", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=180) as reponse:
        return json.loads(reponse.read())


def jeu_de_l_age_conjoncturel() -> tuple[str, str]:
    """Identifiant et titre du jeu, cherchés par le titre.

    Rend le premier jeu dont le titre porte le mot cherché ET qui expose les
    quatre colonnes attendues. Sans cette seconde condition, une édition
    publiant la même figure sous une autre forme — l'âge par génération, par
    exemple — serait lue comme si elle était celle-ci.
    """
    charge = _lire(f"{BASE}/datasets", {
        "where": f'search(title,"{MOT_DU_TITRE}")',
        "limit": "20",
    })
    for jeu in charge.get("results", []):
        champs = {champ["name"] for champ in jeu.get("fields", [])}
        if "annee" in champs and set(COLONNES) <= champs:
            titre = (jeu.get("metas") or {}).get("default", {}).get("title", "")
            return jeu["dataset_id"], titre
    raise RuntimeError(
        f"aucun jeu « {MOT_DU_TITRE} » portant les colonnes "
        f"{', '.join(sorted(COLONNES))} sur le portail de la DREES"
    )


def lire_serie(identifiant: str) -> dict[str, dict[str, float]]:
    """L'âge conjoncturel par année et par sexe.

    Le portail sert au plus cent enregistrements par appel ; la série en compte
    une vingtaine, et l'on refuse de lire une page tronquée plutôt que de
    publier une série amputée sans le dire.
    """
    charge = _lire(f"{BASE}/datasets/{identifiant}/records",
                   {"limit": "100", "order_by": "annee"})
    total = int(charge.get("total_count", 0))
    resultats = charge.get("results", [])
    if total > len(resultats):
        raise RuntimeError(
            f"série tronquée : {len(resultats)} lignes servies sur {total}")

    valeurs: dict[str, dict[str, float]] = {}
    for ligne in resultats:
        annee = str(ligne.get("annee") or "").strip()
        if not annee.isdigit():
            continue
        for colonne, sexe in COLONNES.items():
            age = ligne.get(colonne)
            if not isinstance(age, (int, float)):
                continue
            if not AGE_MINIMAL <= float(age) <= AGE_MAXIMAL:
                raise RuntimeError(
                    f"{annee} {colonne} : âge invraisemblable ({age})")
            valeurs.setdefault(annee, {})[sexe] = float(age)

    incomplets = [annee for annee, serie in valeurs.items()
                  if len(serie) < len(COLONNES)]
    if incomplets:
        raise RuntimeError(f"années incomplètes : {', '.join(sorted(incomplets))}")
    if not valeurs:
        raise RuntimeError("aucune année lue dans le jeu")
    return dict(sorted(valeurs.items()))


def main() -> int:
    try:
        identifiant, titre = jeu_de_l_age_conjoncturel()
        valeurs = lire_serie(identifiant)
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1

    charge = {
        "source": f"{BASE}/datasets/{identifiant}",
        "jeu": identifiant,
        "titre": titre,
        "mesure": "âge conjoncturel moyen de départ à la retraite, par sexe",
        "unite": "années",
        "valeurs": valeurs,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    annees = sorted(valeurs)
    print(f"{len(annees)} années écrites dans {SORTIE} "
          f"({annees[0]}-{annees[-1]}, jeu {identifiant})")
    for annee in (annees[0], annees[-1]):
        serie = valeurs[annee]
        print(f"  {annee} : ensemble {serie['ensemble']:.2f} ans, "
              f"femmes {serie['F']:.2f}, hommes {serie['H']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
