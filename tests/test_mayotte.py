"""Mayotte : la caisse de sécurité sociale de Mayotte et son régime de retraite
des salariés (fiche ``cssm_mayotte``), dans les deux moteurs (action 177,
étape 3).

LA VALIDATION DES TRIMESTRES. « Pour le calcul de la durée d'assurance, il y a
lieu de retenir autant de trimestres que le salaire annuel correspondant aux
retenues subies par l'assuré sur sa rémunération représente de fois le montant
du salaire minimum garanti en vigueur à Mayotte au 1er janvier de l'année
considérée, calculé sur la base de 200 heures, avec un maximum de quatre
trimestres par année civile » (décret n° 87-175 du 16 mars 1987, article 3,
LEGIARTI000006770151 ; décret n° 2003-589 du 1er juillet 2003, article 8,
LEGIARTI000006781027 et LEGIARTI000026514455). « Pour les périodes
postérieures au 31 décembre 2016 », 150 heures (rédaction du 26 septembre
2016, LEGIARTI000033155442) ; depuis 2018, du « salaire minimum de croissance
en vigueur à Mayotte » (rédaction du 22 octobre 2023, LEGIARTI000048241292).
Le Smig du 1er janvier est celui des barèmes de la Cnav, depuis 2002
(``legislation/mayotte_smig_et_plafond.csv``) : le modèle validait au Smic
national.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from retraite_notionnelle.carriere import LigneRelevee
from retraite_notionnelle.simulateur import Simulateur

RACINE = Path(__file__).resolve().parents[1]
STATUT = "salarie_mayotte"


@pytest.fixture(scope="module")
def simulateur() -> Simulateur:
    return Simulateur()


#: Le jumeau JavaScript : les lignes de chaque relevé, et le résultat entier.
_JUMEAU = """
import { readFileSync } from "node:fs";
import { Simulateur } from "./moteur/js/simulateur.js";
const cas = JSON.parse(process.argv[1]);
const simulateur = new Simulateur(JSON.parse(readFileSync("./moteur/donnees.json", "utf8")));
const sortie = cas.map(({ releve, naissance, age }) => {
  const carriere = simulateur.carriereReleve({
    annee_naissance: naissance, sexe: "F", releve, age_liquidation: age });
  return {
    lignes: carriere.lignes.map((l) => [l.annee, l.trimestres_valides, l.revenu]),
    resultat: simulateur.simuler(carriere).dictionnaire(),
  };
});
process.stdout.write(JSON.stringify(sortie));
"""


def _ecarts(obtenu, attendu, chemin="") -> list[str]:
    """Ce qui sépare le JavaScript du Python, à 1e-9 près en relatif."""
    if attendu is None:
        return []
    if isinstance(attendu, dict):
        if not isinstance(obtenu, dict):
            return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
        return [e for cle, v in attendu.items()
                for e in _ecarts(obtenu.get(cle), v, f"{chemin}.{cle}")]
    if isinstance(attendu, list):
        if not isinstance(obtenu, list) or len(obtenu) != len(attendu):
            return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
        return [e for rang, v in enumerate(attendu)
                for e in _ecarts(obtenu[rang], v, f"{chemin}[{rang}]")]
    if isinstance(attendu, bool) or not isinstance(attendu, (int, float)):
        return [] if obtenu == attendu else [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
    if obtenu is None or abs(obtenu - attendu) > 1e-9 * max(1.0, abs(attendu)):
        return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
    return []


@pytest.fixture
def deux_moteurs(simulateur):
    """Ce qui rend les lignes de chaque relevé, par année, en Python, une fois
    vérifié que le JavaScript rend les mêmes lignes et le même résultat entier.
    Une fixture, et non une fonction : la garde des présomptions saute les
    tests qui la demandent, `"node"` lu dans sa source (`tests/conftest.py`)."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    sys.path.insert(0, str(RACINE / "scripts"))
    from construire_temoins import _fini

    def confronter(cas) -> list[dict]:
        attendus, lignes = [], []
        for c in cas:
            carriere = simulateur.carriere_releve(
                c["naissance"], "F", [LigneRelevee(**ligne) for ligne in c["releve"]],
                c["age"])
            lignes.append({ligne.annee: ligne for ligne in carriere.lignes})
            attendus.append({
                "lignes": [[l.annee, l.trimestres_valides, l.revenu] for l in carriere.lignes],
                "resultat": _fini(simulateur.simuler(carriere).dictionnaire())})
        execution = subprocess.run(
            ["node", "--input-type=module", "-e", _JUMEAU, json.dumps(cas)],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
        assert execution.returncode == 0, execution.stderr[-2000:]
        ecarts = _ecarts(json.loads(execution.stdout), attendus)
        assert not ecarts, ecarts[:10]
        return lignes

    return confronter


def test_un_trimestre_se_valide_a_mayotte_au_smig_mahorais(deux_moteurs):
    """Le salaire qui valide un trimestre, à Mayotte : 200 heures du Smig
    mahorais du 1er janvier jusqu'en 2016, 150 depuis 2017. En 2002, 1 100 €
    font deux trimestres à 200 heures de 2,71 €, 542 €, et aucun au Smic
    national, 1 334 € ; en 2010, 4 750 € en font quatre à 1 186 € (5,93 €), deux
    à 1 772 € ; en 2016, 2 910 € n'en font qu'un à 1 460 € (7,30 €), quand
    150 heures du Smic national, 1 450,50 €, en feraient deux ; en 2017,
    2 220 € en font deux à 150 heures de 7,37 €, 1 105,50 €, un à 1 464 € ; en
    2025, 5 400 € en font quatre à 1 347 € (8,98 €), trois à 1 782 €. Dans les
    deux moteurs."""
    [mahoraise] = deux_moteurs([
        {"naissance": 1960, "age": 66.0, "releve": [
            {"annee": annee, "affiliation": STATUT, "revenu": revenu}
            for annee, revenu in ((2002, 1100.0), (2010, 4750.0), (2016, 2910.0),
                                  (2017, 2220.0), (2025, 5400.0))]}])
    assert {annee: mahoraise[annee].trimestres_valides
            for annee in (2002, 2010, 2016, 2017, 2025)} == {
        2002: 2, 2010: 4, 2016: 1, 2017: 2, 2025: 4}
