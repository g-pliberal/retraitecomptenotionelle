#!/usr/bin/env python3
"""Recontrôle des données de référence contre les sources téléchargées.

    python scripts/fetch/insee_bdm.py            # dépose les sources
    python scripts/fetch/eurostat_esperance_vie.py
    python scripts/fetch/eurostat_hicp.py

    python scripts/verifier_donnees.py           # confronte, sans rien écrire
    python scripts/verifier_donnees.py --appliquer   # aligne et certifie

C'est ce script — et lui seul — qui a le droit de faire passer une valeur au
niveau ``certifiee``. Une valeur n'est certifiée que si elle a été confrontée
avec succès à un fichier source présent dans ``data/brut/``. Sans fichier
source, le contrôle est signalé comme impossible, jamais comme réussi.

Trois familles de contrôles
---------------------------

1. **Cohérence interne** — continuité des séries, absence de trous, plages
   plausibles. Ne dépend d'aucune source et ne certifie rien.

2. **Certification** — reconstruction de la série depuis le fichier source puis
   confrontation valeur par valeur. C'est le seul contrôle qui certifie.
   ``--appliquer`` aligne alors la série de référence sur la source : les
   valeurs qui divergent sont remplacées, les années absentes sont ajoutées, et
   toutes portent ensuite le niveau ``certifiee``. Les années hors de portée de
   la source ne sont pas touchées.

3. **Vraisemblance** — confrontation de l'inflation 1996-2025 à l'IPCH
   d'Eurostat. Ce contrôle ne certifie rien, et c'est délibéré : l'IPCH
   harmonisé et l'IPC national ne mesurent pas la même chose (traitement des
   remboursements de santé, pondérations, champ des ménages). L'écart atteint
   couramment 0,5 à 0,8 point (2022 : 5,2 % pour l'IPC, 5,9 % pour l'IPCH),
   sans qu'aucune des deux valeurs soit fausse. Le seuil d'alerte est donc fixé
   à 1,5 point, et aucune valeur ne passe au niveau ``certifiee`` par ce biais.

Ce qui reste hors de portée — inflation, salaires et productivité d'avant 1950,
plafond d'avant 2002, espérance de vie à 65 ans d'avant 1986, tables de
quotients, paramètres de régime — est énuméré dans docs/limites.md §1.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Callable

RACINE = Path(__file__).resolve().parents[1]
DONNEES = RACINE / "data"
BRUT = DONNEES / "brut"
REFERENCE = DONNEES / "reference"

#: Première année du fichier des espérances de vie : avant elle, aucune série
#: du dépôt n'en a besoin.
PREMIERE_ANNEE_ESPERANCE = 1946
#: Première année où l'OCDE publie e65. En deçà, personne ne la publie et le
#: dépôt la dérive des quotients observés.
PREMIERE_ANNEE_OCDE = 1960
#: Âge auquel la table doit au moins monter pour qu'une espérance à 65 ans
#: dérivée d'elle ait un sens. Les tables de Vallin et Meslé vont à 104 ans.
AGE_TERMINAL_MINIMAL = 100

#: Dérive cumulée au-delà de laquelle la reconstitution d'avant 1950 mérite
#: d'être reprise. Elle est fixée au double de ce que l'instrument mesure sur la
#: période certifiée : la série des coefficients s'y écarte déjà de 2,4 % de la
#: série mensuelle, et l'on ne saurait exiger d'elle mieux qu'elle ne vaut.
SEUIL_DERIVE_PRIX_ANCIENS = 0.05

#: Seuil d'alerte du contrôle de vraisemblance IPC / IPCH, en points de taux.
#: Fixé à 1,5 point : au-dessous, l'écart s'explique par la différence de
#: méthode entre indice national et indice harmonisé ; au-dessus, il y a
#: vraisemblablement une erreur de saisie.
SEUIL_VRAISEMBLANCE = 0.015

#: Année de chaînage entre l'indice des prix base 1980 (publié jusqu'en 1992)
#: et l'indice base 2015 (publié à partir de 1990). Les deux bases se
#: chevauchent sur 1990-1992 ; on bascule au plus tôt, la base récente étant
#: celle que l'INSEE tient à jour.
ANNEE_CHAINAGE_IPC = 1990

#: Trace de la dernière certification, écrite par ``--appliquer``. Le répertoire
#: data/brut/ n'étant pas versionné, c'est ce fichier qui rend la certification
#: vérifiable après coup : il dit quelle source, quel jour, combien de valeurs.
#:
#: Le jour est écrit DANS chaque fiche de série (``verifiee_le``), à chaque
#: passage du récupérateur, que les valeurs bougent ou non : une série
#: recontrôlée sans changement réécrivait une fiche identique, donc ne laissait
#: aucune trace, et le journal ne savait plus distinguer « recontrôlé hier,
#: inchangé » de « pas regardé depuis un mois ». Le champ global
#: ``dernier_passage_le`` n'est que la date du dernier ``--appliquer``, fût-il
#: partiel : c'est le maximum, et la page Données dit le minimum.
JOURNAL = DONNEES / "derive" / "certification.json"


# ---------------------------------------------------------------------------
# Lecture et écriture des CSV de référence, en préservant leur en-tête
# ---------------------------------------------------------------------------


def _table_reference(nom: str, cle: str, colonne: str) -> dict[float, float]:
    """Une table par génération ou par année, lue dans data/reference/legislation."""
    chemin = REFERENCE / "legislation" / nom
    if not chemin.exists():
        return {}
    return {
        float(ligne[cle]): float(ligne[colonne])
        for ligne in charger_csv(chemin)
    }


def charger_csv(chemin: Path) -> list[dict[str, str]]:
    with chemin.open(encoding="utf-8") as flux:
        lignes = (l for l in flux if not l.lstrip().startswith("#"))
        return list(csv.DictReader(lignes))


def _lire(chemin: Path) -> tuple[list[str], list[str], list[dict[str, str]]]:
    """Renvoie (commentaires d'en-tête, noms de colonnes, lignes)."""
    texte = chemin.read_text(encoding="utf-8").splitlines()
    commentaires = [l for l in texte if l.lstrip().startswith("#")]
    utiles = [l for l in texte if l.strip() and not l.lstrip().startswith("#")]
    lecteur = csv.DictReader(utiles)
    return commentaires, list(lecteur.fieldnames or []), list(lecteur)


def _ecrire(chemin: Path, commentaires: list[str], champs: list[str],
            lignes: list[dict[str, str]]) -> None:
    sortie = ["\n".join(commentaires)] if commentaires else []
    tampon = []
    redacteur = csv.DictWriter(_Collecteur(tampon), fieldnames=champs, lineterminator="\n")
    redacteur.writeheader()
    redacteur.writerows(lignes)
    sortie.append("".join(tampon))
    chemin.write_text("\n".join(sortie), encoding="utf-8")


class _Collecteur:
    """Fichier minimal en mémoire, pour que csv.DictWriter écrive dans une liste."""

    def __init__(self, cible: list[str]) -> None:
        self._cible = cible

    def write(self, texte: str) -> None:
        self._cible.append(texte)


# ---------------------------------------------------------------------------
# Reconstruction des séries depuis les fichiers source
# ---------------------------------------------------------------------------


class SourceAbsente(FileNotFoundError):
    """Le fichier source nécessaire à un contrôle n'a pas été téléchargé."""


def _charge_bdm() -> dict[str, dict]:
    chemin = BRUT / "insee_bdm.json"
    if not chemin.exists():
        raise SourceAbsente(f"{chemin} absent (lancer scripts/fetch/insee_bdm.py)")
    return json.loads(chemin.read_text(encoding="utf-8"))["series"]


def _observations(nom: str) -> dict[str, float]:
    series = _charge_bdm()
    if nom not in series:
        raise SourceAbsente(
            f"série {nom!r} absente de data/brut/insee_bdm.json "
            f"(lancer scripts/fetch/insee_bdm.py --serie {nom})"
        )
    return series[nom]["observations"]


def _variations(indice: dict[str, float]) -> dict[int, float]:
    """Taux de variation annuels d'un indice de niveau."""
    annees = sorted(int(p) for p in indice)
    return {
        courante: indice[str(courante)] / indice[str(precedente)] - 1.0
        for precedente, courante in zip(annees, annees[1:])
        if courante == precedente + 1
    }


def _rapport(numerateur: str, denominateur: str) -> dict[str, float]:
    haut, bas = _observations(numerateur), _observations(denominateur)
    return {p: haut[p] / bas[p] for p in sorted(set(haut) & set(bas))}


def source_inflation() -> dict[tuple, float]:
    """Variation annuelle de l'IPC, indice base 1980 puis base 2015."""
    ancienne = _variations(_observations("ipc_base_1980"))
    recente = _variations(_observations("ipc_base_2015"))
    chainee = {a: v for a, v in ancienne.items() if a <= ANNEE_CHAINAGE_IPC}
    chainee.update({a: v for a, v in recente.items() if a > ANNEE_CHAINAGE_IPC})
    return {(str(a),): v for a, v in sorted(chainee.items())}


def source_salaire_moyen() -> dict[tuple, float]:
    """Variation nominale du salaire moyen par tête.

    SMPT = salaires et traitements bruts (D11) rapportés à l'emploi salarié
    intérieur en personnes physiques — la définition des comptes nationaux.
    """
    variations = _variations(_rapport("salaires_bruts", "emploi_salarie"))
    return {(str(a),): v for a, v in sorted(variations.items())}


def source_masse_salariale() -> dict[tuple, float]:
    """Variation nominale de la masse salariale — l'assiette des cotisations.

    Salaires et traitements bruts (D11, total des branches), en euros courants,
    pris EN NIVEAU et non par tête : c'est le produit du salaire moyen par
    l'emploi salarié, et donc la grandeur dont dépend ce que la répartition
    peut servir. Le même agrégat sert de numérateur au salaire moyen par tête ;
    la différence entre les deux séries est exactement la croissance de
    l'emploi salarié.
    """
    variations = _variations(_observations("salaires_bruts"))
    return {(str(a),): v for a, v in sorted(variations.items())}


def _charge_revenu_mixte() -> dict[int, float]:
    """Revenu mixte brut des ménages, en millions d'euros courants.

    Le tableau économique d'ensemble de Melodi, filtré sur l'opération B3G du
    secteur S14 et sur le niveau. Les filtres sont RELUS dans le fichier : un
    téléchargement fait avec d'autres dimensions porterait le même nom et
    passerait sans cela pour la bonne série.
    """
    chemin = BRUT / "insee_revenu_mixte.json"
    if not chemin.exists():
        raise SourceAbsente(
            f"{chemin} absent (lancer scripts/fetch/insee_revenu_mixte.py)"
        )
    charge = json.loads(chemin.read_text(encoding="utf-8"))
    attendus = {"STO": "B3G", "REF_SECTOR": "S14", "TRANSFORMATION": "N"}
    if charge.get("filtres") != attendus:
        raise SourceAbsente(
            f"{chemin} n'a pas été téléchargé avec les filtres attendus "
            f"{attendus} mais avec {charge.get('filtres')} "
            "(relancer scripts/fetch/insee_revenu_mixte.py)"
        )
    return {
        int(observation["dimensions"]["TIME_PERIOD"]):
            float(observation["measures"]["OBS_VALUE_NIVEAU"]["value"])
        for observation in charge["observations"]
    }


def source_assiette_salaires() -> dict[tuple, float]:
    """Salaires et traitements bruts (D11), EN NIVEAU et en millions d'euros.

    La même série que ``source_masse_salariale``, qui n'en garde que les
    variations. Le niveau est ce qu'il faut pour confronter un TAUX de
    cotisation à ce qui rentre : une variation ne dit pas sur quoi on prélève.
    """
    return {
        (str(annee), "salaires_bruts"): valeur
        for annee, valeur in sorted(
            (int(a), v) for a, v in _observations("salaires_bruts").items()
        )
    }


def source_assiette_revenu_mixte() -> dict[tuple, float]:
    """Revenu mixte brut des ménages (B3G du secteur S14), en millions d'euros.

    L'autre moitié de l'assiette des revenus d'activité : ce sur quoi les
    non-salariés cotisent. Mixte parce que cette grandeur rémunère
    indissociablement le travail de l'entrepreneur individuel et le capital
    qu'il engage — le compte national ne sait pas les séparer, et l'assiette
    sociale non plus.
    """
    return {
        (str(annee), "revenu_mixte"): valeur
        for annee, valeur in sorted(_charge_revenu_mixte().items())
    }


#: Les tranches d'âge retenues dans chacun des deux jeux INSEE, et rien de
#: plus : ce script écrit des tranches, il ne les interpole pas. Le MILIEU
#: qu'on prête à chacune est une décision de modèle, et il n'a donc qu'un seul
#: endroit — ``TRANCHES_SERIE`` et ``TRANCHES_CATEGORIE`` de ``carriere.py``.
TRANCHES_AGE_SERIES = ("Y_LT26", "Y26T30", "Y31T40", "Y41T50", "Y51T60", "Y_GT60")
TRANCHES_AGE_CATEGORIES = ("Y_LT30", "Y30T39", "Y40T49", "Y50T59", "Y_GE60")

#: Les quatre catégories socioprofessionnelles du jeu détaillé, sous le nom que
#: le modèle leur donne.
CATEGORIES_SALAIRE = {"3": "cadre", "4": "profession_intermediaire",
                      "5": "employe", "6": "ouvrier"}


def _charge_profil_salaire(fichier: str, attendus: dict[str, str]) -> list[dict]:
    """Observations d'un des deux jeux de profil salarial, filtres relus."""
    chemin = BRUT / fichier
    if not chemin.exists():
        raise SourceAbsente(
            f"{chemin} absent "
            "(lancer scripts/fetch/insee_profil_salaire_age.py)"
        )
    charge = json.loads(chemin.read_text(encoding="utf-8"))
    if charge.get("filtres") != attendus:
        raise SourceAbsente(
            f"{chemin} n'a pas été téléchargé avec les filtres attendus "
            f"{attendus} mais avec {charge.get('filtres')} "
            "(relancer scripts/fetch/insee_profil_salaire_age.py)"
        )
    return charge["observations"]


def source_profil_salaire_age() -> dict[tuple, float]:
    """Salaire d'une tranche d'âge rapporté au salaire moyen de son année.

    Un RAPPORT, et non un montant : c'est la seule forme qui se transporte
    d'une année à l'autre sans convention de prix, et c'est celle dont le
    modèle a besoin, puisqu'il applique déjà la croissance du salaire moyen.

    Ce profil est AGRÉGÉ, donc impropre à décrire une carrière : il mélange
    l'effet d'âge et un effet de composition — les jeunes sont plus souvent
    dans les catégories les moins payées, si bien que son écart entre les
    bords vaut 0,46 en 2024 quand celui des ouvriers vaut 0,24. Ce qu'on lui
    demande est donc l'ÉVOLUTION de cet écart, qui est le seul endroit où
    l'effet de génération se lit : 1,19 entre 51-60 ans et 26-30 ans en 1962,
    1,47 en 2000, 1,35 en 2024.
    """
    attendus = {
        "DERA_MEASURE": "SALAIRE_NET_EQTP_MENSUEL_MOYEN_EUROS_CONSTANTS",
        "SEX": "_T", "PCS_ESE": "_T", "ACTIVITY": "_T", "QUANTILE": "_T",
        "WKTIME": "FT",
    }
    observations = _charge_profil_salaire(
        "insee_profil_salaire_age.json", attendus)
    par_annee: dict[int, dict[str, float]] = {}
    for observation in observations:
        dimensions = observation["dimensions"]
        valeur = observation["measures"].get("OBS_VALUE_NIVEAU", {}).get("value")
        if valeur is None:
            continue
        annee = int(dimensions["TIME_PERIOD"])
        par_annee.setdefault(annee, {})[dimensions["AGE"]] = float(valeur)

    valeurs: dict[tuple, float] = {}
    for annee in sorted(par_annee):
        moyenne = par_annee[annee].get("_T")
        if not moyenne:
            continue
        for tranche in TRANCHES_AGE_SERIES:
            brut = par_annee[annee].get(tranche)
            if brut is not None:
                valeurs[(str(annee), tranche)] = brut / moyenne
    return valeurs


def source_profil_salaire_categorie() -> dict[tuple, float]:
    """Profil d'âge INTRA-CATÉGORIE, rapporté à la moyenne de la catégorie.

    C'est le profil d'une carrière, et le seul : une personne progresse dans sa
    catégorie, elle ne traverse pas la structure d'emploi. Le jeu détaillé est
    le seul des trois à croiser l'âge et la catégorie — ni la série longue du
    privé ni celle du public ne le font, vérifié —, et il ne porte qu'une année.
    Sa forme est donc supposée stable dans le temps, ce que
    ``docs/limites.md`` dit et que rien ne démontre.
    """
    attendus = {
        "DERA_MEASURE": "SALAIRE_NET_EQTP_MENSUEL_MOYENNE",
        "SEX": "_T", "ACTIVITY": "_T", "NUMBER_EMPL": "_T", "QUANTILE": "_T",
        "WKTIME": "FT",
    }
    observations = _charge_profil_salaire(
        "insee_profil_salaire_categorie.json", attendus)
    par_categorie: dict[str, dict[str, float]] = {}
    for observation in observations:
        dimensions = observation["dimensions"]
        valeur = observation["measures"].get("OBS_VALUE_NIVEAU", {}).get("value")
        code = dimensions["PCS_ESE"]
        if valeur is None or code not in CATEGORIES_SALAIRE:
            continue
        par_categorie.setdefault(code, {})[dimensions["AGE"]] = float(valeur)

    valeurs: dict[tuple, float] = {}
    for code in sorted(par_categorie):
        moyenne = par_categorie[code].get("_T")
        if not moyenne:
            continue
        for tranche in TRANCHES_AGE_CATEGORIES:
            brut = par_categorie[code].get(tranche)
            if brut is not None:
                valeurs[(CATEGORIES_SALAIRE[code], tranche)] = brut / moyenne
    return valeurs


#: Les statuts de la fonction publique retenus, sous le nom que le modèle leur
#: donne. Les trois VERSANTS y figurent aussi — État, territoriale,
#: hospitalière —, et ce sont eux que les affiliations lisent par défaut : leur
#: profil pondère déjà les catégories par leurs effectifs réels, là où deviner
#: la catégorie de chaque affiliation serait réinventer ce que ce fichier vient
#: remplacer.
#:
#: ``PM`` est absent, et volontairement : ce n'est pas « personnels militaires »
#: mais « personnels médicaux », il n'existe que dans l'hospitalière, et il
#: vaut 6 765 € nets par mois. Les militaires ne sont dans aucun de ces jeux.
STATUTS_PUBLIC = {
    "F_A": "public_categorie_a", "F_B": "public_categorie_b",
    "F_C": "public_categorie_c", "NT": "public_non_titulaire",
}
VERSANTS_PUBLIC = {"1": "public_etat", "2": "public_territoriale",
                   "3": "public_hospitaliere"}


def source_profil_salaire_public() -> dict[tuple, float]:
    """Profil d'âge de la fonction publique, par statut et par versant.

    Le seul jeu de l'INSEE à croiser l'âge et le statut — la série longue du
    public ne le fait pas, vérifié — et il ne porte que 2023. Les pentes
    observées de moins de 30 ans à 50-59 ans sont très éloignées de celle du
    privé qu'on leur appliquait : ×1,11 pour un catégorie C et ×1,22 pour un
    catégorie B, contre ×1,30 pour un employé du privé, et ×1,56 pour un
    catégorie A contre ×1,86 pour un cadre.

    Les statuts sont lus tous versants confondus, les versants tous statuts
    confondus : le jeu croise les trois dimensions, mais une carrière n'est pas
    à la fois « catégorie B » et « territoriale » dans le modèle, dont les
    affiliations ne portent que l'une des deux.
    """
    attendus = {
        "DERA_MEASURE": "SALAIRE_NET_EQTP_MENSUEL_MOYENNE",
        "SEX": "_T", "PCS_ESE": "_T", "QUANTILE": "_T", "WKTIME": "FT",
    }
    observations = _charge_profil_salaire(
        "insee_profil_salaire_public.json", attendus)
    par_groupe: dict[str, dict[str, float]] = {}
    for observation in observations:
        dimensions = observation["dimensions"]
        valeur = observation["measures"].get("OBS_VALUE_NIVEAU", {}).get("value")
        if valeur is None:
            continue
        statut = dimensions["CIVILSERVANT_STATUS"]
        versant = dimensions["PUBLIC_LEGAL_FORM"]
        groupe = None
        if versant == "_T" and statut in STATUTS_PUBLIC:
            groupe = STATUTS_PUBLIC[statut]
        elif statut == "_T" and versant in VERSANTS_PUBLIC:
            groupe = VERSANTS_PUBLIC[versant]
        if groupe is not None:
            par_groupe.setdefault(groupe, {})[dimensions["AGE"]] = float(valeur)

    valeurs: dict[tuple, float] = {}
    for groupe in sorted(par_groupe):
        moyenne = par_groupe[groupe].get("_T")
        if not moyenne:
            continue
        for tranche in TRANCHES_AGE_CATEGORIES:
            brut = par_groupe[groupe].get(tranche)
            if brut is not None:
                valeurs[(groupe, tranche)] = brut / moyenne
    return valeurs


#: Les trois tranches d'âge que la France publie dans l'enquête européenne, et
#: les deux qui bornent une carrière. Y30-49 est là pour le contrôle, pas pour
#: la pente.
TRANCHES_SECTEUR = ("Y_LT30", "Y30-49", "Y_GE50")

#: La section qui sert de référence : l'ensemble de l'industrie, de la
#: construction et des services. C'est elle qui vaut un, et à laquelle chaque
#: secteur se rapporte.
SECTION_ENSEMBLE = "B-S"


def source_profil_salaire_secteur() -> dict[tuple, float]:
    """Salaire d'une tranche d'âge rapporté à celui du secteur, par vague.

    L'enquête européenne sur la structure des salaires est la SEULE source qui
    approche les régimes spéciaux : sa section ``D`` est le champ des industries
    électriques et gazières, sa section ``H`` celui où sont la SNCF et la RATP.
    Aucune source française ne ventile le salaire par âge pour ces populations.

    Elle est AGRÉGÉE par secteur, donc impropre à décrire une carrière : aucune
    des sources du dépôt ne croise l'âge, le secteur et la profession —
    vérifié chez Eurostat comme chez l'INSEE. Le modèle ne lui prend donc qu'un
    RAPPORT de pentes, secteur sur ensemble, et ``carriere.py`` dit ce que cela
    suppose.

    Les deux vagues sont gardées l'une et l'autre, et c'est ce qui permet de
    trier : un secteur dont le facteur bouge d'une vague à l'autre n'est que du
    bruit, et ``PROFIL_SECTEUR_PAR_AFFILIATION`` ne le nomme pas.
    """
    chemin = BRUT / "eurostat_profil_salaire_secteur.json"
    if not chemin.exists():
        raise SourceAbsente(
            f"{chemin} absent "
            "(lancer scripts/fetch/eurostat_profil_salaire_secteur.py)"
        )
    charge = json.loads(chemin.read_text(encoding="utf-8"))
    valeurs: dict[tuple, float] = {}
    for vague, cellules in sorted(charge.get("vagues", {}).items()):
        totaux = {cle.split("|")[0]: v for cle, v in cellules.items()
                  if cle.endswith("|TOTAL")}
        for cle, brut in cellules.items():
            section, tranche = cle.split("|")
            if tranche not in TRANCHES_SECTEUR:
                continue
            moyenne = totaux.get(section)
            if moyenne:
                valeurs[(section, vague, tranche)] = brut / moyenne
    return valeurs


def source_pib_nominal() -> dict[tuple, float]:
    """Variation nominale du produit intérieur brut.

    PIB approche produit, prix courant (idbank 011779992). C'est l'assiette de
    la variante italienne de l'indexation des comptes notionnels ; le lissage
    sur cinq ans qu'elle applique est une règle du moteur, pas de la série, et
    ne figure donc pas ici.
    """
    variations = _variations(_observations("pib_nominal"))
    return {(str(a),): v for a, v in sorted(variations.items())}


def source_productivite() -> dict[tuple, float]:
    """Variation réelle de la productivité par tête.

    Valeur ajoutée en volume (prix chaînés) rapportée à l'emploi intérieur
    total en personnes physiques. Le concept est bien celui **par tête** retenu
    par le modèle, et non la productivité horaire — les deux divergent
    fortement après 1982.
    """
    variations = _variations(_rapport("valeur_ajoutee_volume", "emploi_total"))
    return {(str(a),): v for a, v in sorted(variations.items())}


#: Nombre minimal d'observations mensuelles concordantes pour retenir une année.
#:
#: Le plafond est fixé par arrêté pour l'ANNÉE CIVILE : ses douze mois sont
#: égaux par construction, et la dernière année à en avoir connu plusieurs est
#: 1961. Exiger les douze revenait donc à refuser de certifier, onze mois durant,
#: une valeur que le décret a déjà fixée — le plafond de 2026 restait `estimee`
#: alors que l'arrêté du 22 décembre 2025 le porte à 4 005 € par mois, et cette
#: fiabilité sous-évaluée se propageait à tout résultat qui touche au plafond.
#:
#: Trois suffisent donc, à trois conditions : qu'elles concordent — une année
#: dont les mois divergent est écartée plutôt que moyennée —, qu'elles ne soient
#: pas une observation isolée, et que la série couvre l'année DEPUIS JANVIER.
#: Cette dernière condition n'est pas une précaution de principe : la série
#: mensuelle de l'INSEE commence en août 2001, et retenir cette année-là sur ses
#: cinq derniers mois donnait 27 348 € contre les 27 349 € que porte le décret —
#: un euro d'arrondi, mais deux certifications qui se disputent la même ligne à
#: chaque exécution.
MOIS_MINIMAUX_PLAFOND = 3


def source_plafond() -> dict[tuple, float]:
    """Plafond annuel de la Sécurité sociale, à partir du plafond mensuel.

    Le plafond est fixé pour l'année civile : les observations d'une même année
    doivent être identiques, et une année où elles ne le sont pas est écartée
    plutôt que moyennée.
    """
    mensuel = _observations("plafond_mensuel")
    par_annee: dict[int, list[float]] = {}
    for periode, valeur in mensuel.items():
        par_annee.setdefault(int(periode[:4]), []).append(valeur)
    debuts = {int(periode[:4]): periode for periode in sorted(mensuel, reverse=True)}
    return {
        (str(annee),): round(valeurs[0] * 12)
        for annee, valeurs in sorted(par_annee.items())
        if len(valeurs) >= MOIS_MINIMAUX_PLAFOND and len(set(valeurs)) == 1
        and debuts[annee].endswith("-01")
    }


def source_pib_courant() -> dict[tuple, float]:
    """Produit intérieur brut en NIVEAU, prix courants, en millions d'euros.

    Le dépôt certifiait déjà la variation annuelle du PIB, qui suffit à
    l'indexation ; elle ne suffit pas à rapporter une dépense au PIB, ce qui
    demande le niveau. C'est la même série et le même idbank : on ne la
    récupère pas deux fois, on la lit deux fois.
    """
    niveaux = _observations("pib_nominal")
    return {(periode,): valeur for periode, valeur in sorted(niveaux.items())}


def source_dette_publique() -> dict[tuple, float]:
    """Dette des administrations publiques au sens de Maastricht, en part du PIB.

    L'INSEE publie la série en points de PIB et par trimestre ; le quatrième
    trimestre est le stock au 31 décembre rapporté au PIB des quatre derniers
    trimestres, c'est-à-dire la dette annuelle telle qu'elle est notifiée à
    la Commission européenne. Les trois autres trimestres ne sont pas lus : le
    dépôt ne connaît que des années. En FRACTION, comme comptes_retraite.csv,
    pour que les deux s'additionnent sans conversion.
    """
    observations = _observations("dette_publique")
    return {
        (periode[:4],): valeur / 100.0
        for periode, valeur in sorted(observations.items())
        if periode.endswith("-Q4")
    }


def source_courbe_taux_sans_risque() -> dict[tuple, float]:
    """Courbe zéro-coupon des souverains AAA de la zone euro, par maturité.

    Les clés portent la DATE d'observation autant que la maturité : une courbe
    est un instantané, et deux jours ne se mélangent pas. Le fichier de
    référence garde donc les courbes successives, et le modèle lit la plus
    récente.
    """
    brut = _lire_json("bce_courbe_taux.json", "scripts/fetch/bce_courbe_taux.py")
    valeurs: dict[tuple, float] = {}
    for cle, taux in brut["courbe"].items():
        _, jour, maturite = cle.split("|")
        valeurs[(jour, maturite)] = float(taux)
    return dict(sorted(valeurs.items()))


def _lire_json(nom_fichier: str, script: str) -> dict:
    chemin = BRUT / nom_fichier
    if not chemin.exists():
        raise SourceAbsente(f"{chemin} absent (lancer {script})")
    return json.loads(chemin.read_text(encoding="utf-8"))


def _serie_json(nom_fichier: str, script: str) -> dict[str, float]:
    return _lire_json(nom_fichier, script)["serie"]


#: Régimes dont la cotisation se lit ANNÉE PAR ANNÉE dans les barèmes datés
#: d'OpenFisca-France, et la série du fichier brut qui porte chacun. Les
#: salariés agricoles y portent la série du régime général, faute de mieux :
#: c'est vrai depuis 2014, où le II de l'article D. 741-35 du code rural renvoie
#: à l'article D. 242-4, et faux avant — leur employeur payait un point de moins,
#: ce que la lecture du Journal officiel a montré. Ces lignes ne servent donc
#: plus qu'aux années que cette lecture ne couvre pas, d'avant 1980. Les artisans
#: et les commerçants ont chacun leur série jusqu'à l'absorption dans le RSI, qui
#: reprend celle des artisans — identiques depuis l'alignement de 1973 —,
#: puis une cotisation déplafonnée depuis 2014.
TAUX_ANNUELS = (
    # régime, série plafonnée, série déplafonnée, première et dernière année
    ("regime_general", "serie", "serie", 1967, None),
    ("msa_salaries", "serie", "serie", 1967, None),
    ("cancava", "artisans_base_plafonnee", None, 1973, 2005),
    ("organic", "commercants_base_plafonnee", None, 1973, 2005),
    ("rsi", "artisans_base_plafonnee", "independants_base_deplafonnee", 2006, 2017),
)

#: Régimes qui n'ont pas de barème propre et portent celui du régime général :
#: les cultes, dont la cotisation est celle du droit commun sur une assiette
#: forfaitaire, et les caisses de Mayotte et de Saint-Pierre-et-Miquelon, dont
#: les taux sont fixés localement et ne sont pas dans l'index. Ils suivent la
#: série que le dépôt tient pour le régime général — celle qu'il a certifiée
#: depuis 1982 comprise —, et non une transcription qui s'en écarterait ; la
#: SUBSTITUTION reste une décision de modélisation, d'où le niveau `haute`.
TAUX_ALIGNES = (
    ("cavimac", 1979),
    ("cssm_mayotte", 1987),
    ("cps_saint_pierre_et_miquelon", 1987),
)


def source_taux_cotisation_annuels() -> dict[tuple, float]:
    """Les taux de cotisation vieillesse datés d'OpenFisca-France, par régime et par année.

    Les fiches de régime portaient un taux par PÉRIODE LÉGISLATIVE — une moyenne
    de dix à vingt-sept ans, écrite comme telle dans leurs notes —, quand le
    droit a changé ce taux presque chaque année : 8,5 % en 1967, 12,9 % en 1979,
    16,35 % en 1991, 17,87 % en 2024 au régime général. C'est la cotisation qui
    alimente le compte notionnel, et une moyenne de période prête à 1972 le
    taux de 1982. Cette source écrit la série annuelle que le chargeur des
    fiches applique année par année ; la fiche garde sa moyenne, qui ne sert
    plus qu'aux années que la série ne couvre pas — avant 1967 pour le régime
    général, avant 1973 pour les non-salariés.

    Quatre mesures : ``taux_plafonne`` (salarié et employeur, sous plafond),
    ``part_salariale`` (fraction du précédent supportée par le salarié),
    ``taux_deplafonne`` et ``part_salariale_deplafonnee``. Les non-salariés
    n'ont que les taux : ils paient tout, la fiche le sait.

    OpenFisca est une transcription des décrets, pas leur producteur : le
    niveau reste ``haute``, et elle ne touche pas aux lignes que la lecture du
    *Journal officiel* a certifiées — la règle du plafond ancien, où une
    transcription tierce ne peut ni certifier ni décertifier.
    """
    brut = _lire_json("openfisca_cotisations.json",
                      "scripts/fetch/openfisca_cotisations.py")
    independants = brut.get("independants", {})
    libres = _cles_non_certifiees(
        REFERENCE / "regimes" / "taux_cotisation_annuels.csv",
        ("regime", "annee", "mesure"))
    valeurs: dict[tuple, float] = {}
    for regime, plafonnee, deplafonnee, premiere, derniere in TAUX_ANNUELS:
        if plafonnee == "serie":
            for annee, composantes in sorted(brut["serie"].items()):
                if int(annee) < premiere or (derniere and int(annee) > derniere):
                    continue
                total = composantes["salarie_plafonnee"] + composantes["employeur_plafonnee"]
                valeurs[(regime, annee, "taux_plafonne")] = total
                valeurs[(regime, annee, "part_salariale")] = (
                    composantes["salarie_plafonnee"] / total
                )
                total_deplafonne = (composantes["salarie_deplafonnee"]
                                    + composantes["employeur_deplafonnee"])
                valeurs[(regime, annee, "taux_deplafonne")] = total_deplafonne
                valeurs[(regime, annee, "part_salariale_deplafonnee")] = (
                    composantes["salarie_deplafonnee"] / total_deplafonne
                    if total_deplafonne > 0 else 0.0
                )
            continue
        for annee, taux in sorted(independants.get(plafonnee, {}).items()):
            if int(annee) < premiere or (derniere and int(annee) > derniere):
                continue
            valeurs[(regime, annee, "taux_plafonne")] = taux
        if deplafonnee:
            for annee, taux in sorted(independants.get(deplafonnee, {}).items()):
                if int(annee) < premiere or (derniere and int(annee) > derniere):
                    continue
                valeurs[(regime, annee, "taux_deplafonne")] = taux
    # Le fichier n'existe pas encore au tout premier passage : rien n'y est
    # certifié, et tout est donc à écrire.
    if libres:
        valeurs = {cle: v for cle, v in valeurs.items() if cle in libres}
    return valeurs


def source_taux_cotisation_jorf() -> dict[tuple, float]:
    """Les taux de cotisation vieillesse lus dans les textes qui les fixent.

    Régime général depuis 1982 — article 2 du décret n° 81-1013 du 13 novembre
    1981, puis article D. 242-4 du code de la sécurité sociale — et salariés
    agricoles depuis 1980 — article 2 du décret n° 50-444 du 20 avril 1950, puis
    article D. 741-35 du code rural, qui renvoie au premier depuis 2014. Le taux
    retenu est celui en vigueur au 1er JANVIER, comme partout ailleurs dans le
    dépôt.

    Les quinze premières années du régime général, 1967 à 1981, ne sont pas ici,
    et c'est la base qui le dit : l'article 3 du décret n° 67-803 n'y a qu'une
    version, datée de 1967 et portant l'état de 1979. Elles restent transcrites
    d'OpenFisca, au niveau ``haute``.

    Le récupérateur refuse de rendre une série dès qu'un décret du *Journal
    officiel* annonce des taux de cotisation vieillesse de ces régimes sans que
    la chaîne des versions ou une surcharge déclarée l'explique ; la
    certification s'arrête alors avec lui.
    """
    charge = _lire_json("dila_taux_cotisation.json",
                        "scripts/fetch/dila_legi_taux_cotisation.py")
    inexpliques = charge.get("decrets_inexpliques") or []
    if inexpliques:
        raise SourceAbsente(
            f"{len(inexpliques)} décret(s) du JORF touchant ces taux ne sont "
            "expliqués ni par la chaîne des versions ni par une surcharge "
            f"déclarée — le premier est {inexpliques[0]}")
    valeurs: dict[tuple, float] = {}
    for regime, annees in sorted(charge["series"].items()):
        for annee, taux in sorted(annees.items()):
            plafonne = taux["employeur_plafonne"] + taux["salarie_plafonne"]
            deplafonne = taux["employeur_deplafonne"] + taux["salarie_deplafonne"]
            valeurs[(regime, annee, "taux_plafonne")] = plafonne
            valeurs[(regime, annee, "part_salariale")] = (
                taux["salarie_plafonne"] / plafonne if plafonne else 0.0)
            valeurs[(regime, annee, "taux_deplafonne")] = deplafonne
            valeurs[(regime, annee, "part_salariale_deplafonnee")] = (
                taux["salarie_deplafonne"] / deplafonne if deplafonne else 0.0)
    return valeurs


def source_taux_cotisation_alignes() -> dict[tuple, float]:
    """Les régimes qui portent la série du régime général, faute d'en publier une.

    Les cultes, Mayotte et Saint-Pierre-et-Miquelon n'ont pas de barème lisible :
    leurs fiches recopiaient la moyenne du régime général, et cette source leur
    donne sa série ANNÉE PAR ANNÉE, telle que le dépôt la tient — certifiée
    depuis 1982, transcrite avant. Elle la lit dans le fichier de référence
    lui-même, et non chez OpenFisca : deux copies du régime général qui
    divergeraient seraient pire qu'une approximation nommée.

    Niveau ``haute`` : la valeur est celle du régime général, mais la
    SUBSTITUTION est une décision de modélisation, comme l'UNIRS tenant lieu
    d'Arrco avant 1999.
    """
    chemin = REFERENCE / "regimes" / "taux_cotisation_annuels.csv"
    if not chemin.exists():
        return {}
    modele = {
        (ligne["annee"], ligne["mesure"]): float(ligne["valeur"])
        for ligne in charger_csv(chemin) if ligne["regime"] == "regime_general"
    }
    return {
        (regime, annee, mesure): valeur
        for regime, premiere in TAUX_ALIGNES
        for (annee, mesure), valeur in sorted(modele.items())
        if int(annee) >= premiere
    }


#: Première année où la DREES ventile le risque vieillesse-survie dans la
#: nomenclature d'organismes encore en vigueur. De 1981 à 1989 elle en publie
#: une autre — « Régime général de la Sécurité sociale », « Régimes spéciaux »,
#: « Régimes de l'État et des entreprises publiques » — dont les périmètres ne
#: se recoupent pas avec ceux de 1990 : le régime général d'alors inclut ce qui
#: est aujourd'hui réparti entre la Cnav et d'autres organismes, et les régimes
#: complémentaires ne sont pas encore distingués de l'Agirc et de l'Arrco.
#: Personne n'a publié le raccord ; ces neuf années restent donc hors de la
#: ventilation, et seul le total les couvre.
PREMIERE_ANNEE_VENTILATION = 1990

#: Regroupement des organismes des Comptes de la protection sociale en systèmes
#: de retraite lisibles. La DREES ventile par SECTEUR INSTITUTIONNEL — c'est la
#: logique de la comptabilité nationale, non celle des caisses —, si bien que
#: l'Agirc et l'Arrco y sont deux lignes jusqu'en 2017 et une seule depuis, et
#: que la CNRACL, la SNCF, la RATP et les IEG sont réunies sous « Autres régimes
#: spéciaux ». Le regroupement ci-dessous ne fait que nommer ce découpage ; il
#: n'en franchit aucune frontière, et n'invente donc aucun chiffre.
#:
#: L'ordre des entrées est celui de l'affichage : les régimes par répartition
#: d'abord, par masse décroissante, puis ce qui n'en relève pas.
REGIMES_CPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("regime_general", ("Caisse nationale d’assurance vieillesse",)),
    ("agirc_arrco", (
        "Association générale des institutions de retraite des cadres et "
        "association des régimes de retraite complémentaire des salariés",
        "Association des régimes de retraite complémentaire des salariés",
        "Association générale des institutions de retraite des cadres",
    )),
    ("fonction_publique_etat", ("Régimes pour les agents de l'Etat (y compris ex-L)",)),
    ("regimes_speciaux", ("Autres régimes spéciaux",)),
    ("exploitants_agricoles", ("Exploitants agricoles",)),
    ("professions_liberales", ("CNAVPL base complementaire",)),
    ("salaries_agricoles", ("Régime des salariés agricoles",)),
    ("ircantec", (
        "Institution de retraite complémentaire des agents non titulaires de "
        "l’État et des collectivités publiques",
    )),
    ("non_salaries_autres", ("Autres régimes non salariés",)),
    ("repartition_autres", (
        "Autres régimes complémentaires de salariés",
        "Autres fonds spéciaux",
        "Autres organismes du régime général",
        "Caisse nationale d’assurance maladie",
        "Caisse nationale des allocations familiales",
        "Caisse nationale de solidarité pour l'autonomie",
        "UNEDIC et autres régimes",
        "ODAC",
    )),
    ("solidarite_etat", (
        "Régime d'intervention sociale de l'État",
        "Régime des crédits d'impôts de l'État",
    )),
    ("aide_sociale_locale", (
        "Régime d'intervention sociale des départements",
        "Régime d'intervention sociale des régions",
    )),
    ("supplementaire", (
        "Autres regimes privés",
        "Entreprises d'assurance - contrats collectifs",
        "Institutions de prévoyance - contrats collectifs",
        "Institutions de retraite supplémentaire",
        "Mutuelles - contrats collectifs",
        "Organismes de retraite professionnelle supplémentaire - contrats collectifs",
        "Régime additionnel de la fonction publique",
    )),
)


