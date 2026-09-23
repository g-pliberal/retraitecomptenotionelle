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

#: La seconde feuille lue. Elle croise le sexe et le fait de toucher un
#: minimum de pension, et c'est d'elle que viennent les EFFECTIFS de
#: bénéficiaires par sexe — ce que la première ne donne qu'en part.
FEUILLE_MINIMA = "Minima"

#: Les colonnes de la feuille des minima, sous le code que le dépôt leur donne
#: et le début de l'en-tête que le classeur leur donne.
COLONNES_MINIMA: dict[str, str] = {
    "beneficiaires_minimum_pension":
        "Retraités bénéficiaires d'un minimum de pension",
    "beneficiaires_minimum_regime_principal":
        "Retraités bénéficiaires d'un minimum de pension dans leur régime "
        "principal",
}

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

#: La troisième feuille lue : les retraités selon leur lieu de NAISSANCE et de
#: RÉSIDENCE. Elle sert à retirer de la distribution des pensions ceux qui
#: résident à l'étranger, que la garantie vieillesse — comme l'ASPA qu'elle
#: remplace, article L. 815-1 — ne sert pas. Le tableau de la distribution
#: les compte : « résidants en France ou à l'étranger », dit sa note.
FEUILLE_RESIDENCE = "Naissance-Résidence"

#: Les trois colonnes retenues, sous le code que le dépôt leur donne et
#: l'en-tête exact du classeur. Les autres croisent la naissance, qui ne
#: sert pas ici.
COLONNES_RESIDENCE: dict[str, str] = {
    "etranger": "Retraités résidents à l'étranger",
    "france": "Retraités résidents en France",
    "ensemble": "Ensemble",
}

#: Les indicateurs de la feuille : l'effectif, les deux pensions moyennes de
#: droit direct — sans et avec les majorations pour enfants —, et les onze
#: quantiles que le classeur publie de la seconde. Le début du libellé suffit,
#: à une précaution près : les quantiles de la pension TOTALE, réversion
#: comprise, commencent pareil jusqu'à « des pensions de » — c'est la suite
#: qui les sépare.
INDICATEURS_RESIDENCE: dict[str, str] = {
    "effectifs": "Effectifs (en milliers)",
    "pension_droit_direct": (
        "Montant moyen de la pension de retraite de droit direct brute"
    ),
    "pension_droit_direct_majorations": (
        "Montant moyen de la pension de droit direct (dont les majorations pour "
        "enfants) brute"
    ),
    "d1": "Premier décile des pensions de droit direct",
    "d2": "Deuxième décile des pensions de droit direct",
    "q1": "Premier quartile des pensions de droit direct",
    "d3": "Troisième décile des pensions de droit direct",
    "d4": "Quatrième décile des pensions de droit direct",
    "mediane": "Médiane des pensions de droit direct",
    "d6": "Sixième décile des pensions de droit direct",
    "d7": "Septième décile des pensions de droit direct",
    "q3": "Troisième quartile des pensions de droit direct",
    "d8": "Huitième décile des pensions de droit direct",
    "d9": "Neuvième décile des pensions de droit direct",
}


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


