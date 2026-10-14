#!/usr/bin/env python3
"""La carte des jumeaux : chaque paire Python–JavaScript, tout ce qui en dépend,
et ce que les tests de concordance en exécutent.

    python scripts/jumeaux.py                # la carte, de la paire la plus facile à retirer à la plus difficile
    python scripts/jumeaux.py releve_lu      # une paire : chaque dépendant, à sa ligne
    python scripts/jumeaux.py --couverture   # mesure ce que les tests de concordance exécutent (quelques minutes)
    python scripts/jumeaux.py --json carte.json

L'action 161 retire les doublons entre le Python et le JavaScript, une paire
par étape, sans rien casser. Avant de supprimer une ligne, il faut savoir tout
ce qui la lit ; les imports n'en disent qu'une partie, et ce script relève six
sortes de dépendants :

- les **imports Python**, lus dans l'arbre syntaxique de chaque fichier de
  ``src/``, ``scripts/``, ``tests/`` et des hooks, y compris ceux qu'une
  fonction fait en cours de route, puis leur fermeture : quels scripts et quels
  tests atteignent le module, et s'il est atteint par la fabrique (les étapes
  de ``regenerer.py``) ou par le coût (``retraite_notionnelle.cout``) ;
- les **imports JavaScript**, depuis ``index.html`` : le site charge-t-il le
  jumeau, ou seulement le précharge-t-il, et quels modules ou tests le lisent ;
- les **chargements par nom** : un fichier qu'une chaîne du code nomme — un
  script qu'un test charge ou lance par son chemin, un module du portage que le
  Python fait lire à node — ou que ``site().module("pages")`` désigne ;
- les **fiches** de règles, dont le champ ``code`` nomme les fonctions de la
  règle dans les deux moteurs (``tests/test_univers.py`` vérifie celles de la
  proposition) ;
- les **chiffres ancrés** de la prose, dont la sonde charge le module que
  l'ancre nomme (``de=retraite_notionnelle.saisie``) ;
- les **mentions** : tout fichier texte qui cite le fichier ou le module,
  rangé en récit, qui garde ce qu'il disait à sa date, ou en texte à tenir,
  d'après son dossier (``RECITS``). Un nom seul, ``primes.py``, qui peut
  désigner plusieurs fichiers, est compté pour chacun et dit ambigu.

Une paire est déclarée par l'en-tête du fichier JavaScript (« Portage de
``src/…/x.py`` », « Jumeau de », « Copie de », « Lecteur de ») ; à défaut,
elle se forme par le nom. Le classement suppose qu'on retire le jumeau Python,
le cas ordinaire, puisque le navigateur n'exécute que le JavaScript : d'abord
ce que ni le coût ni la fabrique n'atteignent, puis par nombre de scripts, de
fiches et d'ancres, de tests, et par taille. Une paire dont le site ne charge
pas le JavaScript le dit, et se tranche à sa relecture.

``--couverture`` rejoue les tests de concordance, sans mémoire de calcul :
``node --test tests/js/``, les tests pytest qui confrontent les deux moteurs
(``-k``, par défaut ceux qui disent « javascript », « portage » ou
« jumeau »), et la fabrication des témoins, que le JavaScript retrouve. Il
relève les lignes exécutées : celles du JavaScript par la couverture de V8
(``NODE_V8_COVERAGE``), celles du Python par ``sys.monitoring`` (Python 3.12
et après). Une ligne qu'aucun d'eux n'exécute n'a jamais été confrontée à son
jumeau. Une ligne du JavaScript compte si elle porte du code : ni blanche, ni
commentaire ; une ligne du Python, si elle porte une instruction. La mesure se
garde dans ``.cache/jumeaux/``, avec le commit où elle a été prise, et la carte
la reprend tant qu'on ne la refait pas.
"""

from __future__ import annotations

import argparse
import ast
import atexit
import bisect
import json
import os
import re
import subprocess
import sys
import tempfile
import types
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote, urlparse

import yaml

RACINE = Path(__file__).resolve().parents[1]
PAQUET = "src/retraite_notionnelle/"
PORTAGE = "moteur/js/"
INDEX = "index.html"
REGLES = "data/reference/regles/"
COUT = "src/retraite_notionnelle/cout.py"
REGENERER = "scripts/regenerer.py"
MESURE = RACINE / ".cache" / "jumeaux" / "couverture.json"
#: Les tests pytest de concordance : ceux qui confrontent les deux moteurs se
#: nomment ainsi (``test_le_portage_javascript_…``) ; ceux de ce script, non.
TESTS_DE_CONCORDANCE = "(javascript or portage or jumeau) and not test_jumeaux"

#: Les dossiers des récits : vrais à leur date, ils gardent ce qu'ils citent
#: (``data/reference/prose/zones.yaml``). Le reste est à tenir.
RECITS = ("docs/archives/", "docs/decisions/", "docs/architecture/versions/",
          "docs/feuille_de_route/", "docs/feuille_de_route.md",
          "data/reference/legislation/journal_de_veille/")
#: Ce script et son test nomment des modules pour l'exemple : ils ne comptent
#: parmi les dépendants d'aucun jumeau.
OUTILS = ("scripts/jumeaux.py", "tests/test_jumeaux.py")
#: Ce que la recherche des mentions ne lit pas : les fichiers fabriqués, les
#: sources brutes, les outils d'interface installés, les captures.
HORS_DES_MENTIONS = ("tests/temoins/", "data/derive/", "data/brut/", ".claude/skills/",
                     "shots/", "moteur/donnees.json") + OUTILS
TEXTES = (".py", ".js", ".mjs", ".md", ".yaml", ".yml", ".html", ".sh", ".toml",
          ".json", ".txt", ".cfg")

CHARGEUR = getattr(yaml, "CSafeLoader", yaml.SafeLoader)

#: La phrase d'un en-tête JavaScript qui nomme son jumeau Python.
DECLARATION = re.compile(
    r"\b(?:Portage|portage|PORT|Jumeau|jumeau|Copie|copie|Lecteur|lecteur)\s+"
    r"(d'une\s+partie\s+)?(?:de|DE)\s+`{1,2}([\w./-]+\.py)`{1,2}")
IMPORT_JS = re.compile(r"""(?:\bimport\s*\(\s*|\bfrom\s*|\bimport\s+)(["'`])([^"'`\n$]+?\.m?js)\1""")
BALISE = re.compile(r"<(link|script)\b([^>]*)>", re.I)
ATTRIBUT = re.compile(r"""\b(rel|href|src|type)\s*=\s*["']([^"']*)["']""", re.I)
#: Un chemin de fichier de code, ou un module du paquet nommé par points.
JETON = re.compile(r"(?<![\w/.-])((?:\.\.?/)*(?:[\w-]+/)*[\w-]+\.(?:py|mjs|js))\b"
                   r"|(?<![\w.])(retraite_notionnelle(?:\.\w+)+)")
