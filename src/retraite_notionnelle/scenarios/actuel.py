"""Scénario 1 — le système actuel, tel qu'il est.

Ce scénario sert d'étalon : c'est la pension que l'assuré perçoit ou percevra
en droit constant. Il conserve tout ce que les scénarios notionnels retirent —
minima, majorations, trimestres gratuits, décote et surcote, bonifications.

Portée et limites
-----------------
Reproduire exactement le droit positif de tous les régimes depuis 1930
supposerait un moteur législatif complet, du type de ceux de la DREES
(TRAJECTOiRE) ou de l'Institut des politiques publiques (PENSIPP). Ce module
est une **approximation documentée**, pas un simulateur officiel :

* régimes en annuités — formule ``taux × salaire de référence × durée / durée
  requise``, avec décote et surcote de la période ;
* régimes en points — la pension est calculée **en points**. Deux façons de les
  acquérir, selon ce que la caisse publie : par un PRIX D'ACHAT, la cotisation
  de l'année étant divisée par le salaire de référence de cette année-là
  (``regimes/valeurs_point.csv``) ; ou par un BARÈME EN POINTS, le régime
  annonçant combien de points ouvre une assiette donnée — 525 points au plafond
  au régime de base des libéraux, 100 points pour 1 820 SMIC à la complémentaire
  agricole. Le total est converti en rente par la valeur de service de l'année
  de liquidation. Les points d'un régime fermé sont convertis dans son
  successeur au rapport des deux valeurs de service, comme l'ont fait
  l'unification Arrco de 1999 et la fusion Agirc-Arrco de 2019. Restent au
  rendement instantané (``regimes/rendements_points.csv``) les complémentaires
  des sections libérales et de l'IRCEC, dont les caisses publient un rendement
  ou un barème annuel mais aucune série de prix d'achat, quelques petits
  régimes — CAFAT, tranche B de la Polynésie, additionnel des enseignants du
  privé, gérants de débits de tabac, conjoints du bâtiment —, et les années
  postérieures au dernier barème publié, sauf là où le texte dit ce que suit
  le prix d'achat : l'Agirc-Arrco, dont le salaire de référence suit le
  salaire moyen (``regimes/prolongement_points.csv``) ;
* trois horloges, comme dans le droit — ce qui s'ACQUIERT est lu à l'année
  travaillée (taux de cotisation, assiette, plafond, prix d'achat du point,
  heures pour valider un trimestre) ; ce qui commande la MONTÉE EN CHARGE des
  réformes est lu à la GÉNÉRATION (durée requise, âge d'ouverture, âge
  d'annulation de la décote, coefficient de minoration, années retenues au
  salaire de référence) ; ce qui LIQUIDE est lu à l'année de liquidation
  (formule du régime, valeur de service du point, barèmes des minima) ;
* avantages datés — la fiche de chaque période dit ce que le régime accordait
  cette année-là, et le moteur ne sert que cela : ni minimum contributif avant
  1983, ni surcote avant 2004, ni trimestres pour enfants avant 1972.

Un écart de quelques pour cent avec la pension réelle est donc attendu.
Ce que le modèle mesure de façon robuste, ce sont les ÉCARTS ENTRE SCÉNARIOS,
tous calculés sur les mêmes carrières et les mêmes séries.

Où est le calcul
----------------
Les TABLES du droit en vigueur sont sous ``donnees/tables_du_droit.py``
(action 161), d'où ce module les reprend ; il garde le moteur qui les tient,
:class:`ScenarioActuel`. Le calcul est dans ``droit/`` (docs/architecture.md,
§ 7.2 et 7.3) : l'acquisition construit le relevé des droits, puis
:func:`~retraite_notionnelle.droit.liquidation.liquider`, une fonction pure,
ouvre le droit, liquide chaque régime et complète tous régimes ; l'ASPA vient
ensuite, de l'étape « foyer et net ». :meth:`ScenarioActuel.calculer` les
enchaîne. Les fiches et leurs versions remplaceront les tables (phase 6).
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from ..calendrier import DateMois
from ..carriere import Affiliations, Carriere
from ..config import Parametres
from ..donnees.chargement import Fiabilite
from ..donnees.macro import DonneesMacro
from ..donnees.minimum_vieillesse import DeuxEtages, MinimumVieillesse  # noqa: F401  (repris d'ici)
from ..donnees.prelevements_historiques import charger_prelevements_historiques
from ..donnees.regimes import CatalogueRegimes, ClassesCotisation, SalairesForfaitaires
from ..droit import coordonner
from ..droit import departs as _departs
from ..droit import foyer as _foyer
from ..droit import invalidite as _invalidite
from ..droit import limite_age as _limite_age
from ..droit import liquidation as _liquidation
from ..droit import progressive as _progressive
# Ce que les étapes créent, que les appelants du scénario 1 lisent ici.
from ..droit.commun import AvantageApplique, PensionRegime  # noqa: F401
from ..droit.commun import fusionner_les_charges
from ..revalorisation import RevalorisationsPensions, mener_au_mois
from ..somme import somme_ordonnee
from ..types_du_pont.resultats import DepartServi, ProgressiveServie, ResultatActuel  # noqa: F401  (types du pont, action 161)
from ..types_du_pont.droit import ConversionPoint, DerogationActive, TrimestresAccordes  # noqa: F401  (types du pont, action 161)
# Les tables du droit en vigueur, relogées sous ``donnees/`` (action 161),
# que le moteur et les appelants du scénario 1 lisent encore ici.
from ..donnees.tables_du_droit import (  # noqa: F401  (reprises d'ici)
    Rendements, TableParGeneration, DureesRequises, DureesRequisesAvantSuspension,
    DureesRequisesAvantReforme2023, _rang_mois, DureesRequisesRegimes,
    CalendriersDureeRequise, _age_ou_rien, AgesRegimes, DureesRequisesFonctionPublique,
    DureesRequisesAvantSoixanteAns, DureesProratisation, AgesOuverture,
    AgesOuvertureAvantReforme2023, AgesOuvertureAvantSuspension, TableRecouverte,
    AgesSurcoteRegimesSpeciaux, AgesAnnulationDecote, AgesCategorieActive,
    DureesServicesMilitaires, DureesServicesActifs, AgesJouissanceMilitaire,
    CoefficientsMinoration, AnneesSalaireReference, AnneesRevenuAnnuelMoyenIndependants,
    FichesDatees, MajorationsPourEnfants, Reversions, Invalidites, CarrieresHorsDeFrance,
    ServicesOuvrantPension, SurcoteParentale, MajorationsEnfantsPoints,
    DecoteFonctionPublique, DecoteRegimesSpeciaux, MaximumDesCultes, CarriereLongue,
    SurcoteBaremes, MinimumGaranti, BaremesTrimestre, ConversionsPoints, ValeursPoint,
    PENSION_MINIMUM, REGLE_DU_MINIMUM_EN_VIGUEUR, MinimumContributif, SANS_PENSION_MAJOREE,
    PMR_SUR_LES_PRIX, PensionMajoreeReference, SANS_COMPLEMENT_DIFFERENTIEL,
    ComplementDifferentielRco,
)

if TYPE_CHECKING:
    from ..droit.foyer import Foyer
    from ..droit.liquidation import Liquidation


def progressive_servie(moteur: ScenarioActuel, progressive: _progressive.Progressive,
                       provisoire: Liquidation | None, depart: DateMois) -> ProgressiveServie:
    """La retraite progressive, telle que le résultat la dit, pour un départ
    à ``depart``."""
    provisoire_total = provisoire.total if provisoire is not None else 0.0
    return ProgressiveServie(
        date_effet=progressive.date_effet, quotite=progressive.quotite,
        motif=progressive.motif, fraction=progressive.fraction,
        regimes=tuple(sorted(progressive.regimes)),
        montant_provisoire=provisoire_total,
        montant_servi=progressive.fraction * provisoire_total,
        age_minimum=progressive.age_minimum, duree_requise=progressive.duree_requise,
        trimestres=progressive.trimestres,
        recalculee=_progressive.recalculee(moteur, depart))


def resultat_actuel(liquidation: Liquidation, foyer: Foyer) -> ResultatActuel:
    """Le scénario 1 à une date d'effet : la liquidation, puis ce que l'étape
    « foyer et net » y ajoute — l'ASPA, qui complète tout le reste,
    majorations comprises, jusqu'au montant du barème."""
    total = liquidation.total
    avantages = list(liquidation.avantages)
    fiabilite = liquidation.fiabilite
    if foyer.minimum_vieillesse > 0:
        # Le barème, moins ce que les pensions étrangères, servies à part, en
        # remplissent ; dans un couple, la pension et la part de l'allocation.
        total = foyer.servie_avec(total)
        fiabilite = min(fiabilite, foyer.fiabilite)
        avantages.append(foyer.avantage())
    return ResultatActuel(
        pension_annuelle=max(0.0, total - liquidation.hors_repartition),
        pension_hors_repartition=liquidation.hors_repartition,
        pensions_par_regime=list(liquidation.regimes),
        avantages_appliques=avantages,
        total_contributif=liquidation.total_contributif,
        trimestres_valides=(liquidation.releve.durees.trimestres
                            + liquidation.releve.durees.trimestres_etrangers),
        trimestres_etrangers=liquidation.releve.durees.trimestres_etrangers,
        trimestres_requis=liquidation.pensions.requis,
        taux_liquidation=liquidation.pensions.taux,
        minimum_applique=liquidation.complements.minimum_applique,
        age_ouverture_opposable=liquidation.ouverture.age,
        liquidation_ouverte=liquidation.ouverture.ouverte,
        motif_ouverture=liquidation.ouverture.motif,
        fiabilite=fiabilite,
        minimum_ecrete=liquidation.complements.minimum_ecrete,
        petites_pensions=liquidation.complements.petites_pensions,
        chef_d_exploitation=liquidation.complements.chef,
        exploitant_agricole=liquidation.complements.exploitant,
    )


