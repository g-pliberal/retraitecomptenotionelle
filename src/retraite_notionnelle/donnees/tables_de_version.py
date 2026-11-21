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
(:func:`vue_par_generation`). Les deux copies d'avant réforme de l'âge légal
sont parties : un droit contrefactuel garde la version d'avant dans une couche
(``donnees/droits_contrefactuels.py``). Une table fusionnée
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

#: La table de l'âge légal que la fabrique, la certification et la prose
#: lisent, vue des versions de la fiche : celle du droit en vigueur (``None``).
VUES_DE_L_AGE_LEGAL = {
    "age_ouverture_requis.csv": None,
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
             _vues: tuple[str, ...] = (), nom: str = "age") -> dict[int, float]:
    """La table d'une version, résolue : la valeur de chaque mois de naissance
    qu'elle couvre, de la première à la dernière génération du modèle.

    Ses propres lignes d'abord, tous textes confondus : deux textes d'une
    version peuvent écrire la même génération, la loi sa cible et le décret la
    montée, s'ils disent la même valeur. Puis ce qu'elle laisse à sa rédaction
    antérieure, pour les naissances que le renvoi nomme. Puis, pour les
    naissances qui restent, la valeur que la version écrit pour toute
    génération, son paramètre ``nom`` (le I de R. 351-45 : « quelle que soit
    la date de naissance »). Une contradiction, une version sans ligne, une
    naissance écrite et renvoyée à la fois, un renvoi qui boucle arrêtent la
    fabrication."""
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
        avant = par_mois(fiche, anterieure["version"], racine, _vues + (identifiant,), nom)
        valeurs.update({mois: avant[mois] for mois in laissees if mois in avant})
    general = (contenu.get("parametres") or {}).get(nom)
    if general is not None:
        for mois in range(debut, fin):
            valeurs.setdefault(mois, float(general))
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
    if table and table["valeur"] == VALEUR_DES_PORTES:
        ajout["portes"] = _portes_pour_le_moteur(ou, table, racine)
    elif table:
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
    if not table or (contenu.get("parametres") or {}).get("trimestres") is not None \
            or table["valeur"] == VALEUR_DES_PORTES:
        # La fiabilité de la valeur que la version écrit pour tous : sans
        # table, ou pour les générations que sa table ne nomme pas.
        ajout["fiabilite"] = _fiabilite(version.get("fiabilite") or "haute")
    anterieure = contenu.get("redaction_anterieure")
    if anterieure:
        ajout["redaction_anterieure"] = {
            "version": anterieure["version"],
            "generations": [_generation(b) for b in anterieure.get("naissance") or [None, None]]}
    if contenu.get("renvois"):
        ajout["renvois"] = [renvoi_pour_le_moteur(r) for r in contenu["renvois"]]
    return ajout


def _en_mois(duree: dict | None) -> int:
    duree = duree or {}
    return 12 * int(duree.get("ans") or 0) + int(duree.get("mois") or 0) \
        + 3 * int(duree.get("trimestres") or 0)


def renvoi_pour_le_moteur(renvoi: dict) -> dict:
    """Un renvoi daté (contrat C.2, objet ``renvoi``), tel que le moteur le
    suit : la fiche lue, la valeur nommée, de qui, la date qui choisit la
    version lue, et ce que l'opération ajoute, en mois (négatif s'il le
    retranche). Une opération par fonction (``code``) n'a pas encore de
    lecteur : elle arrête la fabrication."""
    if renvoi.get("code"):
        raise ValueError(f"renvoi à {renvoi.get('fiche')} : le moteur ne suit pas encore "
                         f"une opération par fonction ({renvoi['code']})")
    lu = {"fiche": renvoi["fiche"], "valeur": renvoi["valeur"], "de": renvoi["de"],
          "date": renvoi["date"],
          "mois": _en_mois(renvoi.get("ajoute")) - _en_mois(renvoi.get("retranche"))}
    if renvoi.get("naissance"):
        # Les générations auxquelles le texte écrit le renvoi, comme les tables
        # les écrivent ; `null`, sans borne.
        lu["generations"] = [_generation(b) for b in renvoi["naissance"]]
    if renvoi.get("ligne"):
        lu["ligne"] = dict(renvoi["ligne"])
    return lu


