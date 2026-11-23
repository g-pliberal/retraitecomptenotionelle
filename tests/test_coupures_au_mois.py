"""Les règles qu'un texte change en cours d'année, coupées à la date d'effet.

Le moteur choisissait la période d'un régime à l'année, et servait à toute une
année la règle d'un texte entré en vigueur en avril ou en septembre. Une
période déclare désormais, au jour, les dates d'effet qu'elle liquide
(`date_effet`, docs/architecture.md, § 4.6), et la liquidation la choisit à la
date d'effet de la pension ; l'acquisition garde les années. Trois textes
coupent ainsi leur année (feuille de route, action 131) :

- l'ordonnance n° 82-270 du 26 mars 1982, en vigueur le 1er avril 1983
  (article 9), et le décret n° 82-1054, le même jour chez les salariés
  agricoles (article 2) : une pension de janvier à mars 1983 relève encore du
  taux qui croît avec l'âge ;
- à la CAVEC, l'arrêté du 20 août 2018, publié le 4 septembre, et celui du
  4 juillet 2025, publié le 6 juillet, tous deux sans date d'effet propre :
  la majoration de report tombe à 0,75 % le 5 septembre 2018, remonte à
  1,25 % le 7 juillet 2025, avec la majoration pour trois enfants ;
- au RACL, l'arrêté du 13 mai 2025, publié le 15 : la règle des deux autres
  régimes de l'IRCEC dès le 16 mai 2025.

L'assuré présumé né le 15 liquide au 1er du mois qui suit son anniversaire
(fiche `date_effet_mois_suivant`) : né le 15 février 1923, il part à soixante
ans le 1er mars 1983.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.types_du_pont.carriere import Metier
from retraite_notionnelle.donnees.regimes import CatalogueRegimes

from facade import Carriere, Simulateur, commun

date_d_effet = commun.date_d_effet
periode_de_liquidation = commun.periode_de_liquidation

RACINE = Path(__file__).resolve().parents[1]
RACINE_DONNEES = RACINE / "data"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int, mois: int,
              liquidation: float, debut: float, sexe: str = "H", enfants: int = 0):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, mois_naissance=mois, jour_naissance=15, sexe=sexe,
        metiers=[Metier(affiliation=affiliation, age_debut=debut, niveau_salaire=1.0)],
        age_liquidation=liquidation, macro=simulateur.macro, nombre_enfants=enfants,
    )
    resultat = simulateur.scenario_actuel.calculer(carriere)
    return (date_d_effet(carriere), resultat,
            {p.regime: p for p in resultat.pensions_par_regime})


def _coefficient(detail: str) -> float:
    """Le coefficient écrit dans le détail d'une pension en points, 1 sans."""
    for marque in ("coefficient d'anticipation ", "coefficient de majoration "):
        if marque in detail:
            return float(detail.split(marque)[1].split()[0])
    return 1.0


def _majoration(resultat, regime: str) -> float:
    """La majoration pour enfants que le scénario 1 sert à ce régime."""
    for avantage in resultat.avantages_appliques:
        if avantage.code == "majoration_enfants":
            return dict(avantage.par_regime).get(regime, 0.0)
    return 0.0


# -- le 1er avril 1983 ------------------------------------------------------------


@pytest.mark.parametrize("affiliation,regime", [
    ("salarie_prive_non_cadre", "regime_general"),
    ("salarie_agricole", "msa_salaries"),
])
def test_le_taux_plein_a_soixante_ans_vaut_pour_les_pensions_d_avril_1983(
        simulateur, affiliation, regime):
    """Cent soixante trimestres à soixante ans : 25 % pour la pension du 1er
    mars 1983, quand le taux croît encore avec l'âge, 50 % pour celle du 1er
    avril. Le moteur servait 50 % dès janvier."""
    effet, resultat, pensions = _calculer(simulateur, affiliation, 1923, 2, 60.0, 20.0)
    assert effet == "1983-03-01"
    assert resultat.taux_liquidation == pytest.approx(0.25)
    mars = pensions[regime].montant
    effet, resultat, pensions = _calculer(simulateur, affiliation, 1923, 3, 60.0, 20.0)
    assert effet == "1983-04-01"
    assert resultat.taux_liquidation == pytest.approx(0.50)
    assert pensions[regime].montant == pytest.approx(2 * mars, rel=1e-3)


