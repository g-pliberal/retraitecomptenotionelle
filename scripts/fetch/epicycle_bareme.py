#!/usr/bin/env python3
"""Le barème du décret n° 82-1105 : l'indice majoré de chaque indice brut, de 1983 à aujourd'hui.

    python scripts/fetch/epicycle_bareme.py      # quelques secondes, ou quelques
                                                 # minutes si data.gouv.fr coupe
    python scripts/verifier_donnees.py --appliquer

LE BARÈME. Une grille donne l'indice BRUT de chaque échelon ; le traitement se
calcule sur l'indice MAJORÉ, que le barème A annexé au décret n° 82-1105 du
23 décembre 1982 fait correspondre à chaque indice brut, de 100 à 1015 (1027
depuis 2018). Vingt-huit décrets l'ont remplacé depuis le 1er janvier 1983 : par
des points uniformes, ajoutés à tous les indices majorés (1988 à 1991, 1999,
2006, 2024), ou par des points donnés au bas de l'échelle (1998 à 2013, 2021,
2023). Le Noyau RH de l'État n'en a qu'une ligne avant novembre 2006, et
prolonge à tort jusqu'en 1900 les valeurs de mai 2008 des indices bruts 100 à
302 (action 158).

LA SOURCE. Le LEGI ne reproduit les tableaux que depuis le 1er juillet 2007 ;
avant, l'article 1er dit « tableau non reproduit », et les décrets au JORF
renvoient au Journal officiel imprimé, que seul un poste lit. Épicycle publie
sur data.gouv.fr, sous licence CC BY-SA, une colonne par version, de 1972 à
2024 (jeu 61c26e0a8b4b58472b8d0907). Ses treize colonnes de 2007 à 2024 sont les
tableaux du LEGI, couple pour couple ; avant, elles redonnent chaque couple
« indice majoré X (indice brut Y) » que les articles 7 à 10 du décret
n° 85-1148 écrivent, de 1985 à 2008. Le récupérateur, quand l'index LEGI du
dépôt est là, refait la première confrontation et refuse d'écrire sur un écart.

CE QU'IL Y AJOUTE. Chaque version est datée par son texte (``VERSIONS``), et non
par l'intitulé de la colonne : celle qu'Épicycle date du 1er septembre 1979 est
le barème du décret n° 82-1105, qui s'applique au 1er janvier 1983. La source
omet la version du 1er juillet 1999 (décret n° 99-491) : elle se déduit de celle
du 1er décembre 1999, moins le point uniforme que le décret n° 99-943 ajoute à
tous (lecture ``deduite``). Huit valeurs, recopiées de l'indice brut suivant,
démentent les points uniformes des décrets qui les entourent : chacune prend la
valeur que les versions voisines donnent ensemble (``CORRECTIONS``, lecture
``corrigee``). Le récupérateur refuse une version uniforme qui ne l'est pas, un
indice majoré qui baisse, une correction que la source ne justifie plus.

CE QU'IL ÉCRIT. Sous ``data/reference/grilles/bareme/`` : ``versions.csv``, les
versions et leurs textes ; ``indices.csv``, l'indice majoré de chaque indice
brut, période par période. Et ``data/brut/epicycle_bareme.json``, que
``scripts/verifier_donnees.py`` confronte au fichier de référence : ``haute``
pour ce que la source dit ou que les décrets en déduisent, ``estimee`` pour les
valeurs corrigées.

CE QUE LA DONNÉE NE DIT PAS. Le minimum de traitement, que l'article 8 du décret
n° 85-1148 sert aux indices majorés plus bas (depuis 2024, le Noyau RH le mêle
à son barème) ; la hors-échelle, payée par l'article 6 du même décret ; avant
1983, les indices nouveaux majorés, que la source donne depuis 1972 et que ce
fichier ne reprend pas.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]

JEU = "61c26e0a8b4b58472b8d0907"
API = f"https://www.data.gouv.fr/api/1/datasets/{JEU}/"
PAGE = f"https://www.data.gouv.fr/datasets/{JEU}"
LOCAL = RACINE / "data" / "brut" / "epicycle_bareme.csv"
BRUT = RACINE / "data" / "brut" / "epicycle_bareme.json"
INDEX_LEGI = RACINE / "data" / "brut" / "dila" / "legi.sqlite"
REFERENCE = RACINE / "data" / "reference" / "grilles" / "bareme"


@dataclass(frozen=True)
class Version:
    """Une version du barème A : sa date d'effet, le décret qui l'annexe, sa
    date de signature, le texte au JORF, l'article du LEGI qui la date
    (l'article 1er, jusqu'en 2006) ou qui en reproduit le tableau (depuis
    2007), les points uniformes que le titre du décret attribue à tous, et la
    colonne de la source (``None`` : absente, déduite)."""

    debut: str
    texte: str
    signature: str
    jorf: str
    legi: str
    points: int | None
    colonne: str | None


V = Version
VERSIONS = (
    V("1983-01-01", "82-1105", "1982-12-23", "JORFTEXT000000703628", "", None, "1979-09-01"),
    V("1985-01-01", "86-166", "1986-01-31", "JORFTEXT000000881232", "LEGIARTI000006455029",
      None, "1985-01-01"),
    V("1988-10-01", "88-1067", "1988-11-23", "JORFTEXT000000504298", "LEGIARTI000006455030",
      2, "1988-10-01"),
    V("1989-02-01", "89-64", "1989-02-04", "JORFTEXT000000882942", "LEGIARTI000006455031",
      1, "1989-02-01"),
    V("1990-01-01", "90-321", "1990-04-05", "JORFTEXT000000166950", "LEGIARTI000006455032",
      1, "1990-01-01"),
    V("1991-08-01", "91-1191", "1991-11-18", "JORFTEXT000000538342", "LEGIARTI000006455033",
      2, "1991-08-01"),
    V("1998-07-01", "98-462", "1998-06-10", "JORFTEXT000000740811", "LEGIARTI000006455034",
      None, "1998-07-01"),
    # Le LEGI intervertit les dates de ses deux versions de 1999 : celle qui dit
    # « 1er avril » commence le 13 juin, celle qui dit « 1er juillet » le 20 mars.
    V("1999-04-01", "99-208", "1999-03-17", "JORFTEXT000000393446", "LEGIARTI000006455035",
      1, "1999-04-01"),
    V("1999-07-01", "99-491", "1999-06-10", "JORFTEXT000000394805", "LEGIARTI000006455036",
      None, None),
    V("1999-12-01", "99-943", "1999-11-12", "JORFTEXT000000397436", "LEGIARTI000006455037",
      1, "1999-12-01"),
    V("2001-05-01", "2001-370", "2001-04-25", "JORFTEXT000000210853", "LEGIARTI000006455038",
      None, "2001-05-01"),
    V("2001-07-01", "2001-559", "2001-06-28", "JORFTEXT000000579944", "LEGIARTI000006455039",
      None, "2001-07-01"),
    V("2004-07-01", "2004-679", "2004-07-09", "JORFTEXT000000620605", "LEGIARTI000006455040",
      None, "2004-07-01"),
    V("2005-07-01", "2005-726", "2005-06-29", "JORFTEXT000000810890", "LEGIARTI000006455041",
      None, "2005-07-01"),
    V("2006-07-01", "2006-759", "2006-06-29", "JORFTEXT000000422923", "LEGIARTI000006455042",
      None, "2006-07-01"),
    V("2006-11-01", "2006-1283", "2006-10-19", "JORFTEXT000000615828", "LEGIARTI000006455043",
      1, "2006-11-01"),
    V("2007-07-01", "2007-1054", "2007-06-28", "JORFTEXT000000649573", "LEGIARTI000018191834",
      None, "2007-07-01"),
    V("2008-05-01", "2008-400", "2008-04-24", "JORFTEXT000018693706", "LEGIARTI000018728052",
      None, "2008-05-01"),
    V("2008-07-01", "2008-622", "2008-06-27", "JORFTEXT000019108374", "LEGIARTI000023596059",
      None, "2008-07-01"),
    V("2009-07-01", "2009-824", "2009-07-03", "JORFTEXT000020815910", "LEGIARTI000020973724",
      None, "2009-07-01"),
    V("2011-01-01", "2011-51", "2011-01-13", "JORFTEXT000023417934", "LEGIARTI000023427645",
      None, "2011-01-01"),
    V("2012-01-01", "2012-37", "2012-01-11", "JORFTEXT000025135486", "LEGIARTI000025140239",
      None, "2012-01-01"),
    # Le LEGI fait commencer ce tableau le 7 juillet, lendemain de la publication ;
    # l'article 1er dit « à compter du 1er juillet 2012 ».
    V("2012-07-01", "2012-853", "2012-07-05", "JORFTEXT000026149212", "LEGIARTI000026151662",
      None, "2012-07-01"),
    V("2013-01-01", "2013-33", "2013-01-10", "JORFTEXT000026924624", "LEGIARTI000026928467",
      None, "2013-01-01"),
    V("2017-01-01", "2017-85", "2017-01-26", "JORFTEXT000033927793", "LEGIARTI000034061028",
      None, "2017-01-01"),
    V("2018-01-01", "2017-85", "2017-01-26", "JORFTEXT000033927793", "LEGIARTI000034079564",
      None, "2018-01-01"),
    V("2021-04-01", "2021-406", "2021-04-08", "JORFTEXT000043339489", "LEGIARTI000043341340",
      None, "2021-04-01"),
    V("2023-07-01", "2023-519", "2023-06-28", "JORFTEXT000047749211", "LEGIARTI000047751782",
      None, "2023-07-01"),
    V("2024-01-01", "2023-519", "2023-06-28", "JORFTEXT000047749211", "LEGIARTI000047780477",
      None, "2024-01-01"),
)

#: Les valeurs de la source recopiées de l'indice brut suivant : (version,
#: indice brut) → (valeur de la source, valeur retenue, motif). Chacune fait un
#: saut de deux points que le barème ne fait nulle part ailleurs au-dessus de
#: l'indice brut 400, et la valeur retenue est celle que les versions voisines
#: donnent ensemble, par les points qui les séparent.
CORRECTIONS = {
    ("1983-01-01", 621): (509, 510, "le barème de 1985 lui donne 512, deux points de plus, "
                                    "comme aux 915 autres indices et aux six que ses textes écrivent"),
    ("1989-02-01", 467): (402, 401, "400 en octobre 1988 et 402 en 1990, un point uniforme chaque fois"),
    ("1989-02-01", 792): (646, 645, "644 en octobre 1988 et 646 en 1990, un point uniforme chaque fois"),
    ("1990-01-01", 554): (466, 465, "464 en 1989, un point de plus ; 467 en 1991, deux points de plus"),
    ("1990-01-01", 567): (476, 475, "474 en 1989, un point de plus ; 477 en 1991, deux points de plus"),
    ("1990-01-01", 607): (506, 505, "504 en 1989, un point de plus ; 507 en 1991, deux points de plus"),
    ("1990-01-01", 633): (526, 525, "524 en 1989, un point de plus ; 527 en 1991, deux points de plus"),
    ("2004-07-01", 457): (398, 399, "399 en 2001 et en 2005 : un indice majoré ne baisse pas"),
}

MOIS = ("janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|septembre|octobre"
        "|novembre|d[ée]cembre")


# ---------------------------------------------------------------------------
# La lecture
# ---------------------------------------------------------------------------

def lire_csv(texte: str) -> dict[str, dict[int, int]]:
    """Le fichier d'Épicycle : une colonne ``indices_bruts``, puis une colonne
    par date d'effet ; chaque colonne rendue sous sa date, ses cases vides
    omises. Une date ou une valeur illisible arrête tout."""
    lignes = csv.reader(io.StringIO(texte))
    entete = next(lignes)
    for colonne in entete[1:]:
        date.fromisoformat(colonne)
    colonnes: dict[str, dict[int, int]] = {colonne: {} for colonne in entete[1:]}
    for ligne in lignes:
        if not ligne:
            continue
        brut = int(ligne[0])
        for colonne, valeur in zip(entete[1:], ligne[1:]):
            if valeur.strip():
                colonnes[colonne][brut] = int(valeur)
    return colonnes


def lire_tableau_legi(texte: str) -> dict[int, int]:
    """Un tableau du barème tel que l'index LEGI le garde : des couples
    « brut majoré », coupés d'en-têtes datés et de tirets, les milliers parfois
    écrits « 1 001 ». Un même indice brut deux fois avec deux valeurs arrête
    tout ; deux fois avec la même (un saut de page) passe."""
    texte = re.sub(r"Conformément à l'article \d+ du décret n° [\d-]+ du \d+ \w+ \d{4}, "
                   r"ces dispositions entrent en vigueur le 1\s*er \w+ \d{4}\.", " ", texte)
    texte = re.sub(rf"(?i)\b(?:du|au|à compter du)?\s*1\s*er\s+(?:{MOIS})\s+(?:19|20)\d\d",
                   " ", texte)
    texte = re.sub(r"(?<=\s)1 (\d{3})(?=\s)", r"1\1", f" {texte} ")
    nombres = [int(n) for n in re.findall(r"(?<!\d)\d{3,4}(?!\d)", texte)]
    if len(nombres) % 2:
        raise ValueError(f"{len(nombres)} nombres : un couple est incomplet")
    couples: dict[int, int] = {}
    for brut, majore in zip(nombres[::2], nombres[1::2]):
        if couples.setdefault(brut, majore) != majore:
            raise ValueError(f"indice brut {brut} : {couples[brut]} puis {majore}")
    return couples


# ---------------------------------------------------------------------------
# La construction
# ---------------------------------------------------------------------------

def _veille(jour: str) -> str:
    return (date.fromisoformat(jour) - timedelta(days=1)).isoformat()


def construire(colonnes: dict[str, dict[int, int]], versions=VERSIONS,
               corrections=CORRECTIONS) -> list[dict]:
    """Les périodes de chaque indice brut : une ligne par valeur, de la version
    qui la pose à la veille de celle qui la change ; la lecture de la version
    qui l'a posée. Refuse ce que les décrets démentent."""
    valeurs: dict[str, dict[int, int]] = {}
    lectures: dict[str, dict[int, str]] = {}
    for version in versions:
        if version.colonne is not None:
            valeurs[version.debut] = dict(colonnes[version.colonne])
            lectures[version.debut] = dict.fromkeys(valeurs[version.debut], "lue")
    for (debut, brut), (lu, retenu, motif) in corrections.items():
        source = valeurs.get(debut, {}).get(brut)
        if source != lu:
            raise ValueError(f"correction {debut}, indice brut {brut} : la source donne "
                             f"{source}, et non {lu} — la revoir ({motif})")
        valeurs[debut][brut] = retenu
        lectures[debut][brut] = "corrigee"
    for rang, version in enumerate(versions):
        if version.colonne is not None:
            continue
        suivante = versions[rang + 1] if rang + 1 < len(versions) else None
        if suivante is None or suivante.points is None or suivante.debut not in valeurs:
            raise ValueError(f"{version.debut} : absente de la source, et la version suivante "
                             "n'ajoute pas un nombre de points uniforme dont la déduire")
        valeurs[version.debut] = {brut: majore - suivante.points
                                  for brut, majore in valeurs[suivante.debut].items()}
        lectures[version.debut] = dict.fromkeys(valeurs[version.debut], "deduite")

    for precedente, version in zip(versions, versions[1:]):
        avant, apres = valeurs[precedente.debut], valeurs[version.debut]
        communs = sorted(set(avant) & set(apres))
        if version.points is not None:
            ecarts = [b for b in communs if apres[b] - avant[b] != version.points]
            if ecarts:
                raise ValueError(f"{version.debut} : {version.points} point(s) uniforme(s), et "
                                 f"{len(ecarts)} indice(s) brut(s) qui s'en écartent : "
                                 f"{ecarts[:5]}")
        baisses = [b for b in communs if apres[b] < avant[b]]
        if baisses:
            raise ValueError(f"{version.debut} : l'indice majoré baisse aux indices bruts "
                             f"{baisses[:5]}")
    for version in versions:
        bruts = sorted(valeurs[version.debut])
        inversions = [s for b, s in zip(bruts, bruts[1:])
                      if valeurs[version.debut][s] < valeurs[version.debut][b]]
        if inversions:
            raise ValueError(f"{version.debut} : l'indice majoré baisse quand l'indice brut "
                             f"monte, aux indices bruts {inversions[:5]}")

    periodes: list[dict] = []
    for brut in sorted({b for v in valeurs.values() for b in v}):
        courante: dict | None = None
        for version in versions:
            majore = valeurs[version.debut].get(brut)
            if courante is not None and majore == courante["indice_majore"]:
                continue
            if courante is not None:
                courante["fin"] = _veille(version.debut)
                periodes.append(courante)
                courante = None
            if majore is not None:
                courante = {"indice_brut": brut, "debut": version.debut, "fin": "",
                            "indice_majore": majore,
                            "lecture": lectures[version.debut][brut]}
        if courante is not None:
            periodes.append(courante)
    return periodes


