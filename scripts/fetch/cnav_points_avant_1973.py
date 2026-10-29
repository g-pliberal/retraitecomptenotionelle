#!/usr/bin/env python3
"""Valeur de service des points d'avant 1973 des artisans et des commerçants.

    python scripts/fetch/cnav_points_avant_1973.py            # data/brut/…json
    python scripts/fetch/cnav_points_avant_1973.py --lignes   # et les lignes CSV

POURQUOI IL EXISTE. Avant l'alignement du 1er janvier 1973, les régimes de
base des artisans (CANCAVA) et des commerçants (ORGANIC) étaient en points ;
ces droits « demeurent calculés, liquidés et servis dans les conditions
définies par les dispositions […] en vigueur au 31 décembre 1972 » (L. 634-3),
l'allocation valant « le produit de la valeur du point de retraite […] par la
somme des points acquis » (décret n° 66-248, art. 19 ; décret n° 64-994,
art. 26 pour les artisans). Le dépôt les servait par un rendement estimé de
9 % (`rendements_points.csv`), puis en annuités du régime aligné : il lui
manquait la valeur du point (action 138, étape 18 ; fiche
``points_avant_1973_independants``).

TROIS SOURCES, DANS L'ORDRE DE LEUR AUTORITÉ.

* **La Cnav, depuis 2020** : barème ``ti_prestation_valeur_point_retraite_
  commercant_bar`` de sa base de législation, une ligne par date d'effet et
  sa circulaire, artisans et commerçants. En 2020, la revalorisation dépend
  du montant total des pensions (circulaires Cnav 2020/5 et 2020/9) : le
  dépôt retient la ligne « inférieur ou égal à 2 000 € », celle de la plupart
  des pensions, et le dit.
* **La Cnav, de 1988 à 2019** : les deux fiches « Valeur du point de retraite
  RVB » du RSI (Info-doc, mise à jour du 26 février 2019) que le barème cite
  sous « De 1988 à 2019 ». Par semestre jusqu'en 1995, par année ensuite,
  puis au 1er avril, au 1er octobre ou au 1er janvier.
* **L'IPP, avant 1988** : ``pt_organic`` (commerçants, valeur des points
  acquis par cotisations) et ``pt_cancava`` (artisans, depuis 1974). Avant
  1960, l'IPP libelle la valeur en anciens francs sans que le saut vers les
  nouveaux francs se voie (4,10 en 1958, 4,76 en 1960) : ces années, où le
  modèle ne liquide personne, ne sont pas reprises.

Les francs sont convertis à 6,55957 F pour un euro ; la valeur de 2001 est
celle en francs. Fiabilité ``haute`` : la Cnav et l'IPP transcrivent les
décisions de la caisse nationale, puis la revalorisation de L. 161-25.

Le script écrit ``data/brut/cnav_points_avant_1973.json`` : la valeur du 31
décembre de chaque année (``serie``, comme ``valeurs_point.csv``) et chaque
valeur à sa date d'effet (``datees``, comme ``valeurs_service_datees.csv``).
Il refuse d'écrire si une variation sort de [0,95 ; 1,40] d'une date à la
suivante : un franc lu pour un euro, ou une ligne de l'autre régime.
"""

from __future__ import annotations

import csv
import html
import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cnav_api  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "data" / "brut" / "cnav_points_avant_1973.json"
BAREME = "ti_prestation_valeur_point_retraite_commercant_bar"
FICHES = {
    "cancava_avant_1973": cnav_api.SITE + "/Bareme/Pages/doc_communs/listes_baremes/"
                                          "ti_prestation_valeur_point_retraite_artisan.pdf",
    "organic_avant_1973": cnav_api.SITE + "/Bareme/Pages/doc_communs/listes_baremes/"
                                          "ti_prestation_valeur_point_retraite_commercant.pdf",
}
IPP = "https://baremes.ipp.eu/parameters/regimes-de-retraites/{}/csv"
PARAMETRES_IPP = {
    "cancava_avant_1973": ("retraites.independants.pt_cancava",
                           "valeur_point_retraite_cancava_regime_base_droits_"
                           "acquis_avant_1973.valeur_annuelle"),
    "organic_avant_1973": ("retraites.independants.pt_organic",
                           "valeur_point_retraite_organic_regime_base_droits_"
                           "acquis_avant_1973.valeur_point_acquis_par_cotisations"),
}
#: Titres du barème de la Cnav, et le régime qu'ils portent.
TITRES = {"Artisans": "cancava_avant_1973", "Commerçants": "organic_avant_1973"}
FRANC_PAR_EURO = 6.55957
#: Première année des fiches du RSI ; l'IPP ne sert qu'avant elle.
DEBUT_FICHES = 1988
#: Première année de l'IPP reprise : voir l'en-tête.
DEBUT_IPP = 1960


