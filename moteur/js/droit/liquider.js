/**
 * Liquider chaque régime (docs/architecture.md, § 7.3).
 *
 * Jumeau de `src/retraite_notionnelle/droit/liquider.py`, fonction pour
 * fonction : chaque régime liquide sa pension sous ses propres règles, sur ce
 * que le relevé lui a acquis. En annuités, un salaire de référence
 * (`salaireDeReference`) ou un forfait, un taux — décote et surcote faites
 * (`decoteOpposable`, `trimestresDeDecote`, `coefficientSurcoteDatee`) — et
 * une durée proratisée (`dureeProratisation`) ; en points, les points à la
 * valeur de service (`valeurDuPoint`), l'abattement et la majoration
 * (`abattementPoints`, `surcotePoints`), le capital du RAFP sous son seuil.
 * Ce que l'étape écrit, `Pensions`, suit son schéma,
 * `data/reference/etapes/liquider_chaque_regime.yaml`.
 */

import { DateMois, enMois } from "../calendrier.js";
import { salaireMoyenAnnuel } from "../carriere.js";
import { formatFixe, formatPourcentage } from "../format.js";
import { FIN_PEREQUATION, coefficientTraitementDiffere, dateIso } from "../revalorisation.js";
import { Fiabilite, nomFiabilite } from "../serie.js";
import * as acquerir from "./acquerir.js";
import { derniereAnnee } from "./commun.js";
import * as coordonner from "./coordonner.js";
import { REGIMES_CODE_DES_PENSIONS } from "./coordonner.js";
import * as ouvrir from "./ouvrir.js";
import { TRIMESTRES_DECOTE_MILITAIRE } from "./ouvrir.js";

/** La version du schéma de l'étape. */
export const SCHEMA_VERSION = 1;

/** Premier trimestre que la surcote puisse compter (loi du 21 août 2003). */
const SURCOTE_DEPUIS = new DateMois(2004, 1);

/** Âge au-delà duquel le barème de 2007-2008 sert 1,25 %. */
const SURCOTE_AGE_MAJORE = 65;

/**
 * Barèmes de décote lus dans une table, et non dans la fiche du régime : le
 * coefficient et l'âge d'annulation y montent en charge à l'année de
 * liquidation. `regimes_speciaux_age_fixe` prend le coefficient de la table des
 * régimes spéciaux mais garde l'âge d'annulation écrit dans la fiche.
 */
const BAREMES_DECOTE_EN_TABLE = new Set([
  "fonction_publique", "regimes_speciaux", "regimes_speciaux_age_fixe",
]);

/**
 * Trimestres dont l'âge d'annulation de la décote est minoré pour ouvrir le
 * minimum garanti sans la durée, selon l'année où l'âge d'ouverture est
 * atteint : article 3 du décret n° 2010-1744 du 30 décembre 2010. Aucun à
 * partir de 2016.
 */
const MINORATION_AGE_MINIMUM_GARANTI = { 2011: 9, 2012: 7, 2013: 5, 2014: 3, 2015: 1 };

/** Ce que l'étape « liquider chaque régime » écrit. */
export class Pensions {
  constructor({ personne, regimes, minimum, garanti, requis, taux, fiabilite }) {
    this.personne = personne;
    this.regimes = regimes;
    this.minimum = minimum;
    this.garanti = garanti;
    this.requis = requis;
    this.taux = taux;
    this.fiabilite = fiabilite;
  }

  /** Les pensions, telles que le schéma de l'étape les décrit. */
  donnees() {
    const regimes = this.regimes.map((p) => ({
      regime: p.regime, montant: p.montant, calcul: p.type_calcul, detail: p.detail,
      fiabilite: nomFiabilite(p.fiabilite),
    }));
    for (const eligible of this.minimum) {
      regimes[eligible.indice].minimum = {
        prorata_assurance: eligible.prorataAssurance,
        prorata_cotise: eligible.prorataCotise,
        taux_plein: eligible.tauxPlein,
        surcote: eligible.surcote,
      };
    }
    for (const eligible of this.garanti) {
      regimes[eligible.indice].garanti = {
        trimestres_services: eligible.trimestresServices,
        ouvert: eligible.ouvert,
        duree_maximum: eligible.dureeMaximum,
      };
    }
    return {
      schema_version: SCHEMA_VERSION, personne: this.personne, regimes,
      requis: this.requis, taux: this.taux, fiabilite: nomFiabilite(this.fiabilite),
    };
  }
}

/**
 * La pension de chaque régime où le relevé porte un droit. Le contexte dit ce
 * que le calcul neutralise : la décote et la surcote pour valoriser des droits
 * acquis, l'AVPF pour en mesurer l'apport. Voir le Python.
 */
