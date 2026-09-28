"""La réversion, régime par régime : ce que le décès de l'assuré ouvre à son conjoint.

Le domaine de la réversion (docs/architecture.md, § 11). Les versions des fiches
``reversion``, ``reversion_fonction_publique`` et ``reversion_agirc_arrco`` se
lisent sur la date d'effet de la réversion et sur la date du décès
(``droit/reversion.py``). Ce fichier tient les bornes et les conditions que
chaque version porte : la veille et le jour d'un taux, l'âge qui reporte la
date d'effet, le plafond de ressources, la durée du mariage. Les deux moteurs,
eux, sont comparés par les témoins ``reversion_*`` des simulations.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle.carriere import Carriere
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.droit.reversion import reversion
from retraite_notionnelle.saisie import ErreurSaisie, Saisie
from retraite_notionnelle.simulateur import Simulateur

HAUTE = Fiabilite.HAUTE


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur, naissance: int, depart: float, conjoint: str, deces: str,
              mariage: str | None = None, ressources: float | None = None,
              enfants: int = 0, sexe_conjoint: str = "F") -> Carriere:
    """Un salarié né en janvier ``naissance``, parti à ``depart`` ans, et son
    conjoint ; le décès ouvre la réversion. Les pensions, elles, sont données
    à :func:`reversion` : seule la règle est en cause ici."""
    return Carriere.depuis_profil(
        naissance, "H", "salarie_prive", 21.0, depart, simulateur.macro,
        nombre_enfants=enfants,
        conjoint={"naissance": conjoint, "sexe": sexe_conjoint, "mariage": mariage,
                  "ressources": ressources},
        deces=deces)


def _lignes(simulateur, carriere, pensions, annee):
    """Chaque ligne de la réversion : régime, taux, montant arrondi, motif,
    version, date d'effet."""
    resultat = reversion(simulateur.scenario_actuel,
                         [(regime, base, HAUTE) for regime, base in pensions],
                         carriere, annee)
    return [(r.regime, r.taux, round(r.montant, 2), r.motif, r.version, r.date_effet)
            for r in resultat.regimes]


def _plafond(simulateur, annee: int) -> float:
    """2 080 fois le SMIC horaire du 1er janvier (R. 353-1-1)."""
    return 2080 * simulateur.macro.smic_horaire(annee)


# -- le régime général ------------------------------------------------------------

@pytest.mark.parametrize("deces, attendu", [
    ("1982-10-15", ("regime_general", 0.50, 5000.0, "servie", "avant_1982", "1982-11-01")),
    ("1982-11-10", ("regime_general", 0.52, 5200.0, "servie", "taux_52", "1982-12-01")),
])
def test_le_taux_suit_la_date_d_effet(simulateur, deces, attendu):
    """Décret n° 82-1035 : 52 % pour les réversions prenant effet à compter du
    1er décembre 1982 (circulaire Cnav n° 120/82). Un décès d'octobre ouvre la
    réversion en novembre, à 50 % ; un décès de novembre, en décembre, à 52 %."""
    carriere = _carriere(simulateur, 1920, 60.0, "1925", deces)
    assert _lignes(simulateur, carriere, [("regime_general", 10000.0)], 1982) == [attendu]


def test_l_age_requis_reporte_la_date_d_effet(simulateur):
    """Cinquante-cinq ans : le conjoint de quarante-cinq ans attend le premier
    jour du mois qui suit son anniversaire (R. 353-7), au régime général comme
    à l'Agirc-Arrco, et la date d'effet choisit la version."""
    carriere = _carriere(simulateur, 1955, 62.0, "1975-03-10", "2020-06-15")
    lignes = _lignes(simulateur, carriere,
                     [("arrco", 5000.0), ("regime_general", 10000.0)], 2020)
    assert [(l[0], l[4], l[5]) for l in lignes] == [
        ("arrco", "accord_2017", "2030-04-01"),
        ("regime_general", "minimum_2026", "2030-04-01"),
    ]


@pytest.mark.parametrize("deces, attendu", [
    ("2008-06-10", ("age_51_2009", "2009-04-01")),
    ("2009-02-10", ("minimum_2012", "2013-04-01")),
])
def test_cinquante_et_un_ans_pour_le_survivant_d_un_deces_d_avant_2009(
        simulateur, deces, attendu):
    """Décret n° 2008-1509, article 2, II : le survivant d'un assuré décédé
    avant le 1er janvier 2009 garde l'âge de cinquante et un ans, « quelle que
    soit la date de dépôt de la demande » (circulaire Cnav n° 2009/11) ; décédé
    depuis, il attend cinquante-cinq ans."""
    carriere = _carriere(simulateur, 1945, 60.0, "1958-03-01", deces)
    ligne, = _lignes(simulateur, carriere, [("regime_general", 10000.0)],
                     int(deces[:4]))
    assert (ligne[4], ligne[5]) == attendu


