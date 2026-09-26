"""La table de minoration que l'Ircantec publie, rejouée contre le modèle.

Le dépôt applique à l'Ircantec l'escalier de l'article 16 de l'arrêté du
30 décembre 1970, lu version par version dans la base LEGI : 0,43 dix ans
avant l'âge normal, majoré de 0,017 5 par trimestre jusqu'à cinq ans avant,
de 0,012 5 sur les deux années suivantes et de 0,01 sur les trois dernières.
C'était une LECTURE DE TEXTE, et le texte est ce que la caisse doit
appliquer — pas la preuve qu'elle l'applique ainsi.

La preuve est dans l'annexe « Retraite à taux réduit — taux de minoration »
que la base documentaire du régime publie pour ses gestionnaires
(`baseircantec.retraites.fr`, tableaux 2023, lus le 22 septembre 2026) :
onze tables, une par génération de 1955 à « à compter de 1968 », chacune
donnant le coefficient trimestre par trimestre. Les valeurs ci-dessous en
sont la transcription, et ce test les oppose au barème du modèle.

Ce que la confrontation a montré, et qui ne se déduisait pas du texte : les
ancrages du barème sont des ÂGES FIXES — 1 à soixante-sept ans, 0,88 à
soixante-quatre, 0,78 à soixante-deux, 0,43 à cinquante-sept — et ils ne
bougent pas d'une génération à l'autre, alors que la colonne des durées, elle,
suit la génération. La génération 1968, dont l'âge légal est soixante-quatre
ans, se voit opposer le même 0,78 à soixante-deux ans que la génération 1955,
dont l'âge légal est soixante-deux. C'est l'âge du taux plein qui ancre
l'escalier, jamais l'âge d'ouverture.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.droit.liquider import (
    _COEFFICIENT_ANTICIPATION_PLANCHER,
    _coefficient_anticipation,
)

#: L'âge auquel le coefficient vaut un, dans toutes les tables publiées.
AGE_NORMAL = 67.0

#: La table publiée, âge par âge, telle que l'annexe l'imprime. Identique
#: pour les onze générations : c'est le constat, et il est vérifié plus bas.
TABLE_PUBLIEE: dict[float, float] = {
    67.0: 1.0,
    66 + 9 / 12: 0.99,
    66 + 6 / 12: 0.98,
    66 + 3 / 12: 0.97,
    66.0: 0.96,
    65 + 9 / 12: 0.95,
    65 + 6 / 12: 0.94,
    65 + 3 / 12: 0.93,
    65.0: 0.92,
    64 + 9 / 12: 0.91,
    64 + 6 / 12: 0.90,
    64 + 3 / 12: 0.89,
    64.0: 0.88,
    63 + 9 / 12: 0.8675,
    63 + 6 / 12: 0.855,
    63 + 3 / 12: 0.8425,
    63.0: 0.83,
    62 + 9 / 12: 0.8175,
    62 + 6 / 12: 0.805,
    62 + 3 / 12: 0.7925,
    62.0: 0.78,
    61 + 9 / 12: 0.7625,
    61 + 6 / 12: 0.745,
    61 + 3 / 12: 0.7275,
    61.0: 0.71,
    60 + 9 / 12: 0.6925,
    60 + 6 / 12: 0.675,
    60 + 3 / 12: 0.6575,
    60.0: 0.64,
    59 + 9 / 12: 0.6225,
    59 + 6 / 12: 0.605,
    59 + 3 / 12: 0.5875,
    59.0: 0.57,
    58 + 9 / 12: 0.5525,
    58 + 6 / 12: 0.535,
    58 + 3 / 12: 0.5175,
    58.0: 0.50,
    57 + 9 / 12: 0.4825,
    57 + 6 / 12: 0.465,
    57 + 3 / 12: 0.4475,
    57.0: 0.43,
}


@pytest.mark.parametrize("age,attendu", sorted(TABLE_PUBLIEE.items()))
def test_le_modele_rend_le_coefficient_publie(age: float, attendu: float):
    """Chaque ligne de l'annexe, opposée au barème du modèle."""
    trimestres = (AGE_NORMAL - age) * 4
    coefficient = _coefficient_anticipation(trimestres, 40)
    if coefficient is None:  # au-delà de la dernière ligne de la table
        coefficient = _COEFFICIENT_ANTICIPATION_PLANCHER
    assert coefficient == pytest.approx(attendu, abs=5e-5), (
        f"{age:g} ans : l'annexe donne {attendu}, le modèle {coefficient}")


def test_les_trois_marches_sont_bien_celles_de_l_arrete():
    """Un point par trimestre, puis un et quart, puis un et trois quarts.

    Le barème n'est pas une pente : c'est un escalier à trois marches, et
    c'est ce qui le distingue d'une décote linéaire. Le dépôt lui opposait
    1,1 % par trimestre jusqu'au 18 septembre 2026 — taux moyen juste à ses
    deux extrémités et faux entre les deux.
    """
    pas = {}
    ages = sorted(TABLE_PUBLIEE, reverse=True)
    for precedent, suivant in zip(ages, ages[1:]):
        pas[round(TABLE_PUBLIEE[precedent] - TABLE_PUBLIEE[suivant], 6)] = True
    assert sorted(pas) == [0.01, 0.0125, 0.0175]


def test_le_plancher_est_atteint_a_dix_ans_d_anticipation():
    """« Au plus tôt dix ans avant » : la table s'arrête, elle ne continue pas."""
    assert TABLE_PUBLIEE[57.0] == _COEFFICIENT_ANTICIPATION_PLANCHER
    assert _coefficient_anticipation(40, 40) == pytest.approx(0.43, abs=5e-5)
    assert _coefficient_anticipation(41, 40) is None


def test_l_escalier_est_ancre_sur_l_age_du_taux_plein_pas_sur_l_age_legal():
    """La découverte de l'annexe, écrite comme un test.

    Les onze tables publiées — générations 1955 à 1968 et au-delà — portent le
    MÊME coefficient au même âge, alors que l'âge légal passe de soixante-deux
    à soixante-quatre ans sur cette plage de générations. Si le modèle ancrait
    l'escalier sur l'âge d'ouverture, la génération 1968 verrait 0,78 à
    soixante-quatre ans au lieu de soixante-deux : deux ans d'écart, et huit
    points de pension.
    """
    for age_legal in (62.0, 62.75, 63.0, 64.0):
        trimestres = (AGE_NORMAL - 62.0) * 4
        assert _coefficient_anticipation(trimestres, 40) == pytest.approx(0.78)
        ancre_sur_l_age_legal = _coefficient_anticipation(
            (age_legal - 62.0) * 4, 40)
        if age_legal > 62.0:
            assert ancre_sur_l_age_legal != pytest.approx(0.78), (
                "l'âge légal n'est pas l'ancre du barème")
