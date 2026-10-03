"""La pension du régime des cultes en deux fractions : celle des périodes
d'avant 1998 aux règles du 31 décembre 1997 — le maximum de l'année au
prorata de la durée, les années d'avant 1979 validées gratuitement —,
adaptées par le décret n° 2006-1325 ; celle des périodes suivantes aux règles
du régime général. La règle est dans `droit/cultes.py`, la fiche dans
`regles/cultes_fractions_de_pension.yaml` ; le balayage des deux statuts et
les témoins `cultes_*` confrontent les deux moteurs."""

from __future__ import annotations

import re

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.config import PartCotisation
from retraite_notionnelle.droit import cultes
from retraite_notionnelle.droit import releve as _releve
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.simulateur import Simulateur

FRANCS_PAR_EURO = 6.55957


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(Parametres())


def _carriere(simulateur, naissance, debut, depart, affiliation="ministre_du_culte",
              mois_naissance=1):
    return simulateur.carriere_simple(
        annee_naissance=naissance, sexe="H", affiliation=affiliation,
        mois_naissance=mois_naissance, age_debut=debut, age_liquidation=depart,
        niveau_salaire=1.0, profil_carriere="plat")


def _cavimac(resultat):
    return next(p for p in resultat.pensions_par_regime if p.regime == "cavimac")


def _euros(texte: str) -> float:
    return float(texte.replace(",", ""))


def _fractions(detail: str) -> tuple[float, float]:
    """Les deux montants que le détail écrit : la fraction d'après 1997, puis
    celle d'avant 1998."""
    apres = re.search(r"= ([\d,]+\.\d\d) € ; avant 1998", detail)
    avant = re.search(r"avant 1998, .*? = ([\d,]+\.\d\d) €", detail)
    return _euros(apres.group(1)), _euros(avant.group(1))


def test_le_maximum_suit_les_arretes_puis_les_pensions(simulateur):
    """Les arrêtés jusqu'en 1997, les coefficients des pensions ensuite :
    3 839,26 € par an en 2002 selon la réponse ministérielle du 24 mars 2003
    (question n° 11394), 452,15 € par mois au 1er janvier 2026 selon la caisse.
    La caisse arrondit à chaque revalorisation : le calcul s'en écarte de
    quelques centimes, et l'ancre de 2026 le remplace."""
    maximum = simulateur.scenario_actuel.maximum_des_cultes
    assert maximum.valeur(1978) is None
    # Le fichier garde six décimales.
    assert maximum.valeur(1979)[0] == pytest.approx(7500 / FRANCS_PAR_EURO, abs=1e-6)
    assert maximum.valeur(1990)[0] == pytest.approx(19650 / FRANCS_PAR_EURO, abs=1e-6)
    assert maximum.valeur(1997)[0] == pytest.approx(23449 / FRANCS_PAR_EURO, abs=1e-6)
    assert maximum.valeur(2002)[0] == pytest.approx(3839.26, abs=0.02)
    assert maximum.valeur(2025)[0] * 1.009 / 12 == pytest.approx(452.15, abs=0.03)
    assert maximum.valeur(2026)[0] == pytest.approx(452.15 * 12, abs=1e-9)
    assert maximum.valeur(2030)[0] == pytest.approx(
        452.15 * 12 * simulateur.macro.coefficient_prix(2026, 2030), rel=1e-12)


def test_la_part_de_l_ecart_monte_avec_la_generation():
    """Le V du décret n° 2006-1325 : rien avant 1939, 20 % de l'écart né en
    1939, autant de plus chaque année, l'écart entier depuis 1943."""
    assert [cultes.part_de_l_ecart(n) for n in range(1937, 1945)] == [
        0.0, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.0]


