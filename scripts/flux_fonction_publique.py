#!/usr/bin/env python3
"""Les cas types statutaires face aux départs de 2025 que décrit le jaune pensions.

    python scripts/flux_fonction_publique.py            # le tableau, cas type par cas type
    python scripts/flux_fonction_publique.py --json f.json

LA QUESTION
-----------
Les trois cas types statutaires de la grille — le fonctionnaire sédentaire de
l'État, l'agent de catégorie active de la CNRACL, le militaire — sont des
individus moyens : chacun porte toute sa caisse sur la page « Coût ».
Partent-ils comme partent les fonctionnaires réels ? Le jaune pensions annexé
au PLF 2027 décrit les départs de 2025 de chacun de ces groupes, et le dépôt
les certifie (``data/reference/macro/caracteristiques_fonction_publique.csv``,
action 159, étape 4). Ce script fait partir chaque cas type en 2025, et met
en regard ce que le modèle lui sert et ce que le jaune publie.

CE QU'ON COMPARE À QUOI
-----------------------
Chaque cas type a son départ de référence (:data:`REFERENTS`) : les civils de
l'État partis pour ancienneté en catégorie sédentaire, hors carrières longues
(tableau B-4) ; les agents de la CNRACL partis pour ancienneté en catégorie
active (B-5) ; les militaires partis pour ancienneté, tous grades (B-3), dont
le cas type est le militaire moyen depuis l'action 152. Cinq mesures :

- l'âge de la première mise en paiement ;
- la durée d'assurance tous régimes, bonifications comprises, en trimestres ;
- le taux de liquidation : la pension rapportée au traitement qui la liquide,
  décote ou surcote comprise. Le jaune le calcule, à l'État, hors pensions
  portées au minimum garanti ; aucun cas type n'y est porté ;
- l'indice : le traitement de référence du cas type, ramené à l'indice majoré
  par la valeur annuelle du point de 2025 ;
- la pension mensuelle brute, avantage principal, sans accessoire ni
  majoration : aucun cas type n'a d'enfant.

QUATRE RÉSERVES
---------------
1. **Un cas type est UNE carrière, le jaune une moyenne.** Un cas type au taux
   plein face à un flux dont la moitié a une surcote et le cinquième une
   décote n'est pas en faute pour autant : c'est l'écart des moyennes qui se
   lit, non celui des distributions.
2. **Le cas type part en 2025 parce qu'on choisit sa génération pour cela** :
   celle que le droit, appliqué à sa carrière, fait partir cette année-là
   (:func:`depart_en`). Les générations de la page avancent de cinq en cinq ;
   aucune ne part forcément en 2025.
3. **Le flux réel a d'autres carrières que la sienne** : des polypensionnés,
   entrés tard ou partis avant dans le privé, dont la durée tous régimes
   dépasse les services. Un cas type n'a qu'une carrière, entière dans son
   régime.
4. **Les euros sont ceux de 2025, courants, des deux côtés** : le cas type est
   liquidé en 2025, et le jaune publie les pensions entrées en paiement en
   2025.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE / "src"))

from retraite_notionnelle import memoire  # noqa: E402
from retraite_notionnelle.castypes import CAS_TYPES, CasType, calculer_cas_types  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

REFERENCE = RACINE / "data" / "reference" / "macro" / "caracteristiques_fonction_publique.csv"
POINT = RACINE / "data" / "reference" / "legislation" / "point_indice_fonction_publique.csv"

#: L'année des départs que le jaune décrit.
ANNEE = 2025

#: Le départ du flux de 2025 auquel chaque cas type se mesure : (tableau,
#: population, champ) de ``caracteristiques_fonction_publique.csv``.
REFERENTS = {
    "fonctionnaire_sedentaire": ("B-4", "fpe_civils", "sedentaire"),
    "fonctionnaire_actif": ("B-5", "cnracl_total", "active"),
    "militaire": ("B-3", "fpe_militaires", "anciennete"),
}

#: Les mesures, dans l'ordre du tableau, et leur libellé.
INDICATEURS = (
    ("age_premiere_mise_en_paiement", "âge de première mise en paiement"),
    ("duree_tous_regimes_trimestres", "durée tous régimes (trimestres)"),
    ("taux_liquidation", "taux de liquidation"),
    ("indice_liquidation", "indice de liquidation"),
    ("pension_principale_eur", "pension mensuelle (€)"),
)


@dataclass
class Mesure:
    """Ce que le modèle et le jaune disent d'un même cas type."""

    cas_type: str
    generation: int
    tableau: str
    population: str
    champ: str
    indicateur: str
    modele: float
    jaune: float

    @property
    def ecart(self) -> float:
        """Le modèle moins le jaune, dans l'unité de la mesure."""
        return self.modele - self.jaune

    @property
    def ecart_relatif(self) -> float:
        """Le même écart, rapporté au jaune."""
        return self.modele / self.jaune - 1.0


def referents_publies() -> dict[tuple[str, str, str, str, str], float]:
    """Le fichier certifié, à plat : (tableau, population, champ, modalite,
    indicateur)."""
    with REFERENCE.open(encoding="utf-8") as flux:
        lignes = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        return {(l["tableau"], l["population"], l["champ"], l["modalite"], l["indicateur"]):
                float(l["valeur"]) for l in csv.DictReader(lignes)}


def point_annuel(annee: int = ANNEE) -> float:
    """La valeur annuelle du point d'indice de la fonction publique, en euros."""
    with POINT.open(encoding="utf-8") as flux:
        lignes = (ligne for ligne in flux if not ligne.lstrip().startswith("#"))
        for ligne in csv.reader(lignes):
            if ligne and ligne[0] == str(annee):
                return float(ligne[1])
    raise LookupError(f"pas de valeur du point en {annee} dans {POINT.name}")


