"""Le jumeau Python de la mesure des avantages non contributifs : les
scénarios 1 neutralisés, chacun privé d'un avantage, et le recalcul d'une
case de la grille sous chacun d'eux.

Le coût des avantages (``avantages.decomposer``) ne les exécute plus : le
portage bâtit les mêmes variantes (``scenariosNeutralises`` de ``pont.mjs``)
et liquide chaque case sous elles (``pont.avantages``). Seuls des tests les
liquidaient encore en Python, pour confronter le portage à son jumeau ou
éprouver une variante : ils logent ici depuis ``avantages.py``, tels quels
(action 161, étape 4 de l'inventaire du retrait des règles), et partiront
avec les règles Python.
"""

from __future__ import annotations

import copy
import dataclasses
from dataclasses import replace
from pathlib import Path

from retraite_notionnelle.avantages import (
    _ecarts,
    _options_de_la_variante,
    _variantes_demandees,
)
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.carriere import Carriere as CarriereDesRegles
from retraite_notionnelle.castypes import CasType
from retraite_notionnelle.donnees.simulateur import SimulateurDeDonnees
from retraite_notionnelle.donnees.tables_du_droit import CarriereLongue, FichesDatees
from retraite_notionnelle.droit.compter import (FICHE_DE_L_APPRENTISSAGE, FICHE_DES_MILITAIRES,
                                                FICHES_DES_EMPLOIS, _contrats)
from retraite_notionnelle.scenarios.actuel import ScenarioActuel
from retraite_notionnelle.somme import somme_ordonnee


def des_regles(carriere):
    """La carrière nue que rend le pont, recopiée champ à champ sous la classe
    des règles, que le moteur Python interroge (``prolongee``,
    ``date_entree``…)."""
    if isinstance(carriere, CarriereDesRegles):
        return carriere
    return CarriereDesRegles(**{champ.name: getattr(carriere, champ.name)
                               for champ in dataclasses.fields(carriere) if champ.init})


#: Les fiches que retire chacune des neutralisations des bonifications de
#: service : celles des emplois classés, puis celle des militaires.
FICHES_RETIREES: dict[str, tuple[str, ...]] = {
    "bonification_cinquieme_services_actifs": tuple(
        nom for nom in FICHES_DES_EMPLOIS if nom != FICHE_DES_MILITAIRES),
    "bonification_cinquieme_militaires": (FICHE_DES_MILITAIRES,),
}


def statuts_des_emplois(simulateur: SimulateurDeDonnees, code: str) -> frozenset[str]:
    """Les statuts qu'une version des fiches que cette neutralisation retire
    bonifie (:data:`FICHES_RETIREES`) : les seules carrières que le retrait
    peut toucher."""
    # Les fiches, des données que leur chargeur lit, sans le moteur.
    fiches = FichesDatees(simulateur.parametres.racine_donnees).fiches()
    return frozenset(statut for nom in FICHES_RETIREES[code] if nom in fiches
                     for version in fiches[nom]["versions"]
                     for statut in version["parametres"].get("statuts") or ())

def _catalogue_sans(catalogue, code: str | None = None):
    """Le catalogue, privé d'une déclaration, sans qu'aucun code du moteur change.

    Le moteur lit ``avantages_non_contributifs`` période par période. Retirer
    la déclaration suffit à ce que le régime cesse de servir l'avantage : c'est
    la contrefactuelle la plus fidèle qui soit, puisqu'elle ne change que la
    DÉCLARATION, là où le droit l'a lui-même écrite. La garantie minimale de
    points de l'Agirc s'y mesurait aussi, en retirant son plancher, jusqu'au
    2 octobre 2026 : une cotisation forfaitaire achetait ses points, et elle
    n'est plus un avantage non contributif.
    """
    variante = copy.deepcopy(catalogue)
    for nom, regime in list(variante._regimes.items()):
        periodes = []
        for periode in regime.periodes:
            champs: dict = {}
            if code is not None and code in periode.avantages_non_contributifs:
                champs["avantages_non_contributifs"] = tuple(
                    declare for declare in periode.avantages_non_contributifs
                    if declare != code
                )
            periodes.append(replace(periode, **champs) if champs else periode)
        variante._regimes[nom] = replace(regime, periodes=tuple(periodes))
    return variante


class _ScenarioDuJumeau(ScenarioActuel):
    """Le scénario 1 du moteur Python, qui lit la carrière sous la classe des
    règles : celle que le pont rend, nue, y est recopiée."""

    def calculer(self, carriere, *args, **kwargs):
        return super().calculer(des_regles(carriere), *args, **kwargs)