def test_le_plafond_de_2026_est_celui_que_publie_service_public(simulateur):
    """« 25 001,60 € si vous vivez seul » : service-public.gouv.fr, fiche
    F13104, Pension de réversion de l'Assurance retraite, vérifiée le 1er
    janvier 2026 — 2 080 fois le SMIC horaire de 12,02 euros."""
    assert round(_plafond(simulateur, 2026), 2) == 25001.60


def test_le_plafond_ecrete_la_reversion(simulateur):
    """Depuis juillet 2004, la réversion est réduite à due concurrence du
    dépassement du plafond (L. 353-1) : 2 080 SMIC horaires, moins les
    ressources du survivant."""
    carriere = _carriere(simulateur, 1958, 62.0, "1960", "2023-05-10", ressources=15000.0)
    ligne, = _lignes(simulateur, carriere, [("regime_general", 20000.0)], 2023)
    assert ligne[3] == "ecretee"
    assert ligne[2] == round(_plafond(simulateur, 2023) - 15000.0, 2)


def test_avant_2004_les_ressources_ferment_le_droit(simulateur):
    """Avant juillet 2004, le plafond est une condition d'ouverture : au-dessus,
    rien n'est servi ; en dessous, tout."""
    carriere = _carriere(simulateur, 1935, 60.0, "1938", "1999-05-10",
                         ressources=_plafond(simulateur, 1999) + 1.0)
    ligne, = _lignes(simulateur, carriere, [("regime_general", 10000.0)], 1999)
    assert (ligne[2], ligne[3]) == (0.0, "ressources")


def test_la_fonction_publique_compte_au_plafond_du_regime_general(simulateur):
    """La réversion d'un autre régime de base compte aux ressources du régime
    général ; celle des complémentaires, non (R. 353-1)."""
    plafond = _plafond(simulateur, 2023)
    carriere = _carriere(simulateur, 1958, 62.0, "1960", "2023-05-10", ressources=5000.0)
    fonctionnaire = _lignes(simulateur, carriere, [
        ("fonction_publique_etat", 30000.0), ("regime_general", 10000.0)], 2023)
    assert fonctionnaire[0][2:4] == (15000.0, "servie")
    assert fonctionnaire[1][2:4] == (round(plafond - 5000.0 - 15000.0, 2), "ecretee")
    salarie = _lignes(simulateur, carriere, [
        ("arrco", 30000.0), ("regime_general", 10000.0)], 2023)
    assert salarie[1][2:4] == (5400.0, "servie")


@pytest.mark.parametrize("enfants, attendu", [(0, (0.0, "mariage")), (1, (5400.0, "servie"))])
def test_deux_ans_de_mariage_avant_2004_sauf_enfant(simulateur, enfants, attendu):
    """Avant juillet 2004, deux ans de mariage à la date du décès, sauf enfant
    issu du mariage ; l'Arrco n'en demande pas."""
    carriere = _carriere(simulateur, 1930, 60.0, "1935", "1995-03-10",
                         mariage="1994-06", enfants=enfants)
    lignes = _lignes(simulateur, carriere,
                     [("arrco", 1000.0), ("regime_general", 10000.0)], 1995)
    assert lignes[0][2:4] == (600.0, "servie")
    assert lignes[1][2:4] == attendu


# -- la fonction publique -----------------------------------------------------------

@pytest.mark.parametrize("mariage, deces, servie", [
    ("2013-05", "2015-02-10", False),
    ("2009-12", "2015-02-10", True),
    ("2013-05", "2017-06-10", True),
])
def test_l_anteriorite_du_mariage_de_la_fonction_publique(
        simulateur, mariage, deces, servie):
    """L. 39 : deux ans de services depuis le mariage, ou quatre ans de
    mariage. Marié après son départ, en 2012, le fonctionnaire mort vingt et
    un mois plus tard n'ouvre rien ; marié deux ans avant, tout ; marié quatre
    ans avant sa mort, tout."""
    carriere = _carriere(simulateur, 1950, 62.0, "1960", deces, mariage=mariage)
    ligne, = _lignes(simulateur, carriere, [("fonction_publique_etat", 30000.0)],
                     int(deces[:4]))
    assert ligne[2:4] == ((15000.0, "servie") if servie else (0.0, "mariage"))


