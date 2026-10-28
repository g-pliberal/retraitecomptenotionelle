"""Les départs d'une génération, selon l'âge et les conditions de liquidation : lus dans deux classeurs de l'EIR, certifiés dans un CSV.

`departs_generations.csv` est écrit par `scripts/verifier_donnees.py` depuis ce
que `scripts/fetch/drees_departs_generations.py` lit dans les classeurs
« Caractéristiques des retraités nés en 1950 (EIR 2016) » et « nés en 1953
(EIR 2020) » de la DREES : trois feuilles, l'âge de liquidation, la position
du départ par rapport à l'âge légal et à l'âge d'annulation de la décote, et
la condition de liquidation dans le régime principal. Les classeurs restent
dans `data/brut/` : le lecteur se teste sur des grilles rendues comme les
leurs, et le fichier certifié sur ce que les classeurs impriment.

`quintiles_eqcc_generations.csv` vient des mêmes classeurs, de leur feuille
« QuintilesEQCC » : chaque génération rangée par quintile de sa pension en
équivalent carrière complète, la durée validée et la durée cotisée de chaque
quintile, d'où la population tire la masse assimilée de chaque génération
selon le rang (action 138, étape 14).
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
FICHIER = RACINE / "data" / "reference" / "macro" / "departs_generations.csv"

sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
import drees_departs_generations as recuperateur  # noqa: E402


def _grille(lignes: list[list]) -> dict[tuple[int, int], float | str]:
    """Une feuille comme ``lecture_xlsx.feuilles`` la rend : les cellules vides
    absentes."""
    return {(r, c): v for r, ligne in enumerate(lignes) for c, v in enumerate(ligne)
            if v is not None}


#: Le haut de la feuille « ÂgeLiq_Détails » du classeur des nés en 1953, tel
#: qu'il se lit : trois colonnes d'âge sur neuf, et l'ensemble.
AGES = [
    ["sexe", "Variable", "Intitulé", "Avant 60 ans", "62 ans", "67 ans et plus", "Ensemble"],
    ["Ensemble", "Effectifs", "Effectifs (en milliers)", 114.0, 65.0, 6.0, 185.0],
    ["Femme", "Effectifs", "Effectifs (en milliers)", 40.0, 35.0, 3.0, 78.0],
    ["Homme", "Effectifs", "Effectifs (en milliers)", 74.0, 30.0, 3.0, 107.0],
    ["Ensemble", "Effectifs", "Part parmi l'ensemble des retraités (en %)",
     61.6, 35.1, 3.3, 100.0],
    ["Femme", "Effectifs", "Part parmi l'ensemble des retraités (en %)",
     51.3, 44.9, 3.8, 100.0],
    ["Homme", "Effectifs", "Part parmi l'ensemble des retraités (en %)",
     69.2, 28.0, 2.8, 100.0],
    ["Ensemble", "Carrière complète", "Part d'assurés à carrière complète (en %)",
     68.3, 60.6, 41.1, 65.0],
    ["Femme", "Carrière complète", "Part d'assurés à carrière complète (en %)",
     50.0, 56.6, 35.5, 52.0],
    ["Homme", "Carrière complète", "Part d'assurés à carrière complète (en %)",
     78.4, 65.2, 47.3, 74.0],
    # Une condition vide se lit zéro : nul ne surcote avant 60 ans.
    ["Ensemble", "Conditions de liquidation", "Part de départ avec surcote (en %)",
     None, 46.0, 34.6, 9.0],
    ["Femme", "Conditions de liquidation", "Part de départ avec surcote (en %)",
     None, 46.8, 29.1, 10.0],
    ["Homme", "Conditions de liquidation", "Part de départ avec surcote (en %)",
     None, 45.2, 40.6, 8.0],
    ["Ensemble", "Conditions de liquidation",
     "Part de départ au taux plein par la durée (hors surcote et carrière longue, en %)",
     98.0, 54.0, 65.0, 81.0],
    ["Femme", "Conditions de liquidation",
     "Part de départ au taux plein par la durée (hors surcote et carrière longue, en %)",
     99.0, 53.0, 70.9, 80.0],
    ["Homme", "Conditions de liquidation",
     "Part de départ au taux plein par la durée (hors surcote et carrière longue, en %)",
     97.0, 54.8, 59.4, 92.0],
    # Les autres conditions, vides ici : chacune a sa ligne dans la feuille.
    *[[sexe, "Conditions de liquidation", libelle, None, None, None, None]
      for libelle in ("Part de départs anticipés pour carrière longue (en %)",
                      "Part de départ avec décote (en %)",
                      "Part de départ où la décote est inapplicable (en %)",
                      "Part des retraités ayant liquidé pour invalidité (en %)",
                      "Part des retraités ayant liquidé pour inaptitude (en %)",
                      "Part de départ au taux plein pour un autre motif que l'âge, la "
                      "durée, l'invalidité ou l'inaptitude (en %)",
                      "Part de départ au taux plein par l'âge (en %)")
      for sexe in ("Ensemble", "Femme", "Homme")],
    # Ce que la feuille dit d'autre ne se lit pas : la pension, la CSG.
    ["Ensemble", "Pension brute",
     "Montant moyen de la pension de retraite totale brute (en euros/mois)",
     1900.0, 1800.0, 1500.0, 1850.0],
]


def test_le_lecteur_lit_chaque_colonne_de_l_age_de_liquidation():
    """Chaque colonne sous son code, chaque sexe : l'effectif, sa part dans la
    génération, la part des carrières complètes, et la part de chaque
    condition de liquidation, une case vide se lisant zéro ; le reste de la
    feuille n'est pas lu."""
    lu = recuperateur.lire_tableau(_grille(AGES), "age_liquidation")
    assert sorted(lu) == ["62", "67_plus", "avant_60", "ensemble"]
    assert lu["62"]["F"]["effectifs"] == 35.0
    assert lu["67_plus"]["ensemble"]["part"] == 3.3
    assert lu["avant_60"]["H"]["carriere_complete"] == 78.4
    assert lu["62"]["ensemble"]["condition_surcote"] == 46.0
    assert lu["avant_60"]["F"]["condition_surcote"] == 0.0
    assert lu["67_plus"]["H"]["condition_taux_plein_duree"] == 59.4
    assert not any("pension" in indicateur for colonne in lu.values()
                   for sexe in colonne.values() for indicateur in sexe)


