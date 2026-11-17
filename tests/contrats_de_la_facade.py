"""Les contrats de la façade des tests : la signature et le type rendu de
chaque entrée qu'elle sert, sans corps (action 161, étape 2 du retrait des
règles Python).

La façade (``facade.py``) lie les arguments d'une règle, d'une méthode de
table ou de constructeur, de la mortalité ou d'une entrée comme le Python les
lie, et relit ce que le portage calcule sous le type que l'entrée annonce.
Elle lisait l'une et l'autre sur le jumeau Python ; elle les lit ici, qui ne
charge aucun fichier de règles. Les types rendus logent sous
``types_du_pont`` ; une carrière se rend sous la carrière nue, que le pont
relit en carrière du moteur Python tant qu'il la bâtit.

Les annotations des arguments ne servent pas : la façade ne lit que leurs
noms, leur genre et leurs valeurs par défaut. Tant que le jumeau vit,
``test_contrats_de_la_facade.py`` confronte chaque contrat au sien.
"""
# ruff: noqa: N801

from __future__ import annotations

from retraite_notionnelle.calendrier import DateMois
from retraite_notionnelle.donnees.chargement import Fiabilite
from retraite_notionnelle.donnees.minimum_vieillesse import DeuxEtages
from retraite_notionnelle.types_du_pont.carriere import Carriere, LigneRelevee
from retraite_notionnelle.types_du_pont.droit import (
    ConversionPoint, DemandeExaminee, Depart, DepartParentTroisEnfants, DerogationActive,
    DureesDesCultes, EligibleMinimum, Foyer, MajorationEnfants, MajorationProportionnelle,
    PensionMajoree, PlancherDeLaSubstitution, PrestationRafp, Progressive, Radiation,
    RevenuDesPoints, TrimestresAccordes)
from retraite_notionnelle.types_du_pont.moteur import CompteNotionnel, CotisationAnnuelle

# -- les règles du droit (pont.REGLES_DE_LA_FACADE) ------------------------------------


class _Regles_acquerir:
    """``droit.acquerir``."""
    @staticmethod
    def points_msa(moteur, periode, annee, revenu) -> float: ...
    @staticmethod
    def points_msa_retenus(points, annee_liquidation) -> float: ...


class _Regles_carriere:
    """``carriere``."""
    @staticmethod
    def prolonger_releve(
            releve,
            fin,
            macro,
            interruptions=None,
            progressive=None,
            temps_partiel=None,
            dispenses=None,
    ) -> list[LigneRelevee]: ...
    @staticmethod
    def salaire_moyen_annuel(macro, annee) -> float: ...


class _Regles_categories:
    """``droit.categories``."""
    @staticmethod
    def age_des_anciens_combattants(moteur, regle, carriere, mois) -> float | None: ...
    @staticmethod
    def age_legal(moteur, carriere) -> float: ...


class _Regles_commun:
    """``droit.commun``."""
    @staticmethod
    def date_d_effet(carriere) -> str | None: ...
    @staticmethod
    def fusionner_les_charges(
            une,
            autre,
    ) -> tuple[tuple[str, tuple[tuple[str, float], ...]], ...]: ...
    @staticmethod
    def ligne_cotisee(moteur, carriere, ligne) -> bool: ...
    @staticmethod
    def majoration_du_conjoint(etapes, quand) -> float: ...
    @staticmethod
    def parts_de_la_majoration(
            avantages,
            quand=None,
            a_charge=True,
    ) -> list[tuple[str, float]]: ...


class _Regles_compter:
    """``droit.compter``."""
    @staticmethod
    def arrondir_les_services(jours, parametres) -> int: ...
    @staticmethod
    def bonification_ouverte(condition, naissance, recrutement, derniere) -> bool: ...
    @staticmethod
    def droit_regime_special(
            moteur,
            periode,
            carriere,
            annee_liquidation,
            condition,
            naissance,
    ) -> tuple[bool, bool, Fiabilite] | None: ...
    @staticmethod
    def majoration_pour_enfants(
            moteur,
            carriere,
            trimestres_par_regime,
            annee_liquidation,
    ) -> MajorationEnfants | None: ...
    @staticmethod
    def services_a_temps_partiel(trimestres, quotite) -> int: ...