#: Dernière année que l'INSEE tient pour OBSERVÉE dans son classeur de
#: projections : « estimations de population jusqu'en 2023 ; projections de
#: population 2026 à partir de 2024 », dit son pied de tableau. Le critère 2 du
#: manifeste — l'observé prime sur le projeté — passe exactement là.
DERNIERE_ANNEE_POPULATION_OBSERVEE = 2023


def _population() -> dict:
    return _lire_json("insee_projections_population.json",
                      "scripts/fetch/insee_projections_population.py")


def source_population_par_age() -> dict[tuple, float]:
    """Population au 1er janvier par âge, de 50 à 104 ans, 1962-2070.

    C'est la pièce qui manquait au dépôt pour passer du droit individuel au
    coût collectif : sans elle, il fallait supposer une population
    stationnaire, c'est-à-dire toutes les générations de même taille — ce que
    le baby-boom dément d'un tiers.

    Les années projetées entrent au niveau `estimee`, qui se propage jusqu'au
    résultat affiché : une projection ne se fait jamais passer pour une
    observation, fût-elle publiée par le producteur de l'observation.
    """
    return {
        tuple(cle.split("|")): effectif
        for cle, effectif in sorted(_population()["par_age"].items())
    }


def source_population_active() -> dict[tuple, float]:
    """Population des 20-64 ans, 1962-2070 — le dénominateur du PIB projeté.

    Elle ne sert à compter aucun retraité. Elle sert à projeter la richesse
    produite : l'hypothèse d'emploi constant que porte
    `hypotheses_projection.yaml` est neutre pour l'indexation des comptes, et ne
    l'est pas du tout pour une part de PIB, dont elle gonflerait le
    dénominateur de 12 % en 2070.
    """
    return {
        (annee,): effectif
        for annee, effectif in sorted(_population()["actifs_20_64"].items())
    }


def _cps() -> dict:
    return _lire_json("drees_cps.json", "scripts/fetch/drees_cps.py")


def source_depenses_retraite() -> dict[tuple, float]:
    """Prestations du risque vieillesse-survie, tous régimes, en millions d'euros.

    C'est l'agrégat que la DREES publie sans interruption depuis 1959, et la
    seule série longue française de dépenses de retraite qui vienne de son
    producteur. Il est plus large que « les retraites » : il porte aussi le
    minimum vieillesse, les prestations de dépendance des personnes âgées et la
    retraite supplémentaire. La ventilation par régime dit de combien, et la
    page « Coût » le montre.
    """
    return {(annee,): valeur for annee, valeur in sorted(_cps()["total"].items())}



def source_prestations_non_contributives() -> dict[tuple, float]:
    """Les prestations non contributives que les comptes de la protection
    sociale isolent, poste par poste et tous régimes.

    C'EST CE QUI MANQUAIT À LA PAGE « AVANTAGES ». Le modèle mesure un avantage
    en refaisant la pension sans lui, sur treize carrières types — et cette
    grille n'est pas une population : elle n'a aucun cas type de trois enfants,
    si bien que la majoration pour enfants y valait ZÉRO quand les comptes en
    portent près de huit milliards. Là où ces postes existent, ils remplacent la
    ligne calculée au lieu de la compléter : le producteur prime sur le modèle,
    et c'est le critère 1 de `data/sources.yaml`.

    Cinq lignes de l'inventaire n'avaient AUCUN chiffre et en ont un : la
    majoration pour tierce personne, celle pour conjoint à charge, celle des
    pensions de réversion, les pensions d'orphelin et les pensions servies au
    titre de l'inaptitude ou de l'invalidité.

    LA FENÊTRE EST COURTE, et c'est la limite de cette source : la DREES ne
    publie ce grain qu'à partir de 2020, quand le total du risque remonte à
    1959. Une série de cinq ans n'est pas une histoire ; elle est un ordre de
    grandeur, et la page le dit.
    """
    prestations = _cps().get("prestations") or {}
    if not prestations:
        raise SourceAbsente(
            "data/brut/drees_cps.json ne porte pas les prestations non "
            "contributives — relancer scripts/fetch/drees_cps.py"
        )
    return {
        (annee, poste): valeur
        for poste, serie in sorted(prestations.items())
        for annee, valeur in sorted(serie.items())
    }


def source_depenses_retraite_regimes() -> dict[tuple, float]:
    """Le même risque, ventilé par système, à partir de 1990.

    Les organismes que la DREES distingue sont regroupés selon ``REGIMES_CPS``.
    Le contrôle qui compte est celui de la somme : elle doit rendre le total,
    à l'euro près, chaque année — c'est ``controle_ventilation_depenses`` qui
    l'exerce.
    """
    par_systeme: dict[tuple, float] = {}
    regimes = _cps()["regimes"]
    for code, organismes in REGIMES_CPS:
        for organisme in organismes:
            for annee, valeur in regimes.get(organisme, {}).items():
                if int(annee) < PREMIERE_ANNEE_VENTILATION:
                    continue
                cle = (annee, code)
                par_systeme[cle] = par_systeme.get(cle, 0.0) + valeur
    return dict(sorted(par_systeme.items()))


#: Postes de la structure des ressources du système de retraite, du libellé que
#: le COR leur donne au code que le dépôt leur donne. Le libellé change de
#: ponctuation d'un rapport à l'autre ; il est donc comparé sans accents, replié
#: sur ses espaces, et sur son DÉBUT — c'est ce que fait ``_code_poste``.
POSTES_RESSOURCES: tuple[tuple[str, str], ...] = (
    ("cotisations", "cotisations sociales hors contribution d'equilibre"),
    ("contribution_equilibre_etat", "contribution d'equilibre au regime de la fpe"),
    ("impots_et_taxes", "itaf et prises en charge etat"),
    ("subventions_equilibre", "subventions d'equilibre versees par l'etat"),
    ("transferts", "transferts depuis organismes exterieurs"),
    ("autres_produits", "autres produits"),
)


def _cor_comptes() -> dict:
    return _lire_json("cor_comptes_retraite.json",
                      "scripts/fetch/cor_comptes_retraite.py")


def _sans_accents(texte: str) -> str:
    plie = unicodedata.normalize("NFD", texte)
    plie = "".join(c for c in plie if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", plie).strip().lower()


def _code_poste(libelle: str) -> str | None:
    plie = _sans_accents(libelle)
    for code, attendu in POSTES_RESSOURCES:
        if plie.startswith(attendu):
            return code
    return None


def _comptes_retraite(marqueur: str) -> dict[tuple, float]:
    """Dépenses et ressources du système de retraite, en part de PIB.

    ``marqueur`` vaut ``observe`` — les rapports à la Commission des comptes de
    la Sécurité sociale, consolidés par le COR — ou ``projete``, le scénario de
    référence de son dernier rapport. Les deux ne peuvent pas porter le même
    niveau de fiabilité : c'est le critère 2 du manifeste, et la frontière est
    datée par le producteur lui-même, qui marque ses colonnes.
    """
    comptes = _cor_comptes()["comptes"]
    valeurs: dict[tuple, float] = {}
    for poste in ("depenses", "ressources"):
        for annee, part in comptes[poste][marqueur].items():
            valeurs[(annee, poste)] = part
    return dict(sorted(valeurs.items()))


def source_comptes_retraite() -> dict[tuple, float]:
    """Le compte observé du système de retraite, 2002 à la dernière année connue."""
    return _comptes_retraite("observe")


def source_comptes_retraite_projetes() -> dict[tuple, float]:
    """Le même compte, projeté par le COR jusqu'à son horizon."""
    return _comptes_retraite("projete")


def source_structure_ressources() -> dict[tuple, float]:
    """Part de chaque poste dans les ressources du système de retraite.

    Elle dit ce que « ressources » contient : deux tiers de cotisations, mais
    aussi la contribution d'équilibre que l'État verse au régime de ses propres
    fonctionnaires, des impôts affectés et des transferts. Un système en comptes
    notionnels n'est pas financé par la même chose que ces quatre postes-là, et
    c'est ce qui borne la lecture du coefficient d'équilibre.
    """
    valeurs: dict[tuple, float] = {}
    for libelle, serie in _cor_comptes()["structure"].items():
        code = _code_poste(libelle)
        if code is None:
            continue
        for annee, part in serie.items():
            valeurs[(annee, code)] = part
    return dict(sorted(valeurs.items()))


#: Ce que le COR appelle chaque régime dans son classeur par régime, et le code
#: de caisse que le dépôt emploie. Le FSV n'y est pas : ce n'est pas un régime,
#: et sa feuille porte DEUX tableaux de financement dont les parts somment à 2.
#: La FPE est d'un seul tenant chez le COR, là où le dépôt sépare les civils
#: des militaires : on garde le bloc sous un code propre plutôt que de répartir
#: au jugé.
REGIMES_COR: dict[str, str] = {
    "Agirc-Arrco": "agirc_arrco",
    "BDF": "banque_de_france",
    "CANSSM": "canssm",
    "CNAV": "cnav",
    "CNAVPL_RB": "cnavpl",
    "CNAVPL_RC": "cnavpl_complementaire",
    "CNBF": "cnbf",
    "CNIEG": "cnieg",
    "CNRACL": "cnracl",
    "CPRPF": "sncf",
    "CRPCEN": "crpcen",
    "CRPNPAC": "crpnpac",
    "ENIM": "enim",
    "FPE": "fonction_publique_etat",
    "FSPOEIE": "fspoeie",
    "IRCANTEC": "ircantec",
    "MSA_NSA_RB": "msa_exploitants",
    "MSA_NSA_RCO": "msa_exploitants_complementaire",
    "MSA_SA": "msa_salaries",
    "RAFP": "erafp",
    "RATP": "ratp",
    "RCI": "rci_complementaire",
}

#: Les vingt-cinq libellés du bloc « Répartition du financement » ramenés à huit
#: postes. Les cinq premiers codes sont ceux de
#: ``structure_ressources_retraite.csv``, pour que l'agrégat et le détail par
#: régime se lisent avec le même vocabulaire ; les trois derniers n'existent
#: qu'ici, la ventilation par régime étant plus fine que celle du système.
POSTES_FINANCEMENT: dict[str, str] = {
    "Cotisations totales": "cotisations",
    "Cotisations salariés": "cotisations",
    "Cotisations patronales (DSPNR et DSF)": "cotisations",
    "Cotisations salariés et employeurs (opérateurs de l'État)": "cotisations",
    "Contribution d'équilibre de l'État": "contribution_equilibre_etat",
    "Contribution d'équilibre": "contribution_equilibre_etat",
    "Subvention d'équilibre": "subventions_equilibre",
    "ITAF et prises en charge État": "impots_et_taxes",
    "ITAF": "impots_et_taxes",
    "CTA (Itaf et prise en charge État)": "impots_et_taxes",
    "CSG": "impots_et_taxes",
    "Compensation démographique": "compensation_demographique",
    "Prises en charge FSV": "transferts",
    "Transferts entre organismes (externes)": "transferts",
    "Transferts entre organismes (internes)": "transferts",
    "Transferts externes (Cnaf)": "transferts",
    "Pec Aspa": "transferts",
    "Pec majo de pensions": "transferts",
    "Pec Mico": "transferts",
    "Pec cot chômage RB": "transferts",
    "Pec cot chômage RC": "transferts",
    "Autres pec cot": "transferts",
    "Produits de gestion, financiers": "autres_produits",
    "Produits de gestion, etc.": "autres_produits",
    "Besoin de financement": "besoin_de_financement",
}


def _cor_regimes() -> dict:
    return _lire_json("cor_regimes.json", "scripts/fetch/cor_regimes.py")


def source_structure_financement_regimes() -> dict[tuple, float]:
    """Qui finance chaque régime, poste par poste, de 2010 à 2070.

    C'est le détail de ce que ``structure_ressources_retraite.csv`` ne dit que
    pour le système entier. La question à laquelle il répond est celle que la
    page « Coût » ne sait pas poser : un scénario qui remplace tous les taux
    par 18 % déplace-t-il une charge vers l'État ou vers les caisses ? La
    réponse n'est pas la même selon le régime — l'État finance 86 % de la
    fonction publique d'État par sa contribution d'équilibre, et 61 % de la
    SNCF par une subvention, quand la CNRACL ne reçoit rien de lui et porte un
    besoin de financement que personne ne couvre.

    LES PARTS NE SOMMENT PAS TOUJOURS À UN, et on ne les normalise pas. Sur les
    134 couples (régime, année), 100 somment à un à un millième près ; les
    autres s'en écartent jusqu'à onze pour cent — l'Ircantec de 2010, dont les
    produits financiers pèsent 17,7 %, et la CNRACL de 2010 et 2023. C'est ce
    que le classeur publie ; corriger en silence reviendrait à inventer.
    """
    valeurs: dict[tuple, float] = {}
    for ligne in _cor_regimes()["valeurs"]:
        if "Répartition du financement" not in ligne["bloc"]:
            continue
        regime = REGIMES_COR.get(ligne["regime"])
        poste = POSTES_FINANCEMENT.get(ligne["serie"])
        if regime is None or poste is None:
            continue
        cle = (str(ligne["annee"]), regime, poste)
        valeurs[cle] = valeurs.get(cle, 0.0) + ligne["valeur"]
    return dict(sorted(valeurs.items()))


#: Les deux blocs du classeur du COR qui portent les effectifs de cotisants, et
#: l'unité que chacun annonce. Le classeur écrit « en millions » sur dix-sept
#: feuilles et « en milliers » sur trois — CRPCEN, CRPNPAC, FSPOEIE —, et la
#: série est rendue en PERSONNES, pour qu'un lecteur n'ait pas à savoir cela.
BLOCS_COTISANTS_COR: dict[str, float] = {
    "Effectifs de cotisants en millions": 1e6,
    "Effectifs de cotisants en milliers": 1e3,
}


def source_cotisants_regimes() -> dict[tuple, float]:
    """Les cotisants de chaque régime, observés puis projetés, 2010-2070.

    C'est la série que la page « Coût » n'avait pas : le poids d'un cas type
    parmi les COTISANTS y était celui qu'il a parmi les RETRAITÉS de sa caisse,
    faute de mieux, et ``limites.md`` disait que cette approximation
    surreprésente les régimes qui s'éteignent. Le classeur du COR est la seule
    source publique qui donne les cotisants des treize caisses des cas types à
    la même maille, l'Ircantec et le RCI compris, et qui les PROJETTE : la
    CNIEG y tombe de 136 287 cotisants en 2023 à 51 en 2070, la SNCF à zéro,
    ce qu'aucune reconduction d'effectifs de retraités ne saurait imiter.

    Seule la ligne « Ensemble » est retenue ; le classeur ventile aussi par
    sexe, et la pondération n'en a pas l'usage. Le régime, le bloc et la
    série sont ceux du fichier brut ; rien n'est complété : l'année de départ
    varie d'une feuille à l'autre — 2010 le plus souvent, 2015 pour la FPE,
    2019 pour le RCI, 2023 pour la CNRACL et la CNBF — et une absence reste
    une absence. La fonction publique d'État est d'un seul tenant, civils et
    militaires confondus, comme partout dans ce classeur ; le partage est une
    décision du modèle, écrite dans ``donnees/cotisants.py``.
    """
    valeurs: dict[tuple, float] = {}
    for ligne in _cor_regimes()["valeurs"]:
        facteur = BLOCS_COTISANTS_COR.get(ligne["bloc"])
        if facteur is None or ligne["serie"] != "Ensemble":
            continue
        regime = REGIMES_COR.get(ligne["regime"])
        if regime is None:
            continue
        valeurs[(str(ligne["annee"]), regime)] = ligne["valeur"] * facteur
    return dict(sorted(valeurs.items()))


#: Les trois blocs du classeur du COR qui portent la ventilation d'une masse de
#: pensions. Le troisième sert de FILET : dix des vingt-deux régimes ne publient
#: pas leur droit dérivé à part, et la différence entre la masse de prestations
#: et le droit direct le rend, à ceci près qu'elle porte aussi le petit résidu
#: de prestations qui n'est ni l'un ni l'autre — 0,3 % des prestations chez les
#: douze régimes où les trois blocs permettent de le mesurer.
BLOCS_MASSES_COR: dict[str, str] = {
    "direct": "Masse de pensions de droit direct en milliards d'euros 2023",
    "derive": "Masse de pensions de droit dérivé en milliards d'euros 2023",
    "prestations": "Masse de prestations en milliards d'euros 2023",
}

#: Le seul régime du classeur que le périmètre du système de retraite exclut :
#: le RAFP est de la capitalisation, et ``equilibre.py`` le dit déjà de
#: l'agrégat. Le FSV, lui, n'a pas de masse de pensions à ventiler.
HORS_PERIMETRE_MASSES: frozenset[str] = frozenset({"RAFP", "FSV"})


def source_part_droits_derives() -> dict[tuple, float]:
    """La part des pensions de RÉVERSION dans la masse versée, 2010-2070.

    Elle répond à une question que le modèle posait mal. Le rapport de masses
    par lequel ``cout.py`` fait réagir la dépense est celui des droits DIRECTS
    des cas types ; la base à laquelle il s'applique, elle, porte les droits
    dérivés — un huitième de la masse en 2010, un dix-huitième en 2070. Sans
    cette part, le modèle recalculait à la baisse une réversion qu'il ne
    calcule pas.

    CONSTRUITE, ET NON LUE TELLE QUELLE. Douze des vingt-deux régimes du
    classeur publient leur droit dérivé à part ; pour les dix autres — dont la
    fonction publique d'État et la CNRACL, qui pèsent — c'est la différence
    entre la masse de prestations et le droit direct, ce qui l'augmente du
    résidu décrit sous ``BLOCS_MASSES_COR``. Le RAFP est écarté, le périmètre
    du système de retraite excluant la capitalisation.

    CONTRÔLÉE CHEZ UN AUTRE PRODUCTEUR, ET C'EST LE POINT FORT DE CETTE SÉRIE.
    Les Comptes de la protection sociale de la DREES ventilent les pensions en
    droit direct (poste ``E11-21.1``) et droit dérivé (``E11-22.1``) depuis
    2020. Deux producteurs, deux périmètres, deux nomenclatures : sur les cinq
    années communes, les parts s'écartent de 0,06 point au plus et de 0,01
    point deux fois. ``controle_part_droits_derives`` l'exerce à chaque
    vérification.
    """
    masses: dict[int, dict[str, float]] = {}
    for ligne in _cor_regimes()["valeurs"]:
        if ligne["regime"] in HORS_PERIMETRE_MASSES:
            continue
        for cle, bloc in BLOCS_MASSES_COR.items():
            if ligne["bloc"] == bloc:
                par_regime = masses.setdefault(ligne["annee"], {})
                par_regime[f"{ligne['regime']}|{cle}"] = ligne["valeur"]
    parts: dict[tuple, float] = {}
    for annee, valeurs in sorted(masses.items()):
        regimes = {nom.split("|", 1)[0] for nom in valeurs}
        derive = prestations = 0.0
        for regime in regimes:
            presta = valeurs.get(f"{regime}|prestations")
            direct = valeurs.get(f"{regime}|direct")
            if presta is None or direct is None:
                continue
            prestations += presta
            derive += valeurs.get(f"{regime}|derive", presta - direct)
        if prestations > 0.0:
            parts[(str(annee),)] = derive / prestations
    return parts


#: Les deux sous-postes du risque vieillesse-survie que la DREES publie depuis
#: 2020, et la catégorie du dépôt qu'ils portent.
POSTES_PENSIONS_CPS: dict[str, str] = {
    "E11-21.1": "direct",
    "E11-22.1": "derive",
}


def source_pensions_droits() -> dict[tuple, float]:
    """Les pensions de droit direct et de droit dérivé, en millions d'euros.

    C'est le producteur de la dépense qui ventile lui-même sa dépense, et c'est
    donc la ventilation la mieux établie qui existe. Elle est courte — la DREES
    ne publie ces deux sous-postes que depuis 2020, là où le risque entier
    remonte à 1959 — et c'est pour cela qu'elle ne sert pas de série au modèle :
    elle CONTRÔLE ``part_droits_derives.csv``, qui, lui, couvre 2010-2070.

    La somme des deux vaut 401,4 milliards en 2024, contre 426,7 pour le risque
    vieillesse-survie tout entier : l'écart est le minimum vieillesse, les
    prestations de dépendance et la retraite supplémentaire, que le poste large
    porte aussi.
    """
    pensions = _cps()["pensions"]
    valeurs: dict[tuple, float] = {}
    for code, categorie in POSTES_PENSIONS_CPS.items():
        for annee, montant in pensions.get(code, {}).items():
            valeurs[(str(annee), categorie)] = montant
    return dict(sorted(valeurs.items()))


#: Postes de la ventilation des transferts, tels que ``ccss_transferts_retraite.py``
#: les écrit : deux lignes de la CNAF, deux de l'Unédic, deux du fonds de
#: solidarité vieillesse.
POSTES_TRANSFERTS: tuple[str, ...] = (
    "cnaf_avpf", "cnaf_majorations", "unedic_agirc_arrco", "unedic_ircantec",
    "fsv_cotisations", "fsv_prestations",
)


def _ccss_transferts() -> dict:
    return _lire_json("ccss_transferts_retraite.json",
                      "scripts/fetch/ccss_transferts_retraite.py")


def source_transferts_retraite() -> dict[tuple, float]:
    """Ce que la CNAF et l'Unédic versent à la retraite, en millions d'euros.

    Lu du côté de celui qui paie, dans les rapports à la Commission des comptes
    de la Sécurité sociale : la fiche de la CNAF pour l'AVPF et les majorations
    pour enfants, celles de l'Agirc-Arrco et de l'Ircantec pour les points de
    retraite complémentaire des chômeurs. C'est la part du poste « transferts »
    du COR que le compte notionnel ne peut pas supposer acquise, puisqu'il
    supprime les droits qu'elle finance.
    """
    valeurs: dict[tuple, float] = {}
    for poste in POSTES_TRANSFERTS:
        for annee, montant in _ccss_transferts()["series"].get(poste, {}).items():
            valeurs[(annee, poste)] = montant
    return dict(sorted(valeurs.items()))


def _eacr() -> dict:
    return _lire_json("drees_eacr.json", "scripts/fetch/drees_eacr.py")


#: Caisses de l'EACR, du code que la DREES leur donne au nom que ce dépôt leur
#: donne. Deux raisons de ne pas garder le code brut : il ne dit rien à la
#: lecture, et la DREES RENUMÉROTE — la Cnav porte 0010 jusqu'en 2019 puis 0015,
#: sur un champ légèrement plus large (13,80 contre 13,96 million en 2019, seule
#: année où les deux coexistent). Les deux codes font une seule série, et là où
#: ils se recouvrent c'est le PLUS RÉCENT qui l'emporte : la DREES a cessé de
#: publier l'ancien, et le nouveau est celui qu'elle prolonge.
CAISSES_EACR: tuple[tuple[str, str], ...] = (
    ("0000", "tous_regimes"),
    ("0010", "cnav"),
    ("0015", "cnav"),
    ("0012", "fonction_publique_etat_civile"),
    ("0013", "fonction_publique_etat_militaire"),
    ("0021", "msa_salaries"),
    ("0022", "msa_exploitants"),
    ("0023", "msa_exploitants_complementaire"),
    ("0032", "cnracl"),
    ("0033", "fspoeie"),
    ("0043", "rci_complementaire"),
    ("0060", "sncf"),
    ("0061", "sncf_coordination"),
    ("0070", "enim"),
    ("0080", "canssm"),
    ("0090", "cavimac"),
    ("0100", "cnieg"),
    ("0300", "ratp"),
    ("0301", "ratp_coordination"),
    ("0500", "crpcen"),
    ("0600", "banque_de_france"),
    ("1000", "ircantec"),
    ("2100", "cnavpl"),
    ("2200", "cnavpl_complementaire"),
    ("2201", "cnbf"),
    ("2202", "cnbf_complementaire"),
    ("3000", "erafp"),
    ("5600", "agirc_arrco"),
)


def source_effectifs_retraites() -> dict[tuple, float]:
    """Effectifs de retraités de droit direct, caisse par caisse et année par année.

    Le dénombrement exhaustif de l'enquête annuelle auprès des caisses de
    retraite. Il sert à PONDÉRER les cas types de la page « Coût » : sans lui,
    l'agent de conduite pèse ce que pèse le salarié au salaire moyen.

    Une caisse absente de ``CAISSES_EACR`` ferait échouer le contrôle plutôt que
    de disparaître en silence : la DREES ajoute des caisses d'une campagne à
    l'autre — la Cavimac est apparue en 2023 —, et une série qu'on ne nomme pas
    est une série qu'on ne voit pas.
    """
    effectifs = _eacr()["effectifs"]
    inconnues = set(effectifs) - {code for code, _ in CAISSES_EACR}
    if inconnues:
        raise SourceAbsente(
            "caisses EACR absentes de CAISSES_EACR : " + ", ".join(sorted(inconnues))
        )
    par_caisse: dict[tuple, tuple[str, float]] = {}
    for code, nom in CAISSES_EACR:
        for annee, valeur in effectifs.get(code, {}).items():
            cle = (annee, nom)
            if code >= par_caisse.get(cle, ("", 0.0))[0]:
                par_caisse[cle] = (code, valeur)
    return {cle: valeur for cle, (_, valeur) in par_caisse.items()}


def source_droits_derives() -> dict[tuple, float]:
    """Masse des pensions de réversion, caisse par caisse et année par année.

    LA SEULE LIGNE DE L'INVENTAIRE DES AVANTAGES NON CONTRIBUTIFS QUI SE LISE
    AU LIEU DE SE CALCULER, et de très loin la plus lourde. Le modèle décrit
    une carrière, pas un ménage : il n'a ni conjoint, ni date de décès, ni
    ressources du survivant, et ne saura donc jamais produire une réversion. La
    DREES, elle, la dénombre caisse par caisse depuis 2004.

    LA MASSE EST UN PRODUIT, et chacun de ses deux termes vient d'une cellule
    différente du même tableau : le NOMBRE de bénéficiaires d'un droit dérivé
    (champ ``ddert``) et le MONTANT MENSUEL MOYEN de ce droit-là (colonne
    ``m2``). Douze mois plus tard, on a des euros.

    DEUX PIÈGES, ET ILS COÛTENT CHER.

    Le premier est la colonne. ``mont`` porte la pension TOTALE du
    bénéficiaire, droit direct compris ; ``m2`` la seule part dérivée. Prendre
    la première doublerait la masse — 745,60 € contre 326,70 € à la Cnav en
    2020. Le classeur se contrôle d'ailleurs lui-même : la moyenne des ``m2``
    de ``dders`` (dérivé seul) et de ``cumd`` (cumul des deux), pondérée par
    leurs effectifs, vaut exactement le ``m2`` de ``ddert``.

    Le second est la somme des caisses. Un polypensionné touche une réversion à
    la Cnav ET à l'Agirc-Arrco : la somme des effectifs compte deux fois la
    même veuve — 8,5 millions de bénéficiaires au lieu de 4,4. Les MASSES, en
    revanche, s'additionnent sans double compte, puisque chaque caisse verse la
    sienne. La ligne ``tous_regimes`` (code 0000) est la seule qui compte des
    PERSONNES, et c'est elle que le modèle lit ; les caisses ne sont là que
    pour la ventilation, et leur somme la recoupe à 2 % près.
    """
    charge = _eacr().get("droits_derives") or {}
    series = charge.get("series") or {}
    if not series:
        raise SourceAbsente(
            "data/brut/drees_eacr.json ne porte pas les droits dérivés — "
            "relancer scripts/fetch/drees_eacr.py"
        )
    inconnues = set(series) - {code for code, _ in CAISSES_EACR}
    if inconnues:
        raise SourceAbsente(
            "caisses EACR absentes de CAISSES_EACR : " + ", ".join(sorted(inconnues))
        )
    par_caisse: dict[tuple, tuple[str, float]] = {}
    for code, nom in CAISSES_EACR:
        for annee, (beneficiaires, montant) in series.get(code, {}).items():
            cle = (annee, nom)
            # En millions d'euros, comme toutes les masses du dépôt.
            masse = beneficiaires * montant * 12.0 / 1e6
            if code >= par_caisse.get(cle, ("", 0.0))[0]:
                par_caisse[cle] = (code, masse)
    return {cle: valeur for cle, (_, valeur) in par_caisse.items()}


def source_distribution_pensions() -> dict[tuple, float]:
    """Part des retraités par tranche de cent euros de pension brute mensuelle.

    L'échantillon interrégimes de retraités, seule source française qui dise
    non pas la moyenne d'un régime mais la RÉPARTITION des pensions
    individuelles. Elle sert à chiffrer la garantie vieillesse du scénario 6,
    qui est une allocation différentielle : son coût est celui de la queue
    basse de cette distribution, et ne se lit sur aucun cas type.
    """
    charge = _lire_json(
        "drees_distribution_pensions.json",
        "scripts/fetch/drees_distribution_pensions.py",
    )
    # Le millésime de l'EIR est une CLÉ et non une note d'en-tête : les pensions
    # d'une distribution sont dans les euros de son année, et l'enquête paraît
    # tous les quatre ans. Une campagne nouvelle ajoutera ses lignes sans
    # effacer celles de la précédente.
    annee = str(charge["millesime"])
    return {
        (annee, borne, sexe): part
        for sexe, serie in charge["parts"].items()
        for borne, part in serie.items()
    }


def source_esperances() -> dict[tuple, float]:
    """Espérances de vie : e0 et e60 par l'INSEE, e65 par l'OCDE.

    L'INSEE publie e0, e1, e20, e40 et e60 depuis 1946, **jamais e65** — dont la
    calibration a pourtant besoin pour fixer la pente de la force de mortalité.
    C'est la seule raison pour laquelle une donnée française transite ici par
    l'OCDE, qui la publie depuis 1960 et la tient de l'INSEE. Eurostat la publie
    aussi mais seulement depuis 1986 : elle sert de contrôle croisé.
    """
    valeurs: dict[tuple, float] = {}
    for mesure in ("e0", "e60"):
        for sexe in ("H", "F"):
            for periode, valeur in _observations(f"{mesure}_{sexe}").items():
                valeurs[(periode, sexe, mesure)] = valeur

    ocde = _serie_json("oecd_esperance_vie.json", "scripts/fetch/oecd_esperance_vie.py")
    for cle, valeur in ocde.items():
        annee, sexe, mesure = cle.split("|")
        if mesure == "e65":
            valeurs[(annee, sexe, mesure)] = valeur
    return dict(sorted(valeurs.items()))


def source_esperance_65_derivee() -> dict[tuple, float]:
    """Espérance de vie à 65 ans d'avant 1960, dérivée des quotients observés.

    L'OCDE ne remonte pas plus haut, et l'INSEE ne publie jamais e65 : ces
    années restaient saisies depuis les tables TD/TV, et les années qu'aucune
    saisie ne couvrait — 1947 à 1949, 1951 à 1959 — étaient simplement
    interpolées. Or le dépôt a mieux depuis qu'il porte les tables de Vallin et
    Meslé : **les quotients du moment eux-mêmes**, certifiés, de 1899 à 1985 et
    jusqu'à 104 ans. Une espérance de vie n'est rien d'autre que leur somme
    cumulée ; il n'y avait donc plus de raison de la saisir.

    La méthode se contrôle d'elle-même : appliquée à e60, que l'INSEE publie et
    que le dépôt certifie, elle retrouve la valeur publiée à moins d'un dixième
    d'année sur toute la période. Appliquée à e65 après 1960, elle retrouve
    l'OCDE dans la même marge. C'est ce double recoupement, et non la formule,
    qui autorise à s'en servir là où personne ne publie.

    Niveau ``haute`` et non ``certifiee`` : la valeur est calculée, non
    confrontée à une publication. Elle est en revanche RECALCULÉE à chaque
    exécution depuis un fichier certifié, ce qu'aucune saisie ne peut offrir.
    """
    chemin = REFERENCE / "mortalite" / "quotients_periode.csv"
    if not chemin.exists():
        raise SourceAbsente(f"{chemin} absent (lancer scripts/fetch/ined_vallin_mesle.py)")

    quotients: dict[tuple[int, str], dict[int, float]] = {}
    for ligne in charger_csv(chemin):
        quotients.setdefault(
            (int(ligne["annee"]), ligne["sexe"]), {}
        )[int(ligne["age"])] = float(ligne["qx"])

    valeurs: dict[tuple, float] = {}
    for (annee, sexe), table in quotients.items():
        if not (PREMIERE_ANNEE_ESPERANCE <= annee < PREMIERE_ANNEE_OCDE):
            continue
        if AGE_TERMINAL_MINIMAL not in table:
            # Une table tronquée trop bas rendrait une espérance trop courte.
            continue
        total, survie, age = 0.0, 1.0, 65
        while age in table:
            survie *= 1.0 - table[age]
            total += survie
            age += 1
        valeurs[(str(annee), sexe, "e65")] = round(total + 0.5, 2)
    return dict(sorted(valeurs.items()))


def source_quotients() -> dict[tuple, float]:
    """Quotients de mortalité par âge — les vraies tables du moment.

    Leur présence dispense le modèle de sa calibration paramétrique aux âges
    couverts. Les classes ouvertes (85 ans et plus, puis 95 ans et plus selon
    les millésimes) sont écartées à la récupération : au-delà du dernier âge
    publié, la loi de Gompertz-Makeham reprend la main.
    """
    serie = _serie_json("eurostat_quotients.json", "scripts/fetch/eurostat_mortalite.py")
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(serie.items(),
                                  key=lambda kv: (int(kv[0].split("|")[0]),
                                                  kv[0].split("|")[1],
                                                  int(kv[0].split("|")[2])))
    }


