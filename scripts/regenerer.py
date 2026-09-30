#!/usr/bin/env python3
"""Régénère tout ce qu'un script fabrique, dans l'ordre où les fichiers se lisent.

    python scripts/regenerer.py              # réécrit tout, et dit ce que chaque étape a pris
    python scripts/regenerer.py --verifier   # n'écrit rien : dit tout ce qui est périmé
    python scripts/regenerer.py --prose      # le tableau de bord et les chiffres ancrés seuls
    python scripts/regenerer.py --etapes     # les étapes, sans rien lancer

POURQUOI
--------
Un changement du modèle déplace une dizaine de fichiers fabriqués : l'inventaire,
le paquet du site, les témoins, le chiffrage, les tableaux du README, le tableau
de bord, les chiffres ancrés de la prose. Chacun a son script, et ils se lisent
les uns les autres : les témoins de pages rendent le site avec le paquet, le
tableau de bord compte les témoins, les chiffres ancrés sondent tout le reste.
C'étaient sept ou huit commandes dans un ordre à retenir, et en oublier une
coûtait un passage de la suite complète, qui la trouvait périmée huit minutes
plus tard (action 132). Ce script les lance toutes, dans l'ordre, et
``--verifier`` les passe TOUTES en revue au lieu de s'arrêter à la première.

L'ORDRE
-------
Trois temps. L'inventaire d'abord, que tout lit, et le document des régimes qui
en sort. Puis, en même temps, trois branches qui ne se lisent pas : le paquet
suivi des témoins, qui rendent le site avec lui ; le chiffrage ; les tableaux du
README. Enfin le tableau de bord, qui compte les témoins et les tests, et les
chiffres ancrés, qui sondent tout. Les trois branches du milieu prennent
ensemble le temps de la plus longue, le paquet et les témoins, une minute et
demie, au lieu de deux et quart ; ``--sequentiel`` les enchaîne. Les chiffres
ancrés, qui prenaient trois minutes, en prennent moins d'une quand le modèle a
bougé, et un quart sinon : leurs calculs lourds se font en parallèle et se
gardent sur le disque (``mesures_prose.py`` ; feuille de route, action 135).

UNE ÉTAPE INCHANGÉE NE SE RELANCE PAS. Le paquet, les témoins, le chiffrage
et les chiffres ancrés gardent, à la fin d'une régénération, l'empreinte de ce
qu'ils lisent et écrivent (``retraite_notionnelle/fabrique.py``) : une
retouche du site ne refait ni le paquet ni le chiffrage, et ``--verifier``,
juste après une régénération, ne refait rien. ``FABRIQUE_SANS_MEMOIRE=1``
relance tout.

Le contrôle de conservation (``conservation.py``) vient à la fin, et ne fait
que contrôler : refiger sa référence est un geste délibéré, qui se dit dans le
commit (``--figer``, et ``--accepter-les-pertes`` pour un récit réécrit exprès).
Ce que les témoins ont bougé se lit ensuite par ``scripts/resumer_temoins.py``.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from retraite_notionnelle import fabrique

RACINE = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Etape:
    """Un script de fabrication, et ce qu'il écrit."""

    nom: str
    script: str
    #: Ses arguments pour écrire, et pour vérifier sans rien écrire.
    ecrire: tuple[str, ...]
    verifier: tuple[str, ...]
    ecrit: str


INVENTAIRE = Etape("inventaire", "construire_inventaire.py", (), ("--verifier",),
                   "data/reference/regimes/inventaire.yaml")
REGIMES = Etape("régimes", "construire_regimes_md.py", (), ("--verifier",),
                "docs/regimes.md")
PAQUET = Etape("paquet", "construire_donnees.py", (), ("--verifier",),
               "moteur/donnees.json, data/derive/equilibre.json, "
               "data/derive/calibrations_mortalite.json")
TEMOINS = Etape("témoins", "construire_temoins.py", (), ("--verifier",),
                "tests/temoins/simulations.json, tests/temoins/pages.json")
CHIFFRAGE = Etape("chiffrage", "chiffrage_plf.py", (), ("--verifier",),
                  "docs/chiffrage_plf.md, docs/chiffrage_plf.csv")
TABLEAUX = Etape("tableaux", "construire_tableaux_md.py", (), ("--verifier",),
                 "les blocs produits du README")
TABLEAU_DE_BORD = Etape("tableau de bord", "tableau_de_bord.py", (), ("--verifier",),
                        "docs/etat.md")
PROSE = Etape("prose", "verifier_prose.py", ("--corriger",), (),
              "les chiffres ancrés des documents")
CONSERVATION = Etape("conservation", "conservation.py", (), (),
                     "rien : un contrôle")