def vue_par_generation(table: dict[int, float]) -> list[tuple[str, float]]:
    """La table par génération que le moteur lit : une ligne à chaque janvier,
    et une à chaque coupure en cours d'année."""
    vue, precedente = [], None
    for mois, valeur in table.items():
        if mois % 12 == 0 or valeur != precedente:
            vue.append((cle(mois), valeur))
        precedente = valeur
    return vue


def vues_de_l_age_legal(racine: Path = RACINE_DONNEES) -> dict[str, list[tuple[str, float]]]:
    """La table de l'âge légal, fabriquée depuis les versions de sa fiche :
    chaque fichier de :data:`VUES_DE_L_AGE_LEGAL`, en lignes (génération,
    âge)."""
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
    for nom in VUES_DE_L_AGE_LEGAL:
        vues[nom] = vue_par_generation(par_mois(fiche, en_vigueur, racine))
    return vues


# --- L'âge du taux plein (note de décision 0009, étape 3) --------------------

#: La fiche de l'âge du 1° de L. 351-8, et la vue par génération qu'on en
#: fabrique.
FICHE_DE_L_AGE_DU_TAUX_PLEIN = "age_annulation_decote"
VUE_DE_L_AGE_DU_TAUX_PLEIN = "age_annulation_decote.csv"


def _jour(valeur) -> str | None:
    return None if valeur is None else str(valeur)[:10]


def _vaut(version: dict, jour: str) -> bool:
    debut, fin = (_jour(b) for b in version["bornes"][DATE_D_EFFET])
    return (debut is None or debut <= jour) and (fin is None or jour < fin)


def _a_la_date(fiche: dict, jour: str) -> dict | None:
    valent = [v for v in fiche.get("versions") or [] if _vaut(v, jour)]
    if len(valent) > 1:
        raise ValueError(f"{fiche['id']} : {', '.join(v['id'] for v in valent)} valent "
                         f"ensemble le {jour}")
    return valent[0] if valent else None


def _toutes_les_generations(age: float) -> dict[int, float]:
    return {mois: age for mois in range(rang(PREMIERE_GENERATION), rang(DERNIERE_GENERATION + 1))}


def ages_du_taux_plein_a_l_effet(taux_plein: dict, age_legal: dict, jour: str,
                                 racine: Path = RACINE_DONNEES) -> dict[int, float]:
    """L'âge du taux plein que la version de ``jour`` (AAAA-MM-JJ) oppose à
    chaque mois de naissance, au mois exact : sa valeur, ou celle qu'elle lit
    par son renvoi dans la version de l'âge légal du même jour, augmentée de
    ce que l'opération ajoute. Vide quand aucune version ne vaut ce jour-là.
    Le portage lit de même (``AgesAnnulationDecote.aLEffet``)."""
    version = _a_la_date(taux_plein, jour)
    if version is None:
        return {}
    contenu = version.get("contenu") or {}
    if "age" in (contenu.get("parametres") or {}):
        age = contenu["parametres"]["age"]
        # Sans règle commune (avant 1983), la version ne dit rien.
        return {} if age is None else _toutes_les_generations(au_mois(float(age)))
    (renvoi,) = contenu["renvois"]
    lue = _a_la_date(age_legal, jour)
    ou = f"{taux_plein['id']}.{version['id']}"
    if lue is None:
        raise ValueError(f"{ou} : aucune version de {age_legal['id']} le {jour}")
    parametres = (lue.get("contenu") or {}).get("parametres") or {}
    if renvoi["valeur"] in parametres:
        lus = _toutes_les_generations(float(parametres[renvoi["valeur"]]))
    elif renvoi["valeur"] == "age":
        lus = par_mois(age_legal, lue["id"], racine)
    else:
        raise ValueError(f"{ou} : lit « {renvoi['valeur']} », que "
                         f"{age_legal['id']}.{lue['id']} ne porte pas")
    ajout = renvoi_pour_le_moteur(renvoi)["mois"]
    return {mois: (round(age * 12) + ajout) / 12 for mois, age in lus.items()}


def _premier_du_mois_depuis(jour: str) -> int:
    """Le rang du premier 1er du mois à compter de ``jour``."""
    annee, mois, quantieme = (int(x) for x in jour.split("-"))
    return annee * 12 + mois - 1 + (quantieme > 1)


def _premier_jour(rang_du_mois: int) -> str:
    annee, mois = divmod(rang_du_mois, 12)
    return f"{annee:04d}-{mois + 1:02d}-01"


