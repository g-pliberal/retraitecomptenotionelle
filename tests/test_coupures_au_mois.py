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

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest
import yaml

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.donnees.regimes import CatalogueRegimes
from retraite_notionnelle.droit.commun import date_d_effet, periode_de_liquidation
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
RACINE_DONNEES = RACINE / "data"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _calculer(simulateur: Simulateur, affiliation: str, naissance: int, mois: int,
              liquidation: float, debut: float, sexe: str = "H", enfants: int = 0):
    carriere = Carriere.depuis_parcours(
        annee_naissance=naissance, mois_naissance=mois, sexe=sexe,
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
    assert regime.periode(1983).debut == 1983
    assert periode_de_liquidation(regime, DateMois(1983, 3)).debut == 1979
    assert periode_de_liquidation(regime, DateMois(1983, 4)).debut == 1983


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
    trois trimestres à 1,25 %."""
    effet, _, pensions = _calculer(simulateur, "auteur_lyrique", 1962, 7, 62.75, 21.0)
    assert effet == "2025-05-01"
    assert _coefficient(pensions["ircec_racl"].detail) == pytest.approx(0.75)
    effet, _, pensions = _calculer(simulateur, "auteur_lyrique", 1962, 8, 62.75, 21.0)
    assert effet == "2025-06-01"
    assert _coefficient(pensions["ircec_racl"].detail) == pytest.approx(0.9625)


# -- les dates d'effet des périodes --------------------------------------------


def test_les_dates_d_effet_partagent_les_annees_sans_trou_ni_doublon():
    """Chaque jour d'effet, autant de périodes liquident qu'il y en a qui
    couvrent son année : une borne au jour déplace la coupure d'une période à
    sa voisine, n'en crée ni n'en perd une, et les morceaux que la datation
    des taux découpe se la partagent (``morceau_d_annees``)."""
    catalogue = CatalogueRegimes(RACINE_DONNEES)
    coupees = set()
    for regime in catalogue:
        for periode in regime.periodes:
            if periode.date_effet is not None:
                coupees.add(regime.code)
        for annee in range(1930, 2071):
            couvrent = [p for p in regime.periodes if p.couvre(annee)]
            for mois in range(1, 13):
                jour = f"{annee:04d}-{mois:02d}-01"
                liquident = [p for p in regime.periodes if p.liquide(jour)]
                assert len(liquident) == len(couvrent), (regime.code, jour)
    assert coupees == {"regime_general", "msa_salaries", "cavec_complementaire",
                       "ircec_racl", "cps_saint_pierre_et_miquelon", "cssm_mayotte"}


@pytest.mark.parametrize("bornes,message", [
    ("1983-04-01", "s'écrit"),
    (["1983-04-01"], "s'écrit"),
    (["avril 1983", None], "AAAA-MM-JJ"),
    (["1983-04-01", "1983-01-01"], "avant son début"),
    (["1981-04-01", "1994-01-01"], "plus d'un an"),
    (["1983-04-01", None], "plus d'un an"),
])
def test_le_chargeur_refuse_une_date_d_effet_mal_ecrite(tmp_path, bornes, message):
    """Une borne qui n'est pas un jour, qui finit avant de commencer, ou qui
    déplace la période de plus d'un an au lieu de couper une année."""
    source = RACINE_DONNEES / "reference"
    dossier = tmp_path / "reference" / "regimes"
    dossier.mkdir(parents=True)
    shutil.copytree(source / "regles", tmp_path / "reference" / "regles")
    shutil.copy(source / "regimes" / "_schema.yaml", dossier / "_schema.yaml")
    regime = yaml.safe_load((source / "regimes" / "regime_general.yaml").read_text(
        encoding="utf-8"))
    for periode in regime["periodes"]:
        if periode["debut"] == 1983:
            periode["date_effet"] = bornes
    (dossier / "regime_general.yaml").write_text(
        yaml.safe_dump(regime, allow_unicode=True), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        CatalogueRegimes(tmp_path)


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
    from test_liquidation import _ecarts, _python

    requetes = [{**REQUETE, **cas} for cas in CAS]
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
