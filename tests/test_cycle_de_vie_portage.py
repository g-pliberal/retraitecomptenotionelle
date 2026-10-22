"""Les jumeaux que lit le cycle de vie du portage, rejoués contre le Python.

Le cycle de vie n'a plus qu'un exemplaire, ``moteur/js/cycle-de-vie.js``
(action 161) : ses définitions se tiennent dans ``tests/js/cycle-de-vie.test.js``,
et sa concordance avec ``cycle_de_vie.py`` est partie avec lui. Restent ici
trois paires qu'il lit, et dont le Python garde son jumeau pour le coût et la
fabrique : ``contributions_equilibre.py`` et
``moteur/js/contributions-equilibre.js``, sur des carrières de statuts et de
générations variés ; ``impot_revenu.py`` et ``moteur/js/impot-revenu.js``,
étape par étape, sur une grille de foyers, d'années et de revenus ;
``donnees/prelevements_historiques.py`` et
``moteur/js/prelevements-historiques.js``, famille par famille, sur une
grille d'années et de revenus. Chaque chiffre doit s'y retrouver.
"""

from __future__ import annotations

import json
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from retraite_notionnelle.contexte import Contexte
from retraite_notionnelle.contributions_equilibre import contributions_d_une_carriere

from outils_portage import moitie_python

RACINE = Path(__file__).resolve().parents[1]

#: Les carrières : un statut, une génération, un âge de départ, des enfants.
#: Les salariés du privé versent des contributions d'équilibre depuis 1984 ;
#: le fonctionnaire, l'artisan, le commerçant et les agents des régimes
#: spéciaux n'en versent pas.
CARRIERES = (
    ("salarie_prive_non_cadre", 1948, "H", 62.0, 3),
    ("salarie_prive_cadre", 1958, "F", 62.0, 0),
    ("salarie_prive_non_cadre", 1962, "H", 64.0, 0),
    ("salarie_prive_cadre", 1975, "H", 66.0, 0),
    ("fonctionnaire_etat", 1966, "F", 63.0, 0),
    ("artisan", 1970, "H", 64.0, 0),
    ("salarie_prive_non_cadre", 1990, "F", 65.0, 0),
    ("agent_sncf", 1975, "H", 57.0, 0),
    ("commercant", 1936, "H", 65.0, 0),
    ("artisan", 1936, "F", 64.0, 0),
    ("agent_chemins_fer_secondaires", 1930, "H", 55.0, 0),
)

#: La grille du module de l'impôt seul : des années de chaque règle — chaque
#: année de 1960 à 1968, leurs décimes, la décote de 1960 et ses limites par
#: part, puis pour le foyer et les âgés, les réductions de 1966 et 1967, la
#: majoration de 1967 et ses décotes, les paliers de 1968 et 1969, la réduction
#: des salaires et des pensions de 1960 à 1971, les limites de la décote de 1969
#: et de 1970, l'exonération des salariés de 1972, l'arrondi à la centaine de
#: 1968 à 1979, la décote de 1981 à 1985, le plafonnement, les 20 % d'avant
#: 2006, l'abattement des adhérents de 1976 et de 1977, la prime pour l'emploi,
#: celle d'un bénéfice ou d'un déficit mêlé à un salaire, les mesures de 2001,
#: 2008 et 2013, la réduction de 2016 à 2019 —, deux années projetées, des
#: foyers de chaque sorte, quatre revenus.
ANNEES_IMPOT = (1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971,
                1972, 1975, 1976, 1977, 1978, 1981, 1983, 1984, 1988, 1995, 1999, 2000,
                2001, 2005, 2008, 2010, 2013, 2014, 2017, 2020, 2024, 2025, 2031, 2045)
