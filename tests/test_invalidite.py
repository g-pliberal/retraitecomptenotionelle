"""L'invalidité et l'inaptitude : le quatrième domaine (docs/architecture.md, § 11).

Trois fiches le portent, ouvertes le 30 septembre 2026 :
``pension_d_invalidite_substituee`` — la pension d'invalidité remplacée à l'âge
légal par la pension de vieillesse de l'inapte —, ``inaptitude_au_travail`` et
``retraite_pour_invalidite_fonction_publique``. Ce fichier tient d'abord les
faits : ce que la saisie lit, ce que la chronologie en garde, ce que la
carrière en présume, et ce qui se refuse.
"""

from __future__ import annotations

import pytest

from retraite_notionnelle import chronologie as chrono
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere, Metier
from retraite_notionnelle.saisie import ErreurSaisie, Saisie
from retraite_notionnelle.simulateur import Simulateur


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _saisie(**champs) -> Saisie:
    return Saisie.depuis_requete({"naissance": "1965-06-15", "debut": "1986-09",
                                  "liquidation": "2029-01", **champs})


# -- la saisie -------------------------------------------------------------------

def test_la_saisie_lit_l_invalidite_et_la_rend_a_l_adresse():
    """Les trois faits se disent par l'adresse, en dates comme un début
    d'activité, et l'adresse les rend tels qu'elle les a reçus."""
    saisie = _saisie(statut="fonctionnaire_territorial_hospitalier",
                     invalidite="2019-03", inaptitude="oui",
                     radiation_invalidite="2018-11", invalidite_imputable="oui",
                     taux_invalidite="65")
    assert saisie.date_de(saisie.invalidite) == DateMois(2019, 3)
    assert saisie.inaptitude and saisie.invalidite_imputable
    assert saisie.date_de(saisie.radiation_invalidite) == DateMois(2018, 11)
    assert saisie.invalidite_declaree() == {
        "pension": saisie.invalidite, "inaptitude": True,
        "radiation": {"age": saisie.radiation_invalidite, "imputable": True, "taux": 65},
        "handicap": None}
    relue = Saisie.depuis_requete(dict(
        pair.split("=", 1) for pair in saisie.requete().split("&")))
    assert relue.invalidite_declaree() == saisie.invalidite_declaree()
    assert _saisie().invalidite_declaree() is None


@pytest.mark.parametrize("champs, refus", [
    ({"taux_invalidite": "50"},
     "« taux_invalidite » ne sert qu'à la retraite pour invalidité d'un fonctionnaire"),
    ({"invalidite_imputable": "oui"},
     "« invalidite_imputable » ne sert qu'à la retraite pour invalidité"),
    ({"inaptitude": "peut-être"}, "n'est pas une réponse possible"),
    ({"radiation_invalidite": "2010-01", "taux_invalidite": "0"},
     "Taux d'invalidité : en pour cent, entre 1 et 100."),
    ({"invalidite": "1986-09"}, "elle suit le début de la carrière"),
    ({"invalidite": "2029-01"}, "elle précède le départ à la retraite"),
    ({"radiation_invalidite": "2029-02"}, "elle ne suit pas le départ"),
    ({"handicap": "1965-06"}, "Incapacité d'au moins 50 % en juin 1965 : elle suit la naissance"),
    ({"handicap": "2029-02"}, "Incapacité d'au moins 50 % en février 2029 : elle ne suit pas"),
])
def test_la_saisie_refuse_ce_qui_ne_tient_pas(champs, refus):
    with pytest.raises(ErreurSaisie, match=refus):
        _saisie(**champs)


def test_la_radiation_peut_tomber_au_depart():
    """Le fonctionnaire dont la radiation est le départ : la même date."""
    saisie = _saisie(statut="fonctionnaire_etat", radiation_invalidite="2029-01")
    assert saisie.date_de(saisie.radiation_invalidite) == DateMois(2029, 1)


# -- la chronologie et la carrière -----------------------------------------------

def _carriere(simulateur, metiers, invalidite=None, interruptions=None,
              liquidation=62.0) -> Carriere:
    return Carriere.depuis_parcours(
        annee_naissance=1965, sexe="H", mois_naissance=6, metiers=metiers,
        age_liquidation=liquidation, macro=simulateur.macro,
        interruptions=interruptions, invalidite=invalidite)


