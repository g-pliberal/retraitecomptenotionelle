"""L'outre-mer dans la carrière : le département où l'assuré a travaillé.

R. 753-21 et R. 351-9 (action 138, étape 6) donnent aux années travaillées en
Guadeloupe, en Guyane, en Martinique et à La Réunion leur seuil d'un trimestre
(``test_outre_mer_le_trimestre_se_valide_au_seuil_du_departement``, dans
``tests/test_salaire_annuel_moyen.py``). La période d'activité de la
chronologie porte le département (``outre_mer``), comme la ligne du relevé
(``LigneRelevee.outre_mer``) ; l'année de carrière le garde, et ses trimestres
se valident à son seuil. Depuis 1972, R. 351-9 retient le SMIC du département
pour l'assuré qui y a exercé son activité « au cours de tout ou partie d'une
année » : l'année d'un départ pour la métropole garde le département.

Les seuils viennent du Journal officiel : la semaine de 40 heures à 593,36 F
aux Antilles et en Guyane et à 553,64 F à La Réunion au 1er janvier 1982
(arrêté du 30 décembre 1981), soit 2 966,80 F et 2 768,20 F pour 200 heures,
contre 3 630 F en métropole (200 fois 18,15 F) ; en 1985, 4 062,51 F et
3 790,61 F au barème de la Cnav, contre 4 872 F.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from retraite_notionnelle import chronologie as chrono
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import (
    AnneeCarriere,
    Carriere,
    LigneRelevee,
    Metier,
    prolonger_releve,
)
from retraite_notionnelle.droit import liquider
from retraite_notionnelle.droit.preparer import preparer
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
STATUT = "salarie_prive_non_cadre"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


def _euros(francs: float) -> float:
    return francs / 6.55957


def _releve(simulateur, departement: str) -> list[LigneRelevee]:
    """Deux années déclarées sans leurs trimestres, puis la dernière prolongée
    jusqu'au départ, comme la saisie le fait d'un relevé (``contexte.py``)."""
    declare = [LigneRelevee(1981, STATUT, _euros(30_000.0), outre_mer=departement),
               LigneRelevee(1982, STATUT, _euros(2_900.0), outre_mer=departement)]
    return prolonger_releve(declare, DateMois(1986, 1), simulateur.macro)


def _trimestres(carriere: Carriere) -> dict[int, int]:
    return {ligne.annee: ligne.trimestres_valides for ligne in carriere.lignes}


def test_le_releve_le_porte_et_ses_trimestres_suivent_le_seuil(simulateur):
    """2 900 F en 1982 valident un trimestre à La Réunion, aucun aux Antilles,
    en Guyane ni en métropole ; la dernière année prolongée garde son
    département, comme son statut."""
    trimestres = {}
    for departement in ("reunion", "martinique", ""):
        releve = _releve(simulateur, departement)
        assert [ligne.annee for ligne in releve] == [1981, 1982, 1983, 1984, 1985]
        assert {ligne.outre_mer for ligne in releve} == {departement}
        carriere = simulateur.carriere_releve(1925, "F", releve, 61.0)
        assert {ligne.outre_mer for ligne in carriere.lignes} == {departement}
        trimestres[departement] = _trimestres(carriere)
    assert trimestres["reunion"][1982] == 1
    assert trimestres["martinique"][1982] == 0
    assert trimestres[""][1982] == 0
    assert trimestres["reunion"][1981] == trimestres[""][1981] == 4


def test_un_departement_inconnu_est_refuse(simulateur):
    """Mayotte n'est pas un département de L. 751-1 : sa caisse a son régime,
    que la carrière déclare par son statut (``salarie_mayotte``)."""
    with pytest.raises(ValueError, match="département d'outre-mer inconnu"):
        simulateur.carriere_releve(
            1925, "F", [LigneRelevee(1982, STATUT, _euros(2_900.0), outre_mer="mayotte")],
            58.0)


def _chronologie_du_parcours(metiers: list[tuple[Metier, str]], annee_naissance: int,
                             age_liquidation: float) -> dict:
    """La chronologie d'un parcours dont chaque métier dit son département."""
    chronologie = chrono.du_parcours(annee_naissance, "F", [m for m, _ in metiers],
                                     age_liquidation)
    emplois = [fait for fait in chronologie["faits"] if fait["sorte"] == chrono.EMPLOI]
    for fait, (_, departement) in zip(emplois, metiers):
        if departement:
            fait["attributs"]["outre_mer"] = departement
    return preparer(chronologie)


