"""Les carrières hors de France : le cinquième domaine (docs/architecture.md, § 11).

Quatre fiches le portent, ouvertes le 1er octobre 2026 :
``totalisation_des_periodes_etrangeres``, ``pension_proratisee``,
``minimum_contributif_international`` et ``residence_et_minimum_vieillesse`` ;
le tableau des accords (``data/reference/legislation/accords_internationaux.yaml``)
dit l'accord en vigueur avec chaque État. Ce fichier tient d'abord les faits :
ce que la saisie lit, ce que la chronologie en garde, ce que la carrière en
lit, et ce qui se refuse.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pytest

from retraite_notionnelle import chronologie as chrono
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import (
    Carriere, LigneRelevee, Metier, PensionEtrangere, PeriodeALEtranger,
)
from retraite_notionnelle.donnees.chargement import charger_accords_internationaux
from retraite_notionnelle.saisie import ErreurSaisie, Saisie
from retraite_notionnelle.simulateur import Simulateur

DONNEES = Path(__file__).resolve().parents[1] / "data"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _saisie(**champs) -> Saisie:
    return Saisie.depuis_requete({"naissance": "1965-06-15", "debut": "1986-09",
                                  "liquidation": "2029-01", **champs})


# -- le tableau des accords --------------------------------------------------------

def test_le_tableau_des_accords_dit_un_accord_par_date():
    """Chaque État a son nom et ses accords, qui se suivent bout à bout : un
    seul est en vigueur à une date d'effet, et le dernier l'est encore. Chaque
    accord dit son instrument, et ses valeurs sont celles que l'en-tête du
    tableau définit ; ses dates sont au jour, comme celles des faits."""
    etats = charger_accords_internationaux(DONNEES)
    assert etats["MA"]["nom"] == "Maroc" and "FR" not in etats
    valeurs = {
        "instrument": {"reglements_europeens", "accord_de_commerce_et_de_cooperation",
                       "convention", "organisation_internationale"},
        "calcul": {"comparaison", "calcul_separe", "option", "taux_seul", "non_lu"},
        "prorata": {"limite", "non_lu"},
        "personnes": {"salaries", "salaries_et_non_salaries"},
    }
    for code, etat in etats.items():
        assert code == "OI" or re.fullmatch(r"[A-Z]{2}", code), code
        accords = etat["accords"]
        assert accords and accords[-1].get("a") is None, code
        for avant, apres in zip(accords, accords[1:]):
            assert avant["a"] == apres["de"], code
        for accord in accords:
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", accord["de"]), code
            assert accord.get("a") is None or accord["de"] < accord["a"], code
            for cle, permises in valeurs.items():
                assert accord.get(cle) is None or accord[cle] in permises, (code, cle)
            if accord["instrument"] == "convention":
                assert accord["calcul"] in valeurs["calcul"], code
            # Les États tiers qu'une convention fait compter sont des États du
            # tableau, autres qu'elle.
            tiers = accord.get("etats_tiers")
            assert tiers is None or (accord["instrument"] == "convention" and tiers
                                     and set(tiers) <= set(etats) - {code, "OI"}), code
            # Les listes plus anciennes sont datées, après l'entrée en vigueur
            # de la convention et avant la liste du CLEISS.
            le = accord.get("etats_tiers_le")
            assert le is None or (tiers and re.fullmatch(r"\d{4}-\d{2}-\d{2}", le)), code
            for lue in accord.get("etats_tiers_lus") or ():
                assert set(lue) == {"le", "etats", "source"}, code
                assert accord["de"] <= lue["le"] < (le or "9999"), code
                assert set(lue["etats"]) <= set(etats) - {code, "OI"}, code
        # Un régime équivalent pour le salaire annuel moyen est celui d'un
        # État des règlements européens, pour des activités que la saisie
        # connaît, ses dates au jour.
        equivalence = etat.get("salaire_moyen")
        if equivalence is not None:
            assert accords[-1]["instrument"] == "reglements_europeens", code
            assert equivalence["activites"] and set(equivalence["activites"]) <= {
                "salariee", "non_salariee"}, code
            assert set(equivalence) <= {"activites", "periodes_depuis", "pensions_depuis"}, code
            for cle in ("periodes_depuis", "pensions_depuis"):
                assert equivalence.get(cle) is None or re.fullmatch(
                    r"\d{4}-01-01", equivalence[cle]), code
    # Le tableau de la circulaire Cnav n° 2012/26 et la Croatie (n° 2013/56).
    assert sorted(code for code, etat in etats.items() if etat.get("salaire_moyen")) == sorted(
        "AT BE CH CY CZ DE EE ES HR HU IT LI LU PL PT RO SE SI SK".split())


# -- la saisie ---------------------------------------------------------------------

#: Une carrière commencée au Maroc, interrompue par trois ans en Allemagne, une
#: pension allemande à venir, une retraite au Portugal.
CHAMPS = {"etranger1_pays": "MA", "etranger1_debut": "1980-01", "etranger1_fin": "1986-09",
          "etranger2_pays": "DE", "etranger2_debut": "1998-01", "etranger2_fin": "2001-07",
          "etranger2_activite": "non_salariee",
          "pension_etrangere1_pays": "DE", "pension_etrangere1": "250",
          "pension_etrangere1_debut": "2032-07", "residence": "PT"}


def test_la_saisie_lit_la_carriere_hors_de_france_et_la_rend_a_l_adresse():
    """Les périodes, les pensions et la résidence se disent par l'adresse, les
    dates comme un début d'activité, et l'adresse les rend telles qu'elle les
    a reçues ; l'activité salariée, celle qu'une ligne ne dit pas, ne
    s'écrit pas."""
    saisie = _saisie(**CHAMPS)
    declare = saisie.etranger_declare()
    assert [(p["pays"], saisie.date_de(p["debut"]), saisie.date_de(p["fin"]), p["activite"])
            for p in declare["periodes"]] == [
        ("MA", DateMois(1980, 1), DateMois(1986, 9), "salariee"),
        ("DE", DateMois(1998, 1), DateMois(2001, 7), "non_salariee")]
    assert [(p["pays"], saisie.date_de(p["age"]), p["montant"]) for p in declare["pensions"]] \
        == [("DE", DateMois(2032, 7), 250.0)]
    assert declare["residence"] == "PT"
    requete = saisie.requete()
    assert "etranger1_activite" not in requete and "etranger2_activite=non_salariee" in requete
    relue = Saisie.depuis_requete(dict(pair.split("=", 1) for pair in requete.split("&")))
    assert relue.etranger_declare() == declare
    assert _saisie().etranger_declare() is None
    assert _saisie(residence="autre").etranger_declare() == {
        "periodes": [], "pensions": [], "residence": "autre", "mois_en_france": None}
    # Les mois passés en France chaque année, pour qui y réside.
    en_france = _saisie(mois_en_france="8")
    assert en_france.etranger_declare()["mois_en_france"] == 8
    assert "mois_en_france=8" in en_france.requete()


def test_une_annee_passee_hors_de_france_n_est_pas_travaillee_en_france():
    """L'année que la période à l'étranger occupe pour plus de la moitié de
    ses mois de carrière est une année sans activité ; celle qui précède le
    premier emploi en France n'en interrompt aucune, et le champ
    « Interruptions » garde le dernier mot."""
    saisie = _saisie(**CHAMPS)
    assert saisie.interruptions_de_carriere() == {1998: "sans_activite",
                                                  1999: "sans_activite",
                                                  2000: "sans_activite"}
    # Six mois sur douze en 2001 : à égalité, l'année reste travaillée. La
    # période marocaine finit au premier emploi en France : elle n'en touche
    # aucun mois. Prolongée jusqu'en mars 1987, elle prend les quatre mois de
    # 1986, et deux mois sur douze de 1987 ; jusqu'en août, sept.
    debordante = _saisie(etranger1_pays="MA", etranger1_debut="1980-01",
                         etranger1_fin="1987-03")
    assert debordante.interruptions_de_carriere() == {1986: "sans_activite"}
    assert _saisie(etranger1_pays="MA", etranger1_debut="1980-01", etranger1_fin="1987-08",
                   ).interruptions_de_carriere() == {1986: "sans_activite",
                                                     1987: "sans_activite"}
    assert _saisie(**CHAMPS, interruptions="1999:1999:chomage_indemnise",
                   ).interruptions_de_carriere()[1999] == "chomage_indemnise"


