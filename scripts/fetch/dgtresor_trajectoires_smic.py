#!/usr/bin/env python3
"""Récupération de la persistance au voisinage du Smic, par sexe et par âge,
dans le document de travail de la DG Trésor n° 2018/3.

    python scripts/fetch/dgtresor_trajectoires_smic.py
    python scripts/fetch/dgtresor_trajectoires_smic.py --fichier ~/Téléchargements/document.pdf

CE QU'ON VIENT CHERCHER, ET POURQUOI
-------------------------------------
Combien de salariés payés au Smic y restent, et combien de temps. La
population de la page Coût (action 136, étape 6) tire chaque carrière d'une
coupe des salaires de l'année, resserrée d'un facteur uniforme : sa seconde
version n'a plus d'homme au Smic toute sa carrière, quand le minimum
contributif en vit. La part des salariés au Smic ne suffit pas à le corriger :
la plupart des jeunes qui y sont en sortent, et ce qui compte pour une
pension est ce qui reste.

CE QU'IL LIT
------------
« Les trajectoires des individus payés au voisinage du Smic pendant la crise »
(Claire Bernard, Mathilde Caurier, Sévane Ananian et Amine Chamkhi, Documents
de travail de la DG Trésor, n° 2018/3, juin 2018) suit, dans le panel DADS de
l'Insee, les salariés du privé de 18 à 65 ans payés au voisinage du Smic en
2007 — une rémunération horaire nette entre 80 % de la plus petite valeur du
Smic net de l'année et 105 % de la plus grande — jusqu'en 2013. Trois
tableaux de même forme : le tableau 7, toute la cohorte, avec celle des
salariés payés au-dessus en 2007 ; le tableau A de l'annexe 3, par âge ; le
tableau B, par sexe. Chaque année de 2008 à 2013, chacun donne la part de la
cohorte hors du champ (sortie de l'emploi salarié privé : chômage, inactivité,
retraite, fonction publique, étranger), encore au voisinage du Smic, et
au-dessus, en tout puis par tranche : de 1,05 à 1,1 Smic, de 1,1 à 1,3, de
1,3 à 1,6, plus de 1,6.

CE QU'IL CONTRÔLE
-----------------
Le lecteur du dépôt (``lecture_pdf.py``) coupe parfois un nombre en deux —
« 4 3,6 » pour 43,6, « 2 012 » pour 2012 — : les chiffres d'une même valeur
se recollent jusqu'à sa virgule, et une ligne qui ne rend pas sept valeurs
arrête tout. Chaque ligne doit ensuite tenir ses comptes : ses trois états
font 100 à l'arrondi près, ses quatre tranches font le total « au-dessus ».
Enfin les sexes, pondérés par leur part dans la cohorte de 2007 que donne le
tableau 1 (38,1 % d'hommes), doivent redonner le tableau 7 : ils le font à
0,22 point près, et des étiquettes interverties ne passeraient pas. Les âges
ne se contrôlent pas ainsi : pondérés par la composition du tableau 1, ils
s'écartent du tableau 7 de 0,9 point, quand une cohorte plus jeune (25, 30,
31 et 13 % de 18-24, 25-34, 35-49 et 50-65 ans, pour 21, 28, 35 et 16) le
redonnerait à 0,08 près. Le tableau 1 ne décrit donc pas exactement, par
l'âge, la cohorte que suivent les autres ; seuls leurs comptes se vérifient.

LA LICENCE
----------
Les mentions légales du site de la DG Trésor autorisent la réutilisation non
commerciale, la source et la date citées, mais réservent toute reprise de
contenu et ne permettent le téléchargement d'un PDF qu'à des fins
personnelles : le document reste dans ``data/brut/``, que git ignore, et ne
se republie pas (``rediffusion: interdite`` dans ``data/sources.yaml``). Son
empreinte, ci-dessous, le vérifie.

Le fichier produit, ``data/brut/dgtresor_trajectoires_smic.json``, est le
document source : il n'est pas lu par le modèle, seulement par le
vérificateur, qui en écrit ``data/reference/macro/persistance_smic.csv``.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lecture_pdf import lignes_par_page  # noqa: E402
from source_locale import (  # noqa: E402
    RACINE,
    lire_ou_telecharger,
    option_fichier,
    telecharger,
)

PAGE = ("https://www.tresor.economie.gouv.fr/Articles/2018/06/07/documents-de-travail-"
        "n-2018-3-les-trajectoires-des-individus-payes-au-voisinage-du-smic-pendant-la-crise")
DOCUMENT = ("https://www.tresor.economie.gouv.fr/Articles/d5aa8c3b-2e65-4002-84a1-61f4c82b675d"
            "/files/35d099ae-3cd7-4a00-9110-0c00b8f29e6c")
#: L'empreinte du document lu le 11 octobre 2026 : une autre édition se lirait
#: autrement, et s'arrête ici.
SHA256 = "a5917b64ca05c4a4b97fe570e45f777706f138eecd7317cd88329dc248c50721"
COPIE = "dgtresor_trajectoires_smic_2018.pdf"
SORTIE = RACINE / "data" / "brut" / "dgtresor_trajectoires_smic.json"

#: Les colonnes des trois tableaux, dans leur ordre.
ETATS = ("hors_champ", "voisinage", "superieur",
         "de_1_05_a_1_10", "de_1_10_a_1_30", "de_1_30_a_1_60", "plus_de_1_60")
ANNEES = tuple(range(2008, 2014))
#: Les tranches d'âge du document, sous le nom que le dépôt leur donne.
AGES = {"18-24ans": "Y18T24", "25-34ans": "Y25T34", "35-49ans": "Y35T49",
        "50-65ans": "Y50T65"}
SEXES = {"Hommes": "H", "Femmes": "F"}
#: Les blocs que chaque tableau doit porter : (origine, sexe, âge).
ATTENDUS = {
    "7": [("voisinage", "ensemble", "ensemble"), ("superieur", "ensemble", "ensemble")],
    "A": [("voisinage", "ensemble", age) for age in AGES.values()],
    "B": [("voisinage", sexe, "ensemble") for sexe in SEXES.values()],
}
#: Écarts tolérés, en points : trois états arrondis au dixième font 100 à
#: 0,15 près, quatre tranches leur total à 0,25 près.
ECART_ETATS = 0.15
ECART_TRANCHES = 0.25
#: Les sexes, pondérés par la composition de la cohorte de 2007, s'écartent du
#: tableau 7 d'au plus 0,22 point dans le document : l'arrondi des parts.
#: Intervertis, ils s'en écarteraient de 2,4 points en 2008.
ECART_COMPOSITION = 0.3

_ANNEE = re.compile(r"^\s*((?:\d\s?){3}\d)\s+(.*)$")
_VALEUR = re.compile(r"\d(?:\s?\d)*,\d")


def _compacte(ligne: str) -> str:
    return re.sub(r"\s+", "", ligne)


def valeurs(texte: str) -> list[float]:
    """Les nombres décimaux d'une ligne, recollés quand le lecteur les a coupés."""
    return [float(m.group(0).replace(" ", "").replace(",", ".")) for m in _VALEUR.finditer(texte)]


