#!/usr/bin/env python3
"""Les impôts de la retraite qui sont assis sur une rémunération.

    python scripts/fetch/ccss_impots_retraite.py [--depuis 2013] [--jusqu 2026]

CE QU'ON VIENT CHERCHER, ET POURQUOI
-------------------------------------
La proposition du Parti libéral cesse d'affecter à la retraite les impôts et
taxes qui la financent — 57,1 Md€ en 2024, le poste que ``cout.py`` appelle
``impots_et_taxes``. La décision du 20 septembre 2026 ajoute ce qu'il advient
de cette recette : **la moitié est rendue aux salaires, la moitié éteint de la
dette.** Rendre aux salaires suppose de savoir ce qui, dans ce poste, est
PRÉLEVÉ SUR UNE RÉMUNÉRATION — le reste est assis sur du capital, sur des
pensions, sur un chiffre d'affaires, et le rendre au salarié n'aurait pas de
sens.

Le droit dit lesquels, et il tient en deux lignes :

* la **taxe sur les salaires** (article 231 du code général des impôts), dont
  l'article L. 131-8, 1° du code de la sécurité sociale verse 58,35 % à la
  branche vieillesse — la fraction est de la loi, elle bouge à chaque LFSS ;
* le **forfait social** (article L. 137-15), dont l'article L. 241-3, 1° donne
  le produit ENTIER à l'assurance vieillesse.

Et il dit, ce qui est le résultat le plus contre-intuitif de cette lecture :
**la CSG sur les revenus d'activité ne finance AUCUNE retraite.** Ses 9,20
points se répartissent CNAF 0,95, assurance maladie 4,25, CADES 0,45, Unédic
1,47, CNSA 2,08 — 9,20 exactement, et rien pour la branche vieillesse
(L. 131-8, 3°, version en vigueur au 1er février 2026). Ce que la retraite
encaisse en CSG est assis sur le capital (6,67 points sur 10,6) et sur les
pensions (2,94 points) : pas sur un salaire.

LA SÉRIE COMMENCE EN 2019, ET C'EST LE DROIT QUI LE DIT
--------------------------------------------------------
Jusqu'en 2018, le fonds de solidarité vieillesse recevait LUI AUSSI une
fraction de la taxe sur les salaires et du forfait social : lire la seule
section CNAV d'un rapport plus ancien donnerait donc moins que ce que la
retraite encaisse, sans le dire. L'article L. 135-3 du code de la sécurité
sociale, dans sa rédaction en vigueur depuis le 1er janvier 2019, referme la
question d'une phrase : « Les recettes du fonds sont constituées par une
fraction du produit de la contribution sociale généralisée » — et rien
d'autre. À compter de 2019, la section CNAV porte donc l'intégralité de ce
que ces deux impôts versent à la retraite.

Les rapports antérieurs sont lus quand même, et ce qu'ils donnent est écarté
ici plutôt qu'en amont : ce qui est jeté se voit.

OÙ, ET POURQUOI LÀ
-------------------
Dans les rapports à la Commission des comptes de la Sécurité sociale, comme
``ccss_transferts_retraite.py``, dont ce script reprend la mécanique entière —
la page qui liste les rapports, le cache, le lecteur de PDF, la lecture d'une
ligne de tableau, la règle du PREMIER rapport qui arrête une année. La fiche
cherchée est celle des « contributions sociales et recettes fiscales brutes »,
qui ventile ces recettes PAR AFFECTATAIRE : une section par branche, et la
section CNAV porte les deux lignes.

LA SECTION, ET POURQUOI ELLE NE PEUT PAS ÊTRE IGNORÉE
------------------------------------------------------
« Taxe sur les salaires » apparaît quatre fois dans le même tableau — une par
branche qui en reçoit une fraction — et une cinquième dans la fiche de la CNAF.
Prendre la première ligne qui porte ce libellé, comme le fait le script des
transferts, donnerait la part de la branche maladie. Ce script suit donc les
SECTIONS : un en-tête d'affectataire ouvre la sienne, le suivant la ferme, et
seules les lignes de la section CNAV sont retenues.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fetch.ccss_transferts_retraite import (  # noqa: E402
    COLONNE, ENTETE, _colonnes, _libelle, _plie, _telecharger, _valeurs,
    lignes_pdf, rapports,
)

SORTIE = Path("data/brut/ccss_impots_retraite.json")

#: Première année où la section CNAV porte TOUT ce que ces deux impôts versent
#: à la retraite. Voir le docstring : avant 2019, le fonds de solidarité
#: vieillesse en recevait sa part.
PREMIERE_ANNEE = 2019

#: L'en-tête qui ouvre la section de l'assurance vieillesse, et ceux qui la
#: ferment. Le rapport nomme l'affectataire « CNAV » ; les autres sections
#: portent le nom de leur branche, et la ligne de total « CNAV - Recettes
#: fiscales » clôt la sienne.
OUVRE_CNAV = re.compile(r"^cnav$")
FERME_CNAV = re.compile(
    r"^(cnav-recettesfiscales|branche[a-z-]+|rg-total|fsv|autresregimesdebase)"
)

#: Les deux lignes cherchées, dans la section CNAV.
LIGNES = (
    ("taxe_sur_les_salaires", r"^taxesurlessalaires$"),
    ("forfait_social", r"^forfaitsocial$"),
)


def lire_rapport(octets: bytes) -> dict[str, dict[int, float]]:
    """Les deux lignes de la section CNAV d'un rapport."""
    colonnes: list | None = None
    dans_la_section = False
    trouvees: dict[str, dict[int, float]] = {}
    for ligne in lignes_pdf(octets):
        if ENTETE.match(ligne) and len(COLONNE.findall(ligne)) >= 2:
            candidates = _colonnes(ligne)
            if sum(1 for c in candidates if c is not None) >= 2:
                colonnes = candidates
                dans_la_section = False
            continue
        if colonnes is None:
            continue
        libelle = _libelle(ligne)
        plie = _plie(libelle)
        if OUVRE_CNAV.match(plie):
            dans_la_section = True
            continue
        if dans_la_section and FERME_CNAV.match(plie):
            dans_la_section = False
            continue
        if not dans_la_section:
            continue
        for cle, motif in LIGNES:
            if re.match(motif, plie) and cle not in trouvees:
                valeurs = _valeurs(ligne, libelle, colonnes)
                if valeurs:
                    trouvees[cle] = valeurs
    return trouvees


