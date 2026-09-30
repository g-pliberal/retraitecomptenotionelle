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
        "radiation": {"age": saisie.radiation_invalidite, "imputable": True, "taux": 65}}
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