class _Regles_cultes:
    """``droit.cultes``."""
    @staticmethod
    def durees(releve_durees, membres, enfants) -> DureesDesCultes: ...
    @staticmethod
    def part_de_l_ecart(naissance) -> float: ...


class _Regles_completer:
    """``droit.completer``."""
    @staticmethod
    def _seuil_a_la_date(seuils, date_effet) -> float | None: ...
    @staticmethod
    def _taux_majoration_enfants(regime, nombre_enfants, periode=None) -> float: ...
    @staticmethod
    def avpf_retenue(moteur, carriere, plafond) -> int: ...
    @staticmethod
    def borne_avec_les_droits_d_avant_1973(
            plancher,
            eligible,
            avant_1973,
            duree_avant_1973,
            cotisee_avant_1973,
            montant_base,
            montant_majore,
            majoration,
            regle,
            avpf,
    ) -> float: ...
    @staticmethod
    def coefficient_du_versement(regle, age) -> tuple[float, int]: ...
    @staticmethod
    def complement_minimum(nue, plancher, coefficient_surcote, date_effet) -> float: ...
    @staticmethod
    def fins_de_charge(carriere, regle, date_effet) -> list[str]: ...
    @staticmethod
    def majoration_ouverte(regle, cotises) -> bool: ...
    @staticmethod
    def majoration_retraite_proportionnelle(
            moteur,
            carriere,
            eligible,
            pension,
            trimestres,
            quand=None,
    ) -> MajorationProportionnelle | None: ...
    @staticmethod
    def majoration_sous_le_traitement(
            montant,
            majoration,
            traitement,
            surcote,
            hors_du_plafond,
    ) -> float: ...
    @staticmethod
    def pension_majoree(
            moteur,
            carriere,
            eligible,
            pension,
            ressources,
            quand=None,
            regle=None,
            taux_plein_requis=True,
            surcote_comprise=False,
    ) -> PensionMajoree | None: ...
    @staticmethod
    def plancher_du_regime(
            eligible,
            montant_base,
            montant_majore,
            majoration,
            tous_regimes,
    ) -> float: ...
    @staticmethod
    def points_rco_de_chef(droits, carriere) -> float: ...
    @staticmethod
    def selon_la_regle(eligible, regle, avpf) -> EligibleMinimum: ...


class _Regles_cumul:
    """``droit.cumul``."""
    @staticmethod
    def assiette_csg(annee) -> float: ...
    @staticmethod
    def jour(date_mois) -> str: ...


class _Regles_departs:
    """``droit.departs``."""
    @staticmethod
    def age_legal(moteur, carriere) -> float: ...
    @staticmethod
    def demandes(moteur, carriere) -> tuple[DemandeExaminee, ...]: ...
    @staticmethod
    def departs(moteur, carriere) -> tuple[Depart, ...]: ...
    @staticmethod
    def departs_et_demandes(
            moteur,
            carriere,
    ) -> tuple[tuple[Depart, ...], tuple[DemandeExaminee, ...]]: ...


class _Regles_foyer:
    """``droit.foyer``."""
    @staticmethod
    def foyer_et_net(
            moteur,
            personne,
            date,
            annee,
            ressources,
            age_atteint,
            contexte=None,
            carriere=None,
    ) -> Foyer: ...


class _Regles_invalidite:
    """``droit.invalidite``."""
    @staticmethod
    def age_de_l_aspa(moteur, carriere) -> float: ...
    @staticmethod
    def categorie_de_la_pension(moteur, carriere) -> tuple[int, str | None]: ...
    @staticmethod
    def plancher_de_la_substitution(
            moteur,
            carriere,
            regimes,
    ) -> PlancherDeLaSubstitution | None: ...
    @staticmethod
    def rente_viagere_d_invalidite(traitement, taux, seuil) -> float: ...


class _Regles_limite_age:
    """``droit.limite_age``."""
    @staticmethod
    def radiation(moteur, carriere) -> Radiation | None: ...
    @staticmethod
    def radier(moteur, carriere) -> Carriere: ...


