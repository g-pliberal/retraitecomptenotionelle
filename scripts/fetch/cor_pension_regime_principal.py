#!/usr/bin/env python3
"""La pension moyenne de droit direct par régime principal, fin 2024, du modèle Ancetre de la DREES.

    python scripts/fetch/cor_pension_regime_principal.py
    python scripts/fetch/cor_pension_regime_principal.py --fichier Données_RA2026_P3.xlsx

POURQUOI CE TÉMOIN. La page Coût pèse des effectifs de caisse, non des
personnes (limite n° 1 de ``cout.py``), et ses cas types n'avaient aucun
contrôle de leur niveau de pension. Ancetre, la microsimulation statique de la
DREES, calée sur l'EACR, décrit des personnes : elle donne la pension brute
moyenne de droit direct de chaque retraité, tous régimes, selon celui où il a
fait plus de la moitié de sa carrière, et la même pour les seules carrières
complètes. ``retraite_notionnelle.controle_ancetre`` lui confronte les cas
types de la grille, en 2024 (action 138, étape 3).

LA SOURCE. Le classeur de la partie 3 du rapport annuel du COR de juin 2026,
feuille « Tab 3.2 » (p. 161 du rapport) : « Sources : Drees, EACR, modèle
Ancètre ». Son titre dit « fin 2023 », son champ « retraités ayant perçu un
droit direct au cours de l'année 2024 […] vivants au 31 décembre 2024 » : le
champ fait foi, le titre est celui du rapport de 2025, comme celui du tableau
2.11 du même rapport (``cor_leviers.py``). Les montants sont arrondis à la
dizaine d'euros, majoration pour trois enfants comprise, hors versement
forfaitaire unique.

Le témoin est versionné : les tests le relisent sans réseau. ``--fichier``
lit le classeur déjà téléchargé.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lecture_xlsx import feuilles  # noqa: E402

RACINE = Path(__file__).resolve().parents[2]
URL = ("https://www.cor-retraites.fr/sites/default/files/2026-06/"
       "Donn%C3%A9es_RA2026_P3.xlsx")
SORTIE = RACINE / "tests" / "temoins" / "cor_pension_regime_principal_2026.json"
ENTETES = {"User-Agent": "retraite-notionnelle/0.1 (recherche publique)"}
FEUILLE = "Tab 3.2"

#: Les lignes du tableau, reconnues au début de leur libellé, sans accents ni
#: casse, renvois numérotés ôtés.
LIGNES: tuple[tuple[str, str], ...] = (
    ("ensemble", "ensemble des retraites de droit direct"),
    ("regime_de_base", "retraites de droit direct d'un regime de base"),
    ("regime_general", "dont regime general a titre principal"),
    ("autre_salarie", "dont autre regime de salarie"),
    ("fpe_civils", "fpe civils"),
    ("fpe_militaires", "fpe militaires"),
    ("cnracl", "cnracl"),
    ("msa_salaries", "msa salaries"),
    ("regimes_speciaux", "regimes speciaux"),
    ("autre_non_salarie", "dont autre regime de non-salaries"),
    ("msa_non_salaries", "msa non-salaries"),
    ("professions_liberales", "professions liberales"),
    ("aucun_principal", "dont aucun regime principal"),
    ("monopensionnes", "monopensionnes"),
    ("polypensionnes", "polypensionnes"),
)

#: Les six colonnes : tous les retraités de droit direct, puis ceux à carrière
#: complète, chacun en ensemble, femmes, hommes.
COLONNES: tuple[tuple[str, str], ...] = tuple(
    (champ, sexe) for champ in ("tous", "carriere_complete")
    for sexe in ("ensemble", "femmes", "hommes"))


def _texte(valeur) -> str:
    texte = unicodedata.normalize("NFD", str(valeur))
    texte = "".join(c for c in texte if unicodedata.category(c) != "Mn")
    return re.sub(r"[\d,\s]+$", "", texte.lower().replace("’", "'")).strip()


def lire_tableau(grille: dict) -> dict[str, dict[str, dict[str, float]]]:
    """Chaque ligne : ses six montants mensuels, par champ et par sexe. Les
    montants sont, de gauche à droite, dans l'ordre de :data:`COLONNES`."""
    lignes: dict[int, dict[int, object]] = {}
    for (ligne, colonne), valeur in grille.items():
        lignes.setdefault(ligne, {})[colonne] = valeur
    resultat: dict[str, dict[str, dict[str, float]]] = {}
    for cellules in lignes.values():
        libelles = [_texte(v) for _, v in sorted(cellules.items()) if isinstance(v, str)]
        nombres = [v for _, v in sorted(cellules.items()) if isinstance(v, float)]
        if len(libelles) != 1 or len(nombres) != len(COLONNES):
            continue
        for cle, debut in LIGNES:
            if libelles[0].startswith(debut) and cle not in resultat:
                resultat[cle] = {}
                for (champ, sexe), montant in zip(COLONNES, nombres):
                    resultat[cle].setdefault(champ, {})[sexe] = montant
                break
    manquantes = [cle for cle, _ in LIGNES if cle not in resultat]
    if manquantes:
        raise ValueError(f"tableau 3.2 : lignes introuvables {manquantes}")
    return resultat


