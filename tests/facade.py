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
"""

from __future__ import annotations

import inspect

from retraite_notionnelle import carriere as _carriere
from retraite_notionnelle import memoire, pont
from retraite_notionnelle import simulateur as _simulateur
from retraite_notionnelle.config import Parametres
from retraite_notionnelle.droit import reversion as _reversion
from retraite_notionnelle.scenarios import actuel as _actuel

#: Les données du simulateur Python que la façade laisse lire : des chargeurs,
#: qui restent en Python (note de décision 0006), et aucune règle.
DONNEES = frozenset({"catalogue", "affiliations"})


class NonTransmissible(BaseException):
    """Ce que le test demande, la façade ne sait pas le faire parvenir au
    portage. Elle ne dérive pas d'``Exception`` : un test qui attend une erreur
    du moteur (``pytest.raises(Exception)``) ne verdit pas de ce refus."""


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


class ScenarioActuel(_Ferme):
    """Le moteur du scénario 1 d'un simulateur de la façade."""

    def __init__(self, simulateur: Simulateur) -> None:
        object.__setattr__(self, "_simulateur", simulateur)

    @property
    def macro(self):
        """Les séries du moteur : celles de son simulateur."""
        return self._simulateur.macro

    def calculer(self, carriere, *drapeaux, **nommes):
        """``ScenarioActuel.calculer`` : le résultat entier du scénario 1, ses
        drapeaux liés comme le Python les lie."""
        lies = inspect.signature(_actuel.ScenarioActuel.calculer).bind(
            self, carriere, *drapeaux, **nommes)
        lies.apply_defaults()
        _, _, *valeurs = lies.arguments.values()
        return _demander("scenario_actuel.calculer", self._simulateur.parametres,
                         pont.MOTEUR, carriere, *valeurs)


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

    @property
    def macro(self):
        """Les séries du simulateur, que ses tests lisent et passent aux
        bâtisseurs de la carrière : la façade s'en souvient."""
        macro = self._donnees.macro
        _SERIES[id(macro)] = (macro, self.parametres)
        return macro

    def __getattr__(self, nom):
        if nom in DONNEES:
            return getattr(self._donnees, nom)
        return super().__getattr__(nom)

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


class Carriere(_carriere.Carriere):
    """``Carriere``, ses deux bâtisseurs servis par le portage : la carrière
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
