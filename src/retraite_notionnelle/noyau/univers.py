"""Les univers de droit : des couches posées sur le droit réel.

``docs/architecture.md``, § 4.8 et annexe C.4. Chaque scénario est un univers :
une pile de couches, le droit réel en bas, dans l'ordre que l'univers déclare.
Un fichier par univers dans ``data/reference/univers/``, un par couche dans
``data/reference/couches/``. Le droit réel n'a pas de fichier : c'est la carte
des règles (``data/reference/regles/``), que chaque couche garde, neutralise ou
complète des fiches de la proposition (``regles/proposition/``).

Une couche fait six choses (liste ``operations_de_couche`` du vocabulaire), et
chacune vise une fiche nommée ou un sélecteur (liste ``selecteurs``) :
``{etape: liquider_chaque_regime}``. Elle agit depuis une date (``depuis``),
sur l'univers entier ou sur le seul calcul que nomme la transition posée
au-dessus d'elle (``portee``).

Ce module lit couches et univers, les confronte au contrat C.4, à la carte et
au vocabulaire, et dit de chaque univers ce qu'il ajoute, ce qu'il change, ce
qu'il neutralise dans un calcul, et quelles fiches du droit réel aucune de ses
couches ne décide. Il ne calcule rien : le moteur lit ce qu'il en tire
(``scenarios/univers.py``) et refuse ce qu'il ne sait pas faire.

Les règles de la pile, que :func:`controler` tient :

- le droit réel est en bas de chaque pile, et nulle part ailleurs ; une couche
  n'y paraît qu'une fois ;
- une transition coupe le temps de l'univers : les couches posées au-dessus
  d'elle n'agissent qu'à compter de sa date, et une couche d'un seul calcul
  n'a de sens que sous une transition, dont elle sert le calcul ;
- une couche ne garde, ne neutralise ni ne change une fiche de la proposition
  qu'une couche d'en dessous a ajoutée ;
- deux couches qui touchent la même fiche ne la décident pas autrement l'une
  que l'autre, ne changent pas le même paramètre, ne l'ajoutent pas deux fois :
  c'est ce que l'architecture appelle toucher la même fiche sans ordre déclaré.
"""

from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field
from datetime import date
from functools import lru_cache
from pathlib import Path

from ..config import RACINE_DONNEES, RACINE_PROJET, Parametres
from ..donnees.chargement import charger_yaml
from . import carte, contrats, vocabulaire

UNIVERS = RACINE_DONNEES / "reference" / "univers"
COUCHES = RACINE_DONNEES / "reference" / "couches"
#: La couche du bas de chaque pile : la carte des règles elle-même.
DROIT_REEL = "droit_reel"
#: Le ``depuis`` d'une couche qui agit depuis toujours.
ORIGINE = "origine"
#: Le texte de la proposition, sa référence (§ 3.1).
TEXTE_DE_LA_PROPOSITION = RACINE_PROJET / "README.md"

#: Les opérations qui décident d'une fiche du droit réel (§ 4.8, § 8).
DECISIONS = ("garder", "remplacer_une_version", "neutraliser")
#: Les opérations qui font entrer une fiche de la proposition dans l'univers.
AJOUTS = ("ajouter", "ajouter_une_transition")
#: Les sélecteurs qui se résolvent en fiches, par le champ qu'ils lisent.
#: La contributivité ne se résout pas encore : seul le contexte d'une
#: liquidation la connaît, et elle ne vaut donc que dans un calcul.
SELECTEURS_DE_FICHES = ("etape", "domaine", "face", "regime")