export function liquiderChaqueRegime(moteur, releve, ouverture, contexte = null) {
  const carriere = releve.carriere;
  const { durees, droits } = releve;
  const anneeLiquidation = carriere.anneeLiquidation;
  const ageLiquidation = carriere.age_liquidation || 0.0;
  const trimestres = durees.trimestres;
  const requisReference = ouverture.requis;
  const ignorerPenaliteAge = contexte !== null && contexte.neutralise("decote_surcote");
  const avpf = contexte === null || !contexte.neutralise("avpf");
  const codes = droits.codes;
  const groupes = releve.groupes;

  const pensions = [];
  let fiabiliteGlobale = Fiabilite.CERTIFIEE;
  let trimestresRequis = 0;
  let tauxRetenu = 0.0;
  // Régimes de base qui portent le minimum contributif : indice dans
  // `pensions`, prorata de durée d'assurance, prorata de durée COTISÉE,
  // condition de taux plein, et coefficient de surcote déjà incorporé.
  const eligiblesMinimum = [];
  // Régimes de la fonction publique qui portent le minimum garanti.
  const eligiblesGaranti = [];

  // Ce que les étapes de l'acquisition ont écrit, sous les noms que la
  // liquidation lit.
  const cumulCotisations = droits.cumulCotisations;
  const pointsAcquis = droits.pointsAcquis;
  const fiabilitePoints = droits.fiabilitePoints;
  const gratuitsAttribues = droits.gratuits;
  const trimestresParRegime = durees.trimestresParRegime;
  const bonificationsParRegime = durees.bonificationsParRegime;
  const cumulPlafonne = (table, membres) => durees.cumulPlafonne(table, membres);
  const majorationEnfants = durees.enfants;

  for (const code of codes) {
    const cumul = cumulCotisations.get(code) ?? 0.0;
    const regime = moteur.catalogue.obtenir(code);
    const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
    if (periode === null) {
      continue;
    }
    fiabiliteGlobale = Math.min(fiabiliteGlobale, regime.fiabilite);
    const membres = groupes.get(code) ?? [code];
    if (membres[0] !== code) {
      // Liquidé par le régime qui lui a succédé.
      continue;
    }

    if (periode.type_calcul === "points" || periode.type_calcul === "mixte") {
      let montant = 0.0;
      let fiabiliteRegime = regime.fiabilite;
      const details = [];

      const points = pointsAcquis.get(code) ?? 0.0;
      // BARÈME DU TRIMESTRE : la pension minière est la durée, majorée du
      // coefficient de l'article 131-1, multipliée par la valeur du trimestre
      // de la date d'effet. Voir le Python.
      const trimestre = (points && periode.bareme_trimestre)
        ? moteur.baremesTrimestre.valeurs(periode.bareme_trimestre, carriere.dateLiquidation)
        : null;
      if (trimestre !== null) {
        const [valeurTrimestre, coefficientDuree, fiabiliteTrimestre] = trimestre;
        montant += points * coefficientDuree * valeurTrimestre;
        fiabiliteRegime = Math.min(
          fiabiliteRegime, fiabiliteTrimestre, fiabilitePoints.get(code),
        );
        details.push(
          `${formatFixe(points, 2, true)} trimestres × coefficient de majoration de `
          + `la durée ${formatFixe(coefficientDuree, 3)} × valeur du trimestre `
          + `${sansZerosInutiles(valeurTrimestre, 2)} €`,
        );
      } else if (points) {
        let valeur = valeurDuPoint(moteur, periode.points_de ?? code, anneeLiquidation);
        if (valeur === null && periode.valeur_point_euros !== null
            && periode.valeur_point_euros !== undefined) {
          // Valeur de service écrite dans la fiche, faute d'une série
          // certifiable dans `valeurs_point.csv`.
          valeur = [
            valeurPointFiche(moteur, periode, anneeLiquidation), Fiabilite.MOYENNE,
          ];
        }
        if (valeur !== null) {
          const [service, fiabiliteService] = valeur;
          // COEFFICIENT DE DURÉE de la proportionnelle agricole : la pension
          // vaut « points × valeur du point × 37,5 / durée requise ».
          let coefficientDuree = 1.0;
          if (periode.bareme_points === "msa_proportionnelle") {
            const [requisMsa, fiabiliteDureeMsa] = ouvrir.dureeRequise(moteur, periode, carriere);
            if (fiabiliteDureeMsa !== null) {
              fiabiliteRegime = Math.min(fiabiliteRegime, fiabiliteDureeMsa);
            }
            if (requisMsa > 0) {
              coefficientDuree = 37.5 / (requisMsa / 4.0);
            }
          }
          montant += points * service * coefficientDuree;
          fiabiliteRegime = Math.min(
            fiabiliteRegime, fiabiliteService, fiabilitePoints.get(code),
          );
          const gratuits = (gratuitsAttribues.get(code) ?? [0.0, 0])[0];
          details.push(
            `${formatFixe(points, 2, true)} points × valeur de service `
            + `${sansZerosInutiles(service, 6)} €`
            + (coefficientDuree === 1.0 ? "" : ` × ${formatFixe(coefficientDuree, 4)}`)
            // Les points gratuits sont DANS le compte : la formule se refait
            // sur le total, et le lecteur voit ce qu'il n'a pas cotisé.
            + (!gratuits ? "" : ` (dont ${formatFixe(gratuits, 2, true)} points gratuits)`),
          );
        }
      }

      // RÉGIME MIXTE : une part forfaitaire s'ajoute aux points — la retraite
      // forfaitaire agricole, qui vaut l'AVTS pour une carrière complète et
      // se proratise sur la durée (L. 732-24).
      if (periode.type_calcul === "mixte"
          && periode.pension_forfaitaire_annuelle !== null
          && periode.pension_forfaitaire_annuelle !== undefined) {
        const requisForfait = ouvrir.dureeRequise(moteur, periode, carriere)[0];
        const [proratisationForfait, fiabiliteProrataForfait] = dureeProratisation(
          moteur, periode, carriere, requisForfait);
        if (fiabiliteProrataForfait !== null) {
          fiabiliteRegime = Math.min(fiabiliteRegime, fiabiliteProrataForfait);
        }
        const acquis = Math.min(
          trimestresParRegime.get(code) ?? 0, proratisationForfait,
        );
        if (proratisationForfait > 0 && acquis > 0) {
          const forfait = periode.pension_forfaitaire_annuelle
            * moteur.macro.coefficientPrix(
              periode.pension_forfaitaire_annee ?? anneeLiquidation, anneeLiquidation,
            )
            * acquis / proratisationForfait;
          montant += forfait;
          details.push(
            `forfait ${formatFixe(forfait, 2, true)} € `
            + `(${acquis}/${proratisationForfait})`,
          );
        }
      }

      // Années sans prix d'achat connu : le rendement instantané prend le
      // relais, régime par régime et année par année. Une fiche qui emprunte
      // le barème du point d'un autre régime (`points_de`) en emprunte aussi
      // le rendement.
      if (cumul) {
        const [rendement, fiabiliteRendement] = moteur.rendements.rendement(
          periode.points_de ?? code, Math.min(anneeLiquidation, derniereAnnee(regime)),
        );
        montant += cumul * rendement;
        fiabiliteRegime = Math.min(fiabiliteRegime, fiabiliteRendement);
        details.push(
          `cotisations revalorisées ${formatFixe(cumul, 0, true)} € `
          + `× rendement ${formatPourcentage(rendement, 2)}`,
        );
      }

      fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteRegime);
      const montantBrut = montant;
      let abattement = 1.0;
      if (!ignorerPenaliteAge) {
        abattement = abattementPoints(
          moteur, periode, carriere, trimestres, requisReference, ageLiquidation,
          anneeLiquidation, trimestresParRegime.get(code) ?? 0,
        );
        montant *= abattement;
      }
      let detail = formulePoints(details, abattement);
      // Les années qu'aucun prix d'achat ne couvre encore passent par le
      // rendement : le seuil se compare aux points que vaut TOUT le montant.
      let pointsTotaux = points;
      const seuilCapital = periode.capital_seuil_points;
      if (seuilCapital !== null && seuilCapital !== undefined) {
        const valeurSeuil = valeurDuPoint(moteur, periode.points_de ?? code, anneeLiquidation);
        if (valeurSeuil !== null && valeurSeuil[0] > 0) {
          pointsTotaux = montantBrut / valeurSeuil[0];
        }
      }
      if (seuilCapital !== null && seuilCapital !== undefined
          && pointsTotaux > 0 && pointsTotaux < seuilCapital) {
        // SOUS LE SEUIL, UN CAPITAL (décret n° 2004-569, art. 9). Le
        // montant annuel reste celui de la rente dont le capital est
        // l'équivalent actuariel.
        const capital = montant * conversionCapitalRafp(ageLiquidation);
        detail += ` ; versé en capital, ${formatFixe(capital, 0, true)} € en une fois `
          + `(moins de ${formatFixe(periode.capital_seuil_points, 0, true)} points)`;
      }
      pensions.push({
        regime: code,
        montant,
        type_calcul: periode.type_calcul,
        detail,
        fiabilite: fiabiliteRegime,
      });
      continue;
    }

    // Régimes en annuités.
    // Régimes en annuités — et régimes FORFAITAIRES, dont la pension ne dépend
    // pas du revenu mais de la seule durée. Le second cas se traite comme le
    // premier en remplaçant le salaire de référence par le montant
    // forfaitaire. Faute de ce montant, la fiche retombait sur la moyenne des
    // revenus, c'est-à-dire sur un taux de remplacement de 100 %.
    const plafonner = ["plafonnee", "tranche_1", "tranche_a"].includes(periode.assiette);
    const indicePension = pensions.length;
    const forfaitaire = periode.pension_forfaitaire_annuelle !== null
      && periode.pension_forfaitaire_annuelle !== undefined;
    const salaireReference = forfaitaire
      ? periode.pension_forfaitaire_annuelle * moteur.macro.coefficientPrix(
        periode.pension_forfaitaire_annee ?? anneeLiquidation, anneeLiquidation,
      )
      : salaireDeReference(
        moteur, code, carriere, periode, anneeLiquidation, plafonner,
        carriere.annee_naissance, avpf, membres,
        majorationEnfants !== null ? carriere.nombre_enfants : 0,
      );
    const [requis, fiabiliteDuree] = ouvrir.dureeRequise(moteur, periode, carriere);
    if (fiabiliteDuree !== null) {
      fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteDuree);
    }
    trimestresRequis = Math.max(trimestresRequis, requis);
    // Le dénominateur de la PRORATISATION n'est pas la durée requise :
    // l'article R. 351-6 en fixe une autre, plus courte pour les générations
    // d'avant 1949. Confondre les deux retirait à un assuré né en 1945 avec
    // 156 trimestres les 2,5 % que 156/160 lui coûte, là où 156/154 lui donne
    // le coefficient plein.
    const [proratisation, fiabiliteProratisation] = dureeProratisation(
      moteur, periode, carriere, requis,
    );
    if (fiabiliteProratisation !== null) {
      fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteProratisation);
    }
    // Le numérateur n'est pas le même selon le régime : services et
    // bonifications dans la fonction publique (L. 13), durée d'assurance
    // partout ailleurs (R. 351-1). Les membres d'un groupe liquidé ensemble
    // se somment ANNÉE PAR ANNÉE : deux activités cumulées dans deux régimes
    // alignés ne valident pas huit trimestres la même année.
    const acquisParRegime = (
      moteur.catalogue.obtenir(code).famille === "fonction_publique"
        ? "services" : "assurance"
    );
    // Le plafond est la durée requise, que les BONIFICATIONS seules peuvent
    // dépasser, dans la limite d'un taux : « Le pourcentage maximum fixé à
    // l'article L 13 peut-être augmenté de cinq points du chef des
    // bonifications » (L. 12 CPCMR).
    const bonifications = (periode.taux_maximum_bonifie && periode.taux_plein)
      ? membres.reduce((somme, m) => somme + (bonificationsParRegime.get(m) ?? 0), 0)
      : 0;
    let trimestresRegime = Math.min(
      cumulPlafonne(acquisParRegime, membres), proratisation + bonifications,
    );
    // Rapport des trimestres liquidables à la durée requise, borné au taux
    // maximum — 80/75 avec des bonifications, un sans elles.
    const rapportMaximum = bonifications
      ? periode.taux_maximum_bonifie / periode.taux_plein : 1.0;
    if (periode.duree_maximum_avant_age !== null
        && periode.duree_maximum_avant_age !== undefined
        && periode.duree_maximum_avant_age_trimestres !== null
        && periode.duree_maximum_avant_age_trimestres !== undefined
        && ageLiquidation < periode.duree_maximum_avant_age) {
      // DURÉE LIQUIDABLE PLAFONNÉE PAR L'ÂGE. L'article R. 13 du code des
      // pensions de retraite des marins : « le maximum des annuités
      // liquidables dans les pensions d'ancienneté dont la liquidation est
      // demandée avant cinquante-cinq ans est fixé à vingt-cinq annuités ».
      // Levé « au profit d'un marin âgé d'au moins cinquante-deux ans et
      // demi, réunissant trente-sept annuités et demie de services » : le
      // même alinéa, b).
      const levee = periode.duree_maximum_levee_age != null
        && periode.duree_maximum_levee_trimestres != null
        && ageLiquidation >= periode.duree_maximum_levee_age
        && trimestresRegime >= periode.duree_maximum_levee_trimestres;
      if (!levee) {
        trimestresRegime = Math.min(
          trimestresRegime, periode.duree_maximum_avant_age_trimestres,
        );
      }
    }

    let taux = periode.taux_plein || 0.5;
    // Part du taux qui vient de la surcote : le minimum contributif se
    // compare à la pension AVANT surcote, il faut donc pouvoir la retirer.
    let coefficientSurcote = 1.0;
    // Trimestres de décote effectivement retenus : la condition d'ouverture
    // du minimum garanti en dépend.
    let trimestresDecote = 0.0;
    // Âge d'annulation de la décote, que l'ouverture transitoire du minimum
    // garanti minore.
    let ageAnnulation = null;
    if (!ignorerPenaliteAge) {
      const [decote, ageAnnulationPeriode, fiabiliteDecote] = decoteOpposable(
        moteur, periode, carriere, anneeLiquidation,
      );
      ageAnnulation = ageAnnulationPeriode;
      trimestresDecote = trimestresDeDecote(
        moteur, periode, carriere, trimestres, requis, ageLiquidation, ageAnnulation,
      );
      if (decote && trimestresDecote > 0) {
        // Les régimes sans décote (fonction publique avant 2004, régimes
        // spéciaux avant 2008) ne subissent que la proratisation.
        if (fiabiliteDecote !== null) {
          fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteDecote);
        }
        taux *= Math.max(0.0, 1.0 - decote * trimestresDecote);
      }
      // La surcote ne récompense que les trimestres COTISÉS APRÈS l'âge
      // légal ET au-delà de la durée requise.
      // Elle se compte depuis l'âge légal de droit commun — pour l'emploi
      // classé, depuis l'âge anticipé ou minoré majoré de cinq ou dix ans
      // (XXIV, D, de la loi du 14 avril 2023) —, et le militaire n'en a
      // aucune : le III de l'article L. 14 ne la donne qu'au « fonctionnaire
      // civil ».
      let supplementaires = Math.max(0, trimestres - requis);
      const ageOuverture = ouvrir.ageSurcote(moteur, periode, carriere);
      if (periode.surcote_par_trimestre && supplementaires > 0
          && ageLiquidation >= ageOuverture
          && ouvrir.droitMilitaire(moteur, periode, carriere) === null) {
        if (periode.surcote_bareme) {
          // Barème DATÉ : chaque trimestre civil de surcote au taux en
          // vigueur quand il a été accompli, depuis le trimestre qui suit
          // l'âge légal (D. 351-1-4).
          const [coefficient, fiabiliteSurcote] = coefficientSurcoteDatee(
            moteur, periode, carriere, trimestres, requis, supplementaires, ageOuverture,
          );
          coefficientSurcote = coefficient;
          if (fiabiliteSurcote !== null) {
            fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteSurcote);
          }
        } else {
          supplementaires = Math.min(
            supplementaires,
            trimestresCotisesApres(carriere, ageOuverture, anneeLiquidation),
          );
          if (supplementaires > 0) {
            coefficientSurcote = 1.0 + periode.surcote_par_trimestre * supplementaires;
          }
        }
        taux *= coefficientSurcote;
      }
    }

    tauxRetenu = Math.max(tauxRetenu, taux);
    const prorata = Math.min(trimestresRegime / proratisation, rapportMaximum);
    if (periode.avantages_non_contributifs.includes("minimum_contributif")) {
      // Le minimum ne relève que les régimes de base qui le portent, au
      // prorata de la durée acquise DANS CE régime — durée d'assurance pour
      // le montant de base, durée COTISÉE pour la majoration —, et seulement
      // si la pension est liquidée AU TAUX PLEIN (L. 351-10).
      // Le minimum se proratise « dans les mêmes conditions que la pension » :
      // c'est donc la durée de proratisation qui fait office ici aussi.
      const cotisesRegime = Math.min(
        cumulPlafonne("cotises", membres), proratisation,
      );
      eligiblesMinimum.push({
        indice: indicePension,
        prorataAssurance: prorata,
        prorataCotise: cotisesRegime / proratisation,
        tauxPlein: trimestres >= requis
          || ageLiquidation >= ouvrir.ageTauxPlein(moteur, periode, carriere),
        surcote: coefficientSurcote,
      });
    }
    if (periode.avantages_non_contributifs.includes("minimum_garanti")) {
      // Depuis la loi du 9 novembre 2010, le minimum garanti n'est dû qu'au
      // taux plein. Les assurés qui atteignaient l'âge d'ouverture de leurs
      // droits avant 2011 gardent le droit inconditionnel, et le c de L. 17
      // sous quinze ans ; les autres ont le d.
      const ageOuverturePeriode = ouvrir.ageOuverture(moteur, periode, carriere);
      const ancienDroit = carriere.annee_naissance + ageOuverturePeriode < 2011;
      // L'âge d'annulation de la décote qui ouvre le minimum est minoré à
      // titre transitoire, selon l'année où l'âge d'ouverture est atteint
      // (décret n° 2010-1744, article 3).
      const fonctionPublique = moteur.catalogue.obtenir(code).famille === "fonction_publique";
      const minoration = fonctionPublique
        ? (MINORATION_AGE_MINIMUM_GARANTI[
          carriere.dateNaissance.plusMois(enMois(ageOuverturePeriode)).annee] ?? 0)
        : 0;
      eligiblesGaranti.push({
        indice: indicePension,
        trimestresServices: cumulPlafonne("services", membres),
        ouvert: ancienDroit
          || trimestresDecote <= 0
          || trimestres >= requis
          || (minoration > 0 && ageAnnulation !== null
            && ageLiquidation + 1e-9 >= ageAnnulation - minoration / 4),
        // Le d et la minoration ne valent que pour la fonction publique.
        dureeMaximum: fonctionPublique && !ancienDroit ? proratisation : null,
      });
    }
    pensions.push({
      regime: code,
      montant: salaireReference * taux * prorata,
      type_calcul: "annuites",
      // Salaire de référence au centime et taux au millième : à l'euro et au
      // centième, refaire « SR × taux × durée » ratait le montant de 1,20 €
      // sur un régime spécial, le taux arrondi pesant à lui seul 0,89 €.
      detail: `${forfaitaire ? "forfait" : "SR"} `
        + `${formatFixe(salaireReference, 2, true)} € `
        + `× taux ${formatPourcentage(taux, 3)} × ${trimestresRegime}/${proratisation}`
        + (trimestresRegime / proratisation > rapportMaximum
          ? `, taux maximum ${formatPourcentage(periode.taux_maximum_bonifie, 0)} atteint`
          : "")
        // La succession est DITE : sans elle, le lecteur cherche la ligne
        // de la CANCAVA et ne la trouve pas.
        + (membres.length === 1 ? "" : `, ${membres.length} caisses liquidées ensemble `
          + `(${membres.slice(1).join(", ")} puis ${membres[0]})`),
      fiabilite: Math.min(...membres.map((m) => moteur.catalogue.obtenir(m).fiabilite)),
    });
  }

  return new Pensions({
    personne: carriere.personne,
    regimes: pensions,
    minimum: eligiblesMinimum,
    garanti: eligiblesGaranti,
    requis: trimestresRequis,
    taux: tauxRetenu,
    fiabilite: fiabiliteGlobale,
  });
}

