"""Ce que les règlements des sections de santé servent, lus au texte.

La passe du 23 septembre 2026 sur les professions de santé (action 89) a lu au
Journal officiel les statuts et les règlements de la CARMF, de la CARCDSF, de
la CAVP, de la CARPIMKO et de la CARPV, du plus ancien que l'index porte en
entier au règlement que l'arrêté du 10 juillet 2026 approuve. Ce fichier tient
ce qu'elle a corrigé.

**Trois de ces cinq complémentaires minorent par l'âge seul.** La CARCDSF, la
CAVP et la CARPV comptent les trimestres — ou les années — qui séparent de
l'âge de leur taux plein, et la durée d'assurance n'y change rien. Les fiches
leur opposaient la décote du régime de base, que la durée annule : un
dentiste, un pharmacien ou un vétérinaire parti à soixante-quatre ans avec sa
durée ne perdait rien de sa complémentaire, quand sa caisse lui en retire 15,
9 ou 5 %. Deux fiches croyaient le dire en laissant leur durée requise vide ;
le moteur lisait celle de la carrière.

**Les taux sont les leurs, et ont bougé.** La CARCDSF minore de 5 % par année
jusqu'en 2010, de 1,50 % par trimestre les nés depuis 1955 de 2011 à 2023, de
1,25 % depuis dans la limite de 15 %. La CAVP compte deux pentes depuis 2011 :
1,25 % par trimestre jusqu'à 65 ans, 0,5 % de 65 ans à l'âge du taux plein. La
CARMF, de 2000 à 2016, comptait des années d'âge.

**Les mères de la CARCDSF partent plus tôt au taux plein** — une année par
enfant, cinq au plus —, et la voie est exclusive de la minoration : l'âge
dont celle-ci se compte ne bouge pas.

**La CARPIMKO a ses âges** depuis 2015 : taux plein à 65 ans pour les
générations 1955 et antérieures, quatre mois de plus par génération jusqu'à
67 ans en 1961.

**Trois enfants majorent de 10 % les cinq complémentaires** — la CARMF depuis
1964, l'ASV depuis 1981, la CARCDSF et la CAVP depuis leurs premiers statuts
lus, la CARPV depuis 2022, la CARPIMKO depuis 2024. Aucune fiche ne la
portait.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.droit import ouvrir


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int,
              liquidation: float, debut: float = 21.0, sexe: str = "H",
              enfants: int = 0):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance,
        sexe=sexe,
        metiers=[Metier(affiliation=affiliation, age_debut=debut,
                        niveau_salaire=1.0)],
        age_liquidation=liquidation,
        macro=simulateur.macro,
        nombre_enfants=enfants,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return resultat, {p.regime: p for p in resultat.pensions_par_regime}


def _coefficient(detail: str) -> float:
    """Le coefficient écrit dans le détail d'une pension en points, 1 sans."""
    for marque in ("coefficient d'anticipation ", "coefficient de majoration "):
        if marque in detail:
            return float(detail.split(marque)[1].split()[0])
    return 1.0


# -- la CARCDSF ----------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # 2008-2010, statuts de 2007 : 5 % par année d'âge jusqu'à 65 ans, l'année
    # entamée comptant entière — 63 ans et 3 mois laissent deux années.
    (1945, 64.0, 0.95),
    (1945, 63.25, 0.90),
    # 2011-2023 : 1,50 % par trimestre pour les nés depuis 1955, jusqu'à 67 ans.
    (1955, 64.0, 0.82),
    # Entre les deux, le tableau publié en image : 1,25 % en tient lieu,
    # jusqu'à l'âge légal majoré de cinq ans (66 ans et 2 mois en 1953).
    (1953, 63.0, 0.8375),
    # Depuis 2024 : 1,25 % par trimestre, dans la limite de 15 %.
    (1975, 64.0, 0.85),
    (1965, 63.0, 0.85),
    (1975, 67.0, 1.0),
])
def test_la_carcdsf_minore_par_l_age_seul(simulateur, naissance, liquidation,
                                         coefficient):
    """Carrière commencée à 21 ans : la durée est réunie partout, et c'est
    précisément le cas où la fiche ne minorait rien."""
    resultat, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                                   naissance, liquidation)
    assert resultat.liquidation_ouverte
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(
        coefficient)


