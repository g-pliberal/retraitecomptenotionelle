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
              enfants: int = 0, sexe_conjoint: str = "F",
              invalidite: str | None = None, sexe: str = "H",
              naissances: tuple[str, ...] = ()) -> Carriere:
    """Un salarié né en janvier ``naissance``, parti à ``depart`` ans, ses
    enfants nés aux dates ``naissances`` quand elles sont dites, et son
    conjoint, invalide depuis ``invalidite`` s'il est dit ; le décès ouvre la
    réversion. Les pensions, elles, sont données à :func:`reversion` : seule
    la règle est en cause ici."""
    return Carriere.depuis_profil(
        naissance, sexe, "salarie_prive", 21.0, depart, simulateur.macro,
        nombre_enfants=enfants, naissances_enfants=naissances,
        conjoint={"naissance": conjoint, "sexe": sexe_conjoint, "mariage": mariage,
                  "ressources": ressources, "invalidite": invalidite},
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


def test_l_echeancier_reverse_la_pension_sans_le_minimum_contributif(contexte):
    """Un petit salaire parti au taux plein et porté au minimum contributif :
    la part du minimum dans sa pension, menée au décès comme elle, n'entre pas
    dans la base, et la ligne la dit. La survivante n'a pas l'âge du taux
    plein : la majoration de 11,1 % attend, hors du montant."""
    sortie = contexte.simuler(Saisie.depuis_requete({
        "naissance": "1955", "liquidation": "67", "conjoint": "1962",
        "deces": "2024-05", "unite_revenu": "moyen", "salaire": "0.3"})).dictionnaire()
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


def test_l_echeancier_reverse_la_majoration_de_l_agirc_arrco(contexte):
    """La même carrière, avec trois enfants et sans : le régime général ne
    reverse pas la majoration du défunt, mais majore de 10 % la réversion du
    survivant de trois enfants (L. 353-1, R. 353-2) ; l'Agirc-Arrco reverse
    la majoration du défunt en entier."""
    def lignes(enfants):
        sortie = contexte.simuler(Saisie.depuis_requete({
            "naissance": "1958", "liquidation": "62", "conjoint": "1960",
            "deces": "2023-05", "enfants": enfants})).dictionnaire()["reversion"]
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
def test_l_echeancier_dit_quel_rafp_a_ete_verse_en_capital(contexte, primes, en_capital):
    """Aux primes d'un cinquantième du traitement, le fonctionnaire n'a pas les
    5 125 points du RAFP : il le touche en une fois (décret n° 2004-569,
    article 9), et son conjoint n'en reçoit rien ; aux primes d'un
    cinquième, une rente, dont il reçoit la moitié."""
    sortie = contexte.simuler(Saisie.depuis_requete({
        "naissance": "1958", "liquidation": "62", "statut": "fonctionnaire_etat",
        "primes": primes, "conjoint": "1960", "deces": "2023-05"})).dictionnaire()
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
    ({"conjoint_invalidite": "2024-02"}, "« conjoint_invalidite » ne sert qu'à la réversion"),
    ({"conjoint": "1962", "conjoint_invalidite": "1961"},
     "L'invalidité du conjoint précède sa naissance"),
    ({"conjoint": "1962", "conjoint_invalidite": "2024-13"},
     "L'invalidité du conjoint « 2024-13 »"),
])
def test_la_saisie_refuse_ce_qui_ne_tient_pas(requete, message):
    with pytest.raises(ErreurSaisie, match=message):
        Saisie.depuis_requete({"naissance": "1960", "liquidation": "2024-01", **requete})


def test_l_adresse_garde_le_conjoint_et_le_deces():
    from urllib.parse import parse_qsl

    saisie = Saisie.depuis_requete({
        "naissance": "1960", "liquidation": "2024-01", "conjoint": "1962-03",
        "mariage": "1985-06", "ressources_conjoint": "12000",
        "conjoint_invalidite": "2028-04", "deces": "2031-10"})
    relue = Saisie.depuis_requete(dict(parse_qsl(saisie.requete())))
    assert (relue.conjoint, relue.mariage, relue.ressources_conjoint,
            relue.conjoint_invalidite, relue.deces) == (
        "1962-03", "1985-06", 12000.0, "2028-04", "2031-10")
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


# -- l'hypothèse de décès et la page ------------------------------------------------

@pytest.mark.parametrize("requete, deces, annee", [
    # Né en janvier 1975, présumé le 15 : il part au 1er février 2039.
    ({"naissance": "1975", "liquidation": "64", "conjoint": "1977"}, "2039-02-01", 2039),
    ({"naissance": "1955", "liquidation": "62", "conjoint": "1957"}, "2026-01-01", 2026),
])
def test_sans_deces_declare_le_deces_est_suppose_au_depart(contexte, requete, deces, annee):
    """Personne ne déclare la date de sa mort : sans elle, le conjoint déclaré
    reçoit la réversion d'un décès supposé juste après le départ, ou au 1er
    janvier de l'année courante pour qui est déjà parti (présomption
    ``deces_apres_le_depart``). Elle ne s'inscrit pas au journal, qui ne tient
    que ce qui arrive."""
    comparaison = contexte.simuler(Saisie.depuis_requete(requete))
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