ANCRE = re.compile(r"<!--chiffre:(.*?)-->")
DE = re.compile(r"[?&(]de=([^&)]+)")
ETAPE = re.compile(r'Etape\(\s*"[^"]*",\s*"([\w.]+\.py)"')


def _ligne(debuts: list[int], position: int) -> int:
    """La ligne (comptée depuis 1) d'une position, sur la table des débuts de ligne."""
    return bisect.bisect_right(debuts, position)


def _debuts(texte: str) -> list[int]:
    debuts = [0]
    for trouve in re.finditer("\n", texte):
        debuts.append(trouve.end())
    return debuts


def _lire(racine: Path, chemin: str) -> str:
    try:
        return (racine / chemin).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _nombre_de_lignes(texte: str) -> int:
    return texte.count("\n") + (1 if texte and not texte.endswith("\n") else 0)


def fichiers_suivis(racine: Path = RACINE) -> list[str]:
    """Les fichiers du dépôt, suivis ou nouveaux, sans ce que git ignore."""
    try:
        sortie = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=racine, capture_output=True, check=True).stdout.decode("utf-8")
        chemins = {c for c in sortie.split("\0") if c}
    except (OSError, subprocess.CalledProcessError):
        chemins = {p.relative_to(racine).as_posix() for p in racine.rglob("*")
                   if p.is_file() and ".git" not in p.parts}
    return sorted(c for c in chemins if (racine / c).is_file())


# -- le Python ------------------------------------------------------------------


@dataclass(frozen=True)
class Module:
    chemin: str
    #: Le nom qu'un import lui donne : ``retraite_notionnelle.web.releve_lu``,
    #: ``construire_donnees``, ``fetch.lecture_pdf``, ``outils_web``.
    nom: str
    #: ``modele`` (``src/``), ``script`` (``scripts/`` et les hooks) ou ``test``.
    sorte: str


#: Où un import se cherche, comme ``sys.path`` le ferait : un script ou un test
#: se lance depuis son dossier (``None``), puis ajoute ceux des scripts et des
#: sources ; un module du paquet ne voit que ``src/``.
CHEMINS_D_IMPORT = {"modele": ("src",), "script": (None, "scripts", "scripts/fetch", "src"),
                    "test": (None, "tests", "scripts", "scripts/fetch", "src")}


def modules_python(fichiers: list[str]) -> dict[str, Module]:
    sortie = {}
    for chemin in fichiers:
        if not chemin.endswith(".py"):
            continue
        morceaux = chemin[:-3].split("/")
        if morceaux[0] == "src" and len(morceaux) > 1:
            nom, sorte = morceaux[1:], "modele"
            if nom[-1] == "__init__":
                nom = nom[:-1]
        elif morceaux[0] == "scripts":
            nom, sorte = morceaux[1:], "script"
        elif morceaux[:2] == [".claude", "hooks"]:
            nom, sorte = morceaux[2:], "script"
        elif morceaux[0] == "tests":
            nom, sorte = morceaux[1:], "test"
        else:
            continue
        sortie[chemin] = Module(chemin, ".".join(nom), sorte)
    return sortie


def _docstrings(arbre: ast.AST) -> set[int]:
    """Les identifiants des chaînes qui sont des docstrings."""
    ids = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            corps = noeud.body
            if (corps and isinstance(corps[0], ast.Expr) and isinstance(corps[0].value, ast.Constant)
                    and isinstance(corps[0].value.value, str)):
                ids.add(id(corps[0].value))
    return ids


class Python:
    """Les imports du Python, et ce que chaque fichier fait lire à node."""

    def __init__(self, racine: Path, fichiers: list[str], suffixes: dict[str, set[str]]):
        self.modules = modules_python(fichiers)
        self.suffixes = suffixes
        #: Les noms pointés, pour les ancres et les mentions : ceux du paquet
        #: (``retraite_notionnelle.saisie``) et ceux des scripts (``fetch.ines``).
        self.index: dict[str, dict[str, str]] = {sorte: {} for sorte in CHEMINS_D_IMPORT}
        for module in self.modules.values():
            self.index[module.sorte].setdefault(module.nom, module.chemin)
        self.aretes: dict[str, list[tuple[str, int]]] = {}
        #: Les fichiers Python qu'une chaîne du code nomme par leur chemin : un
        #: script qu'un test charge ou lance. Ils ne comptent pas dans la
        #: fermeture, où un message qui cite un script ferait tout atteindre.
        self.par_chemin: dict[str, list[tuple[str, int, str]]] = {}
        #: Les fichiers JavaScript que chaque fichier fait lire à node, par
        #: ``module("…")`` ou une chaîne qui les nomme : (fichier JS, ligne, texte).
        self.vers_node: dict[str, list[tuple[str, int, str]]] = {}
        for module in self.modules.values():
            self._lire(racine, module)
        self.parents = {chemin: self._parents(module) for chemin, module in self.modules.items()}
        self.importe_par: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for source, aretes in self.aretes.items():
            for cible, ligne in sorted(set(aretes)):
                self.importe_par[cible].append((source, ligne))
        #: Pour chaque fichier, les scripts et les tests qui l'atteignent.
        self.atteint_par: dict[str, set[str]] = defaultdict(set)
        for module in self.modules.values():
            if module.sorte in ("script", "test"):
                for chemin in self.fermeture([module.chemin]) - {module.chemin}:
                    self.atteint_par[chemin].add(module.chemin)

    def resoudre(self, nom: str, depuis: Module) -> str | None:
        """Le fichier qu'un import désigne, le nom le plus long d'abord : un
        sous-module, puis le module dont on importe une fonction."""
        morceaux = nom.split(".")
        for base in CHEMINS_D_IMPORT[depuis.sorte]:
            base = base or depuis.chemin.rpartition("/")[0]
            for taille in range(len(morceaux), 0, -1):
                relatif = "/".join(morceaux[:taille])
                for candidat in (f"{base}/{relatif}.py", f"{base}/{relatif}/__init__.py"):
                    if candidat in self.modules:
                        return candidat
        return None

    def _parents(self, module: Module) -> list[str]:
        """Les paquets qu'importer le module exécute d'abord, leurs ``__init__.py``."""
        if module.sorte != "modele":
            return []
        # Le nom d'un ``__init__.py`` est celui de son paquet : dans les deux cas,
        # les parents sont les noms plus courts.
        morceaux = module.nom.split(".")[:-1]
        return [c for c in (self.index["modele"].get(".".join(morceaux[:n]))
                            for n in range(1, len(morceaux) + 1)) if c]

    def _lire(self, racine: Path, module: Module) -> None:
        texte = _lire(racine, module.chemin)
        self.aretes[module.chemin], self.par_chemin[module.chemin] = [], []
        self.vers_node[module.chemin] = []
        try:
            arbre = ast.parse(texte)
        except SyntaxError:
            return
        noms = []
        docstrings = _docstrings(arbre)
        vers_node, par_chemin = [], []
        for noeud in ast.walk(arbre):
            if isinstance(noeud, ast.Import):
                noms += [(alias.name, noeud.lineno) for alias in noeud.names]
            elif isinstance(noeud, ast.ImportFrom):
                base = noeud.module or ""
                if noeud.level:
                    paquet = module.nom.split(".")
                    if not module.chemin.endswith("__init__.py"):
                        paquet = paquet[:-1]
                    paquet = paquet[: len(paquet) - (noeud.level - 1)]
                    base = ".".join(paquet + ([noeud.module] if noeud.module else []))
                noms += [(f"{base}.{alias.name}" if base else alias.name, noeud.lineno)
                         for alias in noeud.names]
            elif isinstance(noeud, ast.Call):
                fonction = noeud.func
                nom_appele = (fonction.attr if isinstance(fonction, ast.Attribute)
                              else fonction.id if isinstance(fonction, ast.Name) else "")
                if (nom_appele == "module" and noeud.args and isinstance(noeud.args[0], ast.Constant)
                        and isinstance(noeud.args[0].value, str)):
                    nom_js = noeud.args[0].value
                    for candidat in (nom_js, nom_js.replace("_", "-")):
                        if (racine / PORTAGE / f"{candidat}.js").is_file():
                            vers_node.append((f"{PORTAGE}{candidat}.js", noeud.lineno,
                                              f'module("{nom_js}")'))
                            break
            elif (isinstance(noeud, ast.Constant) and isinstance(noeud.value, str)
                  and id(noeud) not in docstrings):
                for _, jeton in _jetons(noeud.value):
                    cibles = self.suffixes.get(re.sub(r"^(?:\.\.?/)+", "", jeton), set())
                    if len(cibles) != 1:
                        continue
                    cible = next(iter(cibles))
                    if cible == module.chemin:
                        continue
                    (par_chemin if cible.endswith(".py") else vers_node).append(
                        (cible, noeud.lineno, jeton))
        resolus = []
        for nom, ligne in noms:
            chemin = self.resoudre(nom, module)
            if chemin and chemin != module.chemin:
                resolus.append((chemin, ligne))
        self.aretes[module.chemin] = resolus
        self.vers_node[module.chemin] = vers_node
        self.par_chemin[module.chemin] = par_chemin

    def fermeture(self, departs) -> set[str]:
        vus, pile = set(), list(departs)
        while pile:
            chemin = pile.pop()
            if chemin in vus:
                continue
            vus.add(chemin)
            pile.extend(cible for cible, _ in self.aretes.get(chemin, ()))
            pile.extend(self.parents.get(chemin, ()))
        return vus


