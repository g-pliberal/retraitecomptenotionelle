"""Les versements uniques des petites pensions (action 138, étape 17).

La pension du régime général sous le seuil de R. 351-26 n'est pas servie : un
versement forfaitaire unique de quinze annuités la remplace, jusqu'à ce que la
loi n° 2014-40 le réserve, depuis 2016, à qui a pris sa première retraite avant
(fiche ``versement_forfaitaire_unique``). L'Agirc-Arrco verse en capital
l'allocation d'au plus cent points, au coefficient de l'âge révolu — avant
2019, l'Arrco jusqu'à cent points, l'Agirc sous cinq cents (fiche
``versement_unique_agirc_arrco``) — ; l'Ircantec, sous trois cents points, les
points au salaire de référence de l'année d'avant (fiche
``versement_unique_ircantec``). Le capital versé à l'assuré de ces deux-là ne
laisse pas de réversion.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import LigneRelevee
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.droit.commun import PensionRegime
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.droit.completer import (
    FICHE_DU_VERSEMENT_AGIRC_ARRCO, FICHE_DU_VERSEMENT_FORFAITAIRE,
    FICHE_DU_VERSEMENT_IRCANTEC, _seuil_a_la_date, coefficient_du_versement,
    verser_en_capital)
from retraite_notionnelle.saisie import Saisie
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]

#: 175 francs, le seuil du 1er juillet 1974, en euros.
CENT_SOIXANTE_QUINZE_FRANCS = 175 / 6.55957


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _regle(simulateur, nom: str, date: str) -> dict:
    return simulateur.scenario_actuel.fiches_datees.regle(nom, date)


def _pensions(simulateur, naissance: int, age: float,
              lignes: list[tuple[int, str, float]]) -> dict[str, PensionRegime]:
    """Les pensions d'une carrière que son relevé dit, ligne à ligne."""
    carriere = simulateur.carriere_releve(
        annee_naissance=naissance, sexe="F", age_liquidation=age,
        releve=[LigneRelevee(annee=a, affiliation=s, revenu=r) for a, s, r in lignes])
    return {p.regime: p for p in simulateur.scenario_actuel.calculer(carriere).pensions_par_regime}


# -- les fiches ----------------------------------------------------------------

def test_le_seuil_du_regime_general_suit_le_bareme_de_la_cnav(simulateur):
    """175 F au 1er juillet 1974, revalorisés comme les pensions : 156,09 € jusqu'en
    septembre 2015, 156,24 € depuis octobre ; aucun versement avant 1974, et,
    depuis 2016, seulement à qui a pris une retraite avant."""
    premiere = _regle(simulateur, FICHE_DU_VERSEMENT_FORFAITAIRE, "1974-07-01")
    assert (premiere["multiple"], premiere["regimes"]) == (15, ["regime_general"])
    assert _seuil_a_la_date(premiere["seuils"], "1974-07-01") == pytest.approx(
        CENT_SOIXANTE_QUINZE_FRANCS, abs=5e-5)
    avant_2016 = _regle(simulateur, FICHE_DU_VERSEMENT_FORFAITAIRE, "2015-09-01")
    assert _seuil_a_la_date(avant_2016["seuils"], "2015-09-01") == 156.09
    assert _seuil_a_la_date(avant_2016["seuils"], "2015-10-01") == 156.24
    assert "premiere_retraite_avant" not in avant_2016
    depuis = _regle(simulateur, FICHE_DU_VERSEMENT_FORFAITAIRE, "2026-03-01")
    assert depuis["premiere_retraite_avant"] == "2016-01-01"
    assert _seuil_a_la_date(depuis["seuils"], "2026-03-01") == 183.01
    assert not _regle(simulateur, FICHE_DU_VERSEMENT_FORFAITAIRE, "1974-06-01")["existe"]


def test_les_coefficients_de_l_agirc_arrco_sont_ceux_de_l_age_revolu(simulateur):
    """La valeur viagère : avant 2019, la table que reproduit la fiche RET-B100
    (17,0 à 65 ans), en points ; depuis, en euros, celle de chaque année — 29,6 à
    60 ans en 2020, 31,2 en 2023, 31,6 en 2026 ; au-delà de la table, son bout."""
    avant = _regle(simulateur, FICHE_DU_VERSEMENT_AGIRC_ARRCO, "2010-06-01")
    assert avant["mesure"] == "points"
    assert [(a["seuil_points"], a["seuil_compris"]) for a in avant["allocations"]] == [
        (100, True), (500, False)]
    assert coefficient_du_versement(avant, 65.75) == (17.0, 65)
    assert coefficient_du_versement(_regle(
        simulateur, FICHE_DU_VERSEMENT_AGIRC_ARRCO, "2020-06-01"), 60.0)[0] == 29.6
    assert coefficient_du_versement(_regle(
        simulateur, FICHE_DU_VERSEMENT_AGIRC_ARRCO, "2023-06-01"), 60.0)[0] == 31.2
    depuis = _regle(simulateur, FICHE_DU_VERSEMENT_AGIRC_ARRCO, "2026-03-01")
    assert (depuis["mesure"], depuis["allocations"][0]["point"]) == ("montant", "agirc_arrco")
    assert [coefficient_du_versement(depuis, age)[0] for age in (60.0, 65.0, 104.0)] == [
        31.6, 26.4, 2.7]
    assert not _regle(simulateur, FICHE_DU_VERSEMENT_AGIRC_ARRCO, "2003-12-01")["existe"]


