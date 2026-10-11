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

LE MINIMUM CONTRIBUTIF DES NOUVEAUX RETRAITÉS
---------------------------------------------
Le second classeur porte la feuille ``E-Minima`` : année après année, combien de
nouveaux retraités du régime général et de la MSA salariés ont eu leur pension
portée au minimum contributif. Rapportés au flux des nouveaux retraités de droit
direct de la même caisse (champ ``nl_ddir`` du cadrage, vivants au 31 décembre),
ils donnent la part que l'Études et résultats n° 1297 trace (graphique 1) et que
le dépôt confronte à ses grilles de carrières (action 137). Trois choses à
savoir :

* la Cnav transmet ses chiffres avec un an de retard, et ceux d'une année
  grossissent d'une campagne à l'autre, à mesure que ses dossiers se traitent :
  les liquidants de 2021 en comptent 98 512 à la campagne de 2021, 115 707 à
  celle de 2022. C'est encore le millésime le plus RÉCENT qui est retenu ;
* le type a changé de nom : ``mico_servi`` jusqu'à la campagne de 2022,
  ``mico_traité_servi`` depuis, la Cnav ne distinguant plus les dossiers traités
  des autres depuis 2020 ; dans une même campagne, ``mico_servi``, qui compte
  les deux, l'emporte ;
* la dernière année n'est qu'une ESTIMATION de la DREES
  (``mico_estimation_drees``), que la campagne suivante remplacera.

Le fichier produit, ``data/brut/drees_eacr.json``, est le document source : il
n'est pas lu par le modèle, seulement par ``scripts/verifier_donnees.py``, qui
en écrit ``data/reference/regimes/effectifs_retraites.csv``, la réversion de
``data/reference/macro/droits_derives.csv``, la part des nouveaux retraités
au minimum contributif, ``data/reference/regimes/minimum_contributif_liquidants.csv``,
et le montant moyen qu'il leur sert, ``data/reference/regimes/minimum_contributif_montant.csv``.
"""

from __future__ import annotations

import functools
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lecture_xlsx import feuilles, noms_des_feuilles  # noqa: E402

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

#: Dimensions qu'on ne ventile pas — on veut le total de la caisse. Le sexe se
#: lit à part quand on le demande (:func:`lire_cadrage`).
TOTALISEES = ("Sexe", "Resid", "Liq", "StatutSNCF")

#: Feuille du second classeur qui porte les minima de pension.
FEUILLE_MINIMA = "E-Minima"

#: Champ du cadrage qui compte les NOUVEAUX retraités de droit direct de
#: l'année, vivants au 31 décembre : le dénominateur de la part des
#: bénéficiaires du minimum contributif.
CHAMP_LIQUIDANTS = "nl_ddir"

#: Les caisses qui servent le minimum contributif dans la feuille : la Cnav,
#: sous ses deux codes (0010 jusqu'en 2019, 0015 depuis), et la MSA salariés.
CAISSES_MINIMUM = ("0010", "0015", "0021")

#: Les types de la feuille qui comptent les pensions portées au minimum
#: contributif, du plus complet au moins sûr : dans une même campagne, le
#: premier présent l'emporte.
TYPES_MINIMUM = ("mico_servi", "mico_traité_servi", "mico_estimation_drees")

#: Les sexes de la feuille, sous les noms du dépôt.
SEXES = {"Ensemble": "ensemble", "Femmes": "F", "Hommes": "H"}

_MILLESIME = re.compile(r"(\d{4})")


def _pieces_jointes() -> list[dict]:
    demande = urllib.request.Request(f"{BASE}/attachments", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=120) as reponse:
        return json.loads(reponse.read()).get("attachments", [])


def classeurs() -> list[tuple[str, bytes]]:
    """Télécharge les classeurs du jeu EACR, chacun avec son titre.

    La DREES diffuse l'EACR en deux classeurs — le cadrage dans le premier, les
    minima dans le second — et renomme les pièces jointes à chaque version. On
    les reconnaît donc à leur extension, et chaque feuille à son nom
    (:func:`classeur_portant`), non à celui de la pièce.
    """
    pieces = [
        piece["metas"] for piece in _pieces_jointes()
        if (piece.get("metas") or {}).get("mimetype", "").endswith("spreadsheetml.sheet")
    ]
    if not pieces:
        raise RuntimeError("aucun classeur joint au jeu EACR de la DREES")
    telecharges = []
    for piece in pieces:
        demande = urllib.request.Request(piece["url"], headers=ENTETES)
        with urllib.request.urlopen(demande, timeout=600) as reponse:
            telecharges.append((piece["title"], reponse.read()))
    return telecharges


def classeur_portant(telecharges: list[tuple[str, bytes]], feuille: str,
                     ) -> tuple[str, bytes]:
    """Celui des classeurs qui porte ``feuille``."""
    for titre, contenu in telecharges:
        if feuille in noms_des_feuilles(contenu):
            return titre, contenu
    raise RuntimeError(f"feuille {feuille!r} absente des classeurs EACR")


@functools.lru_cache(maxsize=4)
def _grille(contenu: bytes, feuille: str) -> dict[tuple[int, int], float | str]:
    """La feuille, lue une fois pour toutes les grandeurs qu'on y prend."""
    return feuilles(contenu, (feuille,))[feuille]