def _ramener(moteur, depart: _departs.Depart, declare: DateMois,
             pensions) -> list[float]:
    """Ce qui mène chaque pension d'un départ aux euros du départ déclaré :
    la revalorisation de son régime pour une pension déjà servie, les prix
    pour une pension qui ne commence qu'après."""
    if depart.date == declare:
        return [1.0] * len(pensions)
    if depart.date > declare:
        return [moteur.macro.coefficient_prix(depart.date.annee, declare.annee)] * len(pensions)
    menes = mener_au_mois(moteur, pensions, depart.date, declare)
    return [mene / pension.montant if pension.montant else 1.0
            for pension, mene in zip(pensions, menes)]


def _detail_date(detail: str, depart: _departs.Depart, declare: DateMois,
                 montant: float, ramene: float) -> str:
    """La formule d'une pension datée, et ce qu'elle vaut au départ déclaré."""
    if depart.date == declare:
        return detail
    if depart.date < declare:
        return (f"{detail} ; servie depuis le 1er {depart.date}, {montant:,.2f} € à "
                f"cette date, {ramene:,.2f} € au départ")
    return (f"{detail} ; servie à partir du 1er {depart.date}, {montant:,.2f} € de "
            f"{depart.date.annee}, soit {ramene:,.2f} € de {declare.annee}")


