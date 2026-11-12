"""La relecture des paires de la garantie et de l'impôt sur le revenu (action
161, lot E) : ce que la concordance n'exécutait pas, confronté au bit.

``python scripts/jumeaux.py --couverture``, au commit 3944fdc : les tests de
concordance n'exécutaient que 30 % de ``garantie.py`` — le barème d'une
personne, jamais la garantie d'une population —, et, de ``impot_revenu.py``,
ni un refus, ni l'impôt d'un revenu imposable donné, ni la taxe
complémentaire seule, ni quatre branches rares. Ce fichier fait calculer les
mêmes demandes aux deux jumeaux, ``src/retraite_notionnelle/garantie.py`` et
``impot_revenu.py`` d'un côté, ``moteur/js/garantie.js`` et
``impot-revenu.js`` de l'autre, par un seul appel à node, et les veut égaux
à l'unité du dernier chiffre ; un refus, de même message.

Les valeurs que les tests de concordance comparent ne viennent d'aucune
source : ils disent que les deux jumeaux font le même calcul, non qu'il est
juste — c'est l'objet de ``tests/test_garantie_degressive.py``,
``tests/test_garantie_par_sexe.py``, ``tests/test_impot_revenu.py`` et
``tests/test_referents.py``. Le seul comportement que la relecture change a
sa valeur posée à la main :
:func:`test_une_tranche_sans_borne_superieure_est_la_tranche_ouverte`.
"""

from __future__ import annotations

import dataclasses
import json
import random
import shutil
import subprocess

import pytest

from retraite_notionnelle import garantie, impot_revenu
from retraite_notionnelle.config import RACINE_PROJET
from retraite_notionnelle.donnees import impot_revenu as donnees_impot
from retraite_notionnelle.donnees.distribution import DistributionPensions, Tranche

#: La moitié JavaScript : chaque demande calculée par le portage, sur le
#: paquet du dépôt. Les chemins se résolvent depuis la racine, où node tourne.
SCRIPT = r"""
import { readFileSync } from "node:fs";
import * as garantie from "./moteur/js/garantie.js";
import * as impot from "./moteur/js/impot-revenu.js";

const demandes = JSON.parse(readFileSync(0, "utf8"));
const paquet = JSON.parse(readFileSync("moteur/donnees.json", "utf8"));
const baremes = impot.chargerBaremesImpotRevenu(paquet);

const distribution = (tranches) => ({
  tranches: tranches.map(([borneInferieure, borneSuperieure, part]) => (
    { borneInferieure, borneSuperieure, part })),
});
const chiffre = (c) => [c.plancherMensuel, c.facteur, c.partBeneficiaires, c.beneficiaires,
  c.complementMoyenMensuel, c.coutAnnuelMeur];
const foyerDe = (f) => new impot.Foyer({
  ...f, declarants: f.declarants.map((d) => new impot.Declarant(d)),
});
const croissanceDe = (taux) => (taux === null ? null : () => taux);
const parametresDe = (p) => ({
  annee: p.annee, monnaie: p.monnaie, seuils: p.seuils, taux: p.taux, series: p.series,
  derniere_annee_lue: p.derniere_annee_lue, indexation: p.indexation, fiabilite: p.fiabilite,
  projete: p.projete,
});

const CALCULS = {
  complement: ({ arguments: a }) => garantie.complementGarantie(...a),
  manque: ({ arguments: a }) => garantie.manqueMoyen(...a),
  moyenne: (d) => garantie.pensionMoyenne(distribution(d.tranches)),
  facteurs: ({ arguments: a }) => garantie.facteursParSexe(...a),
  cout: (d) => chiffre(garantie.coutGarantie(distribution(d.tranches), d.effectif, d.plancher,
    d.facteur, ...d.forme)),
  cout_brut: (d) => chiffre(garantie.coutGarantie({ tranches: d.tranches }, d.effectif,
    d.plancher, d.facteur, ...d.forme)),
  par_sexe: (d) => chiffre(garantie.coutGarantieParSexe(distribution(d.femmes),
    distribution(d.hommes), d.part_femmes, d.effectif, d.plancher, d.facteur, d.rapport,
    d.plancher_majore, d.part_seule, ...d.forme)),
  impot: (d) => impot.impotDuFoyer(foyerDe(d.foyer), d.annee, baremes, {
    unite: d.unite, indexation: d.indexation, croissance: croissanceDe(d.croissance),
  }),
  revenu_imposable: (d) => impot.impotDUnRevenuImposable(foyerDe(d.foyer), d.annee, d.revenu,
    baremes, { unite: d.unite, indexation: d.indexation, croissance: croissanceDe(d.croissance) }),
  taxe: (d) => impot.taxeComplementaireDesRevenus(foyerDe(d.foyer), d.annee, baremes,
    { unite: d.unite }),
  parametres: (d) => parametresDe(d.par === "chronique"
    ? baremes.chronique(d.annee, d.indexation, croissanceDe(d.croissance)).get(d.annee)
    : baremes.parametres(d.annee, d.indexation, croissanceDe(d.croissance))),
  constantes: () => Object.fromEntries(Object.entries(impot)
    .filter(([nom, valeur]) => nom === nom.toUpperCase() && typeof valeur !== "function")),
};

process.stdout.write(JSON.stringify(demandes.map((demande) => {
  try {
    return { valeur: CALCULS[demande.quoi](demande) };
  } catch (erreur) {
    return { refus: erreur.message };
  }
})));
"""

