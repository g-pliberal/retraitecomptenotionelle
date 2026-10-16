"""La part des nouveaux retraités au minimum contributif : ce que l'EACR observe, et ce que la mesure lit.

`scripts/part_minimum_contributif.py` confronte les grilles de la page Coût à
l'enquête annuelle auprès des caisses de retraite et à TRAJECTOiRE (action
137). La mesure entière prend trois minutes et ne se rejoue pas ici ; ce qui se
tient ici la rend lisible : les fichiers certifiés redonnent ce que la DREES en
publie, la part des régimes alignés réunis comme le montant moyen du minimum,
que son contrôle borne ; une génération s'étale sur ses mois de naissance ; les
montants se confrontent en euros de 2023 ; le minimum se lit dans le
scénario 1 tel que le moteur le sert ; et les retraités de l'étranger, que
l'EACR compte et la population non, s'y ajoutent aux parts que l'EIR leur
donne (action 138, étape 14).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from retraite_notionnelle.castypes import CAS_TYPES
from retraite_notionnelle.config import Parametres

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import part_minimum_contributif as P  # noqa: E402
import verifier_donnees as V  # noqa: E402


def test_le_fichier_de_l_eacr_redonne_l_etude_de_la_drees():
    """Études et résultats n° 1297, graphique 1 et son texte (p. 3) : 17,5 % des
    nouveaux retraités du régime général et 25,1 % de ceux de la MSA salariés en
    2021. Pour 2012, l'étude lit 27,6 %, et le fichier, qui retient le
    millésime le plus récent, un demi-point de moins."""
    parts = P.observees(Parametres().racine_donnees)
    assert round(parts[(2021, "cnav", "ensemble")], 1) == 17.5
    assert round(parts[(2021, "msa_salaries", "ensemble")], 1) == 25.1
    assert 27.0 < parts[(2012, "cnav", "ensemble")] < 27.6
    # Le sexe n'est ventilé que depuis 2022, et les deux sexes encadrent l'ensemble.
    assert (2021, "cnav", "F") not in parts
    for annee in (2022, 2023, 2024):
        femmes, hommes, ensemble = (parts[(annee, "cnav", s)] for s in ("F", "H", "ensemble"))
        assert hommes < ensemble < femmes


def test_la_part_des_regimes_alignes_compte_des_personnes_depuis_2019():
    """Le champ de TRAJECTOiRE : le régime général, indépendants compris, et la
    MSA salariés, leurs bénéficiaires rapportés à leurs deux flux. Avant la
    liquidation unique de juillet 2017, qui ne s'installe qu'en deux ans, un
    polypensionné des deux caisses comptait dans les deux : la série commence
    en 2019. 17,95 % en 2021, 18,9 % en 2022, 18,8 % en 2023, 18,6 % dans
    l'estimation de 2024 ; et une part de deux caisses tombe entre les leurs."""
    parts = P.observees(Parametres().racine_donnees)
    alignes = {annee for annee, caisse, _ in parts if caisse == "regimes_alignes"}
    assert min(alignes) == V.PREMIERE_ANNEE_REGIMES_ALIGNES == 2019
    assert max(alignes) == 2024
    attendues = {2021: 17.95, 2022: 18.93, 2023: 18.82, 2024: 18.55}
    for annee, attendue in attendues.items():
        assert parts[(annee, "regimes_alignes", "ensemble")] == pytest.approx(attendue)
    for (annee, caisse, sexe), part in parts.items():
        if caisse == "regimes_alignes":
            cnav, msa = parts[(annee, "cnav", sexe)], parts[(annee, "msa_salaries", sexe)]
            assert min(cnav, msa) < part < max(cnav, msa)


def test_le_montant_moyen_de_l_eacr_reste_sous_le_minimum_majore():
    """La colonne ``m1`` de la feuille E-Minima est, pour le privé, le montant
    moyen du minimum : le complément qu'il sert, en euros courants par mois,
    128 € à la Cnav en 2012, 137,7 € en 2023. Le contrôle de la certification
    rejette ce qui dépasse le minimum majoré mensuel de l'année, la MSA
    salariés de 2022 qui y recopie l'effectif ; et la liquidation unique se
    lit à la MSA salariés : un minimum proratisé jusqu'en 2017, entier depuis
    2019."""
    montants = P.montants_observes(Parametres().racine_donnees)
    assert montants[(2012, "cnav", "ensemble")] == 128.0
    assert montants[(2023, "cnav", "ensemble")] == 137.7
    assert (montants[(2023, "cnav", "F")], montants[(2023, "cnav", "H")]) == (139.8, 132.6)
    # Ni la MSA salariés de 2022, rejetée, ni 2024, que l'estimation ne chiffre pas.
    assert (2022, "msa_salaries", "ensemble") not in montants
    assert (2022, "regimes_alignes", "ensemble") not in montants
    assert not [cle for cle in montants if cle[0] == 2024]
    msa = {annee: montant for (annee, caisse, sexe), montant in montants.items()
           if caisse == "msa_salaries" and sexe == "ensemble"}
    assert max(m for a, m in msa.items() if a <= 2017) < 50.0
    assert min(m for a, m in msa.items() if a >= 2019) > 90.0

    bareme = V._bareme_minimum_majore()
    assert V._minimum_majore_mensuel(2023, bareme) == pytest.approx(847.57, abs=0.01)
    assert V._minimum_majore_mensuel(2022, bareme) == pytest.approx(741.64, abs=0.01)
    assert 5771.0 > V._minimum_majore_mensuel(2022, bareme)
    for (annee, _, _), montant in montants.items():
        assert 0.0 < montant <= V._minimum_majore_mensuel(annee, bareme)