def _ouvrir(url: str) -> bytes:
    return cnav_api.telecharger(url, delai=120)


def _texte(fragment: str) -> str:
    brut = html.unescape(re.sub(r"<[^>]+>", " ", fragment))
    return re.sub(r"[\s​﻿]+", " ", brut).strip()


def _nombre(texte: str) -> float:
    return float(re.search(r"\d+,\d+|\d+", texte).group(0).replace(",", "."))


def lire_bareme(contenu: str) -> dict[str, dict[str, float]]:
    """Le barème de la Cnav : {régime : {date d'effet : valeur en euros}}.

    Les titres « Artisans » et « Commerçants » ouvrent chacun un tableau
    « A compter de 2021 » (date, valeur annuelle) et un tableau « 2020 » par
    tranche de pension, dont seule la première ligne est retenue."""
    lues: dict[str, dict[str, float]] = {}
    morceaux = re.split(r"<h2[^>]*>(.*?)</h2>", contenu, flags=re.S)
    for titre, corps in zip(morceaux[1::2], morceaux[2::2]):
        regime = TITRES.get(_texte(titre))
        if regime is None:
            continue
        valeurs = lues.setdefault(regime, {})
        sous = re.split(r"<h3[^>]*>(.*?)</h3>", corps, flags=re.S)
        for sous_titre, tableau in zip(sous[1::2], sous[2::2]):
            for ligne in re.findall(r"<tr[^>]*>(.*?)</tr>", tableau, flags=re.S):
                cellules = [_texte(c) for c in
                            re.findall(r"<td[^>]*>(.*?)</td>", ligne, flags=re.S)]
                if len(cellules) < 2:
                    continue
                effet = re.fullmatch(r"(\d{2})/(\d{2})/(\d{4})", cellules[0])
                if effet:
                    jour, mois, annee = effet.groups()
                    valeurs[f"{annee}-{mois}-{jour}"] = _nombre(cellules[1])
                elif (_texte(sous_titre) == "2020"
                      and cellules[0].startswith("Inférieur ou égal à 2 000")):
                    valeurs["2020-01-01"] = _nombre(cellules[1])
    return lues


#: Une étiquette de date des fiches du RSI, et la date d'effet qu'elle dit.
_SEMESTRE = re.compile(r"(1er|2ème)\s+sem\s+(\d{2})")
_DATE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")
_ANNEE = re.compile(r"^\s*(\d{4})\b")
_VALEUR = re.compile(r"(\d+,\d+)\s*(€|F)")


def lire_fiche(texte: str) -> dict[str, float]:
    """Une fiche « Valeur du point de retraite RVB », mise en page par
    ``pdftotext -layout`` : {date d'effet : valeur annuelle en euros}.

    La date est sur la ligne de la valeur, ou sur la ligne qui la précède
    (« du 01/10/2015 », « 2001 » sous « 48,8904 F ») ; la première valeur de
    la ligne est l'annuelle, les suivantes la trimestrielle et la mensuelle.
    En 2001, la valeur en francs l'emporte sur l'euro entre parenthèses."""
    valeurs: dict[str, float] = {}
    attente: str | None = None
    en_suspens: float | None = None
    for ligne in texte.splitlines():
        etiquette = None
        semestre = _SEMESTRE.search(ligne)
        if semestre:
            mois = "01" if semestre.group(1) == "1er" else "07"
            etiquette = f"19{semestre.group(2)}-{mois}-01"
        elif (trouve := _DATE.search(ligne)):
            jour, mois, annee = trouve.groups()
            etiquette = f"{annee}-{mois}-{jour}"
        elif (trouve := _ANNEE.match(ligne)):
            etiquette = f"{trouve.group(1)}-01-01"
        valeur = _VALEUR.search(ligne.split("(")[0])
        montant = None
        if valeur:
            montant = float(valeur.group(1).replace(",", "."))
            if valeur.group(2) == "F":
                montant /= FRANC_PAR_EURO
        if etiquette and montant is not None:
            valeurs.setdefault(etiquette, montant)
            attente = en_suspens = None
        elif etiquette and en_suspens is not None:
            valeurs.setdefault(etiquette, en_suspens)
            attente = en_suspens = None
        elif etiquette:
            attente = etiquette
        elif montant is not None and attente is not None:
            valeurs.setdefault(attente, montant)
            attente = None
        elif montant is not None:
            en_suspens = montant
    return valeurs


