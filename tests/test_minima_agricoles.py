"""Les deux minima des exploitants agricoles (action 138, étape 8).

La pension majorée de référence relève la pension de base des non-salariés
agricoles liquidée au taux plein (L. 732-54-1 à L. 732-54-4 du code rural) ;
le complément différentiel ajoute des points de RCO jusqu'à un pourcentage du
SMIC net agricole (L. 732-63). Leurs fiches — ``pension_majoree_reference`` et
``complement_differentiel_rco`` — disent la règle de chaque date d'effet ; ces
tests la rejouent sur des chefs d'exploitation à faible revenu, dans les deux
moteurs.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import completer
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _chef(simulateur: Simulateur, naissance: int, liquidation: float, niveau: float = 0.3,
          debut: float = 20.0, metiers: list[Metier] | None = None, **kwargs) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=kwargs.pop("sexe", "H"),
        metiers=metiers or [Metier("exploitant_agricole", debut, niveau_salaire=niveau)],
        age_liquidation=liquidation, macro=simulateur.macro, **kwargs)


def _resultat(simulateur: Simulateur, carriere: Carriere):
    resultat = simulateur.scenario_actuel.calculer(carriere)
    avantages = {a.code: a for a in resultat.avantages_appliques}
    pensions = {p.regime: p.montant for p in resultat.pensions_par_regime}
    return resultat, avantages, pensions


def _cible(simulateur: Simulateur, carriere: Carriere) -> float:
    """Le montant minimal d'une carrière complète, pourcentage × 1 820 × SMIC
    net agricole, de la règle de la date d'effet."""
    actuel = simulateur.scenario_actuel
    regle = actuel.complement_differentiel_rco.regle(
        f"{carriere.annee_liquidation:04d}-{carriere.mois_liquidation:02d}-01")
    smic, _ = actuel.complement_differentiel_rco.smic_net(carriere.annee_liquidation)
    return regle["pourcentage"] * completer.HEURES_DU_COMPLEMENT * smic


# -- les données et les règles ------------------------------------------------

