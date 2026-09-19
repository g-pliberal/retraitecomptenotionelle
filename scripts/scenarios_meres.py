#!/usr/bin/env python3
"""Ce que les enfants font à la pension d'une mère, scénario 1 contre scénario 6.

    python scripts/scenarios_meres.py                     # génération 1966, 0,9 SMPT
    python scripts/scenarios_meres.py --generation 1980
    python scripts/scenarios_meres.py --niveau 0.6 --affiliation salarie_prive_non_cadre
    python scripts/scenarios_meres.py --csv sortie.csv

CE QU'IL MESURE
---------------
Une même femme, salariée du privé, et une grille de situations : zéro à trois
enfants, avec ou sans années d'arrêt pour les élever, départ à l'âge de
référence ou à l'âge légal, temps plein ou mi-temps. Pour chaque ligne, deux
pensions et deux écarts :

- **scénario 1**, le droit en vigueur, qui porte tout ce que le système actuel
  donne au titre des enfants — majoration de durée d'assurance (huit
  trimestres par enfant au régime général), majoration de 10 % pour trois
  enfants et plus, assurance vieillesse des parents au foyer (AVPF) sur les
  années d'arrêt, surcote parentale, trimestres d'enfants réputés cotisés ;
- **scénario 6**, la proposition libérale — compte notionnel rétroactif à la
  cotisation entière, 18 % pour tous dès 2026, 5 + 5 % capitalisés, garantie
  vieillesse de 800 € par mois, 1 050 € pour une personne seule —, qui ne
  porte au compte que ce qui a été cotisé : aucun trimestre gratuit, aucune
  majoration, et une année d'arrêt vaut zéro.

L'« effet des enfants » d'une ligne est ce que la pension gagne, dans chaque
scénario, par rapport à la même carrière SANS enfant, où les années d'arrêt
sont de simples années sans activité. C'est la mesure directe de ce que chaque
système accorde à la maternité, et elle se lit ligne à ligne : ce que le
scénario 1 sert pour les enfants, le scénario 6 ne le sert pas, et l'écart
entre les deux s'en creuse d'autant.

Les montants sont mensuels, bruts, en euros constants de 2026 : c'est la seule
unité qui compare des liquidations d'années différentes. Le scénario 6 est
donné TOTAL, pilier capitalisé compris, comme la dernière ligne du tableau du
simulateur. La garantie vieillesse n'est comptée que si elle est servie à la
liquidation, c'est-à-dire à 65 ans au plus tôt ; avant, la colonne « garantie »
dit ce qu'elle servirait à cet âge.
"""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from retraite_notionnelle import Parametres  # noqa: E402
from retraite_notionnelle.simulateur import Comparaison, Simulateur  # noqa: E402

LIBERAL = "notionnel_liberal"


@dataclass(frozen=True)
class Situation:
    """Une ligne de la grille : ce qui distingue cette mère de la précédente."""

    code: str
    libelle: str
    nombre_enfants: int
    #: Années d'arrêt pour élever les enfants, comptées depuis le premier
    #: enfant, que le modèle place à vingt-huit ans. Zéro : aucune.
    annees_arret: int
    #: Ce qui date le départ. ``taux_plein`` : le premier âge auquel la
    #: pension est servie entière, résolu par le scénario 1 pour cette
    #: carrière-là, comme les cas types le font ; ``ouverture`` : l'âge légal
    #: que le droit oppose à la génération, durée atteinte ou non ; un nombre :
    #: un âge fixe. Les trimestres d'enfants entrent dans la durée qui date
    #: le taux plein : c'est par là qu'une mère part plus tôt qu'une femme
    #: sans enfant, à carrière égale, et la grille le montre.
    depart: str | float = "taux_plein"
    niveau_salaire: float | None = None
    affiliation: str | None = None


