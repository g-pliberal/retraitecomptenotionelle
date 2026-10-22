"""La nature des périodes assimilées, génération par génération : le service national et la maladie, lus dans les données détaillées de l'EIC 2017, certifiés dans un CSV.

`natures_assimilees.csv` est écrit par `scripts/verifier_donnees.py` depuis ce
que `scripts/fetch/drees_natures_assimilees.py` lit dans le fichier
« eic2017_data_drees_er » du jeu « Les droits validés au cours de la
carrière » de la DREES, celui de `premier_trimestre.csv` : parmi les affiliés
d'avant 23 ans, la part de ceux qui ont validé un trimestre de service
national, ou de maladie, et le cumul de ces trimestres par affilié, à 60 ans,
ou au dernier âge que l'échantillon voit, sexe par sexe, pour les générations
1942 à 1994. Le fichier reste dans `data/brut/` : le lecteur se teste sur des
lignes écrites comme les siennes, et le fichier certifié sur ce qu'il publie.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
FICHIER = RACINE / "data" / "reference" / "macro" / "natures_assimilees.csv"

sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import drees_natures_assimilees as recuperateur  # noqa: E402


def _lignes(valeurs: dict[tuple[str, str, str, str, str], str],
            autres: tuple[str, ...] = ()) -> bytes:
    """Le fichier de la DREES, en Latin-1, point-virgule et virgule décimale :
    pour chaque ``(génération, âge, sexe, indicateur, type de trimestre)``, sa
    valeur parmi les affiliés d'avant 23 ans ; puis ``autres``, des lignes
    qu'il porte aussi et que le lecteur laisse."""
    texte = ["Génération;Âge;Sexe;Type_indic;Type_trim;Champ;valeur"]
    for (generation, age, sexe, indicateur, trimestre), valeur in valeurs.items():
        texte.append(f"{generation};{age};{sexe};{indicateur};{trimestre};"
                     f"Aff_avant_23ans;{valeur}")
    texte.extend(autres)
    return ("\r\n".join(texte) + "\r\n").encode("latin-1")


def _generation(generation: str, sexe: str, cotises: dict[str, str],
                natures: dict[str, dict[tuple[str, str], str]]) -> dict:
    """Les lignes d'une génération et d'un sexe : le cumul des trimestres
    cotisés à quelques âges — nul après le dernier âge que l'échantillon
    voit —, et, à chaque âge de ``natures``, la part et le cumul de chaque
    nature."""
    lignes = {(generation, age, sexe, "Cum_trim", "Cotisé"): valeur
              for age, valeur in cotises.items()}
    for age, valeurs in natures.items():
        for (indicateur, trimestre), valeur in valeurs.items():
            lignes[(generation, age, sexe, indicateur, trimestre)] = valeur
    return lignes


#: Les hommes et les femmes nés en 1950, que l'échantillon voit jusqu'à 67
#: ans, et ceux nés en 1976, jusqu'à 41 ans, tels que le fichier les publie.
PUBLIE = {
    **_generation("1950", "Hommes", {"59": "135,2", "60": "136,7", "67": "140,2", "68": "0"}, {
        "59": {("Part_aff", "SN"): "35,1", ("Cum_trim", "SN"): "1,4",
               ("Part_aff", "Maladie"): "11,7", ("Cum_trim", "Maladie"): "2,1"},
        "60": {("Part_aff", "SN"): "35,1", ("Cum_trim", "SN"): "1,4",
               ("Part_aff", "Maladie"): "12,6", ("Cum_trim", "Maladie"): "2,2"},
        "67": {("Part_aff", "SN"): "35,1", ("Cum_trim", "SN"): "1,4",
               ("Part_aff", "Maladie"): "13,3", ("Cum_trim", "Maladie"): "2,3"},
    }),
    **_generation("1950", "Femmes", {"60": "110,7", "67": "113,9", "68": "0"}, {
        "60": {("Part_aff", "SN"): "0,1", ("Cum_trim", "SN"): "0",
               ("Part_aff", "Maladie"): "19,4", ("Cum_trim", "Maladie"): "2,2"},
    }),
    **_generation("1976", "Hommes", {"40": "64,3", "41": "67,5", "42": "0"}, {
        "41": {("Part_aff", "SN"): "42,3", ("Cum_trim", "SN"): "1,4",
               ("Part_aff", "Maladie"): "6,4", ("Cum_trim", "Maladie"): "0,4"},
        "42": {("Part_aff", "SN"): "42,3", ("Cum_trim", "SN"): "0",
               ("Part_aff", "Maladie"): "6,4", ("Cum_trim", "Maladie"): "0"},
    }),
    **_generation("1976", "Femmes", {"41": "59,5", "42": "0"}, {
        "41": {("Part_aff", "SN"): "0", ("Cum_trim", "SN"): "0",
               ("Part_aff", "Maladie"): "15,5", ("Cum_trim", "Maladie"): "0,5"},
    }),
}

