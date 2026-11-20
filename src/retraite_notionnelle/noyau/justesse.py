"""La carte de justesse : l'état de chaque partie, calculé depuis ses preuves.

Action 194, étape A. La carte des règles (``carte.py``) porte un état que la
fiche déclare : « conforme », « approchée ». Ce module en calcule un autre,
que personne n'écrit : il lit les preuves, et dit de chaque PARTIE — une règle
sur une période, c'est-à-dire une version de fiche, ou la fiche entière tant
qu'elle n'est pas découpée — lequel de six états elle a.

    prouvee_avec_temoin    texte tracé, grille indépendante verte, et au
                           moins un témoin extérieur d'accord ;
    prouvee_au_texte_seul  texte tracé et grille indépendante verte ;
    fausse                 un écart est établi ; son action, si une preuve
                           la nomme ;
    approchee              une simplification que la fiche déclare ;
    non_verifiee           personne n'a encore apporté de preuve ;
    hors_champ             le simulateur ne prétend pas la calculer.

Seul le texte tranche. Une GRILLE INDÉPENDANTE établit la justesse : des
valeurs attendues posées depuis le seul texte, par quelqu'un qui n'a pas lu le
code, sur des cas qui couvrent chaque seuil de la règle. Un TÉMOIN — un
exemple officiel, un autre moteur, le simulateur d'une caisse, une
notification de pension — rassure quand il concorde, et désigne où relire
quand il diverge : il ne prouve pas seul.

Les preuves
-----------

Une preuve est un fichier de ``data/reference/preuves/``, sous le nom de son
identifiant :

    schema_version: 1
    id: <le nom du fichier>
    sorte: grille_independante | exemple_officiel | moteur_exterieur
           | simulateur_de_caisse | notification_de_pension
    etage: regle
    parties: [{fiche: <fiche>, version: <version>}]
    source: {auteur: …, reference: …, etabli_le: AAAA-MM-JJ, version: …}
    independance: <une grille dit comment elle s'est passée du code>
    seuils: [<les seuils de la règle que ses cas couvrent>]
    cas: [<un cas, au schéma d'un exemple officiel>]

Un cas suit le schéma de ``tests/temoins/exemples_officiels.yaml`` : la
carrière minuscule, les grandeurs attendues (``attendu``), et, quand le
simulateur ne les rend pas, un écart connu (``ecart_connu`` : ``modele``,
``explication``, ``action``, ``depuis``). ``tests/test_justesse.py`` rejoue
chaque cas par la confrontation des exemples officiels : une grille est verte
parce que ce test passe, et un cas rouge se répare ou se déclare en écart, ce
qui fait la partie fausse.

Les exemples officiels du dépôt n'ont pas à être recopiés : chacun est déjà
un témoin des fiches et des versions qui le citent (``carte.exemples_de``), et
ce module les lit là. Un exemple d'accord ne témoigne que pour la version qui
le cite ; un exemple en écart que seule la fiche cite marque toutes ses
versions, le doute profitant au faux.

Ce que ce module ne fait pas
----------------------------

Il ne rejoue rien : il lit ce que les preuves déclarent, et les tests tiennent
ces déclarations vraies. Il ne connaît encore que l'étage des règles ; les
barèmes, les régimes de bout en bout, les cas types et les totaux auront leurs
preuves aux étapes suivantes de l'action. Les confrontations aux autres
moteurs que les fiches racontent en prose (``referents``) se comptent, sans
valoir témoin : rien n'y dit, cas par cas, ce qui concorde. La confrontation à
TRAJECTOiRE le dit, elle, quantité par quantité (:func:`moteur_exterieur`) ;
mais chacun de ses cas est une carrière entière, que rien ne rattache à une
règle : elle se lit à côté de la carte, sans changer l'état d'aucune partie.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from ..config import RACINE_DONNEES
from ..donnees.chargement import charger_yaml
from ..somme import somme_ordonnee
from . import carte

RACINE = RACINE_DONNEES.parent
PREUVES = RACINE_DONNEES / "reference" / "preuves"
EXEMPLES = RACINE / "tests" / "temoins" / "exemples_officiels.yaml"
INVENTAIRE = RACINE_DONNEES / "reference" / "regimes" / "inventaire.yaml"
#: La confrontation à TRAJECTOiRE, cas par cas et quantité par quantité, que
#: ``scripts/confronter_trajectoire.py`` écrit (action 137).
TRAJECTOIRE = RACINE / "tests" / "temoins" / "trajectoire_3" / "ecarts.json"

#: Les six états d'une partie, du plus sûr au moins sûr.
ETATS = ("prouvee_avec_temoin", "prouvee_au_texte_seul", "fausse", "approchee",
         "non_verifiee", "hors_champ")
PROUVEES = ETATS[:2]
#: Ce qui établit la justesse, et ce qui la témoigne.
GRILLE = "grille_independante"
TEMOINS = ("exemple_officiel", "moteur_exterieur", "simulateur_de_caisse",
           "notification_de_pension")
SORTES = (GRILLE, *TEMOINS)
#: Les étages de la carte ; seul le premier a ses preuves à l'étape A.
ETAGES = ("regle",)
#: La famille des fiches dont aucun régime n'est à l'inventaire.
SANS_FAMILLE = "sans famille"
TOUTE_LA_CARTE = "toute la carte"


def lecture_tracee(version: dict) -> bool:
    """La lecture d'une version laisse-t-elle une trace : pour chaque texte
    cité, sa date de lecture ou sa citation exacte (note de décision 0009,
    cliquet des lectures sans trace)."""
    textes = version.get("textes") or []
    return bool(textes) and all(
        isinstance(texte, dict) and bool(texte.get("lu_le") or texte.get("citation"))
        for texte in textes)


def exemples(chemin: Path = EXEMPLES) -> list[dict]:
    """Les exemples officiels du dépôt."""
    return charger_yaml(chemin)["exemples"]


def preuves(dossier: Path = PREUVES) -> list[dict]:
    """Les preuves du dossier, dans l'ordre de leurs noms ; aucune, s'il
    n'existe pas encore."""
    return [charger_yaml(chemin) for chemin in sorted(dossier.glob("*.yaml"))]