#: Âge de la mère à la naissance du premier enfant. C'est l'hypothèse du
#: scénario 1 pour dater la bonification de la fonction publique, et l'âge
#: moyen à la première naissance en France depuis les années 2000.
AGE_PREMIER_ENFANT = 28

SITUATIONS = (
    Situation("complete_0", "Carrière complète, sans enfant", 0, 0),
    Situation("complete_1", "Carrière complète, 1 enfant", 1, 0),
    Situation("complete_2", "Carrière complète, 2 enfants", 2, 0),
    Situation("complete_3", "Carrière complète, 3 enfants", 3, 0),
    Situation("arret3_2", "2 enfants, 3 ans d'arrêt", 2, 3),
    Situation("arret6_3", "3 enfants, 6 ans d'arrêt", 3, 6),
    Situation("legal_arret6_0", "Départ à l'âge légal, 6 ans d'arrêt, sans enfant", 0, 6, "ouverture"),
    Situation("legal_arret6_2", "Départ à l'âge légal, 6 ans d'arrêt, 2 enfants", 2, 6, "ouverture"),
    Situation("legal_arret6_3", "Départ à l'âge légal, 6 ans d'arrêt, 3 enfants", 3, 6, "ouverture"),
    Situation("mitemps_arret6_3", "Mi-temps au SMIC, 3 enfants, 6 ans d'arrêt", 3, 6, "taux_plein", 0.5),
    Situation("mitemps_65_arret6_3", "Mi-temps au SMIC, 3 enfants, 6 ans d'arrêt, départ à 65 ans", 3, 6, 65, 0.5),
    Situation("fonctionnaire_2", "Fonctionnaire d'État, 2 enfants", 2, 0, "taux_plein", 1.2, "fonctionnaire_etat"),
    Situation("fonctionnaire_3", "Fonctionnaire d'État, 3 enfants, 3 ans d'arrêt", 3, 3, "taux_plein", 1.2, "fonctionnaire_etat"),
)

#: Passes de la recherche de l'âge de départ : l'âge d'ouverture dépend de la
#: carrière, qui dépend de l'âge. Deux suffisent, comme pour les cas types.
PASSES_LIQUIDATION = 4


@dataclass(frozen=True)
class Ligne:
    situation: Situation
    age_liquidation: float
    liquidation_ouverte: bool
    actuel: float
    liberal: float
    garantie: float
    garantie_servie: bool
    effet_enfants_actuel: float
    effet_enfants_liberal: float
    trimestres: int
    trimestres_requis: int
    taux: float
    avantages: tuple[str, ...]

    @property
    def ecart(self) -> float:
        return self.liberal / self.actuel - 1.0 if self.actuel > 0 else float("nan")


