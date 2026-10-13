#!/usr/bin/env python3
"""Mortalité projetée de l'INSEE : quotients par âge et espérances publiées.

    python scripts/fetch/insee_projections_mortalite.py

Le dépôt portait, pour les années projetées, six valeurs saisies à la main aux
années rondes 2030, 2040, 2050, 2060, 2070 — plus 2080, qui dépassait l'horizon
de la source dont elle se réclamait — et les gelait au-delà. Trois défauts d'un
coup : un millésime périmé, une extrapolation non déclarée, et une espérance de
vie qui cessait de progresser vingt ans avant la fin de la projection.

L'INSEE publie mieux, et le publie en clair : ses **projections de population
2026** livrent les quotients de mortalité par âge et par année, de 0 à 120 ans
et de 2023 à 2125, pour les trois hypothèses d'espérance de vie, et, sous chaque
table, les espérances de vie à la naissance, à 60 et à 65 ans qu'elle implique.
On reprend la centrale : ses QUOTIENTS, que le modèle lit âge par âge depuis le
7 octobre 2026 au lieu de sa loi de Gompertz-Makeham (action 138, étape 7), et
ses espérances, telles que l'INSEE les publie. Et, depuis le 13 octobre 2026,
les hypothèses basse et haute, qui s'en écartent de trois ans d'espérance de vie
à la naissance en 2070 : leurs quotients, que le diviseur lit sous
``Parametres.hypothese_esperance_vie``, et leurs espérances publiées, contre
lesquelles leur table se contrôle comme la centrale.

LES ESPÉRANCES SONT PUBLIÉES, ET N'ONT PAS À ÊTRE DÉRIVÉES
----------------------------------------------------------
Ce script les DÉRIVAIT des quotients jusqu'au 7 octobre 2026, au motif que
« l'INSEE ne publie pas e65, ici pas plus qu'ailleurs ». C'était faux pour ce
classeur : chaque feuille porte, sous sa table, une ligne « Espérance de vie à
65 ans », année par année. La dérivation sommait les survies d'une table
indexée par âge atteint, ce qui vaut à la naissance mais pas à 60 ou 65 ans :
elle sous-estimait e60 et e65 jusqu'à 0,09 et 0,12 an en 2026, chez les
hommes, l'écart s'effaçant vers 2125. L'INSEE est le producteur, et sa valeur
prime.

LA CONVENTION D'ÂGE N'EST PAS CELLE DES TABLES DU MOMENT, ET LES CONTRÔLES LE DISENT
-------------------------------------------------------------------------------------
Ce classeur indexe ses quotients par **âge atteint dans l'année** : le quotient
de l'âge x en t est la probabilité, pour qui atteint x pendant l'année t, d'y
mourir avant le 1er janvier suivant. Il couvre un parallélogramme du diagramme
de Lexis, de l'âge exact x − 1 à l'âge exact x + 1, centré sur x. Le modèle lit
des carrés — de l'âge exact x à x + 1, pendant l'année t, sous une force de
mortalité constante (``survie_annuelle``) — centrés sur x + 0,5. Le carré se
tire des deux parallélogrammes qui l'encadrent, par la moyenne géométrique de
leurs survies :

    1 − q(x) = √[(1 − q_atteint(x)) · (1 − q_atteint(x + 1))]

et le dernier âge, 120 ans, garde son quotient.

Deux contrôles l'autorisent, reconduits à chaque exécution ; le script échoue
si l'un casse :

* la convention de lecture : l'INSEE publie l'espérance de vie à la naissance
  que son scénario central implique en 2070, **89,5 ans pour les femmes et
  86,7 ans pour les hommes** (Insee Première n° 2108). La somme des survies du
  classeur, sans le demi-an usuel, rend 89,50 et 86,71 ; avec demi-an, 90,00 et
  87,21. Le demi-an est dans l'indexation par âge atteint. La même publication
  écarte les hypothèses basse et haute de « ± 3,0 ans » de la centrale en 2070 :
  86,5 et 92,5 ans pour les femmes, 83,7 et 89,7 pour les hommes, que la
  somme des survies de leurs feuilles rend à 0,02 an près ;
* la conversion : la table convertie, sommée comme le modèle la somme —
  trapèzes d'âge exact en âge exact —, retrouve à moins de 0,02 an les
  espérances à 60 et 65 ans que l'INSEE publie, chaque année de 2026 à 2125,
  sous les hypothèses centrale et basse, à moins de 0,04 an sous la haute.
  La tolérance est de 0,05 an. À la naissance, l'écart passe le dixième, et il
  est attendu : les décès de la première année se concentrent dans ses
  premières semaines, ce que la moyenne de deux parallélogrammes ignore. Aucun
  calcul du modèle ne part de la naissance.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lecture_xlsx import feuilles  # noqa: E402
from source_locale import lire_ou_telecharger, option_fichier  # noqa: E402

URL = ("https://www.insee.fr/fr/statistiques/fichier/8990899/hyp_mortalite.xlsx")

SORTIE = Path("data/brut/insee_projections_mortalite.json")
SORTIE_QUOTIENTS = Path("data/brut/insee_quotients_projetes.json")
#: Les hypothèses basse et haute, sous des clés que l'hypothèse ouvre
#: (``basse|2070|F|e65``, ``haute|2070|F|65``).
SORTIE_VARIANTES = Path("data/brut/insee_projections_mortalite_variantes.json")
SORTIE_QUOTIENTS_VARIANTES = Path("data/brut/insee_quotients_projetes_variantes.json")

PUBLICATION = ("INSEE, projections de population 2026 pour la France — "
               "hypothèses de mortalité jusqu'en 2125, hypothèse centrale "
               "(Insee Résultats, 2026)")
PUBLICATION_VARIANTES = ("INSEE, projections de population 2026 pour la France — "
                         "hypothèses de mortalité jusqu'en 2125, hypothèses "
                         "d'espérance de vie basse et haute (Insee Résultats, 2026)")

#: Hypothèse d'espérance de vie -> feuille du classeur -> code de sexe du
#: dépôt. Le classeur en porte huit : hypothèses centrale, basse, haute et
#: mortalité constante, par sexe. On reprend les trois premières : la
#: centrale, dont le COR et le dépôt se réclament, et les deux qui
#: l'encadrent, que le diviseur lit en variante depuis le 13 octobre 2026
#: (action 138, étape 7). La mortalité constante, « hypothèse de travail »
#: selon son titre, n'est pas une projection.
HYPOTHESES = {
    "centrale": {"centralF": "F", "centralH": "H"},
    "basse": {"basF": "F", "basH": "H"},
    "haute": {"hautF": "F", "hautH": "H"},
}

#: Les feuilles de l'hypothèse centrale.
FEUILLES = HYPOTHESES["centrale"]

#: Première année reprise. Le classeur commence en 2023, mais 2023 à 2025 sont
#: observées et le dépôt les certifie déjà depuis l'INSEE BDM et l'OCDE :
#: l'observé prime sur le projeté, y compris quand le projeté vient du même
#: producteur. Les hypothèses basse et haute s'écartent de la centrale dès
#: 2025 dans le classeur ; 2025 reste, sous chacune, ce que le dépôt observe.
PREMIERE_ANNEE_PROJETEE = 2026

#: Espérances publiées sous chaque table, par le début de leur libellé.
LIBELLES = {
    "Espérance de vie à la naissance": "e0",
    "Espérance de vie à 60 ans": "e60",
    "Espérance de vie à 65 ans": "e65",
}

#: Contrôle de la convention d'âge : espérance de vie à la naissance que
#: chaque hypothèse implique en 2070, telle que l'INSEE la publie (Insee
#: Première n° 2108, juin 2026) : 89,5 et 86,7 ans sous la centrale, dont
#: « les hypothèses basse et haute d'espérance de vie en 2070 s'écartent de
#: ± 3,0 ans ».
CONTROLE = {
    ("centrale", "F", 2070): 89.5, ("centrale", "H", 2070): 86.7,
    ("basse", "F", 2070): 86.5, ("basse", "H", 2070): 83.7,
    ("haute", "F", 2070): 92.5, ("haute", "H", 2070): 89.7,
}
TOLERANCE_CONTROLE = 0.1

#: Contrôle de la conversion : écart admis entre les espérances à 60 et 65 ans
#: de la table convertie et celles que l'INSEE publie, en années.
TOLERANCE_CONVERSION = 0.05

#: Âge terminal des tables du modèle (``donnees.mortalite.AGE_TERMINAL``).
AGE_TERMINAL = 120

#: Décimales des quotients écrits, celles des quotients observés.
DECIMALES = 6


def _quotients(grille: dict) -> dict[int, dict[int, float]]:
    """Quotients ``annee -> age -> qx`` lus dans une feuille du classeur.

    Disposition : la ligne d'en-tête porte les années à partir de la deuxième
    colonne, chaque ligne suivante un âge en première colonne. Les quotients
    sont exprimés pour 100 000.
    """
    annees = _annees(grille)
    table: dict[int, dict[int, float]] = {}
    ages = {
        ligne: int(valeur)
        for (ligne, colonne), valeur in grille.items()
        if colonne == 0 and ligne > 1 and isinstance(valeur, float)
    }
    for ligne, age in ages.items():
        for colonne, annee in annees.items():
            quotient = grille.get((ligne, colonne))
            if not isinstance(quotient, float):
                continue
            # Un quotient est une probabilité : ce qui n'en est pas une n'est
            # pas une valeur de la table.
            probabilite = quotient / 100_000.0
            if not 0.0 <= probabilite <= 1.0:
                continue
            table.setdefault(annee, {})[age] = probabilite
    return table


def _annees(grille: dict) -> dict[int, int]:
    """Colonne -> année, lues sur la ligne d'en-tête de la feuille."""
    annees = {
        colonne: int(valeur)
        for (ligne, colonne), valeur in grille.items()
        if ligne == 1 and colonne > 0 and isinstance(valeur, float)
    }
    if not annees:
        raise LookupError("aucune année en en-tête de feuille")
    return annees


