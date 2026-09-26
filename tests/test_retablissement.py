"""Le fonctionnaire parti sans droit à pension : rétabli au régime général.

« Le fonctionnaire civil ou le militaire qui vient à quitter le service, pour
quelque cause que ce soit, sans pouvoir obtenir une pension [...] est rétabli,
en ce qui concerne l'assurance vieillesse, dans la situation qu'il aurait eue
s'il avait été affilié au régime général des assurances sociales et à
[l'Ircantec] pendant la période où il a été soumis au présent régime » (L. 65
du code des pensions ; article 64 du décret n° 2003-1306 pour la CNRACL ;
D. 173-15 et D. 173-16 du code de la sécurité sociale pour l'État, la CNRACL,
les ouvriers de l'État et la SEITA). Sans droit à pension : moins de quinze ans
de services pour qui est radié avant 2011, moins de deux ans depuis — les trois
régimes interpénétrés comptés ensemble —, quinze ans pour le militaire dont le
premier engagement précède le 1er janvier 2014.

Le régime général porte au compte « des salaires reconstitués à partir des
cotisations rétroactives calculées sur la base des derniers émoluments ou de
la dernière solde soumis à retenues pour pension au titre du régime spécial de
retraites, dans la limite du plafond en vigueur » (circulaire Cnav 2011/38),
et la période « entre en compte, quel qu'ait été le montant de sa
rémunération » (D. 173-16). L'Ircantec valide les services « suivant sa propre
réglementation » (article 9 du décret n° 70-1277).

Le modèle pensionnait ces années au prorata dans le régime spécial. La passe du
24 septembre 2026 a lu L. 65 dans ses versions depuis 1964, D. 173-15 à
D. 173-17, l'article 64 du décret n° 2003-1306, l'article 9 du décret
n° 70-1277, L. 6 et l'article 42 de la loi n° 2014-40, la circulaire Cnav
2011/38 et les pages de juris-cnracl sur le rétablissement. Ce fichier tient
ce qu'elle a corrigé.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.droit import coordonner
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur: Simulateur, metiers: list[tuple[str, float]],
              naissance: int = 1962, liquidation: float = 64, sexe: str = "H",
              **kwargs) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=naissance, sexe=sexe,
        metiers=[Metier(affiliation=statut, age_debut=debut) for statut, debut in metiers],
        age_liquidation=liquidation, macro=simulateur.macro, **kwargs,
    )


def _pensions(simulateur: Simulateur, carriere: Carriere) -> dict:
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return {p.regime: p for p in resultat.pensions_par_regime if p.montant}


def _retablies(simulateur: Simulateur, carriere: Carriere) -> list:
    return [ligne for ligne in coordonner.retablir(simulateur.scenario_actuel, carriere).lignes
            if ligne.revenu_retabli > 0]


# -- qui est rétabli ------------------------------------------------------------

def test_un_an_a_l_etat_avant_2011(simulateur):
    """Un an à l'État en 1984 : pas de pension civile, mais les quatre
    trimestres au régime général et des points à l'Ircantec. Le modèle servait
    une pension de l'État au prorata de 4/169."""
    pensions = _pensions(simulateur, _carriere(simulateur, [
        ("fonctionnaire_etat", 22), ("salarie_prive_non_cadre", 23)]))
    assert "fonction_publique_etat" not in pensions
    assert "× 168/169" in pensions["regime_general"].detail
    assert "ircantec" in pensions


def test_treize_ans_a_l_hopital_avant_2011(simulateur):
    """Treize ans à la CNRACL, partie en 1997 : les quinze ans manquent."""
    carriere = _carriere(simulateur, [
        ("fonctionnaire_territorial_hospitalier", 22), ("salarie_prive_non_cadre", 35)])
    pensions = _pensions(simulateur, carriere)
    assert "cnracl" not in pensions
    assert "× 168/169" in pensions["regime_general"].detail
    assert [ligne.annee for ligne in _retablies(simulateur, carriere)] == list(range(1984, 1997))