def test_les_montants_se_confrontent_en_euros_de_2023():
    """Le modèle dit son minimum moyen en euros de 2023, comme le tableau 3 de
    TRAJECTOiRE ; l'EACR et son tableau 1 publient en euros courants. Chaque
    montant passe par le coefficient de SON année."""
    coefficients = {2012: 1.25, 2023: 1.0, 2024: 0.98}

    def coefficient_prix(depart: int, arrivee: int) -> float:
        assert arrivee == P.ANNEE_EUROS
        return coefficients[depart]

    convertis = P.en_euros_de_reference(
        {(2012, "cnav", "ensemble"): 128.0, (2023, "cnav", "ensemble"): 137.7,
         (2024, "regimes_alignes", "ensemble"): 136.0}, coefficient_prix)
    assert convertis == pytest.approx({(2012, "cnav", "ensemble"): 160.0,
                                       (2023, "cnav", "ensemble"): 137.7,
                                       (2024, "regimes_alignes", "ensemble"): 133.28})
    assert P.TRAJECTOIRE["liquidants_2024"]["euros_de"] == 2024
    assert P.TRAJECTOIRE["generation_1975"]["euros_de"] == P.ANNEE_EUROS


def test_une_generation_s_etale_sur_ses_mois_de_naissance():
    """La grille fait naître une génération en janvier ; ses autres mois de
    naissance partent au même âge, autant de mois plus tard."""
    # Un effet en janvier : chaque mois de naissance part la même année.
    assert P.etalement(1955, 2017, 1) == pytest.approx({2017: 1.0})
    # Un effet en février : le mois de décembre part l'année suivante.
    assert P.etalement(1955, 2017, 2) == pytest.approx({2017: 11 / 12, 2018: 1 / 12})
    # À 66 ans et 8 mois d'écart, quatre mois de naissance partent cette année-là.
    assert P.etalement(1954, 2020, 9) == pytest.approx({2020: 4 / 12, 2021: 8 / 12})


def test_le_minimum_se_lit_dans_le_scenario_1():
    """Le cas type au Smic de la génération 1955 a sa pension du régime général
    relevée au minimum, majoration comprise ; le cadre l'a au-dessus ; aucun
    n'est refusé, et le plafond de l'écrêtement s'applique aux deux départs,
    postérieurs à 2012."""
    cas = {c.code: c for c in CAS_TYPES}
    lignes = P._mesurer(Parametres(), ((0, cas["smic_carriere_complete"], 1955),
                                       (1, cas["cadre"], 1955)))
    mesures = {indice: mesure for indice, _, mesure in lignes}
    annee, _, minimum, majore, avant = mesures[0]
    assert 2015 <= annee <= 2017
    assert minimum > 0.0 and majore
    assert avant is not None and minimum <= avant
    assert mesures[1][2] == 0.0


def test_les_retraites_de_l_etranger_sont_ceux_de_l_eir():
    """La différence entre tous les retraités de l'EIR 2020 et ses résidents :
    3,3 % des femmes et 7,9 % des hommes, aux carrières françaises courtes,
    62 et 43 % au minimum de pension de leur régime principal."""
    etranger = P.G.non_residents(Parametres().racine_donnees)
    assert etranger["F"][0] == pytest.approx(0.0325, abs=5e-4)
    assert etranger["H"][0] == pytest.approx(0.0793, abs=5e-4)
    for sexe in ("F", "H"):
        assert sum(etranger[sexe][1].values()) == pytest.approx(1.0)
    assert etranger["F"][1]["moins_10"] == pytest.approx(0.284, abs=0.005)
    assert etranger["H"][1]["moins_10"] == pytest.approx(0.222, abs=0.005)
    assert etranger["F"][2] == pytest.approx(62.3, abs=0.1)
    assert etranger["H"][2] == pytest.approx(42.6, abs=0.1)


def test_les_retraites_de_l_etranger_se_pesent_par_tranche():
    """Repesée, une grille garde le total de chaque sexe et donne à chaque
    tranche la part des non-résidents ; mêlée aux résidents, sans nouvelle
    simulation, elle pèse ce que pesaient les résidents seuls."""
    from types import SimpleNamespace as N

    def variante(sexe, tranche):
        return N(cas=N(sexe=sexe), tranche=tranche)

    racine = Parametres().racine_donnees
    etranger = P.G.non_residents(racine)
    variantes = [variante(s, t) for s in ("F", "H")
                 for t in (None, "40_plus", "30_40", "20_30", "10_20", "moins_10")]
    poids = [1.0 + i for i in range(len(variantes))]
    ailleurs = P.G.poids_des_non_residents(variantes, poids, racine)
    for sexe in ("F", "H"):
        lot = [(v, p, q) for v, p, q in zip(variantes, poids, ailleurs) if v.cas.sexe == sexe]
        assert sum(q for _, _, q in lot) == pytest.approx(sum(p for _, p, _ in lot))
        assert (sum(q for v, _, q in lot if v.tranche == "moins_10")
                / sum(q for _, _, q in lot)) == pytest.approx(etranger[sexe][1]["moins_10"])
        pleines = sum(q for v, _, q in lot if v.tranche in (None, "40_plus"))
        assert pleines / sum(q for _, _, q in lot) == pytest.approx(etranger[sexe][1]["40_plus"])
    lignes = [(i, 1955, None) for i in range(len(variantes))]
    doubles, melange, toutes = P.avec_les_non_residents(variantes, poids, ailleurs,
                                                        lignes, etranger)
    assert len(doubles) == len(melange) == len(toutes) == 2 * len(variantes)
    assert sum(melange) == pytest.approx(sum(poids))
    assert toutes[len(variantes)][0] == len(variantes)