BAREMES = donnees_impot.charger_baremes_impot_revenu(RACINE_PROJET / "data")


# -- la moitié Python --------------------------------------------------------


def _distribution(tranches) -> DistributionPensions:
    """Une distribution de tranches données, sans passer par le fichier."""
    distribution = object.__new__(DistributionPensions)
    distribution.tranches = [Tranche(*tranche) for tranche in tranches]
    return distribution


def _chiffre(cout: garantie.CoutGarantie) -> list[float]:
    return [cout.plancher_mensuel, cout.facteur, cout.part_beneficiaires, cout.beneficiaires,
            cout.complement_moyen_mensuel, cout.cout_annuel_meur]


def _foyer(f: dict) -> impot_revenu.Foyer:
    return impot_revenu.Foyer(**{
        **f, "declarants": tuple(impot_revenu.Declarant(**d) for d in f["declarants"])})


def _croissance(taux):
    return None if taux is None else (lambda annee: taux)


def _impot(resultat: impot_revenu.ImpotDuFoyer) -> dict:
    valeurs = dataclasses.asdict(resultat)
    valeurs["fiabilite"] = resultat.fiabilite.name.lower()
    return valeurs


def _parametres(p: donnees_impot.ParametresImpot) -> dict:
    return {"annee": p.annee, "monnaie": p.monnaie, "seuils": p.seuils, "taux": p.taux,
            "series": p.series, "derniere_annee_lue": p.derniere_annee_lue,
            "indexation": p.indexation, "fiabilite": p.fiabilite.name.lower(),
            "projete": p.projete}


def _constantes() -> dict:
    """Les constantes des deux modules Python que le portage réunit, écrites
    comme lui : une plage par ses années, ou par ses deux bornes."""
    valeurs = {nom: valeur for module in (donnees_impot, impot_revenu)
               for nom, valeur in vars(module).items()
               if nom == nom.upper() and not nom.startswith("_") and nom != "CHEMIN"}
    valeurs["DECOTE_DATEE_PAR_L_IPP"] = list(valeurs["DECOTE_DATEE_PAR_L_IPP"])
    centaine = valeurs["ARRONDI_A_LA_CENTAINE"]
    valeurs["ARRONDI_A_LA_CENTAINE"] = [centaine[0], centaine[-1]]
    return valeurs


