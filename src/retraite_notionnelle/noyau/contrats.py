"""Les neuf contrats de données, en schémas, et le validateur qui les applique.

``docs/architecture.md``, § 13.1 et annexe C. Chaque contrat est un fichier de
``data/reference/contrats/`` : un ``schema_version``, l'annexe qu'il suit, et
ses objets, chacun avec ses champs. Un champ dit ce qu'il porte, son type, et
s'il est obligatoire ou, sinon, sa valeur par défaut.

Le validateur rend des CONSTATS de deux genres, et la différence est tout son
objet :

``erreur``
    Un champ que le contrat ne connaît pas, une valeur hors de son
    vocabulaire, un type faux. Une valeur qu'un moteur ne connaît pas
    l'arrête (§ 6.7) : les tests refusent une erreur.
``manque``
    Un champ obligatoire absent. La donnée n'est pas encore mûre — une fiche
    tirée d'un registre ne sait pas encore son étape —, et ce n'est pas une
    faute : le tableau de bord le compte, et rien ne bloque (§ 9.2 : ce qu'on
    apprend n'est jamais bloqué, une règle découverte entre avant d'être
    mûre).

Les types : ``identifiant`` (minuscules, chiffres, soulignés), ``texte``,
``entier``, ``nombre``, ``booleen``, ``date`` (une date, ou rien),
``intervalle`` ([début, fin), chacun une date ou rien), ``bornes`` (un
intervalle par date nommée du vocabulaire), ``date_nommee``, ``valeur`` (dans
la liste de vocabulaire que ``valeurs`` nomme), ``liste`` (dont chaque élément
est du type ou de l'objet que ``de`` dit), ``objet`` (un autre objet du même
contrat), ``exemples`` (des identifiants d'exemples, ou « aucun trouvé ») et
``libre``.

Les étapes du moteur s'échangent des données que décrit, chacune, un schéma
écrit dans la même langue (annexe C, « Les deux règles d'exécution ») : un
fichier par étape dans ``data/reference/etapes/``, que le même validateur
applique — ``Validateur(etape, ETAPES)`` — et que :func:`controler_etapes`
contrôle comme :func:`controler` contrôle les contrats.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from ..config import RACINE_DONNEES
from ..donnees.chargement import charger_yaml
from . import vocabulaire

CONTRATS = RACINE_DONNEES / "reference" / "contrats"
#: Les schémas des données que les étapes s'échangent, un par étape.
ETAPES = RACINE_DONNEES / "reference" / "etapes"

#: Les neuf contrats de l'annexe C, par leur fichier.
NOMS = ("chronologie", "fiche", "table_datee", "univers", "ligne_releve",
        "liquidation", "evenement", "entree_journal", "surface_publique")

TYPES = {"identifiant", "texte", "entier", "nombre", "booleen", "date", "intervalle",
         "bornes", "date_nommee", "valeur", "liste", "objet", "exemples", "libre"}

_IDENTIFIANT = re.compile(r"[a-z0-9][a-z0-9_]*")


@dataclass(frozen=True)
class Constat:
    chemin: str      # « fiche.versions[2].bornes »
    genre: str       # « erreur » ou « manque »
    message: str

    def __str__(self) -> str:
        return f"{self.chemin} : {self.message}"


def contrat(nom: str, dossier: Path = CONTRATS) -> dict:
    return charger_yaml(dossier / f"{nom}.yaml")


def objets(nom: str, dossier: Path = CONTRATS) -> dict[str, dict]:
    """Les objets d'un contrat, chacun avec ses champs ; une relation reçoit
    ceux de la fiche qu'elle étend."""
    brut = contrat(nom, dossier)["objets"]
    resolus = {}
    for objet, spec in brut.items():
        champs = {}
        if spec.get("etend"):
            champs.update(brut[spec["etend"]]["champs"])
        champs.update(spec["champs"])
        resolus[objet] = {**spec, "champs": champs}
    return resolus


