"""Rassemble ce que les travaux d'une course de GitHub ont laissé.

La course (`.github/workflows/tests.yml`) joue la suite en tranches, chacune
sur sa machine, et la garde des présomptions sur une autre (action 135). Le
dernier travail reçoit de chacun un dossier — `tranche-1`, `tranche-2`…,
`garde` — où il a écrit son issue et sa durée (`issue.txt` : le code de
sortie de pytest, puis les secondes), sa sortie (`suite.txt`, `garde.txt`)
et, pour une tranche, ses durées test par test (`durees.xml`). Ce script en
tire ce que `scripts/publier_fabrique.sh` attend :

    python3 scripts/rassembler_course.py <dossier> >> "$GITHUB_OUTPUT"

- `suite` : `success` si chaque tranche a rendu une issue nulle, `failure`
  sinon — une tranche qui n'a rien rendu n'a pas joué ses tests —, `skipped`
  si la fabrique a échoué ; `garde`, de même ;
- `durees` : ce que la fabrique, la suite — sa tranche la plus longue —,
  chaque tranche et la garde ont duré, en secondes ;
- `durees_suite` : le tableau des durées par fichier de tests
  (`scripts/durees_suite.py`), écrit seulement quand la course est partie sans
  mémoire des calculs et que chaque tranche a rendu les siennes ;
- `<dossier>/suite.txt` et `<dossier>/garde.txt` : les sorties, bout à bout.

Entrées, par l'environnement : TRANCHES, le nombre de tranches ; FABRICATION,
l'issue de la fabrique ; DUREE_FABRIQUE, ses secondes ; MEMOIRE, la clé de la
mémoire des calculs reprise, vide si la course est partie sans.

Il tourne sous le Python de la machine, sans le paquet ni PyYAML.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import durees_suite


def _issue(dossier: Path) -> tuple[bool, str] | None:
    """L'issue d'un travail — nulle ou non — et sa durée ; rien s'il n'a rien
    rendu."""
    try:
        code, secondes = (dossier / "issue.txt").read_text(encoding="utf-8").split()
    except (OSError, ValueError):
        return None
    return code == "0", secondes


def rassembler(dossier: Path, tranches: int, fabrication: str, duree_fabrique: str,
               memoire: str) -> dict[str, str]:
    durees = [f"fabrique={duree_fabrique}"] if duree_fabrique else []
    if fabrication != "success":
        return {"suite": "skipped", "garde": "skipped", "durees": " ".join(durees),
                "durees_suite": ""}
    dossier.mkdir(parents=True, exist_ok=True)
    sortie, issues = [], {}
    for rang in range(1, tranches + 1):
        tranche = dossier / f"tranche-{rang}"
        issues[rang] = _issue(tranche)
        if issues[rang] is None:
            sortie.append(f"ERROR la tranche {rang} de la suite n'a rien rendu\n")
        elif (tranche / "suite.txt").is_file():
            sortie.append((tranche / "suite.txt").read_text(encoding="utf-8"))
    (dossier / "suite.txt").write_text("".join(sortie), encoding="utf-8")
    rendues = {rang: issue for rang, issue in issues.items() if issue}
    if rendues:
        durees.append(f"suite={max(int(secondes) for _, secondes in rendues.values())}")
    durees += [f"tranche_{rang}={secondes}" for rang, (_, secondes) in rendues.items()]
    garde = _issue(dossier / "garde")
    if garde:
        durees.append(f"garde={garde[1]}")
        (dossier / "garde.txt").write_text(
            (dossier / "garde" / "garde.txt").read_text(encoding="utf-8"), encoding="utf-8")
    tableau = ""
    releves = [dossier / f"tranche-{rang}" / "durees.xml" for rang in range(1, tranches + 1)]
    if not memoire and all(releve.is_file() for releve in releves):
        tableau = str(dossier / "durees.tsv")
        Path(tableau).write_text(durees_suite.tableau(durees_suite.par_fichier(releves)),
                                 encoding="utf-8")
    return {
        "suite": "success" if len(rendues) == tranches
                 and all(verte for verte, _ in rendues.values()) else "failure",
        "garde": "success" if garde and garde[0] else "failure",
        "durees": " ".join(durees),
        "durees_suite": tableau,
    }


if __name__ == "__main__":
    rendu = rassembler(Path(sys.argv[1]), int(os.environ["TRANCHES"]),
                       os.environ.get("FABRICATION", ""),
                       os.environ.get("DUREE_FABRIQUE", ""), os.environ.get("MEMOIRE", ""))
    for nom, valeur in rendu.items():
        print(f"{nom}={valeur}")
