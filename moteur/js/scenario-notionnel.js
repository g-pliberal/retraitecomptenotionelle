/**
 * Scénarios 2 à 6 — les comptes notionnels.
 *
 * Portage de ``src/retraite_notionnelle/scenarios/notionnel.py``.
 *
 * **Scénario 2, rétroactif.** Le compte est ouvert à l'entrée dans la vie
 * active, ou à l'année d'origine de la répartition si la carrière a commencé
 * avant. Toute la carrière est recalculée sur les seules cotisations versées.
 * Un départ à 55 ans dans un régime spécial en 1985 est traité comme ce qu'il
 * est : douze années de cotisations en moins et douze années de rente en plus.
 *
 * **Scénario 3, prospectif.** Les droits acquis jusqu'à la bascule sont figés
 * selon les règles actuelles, convertis en capital notionnel d'ouverture, puis
 * le compte fonctionne en notionnel au-delà. C'est la variante qui respecte les
 * droits acquis — celle qu'une réforme réelle retiendrait. La conversion inverse
 * la formule de liquidation : K_ouverture = P_acquise × G(a_c, B).
 *
 * Le choix de l'âge a_c est le seul endroit du modèle où le passage aux comptes
 * notionnels peut, à lui seul, retirer quelque chose à des droits déjà ouverts.
 * Voir ``AgeConversionDroitsAcquis``.
 *
 * **Scénario 6, la proposition libérale.** Le scénario 4 jusqu'à la bascule,
 * puis un taux unique de 18 % pour tous — c'est le constructeur qui le porte —,
 * puis une garantie
 * vieillesse par-dessus : différentielle, individualisée, financée par l'impôt,
 * ouverte à 65 ans comme l'ASPA qu'elle remplace. Elle est gardée à part dans
 * ``garantie_vieillesse``, étape par étape.
 */

import { Carriere } from "./carriere.js";
import { AgeConversionDroitsAcquis, SituationFoyer, TableConversion } from "./config.js";
import { MinimumVieillesse } from "./regimes.js";

/** Produit les deux variantes de comptes notionnels. */
export class ScenarioNotionnel {
  constructor(constructeur, convertisseur, ageReference, scenarioActuel, parametres,
              capitalisation = null) {
    this.constructeur = constructeur;
    this.convertisseur = convertisseur;
    this.ageReference = ageReference;
    this.scenarioActuel = scenarioActuel;
    this.parametres = parametres;
    // Le pilier capitalisé n'est construit que pour la proposition : les autres
    // scénarios ne le reçoivent pas, et ne peuvent donc pas le servir par
    // inadvertance.
    this.capitalisation = capitalisation;
  }

  _sexe(carriere) {
    if (this.parametres.table_conversion === TableConversion.UNISEXE) {
      return null;
    }
    return carriere.sexe;
  }

  // -- scénarios 2, 4 et 5 ---------------------------------------------------

  /**
   * Comptes notionnels appliqués depuis l'origine de la répartition.
   *
   * Les scénarios 4 et 5 empruntent ce même chemin : ce qui les distingue du
   * scénario 2 tient entièrement à ce qui alimente le compte, donc aux
   * paramètres du constructeur. Seul le libellé change ici.
   */
  retroactif(carriere, regimeFusionne = null,
             libelle = "Comptes notionnels rétroactifs") {
    const anneeLiquidation = carriere.anneeLiquidation;
    const ageLiquidation = carriere.age_liquidation || 0.0;

    const compte = this.constructeur.construire(
      carriere, anneeLiquidation, carriere.premiereAnnee, regimeFusionne,
    );
    const [conversion] = this.convertisseur.resoudre(
      compte.capital, ageLiquidation, anneeLiquidation, this._sexe(carriere),
      carriere.moisLiquidation, carriere,
    );

    return resultat({
      pension_annuelle: compte.capital / conversion.diviseur,
      capital_notionnel: compte.capital,
      capital_droits_acquis: 0.0,
      compte,
      conversion,
      ecart_age: this.ageReference.ecart(ageLiquidation, anneeLiquidation),
      capital_capitalisation: compte.capital_hors_repartition,
      fiabilite: Math.min(compte.fiabilite, conversion.fiabilite),
      libelle,
    });
  }

