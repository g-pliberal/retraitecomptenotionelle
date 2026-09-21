#!/usr/bin/env python3
"""L'âge de départ à la retraite par catégorie socioprofessionnelle, par la DREES.

    python scripts/fetch/drees_age_depart_csp.py

POURQUOI CETTE SOURCE
---------------------
``drees_age_conjoncturel.py`` a déposé l'âge conjoncturel TOUS RÉGIMES, et
``scripts/age_conjoncturel.py`` a montré que la grille de cas types le suivait
à moins d'une demi-année sur dix-neuf ans. Cette concordance-là ne juge que la
SOMME : treize cas types dont l'un partirait deux ans trop tard et l'autre deux
ans trop tôt la donneraient aussi bien.

Ce jeu-ci est le grain en dessous. La DREES publie le même indicateur —
l'âge conjoncturel — ventilé par catégorie socioprofessionnelle, de 2013 à
2020, et la plupart des cas types du dépôt ont une catégorie : l'artisan est
un artisan, le cadre un cadre, le chef d'exploitation un agriculteur
exploitant. C'est la confrontation qui dit LEQUEL des treize part de travers.

CE QUE CE JEU N'EST PAS
-----------------------
Ce n'est pas la même source que le précédent, et il ne faut pas les additionner
à la légère :

* le tous régimes vient des fichiers des caisses (EACR, modèle ANCETRE) : un
  DÉNOMBREMENT ;
* celui-ci vient de l'enquête Emploi de l'INSEE, traitée par la DREES : un
  SONDAGE. La DREES l'écrit elle-même — « s'agissant d'une enquête sur un
  échantillon, certains indicateurs peuvent être bruités et il est préférable
  de les regarder en moyenne sur plusieurs années ». C'est pourquoi la
  comparaison se fait sur la MOYENNE 2013-2020 et non année par année.

Les deux se rejoignent néanmoins là où ils se recouvrent : 61,3 contre 61,23 en
2013, 62,4 contre 62,42 en 2020 pour la ligne « toutes CSP confondues ». Ce
recoupement est gardé comme contrôle dans ``tests/test_age_depart_csp.py``.

CE QU'ON RETIENT, ET CE QU'ON LAISSE
-------------------------------------
Du jeu, on ne garde que l'âge conjoncturel. Il porte quatre indicateurs de
plus — la durée moyenne passée en emploi et hors emploi entre cinquante ans et
le départ, la proportion de retraités à soixante et un ans, la part de
personnes limitées dans leurs activités la première année de retraite. Ils
diraient ce que « partir plus tard » coûte, ce qu'aucune page du site ne
demande aujourd'hui ; le dépôt lit ce dont il se sert.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = (
    "https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog"
)
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/drees_age_depart_csp.json")

#: Ce qu'on cherche dans le titre des jeux du portail. Comme pour l'âge
#: conjoncturel tous régimes, le jeu est retrouvé par son TITRE : son
#: identifiant est une abréviation que rien n'oblige à durer.
MOT_DU_TITRE = "socioprofessionnelle"

#: La colonne retenue, et les deux qui identifient la ligne.
COLONNE_AGE = "age_conjoncturel_de_depart_a_la_retraite"
COLONNE_CSP = "categorie_socioprofessionnelle"
COLONNE_ANNEE = "annee"

#: Le libellé des catégories commence par leur numéro de groupe dans la
#: nomenclature des professions et catégories socioprofessionnelles de
#: l'INSEE — « 1 - Agriculteurs exploitants ». C'est ce NUMÉRO qui sert de
#: clé : le libellé se réécrit d'une édition à l'autre, le groupe non.
#: Le groupe 9 n'existe pas dans la nomenclature ; la DREES s'en sert ici pour
#: la ligne « toutes CSP confondues », et le dépôt le garde tel quel.
_GROUPE = re.compile(r"^\s*(\d)\s*-\s*(.+?)\s*$")

#: Bornes de vraisemblance, les mêmes que pour le tous régimes.
AGE_MINIMAL, AGE_MAXIMAL = 55.0, 70.0


def _lire(url: str, parametres: dict[str, str]) -> dict:
    demande = urllib.request.Request(
        f"{url}?{urllib.parse.urlencode(parametres)}", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=180) as reponse:
        return json.loads(reponse.read())


def jeu_de_l_age_par_csp() -> tuple[str, str]:
    """Identifiant et titre du jeu, cherchés par le titre puis par ses colonnes."""
    charge = _lire(f"{BASE}/datasets", {
        "where": f'search(title,"{MOT_DU_TITRE}")',
        "limit": "20",
    })
    for jeu in charge.get("results", []):
        champs = {champ["name"] for champ in jeu.get("fields", [])}
        if {COLONNE_ANNEE, COLONNE_CSP, COLONNE_AGE} <= champs:
            titre = (jeu.get("metas") or {}).get("default", {}).get("title", "")
            return jeu["dataset_id"], titre
    raise RuntimeError(
        f"aucun jeu « {MOT_DU_TITRE} » portant la colonne {COLONNE_AGE!r} "
        f"sur le portail de la DREES"
    )


def lire_serie(identifiant: str) -> tuple[dict[str, str], dict[str, dict[str, float]]]:
    """Les libellés des groupes, et l'âge conjoncturel par groupe et par année."""
    charge = _lire(f"{BASE}/datasets/{identifiant}/records",
                   {"limit": "100", "order_by": COLONNE_ANNEE})
    total = int(charge.get("total_count", 0))
    resultats = charge.get("results", [])
    if total > len(resultats):
        raise RuntimeError(
            f"série tronquée : {len(resultats)} lignes servies sur {total}")

    libelles: dict[str, str] = {}
    valeurs: dict[str, dict[str, float]] = {}
    for ligne in resultats:
        annee = str(ligne.get(COLONNE_ANNEE) or "").strip()[:4]
        trouve = _GROUPE.match(str(ligne.get(COLONNE_CSP) or ""))
        age = ligne.get(COLONNE_AGE)
        if not annee.isdigit() or trouve is None:
            continue
        if not isinstance(age, (int, float)):
            continue
        if not AGE_MINIMAL <= float(age) <= AGE_MAXIMAL:
            raise RuntimeError(f"{annee} {trouve.group(0)} : âge invraisemblable ({age})")
        groupe, libelle = trouve.group(1), trouve.group(2)
        libelles[groupe] = libelle
        valeurs.setdefault(groupe, {})[annee] = float(age)

    if not valeurs:
        raise RuntimeError("aucune catégorie lue dans le jeu")
    annees = {annee for serie in valeurs.values() for annee in serie}
    incomplets = [groupe for groupe, serie in valeurs.items()
                  if set(serie) != annees]
    if incomplets:
        raise RuntimeError(
            f"catégories aux années incomplètes : {', '.join(sorted(incomplets))}")
    return (dict(sorted(libelles.items())),
            {groupe: dict(sorted(serie.items()))
             for groupe, serie in sorted(valeurs.items())})


def main() -> int:
    try:
        identifiant, titre = jeu_de_l_age_par_csp()
        libelles, valeurs = lire_serie(identifiant)
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1

    charge = {
        "source": f"{BASE}/datasets/{identifiant}",
        "jeu": identifiant,
        "titre": titre,
        "mesure": "âge conjoncturel de départ à la retraite, par catégorie "
                  "socioprofessionnelle",
        "unite": "années",
        "enquete": "INSEE, enquête Emploi ; traitements DREES",
        "categories": libelles,
        "valeurs": valeurs,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    annees = sorted({annee for serie in valeurs.values() for annee in serie})
    print(f"{len(valeurs)} catégories × {len(annees)} années écrites dans "
          f"{SORTIE} ({annees[0]}-{annees[-1]}, jeu {identifiant})")
    for groupe, serie in valeurs.items():
        moyenne = sum(serie.values()) / len(serie)
        print(f"  {groupe} {libelles[groupe]:48} moyenne {moyenne:.2f} ans "
              f"({serie[annees[0]]:.1f} → {serie[annees[-1]]:.1f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
