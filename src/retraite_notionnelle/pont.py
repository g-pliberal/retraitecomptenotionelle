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

La grille du coût passe le pont en deux demandes, sous les paramètres du
simulateur (:func:`parametres_en_donnees`), sur le paquet des données du jour
(:func:`paquet_des_donnees`), ou sur celui de données d'ailleurs, une copie
que l'on a retouchée, que la fabrique bâtit depuis elles. Le portage la date et la bâtit
(:func:`carrieres_de_la_grille`, :func:`ages_de_depart`) : le Python, qui
garde la définition des cas types et les conventions de projection du COR,
ne lui passe que ce que chacun décrit — sa règle de départ, les options de sa
carrière, les deux métiers de l'entrée tardive d'un fonctionnaire — et la part
des primes que le décrochage du traitement porte
(``castypes.primes_projetees_en_donnees``). Puis le portage la simule
(:func:`grille_du_cout`), chaque carrière passée en données
(:func:`carriere_en_donnees`) : celle qu'il a bâtie, ou, pour la grille
large, dont les cas types datent et bâtissent autrement leurs carrières,
celle que le Python bâtit.

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
Les exemples d'OpenFisca et des caisses (``tests/test_oracle.py``) éprouvent
le droit fonction par fonction, sur des carrières bâties à la main : le pont
fait appeler chacune au portage (:func:`droit`), et relit ce qu'elle rend
sous le type de son jumeau (:data:`LECTURES_DU_DROIT`).

Les sondes de la prose et les mesures de l'accueil, enfin
(``scripts/mesures_prose.py``, ``scripts/solde_fusion.py``) : la carrière
qu'elles bâtissaient et simulaient, et les règles qu'elles appelaient une à
une — l'indexation, la conversion, la fusion, la garantie, le pilier —, se
demandent au même pont du droit (:data:`LECTURES_DES_SONDES`), sous les
paramètres de chaque mesure.

La garantie d'une population, de même, que le coût fait et que le site refait
sur d'autres cas : le barème appliqué à la distribution des pensions ne
s'écrit qu'en JavaScript (``moteur/js/garantie.js``, note de décision 0007),
et le coût, l'effet retour et ``scripts/garantie_par_sexe.py`` le demandent
par lot (:func:`garantie`), leurs distributions passées en données.

L'impôt sur le revenu, enfin, que le site calcule sur la carrière du lecteur
(``moteur/js/impot-revenu.js``, note de décision 0007) : l'effet retour du
coût le demande par lot, une année à la fois (:func:`impot`), ses foyers
passés en données, au barème que le portage lit au paquet et projette.

La revalorisation servie et l'indexation, de même, que le lecteur du site
règle (``moteur/js/revalorisation.js`` et ``indexation.js``, note de décision
0007) : ``RevalorisationServie`` du Python en demande les séries, une fois
par jeu de paramètres (:func:`series_servies`), et ne fait plus que les
lire ; le coût demande d'un lot ce que l'indexation rend à ses cotisations
sous une variante démographique (:func:`indexation`). Les lectures du portage
se demandent aussi une à une, pour les confronter à celles que le Python
garde (:func:`revalorisation_servie`).

Ce que le droit a servi aux pensions liquidées, que le coût seul lit, reste
en Python (``RevalorisationServie.coefficient_historique``), mais les règles
du moteur qu'il appelle — la valeur de service d'un point, le coefficient de
l'article L. 161-23-1, les décrets de la fonction publique, le point d'indice,
le changement d'unité d'un point — se demandent au pont du droit, d'un lot
par règle de revalorisation (:data:`LECTURES_DE_L_HISTOIRE_DU_DROIT`).