class Validateur:
    """Applique un contrat à une donnée ; le vocabulaire est lu une fois."""

    def __init__(self, nom: str, dossier: Path = CONTRATS,
                 dossier_vocabulaire: Path = vocabulaire.VOCABULAIRE):
        self.nom = nom
        self.version = contrat(nom, dossier)["schema_version"]
        self.objets = objets(nom, dossier)
        listes = vocabulaire.valeurs(dossier_vocabulaire)["listes"]
        self.listes = {n: set(l["valeurs"]) for n, l in listes.items()}
        self.dates = set(vocabulaire.dates_nommees(dossier_vocabulaire))

    def valider(self, donnee, objet: str, chemin: str | None = None) -> list[Constat]:
        chemin = chemin or objet
        spec = self.objets[objet]
        if not isinstance(donnee, dict):
            return [Constat(chemin, "erreur", f"un {objet} est une table de champs")]
        constats: list[Constat] = []
        champs = spec["champs"]
        if not spec.get("ouvert"):
            for inconnu in sorted(set(donnee) - set(champs)):
                constats.append(Constat(chemin, "erreur",
                                        f"champ « {inconnu} » inconnu du contrat {self.nom}"))
        if "schema_version" in champs and donnee.get("schema_version") not in (None, self.version):
            constats.append(Constat(chemin, "erreur",
                                    f"schema_version {donnee.get('schema_version')}, le contrat "
                                    f"est à la version {self.version}"))
        for nom, champ in champs.items():
            if donnee.get(nom) is None:
                if self.obligatoire(champ, donnee):
                    constats.append(Constat(f"{chemin}.{nom}", "manque",
                                            f"obligatoire : {champ['porte']}"))
                continue
            constats += self._valeur(donnee[nom], champ, f"{chemin}.{nom}")
        un_des = spec.get("un_des")
        if un_des and not any(donnee.get(c) for c in un_des):
            constats.append(Constat(chemin, "erreur", f"il faut l'un de {un_des}"))
        return constats

    @staticmethod
    def obligatoire(champ: dict, donnee: dict) -> bool:
        """Le champ est-il exigé de cette donnée, conditions comprises ?"""
        if champ.get("obligatoire"):
            return True
        for cle, valeurs in (champ.get("obligatoire_si") or {}).items():
            if donnee.get(cle) in valeurs:
                return True
        for cle, valeurs in (champ.get("obligatoire_sauf") or {}).items():
            if donnee.get(cle) not in valeurs:
                return True
        return False

    def _valeur(self, valeur, champ: dict, chemin: str) -> list[Constat]:
        genre = champ["type"]
        if valeur is None and not champ.get("obligatoire"):
            return []
        if genre == "liste":
            if not isinstance(valeur, list):
                return [Constat(chemin, "erreur", "une liste est attendue")]
            element = champ["de"]
            constats = []
            for rang, item in enumerate(valeur):
                sous = f"{chemin}[{rang}]"
                if isinstance(element, dict) and "objet" in element:
                    constats += self.valider(item, element["objet"], sous)
                else:
                    constats += self._valeur(item, {"type": element, "obligatoire": True}, sous)
            return constats
        if genre == "objet":
            return self.valider(valeur, champ["objet"], chemin)
        if genre == "valeur":
            liste = self.listes.get(champ["valeurs"])
            if liste is None:
                return [Constat(chemin, "erreur", f"liste de vocabulaire inconnue : {champ['valeurs']}")]
            if valeur not in liste:
                return [Constat(chemin, "erreur",
                                f"« {valeur} » n'est pas dans la liste {champ['valeurs']}")]
            return []
        if genre == "date_nommee":
            if valeur not in self.dates:
                return [Constat(chemin, "erreur", f"« {valeur} » n'est pas une date nommée du vocabulaire")]
            return []
        if genre == "bornes":
            if not isinstance(valeur, dict) or not valeur:
                return [Constat(chemin, "erreur", "des bornes : un intervalle par date qui décide")]
            constats = []
            for nom, intervalle in valeur.items():
                if nom not in self.dates:
                    constats.append(Constat(chemin, "erreur", f"borne sur « {nom} », qui n'est pas une date nommée"))
                constats += self._valeur(intervalle, {"type": "intervalle", "obligatoire": True},
                                         f"{chemin}.{nom}")
            return constats
        if genre == "intervalle":
            if (not isinstance(valeur, list) or len(valeur) != 2
                    or not all(v is None or _est_date(v) for v in valeur)):
                return [Constat(chemin, "erreur", "un intervalle [début, fin), chacun une date ou rien")]
            debut, fin = (_en_date(v) for v in valeur)
            if debut and fin and not debut < fin:
                return [Constat(chemin, "erreur", f"intervalle vide ou renversé : [{debut}, {fin})")]
            return []
        if genre == "date":
            return [] if valeur is None or _est_date(valeur) else [
                Constat(chemin, "erreur", f"une date est attendue, pas « {valeur} »")]
        if genre == "identifiant":
            return [] if isinstance(valeur, str) and _IDENTIFIANT.fullmatch(valeur) else [
                Constat(chemin, "erreur", f"« {valeur} » n'est pas un identifiant (minuscules, chiffres, _)")]
        if genre == "texte":
            return [] if isinstance(valeur, (str, int, float)) else [
                Constat(chemin, "erreur", "un texte est attendu")]
        if genre == "entier":
            return [] if isinstance(valeur, int) and not isinstance(valeur, bool) else [
                Constat(chemin, "erreur", "un entier est attendu")]
        if genre == "nombre":
            return [] if isinstance(valeur, (int, float)) and not isinstance(valeur, bool) else [
                Constat(chemin, "erreur", "un nombre est attendu")]
        if genre == "booleen":
            return [] if isinstance(valeur, bool) else [Constat(chemin, "erreur", "oui ou non")]
        if genre == "exemples":
            if valeur == "aucun trouvé":
                return []
            if isinstance(valeur, list) and all(isinstance(v, str) and _IDENTIFIANT.fullmatch(v) for v in valeur):
                return []
            return [Constat(chemin, "erreur", "des identifiants d'exemples, ou « aucun trouvé »")]
        if genre == "libre":
            return []
        return [Constat(chemin, "erreur", f"type inconnu : {genre}")]


