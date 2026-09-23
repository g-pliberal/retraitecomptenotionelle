#!/usr/bin/env python3
"""Ce que coûte de ne pas faire payer l'âge à qui est parti à l'âge légal de sa génération.

    python scripts/stock_age_legal.py            # les trois variantes, solde et cas types
    python scripts/stock_age_legal.py --json s.json

LA QUESTION
-----------
Les scénarios rétroactifs — 2, 4 et 6, la proposition — recalculent les
pensions déjà servies comme des comptes notionnels : capital cotisé, divisé
par le diviseur de l'âge de départ. Ils ne lisent AUCUN âge de référence
(``docs/methodologie.md`` §4) ; ce qui fait baisser la pension d'un départ
précoce est le diviseur lui-même, plus long à 60 ans qu'à 65. Devant le
juge constitutionnel, c'est une atteinte aux effets légitimement attendus
d'une situation acquise : l'assuré parti à 60 ans en 2010 est parti à l'âge
que sa loi lui ouvrait, et la réforme lui compte après coup quatre années
de rente en plus. Ce script chiffre la parade : convertir le stock au
diviseur de l'âge de référence — ``Parametres.age_reference_fixe``, 65 ans
depuis le 22 septembre 2026, 64 avant —, dès lors que l'assuré est parti à
l'âge légal ou après. Qui est parti avant garde son propre diviseur.

TROIS VARIANTES
---------------
``droit_commun``  l'âge légal est celui du régime général pour sa génération
                  (``age_ouverture_requis.csv``) : 60 ans jusqu'à 1950, 62 à
                  partir de 1955. Un agent de conduite parti à 50 ans, un
                  actif parti à 57, une carrière longue restent au diviseur de
                  leur âge.
``tout_droit``    l'âge légal est celui que le droit de l'assuré lui ouvrait,
                  régime spécial et carrière longue compris — ce que
                  ``ScenarioActuel.age_ouverture_droit`` rend. Personne parti
                  « à l'heure » de son propre régime ne paie l'âge.
``acquis``        la même règle pour les scénarios PROSPECTIFS 3 et 5, où
                  seuls les droits acquis avant la bascule sont convertis à
                  l'âge de référence : ils le sont à l'âge légal de la
                  génération quand il est plus bas que lui — sous une
                  référence de 65 ans, toutes les générations que la bascule
                  trouve en activité, dont l'âge légal va de 62 à 64 ans.

CE QUE LE STOCK VEUT DIRE ICI
-----------------------------
Toute liquidation ANTÉRIEURE à la bascule. Après elle, la règle est connue
avant le choix, et le diviseur de l'âge effectif reste la règle.

CE QU'IL EMPRUNTE
-----------------
``ScenarioNotionnel.retroactif`` et ``ScenarioNotionnel._droits_acquis``,
remplacés le temps du calcul et rendus ensuite ; le solde vient de
``cout.calculer_cout`` tel quel.
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
from retraite_notionnelle.scenarios.actuel import AgesOuverture  # noqa: E402
from retraite_notionnelle.scenarios.notionnel import ScenarioNotionnel  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

VARIANTES: tuple[str, ...] = ("reference", "droit_commun", "tout_droit", "acquis")
RETROACTIFS: tuple[str, ...] = (
    "notionnel_retroactif", "notionnel_retroactif_employeur", "notionnel_liberal",
)
PROSPECTIFS: tuple[str, ...] = ("notionnel_prospectif", "notionnel_prospectif_employeur")
ANNEES_AFFICHEES: tuple[int, ...] = (2026, 2030, 2040, 2050, 2060, 2070)
#: Les cas types et générations dont on imprime la pension : des retraités
#: d'avant la bascule, partis à l'âge légal ou avant lui.
CAS_STOCK: tuple[tuple[str, int], ...] = (
    ("salaire_moyen", 1950), ("salaire_moyen", 1960), ("cadre", 1955),
    ("fonctionnaire_sedentaire", 1955), ("fonctionnaire_actif", 1960),
    ("agent_sncf_conduite", 1960), ("militaire", 1970), ("artisan", 1955),
)


class StockALAgeLegal:
    """Le temps d'un calcul : le stock converti à l'âge de référence pour qui est parti à l'heure."""

    def __init__(self, variante: str, simulateur: Simulateur) -> None:
        if variante not in VARIANTES:
            raise ValueError(f"variante inconnue : {variante!r} (attendu : {VARIANTES})")
        self.variante = variante
        self.simulateur = simulateur
        self.ages = AgesOuverture(simulateur.parametres.racine_donnees)
        self._sauvegarde: dict[str, object] = {}
        #: Couples (carrière, âge de départ, âge légal, âge de conversion) touchés.
        self.touches: list[tuple[str, float, float, float]] = []

    def age_legal(self, carriere) -> float | None:
        if self.variante == "tout_droit":
            return self.simulateur.scenario_actuel.age_ouverture_droit(carriere)
        valeur = self.ages.age(carriere.annee_naissance)
        return None if valeur is None else valeur[0]

    def _retroactif(self, original):
        variante = self

        def retroactif(scenario, carriere, regime_fusionne=None, **kwargs):
            resultat = original(scenario, carriere, regime_fusionne, **kwargs)
            if variante.variante not in ("droit_commun", "tout_droit"):
                return resultat
            parametres = scenario.parametres
            age = carriere.age_liquidation or 0.0
            plancher = parametres.age_reference_fixe
            if carriere.annee_liquidation >= parametres.annee_bascule or age >= plancher:
                return resultat
            legal = variante.age_legal(carriere)
            if legal is None or age < legal:
                return resultat
            conversion = scenario.convertisseur.coefficient(
                plancher, carriere.annee_liquidation, scenario._sexe(carriere),
                carriere.mois_liquidation, scenario.convertisseur.population_de(carriere),
            )
            resultat.pension_annuelle = resultat.compte.capital / conversion.diviseur
            resultat.conversion = conversion
            variante.touches.append((carriere.identifiant, age, legal, plancher))
            return resultat
        return retroactif

    def _droits_acquis(self, original):
        variante = self

        def droits_acquis(scenario, carriere, bascule):
            droits = original(scenario, carriere, bascule)
            if variante.variante != "acquis" or droits is None:
                return droits
            legal = variante.age_legal(carriere)
            if legal is None or legal >= droits.age_conversion:
                return droits
            conversion = scenario.convertisseur.coefficient(
                legal, bascule, scenario._sexe(carriere),
                population=scenario.convertisseur.population_de(carriere),
            )
            capital = droits.pension_figee * conversion.diviseur
            variante.touches.append((carriere.identifiant, carriere.age_liquidation or 0.0,
                                     legal, droits.age_conversion))
            return dataclasses.replace(
                droits, age_conversion=legal, diviseur=conversion.diviseur,
                capital_a_la_bascule=capital,
                capital=capital * droits.coefficient_revalorisation,
            )
        return droits_acquis

    def __enter__(self) -> "StockALAgeLegal":
        self._sauvegarde = {
            "retroactif": ScenarioNotionnel.retroactif,
            "_droits_acquis": ScenarioNotionnel._droits_acquis,
        }
        ScenarioNotionnel.retroactif = self._retroactif(ScenarioNotionnel.retroactif)
        ScenarioNotionnel._droits_acquis = self._droits_acquis(ScenarioNotionnel._droits_acquis)
        return self

    def __exit__(self, *exc) -> None:
        ScenarioNotionnel.retroactif = self._sauvegarde["retroactif"]
        ScenarioNotionnel._droits_acquis = self._sauvegarde["_droits_acquis"]


