"""Le portage JavaScript des indicateurs de cycle de vie, rejoué contre le Python.

``moteur/js/cycle-de-vie.js`` et ``moteur/js/contributions-equilibre.js`` sont
les jumeaux de ``cycle_de_vie.py`` et de ``contributions_equilibre.py`` (action
138, étape 9) : les flux bruts des six systèmes, les indicateurs sous la
convention de l'OCDE et sous un âge de décès fixe, l'âge d'équilibre du
diviseur et l'âge de part de vie constante ; depuis le 14 octobre, les
revenus nets de chaque année (``moteur/js/prelevements-historiques.js``, le
jumeau de ``donnees/prelevements_historiques.py``), donc la convention nette
et celle du COR ; depuis le 16 octobre, l'impôt sur le revenu
(``moteur/js/impot-revenu.js``, le jumeau de ``impot_revenu.py`` et de
``donnees/impot_revenu.py``), donc les deux conventions après impôt, l'impôt
de chaque année et le taux de remplacement après impôt au départ ; depuis
le 16 octobre aussi, les âges de départ d'une carrière et ce que chacun
donne (``ages_balayes``, ``balayage_d_une_carriere``) ; depuis le 18 octobre,
la pension du départ par étage et le revenu autour du départ
(``pension_par_etage``, ``revenus_autour_du_depart``). Des carrières de statuts et de générations variés — un départ passé, que le droit
a fait vivre, un départ de l'année, un départ à venir — se calculent des deux
côtés, sous le simulateur du site, et chaque chiffre doit s'y retrouver ; le
module de l'impôt se rejoue seul sur une grille de foyers, d'années et de
revenus.
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

#: Les carrières : un statut, une génération, un âge de départ, des enfants —
#: trois au parent parti en 2010, dont l'impôt exonère la majoration
#: jusqu'aux revenus de 2012.
CARRIERES = (
    ("salarie_prive_non_cadre", 1948, "H", 62.0, 3),
    ("salarie_prive_cadre", 1958, "F", 62.0, 0),
    ("salarie_prive_non_cadre", 1962, "H", 64.0, 0),
    ("salarie_prive_cadre", 1975, "H", 66.0, 0),
    ("fonctionnaire_etat", 1966, "F", 63.0, 0),
    ("artisan", 1970, "H", 64.0, 0),
    ("salarie_prive_non_cadre", 1990, "F", 65.0, 0),
)

#: Les conventions que le portage sait servir ; ``construite`` nomme celles
#: que le modèle bâtit carrière par carrière (``convention_cor``,
#: ``convention_nette``).
CONVENTIONS = {
    "ocde": {},
    "deces_fixe": {"age_deces": "cor", "unisexe": True, "taux_actualisation": 0.0},
    "nette": {"construite": "nette"},
    "cor": {"construite": "cor"},
    "apres_impot": {"construite": "nette", "impot": "prix"},
    "cor_apres_impot": {"construite": "cor", "impot": "salaire_moyen"},
}

#: Les systèmes dont le taux de remplacement après impôt au départ se compare.
SCENARIOS_REMPLACEMENT = ("actuel", "notionnel_retroactif", "notionnel_liberal")

#: Les systèmes dont le revenu autour du départ se compare : le scénario 1, et
#: le 6, que son âge légal fait partir plus tard et qui sert son pilier.
SCENARIOS_AUTOUR = ("actuel", "notionnel_liberal")

EQUILIBRES = ((1950, None), (1975, "F"), (1995, "H"))

#: Les balayages des âges de départ : une carrière sans son âge, l'âge que la
#: saisie demande, la convention du COR ou non, le pas, l'impôt. Une carrière
#: longue après impôt, un départ passé sous le COR, un indépendant.
BALAYAGES = (
    ({"annee_naissance": 1966, "sexe": "H", "affiliation": "salarie_prive_non_cadre",
      "age_debut": 18, "niveau_salaire": 1.0}, 64.0, False, 0.25, "prix"),
    ({"annee_naissance": 1944, "sexe": "F", "affiliation": "fonctionnaire_etat",
      "age_debut": 22, "niveau_salaire": 1.3}, 62.0, True, 0.5, None),
    ({"annee_naissance": 1975, "sexe": "H", "affiliation": "artisan",
      "age_debut": 21, "niveau_salaire": 1.3}, 64.0, False, 0.5, None),
)

#: La grille du module de l'impôt seul : des années de chaque règle — les
#: majorations et minorations des années 1960, les paliers de 1968 et 1969, la
#: réduction des salaires et des pensions de 1969 à 1971, les limites de la
#: décote de 1969 et de 1970, l'exonération des salariés de 1972, la décote de
#: 1981 à 1985, le plafonnement, les 20 % d'avant 2006, l'abattement des
#: adhérents de 1976 et de 1977, la prime pour l'emploi, celle d'un bénéfice ou
#: d'un déficit mêlé à un salaire, les mesures de 2001, 2008 et 2013, la
#: réduction de 2016 à 2019 —, deux années projetées, des foyers de chaque
#: sorte, quatre revenus.
ANNEES_IMPOT = (1962, 1966, 1968, 1969, 1970, 1971, 1972, 1975, 1976, 1977, 1978, 1981,
                1983, 1984, 1988, 1995, 1999, 2000, 2001, 2005, 2008, 2010, 2013, 2014,
                2017, 2020, 2024, 2025, 2031, 2045)
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
                for unite in (("euro", "monnaie") if annee == 1975 else ("euro",)):
                    demandes.append({
                        "annee": annee, "unite": unite,
                        "indexation": "salaire_moyen" if annee == 2045 else "prix",
                        "foyer": {**foyer, "declarants": declarants}, "nom": nom})
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
                  veuf=foyer.get("veuf", False)),
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
            impot = reglages.pop("impot", None)
            if reglages.get("age_deces") == "cor":
                reglages["age_deces"] = cycle_de_vie.age_de_deces_cor(
                    simulateur.mortalite, carriere.annee_naissance)
            if impot:
                convention = cycle_de_vie.convention_apres_impot(
                    simulateur, comparaison, cor=construite == "cor", indexation=impot)
            elif construite:
                convention = cycle_de_vie.convention_nette(simulateur, comparaison,
                                                           cor=construite == "cor")
            else:
                convention = cycle_de_vie.Convention(**reglages)
            systemes = cycle_de_vie.indicateurs_des_systemes(simulateur, comparaison,
                                                             convention)
            indicateurs[nom] = {scenario: valeurs.dictionnaire()
                                for scenario, valeurs in systemes.items()}
        sous_l_impot = cycle_de_vie.flux_des_systemes(simulateur, comparaison, impot="prix")
        actuel = sous_l_impot["actuel"]
        cas.append({
            "etages": {scenario: cycle_de_vie.pension_par_etage(
                simulateur, comparaison, scenario, systemes=sous_l_impot).dictionnaire()
                for scenario in cycle_de_vie.SCENARIOS},
            "autour": {scenario: [ligne.dictionnaire() for ligne in
                                  cycle_de_vie.revenus_autour_du_depart(
                                      simulateur, comparaison, scenario, systemes=sous_l_impot)]
                       for scenario in SCENARIOS_AUTOUR},
            "impots": {str(annee): [i.salaire, i.benefice, i.pension, i.impot, i.sur_la_pension]
                       for annee, i in actuel.impots.items()},
            "revenus_apres_impot": _par_annee(actuel.revenus_apres_impot),
            "dernier_revenu_apres_impot": actuel.dernier_revenu_apres_impot,
            "remplacements_apres_impot": {
                scenario: cycle_de_vie.remplacement_apres_impot(
                    simulateur, comparaison, scenario, systemes=sous_l_impot)
                for scenario in SCENARIOS_REMPLACEMENT},
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


def _depart_en_dictionnaire(depart: cycle_de_vie.Depart) -> dict:
    import dataclasses

    return {
        "age": depart.age, "annee": depart.annee,
        "indicateurs": {scenario: valeurs.dictionnaire()
                        for scenario, valeurs in depart.indicateurs.items()},
        "pensions_nettes": depart.pensions_nettes, "pensions_aspa": depart.pensions_aspa,
        "remplacements": {scenario: None if r is None else dataclasses.asdict(r)
                          for scenario, r in depart.remplacements.items()},
        "remplacements_apres_impot": depart.remplacements_apres_impot,
        "pensions_apres_impot": depart.pensions_apres_impot,
    }


def _balayages_python(balayages: tuple) -> list[dict]:
    simulateur = Contexte().simulateur()
    resultats = []
    for options, age, cor, pas, impot in map(json.loads, balayages):
        def batir(a, options=options):
            return simulateur.carriere_simple(**options, age_liquidation=a)
        resultats.append({
            "ages": list(cycle_de_vie.ages_balayes(simulateur, batir, age, pas)),
            "departs": [_depart_en_dictionnaire(d) for d in cycle_de_vie.balayage_d_une_carriere(
                simulateur, batir, age, cor, pas, impot)],
        })
    return resultats


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
    demandes = _demandes_d_impot()
    attendu["impots"] = moitie_python(
        _impots_python, tuple(json.dumps(d, sort_keys=True) for d in demandes))
    attendu["balayages"] = moitie_python(
        _balayages_python, tuple(json.dumps(b, sort_keys=True) for b in BALAYAGES))
    obtenu = _node({
        "cas": [{"carriere": _options(*c), "conventions": CONVENTIONS} for c in CARRIERES],
        "equilibres": [{"generation": g, "sexe": s} for g, s in EQUILIBRES],
        "remplacements": SCENARIOS_REMPLACEMENT,
        "autour": SCENARIOS_AUTOUR,
        "impots": demandes,
        "balayages": [{"carriere": o, "age": a, "cor": c, "pas": p, "impot": i}
                      for o, a, c, p, i in BALAYAGES],
    })
    return obtenu, attendu


@pytest.mark.parametrize("rang", range(len(CARRIERES)),
                         ids=[f"{a}-{g}" for a, g, *_ in CARRIERES])
def test_les_indicateurs_de_chaque_systeme_se_retrouvent_en_javascript(les_deux, rang):
    obtenu, attendu = les_deux
    cas = obtenu["cas"][rang]
    assert "erreur" not in cas, cas.get("erreur")
    ecarts = _ecarts(cas, attendu["cas"][rang])
    assert not ecarts, "; ".join(sorted(ecarts)[:8])


@pytest.mark.parametrize("rang", range(len(BALAYAGES)),
                         ids=[o["affiliation"] for o, *_ in BALAYAGES])
def test_chaque_age_de_depart_se_retrouve_en_javascript(les_deux, rang):
    """Les âges balayés, et à chacun, sous les six systèmes, les indicateurs
    nets ou après impôt, la pension nette, rapportée au minimum vieillesse, le
    taux de remplacement net en trois unités et après impôt, la pension après
    impôt."""
    obtenu, attendu = les_deux
    balayage = obtenu["balayages"][rang]
    assert "erreur" not in balayage, balayage.get("erreur")
    ecarts = _ecarts(balayage, attendu["balayages"][rang])
    assert not ecarts, "; ".join(sorted(ecarts)[:8])


def test_le_balayage_a_un_objet(les_deux):
    """Le contrôle a un objet : la carrière longue part avant l'âge légal, le
    balayage finit à l'âge d'annulation de la décote, que le pas n'atteint
    pas toujours, chaque âge a son taux de remplacement net, l'impôt y joue,
    et le minimum vieillesse à deux étages d'un départ d'avant 2007 aussi."""
    _, attendu = les_deux
    longue, fonctionnaire, artisan = attendu["balayages"]
    assert longue["ages"][0] < 62.0 and longue["ages"][-1] == 67.0
    assert len(longue["departs"]) == len(longue["ages"]) > 20
    assert all(d["remplacements"]["actuel"] for d in longue["departs"])
    assert all(d["remplacements_apres_impot"]["actuel"] for d in longue["departs"])
    assert all(d["pensions_apres_impot"]["actuel"] < d["pensions_nettes"]["actuel"]
               for d in longue["departs"])
    assert fonctionnaire["departs"][0]["pensions_apres_impot"] is None
    assert fonctionnaire["departs"][0]["annee"] < 2007
    assert all(d["pensions_aspa"]["actuel"] for b in attendu["balayages"]
               for d in b["departs"])
    assert artisan["departs"] and fonctionnaire["departs"]


def test_le_salarie_du_prive_verse_des_contributions_d_equilibre_des_deux_cotes(les_deux):
    """Le contrôle a un objet : un salarié du privé en verse depuis 1984."""
    obtenu, _ = les_deux
    assert len(obtenu["cas"][2]["contributions"]) > 30


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
    sous la limite de 1975, où qui ne vit pas de salaires et de pensions a la
    sienne, et sous celle de 1977."""
    _, attendu = les_deux
    for etape in ("plafonnement", "reduction_complementaire", "reduction_des_salaires", "decote",
                  "reduction_sous_condition_de_revenus", "minoration_exceptionnelle",
                  "majoration_exceptionnelle", "reduction_exceptionnelle",
                  "reduction_proportionnelle", "prime_pour_l_emploi", "credit_exceptionnel",
                  "abattement_vingt_pour_cent", "abattement_age_invalidite",
                  "abattement_adherents", "majoration_des_benefices", "exonere"):
        assert any(i[etape] for i in attendu["impots"]), etape
    exoneres = {(d["nom"], d["annee"]) for d, i in zip(_demandes_d_impot(), attendu["impots"])
                if i["exonere"]}
    assert {("retraite", 1975), ("artisan_adherent", 1975), ("salarie", 1977)} <= exoneres
    abattus = {(d["nom"], d["annee"]) for d, i in zip(_demandes_d_impot(), attendu["impots"])
               if i["abattement_adherents"]}
    assert {("artisan_adherent", 1976), ("artisan_adherent", 1977),
            ("liberal_adherent", 1978), ("liberal_adherent", 1983)} <= abattus
    primes = {(d["nom"], d["annee"]) for d, i in zip(_demandes_d_impot(), attendu["impots"])
              if i["prime_pour_l_emploi"]}
    assert {("artisan_adherent", 2005), ("pluriactif", 2005), ("pluriactif_deficit", 2000),
            ("pluriactif_deficit", 2001)} <= primes


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


