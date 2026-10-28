#!/usr/bin/env python3
"""Les départs d'une génération : l'âge de liquidation et les conditions de départ des retraités nés en 1950 et en 1953.

    python scripts/fetch/drees_departs_generations.py

POURQUOI CETTE SOURCE
---------------------
La population de la page Coût (``scripts/grille_large.py``, action 138, étape
14) fait partir ses carrières au taux plein, et une part de ses carrières
incomplètes avec une décote : rien ne disait si elle part aux âges où partent
les retraités, ni dans leurs conditions. L'EACR les compte année par année
(``tests/temoins/drees_eacr_tables_2026.json``), parmi les liquidants d'une
année que les réformes de 2010 et de 2023 répartissent en vagues. L'EIR les
compte GÉNÉRATION par génération : le même jeu de la DREES que les
caractéristiques des retraités (``drees_caracteristiques_retraites.py``) joint,
à chaque millésime, le classeur d'une génération que l'enquête voit presque
toute partie — celle de 1950 en 2016, à 66 ans, celle de 1953 en 2020, à 67.

CE QU'ON EN GARDE, de chacun des deux classeurs, par sexe :

* ``ÂgeLiq_Détails`` (tableau ``age_liquidation``) — les retraités selon leur
  âge de liquidation dans leur régime principal, d'avant 60 ans au dernier âge
  que l'enquête voit ;
* ``ÂgeLiq`` (tableau ``position``) — les mêmes, selon la place du départ :
  avant l'âge légal d'ouverture des droits, à cet âge, entre lui et l'âge
  d'annulation de la décote, à ce dernier, après lui ;
* ``CondLiquidation`` (tableau ``condition``) — les retraités selon la
  condition de leur liquidation dans le régime principal : carrière longue,
  décote, décote inapplicable, surcote, taux plein pour invalidité, pour
  inaptitude, pour un autre motif, par l'âge, par la durée ;
* ``Naissance-Résidence`` (tableau ``residence``) — les mêmes selon qu'ils
  résident en France ou à l'étranger, ses seules colonnes de la résidence, et
  non celles du lieu de naissance, qui croisent les premières : la population
  ne compte que des résidents, et y prend la décote de chaque génération
  (action 138, étape 14).

De chaque colonne : l'effectif, sa part dans la génération, la part des
carrières complètes ; et, dans les feuilles de l'âge, de la position et de la
résidence, la part de chaque condition de liquidation parmi les départs de la
colonne, une case vide se lisant zéro — nul ne surcote avant 60 ans.

Et ``QuintilesEQCC`` (``quintiles_eqcc``, action 138, étape 14) : la
génération rangée par quintile de sa pension en équivalent carrière complète,
lue comme la feuille de tous les retraités (``drees_caracteristiques_retraites``)
— par quintile et par sexe, les effectifs, la proratisation, les pensions, la
part au minimum, la durée validée hors majorations et ses tranches —, avec la
durée validée, la durée cotisée, et la part des départs en carrière longue et
avec décote. L'écart de la durée cotisée à la durée validée hors majorations
est la masse assimilée de la génération à chaque rang, que la population
compare à celle du stock des retraités de 2020. Le reste des feuilles
(pensions, CSG, régimes) n'est pas lu.

CE QUE LE LECTEUR VÉRIFIE. Les colonnes d'âge et de position comptent toute la
génération : leurs effectifs redonnent celui de l'ensemble, à l'arrondi du
millier près, et leurs parts font cent ; les conditions d'une colonne ne
passent pas cent, et n'en manquent jamais plus de quinze. Le classeur laisse en
effet un retraité sur cent sans condition connue, et, à 65 ans, une femme née
en 1953 sur neuf : les colonnes des conditions ne redonnent l'ensemble qu'à un
pour cent près.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import drees_caracteristiques_retraites as caracteristiques  # noqa: E402
from drees_caracteristiques_retraites import BASE, ENTETES  # noqa: E402
from lecture_xlsx import feuilles  # noqa: E402

SORTIE = Path("data/brut/drees_departs_generations.json")

#: Le titre du classeur d'une génération : sa génération et son millésime.
_TITRE = re.compile(r"Caractéristiques des retraités nés en (\d{4}) \(EIR (\d{4})\)")

#: Les feuilles lues, sous le nom de leur tableau.
TABLEAUX: dict[str, str] = {
    "age_liquidation": "ÂgeLiq_Détails",
    "position": "ÂgeLiq",
    "condition": "CondLiquidation",
    "residence": "Naissance-Résidence",
}

#: Les conditions de liquidation dans le régime principal, dans l'ordre des
#: colonnes de la feuille ``CondLiquidation``.
CONDITIONS: tuple[str, ...] = (
    "carriere_longue", "decote", "decote_inapplicable", "surcote", "invalidite",
    "inaptitude", "autres_motifs", "taux_plein_age", "taux_plein_duree",
)

#: Les en-têtes de la feuille des conditions, sous leurs codes ; le dernier se
#: reconnaît à son début.
_COLONNES_CONDITION: dict[str, str] = {
    "Carrière longue": "carriere_longue",
    "Décote": "decote",
    "Décote non applicable": "decote_inapplicable",
    "Surcote": "surcote",
    "Taux plein invalidité": "invalidite",
    "Taux plein inaptitude": "inaptitude",
    "Taux plein autres motifs": "autres_motifs",
    "Taux plein par âge": "taux_plein_age",
    "Taux plein par la durée": "taux_plein_duree",
}

#: Les en-têtes de la feuille des positions, à leur début.
_COLONNES_POSITION: dict[str, str] = {
    "Départ avant l'âge légal": "avant_age_legal",
    "Départ à l'âge légal": "age_legal",
    "Départ entre l'âge légal": "entre",
    "Départ à l'âge d'annulation": "age_annulation",
    "Départ après l'âge d'annulation": "apres_annulation",
}

#: Les en-têtes des colonnes de la résidence, entiers ; les autres colonnes de
#: la feuille, le lieu de naissance, seul ou croisé avec la résidence, ne se
#: lisent pas.
_COLONNES_RESIDENCE: dict[str, str] = {
    "Retraités résidents en France": "france",
    "Retraités résidents à l'étranger": "etranger",
}

#: Les indicateurs lus dans chaque feuille, au début de leur libellé.
_INDICATEURS: dict[str, str] = {
    "Effectifs (en milliers)": "effectifs",
    "Part parmi l'ensemble des retraités": "part",
    "Part d'assurés à carrière complète": "carriere_complete",
}

#: Les parts de chaque condition parmi les départs d'une colonne, au début de
#: leur libellé : dans les feuilles d'âge et de position seulement.
_INDICATEURS_CONDITION: dict[str, str] = {
    "Part de départs anticipés pour carrière longue": "condition_carriere_longue",
    "Part de départ avec décote": "condition_decote",
    "Part de départ où la décote est inapplicable": "condition_decote_inapplicable",
    "Part de départ avec surcote": "condition_surcote",
    "Part des retraités ayant liquidé pour invalidité": "condition_invalidite",
    "Part des retraités ayant liquidé pour inaptitude": "condition_inaptitude",
    "Part de départ au taux plein pour un autre motif": "condition_autres_motifs",
    "Part de départ au taux plein par l'âge": "condition_taux_plein_age",
    "Part de départ au taux plein par la durée": "condition_taux_plein_duree",
}

#: Les sexes, sous les noms du dépôt.
SEXES = {"Ensemble": "ensemble", "Femme": "F", "Homme": "H"}

#: Les indicateurs de la feuille « QuintilesEQCC » d'une génération, rangée par
#: quintile de sa pension en équivalent carrière complète (action 138, étape
#: 14) : ceux des quintiles de tous les retraités, la durée validée hors
#: majorations sous l'intitulé qui se trompe ; la durée validée et la durée
#: cotisée, dont l'écart à la première est la masse assimilée de la génération
#: selon le rang ; la part des départs en carrière longue et avec décote, que
#: la pente des natures déplace.
INDICATEURS_EQCC: dict[str, str] = {
    **caracteristiques.INDICATEURS_EQCC,
    "duree_validee": "Moyenne de la durée validée (en années)",
    "duree_cotisee": "Moyenne de la durée cotisée (en années)",
    "part_carriere_longue": "Part de départs anticipés pour carrière longue (en %)",
    "part_decote": "Part de départ avec décote (en %)",
}


def _texte(valeur) -> str:
    """Un libellé, ses blancs réduits et son apostrophe droite."""
    return " ".join(str(valeur if valeur is not None else "").replace("’", "'").split())


def code_de_colonne(entete: str, tableau: str) -> str | None:
    """Le code d'une colonne de ``tableau`` : « 62 », « 67_plus » ou
    « avant_60 » pour un âge, celui de :data:`_COLONNES_POSITION` ou de
    :data:`CONDITIONS` pour une position ou une condition, celui de
    :data:`_COLONNES_RESIDENCE` pour une résidence, « ensemble » pour la
    colonne de toute la génération ; aucun pour une colonne de la feuille de
    la résidence qui n'en est pas une, que le lecteur passe."""
    texte = _texte(entete)
    if texte == "Ensemble":
        return "ensemble"
    if tableau == "residence":
        return _COLONNES_RESIDENCE.get(texte)
    if tableau == "age_liquidation":
        if (trouve := re.fullmatch(r"Avant (\d+) ans", texte)):
            return f"avant_{trouve.group(1)}"
        if (trouve := re.fullmatch(r"(\d+) ans et plus", texte)):
            return f"{trouve.group(1)}_plus"
        if (trouve := re.fullmatch(r"(\d+) ans", texte)):
            return trouve.group(1)
    codes = _COLONNES_POSITION if tableau == "position" else (
        _COLONNES_CONDITION if tableau == "condition" else {})
    for debut, code in sorted(codes.items(), key=lambda paire: -len(paire[0])):
        if texte.startswith(debut):
            return code
    raise RuntimeError(f"tableau {tableau!r} : colonne inconnue — {texte!r}")


