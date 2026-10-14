"""Les prestations complémentaires de vieillesse des professions de santé
conventionnées (PCV, ex-ASV), des deux côtés (action 138, étape 18).

Le professionnel de santé conventionné cotise à un troisième étage, en
points, dont l'assurance maladie paie l'essentiel : les deux tiers du forfait
et de l'ajustement du médecin de secteur 1 (D. 645-3), les deux tiers du
forfait et 60 % de l'ajustement de l'auxiliaire médical, les deux tiers du
forfait et la moitié de l'ajustement du chirurgien-dentiste (guide de la
CNAVPL, 2025, p. 85 à 96). Le dépôt ne portait que le médecin, et sa seule
part ; l'infirmier, le kinésithérapeute et le dentiste n'avaient pas cet
étage. Ce fichier tient les deux fiches neuves, la part des caisses au compte
notionnel, et l'accord des deux moteurs.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.config import PartCotisation
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.saisie import Saisie
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur, statut: str, niveau: float = 1.0) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=1960, sexe="F",
        metiers=[Metier(affiliation=statut, age_debut=25.0, niveau_salaire=niveau)],
        age_liquidation=65.0, macro=simulateur.macro)


def _pcv(simulateur, statut: str, niveau: float = 1.0):
    resultat = simulateur.scenario_actuel.calculer(_carriere(simulateur, statut, niveau))
    return {p.regime: p for p in resultat.pensions_par_regime}


@pytest.mark.parametrize("statut,code", [
    ("auxiliaire_medical", "asv_auxiliaires_medicaux"),
    ("chirurgien_dentiste_ou_sage_femme", "asv_chirurgiens_dentistes"),
    ("medecin_liberal", "asv_conventionnes"),
])
def test_chaque_profession_de_sante_a_son_etage(simulateur, statut, code):
    """L'infirmier et le dentiste ont désormais leurs PCV, et elles suivent le
    revenu par l'ajustement."""
    modeste, aise = _pcv(simulateur, statut, 1.0), _pcv(simulateur, statut, 2.0)
    assert modeste[code].montant > 0
    assert aise[code].montant > modeste[code].montant


def test_les_points_de_l_auxiliaire_medical(simulateur):
    """Quarante ans, de 1985 à 2024 : 24,5 points par an pour le forfait (la
    règle de 2010, présumée avant 2008, sauf 2008 et 2009), plus l'ajustement
    depuis 2010, que le texte compte sur la cotisation totale — 40 % payés par
    l'auxiliaire, le tiers du forfait —, au point de 1,49 € en 2025."""
    pension = _pcv(simulateur, "auxiliaire_medical")["asv_auxiliaires_medicaux"]
    forfait = 38 * 24.5 + 44 + 26.5
    points = float(pension.detail.split(" points")[0].replace(",", ""))
    assert forfait < points < forfait + 15 * 9
    assert "valeur de service 1.49 €" in pension.detail


def test_la_part_de_l_assurance_maladie_est_au_compte(simulateur):
    """Le compte porte, sous la convention totale, ce que les caisses versent
    en plus du professionnel : le double de son forfait, une fois et demie
    son ajustement s'il est auxiliaire, autant s'il est dentiste ; sous la
    convention salariale, rien."""
    for statut, code in (("auxiliaire_medical", "asv_auxiliaires_medicaux"),
                         ("chirurgien_dentiste_ou_sage_femme", "asv_chirurgiens_dentistes"),
                         ("medecin_liberal", "asv_conventionnes")):
        carriere = _carriere(simulateur, statut)
        lignes = {}
        for part in (PartCotisation.SALARIALE, PartCotisation.TOTALE):
            constructeur = simulateur._constructeur_variante(part_cotisation=part)
            lignes[part] = constructeur.cotisation_annuelle(carriere, 2020)
        seule = dict(lignes[PartCotisation.SALARIALE].par_regime)[code]
        totale = dict(lignes[PartCotisation.TOTALE].par_regime)[code]
        assert lignes[PartCotisation.SALARIALE].part_employeur == 0.0
        assert totale == pytest.approx(
            seule + lignes[PartCotisation.TOTALE].part_employeur), statut
        # Entre une fois et demie et deux fois ce que paie le professionnel —
        # au millionième près, les deux tiers s'écrivant 0,666667.
        assert 1.5 * seule * (1 - 1e-5) <= totale - seule <= 2.0 * seule * (1 + 1e-5), statut


def test_les_points_du_medecin_ne_changent_pas(simulateur):
    """Les deux tiers du forfait et de l'ajustement : le rapport des
    cotisations totales est celui des parts du médecin, et ses points
    d'ajustement restent ce qu'ils étaient."""
    periode = next(p for p in simulateur.catalogue["asv_conventionnes"].periodes
                   if p.debut == 2020)
    assert periode.ajustement_total(1616.67, 600.0) == pytest.approx(600.0 / 1616.67,
                                                                     rel=1e-5)
    auxiliaire = next(p for p in simulateur.catalogue["asv_auxiliaires_medicaux"].periodes
                      if p.debut == 2011)
    # 0,16 % payés sur 0,40 %, 180 € sur 540 € : le rapport total est 0,40 %
    # du revenu sur 540 €.
    assert auxiliaire.ajustement_total(180.0, 0.0016 * 40000) == pytest.approx(
        0.004 * 40000 / 540.0, rel=1e-5)
    assert auxiliaire.prise_en_charge(180.0, 0.0016 * 40000) == pytest.approx(
        360.0 + 0.0024 * 40000, rel=1e-5)


def test_le_dentiste_compte_ses_points_au_plafond(simulateur):
    """Au-delà de cinq plafonds, 1,93 point d'ajustement depuis 2019 ; dix
    points de forfait par an."""
    periode = next(p for p in simulateur.catalogue["asv_chirurgiens_dentistes"].periodes
                   if p.debut == 2019)
    assert periode.points_ajustement_au_plafond == pytest.approx(1.93)
    assert periode.points_par_trimestre_valide * 4 == pytest.approx(10.0)


CAS = [
    {"statut": "auxiliaire_medical", "naissance": "1960-03-15", "debut": "25",
     "liquidation": "2025-04"},
    {"statut": "chirurgien_dentiste_ou_sage_femme", "naissance": "1962-03-15",
     "debut": "26", "liquidation": "2029-04"},
    {"statut": "medecin_liberal", "naissance": "1958-03-15", "debut": "30",
     "liquidation": "2023-04"},
]


def test_les_deux_moteurs_servent_les_memes_pcv():
    """Le résultat entier — les pensions et les comptes des six scénarios, la
    part des caisses comprise — est le même en Python et en JavaScript."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sys.path.insert(0, str(RACINE / "scripts"))
    from construire_temoins import _fini
    contexte = Contexte()
    attendus = []
    for cas in CAS:
        saisie = Saisie.depuis_requete(cas)
        attendus.append({"requete": cas,
                         "resultat": _fini(contexte.simuler(saisie).dictionnaire())})
    texte = json.dumps(attendus, ensure_ascii=False)
    assert "asv_auxiliaires_medicaux" in texte and "asv_chirurgiens_dentistes" in texte
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(texte)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]
