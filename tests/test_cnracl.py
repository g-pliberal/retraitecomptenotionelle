"""Ce que la CNRACL applique, lu au texte.

La passe du 24 septembre 2026 sur la CNRACL (action 89) a lu les pages de la
caisse et sa documentation juridique (juris-cnracl.retraites.fr), interrogé
ses calculettes, puis relu les textes qu'elles appliquent : le décret
n° 2003-1306, le code des pensions (L. 13, L. 14, D. 16-1), le XXIV de
l'article 10 de la loi n° 2023-270. Trois exemples de la caisse entrent aux
témoins officiels ; ce fichier tient les deux règles qu'elle a corrigées, qui
valent pour les trois régimes du code des pensions — l'État, la CNRACL, le
FSPOEIE.

**La carrière longue ouverte avant soixante ans fait lire la durée à la date
d'ouverture.** Le C du XXIV vise « les fonctionnaires civils, autres que ceux
mentionnés aux A et B du présent XXIV, et les militaires remplissant les
conditions de liquidation de la pension avant l'âge de soixante ans » : 169
trimestres pour qui peut liquider à compter du 1er septembre 2023, un de plus
en 2025 et en 2027. Avant, L. 13, III, disait la même chose de tous les
fonctionnaires. Le modèle ne l'opposait qu'au militaire.

**La surcote se compte en durée, non en trimestres civils.** L. 14, III,
retient les « trimestres d'assurance effectués » au-delà de l'âge et de la
durée : la période s'ouvre quand les conditions sont réunies. Le modèle
appliquait la règle du régime général, qui attend le trimestre civil suivant.

**Le traitement d'une pension différée suit les pensions, non le point.** « Le
traitement ou la solde mentionnés à l'article L. 15 sont revalorisés pendant
la période comprise entre la radiation des cadres et la mise en paiement de la
pension, conformément aux dispositions de l'article L. 16 » (L. 25 du code des
pensions ; article 26 du décret n° 2003-1306, article 22 du décret
n° 2004-1056). Le modèle portait le traitement de l'agent parti avant l'âge au
point d'indice des actifs, gelé de 2010 à 2016 : un quart de revalorisations
perdu de 2012 à 2026.
"""

from __future__ import annotations

from datetime import date

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.revalorisation import coefficient_traitement_differe
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int,
              debut: float, liquidation: float, mois: int = 1, sexe: str = "H"):
    carriere = simulateur.carriere_simple(
        annee_naissance=naissance, mois_naissance=mois, sexe=sexe,
        affiliation=affiliation, age_debut=debut, age_liquidation=liquidation)
    return carriere, simulateur.scenario_actuel.calculer(carriere)


# -- la durée d'une carrière longue ouverte avant soixante ans ---------------

@pytest.mark.parametrize("affiliation, naissance, mois, liquidation, requis", [
    # Droit ouvert à 58 ans en 2025 : 170 (l'exemple de la CNRACL).
    ("fonctionnaire_territorial_hospitalier", 1967, 1, 58, 170),
    # Le même, parti à 62 ans : la durée reste celle de l'ouverture.
    ("fonctionnaire_territorial_hospitalier", 1967, 1, 62, 170),
    # Ouvert à 58 ans en juin 2024 : 169.
    ("fonctionnaire_etat", 1966, 6, 59, 169),
    ("ouvrier_etat", 1967, 1, 58, 170),
    # Ouvert en 2028 : la durée de la génération, 172.
    ("fonctionnaire_etat", 1970, 1, 58, 172),
    # Ouvert à 59 ans en 2020, avant la loi de 2023 : L. 13, III, la durée
    # des fonctionnaires qui ont soixante ans en 2020, génération 1960.
    ("fonctionnaire_etat", 1961, 1, 59, 167),
])
def test_la_carriere_longue_avant_soixante_ans_lit_la_duree_a_l_ouverture(
        simulateur, affiliation, naissance, mois, liquidation, requis):
    _, resultat = _calculer(simulateur, affiliation, naissance, 15, liquidation, mois)
    assert resultat.motif_ouverture == "carriere_longue"
    assert resultat.trimestres_requis == requis


