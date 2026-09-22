#!/usr/bin/env python3
"""Régénère, dans ``docs/regimes.md``, ce qui se déduit de l'inventaire.

Le fichier qui fait foi est ``data/reference/regimes/inventaire.yaml`` ; le
document en est la lecture commentée. Ses tableaux — un par section de
l'inventaire, dans l'ordre du fichier — et sa phrase de compte étaient
recopiés à la main, et ils ont vieilli : ils disaient encore « à modéliser »
de vingt lignes que quatre tranches de travail avaient depuis portées. Ce
script les réécrit entre deux repères, et un test refuse un document qui ne
serait plus celui que le script produit.

    python scripts/construire_regimes_md.py             # réécrit
    python scripts/construire_regimes_md.py --verifier  # échoue s'il est périmé
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle.config import RACINE_DONNEES  # noqa: E402
from retraite_notionnelle.donnees.regimes import charger_inventaire  # noqa: E402

DOCUMENT = RACINE / "docs" / "regimes.md"
INVENTAIRE = RACINE_DONNEES / "reference" / "regimes" / "inventaire.yaml"

COUVERTURES = {
    "modelise": "✅ modélisé",
    "partiel": "◐ partiel",
    "a_modeliser": "✚ à modéliser",
    "routage": "↪ portée par un statut",
    "hors_champ": "⊘ hors champ",
}

FAMILLES = {
    "base_prive": "base, privé",
    "complementaire_prive": "complémentaire, privé",
    "fonction_publique": "fonction publique",
    "special": "spécial",
    "non_salarie": "non-salariés",
    "agricole": "agricole",
    "liberal": "libéral",
    "additionnel_capitalise": "additionnel, capitalisé",
}

#: Les sections de l'inventaire sont ses bannières de commentaire : un titre
#: entre deux lignes de tirets. Le document les suit dans le même ordre.
_BANNIERE = re.compile(r"^  # -{10,}\n  # (?P<titre>.+)\n  # -{10,}$", re.M)
_CODE = re.compile(r"^  - code: (?P<code>\S+)$", re.M)


def sections() -> list[tuple[str, list[str]]]:
    """Les sections du fichier YAML, et les codes de chacune dans l'ordre."""
    texte = INVENTAIRE.read_text(encoding="utf-8")
    bornes = [(m.start(), m.group("titre")) for m in _BANNIERE.finditer(texte)]
    resultat: list[tuple[str, list[str]]] = []
    for rang, (debut, titre) in enumerate(bornes):
        fin = bornes[rang + 1][0] if rang + 1 < len(bornes) else len(texte)
        codes = [m.group("code") for m in _CODE.finditer(texte[debut:fin])]
        resultat.append((titre, codes))
    return resultat


def periode(ligne) -> str:
    if ligne.creation is None:
        return "—"
    if ligne.extinction is not None:
        return f"{ligne.creation}-{ligne.extinction}"
    if ligne.fermeture is not None:
        return f"depuis {ligne.creation}, fermé en {ligne.fermeture}"
    return f"depuis {ligne.creation}"


def _cellule(texte: str) -> str:
    return " ".join(texte.split()).replace("|", "\\|")


def compte(lignes) -> str:
    nombres = {cle: sum(1 for l in lignes if l.couverture == cle) for cle in COUVERTURES}
    reste = (f"{nombres['a_modeliser']} à modéliser" if nombres["a_modeliser"]
             else "et plus aucune ligne à modéliser")
    return (
        f"L'inventaire compte **{len(lignes)} lignes** : {nombres['modelise']} régimes "
        f"modélisés,\n{nombres['partiel']} calculés mais incomplets, "
        f"{nombres['routage']} affiliations portées par un statut,\n"
        f"{nombres['hors_champ']} hors champ — {reste}."
    )


def tableaux(lignes) -> str:
    par_code = {ligne.code: ligne for ligne in lignes}
    blocs = []
    for titre, codes in sections():
        rangs = [
            "| Régime | Famille | Période | Couverture | Statuts | Ce qui manque, ou pourquoi |",
            "|---|---|---|---|---|---|",
        ]
        for code in codes:
            ligne = par_code[code]
            nom = f"{ligne.nom} (`{ligne.code}`)" if ligne.au_catalogue else ligne.nom
            statuts = ", ".join(f"`{s}`" for s in ligne.statuts) if ligne.statuts else "—"
            raison = ligne.raison_hors_champ if ligne.couverture == "hors_champ" else ligne.manque
            rangs.append(
                f"| {_cellule(nom)} | {FAMILLES[ligne.famille]} | {periode(ligne)} | "
                f"{COUVERTURES[ligne.couverture]} | {statuts} | {_cellule(raison)} |"
            )
        blocs.append(f"## {titre}\n\n" + "\n".join(rangs) + "\n")
    return "\n".join(blocs)


def remplacer(texte: str, repere: str, contenu: str) -> str:
    debut, fin = f"<!-- {repere}:debut -->", f"<!-- {repere}:fin -->"
    if debut not in texte or fin not in texte:
        raise SystemExit(f"{DOCUMENT} : repères {debut} / {fin} introuvables")
    avant, reste = texte.split(debut, 1)
    _, apres = reste.split(fin, 1)
    return f"{avant}{debut}\n{contenu}\n{fin}{apres}"


def produire() -> str:
    lignes = charger_inventaire(RACINE_DONNEES)
    texte = DOCUMENT.read_text(encoding="utf-8")
    texte = remplacer(texte, "compte", compte(lignes))
    return remplacer(texte, "tableaux", tableaux(lignes))


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="ne rien écrire ; échouer si le document est périmé")
    arguments = analyseur.parse_args()
    nouveau = produire()
    if arguments.verifier:
        if nouveau != DOCUMENT.read_text(encoding="utf-8"):
            print(f"{DOCUMENT.relative_to(RACINE)} est périmé : lancer "
                  "python scripts/construire_regimes_md.py", file=sys.stderr)
            return 1
        print(f"{DOCUMENT.relative_to(RACINE)} est à jour")
        return 0
    DOCUMENT.write_text(nouveau, encoding="utf-8", newline="\n")
    print(f"{DOCUMENT.relative_to(RACINE)} réécrit")
    return 0


if __name__ == "__main__":
    sys.exit(main())