def _versions(fiche: dict) -> list[dict]:
    return [v for v in fiche.get("versions") or [] if isinstance(v, dict)]


def controler_preuve(preuve: dict, fiches: dict[str, dict]) -> list[str]:
    """Ce qui ne va pas dans une preuve : rien, si elle suit son format."""
    nom = preuve.get("id")
    erreurs = []

    def faute(quoi: str) -> None:
        erreurs.append(f"{nom} : {quoi}")

    if preuve.get("schema_version") != 1:
        faute("elle dit son schema_version, 1")
    sorte = preuve.get("sorte")
    if sorte not in SORTES:
        faute(f"sa sorte est l'une de {', '.join(SORTES)}")
    if preuve.get("etage") not in ETAGES:
        faute(f"son étage est l'un de {', '.join(ETAGES)}")
    parties = preuve.get("parties")
    if not isinstance(parties, list) or not parties:
        faute("elle nomme les parties qu'elle couvre")
    for partie in parties if isinstance(parties, list) else []:
        fiche = fiches.get(partie.get("fiche")) if isinstance(partie, dict) else None
        if fiche is None:
            faute(f"la partie {partie} ne nomme pas une fiche de la carte")
        elif partie.get("version") is None:
            if _versions(fiche):
                faute(f"la fiche {fiche['id']} est découpée : la partie nomme sa version")
        elif partie["version"] not in {v["id"] for v in _versions(fiche)}:
            faute(f"la fiche {fiche['id']} n'a pas de version {partie['version']}")
    source = preuve.get("source")
    if not isinstance(source, dict):
        faute("elle dit sa source")
        source = {}
    else:
        for champ in ("auteur", "reference"):
            if not str(source.get(champ) or "").strip():
                faute(f"sa source dit son champ {champ}")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(source.get("etabli_le"))):
            faute("sa source dit quand elle a été établie, AAAA-MM-JJ")
    if sorte == GRILLE:
        if len(str(preuve.get("independance") or "").split()) < 8:
            faute("une grille dit comment elle s'est passée du code, en une phrase")
        if not preuve.get("seuils"):
            faute("une grille nomme les seuils de la règle que ses cas couvrent")
    if sorte in ("moteur_exterieur", "simulateur_de_caisse") and not source.get("version"):
        faute("un moteur ou un simulateur dit la version qui a répondu")
    cas = preuve.get("cas")
    if not isinstance(cas, list) or not cas:
        faute("elle porte ses cas")
    noms = [c.get("id") for c in cas or [] if isinstance(c, dict)]
    if len(set(noms)) != len(noms) or None in noms:
        faute("chacun de ses cas a son identifiant, qu'aucun autre ne porte")
    for c in cas if isinstance(cas, list) else []:
        if not isinstance(c, dict) or not c.get("attendu") or not c.get("enonce"):
            faute(f"le cas {c.get('id') if isinstance(c, dict) else c} dit son énoncé "
                  "et ce qu'il attend")
            continue
        ecart = c.get("ecart_connu")
        if ecart is None:
            continue
        if (set(ecart) != {"modele", "explication", "action", "depuis"}
                or not ecart["modele"] or not set(ecart["modele"]) <= set(c["attendu"])
                or len(str(ecart["explication"]).split()) < 8
                or not isinstance(ecart["action"], int)
                or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(ecart["depuis"]))):
            faute(f"l'écart connu du cas {c['id']} dit la valeur du modèle, pourquoi, "
                  "le numéro de son action et depuis quand")
    return erreurs