def source_esperances_projetees() -> dict[tuple, float]:
    """Espérances de vie d'APRÈS 2025, dérivées des quotients projetés de l'INSEE.

    Ces années étaient saisies à la main aux seules années rondes, depuis un
    exercice de projection périmé, jusqu'à une année — 2080 — qui dépassait
    l'horizon de la source dont elle se réclamait ; au-delà, la série était
    gelée, ce qui revenait à supposer l'espérance de vie arrêtée vingt ans avant
    la fin de la projection.

    Les projections de population 2026 de l'INSEE publient les quotients de
    mortalité par âge et par année jusqu'en 2125 : on en dérive e0, e60 et e65
    année par année, par la méthode qui sert déjà aux années d'avant 1960. Plus
    d'interpolation entre années rondes, plus d'extrapolation muette, plus de
    gel — la projection du modèle s'arrête en 2100, la source va vingt-cinq ans
    plus loin.

    Niveau ``projetee``, qui vaut ``estimee`` dans le modèle : la valeur vient
    du producteur, mais elle décrit un avenir. Une projection ne se fait jamais
    passer pour une observation, fût-elle publiée par l'INSEE.
    """
    serie = _serie_json("insee_projections_mortalite.json",
                        "scripts/fetch/insee_projections_mortalite.py")
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(serie.items(),
                                  key=lambda kv: (int(kv[0].split("|")[0]),
                                                  kv[0].split("|")[1],
                                                  kv[0].split("|")[2]))
    }


def source_quotients_anciens() -> dict[tuple, float]:
    """Quotients de mortalité par âge d'AVANT 1986, reconstitués par l'INED.

    Eurostat ne publie rien avant 1986, et `docs/limites.md` tenait la Human
    Mortality Database pour la seule à remonter plus haut — donc hors d'atteinte
    d'un script, puisqu'elle exige une inscription. Elle n'est pas la seule :
    les tables de Vallin et Meslé, publiées par l'INED, couvrent 1806-1997 par
    année d'âge jusqu'à 104 ans, et l'INED en sert librement le fichier.

    Les deux sources se recouvrent de 1986 à 1997 et concordent à un demi-point
    de pourcentage près ; le dépôt reprend l'INED jusqu'en 1985 et laisse à
    Eurostat, producteur de la donnée observée, tout ce qu'il publie.

    S'y ajoutent, de 1986 à 1997, les seuls âges de 95 à 104 ans : Eurostat
    s'arrête à 94 et ses classes ouvertes n'en sont pas des quotients. Ce n'est
    donc pas un panachage — c'est une source là où l'autre se tait. Ces
    240 valeurs ne déplacent aucune simulation ; elles servent à AUDITER la loi
    paramétrique qui prend le relais au-delà du dernier âge observé, et
    `tests/test_donnees.py` fige l'écart qu'elles révèlent.
    """
    serie = _serie_json("ined_vallin_mesle.json", "scripts/fetch/ined_vallin_mesle.py")
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(serie.items(),
                                  key=lambda kv: (int(kv[0].split("|")[0]),
                                                  kv[0].split("|")[1],
                                                  int(kv[0].split("|")[2])))
    }


def _charge_points() -> dict:
    chemin = BRUT / "openfisca_points.json"
    if not chemin.exists():
        raise SourceAbsente(f"{chemin} absent (lancer scripts/fetch/openfisca_points.py)")
    return json.loads(chemin.read_text(encoding="utf-8"))


def _cles_points(cle_json: str, substituees: bool) -> dict[tuple, float]:
    charge = _charge_points()
    a_part = set(charge.get("cles_substituees", []))
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(charge[cle_json].items())
        if (cle in a_part) is substituees
    }


def source_valeurs_point_ircantec() -> dict[tuple, float]:
    """Barèmes de l'Ircantec publiés par la Caisse des dépôts, qui la gère.

    Producteur de la donnée, donc seule source de ce fichier qui puisse être
    certifiée. Elle couvre 1971-2021 ; ce qui déborde reste transcrit
    d'OpenFisca.
    """
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(
            _serie_json("cdc_ircantec.json", "scripts/fetch/cdc_ircantec.py").items()
        )
    }


def source_valeurs_point_agirc_arrco() -> dict[tuple, float]:
    """Barèmes publiés par la fédération Agirc-Arrco, qui les fixe.

    Producteur de la donnée, donc seule source de ces lignes qui puisse être
    certifiée. Sa compilation porte le régime unifié depuis 2019, mais aussi les
    tables d'avant la fusion — l'Agirc de 1947 à 2018, l'Arrco de 1999 à 2018 et
    l'UNIRS de 1961 à 1998, la caisse dont le barème tient lieu de point Arrco
    avant l'unification. Ces 260 valeurs venaient d'OpenFisca ; elles viennent
    désormais de qui les a décidées, et la transcription les rendait juste, à
    cinq centièmes de millime près.

    La valeur d'achat y va un an plus loin que la valeur de service : la
    fédération la publie par année civile, quand la valeur de service dépend de
    la décision de novembre. Le récupérateur n'invente pas celle qui manque.
    """
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(
            _serie_json("agirc_arrco_valeurs_point.json",
                        "scripts/fetch/agirc_arrco_valeurs_point.py").items()
        )
    }


def source_valeurs_point_agirc_arrco_en_cours() -> dict[tuple, float]:
    """Valeur de service en vigueur dans l'année en cours, pas encore arrêtée.

    La fédération fixe cette valeur au 1er novembre ; la règle du dépôt retient
    celle du 31 décembre. L'année qui suit la dernière décision a donc une valeur
    OPPOSABLE — celle reconduite depuis le 1er janvier — sans être arrêtée.

    Ne rien écrire n'était pas neutre : faute de barème, le modèle prolongeait la
    dernière valeur par les PRIX, servant 1,46378 € pour 2026 là où la fédération
    publie un gel à 1,4386 € jusqu'au 1er novembre 2026. Entre inventer une
    décision et reconduire celle qui est en vigueur, la seconde a une source —
    d'où un niveau en retrait, et non une absence.
    """
    charge = _lire_json("agirc_arrco_valeurs_point.json",
                        "scripts/fetch/agirc_arrco_valeurs_point.py")
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(charge.get("serie_en_cours", {}).items())
    }


def source_valeurs_point_erafp() -> dict[tuple, float]:
    """Valeurs du point du RAFP, publiées par l'ERAFP qui les fixe.

    Son conseil d'administration arrête chaque année la valeur d'acquisition et
    la valeur de service : c'est le producteur, et la transcription d'OpenFisca
    s'efface devant lui — elle répétait d'ailleurs en 2021 la valeur
    d'acquisition de 2020, ce qui majorait de 0,4 % les points achetés cette
    année-là, et elle s'arrêtait cinq ans avant le tableau publié.
    """
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(
            _serie_json("erafp_valeurs_point.json",
                        "scripts/fetch/erafp_valeurs_point.py").items()
        )
    }


def source_valeurs_point() -> dict[tuple, float]:
    """Salaires de référence, valeurs de service et taux d'appel, par régime.

    Ces trois grandeurs suffisent à reconstituer exactement une pension en
    points : la cotisation d'une année divisée par le salaire de référence et
    par le taux d'appel donne les points acquis, que la valeur de service
    convertit en rente à la liquidation.

    Ce que les producteurs publient eux-mêmes est retiré d'ici — la Caisse des
    dépôts pour l'Ircantec, la fédération pour l'Agirc-Arrco, l'ERAFP pour le
    RAFP : deux contrôles ne doivent pas se disputer les mêmes lignes, et le
    producteur l'emporte sur la transcription. Si l'un de ces fichiers manque,
    OpenFisca reprend sa couverture — au niveau ``haute``, comme il se doit.
    """
    valeurs = _cles_points("serie", substituees=False)
    producteurs: set[tuple] = set()
    for source in (source_valeurs_point_ircantec, source_valeurs_point_agirc_arrco,
                   source_valeurs_point_agirc_arrco_en_cours,
                   source_valeurs_point_erafp):
        try:
            producteurs |= set(source())
        except SourceAbsente:
            continue
    # Et ce que le TEXTE corrige : une valeur saisie depuis l'arrêté (le salaire
    # de référence IPACTE de 1955) prime sur la transcription qui la porte
    # fausse. Sans cette soustraction, les deux contrôles se disputeraient la
    # clé — écart perpétuel, et journal de certification faux d'une ligne.
    producteurs |= set(source_valeurs_point_texte())
    return {cle: valeur for cle, valeur in valeurs.items() if cle not in producteurs}


def source_valeurs_point_substituees() -> dict[tuple, float]:
    """Valeurs de l'UNIRS servant de point Arrco avant l'unification de 1999.

    Publiées, mais pour une autre caisse que celle que le modèle appelle
    « arrco » — d'où un niveau en retrait, que la fédération publie ces valeurs
    ou non. Ce qui est certifié, c'est le barème de l'UNIRS, qui figure sous ce
    nom dans le fichier ; la SUBSTITUTION, elle, est une décision de
    modélisation, et aucune source ne la porte.

    La valeur, en revanche, est celle du producteur dès qu'il la publie : ce
    serait écrire le même franc de deux façons que de laisser la ligne
    ``arrco`` sur l'arrondi d'OpenFisca quand la ligne ``unirs`` porte la
    conversion exacte.
    """
    substituees = _cles_points("serie", substituees=True)
    try:
        producteur = source_valeurs_point_agirc_arrco()
    except SourceAbsente:
        return substituees
    return {
        cle: producteur.get(("unirs", *cle[1:]), valeur)
        for cle, valeur in substituees.items()
    }


def source_valeurs_point_cnbf() -> dict[tuple, float]:
    """Valeurs du point des avocats, dans les barèmes annuels de la CNBF.

    La caisse est le producteur : c'est son propre barème, publié chaque
    janvier. Aucune autre source ne les porte — ni OpenFisca, ni les barèmes
    IPP, ni la législation consolidée, dépouillée deux fois pour s'en assurer.
    """
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(
            _serie_json("cnbf_baremes.json", "scripts/fetch/cnbf_baremes.py").items()
        )
    }


def source_valeurs_point_cnavpl() -> dict[tuple, float]:
    """Valeur du point des professions libérales, dans les recueils CNAVPL.

    La caisse est le producteur, et la seule à publier ce nombre : le décret
    annuel ne fixe qu'un coefficient de revalorisation, jamais le montant.
    """
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(
            _serie_json("cnavpl_recueils.json", "scripts/fetch/cnavpl_recueils.py").items()
        )
    }


def source_valeurs_point_independants() -> dict[tuple, float]:
    """Prix et valeur du point des complémentaires artisans et commerçants.

    Ces deux régimes — le complémentaire des artisans de 1979 à 2012, le
    Nouveau régime des indépendants des commerçants de 2004 à 2012 — sont
    déclarés EN POINTS par leurs fiches, et n'avaient aucune valeur de point :
    le moteur retombait sur le rendement instantané, qui portait pour eux le
    6,74 % du RCI d'aujourd'hui. Leur rendement réel valait 11,95 % en 1980.

    Les barèmes IPP les portent, et sont une TRANSCRIPTION : le niveau est donc
    `haute`, jamais `certifiee`, comme pour OpenFisca. Le RCI qui leur succède
    en 2013 est déjà couvert ; ce contrôle s'arrête en 2012 pour ne pas
    revendiquer deux fois les mêmes lignes.
    """
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(
            _serie_json("ipp_points_independants.json",
                        "scripts/fetch/ipp_points_independants.py").items()
        )
    }


def source_valeurs_point_msa() -> dict[tuple, float]:
    """Valeur de service du point de la complémentaire agricole, dans le code rural.

    Fixée chaque année par décret, à l'article D. 732-166, dont la base LEGI de
    la DILA garde toutes les versions datées. C'est la publication officielle,
    non une transcription : le niveau est donc celui du producteur.
    """
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(
            _serie_json("dila_legi_msa.json", "scripts/fetch/dila_legi_msa.py").items()
        )
    }


def source_minimum_contributif() -> dict[tuple, float]:
    """Minimum contributif, minimum majoré et plafond, dans le code.

    `docs/limites.md` a longtemps écrit que ces montants ne figuraient dans
    aucune source machine ouverte, et qu'il n'y avait donc pas de chemin de
    certification à écrire. C'était la même erreur que pour la MSA : la donnée
    est dans la loi, il fallait chercher par le NUMÉRO D'ARTICLE. D. 351-2-1
    du code de la sécurité sociale porte les deux montants, D. 173-21-0-0-1 le
    plafond d'écrêtement. La base LEGI en garde toutes les versions datées.
    """
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(
            _serie_json("dila_legi_minimum_contributif.json",
                        "scripts/fetch/dila_legi_minimum_contributif.py").items()
        )
    }


def source_point_indice() -> dict[tuple, float]:
    """Traitement annuel d'un point d'indice de la fonction publique.

    Une seule grandeur en dépend, mais elle est décisive : la référence du
    MINIMUM GARANTI, que l'article L. 17 du code des pensions fixe au
    traitement de l'indice majoré 227 au 1er janvier 2004. Le recoupement se
    fait tout seul — 227 × 52,7558 = 11 975,57 € par an, soit les 997,96 € par
    mois que publie le Service des retraites de l'État.

    Transcription tierce du Journal officiel par OpenFisca-France : niveau
    `haute`, jamais `certifiee`. Elle ne garde que ce que le *Journal officiel*
    lui-même ne donne pas — les années d'avant 1996, dont la chaîne des versions
    de l'article 3 du décret de 1985 est incomplète dans le dump LEGI.
    """
    serie = _serie_json("openfisca_point_indice.json",
                        "scripts/fetch/openfisca_point_indice.py")
    try:
        journal_officiel = set(source_point_indice_jo())
    except SourceAbsente:
        journal_officiel = set()
    return {(annee,): valeur for annee, valeur in sorted(serie.items())
            if (annee,) not in journal_officiel}


def source_point_indice_jo() -> dict[tuple, float]:
    """Le même point d'indice, lu dans le décret qui le fixe.

    Article 3 du décret n° 85-1148 du 24 octobre 1985, dont la base LEGI garde
    chaque version datée : « La valeur annuelle du traitement […] afférents à
    l'indice 100 majoré […] est fixée à 5 907,34 € ». C'est le *Journal
    officiel*, non sa transcription — et la confrontation a corrigé deux
    arrondis, dont celui de 2002, que le décret de bascule fixe à 5 181,75 €
    quand la conversion des 33 990 F donne 5 181,74 €.
    """
    serie = _serie_json("dila_legi_point_indice.json",
                        "scripts/fetch/dila_legi_point_indice.py")
    return {(annee,): valeur for annee, valeur in sorted(serie.items())}


def source_smic() -> dict[tuple, float]:
    """SMIC horaire en vigueur au 1er janvier — décrets de relèvement, base LEGI.

    Le SMIC n'est pas fixé par un article de code mais par un décret annuel, et
    c'est le *Journal officiel* qui le porte : la transcription d'OpenFisca, qui
    tenait lieu de source, plafonnait à ``haute``. Les années dont le décret
    manque au dump ne sont pas rendues — voir le récupérateur, qui refuse de
    combler un trou par la valeur de l'année d'avant.
    """
    serie = _serie_json("dila_legi_smic.json", "scripts/fetch/dila_legi_smic.py")
    return {(annee,): valeur for annee, valeur in sorted(serie.items())}


def _parametres_retraite() -> dict[str, float]:
    return _serie_json("dila_legi_parametres_retraite.json",
                       "scripts/fetch/dila_legi_parametres_retraite.py")


def _table_legi(prefixe: str) -> dict[tuple, float]:
    """Une des tables par génération lues dans la loi, mise en forme de clés.

    La clé de génération peut porter des décimales : deux textes coupent une
    génération en cours d'année — le 1er juillet 1951, le 1er septembre 1961 —,
    et le récupérateur rend alors un segment par valeur, `1951.5` désignant le
    premier juillet. Le tri lisait ces clés avec ``int`` et les refusait.
    """
    return {
        (cle.split("|")[1],): valeur
        for cle, valeur in sorted(_parametres_retraite().items(),
                                  key=lambda kv: float(kv[0].split("|")[1]))
        if cle.startswith(f"{prefixe}|")
    }


def source_age_ouverture() -> dict[tuple, float]:
    """Âge d'ouverture des droits par génération — L. 161-17-2 et D. 161-2-1-9.

    Depuis la loi n° 2025-1403 (suspension de la réforme de 2023), la loi
    porte elle-même la table des nés à compter du 1er septembre 1961 ; le
    décret, qu'elle n'a pas réécrit, ne vaut plus que pour les autres. Le
    récupérateur lit les deux, chaque version recouvrant les mois qu'elle
    nomme à compter de sa date d'effet.

    `docs/limites.md` tenait ces tables pour hors de portée : « Légifrance
    expose une API, mais elle demande une clé et renvoie du texte juridique, non
    des paramètres. » Les deux moitiés de la phrase étaient vraies et la
    conclusion fausse. La base LEGI de la DILA est ouverte, et le texte
    juridique EST la table : « Soixante-deux ans et trois mois pour les assurés
    nés entre le 1er septembre 1961 et le 31 décembre 1961 inclus. »
    """
    return _table_legi("age_ouverture")


def source_duree_requise() -> dict[tuple, float]:
    """Durée d'assurance requise par génération — L. 161-17-3."""
    return _table_legi("duree_requise")


def source_duree_requise_1993() -> dict[tuple, float]:
    """Durée requise des générations 1934-1942 — R. 351-45 II.

    `docs/limites.md` tenait ces générations pour hors de portée : « leur montée
    en charge vient de la loi du 22 juillet 1993 […], dont les tableaux ne sont
    pas des textes consolidés séparés ». Vrai, et sans portée : le tableau n'est
    pas un texte séparé, il est CODIFIÉ — à l'article R. 351-45, une disposition
    transitoire abrogée en 2009 que la base garde.

    L'article scope sa table aux pensions prenant effet avant 2003 ; le dépôt
    l'indexe sur la seule génération. L'écart n'existe que pour un assuré de ces
    générations liquidant après 2002, et le récupérateur le documente.
    """
    return _table_legi("duree_requise_1993")


def source_duree_requise_decrets() -> dict[tuple, float]:
    """Durée requise des générations 1953 à 1957, dans leurs décrets.

    L'article L. 161-17-3 ne porte la table qu'à compter de la génération
    1958 ; celles d'avant relèvent de décrets pris sous l'ancien article
    L. 351-1, que `docs/limites.md` tenait pour hors de portée parce que « LEGI
    ne les expose sous aucun numéro d'article ». Ils n'ont pas de numéro utile,
    mais ils ont une phrase : « […] sont fixées à 166 trimestres pour les
    assurés nés en 1955 ». Quatre décrets couvrent 1953 à 1957.
    """
    serie = _serie_json("dila_legi_duree_requise.json",
                        "scripts/fetch/dila_legi_duree_requise.py")
    return {(generation,): valeur for generation, valeur in sorted(serie.items())}


def source_coefficient_minoration() -> dict[tuple, float]:
    """Coefficient de minoration par génération — R. 351-27 II."""
    return _table_legi("coefficient_minoration")


def source_duree_proratisation() -> dict[tuple, float]:
    """Durée maximale prise en compte par la proratisation — R. 351-6 II.

    À ne pas confondre avec la durée REQUISE, et le modèle les a confondues :
    la loi de 1993 a fait monter la première de deux trimestres par génération
    sur les seules générations 1944-1948, quand la seconde montait de dix
    trimestres sur dix générations. Un assuré né en 1945 se voyait diviser par
    160 là où l'article divise par 154.

    L'article couvre les générations d'avant 1944 à 1947 et renvoie au-delà à
    la durée du troisième alinéa de L. 351-1 : la ligne 1948 de la table du
    dépôt est cette jonction, et reste hors de portée de la certification.
    """
    return _table_legi("duree_proratisation")


def source_annees_salaire_reference() -> dict[tuple, float]:
    """Années retenues au salaire annuel moyen, par génération — R. 351-29-1.

    Dix années jusqu'à la génération 1933, vingt-cinq à partir de 1948, et une
    de plus par génération entre les deux. Le paramètre se lit à l'année de
    NAISSANCE : le lire à l'année de liquidation, comme le faisait le modèle,
    opposait vingt-cinq années à des générations auxquelles la loi n'en a jamais
    opposé plus de dix.
    """
    return _table_legi("annees_salaire_reference")


def source_heures_par_trimestre() -> dict[tuple, float]:
    """Heures de SMIC à cotiser pour valider un trimestre — R. 351-9.

    200 heures depuis 1972, 150 depuis 2014. C'est ce qui décide du nombre de
    trimestres qu'une année de petit salaire valide, donc de la décote.
    """
    return _table_legi("heures_par_trimestre")


def _decote_fonction_publique(mesure: str) -> dict[tuple, float]:
    serie = _serie_json("dila_legi_decote_fonction_publique.json",
                        "scripts/fetch/dila_legi_decote_fonction_publique.py")
    return {
        (cle.split("|")[1],): valeur
        for cle, valeur in sorted(serie.items())
        if cle.startswith(f"{mesure}|")
    }


def source_decote_fp_coefficient() -> dict[tuple, float]:
    """Coefficient de minoration de la fonction publique, année par année.

    Article 66 III de la loi du 21 août 2003, qui déroge à l'article L. 14 du
    code des pensions le temps de la montée en charge : un huitième de point
    par trimestre en 2006, un et quart à compter de 2015. Opposer la cible à
    une liquidation de 2008 décote dix fois trop.
    """
    return _decote_fonction_publique("coefficient")


def source_decote_fp_trimestres() -> dict[tuple, float]:
    """Trimestres retranchés à la limite d'âge, année par année.

    L'âge d'annulation de la décote n'est pas un âge en propre dans la fonction
    publique : c'est la limite d'âge du grade, diminuée de seize trimestres en
    2006 et d'un seul en 2019. Le même tableau les porte.
    """
    return _decote_fonction_publique("trimestres_avant_limite")


def _minimum_garanti(mesure: str) -> dict[tuple, float]:
    serie = _serie_json("dila_legi_minimum_garanti.json",
                        "scripts/fetch/dila_legi_minimum_garanti.py")
    return {
        (cle.split("|")[1],): valeur
        for cle, valeur in sorted(serie.items())
        if cle.startswith(f"{mesure}|")
    }


def source_minimum_garanti_indice() -> dict[tuple, float]:
    """Indice majoré de référence du minimum garanti, 2004-2013.

    Article 66 V de la loi du 21 août 2003, qui déroge aux a et b de l'article
    L. 17 du code des pensions le temps de la montée en charge. C'est le même
    article que celui de la décote de la fonction publique, un tableau plus bas.
    """
    return _minimum_garanti("indice_majore")


def source_minimum_garanti_part() -> dict[tuple, float]:
    """Fraction du traitement de référence servie à quinze ans de services."""
    return _minimum_garanti("part_15_ans")


def source_minimum_garanti_points_15_30() -> dict[tuple, float]:
    """Points gagnés par trimestre de services de quinze ans au seuil suivant."""
    return _minimum_garanti("points_15_30")


def source_minimum_garanti_points_30_40() -> dict[tuple, float]:
    """Points gagnés par trimestre au-delà de ce seuil, jusqu'à quarante ans."""
    return _minimum_garanti("points_30_40")


def source_minimum_garanti_seuil() -> dict[tuple, float]:
    """Borne haute de la première pente, en trimestres.

    La loi l'écrit en toutes lettres et parfois en demi-années : « Vingt-cinq
    ans et demi » fait 102 trimestres.
    """
    return _minimum_garanti("trimestres_seuil")


def _cles_non_certifiees(chemin: Path, cles: tuple[str, ...]) -> set[tuple]:
    """Les lignes d'une table que la base LEGI n'a pas certifiées.

    Une transcription tierce ne peut ni certifier ni DÉCERTIFIER : versée au
    niveau ``haute``, elle ne doit toucher qu'aux lignes qui ne sont pas déjà
    au-dessus. C'est la règle du plafond ancien, qui s'efface devant le
    *Journal officiel*, écrite une fois pour toutes les sources OpenFisca.
    """
    if not chemin.exists():
        return set()
    return {
        tuple(ligne[c] for c in cles)
        for ligne in charger_csv(chemin)
        if ligne.get("fiabilite") != "certifiee"
    }


def _tables_generation_openfisca() -> dict[str, dict[float, float]]:
    charge = _lire_json("openfisca_parametres_generation.json",
                        "scripts/fetch/openfisca_parametres_generation.py")
    return {
        serie: {float(g): float(v) for g, v in table.items()}
        for serie, table in charge["series"].items()
    }


def _en_escalier(table: dict[float, float], generation: float) -> float | None:
    """Lecture en escalier, comme ``TableParGeneration`` : la valeur du dernier
    bloc qui commence avant la génération demandée."""
    applicables = [g for g in table if g <= generation]
    return table[max(applicables)] if applicables else None


def source_duree_requise_openfisca() -> dict[tuple, float]:
    """Durée requise des générations que la base LEGI ne certifie pas.

    Les générations 1943 à 1952 — 160 « vient de la règle générale », 161 à
    164 sont dans des décrets absents de la base — sont confrontées à la table
    d'OpenFisca-France-Pension, transcrite des mêmes circulaires par d'autres
    mains. Niveau ``haute``, et rien de plus ; les lignes certifiées ne sont
    pas touchées.
    """
    table = _tables_generation_openfisca()["duree_requise"]
    return {
        cle: valeur
        for cle in sorted(_cles_non_certifiees(
            REFERENCE / "legislation" / "duree_assurance_requise.csv", ("generation",)),
            key=lambda c: float(c[0]))
        if (valeur := _en_escalier(table, float(cle[0]))) is not None
    }


def source_age_annulation_openfisca() -> dict[tuple, float]:
    """Âge d'annulation de la décote, par génération, chez OpenFisca.

    La table du dépôt est calculée — l'âge d'ouverture majoré de cinq ans — et
    recontrôlée à chaque exécution par ``controle_vraisemblance_age_annulation``.
    OpenFisca la porte transcrite : c'est un second chemin, indépendant du
    premier, et il la verse au niveau ``haute`` où elle était déjà.
    """
    table = _tables_generation_openfisca()["age_annulation_decote"]
    return {
        cle: valeur
        for cle in sorted(_cles_non_certifiees(
            REFERENCE / "legislation" / "age_annulation_decote.csv", ("generation",)),
            key=lambda c: float(c[0]))
        if (valeur := _en_escalier(table, float(cle[0]))) is not None
    }


#: Âge d'ouverture d'un sédentaire de la fonction publique avant la réforme de
#: 2010 : la table d'OpenFisca est par génération, celle du dépôt par année
#: d'ouverture du droit, et c'est cet âge qui passe de l'une à l'autre.
AGE_OUVERTURE_SEDENTAIRE_AVANT_2010 = 60


def source_duree_requise_fonction_publique_openfisca() -> dict[tuple, float]:
    """Montée en charge de la loi de 2003 dans la fonction publique, chez OpenFisca.

    Le dépôt la tient du texte, par année d'ouverture du droit ; OpenFisca la
    transcrit par génération. Pour un sédentaire les deux se correspondent à
    soixante ans près, et c'est ce que ce contrôle vérifie — au niveau
    ``haute``, la table étant lue dans un article, non produite par lui.
    """
    table = _tables_generation_openfisca()["duree_requise_fonction_publique"]
    cles = _cles_non_certifiees(
        REFERENCE / "legislation" / "duree_requise_fonction_publique.csv",
        ("annee_ouverture",))
    return {
        (str(int(generation) + AGE_OUVERTURE_SEDENTAIRE_AVANT_2010),): valeur
        for generation, valeur in sorted(table.items())
        if (str(int(generation) + AGE_OUVERTURE_SEDENTAIRE_AVANT_2010),) in cles
    }


def source_carriere_longue() -> dict[tuple, float]:
    """Portes du départ anticipé pour carrière longue — D. 351-1-1.

    Clé : date d'effet de la version en année décimale (`2023.667` pour le
    1er septembre 2023), génération (`1900` pour la règle générale du I,
    `1963.667` pour une adaptation du II ouverte au 1er septembre 1963), âge de
    début d'activité. Le récupérateur lit les versions depuis celle du
    1er septembre 2023 — le I et le II, celui-ci résolu contre la table d'âge
    en vigueur à la date d'effet — et n'ouvre pas de date d'effet à une
    version qui ne change aucune porte. Depuis l'action 27 bis, il lit aussi
    les rédactions de 2003, de 2011 et de 2012, dont les portes sont groupées
    par génération sous des en-têtes « Pour les assurés nés en 1953 : ».
    """
    brut = _lire_json("dila_legi_parametres_retraite.json",
                      "scripts/fetch/dila_legi_parametres_retraite.py")

    def decimale(annee: int, mois: int) -> str:
        return f"{annee + (mois - 1) / 12.0:.3f}".rstrip("0").rstrip(".")

    portes = {}
    for porte in brut.get("carriere_longue", []):
        texte = str(porte["entree_en_vigueur"])
        annee, mois = int(texte[:4]), int(texte[5:7]) if len(texte) >= 7 else 1
        generation = float(porte.get("generation", 1900))
        cle_generation = decimale(int(generation),
                                  int(round((generation - int(generation)) * 12)) + 1)
        portes[(decimale(annee, mois), cle_generation,
                str(int(porte["age_debut_maximum"])),
                str(int(porte["trimestres_supplementaires"])))] = float(porte["age_depart"])
    return portes