CALCULS = {
    "complement": lambda d: garantie.complement_garantie(*d["arguments"]),
    "manque": lambda d: garantie._manque_moyen(*d["arguments"]),
    "moyenne": lambda d: garantie.pension_moyenne(_distribution(d["tranches"])),
    "facteurs": lambda d: garantie.facteurs_par_sexe(*d["arguments"]),
    "cout": lambda d: _chiffre(garantie.cout_garantie(
        _distribution(d["tranches"]), d["effectif"], d["plancher"], d["facteur"],
        part_retrait_entier=d["forme"][0], taux_retrait=d["forme"][1])),
    "par_sexe": lambda d: _chiffre(garantie.cout_garantie_par_sexe(
        _distribution(d["femmes"]), _distribution(d["hommes"]), d["part_femmes"], d["effectif"],
        d["plancher"], d["facteur"], d["rapport"], d["plancher_majore"], d["part_seule"],
        part_retrait_entier=d["forme"][0], taux_retrait=d["forme"][1])),
    "impot": lambda d: _impot(impot_revenu.impot_du_foyer(
        _foyer(d["foyer"]), d["annee"], BAREMES, unite=d["unite"], indexation=d["indexation"],
        croissance=_croissance(d["croissance"]))),
    "revenu_imposable": lambda d: _impot(impot_revenu.impot_d_un_revenu_imposable(
        _foyer(d["foyer"]), d["annee"], d["revenu"], BAREMES, unite=d["unite"],
        indexation=d["indexation"], croissance=_croissance(d["croissance"]))),
    "taxe": lambda d: impot_revenu.taxe_complementaire_des_revenus(
        _foyer(d["foyer"]), d["annee"], BAREMES, unite=d["unite"]),
    "parametres": lambda d: _parametres(
        BAREMES.chronique(d["annee"], d["indexation"], _croissance(d["croissance"]))[d["annee"]]
        if d["par"] == "chronique"
        else BAREMES.parametres(d["annee"], d["indexation"], _croissance(d["croissance"]))),
    "constantes": lambda d: _constantes(),
}


def _python(demande: dict) -> dict:
    """Ce que le jumeau Python rend, écrit comme node l'écrit : en JSON."""
    try:
        valeur = CALCULS[demande["quoi"]](demande)
    except ValueError as erreur:
        return {"refus": str(erreur)}
    return json.loads(json.dumps({"valeur": valeur}))


# -- les demandes ------------------------------------------------------------


def _tranches(sexe: str) -> list[list]:
    distribution = DistributionPensions(RACINE_PROJET / "data", sexe)
    return [[t.borne_inferieure, t.borne_superieure, t.part] for t in distribution.tranches]


#: Le barème différentiel, la forme suédoise de la proposition, et deux formes
#: aux bords : aucun retrait entier, un pivot au tiers sans pente adoucie.
FORMES = ([1.0, 1.0], [0.5, 0.5], [0.0, 0.25], [0.3, 1.0])


def _demandes_de_la_garantie() -> list[dict]:
    ensemble, femmes, hommes = (_tranches(sexe) for sexe in ("ensemble", "F", "H"))
    demandes: list[dict] = []
    for forme in FORMES:
        for plancher in (800.0, 1050.0):
            for pas in range(0, 81):
                demandes.append({"quoi": "complement",
                                 "arguments": [plancher, pas * 25.3, *forme]})
        # Des tranches de part et d'autre du pivot (400 €) et de la sortie
        # (1 200 €) d'un plancher de 800 €, fermées puis ouvertes.
        for basse, haute in ((0, 100), (300, 400), (350, 450), (400, 500), (700, 900),
                             (1150, 1250), (1200, 1300), (1300, 1400), (0, 2000),
                             (300, None), (799, None), (800, None), (1199, None),
                             (1200, None), (1300, None)):
            demandes.append({"quoi": "manque", "arguments": [basse, haute, 800.0, *forme]})
        for tranches in (ensemble, femmes, hommes):
            for facteur in (1.0, 0.9, 0.75, 0.6, 1.1):
                for plancher in (800.0, 1050.0, 916.78, 1200.5):
                    demandes.append({"quoi": "cout", "tranches": tranches, "effectif": 17.2e6,
                                     "plancher": plancher, "facteur": facteur, "forme": forme})
        for rapport in (1.0, 0.95, 0.85):
            for facteur in (1.0, 0.8):
                for majore, seule in ((None, None), (1050.0, {"F": 0.55, "H": 0.3}),
                                      (1050.0, {"F": 1.0, "H": 0.0}), (None, {"F": 0.5, "H": 0.5})):
                    demandes.append({
                        "quoi": "par_sexe", "femmes": femmes, "hommes": hommes,
                        "part_femmes": 0.53, "effectif": 17.2e6, "plancher": 800.0,
                        "facteur": facteur, "rapport": rapport, "plancher_majore": majore,
                        "part_seule": seule, "forme": forme})
    for tranches in (ensemble, femmes, hommes):
        demandes.append({"quoi": "moyenne", "tranches": tranches})
    for rapport in (1.0, 0.9, 0.641, 1.2):
        demandes.append({"quoi": "facteurs", "arguments": [1200.0, 1900.0, 0.53, 0.8, rapport]})
    return demandes


