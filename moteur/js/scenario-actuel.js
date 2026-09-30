/**
 * Scénario 1 — le système actuel, tel qu'il est.
 *
 * Portage de ``src/retraite_notionnelle/scenarios/actuel.py``. Ce scénario sert
 * d'étalon : c'est la pension que l'assuré perçoit ou percevra en droit
 * constant. Il conserve tout ce que les scénarios notionnels retirent — minima,
 * majorations, trimestres gratuits, décote et surcote, bonifications.
 *
 * C'est une approximation documentée, pas un simulateur officiel : régimes en
 * annuités par la formule taux × salaire de référence × durée / durée requise ;
 * régimes en points calculés en points quand le barème est connu — prix d'achat
 * publié, ou nombre de points par tranche d'assiette —, au rendement instantané
 * sinon ; trois horloges, comme dans le droit — ce qui s'acquiert lu à l'année
 * travaillée, la montée en charge des réformes à la génération pour cinq
 * paramètres, la liquidation à son année ; avantages datés, chaque fiche de
 * période disant ce que le régime accordait cette année-là. Un écart de quelques
 * pour cent avec la pension réelle est attendu — ce que le modèle mesure de
 * façon robuste, ce sont les écarts ENTRE SCÉNARIOS.
 *
 * Ce module garde les TABLES du droit en vigueur, et le moteur qui les tient.
 * Le calcul est dans `droit/` : l'acquisition, puis `liquider(demande, état,
 * contexte)`, une fonction pure (`droit/liquidation.js`) ; l'ASPA vient
 * ensuite, de l'étape « foyer et net ». `calculer` les enchaîne.
 */

import {
  AgesAnnulationDecote, AgesCategorieActive, AgesJouissanceMilitaire,
  AgesOuverture, AgesRegimes, AgesSurcoteRegimesSpeciaux, AnneesSalaireReference,
  BaremesTrimestre, CarriereLongue,
  CoefficientsMinoration, DecoteFonctionPublique, DecoteRegimesSpeciaux,
  DureesProratisation, DureesRequises, DureesRequisesAvantSoixanteAns,
  DureesRequisesAvantReforme2023, DureesRequisesAvantSuspension,
  DureesRequisesFonctionPublique, DureesRequisesRegimes, CalendriersDureeRequise,
  DureesServicesMilitaires,
  MajorationsPourEnfants, MinimumContributif, MinimumGaranti, MinimumVieillesse,
  ClassesCotisation, ConversionsPoints, Rendements, SalairesForfaitaires,
  Invalidites, MajorationsEnfantsPoints, Reversions, ServicesOuvrantPension, SurcoteBaremes,
  SurcoteParentale,
  ValeursPoint,
} from "./regimes.js";
import { formatFixe } from "./format.js";
import { RevalorisationsPensions, menerAuMois } from "./revalorisation.js";
import { Fiabilite } from "./serie.js";
import * as lesDeparts from "./droit/departs.js";
import { foyerEtNet } from "./droit/foyer.js";
import { ageDeLAspa } from "./droit/invalidite.js";
import * as liquidation from "./droit/liquidation.js";
import * as lesProgressives from "./droit/progressive.js";

/** Rang du mois de septembre 2026 : premières pensions des parents à 24/23 ans. */
const PARENTS_MEILLEURES_ANNEES_DEPUIS = 2026 * 12 + 8;

