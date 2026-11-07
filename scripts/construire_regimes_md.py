#!/usr/bin/env python3
"""Régénère, dans ``docs/regimes.md``, ce qui se déduit de l'inventaire.

L'inventaire, ``data/reference/regimes/inventaire.yaml``, se fabrique depuis
les fichiers de régimes (``scripts/construire_inventaire.py``) ; le document en
est la lecture commentée. Ses tableaux — un par section de
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

from retraite_notionnelle.somme import somme_ordonnee
from retraite_notionnelle.config import RACINE_DONNEES  # noqa: E402
from retraite_notionnelle.donnees.regimes import (  # noqa: E402
    charger_gestionnaires, charger_inventaire)

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
    nombres = {cle: somme_ordonnee(1 for l in lignes if l.couverture == cle) for cle in COUVERTURES}
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


def gestionnaires(lignes) -> str:
    """Les organismes qui gèrent les régimes : ceux des régimes encore en vie —
    ni éteints, ni fondus dans un autre —, puis ceux qui ont disparu avec les
    leurs, ou les ont laissés à un autre (action 188)."""
    organismes = charger_gestionnaires(RACINE_DONNEES)
    gere: dict[str, list] = {code: [] for code in organismes}
    for ligne in lignes:
        for code in ligne.gestionnaires:
            gere[code].append(ligne)
    vivante = lambda ligne: ligne.extinction is None and ligne.integre_dans is None  # noqa: E731
    vivantes = [ligne for ligne in lignes if vivante(ligne)]
    actifs = [code for code in organismes if any(vivante(l) for l in gere[code])]
    disparus = [code for code in organismes if gere[code] and code not in actifs]
    deleguent = [code for code in actifs if organismes[code].operateur]
    operateurs = sorted({organismes[organismes[code].operateur].nom for code in deleguent})
    sans = [ligne.nom for ligne in lignes if not ligne.gestionnaires]
    compte_ = (
        f"**{len(actifs)} gestionnaires** gèrent les {len(vivantes)} lignes de "
        "l'inventaire encore en vie — ni éteintes, ni fondues dans un autre "
        f"régime ; {len(deleguent)} d'entre eux confient leur gestion à un autre "
        f"organisme ({' ; '.join(operateurs)}). {len(disparus)} gestionnaires ont "
        "disparu avec leurs régimes, ou les ont laissés à un autre. Un code peut "
        "nommer un ensemble, les caisses des deux assemblées par exemple. Aucune "
        f"source du dépôt ne nomme encore celui de {len(sans)} régimes : "
        + " ; ".join(sans) + "."
    )

    def tableau(codes, seulement_vivantes: bool) -> str:
        rangs = ["| Gestionnaire | Géré par | Régimes |", "|---|---|---|"]
        for code in codes:
            organisme = organismes[code]
            par = organismes[organisme.operateur].nom if organisme.operateur else "—"
            regimes = [l.nom for l in gere[code] if vivante(l) or not seulement_vivantes]
            rangs.append(f"| {_cellule(organisme.nom)} | {_cellule(par)} | "
                         f"{_cellule(' ; '.join(regimes))} |")
        return "\n".join(rangs)

    return (
        "## Les organismes qui les gèrent\n\n"
        "Chaque fichier de régime nomme son gestionnaire, un code du référentiel "
        "`data/reference/regimes/_gestionnaires.yaml` : l'organisme qui le gère "
        "aujourd'hui, ou le dernier qui l'a géré en propre.\n\n"
        f"{compte_}\n\n"
        "### Ceux des régimes encore en vie\n\n" + tableau(actifs, True) + "\n\n"
        "### Ceux qui ont disparu, ou laissé leurs régimes à un autre\n\n"
        + tableau(disparus, False) + "\n"
    )


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
    texte = remplacer(texte, "tableaux", tableaux(lignes))
    return remplacer(texte, "gestionnaires", gestionnaires(lignes))


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