/**
 * Ce que vaut, à la liquidation, un point acquis dans ``code``.
 *
 * Un régime fermé ne sert plus ses points : ils ont été convertis dans son
 * successeur, au coefficient que l'accord de fusion a fixé. La méthode remonte
 * la chaîne des successions en cumulant ces coefficients, qui sont LUS dans
 * ``regimes/conversions_points.csv`` et non plus déduits d'un rapport de
 * valeurs de service.
 *
 * Les déduire coûtait cher : la valeur du successeur était lue à sa PREMIÈRE
 * année publiée, or les séries `arrco` et `ircantec` sont rétro-remplies bien
 * avant leur fusion. Le point UNIRS ressortait quinze fois trop cher pour
 * toute liquidation postérieure à 1998, le point IPACTE cinquante fois trop
 * cher au-delà de 2022. Et là où les bornes tombaient juste, la valeur était
 * celle du 31 décembre quand la conversion s'opère au 1er janvier.
 *
 * Quand la chaîne s'arrête — plus de successeur, ou aucun coefficient déclaré
 * — la dernière valeur publiée est ramenée en euros de la liquidation par
 * l'indice des prix, approximation signalée par la fiabilité.
 */
export function valeurDuPoint(moteur, code, anneeLiquidation) {
  let conversion = 1.0;
  let courant = code;
  let fiabilite = Fiabilite.CERTIFIEE;
  for (let garde = 0; garde < moteur.catalogue.taille + 1; garde += 1) {
    const derniere = moteur.valeursPoint.derniereAnneeServie(courant);
    if (derniere === null) {
      return null;
    }
    if (anneeLiquidation <= derniere) {
      const valeur = moteur.valeursPoint.service(courant, anneeLiquidation);
      if (valeur === null) {
        // Liquidation antérieure au premier barème publié. Symétrique du cas
        // ci-dessous : la première valeur connue est ramenée en euros de la
        // liquidation par l'indice des prix, et la fiabilité tombe pour le dire.
        const premiereConnue = moteur.valeursPoint.premiereAnneeServie(courant);
        const ancienne = moteur.valeursPoint.service(courant, premiereConnue);
        return [
          conversion * ancienne[0]
            * moteur.macro.coefficientPrix(premiereConnue, anneeLiquidation),
          Math.min(fiabilite, ancienne[1], Fiabilite.MOYENNE),
        ];
      }
      return [conversion * valeur[0], Math.min(fiabilite, valeur[1])];
    }

    const successeur = moteur.catalogue.contient(courant)
      ? moteur.catalogue.obtenir(courant).integre_dans
      : null;
    const reprise = successeur
      ? moteur.conversionsPoints.fusion(courant, successeur)
      : null;
    if (reprise === null) {
      // AVEC UN AN DE RETARD : la revalorisation du 1er janvier suit les prix
      // de l'année écoulée (L. 161-25). Voir le Python.
      const ancienne = moteur.valeursPoint.service(courant, derniere);
      return [
        conversion * ancienne[0]
          * moteur.macro.coefficientPrix(derniere - 1, anneeLiquidation - 1),
        Math.min(fiabilite, ancienne[1], Fiabilite.MOYENNE),
      ];
    }

    conversion *= reprise.coefficient;
    fiabilite = Math.min(fiabilite, reprise.fiabilite);
    courant = successeur;
  }
  return null;
}

