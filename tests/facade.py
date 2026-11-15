"""La façade des tests : les entrées du moteur Python que les tests appellent,
servies par le portage sous leurs noms (action 161, note de décision 0007).

Un test du moteur bâtit sa carrière, la simule ou la liquide, et compare ce
qu'il lit à la valeur que la source donne. Ici, les mêmes noms — ``Simulateur``
et ses bâtisseurs, ``simulateur.scenario_actuel.calculer``,
``Carriere.depuis_profil`` et ``depuis_parcours``, ``reversion`` — demandent le
calcul au moteur JavaScript, par le pont (``pont.facade``), et rendent ce qu'il
calcule sous les types du Python, lus strictement (``pont.lu_strictement``).
Un fichier de tests y passe en changeant ses imports, ses tests inchangés :
ce qu'il éprouve alors est le moteur du site, contre la même valeur.

La façade vit dans un module à elle tant que le jumeau Python vit : les
confrontations, qui font refaire au jumeau ce que le portage calcule, gardent
les entrées du Python.

**Ce que la façade ne sait pas transmettre, elle le refuse**
(:class:`NonTransmissible`), au lieu de l'ignorer : le portage calculerait sur
le modèle intact, et le test verdirait à tort. Sont refusés : une série qui
n'est pas celle d'un simulateur de la façade ; un moteur qui n'est pas le
sien ; une retouche de son simulateur ou de son moteur ; tout appel sous un
modèle modifié (``memoire.modele_modifie``, que ``monkeypatch`` ouvre) ; des
variantes d'univers ; et la lecture, sur son simulateur, d'une règle qu'elle
ne sert pas. Les données du simulateur — ses séries, son catalogue, ses
affiliations — se lisent, par leurs chargeurs Python, qui restent.

**Les tables du moteur** se lisent par leur nom et leur méthode
(``simulateur.scenario_actuel.reversions.minimum(2025)``) : le portage appelle
la méthode de sa table, parmi celles que ``pont.TABLES_DE_LA_FACADE`` déclare,
et ce qu'elle rend revient sous le type que la méthode du jumeau annonce. Une
règle du moteur Python à qui un test passe le moteur de la façade n'y lit
rien : elle tournerait en Python sur les tables du portage.

**Les règles du droit** se demandent par leur module et leur nom
(``ouvrir.duree_requise(moteur, periode, carriere)``), que le fichier importe
d'ici : le portage appelle la sienne, parmi celles que
``pont.REGLES_DE_LA_FACADE`` déclare, sur le moteur d'un simulateur de la
façade, une période de son catalogue, une carrière et l'une de ses lignes,
une date, des valeurs simples. Ce qui n'en est pas — le moteur Python, une période retouchée, un
objet du moteur — n'arriverait pas au portage : la règle est refusée.

**Le constructeur du compte** (``simulateur.constructeur``,
``simulateur.constructeur_employeur``, ``simulateur.constructeur_prelevement``)
sert ce que ``pont.CONSTRUCTEURS_DE_LA_FACADE`` déclare — la cotisation d'une
année, le taux porté au compte, le compte entier —, ses arguments transmis
comme ceux d'une table. Le régime unique d'après la bascule
(``simulateur.regime_fusionne``) se lit sur le simulateur, et passe au
constructeur par sa marque ; un autre ne passe pas.

Bâti à la main des données d'un simulateur de la façade, sous d'autres
paramètres (``ConstructeurCompte``), il est celui du portage sous ceux-là.

**Le relevé des droits** (``releve.construire``, ses drapeaux compris)
revient en données, ce que les tests en lisent : ses lignes et ses groupes,
sa coordination, ses durées, ses points et ses cotisations, et ce que chaque
étape écrit sous son schéma. Ses étapes se servent aussi seules
(``coordonner.coordonner``, ``compter.compter``, ``acquerir.acquerir``),
refaites par le portage de la carrière et des drapeaux dont elles viennent.
Ses durées repassent au portage, qui les refait du relevé de leur carrière,
quand une règle les reçoit (``liquider.duree_du_regime_aligne``) : celles
du relevé sous ses drapeaux par défaut seulement.

**Un test resté sur le moteur Python**, dans un fichier basculé, porte la
marque ``sur_le_moteur_python`` et sa raison : le temps de ce test, les
entrées de son fichier et son simulateur redeviennent ceux du Python
(:func:`entrees_du_test`, :func:`simulateur_du_test`).
"""

from __future__ import annotations

import dataclasses
import datetime
import inspect
import os
import shutil
import sys
import typing
from pathlib import Path

import pytest

from retraite_notionnelle import carriere as _carriere
from retraite_notionnelle import castypes as _castypes
from retraite_notionnelle import echeancier as _echeancier
from retraite_notionnelle import journal as _journal
from retraite_notionnelle import memoire, pont
from retraite_notionnelle import pilote as _pilote
from retraite_notionnelle import revalorisation as _revalorisation
from retraite_notionnelle import simulateur as _simulateur
from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.config import ContributionEtat, Parametres
from retraite_notionnelle.donnees.mortalite import DonneesMortalite
from retraite_notionnelle.donnees.regimes import PeriodeRegime, Regime
from retraite_notionnelle.pont import NonTransmissible
from retraite_notionnelle.droit import acquerir as _acquerir
from retraite_notionnelle.droit import commun as _commun
from retraite_notionnelle.droit import compter as _compter
from retraite_notionnelle.droit import coordonner as _coordonner
from retraite_notionnelle.droit import completer as _completer
from retraite_notionnelle.droit import cultes as _cultes
from retraite_notionnelle.droit import departs as _departs
from retraite_notionnelle.droit import foyer as _foyer
from retraite_notionnelle.droit import invalidite as _invalidite
from retraite_notionnelle.droit import liquidation as _liquidation
from retraite_notionnelle.droit import liquider as _liquider
from retraite_notionnelle.droit import ouvrir as _ouvrir
from retraite_notionnelle.droit import releve as _releve
from retraite_notionnelle.droit import reversion as _reversion
from retraite_notionnelle.moteur import compte as _compte
from retraite_notionnelle.moteur.fusion import RegimeFusionne
from retraite_notionnelle.scenarios import actuel as _actuel

#: Les données du simulateur Python que la façade laisse lire : des chargeurs,
#: qui restent en Python (note de décision 0006), et aucune règle.
DONNEES = frozenset({"catalogue", "affiliations"})


#: Les entrées du moteur Python que la façade sert, sous leurs noms ;
#: ``droit.etapes``, les étapes de la liquidation, chacune seule.
ENTREES = ("simulateur.simuler", "scenario_actuel.calculer", "reversion.reversion",
           "simulateur.carriere_simple", "simulateur.carriere_parcours",
           "simulateur.carriere_releve", "carriere.depuis_profil", "carriere.depuis_parcours",
           "carriere.depuis_releve", "releve.construire", "simulateur.regime_fusionne", "liquidation.liquider",
           "liquidation.demande_de_depart", "coordonner.coordonner", "compter.compter",
           "acquerir.acquerir", "compter.cumul_plafonne", "compter.des_regimes",
           "droit.etapes", "compter.trimestres_du_contrat", "compter.jours_par_annee",
           "revalorisation.faire_vivre", "commun.periode_de_liquidation",
           "revalorisation.majorer_les_petites_pensions", "revalorisation.actuel_aujourd_hui",
           "simulateur.proposition", "simulateur.carriere_proposition", "carriere.prolongee",
           "simulateur.garantie_vieillesse", "echeancier.parcourir", "simulateur.echeancier",
           "echeancier.depart_de", "echeancier.sortes", "journal.operer",
           "pilote.age_de_depart")

#: Les méthodes des tables du moteur que la façade sert, par table.
TABLES = pont.TABLES_DE_LA_FACADE

#: Les règles du droit que la façade sert, par module.
REGLES = pont.REGLES_DE_LA_FACADE

#: Les constantes du droit que la façade lit au portage, par module.
CONSTANTES = pont.CONSTANTES_DE_LA_FACADE

#: Le salaire moyen des séries du simulateur, une fonction de l'année, en
#: argument d'une méthode de table (``grilles.forfait``) : le portage y met
#: le sien.
SALAIRE_MOYEN = pont.SALAIRE_MOYEN

#: Les méthodes des constructeurs du compte que la façade sert, par
#: constructeur.
CONSTRUCTEURS = pont.CONSTRUCTEURS_DE_LA_FACADE

#: Les séries de chaque simulateur de la façade qui les a données, et ses
#: paramètres : un bâtisseur de la carrière reconnaît ainsi celles qu'on lui
#: passe (:func:`_parametres_des_series`).
_SERIES: dict[int, tuple[object, Parametres]] = {}


def _demander(entree: str, parametres: Parametres, *arguments):
    """L'entrée, demandée au portage sous ``parametres`` — sur le modèle
    intact seulement."""
    if not memoire.modele_intact():
        raise NonTransmissible(
            f"{entree} : modèle modifié (monkeypatch, memoire.modele_modifie) — ce que le "
            "test remplace en Python, le portage ne le voit pas")
    return pont.facade(entree, *arguments, parametres=parametres)


def _options(batisseur, *arguments, **options) -> dict:
    """Les arguments d'un bâtisseur de carrière, par leur nom, liés comme le
    Python les lie — un argument inconnu ou en double est une ``TypeError`` —,
    sans les séries, que le portage a."""
    lies = inspect.signature(batisseur).bind(*arguments, **options).arguments
    return {nom: valeur for nom, valeur in lies.items() if nom != "macro"}


def _parametres_des_series(macro) -> Parametres:
    """Les paramètres du simulateur de la façade dont ``macro`` est les
    séries : le portage bâtit la carrière sur les siennes, sous eux."""
    connue = _SERIES.get(id(macro))
    if connue is None or connue[0] is not macro:
        raise NonTransmissible(
            "série passée en argument que la façade ne sait pas transmettre : le portage "
            "bâtit la carrière sur les séries d'un simulateur de la façade (simulateur.macro)")
    return connue[1]


class _Ferme:
    """Un objet de la façade : il ne se modifie pas, et ne laisse lire que ce
    qu'il sert."""

    def __setattr__(self, nom, valeur):
        raise NonTransmissible(
            f"{type(self).__name__}.{nom} modifié : le portage ne verrait pas ce que le test "
            "pose sur la façade — la variante s'écrit en données, ou le test se porte à la main")

    __delattr__ = __setattr__

    def __getattr__(self, nom):
        if nom.startswith("__"):
            raise AttributeError(nom)
        raise NonTransmissible(
            f"{type(self).__name__}.{nom} : la façade ne sert pas cette règle du moteur "
            "Python — le test la demande au pont (pont.droit), ou se porte à la main")


