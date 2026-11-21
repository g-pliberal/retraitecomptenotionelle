"""La borne de la décote des régimes spéciaux réformés en 2008 retranche
les trimestres cotisés depuis l'ouverture du droit au mois, comme la durée
d'assurance qui « totalise la durée des services », et non au prorata des
trimestres civils de chaque année.

SNCF, décret n° 2008-639, article 13, I, 2° (LEGIARTI000054622824) : « le
nombre de trimestres pris en compte ne peut excéder la différence entre
ledit nombre de trimestres permettant d'obtenir le pourcentage maximum de la
pension et 150, ce maximum étant réduit, le cas échéant, du nombre de
trimestres d'assurance au sens du III ci-après, cotisés et effectués au-delà
de l'âge auquel le droit à pension est ouvert [...]. Le nombre de trimestres
correspondant est arrondi à l'entier supérieur. » CRPCEN, décret n° 90-1215,
article 85-1 (LEGIARTI000047909834), et Comédie-Française, de même.
"""

from __future__ import annotations

import re
import shutil

import pytest

from retraite_notionnelle import pont

pytestmark = pytest.mark.rapide

# Né le 1er février 1962, entré à 25 ans (février 1987), parti à 62 ans et
# 4 mois (1er juin 2024) : 448 mois de services, 149,33 trimestres, liquidés
# à 149 sur 168. Le droit s'ouvre à 62 ans, le 1er février 2024 ; de février
# à mai, quatre mois, 1,33 trimestre cotisé au-delà.
#   1° par l'âge : 67 ans − 62 ans et 4 mois = 18,67 trimestres, arrondis à 19 ;
#   2° par la durée : 168 − 149,33 = 18,67, arrondis à 19 ;
#   la borne : 168 − 150 − 1,33 = 16,67, arrondie à 17.
# 17 trimestres à 1,25 % : 75 % × (1 − 0,2125) = 59,0625 %. Le modèle
# retranchait 0,8 trimestre (un trimestre civil, janvier à mars, réparti sur
# les cinq mois de 2024, dont quatre après l'ouverture), soit 18 trimestres :
# 58,125 %.
CAS = {
    "crpcen": ("clerc_de_notaire", "crpcen", 59.0625),
    "comedie_francaise": ("personnel_comedie_francaise", "comedie_francaise", 59.0625),
}

TAUX = re.compile(r"× taux ([0-9]+[.,][0-9]+) ?% × ([0-9]+)/([0-9]+)")


@pytest.fixture(scope="module")
def details() -> dict[str, tuple[float, int, int]]:
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne se fait pas tourner ici")
    from outils_pont import droit_et_fige

    appels = {
        cle: ("scenario_actuel.calculer", pont.MOTEUR, pont.CarriereSimple({
            "annee_naissance": 1962, "mois_naissance": 2, "jour_naissance": 1,
            "sexe": "H", "affiliation": statut, "age_debut": 25,
            "age_liquidation": 62 + 4 / 12, "niveau_salaire": 1.0}))
        for cle, (statut, _, _) in CAS.items()
    }
    lus, refus = droit_et_fige(appels)
    assert refus == {}
    resultat = {}
    for cle, (_, regime, _) in CAS.items():
        pension = next(p for p in lus[cle]["pensions_par_regime"] if p["regime"] == regime)
        lu = TAUX.search(pension["detail"])
        resultat[cle] = (float(lu.group(1).replace(",", ".")), int(lu.group(2)),
                         int(lu.group(3)))
    return resultat


@pytest.mark.parametrize("cle", CAS)
def test_la_borne_retranche_les_trimestres_cotises_depuis_l_ouverture_au_mois(details, cle):
    taux, liquides, requis = details[cle]
    assert (liquides, requis) == (149, 168)
    assert taux == pytest.approx(CAS[cle][-1], abs=5e-4 + 1e-9)