def _est_date(valeur) -> bool:
    return _en_date(valeur) is not None


def _en_date(valeur):
    if valeur is None:
        return None
    if isinstance(valeur, datetime):
        return valeur.date()
    if isinstance(valeur, date):
        return valeur
    try:
        return date.fromisoformat(str(valeur))
    except ValueError:
        return None


def controler(dossier: Path = CONTRATS, dossier_vocabulaire: Path = vocabulaire.VOCABULAIRE) -> list[str]:
    """Ce qui ne va pas dans les schémas eux-mêmes : rien, s'ils tiennent.

    Chaque contrat nommé, avec sa version et son annexe ; chaque champ avec ce
    qu'il porte et un type connu ; une liste de vocabulaire qui existe ; un
    objet visé qui existe ; un champ facultatif avec sa valeur par défaut, un
    champ obligatoire sans ; un champ additif, facultatif, qui dit pourquoi.
    """
    erreurs = []
    listes = set(vocabulaire.valeurs(dossier_vocabulaire)["listes"])
    presents = sorted(p.stem for p in dossier.glob("*.yaml"))
    if presents != sorted(NOMS):
        erreurs.append(f"les contrats sont {sorted(NOMS)}, le dossier porte {presents}")
    for nom in NOMS:
        if nom not in presents:
            continue
        brut = contrat(nom, dossier)
        if brut.get("contrat") != nom or not isinstance(brut.get("schema_version"), int):
            erreurs.append(f"{nom} : il dit son nom et son schema_version")
        if not re.fullmatch(r"C\.\d", str(brut.get("annexe", ""))):
            erreurs.append(f"{nom} : il dit la section de l'annexe C qu'il suit")
        erreurs += _controler_champs(nom, objets(nom, dossier), listes)
    return erreurs