def par_version(colonnes: dict[str, dict[int, int]], versions=VERSIONS,
                corrections=CORRECTIONS) -> dict[str, dict[int, int]]:
    """Le barème de chaque version, tel que les périodes le disent."""
    periodes = construire(colonnes, versions, corrections)
    return {v.debut: {p["indice_brut"]: p["indice_majore"] for p in periodes
                      if p["debut"] <= v.debut and (not p["fin"] or v.debut <= p["fin"])}
            for v in versions}


# ---------------------------------------------------------------------------
# Le recoupement au LEGI
# ---------------------------------------------------------------------------

def recouper_legi(colonnes: dict[str, dict[int, int]], index: Path = INDEX_LEGI) -> str:
    """Les tableaux que le LEGI reproduit depuis 2007, confrontés couple pour
    couple à la source ; un écart arrête tout. Signale un tableau du LEGI plus
    récent que la dernière version connue."""
    if not index.exists():
        return f"recoupement au LEGI omis : {index.relative_to(RACINE)} absent"
    base = sqlite3.connect(f"file:{index}?mode=ro", uri=True)
    couples, ecarts = 0, []
    bareme = par_version(colonnes)
    for version in VERSIONS:
        if version.debut < "2007-07-01":
            continue
        ligne = base.execute("SELECT texte FROM doc WHERE id = ?", (version.legi,)).fetchone()
        if ligne is None:
            raise SystemExit(f"{version.legi} absent de l'index LEGI")
        for brut, majore in lire_tableau_legi(ligne[0]).items():
            couples += 1
            if bareme[version.debut].get(brut) != majore:
                ecarts.append((version.debut, brut, majore, bareme[version.debut].get(brut)))
    if ecarts:
        raise SystemExit(f"{len(ecarts)} écart(s) entre la source et le LEGI : {ecarts[:5]}")
    connus = {v.legi for v in VERSIONS}
    nouveaux = [i for (i,) in base.execute(
        "SELECT id FROM doc WHERE titre LIKE 'Décret n° 82-1105 %' AND num LIKE 'Barème%'")
        if i not in connus]
    message = f"recoupement au LEGI : {couples} couples, aucun écart"
    if nouveaux:
        message += f" ; tableau(x) du LEGI absent(s) de VERSIONS : {', '.join(nouveaux)}"
    return message


