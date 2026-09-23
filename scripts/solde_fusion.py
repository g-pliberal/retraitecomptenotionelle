#!/usr/bin/env python3
"""Le solde 2026-2070 des scénarios 2 à 6 sous quatre régimes uniques.

    python scripts/solde_fusion.py                      # A à D, les deux conventions
    python scripts/solde_fusion.py --hypotheses A B     # les deux qui se ressemblent
    python scripts/solde_fusion.py --convention rapport # tout reconduit sauf le taux
    python scripts/solde_fusion.py --json solde.json    # la série complète, année par année

CE QU'IL MESURE
---------------
La page Coût confronte chaque système aux ressources du système actuel, et
ne fait suivre la recette au TAUX que pour le scénario 6, qui pose 18 %. Les
scénarios 2 à 5, eux, fusionnent tous les régimes à la bascule dans un régime
unique dont ``moteur/fusion.py`` retient le taux du statut pivot privé — et
ce régime unique change aussi ce qui est PRÉLEVÉ : l'artisan cotise 25,8 %
au lieu de 9, l'État 15 % du traitement au lieu de 82. La page ne le compte
pas. Ce script le compte, et refait le solde sous quatre barèmes du régime
unique, pour dire lequel tient :

    A  le régime unique du modèle : le taux du statut pivot, déplafonné ;
    B  le statut du salarié du privé généralisé à tous, avec ses tranches et
       son plafond de huit PASS — le « cas médian » ;
    C  le régime général seul, plafonné à un PASS ;
    D  la moyenne des taux de tous les régimes (``CritereTaux.MOYENNE_PONDEREE``).

Les âges, la durée et le salaire de référence du régime unique ne sont lus
par aucun compte notionnel : seuls le taux, sa part salariale et l'assiette
font un résultat. C'est pourquoi B ne diffère de A que par le plafond.

COMMENT LA RECETTE SUIT LE TAUX
-------------------------------
Deux conventions, celles que ``cout.py`` tient déjà pour le scénario 6 :

``assiette`` — la règle du programme. Après la bascule, la recette d'un
    scénario notionnel est son taux effectif appliqué à l'assiette mesurée
    des revenus d'activité, plus les transferts et autres produits, moins ce
    que la CNAF et l'Unédic versent pour des droits qu'il ne sert plus. La
    contribution d'équilibre de l'État, les subventions d'équilibre et les
    impôts affectés ne sont pas reconduits — ``SoldeAnnuel.ressources_de``
    dit pourquoi, et la même règle vaut ici pour les scénarios 2 à 6.
``rapport`` — tout est reconduit sauf le taux : la part cotisée des
    ressources est multipliée par le rapport de ce que le régime unique
    prélève sur les carrières de la grille à ce que le droit en vigueur y
    prélève ; les impôts affectés et les subventions restent.

Le taux effectif est lu sur la grille des cas types, pondérée par les
cotisants de chaque caisse : cotisations du régime unique divisées par les
revenus. Sous A et D il est le taux lui-même ; sous B et C, il porte l'effet
du plafond sur les treize carrières, et non sur la distribution nationale
des salaires — une borne, pas une mesure.

CE QUI NE CHANGE PAS
--------------------
Le scénario 6 : ses 18 % remplacent le régime unique après la bascule, et sa
recette est déjà celle du programme. Le scénario 1 : il encaisse tout, et son
solde reste celui du COR. Les réserves des régimes : hors compte, comme sur
la page. Le coefficient d'équilibre : calculé, jamais appliqué.

CE QU'IL EMPRUNTE
-----------------
Trois points d'entrée privés de ``cout.py`` — ``_pensionnes``,
``_rapports_recettes`` et ``SoldeAnnuel.ressources_de`` —, remplacés le temps
d'un calcul par :class:`RegimeUniqueVariante` et rendus ensuite, comme
``mortalite_population.py`` emprunte ``_pensionnes``. Le taux du régime
unique est substitué de la même façon dans ``ConstructeurCompte.taux_unifie``.
Rien ici n'est porté dans ``moteur/js/`` : la page Coût du site garde sa
convention, et la feuille de route dit ce qu'il faudrait pour l'y mettre.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from retraite_notionnelle import cout as C  # noqa: E402
from retraite_notionnelle.config import (  # noqa: E402
    Parametres, PartCotisation, SourceCotisations,
)
from retraite_notionnelle.donnees.assiette import AssietteActivite  # noqa: E402
from retraite_notionnelle.donnees.chargement import Fiabilite  # noqa: E402
from retraite_notionnelle.donnees.depenses import DepensesRetraite  # noqa: E402
from retraite_notionnelle.donnees.equilibre import ComptesRetraite  # noqa: E402
from retraite_notionnelle.donnees.population import Population  # noqa: E402
from retraite_notionnelle.donnees.regimes import CatalogueRegimes  # noqa: E402
from retraite_notionnelle.moteur.compte import ConstructeurCompte  # noqa: E402
from retraite_notionnelle.moteur.fusion import (  # noqa: E402
    CritereTaux, RegleFusion, fusionner,
)
from retraite_notionnelle.simulateur import Simulateur  # noqa: E402

#: Les scénarios dont le régime unique fixe le taux après la bascule.
SCENARIOS_FUSION: tuple[str, ...] = (
    "notionnel_retroactif", "notionnel_prospectif",
    "notionnel_retroactif_employeur", "notionnel_prospectif_employeur",
)
#: Clés ajoutées aux masses de cotisations : ce que le régime unique prélève
#: sur la grille, et les revenus sur lesquels il le prélève.
FUSION = "regime_unique"
REVENU = "revenu_regime_unique"
#: Clé, dans ``rapports_recettes``, du taux effectif lu sur la grille.
TAUX_EFFECTIF = "taux_effectif_regime_unique"

CONVENTIONS: tuple[str, ...] = (C.CONVENTION_ASSIETTE, C.CONVENTION_RAPPORT)
ANNEES_AFFICHEES: tuple[int, ...] = (2026, 2030, 2040, 2050, 2060, 2070)

#: Une tranche du barème : borne haute en PASS (``None`` : sans plafond),
#: taux total, taux à la charge de l'assuré.
Tranche = tuple[float | None, float, float]


@dataclass(frozen=True)
class Hypothese:
    lettre: str
    libelle: str
    #: ``None`` : le régime unique du modèle, tel que ``fusionner`` le rend.
    bareme: tuple[Tranche, ...] | None

    @property
    def taux_affiche(self) -> float:
        """Le taux de la première tranche, celui que le plus grand nombre paie."""
        return self.bareme[0][1] if self.bareme else 0.0


def hypotheses(catalogue: CatalogueRegimes, annee: int) -> dict[str, Hypothese]:
    """Les quatre barèmes, lus dans le catalogue de l'année de bascule."""
    general = min(catalogue["regime_general"].periodes_actives(annee),
                  key=lambda p: p.bornes_assiette_en_pass()[0])
    tranche_1, tranche_2 = sorted(
        catalogue["agirc_arrco"].periodes_actives(annee),
        key=lambda p: p.bornes_assiette_en_pass()[0],
    )[:2]
    plafonne = general.taux_cotisation_retraite
    plafonne_salarie = general.taux_cotisation_salarie
    deplafonne = general.taux_cotisation_deplafonnee
    deplafonne_salarie = deplafonne * general.part_salariale_deplafonnee
    modele = fusionner(catalogue, annee)
    moyenne = fusionner(catalogue, annee,
                        RegleFusion(critere_taux=CritereTaux.MOYENNE_PONDEREE))
    return {
        "A": Hypothese(
            "A", f"le régime unique du modèle : {modele.taux_cotisation_retraite:.2%} déplafonné",
            None,
        ),
        "B": Hypothese(
            "B", "le salarié du privé généralisé : tranches, plafond 8 PASS", (
                (1.0, plafonne + deplafonne + tranche_1.taux_cotisation_retraite,
                 plafonne_salarie + deplafonne_salarie + tranche_1.taux_cotisation_salarie),
                (8.0, deplafonne + tranche_2.taux_cotisation_retraite,
                 deplafonne_salarie + tranche_2.taux_cotisation_salarie),
                (None, deplafonne, deplafonne_salarie),
            ),
        ),
        "C": Hypothese(
            "C", "le régime général seul : plafond 1 PASS", (
                (1.0, plafonne + deplafonne, plafonne_salarie + deplafonne_salarie),
                (None, deplafonne, deplafonne_salarie),
            ),
        ),
        "D": Hypothese(
            "D", f"la moyenne des régimes : {moyenne.taux_cotisation_retraite:.2%} déplafonné",
            ((None, moyenne.taux_cotisation_retraite, moyenne.taux_cotisation_salarie),),
        ),
    }


