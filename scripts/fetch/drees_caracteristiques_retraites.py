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

LES QUINTILES EN ÉQUIVALENT CARRIÈRE COMPLÈTE (action 136, étape 6)
--------------------------------------------------------------------
La feuille « QuintilesEQCC » range les retraités par quintile de leur pension
de droit direct en équivalent carrière complète : la pension divisée par la
somme des coefficients de proratisation de leurs régimes de base, « 950 / (20 %
+ 60 %) = 1 188 € », qui « neutralise l'effet de la proratisation » sans dire
ce qu'aurait été la pension d'une carrière complète (DREES, Conseil
d'orientation des retraites, séance du 24 novembre 2022). La durée retirée, le
quintile dit ce que la carrière a acquis par année validée ; croisé avec les
tranches de durée, il dit où tombent les carrières courtes : chez les femmes,
le premier quintile compte 23,1 % de carrières de moins de dix années validées
hors majorations, le dernier 0,4 %. Pour chaque quintile et chaque sexe : les
effectifs, la proratisation et les pensions moyennes, la part au minimum de
pension de son régime principal, la durée validée hors majorations et ses cinq
tranches. Le récupérateur vérifie ce qu'il lit : les tranches font cent, les
quintiles redonnent l'effectif, et chacun compte un cinquième des retraités.

Le jeu porte la même feuille pour les seuls RÉSIDENTS en France, dans le
classeur qui leur est propre, et le récupérateur la lit aussi : la population
de la page ne compte que des résidents, et c'est contre eux qu'elle se mesure.
Il y lit, de plus, la durée validée majorations comprises, la durée cotisée,
la part des départs avec décote, et la part de chaque régime principal,
monopensionnés et polypensionnés de deux régimes, une case vide se lisant zéro.

LA CONDITION DE LIQUIDATION SELON L'ÂGE (action 138, étape 14)
---------------------------------------------------------------
Du même classeur des résidents, la feuille « CondLiquidation » range les
retraités par condition de leur liquidation dans leur régime principal —
carrière longue, décote, décote inapplicable, surcote, taux plein pour
invalidité, pour inaptitude, pour un autre motif, par l'âge, par la durée —,
et dit, pour chacune et pour tous, l'âge des retraités au 31 décembre de
l'enquête : l'âge moyen, la part de chaque tranche de cinq ans. Le récupérateur
lit l'effectif et l'âge, une case vide se lisant zéro, et vérifie que les
tranches de chaque condition font cent, que les conditions comptent les
retraités de l'ensemble, un sur cent n'en ayant pas, et que les deux sexes le
redonnent. La part des décotés dans chaque tranche s'en tire : 8,8 % des
résidentes de 85 ans et plus sont parties avec une décote, 4,6 % de celles de
75 à 79 ans ; la population de la page y prend la décote des générations
d'avant 1950, que l'EIR ne suit pas une à une.
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

#: Le classeur des seuls résidents en France, du même millésime : on n'en lit
#: que la feuille des quintiles en équivalent carrière complète, contre
#: laquelle se mesure la population de la page, qui ne compte qu'eux (action
#: 136, étape 6).
_TITRE_RESIDENTS = re.compile(
    r"Caractéristiques de tous les retraités résidant en France \(EIR (\d{4})\)")

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
    # Ce qui suit ancre la grille élargie de `scripts/grille_large.py` (action
    # 136, étape 6) : ce que treize cas types, à carrière complète, d'un seul
    # régime et d'hommes pour douze d'entre eux, déplacent sur la page Coût.
    # La durée COTISÉE, et la durée validée hors majorations : leur écart est
    # celui des périodes assimilées, la différence avec la durée validée celui
    # des majorations. Le classeur intitule la seconde « Moyenne de la durée
    # cotisée hors majoration », mais ses valeurs dépassent la durée cotisée et
    # les tranches qui la suivent disent « durée validée hors majoration » :
    # c'est l'intitulé qui se trompe, et le code dit ce que la ligne mesure.
    # Le début est pris jusqu'à la parenthèse, que la ligne voisine n'a pas.
    "duree_cotisee": "Moyenne de la durée cotisée (en années)",
    "duree_validee_hors_majoration": "Moyenne de la durée cotisée hors majoration",
    # Les cinq tranches de durée validée : la part des carrières courtes.
    "part_duree_validee_moins_10": (
        "Proportion d'assurés dont la durée validée est inférieure à 10 ans"
    ),
    "part_duree_validee_10_20": (
        "Proportion d'assurés dont la durée validée est comprise entre 10 et 20 ans"
    ),
    "part_duree_validee_20_30": (
        "Proportion d'assurés dont la durée validée est comprise entre 20 et 30 ans"
    ),
    "part_duree_validee_30_40": (
        "Proportion d'assurés dont la durée validée est comprise entre 30 et 40 ans"
    ),
    "part_duree_validee_40_plus": (
        "Proportion d'assurés dont la durée validée est supérieure ou égale à 40 ans"
    ),
    # Les mêmes, hors majorations : ce que la grille cale, le modèle ajoutant
    # lui-même les trimestres des enfants.
    "part_duree_validee_hors_majoration_moins_10": (
        "Proportion d'assurés dont la durée validée hors majoration est inférieure "
        "à 10 ans"
    ),
    "part_duree_validee_hors_majoration_10_20": (
        "Proportion d'assurés dont la durée validée hors majoration est comprise "
        "entre 10 et 20 ans"
    ),
    "part_duree_validee_hors_majoration_20_30": (
        "Proportion d'assurés dont la durée validée hors majoration est comprise "
        "entre 20 et 30 ans"
    ),
    "part_duree_validee_hors_majoration_30_40": (
        "Proportion d'assurés dont la durée validée hors majoration est comprise "
        "entre 30 et 40 ans"
    ),
    "part_duree_validee_hors_majoration_40_plus": (
        "Proportion d'assurés dont la durée validée hors majoration est supérieure "
        "ou égale à 40 ans"
    ),
    # Les monopensionnés et les polypensionnés de deux régimes de base, selon
    # leur régime principal : des PERSONNES, là où les effectifs de caisse
    # comptent un polypensionné dans chacune des siennes.
    "part_monopensionnes": "Proportion de monopensionnés",
    "part_mono_regime_general": (
        "Monopensionnés, anciens salariés : salariés du régime général"
    ),
    "part_mono_fonction_publique_etat_civile": (
        "Monopensionnés, anciens salariés : fonctionnaires civils d’État"
    ),
    "part_mono_fonction_publique_etat_militaire": (
        "Monopensionnés, anciens salariés : fonctionnaires militaires d’État"
    ),
    "part_mono_msa_salaries": "Monopensionnés, anciens salariés : MSA salariés",
    "part_mono_cnracl": "Monopensionnés, anciens salariés : fonctionnaires CNRACL",
    "part_mono_regimes_speciaux": "Monopensionnés, anciens salariés : régimes spéciaux",
    "part_mono_msa_non_salaries": (
        "Monopensionnés, anciens non-salariés : MSA non-salariés"
    ),
    "part_mono_professions_liberales": (
        "Monopensionnés, anciens non-salariés : Professions libérales"
    ),
    "part_poly_2_regimes": "Proportion de polypensionnés de 2 régimes de base",
    "part_poly_regime_general": (
        "Polypensionnés de 2 régimes de base, anciens salariés : salariés du "
        "régime général"
    ),
    "part_poly_fonction_publique_etat_civile": (
        "Polypensionnés de 2 régimes de base, anciens salariés : fonctionnaires "
        "civils d’État"
    ),
    "part_poly_fonction_publique_etat_militaire": (
        "Polypensionnés de 2 régimes de base, anciens salariés : fonctionnaires "
        "militaires d’État"
    ),
    "part_poly_msa_salaries": (
        "Polypensionnés de 2 régimes de base, anciens salariés : MSA salariés"
    ),
    "part_poly_cnracl": (
        "Polypensionnés de 2 régimes de base, anciens salariés : fonctionnaires "
        "CNRACL"
    ),
    "part_poly_regimes_speciaux": (
        "Polypensionnés de 2 régimes de base, anciens salariés : régimes spéciaux"
    ),
    "part_poly_msa_non_salaries": (
        "Polypensionnés de 2 régimes de base, anciens non-salariés : MSA "
        "non-salariés"
    ),
    "part_poly_professions_liberales": (
        "Polypensionnés de 2 régimes de base, anciens non-salariés : "
        "Professions libérales"
    ),
    "part_poly_3_regimes": (
        "Proportion de polypensionnés d'au moins 3 régimes de base"
    ),
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


#: La quatrième feuille lue : les retraités selon le quintile de leur pension
#: de droit direct en équivalent carrière complète.
FEUILLE_EQCC = "QuintilesEQCC"

#: Les six colonnes, sous le code que le dépôt leur donne et l'en-tête exact
#: du classeur : les cinq quintiles, tous sexes réunis, et l'ensemble.
COLONNES_EQCC: dict[str, str] = {
    "q1": "Premier quintile",
    "q2": "Deuxième quintile",
    "q3": "Troisième quintile",
    "q4": "Quatrième quintile",
    "q5": "Cinquième quintile",
    "ensemble": "Ensemble",
}

#: Les tranches de durée validée hors majorations, sous leur code : leurs
#: libellés sont ceux de :data:`INDICATEURS`.
TRANCHES_EQCC = ("moins_10", "10_20", "20_30", "30_40", "40_plus")

#: Les indicateurs de la feuille, lus au début de leur libellé ; la durée
#: validée hors majorations sous l'intitulé qui se trompe (voir
#: :data:`INDICATEURS`).
INDICATEURS_EQCC: dict[str, str] = {
    "effectifs": "Effectifs (en milliers)",
    "coefficient_proratisation": "Coeficient de proratisation moyen",
    "pension_droit_direct": (
        "Montant moyen de la pension de retraite de droit direct brute"
    ),
    "pension_droit_direct_majorations": (
        "Montant moyen de la pension de droit direct (dont les majorations pour "
        "enfants) brute"
    ),
    "part_minimum_pension_regime_principal": (
        "Part de bénéficiaires du minimum de pension dans leur régime principal"
    ),
    "duree_validee_hors_majoration": "Moyenne de la durée cotisée hors majoration",
    **{f"part_duree_validee_hors_majoration_{tranche}":
       INDICATEURS[f"part_duree_validee_hors_majoration_{tranche}"]
       for tranche in TRANCHES_EQCC},
}


#: Les indicateurs lus chez les résidents : ceux de tous les retraités, et
#: trois de plus — la durée validée majorations comprises, la durée cotisée et
#: la part des départs avec décote, que la population, partie au taux plein,
#: n'a pas.
INDICATEURS_EQCC_RESIDENTS: dict[str, str] = {
    **INDICATEURS_EQCC,
    "duree_validee": "Moyenne de la durée validée (en années)",
    "duree_cotisee": "Moyenne de la durée cotisée (en années)",
    "part_decote": "Part de départ avec décote (en %)",
    # Et le régime principal, quintile par quintile : la place de chaque
    # régime, que la population confronte à la sienne.
    **{code: libelle for code, libelle in INDICATEURS.items()
       if code.startswith(("part_mono_", "part_poly_"))
       and code not in ("part_poly_2_regimes", "part_poly_3_regimes")},
}

#: Les indicateurs dont une case vide se lit zéro : la part d'un régime dans
#: un quintile où la DREES n'en compte aucun retraité — aucun militaire au
#: premier quintile des hommes.
VIDES_NULS_EQCC = tuple(code for code in INDICATEURS_EQCC_RESIDENTS
                        if code.startswith(("part_mono_", "part_poly_")))


def classeur_le_plus_recent(motif: re.Pattern = _TITRE) -> tuple[int, str, bytes]:
    """Le classeur du millésime le plus élevé dont le titre suit ``motif`` :
    « tous les retraités », ou ceux qui résident en France."""
    demande = urllib.request.Request(f"{BASE}/attachments", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=300) as reponse:
        pieces = json.loads(reponse.read()).get("attachments", [])
    candidats = []
    for piece in pieces:
        metas = piece.get("metas") or {}
        trouve = motif.search(metas.get("title", ""))
        if trouve and metas.get("mimetype", "").endswith("spreadsheetml.sheet"):
            candidats.append((int(trouve.group(1)), metas["title"], metas["url"]))
    if not candidats:
        raise RuntimeError(f"aucun classeur {motif.pattern!r} joint au jeu")
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


def lire_quintiles_eqcc(contenu: bytes, indicateurs: dict[str, str] = INDICATEURS_EQCC,
                        vides_nuls: tuple[str, ...] = ()
                        ) -> dict[str, dict[str, dict[str, float]]]:
    """Les ``indicateurs`` de la feuille des quintiles en équivalent carrière
    complète du classeur (:func:`quintiles_de_la_feuille`)."""
    return quintiles_de_la_feuille(feuilles(contenu, (FEUILLE_EQCC,))[FEUILLE_EQCC],
                                   indicateurs, vides_nuls)


def quintiles_de_la_feuille(grille: dict[tuple[int, int], float | str],
                            indicateurs: dict[str, str] = INDICATEURS_EQCC,
                            vides_nuls: tuple[str, ...] = ()
                            ) -> dict[str, dict[str, dict[str, float]]]:
    """Les ``indicateurs`` d'une feuille des quintiles en équivalent carrière
    complète : colonne, indicateur, sexe ; une case vide d'un indicateur de
    ``vides_nuls`` se lit zéro.

    Les colonnes sont cherchées par leur en-tête exact, les indicateurs par le
    début de leur libellé, à sa première occurrence. Ce qui est lu se vérifie :
    dans chaque colonne et pour chaque sexe, les cinq tranches de durée font
    cent, à l'arrondi près ; les cinq quintiles redonnent l'effectif de
    l'ensemble, et chacun compte le cinquième des retraités des deux sexes.
    """
    derniere_colonne = max(colonne for _, colonne in grille)
    derniere_ligne = max(ligne for ligne, _ in grille)
    colonnes: dict[str, int] = {}
    for code, entete in COLONNES_EQCC.items():
        for colonne in range(derniere_colonne + 1):
            if str(grille.get((0, colonne), "")).strip() == entete:
                colonnes[code] = colonne
                break
    manquantes = set(COLONNES_EQCC) - set(colonnes)
    if manquantes:
        raise RuntimeError(
            f"feuille {FEUILLE_EQCC!r} : colonnes absentes — "
            f"{', '.join(sorted(manquantes))}"
        )

    valeurs: dict[str, dict[str, dict[str, float]]] = {
        quintile: {code: {} for code in indicateurs} for quintile in COLONNES_EQCC
    }
    for ligne in range(1, derniere_ligne + 1):
        sexe = SEXES.get(str(grille.get((ligne, 0), "")).strip())
        libelle = " ".join(str(grille.get((ligne, 2), "")).split())
        if sexe is None or not libelle:
            continue
        for code, debut in indicateurs.items():
            if not libelle.startswith(" ".join(debut.split())):
                continue
            for quintile, colonne in colonnes.items():
                valeur = grille.get((ligne, colonne))
                if sexe in valeurs[quintile][code]:
                    continue
                if isinstance(valeur, (int, float)):
                    valeurs[quintile][code][sexe] = float(valeur)
                elif code in vides_nuls and str(valeur if valeur is not None else "").strip() == "":
                    valeurs[quintile][code][sexe] = 0.0
    manquants = [f"{quintile}/{code}" for quintile, serie in valeurs.items()
                 for code, parsexe in serie.items() if len(parsexe) < 3]
    if manquants:
        raise RuntimeError(f"quintiles EQCC illisibles : {', '.join(manquants)}")

    for quintile, serie in valeurs.items():
        for sexe in SEXES.values():
            total = sum(serie[f"part_duree_validee_hors_majoration_{tranche}"][sexe]
                        for tranche in TRANCHES_EQCC)
            if abs(total - 100.0) > 0.6:
                raise RuntimeError(
                    f"quintiles EQCC : les tranches de {quintile}/{sexe} font {total:g} %")
    # Un retraité sur cent n'a pas de quintile : ceux que la colonne de
    # l'ensemble compte, et qu'aucun quintile ne range.
    for sexe in SEXES.values():
        somme = sum(valeurs[q]["effectifs"][sexe] for q in COLONNES_EQCC if q != "ensemble")
        ensemble = valeurs["ensemble"]["effectifs"][sexe]
        if not 0.98 * ensemble <= somme <= ensemble:
            raise RuntimeError(
                f"quintiles EQCC : les quintiles comptent {somme:g} milliers de "
                f"retraités ({sexe}), l'ensemble {ensemble:g}")
    ranges = [valeurs[q]["effectifs"]["ensemble"] for q in COLONNES_EQCC if q != "ensemble"]
    cinquieme = sum(ranges) / 5.0
    if any(abs(effectif - cinquieme) > 0.01 * cinquieme for effectif in ranges):
        raise RuntimeError(f"quintiles EQCC : des quintiles inégaux — {ranges}")
    return valeurs


#: La feuille des conditions de liquidation, lue dans le classeur des
#: résidents pour l'âge des retraités de chaque condition (action 138, étape
#: 14).
FEUILLE_CONDITIONS = "CondLiquidation"

#: Ses colonnes, sous le code que le dépôt leur donne et le début de l'en-tête
#: que le classeur leur donne, le plus long gagnant : « Décote » commence
#: « Décote non applicable ».
COLONNES_CONDITIONS: dict[str, str] = {
    "carriere_longue": "Carrière longue",
    "decote": "Décote",
    "decote_inapplicable": "Décote non applicable",
    "surcote": "Surcote",
    "invalidite": "Taux plein invalidité",
    "inaptitude": "Taux plein inaptitude",
    "autres_motifs": "Taux plein autres motifs",
    "taux_plein_age": "Taux plein par âge",
    "taux_plein_duree": "Taux plein par la durée",
    "ensemble": "Ensemble",
}

#: Le début de la variable des lignes de l'âge, que suit l'année de l'enquête.
VARIABLE_AGE = "Âge au 31 décembre"


def _code_de_tranche(libelle: str) -> str | None:
    """Le code d'une ligne de l'âge au 31 décembre : ``age_moyen``,
    ``age_moins_50``, ``age_50_55``, ``age_85_plus`` ; aucun pour une autre."""
    if libelle.startswith("Âge moyen"):
        return "age_moyen"
    if (trouve := re.fullmatch(r"Inférieur à (\d+) ans", libelle)):
        return f"age_moins_{trouve.group(1)}"
    if (trouve := re.match(r"Entre (\d+) et (\d+) ans", libelle)):
        return f"age_{trouve.group(1)}_{trouve.group(2)}"
    if (trouve := re.fullmatch(r"Au moins (\d+) ans", libelle)):
        return f"age_{trouve.group(1)}_plus"
    return None


def conditions_selon_l_age(grille: dict[tuple[int, int], float | str]
                           ) -> dict[str, dict[str, dict[str, float]]]:
    """L'effectif et l'âge au 31 décembre des retraités de chaque condition de
    liquidation, et de tous : condition, indicateur, sexe. Les indicateurs :
    ``effectifs``, en milliers ; ``age_moyen``, en années ; et la part de
    chaque tranche d'âge parmi les retraités de la condition, en pour cent,
    une case vide se lisant zéro.

    Les colonnes sont cherchées par le début de leur en-tête, le plus long
    gagnant ; l'effectif à la première occurrence de son libellé, l'âge dans
    les lignes de sa variable. Ce qui est lu se vérifie : les tranches de
    chaque condition font cent, à l'arrondi près ; les conditions comptent les
    retraités de l'ensemble, un sur cent n'en ayant pas ; les deux sexes le
    redonnent.
    """
    derniere_colonne = max(colonne for _, colonne in grille)
    derniere_ligne = max(ligne for ligne, _ in grille)
    colonnes: dict[str, int] = {}
    for colonne in range(3, derniere_colonne + 1):
        entete = " ".join(str(grille.get((0, colonne), "")).split())
        codes = [code for code, debut in COLONNES_CONDITIONS.items()
                 if entete.startswith(debut)]
        if codes:
            code = max(codes, key=lambda c: len(COLONNES_CONDITIONS[c]))
            colonnes.setdefault(code, colonne)
    manquantes = set(COLONNES_CONDITIONS) - set(colonnes)
    if manquantes:
        raise RuntimeError(
            f"feuille {FEUILLE_CONDITIONS!r} : colonnes absentes — "
            f"{', '.join(sorted(manquantes))}")

    valeurs: dict[str, dict[str, dict[str, float]]] = {code: {} for code in colonnes}
    for ligne in range(1, derniere_ligne + 1):
        sexe = SEXES.get(str(grille.get((ligne, 0), "")).strip())
        variable = " ".join(str(grille.get((ligne, 1), "")).split())
        libelle = " ".join(str(grille.get((ligne, 2), "")).split())
        if sexe is None:
            continue
        if libelle.startswith("Effectifs (en milliers)"):
            indicateur = "effectifs"
        elif variable.startswith(VARIABLE_AGE):
            indicateur = _code_de_tranche(libelle)
        else:
            continue
        if indicateur is None:
            continue
        for code, colonne in colonnes.items():
            serie = valeurs[code].setdefault(indicateur, {})
            if sexe in serie:
                continue
            valeur = grille.get((ligne, colonne))
            if isinstance(valeur, (int, float)):
                serie[sexe] = float(valeur)
            elif indicateur not in ("effectifs", "age_moyen") and str(
                    valeur if valeur is not None else "").strip() == "":
                serie[sexe] = 0.0
    tranches = sorted({i for serie in valeurs.values() for i in serie
                       if i.startswith("age_") and i != "age_moyen"})
    manquants = [f"{code}/{indicateur}" for code, serie in valeurs.items()
                 for indicateur in ("effectifs", "age_moyen", *tranches)
                 if len(serie.get(indicateur, {})) < 3]
    if manquants or len(tranches) < 5:
        raise RuntimeError(f"conditions selon l'âge illisibles : "
                           f"{', '.join(manquants) or 'trop peu de tranches'}")

    for code, serie in valeurs.items():
        for sexe in SEXES.values():
            total = sum(serie[tranche][sexe] for tranche in tranches)
            if abs(total - 100.0) > 0.6:
                raise RuntimeError(f"conditions selon l'âge : les tranches de "
                                   f"{code}/{sexe} font {total:g} %")
    for sexe in SEXES.values():
        ensemble = valeurs["ensemble"]["effectifs"][sexe]
        somme = sum(serie["effectifs"][sexe] for code, serie in valeurs.items()
                    if code != "ensemble")
        if not 0.97 * ensemble <= somme <= ensemble + 3.0:
            raise RuntimeError(f"conditions selon l'âge : les conditions comptent "
                               f"{somme:g} milliers de retraités ({sexe}), les "
                               f"effectifs de l'ensemble {ensemble:g}")
    for code, serie in valeurs.items():
        deux = serie["effectifs"]["F"] + serie["effectifs"]["H"]
        if abs(deux - serie["effectifs"]["ensemble"]) > 3.0:
            raise RuntimeError(f"conditions selon l'âge : les effectifs des deux sexes "
                               f"font {deux:g} milliers ({code}), l'ensemble "
                               f"{serie['effectifs']['ensemble']:g}")
    return valeurs


def lire_conditions_selon_l_age(contenu: bytes) -> dict[str, dict[str, dict[str, float]]]:
    """:func:`conditions_selon_l_age`, sur la feuille du classeur."""
    return conditions_selon_l_age(
        feuilles(contenu, (FEUILLE_CONDITIONS,))[FEUILLE_CONDITIONS])


def main() -> int:
    try:
        annee, titre, contenu = classeur_le_plus_recent()
        annee_residents, titre_residents, residents = classeur_le_plus_recent(
            _TITRE_RESIDENTS)
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1
    if annee_residents != annee:
        print(f"DREES : le classeur des résidents est de {annee_residents}, celui de "
              f"tous les retraités de {annee}", file=sys.stderr)
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
        "quintiles_eqcc": lire_quintiles_eqcc(contenu),
        "fichier_residents": titre_residents,
        "quintiles_eqcc_residents": lire_quintiles_eqcc(residents,
                                                        INDICATEURS_EQCC_RESIDENTS,
                                                        VIDES_NULS_EQCC),
        "conditions_selon_l_age_residents": lire_conditions_selon_l_age(residents),
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"EIR {annee} : {len(valeurs)} indicateurs écrits dans {SORTIE}")
    for code, serie in valeurs.items():
        rendu = "  ".join(f"{sexe} {valeur:g}" for sexe, valeur in sorted(serie.items()))
        print(f"  {code:36} {rendu}")
    print(f"  quintiles EQCC : {len(COLONNES_EQCC)} colonnes, "
          f"{len(INDICATEURS_EQCC)} indicateurs, trois sexes")
    print(f"  quintiles EQCC des résidents ({titre_residents}) : "
          f"{len(INDICATEURS_EQCC_RESIDENTS)} indicateurs")
    print(f"  conditions selon l'âge des résidents : "
          f"{len(charge['conditions_selon_l_age_residents'])} colonnes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