# -- le JavaScript --------------------------------------------------------------


class JavaScript:
    """Le graphe des modules du portage, depuis la page du site."""

    def __init__(self, racine: Path, fichiers: list[str]):
        self.aretes: dict[str, list[tuple[str, int]]] = {}
        sources = [c for c in fichiers if c.endswith((".js", ".mjs"))
                   and (c.startswith(("moteur/", "tests/js/", "src/")))]
        for chemin in sources + [INDEX]:
            self.aretes[chemin] = self._imports(racine, chemin)
        self.importe_par: dict[str, list[tuple[str, int]]] = defaultdict(list)
        for source, aretes in self.aretes.items():
            for cible, ligne in sorted(set(aretes)):
                self.importe_par[cible].append((source, ligne))
        texte = _lire(racine, INDEX)
        self.precharges: set[str] = set()
        for balise, attributs in BALISE.findall(texte):
            valeurs = {k.lower(): v for k, v in ATTRIBUT.findall(attributs)}
            if balise.lower() == "link" and valeurs.get("rel") == "modulepreload":
                self.precharges.add(os.path.normpath(valeurs.get("href", "")).replace(os.sep, "/"))
        self.site = self.fermeture([INDEX]) - {INDEX}

    @staticmethod
    def _imports(racine: Path, chemin: str) -> list[tuple[str, int]]:
        texte = _lire(racine, chemin)
        debuts = _debuts(texte)
        dossier = os.path.dirname(chemin)
        sortie = [(trouve.group(2), _ligne(debuts, trouve.start()))
                  for trouve in IMPORT_JS.finditer(texte)]
        if chemin.endswith(".html"):
            for trouve in BALISE.finditer(texte):
                valeurs = {k.lower(): v for k, v in ATTRIBUT.findall(trouve.group(2))}
                if trouve.group(1).lower() == "script" and valeurs.get("type") == "module" \
                        and valeurs.get("src"):
                    sortie.append((valeurs["src"], _ligne(debuts, trouve.start())))
        resolus = []
        for cible, ligne in sortie:
            normal = os.path.normpath(os.path.join(dossier, cible)).replace(os.sep, "/")
            if (racine / normal).is_file():
                resolus.append((normal, ligne))
        return resolus

    def fermeture(self, departs) -> set[str]:
        vus, pile = set(), list(departs)
        while pile:
            chemin = pile.pop()
            if chemin in vus:
                continue
            vus.add(chemin)
            pile.extend(cible for cible, _ in self.aretes.get(chemin, ()))
        return vus


# -- les paires -----------------------------------------------------------------


@dataclass(frozen=True)
class Paire:
    python: str
    javascript: str
    #: La phrase de l'en-tête qui déclare la paire ; vide si elle se forme par le nom.
    declaration: str
    partielle: bool

    @property
    def nom(self) -> str:
        return court(self.python)


def court(chemin: str) -> str:
    """Un chemin sans le préfixe de son dossier : ``web/releve_lu.py``, ``droit/releve.js``."""
    for prefixe in (PAQUET, PORTAGE):
        if chemin.startswith(prefixe):
            return chemin[len(prefixe):]
    return chemin


def en_tete(texte: str) -> str:
    """Le premier bloc de commentaire d'un fichier JavaScript, en une ligne."""
    lignes = texte.split("\n")[:15]
    morceaux = []
    for ligne in lignes:
        net = re.sub(r"^\s*(/\*\*?|\*/|\*)\s?", "", ligne)
        morceaux.append(net)
        if "*/" in ligne:
            break
    return " ".join(morceaux)


def declaration(racine: Path, texte: str) -> tuple[str, str, bool] | None:
    """Le jumeau Python qu'un en-tête déclare : (chemin, phrase, partielle)."""
    trouve = DECLARATION.search(en_tete(texte))
    if not trouve:
        return None
    nom = trouve.group(2)
    for candidat in ((nom,) if nom.startswith(("src/", "scripts/")) else (PAQUET + nom, "scripts/" + nom)):
        if (racine / candidat).is_file():
            return candidat, trouve.group(0), bool(trouve.group(1))
    return nom, trouve.group(0), bool(trouve.group(1))


def _par_le_nom(racine: Path, chemin_js: str) -> str | None:
    relatif = chemin_js[len(PORTAGE):-3]
    dossier, _, base = relatif.rpartition("/")
    base = base.replace("-", "_")
    if dossier:
        candidats = [f"{PAQUET}{dossier}/{base}.py"]
    else:
        candidats = [f"{PAQUET}{sous}{base}.py"
                     for sous in ("", "donnees/", "moteur/", "noyau/", "web/")]
        if base.startswith("scenario_"):
            candidats.append(f"{PAQUET}scenarios/{base[len('scenario_'):]}.py")
    return next((c for c in candidats if (racine / c).is_file()), None)


