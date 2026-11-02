#!/usr/bin/env python3
"""La proposition à 18 %, PROSPECTIVE : le stock intact, les droits acquis figés.

    python scripts/proposition_prospective.py
    python scripts/proposition_prospective.py --json p.json

CE QU'ELLE EST
--------------
Le scénario 6 du dépôt est rétroactif : il recalcule toute carrière depuis
1941 comme un compte notionnel, pensions déjà servies comprises, puis
prélève 18 % à compter de la bascule. C'est ce qui le rend le plus exposé
devant le juge — les pensions liquidées sont des situations légalement
acquises — et le plus attaquable au Parlement. La variante chiffrée ici
garde tout le reste de la proposition et change ce seul point : elle est le
scénario 5 à 18 %. Une retraite déjà liquidée à la bascule ne bouge pas ;
un actif voit ses droits d'avant la bascule figés, débarrassés des
avantages non contributifs, convertis en capital à l'âge de référence ; son
compte est alimenté à 18 % ensuite ; le pilier capitalisé et la garantie
vieillesse s'ajoutent comme dans le scénario 6, la garantie valant aussi
pour le stock, puisque le programme la relève.

CE QUE LA PAGE COÛT EN FAIT
---------------------------
Le scénario 6 prend ici la place du sixième système, et la page le traite
comme une réforme prospective : ses courbes sont celles du système actuel
jusqu'à la bascule, à l'euro près ; le stock garde les prix ; la réversion
est servie avant la bascule et plus après, comme pour les scénarios 3 et 5.
Sa recette est celle du programme, inchangée : 18 % sur l'assiette des
revenus d'activité, sans impôts affectés, subventions ni contribution
d'équilibre. La garantie reste financée par l'impôt et hors du solde ; son
coût est imprimé à part.

CE QU'IL EMPRUNTE
-----------------
La variante est un univers, la pile du scénario 5 et les couches de la
proposition (``data/reference/variantes/``) : le simulateur de l'étude la
calcule à la place du scénario 6, et le pont la passe au portage dans la
demande, qui simule la grille du coût et les cas types (action 161). L'étude
ne remplace que la liste ``cout.CLES_PROSPECTIVES``, une fonction du coût,
étendue au sixième système le temps du calcul ; tout est rendu à la sortie.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retraite_notionnelle import cout as C  # noqa: E402
from retraite_notionnelle import memoire, pont  # noqa: E402
from retraite_notionnelle.castypes import CAS_TYPES, cases_de_la_grille  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.donnees.assiette import AssietteActivite  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.equilibre import ComptesRetraite  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.noyau import univers  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

LIBERAL = "notionnel_liberal"
#: La variante, le scénario 5 à 18 % : son univers, sous
#: ``data/reference/variantes/``, que l'étude calcule à la place du scénario 6.
PROSPECTIVE = "notionnel_liberal_prospectif"
ANNEES_AFFICHEES: tuple[int, ...] = (2026, 2030, 2040, 2050, 2060, 2070)
CAS_AFFICHES: tuple[str, ...] = (
    "smic_carriere_complete", "salaire_moyen", "cadre", "fonctionnaire_sedentaire",
    "fonctionnaire_actif", "artisan", "profession_liberale",
)
GENERATIONS_AFFICHEES: tuple[int, ...] = (1965, 1975, 1985, 2000)


def simulateur(parametres: Parametres) -> Simulateur:
    """Le simulateur de l'étude : la proposition prospective à la place du
    scénario 6, lue sous les données de ``parametres``. Le pont passe son
    calcul au portage dans la demande (``Simulateur.univers_de_la_demande``)."""
    reference = parametres.racine_donnees / "reference"
    variante = univers.charger(reference / "variantes", reference / "couches",
                               reference / "regles")[PROSPECTIVE]
    return Simulateur(parametres, variantes={LIBERAL: variante})


class PropositionProspective:
    """Le temps d'un calcul : le sixième système compté parmi les réformes
    prospectives du coût (``cout.CLES_PROSPECTIVES``)."""

    def __init__(self) -> None:
        self._sauvegarde: frozenset[str] = frozenset()

    def __enter__(self) -> "PropositionProspective":
        # Le contexte remplace une fonction du coût, que la mémoire des calculs,
        # qui ne connaît que le modèle intact, ne doit pas garder : elle se tait
        # (``memoire.modele_modifie``). Le moteur, il n'y touche pas.
        self._memoire = memoire.modele_modifie()
        self._memoire.__enter__()
        self._sauvegarde = C.CLES_PROSPECTIVES
        C.CLES_PROSPECTIVES = C.CLES_PROSPECTIVES | {LIBERAL}
        return self

    def __exit__(self, *exc) -> None:
        C.CLES_PROSPECTIVES = self._sauvegarde
        self._memoire.__exit__(None, None, None)


@dataclass
class Lecture:
    soldes: dict[int, float]
    ressources: dict[int, float]
    depenses: dict[int, float]
    coefficients: dict[int, float]
    solde_moyen: float
    premiere_annee_equilibree: int | None
    dette_horizon: float


@dataclass
class Resultat:
    variante: str
    lectures: dict[str, Lecture]
    #: Coût de la garantie vieillesse, en part de PIB, par année projetée.
    garantie: dict[int, float]
    #: Écart de pension au système actuel, par (cas type, génération) et système.
    ecarts: dict[str, dict[str, float]]
    cout: C.Cout | None = field(default=None, repr=False)


def cout(parametres: Parametres) -> C.Cout:
    """Le coût agrégé sous la proposition prospective, gardé par la mémoire des
    calculs (``retraite_notionnelle/memoire.py``).

    La mémoire se tait sous le contexte : il s'ouvre donc DANS le calcul que la
    clé nomme, et le chiffrage budgétaire le partage avec ce script. Le solde,
    lui, se lit paresseusement : il se lit dans le contexte (``calculer``).
    """
    def calcul() -> C.Cout:
        racine = parametres.racine_donnees
        with PropositionProspective():
            return C.calculer_cout(
                simulateur(parametres), DepensesRetraite(racine), Population(racine),
                ComptesRetraite(racine), assiette=AssietteActivite(racine))

    return memoire.memoriser_pour(parametres, ("cout_prospectif", parametres), calcul)


def ecarts_des_cas_types(etude: Simulateur) -> dict[str, dict[str, float]]:
    """L'écart de pension de chaque système au système actuel, par cas type et
    génération affichés, sous les univers du simulateur ``etude`` : le
    portage date les cas types et les simule, la variante dans la demande
    (action 161), sous les réglages de référence, les seuls que le pont leur
    applique."""
    racine = etude.parametres.racine_donnees
    if etude.parametres != Parametres(racine_donnees=racine):
        raise ValueError("les cas types de l'étude se simulent sous les réglages de référence")
    paquet = pont.paquet_des_donnees(racine)
    options, _ = cases_de_la_grille(
        etude, tuple(c for c in CAS_TYPES if c.code in CAS_AFFICHES), GENERATIONS_AFFICHEES,
        paquet=paquet)
    compares = [scenario for scenario, _ in C.SCENARIOS if scenario != "actuel"]
    lus, _ = pont.carrieres([{"cle": f"{code}|{generation}", "options": options[code, generation]}
                             for code, generation in sorted(options)], compares, paquet,
                            univers=etude.univers_de_la_demande)
    return {f"{code}|{generation}": lus[f"{code}|{generation}"]["ecarts"]
            for code, generation in sorted(options) if f"{code}|{generation}" in lus}


def calculer(prospective: bool, parametres: Parametres) -> Resultat:
    """Les lectures d'une variante, sur les données du dépôt."""
    agrege = cout(parametres) if prospective else memoire.cout(parametres)
    ecarts = ecarts_des_cas_types(simulateur(parametres) if prospective
                                  else Simulateur(parametres))
    contexte = PropositionProspective() if prospective else None
    if contexte is not None:
        contexte.__enter__()
    try:
        # Le solde se lit paresseusement, et sa règle de réversion regarde
        # ``CLES_PROSPECTIVES`` au moment de la lecture : on lit donc DANS le
        # contexte, sans quoi les années d'avant la bascule perdraient la
        # réversion que la réforme prospective y sert encore.
        solde = agrege.solde
        lectures = {
            scenario: Lecture(
                soldes={l.annee: l.solde(scenario) for l in solde.projetees()},
                ressources={l.annee: l.ressources_de(scenario) for l in solde.projetees()},
                depenses={l.annee: l.depense(scenario) for l in solde.projetees()},
                coefficients={l.annee: l.coefficient(scenario) for l in solde.projetees()},
                solde_moyen=solde.solde_moyen(scenario, 2026, C.HORIZON),
                premiere_annee_equilibree=solde.premiere_annee_equilibree(scenario),
                dette_horizon=agrege.dette.horizon(scenario),
            )
            for scenario, _ in C.SCENARIOS
        }
        garantie = {l.annee: l.part_pib(C.COMPOSANTE_GARANTIE)
                    for l in agrege.avenir.projetees() if l.pib > 0}
    finally:
        if contexte is not None:
            contexte.__exit__(None, None, None)
    return Resultat("prospective" if prospective else "retroactive", lectures, garantie,
                    ecarts, agrege)