# ---------------------------------------------------------------------------
# L'écriture et le téléchargement
# ---------------------------------------------------------------------------

ENTETE_VERSIONS = (
    "# Les versions du barème A du décret n° 82-1105, datées par le texte qui l'annexe : "
    "l'article 1er du décret au LEGI (« à compter du »), le tableau du LEGI depuis 2007, le "
    "décret au JORF. points : les points d'indice majoré uniformes que le titre du décret "
    "attribue à tous. colonne : celle de la source ; la version du 1er juillet 1999, qu'elle "
    "omet, est déduite.\n"
    "# source_id: epicycle_bareme_indices — scripts/fetch/epicycle_bareme.py\n")


def _entete_indices(millesime: str) -> str:
    return (
        "# Le barème A du décret n° 82-1105 : l'indice majoré de chaque indice brut, du "
        "1er janvier 1983 à aujourd'hui, version par version (versions.csv). Ni le minimum de "
        "traitement (article 8 du décret n° 85-1148) ni la hors-échelle.\n"
        "# source_id: epicycle_bareme_indices — Épicycle, « Correspondances entre indices bruts "
        f"et indices majorés de la fonction publique en fonction du temps », data.gouv.fr, "
        f"fichier du {millesime}, licence CC BY-SA, que ce fichier garde ; "
        "scripts/fetch/epicycle_bareme.py\n"
        "# lecture : lue (la source) ; deduite (la version du 1er juillet 1999, que la source "
        "omet : celle du 1er décembre 1999 moins son point uniforme) ; corrigee (une valeur "
        "recopiée de l'indice brut suivant, remplacée par celle que les versions voisines "
        "donnent ensemble).\n")