def taux_du_bareme(bareme: tuple[Tranche, ...], revenu: float, pass_annuel: float
                   ) -> tuple[float, float]:
    """Taux total et taux salarié effectifs d'un revenu annuel sous un barème."""
    if revenu <= 0.0:
        return 0.0, 0.0
    total = salarie = basse = 0.0
    for haute, taux, taux_salarie in bareme:
        plafond = revenu if haute is None else min(revenu, haute * pass_annuel)
        tranche = max(0.0, plafond - basse)
        total += tranche * taux
        salarie += tranche * taux_salarie
        basse = plafond
        if haute is not None and revenu <= haute * pass_annuel:
            break
    return total / revenu, salarie / revenu


class RegimeUniqueVariante:
    """Le temps d'un calcul : un autre barème, et une recette qui le suit.

    Rend à ``cout.py`` et à ``ConstructeurCompte`` leurs attributs à la sortie,
    quoi qu'il arrive. ``convention`` est modifiable entre deux lectures du
    solde — le stock de pensions ne dépend pas de la recette.
    """

    def __init__(self, hypothese: Hypothese,
                 convention: str = C.CONVENTION_ASSIETTE) -> None:
        self.hypothese = hypothese
        self.convention = convention
        self._sauvegarde: dict[str, object] = {}

    # -- le taux du régime unique -------------------------------------------

    def _taux_unifie(self, original):
        bareme = self.hypothese.bareme

        def taux_unifie(constructeur, ligne, annee, regime_fusionne):
            if (bareme is None or constructeur.parametres.source_cotisations
                    is not SourceCotisations.TAUX_HISTORIQUES):
                return original(constructeur, ligne, annee, regime_fusionne)
            revenu = ligne.revenu if ligne.cotise else ligne.revenu_reference
            revenu /= max(ligne.fraction_annee, 1e-9)
            unifie, salarie = taux_du_bareme(
                bareme, revenu, constructeur.macro.plafond_securite_sociale(annee))
            if not constructeur.a_un_employeur(ligne, annee):
                salarie = unifie
            if constructeur.parametres.part_cotisation is PartCotisation.SALARIALE:
                return salarie, 0.0, "", Fiabilite.CERTIFIEE
            return unifie, unifie - salarie, "", Fiabilite.CERTIFIEE
        return taux_unifie

    # -- la recette suit le taux -------------------------------------------

    @staticmethod
    def _pensionnes(original):
        def pensionnes(simulateur, cas_types, liquidation="droit"):
            # La grille est calculée une fois : ``_pensionnes`` la demande, et
            # on la relit ici pour le compte du scénario 4 — taux réels avant
            # la bascule, régime unique après, part totale.
            memo: dict = {}
            calculer = C.calculer_cas_types

            def memorisee(*args, **kwargs):
                if "grille" not in memo:
                    memo["grille"] = calculer(*args, **kwargs)
                return memo["grille"]
            C.calculer_cas_types = memorisee
            try:
                pensionnes, motifs = original(simulateur, cas_types, liquidation)
                grille = memorisee(simulateur, cas_types, C.generations(), liquidation)
            finally:
                C.calculer_cas_types = calculer
            complets = []
            for pensionne in pensionnes:
                comparaison = grille.resultats[(pensionne.code, pensionne.generation)]
                lignes = comparaison.notionnel_retroactif_employeur.compte.cotisations
                cotisations = dict(pensionne.cotisations)
                cotisations[FUSION] = {l.annee: l.cotisation for l in lignes}
                cotisations[REVENU] = {l.annee: l.revenu for l in lignes}
                complets.append(dataclasses.replace(pensionne, cotisations=cotisations))
            return complets, motifs
        return pensionnes

    @staticmethod
    def _rapports_recettes(original):
        def rapports_recettes(masses, annee, bascule):
            rapports = original(masses, annee, bascule)
            reference = masses[C.TAUX_REELS]
            if annee >= bascule and reference > 0.0:
                for scenario in SCENARIOS_FUSION:
                    rapports[scenario] = masses[FUSION] / reference
                revenus = masses[REVENU]
                rapports[TAUX_EFFECTIF] = masses[FUSION] / revenus if revenus > 0.0 else 0.0
            return rapports
        return rapports_recettes

    def _ressources_de(self, original):
        variante = self

        def ressources_de(ligne, scenario):
            taux = ligne.rapports_recettes.get(TAUX_EFFECTIF, 0.0)
            if (scenario in SCENARIOS_FUSION
                    and variante.convention == C.CONVENTION_ASSIETTE
                    and taux > 0.0
                    and ligne.convention_recette == C.CONVENTION_ASSIETTE
                    and ligne.taux_prelevement > 0.0
                    and 0 < ligne.annee_bascule <= ligne.annee):
                # La même règle que le scénario 6, à son taux près.
                pleine = ligne.ressources * taux / ligne.taux_prelevement
                autres = ligne.ressources * (1.0 - ligne.part_contributive
                                             - ligne.part_subventions
                                             - ligne.part_impots)
                return pleine + autres - (ligne.retrait - ligne.retrait_par_impot)
            return original(ligne, scenario)
        return ressources_de

    def __enter__(self) -> "RegimeUniqueVariante":
        self._sauvegarde = {
            "taux_unifie": ConstructeurCompte.taux_unifie,
            "CLES_RECETTES": C.CLES_RECETTES,
            "_pensionnes": C._pensionnes,
            "_rapports_recettes": C._rapports_recettes,
            "ressources_de": C.SoldeAnnuel.ressources_de,
            "_tva_affectee": C.SoldeAnnuel._tva_affectee,
        }
        ConstructeurCompte.taux_unifie = self._taux_unifie(ConstructeurCompte.taux_unifie)
        C.CLES_RECETTES = C.CLES_RECETTES + (FUSION, REVENU)
        C._pensionnes = self._pensionnes(C._pensionnes)
        C._rapports_recettes = self._rapports_recettes(C._rapports_recettes)
        C.SoldeAnnuel.ressources_de = self._ressources_de(C.SoldeAnnuel.ressources_de)
        # Les variantes comparent des TAUX DE COTISATION sous les mêmes règles
        # de recette. La TVA à taux unique que la proposition affecte à sa
        # retraite depuis le 23 septembre 2026 n'en est pas un : la laisser au
        # seul scénario 6 ferait lire son produit, plus de deux points de PIB,
        # comme une économie des 18 %. Elle est donc tenue hors de la
        # comparaison, le temps du contexte.
        C.SoldeAnnuel._tva_affectee = lambda ligne, scenario: 0.0
        return self

    def __exit__(self, *exc) -> None:
        ConstructeurCompte.taux_unifie = self._sauvegarde["taux_unifie"]
        C.CLES_RECETTES = self._sauvegarde["CLES_RECETTES"]
        C._pensionnes = self._sauvegarde["_pensionnes"]
        C._rapports_recettes = self._sauvegarde["_rapports_recettes"]
        C.SoldeAnnuel.ressources_de = self._sauvegarde["ressources_de"]
        C.SoldeAnnuel._tva_affectee = self._sauvegarde["_tva_affectee"]