def tableau(reference: Resultat, prospective: Resultat,
            annees: tuple[int, ...] = ANNEES_AFFICHEES) -> str:
    entete = (f"{'système':<32}" + "".join(f"{a:>8}" for a in annees)
              + f"{'moy.':>8}{'équil.':>8}{'dette70':>9}{'coef70':>8}")
    lignes = ["Solde en points de PIB ; dette : stock accumulé en 2070 ; coefficient d'équilibre en 2070",
              "", entete, "-" * len(entete)]
    rangees = [
        ("1 système actuel", reference.lectures["actuel"]),
        ("5 prospectif, totale, 25,83 %", reference.lectures["notionnel_prospectif_employeur"]),
        ("6 proposition rétroactive, 18 %", reference.lectures[LIBERAL]),
        ("6 proposition PROSPECTIVE, 18 %", prospective.lectures[LIBERAL]),
    ]
    for libelle, lecture in rangees:
        equilibre = lecture.premiere_annee_equilibree
        lignes.append(
            f"{libelle:<32}" + "".join(f"{lecture.soldes[a] * 100:>+8.2f}" for a in annees)
            + f"{lecture.solde_moyen * 100:>+8.2f}{str(equilibre) if equilibre else '—':>8}"
            + f"{lecture.dette_horizon * 100:>+9.0f}{lecture.coefficients[C.HORIZON]:>8.2f}"
        )
    lignes += ["", "Garantie vieillesse, financée par l'impôt, hors du solde, en points de PIB", ""]
    lignes.append(f"{'':<32}" + "".join(f"{a:>8}" for a in annees))
    for libelle, resultat in (("6 rétroactive", reference), ("6 prospective", prospective)):
        lignes.append(f"{libelle:<32}" + "".join(
            f"{resultat.garantie.get(a, 0.0) * 100:>8.2f}" for a in annees))
    lignes += ["", "Écart de pension au système actuel, cas types", ""]
    lignes.append(f"{'cas type / génération':<34}{'5':>9}{'6 rétro':>9}{'6 prosp':>9}")
    for cle, ecarts in reference.ecarts.items():
        lignes.append(
            f"{cle.replace('|', ' / '):<34}{ecarts['notionnel_prospectif_employeur']:>+9.1%}"
            f"{ecarts[LIBERAL]:>+9.1%}{prospective.ecarts[cle][LIBERAL]:>+9.1%}"
        )
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    analyseur.add_argument("--json", type=Path)
    arguments = analyseur.parse_args(argv)
    parametres = Parametres()
    reference = calculer(False, parametres)
    prospective = calculer(True, parametres)
    print(tableau(reference, prospective))
    if arguments.json:
        arguments.json.write_text(json.dumps({
            r.variante: {"lectures": {s: dataclasses.asdict(l) for s, l in r.lectures.items()},
                         "garantie": r.garantie, "ecarts": r.ecarts}
            for r in (reference, prospective)}, indent=1, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
