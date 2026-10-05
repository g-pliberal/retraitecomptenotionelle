#!/usr/bin/env python3
"""Assiette forfaitaire de l'assurance vieillesse des parents au foyer, par la Cnav.

    python scripts/fetch/cnav_assiette_avpf.py
    python scripts/fetch/cnav_assiette_avpf.py --fichier baremes.json

À QUOI ELLE SERT. La caisse d'allocations familiales cotise au régime général
pour le parent au foyer sur une assiette FORFAITAIRE, et cette assiette est le
salaire porté à son compte : elle entre dans son salaire annuel moyen. L'article
R. 381-3 du code de la sécurité sociale la fixe, par mois, à « 169 fois le
salaire horaire minimum de croissance en vigueur au 1er juillet de l'année
civile précédente » (rédaction d'octobre 2002, LEGIARTI000006750084, reprise en
2023, LEGIARTI000047961951) ; de 1985 à 2002, au SMIC multiplié par les
cinquante-deux douzièmes de la durée hebdomadaire légale, au 1er juillet de
l'année précédente aussi (LEGIARTI000006750080 à 006750083). Le dépôt portait
1 820 heures du SMIC de JANVIER de l'année : 9 à 10 % de trop peu depuis 1982,
12,5 % avant, quand la durée légale était de quarante heures.

LA SOURCE. Le barème « Assurance vieillesse des parents au foyer (AVPF) » de
la base de législation de la Cnav (``cotisation_salaire_avpf_bar``), par la
même API publique que ``cnav_minimum_contributif.py`` : l'assiette mensuelle et
le taux de cotisation à chaque date, du 1er juillet 1972, où l'AVPF naît, au
1er janvier 2026, avec la circulaire qui fixe chacune depuis 2014. Avant 1997,
il donne aussi l'assiette des Antilles, de la Guyane et de La Réunion, plus
basse ; le dépôt n'en garde que la métropole (``docs/limites.md``).

UN ÉCART AU TEXTE, que le script dit sans le corriger. En 2026, la circulaire
2025/33 fixe 2 031,38 € par mois : 169 fois le SMIC du 1er janvier 2026
(12,02 €), et non celui du 1er juillet 2025 (11,88 €), qu'écrit R. 381-3 et qui
donnerait 2 007,72 €. Toutes les autres années tombent sur le SMIC du 1er
juillet précédent. Le modèle suit la caisse, qui porte ce montant au compte.

Le script écrit les montants en euros PAR MOIS — les francs d'avant 2002
convertis à 6,55957 — et refuse d'écrire si une date apparaît deux fois, si une
assiette baisse, ou si les repères (``REPERES``) ne se retrouvent pas au
centime. Statut ``haute`` : la caisse transcrit ce que sa circulaire fixe.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
API = ("https://legislation.lassuranceretraite.fr/api/v1/baremes/"
       "baremesByFileLeafRef/{}.aspx")
BAREME = "cotisation_salaire_avpf_bar"
BRUT = RACINE / "data" / "brut" / "cnav_assiette_avpf.json"
SORTIE = RACINE / "data" / "reference" / "legislation" / "assiette_avpf.csv"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Le taux de conversion du franc en euro, fixé le 31 décembre 1998.
FRANCS_PAR_EURO = 6.55957

#: Ce que le barème doit redonner au centime : la première assiette, celle de
#: 2021 que les barèmes de l'IPP portent aussi (169 × 10,15 €, le SMIC du
#: 1er juillet 2020), et celle de 2026, que la circulaire 2025/33 écrit en
#: toutes lettres (« 2 031,38 euros »).
REPERES = {
    "1972-07-01": 667.32 / FRANCS_PAR_EURO,
    "2021-01-01": 1_715.35,
    "2026-01-01": 2_031.38,
}

ENTETE_CSV = """\
# Assiette forfaitaire mensuelle de l'assurance vieillesse des parents au foyer
# -----------------------------------------------------------------------------
# source_id: cnav_assiette_avpf
#
# Fichier écrit par scripts/fetch/cnav_assiette_avpf.py : ne pas modifier à la
# main.
#
# La caisse d'allocations familiales cotise au régime général pour le parent au
# foyer sur cette assiette, et c'est elle que le compte de l'assuré reçoit comme
# salaire : elle entre dans son salaire annuel moyen (R. 351-29). L'article
# R. 381-3 la fixe, par mois, à 169 fois le SMIC horaire en vigueur au 1er
# juillet de l'année civile précédente — de 1985 à 2002, au SMIC multiplié par
# les cinquante-deux douzièmes de la durée hebdomadaire légale, à la même date.
# Le dépôt portait jusqu'au 5 octobre 2026 1 820 heures du SMIC de janvier de
# l'année : 9 à 10 % de trop peu, 12,5 % avant 1982.
#
# UNE LIGNE PAR DATE DU BARÈME de la Cnav (« Assurance vieillesse des parents au
# foyer (AVPF) »), y compris celles où seul le taux change : l'assiette d'une
# ligne vaut à partir de sa date, et le salaire d'une année est la somme des
# assiettes de ses mois. L'AVPF naît le 1er juillet 1972 : rien avant. Au-delà
# de la dernière ligne, le modèle applique le texte, 169 heures du SMIC du
# 1er juillet précédent.
#
# Métropole seulement : jusqu'en 1996, le barème donne aux Antilles, à la Guyane
# et à La Réunion une assiette plus basse, que le dépôt ne distingue pas.
#
# En 2026, la circulaire 2025/33 fixe 2 031,38 € : 169 fois le SMIC du
# 1er janvier 2026 (12,02 €), et non celui du 1er juillet 2025 (11,88 €) que
# R. 381-3 désigne. Le modèle suit la caisse, qui porte ce montant au compte.
#
# fiabilite : `haute`. La caisse transcrit ce que sa circulaire fixe ; le texte
# ne donne que la règle.
date_effet,assiette_mensuelle,fiabilite
"""


def _texte(fragment: str) -> str:
    """Le texte d'un morceau de HTML, sans balises ni espaces invisibles."""
    brut = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"[\s​﻿]+", " ", brut).strip()