@pytest.mark.parametrize("champs, refus", [
    ({"etranger1_pays": "DE"}, "indiquer le mois où elle commence et celui où elle finit"),
    ({"etranger2_debut": "1990-01", "etranger2_fin": "1992-01"},
     "Période à l'étranger n° 2 : indiquer l'État"),
    ({"etranger1_pays": "DE", "etranger1_debut": "1990-01", "etranger1_fin": "1992-01",
      "etranger1_activite": "independante"}, "n'est pas une activité possible"),
    ({"etranger1_pays": "FR", "etranger1_debut": "1990-01", "etranger1_fin": "1992-01"},
     "la France n'est pas un État étranger"),
    ({"etranger1_pays": "de", "etranger1_debut": "1990-01", "etranger1_fin": "1992-01"},
     "« de » n'est pas un État"),
    ({"etranger1_pays": "DE", "etranger1_debut": "1979-01", "etranger1_fin": "1982-01"},
     "elle commence au plus tôt à 14 ans"),
    ({"etranger1_pays": "DE", "etranger1_debut": "1992-01", "etranger1_fin": "1992-01"},
     "après avoir commencé"),
    ({"etranger1_pays": "DE", "etranger1_debut": "2020-01", "etranger1_fin": "2029-02"},
     "elle finit au plus tard au départ"),
    ({"etranger1_pays": "DE", "etranger1_debut": "1995-01", "etranger1_fin": "1999-01",
      "etranger2_pays": "AT", "etranger2_debut": "1990-01", "etranger2_fin": "1995-02"},
     "Périodes à l'étranger n° 2 et n° 1 : elles se chevauchent"),
    ({"pension_etrangere1_pays": "DE", "pension_etrangere1_debut": "2032-07"},
     "indiquer son montant brut mensuel"),
    ({"pension_etrangere1_pays": "DE", "pension_etrangere1": "250"},
     "indiquer le mois où elle commence"),
    ({"pension_etrangere1_pays": "DE", "pension_etrangere1": "0",
      "pension_etrangere1_debut": "2032-07"}, "strictement positif"),
    ({"pension_etrangere1_pays": "DE", "pension_etrangere1": "250",
      "pension_etrangere1_debut": "2045-07"}, "soit de 14 à 75 ans"),
    ({"residence": "FR"}, "Résidence après le départ : la France n'est pas un État étranger"),
    ({"mois_en_france": "13"}, "Mois en France chaque année : de 0 à 12"),
    ({"mois_en_france": "-1"}, "Mois en France chaque année : de 0 à 12"),
])
def test_la_saisie_refuse_ce_qui_ne_tient_pas(champs, refus):
    with pytest.raises(ErreurSaisie, match=refus):
        _saisie(**champs)


def test_une_periode_peut_finir_au_depart_et_toucher_la_suivante():
    """Une période qui finit le mois du départ, et deux périodes bout à bout :
    rien ne se chevauche."""
    saisie = _saisie(etranger1_pays="DE", etranger1_debut="2020-01", etranger1_fin="2024-01",
                     etranger2_pays="CH", etranger2_debut="2024-01", etranger2_fin="2029-01")
    assert len(saisie.etranger) == 2


# -- le contexte : les États du tableau ---------------------------------------------

def test_le_contexte_refuse_un_etat_que_le_tableau_ne_connait_pas():
    from retraite_notionnelle.contexte import Contexte

    contexte = Contexte()
    with pytest.raises(ErreurSaisie, match="aucun État « ZZ » au tableau des accords"):
        contexte.simuler(_saisie(etranger1_pays="ZZ", etranger1_debut="1990-01",
                                 etranger1_fin="1992-01"))
    with pytest.raises(ErreurSaisie, match="Pension étrangère n° 1 : aucun État « NC »"):
        contexte.simuler(_saisie(pension_etrangere1_pays="NC", pension_etrangere1="100",
                                 pension_etrangere1_debut="2030-07"))
    with pytest.raises(ErreurSaisie, match="on réside dans un État"):
        contexte.simuler(_saisie(residence="OI"))
    # Un État sans accord, une organisation internationale : la carrière tient.
    contexte.simuler(_saisie(etranger1_pays="autre", etranger1_debut="1980-01",
                             etranger1_fin="1983-01", etranger2_pays="OI",
                             etranger2_debut="2010-01", etranger2_fin="2012-01",
                             residence="autre"))


# -- la chronologie et la carrière ---------------------------------------------------

ETRANGER = {
    "periodes": [{"pays": "MA", "debut": 15.0, "fin": 21.0, "activite": "salariee"},
                 {"pays": "DE", "debut": 33.5, "fin": 36.5, "activite": "non_salariee"}],
    "pensions": [{"pays": "DE", "age": 67.0, "mensuel": 250.0}],
    "residence": "PT",
}


def test_la_chronologie_porte_les_periodes_les_pensions_et_la_residence(simulateur):
    carriere = Carriere.depuis_parcours(
        annee_naissance=1965, sexe="H", mois_naissance=6,
        metiers=[Metier("salarie_prive_non_cadre", 21.0)], age_liquidation=64.0,
        macro=simulateur.macro, interruptions={1999: "sans_activite", 2000: "sans_activite",
                                               2001: "sans_activite"},
        etranger=ETRANGER)
    periodes = chrono.periodes_a_l_etranger(carriere.chronologie, carriere.personne)
    assert [(f["id"], f["debut"], f["fin"], f["territoire"], f["attributs"])
            for f in periodes] == [
        ("etranger_1", "1980-06-01", "1986-06-01", "MA", {"activite": "salariee"}),
        ("etranger_2", "1998-12-01", "2001-12-01", "DE", {"activite": "non_salariee"})]
    pension, = chrono.pensions_etrangeres(carriere.chronologie, carriere.personne)
    assert (pension["sorte"], pension["debut"], pension["territoire"]) == (
        "acte_de_la_caisse", "2032-06-01", "DE")
    assert pension["attributs"] == {"acte": "liquidation", "age": 67.0}
    assert pension["montant"] == {"mensuel": 250.0, "monnaie": "EUR"}
    residence = chrono.residence(carriere.chronologie, carriere.personne)
    # Né le 15 juin 1965 (jour présumé), il part à soixante-quatre ans en
    # juillet 2029 : la résidence court de ce mois-là.
    assert (residence["debut"], residence["territoire"]) == ("2029-07-01", "PT")
    assert chrono.controler(carriere.chronologie) == []
    # Aucun autre fait ne dit son territoire : la métropole, le défaut du contrat.
    assert {f.get("territoire") for f in carriere.chronologie["faits"]} == {
        None, "MA", "DE", "PT"}
    assert carriere.periodes_a_l_etranger == (
        PeriodeALEtranger("MA", DateMois(1980, 6), DateMois(1986, 6), "salariee"),
        PeriodeALEtranger("DE", DateMois(1998, 12), DateMois(2001, 12), "non_salariee"))
    assert carriere.pensions_etrangeres == (PensionEtrangere("DE", DateMois(2032, 6), 250.0),)
    assert carriere.residence == "PT"
    # Une copie de travail garde la chronologie dont elle vient.
    prolongee = carriere.prolongee(66.0, simulateur.macro)
    assert prolongee.periodes_a_l_etranger == carriere.periodes_a_l_etranger
    assert prolongee.residence == "PT"


def test_un_releve_porte_aussi_la_carriere_hors_de_france(simulateur):
    carriere = Carriere.depuis_releve(
        annee_naissance=1962, sexe="F", age_liquidation=63.0, macro=simulateur.macro,
        releve=[LigneRelevee(annee, "salarie_prive_non_cadre", 25000.0, 4)
                for annee in range(1990, 2025)],
        etranger={"periodes": [{"pays": "TN", "debut": 18.0, "fin": 27.0,
                                "activite": "salariee"}],
                  "pensions": [], "residence": None})
    assert carriere.periodes_a_l_etranger == (
        PeriodeALEtranger("TN", DateMois(1980, 1), DateMois(1989, 1), "salariee"),)
    assert carriere.pensions_etrangeres == () and carriere.residence is None