def test_le_lecteur_nomme_les_positions_et_les_conditions():
    """Les en-têtes des deux autres feuilles, sous leurs codes : la position du
    départ par rapport à l'âge légal et à l'âge d'annulation de la décote, la
    condition de liquidation dans le régime principal."""
    positions = [recuperateur.code_de_colonne(entete, "position") for entete in (
        "Départ avant l'âge légal d'ouverture des droits à la retraite",
        "Départ à l'âge légal d'ouverture des droits à la retraite",
        "Départ entre l'âge légal d'ouverture des droits à la retraite et l'âge "
        "d'annulation de la décote",
        "Départ à l'âge d'annulation de la décote",
        "Départ après l'âge d'annulation de la décote", "Ensemble")]
    assert positions == ["avant_age_legal", "age_legal", "entre", "age_annulation",
                         "apres_annulation", "ensemble"]
    conditions = [recuperateur.code_de_colonne(entete, "condition") for entete in (
        "Carrière longue", "Décote", "Décote non applicable", "Surcote",
        "Taux plein invalidité", "Taux plein inaptitude", "Taux plein autres motifs",
        "Taux plein par âge", "Taux plein par la durée (hors surcote et RACL)")]
    assert conditions == list(recuperateur.CONDITIONS)
    assert recuperateur.code_de_colonne("66 ans", "age_liquidation") == "66"
    with pytest.raises(RuntimeError):
        recuperateur.code_de_colonne("Départ quelque part", "position")