  // -- scénario 6 ------------------------------------------------------------

  /**
   * Le scénario 4 jusqu'à la bascule, 18 % ensuite, puis la garantie.
   *
   * Le compte est celui de `retroactif` : ce qui l'alimente — les taux réels
   * jusqu'à la bascule, 18 % pour tous à compter d'elle — tient aux paramètres
   * du constructeur. Ce que cette méthode ajoute, et elle
   * seule, est la garantie : différentielle, individualisée, servie en dernier,
   * et gardée à part pour que l'on sache ce qui vient de l'impôt.
   */
  liberal(carriere, regimeFusionne = null,
          libelle = "Comptes notionnels rétroactifs, taux unique dès la bascule et garantie vieillesse") {
    const resultat_ = this.retroactif(carriere, regimeFusionne, libelle);
    // Le pilier capitalisé D'ABORD : la garantie regarde toutes les
    // ressources de retraite, les 18 % de répartition ET les dix points
    // capitalisés, volontaires compris — une allocation différentielle compte
    // les ressources et non leur origine.
    resultat_.capitalisation = this._pilierCapitalise(carriere, resultat_);
    resultat_.rente_capitalisation_obligatoire = resultat_.capitalisation === null
      ? 0.0 : resultat_.capitalisation.rente_annuelle;
    resultat_.rente_capitalisation_volontaire = resultat_.capitalisation === null
      ? 0.0 : resultat_.capitalisation.rente_volontaire;
    const garantie = this._garantieVieillesse(
      carriere, resultat_.pension_annuelle,
      resultat_.rente_capitalisation_obligatoire,
    );
    // Avant 65 ans, on ne touche pas le minimum vieillesse : le complément est
    // calculé, mais il n'entre dans la pension affichée que s'il est dû dès le
    // départ. `annee_ouverture` dit à partir de quand il l'est.
    if (garantie.servie_a_la_liquidation) {
      resultat_.pension_annuelle += garantie.complement;
    }
    resultat_.pension_mensuelle = resultat_.pension_annuelle / 12.0;
    resultat_.garantie_vieillesse = garantie;
    resultat_.pension_totale = resultat_.pension_annuelle
      + resultat_.rente_capitalisation_obligatoire;
    resultat_.pension_totale_mensuelle = resultat_.pension_totale / 12.0;
    return resultat_;
  }

  /**
   * Le pilier capitalisé, bâti sur les assiettes du compte notionnel.
   *
   * Il n'en construit pas d'autre : la cotisation capitalisée est prélevée sur
   * la MÊME assiette, la même année, que la cotisation notionnelle. Les deux ne
   * peuvent donc pas diverger — ni sur le plafonnement, ni sur les années
   * d'interruption, ni sur l'année du départ, qui n'est pleine pour personne.
   *
   * La garantie vieillesse REGARDE cette rente : le plancher se compare à
   * l'ensemble de la pension obligatoire, répartition et capitalisation. Une
   * allocation différentielle compte les ressources, non leur origine.
   */
  _pilierCapitalise(carriere, resultat_) {
    if (this.capitalisation === null) return null;
    // Le pilier ne prélève que sur ce que l'assuré GAGNE : une année de
    // chômage n'y verse rien, personne ne payant ses dix points.
    const assiettes = new Map(
      resultat_.compte.cotisations
        .filter((c) => {
          const ligne = carriere.ligne(c.annee);
          return ligne !== null && ligne.cotise;
        })
        .map((c) => [c.annee, c.assiette_retenue]),
    );
    return this.capitalisation.construire({
      assiettes,
      anneeNaissance: carriere.annee_naissance,
      ageLiquidation: carriere.age_liquidation || 0.0,
      anneeLiquidation: carriere.anneeLiquidation,
      moisLiquidation: carriere.moisLiquidation,
      sexe: carriere.sexe,
      population: this.convertisseur.populationPourPension(
        resultat_.pension_annuelle, carriere.anneeLiquidation, carriere,
      ),
    });
  }

