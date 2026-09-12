#!/usr/bin/env python3
"""Récupération de la valeur du point des professions libérales, chez la CNAVPL.

    python scripts/fetch/cnavpl_recueils.py

Aucune base ne porte cette valeur, et ce n'est pas faute d'avoir cherché : deux
dépouillements de la législation consolidée et deux du *Journal officiel* — 34
gigaoctets au total — n'en trouvent aucune trace. L'explication tient à la
mécanique du régime : le décret annuel fixe un **coefficient de revalorisation**,
pas un montant, et la valeur qui en résulte n'est publiée que par la caisse.

Elle l'est dans son **recueil statistique**, un annuaire d'une soixantaine de
pages paru chaque année, sous une phrase invariable :

    « La valeur du point est fixée à 0,6540 au 1er janvier 2025. »

Le même recueil donne la règle d'acquisition, qui est ce dont un modèle en
points a besoin pour convertir une cotisation en droits :

* la cotisation est proportionnelle au revenu, sur deux tranches — T1 de 0 à un
  plafond de la Sécurité sociale, T2 de 0 à cinq plafonds ;
* le taux de T1 et celui de T2 sont donnés en toutes lettres ;
* **525 points** au maximum sur T1, **25** sur T2 — et 557 sur T1 depuis 2025,
  le taux passant alors à 8,73 %.

Les taux ne sont PAS lus dans la phrase de l'historique, et c'est une correction
importante : cette phrase — « le taux de la première tranche est de 8,23 % » —
décrit la réforme de 2015, non l'année du recueil. La lire donnait 8,23 % pour
2025, alors que le recueil de cette année-là appelle 8,73 %. Les taux et les
points sont donc lus dans le TABLEAU DES COTISATIONS, qui les donne année par
année, sur trois exercices par recueil. Sa mise en page passait pour illisible ;
elle ne l'est pas : les polices qui portent les montants n'exposent pas de table
`ToUnicode`, mais les taux et les nombres de points, eux, se relisent. Les cinq
recueils se recouvrent sur quinze lectures et concordent toutes.

Le prix d'achat d'un point de T1 s'en déduit — taux × plafond ÷ 525 — mais ce
calcul appartient au moteur, pas au récupérateur : on ne verse ici que ce que la
caisse écrit.

Les recueils antérieurs à 2021 emploient une autre mise en page, où la valeur
n'est plus dans une phrase mais dans un graphique. La série commence donc en
2021.
"""

from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_pdf import _flux, _hexa, _litteral, _objets, _polices, JETONS  # noqa: E402

RACINE = "https://www.cnavpl.fr/documents"

#: Les recueils statistiques mis en ligne, avec l'identifiant de téléchargement
#: que le gestionnaire de documents du site attribue à chacun.
RECUEILS = {
    2021: "recueil-statistique-2021/?wpdmdl=263987",
    2022: "recueil-statistique-2022/?wpdmdl=300287",
    2023: "recueil-statistique-2023/?wpdmdl=300881",
    2024: "recueil-statistique-2024/?wpdmdl=301244",
    2025: "recueil-statistique-2025/?wpdmdl=301471",
}

# Les accents disparaissent dans certains millésimes, où la police n'expose pas
# de table ToUnicode complète : les motifs les rendent facultatifs.
VALEUR = re.compile(r"valeurdupointestfix[ée]{0,2}e?à?(\d+[,.]\d+)")
#: Une ligne du tableau des cotisations, pour un exercice. Le texte est collé et
#: entrelardé des caractères que les polices sans table `ToUnicode` rendent
#: illisibles : les séparateurs sont donc tolérants. Les deux nombres de points
#: y sont collés l'un à l'autre — « 557557 », le maximum au plafond et celui à
#: cinq plafonds, qui sont égaux puisque T1 s'arrête au plafond.
TABLEAU = re.compile(
    r"Tauxdecotisation(?P<annee>\d{4})"
    r".*?PASS:(?P<t1>\d+[,.]\d+)%"
    r".*?(?P<points>\d{3})(?P=points)0.{0,6}?5PASS:(?P<t2>\d+[,.]\d+)%",
    re.S,
)
SORTIE = Path("data/brut/cnavpl_recueils.json")


def texte_colle(octets: bytes) -> str:
    """Tout le texte du document, espaces ôtés.

    Le recueil est un annuaire mis en pages sur plusieurs colonnes, avec des
    graphiques : reconstituer ses lignes n'a pas de sens. Seules comptent ici
    deux phrases, qu'on retrouve en collant le texte et en cherchant dedans.
    """
    tables = _polices(octets)
    morceaux: list[str] = []
    for objet in _objets(octets).values():
        contenu = _flux(objet)
        if not contenu or (b"Tj" not in contenu and b"TJ" not in contenu):
            continue
        police = None
        for jeton in JETONS.finditer(contenu):
            if jeton.group("tf"):
                police = jeton.group(9)
            elif jeton.group("hex"):
                morceaux.append(_hexa(jeton.group("hex"), tables.get(police)))
            elif jeton.group("txt"):
                morceaux.append(_litteral(jeton.group("txt")[1:-1]))
    return re.sub(r"\s+", "", "".join(morceaux))


