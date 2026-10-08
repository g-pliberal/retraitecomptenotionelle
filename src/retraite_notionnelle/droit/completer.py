"""Compléter tous régimes (docs/architecture.md, § 7.3).

Ce que le droit ajoute aux pensions de régime en les regardant toutes
ensemble, dans l'ordre où il l'applique — et l'ordre commande le résultat :

* LE MINIMUM CONTRIBUTIF, qui ne relève que les pensions liquidées au taux
  plein, au prorata de la durée acquise dans chaque régime, et que
  l'article L. 173-2 écrête tous régimes confondus (:func:`complement_minimum`) ;
* LE MINIMUM GARANTI de la fonction publique, un barème sur la durée des
  services, qui se substitue à la pension quand il lui est supérieur ;
* LA SURCOTE PARENTALE, sur la pension relevée, pour les trimestres de
  l'année qui précède l'âge légal ;
* LA MAJORATION POUR ENFANTS, sur ce plancher, plafonnée en euros à la
  complémentaire (:func:`plafond_majoration`), et au traitement dans les
  régimes du code des pensions (:func:`majoration_sous_le_traitement`) ;
* LES DEUX MINIMA DES EXPLOITANTS AGRICOLES enfin, qui regardent toutes les
  pensions, majorations pour enfants comprises : la pension majorée de
  référence, qui relève leur pension de base (:func:`pension_majoree`), puis
  le complément différentiel de la RCO, qui porte leurs deux pensions
  agricoles à un pourcentage du SMIC net (:func:`complement_differentiel`) ;
* LES VERSEMENTS UNIQUES, en dernier, sur la pension complétée : la petite
  pension du régime général, de l'Agirc-Arrco ou de l'Ircantec, que son régime
  ne sert pas et remplace par un capital (:func:`verser_en_capital`).

L'ASPA n'en est pas : elle regarde toutes les ressources, c'est l'étape
« foyer et net » (:mod:`.foyer`).

Ce que l'étape écrit, :class:`Complements`, suit son schéma,
``data/reference/etapes/completer_tous_regimes.yaml``. Son jumeau est
``moteur/js/droit/completer.js``.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from ..donnees.chargement import Fiabilite
from . import acquerir
from . import etranger as _etranger
from . import liquider, ouvrir
from .commun import (AvantageApplique, PensionRegime, date_d_effet, derniere_annee,
                     ligne_cotisee)
from .compter import trimestres_de_la_ligne_entre as _trimestres_de_la_ligne_entre
from ..somme import somme_ordonnee

if TYPE_CHECKING:
    from ..carriere import Carriere
    from ..donnees.regimes import PeriodeRegime
    from ..scenarios.actuel import ScenarioActuel
    from .liquidation import Contexte
    from .liquider import Pensions
    from .ouvrir import Ouverture
    from .releve import Releve

#: La version du schéma de l'étape que :meth:`Complements.donnees` suit.
SCHEMA_VERSION = 1

#: La fiche de la carte que chaque dispositif applique.
FICHES = {
    "minimum_contributif": "minimum_contributif",
    "minimum_garanti": "minimum_garanti",
    "surcote_parentale": "surcote_parentale",
    "majoration_enfants": "majoration_dix_pour_cent",
    "pension_majoree_reference": "pension_majoree_reference",
    "complement_differentiel_rco": "complement_differentiel_rco",
}

#: Le régime de la retraite complémentaire des non-salariés agricoles, dont
#: le complément différentiel ajoute des points.
RCO = "msa_rco"

#: Les heures de SMIC d'une année, que le complément de la RCO multiplie
#: (L. 732-63, IV).
HEURES_DU_COMPLEMENT = 1820

#: Les points de RCO d'une carrière complète au minimum, que la formule du
#: complément retranche de 2015 à octobre 2021 (D. 732-166-4 : « 3 750 ×
#: vpRCO »).
POINTS_D_UNE_CARRIERE_COMPLETE = 3750

#: Première date d'effet, (année, mois), où la surcote s'AJOUTE au minimum
#: contributif au lieu d'entrer dans la pension qu'on lui compare : décret
#: n° 2008-1509 du 30 décembre 2008, dernier alinéa de D. 351-2-1.
SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS = (2009, 4)

#: La fiche du plafond de L. 18, que :class:`FichesDatees
#: <retraite_notionnelle.scenarios.actuel.FichesDatees>` lit à la date d'effet
#: (:func:`plafond_de_l_article_l18`).
FICHE_DU_PLAFOND_L18 = "majoration_enfants_plafond_fonction_publique"

#: Les plafonds qu'une version de cette fiche peut nommer : le traitement ou
#: la solde de L. 15 qui a liquidé la pension.
PLAFONDS_DE_L18 = ("traitement",)

#: Ce qu'elle peut dire de la surcote : comptée dans la pension qu'on compare
#: au traitement, ou laissée hors du plafond et servie au-delà (Conseil
#: d'État, 29 décembre 2020, n° 428626).
SURCOTES_DE_L18 = ("dans_le_plafond", "hors_du_plafond")

#: Les fiches des versements uniques, que :class:`FichesDatees
#: <retraite_notionnelle.scenarios.actuel.FichesDatees>` lit à la date d'effet
#: (:func:`verser_en_capital`) : le régime général, l'Agirc-Arrco et ses deux
#: devancières, l'Ircantec.
FICHE_DU_VERSEMENT_FORFAITAIRE = "versement_forfaitaire_unique"
FICHE_DU_VERSEMENT_AGIRC_ARRCO = "versement_unique_agirc_arrco"
FICHE_DU_VERSEMENT_IRCANTEC = "versement_unique_ircantec"

#: Ce à quoi une version de l'Agirc-Arrco compare son seuil : le nombre de
#: points de l'allocation, minorée ou non (avant 2019), ou son montant,
#: coefficients et majorations compris, à l'équivalent en euros des points
#: (accord du 17 novembre 2017, article 107).
MESURES_DU_VERSEMENT = ("points", "montant")


def complement_minimum(nue: float, plancher: float, coefficient_surcote: float,
                       date_effet: tuple[int, int]) -> float:
    """Ce que le minimum contributif ajoute à une pension, surcote comprise.

    ``nue`` est la pension calculée avant surcote, ``plancher`` le minimum
    dû au régime, ``coefficient_surcote`` le facteur de la surcote (1,025 pour
    deux trimestres à 1,25 %). La règle dépend de la date d'effet :

    - depuis le 1er avril 2009, la surcote « est calculée sur la base du
      montant de pension avant qu'il ne soit porté au montant minimum »
      (D. 351-2-1) et s'ajoute au minimum : la pension servie vaut
      ``plancher + nue × (coefficient − 1)``, et le complément ``plancher −
      nue``. Circulaire Cnav 2018-04, 3.4.2 : 621 + (645,07 − 621) + 15,52 =
      660,59 € ;
    - jusqu'au 1er mars 2009, la surcote entrait dans la pension comparée au
      minimum : ``max(nue × coefficient, plancher)``. Même circulaire, 3.4.1 :
      621 × 1,015 = 630,31 € < 633,61 €, portés à 633,61 €.

    Le module servait ``plancher × coefficient`` : il surcotait le minimum
    lui-même, ce qu'aucune des deux règles ne fait.
    """
    if nue <= 0.0:
        return 0.0
    if date_effet >= SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS:
        return max(0.0, plancher - nue)
    return max(0.0, plancher - nue * coefficient_surcote)


def majoration_ouverte(regle: dict, cotises: int) -> bool:
    """La majoration au titre des périodes cotisées est-elle due ?

    Pas avant le 1er janvier 2004, qui la crée ; sans condition de 2004 à mars
    2009 ; pour les pensions qui prennent effet depuis le 1er avril 2009, à qui
    justifie de 120 trimestres cotisés tous régimes, quatre par an au plus
    (L. 351-10, D. 351-2-2) — ceux d'AVPF et d'AVA compris depuis septembre
    2023. Le modèle opposait le seuil à toute date, et servait la majoration
    dès 1983. ``regle`` est la version de la fiche ``minimum_contributif``
    (:meth:`~retraite_notionnelle.scenarios.actuel.MinimumContributif.regle`).
    """
    if regle["majoration"] == "aucune":
        return False
    seuil = regle["seuil_trimestres_cotises"]
    return seuil is None or cotises >= seuil


def avpf_retenue(moteur: ScenarioActuel, carriere: Carriere, plafond: int) -> int:
    """Les trimestres d'AVPF et d'AVA que la majoration compte parmi les
    périodes cotisées : depuis le 1er septembre 2023, « dans la limite de 24
    trimestres (AVPF/AVA confondus) », individualisés année par année
    (L. 351-10 ; D. 351-2-2 ; circulaire Cnav 2024/28, point 3.3).

    Chaque année, ils ne comptent que dans la place que les trimestres cotisés
    de l'année laissent sous les quatre trimestres civils ; les années se
    prennent dans l'ordre jusqu'à la limite. Zéro avant septembre 2023
    (``plafond`` nul)."""
    if plafond <= 0:
        return 0
    annee_liquidation = carriere.annee_liquidation
    cotises = carriere.trimestres_par_annee(
        ligne for ligne in carriere.lignes
        if ligne_cotisee(moteur, carriere, ligne) and ligne.annee <= annee_liquidation)
    avpf = carriere.trimestres_par_annee(
        ligne for ligne in carriere.lignes
        if ligne.revenu_avpf > 0 and ligne.annee <= annee_liquidation)
    retenus = 0
    for annee in sorted(avpf):
        place = max(0, carriere.plafond_trimestres(annee) - cotises.get(annee, 0))
        retenus = min(plafond, retenus + min(avpf[annee], place))
    return retenus


def plancher_du_regime(eligible, montant_base: float, montant_majore: float,
                       majoration: bool, tous_regimes: bool) -> float:
    """Le minimum auquel la pension d'un régime est portée, majoration comprise.

    Le minimum entier se réduit au prorata de la durée d'assurance du régime
    sur sa durée de proratisation, et la majoration — l'écart entre le majoré
    et le minimum entiers — au prorata de sa durée COTISÉE (circulaire Cnav
    2005/30, point 511). Mais depuis 2004, quand la durée d'assurance tous
    régimes dépasse la durée requise pour le taux plein, le minimum se calcule
    « comme si l'assuré avait accompli toute sa carrière à un seul régime,
    puis [ses] montants sont répartis » (L. 351-10, « le cas échéant rapportée
    à la durée d'assurance accomplie tant dans le régime général que dans un ou
    plusieurs autres régimes obligatoires » ; point 513) : le minimum au
    prorata de la durée du régime sur la durée tous régimes, non limitée ; la
    majoration de même, et en outre au prorata de la durée cotisée tous
    régimes sur la durée de proratisation quand elle ne l'atteint pas. Le
    modèle proratisait toujours sur la durée de proratisation, et servait à un
    polypensionné un minimum plus élevé que la loi.
    """
    duree_totale = eligible.duree_tous_regimes
    if (tous_regimes and duree_totale > eligible.requis
            and duree_totale > eligible.duree_regime):
        part = eligible.duree_regime / duree_totale
        plancher = montant_base * part
        if majoration:
            plancher += ((montant_majore - montant_base) * part
                         * min(1.0, eligible.cotisee_tous_regimes / eligible.proratisation))
        return plancher
    plancher = montant_base * min(1.0, eligible.prorata_assurance)
    if majoration:
        plancher += (montant_majore - montant_base) * min(1.0, eligible.prorata_cotise)
    return plancher


def selon_la_regle(eligible, regle: dict, avpf: int):
    """Les durées cotisées de l'éligible, telles que la majoration de cette date
    les lit.

    De janvier 2004 à juin 2005, la majoration ne distinguait pas les périodes
    cotisées : la lettre ministérielle du 25 mars 2004 autorisait « à titre
    transitoire, à appliquer à l'ensemble des pensions prenant effet en 2004 le
    montant afférent aux périodes cotisées », reconduit au premier semestre
    2005 ; la durée cotisée vaut alors la durée d'assurance. Depuis septembre
    2023, l'AVPF et l'AVA retenues s'ajoutent à la durée cotisée du régime
    général, qui les valide."""
    if regle["majoration"] == "sans_distinction":
        return replace(eligible, cotisee_regime=eligible.duree_regime,
                       prorata_cotise=min(1.0, eligible.prorata_assurance),
                       cotisee_tous_regimes=eligible.duree_tous_regimes)
    if avpf and eligible.porte_avpf:
        cotisee = eligible.cotisee_regime + avpf
        return replace(eligible, cotisee_regime=cotisee,
                       prorata_cotise=min(cotisee, eligible.proratisation) / eligible.proratisation,
                       cotisee_tous_regimes=eligible.cotisee_tous_regimes + avpf)
    return eligible


def limiter_le_cumul(complements: dict[int, float], pensions, eligibles,
                     montant_base: float) -> dict[int, float]:
    """La limitation du cumul des pensions portées au minimum, de décembre 1984
    à 2003 : leur total ne dépasse pas « le minimum entier le plus élevé
    susceptible d'être servi par le régime le plus favorable » — le même dans
    le régime général et les régimes alignés. Le régime de la plus longue durée
    d'assurance (le dernier à égalité) sert sa pension portée au minimum ; les
    autres, un complément différentiel au prorata de leurs durées (L. 173-2 et
    R. 173-11 de 1985, décret n° 84-995 ; exposé de la Cnav « Minimum avant
    2012 »). Les complements, limités."""
    portes = [e for e in eligibles if e.indice in complements]
    if len(portes) < 2:
        return complements
    total = somme_ordonnee(pensions[e.indice].montant + complements[e.indice] for e in portes)
    if total <= montant_base:
        return complements
    premier = max(portes, key=lambda e: (e.duree_regime, e.indice))
    autres = [e for e in portes if e is not premier]
    marge = max(0.0, montant_base - pensions[premier.indice].montant
                - complements[premier.indice]
                - somme_ordonnee(pensions[e.indice].montant for e in autres))
    duree = somme_ordonnee(e.duree_regime for e in autres)
    limites = dict(complements)
    for e in autres:
        limites[e.indice] = (min(complements[e.indice], marge * e.duree_regime / duree)
                             if duree > 0 else 0.0)
    return limites


def _minimum_international(moteur: ScenarioActuel, carriere: Carriere) -> bool:
    """Le minimum d'une pension proratisée se proratise-t-il sur la durée
    totale non limitée (fiche ``minimum_contributif_international``, depuis
    2004) ? Avant, il l'était comme la pension, ce que fait le minimum de
    toute pension."""
    version = moteur.carrieres_hors_de_france.version(
        "minimum", {"liquidation.date_effet": date_d_effet(carriere)})
    return (version is not None and version["parametres"].get("prorata_du_minimum")
            == "duree_totale_non_limitee")


def plancher_international(eligible, montant_base: float, montant_majore: float,
                           duree_totale: int, cotisee_totale: int,
                           majoration_ouverte: bool) -> float:
    """Le minimum d'une pension proratisée et sa majoration, théoriques puis
    proratisés (exposé de la Cnav « Minimum de la retraite communautaire ») :
    le minimum entier, ou réduit à la durée totale de toute la carrière,
    française et étrangère, quand elle n'atteint pas la durée maximum, puis
    réduit à la part du régime dans cette durée, NON limitée ; la majoration
    théorique, entière ou réduite à la durée totale cotisée, proratisée de
    trois façons selon que la durée totale dépasse la durée requise, ou que
    la durée cotisée atteint la durée maximum. Les durées du régime restent
    limitées à la durée maximum, comme dans le prorata de la pension :
    l'exposé ne lève la limite que pour la durée totale."""
    maximum = eligible.proratisation
    duree_regime = min(eligible.duree_regime, maximum)
    theorique = montant_base * min(1.0, duree_totale / maximum)
    plancher = theorique * duree_regime / duree_totale
    if majoration_ouverte:
        majoration = montant_majore - montant_base
        if duree_totale > eligible.requis:
            plancher += (majoration * min(1.0, cotisee_totale / maximum)
                         * duree_regime / duree_totale)
        elif cotisee_totale < maximum:
            plancher += (majoration * cotisee_totale / maximum
                         * duree_regime / min(duree_totale, maximum))
        else:
            plancher += majoration * min(eligible.cotisee_regime, maximum) / maximum
    return plancher


