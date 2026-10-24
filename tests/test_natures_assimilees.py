"""La nature des périodes assimilées, génération par génération : le service national, la maladie, le chômage et l'AVPF, lus dans les données détaillées de l'EIC 2017, certifiés dans un CSV.

`natures_assimilees.csv` est écrit par `scripts/verifier_donnees.py` depuis ce
que `scripts/fetch/drees_natures_assimilees.py` lit dans le fichier
« eic2017_data_drees_er » du jeu « Les droits validés au cours de la
carrière » de la DREES, celui de `premier_trimestre.csv` : parmi les affiliés
d'avant 23 ans, la part de ceux qui ont validé un trimestre de service
national, de maladie, de chômage ou d'assurance vieillesse des parents au
foyer, et le cumul de ces trimestres par affilié, à 60 ans, ou au dernier âge
que l'échantillon voit, sexe par sexe, pour les générations 1942 à 1994 ; au
dernier âge vu aussi, quand il passe 60 ans ; et le cumul des trimestres
validés et des trimestres cotisés, aux mêmes âges. Le fichier reste dans
`data/brut/` : le lecteur se teste sur des lignes écrites comme les siennes,
et le fichier certifié sur ce qu'il publie.
"""

from __future__ import annotations

import csv
import json
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
                natures: dict[str, dict[tuple[str, str], str]],
                valides: dict[str, str] | None = None) -> dict:
    """Les lignes d'une génération et d'un sexe : le cumul des trimestres
    cotisés à quelques âges — nul après le dernier âge que l'échantillon
    voit —, celui des trimestres validés, ``valides``, et, à chaque âge de
    ``natures``, la part et le cumul de chaque nature."""
    lignes = {(generation, age, sexe, "Cum_trim", "Cotisé"): valeur
              for age, valeur in cotises.items()}
    for age, valeur in (valides or {}).items():
        lignes[(generation, age, sexe, "Cum_trim", "Validé")] = valeur
    for age, valeurs in natures.items():
        for (indicateur, trimestre), valeur in valeurs.items():
            lignes[(generation, age, sexe, indicateur, trimestre)] = valeur
    return lignes


#: Les hommes et les femmes nés en 1950, que l'échantillon voit jusqu'à 67
#: ans, et ceux nés en 1976, jusqu'à 41 ans, tels que le fichier les publie.
#: Au-delà du dernier âge vu, il met à zéro le cumul des trimestres cotisés,
#: et reporte celui des trimestres validés.
PUBLIE = {
    **_generation("1950", "Hommes", {"59": "135,2", "60": "136,7", "67": "140,2", "68": "0"}, {
        "59": {("Part_aff", "SN"): "35,1", ("Cum_trim", "SN"): "1,4",
               ("Part_aff", "Maladie"): "11,7", ("Cum_trim", "Maladie"): "2,1",
               ("Part_aff", "Chômage"): "31,1", ("Cum_trim", "Chômage"): "4",
               ("Part_aff", "AVPF"): "2,4", ("Cum_trim", "AVPF"): "0,2"},
        "60": {("Part_aff", "SN"): "35,1", ("Cum_trim", "SN"): "1,4",
               ("Part_aff", "Maladie"): "12,6", ("Cum_trim", "Maladie"): "2,2",
               ("Part_aff", "Chômage"): "32,5", ("Cum_trim", "Chômage"): "4,3",
               ("Part_aff", "AVPF"): "2,5", ("Cum_trim", "AVPF"): "0,2"},
        "67": {("Part_aff", "SN"): "35,1", ("Cum_trim", "SN"): "1,4",
               ("Part_aff", "Maladie"): "13,3", ("Cum_trim", "Maladie"): "2,3",
               ("Part_aff", "Chômage"): "33,1", ("Cum_trim", "Chômage"): "4,6",
               ("Part_aff", "AVPF"): "2,6", ("Cum_trim", "AVPF"): "0,2"},
    }, {"59": "144,5", "60": "146,4", "67": "150,5", "68": "150,5"}),
    **_generation("1950", "Femmes", {"60": "110,7", "67": "113,9", "68": "0"}, {
        "60": {("Part_aff", "SN"): "0,1", ("Cum_trim", "SN"): "0",
               ("Part_aff", "Maladie"): "19,4", ("Cum_trim", "Maladie"): "2,2",
               ("Part_aff", "Chômage"): "37,6", ("Cum_trim", "Chômage"): "5,4",
               ("Part_aff", "AVPF"): "39,8", ("Cum_trim", "AVPF"): "10,5"},
        "67": {("Part_aff", "SN"): "0,1", ("Cum_trim", "SN"): "0",
               ("Part_aff", "Maladie"): "20,2", ("Cum_trim", "Maladie"): "2,3",
               ("Part_aff", "Chômage"): "38,3", ("Cum_trim", "Chômage"): "5,8",
               ("Part_aff", "AVPF"): "39,8", ("Cum_trim", "AVPF"): "10,5"},
    }, {"60": "130,5", "67": "134,1", "68": "134,1"}),
    **_generation("1976", "Hommes", {"40": "64,3", "41": "67,5", "42": "0"}, {
        "41": {("Part_aff", "SN"): "42,3", ("Cum_trim", "SN"): "1,4",
               ("Part_aff", "Maladie"): "6,4", ("Cum_trim", "Maladie"): "0,4",
               ("Part_aff", "Chômage"): "42,3", ("Cum_trim", "Chômage"): "3,2",
               ("Part_aff", "AVPF"): "4,8", ("Cum_trim", "AVPF"): "0,3"},
        "42": {("Part_aff", "SN"): "42,3", ("Cum_trim", "SN"): "0",
               ("Part_aff", "Maladie"): "6,4", ("Cum_trim", "Maladie"): "0",
               ("Part_aff", "Chômage"): "42,3", ("Cum_trim", "Chômage"): "0",
               ("Part_aff", "AVPF"): "4,8", ("Cum_trim", "AVPF"): "0"},
    }, {"41": "73", "42": "73"}),
    **_generation("1976", "Femmes", {"41": "59,5", "42": "0"}, {
        "41": {("Part_aff", "SN"): "0", ("Cum_trim", "SN"): "0",
               ("Part_aff", "Maladie"): "15,5", ("Cum_trim", "Maladie"): "0,5",
               ("Part_aff", "Chômage"): "45,1", ("Cum_trim", "Chômage"): "3,1",
               ("Part_aff", "AVPF"): "39,6", ("Cum_trim", "AVPF"): "8"},
    }, {"41": "71,6", "42": "71,6"}),
}

