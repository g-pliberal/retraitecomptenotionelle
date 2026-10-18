"""La fiche de paie d'un libéral et d'un avocat prélève ce que le compte reçoit.

La fiche de paie tire la retraite des fiches de régime
(:func:`~retraite_notionnelle.remuneration.bloc_droit_en_vigueur`), et n'en
lisait que les taux et les bornes en plafonds. Quatre formes lui échappaient,
que le compte notionnel lit depuis qu'elles existent : les tranches fixées en
euros, que la caisse n'indexe pas (la complémentaire de la CNBF, celle de la
CARPIMKO) ; le forfait (``cotisation_forfaitaire_euros`` : la cotisation de
croisière de la CNBF, la CARMF, la CAVP, la CARCDSF, la CARPIMKO, les PCV) ;
les classes, qui appellent un montant selon le revenu (la Cipav jusqu'en 2022,
la CAVEC, la CARPV) ; l'assiette qui n'est pas le revenu
(``assiette_facteur_revenu`` : les commissions de l'agent général, les
produits de l'office du notaire). La complémentaire de la CNBF prélevait ainsi
59,4 % du revenu d'un avocat en 2026, la somme des taux de ses cinq tranches,
et la Cipav n'apparaissait sur la fiche d'un libéral qu'en 2023 (action 138,
étape 9).

Les valeurs attendues viennent des barèmes des caisses : celui de la CNBF pour
2026 (19 janvier 2026), la fiche pratique 2022 de la Cipav, relus le
18 octobre 2026 ; l'exemple que la Cipav déroule elle-même est rejoué par
``test_oracle.py`` (``cipav_cotisations_2022``).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from retraite_notionnelle import Parametres
from retraite_notionnelle.carriere import AnneeCarriere, Carriere
from retraite_notionnelle.config import PartCotisation
from retraite_notionnelle.moteur.compte import ConstructeurCompte
from retraite_notionnelle.remuneration import fiche_depuis_brut, salaire_brut_depuis_net
from retraite_notionnelle.simulateur import Simulateur

PARAMETRES = Parametres()
RACINE = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur(PARAMETRES)


def _fiche(simulateur: Simulateur, statut: str, annee: int, revenu: float):
    return fiche_depuis_brut(PARAMETRES.racine_donnees, simulateur.macro,
                             simulateur.catalogue, simulateur.affiliations,
                             statut, annee, revenu)


def _retraite(simulateur: Simulateur, statut: str, annee: int, revenu: float
              ) -> dict[str, float]:
    """Les lignes de retraite de la fiche, part de l'assuré."""
    return {ligne.code: ligne.salarie
            for ligne in _fiche(simulateur, statut, annee, revenu).lignes if ligne.retraite}


# -- la CNBF, au barème de 2026 ---------------------------------------------
#
# « Revenu/Classes : de 1 € à 42.507 €, 42.508 à 85.014 €, 85.015 à 127.521 €,
# 127.522 à 170.028 €, 170.029 à 212.535 € ; C1 : 7,00 %, 10,40 %, 12,20 %,
# 14,00 %, 15,80 % » ; au régime de base, « 6ème année et avocats âgés de
# 65 ans & plus : 1 988 € » de cotisation forfaitaire et une cotisation
# proportionnelle « taux de 3,2 % » (barème de la CNBF pour 2026).

TRANCHES_CNBF_2026 = (42_507.0, 85_014.0, 127_521.0, 170_028.0, 212_535.0)
TAUX_C1_2026 = (0.0700, 0.1040, 0.1220, 0.1400, 0.1580)