@dataclass(frozen=True)
class PensionMajoree:
    """Ce que la pension majorée de référence ajoute à la pension de base des
    non-salariés agricoles, et ce qu'elle a lu (:func:`pension_majoree`)."""

    #: La PMR entière de la date d'effet, en euros par an.
    entiere: float
    #: La durée retenue et la durée de référence, en trimestres.
    duree: int
    reference: int
    #: La majoration avant l'écrêtement, et après.
    avant_ecretement: float
    complement: float
    #: Le plafond de l'écrêtement.
    plafond: float
    fiabilite: Fiabilite


def pension_majoree(moteur: ScenarioActuel, carriere: Carriere, eligible,
                    pension: PensionRegime, ressources: float) -> PensionMajoree | None:
    """Ce que la pension majorée de référence (PMR) ajoute à la pension de
    base des non-salariés agricoles ; ``None`` quand elle n'y ajoute rien.

    La majoration « a pour objet de porter le total des droits propres et
    dérivés servis à l'assuré par le régime [...] à un montant minimum »
    (L. 732-54-2) : la PMR de la date d'effet au prorata de la durée
    d'assurance non salariée agricole sur la durée de référence DR, la durée
    au plus DR (D. 732-110, D. 732-111). Elle s'ouvre au taux plein, avec, de
    2009 à janvier 2014, une durée minimale dans le régime (D. 732-109).
    La pension se compare AVANT SA SURCOTE, « calculée sur la base du montant
    de pension avant qu'il ne soit porté au montant minimum », et sans la
    majoration pour enfants (D. 732-112) — que D. 732-38 ne fait porter que sur
    la pension calculée, non sur la majoration : la surcote reste, la majoration
    pour enfants ne s'applique pas au complément.

    L'ÉCRÊTEMENT : la majoration ne fait pas dépasser le plafond à
    ``ressources`` — toutes les pensions de base et complémentaires de
    l'assuré et les majorations pour enfants qui leur sont rattachées, celles
    que d'autres départs servent et les pensions étrangères (L. 732-54-3,
    D. 732-114). ``eligible`` est l'
    :class:`~retraite_notionnelle.droit.liquider.EligibleAgricole` du régime.
    """
    regle = moteur.pension_majoree_reference.regle(date_d_effet(carriere))
    if not regle["existe"] or not eligible.taux_plein or pension.montant <= 0.0:
        return None
    duree = eligible.duree + (eligible.enfants if regle["majorations_de_duree"] else 0)
    if duree < (regle["duree_minimale"] or 0):
        return None
    # De 2009 à 2021, PMR1 pour qui a été chef d'exploitation dix-sept ans et
    # demi, PMR2 sinon (D. 732-110, II ; D. 732-111).
    serie = regle["montant"]
    if regle["montant_reduit"] and eligible.duree < (regle["seuil_chef"] or 0):
        serie = regle["montant_reduit"]
    annee, mois = carriere.annee_liquidation, carriere.mois_liquidation
    lu = moteur.pension_majoree_reference.montant(serie, annee, mois)
    if lu is None:
        return None
    entiere, fiabilite = lu
    retenue = min(duree, eligible.reference)
    avant = max(0.0, entiere * retenue / eligible.reference
                - pension.montant / eligible.surcote)
    if avant <= 0.0:
        return None
    if regle["plafond"] == "minimum_contributif":
        _, _, plafond, fiabilite_plafond = moteur.minimum_contributif.valeurs(annee, mois)
    else:
        plafond, fiabilite_plafond = moteur.pension_majoree_reference.montant(
            regle["plafond"], annee, mois)
    return PensionMajoree(
        entiere=entiere, duree=retenue, reference=eligible.reference,
        avant_ecretement=avant, complement=max(0.0, min(avant, plafond - ressources)),
        plafond=plafond, fiabilite=min(fiabilite, fiabilite_plafond))