def _refus_de_la_garantie() -> list[dict]:
    tranches = [[0.0, 1000.0, 0.5], [1000.0, None, 0.5]]
    cout = {"quoi": "cout", "tranches": tranches, "effectif": 1e6, "plancher": 800.0,
            "facteur": 1.0, "forme": [0.5, 0.5]}
    return [
        {**cout, "facteur": 0.0}, {**cout, "facteur": -1.0},
        {**cout, "forme": [-0.1, 0.5]}, {**cout, "forme": [1.1, 0.5]},
        {**cout, "forme": [0.5, 0.0]}, {**cout, "forme": [0.5, 1.5]},
        {"quoi": "facteurs", "arguments": [1200.0, 1900.0, 0.53, 0.8, 0.0]},
        {"quoi": "facteurs", "arguments": [0.0, 0.0, 0.53, 0.8, 1.0]},
        {"quoi": "par_sexe", "femmes": tranches, "hommes": tranches, "part_femmes": 0.5,
         "effectif": 1e6, "plancher": 800.0, "facteur": 1.0, "rapport": -0.5,
         "plancher_majore": None, "part_seule": None, "forme": [1.0, 1.0]},
    ]


def _montant(alea: random.Random, echelle: float) -> float:
    """Un revenu autour de l'échelle : nul, entier, au centime ou quelconque."""
    if alea.random() < 0.25:
        return 0.0
    valeur = (echelle * alea.choice([0.01, 0.05, 0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 1.5, 3.0])
              * alea.uniform(0.5, 1.5))
    tirage = alea.random()
    if tirage < 0.3:
        return float(round(valeur))
    return round(valeur, 2) if tirage < 0.5 else valeur


def _foyers_au_hasard(nombre: int, graine: int = 161) -> list[dict]:
    """Des foyers tirés d'une graine fixe, de 1960 à vingt ans de projection :
    un ou deux déclarants, de tout âge, régime et catégorie, des revenus de
    part et d'autre de chaque seuil du barème de leur année."""
    alea = random.Random(graine)
    demandes = []
    for _ in range(nombre):
        annee = alea.randint(BAREMES.premiere_annee, BAREMES.derniere_annee + 20)
        unite = alea.choice(["euro", "monnaie"])
        lus = BAREMES.lus(min(annee, BAREMES.derniere_annee))
        echelle = lus.seuils[-1] * alea.choice([0.03, 0.08, 0.15, 0.3, 1.0, 2.0])
        if unite == "euro" and lus.monnaie == "FRF":
            echelle /= donnees_impot.FRANC
        declarants = []
        for _ in range(alea.choice([1, 1, 2])):
            categorie = alea.choice(impot_revenu.CATEGORIES_DU_BENEFICE)
            benefice = _montant(alea, echelle) if alea.random() < 0.5 else 0.0
            if alea.random() < 0.15:
                benefice = -benefice
            declarants.append({
                "salaires": _montant(alea, echelle),
                "pensions": _montant(alea, echelle) if alea.random() < 0.5 else 0.0,
                "age": alea.choice([None, 30, 64, 65, 66, 70, 71, 75, 76, 80]),
                "invalide": alea.random() < 0.15, "benefices": benefice,
                "regime": alea.choice(impot_revenu.REGIMES_DU_BENEFICE),
                "categorie": categorie,
                "artisan": categorie == "bic" and alea.random() < 0.3})
        enfants = alea.choice([0, 0, 1, 2, 3, 4, 6])
        demandes.append({"quoi": "impot", "annee": annee, "unite": unite,
                         "indexation": alea.choice(donnees_impot.INDEXATIONS),
                         "croissance": 0.0175, "foyer": {
                             "declarants": declarants, "enfants": enfants,
                             "enfants_invalides": (alea.randint(0, enfants)
                                                   if alea.random() < 0.2 else 0),
                             "veuf": len(declarants) == 1 and alea.random() < 0.2,
                             "vit_seul": alea.random() < 0.7,
                             "taxe_complementaire_de_l_annee_precedente": (
                                 _montant(alea, echelle * 0.05) if alea.random() < 0.2 else 0.0)}})
    return demandes


