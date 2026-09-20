"""Coefficient de conversion du capital notionnel en rente viagère.

La pension annuelle vaut ``capital_notionnel / diviseur``. Le diviseur est
l'espérance de vie résiduelle actualisée :

.. math::

   G(a, L) = \\sum_{t \\ge 0} \\; {}_t p_a \\; (1 + \\nu)^{-t}

où :math:`{}_t p_a` est la probabilité, pour un liquidant d'âge :math:`a` en
année :math:`L`, d'être encore en vie :math:`t` années plus tard, lue sur une
table de **génération**, et :math:`\\nu` le taux de préfinancement.

**Pourquoi :math:`\\nu = 0` par défaut.** Dans un système notionnel, la rente
est actualisée au taux auquel elle sera ensuite revalorisée. Ici les deux sont
le même taux — le triple lock inversé — et se compensent exactement. Le diviseur
se réduit alors à l'espérance de vie résiduelle, ce qui rend le résultat
directement lisible : « votre capital notionnel divisé par le nombre d'années
que vous êtes statistiquement appelé à vivre ». Donner à :math:`\\nu` une valeur
positive revient à verser davantage au début et moins ensuite, à espérance de
coût inchangée.

**Ce que le diviseur sanctionne tout seul.** Partir cinq ans plus tôt augmente
le diviseur d'environ 4 à 5 années d'espérance de vie, soit une pension annuelle
inférieure de 15 à 20 % — avant même de compter les cinq années de cotisations
manquantes. C'est ce mécanisme qui traduit la règle « parti trop tôt, pension
réduite » sans avoir besoin d'une décote administrative.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..carriere import Carriere, salaire_moyen_annuel
from ..config import (
    POPULATION_PAR_NIVEAU_DE_VIE,
    RATTACHEMENT_PENSION,
    Parametres,
    TableConversion,
)
from ..donnees.chargement import Fiabilite
from ..donnees.distribution import DistributionPensions
from ..donnees.macro import DonneesMacro
from ..donnees.mortalite import DonneesMortalite


def niveau_relatif(carriere: Carriere, macro: DonneesMacro) -> float:
    """Le niveau de salaire d'une carrière, en multiples du salaire moyen.

    La somme des revenus cotisés rapportée à la somme des salaires moyens des
    mêmes années, au prorata de la part d'année couverte. Pour une carrière
    paramétrique sans profil, c'est le ``niveau_salaire`` saisi ; pour un
    relevé, c'est ce que le relevé dit. Vaut un si rien n'est cotisé.
    """
    revenus = 0.0
    references = 0.0
    for ligne in carriere.lignes:
        if not ligne.cotise:
            continue
        revenus += ligne.revenu
        references += salaire_moyen_annuel(macro, ligne.annee) * ligne.fraction_annee
    return revenus / references if references > 0.0 else 1.0


@dataclass(frozen=True)
class CoefficientConversion:
    """Diviseur annuitaire et éléments qui l'expliquent."""

    diviseur: float
    age_liquidation: float
    annee_liquidation: int
    esperance_residuelle: float
    table: str
    taux_anticipe: float
    fiabilite: Fiabilite

    @property
    def taux_de_rente(self) -> float:
        """Fraction du capital notionnel servie chaque année."""
        return 1.0 / self.diviseur if self.diviseur else 0.0