/**
 * La rémunération que ce régime liquide : `assietteDeReference`, et, pour un
 * régime à grille, le salaire forfaitaire de la catégorie — le marin liquide
 * « sur le salaire forfaitaire de la catégorie dans laquelle il a été
 * classé » (R. 11), non sur sa paie. Proratisé sur les mois de l'année.
 */
export function assietteDeReference(moteur, periode, ligne) {
  // Une année RÉTABLIE porte au compte le dernier traitement : voir `retablir` (`droit/coordonner.js`).
  if (ligne.revenu_retabli > 0 && periode.assiette !== "primes_uniquement") {
    return ligne.revenu_retabli;
  }
  if (periode.assiette_grille) {
    const forfaitGrille = moteur.grilles.forfait(
      periode.assiette_grille, ligne.annee, ligne.revenuAnnualise,
      (a) => salaireMoyenAnnuel(moteur.macro, a),
    );
    if (forfaitGrille !== null) {
      return forfaitGrille[0] * ligne.fraction_annee;
    }
  }
  if (periode.assiette_forfaitaire) {
    // L'ASSIETTE FORFAITAIRE EST AUSSI LE SALAIRE PORTÉ AU COMPTE : le
    // salaire annuel moyen du régime des cultes est fait du forfait de
    // l'année, « une base SMIC pour tous les assurés cultuels » (CAVIMAC).
    // Voir `_assiette_de_reference` dans le Python.
    const annuelle = moteur.catalogue.obtenir(periode.regime).periode(ligne.annee) ?? periode;
    if (annuelle.assiette_repere_smic !== null && annuelle.assiette_repere_smic !== undefined) {
      return annuelle.assiette_repere_smic
        * moteur.macro.smic_horaire.valeur(ligne.annee) * ligne.fraction_annee;
    }
  }
  return _assietteDeReference(periode, ligne);
}

/**
 * Salaire de référence, en euros de l'année de liquidation. Il porte sur les
 * seules années passées dans ce régime — ou dans l'un des `membres` de sa
 * chaîne de succession, quand `code` liquide pour un régime qu'il a
 * absorbé : les années CANCAVA d'un artisan sont des années du RSI, puis du
 * régime général, et n'entrent qu'une fois dans un seul salaire annuel
 * moyen. Voir `groupesDeSuccession`.
 */
export function salaireDeReference(moteur, code, carriere, periode, anneeLiquidation, plafonner,
  generation = null, avpf = true, membres = null, enfantsMajores = 0) {
  const codesAdmis = new Set(membres && membres.length > 0 ? membres : [code]);
  const avpfOuvert = avpf
    && periode.avantages_non_contributifs.includes("avpf");
  // Les coefficients des arrêtés ne valent que pour un salaire PORTÉ AU
  // COMPTE. Un régime qui liquide sur le dernier traitement ne porte rien à
  // un compte : lui appliquer les coefficients du régime général serait une
  // erreur de catégorie. Le traitement d'un FONCTIONNAIRE suit le point
  // d'indice — l'agent garde son indice — ; les autres régimes à dernier
  // salaire restent sur les prix, avec la réserve de `docs/limites.md`.
  const porteAuCompte = periode.salaire_reference !== "derniers_6_mois"
    && periode.salaire_reference !== "dernier_salaire";
  const suitLePoint = !porteAuCompte
    && moteur.catalogue.contient(code)
    && moteur.catalogue.obtenir(code).famille === "fonction_publique";
  // Le MOIS de la liquidation désigne la circulaire applicable : les arrêtés
  // ne prennent pas tous effet au 1er janvier, et deux d'entre eux portent
  // l'année 2022. Le mois ne vaut que si l'année passée est bien celle de la
  // liquidation — certains appels la bornent à la fiche du régime.
  const moisLiquidation = (carriere.age_liquidation !== null
    && carriere.age_liquidation !== undefined
    && anneeLiquidation === carriere.anneeLiquidation)
    ? carriere.moisLiquidation
    : 1;
  const revaloriser = porteAuCompte
    ? (depart, arrivee) => moteur.macro.coefficientRevalorisationPorteeAuCompte(
      depart, arrivee, moisLiquidation)
    : (depart, arrivee) => {
      if (suitLePoint) {
        const ratio = moteur.minimumGaranti.ratioPointIndice(depart, arrivee);
        if (ratio !== null) {
          return ratio;
        }
      }
      return moteur.macro.coefficientRevalorisationSalaires(depart, arrivee);
    };
  // LE REVENU D'UNE ANNÉE, TOUTES ACTIVITÉS DU RÉGIME RÉUNIES : deux
  // activités qui versent au même régime, ou à deux régimes alignés que la
  // liquidation unique réunit, forment un seul revenu annuel, écrêté UNE fois
  // au plafond (R. 173-4-4-1, 1°). Une année d'une seule activité n'a qu'un
  // terme, et rien ne bouge.
  const parAnnee = new Map();
  for (const ligne of carriere.lignes) {
    if (ligne.annee >= anneeLiquidation) {
      continue;
    }
    if (!coordonner.regimesDe(moteur, 
      ligne, ligne.annee, carriere.dateEntree(ligne.affiliation),
      ligne.cotise ? ligne.revenu : ligne.revenu_reference,
      moteur.macro.plafond_securite_sociale.valeur(ligne.annee),
    ).some((c) => codesAdmis.has(c))) {
      continue;
    }
    let revenu;
    if (!ligne.cotise) {
      // Assurance vieillesse des parents au foyer : la CNAF cotise sur une
      // assiette forfaitaire égale au SMIC, et ce salaire est PORTÉ AU
      // COMPTE. C'est ce qui la distingue d'une période assimilée, laquelle
      // valide des trimestres sans jamais ajouter de salaire.
      if (!(avpfOuvert && ligne.revenu_avpf > 0)) {
        continue;
      }
      revenu = ligne.revenu_avpf;
    } else {
      revenu = Math.max(assietteDeReference(moteur, periode, ligne),
        acquerir.assietteMinimale(moteur, [...codesAdmis], ligne));
    }
    // TRANCHE DE SALAIRE. Un régime qui liquide tranche par tranche — le
    // personnel navigant, 1,85 % par annuité sur la première et 1,4 % sur la
    // seconde (R. 426-16-1) — a besoin du salaire de SA tranche, sans quoi
    // les deux périodes simultanées calculeraient le même salaire moyen.
    // N'affecte que les assiettes à borne basse non nulle : celles qui
    // partent de zéro passent par `plafonner` comme avant.
    const [borneBasse, borneHaute] = periode.bornesAssietteEnEuros(
      moteur.macro.plafond_securite_sociale.valeur(ligne.annee)
        * ligne.fraction_annee,
    );
    if (borneBasse > 0) {
      revenu = Math.max(0.0, Math.min(revenu, borneHaute || revenu) - borneBasse);
    }
    const [somme, fraction] = parAnnee.get(ligne.annee) ?? [0.0, 0.0];
    parAnnee.set(ligne.annee,
      [somme + revenu, Math.max(fraction, ligne.fraction_annee)]);
  }

  const revenus = [];
  // Le dernier revenu avant revalorisation, et son année : ce qu'une pension
  // différée revalorise autrement (voir plus bas).
  let dernierBrut = null;
  for (const annee of [...parAnnee.keys()].sort((a, b) => a - b)) {
    let [revenu, fraction] = parAnnee.get(annee);
    if (plafonner) {
      // Le plafond se proratise sur les mois travaillés : l'année d'entrée
      // dans la vie active n'est pas pleine.
      revenu = Math.min(
        revenu, moteur.macro.plafond_securite_sociale.valeur(annee) * fraction,
      );
    }
    dernierBrut = [annee, revenu];
    revenus.push(revenu * revaloriser(annee, anneeLiquidation));
  }

  if (revenus.length === 0) {
    return 0.0;
  }

  const reference = periode.salaire_reference;
  let retenus;
  if (reference === "25_meilleures_annees" || reference === "10_meilleures_annees") {
    let annees = reference === "25_meilleures_annees" ? 25 : 10;
    if (periode.salaire_reference_par_generation && generation !== null) {
      const parGeneration = moteur.anneesSalaireReference.annees(generation);
      if (parGeneration !== null) {
        annees = parGeneration[0];
      }
      // LES PARENTS : vingt-quatre années pour qui bénéficie d'une
      // majoration ou d'une bonification au titre d'un enfant, vingt-trois
      // pour deux enfants et plus, pensions prenant effet à compter du
      // 1er septembre 2026 (R. 173-3-2, décret n° 2026-699).
      if (enfantsMajores > 0 && carriere.age_liquidation !== null
          && carriere.dateLiquidation.rang >= moteur.parentsMeilleuresAnneesDepuis) {
        annees = Math.max(1, annees - (enfantsMajores === 1 ? 1 : 2));
      }
    }
    retenus = [...revenus].sort((a, b) => b - a).slice(0, annees);
  } else if (reference === "derniers_6_mois" || reference === "dernier_salaire") {
    // Le traitement des six derniers mois est celui EN VIGUEUR au départ.
    // L'année de la liquidation est incomplète — l'assuré n'y a travaillé que
    // quelques mois —, mais c'est bien son traitement que liquide le régime :
    // on l'annualise plutôt que de reculer d'un an.
    // La ligne du régime, et non l'activité principale : un fonctionnaire
    // qui cumule une activité libérale liquide son traitement.
    const derniere = carriere.lignesDe(anneeLiquidation).find(
      (ligne) => coordonner.regimesDe(moteur, 
        ligne, anneeLiquidation,
        carriere.dateEntree(ligne.affiliation),
        ligne.revenu, moteur.macro.plafond_securite_sociale.valeur(anneeLiquidation))
        .some((c) => codesAdmis.has(c)),
    ) ?? null;
    if (derniere !== null && derniere.cotise && derniere.fraction_annee > 0) {
      let traitement = assietteDeReference(moteur, periode, derniere)
        / derniere.fraction_annee;
      if (plafonner) {
        traitement = Math.min(
          traitement,
          moteur.macro.plafond_securite_sociale.valeur(anneeLiquidation),
        );
      }
      return traitement;
    }
    // LA PENSION DIFFÉRÉE : le traitement de l'agent radié suit les
    // revalorisations des pensions de la radiation à la mise en paiement
    // (L. 25 du code des pensions), et non le point d'indice. Voir le Python.
    if (dernierBrut !== null && REGIMES_CODE_DES_PENSIONS.has(code)) {
      const [derniereAnnee, brut] = dernierBrut;
      const radiation = dateIso(derniereAnnee + 1, 1, 1);
      const paiement = dateIso(anneeLiquidation, moisLiquidation, 1);
      if (radiation < paiement && paiement >= FIN_PEREQUATION) {
        const coefficient = coefficientTraitementDiffere(
          moteur.revalorisationsPensions,
          (depart, arrivee) => moteur.minimumGaranti.ratioPointIndice(depart, arrivee),
          derniereAnnee, radiation, paiement,
        );
        if (coefficient !== null) {
          return brut * coefficient;
        }
      }
    }
    return revenus[revenus.length - 1];
  } else {
    retenus = revenus;
  }
  return retenus.reduce((total, valeur) => total + valeur, 0.0) / retenus.length;
}

