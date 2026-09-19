#!/usr/bin/env python3
"""Les comptes et les effectifs de CHAQUE régime, chez le COR, jusqu'en 2070.

    python scripts/fetch/cor_regimes.py

CE QU'ON VIENT CHERCHER, ET POURQUOI ICI
-----------------------------------------
``cor_comptes_retraite.py`` va chercher le compte CONSOLIDÉ du système de
retraite. Celui-ci va chercher le compte de chaque RÉGIME, ce qui est une autre
source et un autre fichier : les « Compléments du rapport annuel : projections
détaillées par régime », que le COR publie à côté de son rapport. Vingt-deux
fiches, une par régime, et surtout UN classeur qui porte leurs données —
vingt-quatre feuilles, une par régime.

C'est la seule source publique qui donne, à la même maille et sur la même
convention, pour treize caisses des cas types — l'Ircantec et le RCI comprises,
que la CCSS ne couvre pas :

* les EFFECTIFS de retraités de droit direct et de cotisants, ventilés
  femmes / hommes / ensemble ;
* les MASSES : prestations, pensions de droit direct et de droit dérivé,
  dépenses totales, en milliards d'euros constants et en part de PIB ;
* les RESSOURCES totales et techniques, le solde technique et le solde élargi,
  les réserves ;
* l'âge moyen de départ, le rapport démographique et la pension relative.

De 2010 à 2070 : l'observé et le projeté dans le même tableau, ce qu'aucune
autre source ne fait par caisse. Les régimes que la réforme de 2023 a fermés
s'y éteignent — la CNIEG tombe de 136 287 cotisants en 2023 à 51 en 2070, la
SNCF à zéro —, là où reconduire des effectifs de retraités ferait l'inverse.

LE MILLÉSIME, QUI EST LA RÉSERVE PRINCIPALE
--------------------------------------------
**Il n'existe qu'une version de ce classeur, celle du rapport de juin 2024.**
Son sommaire l'écrit, ses métadonnées la datent du 10 juillet 2024, révisée le
10 février 2025. L'en-tête ``Last-Modified`` du serveur affiche avril 2026 et
ne veut rien dire : c'est une remise en ligne. Les rapports de 2025 et de 2026
n'ont pas reconduit ces compléments — vérifié le 19 septembre 2026, index des
fiches, pages des deux rapports et sondage des chemins.

Les valeurs entrent donc au niveau ``haute``, jamais ``certifiee``, et leur
millésime est porté dans le fichier produit : les mélanger aux figures 1.13 et
2.7 du rapport 2026, qui portent les hypothèses COR 2026, coudrait deux
exercices de projection.

TROIS PIÈGES, MESURÉS ET TRAITÉS ICI
-------------------------------------
1. **L'unité ment sur deux feuilles.** Les en-têtes annoncent « en millions »
   partout, mais les feuilles CRPCEN et CRPNPAC portent des UNITÉS : 60 378
   cotisants au CRPCEN en 2023, à rapprocher des 60 303 de la Cnav. On ne
   corrige pas en silence — l'en-tête lu est recopié tel quel dans la sortie,
   et c'est à l'appelant de voir « en millions » devant 60 378.
2. **L'année de départ varie d'une feuille à l'autre** : 2010 le plus souvent,
   2015 pour la FPE, 2019 pour le RCI, 2023 pour la CNRACL et la CNBF, 2024
   pour le FSPOEIE. On ne complète pas : une absence est une absence.
3. **La FPE est d'un seul tenant**, civils et militaires confondus. Le partage
   ne se prend pas ici, mais au Jaune budgétaire « Pensions ».

CE QUE LE FICHIER PRODUIT CONTIENT
-----------------------------------
Une table longue : régime, bloc, série, année, valeur — 52 049 valeurs, 23
régimes, 61 années, 36 blocs. Le bloc est l'en-tête qui porte les années, la
série est la ligne sous lui (``Ensemble``, ``Femmes``, ``Hommes``, ``Scénario
de référence``…). Rien n'est agrégé ni converti : c'est le classeur, relu.
"""

from __future__ import annotations

import json
import re
import ssl
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lecture_xlsx import feuilles  # noqa: E402

RACINE_SITE = "https://www.cor-retraites.fr"
#: La page qui porte les compléments, et le classeur qu'elle publie. Le chemin
#: est figé parce que le jeu l'est : un seul millésime, celui de juin 2024.
PAGE_COMPLEMENTS = (
    RACINE_SITE + "/fiches/complements-rapport-annuel-2024-"
    "projections-detaillees-par-regime"
)
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/cor_regimes.json")