class Grille:
    def __init__(self, generation: int, niveau: float, affiliation: str,
                 age_debut: float, parametres: Parametres | None = None) -> None:
        self.simulateur = Simulateur(parametres or Parametres())
        self.generation = generation
        self.niveau = niveau
        self.affiliation = affiliation
        self.age_debut = age_debut

    @property
    def age_reference(self) -> float:
        # L'âge de référence se lit à l'année où la génération l'atteint ; le
        # simulateur le résout lui-même, on lui demande celui de 64 ans.
        return self.simulateur.age_reference.age(self.generation + 64)

    def _carriere(self, situation: Situation, nombre_enfants: int, motif: str,
                  age_liquidation: float):
        interruptions = {
            self.generation + AGE_PREMIER_ENFANT + i: motif
            for i in range(situation.annees_arret)
        }
        affiliation = situation.affiliation or self.affiliation
        return self.simulateur.carriere_simple(
            annee_naissance=self.generation, sexe="F",
            affiliation=affiliation,
            age_debut=self.age_debut,
            age_liquidation=age_liquidation,
            niveau_salaire=situation.niveau_salaire or self.niveau,
            nombre_enfants=nombre_enfants,
            interruptions=interruptions,
            part_primes=0.18 if affiliation.startswith("fonctionnaire") else 0.0,
        )

    def _age_liquidation(self, situation: Situation, nombre_enfants: int,
                         motif: str) -> float:
        """L'âge auquel cette mère part, résolu par point fixe comme un cas type.

        La même règle que :meth:`CasType.age_liquidation_pour`, réduite à ce
        qui sert ici : on part de l'âge de référence, on demande au scénario 1
        ce que le droit oppose à cette carrière-là, on recommence. L'âge est
        propre à chaque carrière : à durée égale, la mère de deux enfants
        atteint le taux plein seize trimestres avant la femme sans enfant.
        """
        if not isinstance(situation.depart, str):
            return float(situation.depart)
        actuel = self.simulateur.scenario_actuel
        resoudre = (actuel.age_taux_plein_droit if situation.depart == "taux_plein"
                    else actuel.age_ouverture_droit)
        age = self.age_reference
        for _ in range(PASSES_LIQUIDATION):
            propose = resoudre(self._carriere(situation, nombre_enfants, motif, age))
            if propose is None or abs(propose - age) < 1e-9:
                break
            age = propose
        return age

    def _mensuel(self, comparaison: Comparaison, montant: float) -> float:
        return comparaison.en_euros_constants(montant) / 12.0

    def calculer(self, situation: Situation) -> Ligne:
        # Une femme sans enfant n'a pas d'années d'éducation : ses années
        # d'arrêt sont de simples années sans activité, comme celles de la
        # carrière de comparaison. L'effet des enfants y vaut zéro par
        # construction, et la ligne dit ce que l'arrêt seul coûte.
        motif = "education_enfant" if situation.nombre_enfants > 0 else "sans_activite"
        # La carrière de comparaison part au MÊME âge : l'effet des enfants
        # est mesuré à date de départ égale, comme la cascade du scénario 1
        # mesure chaque avantage. Ce que les trimestres d'enfants font à la
        # DATE se lit d'une ligne à l'autre, dans la colonne « Départ ».
        age = self._age_liquidation(situation, situation.nombre_enfants, motif)
        avec = self.simulateur.simuler(self._carriere(situation, situation.nombre_enfants, motif, age))
        sans = self.simulateur.simuler(self._carriere(situation, 0, "sans_activite", age))
        actuel = self._mensuel(avec, avec.actuel.pension_annuelle)
        liberal = self._mensuel(avec, avec.pension_totale(LIBERAL))
        garantie = avec.notionnel_liberal.garantie_vieillesse
        return Ligne(
            situation=situation,
            age_liquidation=avec.carriere.age_liquidation,
            liquidation_ouverte=avec.actuel.liquidation_ouverte,
            actuel=actuel,
            liberal=liberal,
            garantie=self._mensuel(avec, garantie.complement) if garantie else 0.0,
            garantie_servie=bool(garantie and garantie.servie_a_la_liquidation),
            effet_enfants_actuel=actuel - self._mensuel(sans, sans.actuel.pension_annuelle),
            effet_enfants_liberal=liberal - self._mensuel(sans, sans.pension_totale(LIBERAL)),
            trimestres=avec.actuel.trimestres_valides,
            trimestres_requis=avec.actuel.trimestres_requis,
            taux=avec.actuel.taux_liquidation,
            avantages=tuple(
                f"{a.libelle} : {self._mensuel(avec, a.montant):+.0f} €/mois ({a.detail})"
                for a in avec.actuel.avantages_appliques
            ),
        )


def formater_age(age: float) -> str:
    annees = int(age)
    mois = round((age - annees) * 12)
    return f"{annees} ans" if mois == 0 else f"{annees} ans {mois} mois"