def _salarie(salaires: float, **foyer) -> dict:
    return {"declarants": [{"salaires": salaires}], **foyer}


#: Les quatre branches que ni la grille de ``test_cycle_de_vie_portage.py`` ni
#: les essais de ``tests/js`` n'exécutaient des deux côtés, chacune sous son
#: nom : ``_revenus_nets``, ``_minoration`` (deux fois), ``prime_pour_l_emploi``.
BRANCHES_RARES = {
    "les 10 % au-delà du plafond des 20 %, en 1973 et 1974": [
        {"quoi": "impot", "annee": annee, "unite": "monnaie", "indexation": "prix",
         "croissance": None, "foyer": _salarie(salaires)}
        for annee in (1973, 1974) for salaires in (400000.0, 900000.0, 2500000.0)],
    "la minoration de 1967 sans limite au-delà de trois parts": [
        {"quoi": "impot", "annee": 1967, "unite": "monnaie", "indexation": "prix",
         "croissance": None,
         "foyer": {"declarants": [{"salaires": salaires}, {}], "enfants": 3}}
        for salaires in (90000.0, 150000.0, 400000.0)],
    "la minoration entre 6 % et 3 %, de 1986 à 1992": [
        {"quoi": "impot", "annee": annee, "unite": "monnaie", "indexation": "prix",
         "croissance": None, "foyer": _salarie(float(salaires))}
        for annee in (1986, 1989, 1992) for salaires in range(180000, 330000, 3000)],
    "la prime pour l'emploi du couple dont un seul travaille, à sa sortie": [
        {"quoi": "impot", "annee": annee, "unite": "monnaie", "indexation": "prix",
         "croissance": None,
         "foyer": {"declarants": [{"salaires": float(salaires)}, {}], "enfants": 2}}
        for annee in (2002, 2005, 2010) for salaires in range(16000, 30000, 250)],
}


def _demandes_de_l_impot() -> list[dict]:
    demandes = _foyers_au_hasard(3000)
    for branche in BRANCHES_RARES.values():
        demandes.extend(branche)
    # Les corrections d'une seule année, que le hasard touche peu : le crédit
    # de 2008, la réduction de 2013, celle de 2016 à 2019.
    for annee in (2008, 2013, 2016, 2017, 2018, 2019):
        for salaires in range(12000, 42000, 1500):
            for foyer in (_salarie(float(salaires)),
                          {"declarants": [{"salaires": float(salaires)}, {"salaires": 9000.0}],
                           "enfants": 1}):
                demandes.append({"quoi": "impot", "annee": annee, "unite": "euro",
                                 "indexation": "prix", "croissance": None, "foyer": foyer})
    foyers = (
        _salarie(0.0), {"declarants": [{}, {}], "enfants": 2},
        {"declarants": [{}], "enfants": 1}, {"declarants": [{}], "enfants": 1, "veuf": True},
        {"declarants": [{"invalide": True, "age": 70}], "enfants": 3, "enfants_invalides": 1},
    )
    for annee in (1960, 1965, 1972, 1975, 1981, 1985, 1995, 2001, 2008, 2013, 2018, 2024, 2030):
        for foyer in foyers:
            for unite in ("euro", "monnaie"):
                for revenu in (0.0, 0.2, 1.0, 3.0):
                    seuil = BAREMES.lus(min(annee, BAREMES.derniere_annee)).seuils[-2]
                    demandes.append({"quoi": "revenu_imposable", "annee": annee, "foyer": foyer,
                                     "revenu": revenu * seuil, "unite": unite,
                                     "indexation": "salaire_moyen", "croissance": 0.03})
    independants = (
        {"declarants": [{"benefices": 30000.0, "artisan": True}]},
        {"declarants": [{"benefices": 30000.0, "categorie": "bnc"}]},
        {"declarants": [{"benefices": 30000.0}]},
        {"declarants": [{"benefices": 9000.0, "artisan": True},
                        {"benefices": 21000.0, "categorie": "bnc"}]},
        {"declarants": [{"benefices": -5000.0}, {"benefices": 52345.67, "categorie": "ba"}]},
    )
    for annee in range(1958, 1972):
        for foyer in independants:
            for unite in ("euro", "monnaie"):
                demandes.append({"quoi": "taxe", "annee": annee, "foyer": foyer, "unite": unite})
    for annee in (1960, 1978, 2000, 2001, BAREMES.derniere_annee, BAREMES.derniere_annee + 1,
                  BAREMES.derniere_annee + 30):
        for indexation in donnees_impot.INDEXATIONS:
            for par in ("parametres", "chronique"):
                demandes.append({"quoi": "parametres", "annee": annee, "indexation": indexation,
                                 "croissance": 0.021, "par": par})
    return demandes