def test_le_seuil_de_l_ircantec_a_change_deux_fois(simulateur):
    """Arrêté du 30 décembre 1970, article 25 : moins de 500 points jusqu'en 1975,
    moins de 100 jusqu'en septembre 2008, moins de 300 depuis."""
    assert [_regle(simulateur, FICHE_DU_VERSEMENT_IRCANTEC, date)["seuil_points"]
            for date in ("1975-06-01", "1990-06-01", "2008-10-01")] == [500, 100, 300]


# -- les carrières --------------------------------------------------------------

def test_la_petite_pension_du_regime_general_est_versee_en_une_fois(simulateur):
    """Deux trimestres en 1970 : 93,18 € par an au minimum contributif, sous les
    156,09 € de 2015 ; quinze annuités en une fois. Le montant annuel reste celui
    de la pension remplacée."""
    pensions = _pensions(simulateur, 1950, 65, [(1970, "salarie_prive_non_cadre", 150.0)])
    generale = pensions["regime_general"]
    assert generale.montant < 156.09
    assert generale.capital == pytest.approx(15 * generale.montant)
    assert "versement forfaitaire unique" in generale.detail


def test_depuis_2016_seule_la_premiere_retraite_d_avant_garde_le_versement(simulateur):
    """Une pension de dix euros prise en 2018 est servie ; celle de 2017 d'une
    fonctionnaire partie en 2012 est remplacée, sur son montant de 2017."""
    seule = _pensions(simulateur, 1953, 65, [(1973, "salarie_prive_non_cadre", 300.0)])
    assert seule["regime_general"].montant < 157.48
    assert seule["regime_general"].capital is None
    lignes = [(1975, "salarie_prive_non_cadre", 300.0)] + [
        (1976 + i, "fonctionnaire_etat_actif", 20000.0) for i in range(36)]
    pensions = _pensions(simulateur, 1955, 57, lignes)
    generale = pensions["regime_general"]
    assert (pensions["fonction_publique_etat"].date_effet, generale.date_effet) == (
        "2012-02-01", "2017-02-01")
    assert generale.capital == pytest.approx(15 * generale.montant_a_l_effet)


def test_l_arrco_d_avant_2019_compte_ses_points_minores_ou_non(simulateur):
    """En 2015, 27,95 points de l'Arrco : un capital, la pension annuelle par 17,0
    à 65 ans ; en 2018, 7,51 points minorés de 5 % : un capital encore."""
    arrco = _pensions(simulateur, 1950, 65, [(1970, "salarie_prive_non_cadre", 800.0)])["arrco"]
    assert arrco.capital == pytest.approx(17.0 * arrco.montant)
    minoree = _pensions(simulateur, 1953, 65, [(1973, "salarie_prive_non_cadre", 300.0)])["arrco"]
    assert "coefficient d'anticipation" in minoree.detail
    assert minoree.capital == pytest.approx(17.0 * minoree.montant)


def test_l_agirc_arrco_compare_l_allocation_a_cent_points(simulateur):
    """En 2022, 30,72 € d'allocation, sous les 128,41 € de cent points à 1,2841 € :
    un capital à 26,1 fois, le coefficient de 64 ans de la table de 2020 ; deux ans
    de salaires plus hauts la portent au-dessus, et elle est servie."""
    petite = _pensions(simulateur, 1958, 64, [(1978, "salarie_prive_non_cadre", 2000.0)])
    assert petite["arrco"].montant <= 128.41
    assert petite["arrco"].capital == pytest.approx(26.1 * petite["arrco"].montant)
    grande = _pensions(simulateur, 1958, 64, [(1978, "salarie_prive_non_cadre", 6000.0),
                                              (1979, "salarie_prive_non_cadre", 6000.0)])
    assert grande["arrco"].montant > 128.41
    assert grande["arrco"].capital is None


def test_l_ircantec_verse_les_points_au_salaire_de_reference_d_avant(simulateur):
    """En 2022, 116,41 points, moins de 300 : les points par 5,028 €, le salaire de
    référence de 2021."""
    ircantec = _pensions(simulateur, 1958, 64, [(1978, "contractuel_public", 3000.0)])["ircantec"]
    assert ircantec.capital == pytest.approx(116.41 * 5.028, rel=1e-4)
    assert "salaire de référence de 2021" in ircantec.detail