FOYERS_IMPOT = {
    "salarie": {"declarants": [{"salaires": 1.0}]},
    "retraite": {"declarants": [{"pensions": 0.8, "age": 70}]},
    "depart": {"declarants": [{"salaires": 0.4, "pensions": 0.5, "age": 64}]},
    "couple": {"declarants": [{"salaires": 1.0}, {"pensions": 0.6, "age": 66}], "enfants": 2},
    "parent_isole": {"declarants": [{"salaires": 1.0}], "enfants": 3, "enfants_invalides": 1},
    "veuf": {"declarants": [{"pensions": 1.0, "age": 75}], "enfants": 1, "veuf": True},
    "invalide": {"declarants": [{"salaires": 0.5, "invalide": True}]},
    "couple_mono_emploi": {"declarants": [{"salaires": 1.0}, {}], "enfants": 1},
    "artisan_adherent": {"declarants": [{"benefices": 1.0}]},
    "liberal_adherent": {"declarants": [{"benefices": 1.0, "categorie": "bnc"}]},
    "non_adherent": {"declarants": [{"benefices": 1.0, "regime": "reel_non_adherent"}]},
    "deficit": {"declarants": [{"salaires": 1.0}, {"benefices": -0.3, "regime": "micro"}]},
    "pluriactif": {"declarants": [{"salaires": 0.5, "benefices": 0.2}]},
    "pluriactif_deficit": {"declarants": [{"salaires": 0.7, "benefices": -0.1}]},
    "artisan_fiscal": {"declarants": [{"benefices": 1.0, "artisan": True}]},
    "couple_independant": {"declarants": [{"benefices": 0.6, "artisan": True},
                                          {"benefices": 0.5, "categorie": "bnc"}]},
    "taxe_payee": {"declarants": [{"benefices": 1.0}],
                   "taxe_complementaire_de_l_annee_precedente": 0.03},
}
NIVEAUX_IMPOT = (0.25, 0.7, 1.6, 5.0)


def _demandes_d_impot() -> list[dict]:
    """Chaque foyer de la grille, chaque année, à chaque niveau : ses revenus
    en euros, d'environ 20 000 € en 2000 au niveau 1, menés à 4 % l'an ;
    l'année 1975 en francs aussi."""
    demandes = []
    for annee in ANNEES_IMPOT:
        echelle = 20000.0 * 1.04 ** (annee - 2000)
        for nom, foyer in FOYERS_IMPOT.items():
            for niveau in NIVEAUX_IMPOT:
                declarants = [{cle: (valeur * niveau * echelle
                                     if cle in ("salaires", "pensions", "benefices")
                                     else valeur)
                               for cle, valeur in d.items()} for d in foyer["declarants"]]
                payee = {cle: valeur * niveau * echelle for cle, valeur in foyer.items()
                         if cle == "taxe_complementaire_de_l_annee_precedente"}
                for unite in (("euro", "monnaie") if annee == 1975 else ("euro",)):
                    demandes.append({
                        "annee": annee, "unite": unite,
                        "indexation": "salaire_moyen" if annee == 2045 else "prix",
                        "foyer": {**foyer, **payee, "declarants": declarants}, "nom": nom})
    return demandes


def _impots_python(demandes: tuple) -> list[dict]:
    import dataclasses

    from retraite_notionnelle.donnees.impot_revenu import (
        charger_baremes_impot_revenu,
        croissance_macro,
    )
    from retraite_notionnelle.impot_revenu import Declarant, Foyer, impot_du_foyer

    simulateur = Contexte().simulateur()
    baremes = charger_baremes_impot_revenu(RACINE / "data")
    resultats = []
    for demande in map(json.loads, demandes):
        foyer = demande["foyer"]
        resultat = impot_du_foyer(
            Foyer(declarants=tuple(Declarant(**d) for d in foyer["declarants"]),
                  enfants=foyer.get("enfants", 0),
                  enfants_invalides=foyer.get("enfants_invalides", 0),
                  veuf=foyer.get("veuf", False),
                  taxe_complementaire_de_l_annee_precedente=foyer.get(
                      "taxe_complementaire_de_l_annee_precedente", 0.0)),
            demande["annee"], baremes, unite=demande["unite"],
            indexation=demande["indexation"],
            croissance=croissance_macro(simulateur.macro, demande["indexation"]))
        valeurs = dataclasses.asdict(resultat)
        valeurs["fiabilite"] = resultat.fiabilite.name.lower()
        resultats.append(json.loads(json.dumps(valeurs)))
    return resultats


def _options(affiliation, generation, sexe, age, enfants):
    return {"annee_naissance": generation, "sexe": sexe, "affiliation": affiliation,
            "age_debut": 21, "age_liquidation": age, "niveau_salaire": 1.3,
            "nombre_enfants": enfants}


def _contributions_python(carrieres) -> list[dict[str, float]]:
    simulateur = Contexte().simulateur()
    return [{str(annee): montant for annee, montant in contributions_d_une_carriere(
        simulateur, simulateur.carriere_simple(**_options(*carriere))).items()}
        for carriere in carrieres]


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
    demandes = _demandes_d_impot()
    attendu = {
        "contributions": moitie_python(_contributions_python, CARRIERES),
        "impots": moitie_python(
            _impots_python, tuple(json.dumps(d, sort_keys=True) for d in demandes)),
    }
    obtenu = _node({"carrieres": [_options(*c) for c in CARRIERES], "impots": demandes})
    return obtenu, attendu


