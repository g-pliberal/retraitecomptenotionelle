"""La carte des règles : une fiche par dispositif, dans ``data/reference/regles/``.

``docs/architecture.md``, § 6. Chaque fiche suit le contrat C.2
(``data/reference/contrats/fiche.yaml``) ; une relation est une fiche qui porte
en plus sa sorte, les fiches qu'elle relie et son rang (§ 6.2). Ce module lit
la carte et la contrôle. Les registres d'hier en sont des vues : ce qu'il faut
relire (``scripts/veille_droit.py``), ce qui ne va pas encore et ce qui reste à
faire (``scripts/tableau_de_bord.py``).

Les fiches de la phase 2 sont tirées du registre de veille, dont elles ont
repris les entrées le 26 septembre 2026, sous le même identifiant : elles
savent ce que le registre savait — l'intitulé, l'état, l'effet, les lectures,
les textes, les exemples, les réformes —, et pas encore le reste. Ce qui leur
manque est un MANQUE, que ``manques()`` rend fiche par fiche et que le tableau
de bord compte : une fiche mûrit à mesure qu'on la complète, sans que rien
bloque (§ 9.2).
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

from ..config import RACINE_DONNEES
from ..donnees.chargement import charger_yaml
from . import contrats, partage, vocabulaire

REGLES = RACINE_DONNEES / "reference" / "regles"


def fiches(dossier: Path = REGLES) -> dict[str, dict]:
    """Chaque fiche sous le nom de son fichier, dans l'ordre alphabétique."""
    return {chemin.stem: charger_yaml(chemin) for chemin in sorted(dossier.glob("*.yaml"))}


def est_relation(fiche: dict) -> bool:
    """Une relation se reconnaît à sa sorte (§ 6.2)."""
    return "sorte" in fiche


def etats() -> list[str]:
    """Les états d'une fiche, dans l'ordre du vocabulaire : du plus sûr au
    moins sûr."""
    return list(vocabulaire.valeurs()["listes"]["etats_de_fiche"]["valeurs"])


def constats(dossier: Path = REGLES) -> list[contrats.Constat]:
    """Ce que le contrat dit de chaque fiche ; le chemin commence par son nom."""
    validateur = contrats.Validateur("fiche")
    sortie: list[contrats.Constat] = []
    for nom, fiche in fiches(dossier).items():
        objet = "relation" if est_relation(fiche) else "fiche"
        sortie += validateur.valider(fiche, objet, chemin=nom)
    return sortie


def manques(dossier: Path = REGLES) -> dict[str, list[str]]:
    """Ce qui manque à chaque fiche pour être mûre : ses champs obligatoires
    absents, conditions comprises. Une fiche mûre n'y figure pas."""
    par_fiche: dict[str, list[str]] = {}
    for constat in constats(dossier):
        if constat.genre == "manque":
            nom, _, champ = constat.chemin.partition(".")
            par_fiche.setdefault(nom, []).append(champ)
    return par_fiche


def controler(dossier: Path = REGLES) -> list[str]:
    """Ce qui ne va pas dans la carte : rien, si elle tient.

    Chaque fiche porte le nom de son fichier et suit son contrat sans erreur ;
    ses versions forment un partage à chaque date d'observation ; une relation
    relie des fiches qui existent, autres qu'elle-même (§ 6.7) ; une fiche
    dépréciée renvoie à une fiche qui existe ; une fiche ne lit que des
    présomptions que le vocabulaire nomme (§ 5.6).
    """
    connues = set(vocabulaire.presomptions())
    toutes = fiches(dossier)
    fautives = [c for c in constats(dossier) if c.genre == "erreur"]
    erreurs = [str(c) for c in fautives]
    # Le partage ne se joue que sur une fiche que son contrat accepte.
    a_partager = set(toutes) - {c.chemin.split(".")[0].split("[")[0] for c in fautives}
    for nom, fiche in toutes.items():
        if fiche.get("id") != nom:
            erreurs.append(f"{nom} : la fiche s'appelle « {fiche.get('id')} », "
                           f"son fichier {nom}.yaml")
        if est_relation(fiche):
            for relie in fiche.get("fiches") or []:
                cible = relie.get("fiche") if isinstance(relie, dict) else None
                if cible == nom or cible not in toutes:
                    erreurs.append(f"{nom} : la relation relie « {cible} », "
                                   "qui n'est pas une autre fiche de la carte")
        remplacante = fiche.get("remplacee_par")
        if remplacante is not None and remplacante not in toutes:
            erreurs.append(f"{nom} : remplacée par « {remplacante} », "
                           "qui n'est pas une fiche de la carte")
        presomptions = fiche.get("presomptions") or {}
        for presomption in presomptions if isinstance(presomptions, dict) else []:
            if presomption not in connues:
                erreurs.append(f"{nom} : lit la présomption « {presomption} », que le "
                               "vocabulaire ne nomme pas")
        if nom in a_partager:
            erreurs += partage.controler(fiche)
    return erreurs


def lecteurs_des_presomptions(dossier: Path = REGLES) -> dict[str, list[str]]:
    """Pour chaque présomption, les fiches qui la lisent."""
    lecteurs: dict[str, list[str]] = {}
    for nom, fiche in sorted(fiches(dossier).items()):
        presomptions = fiche.get("presomptions") or {}
        for presomption in presomptions if isinstance(presomptions, dict) else []:
            lecteurs.setdefault(presomption, []).append(nom)
    return lecteurs


def _date(valeur) -> date | None:
    if valeur is None or isinstance(valeur, date) and not isinstance(valeur, datetime):
        return valeur
    if isinstance(valeur, datetime):
        return valeur.date()
    return date.fromisoformat(str(valeur))


def a_relire(aujourd_hui: date, jours: int = 120,
             dossier: Path = REGLES) -> list[tuple[dict, list[str]]]:
    """La veille, vue de la carte : les fiches à relire, et pourquoi.

    Une fiche à vérifier, ou dont la règle manque au modèle ; une fiche lue il
    y a plus de ``jours`` jours, ou jamais ; une fiche dont la date de
    relecture est passée. Dans l'ordre des états, puis des noms.
    """
    rang = {etat: i for i, etat in enumerate(etats())}
    sortie = []
    for fiche in fiches(dossier).values():
        raisons = []
        if fiche.get("etat") in ("a_verifier", "manquante"):
            raisons.append(fiche["etat"])
        sources = fiche.get("sources") or {}
        lue = _date(sources.get("lu_le"))
        if lue is None:
            raisons.append("jamais lue")
        elif (aujourd_hui - lue).days > jours:
            raisons.append(f"lue il y a {(aujourd_hui - lue).days} jours")
        prochaine = _date(sources.get("prochaine_relecture"))
        if prochaine is not None and prochaine <= aujourd_hui:
            raisons.append(f"relecture prévue le {prochaine}")
        if raisons:
            sortie.append((fiche, raisons))
    return sorted(sortie, key=lambda x: (rang.get(x[0].get("etat"), len(rang)), x[0]["id"]))