/**
 * Dénominateur du coefficient de proratisation, dans ce régime.
 *
 * Il vaut la durée requise partout, sauf pour les générations 1944 à 1948 et
 * celles qui les précèdent, auxquelles l'article R. 351-6 oppose une durée
 * maximale plus courte — 150 trimestres avant 1944, puis 152, 154, 156, 158
 * et 160. La table ne répond que là ; ailleurs c'est la durée requise qui
 * fait office, comme le droit le veut depuis 1949.
 *
 * @returns {[number, number|null]} durée de proratisation, et fiabilité.
 */
export function dureeProratisation(moteur, periode, carriere, requis) {
  // La table est celle du CODE DE LA SÉCURITÉ SOCIALE, et la fiche dit qui la
  // suit : le régime général et les régimes alignés. La fonction publique et
  // les régimes spéciaux ont la leur, calendaire (article L. 13 du code des
  // pensions) ; elle n'est pas modélisée, et leur durée requise y fait office.
  if (!periode.duree_proratisation_par_generation) {
    return [requis, null];
  }
  const parGeneration = moteur.dureesProratisation.trimestres(carriere.generation);
  if (parGeneration === null) {
    return [requis, null];
  }
  // Elle ne dépasse jamais la durée requise : les périodes anciennes, dont la
  // durée maximale est plus courte que 150 trimestres, gardent la leur.
  return [Math.min(parGeneration[0], requis), parGeneration[1]];
}

/**
 * Décote opposable : coefficient, âge d'annulation, fiabilité.
 *
 * La FONCTION PUBLIQUE n'a pas la décote du régime général. L'article L. 14
 * du code des pensions lui donne la sienne, montée en charge de 2006 à 2020,
 * et surtout un âge d'annulation qui n'est pas un âge en propre : c'est la
 * LIMITE D'ÂGE du grade, diminuée d'un nombre de trimestres décroissant. Un
 * sédentaire dont le droit s'ouvre en 2012 voit sa décote s'annuler à
 * 63 ans, pas à 67 — et chaque trimestre manquant lui coûte 0,875 %, pas
 * 1,25 %.
 *
 * Les barèmes en table se lisent à l'ANNÉE D'OUVERTURE DU DROIT, pas à
 * celle de la liquidation : « Année au cours de laquelle sont réunies les
 * conditions mentionnées au I et au II de l'article L. 24 », titre le III
 * de l'article 66 de la loi du 21 août 2003, et les décrets de 2008 des
 * régimes spéciaux visent de même « les personnes remplissant les
 * conditions ». Voir `anneeOuvertureDesDroits`.
 *
 * @returns {[number|null, number, number|null]} coefficient, âge, fiabilité.
 */
export function decoteOpposable(moteur, periode, carriere, anneeLiquidation) {
  const ageAnnulation = ouvrir.ageTauxPlein(moteur, periode, carriere);
  if (BAREMES_DECOTE_EN_TABLE.has(periode.bareme_decote)) {
    const table = periode.bareme_decote === "fonction_publique"
      ? moteur.decoteFonctionPublique
      : moteur.decoteRegimesSpeciaux;
    const parametres = table.parametres(
      ouvrir.anneeOuvertureDesDroits(moteur, periode, carriere, anneeLiquidation),
    );
    if (parametres === null || parametres === undefined) {
      return [null, ageAnnulation, null];
    }
    const [trimestresAvant, coefficient, fiabilite] = parametres;
    if (periode.bareme_decote === "regimes_speciaux_age_fixe") {
      // Les catégories d'âge atypique — artistes du ballet, musiciens de
      // l'orchestre — n'ont pas l'âge de référence de droit commun : le V de
      // l'article 14 leur donne leur âge d'ouverture majoré de huit
      // trimestres, un âge fixe que la montée en charge ne recule pas.
      return [coefficient, ageAnnulation, fiabilite];
    }
    return [coefficient, ageAnnulation - trimestresAvant / 4.0, fiabilite];
  }
  if (periode.decote_par_trimestre === null) {
    return [null, ageAnnulation, null];
  }
  if (periode.age_table) {
    // Le taux que le règlement de la section écrit pour la génération,
    // quand il en écrit un : la CARCDSF de 2011 à 2023.
    const propre = moteur.agesRegimes.decote(periode.age_table, carriere.generation);
    if (propre !== null) {
      return [propre[0], ageAnnulation, propre[1]];
    }
  }
  if (periode.decote_par_generation) {
    const parGeneration = moteur.coefficientsMinoration.coefficient(
      carriere.annee_naissance,
    );
    if (parGeneration !== null) {
      return [parGeneration[0], ageAnnulation, parGeneration[1]];
    }
  }
  return [periode.decote_par_trimestre, ageAnnulation, null];
}

/** Trimestres retranchés à la durée requise pour compter la décote. */
export function retrancheDecote(moteur, periode, carriere) {
  const propre = ouvrir.dureePropre(moteur, periode, carriere);
  return propre === null ? 0 : propre[1];
}