#: Des lignes du même fichier que le lecteur ne garde pas : un autre
#: indicateur, un autre type de trimestre, un autre champ, les deux sexes
#: réunis.
AUTRES = (
    "1950;60;Hommes;Nb_trim;SN;Aff_avant_23ans;0",
    "1950;60;Hommes;Part_trim;Maladie;Aff_avant_23ans;1,5",
    "1950;60;Hommes;Part_aff;Validé;Aff_avant_23ans;99,7",
    "1950;60;Hommes;Part_aff;Cotisé;Aff_avant_23ans;99,5",
    "1950;60;Hommes;Part_aff;SN;Aff_avant_2017;34,6",
    "1950;60;Ensemble;Part_aff;SN;Aff_avant_23ans;17,6",
)


def test_le_lecteur_garde_les_natures_a_60_ans_ou_au_dernier_age_vu():
    """Le lecteur garde, sexe par sexe, la part des affiliés d'avant 23 ans qui
    ont validé un trimestre de service national, de maladie, de chômage ou
    d'AVPF, et le cumul de ces trimestres par affilié, à 60 ans : 35,1 % des
    hommes nés en 1950, 1,4 trimestre par homme ; 12,6 % pour la maladie,
    2,2 trimestres ; 32,5 % pour le chômage, 4,3 trimestres ; 39,8 % des
    femmes pour l'AVPF, 10,5 trimestres. Une génération que l'échantillon ne
    voit pas jusqu'à 60 ans se lit au dernier âge où il la voit, celui où le
    cumul de ses trimestres cotisés est encore publié : 41 ans pour les nés en
    1976, 42,3 % des hommes avec un trimestre de service. Le reste du fichier
    ne se lit pas."""
    lu = recuperateur.lire(_lignes(PUBLIE, AUTRES))
    assert lu[(1950, "H", "service_national", "part", 60)] == 35.1
    assert lu[(1950, "H", "service_national", "cumul", 60)] == 1.4
    assert lu[(1950, "H", "maladie", "part", 60)] == 12.6
    assert lu[(1950, "H", "maladie", "cumul", 60)] == 2.2
    assert lu[(1950, "H", "chomage", "part", 60)] == 32.5
    assert lu[(1950, "H", "chomage", "cumul", 60)] == 4.3
    assert lu[(1950, "F", "maladie", "part", 60)] == 19.4
    assert lu[(1950, "F", "avpf", "part", 60)] == 39.8
    assert lu[(1950, "F", "avpf", "cumul", 60)] == 10.5
    assert lu[(1976, "H", "service_national", "part", 41)] == 42.3
    assert lu[(1976, "H", "maladie", "cumul", 41)] == 0.4
    assert lu[(1976, "F", "chomage", "cumul", 41)] == 3.1
    natures = set(recuperateur.NATURES.values())
    assert len([cle for cle in lu if cle[2] in natures and cle[4] <= 60]) == 2 * 2 * 4 * 2


