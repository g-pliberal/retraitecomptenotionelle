"""Le chômage aux régimes complémentaires (action 141) : la borne de quatre
plafonds, le premier jour validé, la solidarité à 4 %, 8 % ou 12 %, et ce que
le compte notionnel porte d'une année chômée — le versement de l'Unédic ou de
l'État, la participation de l'allocataire aux scénarios 2 et 3. Les règles sont
dans `legislation/chomage_complementaires.yaml`, la fiche dans
`regles/chomage_retraite_complementaire.yaml` ; les témoins `chomage_*` et
`solidarite_*` confrontent les deux moteurs."""

from __future__ import annotations

import re

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.config import RACINE_DONNEES, PartCotisation
from retraite_notionnelle.donnees.chargement import charger_chomage_complementaires
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


@pytest.fixture(scope="module")
def regles():
    return charger_chomage_complementaires(RACINE_DONNEES)


def _carriere(simulateur, interruptions, niveau=2.0, naissance=1965):
    return simulateur.carriere_simple(
        annee_naissance=naissance, sexe="F", affiliation="salarie_prive_cadre",
        mois_naissance=1, age_debut=22, age_liquidation=64,
        niveau_salaire=niveau, profil_carriere="plat", interruptions=interruptions)


def _ligne(carriere, annee):
    (ligne,) = [l for l in carriere.lignes if l.annee == annee]
    return ligne


def _compte(simulateur, carriere, annee, part):
    constructeur = ConstructeurCompte(
        simulateur.macro, simulateur.catalogue, simulateur.affiliations,
        simulateur.indexation, simulateur.parametres.avec(part_cotisation=part))
    return constructeur.cotisation_annuelle(carriere, annee)


def _points(simulateur, regime, interruptions):
    resultat = simulateur.scenario_actuel.calculer(_carriere(simulateur, interruptions))
    detail = {p.regime: p for p in resultat.pensions_par_regime}[regime].detail
    return float(re.search(r"([\d,]+\.\d+) points", detail).group(1).replace(",", ""))


def test_les_regles_du_chomage_se_lisent(regles):
    """Ce que le fichier dit, tel que les moteurs le lisent."""
    assert regles.nature("chomage_indemnise", 2010) == "assurance"
    assert regles.nature("chomage_solidarite", 2010) == "solidarite"
    # La solidarité naît le 1er avril 1984 : avant, le régime était unique.
    assert regles.nature("chomage_solidarite", 1983) == "assurance"
    assert regles.nature("maladie", 2010) is None
    # Rien avant le 1er octobre 1967, trois mois en 1967 ; l'Ircantec en 1977.
    assert [regles.part_validee("agirc", a) for a in (1966, 1967, 1968)] == [0.0, 0.25, 1.0]
    assert regles.part_validee("ircantec", 1977) == pytest.approx(5 / 12)
    assert regles.part_validee("agirc_arrco", 2020) == 1.0
    # L'Arrco valide aux taux obligatoires la solidarité des ruptures d'avant
    # juin 2000, que l'État finance pourtant à 4 %.
    assert regles.taux_solidarite("arrco", 1995, points=True) is None
    assert regles.taux_solidarite("arrco", 1995, points=False) == 0.04
    assert regles.taux_solidarite("agirc", 1990, points=True) == 0.08
    assert regles.taux_solidarite("agirc_entreprises_nouvelles", 1990, points=True) == 0.12
    assert regles.taux_solidarite("agirc_arrco", 2021, points=True) == 0.04
    assert regles.taux_solidarite("ircantec", 2021, points=True) is None
    # La participation de l'allocataire : rien avant mars 1988, 3 % depuis 2003.
    assert regles.taux_participation(1987) == 0.0
    assert regles.taux_participation(1988) == pytest.approx(0.004 * 10 / 12)
    assert regles.taux_participation(2010) == 0.03


def test_le_salaire_de_reference_du_chomage_s_arrete_a_quatre_plafonds(simulateur):
    """Le salaire journalier de référence se calcule sur l'assiette des
    contributions, bornée à quatre plafonds (règlement de 2019, art. 11 et
    49) ; la maladie, elle, garde le salaire d'avant."""
    carriere = _carriere(simulateur, {2021: "chomage_indemnise", 2022: "maladie"},
                         niveau=8.0, naissance=1970)
    plafond = simulateur.macro.plafond_securite_sociale(2021)
    assert _ligne(carriere, 2021).revenu_reference == pytest.approx(4 * plafond)
    assert _ligne(carriere, 2022).revenu_reference > 4 * simulateur.macro.plafond_securite_sociale(2022)