def lire_tableau(grille: dict[tuple[int, int], float | str], tableau: str
                 ) -> dict[str, dict[str, dict[str, float]]]:
    """Une feuille, colonne par colonne, sexe par sexe : ``{colonne: {sexe:
    {indicateur: valeur}}}``, vérifiée comme le dit l'en-tête du module.

    Les colonnes sont cherchées à partir de la quatrième, et leur en-tête
    nommé par :func:`code_de_colonne`, celles qu'il ne nomme pas passées ; les
    indicateurs par le début de leur libellé, à leur première occurrence.
    """
    derniere_colonne = max(colonne for _, colonne in grille)
    derniere_ligne = max(ligne for ligne, _ in grille)
    colonnes = {colonne: code for colonne in range(3, derniere_colonne + 1)
                if (0, colonne) in grille
                and (code := code_de_colonne(grille[(0, colonne)], tableau)) is not None}
    indicateurs = dict(_INDICATEURS)
    if tableau != "condition":
        indicateurs.update(_INDICATEURS_CONDITION)
    lu: dict[str, dict[str, dict[str, float]]] = {
        code: {sexe: {} for sexe in SEXES.values()} for code in colonnes.values()}
    for ligne in range(1, derniere_ligne + 1):
        sexe = SEXES.get(_texte(grille.get((ligne, 0))))
        libelle = _texte(grille.get((ligne, 2)))
        if sexe is None:
            continue
        for debut, indicateur in indicateurs.items():
            if not libelle.startswith(debut):
                continue
            for colonne, code in colonnes.items():
                if indicateur in lu[code][sexe]:
                    continue
                valeur = grille.get((ligne, colonne))
                if isinstance(valeur, (int, float)):
                    lu[code][sexe][indicateur] = float(valeur)
                elif indicateur.startswith("condition_") and _texte(valeur) == "":
                    lu[code][sexe][indicateur] = 0.0
    manquants = sorted(f"{code}/{sexe}/{indicateur}" for code, parsexe in lu.items()
                       for sexe, valeurs in parsexe.items() for indicateur in
                       set(indicateurs.values()) - set(valeurs))
    if manquants:
        raise RuntimeError(f"tableau {tableau!r} : illisible — {', '.join(manquants[:6])}")
    _verifier(lu, tableau)
    return lu


