"""La pension du régime des cultes, en deux fractions (fiche
``cultes_fractions_de_pension``).

La CAVIMAC ne liquide pas une pension, mais deux. Les périodes postérieures
au 31 décembre 1997 suivent les règles du régime général (L. 382-27) : un
salaire annuel moyen, fait du forfait du SMIC (R. 721-39-2), un taux, une
durée, et le minimum contributif. Les périodes antérieures gardent « les
conditions législatives et réglementaires en vigueur au 31 décembre 1997 »
(même article) : une pension « calculée sur des bases forfaitaires, en
fonction de la durée d'assurance » (L. 721-6 de 1985), égale au maximum de
l'année au prorata de cent cinquante trimestres (D. 721-7), sur des
trimestres qui comprennent les années d'activité cultuelle d'avant la
création du régime, validées gratuitement (D. 721-11 ; décret n° 79-607,
art. 42). Le modèle appliquait les règles de 1998 à toute la carrière, et ne
comptait pas les années d'avant 1979.

Le décret n° 2006-1325 (art. 2) adapte cette fraction aux pensions prenant
effet à compter du 1er novembre 2006 : la durée maximale de R. 351-6 au lieu
de cent cinquante trimestres (III), la décote du régime général à qui part
avant le taux plein (II), la surcote (IV), et, au taux plein, une majoration
qui porte les trimestres cotisés de 1979 à 1997 au minimum contributif majoré
— une part de l'écart pour les générations nées de 1939 à 1942, tout l'écart
ensuite (V). Depuis le 1er février 2010, une seconde majoration porte de même
les trimestres d'avant 1979 au minimum contributif (V bis, décret
n° 2010-103). La caisse l'écrit : à taux plein, « votre pension sera portée
au niveau du minimum contributif » ; à taux minoré, les deux fractions
« seront portées au niveau du montant maximum de la pension « Cavimac » et
vous aurez de plus une décote ».

Le jumeau de ce module est ``moteur/js/droit/cultes.js``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..donnees.chargement import Fiabilite
from ..somme import somme_ordonnee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..scenarios.actuel import ScenarioActuel
    from .compter import Durees

#: L'alignement : les périodes d'assurance antérieures au 1er janvier 1998
#: gardent les règles du 31 décembre 1997 (L. 721-6 de 1998, L. 382-27).
ALIGNEMENT = 1998

#: La création du régime : les années d'activité d'avant sont validées
#: gratuitement (D. 721-11 du code de 1985).
CREATION = 1979

#: D. 721-7 du code de 1985 : le maximum s'acquiert à cent cinquante
#: trimestres, et sous huit l'assuré « a droit au remboursement des
#: cotisations personnelles qu'il a payées », non à une pension.
DUREE_DU_MAXIMUM = 150
DUREE_MINIMALE = 8

#: Les dates d'effet, (année, mois), à compter desquelles valent le décret
#: n° 2006-1325, puis son V bis (décret n° 2010-103, art. 2 : les pensions
#: « prenant effet à compter du premier jour du mois suivant la date de sa
#: publication », le 30 janvier 2010).
DECRET_DE_2006 = (2006, 11)
DECRET_DE_2010 = (2010, 2)

#: Le V : la part de l'écart que reçoivent les générations de la montée en
#: charge ; rien avant 1939, l'écart entier après 1942.
PART_DE_L_ECART = {1939: 0.2, 1940: 0.4, 1941: 0.6, 1942: 0.8}

#: « si vous totalisez au moins 120 trimestres cotisés tous régimes, votre
#: pension sera portée au niveau du minimum contributif majoré » : la page de
#: la caisse, qui porte sinon les trimestres de 1979 à 1997 au minimum
#: contributif. C'est la condition du régime général (L. 351-10).
TRIMESTRES_COTISES_DU_MINIMUM_MAJORE = 120


@dataclass(frozen=True)
class DureesDesCultes:
    """Les trimestres de la CAVIMAC, rangés par fraction ; chaque année
    plafonnée à ses trimestres civils, comme toute durée d'un régime."""

    #: Les trimestres d'avant 1979, validés gratuitement.
    avant_1979: int
    #: Les trimestres d'assurance de 1979 à 1997, assimilés compris.
    de_1979_a_1997: int
    #: Ceux de ces derniers qui ont porté cotisation.
    cotises_de_1979_a_1997: int
    #: Les trimestres d'assurance depuis 1998, enfants compris.
    depuis_1998: int
    #: Ceux de ces derniers qui ont porté cotisation.
    cotises_depuis_1998: int

    @property
    def avant_1998(self) -> int:
        """La durée que la fraction d'avant 1998 proratise."""
        return self.avant_1979 + self.de_1979_a_1997


def durees(releve_durees: Durees, membres: tuple[str, ...],
           enfants: bool) -> DureesDesCultes:
    """Les trimestres de ``membres``, fraction par fraction.

    ``enfants`` dit si les trimestres des enfants que le régime porte entrent
    dans la fraction d'après 1997 : L. 382-27 renvoie à L. 351-4, que les
    règles de 1997 ne connaissaient pas — elles majoraient la pension d'un
    dixième pour trois enfants (D. 721-12), ce que le modèle sert ailleurs.
    """
    carriere = releve_durees.carriere

    def somme(table: str, depuis: int | None, avant: int | None) -> int:
        sommes: dict[int, int] = {}
        for membre in membres:
            for annee, trimestres in releve_durees.par_annee[table].get(membre, {}).items():
                if (depuis is None or annee >= depuis) and (avant is None or annee < avant):
                    sommes[annee] = sommes.get(annee, 0) + trimestres
        return somme_ordonnee(min(somme, carriere.plafond_trimestres(annee))
                   for annee, somme in sommes.items())

    hors_annee = (somme_ordonnee(releve_durees.hors_annee["assurance"].get(membre, 0)
                      for membre in membres) if enfants else 0)
    return DureesDesCultes(
        avant_1979=somme("assurance", None, CREATION),
        de_1979_a_1997=somme("assurance", CREATION, ALIGNEMENT),
        cotises_de_1979_a_1997=somme("cotises", CREATION, ALIGNEMENT),
        depuis_1998=somme("assurance", ALIGNEMENT, None) + hors_annee,
        cotises_depuis_1998=somme("cotises", ALIGNEMENT, None),
    )


