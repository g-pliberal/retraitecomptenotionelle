"""La réversion, régime par régime : ce que le décès de l'assuré ouvre à son conjoint.

Le domaine de la réversion (docs/architecture.md, § 11). Les versions des fiches
``reversion``, ``reversion_fonction_publique``, ``reversion_agirc_arrco``,
``reversion_rafp``, ``reversion_ircantec`` et ``reversion_rci`` se lisent sur la
date d'effet de la réversion et sur la date du décès (``droit/reversion.py``).
Ce fichier tient les bornes et les conditions que chaque version porte : la
veille et le jour d'un taux, l'âge qui reporte la date d'effet, le plafond de
ressources, la durée du mariage, le droit direct versé en capital. Les deux
moteurs, eux, sont comparés par les témoins ``reversion_*`` des simulations.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.chronologie import fait
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.droit.liquider import maximum_des_pensions
from retraite_notionnelle.droit.reversion import mois_de_mariage, reversion
from retraite_notionnelle.simulateur import Simulateur
from retraite_notionnelle.web.site import ErreurSite

from outils_pont import Saisies, refus_de_la_saisie, saisie_du_portage

HAUTE = Fiabilite.HAUTE


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _carriere(simulateur, naissance: int, depart: float, conjoint: str, deces: str,
              mariage: str | None = None, ressources: float | None = None,
              enfants: int = 0, sexe_conjoint: str = "F",
              invalidite: str | None = None, sexe: str = "H",
              naissances: tuple[str, ...] = (), activite: float | None = None,
              nouvelle_union: str | None = None, apport: float | None = None,
              ex_conjoints: tuple[dict, ...] = (), retraite: str | None = None,
              union_depuis: str | None = None, union_fin: str | None = None,
              fin_d_activite: str | None = None,
              variations: tuple[tuple[str, float], ...] = (),
              variations_de_l_apport: tuple[tuple[str, float], ...] = ()) -> Carriere:
    """Un salarié né en janvier ``naissance``, parti à ``depart`` ans, ses
    enfants nés aux dates ``naissances`` quand elles sont dites, et son
    conjoint, invalide depuis ``invalidite`` s'il est dit, ses ressources et ce
    qu'en rapporte son ``activite``, jusqu'à sa ``fin_d_activite`` si elle est
    dite, et les ``variations`` de ses revenus d'activité, la
    ``nouvelle_union`` où il vit après le décès, depuis ``union_depuis`` et
    jusqu'à ``union_fin`` s'ils sont dits, l'``apport`` de son nouveau conjoint
    et ses variations, et sa propre ``retraite``, datée ; le décès ouvre la
    réversion. Les pensions, elles, sont données à :func:`reversion` : seule
    la règle est en cause ici."""
    return Carriere.depuis_profil(
        naissance, sexe, "salarie_prive_non_cadre", 21.0, depart, simulateur.macro,
        nombre_enfants=enfants, naissances_enfants=naissances,
        conjoint={"naissance": conjoint, "sexe": sexe_conjoint, "mariage": mariage,
                  "ressources": ressources, "invalidite": invalidite,
                  "revenus_d_activite": activite, "fin_d_activite": fin_d_activite,
                  "variations_d_activite": [list(v) for v in variations],
                  "nouvelle_union": nouvelle_union,
                  "ressources_du_nouveau_conjoint": apport,
                  "nouvelle_union_depuis": union_depuis, "nouvelle_union_fin": union_fin,
                  "variations_du_nouveau_conjoint": [list(v) for v in variations_de_l_apport],
                  "retraite": retraite, "ex_conjoints": list(ex_conjoints)},
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
    ("1982-10-15", ("regime_general", 0.50, 2500.0, "servie", "avant_1982", "1982-11-01")),
    ("1982-11-10", ("regime_general", 0.52, 2600.0, "servie", "taux_52", "1982-12-01")),
])
def test_le_taux_suit_la_date_d_effet(simulateur, deces, attendu):
    """Décret n° 82-1035 : 52 % pour les réversions prenant effet à compter du
    1er décembre 1982 (circulaire Cnav n° 120/82). Un décès d'octobre ouvre la
    réversion en novembre, à 50 % ; un décès de novembre, en décembre, à 52 %. La
    pension reste sous le maximum de 1982, la moitié du plafond, 6 252 €."""
    carriere = _carriere(simulateur, 1920, 60.0, "1925", deces)
    assert _lignes(simulateur, carriere, [("regime_general", 5000.0)], 1982) == [attendu]


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
    plafond = _plafond(simulateur, 1999)
    carriere = _carriere(simulateur, 1935, 60.0, "1938", "1999-05-10",
                         ressources=plafond + 1.0, activite=plafond + 1.0)
    ligne, = _lignes(simulateur, carriere, [("regime_general", 10000.0)], 1999)
    assert (ligne[2], ligne[3]) == (0.0, "ressources")


def test_avant_2004_les_reversions_ne_comptent_pas_aux_ressources(simulateur):
    """Avant juillet 2004, les ressources personnelles du survivant, appréciées
    « sans tenir compte des avantages de réversion » (R. 353-1, rédaction de
    1990 ; exposé de la Cnav, « Condition de ressources ») : la réversion de la
    fonction publique ne ferme pas celle du régime général, que ses 15 000 €
    auraient portées au-dessus du plafond."""
    plafond = _plafond(simulateur, 1999)
    carriere = _carriere(simulateur, 1935, 60.0, "1938", "1999-05-10",
                         ressources=plafond - 1000.0, activite=plafond - 1000.0)
    lignes = _lignes(simulateur, carriere, [
        ("fonction_publique_etat", 30000.0), ("regime_general", 10000.0)], 1999)
    assert [l[2:4] for l in lignes] == [(15000.0, "servie"), (5400.0, "servie")]


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


# -- le minimum et les majorations du régime général ------------------------------------

def _servies(simulateur, carriere, pensions, annee, durees=None):
    """Chaque ligne de la réversion, sous son régime."""
    resultat = reversion(simulateur.scenario_actuel,
                         [(regime, base, HAUTE) for regime, base in pensions],
                         carriere, annee, durees=durees)
    return {r.regime: r for r in resultat.regimes}


def test_les_series_du_minimum_et_du_plafond_de_la_majoration(simulateur):
    """Les montants que D. 353-1 et D. 353-4 écrivent, et ce que la Cnav sert
    au 31 décembre de chaque année (barèmes de la caisse) : 3 983,29 € en
    2025, le minimum de la circulaire n° 2023-3 en 2023 ; 2 400 € par
    trimestre au 1er janvier 2010, 2 421,60 € depuis avril."""
    table = simulateur.scenario_actuel.reversions
    assert table.minimum(2025)[0] == 3983.29
    assert table.minimum(2023)[0] == 3701.38
    assert round(table.minimum(1982)[0], 2) == round(10_900 / 6.55957, 2)
    assert table.minimum(1940) is None
    assert table.plafond_majoration(2010)[0] == 2421.60
    assert table.plafond_majoration(2009) is None


def test_la_reversion_est_portee_au_minimum_entier_a_soixante_trimestres(simulateur):
    """D. 353-1 : la réversion ne peut être inférieure au minimum quand le défunt
    a quinze ans d'assurance au régime général — 54 % d'une petite pension, 540 €,
    deviennent 3 701,38 € en 2023. La survivante n'a pas encore l'âge du taux
    plein : la majoration de 11,1 % attend."""
    carriere = _carriere(simulateur, 1950, 62.0, "1960", "2023-05-10")
    ligne = _servies(simulateur, carriere, [("regime_general", 1000.0)], 2023,
                     {"regime_general": 80})["regime_general"]
    assert (round(ligne.montant, 2), ligne.motif, ligne.minimum) == (
        3701.38, "minimum", 3701.38)


def test_sous_soixante_trimestres_le_minimum_se_reduit_en_soixantiemes(simulateur):
    """« Lorsque cette durée est inférieure à quinze années, le montant minimum
    de base est réduit à autant de soixantièmes que l'assuré justifiait de
    trimestres d'assurance » (D. 353-1) : trente trimestres, la moitié."""
    carriere = _carriere(simulateur, 1950, 62.0, "1960", "2023-05-10")
    ligne = _servies(simulateur, carriere, [("regime_general", 1000.0)], 2023,
                     {"regime_general": 30})["regime_general"]
    assert round(ligne.montant, 2) == round(3701.38 / 2, 2)


@pytest.mark.parametrize("conjoint, deces, annee, parts", [
    ("1938", "2000-05-10", 2000, (50 / 60, 40 / 60)),
    ("1960", "2023-05-10", 2023, (50 / 90, 40 / 90)),
])
def test_depuis_juillet_2004_le_minimum_se_partage_entre_les_regimes_alignes(
        simulateur, conjoint, deces, annee, parts):
    """Avant juillet 2004, chaque régime proratise le minimum sur ses propres
    soixantièmes ; depuis, quand les régimes alignés comptent ensemble plus de
    soixante trimestres, chacun au prorata de sa durée sur leur total (exposé de
    la Cnav, « Montant - retraite de réversion » ; circulaire n° 2005-17)."""
    carriere = _carriere(simulateur, 1935, 62.0, conjoint, deces)
    minimum = simulateur.scenario_actuel.reversions.minimum(annee)[0]
    servies = _servies(simulateur, carriere,
                       [("regime_general", 1000.0), ("msa_salaries", 1000.0)], annee,
                       {"regime_general": 50, "msa_salaries": 40})
    assert (round(servies["regime_general"].montant, 2),
            round(servies["msa_salaries"].montant, 2)) == (
        round(minimum * parts[0], 2), round(minimum * parts[1], 2))


@pytest.mark.parametrize("naissance, depart, deces, annee, part", [
    (1950, 62.0, "2015-05-10", 2015, 40 / 80),
    (1960, 64.0, "2025-05-10", 2025, 1.0),
])
def test_sous_la_liquidation_unique_le_minimum_compte_tous_les_regimes_alignes(
        simulateur, naissance, depart, deces, annee, part):
    """La liquidation unique (née en 1953 et après, pensions de juillet 2017 et
    après) sert une pension pour le régime général et les salariés agricoles :
    la réversion se calcule « dans les mêmes conditions » (exposé de la Cnav),
    et quarante trimestres dans chacun valent quatre-vingts. Sans elle, chaque
    régime sert sa part du minimum, la moitié."""
    carriere = _carriere(simulateur, naissance, depart, "1966", deces)
    minimum = simulateur.scenario_actuel.reversions.minimum(annee)[0]
    ligne = _servies(simulateur, carriere, [("msa_salaries", 1000.0)], annee,
                     {"regime_general": 40, "msa_salaries": 40})["msa_salaries"]
    assert round(ligne.minimum, 2) == round(minimum * part, 2)


def test_avant_decembre_1982_le_minimum_est_servi_entier(simulateur):
    """« Avant le 01/12/1982, la retraite de réversion était portée au minimum
    AVTS entier » (exposé de la Cnav ; circulaire n° 31/75) : dix trimestres ne
    le réduisent pas."""
    carriere = _carriere(simulateur, 1920, 60.0, "1925", "1982-10-15")
    ligne = _servies(simulateur, carriere, [("regime_general", 1000.0)], 1982,
                     {"regime_general": 10})["regime_general"]
    assert round(ligne.montant, 2) == round(10_900 / 6.55957, 2)


@pytest.mark.parametrize("base, contributif, montant, motif", [
    (10000.0, 3000.0, 0.54 * 7000.0, "servie"),
    (8000.0, 2000.0, 3701.38, "minimum"),
])
def test_la_reversion_se_calcule_sans_le_minimum_contributif(
        simulateur, base, contributif, montant, motif):
    """La réversion est un pourcentage de la « pension principale » (L. 353-1),
    et le minimum contributif une « majoration » de la pension (L. 351-10) : la
    caisse prend « le montant calculé de la retraite de l'assuré décédé, avant
    comparaison au minimum et au maximum » (exposé de la Cnav, « Retraite de
    l'assuré décédé »). Le minimum de la réversion se compare à ce qui reste."""
    carriere = _carriere(simulateur, 1950, 62.0, "1960", "2023-05-10")
    ligne, = reversion(simulateur.scenario_actuel, [("regime_general", base, HAUTE)],
                       carriere, 2023, durees={"regime_general": 160},
                       minima={"regime_general": contributif}).regimes
    assert (round(ligne.montant, 2), ligne.motif, ligne.base, ligne.minimum_contributif) == (
        round(montant, 2), motif, base, contributif)


# -- les droits d'avant 1973 des artisans et des commerçants ----------------------

@pytest.mark.parametrize("deces, taux, version", [
    ("1990-05-10", 0.52, "taux_52"),
    ("2000-05-10", 0.54, "taux_54"),
])
def test_les_points_d_avant_1973_se_reversent_comme_la_pension_alignee(
        simulateur, deces, taux, version):
    """Les pensions des décrets de 1964 et de 1966 « sont accordées aux
    conjoints survivants des assurés décédés […] au titre des périodes
    d'assurance ou d'activité professionnelle non-salariée accomplies par
    l'assuré antérieurement au 1er janvier 1973, lorsque sont remplies les
    conditions fixées aux articles L. 353-1, L. 353-2, ou L. 353-3 » ; prenant
    effet depuis le 1er décembre 1982, elles « sont égales à 52 p. 100 des
    points de retraite dont bénéficiait ou eût bénéficié l'assuré décédé »,
    54 % depuis le 1er janvier 1995 (décret n° 73-937, article 9, rédactions
    de 1990 et de 1995). La veuve de l'artisan qui avait 4 000 € de points et
    6 000 € de pension alignée reçoit les deux, au même taux, à la même
    date."""
    carriere = _carriere(simulateur, 1925, 65.0, "1930", deces)
    servies = _servies(simulateur, carriere,
                       [("cancava", 6000.0), ("cancava_avant_1973", 4000.0)],
                       int(deces[:4]), {"cancava": 80, "cancava_avant_1973": 80})
    assert [(servies[regime].taux, round(servies[regime].montant, 2), servies[regime].motif,
             servies[regime].version, servies[regime].date_effet)
            for regime in ("cancava", "cancava_avant_1973")] == [
        (taux, round(taux * 6000.0, 2), "servie", version, f"{deces[:4]}-06-01"),
        (taux, round(taux * 4000.0, 2), "servie", version, f"{deces[:4]}-06-01")]


@pytest.mark.parametrize("naissance, conjoint, deces, pensions, durees, attendus", [
    (1925, "1930", "2000-05-10", [("organic", 3000.0), ("organic_avant_1973", 1000.0)],
     {"organic": 40, "organic_avant_1973": 40},
     {"organic": (2182.74, "minimum"), "organic_avant_1973": (540.0, "servie")}),
    (1925, "1930", "1990-05-10", [("cancava", 1000.0), ("cancava_avant_1973", 500.0)],
     {"cancava": 20, "cancava_avant_1973": 25},
     {"cancava": (1453.91, "minimum"), "cancava_avant_1973": (260.0, "servie")}),
    (1915, "1920", "1980-05-10", [("organic", 1000.0), ("organic_avant_1973", 1000.0)],
     {"organic": 20, "organic_avant_1973": 60},
     {"organic": (704.35, "minimum"), "organic_avant_1973": (500.0, "servie")}),
])
def test_le_minimum_compte_ensemble_les_reversions_d_avant_et_d_apres_1973(
        simulateur, naissance, conjoint, deces, pensions, durees, attendus):
    """« Pour l'application des dispositions du deuxième alinéa de l'article
    L. 353-1 relatives au montant minimum de la pension de réversion, il est
    tenu compte, le cas échéant, du montant cumulé de la pension de réversion
    allouée au titre des périodes d'assurance postérieures au 31 décembre 1972
    dont justifiait l'assuré décédé et de l'avantage de réversion alloué au
    titre des périodes d'assurance et d'activité non salariée de l'assuré
    antérieures au 1er janvier 1973 » (D. 634-14, depuis 1990 ; décret
    n° 73-937, article 7-2, depuis le 5 mars 1976). Les deux réversions n'ont
    qu'un minimum, que la réversion alignée complète, et leurs deux durées font
    ses soixantièmes, la réversion qu'il borne correspondant à toutes deux
    (D. 353-1). Le commerçant mort en 2000, quarante trimestres de chaque côté
    de 1973 : 1 620 € et 540 €, sous le minimum de 2 722,74 €, que la réversion
    alignée porte à 2 182,74 €, et non au minimum entier, ni aux 40/60 du
    minimum pour elle seule. L'artisan mort en 1990, vingt et vingt-cinq
    trimestres : les 45/60 du minimum, 1 713,91 €, moins 260 €. Avant décembre
    1982, le minimum entier : le commerçant mort en 1980, 1 204,35 € moins
    500 €."""
    carriere = _carriere(simulateur, naissance, 65.0, conjoint, deces)
    servies = _servies(simulateur, carriere, pensions, int(deces[:4]), durees)
    assert {regime: (round(ligne.montant, 2), ligne.motif)
            for regime, ligne in servies.items()} == attendus


@pytest.mark.parametrize("pensions, durees, attendus", [
    ([("rsi", 1000.0)], {"cancava": 132, "rsi": 19}, {"rsi": (3406.47, "minimum")}),
    ([("cancava_avant_1973", 100.0), ("rsi", 1000.0)],
     {"cancava_avant_1973": 12, "cancava": 132, "rsi": 19},
     {"cancava_avant_1973": (54.0, "servie"), "rsi": (3352.47, "minimum")}),
])
def test_le_minimum_suit_la_caisse_qui_succede(simulateur, pensions, durees, attendus):
    """Le RSI succède à la CANCAVA au 1er janvier 2006, et sa pension de 2012
    sert les années que celle-ci avait : elles sont sa durée, et chaque régime
    « retient, le cas échéant, le montant du minimum de base au prorata de la
    durée d'assurance accomplie en son sein » (D. 353-1, rédaction de 2004).
    Mort en 2015, l'artisan qui avait 132 trimestres à la CANCAVA et 19 au RSI
    laisse une réversion de 540 €, que le minimum entier, 3 406,47 €, relève,
    et non ses 19/151, 428,63 €, la part d'une CANCAVA qui ne sert plus rien.
    Les points d'avant 1973, liquidés avant elle, s'y joignent : 54 €, et
    3 352,47 € au RSI."""
    carriere = _carriere(simulateur, 1950, 62.0, "1952", "2015-05-10")
    servies = _servies(simulateur, carriere, pensions, 2015, durees)
    assert {regime: (round(ligne.montant, 2), ligne.motif)
            for regime, ligne in servies.items()} == attendus


def test_les_points_d_avant_1973_ne_portent_pas_la_majoration_pour_enfants(simulateur):
    """L'article 9 du décret n° 73-937 ne rend applicables aux pensions
    d'avant 1973 que les conditions de L. 353-1 à L. 353-3 et les articles
    qu'il cite, dont n'est ni R. 353-2, ni L. 353-5 : leur réversion est égale
    « à 54 % du montant des points de retraite », sans la majoration de 10 %
    du survivant de trois enfants, que la réversion alignée garde."""
    carriere = _carriere(simulateur, 1925, 65.0, "1930", "2000-05-10", enfants=3)
    servies = _servies(simulateur, carriere,
                       [("cancava", 6000.0), ("cancava_avant_1973", 4000.0)], 2000,
                       {"cancava": 80, "cancava_avant_1973": 80})
    assert [(round(servies[regime].montant, 2), servies[regime].majoration_trois_enfants)
            for regime in ("cancava", "cancava_avant_1973")] == [
        (3564.0, pytest.approx(324.0)), (2160.0, 0.0)]


def test_les_deux_moteurs_reversent_les_droits_d_avant_1973():
    """La veuve de l'artisan et celle du commerçant nés en 1928, entrés à
    vingt-cinq ans et partis à soixante-cinq, morts en 2000, et celle de
    l'artisan né en 1950, que le RSI liquide en 2012, morte en 2015 : chacune
    reçoit la réversion de ses points d'avant 1973, à 54 %, et le minimum qui
    relève la réversion alignée ne porte que leur total au minimum. Les étapes
    de la liquidation et le journal, réversion comprise, sont les mêmes dans
    les deux moteurs."""
    import json
    import shutil
    import subprocess
    import tempfile
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    from test_liquidation import RACINE, _ecarts, _python
    from test_minimum_pension_sncf import REQUETE

    requetes = [{**REQUETE, **cas} for cas in (
        {"naissance": "1928", "liquidation": "65", "statut": "artisan", "debut": "25",
         "salaire": "0.2", "conjoint": "1930", "deces": "2000-05"},
        {"naissance": "1928", "liquidation": "65", "statut": "commercant", "debut": "25",
         "salaire": "0.3", "conjoint": "1930", "deces": "2000-05"},
        {"naissance": "1950", "liquidation": "62", "statut": "artisan", "debut": "20",
         "salaire": "0.2", "conjoint": "1952", "deces": "2015-05"},
    )]
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(requetes, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-liquidation.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr[-2000:]
    obtenus, attendus = json.loads(execution.stdout), _python(requetes)
    assert not any("erreur" in attendu for attendu in attendus), attendus
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
    lignes = [{ligne["regime"]: ligne for ligne in next(
        entree["contenu"]["donnee"]["regimes"] for entree in attendu["journal"]
        if entree["id"] == "liquidation_reversion_conjoint")} for attendu in attendus]
    for reversions, (alignee, points) in zip(lignes, (
            ("cancava", "cancava_avant_1973"), ("organic", "organic_avant_1973"),
            ("rsi", "cancava_avant_1973"))):
        assert (reversions[points]["motif"], reversions[points]["montant"]) == (
            "servie", pytest.approx(0.54 * reversions[points]["base"]))
        assert reversions[alignee]["motif"] == "minimum"
        assert (reversions[alignee]["montant"] + reversions[points]["montant"]
                == pytest.approx(reversions[alignee]["minimum"]))


def test_l_echeancier_reverse_la_pension_sans_le_minimum_contributif(saisies):
    """Un petit salaire parti au taux plein et porté au minimum contributif :
    la part du minimum dans sa pension, menée au décès comme elle, n'entre pas
    dans la base, et la ligne la dit. La survivante n'a pas l'âge du taux
    plein : la majoration de 11,1 % attend, hors du montant."""
    sortie = saisies.simuler({
        "naissance": "1955", "liquidation": "67", "conjoint": "1962",
        "deces": "2024-05", "unite_revenu": "moyen", "salaire": "0.3"}).dictionnaire()
    actuel = sortie["scenarios"]["actuel"]
    minimum, = (a["montant"] for a in actuel["avantages_appliques"]
                if a["code"] == "minimum_contributif")
    pension, = (p["montant"] for p in actuel["par_regime"] if p["regime"] == "regime_general")
    ligne, = (l for l in sortie["reversion"]["regimes"] if l["regime"] == "regime_general")
    assert ligne["minimum_contributif"] == pytest.approx(ligne["base"] * minimum / pension)
    assert (ligne["motif"], ligne["montant"]) == (
        "servie", pytest.approx(0.54 * (ligne["base"] - ligne["minimum_contributif"])))


def test_trois_enfants_majorent_la_reversion_reduite_sans_descendre_sous_le_dixieme_du_minimum(
        simulateur):
    """La réversion, portée au minimum, est réduite du dépassement du plafond ;
    la majoration de 10 % s'ajoute ensuite, hors du plafond (circulaire Cnav
    n° 2022-26, § 3.6), et ne peut être inférieure au dixième du minimum de la
    réversion (R. 353-2)."""
    ressources = _plafond(simulateur, 2023) - 2000.0
    carriere = _carriere(simulateur, 1950, 62.0, "1953-01-15", "2023-05-10",
                         ressources=ressources, enfants=3)
    ligne = _servies(simulateur, carriere, [("regime_general", 6000.0)], 2023,
                     {"regime_general": 160})["regime_general"]
    assert ligne.motif == "ecretee"
    assert round(ligne.majoration_trois_enfants, 2) == round(0.10 * 3701.38, 2)
    assert round(ligne.montant, 2) == round(2000.0 + 0.10 * 3701.38, 2)


@pytest.mark.parametrize("ressources, majoration", [
    (3000.0, 0.111 * 3701.38),
    (7200.0, 4 * 2781.31 - 7200.0 - 3701.38),
    (10000.0, 0.0),
])
def test_la_majoration_de_11_1_pour_cent_sous_le_plafond(simulateur, ressources, majoration):
    """L. 353-6 et D. 353-4 : 11,1 % de la réversion, au survivant qui a l'âge
    du taux plein — soixante-six ans et deux mois pour la génération 1953 —,
    réduite de ce que ses retraites, réversion et majoration comprises,
    dépassent du plafond, 2 781,31 € par trimestre en 2023."""
    carriere = _carriere(simulateur, 1950, 62.0, "1953-01-15", "2023-05-10",
                         ressources=ressources)
    ligne = _servies(simulateur, carriere, [("regime_general", 1000.0)], 2023,
                     {"regime_general": 160})["regime_general"]
    assert round(ligne.majoration_petites_retraites, 2) == round(majoration, 2)
    assert round(ligne.montant, 2) == round(3701.38 + majoration, 2)
    if majoration:
        assert ligne.majoration_petites_retraites_effet == ligne.date_effet == "2023-06-01"


@pytest.mark.parametrize("conjoint, effet", [
    ("1960-03-10", "2027-04-01"),
    ("1960-03-01", "2027-03-01"),
])
def test_avant_l_age_du_taux_plein_la_majoration_attend(simulateur, conjoint, effet):
    """La majoration est due au premier jour du mois qui suit l'âge du taux plein
    (R. 353-13), le jour même de l'anniversaire pour qui est né le premier d'un
    mois : écrite à part, avec sa date, hors du montant que la réversion sert
    d'ici là."""
    carriere = _carriere(simulateur, 1950, 62.0, conjoint, "2023-05-10", ressources=3000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 1000.0)], 2023,
                     {"regime_general": 160})["regime_general"]
    assert round(ligne.montant, 2) == 3701.38
    assert round(ligne.majoration_petites_retraites, 2) == round(0.111 * 3701.38, 2)
    assert ligne.majoration_petites_retraites_effet == effet