def controler(dossier: Path = PREUVES, fiches: dict[str, dict] | None = None) -> list[str]:
    """Ce qui ne va pas dans les preuves du dossier : rien, si elles tiennent.
    Chacune porte le nom de son fichier, suit son format, et aucun cas ne
    porte l'identifiant d'un autre, ni celui d'un exemple officiel."""
    fiches = carte.fiches() if fiches is None else fiches
    erreurs = []
    vus: dict[str, str] = {}
    for chemin in sorted(dossier.glob("*.yaml")):
        preuve = charger_yaml(chemin)
        if not isinstance(preuve, dict) or preuve.get("id") != chemin.stem:
            erreurs.append(f"{chemin.stem} : la preuve porte le nom de son fichier")
            continue
        erreurs += controler_preuve(preuve, fiches)
        for cas in preuve.get("cas") or []:
            if isinstance(cas, dict) and cas.get("id") in vus:
                erreurs.append(f"{chemin.stem} : le cas {cas['id']} est déjà celui de "
                               f"{vus[cas['id']]}")
            elif isinstance(cas, dict):
                vus[cas.get("id")] = chemin.stem
    return erreurs


def _approchees(fiche: dict) -> set[str] | None:
    """Les versions qu'une fiche approchée déclare approchées ; ``None``
    quand c'est la fiche entière — elle n'en déclare aucune, ou l'une de ses
    approximations ne nomme pas ses versions."""
    approximations = fiche.get("approximations") or []
    touchees: set[str] = set()
    for approximation in approximations:
        versions = approximation.get("version") if isinstance(approximation, dict) else None
        if isinstance(versions, str):
            versions = [versions]
        if not versions:
            return None
        touchees |= {str(v) for v in versions}
    connues = {v["id"] for v in _versions(fiche)}
    # Une version nommée en prose, que la fiche ne porte pas, ne situe rien.
    return touchees if approximations and touchees <= connues else None


