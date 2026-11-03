"""Le taux et la limite de la surcote des régimes spéciaux réformés en 2008.

Les six décrets — SNCF (n° 2008-639, article 13, II), RATP (n° 2008-637,
article 24, II), IEG (annexe 3 du statut, article 10, II), CRPCEN
(n° 90-1215, article 85-1, II), Comédie-Française (n° 68-960, article 12,
III), Opéra (n° 68-382, article 14, III) — écrivent la même phrase : « Le
taux du coefficient de majoration est égal, par trimestre supplémentaire
dans la limite de vingt trimestres, à celui prévu pour les fonctionnaires de
l'Etat en application du III de l'article L. 14 du code des pensions civiles
et militaires de retraite ». Lu dans l'index LEGI le 3 novembre 2026 :

- le taux de L. 14, III, est de 0,75 % jusqu'au 18 décembre 2008, puis de
  1,25 % ; mais la loi n° 2008-1330 (article 89, III) n'applique le 1,25 %
  qu'« aux trimestres d'assurance cotisés et effectués à compter du
  1er janvier 2009 » : ceux du second semestre de 2008 gardent 0,75 % ;
- la limite de vingt trimestres tombe à la CRPCEN le 19 septembre 2011, à la
  Comédie-Française le 23 septembre 2011, à la SNCF, à la RATP, aux IEG et
  à l'Opéra le 1er janvier 2017.

Le modèle servait 0,75 % à tout trimestre de la SNCF de 2009 à 2017, 1,25 %
à ceux de 2008 des cinq autres, et aucune limite. Chaque cas est posé à la
main depuis ces textes : le nombre de trimestres de surcote à 0,75 % et à
1,25 %, d'où le coefficient que la pension doit porter ; le portage le
calcule, et son jumeau Python le refait au bit près (``droit_et_refait``).
"""

from __future__ import annotations

import re
import shutil

import pytest

from retraite_notionnelle import pont

#: Le cas : le statut, le régime, l'année et le mois de naissance (le 1er du
#: mois), l'âge au premier emploi, l'âge du départ demandé ; puis les
#: trimestres de surcote que le texte compte à 0,75 % et à 1,25 %.
CAS = {
    # Né en janvier 1951, l'agent de conduite part à sa limite d'âge, en
    # janvier 2016 : vingt trimestres depuis ses soixante ans, en janvier
    # 2011, tous au taux de 2009. Le modèle servait 0,75 % (1,15).
    "sncf_1951": ("agent_sncf", "sncf", 1951, 1, 20, 65.0, 0, 20),
    # Né en juillet 1948, sa limite d'âge l'arrête en juillet 2013 : vingt
    # trimestres depuis juillet 2008, dont deux en 2008. Le modèle : 1,15.
    "sncf_1948": ("agent_sncf", "sncf", 1948, 7, 20, 68.0, 2, 18),
    # Nés en janvier 1945, partis à soixante-quatre ans en janvier 2009 :
    # les deux trimestres du second semestre de 2008, à 0,75 %. Le modèle
    # servait 1,25 % à la RATP et à la CRPCEN.
    "sncf_1945": ("agent_sncf", "sncf", 1945, 1, 21, 64.0, 2, 0),
    "ratp_1945": ("agent_ratp", "ratp", 1945, 1, 21, 64.0, 2, 0),
    "crpcen_1945": ("clerc_de_notaire", "crpcen", 1945, 1, 21, 64.0, 2, 0),
    # Né en janvier 1951, le roulant part en janvier 2016 : vingt trimestres
    # depuis ses soixante ans, au taux de 2009, comme le modèle le servait.
    "ratp_1951": ("agent_ratp", "ratp", 1951, 1, 20, 65.0, 0, 20),
    # Né en janvier 1950, l'agent de l'Opéra part en janvier 2016 :
    # vingt-six trimestres au-delà de la durée requise, tous de 2009 et
    # après ; la limite de vingt les arrête. Le modèle : 1,325.
    "opera_1950": ("personnel_opera", "opera_de_paris", 1950, 1, 20, 66.0, 0, 20),
    # Né en janvier 1946, le sociétaire part en janvier 2016 : trente
    # trimestres depuis juillet 2008, dont deux en 2008, et plus de limite
    # depuis septembre 2011. Le modèle : 1,375.
    "comedie_francaise_1946": ("personnel_comedie_francaise", "comedie_francaise",
                               1946, 1, 18, 70.0, 2, 28),
}


#: Le taux plein des six régimes : 75 % du traitement.
TAUX_PLEIN = 75.0
#: Le taux de la pension, que son détail écrit au millième.
TAUX_DU_DETAIL = re.compile(r"× taux ([0-9]+[.,][0-9]+) ?%")


@pytest.fixture(scope="module")
def taux() -> dict[str, float]:
    """Le taux de la pension du régime, en pour cent, sous la clé de chaque
    cas : le portage le calcule, son jumeau le refait au bit près. Le pont
    n'en rend que le détail, qui l'écrit au millième."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage ne se fait pas tourner ici")
    from outils_pont import droit_et_refait

    appels = {
        cle: ("scenario_actuel.calculer", pont.MOTEUR, pont.CarriereSimple({
            "annee_naissance": annee, "mois_naissance": mois, "jour_naissance": 1,
            "sexe": "H", "affiliation": statut, "age_debut": debut,
            "age_liquidation": depart, "niveau_salaire": 1.0}))
        for cle, (statut, _, annee, mois, debut, depart, _, _) in CAS.items()
    }
    lus, refus = droit_et_refait(appels)
    assert refus == {}
    resultat = {}
    for cle, (_, regime, *_) in CAS.items():
        pension = next(p for p in lus[cle]["pensions_par_regime"] if p["regime"] == regime)
        resultat[cle] = float(TAUX_DU_DETAIL.search(pension["detail"]).group(1).replace(",", "."))
    return resultat


@pytest.mark.parametrize("cle", CAS)
def test_chaque_trimestre_de_surcote_a_le_taux_de_sa_date_dans_la_limite_du_decret(
        taux, cle):
    """0,75 % pour un trimestre de 2008, 1,25 % pour un trimestre de 2009 et
    après, et vingt trimestres au plus là où le décret en vigueur à la date
    d'effet de la pension l'écrit : le taux plein, majoré du coefficient."""
    *_, a_0_75, a_1_25 = CAS[cle]
    assert taux[cle] == pytest.approx(TAUX_PLEIN * (1.0 + 0.0075 * a_0_75 + 0.0125 * a_1_25),
                                      abs=5e-4)
