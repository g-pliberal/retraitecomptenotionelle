"""La durée des services des régimes spéciaux, additionnée puis arrondie une fois.

Les règlements écrivent tous la même règle depuis leur réforme : la durée des
services « s'exprime en trimestres. Dans le décompte final des trimestres
liquidables, la fraction de trimestre égale ou supérieure à quarante-cinq
jours est comptée pour un trimestre. La fraction de trimestre inférieure à
quarante-cinq jours est négligée » — SNCF (décret n° 2008-639, article 12),
RATP (n° 2008-637, article 23), IEG (annexe 3 du statut, article 9), CRPCEN
(n° 90-1215, article 85, I), Opéra (n° 68-382, article 14, I),
Comédie-Française (n° 68-960, article 12, I), Banque de France (n° 2007-262,
annexe, article 31, II). Lu dans l'index LEGI le 21 novembre 2026. La durée
d'assurance que la décote lit « totalise la durée des services » (le III de
chaque article), et le nombre de trimestres qui lui manquent « est arrondi à
l'entier supérieur ».

Le modèle comptait les trimestres civils entiers de l'année d'entrée et de
celle du départ, chacune à part : les fractions des deux années se perdaient
au lieu de s'additionner. Chaque cas est posé à la main depuis ces textes :
l'agent né le 1er du mois entre au mois de son anniversaire et part au
premier du mois qui suit l'âge demandé ; ses services courent de son entrée
au dernier jour du mois qui précède ce départ, à trente jours le mois.
"""

from __future__ import annotations

import re
import shutil

import pytest

from retraite_notionnelle import pont

#: Le cas : le statut, le régime, l'année et le mois de naissance, l'âge au
#: premier emploi, l'âge du départ demandé ; puis les trimestres liquidés que
#: le texte compte, la durée requise, et le taux de la pension en pour cent.
CAS = {
    # Né le 1er février 1975, entré à 30 ans, parti à 62 ans et 9 mois :
    # 394 mois de services (onze en 2005, trente et une années, onze en 2037),
    # 131 trimestres et un mois, soit 131 (trente jours, sous quarante-cinq).
    # Le modèle en comptait 130 (3 + 124 + 3). Sédentaire, âge de référence
    # atteint : pas de décote.
    "sncf_fevrier": ("agent_sncf", "sncf", 1975, 2, 30, 62.75, 131, 170, 75.0),
    "ratp_fevrier": ("agent_ratp", "ratp", 1975, 2, 30, 62.75, 131, 170, 75.0),
    "ieg_fevrier": ("agent_ieg", "ieg", 1975, 2, 30, 62.75, 131, 172, 75.0),
    # Le même, né en janvier : 394 mois aussi, le modèle comptait déjà 131.
    "sncf_janvier": ("agent_sncf", "sncf", 1975, 1, 30, 62.75, 131, 170, 75.0),
    # Clerc de notaire né en février 1975, entré à 22 ans, parti à 62 ans et
    # 9 mois : 490 mois, 163 trimestres et un mois, liquidés à 163 ; la durée
    # d'assurance, 163,33 trimestres, en laisse manquer 8,67 sur 172, arrondis à
    # 9 ; l'âge de référence, 67 ans, en laisse 17 : 9 trimestres de décote à
    # 1,25 %, taux 75 % × (1 − 0,1125) = 66,5625 %. Le modèle : 162 et 10.
    "crpcen_fevrier": ("clerc_de_notaire", "crpcen", 1975, 2, 22, 62.75, 163, 172, 66.5625),
    "comedie_francaise_fevrier": ("personnel_comedie_francaise", "comedie_francaise",
                                  1975, 2, 22, 62.75, 163, 172, 66.5625),
    # Agent de la Banque de France, mêmes dates qu'à la SNCF : 131 sur 172.
    "banque_de_france_fevrier": ("agent_banque_de_france", "banque_de_france",
                                 1975, 2, 30, 62.75, 131, 172, None),
    # Artiste de l'Opéra né en février 1954, entré à 18 ans, parti à 63 ans et
    # 9 mois : 549 mois, 183 trimestres, liquidés au maximum, 150 sur 150. La
    # surcote compte les trimestres entiers au-delà des 150 requis : 33, au lieu
    # des 32 que les années civiles laissaient, à 1,25 % chacun : 75 % × 1,4125,
    # soit 105,9375 %, au lieu de 105 %.
    "opera_fevrier": ("personnel_opera", "opera_de_paris", 1954, 2, 18, 63.75,
                      150, 150, 105.9375),
}

#: Le taux plein des régimes : 75 % du traitement.
#: Le détail de la pension : « × taux 66.562% × 163/172 ».
DETAIL = re.compile(r"× taux ([0-9]+[.,][0-9]+) ?% × ([0-9]+)/([0-9]+)")


@pytest.fixture(scope="module")
def details() -> dict[str, tuple[float, int, int]]:
    """Le taux, les trimestres liquidés et la durée requise que le portage
    écrit au détail de la pension de chaque cas."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne se fait pas tourner ici")
    from outils_pont import droit_et_fige

    appels = {
        cle: ("scenario_actuel.calculer", pont.MOTEUR, pont.CarriereSimple({
            "annee_naissance": annee, "mois_naissance": mois, "jour_naissance": 1,
            "sexe": "H", "affiliation": statut, "age_debut": debut,
            "age_liquidation": depart, "niveau_salaire": 1.0}))
        for cle, (statut, _, annee, mois, debut, depart, *_) in CAS.items()
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
def test_la_duree_des_services_s_additionne_puis_s_arrondit_une_fois(details, cle):
    """Les trimestres liquidés sont ceux du total des services, la fraction
    de quarante-cinq jours et plus comptée pour un trimestre."""
    *_, liquides, requis, _ = CAS[cle]
    assert details[cle][1:] == (liquides, requis)


@pytest.mark.parametrize("cle", [cle for cle, cas in CAS.items() if cas[-1] is not None])
def test_la_decote_lit_la_duree_des_services_et_non_les_annees_civiles(details, cle):
    """Le taux, décote comprise, que la durée totale des services laisse."""
    assert details[cle][0] == pytest.approx(CAS[cle][-1], abs=5e-4 + 1e-9)