def ecrire_reference(periodes: list[dict], millesime: str, dossier: Path = REFERENCE) -> None:
    """Les deux fichiers. ``indices.csv`` garde sa colonne ``fiabilite`` : vide
    pour une ligne neuve ou changée, la valeur qu'elle avait sinon — seul
    ``verifier_donnees.py`` la fait ``haute`` ou ``estimee``."""
    dossier.mkdir(parents=True, exist_ok=True)
    tampon = io.StringIO()
    tampon.write(ENTETE_VERSIONS)
    redacteur = csv.writer(tampon, lineterminator="\n")
    redacteur.writerow(["debut", "texte", "signature", "jorf", "legi", "points", "colonne",
                        "lecture"])
    for v in VERSIONS:
        redacteur.writerow([v.debut, v.texte, v.signature, v.jorf, v.legi,
                            "" if v.points is None else v.points, v.colonne or "",
                            "lue" if v.colonne else "deduite"])
    (dossier / "versions.csv").write_text(tampon.getvalue(), encoding="utf-8")

    chemin = dossier / "indices.csv"
    champs = ["indice_brut", "debut", "fin", "indice_majore", "lecture"]
    anciennes: dict[tuple, dict] = {}
    if chemin.exists():
        with chemin.open(encoding="utf-8") as flux:
            for ligne in csv.DictReader(l for l in flux if not l.startswith("#")):
                anciennes[(ligne["indice_brut"], ligne["debut"])] = ligne
    tampon = io.StringIO()
    tampon.write(_entete_indices(millesime))
    redacteur = csv.DictWriter(tampon, fieldnames=[*champs, "fiabilite"], lineterminator="\n")
    redacteur.writeheader()
    for periode in periodes:
        sortie = {c: str(periode[c]) for c in champs}
        avant = anciennes.get((sortie["indice_brut"], sortie["debut"]), {})
        identique = all(avant.get(c) == sortie[c] for c in champs)
        sortie["fiabilite"] = avant.get("fiabilite", "") if identique else ""
        redacteur.writerow(sortie)
    chemin.write_text(tampon.getvalue(), encoding="utf-8")


