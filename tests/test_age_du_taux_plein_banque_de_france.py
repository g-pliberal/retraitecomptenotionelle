"""L'âge du taux plein de la Banque de France est celui de son règlement, non
celui du régime général (action 191, note 0009, étape 4 : le renvoi de la
Banque de France à l'âge du taux plein, « laissé : à corriger »).

Le règlement annexé au décret n° 2007-262 ne connaît qu'un âge où la pension
cesse d'être minorée : « l'âge auquel s'annule le coefficient de minoration »,
la limite d'âge du grade (article 32, 1°), que l'article 70 abaisse à titre
transitoire, d'abord par période où l'agent « est susceptible de liquider sa
pension » (rédaction d'origine, LEGIARTI000006778516), puis par période de
naissance, la limite d'âge diminuée de trimestres (rédaction du décret
n° 2012-701, LEGIARTI000025882187 ; celle du 1er janvier 2025,
LEGIARTI000047909725, au mot près pour les nés depuis 1956). Aucune de ses
rédactions ne renvoie à l'article L. 351-8 du code de la sécurité sociale :
le dépôt y renvoyait pourtant de 2008 à aujourd'hui
(`age_taux_plein_par_generation: age_annulation_decote`), et la décote seule,
depuis le 19 novembre 2026, lisait l'article 70. Le départ « au taux plein »
et le « taux plein automatique » que le site propose lisaient l'âge du régime
général : 65 ans et 4 mois à l'agent né en juillet 1951, pour 62 ans et un
trimestre au règlement.

« Jusqu'au 31 décembre 2008 » et « jusqu'au 2e semestre 1948 », le tableau
écrit « Sans objet » : aucune minoration, la pension est entière dès l'âge
d'ouverture, comme aux régimes sans décote, dont la fiche écrit l'âge du taux
plein égal à l'âge d'ouverture (État et CNRACL avant 2004, SNCF, RATP et IEG
avant 2008).

La fin de l'indemnisation du chômage, elle, n'est pas un âge du règlement :
l'article L. 5421-4 du code du travail nomme l'âge du 1° de L. 351-8 du code
de la sécurité sociale. Elle garde celui du régime général.

Les valeurs attendues sont lues dans les tableaux de l'article 70 et posées à
la main.
"""

from __future__ import annotations

import pytest

from facade import Simulateur, ouvrir


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _agent(simulateur: Simulateur, naissance: int, mois: int, depart: float):
    return simulateur.carriere_simple(
        annee_naissance=naissance, mois_naissance=mois, sexe="H",
        affiliation="agent_banque_de_france", age_debut=28, age_liquidation=depart)


@pytest.mark.parametrize("naissance, mois, depart, attendu", [
    # Rédaction de 2007, la pension de 2007 : « Jusqu'au 31 décembre 2008.
    # Sans objet » ; soixante ans en mai 2007, l'âge d'ouverture.
    (1947, 5, 60, 60.0),
    # La même ligne, une pension de 2008.
    (1948, 1, 60, 60.0),
    # « Du 1er janvier 2009 au 30 juin 2009. 0,125 % 61 ans ».
    (1949, 1, 60, 61.0),
    # « Du 1er juillet 2011 au 31 décembre 2011. 0,375 % 62 ans et 1 trimestre » :
    # l'agent né en juillet 1951, que le dépôt datait à 65 ans et 4 mois.
    (1951, 7, 60, 62.25),
    # Rédaction de 2012 : « 1er semestre 1958 1,250 % Lim. âge - 5 trimestres »,
    # la limite d'âge de 66 ans et 3 mois (statut, article 241), soit 65 ans.
    (1958, 1, 62, 65.0),
    # Rédaction de 2025 : « 1er semestre 1962 1,250 % Lim. âge - 1 trimestre »,
    # 67 ans moins un trimestre.
    (1962, 1, 63, 66.75),
])
def test_l_age_du_taux_plein_est_celui_de_l_article_70(
        simulateur, naissance, mois, depart, attendu):
    carriere = _agent(simulateur, naissance, mois, depart)
    periode = simulateur.catalogue["banque_de_france"].periode(carriere.annee_liquidation)
    assert ouvrir.age_taux_plein(simulateur.scenario_actuel, periode, carriere) == pytest.approx(
        attendu)


def test_le_depart_au_taux_plein_et_le_taux_plein_automatique_lisent_le_reglement(simulateur):
    """Né en juillet 1951, entré à vingt-huit ans : à soixante ans, en juillet
    2011, 128 trimestres, loin de la durée ; la pension cesse d'être minorée à
    62 ans et un trimestre (article 70), non à 65 ans et 4 mois (L. 351-8)."""
    carriere = _agent(simulateur, 1951, 7, 60)
    moteur = simulateur.scenario_actuel
    assert ouvrir.age_annulation_droit(moteur, carriere) == pytest.approx(62.25)
    assert ouvrir.age_taux_plein_droit(moteur, carriere) == pytest.approx(62.25)


def test_la_fin_du_chomage_garde_l_age_du_code_du_travail(simulateur):
    """L. 5421-4, 1° du code du travail : l'âge du 1° de L. 351-8 du code de la
    sécurité sociale, 65 ans et 4 mois pour un assuré né en juillet 1951
    (loi n° 2010-1330, article 20, et LFSS pour 2012, article 88), atteint en
    novembre 2016 ; né après le premier du mois (le jour que la chronologie
    présume), il ne l'a au premier jour d'un mois qu'en décembre 2016, le
    premier mois que la règle coupe. Le règlement de la Banque de France n'y
    change rien."""
    carriere = _agent(simulateur, 1951, 7, 60)
    fin = ouvrir.fin_indemnisation(simulateur.scenario_actuel, carriere)
    assert (fin.annee, fin.mois) == (2016, 12)
