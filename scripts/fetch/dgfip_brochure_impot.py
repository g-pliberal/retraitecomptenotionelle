#!/usr/bin/env python3
"""Les tableaux de l'impôt de la brochure pratique de la DGFiP, en témoin.

    python scripts/fetch/dgfip_brochure_impot.py           # réécrit le témoin
    python scripts/fetch/dgfip_brochure_impot.py --lister  # imprime, sans écrire

À quoi il sert. Le calcul de l'impôt sur le revenu d'un foyer
(``retraite_notionnelle/impot_revenu.py``, action 138, étape 5) se vérifie à
l'euro sur les exemples que l'administration publie. La brochure pratique de
chaque année en publie des milliers : au chapitre « Calcul de l'impôt », un
barème « qui vous donne, par lecture directe, le montant de l'impôt en
fonction du revenu imposable et du nombre de parts », plafonnement du
quotient familial et décote compris, pour quatre situations — les personnes
seules qui ne vivent pas seules avec leurs enfants, les parents isolés, les
veufs ayant un enfant à charge, les couples mariés ou pacsés.

Ce script télécharge ce chapitre des brochures de 2024 (revenus de 2023) et
de 2025 (revenus de 2024), en lit les tableaux avec ``lecture_pdf.py``, et
les écrit dans ``tests/temoins/brochure_impot_revenu.json``, que
``tests/test_impot_revenu.py`` rejoue. Le témoin est VERSIONNÉ : le test
tourne sans réseau.

Ce qu'il écarte : le tableau de qui vit seul après avoir élevé un enfant
(case L), que le dépôt ne calcule pas, et toute ligne qui ne se lit pas
entière — un montant coupé par un blanc de milliers (« 32 198 »), qu'un
nombre de colonnes faux trahit, ou un bloc invraisemblable
(:func:`_vraisemblable`). Le lecteur du dépôt ne lit pas la page des
personnes seules de la brochure de 2025 : son tableau manque au témoin, celui
de 2024 y est. La brochure ne tient compte ni des
réductions d'impôt, ni de la réduction complémentaire des invalides ; le
barème des veufs tient compte de la leur.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_pdf import lignes_pdf  # noqa: E402

RACINE_DEPOT = Path(__file__).resolve().parents[2]
SORTIE = RACINE_DEPOT / "tests" / "temoins" / "brochure_impot_revenu.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Chaque brochure : l'année des revenus qu'elle impose, et l'adresse de son
#: chapitre « Calcul de l'impôt ».
BROCHURES = {
    2023: "https://www.impots.gouv.fr/www2/fichiers/documentation/brochure/ir_2024/pdf_som/"
          "21-calcul_impot_361a374.pdf",
    2024: "https://www.impots.gouv.fr/www2/fichiers/documentation/brochure/ir_2025/pdf_som/"
          "21-calcul_impot_359a372.pdf",
}

ENTETE_TABLEAU = "IMPÔT SUIVANT LE NOMBRE DE PARTS"


def _telecharger(adresse: str) -> bytes:
    demande = urllib.request.Request(adresse, headers=ENTETES)
    with urllib.request.urlopen(demande, timeout=180) as reponse:
        return reponse.read()


def _parts(ligne: str) -> list[float] | None:
    """Les parts d'un en-tête de colonnes (« 2 2,5 3 … »), une fois : des
    nombres de parts, dont un demi au moins."""
    jetons = ligne.split()
    if (not jetons or not all(re.fullmatch(r"\d{1,2}(,5)?", j) for j in jetons)
            or not any("," in j for j in jetons)):
        return None
    parts = [float(j.replace(",", ".")) for j in jetons]
    moitie = len(parts) // 2
    if len(parts) % 2 == 0 and parts[:moitie] == parts[moitie:]:
        parts = parts[:moitie]
    return parts


def _situation(parts: list[float], avant: list[str]) -> str | None:
    """La situation d'un tableau, par ses colonnes et par son titre."""
    if parts[0] == 1.0:
        return "personne_seule"
    if parts[0] == 2.5:
        return "veuf"
    titre = " ".join(avant)
    if "MARIÉS OU PACSÉS" in titre:
        return "couple"
    if "élevant seuls" in titre:
        return "parent_isole"
    return None