def test_le_parcours_le_porte_et_l_annee_d_un_depart_le_garde_depuis_1972(simulateur):
    """Un parcours à La Réunion puis en métropole, au vingtième du salaire moyen :
    3 083 F environ en 1982, entre le seuil de La Réunion et celui de la
    métropole. L'année 1982, trois mois à La Réunion et neuf en métropole,
    prend le seuil de La Réunion (R. 351-9, « tout ou partie » de l'année) ; en
    1950, où R. 351-9 ne dit pas cela, l'année suit le métier qui en occupe le
    plus de mois, comme son statut."""
    macro = simulateur.macro
    reunion = Metier(affiliation=STATUT, age_debut=20.0, niveau_salaire=0.045)
    metropole = Metier(affiliation=STATUT, age_debut=27.25, niveau_salaire=0.045)
    carriere = Carriere.depuis_chronologie(
        _chronologie_du_parcours([(reunion, "reunion"), (metropole, "")], 1955, 62.0), macro)
    lignes = {ligne.annee: ligne for ligne in carriere.lignes}
    assert lignes[1981].outre_mer == "reunion"
    assert lignes[1982].outre_mer == "reunion"
    assert lignes[1983].outre_mer == ""
    assert _euros(2_768.20) <= lignes[1982].revenu < _euros(3_630.0)
    assert lignes[1982].trimestres_valides == 1
    seule = Carriere.depuis_chronologie(
        _chronologie_du_parcours([(reunion, ""), (metropole, "")], 1955, 62.0), macro)
    assert {ligne.annee: ligne.trimestres_valides for ligne in seule.lignes}[1982] == 0

    avant = Carriere.depuis_chronologie(_chronologie_du_parcours(
        [(Metier(affiliation=STATUT, age_debut=20.0), "martinique"),
         (Metier(affiliation=STATUT, age_debut=20.25), "")], 1930, 62.0), macro)
    assert {ligne.annee: ligne.outre_mer for ligne in avant.lignes}[1950] == ""


def test_l_annee_validante_du_salaire_annuel_moyen_suit_le_seuil(simulateur):
    """Depuis 2004, une année sans trimestre ne compte plus dans le salaire
    annuel moyen ; R. 351-9 la dit valide quand ses salaires, toutes activités
    réunies, atteignent le seuil d'un trimestre. Deux activités de 320 € en
    1985, 640 € à elles deux, n'atteignent pas les 4 872 F de la métropole
    (742,73 €), mais passent les 4 062,51 F des Antilles (619,33 €) : l'année
    compte en Martinique."""
    actuel = simulateur.scenario_actuel
    macro = simulateur.macro
    code = "regime_general"

    def carriere(departement: str) -> Carriere:
        lignes = [AnneeCarriere(annee=annee, revenu=30_000.0, affiliation=STATUT,
                                trimestres_valides=4) for annee in range(1986, 2002)]
        lignes += [AnneeCarriere(annee=1985, revenu=320.0, affiliation=statut,
                                 trimestres_valides=0, outre_mer=departement)
                   for statut in (STATUT, "salarie_prive_cadre")]
        return Carriere.depuis_lignes(1950, "H", lignes, age_liquidation=62)

    periode = simulateur.catalogue[code].periode(2012)

    def revalorise(annee: int, revenu: float, mois: int) -> float:
        return (min(revenu, macro.plafond_securite_sociale(annee))
                * macro.coefficient_revalorisation_portee_au_compte(annee, 2012, mois))

    metropole = carriere("")
    bonnes = [revalorise(annee, 30_000.0, metropole.mois_liquidation)
              for annee in range(1986, 2002)]
    sam = liquider.salaire_de_reference(actuel, code, metropole, periode, 2012, True, 1950)
    assert sam == pytest.approx(sum(bonnes) / len(bonnes))
    martinique = carriere("martinique")
    sam = liquider.salaire_de_reference(actuel, code, martinique, periode, 2012, True, 1950)
    assert sam == pytest.approx(
        (sum(bonnes) + revalorise(1985, 640.0, martinique.mois_liquidation)) / 17)