def test_rien_n_est_valide_avant_1967(simulateur):
    """Les complémentaires ne valident le chômage que depuis le 1er octobre
    1967 : une année chômée de 1966 ne vaut rien au compte, quand celle de 1968
    vaut ce que l'Unédic versait."""
    carriere = simulateur.carriere_simple(
        annee_naissance=1945, sexe="H", affiliation="salarie_prive_non_cadre",
        mois_naissance=1, age_debut=19, age_liquidation=60, niveau_salaire=1.0,
        profil_carriere="plat", interruptions={1966: "chomage_indemnise",
                                               1968: "chomage_indemnise"})
    assert _compte(simulateur, carriere, 1966, PartCotisation.TOTALE).cotisation == 0.0
    assert _compte(simulateur, carriere, 1968, PartCotisation.TOTALE).cotisation > 0.0


def test_le_compte_porte_le_versement_de_l_unedic(simulateur):
    """Une année d'assurance porte 60 % de ce qu'une année travaillée porterait
    à chaque régime, et 0,8 % de son assiette ; les scénarios 2 et 3, la
    participation de l'allocataire, 3 % du salaire de référence en 2010."""
    chomee = _carriere(simulateur, {2010: "chomage_indemnise"})
    revenu = _ligne(chomee, 2010).revenu_reference
    plafond = simulateur.macro.plafond_securite_sociale(2010)
    assert revenu > plafond
    travaillee = dict(_compte(simulateur, _carriere(simulateur, {}), 2010,
                              PartCotisation.TOTALE).par_regime)
    verse = dict(_compte(simulateur, chomee, 2010, PartCotisation.TOTALE).par_regime)
    assert verse["arrco"] == pytest.approx(0.6 * travaillee["arrco"] + 0.008 * plafond)
    assert verse["agirc"] == pytest.approx(
        0.6 * travaillee["agirc"] + 0.008 * (revenu - plafond))
    salariale = _compte(simulateur, chomee, 2010, PartCotisation.SALARIALE)
    assert salariale.cotisation == pytest.approx(0.03 * revenu)
    assert salariale.part_employeur == 0.0


def test_le_compte_porte_le_versement_de_l_etat_pour_la_solidarite(simulateur):
    """Une année de solidarité porte 70 % de la cotisation au taux que l'État
    finance — 4 % à l'Arrco, 8 % sur la tranche B de l'Agirc —, taux d'appel
    compris ; l'allocataire ne paie rien, et les scénarios 2 et 3 n'en portent
    rien."""
    chomee = _carriere(simulateur, {2010: "chomage_solidarite"})
    revenu = _ligne(chomee, 2010).revenu_reference
    plafond = simulateur.macro.plafond_securite_sociale(2010)
    valeurs = simulateur.scenario_actuel.valeurs_point
    verse = dict(_compte(simulateur, chomee, 2010, PartCotisation.TOTALE).par_regime)
    assert verse["arrco"] == pytest.approx(
        0.7 * plafond * 0.04 * valeurs.achat("arrco", 2010)[1])
    assert verse["agirc"] == pytest.approx(
        0.7 * (revenu - plafond) * 0.08 * valeurs.achat("agirc", 2010)[1])
    assert _compte(simulateur, chomee, 2010, PartCotisation.SALARIALE).cotisation == 0.0


def test_la_solidarite_vaut_des_points_a_son_taux(simulateur):
    """Au scénario 1, une année d'assurance vaut les points d'une année
    travaillée ; une année de solidarité, ceux de 4 % à l'Arrco et de 8 % sur la
    tranche B de l'Agirc, au lieu des taux contractuels de l'année."""
    for regime, taux in (("arrco", 0.04), ("agirc", 0.08)):
        sans = _points(simulateur, regime, {2010: "sans_activite"})
        travaillee = _points(simulateur, regime, {})
        assurance = _points(simulateur, regime, {2010: "chomage_indemnise"})
        solidarite = _points(simulateur, regime, {2010: "chomage_solidarite"})
        assert assurance == pytest.approx(travaillee, abs=0.01)
        (periode,) = [p for p in simulateur.catalogue[regime].periodes_actives(2010)
                      if p.assiette in ("tranche_1", "tranche_a", "tranche_b")]
        appel = simulateur.scenario_actuel.valeurs_point.achat(regime, 2010)[1]
        contractuel = periode.taux_cotisation_retraite / appel
        assert (solidarite - sans) / (travaillee - sans) == pytest.approx(
            taux / contractuel, abs=0.001)