# -- le calcul ---------------------------------------------------------------


@dataclass
class Lecture:
    """Le solde d'un système sous une hypothèse et une convention."""

    soldes: dict[int, float]
    ressources: dict[int, float]
    depenses: dict[int, float]
    coefficients: dict[int, float]
    solde_moyen: float
    solde_moyen_debut: float
    solde_moyen_fin: float
    premiere_annee_equilibree: int | None
    dette_horizon: float
    pic_dette: tuple[int, float] | None


@dataclass
class Resultat:
    hypothese: Hypothese
    taux_effectif: float
    rapport_recette: float
    echecs: dict[str, int]
    lectures: dict[str, dict[str, Lecture]] = field(default_factory=dict)
    #: Le coût complet, gardé pour qui veut lire les années observées ; il
    #: n'est pas écrit dans le JSON.
    cout: C.Cout | None = None


def calculer(hypothese: Hypothese, simulateur: Simulateur,
             depenses: DepensesRetraite, population: Population,
             comptes: ComptesRetraite, assiette: AssietteActivite,
             conventions: tuple[str, ...] = CONVENTIONS,
             annee_lecture: int = 2030) -> Resultat:
    """Le solde de chaque système sous ``hypothese``, convention par convention."""
    with RegimeUniqueVariante(hypothese) as variante:
        cout = C.calculer_cout(simulateur, depenses, population, comptes,
                               assiette=assiette)
        ligne = cout.avenir.annee(annee_lecture)
        resultat = Resultat(
            hypothese=hypothese,
            taux_effectif=ligne.rapports_recettes.get(TAUX_EFFECTIF, 0.0),
            rapport_recette=ligne.rapports_recettes.get("notionnel_prospectif", 1.0),
            echecs=cout.echecs,
            cout=cout,
        )
        milieu = (2026 + C.HORIZON) // 2
        for convention in conventions:
            variante.convention = convention
            dette = C.calculer_dette(cout.solde, cout.avenir, simulateur.courbe_taux,
                                     dette_publique=comptes.dette_publique)
            solde = cout.solde
            lectures: dict[str, Lecture] = {}
            for scenario, _ in C.SCENARIOS:
                pic = dette.pic(scenario)
                lectures[scenario] = Lecture(
                    soldes={l.annee: l.solde(scenario) for l in solde.projetees()},
                    ressources={l.annee: l.ressources_de(scenario) for l in solde.projetees()},
                    depenses={l.annee: l.depense(scenario) for l in solde.projetees()},
                    coefficients={l.annee: l.coefficient(scenario) for l in solde.projetees()},
                    solde_moyen=solde.solde_moyen(scenario, 2026, C.HORIZON),
                    solde_moyen_debut=solde.solde_moyen(scenario, 2026, milieu),
                    solde_moyen_fin=solde.solde_moyen(scenario, milieu + 1, C.HORIZON),
                    premiere_annee_equilibree=solde.premiere_annee_equilibree(scenario),
                    dette_horizon=dette.horizon(scenario),
                    pic_dette=(pic.annee, pic.stock(scenario)) if pic else None,
                )
            resultat.lectures[convention] = lectures
    return resultat