class _Regles_liquider:
    """``droit.liquider``."""
    @staticmethod
    def _coefficient_anticipation(trimestres_manquants, maximum) -> float | None: ...
    @staticmethod
    def abattement_points(
            moteur,
            periode,
            carriere,
            trimestres,
            requis,
            age_liquidation,
            annee_liquidation,
            trimestres_regime=0,
            handicap=False,
            categorie=None,
            durees=None,
            carriere_longue=False,
            code=None,
    ) -> float: ...
    @staticmethod
    def abattre_au_dela_du_plafond(salaire, plafond, part) -> float: ...
    @staticmethod
    def age_de_la_duree_atteinte(
            moteur,
            periode,
            carriere,
            trimestres,
            requis,
            age_liquidation,
    ) -> float | None: ...
    @staticmethod
    def annees_au_prorata(total, duree, somme) -> int: ...
    @staticmethod
    def assiette_de_reference(moteur, periode, ligne) -> float: ...
    @staticmethod
    def conversion_capital_rafp(age_liquidation, date_effet) -> float: ...
    @staticmethod
    def majoration_rafp(age_liquidation, date_effet) -> float: ...
    @staticmethod
    def mois_apres_le_depart(carriere, age) -> int: ...
    @staticmethod
    def prestation_rafp(
            rente,
            points,
            seuil,
            age,
            date_effet,
            mois_apres_la_base,
    ) -> PrestationRafp: ...
    @staticmethod
    def borne_de_la_duree(moteur, periode, carriere, cible) -> int: ...
    @staticmethod
    def coefficient_surcote_datee(
            moteur,
            periode,
            carriere,
            trimestres,
            requis,
            supplementaires,
            age_ouverture,
    ) -> tuple[float, Fiabilite | None]: ...
    @staticmethod
    def decote_opposable(
            moteur,
            periode,
            carriere,
            annee_liquidation,
    ) -> tuple[float | None, float, Fiabilite | None]: ...
    @staticmethod
    def duree_du_regime_aligne(carriere, durees, membres) -> int: ...
    @staticmethod
    def duree_majoree_apres_taux_plein(
            moteur,
            periode,
            carriere,
            durees,
            membres,
            trimestres_regime,
            proratisation,
            age_annulation,
    ) -> int: ...
    @staticmethod
    def duree_proratisation(moteur, periode, carriere, requis) -> tuple[int, Fiabilite | None]: ...
    @staticmethod
    def majoration_des_points_de_1952_a_1972_d_avant_2026(
            cotisations,
            chef,
            rendement,
            service,
    ) -> tuple[float, float, float]: ...
    @staticmethod
    def majorer_les_points_de_1952_a_1972(
            points,
            chef,
    ) -> tuple[dict[int, float], float, float]: ...
    @staticmethod
    def maximum_des_pensions(
            moteur,
            code,
            date_effet,
            annee,
    ) -> tuple[float, Fiabilite] | None: ...
    @staticmethod
    def moyenne_des_meilleures_annees(valeurs, annees) -> int: ...
    @staticmethod
    def nombre_d_annees_retenues(
            moteur,
            periode,
            carriere,
            generation,
            enfants_majores=0,
    ) -> int: ...
    @staticmethod
    def pension_maximale(moteur, code, carriere) -> tuple[float, Fiabilite] | None: ...
    @staticmethod
    def plafond_du_salaire_de_reference(moteur, periode, annee, mois) -> float | None: ...
    @staticmethod
    def repartir_les_annees(nombre, durees, minimums=None, priorite=()) -> dict[str, int]: ...
    @staticmethod
    def retranche_decote(moteur, periode, carriere) -> int: ...
    @staticmethod
    def revenu_des_cotisations_minimales(annee, revenu, smic, fraction=1.0) -> float: ...
    @staticmethod
    def salaire_de_reference(
            moteur,
            code,
            carriere,
            periode,
            annee_liquidation,
            plafonner,
            generation=None,
            avpf=True,
            membres=None,
            enfants_majores=0,
            depuis=None,
            annees=None,
            plancher=False,
            affilie_avant_2016=False,
    ) -> float: ...
    @staticmethod
    def taux_acquis_l_emporte(
            acquis,
            trimestres,
            taux,
            majores,
            maximum_en_trimestres,
            taux_plein,
            coefficient,
    ) -> bool: ...
    @staticmethod
    def taux_de_majoration_de_1952_a_1972(moyenne) -> float: ...
    @staticmethod
    def trimestres_de_decote(
            moteur,
            periode,
            carriere,
            trimestres,
            requis,
            age_liquidation,
            age_annulation,
    ) -> float: ...
    @staticmethod
    def trimestres_de_surcote_regimes_speciaux(
            carriere,
            trimestres,
            requis,
            age_surcote,
    ) -> int: ...
    @staticmethod
    def valeur_du_point(moteur, code, quand) -> tuple[float, Fiabilite] | None: ...
    @staticmethod
    def valeur_point_fiche(moteur, periode, annee) -> float: ...


