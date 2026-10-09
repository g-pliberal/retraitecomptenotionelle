"""Ce que les étapes du droit partagent avec la liquidation.

La dernière année d'un régime, que l'acquisition et la liquidation lisent ;
la date d'effet d'une demande ; ce qu'est une année cotisée, que l'ouverture,
le compte des durées et les départs lisent ;
la pension d'un régime, que « liquider chaque régime » écrit et que
« compléter tous régimes » relève ; l'avantage non contributif, que la
cascade des avantages mesure et que les deux étapes qui complètent
appliquent.

Son jumeau est ``moteur/js/droit/commun.js``.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..donnees.chargement import Fiabilite


def derniere_annee(regime) -> int:
    """Dernière année pour laquelle le régime a des paramètres."""
    annees = [p.fin if p.fin is not None else 9999 for p in regime.periodes]
    return min(max(annees), 2100) if annees else 2100


def date_d_effet(carriere) -> str | None:
    """La date d'effet d'une demande (AAAA-MM-JJ) : le premier jour du mois de
    la liquidation, ou ``None`` pour une carrière sans départ."""
    if carriere.age_liquidation is None:
        return None
    date = carriere.date_liquidation
    return f"{date.annee:04d}-{date.mois:02d}-01"


def ligne_cotisee(moteur, carriere, ligne) -> bool:
    """La ligne compte-t-elle parmi les trimestres COTISÉS ?

    Une année d'emploi, sauf celle que tous ses régimes valident sans
    cotisation : l'activité cultuelle d'avant 1979, que la CAVIMAC valide
    gratuitement (:meth:`~retraite_notionnelle.carriere.Affiliations.validee_sans_cotisation`).
    La carrière longue et le minimum contributif majoré lisent ce compte."""
    return ligne.cotise and not moteur.affiliations.validee_sans_cotisation(
        ligne.affiliation, ligne.annee, carriere.date_entree(ligne.affiliation))


@dataclass(frozen=True)
class PensionRegime:
    """Pension annuelle brute servie par un régime."""

    regime: str
    montant: float
    type_calcul: str
    detail: str
    fiabilite: Fiabilite
    #: Quand les régimes liquident à des dates différentes
    #: (:mod:`~retraite_notionnelle.droit.departs`) : la date d'effet de cette
    #: pension (AAAA-MM-JJ), et son montant à cette date, dans ses euros. Le
    #: champ ``montant`` est alors celui du départ déclaré — la pension servie
    #: avant lui y est menée, celle qui commence après y est ramenée par les
    #: prix. ``None`` pour un départ unique, où tout liquide à la même date.
    date_effet: str | None = None
    montant_a_l_effet: float | None = None
    #: La prestation versée en une fois, sous le seuil de points d'un régime
    #: qui en a un (le RAFP, décret n° 2004-569, article 9), ou la petite
    #: pension que son régime remplace par un versement unique — le régime
    #: général, l'Agirc-Arrco, l'Ircantec (:func:`~.completer.verser_en_capital`)
    #: — : ce capital, en euros de la liquidation ; ``None`` pour une rente.
    #: ``montant`` reste la rente qu'il remplace, et la réversion sait qu'il
    #: n'y en a pas après lui quand sa fiche le dit (``rien_apres_un_capital``).
    capital: float | None = None
    #: La majoration pour conjoint à charge que la pension porte (L. 351-13),
    #: depuis chaque date où elle change : ``((date, montant), ...)``, en
    #: euros courants, sans revalorisation. Celle de la date d'effet est dans
    #: ``montant`` ; la revalorisation sert celle de chaque échéance
    #: (:func:`majoration_du_conjoint`, fiche ``majoration_conjoint_a_charge``).
    conjoint: tuple[tuple[str, float], ...] = ()
    #: Ce que la réversion du régime général lit du maximum des pensions
    #: (fiche ``pension_maximale_regime_general``), aux euros de ``montant`` :
    #: ce que le maximum a retiré de la pension calculée, que la réversion
    #: reprend, la caisse la calculant sur la pension « sans être comparé[e] au
    #: minimum et au maximum » ; ce que la surcote ajoute à la pension ramenée,
    #: que le maximum de la réversion laisse passer (circulaire Cnav n° 2018-4,
    #: § 5) ; le coefficient de l'ajournement d'avant 1983 ou du taux acquis au
    #: 31 mars 1983, qui multiplie le maximum « opposable à l'assuré »
    #: (circulaire n° 120/82, § 4).
    ecretement_du_maximum: float = 0.0
    surcote: float = 0.0
    coefficient_du_maximum: float = 1.0
    #: La pension a-t-elle été liquidée sur la durée d'assurance maximum que sa
    #: date d'effet prenait en compte — 120 trimestres avant 1972, 128 en 1972,
    #: 136 en 1973, 144 en 1974 — ? Les majorations forfaitaires de 1972 à 1982
    #: le lisent (fiche ``majorations_forfaitaires_1972_1982``).
    sur_la_duree_maximum: bool = False


def majoration_du_conjoint(etapes, quand: str) -> float:
    """La majoration pour conjoint à charge que les étapes d'une pension
    servent à ``quand`` (AAAA-MM-JJ) : celle de la dernière commencée, rien
    avant la première."""
    servie = 0.0
    for depuis, montant in etapes:
        if depuis <= quand:
            servie = montant
    return servie


@dataclass(frozen=True)
class AvantageApplique:
    """Effet en euros d'un avantage non contributif du droit positif.

    Les trois avantages s'appliquent dans cet ordre, et l'ordre compte : la
    MDA ajoute des trimestres, donc modifie la décote et la proratisation AVANT
    que la majoration ne multiplie, et le minimum ne comble qu'ensuite. Leurs
    effets s'additionnent exactement au total : c'est ce qui rend la cascade
    vérifiable ligne à ligne.
    """

    code: str
    libelle: str
    montant: float
    detail: str = ""
    #: Part de chaque régime, dans l'ordre des pensions, quand l'avantage se
    #: répartit entre eux — la majoration pour enfants, plafond compris, et le
    #: minimum contributif.
    par_regime: tuple[tuple[str, float], ...] = ()
    #: Ce que les enfants À CHARGE à la date d'effet ajoutent à la majoration
    #: pour enfants, régime par régime, depuis chaque date où leur nombre
    #: change, la première étant la date d'effet : ``((date, ((régime, part),
    #: ...)), ...)``. Les parts de la première sont dans ``par_regime`` ; elles
    #: cessent avec la charge (:func:`parts_de_la_majoration`, fiche
    #: ``majoration_enfants_a_charge_agirc_arrco``).
    a_charge: tuple[tuple[str, tuple[tuple[str, float], ...]], ...] = ()


#: Le code de la majoration pour enfants, que la revalorisation mène à chaque
#: échéance.
MAJORATION_ENFANTS = "majoration_enfants"


def _etape_au(etapes, quand: str) -> tuple[tuple[str, float], ...]:
    """Les parts de la dernière étape commencée à ``quand`` (AAAA-MM-JJ),
    celles de la première avant elle."""
    retenues = etapes[0][1]
    for depuis, parts in etapes:
        if depuis <= quand:
            retenues = parts
    return retenues


def parts_de_la_majoration(avantages, quand: str | None = None,
                           a_charge: bool = True) -> list[tuple[str, float]]:
    """Les parts de la majoration pour enfants, régime par régime : celles de
    la date d'effet, ou, à ``quand`` (AAAA-MM-JJ), celles qu'elle sert alors,
    les enfants à charge qui ne le sont plus retirés (``AvantageApplique.a_charge``).
    Sans ``a_charge``, celles des seuls enfants nés ou élevés, que la réversion
    lit (accord du 17 novembre 2017, article 109). Un régime peut y revenir :
    la part qu'elle perd s'y écrit en négatif."""
    parts: list[tuple[str, float]] = []
    for avantage in avantages:
        if avantage.code != MAJORATION_ENFANTS:
            continue
        parts.extend(avantage.par_regime)
        if avantage.a_charge and not a_charge:
            parts.extend((code, -part) for code, part in avantage.a_charge[0][1])
            continue
        if quand is None or not avantage.a_charge:
            continue
        servies = _etape_au(avantage.a_charge, quand)
        if servies is not avantage.a_charge[0][1]:
            parts.extend((code, -part) for code, part in avantage.a_charge[0][1])
            parts.extend(servies)
    return parts


def fusionner_les_charges(une, autre):
    """Les étapes de deux majorations pour enfants à charge réunies, celles de
    deux départs que le scénario additionne : à chaque date de l'une ou de
    l'autre, la somme de leurs parts."""
    if not une:
        return autre
    if not autre:
        return une
    dates = sorted({depuis for depuis, _ in une} | {depuis for depuis, _ in autre})
    return tuple((depuis, _etape_au(une, depuis) + _etape_au(autre, depuis))
                 for depuis in dates)
