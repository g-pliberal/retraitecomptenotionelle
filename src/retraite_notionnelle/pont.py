"""Le pont : ce que la fabrique fait calculer au moteur JavaScript, par node.

Le moteur d'une carrière n'aura qu'un exemplaire, en JavaScript, puisque le
site le fait tourner chez son lecteur ; la fabrique, le coût et les études le
feront tourner par node au lieu de son jumeau Python (note de décision 0003,
action 161, étape 5). Le pont doit tenir six conditions : les données des
contrats les mêmes dans un sens et dans l'autre ; les témoins et les agrégats
identiques à l'octet ; le budget de calcul tenu ; la mémoire des calculs
indexée sur le portage ; sans node, la fabrique qui s'arrête, sans repli sur
un moteur périmé ; aucune dépendance nouvelle.

Ce module lance ``pont.mjs`` et lui passe une demande. La fabrique y lit
d'abord la grille des carrières types de la table des agrégats, et les deux
départs que compare Droits non cotisés (``scripts/construire_donnees.py``) ;
puis, pour le bilan figé, la même grille, dont elle tire les écarts médians,
et les carrières d'exemple de « Pourquoi changer », des saisies. Le portage
calcule ses exponentielles comme la libm de Linux (``moteur/js/libm.js``) :
ce qu'il rend est, au bit près, ce que le moteur Python calcule, et
``tests/test_agregats.py``, ``tests/test_cout.py`` et
``tests/test_affirmations.py`` l'exigent des deux tables.

La grille du coût passe le pont autrement : sous les conventions de
projection du COR, la carrière d'un cas type se déforme en Python — l'entrée
tardive d'un fonctionnaire, la part des primes que le décrochage du
traitement porte (``castypes.primes_projetees``) —, et le portage, qui n'en
garde pas de copie, la reçoit en données (:func:`carriere_en_donnees`), sous
les paramètres du simulateur (:func:`parametres_en_donnees`), sur le paquet
des données du jour (:func:`paquet_des_donnees`).

Dans l'autre sens, la saisie, dont le portage garde le seul exemplaire
(étape 6, la paire du contexte) : il bâtit la carrière d'une requête du
simulateur et ses paramètres, et le Python les relit sous ses propres types
(:func:`carrieres_des_saisies`) pour les simuler de son moteur, qui garde son
jumeau.

Les témoins de simulations, enfin : le portage simule chaque requête comme le
site la simule (:func:`simulations`), et le Python relit son résultat sous une
table des types déclarée champ par champ (:func:`resultat_des_donnees`), node
n'écrivant qu'un type de nombre. ``scripts/construire_temoins.py`` écrit
ainsi les témoins, le zéro d'un champ flottant « 0.0 » (décision du
propriétaire, 31 octobre 2026), et le moteur Python, tant qu'il garde ses
jumeaux, les refait au bit près (``tests/test_pont.py`` ; action 161,
étape 6).

Les confrontations aux références extérieures, de même : l'estimation
officielle (``scripts/estimation_officielle.py``) et Destinie 2
(``tests/test_destinie.py``) lisent du scénario 1 que le portage sert ce
que les témoins n'écrivent pas tout entier (:func:`scenario_actuel`), et le
moteur Python le refait au bit près, cas par cas (``tests/outils_pont.py``).

Une demande sur le paquet du dépôt, sans paquet, ne lance pas node à chaque
fois : les tests en font une par carrière, et chacune coûtait trois dixièmes
de seconde, à lancer node et à relire le paquet. Le pont reste ouvert
(``pont.mjs --servir``), sur le paquet qu'il a lu, jusqu'à ce que ce paquet
change ou que le processus finisse.
"""

from __future__ import annotations

import atexit
import dataclasses
import enum
import functools
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import types
import typing
from pathlib import Path

from .config import RACINE_PROJET

#: Le programme que node fait tourner.
PROGRAMME = Path(__file__).with_name("pont.mjs")


class PontIndisponible(RuntimeError):
    """Node manque : ce que le pont calcule ne se calcule pas, et rien ne prend
    le relais."""