def lire_champ(grille: dict) -> str:
    """La note de champ du tableau, qui en dit l'année."""
    for valeur in grille.values():
        if isinstance(valeur, str) and _texte(valeur).startswith("champ"):
            return " ".join(valeur.replace("\xa0", " ").split())
    raise ValueError("tableau 3.2 : note de champ introuvable")


def controler(temoin: dict) -> list[str]:
    """Ce que le rapport imprime : les montants que le registre cite, et
    l'année du champ."""
    pensions = temoin["pensions"]
    attendus = (
        (pensions["ensemble"]["tous"]["ensemble"], 1750.0),
        (pensions["regime_general"]["tous"]["ensemble"], 1610.0),
        (pensions["fpe_civils"]["tous"]["ensemble"], 2570.0),
        (pensions["ensemble"]["carriere_complete"]["ensemble"], 2100.0),
    )
    ecarts = [f"{lu} au lieu de {imprime}" for lu, imprime in attendus if lu != imprime]
    if "2024" not in temoin["champ"]:
        ecarts.append(f"champ sans 2024 : {temoin['champ']}")
    return ecarts


def _classeur(fichier: Path | None) -> bytes:
    if fichier is not None:
        return fichier.read_bytes()
    requete = urllib.request.Request(URL, headers=ENTETES)
    with urllib.request.urlopen(requete, timeout=120) as reponse:
        return reponse.read()


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--fichier", type=Path, help="le classeur déjà téléchargé")
    arguments = analyseur.parse_args(argv)

    grille = feuilles(_classeur(arguments.fichier), (FEUILLE,))[FEUILLE]
    temoin = {
        "source": {
            "editeur": "Conseil d'orientation des retraites",
            "producteur": "DREES, EACR et modèle Ancetre",
            "reference": ("Rapport annuel de juin 2026, tableau 3.2, p. 161 "
                          "(Données_RA2026_P3.xlsx, feuille « Tab 3.2 »)"),
            "url": URL,
            "lu_le": date.today().isoformat(),
        },
        "annee": 2024,
        "champ": lire_champ(grille),
        "unite": "euros bruts par mois, droit direct, majoration pour trois enfants comprise",
        "pensions": lire_tableau(grille),
    }
    ecarts = controler(temoin)
    if ecarts:
        print("Le classeur ne redonne pas le rapport : " + " ; ".join(ecarts), file=sys.stderr)
        return 1
    SORTIE.write_text(json.dumps(temoin, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                      encoding="utf-8")
    print(f"{SORTIE.relative_to(RACINE)} écrit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