def test_la_complementaire_de_l_avocat_suit_les_tranches_en_euros_de_son_bareme(
        simulateur):
    """Chaque taux sur sa seule tranche, et rien au-delà de la dernière borne :
    à 60 000 €, 7 % de 42 507 € et 10,40 % des 17 493 € qui suivent ; à
    250 000 €, les cinq tranches pleines, 42 507 € chacune."""
    a_60_000 = 0.07 * 42_507 + 0.104 * (60_000 - 42_507)
    assert _retraite(simulateur, "avocat", 2026, 60_000.0)["cnbf_complementaire"] == (
        pytest.approx(a_60_000, abs=0.01))
    pleines = sum(taux * 42_507 for taux in TAUX_C1_2026)
    assert _retraite(simulateur, "avocat", 2026, 250_000.0)["cnbf_complementaire"] == (
        pytest.approx(pleines, abs=0.01))
    assert pleines / 250_000.0 < 0.11


def test_la_base_de_l_avocat_preleve_son_forfait_de_croisiere(simulateur):
    """Le forfait de la sixième année, 1 988 €, et 3,2 % du revenu."""
    assert _retraite(simulateur, "avocat", 2026, 60_000.0)["cnbf"] == pytest.approx(
        1_988 + 0.032 * 60_000, abs=0.01)


# -- la Cipav d'avant 2023, à la grille de sa fiche pratique 2022 ------------
#
# « Jusqu'à 26 580 € Classe A : 1 527 € ; de 26 581 € à 49 280 € Classe B :
# 3 055 € ; de 49 281 € à 57 850 € Classe C : 4 582 € ; de 57 851 € à 66 400 €
# Classe D : 7 637 € ; [...] 123 301 € et plus Classe H : 19 857 € ».


@pytest.mark.parametrize("revenu, cotisation", [
    (20_000.0, 1_527.0), (60_000.0, 7_637.0), (66_400.0, 7_637.0), (130_000.0, 19_857.0)])
def test_la_cipav_d_avant_2023_appelle_la_classe_ou_tombe_le_revenu(
        simulateur, revenu, cotisation):
    assert _retraite(simulateur, "profession_liberale", 2022, revenu)[
        "cipav_complementaire"] == pytest.approx(cotisation, abs=0.01)


# -- la fiche prélève ce que le compte reçoit ---------------------------------

#: Les statuts d'indépendants dont un régime porte une des quatre formes.
STATUTS = ("avocat", "profession_liberale", "auxiliaire_medical", "pharmacien",
           "biologiste_liberal", "expert_comptable", "agent_general_assurance",
           "notaire", "veterinaire", "chirurgien_dentiste_ou_sage_femme",
           "sage_femme", "medecin_liberal", "medecin_liberal_secteur_2")


@pytest.mark.parametrize("statut", STATUTS)
def test_la_fiche_preleve_ce_que_le_compte_recoit(simulateur, statut):
    """Un revenu constant de 60 000 € par an depuis 1960 : chaque année de
    1975 à 2029, chaque ligne de retraite de la fiche vaut ce que le compte
    reçoit de l'assuré pour ce régime. Le revenu ne changeant pas, l'année de
    revenu que la classe regarde (N, N-1 ou N-2) n'y change rien, et la classe
    du début d'activité est passée depuis longtemps."""
    revenu = 60_000.0
    carriere = Carriere(
        annee_naissance=1935, sexe="H", age_liquidation=95,
        lignes=[AnneeCarriere(annee=annee, affiliation=statut, trimestres_valides=4,
                              revenu=revenu) for annee in range(1960, 2030)])
    compte = ConstructeurCompte(
        simulateur.macro, simulateur.catalogue, simulateur.affiliations,
        simulateur.indexation, PARAMETRES.avec(part_cotisation=PartCotisation.SALARIALE))
    ecarts = []
    for annee in range(1975, 2030):
        recu = dict(compte.cotisation_annuelle(carriere, annee).par_regime)
        preleve = _retraite(simulateur, statut, annee, revenu)
        for code in sorted(set(recu) | set(preleve)):
            if abs(recu.get(code, 0.0) - preleve.get(code, 0.0)) > 0.01:
                ecarts.append((annee, code, recu.get(code, 0.0), preleve.get(code, 0.0)))
    assert not ecarts, ecarts[:5]


