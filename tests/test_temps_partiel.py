"""Le temps partiel des fonctionnaires (fiche ``temps_partiel_fonction_publique``).

Le temps partiel compte en entier pour ouvrir le droit et dans la durée
d'assurance, et à sa quotité dans les services que la pension liquide (L. 5,
L. 14, I, et L. 11, 1°, du code des pensions ; article 13 du décret
n° 2003-1306 pour la CNRACL). Le formulaire le déclare par années entières,
« 2000:2009:80 » ; la chronologie porte la quotité sur les périodes
d'activité, coupées au 1er janvier ; la carrière en réduit le revenu d'un
parcours, garde celui d'un relevé, et les services la comptent.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import parse_qs

import pytest

from retraite_notionnelle import chronologie as chrono
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import (
    Carriere, LigneRelevee, Metier, prolonger_releve, salaire_moyen_annuel,
)
from retraite_notionnelle.droit import releve
from retraite_notionnelle.saisie import ErreurSaisie, Saisie
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]

#: Les dix années à 80 % de l'exemple du SRE, que la page ne date pas.
DIX_ANS_A_80 = {annee: 0.8 for annee in range(2000, 2010)}


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _pierre(simulateur: Simulateur, temps_partiel: dict[int, float] | None = None) -> Carriere:
    """Le fonctionnaire de l'État de l'exemple du SRE (`sre_temps_partiel_pierre`) :
    né le 10 avril 1958, trente-neuf ans de services, de mai 1986 à avril 2025 ;
    sa pension prend effet le 1er mai, et ses âges se comptent de ce mois-là."""
    return simulateur.carriere_simple(
        annee_naissance=1958, sexe="H", affiliation="fonctionnaire_etat",
        age_debut=28 + 1 / 12, age_liquidation=67.0, mois_naissance=4,
        jour_naissance=10, temps_partiel=temps_partiel)


def _services(simulateur: Simulateur, carriere: Carriere) -> int:
    durees = releve.construire(simulateur.scenario_actuel, carriere).durees
    return durees.services_liquidables(("fonction_publique_etat",))


def _pension_de_l_etat(simulateur: Simulateur, carriere: Carriere):
    [etat] = [p for p in simulateur.scenario_actuel.calculer(carriere).pensions_par_regime
              if p.regime == "fonction_publique_etat"]
    return etat


# -- la saisie ----------------------------------------------------------------------

def test_la_saisie_lit_les_annees_et_leur_quotite():
    saisie = Saisie(temps_partiel="2005:2007:80,\n 2010:2010:50")
    assert saisie.temps_partiel_analyse() == {2005: 0.8, 2006: 0.8, 2007: 0.8, 2010: 0.5}
    assert Saisie().temps_partiel_analyse() == {}


#: Chaque faute, et la phrase qui la refuse, la même dans les deux moteurs.
REFUS = {
    "2005-2007:80": "Temps partiel mal formé : « 2005-2007:80 ». Attendu "
                    "« année_début:année_fin:quotité », par exemple 2005:2014:80.",
    "2005:2007:80 %": "Temps partiel mal formé : « 2005:2007:80 % ». Attendu "
                      "« année_début:année_fin:quotité », par exemple 2005:2014:80.",
    "1700:1710:80": "Temps partiel « 1700:1710:80 » : 1700 ne tombe dans aucune carrière "
                    "possible. Attendu entre",
    "2007:2005:80": "Temps partiel « 2007:2005:80 » : il finit (2005) avant de commencer "
                    "(2007).",
    "2005:2007:0": "Temps partiel « 2005:2007:0 » : quotité attendue entre 1 et 99 %, le "
                   "temps plein n'ayant rien à déclarer.",
    "2005:2007:100": "Temps partiel « 2005:2007:100 » : quotité attendue entre 1 et 99 %, "
                     "le temps plein n'ayant rien à déclarer.",
    "2005:2010:80, 2008:2012:50": "Temps partiel « 2008:2012:50 » : l'année 2008 a déjà "
                                  "sa quotité.",
}


@pytest.mark.parametrize("texte", list(REFUS))
def test_un_temps_partiel_mal_dit_est_refuse(texte):
    """Se tromper de touche ne donne pas un autre chiffre, mais un refus — et
    la saisie le prononce avant tout calcul (``verifier``)."""
    with pytest.raises(ErreurSaisie) as refus:
        Saisie(temps_partiel=texte).verifier()
    assert str(refus.value).startswith(REFUS[texte])


def test_l_adresse_porte_le_temps_partiel_qu_on_a_dit():
    """L'adresse réécrite garde le champ, et ne l'écrit pas quand il est vide."""
    saisie = Saisie.depuis_requete({"temps_partiel": " 2005:2007:80 "})
    lu = parse_qs(saisie.requete())
    assert lu["temps_partiel"] == ["2005:2007:80"]
    assert Saisie.depuis_requete({k: v[0] for k, v in lu.items()}).temps_partiel == "2005:2007:80"
    assert "temps_partiel" not in parse_qs(Saisie.depuis_requete({}).requete())


LECTURE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { Saisie } from "./moteur/js/saisie.js";

const contexte = new Contexte(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));
const sortie = JSON.parse(readFileSync(0, "utf8")).map((requete) => {
  let saisie;
  try {
    saisie = Saisie.depuisRequete(requete, false, contexte.paquet.presomptions);
  } catch (erreur) {
    return { refus: erreur.message };
  }
  const carriere = contexte.carriere(saisie);
  return {
    requete: saisie.requete(),
    quotites: Object.fromEntries(saisie.tempsPartielAnalyse()),
    faits: carriere.chronologie.faits.filter((f) => f.sorte === "periode_d_activite")
      .map((f) => [f.id, f.debut, f.fin, f.attributs.quotite ?? null]),
    lignes: carriere.lignes.map((l) => [l.annee, l.quotite]),
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def _lu_par_python(requete: dict) -> dict:
    from retraite_notionnelle.contexte import Contexte

    try:
        saisie = Saisie.depuis_requete(requete)
    except ErreurSaisie as refus:
        return {"refus": str(refus)}
    carriere = Contexte().carriere(saisie)
    return {
        "requete": saisie.requete(),
        "quotites": {str(annee): quotite
                     for annee, quotite in saisie.temps_partiel_analyse().items()},
        "faits": [[f["id"], f["debut"], f["fin"], f["attributs"].get("quotite")]
                  for f in chrono.faits_de(carriere.chronologie, chrono.ASSURE, chrono.EMPLOI)],
        "lignes": [[ligne.annee, ligne.quotite] for ligne in carriere.lignes],
    }


def test_le_portage_lit_le_meme_temps_partiel():
    """Les deux saisies refusent par la même phrase, et lisent les mêmes
    quotités ; les deux chronologies coupent les mêmes périodes, et les deux
    carrières portent les mêmes quotités, parcours et relevé."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    base = {"naissance": "1966", "debut": "22", "liquidation": "64",
            "statut": "fonctionnaire_territorial_hospitalier"}
    requetes = [{**base, "temps_partiel": texte} for texte in REFUS]
    requetes += [
        {**base, "temps_partiel": "2000:2003:50, 2004:2006:80",
         "metier2_debut": "2005-07", "metier2_statut": "fonctionnaire_etat"},
        {**base, "temps_partiel": "2022:2024:70, 2027:2027:90",
         "releve": "2023:fonctionnaire_territorial_hospitalier:16700:4\n"
                   "2024:fonctionnaire_territorial_hospitalier:17200:4"},
    ]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", LECTURE_JS], cwd=RACINE,
        input=json.dumps(requetes), capture_output=True, text=True, encoding="utf-8",
        check=False)
    assert execution.returncode == 0, execution.stderr
    attendus = [_lu_par_python(requete) for requete in requetes]
    assert json.loads(execution.stdout) == attendus
    assert [a["refus"][:40] for a in attendus[:len(REFUS)]] == [r[:40] for r in REFUS.values()]
    # Le second métier commence en juillet 2005, au milieu des années à 80 % :
    # ses deux morceaux et ceux du premier portent la quotité de leurs années.
    assert attendus[-2]["faits"] == [
        ["emploi_1", "1988-01-01", "2000-01-01", None],
        ["emploi_1_2", "2000-01-01", "2004-01-01", 0.5],
        ["emploi_1_3", "2004-01-01", "2005-07-01", 0.8],
        ["emploi_2", "2005-07-01", "2007-01-01", 0.8],
        ["emploi_2_2", "2007-01-01", "2030-02-01", None],
    ]