export class ScenarioActuel {
  constructor(paquet, macro, catalogue, affiliations, parametres) {
    this.macro = macro;
    this.catalogue = catalogue;
    this.affiliations = affiliations;
    this.parametres = parametres;
    this.rendements = new Rendements(paquet);
    this.valeursPoint = new ValeursPoint(paquet);
    this.conversionsPoints = new ConversionsPoints(paquet);
    this.classes = new ClassesCotisation(paquet);
    this.grilles = new SalairesForfaitaires(paquet);
    this.dureesRequises = new DureesRequises(paquet);
    this.dureesRequisesAvantSuspension = new DureesRequisesAvantSuspension(paquet);
    this.dureesRequisesAvantReforme2023 = new DureesRequisesAvantReforme2023(paquet);
    this.dureesRequisesRegimes = new DureesRequisesRegimes(paquet);
    this.calendriersDureeRequise = new CalendriersDureeRequise(paquet);
    this.dureesRequisesFonctionPublique = new DureesRequisesFonctionPublique(paquet);
    this.dureesRequisesAvantSoixanteAns = new DureesRequisesAvantSoixanteAns(paquet);
    this.dureesProratisation = new DureesProratisation(paquet);
    this.agesOuverture = new AgesOuverture(paquet);
    this.agesSurcoteRegimesSpeciaux = new AgesSurcoteRegimesSpeciaux(paquet);
    this.agesAnnulationDecote = new AgesAnnulationDecote(paquet);
    this.agesRegimes = new AgesRegimes(paquet);
    this.agesCategorieActive = new AgesCategorieActive(paquet);
    this.dureesServicesMilitaires = new DureesServicesMilitaires(paquet);
    this.agesJouissanceMilitaire = new AgesJouissanceMilitaire(paquet);
    this.coefficientsMinoration = new CoefficientsMinoration(paquet);
    this.anneesSalaireReference = new AnneesSalaireReference(paquet);
    this.minimumContributif = new MinimumContributif(paquet, macro);
    this.decoteFonctionPublique = new DecoteFonctionPublique(paquet);
    this.decoteRegimesSpeciaux = new DecoteRegimesSpeciaux(paquet);
    this.minimumGaranti = new MinimumGaranti(paquet, macro);
    this.baremesTrimestre = new BaremesTrimestre(paquet, macro);
    // Les revalorisations des pensions servies, qui portent aussi le
    // traitement d'une pension différée : voir `coefficientTraitementDiffere`.
    this.revalorisationsPensions = new RevalorisationsPensions(paquet);
    this.minimumVieillesse = new MinimumVieillesse(paquet, macro);
    this.carriereLongue = new CarriereLongue(paquet);
    // Vrai pendant que `ouvertureCarriereLongue` date le droit : voir le Python.
    this.ouvertureCarriereLongueEnCours = false;
    // Propriété d'instance, comme l'attribut de classe du Python : la mesure
    // des avantages non contributifs la repousse hors de portée pour lire ce
    // que la règle des parents ajoute à une pension.
    this.parentsMeilleuresAnneesDepuis = PARENTS_MEILLEURES_ANNEES_DEPUIS;
    this.surcoteBaremes = new SurcoteBaremes(paquet);
    this.majorationsEnfants = new MajorationsPourEnfants(paquet);
    this.reversions = new Reversions(paquet);
    this.invalidites = new Invalidites(paquet);
    this.servicesOuvrantPension = new ServicesOuvrantPension(paquet);
    this.surcoteParentale = new SurcoteParentale(paquet);
    this.majorationsEnfantsPoints = new MajorationsEnfantsPoints(paquet);
    // Les régimes qui attribuent des POINTS GRATUITS, rangés sous le régime de
    // base dont les années les ouvrent : voir `pointsGratuits`.
    this.pointsGratuitsParBase = new Map();
    for (const regime of catalogue) {
      for (const periode of regime.periodes) {
        const regle = periode.points_gratuits;
        if (regle === null || regle === undefined) {
          continue;
        }
        const attribuants = this.pointsGratuitsParBase.get(regle.regime) ?? [];
        if (!attribuants.includes(regime.code)) {
          this.pointsGratuitsParBase.set(regle.regime, [...attribuants, regime.code]);
        }
      }
    }
  }