def vue_de_l_age_du_taux_plein(racine: Path = RACINE_DONNEES) -> list[tuple[str, float]]:
    """La table de l'âge du taux plein par génération, fabriquée depuis les
    versions de sa fiche : l'âge de chaque mois de naissance est celui de la
    version sous laquelle l'assuré l'atteint, ses âges comptés du mois qui
    suit sa naissance — la recherche du premier départ de l'âge légal
    (``AgesOuverture.premierDepart`` du portage), que
    ``AgesAnnulationDecote.age`` fait aussi. Les fenêtres se coupent à chaque
    borne des deux fiches, celle de l'âge du taux plein et celle de l'âge
    légal qu'elle lit."""
    regles = racine / "reference" / "regles"
    taux_plein = charger_yaml(regles / f"{FICHE_DE_L_AGE_DU_TAUX_PLEIN}.yaml")
    age_legal = charger_yaml(regles / f"{FICHE_DE_L_AGE_LEGAL}.yaml")
    erreurs = [e for e in renvois.controler(
        {chemin.stem: charger_yaml(chemin) for chemin in sorted(regles.glob("*.yaml"))})
        if f"{FICHE_DE_L_AGE_DU_TAUX_PLEIN}." in e]
    if erreurs:
        raise ValueError(" ; ".join(erreurs))
    bornes = sorted({_jour(b) for fiche in (taux_plein, age_legal) for v in fiche["versions"]
                     for b in v["bornes"][DATE_D_EFFET] if b is not None})
    fenetres = [(debut, fin, ages_du_taux_plein_a_l_effet(taux_plein, age_legal, debut, racine))
                for debut, fin in zip(bornes, bornes[1:] + [None])]
    table: dict[int, float] = {}
    for mois in range(rang(PREMIERE_GENERATION), rang(DERNIERE_GENERATION + 1)):
        origine = mois + 1
        for debut, fin, ages in fenetres:
            if mois not in ages:
                continue
            atteint = origine + round(ages[mois] * 12)
            date = max(atteint, _premier_du_mois_depuis(debut))
            if fin is None or _premier_jour(date) < fin:
                table[mois] = ages[mois]
                break
    return vue_par_generation(table)


# --- La durée requise (note de décision 0009, étape 3) ------------------------

#: La fiche de la durée requise pour le taux plein, et la vue par génération
#: qu'on en fabrique : la table du droit en vigueur, celle de sa dernière
#: version, que la certification confronte aux textes.
FICHE_DE_LA_DUREE_REQUISE = "duree_requise_par_generation"
VUE_DE_LA_DUREE_REQUISE = "duree_assurance_requise.csv"


def vue_de_la_duree_requise(racine: Path = RACINE_DONNEES) -> list[tuple[str, float]]:
    """La durée requise par génération du droit en vigueur, fabriquée depuis
    la dernière version de la fiche, résolue : en lignes (génération,
    trimestres), une à chaque janvier et à chaque coupure en cours d'année."""
    fiche = charger_yaml(racine / "reference" / "regles" / f"{FICHE_DE_LA_DUREE_REQUISE}.yaml")
    en_vigueur = next(v["id"] for v in fiche["versions"]
                      if v["bornes"][DATE_D_EFFET][1] is None)
    return vue_par_generation(par_mois(fiche, en_vigueur, racine, nom="trimestres"))


# --- La carrière longue (note de décision 0009, étape 3) ---------------------

#: La fiche du départ anticipé pour carrière longue (D. 351-1-1), et la colonne
#: que ses versions désignent : non une valeur par génération, mais des portes,
#: plusieurs par génération, chacune une borne de début, un âge et des durées.
FICHE_DE_LA_CARRIERE_LONGUE = "carriere_longue"

#: La fiche de la surcote du régime général (D. 351-1-4), dont chaque version
#: porte les taux par date de trimestre (étape 3, quatrième session).
FICHE_DE_LA_SURCOTE = "surcote_regime_general"
VALEUR_DES_PORTES = "age_depart"
VUE_DE_LA_CARRIERE_LONGUE = "carriere_longue.csv"

#: Les colonnes d'une porte, dans l'ordre où le moteur les lit (``CarriereLongue``
#: du portage) : la génération qui l'ouvre, la première qu'elle ne vise plus, la
#: borne de début, les trimestres de début, l'âge de départ, les trimestres
#: cotisés et d'assurance au-delà de la durée requise, la fiabilité.
COLONNES_DES_PORTES = ("generation", "generation_fin", "age_debut_maximum",
                       "trimestres_debut", "age_depart", "trimestres_supplementaires",
                       "trimestres_assurance_supplementaires", "fiabilite")