def test_la_condition_de_la_carriere_longue_reste_la_duree_de_la_generation(simulateur):
    """D. 16-1, rédaction du décret n° 2026-345 : la carrière longue s'ouvre à
    qui a cotisé « au moins [la] durée mentionnée à l'article L. 161-17-3 »,
    celle de sa génération. Le fonctionnaire né en 1967 qui n'a que 171
    trimestres cotisés à cinquante-huit ans n'y a pas droit, même si la
    durée que ce droit lui ferait opposer est de 170."""
    _, resultat = _calculer(simulateur, "fonctionnaire_territorial_hospitalier",
                            1967, 15.25, 58)
    assert resultat.motif_ouverture == "non_ouverte"


def test_la_banque_de_france_garde_la_duree_de_sa_generation(simulateur):
    """Elle emprunte le barème de décote de la fonction publique, pas le code
    des pensions : le XXIV ne la vise pas."""
    _, resultat = _calculer(simulateur, "agent_banque_de_france", 1967, 15, 58)
    assert resultat.motif_ouverture == "carriere_longue"
    assert resultat.trimestres_requis == 172


# -- la surcote en durée ------------------------------------------------------

def test_la_surcote_de_la_fonction_publique_se_compte_en_duree(simulateur):
    """Née en avril 1962, à l'âge légal de 62 ans et 6 mois en octobre 2024,
    partie en février 2026 : quinze mois de services au-delà, cinq trimestres
    entiers de surcote, 6,25 %. La règle du régime général en comptait quatre
    — de janvier 2025, trimestre civil qui suit l'âge, à décembre 2025 —, et
    c'est ce que la salariée du privé née le même mois reçoit encore."""
    for affiliation in ("fonctionnaire_etat", "fonctionnaire_territorial_hospitalier",
                        "ouvrier_etat"):
        carriere, resultat = _calculer(simulateur, affiliation, 1962, 20,
                                       63 + 10 / 12, mois=4, sexe="F")
        assert (carriere.date_liquidation.annee, carriere.date_liquidation.mois) == (2026, 2)
        assert resultat.trimestres_requis == 169
        assert resultat.taux_liquidation == pytest.approx(0.75 * (1 + 5 * 0.0125)), affiliation
    _, prive = _calculer(simulateur, "salarie_prive_non_cadre", 1962, 20,
                         63 + 10 / 12, mois=4, sexe="F")
    assert prive.taux_liquidation == pytest.approx(0.50 * (1 + 4 * 0.0125))


def test_un_trimestre_de_duree_prend_le_taux_de_son_dernier_mois(simulateur):
    """Né en janvier 1948, à soixante ans en janvier 2008, parti en janvier
    2011 : onze trimestres depuis février 2008, dont trois achevés en 2008 à
    0,75 % et huit à 1,25 % — celui de novembre 2008 à janvier 2009 compris,
    accompli sous la LFSS pour 2009."""
    _, resultat = _calculer(simulateur, "fonctionnaire_etat", 1948, 20, 63)
    assert resultat.taux_liquidation == pytest.approx(0.75 * (1 + 3 * 0.0075 + 8 * 0.0125))


# -- la pension différée ------------------------------------------------------

def _sans_point(perception: int, arrivee: int) -> float:
    return 1.0