  /**
   * Salaire de référence, exprimé en euros de l'année de liquidation.
   *
   * Deux règles de droit commandent ce calcul. La REVALORISATION des salaires
   * portés au compte, d'abord, que le modèle lit dans les arrêtés eux-mêmes
   * plutôt que de la reconstituer — elle commande le résultat deux fois plutôt
   * qu'une, puisque la moyenne porte sur les N meilleures années et que
   * « meilleures » se juge sur des salaires revalorisés. Le NOMBRE D'ANNÉES
   * retenues ensuite, que la loi du 22 juillet 1993 fait passer de dix à
   * vingt-cinq à raison d'une par génération — lu à l'année de naissance,
   * donc, et non à celle de la liquidation.
   *
   * Le salaire retenu est celui de l'assiette du régime, et pas la
   * rémunération entière : la pension civile porte sur le seul traitement
   * indiciaire, primes exclues.
   */
  /**
   * Pension servie par le système en vigueur.
   *
   * ``ignorerPenaliteAge`` neutralise la décote et la surcote liées à l'âge. On
   * ne l'utilise que pour VALORISER DES DROITS ACQUIS à une date donnée — la
   * question n'est alors pas « que toucherait cet assuré s'il liquidait
   * aujourd'hui à 40 ans », qui n'a pas de sens, mais « quels droits sa carrière
   * lui a-t-elle déjà ouverts ». La proratisation par la durée continue de
   * s'appliquer.
   */
  /**
   * L'âge légal de droit commun, sans égard au classement de l'emploi.
   *
   * C'est lui, et non l'âge anticipé, qui commande la SURCOTE : le III de
   * l'article L. 14 ne la donne qu'« au-delà de l'âge mentionné à l'article
   * L. 161-17-2 », et le D du XXIV de l'article 10 de la loi du 14 avril 2023
   * le confirme pour les emplois classés — l'âge anticipé majoré de cinq
   * années, l'âge minoré majoré de dix, c'est-à-dire l'âge légal dans les deux
   * cas.
   */
  /**
   * Âge au-delà duquel les trimestres cotisés ouvrent la surcote : l'âge légal
   * de droit commun, sauf pour la SNCF et la RATP, qui écrivent le leur.
   */
  /**
   * L'âge auquel cette carrière obtient le TAUX PLEIN, et non seulement le
   * droit de partir.
   *
   * Les deux âges ne se confondent pas, et l'écart entre eux est l'un des
   * ressorts du système : la loi ouvre le droit à soixante-quatre ans, mais elle
   * ne le sert entier qu'à qui a la durée requise — cent soixante-douze
   * trimestres pour les générations d'après 1964. Un cadre entré à vingt-trois
   * ans ne les a pas à soixante-quatre : partir là serait partir avec une
   * décote de huit trimestres, ce que personne ne fait.
   *
   * Trois termes, et le plus tardif des deux premiers l'emporte, sous le
   * plafond du troisième : l'âge d'ouverture ; l'âge auquel la DURÉE requise
   * est atteinte, déduit sans simuler — il manque `requis - acquis` trimestres,
   * et une année pleine en rend quatre, la soustraction étant signée ; l'âge
   * d'annulation de la décote, qui donne le taux plein sans condition de durée
   * et au-delà duquel attendre ne rapporte plus de taux. La durée acquise
   * compte les trimestres pour enfants, et la carrière longue passe avant.
   */
  /**
   * Trimestres de décote opposables, plafond compris.
   *
   * Le décompte retient le plus favorable des deux : trimestres manquants pour
   * la durée requise, ou trimestres manquants jusqu'à l'âge d'annulation de la
   * décote. Et il est PLAFONNÉ — vingt trimestres partout où une décote
   * s'applique.
   *
   * Avant l'ordonnance du 26 mars 1982, le taux ne dépendait QUE de l'âge :
   * aucune durée, si longue fût-elle, n'ouvrait le taux plein avant l'heure.
   */
  /** Rang du mois où l'assuré réunit les conditions : l'âge d'ouverture
   * atteint, ou la liquidation si elle vient avant. */
  /**
   * Abattement d'un régime en points liquidé avant le taux plein.
   *
   * « Avant le taux plein » est une condition de DURÉE autant que d'âge : une
   * complémentaire est servie sans abattement dès que l'assuré a le taux plein
   * au régime de base. L'Agirc-Arrco, elle, ne reprend pas la décote du régime
   * de base : elle publie ses propres COEFFICIENTS D'ANTICIPATION, en deux
   * tables — trimestres manquants, et âge — et retient la plus avantageuse.
   */
  /**
   * Majoration d'un régime en points liquidé APRÈS le taux plein.
   *
   * Trois façons de compter, et la fiche dit laquelle par `surcote_points` :
   * `regime_general`, les trimestres COTISÉS après l'âge légal et au-delà de
   * la durée requise, comme la branche en annuités (CNAVPL, R. 643-8 ; MSA
   * des non-salariés, D. 732-42) ; `par_age_seul`, les trimestres civils
   * ENTIERS écoulés depuis `surcote_age_debut` — l'âge du taux plein à
   * défaut —, sans condition de durée, bornés par `surcote_age_maximum` et
   * `surcote_trimestres_maximum`, comptés par `surcote_pas_trimestres`, à un
   * second taux après `surcote_palier_age`, et dus seulement au-delà de
   * `surcote_affiliation_minimale_trimestres` d'affiliation au régime, comme
   * l'écrivent les statuts des sections libérales ; `ircantec`, le IV de
   * l'article 16 de l'arrêté du 30 décembre 1970 et ses deux taux. Voir le
   * docstring du modèle Python.
   */
  /**
   * Pension servie par le système en vigueur, à la date d'effet : la
   * liquidation (`droit/liquidation.js`), puis l'ASPA de l'étape « foyer et
   * net ». Les drapeaux sont ce qu'une couche d'un seul calcul neutralise ;
   * `nature` est celle de la demande. Voir le Python.
   */
  calculer(carriereSaisie, ignorerPenaliteAge = false, avantagesNonContributifs = true,
    avpf = true, liquiderSuccessions = true, pointsGratuits = null, nature = "definitive") {
    // `pointsGratuits` nul suit `avantagesNonContributifs` : voir le Python.
    const avecPointsGratuits = pointsGratuits ?? avantagesNonContributifs;
    const neutralisations = [
      ["avantages_non_contributifs", !avantagesNonContributifs],
      ["avpf", !avpf],
      ["points_gratuits", !avecPointsGratuits],
      ["decote_surcote", ignorerPenaliteAge],
      ["successions", !liquiderSuccessions],
    ].filter(([, neutre]) => neutre).map(([nom]) => nom);
    const contexte = new liquidation.Contexte(this, neutralisations);
    // LA RETRAITE PROGRESSIVE (`droit/progressive.js`) se liquide d'abord, à
    // titre provisoire, et laisse aux départs le plancher de la pension
    // complète. La liquidation fictive ne la voit pas.
    let progressive = null;
    let provisoire = null;
    if (nature !== "fictive") {
      progressive = lesProgressives.examiner(this, carriereSaisie);
      if (progressive !== null && progressive.ouverte) {
        provisoire = lesProgressives.liquider(this, carriereSaisie, contexte, progressive);
        progressive = lesProgressives.avecLaDuree(progressive, provisoire);
      }
    }
    const plancher = progressive !== null && progressive.ouverte
      ? [progressive, provisoire] : null;
    // CHAQUE RÉGIME LIQUIDE À SA DATE (`droit/departs.js`), sauf la
    // liquidation fictive, qui valorise des droits à une date. Un seul départ
    // qui n'est pas le départ déclaré se liquide à sa date, comme plusieurs.
    const [departs, demandes] = nature !== "fictive"
      ? lesDeparts.departsEtDemandes(this, carriereSaisie) : [[], []];
    let sortie;
    if (departs.length > 1 || (departs.length === 1 && !departs[0].unique)) {
      const liquidations = lesDeparts.liquiderLesDeparts(
        this, carriereSaisie, contexte, nature, departs, null, plancher);
      sortie = resultatDesDeparts(this, carriereSaisie, departs, liquidations, contexte);
    } else {
      const resultat = liquidation.liquider(
        liquidation.demandeDeDepart(carriereSaisie, nature),
        etatDuDepart(this, carriereSaisie, plancher), contexte);
      const carriere = resultat.carriere;
      const foyer = foyerEtNet(
        this, carriere.personne, resultat.demande.dateEffet, carriere.anneeLiquidation,
        resultat.total, (carriere.age_liquidation || 0.0) >= ageDeLAspa(this, carriere),
        contexte);
      sortie = resultatActuel(resultat, foyer);
    }
    if (progressive !== null) {
      sortie.retraite_progressive = progressiveServie(progressive, provisoire,
        carriereSaisie.dateLiquidation);
    }
    if (demandes.length > 0) {
      sortie.demandes = demandes;
    }
    return sortie;
  }
}

