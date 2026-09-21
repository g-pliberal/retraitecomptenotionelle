#!/usr/bin/env python3
"""Ce que les carrières des femmes et des hommes doivent aux droits non cotisés.

    python scripts/fetch/drees_caracteristiques_retraites.py

POURQUOI CETTE SOURCE
---------------------
La garantie vieillesse du scénario 6 est chiffrée en déplaçant la distribution
des pensions de l'EIR d'un facteur unique. Le scénario ne déplace pourtant pas
toutes les carrières du même rapport : il retire les droits NON COTISÉS, et les
femmes en détiennent plus souvent. Le dépôt savait le dire, savait qu'il se
trompait dans un sens connu, et ne savait pas de combien — faute d'une
ventilation par sexe de ce que les avantages non contributifs pèsent.

La voici. Le même échantillon interrégimes qui porte la distribution porte
aussi, dans un autre classeur du même millésime, les CARACTÉRISTIQUES des
retraités par sexe. Deux d'entre elles suffisent :

* **la proportion de la durée validée qui n'est pas cotisée** — 26,0 % chez les
  femmes contre 10,9 % chez les hommes en 2020. Un compte notionnel ne crédite
  que ce qui a été cotisé : une année validée sans cotisation n'y porte RIEN,
  qu'elle vienne de l'AVPF, du chômage, de la maladie ou d'une majoration de
  durée. C'est le terme qui domine ;
* **la pension de droit direct, avec et sans les majorations pour enfants** —
  1 152 contre 1 122 euros chez les femmes, 1 840 contre 1 784 chez les hommes.
  La majoration pèse 2,6 % de la pension des femmes et 3,0 % de celle des
  hommes : elle est proportionnelle à la pension, et les pensions des hommes
  sont plus hautes. Ce terme joue donc à l'envers de l'intuition, et c'est
  précisément pourquoi il vaut mieux le lire que le supposer.

Le classeur porte en outre les EFFECTIFS par sexe, que le dépôt n'avait pas :
8 737 milliers de femmes sur 16 553 retraités en 2020, soit 52,8 %. C'est le
poids que ``donnees.distribution.part_femmes`` ajustait jusque-là sur les
tranches, faute de mieux — une déduction, là où il y avait une lecture.

CE QU'ON NE LIT PAS ICI, ET QUI IRAIT DANS LE MÊME SENS
--------------------------------------------------------
Le classeur donne la PART de bénéficiaires d'un minimum de pension — 46,5 %
des femmes contre 26,1 % des hommes — mais pas ce que ce minimum leur APPORTE.
Le retirer creuserait l'écart davantage : la mesure qui suit est donc, elle
aussi, une borne basse.
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
    "/datasets/3013_donnees-statistiques-sur-les-caracteristiques-des-retraites"
)
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/drees_caracteristiques_retraites.json")

#: Feuille du classeur. Elle croise le sexe et le quintile de pension ; la
#: colonne « Ensemble » porte la valeur tous quintiles confondus, et c'est la
#: seule qu'on lise — le quintile n'ajoute rien à la question posée.
FEUILLE = "Quintiles"

#: Le classeur empile les millésimes dans le même jeu, et chacun en trois
#: variantes : tous les retraités, ceux qui résident en France, une génération.
#: On retient « tous les retraités », qui est le champ de la distribution.
_TITRE = re.compile(r"Caractéristiques de tous les retraités \(EIR (\d{4})\)")

#: Les six indicateurs retenus, sous le code que le dépôt leur donne et le
#: libellé, tronqué, que le classeur leur donne. Le libellé complet varie d'un
#: millésime à l'autre par sa ponctuation ; le début, non.
INDICATEURS: dict[str, str] = {
    "effectifs": "Effectifs (en milliers)",
    "pension_droit_direct": (
        "Montant moyen de la pension de retraite de droit direct brute"
    ),
    "pension_droit_direct_majorations": (
        "Montant moyen de la pension de droit direct (dont les majorations pour "
        "enfants) brute"
    ),
    "duree_validee_non_cotisee": (
        "Proportion de la durée validée qui n'est pas cotisée"
    ),
    "duree_validee": "Moyenne de la durée validée",
    "coefficient_proratisation": "Coeficient de proratisation moyen",
    # Pas dans le rapport : la PART de bénéficiaires ne dit pas ce que le
    # minimum leur apporte. Elle est lue quand même, parce que la page la cite
    # pour dire dans quel sens la mesure est une borne basse.
    "part_minimum_pension": "Part de bénéficiaires du minimum de pension (en %)",
}

SEXES = {"Femme": "F", "Homme": "H", "Ensemble": "ensemble"}


def classeur_le_plus_recent() -> tuple[int, str, bytes]:
    """Le classeur « tous les retraités » du millésime le plus élevé."""
    demande = urllib.request.Request(f"{BASE}/attachments", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=300) as reponse:
        pieces = json.loads(reponse.read()).get("attachments", [])
    candidats = []
    for piece in pieces:
        metas = piece.get("metas") or {}
        trouve = _TITRE.search(metas.get("title", ""))
        if trouve and metas.get("mimetype", "").endswith("spreadsheetml.sheet"):
            candidats.append((int(trouve.group(1)), metas["title"], metas["url"]))
    if not candidats:
        raise RuntimeError("aucun classeur « tous les retraités » joint au jeu")
    annee, titre, url = max(candidats)
    demande = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=600) as reponse:
        return annee, titre, reponse.read()


def lire_caracteristiques(contenu: bytes) -> dict[str, dict[str, float]]:
    """Les six indicateurs, par sexe, lus dans la colonne « Ensemble ».

    La feuille range le sexe en première colonne, le libellé en troisième, et
    la valeur tous quintiles confondus dans la colonne intitulée « Ensemble ».
    On la CHERCHE par son en-tête plutôt que par son rang : le classeur ajoute
    des quintiles d'un millésime à l'autre.
    """
    grille = feuilles(contenu)[FEUILLE]
    derniere_ligne = max(ligne for ligne, _ in grille)
    derniere_colonne = max(colonne for _, colonne in grille)
    colonne_ensemble = next(
        (colonne for colonne in range(derniere_colonne + 1)
         if str(grille.get((0, colonne), "")).strip() == "Ensemble"),
        None,
    )
    if colonne_ensemble is None:
        raise RuntimeError(f"feuille {FEUILLE!r} : colonne « Ensemble » absente")

    valeurs: dict[str, dict[str, float]] = {code: {} for code in INDICATEURS}
    for ligne in range(1, derniere_ligne + 1):
        sexe = SEXES.get(str(grille.get((ligne, 0), "")).strip())
        libelle = str(grille.get((ligne, 2), "")).strip()
        if sexe is None or not libelle:
            continue
        for code, debut in INDICATEURS.items():
            if not libelle.startswith(debut):
                continue
            valeur = grille.get((ligne, colonne_ensemble))
            if isinstance(valeur, (int, float)):
                valeurs[code][sexe] = float(valeur)
    manquants = [code for code, serie in valeurs.items() if len(serie) < 3]
    if manquants:
        raise RuntimeError(f"indicateurs illisibles : {', '.join(manquants)}")
    return valeurs


def main() -> int:
    try:
        annee, titre, contenu = classeur_le_plus_recent()
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1

    valeurs = lire_caracteristiques(contenu)
    charge = {
        "source": BASE,
        "fichier": titre,
        "millesime": annee,
        "mesure": "caractéristiques des retraités par sexe",
        "valeurs": valeurs,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"EIR {annee} : {len(valeurs)} indicateurs écrits dans {SORTIE}")
    for code, serie in valeurs.items():
        rendu = "  ".join(f"{sexe} {valeur:g}" for sexe, valeur in sorted(serie.items()))
        print(f"  {code:36} {rendu}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