  /**
   * Ce qui manque à la pension OBLIGATOIRE pour atteindre le plancher.
   *
   * Le plancher d'une personne seule est la garantie de base plus l'allocation
   * d'isolement ; celui d'une personne en couple est la garantie de base seule,
   * et la pension du conjoint ne compte pas — c'est l'individualisation. Les
   * ressources regardées sont les deux étages obligatoires réunis, 18 % de
   * répartition et 5 % capitalisés.
   *
   * L'ÂGE est celui de l'ASPA, 65 ans, et il ne fait plus disparaître le
   * complément : il en retarde le service. Le montant vaut à compter de
   * `annee_ouverture`, et il est calculé POUR cette année-là. Les deux ne
   * coïncident pas, contrairement à ce que ce texte affirmait : le plancher
   * suit les prix comme l'ASPA (article L. 816-2), la pension notionnelle suit
   * la masse salariale, et entre 62 et 65 ans la seconde gagne deux points sur
   * le premier. `revalorisation_differee` porte cet écart.
   */
  _garantieVieillesse(carriere, pensionContributive, renteCapitalisee = 0.0) {
    const parametres = this.parametres;
    const annee = carriere.anneeLiquidation;
    const coefficient = this.constructeur.macro.coefficientPrix(
      parametres.annee_euros_garantie_vieillesse, annee,
    );
    const base = parametres.garantie_vieillesse_mensuelle * 12.0 * coefficient;
    const isolement = parametres.situation_foyer === SituationFoyer.SEUL
      ? parametres.allocation_isolement_mensuelle * 12.0 * coefficient
      : 0.0;
    const plancher = base + isolement;
    const ageAtteint = (carriere.age_liquidation || 0.0) >= MinimumVieillesse.AGE_OUVERTURE;
    const ressources = pensionContributive + renteCapitalisee;
    const ouverture = ageAtteint
      ? annee
      : carriere.annee_naissance + MinimumVieillesse.AGE_OUVERTURE;
    // Ce que la pension gagne en termes réels d'ici l'ouverture : la
    // revalorisation nominale de la règle d'indexation, ramenée aux euros de la
    // liquidation, qui sont ceux du plancher. Vaut un si la règle suit les prix.
    const erosion = ouverture > annee
      ? this.constructeur.macro.coefficientPrix(ouverture, annee)
      : 1.0;
    const revalorisation = ouverture > annee
      ? this.constructeur.indexation.coefficient(annee, ouverture) * erosion
      : 1.0;
    // La rente du pilier, nominale et constante, ne gagne rien : les prix
    // seuls la déprécient d'ici l'ouverture.
    const aLOuverture = pensionContributive * revalorisation
      + renteCapitalisee * erosion;
    const complement = Math.max(0.0, plancher - aLOuverture);
    return {
      situation: parametres.situation_foyer,
      age_atteint: ageAtteint,
      annee_ouverture: ouverture,
      coefficient_prix: coefficient,
      base_annuelle: base,
      isolement_annuel: isolement,
      plancher_annuel: plancher,
      pension_contributive: pensionContributive,
      rente_capitalisee: renteCapitalisee,
      ressources,
      revalorisation_differee: revalorisation,
      ressources_a_l_ouverture: aLOuverture,
      erosion_rente: erosion,
      complement,
      servie: complement > 0,
      servie_a_la_liquidation: ageAtteint && complement > 0,
      differee: complement > 0 && !ageAtteint,
    };
  }

  // -- scénario 3 ------------------------------------------------------------