def _esperances_publiees(grille: dict) -> dict[int, dict[str, float]]:
    """Espérances ``annee -> mesure -> valeur`` publiées sous la table."""
    annees = _annees(grille)
    lignes = {
        ligne: mesure
        for (ligne, colonne), texte in grille.items()
        if colonne == 0 and isinstance(texte, str)
        for debut, mesure in LIBELLES.items()
        if texte.strip().startswith(debut)
    }
    if sorted(lignes.values()) != sorted(LIBELLES.values()):
        raise LookupError(
            f"espérances publiées introuvables sous la table : {sorted(lignes.values())}")
    table: dict[int, dict[str, float]] = {}
    for ligne, mesure in lignes.items():
        for colonne, annee in annees.items():
            valeur = grille.get((ligne, colonne))
            if isinstance(valeur, float):
                table.setdefault(annee, {})[mesure] = valeur
    return table


def esperance(quotients: dict[int, float], age: int) -> float:
    """Espérance de vie résiduelle à ``age``, somme cumulée des survies.

    Sans le demi-an de la formule usuelle : le classeur indexe ses quotients par
    âge atteint dans l'année, qui le comprend déjà. Voir l'en-tête du module.
    """
    total, survie, courant = 0.0, 1.0, age
    while courant in quotients:
        survie *= 1.0 - quotients[courant]
        total += survie
        courant += 1
    return total


