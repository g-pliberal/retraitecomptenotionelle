"""Les dispenses de l'assiette minimale, saisies (fiche
``assiette_minimale_independants`` ; action 138, étape 18).

L'artisan, le commerçant ou le libéral que L. 613-11 ou D. 642-4 dispense de
l'assiette minimale (``legislation/dispenses_assiette_minimale.yaml``) le dit
par années entières, « 2016:2019:rsa », comme le temps partiel ; la saisie le
lit et refuse ce qui est mal dit ; le relevé et les métiers le portent sur les
lignes des années qu'il nomme — la chronologie coupe les métiers au
1er janvier où il change —, et la règle ne le retient que là où le texte
dispense le statut.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from urllib.parse import parse_qs

import pytest

from retraite_notionnelle import chronologie as chrono
from retraite_notionnelle.web.site import ErreurSite, module

from outils_pont import RefusDuPortage, Saisies, saisie_du_portage

RACINE = Path(__file__).resolve().parents[1]

#: Née le 15 mars 1962, partie le 1er avril 2027 : les dates sont dites
#: entières, aucune présomption ne les déplace.
NEE_EN_1962 = {"naissance": "1962-03-15", "liquidation": "2027-04-01"}

#: Trois années d'artisane à 3 000 €, la dernière prolongée jusqu'au départ.
RELEVE = "2019:artisan:3000\n2020:artisan:3000\n2021:artisan:3000"

#: Une salariée, artisane à son compte de juillet 2014 au départ, commerçante
#: en plus de 2019 à 2022.
PARCOURS = {
    **NEE_EN_1962, "debut": "1990-01-01", "statut": "salarie_prive_non_cadre",
    "unite_revenu": "euros_mois", "salaire": "1500",
    "metier2_debut": "2014-07-01", "metier2_statut": "artisan", "metier2_salaire": "400",
    "metier3_debut": "2019-01-01", "metier3_statut": "commercant", "metier3_salaire": "400",
    "metier3_cumul": "oui", "metier3_fin": "2023-01-01",
}


@pytest.fixture(scope="module")
def saisies() -> Saisies:
    return Saisies()


def _saisie(**champs):
    """La saisie du portage, de ses champs."""
    return module("saisie").Saisie(champs)


# -- la saisie ----------------------------------------------------------------------

def test_la_saisie_lit_les_annees_et_leur_motif():
    saisie = _saisie(dispenses="2016:2018:rsa,\n 2020:2020: activite_saisonniere")
    assert saisie.dispenses_analysees() == {
        2016: "rsa", 2017: "rsa", 2018: "rsa", 2020: "activite_saisonniere"}
    assert _saisie().dispenses_analysees() == {}


#: Chaque faute, et la phrase qui la refuse, la même dans les deux moteurs.
REFUS = {
    "2016-2018:rsa": "Dispense mal formée : « 2016-2018:rsa ». Attendu "
                     "« année_début:année_fin:motif », par exemple 2016:2019:rsa.",
    "2016:2018:": "Dispense mal formée : « 2016:2018: ». Attendu "
                  "« année_début:année_fin:motif », par exemple 2016:2019:rsa.",
    "1700:1710:rsa": "Dispense « 1700:1710:rsa » : 1700 ne tombe dans aucune carrière "
                     "possible. Attendu entre",
    "2018:2016:rsa": "Dispense « 2018:2016:rsa » : elle finit (2016) avant de "
                     "commencer (2018).",
    "2016:2020:rsa, 2019:2021:prime_activite": "Dispense « 2019:2021:prime_activite » : "
                                               "l'année 2019 a déjà son motif.",
}

#: Le motif inconnu, que refuse qui connaît la table : la saisie ne connaît pas
#: les données, le contexte les lui donne. Les motifs sont ceux de la table.
INCONNU = ("2016:2018:rsx",
           "Dispense « 2016:2018:rsx » : motif inconnu « rsx ». Attendu l'un de : "
           "activite_non_principale, activite_saisonniere, pensionne, prime_activite, rsa.")


@pytest.mark.parametrize("texte", list(REFUS))
def test_une_dispense_mal_dite_est_refusee(texte):
    """Se tromper de touche ne donne pas un autre chiffre, mais un refus — et
    la saisie le prononce avant tout calcul (``verifier``)."""
    with pytest.raises(ErreurSite, match="ErreurSaisie : " + re.escape(REFUS[texte])):
        _saisie(dispenses=texte).verifier()


def test_le_motif_n_est_controle_que_par_qui_connait_la_table(saisies):
    texte, phrase = INCONNU
    assert _saisie(dispenses=texte).dispenses_analysees() == {
        2016: "rsx", 2017: "rsx", 2018: "rsx"}
    with pytest.raises(RefusDuPortage) as refus:
        saisies.carriere({**PARCOURS, "dispenses": texte})
    assert str(refus.value) == phrase
    with pytest.raises(RefusDuPortage) as refus:
        saisies.carriere({**NEE_EN_1962, "releve": RELEVE, "dispenses": texte})
    assert str(refus.value) == phrase


def test_l_adresse_porte_les_dispenses_qu_on_a_dites():
    """L'adresse réécrite garde le champ, et ne l'écrit pas quand il est vide."""
    saisie = saisie_du_portage({"dispenses": " 2016:2019:rsa "})
    lu = parse_qs(saisie.requete())
    assert lu["dispenses"] == ["2016:2019:rsa"]
    assert saisie_du_portage({k: v[0] for k, v in lu.items()}).dispenses == "2016:2019:rsa"
    assert "dispenses" not in parse_qs(saisie_du_portage({}).requete())


# -- le relevé ----------------------------------------------------------------------

def _dispenses_des_lignes(carriere) -> list[tuple[int, str, str]]:
    return [(ligne.annee, ligne.affiliation, ligne.dispense_assiette_minimale)
            for ligne in carriere.lignes]


def test_le_releve_porte_la_dispense_des_annees_qu_elle_nomme(saisies):
    """Chaque ligne du relevé prend le motif de son année, sauf une année
    d'interruption, qui ne cotise pas ; les années qui prolongent le relevé
    jusqu'au départ le prennent aussi. La règle ne le retient que depuis 2016
    pour le RSA (L. 131-6-3, rétabli pour les périodes courant à compter du
    1er janvier 2016)."""
    requete = {**NEE_EN_1962, "releve": "2015:artisan:3000\n" + RELEVE,
               "interruptions": "2019:2019:chomage_indemnise", "dispenses": "2015:2023:rsa"}
    assert [(ligne.annee, ligne.dispense_assiette_minimale)
            for ligne in saisie_du_portage(requete).releve_analyse()] == [
        (2015, "rsa"), (2019, ""), (2020, "rsa"), (2021, "rsa")]
    assert _dispenses_des_lignes(saisies.carriere(requete)) == [
        (2015, "artisan", ""), (2019, "artisan", ""), (2020, "artisan", "rsa"),
        (2021, "artisan", "rsa"), (2022, "artisan", "rsa"), (2023, "artisan", "rsa"),
        (2024, "artisan", ""), (2025, "artisan", ""), (2026, "artisan", ""),
        (2027, "artisan", "")]


def test_l_annee_dispensee_ne_valide_que_ce_que_son_revenu_valide(saisies):
    """L'artisane au RSA qui déclare 3 000 € en 2020 cotise sur eux seuls : un
    trimestre, 150 heures de SMIC à 10,15 € en valant 1 522,50 € (R. 351-9),
    au lieu des trois que lui valide l'assiette minimale, 11,5 % du plafond de
    41 136 €, soit 4 730,64 € (D. 633-2)."""
    sans = saisies.carriere({**NEE_EN_1962, "releve": RELEVE})
    avec = saisies.carriere({**NEE_EN_1962, "releve": RELEVE, "dispenses": "2020:2020:rsa"})
    trimestres = {ligne.annee: ligne.trimestres_valides for ligne in avec.lignes}
    assert {ligne.annee: ligne.trimestres_valides for ligne in sans.lignes}[2020] == 3
    assert trimestres[2020] == 1
    assert trimestres[2019] == trimestres[2021] == 3


# -- les métiers --------------------------------------------------------------------

def test_les_metiers_se_coupent_aux_annees_des_dispenses(saisies):
    """Un métier, principal ou ajouté, se coupe au 1er janvier où le motif
    change, et chaque morceau porte le sien ; la chronologie tient toujours.
    Sans dispense, rien n'est coupé."""
    carriere = saisies.carriere(
        {**PARCOURS, "dispenses": "2015:2017:rsa, 2021:2021:activite_saisonniere"})
    faits = [(f["id"], f["debut"], f["fin"], f["attributs"].get("dispense_assiette_minimale"))
             for f in chrono.faits_de(carriere.chronologie, chrono.ASSURE, chrono.EMPLOI)]
    assert faits == [
        ("emploi_1", "1990-01-01", "2014-07-01", None),
        ("emploi_2", "2014-07-01", "2015-01-01", None),
        ("emploi_2_2", "2015-01-01", "2018-01-01", "rsa"),
        ("emploi_2_3", "2018-01-01", "2021-01-01", None),
        ("emploi_2_4", "2021-01-01", "2022-01-01", "activite_saisonniere"),
        ("emploi_2_5", "2022-01-01", "2027-04-01", None),
        ("cumul_1", "2019-01-01", "2021-01-01", None),
        ("cumul_1_2", "2021-01-01", "2022-01-01", "activite_saisonniere"),
        ("cumul_1_3", "2022-01-01", "2023-01-01", None),
    ]
    assert chrono.controler(carriere.chronologie) == []
    sans = saisies.carriere(PARCOURS)
    assert [f["id"] for f in chrono.faits_de(sans.chronologie, chrono.ASSURE, chrono.EMPLOI)] == [
        "emploi_1", "emploi_2", "cumul_1"]