def test_les_montants_de_la_pmr_se_refont_de_leurs_ancres():
    """Le fichier est ce que son récupérateur écrit : les ancres de D. 732-111
    et D. 732-113, revalorisées par les coefficients de l'article L. 161-23-1
    au centime inférieur. Le plafond de juillet 2022 retrouve celui que la MSA
    publie, et la PMR des pensions de septembre 2023 vaut le minimum
    contributif majoré, que la loi lui fait suivre."""
    chemin = RACINE / "scripts" / "fetch" / "dila_legi_pension_majoree.py"
    spec = importlib.util.spec_from_file_location("dila_legi_pension_majoree", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    lues = [(l["mesure"], l["date"], float(l["valeur"]), l["fiabilite"])
            for l in module._lignes(module.SORTIE)]
    assert lues == module.serie()
    valeurs = {(mesure, jour): valeur for mesure, jour, valeur, _ in lues}
    assert valeurs[("pmr_chef", "2009-01-01")] == 7596.00
    assert valeurs[("pmr_conjoint", "2009-01-01")] == 6036.00
    assert valeurs[("plafond", "2022-07-01")] == 11441.49
    majore = dict((jour, valeur) for jour, valeur, _ in
                  module.mesure_du_minimum("montant_majore"))
    for (mesure, jour), valeur in valeurs.items():
        if mesure == "pmr_depuis_septembre_2023":
            assert valeur == majore[jour], jour


def test_la_pmr_suit_la_version_de_sa_date_d_effet(simulateur):
    """Rien avant 2009 ; vingt-deux ans et demi exigés jusqu'en 2010,
    dix-sept et demi jusqu'en janvier 2014, aucun ensuite ; deux montants
    jusqu'en 2021 ; le montant de septembre 2023 ; le plafond de l'article
    L. 173-2 et les trimestres pour enfants depuis 2026."""
    pmr = simulateur.scenario_actuel.pension_majoree_reference
    assert not pmr.regle("2008-12-01")["existe"]
    assert pmr.regle("2010-06-01")["duree_minimale"] == 90
    assert pmr.regle("2012-06-01")["duree_minimale"] == 70
    assert pmr.regle("2015-06-01")["duree_minimale"] == 0
    assert pmr.regle("2015-06-01")["montant_reduit"] == "pmr_conjoint"
    assert pmr.regle("2022-06-01")["montant_reduit"] is None
    assert pmr.regle("2023-08-01")["montant"] == "pmr_chef"
    assert pmr.regle("2023-09-01")["montant"] == "pmr_depuis_septembre_2023"
    assert pmr.regle("2026-06-01")["plafond"] == "minimum_contributif"
    assert pmr.regle("2026-06-01")["majorations_de_duree"]
    assert pmr.montant("pmr_chef", 2019, 2) == (8272.80, pmr.montant("pmr_chef", 2019, 1)[1])


def test_le_complement_suit_la_version_de_sa_date_d_effet(simulateur):
    """Rien avant 2015 ; 73, 74 puis 75 % d'une carrière complète ; 85 % et
    la formule différentielle depuis novembre 2021 ; le taux plein au lieu de
    la durée requise depuis septembre 2023."""
    complement = simulateur.scenario_actuel.complement_differentiel_rco
    assert not complement.regle("2014-12-01")["existe"]
    assert complement.regle("2015-06-01")["pourcentage"] == 0.73
    assert complement.regle("2016-06-01")["pourcentage"] == 0.74
    assert complement.regle("2019-02-01")["formule"] == "carriere_complete"
    regle = complement.regle("2021-11-01")
    assert (regle["pourcentage"], regle["formule"], regle["condition"]) == (
        0.85, "differentielle", "duree_requise")
    assert regle["plafond_tous_regimes"]
    assert complement.regle("2023-09-01")["condition"] == "taux_plein"
    # Les montants que la MSA publie se refont au centime : 1 035,57 € par
    # mois pour 2021, 1 214,40 € au 1er janvier 2026.
    for annee, mensuel in ((2021, 1035.57), (2026, 1214.40)):
        smic, _ = complement.smic_net(annee)
        assert int(0.85 * 1820 * smic / 12 * 100) / 100 == mensuel


# -- le scénario 1 --------------------------------------------------------------

def test_un_chef_parti_en_2019_atteint_75_pour_cent_du_smic_net(simulateur):
    """Quarante-quatre ans de chef d'exploitation à faible revenu, au taux
    plein : la PMR porte la pension de base, avant surcote, à 8 272,80 € ; le
    complément de la RCO porte les deux pensions agricoles à 75 % de 1 820
    heures au SMIC net agricole, à un demi-point près."""
    carriere = _chef(simulateur, 1955, 64)
    resultat, avantages, pensions = _resultat(simulateur, carriere)
    pmr = avantages["pension_majoree_reference"]
    assert pmr.montant > 0
    assert "PMR 8,272.80 €" in pmr.detail
    assert "complement_differentiel_rco" in avantages
    valeur = 0.3392
    agricoles = pensions["msa_non_salaries"] + pensions["msa_rco"]
    assert abs(agricoles - _cible(simulateur, carriere)) <= valeur / 2 + 1e-6
    assert resultat.pension_annuelle == pytest.approx(
        resultat.total_contributif + sum(a.montant for a in resultat.avantages_appliques))


def test_un_chef_parti_en_2024_atteint_85_pour_cent(simulateur):
    """En 2024, la cible est de 85 %, et le plafond de toutes les pensions
    s'y ajoute : les deux pensions agricoles l'atteignent à un demi-point
    près."""
    carriere = _chef(simulateur, 1958, 66)
    _, avantages, pensions = _resultat(simulateur, carriere)
    assert {"pension_majoree_reference", "complement_differentiel_rco"} <= set(avantages)
    agricoles = pensions["msa_non_salaries"] + pensions["msa_rco"]
    assert agricoles == pytest.approx(_cible(simulateur, carriere), abs=0.2)


def test_ni_pmr_avant_2009_ni_complement_avant_2015(simulateur):
    _, avantages, _ = _resultat(simulateur, _chef(simulateur, 1945, 63))
    assert not {"pension_majoree_reference", "complement_differentiel_rco"} & set(avantages)
    _, avantages, _ = _resultat(simulateur, _chef(simulateur, 1950, 62))
    assert "pension_majoree_reference" in avantages
    assert "complement_differentiel_rco" not in avantages


def test_une_pension_decotee_n_a_ni_pmr_ni_complement(simulateur):
    """Trente-deux ans de carrière à 62 ans : la décote, et aucun des deux
    minima, qui ne s'ouvrent qu'au taux plein."""
    _, avantages, _ = _resultat(simulateur, _chef(simulateur, 1957, 62, debut=30.0))
    assert not {"pension_majoree_reference", "complement_differentiel_rco"} & set(avantages)


def test_les_autres_pensions_ecretent_les_deux_minima(simulateur):
    """Vingt ans de salarié bien payé, puis vingt-quatre de chef
    d'exploitation : sa pension du régime général dépasse le plafond, et ni
    la PMR ni le complément, qui le regardent depuis 2021, ne lui sont
    servis."""
    metiers = [Metier("salarie_prive_non_cadre", 20.0, niveau_salaire=1.5),
               Metier("exploitant_agricole", 40.0, niveau_salaire=0.3)]
    _, avantages, _ = _resultat(simulateur, _chef(simulateur, 1958, 66, metiers=metiers))
    assert not {"pension_majoree_reference", "complement_differentiel_rco"} & set(avantages)


def test_la_majoration_pour_enfants_ne_porte_pas_sur_la_pmr(simulateur):
    """Une mère de trois enfants : les 10 % de D. 732-38 portent sur la
    pension calculée, non sur la majoration de L. 732-54-1 ; la PMR, elle,
    compte la majoration pour enfants dans les ressources qu'elle écrête."""
    carriere = _chef(simulateur, 1958, 66, sexe="F", nombre_enfants=3)
    _, avantages, pensions = _resultat(simulateur, carriere)
    pmr = avantages["pension_majoree_reference"].montant
    part = dict(avantages["majoration_enfants"].par_regime)["msa_non_salaries"]
    assert part == pytest.approx(0.10 * (pensions["msa_non_salaries"] - pmr))


# -- les deux moteurs -------------------------------------------------------------

#: Des chefs d'exploitation à faible revenu, de 2010 à 2030 : la PMR seule,
#: écrêtée ou non, le complément de 2015 et celui de 2021, une mère de trois
#: enfants avant et après 2026, une pension décotée.
REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "20", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "64", "naissance": "1955", "primes": "0",
    "profil": "ascendant", "projection": "cor_reference", "salaire": "0.3", "sexe": "H",
    "statut": "exploitant_agricole", "stock": "prix", "table": "unisexe",
}
CAS = [
    {"naissance": "1945", "liquidation": "65"},
    {"naissance": "1950", "liquidation": "62"},
    {"naissance": "1955"},
    {"naissance": "1958", "liquidation": "66", "enfants": "3", "sexe": "F"},
    {"naissance": "1962", "liquidation": "67", "salaire": "0.15", "debut": "35"},
    {"naissance": "1957", "liquidation": "62", "debut": "30"},
    {"naissance": "1965", "liquidation": "65", "enfants": "3", "sexe": "F"},
]


def test_les_deux_moteurs_servent_les_memes_minima_agricoles():
    """Chaque étape de la liquidation écrit la même donnée en Python et en
    JavaScript, minima des exploitants compris."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    from test_liquidation import _ecarts, _python

    requetes = [{**REQUETE, **cas} for cas in CAS]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-liquidation.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus, attendus = json.loads(execution.stdout), _python(requetes)
    codes = {d["code"] for a in attendus for l in a["liquidations"]
             for d in l["complements"]["dispositifs"]}
    assert {"pension_majoree_reference", "complement_differentiel_rco"} <= codes
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