def test_la_chronologie_porte_deux_decisions_medicales_et_une_radiation(simulateur):
    carriere = _carriere(
        simulateur,
        [Metier("fonctionnaire_etat", 22.0), Metier("salarie_prive_non_cadre", 50.0)],
        invalidite={"pension": 55.0, "inaptitude": True,
                    "radiation": {"age": 50.0, "imputable": True, "taux": 70}})
    pension = chrono.decision_medicale(carriere.chronologie, carriere.personne,
                                       "pension_d_invalidite")
    assert pension["debut"] == "2020-06-01" and pension["origine"] == "declare"
    inaptitude = chrono.decision_medicale(carriere.chronologie, carriere.personne,
                                          "inaptitude")
    # L'inaptitude est constatée au départ : juillet 2027, le mois qui suit
    # les soixante-deux ans.
    assert carriere.date_liquidation == DateMois(2027, 7)
    assert inaptitude["debut"] == "2027-07-01"
    radiation = chrono.radiation_pour_invalidite(carriere.chronologie, carriere.personne)
    assert radiation["debut"] == "2015-06-01"
    assert radiation["attributs"] == {"motif": "invalidite", "age": 50.0,
                                      "imputable": True, "taux": 70}
    assert carriere.pension_d_invalidite.debut == DateMois(2020, 6)
    assert carriere.pension_d_invalidite.presomption is None
    assert carriere.pension_d_invalidite.affiliations == ("salarie_prive_non_cadre",)
    assert carriere.inaptitude
    assert carriere.radiation_pour_invalidite.date == DateMois(2015, 6)
    # Juin 2015 : l'année du changement d'emploi va au salarié, qui en
    # occupe sept mois ; l'emploi que la radiation clôt porte 2014.
    assert carriere.radiation_pour_invalidite.affiliations == (
        "salarie_prive_non_cadre", "fonctionnaire_etat")
    assert carriere.radiation_pour_invalidite.taux == 70


def test_une_carriere_qui_finit_en_invalidite_presume_la_pension(simulateur):
    """Présomption ``pension_d_invalidite_de_la_periode`` : la pension depuis
    le 1er janvier de la première année de l'invalidité finale."""
    carriere = _carriere(
        simulateur, [Metier("salarie_prive_non_cadre", 21.0)],
        interruptions={annee: "invalidite" for annee in range(2019, 2028)})
    assert carriere.pension_d_invalidite.debut == DateMois(2019, 1)
    assert carriere.pension_d_invalidite.presomption == "pension_d_invalidite_de_la_periode"
    # Le régime qui la sert : celui de l'emploi qu'elle a interrompu.
    assert carriere.pension_d_invalidite.affiliations == ("salarie_prive_non_cadre",)
    assert not carriere.inaptitude
    assert carriere.radiation_pour_invalidite is None


def test_une_invalidite_suivie_d_une_reprise_a_pris_fin(simulateur):
    """Une période d'invalidité que l'activité suit : la pension a été
    supprimée, et rien n'est présumé."""
    carriere = _carriere(
        simulateur, [Metier("salarie_prive_non_cadre", 21.0)],
        interruptions={annee: "invalidite" for annee in range(2005, 2008)})
    assert carriere.pension_d_invalidite is None


# -- ce que le contexte refuse ---------------------------------------------------

def test_la_radiation_clot_un_emploi_de_fonctionnaire_civil():
    from retraite_notionnelle.contexte import Contexte

    contexte = Contexte()
    with pytest.raises(ErreurSaisie, match="elle clôt un emploi de fonctionnaire civil"):
        contexte.simuler(_saisie(radiation_invalidite="2015-06"))
    with pytest.raises(ErreurSaisie, match="la carrière reste dans la fonction publique en 2016"):
        contexte.simuler(_saisie(statut="fonctionnaire_etat",
                                 radiation_invalidite="2015-06"))
    # Radiée en janvier, l'emploi clos ne touche pas son année.
    with pytest.raises(ErreurSaisie, match="la carrière reste dans la fonction publique en 2015"):
        contexte.simuler(_saisie(statut="fonctionnaire_etat",
                                 radiation_invalidite="2015-01"))
    # Radiée en juin 2015, sans activité ensuite : la carrière tient.
    contexte.simuler(_saisie(statut="fonctionnaire_etat", radiation_invalidite="2015-06",
                             metier2_debut="2015-06", metier2_statut="sans_activite"))


# -- le portage ------------------------------------------------------------------