def depart_en(simulateur: Simulateur, cas: CasType, annee: int = ANNEE):
    """(génération, comparaison) du cas type que le droit fait partir en
    ``annee`` : on part de l'année moins son âge de départ, et l'on avance ou
    recule d'une génération tant que le départ tombe avant ou après."""
    generation = annee - round(cas.age_liquidation)
    vues: set[int] = set()
    while generation not in vues:
        vues.add(generation)
        grille = calculer_cas_types(simulateur, (cas,), (generation,), "droit")
        comparaison = grille.resultats.get((cas.code, generation))
        if comparaison is None:
            raise ValueError(f"{cas.code}, {generation} : {grille.echecs}")
        depart = comparaison.carriere.annee_liquidation
        if depart == annee:
            return generation, comparaison
        generation += 1 if depart < annee else -1
    raise ValueError(f"{cas.code} : aucune génération ne part en {annee}")


def pension_et_traitement(comparaison) -> tuple[float, float]:
    """La pension annuelle du régime du code des pensions qui liquide le cas
    type, avant tout complément, et le traitement ou la solde de L. 15 qui la
    liquide, en euros de la date d'effet : ce que la liquidation garde pour
    le plafond de la majoration pour enfants (L. 18)."""
    for entree in comparaison.journal:
        if entree.sorte != "liquidation":
            continue
        pensions = entree.contenu.pensions
        for plafond in pensions.plafonds:
            return pensions.regimes[plafond.indice].montant, plafond.traitement
    raise ValueError("aucune pension du code des pensions")


def mesures_du_cas(comparaison, point: float) -> dict[str, float]:
    """Les cinq mesures d'un cas type parti en 2025."""
    pension, traitement = pension_et_traitement(comparaison)
    return {
        "age_premiere_mise_en_paiement": float(comparaison.carriere.age_liquidation),
        "duree_tous_regimes_trimestres": float(comparaison.actuel.trimestres_valides),
        "taux_liquidation": pension / traitement,
        "indice_liquidation": traitement / point,
        "pension_principale_eur": pension / 12.0,
    }


def mesurer_le_modele(simulateur: Simulateur) -> dict[str, tuple[int, dict[str, float]]]:
    """Ce que le modèle dit de chaque cas type statutaire parti en 2025 : sa
    génération, et ses cinq mesures."""
    point = point_annuel()
    par_code = {cas.code: cas for cas in CAS_TYPES}
    modele: dict[str, tuple[int, dict[str, float]]] = {}
    for code in REFERENTS:
        generation, comparaison = depart_en(simulateur, par_code[code])
        modele[code] = (generation, {indicateur: round(valeur, 4) for indicateur, valeur
                                     in mesures_du_cas(comparaison, point).items()})
    return modele


def confronter(modele: dict[str, tuple[int, dict[str, float]]],
               publies: dict[tuple[str, str, str, str, str], float]) -> list[Mesure]:
    """Le tableau : chaque mesure du modèle face à celle du jaune."""
    mesures: list[Mesure] = []
    for code, (tableau, population, champ) in REFERENTS.items():
        generation, valeurs = modele[code]
        for indicateur, _ in INDICATEURS:
            mesures.append(Mesure(code, generation, tableau, population, champ, indicateur,
                                  valeurs[indicateur],
                                  publies[(tableau, population, champ, "ensemble",
                                           indicateur)]))
    return mesures


def mesurer(simulateur: Simulateur) -> list[Mesure]:
    """Le tableau, sur ce simulateur."""
    return confronter(mesurer_le_modele(simulateur), referents_publies())


def mesures_du_depot(parametres: Parametres) -> list[Mesure]:
    """Le tableau, sur un simulateur neuf et les données du dépôt. La part du
    modèle se garde dans la mémoire des calculs (``retraite_notionnelle/
    memoire.py``) ; le jaune se relit à chaque fois : il est hors de
    l'empreinte du modèle (``HORS_DU_MODELE``), qui ne dirait pas qu'il a
    changé."""
    modele = memoire.memoriser_pour(parametres, ("flux_fonction_publique", parametres),
                                    lambda: mesurer_le_modele(Simulateur(parametres)))
    return confronter(modele, referents_publies())


def _format(indicateur: str, valeur: float) -> str:
    if indicateur == "taux_liquidation":
        return f"{valeur:.1%}"
    if indicateur in ("indice_liquidation", "pension_principale_eur"):
        return f"{valeur:,.0f}".replace(",", " ")
    return f"{valeur:.1f}"


def imprimer(mesures: list[Mesure]) -> None:
    libelles = dict(INDICATEURS)
    courant = None
    for mesure in mesures:
        if mesure.cas_type != courant:
            courant = mesure.cas_type
            print(f"\n{mesure.cas_type}, génération {mesure.generation}, face au tableau "
                  f"{mesure.tableau} ({mesure.population}, {mesure.champ})")
            print(f"  {'':34} {'modèle':>9} {'jaune':>9} {'écart':>8}")
        print(f"  {libelles[mesure.indicateur]:34} {_format(mesure.indicateur, mesure.modele):>9} "
              f"{_format(mesure.indicateur, mesure.jaune):>9} {mesure.ecart_relatif:>+8.1%}")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--json", type=Path, help="écrit aussi le tableau dans ce fichier")
    options = analyseur.parse_args(argv)
    mesures = mesures_du_depot(Parametres())
    imprimer(mesures)
    if options.json:
        options.json.write_text(json.dumps([asdict(m) for m in mesures], ensure_ascii=False,
                                           indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
