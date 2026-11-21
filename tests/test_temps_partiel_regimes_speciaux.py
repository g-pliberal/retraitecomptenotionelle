"""Les services à temps partiel des régimes spéciaux ne comptent, pour le
calcul de la pension, que pour leur quotité ; pour la durée d'assurance que
la décote et la surcote lisent, ils comptent en entier.

PRÉSOMPTION : l'agent n'a pas surcotisé. Quatre règlements lui permettent de
compter son temps partiel à temps plein contre une retenue (RATP, article 18 ;
IEG, annexe 3, article 11 ; Banque de France, annexe, article 11 ; Opéra,
article 11 ; Comédie-Française, article 13 bis) : la saisie ne le dit pas, et
le modèle retient la règle par défaut du texte. Fiche
`decompte_des_services_regimes_speciaux`, paramètre `services_a_quotite`.

SNCF, décret n° 2008-639, article 7, IV, 3° (LEGIARTI000054622844) : « Pour le
calcul de la pension, à raison de la fraction de leur durée égale au rapport
entre la durée des services effectués et les obligations de service à temps
plein » ; article 13, III : les périodes à temps partiel « sont décomptées
comme des périodes d'activité à temps plein ». RATP, article 19, I, 1°
(LEGIARTI000050710714) ; IEG, annexe 3, article 9 (LEGIARTI000052046924) ;
Banque de France, annexe, article 10 (LEGIARTI000047909725) ; Opéra, article
13 ter, II (LEGIARTI000006765558) ; Comédie-Française, article 13 bis
(LEGIARTI000018253616). La CRPCEN liquide « la durée des périodes de
versement de cotisations » (article 85, I, LEGIARTI000047909839), sans
réduire le temps partiel.
"""

from __future__ import annotations

import re
import shutil

import pytest

from retraite_notionnelle import pont

pytestmark = pytest.mark.rapide

# Né le 1er janvier 1975, entré à 22 ans (janvier 1997), parti à 64 ans
# (janvier 2039) : 504 mois, 168 trimestres. À mi-temps de 2005 à 2014,
# cent vingt mois qui n'en valent que soixante : 444 mois, 148 trimestres
# liquidés. La durée d'assurance reste de 168 : le taux ne bouge pas.
# Clé : (statut, régime, trimestres liquidés, durée requise, taux en %).
CAS = {
    "sncf": ("agent_sncf", "sncf", 148, 170, 75.0),
    "ratp": ("agent_ratp", "ratp", 148, 170, 75.0),
    "ieg": ("agent_ieg", "ieg", 148, 172, 75.0),
    "banque_de_france": ("agent_banque_de_france", "banque_de_france", 148, 172, 71.25),
    "opera_de_paris": ("personnel_opera", "opera_de_paris", 148, 162, 80.625),
    "comedie_francaise": ("personnel_comedie_francaise", "comedie_francaise", 148, 172, 71.25),
    # La CRPCEN, conforme : ses 168 trimestres.
    "crpcen": ("clerc_de_notaire", "crpcen", 168, 172, 71.25),
}

DETAIL = re.compile(r"× taux ([0-9]+[.,][0-9]+) ?% × ([0-9]+)/([0-9]+)")


@pytest.fixture(scope="module")
def details() -> dict[str, tuple[float, int, int]]:
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne se fait pas tourner ici")
    from outils_pont import droit_et_fige

    appels = {
        cle: ("scenario_actuel.calculer", pont.MOTEUR, pont.CarriereSimple({
            "annee_naissance": 1975, "mois_naissance": 1, "jour_naissance": 1,
            "sexe": "H", "affiliation": statut, "age_debut": 22, "age_liquidation": 64,
            "niveau_salaire": 1.0, "temps_partiel": {annee: 0.5 for annee in range(2005, 2015)}}))
        for cle, (statut, *_) in CAS.items()
    }
    lus, refus = droit_et_fige(appels)
    assert refus == {}
    resultat = {}
    for cle, (_, regime, *_) in CAS.items():
        pension = next(p for p in lus[cle]["pensions_par_regime"] if p["regime"] == regime)
        lu = DETAIL.search(pension["detail"])
        resultat[cle] = (float(lu.group(1).replace(",", ".")), int(lu.group(2)),
                         int(lu.group(3)))
    return resultat


@pytest.mark.parametrize("cle", CAS)
def test_le_temps_partiel_compte_pour_sa_quotite_dans_les_services(details, cle):
    _, _, liquides, requis, _ = CAS[cle]
    assert details[cle][1:] == (liquides, requis)


@pytest.mark.parametrize("cle", CAS)
def test_le_temps_partiel_compte_en_entier_dans_la_duree_d_assurance(details, cle):
    assert details[cle][0] == pytest.approx(CAS[cle][-1], abs=5e-4 + 1e-9)
