"""La table d'une version de fiche, et les vues qu'on en fabrique.

Note de décision 0009 et son second rectificatif. Une version porte ce que son
texte écrit : sa table tient dans un fichier indexé par version, que le
récupérateur écrit quand LEGI porte le texte, et où la version désigne ses
lignes (``contenu.table``, contrat C.2). Ce que le texte laisse à sa rédaction
antérieure (``contenu.redaction_anterieure``) se lit dans la version nommée,
pour les seules naissances qu'il lui laisse.

Ce module lit la table d'une version, résolue, mois de naissance par mois
(:func:`par_mois`), et en fabrique les tables par génération que le moteur lit
encore : la table du droit en vigueur, qui est celle de la dernière version
(:func:`vue_par_generation`), et la copie d'avant une réforme, qui est celle de
la version que la réforme a fermée (:func:`vue_d_avant`). Une table fusionnée
se fabrique depuis les versions, et ne s'écrit jamais à la main :
``scripts/verifier_donnees.py --appliquer`` écrit les vues, et la suite les
confronte (``tests/test_tables_de_version.py``).

Un mois de naissance se compte en rang, l'année fois douze plus le mois moins
un ; une génération s'écrit dans les fichiers comme l'année plus la part
écoulée avant le premier du mois, ``1961.667`` pour le 1er septembre 1961.
"""

from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path

from ..config import RACINE_DONNEES
from ..noyau import renvois
from .chargement import Fiabilite, au_mois, charger_yaml

#: Les générations que le modèle couvre, et la fin d'une étendue que le texte
#: ne borne pas : celles du récupérateur
#: (``scripts/fetch/dila_legi_parametres_retraite.py``).
PREMIERE_GENERATION, DERNIERE_GENERATION, GENERATION_SANS_FIN = 1900, 1975, 2100

#: La fiche de l'âge légal, et la date qui choisit sa version.
FICHE_DE_L_AGE_LEGAL = "age_legal_par_generation"
DATE_D_EFFET = "liquidation.date_effet"

#: Les trois tables de l'âge légal que le moteur lit, vues des versions de la
#: fiche : celle du droit en vigueur (``None``), et les deux copies d'avant
#: réforme, chacune sous la version qui a fermé celle qu'elle garde.
VUES_DE_L_AGE_LEGAL = {
    "age_ouverture_requis.csv": None,
    "age_ouverture_avant_reforme_2023.csv": "loi_de_2023",
    "age_ouverture_avant_suspension.csv": "suspension_de_2025",
}


def rang(generation) -> int:
    """La clé d'une génération, en rang de mois : ``1961.667`` -> septembre 1961."""
    generation = float(generation)
    annee = int(generation)
    return annee * 12 + int(round((generation - annee) * 12))


def cle(rang_du_mois: int) -> str:
    """Le rang d'un mois, en clé de génération : « 1961 », « 1961.667 »."""
    annee, mois = divmod(rang_du_mois, 12)
    return f"{annee + mois / 12.0:.3f}".rstrip("0").rstrip(".")


def _rang_du_jour(valeur) -> int | None:
    """Le rang du mois d'une date de naissance, ``None`` pour « sans borne »."""
    if valeur is None:
        return None
    if isinstance(valeur, datetime):
        valeur = valeur.date()
    if not isinstance(valeur, date):
        valeur = date.fromisoformat(str(valeur))
    if valeur.day != 1:
        raise ValueError(f"une table par génération se coupe au premier du mois, pas le {valeur}")
    return valeur.year * 12 + valeur.month - 1


def _version(fiche: dict, identifiant: str) -> dict:
    for version in fiche.get("versions") or []:
        if version.get("id") == identifiant:
            return version
    raise ValueError(f"{fiche.get('id')} : pas de version « {identifiant} »")


def _lignes(table: dict, racine: Path) -> list[dict]:
    """Les lignes du fichier que la version désigne."""
    chemin = racine / "reference" / table["fichier"]
    with chemin.open(encoding="utf-8") as flux:
        lignes = list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))
    return [ligne for ligne in lignes
            if all(ligne[colonne] in {str(v) for v in valeurs}
                   for colonne, valeurs in table["lignes"].items())]