# -- la chronologie et la carrière ---------------------------------------------------

def test_la_chronologie_coupe_l_activite_aux_annees_du_temps_partiel(simulateur):
    """Une période d'activité a une quotité, ou n'en a pas (le temps plein) :
    le métier se coupe au 1er janvier où elle change, et la chronologie tient
    toujours. Sans temps partiel, rien n'est coupé."""
    carriere = _pierre(simulateur, DIX_ANS_A_80)
    faits = [(f["id"], f["debut"], f["fin"], f["attributs"].get("quotite"))
             for f in chrono.faits_de(carriere.chronologie, chrono.ASSURE, chrono.EMPLOI)]
    assert faits == [("emploi_1", "1986-05-01", "2000-01-01", None),
                     ("emploi_1_2", "2000-01-01", "2010-01-01", 0.8),
                     ("emploi_1_3", "2010-01-01", "2025-05-01", None)]
    assert chrono.controler(carriere.chronologie) == []
    plein = _pierre(simulateur)
    assert [f["id"] for f in chrono.faits_de(plein.chronologie, chrono.ASSURE,
                                            chrono.EMPLOI)] == ["emploi_1"]
    # Le revenu d'un parcours est celui du temps plein, réduit à la quotité.
    revenus = {ligne.annee: ligne.revenu for ligne in plein.lignes}
    for ligne in carriere.lignes:
        assert ligne.quotite == DIX_ANS_A_80.get(ligne.annee, 1.0)
        assert ligne.revenu == pytest.approx(revenus[ligne.annee] * ligne.quotite)