def test_les_annees_d_avant_1979_sont_validees_sans_cotisation(simulateur):
    """D. 721-11 du code de 1985 : l'activité cultuelle d'avant 1979 compte
    pour la pension, sans avoir porté de cotisation. Elle entre dans la durée
    de la CAVIMAC, jamais parmi les trimestres cotisés, et le compte notionnel
    n'en porte rien. Les services passés calédoniens, eux, s'ajoutent à une
    année cotisée à la CAFAT."""
    affiliations = simulateur.affiliations
    assert affiliations.regimes("ministre_du_culte", 1970) == ("cavimac",)
    assert affiliations.validee_sans_cotisation("ministre_du_culte", 1970)
    assert affiliations.validee_sans_cotisation("membre_congregation", 1978)
    assert not affiliations.validee_sans_cotisation("ministre_du_culte", 1979)
    assert not affiliations.validee_sans_cotisation("salarie_nouvelle_caledonie", 1970)

    # Né en 1940, ministre de vingt à soixante-dix ans.
    carriere = _carriere(simulateur, 1940, 20, 70)
    releve = _releve.construire(simulateur.scenario_actuel, carriere)
    assurance = releve.durees.par_annee["assurance"]["cavimac"]
    cotises = releve.durees.par_annee["cotises"]["cavimac"]
    assert assurance[1970] == 4 and 1970 not in cotises
    assert assurance[1985] == 4 and cotises[1985] == 4
    duree = cultes.durees(releve.durees, ("cavimac",), enfants=True)
    assert (duree.avant_1979, duree.de_1979_a_1997, duree.cotises_de_1979_a_1997) == (
        76, 76, 76)
    lignes = {ligne["id"]: ligne for ligne in releve.lignes()}
    assert not lignes["assurance_cavimac_1970"]["contributive"]
    assert lignes["assurance_cavimac_1985"]["contributive"]

    constructeur = ConstructeurCompte(
        simulateur.macro, simulateur.catalogue, simulateur.affiliations,
        simulateur.indexation, simulateur.parametres.avec(part_cotisation=PartCotisation.TOTALE))
    assert constructeur.cotisation_annuelle(carriere, 1970).regimes == ()
    assert constructeur.cotisation_annuelle(carriere, 1985).regimes == ("cavimac",)


def test_avant_1998_la_pension_est_le_maximum_au_prorata_a_soixante_cinq_ans(simulateur):
    """D. 721-6 et D. 721-7 du code de 1985 : à soixante-cinq ans, le maximum
    de l'année au prorata de cent cinquante trimestres, et aucun minimum
    contributif. Né en 1925, ministre depuis ses trente-cinq ans : 76
    trimestres d'avant 1979 et 44 de 1979 à 1989, liquidés en 1990."""
    resultat = simulateur.scenario_actuel.calculer(_carriere(simulateur, 1925, 35, 65))
    pension = _cavimac(resultat)
    maximum = simulateur.scenario_actuel.maximum_des_cultes.valeur(1990)[0]
    assert maximum == pytest.approx(19650 / FRANCS_PAR_EURO, abs=1e-6)
    assert pension.montant == pytest.approx(maximum * 120 / 150, abs=1e-9)
    assert pension.detail == (f"avant 1998, maximum {maximum:,.2f} € × 120/150 "
                              f"= {pension.montant:,.2f} €")
    assert not any(a.code == "minimum_contributif" for a in resultat.avantages_appliques)
    # À soixante-quatre ans, le régime n'ouvre rien.
    assert simulateur.scenario_actuel.calculer(
        _carriere(simulateur, 1925, 35, 64)).motif_ouverture == "non_ouverte"