def par_mois(fiche: dict, identifiant: str, racine: Path = RACINE_DONNEES,
             _vues: tuple[str, ...] = ()) -> dict[int, float]:
    """La table d'une version, résolue : la valeur de chaque mois de naissance
    qu'elle couvre, de la première à la dernière génération du modèle.

    Ses propres lignes d'abord, tous textes confondus : deux textes d'une
    version peuvent écrire la même génération, la loi sa cible et le décret la
    montée, s'ils disent la même valeur. Puis ce qu'elle laisse à sa rédaction
    antérieure, pour les naissances que le renvoi nomme. Une contradiction,
    une version sans ligne, une naissance écrite et renvoyée à la fois, un
    renvoi qui boucle arrêtent la fabrication."""
    ou = f"{fiche.get('id')}.{identifiant}"
    if identifiant in _vues:
        raise ValueError(f"{ou} : les rédactions antérieures bouclent")
    contenu = _version(fiche, identifiant).get("contenu") or {}
    table = contenu.get("table")
    debut, fin = rang(PREMIERE_GENERATION), rang(DERNIERE_GENERATION + 1)
    valeurs: dict[int, float] = {}
    if table:
        lignes = _lignes(table, racine)
        if not lignes:
            raise ValueError(f"{ou} : aucune ligne de {table['fichier']} pour "
                             f"{table['lignes']}")
        for ligne in lignes:
            valeur = float(ligne[table["valeur"]])
            for mois in range(max(debut, rang(ligne[table["cle"]])),
                              min(fin, rang(ligne[f"{table['cle']}_fin"]))):
                if valeurs.setdefault(mois, valeur) != valeur:
                    raise ValueError(
                        f"{ou} : deux textes se contredisent pour la génération "
                        f"{cle(mois)}, {valeurs[mois]} et {valeur}")
    anterieure = contenu.get("redaction_anterieure")
    if anterieure:
        premier, dernier = (_rang_du_jour(b) for b in anterieure.get("naissance") or [None, None])
        laissees = range(debut if premier is None else max(debut, premier),
                         fin if dernier is None else min(fin, dernier))
        ecrites = sorted(set(laissees) & set(valeurs))
        if ecrites:
            raise ValueError(f"{ou} : écrit la génération {cle(ecrites[0])}, qu'elle "
                             "renvoie aussi à sa rédaction antérieure")
        avant = par_mois(fiche, anterieure["version"], racine, _vues + (identifiant,))
        valeurs.update({mois: avant[mois] for mois in laissees if mois in avant})
    return dict(sorted(valeurs.items()))


def _fiabilite(texte) -> int:
    """Le niveau qu'écrit une ligne ou une version, en nombre."""
    return int(Fiabilite[str(texte).strip().upper()])


def _generation(valeur) -> float | None:
    """Une borne de naissance, en génération : le 1er septembre 1961 est
    ``1961.667``, comme les tables l'écrivent."""
    mois = _rang_du_jour(valeur)
    return None if mois is None else float(cle(mois))


def pour_le_moteur(fiche: dict, identifiant: str, racine: Path = RACINE_DONNEES) -> dict:
    """Ce que le paquet ajoute à une version préparée (``versions.preparer``)
    pour que le moteur la lise : ses propres lignes, en étendues de générations
    ``[première, fin exclue ou None, valeur, fiabilité]``, tous textes
    confondus, un âge au mois exact ; ce qu'elle laisse à sa rédaction antérieure, qui reste un
    renvoi que le moteur suit ; et, sans table, la fiabilité de la valeur
    qu'elle écrit, `haute` quand la version ne dit rien : lue, non recontrôlée
    par un récupérateur. Deux textes qui se contredisent arrêtent la
    fabrication, comme dans :func:`par_mois`."""
    ou = f"{fiche.get('id')}.{identifiant}"
    version = _version(fiche, identifiant)
    contenu = version.get("contenu") or {}
    table = contenu.get("table")
    ajout: dict = {}
    if table:
        lignes = _lignes(table, racine)
        if not lignes:
            raise ValueError(f"{ou} : aucune ligne de {table['fichier']} pour "
                             f"{table['lignes']}")
        # Un âge s'écrit au mois dans les textes, en centièmes dans le fichier :
        # le moteur le lit au mois exact, comme dans les tables par génération
        # (``chargement.au_mois``).
        exacte = au_mois if table["valeur"] == "age" else float
        etendues = [(float(l[table["cle"]]), float(l[f"{table['cle']}_fin"]),
                     exacte(float(l[table["valeur"]])), _fiabilite(l["fiabilite"]))
                    for l in lignes]
        coupures = sorted({borne for debut, fin, _, _ in etendues for borne in (debut, fin)})
        ajout["table"] = []
        for debut, fin in zip(coupures, coupures[1:]):
            dites = {(valeur, fiabilite) for d, f, valeur, fiabilite in etendues
                     if d <= debut and fin <= f}
            if len({valeur for valeur, _ in dites}) > 1:
                raise ValueError(
                    f"{ou} : deux textes se contredisent pour la génération "
                    f"{cle(rang(debut))}, " + " et ".join(
                        str(valeur) for valeur in sorted({v for v, _ in dites})))
            if not dites:
                continue
            valeur, fiabilite = next(iter(dites))[0], min(f for _, f in dites)
            derniere = ajout["table"][-1] if ajout["table"] else None
            fin = None if fin >= GENERATION_SANS_FIN else fin
            if derniere and derniere[1] == debut and derniere[2:] == [valeur, fiabilite]:
                derniere[1] = fin
            else:
                ajout["table"].append([debut, fin, valeur, fiabilite])
    else:
        ajout["fiabilite"] = _fiabilite(version.get("fiabilite") or "haute")
    anterieure = contenu.get("redaction_anterieure")
    if anterieure:
        ajout["redaction_anterieure"] = {
            "version": anterieure["version"],
            "generations": [_generation(b) for b in anterieure.get("naissance") or [None, None]]}
    return ajout