def etats(fiches: dict[str, dict] | None = None, officiels: list[dict] | None = None,
          declarees: list[dict] | None = None) -> dict[tuple[str, str | None], dict]:
    """L'état de chaque partie de la carte, sous ``(fiche, version)`` — la
    version est ``None`` pour une fiche qui n'est pas découpée.

    Chaque partie dit son état, ses régimes, si son texte est tracé, ses
    grilles vertes, ses témoins d'accord, ses écarts, les actions que ses
    écarts nomment, et les témoins que sa fiche cite sans dire pour quelle
    version (``temoins_a_situer``).
    """
    fiches = carte.fiches() if fiches is None else fiches
    officiels = exemples() if officiels is None else officiels
    declarees = preuves() if declarees is None else declarees
    en_ecart = {e["id"] for e in officiels if e.get("ecart_connu")}
    connus = {e["id"] for e in officiels}

    sortie: dict[tuple[str, str | None], dict] = {}
    for nom, fiche in fiches.items():
        versions = _versions(fiche)
        de_la_fiche = [e for e in fiche.get("exemples") or [] if e in connus]
        approchees = _approchees(fiche) if fiche.get("etat") == "approchee" else set()
        for version in versions or [None]:
            cites = de_la_fiche if version is None else [
                e for e in (version.get("exemples") if isinstance(version.get("exemples"), list)
                            else []) if e in connus]
            sortie[(nom, version and version["id"])] = {
                "fiche": nom, "version": version and version["id"],
                "regimes": list(fiche.get("regimes") or []),
                "declare": fiche.get("etat"),
                "decoupee": version is not None,
                "supposee": version is not None and version.get("statut") == "supposee",
                "tracee": (version is not None and version.get("statut", "lue") == "lue"
                           and lecture_tracee(version)),
                "approchee": approchees is None or (version is not None
                                                    and version["id"] in approchees),
                "grilles": [],
                "temoins": [e for e in cites if e not in en_ecart],
                # Un écart que seule la fiche cite touche chacune de ses versions.
                "ecarts": [e for e in dict.fromkeys(cites + de_la_fiche) if e in en_ecart],
                "actions": [],
                "temoins_a_situer": [] if version is None else [
                    e for e in de_la_fiche if e not in en_ecart],
            }
    for preuve in declarees:
        ecarts = [c for c in preuve["cas"] if c.get("ecart_connu")]
        for vise in preuve["parties"]:
            partie = sortie.get((vise["fiche"], vise.get("version")))
            if partie is None:
                continue
            if ecarts:
                partie["ecarts"].append(preuve["id"])
                partie["actions"] += [c["ecart_connu"]["action"] for c in ecarts
                                      if c["ecart_connu"].get("action") is not None]
            elif preuve["sorte"] == GRILLE:
                partie["grilles"].append(preuve["id"])
            else:
                partie["temoins"].append(preuve["id"])
    for partie in sortie.values():
        partie["actions"] = sorted(set(partie["actions"]))
        partie["etat"] = _etat(partie)
    return sortie


def _etat(partie: dict) -> str:
    if partie["declare"] == "pas_encore_modelisee":
        return "hors_champ"
    if partie["ecarts"] or partie["declare"] == "manquante":
        return "fausse"
    if partie["declare"] == "approchee" and partie["approchee"]:
        return "approchee"
    if partie["grilles"] and partie["tracee"]:
        return "prouvee_avec_temoin" if partie["temoins"] else "prouvee_au_texte_seul"
    return "non_verifiee"


def nom_de_partie(fiche: str, version: str | None) -> str:
    """Le nom sous lequel le cliquet inscrit une partie."""
    return fiche if version is None else f"{fiche} / {version}"


def prouvees(calcules: dict | None = None) -> set[str]:
    """Les parties prouvées, avec ou sans témoin, par leur nom."""
    calcules = etats() if calcules is None else calcules
    return {nom_de_partie(*cle) for cle, partie in calcules.items()
            if partie["etat"] in PROUVEES}


def reculs(prouvees_du_jour: set[str], liste: dict) -> tuple[list[str], list[str]]:
    """Le cliquet : les parties inscrites qui ne sont plus prouvées, et
    celles qui le sont sans être inscrites.

    Une partie ne quitte la liste qu'en passant sous ``retirees``, avec le
    jour et une raison d'au moins huit mots ; prouvée de nouveau, elle se
    réinscrit.
    """
    inscrites = set(liste.get("prouvees") or [])
    retirees = liste.get("retirees") or {}
    sans_raison = {nom for nom, dit in retirees.items()
                   if not isinstance(dit, dict) or len(str(dit.get("raison") or "").split()) < 8
                   or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(dit.get("le")))}
    perdues = (inscrites - prouvees_du_jour) | (sans_raison - prouvees_du_jour)
    return sorted(perdues), sorted(prouvees_du_jour - inscrites)


