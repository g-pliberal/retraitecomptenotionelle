#!/usr/bin/env python3
"""SMIC net agricole, que le complément différentiel de la RCO lit : refait des
taux salariaux, confronté à ce que la MSA publie.

    python scripts/fetch/msa_smic_net_agricole.py              # le calcul, confronté au fichier
    python scripts/fetch/msa_smic_net_agricole.py --verifier   # et chaque montant relu à sa source

À QUOI IL SERT. Le complément différentiel de points de RCO (L. 732-63 du code
rural) porte la pension d'un chef d'exploitation à un pourcentage de « 1 820
fois le montant du salaire minimum de croissance retenu après déduction des
contributions et cotisations obligatoires dues au titre des régimes de base et
complémentaire légalement obligatoire des salariés agricoles en vigueur le
1er janvier ». Aucun texte n'en fixe le montant : la MSA le calcule, et n'en
publie que la garantie mensuelle d'une carrière complète, certaines années.
``data/reference/legislation/complement_differentiel_rco.csv`` en tirait le
SMIC net de l'heure pour ces années-là et estimait les autres, une déduction de
0,79 point restant inexpliquée.

CE QUE LE SCRIPT ÉTABLIT. La déduction est la somme des taux SALARIAUX d'un
salarié non cadre d'une entreprise de la production agricole au SMIC, au
1er janvier, que les barèmes de la MSA donnent : vieillesse plafonnée et
déplafonnée, maladie et chômage tant qu'ils ont existé, CSG et CRDS sur
98,25 %, la retraite complémentaire d'AGRICA — 3,875 % (CAMARCA) jusqu'en
2018 et l'AGFF, 3,93 % et la CEG depuis 2019 —, et 0,01 % pour l'AFNCA, le
fonds du paritarisme agricole. Les 0,79 point : la part salariale d'AGRICA
au-delà de celle du régime général (3,93 au lieu de 3,15, 3,875 au lieu de
3,10) et l'AFNCA. Ce calcul redonne au centime chaque montant publié, sauf
celui de 2024, à trois centimes (« ECARTS_CONNUS »).

LE FICHIER garde sa convention : le SMIC net de l'heure à quatre décimales,
le plus petit qui redonne au centime inférieur le montant publié quand il y en
a un, le calcul arrondi sinon. Le test ``test_minima_agricoles.py`` vérifie
que chaque ligne s'écarte de moins de 0,0002 € du calcul, et que le niveau
de fiabilité suit la source : ``certifiee`` si la MSA, productrice de la
donnée, l'a publiée et que ``--verifier`` la relit ; ``haute`` si un tiers
(rapport parlementaire) la cite ; ``moyenne`` si seul le calcul la donne, sur
des taux lus.

``--verifier`` télécharge chaque source de ``PUBLIES`` et y cherche la phrase
citée, espaces normalisés : une page qui ne la porte plus le dit, et le niveau
de la ligne doit alors redescendre. Écrit le 14 octobre 2026 (action 138,
étape 8).
"""

from __future__ import annotations

import argparse
import csv
import html
import math
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
FICHIER = RACINE / "data" / "reference" / "legislation" / "complement_differentiel_rco.csv"
SMIC_BRUT = RACINE / "data" / "reference" / "macro" / "smic_horaire.csv"
ENTETES = {"User-Agent": "Mozilla/5.0 (retraite-notionnelle, recherche publique)"}

#: Les heures d'une année que L. 732-63 compte, et donc d'un mois.
HEURES_PAR_MOIS = 1820 / 12

#: L'assiette de la CSG et de la CRDS d'un salaire : 98,25 %.
ABATTEMENT_CSG = 0.9825