@dataclass(frozen=True)
class Operation:
    """Une opération de couche (contrat C.4, ``operation``)."""

    operation: str
    #: Une fiche nommée, ou un sélecteur : ``("etape", "liquider_chaque_regime")``.
    vise: str | tuple[str, str]
    parametre: str | None = None
    valeur: object = None
    motif: str | None = None

    @classmethod
    def lue(cls, donnee: dict) -> Operation:
        vise = donnee.get("vise")
        if isinstance(vise, dict) and len(vise) == 1:
            vise = next(iter(vise.items()))
        return cls(donnee.get("operation"), vise, donnee.get("parametre"),
                   donnee.get("valeur"), donnee.get("motif"))

    @property
    def fiche(self) -> str | None:
        """La fiche nommée qu'elle vise, ``None`` pour un sélecteur."""
        return self.vise if isinstance(self.vise, str) else None

    @property
    def selecteur(self) -> tuple[str, str] | None:
        return self.vise if isinstance(self.vise, tuple) else None

    def __str__(self) -> str:
        if self.selecteur:
            return f"{self.operation} {{{self.selecteur[0]}: {self.selecteur[1]}}}"
        return f"{self.operation} {self.vise}"


@dataclass(frozen=True)
class Couche:
    """Une couche (contrat C.4, ``couche``)."""

    id: str
    nom: str
    operations: tuple[Operation, ...]
    depuis: object = ORIGINE
    portee: str = "univers"

    @classmethod
    def lue(cls, donnee: dict) -> Couche:
        return cls(donnee.get("id"), donnee.get("nom"),
                   tuple(Operation.lue(o) for o in donnee.get("operations") or ()),
                   donnee.get("depuis") or ORIGINE, donnee.get("portee") or "univers")

    @property
    def d_un_calcul(self) -> bool:
        return self.portee == "calcul"

    @property
    def transition(self) -> str | None:
        """La fiche de transition qu'elle ajoute, s'il y en a une."""
        return next((o.fiche for o in self.operations
                     if o.operation == "ajouter_une_transition"), None)


@dataclass(frozen=True)
class Univers:
    """Un univers (contrat C.4, ``univers``), sa pile résolue."""

    id: str
    nom: str
    #: Les couches posées sur le droit réel, de bas en haut.
    pile: tuple[Couche, ...]
    numero: int | None = None
    libelle: str | None = None
    observation: object = None
    parametres_du_pilote: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def couches(self) -> tuple[str, ...]:
        """La pile telle que l'univers la déclare, le droit réel en bas."""
        return (DROIT_REEL, *(c.id for c in self.pile))

    @property
    def est_le_droit_reel(self) -> bool:
        return not self.pile

    def titre(self, bascule: int) -> str:
        """Son nom, l'année de la bascule dite."""
        return self.nom.format(bascule=bascule)

    @property
    def de_l_univers(self) -> tuple[Couche, ...]:
        """Les couches qui valent pour l'univers entier."""
        return tuple(c for c in self.pile if not c.d_un_calcul)

    @property
    def transition(self) -> Couche | None:
        """La couche qui porte sa transition, s'il en a une."""
        return next((c for c in self.pile if c.transition), None)

    @property
    def ajoutees(self) -> tuple[str, ...]:
        """Les fiches de la proposition qu'il ajoute, dans l'ordre de la pile."""
        return tuple(o.fiche for c in self.de_l_univers for o in c.operations
                     if o.operation in AJOUTS)

    def ajoute(self, fiche: str) -> bool:
        return fiche in self.ajoutees

    @property
    def calcul(self) -> tuple[Operation, ...]:
        """Ce que ses couches d'un seul calcul neutralisent."""
        return tuple(o for c in self.pile if c.d_un_calcul for o in c.operations)

    @property
    def changements(self) -> tuple[tuple[str, str, object], ...]:
        """Ses changements de paramètre : (fiche, paramètre, valeur), dans
        l'ordre de la pile."""
        return tuple((o.fiche, o.parametre, o.valeur) for c in self.de_l_univers
                     for o in c.operations if o.operation == "changer_un_parametre")

    @property
    def decisions(self) -> tuple[tuple[Couche, Operation], ...]:
        """Ce que ses couches décident des fiches du droit réel."""
        return tuple((c, o) for c in self.de_l_univers for o in c.operations
                     if o.operation in DECISIONS)


# -- lecture -------------------------------------------------------------------