class _Regles_ouvrir:
    """``droit.ouvrir``."""
    @staticmethod
    def age_annulation_droit(moteur, carriere) -> float | None: ...
    @staticmethod
    def age_ouverture(
            moteur,
            periode,
            carriere,
            invalidite_comprise=True,
            parents_compris=True,
    ) -> float: ...
    @staticmethod
    def age_ouverture_commun(moteur, periode, carriere) -> float: ...
    @staticmethod
    def age_ouverture_droit(moteur, carriere) -> float | None: ...
    @staticmethod
    def age_surcote(moteur, periode, carriere) -> float: ...
    @staticmethod
    def age_taux_plein(moteur, periode, carriere) -> float: ...
    @staticmethod
    def age_taux_plein_droit(moteur, carriere) -> float | None: ...
    @staticmethod
    def depart_parent_trois_enfants(
            moteur,
            periode,
            carriere,
    ) -> DepartParentTroisEnfants | None: ...
    @staticmethod
    def derogation_active(moteur, periode, carriere) -> DerogationActive | None: ...
    @staticmethod
    def duree_requise(moteur, periode, carriere) -> tuple[int, Fiabilite | None]: ...
    @staticmethod
    def fin_indemnisation(moteur, carriere) -> DateMois | None: ...
    @staticmethod
    def indemnisation_bornee(moteur, carriere) -> Carriere: ...
    @staticmethod
    def mois_ouverture_des_droits(moteur, periode, carriere) -> int: ...
    @staticmethod
    def ouverture_carriere_longue(moteur, periode, carriere) -> float | None: ...


class _Regles_progressive:
    """``droit.progressive``."""
    @staticmethod
    def age_minimum(moteur, carriere, date) -> float | None: ...
    @staticmethod
    def duree_requise(moteur, date) -> int | None: ...
    @staticmethod
    def examiner(moteur, carriere) -> Progressive | None: ...
    @staticmethod
    def fraction(moteur, date, quotite, fonctionnaire) -> float | None: ...
    @staticmethod
    def recalculee(moteur, date) -> bool: ...
    @staticmethod
    def regimes_liquides(moteur, date) -> frozenset[str] | None: ...
    @staticmethod
    def regimes_ouverts(moteur, date) -> frozenset[str]: ...
    @staticmethod
    def regle(moteur, date) -> dict: ...


class _Regles_releve:
    """``droit.releve``."""
    @staticmethod
    def points_de_l_annee(moteur, statut, annee, etage, revenu, trimestres=None) -> float: ...
    @staticmethod
    def revenu_des_points(
            moteur,
            statut,
            annee,
            etage,
            points,
            trimestres=None,
    ) -> RevenuDesPoints | None: ...


class _Regles_reversion:
    """``droit.reversion``."""
    @staticmethod
    def _cumuler(
            parametres,
            montant,
            retraites,
            principale,
            forfaitaire,
            reversions,
    ) -> tuple[float, float]: ...
    @staticmethod
    def mois_de_mariage(debut, fin) -> int: ...


class _Regles_revalorisation:
    """``revalorisation``."""
    @staticmethod
    def majorations_forfaitaires(moteur, pension, depart) -> tuple[tuple[str, float], ...]: ...


class _Regles_compte:
    """``moteur.compte``."""
    @staticmethod
    def taux_du_bareme(bareme, revenu, pass_annuel) -> tuple[float, float]: ...


#: Les règles, par le module de leur jumeau.
REGLES = {"acquerir": _Regles_acquerir, "carriere": _Regles_carriere, "categories": _Regles_categories, "commun": _Regles_commun, "compter": _Regles_compter, "cultes": _Regles_cultes, "completer": _Regles_completer, "cumul": _Regles_cumul, "departs": _Regles_departs, "foyer": _Regles_foyer, "invalidite": _Regles_invalidite, "limite_age": _Regles_limite_age, "liquider": _Regles_liquider, "ouvrir": _Regles_ouvrir, "progressive": _Regles_progressive, "releve": _Regles_releve, "reversion": _Regles_reversion, "revalorisation": _Regles_revalorisation, "compte": _Regles_compte}


