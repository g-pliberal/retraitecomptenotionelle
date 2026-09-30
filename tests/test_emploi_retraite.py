"""L'activité exercée après le départ, le cumul emploi-retraite (fiches
``cumul_emploi_retraite_et_retraite_progressive``, ``droits_apres_la_premiere_pension``
et ``seconde_pension``).

La saisie la déclare — sa date, sa fin, son statut, son revenu, l'employeur —,
la chronologie la date comme une période d'activité postérieure au départ, et
la carrière en garde les années à part : la première liquidation, que le
départ arrête, ne les voit pas.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import chronologie as chrono
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.saisie import ErreurSaisie, Saisie
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


BASE = {"naissance": "1960", "sexe": "F", "debut": "20", "liquidation": "62",
        "unite_revenu": "moyen", "salaire": "1"}

#: Deux ans d'activité après le départ, chez un autre employeur, à la moitié
#: du salaire moyen.
EMPLOI = {"age": 63.0, "fin": 65.0, "affiliation": "salarie_prive_non_cadre",
          "niveau_salaire": 0.5, "employeur": "autre"}


def _carriere(simulateur: Simulateur, emploi: dict | None = EMPLOI) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=1960, sexe="F", metiers=[Metier("salarie_prive_non_cadre", 20.0)],
        age_liquidation=62, macro=simulateur.macro, emploi_retraite=emploi)


# -- la saisie ----------------------------------------------------------------------

def test_la_saisie_porte_l_activite_apres_le_depart():
    saisie = Saisie.depuis_requete({**BASE, "emploi_retraite": "2023-03",
                                    "emploi_retraite_fin": "2025-01",
                                    "emploi_retraite_salaire": "0.5",
                                    "emploi_retraite_employeur": "dernier"})
    assert saisie.emploi_retraite_declare() == {
        "age": pytest.approx(63 + 1 / 12), "fin": pytest.approx(64 + 11 / 12),
        "affiliation": "salarie_prive_non_cadre", "niveau_salaire": 0.5,
        "employeur": "dernier"}
    requete = saisie.requete()
    for morceau in ("emploi_retraite=2023-03", "emploi_retraite_fin=2025-01",
                    "emploi_retraite_salaire=0.5", "emploi_retraite_employeur=dernier"):
        assert morceau in requete
    # Sans statut ni revenu, ceux du dernier métier.
    defaut = Saisie.depuis_requete({**BASE, "emploi_retraite": "2023-03",
                                    "emploi_retraite_fin": "2025-01"})
    assert defaut.emploi_retraite_declare()["niveau_salaire"] == 1.0
    assert "emploi_retraite_employeur" not in defaut.requete()


@pytest.mark.parametrize("champs, message", [
    ({"emploi_retraite_fin": "2025-01"}, "dites aussi quand elle commence"),
    ({"emploi_retraite": "2021-01", "emploi_retraite_fin": "2025-01"}, "elle suit le départ"),
    ({"emploi_retraite": "2023-03"}, "dites quand elle finit"),
    ({"emploi_retraite": "2023-03", "emploi_retraite_fin": "2023-02"},
     "elle finit après avoir commencé"),
    ({"emploi_retraite": "2023-03", "emploi_retraite_fin": "2024-02",
      "emploi_retraite_statut": "maladie"}, "n'est pas une activité"),
    ({"emploi_retraite": "2023-03", "emploi_retraite_fin": "2024-02",
      "emploi_retraite_salaire": "20"}, "entre 0,1 et 10 fois"),
])
def test_la_saisie_refuse_une_activite_qui_ne_se_tient_pas(champs, message):
    with pytest.raises(ErreurSaisie, match=message):
        Saisie.depuis_requete({**BASE, **champs})


# -- la chronologie et la carrière ------------------------------------------------

def test_la_chronologie_date_l_activite_apres_le_depart(simulateur):
    carriere = _carriere(simulateur)
    fait = chrono.emploi_retraite(carriere.chronologie, carriere.personne)
    assert fait["sorte"] == chrono.EMPLOI and fait["attributs"]["apres_depart"]
    assert (fait["debut"], fait["fin"]) == ("2023-02-01", "2025-02-01")
    assert fait not in chrono.periodes(carriere.chronologie, carriere.personne)
    assert carriere.emploi_retraite == {
        "debut": DateMois(2023, 2), "fin": DateMois(2025, 2),
        "affiliation": "salarie_prive_non_cadre", "employeur": "autre"}


def test_la_carriere_garde_ses_annees_a_part(simulateur):
    """Les années d'après le départ ne sont pas des lignes : la première
    liquidation ne les voit pas, et les copies de la carrière les gardent."""
    avec, sans = _carriere(simulateur), _carriere(simulateur, None)
    assert [l.annee for l in avec.lignes] == [l.annee for l in sans.lignes]
    assert [l.annee for l in avec.lignes_apres_depart] == [2023, 2024, 2025]
    premiere = avec.lignes_apres_depart[0]
    assert premiere.fraction_annee == pytest.approx(11 / 12)
    assert premiere.trimestres_valides <= 3
    assert avec.liquidee_au(DateMois(2023, 1)).lignes_apres_depart == avec.lignes_apres_depart
    assert avec.avec_lignes(avec.lignes).lignes_apres_depart == avec.lignes_apres_depart
    moteur = simulateur.scenario_actuel
    assert (moteur.calculer(avec).pension_annuelle
            == pytest.approx(moteur.calculer(sans).pension_annuelle))