def brut(periodes: list[dict], source: str, empreinte: str) -> dict:
    """Le fichier brut de la certification : l'indice majoré de chaque période
    sous la clé « indice brut|début », à part celles que la source ne dit pas
    telles quelles (``indice_majore_corrige``)."""
    contenu = {"source": source, "sha1": empreinte, "recupere_le": date.today().isoformat(),
               "indice_majore": {}, "indice_majore_corrige": {}}
    for p in periodes:
        serie = "indice_majore_corrige" if p["lecture"] == "corrigee" else "indice_majore"
        contenu[serie][f"{p['indice_brut']}|{p['debut']}"] = p["indice_majore"]
    return contenu


def _lire_url(url: str, essais: int) -> bytes:
    requete = urllib.request.Request(url, headers={"User-Agent": "retraitecomptenotionelle"})
    for essai in range(1, essais + 1):
        try:
            with urllib.request.urlopen(requete, timeout=120) as reponse:
                return reponse.read()
        except (urllib.error.URLError, OSError) as erreur:
            print(f"{url} : essai {essai}/{essais} : {erreur}", file=sys.stderr)
            time.sleep(5)
    raise SystemExit(f"{url} : aucun des {essais} essais n'a abouti")


def telecharger(essais: int = 30) -> tuple[str, str, str]:
    """Le fichier de la source, par la notice du jeu : rend son texte, son
    adresse et sa date. data.gouv.fr coupe souvent la connexion à travers le
    mandataire d'une session : le récupérateur retente. L'empreinte SHA-1 que
    la notice publie doit être celle du fichier reçu."""
    notice = json.loads(_lire_url(API, essais))
    ressources = [r for r in notice["resources"] if (r.get("format") or "").lower() == "csv"]
    if len(ressources) != 1:
        raise SystemExit(f"{PAGE} : {len(ressources)} fichiers CSV, un seul attendu")
    ressource = ressources[0]
    octets = _lire_url(ressource["url"], essais)
    attendue = (ressource.get("checksum") or {}).get("value")
    if attendue and hashlib.sha1(octets).hexdigest() != attendue:
        raise SystemExit(f"{ressource['url']} : empreinte {hashlib.sha1(octets).hexdigest()}, "
                         f"la notice dit {attendue}")
    LOCAL.parent.mkdir(parents=True, exist_ok=True)
    LOCAL.write_bytes(octets)
    return octets.decode("utf-8"), ressource["url"], ressource["last_modified"][:10]