def _lignes(contenu: str) -> list[list[str]]:
    return [
        [_texte(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", ligne, flags=re.S)]
        for ligne in re.findall(r"<tr[^>]*>(.*?)</tr>", contenu, flags=re.S)
    ]


def _montant(cellule: str) -> float | None:
    """« 6 249,62 F » → 952,74 € ; « 2 031,38 € » → 2 031,38 €."""
    trouve = re.fullmatch(r"([\d ]+(?:,\d+)?)\s*(€|F)", cellule)
    if trouve is None:
        return None
    valeur = float(trouve.group(1).replace(" ", "").replace(",", "."))
    return valeur / FRANCS_PAR_EURO if trouve.group(2) == "F" else valeur


def _date(cellule: str) -> str | None:
    trouve = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", cellule)
    if trouve is None:
        return None
    jour, mois, annee = trouve.groups()
    return f"{annee}-{mois}-{jour}"


def lire(contenu: str) -> list[tuple[str, float | None, str]]:
    """(date, assiette mensuelle en euros, référence) : l'assiette de la
    métropole est la deuxième cellule ; la référence, la dernière quand elle
    nomme une circulaire."""
    lus = []
    for cellules in _lignes(contenu):
        effet = _date(cellules[0]) if cellules else None
        if effet is None or len(cellules) < 2:
            continue
        reference = cellules[-1] if "irculaire" in cellules[-1] else ""
        lus.append((effet, _montant(cellules[1]), reference))
    return lus


def controler(lus: list[tuple[str, float | None, str]]) -> list[str]:
    """Ce qui ferait d'une lecture de travers une série fausse sans bruit."""
    erreurs = []
    vus: dict[str, float] = {}
    for effet, valeur, _ in lus:
        if valeur is None:
            erreurs.append(f"{effet} : assiette illisible")
        elif effet in vus:
            erreurs.append(f"{effet} : la date apparaît deux fois")
        else:
            vus[effet] = valeur
    serie = sorted(vus.items())
    if not serie:
        erreurs.append("aucune ligne lue")
    for (avant, a), (apres, b) in zip(serie, serie[1:]):
        if b < a - 0.005:
            erreurs.append(f"{apres} : {b:.2f} €, moins que {a:.2f} € au {avant}")
    for effet, attendu in REPERES.items():
        lu = vus.get(effet)
        if lu is None or abs(lu - attendu) > 0.005:
            erreurs.append(f"{effet} : attendu {attendu:.2f}, lu {lu}")
    return erreurs


def telecharger() -> str:
    requete = urllib.request.Request(API.format(BAREME), headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        donnees = json.loads(reponse.read().decode("utf-8-sig"))
    return (donnees[0] if isinstance(donnees, list) else donnees)["contenu"]


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument(
        "--fichier", type=Path,
        help="réponse JSON de l'API des barèmes (liste complète) déjà "
             "téléchargée, lue au lieu du réseau")
    arguments = analyseur.parse_args(argv)
    if arguments.fichier:
        tous = {b["fileLeafRef"]: b["contenu"] for b in
                json.loads(arguments.fichier.read_text(encoding="utf-8-sig"))}
        contenu = tous[f"{BAREME}.aspx"]
    else:
        contenu = telecharger()
    lus = lire(contenu)
    erreurs = controler(lus)
    if erreurs:
        print("Barème refusé :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    BRUT.parent.mkdir(parents=True, exist_ok=True)
    BRUT.write_text(json.dumps({
        "source": API.format(BAREME),
        "recupere_le": date.today().isoformat(),
        "note": "Assiette forfaitaire mensuelle de la métropole, en euros, à "
                "chaque date du barème : les francs convertis à 6,55957.",
        "serie": {effet: valeur for effet, valeur, _ in sorted(lus)},
        "references": {effet: ref for effet, _, ref in sorted(lus) if ref},
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    SORTIE.write_bytes((ENTETE_CSV + "".join(
        f"{effet},{valeur:.6f},haute\n" for effet, valeur, _ in sorted(lus)
    )).encode("utf-8"))
    print(f"{len(lus)} assiettes écrites dans {SORTIE.relative_to(RACINE)}, "
          f"du {min(lus)[0]} au {max(lus)[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