#: Le jumeau JavaScript : les mêmes carrières, du relevé et du parcours.
_JUMEAU = """
import { readFileSync } from "node:fs";
import { Carriere } from "./moteur/js/carriere.js";
import { DonneesMacro } from "./moteur/js/macro.js";
import { Simulateur } from "./moteur/js/simulateur.js";
const { releves, chronologies } = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("./moteur/donnees.json", "utf8"));
const simulateur = new Simulateur(paquet);
const lignes = (carriere) => carriere.lignes.map((l) =>
  [l.annee, l.trimestres_valides, l.outre_mer, l.revenu]);
const duReleve = releves.map((releve) => lignes(simulateur.carriereReleve({
  annee_naissance: 1925, sexe: "F", releve, age_liquidation: 61,
})));
const duParcours = chronologies.map((chronologie) =>
  lignes(Carriere.depuisChronologie(chronologie, new DonneesMacro(paquet))));
process.stdout.write(JSON.stringify({ duReleve, duParcours }));
"""


def test_le_portage_javascript_rend_les_memes_carrieres(simulateur):
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    macro = simulateur.macro
    releves = [_releve(simulateur, departement)
               for departement in ("reunion", "martinique", "guyane", "")]
    reunion = Metier(affiliation=STATUT, age_debut=20.0, niveau_salaire=0.045)
    metropole = Metier(affiliation=STATUT, age_debut=27.25, niveau_salaire=0.045)
    chronologies = [
        _chronologie_du_parcours([(reunion, "reunion"), (metropole, "")], 1955, 62.0),
        _chronologie_du_parcours([(reunion, "guadeloupe"), (metropole, "martinique")],
                                 1955, 62.0),
        _chronologie_du_parcours([(Metier(affiliation=STATUT, age_debut=20.0), "martinique"),
                                  (Metier(affiliation=STATUT, age_debut=20.25), "")],
                                 1930, 62.0),
    ]

    def lignes(carriere: Carriere) -> list:
        return [[l.annee, l.trimestres_valides, l.outre_mer, l.revenu]
                for l in carriere.lignes]

    attendu_releves = [lignes(simulateur.carriere_releve(1925, "F", releve, 61.0))
                       for releve in releves]
    attendu_parcours = [lignes(Carriere.depuis_chronologie(chronologie, macro))
                        for chronologie in chronologies]
    entree = {
        "releves": [[{"annee": l.annee, "affiliation": l.affiliation, "revenu": l.revenu,
                      "outre_mer": l.outre_mer} for l in releve] for releve in releves],
        "chronologies": chronologies,
    }
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU, json.dumps(entree)],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    obtenu = json.loads(execution.stdout)
    for rendues, attendues in ((obtenu["duReleve"], attendu_releves),
                               (obtenu["duParcours"], attendu_parcours)):
        assert len(rendues) == len(attendues)
        for rendue, attendue in zip(rendues, attendues):
            assert [l[:3] for l in rendue] == [l[:3] for l in attendue]
            assert [l[3] for l in rendue] == pytest.approx([l[3] for l in attendue],
                                                           abs=1e-6)