# -- les tables du moteur (pont.TABLES_DE_LA_FACADE) ----------------------------------


class _Table_ages_annulation_decote:
    """``AgesAnnulationDecote``."""
    def age(self, generation) -> tuple[float, Fiabilite] | None: ...


class _Table_ages_categorie_active:
    """``AgesCategorieActive``."""
    def derogation(self, classement, generation) -> DerogationActive | None: ...


class _Table_ages_jouissance_militaire:
    """``AgesJouissanceMilitaire``."""
    def age(self, generation) -> tuple[float, Fiabilite] | None: ...


class _Table_ages_ouverture:
    """``AgesOuverture``."""
    def age(self, generation) -> tuple[float, Fiabilite] | None: ...


class _Table_ages_regimes:
    """``AgesRegimes``."""
    def ages(self, table, generation) -> tuple[float | None, float | None, Fiabilite] | None: ...


class _Table_ages_surcote_regimes_speciaux:
    """``AgesSurcoteRegimesSpeciaux``."""
    def age(self, generation) -> tuple[float, Fiabilite] | None: ...


class _Table_calendriers_duree_requise:
    """``CalendriersDureeRequise``."""
    def trimestres(self, calendrier, ouverture) -> tuple[int, Fiabilite] | None: ...


class _Table_decote_regimes_speciaux:
    """``DecoteRegimesSpeciaux``."""
    def parametres(self, annee) -> tuple[int, float, Fiabilite] | None: ...


class _Table_durees_requises_regimes:
    """``DureesRequisesRegimes``."""
    def ligne(
            self,
            table,
            generation,
            ouverture,
            age_liquidation=None,
    ) -> tuple[int, int, Fiabilite] | None: ...


class _Table_durees_services_actifs:
    """``DureesServicesActifs``."""
    def annees_requises(self, categorie, annee_atteinte) -> tuple[float, Fiabilite] | None: ...
    def duree_de_base(self, categorie) -> float | None: ...


class _Table_durees_services_militaires:
    """``DureesServicesMilitaires``."""
    def annees_requises(self, categorie, annee_atteinte) -> tuple[float, Fiabilite] | None: ...
    def duree_de_base(self, categorie) -> float | None: ...


class _Table_grilles:
    """``SalairesForfaitaires``."""
    def forfait(
            self,
            regime,
            annee,
            revenu_annuel,
            indice_salaire,
    ) -> tuple[float, int, Fiabilite] | None: ...


class _Table_annees_salaire_reference:
    """``AnneesSalaireReference``."""
    def annees(self, generation) -> tuple[int, Fiabilite] | None: ...


class _Table_baremes_trimestre:
    """``BaremesTrimestre``."""
    def valeurs(self, nom, date) -> tuple[float, float, Fiabilite] | None: ...


class _Table_affiliations:
    """``Affiliations``."""
    def date_entree(self, carriere, affiliation, annee) -> DateMois | None: ...


class _Table_carriere_longue:
    """``CarriereLongue``."""
    def _portes(
            self,
            carriere,
            fonction_publique=False,
    ) -> list[tuple[int, int, float, int, Fiabilite, int | None]] | None: ...
    def age_de_depart(
            self,
            carriere,
            annee_liquidation,
            trimestres_cotises,
            requis,
            etrangers=None,
            fonction_publique=False,
            trimestres_assurance=None,
            agricoles=None,
    ) -> tuple[float, Fiabilite] | None: ...
    def cotises_reputes(self, carriere, trimestres_cotises, trimestres_enfants) -> int: ...


class _Table_complement_differentiel_rco:
    """``ComplementDifferentielRco``."""
    def regle(self, date_effet) -> dict: ...
    def smic_net(self, annee) -> tuple[float, Fiabilite] | None: ...


class _Table_coefficients_minoration:
    """``CoefficientsMinoration``."""
    def coefficient(self, generation) -> tuple[float, Fiabilite] | None: ...


class _Table_conversions_points:
    """``ConversionsPoints``."""
    def echelle(self, regime, annee_acquisition, annee_liquidation) -> tuple[float, Fiabilite]: ...
    def fusion(self, regime, successeur) -> ConversionPoint | None: ...