def version_de_node() -> bytes:
    """La version de node, qui fait tourner le portage, telle qu'il l'écrit ;
    « - » sans lui. Les empreintes de la mémoire des calculs et de la fabrique
    la lisent."""
    try:
        return subprocess.run(["node", "--version"], capture_output=True,
                              check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return b"-"


def _demander(demande: dict, paquet: bytes | None) -> dict:
    """La réponse du portage à une demande, calculée sur ``paquet`` — les
    octets d'un paquet de données —, ou sur ``moteur/donnees.json`` sans lui,
    par le pont gardé ouvert (:class:`_PontOuvert`)."""
    if shutil.which("node") is None:
        raise PontIndisponible(
            "node absent : la fabrique calcule par le portage JavaScript "
            "(retraite_notionnelle/pont.mjs), sans repli sur le moteur Python")
    if paquet is None:
        return _ouvert().demander(demande)
    entree = (b'{"paquet":' + paquet
              + b',"demande":' + json.dumps(demande).encode("utf-8") + b"}")
    execution = subprocess.run(["node", str(PROGRAMME)], input=entree, cwd=RACINE_PROJET,
                               capture_output=True, check=False)
    if execution.returncode != 0:
        raise RuntimeError(f"{PROGRAMME.name} : "
                           + execution.stderr.decode("utf-8", "replace").strip())
    return json.loads(execution.stdout)


def _signature_du_paquet() -> tuple[int, int]:
    """La date et la taille du paquet du dépôt : la fabrique le récrit."""
    etat = (RACINE_PROJET / "moteur" / "donnees.json").stat()
    return etat.st_mtime_ns, etat.st_size


class _PontOuvert:
    """``pont.mjs --servir`` : node lancé une fois, sur le paquet du dépôt lu
    une fois, une demande par ligne et sa réponse."""

    def __init__(self) -> None:
        self.signature = _signature_du_paquet()
        self._journal = tempfile.TemporaryFile()
        self._processus = subprocess.Popen(
            ["node", str(PROGRAMME), "--servir"], cwd=RACINE_PROJET, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=self._journal, text=True, encoding="utf-8",
            bufsize=1)
        atexit.register(self.fermer)

    def demander(self, demande: dict) -> dict:
        try:
            self._processus.stdin.write(json.dumps({"demande": demande}) + "\n")
            self._processus.stdin.flush()
        except BrokenPipeError:
            pass  # node s'est arrêté : la lecture le dit, avec son journal
        ligne = self._processus.stdout.readline()
        if not ligne:
            self._journal.seek(0)
            raise RuntimeError(f"{PROGRAMME.name} : node s'est arrêté : "
                               + self._journal.read().decode("utf-8", "replace")[-2000:])
        reponse = json.loads(ligne)
        if "erreur" in reponse:
            raise RuntimeError(f"{PROGRAMME.name} : {reponse['erreur']}")
        return reponse["reponse"]

    def fermer(self) -> None:
        if self._processus.poll() is None:
            self._processus.stdin.close()
            try:
                self._processus.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._processus.kill()


#: Le pont gardé ouvert de ce processus, s'il y en a un.
_OUVERT: _PontOuvert | None = None


def _ouvert() -> _PontOuvert:
    """Le pont ouvert sur le paquet du dépôt tel qu'il est : relancé quand la
    fabrique l'a récrit."""
    global _OUVERT
    if _OUVERT is None or _OUVERT.signature != _signature_du_paquet():
        fermer()
        _OUVERT = _PontOuvert()
    return _OUVERT


def fermer() -> None:
    """Referme le pont gardé ouvert, s'il y en a un : la demande suivante le
    relance."""
    global _OUVERT
    if _OUVERT is not None:
        _OUVERT.fermer()
        _OUVERT = None


def _flottant(valeur) -> float:
    """Un nombre que le Python tient pour un flottant : node écrit 2.0 « 2 »,
    et un nombre non fini « null »."""
    return math.nan if valeur is None else float(valeur)


def _par_scenario(lus: dict) -> dict[str, float]:
    return {scenario: _flottant(nombre) for scenario, nombre in lus.items()}


def _aujourd_hui(lu: dict | None) -> dict | None:
    if lu is None:
        return None
    return {
        "pension_annuelle": _flottant(lu["pension_annuelle"]),
        "pensions_totales": _par_scenario(lu["pensions_totales"]),
        "rente_capitalisee_volontaire": _flottant(lu["rente_capitalisee_volontaire"]),
    }


def carrieres(cas: list[dict], scenarios, paquet: bytes | None = None,
              ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque carrière d'un seul statut, ``{"cle", "options"}`` aux options de
    ``carriere_simple``, simulée par le portage sous les réglages de
    référence : sous sa clé, l'année de son départ et celle de chaque
    scénario, l'écart de chacun au système actuel, pilier capitalisé compris
    (``variation_totale``), la pension du système actuel et la durée qu'il
    requiert ; la pension de chaque scénario, pilier capitalisé compris
    (``pension_totale``), et la rente des points volontaires
    (``rente_capitalisee_volontaire``) ; et, pour qui est déjà parti, ce que
    le système actuel et chaque scénario lui servent aujourd'hui
    (``Comparaison.aujourd_hui``), sinon ``None``. Puis, sous leur clé, les
    motifs des carrières que le portage refuse."""
    reponse = _demander({"carrieres": {"cas": cas, "scenarios": list(scenarios)}}, paquet)
    resultats = {
        cle: {
            "annee_liquidation": lu["annee_liquidation"],
            "annees_liquidation": dict(lu["annees_liquidation"]),
            "variations": _par_scenario(lu["variations"]),
            "pension_annuelle": _flottant(lu["pension_annuelle"]),
            "trimestres_requis": lu["trimestres_requis"],
            "pensions_totales": _par_scenario(lu["pensions_totales"]),
            "rentes_volontaires": _par_scenario(lu["rentes_volontaires"]),
            "aujourd_hui": _aujourd_hui(lu["aujourd_hui"]),
        }
        for cle, lu in reponse["resultats"].items()
    }
    return resultats, reponse["echecs"]


def _en_donnees(valeur):
    """Une valeur telle que JSON l'écrit et que le portage la lit : un membre
    d'énumération par sa valeur, un dataclass par ses champs, une suite en
    liste."""
    if isinstance(valeur, enum.Enum):
        return valeur.value
    if dataclasses.is_dataclass(valeur):
        return {champ.name: _en_donnees(getattr(valeur, champ.name))
                for champ in dataclasses.fields(valeur)}
    if isinstance(valeur, (list, tuple)):
        return [_en_donnees(element) for element in valeur]
    if isinstance(valeur, dict):
        return {cle: _en_donnees(element) for cle, element in valeur.items()}
    return valeur


def parametres_en_donnees(parametres) -> dict:
    """Les paramètres d'un simulateur tels que le portage les lit, sous les
    mêmes noms (``PARAMETRES_DEFAUT`` de ``moteur/js/config.js``) : tous, sauf
    la racine des données, dont le paquet tient lieu."""
    return {champ.name: _en_donnees(getattr(parametres, champ.name))
            for champ in dataclasses.fields(parametres) if champ.name != "racine_donnees"}


def carriere_en_donnees(carriere) -> dict:
    """La carrière telle que le portage la relit (``carriereDesDonnees`` de
    ``pont.mjs``) : chacun de ses champs, chacune de ses lignes entière, et la
    chronologie dont elle est la vue, telle que le Python l'a complétée. Ce que
    le Python a fait de la carrière passe ainsi tel quel, et le portage n'en
    garde pas de copie."""
    donnees = {}
    for champ in dataclasses.fields(carriere):
        valeur = getattr(carriere, champ.name)
        if champ.name == "dates_entree":
            valeur = {statut: [date.annee, date.mois] for statut, date in valeur.items()}
        donnees[champ.name] = _en_donnees(valeur)
    return donnees


@functools.cache
def _indices(type_) -> dict:
    """Les types des champs d'un dataclass, lus une fois :
    ``typing.get_type_hints`` évalue les annotations à chaque appel."""
    return typing.get_type_hints(type_)


def _depuis_donnees(type_, valeur):
    """Une valeur que le portage a écrite, rendue sous le type que le Python
    lui donne : JSON n'écrit pas « 2.0 », et un flottant entier reviendrait
    entier ; un membre d'énumération revient de sa valeur, un dataclass de ses
    champs, tous et rien d'autre, une suite en tuple ou en liste."""
    if typing.get_origin(type_) in (typing.Union, types.UnionType):
        if valeur is None:
            return None
        (autre,) = (membre for membre in typing.get_args(type_) if membre is not type(None))
        return _depuis_donnees(autre, valeur)
    if type_ is float:
        return _flottant(valeur)
    if type_ is int:
        if type(valeur) is not int:
            raise TypeError(f"entier attendu, le portage a écrit {valeur!r}")
        return valeur
    if isinstance(type_, type) and issubclass(type_, enum.Enum):
        return type_(valeur)
    if dataclasses.is_dataclass(type_):
        champs = dataclasses.fields(type_)
        if set(valeur) != {champ.name for champ in champs}:
            raise ValueError(f"{type_.__name__} : le portage écrit les champs {sorted(valeur)}")
        indices = _indices(type_)
        return type_(**{champ.name: _depuis_donnees(indices[champ.name], valeur[champ.name])
                        for champ in champs})
    if typing.get_origin(type_) in (tuple, list):
        arguments = typing.get_args(type_)
        if len(arguments) == 2 and arguments[1] is Ellipsis:
            arguments = (arguments[0],) * len(valeur)
        elif typing.get_origin(type_) is list:
            arguments = arguments * len(valeur)
        return typing.get_origin(type_)(_depuis_donnees(sous_type, element)
                                        for sous_type, element in zip(arguments, valeur,
                                                                      strict=True))
    return valeur


def parametres_des_donnees(donnees: dict):
    """Les paramètres que le portage a écrits, sous les types du Python : le
    chemin inverse de :func:`parametres_en_donnees`. La racine des données est
    celle du Python, dont le paquet tenait lieu."""
    from .config import Parametres

    champs = {champ.name for champ in dataclasses.fields(Parametres)} - {"racine_donnees"}
    if set(donnees) != champs:
        raise ValueError(f"Parametres : le portage écrit les champs {sorted(donnees)}")
    indices = _indices(Parametres)
    return Parametres(**{nom: _depuis_donnees(indices[nom], valeur)
                         for nom, valeur in donnees.items()})


#: Les nombres libres de la chronologie — les attributs et le montant d'un
#: fait, que le contrat C.1 ne type pas — que le Python écrit toujours en
#: flottants : JSON n'écrit pas « 64.0 », et ils reviendraient entiers. Les
#: autres gardent le type que JSON leur rend, qui est le leur : un entier, ou
#: les trimestres d'un relevé, entiers quand ils le sont
#: (``Saisie.releve_analyse``).
FLOTTANTS_DE_LA_CHRONOLOGIE = frozenset({
    "age", "annuel", "mensuel", "niveau_salaire", "part_primes", "quotite", "revenu"})


def _chronologie_des_donnees(chronologie: dict | None) -> dict | None:
    """La chronologie que le portage a écrite, ses nombres libres sous le type
    que le Python leur donne (:data:`FLOTTANTS_DE_LA_CHRONOLOGIE`)."""
    if chronologie is None:
        return None

    def flottants(libres):
        if not isinstance(libres, dict):
            return libres
        return {nom: float(valeur) if nom in FLOTTANTS_DE_LA_CHRONOLOGIE
                and type(valeur) is int else valeur
                for nom, valeur in libres.items()}

    faits = []
    for fait in chronologie["faits"]:
        fait = dict(fait)
        for libre in ("attributs", "montant"):
            if libre in fait:
                fait[libre] = flottants(fait[libre])
        faits.append(fait)
    return {**chronologie, "faits": faits}


def carriere_des_donnees(donnees: dict):
    """La carrière que le portage a bâtie, sous les types du Python : le chemin
    inverse de :func:`carriere_en_donnees`. Chacun de ses champs, chacune de
    ses lignes, et la chronologie dont elle est la vue, telle quelle."""
    from .calendrier import DateMois
    from .carriere import AnneeCarriere, Carriere

    champs = {champ.name for champ in dataclasses.fields(Carriere)}
    if set(donnees) != champs:
        raise ValueError(f"Carriere : le portage écrit les champs {sorted(donnees)}")
    indices = _indices(Carriere)
    speciaux = {
        "dates_entree": {statut: DateMois(annee, mois)
                         for statut, (annee, mois) in donnees["dates_entree"].items()},
        "lignes_apres_depart": tuple(_depuis_donnees(AnneeCarriere, ligne)
                                     for ligne in donnees["lignes_apres_depart"]),
        "chronologie": _chronologie_des_donnees(donnees["chronologie"]),
    }
    return Carriere(**{nom: speciaux[nom] if nom in speciaux
                       else _depuis_donnees(indices[nom], valeur)
                       for nom, valeur in donnees.items()})


def carrieres_des_saisies(cas: list[dict], paquet: bytes | None = None,
                          ) -> tuple[dict[str, tuple], dict[str, str]]:
    """Chaque requête du simulateur, ``{"cle", "requete"}``, lue par la saisie
    du portage, la seule (action 161, étape 6), ou chaque saisie aux champs de
    ``Saisie``, ``{"cle", "saisie"}``, comme :func:`saisies` les lit : sous sa
    clé, les paramètres de la saisie et la carrière que le site simulerait,
    relus sous les types du Python (:func:`parametres_des_donnees`,
    :func:`carriere_des_donnees`), que son moteur simule à son tour — celle
    d'une saisie par la pension, que le portage trouve en l'inversant ; un
    relevé avec ``"prolonger": False`` s'en tient à ses années, pour qui l'a
    déjà prolongé à sa façon. Puis, sous leur clé, les motifs des requêtes
    que le portage refuse."""
    reponse = _demander({"carrieres_des_saisies": {"cas": cas}}, paquet)
    resultats = {cle: (parametres_des_donnees(lu["parametres"]),
                       carriere_des_donnees(lu["carriere"]))
                 for cle, lu in reponse["resultats"].items()}
    return resultats, reponse["echecs"]


#: Le programme qui bâtit le paquet des données du jour, dans un processus à lui.
_BATIR_LE_PAQUET = """\
import importlib.util, sys
spec = importlib.util.spec_from_file_location("construire_donnees", sys.argv[1])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
sys.stdout.buffer.write(module.construire(b"{}", b"{}"))
"""


#: Le dernier paquet du jour que ce processus a bâti, sous la signature des
#: sources d'où il l'a bâti (``memoire.signature``).
_PAQUET: tuple[str | None, bytes] | None = None


def paquet_des_donnees() -> bytes:
    """Le paquet des données du jour, tel que la fabrique l'écrira, sans le
    bilan ni les agrégats, que la simulation d'une carrière ne lit pas : celui
    sur lequel le coût fait simuler sa grille.

    Il ne se lit pas dans ``moteur/donnees.json`` : une retouche des données
    n'y entre qu'à la fabrique suivante, et la fabrique, qui l'écrit pendant
    que d'autres étapes calculent le coût, le leur donnerait à demi écrit. Il
    se bâtit donc depuis ``data/``, une fois par état des sources de la
    mémoire des calculs (``memoire.signature``), et non une fois par
    processus : une donnée retouchée pendant qu'un processus calcule entre
    dans le paquet de son calcul suivant, et la mémoire ne garde pas, sous
    l'empreinte des données nouvelles, une grille simulée sur le paquet des
    anciennes."""
    global _PAQUET
    from .memoire import signature

    etat = signature()
    if _PAQUET is None or _PAQUET[0] != etat:
        _PAQUET = (etat, _batir_le_paquet())
    return _PAQUET[1]


def _batir_le_paquet() -> bytes:
    """Le paquet du jour, bâti par la fabrique elle-même
    (``scripts/construire_donnees.py``), dans un processus à elle, comme node
    fait tourner le moteur JavaScript dans le sien : ce qu'elle lit pour le
    site seul — les crédits des ministères, le manifeste des sources, qu'aucun
    calcul ne lit — n'entre ni dans les mémoires des chargeurs de ce
    processus-ci, ni dans le relevé de ce que lisent les calculs gardés
    (``memoire.HORS_DU_MODELE``)."""
    environnement = {**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, (
        str(RACINE_PROJET / "src"), os.environ.get("PYTHONPATH"))))}
    execution = subprocess.run(
        [sys.executable, "-c", _BATIR_LE_PAQUET,
         str(RACINE_PROJET / "scripts" / "construire_donnees.py")],
        cwd=RACINE_PROJET, env=environnement, capture_output=True, check=False)
    if execution.returncode != 0:
        raise RuntimeError("le paquet des données du jour ne se bâtit pas : "
                           + execution.stderr.decode("utf-8", "replace").strip()[-2000:])
    return execution.stdout