def test_avant_2010_la_majoration_n_existe_pas(simulateur):
    """L. 353-6 n'est en vigueur que depuis le 1er janvier 2010 : la version d'une
    réversion de 2009 ne porte pas de taux de majoration."""
    carriere = _carriere(simulateur, 1930, 62.0, "1935-01-15", "2009-05-10",
                         ressources=1000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 1000.0)], 2009,
                     {"regime_general": 160})["regime_general"]
    assert (ligne.majoration_petites_retraites, ligne.majoration_petites_retraites_effet) == (
        0.0, None)


# -- le maximum du régime général -----------------------------------------------------

FRANC = 6.55957

#: Le barème « Montant maximum de la retraite de réversion » de la Cnav, aux dates
#: où le plafond n'a pas changé en cours d'année : (date, montant, unité).
BAREME_DU_MAXIMUM = [
    ("1958-01-01", 120_000, "AF"), ("1959-01-01", 132_000, "AF"),
    ("1962-01-01", 1_920, "F"), ("1963-01-01", 2_088, "F"), ("1964-01-01", 2_280, "F"),
    ("1965-01-01", 2_448, "F"), ("1966-01-01", 2_592, "F"), ("1967-01-01", 2_736, "F"),
    ("1968-01-01", 2_880, "F"), ("1969-01-01", 3_264, "F"), ("1970-01-01", 3_600, "F"),
    ("1971-01-01", 3_960, "F"), ("1972-01-01", 4_831.20, "F"),
    ("1973-01-01", 5_630.40, "F"), ("1974-01-01", 6_681.60, "F"),
    ("1975-01-01", 8_250, "F"), ("1976-01-01", 9_480, "F"), ("1977-01-01", 10_830, "F"),
    ("1978-01-01", 12_000, "F"), ("1979-01-01", 13_410, "F"), ("1980-01-01", 15_030, "F"),
    ("1981-01-01", 17_190, "F"), ("1997-01-01", 44_452.80, "F"),
    ("2001-01-01", 48_438, "F"), ("2002-01-01", 7_620.48, "€"),
    ("2005-01-01", 8_151.84, "€"), ("2010-01-01", 9_347.40, "€"),
    ("2012-01-01", 9_820.44, "€"), ("2020-01-01", 11_106.72, "€"),
    ("2022-01-01", 11_106.72, "€"), ("2023-01-01", 11_877.84, "€"),
    ("2025-01-01", 12_717.00, "€"), ("2026-01-01", 12_976.20, "€"),
]


@pytest.mark.parametrize("date, montant, unite", BAREME_DU_MAXIMUM)
def test_le_maximum_de_la_reversion_est_celui_du_bareme_de_la_cnav(
        simulateur, date, montant, unite):
    """« Le montant maximum de la pension principale de réversion [...] est égal à
    54 % du maximum qui était ou aurait été opposable à l'assuré décédé »
    (circulaire Cnav n° 3/95, § 13 ; 52 % à la n° 120/82, § 4) : le taux de la
    version, du maximum des pensions de la date, au plafond de l'année — le barème
    de la caisse, au franc près, le plafond du dépôt étant arrondi à l'euro. Celui
    de 1965 est 20 % du plafond de 1965, que le barème du maximum des pensions
    remplace par celui de 1966."""
    table = simulateur.scenario_actuel.reversions
    taux = float(table.version(table.fiche_du_regime("regime_general"), date, date)
                 ["parametres"]["taux"])
    maximum, _ = maximum_des_pensions(simulateur.scenario_actuel, "regime_general", date,
                                      int(date[:4]))
    euros = montant if unite == "€" else montant / FRANC / (100 if unite == "AF" else 1)
    assert taux * maximum == pytest.approx(euros, rel=1e-3)


def test_la_reversion_part_de_la_pension_d_avant_le_maximum(simulateur):
    """La caisse calcule la réversion sur la pension « sans être comparé[e] au
    minimum et au maximum » (exposé de la Cnav), et les revalorisations
    s'appliquent « sur le montant calculé » (circulaire n° 105/90, § 22) : la
    pension de 9 000 €, que le maximum avait ramenée de 10 000 €, laisse 54 % de
    10 000 € en 2005, sous le maximum de la réversion de l'année, 8 151,84 €."""
    carriere = _carriere(simulateur, 1925, 65.0, "1930", "2005-05-10")
    ligne, = reversion(simulateur.scenario_actuel, [("regime_general", 9000.0, HAUTE)],
                       carriere, 2005, maxima={"regime_general": (1000.0, 0.0, 1.0)}).regimes
    assert (round(ligne.montant, 2), ligne.motif, round(ligne.maximum, 2)) == (
        5400.0, "servie", 8151.84)
    assert ligne.ecretement_du_maximum == 1000.0


def test_la_reversion_est_ramenee_a_son_maximum(simulateur):
    """Le plafond gelé de 2020 à 2022 n'a pas suivi la revalorisation des
    pensions : la pension de 21 000 € en 2022 passe le maximum des pensions de
    l'année, 20 568 €, et sa réversion est ramenée à 54 % de lui, 11 106,72 € —
    le barème de la Cnav, la comparaison au maximum s'effectuant « à chaque
    revalorisation des retraites ou du montant maximum des retraites »."""
    carriere = _carriere(simulateur, 1955, 64.0, "1957", "2022-05-10")
    ligne, = reversion(simulateur.scenario_actuel, [("regime_general", 21000.0, HAUTE)],
                       carriere, 2022).regimes
    assert (round(ligne.montant, 2), ligne.motif) == (11106.72, "maximum")


def test_la_surcote_passe_le_maximum_de_la_reversion(simulateur):
    """« Le montant de la retraite de réversion est éventuellement ramené au
    maximum des retraites de réversion auquel s'ajoute 54 % de la surcote »
    (exposé de la Cnav ; circulaire n° 2018-4, § 5) : 2 000 € de surcote portent
    le maximum de 2022 à 11 106,72 + 1 080 €."""
    carriere = _carriere(simulateur, 1955, 64.0, "1957", "2022-05-10")
    ligne, = reversion(simulateur.scenario_actuel, [("regime_general", 23000.0, HAUTE)],
                       carriere, 2022,
                       maxima={"regime_general": (500.0, 2000.0, 1.0)}).regimes
    assert (round(ligne.montant, 2), ligne.motif) == (round(11106.72 + 1080.0, 2), "maximum")


def test_l_ajournement_d_avant_1983_majore_le_maximum_de_la_reversion(simulateur):
    """« 52% du maximum qui était ou aurait été opposable à l'assuré décédé »
    (circulaire n° 120/82, § 4) : celui de l'assuré parti à soixante-dix ans en
    1982, majoré de 1,25 % par trimestre d'ajournement (arrêté du 9 octobre 1986,
    article 2), vaut une fois et demie le maximum de soixante-cinq ans."""
    carriere = _carriere(simulateur, 1912, 70.0, "1920", "1984-05-10")
    plafond = simulateur.macro.plafond_securite_sociale(1984)
    ligne, = reversion(simulateur.scenario_actuel,
                       [("regime_general", 0.8 * plafond, HAUTE)], carriere, 1984,
                       maxima={"regime_general": (0.2 * plafond, 0.0, 1.5)}).regimes
    assert ligne.motif == "maximum"
    assert ligne.montant == pytest.approx(0.52 * 0.5 * 1.5 * plafond)


@pytest.mark.parametrize("deces, motif", [("2005-05", "servie"), ("1990-09", "maximum")])
def test_l_echeancier_reverse_la_pension_d_avant_le_maximum(saisies, simulateur, deces,
                                                             motif):
    """Le cadre parti à soixante-cinq ans en 1990, dont le salaire annuel moyen
    passait le plafond : sa pension, ramenée au maximum, laisse à sa veuve le taux
    de la pension calculée, menée jusqu'au décès comme elle ; mort en 2005, sous le
    maximum de l'année ; mort en 1990, ramenée au maximum, 52 % de la moitié du
    plafond de l'année."""
    sortie = saisies.simuler({
        "naissance": "1925", "liquidation": "65", "conjoint": "1930", "salaire": "5",
        "statut": "salarie_prive_cadre", "deces": deces}).dictionnaire()
    ligne, = (l for l in sortie["reversion"]["regimes"] if l["regime"] == "regime_general")
    assert ligne["ecretement_du_maximum"] > 0
    calculee = ligne["taux"] * (ligne["base"] + ligne["ecretement_du_maximum"])
    assert (ligne["motif"], ligne["montant"]) == (
        motif, pytest.approx(min(calculee, ligne["maximum"])))
    if motif == "maximum":
        plafond = simulateur.macro.plafond_securite_sociale(1990)
        assert ligne["maximum"] == pytest.approx(0.52 * 0.5 * plafond)


# -- le ménage et les revenus d'activité du survivant -----------------------------------

#: Le barème « Plafond de ressources pour la retraite de réversion » de la Cnav, au
#: 1er janvier de chaque année depuis 2005 : (année, personne seule, couple).
BAREME_DU_PLAFOND = [
    (2005, 15_828.80, 25_326.08), (2006, 16_702.40, 26_723.84),
    (2007, 17_201.60, 27_522.56), (2008, 17_555.20, 28_088.32),
    (2009, 18_116.80, 28_986.88), (2010, 18_428.80, 29_486.08),
    (2011, 18_720.00, 29_952.00), (2012, 19_177.60, 30_684.16),
    (2013, 19_614.40, 31_383.04), (2014, 19_822.40, 31_715.84),
    (2015, 19_988.80, 31_982.08), (2016, 20_113.60, 32_181.76),
    (2017, 20_300.80, 32_481.28), (2018, 20_550.40, 32_880.64),
    (2019, 20_862.40, 33_379.84), (2020, 21_112.00, 33_779.20),
    (2021, 21_320.00, 34_112.00), (2022, 21_985.60, 35_176.96),
    (2023, 23_441.60, 37_506.56), (2024, 24_232.00, 38_771.20),
    (2025, 24_710.40, 39_536.64), (2026, 25_001.60, 40_002.56),
]


@pytest.mark.parametrize("annee, seul, couple", BAREME_DU_PLAFOND)
def test_le_plafond_du_menage_est_celui_du_bareme_de_la_cnav(simulateur, annee, seul,
                                                             couple):
    """« Le plafond annuel de ressources du ménage [...] est fixé à 1,6 fois le
    plafond » d'une personne seule, 2 080 fois le SMIC horaire du 1er janvier
    (D. 353-1-1), et « Le plafond "couple" s'applique aux couples mariés, aux
    partenaires pacsés et aux concubins » (exposé de la Cnav, « Condition de
    ressources ») : le barème de la caisse, au centime, de 2005 à 2026 ;
    service-public le dit pour 2026, « 40 002,56 € si vous vivez en couple »."""
    for union, attendu in ((None, seul), ("mariage", couple), ("pacs", couple),
                           ("concubinage", couple)):
        carriere = _carriere(simulateur, 1938, 62.0, "1940", f"{annee}-03-10",
                             nouvelle_union=union)
        ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                         annee)["regime_general"]
        assert round(ligne.plafond, 2) == attendu


def test_le_menage_compte_les_ressources_du_nouveau_conjoint(simulateur):
    """Le survivant qui vit en couple : ses ressources et celles de son nouveau
    conjoint, ensemble, sous le plafond du ménage, et la réversion réduite de ce
    qui le dépasse (L. 353-1). Seul, avec les mêmes ressources, il la garde
    entière ; pacsé sans dire les ressources de l'autre, aussi (présomption
    ``ressources_du_survivant``)."""
    plafond = _plafond(simulateur, 2023)
    pensions = [("regime_general", 20000.0)]
    seul = _carriere(simulateur, 1958, 62.0, "1960", "2023-05-10", ressources=10000.0)
    assert _servies(simulateur, seul, pensions, 2023)["regime_general"].montant == 10800.0
    pacse = _carriere(simulateur, 1958, 62.0, "1960", "2023-05-10", ressources=10000.0,
                      nouvelle_union="pacs")
    assert _servies(simulateur, pacse, pensions, 2023)["regime_general"].montant == 10800.0
    menage = _carriere(simulateur, 1958, 62.0, "1960", "2023-05-10", ressources=10000.0,
                       nouvelle_union="pacs", apport=20000.0)
    ligne = _servies(simulateur, menage, pensions, 2023)["regime_general"]
    assert (ligne.motif, ligne.ressources_retenues) == ("ecretee", 30000.0)
    assert round(ligne.montant, 2) == round(1.6 * plafond - 30000.0, 2)


def test_avant_juillet_2004_le_menage_ne_compte_pas(simulateur):
    """Avant la loi du 21 août 2003, les ressources « personnelles » du seul
    survivant (R. 353-1, rédaction de 1990) : son nouveau conjoint n'y entre pas,
    et son plafond reste celui d'une personne seule."""
    carriere = _carriere(simulateur, 1935, 60.0, "1938", "1999-05-10", ressources=5000.0,
                         activite=5000.0, nouvelle_union="mariage", apport=50000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     1999)["regime_general"]
    assert (ligne.motif, ligne.ressources_retenues) == ("servie", 5000.0)
    assert ligne.plafond == _plafond(simulateur, 1999)


@pytest.mark.parametrize("conjoint, deces, retenues", [
    # La version de juillet 2004 : R. 353-1 n'abat rien encore.
    ("1940", "2004-09-10", 15000.0),
    # Le décret n° 2004-1447, publié le 30 décembre 2004 : 70 % du salaire.
    ("1940", "2005-02-10", 10500.0),
    # Cinquante-deux ans à la date d'effet, en 2006 : le salaire entier.
    ("1953-06", "2006-03-10", 15000.0),
    ("1960", "2023-05-10", 10500.0),
])
def test_les_revenus_d_activite_sont_abattus_a_cinquante_cinq_ans(simulateur, conjoint,
                                                                  deces, retenues):
    """« Les revenus d'activité du conjoint survivant font l'objet d'un
    abattement de 30 % s'il est âgé de 55 ans ou plus » (R. 353-1, depuis le 30
    décembre 2004), à la date d'effet, « quel que soit l'âge atteint au moment
    où ces revenus ont été perçus » (circulaire Cnav n° 2006-37, § 7)."""
    carriere = _carriere(simulateur, 1938, 62.0, conjoint, deces, ressources=15000.0,
                         activite=15000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     int(deces[:4]))["regime_general"]
    assert ligne.ressources_retenues == retenues


def test_la_majoration_de_11_1_pour_cent_ne_compte_pas_les_revenus_d_activite(simulateur):
    """L. 353-6 ne compte que les « retraites personnelles et de réversion » :
    les 7 200 € d'un salaire laissent la majoration entière, quand 7 200 € de
    retraite la réduisaient de ce qui dépasse le plafond."""
    carriere = _carriere(simulateur, 1950, 62.0, "1953-01-15", "2023-05-10",
                         ressources=7200.0, activite=7200.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 1000.0)], 2023,
                     {"regime_general": 160})["regime_general"]
    assert round(ligne.majoration_petites_retraites, 2) == round(0.111 * 3701.38, 2)


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


@pytest.mark.parametrize("mariage, deces, version, servie", [
    ("2013-05", "2015-02-10", "conjoints_2006", False),
    ("2009-12", "2015-02-10", "conjoints_2006", True),
    ("2013-05", "2017-06-10", "conjoints_2006", True),
    ("2003-05", "2005-02-10", "veuves_1990", False),
    ("1999-12", "2005-02-10", "veuves_1990", True),
])
def test_la_crpcen_reverse_la_moitie_sous_la_condition_de_mariage(
        simulateur, mariage, deces, version, servie):
    """Décret n° 90-1215, article 113 : la moitié de la pension, sans âge ni
    ressources, sous la condition de L. 39 depuis le 5 mai 2006 ; avant, à la
    veuve d'un pensionné, aux mêmes conditions de mariage. La caisse n'avait
    pas de réversion."""
    carriere = _carriere(simulateur, 1940 if deces < "2006" else 1950, 62.0, "1945"
                         if deces < "2006" else "1960", deces, mariage=mariage)
    ligne, = _lignes(simulateur, carriere, [("crpcen", 20000.0)], int(deces[:4]))
    assert ligne[0] == "crpcen" and ligne[4] == version
    assert ligne[2:4] == ((10000.0, "servie") if servie else (0.0, "mariage"))


@pytest.mark.parametrize("mariage, deces, servie", [
    # Marié avant le départ, en 2012 : aucune condition.
    ("2009-12", "2013-02-10", True),
    # Marié après, et mort moins de deux ans plus tard : rien.
    ("2013-05", "2014-02-10", False),
    # Deux ans de mariage au décès : la moitié.
    ("2013-05", "2015-06-10", True),
])
def test_les_ieg_reversent_la_moitie_sous_la_condition_de_l_article_24(
        simulateur, mariage, deces, servie):
    """Annexe 3 au statut national des IEG, articles 22 et 24 : la moitié de
    la pension, sans âge ni ressources ; le mariage contracté après la
    liquidation doit avoir duré deux ans au décès, sauf enfant de l'union. Le
    régime n'avait pas de réversion."""
    carriere = _carriere(simulateur, 1950, 62.0, "1960", deces, mariage=mariage)
    ligne, = _lignes(simulateur, carriere, [("ieg", 30000.0)], int(deces[:4]))
    assert (ligne[0], ligne[4]) == ("ieg", "conjoints_2008")
    assert ligne[2:4] == ((15000.0, "servie") if servie else (0.0, "mariage"))


def test_les_ieg_reversent_la_majoration_pour_enfants_a_moitie(simulateur):
    """« la moitié, majoration pour enfant comprise » (article 22, I)."""
    carriere = _carriere(simulateur, 1950, 62.0, "1960", "2015-06-10", mariage="2009-12")
    resultat = reversion(simulateur.scenario_actuel, [("ieg", 30000.0, HAUTE)], carriere,
                         2015, majorations={"ieg": 3000.0})
    ligne, = resultat.regimes
    assert (ligne.montant, ligne.majoration) == (15000.0 + 1500.0, 1500.0)


# -- la SNCF -------------------------------------------------------------------------

@pytest.mark.parametrize("naissance, mariage, deces, naissances, version, servie", [
    # Deux ans de mariage le jour de la cessation des fonctions, au départ de
    # février 2012 : la moitié.
    (1950, "2009-12", "2013-02-10", (), "conjoints_2008", True),
    # Vingt mois au départ, deux ans et huit mois au décès : rien.
    (1950, "2010-06", "2013-02-10", (), "conjoints_2008", False),
    # Quatre ans de mariage au décès : la moitié.
    (1950, "2010-06", "2014-07-10", (), "conjoints_2008", True),
    # Marié après le départ, un enfant né du mariage : deux ans de mariage au
    # décès suffisent, vingt et un mois non — L. 39 servirait les deux.
    (1950, "2013-05", "2015-06-10", ("2014-03-01",), "conjoints_2008", True),
    (1950, "2013-05", "2015-02-10", ("2014-03-01",), "conjoints_2008", False),
    # Un enfant né avant la cessation des fonctions lève la condition : cinq
    # mois de mariage au départ, onze au décès.
    (1950, "2011-09", "2012-08-10", ("1995-03-01",), "conjoints_2008", True),
    # Avant le 1er juillet 2008, le règlement de retraites, que l'index ne
    # porte pas : la fiche lui prête la règle de 2008.
    (1940, "1999-12", "2005-02-10", (), "avant_2008", True),
])
def test_la_sncf_reverse_la_moitie_sous_la_condition_de_l_article_19(
        simulateur, naissance, mariage, deces, naissances, version, servie):
    """Décret n° 2008-639, articles 18 et 19, I : la moitié de la pension, sans
    âge ni ressources, au conjoint marié deux ans le jour de la cessation des
    fonctions, ou quatre ans au décès, deux s'il existe un enfant issu du
    mariage ; sans durée, quand un enfant est né avant la cessation. Le régime
    n'avait pas de réversion."""
    carriere = _carriere(simulateur, naissance, 62.0, str(naissance + 10), deces,
                         mariage=mariage, enfants=len(naissances), naissances=naissances)
    ligne, = _lignes(simulateur, carriere, [("sncf", 30000.0)], int(deces[:4]))
    assert (ligne[0], ligne[4]) == ("sncf", version)
    assert ligne[2:4] == ((15000.0, "servie") if servie else (0.0, "mariage"))


def test_la_sncf_majore_la_reversion_comme_la_pension(simulateur):
    """« Les pensions de conjoints ou d'ex-conjoints sont, le cas échéant,
    majorées dans les conditions fixées à l'article 16 » (article 18) : 10 %
    de la réversion pour trois enfants, la moitié de la majoration de
    l'agent."""
    carriere = _carriere(simulateur, 1950, 62.0, "1960", "2015-06-10", mariage="2009-12")
    resultat = reversion(simulateur.scenario_actuel, [("sncf", 30000.0, HAUTE)], carriere,
                         2015, majorations={"sncf": 3000.0})
    ligne, = resultat.regimes
    assert (ligne.montant, ligne.majoration) == (15000.0 + 1500.0, 1500.0)


@pytest.mark.parametrize("union, depuis, montant, motif", [
    # En concubinage au décès, le survivant « ne peut entrer en jouissance de
    # sa pension » (article 19, I).
    ("concubinage", None, 0.0, "remariage"),
    # Remarié, pacsé ou en concubinage après le décès, il « perçoit, sans
    # revalorisation ultérieure, la pension dont il bénéficiait » (article
    # 31) : la ligne ne s'arrête pas.
    ("mariage", "2014-03", 15000.0, "servie"),
    ("pacs", "2014-03", 15000.0, "servie"),
    ("concubinage", "2014-03", 15000.0, "servie"),
])
def test_l_union_nouvelle_ne_retire_pas_la_reversion_de_la_sncf(simulateur, union, depuis,
                                                                montant, motif):
    carriere = _carriere(simulateur, 1950, 62.0, "1960", "2013-02-10", mariage="2009-12",
                         nouvelle_union=union, union_depuis=depuis)
    ligne, = reversion(simulateur.scenario_actuel, [("sncf", 30000.0, HAUTE)], carriere,
                       2013).regimes
    assert (ligne.montant, ligne.motif, ligne.fin) == (montant, motif, None)


#: Le minimum de pension de la SNCF (décret n° 2008-639, article 15, IV), par an :
#: 3 379,38 € par trimestre au 1er décembre 2008, 1 215,64 € par mois au 1er
#: octobre 2014, revalorisé entre-temps et depuis comme les pensions (article
#: 30) : 1,01 au 1er avril 2009, 1,001 au 1er octobre 2015.
MINIMUM_SNCF_2008 = 3379.38 * 4
MINIMUM_SNCF_2014 = 1215.64 * 12