/**
 * Le scénario 1 à une date d'effet : la liquidation, puis ce que l'étape « foyer
 * et net » y ajoute — l'ASPA, qui complète tout le reste jusqu'au barème.
 */
export function resultatActuel(resultat, foyer) {
  let total = resultat.total;
  const avantages = [...resultat.avantages];
  let fiabilite = resultat.fiabilite;
  if (foyer.minimumVieillesse > 0) {
    total = foyer.plafond;
    fiabilite = Math.min(fiabilite, foyer.fiabilite);
    avantages.push(foyer.avantage());
  }
  return {
    pension_annuelle: Math.max(0.0, total - resultat.horsRepartition),
    pension_hors_repartition: resultat.horsRepartition,
    pensions_par_regime: [...resultat.regimes],
    trimestres_valides: resultat.releve.durees.trimestres,
    trimestres_requis: resultat.pensions.requis,
    taux_liquidation: resultat.pensions.taux,
    minimum_applique: resultat.complements.minimumApplique,
    age_ouverture_opposable: resultat.ouverture.age,
    liquidation_ouverte: resultat.ouverture.ouverte,
    motif_ouverture: resultat.ouverture.motif,
    avantages_appliques: avantages,
    total_contributif: resultat.totalContributif,
    fiabilite,
    // Comme la pension annuelle : hors capitalisation.
    pension_mensuelle: Math.max(0.0, total - resultat.horsRepartition) / 12.0,
    // Un seul départ : tous les régimes liquident à la même date.
    departs: [],
    // Les pensions dont la carrière dit la date de demande, examinées.
    demandes: [],
    retraite_progressive: null,
    cumul: null,
    droits_apres_depart: null,
  };
}

