"""Le site, lu depuis le Python : ses pages et ses modules, par node.

Le texte du site n'est écrit qu'une fois, en JavaScript
(docs/architecture.md, § 8) : ``moteur/js/pages.js`` et ``gabarit.js``. Le
Python ne le rend plus. Ce qu'il en lit — les pages que ses tests examinent,
les témoins de pages, les constantes du site que la prose cite — il le demande
au portage lui-même, par ``site.mjs`` : un processus node, lancé à la première
demande et gardé ouvert, qui lit le paquet une fois et garde ses agrégats
d'une demande à l'autre, comme le navigateur.

    from retraite_notionnelle.web.site import module, rendre

    titre, corps = rendre("/simuler", {"naissance": "1975"})
    pages = module("pages")
    pages.TITRES["/cout"]                    # une constante du site
    pages.fraction_en_mots(0.25)             # une fonction : fractionEnMots
    g = module("gabarit")
    g.pourcentage(0.25, decimales=0)         # les arguments nommés vont à leur place

Un nom s'écrit à la manière du Python — ``fraction_en_mots``, ``_VUES_DE_PAGE``
— et se lit sous celui du portage — ``fractionEnMots``, ``VUES_DE_PAGE``. Une
instance de classe revient par référence (:class:`ObjetJS`) : ses champs se
lisent et ses méthodes s'appellent comme en Python, et elle se rend telle
quelle en argument.
``site().contexte`` est le contexte du site, en argument comme en objet.
"""

from __future__ import annotations

import atexit
import enum
import json
import math
import re
import selectors
import shutil
import subprocess
import tempfile
from functools import lru_cache
from pathlib import Path

RACINE = Path(__file__).resolve().parents[3]
PROGRAMME = Path(__file__).with_name("site.mjs")

#: Ce qu'une demande peut attendre sa réponse. Le premier rendu de la page Coût
#: calcule tout le bilan : six secondes ; dix minutes ne se rencontrent que si
#: node s'est arrêté sans le dire.
DELAI = 600.0


class ErreurSite(RuntimeError):
    """Le portage a levé une erreur, ou node s'est arrêté."""


def disponible() -> bool:
    """Node est-il là ? Sans lui, rien du site ne se lit depuis le Python."""
    return shutil.which("node") is not None


def nom_js(nom: str) -> str:
    """``fraction_en_mots`` -> ``fractionEnMots`` ; ``_VUES_DE_PAGE`` -> ``VUES_DE_PAGE``."""
    nom = nom.lstrip("_")
    if nom.upper() == nom or "_" not in nom:
        return nom
    tete, *suite = nom.split("_")
    return tete + "".join(morceau[:1].upper() + morceau[1:] for morceau in suite)


class Donnee(dict):
    """Un objet de données du portage : un dictionnaire, dont les clés se lisent
    aussi comme des attributs — ``compte.ligne``, ``compte.pib``. Rendu en
    argument, c'est l'objet du portage lui-même qui revient."""

    _ref: int | None = None

    def __getattr__(self, nom: str):
        if nom.startswith("__"):
            raise AttributeError(nom)
        for cle in (nom, nom_js(nom)):
            if cle in self:
                return self[cle]
        raise AttributeError(nom)

    def __missing__(self, cle):
        # « sous_un » se lit sous le nom que le portage lui donne, « sousUn ».
        if isinstance(cle, str) and nom_js(cle) != cle and nom_js(cle) in self:
            return self[nom_js(cle)]
        raise KeyError(cle)