def paires(racine: Path, fichiers: list[str]) -> tuple[list[Paire], list[tuple[str, str]]]:
    """Les paires du dépôt, et les déclarations qui nomment un fichier absent."""
    sortie, mortes = [], []
    for chemin in fichiers:
        if not (chemin.startswith(PORTAGE) and chemin.endswith(".js")):
            continue
        declaree = declaration(racine, _lire(racine, chemin))
        if declaree:
            python, phrase, partielle = declaree
            if (racine / python).is_file():
                sortie.append(Paire(python, chemin, phrase, partielle))
            else:
                mortes.append((chemin, phrase))
            continue
        python = _par_le_nom(racine, chemin)
        if python:
            sortie.append(Paire(python, chemin, "", False))
    return sorted(sortie, key=lambda p: p.python), mortes


# -- ce qui nomme le code : fiches, ancres, mentions ----------------------------


def index_des_suffixes(fichiers: list[str]) -> dict[str, set[str]]:
    """Chaque fin de chemin d'un fichier de code, vers les fichiers qu'elle peut
    désigner : ``releve_lu.py``, ``web/releve_lu.py``, ``src/…/web/releve_lu.py``."""
    suffixes: dict[str, set[str]] = defaultdict(set)
    for chemin in fichiers:
        if chemin.endswith((".py", ".js", ".mjs")):
            morceaux = chemin.split("/")
            for debut in range(len(morceaux)):
                suffixes["/".join(morceaux[debut:])].add(chemin)
    return suffixes


class Resolveur:
    """Le fichier qu'un jeton désigne : un chemin, entier ou par sa fin, ou un
    module nommé par points."""

    def __init__(self, suffixes: dict[str, set[str]], python: Python):
        self.suffixes = suffixes
        self.python = python

    def fichiers(self, jeton: str) -> set[str]:
        """Les fichiers qu'un jeton peut désigner. Un nom pointé se lit du plus
        long au plus court, ``….releve_lu.lire_releve`` désignant le module ;
        un paquet ne répond qu'à son nom entier, sans quoi un module disparu
        se prendrait pour le paquet qui le portait."""
        jeton = re.sub(r"^(?:\.\.?/)+", "", jeton)
        if jeton.endswith((".py", ".js", ".mjs")):
            return set(self.suffixes.get(jeton, ()))
        morceaux = jeton.split(".")
        for taille in range(len(morceaux), 0, -1):
            prefixe = ".".join(morceaux[:taille])
            for espace in ("modele", "script"):
                chemin = self.python.index[espace].get(prefixe)
                if chemin and (taille == len(morceaux) or not chemin.endswith("__init__.py")):
                    return {chemin}
        return set()


@dataclass(frozen=True)
class Renvoi:
    """Un endroit qui nomme un fichier de code."""
    fichier: str
    ligne: int
    texte: str
    ambigu: bool = False

    @property
    def recit(self) -> bool:
        return self.fichier.startswith(RECITS)


def _jetons(texte: str):
    for trouve in JETON.finditer(texte):
        yield trouve.start(), trouve.group(1) or trouve.group(2)


def code_des_fiches(racine: Path, fichiers: list[str], resolveur: Resolveur):
    """Ce que le champ ``code`` de chaque fiche nomme : {fichier: [Renvoi]}, et
    les noms qui ne désignent aucun fichier."""
    sortie: dict[str, list[Renvoi]] = defaultdict(list)
    mortes = []
    for chemin in fichiers:
        if not (chemin.startswith(REGLES) and chemin.endswith(".yaml")):
            continue
        texte = _lire(racine, chemin)
        try:
            donnees = yaml.load(texte, Loader=CHARGEUR)
        except yaml.YAMLError:
            continue
        code = donnees.get("code") if isinstance(donnees, dict) else None
        if not isinstance(code, dict):
            continue
        debuts = _debuts(texte)
        depuis = max(texte.find("\ncode:"), 0)
        for moteur in ("python", "javascript"):
            if code.get(moteur) is None:
                continue
            aplati = json.dumps(code[moteur], ensure_ascii=False, default=str)
            for _, jeton in _jetons(aplati):
                position = texte.find(jeton, depuis)
                ligne = _ligne(debuts, position if position >= 0 else depuis + 1)
                cibles = resolveur.fichiers(jeton)
                if not cibles:
                    mortes.append(Renvoi(chemin, ligne, jeton))
                for cible in cibles:
                    sortie[cible].append(Renvoi(chemin, ligne, jeton, len(cibles) > 1))
    return sortie, mortes


def ancres(racine: Path, fichiers: list[str], resolveur: Resolveur):
    """Les chiffres ancrés dont la sonde charge un module par son nom :
    {fichier: [Renvoi]}, et ceux qui nomment un module introuvable."""
    sortie: dict[str, list[Renvoi]] = defaultdict(list)
    mortes = []
    for chemin in fichiers:
        if not chemin.endswith(".md"):
            continue
        texte = _lire(racine, chemin)
        if "<!--chiffre:" not in texte:
            continue
        debuts = _debuts(texte)
        for trouve in ANCRE.finditer(texte):
            for de in DE.findall(trouve.group(1)):
                if de.isdigit():
                    continue
                cibles = resolveur.fichiers(de)
                renvoi = Renvoi(chemin, _ligne(debuts, trouve.start()), de)
                if not cibles and ("retraite_notionnelle" in de or de.endswith(".js")):
                    mortes.append(renvoi)
                for cible in cibles:
                    sortie[cible].append(renvoi)
    return sortie, mortes


def mentions(racine: Path, fichiers: list[str], resolveur: Resolveur, cibles: set[str]):
    """Chaque fichier texte qui nomme l'un des fichiers ``cibles`` : {cible: [Renvoi]}."""
    sortie: dict[str, list[Renvoi]] = defaultdict(list)
    for chemin in fichiers:
        if not chemin.endswith(TEXTES) or chemin.startswith(HORS_DES_MENTIONS):
            continue
        texte = _lire(racine, chemin)
        debuts = None
        for position, jeton in _jetons(texte):
            trouves = resolveur.fichiers(jeton)
            utiles = (trouves & cibles) - {chemin}
            if not utiles:
                continue
            if debuts is None:
                debuts = _debuts(texte)
            ligne = _ligne(debuts, position)
            for cible in utiles:
                sortie[cible].append(Renvoi(chemin, ligne, jeton, len(trouves) > 1))
    return sortie


# -- la carte -------------------------------------------------------------------


