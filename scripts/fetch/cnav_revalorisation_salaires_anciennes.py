#!/usr/bin/env python3
"""Coefficients de revalorisation des salaires portés au compte, de 1946 à 2017.

    python scripts/fetch/cnav_revalorisation_salaires_anciennes.py

À QUOI ILS SERVENT. ``cnav_revalorisation_salaires.py`` lit les circulaires de
la Cnav depuis octobre 2017 : avant, le modèle reconstruisait chaque colonne
depuis la plus proche, et ``docs/limites.md`` disait la dérive « invérifiable »,
faute de circulaire en ligne. La caisse publie pourtant toutes les autres, et
ce récupérateur les lit :

* les colonnes d'avant le 1er avril 2013, quatre-vingt-six dates d'effet de
  l'arrêté du 14 mai 1946 à la circulaire 2012/35, chacune avec l'arrêté, la loi
  ou la circulaire qui la fixe : la page « Coefficients de revalorisation des
  salaires et cotisations » d'avant 2013, dont le barème actuel garde le lien
  (« Accès aux coefficients de revalorisation applicables avant le
  01/04/2013 ») et dont le script de déclaration porte les valeurs ;
* les deux colonnes suivantes, celles des retraites attribuées du 1er avril
  2013 au 30 septembre 2015 (circulaire 2013/29) et du 1er octobre 2015 au
  30 septembre 2017, par l'API publique des barèmes.

CE QUI EN EST GARDÉ. La caisse publie, pour les années 1930 à 1946, des
coefficients de COTISATIONS — le compte portait alors des cotisations — et, à
partir de 1947, des coefficients de SALAIRES. Le modèle porte des salaires : il
ne garde que les seconds. Les colonnes d'avant 1952 ne sont pas multiplicatives
— l'arrêté fixait alors un coefficient par année de perception, « d'après le
rapport du salaire moyen des assurés » (ordonnance du 19 octobre 1945, art. 71) —
et aucune colonne ancienne ne sert à en reconstruire une autre : le modèle les
lit seulement à la date où elles sont en vigueur. Elles vont donc dans un
fichier à part, que le rapport entre deux valeurs d'une même colonne ne lit
pas.

TROIS CORRECTIONS, dites ici parce qu'aucune ne se voit dans la page :

1. La colonne que la page étiquette « 01/04/1958 au 31/03/1959 » porte l'arrêté
   du 18 avril 1957 et s'arrête aux salaires de 1956, comme celle d'avril 1956 ;
   aucune colonne ne couvre d'avril 1957 à mars 1958 ; et la suivante, d'avril
   1959, ajoute 1957 et 1958. C'est celle d'avril 1957, en vigueur deux ans,
   comme celle d'avril 1953 l'était : le script la date du 1er avril 1957
   (``DATES_CORRIGEES``).
2. Deux valeurs sont écrites avec un point décimal, « 40.085 » (1953, septembre
   2008) et « 40.849 » (1953, avril 2010), là où la page sépare les milliers
   d'un point et les décimales d'une virgule. Aucun coefficient de salaire n'y
   atteint mille : une valeur sans virgule porte une décimale.
3. La colonne « Avant le 01/01/1949 », de l'arrêté du 14 mai 1946, n'a pas de
   date d'effet : le script lui donne celle de l'arrêté. Elle ne porte que deux
   salaires, ceux de 1947 et de 1948, au coefficient 1.

Deux cellules de la colonne de juillet 1990 s'écartent de la chaîne des autres
de 0,4 % (1954 : 27,442 au lieu de 27,556 ; 1962 : 11,658 au lieu de 11,618) :
elles sont gardées telles que la caisse les publie.

Le script refuse d'écrire si une colonne a des trous, si un coefficient remonte
d'une année à la suivante ou passe sous 1, si deux colonnes consécutives
d'après 1952 s'écartent de plus de 1 % de la multiplicativité, ou si les
repères recopiés à la main (``REPERES``) ne se retrouvent pas.

Statut de fiabilité : ``haute``, comme les circulaires : la caisse transcrit
l'arrêté.
"""

from __future__ import annotations

import html
import json
import re
import statistics
import sys
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
PAGE = ("https://legislation.lassuranceretraite.fr/Bareme/Pages/doc_communs/"
        "listes_baremes/_layouts/CAMPUS/Campus-baremes/js/declare/"
        "decREVCOEFSALCOT.js")
API = ("https://legislation.lassuranceretraite.fr/api/v1/baremes/"
       "baremesByFileLeafRef/{}.aspx")
