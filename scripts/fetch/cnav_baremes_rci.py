#!/usr/bin/env python3
"""Prix et valeur du point du RCI, dans les barèmes de législation de la Cnav.

    python scripts/fetch/cnav_baremes_rci.py

POURQUOI IL EXISTE. La transcription d'OpenFisca-France-Pension s'arrête en
2023 pour la complémentaire des indépendants. Faute de valeurs, le modèle
retombait pour 2024 et au-delà sur un rendement instantané de 6,74 % — celui
de 2013 —, quand le rendement réel est descendu à 6,20 % en 2024 : les points
d'un artisan ou d'un commerçant étaient surestimés d'environ 9 %, ce que la
calculette de l'Urssaf a montré le 22 septembre 2026 (44,7 points pour
12 000 € de revenu en 2026, là où le modèle en donnait 48,8).

La Cnav sert, depuis sa base de législation, deux barèmes que son site lit par
une API publique :

* ``rci_valeur_achat_point_bar`` — le « revenu de référence », valeur d'achat
  du point, par date d'effet, chaque ligne citant la circulaire qui la porte ;
* ``rci_valeur_point_bar`` — la valeur de service, par année, sous l'intitulé
  « Point RCI cotisé ».

Statut de fiabilité : ``haute``, jamais ``certifiee``. Ces valeurs sont
fixées par le conseil de la protection sociale des travailleurs indépendants ;
la Cnav, qui liquide ces pensions depuis 2020, les reprend dans ses
circulaires. C'est une transcription, comme celle d'OpenFisca.

Le script ne garde que les années qu'OpenFisca ne porte pas : les autres sont
déjà couvertes, et deux contrôles ne revendiquent pas la même ligne. Il relit
néanmoins les années communes et refuse d'écrire si l'une diffère de la
valeur du dépôt — une transcription qui contredit l'autre sans que personne
le voie serait pire que pas de source du tout.
"""

from __future__ import annotations

import csv
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
BAREMES = {
    "salaire_reference": "rci_valeur_achat_point_bar",
    "valeur_service": "rci_valeur_point_bar",
}
SORTIE = RACINE / "data" / "brut" / "cnav_baremes_rci.json"
REFERENCE = RACINE / "data" / "reference" / "regimes" / "valeurs_point.csv"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Dernière année que la transcription d'OpenFisca porte pour le RCI.
FIN_OPENFISCA = 2023


def _texte(fragment: str) -> str:
    """Le texte d'un morceau de HTML : sans balises, espaces insécables
    ni caractères de largeur nulle, que l'éditeur de la Cnav sème partout."""
    brut = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"[\s​﻿]+", " ", brut).strip()


def _nombre(texte: str) -> float:
    return float(re.search(r"\d+,\d+", texte).group(0).replace(",", "."))


def lire_achat(contenu: str) -> dict[int, float]:
    """Une ligne par date d'effet : « 01/01/2026 | 21,726 € | circulaire »."""
    valeurs: dict[int, float] = {}
    for ligne in re.findall(r"<tr>(.*?)</tr>", contenu, flags=re.S):
        cellules = [_texte(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", ligne, flags=re.S)]
        if len(cellules) < 2:
            continue
        date_effet = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", cellules[0])
        if not date_effet or not re.search(r"\d+,\d+", cellules[1]):
            continue
        annee = int(date_effet.group(3))
        # La règle du dépôt retient la valeur en vigueur au 31 décembre. Le
        # barème va de la plus récente à la plus ancienne : si une année
        # avait deux dates d'effet, la première lue, la plus tardive, reste.
        valeurs.setdefault(annee, _nombre(cellules[1]))
    return valeurs


def lire_service(contenu: str) -> dict[int, float]:
    """Un tableau par année, sous un titre « 2026 » ; la ligne « Point RCI
    cotisé » porte la valeur de service du régime unifié."""
    valeurs: dict[int, float] = {}
    morceaux = re.split(r"<h2[^>]*>(.*?)</h2>", contenu, flags=re.S)
    for titre, corps in zip(morceaux[1::2], morceaux[2::2]):
        annee = re.fullmatch(r"(\d{4})", _texte(titre))
        if not annee:
            continue
        for ligne in re.findall(r"<tr>(.*?)</tr>", corps, flags=re.S):
            cellules = [_texte(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", ligne, flags=re.S)]
            if len(cellules) >= 2 and cellules[0].startswith("Point RCI cotisé"):
                valeurs[int(annee.group(1))] = _nombre(cellules[1])
    return valeurs


def telecharger(fichier: str) -> str:
    requete = urllib.request.Request(API.format(fichier), headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=60) as reponse:
        return json.loads(reponse.read().decode("utf-8"))["contenu"]


def main() -> int:
    lus = {
        "salaire_reference": lire_achat(telecharger(BAREMES["salaire_reference"])),
        "valeur_service": lire_service(telecharger(BAREMES["valeur_service"])),
    }
    with REFERENCE.open(encoding="utf-8") as flux:
        depot = {
            (ligne["annee"], ligne["mesure"]): float(ligne["valeur"])
            for ligne in csv.DictReader(l for l in flux if not l.startswith("#"))
            if ligne["regime"] == "rci"
        }

    serie: dict[str, float] = {}
    desaccords = []
    for mesure, valeurs in lus.items():
        if not valeurs:
            print(f"{mesure} : aucun barème lu", file=sys.stderr)
            return 1
        for annee, valeur in sorted(valeurs.items()):
            if annee <= FIN_OPENFISCA:
                connu = depot.get((str(annee), mesure))
                if connu is not None and abs(connu - valeur) > 5e-7:
                    desaccords.append(f"rci {annee} {mesure} : Cnav {valeur}, dépôt {connu}")
                continue
            serie[f"rci|{annee}|{mesure}"] = valeur
    if desaccords:
        print("La Cnav contredit la transcription du dépôt :", *desaccords,
              sep="\n  ", file=sys.stderr)
        return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": "Cnav, base de législation : " + ", ".join(BAREMES.values()),
        "recupere_le": date.today().isoformat(),
        "serie": dict(sorted(serie.items())),
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(serie)} valeurs écrites dans {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