def lire(pages: list[list[str]]) -> tuple[dict[str, float], dict[str, float]]:
    """Les trois tableaux, en ``{origine|sexe|âge|année|état: part}``, et la
    composition par sexe de la cohorte de 2007 que donne le tableau 1."""
    serie: dict[str, float] = {}
    composition: dict[str, float] = {}
    tableau = None
    bloc = None
    for ligne in (ligne for page in pages for ligne in page):
        compacte = _compacte(ligne)
        titre = re.match(r"Tableau([0-9A-Z]+):", compacte)
        if titre:
            tableau = titre.group(1) if titre.group(1) in (*ATTENDUS, "1") else None
            bloc = ("voisinage", "ensemble", "ensemble") if tableau in ATTENDUS else None
            continue
        if tableau is None:
            continue
        if compacte.startswith("Source:"):
            tableau = bloc = None
            continue
        if tableau == "1":
            # La première valeur de la ligne est celle de 2007.
            for libelle, code in SEXES.items():
                if compacte.startswith(libelle) and code not in composition and valeurs(ligne):
                    composition[code] = valeurs(ligne)[0]
            continue
        if compacte.lower() == "individusauvoisinagedusmicen2007":
            bloc = ("voisinage", "ensemble", "ensemble")
        elif compacte.lower() == "individusavecdessalairessupérieursen2007":
            bloc = ("superieur", "ensemble", "ensemble")
        elif compacte in AGES:
            bloc = ("voisinage", "ensemble", AGES[compacte])
        elif compacte in SEXES:
            bloc = ("voisinage", SEXES[compacte], "ensemble")
        annee = _ANNEE.match(ligne)
        if not annee or bloc is None:
            continue
        an = int(annee.group(1).replace(" ", ""))
        if an not in ANNEES:
            continue
        nombres = valeurs(annee.group(2))
        if len(nombres) != len(ETATS):
            raise ValueError(f"tableau {tableau}, {bloc} {an} : {len(nombres)} valeurs "
                             f"lues au lieu de {len(ETATS)} dans « {ligne.strip()} »")
        if bloc not in ATTENDUS[tableau]:
            raise ValueError(f"tableau {tableau} : bloc inattendu {bloc}")
        for etat, valeur in zip(ETATS, nombres):
            cle = "|".join((*bloc, str(an), etat))
            if cle in serie:
                raise ValueError(f"tableau {tableau} : {cle} lu deux fois")
            serie[cle] = valeur
    return serie, composition