def resultat_des_departs(moteur, carriere: Carriere, departs, liquidations,
                         contexte) -> ResultatActuel:
    """Le scénario 1 d'une carrière dont les régimes liquident à des dates
    différentes (:mod:`~retraite_notionnelle.droit.departs`).

    LES MONTANTS SONT CEUX DU DÉPART DÉCLARÉ, pour que la page compare les six
    systèmes à la même date : la pension déjà servie y est menée par la
    revalorisation de son régime, celle qui ne commence qu'après y est
    ramenée par les prix. ``pension_annuelle`` est donc la pension COMPLÈTE,
    celle qu'on touche une fois tous les régimes liquidés, en euros du départ ;
    :attr:`ResultatActuel.departs` dit ce que chaque départ y ajoute, et
    quand. Chaque pension garde sa date d'effet et son montant à cette date,
    que « faire vivre » reprend. Les durées, le taux et l'ouverture sont ceux
    de la liquidation du départ déclaré ; l'ASPA se lit à ce départ, sur la
    pension complète.
    """
    declare = carriere.date_liquidation
    principale = next((liquidation for depart, liquidation in zip(departs, liquidations)
                       if depart.date == declare), liquidations[-1])
    isoler = moteur.parametres.isoler_capitalisation
    pensions = []
    avantages: dict[str, AvantageApplique] = {}
    servis = []
    total = hors_repartition = total_contributif = 0.0
    fiabilite = Fiabilite.CERTIFIEE
    for depart, liquidation in zip(departs, liquidations):
        regimes = list(liquidation.regimes)
        facteurs = _ramener(moteur, depart, declare, regimes)
        par_regime = {p.regime: f for p, f in zip(regimes, facteurs)}
        nues = somme_ordonnee(p.montant for p in regimes)
        moyen = (somme_ordonnee(p.montant * f for p, f in zip(regimes, facteurs)) / nues
                 if nues else (facteurs[0] if facteurs else 1.0))
        for pension, facteur in zip(regimes, facteurs):
            ramene = pension.montant * facteur
            # Ce que la réversion lit du maximum des pensions est aux euros du
            # montant : ramené comme lui.
            pensions.append(replace(
                pension, montant=ramene, date_effet=depart.date_effet,
                montant_a_l_effet=pension.montant,
                detail=_detail_date(pension.detail, depart, declare, pension.montant, ramene),
                ecretement_du_maximum=pension.ecretement_du_maximum * facteur,
                surcote=pension.surcote * facteur))
            if isoler and moteur.catalogue[pension.regime].hors_repartition:
                hors_repartition += ramene
        majoration = 0.0
        for avantage in liquidation.avantages:
            parts = tuple((code, part * par_regime.get(code, moyen))
                          for code, part in avantage.par_regime)
            # Celles de la majoration sans le coefficient d'anticipation, de même.
            sans_anticipation = tuple((code, part * par_regime.get(code, moyen))
                                      for code, part in avantage.par_regime_sans_anticipation)
            montant = (somme_ordonnee(part for _, part in parts) if parts
                       else avantage.montant * moyen)
            # Les étapes des enfants à charge sont ramenées comme les parts.
            a_charge = tuple(
                (depuis, tuple((code, part * par_regime.get(code, moyen)) for code, part in etape))
                for depuis, etape in avantage.a_charge)
            if avantage.code == "majoration_enfants":
                majoration += montant
            deja = avantages.get(avantage.code)
            if deja is None:
                avantages[avantage.code] = replace(
                    avantage, montant=montant, par_regime=parts,
                    par_regime_sans_anticipation=sans_anticipation, a_charge=a_charge)
            else:
                details = [d for d in (deja.detail, avantage.detail) if d]
                avantages[avantage.code] = replace(
                    deja, montant=deja.montant + montant,
                    detail=" ; ".join(dict.fromkeys(details)),
                    par_regime=deja.par_regime + parts,
                    par_regime_sans_anticipation=(deja.par_regime_sans_anticipation
                                                  + sans_anticipation),
                    a_charge=fusionner_les_charges(deja.a_charge, a_charge))
        servi = somme_ordonnee(p.montant * f for p, f in zip(regimes, facteurs)) + majoration
        total += servi
        total_contributif += liquidation.total_contributif * moyen
        fiabilite = min(fiabilite, liquidation.fiabilite)
        servis.append(_departs_servi(depart, liquidation, servi))
    foyer = _foyer.foyer_et_net(
        moteur, carriere.personne, _departs.Depart(declare).date_effet, declare.annee,
        total, (carriere.age_liquidation or 0.0) >= _invalidite.age_de_l_aspa(moteur, carriere),
        contexte, carriere=carriere)
    liste = list(avantages.values())
    if foyer.minimum_vieillesse > 0:
        total = foyer.servie_avec(total)
        fiabilite = min(fiabilite, foyer.fiabilite)
        liste.append(foyer.avantage())
    return ResultatActuel(
        pension_annuelle=max(0.0, total - hors_repartition),
        pension_hors_repartition=hors_repartition,
        pensions_par_regime=pensions,
        avantages_appliques=liste,
        total_contributif=total_contributif,
        trimestres_valides=(principale.releve.durees.trimestres
                            + principale.releve.durees.trimestres_etrangers),
        trimestres_etrangers=principale.releve.durees.trimestres_etrangers,
        trimestres_requis=principale.pensions.requis,
        taux_liquidation=principale.pensions.taux,
        minimum_applique=any(l.complements.minimum_applique for l in liquidations),
        age_ouverture_opposable=principale.ouverture.age,
        liquidation_ouverte=all(l.ouverture.ouverte for l in liquidations),
        motif_ouverture=principale.ouverture.motif,
        fiabilite=fiabilite,
        departs=tuple(servis),
        petites_pensions=tuple(petite for liquidation in liquidations
                               for petite in liquidation.complements.petites_pensions),
        chef_d_exploitation=next((liquidation.complements.chef for liquidation in liquidations
                                  if liquidation.complements.chef is not None), None),
        exploitant_agricole=next((liquidation.complements.exploitant
                                  for liquidation in liquidations
                                  if liquidation.complements.exploitant is not None), None),
    )