@pytest.mark.parametrize("deces, annee, base, minimum, montant, motif", [
    # La pension de l'agent dépasse le minimum de pension : la réversion « ne
    # peut être inférieure » à 54 % de ce minimum, 7 877,35 €, où la moitié de
    # la pension, 7 500 €, descendrait.
    ("2014-06-10", 2014, 15000.0, 0.54 * MINIMUM_SNCF_2014, 0.54 * MINIMUM_SNCF_2014,
     "minimum"),
    # Portée au minimum, la pension en est le montant : 54 % aussi.
    ("2014-06-10", 2014, MINIMUM_SNCF_2014, 0.54 * MINIMUM_SNCF_2014,
     0.54 * MINIMUM_SNCF_2014, "minimum"),
    # La moitié au-dessus des 54 % : la moitié.
    ("2014-06-10", 2014, 16000.0, 0.54 * MINIMUM_SNCF_2014, 8000.0, "servie"),
    # Sous le minimum, que la liquidation ne lui a pas fait atteindre : la
    # moitié, sans plancher.
    ("2014-06-10", 2014, 14000.0, 0.0, 7000.0, "servie"),
    # Le minimum revalorisé de 1,001 au 1er octobre 2015.
    ("2016-03-10", 2016, 15000.0, 0.54 * MINIMUM_SNCF_2014 * 1.001,
     0.54 * MINIMUM_SNCF_2014 * 1.001, "minimum"),
    # Les taux de passage : 51,3 % au 1er juillet 2008, 52,7 % au 1er juillet
    # 2009, à la date d'effet de la réversion, le premier jour du mois qui suit
    # le décès.
    ("2008-09-10", 2008, 13600.0, 0.513 * MINIMUM_SNCF_2008, 0.513 * MINIMUM_SNCF_2008,
     "minimum"),
    ("2009-05-10", 2009, 13700.0, 0.513 * MINIMUM_SNCF_2008 * 1.01,
     0.513 * MINIMUM_SNCF_2008 * 1.01, "minimum"),
    ("2009-08-10", 2009, 13700.0, 0.527 * MINIMUM_SNCF_2008 * 1.01,
     0.527 * MINIMUM_SNCF_2008 * 1.01, "minimum"),
    # Avant le 1er juillet 2008, le règlement de retraites, que l'index ne
    # porte pas : aucun minimum lu.
    ("2005-02-10", 2005, 10000.0, 0.0, 5000.0, "servie"),
])
def test_la_reversion_de_la_sncf_ne_descend_pas_sous_54_pour_cent_du_minimum_de_pension(
        simulateur, deces, annee, base, minimum, montant, motif):
    """Décret n° 2008-639, article 18 : « Lorsque la pension de l'agent a été
    portée au montant du minimum de pension prévu à l'article 15, la pension de
    réversion est portée à 51,3 % de ce montant au 1er juillet 2008, à 52,7 %
    de ce montant au 1er juillet 2009 et à 54 % de ce montant au 1er juillet
    2010. Lorsque la pension de l'agent est supérieure au montant du minimum
    [...], la pension de réversion ne peut être inférieure à celle qui
    résulterait de l'application de l'alinéa précédent. »"""
    carriere = _carriere(simulateur, 1940, 62.0, "1945", deces, mariage="1999-12")
    ligne, = reversion(simulateur.scenario_actuel, [("sncf", base, HAUTE)], carriere,
                       annee).regimes
    assert (ligne.minimum, ligne.montant, ligne.motif) == (
        pytest.approx(minimum), pytest.approx(montant), motif)


def test_le_minimum_de_la_reversion_de_la_sncf_se_partage_et_se_majore(simulateur):
    """Le minimum est celui de la réversion entière, que le conjoint survivant
    partage avec le précédent conjoint au prorata des mariages (article 20,
    1°) : 168 mois avec le survivant, 120 avec le précédent ; la réversion
    portée au minimum est « majorée dans les conditions fixées à l'article
    16 » (article 18), 10 % de son montant pour trois enfants, le taux de la
    majoration de l'agent."""
    carriere = _carriere(simulateur, 1940, 62.0, "1945", "2014-06-10", mariage="2000-06",
                         ex_conjoints=({"naissance": "1942", "mariage": "1975-06",
                                        "divorce": "1985-06", "remariage": None},))
    ligne, = reversion(simulateur.scenario_actuel, [("sncf", 15000.0, HAUTE)], carriere,
                       2014, majorations={"sncf": 1500.0}).regimes
    part = 168 / (168 + 120)
    minimum = 0.54 * MINIMUM_SNCF_2014 * part
    assert (ligne.part, ligne.motif) == (pytest.approx(part), "minimum")
    assert (ligne.minimum, ligne.majoration) == (pytest.approx(minimum),
                                                 pytest.approx(0.10 * minimum))
    assert ligne.montant == pytest.approx(1.10 * minimum)


@pytest.mark.parametrize("remariage, part", [(None, 152 / (152 + 120)), ("1990-01", 1.0)])
def test_la_sncf_partage_avec_le_conjoint_divorce_non_remarie(simulateur, remariage, part):
    """La pension « partagée entre le conjoint survivant et le ou les conjoints
    divorcés [...] au prorata de la durée respective de chaque mariage »
    (article 20, 1°) : 152 mois avec le survivant, 120 avec le précédent
    conjoint ; celui qui s'est remarié avant le décès n'y a pas droit
    (article 19, II, 1°)."""
    carriere = _carriere(simulateur, 1950, 62.0, "1960", "2013-02-10", mariage="2000-06",
                         ex_conjoints=({"naissance": "1952", "mariage": "1975-06",
                                        "divorce": "1985-06", "remariage": remariage},))
    ligne, = reversion(simulateur.scenario_actuel, [("sncf", 30000.0, HAUTE)], carriere,
                       2013).regimes
    assert (ligne.part, ligne.montant) == (pytest.approx(part), pytest.approx(15000.0 * part))


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


def test_l_invalidite_du_survivant_leve_l_age_de_l_agirc_arrco(simulateur):
    """« La pension de réversion peut être versée sans condition d'âge quel que
    soit la date du décès : [...] s'il est en situation d'invalidité au moment
    du décès ou plus tard » (fédération Agirc-Arrco) : elle part au mois qui
    suit le décès, ou l'invalidité quand elle vient après ; le régime général
    attend toujours cinquante-cinq ans."""
    pensions = [("arrco", 5000.0), ("regime_general", 10000.0)]
    apres = _carriere(simulateur, 1955, 62.0, "1975-03-10", "2020-06-15",
                      invalidite="2022-09")
    assert [(l[0], l[5]) for l in _lignes(simulateur, apres, pensions, 2020)] == [
        ("arrco", "2022-10-01"), ("regime_general", "2030-04-01")]
    avant = _carriere(simulateur, 1955, 62.0, "1975-03-10", "2020-06-15",
                      invalidite="2018")
    assert [l[5] for l in _lignes(simulateur, avant, pensions[:1], 2020)] == ["2020-07-01"]
    # Avant 2019 aussi, à l'Agirc qui attendait soixante ans.
    agirc = _carriere(simulateur, 1945, 62.0, "1966-01-15", "2010-05-10",
                      invalidite="2012-03")
    assert [l[5] for l in _lignes(simulateur, agirc, [("agirc", 5000.0)], 2010)] == [
        "2012-04-01"]



@pytest.mark.parametrize("naissances, attendu", [
    (("2008-03", "2011-07"), "2024-05-01"),
    # L'aîné a dix-huit ans au décès : un seul enfant à charge, l'âge revient.
    (("2006-03", "2011-07"), "2027-06-01"),
])
def test_deux_enfants_a_charge_levent_l_age_de_l_agirc_arrco(simulateur, naissances, attendu):
    """Accord du 17 novembre 2017, article 110 : l'âge de cinquante-cinq ans
    « ne s'applique pas si le conjoint a au moins deux enfants à charge à la
    date du décès », de moins de dix-huit ans (article 93) ; et la réversion
    reste servie quand ils cessent de l'être (article 111)."""
    carriere = _carriere(simulateur, 1961, 62.0, "1972-05-10", "2024-04-25",
                         enfants=2, naissances=naissances)
    ligne, = _lignes(simulateur, carriere, [("agirc_arrco", 5000.0)], 2024)
    assert ligne[5] == attendu


def test_la_majoration_pour_enfants_du_defunt_est_reversee_en_entier(simulateur):
    """Article 109 : « Les majorations pour enfants nés ou élevés applicables
    aux droits du participant décédé sont réversibles au taux de 100% » :
    60 % de la retraite, et la majoration en plus. Avant 2019, le moteur ne la
    reverse pas, ce que la fiche déclare."""
    depuis = _carriere(simulateur, 1955, 62.0, "1957-03-10", "2020-06-15")
    ligne, = reversion(simulateur.scenario_actuel, [("agirc_arrco", 10000.0, HAUTE)],
                       depuis, 2020, majorations={"agirc_arrco": 1000.0}).regimes
    assert (ligne.montant, ligne.majoration) == (pytest.approx(7000.0), 1000.0)
    avant = _carriere(simulateur, 1945, 62.0, "1947-03-10", "2015-06-15")
    ligne, = reversion(simulateur.scenario_actuel, [("arrco", 10000.0, HAUTE)],
                       avant, 2015, majorations={"arrco": 1000.0}).regimes
    assert (ligne.montant, ligne.majoration) == (pytest.approx(6000.0), 0.0)


def test_l_echeancier_reverse_la_majoration_de_l_agirc_arrco(saisies):
    """La même carrière, avec trois enfants et sans : le régime général ne
    reverse pas la majoration du défunt, mais majore de 10 % la réversion du
    survivant de trois enfants (L. 353-1, R. 353-2) ; l'Agirc-Arrco reverse
    la majoration du défunt en entier."""
    def lignes(enfants):
        sortie = saisies.simuler({
            "naissance": "1958", "liquidation": "62", "conjoint": "1960",
            "deces": "2023-05", "enfants": enfants}).dictionnaire()["reversion"]
        return {l["regime"]: l for l in sortie["regimes"]}
    sans, avec = lignes("0"), lignes("3")
    assert avec["regime_general"]["majoration"] == 0.0
    assert avec["regime_general"]["majoration_trois_enfants"] == pytest.approx(
        0.10 * sans["regime_general"]["montant"])
    assert avec["regime_general"]["montant"] == pytest.approx(
        1.10 * sans["regime_general"]["montant"])
    for regime in ("arrco", "agirc_arrco"):
        assert avec[regime]["majoration"] > 0
        assert avec[regime]["montant"] == pytest.approx(
            sans[regime]["montant"] + avec[regime]["majoration"])

# -- le RAFP --------------------------------------------------------------------------

def test_le_rafp_reverse_la_moitie_sans_age_ni_duree_du_mariage(simulateur):
    """Décret n° 2004-569, article 10, et arrêté du 26 novembre 2004 : la
    moitié de la prestation, au mois qui suit le décès, sans condition d'âge,
    de ressources ni de durée du mariage — quand la pension civile attend la
    condition de L. 39, que le mariage d'après le départ ne remplit pas."""
    carriere = _carriere(simulateur, 1950, 62.0, "1985-03-10", "2015-02-10",
                         mariage="2013-05")
    lignes = _lignes(simulateur, carriere,
                     [("fonction_publique_etat", 30000.0), ("rafp", 800.0)], 2015)
    assert [(l[0], l[2], l[3], l[4], l[5]) for l in lignes] == [
        ("fonction_publique_etat", 0.0, "mariage", "conjoints_2004", "2015-03-01"),
        ("rafp", 400.0, "servie", "decret_2004", "2015-03-01")]


def test_un_droit_direct_verse_en_capital_ne_laisse_rien_a_reverser(simulateur):
    """« Aucune prestation de réversion n'est due lorsque la prestation
    additionnelle de droit direct a été servie sous forme de capital » (arrêté
    du 26 novembre 2004, article 4) : la ligne du RAFP ne s'écrit pas."""
    carriere = _carriere(simulateur, 1957, 62.0, "1965", "2022-03-10")
    pensions = [("fonction_publique_etat", 30000.0, HAUTE), ("rafp", 500.0, HAUTE)]
    capital = reversion(simulateur.scenario_actuel, pensions, carriere, 2022,
                        en_capital=frozenset({"rafp"}))
    rente = reversion(simulateur.scenario_actuel, pensions, carriere, 2022)
    assert [r.regime for r in capital.regimes] == ["fonction_publique_etat"]
    assert [(r.regime, r.montant) for r in rente.regimes] == [
        ("fonction_publique_etat", 15000.0), ("rafp", 250.0)]


@pytest.mark.parametrize("primes, en_capital", [("0.02", True), ("0.2", False)])
def test_l_echeancier_dit_quel_rafp_a_ete_verse_en_capital(saisies, primes, en_capital):
    """Aux primes d'un cinquantième du traitement, le fonctionnaire n'a pas les
    5 125 points du RAFP : il le touche en une fois (décret n° 2004-569,
    article 9), et son conjoint n'en reçoit rien ; aux primes d'un
    cinquième, une rente, dont il reçoit la moitié."""
    sortie = saisies.simuler({
        "naissance": "1958", "liquidation": "62", "statut": "fonctionnaire_etat",
        "primes": primes, "conjoint": "1960", "deces": "2023-05"}).dictionnaire()
    rafp, = [p for p in sortie["scenarios"]["actuel"]["par_regime"] if p["regime"] == "rafp"]
    assert ("versé en capital" in rafp["detail"]) is en_capital
    lignes = {r["regime"]: r for r in sortie["reversion"]["regimes"]}
    assert ("rafp" in lignes) is not en_capital
    if not en_capital:
        assert lignes["rafp"]["montant"] == pytest.approx(lignes["rafp"]["base"] / 2)


def test_le_rafp_compte_aux_ressources_du_regime_general(simulateur):
    """R. 353-1, 2°, n'écarte des ressources que les réversions des régimes
    complémentaires du régime général, des régimes agricoles, des professions
    libérales et des indépendants : celle du RAFP, complémentaire de la
    fonction publique, y compte, comme la pension civile."""
    plafond = _plafond(simulateur, 2023)
    carriere = _carriere(simulateur, 1958, 62.0, "1960", "2023-05-10", ressources=5000.0)
    lignes = _lignes(simulateur, carriere, [
        ("fonction_publique_etat", 30000.0), ("rafp", 1000.0), ("regime_general", 10000.0)],
        2023)
    assert lignes[2][2:4] == (round(plafond - 5000.0 - 15000.0 - 500.0, 2), "ecretee")


# -- l'Ircantec -----------------------------------------------------------------------

def test_l_ircantec_sert_la_moitie_a_cinquante_ans(simulateur):
    """Arrêté du 30 décembre 1970, articles 20 et 21 : la moitié des points, à
    partir de cinquante ans, au premier jour du mois qui suit ; le régime
    général attend cinquante-cinq ans."""
    carriere = _carriere(simulateur, 1955, 62.0, "1975-03-10", "2020-06-15")
    lignes = _lignes(simulateur, carriere,
                     [("ircantec", 3000.0), ("regime_general", 10000.0)], 2020)
    assert [(l[0], l[2], l[4], l[5]) for l in lignes] == [
        ("ircantec", 1500.0, "conjoints_2004", "2025-04-01"),
        ("regime_general", 5400.0, "minimum_2026", "2030-04-01")]


@pytest.mark.parametrize("naissances, attendu", [
    (("2003-05", "2006-09"), "2020-07-01"),
    (("1997-05", "2006-09"), "2025-04-01"),
])
def test_deux_enfants_de_moins_de_vingt_et_un_ans_levent_l_age_de_l_ircantec(
        simulateur, naissances, attendu):
    """Article 21 : avec deux enfants de moins de vingt et un ans à sa charge
    au décès, le conjoint reçoit l'allocation dès le décès, à tout âge ; avec
    un seul, il attend cinquante ans."""
    carriere = _carriere(simulateur, 1955, 62.0, "1975-03-10", "2020-06-15",
                         enfants=2, naissances=naissances)
    ligne, = _lignes(simulateur, carriere, [("ircantec", 3000.0)], 2020)
    assert ligne[5] == attendu


@pytest.mark.parametrize("depart, mariage, deces, enfants, servie", [
    (62.0, "2017-05", "2020-06-15", 0, False),
    (62.0, "2016-01", "2020-06-15", 0, True),
    (62.0, "2014-12", "2018-06-15", 0, True),
    (52.0, "2006-06", "2009-06-15", 0, True),
    (62.0, "2017-05", "2020-06-15", 1, True),
])
def test_la_duree_du_mariage_de_l_ircantec(simulateur, depart, mariage, deces, enfants,
                                           servie):
    """Article 20, IV : quatre ans de mariage, ou un mariage contracté deux ans
    au moins avant la cessation des fonctions — le départ, pour le modèle — ou
    avant les cinquante-cinq ans de l'agent ; sans durée, un enfant issu du
    mariage. Marié après son départ, l'agent mort trois ans plus tard n'ouvre
    rien ; marié quatre ans avant sa mort, deux ans avant son départ, ou à
    cinquante et un ans, tout ; avec un enfant, tout."""
    carriere = _carriere(simulateur, 1955, depart, "1960", deces, mariage=mariage,
                         enfants=enfants)
    ligne, = _lignes(simulateur, carriere, [("ircantec", 3000.0)], int(deces[:4]))
    assert ligne[2:4] == ((1500.0, "servie") if servie else (0.0, "mariage"))


def test_avant_2004_le_veuf_attend_soixante_ans_a_l_ircantec(simulateur):
    """De 1976 à 2003, le veuf reçoit l'allocation à soixante ans, la veuve à
    cinquante (article 20, rédactions de 1976, 1980 et 1994) ; depuis 2004, le
    conjoint à cinquante ans."""
    pensions = [("ircantec", 3000.0)]
    veuf = _carriere(simulateur, 1940, 60.0, "1945-03-10", "2001-06-15", sexe="F",
                     sexe_conjoint="H")
    veuve = _carriere(simulateur, 1940, 60.0, "1945-03-10", "2001-06-15")
    assert [(l[4], l[5]) for l in _lignes(simulateur, veuf, pensions, 2001)] == [
        ("enfant_1994", "2005-04-01")]
    assert [(l[4], l[5]) for l in _lignes(simulateur, veuve, pensions, 2001)] == [
        ("enfant_1994", "2001-07-01")]
    veuf_2004 = _carriere(simulateur, 1940, 60.0, "1945-03-10", "2004-06-15", sexe="F",
                          sexe_conjoint="H")
    assert [(l[4], l[5]) for l in _lignes(simulateur, veuf_2004, pensions, 2004)] == [
        ("conjoints_2004", "2004-07-01")]


# -- la complémentaire des indépendants ------------------------------------------------

def test_la_rci_sert_soixante_pour_cent_a_cinquante_cinq_ans(simulateur):
    """Règlement approuvé par l'arrêté du 9 février 2012, articles 17, 19 et
    34 : 60 % des points, à l'âge de L. 353-1, cinquante-cinq ans, les points
    repris en 2013 des régimes des artisans et des commerçants comme les
    autres."""
    carriere = _carriere(simulateur, 1955, 62.0, "1975-03-10", "2020-06-15")
    lignes = _lignes(simulateur, carriere, [("rci", 2000.0), ("rco_artisans", 3000.0)], 2020)
    assert [(l[0], l[2], l[3], l[4], l[5]) for l in lignes] == [
        ("rci", 1200.0, "servie", "reglement_2013", "2030-04-01"),
        ("rco_artisans", 1800.0, "servie", "reglement_2013", "2030-04-01")]


def test_le_plafond_de_la_rci_compte_les_reversions_des_regimes_de_base(simulateur):
    """Articles 17 et 35 : les ressources, appréciées comme celles de R. 353-1,
    comptent les réversions des régimes de base ; leur dépassement de deux
    plafonds annuels de la Sécurité sociale, 96 120 euros en 2026 (circulaire
    Cnav n° 2026-01, § 9), réduit les réversions de la RCI à due concurrence,
    au prorata de chacune."""
    plafond = 2 * simulateur.macro.plafond_securite_sociale(2026)
    assert plafond == 96120.0
    carriere = _carriere(simulateur, 1958, 62.0, "1960", "2026-05-10",
                         ressources=plafond - 20000.0)
    lignes = _lignes(simulateur, carriere, [
        ("fonction_publique_etat", 30000.0), ("rci", 4000.0), ("nric", 6000.0)], 2026)
    # 15 000 euros de pension civile et 6 000 de réversions brutes : 1 000 de
    # trop, imputés pour deux cinquièmes et trois cinquièmes.
    assert [(l[0], l[2], l[3], l[4]) for l in lignes] == [
        ("fonction_publique_etat", 15000.0, "servie", "complement_aspa_2025"),
        ("rci", 2000.0, "ecretee", "plafond_2021"),
        ("nric", 3000.0, "ecretee", "plafond_2021")]


def test_la_rci_compte_le_menage_sous_le_meme_plafond(simulateur):
    """Article 17 : des ressources « personnelles ou du ménage », appréciées
    selon R. 353-1 — les revenus d'activité abattus de 30 % à cinquante-cinq
    ans —, sous le plafond que le CPSTI fixe, sans plafond propre au ménage :
    deux plafonds annuels de la Sécurité sociale en 2026."""
    plafond = 2 * simulateur.macro.plafond_securite_sociale(2026)
    carriere = _carriere(simulateur, 1958, 62.0, "1960", "2026-05-10",
                         ressources=plafond - 30000.0, activite=10000.0,
                         nouvelle_union="concubinage", apport=31000.0)
    ligne = _servies(simulateur, carriere, [("rci", 4000.0)], 2026)["rci"]
    # 63 120 euros au survivant, son salaire abattu, 31 000 à son concubin et
    # 2 400 de réversion : 400 de trop.
    assert (ligne.plafond, ligne.ressources_retenues) == (plafond, plafond - 2000.0)
    assert (round(ligne.montant, 2), ligne.motif) == (2000.0, "ecretee")


# -- l'âge d'avant 1973, le cumul d'avant 2004, les majorations forfaitaires -------------

@pytest.mark.parametrize("conjoint, invalidite, version, date_effet", [
    # Cinquante-cinq ans en juin 1970 : soixante-cinq ans alors, cinquante-cinq
    # au 1er janvier 1973, « au plus tôt » (décret n° 72-1098, article 5).
    ("1915-06-10", None, "avant_juillet_1974", "1973-01-01"),
    # Soixante-cinq ans en juin 1971.
    ("1906-06-10", None, "avant_1973", "1971-07-01"),
    # Soixante et un ans, inapte : soixante ans suffisent.
    ("1908-06-10", "1969-01-01", "avant_1973", "1970-04-01"),
])
def test_avant_1973_la_reversion_attend_soixante_cinq_ans(simulateur, conjoint, invalidite,
                                                           version, date_effet):
    carriere = _carriere(simulateur, 1910, 60.0, conjoint, "1970-03-10",
                         invalidite=invalidite)
    ligne = _servies(simulateur, carriere, [("regime_general", 500.0)],
                     1970)["regime_general"]
    assert (ligne.version, ligne.date_effet) == (version, date_effet)


def test_avant_juillet_1974_la_reversion_complete_la_retraite_personnelle(simulateur):
    """Avant la loi n° 75-3, en vigueur au 1er juillet 1974, la réversion ne
    se cumule pas avec une retraite personnelle : elle la complète (exposé de
    la Cnav, « Retraite de réversion cumulable »)."""
    carriere = _carriere(simulateur, 1905, 60.0, "1910", "1973-03-10", ressources=300.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 1000.0)],
                     1973)["regime_general"]
    assert (round(ligne.montant, 2), ligne.motif, ligne.limite_cumul) == (200.0, "cumul", 0.0)


@pytest.mark.parametrize("retraites, montant, motif, limite", [
    # 5 400 € de réversion et 6 000 € de retraite : la limite forfaitaire de
    # 1999, 73 % du maximum des pensions, au-dessus de 52 % des 16 000 €.
    (6000.0, 3662.01, "cumul", 9662.01),
    # 20 000 € de retraite : 52 % de 30 000 €, 15 600 €, que la retraite
    # dépasse avec la réversion de plus que la réversion même.
    (20000.0, 0.0, "cumul", 15600.0),
    # 2 000 € : sous la limite, la réversion entière.
    (2000.0, 5400.0, "servie", 9662.01),
])
def test_avant_2004_la_reversion_se_cumule_dans_une_limite(simulateur, retraites, montant,
                                                         motif, limite):
    """D. 355-1 : la réversion se cumule avec les retraites personnelles du
    survivant dans la limite de 52 % de leur total et de la pension du défunt,
    pas moins que 73 % du maximum des pensions ; ces retraites, elles, ne
    comptent plus aux ressources."""
    carriere = _carriere(simulateur, 1930, 60.0, "1935-06-10", "1999-03-10",
                         ressources=retraites)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     1999)["regime_general"]
    assert (round(ligne.montant, 2), ligne.motif, round(ligne.limite_cumul, 2)) == (
        montant, motif, limite)
    assert ligne.ressources_retenues == 0.0
    assert ligne.limite_cumul >= simulateur.scenario_actuel.reversions.limite_cumul(1999)[0] - 0.01


def test_la_limite_forfaitaire_est_celle_de_la_cnav(simulateur):
    """Le barème de la Cnav : 6 300 F au 1er juillet 1974, 73 % du maximum des
    pensions, 17 541,90 € en 2026 (24 030 € × 0,73)."""
    table = simulateur.scenario_actuel.reversions
    assert table.limite_cumul(1973) is None
    assert round(table.limite_cumul(1974)[0], 2) == round(6300 / 6.55957, 2)
    assert table.limite_cumul(2026)[0] == 17541.90
    assert table.majoration_enfant(1987) is None
    assert round(table.majoration_enfant(1988)[0], 2) == round(12 * 405.20 / 6.55957, 2)
    assert table.majoration_enfant(2025)[0] == pytest.approx(12 * 112.58)


