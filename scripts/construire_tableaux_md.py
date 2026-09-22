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

#: Le second tableau du §1 du README : ce que la correction de la ligne de
#: référence déplace, génération par génération. Les cinq générations sont
#: celles que la prose commente — deux carrières d'avant 1987, une à cheval,
#: deux d'après —, et la carrière est celle qu'elle annonce.
GENERATIONS = (1920, 1930, 1945, 1958, 1990)
AGE_DEBUT_GENERATIONS = 20
AGE_LIQUIDATION_GENERATIONS = 62
REPERE_GENERATIONS = "generations"


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


def ecarts_par_generation() -> list[tuple[int, float, float]]:
    """L'écart du scénario rétroactif au scénario 1, sous les deux règles.

    La ligne de référence « Prix » est celle que le dépôt a longtemps donnée
    pour la règle qui neutralise l'indexation ; la ligne corrigée est la
    revalorisation réellement portée au compte. Ce que leur différence
    déplace se lit génération par génération, et change de signe pour les
    carrières entièrement postérieures à 1987.
    """
    from retraite_notionnelle.config import ModeIndexation

    simulateurs = {}
    for mode in (ModeIndexation.PRIX,
                 ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE):
        simulateurs[mode] = Simulateur(
            replace(Parametres(), mode_indexation=mode))

    rendus = []
    for generation in GENERATIONS:
        ecarts = []
        for mode, simulateur in simulateurs.items():
            carriere = simulateur.carriere_simple(
                annee_naissance=generation, sexe="H",
                affiliation="salarie_prive_non_cadre",
                age_debut=AGE_DEBUT_GENERATIONS,
                age_liquidation=AGE_LIQUIDATION_GENERATIONS)
            resultat = simulateur.simuler(carriere)
            ecarts.append((resultat.notionnel_retroactif.pension_annuelle
                           / resultat.actuel.pension_annuelle - 1) * 100)
        rendus.append((generation, ecarts[0], ecarts[1]))
    return rendus


def tableau_generations() -> str:
    """Le tableau des cinq générations, prêt à poser entre les repères."""
    rendus = ecarts_par_generation()
    differences = [corrige - prix for _, prix, corrige in rendus]
    haut, bas = max(differences), min(differences)
    lignes = [
        "| Génération | Carrière | Ligne de référence « Prix » | Ligne corrigée | Écart |",
        "|---|---|---|---|---|",
    ]
    for (generation, prix, corrige), difference in zip(rendus, differences):
        debut = generation + AGE_DEBUT_GENERATIONS
        fin = generation + AGE_LIQUIDATION_GENERATIONS
        # Un écart nul n'a pas de signe : « -0,0 pt » se lit comme une erreur
        # de calcul, quand c'est la mesure qui dit « rien ne bouge ».
        arrondi = round(difference, 1)
        ecrit = (f"{arrondi:+.1f}" if arrondi else "0,0").replace(".", ",")
        ecrit = ecrit if ecrit.endswith("pt") else f"{ecrit} pt"
        # Les deux extrêmes portent le propos : le plus grand écart, et celui
        # qui change de signe. Les mettre en valeur est le geste de la page.
        if difference in (haut, bas):
            ecrit = f"**{ecrit}**"
        lignes.append(
            f"| {generation} | {debut}-{fin} | {nombre(prix)} % "
            f"| {nombre(corrige)} % | {ecrit} |")
    return "\n".join(lignes)


#: L'exemple du §3 du README : la sortie de ``Comparaison.tableau()`` pour la
#: carrière que le bloc de code juste au-dessus construit. Elle était collée à
#: la main, et elle avait vieilli — la rente du pilier annonçait 1 569 € quand
#: le modèle en sert 1 515 — sans que le bloc de code, que le contrôle de la
#: prose ne lit pas, puisse le dire.
REPERE_EXEMPLE = "exemple_fonctionnaire"
TITRE_EXEMPLE = "Fonctionnaire d'État née en 1975, 20 % de primes, partie à 64 ans"


def sortie_exemple() -> str:
    """Le tableau de l'exemple et la ligne de qui verse quoi, sans le reste."""
    sys.path.insert(0, str(RACINE / "scripts"))
    from mesures_prose import _comparaison_de

    lignes = _comparaison_de({"exemple": "fonctionnaire"}).tableau().split("\n")
    debut = next(i for i, l in enumerate(lignes) if l.startswith("Scénario"))
    fin = next(i for i, l in enumerate(lignes) if l.lstrip().startswith("= total"))
    verse = next(i for i, l in enumerate(lignes) if l.startswith("Qui verse"))
    corps = lignes[debut:fin + 1] + [""] + lignes[verse:verse + 5]
    return "\n".join(["```", TITRE_EXEMPLE, "", *(l.rstrip() for l in corps), "```"])


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
        chemin.write_text(voulu, encoding="utf-8", newline="\n")
        print(f"{document} : tableau des règles d'indexation réécrit")

    # Le second tableau ne vit que dans le README : il commente la correction
    # de la ligne de référence, que la méthodologie ne reprend pas. La sortie
    # de l'exemple du §3 non plus.
    chemin = RACINE / "README.md"
    for repere, fabrique, quoi in (
            (REPERE_GENERATIONS, tableau_generations, "tableau des générations"),
            (REPERE_EXEMPLE, sortie_exemple, "sortie de l'exemple du §3")):
        texte = chemin.read_text(encoding="utf-8")
        voulu = remplacer(texte, repere, fabrique())
        if voulu == texte:
            continue
        if arguments.verifier:
            perimes.append(f"README.md ({quoi})")
        else:
            chemin.write_text(voulu, encoding="utf-8", newline="\n")
            print(f"README.md : {quoi} réécrit")

    if perimes:
        print("\n".join(
            f"{document} : un bloc produit a dérivé — "
            "lancer python scripts/construire_tableaux_md.py"
            for document in perimes), file=sys.stderr)
        return 1
    if arguments.verifier:
        print("les tableaux produits sont à jour")
    return 0


if __name__ == "__main__":
    sys.exit(main())