class Table(_Ferme):
    """Une table du moteur d'un simulateur de la façade : celles de ses
    méthodes que la façade sert (:data:`TABLES`), appelées par le portage sur
    la sienne."""

    def __init__(self, moteur: ScenarioActuel, nom: str) -> None:
        object.__setattr__(self, "_moteur", moteur)
        object.__setattr__(self, "_nom", nom)

    def __getattr__(self, methode):
        if methode.startswith("__"):
            raise AttributeError(methode)
        if methode not in TABLES[self._nom]:
            raise NonTransmissible(
                f"{self._nom}.{methode} : la façade ne sert pas cette méthode de la table "
                "(pont.TABLES_DE_LA_FACADE) — le test la demande au pont, ou se porte à la main")
        jumelle = getattr(type(getattr(self._moteur._simulateur._donnees.scenario_actuel,
                                       self._nom)), methode)
        rendu = typing.get_type_hints(jumelle)["return"]
        simulateur = self._moteur._simulateur

        def servie(*arguments, **nommes):
            lies = inspect.signature(jumelle).bind(None, *arguments, **nommes)
            lies.apply_defaults()
            _, *valeurs = lies.arguments.values()
            return _demander_la_table(simulateur, self._nom, methode, rendu, valeurs)

        return servie


def _demander_la_table(simulateur: Simulateur, table: str, methode: str, rendu, valeurs):
    """La méthode d'une table, demandée au portage sous les paramètres du
    simulateur — sur le modèle intact seulement. Les séries du simulateur
    passent par leur marque ; d'autres séries ne passent pas."""
    if not memoire.modele_intact():
        raise NonTransmissible(
            f"{table}.{methode} : modèle modifié (monkeypatch, memoire.modele_modifie) — ce "
            "que le test remplace en Python, le portage ne le voit pas")
    return pont.table_du_moteur(table, methode, rendu,
                                *(_argument_de_table(simulateur, valeur) for valeur in valeurs),
                                parametres=simulateur.parametres)


def _argument_de_table(simulateur: Simulateur, valeur):
    """Un argument d'une méthode de table tel que le pont le transmet : les
    séries du simulateur par leur marque ; une période de son catalogue par
    son rang dans son régime ; une date en texte, comme le portage la tient ;
    une autre valeur telle quelle. Une période qui n'est pas de son catalogue,
    que le test aurait faite ou retouchée, ne lui parviendrait pas."""
    if valeur is simulateur._donnees.macro:
        return pont.SERIES
    if isinstance(valeur, RegimeFusionne):
        if valeur is not simulateur._regime_fusionne:
            raise NonTransmissible(
                "régime unique passé en argument qui n'est pas celui du simulateur de la "
                "façade (simulateur.regime_fusionne) : le portage ne le verrait pas")
        return pont.REGIME_FUSIONNE
    if type(valeur) is datetime.date:
        return valeur.isoformat()
    if isinstance(valeur, PeriodeRegime):
        return _periode_du_catalogue(simulateur, valeur)
    return valeur


def _periode_du_catalogue(simulateur: Simulateur, periode: PeriodeRegime):
    """Une période du catalogue du simulateur telle que le pont la transmet :
    par son rang dans son régime."""
    periodes = (simulateur._donnees.catalogue[periode.regime].periodes
                if periode.regime in simulateur._donnees.catalogue else ())
    rang = next((rang for rang, connue in enumerate(periodes) if connue is periode), None)
    if rang is None:
        raise NonTransmissible(
            f"période du régime {periode.regime} passée en argument qui n'est pas du "
            "catalogue du simulateur de la façade : le portage ne la verrait pas")
    return pont.PeriodeDuCatalogue(periode.regime, rang, periode.debut)


class ScenarioActuel(_Ferme):
    """Le moteur du scénario 1 d'un simulateur de la façade."""

    def __init__(self, simulateur: Simulateur) -> None:
        object.__setattr__(self, "_simulateur", simulateur)

    def __getattr__(self, nom):
        if nom.startswith("__"):
            raise AttributeError(nom)
        # Qui lit : une règle du moteur Python à qui le test a passé ce moteur
        # tournerait en Python sur les tables du portage.
        if sys._getframe(1).f_globals.get("__name__", "").startswith(_carriere.__package__ + "."):
            raise NonTransmissible(
                f"ScenarioActuel.{nom}, lu par une règle du moteur Python "
                f"({sys._getframe(1).f_globals['__name__']}.{sys._getframe(1).f_code.co_name}) : "
                "le moteur de la façade ne sert pas le moteur Python — le test reste sur le "
                "moteur Python, ou demande la règle au pont (pont.droit)")
        if nom in TABLES:
            return Table(self, nom)
        return super().__getattr__(nom)

    @property
    def macro(self):
        """Les séries du moteur : celles de son simulateur."""
        return self._simulateur.macro

    @property
    def parametres(self):
        """Les paramètres du moteur : ceux de son simulateur."""
        return self._simulateur.parametres

    def calculer(self, carriere, *drapeaux, **nommes):
        """``ScenarioActuel.calculer`` : le résultat entier du scénario 1, ses
        drapeaux liés comme le Python les lie."""
        lies = inspect.signature(_actuel.ScenarioActuel.calculer).bind(
            self, carriere, *drapeaux, **nommes)
        lies.apply_defaults()
        _, _, *valeurs = lies.arguments.values()
        resultat = _demander("scenario_actuel.calculer", self._simulateur.parametres,
                             pont.MOTEUR, carriere, *valeurs)
        if not nommes and not drapeaux:
            # « Faire vivre » reçoit ce résultat : le portage le refait de la
            # même carrière, sous ses drapeaux par défaut.
            _CALCULES[id(resultat)] = (resultat, carriere, self._simulateur)
            if len(_CALCULES) > _CALCULES_GARDES:
                del _CALCULES[next(iter(_CALCULES))]
        return resultat


#: Les catalogues que les simulateurs de la façade ont laissé lire, et leur
#: simulateur : une règle qui reçoit un régime du catalogue le demande au
#: portage sous ses paramètres (:meth:`_Commun.periode_de_liquidation`).
_CATALOGUES: dict[int, tuple] = {}

#: Les résultats du scénario 1 que la façade a rendus sous les drapeaux par
#: défaut, par leur identité : le résultat, sa carrière et son simulateur.
#: Les derniers seulement, que les tests d'un fichier relisent.
_CALCULES: dict[int, tuple] = {}
_CALCULES_GARDES = 512


def faire_vivre(simulateur, carriere, resultat, annee: int | None = None):
    """``revalorisation.faire_vivre`` : les pensions du scénario 1 menées à
    l'échéance de ``annee``, servies par le portage, qui refait ``resultat``
    de ``carriere``, et rendues sous le type du Python (``Revalorisee``). Le
    résultat doit être celui que le moteur de ce simulateur de la façade a
    rendu pour cette carrière, sous les drapeaux par défaut : un autre
    n'arriverait pas au portage."""
    return _sur_le_scenario_1("revalorisation.faire_vivre", simulateur, carriere, resultat,
                              annee)


def actuel_aujourd_hui(simulateur, carriere, resultat, annee: int | None = None):
    """``revalorisation.actuel_aujourd_hui`` : le système 1 servi en ``annee``
    — « faire vivre », puis « foyer et net » —, servi par le portage sous le
    type du Python (``ActuelAujourdhui``), sur le résultat que demande
    :func:`faire_vivre`."""
    return _sur_le_scenario_1("revalorisation.actuel_aujourd_hui", simulateur, carriere,
                              resultat, annee)


def _sur_le_scenario_1(entree: str, simulateur, carriere, resultat, annee: int | None):
    """L'entrée, sur le scénario 1 que le portage refait de ``carriere`` : le
    résultat doit être celui que le moteur de ce simulateur de la façade a
    rendu pour cette carrière, sous les drapeaux par défaut."""
    calcule = _CALCULES.get(id(resultat))
    if (not isinstance(simulateur, Simulateur) or calcule is None
            or calcule[0] is not resultat or calcule[1] is not carriere
            or calcule[2] is not simulateur):
        raise NonTransmissible(
            f"{entree} : un résultat que le portage ne refait pas — il "
            "refait le scénario 1 de la carrière, sous ses drapeaux par défaut, sur le "
            "moteur du simulateur de la façade qui l'a rendu (simulateur.scenario_actuel."
            "calculer(carriere))")
    return _demander(entree, simulateur.parametres, pont.SIMULATEUR, carriere, annee)


class PensionServie(_Ferme):
    """``revalorisation.PensionServie`` : la règle de chaque régime, d'une date
    à une autre, celle du simulateur de la façade — une marque, que le
    portage refait de ce simulateur, sous ses paramètres."""

    def __init__(self, simulateur: Simulateur) -> None:
        object.__setattr__(self, "_simulateur", simulateur)


def majorer_les_petites_pensions(moteur, resultat, datees, regimes, servie, a_l_effet,
                                 mensuel_2019, fin):
    """``revalorisation.majorer_les_petites_pensions`` : la majoration
    exceptionnelle de septembre 2023, servie par le portage, sur le moteur et
    la règle de chaque régime (:class:`PensionServie`) d'un même simulateur de
    la façade. Le résultat ne passe que par ses petites pensions : des
    avantages appliqués n'y arriveraient pas."""
    entree = "revalorisation.majorer_les_petites_pensions"
    if (not isinstance(moteur, ScenarioActuel) or not isinstance(servie, PensionServie)
            or servie._simulateur is not moteur._simulateur):
        raise NonTransmissible(
            f"{entree} : le moteur et la règle de chaque régime (facade.PensionServie) "
            "d'un même simulateur de la façade — un autre n'arriverait pas au portage")
    if list(getattr(resultat, "avantages_appliques", ())):
        raise NonTransmissible(f"{entree} : des avantages appliqués, que la façade ne "
                               "transmet pas au portage")
    return _demander(
        entree, moteur._simulateur.parametres, pont.SIMULATEUR,
        list(getattr(resultat, "petites_pensions", ())),
        [[pension, annee, debut.isoformat(), montant]
         for pension, annee, debut, montant in datees],
        list(regimes), list((a_l_effet or {}).items()), mensuel_2019, fin.isoformat())


class Echeancier(_Ferme):
    """``Echeancier`` : sur un simulateur de la façade, ``parcourir``, servi
    par le portage, l'échéance comprise ; puis ce que les tests en lisent —
    son journal (:class:`Journal`), le scénario 1 au départ (``au_depart``) et
    à l'échéance (``aujourd_hui``), la réversion qu'il liquide au décès de
    l'assuré (``reversion``). Les liquidations de son parcours se comptent
    dans ``liquidation.appels()``. Le reste de l'échéancier — ses durées au
    départ, sa retraite progressive — ne passe pas le pont, et se refuse."""

    def __init__(self, simulateur) -> None:
        if not isinstance(simulateur, Simulateur):
            raise NonTransmissible(
                "Echeancier : simulateur que la façade ne sait pas transmettre — l'échéancier "
                "se demande sur un simulateur de la façade")
        object.__setattr__(self, "simulateur", simulateur)
        object.__setattr__(self, "journal", Journal())
        object.__setattr__(self, "au_depart", None)
        object.__setattr__(self, "aujourd_hui", None)
        object.__setattr__(self, "reversion", None)

    def _lire(self, lu: dict) -> None:
        entrees = [dataclasses.replace(entree, contenu=_Decrit(entree.sorte,
                                                              lu["decrites"][entree.id]))
                   if entree.id in lu["decrites"] else entree for entree in lu["journal"]]
        object.__setattr__(self, "journal", Journal._des_entrees(entrees))
        object.__setattr__(self, "au_depart", lu["au_depart"])
        object.__setattr__(self, "aujourd_hui", lu["aujourd_hui"])
        object.__setattr__(self, "reversion", lu["reversion"])
        _APPELS[0] += lu["appels"]

    def parcourir(self, carriere, echeance: int | None = None):
        self._lire(_demander("echeancier.parcourir", self.simulateur.parametres,
                             pont.SIMULATEUR, carriere, echeance))
        return self.journal


