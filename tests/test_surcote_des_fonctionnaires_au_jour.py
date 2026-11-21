"""La surcote du fonctionnaire court du jour où sa durée d'assurance,
comptée au jour, atteint la durée requise, et non du trimestre civil où les
années civiles l'y portent.

Code des pensions civiles et militaires, L. 14, III : la surcote compte les
trimestres entiers « effectués après le 1er janvier 2004, au-delà de l'âge
[d'ouverture] et en sus du nombre de trimestres nécessaire pour obtenir le
pourcentage maximum » ; cette durée se compte au jour (L. 14, I), que le
Service des retraites de l'État dit « calculée en trimestres et jours sans
règle d'arrondi ».
"""

from __future__ import annotations

import shutil

import pytest

from retraite_notionnelle import pont

pytestmark = pytest.mark.rapide

# Née le 1er janvier 1964, 170 trimestres requis, l'âge légal atteint en
# octobre 2026. Clé : (affiliation, mois d'entrée après janvier 1984, mois de
# départ après janvier 2027, taux attendu en %).
#   - entrée le 1er septembre 1984, départ le 1er juin 2027 : 510 mois, la
#     durée requise, au 1er mars 2027 ; de mars à mai, un trimestre entier :
#     75 % × 1,0125 = 75,9375 %. Les années civiles (un trimestre en 1984,
#     169 à la fin de 2026) la plaçaient au 1er avril, et ne laissaient que
#     deux mois ;
#   - entrée le 1er août 1984, même départ : la durée requise au 1er février
#     2027, quatre mois après, un trimestre : 75,9375 % ;
#   - entrée en septembre, départ le 1er mai 2027 : deux mois, rien ; 75 % ;
#   - entrée en septembre, départ le 1er juillet 2027 : quatre mois, un
#     trimestre ; 75,9375 %, que les années civiles donnaient déjà.
CAS = {}
for _affiliation in ("fonctionnaire_etat", "fonctionnaire_territorial_hospitalier"):
    CAS[f"{_affiliation}_septembre_juin"] = (_affiliation, 8, 5, 75.9375)
    CAS[f"{_affiliation}_aout_juin"] = (_affiliation, 7, 5, 75.9375)
    CAS[f"{_affiliation}_septembre_mai"] = (_affiliation, 8, 4, 75.0)
    CAS[f"{_affiliation}_septembre_juillet"] = (_affiliation, 8, 6, 75.9375)


@pytest.fixture(scope="module")
def taux() -> dict[str, float]:
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne se fait pas tourner ici")
    from outils_pont import droit_et_fige

    appels = {
        cle: ("scenario_actuel.calculer", pont.MOTEUR, pont.CarriereSimple({
            "annee_naissance": 1964, "mois_naissance": 1, "jour_naissance": 1,
            "sexe": "F", "affiliation": affiliation, "age_debut": 20 + entree / 12,
            "age_liquidation": 63 + depart / 12, "niveau_salaire": 1.0}))
        for cle, (affiliation, entree, depart, _) in CAS.items()
    }
    lus, refus = droit_et_fige(appels)
    assert refus == {}
    return {cle: 100 * lus[cle]["taux_liquidation"] for cle in CAS}


@pytest.mark.parametrize("cle", CAS)
def test_la_surcote_court_du_jour_ou_la_duree_requise_est_atteinte(taux, cle):
    assert taux[cle] == pytest.approx(CAS[cle][-1], abs=1e-9)