def test_sans_carriere_hors_de_france_la_carriere_n_en_dit_rien(simulateur):
    carriere = Carriere.depuis_profil(1965, "H", "salarie_prive_non_cadre", 21.0, 64.0,
                                      simulateur.macro)
    assert carriere.periodes_a_l_etranger == () and carriere.pensions_etrangeres == ()
    assert carriere.residence is None


@pytest.mark.parametrize("etranger, erreur", [
    ({"periodes": [{"pays": "DE", "debut": 30.0, "fin": 35.0, "activite": "salariee"},
                   {"pays": "AT", "debut": 34.0, "fin": 36.0, "activite": "salariee"}]},
     "deux périodes à l'étranger se chevauchent"),
    ({"periodes": [{"pays": "DE", "debut": 30.0, "fin": 70.0, "activite": "salariee"}]},
     "au plus tard au départ"),
    ({"periodes": [{"pays": "FR", "debut": 30.0, "fin": 35.0, "activite": "salariee"}]},
     "un État étranger : son code, reçu « FR »"),
    ({"periodes": [{"pays": "DE", "debut": 30.0, "fin": 35.0, "activite": "artiste"}]},
     "salariée ou non, reçu « artiste »"),
    ({"pensions": [{"pays": "DE", "age": 67.0, "mensuel": 0}]},
     "le montant d'une pension étrangère : positif"),
])
def test_la_chronologie_refuse_ce_qui_ne_tient_pas(simulateur, etranger, erreur):
    with pytest.raises(ValueError, match=erreur):
        chrono.du_resume(1965, "H", 6, 64.0, etranger=etranger)


# -- le portage ----------------------------------------------------------------------