class _Decrit(_Ferme):
    """Le contenu d'une entrée du journal qui ne passe pas le pont — une
    liquidation tient son contexte, les tables du moteur —, par ce que son
    contrat en décrit (``donnees()``), que le portage écrit ; le reste se
    refuse."""

    def __init__(self, sorte: str, donnee: dict) -> None:
        object.__setattr__(self, "sorte", sorte)
        object.__setattr__(self, "_donnee", donnee)

    def donnees(self) -> dict:
        return self._donnee


class Journal(_Ferme):
    """``journal.Journal`` : ses entrées tenues ici, sous le type du Python
    (``Entree``), qui porte leur contenu ; chaque inscription, ce qu'il sert
    pour une période et son état à une date, demandés au portage, qui refait
    le journal de ce qui date chaque entrée — son contenu, qu'il ne lit pas,
    n'y passe pas. Ce que le portage refuse d'inscrire lève la ``ValueError``
    du Python."""

    def __init__(self) -> None:
        object.__setattr__(self, "_entrees", [])

    @classmethod
    def _des_entrees(cls, entrees: list) -> "Journal":
        """Le journal de ces entrées, que le portage a déjà inscrites."""
        journal = cls()
        journal._entrees.extend(entrees)
        return journal

    def _operer(self, entrees: list, operation: str, *valeurs):
        datees = [{"id": e.id, "evenement": e.evenement, "inscrite_le": e.inscrite_le,
                   "debut": e.debut, "fin": e.fin, "sorte": e.sorte, "remplace": e.remplace,
                   "annule": e.annule} for e in entrees]
        return _demander("journal.operer", Parametres(), datees, operation, list(valeurs))

    def inscrire(self, entree):
        if not isinstance(entree, _journal.Entree):
            raise NonTransmissible("journal.inscrire : ce n'est pas une Entree du journal")
        self._operer([*self._entrees, entree], "inscrire")
        self._entrees.append(entree)
        return entree

    def __iter__(self):
        return iter(list(self._entrees))

    def __len__(self) -> int:
        return len(self._entrees)

    def entree(self, ident: str):
        for entree in self._entrees:
            if entree.id == ident:
                return entree
        raise KeyError(ident)

    def etat_au(self, date: str) -> list:
        return [self._entrees[rang] for rang in self._operer(self._entrees, "etat_au", date)]

    def servi(self, debut: str, fin: str | None = None, sorte: str | None = None) -> list:
        return [self._entrees[rang]
                for rang in self._operer(self._entrees, "servi", debut, fin, sorte)]

    def donnees(self) -> list[dict]:
        return [entree.donnees() for entree in self._entrees]


class Simulateur(_Ferme):
    """``Simulateur`` : ses bâtisseurs de carrière et son moteur du scénario 1
    servis par le portage, sous ses paramètres ; ses données lues par leurs
    chargeurs Python."""

    def __init__(self, parametres: Parametres | None = None, variantes=None) -> None:
        if variantes:
            raise NonTransmissible(
                "variantes d'univers : la façade ne les transmet pas — une étude les passe "
                "au pont dans sa demande (Simulateur.univers_de_la_demande)")
        donnees = _simulateur.Simulateur(parametres)
        object.__setattr__(self, "parametres", donnees.parametres)
        object.__setattr__(self, "_donnees", donnees)
        object.__setattr__(self, "scenario_actuel", ScenarioActuel(self))
        object.__setattr__(self, "_constructeurs", {})
        object.__setattr__(self, "_regime_fusionne", None)
        object.__setattr__(self, "_projection", None)

    @property
    def macro(self):
        """Les séries du simulateur, que ses tests lisent et passent aux
        bâtisseurs de la carrière : la façade s'en souvient."""
        macro = self._donnees.macro
        _SERIES[id(macro)] = (macro, self.parametres)
        return macro

    @property
    def regime_fusionne(self):
        """Le régime unique d'après la bascule, que le portage fusionne de son
        catalogue, sous les paramètres du simulateur : le même à chaque
        lecture, et le seul qu'un constructeur du compte reçoive."""
        if self._regime_fusionne is None:
            object.__setattr__(self, "_regime_fusionne", _demander(
                "simulateur.regime_fusionne", self.parametres, pont.SIMULATEUR))
        return self._regime_fusionne

    @property
    def mortalite(self):
        """Les données de mortalité du simulateur : ses quotients lus par
        leur chargeur, ses méthodes servies par le portage."""
        return _Mortalite(self)

    @property
    def indexation(self):
        """L'indexation du simulateur, une marque : elle ne se lit pas, et ne
        sert qu'à bâtir un constructeur du compte (:func:`ConstructeurCompte`)."""
        return _Indexation(self)

    def __getattr__(self, nom):
        if nom in DONNEES:
            donnee = getattr(self._donnees, nom)
            if nom == "catalogue":
                _CATALOGUES[id(donnee)] = (donnee, self)
            return donnee
        if nom in CONSTRUCTEURS:
            # Sous le taux entier de l'État, le simulateur du portage ne bâtit
            # pas de constructeur du prélèvement : c'est celui des scénarios 4
            # et 5 (``constructeurPrelevement``, ``moteur/js/simulateur.js``).
            if (nom == "constructeur_prelevement"
                    and self.parametres.contribution_etat == ContributionEtat.ENTIERE):
                nom = "constructeur_employeur"
            return self._constructeurs.setdefault(nom, Constructeur(self, nom))
        return super().__getattr__(nom)

    @property
    def scenario_liberal(self):
        """Le scénario 6, par sa garantie vieillesse seule."""
        return _ScenarioLiberal(self)

    def pour_la_projection(self) -> "Simulateur":
        """``Simulateur.pour_la_projection`` : le simulateur de la page Coût,
        sous les conventions du COR et sans le minimum vieillesse au scénario
        1, un simulateur de la façade, bâti une fois ; sous ces réglages,
        lui-même. Ce ne sont que des paramètres : le portage les reçoit."""
        if (self.parametres.conventions_cor
                and not self.parametres.minimum_vieillesse_dans_le_scenario_actuel):
            return self
        if self._projection is None:
            object.__setattr__(self, "_projection", Simulateur(dataclasses.replace(
                self.parametres, conventions_cor=True,
                minimum_vieillesse_dans_le_scenario_actuel=False)))
        return self._projection

    def simuler(self, carriere):
        """``Simulateur.simuler`` : la comparaison entière, son journal
        compris, sous les paramètres du simulateur, racine des données
        comprise."""
        comparaison = _demander("simulateur.simuler", self.parametres, pont.SIMULATEUR, carriere)
        # Le portage range ses simulateurs sous une clé qui ne lit pas les
        # neutralisations (``cleParametres`` de ``config.js``), qui ne
        # commandent rien : il rend celles du premier simulateur qu'il a bâti.
        if dataclasses.replace(comparaison.parametres,
                               racine_donnees=self.parametres.racine_donnees,
                               neutralisations=self.parametres.neutralisations) != self.parametres:
            raise RuntimeError("le portage a simulé sous d'autres paramètres que ceux du "
                               "simulateur de la façade")
        comparaison.parametres = self.parametres
        return comparaison

    def echeancier(self, carriere) -> Echeancier:
        """``Simulateur.echeancier`` : l'échéancier du scénario 1 parcouru
        pour la carrière, servi par le portage, qui date lui-même
        l'échéance."""
        echeancier = Echeancier(self)
        echeancier._lire(_demander("simulateur.echeancier", self.parametres, pont.SIMULATEUR,
                                   carriere))
        return echeancier

    def carriere_proposition(self, carriere):
        """``Simulateur.carriere_proposition`` : la carrière que la proposition
        fait liquider, reportée à son âge légal, ou celle qu'on lui passe."""
        reportee = _demander("simulateur.carriere_proposition", self.parametres,
                             pont.SIMULATEUR, carriere)
        return carriere if reportee is None else reportee

    def proposition(self, carriere):
        """``Simulateur.proposition`` : le scénario 6 sur cette carrière-là."""
        return _demander("simulateur.proposition", self.parametres, pont.SIMULATEUR, carriere)

    def carriere_simple(self, annee_naissance, sexe, affiliation, age_debut, age_liquidation,
                        **options):
        return _demander("simulateur.carriere_simple", self.parametres, pont.SIMULATEUR, _options(
            _carriere.Carriere.depuis_profil, annee_naissance=annee_naissance, sexe=sexe,
            affiliation=affiliation, age_debut=age_debut, age_liquidation=age_liquidation,
            macro=None, **options))

    def carriere_parcours(self, annee_naissance, sexe, metiers, age_liquidation, **options):
        return _demander("simulateur.carriere_parcours", self.parametres, pont.SIMULATEUR, _options(
            _carriere.Carriere.depuis_parcours, annee_naissance=annee_naissance, sexe=sexe,
            metiers=list(metiers), age_liquidation=age_liquidation, macro=None, **options))

    def carriere_releve(self, annee_naissance, sexe, releve, age_liquidation, **options):
        return _demander("simulateur.carriere_releve", self.parametres, pont.SIMULATEUR, _options(
            _carriere.Carriere.depuis_releve, annee_naissance=annee_naissance, sexe=sexe,
            releve=list(releve), age_liquidation=age_liquidation, macro=None, **options))


class _ScenarioLiberal(_Ferme):
    """Le scénario 6 d'un simulateur de la façade : sa garantie vieillesse,
    servie par le portage."""

    def __init__(self, simulateur: Simulateur) -> None:
        object.__setattr__(self, "_simulateur", simulateur)

    def _garantie_vieillesse(self, carriere, pension_contributive: float,
                             rente_capitalisee: float = 0.0):
        return _demander("simulateur.garantie_vieillesse", self._simulateur.parametres,
                         pont.SIMULATEUR, carriere, pension_contributive, rente_capitalisee)


def prolongee(carriere, age_liquidation: float, macro, attente_travaillee: bool = True):
    """``Carriere.prolongee`` : la carrière poursuivie jusqu'à un départ à
    ``age_liquidation``, par le portage, sur les séries du simulateur de la
    façade qui les a données ; elle-même quand le départ n'est pas plus
    tardif."""
    parametres = _parametres_des_series(macro)
    prolongee_ = _demander("carriere.prolongee", parametres, pont.SIMULATEUR, carriere,
                           age_liquidation, attente_travaillee)
    return carriere if prolongee_ is None else prolongee_