/**
 * L'état du départ unique : la carrière, et, après une retraite progressive,
 * la pension provisoire de ses régimes de base, menée au départ, que la
 * pension complète garde (`droit/progressive.js`).
 */
export function etatDuDepart(moteur, carriere, plancher, journal = null) {
  if (plancher === null) {
    return new liquidation.Etat(carriere, journal);
  }
  const [progressive, provisoire] = plancher;
  return new liquidation.Etat(carriere, journal, [],
    lesProgressives.initiales(moteur, progressive, provisoire, carriere.dateLiquidation),
    lesProgressives.recalculee(carriere.dateLiquidation));
}

/**
 * La retraite progressive, telle que le résultat la dit, pour un départ à
 * `depart`. Voir le Python.
 */
export function progressiveServie(progressive, provisoire, depart) {
  const provisoireTotal = provisoire !== null ? provisoire.total : 0.0;
  return {
    date_effet: progressive.dateEffet,
    quotite: progressive.quotite,
    motif: progressive.motif,
    fraction: progressive.fraction,
    regimes: [...progressive.regimes].sort(),
    montant_provisoire: provisoireTotal,
    montant_servi: progressive.fraction * provisoireTotal,
    age_minimum: progressive.ageMinimum,
    duree_requise: progressive.dureeRequise,
    trimestres: progressive.trimestres,
    recalculee: lesProgressives.recalculee(depart),
    get ouverte() {
      return this.motif === lesProgressives.OUVERTE;
    },
    donnees() {
      return {
        date_effet: this.date_effet, quotite: this.quotite, motif: this.motif,
        fraction: this.fraction, regimes: [...this.regimes],
        montant_provisoire: this.montant_provisoire, montant_servi: this.montant_servi,
        age_minimum: this.age_minimum, duree_requise: this.duree_requise,
        trimestres: this.trimestres, recalculee: this.recalculee,
      };
    },
  };
}