@pytest.mark.parametrize("naissance,liquidation,enfants,coefficient", [
    # « Si vous avez eu 2 enfants, vous pouvez bénéficier du taux plein pour ce
    # régime dès 65 ans » — la page de la caisse, lue le 23 septembre 2026.
    (1960, 65.0, 2, 1.0),
    # Trois mois plus tôt, la voie particulière est fermée, et la minoration se
    # compte depuis 67 ans : neuf trimestres, 11,25 %.
    (1960, 64.75, 2, 0.8875),
    # Cinq années au plus : sept enfants n'avancent pas davantage que cinq.
    (1960, 62.0, 7, 1.0),
    # Les statuts de 2007 l'écrivaient déjà : « à partir de 63 ans pour deux
    # enfants », quand le taux plein était à 65.
    (1945, 63.0, 2, 1.0),
])
def test_la_mere_part_au_taux_plein_une_annee_plus_tot_par_enfant(
        simulateur, naissance, liquidation, enfants, coefficient):
    _, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                            naissance, liquidation, sexe="F", enfants=enfants)
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(
        coefficient)


def test_le_pere_n_a_pas_l_anticipation_des_meres(simulateur):
    """« Aux affiliées […] au titre de l'incidence sur leur vie professionnelle
    de la maternité » : le même dentiste, père de deux enfants, est minoré."""
    _, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                            1960, 65.0, sexe="H", enfants=2)
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(0.90)


def test_la_carcdsf_majore_apres_son_age(simulateur):
    """Huit trimestres civils entiers après 67 ans, 1,25 % chacun depuis 2024.

    Avant 2011 la caisse ne majorait pas ; de 2011 à 2023, 1 % par trimestre.
    """
    _, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                            1957, 69.0)
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(1.10)
    _, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                            1948, 67.0)
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(1.08)
    _, pensions = _calculer(simulateur, "chirurgien_dentiste_ou_sage_femme",
                            1943, 67.0)
    assert _coefficient(pensions["carcdsf_complementaire"].detail) == pytest.approx(1.0)


# -- la CAVP -------------------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    # Deux pentes : quatre trimestres à 1,25 % jusqu'à 65 ans, huit à 0,5 %
    # de 65 à 67 ans.
    (1975, 64.0, 0.91),
    (1975, 66.0, 0.98),
    (1960, 62.0, 0.81),
    # 66 ans pour les générations 1953 à 1955 : quatre et quatre.
    (1954, 64.0, 0.93),
    # Avant 2012, 65 ans pour tous et 1,25 % par trimestre.
    (1945, 64.0, 0.95),
    (1975, 67.0, 1.0),
])
def test_la_cavp_minore_a_deux_pentes(simulateur, naissance, liquidation,
                                      coefficient):
    resultat, pensions = _calculer(simulateur, "pharmacien", naissance, liquidation)
    assert resultat.liquidation_ouverte
    assert _coefficient(pensions["cavp_complementaire"].detail) == pytest.approx(
        coefficient)


# -- la CARPV et la CARMF --------------------------------------------------------


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    (1975, 64.0, 0.95),
    (1945, 64.0, 0.95),
    (1925, 64.0, 0.95),
    (1975, 65.0, 1.0),
])
def test_le_veterinaire_est_minore_jusqu_a_soixante_cinq_ans(
        simulateur, naissance, liquidation, coefficient):
    """« 1,25 % par trimestre manquant avant l'âge de soixante-cinq ans », que
    la durée d'assurance n'annule pas."""
    _, pensions = _calculer(simulateur, "veterinaire", naissance, liquidation)
    assert _coefficient(pensions["carpv_complementaire"].detail) == pytest.approx(
        coefficient)


