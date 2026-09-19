#!/usr/bin/env python3
"""Récupération des effectifs de retraités par caisse, auprès de la DREES.

    python scripts/fetch/drees_eacr.py

L'enquête annuelle auprès des caisses de retraite (EACR) est le dénombrement
exhaustif des retraités, caisse par caisse et année par année. La DREES en
diffuse le résultat en open data, dans un classeur dont la feuille
``A-Cadrage`` porte le tableau de cadrage : pour chaque couple (année, caisse),
l'effectif des bénéficiaires et le montant moyen de leur pension.

C'est la source qui manquait pour PONDÉRER les cas types. La page « Coût » les
a longtemps pesés à égalité faute de mieux, ce qui donnait à l'agent de conduite
le même poids qu'au salarié au salaire moyen ; ces effectifs disent ce que
chaque régime pèse réellement.

CE QU'ON RETIENT, ET POURQUOI
-----------------------------
Le classeur croise cinq dimensions. On ne garde qu'une cellule par couple :

* ``Champ = ddir`` — les bénéficiaires d'un droit DIRECT, c'est-à-dire d'une
  pension acquise par leur propre carrière. Les droits dérivés (réversion) sont
  hors du modèle par construction : il décrit une carrière, pas un ménage ;
* ``Sexe``, ``Resid``, ``Liq``, ``StatutSNCF`` à ``Ensemble`` — aucune
  ventilation, le total de la caisse.

UN MÊME COUPLE, PLUSIEURS MILLÉSIMES
-------------------------------------
La DREES empile les campagnes : l'effectif de la MSA en 2014 est publié par
l'EACR 2014 puis corrigé par l'EACR 2015, et les deux lignes coexistent dans le
classeur. On retient la plus RÉCENTE, au millésime lu dans le libellé de la
source — c'est la valeur corrigée. Les désaccords sont minces : nuls pour la
moitié des couples, et 2,5 % au pire.

Le fichier produit, ``data/brut/drees_eacr.json``, est le document source : il
n'est pas lu par le modèle, seulement par ``scripts/verifier_donnees.py``, qui
en écrit ``data/reference/regimes/effectifs_retraites.csv``.
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
    "/datasets/donnes_eacr"
)
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/drees_eacr.json")

#: Feuille du classeur qui porte le tableau de cadrage.
FEUILLE = "A-Cadrage"

#: Champ des bénéficiaires d'un droit DIRECT, et colonne qui porte leur nombre.
CHAMP = "ddir"

#: Champ des bénéficiaires d'un droit DÉRIVÉ — la réversion —, et colonne qui
#: porte le montant mensuel moyen de ce droit-là.
#:
#: ``ddert`` compte TOUS les bénéficiaires d'un droit dérivé, qu'ils aient ou
#: non une pension de droit direct par ailleurs ; ``dders`` ne compte que ceux
#: qui n'ont que cela. C'est ``ddert`` qu'il faut pour une masse, puisque la
#: caisse verse la réversion aux uns comme aux autres.
#:
#: Et c'est ``m2`` qu'il faut, non ``mont`` : la seconde colonne porte la
#: pension TOTALE du bénéficiaire, droit direct compris, la première la seule
#: part dérivée. Les confondre doublerait la masse. Le classeur le vérifie
#: lui-même : la moyenne pondérée des ``m2`` de ``dders`` et de ``cumd`` vaut
#: exactement le ``m2`` de ``ddert``.
CHAMP_DERIVE = "ddert"
COLONNE_DERIVE = "m2"

#: Dimensions qu'on ne ventile pas — on veut le total de la caisse.
TOTALISEES = ("Sexe", "Resid", "Liq", "StatutSNCF")

_MILLESIME = re.compile(r"(\d{4})")


def _pieces_jointes() -> list[dict]:
    demande = urllib.request.Request(f"{BASE}/attachments", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=120) as reponse:
        return json.loads(reponse.read()).get("attachments", [])


def classeur_de_cadrage() -> tuple[str, bytes]:
    """Télécharge la partie du classeur qui porte ``A-Cadrage``.

    La DREES diffuse l'EACR en deux classeurs, dont seul le premier porte le
    cadrage, et renomme la pièce jointe à chaque version. On la reconnaît donc
    à son extension et à son rang, non à son nom.
    """
    pieces = [
        piece["metas"] for piece in _pieces_jointes()
        if (piece.get("metas") or {}).get("mimetype", "").endswith("spreadsheetml.sheet")
    ]
    if not pieces:
        raise RuntimeError("aucun classeur joint au jeu EACR de la DREES")
    for piece in pieces:
        demande = urllib.request.Request(piece["url"], headers=ENTETES)
        with urllib.request.urlopen(demande, timeout=600) as reponse:
            contenu = reponse.read()
        if FEUILLE in feuilles(contenu):
            return piece["title"], contenu
    raise RuntimeError(f"feuille {FEUILLE!r} absente des classeurs EACR")


def lire_cadrage(contenu: bytes, champ: str = CHAMP,
                 mesure: str = "effectifs",
                 ) -> tuple[dict[str, str], dict[str, dict[str, float]]]:
    """Une grandeur du cadrage, par caisse et par année, millésime le plus récent.

    Rend deux tables : le libellé de chaque caisse, et la grandeur demandée
    indexée par année. Les caisses sont désignées par leur CODE et non par leur
    nom : la DREES rebaptise ses caisses — « SSI complémentaire » est devenue
    « RCI complémentaire » sans changer de code — et une série ne doit pas se
    couper parce qu'un régime a changé d'enseigne.

    ``champ`` et ``mesure`` disent quelle cellule lire : les effectifs de droit
    direct par défaut, le montant mensuel moyen du droit dérivé pour la
    réversion. Les deux passent par le même filtrage et la même règle de
    millésime, ce qui est la raison d'être de ce paramètre : deux lectures
    séparées auraient divergé à la première correction de campagne.
    """
    grille = feuilles(contenu)[FEUILLE]
    derniere_ligne = max(ligne for ligne, _ in grille)
    entete = {}
    for ligne, colonne in grille:
        if ligne == 0:
            entete[grille[(0, colonne)]] = colonne

    libelles: dict[str, str] = {}
    # (code, année) -> (millésime de la campagne, libellé de la source, effectif)
    retenues: dict[tuple[str, int], tuple[int, str, float]] = {}
    for ligne in range(1, derniere_ligne + 1):
        cellule = {nom: grille.get((ligne, colonne)) for nom, colonne in entete.items()}
        if cellule.get("Champ") != champ:
            continue
        if any(cellule.get(nom) != "Ensemble" for nom in TOTALISEES):
            continue
        effectif = cellule.get(mesure)
        if not isinstance(effectif, float) or effectif <= 0:
            continue
        code, annee = str(cellule["CC"]), int(cellule["Année"])
        source = str(cellule.get("Source") or "")
        trouve = _MILLESIME.search(source)
        millesime = int(trouve.group(1)) if trouve else 0
        rang = (millesime, source, effectif)
        if rang[:2] > retenues.get((code, annee), (-1, ""))[:2]:
            retenues[(code, annee)] = rang
        libelles[code] = str(cellule["Caisse"])

    effectifs: dict[str, dict[str, float]] = {}
    for (code, annee), (_, _, effectif) in sorted(retenues.items()):
        effectifs.setdefault(code, {})[str(annee)] = effectif
    return libelles, effectifs


def main() -> int:
    try:
        nom, contenu = classeur_de_cadrage()
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1

    libelles, effectifs = lire_cadrage(contenu)
    # La réversion se lit dans le même tableau, sur deux cellules : le NOMBRE de
    # bénéficiaires d'un droit dérivé, et le MONTANT MENSUEL MOYEN de ce
    # droit-là. Leur produit, sur douze mois, est la masse que la caisse verse à
    # ce titre — la seule grandeur que le modèle ne saura jamais calculer, faute
    # de décrire des ménages.
    derives_libelles, derives_effectifs = lire_cadrage(
        contenu, CHAMP_DERIVE, "effectifs")
    _, derives_montants = lire_cadrage(contenu, CHAMP_DERIVE, COLONNE_DERIVE)
    libelles = {**derives_libelles, **libelles}
    derives = {
        code: {
            annee: [effectif, derives_montants[code][annee]]
            for annee, effectif in sorted(serie.items())
            if annee in derives_montants.get(code, {})
        }
        for code, serie in sorted(derives_effectifs.items())
    }
    charge = {
        "source": BASE,
        "fichier": nom,
        "champ": CHAMP,
        "unite": "personnes",
        "caisses": dict(sorted(libelles.items())),
        "effectifs": {code: effectifs[code] for code in sorted(effectifs)},
        "droits_derives": {
            "champ": CHAMP_DERIVE,
            "colonne": COLONNE_DERIVE,
            "unite": "bénéficiaires, puis euros par mois",
            "series": {code: serie for code, serie in derives.items() if serie},
        },
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    annees = sorted(int(a) for serie in effectifs.values() for a in serie)
    print(f"{len(effectifs)} caisses écrites dans {SORTIE}")
    print(f"Effectifs de droit direct : {min(annees)}-{max(annees)}")
    tous = charge["droits_derives"]["series"].get("0000", {})
    if tous:
        derniere = max(tous)
        beneficiaires, montant = tous[derniere]
        print(f"Droits dérivés, tous régimes en {derniere} : "
              f"{beneficiaires / 1e6:.3f} M bénéficiaires, {montant:.1f} €/mois, "
              f"soit {beneficiaires * montant * 12 / 1e9:.1f} Md€")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
