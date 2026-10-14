#!/usr/bin/env python3
"""La pension moyenne brute et nette de tous les retraités, et leur répartition par taux de CSG, auprès de la DREES.

    python scripts/fetch/drees_pension_nette.py
    python scripts/fetch/drees_pension_nette.py --montants fin_2022.xlsx --eacr eacr_part_1.xlsx

POURQUOI CE TÉMOIN. Ce que les prélèvements sociaux retirent VRAIMENT à la
masse des pensions — la CSG, la CRDS, la CASA et la cotisation maladie des
complémentaires —, et non ce qu'ils retireraient au taux plein : 22 % des
retraités de droit direct sont exonérés de CSG, 13 % au taux réduit, 22 % au
taux médian. La dépense NETTE que l'Ageing Report publie à côté de la brute
s'y compare (``src/retraite_notionnelle/depense_nette.py``, action 138,
étape 3 ; ``tests/test_depense_nette.py``).

LES DEUX SOURCES.

* Le tableau 2.1-a des « Effectifs de retraités, montants des pensions et âges
  de départ à la retraite » (fin 2022, la dernière édition diffusée en
  classeur) : le montant mensuel moyen de la pension brute et de la pension
  nette, de droit direct ou totale (droit dérivé et majoration pour trois
  enfants compris), par retraité résidant en France ou à l'étranger, de 2008
  à 2022 (modèle Ancetre ; EIR). Deux moyennes sur les mêmes retraités : leur
  rapport est celui des MASSES, le taux effectif que la masse paie. La
  pension nette y est « calculée après déduction de la CSG, de la CRDS, de la
  Casa et de la cotisation maladie sur les retraites complémentaires ».
  L'ASPA n'y est pas.
* La feuille ``A-Prelev_sociaux`` de l'EACR, aux lignes « tous régimes » de
  source Ancetre ou EIR : les retraités de droit direct et de droit dérivé,
  sans doublon, par taux de CSG — exonérés, taux réduit, médian (depuis
  2019), plein. Des têtes, non des masses : elles bornent le taux effectif
  par en dessous, les pensions exonérées étant les plus petites.

Le témoin est versionné : les tests le relisent sans réseau.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_xlsx import feuilles  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
SORTIE = RACINE / "tests" / "temoins" / "drees_pension_nette.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
API = "https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog/datasets"
URL_MONTANTS = (f"{API}/1393_les-effectifs-et-montants-de-pension-des-retraites/attachments/"
                "les_effectifs_de_retraites_montants_des_pensions_et_ages_de_depart_a_la_"
                "retraite_fin_2022_xlsx")
URL_EACR = (f"{API}/donnes_eacr/attachments/"
            "62_eacr_diffusee_part_1_version_du_26_mai_2026_xlsx")

FEUILLE_MONTANTS = "2.1-a"
FEUILLE_CSG = "A-Prelev_sociaux"

#: Les colonnes du tableau 2.1-a que le témoin garde, pour l'ensemble des
#: retraités, par leur rang (la première, zéro, porte l'année).
COLONNES_MONTANTS = {
    "brute_directe": 7, "nette_directe": 10,  # droit direct, majoration comprise
    "brute_totale": 13, "nette_totale": 16,   # droit direct, dérivé et majoration
}

#: Les colonnes de la feuille de l'EACR, par leur intitulé, sous les noms du
#: dépôt.
TAUX_CSG = {"exonération": "exonere", "txRéduit": "reduit", "txMédian": "median",
            "txPlein": "plein", "txInconnu": "inconnu", "ensemble": "ensemble"}
DROITS = {"Direct": "direct", "Dérivé": "derive"}

_ANNEE = re.compile(r"^(\d{4})")


def _telecharger(url: str) -> bytes:
    demande = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=600) as reponse:
        return reponse.read()


def lire_montants(contenu: bytes) -> dict[int, dict[str, float]]:
    """Les montants mensuels moyens de chaque année publiée, en euros."""
    grille = feuilles(contenu, (FEUILLE_MONTANTS,))[FEUILLE_MONTANTS]
    entete = {c: grille.get((4, c)) for c in COLONNES_MONTANTS.values()}
    attendu = {7: "brute", 10: "nette", 13: "brute", 16: "nette"}
    if entete != attendu or grille.get((5, 7)) != "Ensemble" or grille.get((5, 16)) != "Ensemble":
        raise ValueError(f"le tableau 2.1-a a changé de forme : {entete}")
    resultat: dict[int, dict[str, float]] = {}
    for ligne in range(6, 60):
        trouve = _ANNEE.match(str(grille.get((ligne, 0), "")).replace(".0", ""))
        if not trouve:
            continue
        valeurs = {cle: grille.get((ligne, colonne))
                   for cle, colonne in COLONNES_MONTANTS.items()}
        if all(isinstance(v, float) for v in valeurs.values()):
            resultat[int(trouve.group(1))] = valeurs
    return resultat


def lire_csg(contenu: bytes) -> dict[int, dict[str, dict[str, float]]]:
    """Les retraités tous régimes de chaque année, par droit et taux de CSG."""
    grille = feuilles(contenu, (FEUILLE_CSG,))[FEUILLE_CSG]
    colonnes = {grille.get((0, c)): c for c in range(12)}
    resultat: dict[int, dict[str, dict[str, float]]] = {}
    for ligne in range(1, max(r for r, _c in grille) + 1):
        def cellule(nom: str):
            return grille.get((ligne, colonnes[nom]))
        if cellule("CC") != "0000" or cellule("PSoc") != "CSG":
            continue
        annee = int(cellule("Année"))
        droit = DROITS[cellule("Droit")]
        resultat.setdefault(annee, {})[droit] = {
            cle: float(cellule(nom) or 0.0) for nom, cle in TAUX_CSG.items()}
        resultat[annee][droit]["source"] = cellule("Source")
    return resultat


def temoin(montants: bytes, eacr: bytes) -> dict:
    return {
        "source": {
            "editeur": "DREES",
            "montants": ("Les effectifs de retraités, montants des pensions et âges de départ "
                         "à la retraite, fin 2022, tableau 2.1-a (DREES, EIR, modèle Ancetre)"),
            "url_montants": URL_MONTANTS,
            "csg": ("Enquête annuelle auprès des caisses de retraite, classeur diffusé "
                    "le 26 mai 2026, feuille A-Prelev_sociaux, lignes tous régimes (0000)"),
            "url_csg": URL_EACR,
            "lu_le": "2026-10-14",
        },
        "conventions": {
            "montants": ("montant mensuel moyen au 31 décembre, en euros courants, par "
                         "retraité de droit direct résidant en France ou à l'étranger ; "
                         "« totale » ajoute le droit dérivé et la majoration pour trois "
                         "enfants ; la nette déduit la CSG, la CRDS, la Casa et la "
                         "cotisation maladie des complémentaires ; ni l'ASPA ni les "
                         "versements forfaitaires uniques"),
            "csg": ("retraités sans doublon, tous régimes, par taux de CSG au 31 décembre ; "
                    "le taux médian existe depuis 2019"),
        },
        "montants": {str(a): v for a, v in sorted(lire_montants(montants).items())},
        "csg": {str(a): v for a, v in sorted(lire_csg(eacr).items())},
    }


def main() -> int:
    analyse = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    analyse.add_argument("--montants", type=Path, help="le classeur des montants, déjà téléchargé")
    analyse.add_argument("--eacr", type=Path, help="la première partie de l'EACR, déjà téléchargée")
    arguments = analyse.parse_args()
    montants = (arguments.montants.read_bytes() if arguments.montants
                else _telecharger(URL_MONTANTS))
    eacr = arguments.eacr.read_bytes() if arguments.eacr else _telecharger(URL_EACR)
    contenu = temoin(montants, eacr)
    SORTIE.write_text(json.dumps(contenu, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} : {len(contenu['montants'])} années de montants, "
          f"{len(contenu['csg'])} de taux de CSG")
    return 0


if __name__ == "__main__":
    sys.exit(main())