class Convertisseur:
    """Produit les coefficients de conversion."""

    #: Tours de point fixe entre la pension et son vingtile, au plus. Le
    #: rattachement par la pension est monotone — un vingtile plus haut vit
    #: plus longtemps, sert moins, retombe plus bas —, si bien qu'il converge
    #: ou oscille entre deux vingtiles voisins ; six tours suffisent, et le
    #: dernier est retenu dans les deux cas, ce qui rend le résultat
    #: déterministe des deux côtés du portage.
    TOURS_POINT_FIXE = 6

    def __init__(self, mortalite: DonneesMortalite, parametres: Parametres,
                 macro: DonneesMacro | None = None,
                 distribution: DistributionPensions | None = None) -> None:
        self.mortalite = mortalite
        self.parametres = parametres
        #: Les séries macroéconomiques, pour rattacher une carrière à son
        #: vingtile de niveau de vie ; sans elles, le rattachement automatique
        #: retombe sur la table commune.
        self.macro = macro
        #: La distribution des pensions de la DREES, pour rattacher une
        #: carrière par le RANG de sa pension parmi les retraités.
        self.distribution = distribution

    @property
    def rattache_par_pension(self) -> bool:
        return (self.parametres.population_conversion == POPULATION_PAR_NIVEAU_DE_VIE
                and self.parametres.rattachement_niveau_de_vie == RATTACHEMENT_PENSION
                and self.macro is not None and self.distribution is not None)

    def population_par_pension(self, pension_annuelle: float, annee: int) -> str | None:
        """Le vingtile où une pension brute annuelle place son titulaire : son
        RANG parmi les retraités.

        Comparer une pension aux niveaux de vie de la population entière la
        classerait presque toujours en bas — une pension est plus petite qu'un
        salaire, et les vingtiles mêlent actifs et retraités —, alors que le
        niveau de vie moyen des retraités vaut celui de la population. La
        pension est donc rangée parmi les RETRAITÉS, dans la distribution des
        pensions brutes de droit direct de la DREES, ramenée aux euros du
        millésime de l'enquête au rythme du salaire moyen ; le vingtile est
        celui de ce rang. C'est supposer que le rang parmi les retraités par
        la pension est le rang par le niveau de vie, ce qui néglige le
        conjoint et le patrimoine.
        """
        if self.macro is None or self.distribution is None:
            return None
        mensuelle = pension_annuelle / 12.0
        ramenee = mensuelle * (salaire_moyen_annuel(self.macro, self.distribution.millesime)
                               / salaire_moyen_annuel(self.macro, annee))
        rang = self.distribution.part_sous(ramenee)
        vingtile = min(20, int(rang * 20.0) + 1)
        return f"niveau_de_vie_v{vingtile:02d}"

    def population_pour_pension(self, pension_annuelle: float, annee: int,
                                carriere: Carriere | None) -> str | None:
        """La population d'une carrière dont la pension est CONNUE — droit en
        vigueur, droits figés — : par la pension si c'est le rattachement,
        par la carrière sinon."""
        if self.rattache_par_pension:
            return self.population_par_pension(pension_annuelle, annee)
        return self.population_de(carriere)

    def resoudre(self, capital: float, age_liquidation: float, annee_liquidation: int,
                 sexe: str | None, mois_liquidation: int,
                 carriere: Carriere | None) -> tuple[CoefficientConversion, str | None]:
        """Le coefficient d'un capital notionnel, et la population retenue.

        Par le salaire, la population se lit sur la carrière et le coefficient
        s'ensuit. Par la pension, elle dépend de la pension, qui dépend du
        diviseur : on part de la table commune et on itère, ``TOURS_POINT_FIXE``
        fois au plus, jusqu'à ce que le vingtile de la pension servie soit
        celui qui l'a servie.
        """
        if not self.rattache_par_pension:
            population = self.population_de(carriere)
            return self.coefficient(age_liquidation, annee_liquidation, sexe,
                                    mois_liquidation, population), population
        population: str | None = None
        for _ in range(self.TOURS_POINT_FIXE):
            conversion = self.coefficient(age_liquidation, annee_liquidation, sexe,
                                          mois_liquidation, population)
            suivante = self.population_par_pension(capital / conversion.diviseur,
                                                   annee_liquidation)
            if suivante == population:
                break
            population = suivante
        return self.coefficient(age_liquidation, annee_liquidation, sexe,
                                mois_liquidation, population), population

    def population_de(self, carriere: Carriere | None) -> str | None:
        """La population dont la mortalité sert à cette carrière.

        C'est ici que ``population_conversion`` se lit : ``None`` est la
        table commune ; une clé nommée vaut pour tout le monde ; la valeur
        ``niveau_de_vie`` rattache la carrière au vingtile où son salaire la
        place (:meth:`DonneesMortalite.population_niveau_de_vie`).
        """
        choix = self.parametres.population_conversion
        if choix != POPULATION_PAR_NIVEAU_DE_VIE:
            return choix
        if carriere is None or self.macro is None:
            return None
        return self.mortalite.population_niveau_de_vie(niveau_relatif(carriere, self.macro))

    def _sexe_table(self, sexe: str | None) -> str | None:
        if self.parametres.table_conversion is TableConversion.UNISEXE:
            return None
        if sexe is None:
            raise ValueError(
                "table de conversion par sexe demandée mais sexe non renseigné"
            )
        return sexe

    def coefficient(self, age_liquidation: float, annee_liquidation: int,
                    sexe: str | None = None,
                    mois_liquidation: int = 1,
                    population: str | None = None) -> CoefficientConversion:
        """Diviseur annuitaire à une DATE de liquidation.

        ``mois_liquidation`` dit où la liquidation tombe dans son année civile,
        donc sous quel millésime de table le rentier passe chaque tronçon de sa
        première année de rente. Sans lui, la table sautait d'un millésime au
        1er janvier quand l'âge avançait mois par mois, et le diviseur remontait
        à cette date.

        ``population`` est ce que :meth:`population_de` a rendu pour la
        carrière. Sans elle, une population NOMMÉE dans les paramètres vaut
        quand même ; le rattachement par niveau de vie, lui, n'a rien à lire
        sans carrière et retombe sur la table commune.
        """
        sexe_table = self._sexe_table(sexe)
        generation = self.parametres.table_generation
        if population is None:
            population = self.population_de(None)
        date_liquidation = annee_liquidation + (mois_liquidation - 1) / 12
        courbe = self.mortalite.courbe(
            age_liquidation, date_liquidation, sexe_table, generation, population
        )

        nu = self.parametres.taux_anticipe_conversion
        diviseur = 0.0
        for t in range(len(courbe) - 1):
            # Rente supposée servie en continu sur l'année : on prend la survie
            # moyenne de début et de fin de période.
            survie_moyenne = 0.5 * (courbe[t] + courbe[t + 1])
            diviseur += survie_moyenne / ((1.0 + nu) ** (t + 0.5))

        if diviseur <= 0:
            raise ValueError(
                f"diviseur nul à {age_liquidation} ans en {annee_liquidation} : "
                "âge de liquidation hors des bornes de la table"
            )

        esperance = sum(
            0.5 * (courbe[t] + courbe[t + 1]) for t in range(len(courbe) - 1)
        )
        return CoefficientConversion(
            diviseur=diviseur,
            age_liquidation=age_liquidation,
            annee_liquidation=annee_liquidation,
            esperance_residuelle=esperance,
            table=("unisexe" if sexe_table is None else sexe_table)
            + ("_generation" if generation else "_moment")
            + ("" if population is None else f"_{population}"),
            taux_anticipe=nu,
            fiabilite=self.mortalite.fiabilite(annee_liquidation),
        )

    def effet_anticipation(self, age_anticipe: float, age_reference: float,
                           annee_liquidation: int, sexe: str | None = None,
                           mois_liquidation: int = 1,
                           population: str | None = None) -> float:
        """Rapport des pensions à capital notionnel donné, anticipé / à l'heure.

        Isole la seule sanction due à l'allongement de la durée de service.
        L'effet total d'un départ anticipé est plus fort, puisque s'y ajoutent
        les cotisations non versées.
        """
        anticipe = self.coefficient(
            age_anticipe, annee_liquidation, sexe, mois_liquidation, population
        )
        reference = self.coefficient(
            age_reference, annee_liquidation, sexe, mois_liquidation, population
        )
        return reference.diviseur / anticipe.diviseur