def test_le_lecteur_refuse_des_colonnes_qui_ne_redonnent_pas_l_ensemble():
    """Les colonnes d'une feuille comptent toute la génération : leurs
    effectifs redonnent celui de l'ensemble, à l'arrondi du millier près, et
    leurs parts font cent ; les conditions d'une colonne ne passent pas cent.
    Le classeur laisse sans condition un retraité sur cent, et, à 65 ans, une
    femme née en 1953 sur neuf : leur somme peut rester en deçà."""
    casse = [list(ligne) for ligne in AGES]
    casse[2][4] = 45.0
    with pytest.raises(RuntimeError, match="effectifs"):
        recuperateur.lire_tableau(_grille(casse), "age_liquidation")
    casse = [list(ligne) for ligne in AGES]
    casse[11][4] = 60.0
    with pytest.raises(RuntimeError, match="conditions"):
        recuperateur.lire_tableau(_grille(casse), "age_liquidation")


def _certifie() -> dict[tuple[str, str, str, str, str], float]:
    with FICHIER.open(encoding="utf-8") as flux:
        lignes = [ligne for ligne in flux if not ligne.startswith("#")]
    return {(l["generation"], l["tableau"], l["colonne"], l["sexe"], l["indicateur"]):
            float(l["valeur"]) for l in csv.DictReader(lignes)}


def test_le_fichier_certifie_redonne_ce_que_les_classeurs_impriment():
    """Ce que les deux classeurs impriment : 757 milliers de retraités nés en
    1953, dont 14,3 % partis avec une surcote, 14,2 % des femmes et 14,5 %
    des hommes ; 53,5 % des départs à 63 ans le sont avec une surcote ; 87,4 %
    des surcotées ont une carrière complète. Nés en 1950 : 808 milliers, 46,0 %
    partis à 60 ans et 12,3 % à 65, 11,4 % à l'âge d'annulation de la décote,
    11,7 % avec une surcote, 18,2 % des hommes en carrière longue."""
    lu = _certifie()
    assert lu[("1953", "condition", "ensemble", "ensemble", "effectifs")] == 757.0
    assert lu[("1953", "condition", "surcote", "ensemble", "part")] == 14.3
    assert lu[("1953", "condition", "surcote", "F", "part")] == 14.2
    assert lu[("1953", "condition", "surcote", "H", "part")] == 14.5
    assert lu[("1953", "age_liquidation", "63", "ensemble", "condition_surcote")] == 53.5
    assert lu[("1953", "condition", "surcote", "F", "carriere_complete")] == 87.4
    assert lu[("1950", "age_liquidation", "ensemble", "ensemble", "effectifs")] == 808.0
    assert lu[("1950", "age_liquidation", "60", "ensemble", "part")] == 46.0
    assert lu[("1950", "position", "ensemble", "ensemble", "condition_surcote")] == 11.7
    assert lu[("1950", "position", "ensemble", "H", "condition_carriere_longue")] == 18.2
    assert lu[("1950", "position", "age_annulation", "ensemble", "part")] == 11.4
    assert lu[("1950", "age_liquidation", "65", "ensemble", "part")] == 12.3


def test_le_fichier_certifie_compte_chaque_generation_entiere():
    """Dans chaque génération et chaque feuille d'âge, les colonnes redonnent
    l'effectif de l'ensemble et font cent ; la colonne de l'ensemble redonne,
    condition par condition, la part que la feuille des conditions imprime."""
    lu = _certifie()
    for generation in ("1950", "1953"):
        for tableau in ("age_liquidation", "position"):
            for sexe in ("ensemble", "F", "H"):
                colonnes = {c for (g, t, c, s, i) in lu
                            if (g, t, s, i) == (generation, tableau, sexe, "effectifs")
                            and c != "ensemble"}
                effectifs = sum(lu[(generation, tableau, c, sexe, "effectifs")]
                                for c in colonnes)
                total = lu[(generation, tableau, "ensemble", sexe, "effectifs")]
                assert abs(effectifs - total) <= 3.0, (generation, tableau, sexe)
                parts = sum(lu[(generation, tableau, c, sexe, "part")] for c in colonnes)
                assert parts == pytest.approx(100.0, abs=0.6), (generation, tableau, sexe)
            for condition in recuperateur.CONDITIONS:
                assert lu[(generation, tableau, "ensemble", "ensemble",
                           f"condition_{condition}")] == pytest.approx(
                    lu[(generation, "condition", condition, "ensemble", "part")],
                    abs=0.15), (generation, tableau, condition)