def _point_insee() -> dict[str, dict[int, float]]:
    """Valeur de service du point Agirc, Arrco et Agirc-Arrco, au 31 décembre.

    L'INSEE diffuse ces barèmes en série mensuelle. La convention du dépôt
    retient la valeur en vigueur au 31 décembre : c'est donc l'observation de
    décembre qu'on garde, et une année dont il manque n'est pas reconstituée.
    """
    par_regime: dict[str, dict[int, float]] = {}
    for nom, regime in (
        ("point_arrco", "arrco"),
        ("point_agirc", "agirc"),
        ("point_agirc_arrco", "agirc_arrco"),
    ):
        par_regime[regime] = {
            int(periode[:4]): valeur
            for periode, valeur in sorted(_observations(nom).items())
            if periode[5:7] == "12"
        }
    return par_regime


def source_valeurs_point_insee() -> dict[tuple, float]:
    """Ce que l'INSEE ajoute aux valeurs du point d'OpenFisca, et lui seul.

    L'INSEE n'est pas le producteur de ces barèmes — l'Agirc-Arrco l'est — si
    bien que cette série ne prime pas sur la transcription là où les deux se
    recouvrent : ``controle_vraisemblance_point_insee`` les y confronte, et
    c'est tout. Ce qu'elle apporte, c'est la fin de la série : OpenFisca
    s'arrête à sa dernière année publiée, l'INSEE continue.

    Elle s'efface AUSSI devant le producteur lui-même, depuis que la fédération
    Agirc-Arrco est lue directement. Sans cela, l'INSEE reprenait la valeur de
    service de 2025 — la seule qu'OpenFisca n'ait pas — et la reversait au
    niveau ``haute`` après que le producteur l'avait certifiée : la dernière
    certification écrite gagne, et c'était la moins bien placée.
    """
    connues = set(_cles_points("serie", substituees=False))
    for source in (source_valeurs_point_agirc_arrco,
                   source_valeurs_point_agirc_arrco_en_cours):
        try:
            connues |= set(source())
        except SourceAbsente:
            continue
    return {
        (regime, str(annee), "valeur_service"): valeur
        for regime, valeurs in sorted(_point_insee().items())
        for annee, valeur in sorted(valeurs.items())
        if (regime, str(annee), "valeur_service") not in connues
    }


def source_valeurs_point_texte() -> dict[tuple, float]:
    """Ce qu'aucune transcription machine ne porte, saisi depuis le texte."""
    charge = _charge_points()
    return {tuple(cle.split("|")): valeur
            for cle, valeur in sorted(charge["complements"].items())}


def source_valeurs_point_estimees() -> dict[tuple, float]:
    """Prolongements assumés, sans texte : le taux d'appel des prédécesseurs de
    l'Ircantec, emprunté à son successeur. Niveau ``estimee``, et rien de plus :
    ce n'est ni une lecture ni une transcription."""
    charge = _charge_points()
    return {tuple(cle.split("|")): valeur
            for cle, valeur in sorted(charge.get("complements_estimes", {}).items())}


def source_minimum_vieillesse() -> dict[tuple, float]:
    """Montant de l'ASPA, lu dans l'article D. 815-1 du code.

    Le dépôt le tenait d'une saisie sur Légifrance. L'article le porte, daté, et
    la base LEGI en garde les versions — mais il n'est pas réécrit à chaque
    revalorisation : il s'arrête en 2020 et saute 2013 et 2015-2017. Les ancres
    que le dépôt tient d'ailleurs comblent ce qu'il tait, au niveau ``haute``.

    Le montant lu est l'ANNUEL que le texte fixe, non douze fois le mensuel
    arrondi : neuf centimes séparent les deux en 2010, et c'est le texte qui
    dit lequel est la grandeur.
    """
    serie = _serie_json("dila_legi_minimum_vieillesse.json",
                        "scripts/fetch/dila_legi_minimum_vieillesse.py")
    return {(annee,): valeur for annee, valeur in sorted(serie.items())}


def source_minimum_garanti_reference() -> dict[tuple, float]:
    """Traitement de référence du minimum garanti, par le service qui le sert.

    L'article L. 17 le définit comme le traitement de l'indice majoré 227 au
    1er janvier 2004, revalorisé comme les pensions. Le Service des retraites de
    l'État publie les deux bornes de cette chaîne — l'ancre et le montant
    courant, daté —, et c'est lui qui liquide : ce n'est pas une transcription
    du barème, c'est le barème opposé à l'assuré.

    L'ancre de 2004 se trouve ainsi confirmée par un TROISIÈME chemin, après le
    produit 227 × point d'indice que ``controle_vraisemblance_minimum_garanti``
    refait déjà. Les années intermédiaires ne sont pas publiées et restent
    transcrites.
    """
    serie = _serie_json("sre_minimum_garanti.json",
                        "scripts/fetch/sre_minimum_garanti.py")
    return {(annee,): valeur for annee, valeur in sorted(serie.items())}


def source_salaires_forfaitaires_marins() -> dict[tuple, float]:
    """Les salaires forfaitaires des marins, par catégorie et par année, au JORF.

    Cotisations et pensions des marins sont assises sur un salaire FORFAITAIRE
    par catégorie de fonction à bord, non sur la rémunération réelle. Le
    *Journal officiel* en est le producteur : chaque année depuis 2008, un
    arrêté « portant majoration des salaires forfaitaires » publie les vingt
    montants ; ``scripts/fetch/jorf_salaires_forfaitaires_marins.py`` les lit
    dans l'index du dépôt et retient la grille en vigueur au 1er juillet.
    """
    return {
        tuple(cle.split("|")): valeur
        for cle, valeur in sorted(
            _serie_json("jorf_salaires_forfaitaires_marins.json",
                        "scripts/fetch/jorf_salaires_forfaitaires_marins.py").items()
        )
    }


#: Part de la cotisation d'assurances sociales d'avant 1967 que le modèle
#: attribue à la vieillesse : celle que l'ordonnance du 21 août 1967 lui a
#: donnée en séparant les branches — 8,5 points sur 21 (3 + 5,5 pour la
#: vieillesse, 6 + 15 en tout au 1er octobre 1967, décret n° 67-803).
PART_VIEILLESSE_AVANT_1967 = 8.5 / 21.0
_TAUX_AVANT_1967 = re.compile(
    r"^(\d\d)/(\d\d)/(19[4-6]\d)\s*([\d,]+)%\s*([\d,]+)%\s*([\d,]+)%", re.M
)


def source_taux_avant_1967() -> dict[tuple, float]:
    """Le régime général avant 1967 : la cotisation d'assurances sociales, et sa
    part vieillesse par convention.

    Avant l'ordonnance du 21 août 1967, la cotisation des assurances sociales
    couvrait maladie, maternité, invalidité, vieillesse et décès d'un seul
    taux, et aucun texte n'en isolait la part vieillesse. Le tableau « Taux de
    cotisation vieillesse des assurances sociales (maladie et vieillesse) du
    régime général (1945-1967) » du document du COR « L'évolution des
    paramètres du régime de la CNAV » (d'après la Cnav) date chaque taux et
    son texte : 6 % salarié et 6 % employeur au 1er janvier 1945 (ordonnance
    du 30 décembre 1944), 6 % et 10 % au 1er janvier 1947, 12,5 % employeur
    en 1959, 13,5 % en 1961, 14,25 % en 1962, 15 % au 1er septembre 1966.

    La part vieillesse est une CONVENTION, nommée et unique : la part que
    l'ordonnance de 1967 a donnée à la vieillesse en séparant les branches
    (8,5 points sur 21). Elle vaut 4,86 % en 1945, 6,48 % de 1947 à 1958,
    7,49 % en 1959, 7,89 % en 1961, 8,20 % en 1962, 8,50 % en 1966 — la
    cotisation de 1966 retrouve exactement celle du 1er octobre 1967. La
    Cnav, elle, retient « un taux de 9 % » pour les périodes antérieures au
    1er octobre 1967 dans ses calculs de validation. Niveau ``estimee``, parce
    que la convention n'est pas un texte ; les taux globaux, eux, sont datés.
    """
    chemin = BRUT / "sites_institutionnels" / "cor_parametres_cnav_2009.pdf"
    if not chemin.exists():
        raise SourceAbsente(
            f"{chemin} absent (lancer scripts/fetch/sites_institutionnels.py)"
        )
    sys.path.insert(0, str(RACINE / "scripts" / "fetch"))
    from lecture_pdf import texte_pdf  # noqa: E402

    texte = texte_pdf(chemin.read_bytes()).replace("\u202f", " ")
    bornes: list[tuple[int, int, float, float]] = []
    for jour, mois, annee, salarie, _, employeur in _TAUX_AVANT_1967.findall(texte):
        bornes.append((int(annee), int(mois), float(salarie.replace(",", ".")),
                       float(employeur.replace(",", "."))))
    if not bornes:
        raise SourceAbsente(f"{chemin} : tableau des taux 1945-1967 introuvable")
    bornes.sort()
    valeurs: dict[tuple, float] = {}
    for annee in range(1945, 1967):
        # Le taux en vigueur au 1er janvier ; l'année 1966 prend celui du
        # 1er septembre, qui est celui que 1967 reconduit.
        en_vigueur = [b for b in bornes if (b[0], b[1]) <= (annee, 12)]
        if not en_vigueur:
            continue
        _, _, salarie, employeur = en_vigueur[-1]
        total = (salarie + employeur) / 100.0 * PART_VIEILLESSE_AVANT_1967
        valeurs[("regime_general", str(annee), "taux_plafonne")] = total
        valeurs[("regime_general", str(annee), "part_salariale")] = salarie / (salarie + employeur)
        valeurs[("regime_general", str(annee), "taux_deplafonne")] = 0.0
        valeurs[("regime_general", str(annee), "part_salariale_deplafonnee")] = 0.0
        valeurs[("msa_salaries", str(annee), "taux_plafonne")] = total
        valeurs[("msa_salaries", str(annee), "part_salariale")] = salarie / (salarie + employeur)
    return valeurs


def source_plafond_journal_officiel() -> dict[tuple, float]:
    """Plafond de la Sécurité sociale d'avant 2002, dans les décrets qui le fixent.

    Le plafond n'est pas une statistique, c'est un décret : le *Journal
    officiel* en est le producteur, et la base JORF de la DILA le porte. Les
    années 2002 et suivantes viennent de l'INSEE, qui publie le plafond mensuel
    et l'emporte pour cette période ; celles d'avant venaient d'OpenFisca, une
    transcription tierce plafonnée à ``haute``.

    La chaîne des décrets est complète depuis 1963, mais leur RÉDACTION ne l'est
    pas : le récupérateur ne rend que les années dont il a lu le montant, jamais
    une année reconduite ni une année calculée à partir d'un taux. Sa
    documentation les recense une à une.
    """
    serie = _serie_json("jorf_plafond_securite_sociale.json",
                        "scripts/fetch/jorf_plafond_securite_sociale.py")
    return {
        (annee,): round(valeur)
        for annee, valeur in sorted(serie.items())
        if int(annee) < 2002
    }


def source_plafond_ancien() -> dict[tuple, float]:
    """Plafond de la Sécurité sociale d'avant 2002, par OpenFisca-France.

    Bornée à 2001 : au-delà, le plafond publié par l'INSEE est une source
    primaire, qui l'emporte. Les années 2002-2026 servent de contrôle croisé
    entre les deux, sans être versées ici.

    Elle s'efface AUSSI devant le *Journal officiel*, pour les années qu'il
    porte. Non que l'appliquer d'abord et laisser la certification l'écraser
    ensuite donnerait un autre fichier — l'ordre de la liste suffirait —, mais
    parce que le JOURNAL DE CERTIFICATION consignerait alors soixante et onze
    valeurs versées au niveau ``haute`` quand le fichier n'en porterait que
    cinquante-neuf. Une trace qui décrit autre chose que ce qui a été écrit ne
    vaut rien, et c'est un test qui l'a dit.
    """
    serie = _serie_json("openfisca_plafond.json", "scripts/fetch/openfisca_plafond.py")
    try:
        lues = set(source_plafond_journal_officiel())
    except SourceAbsente:
        lues = set()
    return {
        (annee,): round(valeur)
        for annee, valeur in sorted(serie.items())
        if int(annee) < 2002 and (annee,) not in lues
    }


def _contributions_employeur(nom: str) -> dict[str, float]:
    """Une des quatre séries de contribution employeur publique."""
    chemin = BRUT / "contribution_employeur_public.json"
    if not chemin.exists():
        raise SourceAbsente(
            f"{chemin} absent "
            "(lancer scripts/fetch/contribution_employeur_public.py)"
        )
    return json.loads(chemin.read_text(encoding="utf-8"))["series"][nom]


def source_employeur_etat_appele() -> dict[tuple, float]:
    """Contribution employeur de l'État appelée depuis 2006, agents civils.

    Fiche « Historique des taux de cotisations » du Service des retraites de
    l'État, qui appelle la cotisation : source PRIMAIRE, donc certifiable. Le
    script de récupération la recoupe année par année contre la transcription
    OpenFisca des mêmes décrets.
    """
    return {
        (annee, "fonction_publique_etat"): taux
        for annee, taux in sorted(
            _contributions_employeur("fonction_publique_etat_explicite").items())
    }


def source_employeur_etat_implicite() -> dict[tuple, float]:
    """Taux de cotisation employeur IMPLICITE de l'État, 1995-2005.

    Reconstitution publiée par l'annexe « pensions » au projet de loi de
    finances pour 2011, transcrite par OpenFisca. Deux raisons de ne pas
    dépasser `haute` : ce n'est pas le producteur qui la sert, et ce n'est pas
    un taux appelé mais une simulation du compte du régime, sur un périmètre
    plus étroit que celui du CAS.
    """
    return {
        (annee, "fonction_publique_etat"): taux
        for annee, taux in sorted(
            _contributions_employeur("fonction_publique_etat_implicite").items())
    }


def source_employeur_public_texte() -> dict[tuple, float]:
    """Taux employeur qu'aucune transcription machine ne porte, saisis du décret.

    Le décret n° 2025-86 du 30 janvier 2025 programme quatre marches de trois
    points pour la CNRACL — 34,65 % en 2025, puis 37,65 %, 40,65 % et 43,65 % —
    quand la transcription d'OpenFisca s'arrête à la première. Les ignorer
    revenait à prolonger le taux de 2025 au niveau ``estimee``, c'est-à-dire à
    ne pas voir une hausse déjà publiée au *Journal officiel*.

    Saisies depuis le texte, ni transcrites par un tiers ni recoupées : niveau
    ``moyenne``, comme le taux d'appel Agirc-Arrco.
    """
    charge = _lire_json("contribution_employeur_public.json",
                        "scripts/fetch/contribution_employeur_public.py")
    couvertes = _annees_cnracl_du_journal_officiel()
    return {
        (annee, regime): taux
        for cle, taux in sorted(charge.get("complements", {}).items())
        for regime, annee in [cle.split("|")]
        if (annee, regime) not in couvertes
    }


def source_employeur_cnracl_jo() -> dict[tuple, float]:
    """Contribution employeur à la CNRACL, lue dans le décret qui la fixe.

    Article 5 II du décret n° 91-613 du 28 juin 1991, dont la base LEGI garde
    vingt versions datées : « Le taux de la contribution sur les traitements
    […] est fixé à 31,65 % ». Elle couvre 1993 à 2028 — y compris les trois
    marches que le décret du 30 janvier 2025 programme jusqu'en 2028, et que le
    dépôt tenait pour une saisie.

    Le I du même article porte la RETENUE de l'agent, et la contribution
    supplémentaire qui suit le II est un autre prélèvement : ni l'un ni l'autre
    n'entre ici.

    Elle couvre aussi 1984-1988. L'avant-1993 n'était pas hors de portée : il
    était cherché dans les décrets modificatifs — qui ne portent qu'un
    remplacement — au lieu de l'article 3 du décret de 1947, qu'ils modifiaient
    et dont la base garde les versions datées. Le récupérateur n'en rend que les
    années dont la chaîne est sûre ; voir sa documentation.
    """
    serie = _serie_json("dila_legi_cnracl.json", "scripts/fetch/dila_legi_cnracl.py")
    return {(annee, "cnracl"): taux for annee, taux in sorted(serie.items())}


def _annees_cnracl_du_journal_officiel() -> set[tuple]:
    try:
        return set(source_employeur_cnracl_jo())
    except SourceAbsente:
        return set()


def source_employeur_cnracl() -> dict[tuple, float]:
    """Contribution employeur à la CNRACL, depuis 1948.

    La fonction publique territoriale et hospitalière n'a jamais eu le problème
    de l'État : ses employeurs cotisent à une caisse, dont le taux est fixé par
    décret depuis 1947. Transcription OpenFisca des décrets et des barèmes de la
    Caisse des dépôts : niveau `haute`.

    Elle ne garde que ce que le *Journal officiel* ne rend pas — les années
    d'avant 1993, dont les taux sont dans les décrets abrogés que celui de 1991
    a remplacés.
    """
    couvertes = _annees_cnracl_du_journal_officiel()
    return {
        (annee, "cnracl"): taux
        for annee, taux in sorted(_contributions_employeur("cnracl").items())
        if (annee, "cnracl") not in couvertes
    }


def source_employeur_sncf_textes() -> dict[tuple, float]:
    """Contribution employeur de la SNCF, lue dans ses deux textes.

    T1 est arrêté chaque année et publié au *Journal officiel* ; T2 est au IV de
    l'article 2 du décret n° 2007-1056, que la base LEGI garde daté. Leur somme
    est ce que l'entreprise verse, et elle n'est lisible que là où ses deux
    termes le sont — c'est-à-dire de 2007 à 2011, le décret cessant ensuite de
    chiffrer T2 pour le faire évoluer par formule.

    Le T1 retenu est le DÉFINITIF de l'année, arrêté l'exercice une fois connu,
    non le provisionnel appelé en décembre : les deux diffèrent de six dixièmes
    de point en 2018.
    """
    serie = _serie_json("sncf_contribution_employeur.json",
                        "scripts/fetch/sncf_contribution_employeur.py")
    return {
        (cle.split("|")[1], "sncf"): taux
        for cle, taux in sorted(serie.items())
        if cle.startswith("taux|")
    }


def _annees_sncf_des_textes() -> set[tuple]:
    try:
        return set(source_employeur_sncf_textes())
    except SourceAbsente:
        return set()


def _employeur_du_journal_officiel(regime: str) -> dict[tuple, float]:
    """Une des six séries lues dans les textes par ``dila_legi_contribution_employeur``."""
    charge = _lire_json("dila_contribution_employeur.json",
                        "scripts/fetch/dila_legi_contribution_employeur.py")
    return {
        (annee, regime): taux
        for annee, taux in sorted(charge["series"].get(regime, {}).items())
    }


def source_employeur_ratp() -> dict[tuple, float]:
    """Contribution de la RATP à la caisse de son personnel, 2007-2025.

    Arrêtés annuels pris pour l'article 2 du décret n° 2005-1637 du 26 décembre
    2005 : « le taux définitif de la cotisation à la charge de la Régie autonome
    des transports parisiens […] est fixé à 19,43 % pour l'exercice 2024 ». Le
    taux retenu est le DÉFINITIF de l'exercice, non le provisionnel appelé
    d'avance, et l'arrêté modificatif du 23 juin 2020 l'emporte sur celui qu'il
    corrige.

    Ce que ce taux n'est pas : les droits spécifiques du régime, que l'État
    finance jusqu'à 45 000 agents (article 4 du même décret), n'y sont pas. Un
    taux d'employeur, non un taux d'équilibre.
    """
    return _employeur_du_journal_officiel("ratp")


def source_employeur_ieg() -> dict[tuple, float]:
    """Contribution des employeurs à la CNIEG, 2005-2020.

    Arrêtés annuels pris pour l'article 3 du décret n° 2005-278 du 24 mars
    2005, qui approuvent la délibération du conseil d'administration de la
    caisse « établissant à 29,70 % le taux définitif de la cotisation à la
    charge des employeurs […] pour l'exercice 2020 ».

    La série s'arrête à 2020 parce que le texte cesse de chiffrer : l'arrêté du
    29 décembre 2021 remplace la fixation annuelle par une formule, et un taux
    qui évolue par renvoi n'est écrit nulle part. Même mur que la composante T2
    de la SNCF.
    """
    return _employeur_du_journal_officiel("ieg")


def source_employeur_sncf_avant_2007() -> dict[tuple, float]:
    """Contribution employeur de la SNCF avant la réforme de 2007, 1992-2006.

    « Le taux de la cotisation d'assurance vieillesse due pour le personnel en
    activité relevant du régime spécial […] est fixé à 36,29 p. 100, soit
    28,44 p. 100 à la charge de l'employeur et 7,85 p. 100 à la charge de
    l'agent » — II de l'article 8 du décret n° 91-613 du 28 juin 1991, abrogé
    le 29 juin 2007 par le décret qui institue les composantes T1 et T2.

    2007 n'est pas rendue : l'arrêté qui fixe T1 « pour l'année 2007 » date
    l'exercice entier, et le dépôt porte déjà cette année-là au titre de la
    somme T1 + T2.
    """
    return _employeur_du_journal_officiel("sncf")


def source_employeur_mines() -> dict[tuple, float]:
    """Cotisation de l'exploitant au régime minier, 1984-2026.

    Article 52 du décret n° 46-2769 du 27 novembre 1946 jusqu'en 1992 — « la
    cotisation de l'exploitant est fixée à 7,75 p. 100 des salaires » —, puis
    article 90 du même décret, qui reprend le 1er janvier 1993 : « à hauteur de
    15,60 %, soit 7,75 % à la charge des employeurs et 7,85 % à la charge des
    salariés ». Le taux n'a pas bougé en quarante-trois ans.

    Deux choses n'y sont pas. La contribution de l'État, « une cotisation
    correspondant à 22 % des salaires » plus un complément d'équilibre, qui
    pèse près de trois fois celle de l'exploitant mais n'est pas une cotisation
    d'employeur. Et les 1,6 % dus depuis 1991 sur la TOTALITÉ des rémunérations :
    la fiche du régime a une assiette plafonnée, où ils ne trouveraient pas leur
    place.
    """
    return _employeur_du_journal_officiel("mines")


def source_employeur_opera() -> dict[tuple, float]:
    """Contribution de l'Opéra national de Paris à sa caisse, 1992-2026.

    II de l'article 6 du décret n° 91-613 du 28 juin 1991, qui fixe « le taux de
    la contribution mentionnée au 2° de l'article 4 du décret du 5 avril 1968 ».
    Cette contribution est, aux termes de l'article qu'il vise, « égale à un
    pourcentage des rémunérations soumises à retenues pour pension » : la même
    assiette que la retenue de l'agent, ce qui rend leur somme lisible.
    """
    return _employeur_du_journal_officiel("opera_de_paris")


def source_employeur_comedie_francaise() -> dict[tuple, float]:
    """Contribution de la Comédie-Française à sa caisse, 1992-2026.

    II de l'article 7 du décret n° 91-613 du 28 juin 1991, jumeau de l'article 6
    et renvoyant de la même façon au 2° de l'article 4 du décret n° 68-960 du
    11 octobre 1968.
    """
    return _employeur_du_journal_officiel("comedie_francaise")


def source_employeur_sncf() -> dict[tuple, float]:
    """Contribution employeur de la SNCF, T1 + T2, 2007-2018.

    T1 est calée sur ce que coûteraient les mêmes salariés au régime général et
    aux complémentaires du privé ; T2 finance les droits spécifiques du régime
    et son déséquilibre démographique. Leur somme est ce que l'entreprise verse.

    Transcription OpenFisca : elle ne garde que les années dont les textes ne
    portent pas les deux composantes.
    """
    couvertes = _annees_sncf_des_textes()
    return {
        (annee, "sncf"): taux
        for annee, taux in sorted(_contributions_employeur("sncf").items())
        if (annee, "sncf") not in couvertes
    }


# ---------------------------------------------------------------------------
# Contrôles de certification
# ---------------------------------------------------------------------------


#: Colonnes-clés qui se trient en NOMBRE et non en texte. Sans elles, la borne
#: « 1000 » d'une tranche de pension tomberait entre « 100 » et « 200 ».
CLES_NUMERIQUES = frozenset({"annee", "date_effet", "generation", "borne_mensuelle",
                             "maturite"})


@dataclass(frozen=True)
class Certification:
    """Confrontation d'une série de référence à sa source."""

    nom: str
    chemin: Path
    cles: tuple[str, ...]
    colonne: str
    source: Callable[[], dict[tuple, float]]
    origine: str
    decimales: int
    tolerance: float
    unite: str = ""
    #: colonnes fixes à renseigner sur les lignes créées de toutes pièces
    gabarit: dict[str, str] = field(default_factory=dict)
    #: Niveau accordé aux valeurs confrontées. ``certifiee`` suppose que la
    #: source soit le producteur de la donnée ; une transcription tierce, même
    #: sourcée et reprise automatiquement, ne va pas au-delà de ``haute``.
    niveau: str = "certifiee"
    #: en-tête à écrire si le fichier de référence n'existe pas encore
    entete: tuple[str, ...] = ()
    #: Source d'APPOINT : elle ne comble que ce que les autres ne couvrent pas,
    #: et peut donc légitimement n'avoir rien à dire. Sans ce drapeau, une telle
    #: source vide serait indiscernable d'un récupérateur cassé — et le contrôle
    #: qui exige qu'une série certifiée apporte au moins une valeur doit rester
    #: sévère pour toutes les autres.
    complementaire: bool = False

    def format(self, valeur: float) -> str:
        return f"{valeur:.{self.decimales}f}" if self.decimales else f"{valeur:.0f}"

    def confronter(self, appliquer: bool) -> tuple[list[str], dict | None]:
        """Confronte la série à sa source.

        Rend les messages et la trace à consigner : un dictionnaire vide quand
        il n'y a rien à consigner, et ``None`` quand la trace existante doit au
        contraire être RETIRÉE du journal.
        """
        try:
            attendu = self.source()
        except SourceAbsente as erreur:
            return [f"IGNORÉ  {self.nom} : {erreur}"], {}

        if not attendu and self.complementaire:
            # ``None`` et non ``{}`` : le journal se complète d'ordinaire, mais
            # une trace qui affirme une certification qui n'a plus lieu doit
            # être RETIRÉE, pas conservée.
            return [
                f"RIEN    {self.nom} : {self.origine} n'ajoute rien, tout ce "
                "qu'elle couvre l'est déjà par une source mieux placée"
            ], None

        if not self.chemin.exists():
            if not appliquer:
                return [
                    f"ABSENT  {self.nom} : {self.chemin.name} n'existe pas encore, "
                    f"{len(attendu)} valeurs à créer — relancer avec --appliquer"
                ], {}
            self.chemin.parent.mkdir(parents=True, exist_ok=True)
            champs = [*self.cles, self.colonne, "fiabilite"]
            self.chemin.write_text(
                "\n".join(self.entete) + "\n" + ",".join(champs) + "\n",
                encoding="utf-8",
            )

        commentaires, champs, lignes = _lire(self.chemin)
        par_cle = {tuple(l[c] for c in self.cles): l for l in lignes}

        identiques, corrigees, ajoutees, ecarts = 0, [], [], []
        for cle, valeur in attendu.items():
            texte = self.format(valeur)
            ligne = par_cle.get(cle)
            if ligne is None:
                ajoutees.append(cle)
                if appliquer:
                    neuve = {c: "" for c in champs}
                    neuve.update(self.gabarit)
                    neuve.update(dict(zip(self.cles, cle)))
                    neuve[self.colonne] = texte
                    neuve["fiabilite"] = self.niveau
                    lignes.append(neuve)
                continue
            ancienne = float(ligne[self.colonne])
            if abs(ancienne - valeur) > self.tolerance:
                corrigees.append((cle, ancienne, valeur, ligne["fiabilite"]))
                ecarts.append(
                    f"ÉCART   {self.nom} {'/'.join(cle)} : référence "
                    f"{self.format(ancienne)}{self.unite}, source {texte}{self.unite} "
                    f"(niveau {ligne['fiabilite']})"
                )
            else:
                identiques += 1
            if appliquer:
                ligne[self.colonne] = texte
                ligne["fiabilite"] = self.niveau

        if appliquer:
            lignes.sort(key=lambda l: tuple(
                float(l[c]) if c in CLES_NUMERIQUES else l[c]
                for c in self.cles
            ))
            _ecrire(self.chemin, commentaires, champs, lignes)

        verbe = ("versées au niveau " + self.niveau) if appliquer else "confrontables"
        messages = [
            f"OK      {self.nom} : {len(attendu)} valeurs {verbe} depuis {self.origine} "
            f"— {identiques} identiques, {len(corrigees)} corrigées, "
            f"{len(ajoutees)} ajoutées"
        ]
        messages.extend(ecarts[:12])
        if len(ecarts) > 12:
            messages.append(f"        … et {len(ecarts) - 12} autres écarts")

        journal = {
            "source": self.origine,
            "niveau": self.niveau,
            # Le jour du passage, valeurs changées ou non : c'est ce qui rend
            # l'absence de diff lisible — la fiche a été relue ce jour-là.
            "verifiee_le": date.today().isoformat(),
            # Deux contrôles peuvent porter sur les mêmes LIGNES et des COLONNES
            # différentes — la décote de la fonction publique, dont un article
            # fixe le coefficient et l'âge d'annulation dans le même tableau.
            # Sans le nom de la colonne, on ne saurait pas si deux traces
            # comptent deux fois les mêmes lignes.
            "colonne": self.colonne,
            "valeurs": len(attendu),
            "identiques": identiques,
            "corrigees": len(corrigees),
            "ajoutees": len(ajoutees),
            "empreinte": hashlib.sha256(
                "".join(f"{'/'.join(c)}={self.format(v)};"
                        for c, v in attendu.items()).encode()
            ).hexdigest()[:16],
        }
        return messages, journal


