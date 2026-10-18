"""L'âge du premier trimestre, génération par génération : lu dans les données détaillées de l'EIC 2017, certifié dans un CSV.

`premier_trimestre.csv` est écrit par `scripts/verifier_donnees.py` depuis ce
que `scripts/fetch/drees_premier_trimestre.py` lit dans le fichier
« eic2017_data_drees_er » du jeu « Les droits validés au cours de la
carrière » de la DREES : la part des affiliés d'avant 23 ans qui ont validé,
à chaque âge de 16 à 23 ans, au moins un trimestre, et au moins un trimestre
cotisé, sexe par sexe, pour les générations 1942 à 1994. Le fichier reste dans
`data/brut/` : le lecteur se teste sur des lignes écrites comme les siennes, et
le fichier certifié sur ce qu'il publie.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
FICHIER = RACINE / "data" / "reference" / "macro" / "premier_trimestre.csv"

sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import drees_premier_trimestre as recuperateur  # noqa: E402


def _lignes(parts: dict[tuple[str, str, str], list[str]],
            autres: tuple[str, ...] = ()) -> bytes:
    """Le fichier de la DREES, en Latin-1, point-virgule et virgule décimale :
    pour chaque ``(génération, sexe, type de trimestre)``, la part des
    affiliés d'avant 23 ans de 16 à 23 ans ; puis ``autres``, des lignes
    qu'il porte aussi et que le lecteur laisse."""
    texte = ["Génération;Âge;Sexe;Type_indic;Type_trim;Champ;valeur"]
    for (generation, sexe, trimestre), valeurs in parts.items():
        for age, valeur in zip(range(16, 24), valeurs):
            texte.append(f"{generation};{age};{sexe};Part_aff;{trimestre};"
                         f"Aff_avant_23ans;{valeur}")
    texte.extend(autres)
    return ("\r\n".join(texte) + "\r\n").encode("latin-1")


#: Les hommes et les femmes nés en 1954, tels que le fichier les publie.
HOMMES_1954_COTISE = ["29,9", "50,8", "67,3", "77,7", "84", "88,2", "93,5", "96"]
HOMMES_1954_VALIDE = ["30,3", "52", "70,6", "83,4", "93,4", "95,7", "97,9", "99,3"]
FEMMES_1954_COTISE = ["22,5", "44", "62,4", "75,4", "83,2", "87,9", "92,1", "94,4"]
FEMMES_1954_VALIDE = ["22,8", "44,4", "65,2", "78,9", "86,9", "92,2", "96", "98,3"]

PUBLIE = {
    ("1954", "Hommes", "Cotisé"): HOMMES_1954_COTISE,
    ("1954", "Hommes", "Validé"): HOMMES_1954_VALIDE,
    ("1954", "Femmes", "Cotisé"): FEMMES_1954_COTISE,
    ("1954", "Femmes", "Validé"): FEMMES_1954_VALIDE,
}

#: Des lignes du même fichier que le lecteur ne garde pas : un autre
#: indicateur, un autre type de trimestre, un autre champ, les deux sexes
#: réunis, un âge au-delà de 23 ans.
AUTRES = (
    "1954;19;Hommes;Cum_trim;Cotisé;Aff_avant_23ans;9,1",
    "1954;19;Hommes;Part_aff;SN;Aff_avant_23ans;3,7",
    "1954;19;Hommes;Part_aff;Cotisé;Aff_avant_2017;68,6",
    "1954;19;Ensemble;Part_aff;Cotisé;Aff_avant_23ans;76,5",
    "1954;24;Hommes;Part_aff;Cotisé;Aff_avant_23ans;96,9",
)


def test_le_lecteur_garde_la_part_des_affilies_d_avant_23_ans_a_chaque_age():
    """Le lecteur garde, sexe par sexe, la part des affiliés d'avant 23 ans
    qui ont validé un trimestre, et un trimestre cotisé, à chaque âge de 16 à
    23 ans : 77,7 % des hommes nés en 1954 avaient cotisé un trimestre à la fin
    de l'année de leurs 19 ans, 83,4 % en avaient validé un — le service
    national compte ici. Le reste du fichier ne se lit pas."""
    lu = recuperateur.lire(_lignes(PUBLIE, AUTRES))
    assert lu[(1954, "H", "cotise", 19)] == 77.7
    assert lu[(1954, "H", "valide", 19)] == 83.4
    assert lu[(1954, "F", "cotise", 16)] == 22.5
    assert lu[(1954, "F", "valide", 23)] == 98.3
    assert len(lu) == 4 * 8