def scenarios_neutralises(simulateur: SimulateurDeDonnees) -> dict[str, ScenarioActuel]:
    """Un scénario 1 par avantage retiré, construit une fois pour toute la grille.

    Les trois cent quarante-deux couples de la grille partagent ces variantes :
    les construire par couple coûterait le chargement des tables autant de fois,
    et rendrait la page inutilisable.

    Les avantages retirés PAR LA CARRIÈRE n'y sont pas : ils ne demandent aucun
    scénario nouveau, seulement une carrière autre.
    """
    variantes: dict[str, ScenarioActuel] = {}
    catalogues = {
        "categorie_active": _catalogue_sans(simulateur.catalogue,
                                            code="categorie_active"),
    }
    # Le classement de l'emploi et la jouissance militaire partagent leur
    # déclaration : un seul catalogue les neutralise, et c'est l'affiliation de
    # la carrière qui dit laquelle des deux lignes l'écart renseigne.
    catalogues["age_jouissance_militaire"] = catalogues["categorie_active"]
    for code, catalogue in catalogues.items():
        variantes[code] = _ScenarioDuJumeau(
            simulateur.macro, catalogue, simulateur.affiliations,
            simulateur.parametres,
        )
    parents = _ScenarioDuJumeau(simulateur.macro, simulateur.catalogue,
                             simulateur.affiliations, simulateur.parametres)
    # La date d'entrée en vigueur, repoussée hors de portée : la branche qui
    # retire une ou deux années au salaire de référence ne s'exécute plus.
    parents.PARENTS_MEILLEURES_ANNEES_DEPUIS = DateMois(2999, 1)
    variantes["salaire_de_reference_des_parents"] = parents

    longue = _ScenarioDuJumeau(simulateur.macro, simulateur.catalogue,
                            simulateur.affiliations, simulateur.parametres)
    # Un barème lu sur un fichier absent est un barème vide, et le constructeur
    # le prévoit : aucune porte ne s'ouvre plus avant l'âge légal.
    longue.carriere_longue = CarriereLongue(Path("barème-vidé-pour-la-mesure"))
    variantes["carriere_longue"] = longue

    handicap = _ScenarioDuJumeau(simulateur.macro, simulateur.catalogue,
                              simulateur.affiliations, simulateur.parametres)
    # La fiche du départ anticipé des assurés handicapés, retirée : ses régimes
    # n'ouvrent plus rien à ce titre. Seule une carrière qui déclare une
    # incapacité y perd quelque chose (:func:`recalculer`).
    handicap.invalidites = handicap.invalidites.sans("handicap")
    variantes["retraite_anticipee_handicap"] = handicap

    for code, noms in FICHES_RETIREES.items():
        emplois = _ScenarioDuJumeau(simulateur.macro, simulateur.catalogue,
                                 simulateur.affiliations, simulateur.parametres)
        # Les fiches des bonifications des emplois classés, ou celle des
        # militaires, retirées : seule une carrière servie dans un emploi
        # qu'elles bonifient y perd quelque chose.
        emplois.fiches_datees = emplois.fiches_datees.sans(*noms)
        variantes[code] = emplois

    apprentissage = _ScenarioDuJumeau(simulateur.macro, simulateur.catalogue,
                                   simulateur.affiliations, simulateur.parametres)
    # La fiche de l'apprentissage retirée : le contrat ne valide plus que ce
    # que ses salaires portent. Seule une carrière qui déclare un contrat y
    # perd quelque chose (:func:`recalculer`).
    apprentissage.fiches_datees = apprentissage.fiches_datees.sans(FICHE_DE_L_APPRENTISSAGE)
    variantes["apprentissage"] = apprentissage
    return variantes


def carriere_variante(simulateur: SimulateurDeDonnees, cas: CasType, generation: int,
                      age: float, affiliation: str | None = None,
                      interruptions: dict[int, str] | None = None):
    """La carrière d'un cas type, avec une variante possible.

    Reprend ``CasType._carriere`` à deux libertés près, qui sont exactement les
    deux contrefactuelles : le statut d'affiliation, et le motif des périodes
    non travaillées. L'âge de liquidation est PASSÉ et non recalculé — c'est ce
    qui tient les deux pensions comparables.
    """
    return des_regles(simulateur.carriere_simple(**_options_de_la_variante(
        cas, generation, age, affiliation, interruptions)))