# -- l'impression ------------------------------------------------------------

LIBELLES = {
    "actuel": "1 système actuel",
    "notionnel_retroactif": "2 rétroactif, salariale",
    "notionnel_prospectif": "3 prospectif, salariale",
    "notionnel_retroactif_employeur": "4 rétroactif, totale",
    "notionnel_prospectif_employeur": "5 prospectif, totale",
    "notionnel_liberal": "6 proposition, 18 %",
}


def tableau(resultat: Resultat, convention: str,
            annees: tuple[int, ...] = ANNEES_AFFICHEES) -> str:
    lectures = resultat.lectures[convention]
    milieu = (2026 + C.HORIZON) // 2
    entete = (f"{'système':<26}" + "".join(f"{a:>8}" for a in annees)
              + f"{'moy.':>8}{f'26-{milieu % 100}':>8}{f'{milieu % 100 + 1}-70':>8}"
              + f"{'équil.':>8}{'dette70':>9}{'coef70':>8}")
    lignes = [
        f"{resultat.hypothese.lettre} — {resultat.hypothese.libelle}",
        f"  taux effectif sur la grille en 2030 : {resultat.taux_effectif:.2%} ; "
        f"rapport de recette : {resultat.rapport_recette:.3f} ; convention « {convention} »",
        "  solde en points de PIB ; dette : stock accumulé à l'horizon, en points de PIB",
        entete, "-" * len(entete),
    ]
    for scenario, _ in C.SCENARIOS:
        lecture = lectures[scenario]
        equilibre = lecture.premiere_annee_equilibree
        lignes.append(
            f"{LIBELLES[scenario]:<26}"
            + "".join(f"{lecture.soldes[a] * 100:>+8.2f}" for a in annees)
            + f"{lecture.solde_moyen * 100:>+8.2f}{lecture.solde_moyen_debut * 100:>+8.2f}"
            + f"{lecture.solde_moyen_fin * 100:>+8.2f}"
            + f"{str(equilibre) if equilibre else '—':>8}"
            + f"{lecture.dette_horizon * 100:>+9.0f}{lecture.coefficients[C.HORIZON]:>8.2f}"
        )
    return "\n".join(lignes)