def _verifier(lu: dict[str, dict[str, dict[str, float]]], tableau: str) -> None:
    """Les contrôles de l'en-tête du module : les colonnes redonnent
    l'ensemble, leurs parts font cent, les conditions d'une colonne aussi ;
    les deux sexes redonnent l'ensemble."""
    partition = tableau != "condition"
    for sexe in SEXES.values():
        total = lu["ensemble"][sexe]["effectifs"]
        effectifs = sum(lu[code][sexe]["effectifs"] for code in lu if code != "ensemble")
        parts = sum(lu[code][sexe]["part"] for code in lu if code != "ensemble")
        bas = total - 3.0 if partition else 0.97 * total
        if not bas <= effectifs <= total + 3.0:
            raise RuntimeError(f"tableau {tableau!r} : les effectifs des colonnes font "
                               f"{effectifs:g} milliers ({sexe}), l'ensemble {total:g}")
        if not (99.4 if partition else 97.0) <= parts <= 100.6:
            raise RuntimeError(f"tableau {tableau!r} : les parts des colonnes font "
                               f"{parts:g} % ({sexe})")
        if not partition:
            continue
        for code, valeurs in lu.items():
            somme = sum(valeurs[sexe][f"condition_{c}"] for c in CONDITIONS)
            if not 85.0 <= somme <= 100.5:
                raise RuntimeError(f"tableau {tableau!r} : les conditions de {code}/{sexe} "
                                   f"font {somme:g} %")
    deux = lu["ensemble"]["F"]["effectifs"] + lu["ensemble"]["H"]["effectifs"]
    if abs(deux - lu["ensemble"]["ensemble"]["effectifs"]) > 3.0:
        raise RuntimeError(f"tableau {tableau!r} : les effectifs des deux sexes font "
                           f"{deux:g} milliers, l'ensemble "
                           f"{lu['ensemble']['ensemble']['effectifs']:g}")


