"""Le salaire net de la fiche de paie, confronté au simulateur de l'Urssaf.

Le site demande le « net à payer avant impôt » de la fiche de paie. Sur une
vraie fiche, ce net a déjà perdu la part salariale de la complémentaire santé
que l'employeur doit à ses salariés depuis le 1er janvier 2016 (L. 911-7 du
code de la sécurité sociale, I ; loi n° 2013-504 du 14 juin 2013, art. 1,
IX), dont il finance au moins la moitié (III) ; et sa part patronale entre
dans l'assiette de la CSG et de la CRDS, sans l'abattement pour frais
professionnels, que le III, 1° de L. 136-1-1 ne donne qu'aux revenus
d'activité. Un cadre doit en outre la CSG sur la prévoyance que son employeur
finance, 1,50 % de la tranche 1 (accord national interprofessionnel du
17 novembre 2017 relatif à la prévoyance des cadres, art. 1er). La fiche du
moteur n'en portait rien : un net saisi remontait à un brut trop bas, de
1,1 % à 2 500 € brut, de 1,7 % au SMIC.

Le montant de la complémentaire santé n'est pas dans la loi. Le moteur reprend
celui de mon-entreprise, 40 € par mois partagés par moitié en 2026, qu'il fait
suivre le plafond de la sécurité sociale ; la saisie en dit un autre si le
lecteur le veut (décision du propriétaire du 21 novembre 2026).

Les cas viennent de l'API publique de mon-entreprise
(``scripts/fetch/mon_entreprise_brut_net.py``,
``tests/temoins/brut_net_mon_entreprise.json``). La ligne Agirc-Arrco y est
au centime : 3,15 % et 8,64 % au salarié, comme le régime les publie.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

RACINE = Path(__file__).resolve().parents[1]
TEMOIN = RACINE / "tests" / "temoins" / "brut_net_mon_entreprise.json"

#: Le portage : la fiche de chaque cas, mensuelle, et le brut d'un net.
_PORTAGE = """
import { readFileSync } from "node:fs";
import { CatalogueRegimes, Affiliations } from "./moteur/js/regimes.js";
import { DonneesMacro } from "./moteur/js/macro.js";
import { BaremePrelevements, ficheDepuisBrut, salaireBrutDepuisNet }
  from "./moteur/js/remuneration.js";
