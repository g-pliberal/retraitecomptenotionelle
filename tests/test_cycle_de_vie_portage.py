"""Le portage JavaScript des indicateurs de cycle de vie, rejoué contre le Python.

``moteur/js/cycle-de-vie.js`` et ``moteur/js/contributions-equilibre.js`` sont
les jumeaux de ``cycle_de_vie.py`` et de ``contributions_equilibre.py`` (action
138, étape 9) : les flux bruts des six systèmes, les indicateurs sous la
convention de l'OCDE et sous un âge de décès fixe, l'âge d'équilibre du
diviseur et l'âge de part de vie constante. Des carrières de statuts et de
générations variés — un départ passé, que le droit a fait vivre, un départ
de l'année, un départ à venir — se calculent des deux côtés, sous le
simulateur du site, et chaque chiffre doit s'y retrouver. Ce que le portage
n'a pas encore — les revenus nets, la convention du COR, l'impôt — est refusé
par lui, et le test le vérifie aussi.
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle import cycle_de_vie
from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.contributions_equilibre import contributions_d_une_carriere

from outils_portage import moitie_python

RACINE = Path(__file__).resolve().parents[1]

#: Les carrières : un statut, une génération, un âge de départ.
CARRIERES = (
    ("salarie_prive_non_cadre", 1948, "H", 62.0),
    ("salarie_prive_cadre", 1958, "F", 62.0),
    ("salarie_prive_non_cadre", 1962, "H", 64.0),
    ("salarie_prive_cadre", 1975, "H", 66.0),
    ("fonctionnaire_etat", 1966, "F", 63.0),
    ("artisan", 1970, "H", 64.0),
    ("salarie_prive_non_cadre", 1990, "F", 65.0),
)

#: Les conventions que le portage sait servir.
CONVENTIONS = {
    "ocde": {},
    "deces_fixe": {"age_deces": "cor", "unisexe": True, "taux_actualisation": 0.0},
}

EQUILIBRES = ((1950, None), (1975, "F"), (1995, "H"))


def _options(affiliation, generation, sexe, age):
    return {"annee_naissance": generation, "sexe": sexe, "affiliation": affiliation,
            "age_debut": 21, "age_liquidation": age, "niveau_salaire": 1.3}


def _python(carrieres, conventions, equilibres):
    simulateur = Contexte().simulateur()
    cas = []
    for carriere_ in carrieres:
        carriere = simulateur.carriere_simple(**_options(*carriere_))
        comparaison = simulateur.simuler(carriere)
        indicateurs = {}
        for nom, champs in conventions:
            reglages = dict(champs)
            if reglages.get("age_deces") == "cor":
                reglages["age_deces"] = cycle_de_vie.age_de_deces_cor(
                    simulateur.mortalite, carriere.annee_naissance)
            systemes = cycle_de_vie.indicateurs_des_systemes(
                simulateur, comparaison, cycle_de_vie.Convention(**reglages))
            indicateurs[nom] = {scenario: valeurs.dictionnaire()
                                for scenario, valeurs in systemes.items()}
        cas.append({
            "contributions": {str(annee): montant for annee, montant in
                              contributions_d_une_carriere(simulateur, carriere).items()},
            "taux_de_prelevement": cycle_de_vie.taux_de_prelevement(simulateur,
                                                                    comparaison.actuel),
            "indicateurs": indicateurs,
        })
    ages = []
    for generation, sexe in equilibres:
        age = cycle_de_vie.age_d_equilibre(simulateur, generation, sexe)
        ages.append({
            "age": age.age, "au_mois": age.au_mois, "coefficient": age.coefficient,
            "part_de_vie": cycle_de_vie.age_de_part_de_vie_constante(
                simulateur, generation, sexe),
            "part_de_vie_cor": cycle_de_vie.age_de_part_de_vie_constante(
                simulateur, generation, sexe, cor=True),
        })
    return {"cas": cas, "equilibres": ages}


def _node(demande: dict) -> dict:
    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8",
                                     delete=False) as fichier:
        json.dump(demande, fichier)
        chemin = fichier.name
    try:
        execution = subprocess.run(
            ["node", str(RACINE / "tests" / "js" / "comparer-cycle-de-vie.mjs"), chemin],
            cwd=RACINE, capture_output=True, text=True, encoding="utf-8", check=False)
    finally:
        Path(chemin).unlink()
    assert execution.returncode == 0, execution.stderr
    return json.loads(execution.stdout)


def _ecarts(obtenu, attendu, chemin="") -> list[str]:
    if isinstance(attendu, dict):
        if not isinstance(obtenu, dict):
            return [f"{chemin} : {obtenu!r} au lieu d'un objet"]
        return [e for cle in attendu.keys() | obtenu.keys()
                for e in _ecarts(obtenu.get(cle), attendu.get(cle), f"{chemin}.{cle}")]
    if isinstance(attendu, list):
        if not isinstance(obtenu, list) or len(obtenu) != len(attendu):
            return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]
        return [e for i, (o, a) in enumerate(zip(obtenu, attendu))
                for e in _ecarts(o, a, f"{chemin}[{i}]")]
    if (isinstance(attendu, (int, float)) and isinstance(obtenu, (int, float))
            and not isinstance(attendu, bool) and not isinstance(obtenu, bool)):
        if math.isclose(obtenu, attendu, rel_tol=1e-9, abs_tol=1e-9):
            return []
    elif obtenu == attendu:
        return []
    return [f"{chemin} : {obtenu!r} au lieu de {attendu!r}"]


@pytest.fixture(scope="module")
def les_deux():
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    conventions = tuple(sorted((nom, tuple(sorted(champs.items())))
                               for nom, champs in CONVENTIONS.items()))
    attendu = moitie_python(_python, CARRIERES, conventions, EQUILIBRES)
    obtenu = _node({
        "cas": [{"carriere": _options(*c), "conventions": CONVENTIONS} for c in CARRIERES],
        "equilibres": [{"generation": g, "sexe": s} for g, s in EQUILIBRES],
    })
    return obtenu, attendu


@pytest.mark.parametrize("rang", range(len(CARRIERES)),
                         ids=[f"{a}-{g}" for a, g, _, _ in CARRIERES])
def test_les_indicateurs_de_chaque_systeme_se_retrouvent_en_javascript(les_deux, rang):
    obtenu, attendu = les_deux
    cas = obtenu["cas"][rang]
    assert "erreur" not in cas, cas.get("erreur")
    ecarts = _ecarts(cas, attendu["cas"][rang])
    assert not ecarts, "; ".join(sorted(ecarts)[:8])


def test_le_salarie_du_prive_verse_des_contributions_d_equilibre_des_deux_cotes(les_deux):
    """Le contrôle a un objet : un salarié du privé en verse depuis 1984."""
    obtenu, _ = les_deux
    assert len(obtenu["cas"][2]["contributions"]) > 30


def test_les_ages_d_equilibre_se_retrouvent_en_javascript(les_deux):
    obtenu, attendu = les_deux
    ecarts = _ecarts(obtenu["equilibres"], attendu["equilibres"])
    assert not ecarts, "; ".join(ecarts[:8])


def test_ce_que_le_portage_n_a_pas_encore_est_refuse():
    """Les revenus nets et l'impôt ne sont pas portés : une convention qui les
    demande lève une erreur, plutôt que de rendre un chiffre faux."""
    if shutil.which("node") is None:
        pytest.skip("node absent")
    script = (
        "import { Contexte } from './moteur/js/contexte.js';"
        "import { Convention, indicateursDesSystemes } from './moteur/js/cycle-de-vie.js';"
        "import { readFileSync } from 'node:fs';"
        "const s = new Contexte(JSON.parse(readFileSync('moteur/donnees.json','utf8'))).simulateur();"
        "const c = s.simuler(s.carriereSimple({annee_naissance: 1962, sexe: 'H',"
        " affiliation: 'salarie_prive_non_cadre', age_debut: 21, age_liquidation: 64,"
        " niveau_salaire: 1}));"
        "const refus = [];"
        "for (const f of [() => indicateursDesSystemes(s, c, new Convention({prelevement: 0.1})),"
        " () => new Convention({impot: 'prix'})]) {"
        " try { f(); refus.push(false); } catch (e) { refus.push(/pas encore port/.test(e.message)); } }"
        "process.stdout.write(JSON.stringify(refus));")
    execution = subprocess.run(["node", "--input-type=module", "-e", script], cwd=RACINE,
                               capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    assert json.loads(execution.stdout) == [True, True]
