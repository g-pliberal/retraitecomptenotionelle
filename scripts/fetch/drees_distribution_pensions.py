#!/usr/bin/env python3
"""Récupération de la distribution des pensions, auprès de la DREES.

    python scripts/fetch/drees_distribution_pensions.py

L'échantillon interrégimes de retraités (EIR) est l'appariement, tous les quatre
ans, des fichiers de toutes les caisses sur un même échantillon d'individus.
C'est la seule source française qui dise combien de retraités touchent combien —
non pas la moyenne d'un régime, mais la RÉPARTITION des pensions individuelles,
par tranches de cent euros.

À QUOI CETTE SÉRIE SERT
-----------------------
À chiffrer la garantie vieillesse du scénario 6. Une allocation différentielle
qui porte toute pension à 800 € — 1 050 € pour qui vit seul — ne se chiffre pas
sur treize cas types : elle se chiffre sur la queue basse de la distribution, et
c'est celle-ci. La page « Coût » donnait jusqu'ici le coût de la garantie tel
que le voyaient les seuls cas types qui liquident à 65 ans ou après ; elle donne
désormais aussi ce que le barème coûte appliqué à la distribution réelle.

CE QU'ON RETIENT, ET POURQUOI
-----------------------------
Le classeur porte huit tableaux ; on lit le PREMIER, « pension mensuelle BRUTE
de DROIT DIRECT », parce que c'est le seul des huit qui soit dans la même
grandeur que la pension du modèle :

* **brute**, parce que le modèle ne calcule aucun prélèvement social ; comparer
  une pension brute à un plancher net surestimerait le nombre de bénéficiaires ;
* **de droit direct**, parce que la réversion est hors du modèle par
  construction — il décrit une carrière, pas un ménage. Les tableaux « pension
  totale » l'incluent, et ils sont donc écartés.

Une réserve demeure, qui n'a pas de remède dans cette source : le tableau
comprend la majoration pour trois enfants, que les scénarios notionnels ne
servent pas.

Le fichier produit, ``data/brut/drees_distribution_pensions.json``, est le
document source : il n'est pas lu par le modèle, seulement par
``scripts/verifier_donnees.py``, qui en écrit
``data/reference/macro/distribution_pensions.csv``.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lecture_xlsx import feuilles  # noqa: E402

BASE = (
    "https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog"
    "/datasets/4178_distribution-des-pensions-mensuelles"
)
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/drees_distribution_pensions.json")

#: Feuille du classeur : la pension brute de droit direct.
FEUILLE = "pension brute de droit direct"

#: Colonnes du tableau, dans l'ordre où le classeur les range.
SEXES = {1: "F", 2: "H", 3: "ensemble"}

_TRANCHE = re.compile(r"De (\d+) à (\d+) euros")
_QUEUE = re.compile(r"Supérieur à (\d+) euros")
_ANNEE = re.compile(r"EIR\s*(\d{4})")


def _pieces_jointes() -> list[dict]:
    demande = urllib.request.Request(f"{BASE}/attachments", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=120) as reponse:
        return json.loads(reponse.read()).get("attachments", [])


def classeur_le_plus_recent() -> tuple[int, str, bytes]:
    """Télécharge le classeur de l'EIR le plus récent joint au jeu.

    La DREES empile les millésimes de l'EIR dans le même jeu — 2012, 2016,
    2020 — et n'en retire aucun. Le millésime se lit dans le nom de la pièce
    jointe, et c'est le plus élevé qu'on retient : chaque EIR décrit un état de
    la population à sa date, et le dernier est le moins périmé.
    """
    candidats = []
    for piece in _pieces_jointes():
        metas = piece.get("metas") or {}
        trouve = _ANNEE.search(metas.get("title", ""))
        if trouve and metas.get("mimetype", "").endswith("spreadsheetml.sheet"):
            candidats.append((int(trouve.group(1)), metas["title"], metas["url"]))
    if not candidats:
        raise RuntimeError("aucun classeur EIR joint au jeu de la DREES")
    annee, titre, url = max(candidats)
    demande = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=600) as reponse:
        return annee, titre, reponse.read()


def lire_distribution(contenu: bytes) -> dict[str, dict[str, float]]:
    """Parts de chaque tranche de cent euros, par sexe, en pour cent.

    Les tranches sont identifiées par leur BORNE INFÉRIEURE, en euros par mois :
    « 700 » est la tranche de 700 à 800 euros, et la dernière — ouverte — porte
    la borne au-delà de laquelle le classeur ne découpe plus. C'est un identifiant
    stable, là où le libellé change de forme d'un millésime à l'autre.
    """
    grille = feuilles(contenu)[FEUILLE]
    derniere_ligne = max(ligne for ligne, _ in grille)
    parts: dict[str, dict[str, float]] = {code: {} for code in SEXES.values()}
    for ligne in range(derniere_ligne + 1):
        libelle = grille.get((ligne, 0))
        if not isinstance(libelle, str):
            continue
        tranche = _TRANCHE.match(libelle.strip()) or _QUEUE.match(libelle.strip())
        if tranche is None:
            continue
        borne = tranche.group(1)
        for colonne, code in SEXES.items():
            valeur = grille.get((ligne, colonne))
            if isinstance(valeur, float):
                parts[code][borne] = valeur
    if not parts["ensemble"]:
        raise RuntimeError(f"feuille {FEUILLE!r} illisible")
    return {
        code: {borne: serie[borne] for borne in sorted(serie, key=int)}
        for code, serie in parts.items()
    }


def main() -> int:
    try:
        annee, titre, contenu = classeur_le_plus_recent()
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1

    parts = lire_distribution(contenu)
    charge = {
        "source": BASE,
        "fichier": titre,
        "millesime": annee,
        "mesure": "pension mensuelle brute de droit direct",
        "unite": "pour cent des retraités de droit direct",
        "parts": parts,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    print(f"EIR {annee} : {len(parts['ensemble'])} tranches écrites dans {SORTIE}")
    for code, serie in parts.items():
        print(f"  {code} : somme des parts {sum(serie.values()):.2f} %")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