class Carte:
    """Les paires du dépôt et tout ce qui en dépend, calculés une fois."""

    def __init__(self, racine: Path = RACINE):
        self.racine = racine
        self.fichiers = fichiers_suivis(racine)
        suffixes = index_des_suffixes(self.fichiers)
        self.python = Python(racine, self.fichiers, suffixes)
        self.js = JavaScript(racine, self.fichiers)
        self.paires, self.declarations_mortes = paires(racine, self.fichiers)
        self.resolveur = Resolveur(suffixes, self.python)
        self.fiches, self.fiches_mortes = code_des_fiches(racine, self.fichiers, self.resolveur)
        self.ancres, self.ancres_mortes = ancres(racine, self.fichiers, self.resolveur)
        jumeaux = {p.python for p in self.paires} | {p.javascript for p in self.paires}
        self.mentions = mentions(racine, self.fichiers, self.resolveur, jumeaux)
        fabrique = [REGENERER] + [f"scripts/{nom}" for nom in
                                  ETAPE.findall(_lire(racine, REGENERER))]
        self.fabrique = self.python.fermeture(c for c in fabrique if c in self.python.modules)
        self.cout = self.python.fermeture([COUT]) if COUT in self.python.modules else set()
        self.par_chemin: dict[str, list[Renvoi]] = defaultdict(list)
        for source, appels in self.python.par_chemin.items():
            for cible, ligne, texte in appels if source not in OUTILS else ():
                self.par_chemin[cible].append(Renvoi(source, ligne, texte))
        #: Ce que le Python fait lire à node : le fichier qu'il nomme, puis tout
        #: ce que ce fichier importe (un script de ``tests/js/``, ``pages.js``…).
        self.vers_node: dict[str, list[Renvoi]] = defaultdict(list)
        self.par_node: dict[str, set[str]] = defaultdict(set)
        for source, appels in self.python.vers_node.items():
            for cible, ligne, texte in appels if source not in OUTILS else ():
                self.vers_node[cible].append(Renvoi(source, ligne, texte))
                for atteint in self.js.fermeture([cible]) - {cible}:
                    self.par_node[atteint].add(source)
        self.lignes = {c: _nombre_de_lignes(_lire(racine, c)) for c in jumeaux}
        self.mesure = lire_la_mesure()

    def python_seul(self) -> list[str]:
        apparies = {p.python for p in self.paires}
        return [c for c, m in self.python.modules.items()
                if m.sorte == "modele" and c not in apparies and not c.endswith("__init__.py")]

    def javascript_seul(self) -> list[str]:
        apparies = {p.javascript for p in self.paires}
        return [c for c in self.fichiers if c.startswith(PORTAGE) and c.endswith(".js")
                and c not in apparies]

    def fiche(self, paire: Paire) -> dict:
        """Tout ce qui dépend des deux jumeaux d'une paire."""
        py, js = paire.python, paire.javascript
        atteint = self.python.atteint_par.get(py, set())
        cote_python = {
            "importe_par": sorted(self.python.importe_par.get(py, [])),
            "scripts": sorted(c for c in atteint if self.python.modules[c].sorte == "script"),
            "tests": sorted(c for c in atteint if self.python.modules[c].sorte == "test"),
            "fabrique": py in self.fabrique,
            "cout": py in self.cout,
            "fiches": self.fiches.get(py, []),
            "ancres": self.ancres.get(py, []),
            "charge_par_chemin": self.par_chemin.get(py, []),
            "mentions": self.mentions.get(py, []),
        }
        cote_javascript = {
            "importe_par": sorted(self.js.importe_par.get(js, [])),
            "site": js in self.js.site,
            "precharge": js in self.js.precharges,
            "charge_par_nom": self.vers_node.get(js, []),
            "charge_par_un_autre_module": sorted(self.par_node.get(js, set())),
            "fiches": self.fiches.get(js, []),
            "ancres": self.ancres.get(js, []),
            "mentions": self.mentions.get(js, []),
        }
        for cote, nommants in ((cote_python, ("fiches", "ancres", "charge_par_chemin")),
                               (cote_javascript, ("fiches", "ancres", "charge_par_nom"))):
            noms = {r.fichier for cle in nommants for r in cote[cle]}
            importeurs = {source for source, _ in cote["importe_par"]}
            cote["noms"] = sorted(noms)
            cote["mentions_a_tenir"] = sorted({r.fichier for r in cote["mentions"]
                                               if not r.recit} - noms - importeurs)
        return {
            "python": py,
            "javascript": js,
            "declaration": paire.declaration,
            "partielle": paire.partielle,
            "lignes": {"python": self.lignes[py], "javascript": self.lignes[js]},
            "cote_python": cote_python,
            "cote_javascript": cote_javascript,
            "couverture": self.couverture(paire),
        }

    def couverture(self, paire: Paire) -> dict | None:
        if not self.mesure:
            return None
        python = self.mesure.get("python", {}).get(paire.python)
        javascript = self.mesure.get("javascript", {}).get(paire.javascript)
        sortie = {}
        if python:
            vues = set(python["executees"])
            sortie["python"] = {"lignes": len(python["executables"]),
                                "executees": len(vues),
                                "jamais": [n for n in python["executables"] if n not in vues]}
        if javascript:
            vues = set(javascript["couvertes"])
            sortie["javascript"] = {"lignes": len(javascript["comptees"]),
                                    "executees": len(vues),
                                    "jamais": [n for n in javascript["comptees"] if n not in vues]}
        return sortie

    def classement(self) -> list[dict]:
        """Les fiches des paires, de la plus facile à retirer côté Python à la plus difficile."""
        return sorted((self.fiche(p) for p in self.paires), key=difficulte)


def difficulte(fiche: dict) -> tuple:
    cote = fiche["cote_python"]
    return (cote["cout"], cote["fabrique"], len(cote["scripts"]), len(cote["noms"]),
            len(cote["tests"]), fiche["lignes"]["python"], fiche["python"])


# -- la couverture --------------------------------------------------------------


def lignes_executables(texte: str, nom: str = "<source>") -> set[int]:
    """Les lignes d'un fichier Python qui portent une instruction."""
    try:
        code = compile(texte, nom, "exec", dont_inherit=True)
    except SyntaxError:
        return set()
    lignes, pile = set(), [code]
    while pile:
        objet = pile.pop()
        lignes.update(ligne for _, _, ligne in objet.co_lines() if ligne)
        pile.extend(k for k in objet.co_consts if isinstance(k, types.CodeType))
    return lignes


def _utf16(texte: str) -> int:
    return len(texte.encode("utf-16-le")) // 2


def _portees(source: str) -> tuple[list[tuple[int, int] | None], list[int]]:
    """Pour chaque ligne : les bornes de son code, en unités UTF-16 comme les
    décalages de V8, sans les blancs autour ; ``None`` si elle n'en porte pas."""
    portees, debuts, position = [], [], 0
    for texte in source.split("\n"):
        debuts.append(position)
        largeur = _utf16(texte)
        net = texte.strip()
        if net and not net.startswith(("//", "/*", "*")):
            gauche = _utf16(texte[: len(texte) - len(texte.lstrip())])
            droite = largeur - _utf16(texte[len(texte.rstrip()):])
            portees.append((position + gauche, position + droite))
        else:
            portees.append(None)
        position += largeur + 1
    return portees, debuts


