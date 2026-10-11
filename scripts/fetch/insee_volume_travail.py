#!/usr/bin/env python3
"""Récupération du volume de travail salarié auprès de l'INSEE : sa moyenne par
sexe et par âge, et la distribution des heures de l'année.

    python scripts/fetch/insee_volume_travail.py

CE QU'ON VIENT CHERCHER, ET POURQUOI
-------------------------------------
Combien d'une année un salarié travaille. Les centiles du salaire
(``insee_profil_salaire_age.py``) sont ceux des temps complets, en équivalent
temps plein : le prix d'une année entière. La pension compte le salaire de
l'année, et une année se travaille rarement entière : les entrées et les
sorties, le chômage, les contrats courts la coupent, le temps partiel la
raccourcit. La population de la page Coût (action 136, étape 6) n'a que le
temps partiel ; ses hommes touchent le minimum contributif deux fois moins
souvent que ceux de l'EACR, et ses bénéficiaires sont des carrières courtes,
non des salaires bas : c'est le volume qui manque.

LES DEUX TABLEAUX
-----------------
``volume`` : la fiche « Revenu salarial » d'« Emploi, chômage, revenus du
travail », édition 2026, figure 1 — pour 2023, le revenu salarial annuel
moyen, le salaire annuel moyen en équivalent temps plein et le volume de
travail annuel moyen en équivalent temps plein, par sexe, âge, diplôme,
catégorie, quotité et secteur, tous salariés du privé et de la fonction
publique. Le volume est à peu près le rapport des deux premiers, sans l'être
exactement : le récupérateur vérifie ligne par ligne qu'il ne s'en écarte pas
de plus de deux centièmes.

``heures`` : le dossier « Dans le secteur privé, la moitié des salariés qui
avaient un bas revenu salarial en 2011 sont dans la même situation 8 ans plus
tard » de la même publication, édition 2024 (Emmanuel Berger, Dares), figure 5
— pour 2019, les heures salariées dans l'année, centile par centile, des
salariés du privé de 24 à 62 ans et de ceux d'entre eux à bas revenu salarial
(dans les 20 % les plus bas deux années de suite). Les centiles doivent
croître ; le centième, que l'INSEE dit non significatif, ne se lit pas.

Les deux classeurs sont gardés dans ``data/brut/``, à côté du fichier produit,
``data/brut/insee_volume_travail.json`` : il n'est pas lu par le modèle,
seulement par ``scripts/verifier_donnees.py``.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lecture_xlsx import feuilles  # noqa: E402

ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
BRUT = Path("data/brut")
SORTIE = BRUT / "insee_volume_travail.json"

#: Les deux classeurs : nom local, adresse, page qui les sert.
CLASSEURS = {
    "volume": ("insee_revenu_salarial_2026.xlsx",
               "https://www.insee.fr/fr/statistiques/fichier/8733097/ECRT2026_F30.xlsx",
               "https://www.insee.fr/fr/statistiques/8733097"),
    "heures": ("insee_bas_revenus_salariaux_2024.xlsx",
               "https://www.insee.fr/fr/statistiques/fichier/8195699/ECRT2024-D3.xlsx",
               "https://www.insee.fr/fr/statistiques/8195699"),
}

#: Les lignes de la figure 1 de la fiche, sous le nom que le dépôt leur donne :
#: (caractéristique, modalité).
LIGNES_VOLUME = {
    "Femmes": ("sexe", "F"), "Hommes": ("sexe", "H"),
    "Moins de 25 ans": ("age", "Y_LT25"), "25-39 ans": ("age", "Y25T39"),
    "40-49 ans": ("age", "Y40T49"), "50-54 ans": ("age", "Y50T54"),
    "55 ans ou plus": ("age", "Y_GE55"),
    "Diplôme supérieur à bac+2": ("diplome", "superieur_bac_2"),
    "Bac+2": ("diplome", "bac_2"), "Bac": ("diplome", "bac"),
    "CAP, BEP ou moins": ("diplome", "cap_bep"), "Sans diplôme": ("diplome", "sans_diplome"),
    "Cadres": ("categorie", "cadres"),
    "Professions intermédiaires": ("categorie", "professions_intermediaires"),
    "Employés": ("categorie", "employes"), "Ouvriers": ("categorie", "ouvriers"),
    "Temps complet": ("quotite", "temps_complet"), "Temps partiel": ("quotite", "temps_partiel"),
    "Secteur privé": ("secteur", "prive"), "Fonction publique": ("secteur", "fonction_publique"),
    "Ensemble": ("ensemble", "ensemble"),
}

#: Le volume publié n'est pas exactement le rapport du revenu salarial au
#: salaire en équivalent temps plein : il s'en écarte de −0,001 à +0,016 dans le
#: classeur, l'INSEE ne calculant pas les trois moyennes sur la même
#: pondération. Deux centièmes de plus trahiraient une colonne mal lue.
ECART_VOLUME = 0.02


def _libelle(texte: str) -> str:
    """Un libellé sans espace insécable, sans renvoi de note, sans espace en trop."""
    return " ".join(texte.replace("\xa0", " ").rstrip("¹²³ ").split())


def _lignes(grille: dict[tuple[int, int], float | str]) -> list[list[float | str]]:
    rangs = sorted({ligne for ligne, _ in grille})
    return [[grille[(r, c)] for c in sorted(c for l, c in grille if l == r)] for r in rangs]


def lire_volume(classeur: bytes) -> dict[str, float]:
    """La figure 1 de la fiche : ``{caractéristique|modalité|mesure: valeur}``."""
    grille = feuilles(classeur, ("Figure 1",))["Figure 1"]
    serie: dict[str, float] = {}
    for cellules in _lignes(grille):
        if len(cellules) != 4 or not isinstance(cellules[0], str):
            continue
        cle = LIGNES_VOLUME.get(_libelle(cellules[0]))
        if cle is None:
            continue
        revenu, salaire, volume = (float(c) for c in cellules[1:])
        if abs(revenu / salaire - volume) > ECART_VOLUME:
            raise ValueError(f"{cellules[0]} : le volume {volume} n'est pas le rapport "
                             f"du revenu salarial {revenu} au salaire {salaire}")
        for mesure, valeur in (("revenu_salarial", revenu), ("salaire_eqtp", salaire),
                               ("volume_eqtp", volume)):
            serie[f"{cle[0]}|{cle[1]}|{mesure}"] = valeur
    manquantes = sorted(set(LIGNES_VOLUME) - {_libelle(c[0]) for c in _lignes(grille)
                                              if c and isinstance(c[0], str)})
    if manquantes:
        raise ValueError(f"figure 1 : lignes introuvables {manquantes}")
    return serie


def lire_heures(classeur: bytes) -> dict[str, float]:
    """La figure 5 du dossier : ``{population|centile: heures}``."""
    grille = feuilles(classeur, ("Figure 5",))["Figure 5"]
    serie: dict[str, float] = {}
    for cellules in _lignes(grille):
        if len(cellules) != 3 or not all(isinstance(c, float) for c in cellules):
            continue
        centile, bas, tous = cellules
        serie[f"bas_revenus|{int(centile)}"] = bas
        serie[f"ensemble|{int(centile)}"] = tous
    for population in ("bas_revenus", "ensemble"):
        heures = [serie.get(f"{population}|{c}") for c in range(100)]
        if None in heures:
            raise ValueError(f"figure 5 : centiles manquants pour {population}")
        if any(b < a for a, b in zip(heures, heures[1:])):
            raise ValueError(f"figure 5 : les heures de {population} ne croissent pas")
    return serie


def main() -> int:
    BRUT.mkdir(parents=True, exist_ok=True)
    classeurs = {}
    for nom, (local, adresse, _) in CLASSEURS.items():
        chemin = BRUT / local
        try:
            requete = urllib.request.Request(adresse, headers=ENTETES)
            with urllib.request.urlopen(requete, timeout=120) as reponse:
                classeurs[nom] = reponse.read()
        except urllib.error.URLError as erreur:
            print(f"{adresse} : {erreur}", file=sys.stderr)
            return 1
        chemin.write_bytes(classeurs[nom])
    try:
        volume = lire_volume(classeurs["volume"])
        heures = lire_heures(classeurs["heures"])
    except (KeyError, ValueError) as erreur:
        print(f"classeurs de l'INSEE : {erreur} — rien n'est écrit", file=sys.stderr)
        return 1
    SORTIE.write_text(json.dumps({
        "classeurs": {nom: {"fichier": local, "adresse": adresse, "page": page}
                      for nom, (local, adresse, page) in CLASSEURS.items()},
        "recupere_le": date.today().isoformat(),
        "volume": {"annee": 2023, "serie": dict(sorted(volume.items()))},
        "heures": {"annee": 2019, "serie": heures},
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"volume en 2023 : femmes {volume['sexe|F|volume_eqtp']}, "
          f"hommes {volume['sexe|H|volume_eqtp']} année d'équivalent temps plein")
    print(f"heures en 2019, médiane : {heures['ensemble|50']:.0f} pour tous, "
          f"{heures['bas_revenus|50']:.0f} aux bas revenus salariaux")
    print(f"{SORTIE} : {len(volume)} valeurs de la fiche, {len(heures)} centiles d'heures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