def test_deux_ans_depuis_2011_ouvrent_une_pension(simulateur):
    """Trois ans à l'État, radiée au 1er janvier 2013 : R. 4-1 lui ouvre une
    pension, et rien n'est rétabli."""
    carriere = _carriere(simulateur, [
        ("salarie_prive_non_cadre", 22), ("fonctionnaire_etat", 25),
        ("salarie_prive_non_cadre", 28)], naissance=1985)
    assert coordonner.retablir(simulateur.scenario_actuel, carriere) is carriere
    assert "fonction_publique_etat" in _pensions(simulateur, carriere)


@pytest.mark.parametrize("statut, rétabli", [
    # Le militaire engagé avant 2014 garde ses quinze ans (L. 6) ; le civil
    # n'en demande que deux depuis 2011 (R. 4-1).
    ("militaire", True),
    ("fonctionnaire_etat", False),
])
def test_deux_ans_radies_en_2012(simulateur, statut, rétabli):
    carriere = _carriere(simulateur, [
        ("salarie_prive_non_cadre", 22), (statut, 25),
        ("salarie_prive_non_cadre", 27)], naissance=1985)
    assert bool(_retablies(simulateur, carriere)) is rétabli


def test_le_militaire_engage_depuis_2014(simulateur):
    """Deux ans sous l'uniforme, engagé en 2015 : la durée de R. 4-1 vaut aussi
    pour lui, et il a sa pension militaire."""
    carriere = _carriere(simulateur, [
        ("salarie_prive_non_cadre", 22), ("militaire", 30),
        ("salarie_prive_non_cadre", 32)], naissance=1985)
    assert not _retablies(simulateur, carriere)


def test_le_militaire_engage_avant_2014_garde_ses_quinze_ans(simulateur):
    """Engagé en 2012, radié en 2016 après quatre ans : la loi n° 2014-40 ne
    donne les deux ans de R. 4-1 qu'aux « militaires dont le premier engagement
    a été conclu à compter du 1er janvier 2014 » (article 42, II). Il est
    rétabli, quand la radiation seule lui aurait ouvert une pension."""
    carriere = _carriere(simulateur, [
        ("salarie_prive_non_cadre", 22), ("militaire", 27),
        ("salarie_prive_non_cadre", 31)], naissance=1985)
    assert [ligne.annee for ligne in _retablies(simulateur, carriere)] == [
        2012, 2013, 2014, 2015]
    assert "fonction_publique_etat" not in _pensions(simulateur, carriere)


def test_le_retour_dans_un_regime_interpenetre_annule_le_retablissement(simulateur):
    """Un an à l'État en 1984, puis vingt-quatre à la CNRACL : l'agent « remis
    en activité » dans un régime interpénétré « bénéficie, pour la retraite, de
    la totalité des services accomplis » (article 64, II, du décret
    n° 2003-1306). Rien n'est rétabli ; la pension unique compte l'année de
    1984."""
    carriere = _carriere(simulateur, [
        ("fonctionnaire_etat", 22), ("salarie_prive_non_cadre", 23),
        ("fonctionnaire_territorial_hospitalier", 40)])
    assert not _retablies(simulateur, carriere)
    assert "× 100/169" in _pensions(simulateur, carriere)["cnracl"].detail


@pytest.mark.parametrize("fin_seita, rétabli", [(60, False), (58, True)])
def test_la_seita(simulateur, fin_seita, rétabli):
    """Dix ans à la SEITA : partie à cinquante-huit ans, elle n'a pas les quinze
    ans de l'article 112 et est rétablie ; restée jusqu'à soixante ans,
    l'article 110 lui ouvre la pension sans durée."""
    metiers = [("salarie_prive_non_cadre", 22), ("agent_seita", 48)]
    if fin_seita < 60:
        metiers.append(("salarie_prive_non_cadre", fin_seita))
    carriere = _carriere(simulateur, metiers, naissance=1930, liquidation=60)
    assert bool(_retablies(simulateur, carriere)) is rétabli


def test_avant_1950_rien_n_est_retabli(simulateur):
    """Le rétablissement ne vaut que pour qui a quitté son régime après le
    28 janvier 1950 (décret n° 50-133 ; circulaire Cnav 2011/38)."""
    carriere = _carriere(simulateur, [
        ("fonctionnaire_etat", 22), ("salarie_prive_non_cadre", 28)],
        naissance=1915, liquidation=65)
    assert coordonner.retablir(simulateur.scenario_actuel, carriere) is carriere


