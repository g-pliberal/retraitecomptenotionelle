#!/usr/bin/env python3
"""Frais des PER individuels, lus dans le rapport annuel de l'OPEF lui-même.

    pip install pypdf
    python scripts/fetch/opef_frais_per.py                # lit data/brut/OPEF2026.pdf
    python scripts/fetch/opef_frais_per.py --confronter   # et compare au fichier de référence
    python scripts/fetch/opef_frais_per.py --fichier ~/Téléchargements/OPEF2026.pdf

À QUOI ÇA SERT. Les trois frais du pilier capitalisé — sur versement, sur
encours, sur arrérages — sont dans ``data/reference/macro/frais_epargne_retraite.yaml``,
saisis depuis la reprise du rapport par la presse, parce que le serveur de la
Banque de France refuse ses PDF à tout ce qui n'est pas un navigateur. Ce
script lit le tableau « Frais liés aux PER individuels » dans le document du
producteur, et dit si la saisie lui est conforme. C'est la confrontation que
le manifeste demandait « dès qu'une session peut l'ouvrir ».

CE QU'IL LIT. Le rapport présente trois tableaux de même forme, un par
produit assurantiel : assurance-vie (T5), contrat de capitalisation (T6),
PER individuel (T7). Chacun porte, pour deux exercices, les frais sur
versements et les frais de gestion par support, et une ligne « frais sur
arrérages de rente » assortie d'une note qui dit combien d'organismes les
facturent. Les trois sont lus : les deux premiers sont les points de
comparaison que le fichier de référence cite, le troisième est la source.

CE QUE LE DOCUMENT DIT ET QUE LA PRESSE NE DISAIT PAS. La moyenne des frais
sur arrérages est « non pondérée » et « ne tient compte que » des organismes
qui facturent effectivement ces frais — 9 sur 20 pour le PER individuel en
2025. Les onze autres ne prélèvent rien sur la rente. La valeur du fichier de
référence est donc la moyenne de ceux qui facturent, pas celle du marché. Le
script imprime les deux effectifs et en déduit ce que le rapport ne dit pas :
la moyenne non pondérée sur tous les déclarants (la publiée, multipliée par la
part des facturants) et la médiane, nulle dès que les facturants sont moins de
la moitié — 0,99 % et zéro pour le PER individuel en 2025.

Le document se lit avec ``pypdf``, comme celui de l'ERAFP : le lecteur du
dépôt (``lecture_pdf.py``) ne rend pas les polices CFF de ce rapport.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from source_locale import (  # noqa: E402
    RACINE,
    jeux_bloques,
    lire_ou_telecharger,
    option_fichier,
)

IDENTIFIANT = "opef_rapport_annuel"
SORTIE = RACINE / "data" / "brut" / "opef_frais_per.json"
REFERENCE = RACINE / "data" / "reference" / "macro" / "frais_epargne_retraite.yaml"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}

#: Les trois tableaux, reconnus par leur titre. Le numéro (T5, T6, T7) change
#: d'une édition à l'autre ; le libellé du produit, non.
TABLEAUX = {
    "assurance_vie": r"Frais liés aux contrats d[’']assurance-vie",
    "capitalisation": r"Frais liés aux contrats de capitalisation",
    "per_individuel": r"Frais liés aux PER individuels",
}

ANNEES = re.compile(r"Frais (20\d\d) Frais (20\d\d)")
NOMBRE = r"(\d+,\d+)"
FONDS_EUROS = re.compile(r"Support fonds en euros\s+" + NOMBRE + r"\s+" + NOMBRE)
ARRERAGES = re.compile(r"en % du montant de chaque rente\s+" + NOMBRE + r"\s+" + NOMBRE)
DECLARANTS = re.compile(r"Sur les (\d+) organismes déclarants, (\d+) ont reporté")

#: Écart toléré entre la saisie et la lecture : le document donne deux
#: décimales en pour cent, la référence quatre en fraction ; rien à tolérer
#: au-delà de l'arrondi d'écriture.
TOLERANCE = 5e-6


def telecharger(url: str) -> bytes:
    requete = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=180) as reponse:
        return reponse.read()


def texte_du_pdf(pdf: bytes) -> str:
    import io

    from pypdf import PdfReader

    return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(pdf)).pages)


def _fraction(texte: str) -> float:
    return round(float(texte.replace(",", ".")) / 100.0, 6)


def lire_tableau(texte: str, titre: str) -> dict:
    """Le tableau dont le titre contient ``titre``, en fractions par exercice.

    La fenêtre lue va du titre à la mention « Source : », qui clôt chaque
    tableau du rapport. Dans cette fenêtre, la ligne « Support fonds en
    euros » apparaît deux fois : d'abord sous les frais ponctuels (sur
    versements), puis sous les frais récurrents (de gestion). C'est l'ordre
    du tableau qui dit laquelle est laquelle, et il est vérifié : les
    intitulés des deux blocs doivent se suivre dans cet ordre.
    """
    debut = re.search(titre, texte)
    if debut is None:
        raise LookupError(f"tableau introuvable : {titre}")
    fin = texte.find("Source :", debut.end())
    if fin < 0:
        raise LookupError(f"tableau sans mention de source : {titre}")
    bloc = texte[debut.start():fin]

    annees = ANNEES.search(bloc)
    if annees is None:
        raise LookupError(f"tableau sans en-tête d'exercices : {titre}")
    ponctuels = bloc.find("Frais ponctuels")
    recurrents = bloc.find("Frais récurrents")
    if not 0 <= ponctuels < recurrents:
        raise LookupError(f"les blocs ponctuels et récurrents ne se suivent pas : {titre}")

    euros = FONDS_EUROS.findall(bloc)
    if len(euros) != 2:
        raise LookupError(f"{len(euros)} lignes « fonds en euros » au lieu de 2 : {titre}")
    arrerages = ARRERAGES.search(bloc)
    if arrerages is None:
        raise LookupError(f"ligne des arrérages introuvable : {titre}")
    declarants = DECLARANTS.search(bloc)

    par_annee = {}
    for rang, annee in enumerate(annees.groups()):
        par_annee[int(annee)] = {
            "versement": _fraction(euros[0][rang]),
            "gestion": _fraction(euros[1][rang]),
            "arrerages": _fraction(arrerages.group(rang + 1)),
        }
    n_declarants = int(declarants.group(1)) if declarants else None
    n_facturant = int(declarants.group(2)) if declarants else None
    # La moyenne publiée ne porte que sur ceux qui facturent. Sur TOUS les
    # déclarants, les autres prélevant zéro, la moyenne non pondérée est la
    # publiée multipliée par la part des facturants ; la médiane est nulle dès
    # que les facturants sont moins de la moitié, et n'est pas déterminable
    # autrement, le rapport ne donnant pas la distribution.
    tous_declarants = None
    mediane = None
    if n_declarants:
        tous_declarants = {
            annee: round(frais["arrerages"] * n_facturant / n_declarants, 6)
            for annee, frais in par_annee.items()
        }
        mediane = 0.0 if 2 * n_facturant < n_declarants else None
    return {
        "exercices": par_annee,
        "arrerages_organismes_declarants": n_declarants,
        "arrerages_organismes_facturant": n_facturant,
        "arrerages_moyenne_tous_declarants": tous_declarants,
        "arrerages_mediane_declarants": mediane,
    }


def lire(octets: bytes) -> dict:
    texte = texte_du_pdf(octets).replace("’", "'")
    return {cle: lire_tableau(texte, titre) for cle, titre in TABLEAUX.items()}


def confronter(tables: dict, reference: Path = REFERENCE) -> list[str]:
    """Les écarts entre la saisie et le document, poste par poste ; vide si aucun."""
    import yaml

    fiche = yaml.safe_load(reference.read_text(encoding="utf-8"))
    annee = int(fiche["annee_reference"])
    exercices = tables["per_individuel"]["exercices"]
    if annee not in exercices:
        return [f"l'exercice {annee} du fichier de référence n'est pas dans le document "
                f"({', '.join(map(str, exercices))})"]
    ecarts = []
    for poste, lu in exercices[annee].items():
        saisi = float(fiche["frais"][poste]["valeur"])
        if abs(saisi - lu) > TOLERANCE:
            ecarts.append(f"{poste} : référence {saisi:.4%}, document {lu:.4%}")
    return ecarts


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    option_fichier(analyseur)
    analyseur.add_argument("--confronter", action="store_true",
                           help="compare les trois frais du PER individuel à "
                                "frais_epargne_retraite.yaml")
    options = analyseur.parse_args(argv)
    jeu = next((j for j in jeux_bloques() if j["id"] == IDENTIFIANT), None)
    if jeu is None:
        print(f"{IDENTIFIANT} absent de data/sources.yaml, ou plus déclaré bloqué",
              file=sys.stderr)
        return 1
    try:
        octets = lire_ou_telecharger(jeu.get("document", jeu["url"]), telecharger,
                                     options.fichier, nom_local=jeu.get("fichier_local"),
                                     miroir=jeu.get("miroir"), sha256=jeu.get("sha256"))
    except (OSError, ValueError) as erreur:
        print(f"échec de la lecture du document : {erreur}", file=sys.stderr)
        return 1
    try:
        tables = lire(octets)
    except (LookupError, ValueError) as erreur:
        print(f"rapport OPEF : {erreur} — rien n'est écrit", file=sys.stderr)
        return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps({
        "source": jeu.get("document", jeu["url"]),
        "miroir": jeu.get("miroir"),
        "sha256": jeu.get("sha256"),
        "recupere_le": date.today().isoformat(),
        "producteur": "Observatoire des produits d'épargne financière (CCSF, Banque de "
                      "France), sur les remises des assureurs à l'ACPR. C'est le "
                      "producteur de la donnée, non une transcription.",
        "tables": tables,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    per = tables["per_individuel"]
    for annee, frais in sorted(per["exercices"].items()):
        print(f"PER individuel {annee} : versement {frais['versement']:.2%}, "
              f"gestion {frais['gestion']:.2%}, arrérages {frais['arrerages']:.2%}")
    if per["arrerages_organismes_declarants"]:
        derniere = max(per["exercices"])
        print(f"arrérages : moyenne non pondérée sur {per['arrerages_organismes_facturant']} "
              f"organismes qui facturent, sur {per['arrerages_organismes_declarants']} déclarants ; "
              f"sur tous les déclarants, {per['arrerages_moyenne_tous_declarants'][derniere]:.2%} "
              f"en moyenne, médiane "
              + ("nulle" if per["arrerages_mediane_declarants"] == 0.0 else "non déterminable"))
    print(f"{SORTIE.relative_to(RACINE)} : {len(tables)} tableaux lus")

    if options.confronter:
        ecarts = confronter(tables)
        if ecarts:
            for ligne in ecarts:
                print(f"  ÉCART   {ligne}")
            return 1
        print("confrontation : les trois frais du fichier de référence sont ceux du document")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