def test_les_lignes_des_metiers_portent_ce_que_la_regle_retient(saisies):
    """Le RSA ne dispense qu'à compter de 2016, et l'activité saisonnière
    qu'à compter de 2020 ; le salarié, jamais. Couper les métiers ne change
    ni les revenus ni les trimestres des années sans dispense."""
    carriere = saisies.carriere(
        {**PARCOURS, "dispenses": "2015:2017:rsa, 2021:2021:activite_saisonniere"})
    retenues = {(annee, affiliation): motif
                for annee, affiliation, motif in _dispenses_des_lignes(carriere) if motif}
    assert retenues == {(2016, "artisan"): "rsa", (2017, "artisan"): "rsa",
                        (2021, "artisan"): "activite_saisonniere",
                        (2021, "commercant"): "activite_saisonniere"}
    sans = saisies.carriere(PARCOURS)
    dispensees = {annee for annee, _ in retenues}
    assert ([(l.annee, l.affiliation, l.revenu, l.trimestres_valides)
             for l in carriere.lignes if l.annee not in dispensees]
            == [(l.annee, l.affiliation, l.revenu, l.trimestres_valides)
                for l in sans.lignes if l.annee not in dispensees])


# -- le portage ---------------------------------------------------------------------

LECTURE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { Saisie } from "./moteur/js/saisie.js";