def imprimer(grille: Grille, lignes: list[Ligne], detail: bool) -> None:
    print(f"Femme née en {grille.generation}, {grille.affiliation}, entrée à "
          f"{formater_age(grille.age_debut)}, {grille.niveau:.2f} × salaire moyen, "
          f"âge de référence {formater_age(grille.age_reference)}.")
    print("Montants mensuels bruts, en euros constants de 2026. Scénario 6 : total "
          "servi, pilier capitalisé compris.\n")
    entete = (f"{'Situation':58} {'Départ':>14} {'Scén. 1':>9} {'Scén. 6':>9} "
              f"{'Écart':>7} {'Enfants S1':>11} {'Enfants S6':>11} {'Garantie':>9}")
    print(entete)
    print("-" * len(entete))
    for l in lignes:
        depart = formater_age(l.age_liquidation) + ("" if l.liquidation_ouverte else " *")
        garantie = ("" if l.garantie <= 0
                    else f"{l.garantie:.0f} €" + ("" if l.garantie_servie else " à 65"))
        print(f"{l.situation.libelle:58} {depart:>14} {l.actuel:>8.0f}€ {l.liberal:>8.0f}€ "
              f"{l.ecart:>+7.1%} {l.effet_enfants_actuel:>+10.0f}€ "
              f"{l.effet_enfants_liberal:>+10.0f}€ {garantie:>9}")
        if detail:
            print(f"{'':6}trimestres {l.trimestres}/{l.trimestres_requis}, taux {l.taux:.2%}")
            for a in l.avantages:
                print(f"{'':6}{a}")
    if any(not l.liquidation_ouverte for l in lignes):
        print("\n* Liquidation que le droit n'ouvre pas à cet âge : montant contrefactuel.")
    print("\n« Enfants S1 » et « Enfants S6 » : ce que la pension gagne, dans chaque "
          "scénario, par rapport à la même carrière sans enfant, les années d'arrêt "
          "devenant de simples années sans activité.")


def ecrire_csv(chemin: Path, lignes: list[Ligne]) -> None:
    with chemin.open("w", encoding="utf-8", newline="") as flux:
        w = csv.writer(flux)
        w.writerow(["code", "situation", "enfants", "annees_arret", "age_liquidation",
                    "liquidation_ouverte", "actuel_mensuel", "liberal_mensuel", "ecart",
                    "effet_enfants_actuel", "effet_enfants_liberal", "garantie_mensuelle",
                    "garantie_servie", "trimestres", "trimestres_requis", "taux"])
        for l in lignes:
            w.writerow([l.situation.code, l.situation.libelle, l.situation.nombre_enfants,
                        l.situation.annees_arret, f"{l.age_liquidation:.2f}",
                        int(l.liquidation_ouverte), f"{l.actuel:.2f}", f"{l.liberal:.2f}",
                        f"{l.ecart:.4f}", f"{l.effet_enfants_actuel:.2f}",
                        f"{l.effet_enfants_liberal:.2f}", f"{l.garantie:.2f}",
                        int(l.garantie_servie), l.trimestres, l.trimestres_requis,
                        f"{l.taux:.4f}"])


def main(argv: list[str] | None = None) -> int:
    parseur = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parseur.add_argument("--generation", type=int, default=1966)
    parseur.add_argument("--niveau", type=float, default=0.9,
                         help="revenu en multiples du salaire moyen (défaut 0,9)")
    parseur.add_argument("--affiliation", default="salarie_prive_non_cadre")
    parseur.add_argument("--age-debut", type=float, default=21)
    parseur.add_argument("--detail", action="store_true",
                         help="sous chaque ligne, les avantages que le scénario 1 applique")
    parseur.add_argument("--csv", type=Path)
    args = parseur.parse_args(argv)

    grille = Grille(args.generation, args.niveau, args.affiliation, args.age_debut)
    lignes = [grille.calculer(s) for s in SITUATIONS]
    imprimer(grille, lignes, args.detail)
    if args.csv:
        ecrire_csv(args.csv, lignes)
        print(f"\nÉcrit : {args.csv}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