def test_le_lecteur_garde_l_apres_60_ans_et_les_trimestres_valides_et_cotises():
    """Quand l'échantillon voit une génération au-delà de 60 ans, le lecteur
    garde aussi ses natures au dernier âge vu : 67 ans pour les nés en 1950,
    33,1 % des hommes au chômage, 4,6 trimestres par homme, quand ils en
    avaient 4,3 à 60 ans ; 20,2 % des femmes malades, 2,3 trimestres. Et, à
    chacun des âges lus, le cumul des trimestres validés et celui des
    trimestres cotisés au titre de l'activité, dont l'écart, les quatre
    natures ôtées, est ce qu'aucune ne dit : les hommes nés en 1950 ont validé
    146,4 trimestres à 60 ans, dont 136,7 cotisés, 150,5 et 140,2 à 67 ans.
    Ces deux cumuls n'ont pas de part ; les nés en 1976, vus jusqu'à 41 ans,
    n'ont que cet âge."""
    lu = recuperateur.lire(_lignes(PUBLIE, AUTRES))
    assert lu[(1950, "H", "chomage", "part", 67)] == 33.1
    assert lu[(1950, "H", "chomage", "cumul", 67)] == 4.6
    assert lu[(1950, "H", "maladie", "cumul", 67)] == 2.3
    assert lu[(1950, "F", "maladie", "part", 67)] == 20.2
    assert lu[(1950, "F", "maladie", "cumul", 67)] == 2.3
    assert lu[(1950, "H", "valide", "cumul", 60)] == 146.4
    assert lu[(1950, "H", "cotise", "cumul", 60)] == 136.7
    assert lu[(1950, "H", "valide", "cumul", 67)] == 150.5
    assert lu[(1950, "H", "cotise", "cumul", 67)] == 140.2
    assert lu[(1950, "F", "valide", "cumul", 67)] == 134.1
    assert lu[(1976, "H", "valide", "cumul", 41)] == 73.0
    assert lu[(1976, "F", "cotise", "cumul", 41)] == 59.5
    assert (1950, "H", "valide", "part", 60) not in lu
    assert not [cle for cle in lu if cle[0] == 1976 and cle[4] != 41]
    assert len(lu) == 2 * 2 * 4 * 2 + 2 * 4 * 2 + 4 * 2 + 2 * 2


def test_le_lecteur_refuse_ce_qui_ne_se_tient_pas():
    """Une valeur manquante à l'âge lu se refuse ; une part hors de cent
    aussi ; un cumul sans part, ou plus grand que ce que ceux qui en ont
    peuvent valider — quatre trimestres par an depuis 16 ans — ; un cumul
    qui baisse après 60 ans ; des trimestres validés en moindre nombre que
    les cotisés, ou plus nombreux que quatre par an depuis 14 ans, l'âge où
    finissait l'école avant 1959 ; une génération dont aucun cumul de
    trimestres cotisés ne dit jusqu'où l'échantillon la voit."""
    casse = dict(PUBLIE)
    del casse[("1950", "60", "Hommes", "Cum_trim", "Maladie")]
    with pytest.raises(RuntimeError, match="manque"):
        recuperateur.lire(_lignes(casse))
    casse = dict(PUBLIE)
    del casse[("1950", "60", "Femmes", "Part_aff", "AVPF")]
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
    casse = dict(PUBLIE)
    del casse[("1950", "67", "Femmes", "Cum_trim", "Validé")]
    with pytest.raises(RuntimeError, match="manque"):
        recuperateur.lire(_lignes(casse))
    casse = dict(PUBLIE)
    casse[("1950", "67", "Hommes", "Cum_trim", "Chômage")] = "4,1"
    with pytest.raises(RuntimeError, match="baisse"):
        recuperateur.lire(_lignes(casse))
    casse = dict(PUBLIE)
    casse[("1950", "60", "Hommes", "Cum_trim", "Validé")] = "130"
    with pytest.raises(RuntimeError, match="cotisés"):
        recuperateur.lire(_lignes(casse))
    casse = dict(PUBLIE)
    casse[("1976", "41", "Hommes", "Cum_trim", "Validé")] = "120"
    with pytest.raises(RuntimeError, match="par an"):
        recuperateur.lire(_lignes(casse))
    casse = {(generation, age, sexe, indicateur, trimestre): valeur
             for (generation, age, sexe, indicateur, trimestre), valeur in PUBLIE.items()
             if (generation, sexe, trimestre) != ("1976", "Femmes", "Cotisé")}
    with pytest.raises(RuntimeError, match="voit"):
        recuperateur.lire(_lignes(casse))