def couches(dossier: Path = COUCHES) -> dict[str, dict]:
    """Chaque couche sous le nom de son fichier."""
    return {chemin.stem: charger_yaml(chemin) for chemin in sorted(dossier.glob("*.yaml"))}


def univers_declares(dossier: Path = UNIVERS) -> dict[str, dict]:
    """Chaque univers sous le nom de son fichier."""
    return {chemin.stem: charger_yaml(chemin) for chemin in sorted(dossier.glob("*.yaml"))}


def charger(dossier: Path = UNIVERS, dossier_couches: Path = COUCHES,
            regles: Path = carte.REGLES) -> dict[str, Univers]:
    """Les univers, leur pile résolue, dans l'ordre de leurs numéros. Ce qui ne
    tient pas l'arrête : un moteur ne calcule pas un univers mal formé."""
    return dict(_charger(dossier, dossier_couches, regles))


@lru_cache(maxsize=8)
def _charger(dossier: Path, dossier_couches: Path, regles: Path) -> tuple[tuple[str, Univers], ...]:
    erreurs = erreurs_de_structure(dossier, dossier_couches, regles)
    if erreurs:
        raise ValueError("univers mal formés :\n" + "\n".join(erreurs))
    lues = {nom: Couche.lue(donnee) for nom, donnee in couches(dossier_couches).items()}
    tous = []
    for nom, donnee in univers_declares(dossier).items():
        tous.append(Univers(
            id=nom, nom=donnee["nom"],
            pile=tuple(lues[c] for c in (donnee.get("couches") or [DROIT_REEL])[1:]),
            numero=donnee.get("numero"), libelle=donnee.get("libelle"),
            observation=donnee.get("observation"),
            parametres_du_pilote=dict(donnee.get("parametres_du_pilote") or {})))
    tous.sort(key=lambda u: (u.numero is None, u.numero or 0, u.id))
    return tuple((u.id, u) for u in tous)


def de_la_proposition(dossier: Path = UNIVERS, dossier_couches: Path = COUCHES,
                      regles: Path = carte.REGLES) -> tuple[Univers, ...]:
    """Les univers de la proposition : tous, sauf le droit réel."""
    return tuple(u for u in charger(dossier, dossier_couches, regles).values()
                 if not u.est_le_droit_reel)


# -- ce qu'une opération atteint ------------------------------------------------

def fiches_visees(vise, fiches: dict[str, dict]) -> set[str]:
    """Les fiches de ``fiches`` qu'une opération atteint : la fiche nommée, ou
    celles que le sélecteur désigne par leur champ. Une fiche qui ne dit pas
    encore ce champ n'est atteinte que par son nom."""
    if isinstance(vise, dict) and len(vise) == 1:
        vise = next(iter(vise.items()))
    if isinstance(vise, str):
        return {vise} if vise in fiches else set()
    sorte, valeur = vise
    if sorte == "regime":
        return {n for n, f in fiches.items() if valeur in (f.get("regimes") or ())}
    if sorte in SELECTEURS_DE_FICHES:
        return {n for n, f in fiches.items() if f.get(sorte) == valeur}
    raise ValueError(f"le sélecteur « {sorte} » ne se résout pas en fiches")


def sans_decision(univers: Univers, fiches: dict[str, dict] | None = None) -> list[str]:
    """Les fiches du droit réel qu'aucune couche de l'univers ne garde, ne
    remplace ni ne neutralise, par leur nom ou par un sélecteur (§ 4.8) : les
    domaines sans décision (§ 8). Le droit réel n'en a pas : il est la carte."""
    fiches = carte.fiches() if fiches is None else fiches
    if univers.est_le_droit_reel:
        return []
    decidees: set[str] = set()
    for _, operation in univers.decisions:
        decidees |= fiches_visees(operation.vise, fiches)
    return sorted(set(fiches) - decidees)


# -- contrôle ------------------------------------------------------------------