class _Mortalite(_Ferme):
    """``Simulateur.mortalite`` : ses quotients observés, des données, lus
    par leur chargeur Python ; celles de ses méthodes que la façade sert
    (``pont.MORTALITE_DE_LA_FACADE``), appelées par le portage sur les
    siennes."""

    def __init__(self, simulateur: Simulateur) -> None:
        object.__setattr__(self, "_simulateur", simulateur)

    @property
    def _quotients_observes(self):
        return self._simulateur._donnees.mortalite._quotients_observes

    def __getattr__(self, methode):
        if methode.startswith("__"):
            raise AttributeError(methode)
        if methode not in pont.MORTALITE_DE_LA_FACADE:
            raise NonTransmissible(
                f"mortalite.{methode} : la façade ne sert pas cette méthode de la mortalité "
                "(pont.MORTALITE_DE_LA_FACADE) — le test la demande au pont, ou se porte à "
                "la main")
        jumelle = getattr(DonneesMortalite, methode)
        rendu = typing.get_type_hints(jumelle)["return"]
        simulateur = self._simulateur

        def servie(*arguments, **nommes):
            if not memoire.modele_intact():
                raise NonTransmissible(
                    f"mortalite.{methode} : modèle modifié (monkeypatch, "
                    "memoire.modele_modifie) — le portage ne le voit pas")
            lies = inspect.signature(jumelle).bind(None, *arguments, **nommes)
            lies.apply_defaults()
            _, *valeurs = lies.arguments.values()
            return pont.mortalite_du_simulateur(methode, rendu, *valeurs,
                                                parametres=simulateur.parametres)

        return servie


class Constructeur(_Ferme):
    """Un constructeur du compte d'un simulateur de la façade : celles de ses
    méthodes que la façade sert (:data:`CONSTRUCTEURS`), appelées par le
    portage sur le sien, leurs arguments transmis comme ceux d'une méthode de
    table."""

    def __init__(self, simulateur: Simulateur, nom: str) -> None:
        object.__setattr__(self, "_simulateur", simulateur)
        object.__setattr__(self, "_nom", nom)

    def __getattr__(self, methode):
        if methode.startswith("__"):
            raise AttributeError(methode)
        if methode not in CONSTRUCTEURS[self._nom]:
            raise NonTransmissible(
                f"{self._nom}.{methode} : la façade ne sert pas cette méthode du constructeur "
                "(pont.CONSTRUCTEURS_DE_LA_FACADE) — le test la demande au pont, ou se porte "
                "à la main")
        jumelle = getattr(_compte.ConstructeurCompte, methode)
        rendu = typing.get_type_hints(jumelle, vars(_compte))["return"]
        simulateur = self._simulateur

        def servie(*arguments, **nommes):
            lies = inspect.signature(jumelle).bind(None, *arguments, **nommes)
            lies.apply_defaults()
            _, *valeurs = lies.arguments.values()
            if not memoire.modele_intact():
                raise NonTransmissible(
                    f"{self._nom}.{methode} : modèle modifié (monkeypatch, "
                    "memoire.modele_modifie) — ce que le test remplace en Python, le portage "
                    "ne le voit pas")
            return pont.constructeur_du_compte(
                self._nom, methode, rendu,
                *(_argument_de_table(simulateur, valeur) for valeur in valeurs),
                parametres=simulateur.parametres)

        return servie


class _Indexation(_Ferme):
    """L'indexation d'un simulateur de la façade, que le portage refait sous
    ses paramètres : une marque, qu'on ne lit pas."""

    def __init__(self, simulateur: Simulateur) -> None:
        object.__setattr__(self, "_simulateur", simulateur)


#: Les réglages que lisent les données d'un simulateur que reçoit un
#: constructeur du compte — ses séries, son catalogue, ses affiliations, son
#: indexation (``simulateur.py``, ``moteur/indexation.py``).
REGLAGES_DES_DONNEES = ("racine_donnees", "scenario_projection", "trajectoire_emploi",
                        "conventions_cor", "lissage_indexation", "plancher_indexation",
                        "mode_indexation")

#: Les simulateurs de la façade que ``ConstructeurCompte`` a bâtis, par
#: paramètres.
_SOUS_D_AUTRES_PARAMETRES: dict[Parametres, Simulateur] = {}


def ConstructeurCompte(macro, catalogue, affiliations, indexation, parametres) -> Constructeur:
    """``ConstructeurCompte`` bâti des données d'un simulateur de la façade,
    sous d'autres paramètres : le constructeur du portage sous ceux-là
    (``Simulateur._constructeur_variante`` du Python le bâtit ainsi). Des
    données d'un autre simulateur, ou que ces paramètres feraient autres
    (:data:`REGLAGES_DES_DONNEES`), n'arriveraient pas au portage : refusées."""
    if not isinstance(indexation, _Indexation):
        raise NonTransmissible(
            "ConstructeurCompte : indexation qui n'est pas celle d'un simulateur de la "
            "façade (simulateur.indexation) — le portage refait la sienne")
    simulateur = indexation._simulateur
    donnees = simulateur._donnees
    for nom, recue, sienne in (("séries", macro, donnees.macro),
                               ("catalogue", catalogue, donnees.catalogue),
                               ("affiliations", affiliations, donnees.affiliations)):
        if recue is not sienne:
            raise NonTransmissible(
                f"ConstructeurCompte : {nom} d'un autre simulateur que celui de "
                "l'indexation — le portage refait les siennes")
    autres = [nom for nom in REGLAGES_DES_DONNEES
              if getattr(parametres, nom) != getattr(simulateur.parametres, nom)]
    if autres:
        raise NonTransmissible(
            f"ConstructeurCompte : paramètres qui changent les données reçues "
            f"({', '.join(autres)}) — le constructeur se demande au simulateur de la façade "
            "sous ces paramètres")
    if parametres not in _SOUS_D_AUTRES_PARAMETRES:
        _SOUS_D_AUTRES_PARAMETRES[parametres] = Simulateur(parametres)
    return _SOUS_D_AUTRES_PARAMETRES[parametres].constructeur


class Carriere(_carriere.Carriere):
    """``Carriere``, ses trois bâtisseurs servis par le portage : la carrière
    qu'ils rendent est une ``Carriere`` du Python, le type que le pont
    échange."""

    @classmethod
    def depuis_profil(cls, *arguments, **options):
        return _batie("carriere.depuis_profil", _carriere.Carriere.depuis_profil,
                      arguments, options)

    @classmethod
    def depuis_parcours(cls, *arguments, **options):
        return _batie("carriere.depuis_parcours", _carriere.Carriere.depuis_parcours,
                      arguments, options)

    @classmethod
    def depuis_releve(cls, *arguments, **options):
        return _batie("carriere.depuis_releve", _carriere.Carriere.depuis_releve,
                      arguments, options)


def _batie(entree: str, batisseur, arguments: tuple, options: dict):
    """La carrière d'un bâtisseur de ``Carriere``, sous les paramètres du
    simulateur dont on lui passe les séries."""
    lies = inspect.signature(batisseur).bind(*arguments, **options).arguments
    parametres = _parametres_des_series(lies["macro"])
    return _demander(entree, parametres, pont.SIMULATEUR,
                     _options(batisseur, *arguments, **options))


def reversion(moteur, pensions, carriere, annee, *arguments, **options):
    """``droit.reversion.reversion``, sur le moteur d'un simulateur de la
    façade : ses arguments liés comme le Python les lie, les régimes servis en
    capital en liste."""
    if not isinstance(moteur, ScenarioActuel):
        raise NonTransmissible(
            "moteur passé en argument que la façade ne sait pas transmettre : la réversion "
            "se calcule sur le moteur d'un simulateur de la façade (simulateur.scenario_actuel)")
    lies = inspect.signature(_reversion.reversion).bind(
        moteur, pensions, carriere, annee, *arguments, **options)
    lies.apply_defaults()
    valeurs = dict(lies.arguments)
    valeurs["en_capital"] = sorted(valeurs["en_capital"])
    del valeurs["moteur"]
    return _demander("reversion.reversion", moteur._simulateur.parametres, pont.MOTEUR,
                     *valeurs.values())


# -- les règles du droit ---------------------------------------------------------------

#: Les valeurs simples qu'une règle reçoit telles quelles.
_SIMPLES = (bool, int, float, str, type(None))


class Regles(_Ferme):
    """Un module de règles du droit, sous le nom de son jumeau : celles de ses
    règles que la façade sert (:data:`REGLES`), appelées par le portage, et
    ses constantes, des valeurs simples, telles quelles."""

    def __init__(self, nom: str, jumeau) -> None:
        object.__setattr__(self, "_nom", nom)
        object.__setattr__(self, "_jumeau", jumeau)

    def __getattr__(self, regle):
        if regle in CONSTANTES.get(self._nom, ()):
            # Une constante du portage, que le jumeau tient ailleurs ou pas.
            return pont.constante_du_droit(self._nom, regle)
        # Ce que le jumeau ne porte pas manque ici comme à un module : pytest
        # sonde ainsi ce qu'un fichier de tests importe.
        if regle.startswith("__") or not hasattr(self._jumeau, regle):
            raise AttributeError(f"{self._nom}.{regle}")
        if type(getattr(self._jumeau, regle)) in _SIMPLES:
            # Une constante du module, une valeur simple : rien à calculer.
            return getattr(self._jumeau, regle)
        if regle not in REGLES[self._nom]:
            raise NonTransmissible(
                f"{self._nom}.{regle} : la façade ne sert pas cette règle du droit "
                "(pont.REGLES_DE_LA_FACADE) — le test reste sur le moteur Python, ou la "
                "demande au pont")
        jumelle = getattr(self._jumeau, regle)
        rendu = _type_rendu(jumelle, vars(self._jumeau))

        def servie(*arguments, **nommes):
            lies = inspect.signature(jumelle).bind(*arguments, **nommes)
            lies.apply_defaults()
            return _demander_la_regle(self._nom, regle, rendu, lies.arguments)

        return servie


def _type_rendu(jumelle, noms: dict):
    """Le type que la règle du jumeau annonce rendre, lu seul : ceux de ses
    arguments nomment des types que son module n'importe que pour les
    annoncer. Un type rendu que le module n'importe que pour l'annoncer
    (``DerogationActive``) se lit dans le module du moteur qui le tient."""
    from retraite_notionnelle.scenarios import actuel

    def porteur(): ...
    porteur.__annotations__ = {"return": jumelle.__annotations__["return"]}
    return typing.get_type_hints(porteur, globalns={**vars(actuel), **noms})["return"]


