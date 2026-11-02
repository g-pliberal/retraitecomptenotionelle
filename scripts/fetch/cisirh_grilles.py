#!/usr/bin/env python3
"""Les grilles indiciaires de la fonction publique de l'État, au Noyau RH du CISIRH.

    python scripts/fetch/cisirh_grilles.py                   # télécharge, lit, écrit
    python scripts/fetch/cisirh_grilles.py --archive N.zip   # depuis une archive déjà là
    python scripts/verifier_donnees.py --appliquer           # puis certifie

LA SOURCE. Le centre interministériel de services informatiques relatifs aux
ressources humaines (CISIRH) publie les nomenclatures du « Noyau RH » de
l'État, celles que ses logiciels de paye appliquent : jeu « Offre de
référentiels pour la gestion de la chaîne ressources humaines (RH) de l'État
(Gestion administrative, Paye et Post-paye) – Juillet 2026 » de
data.economie.gouv.fr, licence ouverte 2.0, version 26.00.00 du noyau, mise
en ligne le 7 juillet 2026. Sa pièce ``6_nomenclatures_noyau_xmlzip`` (12 Mo)
porte 364 tableaux XML, en ISO-8859-15 ; sept servent ici : CORPS, GRADE,
GRILLE_IND, ECHELON, INDICE et TEXTE, et CATG_STATUTAIRE, qui nomme les
catégories. Le serveur coupe souvent la connexion à travers le mandataire
d'une session (2 novembre 2026) : le téléchargement retente.

CE QU'IL ÉCRIT. Sous ``data/reference/grilles/etat/`` : ``corps.csv``,
``grades.csv``, ``grilles.csv``, ``echelons.csv``, ``indices.csv`` (le barème
de l'indice brut à l'indice majoré) et ``textes.csv`` (ceux que les trois
premiers citent). Chaque ligne y porte ses dates de début et de fin, comme au
noyau : une grille, un échelon, un grade a autant de lignes que de versions.
Et ``data/brut/cisirh_grilles.json`` : les valeurs que
``scripts/verifier_donnees.py`` confronte aux fichiers de référence pour les
certifier — l'indice, les durées et le rang de chaque échelon, l'indice majoré
de chaque indice brut.

CE QUE LA DONNÉE DIT, ET NE DIT PAS. Les grilles commencent avec leur corps :
1989-1990 pour les enseignants, 2005-2011 pour les autres grands corps ; avant,
le LEGI (action 158). Les durées d'échelon sont en mois — minimale, moyenne,
maximale : les trois rythmes d'avant le protocole PPCR, un seul depuis. Le
barème du noyau est l'indice majoré PAYÉ : il mêle au barème du décret
n° 82-1105 le minimum de traitement (l'indice majoré 366 à tout indice brut
jusqu'à 367 depuis le 1er janvier 2024), et n'a pas d'histoire avant novembre
2006. La territoriale et l'hospitalière n'y sont pas.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SOURCE = ("https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/"
          "offre-de-referentiels-pour-la-gestion-de-la-chaine-ressources-humaines-rh-"
          "de-letat-gestion-administrative-paye-et-post-paye-juillet-2026/attachments/"
          "6_nomenclatures_noyau_xmlzip")
ARCHIVE = RACINE / "data" / "brut" / "cisirh_nomenclatures_xml.zip"
BRUT = RACINE / "data" / "brut" / "cisirh_grilles.json"
REFERENCE = RACINE / "data" / "reference" / "grilles" / "etat"

TABLES = ("CORPS", "GRADE", "GRILLE_IND", "ECHELON", "INDICE", "TEXTE", "CATG_STATUTAIRE")
NOM_DE_TABLE = re.compile(r"_P00_([A-Z_]+?)_\d+\.xml$")

NATURES_TEXTE = {"1": "origine", "2": "rectificatif", "3": "modificatif", "4": "abrogateur"}
TYPES_INDICE = {"INBRU": "brut", "INMAJ": "majore", "INAUT": "autre", "SAOBJ": "sans_objet"}
#: Les échelons particuliers, que le noyau marque d'un drapeau chacun.
NATURES_ECHELON = (("R_ADM_ECHSTG", "stagiaire"), ("R_ADM_ECHELV", "eleve"),
                   ("R_ADM_ECHEXC", "exceptionnel"), ("R_ADM_ECHFON", "fonctionnel"),
                   ("R_ADM_ECHPRO", "provisoire"))

COLONNES = {
    "corps": ("corps", "debut", "fin", "libelle", "categorie", "filiere", "nature",
              "ministere", "anterieurs", "suivants", "textes"),
    "grades": ("grade", "debut", "fin", "libelle", "corps", "grille", "pcs", "nne",
               "anterieurs", "suivants", "textes"),
    "grilles": ("grille", "debut", "fin", "libelle", "type_indice", "anterieure",
                "suivante", "textes"),
    "echelons": ("echelon", "debut", "fin", "grille", "rang", "indice", "hors_echelle",
                 "chevron", "nature", "duree_min", "duree_moy", "duree_max", "suivant"),
    "indices": ("indice_brut", "debut", "fin", "indice_majore"),
    "textes": ("texte", "numero", "date", "effet", "publication", "fin", "nor", "jorf",
               "titre"),
}

#: Ce que ``scripts/verifier_donnees.py`` certifie : un fichier, une colonne.
CERTIFIEES = {"echelons": ("rang", "indice", "duree_min", "duree_moy", "duree_max"),
              "indices": ("indice_majore",)}

ENTETES = {
    "corps": "Les corps de la fonction publique de l'État et leurs versions datées. "
             "categorie : A, B, C, D ou le libellé du noyau (officier, hors catégorie…) ; "
             "anterieurs, suivants : les corps d'avant et d'après une fusion (chaînage).",
    "grades": "Les grades : leur corps, leur grille, leurs codes PCS et NNE, leurs "
              "grades d'avant et d'après.",
    "grilles": "Les grilles indiciaires. type_indice : ce que la colonne indice de leurs "
               "échelons porte (brut, majore, autre, sans_objet) ; textes : identifiant "
               "du noyau et nature de chaque texte (origine, modificatif…), à lire dans "
               "textes.csv.",
    "echelons": "Les échelons de chaque grille, version par version : indice, lettre de "
                "hors-échelle, chevron, nature (stagiaire, élève…), durées minimale, "
                "moyenne et maximale en mois, échelon suivant.",
    "indices": "Le barème payé : l'indice majoré de chaque indice brut, minimum de "
               "traitement compris ; une seule ligne avant novembre 2006.",
    "textes": "Les textes que corps, grades et grilles citent : numéro, dates du "
              "texte, d'effet, de publication et de fin, NOR, identifiant JORF, titre.",
}


# ---------------------------------------------------------------------------
# La lecture
# ---------------------------------------------------------------------------

def _enregistrements(octets: bytes, table: str) -> list[dict[str, list]]:
    """Les ``R_<TABLE>`` d'un tableau, chacun en dictionnaire : à chaque
    balise, la liste de ses valeurs — un texte pour une feuille, un
    dictionnaire pour un groupe (les textes d'une grille), les groupes vides
    omis. Une balise peut se répéter : les grades d'avant un grade."""
    lignes = []
    for _, element in ET.iterparse(io.BytesIO(octets)):
        if element.tag != f"R_{table}":
            continue
        ligne: dict[str, list] = {}
        for enfant in element:
            if len(enfant):
                ligne.setdefault(enfant.tag, []).append(
                    {c.tag: (c.text or "").strip() for c in enfant})
            elif enfant.tag.startswith(("R_FOR_", "R_ADM_", "R_REL_")):
                ligne.setdefault(enfant.tag, []).append((enfant.text or "").strip())
        lignes.append(ligne)
        element.clear()
    return lignes


def lire_archive(chemin: Path) -> dict[str, list[dict[str, list]]]:
    """Les tableaux utiles de l'archive des nomenclatures, par nom."""
    tables: dict[str, list[dict[str, list]]] = {}
    with zipfile.ZipFile(chemin) as archive:
        for nom in archive.namelist():
            trouve = NOM_DE_TABLE.search(nom)
            if trouve and trouve.group(1) in TABLES:
                tables[trouve.group(1)] = _enregistrements(archive.read(nom), trouve.group(1))
    return tables


def _un(ligne: dict[str, list], balise: str) -> str:
    valeurs = [v for v in ligne.get(balise, []) if isinstance(v, str) and v]
    return valeurs[0] if valeurs else ""


def _tous(ligne: dict[str, list], balise: str) -> str:
    return " ".join(v for v in ligne.get(balise, []) if isinstance(v, str) and v)


def _nombre(code: str) -> str:
    return str(int(code)) if code else ""


def _mois(duree: str) -> str:
    """Une durée du noyau, en années et mois (« 0206 »), en mois (« 30 »)."""
    return str(12 * int(duree[:2]) + int(duree[2:])) if duree else ""


def _textes(ligne: dict[str, list], groupe: str) -> str:
    return " ".join(f"{int(t['R_REL_IDTEXT'])}:{NATURES_TEXTE.get(t.get('R_REL_NATTEX', ''), '')}"
                    for t in ligne.get(groupe, []) if t.get("R_REL_IDTEXT"))


def _dates(ligne: dict[str, list]) -> dict[str, str]:
    return {"debut": _un(ligne, "R_FOR_DATDEB"), "fin": _un(ligne, "R_FOR_DATFIN")}


def _categories(lignes: list[dict[str, list]]) -> dict[str, str]:
    categories = {}
    for ligne in lignes:
        libelle = _un(ligne, "R_FOR_LIBCOU")
        categories[_un(ligne, "R_FOR_IDEN02")] = (
            libelle.removeprefix("catégorie ") if libelle.startswith("catégorie ")
            else libelle)
    return categories


def extraire(tables: dict[str, list[dict[str, list]]]) -> dict[str, list[dict[str, str]]]:
    """Les six fichiers de référence, ligne par ligne, dans l'ordre de leurs clés."""
    categories = _categories(tables.get("CATG_STATUTAIRE", []))
    corps = [{
        "corps": _un(l, "R_FOR_IDEN05"), **_dates(l), "libelle": _un(l, "R_FOR_LIBLON"),
        "categorie": categories.get(_un(l, "R_REL_CATEGO"), _un(l, "R_REL_CATEGO")),
        "filiere": _un(l, "R_REL_FILIER"), "nature": _un(l, "R_REL_NACORP"),
        "ministere": _un(l, "R_REL_MINIST"), "anterieurs": _tous(l, "R_REL_COANTE"),
        "suivants": _tous(l, "R_REL_COSUCS"), "textes": _textes(l, "R_CORPS_TEXTE"),
    } for l in tables["CORPS"]]
    grades = [{
        "grade": _un(l, "R_FOR_IDEN05"), **_dates(l), "libelle": _un(l, "R_FOR_LIBLOM"),
        "corps": _un(l, "R_REL_CORPS"), "grille": _un(l, "R_REL_GRIIND"),
        "pcs": _un(l, "R_REL_CODPCS"), "nne": _un(l, "R_REL_CODNNE"),
        "anterieurs": _tous(l, "R_REL_GRANTE"), "suivants": _tous(l, "R_REL_GRSUCS"),
        "textes": _textes(l, "R_GRADE_TEXTE"),
    } for l in tables["GRADE"]]
    grilles = [{
        "grille": _un(l, "R_FOR_IDEN05"), **_dates(l), "libelle": _un(l, "R_FOR_LIBLON"),
        "type_indice": TYPES_INDICE.get(_un(l, "R_REL_TYPIND"), _un(l, "R_REL_TYPIND")),
        "anterieure": _tous(l, "R_REL_GIANTE"), "suivante": _tous(l, "R_REL_GISUCS"),
        "textes": _textes(l, "R_GRILLE_TEXTE"),
    } for l in tables["GRILLE_IND"]]
    echelons = [{
        "echelon": _un(l, "R_FOR_IDEN05"), **_dates(l), "grille": _un(l, "R_REL_GRIIND"),
        "rang": _nombre(_un(l, "R_REL_RANECH")), "indice": _nombre(_un(l, "R_ADM_ECHIND")),
        "hors_echelle": _un(l, "R_REL_HOECHL"), "chevron": _un(l, "R_REL_CHEVRO"),
        "nature": next((nom for balise, nom in NATURES_ECHELON if _un(l, balise) == "1"), ""),
        "duree_min": _mois(_un(l, "R_FOR_DURMIN")), "duree_moy": _mois(_un(l, "R_FOR_DURMOY")),
        "duree_max": _mois(_un(l, "R_FOR_DURMAX")), "suivant": _un(l, "R_REL_ECSUIV"),
    } for l in tables["ECHELON"]]
    indices = [{
        "indice_brut": _nombre(_un(l, "R_FOR_IDEN04")), **_dates(l),
        "indice_majore": _nombre(_un(l, "R_ADM_INDMAJ")),
    } for l in tables["INDICE"]]

    cites = {int(t.split(":")[0]) for ligne in (*corps, *grades, *grilles)
             for t in ligne["textes"].split()}
    textes = [{
        "texte": str(int(_un(l, "R_ADM_TEXIDE"))), "numero": _un(l, "R_ADM_TEXNUM"),
        "date": _un(l, "R_ADM_TEXDTE"), "effet": _un(l, "R_ADM_TEXDEF"),
        "publication": _un(l, "R_ADM_TEXDPU"), "fin": _un(l, "R_ADM_TEXFVA"),
        "nor": _un(l, "R_ADM_TEXNOR"), "jorf": _un(l, "R_ADM_TEXBIF"),
        "titre": _un(l, "R_ADM_TEXLIB"),
    } for l in tables["TEXTE"] if _un(l, "R_ADM_TEXIDE") and int(_un(l, "R_ADM_TEXIDE")) in cites]

    return {
        "corps": sorted(corps, key=lambda l: (l["corps"], l["debut"])),
        "grades": sorted(grades, key=lambda l: (l["grade"], l["debut"])),
        "grilles": sorted(grilles, key=lambda l: (l["grille"], l["debut"])),
        "echelons": sorted(echelons, key=lambda l: (l["echelon"], l["debut"])),
        "indices": sorted(indices, key=lambda l: (int(l["indice_brut"]), l["debut"])),
        "textes": sorted(textes, key=lambda l: int(l["texte"])),
    }


def _cle(fichier: str, ligne: dict[str, str]) -> str:
    return f"{ligne[COLONNES[fichier][0]]}|{ligne['debut']}"


def brut(extrait: dict[str, list[dict[str, str]]], source: str) -> dict:
    """Le fichier brut de la certification : par colonne certifiée, chaque
    valeur sous la clé ``identifiant|début``, les cases vides omises."""
    contenu: dict = {"source": source, "recupere_le": date.today().isoformat()}
    for fichier, colonnes in CERTIFIEES.items():
        for colonne in colonnes:
            contenu[colonne] = {_cle(fichier, l): int(l[colonne])
                                for l in extrait[fichier] if l[colonne]}
    return contenu


# ---------------------------------------------------------------------------
# L'écriture et le téléchargement
# ---------------------------------------------------------------------------

def ecrire_reference(extrait: dict[str, list[dict[str, str]]], dossier: Path = REFERENCE) -> None:
    """Les six fichiers. Ceux que la certification touche gardent leur colonne
    ``fiabilite`` : vide pour une ligne neuve ou changée, la valeur qu'elle
    avait sinon — seul ``verifier_donnees.py`` la fait ``certifiee``."""
    dossier.mkdir(parents=True, exist_ok=True)
    for fichier, colonnes in COLONNES.items():
        chemin = dossier / f"{fichier}.csv"
        champs = [*colonnes, "fiabilite"] if fichier in CERTIFIEES else list(colonnes)
        anciennes = {}
        if fichier in CERTIFIEES and chemin.exists():
            with chemin.open(encoding="utf-8") as flux:
                for ligne in csv.DictReader(l for l in flux if not l.startswith("#")):
                    anciennes[_cle(fichier, ligne)] = ligne
        tampon = io.StringIO()
        tampon.write(f"# {ENTETES[fichier]}\n# source_id: cisirh_noyau_rh — "
                     "Noyau RH de l'État, juillet 2026 (version 26.00.00), licence "
                     "ouverte 2.0 ; scripts/fetch/cisirh_grilles.py\n")
        redacteur = csv.DictWriter(tampon, fieldnames=champs, lineterminator="\n")
        redacteur.writeheader()
        for ligne in extrait[fichier]:
            sortie = dict(ligne)
            if fichier in CERTIFIEES:
                avant = anciennes.get(_cle(fichier, ligne), {})
                identique = all(avant.get(c) == ligne[c] for c in colonnes)
                sortie["fiabilite"] = avant.get("fiabilite", "") if identique else ""
            redacteur.writerow(sortie)
        chemin.write_text(tampon.getvalue(), encoding="utf-8")


def telecharger(url: str = SOURCE, cible: Path = ARCHIVE, essais: int = 30) -> Path:
    """L'archive, retentée tant que le serveur coupe la connexion."""
    cible.parent.mkdir(parents=True, exist_ok=True)
    partiel = cible.with_suffix(".part")
    for essai in range(1, essais + 1):
        try:
            with urllib.request.urlopen(url, timeout=900) as reponse, partiel.open("wb") as sortie:
                while bloc := reponse.read(1 << 20):
                    sortie.write(bloc)
            zipfile.ZipFile(partiel).testzip()
            partiel.replace(cible)
            return cible
        except (urllib.error.URLError, OSError, zipfile.BadZipFile) as erreur:
            print(f"essai {essai}/{essais} : {erreur}", file=sys.stderr)
            time.sleep(10)
    raise SystemExit(f"{url} : aucun des {essais} essais n'a abouti")


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    analyseur.add_argument("--archive", type=Path,
                           help="lire cette archive des nomenclatures XML au lieu de la télécharger")
    options = analyseur.parse_args(arguments)
    archive = options.archive or telecharger()
    extrait = extraire(lire_archive(archive))
    ecrire_reference(extrait)
    BRUT.parent.mkdir(parents=True, exist_ok=True)
    BRUT.write_text(json.dumps(brut(extrait, source=SOURCE), ensure_ascii=False, indent=0,
                               sort_keys=True), encoding="utf-8")
    for fichier, lignes in extrait.items():
        print(f"{fichier:9} {len(lignes):6} lignes")
    print(f"brut : {BRUT.relative_to(RACINE)} ; certifier : python scripts/verifier_donnees.py --appliquer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