@dataclass(frozen=True)
class ComplementDifferentiel:
    """Ce que le complément différentiel ajoute à la RCO, et ce qu'il a lu
    (:func:`complement_differentiel`)."""

    #: Le pourcentage du SMIC net, et le SMIC net agricole horaire.
    pourcentage: float
    smic_net: float
    #: Le montant minimal d'une carrière complète : pourcentage × 1 820 ×
    #: SMIC net, en euros par an.
    cible: float
    #: La durée de chef retenue et la durée de référence, en trimestres.
    duree: int
    reference: int
    #: Les points ajoutés, arrondis à l'entier, et la valeur du point.
    points: int
    valeur_point: float
    #: Leur montant, en euros par an.
    montant: float
    #: Un plafond a-t-il réduit le complément de la formule ?
    plafonne: bool
    fiabilite: Fiabilite


def complement_differentiel(moteur: ScenarioActuel, carriere: Carriere, eligible,
                            base: float, rco: float, points_rco: float,
                            valeur_point: float, personnelles: float,
                            quand: str | None = None,
                            smic: tuple[float, Fiabilite] | None = None,
                            pmr: tuple[float, Fiabilite] | None = None
                            ) -> ComplementDifferentiel | None:
    """Les points de RCO que le complément différentiel ajoute (L. 732-63) ;
    ``None`` quand il n'en ajoute pas.

    Il s'ouvre au chef d'exploitation de dix-sept ans et demi qui a la durée
    requise tous régimes — le taux plein suffit depuis septembre 2023 —, et
    porte ses deux pensions agricoles, ``base`` (pension majorée de référence
    et surcote comprises, sans la majoration pour enfants) et ``rco``, à un
    pourcentage de 1 820 fois le SMIC net agricole horaire du 1er janvier de
    l'année d'effet, la CIBLE (D. 732-166-2 à D. 732-166-4) :

    * jusqu'en octobre 2021, ``(cible − (PMR1 + 3 750 × vpRCO)) × DCE / DR`` :
      l'écart entre la cible et ce que vaudraient une PMR et une RCO entières ;
    * depuis, ``(cible − PMRmax) × DCE / DR − N × vpRCO`` : l'écart entre la part
      de la cible que la PMR ne couvre pas et les ``points_rco`` de chef.

    Le complément ne fait pas dépasser aux deux pensions agricoles la cible au
    prorata de la durée agricole (D. 732-166-5), ni, depuis novembre 2021, à
    toutes les pensions personnelles de l'assuré, ``personnelles``, la cible
    entière (L. 732-63, V ; D. 732-166-5-1). Il se convertit en points à la
    valeur de service de l'année, arrondis à l'entier le plus proche
    (D. 732-166-6). Le modèle ne connaissant que le statut de chef, la durée
    de chef, DCE, est la durée agricole, Dnsa.

    ``quand``, ``smic`` et ``pmr`` lisent la règle, le SMIC net agricole et la
    PMR d'une autre date que la date d'effet : ceux du 1er septembre 2023, pour
    une pension prise avant, que le taux plein ouvre depuis (loi n° 2023-270,
    article 18, VI ; :func:`~retraite_notionnelle.revalorisation.relever_les_exploitants`).
    """
    date_effet = date_d_effet(carriere)
    regle = moteur.complement_differentiel_rco.regle(quand or date_effet)
    if not regle["existe"] or valeur_point <= 0.0:
        return None
    duree = eligible.duree + (eligible.enfants if regle["majorations_de_duree"] else 0)
    ouvert = (eligible.taux_plein if regle["condition"] == "taux_plein"
              else eligible.duree_requise_atteinte)
    if duree < (regle["seuil_chef"] or 0) or not ouvert:
        return None
    annee = carriere.annee_liquidation
    smic = smic or moteur.complement_differentiel_rco.smic_net(annee)
    pmr = pmr or moteur.pension_majoree_reference.montant(
        moteur.pension_majoree_reference.regle(date_effet)["montant"] or "pmr_chef",
        annee, regle["pmr_au_mois"] or 1)
    if smic is None or pmr is None:
        return None
    smic_net, fiabilite = smic
    cible = regle["pourcentage"] * HEURES_DU_COMPLEMENT * smic_net
    retenue = min(duree, eligible.reference)
    prorata = retenue / eligible.reference
    if regle["formule"] == "carriere_complete":
        formule = (cible - (pmr[0] + POINTS_D_UNE_CARRIERE_COMPLETE * valeur_point)) * prorata
    else:
        formule = (cible - pmr[0]) * prorata - points_rco * valeur_point
    montant = min(formule, cible * prorata - (base + rco))
    if regle["plafond_tous_regimes"]:
        montant = min(montant, cible - personnelles)
    montant = max(0.0, montant)
    points = math.floor(montant / valeur_point + 0.5 + 1e-9)
    if points <= 0:
        return None
    return ComplementDifferentiel(
        pourcentage=regle["pourcentage"], smic_net=smic_net, cible=cible,
        duree=retenue, reference=eligible.reference, points=points,
        valeur_point=valeur_point, montant=points * valeur_point,
        plafonne=montant < formule - 1e-9,
        fiabilite=min(fiabilite, pmr[1]))


@dataclass(frozen=True)
class MinimumEcrete:
    """Ce que la révision du minimum contributif relit après le départ : sa
    majoration « est révisée lorsque le montant des avantages personnels de
    retraite a varié », et le plafond auquel le total des pensions se compare
    est celui de l'entrée en jouissance, « revalorisé [...] dans les
    conditions prévues à l'article L. 161-23-1 » (R. 173-8). En euros de la
    liquidation."""

    #: Le complément de tous les régimes, avant l'écrêtement.
    avant_ecretement: float
    #: Ce qui sépare les pensions du plafond de l'article L. 173-2 : le
    #: plafond, moins les pensions, celles d'autres départs et les pensions
    #: étrangères qu'il compte ; négatif quand elles le dépassent.
    marge: float
    #: Le complément de chaque régime, après l'écrêtement.
    par_regime: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class PetitePension:
    """Ce que la majoration exceptionnelle des petites pensions relit d'une
    pension de base liquidée avant le 1er septembre 2023 (loi n° 2023-270,
    article 18, V ; décret n° 2023-754, article 3 ; circulaire Cnav
    n° 2023-21) : :func:`~retraite_notionnelle.revalorisation.majorer_les_petites_pensions`
    la calcule le mois où elle est due, sur ce que les pensions servent alors.
    Ses régimes sont ceux qui portent le minimum contributif : le régime
    général, les régimes des artisans et des commerçants qu'il a intégrés,
    celui des salariés agricoles et celui des cultes. En euros de la date
    d'effet de la pension."""

    #: Le régime « concerné », qui sert la pension et doit la majoration.
    regime: str
    #: Liquidée au taux plein, par la durée, l'âge ou l'inaptitude
    #: (circulaire, 2.2).
    taux_plein: bool
    #: Les durées cotisée et validée dans le régime, en trimestres, et la
    #: durée d'assurance maximum de la génération (L. 351-1, troisième
    #: alinéa), qui proratise la majoration sur la première et son plafond
    #: sur la seconde (circulaire, 3.1 et 3.2.2).
    cotisee: int
    validee: int
    maximum: int
    #: Les trimestres cotisés tous régimes de base, français et étrangers,
    #: quatre par an au plus, l'AVPF exclue : cent vingt ouvrent la majoration
    #: (circulaire, 2.3).
    cotises_tous_regimes: int
    #: Ce que la surcote ajoute à la pension, que la comparaison aux plafonds
    #: écarte (circulaire, 3.2.3).
    surcote: float = 0.0


def surcote_hors_minimum(montant: float, eligible, ajout: float,
                         date_effet: tuple[int, int]) -> float:
    """Ce que la surcote ajoute à ``montant``, la pension d'un régime que le
    minimum contributif a relevée de ``ajout`` : celle de la pension nue, que
    le minimum laisse en sus depuis avril 2009 (D. 351-2-1) ; avant, rien
    quand il l'a relevée, la surcote s'y fondant (:func:`complement_minimum`).
    ``eligible`` est l':class:`~retraite_notionnelle.droit.liquider.EligibleMinimum`
    du régime."""
    if eligible.surcote <= 1.0 or (ajout > 0
                                   and date_effet < SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS):
        return 0.0
    nue = (montant - ajout - eligible.hors_minimum) / eligible.surcote
    return max(0.0, nue * (eligible.surcote - 1.0))