def vue_par_generation(table: dict[int, float]) -> list[tuple[str, float]]:
    """La table par génération que le moteur lit : une ligne à chaque janvier,
    et une à chaque coupure en cours d'année."""
    vue, precedente = [], None
    for mois, valeur in table.items():
        if mois % 12 == 0 or valeur != precedente:
            vue.append((cle(mois), valeur))
        precedente = valeur
    return vue


def vue_d_avant(avant: dict[int, float], apres: dict[int, float]) -> list[tuple[str, float]]:
    """La copie d'avant une réforme : la table de la version qu'elle a fermée,
    depuis la première génération dont elle change la valeur, une ligne par
    changement. Posée sur la table du droit en vigueur, de sa première
    génération à toutes les suivantes, elle rend le droit d'avant."""
    changes = [mois for mois in avant if mois in apres and avant[mois] != apres[mois]]
    if not changes:
        return []
    vue, precedente = [], None
    for mois, valeur in avant.items():
        if mois >= changes[0] and valeur != precedente:
            vue.append((cle(mois), valeur))
            precedente = valeur
    return vue


def _fermee_par(fiche: dict, identifiant: str) -> str:
    """La version que ``identifiant`` a fermée : celle qui finit où elle commence."""
    debut = _version(fiche, identifiant)["bornes"][DATE_D_EFFET][0]
    for version in fiche["versions"]:
        if version["bornes"][DATE_D_EFFET][1] == debut and debut is not None:
            return version["id"]
    raise ValueError(f"{fiche.get('id')}.{identifiant} : aucune version ne finit où elle commence")


def vues_de_l_age_legal(racine: Path = RACINE_DONNEES) -> dict[str, list[tuple[str, float]]]:
    """Les trois tables de l'âge légal, fabriquées depuis les versions de sa
    fiche : chaque fichier de :data:`VUES_DE_L_AGE_LEGAL`, en lignes
    (génération, âge)."""
    regles = racine / "reference" / "regles"
    fiche = charger_yaml(regles / f"{FICHE_DE_L_AGE_LEGAL}.yaml")
    # Un renvoi se contrôle avant d'écrire : ceux de la fiche, et toute chaîne
    # de renvois qui passe par elle.
    erreurs = [e for e in renvois.controler(
        {chemin.stem: charger_yaml(chemin) for chemin in sorted(regles.glob("*.yaml"))})
        if f"{FICHE_DE_L_AGE_LEGAL}." in e]
    if erreurs:
        raise ValueError(" ; ".join(erreurs))
    en_vigueur = next(v["id"] for v in fiche["versions"]
                      if v["bornes"][DATE_D_EFFET][1] is None)
    vues = {}
    for nom, reforme in VUES_DE_L_AGE_LEGAL.items():
        if reforme is None:
            vues[nom] = vue_par_generation(par_mois(fiche, en_vigueur, racine))
        else:
            vues[nom] = vue_d_avant(par_mois(fiche, _fermee_par(fiche, reforme), racine),
                                    par_mois(fiche, reforme, racine))
    return vues