def familles(chemin: Path = INVENTAIRE) -> dict[str, str]:
    """La famille de chaque régime de l'inventaire."""
    return {ligne["code"]: ligne["famille"] for ligne in charger_yaml(chemin)["inventaire"]}


def _confrontee_a_un_moteur(fiche: dict) -> bool:
    referents = fiche.get("referents") or {}
    return isinstance(referents, dict) and any(
        isinstance(dit, dict) and dit.get("confrontation") for dit in referents.values())


def par_famille(calcules: dict | None = None, fiches: dict[str, dict] | None = None,
                de_regime: dict[str, str] | None = None) -> list[dict]:
    """La carte, famille de régimes par famille, puis toute la carte.

    Une partie compte dans chacune des familles de ses régimes, et une fois
    dans le total. Chaque ligne dit ses parties, leur nombre dans chaque
    état, celles dont le texte est tracé, celles qu'un exemple officiel
    d'accord témoigne, et, comptées en fiches, les fiches, celles qui se
    disent conformes et celles qu'une confrontation à un autre moteur
    raconte.
    """
    fiches = carte.fiches() if fiches is None else fiches
    calcules = etats(fiches) if calcules is None else calcules
    de_regime = familles() if de_regime is None else de_regime

    def ligne(nom: str) -> dict:
        return {"famille": nom, "parties": 0, **{etat: 0 for etat in ETATS},
                "tracees": 0, "temoignees": 0, "supposees": 0,
                "fiches": set(), "conformes": set(), "moteurs": set()}

    lignes: dict[str, dict] = {}
    total = ligne(TOUTE_LA_CARTE)
    for (nom, _), partie in calcules.items():
        siennes = sorted({de_regime[r] for r in partie["regimes"] if r in de_regime})
        for famille in [*(siennes or [SANS_FAMILLE]), None]:
            cible = total if famille is None else lignes.setdefault(famille, ligne(famille))
            cible["parties"] += 1
            cible[partie["etat"]] += 1
            cible["tracees"] += partie["tracee"]
            cible["temoignees"] += bool(partie["temoins"])
            cible["supposees"] += partie["supposee"]
            cible["fiches"].add(nom)
            if partie["declare"] == "conforme":
                cible["conformes"].add(nom)
            if _confrontee_a_un_moteur(fiches[nom]):
                cible["moteurs"].add(nom)
    sortie = [lignes[nom] for nom in sorted(lignes)] + [total]
    for cible in sortie:
        for champ in ("fiches", "conformes", "moteurs"):
            cible[champ] = len(cible[champ])
    return sortie


def moteur_exterieur(chemin: Path = TRAJECTOIRE) -> dict | None:
    """Ce qu'un autre moteur confirme, quantité par quantité : pour chacune,
    le nombre de cas qui la confrontent et le nombre de ceux qui concordent ;
    ``None`` si la confrontation n'est pas au dépôt. Un écart n'y est pas une
    erreur du dépôt : seul le texte tranche."""
    if not chemin.is_file():
        return None
    lu = json.loads(chemin.read_text(encoding="utf-8"))
    quantites: dict[str, tuple[int, int]] = {}
    for cas in lu["cas"].values():
        for nom, dit in cas["quantites"].items():
            vus, d_accord = quantites.get(nom, (0, 0))
            quantites[nom] = (vus + 1, d_accord + (dit["statut"] == "concorde"))
    return {"modele": lu["modele"], "version": lu["version"], "cas": len(lu["cas"]),
            "quantites": dict(sorted(quantites.items())),
            "confrontees": somme_ordonnee(vus for vus, _ in quantites.values()),
            "concordent": somme_ordonnee(d_accord for _, d_accord in quantites.values())}