const demandes = JSON.parse(process.argv[1]);
const paquet = JSON.parse(readFileSync("./moteur/donnees.json", "utf8"));
const macro = new DonneesMacro(paquet);
const catalogue = new CatalogueRegimes(paquet);
const affiliations = new Affiliations(paquet);
const sortie = demandes.map(({ statut, annee, brut, net, mutuelle }) => {
  const plafond = macro.plafond_securite_sociale.valeur(2026);
  const bareme = new BaremePrelevements(paquet.prelevements_remuneration, mutuelle ?? null,
    plafond);
  const resultat = {};
  if (brut !== undefined) {
    const f = ficheDepuisBrut(bareme, macro, catalogue, affiliations, statut, annee,
      brut * 12, 0, null, null);
    resultat.net = f.net / 12;
    resultat.cout = f.coutDuTravail / 12;
    resultat.lignes = Object.fromEntries(f.lignes.map((l) => [l.code,
      [l.salarie / 12, l.employeur / 12]]));
  }
  if (net !== undefined) {
    resultat.brut = salaireBrutDepuisNet(bareme, macro, catalogue, affiliations, statut,
      annee, net * 12, 0, null) / 12;
  }
  return resultat;
});
process.stdout.write(JSON.stringify(sortie));
"""


def _portage(demandes: list[dict]) -> list[dict]:
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", _PORTAGE, json.dumps(demandes)],
        cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    return json.loads(execution.stdout)


def _statut(cadre: bool) -> str:
    return "salarie_prive_cadre" if cadre else "salarie_prive_non_cadre"


@pytest.fixture(scope="module")
def cas() -> list[dict]:
    return json.loads(TEMOIN.read_text(encoding="utf-8"))["cas"]


def test_le_temoin_porte_la_situation_attendue(cas):
    """Seize cas de 2026 : huit bruts, cadres et non-cadres, chacun avec la
    complémentaire santé de 20 € par mois que mon-entreprise retient."""
    assert len(cas) == 16
    assert {c["date"][-4:] for c in cas} == {"2026"}
    assert all(c["sante"] == 20.0 for c in cas)


def test_le_net_de_la_fiche_est_celui_de_l_urssaf(cas):
    """Au centime, Agirc-Arrco comprise : la complémentaire santé, la CSG sur sa part patronale et, pour un cadre, la
    CSG sur la prévoyance de 1,50 % de la tranche 1 sont dans la fiche."""
    obtenus = _portage([{"statut": _statut(c["cadre"]), "annee": 2026, "brut": c["brut"]}
                        for c in cas])
    for attendu, obtenu in zip(cas, obtenus):
        assert obtenu["lignes"]["agirc_arrco"][0] == pytest.approx(
            attendu["retraite_complementaire"], abs=0.005), attendu
        assert obtenu["net"] == pytest.approx(attendu["net"], abs=0.01), attendu
        assert obtenu["lignes"]["csg_crds"][0] == pytest.approx(attendu["csg_crds"],
                                                               abs=0.01), attendu


def test_la_complementaire_sante_est_un_forfait_partage_par_moitie():
    """20 € pour le salarié, 20 € pour l'employeur, au plafond de 2026 ; la
    CSG et la CRDS, 9,70 %, frappent la part patronale entière (L. 136-1-1) :
    1,94 € par mois."""
    [avec] = _portage([{"statut": "salarie_prive_non_cadre", "annee": 2026, "brut": 2500.0}])
    salarie, employeur = avec["lignes"]["complementaire_sante"]
    assert salarie == pytest.approx(20.0, abs=1e-6)
    assert employeur == pytest.approx(20.0, abs=1e-6)
    # 2 500 × 98,25 % × 9,70 % = 238,25625, plus 20 × 9,70 % = 1,94.
    assert avec["lignes"]["csg_crds"][0] == pytest.approx(238.25625 + 1.94, abs=1e-6)
    assert "prevoyance_cadres" not in avec["lignes"]


def test_la_prevoyance_des_cadres_est_due_sur_la_tranche_1():
    """1,50 % de la tranche 1, à la charge de l'employeur, et sa CSG : 52,50 €
    et 5,0925 € à 3 500 € brut ; 60,075 € et 5,827275 € au-delà du plafond."""
    bas, haut = _portage([
        {"statut": "salarie_prive_cadre", "annee": 2026, "brut": 3500.0},
        {"statut": "salarie_prive_cadre", "annee": 2026, "brut": 8000.0}])
    assert bas["lignes"]["prevoyance_cadres"] == [0.0, pytest.approx(52.5, abs=1e-6)]
    assert haut["lignes"]["prevoyance_cadres"] == [0.0, pytest.approx(60.075, abs=1e-6)]
    assert bas["lignes"]["csg_crds"][0] == pytest.approx(
        3500 * 0.9825 * 0.097 + (20 + 52.5) * 0.097, abs=1e-6)


def test_la_complementaire_sante_n_est_due_que_depuis_2016():
    """L. 911-7, I, entre en vigueur le 1er janvier 2016 : une fiche de 2015
    n'en porte pas, une fiche de 2016 la porte."""
    avant, apres = _portage([
        {"statut": "salarie_prive_non_cadre", "annee": 2015, "brut": 2500.0},
        {"statut": "salarie_prive_non_cadre", "annee": 2016, "brut": 2500.0}])
    assert "complementaire_sante" not in avant["lignes"]
    assert "complementaire_sante" in apres["lignes"]


def test_le_lecteur_peut_dire_sa_propre_mutuelle():
    """35 € par mois au lieu de 20 : le salarié en paie 15 de plus, et 15 de
    plus de part patronale entrent dans l'assiette de la CSG, 1,455 € ; le
    net baisse de 16,455 €."""
    defaut, sienne = _portage([
        {"statut": "salarie_prive_non_cadre", "annee": 2026, "brut": 2500.0},
        {"statut": "salarie_prive_non_cadre", "annee": 2026, "brut": 2500.0,
         "mutuelle": 35.0}])
    assert sienne["lignes"]["complementaire_sante"] == [
        pytest.approx(35.0, abs=1e-6), pytest.approx(35.0, abs=1e-6)]
    assert defaut["net"] - sienne["net"] == pytest.approx(15 + 15 * 0.097, abs=1e-6)


def test_un_net_de_fiche_de_paie_remonte_a_son_brut(cas):
    """Le net à payer de l'Urssaf remonte au brut d'où il vient, au centime :
    1 957,05 € à 2 500 €."""
    choisis = [c for c in cas if c["brut"] in (1823.03, 2500.0, 5000.0)]
    nets = [c["net"] for c in choisis]
    bruts = _portage([{"statut": _statut(c["cadre"]), "annee": 2026, "net": n}
                      for c, n in zip(choisis, nets)])
    for c, obtenu in zip(choisis, bruts):
        assert obtenu["brut"] == pytest.approx(c["brut"], abs=0.01), c
