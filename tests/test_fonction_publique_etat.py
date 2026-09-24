"""Ce que le Service des retraites de l'État sert, lu au texte.

La passe du 24 septembre 2026 sur la fonction publique de l'État (action 89) a
lu les pages du SRE, deux fiches de service-public.gouv.fr et trois
calculettes, puis les articles qu'elles appliquent : L. 14, L. 14 bis et L. 17
du code des pensions, les articles 45 et 53 de la loi n° 2010-1330, le décret
n° 2010-1744, le XXIV de l'article 10 de la loi n° 2023-270 et l'article 13 du
décret n° 2023-435. Ce fichier tient ce qu'elle a corrigé.

**Sous quinze ans de services, le minimum garanti n'est plus un quinzième de
57,5 % par année.** C'est la règle de l'invalidité (L. 17, c). Depuis la loi
du 9 novembre 2010 (article 53, V), toute autre pension reçoit, par année de
services, le montant plein rapporté à la durée qui ouvre le pourcentage
maximum (L. 17, d) : 52/170 de la référence pour treize ans et un sédentaire
né en 1964, là où le modèle en servait 52/60 × 57,5 %, soit 63 % de plus.

**L'âge qui ouvre le minimum sans la durée était trop tardif pour les
générations de la montée en charge.** L'article 3 du décret n° 2010-1744 le
minore de neuf trimestres pour qui atteint l'âge d'ouverture en 2011, puis de
sept, cinq, trois et un.

**L'emploi classé surcote avant l'âge légal de sa génération.** Le D du XXIV de
l'article 10 de la loi du 14 avril 2023 lui donne l'âge anticipé majoré de cinq
années — l'âge minoré majoré de dix pour la super-active —, et soixante-deux
ans aux générations d'avant les marches. Le modèle attendait l'âge légal de
leur génération : un actif né en 1969 surcotait à soixante-quatre ans au lieu
de soixante-deux ans et neuf mois.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, metiers: list[Metier], naissance: int,
              liquidation: float, mois: int = 1, sexe: str = "H",
              part_primes: float = 0.15):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=sexe, metiers=metiers,
        age_liquidation=liquidation, macro=simulateur.macro,
        mois_naissance=mois, part_primes=part_primes,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return carriere, resultat, {p.regime: p for p in resultat.pensions_par_regime}


# -- le minimum garanti sous quinze ans --------------------------------------

def test_le_bareme_de_2026_est_celui_que_le_sre_publie(simulateur):
    """La table « Montant du minimum garanti à compter du 1er janvier 2026 ».

    Au-delà de soixante trimestres, le barème de L. 17, b, au trimestre près :
    785,65 € à quinze ans, 1 298,03 € à trente, 1 366,35 € à quarante. En
    deçà, hors invalidité, la colonne « cas général » se lit sur une durée
    requise de 170 trimestres : 64,30 € pour huit, 417,94 € pour cinquante-deux
    — l'exemple de la fiche F21142 de service-public.gouv.fr, un sédentaire né
    en 1964 parti après treize ans de services. La colonne de l'invalidité,
    elle, est le c : 680,90 € pour les mêmes treize ans.
    """
    minimum = simulateur.scenario_actuel.minimum_garanti

    def mensuel(trimestres, duree_maximum=None):
        return minimum.montant(2026, trimestres, duree_maximum)[0] / 12

    assert mensuel(60) == pytest.approx(785.65, abs=0.01)
    assert mensuel(94) == pytest.approx(1076.00, abs=0.01)
    assert mensuel(120) == pytest.approx(1298.03, abs=0.01)
    assert mensuel(140) == pytest.approx(1332.19, abs=0.01)
    assert mensuel(160) == pytest.approx(1366.35, abs=0.01)
    assert mensuel(8, 170) == pytest.approx(64.30, abs=0.01)
    assert mensuel(52, 170) == pytest.approx(417.94, abs=0.01)
    assert mensuel(59, 170) == pytest.approx(474.20, abs=0.01)
    # Le c, qui ne vaut plus que pour l'invalidité et l'ancien droit :
    # « (785,65 € / 15) × 13 = 680,89 € » dit la fiche, qui tronque.
    assert mensuel(52) == pytest.approx(680.90, abs=0.01)
    assert mensuel(8) == pytest.approx(104.75, abs=0.01)


def test_une_courte_carriere_publique_recoit_le_minimum_du_d(simulateur):
    """Treize ans de fonction publique après une carrière privée.

    Née en 1959, elle a 167 trimestres à réunir et liquide à 67 ans en 2026,
    au taux plein par l'âge. Son minimum est de 52/167 de la référence,
    425,45 € par mois ; le modèle lui servait 680,90 €, le montant de
    l'invalidité.
    """
    _, resultat, pensions = _calculer(
        simulateur,
        [Metier("salarie_prive_non_cadre", 30.0, 0.3),
         Metier("fonctionnaire_etat", 54.0, 0.5)],
        naissance=1959, liquidation=67.0, sexe="F",
    )
    etat = pensions["fonction_publique_etat"]
    assert "porté au minimum garanti" in etat.detail
    assert etat.montant / 12 == pytest.approx(16396.19 * 52 / 167 / 12, abs=0.01)
    assert any(a.code == "minimum_garanti" for a in resultat.avantages_appliques)


def test_l_ancien_droit_garde_le_quinzieme_de_57_5_pour_cent(simulateur):
    """Qui avait atteint l'âge d'ouverture avant 2011 garde L. 17 d'alors.

    Le V de l'article 45 de la loi du 9 novembre 2010 lui conserve l'article
    « dans [sa] rédaction antérieure » : le c, pour toutes les pensions de moins
    de quinze ans. Une fonctionnaire née en 1950, soixante ans en 2010, dix
    ans de services, reçoit donc 40/60 × 57,5 % de la référence.
    """
    carriere, _, pensions = _calculer(
        simulateur,
        [Metier("salarie_prive_non_cadre", 25.0, 0.3),
         Metier("fonctionnaire_etat", 55.0, 0.4)],
        naissance=1950, liquidation=65.0, sexe="F",
    )
    minimum = simulateur.scenario_actuel.minimum_garanti
    attendu = minimum.montant(carriere.annee_liquidation, 40)[0]
    assert pensions["fonction_publique_etat"].montant == pytest.approx(attendu)
    assert attendu == pytest.approx(
        minimum.reference(carriere.annee_liquidation)[0] * 0.575 * 40 / 60)


def test_l_age_du_minimum_est_minore_pendant_la_montee_en_charge(simulateur):
    """Le tableau de l'article 3 du décret n° 2010-1744.

    Né en août 1951, un sédentaire atteint l'âge d'ouverture en 2011 : l'âge
    qui lui ouvre le minimum garanti sans la durée est l'âge d'annulation de sa
    décote diminué de neuf trimestres. Parti à 63 ans avec une décote, il
    reçoit le minimum ; le même parti deux ans et demi plus tôt, non.
    """
    from retraite_notionnelle.scenarios.actuel import MINORATION_AGE_MINIMUM_GARANTI

    assert MINORATION_AGE_MINIMUM_GARANTI == {
        2011: 9, 2012: 7, 2013: 5, 2014: 3, 2015: 1}
    metiers = [Metier("fonctionnaire_etat", 40.0, 0.4)]
    _, resultat, pensions = _calculer(
        simulateur, metiers, naissance=1951, mois=8, liquidation=63.0)
    assert resultat.taux_liquidation < 0.75, "la pension doit porter une décote"
    assert "porté au minimum garanti" in pensions["fonction_publique_etat"].detail

    _, resultat, pensions = _calculer(
        simulateur, metiers, naissance=1951, mois=8, liquidation=60.5)
    assert "porté au minimum garanti" not in pensions["fonction_publique_etat"].detail


# -- la surcote de l'emploi classé -------------------------------------------

@pytest.mark.parametrize("statut,naissance,mois,age", [
    # Décret n° 2026-344 du 7 mai 2026, article 3, D, 2° : les huit alinéas
    # de l'active, un par génération, jusqu'aux soixante-quatre ans de 1974.
    ("fonctionnaire_etat_actif", 1966, 10, 62.25),
    ("fonctionnaire_etat_actif", 1967, 6, 62.5),
    ("fonctionnaire_etat_actif", 1968, 6, 62.75),
    ("fonctionnaire_etat_actif", 1970, 2, 62.75),
    ("fonctionnaire_etat_actif", 1970, 6, 63.0),
    ("fonctionnaire_etat_actif", 1971, 6, 63.25),
    ("fonctionnaire_etat_actif", 1972, 6, 63.5),
    ("fonctionnaire_etat_actif", 1973, 6, 63.75),
    ("fonctionnaire_etat_actif", 1976, 6, 64.0),
    # Et le 3° pour la super-active, dix ans plus tard.
    ("fonctionnaire_etat_super_actif", 1971, 10, 62.25),
    ("fonctionnaire_etat_super_actif", 1972, 6, 62.5),
    ("fonctionnaire_etat_super_actif", 1975, 6, 63.0),
    ("fonctionnaire_etat_super_actif", 1979, 6, 64.0),
    # Avant les marches, « celui applicable avant l'entrée en vigueur » de la
    # réforme : soixante-deux ans, et non l'âge légal de la génération.
    ("fonctionnaire_etat_actif", 1965, 6, 62.0),
    ("fonctionnaire_etat_super_actif", 1968, 6, 62.0),
    # La CNRACL a la même règle (décret n° 2023-435, article 13, II, D).
    ("fonctionnaire_territorial_hospitalier_actif", 1969, 6, 62.75),
])
def test_l_emploi_classe_surcote_a_l_age_anticipe_majore(simulateur, statut,
                                                         naissance, mois, age):
    carriere, _, _ = _calculer(
        simulateur, [Metier(statut, 20.0, 1.0)],
        naissance=naissance, mois=mois, liquidation=64.0,
    )
    actuel = simulateur.scenario_actuel
    regime = ("cnracl" if "territorial" in statut else "fonction_publique_etat")
    periode = simulateur.catalogue[regime].periode(carriere.annee_liquidation)
    assert actuel._age_surcote(periode, carriere) == pytest.approx(age)


def test_le_sedentaire_surcote_toujours_a_l_age_legal(simulateur):
    """La dérogation ne vaut que pour l'emploi classé qui en remplit la durée."""
    actuel = simulateur.scenario_actuel
    for statut, naissance in (("fonctionnaire_etat", 1969),
                              ("fonctionnaire_etat", 1965)):
        carriere, _, _ = _calculer(simulateur, [Metier(statut, 20.0, 1.0)],
                                   naissance=naissance, mois=6, liquidation=64.0)
        periode = simulateur.catalogue["fonction_publique_etat"].periode(
            carriere.annee_liquidation)
        assert actuel._age_surcote(periode, carriere) == pytest.approx(
            actuel._age_ouverture_commun(periode, carriere))
    # Un actif qui n'a pas ses dix-sept ans de services classés reste au droit
    # commun : quinze ans d'emploi classé, puis un emploi sédentaire.
    carriere, _, _ = _calculer(
        simulateur, [Metier("fonctionnaire_etat", 20.0, 1.0),
                     Metier("fonctionnaire_etat_actif", 49.0, 1.0)],
        naissance=1969, mois=6, liquidation=64.0)
    periode = simulateur.catalogue["fonction_publique_etat"].periode(
        carriere.annee_liquidation)
    assert actuel._age_surcote(periode, carriere) == pytest.approx(64.0)


def test_un_actif_ne_en_1969_surcote_des_62_ans_et_9_mois(simulateur):
    """Quarante-trois ans de services actifs, départ à 64 ans.

    Le droit lui ouvre la surcote à 62 ans et 9 mois ; chaque trimestre civil
    entier cotisé ensuite, au-delà de ses 170 trimestres, vaut 1,25 %. Le
    modèle ne lui en comptait aucun avant 64 ans.
    """
    _, resultat, _ = _calculer(
        simulateur, [Metier("fonctionnaire_etat_actif", 21.0, 1.0)],
        naissance=1969, mois=6, liquidation=64.0, part_primes=0.2)
    assert resultat.trimestres_requis == 170
    # 171 trimestres à 64 ans : un seul au-delà de la durée, accompli après
    # 62 ans et 9 mois. Compté depuis 64 ans, il ne valait rien.
    supplementaires = resultat.trimestres_valides - 170
    assert supplementaires == 1
    assert resultat.taux_liquidation == pytest.approx(
        0.75 * (1 + 0.0125 * supplementaires))
