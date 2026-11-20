#!/usr/bin/env python3
"""Récupération du prix et de la valeur du point de la complémentaire des
médecins, dans « La chronologie des chiffres de la CARMF ».

    python scripts/fetch/carmf_chronologie.py

La caisse est le producteur, et la seule à publier ces nombres. Sa chronologie,
un PDF d'une centaine de pages, porte deux tables qui suffisent à compter des
points depuis 1996, l'année où la cotisation du régime complémentaire devient
« totalement proportionnelle aux revenus » :

* « Régime complémentaire, cotisations proportionnelles » : pour chaque année
  de cotisation, la cotisation maximale et les **points attribués**, dix de
  1996 à 2025. Le point s'achète donc au dixième de cette cotisation ;
* « Rendement du régime complémentaire » et « Valeurs des points de
  retraite » : la **valeur du point** du médecin, « à 65 ans » jusqu'en 2016,
  « à 62 ans » depuis 2017, quand le règlement sert sans coefficient à l'âge
  légal et majore au-delà de soixante-deux ans.

Le règlement du régime (arrêté du 10 juillet 2026, article 3) dit que « le
montant de la retraite d'un médecin s'obtient en multipliant le nombre de
points acquis, alloués ou rachetés, par la valeur du point » : ces deux tables
sont ce qu'il faut au moteur pour le faire, au lieu du rendement de l'année du
départ qu'il appliquait jusqu'au 20 novembre 2026.

Le garde-fou. Lire un PDF, c'est reconstituer une mise en page. Le script
refuse donc d'écrire une série où une année de 1996 à la dernière manquerait,
où la cotisation maximale n'attribuerait pas dix points, où elle baisserait de
plus de 1 %, ou dont la valeur du point sortirait de 60 à 90 €.

Avant 1996, une cotisation forfaitaire (quatre points) et une proportionnelle
assise entre un plancher et un plafond achètent à deux prix la même année : ces
années ne sont pas extraites, et le moteur les garde au rendement
(`rendements_points.csv`, `docs/limites.md`).

L'ANNÉE EN COURS n'est pas dans la chronologie, qui paraît l'année d'après.
Elle est SAISIE ici depuis les pages « chiffres clés » de la caisse, au niveau
``moyenne`` : voir `SAISIES`.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_pdf import lignes_pdf  # noqa: E402
from source_locale import telecharger  # noqa: E402

URL = "https://www.carmf.fr/doc/publications/chronologie/2025/chronologie-2025.pdf"
SORTIE = Path("data/brut/carmf_chronologie.json")
REGIME = "carmf_complementaire"
PREMIERE, DERNIERE = 1996, 2025

#: Les chiffres clés de 2026, lus le 22 septembre et relus le 20 novembre 2026
#: sur https://www.carmf.fr/page.php?page=cdrom/retr/retr-chiffre.htm (« 11,52
#: points maximum », « 77,14 € » le point à 62 ans) et sur la page des
#: cotisations (11,8 % dans la limite de trois plafonds et demi, 19 849 €) : le
#: point s'achète 19 849 / 11,52 €.
SAISIES = {
    f"{REGIME}|2026|salaire_reference": round(19_849 / 11.52, 6),
    f"{REGIME}|2026|taux_appel": 1.0,
    f"{REGIME}|2026|valeur_service": 77.14,
}
ORIGINE_SAISIES = (
    "CARMF, chiffres clés de 2026 lus sur le site de la caisse le 20 novembre "
    "2026 : 19 849 € de cotisation maximale pour 11,52 points, 77,14 € le point"
)

_EUROS = r"(\d{1,3}(?:[   ]\d{3})*,\d{2,3})[   ]?€"
#: « 2025 2023 0 164 850,00 € - 10,2 % 16 815,00 € 10 » : l'année de
#: cotisation, celle des revenus, le plancher nul, le plafond, le taux, la
#: cotisation maximale et les points attribués.
COTISATION = re.compile(
    r"^(?:\(\d\) )?((?:19|20)\d\d) (?:19|20)\d\d 0 " + _EUROS
    + r" - \d+(?:,\d+)?[   ]?% " + _EUROS + r" (\d+(?:,\d+)?)$")
#: « 2 68,53 € 9,99 % 1996 6 860,21 € » : la table des rendements, dont les
#: cellules sortent dans un ordre qui change d'une ligne à l'autre.
ANNEE = re.compile(r"(?<![\d,])((?:19|20)\d\d)(?![\d,])")
#: On en ôte d'abord la cotisation, qui a ses milliers, puis on lit ce qui reste.
MILLIERS = re.compile(r"\d{1,3} \d{3},\d\d ?€")
VALEUR = re.compile(r"(?<![\d,])(\d\d,\d{2,3}) ?€")
#: « (2) 1994 0 91 469,41 € - 7,5 % 6 860,21 € 10 1996 » : la ligne de 1996,
#: dont l'année de cotisation sort en dernier.
COTISATION_DE_1996 = re.compile(
    r"^\(\d\) (?:19|20)\d\d 0 " + _EUROS
    + r" - \d+(?:,\d+)? ?% " + _EUROS + r" (\d+(?:,\d+)?) (1996)$")
#: « (1) (6) (6) 2025 0,6540 € 76,15 € 45,69 € … » : la table des valeurs, pour
#: la dernière année, dont la table des rendements donne une moyenne.
DERNIERE_VALEUR = re.compile(
    r"\b" + str(DERNIERE) + r" 0,\d{3,4}[   ]?€ (\d\d,\d\d)[   ]?€")


def _nombre(texte: str) -> float:
    return float(re.sub(r"[   ]", "", texte).replace(",", "."))


def _propre(ligne: str) -> str:
    """La ligne, ses espaces insécables rendus ordinaires."""
    return re.sub(r"[\u00a0\u202f]", " ", ligne).strip()


def extraire(lignes: list[str]) -> dict[int, tuple[float, float, float]]:
    """Par année : (cotisation maximale, points attribués, valeur du point)."""
    cotisations: dict[int, tuple[float, float]] = {}
    for ligne in lignes:
        propre = _propre(ligne)
        trouve = COTISATION.match(propre)
        if trouve:
            cotisations[int(trouve.group(1))] = (
                _nombre(trouve.group(3)), _nombre(trouve.group(4)))
        trouve = COTISATION_DE_1996.match(propre)
        if trouve:
            cotisations[1996] = (_nombre(trouve.group(2)), _nombre(trouve.group(3)))
    valeurs: dict[int, float] = {}
    dans_la_table = False
    for ligne in lignes:
        if ligne.startswith("Rendement du régime complémentaire"):
            dans_la_table = True
        elif dans_la_table and ligne.startswith("Montant maximum de la cotisation"):
            dans_la_table = False
        if not dans_la_table or "%" not in ligne:
            continue
        reste = MILLIERS.sub(" ", _propre(ligne))
        annees = ANNEE.findall(reste)
        lues = VALEUR.findall(reste)
        if len(annees) == 1 and len(lues) == 1:
            valeurs[int(annees[0])] = _nombre(lues[0])
    for ligne in lignes:
        trouve = DERNIERE_VALEUR.search(_propre(ligne))
        if trouve:
            valeurs[DERNIERE] = _nombre(trouve.group(1))
    return {annee: (*cotisations[annee], valeurs[annee])
            for annee in sorted(cotisations) if annee in valeurs and annee >= PREMIERE}


def verifier(serie: dict[int, tuple[float, float, float]]) -> list[str]:
    """Contrôle de structure : sans lui, une erreur de lecture passerait."""
    anomalies = [f"année {annee} absente" for annee in range(PREMIERE, DERNIERE + 1)
                 if annee not in serie]
    precedente = None
    for annee, (maximale, points, valeur) in sorted(serie.items()):
        if points != 10:
            anomalies.append(f"{annee} : {points} points pour la cotisation maximale, et non dix")
        if not 60 <= valeur <= 90:
            anomalies.append(f"{annee} : valeur du point de {valeur} €")
        if precedente is not None and maximale < 0.99 * precedente:
            anomalies.append(f"{annee} : cotisation maximale en baisse, {maximale} €")
        precedente = maximale
    return anomalies


def main() -> int:
    try:
        octets = telecharger(URL)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as erreur:
        print(f"Échec : {URL} : {erreur}", file=sys.stderr)
        return 1
    lue = extraire(lignes_pdf(octets))
    anomalies = verifier(lue)
    if anomalies:
        print("Série refusée :\n  " + "\n  ".join(anomalies), file=sys.stderr)
        return 1
    serie: dict[str, float] = {}
    for annee, (maximale, points, valeur) in sorted(lue.items()):
        serie[f"{REGIME}|{annee}|salaire_reference"] = round(maximale / points, 6)
        serie[f"{REGIME}|{annee}|taux_appel"] = 1.0
        serie[f"{REGIME}|{annee}|valeur_service"] = valeur
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": URL,
            "telecharge_le": date.today().isoformat(),
            "serie": serie,
            "origine_saisies": ORIGINE_SAISIES,
            "saisies": SAISIES,
        }, ensure_ascii=False, indent=1, sort_keys=True),
        encoding="utf-8",
    )
    print(f"{SORTIE} : {len(lue)} années, de {min(lue)} à {max(lue)}, "
          f"et {len(SAISIES)} valeurs saisies pour 2026")
    return 0


if __name__ == "__main__":
    sys.exit(main())