@pytest.mark.parametrize("deces, base, attendues", [
    # Attribuée en 1980, au taux de 50 % : 4 % en décembre 1982, puis 3,846 %
    # du montant majoré en 1995 — 54 % au bout du compte.
    ("1980-03-10", 4000.0, (("1982-12-01", 80.0), ("1995-01-01", 80.0))),
    # Attribuée en 1990, au taux de 52 % : 3,846 % en 1995.
    ("1990-03-10", 8000.0, (("1995-01-01", 160.0),)),
    # La même, portée au minimum, que 3,846 % ne dépassent pas : rien.
    ("1990-03-10", 4000.0, (("1995-01-01", 0.0),)),
    # Attribuée en 1999, au taux de 54 % : aucune.
    ("1999-03-10", 8000.0, ()),
])
def test_les_majorations_forfaitaires_de_1982_et_de_1995(simulateur, deces, base, attendues):
    """La réversion attribuée avant le 1er décembre 1982 « a été majorée de
    4 % », celle d'avant le 1er janvier 1995 « de 3,846 % » (exposé de la Cnav,
    « Montant - retraite de réversion ») : à leur date, hors du montant."""
    carriere = _carriere(simulateur, 1918, 60.0, "1920-06-10", deces)
    ligne = _servies(simulateur, carriere, [("regime_general", base)],
                     int(deces[:4]))["regime_general"]
    assert tuple((jour, round(montant)) for jour, montant
                 in ligne.majorations_forfaitaires) == attendues


def test_la_majoration_forfaitaire_pour_enfant_a_charge(simulateur):
    """L. 353-5 : au survivant sans retraite personnelle, par enfant de moins
    de seize ans en 1997, le montant de R. 353-11 ; rien quand il a une
    retraite."""
    sans = _carriere(simulateur, 1935, 60.0, "1940-06-10", "1997-03-10", ressources=0.0,
                     naissances=("1985-01-01",), enfants=1)
    ligne = _servies(simulateur, sans, [("regime_general", 6000.0)], 1997)["regime_general"]
    par_enfant = simulateur.scenario_actuel.reversions.majoration_enfant(1997)[0]
    assert ligne.majoration_forfaitaire_enfants == par_enfant
    assert round(ligne.montant, 2) == round(3240.0 + par_enfant, 2)
    avec = _carriere(simulateur, 1935, 60.0, "1940-06-10", "1997-03-10", ressources=3000.0,
                     naissances=("1985-01-01",), enfants=1)
    assert _servies(simulateur, avec, [("regime_general", 6000.0)],
                    1997)["regime_general"].majoration_forfaitaire_enfants == 0.0


@pytest.mark.parametrize("naissances, enfants", [
    # Depuis 2016, l'enfant mineur (R. 161-4) : seize et dix-sept ans comptent.
    (("2013-01-01", "2014-01-01", "2020-01-01"), 3),
    # Dix-huit ans passés : plus à charge.
    (("2011-01-01",), 0),
])
def test_depuis_2016_l_enfant_mineur_est_a_charge(simulateur, naissances, enfants):
    carriere = _carriere(simulateur, 1975, 60.0, "1975-06-10", "2030-03-10",
                         naissances=naissances, enfants=len(naissances))
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2026)["regime_general"]
    par_enfant = simulateur.scenario_actuel.reversions.majoration_enfant(2026)[0]
    assert ligne.majoration_forfaitaire_enfants == pytest.approx(enfants * par_enfant)


def test_la_majoration_pour_enfant_suit_la_reversion_reduite(simulateur):
    """« MFE réduite = montant de la majoration × (Retraite de réversion réduite
    ÷ Retraite de réversion entière) » (exposé de la Cnav ; D. 353-2)."""
    # Un salaire de 1,3 fois le plafond, abattu de 30 % : 0,91 plafond.
    salaire = 1.3 * _plafond(simulateur, 2026)
    carriere = _carriere(simulateur, 1965, 60.0, "1970-06-10", "2026-03-10",
                         ressources=salaire, activite=salaire,
                         naissances=("2015-01-01",), enfants=1)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2026)["regime_general"]
    par_enfant = simulateur.scenario_actuel.reversions.majoration_enfant(2026)[0]
    reduite = ligne.montant - ligne.majoration_forfaitaire_enfants
    assert ligne.motif == "ecretee" and reduite < 5400.0
    assert ligne.majoration_forfaitaire_enfants == pytest.approx(par_enfant * reduite / 5400.0)


def test_l_exemple_chiffre_de_2026(simulateur):
    """Aucune caisse ne publie d'exemple : celui-ci se pose à la main. La veuve
    de cinquante-six ans d'un assuré mort en mars 2026, qui gagne 30 000 € par
    an et élève leurs deux enfants de treize et neuf ans, a droit à 54 % des
    10 000 € de sa pension, 5 400 € ; ses revenus d'activité comptent pour 70 %,
    21 000 €, sous le plafond de 25 001,60 € (service-public, fiche F13104,
    vérifiée le 1er janvier 2026) : sa réversion est réduite à 4 001,60 €
    (L. 353-1). La majoration de 113,59 € par mois et par enfant (barème de la
    Cnav au 1er janvier 2026) l'est « dans les mêmes proportions » (D. 353-2) :
    2 × 12 × 113,59 × 4 001,60 / 5 400, soit 2 020,19 € par an."""
    carriere = _carriere(simulateur, 1960, 64.0, "1970-01-10", "2026-03-10",
                         ressources=30000.0, activite=30000.0,
                         naissances=("2012-06-01", "2016-09-01"), enfants=2)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2026)["regime_general"]
    reduite = 25001.60 - 0.70 * 30000.0
    assert ligne.montant - ligne.majoration_forfaitaire_enfants == pytest.approx(reduite)
    assert ligne.majoration_forfaitaire_enfants == pytest.approx(
        2 * 12 * 113.59 * reduite / 5400.0)
    assert round(ligne.majoration_forfaitaire_enfants, 2) == 2020.19


def test_a_l_age_du_taux_plein_pas_de_majoration_pour_enfant(simulateur):
    """R. 353-9 depuis juin 2011 : le survivant qui a l'âge du taux plein à la
    demande n'a pas la majoration."""
    carriere = _carriere(simulateur, 1950, 62.0, "1945-06-10", "2020-03-10",
                         naissances=("2008-01-01",), enfants=1)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2020)["regime_general"]
    assert ligne.majoration_forfaitaire_enfants == 0.0


@pytest.mark.parametrize("naissances, etapes", [
    # Seize ans en mai 2014, avant 2016 : sa part cesse le 1er juin ; mineur
    # au 1er janvier 2016, il redevient à charge, et sa part revient le 1er
    # février, jusqu'au mois qui suit ses dix-huit ans. L'autre, qui n'a pas
    # seize ans au 1er janvier 2016, compte jusqu'à sa majorité.
    (("1998-05-17", "2003-02-01"),
     (("2014-06-01", 1), ("2016-02-01", 2), ("2016-06-01", 1), ("2021-03-01", 0))),
    # Seize ans en décembre 2015 : sa part cesse au 1er janvier 2016, et revient
    # le 1er février, jusqu'à sa majorité.
    (("1999-12-20",), (("2016-01-01", 0), ("2016-02-01", 1), ("2018-01-01", 0))),
    # Des jumeaux : une seule étape ; majeurs en 2016, rien ne revient.
    (("1996-05-17", "1996-05-17"), (("2012-06-01", 0),)),
])
def test_la_majoration_pour_enfant_cesse_avec_la_charge_du_dernier_enfant(
        simulateur, naissances, etapes):
    """« Date de cessation du versement : 1er jour du mois suivant celui au
    cours duquel l'une des conditions d'attribution n'est plus satisfaite » ;
    l'enfant « n'est plus à charge le jour de son » anniversaire (circulaire
    Cnav n° 76/88, fiche n° 9) — seize ans avant 2016, la majorité depuis
    (R. 353-9, R. 313-12, R. 161-4). Le 1er janvier 2016, R. 353-9 renvoie à
    R. 161-4 (décret n° 2015-1865, article 10, 18°, en vigueur ce jour-là,
    article 12) : l'enfant de seize ou dix-sept ans redevient à charge, et
    « La majoration est alors payée à compter du premier jour du mois suivant
    la date à laquelle l'ensemble des conditions sont à nouveau remplies »
    (circulaire n° 76/88, § 6 ; R. 353-10)."""
    carriere = _carriere(simulateur, 1950, 60.0, "1955-01-10", "2010-03-10", ressources=0.0,
                         naissances=naissances, enfants=len(naissances))
    ligne = _servies(simulateur, carriere, [("regime_general", 6000.0)],
                     2010)["regime_general"]
    par_enfant = simulateur.scenario_actuel.reversions.majoration_enfant(2010)[0]
    assert ligne.majoration_forfaitaire_enfants == pytest.approx(len(naissances) * par_enfant)
    assert tuple((jour, round(montant / par_enfant)) for jour, montant
                 in ligne.majoration_forfaitaire_enfants_etapes) == etapes


def test_la_majoration_pour_enfant_cesse_avec_sa_propre_retraite(simulateur):
    """« La majoration est supprimée lors de l'attribution de la retraite
    personnelle » (exposé de la Cnav), le premier jour du mois qui suit
    (circulaire n° 76/88, fiche n° 9). Le survivant qui ne l'a pas encore à la
    date d'effet la reçoit, quoiqu'il déclare des ressources hors de son
    activité, que le modèle tient pour cette retraite ; sans la date, elles
    sont servies dès la date d'effet, et il n'en a pas."""
    def ligne(retraite):
        carriere = _carriere(simulateur, 1950, 60.0, "1955-01-10", "2010-03-10",
                             ressources=4000.0, naissances=("2003-02-01",), enfants=1,
                             retraite=retraite)
        return _servies(simulateur, carriere, [("regime_general", 6000.0)],
                        2010)["regime_general"]
    par_enfant = simulateur.scenario_actuel.reversions.majoration_enfant(2010)[0]
    datee = ligne("2013-04")
    assert datee.majoration_forfaitaire_enfants == pytest.approx(par_enfant)
    assert datee.majoration_forfaitaire_enfants_etapes == (("2013-05-01", 0.0),)
    assert ligne(None).majoration_forfaitaire_enfants == 0.0


@pytest.mark.parametrize("union, fin", [
    # En concubinage en 2001 : la majoration s'arrête le mois suivant.
    ("2001-09", "2001-10-01"),
    # En 2005, l'union ne l'arrête plus : l'enfant de 1990 a seize ans en 2006.
    ("2005-09", "2006-03-01"),
])
def test_avant_juillet_2004_l_union_nouvelle_arrete_la_majoration_pour_enfant(
        simulateur, union, fin):
    """« La majoration n'était plus servie si le bénéficiaire se remariait ou
    vivait maritalement » avant juillet 2004 (exposé de la Cnav, « Conditions
    d'attribution »)."""
    carriere = _carriere(simulateur, 1935, 60.0, "1940-01-10", "1997-03-10", ressources=0.0,
                         naissances=("1990-02-01",), enfants=1,
                         nouvelle_union="concubinage", union_depuis=union)
    ligne = _servies(simulateur, carriere, [("regime_general", 6000.0)],
                     1997)["regime_general"]
    assert ligne.majoration_forfaitaire_enfants > 0
    assert ligne.majoration_forfaitaire_enfants_etapes == ((fin, 0.0),)


@pytest.mark.parametrize("fin, servie", [(None, False), ("1993-09", True)])
def test_avant_juillet_2004_l_union_defaite_avant_l_attribution_ne_refuse_pas_la_majoration(
        simulateur, fin, servie):
    """Le survivant qui « vit maritalement » le jour où la majoration pour
    enfant s'attribuerait ne l'a pas, avant juillet 2004 (exposé de la Cnav,
    « Conditions d'attribution ») ; celui dont l'union s'est défaite avant ce
    jour vit seul (lettre de la Cnav du 18 avril 2007). La veuve, née en
    janvier 1940, d'un assuré mort en 1990 a sa réversion à cinquante-cinq
    ans, le 1er février 1995, et son enfant de 1985 est alors à sa charge,
    jusqu'à ses seize ans : en concubinage depuis 1991, elle n'a pas la
    majoration ; séparée en septembre 1993, si, jusqu'au mois qui suit les
    seize ans de l'enfant."""
    carriere = _carriere(simulateur, 1930, 60.0, "1940-01-10", "1990-03-10", ressources=0.0,
                         naissances=("1985-02-01",), enfants=1,
                         nouvelle_union="concubinage", union_depuis="1991-06", union_fin=fin)
    ligne = _servies(simulateur, carriere, [("regime_general", 6000.0)],
                     1990)["regime_general"]
    assert ligne.date_effet == "1995-02-01"
    if not servie:
        assert ligne.majoration_forfaitaire_enfants == 0.0
        return
    assert ligne.majoration_forfaitaire_enfants > 0
    assert ligne.majoration_forfaitaire_enfants_etapes == (("2001-03-01", 0.0),)


def test_l_enfant_ne_apres_la_date_d_effet_a_sa_part_le_mois_qui_suit(simulateur):
    """« La majoration est due à la date d'entrée en jouissance de la pension
    de réversion si, à cette date, les conditions d'ouverture du droit à cette
    majoration sont remplies ou à compter du premier jour du mois suivant la
    date à laquelle ces conditions sont satisfaites » (R. 353-10). La veuve de
    cinquante et un ans d'un assuré mort en juin 2008 a sa réversion le 1er
    juillet ; l'enfant né le 15 décembre lui ouvre la majoration le 1er janvier
    2009, jusqu'au mois qui suit sa majorité, en décembre 2026."""
    carriere = _carriere(simulateur, 1950, 60.0, "1957-01-10", "2008-06-10", ressources=0.0,
                         naissances=("2008-12-15",), enfants=1)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2008)["regime_general"]
    par_enfant = simulateur.scenario_actuel.reversions.majoration_enfant(2008)[0]
    assert ligne.date_effet == "2008-07-01"
    assert ligne.majoration_forfaitaire_enfants == 0.0
    assert ligne.montant == pytest.approx(5400.0)
    assert tuple((jour, round(montant / par_enfant)) for jour, montant
                 in ligne.majoration_forfaitaire_enfants_etapes) == (
        ("2009-01-01", 1), ("2027-01-01", 0))


@pytest.mark.parametrize("conjoint, etapes", [
    # Cinquante-sept ans au 1er janvier 1988 : la majoration de l'enfant de
    # douze ans, jusqu'au mois qui suit ses seize ans.
    ("1930-01-10", (("1988-01-01", 1), ("1991-03-01", 0))),
    # Soixante-cinq ans ce jour-là : rien (R. 353-9).
    ("1922-06-10", ()),
])
def test_la_majoration_de_1988_s_ajoute_aux_reversions_deja_servies(
        simulateur, conjoint, etapes):
    """« La majoration est attribuée au plus tôt le 1er janvier 1988 », et la
    caisse l'a demandée aux titulaires d'une réversion « âgés de moins de 65
    ans dont le point de départ de la prestation se situe au plus tard le 1er
    janvier 1988 » (circulaire Cnav n° 76/88, § 3 et 31) : la veuve d'un
    assuré mort en mars 1986, servie depuis avril, la reçoit le 1er janvier
    1988 pour l'enfant né en 1975 — 400 francs par mois ce jour-là (R. 353-11),
    ramenés aux euros de 1986 par les coefficients des pensions."""
    carriere = _carriere(simulateur, 1925, 60.0, conjoint, "1986-03-10", ressources=0.0,
                         naissances=("1975-02-01",), enfants=1)
    ligne = _servies(simulateur, carriere, [("regime_general", 6000.0)],
                     1986)["regime_general"]
    assert ligne.majoration_forfaitaire_enfants == 0.0
    table = simulateur.scenario_actuel.reversions
    coefficient, _ = simulateur.scenario_actuel.revalorisations_pensions.generale(
        date(1986, 12, 31), date(1988, 12, 31), False, None)
    par_enfant = table.majoration_enfant(1988)[0] / coefficient
    assert tuple((jour, round(montant / par_enfant, 9)) for jour, montant
                 in ligne.majoration_forfaitaire_enfants_etapes) == etapes


def _avec_les_faits(simulateur, carriere: Carriere, *faits: dict) -> Carriere:
    """La même carrière, sa chronologie augmentée de ``faits``."""
    chronologie = {**carriere.chronologie, "faits": [*carriere.chronologie["faits"], *faits]}
    return Carriere.depuis_chronologie(chronologie, simulateur.macro)


@pytest.mark.parametrize("deces, conjoint, naissance, faits, etapes", [
    # Avant 2016, le lycéen né en mars 1990 reste à charge après ses seize ans,
    # jusqu'à la fin de ses études en juin 2009 : sa part cesse le 1er août, et
    # non le 1er avril 2006.
    ("2003-03-10", "1945-01-10", "1990-03-15",
     [("periode_d_etudes", "2005-09-01", "2009-07-01", {})], (("2009-08-01", 0),)),
    # Depuis 2016, l'étudiant né en mai 2004, sans fin d'études dite, jusqu'à
    # ses vingt ans : le 1er juin 2024, et non le 1er juin 2022.
    ("2015-03-10", "1960-01-10", "2004-05-20",
     [("periode_d_etudes", "2020-09-01", None, {})], (("2024-06-01", 0),)),
    # L'apprenti, son contrat de dix-sept à dix-neuf ans : jusqu'à sa fin.
    ("2015-03-10", "1960-01-10", "2004-05-20",
     [("periode_d_activite", "2021-09-01", "2023-09-01",
       {"affiliation": "salarie_prive_non_cadre", "apprentissage": True})],
     (("2023-10-01", 0),)),
    # L'enfant infirme : jusqu'à ses vingt ans.
    ("2003-03-10", "1945-01-10", "1990-03-15",
     [("decision_medicale", "1998-01-01", None, {"decision": "infirmite"})],
     (("2010-04-01", 0),)),
])
def test_l_etudiant_l_apprenti_et_l_enfant_infirme_restent_a_charge_jusqu_a_vingt_ans(
        simulateur, deces, conjoint, naissance, faits, etapes):
    """« La limite d'âge est fixée à vingt ans pour les enfants qui poursuivent
    leurs études et pour ceux qui sont, par suite d'infirmités ou de maladies
    chroniques, dans l'impossibilité permanente de se livrer à un travail
    salarié » (R. 313-12, jusqu'en 2015) ; « La limite d'âge prévue au 2° de
    l'article L. 161-1 est fixée à vingt ans » (R. 161-4, depuis) ; l'apprenti,
    à charge « jusqu'à 20 ans (au lieu de 18) » depuis la circulaire Cnav
    n° 44/94, est tenu pour étudiant depuis 2016 (exposé de la Cnav, « Qualité
    d'enfant à charge »). La charge cesse quand la condition cesse, au plus
    tard le jour des vingt ans (circulaire n° 76/88, fiche n° 4)."""
    carriere = _carriere(simulateur, 1940 if deces < "2010" else 1955, 60.0, conjoint, deces,
                         ressources=0.0, naissances=(naissance,), enfants=1)
    sans = _servies(simulateur, carriere, [("regime_general", 6000.0)],
                    int(deces[:4]))["regime_general"]
    prolongee = _avec_les_faits(simulateur, carriere, *(
        fait(f"prolongation_{rang}", "enfant_1", sorte, debut, fin, attributs)
        for rang, (sorte, debut, fin, attributs) in enumerate(faits, 1)))
    ligne = _servies(simulateur, prolongee, [("regime_general", 6000.0)],
                     int(deces[:4]))["regime_general"]
    assert ligne.majoration_forfaitaire_enfants == sans.majoration_forfaitaire_enfants > 0
    assert sans.majoration_forfaitaire_enfants_etapes != ligne.majoration_forfaitaire_enfants_etapes
    assert tuple((jour, round(montant / ligne.majoration_forfaitaire_enfants)) for jour, montant
                 in ligne.majoration_forfaitaire_enfants_etapes) == etapes


@pytest.mark.parametrize("metiers, pensions, servant", [
    # Salarié, puis artisan à quarante-cinq ans : le RSI.
    (("salarie_prive_non_cadre", "artisan"),
     [("regime_general", 6000.0), ("rsi", 4000.0)], "rsi"),
    # Salarié agricole, puis salarié de l'industrie : le régime général, qui
    # n'est pas le premier de la liquidation.
    (("salarie_agricole", "salarie_prive_non_cadre"),
     [("msa_salaries", 6000.0), ("regime_general", 4000.0)], "regime_general"),
    # Salarié, puis salarié agricole : la MSA, non le régime général.
    (("salarie_prive_non_cadre", "salarie_agricole"),
     [("regime_general", 6000.0), ("msa_salaries", 4000.0)], "msa_salaries"),
])
def test_la_majoration_pour_enfant_est_servie_par_le_regime_de_la_derniere_affiliation(
        simulateur, metiers, pensions, servant):
    """« La majoration de pension de réversion prévue à l'article L. 353-5 [...]
    est accordée, par priorité, par le régime auquel l'assuré a été affilié en
    dernier lieu si ce régime sert la majoration » (D. 173-21-1 de 1988 à
    2017, D. 173-21-7 jusqu'en 2025, R. 173-17-3 depuis) : la veuve d'un
    assuré qui a changé de métier à quarante-cinq ans la reçoit de la caisse
    du second, entière, et rien de l'autre."""
    carriere = Carriere.depuis_parcours(
        1950, "H", [Metier(metiers[0], 21.0), Metier(metiers[1], 45.0)], 60.0,
        simulateur.macro, nombre_enfants=1, naissances_enfants=("2000-01-01",),
        conjoint={"naissance": "1955-01-10", "sexe": "F", "ressources": 0.0},
        deces="2010-03-10")
    lignes = _servies(simulateur, carriere, pensions, 2010)
    par_enfant = simulateur.scenario_actuel.reversions.majoration_enfant(2010)[0]
    assert {regime: ligne.majoration_forfaitaire_enfants
            for regime, ligne in lignes.items()} == {
        regime: (pytest.approx(par_enfant) if regime == servant else 0.0)
        for regime, _ in pensions}


#: Des saisies où la majoration pour enfant change après la date d'effet de la
#: réversion — l'enfant de seize ans que la majorité de 2016 rend de nouveau à
#: charge, l'enfant né après le décès de son père, mort avant son départ, la
#: réversion de 1986 que la majoration de 1988 rejoint —, ou que sert le
#: régime de la dernière affiliation : le salarié devenu artisan, et celui
#: devenu salarié agricole, sous la liquidation unique. Chacune avec le
#: régime qui la sert, et si elle croît après la date d'effet.
CAS_DE_LA_MAJORATION_POUR_ENFANT = [
    ({"naissance": "1950", "liquidation": "60", "conjoint": "1955-01", "deces": "2010-03",
      "enfants": "2", "naissances": "1998-05, 2003-02"}, "regime_general", True),
    ({"naissance": "1960", "liquidation": "64", "conjoint": "1957-01", "deces": "2008-06",
      "enfants": "1", "naissances": "2008-12"}, "regime_general", True),
    ({"naissance": "1925", "liquidation": "60", "conjoint": "1930-01", "deces": "1986-03",
      "enfants": "1", "naissances": "1975-02"}, "regime_general", True),
    ({"naissance": "1950", "liquidation": "60", "conjoint": "1955-01", "deces": "2010-03",
      "enfants": "1", "naissances": "2000-01", "metier2_debut": "1995-01",
      "metier2_statut": "artisan"}, "rsi", False),
    ({"naissance": "1955", "liquidation": "62", "conjoint": "1960-01", "deces": "2019-03",
      "enfants": "1", "naissances": "2008-01", "metier2_debut": "2000-01",
      "metier2_statut": "salarie_agricole"}, "msa_salaries", False),
]