def lignes_de_code_js(source: str) -> set[int]:
    portees, _ = _portees(source)
    return {i + 1 for i, portee in enumerate(portees) if portee}


def lignes_executees_js(source: str, fonctions: list[dict]) -> set[int]:
    """Les lignes de code qu'une couverture de V8 dit exécutées.

    Chaque plage porte le nombre de passages du bloc qu'elle couvre ; les plages
    s'emboîtent, la fonction d'abord, ses blocs ensuite. Une ligne prend le
    compte de la plus intérieure qui la contient en entier."""
    portees, debuts = _portees(source)
    comptes: list[int | None] = [None] * len(portees)
    plages = sorted(((p["startOffset"], p["endOffset"], p["count"])
                     for f in fonctions for p in f.get("ranges", ())),
                    key=lambda p: (p[0], -p[1]))
    for debut, fin, compte in plages:
        rang = max(bisect.bisect_right(debuts, debut) - 1, 0)
        while rang < len(portees) and debuts[rang] < fin:
            portee = portees[rang]
            if portee and portee[0] >= debut and portee[1] <= fin:
                comptes[rang] = compte
            rang += 1
    return {i + 1 for i, compte in enumerate(comptes) if compte}


class Sonde:
    """Les lignes du Python exécutées dans ce processus, par ``sys.monitoring``."""

    def __init__(self, dossier: str | Path):
        self.dossier = Path(dossier)
        self.vues: dict[str, set[int]] = defaultdict(set)
        self.prefixes = (str(RACINE / "src") + os.sep, str(RACINE / "scripts") + os.sep)

    def demarrer(self) -> "Sonde":
        surveillance = sys.monitoring
        self.outil = next(i for i in (surveillance.COVERAGE_ID, 0, 2, 3, 4)
                          if surveillance.get_tool(i) is None)
        surveillance.use_tool_id(self.outil, "jumeaux")
        vues, prefixes, desactiver = self.vues, self.prefixes, surveillance.DISABLE

        def ligne(code, numero):
            # Une ligne vue ne se signale plus : la sonde ne coûte presque rien.
            if code.co_filename.startswith(prefixes):
                vues[code.co_filename].add(numero)
            return desactiver

        surveillance.register_callback(self.outil, surveillance.events.LINE, ligne)
        surveillance.set_events(self.outil, surveillance.events.LINE)
        atexit.register(self.ecrire)
        return self

    def arreter(self) -> None:
        surveillance = sys.monitoring
        surveillance.set_events(self.outil, 0)
        surveillance.register_callback(self.outil, surveillance.events.LINE, None)
        surveillance.free_tool_id(self.outil)
        atexit.unregister(self.ecrire)

    def ecrire(self) -> None:
        self.dossier.mkdir(parents=True, exist_ok=True)
        donnees = {Path(nom).relative_to(RACINE).as_posix(): sorted(lignes)
                   for nom, lignes in self.vues.items()}
        (self.dossier / f"py-{os.getpid()}.json").write_text(json.dumps(donnees), encoding="utf-8")


def lancer(script: str, arguments, sonde: Sonde) -> int:
    """Lance un script du dépôt dans ce processus, sous la sonde."""
    import runpy

    sys.argv = [script, *arguments]
    sys.path.insert(0, str((RACINE / script).parent))
    try:
        runpy.run_path(str(RACINE / script), run_name="__main__")
        code = 0
    except SystemExit as fin:
        code = fin.code if isinstance(fin.code, int) else int(bool(fin.code))
    finally:
        sonde.ecrire()
    return code


#: Le greffon que pytest charge dans chacun de ses processus (``PYTEST_PLUGINS``),
#: et que la fabrication des témoins importe : il ouvre la sonde dès son import.
GREFFON = '''\
import importlib.util, os, sys
_spec = importlib.util.spec_from_file_location("jumeaux", {chemin!r})
_jumeaux = importlib.util.module_from_spec(_spec)
sys.modules["jumeaux"] = _jumeaux
_spec.loader.exec_module(_jumeaux)
SONDE = _jumeaux.Sonde(os.environ["JUMEAUX_SONDE"]).demarrer()


def pytest_unconfigure(config):
    SONDE.ecrire()


def lancer(script, *arguments):
    return _jumeaux.lancer(script, arguments, SONDE)
'''


def lire_v8(dossier: Path, fichiers: list[str], racine: Path = RACINE) -> dict:
    couvertes: dict[str, set[int]] = defaultdict(set)
    sources: dict[str, str] = {}
    for chemin in sorted(dossier.glob("*.json")):
        try:
            donnees = json.loads(chemin.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for script in donnees.get("result", ()):
            adresse = script.get("url", "")
            if not adresse.startswith("file://"):
                continue
            try:
                relatif = Path(unquote(urlparse(adresse).path)).relative_to(racine).as_posix()
            except ValueError:
                continue
            if not relatif.startswith(PORTAGE):
                continue
            if relatif not in sources:
                sources[relatif] = _lire(racine, relatif)
            couvertes[relatif] |= lignes_executees_js(sources[relatif], script.get("functions", ()))
    sortie = {}
    for relatif in fichiers:
        if relatif.startswith(PORTAGE) and relatif.endswith(".js"):
            comptees = lignes_de_code_js(sources.get(relatif) or _lire(racine, relatif))
            sortie[relatif] = {"comptees": sorted(comptees),
                               "couvertes": sorted(couvertes[relatif] & comptees)}
    return sortie


def lire_la_sonde(dossier: Path, fichiers: list[str], racine: Path = RACINE) -> dict:
    vues: dict[str, set[int]] = defaultdict(set)
    for chemin in sorted(dossier.glob("py-*.json")):
        try:
            for relatif, lignes in json.loads(chemin.read_text(encoding="utf-8")).items():
                vues[relatif].update(lignes)
        except (OSError, json.JSONDecodeError):
            continue
    sortie = {}
    for relatif in fichiers:
        if relatif.endswith(".py") and relatif.startswith(("src/", "scripts/")):
            executables = lignes_executables(_lire(racine, relatif), relatif)
            sortie[relatif] = {"executables": sorted(executables),
                               "executees": sorted(vues[relatif] & executables)}
    return sortie


def _tete() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], cwd=RACINE, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def mesurer(expression: str = TESTS_DE_CONCORDANCE) -> dict:
    """Rejoue les tests de concordance sous les deux couvertures, et garde la mesure."""
    if not hasattr(sys, "monitoring"):
        raise SystemExit("--couverture demande Python 3.12 ou après (sys.monitoring)")
    fichiers = fichiers_suivis()
    etapes = []
    with tempfile.TemporaryDirectory() as temporaire:
        dossier = Path(temporaire)
        (dossier / "jumeaux_sonde.py").write_text(
            GREFFON.format(chemin=str(Path(__file__).resolve())), encoding="utf-8")
        environnement = dict(
            os.environ, NODE_V8_COVERAGE=str(dossier / "v8"), JUMEAUX_SONDE=str(dossier / "py"),
            FABRIQUE_SANS_MEMOIRE="1", CALCULS_SANS_MEMOIRE="1", PYTEST_PLUGINS="jumeaux_sonde",
            PYTHONPATH=os.pathsep.join(p for p in (str(dossier), os.environ.get("PYTHONPATH"))
                                       if p))
        commandes = [
            ("les tests JavaScript", ["node", "--test",
                                      *sorted(str(p) for p in (RACINE / "tests" / "js").glob("*.test.js"))]),
            ("les tests pytest de concordance", [sys.executable, "-m", "pytest", "-q", "-k", expression]),
            ("la fabrication des témoins", [sys.executable, "-c",
                                            "import sys, jumeaux_sonde; sys.exit(jumeaux_sonde.lancer("
                                            "'scripts/construire_temoins.py', '--verifier'))"]),
        ]
        for nom, commande in commandes:
            print(f"… {nom}", file=sys.stderr, flush=True)
            try:
                fait = subprocess.run(commande, cwd=RACINE, env=environnement,
                                      capture_output=True, text=True)
            except OSError as erreur:
                print(f"   impossible : {erreur}", file=sys.stderr)
                etapes.append({"nom": nom, "code": None})
                continue
            etapes.append({"nom": nom, "code": fait.returncode})
            if fait.returncode != 0:
                fin = (fait.stdout + fait.stderr).strip().split("\n")[-8:]
                print(f"   rendu {fait.returncode} ; la mesure garde ce qui a tourné :",
                      *("   " + ligne for ligne in fin), sep="\n", file=sys.stderr)
        mesure = {
            "commit": _tete(),
            "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "tests": expression,
            "etapes": etapes,
            "python": lire_la_sonde(dossier / "py", fichiers),
            "javascript": lire_v8(dossier / "v8", fichiers),
        }
    MESURE.parent.mkdir(parents=True, exist_ok=True)
    MESURE.write_text(json.dumps(mesure), encoding="utf-8")
    return mesure