def _refus_de_l_impot() -> list[dict]:
    seul = {"quoi": "impot", "annee": 2024, "unite": "euro", "indexation": "prix",
            "croissance": None, "foyer": _salarie(30000.0)}

    def foyer(**champs):
        return {**seul, "foyer": {**seul["foyer"], **champs}}

    def declarant(**champs):
        return {**seul, "foyer": {"declarants": [champs]}}

    return [
        declarant(regime="forfait"), declarant(categorie="bnc ", benefices=1.0),
        declarant(artisan=True, categorie="bnc"),
        foyer(declarants=[]), foyer(declarants=[{}, {}, {}]),
        foyer(declarants=[{}, {}], veuf=True), foyer(enfants=-1),
        foyer(enfants=1, enfants_invalides=2), foyer(enfants_invalides=-1),
        foyer(taxe_complementaire_de_l_annee_precedente=-1.0),
        {**seul, "unite": "franc"}, {**seul, "annee": BAREMES.premiere_annee - 1},
        {**seul, "annee": BAREMES.derniere_annee + 1},
        {**seul, "annee": BAREMES.derniere_annee + 1, "croissance": 0.02,
         "indexation": "pib"},
        {"quoi": "taxe", "annee": 1964, "foyer": _salarie(0.0), "unite": "franc"},
        {"quoi": "revenu_imposable", "annee": 2024, "foyer": _salarie(0.0), "revenu": 1.0,
         "unite": "ecu", "indexation": "prix", "croissance": None},
        {"quoi": "parametres", "annee": 1959, "indexation": "prix", "croissance": None,
         "par": "parametres"},
        {"quoi": "parametres", "annee": BAREMES.derniere_annee + 5, "indexation": "prix",
         "croissance": None, "par": "chronique"},
    ]


# -- la confrontation --------------------------------------------------------


#: Le seul cas dont le portage change à la relecture : une distribution écrite
#: à la main, dont la tranche ouverte n'a pas de borne supérieure du tout.
SANS_BORNE = {
    "quoi": "cout_brut", "effectif": 1e6, "plancher": 1500.0, "facteur": 1.0,
    "forme": [1.0, 1.0],
    "tranches": [{"borneInferieure": 0.0, "borneSuperieure": 1000.0, "part": 0.5},
                 {"borneInferieure": 1000.0, "part": 0.5}],
}


@pytest.fixture(scope="module")
def les_deux():
    """Chaque famille de demandes, ce que le Python en rend et ce que le
    portage en rend."""
    if shutil.which("node") is None:
        pytest.skip("node absent : le portage JavaScript n'est pas vérifiable ici")
    familles = {
        "garantie": _demandes_de_la_garantie(), "refus_garantie": _refus_de_la_garantie(),
        "impot": _demandes_de_l_impot(), "refus_impot": _refus_de_l_impot(),
        "constantes": [{"quoi": "constantes"}], "sans_borne": [SANS_BORNE],
    }
    toutes = [demande for famille in familles.values() for demande in famille]
    execution = subprocess.run(
        ["node", "--input-type=module", "-e", SCRIPT], cwd=RACINE_PROJET,
        input=json.dumps(toutes), capture_output=True, text=True, encoding="utf-8", check=False)
    assert execution.returncode == 0, execution.stderr[-2000:]
    portage = iter(json.loads(execution.stdout))
    return {nom: [(demande, None if demande["quoi"] == "cout_brut" else _python(demande),
                   next(portage)) for demande in famille]
            for nom, famille in familles.items()}