def _portes_pour_le_moteur(ou: str, table: dict, racine: Path) -> list[list]:
    """Les portes d'une version, dans l'ordre du fichier : ``[génération, fin
    exclue ou None, borne de début, trimestres de début, âge au mois exact,
    trimestres cotisés en plus, trimestres d'assurance en plus ou None,
    fiabilité]``."""
    lignes = _lignes(table, racine)
    if not lignes:
        raise ValueError(f"{ou} : aucune ligne de {table['fichier']} pour {table['lignes']}")
    portes = []
    for ligne in lignes:
        fin = float(ligne["generation_fin"])
        assurance = ligne["trimestres_assurance_supplementaires"].strip()
        portes.append([float(ligne["generation"]),
                       None if fin >= GENERATION_SANS_FIN else fin,
                       int(ligne["age_debut_maximum"]), int(ligne["trimestres_debut"]),
                       au_mois(float(ligne["age_depart"])),
                       int(ligne["trimestres_supplementaires"]),
                       int(assurance) if assurance else None,
                       _fiabilite(ligne["fiabilite"])])
    return portes


def _decimale(jour: str) -> str:
    """La date d'effet d'une version, en année décimale du premier mois, comme
    `carriere_longue.csv` l'écrit : ``2023-09-01`` -> ``2023.667``."""
    annee, mois = int(jour[:4]), int(jour[5:7])
    return f"{annee + (mois - 1) / 12.0:.3f}".rstrip("0").rstrip(".")


def vue_de_la_carriere_longue(racine: Path = RACINE_DONNEES) -> list[tuple[str, ...]]:
    """`carriere_longue.csv`, fabriquée depuis les versions de la fiche : les
    portes de chaque version, indexées par l'année décimale de sa date
    d'effet, chaque renvoi résolu contre la version de l'âge légal du même
    jour, mois de naissance par mois, comme le récupérateur les résolvait
    (``carriere_longue`` de ``scripts/fetch/dila_legi_parametres_retraite.py``)
    et comme le moteur les lit. En lignes de texte, dans l'ordre des colonnes
    du fichier, triées par date puis par génération."""
    regles = racine / "reference" / "regles"
    fiche = charger_yaml(regles / f"{FICHE_DE_LA_CARRIERE_LONGUE}.yaml")
    age_legal = charger_yaml(regles / f"{FICHE_DE_L_AGE_LEGAL}.yaml")
    erreurs = [e for e in renvois.controler(
        {chemin.stem: charger_yaml(chemin) for chemin in sorted(regles.glob("*.yaml"))})
        if f"{FICHE_DE_LA_CARRIERE_LONGUE}." in e]
    if erreurs:
        raise ValueError(" ; ".join(erreurs))
    vue = []
    for version in fiche["versions"]:
        contenu = version.get("contenu") or {}
        table = contenu.get("table")
        if not table:
            continue
        jour = _jour(version["bornes"][DATE_D_EFFET][0])
        lignes = _lignes(table, racine)
        for renvoi in contenu.get("renvois") or []:
            ou = f"{fiche['id']}.{version['id']}"
            lue = _a_la_date(age_legal, jour)
            if lue is None:
                raise ValueError(f"{ou} : aucune version de {age_legal['id']} le {jour}")
            ages = par_mois(age_legal, lue["id"], racine)
            ajout = renvoi_pour_le_moteur(renvoi)["mois"]
            modele = next(l for l in lignes if l["generation"] == str(PREMIERE_GENERATION)
                          and all(l[c] == str(v) for c, v in renvoi["ligne"].items()))
            premier, dernier = (_rang_du_jour(b) for b in renvoi["naissance"])
            precedent = None
            for mois in range(premier, dernier):
                age = (round(ages[mois] * 12) + ajout) / 12
                if precedent is not None and precedent["age_depart"] == f"{age:.2f}" \
                        and mois % 12:
                    precedent["generation_fin"] = cle(mois + 1)
                    continue
                precedent = {**modele, "generation": cle(mois), "generation_fin": cle(mois + 1),
                             "age_depart": f"{age:.2f}"}
                lignes.append(precedent)
        lignes.sort(key=lambda l: float(l["generation"]))
        vue += [(_decimale(jour),) + tuple(l[c] for c in COLONNES_DES_PORTES) for l in lignes]
    return vue