#: Des saisies du formulaire qui portent une carrière hors de France, sur les
#: deux chemins : le parcours et le relevé.
REQUETES = [
    {"naissance": "1965-06-15", "debut": "1986-09", "liquidation": "2029-01", **CHAMPS},
    {"naissance": "1958-02", "debut": "1984-03", "liquidation": "2020-03",
     "etranger1_pays": "autre", "etranger1_debut": "1976-01", "etranger1_fin": "1983-04",
     "etranger2_pays": "OI", "etranger2_debut": "2005-01", "etranger2_fin": "2012-01",
     "pension_etrangere1_pays": "OI", "pension_etrangere1": "1200,5",
     "pension_etrangere1_debut": "2018-03", "residence": "autre"},
    {"naissance": "1960-11-15", "liquidation": "2024-01", "residence": "MA",
     "releve": "1988:salarie_prive_non_cadre:21000:4, 1989:salarie_prive_non_cadre:22000:4",
     "etranger1_pays": "MA", "etranger1_debut": "1980-01", "etranger1_fin": "1988-01",
     "pension_etrangere1_pays": "MA", "pension_etrangere1": "310",
     "pension_etrangere1_debut": "2020-12"},
    {"naissance": "1957-04-15", "debut": "1982-01", "liquidation": "2022-01",
     "mois_en_france": "7"},
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
  const saisie = Saisie.depuisRequete(requete, false, contexte.paquet.presomptions);
  contexte.simuler(saisie);
  return {
    requete: saisie.requete(),
    interruptions: Object.fromEntries(saisie.interruptionsDeCarriere()),
    sans_activite: vue.lignes.filter((l) => l.type_periode === "sans_activite")
      .map((l) => l.annee),
    periodes: vue.periodesALEtranger.map((p) => [p.pays, mois(p.debut), mois(p.fin),
      p.activite]),
    pensions: vue.pensionsEtrangeres.map((p) => [p.pays, mois(p.debut), p.mensuel]),
    residence: vue.residence,
    mois_en_france: vue.moisEnFrance,
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
    saisie = Saisie.depuis_requete(requete)
    Contexte().simuler(saisie)
    vue = vues[0]
    mois = "{0.annee}-{0.mois:02d}".format
    return {
        "requete": saisie.requete(),
        "interruptions": {str(annee): motif
                          for annee, motif in saisie.interruptions_de_carriere().items()},
        "sans_activite": [ligne.annee for ligne in vue.lignes
                          if ligne.type_periode == "sans_activite"],
        "periodes": [[p.pays, mois(p.debut), mois(p.fin), p.activite]
                     for p in vue.periodes_a_l_etranger],
        "pensions": [[p.pays, mois(p.debut), p.mensuel] for p in vue.pensions_etrangeres],
        "residence": vue.residence,
        "mois_en_france": vue.mois_en_france,
    }


def test_le_portage_lit_les_memes_faits(monkeypatch):
    """La saisie et la carrière des deux moteurs lisent les mêmes faits de la
    même adresse : l'adresse qu'elles réécrivent, les années que l'étranger
    interrompt, les périodes, les pensions ramenées à leur date sur les mêmes
    prix, la résidence et les mois passés en France."""
    import json
    import shutil
    import subprocess

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
    # Chaque fait y est au moins une fois : une pension future, saisie en
    # euros d'aujourd'hui, grandit avec les prix d'ici sa date ; une pension
    # passée diminue. Les années passées en Allemagne ne sont pas travaillées
    # en France ; celles d'un relevé sont celles qu'il porte.
    assert attendus[0]["pensions"][0][2] > 250.0 and attendus[1]["pensions"][0][2] < 1200.5
    assert attendus[0]["sans_activite"] == [1998, 1999, 2000]
    assert attendus[1]["periodes"][1][0] == "OI" and attendus[1]["residence"] == "autre"
    assert attendus[2]["sans_activite"] == [] and attendus[2]["residence"] == "MA"


# -- le moteur : la totalisation des périodes étrangères ---------------------------

@pytest.fixture(scope="module")
def contexte():
    from retraite_notionnelle.contexte import Contexte

    return Contexte()


def _actuel(contexte, **champs):
    """Le scénario 1 d'une saisie : ce que la page lit du système actuel."""
    return contexte.simuler(Saisie.depuis_requete(champs)).actuel


def _pension(actuel, regime):
    return next(p for p in actuel.pensions_par_regime if p.regime == regime)


#: Né en mars 1962, entré dans la vie active en France en septembre 1990,
#: parti à soixante-quatre ans : 142 trimestres en France, 169 requis.
NE_EN_1962 = {"naissance": "1962-03-15", "debut": "1990-09", "liquidation": "2026-04"}
#: Dix ans et demi au Maroc avant d'arriver en France.
AU_MAROC = {"etranger1_pays": "MA", "etranger1_debut": "1980-01", "etranger1_fin": "1990-09"}


def test_les_periodes_d_un_accord_comptent_pour_le_taux_et_non_pour_la_duree(contexte):
    """La convention franco-marocaine de 2007 fait compter les dix ans et
    demi du Maroc : 43 trimestres, qui portent la durée tous régimes de 142 à
    185, au-delà des 169 requis — le taux plein, la surcote des six trimestres
    travaillés en France après l'âge légal, et l'Agirc-Arrco sans coefficient.
    La pension reste proratisée sur les 142 trimestres français."""
    francais = _actuel(contexte, **NE_EN_1962)
    totalisee = _actuel(contexte, **NE_EN_1962, **AU_MAROC)
    assert (francais.trimestres_valides, francais.trimestres_etrangers) == (142, 0)
    assert (totalisee.trimestres_valides, totalisee.trimestres_etrangers) == (185, 43)
    assert "taux 42.500% × 142/169" in _pension(francais, "regime_general").detail
    assert "taux 53.750% × 142/169" in _pension(totalisee, "regime_general").detail
    assert "coefficient d'anticipation" in _pension(francais, "agirc_arrco").detail
    assert "coefficient" not in _pension(totalisee, "agirc_arrco").detail


def test_une_convention_qui_ne_vise_que_les_salaries(contexte):
    """La convention franco-algérienne ne vise que les salariés : l'activité
    non salariée en Algérie n'y compte pas, sauf comme activité à l'étranger
    d'avant le 1er avril 1983, reconnue équivalente pour le taux — treize
    trimestres de 1980 à mars 1983 (R. 351-4, 1°). Un État qu'aucun accord ne
    lie à la France en fait autant."""
    algerie = {"etranger1_pays": "DZ", "etranger1_debut": "1980-01", "etranger1_fin": "1990-09"}
    salariee = _actuel(contexte, **NE_EN_1962, **algerie)
    non_salariee = _actuel(contexte, **NE_EN_1962, **algerie, etranger1_activite="non_salariee")
    autre = _actuel(contexte, **NE_EN_1962, **{**algerie, "etranger1_pays": "autre"})
    assert salariee.trimestres_etrangers == 43
    assert non_salariee.trimestres_etrangers == autre.trimestres_etrangers == 13


def test_les_fonctionnaires_ne_comptent_que_les_reglements_europeens(contexte):
    """Les régimes du code des pensions n'entrent dans la coordination
    européenne que le 25 octobre 1998 (règlement 1606/98), et aucune
    convention bilatérale ne les vise : dix ans en Allemagne portent la
    décote de l'agent de l'État au taux plein, dix ans au Maroc ne lui
    apportent rien."""
    etat = {**NE_EN_1962, "statut": "fonctionnaire_etat"}
    allemagne = _actuel(contexte, **etat, **{**AU_MAROC, "etranger1_pays": "DE"})
    maroc = _actuel(contexte, **etat, **AU_MAROC)
    assert allemagne.trimestres_etrangers == 43 and maroc.trimestres_etrangers == 0
    assert "taux 80.625%" in _pension(allemagne, "fonction_publique_etat").detail
    assert "taux 63.750%" in _pension(maroc, "fonction_publique_etat").detail


def test_l_annee_ne_depasse_pas_quatre_trimestres(contexte, simulateur):
    """Les périodes étrangères complètent celles de la carrière française sans
    s'y superposer (R. 351-5) : huit mois au Maroc en 1990, l'année où la
    carrière française commence en septembre, n'en apportent que trois ; le
    trimestre de l'année du départ, au plus les trimestres civils écoulés."""
    from retraite_notionnelle.droit import etranger

    carriere = Carriere.depuis_parcours(
        annee_naissance=1962, sexe="H", mois_naissance=3,
        metiers=[Metier("salarie_prive_non_cadre", 28.5)], age_liquidation=64.0,
        macro=simulateur.macro,
        etranger={"periodes": [{"pays": "MA", "debut": 18.0, "fin": 28.5,
                                "activite": "salariee"}],
                  "pensions": [], "residence": None})
    trimestres = etranger.trimestres_etrangers(simulateur.scenario_actuel, carriere)
    assert trimestres.pour_le_taux[etranger.GENERALE][1980] == 4
    assert trimestres.pour_le_taux[etranger.GENERALE][1990] == 3
    assert trimestres.cotises[etranger.GENERALE] == trimestres.pour_le_taux[etranger.GENERALE]
    assert trimestres.trimestres(etranger.FONCTIONNAIRES) == 0


def test_une_organisation_internationale_compte_pour_le_taux_seul(contexte, simulateur):
    """Depuis 2010, l'affiliation au régime d'une organisation internationale
    compte pour le taux, un trimestre par quatre-vingt-dix jours (R. 161-16-1),
    jamais comme durée cotisée ; avant 2010, rien."""
    from retraite_notionnelle.droit import etranger

    def compte(liquidation: float):
        carriere = Carriere.depuis_parcours(
            annee_naissance=1955, sexe="F", mois_naissance=6,
            metiers=[Metier("salarie_prive_non_cadre", 22.0)], age_liquidation=liquidation,
            macro=simulateur.macro, interruptions={a: "sans_activite" for a in range(2000, 2006)},
            etranger={"periodes": [{"pays": "OI", "debut": 44.5, "fin": 51.0,
                                    "activite": "salariee"}],
                      "pensions": [], "residence": None})
        return etranger.trimestres_etrangers(simulateur.scenario_actuel, carriere)

    apres = compte(62.0)
    assert apres.trimestres(etranger.GENERALE) == apres.trimestres(etranger.FONCTIONNAIRES) == 24
    assert apres.trimestres_cotises(etranger.GENERALE) == 0
    # Liquidée en 2009 : avant que L. 161-19-1 ne s'applique.
    avant = compte(54.0)
    assert avant.trimestres(etranger.GENERALE) == 0


def test_la_carriere_longue_compte_les_periodes_etrangeres(contexte):
    """Un salarié né en 1958, entré au Portugal à quinze ans, en France à
    vingt-six : la convention de 1973, puis les règlements européens
    depuis 1986, font compter ses années portugaises « dans les mêmes
    conditions que les périodes accomplies en France » — l'entrée précoce et
    la durée cotisée de la carrière longue. Il part à soixante ans."""
    champs = {"naissance": "1958-05-15", "debut": "1985-01", "liquidation": "2018-06"}
    francais = _actuel(contexte, **champs)
    portugais = _actuel(contexte, **champs, etranger1_pays="PT", etranger1_debut="1974-03",
                        etranger1_fin="1985-01")
    assert francais.motif_ouverture == "non_ouverte"
    assert portugais.motif_ouverture == "carriere_longue"
    assert portugais.trimestres_etrangers == 44


def test_les_etapes_disent_ce_que_la_coordination_fait_des_periodes(simulateur):
    """La coordination dit le titre de chaque période, les durées ce que
    chaque famille en retient : chacune suit le schéma de son étape."""
    from retraite_notionnelle.droit import compter, coordonner
    from retraite_notionnelle.noyau import contrats

    carriere = Carriere.depuis_parcours(
        annee_naissance=1962, sexe="H", mois_naissance=3,
        metiers=[Metier("salarie_prive_non_cadre", 28.5)], age_liquidation=64.0,
        macro=simulateur.macro,
        etranger={"periodes": [
            {"pays": "MA", "debut": 18.0, "fin": 24.0, "activite": "non_salariee"},
            {"pays": "DE", "debut": 24.0, "fin": 28.5, "activite": "salariee"}],
            "pensions": [], "residence": None})
    actuel = simulateur.scenario_actuel
    coordination = coordonner.coordonner(actuel, carriere)
    donnees = coordination.donnees()
    assert [(p["pays"], p["titre"], p["instrument"], p["familles"])
            for p in donnees["etranger"]] == [
        ("MA", "accord", "convention", ["regime_general"]),
        ("DE", "accord", "reglements_europeens", ["regime_general", "fonction_publique"])]
    durees = compter.compter(actuel, coordination)
    for etape, objet, valeur in (("coordonner_les_affiliations", "coordination", donnees),
                                 ("compter_les_durees", "durees", durees.donnees())):
        erreurs = [c for c in contrats.Validateur(etape, contrats.ETAPES).valider(valeur, objet)
                   if c.genre == "erreur"]
        assert erreurs == [], erreurs
    assert durees.pour_le_taux("regime_general") == durees.trimestres + 43
    assert durees.pour_le_taux(None) == durees.trimestres


# -- le moteur : la pension proratisée, la pension nationale, et leur minimum ------

#: Née en mars 1960, au salaire de 44 % du salaire moyen, partie en avril 2024 :
#: 167 trimestres requis, et le minimum contributif de l'année.
PETIT_SALAIRE = {"naissance": "1960-03-15", "liquidation": "2024-04",
                 "unite_revenu": "moyen", "salaire": "0.44"}
#: Cinq ans en Allemagne, puis toute une carrière en France : 169 trimestres.
APRES_L_ALLEMAGNE = {**PETIT_SALAIRE, "debut": "1982-01", "etranger1_pays": "DE",
                     "etranger1_debut": "1977-01", "etranger1_fin": "1982-01"}
#: Vingt-cinq ans en Espagne, puis 85 trimestres en France, commencés à
#: quarante-deux ans : la carrière a commencé hors de France.
APRES_L_ESPAGNE = {**PETIT_SALAIRE, "debut": "2003-01", "etranger1_pays": "ES",
                   "etranger1_debut": "1978-01", "etranger1_fin": "2003-01"}
#: Les mêmes années au Sénégal, dont la convention sert la pension nationale,
#: les périodes sénégalaises comptées pour le taux (calcul séparé).
APRES_LE_SENEGAL = {**APRES_L_ESPAGNE, "etranger1_pays": "SN"}


def test_une_carriere_commencee_hors_de_france_peut_venir_tard_en_france():
    """Le premier emploi en France peut venir après l'âge de début le plus
    tardif quand la carrière a commencé à l'étranger."""
    with pytest.raises(ErreurSaisie, match="Début d'activité"):
        Saisie.depuis_requete({**PETIT_SALAIRE, "debut": "2003-01"})
    assert Saisie.depuis_requete(APRES_L_ESPAGNE).debut > 42


def test_la_pension_nationale_est_servie_quand_son_minimum_l_emporte(contexte, simulateur):
    """Une carrière française complète, et cinq ans en Allemagne : la pension
    proratisée gagne la surcote des vingt trimestres allemands, mais son
    minimum se proratise sur la durée totale non limitée — 167/189 du minimum
    majoré —, quand celui de la pension nationale est entier. La pension
    nationale, plus élevée, est servie (règlement 883/2004, article 52)."""
    _, majore, _, _ = simulateur.scenario_actuel.minimum_contributif.valeurs(2024)
    actuel = _actuel(contexte, **APRES_L_ALLEMAGNE)
    pension = _pension(actuel, "regime_general")
    assert (actuel.trimestres_valides, actuel.trimestres_etrangers) == (189, 20)
    assert pension.detail.startswith(
        "pension nationale, plus élevée que la pension proratisée (10,208.36 €) : "
        "SR 18,371.05 € × taux 51.250% × 167/167 = 9,415.16 €, porté au minimum "
        "contributif par + 1,328.08 €")
    # Le minimum se compare à la pension avant surcote, qui s'y ajoute : la
    # nationale a celle de ses deux trimestres français au-delà des 167, la
    # proratisée celle des huit trimestres d'après l'âge légal.
    nue = 18371.05 * 0.5
    assert pension.montant == pytest.approx(majore + nue * 0.025, abs=0.02)
    assert majore * 167 / 189 + nue * 0.1 == pytest.approx(10208.36, abs=0.02)


def test_la_pension_proratisee_est_portee_au_minimum_international(contexte, simulateur):
    """Vingt-cinq ans en Espagne : le minimum de la pension proratisée est le
    minimum entier — la durée totale dépasse la durée maximum —, réduit à la
    part française de la durée totale, 85/185 ; la majoration de même. La
    pension nationale, décotée faute de durée française, est plus faible."""
    _, majore, _, _ = simulateur.scenario_actuel.minimum_contributif.valeurs(2024)
    pension = _pension(_actuel(contexte, **APRES_L_ESPAGNE), "regime_general")
    assert pension.detail.startswith(
        "pension proratisée, au moins égale à la pension nationale (4,072.48 €) : "
        "SR 18,826.39 € × taux 55.000% × 85/167 = 5,270.26 €, porté au minimum "
        "contributif par + ")
    nue = 18826.39 * 0.5 * 85 / 167
    assert pension.montant == pytest.approx(majore * 85 / 185 + nue * 0.1, abs=0.01)


def test_une_convention_a_calcul_separe_garde_le_minimum_de_toute_pension(contexte):
    """La convention franco-sénégalaise ne compare rien : sa pension, au taux
    que les périodes sénégalaises ouvrent, est portée au minimum de toute
    pension, proratisé sur la durée française — plus haut que le minimum
    international de l'Espagne."""
    senegal = _pension(_actuel(contexte, **APRES_LE_SENEGAL), "regime_general")
    espagne = _pension(_actuel(contexte, **APRES_L_ESPAGNE), "regime_general")
    assert senegal.detail == ("SR 18,826.39 € × taux 55.000% × 85/167 = 5,270.26 €, "
                              "porté au minimum contributif par + 560.09 €")
    assert senegal.montant > espagne.montant


#: Une pension sénégalaise de 750 € par mois, en euros d'aujourd'hui, depuis
#: avril 2020.
AU_SENEGAL = {"pension_etrangere1_pays": "SN", "pension_etrangere1": "750",
              "pension_etrangere1_debut": "2020-04"}


@pytest.mark.parametrize("ce_qui_change, ecretee", [
    (AU_SENEGAL, True),
    ({**AU_SENEGAL, "pension_etrangere1_debut": "2025-04"}, False),
    ({**AU_SENEGAL, "etranger1_pays": "ES", "pension_etrangere1_pays": "ES"}, False),
    ({**AU_SENEGAL, "naissance": "1946-03-15", "liquidation": "2011-04",
      "pension_etrangere1": "3000", "pension_etrangere1_debut": "2008-04"}, False),
])
def test_l_ecretement_du_minimum_compte_les_pensions_etrangeres(contexte, simulateur,
                                                                 ce_qui_change, ecretee):
    """Depuis 2012, le minimum n'est servi que jusqu'au plafond de toutes les
    pensions personnelles, étrangères comprises (L. 173-2) : la pension
    sénégalaise le rogne jusqu'au plafond. Une pension qui commence après la
    date d'effet, celle que calculent les règlements européens, ou toute
    pension d'avant 2012, n'y comptent pas."""
    def minimum(actuel):
        return next(a.montant for a in actuel.avantages_appliques
                    if a.code == "minimum_contributif")

    requete = {**APRES_LE_SENEGAL, **ce_qui_change}
    sans = {cle: valeur for cle, valeur in requete.items()
            if not cle.startswith("pension_etrangere")}
    avec, declaree = _actuel(contexte, **sans), _actuel(contexte, **requete)
    if not ecretee:
        assert minimum(declaree) == minimum(avec) > 0
        return
    # Le total des pensions françaises et de la pension sénégalaise, en euros
    # de la date d'effet, atteint le plafond, et ne le dépasse pas.
    _, _, plafond, _ = simulateur.scenario_actuel.minimum_contributif.valeurs(2024)
    etrangere = 750 * 12 * simulateur.macro.coefficient_prix(
        simulateur.parametres.annee_courante, 2024)
    assert declaree.pension_annuelle + etrangere == pytest.approx(plafond, abs=0.01)
    assert 0 < minimum(declaree) < minimum(avec)


def test_le_minimum_se_revise_quand_une_pension_etrangere_commence_apres_le_depart(
        contexte):
    """La majoration du minimum « est révisée lorsque le montant des avantages
    personnels de retraite a varié », le plafond revalorisé comme les pensions
    (R. 173-8) : la pension sénégalaise qui commence en 2025, un an après le
    départ, ne change rien au départ, et rogne aujourd'hui le minimum de ce
    qu'elle passe de la marge sous le plafond. Une pension des règlements
    européens n'y compte pas ; une petite pension tient dans la marge."""
    sans = contexte.simuler(Saisie.depuis_requete(APRES_LE_SENEGAL))
    apres = {**AU_SENEGAL, "pension_etrangere1_debut": "2025-01"}
    avec = contexte.simuler(Saisie.depuis_requete({**APRES_LE_SENEGAL, **apres}))
    assert avec.actuel.pension_annuelle == pytest.approx(sans.actuel.pension_annuelle)
    ecrete = avec.actuel.minimum_ecrete
    assert ecrete is not None and ecrete.marge > ecrete.avant_ecretement > 0
    servi = next(r for r in avec.aujourd_hui.actuel.regimes if r.regime == "regime_general")
    garde = next(r for r in sans.aujourd_hui.actuel.regimes if r.regime == "regime_general")
    assert garde.revision == 0 and servi.coefficient == pytest.approx(garde.coefficient)
    # Les 750 € d'aujourd'hui, en euros de l'année : 9 000 € par an.
    mene = servi.coefficient
    attendue = (ecrete.avant_ecretement * mene
                - max(0.0, min(ecrete.avant_ecretement * mene, ecrete.marge * mene - 9000.0)))
    assert servi.revision == pytest.approx(attendue) and servi.revision > 0
    assert servi.aujourd_hui == pytest.approx(garde.aujourd_hui - attendue)
    for autre in ({**apres, "pension_etrangere1_pays": "ES"},
                  {**apres, "pension_etrangere1": "300"}):
        tenue = contexte.simuler(Saisie.depuis_requete({**APRES_LE_SENEGAL, **autre}))
        assert all(r.revision == 0 for r in tenue.aujourd_hui.actuel.regimes)


#: Né en mars 1955, vingt-six ans en France au cinquième du salaire moyen,
#: parti à soixante-cinq ans en avril 2020 : l'ASPA complète sa pension.
PETITE_CARRIERE = {"naissance": "1955-03-15", "debut": "1994-01", "liquidation": "2020-04",
                   "unite_revenu": "moyen", "salaire": "0.2"}
#: Quatre ans au Maroc avant la France.
AU_MAROC_AVANT = {"etranger1_pays": "MA", "etranger1_debut": "1990-01",
                  "etranger1_fin": "1994-01"}


@pytest.mark.parametrize("residence", ["MA", "autre"])
def test_l_aspa_n_est_servie_qu_a_qui_reside_en_france(contexte, residence):
    """L'allocation de solidarité aux personnes âgées n'est servie qu'à qui
    réside en France, et supprimée au départ hors de France (L. 815-1) : la
    même petite carrière, qui part vivre au Maroc ou ailleurs, ne touche que
    sa pension, à la liquidation comme à chaque échéance."""
    def aspa(actuel):
        return sum(a.montant for a in actuel.avantages_appliques
                   if a.code == "minimum_vieillesse")

    en_france = contexte.simuler(Saisie.depuis_requete(PETITE_CARRIERE))
    ailleurs = contexte.simuler(Saisie.depuis_requete({**PETITE_CARRIERE,
                                                       "residence": residence}))
    assert aspa(en_france.actuel) > 0 and aspa(ailleurs.actuel) == 0
    assert ailleurs.actuel.pension_annuelle == pytest.approx(
        en_france.actuel.pension_annuelle - aspa(en_france.actuel))
    assert en_france.aujourd_hui.actuel.minimum_vieillesse > 0
    assert ailleurs.aujourd_hui.actuel.minimum_vieillesse == 0


def test_la_garantie_de_la_proposition_ne_se_sert_qu_en_france(contexte):
    """La garantie vieillesse du scénario 6 remplace l'ASPA et en garde la
    condition de résidence, comme le texte de la proposition le dit : la même
    petite carrière, au Maroc, n'en reçoit rien, ni au départ ni aujourd'hui ;
    son compte notionnel, fait de ses seules cotisations françaises, ne bouge
    pas."""
    en_france = contexte.simuler(Saisie.depuis_requete(PETITE_CARRIERE))
    au_maroc = contexte.simuler(Saisie.depuis_requete({**PETITE_CARRIERE,
                                                       "residence": "MA"}))
    garantie = en_france.notionnel_liberal.garantie_vieillesse
    hors = au_maroc.notionnel_liberal.garantie_vieillesse
    assert garantie.complement > 0 and garantie.residence is None
    assert hors.complement == 0 and hors.residence == "MA"
    assert hors.pension_contributive == pytest.approx(garantie.pension_contributive)
    assert en_france.aujourd_hui.garantie_vieillesse > 0
    assert au_maroc.aujourd_hui.garantie_vieillesse == 0


#: Une pension marocaine de 150 € par mois, en euros d'aujourd'hui, servie
#: depuis janvier 2019 : avant le départ.
PENSION_MAROCAINE = {"pension_etrangere1_pays": "MA", "pension_etrangere1": "150",
                     "pension_etrangere1_debut": "2019-01"}


def _aspa(actuel) -> float:
    return sum(a.montant for a in actuel.avantages_appliques if a.code == "minimum_vieillesse")


def test_l_aspa_compte_les_pensions_etrangeres(contexte, simulateur):
    """L'allocation compte « tous les avantages d'invalidité et de vieillesse
    dont bénéficie l'intéressé » (R. 815-22), ceux qu'un autre État sert
    compris : la petite carrière qui touche une pension marocaine reçoit
    d'autant moins d'ASPA, au départ, et sa pension française, ASPA comprise,
    s'arrête au barème moins ce que le Maroc lui sert à part. Une pension qui
    commence après le départ ne compte qu'à partir d'elle : aujourd'hui."""
    en_france = contexte.simuler(Saisie.depuis_requete(PETITE_CARRIERE))
    marocaine = contexte.simuler(Saisie.depuis_requete({**PETITE_CARRIERE,
                                                        **PENSION_MAROCAINE}))
    # Les 150 € d'aujourd'hui, ramenés aux euros de 2020 et suivis sur les prix.
    annuelle = 150 * 12 * simulateur.macro.coefficient_prix(2026, 2020)
    assert _aspa(en_france.actuel) - _aspa(marocaine.actuel) == pytest.approx(annuelle)
    plafond = simulateur.scenario_actuel.minimum_vieillesse.plafond(2020)[0]
    assert marocaine.actuel.pension_annuelle == pytest.approx(plafond - annuelle)
    # Aujourd'hui, en euros de l'année : 1 800 €.
    assert (en_france.aujourd_hui.actuel.minimum_vieillesse
            - marocaine.aujourd_hui.actuel.minimum_vieillesse) == pytest.approx(1800.0)
    plus_tard = contexte.simuler(Saisie.depuis_requete({
        **PETITE_CARRIERE, **PENSION_MAROCAINE, "pension_etrangere1_debut": "2024-01"}))
    assert _aspa(plus_tard.actuel) == pytest.approx(_aspa(en_france.actuel))
    assert plus_tard.aujourd_hui.actuel.minimum_vieillesse == pytest.approx(
        marocaine.aujourd_hui.actuel.minimum_vieillesse)


@pytest.mark.parametrize("mois, au_depart, aujourd_hui", [
    # Parti en 2020 : plus de six mois suffisent au départ ; aujourd'hui, il
    # en faut plus de neuf (L. 815-1, R. 111-2, depuis le 1er septembre 2023).
    ("12", True, True), ("10", True, True), ("8", True, False), ("6", False, False),
])
def test_l_aspa_demande_assez_de_mois_en_france(contexte, mois, au_depart, aujourd_hui):
    """Qui réside en France n'a l'allocation que s'il y séjourne « plus de six
    mois au cours de l'année civile de versement », plus de neuf depuis le
    1er septembre 2023 : la caisse totalise ses séjours de l'année (exposé de
    la Cnav « Condition de résidence - Aspa »). La garantie de la proposition
    garde la condition de l'ASPA qu'elle remplace."""
    simulation = contexte.simuler(Saisie.depuis_requete({**PETITE_CARRIERE,
                                                         "mois_en_france": mois}))
    assert (_aspa(simulation.actuel) > 0) is au_depart
    assert (simulation.aujourd_hui.actuel.minimum_vieillesse > 0) is aujourd_hui
    garantie = simulation.notionnel_liberal.garantie_vieillesse
    assert (garantie.complement > 0) is au_depart
    assert garantie.condition_de_residence is au_depart
    assert (simulation.aujourd_hui.garantie_vieillesse > 0) is aujourd_hui


def test_la_garantie_compte_les_pensions_etrangeres(contexte, simulateur):
    """La garantie de la proposition « remplace l'ASPA » (README) et porte au
    plancher toutes les retraites obligatoires : celle qu'un autre État sert
    en est une, que l'ASPA compte aussi. Le complément baisse d'autant, au
    départ comme aujourd'hui ; le compte notionnel ne bouge pas."""
    en_france = contexte.simuler(Saisie.depuis_requete(PETITE_CARRIERE))
    marocaine = contexte.simuler(Saisie.depuis_requete({**PETITE_CARRIERE,
                                                        **PENSION_MAROCAINE}))
    garantie = en_france.notionnel_liberal.garantie_vieillesse
    avec = marocaine.notionnel_liberal.garantie_vieillesse
    annuelle = 150 * 12 * simulateur.macro.coefficient_prix(2026, 2020)
    assert avec.pensions_etrangeres == pytest.approx(annuelle)
    assert garantie.pensions_etrangeres == 0
    assert avec.pension_contributive == pytest.approx(garantie.pension_contributive)
    assert garantie.complement - avec.complement == pytest.approx(annuelle)
    assert (en_france.aujourd_hui.garantie_vieillesse
            - marocaine.aujourd_hui.garantie_vieillesse) == pytest.approx(1800.0)


def test_le_minimum_international_suit_les_trois_cas_de_sa_majoration():
    """L'exposé de la Cnav, à la lettre : le minimum théorique, réduit à la
    durée totale quand elle n'atteint pas la durée maximum (160 ici), puis à
    la part du régime ; la majoration proratisée sur la durée totale non
    limitée quand elle dépasse la durée requise, sur la durée totale limitée
    quand la durée cotisée n'atteint pas la durée maximum, sur la durée
    cotisée du régime sinon. Le portage calcule de même."""
    import json
    import shutil
    import subprocess
    from types import SimpleNamespace

    from retraite_notionnelle.droit.completer import plancher_international

    eligible = SimpleNamespace(proratisation=160, requis=160, duree_regime=80,
                               cotisee_regime=70)
    cas = [(200, 180, True, 9000 * 80 / 200 + 2000 * 80 / 200),
           (150, 130, True, 9000 * 150 / 160 * 80 / 150 + 2000 * 130 / 160 * 80 / 150),
           (160, 160, True, 9000 * 80 / 160 + 2000 * 70 / 160),
           (200, 180, False, 9000 * 80 / 200)]
    for duree, cotisee, ouverte, attendu in cas:
        assert plancher_international(eligible, 9000, 11000, duree, cotisee,
                                      ouverte) == pytest.approx(attendu)
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    script = """
import { plancherInternational } from "./moteur/js/droit/completer.js";
const eligible = { proratisation: 160, requis: 160, dureeRegime: 80, cotiseeRegime: 70 };
const cas = JSON.parse(process.argv[1]);
process.stdout.write(JSON.stringify(cas.map(([duree, cotisee, ouverte]) =>
  plancherInternational(eligible, 9000, 11000, duree, cotisee, ouverte))));
"""
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", script, json.dumps(cas)],
        cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    assert json.loads(execution.stdout) == pytest.approx([c[3] for c in cas])


def test_la_caisse_ne_totalise_qu_un_accord_a_la_fois(contexte):
    """Huit ans en Algérie, puis trois à Monaco : les deux conventions ne
    font compter aucun État tiers, et la caisse retient les périodes d'une
    seule, celle qui lui en apporte le plus (CLEISS) — 33 trimestres, les
    mois de 1979 et de 1987 arrondis au trimestre supérieur. Les mêmes années
    en Espagne et en Tunisie s'additionnent, l'année 1987 ramenée à quatre
    trimestres : l'accord franco-tunisien fait compter l'Espagne, liée aux
    deux États."""
    deux = {**NE_EN_1962, "etranger1_pays": "DZ", "etranger1_debut": "1979-09",
            "etranger1_fin": "1987-09", "etranger2_pays": "MC", "etranger2_debut": "1987-09",
            "etranger2_fin": "1990-09"}
    algerie = _actuel(contexte, **{k: v for k, v in deux.items()
                                   if not k.startswith("etranger2")})
    assert _actuel(contexte, **deux).trimestres_etrangers == algerie.trimestres_etrangers == 33
    espagne_tunisie = _actuel(contexte, **{**deux, "etranger1_pays": "ES",
                                           "etranger2_pays": "TN"})
    assert espagne_tunisie.trimestres_etrangers == 33 + 13 - 1


#: Né en janvier 1949, parti en juillet 2009 : dix-huit ans et demi en Allemagne,
#: cinq en Belgique, puis 66 trimestres en France — l'exemple 2 de la circulaire
#: ministérielle du 3 juillet 2008.
MIGRANT_DE_2009 = {"naissance": "1949-01-15", "debut": "1993-01", "liquidation": "2009-07",
                   "etranger1_pays": "DE", "etranger1_debut": "1969-07",
                   "etranger1_fin": "1988-01", "etranger2_pays": "BE",
                   "etranger2_debut": "1988-01", "etranger2_fin": "1993-01"}
#: Vingt ans dans un autre État, puis la France.
VINGT_ANS_AILLEURS = {"debut": "2000-01", "etranger1_debut": "1980-01",
                      "etranger1_fin": "2000-01"}


def _annees_du_salaire_moyen(actuel) -> tuple[int, str] | None:
    """Les années que le salaire annuel moyen du régime général retient, et
    l'article qui les réduit, quand son détail le dit."""
    lu = re.search(r"(\d+) années au plus au salaire annuel moyen \(([^)]*)\)",
                   _pension(actuel, "regime_general").detail)
    return None if lu is None else (int(lu.group(1)), lu.group(2))


def test_les_regimes_etrangers_equivalents_reduisent_les_annees_du_salaire_moyen(contexte):
    """De 2004 à juin 2022, la pension proratisée prend son salaire annuel
    moyen sur « 25 meilleures années x 66/160ème = 10 » : la durée du régime
    général rapportée à celle des régimes retenus, les régimes étrangers
    équivalents compris (circulaire ministérielle du 3 juillet 2008, exemple
    2). Le salaire moyen des dix meilleures années française l'emporte sur la
    pension nationale, qui ne compte pas l'étranger."""
    actuel = _actuel(contexte, **MIGRANT_DE_2009)
    assert (actuel.trimestres_valides, actuel.trimestres_etrangers) == (160, 94)
    assert _annees_du_salaire_moyen(actuel) == (10, "R. 173-4-3, périodes étrangères comprises")
    assert _pension(actuel, "regime_general").detail.startswith(
        "pension proratisée, au moins égale à la pension nationale")


@pytest.mark.parametrize("champs, annees", [
    # L'Italie, son « nouveau système » : les périodes depuis 1996, pour les
    # pensions depuis 2011 — seize trimestres face à soixante, 19,7 années.
    ({"naissance": "1950-02-15", "liquidation": "2015-03", "etranger1_pays": "IT"}, 20),
    ({"naissance": "1950-02-15", "liquidation": "2010-03", "etranger1_pays": "IT"}, None),
    # La Hongrie, ses seuls salariés : 25 × 76/156.
    ({"naissance": "1955-02-15", "liquidation": "2019-03", "etranger1_pays": "HU"}, 12),
    ({"naissance": "1955-02-15", "liquidation": "2019-03", "etranger1_pays": "HU",
      "etranger1_activite": "non_salariee"}, None),
    # Les Pays-Bas servent leur pension sur la résidence.
    ({"naissance": "1955-02-15", "liquidation": "2019-03", "etranger1_pays": "NL"}, None),
    # Depuis juillet 2022, la réduction ne vaut plus que hors de la
    # liquidation unique : pour qui est né avant 1953, 25 × 92/172.
    ({"naissance": "1955-02-15", "liquidation": "2023-03", "etranger1_pays": "ES"}, None),
    ({"naissance": "1952-02-15", "liquidation": "2023-03", "etranger1_pays": "ES"}, 13),
])
def test_la_reduction_suit_le_tableau_des_regimes_equivalents(contexte, champs, annees):
    """Le régime de l'État est-il équivalent pour l'activité de la période, à
    la date d'effet de la pension, et la fiche réduit-elle encore les années
    (circulaires Cnav n° 2012/26 et 2021/33) ?"""
    lu = _annees_du_salaire_moyen(_actuel(contexte, **VINGT_ANS_AILLEURS, **champs))
    assert lu == (None if annees is None
                  else (annees, "R. 173-4-3, périodes étrangères comprises"))


@pytest.mark.parametrize("tiers, liquidation, trimestres", [
    # La Roumanie, dans la liste de 2011 et non dans celle de 2026 : en 2016,
    # ses dix ans s'ajoutent aux quinze du Maroc ; en 2027, la caisse ne
    # retient qu'un accord, celui qui en apporte le plus.
    ("RO", "2016-04", 60 + 40), ("RO", "2027-04", 40),
    # Le Luxembourg, dans celle de 2026 seulement.
    ("LU", "2016-04", 60), ("LU", "2027-04", 20 + 40),
])
def test_les_etats_tiers_suivent_la_liste_lue_a_la_date_d_effet(contexte, tiers, liquidation,
                                                                trimestres):
    """Le Maroc fait compter les États tiers de la liste de la circulaire Cnav
    n° 2011/78 jusqu'à celle que le CLEISS donne en 2026 : une pension prend
    la dernière liste lue au plus tard à sa date d'effet."""
    naissance = "1951-03-15" if liquidation < "2020" else "1962-03-15"
    maroc_debut = "1975-01" if liquidation < "2020" else "1985-01"
    actuel = _actuel(contexte, naissance=naissance, debut="2000-01", liquidation=liquidation,
                     etranger1_pays="MA", etranger1_debut=maroc_debut,
                     etranger1_fin="1990-01", etranger2_pays=tiers,
                     etranger2_debut="1990-01", etranger2_fin="2000-01")
    assert actuel.trimestres_etrangers == trimestres


#: Des carrières hors de France que les deux moteurs liquident.
CARRIERES_HORS_DE_FRANCE = [
    {**NE_EN_1962, **AU_MAROC},
    {**NE_EN_1962, "etranger1_pays": "DZ", "etranger1_debut": "1980-01",
     "etranger1_fin": "1990-09", "etranger1_activite": "non_salariee"},
    {**NE_EN_1962, "statut": "fonctionnaire_etat", "etranger1_pays": "DE",
     "etranger1_debut": "1980-01", "etranger1_fin": "1990-09"},
    {**NE_EN_1962, "statut": "fonctionnaire_territorial_hospitalier", "etranger1_pays": "OI",
     "etranger1_debut": "2011-01", "etranger1_fin": "2014-07"},
    {**NE_EN_1962, "etranger1_pays": "GB", "etranger1_debut": "1985-01",
     "etranger1_fin": "1990-09", "metier2_debut": "2000-01", "metier2_statut": "fonctionnaire_etat"},
    {"naissance": "1958-05-15", "debut": "1985-01", "liquidation": "2018-06",
     "etranger1_pays": "PT", "etranger1_debut": "1974-03", "etranger1_fin": "1985-01"},
    {"naissance": "1950-02-15", "debut": "1978-01", "liquidation": "2012-03",
     "etranger1_pays": "autre", "etranger1_debut": "1968-01", "etranger1_fin": "1978-01"},
    APRES_L_ALLEMAGNE,
    APRES_L_ESPAGNE,
    {**APRES_LE_SENEGAL, **AU_SENEGAL},
    {**APRES_L_ESPAGNE, "naissance": "1945-02-15", "liquidation": "2005-03",
     "etranger1_debut": "1966-01"},
    {**PETITE_CARRIERE, **AU_MAROC_AVANT, "residence": "MA"},
    {**PETITE_CARRIERE, **AU_MAROC_AVANT, "residence": "autre",
     "metier2_debut": "2005-01", "metier2_statut": "fonctionnaire_etat"},
    # Une pension étrangère dans les ressources de l'ASPA et de la garantie.
    {**PETITE_CARRIERE, **AU_MAROC_AVANT, **PENSION_MAROCAINE},
    {**PETITE_CARRIERE, **AU_MAROC_AVANT, **PENSION_MAROCAINE,
     "pension_etrangere1_debut": "2024-01"},
    # Les mois passés en France chaque année.
    {**PETITE_CARRIERE, **AU_MAROC_AVANT, "mois_en_france": "8"},
    {**PETITE_CARRIERE, **AU_MAROC_AVANT, "mois_en_france": "6"},
    # La révision du minimum, quand une pension étrangère commence après le
    # départ.
    {**APRES_LE_SENEGAL, **AU_SENEGAL, "pension_etrangere1_debut": "2025-01"},
    # Les listes d'États tiers datées.
    {"naissance": "1951-03-15", "debut": "2000-01", "liquidation": "2016-04",
     "etranger1_pays": "MA", "etranger1_debut": "1975-01", "etranger1_fin": "1990-01",
     "etranger2_pays": "RO", "etranger2_debut": "1990-01", "etranger2_fin": "2000-01"},
    # Un seul accord à la fois, et les États tiers qu'une convention fait
    # compter.
    {"naissance": "1963-03-15", "debut": "2001-01", "liquidation": "2026-01",
     "etranger1_pays": "JP", "etranger1_debut": "1982-01", "etranger1_fin": "1997-01",
     "etranger2_pays": "MA", "etranger2_debut": "1997-01", "etranger2_fin": "2001-01"},
    {"naissance": "1964-03-15", "debut": "2002-01", "liquidation": "2027-01",
     "etranger1_pays": "ES", "etranger1_debut": "1984-01", "etranger1_fin": "1996-01",
     "etranger2_pays": "TN", "etranger2_debut": "1996-01", "etranger2_fin": "2002-01"},
    # Les années du salaire annuel moyen que les régimes équivalents réduisent.
    MIGRANT_DE_2009,
    {**VINGT_ANS_AILLEURS, "naissance": "1950-02-15", "liquidation": "2015-03",
     "etranger1_pays": "IT"},
    {**VINGT_ANS_AILLEURS, "naissance": "1955-02-15", "liquidation": "2019-03",
     "etranger1_pays": "PL", "statut": "artisan"},
    {**VINGT_ANS_AILLEURS, "naissance": "1952-02-15", "liquidation": "2023-03",
     "etranger1_pays": "ES"},
]

#: Ce que le portage liquide de ces carrières.
LIQUIDATION_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { Saisie } from "./moteur/js/saisie.js";

const contexte = new Contexte(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));
const arrondi = (montant) => (montant === undefined || montant === null ? null
  : Math.round(montant * 1e6) / 1e6);
const sortie = JSON.parse(readFileSync(0, "utf8")).map((requete) => {
  const simulation = contexte.simuler(
    Saisie.depuisRequete(requete, false, contexte.paquet.presomptions));
  const actuel = simulation.actuel;
  return {
    trimestres: [actuel.trimestres_valides, actuel.trimestres_etrangers,
      actuel.trimestres_requis],
    motif: actuel.motif_ouverture,
    pensions: actuel.pensions_par_regime.map((p) => [p.regime, p.montant, p.detail]),
    total: actuel.pension_annuelle,
    avantages: actuel.avantages_appliques.map((a) => [a.code, a.montant]),
    aspa_aujourd_hui: simulation.aujourd_hui?.actuel.minimum_vieillesse ?? null,
    // Le compte notionnel ne s'additionne pas dans le même ordre d'un moteur à
    // l'autre : la garantie se compare au millionième d'euro.
    garantie: arrondi(simulation.notionnel_liberal.garantie_vieillesse?.complement),
    garantie_aujourd_hui: arrondi(simulation.aujourd_hui?.garantie_vieillesse),
    regimes_aujourd_hui: simulation.aujourd_hui === null ? null
      : simulation.aujourd_hui.actuel.regimes.map((r) => [r.regime, arrondi(r.aujourd_hui)]),
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def _arrondi(montant: float) -> float:
    """Au millionième d'euro, comme le portage l'écrit (``Math.round``)."""
    return math.floor(montant * 1e6 + 0.5) / 1e6


def test_le_portage_liquide_les_memes_carrieres_hors_de_france(contexte):
    """Les deux moteurs comptent les mêmes trimestres étrangers et liquident
    les mêmes pensions, régime par régime, au centime et au mot près."""
    import json
    import shutil
    import subprocess

    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    racine = Path(__file__).resolve().parents[1]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", LIQUIDATION_JS], cwd=racine,
        input=json.dumps(CARRIERES_HORS_DE_FRANCE), capture_output=True, text=True,
        encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    attendus = []
    for requete in CARRIERES_HORS_DE_FRANCE:
        simulation = contexte.simuler(Saisie.depuis_requete(requete))
        actuel = simulation.actuel
        attendus.append({
            "trimestres": [actuel.trimestres_valides, actuel.trimestres_etrangers,
                           actuel.trimestres_requis],
            "motif": actuel.motif_ouverture,
            "pensions": [[p.regime, p.montant, p.detail] for p in actuel.pensions_par_regime],
            "total": actuel.pension_annuelle,
            "avantages": [[a.code, a.montant] for a in actuel.avantages_appliques],
            "aspa_aujourd_hui": (None if simulation.aujourd_hui is None
                                 else simulation.aujourd_hui.actuel.minimum_vieillesse),
            "garantie": (None if simulation.notionnel_liberal.garantie_vieillesse is None
                         else _arrondi(
                             simulation.notionnel_liberal.garantie_vieillesse.complement)),
            "garantie_aujourd_hui": (None if simulation.aujourd_hui is None
                                     else _arrondi(simulation.aujourd_hui.garantie_vieillesse)),
            "regimes_aujourd_hui": (None if simulation.aujourd_hui is None
                                    else [[r.regime, _arrondi(r.aujourd_hui)]
                                          for r in simulation.aujourd_hui.actuel.regimes]),
        })
    assert json.loads(execution.stdout) == json.loads(json.dumps(attendus))
    assert all(attendu["trimestres"][1] > 0 for attendu in attendus)