  /**
   * Droits figés à la bascule, comptes notionnels au-delà.
   *
   * Pour un assuré dont la retraite est déjà liquidée à la bascule, ce scénario
   * ne peut rien changer : ses droits sont intégralement acquis. On renvoie
   * alors sa pension actuelle, de sorte que le tableau comparatif reste lisible.
   */
  prospectif(carriere, regimeFusionne,
             libelle = "Comptes notionnels à compter de la bascule") {
    const anneeLiquidation = carriere.anneeLiquidation;
    const ageLiquidation = carriere.age_liquidation || 0.0;
    const bascule = this.parametres.annee_bascule;

    if (anneeLiquidation <= bascule) {
      return this._dejaLiquide(carriere);
    }

    const droitsAcquis = this._droitsAcquis(carriere, bascule);
    const capitalAcquis = droitsAcquis === null ? 0.0 : droitsAcquis.capital;

    const compte = this.constructeur.construire(
      carriere, anneeLiquidation, bascule, regimeFusionne,
    );
    const capitalTotal = compte.capital + capitalAcquis;
    const [conversion] = this.convertisseur.resoudre(
      capitalTotal, ageLiquidation, anneeLiquidation, this._sexe(carriere),
      carriere.moisLiquidation, carriere,
    );

    return resultat({
      pension_annuelle: capitalTotal / conversion.diviseur,
      capital_notionnel: capitalTotal,
      capital_droits_acquis: capitalAcquis,
      compte,
      conversion,
      ecart_age: this.ageReference.ecart(ageLiquidation, anneeLiquidation),
      capital_capitalisation: compte.capital_hors_repartition,
      fiabilite: Math.min(compte.fiabilite, conversion.fiabilite),
      libelle,
      droits_acquis: droitsAcquis,
    });
  }

  /** Cas d'un assuré déjà retraité à la bascule : rien ne change. */
  _dejaLiquide(carriere) {
    const anneeLiquidation = carriere.anneeLiquidation;
    const ageLiquidation = carriere.age_liquidation || 0.0;
    const actuel = this.scenarioActuel.calculer(carriere);
    const conversion = this.convertisseur.coefficient(
      ageLiquidation, anneeLiquidation, this._sexe(carriere),
      carriere.moisLiquidation,
      this.convertisseur.populationPourPension(
        actuel.pension_annuelle, anneeLiquidation, carriere,
      ),
    );
    const compte = this.constructeur.construire(
      carriere, anneeLiquidation, anneeLiquidation, // aucune cotisation postérieure
    );
    return resultat({
      pension_annuelle: actuel.pension_annuelle,
      capital_notionnel: actuel.pension_annuelle * conversion.diviseur,
      capital_droits_acquis: actuel.pension_annuelle * conversion.diviseur,
      compte,
      conversion,
      ecart_age: this.ageReference.ecart(ageLiquidation, anneeLiquidation),
      capital_capitalisation: 0.0,
      fiabilite: actuel.fiabilite,
      libelle: "Retraite déjà liquidée à la bascule — droits inchangés",
    });
  }