#: Les taux salariaux d'un non cadre de la production agricole au SMIC, au
#: 1er janvier, en pour cent, de la première année où chacun vaut à la
#: dernière. Sources : le barème des cotisations sur salaires au 1er janvier
#: 2016 (ministère de l'agriculture, d'après la MSA) et le barème de la MSA
#: Midi-Pyrénées Sud au 1er avril 2020, lus le 14 octobre 2026 ; pour la
#: vieillesse, le chômage, la maladie et la CSG, les taux du régime général,
#: que ces barèmes reprennent.
TAUX: dict[str, list[tuple[int, int, float]]] = {
    "vieillesse_plafonnee": [(2015, 2015, 6.85), (2016, 2026, 6.90)],
    "vieillesse_deplafonnee": [(2015, 2015, 0.30), (2016, 2016, 0.35), (2017, 2026, 0.40)],
    "maladie": [(2015, 2017, 0.75)],
    "chomage": [(2015, 2017, 2.40), (2018, 2018, 0.95)],
    "csg_crds_sur_assiette": [(2015, 2017, 8.00), (2018, 2026, 9.70)],
    "agrica_tranche_1": [(2015, 2018, 3.875), (2019, 2026, 3.93)],
    "agff": [(2015, 2018, 0.80)],
    "ceg": [(2019, 2026, 0.86)],
    "afnca": [(2015, 2026, 0.01)],
}

#: Les montants mensuels publiés : (année, part du SMIC net, montant, éditeur,
#: producteur ?, adresse, phrase citée). La part vaut 1 pour le SMIC net
#: mensuel lui-même. Un montant écrit à l'euro se compare à l'euro.
PUBLIES: list[tuple[int, float, float, str, bool, str, str]] = [
    (2018, 1.00, 1161, "Sénat, rapport n° 315 (2017-2018)", False,
     "https://www.senat.fr/rap/l17-315/l17-3151.pdf",
     "agricole (1 161 euros au 1 er janvier 2018)"),
    (2018, 0.75, 871, "Sénat, rapport n° 315 (2017-2018)", False,
     "https://www.senat.fr/rap/l17-315/l17-3151.pdf",
     "agricole, soit 871 euros"),
    (2020, 1.00, 1206.44, "Assemblée nationale, rapport n° 3071 (juin 2020)", False,
     "https://www.assemblee-nationale.fr/dyn/15/rapports/cion-soc/l15b3071_rapport-fond.pdf",
     "Avec un SMIC net agricole (1) de 1 206,44 euros en 2020"),
    (2020, 0.75, 904.83, "Assemblée nationale, rapport n° 3071 (juin 2020)", False,
     "https://www.assemblee-nationale.fr/dyn/15/rapports/cion-soc/l15b3071_rapport-fond.pdf",
     "passerait donc de 904,83 euros"),
    (2021, 0.85, 1035.57, "MSA d'Armorique", True,
     "https://armorique.msa.fr/lfp/en/revalorisation-des-petites-retraites-agricoles-des-chefs-d-exploitation",
     "portée à 1 035,57 € par mois"),
    (2022, 0.85, 1067.91, "MSA, CGSS de La Réunion", True,
     "https://reunion.msa.fr/lfp/en/revalorisation-des-retraites-agricoles",
     "puis à 1067,91 euros au 1er janvier 2022"),
    (2026, 0.85, 1214.40, "MSA", True,
     "https://www.msa.fr/lfp/en/retraite/revalorisation-retraites-agricoles-loi-3-juillet",
     "portée à 1214,40 € par mois au 1er janvier 2026"),
]

#: Les montants publiés que le calcul ne redonne pas au centime, et de combien
#: d'euros par mois. 2024 : 1 177,03 € publiés, repris par Cerfrance d'une page
#: de la MSA qui ne le porte plus, 1 177,00 € calculés.
ECARTS_CONNUS = {2024: 0.03}


def taux_deduit(annee: int) -> float:
    """La part du SMIC brut que la MSA en déduit, en pour cent."""
    total = 0.0
    for poste, periodes in TAUX.items():
        for debut, fin, taux in periodes:
            if debut <= annee <= fin:
                total += taux * ABATTEMENT_CSG if poste == "csg_crds_sur_assiette" else taux
    return total