def _demander_la_regle(module: str, regle: str, rendu, arguments: dict):
    """La règle, demandée au portage sous les paramètres du simulateur dont
    elle reçoit le moteur, les réglages de référence quand elle n'en reçoit
    pas — sur le modèle intact seulement."""
    if not memoire.modele_intact():
        raise NonTransmissible(
            f"{module}.{regle} : modèle modifié (monkeypatch, memoire.modele_modifie) — ce "
            "que le test remplace en Python, le portage ne le voit pas")
    simulateur = None
    if "moteur" in arguments:
        if not isinstance(arguments["moteur"], ScenarioActuel):
            raise NonTransmissible(
                f"{module}.{regle} : moteur passé en argument que la façade ne sait pas "
                "transmettre — la règle se demande sur le moteur d'un simulateur de la façade "
                "(simulateur.scenario_actuel)")
        simulateur = arguments["moteur"]._simulateur
    for durees in (valeur for valeur in arguments.values()
                   if isinstance(valeur, (Durees, Droits))):
        # Le portage refait ces durées du relevé de leur carrière, sous les
        # paramètres du simulateur qui les a rendues : la règle les reçoit
        # avec cette carrière-là, et sur ce simulateur-là.
        if "carriere" in arguments and arguments["carriere"] is not durees._carriere:
            raise NonTransmissible(
                f"{module}.{regle} : durées ou droits d'une autre carrière que celle de la "
                "règle — le portage les refait du relevé de la carrière qu'il reçoit")
        if simulateur is not None and simulateur.parametres != durees._simulateur.parametres:
            raise NonTransmissible(
                f"{module}.{regle} : durées rendues sous d'autres paramètres que ceux du moteur")
        simulateur = durees._simulateur
    for regime in (valeur for valeur in arguments.values() if isinstance(valeur, Regime)):
        # Un régime du catalogue : le portage le prend dans le sien, sous les
        # paramètres du simulateur qui l'a laissé lire.
        du_regime = _simulateur_du_regime(regime)
        if du_regime is None or (simulateur is not None
                                 and simulateur.parametres != du_regime.parametres):
            raise NonTransmissible(
                f"{module}.{regle} : un régime qui n'est pas du catalogue d'un simulateur de "
                "la façade (simulateur.catalogue), sous les paramètres du moteur — le "
                "portage ne le verrait pas")
        simulateur = simulateur or du_regime
    parametres = None if simulateur is None else simulateur.parametres
    if "macro" in arguments:
        # Les séries d'un simulateur de la façade : le portage prend les
        # siennes, sous les paramètres de ce simulateur-là.
        des_series = _parametres_des_series(arguments["macro"])
        if parametres is not None and parametres != des_series:
            raise NonTransmissible(
                f"{module}.{regle} : séries d'un autre simulateur que celui du moteur")
        parametres = des_series
    lu = pont.regle_du_droit(
        module, regle, rendu,
        *(_argument_de_regle(f"{module}.{regle}", simulateur, nom, valeur,
                             arguments.get("carriere"))
          for nom, valeur in arguments.items()),
        parametres=parametres)
    carriere = arguments.get("carriere")
    if (isinstance(lu, _carriere.Carriere) and isinstance(carriere, _carriere.Carriere)
            and pont.carriere_en_donnees(lu) == pont.carriere_en_donnees(carriere)):
        # Une règle qui rend la carrière qu'elle reçoit, intacte
        # (``ouvrir.indemnisation_bornee``), la rend elle-même, comme le
        # jumeau : le pont n'en transmet qu'une copie.
        return carriere
    return lu


def _argument_de_regle(regle: str, simulateur: Simulateur | None, nom: str, valeur,
                       carriere=None):
    """Un argument d'une règle du droit tel que le pont le transmet : le
    moteur du simulateur par sa marque ; un régime de son catalogue par son
    code ; une période de son catalogue par son rang ; une carrière, une date au mois, une valeur simple, une suite de
    valeurs simples ou de couples de valeurs simples, la règle d'une fiche —
    un dictionnaire de valeurs simples sous des noms —, un éligible au
    minimum (``pont.TYPES_DE_LA_FACADE``), tels quels ; une ligne de la
    carrière de la règle, par son rang ; un dictionnaire que le portage lit
    en ``Map`` (``pont.TABLES_DES_REGLES``), en table. Le reste — un objet du
    moteur Python, un dictionnaire que la façade ne déclare pas en table —
    n'arriverait pas au portage sous son type."""
    if nom == "moteur":
        return pont.MOTEUR
    if nom == "macro":
        # Les séries d'un simulateur de la façade, par leur marque
        # (``_demander_la_regle`` en a pris les paramètres).
        _parametres_des_series(valeur)
        return pont.SERIES
    if nom in pont.TABLES_DES_REGLES.get(regle, ()):
        # Le portage lit l'argument en ``Map`` : il passe en table, ses clés
        # sous leur type ; ``None``, la table vide que le Python lui substitue.
        table = {} if valeur is None else valeur
        if type(table) is dict and all(type(cle) in _SIMPLES and type(element) in _SIMPLES
                                       for cle, element in table.items()):
            return pont.Table(tuple(table.items()))
        raise NonTransmissible(
            f"{regle} : argument {nom}, une table que le portage lit en Map, dont une clé ou "
            "une valeur n'est pas simple — elle n'arriverait pas au portage sous son type")
    if isinstance(valeur, PeriodeRegime) and simulateur is not None:
        return _periode_du_catalogue(simulateur, valeur)
    if isinstance(valeur, Regime) and simulateur is not None:
        return pont.RegimeDuCatalogue(valeur.code)
    if type(valeur) in _SIMPLES or isinstance(valeur, (_carriere.Carriere, DateMois)):
        return valeur
    if type(valeur) in (tuple, list) and all(type(element) in _SIMPLES for element in valeur):
        return list(valeur)
    if type(valeur) in (tuple, list) and all(
            type(element) in (tuple, list) and all(type(membre) in _SIMPLES for membre in element)
            for element in valeur):
        return [list(element) for element in valeur]
    if type(valeur) is dict and all(type(cle) is str and type(element) in _SIMPLES
                                    for cle, element in valeur.items()):
        return dict(valeur)
    if dataclasses.is_dataclass(valeur) and type(valeur).__name__ in pont.TYPES_DE_LA_FACADE:
        return valeur
    if type(valeur) in (tuple, list) and all(type(element) is _carriere.LigneRelevee
                                             for element in valeur):
        # Un relevé saisi, ses lignes de données, que le pont passe champ à champ.
        return list(valeur)
    if isinstance(valeur, _liquidation.Contexte):
        return pont.ContexteDuMoteur(tuple(_contexte_de_la_facade(
            regle, None if simulateur is None else simulateur.scenario_actuel, valeur)))
    if isinstance(valeur, pont.DureesPosees):
        return valeur
    if isinstance(valeur, Durees):
        if not valeur._source.du_releve:
            raise NonTransmissible(
                f"{regle} : argument {nom}, des durées comptées sous d'autres drapeaux que "
                "ceux du relevé — le portage les refait du relevé de la carrière, sous ses "
                "drapeaux par défaut")
        return pont.DureesDuReleve(valeur._carriere)
    if isinstance(valeur, Droits):
        if not valeur._source.du_releve:
            raise NonTransmissible(
                f"{regle} : argument {nom}, des droits acquis sous d'autres drapeaux que "
                "ceux du relevé — le portage les refait du relevé de la carrière, sous ses "
                "drapeaux par défaut")
        return pont.DroitsDuReleve(valeur._carriere)
    if isinstance(valeur, _carriere.AnneeCarriere):
        # Le portage relit la ligne, par son rang, dans la carrière que la
        # règle reçoit : une ligne qui n'en est pas n'y arriverait pas.
        rang = next((rang for rang, ligne in enumerate(getattr(carriere, "lignes", ()))
                     if ligne is valeur), None)
        if rang is None:
            raise NonTransmissible(
                f"{regle} : argument {nom}, une ligne qui n'est pas de la carrière de la "
                "règle — le portage la relit, par son rang, dans cette carrière")
        return pont.LigneDeCarriere(carriere, rang)
    raise NonTransmissible(
        f"{regle} : argument {nom} ({type(valeur).__name__}) que la façade ne sait pas "
        "transmettre au portage — le test reste sur le moteur Python, ou se porte à la main")


# -- les étapes de la liquidation, chacune seule ---------------------------------------
#
# ``ouvrir.ouvrir``, ``liquider.liquider_chaque_regime`` et
# ``completer.completer`` reçoivent le relevé et ce que l'étape précédente a
# écrit, objets du moteur que le pont ne passe pas. Chaque étape de la façade
# garde donc son relevé et la chaîne des étapes qui l'ont faite, leurs
# options comprises : le portage refait le relevé de sa carrière, sous ses
# drapeaux, puis chaque étape de la chaîne (``droit.etapes`` de ``pont.mjs``).
# Le contexte d'une liquidation passe par ses neutralisations, sur le moteur
# de l'étape ; une date d'observation, une hypothèse n'arriveraient pas au
# portage.


def _contexte_de_la_facade(entree: str, moteur, contexte):
    """Les neutralisations du contexte, triées, que le portage reçoit ;
    ``None`` sans contexte."""
    if contexte is None:
        return None
    if not isinstance(contexte, _liquidation.Contexte) or contexte.univers is not moteur:
        raise NonTransmissible(
            f"{entree} : contexte d'un autre moteur que celui de l'étape — le portage le "
            "refait sur le moteur du simulateur de la façade (simulateur.scenario_actuel)")
    if (contexte.observation, contexte.hypothese) != (None, None):
        raise NonTransmissible(
            f"{entree} : contexte qui porte plus que le moteur et ses neutralisations "
            "(observation, hypothèse) — le portage ne le verrait pas")
    return sorted(contexte.neutralisations)


class Etape(_Ferme):
    """Ce qu'une étape de la liquidation a écrit, lu du portage : ses champs,
    et ``donnees()``, ce que son schéma décrit — l'ouverture, ``requis``,
    ``age``, ``motif``, ``trimestres_cotises`` ; les pensions, ``regimes`` et
    ``taux`` ; les compléments, ``regimes`` et ``total``. Elle garde son
    relevé et la chaîne des étapes dont elle vient, que le portage refait."""

    def __init__(self, releve, chaine: tuple, lu: dict) -> None:
        object.__setattr__(self, "_releve", releve)
        object.__setattr__(self, "_chaine", chaine)
        for nom, valeur in lu.items():
            object.__setattr__(self, "_donnees" if nom == "donnees" else nom, valeur)

    def donnees(self) -> dict:
        return self._donnees


def _etape(entree: str, moteur, releve, chaine: tuple) -> Etape:
    """L'étape au bout de ``chaine``, sur le relevé de la façade ``releve``,
    demandée au portage."""
    _moteur_de_la_facade(entree, moteur)
    if not isinstance(releve, Releve) or releve._source.moteur is not moteur:
        raise NonTransmissible(
            f"{entree} : relevé que la façade ne sait pas transmettre — il vient de "
            "releve.construire de la façade, sur le moteur de l'étape")
    source = releve._source
    return Etape(releve, chaine, source.demander(
        "droit.etapes", source.avantages_non_contributifs, source.points_gratuits,
        source.liquider_successions, [[nom, options] for nom, options in chaine]))


def _precedente(entree: str, nom: str, etape, releve, attendue: str) -> tuple:
    """La chaîne de l'étape précédente, qui doit être de ce relevé-là."""
    if (not isinstance(etape, Etape) or etape._releve is not releve
            or etape._chaine[-1][0] != attendue):
        raise NonTransmissible(
            f"{entree} : {nom} qui ne vient pas de l'étape « {attendue} » de la façade sur ce "
            "relevé — le portage refait chaque étape du relevé qu'il reçoit")
    return etape._chaine


def _regimes(regimes) -> list | None:
    return None if regimes is None else sorted(regimes)


class _Ouvrir(Regles):
    """``droit.ouvrir`` : ses règles, et l'étape ``ouvrir``."""

    def ouvrir(self, moteur, releve, regimes=None) -> Etape:
        return _etape("ouvrir.ouvrir", moteur, releve,
                      (("ouvrir", {"regimes": _regimes(regimes)}),))


class _Liquider(Regles):
    """``droit.liquider`` : ses règles, et l'étape ``liquider_chaque_regime``."""

    def liquider_chaque_regime(self, moteur, releve, ouverture, contexte=None, regimes=None,
                               nationale: bool = False) -> Etape:
        entree = "liquider.liquider_chaque_regime"
        chaine = _precedente(entree, "ouverture", ouverture, releve, "ouvrir")
        return _etape(entree, moteur, releve, chaine + (("liquider", {
            "neutralisations": _contexte_de_la_facade(entree, moteur, contexte),
            "regimes": _regimes(regimes), "nationale": nationale}),))