def controler(serie: dict[str, float], composition: dict[str, float]) -> list[str]:
    """Ce qui ne tient pas : lignes absentes, comptes faux, sexes qui ne
    redonnent pas le tableau d'ensemble."""
    erreurs = []
    for tableau, blocs in ATTENDUS.items():
        for bloc in blocs:
            for an in ANNEES:
                ligne = {etat: serie.get("|".join((*bloc, str(an), etat))) for etat in ETATS}
                if None in ligne.values():
                    erreurs.append(f"tableau {tableau}, {bloc} {an} : ligne absente")
                    continue
                etats = ligne["hors_champ"] + ligne["voisinage"] + ligne["superieur"]
                if abs(etats - 100.0) > ECART_ETATS:
                    erreurs.append(f"{bloc} {an} : les trois états font {etats:.1f}")
                tranches = sum(ligne[e] for e in ETATS[3:])
                if abs(tranches - ligne["superieur"]) > ECART_TRANCHES:
                    erreurs.append(f"{bloc} {an} : les tranches font {tranches:.1f}, "
                                   f"le total {ligne['superieur']:.1f}")
    sexes = tuple(SEXES.values())
    if any(sexe not in composition for sexe in sexes):
        return [*erreurs, f"tableau 1 : composition par sexe illisible ({composition})"]
    poids = sum(composition[sexe] for sexe in sexes)
    if abs(poids - 100.0) > ECART_ETATS:
        return [*erreurs, f"tableau 1 : la composition par sexe fait {poids:.1f}"]
    for an in ANNEES:
        for etat in ETATS:
            ensemble = serie.get(f"voisinage|ensemble|ensemble|{an}|{etat}")
            parts = [serie.get(f"voisinage|{sexe}|ensemble|{an}|{etat}") for sexe in sexes]
            if ensemble is None or None in parts:
                continue
            pondere = sum(composition[s] * p for s, p in zip(sexes, parts)) / poids
            if abs(pondere - ensemble) > ECART_COMPOSITION:
                erreurs.append(f"par sexe, {an} {etat} : {pondere:.2f} pondéré, "
                               f"{ensemble:.1f} au tableau 7")
    return erreurs


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    option_fichier(analyseur)
    options = analyseur.parse_args(argv)
    try:
        octets = lire_ou_telecharger(DOCUMENT, telecharger, options.fichier,
                                     nom_local=COPIE, sha256=SHA256)
    except (OSError, ValueError) as erreur:
        print(f"échec de la lecture du document : {erreur}", file=sys.stderr)
        return 1
    copie = SORTIE.parent / COPIE
    copie.parent.mkdir(parents=True, exist_ok=True)
    if not copie.is_file():
        copie.write_bytes(octets)
    try:
        serie, composition = lire(lignes_par_page(octets))
    except ValueError as erreur:
        print(f"document de travail 2018/3 : {erreur} — rien n'est écrit", file=sys.stderr)
        return 1
    erreurs = controler(serie, composition)
    if erreurs:
        for erreur in erreurs:
            print(f"  ÉCART   {erreur}", file=sys.stderr)
        print("document de travail 2018/3 : les tableaux ne tiennent pas leurs comptes "
              "— rien n'est écrit", file=sys.stderr)
        return 1

    SORTIE.write_text(json.dumps({
        "page": PAGE,
        "document": DOCUMENT,
        "sha256": SHA256,
        "recupere_le": date.today().isoformat(),
        "producteur": "DG Trésor (Bernard, Caurier, Ananian et Chamkhi), sur le panel "
                      "DADS 2007-2013 de l'Insee, base Dares-Urssaf. C'est le producteur "
                      "de la donnée, non une transcription.",
        "champ": "salariés du privé de 18 à 65 ans, France métropolitaine, hors "
                 "fonction publique, intérim, apprentis et stagiaires, payés au "
                 "voisinage du Smic en 2007 (rémunération horaire nette de 80 % à "
                 "105 % du Smic net), suivis de 2008 à 2013",
        "composition_2007": composition,
        "serie": dict(sorted(serie.items())),
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for sexe in ("H", "F"):
        restes = [serie[f"voisinage|{sexe}|ensemble|{an}|voisinage"] for an in ANNEES]
        print(f"{sexe} : encore au voisinage du Smic de 2008 à 2013, "
              + ", ".join(f"{r:.1f}" for r in restes) + " %")
    print(f"{SORTIE.relative_to(RACINE)} : {len(serie)} valeurs, trois tableaux")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