def test_la_periode_de_1983_cotise_toute_l_annee(simulateur):
    """La coupure ne vise que la liquidation : 1983 cotise au taux de la
    période de 1983, quelle que soit la date d'effet d'une pension."""
    regime = simulateur.catalogue["regime_general"]
    mars, avril = (periode_de_liquidation(regime, DateMois(1983, mois)) for mois in (3, 4))
    # Le portage rend les paramètres qu'il lit à la date (`aLaDate`) : la
    # liquidation du jour d'effet, la cotisation de son année.
    assert (mars, avril) == (regime.a_la_date("1983-03-01"), regime.a_la_date("1983-04-01"))
    rangs = regime.rangs
    assert rangs(mars)[0] == rangs(regime.a_la_date("1979-01-01"))[0] != rangs(avril)[0]
    assert regime.liquidation[rangs(avril)[0]]["du"] == "1983-04-01"
    assert rangs(mars)[3] == rangs(avril)[3]
    assert regime.cotisation[rangs(avril)[3]]["du"] == 1983


# -- la CAVEC ------------------------------------------------------------------


@pytest.mark.parametrize("naissance,mois,effet,coefficient", [
    # Quatre trimestres pleins après soixante-cinq ans : 1,25 % chacun
    # jusqu'au 4 septembre 2018, 0,75 % ensuite ; 1,25 % de nouveau depuis le
    # 7 juillet 2025.
    (1952, 8, "2018-09-01", 1.05),
    (1952, 9, "2018-10-01", 1.03),
    (1959, 6, "2025-07-01", 1.03),
    (1959, 7, "2025-08-01", 1.05),
])
def test_la_cavec_majore_le_report_au_taux_de_la_date_d_effet(
        simulateur, naissance, mois, effet, coefficient):
    date, _, pensions = _calculer(simulateur, "expert_comptable", naissance, mois,
                                  66.0, 30.0)
    assert date == effet
    assert _coefficient(pensions["cavec_complementaire"].detail) == pytest.approx(
        coefficient)


def test_la_cavec_majore_pour_trois_enfants_depuis_le_7_juillet_2025(simulateur):
    """L'arrêté du 4 juillet 2025 n'a pas de date d'effet propre : la pension
    du 1er août 2025 est majorée de 10 %, celle du 1er juillet ne l'est pas."""
    effet, resultat, _ = _calculer(simulateur, "expert_comptable", 1960, 6, 65.0, 30.0,
                                   sexe="F", enfants=3)
    assert effet == "2025-07-01"
    assert _majoration(resultat, "cavec_complementaire") == 0.0
    effet, resultat, pensions = _calculer(simulateur, "expert_comptable", 1960, 7, 65.0,
                                          30.0, sexe="F", enfants=3)
    assert effet == "2025-08-01"
    assert _majoration(resultat, "cavec_complementaire") == pytest.approx(
        0.10 * pensions["cavec_complementaire"].montant)


# -- le RACL -------------------------------------------------------------------


def test_le_racl_rejoint_l_ircec_le_16_mai_2025(simulateur):
    """Parti à soixante-deux ans et neuf mois, sans sa durée : la pension du 1er
    mai 2025 perd encore 5 % par année entamée jusqu'à soixante-sept ans, 25 % ;
    celle du 1er juin prend les coefficients du régime de base, plus favorables,
    trois trimestres à 1,25 %. Né en août 1962 et entré à vingt et un ans et
    quatre mois, en décembre 1983, il gagne cette année-là 917 €, qui valent un
    trimestre de 200 heures au SMIC du 1er janvier 1983, 3,093191 € (R. 351-9
    CSS : 917 / 618,64 = 1,5) ; puis 164 de 1984 à 2024 et un en 2025 : 166
    des 169 de sa génération."""
    effet, _, pensions = _calculer(simulateur, "auteur_lyrique", 1962, 7, 62.75, 21 + 4 / 12)
    assert effet == "2025-05-01"
    assert _coefficient(pensions["ircec_racl"].detail) == pytest.approx(0.75)
    effet, _, pensions = _calculer(simulateur, "auteur_lyrique", 1962, 8, 62.75, 21 + 4 / 12)
    assert effet == "2025-06-01"
    assert _coefficient(pensions["ircec_racl"].detail) == pytest.approx(0.9625)