def test_le_net_d_un_avocat_au_revenu_modeste_se_retrouve(simulateur):
    """Le forfait pèse plus du tiers d'un petit revenu : la dichotomie qui
    remonte du net au brut ne s'arrête plus à trois fois le net."""
    brut = salaire_brut_depuis_net(PARAMETRES.racine_donnees, simulateur.macro,
                                   simulateur.catalogue, simulateur.affiliations,
                                   "avocat", 2026, 1_000.0)
    assert brut > 3_000.0
    assert _fiche(simulateur, "avocat", 2026, brut).net == pytest.approx(1_000.0, abs=0.01)


# -- le portage JavaScript ----------------------------------------------------

#: Les cas que le jumeau rejoue : chaque forme, à plusieurs années.
CAS = (("avocat", 2026, 60_000.0), ("avocat", 2026, 250_000.0), ("avocat", 2010, 60_000.0),
       ("avocat", 2016, 30_000.0), ("profession_liberale", 2022, 27_000.0),
       ("profession_liberale", 2022, 60_000.0), ("profession_liberale", 1990, 40_000.0),
       ("profession_liberale", 2026, 60_000.0), ("agent_general_assurance", 2026, 60_000.0),
       ("notaire", 2026, 60_000.0), ("medecin_liberal", 2026, 90_000.0),
       ("medecin_liberal", 1990, 50_000.0), ("pharmacien", 1980, 40_000.0),
       ("expert_comptable", 2026, 50_000.0), ("veterinaire", 2026, 50_000.0),
       ("auxiliaire_medical", 2026, 40_000.0),
       ("chirurgien_dentiste_ou_sage_femme", 2026, 80_000.0))

_JUMEAU = """
import { readFileSync } from "node:fs";
import { CatalogueRegimes, Affiliations } from "./moteur/js/regimes.js";
import { DonneesMacro } from "./moteur/js/macro.js";
import { BaremePrelevements, ficheDepuisBrut, salaireBrutDepuisNet }
  from "./moteur/js/remuneration.js";
const cas = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("./moteur/donnees.json", "utf8"));
const bareme = new BaremePrelevements(paquet.prelevements_remuneration);
const macro = new DonneesMacro(paquet);
const catalogue = new CatalogueRegimes(paquet);
const affiliations = new Affiliations(paquet);
const fiches = cas.map(([statut, annee, revenu]) => {
  const fiche = ficheDepuisBrut(bareme, macro, catalogue, affiliations, statut, annee, revenu);
  return {
    net: fiche.net,
    lignes: Object.fromEntries(fiche.lignes.map((l) => [l.code, [l.salarie, l.employeur]])),
  };
});
const brut = salaireBrutDepuisNet(bareme, macro, catalogue, affiliations, "avocat", 2026, 1000);
process.stdout.write(JSON.stringify({ fiches, brut }));
"""


def test_le_portage_javascript_rend_les_memes_fiches(simulateur):
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _JUMEAU, json.dumps(CAS)],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    obtenu = json.loads(execution.stdout)
    for (statut, annee, revenu), fiche in zip(CAS, obtenu["fiches"]):
        attendue = _fiche(simulateur, statut, annee, revenu)
        lignes = {ligne.code: [ligne.salarie, ligne.employeur] for ligne in attendue.lignes}
        assert set(fiche["lignes"]) == set(lignes), (statut, annee)
        for code, (salarie, employeur) in lignes.items():
            assert fiche["lignes"][code] == [pytest.approx(salarie, abs=1e-6),
                                             pytest.approx(employeur, abs=1e-6)], (
                statut, annee, code)
        assert fiche["net"] == pytest.approx(attendue.net, abs=1e-6), (statut, annee)
    assert obtenu["brut"] == pytest.approx(salaire_brut_depuis_net(
        PARAMETRES.racine_donnees, simulateur.macro, simulateur.catalogue,
        simulateur.affiliations, "avocat", 2026, 1_000.0), abs=1e-6)