#: Le classeur de données, sur la page des compléments.
LIEN_CLASSEUR = re.compile(
    r'href="(/sites/default/files/[^"]*[Rr]%C3%A9gimes[^"]*\.xlsx)"'
)
#: Une ligne d'en-tête porte un libellé puis une file d'années croissantes.
#: Les bornes sont larges à dessein : le classeur ne va que de 2010 à 2070,
#: mais un millésime ultérieur pourrait déborder.
ANNEE_MIN, ANNEE_MAX = 1990, 2100
#: Quatre années suffisent à reconnaître un en-tête. Le seuil est bas parce que
#: le bloc « structure de financement » n'en porte que SIX — 2010, 2023, 2030,
#: 2040, 2050, 2070 — là où tous les autres en portent soixante et une. Le
#: reconnaître demandait de descendre sous le seuil qui lui allait.
ANNEES_MINIMUM = 4
#: Une ligne de valeurs doit remplir la moitié des colonnes de son en-tête,
#: sans quoi c'est une note ou un renvoi.
PART_MINIMALE = 0.5


def _contexte() -> ssl.SSLContext:
    return ssl.create_default_context()


def _recuperer(url: str) -> bytes:
    requete = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(requete, context=_contexte(), timeout=120) as flux:
        return flux.read()


def adresse_classeur() -> str:
    """Le classeur est lu sur la page, jamais deviné : son nom porte un ``_V2``."""
    page = _recuperer(PAGE_COMPLEMENTS).decode("utf-8", "replace")
    liens = LIEN_CLASSEUR.findall(page)
    if not liens:
        raise LookupError(
            "aucun classeur par régime sur la page des compléments du COR — "
            "le millésime a peut-être changé, relire le docstring"
        )
    return RACINE_SITE + liens[0]


def _est_file_dannees(nombres: dict[int, float]) -> bool:
    """Reconnaît la ligne d'en-tête d'un bloc : des années, et rien d'autre.

    Le test est volontairement strict, parce que le seuil est descendu à quatre
    valeurs : il faut des ENTIERS, tous dans la fenêtre, tous distincts et
    STRICTEMENT CROISSANTS de gauche à droite. Aucune série du classeur ne
    ressemble à ça — ni les effectifs, ni les masses, ni les âges de départ, qui
    tournent autour de soixante-deux.
    """
    if len(nombres) < ANNEES_MINIMUM:
        return False
    suite = [nombres[k] for k in sorted(nombres)]
    if not all(float(v).is_integer() and ANNEE_MIN < v < ANNEE_MAX for v in suite):
        return False
    return all(a < b for a, b in zip(suite, suite[1:]))


def lire_feuille(cellules: dict) -> list[tuple[str, str, int, float]]:
    """Les séries d'une feuille de régime, sous forme (bloc, série, année, valeur).

    Une feuille alterne des en-têtes — un libellé puis soixante et une années —
    et des lignes de valeurs sous eux. On suit l'en-tête courant ; une ligne qui
    ne porte pas assez de nombres est un titre ou une note, et se saute.
    """
    lignes: dict[int, dict[int, object]] = {}
    for (rang, colonne), valeur in cellules.items():
        lignes.setdefault(rang, {})[colonne] = valeur

    sortie: list[tuple[str, str, int, float]] = []
    bloc: str | None = None
    annees: dict[int, int] = {}
    for rang in sorted(lignes):
        cellule = lignes[rang]
        textes = [v for v in cellule.values() if isinstance(v, str)]
        nombres = {k: v for k, v in cellule.items() if isinstance(v, (int, float))}
        libelle = textes[0].strip() if textes else ""
        if libelle and _est_file_dannees(nombres):
            bloc = libelle
            annees = {k: int(v) for k, v in nombres.items()}
            continue
        if annees and libelle and len(nombres) >= max(3, PART_MINIMALE * len(annees)):
            for colonne, annee in annees.items():
                if colonne in nombres:
                    sortie.append((bloc or "", libelle, annee, float(nombres[colonne])))
    return sortie


def lire_classeur(octets: bytes) -> list[dict]:
    valeurs: list[dict] = []
    for regime, cellules in feuilles(octets).items():
        if regime == "Sommaire":
            continue
        for bloc, serie, annee, valeur in lire_feuille(cellules):
            valeurs.append(
                {
                    "regime": regime,
                    "bloc": bloc,
                    "serie": serie,
                    "annee": annee,
                    "valeur": valeur,
                }
            )
    return valeurs


def main() -> int:
    try:
        adresse = adresse_classeur()
        octets = _recuperer(adresse)
    except (urllib.error.HTTPError, urllib.error.URLError, LookupError) as erreur:
        print(f"échec : {erreur}", file=sys.stderr)
        return 1

    valeurs = lire_classeur(octets)
    if not valeurs:
        print("échec : le classeur n'a livré aucune série", file=sys.stderr)
        return 1

    regimes = sorted({v["regime"] for v in valeurs})
    annees = sorted({v["annee"] for v in valeurs})
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(
            {
                "source": adresse,
                "millesime": "Complément du rapport annuel du COR — juin 2024",
                "fiabilite": "haute",
                "valeurs": valeurs,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    blocs = sorted({v["bloc"] for v in valeurs})
    print(
        f"{len(valeurs)} valeurs — {len(regimes)} régimes, "
        f"{annees[0]}-{annees[-1]}, {len(blocs)} blocs → {SORTIE}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