#: Les deux barèmes de l'API qui comblent avril 2013 - septembre 2017, avec la
#: date d'effet de leur colonne.
BAREMES = (
    ("2013-04-01", "revalorisation_coefficient_revalorisation_salaire_cotisation_04_2013_bar"),
    ("2015-10-01", "revalorisation_coefficient_revalorisation_salaire_cotisation_10_2015_bar"),
)
BRUT = RACINE / "data" / "brut" / "cnav_revalorisation_salaires_anciennes.json"
SORTIE = RACINE / "data" / "reference" / "legislation" / "revalorisation_salaires_anciennes.csv"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: La page ne date pas toutes ses colonnes juste : voir la docstring.
DATES_CORRIGEES = {"1958-04-01": "1957-04-01", "avant_1949": "1946-05-14"}

#: Première année de perception d'un SALAIRE : avant, la page porte des
#: coefficients de cotisations.
PREMIERE_ANNEE_DE_SALAIRE = 1947

#: À partir de quelle date d'effet deux colonnes consécutives doivent être
#: multiplicatives : avant, l'arrêté fixait un coefficient par année.
MULTIPLICATIVE_DEPUIS = "1952-04-01"
TOLERANCE_MULTIPLICATIVITE = 1e-2

#: Recopiés à la main de la page et des barèmes, pour qu'un défaut de lecture
#: ne puisse pas se reproduire lui-même : (date d'effet, perception, coefficient).
REPERES = (
    ("1949-01-01", 1947, 1.600),
    ("1972-04-01", 1947, 19.015),
    ("1990-07-01", 1989, 1.013),
    ("2012-04-01", 1947, 141.027),
    ("2013-04-01", 1990, 1.431),
    ("2013-04-01", 2014, 1.0),
)

ENTETE_CSV = """\
# Coefficients de revalorisation des salaires portés au compte, 1946-2017
# ----------------------------------------------------------------------
# source_id: cnav_revalorisation_salaires_anciennes
#
# Fichier écrit par scripts/fetch/cnav_revalorisation_salaires_anciennes.py :
# ne pas modifier à la main.
#
# Les colonnes de la Cnav d'AVANT celles des circulaires lues depuis octobre
# 2017 (revalorisation_salaires.csv) : quatre-vingt-six dates d'effet, de
# l'arrêté du 14 mai 1946 à la circulaire 2012/35, puis celles d'avril 2013 et
# d'octobre 2015. Une colonne vaut de sa date d'effet à la suivante ; le modèle
# y lit, pour une liquidation, la colonne EN VIGUEUR à sa date d'effet, et rien
# d'autre : avant 1952, l'arrêté fixait un coefficient par année de perception,
# et le rapport de deux valeurs d'une colonne n'y vaut pas revalorisation.
#
# Salaires seulement, depuis 1947 : pour 1930 à 1946, la caisse publie des
# coefficients de cotisations, que le modèle, qui porte des salaires, ne lit
# pas. Une colonne porte parfois l'année de sa propre date d'effet, au
# coefficient 1.
#
# Trois corrections de la page, que le récupérateur dit : la colonne étiquetée
# « 01/04/1958 » est celle de l'arrêté du 18 avril 1957, datée du 1er avril
# 1957 ; deux valeurs écrites avec un point décimal (1953, en septembre 2008 et
# en avril 2010) ; la colonne « avant 1949 », datée de son arrêté.
#
# fiabilite : `haute`. La caisse transcrit l'arrêté ou la loi qu'elle cite.
date_effet,annee_perception,coefficient,fiabilite
"""


def telecharger(url: str) -> bytes:
    requete = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=120) as reponse:
        return reponse.read()


def _nombre(cellule: str) -> float:
    """« 141,027 » → 141,027 ; « 53.527,175 » → 53 527,175 ; « 40.085 » →
    40,085 : sans virgule, le point est une décimale (voir la docstring)."""
    cellule = cellule.strip().replace(" ", "")
    if "," in cellule:
        return float(cellule.replace(".", "").replace(",", "."))
    return float(cellule)


def lire_page(script: str) -> dict[str, tuple[str, dict[int, float]]]:
    """Les colonnes de la page d'avant 2013 : date d'effet → (référence, table)."""
    blocs = re.findall(
        r't_p\[i\]\s*=\s*"([^"]+)";.*?m_v\[0\]\s*=\s*"([^"]*)";'
        r'.*?m_v\[1\]\s*=\s*new Array\(([^)]*)\)', script, flags=re.S)
    colonnes: dict[str, tuple[str, dict[int, float]]] = {}
    for periode, reference, valeurs in blocs:
        cellules = re.findall(r'"([^"]*)"', valeurs)
        if periode.strip().lower().startswith("avant"):
            effet = DATES_CORRIGEES["avant_1949"]
        else:
            jour, mois, annee = re.search(r"(\d\d)/(\d\d)/(\d{4})", periode).groups()
            effet = DATES_CORRIGEES.get(f"{annee}-{mois}-{jour}", f"{annee}-{mois}-{jour}")
        # Treize cellules de cotisations — 1930-1935 en deux catégories, puis
        # 1936 à 1946 —, puis les salaires depuis 1947.
        table = {PREMIERE_ANNEE_DE_SALAIRE + rang: _nombre(c)
                 for rang, c in enumerate(cellules[13:]) if c.strip()}
        if effet in colonnes:
            raise ValueError(f"deux colonnes au {effet}")
        colonnes[effet] = (" ".join(reference.split()), table)
    return colonnes