# -- les coupures au jour -------------------------------------------------------


def test_les_regimes_qu_un_texte_coupe_au_jour():
    """Les régimes dont une ligne de liquidation, de servi ou de structure
    s'ouvre ou se ferme un autre jour qu'un 1er janvier : ceux qu'un texte
    coupe en cours d'année."""
    catalogue = CatalogueRegimes(RACINE_DONNEES)
    coupees = {regime.code for regime in catalogue
               for bloc in ("liquidation", "servi", "structure")
               for ligne in getattr(regime, bloc)
               for jour in (ligne["du"], ligne["au"])
               if jour is not None and not jour.endswith("-01-01")}
    assert coupees == {"regime_general", "msa_salaries", "cavec_complementaire",
                       "ircec_racl", "cps_saint_pierre_et_miquelon", "cssm_mayotte",
                       # statuts de 2011, en vigueur le 1er juillet 2011
                       "cavamac_complementaire",
                       # article 15 des statuts récrit, en vigueur le 10 janvier 2024
                       "cavp_complementaire",
                       # arrêté du 22 mars 2017, en vigueur le 30 mars 2017
                       "carmf_complementaire", "asv_conventionnes",
                       # statuts de 2007, en vigueur le 11 octobre 2007, et de
                       # 2011, le 1er juillet 2011
                       "carcdsf_complementaire",
                       # arrêté du 31 juillet 2015, en vigueur le 3 octobre 2015
                       "carpimko_complementaire",
                       # règlement de 2007, « à compter du 1er avril 2007 »
                       "banque_de_france",
                       # décret n° 2012-1129, en vigueur le 7 octobre 2012
                       "organic_avant_1973", "cancava_avant_1973",
                       # ordonnance n° 82-270, en vigueur le 1er avril 1983
                       "organic", "cancava",
                       # loi n° 2023-270, pensions prenant effet à compter du
                       # 1er septembre 2023
                       "cnavpl",
                       # décret n° 2006-1325, en vigueur le 2 novembre 2006
                       "cavimac",
                       # décrets de juin 2008, pour les pensions prenant effet
                       # à compter du 1er juillet 2008
                       "sncf", "ratp", "ieg", "opera_de_paris", "comedie_francaise",
                       # les dates lues le 23 novembre 2026, une à une dans
                       # `test_frontieres_au_jour.py`
                       "fonction_publique_etat", "cnracl", "fspoeie", "msa_non_salaries",
                       "ircantec", "rafp", "mines", "asv_directeurs_laboratoire", "cnbf"}


# -- les deux moteurs ----------------------------------------------------------

REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "20", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "60", "naissance": "1923", "primes": "0",
    "profil": "plat", "projection": "cor_reference", "salaire": "1", "sexe": "H",
    "statut": "salarie_prive_non_cadre", "stock": "prix", "table": "unisexe",
}
#: De part et d'autre de chaque coupure.
CAS = [
    {"naissance_mois": "2"},
    {"naissance_mois": "3"},
    {"statut": "salarie_agricole", "naissance_mois": "2"},
    {"statut": "salarie_agricole", "naissance_mois": "3"},
    *({"statut": "expert_comptable", "naissance": naissance, "naissance_mois": mois,
       "liquidation": "66", "debut": "30"}
      for naissance, mois in (("1952", "8"), ("1952", "9"), ("1959", "6"), ("1959", "7"))),
    *({"statut": "expert_comptable", "sexe": "F", "enfants": "3", "naissance": "1960",
       "naissance_mois": mois, "liquidation": "65", "debut": "30"}
      for mois in ("6", "7")),
    *({"statut": "auteur_lyrique", "naissance": "1962", "naissance_mois": mois,
       "liquidation": "62.75", "debut": "21"}
      for mois in ("7", "8")),
]


def test_les_deux_moteurs_coupent_au_meme_jour():
    """Chaque étape de la liquidation écrit la même donnée en Python et en
    JavaScript, de part et d'autre de chaque coupure."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    from outils_sorties import sortie_figee

    requetes = [{**REQUETE, **cas} for cas in CAS]
    obtenus = sortie_figee("comparer-liquidation.mjs", requetes)
    assert not any("erreur" in obtenu for obtenu in obtenus), obtenus
