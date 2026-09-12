#!/usr/bin/env python3
"""Prix et valeur du point des complémentaires artisans et commerçants, chez l'IPP.

    python scripts/fetch/ipp_points_independants.py

POURQUOI IL EXISTE.

Le régime complémentaire des artisans (1979-2012) et le Nouveau régime des
indépendants des commerçants (2004-2012) sont des régimes EN POINTS, et leurs
fiches le disent. Mais aucune valeur de point n'était versée pour eux : le
moteur retombait alors sur le rendement instantané de
`regimes/rendements_points.csv`, qui portait 6,74 % — le rendement du RCI
d'aujourd'hui — de 1979 à 2012. Or le rendement de ces régimes valait ONZE
POUR CENT au début des années 1980. Trente ans de droits étaient comptés à
peu près moitié moins qu'ils ne valaient.

Les barèmes de l'Institut des politiques publiques les portent, dans deux
paramètres par régime :

* ``salref_rc_art`` et ``salref_rc_com`` — le SALAIRE DE RÉFÉRENCE, c'est-à-dire
  le prix d'achat d'un point ;
* ``pt_rc_art`` et ``pt_rc_com`` — la VALEUR DE SERVICE, ce qu'un point rapporte
  en rente annuelle.

Leur rapport est le rendement, et c'est exactement ce que consomme le moteur.
Le RCI, qui leur succède en 2013, est déjà couvert par OpenFisca : ce
récupérateur s'arrête donc en 2012, pour ne pas revendiquer deux fois les mêmes
lignes.

TROIS PIÈGES, ET CE QUE LE SCRIPT EN FAIT.

* **LES FRANCS.** Jusqu'en 2001 les barèmes sont libellés en francs, et le
  fichier de référence tient ses valeurs « en euros courants de l'année ». La
  conversion est celle de la loi : 6,55957 francs pour un euro.

* **UN LIBELLÉ FAUX.** La valeur de service des artisans au 1er janvier 2001 est
  écrite « 0,2847 FRF ». Ce n'est pas un franc : c'est un euro. La lecture est
  arithmétique — 0,2847 € font 1,867 F, dans le prolongement des 1,83 F de 2000
  et des 0,2845 € de 2002, quand la lire en francs donnerait 0,0434 €, une
  division par six en une année. Le script CORRIGE cette ligne, et il vérifie
  ensuite que plus aucune rupture de ce genre ne subsiste : toute variation
  annuelle hors de la plage [0,5 ; 2] arrête tout.

* **LES DATES D'EFFET.** Le barème est une suite de dates d'effet, pas une série
  annuelle : une année absente veut dire que rien n'a changé, et plusieurs
  valeurs peuvent se succéder dans la même année. Le fichier de référence
  retient « la valeur en vigueur au 31 décembre » ; c'est donc la DERNIÈRE date
  d'effet de l'année, ou la dernière antérieure si l'année n'en porte aucune.

CE QUE LE SCRIPT NE REND PAS. Les trois valeurs de point que le RCI sert selon
l'ANCIENNETÉ des points repris — un point d'artisan acquis avant 1979, entre
1979 et 1996, ou entre 1997 et 2012 n'a pas la même valeur depuis 2009. Le
fichier de référence porte une valeur de service par régime et par année, et le
dépôt retient celle du millésime 1997-2012, qui est aussi celle du RCI. Les
points acquis de 1979 à 1996 sont donc surestimés de 4,5 % à la liquidation.
L'écart est documenté dans la fiche ; il est sans commune mesure avec celui que
ce récupérateur corrige.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

RACINE = "https://baremes.ipp.eu/parameters/regimes-de-retraites"
SORTIE = Path(__file__).resolve().parents[2] / "data" / "brut" / "ipp_points_independants.json"

#: Taux de conversion légal du franc en euro (règlement CE 2866/98).
FRANC_PAR_EURO = 6.55957

#: Les quatre paramètres à lire, et où ils vont. Pour les artisans, la valeur de
#: service éclate en trois colonnes à partir de 2009, selon l'ancienneté des
#: points : on retient celle du millésime 1997-2012, qui est aussi la valeur du
#: point du RCI.
PARAMETRES = {
    ("rco_artisans", "salaire_reference"): (
        "retraites.independants.salref_rc_art",
        ("retraites.independants.salref_rc_art",),
    ),
    ("rco_artisans", "valeur_service"): (
        "retraites.independants.pt_rc_art",
        ("valeur_points_acquis", "valeur_points_acquis_entre_1997_2012"),
    ),
    ("nric", "salaire_reference"): (
        "retraites.independants.salref_rc_com",
        ("retraites.independants.salref_rc_com",),
    ),
    ("nric", "valeur_service"): (
        "retraites.independants.pt_rc_com",
        ("retraites.independants.pt_rc_com",),
    ),
}

#: Dernière année où ces régimes existent. Le RCI prend la suite en 2013, et il
#: est déjà couvert par OpenFisca.
DERNIERE_ANNEE = 2012

#: Le libellé fautif, et ce qu'il vaut réellement. Voir l'en-tête.
LIBELLE_FAUTIF = {("rco_artisans", "valeur_service", 2001): 0.2847}


def _nombre(brut: str) -> tuple[float, bool] | None:
    """(valeur, est_en_francs) — None si la cellule est vide."""
    texte = brut.replace(" ", "").replace("\xa0", "").replace(" ", "").strip()
    if not texte:
        return None
    francs = texte.endswith("FRF")
    texte = texte.removesuffix("FRF").removesuffix("€").replace(",", ".").strip()
    if not texte:
        return None
    return float(texte), francs


def _telecharger(parametre: str) -> list[dict[str, str]]:
    url = f"{RACINE}/{parametre}/csv"
    demande = urllib.request.Request(url, headers={"User-Agent": "retraite-notionnelle"})
    with urllib.request.urlopen(demande, timeout=180) as reponse:
        texte = reponse.read().decode("utf-8")
    return list(csv.DictReader(io.StringIO(texte)))


def _serie_annuelle(lignes: list[dict[str, str]], colonnes: tuple[str, ...],
                    regime: str, mesure: str) -> dict[int, float]:
    """Dates d'effet -> valeur en vigueur au 31 décembre de chaque année."""
    effets: list[tuple[tuple[int, int, int], float]] = []
    for ligne in lignes:
        jour, mois, annee = (int(x) for x in ligne["date"].split("/"))
        for colonne in colonnes:
            lu = _nombre(ligne.get(colonne, "") or "")
            if lu is None:
                continue
            valeur, francs = lu
            fautif = LIBELLE_FAUTIF.get((regime, mesure, annee))
            if fautif is not None and abs(valeur - fautif) < 1e-9:
                francs = False
            effets.append(((annee, mois, jour), valeur / (FRANC_PAR_EURO if francs else 1.0)))
            break
    if not effets:
        return {}
    effets.sort()
    serie: dict[int, float] = {}
    courant: float | None = None
    index = 0
    for annee in range(effets[0][0][0], DERNIERE_ANNEE + 1):
        while index < len(effets) and effets[index][0][0] <= annee:
            courant = effets[index][1]
            index += 1
        if courant is not None:
            serie[annee] = courant
    return serie


