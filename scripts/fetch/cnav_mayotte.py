#!/usr/bin/env python3
"""Le Smig horaire et le plafond de la sécurité sociale de Mayotte.

    python scripts/fetch/cnav_mayotte.py
    python scripts/fetch/cnav_mayotte.py --fichier baremes.json

POURQUOI IL EXISTE (action 175, étape 2). La fiche de Mayotte (`cssm_mayotte`)
dit ce qui lui manque : « Le SMIG mahorais, qui valide les trimestres (200 puis
150 heures par trimestre), n'est pas une série du dépôt : la validation se fait
au SMIC national. Taux et plafond de la caisse de sécurité sociale de Mayotte,
en convergence jusqu'en 2036, remplacés par ceux du régime général. » La base
de législation de la Cnav publie l'un et l'autre ; ce récupérateur en fait une
série, que la fiche lit depuis l'action 177, étape 3, les deux moteurs ensemble.

CE QU'IL LIT. Trois barèmes de la base : « Smic horaire - Mayotte », chaque
relèvement du Smig mahorais depuis le 1er janvier 2002 ; « Salaire plafond -
Mayotte », le plafond annuel depuis le 1er juillet 2004 ; « Salaire validant
un trimestre - Mayotte », depuis 2011.

LE CONTRÔLE. Un trimestre se valide à Mayotte par 200 heures du Smig mahorais
du 1er janvier, puis 150 depuis 2017 (décret n° 87-175, art. 3 ; décret
n° 2003-589, art. 8, dans la fiche) : le salaire validant que la caisse publie
chaque année est ce produit, et le récupérateur n'écrit rien s'il ne le
retrouve pas — la lecture du Smig, de ses dates comme de ses montants, s'en
trouve recoupée.

CE QU'IL ÉCRIT. `data/reference/legislation/mayotte_smig_et_plafond.csv`, une
ligne par année : le Smig horaire du 1er janvier, depuis 2002, et le plafond
annuel en vigueur au 1er janvier, depuis 2005, la première année entière qu'il
couvre. Fiabilité `haute` : la caisse transcrit les décrets et les arrêtés.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cnav_api  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "reference" / "legislation" / "mayotte_smig_et_plafond.csv"

SMIG = "mayotte_smic_smig_smic_bar"
PLAFOND = "salaire_plafond_mayotte_bar"
SALAIRE_VALIDANT = "mayotte_salaire_validant_un_trimestre_montant_bar"

#: Les heures du Smig qui valident un trimestre, depuis l'année dite.
HEURES = ((1987, 200), (2017, 150))
#: La première année de chaque colonne : le Smig du 1er janvier 2002, le
#: plafond du 1er juillet 2004, entier à partir de 2005.
PREMIERE_ANNEE_DU_SMIG = 2002
PREMIERE_ANNEE_DU_PLAFOND = 2005

_LIGNE = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S | re.I)
_CELLULE = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S | re.I)
_JOUR = re.compile(r"^(\d\d)/(\d\d)/(\d{4})")
_ANNEE = re.compile(r"^(\d{4})$")

ENTETE_CSV = """\
# Smig horaire et plafond de la sécurité sociale de Mayotte, en euros
# -------------------------------------------------------------------
# source_id: cnav_mayotte
#
# Fichier écrit par scripts/fetch/cnav_mayotte.py : ne pas modifier à la main.
#
# LE SMIG MAHORAIS valide les trimestres de Mayotte : 200 heures du Smig du
# 1er janvier jusqu'en 2016, 150 depuis 2017 (décret n° 87-175, art. 3 ; décret
# n° 2003-589, art. 8). LE PLAFOND est celui de la caisse de sécurité sociale
# de Mayotte, en convergence vers le plafond national jusqu'en 2036, qui borne
# le salaire annuel moyen de son régime (décret n° 2003-589, art. 7). La fiche
# cssm_mayotte les lit depuis l'action 177, étape 3, dans les deux moteurs
# (DonneesMacro.smig_mayotte, DonneesMacro.plafond_mayotte).
#
# D'OÙ VIENNENT CES MONTANTS. Des barèmes de la base de législation de la Cnav
# « Smic horaire - Mayotte » (le Smig du 1er janvier de chaque année, depuis
# 2002) et « Salaire plafond - Mayotte » (le plafond annuel en vigueur au
# 1er janvier, depuis 2005, le plafond du 1er juillet 2004 n'en couvrant que la
# moitié) ; le salaire validant qu'elle publie depuis 2011, le Smig fois les
# heures, les recoupe. Fiabilité `haute` : la caisse transcrit les textes.
annee,smig_horaire,plafond_annuel,fiabilite
"""


def _texte(cellule: str) -> str:
    texte = html.unescape(re.sub(r"<[^>]+>", "", cellule))
    return " ".join(texte.replace("​", "").replace("\xa0", " ").split())


def _montant(texte: str) -> float | None:
    trouve = re.match(r"^([\d ]+(?:,\d+)?)\s*€", texte)
    return float(trouve.group(1).replace(" ", "").replace(",", ".")) if trouve else None


def lignes(contenu: str, colonne: int = 1) -> list[tuple[str, float]]:
    """Chaque ligne d'un barème, par sa date — le jour qu'elle porte, le début
    de sa période, ou le 1er janvier de son année — et le montant de la
    colonne dite, dans l'ordre du barème."""
    lues = []
    for ligne in _LIGNE.findall(contenu):
        cellules = [_texte(cellule) for cellule in _CELLULE.findall(ligne)]
        if len(cellules) <= colonne:
            continue
        if jour := _JOUR.match(cellules[0]):
            date = f"{jour.group(3)}-{jour.group(2)}-{jour.group(1)}"
        elif annee := _ANNEE.match(cellules[0]):
            date = f"{annee.group(1)}-01-01"
        else:
            continue
        if (montant := _montant(cellules[colonne])) is not None:
            lues.append((date, montant))
    return lues