/**
 * Ce qui mène chaque pension d'un départ aux euros du départ déclaré : la
 * revalorisation de son régime pour une pension déjà servie, les prix pour
 * une pension qui ne commence qu'après.
 */
function ramener(moteur, depart, declare, pensions) {
  if (depart.date.rang === declare.rang) {
    return pensions.map(() => 1.0);
  }
  if (depart.date.rang > declare.rang) {
    const prix = moteur.macro.coefficientPrix(depart.date.annee, declare.annee);
    return pensions.map(() => prix);
  }
  const menes = menerAuMois(moteur, pensions, depart.date, declare);
  return pensions.map((pension, i) => (pension.montant ? menes[i] / pension.montant : 1.0));
}

/** La formule d'une pension datée, et ce qu'elle vaut au départ déclaré. */
function detailDate(detail, depart, declare, montant, ramene) {
  if (depart.date.rang === declare.rang) {
    return detail;
  }
  if (depart.date.rang < declare.rang) {
    return `${detail} ; servie depuis le 1er ${depart.date}, ${formatFixe(montant, 2, true)} € `
      + `à cette date, ${formatFixe(ramene, 2, true)} € au départ`;
  }
  return `${detail} ; servie à partir du 1er ${depart.date}, `
    + `${formatFixe(montant, 2, true)} € de ${depart.date.annee}, `
    + `soit ${formatFixe(ramene, 2, true)} € de ${declare.annee}`;
}

/** Ce qu'un départ ajoute à la pension, dans les deux euros. */
function departServi(depart, resultat, servi) {
  const aLEffet = resultat.regimes.reduce((somme, p) => somme + p.montant, 0.0)
    + resultat.complements.avantages
      .filter((a) => a.code === "majoration_enfants")
      .reduce((somme, a) => somme + a.montant, 0.0);
  const regimes = resultat.regimes.map((p) => p.regime);
  return {
    date_effet: depart.dateEffet, motif: depart.motif, regimes,
    montant: servi, montant_a_l_effet: aLEffet,
    donnees() {
      return { date_effet: this.date_effet, motif: this.motif, regimes: [...this.regimes],
        montant: this.montant, montant_a_l_effet: this.montant_a_l_effet };
    },
  };
}

/**
 * Le scénario 1 d'une carrière dont les régimes liquident à des dates
 * différentes (`droit/departs.js`). LES MONTANTS SONT CEUX DU DÉPART DÉCLARÉ :
 * la pension déjà servie y est menée par la revalorisation de son régime,
 * celle qui ne commence qu'après y est ramenée par les prix ; `departs` dit ce
 * que chaque départ y ajoute, et quand. Voir `resultat_des_departs` dans le
 * Python.
 */