def test_les_deux_moteurs_servent_la_meme_majoration_pour_enfant(saisies):
    """Le résultat entier, des six scénarios, est le même en Python et en
    JavaScript ; chaque cas sert la majoration du régime qu'il dit, et la voit
    croître après la date d'effet quand il le dit."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(racine / "scripts"))
    from construire_temoins import _fini
    attendus = [{"requete": cas, "resultat": _fini(saisies.simuler(cas).dictionnaire())}
                for cas, _, _ in CAS_DE_LA_MAJORATION_POUR_ENFANT]
    for attendu, (_, servant, croit) in zip(attendus, CAS_DE_LA_MAJORATION_POUR_ENFANT):
        lignes = attendu["resultat"]["reversion"]["regimes"]
        assert {r["regime"] for r in lignes if r["majoration_forfaitaire_enfants_etapes"]} == {
            servant}, lignes
        ligne, = (r for r in lignes if r["regime"] == servant)
        montants = [ligne["majoration_forfaitaire_enfants"]] + [
            etape["montant"] for etape in ligne["majoration_forfaitaire_enfants_etapes"]]
        assert any(apres > avant for avant, apres in zip(montants, montants[1:])) is croit, ligne
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(json.dumps(attendus, ensure_ascii=False))
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(racine / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]


def test_la_limite_de_cumul_s_applique_quand_sa_retraite_suit_la_reversion(simulateur):
    """« Les règles de cumul s'appliquaient à la date d'attribution du 2e
    avantage : soit au point de départ de l'avantage personnel s'il était
    attribué après la retraite de réversion » (exposé de la Cnav, « Retraite de
    réversion cumulable ») : la réversion de juin 1999 est servie entière
    jusqu'en mars 2001, puis réduite par la limite de ce jour — la limite
    forfaitaire de 2001, ramenée aux euros de 1999 par les coefficients des
    pensions, au-dessus de 52 % de sa retraite et de la pension du défunt."""
    def ligne(retraite):
        carriere = _carriere(simulateur, 1930, 60.0, "1940-06-10", "1999-03-10",
                             ressources=6000.0, retraite=retraite)
        return _servies(simulateur, carriere, [("regime_general", 10000.0)],
                        1999)["regime_general"]
    revue = ligne("2001-03")
    assert (round(revue.montant, 2), revue.motif, revue.cumul_effet) == (
        5400.0, "servie", "2001-03-01")
    assert (revue.revision_effet, revue.derniere_revision) == (None, None)
    moteur = simulateur.scenario_actuel
    coefficient, _ = moteur.revalorisations_pensions.generale(
        date(1999, 12, 31), date(2001, 12, 31), False, None)
    forfaitaire = moteur.reversions.limite_cumul(2001)[0] / coefficient
    assert forfaitaire > 0.52 * (6000.0 + 10000.0)
    assert revue.limite_cumul == pytest.approx(forfaitaire)
    assert revue.reduction_du_cumul == pytest.approx(5400.0 + 6000.0 - forfaitaire)
    # Sans la date de sa retraite, la limite de 1999 dès la date d'effet.
    d_emblee = ligne(None)
    assert (d_emblee.motif, d_emblee.cumul_effet, d_emblee.reduction_du_cumul) == (
        "cumul", None, 0.0)
    # Prise en 2005, sa retraite recalcule la réversion aux règles de
    # ressources de 2004, sans limite de cumul : sous le plafond de 2005, la
    # réversion reste entière.
    tardive = ligne("2005-01")
    assert (round(tardive.montant, 2), tardive.cumul_effet, tardive.limite_cumul) == (
        5400.0, None, 0.0)
    assert (tardive.revision_effet, tardive.reduction_de_la_revision) == ("2005-01-01", 0.0)


@pytest.mark.parametrize("retraite, reduction", [
    # Avant le 15 novembre 1990, la pension du défunt est tenue pour la
    # réversion servie rapportée à 52 % : la limite laisse 52 % de la
    # retraite, et en retire 48 %.
    ("1990-08", 0.48 * 7000.0),
    # Depuis, pour celle qui a servi de base à la réversion : 52 % de
    # 37 000 €, au-dessus de la retraite et de la réversion ramenée au maximum.
    ("1991-01", 0.0),
])
def test_avant_le_15_novembre_1990_la_limite_revue_lit_la_reversion_servie(
        simulateur, retraite, reduction):
    """Circulaire Cnav n° 105/90, § 12 et 13 : la « mesure de simplification »
    qui tenait la pension du défunt pour « 100/52èmes de la pension de
    réversion effectivement servie », abandonnée le 15 novembre 1990, pèse
    sur la réversion ramenée au maximum."""
    carriere = _carriere(simulateur, 1925, 60.0, "1928-06-10", "1988-11-10",
                         ressources=7000.0, retraite=retraite)
    ligne = _servies(simulateur, carriere, [("regime_general", 30000.0)],
                     1988)["regime_general"]
    assert ligne.motif == "maximum"
    assert ligne.reduction_du_cumul == pytest.approx(reduction)


def test_l_exemple_de_la_circulaire_105_90():
    """Circulaire Cnav n° 105/90, § 13 : la réversion court depuis le 1er
    janvier 1989, la retraite personnelle, 50 000 F, depuis le 1er août 1990 ;
    la pension du défunt, 63 000 F au 1er janvier 1989, « amenée à la valeur
    juillet 1990 soit 63.000 F x 1,012 x 1,0215 x 1,013 », fait 65 973 F, et
    « la limite de cumul au 1er août 1990 est égale à : (65.973 + 50.000) x
    52 % = 60.305 F ». Les coefficients des pensions entre les deux dates sont
    ceux que le modèle lit, et sa limite, la même."""
    from retraite_notionnelle.droit.reversion import _cumuler
    moteur = Simulateur().scenario_actuel
    coefficient, _ = moteur.revalorisations_pensions.generale(
        date(1989, 1, 1), date(1990, 8, 1), False, None)
    assert coefficient == pytest.approx(1.012 * 1.0215 * 1.013)
    principale = round(63000 * coefficient)
    assert principale == 65973
    _, limite = _cumuler({"cumul": "limite", "cumul_taux": 0.52}, 0.52 * 62040 * coefficient,
                         50000.0, principale, None, 1)
    assert int(limite) == 60305


# -- la réversion revue à la retraite du survivant (L. 353-1, R. 353-1-1) --------------

def _coefficient(simulateur, depuis: int, jusqu_a: int) -> float:
    """Les coefficients des pensions du 31 décembre de ``depuis`` à celui de
    ``jusqu_a`` ; en 2020, ceux des pensions de 2 000 € par mois au plus, que
    passe la seule réversion du survivant de 2019."""
    return simulateur.scenario_actuel.revalorisations_pensions.generale(
        date(depuis, 12, 31), date(jusqu_a, 12, 31), False, 0.0)[0]


def test_sa_retraite_prise_depuis_juillet_2004_recalcule_la_reversion_aux_ressources(
        simulateur):
    """« Si un avantage personnel était attribué à partir du 01/07/2004, la
    retraite de réversion était recalculée compte tenu des règles de
    ressources applicables depuis le 01/07/2004 » (exposé de la Cnav,
    « Retraite de réversion cumulable »), « à compter de la date d'effet de
    l'avantage personnel » (circulaire Cnav n° 2005-17, § 31), la limite de
    cumul supprimée avec elles (lettre ministérielle du 22 mars 2005, § 1). La
    veuve de 1999, née en 1940, prend sa retraite en juillet 2005 : sa
    réversion de 5 400 €, servie entière depuis 1999, se mesure alors au
    plafond de 2005, 2 080 fois le SMIC horaire du 1er janvier, 7,61 €, ramené
    aux euros de 1999 par les coefficients des pensions, ses 12 000 € de
    retraites comptés, et n'est plus révisable trois mois après (R. 353-1-1)."""
    carriere = _carriere(simulateur, 1930, 60.0, "1940-06-10", "1999-03-10",
                         ressources=12000.0, retraite="2005-07")
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     1999)["regime_general"]
    plafond = 2080 * 7.61 / _coefficient(simulateur, 1999, 2005)
    assert (round(ligne.montant, 2), ligne.motif, ligne.cumul_effet) == (
        5400.0, "servie", None)
    assert (ligne.revision_effet, ligne.derniere_revision) == ("2005-07-01", "2005-10-01")
    assert ligne.reduction_de_la_revision == pytest.approx(5400.0 - (plafond - 12000.0))


@pytest.mark.parametrize("enfants", [0, 3])
def test_sa_retraite_revise_la_reversion_le_mois_qui_suit_pour_la_derniere_fois(
        simulateur, enfants):
    """La réversion attribuée depuis juillet 2004 « est révisable en cas de
    variation dans le montant des ressources », et « la date de la dernière
    révision ne peut être postérieure » de trois mois à celle où le survivant
    « est entré en jouissance de l'ensemble des avantages personnels de
    retraite » (R. 353-1-1) : sa retraite la révise « à compter du premier
    jour du mois qui suit la date d'effet de cet avantage », la dernière
    révision trois mois après elle (circulaire Cnav n° 2010/58, § 22 et 24 :
    retraites au 1er janvier 2008, révision au 1er février, « dernière
    révision (cristallisation) » au 1er avril). Les ressources sont celles des
    trois mois qui précèdent chaque révision (exposé de la Cnav, « Condition
    de ressources »), « les sommes réellement perçues au titre du nouvel
    avantage » (§ 22). Le veuf de 2015, né en 1958, prend sa retraite en
    juillet 2020 : en août, sous le plafond de 2020, 2 080 fois 10,15 €,
    ramené aux euros de 2015, un seul des trois mois porte ses 18 000 € de
    retraites, 6 000 € par an, et sa réversion reste entière ; le 1er
    octobre, les trois portent ses retraites, et la dernière révision la
    réduit. La majoration de 10 % des trois enfants suit la réversion revue,
    sans descendre sous le dixième du minimum de 2015 (R. 353-2)."""
    carriere = _carriere(simulateur, 1955, 60.0, "1958-06-10", "2015-03-10",
                         ressources=18000.0, retraite="2020-07", enfants=enfants)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2015)["regime_general"]
    plafond = 2080 * 10.15 / _coefficient(simulateur, 2015, 2020)
    assert plafond - 18000.0 / 3 > 5400.0
    revue = plafond - 18000.0
    minimum = simulateur.scenario_actuel.reversions.minimum(2015)[0]
    majorations = (540.0, max(0.1 * revue, 0.1 * minimum)) if enfants else (0.0, 0.0)
    assert (round(ligne.montant, 2), ligne.motif) == (5400.0 + majorations[0], "servie")
    assert [jour for jour, _ in ligne.revisions] == ["2020-08-01", "2020-10-01"]
    assert ligne.revisions[0][1] == pytest.approx(0.0)
    assert (ligne.revision_effet, ligne.derniere_revision) == ("2020-10-01", "2020-10-01")
    assert ligne.reduction_de_la_revision == pytest.approx(
        5400.0 + majorations[0] - revue - majorations[1])
    assert [ressources for _, ressources in ligne.ressources_des_revisions] == [
        pytest.approx(6000.0), pytest.approx(18000.0)]


@pytest.mark.parametrize("depuis, fin, menage", [
    ("2018-05", None, True), ("2021-01", None, False),
    # Défait avant sa retraite, le ménage ne compte plus à la révision qu'elle
    # ouvre : il vit seul.
    ("2018-05", "2019-11", False),
])
def test_la_revision_compte_le_menage_forme_avant_elle(simulateur, depuis, fin, menage):
    """L'union que le survivant forme après la date d'effet ne compte pas à
    celle-ci ; « le remariage du bénéficiaire entraîne la révision de la
    retraite de réversion pour tenir compte des ressources du nouveau
    ménage » (exposé de la Cnav, « Condition de ressources ») : formé avant sa
    retraite, le ménage compte à la révision qu'elle ouvre, sous le plafond
    du ménage, et n'y compte plus s'il s'est défait avant elle (lettre de la
    Cnav du 18 avril 2007). Formé après la dernière révision, il ne change plus
    rien : « A partir de cette date de dernière révision, aucun changement de
    ressources ou de situation familiale n'est pris en compte »."""
    carriere = _carriere(simulateur, 1955, 60.0, "1958-06-10", "2015-03-10",
                         ressources=18000.0, retraite="2020-07", nouvelle_union="mariage",
                         union_depuis=depuis, union_fin=fin, apport=12000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2015)["regime_general"]
    plafond = 2080 * 10.15 / _coefficient(simulateur, 2015, 2020)
    revue = 1.6 * plafond - 30000.0 if menage else plafond - 18000.0
    assert (round(ligne.montant, 2), ligne.ressources_retenues) == (5400.0, 0.0)
    assert ligne.reduction_de_la_revision == pytest.approx(5400.0 - revue)


def _dernier_smic_publie() -> tuple[int, float]:
    """La dernière année du barème du SMIC horaire, et son montant du 1er
    janvier, tels que le fichier de la source les écrit."""
    chemin = Path(__file__).resolve().parents[1] / "data" / "reference" / "macro" / (
        "smic_horaire.csv")
    lignes = [ligne.split(",") for ligne in chemin.read_text(encoding="utf-8").splitlines()
              if ligne and ligne[0].isdigit()]
    return int(lignes[-1][0]), float(lignes[-1][1])


def test_une_revision_a_venir_se_mesure_au_dernier_smic_publie(simulateur):
    """Les montants d'une réversion sont ceux d'une année passée, ou de
    l'année courante, où s'arrêtent les revalorisations publiées : la
    révision qu'ouvrira la retraite de 2030 se mesure au plafond de la
    dernière année dont le barème publie le SMIC, ramené aux euros de l'année
    des montants, non à un SMIC projeté."""
    carriere = _carriere(simulateur, 1960, 62.0, "1964-03-10", "2024-05-10",
                         ressources=20000.0, retraite="2030-01")
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2024)["regime_general"]
    annee, smic = _dernier_smic_publie()
    plafond = 2080 * smic / _coefficient(simulateur, 2024, annee)
    assert [jour for jour, _ in ligne.revisions] == ["2030-02-01", "2030-04-01"]
    assert (ligne.revision_effet, ligne.derniere_revision) == ("2030-04-01", "2030-04-01")
    assert ligne.reduction_de_la_revision == pytest.approx(5400.0 - (plafond - 20000.0))


@pytest.mark.parametrize("retraite, derniere", [
    # Sans retraite datée, ses retraites sont servies dès la date d'effet,
    # depuis plus de trois mois (présomption ``retraites_du_survivant_servies``) :
    # la réversion n'est plus révisable dès elle.
    (None, "2015-04-01"),
    # Servies depuis plus de trois mois à la date d'effet, la réversion
    # « n'est plus révisable dès son point de départ » (circulaire Cnav
    # n° 2010/58, § 24).
    ("2014-01", "2015-04-01"),
    # Depuis moins, elle l'est jusqu'à trois mois après elles (R. 353-1-1).
    ("2015-02", "2015-05-01"),
])
def test_sa_retraite_avant_la_date_d_effet_ne_la_revise_pas(simulateur, retraite, derniere):
    """Ses retraites, servies à la date d'effet, comptent à ses ressources dès
    elle : rien ne revoit plus la réversion, que sa dernière révision fige."""
    carriere = _carriere(simulateur, 1950, 60.0, "1950-06-10", "2015-03-10",
                         ressources=18000.0, retraite=retraite)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2015)["regime_general"]
    assert (round(ligne.montant, 2), ligne.motif) == (
        round(_plafond(simulateur, 2015) - 18000.0, 2), "ecretee")
    assert (ligne.revision_effet, ligne.reduction_de_la_revision, ligne.derniere_revision) == (
        None, 0.0, derniere)


# -- la réversion révisée avant la retraite du survivant, ou sans elle (R. 353-1-1) ----

def test_le_menage_qu_il_forme_avant_sa_retraite_la_revise_le_mois_qui_suit(simulateur):
    """« En cas de modification des ressources, la retraite de réversion
    attribuée à partir du 01/07/2004 est révisée à partir du 1er jour du mois
    qui suit la date de modification des ressources », et « le remariage du
    bénéficiaire entraîne la révision de la retraite de réversion pour tenir
    compte des ressources du nouveau ménage » (exposé de la Cnav, « Condition
    de ressources » ; circulaire Cnav n° 2010/58, § 21). Le veuf de 2015, né
    en 1958, travaille : ses 15 000 € de salaire, abattus de 30 %, laissent sa
    réversion entière sous le plafond de 2015. Il se remarie en mai 2018 : en
    juin, le plafond du ménage de 2018, 1,6 fois 2 080 fois 9,88 €, ramené
    aux euros de 2015, compte aussi les 20 000 € de sa nouvelle épouse. Ayant
    travaillé sans avoir liquidé ses retraites, il garde une réversion
    « révisable jusqu'à ce que ces droits soient liquidés » (circulaire Cnav
    n° 2007-35, § 222) : pas de dernière révision."""
    carriere = _carriere(simulateur, 1955, 60.0, "1958-06-10", "2015-03-10",
                         ressources=15000.0, activite=15000.0, nouvelle_union="mariage",
                         union_depuis="2018-05", apport=20000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2015)["regime_general"]
    assert (round(ligne.montant, 2), ligne.motif, ligne.ressources_retenues) == (
        5400.0, "servie", pytest.approx(0.7 * 15000.0))
    revue = 1.6 * 2080 * 9.88 / _coefficient(simulateur, 2015, 2018) - (0.7 * 15000.0 + 20000.0)
    assert 0.0 < revue < 5400.0
    assert [jour for jour, _ in ligne.revisions] == ["2018-06-01"]
    assert ligne.revisions[0][1] == pytest.approx(5400.0 - revue)
    assert (ligne.revision_effet, ligne.derniere_revision) == ("2018-06-01", None)
    assert ligne.reduction_de_la_revision == pytest.approx(5400.0 - revue)


@pytest.mark.parametrize("depuis, revision", [
    # Formé avant son âge légal, le ménage révise la réversion le mois qui suit.
    ("2014-09", "2014-10-01"),
    # Formé le mois où elle l'atteint, au jour de sa dernière révision.
    ("2014-10", "2014-11-01"),
    # Formé le jour de sa dernière révision, il ne change plus rien.
    ("2014-11", None),
])
def test_sans_retraite_ni_activite_la_derniere_revision_tombe_a_son_age_legal(
        simulateur, depuis, revision):
    """« La date de la dernière révision ne peut être postérieure [...]
    lorsque le conjoint survivant ne peut prétendre à de tels avantages, à la
    date à laquelle il atteint l'âge » de L. 161-17-2 (R. 353-1-1, b, depuis
    le 3 juin 2011) : la réversion « n'est plus révisable [...] à compter du
    1er jour du mois qui suit l'âge légal de la retraite du demandeur, s'il
    n'a pas droit à des retraites personnelles », et, depuis, « aucun
    changement de ressources ou de situation familiale n'est pris en compte »
    (exposé « Condition de ressources »). La veuve de 2010, née le 17 août
    1953, sans ressources, est tenue pour n'avoir jamais travaillé
    (présomption ``survivant_sans_droit_propre``) : soixante et un ans et deux
    mois pour sa génération (circulaire Cnav n° 2012/25, annexe 1), le 17
    octobre 2014, sa réversion figée au 1er novembre. Remariée en septembre,
    elle voit sa réversion révisée en octobre sous le plafond du ménage de
    2014, 1,6 fois 2 080 fois 9,53 €, ramené aux euros de 2010, ses 28 000 €
    comptés ; remariée en octobre, au 1er novembre, « date d'effet de la
    dernière révision » (circulaire Cnav n° 2005/17, § 322) ; remariée en
    novembre, non."""
    carriere = _carriere(simulateur, 1945, 60.0, "1953-08-17", "2010-03-10",
                         nouvelle_union="mariage", union_depuis=depuis, apport=28000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2010)["regime_general"]
    assert (round(ligne.montant, 2), ligne.motif, ligne.derniere_revision) == (
        5400.0, "servie", "2014-11-01")
    if revision is None:
        assert (ligne.revisions, ligne.revision_effet, ligne.reduction_de_la_revision) == (
            (), None, 0.0)
        return
    revue = 1.6 * 2080 * 9.53 / _coefficient(simulateur, 2010, 2014) - 28000.0
    assert 0.0 < revue < 5400.0
    assert [jour for jour, _ in ligne.revisions] == [revision]
    assert ligne.reduction_de_la_revision == pytest.approx(5400.0 - revue)


@pytest.mark.parametrize("naissance, derniere", [
    # « Assurés nés avant le 1er juillet 1951 : 60 ans » ; puis soixante ans
    # et quatre mois, neuf mois, soixante et un ans et deux mois, et sept
    # mois ; soixante-deux ans dès 1955 (circulaire Cnav n° 2012/25,
    # annexe 1).
    ("1950-03-10", "2010-04-01"),
    ("1951-09-10", "2012-02-01"),
    ("1952-05-10", "2013-03-01"),
    ("1953-08-17", "2014-11-01"),
    ("1954-02-10", "2015-10-01"),
    ("1955-06-10", "2017-07-01"),
    # Né le premier d'un mois, il atteint l'âge ce jour-là : la réversion est
    # figée au premier jour du mois qui suit.
    ("1955-07-01", "2017-08-01"),
])
def test_l_age_de_la_derniere_revision_suit_sa_generation(simulateur, naissance, derniere):
    """La cristallisation de la réversion du survivant qui ne peut prétendre à
    aucune retraite « doit, dans un tel cas, être fixée entre 60 ans et 62
    ans, selon la date de naissance de l'assuré, conformément au tableau
    figurant en annexe 1 » (circulaire Cnav n° 2012/25, § 1), au premier jour
    du mois qui suit. Le défunt meurt en mars 2008 ; la réversion court dès
    avril, chacun ayant cinquante et un ans."""
    carriere = _carriere(simulateur, 1945, 60.0, naissance, "2008-03-10")
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2008)["regime_general"]
    assert (ligne.date_effet, ligne.derniere_revision, ligne.revisions) == (
        "2008-04-01", derniere, ())


def test_le_menage_qu_il_forme_dans_les_trois_mois_de_sa_retraite_la_revise_encore(
        simulateur):
    """Sa retraite révise la réversion le mois qui suit, et la dernière
    révision vient trois mois après elle (R. 353-1-1 ; circulaire Cnav
    n° 2010/58, § 22 et 24) : le veuf de 2015, retraité en juillet 2020, voit
    sa réversion révisée en août sous le plafond de 2020, un mois de ses
    18 000 € de retraites compté, et elle reste entière. Remarié le 20 août,
    avant le 1er octobre, il la voit révisée en septembre sous le plafond du
    ménage, 1,6 fois plus haut, les 12 000 € de sa nouvelle épouse comptés :
    la situation familiale changée dans les trois mois, les ressources
    d'après le 20 août sont transposées sur les trois (circulaire Cnav
    n° 2005/17, § 146), ses retraites entières. La dernière révision, le 1er
    octobre, transpose les mêmes, et ne change rien : elle n'est pas écrite.
    La ligne dit chaque révision ; ``revision_effet`` et
    ``reduction_de_la_revision``, la dernière."""
    carriere = _carriere(simulateur, 1955, 60.0, "1958-06-10", "2015-03-10",
                         ressources=18000.0, retraite="2020-07", nouvelle_union="mariage",
                         union_depuis="2020-08-20", apport=12000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2015)["regime_general"]
    plafond = 2080 * 10.15 / _coefficient(simulateur, 2015, 2020)
    seul, menage = plafond - 18000.0 / 3, min(5400.0, 1.6 * plafond - 30000.0)
    assert 0.0 < menage < 5400.0 < seul
    assert [jour for jour, _ in ligne.revisions] == ["2020-08-01", "2020-09-01"]
    assert [reduction for _, reduction in ligne.revisions] == [
        pytest.approx(0.0), pytest.approx(5400.0 - menage)]
    assert [ressources for _, ressources in ligne.ressources_des_revisions] == [
        pytest.approx(6000.0), pytest.approx(30000.0)]
    assert (ligne.revision_effet, ligne.derniere_revision) == ("2020-09-01", "2020-10-01")
    assert ligne.reduction_de_la_revision == pytest.approx(5400.0 - menage)


def test_ses_cinquante_cinq_ans_revisent_la_reversion_par_l_abattement(simulateur):
    """Les revenus d'activité du survivant « font l'objet d'un abattement de
    30 % s'il est âgé de 55 ans ou plus » (R. 353-1), quel que soit l'âge où
    il les a perçus (circulaire Cnav n° 2006-37, § 7) ; « pour appliquer cette
    mesure aux pensions de réversion en cours de service », la caisse
    interroge le survivant à cinquante-cinq ans (circulaire Cnav n° 2007-35,
    § 221), et la révise au premier jour du mois qui suit (circulaire Cnav
    n° 2010/58, § 21). La veuve de 2006, née le 15 septembre 1953, a
    cinquante-trois ans à sa date d'effet : ses 14 000 € de salaire, entiers,
    réduisent sa réversion sous le plafond de 2006, 2 080 fois 8,03 €. Le 15
    septembre 2008, l'abattement les ramène à 9 800 € : en octobre, sous le
    plafond de 2008, sa réversion redevient entière."""
    carriere = _carriere(simulateur, 1945, 60.0, "1953-09-15", "2006-10-10",
                         ressources=14000.0, activite=14000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2006)["regime_general"]
    reduite = 2080 * 8.03 - 14000.0
    assert (ligne.date_effet, round(ligne.montant, 2), ligne.motif) == (
        "2006-11-01", round(reduite, 2), "ecretee")
    assert 2080 * 8.44 / _coefficient(simulateur, 2006, 2008) - 0.7 * 14000.0 > 5400.0
    assert [jour for jour, _ in ligne.revisions] == ["2008-10-01"]
    assert ligne.reduction_de_la_revision == pytest.approx(reduite - 5400.0)
    assert ligne.derniere_revision is None