#: La feuille « QuintilesEQCC » du classeur des nés en 1953, telle qu'elle se
#: lit : chaque ligne lue, par sexe, aux cinq quintiles et à l'ensemble ; une
#: ligne de plus, qui ne se lit pas.
_LIGNES_EQCC: dict[str, dict[str, list[float]]] = {
    "Effectifs (en milliers)": {
        "Ensemble": [150, 150, 150, 150, 150, 757], "Femme": [109, 96, 70, 66, 51, 393],
        "Homme": [42, 54, 80, 85, 99, 363]},
    "Part de bénéficiaires du minimum de pension dans leur régime principal (en %)": {
        "Ensemble": [55.0, 39.0, 9.0, 3.4, 0.5, 21.4], "Femme": [57.8, 47.0, 12.5, 4.6, 0.6, 30.6],
        "Homme": [47.8, 24.9, 5.9, 2.5, 0.4, 11.4]},
    "Montant moyen de la pension de retraite de droit direct brute (en euros/mois)": {
        "Ensemble": [471, 936, 1387, 1852, 2922, 1510], "Femme": [468, 907, 1345, 1811, 2640, 1239],
        "Homme": [479, 987, 1424, 1883, 3067, 1803]},
    "Montant moyen de la pension de droit direct (dont les majorations pour enfants) brute "
    "(en euros/mois)": {
        "Ensemble": [487, 965, 1420, 1895, 3006, 1551], "Femme": [486, 937, 1374, 1843, 2696, 1269],
        "Homme": [489, 1013, 1460, 1936, 3165, 1856]},
    "Coeficient de proratisation moyen": {
        "Ensemble": [67.0, 91.6, 98.1, 99.1, 97.9, 88.5], "Femme": [69.2, 92.0, 97.4, 99.3, 98.7, 86.0],
        "Homme": [61.7, 91.1, 98.5, 99.0, 97.5, 91.1]},
    "Moyenne de la durée validée (en années)": {
        "Ensemble": [31, 41, 43, 43, 43, 40], "Femme": [31, 42, 44, 43, 43, 39],
        "Homme": [30, 40, 43, 43, 42, 41]},
    "Moyenne de la durée cotisée (en années)": {
        "Ensemble": [19, 31, 38, 39, 39, 33], "Femme": [17, 29, 37, 38, 39, 30],
        "Homme": [25, 35, 40, 39, 39, 37]},
    "Moyenne de la durée cotisée hors majoration": {
        "Ensemble": [27, 38, 41, 41, 41, 38], "Femme": [26, 37, 40, 40, 40, 35],
        "Homme": [30, 40, 42, 42, 41, 40]},
    "Proportion d'assurés dont la durée validée hors majoration est inférieure à 10 ans": {
        "Ensemble": [13.0, 1.6, 0.4, 0.2, 0.2, 3.1], "Femme": [13.5, 1.9, 0.5, 0.2, 0.2, 4.4],
        "Homme": [12.0, 1.1, 0.3, 0.2, 0.2, 1.8]},
    "Proportion d'assurés dont la durée validée hors majoration est comprise entre 10 et 20 "
    "ans": {
        "Ensemble": [18.5, 4.7, 1.1, 1.3, 0.4, 5.3], "Femme": [20.4, 5.5, 1.4, 2.1, 0.7, 7.8],
        "Homme": [13.4, 3.3, 0.9, 0.6, 0.3, 2.5]},
    "Proportion d'assurés dont la durée validée hors majoration est comprise entre 20 et 30 "
    "ans": {
        "Ensemble": [23.2, 8.5, 2.9, 2.7, 1.9, 7.9], "Femme": [25.7, 9.7, 4.2, 3.8, 2.6, 11.3],
        "Homme": [16.6, 6.4, 1.7, 1.9, 1.5, 4.2]},
    "Proportion d'assurés dont la durée validée hors majoration est comprise entre 30 et 40 "
    "ans": {
        "Ensemble": [24.7, 26.5, 18.0, 19.5, 23.9, 22.6], "Femme": [24.8, 30.7, 25.1, 23.8, 33.0, 27.2],
        "Homme": [24.3, 19.1, 11.7, 16.2, 19.3, 17.5]},
    "Proportion d'assurés dont la durée validée hors majoration est supérieure ou égale à 40 "
    "ans": {
        "Ensemble": [20.7, 58.6, 77.6, 76.3, 73.5, 61.1], "Femme": [15.6, 52.1, 68.7, 70.2, 63.5, 49.3],
        "Homme": [33.8, 70.2, 85.4, 81.0, 78.6, 73.9]},
    "Part de départs anticipés pour carrière longue (en %)": {
        "Ensemble": [2.7, 14.3, 32.7, 32.5, 19.8, 20.3], "Femme": [1.7, 10.8, 22.4, 24.4, 13.2, 12.9],
        "Homme": [5.5, 20.3, 41.8, 38.7, 23.3, 28.3]},
    "Part de départ avec décote (en %)": {
        "Ensemble": [24.9, 7.5, 6.2, 6.0, 7.7, 10.6], "Femme": [25.9, 7.4, 6.3, 6.4, 8.2, 12.4],
        "Homme": [22.3, 7.6, 6.2, 5.6, 7.5, 8.6]},
    "Indice de Gini des pensions de retraite (droit direct + droit dérivé + majoration pour "
    "enfants) brutes (en euros/mois)": {
        "Ensemble": [0.393, 0.196, 0.11, 0.095, 0.167, 0.341],
        "Femme": [0.372, 0.206, 0.128, 0.11, 0.133, 0.344],
        "Homme": [0.444, 0.175, 0.093, 0.085, 0.176, 0.319]},
}