#: Des lignes du même fichier que le lecteur ne garde pas : un autre
#: indicateur, une autre nature, un autre champ, les deux sexes réunis.
AUTRES = (
    "1950;60;Hommes;Nb_trim;SN;Aff_avant_23ans;0",
    "1950;60;Hommes;Part_trim;Maladie;Aff_avant_23ans;1,5",
    "1950;60;Hommes;Part_aff;Chômage;Aff_avant_23ans;32,5",
    "1950;60;Hommes;Cum_trim;AVPF;Aff_avant_23ans;0,2",
    "1950;60;Hommes;Part_aff;SN;Aff_avant_2017;34,6",
    "1950;60;Ensemble;Part_aff;SN;Aff_avant_23ans;17,6",
)


def test_le_lecteur_garde_les_natures_a_60_ans_ou_au_dernier_age_vu():
    """Le lecteur garde, sexe par sexe, la part des affiliés d'avant 23 ans qui
    ont validé un trimestre de service national, ou de maladie, et le cumul de
    ces trimestres par affilié, à 60 ans : 35,1 % des hommes nés en 1950,
    1,4 trimestre par homme ; 12,6 % pour la maladie, 2,2 trimestres. Une
    génération que l'échantillon ne voit pas jusqu'à 60 ans se lit au dernier
    âge où il la voit, celui où le cumul de ses trimestres cotisés est encore
    publié : 41 ans pour les nés en 1976, 42,3 % des hommes avec un trimestre
    de service. Le reste du fichier ne se lit pas."""
    lu = recuperateur.lire(_lignes(PUBLIE, AUTRES))
    assert lu[(1950, "H", "service_national", "part", 60)] == 35.1
    assert lu[(1950, "H", "service_national", "cumul", 60)] == 1.4
    assert lu[(1950, "H", "maladie", "part", 60)] == 12.6
    assert lu[(1950, "H", "maladie", "cumul", 60)] == 2.2
    assert lu[(1950, "F", "maladie", "part", 60)] == 19.4
    assert lu[(1976, "H", "service_national", "part", 41)] == 42.3
    assert lu[(1976, "H", "maladie", "cumul", 41)] == 0.4
    assert len(lu) == 2 * 2 * 2 * 2


def test_le_lecteur_refuse_ce_qui_ne_se_tient_pas():
    """Une valeur manquante à l'âge lu se refuse ; une part hors de cent
    aussi ; un cumul sans part, ou plus grand que ce que ceux qui en ont
    peuvent valider — quatre trimestres par an depuis 16 ans — ; une
    génération dont aucun cumul de trimestres cotisés ne dit jusqu'où
    l'échantillon la voit."""
    casse = dict(PUBLIE)
    del casse[("1950", "60", "Hommes", "Cum_trim", "Maladie")]
    with pytest.raises(RuntimeError, match="manque"):
        recuperateur.lire(_lignes(casse))
    casse = dict(PUBLIE)
    casse[("1950", "60", "Femmes", "Part_aff", "Maladie")] = "119,4"
    with pytest.raises(RuntimeError, match="cent"):
        recuperateur.lire(_lignes(casse))
    casse = dict(PUBLIE)
    casse[("1976", "41", "Femmes", "Cum_trim", "SN")] = "0,3"
    with pytest.raises(RuntimeError, match="cumul"):
        recuperateur.lire(_lignes(casse))
    casse = dict(PUBLIE)
    casse[("1976", "41", "Hommes", "Cum_trim", "Maladie")] = "7"
    with pytest.raises(RuntimeError, match="cumul"):
        recuperateur.lire(_lignes(casse))
    casse = {(generation, age, sexe, indicateur, trimestre): valeur
             for (generation, age, sexe, indicateur, trimestre), valeur in PUBLIE.items()
             if (generation, sexe, trimestre) != ("1976", "Femmes", "Cotisé")}
    with pytest.raises(RuntimeError, match="voit"):
        recuperateur.lire(_lignes(casse))