def _pdftotext(contenu: bytes) -> str:
    if shutil.which("pdftotext") is None:
        raise SystemExit("pdftotext (poppler) est requis pour lire les fiches du RSI")
    with tempfile.TemporaryDirectory() as dossier:
        chemin = Path(dossier) / "fiche.pdf"
        chemin.write_bytes(contenu)
        return subprocess.run(["pdftotext", "-layout", str(chemin), "-"],
                              check=True, capture_output=True, text=True).stdout


def lire_ipp(texte: str, colonne: str) -> dict[str, float]:
    """Les dates d'effet de l'IPP, en euros, de DEBUT_IPP à DEBUT_FICHES."""
    valeurs: dict[str, float] = {}
    for ligne in csv.DictReader(io.StringIO(texte)):
        jour, mois, annee = ligne["date"].split("/")
        cellule = (ligne.get(colonne) or "").replace("\xa0", " ").strip()
        if not cellule or not DEBUT_IPP <= int(annee) < DEBUT_FICHES:
            continue
        montant = _nombre(cellule)
        if "FRF" in cellule:
            montant /= FRANC_PAR_EURO
        valeurs[f"{annee}-{mois}-{jour}"] = montant
    return valeurs


def au_31_decembre(datees: dict[str, float]) -> dict[int, float]:
    """La valeur en vigueur au 31 décembre de chaque année couverte."""
    dates = sorted(datees)
    premiere, derniere = int(dates[0][:4]), int(dates[-1][:4])
    annuelles: dict[int, float] = {}
    for annee in range(premiere, derniere + 1):
        en_vigueur = [d for d in dates if d <= f"{annee}-12-31"]
        annuelles[annee] = datees[en_vigueur[-1]]
    return annuelles


def controler(regime: str, datees: dict[str, float]) -> list[str]:
    erreurs = []
    dates = sorted(datees)
    for avant, apres in zip(dates, dates[1:]):
        rapport = datees[apres] / datees[avant]
        if not 0.95 <= rapport <= 1.40:
            erreurs.append(f"{regime} : {avant} {datees[avant]:.4f} → "
                           f"{apres} {datees[apres]:.4f} (× {rapport:.3f})")
    return erreurs


def main(argv: list[str]) -> int:
    bareme = lire_bareme(cnav_api.bareme(BAREME)["contenu"])
    resultat: dict[str, dict[str, float]] = {}
    erreurs: list[str] = []
    for regime in FICHES:
        fiche = lire_fiche(_pdftotext(_ouvrir(FICHES[regime])))
        parametre, colonne = PARAMETRES_IPP[regime]
        ipp = lire_ipp(_ouvrir(IPP.format(parametre)).decode("utf-8"), colonne)
        if not bareme.get(regime) or not fiche or not ipp:
            print(f"{regime} : une source est vide", file=sys.stderr)
            return 1
        datees = {**ipp, **fiche, **bareme[regime]}
        erreurs += controler(regime, datees)
        resultat[regime] = {d: round(v, 6) for d, v in sorted(datees.items())}
    if erreurs:
        print("Variations hors de [0,95 ; 1,40] :", *erreurs, sep="\n  ", file=sys.stderr)
        return 1
    serie = {
        f"{regime}|{annee}|valeur_service": round(valeur, 6)
        for regime, datees in resultat.items()
        for annee, valeur in au_31_decembre(datees).items()
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": "Cnav, base de législation (barème et fiches RVB du RSI) ; IPP avant 1988",
        "recupere_le": date.today().isoformat(),
        "serie": dict(sorted(serie.items())),
        "datees": resultat,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(serie)} valeurs annuelles écrites dans {SORTIE.relative_to(RACINE)}")
    if "--lignes" in argv:
        for cle, valeur in sorted(serie.items()):
            regime, annee, mesure = cle.split("|")
            print(f"{regime},{annee},{mesure},{valeur:.6f},haute")
        for regime, datees in resultat.items():
            for effet, valeur in datees.items():
                print(f"{regime},{effet},{valeur:.6f},haute")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