export function trimestresDeDecote(moteur, periode, carriere, trimestres, requis, ageLiquidation,
  ageAnnulation) {
  // LE MILITAIRE A LA SIENNE, et elle ne compte pas des âges. Le II de
  // l'article L. 14 lui oppose « le nombre de trimestres manquants […] pour
  // atteindre […] la durée de services militaires effectifs nécessaire pour
  // pouvoir bénéficier d'une liquidation de la pension […] augmentée d'une
  // durée de services effectifs de dix trimestres », dans la limite de dix
  // trimestres et non de vingt.
  const militaire = ouvrir.droitMilitaire(moteur, periode, carriere);
  if (militaire !== null) {
    const manquantsServices = Math.max(
      0, militaire.trimestresCible - militaire.trimestresServis,
    );
    const manquantsDuree = Math.max(0, requis - trimestres);
    return Math.min(manquantsServices, manquantsDuree, TRIMESTRES_DECOTE_MILITAIRE);
  }
  // Arrondi à l'entier supérieur, comme le veut l'article R. 351-27 : les
  // âges d'annulation des générations 1951 à 1954 ne tombent pas sur un
  // trimestre entier, et l'on opposait 13,32 trimestres là où le droit en
  // oppose 14.
  const manquantsAge = auTrimestreSuperieur((ageAnnulation - ageLiquidation) * 4);
  // La SNCF compte la décote par la durée sur une cible abaissée de deux à
  // dix trimestres selon la génération (décret n° 2008-639, article 35, II).
  const cible = requis - retrancheDecote(moteur, periode, carriere);
  // La CRPN depuis 2022 compte la durée seule, l'âge d'annulation ne faisant
  // qu'effacer la décote (R. 6527-22 et R. 6527-23 du code des transports).
  let trimestresDecote;
  if (periode.decote_par_la_duree_seule) {
    trimestresDecote = manquantsAge <= 0 ? 0 : Math.max(0, requis - trimestres);
  } else {
    trimestresDecote = periode.decote_annulee_par_la_duree
      ? Math.min(Math.max(0, cible - trimestres), manquantsAge)
      : manquantsAge;
  }
  if (trimestresDecote <= 0) {
    return 0.0;
  }
  if (periode.decote_trimestres_maximum !== null) {
    trimestresDecote = Math.min(trimestresDecote, periode.decote_trimestres_maximum);
  }
  return trimestresDecote;
}

/** Valeur de service du point écrite dans la fiche, à l'année demandée.
 *
 * La MSA est seule à publier celle de sa retraite proportionnelle. Une ancre
 * datée suffit : la loi (L. 161-23-1) la revalorise sur les prix.
 */
export function valeurPointFiche(moteur, periode, annee) {
  if (periode.valeur_point_euros === null || periode.valeur_point_euros === undefined) {
    return 0.0;
  }
  return periode.valeur_point_euros * moteur.macro.coefficientPrix(
    periode.valeur_point_annee ?? annee, annee,
  );
}

/**
 * Coefficient qui reprend la décote du régime de base — à deux pentes quand
 * la fiche en écrit deux : la CAVP minore de 1,25 % par trimestre jusqu'à
 * 65 ans et de 0,5 % de 65 ans à l'âge du taux plein. Les trimestres d'avant
 * le palier se comptent au premier taux. Voir le modèle Python.
 */
export function abattementRegimeDeBase(moteur, periode, carriere, trimestres, requis, ageLiquidation,
  anneeLiquidation) {
  const [decote, ageAnnulation] = decoteOpposable(moteur, periode, carriere, anneeLiquidation);
  if (decote === null) {
    return 1.0;
  }
  const trimestresDecote = trimestresDeDecote(
    moteur, periode, carriere, trimestres, requis, ageLiquidation, ageAnnulation,
  );
  const palier = periode.decote_palier_age ?? null;
  const tauxApres = periode.decote_par_trimestre_apres_palier ?? null;
  if (palier !== null && tauxApres !== null && trimestresDecote > 0) {
    const avant = Math.min(
      trimestresDecote, auTrimestreSuperieur((palier - ageLiquidation) * 4),
    );
    const apres = trimestresDecote - avant;
    return Math.max(0.0, 1.0 - decote * avant - tauxApres * apres);
  }
  return Math.max(0.0, 1.0 - decote * trimestresDecote);
}

/**
 * Le taux plein qu'une section ouvre aux mères avant son âge : une année
 * par enfant à la CARCDSF, cinq au plus. Les dispositions générales et
 * particulières « sont exclusives les unes des autres » : l'anticipation
 * ouvre le taux plein à un âge, elle n'abaisse pas l'âge dont se compte la
 * minoration. Voir le modèle Python.
 */
export function tauxPleinAnticipe(moteur, periode, carriere, ageLiquidation) {
  const parEnfant = periode.taux_plein_anticipe_par_enfant_annees ?? null;
  if (parEnfant === null || carriere.sexe !== "F" || carriere.nombre_enfants <= 0) {
    return false;
  }
  let anticipation = carriere.nombre_enfants * parEnfant;
  const maximum = periode.taux_plein_anticipe_maximum_annees ?? null;
  if (maximum !== null) {
    anticipation = Math.min(anticipation, maximum);
  }
  return ageLiquidation >= ouvrir.ageTauxPlein(moteur, periode, carriere) - anticipation - 1e-9;
}

/**
 * Minoration des trois régimes de l'IRCEC : 2,5 % pour chacune des deux
 * premières années manquantes jusqu'à l'âge du taux plein, 5 % au-delà, une
 * année entamée comptant entière ; ou la décote du régime de base si elle
 * est plus favorable. `ircec_age_seul` est le RACL de 2014 à 2024 : 5 % par
 * année, sans autre voie que l'âge. Voir le docstring du modèle Python.
 */
export function abattementIrcec(moteur, periode, carriere, trimestres, requis, ageLiquidation,
  anneeLiquidation) {
  const ageTauxPlein = ouvrir.ageTauxPlein(moteur, periode, carriere);
  // `cavom` est la même règle que `ircec_age_seul`, sous un autre
  // règlement : 5 % par année manquante, et seul l'âge ouvre le taux plein.
  const ageSeul = periode.abattement_points === "ircec_age_seul"
    || periode.abattement_points === "cavom";
  if (ageLiquidation >= ageTauxPlein - 1e-9) {
    return 1.0;
  }
  if (!ageSeul && trimestres >= requis) {
    return 1.0;
  }
  const annees = Math.ceil(
    auTrimestreSuperieur((ageTauxPlein - ageLiquidation) * 4) / 4,
  );
  const propre = Math.max(0.0, ageSeul
    ? 1.0 - 0.05 * annees
    : 1.0 - 0.025 * Math.min(annees, 2) - 0.05 * Math.max(0, annees - 2));
  if (ageSeul) {
    return propre;
  }
  return Math.max(propre, abattementRegimeDeBase(
    moteur, periode, carriere, trimestres, requis, ageLiquidation, anneeLiquidation,
  ));
}

export function abattementPoints(moteur, periode, carriere, trimestres, requis, ageLiquidation,
  anneeLiquidation, trimestresRegime = 0) {
  // L'Ircantec a le même barème que l'Agirc-Arrco, et son texte l'écrit :
  // article 16 de l'arrêté du 30 décembre 1970, mêmes marches et mêmes deux
  // lectures. Voir le docstring du modèle Python. `trimestresRegime` est la
  // durée d'affiliation à CE régime, que la CIPAV oppose à sa surcote.
  let abattement;
  if (periode.abattement_points === "agirc_arrco"
    || periode.abattement_points === "ircantec") {
    // Avant l'ASF de 1983, l'âge seul : une période sans durée requise — ni
    // en dur, ni lue à la génération — abat toute anticipation avant
    // l'âge du taux plein, et la table par durée ne s'y consulte pas.
    const parAgeSeul = (periode.duree_requise_trimestres === null
      || periode.duree_requise_trimestres === undefined)
      && !periode.duree_requise_par_generation;
    if (!parAgeSeul && trimestres >= requis) {
      abattement = 1.0;
    } else {
      const parDuree = parAgeSeul
        ? null : coefficientAnticipation(requis - trimestres, 20);
      const ecartAge = Math.max(
        0.0, (ouvrir.ageTauxPlein(moteur, periode, carriere) - ageLiquidation) * 4,
      );
      let parAge = coefficientAnticipation(ecartAge, 40);
      if (parAge === null) {
        parAge = COEFFICIENT_ANTICIPATION_PLANCHER;
      }
      const candidats = [parDuree, parAge].filter((c) => c !== null);
      abattement = candidats.length ? Math.max(...candidats) : 1.0;
    }
  } else if (periode.abattement_points === "ircec"
    || periode.abattement_points === "ircec_age_seul"
    || periode.abattement_points === "cavom") {
    abattement = abattementIrcec(
      moteur, periode, carriere, trimestres, requis, ageLiquidation, anneeLiquidation,
    );
  } else {
    abattement = abattementRegimeDeBase(
      moteur, periode, carriere, trimestres, requis, ageLiquidation, anneeLiquidation,
    );
  }
  if (abattement < 1.0 && tauxPleinAnticipe(moteur, periode, carriere, ageLiquidation)) {
    abattement = 1.0;
  }

  // Abattu et majoré ne se rencontrent pas : les deux majorations de
  // l'arrêté supposent l'âge du taux plein ou la durée requise dépassés,
  // c'est-à-dire un coefficient d'anticipation déjà revenu à 1.
  if (abattement < 1.0) {
    return abattement;
  }
  return surcotePoints(
    moteur, periode, carriere, trimestres, requis, ageLiquidation, anneeLiquidation,
    trimestresRegime,
  );
}