def test_l_interruption_l_emporte_et_le_cumul_garde_le_temps_plein(simulateur):
    """Une année d'interruption n'a pas de quotité : l'interruption la prend
    tout entière. Une activité cumulée garde son revenu et le temps plein : le
    temps partiel est celui de l'activité principale."""
    carriere = Carriere.depuis_parcours(
        annee_naissance=1970, sexe="F", age_liquidation=64, macro=simulateur.macro,
        metiers=[Metier("fonctionnaire_territorial_hospitalier", 22.0),
                 Metier("profession_liberale", 40.0, 0.5, cumul=True, age_fin=45.0)],
        interruptions={2012: "education_enfant"},
        temps_partiel={annee: 0.6 for annee in range(2010, 2014)})
    vues = 0
    for ligne in carriere.lignes:
        if ligne.affiliation == "profession_liberale":
            assert ligne.quotite == 1.0
        elif ligne.annee == 2012:
            assert (ligne.type_periode, ligne.quotite) == ("education_enfant", 1.0)
        else:
            assert ligne.quotite == (0.6 if 2010 <= ligne.annee <= 2013 else 1.0)
            vues += 2010 <= ligne.annee <= 2013
    assert vues == 3


def test_la_retraite_progressive_prend_la_suite_du_temps_partiel(simulateur):
    """Les mois de retraite progressive ont sa quotité, les autres celle du
    temps partiel déclaré : l'année où elle commence en fait la moyenne. Née
    un 1er, l'assurée a ses soixante ans et dix mois le 1er novembre 2025, où
    sa retraite progressive prend effet."""
    carriere = Carriere.depuis_parcours(
        annee_naissance=1965, sexe="F", age_liquidation=64, macro=simulateur.macro,
        jour_naissance=1, metiers=[Metier("salarie_prive_non_cadre", 20.0)],
        temps_partiel={annee: 0.5 for annee in range(2020, 2027)},
        retraite_progressive={"age": 60 + 10 / 12, "quotite": 0.6})
    quotites = {ligne.annee: ligne.quotite for ligne in carriere.lignes}
    assert quotites[2019] == 1.0 and quotites[2024] == 0.5
    assert quotites[2025] == pytest.approx((10 * 0.5 + 2 * 0.6) / 12)
    assert quotites[2026] == quotites[2027] == 0.6