export function resultatDesDeparts(moteur, carriere, departs, liquidations, contexte) {
  const declare = carriere.dateLiquidation;
  const rangPrincipal = departs.findIndex((depart) => depart.date.rang === declare.rang);
  const principale = liquidations[rangPrincipal >= 0 ? rangPrincipal : liquidations.length - 1];
  const isoler = moteur.parametres.isoler_capitalisation;
  const pensions = [];
  const avantages = new Map();
  const servis = [];
  let total = 0.0;
  let horsRepartition = 0.0;
  let totalContributif = 0.0;
  let fiabilite = Fiabilite.CERTIFIEE;
  departs.forEach((depart, rang) => {
    const resultat = liquidations[rang];
    const regimes = [...resultat.regimes];
    const facteurs = ramener(moteur, depart, declare, regimes);
    const parRegime = new Map(regimes.map((p, i) => [p.regime, facteurs[i]]));
    const nues = regimes.reduce((somme, p) => somme + p.montant, 0.0);
    const moyen = nues
      ? regimes.reduce((somme, p, i) => somme + p.montant * facteurs[i], 0.0) / nues
      : (facteurs.length > 0 ? facteurs[0] : 1.0);
    let servi = 0.0;
    regimes.forEach((pension, i) => {
      const ramene = pension.montant * facteurs[i];
      servi += ramene;
      pensions.push({
        ...pension, montant: ramene, date_effet: depart.dateEffet,
        montant_a_l_effet: pension.montant,
        detail: detailDate(pension.detail, depart, declare, pension.montant, ramene),
      });
      if (isoler && moteur.catalogue.obtenir(pension.regime).hors_repartition) {
        horsRepartition += ramene;
      }
    });
    let majoration = 0.0;
    for (const avantage of resultat.avantages) {
      const parts = (avantage.par_regime ?? []).map(
        ([code, part]) => [code, part * (parRegime.has(code) ? parRegime.get(code) : moyen)]);
      const montant = parts.length > 0
        ? parts.reduce((somme, [, part]) => somme + part, 0.0)
        : avantage.montant * moyen;
      if (avantage.code === "majoration_enfants") {
        majoration += montant;
      }
      const deja = avantages.get(avantage.code);
      if (deja === undefined) {
        avantages.set(avantage.code, { ...avantage, montant, par_regime: parts });
      } else {
        const details = [...new Set([deja.detail, avantage.detail].filter((d) => d))];
        avantages.set(avantage.code, {
          ...deja, montant: deja.montant + montant, detail: details.join(" ; "),
          par_regime: [...deja.par_regime, ...parts],
        });
      }
    }
    servi += majoration;
    total += servi;
    totalContributif += resultat.totalContributif * moyen;
    fiabilite = Math.min(fiabilite, resultat.fiabilite);
    servis.push(departServi(depart, resultat, servi));
  });
  const foyer = foyerEtNet(
    moteur, carriere.personne, new lesDeparts.Depart(declare).dateEffet, declare.annee,
    total, (carriere.age_liquidation || 0.0) >= ageDeLAspa(moteur, carriere), contexte);
  const liste = [...avantages.values()];
  if (foyer.minimumVieillesse > 0) {
    total = foyer.plafond;
    fiabilite = Math.min(fiabilite, foyer.fiabilite);
    liste.push(foyer.avantage());
  }
  return {
    pension_annuelle: Math.max(0.0, total - horsRepartition),
    pension_hors_repartition: horsRepartition,
    pensions_par_regime: pensions,
    trimestres_valides: principale.releve.durees.trimestres,
    trimestres_requis: principale.pensions.requis,
    taux_liquidation: principale.pensions.taux,
    minimum_applique: liquidations.some((l) => l.complements.minimumApplique),
    age_ouverture_opposable: principale.ouverture.age,
    liquidation_ouverte: liquidations.every((l) => l.ouverture.ouverte),
    motif_ouverture: principale.ouverture.motif,
    avantages_appliques: liste,
    total_contributif: totalContributif,
    fiabilite,
    pension_mensuelle: Math.max(0.0, total - horsRepartition) / 12.0,
    departs: servis,
    demandes: [],
    retraite_progressive: null,
    cumul: null,
    droits_apres_depart: null,
  };
}