def _millesime(source: str) -> int:
    trouve = _MILLESIME.search(source)
    return int(trouve.group(1)) if trouve else 0


def _lignes(grille: dict[tuple[int, int], float | str]):
    """Les lignes de la feuille, chacune en dictionnaire de ses colonnes."""
    derniere_ligne = max(ligne for ligne, _ in grille)
    entete = {grille[(0, colonne)]: colonne for ligne, colonne in grille if ligne == 0}
    for ligne in range(1, derniere_ligne + 1):
        yield {nom: grille.get((ligne, colonne)) for nom, colonne in entete.items()}


def lire_cadrage(contenu: bytes, champ: str = CHAMP,
                 mesure: str = "effectifs", sexe: str = "Ensemble",
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
    séparées auraient divergé à la première correction de campagne. ``sexe``
    lit l'une des trois modalités de la feuille, « Ensemble » par défaut.
    """
    libelles: dict[str, str] = {}
    # (code, année) -> (millésime de la campagne, libellé de la source, effectif)
    retenues: dict[tuple[str, int], tuple[int, str, float]] = {}
    for cellule in _lignes(_grille(contenu, FEUILLE)):
        if cellule.get("Champ") != champ or cellule.get("Sexe") != sexe:
            continue
        if any(cellule.get(nom) != "Ensemble" for nom in TOTALISEES if nom != "Sexe"):
            continue
        effectif = cellule.get(mesure)
        if not isinstance(effectif, float) or effectif <= 0:
            continue
        code, annee = str(cellule["CC"]), int(cellule["Année"])
        source = str(cellule.get("Source") or "")
        rang = (_millesime(source), source, effectif)
        if rang[:2] > retenues.get((code, annee), (-1, ""))[:2]:
            retenues[(code, annee)] = rang
        libelles[code] = str(cellule["Caisse"])

    effectifs: dict[str, dict[str, float]] = {}
    for (code, annee), (_, _, effectif) in sorted(retenues.items()):
        effectifs.setdefault(code, {})[str(annee)] = effectif
    return libelles, effectifs


def lire_minima(contenu: bytes) -> dict[str, dict[str, dict[str, list]]]:
    """Les nouveaux retraités portés au minimum contributif, par caisse, sexe et
    année : ``{code: {sexe: {année: [effectif, montant moyen, source, type]}}}``.

    Une cellule par triplet : celle de la campagne la plus récente, et, dans
    elle, le premier des :data:`TYPES_MINIMUM` présent. Le montant moyen du
    complément (colonne ``m1``, en euros par mois) suit, ``None`` quand la
    feuille n'en porte pas ; à la MSA salariés, la campagne de 2023 y recopie
    l'effectif, et il ne se lit donc pas sans le contrôle que
    ``scripts/verifier_donnees.py`` lui fait passer. La feuille ventile aussi
    par nombre de trimestres, pour le seul minimum garanti : on ne lit que la
    modalité « Ensemble ».
    """
    retenues: dict[tuple[str, str, int], tuple] = {}
    for cellule in _lignes(_grille(contenu, FEUILLE_MINIMA)):
        code, type_minimum = str(cellule.get("CC")), cellule.get("Type")
        if code not in CAISSES_MINIMUM or type_minimum not in TYPES_MINIMUM:
            continue
        if cellule.get("Nb_trim") != "Ensemble" or cellule.get("Sexe") not in SEXES:
            continue
        effectif = cellule.get("effectifs")
        if not isinstance(effectif, float) or effectif <= 0:
            continue
        source = str(cellule.get("Source") or "")
        montant = cellule.get("m1")
        cle = (code, SEXES[cellule["Sexe"]], int(cellule["Année"]))
        # La campagne la plus récente, puis le type le plus complet.
        rang = (_millesime(source), -TYPES_MINIMUM.index(type_minimum))
        if cle not in retenues or rang > retenues[cle][0]:
            retenues[cle] = (rang, [effectif,
                                    montant if isinstance(montant, float) else None,
                                    source, type_minimum])
    sortie: dict[str, dict[str, dict[str, list]]] = {}
    for (code, sexe, annee), (_, cellule) in sorted(retenues.items()):
        sortie.setdefault(code, {}).setdefault(sexe, {})[str(annee)] = cellule
    return sortie


def minimum_contributif(contenu_cadrage: bytes, titre: str, contenu_minima: bytes,
                        ) -> dict:
    """Ce que le fichier source porte du minimum contributif : les bénéficiaires
    parmi les nouveaux retraités, et le flux de ces nouveaux retraités, des
    mêmes caisses et des mêmes sexes."""
    beneficiaires = lire_minima(contenu_minima)
    liquidants: dict[str, dict[str, dict[str, float]]] = {}
    for libelle, sexe in SEXES.items():
        _, flux = lire_cadrage(contenu_cadrage, CHAMP_LIQUIDANTS, "effectifs", libelle)
        for code in CAISSES_MINIMUM:
            if code in flux:
                liquidants.setdefault(code, {})[sexe] = flux[code]
    return {
        "fichier": titre,
        "feuille": FEUILLE_MINIMA,
        "types": list(TYPES_MINIMUM),
        "unite": "nouveaux retraités, puis euros par mois",
        "beneficiaires": beneficiaires,
        "liquidants": {"champ": CHAMP_LIQUIDANTS, "series": liquidants},
    }


def main() -> int:
    try:
        telecharges = classeurs()
        nom, contenu = classeur_portant(telecharges, FEUILLE)
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
    # Les minima sont dans l'autre classeur. Son absence ne retient pas le reste :
    # les effectifs pondèrent la page Coût, le minimum ne sert qu'à confronter.
    try:
        nom_minima, contenu_minima = classeur_portant(telecharges, FEUILLE_MINIMA)
    except RuntimeError as erreur:
        print(f"Minimum contributif non lu : {erreur}", file=sys.stderr)
    else:
        charge["minimum_contributif"] = minimum_contributif(
            contenu, nom_minima, contenu_minima)
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
    minimum = charge.get("minimum_contributif")
    if minimum:
        cnav = minimum["beneficiaires"].get("0015", {}).get("ensemble", {})
        flux = minimum["liquidants"]["series"].get("0015", {}).get("ensemble", {})
        for annee in sorted(set(cnav) & set(flux)):
            effectif, _, source, type_minimum = cnav[annee]
            print(f"Minimum contributif, Cnav, liquidants de {annee} : "
                  f"{100 * effectif / flux[annee]:.1f} % ({source}, {type_minimum})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