def en_dictionnaire(resultat: Resultat) -> dict:
    return {
        "hypothese": dataclasses.asdict(resultat.hypothese),
        "taux_effectif_2030": resultat.taux_effectif,
        "rapport_recette_2030": resultat.rapport_recette,
        "echecs": resultat.echecs,
        "conventions": {
            convention: {scenario: dataclasses.asdict(lecture)
                         for scenario, lecture in lectures.items()}
            for convention, lectures in resultat.lectures.items()
        },
    }


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    analyseur.add_argument("--hypotheses", nargs="+", default=["A", "B", "C", "D"],
                           choices=["A", "B", "C", "D"])
    analyseur.add_argument("--convention", choices=CONVENTIONS + ("les-deux",),
                           default="les-deux")
    analyseur.add_argument("--json", type=Path, help="écrit la série complète")
    arguments = analyseur.parse_args(argv)
    conventions = CONVENTIONS if arguments.convention == "les-deux" else (arguments.convention,)

    parametres = Parametres()
    racine = parametres.racine_donnees
    simulateur = Simulateur(parametres)
    depenses, population = DepensesRetraite(racine), Population(racine)
    comptes, assiette = ComptesRetraite(racine), AssietteActivite(racine)
    toutes = hypotheses(simulateur.catalogue, parametres.annee_bascule)

    resultats = []
    for lettre in arguments.hypotheses:
        resultat = calculer(toutes[lettre], Simulateur(parametres), depenses,
                            population, comptes, assiette, conventions)
        resultats.append(resultat)
        for convention in conventions:
            print(tableau(resultat, convention))
            print()
    if arguments.json:
        arguments.json.write_text(json.dumps(
            {r.hypothese.lettre: en_dictionnaire(r) for r in resultats},
            indent=1, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