  /**
   * Convertit les droits figés à la bascule en capital notionnel.
   *
   * Les droits sont ceux qu'aurait produits la carrière si elle s'était
   * arrêtée à la bascule, calculés selon les règles actuelles mais DÉBARRASSÉS
   * des avantages non contributifs. La valorisation se fait à l'année de
   * bascule, sans décote ni surcote : on mesure des droits déjà ouverts, pas
   * une liquidation anticipée.
   *
   * Reste l'âge auquel prendre le diviseur, et c'est le paramètre
   * ``age_conversion_droits_acquis`` qui tranche : l'âge de référence fait
   * payer l'anticipation une seconde fois, sur des droits pourtant déjà
   * ouverts ; l'âge effectif de liquidation rend la conversion neutre. Dans les
   * deux cas, l'écart de longévité entre la bascule et la liquidation subsiste.
   *
   * Renvoie les étapes de la cascade, ou ``null`` si rien n'a été acquis.
   */
  _droitsAcquis(carriere, bascule) {
    const lignesAvant = carriere.lignes.filter((ligne) => ligne.annee < bascule);
    if (lignesAvant.length === 0) {
      return null;
    }

    const carriereTronquee = new Carriere({
      annee_naissance: carriere.annee_naissance,
      sexe: carriere.sexe,
      lignes: lignesAvant,
      // L'année de liquidation de cette carrière fictive doit être l'année de
      // bascule : c'est en euros de cette année-là que les droits sont valorisés.
      age_liquidation: bascule - carriere.annee_naissance,
      nombre_enfants: 0, // avantages familiaux neutralisés
      identifiant: `${carriere.identifiant} (droits figés ${bascule})`,
    });
    // Une liquidation FICTIVE (docs/architecture.md, § 7.3) : calculée sans
    // être servie, au contributif seul, décote et surcote neutralisées.
    const droits = this.scenarioActuel.calculer(
      carriereTronquee, true, false, true, true, null, "fictive");

    const ageConversion = this.parametres.age_conversion_droits_acquis
        === AgeConversionDroitsAcquis.REFERENCE
      ? this.ageReference.age(bascule)
      : (carriere.age_liquidation || this.ageReference.age(bascule));
    const conversion = this.convertisseur.coefficient(
      ageConversion, bascule, this._sexe(carriere), 1,
      this.convertisseur.populationPourPension(droits.pension_annuelle, bascule, carriere),
    );
    const capitalALaBascule = droits.pension_annuelle * conversion.diviseur;

    // Le capital d'ouverture se revalorise ensuite comme tout compte notionnel.
    const coefficient = this.constructeur.indexation.coefficient(
      bascule, carriere.anneeLiquidation,
    );
    return {
      pension_figee: droits.pension_annuelle,
      age_conversion: ageConversion,
      diviseur: conversion.diviseur,
      capital_a_la_bascule: capitalALaBascule,
      coefficient_revalorisation: coefficient,
      capital: capitalALaBascule * coefficient,
    };
  }
}

/** Pension issue d'un compte notionnel, et tout ce qui l'explique. */
function resultat(champs) {
  return {
    // Le détail de la conversion des droits figés n'existe qu'en prospectif ;
    // ailleurs il vaut null, comme du côté Python. La garantie vieillesse et le
    // pilier capitalisé, de même, n'existent que dans le scénario 6.
    droits_acquis: null,
    garantie_vieillesse: null,
    //: `pension_annuelle` ne comprend PAS la rente du pilier capitalisé : elle
    //: n'est pas une pension de répartition, elle ne se revalorise pas comme
    //: elle, et elle se transmet là où l'autre ne se transmet pas. Le total est
    //: à `pension_totale`, toujours affiché comme une somme de deux lignes.
    capitalisation: null,
    rente_capitalisation_obligatoire: 0.0,
    //: La part de cette rente qui vient des cinq points VOLONTAIRES, ceux que
    //: la proposition rend et que le modèle suppose remis au compte.
    rente_capitalisation_volontaire: 0.0,
    ...champs,
    pension_mensuelle: champs.pension_annuelle / 12.0,
    pension_totale: champs.pension_annuelle,
    pension_totale_mensuelle: champs.pension_annuelle / 12.0,
    /**
     * Ce que vaudrait le compartiment de capitalisation, POUR MÉMOIRE. Le RAFP
     * et les droits des anciennes assurances sociales ne sont pas convertis en
     * capital notionnel : ils restent dans un compartiment distinct, et cette
     * valeur dit ce qu'il donnerait s'il l'était.
     *
     * Ce n'est PAS ce qui est servi. Un régime provisionné n'est pas atteint
     * par une réforme de la répartition : les six scénarios servent sa rente à
     * son propre barème, celui du scénario 1 (`pension_hors_repartition`), et
     * c'est cette valeur-là qui est affichée.
     */
    rente_capitalisation_annuelle: champs.conversion.diviseur <= 0
      ? 0.0
      : champs.capital_capitalisation / champs.conversion.diviseur,
  };
}