class _Table_durees_requises:
    """``DureesRequises``."""
    def trimestres(self, generation) -> tuple[int, Fiabilite] | None: ...


class _Table_fiches_datees:
    """``FichesDatees``."""
    def regle(self, nom, date_effet) -> dict | None: ...
    def version(self, nom, date_effet) -> dict | None: ...


class _Table_invalidites:
    """``Invalidites``."""
    def version(self, fiche, date_effet) -> dict | None: ...


class _Table_majorations_enfants:
    """``MajorationsPourEnfants``."""
    def par_enfant(
            self,
            dispositif,
            sexe,
            naissance,
            date_effet,
            naissances,
    ) -> TrimestresAccordes | None: ...


class _Table_majorations_enfants_points:
    """``MajorationsEnfantsPoints``."""
    def taux(self, regime, annee, nombre_enfants, annee_service=None) -> float | None: ...


class _Table_maximum_des_cultes:
    """``MaximumDesCultes``."""
    def valeur(self, annee) -> tuple[float, Fiabilite] | None: ...


class _Table_minimum_contributif:
    """``MinimumContributif``."""
    def avts(self, annee, mois=1) -> tuple[float, Fiabilite] | None: ...
    def pension_minimum(self, annee, mois=1) -> tuple[float, Fiabilite]: ...
    def regle(self, date_effet) -> dict: ...
    def valeurs(self, annee, mois=1) -> tuple[float, float, float, Fiabilite]: ...


class _Table_minimum_garanti:
    """``MinimumGaranti``."""
    def montant(
            self,
            annee_liquidation,
            trimestres_services,
            duree_maximum=None,
            mois=1,
    ) -> tuple[float, Fiabilite] | None: ...
    def ratio_point_indice(self, depart, arrivee) -> float | None: ...
    def reference(self, annee_liquidation, mois=1) -> tuple[float, Fiabilite] | None: ...


class _Table_minimum_vieillesse:
    """``MinimumVieillesse``."""
    def deux_etages(self, annee) -> DeuxEtages | None: ...
    def plafond(self, annee) -> tuple[float, Fiabilite] | None: ...
    def plafond_couple(self, annee) -> tuple[float, Fiabilite] | None: ...


class _Table_pension_majoree_reference:
    """``PensionMajoreeReference``."""
    def montant(self, mesure, annee, mois=1) -> tuple[float, Fiabilite] | None: ...
    def regle(self, date_effet) -> dict: ...


class _Table_rendements:
    """``Rendements``."""
    def rendement(self, regime, annee) -> tuple[float, Fiabilite]: ...


class _Table_revalorisations_pensions:
    """``RevalorisationsPensions``."""
    def generale(
            self,
            depuis,
            jusqu_a,
            inclure_depuis,
            mensuel_2019,
    ) -> tuple[float, Fiabilite]: ...


class _Table_services_ouvrant_pension:
    """``ServicesOuvrantPension``."""
    def annees(self, regime, radiation, en_fonctions) -> tuple[float, Fiabilite] | None: ...


class _Table_surcote_baremes:
    """``SurcoteBaremes``."""
    def coefficient(self, bareme, trimestres, effet=None) -> tuple[float, Fiabilite | None]: ...
    def connait(self, bareme) -> bool: ...


class _Table_reversions:
    """``Reversions``."""
    def fiche_du_regime(self, regime) -> dict | None: ...
    def limite_cumul(self, annee) -> tuple[float, Fiabilite] | None: ...
    def majoration_enfant(self, annee) -> tuple[float, Fiabilite] | None: ...
    def minimum(self, annee) -> tuple[float, Fiabilite] | None: ...
    def plafond_majoration(self, annee) -> tuple[float, Fiabilite] | None: ...
    def version(self, fiche, date_effet, deces) -> dict | None: ...


class _Table_valeurs_point:
    """``ValeursPoint``."""
    def _en_vigueur(self, regime, mesure, annee) -> tuple[float, Fiabilite] | None: ...
    def achat(self, regime, annee) -> tuple[float, float, Fiabilite] | None: ...
    def achat_prolonge(self, regime, annee, macro) -> tuple[float, float, Fiabilite] | None: ...
    def derniere_annee_servie(self, regime) -> int | None: ...
    def garantie(
            self,
            regime,
            periode,
            annee,
            part,
            quotite,
            taux_contractuel=None,
    ) -> tuple[float, Fiabilite] | None: ...
    def regimes_convenus(self, mesure) -> tuple[str, ...]: ...
    def service(self, regime, annee) -> tuple[float, Fiabilite] | None: ...
    def service_au(self, regime, annee, mois) -> tuple[float, Fiabilite] | None: ...


