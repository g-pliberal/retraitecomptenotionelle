#!/usr/bin/env python3
"""Témoin d'Ines (INSEE, DREES, Cnaf), exécuté à part, sur des foyers de retraités.

    python scripts/fetch/ines.py --ines ~/modeles/ines-public   # refait tests/temoins/ines.json
    python scripts/fetch/ines.py --lister                       # les cas, sans rien exécuter

À quoi il sert. Ines est le modèle de microsimulation statique de l'INSEE, de
la DREES et de la Cnaf : il applique la législation sociale et fiscale d'une
année aux ménages de l'enquête Revenus fiscaux et sociaux. Il ne calcule pas
la pension, qui est une donnée de l'enquête, mais tout ce qui l'entoure : les
prélèvements selon le revenu fiscal du foyer, et l'ASPA. C'est une seconde
implémentation de ces règles, écrite par d'autres et hors de toute famille du
registre (`data/reference/referents.yaml`, `ines`). Ce n'est PAS une source
officielle : un désaccord ne désigne pas d'office le coupable, il se tranche
par le texte, ou par le barème que la caisse applique.

Ce qu'il fait. Il décrit trois sortes de foyers, et les écrit en tables d'Ines
(CSV) que `ines.R` exécute : des retraités dont il donne la pension imposable,
la profession et le revenu fiscal de l'avant-dernière année, pour les
prélèvements de 2023 à 2025 ; des personnes seules et des couples dont il donne
les pensions brutes, pour l'ASPA de 2021 à 2025 ; deux allocataires dont l'ASPA
lit la pension brute qu'Ines reconstitue, de 2023 à 2025. Les revenus fiscaux
des foyers « au seuil » sont ceux du barème que la caisse publie pour chaque
année (son API, `prelevement_sur_retraite_seuil_revenu_assujettissement_taux_csg_<année>_bar`),
lu au moment de l'exécution et recopié dans le témoin. Il fige les sorties dans
`tests/temoins/ines.json`, avec la version, le commit, la date, les paramètres
qu'Ines a lus et les entrées ; `tests/test_ines.py` y confronte le scénario 1,
sans R.

Ce qu'il ne fait pas. Le code d'Ines n'entre jamais au dépôt : ses programmes
sont sous CeCILL 2.1, licence à réciprocité, et ses paramètres sous ODbL et
DbCL (`docs/architecture.md`, § 3.4) ; seules ses sorties entrent ici, leur
origine et leur licence dites dans le témoin. L'ERFS n'est pas lue : elle
demande une habilitation, et les foyers sont écrits à la main. Le modèle n'est
pas « installé » : `ines.R` charge ses fonctions depuis le dossier de ses
programmes et n'évalue de `calcule_cotis` que les instructions qui touchent une
pension (voir son en-tête).

Installation, une fois (le commit est dans le témoin) : télécharger l'archive
du dépôt d'Ines au commit voulu
(`https://gitlab.com/insee_drees_cnaf/ines-public/-/archive/<commit>/ines-public-<commit>.tar.gz`),
la décompresser, par exemple dans `~/modeles/ines-public` ; R 4.3 et les
paquets dplyr, tidyr, rlang, stringr, readxl et jsonlite (sous Ubuntu, les
paquets `r-cran-*` du même nom). Rien ne se compile.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "tests" / "temoins" / "ines.json"
SCRIPT_R = Path(__file__).resolve().with_suffix(".R")

#: Le modèle, tel qu'il a été téléchargé (voir l'en-tête).
DEPOT_INES = "https://gitlab.com/insee_drees_cnaf/ines-public"
COMMIT = "a55816ca5bb50aa22f2d6391d330a4ffa9aff315"
VERSION = "Ines 2024.1"
LICENCE = "CeCILL 2.1 (programmes) ; ODbL et DbCL (paramètres)"

#: Les législations. Ines 2024.1 porte les paramètres des prélèvements
#: jusqu'à 2025 (`param_prelev.xlsx`, onglet `cotis`), et le barème des minima
#: au mois de janvier 2021 à décembre 2025 (`param_presta_mensuel.xlsx`, onglet
#: `Minima`) ; avant 2021, une valeur par an, que sa fonction de l'ASPA ne lit
#: pas.
ANNEES_PRELEVEMENTS = (2023, 2024, 2025)
ANNEES_ASPA = (2021, 2022, 2023, 2024, 2025)
ANNEES_CHAINE = (2023, 2024, 2025)

#: Les professions, en nomenclature des PCS à quatre chiffres, telles que la
#: section des retraités d'Ines les range (`ancienne_prof`) : un employé du
#: privé, dont il impute la part complémentaire de la pension ; un cadre du
#: privé ; un cadre de la fonction publique, sans part complémentaire.
NON_CADRE, CADRE, FONCTIONNAIRE = "5411", "3721", "3311"

#: Le barème de la caisse : les seuils de revenu fiscal de la CSG d'une
#: pension, première part, demi-part et quart de part supplémentaires, en
#: métropole.
API_CNAV = ("https://legislation.lassuranceretraite.fr/api/v1/baremes/"
            "baremesByFileLeafRef/{}.aspx")
BAREME_CSG = "prelevement_sur_retraite_seuil_revenu_assujettissement_taux_csg_{}_bar"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
#: Les trois seuils, dans l'ordre du barème : au-delà du premier, le taux
#: réduit ; au-delà du deuxième, le taux médian ; à partir du troisième, le
#: taux plein.
SEUILS = ("exoneration", "taux_reduit", "taux_plein")


@dataclass(frozen=True)
class Prelevement:
    """Un retraité seul dans son foyer fiscal : sa pension imposable de
    l'année, sa profession, les parts et le revenu fiscal de l'avant-dernière
    année. ``seuil`` (l'un de :data:`SEUILS`) remplace le revenu par le seuil de
    la caisse à ces parts, plus ``au_dela`` euros."""

    code: str
    objet: str
    pension_imposable: float
    profession: str
    parts: float
    revenu_fiscal: float | None = None
    seuil: str | None = None
    au_dela: int = 0


@dataclass(frozen=True)
class Personne:
    age: int
    pension_brute: float
    salaire_brut: float = 0.0


@dataclass(frozen=True)
class Aspa:
    """Une personne seule, ou un couple marié : la première personne est
    l'assuré, la seconde son conjoint. Les pensions sont brutes."""

    code: str
    objet: str
    personnes: tuple[Personne, ...]


@dataclass(frozen=True)
class Chaine:
    """Une personne seule dont l'ASPA lit la pension brute qu'Ines
    reconstitue de sa pension imposable."""

    code: str
    objet: str
    age: int
    pension_imposable: float
    profession: str
    parts: float
    revenu_fiscal: float


PRELEVEMENTS: tuple[Prelevement, ...] = (
    Prelevement("une_part_exoneree", "une part, sous le seuil d'exonération",
                9000, NON_CADRE, 1, 8000),
    Prelevement("une_part_taux_reduit", "une part, au taux réduit", 15000, NON_CADRE, 1, 14000),
    Prelevement("une_part_taux_median", "une part, au taux médian", 21000, NON_CADRE, 1, 20000),
    Prelevement("une_part_taux_plein", "une part, au taux plein", 42000, NON_CADRE, 1, 40000),
    Prelevement("une_part_taux_plein_cadre", "un ancien cadre du privé, au taux plein",
                42000, CADRE, 1, 40000),
    Prelevement("deux_parts_exoneree", "deux parts, un ancien fonctionnaire, exonéré",
                16000, FONCTIONNAIRE, 2, 15000),
    Prelevement("deux_parts_taux_reduit", "deux parts, un ancien fonctionnaire, au taux réduit",
                22000, FONCTIONNAIRE, 2, 21000),
    Prelevement("deux_parts_taux_median", "deux parts, un ancien fonctionnaire, au taux médian",
                34000, FONCTIONNAIRE, 2, 33000),
    Prelevement("deux_parts_taux_plein", "deux parts, un ancien fonctionnaire, au taux plein",
                62000, FONCTIONNAIRE, 2, 60000),
    *(Prelevement(f"une_part_au_seuil_{seuil}", f"une part, au seuil « {seuil} » de la caisse",
                  20000, NON_CADRE, 1, seuil=seuil) for seuil in SEUILS),
    *(Prelevement(f"deux_parts_au_seuil_{seuil}",
                  f"deux parts, au seuil « {seuil} » de la caisse",
                  30000, NON_CADRE, 2, seuil=seuil) for seuil in SEUILS),
    *(Prelevement(f"deux_parts_un_euro_au_dela_du_seuil_{seuil}",
                  f"deux parts, un euro au-delà du seuil « {seuil} » de la caisse",
                  30000, NON_CADRE, 2, seuil=seuil, au_dela=1) for seuil in SEUILS),
)

ASPA: tuple[Aspa, ...] = (
    Aspa("seul_sans_ressources", "une personne seule, sans pension", (Personne(70, 0),)),
    Aspa("seul_petite_pension", "une personne seule, 6 000 € de pension",
         (Personne(70, 6000),)),
    Aspa("seul_au_dessus_du_plafond", "une personne seule, au-dessus du plafond",
         (Personne(70, 13000),)),
    Aspa("seul_avec_salaire", "une personne seule qui travaille encore",
         (Personne(66, 5000, 9000),)),
    Aspa("couple_un_allocataire", "un couple, le conjoint n'a pas 65 ans",
         (Personne(70, 6000), Personne(60, 4000))),
    Aspa("couple_un_allocataire_sans_ressources",
         "un couple, le conjoint n'a pas 65 ans ni de ressources",
         (Personne(70, 1000), Personne(60, 0))),
    Aspa("couple_deux_allocataires", "un couple de deux allocataires",
         (Personne(70, 6000), Personne(68, 4000))),
    Aspa("couple_deux_allocataires_au_dessus_du_plafond",
         "un couple de plus de 65 ans, au-dessus du plafond du couple",
         (Personne(70, 12000), Personne(68, 9000))),
)

CHAINES: tuple[Chaine, ...] = (
    Chaine("seul_exonere", "un allocataire exonéré de CSG par son revenu fiscal",
           70, 9000, FONCTIONNAIRE, 1, 8000),
    Chaine("seul_taux_reduit", "un allocataire au taux réduit par son revenu fiscal",
           70, 9500, FONCTIONNAIRE, 1, 13500),
)


# ---- Le barème de la caisse ----------------------------------------------------

def _cellules(contenu: str) -> list[str]:
    texte = re.sub(r"<[^>]+>", "|", contenu)
    texte = html.unescape(texte).replace("​", "").replace(" ", " ")
    return [c.strip() for c in texte.split("|") if c.strip()]


def _euros(cellule: str) -> int:
    chiffres = re.sub(r"[^\d]", "", cellule)
    if not cellule.strip().endswith("€") or not chiffres:
        raise ValueError(f"pas un montant en euros : {cellule!r}")
    return int(chiffres)


def seuils_de_la_caisse(annee: int) -> dict:
    """Les seuils de la métropole que le barème de la caisse donne pour
    ``annee`` : première part, demi-part et quart de part, et la circulaire
    qu'il cite."""
    feuille = BAREME_CSG.format(annee)
    requete = urllib.request.Request(API_CNAV.format(feuille), headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        bareme = json.load(reponse)
    cellules = _cellules(bareme["contenu"])
    debut = cellules.index("Résidence en métropole")
    fin = next(i for i, c in enumerate(cellules) if i > debut and c.startswith("Résidence en"))
    metropole = cellules[debut:fin]

    def ligne(entete: str) -> list[int]:
        i = metropole.index(entete)
        return [_euros(c) for c in metropole[i + 1:i + 4]]

    circulaire = next(c for c in metropole if c.startswith("Circulaire Cnav"))
    return {"premiere_part": ligne("1"), "demi_part": ligne("par demi-part supplémentaire"),
            "quart_de_part": ligne("par quart de part supplémentaire"),
            "circulaire": circulaire, "bareme": API_CNAV.format(feuille),
            "titre": bareme["titre"], "modifie_le": bareme["dateModification"]}


def seuil(seuils: dict, nom: str, parts: float) -> int:
    """Le seuil de la caisse à ``parts`` parts, par demi-parts entières."""
    rang = SEUILS.index(nom)
    demi_parts = round(2 * (parts - 1))
    if demi_parts != 2 * (parts - 1):
        raise ValueError(f"{parts} parts : le cas n'a que des demi-parts entières")
    return seuils["premiere_part"][rang] + demi_parts * seuils["demi_part"][rang]


# ---- Les tables d'Ines ---------------------------------------------------------

def tables(seuils: dict[int, dict]) -> dict[str, list[dict]]:
    """Les trois tables d'entrée de `ines.R`, une ligne par cas et par année."""
    prelevements = []
    for annee in ANNEES_PRELEVEMENTS:
        for rang, cas in enumerate(PRELEVEMENTS):
            revenu = (cas.revenu_fiscal if cas.seuil is None
                      else seuil(seuils[annee], cas.seuil, cas.parts) + cas.au_dela)
            prelevements.append({
                "annee": annee, "code": cas.code, "ident": f"p{rang:02d}", "noi": "01",
                "idfoyer": f"p{rang:02d}01", "coldec": "1", "quelfic": "EE&FIP", "ag": 70,
                "pcstot4_comp": cas.profession, "zrsti": cas.pension_imposable,
                "npart": cas.parts, "rfr": revenu})
    aspa = []
    for annee in ANNEES_ASPA:
        for rang, cas in enumerate(ASPA):
            couple = len(cas.personnes) == 2
            for numero, personne in enumerate(cas.personnes, start=1):
                aspa.append({
                    "annee": annee, "code": cas.code, "ident": f"a{rang:02d}",
                    "noi": f"{numero:02d}",
                    "noicon": f"{3 - numero:02d}" if couple else "",
                    "idfoyer": f"a{rang:02d}01", "coldec": str(numero),
                    "lprl": str(numero), "sif_mcdv": "M" if couple else "C",
                    "ag": personne.age, "pension_brute": personne.pension_brute,
                    "salaire_brut": personne.salaire_brut})
    chaine = []
    for annee in ANNEES_CHAINE:
        for rang, cas in enumerate(CHAINES):
            chaine.append({
                "annee": annee, "code": cas.code, "ident": f"c{rang:02d}", "noi": "01",
                "noicon": "", "idfoyer": f"c{rang:02d}01", "coldec": "1", "lprl": "1",
                "sif_mcdv": "C", "quelfic": "EE&FIP", "ag": cas.age,
                "pcstot4_comp": cas.profession, "zrsti": cas.pension_imposable,
                "npart": cas.parts, "rfr": cas.revenu_fiscal, "salaire_brut": 0})
    return {"prelevements": prelevements, "aspa": aspa, "chaine": chaine}


def _ecrire_csv(chemin: Path, lignes: list[dict]) -> None:
    with chemin.open("w", encoding="utf-8", newline="") as fichier:
        ecrivain = csv.DictWriter(fichier, fieldnames=list(lignes[0]))
        ecrivain.writeheader()
        ecrivain.writerows(lignes)


def _nombre(texte: str):
    if texte in ("", "NA"):
        return None
    if texte in ("TRUE", "FALSE"):
        return texte == "TRUE"
    try:
        valeur = float(texte)
    except ValueError:
        return texte
    return int(valeur) if valeur.is_integer() and "." not in texte and "e" not in texte else valeur


#: Les colonnes que R écrit et qui restent du texte : des identifiants, dont
#: les zéros comptent (« 01 »), et des libellés.
TEXTES = frozenset({"ident", "noi", "idfoyer", "coldec", "ancienne_prof", "nom", "source"})


def _lire_csv(chemin: Path) -> list[dict]:
    with chemin.open(encoding="utf-8") as fichier:
        return [{cle: valeur if cle in TEXTES else _nombre(valeur)
                 for cle, valeur in ligne.items()}
                for ligne in csv.DictReader(fichier)]


def commande_r(distribution: str | None) -> list[str]:
    """Rscript, directement ou par la WSL."""
    if distribution:
        return ["wsl", "-d", distribution, "--exec", "Rscript"]
    return ["Rscript"]


def chemin_r(chemin: Path, distribution: str | None) -> str:
    """Un chemin tel que R le lit : vu de la WSL (`/mnt/c/…`), ou tel quel."""
    if not distribution:
        return str(chemin)
    absolu = chemin.resolve()
    lecteur = absolu.drive.rstrip(":").lower()
    return f"/mnt/{lecteur}" + absolu.as_posix()[len(absolu.drive):]


def executer(dossier: Path, code_ines: str, distribution: str | None) -> dict[str, list]:
    sortie = dossier / "sorties"
    commande = commande_r(distribution) + [
        chemin_r(SCRIPT_R, distribution), code_ines, chemin_r(dossier, distribution),
        chemin_r(sortie, distribution)]
    print("Ines…", flush=True)
    fini = subprocess.run(commande, capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    if fini.returncode != 0:
        raise RuntimeError(f"Ines a échoué :\n{fini.stdout[-3000:]}\n{fini.stderr[-3000:]}")
    return {
        "prelevements": _lire_csv(sortie / "prelevements.csv"),
        "aspa": _lire_csv(sortie / "aspa.csv"),
        "chaine": _lire_csv(sortie / "chaine.csv"),
        "parametres": _lire_csv(sortie / "parametres.csv"),
        "versions": json.loads((sortie / "versions.json").read_text(encoding="utf-8")),
    }


# ---- Le témoin -----------------------------------------------------------------

#: Ce que la section des retraités d'Ines écrit, recopié tel quel.
SORTIES_PRELEVEMENTS = ("exo_csg", "reduc_csg", "interm_csg", "ancienne_prof",
                        "partretrcompl", "zpenu", "zpenug", "zpenuc", "coprmal", "csgprd",
                        "csgpri", "csgpr_mal", "crdspr", "casapr", "zrstbrut")
SORTIES_ASPA = ("nb_elig_aspa", "en_couple", "rev_tot_aspa_abat", "aspa_eli", "asi")


def _par_cle(lignes: list[dict], *cles: str) -> dict[tuple, dict]:
    return {tuple(str(ligne[cle]) for cle in cles): ligne for ligne in lignes}


def temoin(sorties: dict[str, list], entrees: dict[str, list[dict]],
           seuils: dict[int, dict]) -> dict:
    prelevements = _par_cle(sorties["prelevements"], "annee", "ident")
    cas_prelevements = {}
    for ligne in entrees["prelevements"]:
        cas = next(c for c in PRELEVEMENTS if c.code == ligne["code"])
        fiche = cas_prelevements.setdefault(cas.code, {
            "objet": cas.objet, "pension_imposable": cas.pension_imposable,
            "profession": cas.profession, "parts": cas.parts,
            **({"seuil": cas.seuil, "au_dela": cas.au_dela} if cas.seuil else {}),
            "par_annee": {}})
        sortie = prelevements[(str(ligne["annee"]), ligne["ident"])]
        fiche["par_annee"][str(ligne["annee"])] = {
            "revenu_fiscal": ligne["rfr"], **{c: sortie[c] for c in SORTIES_PRELEVEMENTS}}
    aspa = _par_cle(sorties["aspa"], "annee", "ident", "noi")
    cas_aspa = {}
    for ligne in entrees["aspa"]:
        cas = next(c for c in ASPA if c.code == ligne["code"])
        fiche = cas_aspa.setdefault(cas.code, {
            "objet": cas.objet,
            "personnes": [{"age": p.age, "pension_brute": p.pension_brute,
                           "salaire_brut": p.salaire_brut} for p in cas.personnes],
            "par_annee": {}})
        sortie = aspa[(str(ligne["annee"]), ligne["ident"], ligne["noi"])]
        fiche["par_annee"].setdefault(str(ligne["annee"]), []).append(
            {c: sortie[c] for c in SORTIES_ASPA})
    chaine = _par_cle(sorties["chaine"], "annee", "ident")
    cas_chaine = {}
    for ligne in entrees["chaine"]:
        cas = next(c for c in CHAINES if c.code == ligne["code"])
        fiche = cas_chaine.setdefault(cas.code, {
            "objet": cas.objet, "age": cas.age, "pension_imposable": cas.pension_imposable,
            "profession": cas.profession, "parts": cas.parts,
            "revenu_fiscal": cas.revenu_fiscal, "par_annee": {}})
        sortie = chaine[(str(ligne["annee"]), ligne["ident"])]
        fiche["par_annee"][str(ligne["annee"])] = {
            c: sortie[c] for c in SORTIES_PRELEVEMENTS + SORTIES_ASPA}
    parametres: dict[str, dict] = {}
    for ligne in sorties["parametres"]:
        parametres.setdefault(str(ligne["annee"]), {})[ligne["nom"]] = ligne["valeur"]
    return {
        "modele": VERSION.split()[0],
        "auteur": "INSEE, DREES et Cnaf",
        "code": DEPOT_INES,
        "commit": COMMIT,
        "version": VERSION,
        "licence": LICENCE,
        "origine": (
            "Sorties d'Ines, exécuté à part par scripts/fetch/ines.py et ines.R ; le code "
            "d'Ines n'entre pas au dépôt. Les chiffres ci-dessous sont ses résultats et "
            "les paramètres qu'il a lus, publiés sous sa licence, avec leur origine."),
        "execute_le": dt.date.today().isoformat(),
        "environnement": sorties["versions"],
        "legislation": {
            "prelevements": list(ANNEES_PRELEVEMENTS),
            "aspa": list(ANNEES_ASPA),
            "chaine": list(ANNEES_CHAINE),
            "dit": ("les années qu'Ines 2024.1 paramètre : les prélèvements jusqu'à 2025, "
                    "le barème mensuel des minima de janvier 2021 à décembre 2025"),
        },
        "execution": (
            "Des prélèvements, les instructions de calcule_cotis (R/12_cotisations.R) "
            "qui classent le foyer par son revenu fiscal (param_cotisations2, impot_ind) "
            "puis celles de la section des retraités (param_retraite, retraites), "
            "évaluées telles qu'Ines les écrit ; la table prof qui les relie est écrite "
            "par ines.R. De l'ASPA, modelise_aspa_asi (R/14_minima_pa.R), appelée "
            "entière, sur le barème mensuel de l'année (import_param_mensuel, profondeur "
            "nulle). La chaîne : l'ASPA sur la pension brute zrstbrut que la section des "
            "retraités reconstitue."),
        "conventions": {
            "montants": "annuels, en euros de l'année de législation",
            "pension_imposable": ("zrsti : la pension déclarée, nette de la CSG déductible "
                                  "et de la cotisation maladie ; Ines en reconstitue la "
                                  "brute, zpenu"),
            "revenu_fiscal": ("rfr : celui de l'avant-dernière année, avec ses parts, que "
                              "la table des foyers d'Ines porte à l'année N−2"),
            "classement": ("exo_csg, reduc_csg et interm_csg, les indicatrices d'Ines : "
                           "exonéré si exo_csg, taux réduit si reduc_csg, taux médian si "
                           "interm_csg, taux plein sinon"),
            "aspa": ("aspa_eli, l'allocation annuelle de chaque personne ; une personne "
                     "absente des éligibles vaut null"),
        },
        "seuils_de_la_caisse": {str(annee): seuils[annee] for annee in sorted(seuils)},
        "parametres_ines": parametres,
        "prelevements": cas_prelevements,
        "aspa": cas_aspa,
        "chaine": cas_chaine,
    }


def _ecrire(document: dict) -> None:
    texte = json.dumps(document, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_bytes(texte.encode("utf-8"))


def main(arguments: list[str] | None = None) -> int:
    lecteur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    lecteur.add_argument("--ines", default="~/modeles/ines-public", metavar="DOSSIER",
                         help="le dossier du code d'Ines, au commit du témoin, tel que R "
                              "le voit")
    lecteur.add_argument("--wsl", default="Ubuntu", metavar="DISTRIBUTION",
                         help="la distribution de la WSL où R est installé ; "
                              "« aucune » pour lancer Rscript directement")
    lecteur.add_argument("--lister", action="store_true",
                         help="imprime les cas, sans rien exécuter")
    lecteur.add_argument("--garder", action="store_true",
                         help="garde le dossier des tables et des sorties de R")
    options = lecteur.parse_args(arguments)
    if options.lister:
        for cas in (*PRELEVEMENTS, *ASPA, *CHAINES):
            print(f"{cas.code} : {cas.objet}")
        return 0
    distribution = None if options.wsl in ("", "aucune") else options.wsl
    if distribution is None and shutil.which("Rscript") is None:
        print("Rscript est introuvable : installer R et ses paquets (voir l'en-tête).",
              file=sys.stderr)
        return 1
    code_ines = options.ines if distribution else str(Path(options.ines).expanduser())
    seuils = {annee: seuils_de_la_caisse(annee) for annee in ANNEES_PRELEVEMENTS}
    entrees = tables(seuils)
    dossier = Path(tempfile.mkdtemp(prefix="ines_"))
    try:
        for nom, lignes in entrees.items():
            _ecrire_csv(dossier / f"{nom}.csv", lignes)
        (dossier / "options.json").write_bytes(json.dumps({
            "annees_prelevements": list(ANNEES_PRELEVEMENTS),
            "annees_aspa": list(ANNEES_ASPA),
            "annees_chaine": list(ANNEES_CHAINE),
        }).encode("utf-8"))
        sorties = executer(dossier, code_ines, distribution)
    finally:
        if options.garder:
            print(f"Tables et sorties gardées dans {dossier}")
        else:
            shutil.rmtree(dossier, ignore_errors=True)
    document = temoin(sorties, entrees, seuils)
    _ecrire(document)
    print(f"{SORTIE} : {len(document['prelevements'])} foyers aux prélèvements, "
          f"{len(document['aspa'])} à l'ASPA, {len(document['chaine'])} en chaîne")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