@dataclass(frozen=True)
class ChefDExploitation:
    """Ce que le relèvement de septembre 2023 relit d'un chef d'exploitation
    parti avant : le taux plein ouvre depuis les points gratuits et le
    complément différentiel de la RCO à qui n'avait pas la durée requise tous
    régimes (loi n° 2023-270, article 18, VI) ;
    :func:`~retraite_notionnelle.revalorisation.relever_les_exploitants` les
    calcule au 1er septembre 2023, sur ce que ses pensions servent alors."""

    #: Le régime de base des non-salariés agricoles.
    regime: str
    #: Son taux plein, la durée requise, ses durées et sa durée de référence
    #: (:class:`~retraite_notionnelle.droit.liquider.EligibleAgricole`).
    eligible: object
    #: Les points de RCO acquis à la liquidation, par cotisation ou à titre
    #: gratuit : le N du complément (D. 732-166-4).
    points: float
    #: Les points gratuits que le taux plein ouvre, quand la durée requise ne
    #: les avait pas ouverts à la liquidation (L. 732-56, D. 732-154).
    gratuits: float
    #: Le complément différentiel a-t-il été servi à la liquidation ?
    complement: bool


@dataclass(frozen=True)
class Complements:
    """Ce que l'étape « compléter tous régimes » écrit."""

    #: La personne dont les pensions sont complétées.
    personne: str
    #: Les pensions de régime une fois les minima et la surcote parentale
    #: faits, chacune avec la formule qui le dit.
    regimes: tuple[PensionRegime, ...]
    #: Ce que chaque dispositif ajoute, dans l'ordre où le droit l'applique.
    avantages: tuple[AvantageApplique, ...]
    #: Le total des pensions, complété : minima, surcote parentale et
    #: majoration pour enfants compris.
    total: float
    #: Un des deux minima a-t-il relevé une pension ?
    minimum_applique: bool
    fiabilite: Fiabilite
    #: Ce que la pension provisoire d'une retraite progressive ajoute à la
    #: pension complète qui descendrait sous elle (:mod:`.progressive`) :
    #: un droit acquis, qui entre au total contributif.
    plancher: float = 0.0
    #: Le minimum contributif servi, et ce que sa révision relit
    #: (:class:`MinimumEcrete`) ; ``None`` sans lui.
    minimum_ecrete: MinimumEcrete | None = None
    #: Ce que la majoration exceptionnelle de septembre 2023 relit de chaque
    #: pension que le minimum contributif regarde (:class:`PetitePension`).
    petites_pensions: tuple[PetitePension, ...] = ()
    #: Ce que le relèvement des exploitants de septembre 2023 relit
    #: (:class:`ChefDExploitation`) ; ``None`` sans RCO.
    chef: ChefDExploitation | None = None

    def donnees(self) -> dict:
        """Les compléments, tels que le schéma de l'étape les décrit."""
        return {
            "schema_version": SCHEMA_VERSION,
            "personne": self.personne,
            "dispositifs": [
                {"code": a.code, "fiche": FICHES[a.code], "montant": a.montant,
                 "parts": [{"regime": code, "montant": part} for code, part in a.par_regime]}
                for a in self.avantages],
            "fiabilite": self.fiabilite.name.lower(),
        }