def test_avant_juillet_2004_le_menage_qu_il_forme_ne_la_revise_pas(simulateur):
    """La réversion attribuée avant le 1er juillet 2004 n'est révisée aux
    règles de ressources que par une retraite personnelle prise depuis ;
    « dans tous les autres cas », elle « continue d'être servie selon les
    règles applicables avant cette date » (exposé « Condition de
    ressources » ; lettre ministérielle du 22 mars 2005, § 1) : la veuve de
    1999 qui se remarie en 2006 la garde telle quelle, et quand ce ménage se
    défait, en 2008, aussi."""
    def ligne(**union):
        carriere = _carriere(simulateur, 1930, 60.0, "1940-06-10", "1999-03-10",
                             ressources=6000.0, **union)
        return _servies(simulateur, carriere, [("regime_general", 10000.0)],
                        1999)["regime_general"]
    seule = ligne()
    for remariee in (ligne(nouvelle_union="mariage", union_depuis="2006-05", apport=30000.0),
                     ligne(nouvelle_union="mariage", union_depuis="2006-05",
                           union_fin="2008-02", apport=30000.0)):
        assert (remariee.montant, remariee.motif) == (seule.montant, seule.motif)
        assert (remariee.revisions, remariee.revision_effet,
                remariee.derniere_revision) == ((), None, None)


# -- la réversion révisée quand le ménage se défait, ou que l'activité cesse ---------

def test_le_menage_qui_se_defait_revise_la_reversion_sous_le_plafond_d_une_personne_seule(
        simulateur):
    """« En cas de modification des ressources, la retraite de réversion
    attribuée à partir du 01/07/2004 est révisée à partir du 1er jour du mois
    qui suit la date de modification des ressources » (exposé de la Cnav,
    « Condition de ressources » ; circulaire Cnav n° 2010/58, § 21). Le
    divorce, la résiliation d'un pacs, la fin du concubinage, le décès du
    nouveau conjoint changent la situation familiale, et avec elle « le
    plafond de ressources à retenir (personne seule ou ménage) » et « le
    montant des ressources elles-mêmes » (lettre de la Cnav du 18 avril
    2007) : « le salaire du conjoint doit être ignoré, et le décompte doit
    s'effectuer en retenant le plafond de ressources personne seule »
    (circulaire Cnav n° 2005/17, § 146). Le veuf de 2015, né en 1958, gagne
    25 000 €, abattus de 30 % : sa réversion est écrêtée sous le plafond de
    2015, 2 080 fois 9,61 €. Pacsé en septembre 2015, il la voit révisée en
    octobre sous le plafond du ménage, 1,6 fois plus haut, les 10 000 € de son
    partenaire comptés ; le pacs rompu en mars 2021, elle l'est encore en
    avril, sous le plafond d'une personne seule de 2021, 2 080 fois 10,25 €,
    ramené aux euros de 2015, ses seuls revenus comptés. Ayant travaillé sans
    avoir liquidé ses retraites, il la garde révisable."""
    carriere = _carriere(simulateur, 1955, 60.0, "1958-06-10", "2015-03-10",
                         ressources=25000.0, activite=25000.0, nouvelle_union="pacs",
                         union_depuis="2015-09", union_fin="2021-03", apport=10000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2015)["regime_general"]
    seul = 2080 * 9.61 - 0.7 * 25000.0
    menage = 1.6 * 2080 * 9.61 - (0.7 * 25000.0 + 10000.0)
    revue = 2080 * 10.25 / _coefficient(simulateur, 2015, 2021) - 0.7 * 25000.0
    assert 0.0 < seul < revue < menage < 5400.0
    assert (round(ligne.montant, 2), ligne.motif) == (round(seul, 2), "ecretee")
    assert [jour for jour, _ in ligne.revisions] == ["2015-10-01", "2021-04-01"]
    assert [reduction for _, reduction in ligne.revisions] == [
        pytest.approx(seul - menage), pytest.approx(seul - revue)]
    assert (ligne.revision_effet, ligne.derniere_revision) == ("2021-04-01", None)


def test_la_fin_de_son_activite_revise_la_reversion_le_mois_qui_suit(simulateur):
    """« Un assuré titulaire d'une pension de réversion nous informe le 20 mars
    2008 qu'il a cessé son activité professionnelle le 15 février 2008 : date
    d'effet de la révision = 1er mars 2008 » (circulaire Cnav n° 2010/58,
    § 21). La veuve de 2006, née le 15 septembre 1953, gagne 14 000 € : à
    cinquante-trois ans, entiers, ils réduisent sa réversion sous le plafond de
    2006, 2 080 fois 8,03 €. Son activité cessée le 15 février 2008, sa
    réversion est révisée le 1er mars sous le plafond de 2008 : « les
    ressources sont examinées sur les 3 mois qui précèdent cette date de
    révision » (exposé de la Cnav, « Condition de ressources »), ses revenus
    d'activité « pour leur montant réellement perçu » (circulaire RSI
    n° 2007/061, annexe 3, § 6.1), décembre, janvier et quatorze jours de
    février, en mois de trente jours, 11 511,11 € par an : elle redevient
    entière. Le 1er juin, les trois mois sans revenus ne la changent plus, et
    la révision n'est pas écrite ; ses cinquante-cinq ans, en septembre,
    n'ont plus de revenus d'activité à abattre, et ne la révisent pas. Ayant
    travaillé, elle la garde révisable jusqu'à ce qu'elle liquide ses droits
    (circulaire Cnav n° 2007-35, § 222)."""
    carriere = _carriere(simulateur, 1945, 60.0, "1953-09-15", "2006-10-10",
                         ressources=14000.0, activite=14000.0, fin_d_activite="2008-02-15")
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2006)["regime_general"]
    reduite = 2080 * 8.03 - 14000.0
    assert (ligne.date_effet, round(ligne.montant, 2), ligne.motif) == (
        "2006-11-01", round(reduite, 2), "ecretee")
    percus = 14000.0 * (2 + 14 / 30) / 3
    assert 2080 * 8.44 / _coefficient(simulateur, 2006, 2008) - percus > 5400.0
    assert [jour for jour, _ in ligne.revisions] == ["2008-03-01"]
    assert ligne.ressources_des_revisions == (("2008-03-01", pytest.approx(percus)),)
    assert ligne.reduction_de_la_revision == pytest.approx(reduite - 5400.0)
    assert ligne.derniere_revision is None


def test_le_menage_qui_se_defait_apres_sa_derniere_revision_ne_change_rien(simulateur):
    """« A partir de cette date de dernière révision, aucun changement de
    ressources ou de situation familiale n'est pris en compte » (exposé de la
    Cnav, « Condition de ressources ») : la veuve de 2010, née le 17 août 1953,
    remariée en septembre 2014, voit sa réversion révisée en octobre sous le
    plafond du ménage, puis figée au 1er novembre, à son âge légal ; son
    divorce de 2016 n'y change plus rien."""
    carriere = _carriere(simulateur, 1945, 60.0, "1953-08-17", "2010-03-10",
                         nouvelle_union="mariage", union_depuis="2014-09",
                         union_fin="2016-06", apport=28000.0)
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2010)["regime_general"]
    assert [jour for jour, _ in ligne.revisions] == ["2014-10-01"]
    assert (ligne.revision_effet, ligne.derniere_revision) == ("2014-10-01", "2014-11-01")


def test_l_activite_qu_il_reprend_revise_la_reversion_le_mois_qui_suit(simulateur):
    """La réversion « est révisable en cas de variation dans le montant des
    ressources » (R. 353-1-1), et c'est la règle qui s'applique « lorsque,
    notamment, la variation du montant des ressources résulte de la variation
    des revenus professionnels du conjoint survivant » (circulaire Cnav
    n° 2006-6, § 12) : « la réduction, l'augmentation, la suspension ou le
    rétablissement de la prestation » prend effet « à compter du premier jour
    du mois suivant la date de variation des ressources » (circulaire Cnav
    n° 2010/58, § 21). La veuve de 2006, née le 15 septembre 1953, sans
    ressources au décès, reçoit sa réversion entière, 5 400 €. Elle commence
    une activité le 15 mars 2007, qui lui rapporte 14 000 € par an : sa
    réversion est révisée le 1er avril sous le plafond de 2007, 2 080 fois
    8,27 €, ramené aux euros de 2006, sur les trois mois qui précèdent (exposé
    de la Cnav, « Condition de ressources »), ses revenus tels que perçus, les
    seize derniers jours de mars en mois de trente jours (circulaire RSI
    n° 2007/061, annexe 3, § 6.1 et 7) : elle reste entière. Le modèle la
    révise encore le premier mois dont les trois mois ne portent plus que ses
    revenus nouveaux, le 1er juillet : ses revenus entiers la réduisent. À ses
    cinquante-cinq ans, abattus de 30 %, ils la laissent entière sous le
    plafond de 2008, 2 080 fois 8,44 €. Ayant travaillé, elle la garde
    révisable jusqu'à ce qu'elle liquide ses droits (circulaire Cnav n° 2007-35,
    § 222) : son âge légal ne la fige plus."""
    carriere = _carriere(simulateur, 1945, 60.0, "1953-09-15", "2006-10-10",
                         variations=(("2007-03-15", 14000.0),))
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2006)["regime_general"]
    assert (ligne.date_effet, round(ligne.montant, 2), ligne.motif) == (
        "2006-11-01", 5400.0, "servie")
    plafond = 2080 * 8.27 / _coefficient(simulateur, 2006, 2007)
    percus, reduite = 14000.0 * (16 / 30) / 3, plafond - 14000.0
    assert 0.0 < reduite < 5400.0 < plafond - percus
    assert 2080 * 8.44 / _coefficient(simulateur, 2006, 2008) - 0.7 * 14000.0 > 5400.0
    assert [jour for jour, _ in ligne.revisions] == ["2007-04-01", "2007-07-01", "2008-10-01"]
    assert [reduction for _, reduction in ligne.revisions] == [
        pytest.approx(0.0), pytest.approx(5400.0 - reduite), pytest.approx(0.0)]
    assert [ressources for _, ressources in ligne.ressources_des_revisions] == [
        pytest.approx(percus), pytest.approx(14000.0), pytest.approx(0.7 * 14000.0)]
    assert ligne.derniere_revision is None


def test_le_salaire_qui_change_revise_la_reversion_le_mois_qui_suit(simulateur):
    """« La variation des revenus professionnels du conjoint survivant »
    révise la réversion le mois qui suit (circulaire Cnav n° 2006-6, § 12 ;
    circulaire Cnav n° 2010/58, § 21) : le veuf de 2015, né le 10 juin 1958,
    gagne 15 000 €, abattus de 30 % à cinquante-six ans, qui laissent sa
    réversion entière sous le plafond de 2015. Son salaire passe à 25 000 € le
    15 mars 2018 : sa réversion est révisée le 1er avril, sous le plafond de
    2018, 2 080 fois 9,88 €, ramené aux euros de 2015, sur ses revenus
    abattus des trois mois qui précèdent, tels que perçus — janvier, février et
    quatorze jours de mars à l'ancien salaire, seize au nouveau —, qui la
    laissent entière ; le 1er juillet, sur ses seuls nouveaux revenus, qui la
    réduisent. Ayant travaillé sans avoir liquidé ses retraites, il la garde
    révisable."""
    carriere = _carriere(simulateur, 1955, 60.0, "1958-06-10", "2015-03-10",
                         ressources=15000.0, activite=15000.0,
                         variations=(("2018-03-15", 25000.0),))
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2015)["regime_general"]
    assert 2080 * 9.61 - 0.7 * 15000.0 > 5400.0
    assert (round(ligne.montant, 2), ligne.motif) == (5400.0, "servie")
    plafond = 2080 * 9.88 / _coefficient(simulateur, 2015, 2018)
    percus = 0.7 * (15000.0 * (2 + 14 / 30) + 25000.0 * 16 / 30) / 3
    revue = plafond - 0.7 * 25000.0
    assert 0.0 < revue < 5400.0 < plafond - percus
    assert [jour for jour, _ in ligne.revisions] == ["2018-04-01", "2018-07-01"]
    assert [reduction for _, reduction in ligne.revisions] == [
        pytest.approx(0.0), pytest.approx(5400.0 - revue)]
    assert [ressources for _, ressources in ligne.ressources_des_revisions] == [
        pytest.approx(percus), pytest.approx(0.7 * 25000.0)]
    assert (ligne.revision_effet, ligne.derniere_revision) == ("2018-07-01", None)


def test_les_ressources_du_nouveau_conjoint_qui_changent_revisent_la_reversion(simulateur):
    """La variation des revenus professionnels « du ménage » la révise de même
    (circulaire Cnav n° 2006-6, § 12). Le veuf de 2015, né le 10 juin 1958,
    15 000 € de salaire abattus, a sa réversion entière ; remarié en mai 2018 à
    une conjointe qui gagne 20 000 €, il la voit révisée le 1er juin sous le
    plafond du ménage, 1,6 fois 2 080 fois 9,88 €, ramené aux euros de 2015 :
    l'union formée en mai, ses ressources d'après elle sont transposées sur les
    trois mois (circulaire Cnav n° 2005/17, § 146). Les ressources de sa
    conjointe tombent à 12 000 € en janvier 2020 : sa réversion est révisée le
    1er février, sous le plafond du ménage de 2020, 1,6 fois 2 080 fois
    10,15 €, sur les trois mois qui précèdent, tels que perçus — novembre et
    décembre à 20 000 € par an, janvier à 12 000 € —, encore un peu réduite ;
    entière le 1er avril, les trois mois à 12 000 €."""
    carriere = _carriere(simulateur, 1955, 60.0, "1958-06-10", "2015-03-10",
                         ressources=15000.0, activite=15000.0, nouvelle_union="mariage",
                         union_depuis="2018-05", apport=20000.0,
                         variations_de_l_apport=(("2020-01", 12000.0),))
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2015)["regime_general"]
    assert (round(ligne.montant, 2), ligne.motif) == (5400.0, "servie")
    menage = (1.6 * 2080 * 9.88 / _coefficient(simulateur, 2015, 2018)
              - (0.7 * 15000.0 + 20000.0))
    assert 0.0 < menage < 5400.0
    plafond = 1.6 * 2080 * 10.15 / _coefficient(simulateur, 2015, 2020)
    percus = 0.7 * 15000.0 + (2 * 20000.0 + 12000.0) / 3
    assert 0.0 < plafond - percus < 5400.0 < plafond - (0.7 * 15000.0 + 12000.0)
    assert [jour for jour, _ in ligne.revisions] == ["2018-06-01", "2020-02-01", "2020-04-01"]
    assert [reduction for _, reduction in ligne.revisions] == [
        pytest.approx(5400.0 - menage), pytest.approx(5400.0 - (plafond - percus)),
        pytest.approx(0.0)]
    assert [ressources for _, ressources in ligne.ressources_des_revisions] == [
        pytest.approx(0.7 * 15000.0 + 20000.0), pytest.approx(percus),
        pytest.approx(0.7 * 15000.0 + 12000.0)]
    assert ligne.derniere_revision is None


def test_les_ressources_qui_varient_apres_sa_derniere_revision_ne_changent_rien(simulateur):
    """« A partir de cette date de dernière révision, aucun changement de
    ressources ou de situation familiale n'est pris en compte » (exposé de la
    Cnav, « Condition de ressources ») : la veuve de 2010, née le 17 août 1953,
    remariée en septembre 2014, figée au 1er novembre à son âge légal, sans
    activité jusque-là ; ni l'activité qu'elle commence en 2015, ni les
    ressources de son conjoint qui tombent en 2016 n'y changent plus rien. Et
    la réversion attribuée avant juillet 2004 « continue d'être servie selon les
    règles applicables avant cette date » quand ses ressources varient, sans
    retraite prise depuis (exposé « Condition de ressources »)."""
    carriere = _carriere(simulateur, 1945, 60.0, "1953-08-17", "2010-03-10",
                         nouvelle_union="mariage", union_depuis="2014-09", apport=28000.0,
                         variations=(("2015-03", 12000.0),),
                         variations_de_l_apport=(("2016-01", 10000.0),))
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2010)["regime_general"]
    assert [jour for jour, _ in ligne.revisions] == ["2014-10-01"]
    assert (ligne.revision_effet, ligne.derniere_revision) == ("2014-10-01", "2014-11-01")
    ancienne = _carriere(simulateur, 1930, 60.0, "1940-06-10", "1999-03-10",
                         ressources=12000.0, activite=12000.0,
                         variations=(("2001-05", 15000.0),))
    ligne = _servies(simulateur, ancienne, [("regime_general", 10000.0)],
                     1999)["regime_general"]
    assert (ligne.revisions, ligne.derniere_revision) == ((), None)


def test_la_date_d_effet_retient_les_trois_mois_qui_la_precedent_depuis_le_deces(simulateur):
    """« Les ressources à prendre en compte lors de la demande sont celles
    afférentes aux trois mois civils précédant la date d'effet de la pension
    de réversion » (R. 353-1), les revenus d'activité « pour leur montant
    réellement perçu au cours de la période de référence » (circulaire RSI
    n° 2007/061, annexe 3, § 6.1) ; quand la situation familiale change dans
    la période — le décès de l'assuré en est un (lettre de la Cnav du 18 avril
    2007) —, celles qui suivent le changement, « transposées sur 3 mois », en
    mois de trente jours (§ 7, exemple 1). La veuve de 2006, née le 15
    septembre 1953, gagne 20 000 € par an ; son mari meurt le 10 octobre, et
    son activité cesse le 25 : sa réversion part le 1er novembre, sur les
    vingt et un jours qui suivent le décès, dont quinze de salaire, soit
    14 285,71 € par an, qui la réduisent sous le plafond de 2006, 2 080 fois
    8,03 €. Le modèle la révise le premier mois dont les trois mois ne portent
    plus de salaire, le 1er février 2007, comme la caisse qui, la date d'effet
    passée, « calcule différents dépassements jusqu'à stabilisation des
    ressources » (circulaire RSI n° 2007/061, annexe 3, exemples) : elle
    redevient entière."""
    carriere = _carriere(simulateur, 1945, 60.0, "1953-09-15", "2006-10-10",
                         ressources=20000.0, activite=20000.0, fin_d_activite="2006-10-25")
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2006)["regime_general"]
    percus = 20000.0 * 15 / 21
    reduite = 2080 * 8.03 - percus
    assert ligne.date_effet == "2006-11-01"
    assert ligne.ressources_retenues == pytest.approx(percus)
    assert (round(ligne.montant, 2), ligne.motif) == (round(reduite, 2), "ecretee")
    assert ligne.periode_de_reference == 3
    assert 2080 * 8.27 / _coefficient(simulateur, 2006, 2007) > 5400.0
    assert ligne.revisions == (("2007-02-01", pytest.approx(reduite - 5400.0)),)
    assert ligne.ressources_des_revisions == (("2007-02-01", 0.0),)


def test_au_dela_du_quart_du_plafond_la_date_d_effet_retient_les_douze_mois(simulateur):
    """« Lorsqu'elles excèdent le quart du plafond [...], il leur est substitué
    celles afférentes aux douze mois civils précédant cette date, qui sont
    alors comparées au montant annuel de ce plafond » (R. 353-1). La veuve de
    2010, née le 10 juin 1956, attend ses cinquante-cinq ans : sa réversion part
    le 1er juillet 2011. Elle gagne 10 000 € par an, 40 000 € depuis le 1er mai
    2011 : avril, mai et juin, abattus de 30 %, valent 21 000 € par an, plus
    que le plafond de 2010, 2 080 fois 8,86 € ; les douze mois de juillet 2010
    à juin 2011, 10 500 €, la laissent entière. Une révision n'apprécie que
    trois mois (circulaire Cnav n° 2005/17, § 321) : le 1er août, quand ils ne
    portent plus que son nouveau salaire, 28 000 € abattus la suspendent."""
    carriere = _carriere(simulateur, 1950, 60.0, "1956-06-10", "2010-03-10",
                         ressources=10000.0, activite=10000.0,
                         variations=(("2011-05-01", 40000.0),))
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2010)["regime_general"]
    assert 0.7 * (10000.0 + 2 * 40000.0) / 3 > 2080 * 8.86
    assert ligne.date_effet == "2011-07-01"
    assert ligne.ressources_retenues == pytest.approx(0.7 * (10 * 10000.0 + 2 * 40000.0) / 12)
    assert (round(ligne.montant, 2), ligne.motif) == (5400.0, "servie")
    assert ligne.periode_de_reference == 12
    assert ligne.revisions == (("2011-08-01", pytest.approx(5400.0)),)
    assert ligne.ressources_des_revisions == (("2011-08-01", pytest.approx(0.7 * 40000.0)),)


def test_sa_retraite_du_jour_de_la_date_d_effet_ne_compte_qu_a_la_revision(simulateur):
    """Les trois mois civils qui précèdent la date d'effet ne portent pas le
    droit propre qui commence ce jour-là : la caisse ne le compte pas « à la
    date d'effet de la PR puisque la date d'effet du DP est le 01/10/06 », et
    le compte à la révision du mois qui suit (circulaire RSI n° 2007/061,
    annexe 3, exemple 3). La veuve de 2015, née le 5 avril 1952, prend sa
    retraite, 18 000 € par an, le 1er avril, quand sa réversion part : entière
    à sa date d'effet ; révisée le 1er mai, sur les cinquante et un jours qui
    suivent le décès du 10 mars, dont trente de retraite, qui la laissent
    entière ; puis le 1er juillet, sa dernière révision, sur trois mois de
    retraite, qui la réduisent sous le plafond de 2015, 2 080 fois 9,61 €."""
    carriere = _carriere(simulateur, 1950, 65.0, "1952-04-05", "2015-03-10",
                         ressources=18000.0, retraite="2015-04-01")
    ligne = _servies(simulateur, carriere, [("regime_general", 10000.0)],
                     2015)["regime_general"]
    assert ligne.date_effet == "2015-04-01"
    assert ligne.ressources_retenues == 0.0
    assert (round(ligne.montant, 2), ligne.motif) == (5400.0, "servie")
    assert ligne.periode_de_reference == 3
    revue = 2080 * 9.61 - 18000.0
    assert ligne.revisions == (("2015-05-01", pytest.approx(0.0)),
                               ("2015-07-01", pytest.approx(5400.0 - revue)))
    assert ligne.ressources_des_revisions == (
        ("2015-05-01", pytest.approx(18000.0 * 30 / 51)), ("2015-07-01", pytest.approx(18000.0)))
    assert ligne.derniere_revision == "2015-07-01"


#: Des saisies où la réversion du régime général se révise avant la retraite
#: du survivant, ou sans elle : le veuf de 2015 qui travaille et se remarie en
#: 2018 ; la veuve de 2010, sans ressources, remariée avant son âge légal ; le
#: veuf retraité en juillet 2020, remarié en août ; la veuve de 2006 à qui ses
#: cinquante-cinq ans valent l'abattement ; la veuve de 2023, sans ressources ni
#: ménage, dont la réversion se fige à son âge légal ; le veuf de 2015 pacsé en
#: septembre, le pacs rompu en mars 2021 ; la veuve de 2006 qui cesse son
#: activité en février 2008. Chacune avec les jours de ses révisions, et celui
#: où elle n'est plus révisable.
CAS_DES_REVISIONS = [
    ({"naissance": "1955", "liquidation": "60", "sexe": "F", "conjoint": "1958-06",
      "conjoint_sexe": "H", "deces": "2015-03", "ressources_conjoint": "15000",
      "activite_conjoint": "15000", "nouvelle_union": "mariage",
      "nouvelle_union_depuis": "2018-05", "ressources_nouveau_conjoint": "20000"},
     ["2018-06-01"], None),
    ({"naissance": "1945", "liquidation": "60", "conjoint": "1953-08", "deces": "2010-03",
      "nouvelle_union": "mariage", "nouvelle_union_depuis": "2014-09",
      "ressources_nouveau_conjoint": "28000"}, ["2014-10-01"], "2014-11-01"),
    ({"naissance": "1955", "liquidation": "60", "sexe": "F", "conjoint": "1958-06",
      "conjoint_sexe": "H", "deces": "2015-03", "ressources_conjoint": "18000",
      "conjoint_retraite": "2020-07", "nouvelle_union": "mariage",
      "nouvelle_union_depuis": "2020-08", "ressources_nouveau_conjoint": "12000"},
     ["2020-08-01", "2020-09-01"], "2020-10-01"),
    ({"naissance": "1945", "liquidation": "60", "conjoint": "1953-09", "deces": "2006-10",
      "ressources_conjoint": "14000", "activite_conjoint": "14000"}, ["2008-10-01"], None),
    ({"naissance": "1960", "liquidation": "62", "conjoint": "1962", "deces": "2023-05"},
     [], "2024-08-01"),
    ({"naissance": "1955", "liquidation": "60", "sexe": "F", "conjoint": "1958-06",
      "conjoint_sexe": "H", "deces": "2015-03", "ressources_conjoint": "25000",
      "activite_conjoint": "25000", "nouvelle_union": "pacs",
      "nouvelle_union_depuis": "2015-09", "nouvelle_union_fin": "2021-03",
      "ressources_nouveau_conjoint": "10000"}, ["2015-10-01", "2021-04-01"], None),
    ({"naissance": "1945", "liquidation": "60", "conjoint": "1953-09", "deces": "2006-10",
      "ressources_conjoint": "14000", "activite_conjoint": "14000",
      "activite_conjoint_fin": "2008-02"}, ["2008-03-01"], None),
    # Les ressources qui varient autrement : la veuve de 2006, sans ressources,
    # qui commence une activité en mars 2007 ; le veuf de 2015 dont le salaire
    # passe à 25 000 € en mars 2018 ; remarié en mai 2018, sa conjointe dont les
    # ressources tombent à 12 000 € en janvier 2020. Chacune révisée le mois
    # qui suit, sur les trois mois qui précèdent, tels que perçus, puis quand
    # les trois mois ne portent plus que les revenus nouveaux.
    ({"naissance": "1945", "liquidation": "60", "conjoint": "1953-09", "deces": "2006-10",
      "activite_conjoint_variations": "2007-03:14000"},
     ["2007-04-01", "2007-06-01", "2008-10-01"], None),
    ({"naissance": "1955", "liquidation": "60", "sexe": "F", "conjoint": "1958-06",
      "conjoint_sexe": "H", "deces": "2015-03", "ressources_conjoint": "15000",
      "activite_conjoint": "15000", "activite_conjoint_variations": "2018-03:25000"},
     ["2018-04-01", "2018-06-01"], None),
    ({"naissance": "1955", "liquidation": "60", "sexe": "F", "conjoint": "1958-06",
      "conjoint_sexe": "H", "deces": "2015-03", "ressources_conjoint": "15000",
      "activite_conjoint": "15000", "nouvelle_union": "mariage",
      "nouvelle_union_depuis": "2018-05", "ressources_nouveau_conjoint": "20000",
      "ressources_nouveau_conjoint_variations": "2020-01:12000"},
     ["2018-06-01", "2020-02-01", "2020-04-01"], None),
]