#: Les trois temps : chacun est une liste de branches, et une branche une suite
#: d'étapes. Les branches d'un même temps ne se lisent pas l'une l'autre.
TEMPS: tuple[tuple[tuple[Etape, ...], ...], ...] = (
    ((INVENTAIRE, REGIMES),),
    ((PAQUET, TEMOINS), (CHIFFRAGE,), (TABLEAUX,)),
    ((TABLEAU_DE_BORD, PROSE, CONSERVATION),),
)
#: Ce que ``--prose`` relance : ce qui ne lit que les documents et les registres.
TEMPS_PROSE: tuple[tuple[tuple[Etape, ...], ...], ...] = (
    ((TABLEAU_DE_BORD, PROSE, CONSERVATION),),
)


def etapes(temps=TEMPS) -> list[Etape]:
    """Les étapes, dans l'ordre où une exécution sans parallélisme les lance."""
    return [etape for branches in temps for branche in branches for etape in branche]


@dataclass
class Issue:
    etape: Etape
    code: int
    duree: float
    sortie: str
    #: Vraie quand le script a réellement tourné, ou que la mémoire l'a
    #: dispensé : seule une telle issue se retient (``fabrique.py``).
    reelle: bool = False


def lancer(etape: Etape, verifier: bool) -> Issue:
    if etape.nom in fabrique.ETAPES and fabrique.a_jour(etape.nom):
        return Issue(etape, 0, 0.0, "inchangé depuis la dernière fabrication", True)
    arguments = etape.verifier if verifier else etape.ecrire
    debut = time.perf_counter()
    fini = subprocess.run([sys.executable, str(RACINE / "scripts" / etape.script),
                           *arguments], cwd=RACINE, capture_output=True, text=True)
    return Issue(etape, fini.returncode, time.perf_counter() - debut,
                 (fini.stdout + fini.stderr).strip(), True)


def branche(suite: tuple[Etape, ...], verifier: bool) -> list[Issue]:
    """Une suite d'étapes, dont chacune lit ce que la précédente écrit : en
    écriture, un échec arrête la branche ; en vérification, chaque étape est
    passée en revue."""
    issues = []
    for etape in suite:
        issue = lancer(etape, verifier)
        issues.append(issue)
        if issue.code and not verifier:
            break
    return issues


def dire(issue: Issue, verifier: bool) -> str:
    etat = ("à jour" if verifier else "fait") if not issue.code else (
        "PÉRIMÉ" if verifier else "ÉCHEC")
    ligne = f"{issue.etape.nom:<16} {issue.duree:6.1f} s  {etat}"
    if issue.code or not verifier:
        detail = issue.sortie.splitlines()
        if detail:
            montrees = detail if issue.code else detail[-3:]
            ligne += "\n" + "\n".join(f"    {l}" for l in montrees)
    return ligne


def regenerer(temps=TEMPS, verifier: bool = False, sequentiel: bool = False) -> int:
    debut = time.perf_counter()
    echecs = []
    reussies = []
    for branches in temps:
        if sequentiel or len(branches) == 1:
            resultats = [branche(b, verifier) for b in branches]
        else:
            with ThreadPoolExecutor(max_workers=len(branches)) as pool:
                resultats = list(pool.map(lambda b: branche(b, verifier), branches))
        for issues in resultats:
            for issue in issues:
                print(dire(issue, verifier), flush=True)
                if issue.code:
                    echecs.append(issue.etape.nom)
                elif issue.reelle:
                    reussies.append(issue.etape.nom)
        if echecs and not verifier:
            break
    # À la fin seulement : une étape suivante peut encore écrire ce qu'une
    # étape réussie lit, et l'empreinte doit être celle de l'état final.
    for nom in reussies:
        if nom in fabrique.ETAPES:
            fabrique.retenir(nom)
    total = time.perf_counter() - debut
    if echecs:
        quoi = "périmé" if verifier else "en échec"
        print(f"{', '.join(echecs)} : {quoi} ({total:.0f} s)", file=sys.stderr)
        return 1
    print(f"tout est à jour ({total:.0f} s)" if verifier
          else f"tout est régénéré ({total:.0f} s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="n'écrit rien ; dit chaque fichier fabriqué périmé")
    analyseur.add_argument("--prose", action="store_true",
                           help="le tableau de bord et les chiffres ancrés seuls, "
                                "quand seuls les documents ou les registres ont changé")
    analyseur.add_argument("--sequentiel", action="store_true",
                           help="enchaîne les branches au lieu de les lancer ensemble")
    analyseur.add_argument("--etapes", action="store_true",
                           help="les étapes et ce qu'elles écrivent, sans rien lancer")
    arguments = analyseur.parse_args(argv)
    temps = TEMPS_PROSE if arguments.prose else TEMPS
    if arguments.etapes:
        for rang, branches in enumerate(temps, 1):
            for suite in branches:
                print(f"{rang}. " + " → ".join(
                    f"{e.nom} ({e.script} : {e.ecrit})" for e in suite))
        return 0
    return regenerer(temps, verifier=arguments.verifier, sequentiel=arguments.sequentiel)


if __name__ == "__main__":
    raise SystemExit(main())