def _en_lettres(jour: str) -> str:
    """« 2023-11-14 » → « 14 novembre 2023 »."""
    noms = ("janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
            "septembre", "octobre", "novembre", "décembre")
    j = date.fromisoformat(jour)
    return f"{'1er' if j.day == 1 else j.day} {noms[j.month - 1]} {j.year}"


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analyseur.add_argument("--csv", type=Path,
                           help="lire ce fichier de la source au lieu de le télécharger")
    analyseur.add_argument("--millesime", default="14 novembre 2023",
                           help="la date du fichier lu par --csv")
    options = analyseur.parse_args(arguments)
    if options.csv:
        texte, adresse = options.csv.read_text(encoding="utf-8"), str(options.csv)
        millesime = options.millesime
    else:
        texte, adresse, jour = telecharger()
        millesime = _en_lettres(jour)
    colonnes = lire_csv(texte)
    print(recouper_legi(colonnes))
    periodes = construire(colonnes)
    ecrire_reference(periodes, millesime)
    empreinte = hashlib.sha1(texte.encode("utf-8")).hexdigest()
    BRUT.parent.mkdir(parents=True, exist_ok=True)
    BRUT.write_text(json.dumps(brut(periodes, adresse, empreinte), ensure_ascii=False,
                               indent=0, sort_keys=True), encoding="utf-8")
    lectures = {}
    for p in periodes:
        lectures[p["lecture"]] = lectures.get(p["lecture"], 0) + 1
    print(f"{len(VERSIONS)} versions, {len(periodes)} périodes "
          f"({', '.join(f'{n} {l}' for l, n in sorted(lectures.items()))}) ; "
          f"brut : {BRUT.relative_to(RACINE)} ; certifier : "
          "python scripts/verifier_donnees.py --appliquer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
