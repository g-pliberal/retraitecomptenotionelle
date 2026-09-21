#!/usr/bin/env python3
"""Ce que le déplacement UNIFORME de la distribution cache, mesuré.

    python scripts/garantie_par_sexe.py
    python scripts/garantie_par_sexe.py --json garantie_sexe.json

CE QU'IL MESURE
---------------
La garantie vieillesse du scénario 6 est chiffrée en déplaçant la
distribution des pensions de l'EIR d'un FACTEUR UNIQUE — la pension moyenne
du scénario 6 rapportée à celle du système actuel, lue sur la grille de cas
types. Ce déplacement est proportionnel et uniforme, alors que le scénario
ne déplace pas toutes les carrières du même rapport : il retire les droits
non contributifs — majorations pour enfants, assurance vieillesse des parents
au foyer, minimum contributif, trimestres assimilés —, et les femmes en
détiennent plus souvent. Leurs pensions tombent donc plus que la moyenne,
davantage d'entre elles passent sous le plancher, et le coût affiché est à ce
titre une BORNE BASSE.

Cette réserve était écrite dans les limites depuis que la garantie est lue
sur la distribution. Elle n'était pas chiffrée. Ce script la chiffre.

POURQUOI PAS UN FACTEUR PAR SEXE TIRÉ DE LA GRILLE
---------------------------------------------------
Ce serait la mesure directe, et elle n'est pas disponible : sur les treize
cas types, **un seul est une femme**. Une carrière ne fait pas une
population, et un facteur féminin tiré d'elle seule serait moins fiable que
la convention qu'il prétendrait corriger. Le dépôt ne porte par ailleurs
aucune ventilation par sexe du coût des avantages non contributifs, qui
serait l'autre chemin.

CE QUE LE SCRIPT FAIT À LA PLACE : UNE SENSIBILITÉ, SOUS CONTRAINTE DE MASSE
-----------------------------------------------------------------------------
L'EIR publie la distribution des DEUX sexes à part. On peut donc déplacer
chacune du sien — ``f_F`` et ``f_H`` — au lieu de déplacer l'ensemble du
même. Reste à savoir de combien, et c'est précisément ce que personne ne
publie. Le script ne le suppose donc pas : il le PARAMÈTRE, par le seul
rapport ``r = f_F / f_H``, et impose que la moyenne d'ensemble bouge du même
facteur qu'aujourd'hui. Cette contrainte est ce qui fait de l'exercice une
mesure et non une hypothèse de plus : la grille garde le dernier mot sur
l'agrégat, et le script ne fait que le RÉPARTIR entre les deux sexes.

    w·μ_F·f_F + (1−w)·μ_H·f_H = f·(w·μ_F + (1−w)·μ_H)

``w`` est la part des femmes dans la population de l'enquête — 52,8 %, lue
sur le fichier par ``donnees.distribution.part_femmes`` —, ``μ`` la pension
moyenne de chaque sexe, et ``f`` le facteur d'ensemble de l'année de
l'enquête. À ``r = 1`` le script redonne EXACTEMENT le coût de la page :
c'est son contrôle, et ``tests/test_garantie_par_sexe.py`` le tient.

COMMENT SE LIT ``r``
---------------------
Si le scénario retire à chacun la part non contributive de sa pension,
``f_s ≈ f_commun·(1 − a_s)`` où ``a_s`` est cette part pour le sexe ``s``, et
``r ≈ (1 − a_F)/(1 − a_H)``. Un ``r`` de 0,90 dit donc que la part non
contributive de la pension des femmes dépasse celle des hommes d'environ dix
points. Le dépôt ne mesure ni l'une ni l'autre : ``r`` reste un paramètre, et
le tableau une sensibilité. Ce qui est établi, et que le tableau montre,
c'est le SENS de l'écart — toujours à la hausse — et son ORDRE DE GRANDEUR.
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
from retraite_notionnelle.donnees.distribution import (  # noqa: E402
    DistributionPensions,
    part_femmes,
)
from retraite_notionnelle.donnees.equilibre import ComptesRetraite  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.garantie import cout_garantie  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

#: Les rapports parcourus. Un est l'ANCIENNE convention — un facteur unique
#: pour tous —, gardée comme repère ; en deçà, les pensions des femmes tombent
#: davantage que celles des hommes. Au-delà de un il n'y a rien à explorer : le
#: sens de l'écart n'est pas douteux. Le rapport MESURÉ sur l'enquête s'insère
#: dans cette liste à son rang, et c'est lui que le modèle applique.
RAPPORTS: tuple[float, ...] = (1.00, 0.95, 0.90, 0.85, 0.80)


@dataclass(frozen=True)
class Lecture:
    """Le coût de la garantie sous un rapport ``r``, pour un plancher."""

    plancher: str
    rapport: float
    #: Ce rapport est-il celui que l'enquête donne, et que le modèle applique ?
    mesure: bool
    facteur_femmes: float
    facteur_hommes: float
    part_sous_plancher: float
    cout_mds: float
    ecart_mds: float


def _moyenne(distribution: DistributionPensions) -> float:
    """Pension moyenne de la distribution, dans les euros de l'enquête.

    Même convention que ``garantie.cout_garantie`` : le milieu de chaque
    tranche, et la tranche ouverte à sa borne inférieure. Elle sous-estime
    donc les deux moyennes, et celle des hommes un peu plus — ils sont plus
    nombreux dans la tranche ouverte. Ce que cela déplace est sans effet ici :
    seul le RAPPORT des deux moyennes entre dans la contrainte, et repousser
    la tranche ouverte de 4 500 à 6 500 € le fait passer de 0,641 à 0,624.
    """
    return sum(
        tranche.part * (
            tranche.borne_inferieure if tranche.borne_superieure is None
            else 0.5 * (tranche.borne_inferieure + tranche.borne_superieure)
        )
        for tranche in distribution.tranches
    )


def calculer(parametres: Parametres | None = None,
             rapports: tuple[float, ...] = RAPPORTS) -> list[Lecture]:
    """Le coût de la garantie à l'année de l'enquête, rapport par rapport."""
    parametres = parametres or Parametres()
    simulateur = Simulateur(parametres)
    racine = parametres.racine_donnees
    # Les mêmes entrées que la page Coût : le facteur de déplacement doit être
    # celui qu'elle affiche, sans quoi la colonne « r = 1 » ne la redonnerait
    # pas et la sensibilité porterait à côté.
    cout = calculer_cout(
        simulateur, DepensesRetraite(racine), Population(racine),
        ComptesRetraite(racine), assiette=AssietteActivite(racine))
    millesime = simulateur.distribution.millesime
    colonnes = {
        sexe: DistributionPensions(racine, sexe=sexe, millesime=millesime)
        for sexe in ("F", "H")
    }
    poids_femmes = part_femmes(racine, millesime)
    # Le rapport MESURÉ prend sa place dans le parcours : c'est celui que le
    # modèle applique depuis le 21 septembre 2026, et la colonne « 1,00 » n'est
    # plus que le repère de ce que la convention uniforme valait.
    mesure = simulateur.caracteristiques.rapport_deplacement()
    rapports = tuple(sorted(set(rapports) | {mesure}, reverse=True))
    moyennes = {sexe: _moyenne(colonnes[sexe]) for sexe in ("F", "H")}
    ligne = cout.annee(millesime)
    if ligne is None or ligne.garantie is None:
        raise RuntimeError("la trajectoire ne porte pas l'année de l'enquête")
    facteur = ligne.garantie.facteur
    vers_enquete = simulateur.macro.coefficient_prix(
        parametres.annee_euros_garantie_vieillesse, millesime)
    vers_constants = simulateur.macro.coefficient_prix(
        millesime, parametres.annee_euros_constants)
    effectif = simulateur.effectifs.effectif("tous_regimes", millesime)
    recours = parametres.taux_recours_garantie
    moyenne_ensemble = (poids_femmes * moyennes["F"]
                        + (1.0 - poids_femmes) * moyennes["H"])

    planchers = (
        ("plancher majoré (personne seule)",
         parametres.garantie_vieillesse_mensuelle
         + parametres.allocation_isolement_mensuelle),
        ("plancher de base (vie à deux)",
         parametres.garantie_vieillesse_mensuelle),
    )
    lectures: list[Lecture] = []
    for libelle, mensuel in planchers:
        plancher = mensuel * vers_enquete
        reference = None
        for rapport in rapports:
            # La contrainte de masse : la moyenne d'ensemble bouge du même
            # facteur qu'aujourd'hui, quelle que soit la façon dont les deux
            # sexes se partagent ce déplacement.
            denominateur = (poids_femmes * moyennes["F"] * rapport
                            + (1.0 - poids_femmes) * moyennes["H"])
            facteur_h = facteur * moyenne_ensemble / denominateur
            facteurs = {"F": rapport * facteur_h, "H": facteur_h}
            part = 0.0
            cout_meur = 0.0
            for sexe, poids in (("F", poids_femmes), ("H", 1.0 - poids_femmes)):
                chiffre = cout_garantie(colonnes[sexe], effectif * poids,
                                        plancher, facteurs[sexe])
                part += poids * chiffre.part_beneficiaires
                cout_meur += chiffre.cout_annuel_meur
            milliards = cout_meur * vers_constants * recours / 1000.0
            if reference is None:
                reference = milliards
            lectures.append(Lecture(
                plancher=libelle,
                rapport=rapport,
                mesure=abs(rapport - mesure) < 1e-12,
                facteur_femmes=facteurs["F"],
                facteur_hommes=facteurs["H"],
                part_sous_plancher=part,
                cout_mds=milliards,
                ecart_mds=milliards - reference,
            ))
    return lectures


def tableau(lectures: list[Lecture], parametres: Parametres) -> str:
    lignes = [
        "Le coût de la garantie quand les deux sexes ne tombent pas du même "
        "rapport",
        f"Année de l'enquête, euros de {parametres.annee_euros_constants}, "
        f"un ayant droit sur {round(1 / parametres.taux_recours_garantie)} "
        "réclamant.",
        "",
    ]
    plancher = None
    for lecture in lectures:
        if lecture.plancher != plancher:
            plancher = lecture.plancher
            lignes += [
                f"  {plancher}",
                f"    {'r=fF/fH':>8}  {'fF':>6} {'fH':>7} "
                f"{'sous le plancher':>17} {'coût':>10} {'écart':>9}",
            ]
        lignes.append(
            f"    {lecture.rapport:>8.3f}{'*' if lecture.mesure else ' '}"
            f"{lecture.facteur_femmes:>7.4f} "
            f"{lecture.facteur_hommes:>7.4f} "
            f"{lecture.part_sous_plancher:>16.2%} "
            f"{lecture.cout_mds:>7.1f} Md {lecture.ecart_mds:>+6.1f} Md"
        )
    lignes += [
        "",
        "* le rapport MESURÉ sur l'enquête, celui que le modèle applique.",
        "r = 1 est l'ancienne convention : un seul facteur pour tous. En deçà,",
        "les pensions des femmes tombent davantage que celles des hommes, la",
        "moyenne d'ensemble restant déplacée du même facteur.",
    ]
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    analyseur.add_argument("--json", type=Path)
    arguments = analyseur.parse_args(argv)
    parametres = Parametres()
    lectures = calculer(parametres)
    print(tableau(lectures, parametres))
    if arguments.json:
        arguments.json.write_text(json.dumps(
            [lecture.__dict__ for lecture in lectures],
            indent=1, ensure_ascii=False,
        ), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