CERTIFICATIONS = (
    Certification(
        nom="courbe_taux_sans_risque",
        chemin=REFERENCE / "macro" / "courbe_taux_sans_risque.csv",
        cles=("date", "maturite"),
        colonne="taux_continu",
        source=source_courbe_taux_sans_risque,
        origine="BCE, portail de données, jeu YC (souverains AAA, Svensson)",
        decimales=8,
        tolerance=1e-8,
        entete=(
            "# Courbe des taux sans risque de la zone euro — zéro-coupon par maturité",
            "# source_id: bce_courbe_taux_aaa",
            "# unite: taux zéro-coupon à COMPOSITION CONTINUE, en fraction. Le taux",
            "#        annuel équivalent est exp(taux_continu) - 1 ; la conversion est",
            "#        faite par le modèle, pas à la saisie.",
            "# fiabilite:",
            "#   certifiee : valeurs relevées sur le portail de données de la BCE, qui",
            "#               estime et publie cette courbe, et recontrôlées par",
            "#               scripts/verifier_donnees.py.",
            "#",
            "# Une courbe est un INSTANTANÉ : chaque ligne porte sa date d'observation,",
            "# et le modèle lit la plus récente. Les courbes passées restent ici pour",
            "# que l'on puisse refaire un calcul tel qu'il a été publié.",
            "#",
            "# Ces taux servent au seul pilier de capitalisation obligatoire de la",
            "# proposition : ils disent à quel taux un versement se place pour une durée",
            "# donnée, et, par leurs forwards implicites, à quel taux les versements des",
            "# années suivantes se placeront. La courbe AAA rend moins que l'OAT",
            "# française — 51 points de base au 10 ans en septembre 2026 — et c'est",
            "# voulu : cet écart rémunère un risque de crédit, qu'un régime obligatoire",
            "# ne peut pas promettre. Voir docs/methodologie.md.",
            "#",
            "# Ne pas modifier à la main : les valeurs seraient écrasées au prochain",
            "# scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="inflation",
        chemin=REFERENCE / "macro" / "ipc_annuel.csv",
        cles=("annee",),
        colonne="variation",
        source=source_inflation,
        origine="INSEE BDM, idbanks 000008965 et 001764363",
        decimales=5,
        tolerance=5e-4,
        unite="",
    ),
    Certification(
        nom="salaire_moyen",
        chemin=REFERENCE / "macro" / "salaire_moyen.csv",
        cles=("annee",),
        colonne="variation_nominale",
        source=source_salaire_moyen,
        origine="INSEE BDM, idbanks 011785411 et 011793486",
        decimales=5,
        tolerance=5e-4,
    ),
    Certification(
        nom="masse_salariale",
        chemin=REFERENCE / "macro" / "masse_salariale.csv",
        cles=("annee",),
        colonne="variation_nominale",
        source=source_masse_salariale,
        origine="INSEE BDM, idbank 011785411",
        decimales=5,
        tolerance=5e-4,
        entete=(
            "# Masse salariale — variation annuelle nominale, ensemble de l'économie",
            "# source_id: insee_bdm_masse_salariale (comptes nationaux annuels, base 2020)",
            "# unite: taux de variation annuel nominal, en fraction",
            "# fiabilite:",
            "#   certifiee (1950-2025) : salaires et traitements bruts (D11, total des",
            "#             branches, idbank 011785411) pris EN NIVEAU, recontrôlés par",
            "#             scripts/verifier_donnees.py.",
            "#   estimee   (1930-1949) : les comptes nationaux ne remontent pas avant",
            "#             1949, et aucune série d'emploi salarié ne couvre la guerre.",
            "#             Ces vingt années reprennent donc la variation du SALAIRE",
            "#             MOYEN, c'est-à-dire supposent l'emploi salarié constant.",
            "#             L'hypothèse est fausse — l'emploi s'est effondré puis",
            "#             reconstitué — mais elle est la seule qui n'invente rien, et",
            "#             la fiabilité `estimee` se propage jusqu'au résultat.",
            "#",
            "# C'est l'assiette des cotisations : le taux de rendement qu'un système en",
            "# répartition peut servir sans changer son taux de cotisation (Samuelson",
            "# 1958, Aaron 1966). La différence avec salaire_moyen.csv est exactement la",
            "# croissance de l'emploi salarié : ×2,14 sur 1950-2025.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="assiette_salaires",
        chemin=REFERENCE / "macro" / "assiette_activite.csv",
        cles=("annee", "poste"),
        colonne="montant_meur",
        source=source_assiette_salaires,
        origine="INSEE BDM, idbank 011785411 (D11, total des branches)",
        decimales=1,
        tolerance=0.05,
        unite=" M€",
        entete=(
            "# Assiette des revenus d'activité, en niveau — France",
            "# source_id: insee_assiette_activite",
            "# unite: millions d'euros courants",
            "# fiabilite:",
            "#   certifiee (1949-) : comptes nationaux annuels base 2020, lus chez",
            "#             l'INSEE et recontrôlés par scripts/verifier_donnees.py.",
            "#             `salaires_bruts` vient de la banque de données",
            "#             macroéconomiques (idbank 011785411), `revenu_mixte` du",
            "#             tableau économique d'ensemble exposé par Melodi",
            "#             (opération B3G, secteur S14).",
            "#",
            "# À QUOI CETTE SÉRIE SERT",
            "# ------------------------",
            "# À dire SUR QUOI l'on prélève, et donc ce qu'un taux de cotisation",
            "# rapporte réellement. Le reste du dépôt travaille en rapports — de",
            "# masses de pension, de cotisations — parce qu'un rapport est robuste ;",
            "# mais un rapport de taux LÉGAUX appliqué à des ressources OBSERVÉES",
            "# transporte avec lui la structure du dénominateur, exonérations",
            "# comprises. C'est cette série qui permet de le voir : en 2024, les",
            "# deux postes font 1 250 Md€, soit 42,5 % du PIB, et le système de",
            "# retraite y prélève 24,9 points de cotisations là où le taux légal",
            "# d'un salarié type est de 28 à 29 %.",
            "#",
            "# LES DEUX POSTES, ET POURQUOI IL EN FAUT DEUX",
            "# ---------------------------------------------",
            "# `salaires_bruts` est l'assiette des salariés : c'est sur le salaire",
            "# brut que les deux parts de la cotisation sont calculées, et c'est",
            "# aussi sur le traitement que l'État verse sa contribution d'équilibre.",
            "# `revenu_mixte` est celle des non-salariés. Les additionner suppose",
            "# que l'on tienne le revenu mixte pour un revenu du TRAVAIL, ce qu'il",
            "# n'est qu'en partie : il rémunère aussi le capital de l'entrepreneur",
            "# individuel. Le compte national ne les sépare pas, l'assiette sociale",
            "# non plus, et la convention est donc celle des deux.",
            "#",
            "# UN CONTRÔLE EXTERNE, ET IL TOMBE À 3,8 %",
            "# -----------------------------------------",
            "# Le tableau 2.11 du rapport annuel du COR chiffre l'ajustement",
            "# nécessaire à l'équilibre DEUX FOIS : en pour-cent de la masse de",
            "# pension et en points de taux de prélèvement. Le rapport des deux",
            "# donne son assiette sans qu'il ait eu à la publier — 3,19 fois la",
            "# masse de pension, soit 1 298 Md€ en 2024 contre 1 250 ici. Les deux",
            "# routes sont indépendantes : l'une ne doit rien au COR, l'autre rien",
            "# à l'INSEE.",
            "#",
            "# Ne pas modifier à la main : les valeurs seraient écrasées au prochain",
            "# scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="assiette_revenu_mixte",
        chemin=REFERENCE / "macro" / "assiette_activite.csv",
        cles=("annee", "poste"),
        colonne="montant_meur",
        source=source_assiette_revenu_mixte,
        origine="INSEE Melodi, DD_CNA_TEE (B3G du secteur S14)",
        decimales=1,
        tolerance=0.05,
        unite=" M€",
    ),
    Certification(
        nom="profil_salaire_age",
        chemin=REFERENCE / "macro" / "profil_salaire_age.csv",
        cles=("annee", "tranche"),
        colonne="salaire_relatif",
        source=source_profil_salaire_age,
        origine="INSEE Melodi, DS_DERA_PRIVE_SERIES_LONGUES",
        decimales=4,
        tolerance=5e-4,
        entete=(
            "# Salaire par tranche d'âge, rapporté au salaire moyen de l'année",
            "# source_id: insee_profil_salaire_age",
            "# unite: rapport sans dimension (1,00 = salaire moyen de l'année)",
            "# fiabilite:",
            "#   certifiee (1962-2024, tranches 26-60) : salaire net mensuel en",
            "#             équivalent temps plein, à temps complet, euros constants,",
            "#             recontrôlé par scripts/verifier_donnees.py.",
            "#   certifiee (1996-2024, moins de 26 et plus de 60) : mêmes séries, que",
            "#             l'INSEE ne ventile pas plus tôt sur ces deux bords.",
            "#",
            "# CE QUE CE FICHIER N'EST PAS. Un profil de carrière. Il est AGRÉGÉ :",
            "# il mélange l'effet d'âge et un effet de composition, les jeunes étant",
            "# plus souvent dans les catégories les moins payées. Son écart entre",
            "# les bords vaut 0,46 en 2024, celui des ouvriers 0,24 — le lire comme",
            "# une carrière individuelle surestimerait la progression du double.",
            "# Le modèle ne lui demande que l'ÉVOLUTION de cet écart, qui porte",
            "# l'effet de génération : 1,19 entre 51-60 ans et 26-30 ans en 1962,",
            "# 1,47 en 2000, 1,35 en 2024. La FORME vient de",
            "# profil_salaire_categorie.csv.",
            "#",
            "# Ne pas modifier à la main : les valeurs seraient écrasées au prochain",
            "# scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="profil_salaire_categorie",
        chemin=REFERENCE / "macro" / "profil_salaire_categorie.csv",
        cles=("categorie", "tranche"),
        colonne="salaire_relatif",
        source=source_profil_salaire_categorie,
        origine="INSEE Melodi, DS_DERA_PRIVE_ANNUEL (2024)",
        decimales=4,
        tolerance=5e-4,
        entete=(
            "# Profil d'âge par catégorie socioprofessionnelle, privé, 2024",
            "# source_id: insee_profil_salaire_categorie",
            "# unite: rapport sans dimension (1,00 = moyenne de la catégorie)",
            "# fiabilite:",
            "#   certifiee (2024) : salaire net mensuel en équivalent temps plein, à",
            "#             temps complet, recontrôlé par scripts/verifier_donnees.py.",
            "#",
            "# C'EST LE PROFIL D'UNE CARRIÈRE, et le seul : une personne progresse",
            "# dans sa catégorie, elle ne traverse pas la structure d'emploi. Ce jeu",
            "# est le seul des trois à croiser l'âge et la catégorie — ni la série",
            "# longue du privé ni celle du public ne le font — et il ne porte qu'une",
            "# année. Sa forme est donc supposée stable dans le temps, ce que rien",
            "# ne démontre et que docs/limites.md dit.",
            "#",
            "# Ne pas modifier à la main : les valeurs seraient écrasées au prochain",
            "# scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="profil_salaire_public",
        chemin=REFERENCE / "macro" / "profil_salaire_statut_public.csv",
        cles=("statut", "tranche"),
        colonne="salaire_relatif",
        source=source_profil_salaire_public,
        origine="INSEE Melodi, DS_DERA_PUBLIC_ANNUEL (2023)",
        decimales=4,
        tolerance=5e-4,
        entete=(
            "# Profil d'âge de la fonction publique, par statut et par versant",
            "# source_id: insee_profil_salaire_public",
            "# unite: rapport sans dimension (1,00 = moyenne du groupe)",
            "# fiabilite:",
            "#   certifiee (2023) : salaire net mensuel en équivalent temps plein, à",
            "#             temps complet, recontrôlé par scripts/verifier_donnees.py.",
            "#",
            "# Le profil du privé qu'on appliquait aux fonctionnaires était trop",
            "# pentu pour les catégories B et C — ×1,30 servi contre ×1,22 et ×1,11",
            "# observés de 26 à 55 ans — et trop plat pour un catégorie A, qui fait",
            "# ×1,56. Les trois VERSANTS sont ici pour les affiliations, qui ne",
            "# portent pas la catégorie : leur profil pondère les catégories par",
            "# leurs effectifs réels, et ne suppose rien.",
            "#",
            "# CE QU'IL N'Y A PAS : les militaires. Le code PM de ce jeu désigne les",
            "# personnels MÉDICAUX de l'hospitalière, à 6 765 € nets par mois, et non",
            "# des militaires. Aucun jeu de l'INSEE ne porte la solde indiciaire par",
            "# âge : les cas types militaires gardent le profil de l'État.",
            "#",
            "# Ne pas modifier à la main : les valeurs seraient écrasées au prochain",
            "# scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="profil_salaire_secteur",
        chemin=REFERENCE / "macro" / "profil_salaire_secteur.csv",
        cles=("secteur", "vague", "tranche"),
        colonne="salaire_relatif",
        source=source_profil_salaire_secteur,
        origine="Eurostat, earn_ses18_20 et earn_ses22_20 (France)",
        decimales=4,
        tolerance=5e-4,
        entete=(
            "# Profil de salaire par âge et par section d'activité, France",
            "# source_id: eurostat_profil_salaire_secteur",
            "# unite: rapport sans dimension (1,00 = moyenne de la section)",
            "# fiabilite:",
            "#   certifiee (2018, 2022) : enquête quadriennale sur la structure des",
            "#             salaires, salaire mensuel brut moyen, recontrôlé par",
            "#             scripts/verifier_donnees.py. La France ne publie que trois",
            "#             tranches d'âge à ce niveau ; 2010 et 2014 ne répondent pas,",
            "#             2006 n'a pas la dimension d'activité.",
            "#",
            "# POURQUOI CETTE SOURCE EXISTE ICI. Les régimes spéciaux portaient le",
            "# profil des employés du privé faute de mieux. La section D est le champ",
            "# des industries électriques et gazières, la section H celui où sont la",
            "# SNCF et la RATP : aucune source FRANÇAISE ne ventile le salaire par âge",
            "# pour ces populations.",
            "#",
            "# CE QU'ELLE N'EST PAS : un profil de carrière. Elle est AGRÉGÉE par",
            "# secteur — aucune source ne croise l'âge, le secteur et la profession,",
            "# vérifié chez Eurostat comme chez l'INSEE. Le modèle ne lui prend qu'un",
            "# RAPPORT de pentes, secteur sur ensemble, ce qui suppose ce rapport",
            "# identique à l'intérieur des catégories et en agrégé. Rien ne le",
            "# démontre, et docs/limites.md le dit.",
            "#",
            "# Ne pas modifier à la main : les valeurs seraient écrasées au prochain",
            "# scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="pib_nominal",
        chemin=REFERENCE / "macro" / "pib_nominal.csv",
        cles=("annee",),
        colonne="variation_nominale",
        source=source_pib_nominal,
        origine="INSEE BDM, idbank 011779992",
        decimales=5,
        tolerance=5e-4,
        entete=(
            "# Produit intérieur brut — variation annuelle nominale, France",
            "# source_id: insee_bdm_pib (comptes nationaux annuels, base 2020)",
            "# unite: taux de variation annuel nominal, en fraction",
            "# fiabilite:",
            "#   certifiee (1950-2025) : PIB approche produit, prix courant",
            "#             (idbank 011779992), recontrôlé par",
            "#             scripts/verifier_donnees.py.",
            "#   estimee   (1930-1949) : les comptes nationaux ne remontent pas avant",
            "#             1949. Ces vingt années reprennent la variation du salaire",
            "#             moyen, faute de mieux — même convention que",
            "#             masse_salariale.csv, et même réserve.",
            "#",
            "# Sert la variante « à l'italienne » de l'indexation : l'Italie revalorise",
            "# les comptes notionnels sur la moyenne géométrique du PIB nominal des cinq",
            "# dernières années. Le LISSAGE est appliqué par le moteur, pas ici : cette",
            "# série est la variation annuelle brute, seule grandeur que l'INSEE publie",
            "# et donc seule grandeur certifiable.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="pib_courant",
        chemin=REFERENCE / "macro" / "pib_courant.csv",
        cles=("annee",),
        colonne="pib_meur",
        source=source_pib_courant,
        origine="INSEE BDM, idbank 011779992",
        decimales=0,
        tolerance=0.51,
        unite=" M€",
        entete=(
            "# Produit intérieur brut en NIVEAU, prix courants, France",
            "# source_id: insee_bdm_pib (comptes nationaux annuels, base 2020)",
            "# unite: millions d'euros courants de l'année",
            "# fiabilite:",
            "#   certifiee (1949-2025) : PIB approche produit, prix courant",
            "#             (idbank 011779992), recontrôlé par",
            "#             scripts/verifier_donnees.py.",
            "#",
            "# pib_nominal.csv porte la VARIATION de la même série, qui suffit à",
            "# l'indexation. Rapporter une dépense au PIB demande le NIVEAU, et c'est",
            "# la seule raison d'être de ce fichier : il ne double pas une donnée, il",
            "# en lit une autre grandeur.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="dette_publique",
        chemin=REFERENCE / "macro" / "dette_publique.csv",
        cles=("annee",),
        colonne="part_pib",
        source=source_dette_publique,
        origine="INSEE BDM, idbank 010777608 (quatrième trimestre)",
        decimales=3,
        tolerance=5.1e-4,
        entete=(
            "# Dette des administrations publiques au sens de Maastricht, France",
            "# source_id: insee_bdm_dette_publique (comptes nationaux, base 2020)",
            "# unite: part du produit intérieur brut, en fraction",
            "# fiabilite:",
            "#   certifiee (1995-…) : stock au 31 décembre rapporté au PIB des quatre",
            "#             derniers trimestres, quatrième trimestre de la série",
            "#             trimestrielle en point de PIB (idbank 010777608),",
            "#             recontrôlé par scripts/verifier_donnees.py.",
            "#",
            "# C'est la dette de TOUTES les administrations publiques — État,",
            "# organismes divers, collectivités locales, Sécurité sociale —, brute et",
            "# consolidée, au périmètre que la France notifie à la Commission",
            "# européenne. Elle ne sert à aucun calcul de pension : la page Coût la",
            "# pose sous ce que chaque système de retraite accumule, pour que le",
            "# stock d'un système se lise à l'échelle de celui que le pays porte déjà.",
            "#",
            "# POURQUOI LE QUATRIÈME TRIMESTRE D'UNE SÉRIE TRIMESTRIELLE",
            "# --------------------------------------------------------",
            "# Les séries annuelles de la BDM sont restées dans les bases 2010 et",
            "# 2014 des comptes nationaux ; seule la trimestrielle est en base 2020,",
            "# celle de pib_courant.csv. Un rapport au PIB ne se lit que dans la",
            "# base du PIB qu'on lui oppose, et le stock au 31 décembre rapporté au",
            "# PIB des quatre derniers trimestres EST la dette annuelle.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="population_par_age",
        chemin=REFERENCE / "macro" / "population_par_age.csv",
        cles=("annee", "age"),
        colonne="effectif",
        source=lambda: {
            cle: valeur for cle, valeur in source_population_par_age().items()
            if int(cle[0]) <= DERNIERE_ANNEE_POPULATION_OBSERVEE
        },
        origine="INSEE, estimations de population, scénario central des "
                "projections 2026",
        decimales=0,
        tolerance=0.51,
        entete=(
            "# Population au 1er janvier par âge, France, 50 ans et plus",
            "# source_id: insee_projections_population",
            "# unite: personnes",
            "# fiabilite:",
            "#   certifiee (1962-2023) : estimations de population de l'INSEE,",
            "#             recontrôlées par scripts/verifier_donnees.py contre",
            "#             l'onglet `population` du classeur du scénario central.",
            "#   estimee   (2024-2070) : projections de population 2026, scénario",
            "#             central. Une projection ne se fait pas passer pour une",
            "#             observation, fût-elle publiée par le producteur de",
            "#             l'observation : c'est le critère 2 du manifeste, et la",
            "#             frontière est datée par l'INSEE lui-même en pied de",
            "#             tableau.",
            "#",
            "# POURQUOI 50 ANS ET PLUS, ET PAS TOUS LES ÂGES",
            "# ----------------------------------------------",
            "# Cette série ne sert qu'à compter des RETRAITÉS. Aucune pension de",
            "# droit direct n'est servie avant 50 ans — le cas type qui part le plus",
            "# tôt, l'agent de conduite de la SNCF, liquide à 52 ans. Reprendre les",
            "# cinquante premiers âges quadruplerait le poids du paquet que charge",
            "# le site sans déplacer un seul chiffre.",
            "#",
            "# Au-delà de 104 ans, le classeur regroupe sous « 105 ans ou plus » :",
            "# 1 570 personnes en 2024, deux millionièmes de la population. Ce",
            "# regroupement reste dehors.",
            "#",
            "# Champ : France métropolitaine jusqu'en 1994, France hors Mayotte de",
            "# 1995 à 2013, France entière ensuite — celui de l'INSEE, non retouché.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="population_par_age_projetee",
        chemin=REFERENCE / "macro" / "population_par_age.csv",
        cles=("annee", "age"),
        colonne="effectif",
        source=lambda: {
            cle: valeur for cle, valeur in source_population_par_age().items()
            if int(cle[0]) > DERNIERE_ANNEE_POPULATION_OBSERVEE
        },
        origine="INSEE, projections de population 2026, scénario central",
        decimales=0,
        tolerance=0.51,
        niveau="projetee",
    ),
    Certification(
        nom="population_active",
        chemin=REFERENCE / "macro" / "population_active.csv",
        cles=("annee",),
        colonne="effectif",
        source=lambda: {
            cle: valeur for cle, valeur in source_population_active().items()
            if int(cle[0]) <= DERNIERE_ANNEE_POPULATION_OBSERVEE
        },
        origine="INSEE, estimations de population, scénario central des "
                "projections 2026",
        decimales=0,
        tolerance=0.51,
        entete=(
            "# Population des 20 à 64 ans au 1er janvier, France",
            "# source_id: insee_projections_population",
            "# unite: personnes",
            "# fiabilite:",
            "#   certifiee (1962-2023) : estimations de population de l'INSEE.",
            "#   estimee   (2024-2070) : projections de population 2026, scénario",
            "#             central.",
            "#",
            "# À QUOI ELLE SERT, ET À QUOI ELLE NE SERT PAS",
            "# ---------------------------------------------",
            "# Elle ne compte aucun retraité : elle projette le DÉNOMINATEUR d'une",
            "# part de PIB. hypotheses_projection.yaml suppose l'emploi salarié",
            "# constant au-delà de la dernière année observée, et le dit neutre.",
            "# L'hypothèse est effectivement neutre pour l'indexation des comptes,",
            "# qui ne dépend que d'un taux de croissance ; elle ne l'est pas du tout",
            "# pour une dépense rapportée au PIB, où elle prêterait à la France de",
            "# 2070 douze pour cent d'actifs qu'aucune projection ne lui donne.",
            "#",
            "# Ce n'est pas non plus la population ACTIVE au sens du BIT — le",
            "# classeur de l'INSEE ne la projette pas. C'est la population d'âge",
            "# actif, dont on suppose le taux d'emploi constant. L'écart entre les",
            "# deux est une hypothèse assumée, et elle est écrite là où elle joue :",
            "# docs/limites.md, §5 ter.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="population_active_projetee",
        chemin=REFERENCE / "macro" / "population_active.csv",
        cles=("annee",),
        colonne="effectif",
        source=lambda: {
            cle: valeur for cle, valeur in source_population_active().items()
            if int(cle[0]) > DERNIERE_ANNEE_POPULATION_OBSERVEE
        },
        origine="INSEE, projections de population 2026, scénario central",
        decimales=0,
        tolerance=0.51,
        niveau="projetee",
    ),
    Certification(
        nom="depenses_retraite",
        chemin=REFERENCE / "macro" / "depenses_retraite.csv",
        cles=("annee",),
        colonne="depenses_meur",
        source=source_depenses_retraite,
        origine="DREES, Comptes de la protection sociale, risque vieillesse-survie",
        decimales=1,
        tolerance=0.051,
        unite=" M€",
        entete=(
            "# Dépenses du risque vieillesse-survie, tous régimes, France",
            "# source_id: drees_comptes_protection_sociale",
            "# unite: millions d'euros courants de l'année",
            "# fiabilite:",
            "#   certifiee (1959-2024) : prestations du poste E11-2 des Comptes de la",
            "#             protection sociale, recontrôlées par",
            "#             scripts/verifier_donnees.py contre l'API de la DREES.",
            "#",
            "# CE QUE CE POSTE CONTIENT, ET CE QU'IL N'EST PAS",
            "# ------------------------------------------------",
            "# C'est le risque vieillesse-survie TOUT ENTIER : pensions de droit direct",
            "# et de droit dérivé, mais aussi minimum vieillesse, prestations liées à la",
            "# dépendance des personnes âgées, retraite supplémentaire par",
            "# capitalisation. Il est donc PLUS LARGE que « les dépenses de retraite »",
            "# au sens où le Conseil d'orientation des retraites les entend, et le",
            "# dépasse d'environ 6 % : 426,7 milliards en 2024 contre 401,4 milliards",
            "# pour les seules pensions de droit direct et de droit dérivé.",
            "#",
            "# C'est pourtant lui qu'on retient, et pour une raison : il est le seul",
            "# niveau que la DREES publie SANS INTERRUPTION depuis 1959. Les",
            "# sous-postes ne le sont que depuis 2020. Un agrégat continu sur",
            "# soixante-six ans, dont on sait dire ce qu'il contient, vaut mieux qu'un",
            "# agrégat plus juste qui commence il y a cinq ans.",
            "#",
            "# depenses_retraite_regimes.csv le ventile, et cette ventilation permet",
            "# d'en retrancher ce qui ne relève pas de la répartition obligatoire.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="depenses_retraite_regimes",
        chemin=REFERENCE / "macro" / "depenses_retraite_regimes.csv",
        cles=("annee", "regime"),
        colonne="depenses_meur",
        source=source_depenses_retraite_regimes,
        origine="DREES, Comptes de la protection sociale, risque vieillesse-survie "
                "par organisme",
        decimales=1,
        tolerance=0.051,
        unite=" M€",
        entete=(
            "# Dépenses du risque vieillesse-survie, ventilées par système, France",
            "# source_id: drees_comptes_protection_sociale",
            "# unite: millions d'euros courants de l'année",
            "# fiabilite:",
            "#   certifiee (1990-2024) : prestations du poste E11-2 par organisme,",
            "#             regroupées selon REGIMES_CPS dans",
            "#             scripts/verifier_donnees.py, qui les recontrôle contre",
            "#             l'API de la DREES et vérifie que leur somme rend le total.",
            "#",
            "# POURQUOI LA VENTILATION NE COMMENCE QU'EN 1990",
            "# -----------------------------------------------",
            "# La DREES ventile bien le risque depuis 1981, mais dans une nomenclature",
            "# différente — « Régime général de la Sécurité sociale », « Régimes",
            "# spéciaux », « Régimes de l'État et des entreprises publiques » — dont",
            "# les périmètres ne se recoupent pas avec ceux de 1990 : les",
            "# complémentaires n'y sont pas encore séparées de l'Agirc et de l'Arrco.",
            "# Personne n'a publié le raccord. Ces neuf années sont une impasse, et",
            "# le total, lui, les couvre depuis 1959.",
            "#",
            "# LE DÉCOUPAGE EST CELUI DE LA COMPTABILITÉ NATIONALE",
            "# ----------------------------------------------------",
            "# La DREES ventile par SECTEUR INSTITUTIONNEL et non par caisse. Deux",
            "# conséquences qu'il faut connaître pour lire ces chiffres :",
            "#   * « regimes_speciaux » réunit la CNRACL, la SNCF, la RATP, les IEG et",
            "#     les autres — la fonction publique territoriale et hospitalière y est",
            "#     donc, et non avec l'État ;",
            "#   * « regime_general » absorbe, à compter de 2020, les artisans et les",
            "#     commerçants, dont le régime a été adossé à la Cnav.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="comptes_retraite",
        chemin=REFERENCE / "macro" / "comptes_retraite.csv",
        cles=("annee", "poste"),
        colonne="part_pib",
        source=source_comptes_retraite,
        origine="COR, rapport annuel, comptes du système de retraite "
                "(rapports à la CCSS consolidés)",
        decimales=6,
        tolerance=5.1e-7,
        # Une consolidation de comptes produits par d'autres ne peut pas être
        # certifiée : c'est le critère 1 du manifeste, le même qui plafonne
        # OpenFisca. Le COR est pourtant seul à l'établir, et c'est à ce titre
        # qu'elle entre.
        niveau="haute",
        entete=(
            "# Dépenses et ressources du système de retraite, en part du PIB",
            "# source_id: cor_comptes_systeme_retraite",
            "# unite: part du produit intérieur brut, en fraction",
            "# fiabilite:",
            "#   haute    (2002-…) : compte observé du système de retraite, consolidé",
            "#             par le COR depuis les rapports à la Commission des comptes",
            "#             de la Sécurité sociale, recontrôlé par",
            "#             scripts/verifier_donnees.py contre les classeurs de données",
            "#             du dernier rapport annuel.",
            "#   projetee (…-2070) : scénario de référence du même rapport. Une",
            "#             projection ne se fait pas passer pour une observation ; la",
            "#             frontière est celle que le COR marque lui-même, colonne par",
            "#             colonne, « Obs » puis « Sc. Ref ».",
            "#",
            "# POURQUOI LE COR ET NON LA DREES, QUI PUBLIE LES DÉPENSES",
            "# ---------------------------------------------------------",
            "# Les Comptes de la protection sociale, d'où vient depenses_retraite.csv,",
            "# NE VENTILENT PAS LEURS RESSOURCES PAR RISQUE : le jeu 305 de la DREES",
            "# ne porte que des prestations, et son classeur annexe donne les",
            "# ressources de la protection sociale tout entière, maladie et famille",
            "# comprises. Il n'existe donc pas de « recettes du risque vieillesse »",
            "# chez le producteur des dépenses. Le compte du SYSTÈME DE RETRAITE,",
            "# lui, est publié — dépenses, ressources et solde du même périmètre,",
            "# sous la même convention — et par le seul COR.",
            "#",
            "# CE N'EST PAS LE PÉRIMÈTRE DE depenses_retraite.csv",
            "# ---------------------------------------------------",
            "# Champ : ensemble des régimes de retraite français légalement",
            "# obligatoires, y compris le FSV, hors RAFP. C'est plus étroit que le",
            "# risque vieillesse-survie de la DREES — ni dépendance, ni",
            "# capitalisation — et un peu plus large que sa « répartition",
            "# obligatoire » : 13,86 % du PIB en 2024 contre 13,59 %. Les deux séries",
            "# ne se soustraient donc pas l'une de l'autre, et le solde de ce fichier",
            "# est celui de SES DEUX colonnes, jamais d'une colonne empruntée ailleurs.",
            "#",
            "# Convention EPR, hors produits et charges financières, hors dotations et",
            "# reprises sur provisions — celle sous laquelle le COR suit l'objectif de",
            "# pérennité financière.",
            "#",
            "# Ne pas modifier ces valeurs à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="comptes_retraite_projetes",
        chemin=REFERENCE / "macro" / "comptes_retraite.csv",
        cles=("annee", "poste"),
        colonne="part_pib",
        source=source_comptes_retraite_projetes,
        origine="COR, rapport annuel, scénario de référence",
        decimales=6,
        tolerance=5.1e-7,
        niveau="projetee",
    ),
    Certification(
        nom="structure_ressources_retraite",
        chemin=REFERENCE / "macro" / "structure_ressources_retraite.csv",
        cles=("annee", "poste"),
        colonne="part",
        source=source_structure_ressources,
        origine="COR, rapport annuel, structure des ressources du système de retraite",
        decimales=5,
        tolerance=5.1e-6,
        niveau="haute",
        entete=(
            "# Structure des ressources du système de retraite, par poste",
            "# source_id: cor_comptes_systeme_retraite",
            "# unite: part des ressources de l'année, en fraction",
            "# fiabilite:",
            "#   haute (2004-…) : parts publiées par le COR dans son rapport annuel,",
            "#             calculées par le SG-COR sur les rapports à la Commission",
            "#             des comptes de la Sécurité sociale, et recontrôlées par",
            "#             scripts/verifier_donnees.py contre le classeur du rapport.",
            "#",
            "# À QUOI CETTE SÉRIE SERT",
            "# ------------------------",
            "# À dire ce que « ressources » contient. Deux tiers sont des cotisations",
            "# assises sur des revenus d'activité, c'est-à-dire la seule chose qu'un",
            "# compte notionnel sache créditer. Le reste ne l'est pas : la",
            "# contribution d'équilibre que l'État verse au régime de ses propres",
            "# fonctionnaires — dont le taux est fixé pour ÉQUILIBRER et non pour",
            "# acquérir —, des impôts et taxes affectés, des subventions d'équilibre",
            "# aux régimes spéciaux, des transferts de la branche famille et de",
            "# l'Unédic. Le coefficient d'équilibre de la page « Coût » suppose ces",
            "# ressources-là inchangées ; ces parts disent de quoi cette hypothèse",
            "# est faite.",
            "#",
            "# Ne pas modifier ces valeurs à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="part_droits_derives",
        chemin=REFERENCE / "macro" / "part_droits_derives.csv",
        cles=("annee",),
        colonne="part",
        source=source_part_droits_derives,
        origine="COR, compléments du rapport annuel de juin 2024, "
                "masses de pensions de droit direct et de droit dérivé",
        decimales=6,
        tolerance=5.1e-7,
        niveau="haute",
        entete=(
            "# La part des pensions de RÉVERSION dans la masse versée",
            "# source_id: cor_regimes",
            "# unite: part de la masse de prestations, en fraction",
            "# fiabilite:",
            "#   haute (2010-2070) : masses publiées par le COR dans les",
            "#             compléments de son rapport annuel, recomposées par",
            "#             scripts/verifier_donnees.py et recontrôlées contre la",
            "#             ventilation que la DREES publie de son côté.",
            "#",
            "# À QUOI CETTE SÉRIE SERT",
            "# ------------------------",
            "# À ne pas recalculer une réversion que le modèle ne calcule pas.",
            "# Le rapport de masses par lequel cout.py fait réagir la dépense est",
            "# celui des droits DIRECTS des treize cas types ; la base à laquelle",
            "# il s'applique porte aussi les droits dérivés. Sans cette part, un",
            "# scénario notionnel réduisait la réversion dans la même proportion",
            "# que les pensions de droit direct, sans que rien ne l'ait décidé.",
            "#",
            "# CE QU'ELLE DIT, ET IL FAUT LE LIRE",
            "# -----------------------------------",
            "# La réversion recule, et c'est la projection du COR qui le dit :",
            "# 12,4 % de la masse en 2010, 10,4 % en 2024, 9,5 % en 2040, 5,7 %",
            "# en 2070. Les carrières des femmes se rapprochent de celles des",
            "# hommes, et une pension de réversion différentielle s'éteint à",
            "# mesure que la pension propre du survivant monte.",
            "#",
            "# CE QU'IL FAUT SAVOIR AVANT DE S'EN SERVIR",
            "# ------------------------------------------",
            "# 1. ELLE EST CONSTRUITE. Douze des vingt-deux régimes du classeur",
            "#    publient leur droit dérivé à part ; pour les dix autres — dont",
            "#    la fonction publique d'État et la CNRACL, qui pèsent — c'est la",
            "#    différence entre la masse de prestations et le droit direct.",
            "#    Cette différence porte aussi un petit résidu de prestations qui",
            "#    n'est ni l'un ni l'autre : 0,3 % des prestations là où les trois",
            "#    blocs permettent de le mesurer. La part est donc très",
            "#    légèrement surestimée, et jamais de plus de ce résidu.",
            "# 2. LE MILLÉSIME est celui des compléments de JUIN 2024, seul",
            "#    publié, quand le reste du dépôt tourne sur le COR 2026.",
            "# 3. HORS DE 2010-2070, la valeur de bord est reconduite, et la",
            "#    fiabilité tombe à « estimée » : la dépense observée remonte à",
            "#    1959, cette ventilation non.",
            "# 4. LE RAFP EST ÉCARTÉ, le périmètre du système de retraite",
            "#    excluant la capitalisation ; le FSV n'a pas de masse de",
            "#    pensions à ventiler.",
            "#",
            "# pensions_droits.csv porte la ventilation de la DREES, qui la",
            "# contrôle sur 2020-2024.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient",
            "# écrasées au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="pensions_droits",
        chemin=REFERENCE / "macro" / "pensions_droits.csv",
        cles=("annee", "categorie"),
        colonne="montant_meur",
        source=source_pensions_droits,
        origine="DREES, Comptes de la protection sociale, postes E11-21.1 et "
                "E11-22.1",
        decimales=2,
        tolerance=0.011,
        unite=" M€",
        niveau="certifiee",
        entete=(
            "# Pensions de droit direct et de droit dérivé, tous régimes, France",
            "# source_id: drees_comptes_protection_sociale",
            "# unite: millions d'euros courants de l'année",
            "# fiabilite:",
            "#   certifiee (2020-2024) : sous-postes E11-21.1 et E11-22.1 des",
            "#             Comptes de la protection sociale, recontrôlés par",
            "#             scripts/verifier_donnees.py contre l'API de la DREES.",
            "#",
            "# POURQUOI SI COURT, ET POURQUOI QUAND MÊME",
            "# ------------------------------------------",
            "# La DREES ne publie ces deux sous-postes que depuis 2020, là où le",
            "# risque vieillesse-survie entier remonte à 1959. Cinq années ne",
            "# font pas une série, et celle-ci n'en est pas une : elle CONTRÔLE",
            "# part_droits_derives.csv, qui couvre 2010-2070 mais vient du COR.",
            "# Deux producteurs qui trouvent la même part de réversion à six",
            "# centièmes de point près valent mieux qu'un seul qui l'affirme.",
            "#",
            "# CE QUE LEUR SOMME N'EST PAS",
            "# ----------------------------",
            "# 401,4 milliards en 2024, contre 426,7 pour le risque",
            "# vieillesse-survie entier de depenses_retraite.csv. L'écart est le",
            "# minimum vieillesse, les prestations liées à la dépendance des",
            "# personnes âgées et la retraite supplémentaire, que le poste large",
            "# porte aussi.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient",
            "# écrasées au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="structure_financement_regimes",
        chemin=REFERENCE / "regimes" / "structure_financement.csv",
        cles=("annee", "regime", "poste"),
        colonne="part",
        source=source_structure_financement_regimes,
        origine="COR, compléments du rapport annuel de juin 2024, "
                "projections détaillées par régime",
        decimales=6,
        tolerance=5.1e-7,
        niveau="haute",
        entete=(
            "# Qui finance chaque régime : cotisations, État, transferts, et ce",
            "# que personne ne couvre",
            "# source_id: cor_regimes",
            "# unite: part du financement du régime pour l'année, en fraction",
            "# fiabilite:",
            "#   haute (2010-2070) : parts publiées par le COR dans les",
            "#             compléments de son rapport annuel, et recontrôlées par",
            "#             scripts/verifier_donnees.py contre son classeur.",
            "#",
            "# À QUOI CETTE SÉRIE SERT",
            "# ------------------------",
            "# À répondre à une question que structure_ressources_retraite.csv",
            "# ne sait poser que pour le système entier : un scénario qui",
            "# remplace tous les taux par 18 % déplace-t-il une charge vers",
            "# l'ÉTAT ou vers les CAISSES ? La réponse dépend du régime. L'État",
            "# finance 86 % de la fonction publique d'État par sa contribution",
            "# d'équilibre, et 61 % de la SNCF par une subvention ; la CNRACL ne",
            "# reçoit rien de lui et porte un besoin de financement que personne",
            "# ne couvre — 7 % en 2023, 49 % en 2070.",
            "#",
            "# CE QU'IL FAUT SAVOIR AVANT DE S'EN SERVIR",
            "# ------------------------------------------",
            "# 1. LE MILLÉSIME. Ces parts viennent des compléments du rapport de",
            "#    JUIN 2024, seul millésime publié : ni 2025 ni 2026 ne les ont",
            "#    reconduits. Le reste du dépôt tourne sur le COR 2026. Mélanger",
            "#    les deux coudrait deux exercices de projection.",
            "# 2. LES ANNÉES. Six seulement — 2010, 2015, 2023, 2030, 2040, 2050",
            "#    et 2070 selon les régimes — parce que le classeur ne publie",
            "#    cette ventilation qu'à ces dates-là. Ce n'est pas une série",
            "#    annuelle, et interpoler serait inventer.",
            "# 3. LES PARTS NE SOMMENT PAS TOUJOURS À UN. Cent couples (régime,",
            "#    année) sur 134 somment à un à un millième près ; les autres",
            "#    s'en écartent jusqu'à onze pour cent. C'est ce que le classeur",
            "#    publie, et on ne normalise pas.",
            "# 4. LA FONCTION PUBLIQUE D'ÉTAT EST D'UN SEUL TENANT, civils et",
            "#    militaires confondus, là où le reste du dépôt les sépare.",
            "#",
            "# Ne pas modifier ces valeurs à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="cotisants_regimes",
        chemin=REFERENCE / "regimes" / "cotisants.csv",
        cles=("annee", "caisse"),
        colonne="cotisants",
        source=source_cotisants_regimes,
        origine="COR, compléments du rapport annuel de juin 2024, "
                "projections détaillées par régime",
        decimales=0,
        tolerance=0.51,
        unite=" cotisants",
        niveau="haute",
        entete=(
            "# Cotisants de chaque régime, observés puis projetés",
            "# source_id: cor_regimes",
            "# unite: personnes",
            "# fiabilite:",
            "#   haute (2010-2070) : effectifs publiés par le COR dans les",
            "#             compléments de son rapport annuel, et recontrôlés par",
            "#             scripts/verifier_donnees.py contre son classeur.",
            "#",
            "# À QUOI CETTE SÉRIE SERT",
            "# ------------------------",
            "# À PONDÉRER les cas types du côté de la RECETTE. La page « Coût »",
            "# fait réagir la recette du système 4 par un rapport de cotisations",
            "# calculé sur la grille des cas types ; chaque cas type y pesait",
            "# jusqu'ici le nombre de RETRAITÉS de sa caisse, faute d'une série",
            "# de cotisants, ce qui surreprésentait les régimes qui s'éteignent.",
            "# Cette série donne les cotisants, et les projette : la SNCF n'en a",
            "# plus aucun en 2070, la CNIEG cinquante et un.",
            "#",
            "# CE QU'IL FAUT SAVOIR AVANT DE S'EN SERVIR",
            "# ------------------------------------------",
            "# 1. LE MILLÉSIME. Ces effectifs viennent des compléments du rapport",
            "#    de JUIN 2024, seul millésime publié : ni 2025 ni 2026 ne les",
            "#    ont reconduits. Le reste du dépôt tourne sur le COR 2026.",
            "# 2. L'ANNÉE DE DÉPART VARIE d'une caisse à l'autre : 2010 le plus",
            "#    souvent, 2015 pour la fonction publique d'État, 2019 pour le",
            "#    RCI, 2023 pour la CNRACL. Hors de la fenêtre de chaque caisse,",
            "#    la valeur de bord est reconduite au niveau « estimée ».",
            "# 3. UN COTISANT DE CAISSE N'EST PAS UNE PERSONNE : un polyaffilié",
            "#    compte dans chacune de ses caisses. Les poids qu'on en tire sont",
            "#    RELATIFS, comme ceux des retraités.",
            "# 4. LA FONCTION PUBLIQUE D'ÉTAT EST D'UN SEUL TENANT, civils et",
            "#    militaires confondus. Le partage entre les deux cas types qui",
            "#    la réclament est une décision du modèle, écrite dans",
            "#    donnees/cotisants.py.",
            "#",
            "# Ne pas modifier ces valeurs à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="transferts_retraite",
        chemin=REFERENCE / "macro" / "transferts_retraite.csv",
        cles=("annee", "poste"),
        colonne="montant_meur",
        source=source_transferts_retraite,
        origine="rapports à la Commission des comptes de la Sécurité sociale, "
                "fiches CNAF, Agirc-Arrco, Ircantec et CNAV",
        decimales=1,
        tolerance=0.06,
        unite=" M€",
        niveau="haute",
        entete=(
            "# Ce que la branche famille et l'assurance chômage versent à la retraite",
            "# source_id: dss_ccss_transferts_retraite",
            "# unite: millions d'euros courants de l'année",
            "# fiabilite:",
            "#   haute (2011-…) : comptes arrêtés, lus dans les rapports à la",
            "#             Commission des comptes de la Sécurité sociale — fiche de",
            "#             la CNAF (AVPF, majorations pour enfants), fiches de",
            "#             l'Agirc-Arrco et de l'Ircantec (points des chômeurs payés",
            "#             par l'Unédic) —, recontrôlés par scripts/verifier_donnees.py",
            "#             contre le rapport de l'année suivante, et confrontés au",
            "#             « dont CNAF, dont Unédic » du COR là où il existe.",
            "#",
            "# À QUOI CETTE SÉRIE SERT",
            "# ------------------------",
            "# Le poste « transferts d'organismes extérieurs » du compte du système",
            "# de retraite est un agrégat. Cette série le ventile par celui qui paie :",
            "# la CNAF finance les droits liés aux enfants — cotisations d'assurance",
            "# vieillesse des parents au foyer, majorations de pension pour trois",
            "# enfants —, l'Unédic les points de retraite complémentaire des",
            "# chômeurs. Le compte notionnel du dépôt SUPPRIME les droits que la",
            "# CNAF finance ; il ne peut pas compter comme acquise la recette qui",
            "# les paie, et c'est ici qu'on lit ce qu'elle vaut.",
            "#",
            "# Ne pas modifier ces valeurs à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="prestations_non_contributives",
        chemin=REFERENCE / "macro" / "prestations_non_contributives.csv",
        cles=("annee", "poste"),
        colonne="montant_meur",
        source=source_prestations_non_contributives,
        origine="DREES, Comptes de la protection sociale",
        decimales=2,
        tolerance=0.006,
        unite=" M€",
        entete=(
            "# Les prestations non contributives que les comptes isolent",
            "# source_id: drees_comptes_protection_sociale",
            "# unite: millions d'euros courants de l'année",
            "# fiabilite:",
            "#   certifiee (2020-…) : postes du risque vieillesse-survie des",
            "#             Comptes de la protection sociale, tous régimes,",
            "#             recontrôlés par scripts/verifier_donnees.py.",
            "#",
            "# À QUOI CETTE SÉRIE SERT",
            "# ------------------------",
            "# À chiffrer les avantages non contributifs que le modèle ne sait",
            "# pas mesurer, et surtout ceux qu'il mesurait FAUX. Un avantage se",
            "# mesure ici en refaisant la pension sans lui, sur treize carrières",
            "# types ; or cette grille n'est pas une population. Aucun de ses cas",
            "# types n'a trois enfants, si bien que la majoration pour enfants y",
            "# valait zéro quand les comptes en portent près de huit milliards.",
            "#",
            "# LE PRODUCTEUR PRIME SUR LE MODÈLE, et c'est le critère 1 de",
            "# data/sources.yaml : là où ces postes existent, ils REMPLACENT la",
            "# ligne calculée au lieu de la compléter.",
            "#",
            "# CE QUE CETTE SÉRIE N'EST PAS",
            "# -----------------------------",
            "# Une histoire. La DREES ne publie ce grain qu'à partir de 2020,",
            "# quand le total du risque remonte à 1959 : cinq années ne font pas",
            "# une tendance, elles font un ordre de grandeur. La page le dit.",
            "#",
            "# Et une partition. Les postes ne se recouvrent pas mais ne couvrent",
            "# pas tout : les bonifications de service, les départs anticipés pour",
            "# handicap et le compte de pénibilité n'ont de poste nulle part.",
            "#",
            "# Ne pas modifier ces valeurs à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="droits_derives",
        chemin=REFERENCE / "macro" / "droits_derives.csv",
        cles=("annee", "caisse"),
        colonne="masse_meur",
        source=source_droits_derives,
        origine="DREES, enquête annuelle auprès des caisses de retraite (EACR)",
        decimales=1,
        tolerance=0.06,
        unite=" M€",
        entete=(
            "# La réversion : ce que les caisses versent aux survivants",
            "# source_id: drees_eacr",
            "# unite: millions d'euros courants de l'année",
            "# fiabilite:",
            "#   certifiee (2004-2024) : effectifs et montant mensuel moyen du",
            "#             droit dérivé, feuille A-Cadrage du classeur diffusé par",
            "#             la DREES, recontrôlés par scripts/verifier_donnees.py.",
            "#",
            "# À QUOI CETTE SÉRIE SERT",
            "# ------------------------",
            "# À chiffrer la première dépense non contributive du système, et la",
            "# seule ligne de `legislation/avantages_non_contributifs.yaml` que le",
            "# modèle ne calculera jamais : il décrit une carrière, pas un ménage,",
            "# et n'a ni conjoint, ni date de décès, ni ressources du survivant.",
            "# Là où les autres avantages se mesurent en retirant une règle et en",
            "# refaisant la pension, celui-ci se LIT.",
            "#",
            "# COMMENT LA MASSE EST OBTENUE",
            "# -----------------------------",
            "# Par un produit : le nombre de bénéficiaires d'un droit dérivé",
            "# (champ `ddert` du classeur) par le montant mensuel moyen de ce",
            "# droit-là (colonne `m2`), sur douze mois. La colonne compte : `mont`",
            "# porterait la pension TOTALE du bénéficiaire, droit direct compris,",
            "# et doublerait la masse.",
            "#",
            "# CE QUE LA SOMME DES CAISSES N'EST PAS",
            "# --------------------------------------",
            "# Un effectif de personnes. Un polypensionné touche une réversion à",
            "# la Cnav ET à l'Agirc-Arrco, et la somme des caisses compte deux fois",
            "# la même veuve : 8,5 millions de bénéficiaires contre 4,4 au « Tous",
            "# régimes ». Les MASSES, elles, s'additionnent sans double compte,",
            "# chaque caisse versant la sienne — et leur somme recoupe la ligne",
            "# `tous_regimes` à 2 % près, ce qui est le contrôle interne de cette",
            "# série.",
            "#",
            "# Ne pas modifier ces valeurs à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="effectifs_retraites",
        chemin=REFERENCE / "regimes" / "effectifs_retraites.csv",
        cles=("annee", "caisse"),
        colonne="effectifs",
        source=source_effectifs_retraites,
        origine="DREES, enquête annuelle auprès des caisses de retraite (EACR)",
        decimales=0,
        tolerance=0.51,
        unite=" retraités",
        entete=(
            "# Retraités de droit direct, par caisse, France",
            "# source_id: drees_eacr",
            "# unite: personnes",
            "# fiabilite:",
            "#   certifiee (2004-2024) : effectifs de l'enquête annuelle auprès des",
            "#             caisses de retraite, feuille A-Cadrage du classeur diffusé",
            "#             par la DREES, recontrôlés par scripts/verifier_donnees.py.",
            "#",
            "# À QUOI CETTE SÉRIE SERT",
            "# ------------------------",
            "# À PONDÉRER les cas types de la page « Coût ». Ils ont d'abord pesé",
            "# d'un poids égal, faute de source : l'agent de conduite comptait",
            "# autant que le salarié au salaire moyen, alors qu'il y a cent fois",
            "# moins de retraités à la SNCF qu'à la Cnav. Ces effectifs disent le",
            "# rapport, et la page le porte désormais.",
            "#",
            "# LA CAISSE EST DÉSIGNÉE PAR SON CODE",
            "# ------------------------------------",
            "# La DREES rebaptise ses caisses sans changer leur code — « SSI",
            "# complémentaire » est devenue « RCI complémentaire » —, et elle en",
            "# renumérote : la Cnav porte le code 0010 jusqu'en 2019 puis 0015,",
            "# sur un champ légèrement plus large. Le code est donc conservé tel",
            "# quel, la colonne `caisse` porte le libellé de la dernière campagne,",
            "# et le raccord des deux codes d'une même caisse est une décision du",
            "# modèle, écrite dans donnees/effectifs.py.",
            "#",
            "# CE QU'UN EFFECTIF DE CAISSE N'EST PAS",
            "# --------------------------------------",
            "# Ce n'est pas un effectif de personnes : un polypensionné compte dans",
            "# chacune de ses caisses, et la somme des caisses dépasse d'un tiers le",
            "# « Tous régimes » (code 0000) qui, lui, compte les personnes. C'est la",
            "# raison pour laquelle les poids des cas types sont RELATIFS et que",
            "# docs/limites.md §5 bis dit le sens du biais qui reste.",
            "#",
            "# Ne pas modifier les années certifiées à la main : elles seraient écrasées",
            "# au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="distribution_pensions",
        chemin=REFERENCE / "macro" / "distribution_pensions.csv",
        cles=("annee", "borne_mensuelle", "sexe"),
        colonne="part_pct",
        source=source_distribution_pensions,
        origine="DREES, échantillon interrégimes de retraités (EIR)",
        decimales=2,
        tolerance=0.005,
        unite=" %",
        entete=(
            "# Distribution de la pension mensuelle brute de droit direct",
            "# source_id: drees_eir_distribution",
            "# unite: pour cent des retraités de droit direct, par tranche de 100 €",
            "# fiabilite:",
            "#   certifiee : tableau 1 du classeur « Distribution des pensions",
            "#             mensuelles » de l'EIR, diffusé par la DREES et recontrôlé",
            "#             par scripts/verifier_donnees.py.",
            "#",
            "# `annee` est le millésime de l'enquête, qui paraît tous les quatre ans :",
            "# les montants sont dans les euros de cette année-là, et le modèle les y",
            "# ramène avant de leur appliquer un barème.",
            "#",
            "# `borne_mensuelle` est la borne INFÉRIEURE de la tranche, en euros par",
            "# mois : 700 est la tranche de 700 à 800 euros. La dernière — 4500 — est",
            "# ouverte : le classeur ne découpe pas au-delà.",
            "#",
            "# POURQUOI LA PENSION BRUTE DE DROIT DIRECT, ET PAS UNE AUTRE",
            "# ------------------------------------------------------------",
            "# Le classeur porte huit tableaux ; celui-ci est le seul qui soit dans",
            "# la même grandeur que la pension du modèle. BRUTE, parce que le modèle",
            "# ne calcule aucun prélèvement social. DE DROIT DIRECT, parce que la",
            "# réversion est hors du modèle par construction — il décrit une",
            "# carrière, pas un ménage. Une réserve reste, sans remède dans cette",
            "# source : le tableau comprend la majoration pour trois enfants, que les",
            "# scénarios notionnels ne servent pas.",
            "#",
            "# À QUOI CETTE SÉRIE SERT",
            "# ------------------------",
            "# À chiffrer la garantie vieillesse du scénario 6, qui est une allocation",
            "# différentielle : son coût est celui de la queue basse de cette",
            "# distribution, et ne se lit sur aucun cas type.",
            "#",
            "# Ne pas modifier les valeurs certifiées à la main : elles seraient",
            "# écrasées au prochain scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="productivite",
        chemin=REFERENCE / "macro" / "productivite.csv",
        cles=("annee",),
        colonne="variation_reelle",
        source=source_productivite,
        origine="INSEE BDM, idbanks 011785223 et 011793334",
        decimales=5,
        tolerance=5e-4,
    ),
    Certification(
        nom="plafond",
        chemin=REFERENCE / "macro" / "plafond_securite_sociale.csv",
        cles=("annee",),
        colonne="pass_eur",
        source=source_plafond,
        origine="INSEE BDM, idbank 000822494",
        decimales=0,
        tolerance=0.5,
        unite=" €",
    ),
    Certification(
        nom="plafond_ancien",
        chemin=REFERENCE / "macro" / "plafond_securite_sociale.csv",
        cles=("annee",),
        colonne="pass_eur",
        source=source_plafond_ancien,
        origine="OpenFisca-France, plafond_securite_sociale_annuel.yaml",
        decimales=0,
        tolerance=0.5,
        unite=" €",
        niveau="haute",
    ),
    # Les deux se partagent l'avant-2002 sans se recouvrir : `plafond_ancien`
    # s'efface devant les années que celle-ci porte. Voir sa documentation —
    # c'est le journal de certification, non le fichier, qui l'exigeait.
    Certification(
        nom="minimum_garanti_reference",
        chemin=REFERENCE / "legislation" / "minimum_garanti_montants.csv",
        cles=("annee",),
        colonne="valeur",
        source=source_minimum_garanti_reference,
        origine="Service des retraites de l'État, page du minimum garanti",
        decimales=6,
        tolerance=5e-7,
        unite=" €",
    ),
    Certification(
        nom="minimum_vieillesse",
        chemin=REFERENCE / "legislation" / "minimum_vieillesse.csv",
        cles=("annee",),
        colonne="valeur",
        source=source_minimum_vieillesse,
        origine="DILA, base LEGI, code de la sécurité sociale, article D. 815-1",
        decimales=6,
        tolerance=5e-7,
        unite=" €",
    ),
    Certification(
        nom="plafond_journal_officiel",
        chemin=REFERENCE / "macro" / "plafond_securite_sociale.csv",
        cles=("annee",),
        colonne="pass_eur",
        source=source_plafond_journal_officiel,
        origine="DILA, base JORF, décrets portant fixation du plafond de la "
                "sécurité sociale",
        decimales=0,
        tolerance=0.5,
        unite=" €",
    ),
    Certification(
        nom="esperances_vie",
        chemin=REFERENCE / "mortalite" / "esperances_vie.csv",
        cles=("annee", "sexe", "mesure"),
        colonne="valeur",
        source=source_esperances,
        origine="INSEE BDM (e0, e60) et OCDE DSD_HEALTH_STAT@DF_LE (e65)",
        decimales=2,
        tolerance=0.05,
        unite=" ans",
    ),
    Certification(
        nom="valeurs_point",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point,
        origine="OpenFisca-France-Pension, paramètres des régimes en points",
        decimales=6,
        tolerance=5e-7,
        niveau="haute",
        entete=(
            "# Valeurs d'achat et de service du point, régime par régime",
            "# source_id: openfisca_points (Agirc depuis 1947, Ircantec depuis 1949)",
            "#",
            "# mesure :",
            "#   salaire_reference : prix d'achat du point, en euros courants de l'année.",
            "#                       cotisation / (taux_appel × salaire_reference) = points acquis",
            "#   valeur_service    : rente annuelle servie par un point, euros courants",
            "#   taux_appel        : écart entre ce qui est prélevé et ce qui ouvre des",
            "#                       droits. 1,25 depuis 1995 : cotiser 125 € n'acquiert",
            "#                       que 100 € de points.",
            "#",
            "# Règle annuelle : valeur en vigueur au 31 décembre de l'année. Le salaire",
            "# de référence change au 1er janvier, la valeur de service au 1er avril",
            "# autrefois et au 1er novembre aujourd'hui.",
            "#",
            "# fiabilite :",
            "#   haute   : transcription OpenFisca du texte de la circulaire",
            "#   moyenne : valeurs de l'UNIRS tenant lieu de point Arrco avant son",
            "#             unification de 1999, ou valeur saisie depuis le texte légal",
            "#",
            "# Repère de contrôle : Agirc-Arrco 2025, salaire de référence 20,1877 €,",
            "# valeur de service 1,4386 €, taux d'appel 1,27 — soit un rendement",
            "# instantané de 5,61 %, la valeur que publie le régime.",
            "#",
            "# Fichier écrit par scripts/verifier_donnees.py --appliquer : ne pas",
            "# modifier à la main.",
        ),
    ),
    Certification(
        nom="valeurs_point_ircantec",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_ircantec,
        origine="Caisse des dépôts, barèmes Ircantec (IRC_BAR_01 et IRC_BAR_02)",
        decimales=6,
        tolerance=5e-7,
    ),
    Certification(
        nom="valeurs_point_agirc_arrco",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_agirc_arrco,
        origine="Fédération Agirc-Arrco, compilation des valeurs de point "
                "(régime unifié, Agirc, Arrco et UNIRS)",
        decimales=6,
        tolerance=5e-7,
    ),
    Certification(
        nom="valeurs_point_agirc_arrco_en_cours",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_agirc_arrco_en_cours,
        origine="Fédération Agirc-Arrco, valeur en vigueur dans l'année en cours",
        decimales=6,
        tolerance=5e-7,
        niveau="haute",
    ),
    Certification(
        nom="valeurs_point_rafp",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_erafp,
        origine="ERAFP, évolution des valeurs du point depuis la création du RAFP",
        decimales=6,
        tolerance=5e-7,
    ),
    Certification(
        nom="valeurs_point_cnbf",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_cnbf,
        origine="CNBF, barèmes annuels des cotisations et prestations",
        decimales=6,
        tolerance=5e-7,
    ),
    Certification(
        nom="valeurs_point_cnavpl",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_cnavpl,
        origine="CNAVPL, recueils statistiques annuels",
        decimales=6,
        tolerance=5e-7,
    ),
    Certification(
        nom="valeurs_point_independants",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_independants,
        origine="IPP, barèmes des régimes de retraite des indépendants",
        decimales=6,
        tolerance=5e-7,
        niveau="haute",
    ),
    Certification(
        nom="valeurs_point_msa",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_msa,
        origine="DILA, base LEGI, code rural D. 732-166",
        decimales=6,
        tolerance=5e-7,
    ),
    Certification(
        nom="age_annulation_decote_openfisca",
        chemin=REFERENCE / "legislation" / "age_annulation_decote.csv",
        cles=("generation",),
        colonne="age",
        source=source_age_annulation_openfisca,
        origine="OpenFisca-France-Pension, aad.yaml du régime général",
        decimales=2,
        tolerance=0.01,
        unite=" ans",
        niveau="haute",
        complementaire=True,
    ),
    Certification(
        nom="duree_requise_fonction_publique_openfisca",
        chemin=REFERENCE / "legislation" / "duree_requise_fonction_publique.csv",
        cles=("annee_ouverture",),
        colonne="trimestres",
        source=source_duree_requise_fonction_publique_openfisca,
        origine="OpenFisca-France-Pension, trimtp.yaml de la pension civile, "
                "colonne de 2003",
        decimales=0,
        tolerance=0.5,
        unite=" trimestres",
        niveau="haute",
        complementaire=True,
    ),
    Certification(
        nom="minimum_contributif",
        chemin=REFERENCE / "legislation" / "minimum_contributif.csv",
        cles=("mesure", "annee"),
        colonne="valeur",
        source=source_minimum_contributif,
        origine="DILA, base LEGI, code de la sécurité sociale D. 351-2-1 et "
                "D. 173-21-0-0-1",
        decimales=6,
        tolerance=5e-3,
        unite=" €/an",
    ),
    Certification(
        nom="valeurs_point_insee",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_insee,
        origine="INSEE BDM, idbanks 000849395, 000822495 et 010593202",
        decimales=6,
        tolerance=5e-7,
        niveau="haute",
        # Elle ne sert que la fin de la série, là où ni OpenFisca ni la
        # fédération ne vont : depuis que celle-ci est lue directement, elle
        # peut n'avoir plus rien à ajouter.
        complementaire=True,
    ),
    Certification(
        nom="valeurs_point_unirs",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_substituees,
        origine="UNIRS tenant lieu de point Arrco avant 1999 — barème de la "
                "fédération Agirc-Arrco, substitution du dépôt",
        decimales=6,
        tolerance=5e-7,
        niveau="moyenne",
    ),
    Certification(
        nom="valeurs_point_texte",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_texte,
        origine="Valeurs saisies dans le texte : ANI du 17 novembre 2017, art. 3 ; "
                "arrêté du 12 décembre 1951, art. 8 (LEGIARTI000006381673)",
        decimales=6,
        tolerance=5e-7,
        niveau="moyenne",
    ),
    Certification(
        nom="valeurs_point_estimees",
        chemin=REFERENCE / "regimes" / "valeurs_point.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_valeurs_point_estimees,
        origine="Taux d'appel de l'Ircantec 1971 prolongé sur l'IPACTE et l'IGRANTE "
                "(décret 70-1277, art. 7, LEGIARTI000006368121)",
        decimales=6,
        tolerance=5e-7,
        niveau="estimee",
    ),
    Certification(
        nom="age_ouverture_requis",
        chemin=REFERENCE / "legislation" / "age_ouverture_requis.csv",
        cles=("generation",),
        colonne="age",
        source=source_age_ouverture,
        origine="DILA, base LEGI, code de la sécurité sociale L. 161-17-2 "
                "et D. 161-2-1-9",
        decimales=2,
        tolerance=0.005,
        unite=" ans",
    ),
    Certification(
        nom="duree_assurance_requise",
        chemin=REFERENCE / "legislation" / "duree_assurance_requise.csv",
        cles=("generation",),
        colonne="trimestres",
        source=source_duree_requise,
        origine="DILA, base LEGI, code de la sécurité sociale L. 161-17-3",
        decimales=0,
        tolerance=0.5,
        unite=" trimestres",
    ),
    Certification(
        nom="duree_assurance_requise_openfisca",
        chemin=REFERENCE / "legislation" / "duree_assurance_requise.csv",
        cles=("generation",),
        colonne="trimestres",
        source=source_duree_requise_openfisca,
        origine="OpenFisca-France-Pension, trimtp.yaml du régime général",
        decimales=0,
        tolerance=0.5,
        unite=" trimestres",
        niveau="haute",
        complementaire=True,
    ),
    Certification(
        nom="duree_assurance_requise_decrets",
        chemin=REFERENCE / "legislation" / "duree_assurance_requise.csv",
        cles=("generation",),
        colonne="trimestres",
        source=source_duree_requise_decrets,
        origine="DILA, base LEGI, décrets pris pour l'application de la loi du "
                "21 août 2003 et de celle du 9 novembre 2010",
        decimales=0,
        tolerance=0.5,
        unite=" trimestres",
    ),
    Certification(
        nom="duree_assurance_requise_1993",
        chemin=REFERENCE / "legislation" / "duree_assurance_requise.csv",
        cles=("generation",),
        colonne="trimestres",
        source=source_duree_requise_1993,
        origine="DILA, base LEGI, code de la sécurité sociale R. 351-45 II",
        decimales=0,
        tolerance=0.5,
        unite=" trimestres",
    ),
    Certification(
        nom="coefficient_minoration",
        chemin=REFERENCE / "legislation" / "coefficient_minoration.csv",
        cles=("generation",),
        colonne="coefficient",
        source=source_coefficient_minoration,
        origine="DILA, base LEGI, code de la sécurité sociale R. 351-27",
        decimales=5,
        tolerance=5e-6,
    ),
    Certification(
        nom="carriere_longue",
        chemin=REFERENCE / "legislation" / "carriere_longue.csv",
        # Deux portes de 2004 partagent date, génération et âge de début —
        # 56 ans avec huit trimestres de plus, 58 ans avec quatre : le
        # supplément fait partie de la clé.
        cles=("date_effet", "generation", "age_debut_maximum",
              "trimestres_supplementaires"),
        colonne="age_depart",
        source=source_carriere_longue,
        origine="DILA, base LEGI, code de la sécurité sociale L. 351-1-1 "
                "et D. 351-1-1 (I et II)",
        decimales=2,
        tolerance=0.005,
        unite=" ans",
        gabarit={"trimestres_debut": "5", "trimestres_supplementaires": "0"},
    ),
    Certification(
        nom="duree_proratisation",
        chemin=REFERENCE / "legislation" / "duree_proratisation.csv",
        cles=("generation",),
        colonne="trimestres",
        source=source_duree_proratisation,
        origine="DILA, base LEGI, code de la sécurité sociale R. 351-6 II",
        decimales=0,
        tolerance=0.5,
        unite=" trimestres",
    ),
    Certification(
        nom="annees_salaire_reference",
        chemin=REFERENCE / "legislation" / "annees_salaire_reference.csv",
        cles=("generation",),
        colonne="annees",
        source=source_annees_salaire_reference,
        origine="DILA, base LEGI, code de la sécurité sociale R. 351-29-1",
        decimales=0,
        tolerance=0.5,
        unite=" années",
    ),
    Certification(
        nom="validation_trimestres",
        chemin=REFERENCE / "legislation" / "validation_trimestres.csv",
        cles=("annee",),
        colonne="heures",
        source=source_heures_par_trimestre,
        origine="DILA, base LEGI, code de la sécurité sociale R. 351-9",
        decimales=0,
        tolerance=0.5,
        unite=" heures",
    ),
    Certification(
        nom="smic_horaire",
        chemin=REFERENCE / "macro" / "smic_horaire.csv",
        cles=("annee",),
        colonne="smic_horaire",
        source=source_smic,
        origine="DILA, base LEGI, décrets portant relèvement du salaire minimum "
                "de croissance",
        decimales=6,
        tolerance=5e-7,
        unite=" €",
    ),
    Certification(
        nom="decote_fonction_publique_coefficient",
        chemin=REFERENCE / "legislation" / "decote_fonction_publique.csv",
        cles=("annee",),
        colonne="coefficient",
        source=source_decote_fp_coefficient,
        origine="DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 III",
        decimales=5,
        tolerance=5e-6,
    ),
    Certification(
        nom="decote_fonction_publique_trimestres",
        chemin=REFERENCE / "legislation" / "decote_fonction_publique.csv",
        cles=("annee",),
        colonne="trimestres_avant_limite",
        source=source_decote_fp_trimestres,
        origine="DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 III",
        decimales=0,
        tolerance=0.5,
        unite=" trimestres",
    ),
    Certification(
        nom="minimum_garanti_indice",
        chemin=REFERENCE / "legislation" / "minimum_garanti.csv",
        cles=("annee",),
        colonne="indice_majore",
        source=source_minimum_garanti_indice,
        origine="DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 V",
        decimales=0,
        tolerance=0.5,
        unite="",
    ),
    Certification(
        nom="minimum_garanti_part",
        chemin=REFERENCE / "legislation" / "minimum_garanti.csv",
        cles=("annee",),
        colonne="part_15_ans",
        source=source_minimum_garanti_part,
        origine="DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 V",
        decimales=3,
        tolerance=0.0005,
        unite="",
    ),
    Certification(
        nom="minimum_garanti_points_15_30",
        chemin=REFERENCE / "legislation" / "minimum_garanti.csv",
        cles=("annee",),
        colonne="points_15_30",
        source=source_minimum_garanti_points_15_30,
        origine="DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 V",
        decimales=6,
        tolerance=5e-07,
        unite="",
    ),
    Certification(
        nom="minimum_garanti_points_30_40",
        chemin=REFERENCE / "legislation" / "minimum_garanti.csv",
        cles=("annee",),
        colonne="points_30_40",
        source=source_minimum_garanti_points_30_40,
        origine="DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 V",
        decimales=6,
        tolerance=5e-07,
        unite="",
    ),
    Certification(
        nom="minimum_garanti_seuil",
        chemin=REFERENCE / "legislation" / "minimum_garanti.csv",
        cles=("annee",),
        colonne="trimestres_seuil",
        source=source_minimum_garanti_seuil,
        origine="DILA, base LEGI, loi n° 2003-775 du 21 août 2003, article 66 V",
        decimales=0,
        tolerance=0.5,
        unite=" trimestres",
    ),
    Certification(
        nom="point_indice_fonction_publique",
        chemin=REFERENCE / "legislation" / "point_indice_fonction_publique.csv",
        cles=("annee",),
        colonne="valeur",
        source=source_point_indice,
        origine="OpenFisca-France, point_indice_en_euros.yaml",
        decimales=4,
        tolerance=5e-5,
        niveau="haute",
    ),
    Certification(
        nom="point_indice_journal_officiel",
        chemin=REFERENCE / "legislation" / "point_indice_fonction_publique.csv",
        cles=("annee",),
        colonne="valeur",
        source=source_point_indice_jo,
        origine="DILA, base LEGI, décret n° 85-1148 du 24 octobre 1985, article 3",
        decimales=4,
        tolerance=5e-5,
    ),
    Certification(
        nom="esperances_projetees",
        chemin=REFERENCE / "mortalite" / "esperances_vie.csv",
        cles=("annee", "sexe", "mesure"),
        colonne="valeur",
        source=source_esperances_projetees,
        origine="dérivée des quotients projetés de l'INSEE, projections 2026",
        decimales=2,
        tolerance=0.005,
        unite=" ans",
        niveau="projetee",
    ),
    Certification(
        nom="esperance_65_derivee",
        chemin=REFERENCE / "mortalite" / "esperances_vie.csv",
        cles=("annee", "sexe", "mesure"),
        colonne="valeur",
        source=source_esperance_65_derivee,
        origine="dérivée des quotients INED de Vallin et Meslé",
        decimales=2,
        tolerance=0.005,
        unite=" ans",
        niveau="haute",
    ),
    Certification(
        nom="quotients_mortalite_anciens",
        chemin=REFERENCE / "mortalite" / "quotients_periode.csv",
        cles=("annee", "sexe", "age"),
        colonne="qx",
        source=source_quotients_anciens,
        origine="INED, tables de Vallin et Meslé, quotients du moment par âge",
        decimales=6,
        tolerance=5e-7,
    ),
    Certification(
        nom="quotients_mortalite",
        chemin=REFERENCE / "mortalite" / "quotients_periode.csv",
        cles=("annee", "sexe", "age"),
        colonne="qx",
        source=source_quotients,
        origine="Eurostat demo_mlifetable, quotients de mortalité par âge",
        decimales=6,
        tolerance=5e-7,
        entete=(
            "# Quotients de mortalité par âge — tables du moment, France",
            "# source_id: eurostat_mlifetable",
            "# unite: probabilité de décès dans l'année, entre 0 et 1",
            "#",
            "# Ce fichier PRIME sur la calibration paramétrique : dès qu'un couple",
            "# (année, sexe, âge) y figure, le moteur l'utilise tel quel et n'appelle",
            "# pas la loi de Gompertz-Makeham. Au-delà du dernier âge publié — 84 ans",
            "# jusqu'en 2011, 94 ans ensuite — et hors des années couvertes, la loi",
            "# paramétrique reprend la main : c'est un raccord assumé, pas un oubli.",
            "#",
            "# Champ : France métropolitaine jusqu'en 1997, France entière ensuite.",
            "# Avant 1986, Eurostat ne publie pas de table française ; les tables TD/TV",
            "# de l'INSEE, seules à remonter plus haut, ne sont diffusées qu'en tableurs.",
            "#",
            "# Fichier écrit par scripts/verifier_donnees.py --appliquer : ne pas",
            "# modifier à la main.",
        ),
    ),
    # -- contribution employeur des régimes publics --------------------------
    # Quatre séries dans un seul fichier, de trois niveaux différents : le taux
    # appelé par l'État depuis 2006 vient de son producteur et se certifie ; le
    # taux implicite d'avant 2006 est une reconstitution budgétaire transcrite
    # par un tiers ; la CNRACL et la SNCF sont des transcriptions de décrets et
    # d'arrêtés. Le fichier est créé par la première d'entre elles.
    Certification(
        nom="employeur_public_etat",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_etat_appele,
        origine="Service des retraites de l'État, fiche « Historique des taux "
                "de cotisations »",
        decimales=6,
        tolerance=5e-7,
        gabarit={"nature": "appelee"},
    ),
    Certification(
        nom="employeur_public_etat_implicite",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_etat_implicite,
        origine="OpenFisca-France, taux implicite du jaune « pensions » du PLF 2011",
        decimales=6,
        tolerance=5e-7,
        niveau="haute",
        gabarit={"nature": "implicite"},
    ),
    Certification(
        nom="employeur_public_texte",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_public_texte,
        origine="Décret n° 2025-86 du 30 janvier 2025 (montée en charge CNRACL)",
        decimales=6,
        tolerance=5e-7,
        niveau="moyenne",
        gabarit={"nature": "appelee"},
        # Elle ne comble que ce qu'aucune autre source ne porte : depuis que le
        # décret est lu dans la base LEGI, la saisie n'a plus rien à ajouter.
        complementaire=True,
    ),
    Certification(
        nom="employeur_public_cnracl_journal_officiel",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_cnracl_jo,
        origine="DILA, base LEGI, décret n° 91-613 du 28 juin 1991, article 5 II, "
                "et décret n° 47-1846 du 19 septembre 1947, article 3",
        decimales=6,
        tolerance=5e-7,
        gabarit={"nature": "appelee"},
    ),
    Certification(
        nom="employeur_public_cnracl",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_cnracl,
        origine="OpenFisca-France, décrets CNRACL et barèmes de la Caisse des dépôts",
        decimales=6,
        tolerance=5e-7,
        niveau="haute",
        gabarit={"nature": "appelee"},
    ),
    Certification(
        nom="employeur_public_sncf",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_sncf,
        origine="OpenFisca-France, arrêtés annuels fixant les composantes T1 et T2",
        decimales=6,
        tolerance=5e-7,
        niveau="haute",
        gabarit={"nature": "appelee"},
    ),
    # Comme pour la CNRACL : la transcription s'efface devant les années que
    # les textes portent, pour que le journal de certification dise ce que le
    # fichier contient et non ce qu'il aurait contenu.
    Certification(
        nom="employeur_public_sncf_textes",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_sncf_textes,
        origine="DILA, arrêtés annuels du taux T1 (base JORF) et décret "
                "n° 2007-1056 du 28 juin 2007, article 2 IV (base LEGI)",
        decimales=6,
        tolerance=5e-7,
        gabarit={"nature": "appelee"},
    ),
    # -- les six régimes que le Journal officiel portait sans qu'on l'ait lu --
    # Ils étaient rangés ensemble sous la ligne « rien / tout » de limites.md,
    # et leur part patronale était celle d'un salarié du privé. Deux formes de
    # texte les portent : l'arrêté annuel, pour les deux régimes adossés au
    # régime général en 2005-2006, et la version datée d'un article, pour les
    # quatre autres. Voir scripts/fetch/dila_legi_contribution_employeur.py.
    Certification(
        nom="employeur_public_ratp",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_ratp,
        origine="DILA, arrêtés annuels pris pour l'article 2 du décret "
                "n° 2005-1637 du 26 décembre 2005",
        decimales=6,
        tolerance=5e-7,
        gabarit={"nature": "appelee"},
    ),
    Certification(
        nom="employeur_public_ieg",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_ieg,
        origine="DILA, arrêtés annuels pris pour l'article 3 du décret "
                "n° 2005-278 du 24 mars 2005",
        decimales=6,
        tolerance=5e-7,
        gabarit={"nature": "appelee"},
    ),
    Certification(
        nom="employeur_public_sncf_avant_2007",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_sncf_avant_2007,
        origine="DILA, base LEGI, décret n° 91-613 du 28 juin 1991, article 8 II",
        decimales=6,
        tolerance=5e-7,
        gabarit={"nature": "appelee"},
    ),
    Certification(
        nom="employeur_public_mines",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_mines,
        origine="DILA, base LEGI, décret n° 46-2769 du 27 novembre 1946, "
                "articles 52 puis 90",
        decimales=6,
        tolerance=5e-7,
        gabarit={"nature": "appelee"},
    ),
    Certification(
        nom="employeur_public_opera",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_opera,
        origine="DILA, base LEGI, décret n° 91-613 du 28 juin 1991, article 6 II",
        decimales=6,
        tolerance=5e-7,
        gabarit={"nature": "appelee"},
    ),
    Certification(
        nom="employeur_public_comedie_francaise",
        chemin=REFERENCE / "legislation" / "contribution_employeur_public.csv",
        cles=("annee", "regime"),
        colonne="taux",
        source=source_employeur_comedie_francaise,
        origine="DILA, base LEGI, décret n° 91-613 du 28 juin 1991, article 7 II",
        decimales=6,
        tolerance=5e-7,
        gabarit={"nature": "appelee"},
    ),
    Certification(
        nom="taux_cotisation_avant_1967",
        chemin=REFERENCE / "regimes" / "taux_cotisation_annuels.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_taux_avant_1967,
        origine="COR d'après la Cnav, taux des assurances sociales 1945-1967 ; "
                "part vieillesse conventionnelle de 8,5/21",
        decimales=6,
        tolerance=5e-7,
        niveau="estimee",
    ),
    Certification(
        nom="salaires_forfaitaires_marins",
        chemin=REFERENCE / "regimes" / "salaires_forfaitaires.csv",
        cles=("regime", "annee", "categorie"),
        colonne="montant_annuel",
        source=source_salaires_forfaitaires_marins,
        origine="DILA, base JORF, arrêtés annuels portant majoration des "
                "salaires forfaitaires des marins",
        decimales=2,
        tolerance=0.005,
        unite=" €",
        entete=(
            "# Salaires forfaitaires des marins, par catégorie et par année",
            "# source_id: jorf_salaires_forfaitaires_marins",
            "# unite: euros courants par an",
            "#",
            "# Cotisations et pensions des marins ne sont pas assises sur le salaire",
            "# réel mais sur un SALAIRE FORFAITAIRE fixé par catégorie de fonction à",
            "# bord — vingt catégories, de l'apprenti à la vingtième — dont le",
            "# montant est fixé par arrêté (décret n° 2020-649, réécrivant le décret",
            "# n° 48-1709). Chaque arrêté est lu dans l'index JORF du dépôt, et la",
            "# grille retenue pour une année est celle en vigueur au 1er juillet.",
            "#",
            "# Une carrière saisie porte un revenu, pas une fonction à bord : le",
            "# moteur range le marin, chaque année, dans la catégorie dont le forfait",
            "# est le plus proche de son revenu annualisé — convention nommée dans",
            "# la fiche `marins` —, et cotise comme il liquide sur ce forfait. Avant",
            "# 2008, la grille de 2008 est ramenée par le salaire moyen (estimee).",
            "#",
            "# Écrit par scripts/verifier_donnees.py --appliquer depuis",
            "# data/brut/jorf_salaires_forfaitaires_marins.json.",
        ),
    ),
    # La lecture du Journal officiel PASSE EN PREMIER : les deux sources qui
    # suivent ne touchent qu'aux lignes qu'elle ne couvre pas, l'une parce
    # qu'une transcription tierce ne décertifie pas, l'autre parce qu'elle
    # recopie la série du régime général telle que celle-ci vient d'être écrite.
    Certification(
        nom="taux_cotisation_journal_officiel",
        chemin=REFERENCE / "regimes" / "taux_cotisation_annuels.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_taux_cotisation_jorf,
        origine="DILA, base LEGI, code de la sécurité sociale D. 242-4 et "
                "décret n° 81-1013 ; code rural D. 741-35 et décret n° 50-444",
        decimales=6,
        tolerance=5e-7,
    ),
    Certification(
        nom="taux_cotisation_annuels",
        chemin=REFERENCE / "regimes" / "taux_cotisation_annuels.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_taux_cotisation_annuels,
        origine="OpenFisca-France, barèmes datés de la cotisation vieillesse "
                "(cnav, artisans, commerçants, indépendants)",
        decimales=6,
        tolerance=5e-7,
        niveau="haute",
        entete=(
            "# Taux de cotisation vieillesse ANNÉE PAR ANNÉE, régime par régime",
            "# source_id: dila_legi_taux_cotisation",
            "#",
            "# Les fiches de data/reference/regimes/ portent un taux par période",
            "# législative — une moyenne de dix à vingt-sept ans, écrite comme telle",
            "# dans leurs notes. Le droit a changé ce taux presque chaque année, et",
            "# c'est lui qui alimente le compte notionnel. Le chargeur des fiches",
            "# (CatalogueRegimes) découpe donc chaque période `plafonnee` de ces",
            "# régimes selon cette table, année par année ; la moyenne de la fiche",
            "# ne sert plus qu'aux années que la table ne couvre pas.",
            "#",
            "# mesure :",
            "#   taux_plafonne              : salarié + employeur, sous plafond",
            "#   part_salariale             : fraction du précédent supportée par le salarié",
            "#   taux_deplafonne            : salarié + employeur, sur la totalité du salaire",
            "#   part_salariale_deplafonnee : fraction du précédent supportée par le salarié",
            "#",
            "# Les non-salariés (cancava, organic, rsi) n'ont que les taux : ils",
            "# paient tout, et la fiche le sait (part_salariale : 1).",
            "#",
            "# Les articles qui fixent le taux sont lus par",
            "# scripts/fetch/dila_legi_taux_cotisation.py et versés `certifiee` ;",
            "# data/brut/openfisca_cotisations.json ne comble que le reste, au",
            "# niveau `haute` — OpenFisca transcrit les décrets sans en être le",
            "# producteur. Les cultes, Mayotte et Saint-Pierre-et-Miquelon",
            "# portent la série du régime général, faute d'un barème propre.",
            "#",
            "# Écrit par scripts/verifier_donnees.py --appliquer.",
        ),
    ),
    Certification(
        nom="taux_cotisation_alignes",
        chemin=REFERENCE / "regimes" / "taux_cotisation_annuels.csv",
        cles=("regime", "annee", "mesure"),
        colonne="valeur",
        source=source_taux_cotisation_alignes,
        origine="la série du régime général du dépôt, que les cultes, Mayotte "
                "et Saint-Pierre-et-Miquelon portent faute d'un barème propre",
        decimales=6,
        tolerance=5e-7,
        niveau="haute",
    ),
)


# ---------------------------------------------------------------------------
# Contrôles sans source : cohérence interne
# ---------------------------------------------------------------------------


def controle_coherence_interne() -> list[str]:
    """Vérifications qui ne dépendent d'aucune source externe."""
    messages: list[str] = []

    fichiers = {
        "ipc_annuel.csv": ("variation", -0.15, 0.70),
        "salaire_moyen.csv": ("variation_nominale", -0.15, 0.70),
        "masse_salariale.csv": ("variation_nominale", -0.15, 0.70),
        "pib_nominal.csv": ("variation_nominale", -0.15, 0.70),
        "productivite.csv": ("variation_reelle", -0.15, 0.20),
    }
    for nom, (colonne, mini, maxi) in fichiers.items():
        lignes = charger_csv(REFERENCE / "macro" / nom)
        annees = [int(l["annee"]) for l in lignes]
        trous = set(range(min(annees), max(annees) + 1)) - set(annees)
        if trous:
            messages.append(f"TROU    {nom} : années manquantes {sorted(trous)}")
        for ligne in lignes:
            valeur = float(ligne[colonne])
            if not mini <= valeur <= maxi:
                messages.append(
                    f"SUSPECT {nom} {ligne['annee']} : {valeur:.3%} hors plage plausible"
                )
        certifiees = sum(1 for l in lignes if l["fiabilite"] == "certifiee")
        messages.append(
            f"OK      {nom} : {len(lignes)} années, {min(annees)}-{max(annees)}, "
            f"{certifiees} certifiées"
        )

    plafond = charger_csv(REFERENCE / "macro" / "plafond_securite_sociale.csv")
    precedent = None
    for ligne in plafond:
        valeur = float(ligne["pass_eur"])
        if precedent is not None and valeur < precedent:
            messages.append(
                f"SUSPECT plafond {ligne['annee']} : recul de {precedent:.0f} à {valeur:.0f} €"
            )
        precedent = valeur
    messages.append(f"OK      plafond : {len(plafond)} années")

    esperances = charger_csv(REFERENCE / "mortalite" / "esperances_vie.csv")
    par_mesure: dict[str, list[int]] = {}
    table: dict[tuple[int, str], dict[str, float]] = {}
    for ligne in esperances:
        annee, sexe = int(ligne["annee"]), ligne["sexe"]
        par_mesure.setdefault(ligne["mesure"], []).append(annee)
        table.setdefault((annee, sexe), {})[ligne["mesure"]] = float(ligne["valeur"])
    for mesure, annees in sorted(par_mesure.items()):
        certifiees = sum(1 for l in esperances
                         if l["mesure"] == mesure and l["fiabilite"] == "certifiee")
        messages.append(
            f"OK      esperances_vie {mesure} : {len(annees)} lignes, "
            f"{min(annees)}-{max(annees)}, {certifiees} certifiées"
        )

    # Le rapport e65/e60 est le seul contrôle qui détecte une valeur cohérente
    # prise isolément mais incompatible avec sa voisine : c'est lui qui pilote
    # la pente de la force de mortalité calibrée.
    for (annee, sexe), valeurs in sorted(table.items()):
        if "e60" in valeurs and "e65" in valeurs:
            rapport = valeurs["e65"] / valeurs["e60"]
            if not 0.6 < rapport < 0.95:
                messages.append(
                    f"SUSPECT esperances_vie {annee}/{sexe} : rapport e65/e60 "
                    f"de {rapport:.3f}, hors plage plausible"
                )
    return messages


#: Familles de régimes dont les assurés ONT un employeur : leur
#: `taux_cotisation_retraite` est un total, et la fiche doit dire qui en paie
#: quelle part. Les autres familles — non-salariés, libéraux — n'ont pas
#: d'employeur, et le défaut `part_salariale: 1.0` y est le bon.
FAMILLES_AVEC_EMPLOYEUR = {
    "base_prive", "complementaire_prive", "additionnel_capitalise",
}

#: Régimes de familles mixtes dont les assurés sont des salariés. `agricole`
#: réunit la MSA des salariés, qui a un employeur, et celle des non-salariés,
#: qui n'en a pas.
REGIMES_SALARIES_HORS_FAMILLE = {"msa_salaries"}


def controle_ventilation_depenses() -> list[str]:
    """La ventilation par système doit rendre le total, année par année.

    C'est le seul contrôle qui vaille sur un regroupement : il ne dit pas que
    les libellés sont bien choisis, mais il dit qu'aucun organisme n'a été
    oublié ni compté deux fois — et c'est exactement ce qu'un regroupement
    écrit à la main risque.
    """
    messages: list[str] = []
    total = {
        int(l["annee"]): float(l["depenses_meur"])
        for l in charger_csv(REFERENCE / "macro" / "depenses_retraite.csv")
    }
    ventile: dict[int, float] = {}
    systemes: set[str] = set()
    for ligne in charger_csv(REFERENCE / "macro" / "depenses_retraite_regimes.csv"):
        annee = int(ligne["annee"])
        ventile[annee] = ventile.get(annee, 0.0) + float(ligne["depenses_meur"])
        systemes.add(ligne["regime"])

    if not ventile:
        return ["ABSENT  ventilation des dépenses : aucune ligne"]

    # Un dixième de million d'euros par système : l'écart d'arrondi que la
    # somme peut légitimement accumuler, et rien de plus.
    marge = 0.1 * len(systemes)
    for annee in sorted(ventile):
        attendu = total.get(annee)
        if attendu is None:
            messages.append(
                f"SUSPECT ventilation des dépenses {annee} : ventilée mais absente "
                f"du total"
            )
        elif abs(ventile[annee] - attendu) > marge:
            messages.append(
                f"ÉCART   ventilation des dépenses {annee} : somme des systèmes "
                f"{ventile[annee]:.1f} M€, total {attendu:.1f} M€"
            )
    annees = sorted(ventile)
    messages.append(
        f"OK      ventilation des dépenses : {len(systemes)} systèmes, "
        f"{annees[0]}-{annees[-1]}, somme conforme au total"
    )
    return messages


def controle_part_droits_derives() -> list[str]:
    """Deux producteurs doivent trouver la même part de réversion.

    ``part_droits_derives.csv`` vient du COR et couvre 2010-2070 ;
    ``pensions_droits.csv`` vient de la DREES, qui est le producteur de la
    dépense, et ne couvre que 2020-2024. Sur ces cinq années, les deux parts
    doivent coïncider — et elles coïncident à six centièmes de point près, deux
    fois à un centième, alors que rien ne les y oblige : deux enquêtes
    différentes, deux périmètres différents, deux nomenclatures différentes.

    C'est le seul contrôle externe dont cette série dispose, et il est
    exigeant : un demi-point d'écart signalerait qu'un régime manque au
    numérateur ou au dénominateur du calcul construit à partir du classeur.
    """
    messages: list[str] = []
    cor = {
        int(l["annee"]): float(l["part"])
        for l in charger_csv(REFERENCE / "macro" / "part_droits_derives.csv")
    }
    drees: dict[int, dict[str, float]] = {}
    for ligne in charger_csv(REFERENCE / "macro" / "pensions_droits.csv"):
        drees.setdefault(int(ligne["annee"]), {})[ligne["categorie"]] = float(
            ligne["montant_meur"]
        )
    if not cor or not drees:
        return ["ABSENT  part des droits dérivés : une des deux séries manque"]

    communes = sorted(set(cor) & set(drees))
    pire = 0.0
    for annee in communes:
        lignes = drees[annee]
        total = lignes.get("direct", 0.0) + lignes.get("derive", 0.0)
        if total <= 0.0:
            continue
        ecart = abs(lignes["derive"] / total - cor[annee])
        pire = max(pire, ecart)
        if ecart > 0.005:
            messages.append(
                f"ÉCART   part des droits dérivés {annee} : COR {cor[annee]:.4f}, "
                f"DREES {lignes['derive'] / total:.4f}"
            )
    if not communes:
        messages.append("SUSPECT part des droits dérivés : aucune année commune")
    else:
        messages.append(
            f"OK      part des droits dérivés : {len(communes)} années communes "
            f"({communes[0]}-{communes[-1]}), écart maximal "
            f"{pire * 100:.2f} point entre le COR et la DREES"
        )
    return messages


def controle_solde_retraite() -> list[str]:
    """Le solde publié par le COR doit être la différence de ses deux colonnes.

    Le dépôt n'écrit pas le solde : il l'obtient en retranchant les dépenses des
    ressources. Ce contrôle confronte ce calcul au solde que le COR publie à
    part, dans une autre figure du même rapport. Deux choses s'y vérifient d'un
    coup : que les deux séries écrites viennent bien du même compte — un
    millésime mélangé à un autre se verrait ici —, et que l'arrondi à six
    décimales de part de PIB ne mange pas le solde, qui vaut deux millièmes.

    Le second contrôle porte sur la structure des ressources, dont les parts
    doivent sommer à un : c'est le même contrôle que celui de la ventilation
    des dépenses, et il dit la même chose — rien d'oublié, rien compté deux fois.
    """
    messages: list[str] = []
    try:
        publie = _cor_comptes()["comptes"]["solde"]
    except SourceAbsente as erreur:
        return [f"IGNORÉ  solde du système de retraite : {erreur}"]

    attendu = {int(a): v for marqueur in publie.values() for a, v in marqueur.items()}
    ecrit: dict[int, dict[str, float]] = {}
    for ligne in charger_csv(REFERENCE / "macro" / "comptes_retraite.csv"):
        ecrit.setdefault(int(ligne["annee"]), {})[ligne["poste"]] = float(
            ligne["part_pib"])

    if not ecrit:
        return ["ABSENT  solde du système de retraite : aucune ligne"]

    # Deux séries arrondies au millionième : leur différence est juste au
    # deux-millionièmes près, et rien au-delà ne serait de l'arrondi.
    marge = 2e-6
    ecarts = 0
    for annee in sorted(ecrit):
        compte = ecrit[annee]
        if set(compte) != {"depenses", "ressources"}:
            messages.append(
                f"SUSPECT comptes du système de retraite {annee} : "
                f"{sorted(compte)} au lieu des deux postes attendus"
            )
            continue
        calcule = compte["ressources"] - compte["depenses"]
        reference = attendu.get(annee)
        if reference is None:
            messages.append(
                f"SUSPECT solde du système de retraite {annee} : année écrite "
                f"mais absente du solde publié"
            )
        elif abs(calcule - reference) > marge:
            ecarts += 1
            messages.append(
                f"ÉCART   solde du système de retraite {annee} : ressources "
                f"moins dépenses {calcule:+.6f}, solde publié {reference:+.6f}"
            )
    annees = sorted(ecrit)
    if not ecarts:
        messages.append(
            f"OK      solde du système de retraite : {annees[0]}-{annees[-1]}, "
            f"ressources moins dépenses conformes au solde publié"
        )

    parts: dict[int, float] = {}
    postes: set[str] = set()
    for ligne in charger_csv(REFERENCE / "macro" / "structure_ressources_retraite.csv"):
        annee = int(ligne["annee"])
        parts[annee] = parts.get(annee, 0.0) + float(ligne["part"])
        postes.add(ligne["poste"])
    if not parts:
        return [*messages, "ABSENT  structure des ressources : aucune ligne"]
    marge_parts = 1e-5 * len(postes)
    for annee in sorted(parts):
        if abs(parts[annee] - 1.0) > marge_parts:
            messages.append(
                f"ÉCART   structure des ressources {annee} : les parts somment "
                f"à {parts[annee]:.5f} et non à 1"
            )
    annees = sorted(parts)
    messages.append(
        f"OK      structure des ressources : {len(postes)} postes, "
        f"{annees[0]}-{annees[-1]}, parts sommant à un"
    )
    return messages


def controle_transferts_retraite() -> list[str]:
    """Ce que la CNAF et l'Unédic versent doit recouper ce que le COR en dit.

    Le COR ventile le poste « transferts » de la dernière année de chaque
    rapport annuel — « dont CNAF », « dont Unédic » — depuis 2023. Le dépôt lit
    la même chose chez celui qui paie, dans les rapports à la CCSS, et sur plus
    d'années. Les deux lectures doivent se recouper : EXACTEMENT pour l'Unédic,
    dont le « dont » du COR est la somme des lignes Agirc-Arrco et Ircantec ; à
    quelques pour cent pour la CNAF, dont le COR consolide les versements du
    côté des régimes qui les reçoivent et n'attrape pas tout ce qu'elle verse.
    Un écart plus grand dirait qu'une des deux lectures a changé de périmètre.
    """
    try:
        cor = _cor_comptes().get("ventilation_transferts", {})
    except SourceAbsente as erreur:
        return [f"IGNORÉ  ventilation des transferts : {erreur}"]
    if not cor:
        return ["IGNORÉ  ventilation des transferts : le COR n'en publie aucune"]

    ecrit: dict[int, dict[str, float]] = {}
    chemin = REFERENCE / "macro" / "transferts_retraite.csv"
    if chemin.exists():
        for ligne in charger_csv(chemin):
            ecrit.setdefault(int(ligne["annee"]), {})[ligne["poste"]] = float(
                ligne["montant_meur"])
    if not ecrit:
        return ["ABSENT  ventilation des transferts : aucune ligne"]

    marges = {"cnaf": 0.05, "unedic": 0.005}
    sommes = {
        "cnaf": ("cnaf_avpf", "cnaf_majorations"),
        "unedic": ("unedic_agirc_arrco", "unedic_ircantec"),
    }
    messages: list[str] = []
    ecarts = 0
    communes = sorted(int(a) for a in cor if int(a) in ecrit)
    for annee in communes:
        for organisme, postes in sommes.items():
            if any(poste not in ecrit[annee] for poste in postes):
                continue
            lu = sum(ecrit[annee][poste] for poste in postes)
            publie = cor[str(annee)][organisme]
            if abs(lu - publie) > marges[organisme] * publie:
                ecarts += 1
                messages.append(
                    f"ÉCART   ventilation des transferts {annee} {organisme} : "
                    f"CCSS {lu:.1f} M€, COR {publie:.1f} M€"
                )
    if not communes:
        messages.append(
            "SUSPECT ventilation des transferts : aucune année commune entre la "
            "série et le COR"
        )
    elif not ecarts:
        messages.append(
            f"OK      ventilation des transferts : {communes[0]}-{communes[-1]}, "
            "CNAF et Unédic conformes au « dont » du COR"
        )
    return messages


def controle_part_salariale() -> list[str]:
    """Aucune période de salariés ne doit oublier sa répartition.

    Le défaut `part_salariale: 1.0` dit « toute la cotisation est personnelle ».
    C'est vrai d'un artisan et d'une période `agent_seul`, dont le taux est déjà
    la seule retenue de l'agent. C'est faux de toute période dont le taux est un
    total employeur compris : l'oublier ferait porter au compte, sous le
    scénario 2, une part patronale qui n'a rien à y faire — sans que rien ne le
    signale.

    Ce contrôle ne dépend d'aucune source et ne certifie rien : il vérifie que
    la fiche dit ce qu'elle doit dire, et que la valeur est plausible.
    """
    import yaml

    anomalies: list[str] = []
    verifiees = 0
    for chemin in sorted((REFERENCE / "regimes").glob("*.yaml")):
        if chemin.name.startswith("_"):
            continue
        for fiche in (yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}).get(
            "regimes", []
        ):
            attendue = (fiche["famille"] in FAMILLES_AVEC_EMPLOYEUR
                        or fiche["code"] in REGIMES_SALARIES_HORS_FAMILLE)
            for periode in fiche.get("periodes", []):
                borne = f"{fiche['code']} {periode['debut']}-{periode.get('fin')}"
                part = periode.get("part_salariale")
                if periode.get("perimetre_taux") == "agent_seul":
                    if part is not None:
                        anomalies.append(
                            f"SUSPECT part salariale {borne} : période `agent_seul`, "
                            "dont le taux est déjà la seule retenue de l'agent — "
                            "`part_salariale` n'y a pas de sens"
                        )
                    continue
                if attendue and part is None:
                    anomalies.append(
                        f"MANQUE  part salariale {borne} : période de salariés sans "
                        "`part_salariale`, le compte y porterait la part patronale"
                    )
                    continue
                if part is None:
                    continue
                verifiees += 1
                if not 0.0 < float(part) <= 1.0:
                    anomalies.append(
                        f"SUSPECT part salariale {borne} : {part}, hors de ]0, 1]"
                    )
    messages = [
        f"OK      part salariale : {verifiees} périodes renseignées, "
        f"{len(anomalies)} anomalie(s)"
    ]
    messages.extend(anomalies)
    return messages


def controle_vraisemblance_inflation() -> list[str]:
    """Confronte la série d'inflation à l'IPCH d'Eurostat.

    Contrôle de vraisemblance uniquement : les deux indices divergent
    légitimement, seul un écart important trahit une erreur de saisie.
    """
    source = BRUT / "eurostat_hicp.json"
    if not source.exists():
        return [
            f"IGNORÉ  vraisemblance inflation : {source} absent "
            "(lancer scripts/fetch/eurostat_hicp.py)"
        ]

    reference = {
        int(annee): valeur
        for annee, valeur in json.loads(source.read_text(encoding="utf-8"))["serie"].items()
    }
    saisi = {
        int(ligne["annee"]): float(ligne["variation"])
        for ligne in charger_csv(REFERENCE / "macro" / "ipc_annuel.csv")
    }

    communes = sorted(set(reference) & set(saisi))
    anomalies = []
    ecart_moyen = 0.0
    for annee in communes:
        ecart = reference[annee] - saisi[annee]
        ecart_moyen += ecart
        if abs(ecart) > SEUIL_VRAISEMBLANCE:
            anomalies.append(
                f"SUSPECT inflation {annee} : référence {saisi[annee]:.2%}, "
                f"IPCH {reference[annee]:.2%} — écart de {abs(ecart):.2%}, "
                "trop élevé pour la seule différence IPC/IPCH"
            )
    if communes:
        ecart_moyen /= len(communes)

    messages = [
        f"OK      vraisemblance inflation : {len(communes)} années comparées à l'IPCH, "
        f"{len(anomalies)} au-delà du seuil de {SEUIL_VRAISEMBLANCE:.1%}",
        f"        écart moyen IPCH − IPC : {ecart_moyen:+.2%} "
        "(positif attendu, l'IPCH est structurellement au-dessus)",
    ]
    return messages + anomalies


def controle_vraisemblance_esperance_65() -> list[str]:
    """Confronte l'espérance de vie à 65 ans de l'OCDE à celle d'Eurostat.

    Les deux organisations rediffusent le chiffre INSEE : elles doivent
    coïncider. Un désaccord signalerait que l'une des deux a changé de champ —
    France métropolitaine contre France entière, par exemple — et donc que la
    série retenue n'est plus homogène avec les espérances à 60 ans, qui viennent
    directement de l'INSEE.
    """
    try:
        ocde = _serie_json("oecd_esperance_vie.json", "scripts/fetch/oecd_esperance_vie.py")
        eurostat = _serie_json("eurostat_esperance_vie.json",
                               "scripts/fetch/eurostat_mortalite.py")
    except SourceAbsente as erreur:
        return [f"IGNORÉ  vraisemblance espérance à 65 ans : {erreur}"]

    communes = [c for c in set(ocde) & set(eurostat) if c.endswith("|e65")]
    ecarts = {c: abs(ocde[c] - eurostat[c]) for c in communes}
    depassements = [
        f"SUSPECT espérance à 65 ans {cle.replace('|', '/')} : OCDE {ocde[cle]}, "
        f"Eurostat {eurostat[cle]} — les deux devraient rediffuser le même chiffre INSEE"
        for cle, ecart in sorted(ecarts.items()) if ecart > 0.05
    ]
    maximum = max(ecarts.values()) if ecarts else 0.0
    return [
        f"OK      vraisemblance espérance à 65 ans : {len(communes)} valeurs "
        f"comparées OCDE / Eurostat, écart maximal {maximum:.2f} an",
    ] + depassements


#: L'article L. 351-8 1° définit l'âge d'annulation de la décote par rapport à
#: l'âge d'ouverture : « augmenté de cinq années » jusqu'à la réforme de 2023,
#: « de trois années » depuis — et la cible est la même, 67 ans.
ANNULATION_APRES_OUVERTURE = 5.0
AGE_ANNULATION_CIBLE = 67.0


def controle_vraisemblance_age_annulation() -> list[str]:
    """Recalcule l'âge d'annulation de la décote depuis l'âge d'ouverture.

    Cette table-là n'est pas certifiable : aucun texte ne l'écrit génération par
    génération. Ce que le code écrit, c'est une RÈGLE — l'article L. 351-8 1°
    donne « l'âge prévu à l'article L. 161-17-2 augmenté de cinq années »,
    devenu trois années quand la réforme de 2023 a porté l'âge d'ouverture à
    64 ans, la cible restant 67. La table du dépôt est donc la table certifiée
    des âges d'ouverture, décalée et plafonnée.

    On ne la certifie pas pour autant — une valeur calculée n'est pas une valeur
    confrontée, et c'est la règle qui vaut pour l'espérance de vie dérivée. Mais
    on la recontrôle : si une réforme déplaçait l'âge d'ouverture sans que
    celui-ci suive, l'écart se verrait ici plutôt que dans une pension.
    """
    ouverture = _table_reference("age_ouverture_requis.csv", "generation", "age")
    annulation = _table_reference("age_annulation_decote.csv", "generation", "age")
    if not ouverture or not annulation:
        return ["IGNORÉ  vraisemblance âge d'annulation : table absente"]

    bornes = sorted(ouverture)
    ecarts = []
    for generation, age in sorted(annulation.items()):
        applicables = [b for b in bornes if b <= generation]
        if not applicables:
            continue
        attendu = min(ouverture[applicables[-1]] + ANNULATION_APRES_OUVERTURE,
                      AGE_ANNULATION_CIBLE)
        if abs(attendu - age) > 0.01:
            ecarts.append(
                f"SUSPECT âge d'annulation, génération {generation:g} : table "
                f"{age:g} ans, règle de L. 351-8 {attendu:g} ans"
            )
    return [
        f"OK      vraisemblance âge d'annulation : {len(annulation)} générations "
        f"comparées à l'âge d'ouverture certifié majoré de "
        f"{ANNULATION_APRES_OUVERTURE:g} ans, {len(ecarts)} en désaccord",
    ] + ecarts


#: L'article L. 17 du code des pensions fixe la référence du minimum garanti à
#: « la valeur du traitement brut afférent à l'indice majoré 227 au 1er janvier
#: 2004 ».
INDICE_REFERENCE_MINIMUM_GARANTI = 227
ANNEE_REFERENCE_MINIMUM_GARANTI = 2004


def controle_vraisemblance_minimum_garanti() -> list[str]:
    """Recalcule la référence du minimum garanti depuis le point d'indice.

    L'article L. 17 la définit comme le traitement de l'indice majoré 227 au
    1er janvier 2004, et le dépôt porte le montant que l'État publie —
    997,96 € par mois, soit 11 975,57 € l'an. Le point d'indice de 2004 étant
    désormais lu dans son décret, les deux chemins doivent se rejoindre :
    227 × 52,7558 = 11 975,57.

    Le montant reste `haute`, parce qu'il est transcrit d'une publication et non
    confronté à un fichier du producteur. Mais un écart entre les deux chemins
    signalerait qu'une des deux séries a bougé sans l'autre.
    """
    points = _table_reference("point_indice_fonction_publique.csv", "annee", "valeur")
    montants = _table_reference("minimum_garanti_montants.csv", "annee", "valeur")
    annee = float(ANNEE_REFERENCE_MINIMUM_GARANTI)
    if annee not in points or annee not in montants:
        return ["IGNORÉ  vraisemblance minimum garanti : ancre de 2004 absente"]

    calcule = INDICE_REFERENCE_MINIMUM_GARANTI * points[annee]
    ecart = abs(calcule - montants[annee])
    messages = [
        f"OK      vraisemblance minimum garanti : référence de 2004 publiée "
        f"{montants[annee]:.2f} €, recalculée {calcule:.2f} € "
        f"({INDICE_REFERENCE_MINIMUM_GARANTI} × {points[annee]:.4f})",
    ]
    if ecart > 0.01:
        messages.append(
            f"SUSPECT minimum garanti : les deux chemins s'écartent de "
            f"{ecart:.2f} € — le point d'indice ou le montant publié a bougé"
        )
    return messages


def controle_vraisemblance_cotisations() -> list[str]:
    """Confronte les taux du régime général saisis à ceux d'OpenFisca-France.

    Ce contrôle ne corrige rien : les fiches de régime sont des YAML structurés
    par périodes législatives, où un taux résume plusieurs années. Le rapprocher
    d'une série annuelle demande un arbitrage — quelle moyenne, sur quelles
    bornes — qui doit rester une décision explicite, prise à la main et tracée
    dans les notes de la fiche. Le rôle du contrôle est de dire quand l'écart
    devient assez grand pour appeler cette décision.
    """
    chemin = BRUT / "openfisca_cotisations.json"
    if not chemin.exists():
        return [
            f"IGNORÉ  vraisemblance cotisations : {chemin} absent "
            "(lancer scripts/fetch/openfisca_cotisations.py)"
        ]

    import yaml

    serie = json.loads(chemin.read_text(encoding="utf-8"))["serie"]
    couverture = {int(a) for a in serie}
    fiches = yaml.safe_load(
        (REFERENCE / "regimes" / "base_prive.yaml").read_text(encoding="utf-8")
    )
    regime = next(r for r in fiches["regimes"] if r["code"] == "regime_general")

    messages, anomalies = [], []
    comparees = 0
    for periode in regime["periodes"]:
        debut = max(int(periode["debut"]), min(couverture))
        fin = min(int(periode["fin"] or max(couverture)), max(couverture))
        annees = [a for a in range(debut, fin + 1) if a in couverture]
        if not annees:
            continue
        comparees += 1

        # PLAFONNÉE ET DÉPLAFONNÉE SÉPARÉMENT. La fiche porte les deux taux :
        # celui qui s'arrête au plafond et celui qui court sur la totalité du
        # salaire. Les confronter un par un — plutôt que leur somme au `total`
        # d'OpenFisca — attrape la faute que la somme masque : deux erreurs de
        # sens contraire qui se compensent, et qui ne portent pourtant pas sur
        # la même assiette.
        def _moyenne(*cles: str) -> float:
            return sum(
                sum(serie[str(a)][cle] for cle in cles) for a in annees
            ) / len(annees)

        for libelle, cles, champ in (
            ("cotisations", ("salarie_plafonnee", "employeur_plafonnee"),
             "taux_cotisation_retraite"),
            ("cotisation déplafonnée",
             ("salarie_deplafonnee", "employeur_deplafonnee"),
             "taux_cotisation_deplafonnee"),
        ):
            publie = _moyenne(*cles)
            saisi = float(periode.get(champ) or 0.0)
            if abs(publie - saisi) > 0.002:
                anomalies.append(
                    f"SUSPECT {libelle} regime_general "
                    f"{periode['debut']}-{periode['fin']} : "
                    f"fiche {saisi:.2%}, OpenFisca {publie:.2%} en moyenne sur "
                    f"{annees[0]}-{annees[-1]}"
                )

        # La RÉPARTITION salarié/employeur, sur les mêmes années. C'est elle qui
        # sépare les scénarios 2 et 3 des scénarios 4 et 5 : une erreur d'un
        # dixième s'y voit autant qu'une erreur de taux. Elle se contrôle sur
        # chaque taux, et non sur leur somme : la déplafonnée est presque
        # entièrement patronale, la plafonnée se partage à peu près par moitié.
        for libelle, part_cle, total_cles, champ in (
            ("part salariale", "salarie_plafonnee",
             ("salarie_plafonnee", "employeur_plafonnee"), "part_salariale"),
            ("part salariale déplafonnée", "salarie_deplafonnee",
             ("salarie_deplafonnee", "employeur_deplafonnee"),
             "part_salariale_deplafonnee"),
        ):
            parts = [
                serie[str(a)][part_cle] / sum(serie[str(a)][cle] for cle in total_cles)
                for a in annees
                if sum(serie[str(a)][cle] for cle in total_cles) > 0
            ]
            if not parts or periode.get(champ) is None:
                continue
            publiee = sum(parts) / len(parts)
            saisie = float(periode[champ])
            if abs(publiee - saisie) > 0.01:
                anomalies.append(
                    f"SUSPECT {libelle} regime_general "
                    f"{periode['debut']}-{periode['fin']} : fiche {saisie:.2%}, "
                    f"OpenFisca {publiee:.2%} en moyenne sur "
                    f"{annees[0]}-{annees[-1]}"
                )
    messages.append(
        f"OK      vraisemblance cotisations : {comparees} périodes du régime général "
        f"comparées à OpenFisca — taux et répartition salarié/employeur —, "
        f"{len(anomalies)} au-delà du seuil"
    )
    messages.append(
        "        avant 1967 aucune transcription n'existe : les taux y restent saisis"
    )

    # Les COMPLÉMENTAIRES pèsent, dans la pension d'un salarié du privé, plus
    # lourd que tous les autres régimes réunis après le régime général. Leurs
    # taux étaient au niveau `estimee` faute de série ; OpenFisca en porte une,
    # dated depuis 1962, et par TRANCHE — ce qui permet enfin de confronter
    # chaque période de fiche à la sienne.
    tranches = {
        "tranche_1": "tranche_1", "tranche_a": "tranche_1",
        "tranche_2_arrco": "tranche_2", "tranche_2": "tranche_2",
        # La tranche B de l'Ircantec s'arrête à 4,75 plafonds jusqu'en 2008 et
        # à huit ensuite : deux assiettes pour une seule tranche de barème,
        # qui se confronte à la même série.
        "tranche_2_ircantec": "tranche_2",
        "tranche_b": "tranche_2", "tranche_c": "tranche_3",
    }
    brut = json.loads(chemin.read_text(encoding="utf-8"))
    par_regime = brut.get("complementaires", {})
    parts_publiees = brut.get("part_salariale", {})
    variante = brut.get("variante_retenue", "?")
    # Les fiches « entreprises nouvelles » portent l'autre barème d'adhésion :
    # elles se confrontent à sa série, pas à celle du dépôt.
    variantes = brut.get("complementaires_variantes", {})
    parts_variantes = brut.get("part_salariale_variantes", {})
    fiches = yaml.safe_load(
        (REFERENCE / "regimes" / "complementaires_prive.yaml").read_text(
            encoding="utf-8")
    )
    # La tranche 2 des non-cadres emprunte le barème de l'Arrco (`points_de`) :
    # elle se confronte à la série de l'Arrco, sur sa propre assiette.
    complementaires = 0
    for regime in fiches["regimes"]:
        code_serie = regime["code"]
        if code_serie not in par_regime:
            code_serie = next(
                (p.get("points_de") for p in regime["periodes"] if p.get("points_de")),
                code_serie,
            )
        if regime["code"].endswith("_entreprises_nouvelles"):
            annuel = variantes.get(code_serie, {}).get("entreprises_nouvelles")
            parts_regime = parts_variantes.get(code_serie, {}).get(
                "entreprises_nouvelles", {})
            variante_fiche = "entreprises_nouvelles"
        else:
            annuel = par_regime.get(code_serie)
            parts_regime = parts_publiees.get(code_serie, {})
            variante_fiche = variante
        if not annuel:
            continue
        couverture = {int(a) for a in annuel}
        for periode in regime["periodes"]:
            tranche = tranches.get(periode.get("assiette"))
            if tranche is None:
                continue
            debut = max(int(periode["debut"]), min(couverture))
            fin = min(int(periode["fin"] or max(couverture)), max(couverture))
            annees = [a for a in range(debut, fin + 1)
                      if a in couverture and annuel[str(a)].get(tranche)]
            if not annees:
                continue
            complementaires += 1
            publie = sum(annuel[str(a)][tranche] for a in annees) / len(annees)
            saisi = float(periode["taux_cotisation_retraite"])
            # DEPUIS LA TRANCHE B3, LES PÉRIODES SONT EXACTES : une par valeur
            # de « contractuel × appel », si bien que le seuil descend d'un
            # demi-point à cinq centièmes — l'arrondi de la fiche, rien de
            # plus. Un écart plus grand est une période qui ne suit plus la
            # série, ou une série qu'OpenFisca a corrigée depuis.
            if abs(publie - saisi) > 0.0005:
                anomalies.append(
                    f"SUSPECT cotisations {regime['code']} {periode['debut']}-"
                    f"{periode['fin']} {periode['assiette']} : fiche {saisi:.2%}, "
                    f"OpenFisca ({variante_fiche}) {publie:.2%} en moyenne sur "
                    f"{annees[0]}-{annees[-1]}"
                )
            parts = [parts_regime[str(a)][tranche] for a in annees
                     if str(a) in parts_regime
                     and tranche in parts_regime[str(a)]]
            if not parts and variante_fiche == "entreprises_nouvelles":
                # Le barème salarié/employeur de la tranche 2 des entreprises
                # nouvelles ne porte que cette tranche, numérotée 1 chez OpenFisca.
                parts = [next(iter(parts_regime[str(a)].values())) for a in annees
                         if str(a) in parts_regime and parts_regime[str(a)]]
            if parts and periode.get("part_salariale") is not None:
                publiee = sum(parts) / len(parts)
                saisie = float(periode["part_salariale"])
                # Même seuil que pour le régime général : un centième. La
                # série salarié d'OpenFisca reste parfois en retard d'une
                # marche d'appel sur la série employeur (Agirc 1953 et 1989).
                if abs(publiee - saisie) > 0.01:
                    anomalies.append(
                        f"SUSPECT part salariale {regime['code']} "
                        f"{periode['debut']}-{periode['fin']} "
                        f"{periode['assiette']} : fiche {saisie:.2%}, "
                        f"OpenFisca {publiee:.2%} en moyenne sur "
                        f"{annees[0]}-{annees[-1]}"
                    )
    messages.append(
        f"OK      vraisemblance cotisations : {complementaires} périodes des "
        f"complémentaires du privé comparées à leurs taux effectifs par tranche "
        f"et à leur répartition salarié/employeur (barème « {variante} »)"
    )

    # LES RÉGIMES PUBLICS ET LES NON-SALARIÉS. Leurs fiches portaient des taux
    # saisis depuis des rapports, un par période ; OpenFisca-France transcrit
    # les barèmes datés — retenue pour pension de l'article L. 61, cotisation
    # de base des artisans et des commerçants, complémentaires, professions
    # libérales. Même confrontation que pour le régime général : une moyenne
    # sur les années de la période, un seuil de deux dixièmes de point.
    par_famille = {"public": brut.get("public", {}),
                   "independants": brut.get("independants", {})}
    publics_et_independants = 0
    for fichier, code, assiette, famille, series, *champ in CONFRONTATIONS_TAUX:
        champ = champ[0] if champ else "taux_cotisation_retraite"
        fiches = yaml.safe_load(
            (REFERENCE / "regimes" / fichier).read_text(encoding="utf-8"))
        regime = next((r for r in fiches["regimes"] if r["code"] == code), None)
        if regime is None:
            continue
        tables = [par_famille[famille].get(s) for s in series]
        if not all(tables):
            continue
        couverture = set.intersection(*({int(a) for a in t} for t in tables))
        for periode in regime["periodes"]:
            if periode.get("assiette") != assiette:
                continue
            debut = max(int(periode["debut"]), min(couverture))
            fin = min(int(periode["fin"] or max(couverture)), max(couverture))
            annees = [a for a in range(debut, fin + 1) if a in couverture]
            if not annees:
                continue
            publics_et_independants += 1
            publie = sum(sum(t[str(a)] for t in tables) for a in annees) / len(annees)
            saisi = float(periode.get(champ) or 0.0)
            if abs(publie - saisi) > 0.002:
                libelle = "cotisation déplafonnée" if "deplafonnee" in champ else "cotisations"
                anomalies.append(
                    f"SUSPECT {libelle} {code} {periode['debut']}-{periode['fin']} "
                    f"{assiette} : fiche {saisi:.2%}, OpenFisca {publie:.2%} en "
                    f"moyenne sur {annees[0]}-{annees[-1]}"
                )
    messages.append(
        f"OK      vraisemblance cotisations : {publics_et_independants} périodes "
        f"des régimes publics et des non-salariés comparées aux barèmes "
        f"d'OpenFisca-France"
    )
    return messages + anomalies


def controle_ancrage_taux_cotisation() -> list[str]:
    """Ce que valent les taux que le dépôt ne peut PAS certifier.

    Deux séries restent transcrites : le régime général d'avant 1982, que la
    base LEGI ne date pas, et les complémentaires du privé, dont les taux ne
    sont dans aucun texte réglementaire. Elles viennent d'OpenFisca-France, qui
    transcrit lui-même les barèmes de l'Institut des politiques publiques.

    Ce contrôle ne les certifie pas et ne le prétend pas : l'IPP est l'AMONT
    d'OpenFisca, et les confronter vérifie une copie contre son original. Ce
    qu'il ajoute tient en trois lignes.

    * l'IPP et OpenFisca doivent dire la même chose, année par année, à la règle
      du 1er janvier — un écart est une erreur de transcription, et il en avait
      déjà été trouvé ;
    * chaque marche de l'IPP nomme un texte et sa date au *Journal officiel* :
      ``ipp_taux_cotisation.py`` vérifie que ce texte y est, ce jour-là, sous ce
      numéro. La CHRONOLOGIE devient vérifiable même quand la VALEUR ne l'est
      pas, et c'est la chronologie dont dépend la règle du 1er janvier ;
    * pour l'Agirc et l'Arrco, l'IPP laisse lui-même la colonne du *Journal
      officiel* vide et cite des accords collectifs. C'est la démonstration,
      mécanique et non affirmée, que ces taux ne se certifieront pas.

    Et il compte les décrets que la série IGNORE. Il en reste un, et il est
    lourd : le décret n° 79-650 du 30 juillet 1979 a relevé les taux du régime
    général du 1er août 1979 au 31 janvier 1981, donc au 1er janvier 1980 ET au
    1er janvier 1981, sans qu'aucune source ne porte la hausse.
    """
    try:
        ipp = _lire_json("ipp_taux_cotisation.json",
                         "scripts/fetch/ipp_taux_cotisation.py")
        openfisca = _lire_json("openfisca_cotisations.json",
                               "scripts/fetch/openfisca_cotisations.py")
    except SourceAbsente as erreur:
        return [f"IGNORÉ  ancrage des taux de cotisation : {erreur}"]

    messages, anomalies = [], []

    # 1. La copie contre son original, année par année.
    compares = 0
    for annee, composantes in sorted(ipp["serie_cnav"].items()):
        chez_openfisca = openfisca["serie"].get(annee)
        if chez_openfisca is None:
            continue
        compares += 1
        for champ, valeur in composantes.items():
            autre = chez_openfisca.get(champ, 0.0)
            if abs(autre - valeur) > 5e-6:
                anomalies.append(
                    f"SUSPECT taux de cotisation {annee} {champ} : IPP "
                    f"{valeur:.4%}, OpenFisca {autre:.4%} — OpenFisca transcrit "
                    "l'IPP, un écart est une erreur de recopie")
    messages.append(
        f"OK      ancrage des taux de cotisation : {compares} années du régime "
        "général confrontées à la source AMONT d'OpenFisca (l'IPP) — c'est une "
        "copie vérifiée, non une seconde lecture")

    # 2. L'ancrage de chaque marche au Journal officiel.
    for nom, marches in sorted(ipp["baremes"].items()):
        ancrees = [m for m in marches if m.get("ancrage") == "ancrée"]
        if len(ancrees) == len(marches):
            messages.append(
                f"OK      ancrage {nom} : {len(marches)}/{len(marches)} marches "
                "retrouvées au Journal officiel, au numéro et à la date que "
                "l'IPP annonce")
            continue
        manquantes = [m for m in marches if m.get("ancrage") != "ancrée"]
        raisons = sorted({m.get("ancrage", "?") for m in manquantes})
        citee = next((m["reference"] for m in manquantes if m["reference"]), "")
        messages.append(
            f"OK      ancrage {nom} : {len(ancrees)}/{len(marches)} marches "
            f"ancrées — pour les autres, {' ; '.join(raisons)}"
            + (f" (« {citee[:60]} »)" if citee else ""))

    # 3. Ce que la corroboration de 1981 dit, et ce que la série ignore.
    corroboration = ipp.get("corroboration_1981") or {}
    verdict = corroboration.get("verdict", "non vérifiée")
    if verdict.startswith("le Journal officiel confirme"):
        messages.append(
            "OK      corroboration 1981 : la notice du décret n° 81-1013, seule "
            "du JORF ancien à porter les chiffres, donne le niveau que la série "
            "porte — 8,20 % employeur, 4,70 % salarié")
    else:
        anomalies.append(f"SUSPECT corroboration 1981 : {verdict}")

    ignores = ipp.get("decrets_ignores") or []
    if ignores:
        messages.append(
            f"        {len(ignores)} décret(s) du Journal officiel qu'aucune "
            "marche ne rejoint, sur 1967-1981 — les années qu'ils couvrent sont "
            "donc FAUSSES et non seulement incertaines :")
        messages.extend(f"        {ligne}" for ligne in ignores)
    return messages + anomalies


#: Fiche, régime, assiette -> séries d'OpenFisca à additionner pour obtenir
#: la grandeur que la fiche porte, et le champ de la fiche quand ce n'est pas
#: `taux_cotisation_retraite`. La retenue de l'agent (`agent_seul`) se lit
#: telle quelle ; le RAFP additionne ses deux parts ; les ouvriers de l'État
#: suivent l'article L. 61 par renvoi, et donc la série de l'État.
CONFRONTATIONS_TAUX = (
    ("fonction_publique.yaml", "fonction_publique_etat", "hors_primes",
     "public", ("fonction_publique_etat",)),
    ("fonction_publique.yaml", "cnracl", "hors_primes", "public", ("cnracl",)),
    ("fonction_publique.yaml", "fspoeie", "hors_primes",
     "public", ("fonction_publique_etat",)),
    ("fonction_publique.yaml", "rafp", "primes_uniquement",
     "public", ("rafp_salarie", "rafp_employeur")),
    ("non_salaries.yaml", "cancava", "plafonnee",
     "independants", ("artisans_base_plafonnee",)),
    ("non_salaries.yaml", "organic", "plafonnee",
     "independants", ("commercants_base_plafonnee",)),
    ("non_salaries.yaml", "rsi", "plafonnee",
     "independants", ("artisans_base_plafonnee",)),
    ("non_salaries.yaml", "rsi", "plafonnee",
     "independants", ("independants_base_deplafonnee",), "taux_cotisation_deplafonnee"),
    ("non_salaries.yaml", "rco_artisans", "plafonnee",
     "independants", ("rco_artisans_tranche_1",)),
    ("non_salaries.yaml", "rco_artisans", "tranche_1_4_pass",
     "independants", ("rco_artisans_tranche_2",)),
    ("non_salaries.yaml", "rci", "plafonnee", "independants", ("rci_tranche_1",)),
    ("non_salaries.yaml", "rci", "tranche_1_4_pass",
     "independants", ("rci_tranche_2",)),
    ("non_salaries.yaml", "cnavpl", "plafonnee_085_pass",
     "independants", ("cnavpl_tranche_1_085",)),
    ("non_salaries.yaml", "cnavpl", "tranche_085_5_pass",
     "independants", ("cnavpl_tranche_2_085_5",)),
    ("non_salaries.yaml", "cnavpl", "plafonnee", "independants", ("cnavpl_tranche_1",)),
    ("non_salaries.yaml", "cnavpl", "plafonnee_5_pass",
     "independants", ("cnavpl_tranche_2",)),
)


def controle_vraisemblance_minimum_contributif() -> list[str]:
    """Confronte les montants SERVIS du minimum contributif à OpenFisca-France-Pension.

    Le fichier du dépôt est une table d'ANCRES : une ligne par montant qui
    change, à l'année où il change. Les ancres du code sont certifiées depuis
    la base LEGI ; les montants réellement servis entre deux ancres sont
    transcrits de réponses ministérielles et de publications de la Cnav, au
    niveau ``haute``. OpenFisca transcrit les mêmes circulaires : on oppose à
    chaque ligne transcrite la dernière date d'effet qu'il porte DANS CETTE
    ANNÉE-LÀ — et rien quand il n'en porte aucune, sa série s'arrêtant en 2023.

    Un contrôle, pas une certification : les deux sont des transcriptions, à
    quelques centimes l'une de l'autre — douze mensualités arrondies contre un
    montant annuel —, et la ligne garde la valeur que le dépôt a transcrite.
    """
    try:
        changements = _lire_json("openfisca_minimum_contributif.json",
                                 "scripts/fetch/openfisca_minimum_contributif.py")["changements"]
    except SourceAbsente as erreur:
        return [f"IGNORÉ  vraisemblance minimum contributif : {erreur}"]
    lignes = charger_csv(REFERENCE / "legislation" / "minimum_contributif.csv")
    comparees, ecarts = 0, []
    for ligne in lignes:
        if ligne["fiabilite"] == "certifiee":
            continue
        mesure, annee = ligne["mesure"], ligne["annee"]
        dans_l_annee = sorted(
            (jour, montant) for jour_mesure, montant in changements.items()
            for m, jour in [jour_mesure.split("|")]
            if m == mesure and jour[:4] == annee
        )
        if not dans_l_annee:
            continue
        comparees += 1
        publie, saisi = dans_l_annee[-1][1], float(ligne["valeur"])
        if abs(publie - saisi) > 0.5:
            ecarts.append(
                f"SUSPECT minimum contributif {mesure} {annee} : fiche {saisi:.2f} €, "
                f"OpenFisca {publie:.2f} € au {dans_l_annee[-1][0]}"
            )
    return [
        f"OK      vraisemblance minimum contributif : {comparees} montants servis "
        f"comparés aux circulaires transcrites par OpenFisca-France-Pension, "
        f"{len(ecarts)} au-delà de cinquante centimes",
    ] + ecarts


def controle_vraisemblance_prix_anciens() -> list[str]:
    """Confronte l'inflation reconstituée d'avant 1950 à la seule série de
    l'INSEE qui remonte plus haut.

    `docs/limites.md` a longtemps écrit que le tableau « IPC depuis 1901 »
    n'existait qu'en fichier tableur, et que ce n'était « plus le format qui
    bloque, c'est l'adresse ». L'adresse est un IDBANK : `010605954`, le
    coefficient de transformation du franc et de l'euro, que la Banque de
    données macroéconomiques sert depuis 1901 par la même API que tout le
    reste.

    **Elle ne remplace pas la série saisie, et c'est mesurable.** Publiée à
    deux décimales sur une base 100 en 2015, elle vaut 0,20 en 1935 : un
    centième y pèse cinq points de taux, et les variations annuelles qu'on en
    tirerait seraient du bruit — la série donne +3,9 % pour 1930 quand le dépôt
    porte −2,5 %, et 0,0 % pour 1934 quand il porte −5,7 %. Le contrôle porte
    donc sur la DÉRIVE CUMULÉE, seule grandeur que cette précision autorise.

    L'étalonnage du contrôle est donné par la période où le dépôt est certifié :
    sur 1949-2025, la série des coefficients s'écarte déjà de 2,4 % de la série
    mensuelle certifiée. Un écart du même ordre sur 1930-1949 ne dit donc rien
    d'autre que la précision de l'instrument.
    """
    chemin = BRUT / "insee_bdm.json"
    if not chemin.exists():
        return [f"IGNORÉ  vraisemblance prix anciens : {chemin} absent "
                "(lancer scripts/fetch/insee_bdm.py)"]

    series = json.loads(chemin.read_text(encoding="utf-8"))["series"]
    coefficients = series.get("coefficient_prix_1901", {}).get("observations")
    if not coefficients:
        return ["IGNORÉ  vraisemblance prix anciens : série 010605954 absente "
                "du téléchargement"]
    indice = {int(a): float(v) for a, v in coefficients.items() if len(a) == 4}

    saisi = {int(l["annee"]): float(l["variation"])
             for l in charger_csv(REFERENCE / "macro" / "ipc_annuel.csv")}

    messages = []
    for debut, fin, etiquette in ((1930, 1949, "reconstituée"),
                                  (1949, 2025, "certifiée")):
        if debut not in indice or fin not in indice:
            continue
        publiee = indice[fin] / indice[debut]
        cumulee = 1.0
        for annee in range(debut + 1, fin + 1):
            cumulee *= 1.0 + saisi.get(annee, 0.0)
        ecart = cumulee / publiee - 1.0
        messages.append(
            f"OK      vraisemblance prix anciens {debut}-{fin} ({etiquette}) : "
            f"dépôt ×{cumulee:.2f}, INSEE 010605954 ×{publiee:.2f}, "
            f"écart cumulé {ecart:+.1%}"
        )
        if abs(ecart) > SEUIL_DERIVE_PRIX_ANCIENS:
            messages.append(
                f"SUSPECT prix anciens {debut}-{fin} : {ecart:+.1%} de dérive "
                f"cumulée, au-delà du seuil de "
                f"{SEUIL_DERIVE_PRIX_ANCIENS:.0%}"
            )
    return messages


def controle_vraisemblance_rendements() -> list[str]:
    """Confronte les rendements saisis aux valeurs du point désormais connues.

    ``rendements_points.csv`` n'est plus la source principale : le moteur
    accumule des points là où il a le prix d'achat. Le fichier reste utilisé
    pour les régimes que la série ne couvre pas, et ce contrôle mesure de
    combien ses estimations s'écartaient de la réalité — le rendement
    instantané n'étant rien d'autre que
    ``valeur_service / (taux_appel × salaire_reference)``.
    """
    try:
        valeurs = _charge_points()
    except SourceAbsente as erreur:
        return [f"IGNORÉ  vraisemblance rendements : {erreur}"]

    serie = {**valeurs["serie"], **valeurs["complements"]}

    def au(regime: str, annee: int, mesure: str, defaut: float | None = None):
        candidates = [
            cle for cle in serie
            if cle.startswith(f"{regime}|") and cle.endswith(f"|{mesure}")
            and int(cle.split("|")[1]) <= annee
        ]
        if not candidates:
            return defaut
        return serie[max(candidates, key=lambda cle: int(cle.split("|")[1]))]

    lignes = charger_csv(REFERENCE / "regimes" / "rendements_points.csv")
    comparees, ecarts = 0, []
    for ligne in lignes:
        regime, debut, fin = ligne["regime"], int(ligne["debut"]), int(ligne["fin"])
        publies = []
        for annee in range(debut, min(fin, 2026) + 1):
            reference = au(regime, annee, "salaire_reference")
            service = au(regime, annee, "valeur_service")
            if reference and service:
                publies.append(service / (reference * au(regime, annee, "taux_appel", 1.0)))
        if not publies:
            continue
        comparees += 1
        calcule = sum(publies) / len(publies)
        saisi = float(ligne["rendement"])
        if abs(calcule - saisi) > 0.005:
            ecarts.append(
                f"SUSPECT rendement {regime} {debut}-{fin} : fiche {saisi:.2%}, "
                f"valeurs du point {calcule:.2%} en moyenne"
            )
    return [
        f"OK      vraisemblance rendements : {comparees} périodes confrontées aux "
        f"valeurs du point, {len(ecarts)} au-delà de 0,5 point",
        "        les régimes sans valeur du point publiée restent calculés au rendement",
    ] + ecarts


def controle_vraisemblance_ircantec() -> list[str]:
    """Confronte les barèmes Ircantec du producteur à ceux d'OpenFisca.

    C'est le seul régime pour lequel le dépôt dispose des deux : la Caisse des
    dépôts, qui gère l'Ircantec, et OpenFisca, qui la transcrit. Mesurer leur
    écart, c'est mesurer ce que vaut la transcription là où on ne peut pas la
    confronter — c'est-à-dire pour tous les autres régimes en points.
    """
    try:
        producteur = _serie_json("cdc_ircantec.json", "scripts/fetch/cdc_ircantec.py")
        transcription = _charge_points()["serie"]
    except SourceAbsente as erreur:
        return [f"IGNORÉ  vraisemblance Ircantec : {erreur}"]

    communes = sorted(set(producteur) & set(transcription))
    ecarts = [
        f"        écart {cle.replace('|', '/')} : Caisse des dépôts "
        f"{producteur[cle]}, OpenFisca {transcription[cle]}"
        for cle in communes
        if abs(producteur[cle] - transcription[cle]) > 1e-4
    ]
    return [
        f"OK      vraisemblance Ircantec : {len(communes)} valeurs comparées "
        f"producteur / transcription, {len(ecarts)} en désaccord",
    ] + ecarts[:6]


def controle_vraisemblance_point_insee() -> list[str]:
    """Confronte les valeurs du point d'OpenFisca à celles que l'INSEE publie.

    L'Ircantec mise à part, aucun producteur ne diffuse ses barèmes en série :
    la transcription d'OpenFisca était donc invérifiable pour les régimes qui
    pèsent le plus lourd, l'Agirc et l'Arrco. L'INSEE en diffuse la valeur de
    service depuis 2001, mensuelle, sous trois idbanks. Ce n'est pas le
    producteur, mais c'est une seconde transcription publique et indépendante :
    leur accord dit ce que vaut la première là où on ne peut pas remonter à la
    caisse.

    La tolérance est plus large que partout ailleurs — l'INSEE arrondit à quatre
    décimales, quand OpenFisca garde la conversion exacte depuis les francs.
    """
    try:
        insee = _point_insee()
        transcription = _cles_points("serie", substituees=False)
    except SourceAbsente as erreur:
        return [f"IGNORÉ  vraisemblance point Agirc-Arrco : {erreur}"]

    comparees, ecarts, ajoutees = 0, [], 0
    for regime, valeurs in sorted(insee.items()):
        for annee, valeur in sorted(valeurs.items()):
            cle = (regime, str(annee), "valeur_service")
            if cle not in transcription:
                ajoutees += 1
                continue
            comparees += 1
            if abs(transcription[cle] - valeur) > 1e-4:
                ecarts.append(
                    f"        écart {regime}/{annee} : INSEE {valeur}, "
                    f"OpenFisca {transcription[cle]}"
                )

    messages = [
        f"OK      vraisemblance point Agirc-Arrco : {comparees} années comparées "
        f"INSEE / OpenFisca, {len(ecarts)} en désaccord",
    ]
    if ajoutees:
        messages.append(
            f"        {ajoutees} année(s) que seul l'INSEE couvre, versées au "
            f"niveau haute : la transcription s'arrête avant lui"
        )
    return messages + ecarts[:6]


def controle_vraisemblance_plafond() -> list[str]:
    """Confronte le plafond d'OpenFisca à celui publié par l'INSEE, sur 2002-2026.

    C'est ce recoupement qui autorise à se servir d'OpenFisca pour les années
    anciennes : là où les deux sources se recouvrent, elles doivent tomber
    d'accord au centime près, faute de quoi la transcription est suspecte.
    """
    try:
        openfisca = _serie_json("openfisca_plafond.json",
                                "scripts/fetch/openfisca_plafond.py")
        insee = {cle[0]: valeur for cle, valeur in source_plafond().items()}
    except SourceAbsente as erreur:
        return [f"IGNORÉ  vraisemblance plafond : {erreur}"]

    communes = sorted(set(openfisca) & set(insee))
    anomalies = [
        f"SUSPECT plafond {annee} : OpenFisca {openfisca[annee]:.0f} €, "
        f"INSEE {insee[annee]:.0f} € — transcription à revoir"
        for annee in communes if abs(openfisca[annee] - insee[annee]) > 1.0
    ]
    return [
        f"OK      vraisemblance plafond : {len(communes)} années comparées "
        f"OpenFisca / INSEE, {len(anomalies)} en désaccord",
    ] + anomalies


# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    analyseur.add_argument(
        "--appliquer", action="store_true",
        help="aligne les séries de référence sur les sources et les certifie",
    )
    arguments = analyseur.parse_args(argv)

    messages: list[str] = []
    journal: dict[str, dict] = {}
    retires: set[str] = set()
    for certification in CERTIFICATIONS:
        lignes, trace = certification.confronter(arguments.appliquer)
        messages.extend(lignes)
        if trace is None:
            retires.add(certification.nom)
        elif trace:
            journal[certification.nom] = trace

    messages.append("")
    messages.extend(controle_coherence_interne())
    messages.extend(controle_ventilation_depenses())
    messages.extend(controle_part_droits_derives())
    messages.extend(controle_solde_retraite())
    messages.extend(controle_transferts_retraite())
    messages.extend(controle_part_salariale())
    messages.append("")
    messages.extend(controle_vraisemblance_inflation())
    messages.extend(controle_vraisemblance_prix_anciens())
    messages.extend(controle_vraisemblance_esperance_65())
    messages.extend(controle_vraisemblance_age_annulation())
    messages.extend(controle_vraisemblance_minimum_garanti())
    messages.extend(controle_vraisemblance_plafond())
    messages.extend(controle_vraisemblance_cotisations())
    messages.extend(controle_ancrage_taux_cotisation())
    messages.extend(controle_vraisemblance_minimum_contributif())
    messages.extend(controle_vraisemblance_rendements())
    messages.extend(controle_vraisemblance_ircantec())
    messages.extend(controle_vraisemblance_point_insee())

    for message in messages:
        print(message)

    if arguments.appliquer and (journal or retires):
        # Le journal se COMPLÈTE, il ne se remplace pas. Les récupérateurs sont
        # indépendants et lents : on lance rarement les onze d'un coup, et
        # réécrire le fichier à partir des seules sources présentes ce jour-là
        # effacerait la trace de toutes les autres — c'est-à-dire la seule
        # pièce qui, sur un dépôt fraîchement cloné, dise d'où viennent les
        # valeurs certifiées.
        JOURNAL.parent.mkdir(parents=True, exist_ok=True)
        consigne = {}
        if JOURNAL.exists():
            consigne = json.loads(JOURNAL.read_text(encoding="utf-8")).get("series", {})
        consigne.update(journal)
        for nom in retires:
            consigne.pop(nom, None)
        JOURNAL.write_text(
            json.dumps({"dernier_passage_le": date.today().isoformat(),
                        "series": consigne},
                       ensure_ascii=False, indent=1, sort_keys=True),
            encoding="utf-8",
        )
        print(f"\nCertification consignée dans {JOURNAL.relative_to(RACINE)}")
    elif not arguments.appliquer:
        print(
            "\nAucune valeur n'a été écrite : relancer avec --appliquer pour "
            "aligner les séries sur les sources et les faire passer au niveau "
            "certifiee. Ce qui reste hors de portée d'une source automatisable "
            "est énuméré dans docs/limites.md §1."
        )

    anomalies = [m for m in messages
                 if m.startswith(("ÉCART", "TROU", "SUSPECT", "MANQUE"))]
    if anomalies:
        print(f"\n{len(anomalies)} point(s) à examiner", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