def test_la_retraite_progressive_n_est_jamais_versee_en_capital(simulateur):
    """L'allocation de l'Agirc-Arrco est servie « dans tous les cas » à la
    retraite progressive (circulaire n° 2020-02-DRJ) ; le modèle ne remplace
    aucune pension provisoire."""
    carriere = simulateur.carriere_releve(
        annee_naissance=1958, sexe="F", age_liquidation=64,
        releve=[LigneRelevee(annee=1978, affiliation="salarie_prive_non_cadre", revenu=2000.0)])
    pensions = [PensionRegime("arrco", 30.0, "points", "", Fiabilite.HAUTE)]
    moteur = simulateur.scenario_actuel
    assert verser_en_capital(moteur, carriere, pensions, [], {"arrco": 27.0},
                             nature="provisoire") is None
    assert pensions[0].capital is None
    assert verser_en_capital(moteur, carriere, pensions, [], {"arrco": 27.0}) is not None
    assert pensions[0].capital == pytest.approx(30.0 * 26.1)


@pytest.mark.parametrize("ligne, regime", [
    ("1978:salarie_prive_non_cadre:2000", "arrco"),
    ("1978:contractuel_public:3000", "ircantec")])
def test_le_capital_verse_a_l_assure_ne_laisse_pas_de_reversion(ligne, regime):
    """« Le versement unique au profit des bénéficiaires de droits directs supprime
    tous droits à réversion » (accord du 17 novembre 2017, article 107) ; à
    l'Ircantec, il « supprime tout droit pour le conjoint » (article 25)."""
    sortie = Contexte().simuler(Saisie.depuis_requete({
        **REQUETE, "naissance": "1958", "liquidation": "64", "releve": ligne,
        "conjoint": "1960", "deces": "2023-05"})).dictionnaire()
    directe, = [p for p in sortie["scenarios"]["actuel"]["par_regime"]
                if p["regime"] == regime]
    assert "versée en capital" in directe["detail"]
    assert regime not in {r["regime"] for r in sortie["reversion"]["regimes"]}
    assert "regime_general" in {r["regime"] for r in sortie["reversion"]["regimes"]}


# -- les deux moteurs -----------------------------------------------------------

REQUETE = {
    "age_reference": "fixe_apres_bascule", "bascule": "2026",
    "conversion_acquis": "reference", "debut": "20", "emploi": "cor_2026",
    "enfants": "0", "euros": "2026", "indexation": "triple_lock_inverse",
    "interruptions": "", "liquidation": "62", "naissance": "1953", "primes": "0",
    "profil": "plat", "projection": "cor_reference", "salaire": "0.45", "sexe": "F",
    "statut": "salarie_prive_non_cadre", "stock": "prix", "table": "unisexe",
}
#: Le versement forfaitaire de 2015, avec ou sans enfants ; la pension de 2018,
#: servie ; celle de 2017 d'une fonctionnaire partie en 2012 ; l'Agirc-Arrco et
#: l'Ircantec de 2022.
CAS = [
    {"naissance": "1950", "liquidation": "65", "releve": "1970:salarie_prive_non_cadre:150"},
    {"naissance": "1950", "liquidation": "65", "enfants": "3",
     "releve": "1970:salarie_prive_non_cadre:150"},
    {"naissance": "1953", "liquidation": "65", "releve": "1973:salarie_prive_non_cadre:300"},
    {"naissance": "1955", "liquidation": "57", "releve": ",".join(
        ["1975:salarie_prive_non_cadre:300"]
        + [f"{1976 + i}:fonctionnaire_etat_actif:20000" for i in range(36)])},
    {"naissance": "1958", "liquidation": "64", "releve": "1978:salarie_prive_non_cadre:2000"},
    {"naissance": "1958", "liquidation": "64", "releve": "1978:contractuel_public:3000",
     "conjoint": "1960", "deces": "2023-05"},
]


def test_les_deux_moteurs_versent_les_memes_capitaux():
    """Le journal de l'échéancier — les composantes et leur formule, la réversion —
    est le même en Python et en JavaScript."""
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
    formules = json.dumps(attendus, ensure_ascii=False)
    for marque in ("versement forfaitaire unique", "versée en capital", "salaire de référence"):
        assert marque in formules, marque
    ecarts: list[str] = []
    for rang, (obtenu, attendu) in enumerate(zip(obtenus, attendus)):
        _ecarts(obtenu, attendu, f"requête {rang}", ecarts)
    assert not ecarts, f"{len(ecarts)} écarts :\n" + "\n".join(ecarts[:20])