def lire_la_mesure() -> dict | None:
    try:
        return json.loads(MESURE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


# -- l'impression ---------------------------------------------------------------


def _n(nombre: int) -> str:
    return f"{nombre:,}".replace(",", " ")


def plages(numeros) -> str:
    """Des numéros de ligne en plages : « 12-18, 40, 52-60 »."""
    sortie, numeros = [], sorted(numeros)
    debut = precedent = None
    for numero in numeros + [None]:
        if numero is not None and precedent is not None and numero == precedent + 1:
            precedent = numero
            continue
        if debut is not None:
            sortie.append(str(debut) if debut == precedent else f"{debut}-{precedent}")
        debut = precedent = numero
    return ", ".join(sortie)


def _taux(cote: dict | None) -> str:
    if not cote or not cote["lignes"]:
        return "—"
    return f"{100 * cote['executees'] / cote['lignes']:.0f} %"


def _site(cote: dict) -> str:
    return "oui" if cote["site"] else ("préch." if cote["precharge"] else "non")


def _bloque(cote: dict) -> str:
    return "coût" if cote["cout"] else ("fabrique" if cote["fabrique"] else "—")


def imprimer_la_carte(carte: Carte) -> list[str]:
    classement = carte.classement()
    total_py = total_js = 0
    for fiche in classement:
        total_py += fiche["lignes"]["python"]
        total_js += fiche["lignes"]["javascript"]
    large_py = max(len(court(f["python"])) for f in classement) + 2
    large_js = max(len(court(f["javascript"])) for f in classement) + 2
    sortie = [
        f"La carte des jumeaux : {len(classement)} paires, {_n(total_py)} lignes de Python "
        f"et {_n(total_js)} de JavaScript.",
        "Classées de la plus facile à retirer côté Python à la plus difficile ; « bloqué » dit "
        "ce qui l'empêche",
        "tant que le coût et la fabrique calculent en Python.",
        "",
    ]
    entete = (f"{'rang':>4}  {'python':<{large_py}}{'lignes':>6}  {'javascript':<{large_js}}"
              f"{'site':<7}{'bloqué':<9}{'scripts':>7}{'tests':>6}{'noms':>5}{'mentions':>9}"
              f"{'py %':>6}{'js %':>6}")
    sortie += [entete, "-" * len(entete)]
    for rang, fiche in enumerate(classement, 1):
        py, js = fiche["cote_python"], fiche["cote_javascript"]
        couverture = fiche["couverture"] or {}
        sortie.append(
            f"{rang:>4}  {court(fiche['python']):<{large_py}}{_n(fiche['lignes']['python']):>6}  "
            f"{court(fiche['javascript']):<{large_js}}{_site(js):<7}{_bloque(py):<9}"
            f"{len(py['scripts']):>7}{len(py['tests']):>6}{len(py['noms']):>5}"
            f"{len(py['mentions_a_tenir']):>9}"
            f"{_taux(couverture.get('python')):>6}{_taux(couverture.get('javascript')):>6}")
    sortie += [
        "",
        "Pour le jumeau Python : scripts, tests, ceux qui l'atteignent par leurs imports ; noms, "
        "les fichiers qui le nomment",
        "(fiches, chiffres ancrés, chaînes du code) ; mentions, les autres textes à tenir qui le "
        "citent, hors récits.",
        "site : le site charge le JavaScript, ou ne fait que le précharger. py %, js % : les "
        "lignes que les tests de",
        "concordance exécutent.",
        "",
        _ligne_de_mesure(carte),
    ]
    seul = sorted(carte.python_seul(), key=lambda c: -_nombre_de_lignes(_lire(carte.racine, c)))
    sortie += ["", "Python seul, sans jumeau : " + ", ".join(
        f"{court(c)} ({_n(_nombre_de_lignes(_lire(carte.racine, c)))})" for c in seul)]
    sortie += ["JavaScript seul : " + ", ".join(
        f"{court(c)} ({_n(_nombre_de_lignes(_lire(carte.racine, c)))})"
        for c in carte.javascript_seul())]
    mortes = ([f"  {c} : « {phrase} »" for c, phrase in carte.declarations_mortes]
              + [f"  {r.fichier}:{r.ligne} : {r.texte}" for r in carte.fiches_mortes]
              + [f"  {r.fichier}:{r.ligne} : de={r.texte}" for r in carte.ancres_mortes])
    sortie += ["", f"Ce qui nomme un fichier de code introuvable : {len(mortes) or 'rien'}"]
    sortie += mortes
    return sortie


def _ligne_de_mesure(carte: Carte) -> str:
    mesure = carte.mesure
    if not mesure:
        return "Couverture : pas encore mesurée (python scripts/jumeaux.py --couverture)."
    tete = _tete()
    ecart = "" if mesure.get("commit") == tete else " ; le dépôt a bougé depuis"
    rouges = [e["nom"] for e in mesure.get("etapes", ()) if e.get("code") not in (0,)]
    alerte = f" ; en échec : {', '.join(rouges)}" if rouges else ""
    return (f"Couverture mesurée le {mesure.get('date', '?')}, au commit "
            f"{mesure.get('commit', '?')[:10]}{ecart}{alerte}.")


def _renvois(titre: str, renvois: list[Renvoi], limite: int = 40) -> list[str]:
    if not renvois:
        return [f"  {titre} : aucun"]
    sortie = [f"  {titre} ({len(renvois)}) :"]
    for renvoi in sorted(renvois, key=lambda r: (r.recit, r.fichier, r.ligne))[:limite]:
        marques = [m for m, oui in (("récit", renvoi.recit), ("nom ambigu", renvoi.ambigu)) if oui]
        suffixe = f" — {', '.join(marques)}" if marques else ""
        sortie.append(f"    {renvoi.fichier}:{renvoi.ligne}  {renvoi.texte}{suffixe}")
    if len(renvois) > limite:
        sortie.append(f"    … et {len(renvois) - limite} de plus (--json pour tout)")
    return sortie


def imprimer_une_paire(carte: Carte, fiche: dict, rang: int) -> list[str]:
    py, js = fiche["cote_python"], fiche["cote_javascript"]
    sortie = [
        f"{fiche['python']} ({_n(fiche['lignes']['python'])} lignes) ↔ "
        f"{fiche['javascript']} ({_n(fiche['lignes']['javascript'])} lignes) — rang {rang}",
        ("  déclarée par l'en-tête : « " + fiche["declaration"] + " »"
         + (" (jumeau partiel)" if fiche["partielle"] else "")) if fiche["declaration"]
        else "  appariée par le nom : l'en-tête du JavaScript ne déclare pas son jumeau",
        "",
        "Côté Python",
        f"  atteint par le coût : {'oui' if py['cout'] else 'non'} ; par la fabrique : "
        f"{'oui' if py['fabrique'] else 'non'}",
        "  importé par : " + (", ".join(f"{c}:{n}" for c, n in py["importe_par"]) or "personne"),
        f"  scripts qui l'atteignent ({len(py['scripts'])}) : " + (", ".join(py["scripts"]) or "aucun"),
        f"  tests qui l'atteignent ({len(py['tests'])}) : " + (", ".join(
            Path(c).name for c in py["tests"]) or "aucun"),
    ]
    sortie += _renvois("fiches qui le nomment", py["fiches"])
    sortie += _renvois("chiffres ancrés qui le chargent", py["ancres"])
    sortie += _renvois("chaînes du code qui le nomment (un chargement par chemin)",
                       py["charge_par_chemin"])
    sortie += _renvois("mentions", py["mentions"])
    autres = js["charge_par_un_autre_module"]
    sortie += [
        "",
        "Côté JavaScript",
        f"  le site le charge : {'oui' if js['site'] else 'non'}"
        + (" ; index.html le précharge" if js["precharge"] else ""),
        "  importé par : " + (", ".join(f"{c}:{n}" for c, n in js["importe_par"]) or "personne"),
        f"  le Python le fait lire à node par un autre module ({len(autres)}) : "
        + (", ".join(Path(c).name for c in autres) or "aucun"),
    ]
    sortie += _renvois("chargé par nom depuis le Python", js["charge_par_nom"])
    sortie += _renvois("fiches qui le nomment", js["fiches"])
    sortie += _renvois("chiffres ancrés qui le chargent", js["ancres"])
    sortie += _renvois("mentions", js["mentions"])
    sortie += ["", "Couverture par les tests de concordance", "  " + _ligne_de_mesure(carte)]
    for cote, nom in (("python", "Python"), ("javascript", "JavaScript")):
        mesure = (fiche["couverture"] or {}).get(cote)
        if mesure:
            sortie.append(f"  {nom} : {_n(mesure['executees'])} lignes exécutées sur "
                          f"{_n(mesure['lignes'])} ({_taux(mesure)}) ; jamais : "
                          f"{plages(mesure['jamais']) or 'aucune'}")
    return sortie


def chercher(carte: Carte, nom: str) -> list[tuple[int, dict]]:
    """Les paires qu'un nom désigne : module, fichier Python ou JavaScript, entier ou par sa fin."""
    nom = nom.strip().removesuffix(".py").removesuffix(".js")
    cles = {nom, nom.replace(".", "/"), nom.replace("-", "_"), nom.replace("_", "-")}
    sortie = []
    for rang, fiche in enumerate(carte.classement(), 1):
        noms = set()
        for chemin in (fiche["python"], fiche["javascript"]):
            sans = chemin.rsplit(".", 1)[0]
            morceaux = sans.split("/")
            noms |= {"/".join(morceaux[i:]) for i in range(len(morceaux))}
        if cles & noms:
            sortie.append((rang, fiche))
    return sortie


def _vers_json(objet):
    if isinstance(objet, Renvoi):
        return {"fichier": objet.fichier, "ligne": objet.ligne, "texte": objet.texte,
                "ambigu": objet.ambigu, "recit": objet.recit}
    if isinstance(objet, set):
        return sorted(objet)
    raise TypeError(type(objet))


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("noms", nargs="*", help="une paire, par le nom d'un de ses jumeaux")
    analyseur.add_argument("--couverture", action="store_true",
                           help="mesure ce que les tests de concordance exécutent, puis imprime")
    analyseur.add_argument("--tests", default=TESTS_DE_CONCORDANCE,
                           help="l'expression -k des tests pytest de concordance")
    analyseur.add_argument("--json", metavar="FICHIER", help="écrit la carte entière en JSON")
    arguments = analyseur.parse_args(argv)
    if arguments.couverture:
        mesurer(arguments.tests)
    carte = Carte()
    if arguments.json:
        donnees = {
            "paires": carte.classement(),
            "python_seul": carte.python_seul(),
            "javascript_seul": carte.javascript_seul(),
            "declarations_mortes": [{"fichier": c, "phrase": p} for c, p in carte.declarations_mortes],
            "fiches_mortes": carte.fiches_mortes,
            "ancres_mortes": carte.ancres_mortes,
            "mesure": {k: v for k, v in (carte.mesure or {}).items() if k not in ("python", "javascript")},
        }
        Path(arguments.json).write_text(
            json.dumps(donnees, ensure_ascii=False, indent=1, default=_vers_json) + "\n",
            encoding="utf-8")
    if not arguments.noms:
        print("\n".join(imprimer_la_carte(carte)))
        return 0
    trouvees = [t for nom in arguments.noms for t in chercher(carte, nom)]
    if not trouvees:
        print("Aucune paire sous ce nom ; la carte entière : python scripts/jumeaux.py")
        return 1
    print("\n\n".join("\n".join(imprimer_une_paire(carte, fiche, rang)) for rang, fiche in trouvees))
    return 0


if __name__ == "__main__":
    sys.exit(main())