def _differences(famille) -> list[str]:
    """Les demandes que les deux jumeaux ne rendent pas identiques, au bit."""
    return [f"{json.dumps(demande, ensure_ascii=False)[:300]} : Python {str(python)[:300]}, "
            f"portage {str(portage)[:300]}"
            for demande, python, portage in famille if python != portage]


def test_la_garantie_d_une_population_se_retrouve_en_javascript_au_bit(les_deux):
    """Le barème d'une personne, le manque moyen d'une tranche, le coût sur
    la distribution, d'un facteur ou de deux, sous un plancher ou deux, la
    pension moyenne et les deux facteurs : un millier de demandes, six
    nombres chacune pour un coût, les mêmes des deux côtés."""
    famille = les_deux["garantie"]
    assert len(famille) > 1000
    assert all("valeur" in python for _, python, _ in famille)
    ecarts = _differences(famille)
    assert not ecarts, f"{len(ecarts)} écarts : " + " ; ".join(ecarts[:3])


def test_la_confrontation_de_la_garantie_a_un_objet(les_deux):
    """Elle chiffre des bénéficiaires et un coût sous chaque forme, et le
    plancher majoré de qui vit seul y déplace le coût."""
    couts = [(d, python["valeur"]) for d, python, _ in les_deux["garantie"]
             if d["quoi"] in ("cout", "par_sexe")]
    for forme in FORMES:
        assert any(d["forme"] == forme and 0.0 < v[2] < 1.0 and v[5] > 0.0 for d, v in couts)
    par_sexe = {(tuple(d["forme"]), d["rapport"], d["facteur"], d["plancher_majore"],
                 json.dumps(d["part_seule"])): v[5] for d, v in couts if d["quoi"] == "par_sexe"}
    sans = par_sexe[(1.0, 1.0), 0.85, 0.8, None, "null"]
    assert par_sexe[(1.0, 1.0), 0.85, 0.8, 1050.0, json.dumps({"F": 0.55, "H": 0.3})] > sans
    # Sans plancher majoré, la part de qui vit seul ne compte pas.
    assert par_sexe[(1.0, 1.0), 0.85, 0.8, None, json.dumps({"F": 0.5, "H": 0.5})] == sans


def test_les_deux_garanties_refusent_les_memes_demandes(les_deux):
    """Un facteur nul ou négatif, une forme qui n'est pas un barème dégressif,
    un rapport ou des pensions moyennes qui ne sont pas positifs : le même
    refus, du même message."""
    famille = les_deux["refus_garantie"]
    assert all("refus" in python for _, python, _ in famille), [p for _, p, _ in famille]
    assert not _differences(famille)


def test_une_tranche_sans_borne_superieure_est_la_tranche_ouverte(les_deux):
    """``coutGarantie`` tient pour ouverte la tranche qui n'a pas de borne
    supérieure, comme ``pensionMoyenne``, ``manqueMoyen`` et ``partSous``
    (``distribution.js``) le font déjà, au lieu de rendre NaN.

    Posé à la main, sous un plancher différentiel de 1 500 € : la moitié des
    retraités, répartie de 0 à 1 000 €, reçoit en moyenne 1 500 − 500 =
    1 000 € ; l'autre, masse ponctuelle à 1 000 €, en reçoit 500. Tous sont
    servis, de 750 € en moyenne : pour un million de retraités, 750 × 12 =
    9 000 millions d'euros par an."""
    [(_, _, portage)] = les_deux["sans_borne"]
    assert portage == {"valeur": [1500.0, 1.0, 1.0, 1e6, 750.0, 9000.0]}


def test_l_impot_se_retrouve_en_javascript_au_bit(les_deux):
    """Trois mille foyers tirés d'une graine fixe, de 1960 à vingt ans de
    projection, l'impôt d'un revenu imposable donné, la taxe complémentaire
    seule, de 1958 à 1971, les paramètres lus et projetés, d'un coup ou année
    après année : chaque étape, à l'unité du dernier chiffre."""
    famille = les_deux["impot"]
    assert all("valeur" in python for _, python, _ in famille), next(
        (d, p) for d, p, _ in famille if "valeur" not in p)
    ecarts = _differences(famille)
    assert not ecarts, f"{len(ecarts)} écarts : " + " ; ".join(ecarts[:3])