def test_au_taux_plein_la_fraction_est_portee_au_minimum_contributif(simulateur):
    """Décret n° 2006-1325, art. 2, III à V bis. Né en 1950, ministre de vingt
    à soixante-quatre ans : 36 trimestres d'avant 1979, 76 cotisés de 1979 à
    1997. Au taux plein et surcoté en 2014, la fraction d'avant 1998 est le
    maximum au prorata, surcoté, porté au minimum contributif majoré pour les
    trimestres cotisés et au minimum contributif pour les autres."""
    moteur = simulateur.scenario_actuel
    pension = _cavimac(moteur.calculer(_carriere(simulateur, 1950, 20, 64)))
    trouve = re.search(r"avant 1998, maximum [\d,.]+ € × 112/(\d+) × surcote ([\d.]+) ",
                       pension.detail)
    assert trouve, pension.detail
    duree, surcote = int(trouve.group(1)), float(trouve.group(2))
    maximum = moteur.maximum_des_cultes.valeur(2014)[0]
    base, majore, _, _ = moteur.minimum_contributif.valeurs(2014)
    attendu = (maximum * 112 / duree * surcote + (majore - maximum) * 76 / duree
               + (base - maximum) * 36 / duree)
    assert _fractions(pension.detail)[1] == pytest.approx(attendu, abs=0.01)
    assert "76 trimestres cotisés de 1979 à 1997 (minimum contributif majoré)" in pension.detail
    assert "36 trimestres d'avant 1979 (minimum contributif)" in pension.detail


def test_les_annees_d_avant_1979_attendent_fevrier_2010(simulateur):
    """Le V bis ne vaut que pour les pensions prenant effet à compter du
    1er février 2010 (décret n° 2010-103). Né le 1er décembre 1949, ministre
    depuis ses dix-huit ans, parti à soixante ans — sa pension prend effet le
    1er janvier 2010 —, puis un mois plus tard."""
    moteur = simulateur.scenario_actuel
    janvier = _cavimac(moteur.calculer(
        _carriere(simulateur, 1949, 18, 60, mois_naissance=12)))
    fevrier = _cavimac(moteur.calculer(
        _carriere(simulateur, 1949, 18, 60 + 1 / 12, mois_naissance=12)))
    assert "trimestres d'avant 1979" not in janvier.detail
    assert "trimestres d'avant 1979 (minimum contributif)" in fevrier.detail
    assert fevrier.montant > janvier.montant


def test_a_taux_minore_la_fraction_reste_au_maximum_et_se_decote(simulateur):
    """« à taux minoré, les fractions de pension avant 1979 et de 1979 à 1997
    seront portées au niveau du montant maximum de la pension « Cavimac » et
    vous aurez de plus une décote ». Née en 1955, religieuse de trente à
    soixante-deux ans : 52 trimestres avant 1998, 128 en tout quand 166 sont
    requis — vingt trimestres de décote, jusqu'à soixante-sept ans."""
    moteur = simulateur.scenario_actuel
    pension = _cavimac(moteur.calculer(
        _carriere(simulateur, 1955, 30, 62, affiliation="membre_congregation")))
    maximum = moteur.maximum_des_cultes.valeur(2017)[0]
    assert f"avant 1998, maximum {maximum:,.2f} € × 52/166 × décote 0.7500 = " in pension.detail
    assert _fractions(pension.detail)[1] == pytest.approx(
        maximum * 52 / 166 * 0.75, abs=0.01)
    assert "minimum contributif" not in pension.detail


def test_le_minimum_contributif_ne_releve_que_la_fraction_d_apres_1997(simulateur):
    """L. 351-10 ne vaut que pour la fraction des règles du régime général : le
    minimum se compare à elle, au prorata de sa durée, et la fraction d'avant
    1998, qui a ses propres majorations, n'en comble pas l'écart. Né en 1975,
    ministre de vingt et un ans à soixante-quatre : 8 trimestres avant 1998, au
    taux plein en 2039."""
    moteur = simulateur.scenario_actuel
    resultat = moteur.calculer(_carriere(simulateur, 1975, 21, 64))
    pension = _cavimac(resultat)
    apres, avant = _fractions(pension.detail)
    trouve = re.search(r"× taux [\d.]+% × (\d+)/(\d+) =", pension.detail)
    depuis_1998, duree = int(trouve.group(1)), int(trouve.group(2))
    base, majore, _, _ = moteur.minimum_contributif.valeurs(2039)
    plancher = majore * depuis_1998 / duree
    assert apres < plancher
    assert pension.montant == pytest.approx(avant + plancher, abs=0.02)