def lire_quintiles(grille: dict[tuple[int, int], float | str]
                   ) -> dict[str, dict[str, dict[str, float]]]:
    """La feuille « QuintilesEQCC » d'une génération : quintile, indicateur,
    sexe (:data:`INDICATEURS_EQCC`), lue et vérifiée comme celle de tous les
    retraités (``quintiles_de_la_feuille``)."""
    return caracteristiques.quintiles_de_la_feuille(grille, INDICATEURS_EQCC)


def lire_generation(contenu: bytes) -> dict[str, dict]:
    """Les trois tableaux du classeur d'une génération, ``tableaux``, et ses
    quintiles en équivalent carrière complète, ``quintiles_eqcc``."""
    noms = (*TABLEAUX.values(), caracteristiques.FEUILLE_EQCC)
    grilles = feuilles(contenu, noms)
    absentes = [feuille for feuille in noms if feuille not in grilles]
    if absentes:
        raise RuntimeError(f"feuilles absentes : {', '.join(absentes)}")
    return {"tableaux": {tableau: lire_tableau(grilles[feuille], tableau)
                         for tableau, feuille in TABLEAUX.items()},
            "quintiles_eqcc": lire_quintiles(grilles[caracteristiques.FEUILLE_EQCC])}


def classeurs() -> list[tuple[int, int, str, bytes]]:
    """Le classeur de chaque génération joint au jeu : ``(génération,
    millésime, titre, contenu)``, le plus récent de chaque génération."""
    demande = urllib.request.Request(f"{BASE}/attachments", headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=300) as reponse:
        pieces = json.loads(reponse.read()).get("attachments", [])
    retenus: dict[int, tuple[int, str, str]] = {}
    for piece in pieces:
        metas = piece.get("metas") or {}
        trouve = _TITRE.search(metas.get("title", ""))
        if not trouve or not metas.get("mimetype", "").endswith("spreadsheetml.sheet"):
            continue
        generation, millesime = int(trouve.group(1)), int(trouve.group(2))
        if millesime > retenus.get(generation, (0, "", ""))[0]:
            retenus[generation] = (millesime, metas["title"], metas["url"])
    if not retenus:
        raise RuntimeError("aucun classeur d'une génération joint au jeu")
    sortie = []
    for generation, (millesime, titre, url) in sorted(retenus.items()):
        demande = urllib.request.Request(url, headers=ENTETES)
        with urllib.request.urlopen(demande, timeout=600) as reponse:
            sortie.append((generation, millesime, titre, reponse.read()))
    return sortie


def main() -> int:
    try:
        lus = classeurs()
    except (urllib.error.HTTPError, urllib.error.URLError, RuntimeError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1
    charge = {"source": BASE, "lu_le": date.today().isoformat(), "generations": {}}
    for generation, millesime, titre, contenu in lus:
        charge["generations"][str(generation)] = {
            "fichier": titre, "millesime": millesime, **lire_generation(contenu)}
        print(f"Nés en {generation} (EIR {millesime}) : {titre}")
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(lus)} générations écrites dans {SORTIE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