def completer(moteur: ScenarioActuel, releve: Releve, ouverture: Ouverture,
              liquidees: Pensions, contexte: Contexte | None = None,
              servies: float = 0.0, initiales: tuple = (),
              recalcul: bool = True, nationales: Pensions | None = None,
              nature: str = "definitive",
              premiere_retraite: str | None = None) -> Complements:
    """Les pensions de ``liquidees``, complétées de ce que le droit y ajoute.

    Le contexte dit ce que le calcul neutralise : les avantages non
    contributifs, que la cascade retire pour en mesurer l'apport ; la décote
    et la surcote, pour valoriser des droits acquis — la surcote parentale
    part avec elles. ``servies`` est ce que valent, par an, à la date d'effet,
    les pensions que des départs précédents servent déjà
    (:mod:`.departs`) : l'écrêtement du minimum contributif les compte.
    ``initiales`` sont, après une retraite progressive, les pensions
    provisoires de ses régimes de base, menées à la date d'effet
    (:mod:`.progressive`) : la pension complète ne descend pas sous elles,
    et les vaut quand ``recalcul`` est faux. ``nationales`` sont les
    pensions nationales de qui a des périodes qu'un accord compare
    (:mod:`.etranger`) : la pension proratisée de chaque régime porté au
    minimum contributif se compare à elle, chacune à son minimum, et la plus
    élevée est servie (fiches ``pension_proratisee`` et
    ``minimum_contributif_international``). ``nature`` est celle de la
    demande, et ``premiere_retraite`` la date d'effet de la première pension de
    base qu'un départ précédent sert déjà : les versements uniques les lisent
    (:func:`verser_en_capital`).
    """
    carriere = releve.carriere
    durees, droits = releve.durees, releve.droits
    annee_liquidation = carriere.annee_liquidation
    avantages_non_contributifs = (contexte is None
                                  or not contexte.neutralise("avantages_non_contributifs"))
    ignorer_penalite_age = contexte is not None and contexte.neutralise("decote_surcote")
    trimestres_cotises = ouverture.trimestres_cotises
    majoration_enfants = durees.enfants
    points_acquis = droits.points_acquis
    majoration_points = droits.majoration_points
    points_majores = droits.points_majores
    pensions = list(liquidees.regimes)
    eligibles_minimum = liquidees.minimum
    eligibles_garanti = liquidees.garanti
    #: Ce que la surcote ajoute à chaque pension que le plafond de L. 18 borne :
    #: le minimum garanti, qui se substitue à la pension, l'efface ; la surcote
    #: parentale s'y ajoute.
    surcotes_l18 = {eligible.indice: eligible.surcote for eligible in liquidees.plafonds}
    total = somme_ordonnee(p.montant for p in pensions)
    avantages: list[AvantageApplique] = []
    fiabilite_globale = Fiabilite.CERTIFIEE
    minimum_applique = False
    minimum_ecrete: MinimumEcrete | None = None
    #: Ce que le minimum contributif ajoute à chaque pension, par son indice.
    ajouts_du_minimum: dict[int, float] = {}
    chef: ChefDExploitation | None = None

    # La règle du minimum que la date d'effet fait valoir (fiche
    # ``minimum_contributif``) : il n'existe que depuis le 1er avril 1983, sa
    # majoration depuis 2004, son seuil depuis avril 2009, son écrêtement
    # depuis 2012, l'AVPF dans sa majoration depuis septembre 2023.
    regle = moteur.minimum_contributif.regle(date_d_effet(carriere))
    if avantages_non_contributifs and eligibles_minimum and regle["existe"]:
        # Le minimum contributif ne relève que les pensions liquidées AU
        # TAUX PLEIN (L. 351-10). Sa majoration au titre des périodes
        # cotisées se proratise sur la durée COTISÉE dans le régime, quand le
        # montant de base se proratise sur sa durée d'assurance : une carrière
        # entrecoupée de chômage indemnisé valide sa durée d'assurance sans
        # cotiser, et n'a donc droit qu'à une part de la majoration. Les
        # montants sont ceux du mois de la date d'effet.
        montant_base, montant_majore, plafond, fiabilite_minimum = (
            moteur.minimum_contributif.valeurs(annee_liquidation,
                                               carriere.mois_liquidation)
        )
        avpf = avpf_retenue(moteur, carriere, regle["plafond_avpf"])
        majoree = majoration_ouverte(regle, trimestres_cotises + avpf)
        date_effet = (annee_liquidation, carriere.mois_liquidation)

        def complement_du(pension: PensionRegime, eligible, plancher: float) -> float:
            # Le minimum se compare à la pension AVANT surcote, et la
            # surcote, calculée sur cette pension nue, s'ajoute au minimum
            # (D. 351-2-1) : voir :func:`complement_minimum`, qui porte
            # aussi la règle d'avant avril 2009.
            if not eligible.taux_plein:
                return 0.0
            # La fraction d'avant 1998 des cultes a ses propres majorations
            # (:mod:`.cultes`) : le minimum ne relève que l'autre.
            return complement_minimum(
                (pension.montant - eligible.hors_minimum) / eligible.surcote, plancher,
                eligible.surcote, date_effet)

        def plancher_national(eligible, majoration: bool) -> float:
            return plancher_du_regime(
                selon_la_regle(eligible, regle, avpf), montant_base, montant_majore,
                majoration, regle["duree_tous_regimes"])

        # LA PENSION PRORATISÉE ET LA PENSION NATIONALE : quand un accord les
        # compare, chacune est portée à SON minimum, puis la plus élevée est
        # servie — la proratisée à égalité.
        alternatives = {} if nationales is None else {
            nationales.regimes[eligible.indice].regime:
                (nationales.regimes[eligible.indice], eligible)
            for eligible in nationales.minimum}
        international = (None if nationales is None
                         else _minimum_international(moteur, carriere))
        if nationales is not None:
            # La pension nationale ne compte que les trimestres cotisés en
            # France pour la majoration.
            cotises_francais = carriere.trimestres_cumules(
                ligne for ligne in carriere.lignes
                if ligne_cotisee(moteur, carriere, ligne)
                and ligne.annee <= annee_liquidation)
            duree_totale = durees.pour_le_taux(_etranger.GENERALE)
        #: Complément dû à chaque régime, avant écrêtement.
        complements: dict[int, float] = {}
        #: Le minimum servi compte-t-il la majoration des périodes cotisées ?
        majore = False
        for eligible in eligibles_minimum:
            pension = pensions[eligible.indice]
            alternative = alternatives.get(pension.regime)
            avec_majoration = majoree
            if alternative is None:
                complement = complement_du(
                    pension, eligible, plancher_national(eligible, majoree))
            else:
                plancher = (
                    plancher_international(
                        selon_la_regle(eligible, regle, avpf), montant_base,
                        montant_majore, duree_totale,
                        (duree_totale if regle["majoration"] == "sans_distinction"
                         else trimestres_cotises + avpf), majoree)
                    if international else plancher_national(eligible, majoree))
                complement = complement_du(pension, eligible, plancher)
                nationale, eligible_national = alternative
                majoree_nationale = majoration_ouverte(regle, cotises_francais + avpf)
                complement_national = complement_du(
                    nationale, eligible_national,
                    plancher_national(eligible_national, majoree_nationale))
                proratisee = pension.montant + complement
                if nationale.montant + complement_national > proratisee:
                    pensions[eligible.indice] = replace(
                        nationale,
                        detail=(f"pension nationale, plus élevée que la pension "
                                f"proratisée ({proratisee:,.2f} €) : {nationale.detail}"))
                    complement, avec_majoration = complement_national, majoree_nationale
                else:
                    pensions[eligible.indice] = replace(
                        pension,
                        detail=(f"pension proratisée, au moins égale à la pension "
                                f"nationale ({nationale.montant + complement_national:,.2f} €)"
                                f" : {pension.detail}"))
            if complement > 0:
                complements[eligible.indice] = complement
                majore = majore or avec_majoration
        if regle["cumul_des_minima"]:
            complements = limiter_le_cumul(complements, pensions, eligibles_minimum,
                                           montant_base)
        total = somme_ordonnee(p.montant for p in pensions)
        releve_minimum = somme_ordonnee(complements.values())
        if releve_minimum > 0 and regle["ecretement"]:
            # Écrêtement de l'article L. 173-2, pour les pensions qui prennent
            # effet depuis le 1er janvier 2012 : le complément est rogné de
            # ce qui dépasse le plafond, tous régimes confondus, et jamais
            # au-delà. La comparaison porte sur les pensions PERSONNELLES,
            # majorations pour enfants exclues — raison de plus pour que
            # celles-ci se calculent après, sur le montant relevé —, celles
            # que d'autres départs servent déjà comprises, au montant du mois
            # de la date d'effet (R. 173-7).
            # Depuis 2012, les pensions étrangères aussi, hors celles des
            # règlements européens et de six conventions (fiche
            # minimum_contributif_international).
            etrangeres = _etranger.pensions_a_l_ecretement(moteur, carriere)
            marge = plafond - total - servies - etrangeres
            admissible = max(0.0, min(releve_minimum, marge))
            if admissible < releve_minimum:
                facteur = admissible / releve_minimum
                complements = {
                    indice: complement * facteur
                    for indice, complement in complements.items()
                }
            minimum_ecrete = MinimumEcrete(
                avant_ecretement=releve_minimum, marge=marge,
                par_regime=tuple((pensions[indice].regime, complement)
                                 for indice, complement in complements.items()))
            releve_minimum = admissible
        if releve_minimum > 0:
            ajouts_du_minimum = dict(complements)
            for indice, complement in complements.items():
                # Le complément est DIT, pas seulement annoncé : sans lui,
                # refaire la formule donnait la pension d'avant le minimum
                # et l'écart restait inexpliqué — deux mille euros par an
                # sur une petite retraite, ce qui n'est pas un détail.
                pensions[indice] = replace(
                    pensions[indice],
                    montant=pensions[indice].montant + complement,
                    detail=(
                        f"{pensions[indice].detail} = "
                        f"{pensions[indice].montant:,.2f} €, porté au minimum "
                        f"contributif par + {complement:,.2f} €"
                    ),
                )
            total += releve_minimum
            minimum_applique = True
            fiabilite_globale = min(fiabilite_globale, fiabilite_minimum)
            avantages.append(AvantageApplique(
                code="minimum_contributif",
                libelle="Minimum contributif",
                montant=releve_minimum,
                detail=(
                    "porté au plancher, au prorata de la durée acquise"
                    + (", majoration des périodes cotisées comprise"
                       if majore else "")
                ),
                # La part de chaque pension : la réversion du régime général
                # se calcule sans elle (:mod:`.reversion`).
                par_regime=tuple((pensions[indice].regime, complement)
                                 for indice, complement in complements.items()
                                 if complement > 0),
            ))

    # LA MAJORATION EXCEPTIONNELLE DE SEPTEMBRE 2023 relève les pensions que
    # le minimum contributif regarde, portées ou non à lui ; elle se calcule
    # le mois où elle est due, sur ce qu'elles servent alors
    # (:func:`~retraite_notionnelle.revalorisation.majorer_les_petites_pensions`).
    # Ce qu'elle relit de chacune s'écrit ici : ses durées, son taux plein et
    # sa surcote, qu'elle écarte de ses comparaisons.
    petites_pensions: tuple[PetitePension, ...] = ()
    if avantages_non_contributifs:
        mois_d_effet = (annee_liquidation, carriere.mois_liquidation)
        petites_pensions = tuple(
            PetitePension(
                regime=pensions[eligible.indice].regime,
                taux_plein=eligible.taux_plein,
                cotisee=eligible.cotisee_regime, validee=eligible.duree_regime,
                maximum=eligible.proratisation,
                cotises_tous_regimes=trimestres_cotises,
                surcote=surcote_hors_minimum(
                    pensions[eligible.indice].montant, eligible,
                    ajouts_du_minimum.get(eligible.indice, 0.0), mois_d_effet))
            for eligible in eligibles_minimum)

    if avantages_non_contributifs and eligibles_garanti:
        # Le minimum garanti n'est pas un minimum proratisé mais un BARÈME
        # sur la durée de services : quinze ans en ouvrent 57,5 % de la
        # référence, trente ans 95 %, quarante ans la totalité. Il ne
        # s'ajoute pas à la pension, il s'y substitue quand il lui est
        # supérieur.
        releve_garanti = 0.0
        for eligible in eligibles_garanti:
            if not eligible.ouvert:
                continue
            plancher = moteur.minimum_garanti.montant(
                annee_liquidation, eligible.trimestres_services,
                eligible.duree_maximum,
            )
            if plancher is None:
                continue
            pension = pensions[eligible.indice]
            if 0 < pension.montant < plancher[0]:
                complement = plancher[0] - pension.montant
                releve_garanti += complement
                fiabilite_globale = min(fiabilite_globale, plancher[1])
                # Le complément est DIT, comme pour le minimum contributif :
                # sans lui, refaire la formule donnait la pension d'avant le
                # plancher, et l'écart restait sans explication.
                pensions[eligible.indice] = replace(
                    pension,
                    montant=plancher[0],
                    detail=(f"{pension.detail} = {pension.montant:,.2f} €, "
                            f"porté au minimum garanti par + {complement:,.2f} €"),
                )
                if eligible.indice in surcotes_l18:
                    surcotes_l18[eligible.indice] = 0.0
        if releve_garanti > 0:
            total += releve_garanti
            avantages.append(AvantageApplique(
                code="minimum_garanti",
                libelle="Minimum garanti de la fonction publique",
                montant=releve_garanti,
                detail="barème de l'article L. 17, sur la durée de services",
            ))

    # LA PENSION COMPLÈTE D'UNE RETRAITE PROGRESSIVE (droit/progressive.py) :
    # liquidée dans les conditions de droit commun, elle ne peut être
    # inférieure au montant entier qui a servi de base à la fraction,
    # revalorisé (D. 351-15, D. 161-2-24-7, D. 37-3) ; avant le décret du
    # 8 juin 2006, elle était ce montant. La comparaison se fait régime par
    # régime, minima compris, avant la surcote parentale et la majoration.
    plancher = 0.0
    for regime, initiale in initiales:
        for indice, pension in enumerate(pensions):
            if pension.regime != regime or (recalcul and pension.montant >= initiale):
                continue
            ecart = initiale - pension.montant
            plancher += ecart
            total += ecart
            pensions[indice] = replace(
                pension, montant=initiale,
                detail=(f"{pension.detail} = {pension.montant:,.2f} €, porté à la "
                        f"pension provisoire revalorisée par + {ecart:,.2f} €"
                        if recalcul else
                        f"la pension provisoire de la retraite progressive, "
                        f"revalorisée : {initiale:,.2f} €, qui ne se recalcule "
                        f"pas avant le 8 juin 2006"))

    # Surcote parentale (L. 351-1-2-1) : elle vient APRÈS les minima,
    # comme la surcote ordinaire, et AVANT la majoration pour enfants, qui
    # se calcule sur la pension surcotée. Elle ne récompense pas les mêmes
    # trimestres que la surcote ordinaire — celle-ci ne compte qu'au-delà
    # de l'âge légal, celle-là dans l'année qui le précède — et les deux se
    # cumulent donc sans se recouvrir.
    parametres_parentale = (
        moteur.surcote_parentale.parametres(annee_liquidation)
        if (avantages_non_contributifs and majoration_enfants is not None
            and not ignorer_penalite_age)
        else None
    )
    if parametres_parentale is not None:
        age_legal_minimal, taux_parental, maximum, fiabilite_parentale = (
            parametres_parentale
        )
        gain_parental = 0.0
        trimestres_parentaux = 0
        for indice, pension in enumerate(pensions):
            regime = moteur.catalogue[pension.regime]
            periode = regime.periode(
                min(annee_liquidation, derniere_annee(regime))
            )
            if (periode is None or "surcote_parentale"
                    not in periode.avantages_non_contributifs):
                continue
            age_legal = ouvrir.age_ouverture(moteur, periode, carriere)
            requis = ouvrir.duree_requise(moteur, periode, carriere)[0]
            # LA FENÊTRE EST L'ANNÉE QUI PRÉCÈDE L'ÂGE LÉGAL, dès que cet
            # âge atteint 63 ans : « accomplie l'année précédant l'âge
            # mentionné à l'article L. 161-17-2, lorsque celui-ci est égal
            # ou supérieur à soixante-trois ans » (L. 351-1-2-1, 2023) ;
            # l'âge de la surcote « est abaissé d'un an » (version de 2025).
            # Le module la faisait courir de 63 ans à l'âge légal : la
            # génération 1966, âge légal 63 ans et trois mois, n'y trouvait
            # qu'un trimestre là où le texte en ouvre quatre, et la
            # génération 1965 d'avril, âge légal 63 ans, aucun.
            if age_legal < age_legal_minimal:
                continue
            # Au MOIS près : l'âge légal tombe en cours d'année depuis la
            # suspension de 2026, et une fenêtre lue à l'année entière n'y
            # trouvait qu'un trimestre pour la génération 1966.
            date_legale = carriere.date_de_l_age(age_legal)
            debut_fenetre = date_legale.plus_mois(-12)
            # Ne comptent que les trimestres cotisés de la fenêtre
            # accomplis « au delà de la limite » de durée (L. 351-1-2-1) :
            # tous, si la durée requise est atteinte à l'ouverture de la
            # fenêtre, trimestres pour enfants compris ; ceux d'après la
            # limite, si elle l'est en cours de fenêtre ; aucun sinon.
            if requis <= 0:
                continue
            avant = majoration_enfants.trimestres + _trimestres_entre_dates(
                carriere, DateMois(carriere.annee_naissance, 1), debut_fenetre,
                cotises_seulement=False,
            )
            valides_fenetre = _trimestres_entre_dates(
                carriere, debut_fenetre, date_legale, cotises_seulement=False,
            )
            # Surtout pas `trimestres` : c'est la durée d'assurance tous
            # régimes, et l'écraser ici la faisait tomber à quatre.
            acquis_parentaux = min(
                maximum,
                _trimestres_entre_dates(carriere, debut_fenetre, date_legale,
                                        cotises_seulement=True),
                max(0, avant + valides_fenetre - requis),
            )
            if acquis_parentaux <= 0:
                continue
            supplement = pension.montant * taux_parental * acquis_parentaux
            pensions[indice] = replace(
                pension,
                montant=pension.montant + supplement,
                detail=(pension.detail + ", surcote parentale "
                        f"{taux_parental * acquis_parentaux:.2%}"),
            )
            gain_parental += supplement
            trimestres_parentaux = max(trimestres_parentaux, acquis_parentaux)
            if indice in surcotes_l18:
                # La surcote parentale du fonctionnaire majore la pension « dans
                # les mêmes conditions que celles prévues au III » (L. 14, IV).
                surcotes_l18[indice] += supplement
        if gain_parental > 0:
            total += gain_parental
            fiabilite_globale = min(fiabilite_globale, fiabilite_parentale)
            avantages.append(AvantageApplique(
                code="surcote_parentale",
                libelle="Surcote parentale",
                montant=gain_parental,
                detail=(f"{taux_parental * trimestres_parentaux:.2%} pour "
                        f"{trimestres_parentaux} trimestre"
                        f"{'s' if trimestres_parentaux > 1 else ''} dans "
                        "l'année qui précède l'âge légal"),
            ))

    if avantages_non_contributifs and carriere.nombre_enfants >= 2:
        majoration = 0.0
        taux_cite = 0.0
        # Le plafond de l'Agirc-Arrco s'oppose à la majoration de LA
        # complémentaire, pas à celle de chacune de ses fiches : les points
        # d'un salarié du privé sont répartis entre l'Agirc, l'Arrco et le
        # régime unifié, et plafonner chacun séparément reviendrait à
        # tripler le plafond. On les met donc dans un même seau.
        majoration_plafonnee = 0.0
        plafond_commun: float | None = None
        #: (régime, part, soumise au plafond), dans l'ordre des pensions.
        parts: list[tuple[str, float, bool]] = []
        # Le plafond de L. 18, au traitement qui a liquidé la pension de chaque
        # régime du code des pensions.
        plafond_l18 = plafond_de_l_article_l18(moteur, carriere)
        traitements = {eligible.indice: eligible.traitement
                       for eligible in liquidees.plafonds}
        bornee_au_traitement = False
        for indice, pension in enumerate(pensions):
            if pension.montant <= 0.0:
                continue
            regime = moteur.catalogue[pension.regime]
            periode = regime.periode(min(annee_liquidation, derniere_annee(regime)))
            if periode is None:
                continue
            if "majoration_enfants" not in periode.avantages_non_contributifs:
                continue
            taux = _taux_majoration_enfants(regime, carriere.nombre_enfants,
                                            periode)
            points = points_acquis.get(pension.regime, 0.0)
            majores = points_majores.get(pension.regime, 0.0)
            if majores > 0.0 and points > 0.0:
                # CHAQUE POINT À SON TAUX, celui de son année d'acquisition
                # (`MajorationsEnfantsPoints`) : le module servait 10 % aux
                # points Arrco de 1999 à 2011, que l'accord majore de 5 %,
                # et aux points Agirc d'avant 2012, qu'il majore de 8 à
                # 24 % selon le nombre d'enfants.
                taux = (majoration_points[pension.regime]
                        + taux * (points - majores)) / points
            if taux <= 0:
                continue
            part = pension.montant * taux
            if (plafond_l18 is not None and indice in traitements
                    and pension.regime in plafond_l18["parametres"]["regimes"]):
                sous = majoration_sous_le_traitement(
                    pension.montant, part, traitements[indice], surcotes_l18[indice],
                    plafond_l18["parametres"]["surcote"] == "hors_du_plafond")
                if sous < part:
                    bornee_au_traitement = True
                    fiabilite_globale = min(fiabilite_globale, Fiabilite.depuis_texte(
                        plafond_l18["parametres"]["fiabilite"]))
                    part = sous
                    if part <= 0.0:
                        continue
            plafond = plafond_majoration(moteur,
                pension.regime, periode, carriere, annee_liquidation
            )
            if plafond is None:
                majoration += part
            else:
                majoration_plafonnee += part
                plafond_commun = (plafond if plafond_commun is None
                                  else max(plafond_commun, plafond))
            parts.append((pension.regime, part, plafond is not None))
            taux_cite = max(taux_cite, taux)
        plafonnee = plafond_commun is not None
        retenue_plafonnee = 1.0
        if plafond_commun is not None:
            majoration += min(majoration_plafonnee, plafond_commun)
            if majoration_plafonnee > plafond_commun:
                retenue_plafonnee = plafond_commun / majoration_plafonnee
        if majoration > 0:
            total += majoration
            detail = f"jusqu'à {taux_cite:.0%} selon le régime"
            if plafonnee:
                detail += ", plafonnée en euros à la complémentaire"
            if bornee_au_traitement:
                detail += ", bornée au traitement dans la fonction publique"
            avantages.append(AvantageApplique(
                code="majoration_enfants",
                libelle=("Majoration pour trois enfants et plus"
                         if carriere.nombre_enfants >= 3
                         else "Bonification pour deux enfants"),
                montant=majoration,
                detail=detail,
                par_regime=tuple(
                    (code, part * (retenue_plafonnee if soumise else 1.0))
                    for code, part, soumise in parts
                ),
            ))

    # LES DEUX MINIMA DES EXPLOITANTS AGRICOLES, après la majoration pour
    # enfants, que leurs plafonds comptent : la pension majorée de référence
    # relève la pension de base, puis le complément différentiel ajoute des
    # points de RCO, en comptant la pension relevée. Les ressources sont
    # toutes les pensions à la date d'effet, celles d'autres départs et les
    # pensions étrangères comprises (L. 732-54-3, L. 732-63, V).
    agricole = liquidees.agricole
    if avantages_non_contributifs and agricole is not None:
        etrangeres = _etranger.pensions_etrangeres_servies(
            moteur.macro, carriere, carriere.date_liquidation)
        base = pensions[agricole.indice]
        majoree = pension_majoree(moteur, carriere, agricole, base,
                                  total + servies + etrangeres)
        if majoree is not None and majoree.complement > 0.0:
            pensions[agricole.indice] = replace(
                base, montant=base.montant + majoree.complement,
                detail=(f"{base.detail} = {base.montant:,.2f} €, porté à la pension "
                        f"majorée de référence par + {majoree.complement:,.2f} €"))
            total += majoree.complement
            fiabilite_globale = min(fiabilite_globale, majoree.fiabilite)
            avantages.append(AvantageApplique(
                code="pension_majoree_reference",
                libelle="Pension majorée de référence",
                montant=majoree.complement,
                detail=(f"PMR {majoree.entiere:,.2f} € × {majoree.duree}/"
                        f"{majoree.reference}, au taux plein"
                        + (f", écrêtée au plafond de {majoree.plafond:,.2f} € de toutes "
                           f"les pensions"
                           if majoree.complement < majoree.avant_ecretement - 1e-9 else "")),
                par_regime=((base.regime, majoree.complement),),
            ))
        # Le complément ne s'ajoute qu'à la RCO dont la période le déclare.
        indice_rco = next((i for i, p in enumerate(pensions) if p.regime == RCO), None)
        periode_rco = None
        if indice_rco is not None:
            regime_rco = moteur.catalogue[RCO]
            periode_rco = regime_rco.periode(
                min(annee_liquidation, derniere_annee(regime_rco)))
        valeur = (liquider.valeur_du_point(moteur, RCO, carriere.date_liquidation)
                  if periode_rco is not None and "complement_differentiel_rco"
                  in periode_rco.avantages_non_contributifs else None)
        differentiel = None
        if indice_rco is not None and valeur is not None:
            rco = pensions[indice_rco]
            differentiel = complement_differentiel(
                moteur, carriere, agricole, pensions[agricole.indice].montant,
                rco.montant, points_acquis.get(RCO, 0.0), valeur[0],
                total + servies + etrangeres)
            if differentiel is not None:
                pensions[indice_rco] = replace(
                    rco, montant=rco.montant + differentiel.montant,
                    detail=(f"{rco.detail} = {rco.montant:,.2f} €, complément "
                            f"différentiel de {differentiel.points:,} points"))
                total += differentiel.montant
                fiabilite_globale = min(fiabilite_globale, differentiel.fiabilite,
                                        valeur[1])
                avantages.append(AvantageApplique(
                    code="complement_differentiel_rco",
                    libelle="Complément différentiel de la complémentaire agricole",
                    montant=differentiel.montant,
                    detail=(f"{differentiel.points:,} points : "
                            f"{differentiel.pourcentage:.0%} de 1 820 heures au SMIC "
                            f"net agricole de {differentiel.smic_net:.4f} €, "
                            f"{differentiel.cible:,.2f} € par an, × {differentiel.duree}/"
                            f"{differentiel.reference}"
                            + (", plafonné" if differentiel.plafonne else "")),
                    par_regime=((RCO, differentiel.montant),),
                ))
        # LE RELÈVEMENT DE SEPTEMBRE 2023 ouvre au taux plein les points
        # gratuits et le complément de la RCO des pensions prises avant ; il
        # se calcule ce jour-là (:func:`~retraite_notionnelle.revalorisation.relever_les_exploitants`).
        # Ce qu'il relira s'écrit ici : les points gratuits que la durée
        # requise n'avait pas ouverts, ceux de la liquidation, le complément.
        if indice_rco is not None:
            gratuits = 0.0
            if (RCO not in droits.gratuits and periode_rco is not None
                    and periode_rco.points_gratuits is not None
                    and not (contexte is not None and contexte.neutralise("points_gratuits"))):
                gratuits = acquerir.points_gratuits(
                    moteur, periode_rco, carriere, durees.par_annee["assurance"],
                    durees.trimestres, carriere.age_liquidation or 0.0,
                    au_taux_plein=True)[0]
            chef = ChefDExploitation(
                regime=pensions[agricole.indice].regime, eligible=agricole,
                points=points_acquis.get(RCO, 0.0), gratuits=gratuits,
                complement=differentiel is not None)

    # LES VERSEMENTS UNIQUES, en dernier : ils lisent la pension complétée,
    # minimum, majorations et compléments compris.
    fiabilite_versee = verser_en_capital(moteur, carriere, pensions, avantages,
                                         points_acquis, nature, premiere_retraite)
    if fiabilite_versee is not None:
        fiabilite_globale = min(fiabilite_globale, fiabilite_versee)

    return Complements(
        personne=carriere.personne,
        regimes=tuple(pensions),
        avantages=tuple(avantages),
        total=total,
        minimum_applique=minimum_applique,
        fiabilite=fiabilite_globale,
        plancher=plancher,
        minimum_ecrete=minimum_ecrete,
        petites_pensions=petites_pensions,
        chef=chef,
    )


