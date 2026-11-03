"""La CAFAT et Wallis-et-Futuna recoupées à leurs sources (action 145).

LE RENDEMENT DE LA CAFAT est celui que son conseil d'administration fixe
chaque année : « Au mois de mars de chaque année, tenant compte du nombre de
points à servir dans l'année, le conseil d'administration de la CAFAT fixe la
valeur du point (valeur de service), la valeur de référence (prix
d'acquisition) et le taux de rendement (c'est-à-dire le rapport entre la
valeur de service et la valeur de référence) » (Chambre territoriale des
comptes de Nouvelle-Calédonie, « CAFAT, exercices 2020 et suivants », 2022,
p. 62). Toute la cotisation achète des points, sans taux d'appel : « Max de
points pour 2025 : 336 », soit 14 % de douze plafonds de 548 600 F CFP
divisés par 2 738,93 (fiche des paramètres de janvier 2026). Le moteur
applique le rendement de l'année de la liquidation aux cotisations
revalorisées de toute la carrière (`droit/liquider`) : la série est celle de
chaque année de départ, au lieu des 10 % constants que la fiche de régime
déduisait de la cotisation et du barème de 2026.

LE TAUX DE WALLIS-ET-FUTUNA est celui de la retraite seule : la caisse publie
le total de ses cotisations, 27 % en 2020, quand « la contribution est de
21 % des salaires, supporté aux deux tiers par les employeurs et un tiers
pour les salariés », la caisse gérant aussi « un régime de prestation
familiale, alimenté par des cotisations employeurs de 6 % » (Cour des
comptes, observations définitives S2022-2223, 2022, p. 33).

Les sources, lues hors du dépôt, et leurs pages : la note
`docs/archives/feuille_de_route/145/2026-11-02-recherches-complementaires.md`.
"""

from __future__ import annotations

import csv

import pytest

from retraite_notionnelle.config import RACINE_DONNEES
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.scenarios.actuel import Rendements

CAFAT = "cafat_nouvelle_caledonie"
WALLIS = "wallis_et_futuna"

#: Valeur de service et valeur de référence du point de la CAFAT, en F CFP :
#: annexe 7 du rapport de la chambre (p. 102), de 2015 à 2021 ; fiches « Les
#: paramètres » de la CAFAT (cafat.nc), de 2022 à 2026 — le point de 247,43
#: au 1er avril 2022, de 256,09 depuis le 1er avril 2023.
#: En 2017 et 2018, la valeur de service de l'annexe est la moyenne de l'année
#: des valeurs du point que la caisse fixe au 1er avril, et que ses fiches
#: publient : 239,28 = ¼ × 238,26 + ¾ × 239,62 ; 241,87 = ¼ × 239,62 + ¾ ×
#: 242,62. Le dépôt garde l'annexe, que cite la décision du propriétaire.
VALEURS_DU_POINT = {
    2015: (236.02, 2280.42),
    2016: (237.96, 2321.93),
    2017: (239.28, 2358.00),
    2018: (241.87, 2407.10),
    2019: (244.46, 2452.37),
    2020: (244.46, 2481.52),
    2021: (245.44, 2517.31),
    2022: (247.43, 2564.04),
    2023: (256.09, 2681.57),
    2024: (256.09, 2709.95),
    2025: (256.09, 2738.93),
    2026: (256.09, 2845.44),
}

#: Le rendement d'avant 2015, que donne l'avis n° 12/2008 du conseil
#: économique et social de Nouvelle-Calédonie, du 17 octobre 2008 (p. 4) :
#: « Ce dernier qui était de 12,45 % en 2001, n'était plus que de 10,98 % au
#: 31 décembre 2007. Il devrait atteindre 10,35 % en 2008 ». La chambre écrit
#: « 12 % en 2008 » et « plus de 25 % en 2000 » (p. 63) : les deux sources se
#: contredisent, d'où le niveau `moyenne`.
RENDEMENTS_DU_CONSEIL = {2001: 0.1245, 2007: 0.1098, 2008: 0.1035}

#: La valeur du point au 1er avril de l'année, que publient les fiches des
#: paramètres de la CAFAT (« valeur du point » du premier trimestre suivant).
POINTS_DES_FICHES = {2016: 238.26, 2017: 239.62, 2018: 242.62}

