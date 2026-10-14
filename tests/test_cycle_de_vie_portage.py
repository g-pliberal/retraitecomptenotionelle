"""Le portage JavaScript des indicateurs de cycle de vie, rejoué contre le Python.

``moteur/js/cycle-de-vie.js`` et ``moteur/js/contributions-equilibre.js`` sont
les jumeaux de ``cycle_de_vie.py`` et de ``contributions_equilibre.py`` (action
138, étape 9) : les flux bruts des six systèmes, les indicateurs sous la
convention de l'OCDE et sous un âge de décès fixe, l'âge d'équilibre du
diviseur et l'âge de part de vie constante ; depuis le 14 octobre, les
revenus nets de chaque année (``moteur/js/prelevements-historiques.js``, le
jumeau de ``donnees/prelevements_historiques.py``), donc la convention nette
et celle du COR. Des carrières de statuts et de générations variés — un
départ passé, que le droit a fait vivre, un départ de l'année, un départ à
venir — se calculent des deux côtés, sous le simulateur du site, et chaque
chiffre doit s'y retrouver. Ce que le portage n'a pas encore — l'impôt — est
refusé par lui, et le test le vérifie aussi.
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

#: Les conventions que le portage sait servir ; ``construite`` nomme celles
#: que le modèle bâtit carrière par carrière (``convention_cor``,
#: ``convention_nette``).
CONVENTIONS = {
    "ocde": {},
    "deces_fixe": {"age_deces": "cor", "unisexe": True, "taux_actualisation": 0.0},
    "nette": {"construite": "nette"},
    "cor": {"construite": "cor"},
}

EQUILIBRES = ((1950, None), (1975, "F"), (1995, "H"))


def _options(affiliation, generation, sexe, age):
    return {"annee_naissance": generation, "sexe": sexe, "affiliation": affiliation,
            "age_debut": 21, "age_liquidation": age, "niveau_salaire": 1.3}


def _par_annee(valeurs):
    return None if valeurs is None else {str(annee): v for annee, v in valeurs.items()}


def _python(carrieres, conventions, equilibres):
    simulateur = Contexte().simulateur()
    cas = []
    for carriere_ in carrieres:
        carriere = simulateur.carriere_simple(**_options(*carriere_))
        comparaison = simulateur.simuler(carriere)
        indicateurs = {}
        for nom, champs in conventions:
            reglages = dict(champs)
            construite = reglages.pop("construite", None)
            if reglages.get("age_deces") == "cor":
                reglages["age_deces"] = cycle_de_vie.age_de_deces_cor(
                    simulateur.mortalite, carriere.annee_naissance)
            convention = (cycle_de_vie.convention_nette(simulateur, comparaison,
                                                        cor=construite == "cor")
                          if construite else cycle_de_vie.Convention(**reglages))
            systemes = cycle_de_vie.indicateurs_des_systemes(simulateur, comparaison,
                                                             convention)
            indicateurs[nom] = {scenario: valeurs.dictionnaire()
                                for scenario, valeurs in systemes.items()}
        cas.append({
            "contributions": {str(annee): montant for annee, montant in
                              contributions_d_une_carriere(simulateur, carriere).items()},
            "taux_de_prelevement": cycle_de_vie.taux_de_prelevement(simulateur,
                                                                    comparaison.actuel),
            "revenus_nets": _par_annee(cycle_de_vie.revenus_nets(simulateur, carriere)),
            "revenus_nets_proposition": _par_annee(
                cycle_de_vie.revenus_nets(simulateur, carriere, proposition=True)),
            "revenus_imposables": _par_annee(
                cycle_de_vie.revenus_imposables(simulateur, carriere)),
            "prelevements": _par_annee(
                cycle_de_vie.prelevements_par_annee(simulateur, comparaison)),
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


def test_les_revenus_nets_ont_un_objet(les_deux):
    """Le contrôle des nets a un objet : chaque carrière a une fiche de paie,
    et l'histoire déplace le net — la CSG n'existait pas en 1970."""
    obtenu, _ = les_deux
    for cas in obtenu["cas"]:
        assert cas["revenus_nets"] and len(cas["prelevements"]) > 20
        assert cas["indicateurs"]["cor"]["actuel"]["taux_annuite"] is not None


def test_ce_que_le_portage_n_a_pas_encore_est_refuse():
    """L'impôt n'est pas porté : une convention qui le demande lève une
    erreur, plutôt que de rendre un chiffre faux."""
    if shutil.which("node") is None:
        pytest.skip("node absent")
    script = (
        "import { Contexte } from './moteur/js/contexte.js';"
        "import { Convention, fluxDesSystemes } from './moteur/js/cycle-de-vie.js';"
        "import { readFileSync } from 'node:fs';"
        "const s = new Contexte(JSON.parse(readFileSync('moteur/donnees.json','utf8'))).simulateur();"
        "const c = s.simuler(s.carriereSimple({annee_naissance: 1962, sexe: 'H',"
        " affiliation: 'salarie_prive_non_cadre', age_debut: 21, age_liquidation: 64,"
        " niveau_salaire: 1}));"
        "const refus = [];"
        "for (const f of [() => fluxDesSystemes(s, c, {impot: 'prix'}),"
        " () => new Convention({impot: 'prix'})]) {"
        " try { f(); refus.push(false); } catch (e) { refus.push(/pas encore port/.test(e.message)); } }"
        "process.stdout.write(JSON.stringify(refus));")
    execution = subprocess.run(["node", "--input-type=module", "-e", script], cwd=RACINE,
                               capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    assert json.loads(execution.stdout) == [True, True]


#: La grille du module seul : chaque famille, des années de chaque époque, des
#: revenus de part et d'autre des plafonds et des paliers.
FAMILLES_GRILLE = ("prive", "contractuel", "agent", "artisan", "commercant", "liberal",
                   "avocat", None)
ANNEES_GRILLE = (1968, 1975, 1983, 1991, 1997, 2001, 2012, 2018, 2021, 2024, 2025, 2026)
REVENUS_GRILLE = (0.2, 0.9, 2.5, 6.0)


def _grille_python():
    from retraite_notionnelle.donnees.prelevements_historiques import (
        charger_prelevements_historiques,
    )
    historique = charger_prelevements_historiques(RACINE / "data")
    parts = {serie: 0.1 + 0.05 * rang for rang, serie
             in enumerate(sorted(historique.regimes_des_pensions))}
    parts["maladie_complementaires"] = 0.4
    lignes = []
    for annee in ANNEES_GRILLE:
        plafond = 10000.0 + 1000.0 * (annee - 1968)
        lignes.append([annee, historique.taux_pension_annuel(annee, parts),
                       historique.taux_deductible_pension_annuel(annee, parts)])
        for famille in FAMILLES_GRILLE:
            for niveau in REVENUS_GRILLE:
                brut = niveau * plafond
                if famille is not None:
                    lignes.append([annee, famille, niveau, historique.hors_retraite_annuel(
                        famille, annee, brut, plafond, 0.12 * brut)])
                lignes.append([annee, famille, niveau, historique.non_deductibles_annuel(
                    famille, annee, brut, plafond, 0.12 * brut)])
    return {"parts": parts, "lignes": lignes}


def test_l_histoire_des_prelevements_se_retrouve_en_javascript():
    """Le jumeau de ``prelevements_historiques.py``, famille par famille, sur
    une grille d'années et de revenus : les pensions, les salaires, les
    indépendants, le net imposable."""
    if shutil.which("node") is None:
        pytest.skip("node absent")
    attendu = _grille_python()
    script = (
        "import { readFileSync } from 'node:fs';"
        "import { chargerPrelevementsHistoriques } from './moteur/js/prelevements-historiques.js';"
        "const h = chargerPrelevementsHistoriques(JSON.parse(readFileSync('moteur/donnees.json','utf8')));"
        f"const d = {json.dumps({'parts': attendu['parts'], 'annees': ANNEES_GRILLE, 'familles': FAMILLES_GRILLE, 'revenus': REVENUS_GRILLE})};"
        "const parts = new Map(Object.entries(d.parts)); const lignes = [];"
        "for (const annee of d.annees) { const plafond = 10000 + 1000 * (annee - 1968);"
        " lignes.push([annee, h.tauxPensionAnnuel(annee, parts), h.tauxDeductiblePensionAnnuel(annee, parts)]);"
        " for (const famille of d.familles) for (const niveau of d.revenus) { const brut = niveau * plafond;"
        "  if (famille !== null) lignes.push([annee, famille, niveau, h.horsRetraiteAnnuel(famille, annee, brut, plafond, 0.12 * brut)]);"
        "  lignes.push([annee, famille, niveau, h.nonDeductiblesAnnuel(famille, annee, brut, plafond, 0.12 * brut)]); } }"
        "process.stdout.write(JSON.stringify(lignes));")
    execution = subprocess.run(["node", "--input-type=module", "-e", script], cwd=RACINE,
                               capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    ecarts = _ecarts(json.loads(execution.stdout), attendu["lignes"])
    assert not ecarts, "; ".join(ecarts[:8])