def test_le_traitement_differe_prend_les_revalorisations_des_pensions(simulateur):
    """De la radiation au 1er janvier 2012 à la mise en paiement au 1er janvier
    2026 : chaque revalorisation des pensions de l'article L. 161-23-1, celle
    du jour de la mise en paiement comprise — « si la pension est due à compter
    de la date de revalorisation, le traitement servant au calcul de la
    pension bénéficie de la revalorisation des pensions » (CNRACL) —, et en
    2020 le coefficient de L. 161-25, 1 %, la dérogation de 0,3 % ne visant que
    les pensions servies."""
    revalorisations = simulateur.scenario_actuel.revalorisations_pensions
    attendu = 1.0
    for coefficient in (1.021, 1.013, 1.001, 1.008, 1.003, 1.01, 1.004, 1.011,
                        1.04, 1.008, 1.053, 1.022, 1.009):
        attendu *= coefficient
    assert coefficient_traitement_differe(
        revalorisations, _sans_point, 2011, date(2012, 1, 1), date(2026, 1, 1),
    ) == pytest.approx(attendu, rel=1e-12)
    # Celle du jour de la radiation n'est pas due, celle du jour de la mise
    # en paiement l'est.
    assert coefficient_traitement_differe(
        revalorisations, _sans_point, 2023, date(2024, 1, 1), date(2025, 1, 1),
    ) == pytest.approx(1.022, rel=1e-12)
    assert coefficient_traitement_differe(
        revalorisations, _sans_point, 2018, date(2019, 1, 1), date(2021, 1, 1),
    ) == pytest.approx(1.01 * 1.004, rel=1e-12)


def test_avant_2004_la_perequation_puis_les_decrets(simulateur):
    """Radié en 1996, payé en 2005 : le point jusqu'en 2003 — la péréquation
    faisait suivre le traitement des actifs à toute pension civile —, puis les
    décrets de 2004 et de 2005, celui du 1er janvier 2004 compris."""
    revalorisations = simulateur.scenario_actuel.revalorisations_pensions
    appels = []

    def point(perception: int, arrivee: int) -> float:
        appels.append((perception, arrivee))
        return 1.0

    assert coefficient_traitement_differe(
        revalorisations, point, 1995, date(1996, 1, 1), date(2005, 1, 1),
    ) == pytest.approx(1.015 * 1.02, rel=1e-12)
    assert appels == [(1995, 2003)]


def test_la_pension_differee_est_celle_du_depart_revalorisee(simulateur):
    """Un fonctionnaire de l'État né en 1962, entré à vingt-deux ans, passé au
    privé à cinquante ans, liquide en janvier 2026 : son traitement de
    référence est celui d'une liquidation en janvier 2012, multiplié par les
    revalorisations des pensions depuis. Le modèle le portait au point
    d'indice, 14,9 % plus bas."""
    actuel = simulateur.scenario_actuel
    code = "fonction_publique_etat"
    differee = Carriere.depuis_parcours(
        annee_naissance=1962, sexe="H", age_liquidation=64, macro=simulateur.macro,
        metiers=[Metier(affiliation="fonctionnaire_etat", age_debut=22),
                 Metier(affiliation="salarie_prive_non_cadre", age_debut=50)])
    immediate = Carriere.depuis_parcours(
        annee_naissance=1962, sexe="H", age_liquidation=50, macro=simulateur.macro,
        metiers=[Metier(affiliation="fonctionnaire_etat", age_debut=22)])
    en_2026 = actuel.salaire_de_reference(
        code, differee, simulateur.catalogue[code].periode(2026), 2026, False)
    en_2012 = actuel.salaire_de_reference(
        code, immediate, simulateur.catalogue[code].periode(2012), 2012, False)
    revalorisations, _ = actuel.revalorisations_pensions.generale(
        date(2012, 1, 1), date(2026, 1, 1), False, 0.0)
    assert en_2026 == pytest.approx(en_2012 * revalorisations, rel=1e-12)
    point = actuel.minimum_garanti.ratio_point_indice(2012, 2026)
    assert revalorisations / point == pytest.approx(1.149, abs=5e-4)


