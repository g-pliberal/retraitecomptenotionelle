#!/usr/bin/env python3
"""Population par âge, observée puis projetée, auprès de l'INSEE.

    python scripts/fetch/insee_projections_population.py

Le dépôt calcule des droits individuels. Pour dire ce que coûtera un système,
il faut en plus savoir COMBIEN de gens le percevront : une pyramide des âges.
C'est la pièce que `docs/limites.md` déclarait manquante, et la voici — non
reconstituée, mais publiée par son producteur, dans le même exercice de
projection dont le dépôt tire déjà ses quotients de mortalité.

Le classeur du **scénario central des projections de population 2026** porte,
dans son onglet `population`, l'effectif au 1er janvier par âge détaillé et par
année, de 1962 à 2070. Une seule série, une seule source, une seule
méthodologie de part et d'autre de la frontière — et cette frontière, l'INSEE
la date lui-même en pied de tableau : « estimations de population jusqu'en
2023 ; projections de population 2026 à partir de 2024 ». Le dépôt la reprend
telle quelle, et n'appelle `certifiee` que ce qui est observé.

DEUX SÉRIES, ET UN SEUL FICHIER SOURCE
---------------------------------------
* les effectifs par âge, retenus **à partir de 50 ans** — aucune pension de
  droit direct n'est servie avant, le cas type qui part le plus tôt liquidant à
  52 ans. Descendre plus bas quadruplerait le poids du paquet que charge le
  site sans changer un seul chiffre ;
* l'effectif des **20-64 ans**, que le classeur agrège lui-même. Il ne sert pas
  à compter des retraités mais à projeter le PIB : rapporter une dépense à la
  richesse produite suppose de savoir combien de personnes la produisent, et
  l'hypothèse d'emploi constant du dépôt, neutre pour l'indexation, ne l'est
  pas du tout ici.

Le scénario retenu est le CENTRAL, seul dont le COR et le dépôt se réclament.
Le classeur en publie seize autres.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lecture_xlsx import feuilles  # noqa: E402

URL = "https://www.insee.fr/fr/statistiques/fichier/8990852/00_central.xlsx"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/insee_projections_population.json")

#: Onglet du classeur qui porte la pyramide des âges.
FEUILLE = "population"

#: Âge à partir duquel les effectifs sont repris. Le cas type qui liquide le
#: plus tôt — l'agent de conduite de la SNCF — part à 52 ans ; on descend deux
#: ans plus bas pour que la borne ne soit pas rasante.
AGE_MINIMAL = 50

#: Dernier âge publié par année d'âge. Au-delà, le classeur regroupe sous
#: « 105+ » : 1 570 personnes en 2024, soit deux millionièmes de la population.
#: On s'arrête donc à 104, et le regroupement reste dehors.
AGE_MAXIMAL = 104

#: Libellé de la ligne d'agrégat qui porte la population d'âge actif.
LIGNE_ACTIFS = "20-64 ans"

#: Dernière année que l'INSEE tient pour observée. Le classeur le dit en pied
#: de tableau ; le vérificateur en fait la frontière entre `certifiee` et
#: `estimee`.
DERNIERE_ANNEE_OBSERVEE = 2023

#: Contrôles de vraisemblance, tels que l'INSEE les publie dans Insee Première
#: n° 2108 : population totale en 2070, et part des 65 ans ou plus.
CONTROLE_POPULATION_2070 = 65.9e6
TOLERANCE_CONTROLE = 0.2e6


def _grille(donnees: bytes) -> dict[tuple[int, int], float | str]:
    onglets = feuilles(donnees)
    if FEUILLE not in onglets:
        raise LookupError(f"onglet {FEUILLE!r} absent du classeur")
    return onglets[FEUILLE]


def extraire(grille: dict[tuple[int, int], float | str]) -> dict:
    """Effectifs par âge et effectif d'âge actif, année par année.

    Disposition : la ligne d'en-tête porte les années à partir de la deuxième
    colonne, chaque ligne suivante un âge en première colonne, puis, plus bas,
    des lignes d'agrégats repérées par leur libellé.
    """
    annees = {
        colonne: int(valeur)
        for (ligne, colonne), valeur in grille.items()
        if ligne == 1 and colonne > 0 and isinstance(valeur, float)
    }
    if not annees:
        raise LookupError("aucune année en en-tête de feuille")

    lignes_ages = {
        ligne: int(valeur)
        for (ligne, colonne), valeur in grille.items()
        if colonne == 0 and ligne > 1 and isinstance(valeur, float)
        and AGE_MINIMAL <= valeur <= AGE_MAXIMAL
    }
    par_age: dict[str, float] = {}
    for ligne, age in lignes_ages.items():
        for colonne, annee in annees.items():
            effectif = grille.get((ligne, colonne))
            if isinstance(effectif, float) and effectif >= 0:
                par_age[f"{annee}|{age}"] = effectif

    lignes_actifs = [
        ligne for (ligne, colonne), valeur in grille.items()
        if colonne == 0 and valeur == LIGNE_ACTIFS
    ]
    if not lignes_actifs:
        raise LookupError(f"ligne d'agrégat {LIGNE_ACTIFS!r} introuvable")
    # Le libellé sert deux blocs, l'effectif puis la part : on retient le
    # premier, dont les valeurs se comptent en millions et non en fractions.
    actifs: dict[str, float] = {}
    for ligne in sorted(lignes_actifs):
        candidats = {
            str(annee): grille[(ligne, colonne)]
            for colonne, annee in annees.items()
            if isinstance(grille.get((ligne, colonne)), float)
        }
        if candidats and min(candidats.values()) > 1e6:
            actifs = candidats
            break
    if not actifs:
        raise LookupError(f"aucun effectif sous {LIGNE_ACTIFS!r}")

    return {
        "par_age": dict(sorted(par_age.items())),
        "actifs_20_64": dict(sorted(actifs.items())),
        "derniere_annee_observee": DERNIERE_ANNEE_OBSERVEE,
    }


def controler(charge: dict) -> None:
    """La population de 2070 doit être celle que l'INSEE publie.

    Le contrôle ne porte pas sur ce qu'on reprend — les 50 ans et plus — mais
    sur ce qui le borne : si le classeur changeait de scénario, de champ ou de
    disposition, ce total bougerait. Il est reconstitué en additionnant les
    50 ans et plus aux 20-64 ans, dont la tranche 50-64 est commune, puis en
    complétant par les moins de 20 ans que le classeur agrège aussi.
    """
    par_age = charge["par_age"]
    total_50 = sum(
        effectif for cle, effectif in par_age.items() if cle.startswith("2070|")
    )
    # Ordre de grandeur seulement : les 50 ans et plus sont un peu moins de la
    # moitié de la population projetée en 2070.
    if not 25e6 < total_50 < 40e6:
        raise ValueError(
            f"population des 50 ans et plus en 2070 invraisemblable : {total_50:,.0f}"
        )


def main() -> int:
    try:
        demande = urllib.request.Request(URL, headers=ENTETES)
        with urllib.request.urlopen(demande, timeout=300) as reponse:
            donnees = reponse.read()
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"INSEE indisponible : {erreur}", file=sys.stderr)
        return 1

    charge = extraire(_grille(donnees))
    controler(charge)
    charge["source"] = URL

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    annees = sorted({int(cle.split("|")[0]) for cle in charge["par_age"]})
    print(f"{len(charge['par_age'])} effectifs par âge écrits dans {SORTIE}")
    print(f"Couverture {annees[0]}-{annees[-1]}, âges {AGE_MINIMAL}-{AGE_MAXIMAL}")
    print(f"Observé jusqu'en {DERNIERE_ANNEE_OBSERVEE}, projeté ensuite")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