def test_les_deux_moteurs_revisent_la_reversion_avant_sa_retraite(saisies):
    """Le résultat entier, des six scénarios, est le même en Python et en
    JavaScript ; chaque cas révise la réversion du régime général aux jours
    qu'il dit, et la fige au jour qu'il dit."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(racine / "scripts"))
    from construire_temoins import _fini
    attendus = [{"requete": cas, "resultat": _fini(saisies.simuler(cas).dictionnaire())}
                for cas, _, _ in CAS_DES_REVISIONS]
    for attendu, (_, revisions, derniere) in zip(attendus, CAS_DES_REVISIONS):
        ligne, = (r for r in attendu["resultat"]["reversion"]["regimes"]
                  if r["regime"] == "regime_general")
        assert ([r["date"] for r in ligne["revisions"]], ligne["derniere_revision"]) == (
            revisions, derniere), ligne
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(json.dumps(attendus, ensure_ascii=False))
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(racine / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]


#: Des saisies où la retraite du survivant suit la date d'effet de sa
#: réversion : la veuve de 1999 qui la prend en 2008, que les règles de
#: ressources de 2004 recalculent ; le veuf de 2015 qui la prend en 2020, seul
#: ou remarié en 2018 ; la veuve de 2024 qui la prendra en 2030. Chacune avec
#: le jour de la dernière révision de sa réversion du régime général — sa
#: retraite, que la révision du mois qui suit ne compte que pour un mois depuis
#: 2010, la revoit encore trois mois après elle —, et celui où elle n'est plus
#: révisable.
CAS_DE_LA_REVISION = [
    ({"naissance": "1930", "liquidation": "60", "conjoint": "1940-06", "deces": "1999-03",
      "ressources_conjoint": "12000", "conjoint_retraite": "2008-03"},
     "2008-03-01", "2008-06-01"),
    ({"naissance": "1955", "liquidation": "60", "sexe": "F", "conjoint": "1958-06",
      "conjoint_sexe": "H", "deces": "2015-03", "ressources_conjoint": "18000",
      "conjoint_retraite": "2020-07"}, "2020-10-01", "2020-10-01"),
    ({"naissance": "1955", "liquidation": "60", "sexe": "F", "conjoint": "1958-06",
      "conjoint_sexe": "H", "deces": "2015-03", "ressources_conjoint": "18000",
      "conjoint_retraite": "2020-07", "nouvelle_union": "mariage",
      "nouvelle_union_depuis": "2018-05", "ressources_nouveau_conjoint": "12000"},
     "2020-10-01", "2020-10-01"),
    ({"naissance": "1960", "liquidation": "62", "conjoint": "1964-03", "deces": "2024-05",
      "ressources_conjoint": "20000", "conjoint_retraite": "2030-01"},
     "2030-04-01", "2030-04-01"),
]


def test_les_deux_moteurs_revoient_la_reversion_a_sa_retraite(saisies):
    """Le résultat entier, des six scénarios, est le même en Python et en
    JavaScript ; chaque cas revoit la réversion du régime général en dernier
    au jour qu'il dit, et la fige trois mois après sa retraite."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(racine / "scripts"))
    from construire_temoins import _fini
    attendus = [{"requete": cas, "resultat": _fini(saisies.simuler(cas).dictionnaire())}
                for cas, _, _ in CAS_DE_LA_REVISION]
    for attendu, (_, revision, derniere) in zip(attendus, CAS_DE_LA_REVISION):
        ligne, = (r for r in attendu["resultat"]["reversion"]["regimes"]
                  if r["regime"] == "regime_general")
        assert (ligne["revision_effet"], ligne["derniere_revision"]) == (
            revision, derniere), ligne
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(json.dumps(attendus, ensure_ascii=False))
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(racine / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]


def test_les_deux_moteurs_comptent_ses_retraites_entieres_avant_juillet_2010(saisies):
    """Au régime général, avant le 30 juin 2010, la révision qui suit la
    retraite du survivant la compte entière, « 3 mois de DP alors qu'un seul
    mois est servi » (circulaire RSI n° 2007/061, annexe 3, § 6.2), ce que les
    versions de la fiche disent (``retraites_entieres_a_la_revision``) et que
    le portage lit dans son paquet : la veuve de 2006, retraitée en janvier
    2008, voit sa réversion revue une seule fois, le 1er février, et figée le
    1er avril, dans les deux moteurs. Le cas est du niveau ``complet`` : le
    paquet que GitHub refait le porte."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(racine / "scripts"))
    from construire_temoins import _fini
    cas = {"naissance": "1945", "liquidation": "60", "conjoint": "1950-03",
           "deces": "2006-10", "ressources_conjoint": "14000", "conjoint_retraite": "2008-01"}
    attendu = {"requete": cas, "resultat": _fini(saisies.simuler(cas).dictionnaire())}
    ligne, = (r for r in attendu["resultat"]["reversion"]["regimes"]
              if r["regime"] == "regime_general")
    assert [revision["date"] for revision in ligne["revisions"]] == ["2008-02-01"]
    assert [revision["ressources"] for revision in ligne["revisions"]] == [14000.0]
    assert ligne["derniere_revision"] == "2008-04-01"
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(json.dumps([attendu], ensure_ascii=False))
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(racine / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]


#: Des saisies où la date d'effet de la réversion du régime général retient
#: les trois ou les douze mois qui la précèdent (R. 353-1) : la veuve de 2006
#: dont l'activité cesse quinze jours après le décès ; la veuve de 2010 dont le
#: salaire quadruple deux mois avant ses cinquante-cinq ans ; la veuve de 2015,
#: retraitée le jour où sa réversion part. Chacune avec les mois de sa période
#: de référence et les jours de ses révisions.
CAS_DE_LA_DATE_D_EFFET = [
    ({"naissance": "1945", "liquidation": "60", "conjoint": "1953-09-15",
      "deces": "2006-10-10", "ressources_conjoint": "20000", "activite_conjoint": "20000",
      "activite_conjoint_fin": "2006-10-25"}, 3, ["2007-02-01"]),
    ({"naissance": "1950", "liquidation": "60", "conjoint": "1956-06-10",
      "deces": "2010-03-10", "ressources_conjoint": "10000", "activite_conjoint": "10000",
      "activite_conjoint_variations": "2011-05-01:40000"}, 12, ["2011-08-01"]),
    ({"naissance": "1950", "liquidation": "65", "conjoint": "1952-04-05",
      "deces": "2015-03-10", "ressources_conjoint": "18000", "conjoint_retraite": "2015-04"},
     3, ["2015-05-01", "2015-07-01"]),
]


def test_les_deux_moteurs_retiennent_les_trois_ou_douze_mois_de_la_date_d_effet(saisies):
    """Le résultat entier, des six scénarios, est le même en Python et en
    JavaScript ; chaque cas retient, à la date d'effet de la réversion du régime
    général, les mois qu'il dit, et la révise aux jours qu'il dit. Le portage
    lit la période de référence dans les versions de son paquet : le cas est du
    niveau ``complet``, que GitHub joue sur le paquet qu'il refait."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(racine / "scripts"))
    from construire_temoins import _fini
    attendus = [{"requete": cas, "resultat": _fini(saisies.simuler(cas).dictionnaire())}
                for cas, _, _ in CAS_DE_LA_DATE_D_EFFET]
    for attendu, (_, mois, revisions) in zip(attendus, CAS_DE_LA_DATE_D_EFFET):
        ligne, = (r for r in attendu["resultat"]["reversion"]["regimes"]
                  if r["regime"] == "regime_general")
        assert (ligne["periode_de_reference"], [r["date"] for r in ligne["revisions"]]) == (
            mois, revisions), ligne
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        fichier.write(json.dumps(attendus, ensure_ascii=False))
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(racine / "tests" / "js" / "comparer.mjs"), chemin],
            cwd=racine, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, (execution.stdout + execution.stderr)[-2000:]


# -- les majorations forfaitaires des pensions d'avant 1975 ----------------------------

def _pension(regime: str = "regime_general", maximum: bool = True):
    from retraite_notionnelle.droit.commun import PensionRegime
    return PensionRegime(regime=regime, montant=1000.0, type_calcul="annuites", detail="",
                         fiabilite=HAUTE, sur_la_duree_maximum=maximum)


@pytest.mark.parametrize("regime, depart, maximum, attendues", [
    # Avant 1972, sur cent vingt trimestres : les quatre.
    ("regime_general", "1970-02-01", True,
     (("1972-01-01", 0.05), ("1976-07-01", 0.05), ("1977-10-01", 0.05), ("1982-12-01", 0.06))),
    # Sur moins : celle de 1982, sans condition de durée.
    ("regime_general", "1970-02-01", False, (("1982-12-01", 0.06),)),
    # Les salariés agricoles : celles de 1972 et de 1982 (lois n° 71-1132,
    # article 10, et n° 82-599, article 1er).
    ("msa_salaries", "1970-02-01", True, (("1972-01-01", 0.05), ("1982-12-01", 0.06))),
    ("regime_general", "1972-02-01", True,
     (("1976-07-01", 0.05), ("1977-10-01", 0.05), ("1982-12-01", 0.04))),
    ("regime_general", "1973-02-01", True, (("1982-12-01", 0.055),)),
    ("regime_general", "1973-02-01", False, ()),
    ("regime_general", "1974-02-01", True, (("1982-12-01", 0.015),)),
    ("regime_general", "1975-02-01", True, ()),
    ("arrco", "1970-02-01", True, ()),
])
def test_les_majorations_forfaitaires_de_1972_a_1982(simulateur, regime, depart, maximum,
                                                     attendues):
    """Lois n° 71-1132, article 8, n° 75-1279, article 3, n° 77-657, article
    1er, et n° 82-599, articles 1er et 2 : chacune selon la date d'effet de la
    pension, son régime et sa durée (fiche ``majorations_forfaitaires_1972_1982``)."""
    from retraite_notionnelle.revalorisation import majorations_forfaitaires
    assert majorations_forfaitaires(simulateur.scenario_actuel, _pension(regime, maximum),
                                    depart) == attendues


@pytest.mark.parametrize("depart, taux, attendu", [
    # « 40 % du SAM », porté par les trois majorations de 5 % à 46,30 %
    # (circulaire Cnav n° 64/77, B).
    ("1970-02-01", 0.40, 46.30),
    # « en 1972 à 42,66 % du SAM (50 x 128 / 150) », porté à 47,04 % (même lieu).
    ("1972-02-01", 0.50 * 128 / 150, 47.04),
    # « en 1973 à 47,82 % (45,33 % x 1,055) », « en 1974 à 48,72 % (48 % X
    # 1,015) » (circulaire Cnav n° 79/82, B).
    ("1973-02-01", 0.50 * 136 / 150, 47.82),
    ("1974-02-01", 0.50 * 144 / 150, 48.72),
])
def test_les_taux_que_les_circulaires_donnent_a_la_pension_majoree(simulateur, depart, taux,
                                                                   attendu):
    """Le taux de la pension au maximum de sa date, que les majorations
    portent avant celle de 1982 pour la pension d'avant 1973, ou que celle de
    1982 porte pour celles de 1973 et de 1974, au centième, tronqué."""
    from retraite_notionnelle.revalorisation import majorations_forfaitaires
    majore = taux
    for jour, majoration in majorations_forfaitaires(simulateur.scenario_actuel, _pension(),
                                                     depart):
        if jour < "1982-12-01" or depart >= "1973-01-01":
            majore *= 1 + majoration
    assert int(majore * 10000 + 1e-6) / 100 == attendu


def test_la_reversion_suit_les_majorations_de_la_pension_du_defunt(saisies):
    """La pension du salarié parti en 1971 sur cent quatre trimestres reçoit
    6 % au 1er décembre 1982 ; sa veuve, à qui la réversion est attribuée au
    1er janvier 1973, les reçoit avec elle, avant les 4 % de la réversion
    même : 10,24 % du montant calculé, puis 3,846 % en 1995 (circulaire Cnav
    n° 79/82, C ; exposé « Montant - retraite de réversion »)."""
    comparaison = saisies.simuler({
        "naissance": "1906", "liquidation": "65", "conjoint": "1916", "deces": "1971-03"})
    general = next(l for l in comparaison.reversion.regimes if l.regime == "regime_general")
    assert (general.date_effet, general.motif) == ("1973-01-01", "servie")
    calcule = 0.5 * general.base
    assert general.montant == pytest.approx(calcule)
    assert general.majorations_forfaitaires == (
        ("1982-12-01", pytest.approx(calcule * (1.06 * 1.04 - 1))),
        ("1995-01-01", pytest.approx(calcule * 1.06 * 1.04 * 0.03846)))


# -- ce qui n'est pas porté ----------------------------------------------------------

def test_un_regime_sans_fiche_le_dit_et_un_regime_vide_ne_reverse_rien(simulateur):
    carriere = _carriere(simulateur, 1957, 62.0, "1965", "2022-03-10")
    lignes = _lignes(simulateur, carriere, [("cnavpl", 500.0), ("ircantec", 0.0)], 2022)
    assert lignes == [("cnavpl", 0.0, 0.0, "non_portee", None, None)]


def test_avant_2013_la_reversion_de_la_rci_n_est_pas_portee(simulateur):
    """Les règlements des régimes complémentaires des artisans et des
    commerçants d'avant 2013 ne sont pas lus : leur ligne le dit."""
    carriere = _carriere(simulateur, 1945, 62.0, "1950", "2010-05-10")
    assert _lignes(simulateur, carriere, [("rco_artisans", 3000.0)], 2010) == [
        ("rco_artisans", 0.0, 0.0, "non_portee", None, None)]


def test_sans_conjoint_pas_de_reversion(simulateur):
    carriere = Carriere.depuis_profil(1957, "H", "salarie_prive_non_cadre", 21.0, 62.0,
                                      simulateur.macro)
    assert carriere.conjoint is None and carriere.deces is None
    assert reversion(simulateur.scenario_actuel, [("regime_general", 1.0, HAUTE)],
                     carriere, 2022) is None


# -- la saisie et la simulation ------------------------------------------------------

