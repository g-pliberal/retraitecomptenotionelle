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
* LA MAJORATION POUR ENFANTS enfin, sur ce plancher, plafonnée en euros à la
  complémentaire (:func:`plafond_majoration`).

L'ASPA n'en est pas : elle regarde toutes les ressources, c'est l'étape
« foyer et net » (:mod:`.foyer`).

Ce que l'étape écrit, :class:`Complements`, suit son schéma,
``data/reference/etapes/completer_tous_regimes.yaml``. Son jumeau est
``moteur/js/droit/completer.js``.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from ..donnees.chargement import Fiabilite
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
}

#: Première date d'effet, (année, mois), où la surcote s'AJOUTE au minimum
#: contributif au lieu d'entrer dans la pension qu'on lui compare : décret
#: n° 2008-1509 du 30 décembre 2008, dernier alinéa de D. 351-2-1.
SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS = (2009, 4)


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
              recalcul: bool = True, nationales: Pensions | None = None) -> Complements:
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
    ``minimum_contributif_international``).
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
    total = somme_ordonnee(p.montant for p in pensions)
    avantages: list[AvantageApplique] = []
    fiabilite_globale = Fiabilite.CERTIFIEE
    minimum_applique = False
    minimum_ecrete: MinimumEcrete | None = None

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
            ))

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
        for pension in pensions:
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


    return Complements(
        personne=carriere.personne,
        regimes=tuple(pensions),
        avantages=tuple(avantages),
        total=total,
        minimum_applique=minimum_applique,
        fiabilite=fiabilite_globale,
        plancher=plancher,
        minimum_ecrete=minimum_ecrete,
    )


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
    :func:`plafond_majoration`.
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
