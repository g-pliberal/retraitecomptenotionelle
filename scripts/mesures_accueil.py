#!/usr/bin/env python3
"""Les mesures que l'accueil cite, écrites par le modèle et non à la main.

    python scripts/mesures_accueil.py             # récrit MESURES_BLOCAGES
    python scripts/mesures_accueil.py --verifier  # échoue si une valeur a vieilli

``MESURES_BLOCAGES`` (``moteur/js/pages.js``) porte ce que les points de
blocage de l'accueil citent : le solde, la dette et le coefficient du coût par
défaut, le taux du régime unique et le coût des 18 %, la variante prospective,
la TVA, le diviseur de l'âge de l'assuré. Écrites à la main, ces mesures ont
rougi la suite trois fois du 6 au 17 octobre 2026, chaque fois qu'un
changement du modèle les déplaçait (action 163, étape 2) : GitHub les récrit
désormais à chaque fabrique, entre le paquet et les témoins
(``scripts/regenerer.py``). Chacune se calcule comme le test qui la tient, à
la précision où l'accueil l'écrit ; ces tests restent, et la tiennent.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
PAGES = RACINE / "moteur" / "js" / "pages.js"
DEBUT = "export const MESURES_BLOCAGES = {"

#: Chaque mesure, et les décimales que l'accueil lui donne : celles du test
#: qui la tient.
PRECISIONS = {
    "taux_regime_unique": 1,            # tests/test_solde_fusion.py
    "cout_18_pour_cent": 1,             # tests/test_solde_fusion.py
    "solde_moyen_proposition": 1,       # tests/test_solde_fusion.py
    "solde_moyen_actuel": 1,
    "dette_2070_proposition": 0,
    "dette_2070_actuel": 0,
    "coefficient_minimum": 2,
    "decennie_coefficient_minimum": 0,
    "coefficient_2070": 2,
    "tva_affectee": 1,                  # tests/test_tva.py
    "solde_moyen_prospectif": 1,        # tests/test_proposition_prospective.py
    "cout_diviseur_age_legal": 1,       # tests/test_stock_age_legal.py
}

LIGNE = re.compile(r"^(\s+)([a-z_0-9]+): (-?\d+(?:\.\d+)?),$", re.M)


def mesures() -> dict[str, float]:
    """Les mesures, refaites comme leurs tests les refont."""
    sys.path.insert(0, str(RACINE / "scripts"))
    import proposition_prospective
    import solde_fusion
    import stock_age_legal

    from retraite_notionnelle import cout as C
    from retraite_notionnelle import memoire
    from retraite_notionnelle.config import RACINE_DONNEES, Parametres
    from retraite_notionnelle.donnees.tva import AssietteTva
    from retraite_notionnelle.simulateur import Simulateur

    liberal = "notionnel_liberal"
    parametres = Parametres()
    reference = memoire.cout(parametres)
    solde, dette = reference.solde, reference.dette
    plus_bas = min(solde.projetees(), key=lambda ligne: ligne.coefficient(liberal))
    simulateur = Simulateur(parametres).pour_la_projection()
    fusion = solde_fusion.calculer(
        solde_fusion.hypotheses(simulateur.catalogue, 2026)["A"], parametres)
    lectures = fusion.lectures[C.CONVENTION_ASSIETTE]
    prospective = proposition_prospective.calculer(True, parametres)
    age_assure = stock_age_legal.calculer("reference", parametres)
    droit_commun = stock_age_legal.calculer("droit_commun", parametres)
    return {
        "taux_regime_unique": fusion.taux_effectif * 100,
        "cout_18_pour_cent": (lectures["notionnel_retroactif_employeur"].solde_moyen
                              - lectures[liberal].solde_moyen) * 100,
        "solde_moyen_proposition": solde.solde_moyen(liberal, 2026, C.HORIZON) * 100,
        "solde_moyen_actuel": solde.solde_moyen("actuel", 2026, C.HORIZON) * 100,
        "dette_2070_proposition": dette.horizon(liberal) * 100,
        "dette_2070_actuel": dette.horizon("actuel") * 100,
        "coefficient_minimum": plus_bas.coefficient(liberal),
        "decennie_coefficient_minimum": plus_bas.annee // 10 * 10,
        "coefficient_2070": solde.annee(C.HORIZON).coefficient(liberal),
        "tva_affectee": AssietteTva(RACINE_DONNEES).recette_supplementaire(
            parametres.taux_tva_liberal) * 100,
        "solde_moyen_prospectif":
            prospective.lectures[proposition_prospective.LIBERAL].solde_moyen * 100,
        "cout_diviseur_age_legal": (age_assure.lectures[liberal].solde_moyen
                                    - droit_commun.lectures[liberal].solde_moyen) * 100,
    }


def reecrire(texte: str, valeurs: dict[str, float],
             precisions: dict[str, int] = PRECISIONS) -> str:
    """Le texte de ``pages.js``, chaque valeur du bloc récrite à sa précision ;
    rien d'autre ne change. Une mesure que le bloc porte sans qu'on la sache
    refaire, ou l'inverse, arrête tout."""
    debut = texte.index(DEBUT)
    fin = texte.index("\n};", debut)
    vues: set[str] = set()

    def remplacer(trouve: re.Match) -> str:
        retrait, cle = trouve.group(1), trouve.group(2)
        if cle not in valeurs:
            raise ValueError(f"MESURES_BLOCAGES porte « {cle} », que rien ne refait")
        vues.add(cle)
        valeur = round(valeurs[cle], precisions[cle]) + 0.0   # sans zéro négatif
        return f"{retrait}{cle}: {valeur:.{precisions[cle]}f},"

    bloc = LIGNE.sub(remplacer, texte[debut:fin])
    if vues != set(valeurs):
        raise ValueError(f"MESURES_BLOCAGES ne porte pas {sorted(set(valeurs) - vues)}")
    return texte[:debut] + bloc + texte[fin:]


def main() -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--verifier", action="store_true",
                           help="échoue si une valeur a vieilli, sans rien écrire")
    arguments = analyseur.parse_args()
    texte = PAGES.read_text(encoding="utf-8")
    voulu = reecrire(texte, mesures())
    if arguments.verifier:
        if voulu != texte:
            print("MESURES_BLOCAGES a vieilli : lancer python scripts/mesures_accueil.py",
                  file=sys.stderr)
            return 1
        print("les mesures de l'accueil sont à jour")
        return 0
    if voulu != texte:
        PAGES.write_text(voulu, encoding="utf-8", newline="\n")
        print("moteur/js/pages.js réécrit : MESURES_BLOCAGES")
    return 0


if __name__ == "__main__":
    sys.exit(main())