def _controler_champs(nom: str, tous: dict[str, dict], listes: set[str]) -> list[str]:
    """Ce qui ne va pas dans les champs des objets d'un schéma."""
    erreurs = []
    for objet, spec in tous.items():
        for champ, c in spec["champs"].items():
            ou = f"{nom}.{objet}.{champ}"
            if len(str(c.get("porte", "")).split()) < 2:
                erreurs.append(f"{ou} : il dit ce qu'il porte")
            if c.get("type") not in TYPES:
                erreurs.append(f"{ou} : type « {c.get('type')} » inconnu")
            if c.get("type") == "valeur" and c.get("valeurs") not in listes:
                erreurs.append(f"{ou} : liste de vocabulaire « {c.get('valeurs')} » inconnue")
            de = c.get("de")
            cible = c.get("objet") or (de.get("objet") if isinstance(de, dict) else None)
            if cible and cible not in tous:
                erreurs.append(f"{ou} : objet « {cible} » inconnu du contrat")
            if c.get("type") == "liste" and not (isinstance(de, str) and de in TYPES or cible):
                erreurs.append(f"{ou} : une liste dit de quoi, un type ou un objet")
            if c.get("type") == "objet" and not c.get("objet"):
                erreurs.append(f"{ou} : un objet dit lequel")
            if c.get("obligatoire") and "defaut" in c:
                erreurs.append(f"{ou} : obligatoire, il n'a pas de valeur par défaut")
            if not c.get("obligatoire") and "defaut" not in c:
                erreurs.append(f"{ou} : facultatif, il a une valeur par défaut")
            if c.get("additif") and (c.get("obligatoire") or len(str(c["additif"]).split()) < 3):
                erreurs.append(f"{ou} : un champ additif est facultatif, et dit pourquoi il est venu")
    return erreurs


def controler_etapes(dossier: Path = ETAPES, contrats: Path = CONTRATS,
                     dossier_vocabulaire: Path = vocabulaire.VOCABULAIRE) -> list[str]:
    """Ce qui ne va pas dans les schémas des étapes : rien, s'ils tiennent.

    Chaque fichier porte le nom d'une étape du vocabulaire, qu'il dit, avec
    son ``schema_version``, les données qu'elle lit et l'objet qu'elle écrit.
    Cet objet est décrit dans le fichier, ou par le contrat qu'il nomme — la
    chronologie que « préparer la chronologie » lit et écrit est celle de C.1 ;
    ses champs suivent les mêmes règles que ceux d'un contrat.
    """
    erreurs = []
    listes = set(vocabulaire.valeurs(dossier_vocabulaire)["listes"])
    etapes = set(vocabulaire.valeurs(dossier_vocabulaire)["listes"]["etapes"]["valeurs"])
    for chemin in sorted(dossier.glob("*.yaml")):
        nom = chemin.stem
        brut = contrat(nom, dossier)
        if nom not in etapes or brut.get("etape") != nom:
            erreurs.append(f"{nom} : le schéma porte le nom d'une étape du vocabulaire, et le dit")
        if not isinstance(brut.get("schema_version"), int):
            erreurs.append(f"{nom} : il dit son schema_version")
        if not isinstance(brut.get("lit"), list) or not brut.get("lit"):
            erreurs.append(f"{nom} : il dit les données que l'étape lit")
        tous = objets(nom, dossier)
        ecrit = brut.get("ecrit")
        if brut.get("contrat"):
            if brut["contrat"] not in NOMS:
                erreurs.append(f"{nom} : contrat « {brut['contrat']} » inconnu")
            elif ecrit not in objets(brut["contrat"], contrats):
                erreurs.append(f"{nom} : le contrat {brut['contrat']} n'a pas d'objet « {ecrit} »")
        elif ecrit not in tous:
            erreurs.append(f"{nom} : l'objet écrit, « {ecrit} », est décrit dans le schéma")
        erreurs += _controler_champs(nom, tous, listes)
    return erreurs