class ObjetJS:
    """Une instance du portage, gardée par node : ses champs se lisent à la demande."""

    def __init__(self, site: "Site", ref: int, classe: str):
        self._site, self._ref, self._classe = site, ref, classe

    def __getattr__(self, nom: str):
        if nom.startswith("__"):
            raise AttributeError(nom)
        valeur = self._site._demander(
            {"op": "attribut", "ref": self._ref, "noms": list(dict.fromkeys((nom_js(nom), nom)))})
        if isinstance(valeur, dict) and "$absent" in valeur:
            raise AttributeError(valeur["$absent"])
        if isinstance(valeur, dict) and "$methode" in valeur:
            site, ref, methode = self._site, self._ref, valeur["$methode"]

            def appeler(*args, **kwargs):
                return site._demander({
                    "op": "methode", "ref": ref, "nom": methode, "args": list(args),
                    "kwargs": {nom_js(k): v for k, v in kwargs.items()}})

            appeler.__name__ = methode
            return appeler
        return valeur

    def __repr__(self) -> str:
        return f"<{self._classe} du portage n° {self._ref}>"


class Appelable:
    """Une fonction ou une classe du portage ; ses membres statiques s'y lisent."""

    def __init__(self, module: "Module", exporte: str):
        self._module, self._exporte = module, exporte
        self.__name__ = exporte

    def __call__(self, *args, **kwargs):
        return self._module._site._demander({
            "op": "appeler", "module": self._module._nom, "nom": self._exporte,
            "args": list(args), "kwargs": {nom_js(k): v for k, v in kwargs.items()}})

    def __getattr__(self, nom: str):
        if nom.startswith("__"):
            raise AttributeError(nom)
        return self._module._lire(f"{self._exporte}.{nom_js(nom)}")

    def __repr__(self) -> str:
        return f"<{self._exporte} du portage ({self._module._nom}.js)>"


class Module:
    """Un module du portage, ``moteur/js/<nom>.js``, vu comme un module Python."""

    def __init__(self, site: "Site", nom: str):
        self._site, self._nom = site, nom
        self._lus: dict[str, object] = {}

    def __getattr__(self, nom: str):
        if nom.startswith("__"):
            raise AttributeError(nom)
        return self._lire(nom_js(nom))

    def _lire(self, exporte: str):
        if exporte not in self._lus:
            valeur = self._site._demander({"op": "lire", "module": self._nom, "nom": exporte})
            if isinstance(valeur, dict) and "$absent" in valeur:
                raise AttributeError(valeur["$absent"])
            if isinstance(valeur, dict) and "$appelable" in valeur:
                valeur = Appelable(self, valeur["$appelable"])
            self._lus[exporte] = valeur
        return self._lus[exporte]