EQCC = [["sexe", "Variable", "Intitulé", "Premier quintile", "Deuxième quintile",
         "Troisième quintile", "Quatrième quintile", "Cinquième quintile", "Ensemble"]] + [
    [sexe, "", libelle, *valeurs] for libelle, sexes in _LIGNES_EQCC.items()
    for sexe, valeurs in sexes.items()]


def test_le_lecteur_lit_les_quintiles_de_la_generation():
    """La feuille « QuintilesEQCC » d'une génération : chaque quintile et
    l'ensemble, chaque sexe, sous le code des quintiles des résidents — la
    durée validée hors majorations sous l'intitulé qui se trompe —, et la part
    des départs en carrière longue et avec décote ; le reste de la feuille ne
    se lit pas. Des tranches qui ne font pas cent, des quintiles inégaux se
    refusent, comme chez les résidents."""
    lu = recuperateur.lire_quintiles(_grille(EQCC))
    assert sorted(lu) == ["ensemble", "q1", "q2", "q3", "q4", "q5"]
    assert lu["ensemble"]["effectifs"]["ensemble"] == 757.0
    assert lu["q1"]["duree_cotisee"]["H"] == 25.0
    assert lu["q1"]["duree_validee_hors_majoration"]["H"] == 30.0
    assert lu["q5"]["duree_validee"]["F"] == 43.0
    assert lu["q3"]["part_carriere_longue"]["H"] == 41.8
    assert lu["q1"]["part_decote"]["F"] == 25.9
    assert lu["q2"]["part_minimum_pension_regime_principal"]["H"] == 24.9
    assert not any("gini" in code for code in lu["q1"])
    casse = [list(ligne) for ligne in EQCC]
    rang = next(i for i, ligne in enumerate(casse) if ligne[0] == "Femme"
                and ligne[2].endswith("inférieure à 10 ans"))
    casse[rang][3] = 23.5
    with pytest.raises(RuntimeError, match="tranches"):
        recuperateur.lire_quintiles(_grille(casse))
    casse = [list(ligne) for ligne in EQCC]
    casse[1][3], casse[1][4] = 140.0, 160.0
    with pytest.raises(RuntimeError, match="inégaux"):
        recuperateur.lire_quintiles(_grille(casse))


