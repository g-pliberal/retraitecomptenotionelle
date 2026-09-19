#!/usr/bin/env python3
"""Récupération des Comptes de la protection sociale auprès de la DREES.

    python scripts/fetch/drees_cps.py

Les Comptes de la protection sociale sont la comptabilité nationale du social :
ils recensent, année par année et régime par régime, les prestations réellement
versées. Le risque ``VIEILLESSE-SURVIE`` est celui qui porte les retraites — et
c'est la SEULE série longue française de dépenses de retraite publiée par leur
producteur.

Deux grains, et deux couvertures :

* le **total tous régimes** remonte à 1959, sans interruption ;
* la **ventilation par régime** ne commence qu'en 1990. De 1981 à 1989, la DREES
  publie bien une ventilation, mais dans une nomenclature qui n'est pas celle
  qui suit — « Régime général de la Sécurité sociale » et « Régimes spéciaux »
  y recouvrent des périmètres que 1990 redécoupe. Les rapprocher demanderait
  une reconstitution que personne n'a publiée : ces neuf années restent donc
  hors de la ventilation, et le total les couvre.

L'API est celle d'Opendatasoft, interrogeable **sans clé**. Le fichier produit,
``data/brut/drees_cps.json``, est le document source : il n'est pas lu par le
modèle, seulement par ``scripts/verifier_donnees.py``, qui y applique le
regroupement des régimes et écrit ``data/reference/macro/``.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = (
    "https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog"
    "/datasets/305_les-comptes-de-la-protection-sociale/exports/json"
)
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
SORTIE = Path("data/brut/drees_cps.json")

#: Poste des comptes retenu. ``E11-2`` est le risque vieillesse-survie tout
#: entier : pensions de droit direct et de droit dérivé, minimum vieillesse,
#: prestations liées à la dépendance des personnes âgées. C'est le seul niveau
#: publié sans interruption depuis 1959 ; les sous-postes ne le sont que depuis
#: 2020, et ils sont récupérés aussi, pour dire quelle part du total est de la
#: retraite au sens strict.
POSTE = "E11-2"

#: Sous-postes récupérés en plus, au niveau national seulement.
SOUS_POSTES = ("E11-21.1", "E11-22.1")

#: Les prestations NON CONTRIBUTIVES que les comptes isolent, et la ligne de
#: `legislation/avantages_non_contributifs.yaml` que chacune renseigne.
#:
#: C'est la découverte de ce chantier : plusieurs avantages que le modèle
#: calculait à zéro — faute de cas type qui les porte — sont PUBLIÉS, poste par
#: poste, depuis 2020. La majoration pour enfants en est l'exemple criant : la
#: grille n'a aucun cas type de trois enfants et la chiffrait donc à zéro, quand
#: les comptes en portent près de huit milliards.
#:
#: Le producteur prime sur le modèle, et c'est la règle du dépôt
#: (`data/sources.yaml`, critère 1) : là où ces postes existent, ils
#: REMPLACENT la ligne calculée au lieu de la compléter.
PRESTATIONS: tuple[tuple[str, str], ...] = (
    ("E11-21.1.41", "majoration_enfants"),
    ("E11-21.1.42", "majoration_tierce_personne"),
    ("E11-21.1.43", "majoration_conjoint_a_charge"),
    ("E11-21.1.12", "pensions_inaptitude"),
    ("E11-21.1.13", "pensions_invalidite"),
    ("E11-21.2", "minimum_vieillesse"),
    ("E11-22.1.16", "pension_orphelin"),
    ("E11-22.1.20", "majoration_reversion"),
    # Trois dispositifs que l'inventaire ne portait pas du tout, et que les
    # comptes isolent : la majoration de résidence des retraités de la fonction
    # publique outre-mer, en deux postes qu'il faut réunir (droit direct et
    # ayants cause) ; l'allocation des anciens combattants, qui n'est pas une
    # pension mais que les comptes rangent dans le risque vieillesse ; et la
    # majoration de pension des assurés partis au titre du handicap.
    ("E11-21.1.21", "indemnite_temporaire_direct"),
    ("E11-22.1.21", "indemnite_temporaire_derive"),
    ("E11-21.1.14", "retraite_du_combattant"),
    ("E11-21.1.44", "majoration_assures_handicapes"),
)


def recuperer(condition: str) -> list[dict]:
    url = f"{BASE}?{urllib.parse.urlencode({'where': condition})}"
    demande = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=180) as reponse:
        return json.loads(reponse.read())


def main() -> int:
    codes = ", ".join(
        f'"{code}"'
        for code in (POSTE, *SOUS_POSTES, *(c for c, _ in PRESTATIONS))
    )
    try:
        lignes = recuperer(f"ps_code in ({codes})")
    except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
        print(f"DREES indisponible : {erreur}", file=sys.stderr)
        return 1

    # Trois séries, dans la forme où le vérificateur les attend : le total
    # national du risque, ses deux sous-postes de pensions, et la ventilation
    # par régime — celle-ci sous le libellé exact que publie la DREES, dont le
    # regroupement en systèmes lisibles relève du vérificateur et non d'ici.
    total: dict[str, float] = {}
    pensions: dict[str, dict[str, float]] = {code: {} for code in SOUS_POSTES}
    prestations: dict[str, dict[str, float]] = {nom: {} for _, nom in PRESTATIONS}
    par_code = dict(PRESTATIONS)
    regimes: dict[str, dict[str, float]] = {}
    for ligne in lignes:
        annee, valeur = str(ligne["annee"]), ligne["val"]
        if valeur is None:
            continue
        if ligne["ps_code"] in par_code:
            if ligne["si_niveau"] == "0":
                prestations[par_code[ligne["ps_code"]]][annee] = valeur
            continue
        if ligne["ps_code"] != POSTE:
            if ligne["si_niveau"] == "0":
                pensions[ligne["ps_code"]][annee] = valeur
            continue
        if ligne["si_niveau"] == "0":
            total[annee] = valeur
        elif ligne["si_niveau"] == "2":
            regimes.setdefault(ligne["nom_regime"], {})[annee] = valeur

    charge = {
        "source": BASE,
        "poste": POSTE,
        "total": dict(sorted(total.items())),
        "pensions": {code: dict(sorted(v.items())) for code, v in pensions.items()},
        "prestations": {
            nom: dict(sorted(serie.items()))
            for nom, serie in sorted(prestations.items()) if serie
        },
        "regimes": {nom: dict(sorted(v.items())) for nom, v in sorted(regimes.items())},
        "unite": "millions d'euros courants",
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps(charge, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    annees = sorted(int(a) for a in total)
    print(f"{len(annees)} années écrites dans {SORTIE}")
    print(f"Total tous régimes : {min(annees)}-{max(annees)}")
    print(f"Ventilation : {len(regimes)} régimes")
    for nom, serie in sorted(prestations.items()):
        if serie:
            derniere = max(serie)
            print(f"  {nom:32s} {serie[derniere] / 1000:7.2f} Md€ en {derniere}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