@pytest.mark.parametrize("requete, message", [
    ({"deces": "2030"}, "« deces » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "deces": "1959"}, "Le décès précède la naissance de l'assuré"),
    ({"conjoint": "1962", "deces": "1985"}, "il précède le mariage, que le modèle présume"),
    ({"conjoint": "1962", "mariage": "1979", "deces": "1980"},
     "il précède le début de la carrière"),
    ({"conjoint": "1962", "mariage": "1961"}, "précède la naissance"),
    ({"conjoint": "1962", "conjoint_sexe": "X"}, "Sexe du conjoint"),
    ({"conjoint": "1962-13"}, "La naissance du conjoint « 1962-13 »"),
    ({"conjoint_invalidite": "2024-02"}, "« conjoint_invalidite » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "conjoint_invalidite": "1961"},
     "L'invalidité du conjoint précède sa naissance"),
    ({"conjoint": "1962", "conjoint_invalidite": "2024-13"},
     "L'invalidité du conjoint « 2024-13 »"),
    ({"activite_conjoint": "5000"}, "« activite_conjoint » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "activite_conjoint": "5000"}, "une part de ses ressources"),
    ({"conjoint": "1962", "ressources_conjoint": "4000", "activite_conjoint": "5000"},
     "une part de ses ressources"),
    ({"conjoint": "1962", "ressources_conjoint": "4000", "activite_conjoint": "-1"},
     "Revenus d'activité du conjoint : un montant annuel positif"),
    ({"nouvelle_union": "pacs"}, "« nouvelle_union » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "nouvelle_union": "veuvage"}, "mariage, pacs ou concubinage"),
    ({"conjoint": "1962", "ressources_nouveau_conjoint": "5000"},
     "« ressources_nouveau_conjoint » ne sert qu'au ménage du conjoint"),
    ({"conjoint": "1962", "nouvelle_union": "pacs", "ressources_nouveau_conjoint": "-1"},
     "Ressources du nouveau conjoint : un montant annuel positif"),
    ({"conjoint": "1962", "nouvelle_union_depuis": "2031"},
     "« nouvelle_union_depuis » ne sert qu'au ménage du conjoint"),
    ({"conjoint": "1962", "mariage": "1990", "deces": "2030", "nouvelle_union": "mariage",
      "nouvelle_union_depuis": "2029"}, "La nouvelle union du conjoint précède votre décès"),
    ({"nouvelle_union_fin": "2031"}, "« nouvelle_union_fin » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "nouvelle_union_fin": "2031"},
     "« nouvelle_union_fin » ne sert qu'au ménage du conjoint"),
    ({"conjoint": "1962", "nouvelle_union": "pacs", "nouvelle_union_fin": "2031-13"},
     "La fin de la nouvelle union du conjoint « 2031-13 »"),
    ({"conjoint": "1962", "mariage": "1990", "deces": "2030", "nouvelle_union": "pacs",
      "nouvelle_union_depuis": "2031-06", "nouvelle_union_fin": "2031-02"},
     "La fin de la nouvelle union du conjoint précède son début"),
    ({"conjoint": "1962", "mariage": "1990", "deces": "2030", "nouvelle_union": "pacs",
      "nouvelle_union_fin": "2029"},
     "La fin de la nouvelle union du conjoint précède votre décès"),
    ({"activite_conjoint_fin": "2031"}, "« activite_conjoint_fin » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "ressources_conjoint": "9000", "activite_conjoint_fin": "2031"},
     "« activite_conjoint_fin » ne sert qu'aux revenus d'activité du conjoint"),
    ({"conjoint": "1962", "ressources_conjoint": "9000", "activite_conjoint": "9000",
      "activite_conjoint_fin": "2031-13"}, "La fin de l'activité du conjoint « 2031-13 »"),
    ({"conjoint": "1962", "mariage": "1990", "deces": "2030", "ressources_conjoint": "9000",
      "activite_conjoint": "9000", "activite_conjoint_fin": "2029"},
     "La fin de l'activité du conjoint précède votre décès"),
    ({"activite_conjoint_variations": "2031:5000"},
     "« activite_conjoint_variations » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "activite_conjoint_variations": "2031"},
     "Variation des revenus d'activité du conjoint mal formée : « 2031 »"),
    ({"conjoint": "1962", "activite_conjoint_variations": "2031-13:5000"},
     "La variation des revenus d'activité du conjoint « 2031-13 »"),
    ({"conjoint": "1962", "activite_conjoint_variations": "2031-04:-1"},
     "Variation des revenus d'activité du conjoint « 2031-04:-1 » : un montant annuel "
     "positif ou nul"),
    ({"conjoint": "1962", "mariage": "1990", "deces": "2030",
      "activite_conjoint_variations": "2029:5000"},
     "La variation des revenus d'activité du conjoint du 2029 précède votre décès"),
    ({"conjoint": "1962", "mariage": "1990", "deces": "2030", "ressources_conjoint": "9000",
      "activite_conjoint": "9000", "activite_conjoint_fin": "2033-02",
      "activite_conjoint_variations": "2033-02:5000"},
     "Deux changements des revenus d'activité du conjoint tombent le même jour"),
    ({"conjoint": "1962", "activite_conjoint_variations": ",".join(
        f"{2031 + i}:5000" for i in range(61))},
     "Variations des revenus d'activité du conjoint : 61"),
    ({"ressources_nouveau_conjoint_variations": "2031:5000"},
     "« ressources_nouveau_conjoint_variations » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "ressources_nouveau_conjoint_variations": "2031:5000"},
     "« ressources_nouveau_conjoint_variations » ne sert qu'au ménage du conjoint"),
    ({"conjoint": "1962", "mariage": "1990", "deces": "2030", "nouvelle_union": "pacs",
      "nouvelle_union_depuis": "2031-06", "ressources_nouveau_conjoint_variations": "2031-02:1"},
     "La variation des ressources du nouveau conjoint du 2031-02 précède le début de "
     "leur union"),
    ({"conjoint": "1962", "mariage": "1990", "deces": "2030", "nouvelle_union": "pacs",
      "nouvelle_union_fin": "2034-11", "ressources_nouveau_conjoint_variations": "2035:1"},
     "La variation des ressources du nouveau conjoint du 2035 ne précède pas la fin de "
     "leur union"),
    ({"conjoint": "1962", "nouvelle_union": "pacs",
      "ressources_nouveau_conjoint_variations": "2033:1,2033-01:2"},
     "Deux changements des ressources du nouveau conjoint tombent le même jour"),
    ({"ex1": "1958", "ex1_mariage": "1980", "ex1_divorce": "1985"},
     "« ex1 » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "mariage": "1990", "ex1": "1958"},
     "Précédent conjoint n° 1 : indiquer sa naissance, la date du mariage"),
    ({"conjoint": "1962", "ex1": "1958", "ex1_mariage": "1980", "ex1_divorce": "1985"},
     "dites aussi la date du mariage avec votre conjoint"),
    ({"conjoint": "1962", "mariage": "1990", "ex1": "1958", "ex1_mariage": "1980",
      "ex1_divorce": "1979"}, "le divorce suit le mariage"),
    ({"conjoint": "1962", "mariage": "1990", "ex1": "1958", "ex1_mariage": "1980",
      "ex1_divorce": "1985", "ex1_remariage": "1984"}, "son remariage suit le divorce"),
    ({"conjoint": "1962", "mariage": "1984", "ex1": "1958", "ex1_mariage": "1980",
      "ex1_divorce": "1985"}, "précède le divorce d'un précédent mariage"),
    ({"conjoint": "1962", "mariage": "1990", "ex1": "1958", "ex1_mariage": "1980",
      "ex1_divorce": "1985", "ex2": "1959", "ex2_mariage": "1984", "ex2_divorce": "1988"},
     "Précédent conjoint n° 2 : le mariage suit les deux naissances"),
])
def test_la_saisie_refuse_ce_qui_ne_tient_pas(requete, message):
    with pytest.raises(ErreurSite, match=refus_de_la_saisie(message)):
        saisie_du_portage({"naissance": "1960", "liquidation": "2024-01", **requete})


def test_l_adresse_garde_le_conjoint_et_le_deces():
    from urllib.parse import parse_qsl

    saisie = saisie_du_portage({
        "naissance": "1960", "liquidation": "2024-01", "conjoint": "1962-03",
        "mariage": "1985-06", "ressources_conjoint": "12000",
        "activite_conjoint": "9000", "nouvelle_union": "concubinage",
        "ressources_nouveau_conjoint": "14000",
        "conjoint_invalidite": "2028-04", "deces": "2031-10"})
    relue = saisie_du_portage(dict(parse_qsl(saisie.requete())))
    assert (relue.conjoint, relue.mariage, relue.ressources_conjoint,
            relue.activite_conjoint, relue.nouvelle_union,
            relue.ressources_nouveau_conjoint, relue.conjoint_invalidite, relue.deces) == (
        "1962-03", "1985-06", 12000.0, 9000.0, "concubinage", 14000.0, "2028-04",
        "2031-10")
    assert "conjoint" not in saisie_du_portage({"naissance": "1960"}).requete()


def test_l_adresse_garde_la_fin_du_menage_et_celle_de_l_activite():
    """Le mois où le ménage du conjoint se défait, et celui où son activité
    cesse, que la réversion lit pour se réviser, reviennent de l'adresse."""
    from urllib.parse import parse_qsl

    saisie = saisie_du_portage({
        "naissance": "1960", "liquidation": "2024-01", "conjoint": "1962-03",
        "mariage": "1985-06", "ressources_conjoint": "12000",
        "activite_conjoint": "9000", "activite_conjoint_fin": "2033-02",
        "nouvelle_union": "pacs", "nouvelle_union_depuis": "2032-06",
        "nouvelle_union_fin": "2034-11", "deces": "2031-10"})
    relue = saisie_du_portage(dict(parse_qsl(saisie.requete())))
    assert (relue.activite_conjoint_fin, relue.nouvelle_union_depuis,
            relue.nouvelle_union_fin) == ("2033-02", "2032-06", "2034-11")
    assert relue.conjointDeclare()["fin_d_activite"] == "2033-02"
    assert relue.conjointDeclare()["nouvelle_union_fin"] == "2034-11"


def test_l_adresse_garde_les_ressources_qui_varient():
    """Les variations des revenus d'activité du conjoint et des ressources de
    son nouveau conjoint, « date:montant » chacune, reviennent de l'adresse, et
    passent à la chronologie en couples, dans l'ordre de leurs dates."""
    from urllib.parse import parse_qsl

    saisie = saisie_du_portage({
        "naissance": "1960", "liquidation": "2024-01", "conjoint": "1962-03",
        "mariage": "1985-06", "ressources_conjoint": "12000",
        "activite_conjoint": "9000", "activite_conjoint_fin": "2033-02",
        "activite_conjoint_variations": " 2035-01:12000.5, 2032-06:9500 ",
        "nouvelle_union": "pacs", "nouvelle_union_depuis": "2032-06",
        "ressources_nouveau_conjoint": "14000",
        "ressources_nouveau_conjoint_variations": "2034:11000", "deces": "2031-10"})
    relue = saisie_du_portage(dict(parse_qsl(saisie.requete())))
    assert (relue.activite_conjoint_variations,
            relue.ressources_nouveau_conjoint_variations) == (
        "2035-01:12000.5, 2032-06:9500", "2034:11000")
    declare = relue.conjointDeclare()
    assert (declare["variations_d_activite"], declare["variations_du_nouveau_conjoint"]) == (
        [["2032-06", 9500], ["2035-01", 12000.5]], [["2034", 11000]])
    assert "variations" not in saisie_du_portage({
        "naissance": "1960", "conjoint": "1962"}).requete()


@pytest.fixture(scope="module")
def saisies() -> Saisies:
    return Saisies()


def test_le_journal_inscrit_le_deces_puis_la_reversion(saisies):
    """Le décès est un événement de l'échéancier, et la réversion la
    liquidation qu'il ouvre au survivant (§ 7.3, § 7.4) ; sans décès déclaré,
    la sortie n'a pas de clé « reversion »."""
    comparaison = saisies.simuler({
        "naissance": "1958", "liquidation": "62", "conjoint": "1960",
        "deces": "2023-05"})
    entrees = {(e.id, e.sorte) for e in comparaison.journal}
    assert {("deces_assure", "evenement"), ("reversion_conjoint", "evenement"),
            ("liquidation_reversion_conjoint", "reversion")} <= entrees
    sortie = comparaison.dictionnaire()["reversion"]
    assert sortie["deces"] == "2023-05-01" and sortie["total"] > 0
    assert "reversion" not in saisies.simuler({
        "naissance": "1958", "liquidation": "62"}).dictionnaire()


# -- l'assuré mort avant son départ (R. 353-6) ----------------------------------------

#: Un salarié né en 1970, qui partirait à soixante-quatre ans, mort à cinquante-
#: quatre ans ; son épouse, née en 1972, attend ses cinquante-cinq ans.
MORT_AVANT = {"naissance": "1970", "liquidation": "64", "conjoint": "1972",
              "deces": "2024-05"}


def _fictive(comparaison):
    """La liquidation de la pension que le défunt eût obtenue, au journal."""
    return next(e.contenu for e in comparaison.journal if e.id == "liquidation_deces_assure")


def test_mort_avant_son_depart_la_reversion_lit_la_pension_qu_il_eut_obtenue(saisies):
    """Mort à cinquante-quatre ans, dix ans avant son départ, l'assuré n'a pas
    de pension : la réversion se calcule sur celle qu'il « eût obtenue »
    (L. 353-1), liquidée à son décès, sur sa carrière de ce jour-là, « au titre
    de l'inaptitude au travail » (R. 353-6), au taux de 50 % « quel que soit
    l'âge de l'assuré au moment du décès » (exposé de la Cnav, « Retraite de
    l'assuré décédé »), quoique le droit ne s'ouvre pas à cet âge. Cette
    liquidation est fictive : elle s'inscrit au journal sous le décès, sans
    composantes."""
    comparaison = saisies.simuler(MORT_AVANT)
    sortie = comparaison.dictionnaire()["reversion"]
    assert (sortie["avant_le_depart"], sortie["deces"], sortie["annee"]) == (
        True, "2024-05-01", 2024)
    fictive = _fictive(comparaison)
    assert fictive.demande.donnees() == {
        "personne": "assure", "date_effet": "2024-04-01",
        "evenement": {"sorte": "deces", "date": "2024-05-01"},
        "motif": "reversion", "nature": "fictive"}
    assert fictive.carriere.au_deces and not fictive.ouverture.ouverte
    assert fictive.pensions.taux == 0.5
    general = next(l for l in sortie["regimes"] if l["regime"] == "regime_general")
    pension = next(p for p in fictive.regimes if p.regime == "regime_general")
    assert general["base"] == pytest.approx(pension.montant)
    assert general["montant"] == pytest.approx(0.54 * pension.montant)
    # Le conjoint, né en janvier 1972, a cinquante-cinq ans en janvier 2027.
    assert general["date_effet"] == "2027-02-01"
    assert {e.sorte for e in comparaison.journal if e.evenement == "deces_assure"} == {
        "evenement", "liquidation"}


@pytest.mark.parametrize("deces, effet, trimestres", [
    ("2024-03", "2024-01-01", 132), ("2024-04", "2024-04-01", 133)])
def test_la_duree_s_arrete_au_trimestre_qui_precede_le_deces(saisies, deces, effet,
                                                             trimestres):
    """« La durée d'assurance est arrêtée au dernier jour du trimestre civil qui
    précède le décès » (exposé de la Cnav) : mort en mars, l'assuré ne compte
    aucun trimestre de l'année ; en avril, le premier."""
    fictive = _fictive(saisies.simuler({**MORT_AVANT, "deces": deces}))
    assert fictive.demande.date_effet == effet
    assert fictive.releve.durees.trimestres_par_regime["regime_general"] == trimestres


def test_sans_decote_ni_coefficient_d_anticipation(saisies, simulateur):
    """La même carrière, liquidée au même jour d'un assuré vivant, serait
    décotée au régime général et abattue à l'Agirc-Arrco : la pension que le
    défunt eût obtenue ne l'est pas — taux plein de l'inaptitude (R. 353-6),
    points acquis sans coefficient."""
    from dataclasses import replace

    from retraite_notionnelle.droit import liquidation as _liquidation

    fictive = _fictive(saisies.simuler(MORT_AVANT))
    vivant = _liquidation.liquider(
        fictive.demande, _liquidation.Etat(replace(fictive.carriere, au_deces=False)),
        _liquidation.Contexte(simulateur.scenario_actuel))
    assert vivant.pensions.taux < fictive.pensions.taux == 0.5
    sans = {p.regime: p.montant for p in vivant.regimes}
    for pension in fictive.regimes:
        if pension.montant > 0:
            assert pension.montant > sans[pension.regime], pension.regime


def test_le_fonctionnaire_mort_en_activite_sans_coefficient_de_minoration(saisies):
    """« Le coefficient de minoration n'est pas applicable aux pensions de
    réversion lorsque la liquidation de la pension dont le fonctionnaire aurait
    pu bénéficier intervient après son décès » (L. 14, I, du code des
    pensions) : la pension civile se liquide au taux de 75 %, sur les services
    accomplis, et sa veuve en reçoit la moitié dès le mois qui suit."""
    comparaison = saisies.simuler({
        **MORT_AVANT, "statut": "fonctionnaire_etat"})
    assert _fictive(comparaison).pensions.taux == 0.75
    ligne, = comparaison.dictionnaire()["reversion"]["regimes"]
    assert (ligne["regime"], ligne["taux"], ligne["motif"], ligne["date_effet"]) == (
        "fonction_publique_etat", 0.5, "servie", "2024-06-01")


@pytest.mark.parametrize("mariage, motif", [("2023-05", "mariage"), ("2022-03", "servie")])
def test_la_cessation_d_activite_du_fonctionnaire_mort_en_activite_est_son_deces(
        saisies, mariage, motif):
    """La condition de L. 39 lit deux ans de services entre le mariage et la
    cessation d'activité : celle du fonctionnaire mort en activité est son
    décès, non le départ qu'il n'a pas pris. Marié un an avant sa mort, sans
    enfant, il ne laisse rien ; deux ans, la moitié de sa pension."""
    comparaison = saisies.simuler({
        **MORT_AVANT, "statut": "fonctionnaire_etat", "mariage": mariage})
    ligne, = comparaison.dictionnaire()["reversion"]["regimes"]
    assert ligne["motif"] == motif


def test_la_page_dit_la_reversion_d_un_assure_mort_avant_son_depart():
    """La carte dit le décès avant le départ, et que la réversion se calcule
    sur la pension que l'assuré aurait obtenue à son décès, sans décote."""
    from retraite_notionnelle.web.site import rendre

    _, page = rendre("/simuler", MORT_AVANT)
    assert "À votre décès, en mai 2024, avant votre départ," in page
    assert "Mort avant votre départ, vous n'auriez pas de pension" in page


# -- le partage entre conjoints et le remariage -------------------------------------

#: Un salarié né en 1958, parti à soixante-deux ans, mort en mai 2023 : marié à
#: son conjoint en juin 2000, il l'avait été de juin 1980 à juin 1995 à un autre.
PARTAGE = {"naissance": "1958", "liquidation": "62", "conjoint": "1960",
           "mariage": "2000-06", "deces": "2023-05", "ex1": "1959",
           "ex1_mariage": "1980-06", "ex1_divorce": "1995-06"}


def _sortie(saisies, requete):
    return saisies.simuler(requete).dictionnaire()["reversion"]


def test_la_duree_d_un_mariage_se_compte_en_mois_de_date_a_date():
    """« Cette durée, déterminée de date à date, est arrondie au nombre de mois
    inférieur » (R. 353-4)."""
    assert mois_de_mariage("1990-06-15", "2000-03-10") == 116
    assert mois_de_mariage("1990-06-15", "2000-03-15") == 117
    assert mois_de_mariage("2000-06-01", "2023-05-01") == 275


def test_la_reversion_se_partage_au_prorata_des_mariages(saisies):
    """275 mois de mariage avec le survivant, 180 avec le précédent conjoint :
    le survivant reçoit 275/455 de la réversion de chaque régime (L. 353-3,
    R. 353-4), et du minimum du régime général (circulaire Cnav n° 105/90,
    § 3)."""
    seul = _sortie(saisies, {cle: valeur for cle, valeur in PARTAGE.items()
                              if not cle.startswith("ex1")})
    partage = _sortie(saisies, PARTAGE)
    part = 275 / 455
    assert [l["regime"] for l in partage["regimes"]] == [l["regime"] for l in seul["regimes"]]
    for avant, apres in zip(seul["regimes"], partage["regimes"]):
        assert apres["part"] == pytest.approx(part), apres["regime"]
        assert apres["montant"] == pytest.approx(avant["montant"] * part), apres["regime"]
    general = next(l for l in partage["regimes"] if l["regime"] == "regime_general")
    avant = next(l for l in seul["regimes"] if l["regime"] == "regime_general")
    assert general["minimum"] == pytest.approx(avant["minimum"] * part)


def test_le_precedent_conjoint_remarie_avant_le_deces(saisies):
    """Remarié en 1998, le précédent conjoint ne partage plus la réversion de
    l'Agirc-Arrco, qui la retire au remariage, mais toujours celle du régime
    général, ouverte au conjoint divorcé « remarié ou non » depuis juillet
    2004 (L. 353-3)."""
    parts = {l["regime"]: l["part"]
             for l in _sortie(saisies, {**PARTAGE, "ex1_remariage": "1998-01"})["regimes"]}
    assert parts["regime_general"] == pytest.approx(275 / 455)
    assert parts["arrco"] == parts["agirc_arrco"] == 1.0


def test_le_conjoint_marie_avant_1998_garde_l_agirc_arrco_entiere(saisies):
    """« Le conjoint marié avant le 13 janvier 1998 » reçoit la réversion de
    l'Agirc-Arrco entière « à condition que le mariage précédent de la personne
    décédée ait été dissous avant le 1er juillet 1980 » (fédération
    Agirc-Arrco) ; le régime général la partage toujours."""
    requete = {"naissance": "1940", "liquidation": "60", "conjoint": "1945",
               "mariage": "1985-06", "deces": "2010-05", "ex1": "1941",
               "ex1_mariage": "1962-06", "ex1_divorce": "1979-06"}
    parts = {l["regime"]: l["part"] for l in _sortie(saisies, requete)["regimes"]}
    assert parts["regime_general"] == pytest.approx(299 / (299 + 204))
    assert parts["arrco"] == 1.0
    apres = {l["regime"]: l["part"]
             for l in _sortie(saisies, {**requete, "ex1_divorce": "1980-07"})["regimes"]}
    assert apres["arrco"] == pytest.approx(299 / (299 + 217))


def test_le_precedent_conjoint_remarie_partage_le_rafp_mais_pas_la_pension_civile(
        saisies):
    """Le conjoint divorcé remarié « perd son droit à pension » civile (L. 46
    du code des pensions) ; au RAFP, son paiement seul est « suspendu », et la
    prestation se partage toujours avec lui (arrêté du 26 novembre 2004,
    article 4)."""
    parts = {l["regime"]: l["part"] for l in _sortie(saisies, {
        **PARTAGE, "statut": "fonctionnaire_etat", "primes": "0.2",
        "ex1_remariage": "1998-01"})["regimes"]}
    assert parts["fonction_publique_etat"] == 1.0
    assert parts["rafp"] == pytest.approx(275 / 455)


@pytest.mark.parametrize("ex, part", [
    ({"naissance": "1932", "mariage": "1955-06", "divorce": "1965-06"}, 360 / 480),
    ({"naissance": "1932", "mariage": "1955-06", "divorce": "1965-06",
      "remariage": "1970-01"}, 1.0),
    ({"naissance": "1932", "mariage": "1955-06", "divorce": "1956-12"}, 1.0),
])
def test_avant_juillet_2004_le_conjoint_divorce_non_remarie_et_marie_deux_ans(
        simulateur, ex, part):
    """Avant juillet 2004, seuls partagent « le ou les précédents conjoints
    divorcés non remariés », dont le mariage « a duré au moins deux ans sauf
    lorsqu'un enfant au moins en est issu » (L. 353-3 et R. 353-4, rédactions
    de 1985) : 360 mois avec le survivant, 120 avec un précédent conjoint."""
    carriere = _carriere(simulateur, 1930, 65.0, "1935", "2003-06", mariage="1973-06",
                         ex_conjoints=({"remariage": None, **ex},))
    general, = reversion(simulateur.scenario_actuel, [("regime_general", 10_000.0, HAUTE)],
                         carriere, 2003).regimes
    assert (general.version, general.part) == ("taux_54", pytest.approx(part))


def test_le_remariage_du_survivant_eteint_les_reversions_qui_le_disent(saisies):
    """Remarié en mars 2025, le survivant perd la réversion de l'Agirc-Arrco au
    mois qui suit, et garde celle du régime général, qui ne mesure le ménage
    qu'à sa date d'effet ; remarié dès le décès, il ne reçoit rien de
    l'Agirc-Arrco, et le régime général compte le ménage ; pacsé, il garde
    tout."""
    base = {"naissance": "1958", "liquidation": "62", "conjoint": "1960",
            "deces": "2023-05", "ressources_conjoint": "15000"}
    seul = {l["regime"]: l for l in _sortie(saisies, base)["regimes"]}
    plus_tard = {l["regime"]: l for l in _sortie(saisies, {
        **base, "nouvelle_union": "mariage", "nouvelle_union_depuis": "2025-03"})["regimes"]}
    assert (plus_tard["arrco"]["fin"], plus_tard["arrco"]["montant"]) == (
        "2025-04-01", seul["arrco"]["montant"])
    assert plus_tard["regime_general"]["plafond"] == seul["regime_general"]["plafond"]
    assert plus_tard["regime_general"]["fin"] is None
    des_le_deces = {l["regime"]: l for l in _sortie(saisies, {
        **base, "nouvelle_union": "mariage"})["regimes"]}
    assert (des_le_deces["arrco"]["motif"], des_le_deces["arrco"]["montant"]) == (
        "remariage", 0.0)
    assert des_le_deces["regime_general"]["plafond"] == pytest.approx(
        1.6 * seul["regime_general"]["plafond"])
    pacse = {l["regime"]: l for l in _sortie(saisies, {
        **base, "nouvelle_union": "pacs", "nouvelle_union_depuis": "2024-01"})["regimes"]}
    assert (pacse["arrco"]["fin"], pacse["arrco"]["montant"]) == (
        None, seul["arrco"]["montant"])


@pytest.mark.parametrize("union, motif", [("concubinage", "remariage"), ("pacs", "servie")])
def test_le_concubinage_eteint_la_reversion_de_la_fonction_publique(saisies, union, motif):
    """« Le conjoint survivant ou le conjoint divorcé, qui contracte un nouveau
    mariage ou vit en état de concubinage notoire, perd son droit à pension »
    (L. 46 du code des pensions) ; le pacs, que le texte ne nomme pas, non."""
    lignes = {l["regime"]: l for l in _sortie(saisies, {
        "naissance": "1958", "liquidation": "62", "conjoint": "1960", "deces": "2023-05",
        "statut": "fonctionnaire_etat", "nouvelle_union": union})["regimes"]}
    assert lignes["fonction_publique_etat"]["motif"] == motif


def test_l_adresse_garde_les_precedents_conjoints():
    from urllib.parse import parse_qsl

    saisie = saisie_du_portage({**PARTAGE, "ex1_remariage": "1998-01",
                                "nouvelle_union": "mariage",
                                "nouvelle_union_depuis": "2025-03"})
    relue = saisie_du_portage(dict(parse_qsl(saisie.requete())))
    assert relue.ex_conjoints == saisie.ex_conjoints
    assert relue.nouvelle_union_depuis == "2025-03"


def test_la_page_dit_le_partage_et_le_remariage():
    """La carte dit la part du survivant et la fin de la réversion que son
    union nouvelle arrête ; le formulaire demande les précédents conjoints."""
    from retraite_notionnelle.web.site import rendre

    _, page = rendre("/simuler", {**PARTAGE, "nouvelle_union": "mariage",
                                  "nouvelle_union_depuis": "2025-03"})
    assert "au prorata des mariages" in page
    assert "jusqu'en avril 2025, que son union nouvelle arrête" in page
    assert 'name="ex1_mariage" value="1980-06"' in page
    assert "aucun précédent mariage" not in page



def test_la_page_dit_le_cumul_et_les_majorations_forfaitaires():
    """La carte dit la réversion réduite par la limite de cumul d'avant 2004,
    à sa date d'effet ou quand la retraite du survivant la suit, les
    majorations forfaitaires de 1982 et 1995, à leur date, et la majoration
    pour enfants à charge, jusqu'à ce que le dernier enfant ne le soit plus ou
    que la retraite du survivant commence."""
    from retraite_notionnelle.web.site import rendre

    cumul_de_1999 = {"naissance": "1925", "liquidation": "65", "conjoint": "1930",
                     "deces": "1999-05", "ressources_conjoint": "6000"}
    _, cumul = rendre("/simuler", cumul_de_1999)
    assert "avec ses propres retraites, elle dépasserait la limite de cumul" in cumul
    _, revue = rendre("/simuler", {**cumul_de_1999, "conjoint": "1940",
                                   "conjoint_retraite": "2001-03"})
    assert "de moins à partir de mars 2001, limite de cumul avec sa propre retraite" in revue
    _, ancienne = rendre("/simuler", {"naissance": "1906", "liquidation": "65",
                                      "conjoint": "1916", "deces": "1971-03"})
    assert "de plus à partir de décembre 1982, majoration forfaitaire" in ancienne
    assert "de plus à partir de janvier 1995, majoration forfaitaire" in ancienne
    enfants_de_2012 = {"naissance": "1970", "liquidation": "64", "conjoint": "1972",
                       "deces": "2024-05", "sexe": "F", "conjoint_sexe": "H", "enfants": "2",
                       "naissances": "2012, 2014"}
    _, enfants = rendre("/simuler", enfants_de_2012)
    assert "de majoration pour enfants à charge" in enfants
    assert "à partir de février 2030, plus rien à partir de février 2032" in enfants
    _, retraite = rendre("/simuler", {**enfants_de_2012, "conjoint_retraite": "2029-01"})
    assert "de majoration pour enfants à charge, plus rien à partir de février 2029" in retraite


# -- l'hypothèse de décès et la page ------------------------------------------------

@pytest.mark.parametrize("requete, deces, annee", [
    # Né le 15 janvier 1975 : il part au 1er février 2039.
    ({"naissance": "1975-01-15", "liquidation": "64", "conjoint": "1977"}, "2039-02-01", 2039),
    ({"naissance": "1955", "liquidation": "62", "conjoint": "1957"}, "2026-01-01", 2026),
])
def test_sans_deces_declare_le_deces_est_suppose_au_depart(saisies, requete, deces, annee):
    """Personne ne déclare la date de sa mort : sans elle, le conjoint déclaré
    reçoit la réversion d'un décès supposé juste après le départ, ou au 1er
    janvier de l'année courante pour qui est déjà parti (présomption
    ``deces_apres_le_depart``). Elle ne s'inscrit pas au journal, qui ne tient
    que ce qui arrive."""
    comparaison = saisies.simuler(requete)
    sortie = comparaison.dictionnaire()["reversion"]
    assert (sortie["deces"], sortie["deces_suppose"], sortie["annee"]) == (deces, True, annee)
    assert sortie["total"] > 0
    assert not any(e.sorte == "reversion" for e in comparaison.journal)


def test_la_page_montre_la_reversion_du_conjoint_declare():
    """Le bloc « Conjoint » rempli, la page dit ce que le conjoint recevrait du
    système actuel, et qu'aucun des trois autres systèmes ne verse de
    réversion ; sans conjoint, ni la section ni le montant."""
    from retraite_notionnelle.web.site import rendre

    _, page = rendre("/simuler", {"naissance": "1962-03-15", "liquidation": "2026-10",
                                  "conjoint": "1964", "ressources_conjoint": "14000"})
    assert 'id="resultats-reversion"' in page
    assert "Si vous décédiez juste après votre départ, en octobre 2026" in page
    assert "aucune réversion" in page
    assert 'name="conjoint" value="1964"' in page
    assert "que la réversion ne compte pas" not in page
    _, sans = rendre("/simuler", {"naissance": "1962-03-15", "liquidation": "2026-10"})
    assert 'id="resultats-reversion"' not in sans
    assert 'name="conjoint"' in sans


def test_la_page_dit_le_minimum_contributif_que_la_reversion_ne_compte_pas():
    """La pension du défunt portée au minimum contributif : la ligne du régime
    général dit la part du minimum, que les 54 % ne multiplient pas."""
    from retraite_notionnelle.web.site import rendre

    _, page = rendre("/simuler", {"naissance": "1955", "liquidation": "67",
                                  "conjoint": "1962", "deces": "2024-05",
                                  "unite_revenu": "moyen", "salaire": "0.3"})
    assert "de minimum contributif, que la réversion ne compte pas" in page


def test_la_page_dit_le_menage_du_conjoint():
    """Le bloc « Conjoint » demande le ménage où le conjoint vivrait, ses
    revenus d'activité et les ressources de son nouveau conjoint ; la carte ne
    suppose plus qu'il vit seul quand la saisie dit le contraire, et dit la
    ressource qu'elle prête au nouveau conjoint faute de l'avoir dite. Le
    survivant pacsé dont le ménage dépasse le plafond voit sa réversion
    réduite « avec les ressources du ménage »."""
    from retraite_notionnelle.web.site import rendre

    requete = {"naissance": "1958", "liquidation": "62", "conjoint": "1960",
               "deces": "2023-05", "ressources_conjoint": "15000"}
    _, seul = rendre("/simuler", requete)
    assert "un conjoint qui vivrait seul après votre décès" in seul
    for nom in ("activite_conjoint", "nouvelle_union", "ressources_nouveau_conjoint"):
        assert f'name="{nom}"' in seul
    _, pacse = rendre("/simuler", {**requete, "nouvelle_union": "pacs"})
    assert "un conjoint qui vivrait seul" not in pacse
    assert "aucune ressource à son nouveau conjoint, faute de l'avoir dite" in pacse
    assert '<option value="pacs" selected' in pacse
    _, menage = rendre("/simuler", {**requete, "nouvelle_union": "pacs",
                                    "ressources_nouveau_conjoint": "30000"})
    assert "réduite : avec les ressources du ménage, elle dépasserait le plafond" in menage
