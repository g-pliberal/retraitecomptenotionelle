"""L'option du conjoint collaborateur, saisie (fiche
``conjoint_collaborateur_independants`` ; action 138, étape 18).

Le conjoint collaborateur d'un artisan ou d'un commerçant cotise « à sa
demande » sur un revenu forfaitaire égal au tiers du plafond, ou sur 33,33 % ou
50 % du revenu d'activité du chef d'entreprise (D. 633-19-2, depuis le 25 mai
2020 ; avant, la même fraction pouvait se partager avec le chef), et sur le
forfait « si aucun autre choix n'est effectué » (R. 662-1). Affilié d'office
depuis le 1er juillet 2007, il ne relevait avant que d'une assurance volontaire,
sur le tiers ou la moitié du revenu du chef (D. 742-26).

Le menu dit l'option, le forfait par défaut ; le revenu d'une période de
conjoint collaborateur est alors celui du chef, dont la saisie ne garde que la
part que l'option retient — rien au forfait, que le modèle donne au tiers du
plafond depuis 2007 (``carriere.assiette_du_conjoint_collaborateur``). Le
relevé, qui porte l'assiette de chaque année, n'en dépend pas.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import parse_qs

import pytest

from retraite_notionnelle.web.site import ErreurSite, module, site

from outils_pont import Saisies, refus_de_la_saisie, saisie_du_portage

RACINE = Path(__file__).resolve().parents[1]

#: Les plafonds annuels de la sécurité sociale de 2010, 2020 et 2026 :
#: 34 620 €, 41 136 € et 48 060 €.
PLAFONDS = {2010: 34_620.0, 2020: 41_136.0, 2026: 48_060.0}

#: Une conjointe d'artisan, née le 15 mars 1962, collaboratrice de 1995 à son
#: départ, le 1er avril 2026 ; le revenu du chef, 1,2 fois le salaire moyen,
#: sous un profil plat, qui le garde le même pour tous les statuts.
COLLABORATRICE = {
    "naissance": "1962-03-15", "sexe": "F", "liquidation": "2026-04-01",
    "debut": "1995-01-01", "statut": "conjoint_collaborateur_artisan",
    "unite_revenu": "moyen", "salaire": "1.2", "profil": "plat",
}
#: Le chef d'entreprise lui-même, au même revenu : sa ligne est le revenu
#: dont l'option prend une part.
CHEF = {**COLLABORATRICE, "statut": "artisan"}

#: Une salariée, collaboratrice de son conjoint commerçant depuis 2000, partie
#: en juillet 2017, qui saisit sa pension.
PAR_PENSION = {
    "naissance": "1955-06-01", "sexe": "F", "situation": "retraite",
    "saisie_par": "pension", "pension": "1200", "montants": "brut",
    "debut": "1975-09-01", "statut": "salarie_prive_non_cadre", "profil": "plat",
    "metier2_debut": "2000-01-01", "metier2_statut": "conjoint_collaborateur_commercant",
    "liquidation": "2017-07-01",
}


@pytest.fixture(scope="module")
def saisies() -> Saisies:
    return Saisies()


def _revenus(carriere) -> dict[int, float]:
    return {ligne.annee: ligne.revenu for ligne in carriere.lignes}


# -- la saisie ----------------------------------------------------------------------

def test_le_menu_offre_le_forfait_puis_les_deux_parts_du_revenu_du_chef():
    """Le forfait d'abord, qui est le défaut (R. 662-1) ; puis 33,33 % et 50 %
    du revenu du chef (D. 633-19-2, 2° et 3°). Le forfait n'en cotise rien."""
    saisie = module("saisie")
    assert [code for code, _ in saisie.ASSIETTES_COLLABORATEUR] == ["", "tiers", "moitie"]
    assert saisie.PARTS_COLLABORATEUR == {"": 0.0, "tiers": 0.3333, "moitie": 0.5}


def test_la_saisie_lit_l_option_et_l_adresse_la_garde():
    assert saisie_du_portage({"collaborateur": "moitie"}).collaborateur == "moitie"
    assert saisie_du_portage({"collaborateur": "quart"}).collaborateur == ""
    lu = parse_qs(saisie_du_portage({"collaborateur": "tiers"}).requete())
    assert lu["collaborateur"] == ["tiers"]
    assert saisie_du_portage({k: v[0] for k, v in lu.items()}).collaborateur == "tiers"
    assert "collaborateur" not in parse_qs(saisie_du_portage({}).requete())


# -- les métiers --------------------------------------------------------------------

def test_au_forfait_le_conjoint_cotise_le_tiers_du_plafond_depuis_2007(saisies):
    """Sans option, le forfait : le tiers du plafond chaque année depuis
    l'affiliation obligatoire, proratisé sur les trois mois de 2026, et rien
    avant 2007, l'assurance volontaire non souscrite. Le revenu du chef n'y
    compte pas."""
    revenus = _revenus(saisies.carriere(COLLABORATRICE))
    assert revenus[2010] == pytest.approx(PLAFONDS[2010] / 3)
    assert revenus[2020] == pytest.approx(PLAFONDS[2020] / 3)
    assert revenus[2026] == pytest.approx(PLAFONDS[2026] / 3 * 3 / 12)
    assert {annee: revenu for annee, revenu in revenus.items() if annee < 2007} == {
        annee: 0.0 for annee in range(1995, 2007)}
    autre = saisies.carriere({**COLLABORATRICE, "salaire": "0.5"})
    assert _revenus(autre) == pytest.approx(revenus)