def moissonner(depuis: int, jusqu: int) -> tuple[dict, dict]:
    """Chaque rapport, du plus ancien au plus récent.

    Le PREMIER rapport qui arrête une année l'emporte — la règle de
    ``ccss_transferts_retraite.py``, et on n'en change pas : les rapports
    suivants reprennent une année pour mémoire, parfois sur un périmètre
    révisé. ``provenance`` garde, année par année, le rapport qui l'a donnée.
    """
    series: dict[str, dict[int, float]] = {cle: {} for cle, _ in LIGNES}
    provenance: dict[str, dict[int, int]] = {cle: {} for cle, _ in LIGNES}
    for annee_rapport, url in sorted(rapports().items()):
        if not depuis <= annee_rapport <= jusqu:
            continue
        try:
            octets = _telecharger(annee_rapport, url)
        except Exception as erreur:  # noqa: BLE001
            print(f"  {annee_rapport} : illisible ({erreur})")
            continue
        lues = lire_rapport(octets)
        neuves, ecartees = 0, 0
        for cle, valeurs in lues.items():
            for annee, montant in valeurs.items():
                if annee >= annee_rapport or annee in series[cle]:
                    continue
                if annee < PREMIERE_ANNEE:
                    ecartees += 1
                    continue
                series[cle][annee] = montant
                provenance[cle][annee] = annee_rapport
                neuves += 1
        trouve = ", ".join(sorted(lues)) or "rien de lisible"
        ecart = f", {ecartees} avant {PREMIERE_ANNEE} écartée(s)" if ecartees else ""
        print(f"  {annee_rapport} : {trouve} — {neuves} valeur(s) neuve(s){ecart}")
    return (
        {cle: dict(sorted(v.items())) for cle, v in series.items()},
        {cle: dict(sorted(v.items())) for cle, v in provenance.items()},
    )


def main() -> int:
    analyse = argparse.ArgumentParser(description=__doc__)
    analyse.add_argument("--depuis", type=int, default=2013)
    analyse.add_argument("--jusqu", type=int, default=2100)
    options = analyse.parse_args()
    print("Rapports à la Commission des comptes de la Sécurité sociale :")
    series, provenance = moissonner(options.depuis, options.jusqu)
    charge = {
        "source": "https://www.securite-sociale.fr",
        "unite": "millions d'euros courants",
        "affectataire": "CNAV",
        "series": series,
        "provenance": provenance,
    }
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(charge, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    for cle, valeurs in series.items():
        annees = sorted(valeurs)
        borne = f"{annees[0]}–{annees[-1]}" if annees else "vide"
        print(f"{cle} : {len(valeurs)} valeurs, {borne}")
    print(f"→ {SORTIE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
