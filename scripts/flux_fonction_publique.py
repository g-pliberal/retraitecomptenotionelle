#!/usr/bin/env python3
"""Les cas types statutaires face aux départs de 2025 que décrit le jaune pensions.

    python scripts/flux_fonction_publique.py            # le flux de 2025, chaque année, le stock
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

Le cas type est mesuré tel que la page Coût le pèse, celle où il porte sa
caisse : sous les conventions de projection du COR
(:meth:`~retraite_notionnelle.simulateur.Simulateur.pour_la_projection`), qui
font entrer les fonctionnaires civils dans leur régime après quelques années
sous un autre statut. La page Cas types en montre la carrière d'un seul
statut : le droit d'une carrière, non le retraité moyen d'une caisse.

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
   dépasse les services, que les enfants allongent aussi. Le cas type entre
   tard dans son régime, s'il est civil, mais sa carrière est continue, sans
   enfant ni temps partiel : sa durée tous régimes reste en deçà.
4. **Les euros sont ceux de 2025, courants, des deux côtés** : le cas type est
   liquidé en 2025, et le jaune publie les pensions entrées en paiement en
   2025.

ANNÉE PAR ANNÉE, PUIS LE STOCK
------------------------------
Le flux de 2025 est une année. Les séries du jaune en donnent dix : chaque cas
type part aussi en 2016, en 2017… jusqu'en 2025 — la génération que le droit
fait partir cette année-là, quand il y en a une —, face à la série qui suit
son groupe (:data:`SERIES`) : l'âge des sédentaires de l'État partis pour
ancienneté (tableau 101) et leur taux hors minimum garanti (107), l'âge des
actifs de la CNRACL (102), et, faute de série plus fine, l'indice, la pension
et le taux de tout le flux de son régime (B-14), pension accessoires compris.

Le stock enfin, pesé comme la page « Coût » le pèse
(:func:`stock_pese_comme_la_page`) : chaque génération de sa grille,
représentant les cinq cohortes de sa tranche, chacune partie à son année, à
l'effectif de son âge et à sa complétude — les poids de
``cout._masses_regimes`` —, sert une pension moyenne aux retraités de chaque
année, au titre de son régime statutaire, face à celle que le jaune publie du
stock de droit direct de ce régime (tableaux A-4 et A-5). La page compte en
euros constants, le droit indexant les pensions sur les prix ; le stock réel
a été revalorisé moins vite que les prix depuis 2016.
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
from retraite_notionnelle.cout import _DEMI_TRANCHE, _pensionnes  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.config import Parametres  # noqa: E402
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402
from retraite_notionnelle.somme import somme_ordonnee  # noqa: E402

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

#: Les années que les séries du jaune couvrent : de 2016, où commence celle du
#: B-14, à 2025.
ANNEES = tuple(range(2016, 2026))

#: Pour chaque cas type, la série du jaune qui suit chaque mesure année par
#: année : (tableau, population, champ, indicateur), l'année en modalité.
#: L'âge et le taux du sédentaire sont ceux des civils sédentaires partis pour
#: ancienneté (tableaux 101 et 107, ce dernier hors minimum garanti) ; l'âge
#: de l'actif, celui des actifs de la CNRACL (102) ; le reste, celui de tout
#: le flux de son régime (B-14), la pension accessoires compris. Le jaune n'a
#: pas de série de l'âge des militaires.
SERIES = {
    "fonctionnaire_sedentaire": {
        "age_premiere_mise_en_paiement": ("101", "fpe_civils", "sedentaire",
                                          "age_premiere_mise_en_paiement"),
        "taux_liquidation": ("107", "fpe_civils", "anciennete", "taux_liquidation"),
        "indice_liquidation": ("B-14", "fpe_civils", "droit_direct", "indice_liquidation"),
        "pension_principale_eur": ("B-14", "fpe_civils", "droit_direct",
                                   "pension_avec_accessoires_eur"),
    },
    "fonctionnaire_actif": {
        "age_premiere_mise_en_paiement": ("102", "cnracl_total", "active",
                                          "age_premiere_mise_en_paiement"),
        "taux_liquidation": ("B-14", "cnracl_total", "droit_direct", "taux_liquidation"),
        "indice_liquidation": ("B-14", "cnracl_total", "droit_direct", "indice_liquidation"),
        "pension_principale_eur": ("B-14", "cnracl_total", "droit_direct",
                                   "pension_avec_accessoires_eur"),
    },
    "militaire": {
        "taux_liquidation": ("B-14", "fpe_militaires", "droit_direct", "taux_liquidation"),
        "indice_liquidation": ("B-14", "fpe_militaires", "droit_direct", "indice_liquidation"),
        "pension_principale_eur": ("B-14", "fpe_militaires", "droit_direct",
                                   "pension_avec_accessoires_eur"),
    },
}

#: Le régime de chaque cas type statutaire, dans le stock du jaune.
REGIMES_DU_STOCK = {"fonctionnaire_sedentaire": "fpe_civils",
                    "fonctionnaire_actif": "cnracl_total", "militaire": "fpe_militaires"}
#: Et dans le modèle : celui qui sert la pension que le jaune décrit.
REGIMES_STATUTAIRES = {"fonctionnaire_sedentaire": "fonction_publique_etat",
                       "fonctionnaire_actif": "cnracl", "militaire": "fonction_publique_etat"}

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
    """Le tableau, sur le simulateur de la page Coût et les données du dépôt.
    La part du modèle se garde dans la mémoire des calculs
    (``retraite_notionnelle/memoire.py``) ; le jaune se relit à chaque fois :
    il est hors de l'empreinte du modèle (``HORS_DU_MODELE``), qui ne dirait
    pas qu'il a changé."""
    modele = memoire.memoriser_pour(
        parametres, ("flux_fonction_publique", parametres),
        lambda: mesurer_le_modele(Simulateur(parametres).pour_la_projection()))
    return confronter(modele, referents_publies())