@pytest.mark.parametrize("option", ["tiers", "moitie"])
def test_a_l_option_le_conjoint_cotise_sa_part_du_revenu_du_chef(saisies, option):
    """À l'option, chaque année cotise sa part du revenu du chef, l'assurance
    volontaire d'avant 2007 comprise (D. 742-26) ; le statut reste le sien."""
    chef = _revenus(saisies.carriere(CHEF))
    carriere = saisies.carriere({**COLLABORATRICE, "collaborateur": option})
    part = {"tiers": 0.3333, "moitie": 0.5}[option]
    assert _revenus(carriere) == pytest.approx(
        {annee: part * revenu for annee, revenu in chef.items()})
    assert {ligne.affiliation for ligne in carriere.lignes} == {
        "conjoint_collaborateur_artisan"}


def test_l_option_ne_touche_pas_aux_autres_statuts(saisies):
    """Le chef lui-même, ou tout autre statut, garde son revenu, quelle que soit
    l'option dite."""
    chef = _revenus(saisies.carriere(CHEF))
    assert _revenus(saisies.carriere({**CHEF, "collaborateur": "moitie"})) == pytest.approx(chef)


def test_un_revenu_du_chef_hors_des_bornes_est_refuse_meme_au_forfait():
    """Le champ porte les bornes d'un revenu ; la saisie les oppose aussi au
    revenu du chef, même au forfait, où il ne compte pas."""
    with pytest.raises(ErreurSite,
                       match=refus_de_la_saisie("entre 0,1 et 10 fois le salaire moyen")):
        saisie_du_portage({**COLLABORATRICE, "salaire": "12"})


# -- la pension saisie et le relevé -------------------------------------------------

@pytest.mark.parametrize("option", ["", "moitie"])
def test_l_inversion_par_la_pension_garde_l_option(option):
    """Saisie par sa pension, la carrière prend un seul niveau de revenu pour
    toutes ses périodes : celui de la salariée, et celui du chef, dont la
    collaboratrice ne cotise que la part de son option. C'est la carrière que
    la page reprend en écrivant ce niveau dans chaque période ; au forfait, le
    niveau trouvé n'y change rien."""
    requete = {**PAR_PENSION, "collaborateur": option}
    comparaison = site().contexte.simuler(saisie_du_portage(requete))
    niveau = repr(comparaison.niveau_inverse.niveau)
    reprise = site().contexte.carriere(saisie_du_portage({
        **{cle: valeur for cle, valeur in requete.items() if cle != "pension"},
        "saisie_par": "revenu", "unite_revenu": "moyen",
        "salaire": niveau, "metier2_salaire": niveau}))
    assert _revenus(comparaison.carriere) == pytest.approx(_revenus(reprise))
    if not option:
        revenus = _revenus(comparaison.carriere)
        assert revenus[2010] == pytest.approx(PLAFONDS[2010] / 3) and revenus[2001] == 0.0


def test_le_releve_porte_l_assiette_quelle_que_soit_l_option(saisies):
    """Un relevé dit l'assiette de chaque année : l'option n'y change rien, et
    une année sans revenu y vaut le forfait depuis 2007."""
    releve = {"naissance": "1962-03-15", "liquidation": "2026-04-01",
              "releve": "2009:conjoint_collaborateur_artisan:9000\n"
                        "2010:conjoint_collaborateur_artisan:0"}
    sans = _revenus(saisies.carriere(releve))
    avec = _revenus(saisies.carriere({**releve, "collaborateur": "moitie"}))
    assert avec == pytest.approx(sans)
    assert sans[2009] == 9000.0 and sans[2010] == pytest.approx(PLAFONDS[2010] / 3)


# -- le portage ---------------------------------------------------------------------

LECTURE_JS = """
import { readFileSync } from "node:fs";
import { Contexte } from "./moteur/js/contexte.js";
import { Saisie } from "./moteur/js/saisie.js";

const contexte = new Contexte(JSON.parse(readFileSync("moteur/donnees.json", "utf8")));
const sortie = JSON.parse(readFileSync(0, "utf8")).map((requete) => {
  const saisie = Saisie.depuisRequete(requete, false, contexte.paquet.presomptions);
  const comparaison = contexte.simuler(saisie);
  return {
    requete: saisie.requete(),
    collaborateur: saisie.collaborateur,
    niveau: comparaison.niveau_inverse ? Math.round(comparaison.niveau_inverse.niveau * 1e6) : null,
    lignes: comparaison.carriere.lignes.map((l) => [l.annee, l.affiliation,
      Math.round(l.revenu * 100) / 100]),
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def test_le_portage_lit_l_option():
    """La saisie du portage lit l'option, au forfait et à l'option, par le
    revenu et par la pension, qu'elle inverse. Sa jumelle Python, à qui elle
    se confrontait ici, ne l'est plus que par les témoins
    (``tests/test_pont.py``), jusqu'à son retrait (action 161, étape 6)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    requetes = [
        COLLABORATRICE,
        {**COLLABORATRICE, "collaborateur": "tiers"},
        {**COLLABORATRICE, "unite_revenu": "euros_mois", "salaire": "3000",
         "collaborateur": "moitie"},
        {**CHEF, "collaborateur": "moitie"},
        PAR_PENSION,
        {**PAR_PENSION, "collaborateur": "tiers"},
    ]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", LECTURE_JS], cwd=RACINE,
        input=json.dumps(requetes), capture_output=True, text=True, encoding="utf-8",
        check=False)
    assert execution.returncode == 0, execution.stderr
    lus = json.loads(execution.stdout)
    assert [lu["collaborateur"] for lu in lus] == [
        "", "tiers", "moitie", "moitie", "", "tiers"]
    assert [lu["niveau"] is None for lu in lus] == [True] * 4 + [False] * 2