Une demande sur le paquet du dépôt, sans paquet, ne lance pas node à chaque
fois : les tests en font une par carrière, et chacune coûtait trois dixièmes
de seconde, à lancer node et à relire le paquet. Le pont reste ouvert
(``pont.mjs --servir``), sur le paquet qu'il a lu, jusqu'à ce que ce paquet
change ou que le processus finisse ; node mort, la demande en cours échoue,
avec son journal, et la suivante le relance.
"""

from __future__ import annotations

import atexit
import contextlib
import dataclasses
import enum
import functools
import hashlib
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

from .calendrier import DateMois
from .config import RACINE_PROJET
from .donnees.chargement import Fiabilite

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


#: La garde des présomptions (``tests/conftest.py`` ; action 135, levier 2) :
#: posée, elle fait dire au vocabulaire du Python d'autres valeurs présumées,
#: et le portage lit les mêmes dans son paquet (``sousLaGarde`` de
#: ``pont.mjs``).
PRESOMPTIONS_DECALEES = "PRESOMPTIONS_DECALEES"


def _signature_du_paquet() -> tuple[int, int, bool]:
    """La date et la taille du paquet du dépôt, que la fabrique récrit, et la
    garde des présomptions, sous laquelle le portage le lit décalé."""
    etat = (RACINE_PROJET / "moteur" / "donnees.json").stat()
    return etat.st_mtime_ns, etat.st_size, bool(os.environ.get(PRESOMPTIONS_DECALEES))


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

    def vivant(self) -> bool:
        """Node tourne-t-il encore ? Mort, tué ou tombé, le pont se relance à
        la demande suivante (:func:`_ouvert`)."""
        return self._processus.poll() is None

    def demander(self, demande: dict) -> dict:
        """La réponse de node ; s'il s'arrête en chemin, la demande échoue,
        avec son journal, et le pont se referme."""
        try:
            self._processus.stdin.write(json.dumps({"demande": demande}) + "\n")
            self._processus.stdin.flush()
        except BrokenPipeError:
            pass  # node s'est arrêté : la lecture le dit, avec son journal
        ligne = self._processus.stdout.readline()
        if not ligne:
            self._journal.seek(0)
            journal = self._journal.read().decode("utf-8", "replace")[-2000:]
            self.fermer()
            raise RuntimeError(f"{PROGRAMME.name} : node s'est arrêté : {journal}")
        reponse = json.loads(ligne)
        if "erreur" in reponse:
            raise RuntimeError(f"{PROGRAMME.name} : {reponse['erreur']}")
        return reponse["reponse"]

    def fermer(self) -> None:
        """Ferme le tuyau d'entrée : node vivant finit et s'arrête ; mort, ce
        qu'on lui écrivait et qu'il n'a pas lu s'y perd, sans que Python le
        signale en ramassant le tuyau."""
        with contextlib.suppress(BrokenPipeError):
            self._processus.stdin.close()
        try:
            self._processus.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self._processus.kill()


def _du_depot(racine) -> bool:
    """``racine`` est-elle celle des données du dépôt ?"""
    from .config import RACINE_DONNEES

    try:
        return Path(racine).resolve() == RACINE_DONNEES.resolve()
    except OSError:
        return False


def _paquet_de(parametres, paquet: bytes | None) -> bytes | None:
    """Le paquet sur lequel se calcule une demande sous ``parametres`` :
    ``paquet``, ou, sans lui, ``moteur/donnees.json``, sur les données du
    dépôt. Des données d'ailleurs se calculent sur le leur
    (:func:`paquet_des_donnees`) : sans paquet, le pont le prend ; un autre, il
    le refuse, qui ferait calculer la demande sur d'autres données que les
    siennes."""
    if parametres is None or _du_depot(parametres.racine_donnees):
        return paquet
    leur = paquet_des_donnees(parametres.racine_donnees)
    if paquet is not None and paquet is not leur and paquet != leur:
        raise ValueError(
            f"des données d'ailleurs ({parametres.racine_donnees}) se calculent sur leur "
            "paquet : pont.paquet_des_donnees(parametres.racine_donnees)")
    return leur


#: Le pont gardé ouvert de ce processus, s'il y en a un.
_OUVERT: _PontOuvert | None = None


def _ouvert() -> _PontOuvert:
    """Le pont ouvert sur le paquet du dépôt tel qu'il est : relancé quand la
    fabrique l'a récrit, ou quand node s'est arrêté (action 190, étape 3)."""
    global _OUVERT
    if (_OUVERT is None or _OUVERT.signature != _signature_du_paquet()
            or not _OUVERT.vivant()):
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
              univers: dict[str, dict] | None = None, parametres=None,
              ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque carrière d'un seul statut, ``{"cle", "options"}`` aux options de
    ``carriere_simple``, simulée par le portage sous les réglages de
    référence, ou sous les ``parametres`` d'une étude, que la demande porte —
    le stock à l'âge légal (``Parametres.stock_age_legal``, action 161),
    qu'aucun réglage de référence ne porte : sous sa clé, l'année de son
    départ et celle de chaque
    scénario, l'écart de chacun au système actuel, pilier capitalisé compris
    (``variation_totale``) ou non (``variation``), la pension du système
    actuel et la durée qu'il requiert ; la pension de chaque scénario, pilier
    capitalisé compris (``pension_totale``), et la rente des points
    volontaires (``rente_capitalisee_volontaire``) ; la pension de l'étalon
    et de chaque scénario, hors du pilier, en euros constants
    (``pensions_euros_constants``) ; et, pour qui est déjà
    parti, ce que le système actuel et chaque scénario lui servent
    aujourd'hui (``Comparaison.aujourd_hui``), sinon ``None``. Puis, sous leur
    clé, les motifs des carrières que le portage refuse. ``univers`` porte les
    variantes d'une étude, chacune à la place du calcul que le paquet porte
    sous sa clé (``Simulateur.univers_de_la_demande``, action 161)."""
    demande = {"cas": cas, "scenarios": list(scenarios), "univers": dict(univers or {})}
    if parametres is not None:
        demande["parametres"] = parametres_en_donnees(parametres)
    reponse = _demander({"carrieres": demande}, _paquet_de(parametres, paquet))
    resultats = {
        cle: {
            "annee_liquidation": lu["annee_liquidation"],
            "annees_liquidation": dict(lu["annees_liquidation"]),
            "variations": _par_scenario(lu["variations"]),
            "ecarts": _par_scenario(lu["ecarts"]),
            "pension_annuelle": _flottant(lu["pension_annuelle"]),
            "trimestres_requis": lu["trimestres_requis"],
            "pensions_totales": _par_scenario(lu["pensions_totales"]),
            "rentes_volontaires": _par_scenario(lu["rentes_volontaires"]),
            "pensions_euros_constants": _par_scenario(lu["pensions_euros_constants"]),
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
    if isinstance(valeur, (set, frozenset)):
        # Un ensemble, en liste triée, comme le portage écrit un ``Set``.
        return sorted(_en_donnees(element) for element in valeur)
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
    champs, tous et rien d'autre, une suite en tuple ou en liste, un
    dictionnaire clé par clé."""
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
    if typing.get_origin(type_) is dict:
        type_des_cles, type_des_valeurs = typing.get_args(type_)
        return {_depuis_donnees(type_des_cles, cle): _depuis_donnees(type_des_valeurs, element)
                for cle, element in valeur.items()}
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


#: La fabrique du paquet, que :func:`_batir_le_paquet` fait tourner.
FABRIQUE = RACINE_PROJET / "scripts" / "construire_donnees.py"

#: Le programme qui bâtit le paquet des données du jour, dans un processus à
#: lui. Sur des données d'ailleurs, sa racine, le second argument, prend la
#: place de ``DONNEES``, et ce qu'il lit des données du dépôt, qu'un autre
#: chemin que sa racine y mènerait, l'arrête.
_BATIR_LE_PAQUET = """\
import importlib.util, os, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("construire_donnees", sys.argv[1])
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
lues = set()
if len(sys.argv) > 2:
    depot = os.path.normcase(os.path.join(os.path.abspath(module.DONNEES), ""))
    module.DONNEES = Path(sys.argv[2])

    def garde(evenement, arguments):
        if (evenement in ("open", "os.listdir", "os.scandir") and arguments
                and isinstance(arguments[0], (str, bytes, os.PathLike))):
            chemin = os.path.abspath(os.fsdecode(arguments[0]))
            if os.path.normcase(chemin).startswith(depot):
                lues.add(chemin)

    sys.addaudithook(garde)
paquet = module.construire(b"{}", b"{}")
if lues:
    sys.exit(f"bâti sur {sys.argv[2]}, le paquet lit {len(lues)} chemins des données du "
             "dépôt : " + ", ".join(sorted(lues)[:5]))
sys.stdout.buffer.write(paquet)
"""


#: Le dernier paquet du jour que ce processus a bâti, sous la signature des
#: sources d'où il l'a bâti (``memoire.signature``).
_PAQUET: tuple[str | None, bytes] | None = None
#: Le dernier paquet de données d'ailleurs, sous leur racine, la signature des
#: sources et celle de leurs fichiers.
_PAQUET_D_AILLEURS: tuple[tuple, bytes] | None = None


def paquet_des_donnees(racine: Path | None = None) -> bytes:
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
    anciennes.

    Des données d'ailleurs, ``racine`` — une copie que l'on a retouchée
    (``scripts/facteurs_depense.py --sans-suspension``) —, ont le leur, que la
    fabrique bâtit de même depuis elles, sans rien lire des données du dépôt,
    une fois par état de leurs fichiers et des sources (action 161, « le coût
    sous un modèle modifié »)."""
    global _PAQUET, _PAQUET_D_AILLEURS
    from .memoire import signature

    if racine is not None and not _du_depot(racine):
        racine = Path(racine).resolve()
        etat = (racine, signature(), _signature_des_fichiers(racine))
        if _PAQUET_D_AILLEURS is None or _PAQUET_D_AILLEURS[0] != etat:
            _PAQUET_D_AILLEURS = (etat, _batir_le_paquet(racine))
        return _PAQUET_D_AILLEURS[1]
    etat = signature()
    if _PAQUET is None or _PAQUET[0] != etat:
        _PAQUET = (etat, _batir_le_paquet())
    return _PAQUET[1]


def _signature_des_fichiers(racine: Path) -> str:
    """Les fichiers de ``racine`` tels que le disque les décrit — le chemin, la
    taille et la date de chacun —, sans les lire, comme ``memoire.signature``
    décrit les sources."""
    somme = hashlib.sha256()
    for dossier, sous_dossiers, fichiers in os.walk(racine):
        sous_dossiers.sort()
        for nom in sorted(fichiers):
            chemin = os.path.join(dossier, nom)
            etat = os.stat(chemin)
            somme.update(f"{os.path.relpath(chemin, racine)}\0{etat.st_size}:"
                         f"{etat.st_mtime_ns}\0".encode("utf-8", "surrogateescape"))
    return somme.hexdigest()


def _batir_le_paquet(racine: Path | None = None) -> bytes:
    """Le paquet du jour, bâti par la fabrique elle-même
    (``scripts/construire_donnees.py``), dans un processus à elle, comme node
    fait tourner le moteur JavaScript dans le sien : ce qu'elle lit pour le
    site seul — les crédits des ministères, le manifeste des sources, qu'aucun
    calcul ne lit — n'entre ni dans les mémoires des chargeurs de ce
    processus-ci, ni dans le relevé de ce que lisent les calculs gardés
    (``memoire.HORS_DU_MODELE``). Celui de données d'ailleurs, sur ``racine``."""
    environnement = {**os.environ, "PYTHONPATH": os.pathsep.join(filter(None, (
        str(RACINE_PROJET / "src"), os.environ.get("PYTHONPATH"))))}
    execution = subprocess.run(
        [sys.executable, "-c", _BATIR_LE_PAQUET, str(FABRIQUE),
         *(() if racine is None else (str(racine),))],
        cwd=RACINE_PROJET, env=environnement, capture_output=True, check=False)
    if execution.returncode != 0:
        raise RuntimeError(
            "le paquet des données " + ("du jour" if racine is None else f"de {racine}")
            + " ne se bâtit pas : "
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


# -- ce que l'étude de la mortalité demande (action 161) ---------------------------

#: Ce que la grille du coût rend du compte de chaque scénario que sa demande
#: nomme sous ``capitaux`` (:func:`grille_du_cout`, ``capitauxDuCompte`` de
#: ``pont.mjs``) : son capital à la liquidation, et ce qu'en portent les
#: droits acquis à la bascule. ``scripts/mortalite_population.py`` en tire la
#: part de chaque pension que porte le compte ouvert à la bascule.
CAPITAUX_DU_COMPTE = ("capital_droits_acquis", "capital_notionnel")


def _capitaux_du_compte(lus: dict) -> dict[str, dict[str, float]]:
    return {scenario: {champ: _flottant(capitaux[champ]) for champ in CAPITAUX_DU_COMPTE}
            for scenario, capitaux in lus.items()}


def grille_du_cout(cas: list[dict], scenarios, parametres, paquet: bytes | None = None,
                   univers: dict[str, dict] | None = None, comptes=(), capitaux=(),
                   ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque case de la grille du coût, ``{"cle", "carriere",
    "propositions"}`` — sa carrière, et celles, nommées, sur lesquelles le coût
    calcule la proposition seule —, simulée par le portage sous
    ``parametres``, ceux de la projection : sous sa clé, ce que le coût en lit
    (``cout._simulations``). Puis, sous leur clé, les motifs des cases que le portage refuse.
    ``univers`` porte les variantes d'une étude, chacune à la place du calcul
    que le paquet porte sous sa clé (``Simulateur.univers_de_la_demande``,
    action 161). ``comptes`` nomme les scénarios dont chaque case rend de plus
    les lignes du compte, sous ``comptes`` — ce qu'il porte, année par année,
    et sur quels revenus : le compte du scénario 4 sous le barème d'un régime
    unique, que ``scripts/solde_fusion.py`` lit (action 161). ``capitaux``
    nomme ceux dont chaque case rend, sous ``capitaux``, le capital du compte
    à la liquidation et ce qu'en portent les droits acquis à la bascule, que
    ``scripts/mortalite_population.py`` lit (:func:`_capitaux_du_compte`)."""
    reponse = _demander({"grille_du_cout": {
        "parametres": parametres_en_donnees(parametres),
        "univers": dict(univers or {}),
        "scenarios": list(scenarios),
        "comptes": list(comptes),
        "capitaux": list(capitaux),
        "cas": [{"cle": un["cle"], "carriere": carriere_en_donnees(un["carriere"]),
                 "propositions": {nom: carriere_en_donnees(carriere)
                                  for nom, carriere in un["propositions"].items()}}
                for un in cas],
    }}, _paquet_de(parametres, paquet))
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
            "comptes": {scenario: {"cotisations": _serie(compte["cotisations"]),
                                   "revenus": _serie(compte["revenus"])}
                        for scenario, compte in lu["comptes"].items()},
            "capitaux": _capitaux_du_compte(lu["capitaux"]),
        }
        for cle, lu in reponse["resultats"].items()
    }
    return resultats, reponse["echecs"]


def ages_de_depart(cas: list[dict], parametres, primes: dict[int, float] | None = None,
                   variante: str = "droit", paquet: bytes | None = None,
                   ) -> tuple[dict[str, float], frozenset[str], dict[str, str]]:
    """L'âge de départ de chaque cas type, ``{"cle", "regle", "options"}`` —
    ce que sa règle lit, et les options de sa carrière d'un seul statut, sans
    l'âge (``CasType.pour_le_portage``) —, que le pilote du portage fixe
    (``ageDeDepart`` de ``moteur/js/pilote.js``) sous ``parametres``, la part
    des primes projetée comme le COR la projette quand ``primes`` porte le
    traitement relatif de chaque année (``castypes.primes_projetees_en_donnees``) :
    sous sa clé, l'âge, en flottant. Un cas type de la grille élargie y ajoute
    son parcours et l'attente de son départ (``CasTypeLarge.pour_le_portage``,
    étape 7) : les clés des âges que l'attente fixe suivent. Puis, sous leur
    clé, les motifs des cas que le portage refuse. Son jumeau est
    ``pilote.age_de_depart`` (action 161, étape 6)."""
    reponse = _demander({"ages_de_depart": {
        "parametres": parametres_en_donnees(parametres), "variante": variante,
        "primes": primes, "cas": cas}}, _paquet_de(parametres, paquet))
    return ({cle: _flottant(age) for cle, age in reponse["resultats"].items()},
            frozenset(reponse["attendus"]), reponse["echecs"])


def carrieres_de_la_grille(cas: list[dict], parametres, primes: dict[int, float] | None = None,
                           variante: str = "droit", paquet: bytes | None = None,
                           ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque case de la grille du coût, ``{"cle", "regle", "options",
    "entree", "rendre"}`` (``CasType.pour_le_portage``), datée et bâtie par le
    portage sous ``parametres`` (``carrieresDeLaGrille`` de ``pont.mjs``) :
    sous sa clé, l'âge de son départ (:func:`ages_de_depart`) et, selon
    ``rendre`` — ``"depart"``, l'année et le mois du départ (``annee``,
    ``mois``) ; ``"carriere"``, la carrière, relue sous les types du Python
    (:func:`carriere_des_donnees`), et les deux que l'âge légal de la
    proposition en dérive, poursuivie jusqu'à lui (``reportee``) ou attendue
    sans activité (``attente``), ``None`` quand il ne la reporte pas. Puis,
    sous leur clé, les motifs des cases que le droit écarte
    (``castypes.carriere_de_la_grille``) ou que le portage refuse."""
    reponse = _demander({"carrieres_de_la_grille": {
        "parametres": parametres_en_donnees(parametres), "variante": variante,
        "primes": primes, "cas": cas}}, _paquet_de(parametres, paquet))
    resultats = {}
    for cle, lu in reponse["resultats"].items():
        if "carriere" in lu:
            resultats[cle] = {"age": _flottant(lu["age"]),
                              **{nom: None if lu[nom] is None else carriere_des_donnees(lu[nom])
                                 for nom in ("carriere", "reportee", "attente")}}
        else:
            resultats[cle] = {"age": _flottant(lu["age"]), "annee": lu["annee"], "mois": lu["mois"]}
        # L'âge que l'attente d'un cas type de la grille élargie fixe
        # (``castypes.age_lu``, étape 7).
        if lu.get("attendu"):
            resultats[cle]["attendu"] = True
    return resultats, reponse["echecs"]


def departs_des_cas(cas: list[dict], parametres, primes: dict[int, float] | None = None,
                    paquet: bytes | None = None) -> tuple[dict[str, dict], dict[str, str]]:
    """Le départ de chaque cas type, ``{"cle", "regle", "options", "parcours",
    "entree", "attente", "lire"}`` (``CasType.pour_le_portage``), au scénario 1,
    sous ``parametres`` (``departsDesCas`` de ``pont.mjs``) : ce que lisent
    les mesures de ``scripts/grille_large.py`` (``Departs``, action 161,
    étape 7). Sous sa clé, l'âge que son pilote fixe (``"age"``, en flottant),
    ``"attendu"`` quand l'attente d'un cas type de la grille élargie le fixe,
    et, sauf sous ``"lire": "age"``, ce que l'échéancier lit à ce départ
    (``"depart"``) — le taux, la durée requise et la durée validée, le motif
    de l'ouverture, chaque avantage appliqué, ``(code, montant)``, chaque
    pension de régime, ``(regime, montant, surcote)`` —, ou ``None`` et le
    motif qui le refuse (``"refus"``). Puis, sous leur clé, les motifs des cas
    dont le portage refuse l'âge. Sous ``"lire": "liquidation"``, que lit
    ``scripts/flux_fonction_publique.py`` (action 161, lot B), le cas est une
    case de la grille, que le droit peut écarter comme
    ``castypes.carriere_de_la_grille`` l'écarte, sous le même motif ; et son
    départ porte de plus son année (``"annee"``) et ce que le journal garde de
    sa liquidation (``"liquidation"``) : chaque pension du code des pensions,
    ``(regime, montant, traitement)``, la pension avant tout complément et le
    traitement de l'article L. 15 qui la liquide. Sous ``"lire": "minimum"``,
    que lit ``scripts/part_minimum_contributif.py`` (étape 6d), son départ
    porte de plus ``"minimum"`` (:func:`_minimum_des_donnees`)."""
    reponse = _demander({"departs_des_cas": {
        "parametres": parametres_en_donnees(parametres), "primes": primes, "cas": cas}},
        _paquet_de(parametres, paquet))
    resultats = {}
    for cle, lu in reponse["resultats"].items():
        depart = None
        if "taux_liquidation" in lu:
            depart = {
                "taux_liquidation": _flottant(lu["taux_liquidation"]),
                "trimestres_requis": _entier(lu["trimestres_requis"], "trimestres_requis"),
                "trimestres_valides": _entier(lu["trimestres_valides"], "trimestres_valides"),
                "motif_ouverture": lu["motif_ouverture"],
                "avantages": tuple((code, _flottant(montant))
                                   for code, montant in lu["avantages_appliques"]),
                "pensions": tuple((regime, _flottant(montant), _flottant(surcote))
                                  for regime, montant, surcote in lu["pensions_par_regime"]),
            }
            if "minimum" in lu:
                depart["minimum"] = _minimum_des_donnees(lu["minimum"])
            if "liquidation" in lu:
                depart["annee"] = _entier(lu["annee"], "annee")
                depart["liquidation"] = tuple(
                    (regime, _flottant(montant), _flottant(traitement))
                    for regime, montant, traitement in lu["liquidation"])
        resultats[cle] = {"age": _flottant(lu["age"]), "attendu": bool(lu.get("attendu")),
                          "depart": depart, "refus": lu.get("refus")}
    return resultats, reponse["echecs"]


def _minimum_des_donnees(lu: dict) -> dict:
    """Ce que la mesure du minimum contributif lit d'un départ
    (``minimumAuDepart`` de ``pont.mjs``), sous les types du Python : l'année
    et le mois de la liquidation, entiers ; chaque pension, ``(regime,
    montant, date_effet)``, la date ``None`` sous un départ unique ; chaque
    minimum contributif appliqué, ``(part de chaque régime, détail)`` ; le
    minimum avant écrêtement, ``None`` sans lui."""
    avant = lu["avant_ecretement"]
    return {
        "annee": _entier(lu["annee"], "minimum.annee"),
        "mois": _entier(lu["mois"], "minimum.mois"),
        "pensions": tuple((regime, _flottant(montant), date_effet)
                          for regime, montant, date_effet in lu["pensions"]),
        "minima": tuple((tuple((regime, _flottant(part)) for regime, part in minimum["par_regime"]),
                         minimum["detail"]) for minimum in lu["minima"]),
        "avant_ecretement": None if avant is None else _flottant(avant),
    }


def debuts_de_la_surcote(cas: list[dict], parametres, primes: dict[int, float] | None = None,
                         paquet: bytes | None = None,
                         ) -> tuple[dict[str, float | None], dict[str, str]]:
    """Le premier âge d'où le modèle sert une surcote à la pension de
    fonctionnaire de chaque cas type, ``{"cle", …, "plein", "recherche"}``
    (``CasType.pour_le_portage``), sur les ``recherche`` trimestres comptés de
    part et d'autre de l'âge ``plein`` (``debutsDeLaSurcote`` de
    ``pont.mjs``) : sous sa clé, cet âge, en flottant, ou ``None`` sans
    surcote. Puis, sous leur clé, les motifs des cas que le portage refuse.
    Son jumeau est ``debut_de_la_surcote`` de ``scripts/grille_large.py``
    (action 161, étape 7)."""
    reponse = _demander({"debuts_de_la_surcote": {
        "parametres": parametres_en_donnees(parametres), "primes": primes, "cas": cas}},
        _paquet_de(parametres, paquet))
    return ({cle: None if debut is None else _flottant(debut)
             for cle, debut in reponse["resultats"].items()}, reponse["echecs"])


def avantages(cas: list[dict], parametres, paquet: bytes | None = None,
              ) -> tuple[dict[str, dict], dict[str, str]]:
    """Chaque case du coût des avantages non contributifs, ``{"cle",
    "options", "carriere", "scenario"}`` — les options de sa carrière d'un
    seul statut (``avantages._options_de_la_variante``) ; les périodes non
    travaillées de chaque contrefactuelle qui les change, sous son code ; les
    codes des scénarios neutralisés sous lesquels la liquider
    (``avantages._variantes_demandees``) —, bâtie et liquidée au scénario 1
    par le portage sous ``parametres`` (``avantages`` de ``pont.mjs``) : sous
    sa clé, ce que la décomposition lit de sa liquidation (``"liquidee"``,
    les champs de ``avantages._Liquidee``) et, sous ``"sans"``, la pension et
    la durée requise de chaque contrefactuelle que les gardes de
    ``avantages.recalculer`` laissent, ``(pension, durée)`` sous son code.
    Puis, sous leur clé, les motifs des cases que le droit écarte
    (``castypes.carriere_de_la_grille``) ou que le portage refuse."""
    reponse = _demander({"avantages": {
        "parametres": parametres_en_donnees(parametres), "cas": cas}},
        _paquet_de(parametres, paquet))
    resultats = {}
    for cle, lu in reponse["resultats"].items():
        resultats[cle] = {
            "liquidee": {
                "annee_liquidation": _entier(lu["annee_liquidation"], "annee_liquidation"),
                "age_liquidation": _flottant(lu["age_liquidation"]),
                "pension_annuelle": _flottant(lu["pension_annuelle"]),
                "total_contributif": _flottant(lu["total_contributif"]),
                "trimestres_requis": _entier(lu["trimestres_requis"], "trimestres_requis"),
                "motif_ouverture": lu["motif_ouverture"],
                "avantages": tuple((code, _flottant(montant))
                                   for code, montant in lu["avantages_appliques"]),
            },
            "sans": {code: (_flottant(pension), _entier(requis, f"sans.{code}"))
                     for code, (pension, requis) in lu["sans"].items()},
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


def actuel_des_donnees(actuel: dict) -> dict:
    """Le résultat du scénario 1 que le portage a écrit (``actuelEnDonnees`` de
    ``pont.mjs``), sous les types que le Python lui donne : les trimestres,
    validés et requis, en entiers, qui doivent en être ; les montants, les
    parts et le taux en flottants, que node écrit « 2 » pour 2.0 ; un texte et
    un booléen tels qu'ils sont — le type de calcul et le détail de chaque
    pension, le détail de chaque avantage, la date d'effet et le motif de
    chaque départ inscrit."""
    return {
        "pension_annuelle": _flottant(actuel["pension_annuelle"]),
        "pension_hors_repartition": _flottant(actuel["pension_hors_repartition"]),
        "pensions_par_regime": [
            {"regime": pension["regime"], "montant": _flottant(pension["montant"]),
             "type_calcul": pension["type_calcul"], "detail": pension["detail"]}
            for pension in actuel["pensions_par_regime"]],
        "avantages_appliques": [
            {"code": avantage["code"], "montant": _flottant(avantage["montant"]),
             "detail": avantage["detail"],
             "par_regime": [(regime, _flottant(part))
                            for regime, part in avantage["par_regime"]],
             "par_regime_sans_anticipation": [
                 (regime, _flottant(part))
                 for regime, part in avantage["par_regime_sans_anticipation"]],
             "a_charge": [(depuis, [(regime, _flottant(part)) for regime, part in parts])
                          for depuis, parts in avantage["a_charge"]]}
            for avantage in actuel["avantages_appliques"]],
        "trimestres_valides": _entier(actuel["trimestres_valides"], "trimestres_valides"),
        "trimestres_requis": _entier(actuel["trimestres_requis"], "trimestres_requis"),
        "taux_liquidation": _flottant(actuel["taux_liquidation"]),
        "liquidation_ouverte": actuel["liquidation_ouverte"],
        "motif_ouverture": actuel["motif_ouverture"],
        "departs": [{"date_effet": depart["date_effet"], "motif": depart["motif"]}
                    for depart in actuel["departs"]],
    }


def scenario_actuel_des_donnees(donnees: dict) -> dict:
    """Le scénario 1 que le portage a servi (:func:`scenario_actuel`), sous
    les types que le Python lui donne : la date du départ et l'année de la
    réversion en entiers, qui doivent en être ; le coefficient et les montants
    en flottants ; le résultat du scénario par :func:`actuel_des_donnees`."""
    reversion = donnees["reversion"]
    return {
        "annee_liquidation": _entier(donnees["annee_liquidation"], "annee_liquidation"),
        "mois_liquidation": _entier(donnees["mois_liquidation"], "mois_liquidation"),
        "coefficient_euros_constants": _flottant(donnees["coefficient_euros_constants"]),
        "actuel": actuel_des_donnees(donnees["actuel"]),
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
    (``code``, ``montant``, la part de chaque régime, ``par_regime``, celle
    que la réversion reprend, ``par_regime_sans_anticipation``, et les étapes
    de la majoration, ``a_charge``) ; la
    durée validée, le taux, l'ouverture et son motif. À côté : la date du
    départ, le passage aux euros constants, et la réversion, ``None`` sans
    elle (son ``annee``, et chacun de ses ``regimes`` : ``regime``,
    ``montant``, ``date_effet``). Puis, sous leur clé, les motifs des
    requêtes que le portage refuse."""
    reponse = _demander({"scenario_actuel": {"cas": cas}}, paquet)
    return ({cle: scenario_actuel_des_donnees(lu) for cle, lu in reponse["resultats"].items()},
            reponse["echecs"])


@dataclasses.dataclass(frozen=True)
class Moteur:
    """Le moteur du scénario 1, ``simulateur.scenario_actuel``, en argument
    d'un appel du droit (:func:`droit`) : :data:`MOTEUR`, une copie dont des
    tables lisent ce que d'autres lisent (:meth:`pretant`), ou l'une de ses
    variantes que la mesure des avantages non contributifs liquide
    (:meth:`neutralisant`)."""

    #: Chaque table prêtée, ``(table, preteuse)``, sous les noms du Python.
    prets: tuple[tuple[str, str], ...] = ()
    #: L'avantage que la mesure retire de ce moteur, ou ``None``.
    neutralise: str | None = None
    #: Le barème de l'ASPA d'un autre modèle, ``(seule, couple)``, ou ``None``.
    bareme_aspa: tuple[float, float] | None = None

    def pretant(self, table: str, preteuse: str) -> Moteur:
        """Ce moteur, sa table ``table`` lisant ce que lit ``preteuse`` — celle
        des indépendants, celle du régime général —, comme un test la prête au
        moteur Python (``monkeypatch.setattr``) : le portage la prête à une
        copie du sien, que les autres appels ne voient pas."""
        return dataclasses.replace(self, prets=(*self.prets, (table, preteuse)))

    def neutralisant(self, code: str) -> Moteur:
        """Ce moteur, l'avantage ``code`` retiré comme la mesure des avantages
        non contributifs le retire (``avantages.scenarios_neutralises``) : le
        portage prend sa variante (``scenariosNeutralises`` de ``pont.mjs``),
        bâtie des leviers de ``moteur/js/regimes.js`` (action 161, étape 6)."""
        return dataclasses.replace(self, neutralise=code)

    def au_bareme_de_l_aspa(self, seule: float, couple: float) -> Moteur:
        """Ce moteur, le minimum vieillesse au barème d'un autre modèle — le
        plafond d'une personne seule et celui d'un couple, chaque année, sans
        les deux étages d'avant 2007 —, comme un test le prête au moteur
        Python : le portage le prête à une copie du sien (``tests/test_ines.py``)."""
        return dataclasses.replace(self, bareme_aspa=(seule, couple))

    def __repr__(self) -> str:
        return ("pont.MOTEUR"
                + ("" if self.neutralise is None else f".neutralisant({self.neutralise!r})")
                + "".join(f".pretant({table!r}, {preteuse!r})"
                          for table, preteuse in self.prets)
                + ("" if self.bareme_aspa is None
                   else f".au_bareme_de_l_aspa{self.bareme_aspa!r}"))


#: Le moteur du scénario 1 en argument d'un appel du droit : le portage y met
#: le sien (``simulateur.scenarioActuel``).
MOTEUR = Moteur()


class _Simulateur:
    """Le simulateur, en argument d'un appel du droit (:func:`droit`)."""

    def __repr__(self) -> str:
        return "pont.SIMULATEUR"


#: Le simulateur en argument d'un appel du droit — celui qui bâtit une
#: carrière (``simulateur.carriere_simple``) : le portage y met le sien, sous
#: les paramètres de la demande.
SIMULATEUR = _Simulateur()


@dataclasses.dataclass(frozen=True)
class CarriereSimple:
    """La carrière que ``simulateur.carriere_simple`` bâtit de ces options, en
    argument d'un appel du droit (:func:`droit`) : le portage la bâtit
    lui-même, sans qu'elle passe le pont, et le jumeau Python de même. Une
    recherche qui essaie des carrières n'en fait passer que les résultats.
    ``depart``, un âge, porte la carrière bâtie à ce départ, ses lignes
    gardées, comme ``dataclasses.replace(carriere, age_liquidation=…)`` : un
    balayage des départs ne bâtit qu'une fois chaque carrière."""

    options: dict
    depart: float | None = None


@dataclasses.dataclass(frozen=True)
class DureesDuReleve:
    """Les durées du relevé de cette carrière (``releve.construire``), en
    argument d'une règle de la façade : elles ne passent pas le pont, et le
    portage les refait du relevé de la carrière, sur le moteur de la demande
    (``durees_du_releve``, ``argumentDuDroit`` de ``pont.mjs``)."""

    carriere: object


@dataclasses.dataclass(frozen=True)
class DroitsDuReleve:
    """Les droits du relevé de cette carrière (``releve.construire``), en
    argument d'une règle de la façade : comme ses durées
    (:class:`DureesDuReleve`), le portage les refait du relevé de la
    carrière, sur le moteur de la demande (``droits_du_releve``)."""

    carriere: object


@dataclasses.dataclass(frozen=True)
class LigneDeCarriere:
    """La ligne de ce rang d'une carrière (``carriere.lignes[rang]``), en
    argument d'une règle de la façade : le portage la relit dans la carrière
    qu'il reçoit (``ligne``, ``argumentDuDroit`` de ``pont.mjs``)."""

    carriere: object
    rang: int


@dataclasses.dataclass(frozen=True)
class ContexteDuMoteur:
    """Le contexte d'une liquidation sur le moteur de la demande, par ses
    neutralisations, en argument d'une règle de la façade : le portage en
    refait un, sur son moteur (``argumentDeLaFacade`` de ``pont.mjs``)."""

    neutralisations: tuple[str, ...]


@dataclasses.dataclass(frozen=True)
class Periode:
    """La période d'un régime à une année, ``catalogue[code].periode(annee)``,
    en argument d'un appel du droit (:func:`droit`) : le portage y met la
    sienne."""

    code: str
    annee: int


def carriere_relue(donnees: dict) -> dict:
    """La carrière qu'un moteur a bâtie, en données (``carriereEnDonnees`` de
    ``pont.mjs``, :func:`carriere_en_donnees`), relue sous les types du Python
    (:func:`carriere_des_donnees`) puis réécrite en données : ce que les deux
    moteurs en ont fait se compare champ par champ, et
    :func:`carriere_des_donnees` en refait la carrière."""
    return carriere_en_donnees(carriere_des_donnees(donnees))


#: Les champs de la prestation du RAFP (``PrestationRafp`` de
#: ``droit/liquider.py``), et ceux qui sont des entiers.
CHAMPS_DE_LA_PRESTATION_RAFP = ("forme", "capital", "conversion", "premiere_fraction",
                                "mois_du_solde", "seuil_du_fractionnement")
ENTIERS_DE_LA_PRESTATION_RAFP = frozenset({"mois_du_solde", "seuil_du_fractionnement"})


def prestation_rafp_des_donnees(prestation: dict) -> dict:
    """La prestation du RAFP que le portage a écrite (``prestationRafp``), sous
    les champs et les types du Python (``PrestationRafp``) : sa forme ; le
    capital, la conversion et la première fraction en flottants, les mois du
    solde et le seuil du fractionnement en entiers, chacun nul quand la forme
    ne le porte pas."""
    if set(prestation) != set(CHAMPS_DE_LA_PRESTATION_RAFP):
        raise ValueError(f"PrestationRafp : le portage écrit les champs {sorted(prestation)}")
    return {nom: (prestation[nom] if nom == "forme" or prestation[nom] is None
                  else _entier(prestation[nom], nom) if nom in ENTIERS_DE_LA_PRESTATION_RAFP
                  else _flottant(prestation[nom]))
            for nom in CHAMPS_DE_LA_PRESTATION_RAFP}


def periodes_des_donnees(periodes: list[dict]) -> list[dict]:
    """Les périodes d'un régime que le portage a écrites
    (``scenario_actuel.catalogue.periodes`` de ``FONCTIONS_DU_DROIT``), ce que
    les confrontations en lisent pour rejouer ses cotisations, sous les types
    que le Python leur donne : la première et la dernière année en entiers, la
    dernière nulle pour une période ouverte ; l'assiette telle quelle ; le taux
    de cotisation et la part du salarié en flottants."""
    return [{"debut": _entier(periode["debut"], "debut"),
             "fin": None if periode["fin"] is None else _entier(periode["fin"], "fin"),
             "assiette": periode["assiette"],
             "taux_cotisation_retraite": _flottant(periode["taux_cotisation_retraite"]),
             "part_salariale": _flottant(periode["part_salariale"])}
            for periode in periodes]


def reversion_des_donnees(reversion: dict | None):
    """La réversion que le portage a écrite (``Reversion`` de
    ``droit/reversion.js``, dont les champs portent les noms du Python), sous
    le dataclass du Python, chacun de ses régimes compris ; ``None`` sans
    réversion. Le module de la réversion ne se charge qu'à la lecture."""
    from .droit.reversion import Reversion

    return None if reversion is None else _depuis_donnees(Reversion, reversion)


def cumul_des_donnees(cumul: dict | None):
    """Le cumul que le portage a écrit (``Cumul`` de ``droit/cumul.js``, dont
    les champs portent les noms du Python), sous le dataclass du Python,
    chacune de ses tranches et ses mois compris ; ``None`` sans activité
    après le départ. Le module du cumul ne se charge qu'à la lecture."""
    from .droit.cumul import Cumul

    return None if cumul is None else _depuis_donnees(Cumul, cumul)


def majorations_des_donnees(majorations: list[dict]) -> tuple:
    """Les majorations exceptionnelles que « faire vivre » sert, que le portage
    a écrites, sous le dataclass du Python (``MajorationExceptionnelle``) : leur
    montant à l'échéance, que le Python en dérive, ne passe pas. Le module de
    la revalorisation ne se charge qu'à la lecture."""
    from .revalorisation import MajorationExceptionnelle

    return tuple(_depuis_donnees(MajorationExceptionnelle, majoration)
                 for majoration in majorations)


#: Ce que rend chaque fonction du droit que le pont fait appeler
#: (``FONCTIONS_DU_DROIT`` de ``pont.mjs``), sous le type que son jumeau
#: Python lui donne, ou relu par une fonction : JSON n'écrit ni n-uplet, ni
#: énumération, ni « 2.0 ». Une fonction qui n'y est pas est refusée avant
#: node, au lieu que le type de ce qu'elle rend se devine.
LECTURES_DU_DROIT = {
    "ouvrir.age_annulation_droit": float,
    "ouvrir.age_ouverture": float,
    "ouvrir.age_ouverture_droit": float,
    "ouvrir.duree_requise": tuple[int, Fiabilite | None],
    "periode.capital_seuil_points": float | None,
    "liquider.duree_proratisation": tuple[int, Fiabilite | None],
    "liquider.annuites_au_taux_de_leur_annee": float,
    "liquider.majoration_rafp": float,
    "liquider.mois_apres_le_depart": int,
    "liquider.nombre_d_annees_retenues": int,
    "liquider.prestation_rafp": prestation_rafp_des_donnees,
    "liquider.decote_opposable": tuple[float | None, float, Fiabilite | None],
    "liquider.salaire_de_reference": float,
    "liquider.trimestres_de_decote": float,
    "liquider.valeur_du_point": tuple[float, Fiabilite] | None,
    "invalidite.exigences_du_handicap": tuple[float, int, int | None] | None,
    # La version de la retraite pour invalidité, puis la pension qu'elle sert,
    # enchaînées dans le portage : la version, une fiche du paquet, ne passe
    # pas le pont ; aucune pension sans elle.
    "invalidite.retraite_pour_invalidite.pension_du_fonctionnaire_invalide":
        tuple[float, str] | None,
    # Le cumul de l'activité après le départ : sous les pensions prêtées,
    # ``{regime: montant}``, chaque année, sans majoration pour enfants, sur le
    # scénario 1 de la carrière liquidée, que le portage refait (ses
    # arguments : le moteur, la carrière, la carrière liquidée, les pensions,
    # l'année courante) ; ou tel que l'échéancier le calcule.
    "cumul.cumuler.pensions_pretees": cumul_des_donnees,
    "echeancier.parcourir.au_depart.cumul": cumul_des_donnees,
    # Ce que lisent les exemples de quatre étapes, sur le simulateur ou le
    # moteur de la demande : le minimum vieillesse du foyer ; les majorations
    # exceptionnelles que « faire vivre » sert, sur le scénario 1 que le
    # portage refait ; les lignes de retraite de la fiche de paie d'un revenu,
    # ``(code, part du salarié)``, aucune sans fiche ; la cotisation de
    # l'année de chaque régime, sous les paramètres de la demande.
    "foyer.foyer_et_net.minimum_vieillesse": float,
    "revalorisation.faire_vivre.majorations": majorations_des_donnees,
    "remuneration.fiche_depuis_brut.lignes_de_retraite": tuple[tuple[str, float], ...] | None,
    "compte.cotisation_annuelle.par_regime": tuple[tuple[str, float], ...],
    "calendrier.en_mois": int,
    "calendrier.origine_des_ages": DateMois,
    "carriere.date_de_l_age": DateMois,
    "departs.age_legal": float,
    "chronologie.valeur": int,
    "regimes.BORNES_ASSIETTE": dict[str, tuple[float, float | None]],
    # Le relevé des droits (``releve.construire``), par ce que les exemples en
    # lisent : les points de chaque régime, chaque année, et leur taux ; la
    # fiche et les services de chaque emploi classé ; les services
    # liquidables de régimes nommés.
    "releve.construire.droits.points": tuple[tuple[str, int, float, float | None], ...],
    "releve.construire.durees.emplois": tuple[tuple[str, int], ...],
    "releve.construire.durees.services_liquidables": int,
    # Chaque ligne du relevé (contrat C.5), par ce que le tableau de bord en
    # compte : son identifiant, la fiche qu'elle cite et sa version, ``None``
    # sans elles.
    "releve.construire.lignes.citations": tuple[tuple[str, str | None, str | None], ...],
    # La réversion que des pensions ouvrent, et celle que l'échéancier liquide
    # au décès de l'assuré ; le plafond de chaque nouvelle pension que
    # l'activité après le départ constitue, ``(regime, plafond)``, aucune
    # sans activité.
    "reversion.reversion": reversion_des_donnees,
    "echeancier.parcourir.reversion": reversion_des_donnees,
    "echeancier.parcourir.au_depart.droits_apres_depart.pensions":
        tuple[tuple[str, float | None], ...] | None,
    "scenario_actuel.ages_annulation_decote.age": tuple[float, Fiabilite] | None,
    # L'âge légal de droit commun d'une génération, que le coût des avantages
    # oppose à ses départs (``avantages.ages_legaux``).
    "scenario_actuel.ages_ouverture.age": tuple[float, Fiabilite] | None,
    "scenario_actuel.calculer": actuel_des_donnees,
    "scenario_actuel.catalogue.etage": str,
    "scenario_actuel.catalogue.periodes": periodes_des_donnees,
    "scenario_actuel.macro.plafond_securite_sociale": float,
    "scenario_actuel.minimum_garanti.montant": tuple[float, Fiabilite] | None,
    "scenario_actuel.valeurs_point.achat": tuple[float, float, Fiabilite] | None,
    "scenario_actuel.valeurs_point.service": tuple[float, Fiabilite] | None,
    "simulateur.carriere_releve": carriere_relue,
    "simulateur.carriere_simple": carriere_relue,
}


#: Les champs du régime unique que la fusion rend (``RegimeFusionne``), et le
#: type de chacun.
CHAMPS_DE_LA_FUSION = {
    "annee_bascule": int, "age_ouverture": float, "age_taux_plein": float,
    "duree_requise_trimestres": int, "salaire_reference": str, "assiette": str,
    "taux_cotisation_retraite": float, "taux_cotisation_salarie": float,
}


def fusion_des_donnees(fusionne: dict) -> dict:
    """Le régime unique que la fusion rend, par ses champs
    (:data:`CHAMPS_DE_LA_FUSION`), chacun sous son type, et d'où vient chaque
    paramètre (``origines``)."""
    return {**{champ: _depuis_donnees(type_, fusionne[champ])
               for champ, type_ in CHAMPS_DE_LA_FUSION.items()},
            "origines": dict(fusionne["origines"])}


def _fiche_des_donnees(fiche: dict) -> dict[str, float]:
    return {champ: _flottant(fiche[champ])
            for champ in ("brut", "net", "retraite_salarie", "retraite_employeur")}


def simulation_des_donnees(simulation: dict) -> dict:
    """La simulation d'une carrière telle que les sondes de la prose la
    lisent : son résultat (``Comparaison.dictionnaire()``), relu sous la table
    des types (:func:`resultat_des_donnees`) ; le diviseur de chaque scénario
    notionnel ; et la fiche de paie de l'année de référence — le gain net, la
    fiche sous le droit en vigueur et sous la proposition, l'indemnité
    compensatrice de la CSG par mois —, ``None`` pour qui ne cotise plus."""
    remuneration = simulation["remuneration"]
    return {
        "resultat": resultat_des_donnees(simulation["resultat"]),
        "diviseurs": _par_scenario(simulation["diviseurs"]),
        "remuneration": None if remuneration is None else {
            "annee": _entier(remuneration["annee"], "remuneration.annee"),
            "gain_net": _flottant(remuneration["gain_net"]),
            "droit_en_vigueur": _fiche_des_donnees(remuneration["droit_en_vigueur"]),
            "proposition": _fiche_des_donnees(remuneration["proposition"]),
            "indemnite_csg_mensuelle": _flottant(remuneration["indemnite_csg_mensuelle"]),
        },
    }


def pilier_des_donnees(pilier: dict) -> dict:
    """Le pilier capitalisé d'une suite d'assiettes, par ce que les sondes en
    lisent : son capital, sa rente mensuelle, ses années de versement."""
    return {"capital": _flottant(pilier["capital"]),
            "rente_mensuelle": _flottant(pilier["rente_mensuelle"]),
            "annees_cotisees": _entier(pilier["annees_cotisees"], "annees_cotisees")}


#: Ce que rendent les règles que les sondes de la prose et les mesures de
#: l'accueil appelaient une à une au moteur Python (``scripts/mesures_prose.py``,
#: ``scripts/solde_fusion.py`` ; action 161, lot A), sur le simulateur de la
#: demande : elles s'ajoutent aux lectures du droit (``FONCTIONS_DES_SONDES``
#: de ``pont.mjs``).
LECTURES_DES_SONDES = {
    "age_reference.age": float,
    "conversion.coefficient.esperance_residuelle": float,
    "conversion.coefficient.diviseur": float,
    "conversion.effet_anticipation": float,
    "indexation.coefficient": float,
    # Le taux d'une année, puis l'inflation, le salaire moyen, la productivité.
    "indexation.taux": tuple[float, float, float, float],
    "capitalisation.facteur_encours_rente": float,
    "carriere.ancrage_salaire_moyen": tuple[int, float],
    "carriere.salaire_moyen_annuel": float,
    "restitution.part_du_poste": float,
    "restitution.annuelle.points_csg": float,
    # La part du taux de l'État portée au compte : le civil, le militaire, et
    # le militaire rapporté au taux civil.
    "compte.parts_retraite_seule": tuple[float, float, float],
    "fusion.fusionner": fusion_des_donnees,
    "fusion.taux_total.tranche_1": float,
    "simulateur.simuler": simulation_des_donnees,
    # La garantie vieillesse servie à une pension : son plancher, son complément.
    "notionnel.garantie_vieillesse": _par_scenario,
    "capitalisation.construire": pilier_des_donnees,
}
LECTURES_DU_DROIT.update(LECTURES_DES_SONDES)


#: La règle que l'étude de la mortalité appelait au moteur Python
#: (``scripts/mortalite_population.py`` ; action 161), sur le simulateur de la
#: demande et une carrière passée en données : le niveau de salaire de cette
#: carrière, en multiples du salaire moyen, qui la range dans un vingtile de
#: niveau de vie (``FONCTIONS_DE_LA_MORTALITE`` de ``pont.mjs``).
LECTURES_DE_LA_MORTALITE = {
    "conversion.niveau_relatif": float,
}
LECTURES_DU_DROIT.update(LECTURES_DE_LA_MORTALITE)


def _argument_du_droit(argument, carrieres: list) -> dict:
    """Un argument d'un appel du droit tel que ``pont.mjs`` le relit : le
    moteur du scénario 1 et les tables qu'on lui prête, la période d'un
    régime, une carrière — passée une fois en données, puis par son rang —, ou
    une valeur."""
    from .carriere import Carriere

    if isinstance(argument, Moteur):
        return {"moteur": "scenario_actuel", "prets": [list(pret) for pret in argument.prets],
                **({} if argument.neutralise is None else {"neutralise": argument.neutralise}),
                **({} if argument.bareme_aspa is None
                   else {"bareme_aspa": list(argument.bareme_aspa)})}
    if argument is SIMULATEUR:
        return {"simulateur": "simulateur"}
    if isinstance(argument, CarriereSimple):
        return {"carriere_simple": _en_donnees(argument.options),
                **({} if argument.depart is None else {"depart": argument.depart})}
    if isinstance(argument, Periode):
        return {"periode": [argument.code, argument.annee]}
    if isinstance(argument, DureesDuReleve):
        return {"durees_du_releve": _argument_du_droit(argument.carriere, carrieres)["carriere"]}
    if isinstance(argument, DroitsDuReleve):
        return {"droits_du_releve": _argument_du_droit(argument.carriere, carrieres)["carriere"]}
    if isinstance(argument, LigneDeCarriere):
        return {"ligne": [_argument_du_droit(argument.carriere, carrieres)["carriere"],
                          argument.rang]}
    if isinstance(argument, Carriere):
        rang = next((rang for rang, connue in enumerate(carrieres) if connue is argument), None)
        if rang is None:
            carrieres.append(argument)
            rang = len(carrieres) - 1
        return {"carriere": rang}
    return {"valeur": _en_donnees(argument)}


def droit(appels: dict[str, tuple], parametres=None, paquet: bytes | None = None,
          ) -> tuple[dict[str, object], dict[str, str]]:
    """Chaque appel d'une fonction du droit que le portage porte, sous sa clé,
    ``(fonction, *arguments)`` — ``fonction`` au nom de son jumeau Python,
    ``"ouvrir.duree_requise"`` ; ses arguments dans l'ordre du jumeau,
    :data:`MOTEUR` pour le moteur du scénario 1 — ou ``MOTEUR.pretant(…)``,
    une table prêtée par une autre (:meth:`Moteur.pretant`) —, :class:`Periode`
    pour la période d'un régime, une carrière que le Python a bâtie, passée en données
    (:func:`carriere_en_donnees`), une valeur telle quelle — sous
    ``parametres``, ceux du simulateur, les réglages de référence sans eux :
    sous sa clé, ce que la fonction rend, relu sous le type de son jumeau
    (:data:`LECTURES_DU_DROIT`). Puis, sous leur clé, les motifs des appels
    que le portage refuse. Les exemples d'OpenFisca et des caisses
    (``tests/test_oracle.py``) éprouvent ainsi le droit fonction par
    fonction."""
    from .config import Parametres

    inconnues = sorted({fonction for fonction, *_ in appels.values()} - set(LECTURES_DU_DROIT))
    if inconnues:
        raise ValueError(f"fonctions du droit que le pont ne relit pas : {', '.join(inconnues)} "
                         "(pont.LECTURES_DU_DROIT)")
    carrieres: list = []
    demandes = [{"cle": cle, "fonction": fonction,
                 "arguments": [_argument_du_droit(argument, carrieres) for argument in arguments]}
                for cle, (fonction, *arguments) in appels.items()]
    reponse = _demander({"droit": {
        "parametres": parametres_en_donnees(Parametres() if parametres is None else parametres),
        "carrieres": [carriere_en_donnees(carriere) for carriere in carrieres],
        "appels": demandes,
    }}, _paquet_de(parametres, paquet))
    return ({cle: relu_du_droit(appels[cle][0], lu) for cle, lu in reponse["resultats"].items()},
            reponse["echecs"])


def relu_du_droit(fonction: str, valeur):
    """Ce que rend une fonction du droit, écrit en données, relu sous le type
    que son jumeau Python lui donne (:data:`LECTURES_DU_DROIT`) : ce que le
    portage a rendu, ou ce que le jumeau rend lui-même, pour les confronter —
    un flottant entier que le jumeau rend « 2 » s'y relit « 2.0 », comme le zéro
    d'une somme vide dans les témoins."""
    lecture = LECTURES_DU_DROIT[fonction]
    return (lecture(valeur) if isinstance(lecture, types.FunctionType)
            else _depuis_donnees(lecture, valeur))



def cout_garantie_des_donnees(cout: dict):
    """Le coût d'un plancher que le portage a écrit, sous le type du coût :
    il ne se charge qu'à la lecture."""
    from .cout import CoutGarantie

    return _depuis_donnees(CoutGarantie, cout)


#: Ce que rend chaque fonction de la garantie d'une population que le pont
#: fait appeler (``FONCTIONS_DE_LA_GARANTIE`` de ``pont.mjs``), sous le type
#: que le Python lui donne. Une fonction qui n'y est pas est refusée avant
#: node.
LECTURES_DE_LA_GARANTIE = {
    "cout_garantie": cout_garantie_des_donnees,
    "cout_garantie_par_sexe": cout_garantie_des_donnees,
    "facteurs_par_sexe": tuple[float, float],
    "manque_moyen": tuple[float, float],
    "pension_moyenne": float,
}


def garantie(appels: list[tuple]) -> list:
    """Chaque appel d'une fonction de la garantie d'une population, que le
    portage seul porte (``moteur/js/garantie.js``, note de décision 0007) :
    ``(fonction, *arguments)``, ses arguments dans l'ordre du portage —
    ``("cout_garantie", distribution, effectif, plancher, facteur, part du
    plancher retirée en entier, taux de retrait)``,
    ``("cout_garantie_par_sexe", femmes, hommes, part des femmes, effectif,
    plancher, facteur, rapport, plancher majoré, part de qui vit seul, les
    deux nombres de la forme)``, ``("manque_moyen", borne inférieure, borne
    supérieure, plancher, les deux nombres de la forme)``,
    ``("facteurs_par_sexe", moyenne des femmes, moyenne des hommes, part des
    femmes, facteur, rapport)``, ``("pension_moyenne", distribution)``. Une
    distribution — tout ce qui porte des ``tranches`` — passe une fois, en
    données. Le lot part d'une seule demande, et ce que chaque fonction rend
    revient dans l'ordre des appels, sous le type du Python
    (:data:`LECTURES_DE_LA_GARANTIE`).

    Un appel que le barème refuse arrête le lot : son motif, celui du portage,
    lève ``ValueError``. Le barème ne lit que ses arguments : la demande se
    passe du paquet, et va au pont gardé ouvert, sur les données du dépôt
    comme sur des données d'ailleurs."""
    inconnues = sorted({fonction for fonction, *_ in appels} - set(LECTURES_DE_LA_GARANTIE))
    if inconnues:
        raise ValueError(f"fonctions de la garantie que le pont ne relit pas : "
                         f"{', '.join(inconnues)} (pont.LECTURES_DE_LA_GARANTIE)")
    if not appels:
        return []
    distributions: list = []

    def en_donnees(argument) -> dict:
        if not hasattr(argument, "tranches"):
            return {"valeur": _en_donnees(argument)}
        rang = next((rang for rang, connue in enumerate(distributions) if connue is argument),
                    None)
        if rang is None:
            distributions.append(argument)
            rang = len(distributions) - 1
        return {"distribution": rang}

    demandes = [{"cle": str(rang), "fonction": fonction,
                 "arguments": [en_donnees(argument) for argument in arguments]}
                for rang, (fonction, *arguments) in enumerate(appels)]
    reponse = _demander({"garantie": {
        "distributions": [[[tranche.borne_inferieure, tranche.borne_superieure, tranche.part]
                           for tranche in distribution.tranches]
                          for distribution in distributions],
        "appels": demandes,
    }}, None)
    for motif in reponse["echecs"].values():
        raise ValueError(motif)
    lus = reponse["resultats"]
    return [_lu_de_la_garantie(fonction, lus[str(rang)])
            for rang, (fonction, *_) in enumerate(appels)]


def _lu_de_la_garantie(fonction: str, valeur):
    lecture = LECTURES_DE_LA_GARANTIE[fonction]
    return (lecture(valeur) if isinstance(lecture, types.FunctionType)
            else _depuis_donnees(lecture, valeur))


# -- l'impôt sur le revenu (action 161, note de décision 0007) ----------------


@dataclasses.dataclass(frozen=True)
class ImpotDemande:
    """Ce que :func:`impot` relit de l'impôt d'un foyer : son montant, dans la
    monnaie de l'année, et s'il est mis en recouvrement."""

    impot: float
    mis_en_recouvrement: bool


def impot(appels: list[tuple], parametres=None, paquet: bytes | None = None, *,
          derniere: int = 2070, indexation: str = "prix") -> list[ImpotDemande | None]:
    """L'impôt sur le revenu de chaque ``(année des revenus, foyer)``, que le
    portage seul calcule pour le coût (``moteur/js/impot-revenu.js``, note de
    décision 0007). Un foyer passe en données, sous les noms du portage :
    ``{"declarants": [{"pensions": 30000.0, "age": 70}]}``, et ce qu'il ne dit
    pas vaut ce que ``Foyer`` et ``Declarant`` présument. Les revenus sont dans
    la monnaie de l'année, l'impôt aussi.

    Le barème de l'année est lu au paquet jusqu'à la dernière loi de finances,
    projeté ensuite jusqu'à ``derniere`` par ``indexation`` — ``"prix"`` ou
    ``"salaire_moyen"`` —, sur le scénario de projection de ``parametres``,
    ceux du simulateur, les réglages de référence sans eux. Le lot part d'une
    seule demande, et les impôts reviennent dans l'ordre des appels ; ``None``
    pour une année sans barème, avant le premier lu ou après ``derniere``. Un
    foyer que l'impôt refuse arrête le lot : son motif, celui du portage, lève
    ``ValueError``."""
    from .config import Parametres

    if not appels:
        return []
    reponse = _demander({"impot": {
        "parametres": parametres_en_donnees(Parametres() if parametres is None else parametres),
        "derniere": derniere,
        "indexation": indexation,
        "appels": [{"cle": str(rang), "annee": annee, "foyer": _en_donnees(foyer)}
                   for rang, (annee, foyer) in enumerate(appels)],
    }}, _paquet_de(parametres, paquet))
    for motif in reponse["echecs"].values():
        raise ValueError(motif)
    lus = reponse["resultats"]
    return [None if lu is None else ImpotDemande(
                impot=_flottant(lu["impot"]), mis_en_recouvrement=lu["mis_en_recouvrement"])
            for lu in (lus[str(rang)] for rang in range(len(appels)))]


# -- la revalorisation servie et l'indexation (action 161, note de décision 0007) --


@dataclasses.dataclass(frozen=True)
class SeriesServies:
    """Ce que :func:`series_servies` relit de la revalorisation servie d'un
    jeu de paramètres : l'index du compte et, sous son régime, la valeur de
    service convenue, en euros constants, de la première année à la dernière ;
    et, de chaque régime du catalogue, celui qui sert ses points au bout de
    ses fusions, s'il a une valeur de service convenue."""

    premiere_annee: int
    derniere_annee: int
    index: dict[int, float]
    points: dict[str, dict[int, float]]
    convenus: dict[str, str | None]


def _regime_lu(valeur) -> str | None:
    if valeur is not None and not isinstance(valeur, str):
        raise TypeError(f"un régime, ou rien, attendu : {valeur!r}")
    return valeur


#: Ce que rend chaque lecture de la revalorisation servie que le pont fait
#: appeler (``LECTURES_DE_LA_REVALORISATION_SERVIE`` de ``pont.mjs``) : celles
#: que la classe Python garde, sous son type. Une lecture qui n'y est pas est
#: refusée avant node.
LECTURES_DE_LA_REVALORISATION_SERVIE = {
    "coefficient": _flottant,
    "coefficient_stock": _flottant,
    "coefficient_points": _flottant,
    "regime_convenu": _regime_lu,
}


def _taux_lu(lu: dict):
    """Le taux d'une année que le portage a écrit, sous le type du Python."""
    from .donnees.chargement import Fiabilite
    from .moteur.indexation import TauxIndexation

    return TauxIndexation(
        annee=_entier(lu["annee"], "annee"), taux=_flottant(lu["taux"]),
        terme_retenu=lu["terme_retenu"], inflation=_flottant(lu["inflation"]),
        salaire_moyen=_flottant(lu["salaire_moyen"]),
        productivite=_flottant(lu["productivite"]), fiabilite=Fiabilite(lu["fiabilite"]))


#: Ce que rend chaque lecture de l'indexation que le pont fait appeler
#: (``LECTURES_DE_L_INDEXATION`` de ``pont.mjs``).
LECTURES_DE_L_INDEXATION = {
    "taux": _taux_lu,
    "coefficient": _flottant,
}


def _lectures_du_portage(demande: str, corps: dict, appels: list[tuple], lectures: dict,
                         parametres, paquet: bytes | None) -> tuple[dict, list]:
    """La réponse du portage à ``demande``, et ce que rend chaque appel,
    ``(lecture, *arguments)``, dans l'ordre, relu sous son type. Une lecture
    que le pont ne relit pas est refusée avant node ; un appel que le portage
    refuse arrête le lot, de son motif."""
    from .config import Parametres

    inconnues = sorted({lecture for lecture, *_ in appels} - set(lectures))
    if inconnues:
        raise ValueError(f"lectures que le pont ne relit pas : {', '.join(inconnues)} "
                         f"(pont, {demande})")
    reponse = _demander({demande: {
        "parametres": parametres_en_donnees(Parametres() if parametres is None else parametres),
        **corps,
        "appels": [{"cle": str(rang), "methode": lecture, "arguments": _en_donnees(arguments)}
                   for rang, (lecture, *arguments) in enumerate(appels)],
    }}, _paquet_de(parametres, paquet))
    for motif in reponse["echecs"].values():
        raise ValueError(motif)
    lus = reponse["resultats"]
    return reponse, [lectures[lecture](lus[str(rang)])
                     for rang, (lecture, *_) in enumerate(appels)]


def series_servies(parametres, premiere_annee: int, derniere_annee: int,
                   paquet: bytes | None = None) -> SeriesServies:
    """Les séries de la revalorisation servie sous ``parametres``, ceux du
    simulateur, de ``premiere_annee`` à ``derniere_annee``, que le portage
    seul calcule (``RevalorisationServie`` de ``moteur/js/revalorisation.js``,
    note de décision 0007) : une demande par jeu de paramètres, que la classe
    Python du même nom lit ensuite, coefficient par coefficient, sans rien
    redemander."""
    reponse, _ = _lectures_du_portage(
        "revalorisation_servie",
        {"premiere": premiere_annee, "derniere": derniere_annee, "series": True},
        [], LECTURES_DE_LA_REVALORISATION_SERVIE, parametres, paquet)
    series = reponse["series"]
    premiere = _entier(series["premiere"], "premiere")

    def serie(valeurs: list) -> dict[int, float]:
        return {premiere + rang: _flottant(valeur) for rang, valeur in enumerate(valeurs)}

    return SeriesServies(
        premiere_annee=premiere, derniere_annee=_entier(series["derniere"], "derniere"),
        index=serie(series["index"]),
        points={regime: serie(valeurs) for regime, valeurs in series["points"].items()},
        convenus={regime: _regime_lu(convenu)
                  for regime, convenu in series["convenus"].items()})


def revalorisation_servie(appels: list[tuple], parametres, premiere_annee: int,
                          derniere_annee: int, paquet: bytes | None = None) -> list:
    """Chaque appel d'une lecture de la revalorisation servie du portage,
    bâtie sous ``parametres`` de ``premiere_annee`` à ``derniere_annee`` :
    ``("coefficient", année de liquidation, année)``, ``("coefficient_stock",
    année de liquidation, année, réforme prospective ?)``,
    ``("coefficient_points", régime, année de liquidation, année)``,
    ``("regime_convenu", régime)``. Ce sont les lectures que la classe Python
    garde : leur confrontation les demande ainsi au portage lui-même. Le lot
    part d'une seule demande, et revient dans l'ordre des appels."""
    if not appels:
        return []
    return _lectures_du_portage(
        "revalorisation_servie",
        {"premiere": premiere_annee, "derniere": derniere_annee, "series": False},
        appels, LECTURES_DE_LA_REVALORISATION_SERVIE, parametres, paquet)[1]


def indexation(appels: list[tuple], parametres=None, paquet: bytes | None = None) -> list:
    """Chaque appel d'une lecture de l'indexation, que le portage seul calcule
    pour le coût (``moteur/js/indexation.js``, note de décision 0007), sous
    ``parametres``, ceux du simulateur, les réglages de référence sans eux :
    ``("taux", année)``, le taux retenu et le terme qui l'emporte
    (``TauxIndexation``) ; ``("coefficient", année de départ, année
    d'arrivée)``, le rendement cumulé d'une cotisation, revalorisée de l'année
    qui suit son versement à celle de l'arrivée comprise. Le lot part d'une
    seule demande, et revient dans l'ordre des appels."""
    if not appels:
        return []
    return _lectures_du_portage("indexation", {}, appels, LECTURES_DE_L_INDEXATION,
                                parametres, paquet)[1]


# -- la fin de la revalorisation servie et de l'indexation ------------------------


# -- la fiche de paie (action 161, étape 6e) --------------------------------------

@dataclasses.dataclass(frozen=True)
class LigneLue:
    """Une ligne de la fiche que le portage rend : son poste, ce qu'en versent
    l'assuré et l'employeur, en euros de l'année, et si elle est de la retraite."""
    code: str
    salarie: float
    employeur: float
    retraite: bool


@dataclasses.dataclass(frozen=True)
class FicheLue:
    """Une fiche de paie annuelle que le portage rend (``FicheDePaie`` de
    ``moteur/js/remuneration.js``) : ses montants, ses lignes, et ce que la
    retraite en prélève de chaque côté, sommé comme le jumeau le somme."""
    brut: float
    net: float
    cout_du_travail: float
    reduction_generale: float
    lignes: tuple[LigneLue, ...]

    @property
    def retraite_salarie(self) -> float:
        from .somme import somme_ordonnee

        return somme_ordonnee(ligne.salarie for ligne in self.lignes if ligne.retraite)

    @property
    def retraite_employeur(self) -> float:
        from .somme import somme_ordonnee

        return somme_ordonnee(ligne.employeur for ligne in self.lignes if ligne.retraite)


def _fiche_lue(lue: dict) -> FicheLue:
    return FicheLue(
        brut=_flottant(lue["brut"]), net=_flottant(lue["net"]),
        cout_du_travail=_flottant(lue["cout_du_travail"]),
        reduction_generale=_flottant(lue["reduction_generale"]),
        lignes=tuple(LigneLue(ligne["code"], _flottant(ligne["salarie"]),
                              _flottant(ligne["employeur"]), bool(ligne["retraite"]))
                     for ligne in lue["lignes"]))


def _taux_du_bloc_lus(lus: dict) -> dict[str, tuple[float, ...]]:
    return {cote: tuple(_flottant(taux) for taux in lus[cote]) for cote in ("salarie", "employeur")}


#: Ce que rendent les lectures de la fiche de paie (``LECTURES_DE_LA_FICHE`` de
#: ``pont.mjs``) : ``("fiche", brut, bloc, cadre)``, une :class:`FicheLue` ;
#: ``("brut_a_cout_donne", coût, bloc, cadre)``, le brut qui épuise ce coût du
#: travail ; ``("taux_du_bloc", bloc)``, les taux de chaque tranche de chaque
#: étage, ``{"salarie": …, "employeur": …}``. Le bloc se nomme en données :
#: ``"droit_en_vigueur"``, ou ``{"part_salariale": …,
#: "part_salariale_capitalisation": … ou None}`` pour la proposition.
LECTURES_DE_LA_FICHE = {
    "fiche": _fiche_lue,
    "brut_a_cout_donne": _flottant,
    "taux_du_bloc": _taux_du_bloc_lus,
}


def fiches_de_paie(statut: str, annee: int, appels: list[tuple], parametres=None,
                   profil: str = "salarie_prive", paquet: bytes | None = None,
                   ) -> tuple[dict[str, float], list]:
    """Les fiches de paie du profil ``profil`` sous le statut ``statut``, à
    ``annee``, que le portage seul bâtit (``ConstructeurFiche`` de
    ``moteur/js/remuneration.js``) sous ``parametres``, les réglages de
    référence sans eux : les repères de l'année, ``{"plafond": …, "smic": …}``,
    annuels, et ce que rend chaque appel (:data:`LECTURES_DE_LA_FICHE`), dans
    l'ordre. Le lot part d'une seule demande."""
    reponse, lus = _lectures_du_portage(
        "fiches_de_paie", {"profil": profil, "statut": statut, "annee": annee},
        appels, LECTURES_DE_LA_FICHE, parametres, paquet)
    reperes = {nom: _flottant(valeur) for nom, valeur in reponse["reperes"].items()}
    return reperes, lus


# -- la fin de la fiche de paie ---------------------------------------------------


# -- l'histoire du droit (action 161, note de décision 0007) ----------------------

#: Ce que rendent les règles du moteur que l'histoire du droit appelle
#: (``RevalorisationServie.coefficient_historique`` : ce que le droit a servi
#: aux pensions liquidées, que le coût seul lit, et qui reste en Python), sur
#: le moteur du scénario 1 (:data:`MOTEUR`) : le coefficient de l'article
#: L. 161-23-1 entre deux dates — ``depuis``, ``jusqu_a``, des dates ISO, la
#: revalorisation du jour du départ comprise ou non, le montant mensuel de
#: décembre 2019 qui choisit la tranche de 2020 — ; le produit des décrets de
#: la fonction publique, sous les mêmes arguments ; ce que devient un
#: traitement indiciaire d'une année à une autre, ``None`` hors de la série du
#: point ; le changement d'unité des points d'un régime entre l'année de leur
#: acquisition et celle de leur liquidation ; la dernière année dont la
#: valeur de service d'un point est publiée, au bout de ses fusions, ``None``
#: sans série (note de décision 0008). Elles s'ajoutent aux lectures du
#: droit (``FONCTIONS_DE_L_HISTOIRE_DU_DROIT`` de ``pont.mjs``) : le coût les
#: demande par lot (:func:`droit`), avec ``liquider.valeur_du_point``.
LECTURES_DE_L_HISTOIRE_DU_DROIT = {
    "scenario_actuel.revalorisations_pensions.generale": tuple[float, Fiabilite],
    "scenario_actuel.revalorisations_pensions.retenues.fonction_publique.produit":
        tuple[float, Fiabilite],
    "scenario_actuel.minimum_garanti.ratio_point_indice": float | None,
    "scenario_actuel.conversions_points.echelle": tuple[float, Fiabilite],
    "revalorisation.derniere_valeur_publiee": int | None,
}
LECTURES_DU_DROIT.update(LECTURES_DE_L_HISTOIRE_DU_DROIT)


# -- la fin de l'histoire du droit --------------------------------------------------


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


# -- la façade des tests (action 161, note de décision 0007) -------------------
#
# Les entrées du moteur Python que les tests appellent, servies par le portage
# sous leurs noms (``tests/facade.py``) : ce bloc en tient la demande
# (:func:`facade`) et la lecture (:func:`lu_strictement`), à part du reste du
# pont tant que le jumeau Python vit.

#: Les champs qu'un type du résultat porte et que le portage n'écrit pas quand
#: ils sont sans objet — la date d'effet d'une pension qui part avec les
#: autres, la part de chaque régime d'un avantage qui n'en a pas : le Python
#: les tient alors à leur valeur par défaut. Tout autre champ doit être écrit.
CHAMPS_SANS_OBJET = {
    "PensionRegime": frozenset({
        "date_effet", "montant_a_l_effet", "capital", "conjoint", "ecretement_du_maximum",
        "surcote", "coefficient_du_maximum", "sur_la_duree_maximum", "planchers",
        "avant_les_planchers"}),
    "AvantageApplique": frozenset({"par_regime", "par_regime_sans_anticipation", "a_charge"}),
    "ResultatActuel": frozenset({"minimum_ecrete"}),
}

#: Les types dont le portage écrit les champs en casse de chameau.
CLASSES_EN_CHAMEAU = frozenset({
    "EligibleAgricole", "RemunerationActif", "AnneeComparee", "FicheDePaie",
    "MajorationProportionnelle", "Foyer", "DepartParentTroisEnfants",
    "DerogationActive"})

#: Les champs que le portage écrit sous un autre nom que celui du Python, hors
#: de la casse de chameau : ``{type: {champ: nom du portage}}``.
NOMS_DU_PORTAGE = {
    "ExploitantAgricole": {"chef_reconstitue": "chefReconstitue"},
    "AnneeComparee": {"_smic": "smic"},
}

#: Ce que le portage tient sur un type et que le Python n'y porte pas : les
#: scénarios que la page énumère. La lecture le laisse.
HORS_DU_TYPE = {
    "Comparaison": frozenset({"scenarios"}),
    # La durée que la fraction d'avant 1998 proratise : une propriété du
    # Python, que le portage tient en champ.
    "DureesDesCultes": frozenset({"avant1998"}),
}

#: Le type des champs que le Python annonce ``object``, pour ne pas faire
#: dépendre un module d'un autre : ``{(type, champ): (module, nom)}``.
OBJETS_DU_RESULTAT = {
    ("ChefDExploitation", "eligible"): ("droit.liquider", "EligibleAgricole"),
    ("ExploitantAgricole", "eligible"): ("droit.liquider", "EligibleAgricole"),
    ("ExploitantAgricole", "carriere"): ("carriere", "Carriere"),
}

#: Les nombres que JSON n'écrit pas, et que le portage écrit par leur nom
#: (``telQuel`` de ``pont.mjs``).
NON_FINIS = {"NaN": math.nan, "Infinity": math.inf, "-Infinity": -math.inf}


def _en_chameau(nom: str) -> str:
    """Un nom du Python en casse de chameau (``enChameau`` de ``pont.mjs``)."""
    tete, *suite = nom.split("_")
    return tete + "".join(mot[:1].upper() + mot[1:] for mot in suite)


def _nom_du_portage(type_, champ: str) -> str:
    """Le nom sous lequel le portage écrit ce champ de ce type."""
    nom = NOMS_DU_PORTAGE.get(type_.__name__, {}).get(champ)
    if nom is not None:
        return nom
    return _en_chameau(champ) if type_.__name__ in CLASSES_EN_CHAMEAU else champ


def _type_du_champ(type_, champ: str):
    """Le type d'un champ : son annotation, ou, quand elle dit ``object``, le
    type déclaré dans :data:`OBJETS_DU_RESULTAT`."""
    import importlib

    declare = OBJETS_DU_RESULTAT.get((type_.__name__, champ))
    if declare is None:
        return _indices(type_)[champ]
    module, nom = declare
    return getattr(importlib.import_module(f"{__package__}.{module}"), nom)


#: Les champs d'un dataclass qu'un nombre de l'un ou l'autre type remplit, et
#: que JSON rend sous le sien : les trimestres d'une ligne de relevé, entiers
#: quand ils le sont (:data:`FLOTTANTS_DE_LA_CHRONOLOGIE`), ``None`` quand le
#: modèle les déduit du revenu.
NOMBRES_TELS_QUELS = frozenset({("LigneRelevee", "trimestres")})


def _nombre_tel_quel(valeur, chemin: str):
    if valeur is not None and type(valeur) not in (int, float):
        raise TypeError(f"{chemin} : nombre attendu, le portage a écrit {valeur!r}")
    return valeur


def _dataclass_lu(type_, valeur, chemin: str):
    """Un dataclass du résultat, de ce que le portage en a écrit : chacun de
    ses champs sous son type, celui qui est sans objet à son défaut
    (:data:`CHAMPS_SANS_OBJET`), et rien que le type ne porte — hors de ce que
    le Python calcule et que le portage tient en champ, une propriété, que le
    type refait."""
    if not isinstance(valeur, dict):
        raise TypeError(f"{chemin} : {type_.__name__} attendu, le portage a écrit {valeur!r}")
    champs = {_nom_du_portage(type_, champ.name): champ for champ in dataclasses.fields(type_)}
    hors_du_type = HORS_DU_TYPE.get(type_.__name__, frozenset())
    en_trop = sorted(nom for nom in valeur if nom not in champs and nom not in hors_du_type
                     and not isinstance(getattr(type_, nom, None), property))
    if en_trop:
        raise ValueError(f"{chemin} : {type_.__name__} : le portage écrit {', '.join(en_trop)}, "
                         "que le type ne porte pas")
    sans_objet = CHAMPS_SANS_OBJET.get(type_.__name__, frozenset())
    manquent = sorted(champ.name for nom, champ in champs.items()
                      if nom not in valeur and champ.name not in sans_objet)
    if manquent:
        raise ValueError(f"{chemin} : {type_.__name__} : le portage n'écrit pas "
                         f"{', '.join(manquent)}")
    return type_(**{champ.name: _nombre_tel_quel(valeur[nom], f"{chemin}.{champ.name}")
                    if (type_.__name__, champ.name) in NOMBRES_TELS_QUELS
                    else lu_strictement(_type_du_champ(type_, champ.name), valeur[nom],
                                        f"{chemin}.{champ.name}")
                    for nom, champ in champs.items() if nom in valeur})


def lu_strictement(type_, valeur, chemin: str = "valeur"):
    """Ce que le portage a écrit tel qu'il le tient (``telQuel`` de
    ``pont.mjs``), sous le type que le Python lui donne, sans rien deviner : un
    nombre où le type attend un nombre — « 2 » relu 2.0, un entier qui doit en
    être un, un nombre non fini par son nom —, un texte, un booléen, un membre
    d'énumération de sa valeur ; un dataclass de ses champs
    (:func:`_dataclass_lu`), une carrière et des paramètres par leur lecture
    (:func:`carriere_des_donnees`, :func:`parametres_des_donnees`) ; une suite
    en tuple ou en liste, un dictionnaire clé par clé, une année en entier.
    Ce qui n'a pas le type attendu, et un type que la lecture ne connaît pas,
    l'arrêtent."""
    from .carriere import Carriere
    from .config import Parametres
    from .journal import Journal

    origine = typing.get_origin(type_)
    if origine in (typing.Union, types.UnionType):
        membres = [membre for membre in typing.get_args(type_) if membre is not type(None)]
        if valeur is None and len(membres) < len(typing.get_args(type_)):
            return None
        if len(membres) != 1:
            raise TypeError(f"{chemin} : la lecture ne départage pas {type_}")
        return lu_strictement(membres[0], valeur, chemin)
    if type_ is float:
        if type(valeur) is str and valeur in NON_FINIS:
            return NON_FINIS[valeur]
        if type(valeur) not in (int, float):
            raise TypeError(f"{chemin} : nombre attendu, le portage a écrit {valeur!r}")
        return float(valeur)
    for simple, nom in ((int, "entier"), (bool, "booléen"), (str, "texte")):
        if type_ is simple:
            if type(valeur) is not simple:
                raise TypeError(f"{chemin} : {nom} attendu, le portage a écrit {valeur!r}")
            return valeur
    if isinstance(type_, type) and issubclass(type_, enum.Enum):
        try:
            return type_(valeur)
        except ValueError:
            raise ValueError(f"{chemin} : {type_.__name__} attendu, le portage a écrit "
                             f"{valeur!r}") from None
    if type_ is Carriere:
        return carriere_des_donnees(valeur)
    if type_ is Parametres:
        return parametres_des_donnees(valeur)
    if type_ is Journal:
        return journal_des_donnees(valeur, chemin)
    if dataclasses.is_dataclass(type_):
        return _dataclass_lu(type_, valeur, chemin)
    if type_ is dict:
        # Une donnée libre, que son contrat ne type pas — ce que vise un
        # événement : telle que JSON la rend, comme la chronologie.
        if not isinstance(valeur, dict):
            raise TypeError(f"{chemin} : dictionnaire attendu, le portage a écrit {valeur!r}")
        return valeur
    if origine is dict:
        type_des_cles, type_des_valeurs = typing.get_args(type_)
        if not isinstance(valeur, dict):
            raise TypeError(f"{chemin} : dictionnaire attendu, le portage a écrit {valeur!r}")
        return {_cle_lue(type_des_cles, cle, chemin):
                lu_strictement(type_des_valeurs, element, f"{chemin}[{cle}]")
                for cle, element in valeur.items()}
    if origine in (tuple, list):
        if not isinstance(valeur, list):
            raise TypeError(f"{chemin} : suite attendue, le portage a écrit {valeur!r}")
        arguments = typing.get_args(type_)
        if origine is list or (len(arguments) == 2 and arguments[1] is Ellipsis):
            arguments = (arguments[0],) * len(valeur)
        elif len(arguments) != len(valeur):
            raise ValueError(f"{chemin} : {len(arguments)} éléments attendus, le portage "
                             f"en a écrit {len(valeur)}")
        return origine(lu_strictement(sous_type, element, f"{chemin}[{rang}]")
                       for rang, (sous_type, element) in enumerate(zip(arguments, valeur)))
    if origine is frozenset:
        # Un ensemble, que le portage écrit en liste (``telQuel`` d'un ``Set``),
        # lu dans l'ordre de ses éléments.
        if not isinstance(valeur, list):
            raise TypeError(f"{chemin} : suite attendue, le portage a écrit {valeur!r}")
        (sous_type,) = typing.get_args(type_)
        return frozenset(sorted(lu_strictement(sous_type, element, f"{chemin}[{rang}]")
                                for rang, element in enumerate(valeur)))
    raise TypeError(f"{chemin} : la lecture ne connaît pas le type {type_!r}")


def _cle_lue(type_, cle: str, chemin: str):
    """La clé d'un dictionnaire, que JSON écrit en texte : telle quelle, ou
    l'entier qu'elle écrit — une année."""
    if type_ is str:
        return cle
    if type_ is int and cle.lstrip("-").isdigit():
        return int(cle)
    raise TypeError(f"{chemin} : clé {cle!r}, que la lecture ne sait pas rendre en {type_!r}")


class NonTransmissible(BaseException):
    """Ce qu'un test demande à la façade, elle ne sait pas le faire parvenir
    au portage, ou le portage ne sait pas le lui rendre. Elle ne dérive pas
    d'``Exception`` : un test qui attend une erreur du moteur
    (``pytest.raises(Exception)``) ne verdit pas de ce refus."""


class ContenuNonLu:
    """Le contenu d'une entrée du journal qui ne passe pas le pont
    (``CONTENUS_QUI_NE_PASSENT_PAS`` de ``pont.mjs``) : l'entrée se lit, ce
    qui la date aussi ; lire son contenu est refusé, au lieu qu'il manque
    sans bruit."""

    def __init__(self, sorte: str) -> None:
        self._sorte = sorte

    def _refuser(self, *_):
        raise NonTransmissible(
            f"le contenu d'une entrée « {self._sorte} » du journal ne passe pas le pont : "
            "le test le demande au pont du droit (pont.droit), ou se porte à la main")

    def __getattr__(self, nom):
        if nom.startswith("_"):
            raise AttributeError(nom)
        self._refuser()

    __getitem__ = __iter__ = __eq__ = __bool__ = _refuser
    __hash__ = None


#: Le type du contenu d'une entrée du journal, par sa sorte : ``(module,
#: nom)``, ou ``None`` pour une composante, une donnée de son contrat, dont
#: les montants sont des flottants (:data:`FLOTTANTS_DE_LA_COMPOSANTE`).
CONTENUS_DU_JOURNAL = {
    "evenement": ("echeancier", "Evenement"),
    "reversion": ("droit.reversion", "Reversion"),
    "foyer": ("droit.foyer", "Foyer"),
    "revalorisation": ("revalorisation", "Revalorisee"),
    "composante": None,
}

#: Les nombres d'une composante du journal que le Python écrit toujours en
#: flottants, par leur clé : JSON n'écrit pas « 1200.0 ». Tout autre nombre
#: y arrête la lecture, au lieu que son type se devine.
FLOTTANTS_DE_LA_COMPOSANTE = frozenset({"annuel"})


def _composante_lue(valeur, chemin: str, cle: str | None = None):
    """Une composante du journal, ou ce qu'elle tient sous ``cle`` : telle que
    JSON la rend, ses montants en flottants."""
    if isinstance(valeur, dict):
        return {nom: _composante_lue(element, f"{chemin}.{nom}", nom)
                for nom, element in valeur.items()}
    if isinstance(valeur, list):
        return [_composante_lue(element, f"{chemin}[{rang}]", cle)
                for rang, element in enumerate(valeur)]
    if cle in FLOTTANTS_DE_LA_COMPOSANTE:
        return lu_strictement(float | None, valeur, chemin)
    if valeur is None or type(valeur) in (str, bool):
        return valeur
    raise TypeError(f"{chemin} : nombre dont la lecture ne connaît pas le type : {valeur!r} "
                    "(pont.FLOTTANTS_DE_LA_COMPOSANTE)")

#: Les champs d'une entrée du journal tels que le portage les écrit, sous le
#: nom du Python (``Entree`` de ``journal.py``), hors de son contenu.
CHAMPS_DE_L_ENTREE = {
    "id": ("id", str), "evenement": ("evenement", str), "inscriteLe": ("inscrite_le", str),
    "debut": ("debut", str | None), "fin": ("fin", str | None), "sorte": ("sorte", str),
    "remplace": ("remplace", str | None), "annule": ("annule", str | None),
}


def _contenu_lu(sorte: str, contenu, chemin: str):
    """Le contenu d'une entrée du journal, sous le type de sa sorte."""
    import importlib

    if contenu is None:
        return ContenuNonLu(sorte)
    if sorte not in CONTENUS_DU_JOURNAL:
        raise ValueError(f"{chemin} : sorte d'entrée que la lecture ne connaît pas : {sorte}")
    declare = CONTENUS_DU_JOURNAL[sorte]
    if declare is None:
        if not isinstance(contenu, dict):
            raise TypeError(f"{chemin} : dictionnaire attendu, le portage a écrit {contenu!r}")
        return _composante_lue(contenu, chemin)
    module, nom = declare
    return lu_strictement(getattr(importlib.import_module(f"{__package__}.{module}"), nom),
                          contenu, chemin)


def journal_des_donnees(entrees: list[dict], chemin: str = "journal"):
    """Le journal que le portage a écrit entrée par entrée
    (``comparaisonTelleQuelle`` de ``pont.mjs``), sous le type du Python : ses
    entrées inscrites dans leur ordre, chacune avec ce qui la date et son
    contenu, sous le type de sa sorte (:data:`CONTENUS_DU_JOURNAL`) — ou
    illisible, quand il ne passe pas (:class:`ContenuNonLu`)."""
    from .journal import Entree, Journal

    if not isinstance(entrees, list):
        raise TypeError(f"{chemin} : suite attendue, le portage a écrit {entrees!r}")
    journal = Journal()
    for rang, ecrite in enumerate(entrees):
        ici = f"{chemin}[{rang}]"
        if set(ecrite) != {*CHAMPS_DE_L_ENTREE, "contenu"}:
            raise ValueError(f"{ici} : Entree : le portage écrit les champs {sorted(ecrite)}")
        champs = {nom: lu_strictement(type_, ecrite[du_portage], f"{ici}.{nom}")
                  for du_portage, (nom, type_) in CHAMPS_DE_L_ENTREE.items()}
        journal.inscrire(Entree(
            **champs, contenu=_contenu_lu(champs["sorte"], ecrite["contenu"], f"{ici}.contenu")))
    return journal


def comparaison_des_donnees(comparaison: dict):
    """La comparaison entière que le portage a écrite, sous le type du Python
    (``Comparaison``), lue strictement, son journal compris. Ses paramètres
    reviennent sans la racine des données, dont le paquet tenait lieu : le
    client y remet les siens. Le module du simulateur ne se charge qu'à la
    lecture."""
    from .simulateur import Comparaison

    return lu_strictement(Comparaison, comparaison, "Comparaison")


def resultat_notionnel_des_donnees(resultat: dict):
    """Le résultat d'un univers notionnel que le portage a écrit, sous le type
    du Python (``ResultatNotionnel``), lu strictement."""
    from .scenarios.notionnel import ResultatNotionnel

    return lu_strictement(ResultatNotionnel, resultat, "ResultatNotionnel")


def garantie_vieillesse_des_donnees(garantie: dict):
    """La garantie vieillesse de la proposition que le portage a écrite
    (``_garantieVieillesse`` du scénario 6), sous le type du Python
    (``GarantieVieillesse``), lue strictement."""
    from .scenarios.notionnel import GarantieVieillesse

    return lu_strictement(GarantieVieillesse, garantie, "GarantieVieillesse")


def resultat_actuel_des_donnees(actuel: dict):
    """Le résultat entier du scénario 1 que le portage a écrit, sous le type du
    Python (``ResultatActuel``), lu strictement. Le module du scénario ne se
    charge qu'à la lecture."""
    from .scenarios.actuel import ResultatActuel

    return lu_strictement(ResultatActuel, actuel, "ResultatActuel")


#: Ce que rend chaque entrée de la façade (``ENTREES_DE_LA_FACADE`` de
#: ``pont.mjs``), relu sous le type du Python. Une entrée qui n'y est pas est
#: refusée avant node.
#: Les durées du relevé, chaque compte et chaque régime par ses années.
_PAR_ANNEE = tuple[tuple[str, tuple[tuple[int, int], ...]], ...]


def liquidation_des_donnees(donnees: dict) -> dict:
    """La liquidation que le portage a écrite (``liquidation.liquider`` de
    ``pont.mjs``), par ce que les tests en lisent, lu strictement : ``taux``,
    le plus haut des taux de liquidation des régimes en annuités ;
    ``regimes``, la pension de chaque régime, complétée, dans l'ordre ;
    ``pensions`` et ``plafonds``, les pensions de l'étape « liquider », avant
    les compléments, et ce que le plafond de L. 18 en écarte ;
    ``complements`` et ``avantages_des_complements``, ce que l'étape
    « compléter » écrit ;
    ``total``, ``hors_repartition`` et ``total_contributif`` ; ``mesures``,
    ce que la cascade a mesuré, et ``avantages``, chaque avantage appliqué ;
    ``lignes``, celles du relevé qu'elle a lues, et ``donnees``, ce que le
    contrat C.6 en décrit, tels quels ; ``appels``, combien de fois
    ``liquider`` a tourné, liquidations d'essai comprises."""
    from .droit.commun import AvantageApplique, PensionRegime
    from .droit.liquidation import Mesure
    from .donnees.chargement import Fiabilite
    from .droit.liquider import EligiblePlafondEnfants
    from .calendrier import DateMois

    return {"taux": lu_strictement(float, donnees["taux"], "liquidation.taux"),
            "pensions": lu_strictement(tuple[PensionRegime, ...], donnees["pensions"],
                                       "liquidation.pensions.regimes"),
            "plafonds": lu_strictement(tuple[EligiblePlafondEnfants, ...], donnees["plafonds"],
                                       "liquidation.pensions.plafonds"),
            "complements": lu_strictement(tuple[PensionRegime, ...], donnees["complements"],
                                          "liquidation.complements.regimes"),
            "avantages_des_complements": lu_strictement(
                tuple[AvantageApplique, ...], donnees["avantages_des_complements"],
                "liquidation.complements.avantages"),
            "regimes": lu_strictement(tuple[PensionRegime, ...], donnees["regimes"],
                                      "liquidation.regimes"),
            **{cle: lu_strictement(float, donnees[cle], f"liquidation.{cle}")
               for cle in ("total", "hors_repartition", "total_contributif")},
            "mesures": lu_strictement(tuple[Mesure, ...], donnees["mesures"],
                                      "liquidation.mesures"),
            "avantages": lu_strictement(tuple[AvantageApplique, ...], donnees["avantages"],
                                        "liquidation.avantages"),
            "lignes": donnees["lignes"], "donnees": donnees["donnees"],
            "appels": lu_strictement(int, donnees["appels"], "liquidation.appels"),
            "fiabilite": lu_strictement(Fiabilite, donnees["fiabilite"], "liquidation.fiabilite"),
            "journal": (None if donnees["journal"] is None
                        else journal_des_donnees(donnees["journal"], "liquidation.journal")),
            "minimum_applique": lu_strictement(bool, donnees["minimum_applique"],
                                               "liquidation.minimum_applique"),
            "demande": demande_des_donnees(donnees["demande"]),
            "date_liquidation": DateMois(*lu_strictement(
                tuple[int, int], donnees["date_liquidation"], "liquidation.date_liquidation")),
            "ouverte": lu_strictement(bool, donnees["ouverte"], "liquidation.ouverte")}


def departs_liquides_des_donnees(lu: dict) -> dict:
    """Chaque départ liquidé que le portage a écrit
    (``departs.liquider_les_departs`` de ``pont.mjs``) : chaque liquidation,
    lue comme :func:`liquidation_des_donnees`, et ``appels``, ceux de
    ``liquider`` qu'elles ont coûtés ensemble."""
    return {"liquidations": [liquidation_des_donnees(liquidee)
                             for liquidee in lu["liquidations"]],
            "appels": lu_strictement(int, lu["appels"], "departs.appels")}


def etape_de_la_liquidation_des_donnees(donnees: dict) -> dict:
    """L'étape de la liquidation au bout d'une chaîne (``droit.etapes`` de
    ``pont.mjs``), par ce que les tests en lisent, lu strictement :
    l'ouverture, ``requis``, ``age``, ``motif`` et ``trimestres_cotises`` ;
    les pensions, ``regimes`` et ``taux`` ; les compléments, ``regimes`` et
    ``total`` ; chacune, ``donnees``, ce que son schéma décrit, tel quel."""
    from .droit.commun import PensionRegime

    etape = donnees["etape"]
    lectures = {
        "ouvrir": {"requis": int, "age": float | None, "motif": str,
                   "trimestres_cotises": int},
        "liquider": {"regimes": tuple[PensionRegime, ...], "taux": float},
        "completer": {"regimes": tuple[PensionRegime, ...], "total": float},
    }[etape]
    return {"donnees": donnees["donnees"],
            **{nom: lu_strictement(type_, donnees[nom], f"{etape}.{nom}")
               for nom, type_ in lectures.items()}}


def demande_des_donnees(donnees: dict):
    """La demande qu'un départ appelle (``liquidation.demande_de_depart`` de
    ``pont.mjs``), lue strictement sous le type du Python (``Demande``)."""
    from .droit.liquidation import Demande

    return lu_strictement(Demande, donnees, "Demande")


def des_regimes_des_donnees(lu: dict) -> dict:
    """Ce que les durées disent de régimes nommés (``compter.des_regimes`` de
    ``pont.mjs``), lu strictement : leurs ``services_effectifs`` et
    ``services_liquidables`` ; ce que les emplois classés leur ajoutent,
    ``services``, ``majorations``, ``bonifications`` — celles qui portent le
    pourcentage au-delà du maximum — ; et ``hors_surcote``, de tous les
    régimes."""
    noms = ("services_effectifs", "services_liquidables", "services", "majorations",
            "bonifications", "hors_surcote")
    if set(lu) != set(noms):
        raise ValueError(f"des_regimes : {sorted(lu)} au lieu de {list(noms)}")
    return {nom: lu_strictement(int, lu[nom], f"des_regimes.{nom}") for nom in noms}


def durees_des_donnees(durees: dict) -> dict:
    """Les durées que le portage a écrites (``dureesEnDonnees`` de
    ``pont.mjs``), lues strictement : ``par_annee``, par compte, régime et
    année, les trimestres crédités ; ``plafonds``, par compte, celui de chaque
    année de la carrière ; ``trimestres_par_regime`` et ``trimestres`` ;
    ``hors_annee``, par compte et régime, ce qui ne tient à aucune année ;
    ``enfants``, les trimestres des enfants, ``None`` sans eux ; ``donnees``,
    ce que leur schéma décrit, tel quel."""
    return {
        "par_annee": {compte: {code: dict(annees) for code, annees in lu_strictement(
            _PAR_ANNEE, regimes, f"releve.par_annee.{compte}")}
            for compte, regimes in durees["par_annee"].items()},
        "plafonds": {compte: dict(lu_strictement(
            tuple[tuple[int, int], ...], plafonds, f"releve.plafonds.{compte}"))
            for compte, plafonds in durees["plafonds"].items()},
        "trimestres_par_regime": dict(lu_strictement(
            tuple[tuple[str, int], ...], durees["trimestres_par_regime"],
            "releve.trimestres_par_regime")),
        "trimestres": lu_strictement(int, durees["trimestres"], "releve.trimestres"),
        "hors_annee": {compte: dict(lu_strictement(
            tuple[tuple[str, float], ...], regimes, f"releve.hors_annee.{compte}"))
            for compte, regimes in durees["hors_annee"].items()},
        "enfants": None if durees["enfants"] is None else {
            **durees["enfants"], "par_regime": dict(lu_strictement(
                tuple[tuple[str, tuple[int, int]], ...], durees["enfants"]["par_regime"],
                "releve.enfants.par_regime"))},
        "donnees": durees["donnees"],
    }


def droits_des_donnees(droits: dict) -> dict:
    """Les droits que le portage a écrits (``droitsEnDonnees`` de
    ``pont.mjs``), lus strictement : ``points``, les crédits
    ``(code, annee, points, taux)``, et ``cotisations``, les cotisations
    revalorisées ``(code, annee, montant)``, dans l'ordre ;
    ``points_acquis`` et ``majoration_points``, par régime ; ``plafonds``,
    ``(code, total, avant, retenus)`` ; ``gratuits``, par régime,
    ``(points, avant)`` ; ``donnees``, ce que leur schéma décrit, tel quel."""
    return {
        "points": lu_strictement(tuple[tuple[str, int, float, float | None], ...],
                                 droits["points"], "releve.points"),
        "cotisations": lu_strictement(tuple[tuple[str, int, float], ...],
                                      droits["cotisations"], "releve.cotisations"),
        "points_acquis": dict(lu_strictement(tuple[tuple[str, float], ...],
                                             droits["points_acquis"], "releve.points_acquis")),
        "majoration_points": dict(lu_strictement(
            tuple[tuple[str, float], ...], droits["majoration_points"],
            "releve.majoration_points")),
        "plafonds": lu_strictement(tuple[tuple[str, float, float, float], ...],
                                   droits["plafonds"], "releve.plafonds_des_droits"),
        "gratuits": {code: tuple(gratuit) for code, gratuit in droits["gratuits"]},
        "donnees": droits["donnees"],
    }


def coordination_des_donnees(coordination: dict) -> dict:
    """La coordination que le portage a écrite (``coordinationEnDonnees`` de
    ``pont.mjs``) : ``donnees``, ce que son schéma décrit, tel quel ;
    ``regimes``, ceux de chaque ligne ; ``inchangee``, quand elle a gardé la
    carrière reçue, et sinon ``carriere``, la carrière rétablie, sous le type
    du Python."""
    return {
        "donnees": coordination["donnees"],
        "regimes": lu_strictement(tuple[tuple[str, ...], ...], coordination["regimes"],
                                  "coordination.regimes"),
        "inchangee": lu_strictement(bool, coordination["inchangee"], "coordination.inchangee"),
        "carriere": (None if coordination["carriere"] is None
                     else carriere_des_donnees(coordination["carriere"])),
    }


def releve_des_donnees(donnees: dict) -> dict:
    """Le relevé des droits que le portage a écrit (``releveEnDonnees`` de
    ``pont.mjs``) : ses ``durees`` (:func:`durees_des_donnees`), ses
    ``droits`` (:func:`droits_des_donnees`), sa ``coordination``
    (:func:`coordination_des_donnees`), ``groupes``, les membres du groupe de
    chaque régime qui liquide avec d'autres, le liquidateur en tête, et
    ``donnees``, l'enveloppe du contrat C.5, telle quelle."""
    return {
        "durees": durees_des_donnees(donnees["durees"]),
        "droits": droits_des_donnees(donnees["droits"]),
        "coordination": coordination_des_donnees(donnees["coordination"]),
        "groupes": {code: tuple(membres) for code, membres in lu_strictement(
            tuple[tuple[str, tuple[str, ...]], ...], donnees["groupes"], "releve.groupes")},
        "donnees": donnees["donnees"],
    }


def regime_fusionne_des_donnees(fusionne: dict):
    """Le régime unique du simulateur, que le portage fusionne de son
    catalogue (``regimeFusionne`` de ``moteur/js/simulateur.js``), lu
    strictement sous le type du Python (``RegimeFusionne``)."""
    from .moteur.fusion import RegimeFusionne

    return lu_strictement(RegimeFusionne, fusionne, "RegimeFusionne")


def majorations_des_donnees(lu: dict) -> tuple[list, tuple]:
    """Ce que rend la majoration exceptionnelle des petites pensions du
    portage (``revalorisation.majorer_les_petites_pensions`` de ``pont.mjs``),
    comme son jumeau : les régimes servis, chacun avec sa majoration, et le
    calcul de la caisse, lus strictement sous les types du Python."""
    from .revalorisation import MajorationExceptionnelle, RegimeServi

    return (list(lu_strictement(tuple[RegimeServi, ...], lu["regimes"], "regimes")),
            lu_strictement(tuple[MajorationExceptionnelle, ...], lu["majorations"],
                           "majorations"))


LECTURES_DE_LA_FACADE = {
    "simulateur.simuler": comparaison_des_donnees,
    "simulateur.carriere_simple": carriere_des_donnees,
    "simulateur.carriere_parcours": carriere_des_donnees,
    "simulateur.carriere_releve": carriere_des_donnees,
    "carriere.depuis_profil": carriere_des_donnees,
    "carriere.depuis_parcours": carriere_des_donnees,
    "carriere.depuis_releve": carriere_des_donnees,
    "carriere.depuis_chronologie": carriere_des_donnees,
    "scenario_actuel.calculer": resultat_actuel_des_donnees,
    "reversion.reversion": reversion_des_donnees,
    "releve.construire": releve_des_donnees,
    "simulateur.regime_fusionne": regime_fusionne_des_donnees,
    "simulateur.proposition": lambda lu: resultat_notionnel_des_donnees(lu),
    "simulateur.carriere_proposition": lambda lu: None if lu is None else carriere_des_donnees(lu),
    "carriere.prolongee": lambda lu: None if lu is None else carriere_des_donnees(lu),
    "simulateur.garantie_vieillesse": garantie_vieillesse_des_donnees,
    "liquidation.liquider": liquidation_des_donnees,
    "liquidation.demande_de_depart": demande_des_donnees,
    "departs.liquider_les_departs": departs_liquides_des_donnees,
    "coordonner.coordonner": coordination_des_donnees,
    "compter.compter": durees_des_donnees,
    "acquerir.acquerir": droits_des_donnees,
    "compter.cumul_plafonne": lambda cumul: lu_strictement(int, cumul, "cumul_plafonne"),
    "compter.trimestres_du_contrat": lambda lu: dict(lu_strictement(
        tuple[tuple[int, int], ...], lu, "trimestres_du_contrat")),
    "compter.jours_par_annee": lambda lu: dict(lu_strictement(
        tuple[tuple[int, int], ...], lu, "jours_par_annee")),
    "compter.des_regimes": lambda lu: des_regimes_des_donnees(lu),
    "droit.etapes": etape_de_la_liquidation_des_donnees,
    "revalorisation.faire_vivre": lambda lu: _contenu_lu("revalorisation", lu, "Revalorisee"),
    "revalorisation.actuel_aujourd_hui": lambda lu: actuel_aujourd_hui_des_donnees(lu),
    "commun.periode_de_liquidation": lambda rang: lu_strictement(
        int | None, rang, "periode_de_liquidation"),
    "revalorisation.majorer_les_petites_pensions": lambda lu: majorations_des_donnees(lu),
    "echeancier.parcourir": lambda lu: echeancier_des_donnees(lu),
    "simulateur.echeancier": lambda lu: echeancier_des_donnees(lu),
    "echeancier.depart_de": lambda lu: evenement_des_donnees(lu),
    "echeancier.sortes": lambda lu: sortes_des_donnees(lu),
    "journal.operer": lambda lu: None if lu is None else lu_strictement(
        tuple[int, ...], lu, "journal"),
    "pilote.age_de_depart": lambda lu: {
        "age": _flottant(lu["age"]),
        "appels": lu_strictement(int, lu["appels"], "pilote.appels")},
}

def echeancier_des_donnees(lu: dict) -> dict:
    """L'échéancier parcouru que le portage a écrit (``echeancierTelQuel`` de
    ``pont.mjs``), lu strictement : ``journal``, sous le type du Python
    (:func:`journal_des_donnees`) ; ``decrites``, ce que le contrat décrit du
    contenu de chaque entrée qui ne passe pas, par son identifiant ;
    ``au_depart`` et ``aujourd_hui``, le
    scénario 1 au départ et à l'échéance, ou ``None`` ; ``reversion``, celle
    qu'il liquide au décès de l'assuré (:func:`reversion_des_donnees`), ou
    ``None`` ; ``appels``, ceux de
    ``liquider`` que son parcours a coûtés."""
    return {"journal": journal_des_donnees(lu["journal"], "echeancier.journal"),
            "decrites": lu_strictement(dict[str, dict], lu["decrites"], "echeancier.decrites"),
            "au_depart": (None if lu["au_depart"] is None
                          else resultat_actuel_des_donnees(lu["au_depart"])),
            "aujourd_hui": (None if lu["aujourd_hui"] is None
                            else actuel_aujourd_hui_des_donnees(lu["aujourd_hui"])),
            "reversion": reversion_des_donnees(lu["reversion"]),
            "appels": lu_strictement(int, lu["appels"], "echeancier.appels")}


def evenement_des_donnees(lu) -> object:
    """Le départ que le portage tire d'une carrière (``departDe`` de
    ``moteur/js/echeancier.js``), sous le type du Python (``Evenement``), ou
    ``None``."""
    from .echeancier import Evenement

    return None if lu is None else lu_strictement(Evenement, lu, "Evenement")


def sortes_des_donnees(lu) -> dict[str, dict]:
    """Ce que chaque sorte d'événement appelle, tel que le paquet le tient :
    ``liquider``, un booléen, ``motif`` et ``nature``, des textes ou rien."""
    sortes = lu_strictement(dict[str, dict], lu, "sortes")
    for nom, sorte in sortes.items():
        if set(sorte) - {"liquider", "motif", "nature"}:
            raise ValueError(f"sortes.{nom} : le portage écrit les champs {sorted(sorte)}")
        lu_strictement(bool, sorte["liquider"], f"sortes.{nom}.liquider")
        for cle in ("motif", "nature"):
            lu_strictement(str | None, sorte.get(cle), f"sortes.{nom}.{cle}")
    return sortes


def actuel_aujourd_hui_des_donnees(lu) -> object:
    """Le système 1 servi une année (``actuelAujourdhui`` de
    ``moteur/js/revalorisation.js``), sous le type du Python
    (``ActuelAujourdhui``), lu strictement."""
    from .revalorisation import ActuelAujourdhui

    return lu_strictement(ActuelAujourdhui, lu, "actuel_aujourd_hui")


#: Le type que le Python donne à une erreur du portage, quand ce n'est pas
#: ``ValueError`` : par le début de son motif, ou par sa fin.
ERREURS_DU_PORTAGE = (
    ("affiliation inconnue", "", KeyError),
    ("présomption inconnue", "", KeyError),
    ("", "la fiche manque aux fiches datées du moteur", LookupError),
)


def erreur_du_portage(classe: str, motif: str) -> Exception:
    """L'erreur que le Python lève là où le portage a levé celle-ci : une
    donnée insuffisante reste ce qu'elle est ; une erreur du moteur est une
    ``ValueError``, sauf celles que le Python range ailleurs
    (:data:`ERREURS_DU_PORTAGE`). Une autre classe — une erreur de la saisie,
    que la façade ne sert pas — n'a pas de type ici."""
    from .donnees.chargement import DonneeInsuffisante

    if classe == "DonneeInsuffisante":
        return DonneeInsuffisante(motif)
    if classe != "Error":
        return RuntimeError(f"{PROGRAMME.name} : {classe} : {motif}")
    for debut, fin, type_ in ERREURS_DU_PORTAGE:
        if motif.startswith(debut) and motif.endswith(fin):
            return type_(motif)
    return ValueError(motif)


def facade(entree: str, *arguments, parametres=None, paquet: bytes | None = None):
    """Une entrée du moteur que les tests appellent, servie par le portage
    (``tests/facade.py``) : ``entree`` au nom de son jumeau Python,
    ``"scenario_actuel.calculer"``, ses arguments comme ceux d'un appel du
    droit (:func:`droit`) — :data:`MOTEUR`, :data:`SIMULATEUR`, une carrière,
    une valeur —, sous ``parametres``, les réglages de référence sans eux. Ce
    qu'elle rend revient sous le type du Python, lu strictement
    (:data:`LECTURES_DE_LA_FACADE`) ; ce que le portage refuse lève l'erreur
    que le Python lève (:func:`erreur_du_portage`), son motif celui du
    portage."""
    from .config import Parametres

    if entree not in LECTURES_DE_LA_FACADE:
        raise ValueError(f"entrée que la façade ne sert pas : {entree} "
                         "(pont.LECTURES_DE_LA_FACADE)")
    carrieres: list = []
    valeurs = [_argument_du_droit(argument, carrieres) for argument in arguments]
    reponse = _demander({"facade": {
        "parametres": parametres_en_donnees(Parametres() if parametres is None else parametres),
        "carrieres": [carriere_en_donnees(carriere) for carriere in carrieres],
        "entree": entree,
        "arguments": valeurs,
    }}, _paquet_de(parametres, paquet))
    if "refus" in reponse:
        raise erreur_du_portage(**reponse["refus"])
    return LECTURES_DE_LA_FACADE[entree](reponse["rendu"])


# -- les tables du moteur, par la façade (action 161) ----------------------------
#
# Un test lit aussi les tables du moteur du scénario 1 —
# ``simulateur.scenario_actuel.reversions.minimum(2025)``. La façade les sert
# par leur nom et leur méthode : le portage appelle la méthode de sa table, et
# ce qu'elle rend revient sous le type que la méthode du jumeau Python annonce,
# lu strictement. Un bloc à part, comme le reste de la façade.

#: Les méthodes des tables du moteur que la façade sert, sous les noms du
#: Python : ``{table: méthodes}``. Chacune a les mêmes arguments, dans le même
#: ordre, dans le portage (``moteur/js/regimes.js``), et un appel confronté au
#: jumeau (``tests/test_facade_jumeau.py``). Une méthode qui n'y est pas est
#: refusée avant node.
TABLES_DE_LA_FACADE: dict[str, tuple[str, ...]] = {
    "ages_annulation_decote": ("age",),
    "ages_categorie_active": ("derogation",),
    "ages_ouverture": ("age",),
    "ages_regimes": ("ages",),
    "ages_surcote_regimes_speciaux": ("age",),
    "calendriers_duree_requise": ("trimestres",),
    "decote_regimes_speciaux": ("parametres",),
    "durees_requises_regimes": ("ligne",),
    # Le forfait de la catégorie d'un marin (R. 11), le salaire moyen passé
    # par sa marque (:data:`SALAIRE_MOYEN`).
    "grilles": ("forfait",),
    "annees_salaire_reference": ("annees",),
    "baremes_trimestre": ("valeurs",),
    "carriere_longue": ("_portes", "cotises_reputes"),
    "complement_differentiel_rco": ("regle", "smic_net"),
    "coefficients_minoration": ("coefficient",),
    "conversions_points": ("echelle", "fusion"),
    "durees_requises": ("trimestres",),
    "fiches_datees": ("regle",),
    "invalidites": ("version",),
    "majorations_enfants": ("par_enfant",),
    "majorations_enfants_points": ("taux",),
    "maximum_des_cultes": ("valeur",),
    "minimum_contributif": ("avts", "pension_minimum", "regle", "valeurs"),
    "minimum_garanti": ("montant", "ratio_point_indice", "reference"),
    "minimum_vieillesse": ("deux_etages", "plafond", "plafond_couple"),
    "pension_majoree_reference": ("montant", "regle"),
    "rendements": ("rendement",),
    "revalorisations_pensions": ("generale",),
    "reversions": ("fiche_du_regime", "limite_cumul", "majoration_enfant", "minimum",
                   "plafond_majoration", "version"),
    "valeurs_point": ("_en_vigueur", "achat", "achat_prolonge", "derniere_annee_servie", "garantie",
                      "regimes_convenus", "service", "service_au"),
}

# Ce que devient un point à une fusion (``conversions_points.fusion``) : le
# portage en écrit les champs en casse de chameau.
CLASSES_EN_CHAMEAU |= {"ConversionPoint", "DeuxEtages"}


class _Series:
    """Les séries du simulateur, en argument d'une méthode de table
    (:func:`table_du_moteur`)."""

    def __repr__(self) -> str:
        return "pont.SERIES"


#: Les séries du simulateur en argument d'une méthode de table : le portage y
#: met les siennes (``simulateur.macro``), sous les paramètres de la demande.
SERIES = _Series()


class _SalaireMoyen:
    """Le salaire moyen des séries du simulateur, une fonction de l'année, en
    argument d'une méthode de table (``grilles.forfait``)."""

    def __repr__(self) -> str:
        return "pont.SALAIRE_MOYEN"


#: Le salaire moyen annuel des séries du simulateur, en argument fonction
#: d'une méthode de table : le portage y met
#: ``(a) => salaireMoyenAnnuel(macro, a)``, sous les paramètres de la demande.
SALAIRE_MOYEN = _SalaireMoyen()


@dataclasses.dataclass(frozen=True)
class DureesPosees:
    """Des durées posées par le test, trimestres par régime, en argument d'une
    règle de la façade qui ne lit d'elles que ``trimestres_par_regime``
    (``liquider.duree_majoree_apres_taux_plein``) : le portage en fait une
    ``Map``. Le jumeau les lit telles quelles."""

    trimestres_par_regime: dict


class _RegimeFusionne:
    """Le régime unique du simulateur, en argument d'une méthode de
    constructeur (:func:`constructeur_du_compte`)."""

    def __repr__(self) -> str:
        return "pont.REGIME_FUSIONNE"


#: Le régime unique du simulateur en argument d'une méthode de constructeur :
#: le portage y met le sien (``simulateur.regimeFusionne``), sous les
#: paramètres de la demande.
REGIME_FUSIONNE = _RegimeFusionne()


@dataclasses.dataclass(frozen=True)
class PeriodeDuCatalogue:
    """Une période d'un régime du catalogue, en argument d'une méthode de
    table : celle de ce rang parmi les périodes du régime, que le portage
    prend dans son catalogue, et l'année où elle commence, qu'il vérifie.
    :class:`Periode` ne nomme que la première période d'une année, quand un
    régime en tient plusieurs à la fois — une par tranche."""

    regime: str
    rang: int
    debut: int


@dataclasses.dataclass(frozen=True)
class RegimeDuCatalogue:
    """Un régime du catalogue, en argument d'une règle du droit : celui de ce
    code, que le portage prend dans son catalogue
    (``completer._taux_majoration_enfants``)."""

    code: str


def table_du_moteur(table: str, methode: str, type_rendu, *arguments, parametres=None,
                    paquet: bytes | None = None):
    """Ce que rend la méthode ``methode`` de la table ``table`` du moteur du
    scénario 1, sous les noms du Python (``"reversions"``, ``"minimum"``),
    appelée par le portage sur la sienne, sous ``parametres`` : ses arguments
    comme ceux d'un appel du droit (:func:`droit`) — une carrière, une valeur
    —, :data:`SERIES`, ou une période du catalogue
    (:class:`PeriodeDuCatalogue`). Ce qu'elle
    rend revient sous ``type_rendu``, que la méthode du jumeau annonce, lu
    strictement. Une méthode que :data:`TABLES_DE_LA_FACADE` ne déclare pas est
    refusée avant node ; ce que le portage refuse lève l'erreur que le Python
    lève (:func:`erreur_du_portage`)."""
    if methode not in TABLES_DE_LA_FACADE.get(table, ()):
        raise ValueError(f"méthode de table que la façade ne sert pas : {table}.{methode} "
                         "(pont.TABLES_DE_LA_FACADE)")
    return _methode_servie("scenario_actuel.table", MOTEUR, table, methode, type_rendu,
                           arguments, parametres, paquet)


def _methode_servie(entree: str, porteur, nom: str, methode: str, type_rendu, arguments,
                    parametres, paquet: bytes | None):
    """La méthode ``methode`` de l'objet ``nom`` du ``porteur`` — le moteur
    ou le simulateur —, demandée au portage par l'entrée ``entree`` de la
    façade, ce qu'elle rend lu strictement sous ``type_rendu``."""
    from .config import Parametres

    carrieres: list = []
    valeurs = [_argument_de_la_facade(argument, carrieres) for argument in arguments]
    reponse = _demander({"facade": {
        "parametres": parametres_en_donnees(Parametres() if parametres is None else parametres),
        "carrieres": [carriere_en_donnees(carriere) for carriere in carrieres],
        "entree": entree,
        "arguments": [_argument_du_droit(porteur, carrieres), {"valeur": nom},
                      {"valeur": methode}, *valeurs],
    }}, _paquet_de(parametres, paquet))
    if "refus" in reponse:
        raise erreur_du_portage(**reponse["refus"])
    return lu_strictement(type_rendu, reponse["rendu"], f"{nom}.{methode}")


# -- le constructeur du compte, par la façade (action 161) -------------------------
#
# Un test lit aussi ce que le constructeur du compte notionnel prélève une
# année — ``simulateur.constructeur_employeur.cotisation_annuelle(carriere,
# 1952)`` — ou le taux qu'il porte au compte. La façade sert ces méthodes comme
# celles d'une table : le portage appelle celle de son constructeur.

#: Les méthodes des constructeurs du compte que la façade sert, sous les noms
#: du Python : ``{constructeur: méthodes}``. Chacune a les mêmes arguments,
#: dans le même ordre, dans le portage (``moteur/js/compte.js``), et un appel
#: confronté au jumeau (``tests/test_facade_jumeau.py``). Une méthode qui n'y
#: est pas est refusée avant node.
CONSTRUCTEURS_DE_LA_FACADE: dict[str, tuple[str, ...]] = {
    "constructeur": ("cotisation_annuelle", "taux_effectif", "construire"),
    "constructeur_employeur": ("cotisation_annuelle", "taux_effectif", "construire"),
    "constructeur_prelevement": ("cotisation_annuelle", "taux_effectif", "construire"),
}


def constructeur_du_compte(constructeur: str, methode: str, type_rendu, *arguments,
                           parametres=None, paquet: bytes | None = None):
    """Ce que rend la méthode ``methode`` du constructeur ``constructeur`` du
    simulateur, sous les noms du Python, appelée par le portage sur le sien,
    sous ``parametres`` : ses arguments comme ceux d'une méthode de table
    (:func:`table_du_moteur`), ce qu'elle rend lu strictement sous
    ``type_rendu``. Une méthode que :data:`CONSTRUCTEURS_DE_LA_FACADE` ne
    déclare pas est refusée avant node."""
    if methode not in CONSTRUCTEURS_DE_LA_FACADE.get(constructeur, ()):
        raise ValueError(f"méthode de constructeur que la façade ne sert pas : "
                         f"{constructeur}.{methode} (pont.CONSTRUCTEURS_DE_LA_FACADE)")
    return _methode_servie("simulateur.constructeur", SIMULATEUR, constructeur, methode,
                           type_rendu, arguments, parametres, paquet)


# -- la mortalité du simulateur, par la façade (action 161) -----------------------

#: Les méthodes des données de mortalité du simulateur que la façade sert,
#: sous les noms du Python : les mêmes arguments, dans le même ordre, dans le
#: portage (``moteur/js/mortalite.js``), et un appel confronté au jumeau
#: (``tests/test_facade_jumeau.py``). Une méthode qui n'y est pas est refusée
#: avant node.
MORTALITE_DE_LA_FACADE: tuple[str, ...] = ("survie_annuelle",)


def mortalite_du_simulateur(methode: str, type_rendu, *arguments, parametres=None,
                            paquet: bytes | None = None):
    """Ce que rend la méthode ``methode`` des données de mortalité du
    simulateur (``simulateur.mortalite``), appelée par le portage sur les
    siennes, sous ``parametres`` : ses arguments comme ceux d'une méthode de
    table (:func:`table_du_moteur`), ce qu'elle rend lu strictement sous
    ``type_rendu``. Une méthode que :data:`MORTALITE_DE_LA_FACADE` ne déclare
    pas est refusée avant node."""
    if methode not in MORTALITE_DE_LA_FACADE:
        raise ValueError(f"méthode de la mortalité que la façade ne sert pas : {methode} "
                         "(pont.MORTALITE_DE_LA_FACADE)")
    return _methode_servie("simulateur.mortalite", SIMULATEUR, "mortalite", methode,
                           type_rendu, arguments, parametres, paquet)


def _argument_de_la_facade(argument, carrieres: list) -> dict:
    """Un argument d'une méthode de table ou d'une règle du droit que la façade
    sert, tel que ``pont.mjs`` le relit : comme celui d'un appel du droit
    (:func:`_argument_du_droit`), sauf six, qui passent par leur marque — les
    séries du simulateur, son régime unique, un régime ou une période de son catalogue, une date au mois,
    dont le portage refait une ``DateMois``, et une :class:`Table`, dont il
    refait une ``Map``."""
    from .calendrier import DateMois

    if argument is SERIES:
        return {"valeur": {"@": "series"}}
    if argument is SALAIRE_MOYEN:
        return {"valeur": {"@": "salaire_moyen"}}
    if isinstance(argument, DureesPosees):
        return {"valeur": {"@": "durees_posees",
                           "trimestres_par_regime": list(argument.trimestres_par_regime.items())}}
    if argument is REGIME_FUSIONNE:
        return {"valeur": {"@": "regime_fusionne"}}
    if isinstance(argument, PeriodeDuCatalogue):
        return {"valeur": {"@": "periode", **dataclasses.asdict(argument)}}
    if isinstance(argument, RegimeDuCatalogue):
        return {"valeur": {"@": "regime", "code": argument.code}}
    if isinstance(argument, DateMois):
        return {"valeur": {"@": "date_mois", "annee": argument.annee, "mois": argument.mois}}
    if isinstance(argument, ContexteDuMoteur):
        return {"valeur": {"@": "contexte", "neutralisations": list(argument.neutralisations)}}
    if isinstance(argument, Table):
        return {"valeur": {"@": "table", "entrees": [[cle, _en_donnees(element)]
                                                     for cle, element in argument.entrees]}}
    if dataclasses.is_dataclass(argument) and type(argument).__name__ in TYPES_DE_LA_FACADE:
        return {"valeur": {_nom_du_portage(type(argument), champ.name):
                           _en_donnees(getattr(argument, champ.name))
                           for champ in dataclasses.fields(argument)}}
    return _argument_du_droit(argument, carrieres)


@dataclasses.dataclass(frozen=True)
class Table:
    """Un dictionnaire que le portage lit en ``Map``, en argument d'une règle
    de la façade (:data:`TABLES_DES_REGLES`) : ses entrées, ``(clé, valeur)``,
    dans l'ordre, chaque clé sous son type — une année reste un entier, quand
    JSON écrirait en texte la clé d'un objet."""

    entrees: tuple


#: Les arguments des règles de la façade que le portage lit en ``Map``, sous
#: leur nom : ``{"module.règle": noms}``. Un dictionnaire y passe en
#: :class:`Table` ; ``None``, la table vide que la règle du Python lui
#: substitue.
TABLES_DES_REGLES: dict[str, frozenset[str]] = {
    "compter.majoration_pour_enfants": frozenset({"trimestres_par_regime"}),
    "liquider.majorer_les_points_de_1952_a_1972": frozenset({"points"}),
    "liquider.repartir_les_annees": frozenset({"durees", "minimums"}),
    "carriere.prolonger_releve": frozenset({"interruptions", "temps_partiel", "dispenses"}),
}


#: Les objets du droit qu'une règle de la façade reçoit, sous les noms que le
#: portage leur donne (:data:`CLASSES_EN_CHAMEAU`) : un éligible au minimum
#: contributif, que ``droit/completer.js`` lit en chameau ; une pension de
#: régime, que le portage écrit et lit sous les noms du Python.
TYPES_DE_LA_FACADE = frozenset({"AvantageApplique", "EligibleMinimum", "EligibleAgricole",
                                "PensionRegime"})
CLASSES_EN_CHAMEAU |= {"EligibleMinimum", "DureesDesCultes", "PensionMajoree",
                       "RevenuDesPoints"}


# -- les règles du droit, par la façade (action 161) ------------------------------
#
# Un test appelle aussi une règle du droit — ``ouvrir.duree_requise(moteur,
# periode, carriere)``. La façade la sert par son module et son nom : le
# portage appelle la sienne, et ce qu'elle rend revient sous le type que le
# jumeau Python annonce, lu strictement, comme une méthode de table.

#: Les règles du droit que la façade sert, sous les noms du Python :
#: ``{module: règles}``. Chacune a les mêmes arguments, dans le même ordre et
#: sous les mêmes valeurs par défaut, dans le portage
#: (``moteur/js/droit/<module>.js`` ; ``tests/test_facade.py`` le vérifie), et
#: un appel confronté au jumeau (``tests/test_facade_jumeau.py``). Une règle
#: qui n'y est pas est refusée avant node.
REGLES_DE_LA_FACADE: dict[str, tuple[str, ...]] = {
    # L'escalier de la retraite proportionnelle agricole (R. 732-71) et son
    # plancher de seize points (R. 732-73).
    "acquerir": ("points_msa", "points_msa_retenus"),
    # Hors de ``droit/`` : ``carriere.js``, à la racine du portage — le relevé
    # prolongé jusqu'au départ, et le salaire moyen d'une année.
    "carriere": ("prolonger_releve", "salaire_moyen_annuel"),
    # L'âge légal de la génération, et l'âge du taux plein de l'ancien
    # combattant ou prisonnier de guerre (D. 351-2).
    "categories": ("age_des_anciens_combattants", "age_legal"),
    # Les parts de la majoration pour enfants à une date, et les étapes de
    # deux majorations à charge réunies.
    "commun": ("date_d_effet", "fusionner_les_charges", "ligne_cotisee",
               "majoration_du_conjoint", "parts_de_la_majoration"),
    # Les trimestres des enfants et le régime qui les porte (R. 173-15).
    "compter": ("arrondir_les_services", "majoration_pour_enfants"),
    # Les deux fractions de la pension des cultes : la durée de chacune, sur
    # les durées du relevé, et la part de l'écart du V du décret n° 2006-1325.
    "cultes": ("durees", "part_de_l_ecart"),
    "completer": ("_taux_majoration_enfants", "avpf_retenue", "borne_avec_les_droits_d_avant_1973", "complement_minimum",
                  "fins_de_charge",
                  "majoration_ouverte", "majoration_retraite_proportionnelle",
                  "pension_majoree", "plancher_du_regime", "points_rco_de_chef",
                  "selon_la_regle"),
    # Les départs de chaque régime, l'âge légal qui les date, et ce que
    # devient chaque date de demande que la carrière dit.
    "departs": ("age_legal", "demandes", "departs", "departs_et_demandes"),
    # L'étape « foyer et net » entière : le portage rend le ``Foyer`` du
    # journal, que la façade lit sous le type du Python.
    "foyer": ("foyer_et_net",),
    # L'âge de l'ASPA de l'inapte (R. 815-1), la catégorie de la pension
    # d'invalidité et le plancher de la pension substituée (L. 341-15).
    # La rente viagère d'invalidité du fonctionnaire (L. 28).
    "invalidite": ("age_de_l_aspa", "categorie_de_la_pension", "plancher_de_la_substitution",
                   "rente_viagere_d_invalidite"),
    # La radiation des cadres par limite d'âge, et la carrière dont elle
    # arrête les services.
    "limite_age": ("radiation", "radier"),
    "liquider": ("_coefficient_anticipation", "abattement_points", "abattre_au_dela_du_plafond",
                 "age_de_la_duree_atteinte", "annees_au_prorata",
                 "assiette_de_reference", "conversion_capital_rafp", "majoration_rafp",
                 "mois_apres_le_depart", "prestation_rafp",
                 "borne_de_la_duree", "coefficient_surcote_datee", "decote_opposable",
                 "duree_du_regime_aligne", "duree_majoree_apres_taux_plein",
                 "duree_proratisation", "majoration_des_points_de_1952_a_1972_d_avant_2026",
                 "majorer_les_points_de_1952_a_1972", "maximum_des_pensions",
                 "moyenne_des_meilleures_annees", "nombre_d_annees_retenues",
                 "pension_maximale", "plafond_du_salaire_de_reference", "repartir_les_annees", "retranche_decote", "revenu_des_cotisations_minimales", "salaire_de_reference",
                 "taux_acquis_l_emporte", "taux_de_majoration_de_1952_a_1972",
                 "trimestres_de_decote",
                 "trimestres_de_surcote_regimes_speciaux", "valeur_du_point",
                 "valeur_point_fiche"),
    "ouvrir": ("age_annulation_droit", "age_ouverture", "age_ouverture_commun",
               "age_ouverture_droit", "age_surcote",
               "age_taux_plein", "age_taux_plein_droit", "depart_parent_trois_enfants", "derogation_active",
               "duree_requise", "fin_indemnisation", "indemnisation_bornee", "mois_ouverture_des_droits",
               "ouverture_carriere_longue"),
    # Le relevé à rebours : les points qu'un revenu ouvre, et le revenu que
    # des points supposent (action 138, étape 11).
    "releve": ("points_de_l_annee", "revenu_des_points"),
    # ``_cumuler``, privée au Python, que le portage exporte sous ``cumuler``.
    "reversion": ("_cumuler", "mois_de_mariage"),
    # Hors de ``droit/`` : ``revalorisation.js``, à la racine du portage.
    "revalorisation": ("majorations_forfaitaires",),
}


#: Les constantes du droit que la façade lit au portage, sous les noms du
#: Python : ``{module: constantes}``. Le portage les exporte de
#: ``moteur/js/droit/<module>.js`` ; une constante qui n'y est pas est refusée
#: avant node.
CONSTANTES_DE_LA_FACADE: dict[str, tuple[str, ...]] = {
    # L'âge du barème de 2007-2008 au-delà duquel la surcote est majorée.
    "liquider": ("SURCOTE_AGE_MAJORE",),
}


def constante_du_droit(module: str, nom: str, paquet: bytes | None = None):
    """La constante ``nom`` du module ``module`` du droit, telle que le portage
    l'exporte : une valeur simple. Une constante que
    :data:`CONSTANTES_DE_LA_FACADE` ne déclare pas est refusée avant node."""
    from .config import Parametres

    if nom not in CONSTANTES_DE_LA_FACADE.get(module, ()):
        raise ValueError(f"constante du droit que la façade ne lit pas : {module}.{nom} "
                         "(pont.CONSTANTES_DE_LA_FACADE)")
    reponse = _demander({"facade": {
        "parametres": parametres_en_donnees(Parametres()), "carrieres": [],
        "entree": "droit.constante",
        "arguments": [_argument_du_droit(SIMULATEUR, []), {"valeur": module}, {"valeur": nom}],
    }}, _paquet_de(None, paquet))
    if "refus" in reponse:
        raise erreur_du_portage(**reponse["refus"])
    return reponse["rendu"]


def regle_du_droit(module: str, regle: str, type_rendu, *arguments, parametres=None,
                   paquet: bytes | None = None):
    """Ce que rend la règle ``regle`` du module ``module`` du droit, sous les
    noms du Python (``"ouvrir"``, ``"duree_requise"``), appelée par le portage,
    sous ``parametres`` : ses arguments dans l'ordre du jumeau, comme ceux
    d'une méthode de table (:func:`table_du_moteur`) — :data:`MOTEUR`, une
    carrière, une période du catalogue (:class:`PeriodeDuCatalogue`), une
    ``DateMois``, une valeur. Ce qu'elle rend revient sous ``type_rendu``, que
    la règle du jumeau annonce, lu strictement. Une règle que
    :data:`REGLES_DE_LA_FACADE` ne déclare pas est refusée avant node ; ce que
    le portage refuse lève l'erreur que le Python lève
    (:func:`erreur_du_portage`)."""
    from .config import Parametres

    if regle not in REGLES_DE_LA_FACADE.get(module, ()):
        raise ValueError(f"règle du droit que la façade ne sert pas : {module}.{regle} "
                         "(pont.REGLES_DE_LA_FACADE)")
    carrieres: list = []
    valeurs = [_argument_de_la_facade(argument, carrieres) for argument in arguments]
    reponse = _demander({"facade": {
        "parametres": parametres_en_donnees(Parametres() if parametres is None else parametres),
        "carrieres": [carriere_en_donnees(carriere) for carriere in carrieres],
        "entree": "droit.regle",
        "arguments": [_argument_du_droit(SIMULATEUR, carrieres), {"valeur": module},
                      {"valeur": regle}, *valeurs],
    }}, _paquet_de(parametres, paquet))
    if "refus" in reponse:
        raise erreur_du_portage(**reponse["refus"])
    return lu_strictement(type_rendu, reponse["rendu"], f"{module}.{regle}")