#: Le taux total des cotisations de la caisse de Wallis-et-Futuna (CPSWF,
#: page « Les taux de cotisation », lue le 16 octobre 2026), au 1er janvier,
#: et la part du salarié : « les taux de cotisations augmentent annuellement ».
TAUX_DE_LA_CAISSE = {
    2009: (0.1710, 0.0370),
    2010: (0.1800, 0.0400),
    2011: (0.1890, 0.0430),
    2012: (0.1980, 0.0460),
    2013: (0.2070, 0.0490),
    2014: (0.2160, 0.0520),
    2015: (0.2250, 0.0550),
    2016: (0.2340, 0.0580),
    2017: (0.2430, 0.0610),
    2018: (0.2520, 0.0640),
    2019: (0.2610, 0.0670),
    2020: (0.2700, 0.0700),
}

#: Les prestations familiales, à la charge de l'employeur seul (Cour des
#: comptes, p. 33 ; « Charges patronales de 20% sur les salaires : 14% pour les
#: retraites 6% pour les prestations familiales », expertise-comptable.wf).
PRESTATIONS_FAMILIALES = 0.06

#: Le taux de la retraite que lisent les rapports annuels de l'IEOM et la Cour
#: des comptes, et sa part salariale quand ils la donnent : « au 1er janvier
#: 2010 le taux des cotisations a été porté à 12 % (contre 11,1 % au
#: 01/01/2009), soit 4 % de part salariale et 8 % à la charge de l'employeur »
#: (IEOM, rapport 2010) ; 15,6 % en 2014 (Assemblée nationale, rapport
#: d'information n° 2667, p. 10) ; 16,5 % en 2015, 17,4 % en 2016, 19,2 % en
#: 2018, 20,1 % en 2019 (IEOM) ; 21 % depuis 2020 (Cour des comptes ; IEOM,
#: rapport 2021 : « soit 7 % pour la part salariale et 14 % pour la part
#: patronale »).
TAUX_DE_RETRAITE_LUS = {
    2009: (0.111, None),
    2010: (0.120, 0.040),
    2014: (0.156, None),
    2015: (0.165, 0.055),
    2016: (0.174, 0.058),
    2018: (0.192, None),
    2019: (0.201, 0.067),
    2020: (0.210, 0.070),
}

#: La caisse locale de retraites, avant 2009 : « les cotisations patronales et
#: salariales, qui s'élèvent respectivement à 6% et 3% des salaires bruts »
#: (IEOM, rapport annuel 2004, p. 64 ; redit pour 2008 au rapport 2008, p. 85).
#: Le dépôt les prolonge jusqu'à la création du régime, faute de rapport plus
#: ancien lu.
TAUX_DE_LA_CAISSE_LOCALE = (0.09, 0.03)


@pytest.fixture(scope="module")
def rendements() -> Rendements:
    return Rendements(RACINE_DONNEES)


@pytest.fixture(scope="module")
def catalogue() -> CatalogueRegimes:
    return CatalogueRegimes(RACINE_DONNEES)


def test_le_rendement_de_la_cafat_est_celui_que_la_caisse_fixe_chaque_annee(rendements):
    """De 10,35 % en 2015 à 9 % en 2026 : la valeur de service divisée par la
    valeur de référence de l'année, au centième de point que la caisse publie."""
    for annee, (service, reference) in VALEURS_DU_POINT.items():
        rendement, fiabilite = rendements.rendement(CAFAT, annee)
        assert rendement == pytest.approx(service / reference, abs=5e-5), annee
        assert fiabilite == Fiabilite.HAUTE, annee


def test_l_annexe_de_la_chambre_est_la_moyenne_des_points_que_fixe_la_caisse(rendements):
    """Le point change au 1er avril : la moyenne de l'année le pèse d'un quart
    à sa valeur de l'année d'avant. Le rendement que donnerait la valeur du
    1er avril s'écarte de celui de l'annexe de 0,03 point au plus."""
    for annee in (2017, 2018):
        moyenne = 0.25 * POINTS_DES_FICHES[annee - 1] + 0.75 * POINTS_DES_FICHES[annee]
        assert moyenne == pytest.approx(VALEURS_DU_POINT[annee][0], abs=0.005), annee
    for annee, point in POINTS_DES_FICHES.items():
        rendement, _ = rendements.rendement(CAFAT, annee)
        assert point / VALEURS_DU_POINT[annee][1] == pytest.approx(rendement, abs=3.5e-4), annee