def convertir(atteints: dict[int, float]) -> dict[int, float]:
    """Quotients d'âge exact tirés des quotients par âge atteint.

    Le carré de l'âge exact x à x + 1 est encadré par les parallélogrammes des
    âges atteints x et x + 1 : sa survie est la moyenne géométrique des leurs.
    Le dernier âge garde son quotient, faute de parallélogramme au-dessus.
    """
    exacts: dict[int, float] = {}
    for age, quotient in sorted(atteints.items()):
        suivant = atteints.get(age + 1)
        exacts[age] = (quotient if suivant is None
                       else 1.0 - math.sqrt((1.0 - quotient) * (1.0 - suivant)))
    return exacts


def esperance_exacte(quotients: dict[int, float], age: int) -> float:
    """Espérance de vie résiduelle à l'âge exact ``age``, comme le modèle la
    somme : trapèzes d'âge exact en âge exact, jusqu'à l'âge terminal."""
    total, survie, courant = 0.0, 1.0, age
    while courant < AGE_TERMINAL and courant in quotients:
        suivante = survie * (1.0 - quotients[courant])
        total += 0.5 * (survie + suivante)
        survie = suivante
        courant += 1
    return total


def extraire(donnees: bytes, hypothese: str = "centrale"
             ) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    """Ce que le classeur apporte au dépôt, de 2026 à 2125, sous une hypothèse
    d'espérance de vie (:data:`HYPOTHESES`).

    Trois dictionnaires : les espérances publiées, ``annee|sexe|mesure`` ; les
    quotients d'âge exact convertis, ``annee|sexe|age`` ; et, pour les
    contrôles, les espérances à la naissance de la convention du classeur et
    les espérances à 60 et 65 ans de la table convertie, ``annee|sexe|mesure``.
    """
    return extraire_du_classeur(feuilles(donnees), hypothese)


