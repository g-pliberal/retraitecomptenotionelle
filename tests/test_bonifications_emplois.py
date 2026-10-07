"""Ce que les emplois classés de la fonction publique ajoutent à la pension.

Action 138, étape 17 : le dépôt ne servait aucune bonification de service, et
TRAJECTOiRE servait celle des policiers (registre, 138.17). La loi n° 57-444
du 8 avril 1957 accorde aux policiers des services actifs « une bonification
pour la liquidation de ladite pension, égale à un cinquième du temps qu'ils
ont effectivement passé en position d'activité dans des services actifs de
police », cinq annuités au plus ; la loi n° 96-452 la même aux surveillants
pénitentiaires. Fiche ``bonification_cinquieme_police_penitentiaire``.

Elle entre aux services liquidés, mais « dans la limite du taux maximal de
75 % » (service des retraites de l'État) ; à la durée d'assurance, qui
« totalise la durée des services et bonifications admissibles en
liquidation » (L. 14, I), et non à celle de la surcote (L. 14, III).
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import releve
from retraite_notionnelle.simulateur import Simulateur

POLICIER = "fonctionnaire_etat_super_actif"
ETAT = ("fonction_publique_etat",)


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, metiers: list[Metier], naissance: int,
              liquidation: float, avantages: bool = True):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, sexe="H", metiers=metiers,
        age_liquidation=liquidation, macro=simulateur.macro, mois_naissance=1,
        part_primes=0.15)
    durees = releve.construire(simulateur.scenario_actuel, carriere,
                               avantages_non_contributifs=avantages).durees
    resultat = simulateur.scenario_actuel.calculer(carriere)
    pensions = {p.regime: p for p in resultat.pensions_par_regime}
    return durees, resultat, pensions


def test_vingt_trimestres_au_policier_de_trente_trois_ans_de_services(simulateur):
    """Le policier du cas type 8 du COR, né en 1960 : trente-trois ans de
    services actifs, départ à cinquante-deux ans en janvier 2012. Un cinquième
    de trente-trois ans, six ans et sept mois, borné à cinq annuités : vingt
    trimestres, aux services liquidés — 152/162 de 75 % — et à la durée."""
    durees, resultat, pensions = _calculer(
        simulateur, [Metier(POLICIER, 19.0, 1.0)], naissance=1960, liquidation=52.0)
    (emploi,) = durees.emplois
    assert (emploi.fiche, emploi.version) == (
        "bonification_cinquieme_police_penitentiaire", "loi_du_9_novembre_2010")
    assert (emploi.services, emploi.duree, emploi.majoration) == (20, 20, 0)
    assert durees.services_des_emplois(ETAT) == 20
    assert resultat.trimestres_valides == 132 + 20
    assert "× 152/162" in pensions["fonction_publique_etat"].detail


def test_sans_la_duree_de_l_age_minore_pas_de_bonification(simulateur):
    """Vingt-deux ans de services actifs, quand la génération 1960 en demande
    vingt-sept pour l'âge minoré : ni l'un ni l'autre."""
    durees, _, _ = _calculer(
        simulateur, [Metier(POLICIER, 30.0, 1.0)], naissance=1960, liquidation=52.0)
    assert durees.emplois == ()


def test_les_services_au_dela_de_cinquante_sept_ans_la_reduisent_jusqu_en_2023(simulateur):
    """Né en 1953, policier de vingt à soixante ans, départ en janvier 2013 :
    les deux années servies après celle de ses cinquante-sept ans retirent
    deux annuités — douze trimestres, et non vingt (« réduite à concurrence
    de la durée des services accomplis au-delà de cinquante-sept ans »). Et
    sous le maximum : 150/150, non 172/150."""
    durees, _, pensions = _calculer(
        simulateur, [Metier(POLICIER, 20.0, 1.0)], naissance=1953, liquidation=60.0)
    assert [e.services for e in durees.emplois] == [12]
    assert "× 150/150" in pensions["fonction_publique_etat"].detail
    # Depuis le 1er septembre 2023, aucune réduction : vingt trimestres.
    durees, _, _ = _calculer(
        simulateur, [Metier(POLICIER, 20.0, 1.0)], naissance=1964, liquidation=62.0)
    assert [(e.version, e.services) for e in durees.emplois] == [("loi_du_14_avril_2023", 20)]


def test_rien_avant_la_loi_de_1957(simulateur):
    """La loi l'accorde « à compter du 1er janvier 1957 »."""
    durees, _, _ = _calculer(
        simulateur, [Metier(POLICIER, 20.0, 1.0)], naissance=1900, liquidation=54.0)
    assert durees.emplois == ()


def test_la_bonification_n_ouvre_pas_la_surcote(simulateur):
    """Né en 1964, policier de vingt-cinq à soixante-quatre ans : 156 trimestres
    de services, vingt de bonification. Sa durée efface la décote et sa
    pension atteint le maximum ; mais « les bonifications de durée de services
    […] ne sont pas prises en compte » pour la surcote (L. 14, III) : ses huit
    trimestres d'après soixante-deux ans n'en ouvrent aucune."""
    durees, resultat, pensions = _calculer(
        simulateur, [Metier(POLICIER, 25.0, 1.0)], naissance=1964, liquidation=64.0)
    assert durees.duree_hors_surcote == 20
    assert resultat.trimestres_valides >= resultat.trimestres_requis
    assert resultat.taux_liquidation == pytest.approx(0.75)
    assert f"× {resultat.trimestres_requis}/{resultat.trimestres_requis}" in (
        pensions["fonction_publique_etat"].detail)


def test_le_contributif_pur_ne_la_sert_pas(simulateur):
    """La valorisation des droits acquis ne mesure que le contributif : la
    bonification, que rien n'a cotisé, en sort avec les trimestres des
    enfants."""
    durees, _, _ = _calculer(simulateur, [Metier(POLICIER, 19.0, 1.0)],
                             naissance=1960, liquidation=52.0, avantages=False)
    assert durees.emplois == ()
    assert durees.trimestres == 132