def _serie(paires) -> dict[int, float]:
    return {annee: _flottant(nombre) for annee, nombre in paires}


def _volet_du_cout(lu: dict) -> dict:
    garantie, pilier = lu["garantie"], lu["pilier"]
    return {
        "annee_liquidation": lu["annee_liquidation"],
        "revenus": _serie(lu["revenus"]),
        "garantie": {
            "annee_ouverture": garantie["annee_ouverture"],
            **{champ: _flottant(garantie[champ])
               for champ in ("pension_contributive", "ressources", "rente_capitalisee")},
        },
        "cotisations": _serie(lu["cotisations"]),
        "pilier": None if pilier is None else {
            "annees": {annee: tuple(_flottant(nombre) for nombre in flux)
                       for annee, *flux in pilier["annees"]},
            **{champ: _flottant(pilier[champ])
               for champ in ("capital", "diviseur", "rente_annuelle")},
        },
    }


def grille_du_cout(cas: list[dict], scenarios, parametres, paquet: bytes | None = None,
                   ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque case de la grille du coût, ``{"cle", "carriere",
    "propositions"}`` — sa carrière, et celles, nommées, sur lesquelles le coût
    calcule la proposition seule —, simulée par le portage sous
    ``parametres``, ceux de la projection : sous sa clé, ce que le coût en lit,
    tel que ``cout._simulations_en_python`` le tire du moteur Python, son
    jumeau. Puis, sous leur clé, les motifs des cases que le portage refuse."""
    reponse = _demander({"grille_du_cout": {
        "parametres": parametres_en_donnees(parametres),
        "scenarios": list(scenarios),
        "cas": [{"cle": un["cle"], "carriere": carriere_en_donnees(un["carriere"]),
                 "propositions": {nom: carriere_en_donnees(carriere)
                                  for nom, carriere in un["propositions"].items()}}
                for un in cas],
    }}, paquet)
    resultats = {
        cle: {
            "pensions": _par_scenario(lu["pensions"]),
            "depart_reporte": lu["depart_reporte"],
            "liberal": _volet_du_cout(lu["liberal"]),
            "coefficient_liberal": _flottant(lu["coefficient_liberal"]),
            "prelevement": _serie(lu["prelevement"]),
            "pension_actuelle": _flottant(lu["pension_actuelle"]),
            "pensions_par_regime": [(regime, _flottant(montant))
                                    for regime, montant in lu["pensions_par_regime"]],
            "population": lu["population"],
            "propositions": {nom: _volet_du_cout(volet)
                             for nom, volet in lu["propositions"].items()},
        }
        for cle, lu in reponse["resultats"].items()
    }
    return resultats, reponse["echecs"]


def saisies(cas: list[dict], scenarios, paquet: bytes | None = None,
            ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque saisie, ``{"cle", "saisie"}`` aux champs de ``Saisie``, simulée
    par le portage comme le site la simule (``Contexte.simuler``) : sous sa
    clé, la fiche de paie de l'année de référence sous le droit en vigueur
    (``remuneration.reference.droit_en_vigueur``), ou ``None`` sans fiche, le
    passage aux euros constants, la pension du système actuel et celle de
    chaque scénario. Puis, sous leur clé, les motifs des saisies que le
    portage refuse."""
    reponse = _demander({"saisies": {"cas": cas, "scenarios": list(scenarios)}}, paquet)
    resultats = {}
    for cle, lu in reponse["resultats"].items():
        fiche = lu["fiche"]
        resultats[cle] = {
            "fiche": None if fiche is None else {
                "annee": fiche["annee"],
                **{champ: _flottant(fiche[champ])
                   for champ in ("brut", "net", "retraite_totale", "retraite_employeur")},
            },
            "coefficient_euros_constants": _flottant(lu["coefficient_euros_constants"]),
            "pension_annuelle": _flottant(lu["pension_annuelle"]),
            "pensions": _par_scenario(lu["pensions"]),
        }
    return resultats, reponse["echecs"]


#: Les champs entiers du résultat d'une simulation (``Comparaison.dictionnaire()``,
#: que les témoins de simulations portent) : une année, un mois, des trimestres,
#: un compte d'années, une version — que le moteur Python calcule en ``int``.
#: Node n'écrit qu'un type de nombre : ces champs reviennent entiers, et un
#: nombre qui ne l'est pas y arrête la relecture.
ENTIERS_DU_RESULTAT = frozenset({
    "annee", "annee_bascule", "annee_liquidation", "annee_naissance", "annee_ouverture",
    "annees_cotisees", "duree_requise", "duree_requise_trimestres", "euros_constants_de",
    "mois", "mois_liquidation", "mois_naissance", "periode_de_reference", "schema_version",
    "trimestres", "trimestres_actuels",
})

#: Les champs flottants du résultat : les montants en euros, les âges, les
#: taux, les parts, les coefficients, les diviseurs et les points, que le
#: moteur Python calcule en flottants et écrit « 2.0 » là où node écrit « 2 ».
#: Leur zéro s'écrit « 0.0 », même là où le moteur Python le rend entier : le
#: zéro d'une somme vide, ``somme_ordonnee`` partant de l'entier 0, que le
#: portage ne distingue pas du zéro d'un flottant (décision du propriétaire,
#: 31 octobre 2026 ; action 161, étape 6).
FLOTTANTS_DU_RESULTAT = frozenset({
    "age", "age_conversion", "age_legal", "age_liquidation", "age_minimum", "age_ouverture",
    "age_ouverture_opposable", "age_taux_plein", "agent", "au_depart", "aujourd_hui", "base",
    "base_annuelle", "brute", "capital", "capital_a_la_bascule", "capital_droits_acquis",
    "capital_hors_frais", "capital_notionnel", "capital_volontaire", "coefficient",
    "coefficient_euros_constants", "coefficient_majoration", "coefficient_prix",
    "coefficient_revalorisation", "complement", "cotisations_employeur", "cotisations_versees",
    "cout_des_frais", "diviseur", "ecart_annees", "ecretement_du_maximum", "employeur",
    "esperance_capital_transmis", "esperance_residuelle", "facteur_encours_rente", "fraction",
    "frais_arrerages", "frais_encours_rente", "frais_preleves", "garantie_vieillesse",
    "interets", "isolement_annuel", "limite_cumul", "majoration", "majoration_enfants",
    "majoration_exceptionnelle", "majoration_forfaitaire_enfants",
    "majoration_petites_retraites", "majoration_trois_enfants", "maximum",
    "mensuel_decembre_2019", "minimum", "minimum_contributif", "minimum_vieillesse", "montant",
    "montant_a_l_effet", "montant_provisoire", "montant_servi", "non_servi", "part",
    "pension_annuelle", "pension_annuelle_euros_constants", "pension_contributive",
    "pension_figee", "pension_hors_repartition", "pension_mensuelle", "pension_totale",
    "pension_totale_euros_constants", "pension_totale_mensuelle", "pensions", "plafond",
    "plancher_annuel", "plancher_garantie", "points", "probabilite_deces_avant_liquidation",
    "quotite", "reduction", "reduction_de_la_revision", "reduction_du_cumul",
    "relevement_des_exploitants", "rendement_cumule", "rente_annuelle", "rente_capitalisation",
    "rente_capitalisation_obligatoire", "rente_capitalisation_volontaire", "rente_capitalisee",
    "rente_capitalisee_volontaire", "rente_mensuelle", "rente_volontaire", "ressources",
    "ressources_garantie", "ressources_retenues", "revenu", "revenu_annuel_moyen",
    "salaire_mensuel", "taux", "taux_cotisation", "taux_cotisation_volontaire",
    "taux_remplacement", "taux_rendement_annuel", "total", "total_contributif",
    "variation_vs_actuel", "versements",
})

#: Les dictionnaires du résultat dont les clés sont libres — un régime, un
#: scénario, l'origine des années d'une part employeur — et le type de leurs
#: valeurs : le capital par régime, la pension et le coefficient d'aujourd'hui
#: de chaque scénario, et des comptes d'années.
DICTIONNAIRES_DU_RESULTAT = {
    "capital_par_regime": float, "notionnels": float, "coefficients_notionnels": float,
    "annees_par_origine": int, "annees_part_employeur": int,
}

def _nombre_du_resultat(valeur, type_: type, chemin: str):
    """Un nombre du résultat sous ``type_`` ; ``None`` pour un nombre non fini,
    que node écrit « null » comme ``_fini`` l'écrit dans les témoins. Un entier
    doit en être un."""
    if valeur is None:
        return None
    if type_ is int:
        if type(valeur) is not int:
            raise TypeError(f"{chemin} : entier attendu, le portage a écrit {valeur!r}")
        return valeur
    return float(valeur)


def resultat_des_donnees(donnees: dict) -> dict:
    """Le résultat d'une simulation que le portage a écrit
    (``Comparaison.dictionnaire()``), sous les types que le moteur Python lui
    donne, déclarés champ par champ (:data:`ENTIERS_DU_RESULTAT`,
    :data:`FLOTTANTS_DU_RESULTAT`, :data:`DICTIONNAIRES_DU_RESULTAT`) : node
    n'écrit qu'un type de nombre, « 2 » pour 2.0. Un nombre sous un champ que
    la table ne déclare pas arrête la relecture, au lieu d'en deviner le type ;
    un nombre non fini reste ``None``, un texte et un booléen ce qu'ils sont.
    Les témoins de simulations s'écrivent sous elle
    (``scripts/construire_temoins.py``), et ce que le moteur Python simule pour
    leur être confronté aussi (``tests/test_pont.py``)."""

    def relire(valeur, nom: str | None, chemin: str):
        if isinstance(valeur, dict):
            if nom in DICTIONNAIRES_DU_RESULTAT:
                return {cle: _nombre_du_resultat(element, DICTIONNAIRES_DU_RESULTAT[nom],
                                                 f"{chemin}.{cle}")
                        for cle, element in valeur.items()}
            return {cle: relire(element, cle, f"{chemin}.{cle}" if chemin else cle)
                    for cle, element in valeur.items()}
        if isinstance(valeur, list):
            return [relire(element, nom, f"{chemin}[{rang}]")
                    for rang, element in enumerate(valeur)]
        if valeur is None or isinstance(valeur, (bool, str)):
            return valeur
        if nom in ENTIERS_DU_RESULTAT:
            return _nombre_du_resultat(valeur, int, chemin)
        if nom in FLOTTANTS_DU_RESULTAT:
            return _nombre_du_resultat(valeur, float, chemin)
        raise ValueError(f"{chemin} : un nombre que la table des types du résultat ne "
                         "déclare pas (pont.ENTIERS_DU_RESULTAT, pont.FLOTTANTS_DU_RESULTAT)")

    return relire(donnees, None, "")


def _entier(valeur, nom: str) -> int:
    """Un entier que le portage a écrit : il doit en être un."""
    if type(valeur) is not int:
        raise TypeError(f"{nom} : entier attendu, le portage a écrit {valeur!r}")
    return valeur


def scenario_actuel_des_donnees(donnees: dict) -> dict:
    """Le scénario 1 que le portage a servi (:func:`scenario_actuel`), sous
    les types que le Python lui donne : la date du départ, ses trimestres et
    l'année de la réversion en entiers, qui doivent en être ; les montants, les
    parts, le taux et le coefficient en flottants, que node écrit « 2 » pour
    2.0 ; un texte, un booléen et ``None`` tels qu'ils sont."""
    actuel, reversion = donnees["actuel"], donnees["reversion"]
    return {
        "annee_liquidation": _entier(donnees["annee_liquidation"], "annee_liquidation"),
        "mois_liquidation": _entier(donnees["mois_liquidation"], "mois_liquidation"),
        "coefficient_euros_constants": _flottant(donnees["coefficient_euros_constants"]),
        "actuel": {
            "pension_annuelle": _flottant(actuel["pension_annuelle"]),
            "pension_hors_repartition": _flottant(actuel["pension_hors_repartition"]),
            "pensions_par_regime": [
                {"regime": pension["regime"], "montant": _flottant(pension["montant"]),
                 "detail": pension["detail"]}
                for pension in actuel["pensions_par_regime"]],
            "avantages_appliques": [
                {"code": avantage["code"], "montant": _flottant(avantage["montant"]),
                 "par_regime": [(regime, _flottant(part))
                                for regime, part in avantage["par_regime"]]}
                for avantage in actuel["avantages_appliques"]],
            "trimestres_valides": _entier(actuel["trimestres_valides"], "trimestres_valides"),
            "taux_liquidation": _flottant(actuel["taux_liquidation"]),
            "liquidation_ouverte": actuel["liquidation_ouverte"],
            "motif_ouverture": actuel["motif_ouverture"],
        },
        "reversion": None if reversion is None else {
            "annee": _entier(reversion["annee"], "reversion.annee"),
            "regimes": [{"regime": ligne["regime"], "montant": _flottant(ligne["montant"]),
                         "date_effet": ligne["date_effet"]}
                        for ligne in reversion["regimes"]],
        },
    }


def scenario_actuel(cas: list[dict], paquet: bytes | None = None,
                    ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque requête du simulateur, ``{"cle", "requete"}``, lue par la saisie
    du portage et simulée comme le site la simule (``Contexte.simuler``) — tel
    quel un relevé que l'appelant a déjà prolongé à sa façon, avec
    ``"prolonger": False`` : sous sa clé, ce que les confrontations aux
    références extérieures lisent de son scénario 1, relu sous les types du
    Python (:func:`scenario_actuel_des_donnees`). ``"actuel"`` en porte la
    pension et, à part, ce qui est hors de la répartition ; chaque pension de
    régime (``regime``, ``montant``, ``detail``) ; chaque avantage appliqué
    (``code``, ``montant``, et la part de chaque régime, ``par_regime``) ; la
    durée validée, le taux, l'ouverture et son motif. À côté : la date du
    départ, le passage aux euros constants, et la réversion, ``None`` sans
    elle (son ``annee``, et chacun de ses ``regimes`` : ``regime``,
    ``montant``, ``date_effet``). Puis, sous leur clé, les motifs des
    requêtes que le portage refuse."""
    reponse = _demander({"scenario_actuel": {"cas": cas}}, paquet)
    return ({cle: scenario_actuel_des_donnees(lu) for cle, lu in reponse["resultats"].items()},
            reponse["echecs"])


def simulations(cas: list[dict], paquet: bytes | None = None,
                ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque requête d'un témoin de simulations, ``{"cle", "requete"}``, lue
    par la saisie du portage et simulée comme le site la simule
    (``Contexte.simuler``), comme ``tests/js/moteur.test.js`` la simule : sous
    sa clé, son résultat (``Comparaison.dictionnaire()``), relu sous les types
    du Python (:func:`resultat_des_donnees`), et les appels de ``liquider`` que
    sa simulation a faits, liquidations d'essai comprises
    (``appels_liquider``). Puis, sous leur clé, les motifs des requêtes que le
    portage refuse."""
    reponse = _demander({"simulations": {"cas": cas}}, paquet)
    resultats = {cle: {"resultat": resultat_des_donnees(lu["resultat"]),
                       "appels_liquider": lu["appels_liquider"]}
                 for cle, lu in reponse["resultats"].items()}
    return resultats, reponse["echecs"]
