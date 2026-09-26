"""Le vocabulaire des dates qui décident, et les listes de valeurs.

``docs/architecture.md``, § 4.2 et § 13.1 à 13.3. Deux fichiers :

* ``data/reference/vocabulaire/dates.yaml`` — les quatre sortes de dates
  (une liste fermée, au noyau), les dates nommées (qui s'ajoutent sans
  décision) et les combinaisons qui ne se présentent pas ;
* ``data/reference/vocabulaire/valeurs.yaml`` — les listes de valeurs que les
  contrats emploient : états, faces, sortes, motifs, natures, origines…

Une valeur qu'un contrat ne connaît pas l'arrête (§ 6.7) : c'est ce qui rend
l'ajout sans risque, et ce module est ce qui le dit.
"""

from __future__ import annotations

from pathlib import Path

from ..config import RACINE_DONNEES
from ..donnees.chargement import charger_yaml

VOCABULAIRE = RACINE_DONNEES / "reference" / "vocabulaire"

#: Les quatre sortes de dates qui décident : une liste FERMÉE, au noyau.
#: Elle ne s'allonge que par une note de décision (§ 4.2).
SORTES_DE_DATES = ("fait", "lien", "liquidation", "derivee")


def dates(dossier: Path = VOCABULAIRE) -> dict:
    """Le fichier des dates qui décident, tel quel."""
    return charger_yaml(dossier / "dates.yaml")


def valeurs(dossier: Path = VOCABULAIRE) -> dict:
    """Le fichier des listes de valeurs, tel quel."""
    return charger_yaml(dossier / "valeurs.yaml")


def dates_nommees(dossier: Path = VOCABULAIRE) -> dict[str, dict]:
    """Les dates nommées, par nom : leur sorte, ce qu'elles disent."""
    return dates(dossier)["dates"]


def liste(nom: str, dossier: Path = VOCABULAIRE) -> set[str]:
    """Les valeurs d'une liste. Une liste inconnue est une erreur, jamais un
    ensemble vide : un contrat qui la nomme se tromperait sans bruit."""
    listes = valeurs(dossier)["listes"]
    if nom not in listes:
        raise KeyError(f"liste de valeurs inconnue : {nom}")
    return set(listes[nom]["valeurs"])


def est_date_nommee(nom: str, dossier: Path = VOCABULAIRE) -> bool:
    return nom in dates_nommees(dossier)


def controler(dossier: Path = VOCABULAIRE) -> list[str]:
    """Ce qui ne va pas dans le vocabulaire : rien, s'il tient.

    Les quatre sortes et elles seules ; chaque date nommée dans l'une d'elles,
    avec ce qu'elle dit ; chaque date dérivée calculée depuis des dates
    connues, et chaque autre sans ``depuis`` ; chaque combinaison impossible
    entre deux dates connues ; chaque liste de valeurs non vide, chaque valeur
    avec ce qu'elle veut dire.
    """
    import re

    erreurs: list[str] = []
    fichier_dates = dates(dossier)
    if tuple(fichier_dates.get("sortes") or ()) != SORTES_DE_DATES:
        erreurs.append(f"les sortes de dates doivent être exactement {SORTES_DE_DATES}, "
                       "une liste fermée qui ne change que par une note de décision")
    nommees = fichier_dates.get("dates") or {}
    identifiant = re.compile(r"[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)?")
    for nom, date in nommees.items():
        if not identifiant.fullmatch(nom):
            erreurs.append(f"{nom} : un nom de date s'écrit en minuscules, `personne.date`")
        if date.get("sorte") not in SORTES_DE_DATES:
            erreurs.append(f"{nom} : sorte « {date.get('sorte')} » hors des quatre")
        if len(str(date.get("dit") or "").split()) < 3:
            erreurs.append(f"{nom} : une date nommée dit ce qu'elle est")
        depuis = date.get("depuis")
        if date.get("sorte") == "derivee":
            if not depuis:
                erreurs.append(f"{nom} : une date dérivée dit de quelles dates elle se calcule")
            for source in depuis or []:
                if source not in nommees:
                    erreurs.append(f"{nom} : se calcule depuis {source}, qui n'est pas nommée")
        elif depuis:
            erreurs.append(f"{nom} : seule une date dérivée se calcule depuis d'autres")
    for combinaison in fichier_dates.get("combinaisons_impossibles") or []:
        for cle in ("date", "apres"):
            if combinaison.get(cle) not in nommees:
                erreurs.append(f"combinaison impossible : {combinaison.get(cle)} n'est pas nommée")
    for nom, contenu in (valeurs(dossier).get("listes") or {}).items():
        if not re.fullmatch(r"[a-z][a-z0-9_]*", nom):
            erreurs.append(f"liste {nom} : un nom de liste s'écrit en minuscules")
        entrees = contenu.get("valeurs") or {}
        if not entrees:
            erreurs.append(f"liste {nom} : vide")
        for valeur, sens in entrees.items():
            if not re.fullmatch(r"[a-z][a-z0-9_]*", str(valeur)):
                erreurs.append(f"liste {nom} : la valeur {valeur} s'écrit en minuscules")
            texte = sens.get("dit") if isinstance(sens, dict) else sens
            if len(str(texte or "").split()) < 2:
                erreurs.append(f"liste {nom} : la valeur {valeur} dit ce qu'elle veut dire")
    return erreurs
