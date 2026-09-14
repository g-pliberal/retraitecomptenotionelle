#!/usr/bin/env python3
"""Tables par génération d'OpenFisca-France-Pension : durée requise, âge d'annulation.

    python scripts/fetch/openfisca_parametres_generation.py

À quoi il sert. Trois tables du dépôt gardent des lignes que la base LEGI ne
certifie pas, parce qu'aucun texte en vigueur ne les écrit telles quelles :

* la durée requise des générations 1943 à 1952 — 160 trimestres « vient de la
  règle générale, non d'un alinéa qui les nomme », et les 161 à 164 sont dans
  des décrets absents de la base ;
* l'âge d'annulation de la décote, qui n'est écrit nulle part génération par
  génération : le code donne une RÈGLE, l'âge d'ouverture majoré de cinq ans ;
* la durée de services de la fonction publique pour les droits ouverts de 2004
  à 2008, montée en charge de la loi du 21 août 2003 mise en table à la main.

OpenFisca-France-Pension porte ces trois tables, transcrites des mêmes textes
par d'autres mains. Ce récupérateur les lit dans son dépôt et les met à plat,
génération par génération ; ``verifier_donnees.py`` les confronte aux lignes
NON CERTIFIÉES du dépôt et les verse au niveau ``haute`` — jamais ``certifiee``,
OpenFisca n'étant pas le producteur —, sans toucher à ce que la base LEGI a
déjà certifié.

Deux choses à savoir sur ces fichiers.

* Ils sont organisés en blocs ``before_1951_07_01`` / ``after_1952_01_01``,
  chacun portant une suite de valeurs datées : la génération est la clé du
  bloc, la date d'effet celle de la valeur. On garde la dernière valeur en
  vigueur — pour la génération 1965, les 172 trimestres du 1er septembre 2023,
  non les 169 de 2015.
* La table de la fonction publique porte, pour les générations 1944 à 1948, une
  seconde valeur datée de 2014 — 151 à 155 trimestres — qui contredit la
  colonne de 2003 et le texte lui-même. C'est la valeur de 2003 qu'on lit, et
  le vérificateur le sait.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = ("https://raw.githubusercontent.com/openfisca/openfisca-france-pension/"
          "master/openfisca_france_pension/parameters/retraites")

#: Série -> (fichier, chemin de clés jusqu'aux blocs par génération,
#:           date à retenir : ``None`` pour la dernière en vigueur, ou une
#:           date d'effet précise).
TABLES = {
    "duree_requise": (
        "secteur_prive/regime_general_cnav/trimtp.yaml",
        ("nombre_trimestres_cibles_par_generation",), None),
    "age_annulation_decote": (
        "secteur_prive/regime_general_cnav/aad.yaml",
        ("age_annulation_decote_en_fonction_date_naissance",), None),
    "duree_requise_fonction_publique": (
        "secteur_public/pension_civile/trimtp.yaml",
        ("nombre_trimestres_cibles_taux_plein_par_generation",), "2003-01-01"),
}

SORTIE = Path("data/brut/openfisca_parametres_generation.json")


def _lire(url: str) -> str:
    demande = urllib.request.Request(
        url, headers={"User-Agent": "retraite-notionnelle/0.1"}
    )
    with urllib.request.urlopen(demande, timeout=120) as reponse:
        return reponse.read().decode("utf-8")


def generation_du_bloc(nom: str) -> float:
    """``after_1951_07_01`` -> 1951.5 ; ``before_1944_01_01`` -> 0.

    Un bloc ``before`` couvre tout ce qui précède la première génération
    nommée : on le range à zéro, et la lecture en escalier fait le reste.
    """
    sens, annee, mois, _jour = nom.split("_")
    if sens == "before":
        return 0.0
    return int(annee) + (int(mois) - 1) / 12


def cle_generation(generation: float) -> str:
    """1951.5 -> ``1951.5``, 1961.6667 -> ``1961.667``, 1934.0 -> ``1934``.

    C'est l'écriture des tables du dépôt, à trois décimales au plus, et c'est
    par elle que le vérificateur apparie les lignes.
    """
    return f"{generation:.3f}".rstrip("0").rstrip(".")


def _valeur(bloc: dict, date_retenue: str | None) -> float | None:
    """La valeur d'un bloc : la dernière en vigueur, ou celle d'une date."""
    valeurs = bloc.get("values")
    if valeurs is None:
        # Bloc à deux composantes — ``annee`` et ``mois`` de l'âge d'annulation.
        annee = _valeur(bloc["annee"], date_retenue)
        mois = _valeur(bloc["mois"], date_retenue)
        if annee is None:
            return None
        return annee + (mois or 0.0) / 12
    datees = {
        str(d): (v or {}).get("value")
        for d, v in valeurs.items()
        if (v or {}).get("value") is not None
    }
    if not datees:
        return None
    if date_retenue is not None:
        return float(datees[date_retenue]) if date_retenue in datees else None
    return float(datees[max(datees)])


def lire_table(texte: str, chemin: tuple[str, ...], date_retenue: str | None
               ) -> dict[float, float]:
    import yaml

    noeud = yaml.safe_load(texte)
    for cle in chemin:
        noeud = noeud[cle]
    table: dict[float, float] = {}
    for nom, bloc in noeud.items():
        if not isinstance(bloc, dict) or not (nom.startswith("before_") or nom.startswith("after_")):
            continue
        valeur = _valeur(bloc, date_retenue)
        if valeur is not None:
            table[generation_du_bloc(nom)] = valeur
    return dict(sorted(table.items()))


def main() -> int:
    series: dict[str, dict[float, float]] = {}
    try:
        for serie, (fichier, chemin, date_retenue) in TABLES.items():
            series[serie] = lire_table(_lire(f"{RACINE}/{fichier}"), chemin, date_retenue)
            print(f"OK      {serie:<34} {len(series[serie])} blocs")
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"OpenFisca indisponible : {erreur}", file=sys.stderr)
        return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": RACINE,
            "recupere_le": date.today().isoformat(),
            "lecture": "clé = génération (année plus part écoulée avant le mois "
                       "de la coupure), 0 pour le bloc `before` ; lecture en "
                       "escalier ; valeur = dernière en vigueur, sauf pour la "
                       "fonction publique, lue à la date de la loi de 2003",
            "series": {
                serie: {cle_generation(generation): valeur
                        for generation, valeur in table.items()}
                for serie, table in series.items()
            },
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"écrit dans {SORTIE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
