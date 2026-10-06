#!/usr/bin/env python3
"""Population par âge, observée puis projetée, auprès de l'INSEE.

    python scripts/fetch/insee_projections_population.py
    python scripts/fetch/insee_projections_population.py --fichier 00_central.xlsx

Le dépôt calcule des droits individuels. Pour dire ce que coûtera un système,
il faut en plus savoir COMBIEN de gens le percevront : une pyramide des âges.
C'est la pièce que `docs/limites.md` déclarait manquante, et la voici — non
reconstituée, mais publiée par son producteur, dans le même exercice de
projection dont le dépôt tire déjà ses quotients de mortalité.

Le classeur du **scénario central des projections de population 2026** porte,
dans son onglet `population`, l'effectif au 1er janvier par âge détaillé et par
année, de 1962 à 2070. Une seule série, une seule source, une seule
méthodologie de part et d'autre de la frontière — et cette frontière, l'INSEE
la date lui-même en pied de tableau : « estimations de population jusqu'en
2023 ; projections de population 2026 à partir de 2024 ». Le dépôt la reprend
telle quelle, et n'appelle `certifiee` que ce qui est observé.

DEUX SÉRIES, ET UN SEUL FICHIER SOURCE
---------------------------------------
* les effectifs par âge, retenus **à partir de 50 ans** — aucune pension de
  droit direct n'est servie avant, le cas type qui part le plus tôt liquidant à
  52 ans. Descendre plus bas quadruplerait le poids du paquet que charge le
  site sans changer un seul chiffre ;
* l'effectif des **20-64 ans**, que le classeur agrège lui-même. Il ne sert pas
  à compter des retraités mais à projeter le PIB : rapporter une dépense à la
  richesse produite suppose de savoir combien de personnes la produisent, et
  l'hypothèse d'emploi constant du dépôt, neutre pour l'indexation, ne l'est
  pas du tout ici.

Le scénario retenu est le CENTRAL, seul dont le COR et le dépôt se réclament.
Le classeur en publie seize autres.

UNE TROISIÈME SÉRIE : LES ARRIVÉES TARDIVES (action 147, étape 11)
-------------------------------------------------------------------
La page Coût compte ses retraités dans cette pyramide, et sert à chacun la
pension d'une carrière française complète. Or une génération y gagne, après
ses études, des personnes arrivées en France à l'âge adulte, dont la carrière
française est courte : la grille les payait plein. Leur part se lit dans le
même classeur, sans autre source : la population d'une génération au 1er
janvier de l'année suivante, moins celle de l'année, plus ses décès de
l'année, est ce qu'elle a gagné ou perdu de résidents (onglets `population`
et `deces`), observé jusqu'en 2022, selon l'hypothèse de solde migratoire
ensuite (+ 150 000 par an). Génération par génération, de 1941 à 2005, le
script en tire, à 64 ans, la part des résidents entrés après 21 ans, et la
part de pension que leur carrière française n'a pas : une arrivée à l'âge
`a` y travaille (64 - a) / (64 - 21) d'une carrière. Voir
:func:`arrivees_tardives` pour ce qui est compté, et ce qui ne l'est pas.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lecture_xlsx import feuilles  # noqa: E402

URL = "https://www.insee.fr/fr/statistiques/fichier/8990852/00_central.xlsx"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/insee_projections_population.json")

#: Onglet du classeur qui porte la pyramide des âges.
FEUILLE = "population"

#: Âge à partir duquel les effectifs sont repris. Le cas type qui liquide le
#: plus tôt — l'agent de conduite de la SNCF — part à 52 ans ; on descend deux
#: ans plus bas pour que la borne ne soit pas rasante.
AGE_MINIMAL = 50

#: Dernier âge publié par année d'âge. Au-delà, le classeur regroupe sous
#: « 105+ » : 1 570 personnes en 2024, soit deux millionièmes de la population.
#: On s'arrête donc à 104, et le regroupement reste dehors.
AGE_MAXIMAL = 104

#: Libellé de la ligne d'agrégat qui porte la population d'âge actif.
LIGNE_ACTIFS = "20-64 ans"

#: Dernière année que l'INSEE tient pour observée. Le classeur le dit en pied
#: de tableau ; le vérificateur en fait la frontière entre `certifiee` et
#: `estimee`.
DERNIERE_ANNEE_OBSERVEE = 2023

#: Contrôles de vraisemblance, tels que l'INSEE les publie dans Insee Première
#: n° 2108 : population totale en 2070, et part des 65 ans ou plus.
CONTROLE_POPULATION_2070 = 65.9e6
TOLERANCE_CONTROLE = 0.2e6

#: Les arrivées tardives (:func:`arrivees_tardives`). Une arrivée compte
#: après ``AGE_ENTREE_ARRIVEES`` — l'âge où la carrière d'un natif commence —,
#: et se mesure à ``AGE_REFERENCE_ARRIVEES``, celui du départ des générations
#: que la projection fait partir.
AGE_ENTREE_ARRIVEES = 21
AGE_REFERENCE_ARRIVEES = 64
#: Les générations mesurées : la première dont toutes les arrivées après 21
#: ans tombent dans le classeur, qui commence en 1962 ; la dernière qui a 64
#: ans au 1er janvier 2070.
GENERATIONS_ARRIVEES = (1941, 2005)
#: 1962, l'année des rapatriés d'Algérie : des carrières françaises, que la
#: grille paie bien. Elle ne compte pas d'arrivée.
ANNEE_RAPATRIES = 1962
#: Les deux changements de champ du classeur — les départements d'outre-mer
#: en 1995, Mayotte en 2014 — font gagner aux générations des résidents qui
#: n'arrivent de nulle part : l'année qui les porte prend la moyenne des
#: deux années qui l'entourent.
RUPTURES_DE_CHAMP = (1994, 2013)


def _grille(onglets: dict, feuille: str = FEUILLE) -> dict[tuple[int, int], float | str]:
    if feuille not in onglets:
        raise LookupError(f"onglet {feuille!r} absent du classeur")
    return onglets[feuille]


def _par_age(grille: dict[tuple[int, int], float | str]) -> dict[tuple[int, int], float]:
    """Une feuille âge × année, tous âges détaillés : (âge, année) -> valeur.

    Même disposition que ``population`` : les années en deuxième ligne, l'âge
    en première colonne ; les lignes d'agrégats, au libellé écrit, restent
    dehors, comme « 105+ ».
    """
    annees = {
        colonne: int(valeur)
        for (ligne, colonne), valeur in grille.items()
        if ligne == 1 and colonne > 0 and isinstance(valeur, float)
    }
    table: dict[tuple[int, int], float] = {}
    for (ligne, colonne), valeur in grille.items():
        age = grille.get((ligne, 0))
        if (ligne > 1 and colonne in annees and isinstance(age, float)
                and isinstance(valeur, float)):
            table[(int(age), annees[colonne])] = valeur
    return table


def arrivees_tardives(onglets: dict) -> dict[str, dict[str, float]]:
    """Génération par génération, ce que les arrivées après 21 ans retirent à
    la pension d'une carrière française complète.

    LE SOLDE. Ce qu'une génération gagne ou perd de résidents une année est
    sa population au 1er janvier suivant, moins celle de l'année, plus ses
    décès de l'année : ``P(a, y+1) - P(a-1, y) + D(a, y)``, ``a`` étant l'âge
    atteint dans l'année — celui des décès —, la population étant comptée en
    âge révolu au 1er janvier. Jusqu'en 2022, l'INSEE l'observe, ajustements
    des recensements compris : ce sont des résidents que la pyramide compte,
    et que la grille paie. Ensuite, c'est l'hypothèse de solde migratoire du
    scénario central (+ 150 000 par an dès 2026, aux trois quarts entre 22 et
    63 ans), au résident près. L'identité se vérifie à l'unité sur les années
    projetées, où l'onglet ``solde_migratoire`` la publie.

    CE QUI EST COMPTÉ. Le solde POSITIF de chaque âge de 22 à 64 ans, porté
    jusqu'à 64 ans par la survie de la génération, rapporté à sa population à
    64 ans : ``arrivees``. Chaque arrivée à l'âge ``a`` travaille en France
    (64 - a) / (64 - 21) d'une carrière, et sa pension en est d'autant plus
    courte : ``manque``, la part de la pension de carrière complète que la
    génération n'a pas. La pension est tenue proportionnelle aux années — ni
    décote, ni salaires plus bas, que l'enquête de la DREES trouve pourtant
    aux retraités nés à l'étranger (leur pension vaut 81 % de celle des
    natifs résidents, leur durée validée 90 %, EIR 2020) —, et le solde, net
    des départs, compte moins d'arrivées qu'il n'y en a : deux bornes basses.

    CE QUI NE L'EST PAS. 1962 (les rapatriés, ``ANNEE_RAPATRIES``) ; les deux
    changements de champ (``RUPTURES_DE_CHAMP``), remplacés par la moyenne des
    années voisines ; les arrivées après 64 ans, rares (8 000 par an dans
    l'hypothèse) ; les arrivées d'avant 1962, faute de pyramide — d'où la
    première génération, 1941, dont la carrière commence en 1963.
    """
    population = _par_age(_grille(onglets, "population"))
    deces = _par_age(_grille(onglets, "deces"))
    entree, reference = AGE_ENTREE_ARRIVEES, AGE_REFERENCE_ARRIVEES

    def solde(age: int, annee: int) -> float:
        if annee == ANNEE_RAPATRIES:
            return 0.0
        if annee in RUPTURES_DE_CHAMP:
            return (solde(age, annee - 1) + solde(age, annee + 1)) / 2.0
        return (population[(age, annee + 1)] - population[(age - 1, annee)]
                + deces[(age, annee)])

    def survie(generation: int, age: int) -> float:
        """De l'année de l'arrivée, à ``age``, au 1er janvier des 65 ans."""
        valeur = 1.0
        for atteint in range(age + 1, reference + 1):
            annee = generation + atteint
            valeur *= 1.0 - deces[(atteint, annee)] / population[(atteint - 1, annee)]
        return valeur

    premiere, derniere = GENERATIONS_ARRIVEES
    resultat: dict[str, dict[str, float]] = {}
    for generation in range(premiere, derniere + 1):
        effectif = population[(reference, generation + reference + 1)]
        arrivees = manque = 0.0
        for age in range(entree + 1, reference + 1):
            venus = max(solde(age, generation + age), 0.0) * survie(generation, age)
            arrivees += venus
            manque += venus * (1.0 - (reference - age) / (reference - entree))
        resultat[str(generation)] = {
            "arrivees": arrivees / effectif,
            "manque": manque / effectif,
        }
    return resultat


def extraire(grille: dict[tuple[int, int], float | str]) -> dict:
    """Effectifs par âge et effectif d'âge actif, année par année.

    Disposition : la ligne d'en-tête porte les années à partir de la deuxième
    colonne, chaque ligne suivante un âge en première colonne, puis, plus bas,
    des lignes d'agrégats repérées par leur libellé.
    """
    annees = {
        colonne: int(valeur)
        for (ligne, colonne), valeur in grille.items()
        if ligne == 1 and colonne > 0 and isinstance(valeur, float)
    }
    if not annees:
        raise LookupError("aucune année en en-tête de feuille")

    lignes_ages = {
        ligne: int(valeur)
        for (ligne, colonne), valeur in grille.items()
        if colonne == 0 and ligne > 1 and isinstance(valeur, float)
        and AGE_MINIMAL <= valeur <= AGE_MAXIMAL
    }
    par_age: dict[str, float] = {}
    for ligne, age in lignes_ages.items():
        for colonne, annee in annees.items():
            effectif = grille.get((ligne, colonne))
            if isinstance(effectif, float) and effectif >= 0:
                par_age[f"{annee}|{age}"] = effectif

    lignes_actifs = [
        ligne for (ligne, colonne), valeur in grille.items()
        if colonne == 0 and valeur == LIGNE_ACTIFS
    ]
    if not lignes_actifs:
        raise LookupError(f"ligne d'agrégat {LIGNE_ACTIFS!r} introuvable")
    # Le libellé sert deux blocs, l'effectif puis la part : on retient le
    # premier, dont les valeurs se comptent en millions et non en fractions.
    actifs: dict[str, float] = {}
    for ligne in sorted(lignes_actifs):
        candidats = {
            str(annee): grille[(ligne, colonne)]
            for colonne, annee in annees.items()
            if isinstance(grille.get((ligne, colonne)), float)
        }
        if candidats and min(candidats.values()) > 1e6:
            actifs = candidats
            break
    if not actifs:
        raise LookupError(f"aucun effectif sous {LIGNE_ACTIFS!r}")

    return {
        "par_age": dict(sorted(par_age.items())),
        "actifs_20_64": dict(sorted(actifs.items())),
        "derniere_annee_observee": DERNIERE_ANNEE_OBSERVEE,
    }


def controler(charge: dict) -> None:
    """La population de 2070 doit être celle que l'INSEE publie.

    Le contrôle ne porte pas sur ce qu'on reprend — les 50 ans et plus — mais
    sur ce qui le borne : si le classeur changeait de scénario, de champ ou de
    disposition, ce total bougerait. Il est reconstitué en additionnant les
    50 ans et plus aux 20-64 ans, dont la tranche 50-64 est commune, puis en
    complétant par les moins de 20 ans que le classeur agrège aussi.
    """
    par_age = charge["par_age"]
    total_50 = sum(
        effectif for cle, effectif in par_age.items() if cle.startswith("2070|")
    )
    # Ordre de grandeur seulement : les 50 ans et plus sont un peu moins de la
    # moitié de la population projetée en 2070.
    if not 25e6 < total_50 < 40e6:
        raise ValueError(
            f"population des 50 ans et plus en 2070 invraisemblable : {total_50:,.0f}"
        )


def main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if arguments[:1] == ["--fichier"] and len(arguments) == 2:
        # Le classeur déjà téléchargé : le même fichier, lu sans réseau.
        donnees = Path(arguments[1]).expanduser().read_bytes()
    elif arguments:
        print("usage : insee_projections_population.py [--fichier CLASSEUR]",
              file=sys.stderr)
        return 2
    else:
        try:
            demande = urllib.request.Request(URL, headers=ENTETES)
            with urllib.request.urlopen(demande, timeout=300) as reponse:
                donnees = reponse.read()
        except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
            print(f"INSEE indisponible : {erreur}", file=sys.stderr)
            return 1

    onglets = feuilles(donnees)
    charge = extraire(_grille(onglets))
    controler(charge)
    charge["arrivees_tardives"] = arrivees_tardives(onglets)
    charge["source"] = URL

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    annees = sorted({int(cle.split("|")[0]) for cle in charge["par_age"]})
    print(f"{len(charge['par_age'])} effectifs par âge écrits dans {SORTIE}")
    print(f"Couverture {annees[0]}-{annees[-1]}, âges {AGE_MINIMAL}-{AGE_MAXIMAL}")
    print(f"Observé jusqu'en {DERNIERE_ANNEE_OBSERVEE}, projeté ensuite")
    manques = charge["arrivees_tardives"]
    print(f"Arrivées tardives de {min(manques)} à {max(manques)} : manque de "
          f"{manques[min(manques)]['manque']:.2%} à {manques[max(manques)]['manque']:.2%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