class _Completer(Regles):
    """``droit.completer`` : ses règles, et l'étape ``completer``, sur les
    pensions d'une seule liquidation : des pensions déjà servies, provisoires
    ou nationales n'arriveraient pas au portage."""

    def completer(self, moteur, releve, ouverture, liquidees, contexte=None,
                  servies: float = 0.0, initiales: tuple = (), recalcul: bool = True,
                  nationales=None, nature: str = "definitive",
                  premiere_retraite: str | None = None) -> Etape:
        entree = "completer.completer"
        if (servies, tuple(initiales), recalcul, nationales, nature, premiere_retraite) != (
                0.0, (), True, None, "definitive", None):
            raise NonTransmissible(
                f"{entree} : pensions servies, initiales, recalcul, nationales, nature ou "
                "première retraite que la façade ne transmet pas — le test reste sur le "
                "moteur Python")
        _precedente(entree, "ouverture", ouverture, releve, "ouvrir")
        chaine = _precedente(entree, "pensions", liquidees, releve, "liquider")
        if chaine[:-1] != ouverture._chaine:
            raise NonTransmissible(
                f"{entree} : pensions d'une autre ouverture que celle de l'étape")
        return _etape(entree, moteur, releve, chaine + (("completer", {
            "neutralisations": _contexte_de_la_facade(entree, moteur, contexte)}),))


def _simulateur_du_regime(regime: Regime):
    """Le simulateur de la façade dont le catalogue tient ``regime``, ou
    ``None``."""
    return next((simulateur for catalogue, simulateur in _CATALOGUES.values()
                 if regime.code in catalogue and catalogue[regime.code] is regime), None)


class _Commun(Regles):
    """``droit.commun`` : ses règles, et la période qui liquide une pension,
    rendue du catalogue du simulateur dont vient le régime."""

    def periode_de_liquidation(self, regime, date: DateMois):
        entree = "commun.periode_de_liquidation"
        simulateur = _simulateur_du_regime(regime)
        if simulateur is None or not isinstance(date, DateMois):
            raise NonTransmissible(
                f"{entree} : un régime qui n'est pas du catalogue d'un simulateur de la façade "
                "(simulateur.catalogue), ou une date qui n'est pas une DateMois — le portage "
                "ne les verrait pas")
        rang = _demander(entree, simulateur.parametres, pont.SIMULATEUR, regime.code,
                         date.annee, date.mois)
        return None if rang is None else regime.periodes[rang]


#: ``droit.commun``, ``droit.completer``, ``droit.liquider`` et
#: ``droit.ouvrir``, leurs règles servies par le portage, et les étapes des
#: trois derniers.
commun = _Commun("commun", _commun)
completer = _Completer("completer", _completer)
#: ``droit.foyer`` : l'étape « foyer et net », rendue sous le type ``Foyer``,
#: le contexte d'une liquidation par ses neutralisations.
foyer = Regles("foyer", _foyer)
liquider = _Liquider("liquider", _liquider)
ouvrir = _Ouvrir("ouvrir", _ouvrir)
#: Les règles du module de la réversion, sous un nom à elles : ``reversion``
#: est l'entrée de la réversion, la fonction du module qui porte son nom.
regles_de_la_reversion = Regles("reversion", _reversion)
#: ``droit.cultes`` : la durée de chaque fraction de la pension des cultes,
#: sur les durées du relevé, et la part de l'écart de la génération.
cultes = Regles("cultes", _cultes)
#: ``droit.invalidite`` : l'âge de l'ASPA de l'inapte, la catégorie de la
#: pension d'invalidité et le plancher de la pension substituée.
invalidite = Regles("invalidite", _invalidite)
class _Departs(Regles):
    """``droit.departs`` : ses règles servies, et ``Depart`` et
    ``DemandeExaminee``, les types du Python, que ses règles rendent et que
    les tests bâtissent pour les comparer."""

    Depart = _departs.Depart
    DemandeExaminee = _departs.DemandeExaminee


departs = _Departs("departs", _departs)
#: ``revalorisation``, hors du droit : les majorations forfaitaires de 1972 à
#: 1982, servies par le portage.
revalorisation = Regles("revalorisation", _revalorisation)
#: ``carriere``, hors du droit : le relevé prolongé jusqu'au départ et le
#: salaire moyen d'une année, servis par le portage sur les séries d'un
#: simulateur de la façade.
carriere = Regles("carriere", _carriere)
prolonger_releve = carriere.prolonger_releve
salaire_moyen_annuel = carriere.salaire_moyen_annuel


# -- la liquidation ---------------------------------------------------------------------

class Liquidee(_Ferme):
    """La liquidation que le portage a calculée, par ce que les tests en
    lisent : ses pensions avant les compléments (``pensions``, leur taux,
    leurs régimes, leurs plafonds), ses compléments (``complements``), la
    pension de chaque régime (``regimes``), ses totaux, ses mesures et ses avantages, sa
    fiabilité, la demande
    et le contexte qu'elle a reçus, les lignes du relevé qu'elle a lues
    (``releve.lignes()``) et ce que le contrat C.6 en décrit (``donnees()``).
    Le reste — le relevé entier, l'ouverture — ne passe pas
    le pont : la liquidation entière tient son contexte, les tables du
    moteur."""

    def __init__(self, lu: dict, demande, contexte) -> None:
        pensions = _Pensions(lu["taux"], lu["pensions"], lu["plafonds"])
        complements = _Complements(lu["complements"], lu["avantages_des_complements"])
        for nom, valeur in (("pensions", pensions), ("complements", complements),
                            ("regimes", lu["regimes"]),
                            ("total", lu["total"]), ("hors_repartition", lu["hors_repartition"]),
                            ("total_contributif", lu["total_contributif"]),
                            ("mesures", lu["mesures"]), ("avantages", lu["avantages"]),
                            ("demande", demande), ("contexte", contexte),
                            ("releve", _Lignes(lu["lignes"])), ("_donnees", lu["donnees"]),
                            ("fiabilite", lu["fiabilite"])):
            object.__setattr__(self, nom, valeur)

    def donnees(self) -> dict:
        return self._donnees


class _Lignes(_Ferme):
    """Le relevé d'une liquidation, par ses seules lignes, en données."""

    def __init__(self, lignes: list[dict]) -> None:
        object.__setattr__(self, "_lignes", lignes)

    def lignes(self) -> list[dict]:
        return self._lignes


class _Pensions(_Ferme):
    """Les pensions d'une liquidation, celles de l'étape « liquider » : leur
    taux, la pension de chaque régime avant les compléments, et ce que le
    plafond de L. 18 en écarte."""

    def __init__(self, taux: float, regimes: tuple, plafonds: tuple) -> None:
        object.__setattr__(self, "taux", taux)
        object.__setattr__(self, "regimes", regimes)
        object.__setattr__(self, "plafonds", plafonds)


class _Complements(_Ferme):
    """Les compléments d'une liquidation : la pension de chaque régime
    complétée, et les avantages que l'étape « compléter » sert."""

    def __init__(self, regimes: tuple, avantages: tuple) -> None:
        object.__setattr__(self, "regimes", regimes)
        object.__setattr__(self, "avantages", avantages)


#: Les appels de ``liquider`` que les liquidations de la façade ont coûtés au
#: portage, liquidations d'essai comprises.
_APPELS = [0]


class _Liquidation(_Ferme):
    """``droit.liquidation`` : ``liquider``, servie par le portage, sur une
    demande, l'état d'une carrière seule et le contexte du moteur d'un
    simulateur de la façade, ses neutralisations comprises ;
    ``demande_de_depart``, servie aussi ; ``appels``, ceux que les
    liquidations de la façade ont coûtés au portage ; ``Demande``, ``Etat``,
    ``Contexte`` et ``Mesure``, les types du Python, qui portent ce qu'on lui
    passe, et ses constantes. Le journal, les pensions déjà servies, une
    pension provisoire, une date d'observation, une hypothèse n'arriveraient
    pas au portage : la liquidation est refusée."""

    Demande = _liquidation.Demande
    Etat = _liquidation.Etat
    Contexte = _liquidation.Contexte
    Mesure = _liquidation.Mesure

    def __getattr__(self, nom):
        # Ce que le jumeau ne porte pas manque ici comme à un module : pytest
        # sonde ainsi ce qu'un fichier de tests importe.
        if nom.startswith("__") or not hasattr(_liquidation, nom):
            raise AttributeError(f"liquidation.{nom}")
        # Une constante du module n'est pas une règle : elle se lit.
        if nom.isupper():
            return getattr(_liquidation, nom)
        return super().__getattr__(nom)

    def appels(self) -> int:
        return _APPELS[0]

    def demande_de_depart(self, carriere, nature: str = "definitive"):
        return _demander("liquidation.demande_de_depart", Parametres(), carriere, nature)

    def liquider(self, demande, etat, contexte) -> Liquidee:
        moteur = contexte.univers
        if not isinstance(moteur, ScenarioActuel):
            raise NonTransmissible(
                "liquidation.liquider : moteur du contexte que la façade ne sait pas "
                "transmettre — la liquidation se demande sur le moteur d'un simulateur de la "
                "façade (simulateur.scenario_actuel)")
        journal = etat.journal
        if journal is not None and (not isinstance(journal, Journal) or len(journal)):
            raise NonTransmissible(
                "liquidation.liquider : journal qui n'est pas un journal vide de la façade — "
                "le portage ne verrait pas ses entrées")
        if (etat.servies, etat.initiales, etat.recalcul) != ((), (), True):
            raise NonTransmissible(
                "liquidation.liquider : état qui porte plus que sa carrière et un journal vide "
                "(pensions servies, pensions provisoires, recalcul) — le portage ne le verrait "
                "pas")
        if (contexte.observation, contexte.hypothese) != (None, None):
            raise NonTransmissible(
                "liquidation.liquider : contexte qui porte plus que le moteur et ses "
                "neutralisations (observation, hypothèse) — le portage ne le verrait pas")
        donnees = {"personne": demande.personne, "dateEffet": demande.date_effet,
                   "evenement": demande.evenement, "dateEvenement": demande.date_evenement,
                   "motif": demande.motif, "nature": demande.nature,
                   "regimes": list(demande.regimes)}
        lu = _demander("liquidation.liquider", moteur._simulateur.parametres, pont.MOTEUR,
                       donnees, etat.carriere, sorted(contexte.neutralisations),
                       journal is not None)
        _APPELS[0] += lu["appels"]
        # Ce que la liquidation a écrit au journal du portage, que le journal
        # de la façade reprend : rien, qu'elle est pure.
        if journal is not None:
            journal._entrees.extend(lu["journal"])
        return Liquidee(lu, demande, contexte)


#: ``droit.liquidation``, sa liquidation servie par le portage.
liquidation = _Liquidation()


