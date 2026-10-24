"""La Lodeom, saisie (action 138, étape 18 ; ``lodeom`` de
``legislation/prelevements_remuneration.yaml``).

En Guadeloupe, en Guyane, en Martinique et à La Réunion, l'employeur de moins
de onze salariés ou d'un secteur que L. 752-3-2, II, énumère reçoit, à la place
de la réduction générale, une exonération de ses cotisations à l'un des trois
barèmes du III : compétitivité, compétitivité renforcée, innovation et
croissance. Le salarié du privé le dit d'un menu ; la saisie le lit, l'adresse
le garde, les métiers et les lignes d'emploi du relevé le portent, et la fiche
de paie, qui seule le lit, met l'exonération à la place de la réduction
générale (``tests/test_lodeom.py`` en éprouve les barèmes).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import parse_qs

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle import chronologie as chrono
from retraite_notionnelle.remuneration import charger_prelevements
from retraite_notionnelle.web.site import module

from outils_pont import Saisies, saisie_du_portage

RACINE = Path(__file__).resolve().parents[1]

#: Né le 15 mars 1980, parti le 1er avril 2045 : les dates sont dites entières.
NE_EN_1980 = {"naissance": "1980-03-15", "liquidation": "2045-04-01"}

#: 1,5 fois 1 820 heures du SMIC du 1er janvier 2026, 12,02 € (D. 241-7) :
#: 32 814,60 €, sous les 2 SMIC où le barème de compétitivité renforcée
#: exonère tout le périmètre (L. 752-3-2, III, B).
BRUT_2026 = 1.5 * 12.02 * 1820
#: BOSS, § 1380 : T, la valeur maximale du coefficient, au 1er janvier 2026,
#: dans une entreprise de cinquante salariés et plus.
T = 0.3241

#: Deux années de relevé, la première au chômage, la dernière prolongée
#: jusqu'au départ.
RELEVE = ("2025:salarie_prive_non_cadre:32000\n"
          f"2026:salarie_prive_non_cadre:{BRUT_2026:.2f}")

#: Un salarié, cadre depuis 2020, qui donne des cours à son compte, en plus,
#: de 2022 à 2030.
PARCOURS = {
    **NE_EN_1980, "debut": "2002-09-01", "statut": "salarie_prive_non_cadre",
    "unite_revenu": "euros_mois", "salaire": "2000",
    "metier2_debut": "2020-01-01", "metier2_statut": "salarie_prive_cadre",
    "metier2_salaire": "3500",
    "metier3_debut": "2022-01-01", "metier3_statut": "profession_liberale",
    "metier3_salaire": "500", "metier3_cumul": "oui", "metier3_fin": "2031-01-01",
}


@pytest.fixture(scope="module")
def saisies() -> Saisies:
    return Saisies()


# -- la saisie ----------------------------------------------------------------------

def test_le_menu_offre_les_baremes_des_donnees():
    """Les barèmes du menu sont ceux du bloc ``lodeom`` des données, sous leur
    libellé : un barème de plus, ou renommé, ne s'y perd pas. « Non » d'abord,
    qui est le défaut."""
    profil = charger_prelevements(Parametres().racine_donnees).profil("salarie_prive")
    baremes = [tuple(choix) for choix in module("saisie").BAREMES_LODEOM]
    assert baremes[0] == ("", "non")
    assert baremes[1:] == [(code, bareme.libelle)
                           for code, bareme in profil.lodeom.baremes.items()]


def test_la_saisie_lit_le_bareme_de_l_employeur():
    """Un barème du menu se lit tel quel ; un autre mot, comme le vide, ne
    déclare rien, à la façon des autres menus."""
    assert saisie_du_portage({"lodeom": "competitivite_renforcee"}).lodeom == (
        "competitivite_renforcee")
    assert saisie_du_portage({"lodeom": "dom"}).lodeom == ""
    assert saisie_du_portage({}).lodeom == ""


def test_l_adresse_porte_la_lodeom_qu_on_a_dite():
    """L'adresse réécrite garde le barème, et ne l'écrit pas sans lui."""
    lu = parse_qs(saisie_du_portage({"lodeom": "innovation_et_croissance"}).requete())
    assert lu["lodeom"] == ["innovation_et_croissance"]
    assert saisie_du_portage({k: v[0] for k, v in lu.items()}).lodeom == (
        "innovation_et_croissance")
    assert "lodeom" not in parse_qs(saisie_du_portage({}).requete())


# -- le relevé et les métiers -------------------------------------------------------

def test_les_lignes_d_emploi_du_releve_portent_la_lodeom(saisies):
    """Chaque ligne d'emploi du relevé prend le barème, une année au chômage
    non, qui ne cotise pas ; les années qui prolongent le relevé jusqu'au départ
    le gardent."""
    requete = {**NE_EN_1980, "releve": RELEVE, "interruptions": "2025:2025:chomage_indemnise",
               "lodeom": "competitivite"}
    saisie = saisie_du_portage(requete)
    assert [(ligne.annee, ligne.lodeom) for ligne in saisie.releve_analyse()] == [
        (2025, ""), (2026, "competitivite")]
    lignes = saisies.carriere(requete).lignes
    assert [(ligne.annee, ligne.lodeom) for ligne in lignes][:3] == [
        (2025, ""), (2026, "competitivite"), (2027, "competitivite")]
    assert {ligne.lodeom for ligne in lignes if ligne.annee >= 2026} == {"competitivite"}


def test_chaque_metier_porte_la_lodeom(saisies):
    """Chaque métier, principal ou ajouté, porte le barème dans la
    chronologie, et chacune de ses années cotisées dans la carrière ; sans lui,
    aucun."""
    carriere = saisies.carriere(
        {**PARCOURS, "lodeom": "competitivite_renforcee"})
    faits = [(f["id"], f["attributs"].get("lodeom"))
             for f in chrono.faits_de(carriere.chronologie, chrono.ASSURE, chrono.EMPLOI)]
    assert faits == [("emploi_1", "competitivite_renforcee"),
                     ("emploi_2", "competitivite_renforcee"),
                     ("cumul_1", "competitivite_renforcee")]
    assert chrono.controler(carriere.chronologie) == []
    assert {ligne.lodeom for ligne in carriere.lignes} == {"competitivite_renforcee"}
    sans = saisies.carriere(PARCOURS)
    assert {f["attributs"].get("lodeom")
            for f in chrono.faits_de(sans.chronologie, chrono.ASSURE, chrono.EMPLOI)} == {None}
    assert {ligne.lodeom for ligne in sans.lignes} == {""}


def test_la_fiche_de_paie_exonere_au_bareme_saisi(saisies):
    """À 1,5 SMIC, sous les 2 SMIC du barème de compétitivité renforcée,
    l'employeur ne verse plus rien du périmètre : l'exonération vaut T fois le
    brut, au dix-millième près où le modèle refait T des fiches de régime
    (``tests/test_lodeom.py``), et la fiche dit son barème. Sans elle, c'est la
    réduction générale, moindre à ce niveau."""
    def reference(lodeom: str):
        requete = {**NE_EN_1980, "releve": RELEVE, "lodeom": lodeom}
        return saisies.simuler(requete).remuneration.reference.droit_en_vigueur
    fiche = reference("competitivite_renforcee")
    assert fiche.annee == 2026 and fiche.brut == pytest.approx(BRUT_2026)
    assert fiche.lodeom == "competitivite_renforcee"
    assert fiche.reduction_generale == pytest.approx(T * BRUT_2026, abs=1e-4 * BRUT_2026)
    generale = reference("")
    assert generale.lodeom == ""
    assert 0 < generale.reduction_generale < fiche.reduction_generale


# -- le portage ---------------------------------------------------------------------

LECTURE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { Saisie } from "./moteur/js/saisie.js";

const contexte = new Contexte(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));
const sortie = JSON.parse(readFileSync(0, "utf8")).map((requete) => {
  const saisie = Saisie.depuisRequete(requete, false, contexte.paquet.presomptions);
  const carriere = contexte.carriere(saisie);
  const fiche = contexte.simuler(saisie).remuneration.reference.droitEnVigueur;
  return {
    requete: saisie.requete(),
    lodeom: saisie.lodeom,
    faits: carriere.chronologie.faits.filter((f) => f.sorte === "periode_d_activite")
      .map((f) => [f.id, f.attributs.lodeom ?? null]),
    lignes: carriere.lignes.map((l) => [l.annee, l.affiliation, l.lodeom]),
    fiche: [fiche.annee, fiche.lodeom, Math.round(fiche.reductionGenerale * 100) / 100],
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def _lu_par_python(saisies: Saisies, requete: dict) -> dict:
    """Ce que le moteur Python lit de la carrière que le portage bâtit."""
    carriere = saisies.carriere(requete)
    fiche = saisies.simuler(requete).remuneration.reference.droit_en_vigueur
    return {
        "faits": [[f["id"], f["attributs"].get("lodeom")]
                  for f in chrono.faits_de(carriere.chronologie, chrono.ASSURE, chrono.EMPLOI)],
        "lignes": [[ligne.annee, ligne.affiliation, ligne.lodeom] for ligne in carriere.lignes],
        "fiche": [fiche.annee, fiche.lodeom, round(fiche.reduction_generale, 2)],
    }


def test_le_portage_lit_la_meme_lodeom(saisies):
    """La saisie du portage lit le barème ; sur la carrière qu'elle bâtit, les
    deux moteurs lisent les mêmes métiers et les mêmes années, et leurs fiches
    de paie exonèrent du même montant, parcours et relevé."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    requetes = [
        {**PARCOURS, "lodeom": "competitivite"},
        {**PARCOURS, "lodeom": "inconnu"},
        {**NE_EN_1980, "releve": RELEVE, "interruptions": "2025:2025:chomage_indemnise",
         "lodeom": "innovation_et_croissance"},
        {**NE_EN_1980, "releve": RELEVE, "lodeom": "competitivite_renforcee"},
    ]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", LECTURE_JS], cwd=RACINE,
        input=json.dumps(requetes), capture_output=True, text=True, encoding="utf-8",
        check=False)
    assert execution.returncode == 0, execution.stderr
    lus = json.loads(execution.stdout)
    attendus = [_lu_par_python(saisies, requete) for requete in requetes]
    assert [{cle: lu[cle] for cle in attendu} for lu, attendu in zip(lus, attendus)] == attendus
    assert [lu["lodeom"] for lu in lus] == [
        "competitivite", "", "innovation_et_croissance", "competitivite_renforcee"]