def _vraisemblable(revenu: int, impots: list[int]) -> bool:
    """Un bloc lu entier : un revenu de tableau (au moins 10 000 €), des impôts
    qui décroissent avec les parts et n'atteignent pas 45 % du revenu. Une
    ligne dont un bloc ne l'est pas — un montant coupé, un bloc décalé — est
    écartée entière."""
    return (revenu >= 10000 and impots == sorted(impots, reverse=True)
            and all(0 <= impot < 0.45 * revenu for impot in impots))


def tableaux(lignes: list[str]) -> dict[str, dict]:
    """Les tableaux d'une brochure : par situation, les parts de ses colonnes,
    et chaque ligne lue entière — un revenu imposable, l'impôt de chaque
    colonne."""
    lus: dict[str, dict] = {}
    entetes = [i for i, ligne in enumerate(lignes) if ENTETE_TABLEAU in ligne]
    for rang, debut in enumerate(entetes):
        fin = entetes[rang + 1] if rang + 1 < len(entetes) else len(lignes)
        parts = next((p for p in map(_parts, lignes[debut + 1:debut + 4]) if p), None)
        if not parts:
            continue
        situation = _situation(parts, lignes[max(debut - 8, 0):debut])
        if situation is None:
            continue
        table = lus.setdefault(situation, {"parts": parts, "lignes": {}})
        largeur = len(parts) + 1
        for ligne in lignes[debut + 1:fin]:
            ligne = ligne.replace("de 0 à", " ")
            if re.search(r"[^\d\s]", ligne) or _parts(ligne):
                continue
            jetons = [int(j) for j in ligne.split()]
            if not jetons or len(jetons) % largeur:
                continue
            blocs = [(jetons[depart], jetons[depart + 1:depart + largeur])
                     for depart in range(0, len(jetons), largeur)]
            if all(_vraisemblable(revenu, impots) for revenu, impots in blocs):
                # Les deux colonnes d'une page peuvent sortir dans l'un ou
                # l'autre ordre : chaque bloc dit son revenu.
                for revenu, impots in blocs:
                    table["lignes"][revenu] = impots
    return {situation: {"parts": table["parts"],
                        "lignes": [[revenu, impots] for revenu, impots in sorted(table["lignes"].items())]}
            for situation, table in sorted(lus.items())}


def ecrire(lus: dict[int, dict]) -> str:
    sortie = ['{',
              '  "source": "DGFiP, brochure pratique de l\'impôt sur le revenu, chapitre '
              '« Calcul de l\'impôt », barème par lecture directe (plafonnement du quotient '
              'familial et décote compris)",',
              '  "ecrit_par": "scripts/fetch/dgfip_brochure_impot.py",',
              '  "brochures": {']
    annees = sorted(lus)
    for rang, annee in enumerate(annees):
        sortie.append(f'    "{annee}": {{')
        sortie.append(f'      "adresse": {json.dumps(BROCHURES[annee])},')
        sortie.append('      "tableaux": {')
        situations = list(lus[annee].items())
        for k, (situation, table) in enumerate(situations):
            sortie.append(f'        "{situation}": {{"parts": {json.dumps(table["parts"])}, "lignes": [')
            lignes = [f'          {json.dumps(ligne)}' for ligne in table["lignes"]]
            sortie.append(",\n".join(lignes))
            sortie.append("        ]}" + ("," if k + 1 < len(situations) else ""))
        sortie.append("      }")
        sortie.append("    }" + ("," if rang + 1 < len(annees) else ""))
    sortie += ["  }", "}"]
    return "\n".join(sortie) + "\n"


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--lister", action="store_true", help="imprime sans écrire")
    arguments = analyseur.parse_args(argv)
    lus = {annee: tableaux(lignes_pdf(_telecharger(adresse)))
           for annee, adresse in BROCHURES.items()}
    texte = ecrire(lus)
    json.loads(texte)
    if arguments.lister:
        print(texte)
        return 0
    SORTIE.write_text(texte, encoding="utf-8")
    for annee, situations in lus.items():
        compte = {s: len(t["lignes"]) for s, t in situations.items()}
        print(f"revenus de {annee} : {compte}")
    print(f"{SORTIE.relative_to(RACINE_DEPOT)} écrit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