def test_l_impot_a_un_objet(les_deux):
    """Le contrôle de l'impôt a un objet : le salarié paie l'impôt de son
    salaire, puis de sa pension, et l'impôt déplace les indicateurs ;
    l'artisan déclare son bénéfice, et a ses revenus après impôt ; le parent
    de trois enfants déclare sa majoration dès les revenus de 2013, et sa
    pension déclarée y fait un saut que la revalorisation ne fait pas."""
    obtenu, _ = les_deux
    parent = obtenu["cas"][0]
    assert parent["impots"]["2013"][2] > 1.05 * parent["impots"]["2012"][2]
    cadre = obtenu["cas"][3]
    assert sum(1 for *_, impot, _ in cadre["impots"].values() if impot > 0) > 40
    assert sum(1 for *_, sur_la_pension in cadre["impots"].values() if sur_la_pension > 0) > 10
    for scenario in ("actuel", "notionnel_prospectif"):
        assert (cadre["indicateurs"]["apres_impot"][scenario]["rendement_reel"]
                < cadre["indicateurs"]["nette"][scenario]["rendement_reel"])
    assert all(cadre["remplacements_apres_impot"].values())
    artisan = obtenu["cas"][5]
    assert sum(1 for _, benefice, *_ in artisan["impots"].values() if benefice > 0) > 30
    assert artisan["revenus_apres_impot"] is not None
    assert artisan["indicateurs"]["apres_impot"]["actuel"]["taux_annuite"] is not None