def extraire_du_classeur(classeur: dict, hypothese: str
                         ) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    """:func:`extraire`, sur un classeur déjà lu : il ne se lit qu'une fois
    pour les trois hypothèses."""
    noms = HYPOTHESES[hypothese]
    manquantes = set(noms) - set(classeur)
    if manquantes:
        raise LookupError(
            f"feuilles absentes du classeur : {sorted(manquantes)} "
            f"(présentes : {sorted(classeur)})"
        )

    esperances: dict[str, float] = {}
    quotients: dict[str, float] = {}
    recalculees: dict[str, float] = {}
    for feuille, sexe in noms.items():
        table = _quotients(classeur[feuille])
        publiees = _esperances_publiees(classeur[feuille])
        for annee, atteints in table.items():
            if annee < PREMIERE_ANNEE_PROJETEE:
                continue
            # Une table tronquée rendrait une espérance trop courte : on exige
            # que la table aille jusqu'au grand âge avant d'en tirer un chiffre.
            if max(atteints) < 105:
                continue
            for mesure in LIBELLES.values():
                if mesure not in publiees.get(annee, {}):
                    raise LookupError(
                        f"{mesure} non publiée pour {sexe} en {annee} ({hypothese})")
                esperances[f"{annee}|{sexe}|{mesure}"] = round(publiees[annee][mesure], 2)
            exacts = {age: round(q, DECIMALES) for age, q in convertir(atteints).items()}
            for age, quotient in sorted(exacts.items()):
                quotients[f"{annee}|{sexe}|{age}"] = quotient
            recalculees[f"{annee}|{sexe}|e0"] = esperance(atteints, 0)
            for age in (60, 65):
                recalculees[f"{annee}|{sexe}|e{age}"] = esperance_exacte(exacts, age)
                recalculees[f"{annee}|{sexe}|e{age}_publiee"] = publiees[annee][f"e{age}"]
    return esperances, quotients, recalculees


def ecarts_de_conversion(recalculees: dict[str, float]) -> list[tuple[str, float]]:
    """Les espérances de la table convertie qui s'écartent de la publication
    de plus que :data:`TOLERANCE_CONVERSION`."""
    return [
        (cle, round(valeur - recalculees[f"{cle}_publiee"], 3))
        for cle, valeur in sorted(recalculees.items())
        if cle.endswith(("|e60", "|e65"))
        and abs(valeur - recalculees[f"{cle}_publiee"]) > TOLERANCE_CONVERSION
    ]