# -- le relevé des droits et ses étapes -----------------------------------------------
#
# ``releve.construire`` rend un relevé que le pont ne passe pas : ses étapes sont
# des objets du moteur. La façade en rend ce que les tests en lisent, en
# données — l'enveloppe du contrat C.5 et ses lignes, les groupes de la
# liquidation unique ; la coordination, ses régimes par ligne et sa carrière ;
# les durées par compte, régime et année, le plafond de chaque année, la durée
# de chaque régime et tous régimes, ce qui ne tient à aucune année, les
# trimestres des enfants ; les points, les cotisations, les points acquis et
# gratuits de chaque régime —, et ce que chaque étape écrit sous son schéma
# (``donnees()``). Les étapes se servent aussi seules (``coordonner``,
# ``compter``, ``acquerir``) : chacune garde la carrière et les drapeaux dont
# elle vient, que le portage reçoit pour la refaire. Ses durées repassent au
# portage, qui les refait du relevé de leur carrière, quand une règle les
# reçoit (``liquider.duree_du_regime_aligne``) : celles du relevé sous ses
# drapeaux par défaut seulement.


@dataclasses.dataclass(frozen=True)
class _Source:
    """D'où vient une étape : la carrière, son moteur, et les drapeaux sous
    lesquels le portage la refait — ``bornee``, la carrière que le relevé lit
    (``ouvrir.indemnisation_bornee``)."""

    moteur: object
    carriere: object
    bornee: bool = True
    avantages_non_contributifs: bool = True
    points_gratuits: bool = True
    liquider_successions: bool = True

    def demander(self, entree: str, *arguments):
        return _demander(entree, self.moteur._simulateur.parametres, pont.MOTEUR,
                         self.carriere, *arguments)

    @property
    def du_releve(self) -> bool:
        """Le relevé de la carrière sous ses drapeaux par défaut, que le
        portage refait quand une règle en reçoit les durées."""
        return (self.bornee, self.avantages_non_contributifs, self.points_gratuits,
                self.liquider_successions) == (True, True, True, True)


class _Lu(_Ferme):
    """Ce qu'une étape a écrit, lu du portage : ses champs, et ``donnees()``,
    ce que son schéma décrit."""

    def __init__(self, source: _Source, lu: dict, champs: tuple[str, ...]) -> None:
        object.__setattr__(self, "_source", source)
        object.__setattr__(self, "_donnees", lu["donnees"])
        for nom in champs:
            object.__setattr__(self, nom, lu[nom])

    def donnees(self) -> dict:
        return self._donnees

    @property
    def _carriere(self):
        return self._source.carriere

    @property
    def _simulateur(self):
        return self._source.moteur._simulateur


class Coordination(_Lu):
    """La coordination d'une carrière (``coordonner.Coordination``), lue du
    portage : ``regimes``, ceux de chaque ligne ; ``carriere``, celle qu'elle
    a reçue quand elle l'a gardée, la carrière rétablie sinon ;
    ``retablissements``, ceux que son schéma décrit."""

    def __init__(self, source: _Source, lu: dict) -> None:
        super().__init__(source, lu, ("regimes",))
        object.__setattr__(self, "carriere",
                           source.carriere if lu["inchangee"] else lu["carriere"])
        object.__setattr__(self, "retablissements", tuple(lu["donnees"]["retablissements"]))


class _Enfant(_Ferme):
    def __init__(self, lu: dict) -> None:
        for nom, valeur in lu.items():
            object.__setattr__(self, nom, valeur)


class _Enfants(_Ferme):
    """Les trimestres des enfants (``compter.MajorationEnfants``) :
    ``trimestres``, ``regimes``, ``dispositifs``, chaque enfant —
    ``enfant``, ``naissance``, ``regime``, ``dispositif``, ``version`` —, et
    les trimestres et les services de chaque régime (:meth:`par_regime`)."""

    def __init__(self, lu: dict) -> None:
        for nom in ("trimestres", "regimes", "dispositifs"):
            object.__setattr__(self, nom, lu[nom])
        object.__setattr__(self, "enfants", tuple(_Enfant(e) for e in lu["enfants"]))
        object.__setattr__(self, "_par_regime", lu["par_regime"])

    def par_regime(self) -> dict[str, tuple[int, int]]:
        return dict(self._par_regime)


class _Emploi(_Ferme):
    """Ce qu'un emploi classé ajoute (``compter.TrimestresEmploi``), tel que
    le schéma des durées le décrit : ``regime``, ``fiche``, ``version``,
    ``services``, ``duree``, ``majoration``, ``au_dela_du_maximum`` et
    ``fiabilite``, en son nom ; le texte n'en passe pas."""

    def __init__(self, lu: dict) -> None:
        for nom, valeur in lu.items():
            object.__setattr__(self, nom, valeur)


class _Assimilee(_Ferme):
    """Ce qu'une période assimilée apporte dans une année
    (``compter.TrimestresAssimiles``), tel que le schéma des durées le
    décrit : ``motif``, ``regime``, ``annee``, ``fiche``, ``version``,
    ``trimestres`` et ``fiabilite``, en son nom ; le texte n'en passe pas."""

    def __init__(self, lu: dict) -> None:
        for nom, valeur in lu.items():
            object.__setattr__(self, nom, valeur)


class Durees(_Lu):
    """Les durées d'une carrière (``compter.Durees``), lues du portage :
    ``par_annee``, ``trimestres_par_regime``, ``trimestres``, ``hors_annee``,
    ``enfants``, ``emplois``, ``assimilees``, le plafond de chaque année de la carrière
    (:meth:`plafond`), et, demandés au portage, le cumul plafonné de régimes
    nommés (:meth:`cumul_plafonne`), leurs services
    (:meth:`services_effectifs`, :meth:`services_liquidables`) et ce que leurs
    emplois classés leur ajoutent (:meth:`services_des_emplois`,
    :meth:`majorations_des_emplois`, :meth:`bonifications_des_emplois`,
    :attr:`duree_hors_surcote`)."""

    def __init__(self, source: _Source, lu: dict) -> None:
        super().__init__(source, lu, ("par_annee", "trimestres_par_regime", "trimestres",
                                      "hors_annee"))
        object.__setattr__(self, "_plafonds", lu["plafonds"])
        object.__setattr__(self, "enfants",
                           None if lu["enfants"] is None else _Enfants(lu["enfants"]))
        object.__setattr__(self, "emplois",
                           tuple(_Emploi(e) for e in lu["donnees"]["emplois"]))
        object.__setattr__(self, "assimilees",
                           tuple(_Assimilee(a) for a in lu["donnees"]["assimilees"]))

    def _des_regimes(self, membres: tuple[str, ...]) -> dict:
        source = self._source
        return source.demander("compter.des_regimes", source.bornee,
                               source.avantages_non_contributifs, list(membres))

    def services_effectifs(self, membres: tuple[str, ...]) -> int:
        return self._des_regimes(membres)["services_effectifs"]

    def services_liquidables(self, membres: tuple[str, ...]) -> int:
        return self._des_regimes(membres)["services_liquidables"]

    def services_des_emplois(self, membres: tuple[str, ...]) -> int:
        return self._des_regimes(membres)["services"]

    def majorations_des_emplois(self, membres: tuple[str, ...]) -> int:
        return self._des_regimes(membres)["majorations"]

    def bonifications_des_emplois(self, membres: tuple[str, ...]) -> int:
        return self._des_regimes(membres)["bonifications"]

    @property
    def duree_hors_surcote(self) -> int:
        return self._des_regimes(())["hors_surcote"]

    def plafond(self, table: str, annee: int, membres: tuple[str, ...] = ()) -> int:
        """Le plafond de l'année, que le portage a lu sans régimes nommés :
        celui de régimes nommés n'a pas passé le pont."""
        if membres:
            raise NonTransmissible(
                "Durees.plafond : le plafond de membres nommés ne passe pas le pont — le "
                "relevé n'en rend que celui de l'année")
        plafonds = self._plafonds[table]
        if annee not in plafonds:
            raise NonTransmissible(
                f"Durees.plafond : {annee} est hors de la carrière, dont le relevé ne rend "
                "que les années")
        return plafonds[annee]

    def cumul_plafonne(self, table: str, membres: tuple[str, ...], annees=None) -> int:
        """Le cumul de ``membres`` dans ``table``, chaque année plafonnée,
        refait par le portage. Un filtre d'années, une fonction, ne passe
        pas le pont : la façade lui soumet les années que ``membres`` ont dans
        ``table``, les seules que le Python lui soumet, et passe celles qu'il
        accepte."""
        source = self._source
        acceptees = None if annees is None else sorted(
            {annee for membre in membres for annee in self.par_annee[table].get(membre, {})
             if annees(annee)})
        return source.demander("compter.cumul_plafonne", source.bornee,
                               source.avantages_non_contributifs, table, list(membres),
                               acceptees)


class Droits(_Lu):
    """Les droits d'une carrière (``acquerir.Droits``), lus du portage :
    ``points``, ``(code, annee, points, taux)``, et ``cotisations``
    revalorisées, ``(code, annee, montant)``, dans l'ordre ;
    ``points_acquis``, ``majoration_points``, ``plafonds``,
    ``(code, total, avant, retenus)``, et ``gratuits``, par régime,
    ``(points, avant)``."""

    def __init__(self, source: _Source, lu: dict) -> None:
        super().__init__(source, lu, ("points", "cotisations", "points_acquis",
                                      "majoration_points", "plafonds", "gratuits"))


class Releve(_Ferme):
    """Le relevé des droits d'une carrière, ce que les tests en lisent :
    ``coordination``, ``durees``, ``droits``, ``groupes``, et l'enveloppe du
    contrat C.5 (:meth:`donnees`) et ses lignes (:meth:`lignes`)."""

    def __init__(self, source: _Source, lu: dict) -> None:
        object.__setattr__(self, "coordination", Coordination(source, lu["coordination"]))
        object.__setattr__(self, "durees", Durees(source, lu["durees"]))
        object.__setattr__(self, "droits", Droits(source, lu["droits"]))
        object.__setattr__(self, "groupes", lu["groupes"])
        object.__setattr__(self, "_donnees", lu["donnees"])
        object.__setattr__(self, "_source", source)

    def donnees(self) -> dict:
        return self._donnees

    def lignes(self) -> list[dict]:
        return self._donnees["lignes"]


class _Module(_Ferme):
    """Un module du droit sous le nom de son jumeau : ses constantes, telles
    quelles ; ce qu'il sert, par le portage ; le reste, refusé."""

    _jumeau = None

    def __getattr__(self, nom):
        # Ce que le jumeau ne porte pas manque ici comme à un module : pytest
        # sonde ainsi ce qu'un fichier de tests importe.
        if nom.startswith("__") or not hasattr(self._jumeau, nom):
            raise AttributeError(f"{self._jumeau.__name__}.{nom}")
        constante = getattr(self._jumeau, nom)
        if type(constante) in _SIMPLES:
            return constante
        # Une table de valeurs simples (``FICHES_DES_ASSIMILEES``), copiée.
        if type(constante) is dict and all(
                type(v) in _SIMPLES for v in (*constante, *constante.values())):
            return dict(constante)
        # Une règle du module que la façade sert (``acquerir.points_msa_retenus``).
        module = self._jumeau.__name__.rsplit(".", 1)[-1]
        if nom in REGLES.get(module, ()):
            return getattr(Regles(module, self._jumeau), nom)
        return super().__getattr__(nom)


def _moteur_de_la_facade(entree: str, moteur) -> ScenarioActuel:
    if not isinstance(moteur, ScenarioActuel):
        raise NonTransmissible(
            f"{entree} : moteur passé en argument que la façade ne sait pas transmettre — "
            "l'étape se demande sur le moteur d'un simulateur de la façade "
            "(simulateur.scenario_actuel)")
    return moteur