def test_une_convention_apres_impot_veut_ses_flux():
    """Une convention après impôt sans prélèvements est refusée, et des flux
    sans l'impôt de son indexation aussi, plutôt que de rendre un chiffre
    faux."""
    if shutil.which("node") is None:
        pytest.skip("node absent")
    script = (
        "import { Contexte } from './moteur/js/contexte.js';"
        "import { Convention, conventionApresImpot, fluxDesSystemes, indicateurs }"
        " from './moteur/js/cycle-de-vie.js';"
        "import { readFileSync } from 'node:fs';"
        "const s = new Contexte(JSON.parse(readFileSync('moteur/donnees.json','utf8'))).simulateur();"
        "const c = s.simuler(s.carriereSimple({annee_naissance: 1962, sexe: 'H',"
        " affiliation: 'salarie_prive_non_cadre', age_debut: 21, age_liquidation: 64,"
        " niveau_salaire: 1}));"
        "const convention = conventionApresImpot(s, c);"
        "const refus = [];"
        "for (const f of [() => new Convention({impot: 'prix'}),"
        " () => new Convention({prelevement: 0.1, impot: 'loyers'}),"
        " () => indicateurs(fluxDesSystemes(s, c, {nets: true}).actuel, s, convention),"
        " () => indicateurs(fluxDesSystemes(s, c, {impot: 'salaire_moyen'}).actuel, s, convention)]) {"
        " try { f(); refus.push(false); } catch (e) { refus.push(true); } }"
        "process.stdout.write(JSON.stringify(refus));")
    execution = subprocess.run(["node", "--input-type=module", "-e", script], cwd=RACINE,
                               capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr
    assert json.loads(execution.stdout) == [True, True, True, True]


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
