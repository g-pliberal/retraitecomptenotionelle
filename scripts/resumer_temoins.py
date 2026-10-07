#!/usr/bin/env python3
"""Ce que les témoins ont bougé depuis une révision, scénario par scénario.

    python scripts/resumer_temoins.py                     # depuis HEAD : le travail en cours
    python scripts/resumer_temoins.py --depuis origin/main
    python scripts/resumer_temoins.py --depuis HEAD~1 --extremes 3

POURQUOI
--------
Un changement de résultats se fait dans un commit à part, avec le diff de ses
témoins (``docs/architecture.md``, § 12). Ce diff fait des dizaines de milliers
de lignes, que personne ne lit : chaque session réécrivait à la main le même
résumé — combien de témoins bougent, de combien en médiane, lesquels le plus —
pour son message de commit et sa feuille de route, et l'action 132 l'a réécrit
quatre fois. Ce script l'imprime au format de la prose du dépôt, pour qu'il se
colle tel quel.

CE QU'IL COMPARE
----------------
La pension annuelle de chaque scénario, témoin par témoin, dans
``tests/temoins/simulations.json`` : celle de la révision, que git lit, contre
celle du répertoire de travail. Une pension bouge quand elle change de plus
d'un milliardième, ce qui écarte le bruit d'un arrondi flottant ; un témoin
bouge quand n'importe lequel de ses chiffres change. Les extrêmes nomment leur
témoin. Les rendus de page (``tests/temoins/pages.json``) ne sont que comptés,
page par page.
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
SIMULATIONS = "tests/temoins/simulations.json"
PAGES = "tests/temoins/pages.json"

sys.path.insert(0, str(RACINE / "src"))
from retraite_notionnelle.somme import somme_ordonnee
from retraite_notionnelle.cout import SCENARIOS  # noqa: E402

#: En deçà, une pension ne bouge pas : c'est le bruit d'un calcul flottant.
SEUIL = 1e-9


@dataclass
class Mouvement:
    """Ce qu'un scénario a bougé, sur les témoins qui le portent des deux côtés."""

    scenario: str
    numero: int
    #: Les témoins qui portent ce scénario des deux côtés.
    compares: int = 0
    #: L'écart relatif de chaque témoin qui bouge, par son nom.
    ecarts: dict[str, float] = field(default_factory=dict)

    @property
    def bougent(self) -> int:
        return len(self.ecarts)

    @property
    def mediane(self) -> float:
        return statistics.median(self.ecarts.values()) if self.ecarts else 0.0

    @property
    def hausses(self) -> int:
        return somme_ordonnee(1 for e in self.ecarts.values() if e > 0)

    @property
    def fortes_baisses(self) -> int:
        """Les baisses de plus de 1 %."""
        return somme_ordonnee(1 for e in self.ecarts.values() if e < -0.01)

    def extremes(self, n: int) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
        """Les ``n`` plus fortes baisses et les ``n`` plus fortes hausses."""
        tries = sorted(self.ecarts.items(), key=lambda paire: (paire[1], paire[0]))
        return tries[:n], list(reversed(tries[-n:]))


@dataclass
class Resume:
    temoins: int
    bougent: int
    nouveaux: list[str]
    disparus: list[str]
    mouvements: list[Mouvement]
    pages: int = 0
    pages_changees: list[str] = field(default_factory=list)


def _pension(temoin: dict, scenario: str) -> float | None:
    return (((temoin.get("resultat") or {}).get("scenarios") or {})
            .get(scenario) or {}).get("pension_annuelle")


def resumer(avant: dict, apres: dict, pages_avant: dict | None = None,
            pages_apres: dict | None = None) -> Resume:
    """Ce qui a bougé d'``avant`` à ``apres``, deux contenus de simulations.json."""
    communs = [nom for nom in apres if nom in avant]
    mouvements = []
    for scenario, libelle in SCENARIOS:
        mouvement = Mouvement(scenario, int(libelle.split(".")[0]))
        for nom in communs:
            pa, pb = _pension(avant[nom], scenario), _pension(apres[nom], scenario)
            if pa is None or pb is None:
                continue
            mouvement.compares += 1
            if pa == pb:
                continue
            ecart = pb / pa - 1.0 if pa else (0.0 if pb == 0 else float("inf"))
            if abs(ecart) > SEUIL:
                mouvement.ecarts[nom] = ecart
        mouvements.append(mouvement)
    pages_avant, pages_apres = pages_avant or {}, pages_apres or {}
    return Resume(
        temoins=len(apres),
        bougent=somme_ordonnee(1 for nom in communs if avant[nom] != apres[nom]),
        nouveaux=sorted(set(apres) - set(avant)),
        disparus=sorted(set(avant) - set(apres)),
        mouvements=mouvements,
        pages=len(pages_apres),
        pages_changees=sorted(nom for nom in pages_apres
                              if nom not in pages_avant
                              or _rendu(pages_avant[nom]) != _rendu(pages_apres[nom])),
    )


