"""Ce que les étapes du droit partagent avec la liquidation.

La dernière année d'un régime, que l'acquisition et la liquidation lisent ;
la période qui liquide une pension, à sa date d'effet ;
la date d'effet d'une demande ; ce qu'est une année cotisée, que l'ouverture,
le compte des durées et les départs lisent ;
la pension d'un régime, que « liquider chaque régime » écrit et que
« compléter tous régimes » relève ; l'avantage non contributif, que la
cascade des avantages mesure et que les deux étapes qui complètent
appliquent.

Son jumeau est ``moteur/js/droit/commun.js``.
"""

from __future__ import annotations


from ..calendrier import DateMois, date_d_effet  # noqa: F401  (logée au calendrier, action 161)
from ..types_du_pont.droit import AvantageApplique, PensionRegime  # noqa: F401  (types du pont, action 161)


#: Les complémentaires que leurs statuts font demander à leur âge, sans la
#: base : chacune forme une unité à elle. La CARPV, « dès leur soixantième
#: anniversaire », sous la seule condition d'« avoir versé les cotisations
#: exigibles de l'ensemble des régimes appelés par la CARPV » (statuts
#: approuvés le 18 octobre 2021, articles 33 et 34, en vigueur le 1er janvier
#: 2022 ; règlement de 2026, articles 1er et 2) — avant 2022, la séparation
#: est présumée, les statuts n'étant publiés qu'au Bulletin officiel (fiche
#: liquidation_regime_par_regime, approximations) ; la
#: CAVEC, « entre 60 et 65 ans, avec application d'un abattement définitif de
#: 1,25 % par trimestre manquant » (statuts de 2008, article 3.13 ; de 2018,
#: partie 2, article 12 ; règlement de 2026, article 1.1.3). Ni leurs textes,
#: ni L. 643-3, ni L. 644-1 ne les lient à la liquidation de la base. La
#: CRPNPAC, ses deux tranches : « Une pension de retraite est servie à
#: l'affilié [...] dès lors qu'il réunit cumulativement à la date d'effet de
#: la pension les conditions suivantes : 1° Avoir atteint l'âge de cinquante
#: ans ; 2° Justifier de vingt annuités » (code de l'aviation civile,
#: R. 426-11, I, rédaction de 2012), sans rien demander du régime général,
#: qui attend l'âge de L. 161-17-2 (L. 351-1). La CAVOM, « 1° À partir de 62
#: ans » et, « pour les générations antérieures », dès 60 ans (statuts,
#: articles 14 et 23, arrêté du 30 décembre 2015 ; article 14, arrêté du
#: 12 décembre 2024) ; la CARPIMKO, « l'âge prévu par les dispositions des
#: articles 3, 4 et 6 » (règlement de 2026, article 2), dès 60 ans pour les
#: générations 1955 et antérieures (article 12 quater des statuts depuis
#: l'arrêté du 31 juillet 2015) ; la CPRN, 60 ans pour les nés avant 1954, et
#: « l'article L. 161-17-2 [...] différé de vingt-quatre mois » après (statuts,
#: article 15, arrêté du 16 décembre 2013, en vigueur de 2014 à 2023) : chacune
#: à son âge, avant la base ou après.
SANS_LEUR_BASE = frozenset({"carpv_complementaire", "cavec_complementaire",
                            "cavom_complementaire", "carpimko_complementaire",
                            "cprn_complementaire",
                            "crpnpac", "crpnpac_tranche_2"})


def derniere_annee(regime) -> int:
    """Dernière année pour laquelle le régime a des paramètres."""
    annees = [p.fin if p.fin is not None else 9999 for p in regime.periodes]
    return min(max(annees), 2100) if annees else 2100


def periode_de_liquidation(regime, date: DateMois):
    """La période de ``regime`` qui liquide une pension prenant effet le 1er
    du mois ``date`` : celle dont les dates d'effet le comprennent, au jour
    quand un texte coupe l'année (``PeriodeRegime.effet`` ;
    docs/architecture.md, § 4.6), et sinon celle de l'année. Après la
    dernière année du régime, celle de cette dernière année. ``None`` quand
    aucune ne la couvre."""
    derniere = derniere_annee(regime)
    if date.annee > derniere:
        return regime.periode(derniere)
    return regime.periode_a_l_effet(f"{date.annee:04d}-{date.mois:02d}-01")


def ligne_cotisee(moteur, carriere, ligne) -> bool:
    """La ligne compte-t-elle parmi les trimestres COTISÉS ?

    Une année d'emploi, sauf celle que tous ses régimes valident sans
    cotisation : l'activité cultuelle d'avant 1979, que la CAVIMAC valide
    gratuitement (:meth:`~retraite_notionnelle.carriere.Affiliations.validee_sans_cotisation`).
    La carrière longue et le minimum contributif majoré lisent ce compte."""
    return ligne.cotise and not moteur.affiliations.validee_sans_cotisation(
        ligne.affiliation, ligne.annee,
        moteur.affiliations.date_entree(carriere, ligne.affiliation, ligne.annee))


def majoration_du_conjoint(etapes, quand: str) -> float:
    """La majoration pour conjoint à charge que les étapes d'une pension
    servent à ``quand`` (AAAA-MM-JJ) : celle de la dernière commencée, rien
    avant la première."""
    servie = 0.0
    for depuis, montant in etapes:
        if depuis <= quand:
            servie = montant
    return servie


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


def parts_sans_anticipation(avantages) -> list[tuple[str, float]]:
    """Les parts de la majoration pour enfants nés ou élevés, régime par
    régime, sans le coefficient d'anticipation qui a pu réduire celle de la
    date d'effet, sous le même plafond
    (``AvantageApplique.par_regime_sans_anticipation``) : celle que la
    réversion de l'Agirc-Arrco reprend depuis 2019 (circulaire 2020-02-DRJ,
    fiche 6, I.1.2.2)."""
    return [part for avantage in avantages if avantage.code == MAJORATION_ENFANTS
            for part in avantage.par_regime_sans_anticipation]


def fusionner_les_charges(une, autre) -> tuple[tuple[str, tuple[tuple[str, float], ...]], ...]:
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
