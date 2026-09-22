#!/usr/bin/env python3
"""Régénère, dans la prose, les tableaux que le modèle sait calculer.

    python scripts/construire_tableaux_md.py             # réécrit
    python scripts/construire_tableaux_md.py --verifier  # échoue s'il est périmé

Le problème qu'il traite
------------------------

Le site calcule le tableau des règles d'indexation à chaque rendu — c'est
``_cumuls_indexation`` de ``web/pages.py``, quatre millisecondes — et la prose
en porte deux copies, dans le README et dans la méthodologie, recopiées à la
main. La page l'a déjà payé une fois : ses neuf nombres y étaient écrits en dur
et l'un d'eux mentait de trois dixièmes de point. Les deux copies de la prose
sont restées dans cet état, à ceci près que personne ne les rend : elles ne se
périment pas bruyamment, elles se périment en silence.

Ce script les écrit entre deux repères, depuis le modèle, et
``tests/test_prose.py`` refuse une prose qui ne serait plus celle qu'il
produit. Le geste est celui de ``construire_regimes_md.py`` pour
``docs/regimes.md`` : ce qui se calcule ne se recopie pas.

Ce qu'il ne fait pas
--------------------

Il ne touche qu'aux lignes entre les repères. La phrase qui commente le
tableau — « une cotisation de 1950 ne conserve que 1,5 % de sa valeur
réelle » — reste de la prose, et c'est l'ancre de ``verifier_prose.py`` qui la
tient, avec la sonde ``tableau`` qui lit la cellule produite ici.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import replace
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle import Parametres  # noqa: E402
from retraite_notionnelle.moteur.indexation import Indexation  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402
from retraite_notionnelle.web.pages import (  # noqa: E402
    ANNEE_ARRIVEE_COMPAREE,
    ANNEE_VERSEMENT_COMPARE,
    REGLES_COMPAREES,
)

#: Les documents qui portent une copie du tableau, et l'intitulé de leur
#: première colonne — le README parle des « comptes », la méthodologie de la
#: « revalorisation cumulée ». Le reste est identique, et c'est bien le
#: problème : deux copies d'un même calcul.
DOCUMENTS = {
    "README.md": "Comptes 1941-2025",
    "docs/methodologie.md": f"Revalorisation cumulée "
                            f"{ANNEE_VERSEMENT_COMPARE + 1}-{ANNEE_ARRIVEE_COMPAREE}",
}

REPERE = "indexation"


def nombre(valeur: float, decimales: int = 1) -> str:
    """« 1 538,2 » : virgule décimale, espace ordinaire pour les milliers.

    C'est la typographie du dépôt, celle que `verifier_prose.py` sait relire.
    """
    rendu = f"{valeur:,.{decimales}f}".replace(",", " ").replace(".", ",")
    return rendu


def cumuls() -> dict[str, float]:
    """Le rendement cumulé de chaque règle, tel que le site le calcule."""
    simulateur = Simulateur(Parametres())
    rendus: dict[str, float] = {}
    for libelle, mode, lissage in REGLES_COMPAREES:
        parametres = replace(simulateur.parametres, mode_indexation=mode,
                             lissage_indexation=lissage)
        rendus[libelle] = Indexation(simulateur.macro, parametres).coefficient(
            ANNEE_VERSEMENT_COMPARE, ANNEE_ARRIVEE_COMPAREE)
    return rendus


def tableau(entete: str) -> str:
    """Le tableau markdown, prêt à poser entre les repères."""
    rendus = cumuls()
    prix = rendus["Indexation sur les prix"]
    lignes = [
        f"| Règle | {entete} | Prix | Pouvoir d'achat conservé |",
        "|---|---|---|---|",
    ]
    for libelle, _, _ in REGLES_COMPAREES:
        valeur = rendus[libelle]
        conserve = f"{nombre(valeur / prix * 100)} %"
        # La règle demandée par le programme est celle que la prose commente :
        # elle est mise en valeur des deux côtés, comme sur la page.
        if libelle == REGLES_COMPAREES[0][0]:
            libelle_rendu, conserve = libelle, f"**{conserve}**"
        else:
            libelle_rendu = libelle
        lignes.append(f"| {libelle_rendu} | ×{nombre(valeur)} | ×{nombre(prix)} "
                      f"| {conserve} |")
    return "\n".join(lignes)


def remplacer(texte: str, repere: str, contenu: str) -> str:
    debut, fin = f"<!-- {repere}:debut -->", f"<!-- {repere}:fin -->"
    if debut not in texte or fin not in texte:
        raise SystemExit(f"repères « {repere} » absents du document")
    avant = texte.split(debut)[0]
    apres = texte.split(fin, 1)[1]
    return f"{avant}{debut}\n{contenu}\n{fin}{apres}"


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="échoue si un document est périmé")
    arguments = analyseur.parse_args()

    perimes = []
    for document, entete in DOCUMENTS.items():
        chemin = RACINE / document
        texte = chemin.read_text(encoding="utf-8")
        voulu = remplacer(texte, REPERE, tableau(entete))
        if voulu == texte:
            continue
        if arguments.verifier:
            perimes.append(document)
            continue
        chemin.write_text(voulu, encoding="utf-8")
        print(f"{document} : tableau des règles d'indexation réécrit")

    if perimes:
        print("\n".join(
            f"{document} : le tableau des règles d'indexation a dérivé — "
            "lancer python scripts/construire_tableaux_md.py"
            for document in perimes), file=sys.stderr)
        return 1
    if arguments.verifier:
        print("les tableaux produits sont à jour")
    return 0


if __name__ == "__main__":
    sys.exit(main())
