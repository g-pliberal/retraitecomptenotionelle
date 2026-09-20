/**
 * Coefficient de conversion du capital notionnel en rente viagère.
 *
 * Portage de ``src/retraite_notionnelle/moteur/conversion.py``. La pension
 * annuelle vaut ``capital_notionnel / diviseur``, où le diviseur est
 * l'espérance de vie résiduelle actualisée :
 *
 *     G(a, L) = Σ_t  t·p_a  (1 + ν)^(−t)
 *
 * lue sur une table de génération. Le taux de préfinancement ν vaut 0 par
 * défaut : la rente est actualisée au taux auquel elle sera revalorisée, les
 * deux se compensent, et le diviseur se réduit à l'espérance de vie résiduelle.
 *
 * Ce que le diviseur sanctionne tout seul : partir cinq ans plus tôt l'augmente
 * de quatre à cinq années, soit une pension inférieure de 15 à 20 % — avant
 * même de compter les cinq années de cotisations manquantes.
 */

import { salaireMoyenAnnuel } from "./carriere.js";
import { POPULATION_PAR_NIVEAU_DE_VIE, TableConversion } from "./config.js";

/**
 * Le niveau de salaire d'une carrière, en multiples du salaire moyen : la
 * somme des revenus cotisés rapportée à la somme des salaires moyens des mêmes
 * années, au prorata de la part d'année couverte. Portage de `niveau_relatif`.
 */
export function niveauRelatif(carriere, macro) {
  let revenus = 0.0;
  let references = 0.0;
  for (const ligne of carriere.lignes) {
    if (!ligne.cotise) {
      continue;
    }
    revenus += ligne.revenu;
    references += salaireMoyenAnnuel(macro, ligne.annee) * ligne.fraction_annee;
  }
  return references > 0.0 ? revenus / references : 1.0;
}

export class Convertisseur {
  constructor(mortalite, parametres, macro = null) {
    this.mortalite = mortalite;
    this.parametres = parametres;
    // Les séries macroéconomiques, pour rattacher une carrière à son vingtile
    // de niveau de vie ; sans elles, le rattachement retombe sur la table commune.
    this.macro = macro;
  }

  /**
   * La population dont la mortalité sert à cette carrière : `null` est la table
   * commune, une clé nommée vaut pour tout le monde, `niveau_de_vie` rattache
   * la carrière au vingtile où son salaire la place.
   */
  populationDe(carriere) {
    const choix = this.parametres.population_conversion ?? null;
    if (choix !== POPULATION_PAR_NIVEAU_DE_VIE) {
      return choix;
    }
    if (carriere === null || carriere === undefined || this.macro === null) {
      return null;
    }
    return this.mortalite.populationNiveauDeVie(niveauRelatif(carriere, this.macro));
  }

  _sexeTable(sexe) {
    if (this.parametres.table_conversion === TableConversion.UNISEXE) {
      return null;
    }
    if (sexe === null || sexe === undefined) {
      throw new Error("table de conversion par sexe demandée mais sexe non renseigné");
    }
    return sexe;
  }

  /**
   * Diviseur annuitaire à une DATE de liquidation.
   *
   * `moisLiquidation` dit où la liquidation tombe dans son année civile, donc
   * sous quel millésime de table le rentier passe chaque tronçon de sa première
   * année de rente. Sans lui, la table sautait d'un millésime au 1er janvier
   * quand l'âge avançait mois par mois, et le diviseur remontait à cette date.
   */
  coefficient(ageLiquidation, anneeLiquidation, sexe = null, moisLiquidation = 1,
    population = null) {
    const sexeTable = this._sexeTable(sexe);
    const generation = this.parametres.table_generation;
    if (population === null || population === undefined) {
      population = this.populationDe(null);
    }
    const dateLiquidation = anneeLiquidation + (moisLiquidation - 1) / 12;
    const courbe = this.mortalite.courbe(
      ageLiquidation, dateLiquidation, sexeTable, generation, population,
    );

    const nu = this.parametres.taux_anticipe_conversion;
    let diviseur = 0.0;
    for (let t = 0; t < courbe.length - 1; t += 1) {
      // Rente supposée servie en continu sur l'année : on prend la survie
      // moyenne de début et de fin de période.
      const survieMoyenne = 0.5 * (courbe[t] + courbe[t + 1]);
      diviseur += survieMoyenne / ((1.0 + nu) ** (t + 0.5));
    }

    if (diviseur <= 0) {
      throw new Error(
        `diviseur nul à ${ageLiquidation} ans en ${anneeLiquidation} : `
        + "âge de liquidation hors des bornes de la table",
      );
    }

    let esperance = 0.0;
    for (let t = 0; t < courbe.length - 1; t += 1) {
      esperance += 0.5 * (courbe[t] + courbe[t + 1]);
    }

    return {
      diviseur,
      age_liquidation: ageLiquidation,
      annee_liquidation: anneeLiquidation,
      esperance_residuelle: esperance,
      table: (sexeTable === null ? "unisexe" : sexeTable)
        + (generation ? "_generation" : "_moment")
        + (population === null ? "" : `_${population}`),
      taux_anticipe: nu,
      fiabilite: this.mortalite.fiabilite(anneeLiquidation),
      /** Fraction du capital notionnel servie chaque année. */
      get taux_de_rente() {
        return this.diviseur ? 1.0 / this.diviseur : 0.0;
      },
    };
  }

  /**
   * Rapport des pensions à capital notionnel donné, anticipé / à l'heure.
   * Isole la seule sanction due à l'allongement de la durée de service.
   */
  effetAnticipation(ageAnticipe, ageReference, anneeLiquidation, sexe = null,
    moisLiquidation = 1, population = null) {
    const anticipe = this.coefficient(
      ageAnticipe, anneeLiquidation, sexe, moisLiquidation, population,
    );
    const reference = this.coefficient(
      ageReference, anneeLiquidation, sexe, moisLiquidation, population,
    );
    return reference.diviseur / anticipe.diviseur;
  }
}
