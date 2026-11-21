"""Les régimes spéciaux réformés en 2008 liquident selon leur nouveau
règlement les pensions qui prennent effet à compter du 1er juillet 2008, et
non du 1er janvier 2009 ; de juillet à décembre 2008, les trimestres de
surcote s'arrondissent « à l'entier supérieur ».

SNCF, décret n° 2008-639, article 13, II, rédaction du 1er juillet au 31
décembre 2008 (LEGIARTI000019108313) : la surcote compte les trimestres
effectués après le 1er juillet 2008 au-delà de l'âge d'ouverture et de la
durée requise ; « Le nombre de trimestres correspondant est arrondi à
l'entier supérieur ». Même phrase à la RATP (LEGIARTI000019104847), à l'Opéra
(LEGIARTI000019138608), à la Comédie-Française (LEGIARTI000019122583) et à la
CRPCEN (LEGIARTI000019375547). Au 1er janvier 2009 : « les trimestres entiers
cotisés » (SNCF, LEGIARTI000020085562). Le taux de ces trimestres de 2008 est
celui de la fonction publique à leur date, 0,75 %.
"""

from __future__ import annotations

import re
import shutil

import pytest

from retraite_notionnelle import pont

pytestmark = pytest.mark.rapide

# Né le 1er janvier 1946, entré à 18 ans ; durée bien au-delà de la durée
# requise. Clé : (statut, régime, âge de départ, taux attendu en %).
#   - départ en mai 2008 : l'ancien règlement, pas de surcote, 75 % ;
#   - départ en novembre 2008 : juillet, août, septembre et octobre 2008
#     après l'âge d'ouverture, 1,33 trimestre arrondi à 2, à 0,75 % :
#     75 % × 1,015 = 76,125 % ;
#   - départ en janvier 2009 : six mois, deux trimestres entiers : 76,125 %.
CAS = {}
for _statut, _regime in [("agent_sncf", "sncf"), ("agent_ratp", "ratp"),
                         ("personnel_opera", "opera_de_paris"),
                         ("personnel_comedie_francaise", "comedie_francaise"),
                         ("clerc_de_notaire", "crpcen")]:
    CAS[f"{_regime}_mai_2008"] = (_statut, _regime, 62 + 4 / 12, 75.0)
    CAS[f"{_regime}_novembre_2008"] = (_statut, _regime, 62 + 10 / 12, 76.125)
    CAS[f"{_regime}_janvier_2009"] = (_statut, _regime, 63.0, 76.125)

TAUX = re.compile(r"× taux ([0-9]+[.,][0-9]+) ?%")


@pytest.fixture(scope="module")
def taux() -> dict[str, float]:
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne se fait pas tourner ici")
    from outils_pont import droit_et_fige

    appels = {
        cle: ("scenario_actuel.calculer", pont.MOTEUR, pont.CarriereSimple({
            "annee_naissance": 1946, "mois_naissance": 1, "jour_naissance": 1,
            "sexe": "H", "affiliation": statut, "age_debut": 18,
            "age_liquidation": depart, "niveau_salaire": 1.0}))
        for cle, (statut, _, depart, _) in CAS.items()
    }
    lus, refus = droit_et_fige(appels)
    assert refus == {}
    resultat = {}
    for cle, (_, regime, *_) in CAS.items():
        pension = next(p for p in lus[cle]["pensions_par_regime"] if p["regime"] == regime)
        resultat[cle] = float(TAUX.search(pension["detail"]).group(1).replace(",", "."))
    return resultat


@pytest.mark.parametrize("cle", CAS)
def test_la_reforme_de_2008_liquide_depuis_le_1er_juillet_2008(taux, cle):
    assert taux[cle] == pytest.approx(CAS[cle][-1], abs=5e-4 + 1e-9)