def lire_bareme(contenu: str) -> dict[int, float]:
    """Les salaires d'un barème de l'API : les lignes « année | coefficient »,
    sans le tableau des cotisations d'avant 1947."""
    texte = html.unescape(re.sub(r"<[^>]+>", "|", contenu)).replace("​", "")
    salaires = re.split(r"cotisations avant 1947", texte, flags=re.I)[0]
    table: dict[int, float] = {}
    for annee, valeur in re.findall(
            r"\|\s*(19\d\d|20\d\d)\s*\|[\s|]*([\d ]+(?:,\d+)?)\s*(?:\(Pas de revalorisation\))?\s*\|",
            salaires):
        if int(annee) >= PREMIERE_ANNEE_DE_SALAIRE:
            table.setdefault(int(annee), _nombre(valeur))
    return table


def controler(colonnes: dict[str, dict[int, float]]) -> list[str]:
    """Ce qu'une colonne lue doit vérifier pour être crédible."""
    griefs = []
    for effet, table in sorted(colonnes.items()):
        annees = sorted(table)
        if not annees or annees[0] != PREMIERE_ANNEE_DE_SALAIRE:
            griefs.append(f"{effet} : la colonne ne commence pas en 1947")
            continue
        if annees != list(range(annees[0], annees[-1] + 1)):
            griefs.append(f"{effet} : la suite des années a des trous")
        # La colonne porte les salaires déjà connus quand elle s'applique : ceux
        # de l'année d'avant, parfois de la sienne ; ceux de 1948 pour la
        # colonne « avant 1949 », qui vaut jusqu'à la fin de 1948.
        if not int(effet[:4]) - 2 <= annees[-1] <= int(effet[:4]) + 2:
            griefs.append(f"{effet} : dernière perception {annees[-1]}, hors de portée")
        for avant, apres in zip(annees, annees[1:]):
            if table[apres] > table[avant] + 1e-9:
                griefs.append(f"{effet} : le coefficient remonte de {avant} à {apres}")
        if min(table.values()) < 1.0:
            griefs.append(f"{effet} : un coefficient est inférieur à 1")
    dates = sorted(colonnes)
    for avant, apres in zip(dates, dates[1:]):
        if avant < MULTIPLICATIVE_DEPUIS:
            continue
        a, b = colonnes[avant], colonnes[apres]
        communes = [p for p in a if p in b and p <= max(a) - 2]
        if not communes:
            continue
        rapports = [b[p] / a[p] for p in communes]
        mediane = statistics.median(rapports)
        pire = max(abs(r / mediane - 1) for r in rapports)
        if pire > TOLERANCE_MULTIPLICATIVITE:
            griefs.append(f"{avant} → {apres} : une perception s'écarte de {pire:.2%} "
                          "du coefficient commun")
    for effet, perception, attendu in REPERES:
        lu = colonnes.get(effet, {}).get(perception)
        if lu is None or abs(lu - attendu) > 5e-4:
            griefs.append(f"repère {effet}, {perception} : attendu {attendu}, lu {lu}")
    return griefs


def main() -> int:
    page = lire_page(telecharger(PAGE).decode("latin-1"))
    references = {effet: reference for effet, (reference, _) in page.items()}
    colonnes = {effet: table for effet, (_, table) in page.items()}
    for effet, bareme in BAREMES:
        reponse = json.loads(telecharger(API.format(bareme)).decode("utf-8-sig"))
        reponse = reponse[0] if isinstance(reponse, list) else reponse
        colonnes[effet] = lire_bareme(reponse["contenu"])
        references[effet] = f"barème {bareme}"
    griefs = controler(colonnes)
    if griefs:
        print("Colonnes refusées :", *griefs, sep="\n  ", file=sys.stderr)
        return 1
    BRUT.parent.mkdir(parents=True, exist_ok=True)
    BRUT.write_text(json.dumps({
        "sources": [PAGE] + [API.format(b) for _, b in BAREMES],
        "recupere_le": date.today().isoformat(),
        "references": references,
        "colonnes": {effet: {str(a): v for a, v in sorted(table.items())}
                     for effet, table in sorted(colonnes.items())},
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    lignes = [f"{effet},{annee},{coefficient:.10g},haute\n"
              for effet, table in sorted(colonnes.items())
              for annee, coefficient in sorted(table.items())]
    SORTIE.write_bytes((ENTETE_CSV + "".join(lignes)).encode("utf-8"))
    print(f"{SORTIE.relative_to(RACINE)} : {len(colonnes)} colonnes, "
          f"{len(lignes)} coefficients, du {min(colonnes)} au {max(colonnes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