@pytest.mark.parametrize("affiliation, code", [
    ("fonctionnaire_territorial_hospitalier", "cnracl"),
    ("ouvrier_etat", "fspoeie"),
])
def test_la_cnracl_et_le_fspoeie_ont_la_meme_regle(simulateur, affiliation, code):
    """Article 26 du décret n° 2003-1306, article 22 du décret n° 2004-1056."""
    actuel = simulateur.scenario_actuel
    differee = Carriere.depuis_parcours(
        annee_naissance=1962, sexe="H", age_liquidation=64, macro=simulateur.macro,
        metiers=[Metier(affiliation=affiliation, age_debut=22),
                 Metier(affiliation="salarie_prive_non_cadre", age_debut=50)])
    immediate = Carriere.depuis_parcours(
        annee_naissance=1962, sexe="H", age_liquidation=50, macro=simulateur.macro,
        metiers=[Metier(affiliation=affiliation, age_debut=22)])
    en_2026 = actuel.salaire_de_reference(
        code, differee, simulateur.catalogue[code].periode(2026), 2026, False)
    en_2012 = actuel.salaire_de_reference(
        code, immediate, simulateur.catalogue[code].periode(2012), 2012, False)
    revalorisations, _ = actuel.revalorisations_pensions.generale(
        date(2012, 1, 1), date(2026, 1, 1), False, 0.0)
    assert en_2026 == pytest.approx(en_2012 * revalorisations, rel=1e-12)


def test_ni_la_carriere_complete_ni_la_banque_de_france_ne_bougent(simulateur):
    """Qui liquide en sortant de service n'a pas de pension différée ; la
    Banque de France n'est pas au code des pensions, et son règlement n'écrit
    pas la règle. Et une pension payée avant 2004 relève de la péréquation."""
    actuel = simulateur.scenario_actuel
    complete = Carriere.depuis_parcours(
        annee_naissance=1962, sexe="H", age_liquidation=64, macro=simulateur.macro,
        metiers=[Metier(affiliation="fonctionnaire_etat", age_debut=22)])
    periode = simulateur.catalogue["fonction_publique_etat"].periode(2026)
    ligne = next(l for l in complete.lignes if l.annee == 2025)
    assert actuel.salaire_de_reference(
        "fonction_publique_etat", complete, periode, 2026, False
    ) == pytest.approx(actuel._assiette_de_reference(periode, ligne)
                       * actuel.minimum_garanti.ratio_point_indice(2025, 2026))
    banque = Carriere.depuis_parcours(
        annee_naissance=1962, sexe="H", age_liquidation=64, macro=simulateur.macro,
        metiers=[Metier(affiliation="agent_banque_de_france", age_debut=22),
                 Metier(affiliation="salarie_prive_non_cadre", age_debut=50)])
    periode_bdf = simulateur.catalogue["banque_de_france"].periode(2026)
    ligne_bdf = next(l for l in banque.lignes if l.annee == 2011)
    assert actuel.salaire_de_reference(
        "banque_de_france", banque, periode_bdf, 2026, False
    ) == pytest.approx(actuel._assiette_de_reference(periode_bdf, ligne_bdf)
                       * simulateur.macro.coefficient_revalorisation_salaires(2011, 2026))
    ancienne = Carriere.depuis_parcours(
        annee_naissance=1940, sexe="H", age_liquidation=61, macro=simulateur.macro,
        metiers=[Metier(affiliation="fonctionnaire_etat", age_debut=22),
                 Metier(affiliation="salarie_prive_non_cadre", age_debut=45)])
    periode_2001 = simulateur.catalogue["fonction_publique_etat"].periode(2001)
    ligne_1984 = next(l for l in ancienne.lignes if l.annee == 1984)
    assert actuel.salaire_de_reference(
        "fonction_publique_etat", ancienne, periode_2001, 2001, False
    ) == pytest.approx(actuel._assiette_de_reference(periode_2001, ligne_1984)
                       * actuel.minimum_garanti.ratio_point_indice(1984, 2001))
