#!/usr/bin/env python3
"""Les naissances de l'année : ce que des cohortes nées toute l'année déplacent à la page Coût.

    python scripts/cout_naissances.py
    python scripts/cout_naissances.py --json n.json

LA QUESTION
-----------
La grille fait naître ses cas types en janvier, et chaque cohorte compte toute
l'année de son départ, dans ses têtes comme dans ses masses : partie en
novembre, elle compte au 31 décembre tous ses retraités, et une année entière
de leur pension. Née toute l'année, elle n'en aurait que ses nés de janvier et
de février de partis, et 1/48 d'une année de pension servie
(``cout._partie``, ``cout._servie``). La masse de 2024, sur laquelle le
modèle s'ancre, et celle de 2025, d'où la dérive se compte, en sont grossies
(action 138, étape 3, note « l'entrée dans l'emploi » du 19 octobre 2026,
point 3).

CE QUE LE SCRIPT FAIT
---------------------
Il calcule la page deux fois (``calculer_cout(naissances=...)``) : sous la
grille, et ses cohortes nées toute l'année. Il imprime ce que la seconde
déplace : les têtes ; la masse du système actuel, et l'ancrage qui la
convertit en euros (``Avenir.ancrage``) ; la dérive, comptée depuis la
première année projetée ; la page — les systèmes 2 et 6, et la borne haute de
leur fourchette ; la reconstitution du passé et ses têtes, contre l'enquête
auprès des caisses.

CE QU'IL NE DÉCIDE PAS
----------------------
La page garde la grille : compter les cohortes nées toute l'année déplace la
proposition à la bascule et la borne haute de sa fourchette, et demanderait
que l'engagement acquis et le coût des avantages comptent de même. C'est au
propriétaire (note « les naissances de l'année » du 24 octobre 2026).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retraite_notionnelle import cout as C  # noqa: E402
from retraite_notionnelle import memoire  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.effectifs import EffectifsRetraites  # noqa: E402

#: Les deux comptes, dans l'ordre des colonnes.
VARIANTES = (C.NAISSANCES_EN_JANVIER, C.NAISSANCES_TOUTE_L_ANNEE)
ANNEES_TETES = (2009, 2022, 2024, 2025, 2030, 2040, 2070)
ANNEES_PAGE = (2026, 2027, 2030, 2050, 2070)
ANNEES_DERIVE = (2030, 2050, 2070)
ANNEES_PASSE = (2004, 2009, 2020)
SYSTEMES = (("notionnel_retroactif", "système 2"), ("notionnel_liberal", "système 6"))


def mesurer(naissances: str, parametres: Parametres) -> dict:
    """Ce que la page compte sous ``naissances`` : ses têtes, la masse du
    système actuel en unités du modèle (la base du modèle sans l'ancrage ni la
    réversion), l'ancrage, la dérive, les deux systèmes et leur borne haute, en
    points de PIB, et le passé refait."""
    cout = memoire.cout(parametres, naissances=naissances)
    avenir = cout.avenir
    racine = parametres.racine_donnees
    decompose = avenir.reconstitution_decomposee(
        EffectifsRetraites(racine).serie(EffectifsRetraites.TOUS_REGIMES),
        DepensesRetraite(racine).droits_derives)
    reconstitution = avenir.reconstitution()
    lignes = {ligne.annee: ligne for ligne in avenir.annees}
    return {
        "ancrage": avenir.ancrage,
        "tetes": {a: lignes[a].tetes for a in ANNEES_TETES},
        "masses": {a: lignes[a].base_modele / avenir.ancrage / lignes[a].facteur_reversion
                   for a in ANNEES_TETES},
        "derive": {a: lignes[a].derive for a in ANNEES_DERIVE},
        "page": {cle: {a: 100 * lignes[a].part_pib(cle) for a in ANNEES_PAGE}
                 for cle, _ in SYSTEMES},
        "borne_haute": {cle: {a: 100 * lignes[a].part_pib_derive(cle) for a in ANNEES_DERIVE}
                        for cle, _ in SYSTEMES},
        "reconstitution": {a: reconstitution[a] - 1.0 for a in ANNEES_PASSE},
        "tetes_du_passe": {a: decompose[a][0] - 1.0 for a in ANNEES_PASSE},
    }


def tableau(mesures: dict[str, dict]) -> str:
    """Chaque grandeur sous les deux comptes, et ce que le second déplace : un
    écart, ou un rapport pour la masse, qui se compte en unités du modèle."""
    grille, nees = (mesures[v] for v in VARIANTES)
    nees_toute_l_annee = "nées toute l'année"
    lignes = [f"{'':<38}{'grille':>10}{nees_toute_l_annee:>20}{'écart':>10}", ""]

    def ecart(libelle: str, avant: float, apres: float, decimales: int) -> None:
        lignes.append(f"{libelle:<38}{avant:>10.{decimales}f}{apres:>20.{decimales}f}"
                      f"{apres - avant:>+10.{decimales}f}")

    def rapport(libelle: str, avant: float, apres: float) -> None:
        lignes.append(f"{libelle:<68}{apres / avant - 1:>+10.1%}")

    for annee in ANNEES_TETES:
        ecart(f"têtes {annee}, millions", grille["tetes"][annee] / 1e6,
              nees["tetes"][annee] / 1e6, 3)
    lignes.append("")
    for annee in ANNEES_TETES:
        rapport(f"masse du système 1 en {annee}", grille["masses"][annee], nees["masses"][annee])
    rapport("ancrage", grille["ancrage"], nees["ancrage"])
    lignes.append("")
    for annee in ANNEES_DERIVE:
        ecart(f"dérive {annee}", grille["derive"][annee], nees["derive"][annee], 4)
    lignes.append("")
    for cle, nom in SYSTEMES:
        for annee in ANNEES_PAGE:
            ecart(f"{nom} {annee}, % du PIB", grille["page"][cle][annee],
                  nees["page"][cle][annee], 3)
        for annee in ANNEES_DERIVE:
            ecart(f"{nom} {annee}, borne haute", grille["borne_haute"][cle][annee],
                  nees["borne_haute"][cle][annee], 3)
    lignes.append("")
    for annee in ANNEES_PASSE:
        ecart(f"passé refait {annee}, %", 100 * grille["reconstitution"][annee],
              100 * nees["reconstitution"][annee], 2)
        ecart("  dont les têtes, %", 100 * grille["tetes_du_passe"][annee],
              100 * nees["tetes_du_passe"][annee], 2)
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    analyseur.add_argument("--json", type=Path)
    arguments = analyseur.parse_args(argv)
    parametres = Parametres()
    mesures = {naissances: mesurer(naissances, parametres) for naissances in VARIANTES}
    print(tableau(mesures))
    if arguments.json:
        arguments.json.write_text(json.dumps(mesures, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