@dataclass
class MesureAnnuelle:
    """Ce que le modèle et une série du jaune disent d'un cas type, une année."""

    cas_type: str
    annee: int
    generation: int
    indicateur: str
    tableau: str
    modele: float
    jaune: float

    @property
    def ecart(self) -> float:
        return self.modele - self.jaune

    @property
    def ecart_relatif(self) -> float:
        return self.modele / self.jaune - 1.0


def mesurer_les_annees(simulateur: Simulateur, annees: tuple[int, ...] = ANNEES
                       ) -> dict[str, dict[int, tuple[int, dict[str, float]]]]:
    """Chaque cas type statutaire, parti chacune de ces années : sa génération
    et ses mesures. Une année où le droit ne fait partir aucune génération —
    le sédentaire de 1960 part en 2023, celui de 1961 en 2025 — n'a pas de
    mesure."""
    par_code = {cas.code: cas for cas in CAS_TYPES}
    modele: dict[str, dict[int, tuple[int, dict[str, float]]]] = {}
    for code in REFERENTS:
        for annee in annees:
            try:
                generation, comparaison = depart_en(simulateur, par_code[code], annee)
            except ValueError:
                continue
            mesures = mesures_du_cas(comparaison, point_annuel(annee))
            modele.setdefault(code, {})[annee] = (
                generation, {indicateur: round(valeur, 4) for indicateur, valeur in mesures.items()})
    return modele


def confronter_les_annees(modele: dict[str, dict[int, tuple[int, dict[str, float]]]],
                          publies: dict[tuple[str, str, str, str, str], float]
                          ) -> list[MesureAnnuelle]:
    """Chaque mesure de chaque année face à la série du jaune qui la suit."""
    mesures: list[MesureAnnuelle] = []
    for code, series in SERIES.items():
        for annee, (generation, valeurs) in sorted(modele.get(code, {}).items()):
            for indicateur, (tableau, population, champ, publie) in series.items():
                jaune = publies.get((tableau, population, champ, str(annee), publie))
                if jaune is not None:
                    mesures.append(MesureAnnuelle(code, annee, generation, indicateur, tableau,
                                                  valeurs[indicateur], jaune))
    return mesures


def mesures_annuelles_du_depot(parametres: Parametres) -> list[MesureAnnuelle]:
    """Les mesures de chaque année, sur le simulateur de la page Coût, comme
    celles du flux de 2025, et les données du dépôt ; la part du modèle se
    garde dans la mémoire des calculs."""
    modele = memoire.memoriser_pour(
        parametres, ("flux_fonction_publique_annees", parametres),
        lambda: mesurer_les_annees(Simulateur(parametres).pour_la_projection()))
    return confronter_les_annees(modele, referents_publies())