def etat_du_depart(moteur, carriere: Carriere, plancher: tuple | None,
                   journal: object | None = None) -> _liquidation.Etat:
    """L'état du départ unique : la carrière, et, après une retraite
    progressive, la pension provisoire de ses régimes de base, menée au
    départ, que la pension complète garde (:mod:`~retraite_notionnelle.droit.progressive`)."""
    if plancher is None:
        return _liquidation.Etat(carriere, journal)
    progressive, provisoire = plancher
    return _liquidation.Etat(
        carriere, journal,
        initiales=_progressive.initiales(moteur, progressive, provisoire,
                                         carriere.date_liquidation),
        recalcul=_progressive.recalculee(moteur, carriere.date_liquidation))


def _departs_servi(depart, liquidation, servi: float) -> DepartServi:
    """Ce qu'un départ ajoute à la pension, dans les deux euros."""
    a_l_effet = somme_ordonnee(p.montant for p in liquidation.regimes) + somme_ordonnee(
        a.montant for a in liquidation.complements.avantages if a.code == "majoration_enfants")
    return DepartServi(
        date_effet=depart.date_effet, motif=depart.motif,
        regimes=tuple(p.regime for p in liquidation.regimes),
        montant=servi, montant_a_l_effet=a_l_effet)


#: Les droits contrefactuels du scénario 1 (action 138, étape 10), et la date
#: d'effet des textes que chacun écarte : la loi de 2023 sans la suspension
#: écarte l'article 105 de la loi n° 2025-1403 du 30 décembre 2025, qui vaut
#: pour les pensions prenant effet à compter du 1er septembre 2026 ; le droit
#: au 31 août 2023, la loi n° 2023-270 du 14 avril 2023, qui vaut à compter du
#: 1er septembre 2023, et la suspension avec elle. Ils ne changent que l'âge
#: légal, la durée requise et les âges de la carrière longue
#: (:meth:`ScenarioActuel._sous_le_droit`) : le reste du droit est celui
#: d'aujourd'hui.
DROITS_CONTREFACTUELS: dict[str, DateMois] = {
    "loi_2023_sans_suspension": DateMois(2026, 9),
    "au_31_aout_2023": DateMois(2023, 9),
}


