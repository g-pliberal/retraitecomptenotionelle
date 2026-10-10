#!/usr/bin/env python3
"""L'impôt sur le revenu de quelques foyers, de 2002 à 2025, par OpenFisca-France.

    pip install OpenFisca-France          # à part : AGPL, ses sorties seules entrent
    python scripts/fetch/openfisca_impot_revenu.py

À quoi il sert. Le calcul de l'impôt d'un foyer
(``retraite_notionnelle/impot_revenu.py``, action 138, étape 5) se vérifie
d'abord sur les exemples que l'administration publie (brochure pratique,
BOFiP). OpenFisca-France en est une seconde implémentation, écrite par
d'autres, qui couvre chaque année depuis 2002 : un désaccord ne désigne pas
d'office le coupable, il se tranche par le texte. Le registre des modèles
(``data/reference/referents.yaml``, ``openfisca_france``) le range en
``executer_a_part`` : sa licence ne permet que d'en faire entrer les sorties.

Le fichier produit, ``tests/temoins/impot_revenu_openfisca.json``, est
VERSIONNÉ : ``tests/test_impot_revenu.py`` rejoue la confrontation sans
installer OpenFisca.

Les foyers. Des salariés, des retraités, des couples, un parent isolé, un
veuf, des enfants à charge de dix ans : ce que le module calcule, et rien
d'autre. Les salaires et les pensions sont IMPOSABLES (nets de la CSG
déductible) et constants en euros d'une année à l'autre, l'âge est celui du
31 décembre de chaque année ; un salarié travaille à temps plein, toute
l'année (``ppe_tp_sa``), pour la prime pour l'emploi. Les grandeurs relevées
sont celles qu'OpenFisca nomme ainsi, dans sa propre convention de signe
(``impot_revenu_restant_a_payer`` est négatif quand le foyer paie) ; une
grandeur qu'il ne sait pas calculer une année, faute d'un paramètre, vaut
``null`` (les réductions d'impôt de 2002, que ``iai`` déroule toutes).
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

SORTIE = Path(__file__).resolve().parents[2] / "tests" / "temoins" / "impot_revenu_openfisca.json"

ANNEES = tuple(range(2002, 2026))

#: Les foyers : chaque déclarant (salaire, pension, âge au 31 décembre,
#: invalide), les enfants à charge, la situation, et la case T du parent isolé.
FOYERS: tuple[dict, ...] = (
    {"code": "celibataire_bas_salaire", "declarants": [{"salaire": 11000}]},
    {"code": "celibataire_salaire_moyen", "declarants": [{"salaire": 30000}]},
    {"code": "celibataire_haut_salaire", "declarants": [{"salaire": 90000}]},
    {"code": "couple_deux_salaires_deux_enfants",
     "declarants": [{"salaire": 32000}, {"salaire": 21000}], "enfants": 2, "statut": "marie"},
    {"code": "couple_un_salaire", "declarants": [{"salaire": 15000}, {}], "statut": "marie"},
    {"code": "couple_haut_salaire_trois_enfants",
     "declarants": [{"salaire": 120000}, {}], "enfants": 3, "statut": "marie"},
    {"code": "parent_isole_un_enfant", "declarants": [{"salaire": 24000}], "enfants": 1,
     "case_t": True},
    {"code": "parent_isole_haut_salaire_deux_enfants", "declarants": [{"salaire": 70000}],
     "enfants": 2, "case_t": True},
    {"code": "veuf_un_enfant", "declarants": [{"salaire": 45000}], "enfants": 1,
     "statut": "veuf"},
    {"code": "retraite_seul_petite_pension", "declarants": [{"pension": 13000, "age": 70}]},
    {"code": "retraite_seul_pension_moyenne", "declarants": [{"pension": 24000, "age": 72}]},
    {"code": "couple_retraites", "declarants": [{"pension": 26000, "age": 70},
                                                {"pension": 9000, "age": 68}], "statut": "marie"},
    {"code": "couple_retraites_aises", "declarants": [{"pension": 60000, "age": 75},
                                                      {"pension": 30000, "age": 74}],
     "statut": "marie"},
    {"code": "salarie_et_retraite", "declarants": [{"salaire": 28000, "age": 60},
                                                   {"pension": 16000, "age": 66}],
     "statut": "marie"},
    {"code": "retraite_invalide", "declarants": [{"pension": 18000, "age": 62, "invalide": True}]},
)

#: Grandeurs relevées, au foyer fiscal.
GRANDEURS = ("nbptr", "rng", "abat_spe", "rni", "rfr", "ir_plaf_qf", "decote", "ip_net",
             "reduction_impot_exceptionnelle", "iai", "ppe", "impot_revenu_restant_a_payer")


def situation(annee: int) -> dict:
    """Une simulation par année : tous les foyers côte à côte."""
    individus, foyers, menages, familles = {}, {}, {}, {}
    for foyer in FOYERS:
        declarants = []
        for rang, d in enumerate(foyer["declarants"]):
            nom = f"{foyer['code']}_{rang}"
            age = d.get("age", 40)
            individus[nom] = {
                "date_naissance": {"ETERNITY": date(annee - age, 7, 1).isoformat()},
                "salaire_imposable": {str(annee): float(d.get("salaire", 0))},
                "retraite_imposable": {str(annee): float(d.get("pension", 0))},
                "statut_marital": {str(annee): foyer.get("statut", "celibataire")},
                "invalidite": {str(annee): bool(d.get("invalide", False))},
                "ppe_tp_sa": {str(annee): bool(d.get("salaire"))},
            }
            declarants.append(nom)
        enfants = []
        for rang in range(foyer.get("enfants", 0)):
            nom = f"{foyer['code']}_enfant_{rang}"
            individus[nom] = {"date_naissance": {"ETERNITY": date(annee - 10, 7, 1).isoformat()}}
            enfants.append(nom)
        foyers[foyer["code"]] = {"declarants": declarants, "personnes_a_charge": enfants,
                                 "caseT": {str(annee): bool(foyer.get("case_t", False))},
                                 "caseP": {str(annee): any(d.get("invalide")
                                                           for d in foyer["declarants"])}}
        menages[foyer["code"]] = {"personne_de_reference": declarants[:1],
                                  "conjoint": declarants[1:], "enfants": enfants}
        familles[foyer["code"]] = {"parents": declarants, "enfants": enfants}
    return {"individus": individus, "foyers_fiscaux": foyers, "menages": menages,
            "familles": familles}


def calculer(tbs, annee: int) -> dict[str, dict[str, float]]:
    from openfisca_core.simulation_builder import SimulationBuilder

    from openfisca_core.errors import ParameterNotFoundError

    valeurs = {}
    for grandeur in GRANDEURS:
        # Une simulation par grandeur : une grandeur qu'OpenFisca ne sait pas
        # calculer une année (un paramètre qui y manque) ne prive pas les autres.
        simulation = SimulationBuilder().build_from_entities(tbs, situation(annee))
        try:
            valeurs[grandeur] = simulation.calculate(grandeur, str(annee))
        except ParameterNotFoundError:
            valeurs[grandeur] = None
    return {foyer["code"]: {grandeur: (None if valeurs[grandeur] is None
                                       else round(float(valeurs[grandeur][rang]), 2))
                            for grandeur in GRANDEURS}
            for rang, foyer in enumerate(FOYERS)}


def ecrire(temoin: dict) -> str:
    """Le témoin, une ligne par foyer et par année : les grandeurs dans l'ordre
    de ``grandeurs``."""
    lignes = ["{"]
    for cle in ("source", "version", "recupere_le", "avertissement", "grandeurs"):
        lignes.append(f'  {json.dumps(cle)}: {json.dumps(temoin[cle], ensure_ascii=False)},')
    lignes.append('  "foyers": {')
    foyers = list(temoin["foyers"].items())
    for rang, (code, contenu) in enumerate(foyers):
        lignes.append(f'    {json.dumps(code)}: {{')
        lignes.append(f'      "foyer": {json.dumps(contenu["foyer"], ensure_ascii=False)},')
        lignes.append('      "annees": {')
        annees = list(contenu["annees"].items())
        lignes += [f'        {json.dumps(annee)}: '
                   f'{json.dumps([valeurs[g] for g in temoin["grandeurs"]])}'
                   + ("," if k + 1 < len(annees) else "")
                   for k, (annee, valeurs) in enumerate(annees)]
        lignes.append("      }")
        lignes.append("    }" + ("," if rang + 1 < len(foyers) else ""))
    lignes += ["  }", "}"]
    return "\n".join(lignes) + "\n"


def main() -> int:
    try:
        from openfisca_france import FranceTaxBenefitSystem
        from importlib.metadata import version
    except ImportError:
        print("OpenFisca-France n'est pas installé : pip install OpenFisca-France", file=sys.stderr)
        return 1
    tbs = FranceTaxBenefitSystem()
    par_annee = {annee: calculer(tbs, annee) for annee in ANNEES}
    temoin = {
        "source": "OpenFisca-France",
        "version": version("OpenFisca-France"),
        "recupere_le": date.today().isoformat(),
        "avertissement": ("Seconde implémentation, pas une source officielle : un désaccord se "
                          "tranche par le texte."),
        "grandeurs": list(GRANDEURS),
        "foyers": {foyer["code"]: {"foyer": foyer,
                                   "annees": {str(a): par_annee[a][foyer["code"]] for a in ANNEES}}
                   for foyer in FOYERS},
    }
    SORTIE.write_text(ecrire(temoin), encoding="utf-8")
    print(f"{SORTIE} : {len(FOYERS)} foyers, {len(ANNEES)} années")
    return 0


if __name__ == "__main__":
    sys.exit(main())