/**
 * Coefficient de surcote, trimestre civil par trimestre civil.
 *
 * Règle de la circulaire Cnav 2018-04 (point 2) : la PÉRIODE DE RÉFÉRENCE
 * commence au plus tard des trois — premier jour du trimestre civil qui
 * suit l'âge légal, premier jour du mois qui suit l'acquisition de la durée
 * requise, 1er janvier 2004 — et s'achève au dernier jour du trimestre
 * civil qui précède la date d'effet. Chaque trimestre civil compte dans la
 * limite des trimestres cotisés de l'année, et au plus `supplementaires` en
 * tout ; chacun prend le taux du barème à sa date. Les trimestres qui ne
 * tiennent à aucune année (majoration pour enfants) sont réputés acquis
 * d'emblée.
 *
 * @returns {[number, number|null]} coefficient et fiabilité.
 */
export function coefficientSurcoteDatee(moteur, periode, carriere, trimestres, requis, supplementaires,
  ageOuverture) {
  const anneeLiquidation = carriere.anneeLiquidation;
  const dateLegal = carriere.dateNaissance.plusMois(enMois(ageOuverture));
  // La fonction publique compte des durées, depuis le premier du mois qui
  // suit l'âge, et non des trimestres civils : voir le Python.
  const enDuree = REGIMES_CODE_DES_PENSIONS.has(periode.regime);
  const trimestreLegal = Math.floor((dateLegal.mois - 1) / 3);
  const debutAge = enDuree
    ? dateLegal.plusMois(1)
    : new DateMois(dateLegal.annee, 1).plusMois(3 * (trimestreLegal + 1));

  const parAnnee = carriere.trimestresParAnnee(carriere.lignes.filter(
    (ligne) => ligne.annee <= anneeLiquidation,
  ));
  const cotisesParAnnee = carriere.trimestresParAnnee(carriere.lignes.filter(
    (ligne) => ligne.cotise && ligne.annee <= anneeLiquidation,
  ));
  let acquis = trimestres;
  for (const valides of parAnnee.values()) {
    acquis -= valides;
  }
  let debutDuree = null;
  if (acquis >= requis) {
    debutDuree = SURCOTE_DEPUIS;
  }
  for (const annee of [...parAnnee.keys()].sort((a, b) => a - b)) {
    if (debutDuree !== null) {
      break;
    }
    const valides = parAnnee.get(annee);
    if (acquis + valides >= requis) {
      const manquants = requis - acquis;
      debutDuree = new DateMois(annee, 1).plusMois(3 * manquants);
    }
    acquis += valides;
  }
  if (debutDuree === null) {
    return [1.0, null];
  }
  let debut = DateMois.depuisRang(Math.max(debutAge.rang, debutDuree.rang, SURCOTE_DEPUIS.rang));
  if ((debut.mois - 1) % 3 && !enDuree) {
    debut = new DateMois(debut.annee, 1).plusMois(3 * (Math.floor((debut.mois - 1) / 3) + 1));
  }
  const fin = carriere.dateLiquidation;
  const date65 = carriere.dateNaissance.plusMois(12 * SURCOTE_AGE_MAJORE);
  const trimestre65 = date65.annee * 4 + Math.floor((date65.mois - 1) / 3);

  const dates = [];
  const restants = new Map(cotisesParAnnee);
  let courant = debut;
  while (courant.rang + 2 < fin.rang && dates.length < supplementaires) {
    if ((restants.get(courant.annee) ?? 0) > 0) {
      restants.set(courant.annee, restants.get(courant.annee) - 1);
      const apres65 = courant.annee * 4 + Math.floor((courant.mois - 1) / 3) > trimestre65;
      // Un trimestre de durée prend le taux de son dernier mois : voir le Python.
      dates.push([enDuree ? courant.plusMois(2) : courant, apres65]);
    }
    courant = courant.plusMois(3);
  }
  if (dates.length === 0) {
    return [1.0, null];
  }
  if (!moteur.surcoteBaremes.connait(periode.surcote_bareme ?? "")) {
    return [1.0 + (periode.surcote_par_trimestre ?? 0.0) * dates.length, null];
  }
  return moteur.surcoteBaremes.coefficient(periode.surcote_bareme, dates);
}

export function surcotePoints(moteur, periode, carriere, trimestres, requis, ageLiquidation,
  anneeLiquidation, trimestresRegime = 0) {
  const mode = periode.surcote_points;
  if (mode === "aucune") {
    return 1.0;
  }
  if (mode === "rafp") {
    // Le RAFP module sa valeur de service par un barème d'âge, sans taux
    // par trimestre : 1,08 à 64 ans, 1,22 à 67, 1,40 à 70.
    return majorationRafp(ageLiquidation);
  }
  if (mode === "ircantec") {
    return surcoteIrcantec(
      moteur, periode, carriere, trimestres, requis, ageLiquidation, anneeLiquidation,
    );
  }
  const taux = periode.surcote_par_trimestre;
  if (!taux) {
    return 1.0;
  }
  if (mode === "regime_general") {
    let supplementaires = Math.max(0, trimestres - requis);
    const ageOuverture = ouvrir.ageOuvertureCommun(moteur, periode, carriere);
    if (supplementaires <= 0 || ageLiquidation < ageOuverture
        || ouvrir.droitMilitaire(moteur, periode, carriere) !== null) {
      return 1.0;
    }
    supplementaires = Math.min(
      supplementaires,
      trimestresCotisesApres(carriere, ageOuverture, anneeLiquidation),
    );
    return 1.0 + taux * supplementaires;
  }
  if (mode !== "par_age_seul") {
    throw new Error(`surcote_points inconnu : ${mode}`);
  }

  const minimum = periode.surcote_affiliation_minimale_trimestres;
  if (minimum !== null && minimum !== undefined && trimestresRegime < minimum) {
    return 1.0;
  }
  let debut = periode.surcote_age_debut;
  if (debut === null || debut === undefined) {
    debut = ouvrir.ageTauxPlein(moteur, periode, carriere);
  }
  let fin = ageLiquidation;
  if (periode.surcote_age_maximum !== null && periode.surcote_age_maximum !== undefined) {
    fin = Math.min(fin, periode.surcote_age_maximum);
  }
  // Des trimestres civils ENTIERS : deux mois de plus ne valent rien.
  let ecoules = Math.floor((Math.max(0.0, fin - debut) + 1e-9) * 4);
  if (periode.surcote_trimestres_cotises) {
    // « Pour chaque année pleine COTISÉE dans le présent régime » (CAVAMAC
    // depuis 2024) : le temps écoulé sans cotiser ne compte plus.
    ecoules = Math.min(ecoules, trimestresCotisesApres(carriere, debut, anneeLiquidation));
  }
  if (periode.surcote_trimestres_maximum !== null
      && periode.surcote_trimestres_maximum !== undefined) {
    ecoules = Math.min(ecoules, periode.surcote_trimestres_maximum);
  }
  const pas = Math.max(1, periode.surcote_pas_trimestres ?? 1);
  ecoules -= ecoules % pas;
  if (ecoules <= 0) {
    return 1.0;
  }
  const palier = periode.surcote_palier_age;
  const tauxApres = periode.surcote_par_trimestre_apres_palier;
  if (palier === null || palier === undefined
      || tauxApres === null || tauxApres === undefined) {
    return 1.0 + taux * ecoules;
  }
  const avantPalier = Math.min(
    ecoules, Math.max(0, Math.floor((palier - debut + 1e-9) * 4)),
  );
  return 1.0 + taux * avantPalier + tauxApres * (ecoules - avantPalier);
}

/** Les deux taux du IV de l'article 16 — voir `surcotePoints`. */
export function surcoteIrcantec(moteur, periode, carriere, trimestres, requis, ageLiquidation,
  anneeLiquidation) {
  const ageTauxPlein = ouvrir.ageTauxPlein(moteur, periode, carriere);
  // 1° — le temps écoulé, en trimestres ENTIERS.
  const ecoules = Math.floor(
    (Math.max(0.0, ageLiquidation - ageTauxPlein) + 1e-9) * 4,
  );
  // 2° — la durée cotisée en deçà. Les trimestres au-delà de la durée
  // requise sont les DERNIERS de la carrière : les compter ici suppose que
  // la durée requise était atteinte avant l'âge du taux plein, sans quoi ils
  // tombent dans la fenêtre du 1° et y sont déjà payés.
  let supplementaires = 0;
  const ageOuverture = ouvrir.ageOuvertureCommun(moteur, periode, carriere);
  if (ageLiquidation >= ageOuverture) {
    const avant = Math.min(
      trimestres,
      trimestresValidesAvant(carriere, ageTauxPlein, anneeLiquidation),
    );
    supplementaires = Math.max(0, avant - requis);
    if (supplementaires > 0) {
      supplementaires = Math.min(supplementaires, trimestresCotisesEntre(
        carriere, ageOuverture, ageTauxPlein, anneeLiquidation,
      ));
    }
  }
  return 1.0
    + SURCOTE_IRCANTEC_AGE * ecoules
    + SURCOTE_IRCANTEC_DUREE * supplementaires;
}