def _seuil_a_la_date(seuils: list, date_effet: str) -> float | None:
    """Le seuil d'une date d'effet : le dernier du barème, ``[[AAAA-MM-JJ,
    euros], ...]``, dont la date ne la passe pas ; ``None`` avant le premier."""
    retenu = None
    for debut, seuil in seuils:
        if str(debut) <= date_effet:
            retenu = float(seuil)
    return retenu


def coefficient_du_versement(regle: dict, age: float) -> tuple[float, int]:
    """Le coefficient de la table d'une version, à l'âge révolu de ``age``, et
    cet âge : « fonction de l'âge révolu du bénéficiaire à la date d'effet de la
    liquidation des droits ». Un âge hors de la table prend celui de son bout."""
    revolu = int(age + 1e-9)
    coefficients = regle["coefficients"]
    rang = min(max(revolu - int(regle["coefficients_depuis"]), 0), len(coefficients) - 1)
    return float(coefficients[rang]), revolu


def salaire_de_reference_points(moteur, regime: str,
                                annee: int) -> tuple[float, Fiabilite] | None:
    """Le salaire de référence, prix d'achat du point, de ``regime`` en
    ``annee`` : publié, ou, au-delà du dernier barème, le dernier publié mené
    comme la valeur de service du point, au rapport qu'il garde avec elle —
    celui de l'Ircantec le garde depuis 2018, 10,32 € par euro de valeur, hors
    2022. ``None`` sans barème."""
    achat = moteur.valeurs_point.achat(regime, annee)
    if achat is not None:
        return achat[0], achat[2]
    derniere = moteur.valeurs_point.derniere_annee_achetee(regime)
    if derniere is None or annee < derniere:
        return None
    publie = moteur.valeurs_point.achat(regime, derniere)
    valeur_alors = liquider.valeur_du_point(moteur, regime, derniere)
    valeur = liquider.valeur_du_point(moteur, regime, annee)
    if publie is None or valeur_alors is None or valeur is None or valeur_alors[0] <= 0:
        return None
    return (publie[0] * valeur[0] / valeur_alors[0],
            min(publie[2], valeur[1], Fiabilite.MOYENNE))