def stock_pese_comme_la_page(simulateur: Simulateur, annees: tuple[int, ...] = ANNEES
                             ) -> dict[str, dict[int, float]]:
    """La pension mensuelle moyenne que la page « Coût » sert, chaque année,
    aux retraités de chaque cas type statutaire, au titre de son régime
    statutaire — celui dont le jaune décrit le stock —, en euros courants de
    l'année.

    C'est la grille de la page (``cout._pensionnes``, sous les conventions du
    COR), pesée comme ``cout._masses_regimes`` la pèse : chaque génération de
    la grille représente les cinq cohortes de sa tranche, chacune partie à son
    année et comptée à l'effectif de son âge ; ce que chaque cohorte touche de
    la pension de la grille (sa complétude) pèse sa masse, non ses têtes ; et
    seule compte la part de la pension que sert le régime statutaire, l'État
    ou la CNRACL, le civil ayant cotisé ailleurs avant d'y entrer. Les pensions
    de la page sont en euros constants, ces régimes les indexant sur les prix :
    l'indice des prix les ramène aux euros de l'année."""
    cas_types = tuple(cas for cas in CAS_TYPES if cas.code in REFERENTS)
    pensionnes, _ = _pensionnes(simulateur, cas_types, "droit")
    population = Population(simulateur.parametres.racine_donnees)
    euros = simulateur.parametres.annee_euros_constants
    stock: dict[str, dict[int, float]] = {}
    for code in REFERENTS:
        regime = REGIMES_STATUTAIRES[code]
        for annee in annees:
            servie = tetes = 0.0
            for pensionne in pensionnes:
                if pensionne.code != code:
                    continue
                pension = pensionne.pensions["actuel"] * pensionne.parts_regimes.get(regime, 0.0)
                for decalage in range(-_DEMI_TRANCHE, _DEMI_TRANCHE + 1):
                    if annee < pensionne.annee_liquidation + decalage:
                        continue
                    effectif = population.effectif(annee - pensionne.generation - decalage,
                                                   annee)
                    servie += effectif * pensionne.completude(decalage) * pension
                    tetes += effectif
            if tetes > 0.0:
                stock.setdefault(code, {})[annee] = round(
                    servie / tetes * simulateur.macro.coefficient_prix(euros, annee) / 12, 2)
    return stock


def stock_du_depot(parametres: Parametres) -> dict[str, dict[int, float]]:
    """Le stock pesé comme la page, sur les données du dépôt, gardé dans la
    mémoire des calculs : la grille de la page prend quelques secondes."""
    return memoire.memoriser_pour(parametres, ("stock_fonction_publique", parametres),
                                  lambda: stock_pese_comme_la_page(Simulateur(parametres)))


def stock_publie(code: str, publies: dict[tuple[str, str, str, str, str], float]
                 ) -> dict[int, tuple[float | None, float | None]]:
    """Le stock de droit direct du régime d'un cas type, chaque année : (la
    pension avec ses accessoires, tableau A-4 ; l'avantage principal seul,
    tableau A-5, en 2024 et 2025)."""
    population = REGIMES_DU_STOCK[code]
    return {annee: (publies.get(("A-4", population, "droit_direct", str(annee),
                                 "pension_avec_accessoires_eur")),
                    publies.get(("A-5", population, "droit_direct", str(annee),
                                 "pension_principale_eur")))
            for annee in ANNEES}


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


def imprimer_les_annees(mesures: list[MesureAnnuelle]) -> None:
    libelles = dict(INDICATEURS)
    print("\nANNÉE PAR ANNÉE : l'écart du cas type parti chaque année à la série du jaune")
    for code in SERIES:
        siennes = [m for m in mesures if m.cas_type == code]
        if not siennes:
            continue
        print(f"\n{code}")
        for indicateur in SERIES[code]:
            ligne = [m for m in siennes if m.indicateur == indicateur]
            ecarts = " ".join(f"{m.annee}:{m.ecart:+.2f}" if indicateur.startswith("age")
                              else f"{m.annee}:{m.ecart_relatif:+.1%}" for m in ligne)
            print(f"  {libelles[indicateur]:34} ({ligne[0].tableau}) {ecarts}")


def imprimer_le_stock(stock: dict[str, dict[int, float]],
                      publies: dict[tuple[str, str, str, str, str], float]) -> None:
    print("\nLE STOCK PESÉ COMME LA PAGE : la pension mensuelle moyenne servie, en euros "
          "courants,\nface au stock de droit direct du jaune (A-4, accessoires compris ; "
          "A-5, avantage principal)")
    for code, serie in stock.items():
        publie = stock_publie(code, publies)
        print(f"\n{code} ({REGIMES_DU_STOCK[code]})")
        for annee, pension in serie.items():
            accessoires, principal = publie[annee]
            texte = f"  {annee} : {pension:7.0f} €"
            if accessoires:
                texte += f", {accessoires:5.0f} € au A-4 ({pension / accessoires - 1:+.1%})"
            if principal:
                texte += f", {principal:5.0f} € au A-5 ({pension / principal - 1:+.1%})"
            print(texte)


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    analyseur.add_argument("--json", type=Path, help="écrit aussi le tableau dans ce fichier")
    options = analyseur.parse_args(argv)
    parametres = Parametres()
    mesures = mesures_du_depot(parametres)
    imprimer(mesures)
    annuelles = mesures_annuelles_du_depot(parametres)
    imprimer_les_annees(annuelles)
    stock = stock_du_depot(parametres)
    imprimer_le_stock(stock, referents_publies())
    if options.json:
        options.json.write_text(json.dumps({
            "flux_2025": [asdict(m) for m in mesures],
            "annees": [asdict(m) for m in annuelles],
            "stock": {code: {str(a): v for a, v in serie.items()}
                      for code, serie in stock.items()},
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