def _lignes(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8") as flux:
        return list(csv.DictReader(l for l in flux if not l.lstrip().startswith("#")))


def smic_brut(chemin: Path = SMIC_BRUT) -> dict[int, float]:
    return {int(l["annee"]): float(l["smic_horaire"]) for l in _lignes(chemin)}


def calcule(annee: int, brut: dict[int, float] | None = None) -> float:
    """Le SMIC net agricole de l'heure au 1er janvier, sans arrondi."""
    brut = smic_brut() if brut is None else brut
    return brut[annee] * (1 - taux_deduit(annee) / 100)


def fichier(chemin: Path = FICHIER) -> dict[int, tuple[float, str]]:
    return {int(l["annee"]): (float(l["smic_net_horaire"]), l["fiabilite"])
            for l in _lignes(chemin)}


def mensuel(part: float, horaire: float, a_l_euro: bool = False) -> float:
    """Le montant mensuel d'une part du SMIC net, au centime (ou à l'euro)
    inférieur, comme la MSA les écrit."""
    valeur = part * HEURES_PAR_MOIS * horaire
    return math.floor(valeur + 1e-9) if a_l_euro else math.floor(valeur * 100 + 1e-6) / 100


def horaire_publie(part: float, montant: float) -> float:
    """Le plus petit SMIC net de l'heure, à quatre décimales, qui redonne le
    montant publié au centime inférieur."""
    horaire = math.floor(montant / (part * HEURES_PAR_MOIS) * 10_000) / 10_000
    while mensuel(part, horaire) < montant:
        horaire = round(horaire + 0.0001, 4)
    return horaire


def confronter(brut: dict[int, float] | None = None) -> list[str]:
    """Chaque montant publié, refait par le calcul : la liste des écarts de plus
    d'un centime (d'un euro pour un montant écrit à l'euro), hors ceux que
    ``ECARTS_CONNUS`` déclare."""
    brut = smic_brut() if brut is None else brut
    ecarts = []
    for annee, part, montant, editeur, *_ in PUBLIES:
        a_l_euro = montant == int(montant)
        valeur = part * HEURES_PAR_MOIS * calcule(annee, brut)
        tolerance = 1.0 if a_l_euro else 0.01 + ECARTS_CONNUS.get(annee, 0.0)
        if abs(valeur - montant) > tolerance + 1e-9:
            ecarts.append(f"{annee} ({editeur}) : publié {montant}, calculé {valeur:.4f}")
    return ecarts


def _texte(contenu: bytes) -> str:
    if contenu[:4] == b"%PDF":
        with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf:
            pdf.write(contenu)
            pdf.flush()
            texte = subprocess.run(["pdftotext", "-layout", pdf.name, "-"], check=True,
                                   capture_output=True, text=True).stdout
    else:
        texte = contenu.decode("utf-8", errors="replace")
        texte = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", texte)
        texte = html.unescape(re.sub(r"<[^>]+>", " ", texte))
    return re.sub(r"\s+", " ", texte.replace(" ", " ").replace(" ", " "))


def relire() -> list[str]:
    """Chaque phrase citée, cherchée dans sa source téléchargée."""
    absentes, pages = [], {}
    for annee, _, _, editeur, _, adresse, phrase in PUBLIES:
        if adresse not in pages:
            requete = urllib.request.Request(adresse, headers=ENTETES)
            with urllib.request.urlopen(requete, timeout=60) as reponse:
                pages[adresse] = _texte(reponse.read())
        if re.sub(r"\s+", " ", phrase) not in pages[adresse]:
            absentes.append(f"{annee} ({editeur}) : « {phrase} » absent de {adresse}")
    return absentes


def main(arguments: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="relit chaque montant publié à sa source")
    options = analyseur.parse_args(arguments)
    brut, lues = smic_brut(), fichier()
    print("année  déduit %   calculé    fichier   niveau")
    for annee, (valeur, niveau) in sorted(lues.items()):
        print(f"{annee}  {taux_deduit(annee):8.5f}  {calcule(annee, brut):8.5f}  "
              f"{valeur:8.4f}  {niveau}")
    problemes = confronter(brut)
    if options.verifier:
        problemes += relire()
    for probleme in problemes:
        print("ÉCART :", probleme, file=sys.stderr)
    if not problemes:
        print(f"{len(PUBLIES)} montants publiés redits par le calcul"
              + (", chacun relu à sa source" if options.verifier else ""))
    return 1 if problemes else 0


if __name__ == "__main__":
    sys.exit(main())