def verser_en_capital(moteur, carriere: Carriere, pensions: list[PensionRegime],
                      avantages: list[AvantageApplique], points_acquis: dict[str, float],
                      nature: str = "definitive",
                      premiere_retraite: str | None = None) -> Fiabilite | None:
    """Les petites pensions que leur régime ne sert pas : un versement unique
    les remplace, que ``pensions`` porte désormais (``PensionRegime.capital``),
    chacune avec la formule qui le dit ; son montant annuel reste celui de la
    pension remplacée, comme pour le capital du RAFP. Rend la fiabilité des
    barèmes lus quand un versement remplace une pension, ``None`` sinon.

    Trois fiches, lues à la date d'effet :

    * LE VERSEMENT FORFAITAIRE UNIQUE du régime général : quinze fois la pension
      annuelle, avantages complémentaires compris — ici la majoration pour
      enfants —, quand elle est sous le seuil de R. 351-26 ; depuis 2016, à qui
      a pris sa première retraite de base avant (loi n° 2014-40, article 44) ;
    * LE VERSEMENT UNIQUE DE L'AGIRC-ARRCO, la valeur viagère de l'allocation :
      l'allocation annuelle par le coefficient de l'âge révolu, quand elle
      n'excède pas l'équivalent de cent points depuis 2019 (accord du 17
      novembre 2017, article 107) ; avant, l'Arrco jusqu'à cent points, l'Agirc
      sous cinq cents, chacune sur ses propres régimes ;
    * CELUI DE L'IRCANTEC, sous 300 points : les points par le salaire de
      référence de l'année qui précède la liquidation (arrêté du 30 décembre
      1970, article 25).

    La retraite progressive, provisoire, n'est jamais remplacée : l'allocation
    de l'Agirc-Arrco y est servie « dans tous les cas », et le versement du
    régime général fermerait les droits qu'elle continue d'acquérir.
    """
    date_effet = date_d_effet(carriere)
    if date_effet is None or nature == "provisoire":
        return None
    enfants: dict[str, float] = {}
    for avantage in avantages:
        if avantage.code == "majoration_enfants":
            for code, part in avantage.par_regime:
                enfants[code] = enfants.get(code, 0.0) + part
    fiabilites: list[Fiabilite] = []

    def annuelle(pension: PensionRegime) -> float:
        return pension.montant + enfants.get(pension.regime, 0.0)

    def remplacer(indice: int, capital: float, formule: str) -> None:
        pensions[indice] = replace(pensions[indice], capital=capital,
                                   detail=pensions[indice].detail + formule)

    # LE RÉGIME GÉNÉRAL : quinze annuités, sous le seuil de la date d'effet.
    regle = moteur.fiches_datees.regle(FICHE_DU_VERSEMENT_FORFAITAIRE, date_effet)
    avant = None if not regle or not regle["existe"] else regle.get("premiere_retraite_avant")
    if (regle and regle["existe"]
            and (avant is None or (premiere_retraite is not None
                                   and premiere_retraite < str(avant)))):
        seuil = _seuil_a_la_date(regle["seuils"], date_effet)
        multiple = int(regle["multiple"])
        for indice, pension in enumerate(pensions):
            if (seuil is None or pension.regime not in regle["regimes"]
                    or pension.montant <= 0.0 or pension.capital is not None):
                continue
            montant = annuelle(pension)
            if montant >= seuil:
                continue
            remplacer(indice, multiple * montant, (
                f" ; {montant:,.2f} € par an"
                + (", majoration pour enfants comprise" if pension.regime in enfants else "")
                + f", sous le seuil de {seuil:,.2f} € : remplacée par un versement "
                f"forfaitaire unique de {multiple * montant:,.2f} €, {multiple} fois "
                "la pension annuelle"))
            fiabilites.append(Fiabilite.depuis_texte(regle["fiabilite"]))

    # L'AGIRC-ARRCO, ou l'Arrco et l'Agirc : chaque allocation, un groupe de
    # régimes, sa valeur viagère au coefficient de l'âge révolu.
    regle = moteur.fiches_datees.regle(FICHE_DU_VERSEMENT_AGIRC_ARRCO, date_effet)
    if regle and regle["existe"]:
        if regle["mesure"] not in MESURES_DU_VERSEMENT:
            raise ValueError(
                f"{FICHE_DU_VERSEMENT_AGIRC_ARRCO} : la mesure {regle['mesure']!r} n'est "
                f"pas de celles que le moteur connaît, {MESURES_DU_VERSEMENT}")
        coefficient, age = coefficient_du_versement(regle, carriere.age_liquidation or 0.0)
        for allocation in regle["allocations"]:
            membres = [indice for indice, pension in enumerate(pensions)
                       if pension.regime in allocation["regimes"]
                       and pension.montant > 0.0 and pension.capital is None]
            if not membres:
                continue
            seuil_points = float(allocation["seuil_points"])
            if regle["mesure"] == "points":
                mesure = somme_ordonnee(points_acquis.get(pensions[i].regime, 0.0)
                                        for i in membres)
                seuil, unite = seuil_points, "points"
                dit = f"{mesure:,.2f} points"
            else:
                valeur = liquider.valeur_du_point(moteur, allocation["point"],
                                                  carriere.date_liquidation)
                if valeur is None:
                    continue
                mesure = somme_ordonnee(annuelle(pensions[i]) for i in membres)
                seuil, unite = seuil_points * valeur[0], "€"
                dit = f"{mesure:,.2f} € par an"
                fiabilites.append(valeur[1])
            sous = (mesure <= seuil if allocation["seuil_compris"] else mesure < seuil)
            if mesure <= 0.0 or not sous:
                continue
            borne = (f"au plus {seuil_points:,.0f} points" if allocation["seuil_compris"]
                     else f"moins de {seuil_points:,.0f} points")
            if unite == "€":
                borne += f", {seuil:,.2f} €"
            for indice in membres:
                montant = annuelle(pensions[indice])
                remplacer(indice, montant * coefficient, (
                    f" ; allocation de {dit}, {borne} : versée en capital, "
                    f"{montant * coefficient:,.2f} € ({montant:,.2f} € × {coefficient:.1f} "
                    f"à {age} ans)"))
            fiabilites.append(Fiabilite.depuis_texte(regle["fiabilite"]))

    # L'IRCANTEC : les points, par le salaire de référence de l'année d'avant.
    regle = moteur.fiches_datees.regle(FICHE_DU_VERSEMENT_IRCANTEC, date_effet)
    if regle and regle["existe"]:
        annee = carriere.annee_liquidation - 1
        for indice, pension in enumerate(pensions):
            if (pension.regime not in regle["regimes"] or pension.montant <= 0.0
                    or pension.capital is not None):
                continue
            points = points_acquis.get(pension.regime, 0.0)
            if not 0.0 < points < float(regle["seuil_points"]):
                continue
            reference = salaire_de_reference_points(moteur, pension.regime, annee)
            if reference is None:
                continue
            remplacer(indice, points * reference[0], (
                f" ; {points:,.2f} points, moins de {float(regle['seuil_points']):,.0f} : "
                f"versée en capital, {points * reference[0]:,.2f} € ({points:,.2f} points "
                f"× salaire de référence de {annee}, {reference[0]:.4f} €)"))
            fiabilites.extend((reference[1], Fiabilite.depuis_texte(regle["fiabilite"])))
    return min(fiabilites) if fiabilites else None