def test_le_recuperateur_lit_un_fichier_deja_telecharge(tmp_path, monkeypatch):
    """``--fichier`` lit le fichier déjà téléchargé, sans le portail de la
    DREES, qui coupe souvent ses connexions, et écrit ce qu'il garde comme
    après un téléchargement."""
    fichier = tmp_path / "eic2017_data_drees_er.csv"
    fichier.write_bytes(_lignes(PUBLIE, AUTRES))
    sortie = tmp_path / "drees_natures_assimilees.json"
    monkeypatch.setattr(recuperateur, "SORTIE", sortie)
    assert recuperateur.main(["--fichier", str(fichier)]) == 0
    valeurs = json.loads(sortie.read_text(encoding="utf-8"))["valeurs"]
    assert len(valeurs) == 60
    assert {"generation": 1950, "sexe": "H", "nature": "cotise", "indicateur": "cumul",
            "age": 67, "valeur": 140.2} in valeurs


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
    des femmes nées en 1950. Un trimestre de chômage : 32,5 % des hommes nés
    en 1950, 4,3 trimestres par homme — treize chacun —, 41,0 % de ceux nés
    en 1956, 5,0 trimestres ; 37,6 % des femmes nées en 1950, 5,4 trimestres.
    Un trimestre d'assurance vieillesse des parents au foyer : 39,8 % des
    femmes nées en 1950, 10,5 trimestres par femme — vingt-six chacune —,
    45,5 % de celles nées en 1956, 12,3 trimestres ; 2,5 % des hommes nés en
    1950. Nés en 1976, vus jusqu'à 41 ans : 42,3 % des hommes avec un
    trimestre de service ; nés en 1980, 0,2 %."""
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
    assert lu[("1950", "H", "chomage", "part", "60")] == 32.5
    assert lu[("1950", "H", "chomage", "cumul", "60")] == 4.3
    assert lu[("1956", "H", "chomage", "part", "60")] == 41.0
    assert lu[("1956", "H", "chomage", "cumul", "60")] == 5.0
    assert lu[("1950", "F", "chomage", "part", "60")] == 37.6
    assert lu[("1950", "F", "chomage", "cumul", "60")] == 5.4
    assert lu[("1950", "F", "avpf", "part", "60")] == 39.8
    assert lu[("1950", "F", "avpf", "cumul", "60")] == 10.5
    assert lu[("1956", "F", "avpf", "part", "60")] == 45.5
    assert lu[("1956", "F", "avpf", "cumul", "60")] == 12.3
    assert lu[("1950", "H", "avpf", "part", "60")] == 2.5
    assert lu[("1976", "H", "service_national", "part", "41")] == 42.3
    assert lu[("1980", "H", "service_national", "part", "37")] == 0.2


def test_le_fichier_certifie_dit_ce_que_l_echantillon_valide_apres_60_ans():
    """Ce que le fichier de la DREES publie au-delà de 60 ans, et le cumul des
    trimestres validés et des trimestres cotisés. Nés en 1950, à 67 ans :
    33,1 % des hommes au chômage, 4,6 trimestres par homme, 4,3 à 60 ans ;
    13,3 % malades, 2,3 trimestres ; 150,5 trimestres validés, dont 140,2
    cotisés — 10,3 validés sans être cotisés, 9,7 à 60 ans, quand les quatre
    natures en font 8,1 à 60 ans, 8,5 à 67. Nés en 1954, à 63 ans : 153,3
    validés, 142,4 cotisés, 4,9 trimestres de chômage ; en 1956, à 61 ans,
    151,5 et 140,3 ; en 1942, à 71 ans, le dernier âge que le fichier publie,
    147,9 et 136,6. Les femmes nées en 1950 : 130,5 et 110,7 à 60 ans, 134,1
    et 113,9 à 67, 38,3 % au chômage, 5,8 trimestres."""
    lu = _certifie()
    assert lu[("1950", "H", "chomage", "part", "67")] == 33.1
    assert lu[("1950", "H", "chomage", "cumul", "67")] == 4.6
    assert lu[("1950", "H", "maladie", "part", "67")] == 13.3
    assert lu[("1950", "H", "maladie", "cumul", "67")] == 2.3
    assert lu[("1950", "H", "valide", "cumul", "67")] == 150.5
    assert lu[("1950", "H", "cotise", "cumul", "67")] == 140.2
    assert lu[("1950", "H", "valide", "cumul", "60")] == 146.4
    assert lu[("1950", "H", "cotise", "cumul", "60")] == 136.7
    quatre = ("service_national", "maladie", "chomage", "avpf")
    assert sum(lu[("1950", "H", n, "cumul", "60")] for n in quatre) == pytest.approx(8.1)
    assert sum(lu[("1950", "H", n, "cumul", "67")] for n in quatre) == pytest.approx(8.5)
    assert lu[("1954", "H", "valide", "cumul", "63")] == 153.3
    assert lu[("1954", "H", "cotise", "cumul", "63")] == 142.4
    assert lu[("1954", "H", "chomage", "cumul", "63")] == 4.9
    assert lu[("1956", "H", "valide", "cumul", "61")] == 151.5
    assert lu[("1956", "H", "cotise", "cumul", "61")] == 140.3
    assert lu[("1942", "H", "valide", "cumul", "71")] == 147.9
    assert lu[("1942", "H", "cotise", "cumul", "71")] == 136.6
    assert lu[("1950", "F", "valide", "cumul", "60")] == 130.5
    assert lu[("1950", "F", "cotise", "cumul", "60")] == 110.7
    assert lu[("1950", "F", "valide", "cumul", "67")] == 134.1
    assert lu[("1950", "F", "cotise", "cumul", "67")] == 113.9
    assert lu[("1950", "F", "chomage", "part", "67")] == 38.3
    assert lu[("1950", "F", "chomage", "cumul", "67")] == 5.8


def test_le_fichier_certifie_couvre_chaque_generation_de_l_echantillon():
    """Les vingt-quatre générations de l'échantillon — 1942, 1946, 1950, puis
    une sur deux de 1954 à 1994 —, les deux sexes, les quatre natures, la
    part et le cumul, chacune à 60 ans ou au dernier âge que l'échantillon de
    2017 voit, 2017 moins la génération ; celles qu'il voit au-delà de
    60 ans, à ce dernier âge aussi — 1942 et 1946 jusqu'à 71 ans, le dernier
    que le fichier publie, 1950 jusqu'à 67, 1954 jusqu'à 63, 1956 jusqu'à
    61 — ; à chaque âge, le cumul des trimestres validés et celui des
    trimestres cotisés. Chaque part sous cent, chaque cumul sous ce que ceux
    qui en ont peuvent valider ; aucun ne baisse après 60 ans ; les
    trimestres cotisés ne passent pas les validés, ni ceux-ci quatre par an
    depuis 14 ans."""
    lu = _certifie()
    generations = sorted({int(g) for g, _, _, _, _ in lu})
    assert generations == [1942, 1946, 1950, *range(1954, 1995, 2)]
    au_dela = {g: min(71, 2017 - g) for g in generations if 2017 - g > 60}
    assert au_dela == {1942: 71, 1946: 71, 1950: 67, 1954: 63, 1956: 61}
    assert len(lu) == (len(generations) + len(au_dela)) * 2 * (4 * 2 + 2)
    quatre = ("service_national", "maladie", "chomage", "avpf")
    for generation in generations:
        g = str(generation)
        ages = [min(60, 2017 - generation)] + ([au_dela[generation]]
                                               if generation in au_dela else [])
        for sexe in ("F", "H"):
            for age in ages:
                for nature in quatre:
                    part = lu[(g, sexe, nature, "part", str(age))]
                    cumul = lu[(g, sexe, nature, "cumul", str(age))]
                    assert 0.0 <= part <= 100.0, (generation, sexe, nature, age)
                    assert cumul <= 4 * (age - 15) * part / 100.0, (generation, sexe, nature, age)
                valide = lu[(g, sexe, "valide", "cumul", str(age))]
                cotise = lu[(g, sexe, "cotise", "cumul", str(age))]
                assert 0.0 <= cotise <= valide <= 4 * (age - 13), (generation, sexe, age)
            if generation in au_dela:
                for cle in [(n, i) for n in quatre for i in ("part", "cumul")] + [
                        ("valide", "cumul"), ("cotise", "cumul")]:
                    assert (lu[(g, sexe, *cle, str(au_dela[generation]))]
                            >= lu[(g, sexe, *cle, "60")]), (generation, sexe, cle)