#: Les tables, par leur nom sur le moteur.
TABLES = {"affiliations": _Table_affiliations, "ages_annulation_decote": _Table_ages_annulation_decote, "ages_categorie_active": _Table_ages_categorie_active, "ages_jouissance_militaire": _Table_ages_jouissance_militaire, "ages_ouverture": _Table_ages_ouverture, "ages_regimes": _Table_ages_regimes, "ages_surcote_regimes_speciaux": _Table_ages_surcote_regimes_speciaux, "calendriers_duree_requise": _Table_calendriers_duree_requise, "decote_regimes_speciaux": _Table_decote_regimes_speciaux, "durees_requises_regimes": _Table_durees_requises_regimes, "durees_services_actifs": _Table_durees_services_actifs, "durees_services_militaires": _Table_durees_services_militaires, "grilles": _Table_grilles, "annees_salaire_reference": _Table_annees_salaire_reference, "baremes_trimestre": _Table_baremes_trimestre, "carriere_longue": _Table_carriere_longue, "complement_differentiel_rco": _Table_complement_differentiel_rco, "coefficients_minoration": _Table_coefficients_minoration, "conversions_points": _Table_conversions_points, "durees_requises": _Table_durees_requises, "fiches_datees": _Table_fiches_datees, "invalidites": _Table_invalidites, "majorations_enfants": _Table_majorations_enfants, "majorations_enfants_points": _Table_majorations_enfants_points, "maximum_des_cultes": _Table_maximum_des_cultes, "minimum_contributif": _Table_minimum_contributif, "minimum_garanti": _Table_minimum_garanti, "minimum_vieillesse": _Table_minimum_vieillesse, "pension_majoree_reference": _Table_pension_majoree_reference, "rendements": _Table_rendements, "revalorisations_pensions": _Table_revalorisations_pensions, "services_ouvrant_pension": _Table_services_ouvrant_pension, "surcote_baremes": _Table_surcote_baremes, "reversions": _Table_reversions, "valeurs_point": _Table_valeurs_point}


# -- les constructeurs du compte (pont.CONSTRUCTEURS_DE_LA_FACADE) -------------------


class _ConstructeurCompte:
    """``moteur.compte.ConstructeurCompte``."""
    def taux_effectif(
            self,
            regime,
            periode,
            annee,
            sans_employeur=False,
            part_salariale_seule=False,
            militaire=False,
    ) -> tuple[float, float, str, Fiabilite]: ...
    def cotisation_annuelle(self, carriere, annee, regime_fusionne=None) -> CotisationAnnuelle: ...
    def construire(
            self,
            carriere,
            annee_liquidation,
            annee_debut=None,
            regime_fusionne=None,
    ) -> CompteNotionnel: ...


class _Convertisseur:
    """``moteur.conversion.Convertisseur``."""
    def population_de(self, carriere) -> str | None: ...


#: Les constructeurs, par leur nom sur le simulateur.
CONSTRUCTEURS = {"constructeur": _ConstructeurCompte, "constructeur_employeur": _ConstructeurCompte, "constructeur_prelevement": _ConstructeurCompte, "convertisseur": _Convertisseur}


# -- la mortalité (pont.MORTALITE_DE_LA_FACADE) ---------------------------------------


class MORTALITE:
    """``donnees.mortalite.DonneesMortalite``."""
    def survie_annuelle(self, age, annee, sexe, facteur=1.0) -> float: ...
    def courbe(
            self,
            age_debut,
            annee_debut,
            sexe,
            generation=True,
            population=None,
    ) -> tuple[float, ...]: ...
    def survie(self, age_debut, annee_debut, duree, sexe, generation=True) -> float: ...
    def esperance_residuelle(
            self,
            age,
            annee,
            sexe=None,
            generation=True,
            population=None,
    ) -> float: ...
    def courbe_survie(
            self,
            age_debut,
            annee_debut,
            sexe,
            generation=True,
            population=None,
    ) -> tuple[float, ...]: ...
    def population_niveau_de_vie_euros(self, montant_mensuel) -> str | None: ...