def plafond_majoration(moteur, code: str, periode: PeriodeRegime,
                        carriere: Carriere,
                        annee_liquidation: int) -> float | None:
    """Plafond en euros de la majoration pour enfants, ou ``None``.

    Les régimes de base servent 10 % sans plafond ; l'Agirc-Arrco, elle,
    borne la majoration en euros — 2 367,48 € par an pour les pensions servies
    depuis le 1er novembre 2024, gelés en 2025 — et le plafond est revalorisé comme la
    valeur de service du point, à laquelle il est donc rapporté ici. Sans
    lui, les familles très nombreuses de salariés du privé étaient
    surestimées.

    Le plafond ne s'oppose qu'aux assurés nés à compter du 2 août 1951 : le
    modèle ne connaît que l'année de naissance et retient les générations à
    partir de 1952, comme il le fait des autres bornes coupées en cours
    d'année.

    Le plafond publié est celui du 31 décembre de son année ; celui d'une
    pension, celui de sa date d'effet, comme la valeur du point qu'il suit.
    """
    if periode.plafond_majoration_enfants is None:
        return None
    if carriere.annee_naissance < 1952:
        return None
    plafond = periode.plafond_majoration_enfants
    annee_reference = periode.plafond_majoration_annee
    if annee_reference is None:
        return plafond
    servie = liquider.valeur_du_point(moteur, code, carriere.date_liquidation)
    publiee = liquider.valeur_du_point(moteur, code, annee_reference)
    if servie is None or publiee is None or publiee[0] <= 0:
        return plafond * moteur.macro.coefficient_prix(
            annee_reference, annee_liquidation
        )
    return plafond * servie[0] / publiee[0]


def plafond_de_l_article_l18(moteur, carriere: Carriere) -> dict | None:
    """La version du plafond de L. 18 qui vaut à la date d'effet de la
    pension (fiche ``majoration_enfants_plafond_fonction_publique``) ;
    ``None`` quand aucun plafond ne la borne. Un plafond ou une surcote que le
    moteur ne connaît pas l'arrête (§ 6.7)."""
    version = moteur.fiches_datees.version(
        FICHE_DU_PLAFOND_L18, date_d_effet(carriere) or ouvrir.SANS_DATE_D_EFFET)
    if version is None or not version["parametres"].get("existe"):
        return None
    parametres = version["parametres"]
    if parametres["plafond"] not in PLAFONDS_DE_L18:
        raise ValueError(f"{FICHE_DU_PLAFOND_L18}.{version['id']} : plafond inconnu, "
                         f"{parametres['plafond']!r}")
    if parametres["surcote"] not in SURCOTES_DE_L18:
        raise ValueError(f"{FICHE_DU_PLAFOND_L18}.{version['id']} : surcote inconnue, "
                         f"{parametres['surcote']!r}")
    return version


def majoration_sous_le_traitement(montant: float, majoration: float, traitement: float,
                                  surcote: float, hors_du_plafond: bool) -> float:
    """La majoration pour enfants d'une pension du code des pensions, sous le
    plafond de L. 18, V : « sans que le montant de la pension majorée puisse
    excéder le montant du traitement ».

    La majoration cède seule, la pension jamais : en 2017, la caisse ne
    servait pas la majoration à qui la surcote portait déjà à 104 % du
    traitement, sans réduire sa pension (Conseil d'État, 29 décembre 2020,
    n° 428626, point 1). Le texte réduit, depuis 2004 et 2012, la pension et
    la majoration « à due proportion » : le total est le même, la part de la
    majoration plus forte.

    ``hors_du_plafond`` : depuis cette décision, la pension qu'on compare au
    traitement est celle d'avant ``surcote``, ce que la surcote lui ajoute —
    elle « ne fait plus l'objet d'un plafonnement depuis la loi du 9 novembre
    2010 » (point 10) —, et la surcote est servie au-delà (« Pension + ME =
    100 % ; surcote servie sans plafond », CNRACL). Huit enfants au taux de
    80 %, avec une surcote de 25 % : le traitement et la surcote, 120 % du
    traitement ; sans surcote, 100 %.
    """
    base = montant - surcote if hors_du_plafond else montant
    return max(0.0, min(majoration, traitement - base))


def _taux_majoration_enfants(regime, nombre_enfants: int,
                             periode: PeriodeRegime | None = None) -> float:
    """Taux de majoration pour enfants, régime par régime.

    Le régime général sert 10 % à partir de trois enfants. La fonction
    publique y ajoute 5 % par enfant au-delà du troisième. Une fiche qui porte
    son propre barème l'emporte : les régimes spéciaux, dont la plupart suivent
    la fonction publique et la Banque de France sert 8,5 % puis 4,25 % par
    enfant, les marins, qui bonifient dès deux enfants. Les points de
    l'Agirc-Arrco ont un taux par année d'acquisition, que
    :class:`~retraite_notionnelle.scenarios.actuel.MajorationsEnfantsPoints`
    porte et que l'appelant substitue à celui-ci ; leur plafond en euros est
    :func:`plafond_majoration`. Celle de la fonction publique cède au
    traitement : :func:`majoration_sous_le_traitement`.
    """
    if periode is not None and periode.taux_majoration_enfants:
        bareme = periode.taux_majoration_enfants
        return bareme[min(nombre_enfants, len(bareme) - 1)]
    if nombre_enfants < 3:
        return 0.0
    if regime.famille == "fonction_publique":
        return 0.10 + 0.05 * (nombre_enfants - 3)
    return 0.10


def _trimestres_entre_dates(carriere: Carriere, debut: DateMois, fin: DateMois,
                            cotises_seulement: bool) -> int:
    """Trimestres acquis entre deux DATES, au mois près — ``fin`` exclue.

    Le pas du moteur est l'année, et les deux aides voisines comparent l'âge
    atteint dans l'année à un seuil. C'est juste quand le seuil tombe sur un
    âge entier ; c'est faux quand il tombe en cours d'année, ce qui est
    devenu la règle depuis que l'âge légal compte des mois. Chaque ligne voit
    ici ses trimestres répartis sur ses mois — les premiers de l'année pour
    celle du départ, les derniers pour celle de l'entrée —, et seuls comptent
    ceux de la plage ; la somme est arrondie au trimestre inférieur.
    """
    total = 0.0
    for ligne in carriere.lignes:
        if cotises_seulement and not ligne.cotise:
            continue
        total += _trimestres_de_la_ligne_entre(carriere, ligne, debut, fin)
    return int(total + 1e-9)