def test_le_lecteur_refuse_une_part_qui_ne_se_cumule_pas():
    """La part d'un âge compte les affiliés qui ont validé leur premier
    trimestre à cet âge ou avant : elle ne baisse pas d'un âge au suivant, et
    celle des trimestres cotisés ne passe pas celle des trimestres validés. Un
    âge manquant se refuse aussi."""
    casse = dict(PUBLIE)
    casse[("1954", "Hommes", "Cotisé")] = [*HOMMES_1954_COTISE[:3], "60", *HOMMES_1954_COTISE[4:]]
    with pytest.raises(RuntimeError, match="baisse"):
        recuperateur.lire(_lignes(casse))
    casse = dict(PUBLIE)
    casse[("1954", "Femmes", "Cotisé")] = [*FEMMES_1954_COTISE[:3], "80", *FEMMES_1954_COTISE[4:]]
    with pytest.raises(RuntimeError, match="validé"):
        recuperateur.lire(_lignes(casse))
    casse = dict(PUBLIE)
    casse[("1954", "Hommes", "Validé")] = HOMMES_1954_VALIDE[:-1]
    with pytest.raises(RuntimeError, match="manque"):
        recuperateur.lire(_lignes(casse))


def _certifie() -> dict[tuple[str, str, str, str], float]:
    with FICHIER.open(encoding="utf-8") as flux:
        lignes = [ligne for ligne in flux if not ligne.startswith("#")]
    return {(l["generation"], l["sexe"], l["trimestre"], l["age"]): float(l["part"])
            for l in csv.DictReader(lignes)}


def test_le_fichier_certifie_redonne_ce_que_la_drees_publie():
    """Ce que le fichier de la DREES publie : 38,2 % des hommes nés en 1950
    avaient cotisé un trimestre à la fin de l'année de leurs 16 ans, 72,3 % à
    celle de leurs 19 ans ; 77,7 % de ceux nés en 1954, 75,4 % des femmes ;
    85,6 % des hommes nés en 1950 avaient validé un trimestre à 20 ans, 99,2 %
    à 23. Nés en 1970 : 3,2 % des hommes à 16 ans, 56,9 % à 19."""
    lu = _certifie()
    assert lu[("1950", "H", "cotise", "16")] == 38.2
    assert lu[("1950", "H", "cotise", "19")] == 72.3
    assert lu[("1954", "H", "cotise", "19")] == 77.7
    assert lu[("1954", "F", "cotise", "19")] == 75.4
    assert lu[("1950", "H", "valide", "20")] == 85.6
    assert lu[("1950", "H", "valide", "23")] == 99.2
    assert lu[("1970", "H", "cotise", "16")] == 3.2
    assert lu[("1970", "H", "cotise", "19")] == 56.9


def test_le_fichier_certifie_couvre_chaque_generation_de_l_echantillon():
    """Les vingt-quatre générations de l'échantillon — 1942, 1946, 1950, puis
    une sur deux de 1954 à 1994 —, les deux sexes, les deux types de
    trimestre, les huit âges ; chaque part cumulée, celle des trimestres
    cotisés sous celle des trimestres validés."""
    lu = _certifie()
    generations = sorted({int(g) for g, _, _, _ in lu})
    assert generations == [1942, 1946, 1950, *range(1954, 1995, 2)]
    assert len(lu) == len(generations) * 2 * 2 * 8
    for generation in generations:
        for sexe in ("F", "H"):
            for trimestre in ("cotise", "valide"):
                parts = [lu[(str(generation), sexe, trimestre, str(age))]
                         for age in range(16, 24)]
                assert parts == sorted(parts), (generation, sexe, trimestre)
            for age in range(16, 24):
                assert (lu[(str(generation), sexe, "cotise", str(age))]
                        <= lu[(str(generation), sexe, "valide", str(age))]), (generation, sexe)