class Site:
    """Le portage JavaScript, servi par un processus node."""

    def __init__(self) -> None:
        # Node ne part qu'à la première demande : un module de tests qui lit
        # ses constantes à la collecte ne le lance que s'il en lit une.
        self._processus: subprocess.Popen | None = None
        self._modules: dict[str, Module] = {}

    def _demarrer(self) -> None:
        if not disponible():
            raise ErreurSite("node absent : le site ne se lit pas sans lui")
        self._journal = tempfile.TemporaryFile()
        self._processus = subprocess.Popen(
            ["node", str(PROGRAMME)], cwd=RACINE, stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=self._journal, text=True, encoding="utf-8",
            bufsize=1)
        self._selecteur = selectors.DefaultSelector()
        self._selecteur.register(self._processus.stdout, selectors.EVENT_READ)

    # -- ce que les pages demandent -------------------------------------------

    def rendre(self, chemin: str, requete: dict | None = None) -> tuple[str, str]:
        """Le titre et le corps d'une page, comme ``rendre`` du portage."""
        titre, corps = self._demander({"op": "rendre", "chemin": chemin,
                                       "requete": _chaines(requete)})
        return titre, corps

    def page(self, chemin: str, requete: dict | None = None) -> str:
        """La page entière — en-tête, corps, pied —, comme le site l'assemble."""
        return self._demander({"op": "page", "chemin": chemin, "requete": _chaines(requete)})

    @property
    def contexte(self) -> ObjetJS:
        """Le contexte du site : un argument des fonctions qui l'attendent, et un
        objet dont les méthodes répondent — ``site().contexte.cout()``."""
        return self._demander({"op": "contexte"})

    def module(self, nom: str) -> Module:
        """``moteur/js/<nom>.js`` : ``pages``, ``gabarit``, ``saisie``, ``cout``…"""
        if nom not in self._modules:
            self._modules[nom] = Module(self, nom)
        return self._modules[nom]

    def fermer(self) -> None:
        if self._processus is not None and self._processus.poll() is None:
            self._processus.stdin.close()
            try:
                self._processus.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self._processus.kill()

    # -- le fil ----------------------------------------------------------------

    def _demander(self, demande: dict):
        if self._processus is None:
            self._demarrer()
        if self._processus.poll() is not None:
            raise ErreurSite("node s'est arrêté : " + self._lire_journal())
        self._processus.stdin.write(json.dumps(_vers_json(demande), ensure_ascii=False) + "\n")
        self._processus.stdin.flush()
        if not self._selecteur.select(timeout=DELAI):
            raise ErreurSite(f"node n'a pas répondu en {DELAI:.0f} s")
        ligne = self._processus.stdout.readline()
        if not ligne:
            raise ErreurSite("node s'est arrêté : " + self._lire_journal())
        reponse = json.loads(ligne)
        if "erreur" in reponse:
            erreur = reponse["erreur"]
            raise ErreurSite(f"{erreur['nom']} : {erreur['message']}\n{erreur['pile']}")
        return self._depuis_json(reponse["resultat"])

    def _lire_journal(self) -> str:
        self._journal.seek(0)
        return self._journal.read().decode("utf-8", "replace")[-4000:]

    def _depuis_json(self, valeur):
        if isinstance(valeur, list):
            return [self._depuis_json(v) for v in valeur]
        if not isinstance(valeur, dict):
            return valeur
        if "$donnee" in valeur:
            donnee = Donnee({k: self._depuis_json(v) for k, v in valeur["$donnee"].items()})
            donnee._ref = valeur["$ref"]
            return donnee
        if "$ref" in valeur:
            return ObjetJS(self, valeur["$ref"], valeur.get("$classe", ""))
        if "$nombre" in valeur:
            return float(valeur["$nombre"].replace("Infinity", "inf"))
        if "$ensemble" in valeur:
            return frozenset(self._depuis_json(v) for v in valeur["$ensemble"])
        if "$table" in valeur:
            return {self._depuis_json(k): self._depuis_json(v) for k, v in valeur["$table"]}
        return Donnee({k: self._depuis_json(v) for k, v in valeur.items()})


def _chaines(requete: dict | None) -> dict[str, str]:
    """Une requête d'adresse ne porte que des chaînes, comme ``URLSearchParams``."""
    return {str(cle): str(valeur) for cle, valeur in (requete or {}).items()}


def _vers_json(valeur):
    if isinstance(valeur, ObjetJS):
        return {"$ref": valeur._ref}
    if isinstance(valeur, Donnee) and getattr(valeur, "_ref", None) is not None:
        return {"$ref": valeur._ref}
    # Une énumération du modèle part par sa valeur, celle que le portage
    # connaît. Un objet du modèle, lui, ne part pas : le portage a les siens, et
    # des champs recopiés au hasard de leurs noms s'y liraient de travers.
    if isinstance(valeur, enum.Enum):
        return valeur.value
    if isinstance(valeur, float) and not math.isfinite(valeur):
        return {"$nombre": "NaN" if valeur != valeur else ("Infinity" if valeur > 0 else "-Infinity")}
    if isinstance(valeur, dict):
        return {str(k): _vers_json(v) for k, v in valeur.items()}
    if isinstance(valeur, (list, tuple, set, frozenset)):
        return [_vers_json(v) for v in valeur]
    return valeur


@lru_cache(maxsize=None)
def site() -> Site:
    """Le site de ce processus : lancé à la première demande, fermé avec lui."""
    ouvert = Site()
    atexit.register(ouvert.fermer)
    return ouvert


def rendre(chemin: str, requete: dict | None = None) -> tuple[str, str]:
    """Le titre et le corps d'une page du site : ``site().rendre``."""
    return site().rendre(chemin, requete)


def module(nom: str) -> Module:
    """Un module du portage, ``moteur/js/<nom>.js`` : ``site().module``."""
    return site().module(nom)
