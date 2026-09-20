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
``ScenarioNotionnel.liberal``, remplacé le temps du calcul par la même
méthode bâtie sur ``prospectif`` au lieu de ``retroactif``, et la liste
``cout.CLES_PROSPECTIVES``, étendue au sixième système. Tout est rendu à la
sortie.
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
from retraite_notionnelle.castypes import CAS_TYPES, calculer_cas_types  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.donnees.assiette import AssietteActivite  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.equilibre import ComptesRetraite  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.scenarios.notionnel import ScenarioNotionnel  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

LIBERAL = "notionnel_liberal"
ANNEES_AFFICHEES: tuple[int, ...] = (2026, 2030, 2040, 2050, 2060, 2070)
CAS_AFFICHES: tuple[str, ...] = (
    "smic_carriere_complete", "salaire_moyen", "cadre", "fonctionnaire_sedentaire",
    "fonctionnaire_actif", "artisan", "profession_liberale",
)
GENERATIONS_AFFICHEES: tuple[int, ...] = (1965, 1975, 1985, 2000)


class PropositionProspective:
    """Le temps d'un calcul : le scénario 6 bâti sur ``prospectif``."""

    def __init__(self) -> None:
        self._sauvegarde: dict[str, object] = {}

    @staticmethod
    def _liberal(original):
        def liberal(scenario, carriere, regime_fusionne=None,
                    libelle="Comptes notionnels à compter de la bascule, 18 % "
                            "et garantie vieillesse"):
            if regime_fusionne is None:
                raise ValueError("la proposition prospective demande le régime unique")
            resultat = scenario.prospectif(carriere, regime_fusionne, libelle=libelle)
            # La suite est celle de ``liberal`` : le pilier d'abord, la
            # garantie ensuite, qui regarde les deux.
            resultat.capitalisation = scenario._pilier_capitalise(carriere, resultat)
            rente = (resultat.capitalisation.rente_annuelle
                     if resultat.capitalisation is not None else 0.0)
            garantie = scenario._garantie_vieillesse(carriere, resultat.pension_annuelle, rente)
            if garantie.servie_a_la_liquidation:
                resultat.pension_annuelle += garantie.complement
            resultat.garantie_vieillesse = garantie
            return resultat
        return liberal

    def __enter__(self) -> "PropositionProspective":
        self._sauvegarde = {
            "liberal": ScenarioNotionnel.liberal,
            "CLES_PROSPECTIVES": C.CLES_PROSPECTIVES,
        }
        ScenarioNotionnel.liberal = self._liberal(ScenarioNotionnel.liberal)
        C.CLES_PROSPECTIVES = C.CLES_PROSPECTIVES | {LIBERAL}
        return self

    def __exit__(self, *exc) -> None:
        ScenarioNotionnel.liberal = self._sauvegarde["liberal"]
        C.CLES_PROSPECTIVES = self._sauvegarde["CLES_PROSPECTIVES"]


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


def calculer(prospective: bool, parametres: Parametres, depenses: DepensesRetraite,
             population: Population, comptes: ComptesRetraite,
             assiette: AssietteActivite) -> Resultat:
    simulateur = Simulateur(parametres)
    contexte = PropositionProspective() if prospective else None
    if contexte is not None:
        contexte.__enter__()
    try:
        cout = C.calculer_cout(simulateur, depenses, population, comptes, assiette=assiette)
        grille = calculer_cas_types(
            simulateur, tuple(c for c in CAS_TYPES if c.code in CAS_AFFICHES),
            GENERATIONS_AFFICHEES,
        )
        # Le solde se lit paresseusement, et sa règle de réversion regarde
        # ``CLES_PROSPECTIVES`` au moment de la lecture : on lit donc DANS le
        # contexte, sans quoi les années d'avant la bascule perdraient la
        # réversion que la réforme prospective y sert encore.
        solde = cout.solde
        lectures = {
            scenario: Lecture(
                soldes={l.annee: l.solde(scenario) for l in solde.projetees()},
                ressources={l.annee: l.ressources_de(scenario) for l in solde.projetees()},
                depenses={l.annee: l.depense(scenario) for l in solde.projetees()},
                coefficients={l.annee: l.coefficient(scenario) for l in solde.projetees()},
                solde_moyen=solde.solde_moyen(scenario, 2026, C.HORIZON),
                premiere_annee_equilibree=solde.premiere_annee_equilibree(scenario),
                dette_horizon=cout.dette.horizon(scenario),
            )
            for scenario, _ in C.SCENARIOS
        }
        garantie = {l.annee: l.part_pib(C.COMPOSANTE_GARANTIE)
                    for l in cout.avenir.projetees() if l.pib > 0}
        ecarts = {
            f"{code}|{generation}": {scenario: comparaison.variation(scenario)
                                     for scenario, _ in C.SCENARIOS if scenario != "actuel"}
            for (code, generation), comparaison in sorted(grille.resultats.items())
        }
    finally:
        if contexte is not None:
            contexte.__exit__(None, None, None)
    return Resultat("prospective" if prospective else "retroactive", lectures, garantie,
                    ecarts, cout)


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
    racine = parametres.racine_donnees
    donnees = (DepensesRetraite(racine), Population(racine), ComptesRetraite(racine),
               AssietteActivite(racine))
    reference = calculer(False, parametres, *donnees)
    prospective = calculer(True, parametres, *donnees)
    print(tableau(reference, prospective))
    if arguments.json:
        arguments.json.write_text(json.dumps({
            r.variante: {"lectures": {s: dataclasses.asdict(l) for s, l in r.lectures.items()},
                         "garantie": r.garantie, "ecarts": r.ecarts}
            for r in (reference, prospective)}, indent=1, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