def _certifie() -> dict[tuple[str, str, str, str, str], float]:
    with FICHIER.open(encoding="utf-8") as flux:
        lignes = [ligne for ligne in flux if not ligne.startswith("#")]
    return {(l["generation"], l["sexe"], l["nature"], l["indicateur"], l["age"]):
            float(l["valeur"]) for l in csv.DictReader(lignes)}


def test_le_fichier_certifie_redonne_ce_que_la_drees_publie():
    """Ce que le fichier de la DREES publie : à 60 ans, 35,1 % des hommes nés
    en 1950 avaient validé un trimestre de service national, 1,4 trimestre
    par homme — quatre chacun, une année ; 45,9 % de ceux nés en 1954,
    1,7 trimestre ; 12,6 % un trimestre de maladie, 2,2 trimestres par homme
    — dix-sept chacun —, 14,4 % de ceux nés en 1954, 2,4 trimestres ; 19,4 %
    des femmes nées en 1950. Nés en 1976, vus jusqu'à 41 ans : 42,3 % des
    hommes avec un trimestre de service ; nés en 1980, 0,2 %."""
    lu = _certifie()
    assert lu[("1950", "H", "service_national", "part", "60")] == 35.1
    assert lu[("1950", "H", "service_national", "cumul", "60")] == 1.4
    assert lu[("1954", "H", "service_national", "part", "60")] == 45.9
    assert lu[("1954", "H", "service_national", "cumul", "60")] == 1.7
    assert lu[("1950", "H", "maladie", "part", "60")] == 12.6
    assert lu[("1950", "H", "maladie", "cumul", "60")] == 2.2
    assert lu[("1954", "H", "maladie", "part", "60")] == 14.4
    assert lu[("1954", "H", "maladie", "cumul", "60")] == 2.4
    assert lu[("1950", "F", "maladie", "part", "60")] == 19.4
    assert lu[("1976", "H", "service_national", "part", "41")] == 42.3
    assert lu[("1980", "H", "service_national", "part", "37")] == 0.2


def test_le_fichier_certifie_couvre_chaque_generation_de_l_echantillon():
    """Les vingt-quatre générations de l'échantillon — 1942, 1946, 1950, puis
    une sur deux de 1954 à 1994 —, les deux sexes, les deux natures, la part
    et le cumul, chacune à 60 ans ou au dernier âge que l'échantillon de 2017
    voit, 2017 moins la génération ; chaque part sous cent, chaque cumul sous
    ce que ceux qui en ont peuvent valider."""
    lu = _certifie()
    generations = sorted({int(g) for g, _, _, _, _ in lu})
    assert generations == [1942, 1946, 1950, *range(1954, 1995, 2)]
    assert len(lu) == len(generations) * 2 * 2 * 2
    for generation in generations:
        age = str(min(60, 2017 - generation))
        for sexe in ("F", "H"):
            for nature in ("service_national", "maladie"):
                part = lu[(str(generation), sexe, nature, "part", age)]
                cumul = lu[(str(generation), sexe, nature, "cumul", age)]
                assert 0.0 <= part <= 100.0, (generation, sexe, nature)
                assert cumul <= 4 * (int(age) - 15) * part / 100.0, (generation, sexe, nature)