# -- les entrées ----------------------------------------------------------------------


def _calculer(
        self,
        carriere,
        ignorer_penalite_age=False,
        avantages_non_contributifs=True,
        avpf=True,
        liquider_successions=True,
        points_gratuits=None,
        nature='definitive',
): ...


def _reversion(
        moteur,
        pensions,
        carriere,
        annee,
        deces_suppose=None,
        en_capital=frozenset(),
        majorations=None,
        durees=None,
        minima=None,
        maxima=None,
        avant_le_depart=False,
        majorations_des_pensions=None,
        majorations_sans_anticipation=None,
): ...


def _construire(
        moteur,
        carriere,
        *,
        avantages_non_contributifs=True,
        points_gratuits=True,
        liquider_successions=True,
): ...


def _depuis_profil(
        annee_naissance,
        sexe,
        affiliation,
        age_debut,
        age_liquidation,
        macro,
        mois_naissance=1,
        niveau_salaire=1.0,
        profil_carriere='auto',
        interruptions=None,
        temps_partiel=None,
        nombre_enfants=0,
        part_primes=0.0,
        identifiant='assuré',
        naissances_enfants=(),
        jour_naissance=None,
        conjoint=None,
        deces=None,
        emploi_retraite=None,
        demandes_de_pension=None,
        invalidite=None,
        etranger=None,
        reversion_agricole=None,
): ...


def _depuis_parcours(
        annee_naissance,
        sexe,
        metiers,
        age_liquidation,
        macro,
        mois_naissance=1,
        profil_carriere='auto',
        interruptions=None,
        temps_partiel=None,
        nombre_enfants=0,
        part_primes=0.0,
        identifiant='assuré',
        naissances_enfants=(),
        jour_naissance=None,
        conjoint=None,
        deces=None,
        retraite_progressive=None,
        emploi_retraite=None,
        demandes_de_pension=None,
        invalidite=None,
        etranger=None,
        periodes_assimilees=(),
        dispenses=None,
        reversion_agricole=None,
        prolongations_de_la_charge=(),
        outre_mer=None,
): ...


def _depuis_releve(
        annee_naissance,
        sexe,
        releve,
        age_liquidation,
        macro,
        mois_naissance=1,
        nombre_enfants=0,
        part_primes=0.0,
        identifiant='assuré',
        naissances_enfants=(),
        jour_naissance=None,
        conjoint=None,
        deces=None,
        retraite_progressive=None,
        emploi_retraite=None,
        demandes_de_pension=None,
        invalidite=None,
        etranger=None,
        periodes_assimilees=(),
        reversion_agricole=None,
        prolongations_de_la_charge=(),
): ...


def _depuis_chronologie(chronologie, macro, personne='assure', identifiant='assuré'): ...


#: Les entrées, sous le nom que la façade leur donne.
ENTREES = {"scenario_actuel.calculer": _calculer, "reversion.reversion": _reversion, "releve.construire": _construire, "carriere.depuis_profil": _depuis_profil, "carriere.depuis_parcours": _depuis_parcours, "carriere.depuis_releve": _depuis_releve, "carriere.depuis_chronologie": _depuis_chronologie}


def contrat_de_la_regle(module: str, regle: str):
    """Le contrat de la règle ``regle`` du module ``module``."""
    return getattr(REGLES[module], regle)


def contrat_de_la_table(table: str, methode: str):
    """Le contrat de la méthode ``methode`` de la table ``table``, son
    ``self`` compris."""
    return getattr(TABLES[table], methode)


def contrat_du_constructeur(nom: str, methode: str):
    """Le contrat de la méthode ``methode`` du constructeur ``nom``, son
    ``self`` compris."""
    return getattr(CONSTRUCTEURS[nom], methode)


def contrat_de_la_mortalite(methode: str):
    """Le contrat de la méthode ``methode`` de la mortalité, son ``self``
    compris."""
    return getattr(MORTALITE, methode)


def contrat_de_l_entree(entree: str):
    """Le contrat d'une entrée, sa signature seule — ce qu'elle rend, le pont
    le lit :  ``scenario_actuel.calculer`` (son ``self``
    compris), ``reversion.reversion``, ``releve.construire``, les bâtisseurs
    ``carriere.depuis_*`` (sans leur ``cls``)."""
    return ENTREES[entree]