def _telecharger(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=300) as reponse:
        return reponse.read()


def _ecrire(chemin: Path, serie: dict[str, float], note: str, cle_tri,
            publication: str = PUBLICATION) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(
        json.dumps({
            "source": URL,
            "publication": publication,
            "recupere_le": date.today().isoformat(),
            "note": note,
            "serie": dict(sorted(serie.items(), key=lambda kv: cle_tri(kv[0]))),
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )


def _echec(message: str) -> int:
    print(f"ÉCHEC   {message}", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    option_fichier(analyseur)
    options = analyseur.parse_args(argv)
    print(f"Source    {URL}")
    try:
        donnees = lire_ou_telecharger(URL, _telecharger, options.fichier)
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as erreur:
        return _echec(f"téléchargement : {erreur}")
    print(f"Classeur  {len(donnees) / 1024:,.0f} Ko")

    try:
        classeur = feuilles(donnees)
        lus = {hypothese: extraire_du_classeur(classeur, hypothese)
               for hypothese in HYPOTHESES}
    except (LookupError, ValueError) as erreur:
        return _echec(f"lecture du classeur : {erreur}")

    serie, quotients, _ = lus["centrale"]
    annees = sorted({int(cle.split("|")[0]) for cle in serie})
    if not annees:
        return _echec("aucune espérance publiée")

    # Le contrôle qui autorise la lecture : la convention d'âge du classeur
    # n'est pas celle des tables du moment, et seule la valeur publiée par
    # l'INSEE peut trancher. Sans lui, un demi-an d'erreur passerait dans le
    # diviseur de conversion de toutes les liquidations à venir.
    for (hypothese, sexe, annee), attendu in CONTROLE.items():
        obtenu = lus[hypothese][2].get(f"{annee}|{sexe}|e0")
        if obtenu is None or abs(obtenu - attendu) > TOLERANCE_CONTROLE:
            return _echec(f"espérance à la naissance {sexe} en {annee}, hypothèse "
                          f"{hypothese} : {obtenu} contre {attendu} publié par l'INSEE")
        print(f"Contrôle  e0 {hypothese:<8} {sexe} {annee} : {obtenu:.2f} ans, "
              f"INSEE {attendu} ans")

    # Le contrôle qui autorise la conversion : la table que le modèle lira doit
    # rendre, à 60 et 65 ans, les espérances que l'INSEE publie, sous chaque
    # hypothèse.
    for hypothese, (_, _, recalculees) in lus.items():
        ecarts = ecarts_de_conversion(recalculees)
        if ecarts:
            return _echec(f"table convertie loin de la publication ({hypothese}) : "
                          f"{ecarts[:5]}")
        plus_grand = max(
            (abs(v - recalculees[f"{c}_publiee"]), c) for c, v in recalculees.items()
            if c.endswith(("|e60", "|e65")))
        print(f"Contrôle  conversion {hypothese:<8} : écart maximal {plus_grand[0]:.3f} an "
              f"({plus_grand[1]}), tolérance {TOLERANCE_CONVERSION}")

    # Trois contrôles de vraisemblance, sans lesquels un décalage de colonne ou
    # une feuille prise pour une autre passeraient inaperçus : sous chaque
    # hypothèse, l'espérance de vie croît sur toute la projection, et les
    # femmes vivent plus longtemps que les hommes à chaque année ; et chaque
    # année, à 60 comme à 65 ans, la basse est sous la centrale, elle-même
    # sous la haute.
    for hypothese, (publiees, _, _) in lus.items():
        if sorted({int(cle.split("|")[0]) for cle in publiees}) != annees:
            return _echec(f"années de l'hypothèse {hypothese} autres que la centrale")
        for sexe in FEUILLES.values():
            suite = [publiees[f"{a}|{sexe}|e0"] for a in annees]
            if any(b < a - 0.01 for a, b in zip(suite, suite[1:])):
                return _echec(f"espérance à la naissance non croissante ({sexe}, {hypothese})")
        for annee in annees:
            if publiees[f"{annee}|F|e60"] <= publiees[f"{annee}|H|e60"]:
                return _echec(f"e60 des femmes sous celle des hommes en {annee} ({hypothese})")
    for annee in annees:
        for sexe in FEUILLES.values():
            for mesure in ("e60", "e65"):
                basse, centrale, haute = (lus[h][0][f"{annee}|{sexe}|{mesure}"]
                                          for h in ("basse", "centrale", "haute"))
                if not basse < centrale < haute:
                    return _echec(f"{mesure} {sexe} {annee} : basse {basse}, centrale "
                                  f"{centrale}, haute {haute}, hors de cet ordre")

    manquantes = [a for a in range(annees[0], annees[-1] + 1) if a not in annees]
    if manquantes:
        print(f"\nAnnées sans espérance : {manquantes}", file=sys.stderr)

    _ecrire(SORTIE, serie,
            "e0, e60 et e65 PUBLIÉES par l'INSEE sous chaque table de quotients "
            "du classeur, arrondies au centième. Elles étaient dérivées des "
            "quotients jusqu'au 7 octobre 2026.",
            lambda cle: (int(cle.split("|")[0]), cle.split("|")[1], cle.split("|")[2]))
    _ecrire(SORTIE_QUOTIENTS, quotients,
            "Quotients d'âge exact CONVERTIS des quotients par âge atteint dans "
            "l'année que publie l'INSEE : 1 − q(x) = √[(1 − q'(x))(1 − q'(x + 1))], "
            "le dernier âge gardant le sien. La table convertie retrouve les "
            "espérances publiées à 60 et 65 ans à moins de 0,05 an.",
            lambda cle: (int(cle.split("|")[0]), cle.split("|")[1], int(cle.split("|")[2])))
    variantes = [hypothese for hypothese in HYPOTHESES if hypothese != "centrale"]
    esperances_variantes = {f"{h}|{cle}": valeur for h in variantes
                            for cle, valeur in lus[h][0].items()}
    quotients_variantes = {f"{h}|{cle}": valeur for h in variantes
                           for cle, valeur in lus[h][1].items()}
    _ecrire(SORTIE_VARIANTES, esperances_variantes,
            "e0, e60 et e65 PUBLIÉES par l'INSEE sous les tables des hypothèses "
            "d'espérance de vie basse et haute, arrondies au centième, sous la "
            "clé hypothese|annee|sexe|mesure.",
            lambda cle: (cle.split("|")[0], int(cle.split("|")[1]),
                         cle.split("|")[2], cle.split("|")[3]),
            PUBLICATION_VARIANTES)
    _ecrire(SORTIE_QUOTIENTS_VARIANTES, quotients_variantes,
            "Quotients d'âge exact des hypothèses d'espérance de vie basse et "
            "haute, CONVERTIS comme ceux de la centrale, sous la clé "
            "hypothese|annee|sexe|age. Chaque table convertie retrouve les "
            "espérances publiées à 60 et 65 ans à moins de 0,05 an.",
            lambda cle: (cle.split("|")[0], int(cle.split("|")[1]),
                         cle.split("|")[2], int(cle.split("|")[3])),
            PUBLICATION_VARIANTES)
    print(f"\n{len(serie)} espérances écrites dans {SORTIE}")
    print(f"{len(quotients)} quotients écrits dans {SORTIE_QUOTIENTS}")
    print(f"{len(esperances_variantes)} espérances écrites dans {SORTIE_VARIANTES}")
    print(f"{len(quotients_variantes)} quotients écrits dans {SORTIE_QUOTIENTS_VARIANTES}")
    print(f"Couverture {annees[0]}-{annees[-1]}, {len(FEUILLES)} sexes, "
          f"{len(HYPOTHESES)} hypothèses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