def _coordination_de_la_facade(entree: str, coordination) -> Coordination:
    if not isinstance(coordination, Coordination):
        raise NonTransmissible(
            f"{entree} : coordination que la façade ne sait pas transmettre — elle vient de "
            "coordonner.coordonner ou du relevé de la façade")
    return coordination


class Releves(_Module):
    """``droit.releve``, sous le nom de son jumeau : ``construire``, servi
    par le portage, ses drapeaux compris ; ses règles (:data:`REGLES`), le
    relevé à rebours, servies comme celles d'un module du droit."""

    _jumeau = _releve

    def __getattr__(self, nom):
        if nom in REGLES["releve"]:
            return Regles("releve", _releve).__getattr__(nom)
        return super().__getattr__(nom)

    def construire(self, moteur, carriere, **drapeaux) -> Releve:
        lies = inspect.signature(_releve.construire).bind(moteur, carriere, **drapeaux)
        lies.apply_defaults()
        _moteur_de_la_facade("releve.construire", moteur)
        source = _Source(moteur, carriere, True, lies.arguments["avantages_non_contributifs"],
                         lies.arguments["points_gratuits"],
                         lies.arguments["liquider_successions"])
        return Releve(source, source.demander(
            "releve.construire", source.avantages_non_contributifs, source.points_gratuits,
            source.liquider_successions))


class _Coordonner(_Module):
    """``droit.coordonner`` : ``coordonner``, servi par le portage."""

    _jumeau = _coordonner

    def coordonner(self, moteur, carriere) -> Coordination:
        source = _Source(_moteur_de_la_facade("coordonner.coordonner", moteur), carriere,
                         bornee=False)
        return Coordination(source, source.demander("coordonner.coordonner"))


class _Compter(_Module):
    """``droit.compter`` : ``compter``, servi par le portage sur une
    coordination de la façade ; ``trimestres_du_contrat`` et
    ``jours_par_annee``, sur leurs dates, que le portage reçoit en jours
    depuis 1970, sous les réglages de référence, qu'elles ne lisent pas ; ses
    règles (:data:`REGLES`), servies comme celles d'un module du droit."""

    _jumeau = _compter

    def __getattr__(self, nom):
        if nom in REGLES["compter"]:
            return Regles("compter", _compter).__getattr__(nom)
        return super().__getattr__(nom)

    @staticmethod
    def _jours(jour: datetime.date) -> int:
        return (jour - datetime.date(1970, 1, 1)).days

    def trimestres_du_contrat(self, debut: datetime.date, fin: datetime.date) -> dict[int, int]:
        return _demander("compter.trimestres_du_contrat", Parametres(), self._jours(debut),
                         self._jours(fin))

    def jours_par_annee(self, debut: datetime.date, fin: datetime.date,
                        jours: int | None = None) -> dict[int, int]:
        return _demander("compter.jours_par_annee", Parametres(), self._jours(debut),
                         self._jours(fin), jours)

    def compter(self, moteur, coordination, avantages_non_contributifs: bool = True) -> Durees:
        _moteur_de_la_facade("compter.compter", moteur)
        origine = _coordination_de_la_facade("compter.compter", coordination)._source
        source = _Source(moteur, origine.carriere, origine.bornee, avantages_non_contributifs,
                         liquider_successions=False)
        return Durees(source, source.demander("compter.compter", source.bornee,
                                              avantages_non_contributifs))


class _Acquerir(_Module):
    """``droit.acquerir`` : ``acquerir``, servi par le portage sur une
    coordination de la façade et les durées qu'elle a comptées."""

    _jumeau = _acquerir

    def acquerir(self, moteur, coordination, durees, avec_points_gratuits: bool = True) -> Droits:
        _moteur_de_la_facade("acquerir.acquerir", moteur)
        origine = _coordination_de_la_facade("acquerir.acquerir", coordination)._source
        if (not isinstance(durees, Durees) or durees._source.carriere is not origine.carriere
                or durees._source.bornee != origine.bornee):
            raise NonTransmissible(
                "acquerir.acquerir : durées qui ne sont pas celles de la coordination — le "
                "portage les refait de sa carrière")
        source = _Source(moteur, origine.carriere, origine.bornee,
                         durees._source.avantages_non_contributifs, avec_points_gratuits,
                         liquider_successions=False)
        return Droits(source, source.demander(
            "acquerir.acquerir", source.bornee, source.avantages_non_contributifs,
            avec_points_gratuits))


class _Echeanciers(_Module):
    """``echeancier`` : l'échéancier (:class:`Echeancier`) ; ``depart_de``,
    servi par le portage ; ``SORTES``, ce que chaque sorte d'événement
    appelle, tel que le paquet du portage le tient, sans ce qui la dit ; et
    ``Evenement``, le type du Python."""

    _jumeau = _echeancier
    Echeancier = Echeancier
    Evenement = _echeancier.Evenement

    def depart_de(self, carriere):
        return _demander("echeancier.depart_de", Parametres(), carriere)

    @property
    def SORTES(self) -> dict[str, dict]:  # noqa: N802 — le nom de la constante du jumeau
        return _demander("echeancier.sortes", Parametres(), pont.SIMULATEUR)


class _Journaux(_Module):
    """``journal`` : le journal (:class:`Journal`) et ``Entree``, le type du
    Python."""

    _jumeau = _journal
    Journal = Journal
    Entree = _journal.Entree


class _Pilote(_Module):
    """``pilote`` : ``age_de_depart``, servi par le portage sur un simulateur
    de la façade, le cas type passé par ce que le portage en lit
    (``CasType.pour_le_portage``), la part des primes projetée comme le COR
    la projette (``castypes.primes_projetees_en_donnees``). Ses appels de
    ``liquider`` se comptent dans ``liquidation.appels()``."""

    _jumeau = _pilote

    def age_de_depart(self, simulateur, cas, generation: int, variante: str = "droit") -> float:
        if not isinstance(simulateur, Simulateur):
            raise NonTransmissible(
                "pilote.age_de_depart : simulateur que la façade ne sait pas transmettre")
        lu = _demander("pilote.age_de_depart", simulateur.parametres, pont.SIMULATEUR,
                       cas.pour_le_portage(simulateur, generation), variante,
                       _castypes.primes_projetees_en_donnees(simulateur))
        _APPELS[0] += lu["appels"]
        return lu["age"]


#: ``echeancier``, ``journal`` et ``pilote``, servis par le portage.
echeancier = _Echeanciers()
journal = _Journaux()
pilote = _Pilote()

#: ``droit.releve``, ``droit.coordonner``, ``droit.compter`` et
#: ``droit.acquerir``, servis par le portage.
releve = Releves()
coordonner = _Coordonner()
compter = _Compter()
acquerir = _Acquerir()


# -- un test resté sur le moteur Python ----------------------------------------------
#
# Dans un fichier basculé, un test que la façade ne sait pas encore servir —
# il appelle une règle du moteur Python, ou lit ce que la façade refuse — garde
# le moteur Python, tel qu'il était, sous la marque ``sur_le_moteur_python`` et
# sa raison. Les tests marqués se comptent, et leur nombre ne fait que
# décroître (``tests/test_fichiers_sur_le_moteur_python.py``).

#: La marque d'un test resté sur le moteur Python.
MARQUE = "sur_le_moteur_python"

#: Le jumeau Python de chaque entrée qu'un fichier basculé importe d'ici.
JUMEAUX = {"Simulateur": _simulateur.Simulateur, "Carriere": _carriere.Carriere,
           "reversion": _reversion.reversion, "commun": _commun, "completer": _completer,
           "foyer": _foyer, "liquider": _liquider, "ouvrir": _ouvrir, "releve": _releve,
           "regles_de_la_reversion": _reversion, "revalorisation": _revalorisation,
           "liquidation": _liquidation, "coordonner": _coordonner, "compter": _compter,
           "acquerir": _acquerir, "cultes": _cultes, "departs": _departs, "invalidite": _invalidite,
           "faire_vivre": _revalorisation.faire_vivre,
           "actuel_aujourd_hui": _revalorisation.actuel_aujourd_hui,
           "PensionServie": _revalorisation.PensionServie,
           "majorer_les_petites_pensions": _revalorisation.majorer_les_petites_pensions,
           "Echeancier": _echeancier.Echeancier, "echeancier": _echeancier,
           "journal": _journal, "pilote": _pilote,
           "ConstructeurCompte": _compte.ConstructeurCompte,
           "prolonger_releve": _carriere.prolonger_releve,
           "salaire_moyen_annuel": _carriere.salaire_moyen_annuel}

#: Les simulateurs des tests, par fichier, par moteur et par paramètres.
#: Les copies retouchées des données de ce processus, par retouches.
_COPIES: dict[tuple, Path] = {}


def donnees_retouchees(request, nom: tuple, retouches: dict) -> Path:
    """Une copie des données du dépôt dont chaque fichier de ``retouches`` —
    son chemin relatif à ``data/`` — est récrit par sa retouche, une fonction
    du texte au texte : ce qu'un test remplaçait en Python, le portage le voit
    ainsi, sur leur paquet. Les autres fichiers sont liés à ceux du dépôt. Une
    copie par ``nom``, qui dit les retouches, et par processus."""
    if nom not in _COPIES:
        copie = request.getfixturevalue("tmp_path_factory").mktemp("donnees") / "data"
        shutil.copytree(Path(__file__).resolve().parents[1] / "data", copie,
                        copy_function=os.symlink)
        for chemin, retoucher in retouches.items():
            fichier = copie / chemin
            texte = Path(os.readlink(fichier)).read_text(encoding="utf-8")
            fichier.unlink()
            retouche = retoucher(texte)
            assert retouche != texte, f"{chemin} : la retouche ne change rien"
            fichier.write_text(retouche, encoding="utf-8")
        _COPIES[nom] = copie
    return _COPIES[nom]


_SIMULATEURS: dict[tuple, object] = {}


def _marque(request) -> bool:
    return request.node.get_closest_marker(MARQUE) is not None


def simulateur_du_test(request, parametres: Parametres | None = None):
    """Le simulateur d'un test, sous ``parametres`` : celui de la façade, ou
    celui du moteur Python pour un test marqué. Le même pour tous les tests
    d'un fichier, comme une fixture de module."""
    parametres = Parametres() if parametres is None else parametres
    cle = (request.module.__name__, _marque(request), parametres)
    if cle not in _SIMULATEURS:
        _SIMULATEURS[cle] = (_simulateur.Simulateur if _marque(request) else Simulateur)(parametres)
    return _SIMULATEURS[cle]


@pytest.fixture(autouse=True)
def entrees_du_test(request):
    """La fixture qu'un fichier basculé importe avec ses entrées : le temps
    d'un test marqué, celles qu'il tient de la façade redeviennent leur jumeau
    Python, pour ses aides comme pour lui."""
    module = request.module
    remplacees = [nom for nom, jumeau in JUMEAUX.items()
                  if _marque(request) and getattr(module, nom, None) is globals()[nom]]
    for nom in remplacees:
        setattr(module, nom, JUMEAUX[nom])
    try:
        yield
    finally:
        for nom in remplacees:
            setattr(module, nom, globals()[nom])