def constats(dossier: Path = UNIVERS, dossier_couches: Path = COUCHES) -> list[contrats.Constat]:
    """Ce que le contrat C.4 dit de chaque couche et de chaque univers."""
    validateur = contrats.Validateur("univers")
    sortie: list[contrats.Constat] = []
    for nom, donnee in couches(dossier_couches).items():
        sortie += validateur.valider(donnee, "couche", chemin=f"couche {nom}")
    for nom, donnee in univers_declares(dossier).items():
        sortie += validateur.valider(donnee, "univers", chemin=f"univers {nom}")
    return sortie


def erreurs_de_structure(dossier: Path = UNIVERS, dossier_couches: Path = COUCHES,
                         regles: Path = carte.REGLES) -> list[str]:
    """Ce qui empêche de résoudre les piles : rien, si elles tiennent.

    Le contrat C.4 sans erreur ni manque ; chaque fichier nommé de son
    identifiant ; chaque couche d'une pile qui existe, le droit réel en bas ;
    chaque opération qui vise une fiche de la carte ou un sélecteur connu, et
    qui dit ce que son opération demande ; chaque ``depuis`` lisible ; les
    règles de la pile (en tête du module).
    """
    erreurs = [str(c) for c in constats(dossier, dossier_couches)]
    droit_reel = carte.fiches(regles)
    proposition = carte.fiches(regles / carte.PROPOSITION.name)
    brutes = couches(dossier_couches)
    for nom, donnee in brutes.items():
        if donnee.get("id") != nom:
            erreurs.append(f"couche {nom} : elle s'appelle « {donnee.get('id')} », "
                           f"son fichier {nom}.yaml")
        if nom == DROIT_REEL:
            erreurs.append(f"couche {nom} : le droit réel est la carte, il n'a pas de fichier")
        erreurs += [f"couche {nom} : {e}" for e in
                    _erreurs_de_couche(Couche.lue(donnee), droit_reel, proposition)]
    for nom, donnee in univers_declares(dossier).items():
        if donnee.get("id") != nom:
            erreurs.append(f"univers {nom} : il s'appelle « {donnee.get('id')} », "
                           f"son fichier {nom}.yaml")
        pile = list(donnee.get("couches") or [DROIT_REEL])
        if pile[0] != DROIT_REEL or pile.count(DROIT_REEL) != 1:
            erreurs.append(f"univers {nom} : le droit réel est en bas de la pile, et seulement là")
        doubles = sorted({c for c in pile if pile.count(c) > 1})
        if doubles:
            erreurs.append(f"univers {nom} : couches posées deux fois : {', '.join(doubles)}")
        inconnues = [c for c in pile if c != DROIT_REEL and c not in brutes]
        if inconnues:
            erreurs.append(f"univers {nom} : couches inconnues : {', '.join(inconnues)}")
            continue
        pile_lue = tuple(Couche.lue(brutes[c]) for c in pile if c != DROIT_REEL)
        erreurs += [f"univers {nom} : {e}" for e in
                    _erreurs_de_pile(pile_lue, droit_reel, proposition)]
    return erreurs


def _erreurs_de_couche(couche: Couche, droit_reel: dict, proposition: dict) -> list[str]:
    erreurs = _erreurs_de_depuis(couche.depuis)
    valeurs = vocabulaire.valeurs()["listes"]
    for operation in couche.operations:
        if operation.selecteur is not None:
            sorte, valeur = operation.selecteur
            erreurs += _erreurs_de_selecteur(sorte, valeur, valeurs)
            if sorte == "contributivite" and not couche.d_un_calcul:
                erreurs.append(f"{operation} : la contributivité ne se résout pas en "
                               "fiches, elle ne vaut que dans un calcul")
        elif not isinstance(operation.vise, str):
            erreurs.append(f"{operation.operation} : vise une fiche nommée, ou un seul sélecteur")
            continue
        elif operation.vise not in droit_reel and operation.vise not in proposition:
            erreurs.append(f"{operation} : aucune fiche de la carte ne s'appelle ainsi")
        if operation.operation in AJOUTS and operation.fiche not in proposition:
            erreurs.append(f"{operation} : n'ajoute qu'une fiche de la proposition "
                           "(data/reference/regles/proposition/)")
        if operation.operation == "changer_un_parametre":
            erreurs += _erreurs_de_changement(operation, {**droit_reel, **proposition})
        elif operation.parametre is not None or operation.valeur is not None:
            erreurs.append(f"{operation} : seul un changement de paramètre porte un "
                           "paramètre et une valeur")
        if couche.d_un_calcul and operation.operation != "neutraliser":
            erreurs.append(f"{operation} : une couche d'un seul calcul ne fait que neutraliser")
    if sum(o.operation == "ajouter_une_transition" for o in couche.operations) > 1:
        erreurs.append("une couche porte une transition au plus")
    if couche.transition and couche.d_un_calcul:
        erreurs.append("une transition vaut pour l'univers, pas pour un calcul")
    return erreurs


