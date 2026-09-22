#!/usr/bin/env python3
"""Retenue et contribution de la CNRACL, chez le gestionnaire du régime.

    python scripts/fetch/juris_cnracl_taux.py

Ce que le script referme. La contribution EMPLOYEUR de la CNRACL est, pour un
agent territorial ou hospitalier, trois fois sa retenue : c'est elle qui décide
de l'essentiel de ce que les scénarios 4 et 5 lui servent. Le dépôt la tenait
de trois sources de rang inégal — le *Journal officiel* pour 1984-1988 et
1993-2028 (`dila_legi_cnracl.py`, `certifiee`), et OpenFisca-France pour tout
le reste, transcription tierce plafonnée à `haute`. Quarante-cinq années
restaient donc au deuxième rang, faute d'une source de premier rang.

Elle existe, et elle est publiée : la **documentation juridique de la CNRACL**
(`juris-cnracl.retraites.fr`), que la Caisse des dépôts tient pour les
employeurs territoriaux et hospitaliers. La Caisse GÈRE le régime : elle en est
le producteur, pas un tiers qui le recopie. Sa page « Cotisations — Historique
des taux applicables » porte un tableau de quarante-neuf périodes, du
19 septembre 1947 — la création de la Caisse nationale — à 2026, avec pour
chacune la retenue de l'agent et la contribution de l'employeur.

LA CONVENTION DE DATE, ET CE QU'ELLE CACHE

Le tableau est par PÉRIODE, le dépôt travaille par ANNÉE. La convention
retenue est celle que les séries du dépôt appliquent déjà : le taux en vigueur
au 1er janvier vaut pour l'année. Elle a l'avantage de coïncider avec la
lecture du *Journal officiel* faite par `dila_legi_cnracl.py`, dont les décrets
paraissent en janvier et valent pour l'exercice entier ; les deux sources
peuvent donc se recouper valeur par valeur, et elles s'accordent.

Ce qu'elle cache, et qu'il faut dire : neuf années ont vu leur taux changer en
cours de route, et la plus spectaculaire est 1980, où la contribution est
tombée de 18 % à 6 % au 1er juillet — l'année entière vaut 12 % en trésorerie
et 18 % sous la convention. Le script imprime ces années et les consigne dans
le fichier brut, sous `changement|<annee>`, pour qu'on sache où la convention
coûte quelque chose.

UNE COQUILLE DANS LA SOURCE, ET C'EST UN AVERTISSEMENT

La ligne de 2020 s'écrit « Du 01/01/20 au 31/12/2020 » : deux chiffres au lieu
de quatre. Le script la répare en lisant l'année de la date de FIN, et il le
dit. Une source officielle est écrite par des mains humaines ; c'est la
première coquille rencontrée dans ce tableau, ce n'est probablement pas la
dernière, et un analyseur qui l'aurait ignorée en silence aurait perdu une
année sans que personne le sache.
"""

from __future__ import annotations

import html
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "brut" / "juris_cnracl_taux.json"

URL = ("https://www.juris-cnracl.retraites.fr/cotisations/taux-de-cotisations"
       "/cotisations-historique-des-taux-applicables")

#: Première année servie. La Caisse nationale est créée par le décret
#: n° 47-1846 du 19 septembre 1947 ; 1947 n'est pas une année pleine et le
#: dépôt ne la porte pas.
PREMIERE_ANNEE = 1948

LIGNE = re.compile(r"<tr.*?</tr>", re.S)
CELLULE = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
PERIODE = re.compile(
    r"(?:Du\s+)?(\d{2})/(\d{2})/(\d{2,4})\s+au\s+(\d{2})/(\d{2})/(\d{4})")