def _nombre(texte: str) -> float:
    return float(texte.replace(",", "."))


def lignes_du_tableau(texte: str) -> dict[int, tuple[float, float, int]]:
    """Taux des deux tranches et points de T1, exercice par exercice.

    Le tableau des cotisations en porte trois par recueil — l'exercice écoulé,
    celui en cours et le suivant. Les recueils se recouvrent donc, et ce
    recouvrement est le contrôle : une lecture qui se contredirait d'un millésime
    à l'autre arrêterait le script.
    """
    lu: dict[int, tuple[float, float, int]] = {}
    for morceau in texte.split("Tauxdecotisation")[1:]:
        trouve = TABLEAU.search("Tauxdecotisation" + morceau)
        if trouve is None:
            continue
        lu[int(trouve.group("annee"))] = (
            _nombre(trouve.group("t1")) / 100,
            _nombre(trouve.group("t2")) / 100,
            int(trouve.group("points")),
        )
    return lu


def main() -> int:
    serie: dict[str, float] = {}
    valeurs: dict[int, float] = {}
    #: Taux et points lus, avec le recueil qui les a donnés : deux recueils qui
    #: se contrediraient sur un même exercice arrêtent le script.
    tranches: dict[int, tuple[tuple[float, float, int], int]] = {}
    for annee, chemin in sorted(RECUEILS.items()):
        url = f"{RACINE}/{chemin}"
        try:
            demande = urllib.request.Request(
                url, headers={"User-Agent": "retraite-notionnelle/0.1"}
            )
            with urllib.request.urlopen(demande, timeout=300) as reponse:
                octets = reponse.read()
        except (urllib.error.HTTPError, urllib.error.URLError) as erreur:
            print(f"ÉCHEC   recueil {annee} : {erreur}", file=sys.stderr)
            return 1

        texte = texte_colle(octets)
        point = VALEUR.search(texte)
        if not point:
            print(f"IGNORÉ  recueil {annee} : la phrase attendue est absente")
            continue
        valeurs[annee] = _nombre(point.group(1))
        serie[f"cnavpl|{annee}|valeur_service"] = valeurs[annee]
        for exercice, lecture in sorted(lignes_du_tableau(texte).items()):
            precedent = tranches.get(exercice)
            if precedent is not None and precedent[0] != lecture:
                print(f"\nLectures contradictoires pour {exercice}, rien n'est "
                      f"écrit : recueil {precedent[1]} donne {precedent[0]}, "
                      f"recueil {annee} donne {lecture}", file=sys.stderr)
                return 1
            tranches[exercice] = (lecture, annee)
            serie[f"cnavpl|{exercice}|taux_t1"] = lecture[0]
            serie[f"cnavpl|{exercice}|taux_t2"] = lecture[1]
        lues = ", ".join(
            f"{e} : {t1:.2%} sur T1 ({p} points) et {t2:.2%} sur T2"
            for e, ((t1, t2, p), source) in sorted(tranches.items())
            if source == annee
        )
        print(f"OK      {annee} : valeur du point {valeurs[annee]} €"
              + (f" ; {lues}" if lues else ""))

    croissantes = sorted(valeurs)
    for precedente, courante in zip(croissantes, croissantes[1:]):
        if valeurs[courante] <= valeurs[precedente]:
            print(f"\nSérie incohérente, rien n'est écrit : la valeur du point recule "
                  f"de {precedente} ({valeurs[precedente]}) à {courante} "
                  f"({valeurs[courante]})", file=sys.stderr)
            return 1

    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(
        json.dumps({
            "source": RACINE,
            "recupere_le": date.today().isoformat(),
            "recueils": {str(a): f"{RACINE}/{c}" for a, c in sorted(RECUEILS.items())},
            "note": "régime de base des professions libérales, en points depuis "
                    "2004 ; taux lus dans le tableau des cotisations, exercice "
                    "par exercice, et non dans la phrase de l'historique, qui "
                    "décrit la réforme de 2015 et non l'année du recueil",
            "points_maximum_t1": {
                str(exercice): points
                for exercice, ((_, _, points), _) in sorted(tranches.items())
            },
            "serie": dict(sorted(serie.items())),
        }, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    print(f"\n{len(serie)} valeurs écrites dans {SORTIE}")
    print(f"Couverture {croissantes[0]}-{croissantes[-1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