const contexte = new Contexte(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));
const sortie = JSON.parse(readFileSync(0, "utf8")).map((requete) => {
  let saisie;
  let carriere;
  try {
    saisie = Saisie.depuisRequete(requete, false, contexte.paquet.presomptions);
    carriere = contexte.carriere(saisie);
  } catch (erreur) {
    return { refus: erreur.message };
  }
  return {
    requete: saisie.requete(),
    dispenses: Object.fromEntries(saisie.dispensesAnalysees()),
    faits: carriere.chronologie.faits.filter((f) => f.sorte === "periode_d_activite")
      .map((f) => [f.id, f.debut, f.fin, f.attributs.dispense_assiette_minimale ?? null]),
    lignes: carriere.lignes.map((l) => [l.annee, l.affiliation,
      l.dispense_assiette_minimale, l.trimestres_valides]),
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def test_le_portage_lit_les_dispenses():
    """La saisie du portage refuse par sa phrase, et lit les motifs ; sa
    chronologie coupe les métiers, et sa carrière retient les dispenses,
    parcours et relevé. Sa jumelle Python, à qui elle se confrontait ici, ne
    l'est plus que par les témoins (``tests/test_pont.py``), jusqu'à son
    retrait (action 161, étape 6)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    requetes = [{**PARCOURS, "dispenses": texte} for texte in [*REFUS, INCONNU[0]]]
    requetes += [
        {**PARCOURS, "dispenses": "2015:2017:rsa, 2021:2021:activite_saisonniere"},
        {**NEE_EN_1962, "releve": "2015:artisan:3000\n" + RELEVE,
         "interruptions": "2019:2019:chomage_indemnise",
         "dispenses": "2015:2023:prime_activite"},
        {**NEE_EN_1962, "releve": "2010:auxiliaire_medical:3000\n"
                                  "2011:auxiliaire_medical:3000",
         "dispenses": "2010:2010:pensionne, 2011:2011:activite_non_principale"},
    ]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", LECTURE_JS], cwd=RACINE,
        input=json.dumps(requetes), capture_output=True, text=True, encoding="utf-8",
        check=False)
    assert execution.returncode == 0, execution.stderr
    lus = json.loads(execution.stdout)
    assert [lu["refus"][:40] for lu in lus[:len(REFUS) + 1]] == [
        r[:40] for r in [*REFUS.values(), INCONNU[1]]]
    # L'infirmière libérale d'avant 2016 : D. 642-4 la dispense, pensionnée
    # ou d'activité non principale.
    assert [ligne[:3] for ligne in lus[-1]["lignes"][:2]] == [
        [2010, "auxiliaire_medical", "pensionne"],
        [2011, "auxiliaire_medical", "activite_non_principale"]]