@pytest.mark.parametrize("naissance,liquidation,coefficient", [
    (1945, 64.0, 0.95),
    # 2012 : deux ans et demi avant 65 ans, trois années, 0,85.
    (1950, 62.5, 0.85),
])
def test_la_carmf_de_2000_a_2016_compte_des_annees_d_age(
        simulateur, naissance, liquidation, coefficient):
    """« 0,75 à 60 ans, 0,80 à 61 ans, 0,85 à 62 ans, 0,90 à 63 ans, 0,95 à
    64 ans » : la durée n'y joue aucun rôle, et la fiche le disait sans que le
    moteur le lise."""
    _, pensions = _calculer(simulateur, "medecin_liberal", naissance, liquidation)
    assert _coefficient(pensions["carmf_complementaire"].detail) == pytest.approx(
        coefficient)


# -- la CARPIMKO -----------------------------------------------------------------


def test_la_carpimko_arrete_sa_minoration_a_son_propre_age(simulateur):
    """Né en 1958, taux plein à 66 ans : la décote d'une carrière commencée à
    30 ans s'arrête à seize trimestres, là où l'âge du régime général en
    comptait vingt."""
    _, pensions = _calculer(simulateur, "auxiliaire_medical", 1958, 62.0, debut=30.0)
    assert _coefficient(pensions["carpimko_complementaire"].detail) == pytest.approx(0.80)


def test_la_carpimko_majore_depuis_son_age(simulateur):
    """Née en 1960, taux plein à 66 ans et 8 mois : un trimestre civil entier
    avant 67 ans, 1,25 %."""
    _, pensions = _calculer(simulateur, "auxiliaire_medical", 1960, 67.0)
    assert _coefficient(pensions["carpimko_complementaire"].detail) == pytest.approx(1.0125)


# -- trois enfants ---------------------------------------------------------------


@pytest.mark.parametrize("statut", [
    "medecin_liberal", "chirurgien_dentiste_ou_sage_femme", "pharmacien",
    "auxiliaire_medical", "veterinaire",
])
def test_trois_enfants_majorent_toute_la_pension_en_2027(simulateur, statut):
    """En 2027, la base (L. 643-1-1) et chaque complémentaire majorent de 10 %."""
    resultat, pensions = _calculer(simulateur, statut, 1960, 67.0, sexe="F",
                                   enfants=3)
    majoration = sum(a.montant for a in resultat.avantages_appliques
                     if a.code == "majoration_enfants")
    assert majoration == pytest.approx(0.10 * sum(p.montant for p in pensions.values()))


def test_trois_enfants_majoraient_deja_les_complementaires_du_medecin(simulateur):
    """En 2010, la base ne majorait pas encore ; la CARMF (1964) et l'ASV
    (1981) le faisaient."""
    resultat, pensions = _calculer(simulateur, "medecin_liberal", 1945, 65.0,
                                   sexe="F", enfants=3)
    majoration = sum(a.montant for a in resultat.avantages_appliques
                     if a.code == "majoration_enfants")
    assert majoration == pytest.approx(0.10 * (pensions["carmf_complementaire"].montant
                                               + pensions["asv_conventionnes"].montant))


# -- l'âge du droit ---------------------------------------------------------------


@pytest.mark.parametrize("statut,naissance,age", [
    ("officier_ministeriel", 1955, 62.0),
    ("auxiliaire_medical", 1955, 62.0),
    ("pharmacien", 1950, 60.0),
])
def test_une_complementaire_qui_a_ses_ages_n_ouvre_pas_le_droit(
        simulateur, statut, naissance, age):
    """La CAVOM et la CARPIMKO s'ouvrent à 60 ans aux générations d'avant
    1956 ; le droit, lui, s'ouvre à l'âge du régime de base. Les règles d'âge
    des cas types proposaient soixante ans que le calcul refusait."""
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, sexe="H", affiliation=statut,
        age_debut=22.0, age_liquidation=64.0)
    actuel = simulateur.scenario_actuel
    assert ouvrir.age_ouverture_droit(actuel, carriere) == pytest.approx(age)
    # Et le taux plein de la carrière est celui de la base, non les 65 ans de
    # la complémentaire.
    assert ouvrir.age_taux_plein_droit(actuel, carriere) >= age