def _erreurs_de_selecteur(sorte: str, valeur, valeurs: dict) -> list[str]:
    connus = valeurs["selecteurs"]["valeurs"]
    if sorte not in connus:
        return [f"sélecteur « {sorte} » inconnu du vocabulaire (liste selecteurs)"]
    liste = {"etape": "etapes", "domaine": "domaines", "face": "faces",
             "contributivite": "neutralisations"}.get(sorte)
    if liste and valeur not in valeurs[liste]["valeurs"]:
        return [f"sélecteur {sorte} : « {valeur} » n'est pas dans la liste {liste}"]
    if sorte == "regime" and not (RACINE_DONNEES / "reference" / "regimes" / f"{valeur}.yaml").exists():
        return [f"sélecteur regime : « {valeur} » n'a pas de fichier de régime"]
    return []


def _erreurs_de_changement(operation: Operation, fiches: dict) -> list[str]:
    erreurs = []
    champs = {f.name for f in dataclasses.fields(Parametres)}
    lus = ((fiches.get(operation.fiche) or {}).get("code") or {}).get("parametres") or []
    if operation.parametre is None or operation.valeur is None:
        erreurs.append(f"{operation} : dit le paramètre qu'il change et sa valeur")
    elif operation.parametre not in lus:
        erreurs.append(f"{operation} : la fiche {operation.fiche} ne lit pas "
                       f"« {operation.parametre} » (code.parametres)")
    valeur = operation.valeur
    if isinstance(valeur, dict):
        if set(valeur) != {"parametre"} or valeur["parametre"] not in champs:
            erreurs.append(f"{operation} : une valeur qui se lit ailleurs nomme un paramètre")
    return erreurs


def _erreurs_de_depuis(depuis) -> list[str]:
    if depuis == ORIGINE:
        return []
    if not isinstance(depuis, dict) or set(depuis) != {"date", "valeur"}:
        return [f"depuis : « {ORIGINE} », ou la date qu'elle lit et sa valeur"]
    erreurs = []
    if not vocabulaire.est_date_nommee(depuis["date"]):
        erreurs.append(f"depuis : « {depuis['date']} » n'est pas une date nommée")
    valeur = depuis["valeur"]
    champs = {f.name for f in dataclasses.fields(Parametres)}
    if isinstance(valeur, dict):
        if set(valeur) != {"parametre"} or valeur["parametre"] not in champs:
            erreurs.append("depuis : une valeur qui se lit ailleurs nomme un paramètre")
    elif not isinstance(valeur, date):
        erreurs.append("depuis : sa valeur est une date, ou le paramètre qui la porte")
    return erreurs