class ScenarioActuel:
    """Le moteur du scénario 1 : les tables du droit en vigueur, que les
    étapes de ``droit/`` lisent, et :meth:`calculer`, qui les enchaîne."""

    def __init__(self, macro: DonneesMacro, catalogue: CatalogueRegimes,
                 affiliations: Affiliations, parametres: Parametres) -> None:
        self.macro = macro
        self.catalogue = catalogue
        self.affiliations = affiliations
        self.parametres = parametres
        self.rendements = Rendements(parametres.racine_donnees)
        self.valeurs_point = ValeursPoint(parametres.racine_donnees,
                                          parametres.conventions_cor)
        self.conversions_points = ConversionsPoints(parametres.racine_donnees)
        self.classes = ClassesCotisation(parametres.racine_donnees)
        self.grilles = SalairesForfaitaires(parametres.racine_donnees)
        self.durees_requises = DureesRequises(parametres.racine_donnees)
        self.durees_requises_avant_reforme_2023 = DureesRequisesAvantReforme2023(
            parametres.racine_donnees)
        self.durees_requises_avant_suspension = DureesRequisesAvantSuspension(
            parametres.racine_donnees)
        self.durees_requises_regimes = DureesRequisesRegimes(parametres.racine_donnees)
        self.calendriers_duree_requise = CalendriersDureeRequise(
            parametres.racine_donnees
        )
        self.durees_proratisation = DureesProratisation(parametres.racine_donnees)
        self.ages_ouverture = AgesOuverture(parametres.racine_donnees)
        self.ages_surcote_regimes_speciaux = AgesSurcoteRegimesSpeciaux(
            parametres.racine_donnees
        )
        self.ages_annulation_decote = AgesAnnulationDecote(parametres.racine_donnees)
        self.ages_regimes = AgesRegimes(parametres.racine_donnees)
        self.ages_categorie_active = AgesCategorieActive(parametres.racine_donnees)
        self.durees_services_militaires = DureesServicesMilitaires(
            parametres.racine_donnees
        )
        self.durees_services_actifs = DureesServicesActifs(parametres.racine_donnees)
        self.ages_jouissance_militaire = AgesJouissanceMilitaire(
            parametres.racine_donnees
        )
        self.coefficients_minoration = CoefficientsMinoration(parametres.racine_donnees)
        self.annees_salaire_reference = AnneesSalaireReference(parametres.racine_donnees)
        self.annees_revenu_independants = AnneesRevenuAnnuelMoyenIndependants(
            parametres.racine_donnees)
        #: Les règles datées du salaire annuel moyen : voir :class:`FichesDatees`.
        self.fiches_datees = FichesDatees(parametres.racine_donnees)
        self.majorations_enfants = MajorationsPourEnfants(parametres.racine_donnees)
        self.reversions = Reversions(parametres.racine_donnees)
        self.invalidites = Invalidites(parametres.racine_donnees)
        self.carrieres_hors_de_france = CarrieresHorsDeFrance(parametres.racine_donnees)
        self.services_ouvrant_pension = ServicesOuvrantPension(parametres.racine_donnees)
        self.surcote_parentale = SurcoteParentale(parametres.racine_donnees)
        self.majorations_enfants_points = MajorationsEnfantsPoints(
            parametres.racine_donnees)
        self.durees_requises_fonction_publique = DureesRequisesFonctionPublique(
            parametres.racine_donnees
        )
        self.durees_requises_avant_soixante_ans = DureesRequisesAvantSoixanteAns(
            parametres.racine_donnees
        )
        self.decote_fonction_publique = DecoteFonctionPublique(
            parametres.racine_donnees
        )
        self.decote_regimes_speciaux = DecoteRegimesSpeciaux(
            parametres.racine_donnees
        )
        self.minimum_contributif = MinimumContributif(parametres.racine_donnees, macro)
        self.minimum_garanti = MinimumGaranti(parametres.racine_donnees, macro)
        #: Les deux minima des exploitants agricoles : voir
        #: :func:`~retraite_notionnelle.droit.completer.pension_majoree` et
        #: :func:`~retraite_notionnelle.droit.completer.complement_differentiel`.
        self.pension_majoree_reference = PensionMajoreeReference(
            parametres.racine_donnees, macro)
        self.complement_differentiel_rco = ComplementDifferentielRco(
            parametres.racine_donnees, macro)
        self.baremes_trimestre = BaremesTrimestre(parametres.racine_donnees, macro)
        #: Les prélèvements des pensions de chaque année, dont le cumul de
        #: l'artisan, du commerçant et du libéral tire la pension nette que le
        #: dépassement épuise (:mod:`~retraite_notionnelle.droit.cumul`).
        self.prelevements_historiques = charger_prelevements_historiques(
            parametres.racine_donnees)
        #: Les revalorisations des pensions servies, qui portent aussi le
        #: traitement d'une pension différée : voir
        #: :func:`~retraite_notionnelle.revalorisation.coefficient_traitement_differe`.
        self.revalorisations_pensions = RevalorisationsPensions(parametres.racine_donnees)
        #: Le maximum de la pension des cultes, que la fraction d'avant 1998
        #: proratise : voir :mod:`~retraite_notionnelle.droit.cultes`.
        self.maximum_des_cultes = MaximumDesCultes(
            parametres.racine_donnees, macro, self.revalorisations_pensions)
        self.carriere_longue = CarriereLongue(parametres.racine_donnees)
        #: Vrai pendant que :func:`~retraite_notionnelle.droit.ouvrir.ouverture_carriere_longue` date le droit :
        #: la condition de durée qu'elle lit est celle de la génération, et non
        #: celle que ce droit fait ensuite opposer au taux plein.
        self._ouverture_carriere_longue_en_cours = False
        self.surcote_baremes = SurcoteBaremes(parametres.racine_donnees)
        self.minimum_vieillesse = MinimumVieillesse(parametres.racine_donnees, macro)
        #: Les régimes qui attribuent des POINTS GRATUITS, rangés sous le régime
        #: de base dont les années les ouvrent : une carrière qui n'a validé
        #: aucun trimestre dans ce dernier n'a rien à chercher. Voir
        #: :func:`~retraite_notionnelle.droit.acquerir.points_gratuits`.
        self.points_gratuits_par_base: dict[str, tuple[str, ...]] = {}
        for regime in catalogue:
            for periode in regime.periodes:
                if periode.points_gratuits is None:
                    continue
                base = periode.points_gratuits.regime
                attribuants = self.points_gratuits_par_base.get(base, ())
                if regime.code not in attribuants:
                    self.points_gratuits_par_base[base] = (*attribuants, regime.code)
        if parametres.droit_contrefactuel is not None:
            self._sous_le_droit(parametres.droit_contrefactuel)

    def _sous_le_droit(self, droit: str) -> None:
        """Le moteur sous un droit contrefactuel (:data:`DROITS_CONTREFACTUELS`).

        Trois tables changent, et rien d'autre. L'âge légal et la durée requise
        de la génération sont ceux des textes d'avant la date que le droit
        écarte, posés sur les tables du droit en vigueur
        (:class:`TableRecouverte`) : D. 161-2-1-9 et L. 161-17-3 dans leurs
        versions du 1er septembre 2023 pour la loi de 2023 sans la suspension,
        dans celles de 2011 et de 2014 pour le droit au 31 août 2023. La
        carrière longue perd les décrets qui prennent effet à compter de cette
        date (:meth:`CarriereLongue.avant`). Et la durée que le droit en vigueur
        garde aux pensions d'avant septembre 2026
        (:func:`~retraite_notionnelle.droit.ouvrir.duree_requise`) devient, au
        31 août 2023, celle de 2014 : sans la loi de 2023, rien n'est à garder.
        """
        if droit not in DROITS_CONTREFACTUELS:
            raise ValueError(
                f"droit contrefactuel inconnu : {droit!r} ; le moteur connaît "
                + ", ".join(sorted(DROITS_CONTREFACTUELS)))
        racine = self.parametres.racine_donnees
        if droit == "au_31_aout_2023":
            ages = AgesOuvertureAvantReforme2023(racine)
            durees = self.durees_requises_avant_reforme_2023
            self.durees_requises_avant_suspension = durees
        else:
            ages = AgesOuvertureAvantSuspension(racine)
            durees = self.durees_requises_avant_suspension
        self.ages_ouverture = TableRecouverte(ages, self.ages_ouverture)
        self.durees_requises = TableRecouverte(durees, self.durees_requises)
        self.carriere_longue = self.carriere_longue.avant(DROITS_CONTREFACTUELS[droit])

    # -- ce que les étapes lisent sur le moteur ------------------------------
    #
    # Les étapes de ``droit/`` lisent ces constantes sur le moteur qu'on leur
    # passe, et non dans leur module : ce sont des paramètres du droit réel,
    # qu'une variante change pour un seul calcul — la cascade des avantages
    # repousse ainsi la date du salaire annuel moyen des parents.

    #: Pensions à compter desquelles le salaire annuel moyen des parents porte
    #: sur vingt-quatre ou vingt-trois années au lieu de vingt-cinq.
    PARENTS_MEILLEURES_ANNEES_DEPUIS = DateMois(2026, 9)

    #: L'âge avant lequel un droit ouvert fait lire la durée à l'année
    #: d'ouverture plutôt qu'à la génération : « avant l'âge de soixante
    #: ans » (L. 13, III ; article 5, VI, de la loi du 21 août 2003).
    AGE_DUREE_A_L_OUVERTURE = 60.0
    #: Le XXIV, C, de l'article 10 de la loi du 14 avril 2023 ne vise que ceux
    #: qui peuvent liquider à compter de ce mois.
    DUREE_XXIV_C_DEPUIS = DateMois(2023, 9)
    #: Les régimes que L. 13 du code des pensions et le XXIV visent : voir
    #: :data:`~retraite_notionnelle.droit.coordonner.REGIMES_CODE_DES_PENSIONS`.
    REGIMES_CODE_DES_PENSIONS = coordonner.REGIMES_CODE_DES_PENSIONS

    #: Dernière année à compter dans les services : voir
    #: :func:`~retraite_notionnelle.droit.coordonner.borne_carriere`.
    _borne_carriere = staticmethod(coordonner.borne_carriere)

    #: Premier trimestre que la surcote puisse compter : les dispositions de
    #: la loi du 21 août 2003 valent pour les périodes cotisées accomplies à
    #: compter du 1er janvier 2004.
    SURCOTE_DEPUIS = DateMois(2004, 1)
    #: Âge au-delà duquel le barème de 2007-2008 sert 1,25 %.
    SURCOTE_AGE_MAJORE = 65

    # -- calcul --------------------------------------------------------------

    def calculer(self, carriere: Carriere,
                 ignorer_penalite_age: bool = False,
                 avantages_non_contributifs: bool = True,
                 avpf: bool = True,
                 liquider_successions: bool = True,
                 points_gratuits: bool | None = None,
                 nature: str = "definitive") -> ResultatActuel:
        """Pension servie par le système en vigueur, à la date d'effet.

        La liquidation est :func:`~retraite_notionnelle.droit.liquidation.liquider`,
        une fonction pure : elle fait l'acquisition, ouvre le droit, liquide
        chaque régime et complète tous régimes. L'ASPA, qui regarde toutes
        les ressources, vient ensuite, de l'étape « foyer et net »
        (:mod:`~retraite_notionnelle.droit.foyer`). Les drapeaux sont ce
        qu'une couche d'un seul calcul neutralise (docs/architecture.md,
        § 4.8 et 6.4) : le contexte de la liquidation les porte. ``nature``
        est celle de la demande — ``fictive`` pour la valorisation des droits
        acquis.

        ``ignorer_penalite_age`` neutralise la décote et la surcote liées à
        l'âge. On ne l'utilise que pour VALORISER DES DROITS ACQUIS à une date
        donnée — la question n'est alors pas « que toucherait cet assuré s'il
        liquidait aujourd'hui à 40 ans », qui n'a pas de sens, mais « quels
        droits sa carrière lui a-t-elle déjà ouverts ». La proratisation par la
        durée, elle, continue de s'appliquer : une carrière courte ouvre bien
        des droits proportionnellement plus faibles.

        ``avantages_non_contributifs`` commande le minimum contributif, la
        majoration pour trois enfants et la majoration de durée d'assurance.
        Il vaut VRAI par défaut, et il doit le rester : ce scénario décrit le
        droit positif, il sert d'étalon, et un étalon amputé de ses minima
        sous-estime le système actuel là où il protège le plus — petites
        pensions et carrières de mères de famille. Seule la valorisation des
        droits acquis du scénario prospectif le met à faux, parce qu'elle
        mesure du contributif pur.

        Les drapeaux :class:`Neutralisations` ne sont PAS lus ici : ils
        décrivent ce que les scénarios notionnels retirent, pas ce que le droit
        en vigueur accorde.

        ``liquider_successions`` fait liquider ensemble un régime d'annuités et
        celui qui lui succède (voir
        :func:`~retraite_notionnelle.droit.coordonner.groupes_de_succession`). C'est le
        droit, et le défaut ; à FAUX, chaque nom de caisse est liquidé sur ses
        seules années, comme le modèle le faisait, et la variante ne sert qu'à
        mesurer ce que la correction déplace.

        ``points_gratuits`` commande les points que la RCO agricole attribue
        sans cotisation (:func:`~retraite_notionnelle.droit.acquerir.points_gratuits`).
        ``None`` suit
        ``avantages_non_contributifs`` : la valorisation des droits acquis n'en
        veut pas, puisqu'elle mesure du contributif pur. Les recalculs de la
        cascade le fixent, eux, pour que chaque avantage soit retiré seul.

        L'agent parti de la fonction publique sans droit à pension y est
        RÉTABLI au régime général et à l'Ircantec
        (:func:`~retraite_notionnelle.droit.coordonner.retablir`) ; le
        fonctionnaire et le militaire dont les services déclarés passent la
        limite d'âge sont RADIÉS à la limite
        (:func:`~retraite_notionnelle.droit.limite_age.radier`).
        """
        if nature != "fictive":
            carriere = _limite_age.radier(self, carriere)
        if points_gratuits is None:
            points_gratuits = avantages_non_contributifs
        neutralisations = frozenset(nom for nom, neutre in (
            ("avantages_non_contributifs", not avantages_non_contributifs),
            ("avpf", not avpf),
            ("points_gratuits", not points_gratuits),
            ("decote_surcote", ignorer_penalite_age),
            ("successions", not liquider_successions),
        ) if neutre)
        contexte = _liquidation.Contexte(self, neutralisations)
        # LA RETRAITE PROGRESSIVE (:mod:`~retraite_notionnelle.droit.progressive`)
        # se liquide d'abord, à titre provisoire, et laisse aux départs le
        # plancher de la pension complète. La liquidation fictive, qui
        # valorise des droits à une date, ne la voit pas.
        progressive = provisoire = None
        if nature != "fictive":
            progressive = _progressive.examiner(self, carriere)
            if progressive is not None and progressive.ouverte:
                provisoire = _progressive.liquider(self, carriere, contexte, progressive)
                progressive = _progressive.avec_la_duree(progressive, provisoire)
        plancher = ((progressive, provisoire)
                    if progressive is not None and progressive.ouverte else None)
        # CHAQUE RÉGIME LIQUIDE À SA DATE (:mod:`~retraite_notionnelle.droit.departs`),
        # sauf la liquidation fictive, qui valorise des droits à une date. Un
        # seul départ qui n'est pas celui du départ déclaré — toutes les
        # pensions demandées plus tard, ou la seule pension militaire — se
        # liquide à sa date, comme plusieurs.
        departs, demandes = (_departs.departs_et_demandes(self, carriere)
                             if nature != "fictive" else ((), ()))
        if len(departs) > 1 or (departs and not departs[0].unique):
            liquidations = _departs.liquider_les_departs(
                self, carriere, contexte, nature, departs, progressive=plancher)
            resultat = resultat_des_departs(self, carriere, departs, liquidations, contexte)
        else:
            liquidation = _liquidation.liquider(
                _liquidation.demande_de_depart(carriere, nature),
                etat_du_depart(self, carriere, plancher), contexte)
            liquidee = liquidation.carriere
            foyer = _foyer.foyer_et_net(
                self, liquidee.personne, liquidation.demande.date_effet,
                liquidee.annee_liquidation, liquidation.total,
                (liquidee.age_liquidation or 0.0)
                >= _invalidite.age_de_l_aspa(self, liquidee),
                contexte, carriere=liquidee)
            resultat = resultat_actuel(liquidation, foyer)
        if progressive is not None:
            resultat = replace(resultat, retraite_progressive=progressive_servie(
                self, progressive, provisoire, carriere.date_liquidation))
        if demandes:
            resultat = replace(resultat, demandes=demandes)
        return resultat