def _rendu(page: dict) -> dict:
    """La page, son HTML recousu : le témoin le garde en morceaux depuis le
    7 octobre 2026 (``retraite_notionnelle.lignes``), une révision plus
    ancienne en une chaîne, et ce changement de forme ne change aucune page.
    ``"".join`` rend une chaîne telle quelle."""
    return {**page, "corps": "".join(page.get("corps", ""))}


def pourcent(ecart: float) -> str:
    """« +0,24 % », « −2,65 % » : la typographie de la prose du dépôt."""
    texte = f"{abs(ecart) * 100:.2f}".replace(".", ",")
    return ("+" if ecart >= 0 else "−") + texte + " %"


def _nombre(n: int, singulier: str, pluriel: str) -> str:
    return f"{n} {singulier if n <= 1 else pluriel}"


#: Les rendus de page nommés, au plus : les autres sont comptés.
PAGES_NOMMEES = 8


def ecrire(resume: Resume, depuis: str, extremes: int = 1) -> str:
    """Le résumé, en français, prêt pour un message de commit."""
    lignes = []
    ajouts = []
    if resume.nouveaux:
        ajouts.append(_nombre(len(resume.nouveaux), "nouveau", "nouveaux"))
    if resume.disparus:
        ajouts.append(_nombre(len(resume.disparus), "disparu", "disparus"))
    suite = f" ; {', '.join(ajouts)}" if ajouts else ""
    if resume.bougent:
        lignes.append(f"{resume.temoins} témoins de simulation, dont {resume.bougent} "
                      f"bougent depuis {depuis}{suite}.")
    else:
        lignes.append(f"{resume.temoins} témoins de simulation, aucun ne bouge "
                      f"depuis {depuis}{suite}.")
    for m in resume.mouvements:
        if not m.compares:
            continue
        if not m.bougent:
            if resume.bougent:
                lignes.append(f"- scénario {m.numero} : aucune pension ne bouge, "
                              f"sur {m.compares}.")
            continue
        baisses, hausses = m.extremes(extremes)
        bas = ", ".join(f"{pourcent(e)} ({nom})" for nom, e in baisses)
        haut = ", ".join(f"{pourcent(e)} ({nom})" for nom, e in hausses)
        fortes = (f"{_nombre(m.fortes_baisses, 'baisse', 'baisses')} de plus de 1 %"
                  if m.fortes_baisses else "aucune baisse de plus de 1 %")
        lignes.append(
            f"- scénario {m.numero} : {m.bougent} sur {m.compares} bougent, "
            f"{pourcent(m.mediane)} en médiane ; de {bas} à {haut} ; "
            f"{_nombre(m.hausses, 'hausse', 'hausses')}, {fortes}.")
    if resume.pages:
        changees = resume.pages_changees
        nommees = ", ".join(changees[:PAGES_NOMMEES])
        reste = len(changees) - PAGES_NOMMEES
        if not changees:
            lignes.append(f"{resume.pages} rendus de page, aucun ne change.")
        else:
            lignes.append(
                f"{resume.pages} rendus de page, dont {len(changees)} changent : "
                f"{nommees}" + (f", et {reste} autres." if reste > 0 else "."))
    return "\n".join(lignes)


def _lire_revision(revision: str, chemin: str) -> dict:
    """Le fichier tel que ``revision`` le porte ; vide s'il n'y est pas."""
    lu = subprocess.run(["git", "-C", str(RACINE), "show", f"{revision}:{chemin}"],
                        capture_output=True, check=False)
    if lu.returncode != 0:
        return {}
    return json.loads(lu.stdout.decode("utf-8"))


def _lire_ici(chemin: str) -> dict:
    fichier = RACINE / chemin
    return json.loads(fichier.read_text(encoding="utf-8")) if fichier.is_file() else {}


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--depuis", default="HEAD", metavar="REVISION",
                           help="la révision de référence (défaut : HEAD)")
    analyseur.add_argument("--extremes", type=int, default=1, metavar="N",
                           help="combien de baisses et de hausses nommer (défaut : 1)")
    arguments = analyseur.parse_args(argv)
    avant = _lire_revision(arguments.depuis, SIMULATIONS)
    if not avant:
        print(f"{SIMULATIONS} n'existe pas à {arguments.depuis}", file=sys.stderr)
        return 1
    resume = resumer(avant, _lire_ici(SIMULATIONS),
                     _lire_revision(arguments.depuis, PAGES), _lire_ici(PAGES))
    print(ecrire(resume, arguments.depuis, arguments.extremes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