def _erreurs_de_pile(pile: tuple[Couche, ...], droit_reel: dict, proposition: dict) -> list[str]:
    """Les règles de la pile, couche après couche, de bas en haut."""
    erreurs = []
    ajoutees: dict[str, str] = {}
    decidees: dict[str, tuple[str, str]] = {}
    changes: dict[tuple[str, str], str] = {}
    transitions = [c.id for c in pile if c.transition]
    if len(transitions) > 1:
        erreurs.append(f"une transition au plus, et la pile en porte {len(transitions)}")
    for rang, couche in enumerate(pile):
        if couche.d_un_calcul:
            if not any(c.transition for c in pile[rang + 1:]):
                erreurs.append(f"la couche {couche.id} ne vaut que pour un calcul, "
                               "et aucune transition au-dessus d'elle n'en demande")
            continue
        for operation in couche.operations:
            if operation.operation in AJOUTS:
                if operation.fiche in ajoutees:
                    erreurs.append(f"{operation.fiche} : ajoutée par {ajoutees[operation.fiche]} "
                                   f"et par {couche.id}")
                ajoutees[operation.fiche] = couche.id
                continue
            if operation.fiche in proposition and operation.fiche not in ajoutees:
                erreurs.append(f"{couche.id}, {operation} : aucune couche d'en dessous "
                               "n'a ajouté cette fiche")
            if operation.operation == "changer_un_parametre":
                cle = (operation.fiche, operation.parametre)
                if cle in changes:
                    erreurs.append(f"{operation.fiche}.{operation.parametre} : changé par "
                                   f"{changes[cle]} et par {couche.id}")
                changes[cle] = couche.id
                continue
            if operation.selecteur and operation.selecteur[0] not in SELECTEURS_DE_FICHES:
                continue                        # signalé avec la couche
            if not isinstance(operation.vise, (str, tuple)):
                continue
            for fiche in sorted(fiches_visees(operation.vise, {**droit_reel, **proposition})):
                avant = decidees.get(fiche)
                if avant and avant[0] != operation.operation:
                    erreurs.append(f"{fiche} : « {avant[0]} » par {avant[1]}, "
                                   f"« {operation.operation} » par {couche.id}")
                decidees.setdefault(fiche, (operation.operation, couche.id))
    return erreurs


def citations(texte: str) -> list[str]:
    """Les passages qu'un motif cite, entre guillemets français."""
    return [" ".join(c.split()) for c in re.findall(r"«\s*(.+?)\s*»", texte or "", re.S)]


def texte_de_la_proposition(chemin: Path = TEXTE_DE_LA_PROPOSITION) -> str:
    """Le texte de la proposition, tel qu'une citation s'y retrouve : sans les
    ancres des chiffres, les marques de gras, de code et de citation en bloc,
    les blancs réduits à un espace."""
    texte = chemin.read_text(encoding="utf-8")
    texte = re.sub(r"<!--.*?-->", "", texte, flags=re.S)
    texte = re.sub(r"^> ?", "", texte, flags=re.M)
    texte = texte.replace("**", "").replace("`", "")
    return " ".join(texte.split())


def controler(dossier: Path = UNIVERS, dossier_couches: Path = COUCHES,
              regles: Path = carte.REGLES,
              proposition: Path = TEXTE_DE_LA_PROPOSITION) -> list[str]:
    """Ce qui ne va pas dans les univers : rien, s'ils tiennent.

    Ce qu':func:`erreurs_de_structure` exige, et que chaque passage cité entre
    guillemets par un motif de couche, ou par une fiche de la proposition qui
    cite le README, se retrouve mot pour mot dans le texte de la proposition
    (§ 3.1, § 3.2) : une déduction n'est pas une lecture.
    """
    erreurs = erreurs_de_structure(dossier, dossier_couches, regles)
    texte = texte_de_la_proposition(proposition)
    for nom, donnee in couches(dossier_couches).items():
        for operation in donnee.get("operations") or ():
            for passage in citations(operation.get("motif")):
                if passage not in texte:
                    erreurs.append(f"couche {nom} : « {passage} » n'est pas dans {proposition.name}")
    for nom, fiche in carte.fiches(regles / carte.PROPOSITION.name).items():
        for version in fiche.get("versions") or ():
            for cite in version.get("textes") or ():
                if not str(cite.get("reference") or "").startswith(proposition.name):
                    continue
                passage = " ".join(str(cite.get("citation") or "").split())
                if not passage or passage not in texte:
                    erreurs.append(f"fiche {nom} : « {passage} » n'est pas dans {proposition.name}")
    return erreurs
