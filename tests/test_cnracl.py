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
"""

from __future__ import annotations

import pytest

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