@pytest.mark.parametrize("rang", range(len(CARRIERES)),
                         ids=[f"{a}-{g}" for a, g, *_ in CARRIERES])
def test_les_contributions_d_equilibre_de_chaque_carriere_se_retrouvent_en_javascript(
        les_deux, rang):
    obtenu, attendu = les_deux
    contributions = obtenu["contributions"][rang]
    assert "erreur" not in contributions, contributions.get("erreur")
    ecarts = _ecarts(contributions, attendu["contributions"][rang])
    assert not ecarts, "; ".join(sorted(ecarts)[:8])


def test_le_salarie_du_prive_verse_des_contributions_d_equilibre_des_deux_cotes(les_deux):
    """Le contrôle a un objet : un salarié du privé en verse depuis 1984."""
    obtenu, _ = les_deux
    assert len(obtenu["contributions"][2]) > 30


def test_l_impot_de_chaque_foyer_se_retrouve_en_javascript(les_deux):
    """Le jumeau de ``impot_revenu.py``, étape par étape, sur la grille : les
    parts, le barème et son plafonnement, la décote, chaque correction, la
    prime pour l'emploi, le seuil de recouvrement, en francs et en euros, lus
    et projetés."""
    obtenu, attendu = les_deux
    assert len(obtenu["impots"]) == len(attendu["impots"])
    ecarts = [e for rang, (o, a) in enumerate(zip(obtenu["impots"], attendu["impots"]))
              for e in _ecarts(o, a, f"[{rang}] {a['annee']}")]
    assert not ecarts, f"{len(ecarts)} écarts : " + "; ".join(ecarts[:8])


def test_la_grille_de_l_impot_a_un_objet(les_deux):
    """La grille touche chaque étape : chaque correction y joue au moins une
    fois, l'abattement des adhérents sous chacune de ses lois, l'exonération
    au minimum garanti de 1971, d'un salaire et d'un déficit, sous la limite
    de 1975, où qui ne vit pas de salaires et de pensions a la sienne, et sous
    celle de 1977 ; la taxe complémentaire, de l'artisan de 1964 et de son
    abattement partagé à l'abattement de 1969, jusqu'à sa fin."""
    _, attendu = les_deux
    for etape in ("plafonnement", "reduction_complementaire", "reduction_des_salaires", "decote",
                  "reduction_sous_condition_de_revenus", "minoration_exceptionnelle",
                  "majoration_exceptionnelle", "reduction_exceptionnelle",
                  "reduction_proportionnelle", "prime_pour_l_emploi", "credit_exceptionnel",
                  "abattement_vingt_pour_cent", "abattement_age_invalidite",
                  "abattement_adherents", "majoration_des_benefices", "exonere",
                  "taxe_complementaire", "taxe_complementaire_deduite"):
        assert any(i[etape] for i in attendu["impots"]), etape
    taxes = {(d["nom"], d["annee"]) for d, i in zip(_demandes_d_impot(), attendu["impots"])
             if i["taxe_complementaire"]}
    assert {("artisan_fiscal", 1964), ("couple_independant", 1964), ("liberal_adherent", 1969),
            ("artisan_adherent", 1969)} <= taxes
    assert not {("artisan_fiscal", 1965), ("artisan_adherent", 1970)} & taxes
    exoneres = {(d["nom"], d["annee"]) for d, i in zip(_demandes_d_impot(), attendu["impots"])
                if i["exonere"]}
    assert {("invalide", 1971), ("deficit", 1971), ("retraite", 1975),
            ("artisan_adherent", 1975), ("salarie", 1977)} <= exoneres
    abattus = {(d["nom"], d["annee"]) for d, i in zip(_demandes_d_impot(), attendu["impots"])
               if i["abattement_adherents"]}
    assert {("artisan_adherent", 1976), ("artisan_adherent", 1977),
            ("liberal_adherent", 1978), ("liberal_adherent", 1983)} <= abattus
    primes = {(d["nom"], d["annee"]) for d, i in zip(_demandes_d_impot(), attendu["impots"])
              if i["prime_pour_l_emploi"]}
    assert {("artisan_adherent", 2005), ("pluriactif", 2005), ("pluriactif_deficit", 2000),
            ("pluriactif_deficit", 2001)} <= primes


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
