"""Les deux minima des exploitants agricoles (action 138, étape 8).

La pension majorée de référence relève la pension de base des non-salariés
agricoles liquidée au taux plein (L. 732-54-1 à L. 732-54-4 du code rural) ;
le complément différentiel ajoute des points de RCO jusqu'à un pourcentage du
SMIC net agricole (L. 732-63). Leurs fiches — ``pension_majoree_reference`` et
``complement_differentiel_rco`` — disent la règle de chaque date d'effet ; ces
tests la rejouent sur des chefs d'exploitation à faible revenu, dans les deux
moteurs. Depuis le 1er septembre 2023, le taux plein ouvre aussi les points
gratuits et le complément aux pensions prises avant sans la durée requise
(fiche ``relevement_des_exploitants_2023``) : « faire vivre » les sert.
"""

from __future__ import annotations

import importlib.util
import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import completer
from retraite_notionnelle.droit.liquider import valeur_du_point
from retraite_notionnelle.echeancier import Echeancier
from retraite_notionnelle.revalorisation import faire_vivre
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
    # mois pour 2021, 1 138,63 € au 1er janvier 2023, 1 214,40 € en 2026.
    for annee, mensuel in ((2021, 1035.57), (2023, 1138.63), (2026, 1214.40)):
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
# -- le relèvement des pensions prises avant septembre 2023 --------------------

def _rco_et_base(vivante):
    regimes = {r.regime: r for r in vivante.regimes}
    return regimes["msa_rco"], regimes["msa_non_salaries"]


def test_le_taux_plein_ouvre_en_2023_ce_que_la_duree_refusait(simulateur):
    """Parti en février 2016 au taux plein par l'âge, avec 124 trimestres de chef
    et sans la durée requise tous régimes : ni points gratuits ni complément à la
    liquidation. Le 1er septembre 2023, cent points par année de chef d'avant
    2003, et le complément différentiel au SMIC net agricole de ce jour, que
    portent ses deux pensions agricoles jusqu'à la cible proratisée
    (D. 732-166-5) ; ensuite, la valeur du point. Rien avant."""
    carriere = _chef(simulateur, 1950, 66, debut=35)
    resultat, avantages, _ = _resultat(simulateur, carriere)
    assert not {"points_gratuits_rco", "complement_differentiel_rco"} & set(avantages)
    chef = resultat.chef_d_exploitation
    assert chef.eligible.taux_plein and not chef.eligible.duree_requise_atteinte
    assert (chef.gratuits, chef.complement) == (1800.0, False)
    assert faire_vivre(simulateur, carriere, resultat, 2022).relevement is None
    vivante = faire_vivre(simulateur, carriere, resultat, 2023)
    relevement = vivante.relevement
    assert (relevement.date, relevement.points_gratuits, relevement.smic_net) == (
        "2023-09-01", 1800.0, 9.0282)
    assert relevement.points_complement > 0
    valeur = valeur_du_point(simulateur.scenario_actuel, "msa_rco", carriere.date_liquidation)[0]
    rco, base = _rco_et_base(vivante)
    assert rco.relevement == pytest.approx(
        (1800 + relevement.points_complement) * relevement.valeur_point, rel=1e-12)
    # La formule de D. 732-166-4 au SMIC net de septembre 2023 et à la PMR des
    # pensions prises avant, 8 970,86 €, sous la cible proratisée : le point de
    # RCO et la pension de base ne bougent pas de septembre à décembre 2023.
    prorata = chef.eligible.duree / chef.eligible.reference
    cible = 0.85 * completer.HEURES_DU_COMPLEMENT * 9.0282
    vp = relevement.valeur_point
    formule = (cible - 8970.86) * prorata - (chef.points + 1800) * vp
    sous_la_cible = cible * prorata - (base.aujourd_hui + rco.au_depart * rco.coefficient
                                       + 1800 * vp)
    assert relevement.points_complement == math.floor(min(formule, sous_la_cible) / vp + 0.5)
    assert rco.aujourd_hui + base.aujourd_hui <= cible * prorata + vp
    assert rco.au_depart == pytest.approx(chef.points * valeur, rel=1e-9)
    en_2026 = faire_vivre(simulateur, carriere, resultat, 2026)
    assert _rco_et_base(en_2026)[0].relevement == pytest.approx(
        rco.relevement * en_2026.relevement.coefficient, rel=1e-12)


def test_une_pension_d_avant_2015_n_a_que_les_points_gratuits(simulateur):
    """Partie en 2012 : le modèle ne servant le complément qu'aux pensions prises
    depuis 2015, à leur liquidation, le relèvement n'ouvre que les points
    gratuits, comme il les ouvre depuis 2003 à qui avait la durée requise."""
    carriere = _chef(simulateur, 1945, 67, debut=40)
    resultat, _, _ = _resultat(simulateur, carriere)
    relevement = faire_vivre(simulateur, carriere, resultat, 2026).relevement
    assert (relevement.points_gratuits, relevement.points_complement) == (1800.0, 0)


def test_ce_que_la_duree_ouvrait_deja_n_est_pas_releve(simulateur):
    """La durée requise atteinte, les points gratuits et le complément sont ceux
    de la liquidation ; une pension prise depuis septembre 2023 les a reçus du
    taux plein. Ni l'une ni l'autre n'est relevée."""
    for carriere in (_chef(simulateur, 1950, 66, debut=20), _chef(simulateur, 1958, 67, debut=45)):
        resultat, _, _ = _resultat(simulateur, carriere)
        assert faire_vivre(simulateur, carriere, resultat, 2026).relevement is None


def test_l_echeancier_inscrit_le_relevement_a_sa_date(simulateur):
    """Un début de composante, que la loi induit, le 1er septembre 2023 : les
    points gratuits et ceux du complément, à la valeur du point de ce jour."""
    carriere = _chef(simulateur, 1950, 66, debut=35)
    echeancier = Echeancier(simulateur)
    entrees = {e.id: e for e in echeancier.parcourir(carriere, 2026)}
    evenement = entrees["relevement_des_exploitants_" + carriere.personne]
    assert (evenement.debut, evenement.contenu.sorte, evenement.contenu.origine) == (
        "2023-09-01", "debut_de_composante", "induit")
    relevement = faire_vivre(simulateur, carriere, echeancier.au_depart, 2026).relevement
    composante = entrees["relevement_msa_rco"].contenu
    assert composante["montant"]["annuel"] == pytest.approx(
        (relevement.points_gratuits + relevement.points_complement)
        * relevement.valeur_point, rel=1e-12)


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
    # Le relèvement de septembre 2023 : au taux plein par l'âge, sans la durée
    # requise, parti en 2016 et en 2012.
    {"naissance": "1950", "liquidation": "66", "debut": "35"},
    {"naissance": "1945", "liquidation": "67", "debut": "40"},
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
    assert sum(any(e["id"] == "relevement_msa_rco" for e in a["journal"])
               for a in attendus) == 2
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