def part_de_l_ecart(naissance: int) -> float:
    """La part de l'écart que le V du décret n° 2006-1325 donne à la
    génération : 20 % née en 1939, autant de plus chaque année, l'écart
    entier depuis 1943 ; rien avant 1939."""
    if naissance < 1939:
        return 0.0
    return PART_DE_L_ECART.get(naissance, 1.0)


@dataclass(frozen=True)
class FractionAvant1998:
    """La pension des périodes d'avant 1998, et ce qui la fait."""

    montant: float
    detail: str
    fiabilite: Fiabilite


def fraction_d_avant_1998(moteur: ScenarioActuel, carriere: Carriere,
                          duree: DureesDesCultes, proratisation: int,
                          taux_plein: bool, decote: float, surcote: float,
                          trimestres_cotises: int,
                          majorations: bool = True) -> FractionAvant1998 | None:
    """La pension des périodes d'avant 1998, ou ``None`` s'il n'y en a pas.

    ``proratisation`` est la durée maximale de R. 351-6 que le régime
    applique à la génération ; ``decote``, le facteur dont la décote réduit
    son taux — un au taux plein — ; ``surcote``, son coefficient de
    surcote ; ``trimestres_cotises``, ceux de la carrière, tous régimes.
    ``majorations`` faux retire les deux majorations : la cascade des
    avantages non contributifs les mesure, comme le minimum contributif
    qu'elles imitent.
    """
    trimestres = duree.avant_1998
    if trimestres < DUREE_MINIMALE:
        return None
    annee = carriere.annee_liquidation
    lu = moteur.maximum_des_cultes.valeur(annee)
    if lu is None:
        return None
    maximum, fiabilite = lu
    date_effet = (annee, carriere.mois_liquidation)
    if date_effet < DECRET_DE_2006:
        # Les règles du 31 décembre 1997, telles quelles : à soixante-cinq
        # ans, sans décote ni surcote, cent cinquante trimestres.
        retenus = min(trimestres, DUREE_DU_MAXIMUM)
        return FractionAvant1998(
            montant=maximum * retenus / DUREE_DU_MAXIMUM,
            detail=(f"avant 1998, maximum {maximum:,.2f} € "
                    f"× {retenus}/{DUREE_DU_MAXIMUM}"),
            fiabilite=fiabilite,
        )
    retenus = min(trimestres, proratisation)
    base = maximum * retenus / proratisation
    detail = f"avant 1998, maximum {maximum:,.2f} € × {retenus}/{proratisation}"
    if not taux_plein:
        # « à taux minoré, les fractions de pension avant 1979 et de 1979 à
        # 1997 seront portées au niveau du montant maximum de la pension
        # « Cavimac » et vous aurez de plus une décote ».
        if decote < 1.0:
            detail += f" × décote {decote:.4f}"
        return FractionAvant1998(montant=base * decote, detail=detail,
                                 fiabilite=fiabilite)
    montant = base * surcote
    if surcote > 1.0:
        detail += f" × surcote {surcote:.4f}"
    if not majorations:
        return FractionAvant1998(montant=montant, detail=detail, fiabilite=fiabilite)
    minimum, majore, _, fiabilite_minimum = moteur.minimum_contributif.valeurs(
        annee, carriere.mois_liquidation)
    # LES DEUX MAJORATIONS se partagent la durée maximale : les trimestres
    # cotisés de 1979 à 1997 d'abord, ceux d'avant 1979 dans ce qui reste.
    # Le décret ne dit pas comment s'additionnent ses deux prorata quand la
    # durée d'avant 1998 la dépasse ; les borner ensemble garde la pension
    # sous celle d'une carrière entière au minimum majoré.
    cotises = min(duree.cotises_de_1979_a_1997, proratisation)
    part = part_de_l_ecart(carriere.annee_naissance)
    majore_ouvert = trimestres_cotises >= TRIMESTRES_COTISES_DU_MINIMUM_MAJORE
    niveau = majore if majore_ouvert else minimum
    if part > 0 and cotises > 0 and niveau > maximum:
        majoration = part * (niveau - maximum) * cotises / proratisation
        montant += majoration
        fiabilite = min(fiabilite, fiabilite_minimum)
        qualificatif = " majoré" if majore_ouvert else ""
        if part < 1.0:
            qualificatif += f", {part:.0%} de l'écart"
        detail += (f" + {majoration:,.2f} € pour {cotises} trimestres cotisés de 1979 à "
                   f"1997 (minimum contributif{qualificatif})")
    if date_effet >= DECRET_DE_2010:
        avant_1979 = min(duree.avant_1979, max(0, proratisation - cotises))
        if avant_1979 > 0 and minimum > maximum:
            majoration = (minimum - maximum) * avant_1979 / proratisation
            montant += majoration
            fiabilite = min(fiabilite, fiabilite_minimum)
            detail += (f" + {majoration:,.2f} € pour {avant_1979} trimestres d'avant "
                       "1979 (minimum contributif)")
    return FractionAvant1998(montant=montant, detail=detail, fiabilite=fiabilite)