/**
 * Coefficients d'anticipation de l'Agirc-Arrco, sous leur forme de barème :
 * un point de pourcentage par trimestre jusqu'à douze, un point et quart
 * jusqu'à vingt, un point trois quarts au-delà — ce dernier palier n'existant
 * que dans la table des âges, qui descend jusqu'à 0,43 pour dix ans.
 */
const PALIERS_ANTICIPATION = [[12, 0.01], [20, 0.0125], [40, 0.0175]];

/** Dernière ligne de la table des âges : dix ans d'anticipation. */
const COEFFICIENT_ANTICIPATION_PLANCHER = 0.43;

/**
 * Majoration par trimestre ENTIER écoulé entre l'âge du taux plein et la
 * liquidation — le 1° du IV de l'article 16 de l'arrêté du 30 décembre 1970.
 * Aucune condition de durée : c'est le temps qui compte.
 */
const SURCOTE_IRCANTEC_AGE = 0.0075;

/**
 * Majoration par trimestre COTISÉ au-delà de la durée requise, entre l'âge
 * légal et l'âge du taux plein — le 2° du même IV. « En aucun cas une même
 * période ne peut donner lieu à la fois » aux deux.
 */
const SURCOTE_IRCANTEC_DUREE = 0.00625;

/**
 * Coefficient d'anticipation pour un nombre de trimestres manquants.
 *
 * ``maximum`` est la dernière ligne du barème : vingt trimestres pour la table
 * des trimestres manquants, quarante pour celle des âges. Au-delà, la table ne
 * dit rien et ``null`` est renvoyé. Les trimestres sont comptés en entiers
 * ARRONDIS AU SUPÉRIEUR : le barème est un escalier.
 */
/**
 * Nombre de trimestres arrondi à l'entier supérieur, jamais négatif.
 *
 * Règle de l'article R. 351-27 pour la décote, et celle que la caisse illustre
 * dans son exemple pour les coefficients d'anticipation. La tolérance de 10⁻³
 * évite qu'un flottant tout juste au-dessus d'un entier n'en fasse compter un
 * de plus.
 */
/**
 * Un nombre à `decimales` chiffres au plus, sans les zéros de fin.
 *
 * Certaines valeurs de service sont des barèmes PUBLIÉS à quatre décimales —
 * 1,8026 € à l'Agirc-Arrco —, d'autres sont CALCULÉES et en portent bien
 * davantage. Les tronquer toutes à quatre inventait un écart de vingt-huit
 * centimes entre la formule affichée et le montant de la ligne ; les afficher
 * toutes à six aurait inventé, à l'inverse, une précision que le barème n'a pas.
 * Chacune est donc écrite à la précision qu'elle porte.
 */
function sansZerosInutiles(valeur, decimales) {
  const texte = formatFixe(valeur, decimales);
  return texte.includes(".") ? texte.replace(/\.?0+$/, "") : texte;
}

/**
 * La formule d'un régime en points, telle qu'on doit pouvoir la refaire.
 *
 * Le coefficient multiplie la SOMME des termes, il ne s'y ajoute pas : il
 * vient donc après, et la somme prend ses parenthèses dès qu'elle en compte
 * plusieurs. Sans lui, la formule affichée ne retrouvait pas le montant de la
 * ligne — à dix ans d'anticipation elle en donnait 2,3 fois trop, sans que
 * rien à l'écran ne dise pourquoi.
 *
 * Il se nomme par ce qu'il fait : « coefficient d'anticipation » quand il
 * retire, « coefficient de majoration » quand il ajoute. Un seul régime
 * ajoute — l'Ircantec, dont le IV de l'article 16 de l'arrêté du 30 décembre
 * 1970 majore les points d'une liquidation tardive.
 */
function formulePoints(termes, coefficient) {
  const formule = termes.join(" + ") || "aucun droit";
  if (coefficient === 1.0 || termes.length === 0) {
    return formule;
  }
  const somme = termes.length > 1 ? `(${formule})` : formule;
  const nom = coefficient > 1.0 ? "de majoration" : "d'anticipation";
  return `${somme} × coefficient ${nom} ${formatFixe(coefficient, 4)}`;
}

export function auTrimestreSuperieur(trimestres) {
  return Math.max(0, Math.ceil(Math.round(trimestres * 1000) / 1000));
}

// RAFP — barème actuariel de modulation de la valeur de service, par âge
// ENTIER à la date d'effet (décret n° 2004-569, art. 8 ; tableau de l'ERAFP).
const MAJORATION_RAFP = {
  62: 1.00, 63: 1.04, 64: 1.08, 65: 1.12, 66: 1.17, 67: 1.22, 68: 1.28,
  69: 1.33, 70: 1.40, 71: 1.47, 72: 1.54, 73: 1.62, 74: 1.71, 75: 1.80,
};

// RAFP — coefficients de conversion en capital depuis le 1er janvier 2022,
// interpolés au mois entre deux âges entiers, comme le document l'écrit.
const CONVERSION_CAPITAL_RAFP = {
  62: 27.11, 63: 26.34, 64: 25.57, 65: 24.79, 66: 24.02, 67: 23.25,
  68: 22.47, 69: 21.70, 70: 20.92, 71: 20.15, 72: 19.37, 73: 18.61,
  74: 17.84, 75: 17.07,
};

function majorationRafp(ageLiquidation) {
  return MAJORATION_RAFP[Math.min(75, Math.max(62, Math.trunc(ageLiquidation + 1e-9)))];
}

function conversionCapitalRafp(ageLiquidation) {
  const age = Math.min(75.0, Math.max(62.0, ageLiquidation));
  const ans = Math.trunc(age + 1e-9);
  if (ans >= 75) {
    return CONVERSION_CAPITAL_RAFP[75];
  }
  const mois = Math.trunc((age - ans) * 12 + 1e-6);
  const bas = CONVERSION_CAPITAL_RAFP[ans];
  return bas + (CONVERSION_CAPITAL_RAFP[ans + 1] - bas) * mois / 12;
}

function coefficientAnticipation(trimestresManquants, maximum) {
  const manquants = auTrimestreSuperieur(trimestresManquants);
  if (manquants <= 0) {
    return 1.0;
  }
  if (manquants > maximum) {
    return null;
  }
  let coefficient = 1.0;
  let precedent = 0;
  for (const [borne, pas] of PALIERS_ANTICIPATION) {
    const tranche = Math.min(manquants, borne) - precedent;
    if (tranche > 0) {
      coefficient -= tranche * pas;
    }
    precedent = borne;
    if (manquants <= borne) {
      break;
    }
  }
  return Math.max(0.0, coefficient);
}

/** Part de la rémunération que ce régime prend en compte. */
function _assietteDeReference(periode, ligne) {
  return periode.partDuRevenu(ligne.revenu, ligne.part_primes);
}

/**
 * Durée d'assurance acquise avant l'année où l'assuré atteint ``age``, périodes
 * assimilées comprises : c'est la durée qu'oppose la condition de taux plein.
 */
function trimestresValidesAvant(carriere, age, anneeLiquidation) {
  return carriere.trimestresCumules(carriere.lignes.filter(
    (ligne) => ligne.annee <= anneeLiquidation
      && ligne.annee - carriere.annee_naissance < age,
  ));
}

/**
 * Trimestres cotisés entre deux âges — bas inclus, haut exclu, à l'âge atteint
 * dans l'année.
 */
function trimestresCotisesEntre(carriere, ageBas, ageHaut, anneeLiquidation) {
  return carriere.trimestresCumules(carriere.lignes.filter((ligne) => {
    const age = ligne.annee - carriere.annee_naissance;
    return ligne.cotise && ligne.annee <= anneeLiquidation
      && age >= ageBas && age < ageHaut;
  }));
}

/**
 * Trimestres cotisés à partir de l'année où l'assuré atteint ``age``. Seuls
 * ceux-là ouvrent droit à la surcote : c'est une récompense du travail
 * prolongé, pas de l'entrée précoce dans la vie active.
 */
function trimestresCotisesApres(carriere, age, anneeLiquidation) {
  return carriere.trimestresCumules(carriere.lignes.filter(
    (ligne) => ligne.cotise && ligne.annee <= anneeLiquidation
      && ligne.annee - carriere.annee_naissance >= age,
  ));
}