@dataclass
class Lecture:
    soldes: dict[int, float]
    depenses: dict[int, float]
    solde_moyen: float
    premiere_annee_equilibree: int | None
    dette_horizon: float


@dataclass
class Resultat:
    variante: str
    lectures: dict[str, Lecture]
    #: Pension annuelle en euros constants, par (cas type, génération), pour
    #: les scénarios 4 et 6 — et 3 et 5 sous ``acquis``.
    pensions: dict[str, dict[str, float]]
    touches: int
    cout: C.Cout | None = field(default=None, repr=False)


def calculer(variante: str, parametres: Parametres, depenses: DepensesRetraite,
             population: Population, comptes: ComptesRetraite,
             assiette: AssietteActivite) -> Resultat:
    simulateur = Simulateur(parametres)
    with StockALAgeLegal(variante, simulateur) as stock:
        cout = C.calculer_cout(simulateur, depenses, population, comptes, assiette=assiette)
        touches = len(stock.touches)
        grille = calculer_cas_types(
            simulateur, tuple(c for c in CAS_TYPES if any(c.code == code for code, _ in CAS_STOCK)),
            tuple(sorted({g for _, g in CAS_STOCK})),
        )
    pensions: dict[str, dict[str, float]] = {}
    for code, generation in CAS_STOCK:
        comparaison = grille.resultats.get((code, generation))
        if comparaison is None:
            continue
        pensions[f"{code}|{generation}"] = {
            scenario: comparaison.en_euros_constants(
                getattr(comparaison, scenario).pension_annuelle, scenario)
            for scenario, _ in C.SCENARIOS
        }
    solde = cout.solde
    lectures = {
        scenario: Lecture(
            soldes={l.annee: l.solde(scenario) for l in solde.projetees()},
            depenses={l.annee: l.depense(scenario) for l in solde.projetees()},
            solde_moyen=solde.solde_moyen(scenario, 2026, C.HORIZON),
            premiere_annee_equilibree=solde.premiere_annee_equilibree(scenario),
            dette_horizon=cout.dette.horizon(scenario),
        )
        for scenario, _ in C.SCENARIOS
    }
    return Resultat(variante, lectures, pensions, touches, cout)