#: Des saisies du formulaire qui portent les trois faits, déclarés ou présumés.
REQUETES = [
    {"naissance": "1965-06-15", "debut": "1986-09", "liquidation": "2029-01",
     "invalidite": "2019-03", "inaptitude": "oui"},
    {"naissance": "1965-06-15", "debut": "1986-09", "liquidation": "2029-01",
     "interruptions": "2019:2028:invalidite"},
    {"naissance": "1975", "statut": "fonctionnaire_etat", "radiation_invalidite": "2010-06",
     "invalidite_imputable": "oui", "taux_invalidite": "60",
     "metier2_debut": "2010-06", "metier2_statut": "salarie_prive_non_cadre"},
    {"naissance": "1975", "statut": "fonctionnaire_territorial_hospitalier",
     "radiation_invalidite": "2012-01", "metier2_debut": "2012-01",
     "metier2_statut": "sans_activite"},
    {"naissance": "1970-06-01", "debut": "2004-01", "liquidation": "2027-06",
     "handicap": "1990-03"},
]

#: Ce que le portage lit de la carrière que la saisie bâtit.
LECTURE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { Saisie } from "./moteur/js/saisie.js";
import { Simulateur } from "./moteur/js/simulateur.js";

const contexte = new Contexte(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));
let vue = null;
const simuler = Simulateur.prototype.simuler;
Simulateur.prototype.simuler = function (carriere, ...reste) {
  vue ??= carriere;
  return simuler.call(this, carriere, ...reste);
};
const mois = (date) => `${date.annee}-${String(date.mois).padStart(2, "0")}`;
const sortie = JSON.parse(readFileSync(0, "utf8")).map((requete) => {
  vue = null;
  contexte.simuler(Saisie.depuisRequete(requete, false, contexte.paquet.presomptions));
  const pension = vue.pensionDInvalidite;
  const radiation = vue.radiationPourInvalidite;
  return {
    pension: pension === null ? null : {
      debut: mois(pension.debut), presomption: pension.presomption,
      affiliations: [...pension.affiliations] },
    inaptitude: vue.inaptitude,
    radiation: radiation === null ? null : {
      date: mois(radiation.date), affiliations: [...radiation.affiliations],
      imputable: radiation.imputable, taux: radiation.taux },
    incapacite: vue.incapacitePermanente === null ? null : {
      debut: mois(vue.incapacitePermanente.debut), taux: vue.incapacitePermanente.taux },
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def _lu_par_python(monkeypatch, requete: dict) -> dict:
    from retraite_notionnelle.contexte import Contexte

    vues = []
    simuler = Simulateur.simuler

    def espion(self, carriere, *reste, **options):
        vues.append(carriere)
        return simuler(self, carriere, *reste, **options)

    monkeypatch.setattr(Simulateur, "simuler", espion)
    Contexte().simuler(Saisie.depuis_requete(requete))
    vue = vues[0]
    pension, radiation = vue.pension_d_invalidite, vue.radiation_pour_invalidite
    mois = "{0.annee}-{0.mois:02d}".format
    return {
        "pension": None if pension is None else {
            "debut": mois(pension.debut), "presomption": pension.presomption,
            "affiliations": list(pension.affiliations)},
        "inaptitude": vue.inaptitude,
        "radiation": None if radiation is None else {
            "date": mois(radiation.date), "affiliations": list(radiation.affiliations),
            "imputable": radiation.imputable, "taux": radiation.taux},
        "incapacite": None if vue.incapacite_permanente is None else {
            "debut": mois(vue.incapacite_permanente.debut),
            "taux": vue.incapacite_permanente.taux},
    }


def test_le_portage_lit_les_memes_faits(monkeypatch):
    """La carrière des deux moteurs lit les mêmes faits de la même saisie :
    la pension d'invalidité, déclarée ou présumée, l'inaptitude, la
    radiation et les affiliations qui les entourent."""
    import json
    import shutil
    import subprocess
    from pathlib import Path

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", LECTURE_JS], cwd=racine,
        input=json.dumps(REQUETES), capture_output=True, text=True, encoding="utf-8",
        check=False)
    assert execution.returncode == 0, execution.stderr
    attendus = [_lu_par_python(monkeypatch, requete) for requete in REQUETES]
    assert json.loads(execution.stdout) == attendus
    # Chaque fait y est au moins une fois.
    assert attendus[0]["pension"]["presomption"] is None and attendus[0]["inaptitude"]
    assert attendus[1]["pension"]["presomption"] == "pension_d_invalidite_de_la_periode"
    assert attendus[2]["radiation"]["taux"] == 60
    assert attendus[3]["radiation"]["affiliations"] == ["fonctionnaire_territorial_hospitalier"]
    assert attendus[4]["incapacite"] == {"debut": "1990-03", "taux": 50}


# -- le moteur : le taux plein de l'inapte, la substitution ----------------------

@pytest.fixture(scope="module")
def contexte():
    from retraite_notionnelle.contexte import Contexte

    return Contexte()


def _actuel(contexte, **champs):
    """Le scénario 1 d'une saisie : ce que la page lit du système actuel."""
    return contexte.simuler(Saisie.depuis_requete(champs)).actuel


def _pension(actuel, regime):
    return next(p for p in actuel.pensions_par_regime if p.regime == regime)


def test_l_inapte_part_a_soixante_deux_ans_au_taux_plein(contexte):
    """Né en 1965, l'âge légal de sa génération ne lui ouvre pas sa pension
    à soixante-deux ans ; reconnu inapte, il part à cet âge au taux plein,
    huit trimestres manquants et sans coefficient d'anticipation à
    l'Agirc-Arrco (L. 351-1-5, L. 351-8, 2° ; accord de 2017, article 84, 3)."""
    champs = {"naissance": "1965-06-15", "debut": "1986-09", "liquidation": "2027-07"}
    inapte = _actuel(contexte, **champs, inaptitude="oui")
    assert inapte.liquidation_ouverte and inapte.motif_ouverture == "inaptitude"
    assert inapte.age_ouverture_opposable == 62.0
    assert inapte.trimestres_valides < inapte.trimestres_requis
    assert "taux 50.000%" in _pension(inapte, "regime_general").detail
    assert "coefficient" not in _pension(inapte, "arrco").detail
    autre = _actuel(contexte, **champs)
    assert not autre.liquidation_ouverte
    assert "taux 45.000%" in _pension(autre, "regime_general").detail
    assert "coefficient d'anticipation" in _pension(autre, "arrco").detail


def test_l_ircantec_sert_l_inapte_sans_coefficient(contexte):
    """« Toutefois, ce coefficient de réduction n'est pas applicable : […]
    aux agents atteints d'une inaptitude au travail » (arrêté du 30 décembre
    1970, article 16)."""
    champs = {"naissance": "1964-02-10", "statut": "contractuel_public",
              "debut": "1992-09", "liquidation": "2026-03"}
    assert "coefficient" not in _pension(
        _actuel(contexte, **champs, inaptitude="oui"), "ircantec").detail
    assert "coefficient d'anticipation 0.7800" in _pension(
        _actuel(contexte, **champs), "ircantec").detail


def test_l_inapte_de_2010_a_le_taux_plein_a_soixante_ans(contexte):
    champs = {"naissance": "1950-03-15", "debut": "1975-09", "liquidation": "2010-04"}
    assert "taux 50.000%" in _pension(
        _actuel(contexte, **champs, inaptitude="oui"), "regime_general").detail
    assert "taux 33.750%" in _pension(_actuel(contexte, **champs), "regime_general").detail


def test_l_ex_invalide_est_substitue_a_soixante_deux_ans(contexte):
    """La pension de vieillesse remplace d'office la pension d'invalidité au
    premier jour du mois qui suit soixante-deux ans, avant le départ déclaré
    à soixante-quatre : le régime général et ses complémentaires y
    liquident, au taux plein (L. 341-15, R. 341-22)."""
    actuel = _actuel(contexte, naissance="1965-06-15", debut="1986-09",
                     liquidation="2029-07", interruptions="2019:2029:invalidite")
    [depart] = actuel.departs
    assert (depart.date_effet, depart.motif) == ("2027-07-01", "invalidite")
    assert set(depart.regimes) == {"regime_general", "agirc_arrco", "arrco",
                                   "arrco_tranche_2"}
    assert actuel.motif_ouverture == "inaptitude"
    assert "taux 50.000%" in _pension(actuel, "regime_general").detail


def test_l_invalide_qui_travaille_part_a_sa_demande(contexte):
    """L'invalide qui travaille à l'âge légal garde sa pension d'invalidité
    jusqu'à sa demande (L. 341-16) : sa pension de vieillesse commence à son
    départ, un seul, au taux plein de l'inapte."""
    actuel = _actuel(contexte, naissance="1965-06-15", debut="1990-09",
                     liquidation="2029-07", invalidite="2015-03")
    assert not actuel.departs
    assert "taux 50.000%" in _pension(actuel, "regime_general").detail


def test_le_demandeur_d_emploi_garde_six_mois_sa_pension_d_invalidite(contexte):
    """Indemnisé à l'âge légal, il la garde six mois de plus (D. 341-1,
    depuis le 1er septembre 2017) : né en mars 1960, soixante-deux ans en
    avril 2022, sa pension de vieillesse commence en octobre."""
    actuel = _actuel(contexte, naissance="1960-03-15", debut="1980-09",
                     liquidation="2024-07", interruptions="2012:2024:chomage_indemnise",
                     invalidite="2014-01")
    [depart] = actuel.departs
    assert (depart.date_effet, depart.motif) == ("2022-10-01", "invalidite")


def test_une_invalidite_nee_apres_l_age_ne_se_substitue_pas(contexte):
    """Une pension d'invalidité qui commencerait après l'âge de la
    substitution n'en a pas : la pension de vieillesse commence au départ."""
    actuel = _actuel(contexte, naissance="1965-06-15", debut="1986-09",
                     liquidation="2029-07", invalidite="2027-12")
    assert not actuel.departs


def test_avant_1983_l_ex_invalide_a_le_taux_de_soixante_cinq_ans(contexte):
    """En 1980, la pension de vieillesse qui remplace la pension d'invalidité
    à soixante ans est calculée au taux de soixante-cinq ans : 50 %, et non
    les 25 % de soixante ans (loi Boulin)."""
    actuel = _actuel(contexte, naissance="1920-03-15", debut="1936-09",
                     liquidation="1982-07", interruptions="1975:1982:invalidite")
    assert actuel.departs[0].date_effet == "1980-04-01"
    assert "taux 50.000%" in _pension(actuel, "regime_general").detail


def test_l_inapte_a_l_aspa_des_son_age(contexte):
    """« L'âge mentionné à l'article L. 815-1 est fixé à soixante-cinq ans. Il
    est abaissé à l'âge prévu à l'article L. 161-17-2 pour les personnes
    mentionnées aux 2° à 5° de l'article L. 351-8 » (R. 815-1, de 2011 à
    2023) : né en 1960, l'inapte parti à soixante-deux ans en 2022 a l'ASPA,
    que l'autre n'aura qu'à soixante-cinq."""
    champs = {"naissance": "1960-03-15", "debut": "1999-09", "liquidation": "2022-04",
              "salaire": "0.5"}
    inapte = _actuel(contexte, **champs, inaptitude="oui")
    assert any(a.code == "minimum_vieillesse" for a in inapte.avantages_appliques)
    autre = _actuel(contexte, **champs)
    assert not any(a.code == "minimum_vieillesse" for a in autre.avantages_appliques)


def test_l_age_de_l_aspa_suit_la_version(simulateur):
    """Soixante ans avant 2011, l'âge légal de 2011 à 2023, soixante-deux ans
    depuis ; soixante-cinq ans pour qui n'est pas inapte."""
    from retraite_notionnelle.droit.invalidite import age_de_l_aspa

    moteur = simulateur.scenario_actuel
    for naissance, liquidation, attendu in ((1945, 60.0, 60.0), (1952, 62.0, 60.75),
                                            (1965, 62.0, 62.0)):
        carriere = Carriere.depuis_parcours(
            annee_naissance=naissance, sexe="H", mois_naissance=6,
            metiers=[Metier("salarie_prive_non_cadre", 21.0)],
            age_liquidation=liquidation, macro=simulateur.macro,
            invalidite={"pension": None, "inaptitude": True, "radiation": None})
        assert age_de_l_aspa(moteur, carriere) == attendu, naissance
        valide = Carriere.depuis_parcours(
            annee_naissance=naissance, sexe="H", mois_naissance=6,
            metiers=[Metier("salarie_prive_non_cadre", 21.0)],
            age_liquidation=liquidation, macro=simulateur.macro)
        assert age_de_l_aspa(moteur, valide) == 65.0


# -- la retraite pour invalidité des fonctionnaires ------------------------------

def test_le_fonctionnaire_radie_pour_invalidite_liquide_a_sa_radiation(contexte):
    """À trente-quatre ans, sept ans de services, invalide à 80 % : la pension
    de la CNRACL à la radiation, sans condition de durée ni décote, portée à
    la moitié du traitement (L. 4, L. 24, L. 30 ; décret n° 2003-1306,
    articles 7, 30, 34 et 39)."""
    actuel = _actuel(contexte, naissance="1985", statut="fonctionnaire_territorial_hospitalier",
                     debut="2012-09", radiation_invalidite="2019-09", taux_invalidite="80",
                     metier2_debut="2019-09", metier2_statut="sans_activite")
    assert actuel.motif_ouverture == "invalidite"
    [depart] = actuel.departs
    assert (depart.date_effet, depart.motif, depart.regimes) == (
        "2019-09-01", "radiation", ("cnracl",))
    detail = _pension(actuel, "cnracl").detail
    assert "taux 75.000%" in detail and "la moitié du traitement (L. 30)" in detail


def test_la_rente_viagere_d_invalidite_et_le_plafond_du_traitement(contexte):
    """Invalide à 70 % du fait du service : la rente viagère s'ajoute à la
    pension portée à la moitié du traitement, et le total, qui le dépasse,
    est ramené au traitement (L. 28, L. 30 ter)."""
    actuel = _actuel(contexte, naissance="1975", statut="fonctionnaire_etat",
                     radiation_invalidite="2020-06", invalidite_imputable="oui",
                     taux_invalidite="70", metier2_debut="2020-06",
                     metier2_statut="sans_activite")
    pension = _pension(actuel, "fonction_publique_etat")
    assert "rente viagère d'invalidité" in pension.detail
    assert "réduite au traitement (L. 30 ter)" in pension.detail
    traitement = float(pension.detail.split("SR ")[1].split(" €")[0].replace(",", ""))
    assert pension.montant_a_l_effet == pytest.approx(traitement)


def test_la_rente_compte_pour_le_tiers_au_dela_du_seuil():
    from retraite_notionnelle.droit.invalidite import rente_viagere_d_invalidite

    assert rente_viagere_d_invalidite(30_000.0, 0.5, 40_000.0) == pytest.approx(15_000.0)
    assert rente_viagere_d_invalidite(70_000.0, 0.5, 40_000.0) == pytest.approx(
        0.5 * (40_000.0 + 30_000.0 / 3.0))
    # Au-delà de dix fois le seuil, rien ne compte plus.
    assert rente_viagere_d_invalidite(900_000.0, 1.0, 40_000.0) == pytest.approx(
        40_000.0 + 360_000.0 / 3.0)


def test_le_minimum_garanti_de_l_invalidite_en_quinziemes(contexte):
    """Dix ans de services, radiée pour invalidité : le minimum garanti est
    dû sans condition de taux plein, en quinzièmes (L. 17, c ; article 22 du
    décret de la CNRACL) ; la même, partie sans invalidité, est décotée et ne
    l'a pas."""
    champs = {"naissance": "1980", "statut": "fonctionnaire_territorial_hospitalier",
              "debut": "2005-09", "salaire": "0.5", "metier2_debut": "2015-09",
              "metier2_statut": "sans_activite"}
    radiee = _pension(_actuel(contexte, **champs, radiation_invalidite="2015-09",
                              taux_invalidite="30"), "cnracl")
    assert "porté au minimum garanti" in radiee.detail
    partie = _pension(_actuel(contexte, **champs), "cnracl")
    assert "minimum garanti" not in partie.detail and "taux 63.750%" in partie.detail


def test_le_fonctionnaire_radie_puis_salarie_a_deux_departs(contexte):
    """Sa pension de fonctionnaire dès la radiation ; le régime général et
    l'Agirc-Arrco à son départ, avec le RAFP, qui n'ouvre qu'à l'âge légal
    (décret n° 2004-569, article 6)."""
    actuel = _actuel(contexte, naissance="1975", statut="fonctionnaire_etat", primes="0.2",
                     radiation_invalidite="2020-06", metier2_debut="2020-06",
                     metier2_statut="salarie_prive_non_cadre")
    premier, second = actuel.departs
    assert (premier.date_effet, premier.motif, premier.regimes) == (
        "2020-06-01", "radiation", ("fonction_publique_etat",))
    assert {"regime_general", "rafp"} <= set(second.regimes)


# -- le départ anticipé des assurés handicapés -------------------------------------

def test_la_saisie_lit_l_incapacite_meme_avant_la_carriere():
    """L'incapacité se date comme un début d'activité, et peut précéder la
    carrière — un handicap de l'enfance — ; l'adresse la rend telle quelle."""
    saisie = _saisie(handicap="1980-03")
    assert saisie.date_de(saisie.handicap) == DateMois(1980, 3)
    assert saisie.invalidite_declaree() == {
        "pension": None, "inaptitude": False, "radiation": None,
        "handicap": saisie.handicap}
    relue = Saisie.depuis_requete(dict(
        pair.split("=", 1) for pair in saisie.requete().split("&")))
    assert relue.invalidite_declaree() == saisie.invalidite_declaree()
    au_depart = _saisie(handicap="2029-01")
    assert au_depart.date_de(au_depart.handicap) == DateMois(2029, 1)


#: Un salarié né le 1er juin 1973, handicapé depuis ses vingt et un ans, qui
#: part à cinquante-cinq ans en juin 2028 : entré en avril 2000, il a cotisé
#: 3 + 27 × 4 + 1 = 112 trimestres, la durée requise de sa génération, 172,
#: moins 60 (D. 351-1-5 du 1er septembre 2026).
NE_EN_1973 = {"naissance": "1973-06-01", "debut": "2000-04", "liquidation": "2028-06",
              "handicap": "1995-01"}


def test_le_handicap_ouvre_le_depart_des_cinquante_cinq_ans_au_taux_plein(contexte):
    """La durée cotisée en situation de handicap ouvre le départ à cinquante-
    cinq ans (L. 351-1-3), au taux plein malgré soixante trimestres manquants
    (L. 351-8, 4° bis), la pension majorée du tiers du rapport de la durée
    cotisée en situation de handicap à la durée d'assurance, 112/112/3 = 0,33
    (D. 351-1-5, II), l'Agirc-Arrco sans coefficient (accord du 17 novembre
    2017, article 84, 3). Un trimestre de moins, et rien ne s'ouvre."""
    actuel = _actuel(contexte, **NE_EN_1973)
    assert actuel.liquidation_ouverte and actuel.motif_ouverture == "handicap"
    assert actuel.age_ouverture_opposable == 55.0
    assert (actuel.trimestres_valides, actuel.trimestres_requis) == (112, 172)
    detail = _pension(actuel, "regime_general").detail
    assert "taux 50.000%" in detail and "majoration des assurés handicapés 0.33" in detail
    assert "écrêtée" not in detail
    assert "coefficient" not in _pension(actuel, "arrco").detail
    un_de_moins = _actuel(contexte, **{**NE_EN_1973, "debut": "2000-07"})
    assert un_de_moins.trimestres_valides == 111
    assert un_de_moins.motif_ouverture == "non_ouverte"
    assert "majoration des assurés handicapés" not in _pension(
        un_de_moins, "regime_general").detail
    sans = _actuel(contexte, **{k: v for k, v in NE_EN_1973.items() if k != "handicap"})
    assert sans.motif_ouverture == "non_ouverte"


def test_la_majoration_est_ecretee_a_la_pension_entiere(contexte):
    """Cent soixante et un trimestres, tous cotisés en situation de handicap :
    le coefficient vaut 0,33, mais la pension majorée ne dépasse pas celle
    d'une durée entière (D. 351-1-5, II ; circulaire Cnav n° 2026-18, 3.3.1),
    la moitié du salaire annuel moyen."""
    import re

    actuel = _actuel(contexte, naissance="1973-06-01", debut="1992-01",
                     liquidation="2032-06", handicap="1992-01")
    assert actuel.motif_ouverture == "handicap" and actuel.trimestres_valides == 161
    pension = _pension(actuel, "regime_general")
    assert "majoration des assurés handicapés 0.33 écrêtée à la pension entière" in (
        pension.detail)
    sam = float(re.search(r"SR ([0-9,]+\.\d\d) €", pension.detail).group(1).replace(",", ""))
    assert pension.montant == pytest.approx(0.5 * sam, abs=0.01)


def test_avant_2015_l_incapacite_declaree_n_etablit_pas_les_80_pour_cent(contexte):
    """Jusqu'au 31 décembre 2014, le taux exigé est celui de la carte
    d'invalidité, 80 % (D. 351-1-6) : la saisie, qui dit au moins 50 %, ne
    l'établit pas, et rien ne s'ouvre. Trois ans plus tard, la même carrière
    d'une autre génération part : 167 − 80 = 87 trimestres cotisés et
    167 − 60 = 107 validés suffisent à cinquante-sept ans (version de 2015)."""
    en_2012 = _actuel(contexte, naissance="1955-06-01", debut="1985-01",
                      liquidation="2012-06", handicap="1985-01")
    assert en_2012.motif_ouverture == "non_ouverte"
    en_2015 = _actuel(contexte, naissance="1958-06-01", debut="1988-01",
                      liquidation="2015-06", handicap="1988-01")
    assert en_2015.trimestres_valides == 109
    assert en_2015.motif_ouverture == "handicap" and en_2015.age_ouverture_opposable == 57.0


def test_l_incapacite_donne_le_taux_plein_a_soixante_deux_ans(contexte):
    """Sans la durée du départ anticipé, l'incapacité d'au moins 50 % fait
    partir à soixante-deux ans au taux plein, comme l'inapte (L. 351-1-5,
    L. 351-8, 2°, R. 351-24-3), quand l'âge légal de la génération 1965 ne
    l'ouvre pas encore."""
    champs = {"naissance": "1965-06-15", "debut": "2000-09", "liquidation": "2027-07"}
    actuel = _actuel(contexte, **champs, handicap="2020-01")
    assert actuel.motif_ouverture == "inaptitude" and actuel.age_ouverture_opposable == 62.0
    assert actuel.trimestres_valides < actuel.trimestres_requis
    assert "taux 50.000%" in _pension(actuel, "regime_general").detail
    assert "coefficient" not in _pension(actuel, "arrco").detail
    assert _actuel(contexte, **champs).motif_ouverture == "non_ouverte"


def test_le_depart_des_handicapes_passe_avant_l_inaptitude(contexte):
    """Entre soixante-deux ans et l'âge légal, les deux portes s'ouvrent ; le
    départ des assurés handicapés, « entre cinquante-neuf ans et l'âge prévu à
    l'article L. 161-17-2 » (D. 351-1-5), majore la pension, que l'inaptitude
    ne majore pas : il l'emporte."""
    actuel = _actuel(contexte, naissance="1966-06-01", debut="1995-01",
                     liquidation="2028-06", handicap="1995-01")
    assert actuel.motif_ouverture == "handicap"
    assert "majoration des assurés handicapés" in _pension(actuel, "regime_general").detail


def test_le_fonctionnaire_handicape_n_a_pas_de_decote(contexte):
    """« Le coefficient de minoration n'est pas applicable aux fonctionnaires
    handicapés dont l'incapacité permanente est au moins égale à un taux fixé
    par décret » (L. 14, I ; D. 14 : 50 %), à tout âge : parti à soixante-
    quatre ans, trois ans avant l'âge d'annulation, sans la durée du départ
    anticipé, il garde 75 % quand l'autre perd douze trimestres de décote."""
    champs = {"naissance": "1966-06-01", "statut": "fonctionnaire_etat",
              "debut": "2000-01", "liquidation": "2030-06"}
    handicape = _actuel(contexte, **champs, handicap="2020-01")
    assert handicape.motif_ouverture == "age_legal"
    assert "taux 75.000%" in _pension(handicape, "fonction_publique_etat").detail
    autre = _actuel(contexte, **champs)
    assert "taux 63.750%" in _pension(autre, "fonction_publique_etat").detail


def test_l_ircantec_sert_le_handicape_sans_coefficient(contexte):
    """« b) Les agents et anciens agents handicapés admis à faire liquider
    leur retraite au régime général en application de l'article L. 351-1-3 »
    n'ont pas de coefficient de réduction (arrêté du 30 décembre 1970,
    article 16)."""
    actuel = _actuel(contexte, **NE_EN_1973, statut="contractuel_public")
    assert actuel.motif_ouverture == "handicap"
    assert "coefficient" not in _pension(actuel, "ircantec").detail


def test_l_age_au_plus_tot_compte_le_depart_des_handicapes(simulateur):
    """L'âge que les cas types et « Mon estimation retraite » lisent : celui
    où la durée cotisée en situation de handicap est réunie, cinquante-cinq
    ans pour qui en a 140 à soixante-deux — au taux plein aussi."""
    from retraite_notionnelle.droit import ouvrir

    def carriere(invalidite=None):
        return Carriere.depuis_parcours(
            1973, "H", [Metier("salarie_prive_non_cadre", 26.0 + 10 / 12, 1.0)], 62.0,
            simulateur.macro, mois_naissance=6, jour_naissance=1, invalidite=invalidite)

    actuel = simulateur.scenario_actuel
    handicape = carriere({"pension": None, "inaptitude": False, "radiation": None,
                          "handicap": 21.0 + 7 / 12})
    assert ouvrir.age_ouverture_droit(actuel, handicape) == pytest.approx(55.0)
    assert ouvrir.age_taux_plein_droit(actuel, handicape) == pytest.approx(55.0)
    assert ouvrir.age_ouverture_droit(actuel, carriere()) > 62.0