def test_le_releve_prolonge_reprend_le_temps_plein_puis_la_quotite_declaree(simulateur):
    """Un relevé porte le revenu perçu, déjà réduit : prolongé jusqu'au départ,
    sa dernière année se ramène au temps plein par sa quotité, et chaque année
    ajoutée prend celle que le champ lui donne."""
    lignes = prolonger_releve(
        [LigneRelevee(2024, "fonctionnaire_etat", 16000.0, 4, quotite=0.8)],
        DateMois(2028, 1), simulateur.macro, temps_partiel={2026: 0.5})
    par_annee = {ligne.annee: ligne for ligne in lignes}
    assert sorted(par_annee) == [2024, 2025, 2026, 2027]

    def plein(annee: int) -> float:
        return 20000.0 * (salaire_moyen_annuel(simulateur.macro, annee)
                          / salaire_moyen_annuel(simulateur.macro, 2024))

    assert (par_annee[2025].revenu, par_annee[2025].quotite) == (pytest.approx(plein(2025)), 1.0)
    assert (par_annee[2026].revenu, par_annee[2026].quotite) == (pytest.approx(plein(2026) / 2),
                                                                 0.5)
    assert par_annee[2027].quotite == 1.0


# -- les services et la pension ----------------------------------------------------------

def test_les_services_comptent_la_quotite_et_la_duree_d_assurance_non(simulateur):
    """L'exemple du SRE : trente-neuf ans dont dix à 80 % font 148 trimestres
    de services au lieu de 156 (L. 11, 1°), sans rien ôter à la durée
    d'assurance (L. 14, I) ni à la durée de services qui ouvre les droits
    (L. 5) ; la pension, sans décote à la limite d'âge, baisse d'autant."""
    moteur = simulateur.scenario_actuel
    plein, partiel = _pierre(simulateur), _pierre(simulateur, DIX_ANS_A_80)
    assert (_services(simulateur, plein), _services(simulateur, partiel)) == (156, 148)
    assert (moteur.calculer(partiel).trimestres_valides
            == moteur.calculer(plein).trimestres_valides)
    assert (partiel.duree_de_service(["fonctionnaire_etat"])
            == plein.duree_de_service(["fonctionnaire_etat"]))
    assert (_pension_de_l_etat(simulateur, partiel).montant
            / _pension_de_l_etat(simulateur, plein).montant) == pytest.approx(148 / 156, abs=1e-6)


def test_le_traitement_de_reference_reste_celui_du_temps_plein(simulateur):
    """À temps partiel jusqu'au départ, le fonctionnaire liquide le traitement
    du temps plein (L. 15, I) : sa pension ne perd que ses services, 149
    trimestres — sept et demi de moins, que le décompte final arrondit au
    trimestre (R. 26)."""
    plein = _pierre(simulateur)
    fin = _pierre(simulateur, {annee: 0.8 for annee in range(2016, 2026)})
    assert _services(simulateur, fin) == 149
    etat_plein, etat_fin = (_pension_de_l_etat(simulateur, plein),
                            _pension_de_l_etat(simulateur, fin))
    assert etat_fin.detail.split(" × ")[0] == etat_plein.detail.split(" × ")[0]
    assert etat_fin.montant / etat_plein.montant == pytest.approx(149 / 156, abs=1e-6)