def test_la_mere_retablie_recoit_ses_trimestres_du_regime_general(simulateur):
    """Treize ans à l'hôpital puis plus rien, deux enfants : la CNRACL ne peut
    pas la pensionner, et R. 173-15 donne les trimestres des enfants au régime
    général, qui a désormais ses treize années — huit par enfant."""
    pensions = _pensions(simulateur, _carriere(simulateur, [
        ("fonctionnaire_territorial_hospitalier", 22), ("sans_activite", 35)],
        sexe="F", nombre_enfants=2))
    assert "cnracl" not in pensions
    assert "× 68/169" in pensions["regime_general"].detail


# -- ce que le régime général et l'Ircantec en font ------------------------------

def test_le_regime_general_porte_le_dernier_traitement(simulateur):
    """Toutes les années rétablies portent le dernier traitement, ramené à leur
    fraction d'année ; le plafond de chaque année s'applique ensuite."""
    carriere = _carriere(simulateur, [
        ("fonctionnaire_territorial_hospitalier", 22), ("sans_activite", 35)])
    retablies = _retablies(simulateur, carriere)
    derniere = retablies[-1]
    traitement = derniere.revenu_annualise * (1.0 - derniere.part_primes)
    for ligne in retablies:
        assert ligne.revenu_retabli == pytest.approx(traitement * ligne.fraction_annee)
    # Le salaire annuel moyen ne porte que sur ces treize années : le dernier
    # traitement, écrêté au plafond de l'année, revalorisé.
    actuel = simulateur.scenario_actuel
    retablie = coordonner.retablir(actuel, carriere)
    annee_liquidation = carriere.annee_liquidation
    periode = actuel.catalogue["regime_general"].periode(annee_liquidation)
    attendus = sorted((
        min(ligne.revenu_retabli,
            actuel.macro.plafond_securite_sociale(ligne.annee) * ligne.fraction_annee)
        * actuel.macro.coefficient_revalorisation_portee_au_compte(
            ligne.annee, annee_liquidation, carriere.mois_liquidation)
        for ligne in retablies), reverse=True)
    reference = actuel.salaire_de_reference(
        "regime_general", retablie, periode, annee_liquidation, True,
        carriere.annee_naissance)
    assert reference == pytest.approx(sum(attendus) / len(attendus), rel=1e-12)


def test_les_annees_retablies_quittent_le_regime_special(simulateur):
    """Une année rétablie cotise au régime général et à l'Ircantec, et garde le
    RAFP ; son statut, lui, ne change pas."""
    carriere = _carriere(simulateur, [
        ("salarie_prive_non_cadre", 22), ("fonctionnaire_etat", 30),
        ("salarie_prive_non_cadre", 31)], naissance=1985)
    actuel = simulateur.scenario_actuel
    ligne = next(l for l in coordonner.retablir(actuel, carriere).lignes if l.revenu_retabli > 0)
    assert ligne.affiliation == "fonctionnaire_etat"
    assert set(coordonner.regimes_de(actuel, ligne, ligne.annee)) == {"regime_general", "ircantec", "rafp"}


def test_les_primes_restent_au_rafp(simulateur):
    """Un an à l'État en 2015, avec un quart de primes : le RAFP garde ses
    points ; l'Ircantec et le régime général ne prennent que le traitement."""
    avec_primes = _carriere(simulateur, [
        ("salarie_prive_non_cadre", 22), ("fonctionnaire_etat", 30),
        ("salarie_prive_non_cadre", 31)], naissance=1985, part_primes=0.25)
    sans_primes = _carriere(simulateur, [
        ("salarie_prive_non_cadre", 22), ("fonctionnaire_etat", 30),
        ("salarie_prive_non_cadre", 31)], naissance=1985)
    pensions = _pensions(simulateur, avec_primes)
    assert pensions["rafp"].montant > 0
    ligne = next(l for l in coordonner.retablir(simulateur.scenario_actuel, avec_primes).lignes
                 if l.revenu_retabli > 0)
    assert ligne.revenu_retabli == pytest.approx(ligne.revenu * 0.75)
    assert "rafp" not in _pensions(simulateur, sans_primes)
