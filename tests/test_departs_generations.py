"""Les départs d'une génération, selon l'âge et les conditions de liquidation : lus dans deux classeurs de l'EIR, certifiés dans un CSV.

`departs_generations.csv` est écrit par `scripts/verifier_donnees.py` depuis ce
que `scripts/fetch/drees_departs_generations.py` lit dans les classeurs
« Caractéristiques des retraités nés en 1950 (EIR 2016) » et « nés en 1953
(EIR 2020) » de la DREES : trois feuilles, l'âge de liquidation, la position
du départ par rapport à l'âge légal et à l'âge d'annulation de la décote, et
la condition de liquidation dans le régime principal. Les classeurs restent
dans `data/brut/` : le lecteur se teste sur des grilles rendues comme les
leurs, et le fichier certifié sur ce que les classeurs impriment.
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