FICHIER_EQCC = RACINE / "data" / "reference" / "macro" / "quintiles_eqcc_generations.csv"


def _quintiles_certifies() -> dict[tuple[str, str, str, str], float]:
    with FICHIER_EQCC.open(encoding="utf-8") as flux:
        lignes = [ligne for ligne in flux if not ligne.startswith("#")]
    return {(l["generation"], l["quintile"], l["indicateur"], l["sexe"]): float(l["valeur"])
            for l in csv.DictReader(lignes)}


def test_les_quintiles_certifies_redonnent_ce_que_les_classeurs_impriment():
    """Ce que les feuilles « QuintilesEQCC » des deux classeurs impriment. Nés
    en 1950, 808 milliers de retraités ; les hommes du premier quintile ont
    validé 28 années hors majorations, dont 25 cotisées, ceux du cinquième 41,
    dont 39 ; les femmes du premier 24, dont 16. Nés en 1953, les hommes du
    premier quintile 30, dont 25, du troisième 42, dont 40 ; 41,8 % de ces
    derniers sont partis en carrière longue, 5,5 % de ceux du premier ; 25,9 %
    des femmes du premier quintile avec une décote."""
    lu = _quintiles_certifies()
    assert lu[("1950", "ensemble", "effectifs", "ensemble")] == 808.0
    assert lu[("1950", "q1", "duree_validee_hors_majoration", "H")] == 28.0
    assert lu[("1950", "q1", "duree_cotisee", "H")] == 25.0
    assert lu[("1950", "q5", "duree_validee_hors_majoration", "H")] == 41.0
    assert lu[("1950", "q5", "duree_cotisee", "H")] == 39.0
    assert lu[("1950", "q1", "duree_validee_hors_majoration", "F")] == 24.0
    assert lu[("1950", "q1", "duree_cotisee", "F")] == 16.0
    assert lu[("1953", "q1", "duree_validee_hors_majoration", "H")] == 30.0
    assert lu[("1953", "q1", "duree_cotisee", "H")] == 25.0
    assert lu[("1953", "q3", "duree_validee_hors_majoration", "H")] == 42.0
    assert lu[("1953", "q3", "duree_cotisee", "H")] == 40.0
    assert lu[("1953", "q3", "part_carriere_longue", "H")] == 41.8
    assert lu[("1953", "q1", "part_carriere_longue", "H")] == 5.5
    assert lu[("1953", "q1", "part_decote", "F")] == 25.9


def test_les_quintiles_certifies_rangent_chaque_generation_en_cinquiemes():
    """Dans chaque génération, les cinq quintiles comptent chacun le cinquième
    de ses retraités, et redonnent, sexe par sexe, l'effectif de l'ensemble à
    deux centièmes près, sans le passer ; dans chaque quintile, les cinq
    tranches de durée validée hors majorations font cent."""
    lu = _quintiles_certifies()
    tranches = ("moins_10", "10_20", "20_30", "30_40", "40_plus")
    quintiles = ("q1", "q2", "q3", "q4", "q5")
    for generation in ("1950", "1953"):
        ranges = [lu[(generation, q, "effectifs", "ensemble")] for q in quintiles]
        assert max(ranges) - min(ranges) <= 0.01 * max(ranges), generation
        for sexe in ("ensemble", "F", "H"):
            somme = sum(lu[(generation, q, "effectifs", sexe)] for q in quintiles)
            ensemble = lu[(generation, "ensemble", "effectifs", sexe)]
            assert 0.98 * ensemble <= somme <= ensemble, (generation, sexe)
            for quintile in (*quintiles, "ensemble"):
                total = sum(lu[(generation, quintile,
                                f"part_duree_validee_hors_majoration_{t}", sexe)]
                            for t in tranches)
                assert total == pytest.approx(100.0, abs=0.6), (generation, quintile, sexe)