# -- l'Agirc-Arrco -------------------------------------------------------------------

def test_l_agirc_attend_soixante_ans_avant_2019(simulateur):
    """Pour un décès d'avant 2019, l'Arrco sert la réversion à cinquante-cinq
    ans, l'Agirc à soixante — le moteur ne sert pas la réversion minorée de
    cinquante-cinq ans ; depuis 2019, cinquante-cinq ans partout."""
    carriere = _carriere(simulateur, 1945, 62.0, "1953-01-15", "2010-05-10")
    lignes = _lignes(simulateur, carriere, [("agirc", 5000.0), ("arrco", 5000.0)], 2010)
    assert [(l[0], l[4], l[5]) for l in lignes] == [
        ("agirc", "arrco_1996", "2013-02-01"), ("arrco", "arrco_1996", "2010-06-01")]
    carriere = _carriere(simulateur, 1945, 62.0, "1966-01-15", "2019-05-10")
    lignes = _lignes(simulateur, carriere, [("agirc", 5000.0)], 2019)
    assert [(l[4], l[5]) for l in lignes] == [("accord_2017", "2021-02-01")]


# -- ce qui n'est pas porté ----------------------------------------------------------

def test_un_regime_sans_fiche_le_dit_et_un_regime_vide_ne_reverse_rien(simulateur):
    carriere = _carriere(simulateur, 1957, 62.0, "1965", "2022-03-10")
    lignes = _lignes(simulateur, carriere, [("rafp", 500.0), ("ircantec", 0.0)], 2022)
    assert lignes == [("rafp", 0.0, 0.0, "non_portee", None, None)]


def test_sans_conjoint_pas_de_reversion(simulateur):
    carriere = Carriere.depuis_profil(1957, "H", "salarie_prive", 21.0, 62.0,
                                      simulateur.macro)
    assert carriere.conjoint is None and carriere.deces is None
    assert reversion(simulateur.scenario_actuel, [("regime_general", 1.0, HAUTE)],
                     carriere, 2022) is None


# -- la saisie et la simulation ------------------------------------------------------

@pytest.mark.parametrize("requete, message", [
    ({"deces": "2030"}, "« deces » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "deces": "2020"}, "il précède le départ"),
    ({"conjoint": "1962", "mariage": "1961"}, "précède la naissance"),
    ({"conjoint": "1962", "conjoint_sexe": "X"}, "Sexe du conjoint"),
    ({"conjoint": "1962-13"}, "La naissance du conjoint « 1962-13 »"),
])
def test_la_saisie_refuse_ce_qui_ne_tient_pas(requete, message):
    with pytest.raises(ErreurSaisie, match=message):
        Saisie.depuis_requete({"naissance": "1960", "liquidation": "2024-01", **requete})


def test_l_adresse_garde_le_conjoint_et_le_deces():
    from urllib.parse import parse_qsl

    saisie = Saisie.depuis_requete({
        "naissance": "1960", "liquidation": "2024-01", "conjoint": "1962-03",
        "mariage": "1985-06", "ressources_conjoint": "12000", "deces": "2031-10"})
    relue = Saisie.depuis_requete(dict(parse_qsl(saisie.requete())))
    assert (relue.conjoint, relue.mariage, relue.ressources_conjoint, relue.deces) == (
        "1962-03", "1985-06", 12000.0, "2031-10")
    assert "conjoint" not in Saisie.depuis_requete({"naissance": "1960"}).requete()


@pytest.fixture(scope="module")
def contexte() -> Contexte:
    return Contexte()


def test_le_journal_inscrit_le_deces_puis_la_reversion(contexte):
    """Le décès est un événement de l'échéancier, et la réversion la
    liquidation qu'il ouvre au survivant (§ 7.3, § 7.4) ; sans décès déclaré,
    la sortie n'a pas de clé « reversion »."""
    comparaison = contexte.simuler(Saisie.depuis_requete({
        "naissance": "1958", "liquidation": "62", "conjoint": "1960",
        "deces": "2023-05"}))
    entrees = {(e.id, e.sorte) for e in comparaison.journal}
    assert {("deces_assure", "evenement"), ("reversion_conjoint", "evenement"),
            ("liquidation_reversion_conjoint", "reversion")} <= entrees
    sortie = comparaison.dictionnaire()["reversion"]
    assert sortie["deces"] == "2023-05-01" and sortie["total"] > 0
    assert "reversion" not in contexte.simuler(Saisie.depuis_requete({
        "naissance": "1958", "liquidation": "62"})).dictionnaire()