def _texte(brut: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", " ", brut)).replace("\xa0", " ").strip()


def _pourcentage(cellule: str) -> float | None:
    trouve = re.search(r"(\d+(?:[.,]\d+)?)\s*%", cellule)
    return float(trouve.group(1).replace(",", ".")) / 100.0 if trouve else None


def _periodes(page: str) -> tuple[list[dict], list[str]]:
    """Les périodes du tableau, de la plus récente à la plus ancienne."""
    periodes: list[dict] = []
    remarques: list[str] = []
    for ligne in LIGNE.findall(page):
        cellules = [_texte(c) for c in CELLULE.findall(ligne)]
        if len(cellules) < 3:
            continue
        bornes = PERIODE.search(cellules[0])
        if not bornes:
            continue
        jour, mois, an, _, _, an_fin = bornes.groups()
        if len(an) < 4:
            # « Du 01/01/20 au 31/12/2020 » : l'année de début est tronquée.
            an = an_fin
            remarques.append(
                f"année de début tronquée dans « {cellules[0]} », lue sur la "
                f"date de fin : {an}")
        retenue, contribution = _pourcentage(cellules[1]), _pourcentage(cellules[2])
        if retenue is None or contribution is None:
            continue
        periodes.append({
            "debut": date(int(an), int(mois), int(jour)),
            "fin": date(int(an_fin), 12, 31) if an_fin else None,
            "retenue": retenue,
            "contribution": contribution,
            "libelle": cellules[0],
        })
    return periodes, remarques


def _annuel(periodes: list[dict], champ: str) -> tuple[dict[int, float], dict[int, str]]:
    """Le taux en vigueur au 1er janvier, année par année, et les changements.

    Les périodes sont triées par date de début ; pour chaque année, on retient
    la dernière période commencée au plus tard le 1er janvier. Une année qui
    voit une période commencer APRÈS son 1er janvier est signalée : la
    convention y perd quelque chose.
    """
    ordonnees = sorted(periodes, key=lambda p: p["debut"])
    derniere = max(p["debut"].year for p in ordonnees)
    serie: dict[int, float] = {}
    changements: dict[int, str] = {}
    for annee in range(PREMIERE_ANNEE, derniere + 1):
        premier_janvier = date(annee, 1, 1)
        en_vigueur = [p for p in ordonnees if p["debut"] <= premier_janvier]
        if not en_vigueur:
            continue
        serie[annee] = en_vigueur[-1][champ]
        en_cours = [p for p in ordonnees
                    if p["debut"].year == annee and p["debut"] > premier_janvier]
        for p in en_cours:
            if p[champ] != serie[annee]:
                changements[annee] = (
                    f"{serie[annee]:.2%} au 1er janvier, {p[champ]:.2%} "
                    f"à partir du {p['debut'].strftime('%d/%m')}")
    return serie, changements


def main() -> int:
    demande = urllib.request.Request(
        URL, headers={"User-Agent": "retraite-notionnelle/0.1"})
    try:
        with urllib.request.urlopen(demande, timeout=120) as reponse:
            page = reponse.read().decode("utf-8", errors="replace")
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"Documentation juridique CNRACL indisponible : {erreur}",
              file=sys.stderr)
        return 1

    periodes, remarques = _periodes(page)
    if len(periodes) < 40:
        print(f"Tableau illisible : {len(periodes)} périodes trouvées, "
              "une quarantaine attendues", file=sys.stderr)
        return 1

    retenues, changements_retenue = _annuel(periodes, "retenue")
    contributions, changements_contribution = _annuel(periodes, "contribution")

    for remarque in remarques:
        print(f"COQUILLE {remarque}")
    changements = {**changements_retenue, **changements_contribution}
    for annee in sorted(changements):
        print(f"EN COURS D'ANNÉE {annee} : {changements[annee]}")
    print(f"{len(periodes)} périodes, de {min(p['debut'] for p in periodes)} à "
          f"{max(p['debut'] for p in periodes)} ; retenue et contribution "
          f"annualisées sur {len(retenues)} années "
          f"({min(retenues)}-{max(retenues)})")

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": URL,
            "recupere_le": date.today().isoformat(),
            "note": "Retenue de l'agent et contribution de l'employeur à la "
                    "CNRACL, telles que la documentation juridique de la Caisse "
                    "des dépôts — gestionnaire du régime, donc productrice — les "
                    "publie par période depuis le 19 septembre 1947. La série "
                    "annuelle applique la convention du dépôt : le taux en "
                    "vigueur au 1er janvier vaut pour l'année. Les années dont "
                    "le taux a changé en cours de route sont rendues sous "
                    "`changement|<annee>`, la plus notable étant 1980, où la "
                    "contribution tombe de 18 % à 6 % au 1er juillet.",
            "serie": {
                **{f"retenue|{a}": v for a, v in sorted(retenues.items())},
                **{f"contribution|{a}": v for a, v in sorted(contributions.items())},
            },
            "changements": {str(a): changements[a] for a in sorted(changements)},
            "coquilles": remarques,
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"{2 * len(retenues)} valeurs écrites dans {SORTIE.relative_to(RACINE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