def lire_beneficiaires(contenu: bytes) -> dict[str, dict[str, float]]:
    """Les effectifs de bénéficiaires d'un minimum de pension, par sexe.

    La feuille des minima croise le sexe et le statut au regard du minimum ;
    la ligne des effectifs porte, colonne par colonne, combien de retraités
    chaque case contient. Les deux colonnes retenues s'emboîtent — le régime
    principal est une part de l'ensemble —, et leur en-tête commence pareil :
    c'est la PLUS LONGUE qui gagne, sans quoi la seconde prendrait la première.
    """
    grille = feuilles(contenu)[FEUILLE_MINIMA]
    derniere_colonne = max(colonne for _, colonne in grille)
    colonnes: dict[str, int] = {}
    for code, debut in sorted(COLONNES_MINIMA.items(),
                              key=lambda paire: -len(paire[1])):
        for colonne in range(derniere_colonne + 1):
            entete = str(grille.get((0, colonne), "")).strip()
            if entete.startswith(debut) and colonne not in colonnes.values():
                colonnes[code] = colonne
                break
    manquantes = set(COLONNES_MINIMA) - set(colonnes)
    if manquantes:
        raise RuntimeError(
            f"feuille {FEUILLE_MINIMA!r} : colonnes absentes — "
            f"{', '.join(sorted(manquantes))}"
        )

    derniere_ligne = max(ligne for ligne, _ in grille)
    valeurs: dict[str, dict[str, float]] = {code: {} for code in COLONNES_MINIMA}
    for ligne in range(1, derniere_ligne + 1):
        sexe = SEXES.get(str(grille.get((ligne, 0), "")).strip())
        libelle = str(grille.get((ligne, 2), "")).strip()
        if sexe is None or not libelle.startswith("Effectifs (en milliers)"):
            continue
        for code, colonne in colonnes.items():
            valeur = grille.get((ligne, colonne))
            if isinstance(valeur, (int, float)):
                valeurs[code][sexe] = float(valeur)
    manquants = [code for code, serie in valeurs.items() if len(serie) < 3]
    if manquants:
        raise RuntimeError(f"effectifs illisibles : {', '.join(manquants)}")
    return valeurs


def lire_residence(contenu: bytes) -> dict[str, dict[str, dict[str, float]]]:
    """Les indicateurs de la feuille de résidence : colonne, indicateur, sexe.

    Les colonnes sont CHERCHÉES par leur en-tête, et la plus longue gagne pour
    la même raison que dans la feuille des minima. Un quantile de la pension
    de droit direct se reconnaît au début de son libellé, pris juste avant la
    parenthèse que le classeur écrit différemment d'une ligne à l'autre.
    """
    grille = feuilles(contenu)[FEUILLE_RESIDENCE]
    derniere_colonne = max(colonne for _, colonne in grille)
    derniere_ligne = max(ligne for ligne, _ in grille)
    colonnes: dict[str, int] = {}
    for code, entete in COLONNES_RESIDENCE.items():
        for colonne in range(derniere_colonne + 1):
            if str(grille.get((0, colonne), "")).strip() == entete:
                colonnes[code] = colonne
                break
    manquantes = set(COLONNES_RESIDENCE) - set(colonnes)
    if manquantes:
        raise RuntimeError(
            f"feuille {FEUILLE_RESIDENCE!r} : colonnes absentes — "
            f"{', '.join(sorted(manquantes))}"
        )

    valeurs: dict[str, dict[str, dict[str, float]]] = {
        residence: {code: {} for code in INDICATEURS_RESIDENCE}
        for residence in COLONNES_RESIDENCE
    }
    for ligne in range(1, derniere_ligne + 1):
        sexe = SEXES.get(str(grille.get((ligne, 0), "")).strip())
        libelle = " ".join(str(grille.get((ligne, 2), "")).split())
        if sexe is None or not libelle:
            continue
        for code, debut in INDICATEURS_RESIDENCE.items():
            if not libelle.startswith(" ".join(debut.split())):
                continue
            for residence, colonne in colonnes.items():
                valeur = grille.get((ligne, colonne))
                # Un indicateur figure deux fois — en brut, puis en net pour
                # les pensions : la PREMIÈRE occurrence est la brute.
                if (isinstance(valeur, (int, float))
                        and sexe not in valeurs[residence][code]):
                    valeurs[residence][code][sexe] = float(valeur)
    manquants = [f"{residence}/{code}" for residence, serie in valeurs.items()
                 for code, parsexe in serie.items() if len(parsexe) < 3]
    if manquants:
        raise RuntimeError(f"résidence illisible : {', '.join(manquants)}")
    return valeurs


def main() -> int:
    try:
        annee, titre, contenu = classeur_le_plus_recent()
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1

    valeurs = lire_caracteristiques(contenu)
    valeurs.update(lire_beneficiaires(contenu))
    charge = {
        "source": BASE,
        "fichier": titre,
        "millesime": annee,
        "mesure": "caractéristiques des retraités par sexe",
        "valeurs": valeurs,
        "residence": lire_residence(contenu),
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