def _impots(les_deux, nom: str) -> list[dict]:
    branche = BRANCHES_RARES[nom]
    return [python["valeur"] for demande, python, _ in les_deux["impot"] if demande in branche]


def test_la_confrontation_de_l_impot_a_un_objet(les_deux):
    """Chacune des quatre branches rares joue au moins une fois, et les
    foyers confrontés touchent chaque étape de l'impôt."""
    au_hasard = [python["valeur"] for d, python, _ in les_deux["impot"] if d["quoi"] == "impot"]
    for etape in ("plafonnement", "reduction_complementaire", "reduction_des_salaires", "decote",
                  "reduction_sous_condition_de_revenus", "minoration_exceptionnelle",
                  "majoration_exceptionnelle", "reduction_exceptionnelle",
                  "reduction_proportionnelle", "prime_pour_l_emploi", "credit_exceptionnel",
                  "abattement_vingt_pour_cent", "abattement_age_invalidite",
                  "abattement_adherents", "majoration_des_benefices", "exonere",
                  "taxe_complementaire", "taxe_complementaire_deduite"):
        assert any(impot[etape] for impot in au_hasard), etape
    assert any(impot["remarques"] and impot["fiabilite"] == "estimee" for impot in au_hasard)

    # 1973 et 1974 : l'abattement dépasse 20 % du plafond, de 10 % du surplus.
    for impot in _impots(les_deux, "les 10 % au-delà du plafond des 20 %, en 1973 et 1974"):
        plafond = BAREMES.lus(impot["annee"])["deductions"]["vingt_pour_cent_plafond"]
        assert impot["abattement_vingt_pour_cent"] > 0.20 * plafond
    # 1967 : quatre parts, un revenu au-delà du dernier palier, et la minoration reste.
    minores = _impots(les_deux, "la minoration de 1967 sans limite au-delà de trois parts")
    assert all(i["parts"] > 3 and i["revenu_net_imposable"] > 55000
               and i["minoration_exceptionnelle"] > 0 for i in minores)
    # 1986 à 1992 : une cotisation entre le quatrième et le cinquième seuil.
    entre = 0
    for impot in _impots(les_deux, "la minoration entre 6 % et 3 %, de 1986 à 1992"):
        m = BAREMES.lus(impot["annee"])["minorations_exceptionnelles"]
        avant = impot["impot_brut"] - impot["decote"]
        entre += m["seuil_impot_4"] < avant <= m["seuil_impot_5"]
    assert entre >= 3
    # La prime du couple dont un seul travaille, dans sa sortie dégressive.
    sorties = 0
    for impot in _impots(
            les_deux, "la prime pour l'emploi du couple dont un seul travaille, à sa sortie"):
        p = BAREMES.lus(impot["annee"])["prime_pour_l_emploi"]
        [revenu, _] = impot["revenus_d_activite"]
        sorties += (p["revenu_taux_plein_mono_emploi"] < revenu < p["revenu_maximum_mono_emploi"]
                    and impot["prime_pour_l_emploi"] > 0)
    assert sorties >= 3


def test_les_deux_impots_refusent_les_memes_demandes(les_deux):
    """Un déclarant ou un foyer mal formé, une unité ou une indexation
    inconnue, une année sans barème, une projection sans croissance : le même
    refus, du même message."""
    famille = les_deux["refus_impot"]
    assert all("refus" in python for _, python, _ in famille), [
        (d, p) for d, p, _ in famille if "refus" not in p]
    assert not _differences(famille)


def test_les_constantes_de_l_impot_sont_les_memes_des_deux_cotes(les_deux):
    """Les années, les taux, les seuils et les listes que les deux modules
    écrivent chacun de son côté, ``HORS_CHAMP`` compris."""
    [(_, python, portage)] = les_deux["constantes"]
    python, portage = python["valeur"], portage["valeur"]
    assert len(python) > 30
    assert sorted(python) == sorted(portage)
    assert not [nom for nom in python if python[nom] != portage[nom]]