def verifier(series: dict[tuple[str, str], dict[int, float]]) -> list[str]:
    """Continuité des séries, et plausibilité des rendements qui s'en déduisent."""
    anomalies = []
    for (regime, mesure), serie in sorted(series.items()):
        annees = sorted(serie)
        for avant, apres in zip(annees, annees[1:]):
            if apres != avant + 1:
                anomalies.append(f"{regime}/{mesure} : trou entre {avant} et {apres}")
            rapport = serie[apres] / serie[avant]
            if not 0.5 <= rapport <= 2.0:
                anomalies.append(
                    f"{regime}/{mesure} : rupture en {apres}, "
                    f"{serie[avant]:.6f} -> {serie[apres]:.6f}"
                )
    for regime in sorted({r for r, _ in series}):
        achat = series.get((regime, "salaire_reference"), {})
        service = series.get((regime, "valeur_service"), {})
        for annee in sorted(set(achat) & set(service)):
            rendement = service[annee] / achat[annee]
            if not 0.03 <= rendement <= 0.20:
                anomalies.append(
                    f"{regime} {annee} : rendement invraisemblable {rendement:.2%}"
                )
    return anomalies


def main() -> int:
    series: dict[tuple[str, str], dict[int, float]] = {}
    for (regime, mesure), (parametre, colonnes) in PARAMETRES.items():
        try:
            lignes = _telecharger(parametre)
        except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
            print(f"ÉCHEC   {parametre} : {erreur}", file=sys.stderr)
            return 1
        serie = _serie_annuelle(lignes, colonnes, regime, mesure)
        if not serie:
            print(f"ÉCHEC   {parametre} : aucune valeur lue", file=sys.stderr)
            return 1
        series[(regime, mesure)] = serie
        annees = sorted(serie)
        print(f"OK      {regime}/{mesure} : {annees[0]}-{annees[-1]}, "
              f"{len(serie)} valeurs")

    anomalies = verifier(series)
    if anomalies:
        print("\nSéries incohérentes, rien n'est écrit :", file=sys.stderr)
        for anomalie in anomalies:
            print(f"  {anomalie}", file=sys.stderr)
        return 1

    plat = {}
    for (regime, mesure), serie in sorted(series.items()):
        for annee, valeur in sorted(serie.items()):
            plat[f"{regime}|{annee}|{mesure}"] = valeur

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": RACINE,
            "recupere_le": date.today().isoformat(),
            "parametres": {f"{r}/{m}": p for (r, m), (p, _) in sorted(PARAMETRES.items())},
            "note": "complémentaires des artisans (1979-2012) et des commerçants "
                    "(2004-2012) ; le RCI qui leur succède est couvert par OpenFisca",
            "serie": plat,
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"\n{len(plat)} valeurs écrites dans {SORTIE}")
    for regime in sorted({r for r, _ in series}):
        achat = series[(regime, "salaire_reference")]
        service = series[(regime, "valeur_service")]
        communes = sorted(set(achat) & set(service))
        if communes:
            debut, fin = communes[0], communes[-1]
            print(f"  {regime} : rendement {service[debut] / achat[debut]:.2%} en "
                  f"{debut}, {service[fin] / achat[fin]:.2%} en {fin}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
