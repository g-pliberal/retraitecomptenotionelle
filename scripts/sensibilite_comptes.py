#!/usr/bin/env python3
"""Ce que les hypothèses du COR déplacent dans le bilan, variante par variante.

    python scripts/sensibilite_comptes.py
    python scripts/sensibilite_comptes.py --json sensibilite.json

LA QUESTION À LAQUELLE IL RÉPOND
---------------------------------
« Avec la croissance à 1 %, on devrait avoir moins de chômage et plus de
recettes. » La phrase contient trois affirmations, et le tableau ci-dessous
les départage une par une.

1. **Plus de croissance ne donne pas plus de recettes en part de PIB, et c'est
   correct.** L'assiette et le PIB montent du même pas —
   ``hypotheses_projection.yaml`` s'interdit explicitement de déformer le
   partage de la valeur ajoutée —, si bien qu'une recette proportionnelle à
   l'assiette garde sa part. En euros elle monte ; en part de PIB, non. Tout le
   bilan étant en part de PIB, l'immobilité est la bonne réponse. Le COR trouve
   même un recul de 0,10 point en 2070, parce que sous sa convention EPR
   l'État verse ce qu'il faut pour équilibrer les régimes de fonctionnaires, et
   qu'il leur faut moins.

2. **Une croissance plus forte n'apporte pas moins de chômage.** Le COR ne le
   suppose pas : ses trois variantes de productivité tiennent toutes le chômage
   à 7 % à partir de 2040, et il fait varier le chômage dans une figure à part.
   Les deux dimensions se croisent, elles ne se déduisent pas l'une de l'autre,
   et c'est pourquoi ce script les tient en deux blocs séparés.

3. **La croissance travaille, mais sur l'autre moitié du bilan.** Une pension
   indexée sur les prix décroche d'un PIB qui accélère : c'est la DÉPENSE qui
   recule, de 0,81 point de PIB en 2070 entre 0,7 % et 1,0 %, quand la recette
   n'en perd qu'un dixième. Le gain est réel, il est simplement de l'autre
   côté du compte.

CE QU'IL MESURE EN PLUS, ET QUI EST LA RAISON DE SON EXISTENCE
---------------------------------------------------------------
Le tableau ne dit pas seulement ce que le COR publie : il dit ce que chaque
variante fait au SOLDE DE LA PROPOSITION, qui est la grandeur que le site
affiche. Et ce solde ne se déduit pas du compte du COR, parce que la dépense
d'un système notionnel ne réagit pas comme celle du droit en vigueur : un
compte indexé sur la masse salariale est neutre à la croissance en part de PIB,
là où une pension indexée sur les prix en profite. Un système notionnel gagne
donc moins que le droit constant à ce que la croissance soit forte — et ce
résultat-là est à lui, non à une convention.

CE QU'IL N'EST PAS. Une variante de chômage n'est pas un réglage du site : le
formulaire ne propose que les trois scénarios de productivité. Le compte, lui,
sait lire les quatre variantes, et ce script est là pour que les deux qui n'ont
pas de bouton ne soient pas pour autant inaccessibles.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.cout import calculer_cout  # noqa: E402
from retraite_notionnelle.donnees.assiette import AssietteActivite  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.equilibre import (  # noqa: E402
    VARIANTE_REFERENCE,
    ComptesRetraite,
)
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

LIBERAL = "notionnel_liberal"
ANNEES_AFFICHEES: tuple[int, ...] = (2030, 2040, 2050, 2060, 2070)

#: Les variantes, dans l'ordre d'affichage, avec la dimension qu'elles font
#: varier et le scénario de projection que le MODÈLE doit prendre avec elles.
#:
#: LES DEUX NE COÏNCIDENT PAS SUR LA DIMENSION DU CHÔMAGE, et c'est le point
#: délicat de ce script. Une variante de productivité déplace le compte du COR
#: ET les hypothèses du modèle : les deux doivent bouger ensemble, sans quoi on
#: comparerait une dépense empruntée à 1,0 % à une dépense calculée à 0,7 %.
#: Une variante de chômage, elle, ne déplace que le compte : le COR tient sa
#: productivité à 0,7 %, donc le modèle reste sur son scénario de référence.
VARIANTES: tuple[tuple[str, str, str, str], ...] = (
    ("productivité", "cor_productivite_basse", "cor_productivite_basse",
     "productivité 0,4 %"),
    ("productivité", VARIANTE_REFERENCE, "cor_reference",
     "productivité 0,7 % (référence)"),
    ("productivité", "cor_productivite_haute", "cor_productivite_haute",
     "productivité 1,0 %"),
    ("chômage", "cor_chomage_bas", "cor_reference", "chômage 5 % en 2040"),
    ("chômage", VARIANTE_REFERENCE, "cor_reference",
     "chômage 7 % en 2040 (référence)"),
    ("chômage", "cor_chomage_haut", "cor_reference", "chômage 10 % en 2040"),
)


@dataclass(frozen=True)
class Lecture:
    """Une variante, lue année par année, en part de PIB."""

    dimension: str
    variante: str
    libelle: str
    ressources: dict[int, float]
    depense_actuel: dict[int, float]
    solde_actuel: dict[int, float]
    depense_liberal: dict[int, float]
    solde_liberal: dict[int, float]


def lire(dimension: str, variante: str, scenario: str, libelle: str,
         racine: Path, donnees) -> Lecture:
    depenses, population, assiette = donnees
    comptes = ComptesRetraite(racine, variante=variante)
    cout = calculer_cout(
        Simulateur(Parametres().avec(scenario_projection=scenario)),
        depenses, population, comptes, assiette=assiette)
    lignes = {ligne.annee: ligne for ligne in cout.solde.annees}
    retenues = [a for a in ANNEES_AFFICHEES if a in lignes]
    return Lecture(
        dimension, variante, libelle,
        {a: lignes[a].ressources for a in retenues},
        {a: lignes[a].depense("actuel") for a in retenues},
        {a: lignes[a].solde("actuel") for a in retenues},
        {a: lignes[a].depense(LIBERAL) for a in retenues},
        {a: lignes[a].solde(LIBERAL) for a in retenues},
    )


def tableau(lectures: list[Lecture]) -> str:
    annees = [a for a in ANNEES_AFFICHEES if a in lectures[0].ressources]
    lignes = [
        "Ce qu'une hypothèse du COR déplace dans le bilan, en part de PIB",
        "=" * 72,
        "",
        "Une variante de PRODUCTIVITÉ déplace le compte du COR et les hypothèses",
        "du modèle ensemble ; une variante de CHÔMAGE ne déplace que le compte,",
        "le COR tenant sa productivité à 0,7 % dans les trois.",
    ]
    grandeurs = (
        ("Recettes du système", "ressources"),
        ("Dépense du droit en vigueur", "depense_actuel"),
        ("Solde du droit en vigueur", "solde_actuel"),
        ("Dépense de la proposition", "depense_liberal"),
        ("Solde de la proposition", "solde_liberal"),
    )
    for dimension in ("productivité", "chômage"):
        retenues = [l for l in lectures if l.dimension == dimension]
        lignes += ["", f"-- {dimension.upper()} " + "-" * (70 - len(dimension)), ""]
        for titre, champ in grandeurs:
            lignes += ["", titre, ""]
            lignes.append(f"{'':<34}" + "".join(f"{a:>9}" for a in annees))
            for lecture in retenues:
                valeurs = getattr(lecture, champ)
                signe = "+" if champ.startswith("solde") else ""
                lignes.append(
                    f"{lecture.libelle:<34}"
                    + "".join(f"{valeurs[a] * 100:>{9}.3f}" if not signe
                              else f"{valeurs[a] * 100:>+9.3f}" for a in annees))
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    analyseur.add_argument("--json", type=Path)
    arguments = analyseur.parse_args(argv)
    racine = Parametres().racine_donnees
    donnees = (DepensesRetraite(racine), Population(racine), AssietteActivite(racine))
    lectures = [lire(dimension, variante, scenario, libelle, racine, donnees)
                for dimension, variante, scenario, libelle in VARIANTES]
    print(tableau(lectures))
    if arguments.json:
        arguments.json.write_text(json.dumps(
            [{"dimension": l.dimension, "variante": l.variante, "libelle": l.libelle,
              "ressources": l.ressources, "depense_actuel": l.depense_actuel,
              "solde_actuel": l.solde_actuel, "depense_liberal": l.depense_liberal,
              "solde_liberal": l.solde_liberal}
             for l in lectures], indent=1, ensure_ascii=False),
            encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