def recalculer(simulateur: SimulateurDeDonnees, cas: CasType, generation: int,
               age: float, reelle,
               variantes: dict[str, ScenarioActuel] | None = None,
               ) -> tuple[dict[str, float], dict[str, str]]:
    """Les avantages non isolés par la cascade, mesurés par recalcul.

    Rend un dictionnaire VIDE quand la carrière n'en porte aucun, plutôt qu'un
    zéro : la plupart des cas types sont dans ce cas, et un zéro écrit
    laisserait croire à une mesure là où il n'y a rien à mesurer.

    DEUX PRÉCAUTIONS ET UN GARDE-FOU.

    La première précaution évite un double compte. Neutraliser les périodes non
    travaillées retire les trimestres assimilés ET l'AVPF, que la cascade
    chiffre déjà sous sa propre ligne. On la retranche donc de l'écart brut.

    La seconde est une interaction qu'on ne mesure pas. Retirer deux avantages à
    la fois n'est pas la somme de deux retraits : la décote est plafonnée, et
    deux pénalités qui butent sur le même plafond ne s'additionnent pas. Chaque
    ligne est donc mesurée seule, contre la pension réelle, et leur somme est un
    ordre de grandeur plutôt qu'un total exact. Aucun cas type de la grille ne
    porte deux avantages d'âge à la fois, ce qu'un test exige.

    LE GARDE-FOU refuse plutôt que de rendre un chiffre faux. Un retrait ne vaut
    comme contrefactuelle que s'il ne déplace QUE l'avantage visé. Quand il
    déplace aussi la DURÉE REQUISE, le rapport de proratisation change avec lui
    et l'écart ne mesure plus rien de nommable. L'appelant reçoit le refus et sa
    raison, et le refus est contagieux : voir :func:`decomposer`.

    SAUF QUAND LA DURÉE REQUISE EST L'AVANTAGE, et c'est le cas du classement de
    l'emploi depuis que le modèle lit le XXIV, B de l'article 10 de la loi du
    14 avril 2023. Le texte donne cette durée « pour les fonctionnaires
    bénéficiant, AU TITRE DE LA CATÉGORIE ACTIVE, d'un droit au départ à l'âge
    anticipé » : elle n'est pas un effet de bord du retrait, elle est l'une des
    trois choses que le classement accorde, avec l'âge anticipé et l'âge
    d'annulation de la décote. La refuser reviendrait à cesser de chiffrer un
    avantage parce qu'on vient d'en mieux comprendre la portée. La jouissance
    militaire, elle, reste refusée : sa durée de 160 trimestres vient de la
    fiche du régime et non du droit d'âge qu'on retire.
    """
    if variantes is None:
        variantes = scenarios_neutralises(simulateur)
    de_carriere, de_scenario = _variantes_demandees(cas, generation)
    sans: dict[str, tuple[float, int]] = {}
    for code, interruptions in de_carriere.items():
        liquidee = simulateur.scenario_actuel.calculer(carriere_variante(
            simulateur, cas, generation, age, interruptions=interruptions))
        sans[code] = (liquidee.pension_annuelle, liquidee.trimestres_requis)
    for code in de_scenario:
        variante = variantes.get(code)
        if variante is None:
            continue
        if (code in FICHES_RETIREES
                and cas.affiliation not in statuts_des_emplois(simulateur, code)):
            # Une carrière qu'aucune fiche ne bonifie n'a rien à perdre au
            # retrait : aucun cas type de la grille n'est policier ni pompier,
            # et le militaire n'a que la sienne.
            continue
        carriere = carriere_variante(simulateur, cas, generation, age)
        if code == "retraite_anticipee_handicap" and carriere.incapacite_permanente is None:
            # Une carrière qui ne déclare aucune incapacité n'a rien à
            # perdre au retrait : aucun cas type de la grille n'en déclare.
            continue
        if code == "apprentissage" and not (carriere.chronologie and _contrats(carriere)):
            # Ni une carrière sans contrat d'apprentissage : aucun cas type
            # de la grille n'est apprenti.
            continue
        liquidee = variante.calculer(carriere)
        sans[code] = (liquidee.pension_annuelle, liquidee.trimestres_requis)
    avpf = somme_ordonnee(a.montant for a in reelle.avantages_appliques if a.code == "avpf")
    return _ecarts(cas, reelle.pension_annuelle, reelle.trimestres_requis, avpf, sans)