def au_1er_janvier(lues: list[tuple[str, float]], premiere: int, derniere: int) -> dict[int, float]:
    """Le montant en vigueur au 1er janvier de chaque année : celui de la
    dernière date qui le précède ou le porte."""
    ordonnees = sorted(lues)
    valeurs = {}
    for annee in range(premiere, derniere + 1):
        en_vigueur = [montant for date, montant in ordonnees if date <= f"{annee}-01-01"]
        if en_vigueur:
            valeurs[annee] = en_vigueur[-1]
    return valeurs


def heures(annee: int) -> int:
    return [nombre for debut, nombre in HEURES if debut <= annee][-1]


def controler(smig: dict[int, float], validants: dict[int, float]) -> list[str]:
    """Ce que le salaire validant publié contredit : le Smig du 1er janvier
    fois les heures de l'année."""
    griefs = []
    for annee, publie in sorted(validants.items()):
        attendu = round(heures(annee) * smig[annee], 2) if annee in smig else None
        if attendu is None or abs(attendu - publie) > 0.005:
            griefs.append(f"{annee} : la caisse publie {publie} €, le Smig du 1er janvier "
                          f"fois {heures(annee)} heures fait {attendu}")
    return griefs


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--fichier", type=Path, help=cnav_api.AIDE_FICHIER)
    arguments = analyseur.parse_args(argv)
    contenus = cnav_api.contenus([SMIG, PLAFOND, SALAIRE_VALIDANT], arguments.fichier)

    smig_lus = lignes(contenus[SMIG])
    validants = dict((int(date[:4]), montant)
                     for date, montant in lignes(contenus[SALAIRE_VALIDANT]))
    derniere = max(int(date[:4]) for date, _ in smig_lus)
    smig = au_1er_janvier(smig_lus, PREMIERE_ANNEE_DU_SMIG, derniere)
    plafond = au_1er_janvier(lignes(contenus[PLAFOND], colonne=2),
                             PREMIERE_ANNEE_DU_PLAFOND, derniere)
    griefs = controler(smig, validants)
    if griefs:
        for grief in griefs:
            print(grief, file=sys.stderr)
        print("le Smig lu ne redonne pas le salaire validant — rien n'est écrit.",
              file=sys.stderr)
        return 1
    def ligne(annee: int) -> str:
        borne = f"{plafond[annee]:.0f}" if annee in plafond else ""
        return f"{annee},{smig[annee]:.2f},{borne},haute\n"

    SORTIE.write_text(ENTETE_CSV + "".join(map(ligne, sorted(smig))), encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} : le Smig de {min(smig)} à {max(smig)}, le plafond "
          f"de {min(plafond)} à {max(plafond)} ; {len(validants)} salaires validants recoupés")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