def test_avant_2015_le_rendement_est_celui_du_conseil_economique_et_social(rendements):
    for annee, publie in RENDEMENTS_DU_CONSEIL.items():
        rendement, fiabilite = rendements.rendement(CAFAT, annee)
        assert rendement == pytest.approx(publie, abs=1e-6), annee
        assert fiabilite == Fiabilite.MOYENNE, annee


def test_hors_des_annees_publiees_le_rendement_se_dit_estime(rendements):
    """Avant 2001, rien n'est publié : la valeur de 2001 se prolonge jusqu'à
    la création du régime. De 2002 à 2006, la ligne droite entre les deux
    valeurs du conseil ; de 2009 à 2014, les 10,35 % de 2008, que la chambre
    donne encore en 2015 ; au-delà de 2026, le dernier rendement fixé."""
    premier, _ = rendements.rendement(CAFAT, 2001)
    for annee in (1958, 1980, 2000):
        assert rendements.rendement(CAFAT, annee) == (premier, Fiabilite.ESTIMEE), annee
    serie = [rendements.rendement(CAFAT, annee) for annee in range(2001, 2008)]
    for (avant, _), (apres, _) in zip(serie, serie[1:]):
        assert apres < avant
    for annee, (rendement, fiabilite) in zip(range(2002, 2007), serie[1:-1]):
        attendu = 0.1245 + (0.1098 - 0.1245) * (annee - 2001) / 6
        assert rendement == pytest.approx(attendu, abs=5e-6), annee
        assert fiabilite == Fiabilite.ESTIMEE, annee
    for annee in range(2009, 2015):
        rendement, fiabilite = rendements.rendement(CAFAT, annee)
        assert rendement == pytest.approx(0.1035, abs=1e-6), annee
        assert fiabilite == Fiabilite.ESTIMEE, annee
    dernier, fiabilite_derniere = rendements.rendement(CAFAT, 2026)
    for annee in (2027, 2060, 2100):
        assert rendements.rendement(CAFAT, annee) == (dernier, fiabilite_derniere), annee


def test_chaque_annee_de_la_cafat_a_une_ligne_et_une_seule():
    """Le moteur sert la première ligne qui couvre l'année : deux lignes qui se
    recouvrent en cacheraient une sans le dire."""
    chemin = RACINE_DONNEES / "reference" / "regimes" / "rendements_points.csv"
    with chemin.open(encoding="utf-8") as flux:
        lignes = [ligne for ligne in csv.DictReader(
            l for l in flux if not l.lstrip().startswith("#")) if ligne["regime"] == CAFAT]
    couvertures = [range(int(l["debut"]), int(l["fin"]) + 1) for l in lignes]
    for annee in range(1958, 2101):
        assert sum(annee in c for c in couvertures) == 1, annee


def test_wallis_et_futuna_cotise_le_taux_de_la_caisse_moins_les_prestations_familiales(
        catalogue):
    """Chaque année, six points de moins que le total de la caisse, tous à la
    charge de l'employeur : la part du salarié reste la sienne, un tiers."""
    regime = catalogue[WALLIS]
    for annee in range(2009, 2027):
        total, salarie = TAUX_DE_LA_CAISSE[min(annee, 2020)]
        periode = regime.periode(annee)
        assert periode.taux_cotisation_retraite == pytest.approx(
            total - PRESTATIONS_FAMILIALES, abs=1e-9), annee
        assert periode.taux_cotisation_salarie == pytest.approx(salarie, abs=1e-5), annee
        assert periode.part_salariale == pytest.approx(1 / 3, abs=1e-4), annee


def test_les_taux_que_lisent_l_ieom_et_la_cour_des_comptes_sont_ceux_de_la_fiche(catalogue):
    regime = catalogue[WALLIS]
    for annee, (taux, salarie) in TAUX_DE_RETRAITE_LUS.items():
        periode = regime.periode(annee)
        assert periode.taux_cotisation_retraite == pytest.approx(taux, abs=1e-9), annee
        if salarie is not None:
            assert periode.taux_cotisation_salarie == pytest.approx(salarie, abs=1e-5), annee


def test_avant_2009_la_caisse_locale_cotisait_neuf_pour_cent(catalogue):
    regime = catalogue[WALLIS]
    taux, salarie = TAUX_DE_LA_CAISSE_LOCALE
    for annee in range(regime.creation, 2009):
        periode = regime.periode(annee)
        assert periode.taux_cotisation_retraite == pytest.approx(taux, abs=1e-9), annee
        assert periode.taux_cotisation_salarie == pytest.approx(salarie, abs=1e-5), annee