LIBELLES = {
    "notionnel_retroactif": "2 rétroactif, salariale",
    "notionnel_prospectif": "3 prospectif, salariale",
    "notionnel_retroactif_employeur": "4 rétroactif, totale",
    "notionnel_prospectif_employeur": "5 prospectif, totale",
    "notionnel_liberal": "6 proposition, 18 %",
}


def tableau(resultats: dict[str, Resultat], annees=ANNEES_AFFICHEES) -> str:
    lignes = ["Solde en points de PIB, par variante du stock ; dette : stock accumulé en 2070", ""]
    entete = (f"{'système / variante':<34}" + "".join(f"{a:>8}" for a in annees)
              + f"{'moy.':>8}{'équil.':>8}{'dette70':>9}")
    lignes += [entete, "-" * len(entete)]
    for scenario in RETROACTIFS + PROSPECTIFS:
        for variante, resultat in resultats.items():
            if variante == "acquis" and scenario not in PROSPECTIFS:
                continue
            if variante in ("droit_commun", "tout_droit") and scenario not in RETROACTIFS:
                continue
            lecture = resultat.lectures[scenario]
            equilibre = lecture.premiere_annee_equilibree
            lignes.append(
                f"{LIBELLES[scenario][:20]:<21}{variante:<13}"
                + "".join(f"{lecture.soldes[a] * 100:>+8.2f}" for a in annees)
                + f"{lecture.solde_moyen * 100:>+8.2f}{str(equilibre) if equilibre else '—':>8}"
                + f"{lecture.dette_horizon * 100:>+9.0f}"
            )
    lignes += ["", "Pension annuelle du scénario 6, euros constants, retraités d'avant la bascule", ""]
    reference = resultats["reference"]
    entete = f"{'cas type / génération':<34}{'référence':>12}" + "".join(
        f"{v:>14}" for v in resultats if v in ("droit_commun", "tout_droit"))
    lignes += [entete, "-" * len(entete)]
    for cle, pensions in reference.pensions.items():
        base = pensions["notionnel_liberal"]
        cellules = "".join(
            f"{resultats[v].pensions[cle]['notionnel_liberal'] / base - 1:>+13.1%} "
            for v in resultats if v in ("droit_commun", "tout_droit"))
        lignes.append(f"{cle.replace('|', ' / '):<34}{base:>12,.0f}{cellules}")
    return "\n".join(lignes).replace(",", " ")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    analyseur.add_argument("--variantes", nargs="+", default=list(VARIANTES), choices=VARIANTES)
    analyseur.add_argument("--json", type=Path)
    arguments = analyseur.parse_args(argv)
    parametres = Parametres()
    racine = parametres.racine_donnees
    donnees = (DepensesRetraite(racine), Population(racine), ComptesRetraite(racine),
               AssietteActivite(racine))
    resultats = {}
    for variante in ["reference", *[v for v in arguments.variantes if v != "reference"]]:
        resultats[variante] = calculer(variante, parametres, *donnees)
        print(f"{variante}: {resultats[variante].touches} couples touchés", file=sys.stderr)
    print(tableau(resultats))
    if arguments.json:
        arguments.json.write_text(json.dumps({
            v: {"lectures": {s: dataclasses.asdict(l) for s, l in r.lectures.items()},
                "pensions": r.pensions, "touches": r.touches}
            for v, r in resultats.items()}, indent=1, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
