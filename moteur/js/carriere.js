/**
 * Description d'une carrière individuelle.
 *
 * Portage de ``src/retraite_notionnelle/carriere.py``. Deux niveaux d'entrée :
 * une ligne par année, telle qu'on la lit sur un relevé de carrière
 * ({@link Carriere.depuisReleve} — le chemin le plus exact, le seul qui ne
 * suppose ni profil ni progression), ou la suite des métiers exercés — statut,
 * âge de début et niveau de rémunération pour chacun. Une carrière d'un seul
 * métier en est le cas particulier.
 */

import {
  MOIS_PAR_AN,
  DateMois,
  enMois,
  fractionAnnee,
  moisTravailles,
  trimestresCivils,
} from "./calendrier.js";

/**
 * Périodes non cotisées reconnues par le système actuel. Elles ouvrent des
 * droits gratuits aujourd'hui ; elles n'en ouvrent aucun dans les scénarios
 * notionnels, sauf si des cotisations ont réellement été versées.
 */
export const PERIODES_NON_COTISEES = new Set([
  "chomage_indemnise",
  "chomage_non_indemnise",
  "maladie",
  "invalidite",
  "maternite",
  "education_enfant",
  "service_militaire",
  "inactivite",
  "etudes",
]);

/** Une année de carrière. */
export class AnneeCarriere {
  constructor({
    annee,
    //: Revenu d'activité brut, EN EUROS COURANTS DE CETTE ANNÉE-LÀ.
    revenu,
    affiliation,
    type_periode = "emploi",
    quotite = 1.0,
    //: Trimestres validés au sens du système ACTUEL.
    trimestres_valides = 4,
    //: Salaire d'avant l'interruption, sur lequel les complémentaires
    //: attribuent des points pendant une période indemnisée.
    revenu_reference = 0.0,
    //: Familles qui attribuent ces points : ce que le scénario 1 sert.
    familles_cotisantes = [],
    //: Celles d'entre elles qui ENCAISSENT de vraies cotisations, versées par
    //: un tiers — l'Unédic pendant un chômage indemnisé. C'est ce que le
    //: compte notionnel porte ; les points gratuits de la maladie n'y entrent
    //: pas. Voir carriere.py.
    familles_financees = [],
    //: Des cotisations retraite ont-elles réellement été versées ? C'est le
    //: seul critère qui compte pour les comptes notionnels.
    cotisations_versees = true,
    //: Part de primes dans le revenu (fonction publique) : assiette du RAFP.
    part_primes = 0.0,
    //: Salaire forfaitaire porté au compte du régime de base au titre de
    //: l'assurance vieillesse des parents au foyer. Ce n'est pas un revenu
    //: d'activité — l'année n'est pas cotisée par l'assuré — mais la CNAF
    //: cotise pour lui sur cette assiette, et le salaire entre dans le salaire
    //: annuel moyen. Une période assimilée, elle, n'y entre jamais.
    revenu_avpf = 0.0,
    //: Part de l'année civile réellement couverte par la carrière. Vaut un
    //: partout, sauf aux deux bords : l'année d'entrée dans la vie active et
    //: celle de la liquidation sont incomplètes, et ``revenu`` ne porte alors
    //: que ce qui a été perçu pendant ces mois-là.
    fraction_annee = 1.0,
    //: Cette année entre-t-elle dans les SERVICES d'un régime de la fonction
    //: publique ? Ce régime-là ne proratise pas sur la durée d'assurance mais
    //: sur les services et bonifications (L. 13 du code des pensions), et
    //: l'article L. 9 écarte le temps passé dans une position statutaire sans
    //: services effectifs, hors la liste qu'il énumère. Une année d'emploi en
    //: est toujours ; une année de chômage n'en est jamais.
    services_fonction_publique = true,
    //: Limite, en trimestres PAR ENFANT, des services que cette année ouvre.
    //: Zéro quand il n'y en a pas — le décompte se fait sur toute la carrière,
    //: et c'est le scénario qui tient le budget.
    services_plafond_trimestres_par_enfant = 0,
    //: Enveloppe de l'article D. 351-1-2 sous laquelle cette année est RÉPUTÉE
    //: COTISÉE pour la carrière longue, et plafond de cette enveloppe sur toute
    //: la carrière. Enveloppe vide : jamais réputée cotisée. Plafond nul :
    //: réputée cotisée sans limite, ce qui n'est vrai que de la maternité.
    reputes_cotises_enveloppe = "",
    reputes_cotises_plafond = 0,
    //: ASSIETTE MINIMALE du régime de base d'un indépendant (D. 633-2,
    //: D. 642-4), en euros de l'année ; nulle pour tout autre statut.
    assiette_minimale_base = 0.0,
  }) {
    Object.assign(this, {
      annee, revenu, affiliation, type_periode, quotite,
      trimestres_valides, cotisations_versees, part_primes,
      revenu_reference, familles_cotisantes, familles_financees, revenu_avpf,
      fraction_annee,
      services_fonction_publique, services_plafond_trimestres_par_enfant,
      reputes_cotises_enveloppe, reputes_cotises_plafond,
      assiette_minimale_base,
    });
  }

  get cotise() {
    return this.cotisations_versees && this.revenu > 0;
  }

  /**
   * Revenu ramené à l'année pleine — le traitement EN VIGUEUR, celui que
   * liquident les régimes servant sur les six derniers mois de service.
   */
  get revenuAnnualise() {
    return this.fraction_annee <= 0 ? 0.0 : this.revenu / this.fraction_annee;
  }
}

/**
 * Une année de carrière, une fois connus son revenu et sa nature.
 *
 * Les deux constructeurs de {@link Carriere} y passent : celui qui déduit le
 * revenu d'un profil ({@link Carriere.depuisParcours}) et celui qui le lit sur
 * un relevé ({@link Carriere.depuisReleve}). Ce que le droit fait d'une période
 * non cotisée — combien de trimestres elle assimile, si elle ouvre des points
 * complémentaires, si la CNAF cotise l'AVPF — ne s'écrit donc qu'une fois.
 *
 * `trimestresDeclares` est le seul point où les deux chemins se séparent : un
 * relevé dit combien de trimestres l'année a validés, et ce chiffre-là fait
 * foi ; une carrière paramétrique les déduit du montant cotisé.
 */
/**
 * La règle d'assiette minimale que ce statut subit cette année-là, lue dans
 * `legislation/assiette_minimale_independants.csv`, ou `null`.
 */
export function assietteMinimale(paquet, statut, annee) {
  for (const regle of paquet.assiette_minimale_independants ?? []) {
    const [statuts, , debut, fin] = regle;
    if (statuts.includes(statut) && debut <= annee && (fin === null || annee <= fin)) {
      return regle;
    }
  }
  return null;
}

/** Le montant de cette règle pour une année couverte à `part`. */
function montantAssietteMinimale(regle, pass, smicHoraire, part) {
  const [, , , , heuresSmic, partPass, proratise, joursMinimum] = regle;
  if (part * 365 + 1e-6 < joursMinimum) {
    return 0.0;
  }
  const montant = heuresSmic !== null ? heuresSmic * smicHoraire : (partPass ?? 0.0) * pass;
  return proratise ? montant * part : montant;
}

/**
 * Article R. 351-12, 4°, d : le chômage NON indemnisé ne valide rien avant
 * 1980, et dans des limites ensuite ; la limite de la première période est
 * choisie par l'année de la PÉRIODE (décret n° 2011-934, article 2). Portage
 * de `CHOMAGE_NON_INDEMNISE_PREMIERE` et `CHOMAGE_NON_INDEMNISE_ULTERIEURE`
 * de `carriere.py`, qui citent le texte.
 */
const CHOMAGE_NON_INDEMNISE_PREMIERE = {
  valideDepuis: 1980, trimestres: 6, trimestresAvant: 4, periodesDepuis: 2011,
};
const CHOMAGE_NON_INDEMNISE_ULTERIEURE = {
  trimestres: 4, trimestresSenior: 20, ageSenior: 55, cotisesSenior: 80,
};

/**
 * Les trimestres que le chômage non indemnisé valide VRAIMENT — portage de
 * `limiter_chomage_non_indemnise` : rien avant 1980, la première période
 * prend l'enveloppe de la première période (quatre trimestres pour une année
 * d'avant 2011, six depuis), une série qui suit un chômage indemnisé en prend
 * quatre (vingt pour le senior qui ne retravaille pas), les années dont un
 * relevé porte les trimestres sont laissées telles quelles.
 */
export function limiterChomageNonIndemnise(lignes, anneeNaissance,
  declarees = new Set()) {
  const premiere = CHOMAGE_NON_INDEMNISE_PREMIERE;
  const ulterieure = CHOMAGE_NON_INDEMNISE_ULTERIEURE;
  const ordre = lignes.map((_, i) => i).sort((a, b) => lignes[a].annee - lignes[b].annee);
  const resultat = lignes.slice();
  let cotises = 0;
  let precedente = null;
  let premiereVue = false;
  let prisPremiere = 0;
  let resteSerie = 0;
  let seriePremiere = true;
  ordre.forEach((indice, rang) => {
    const ligne = lignes[indice];
    if (ligne.type_periode !== "chomage_non_indemnise" || declarees.has(ligne.annee)) {
      if (ligne.cotisations_versees) {
        cotises += ligne.trimestres_valides;
      }
      precedente = ligne;
      return;
    }
    const debutSerie = precedente === null
      || precedente.type_periode !== "chomage_non_indemnise"
      || precedente.annee !== ligne.annee - 1;
    if (debutSerie) {
      const suitIndemnise = precedente !== null
        && precedente.type_periode === "chomage_indemnise"
        && precedente.annee === ligne.annee - 1;
      seriePremiere = !premiereVue || !suitIndemnise;
      if (!seriePremiere) {
        const retravaille = ordre.slice(rang + 1)
          .some((j) => lignes[j].cotisations_versees);
        const senior = ligne.annee - anneeNaissance >= ulterieure.ageSenior
          && cotises >= ulterieure.cotisesSenior && !retravaille;
        resteSerie = senior ? ulterieure.trimestresSenior : ulterieure.trimestres;
      }
    }
    let accordes;
    if (ligne.annee < premiere.valideDepuis) {
      accordes = 0;
    } else if (seriePremiere) {
      premiereVue = true;
      const plafond = ligne.annee >= premiere.periodesDepuis
        ? premiere.trimestres : premiere.trimestresAvant;
      accordes = Math.min(ligne.trimestres_valides, Math.max(0, plafond - prisPremiere));
      prisPremiere += accordes;
    } else {
      accordes = Math.min(ligne.trimestres_valides, resteSerie);
      resteSerie -= accordes;
    }
    if (accordes !== ligne.trimestres_valides) {
      resultat[indice] = new AnneeCarriere({ ...ligne, trimestres_valides: accordes });
    }
    precedente = ligne;
  });
  return resultat;
}

function ligneAnnuelle({
  annee,
  revenu,
  affiliation,
  type_periode: typePeriode,
  macro,
  part,
  part_primes: partPrimes,
  trimestresMaximum,
  trimestresDeclares = null,
}) {
  const cotise = typePeriode === "emploi";
  const motifs = macro.paquet.periodes_non_travaillees ?? {};
  const regle = cotise ? null : (motifs[typePeriode] ?? motifs.sans_activite ?? null);
  const ouvreComplementaires = regle !== null && regle[1] === true;
  // Ces points sont-ils PAYÉS ? Par l'Unédic pour le chômage ; la maladie les
  // reçoit sans contrepartie de cotisations.
  const complementairesVersees = ouvreComplementaires && regle[8] === true;
  const ouvreAvpf = regle !== null && regle[3] === true;
  // Services et durée d'assurance ne sont pas la même case : la première
  // proratise la pension de la fonction publique, la seconde celle du régime
  // général. Une année de chômage indemnisé en valide quatre trimestres à la
  // CNAV et aucun service à l'État.
  const ouvreServices = cotise || regle === null || regle[4] === true;
  const plafondServices = (cotise || regle === null) ? 0 : regle[5];
  // La carrière longue compte la durée COTISÉE, que D. 351-1-2 complète d'une
  // liste fermée de périodes qu'il répute telles, chacune sous sa limite.
  const enveloppeReputes = (cotise || regle === null) ? "" : regle[6];
  const plafondReputes = (cotise || regle === null) ? 0 : regle[7];
  // L'ASSIETTE MINIMALE DES INDÉPENDANTS : un artisan qui déclare 3 000 €
  // cotise en 2026 sur 450 SMIC horaires et valide trois trimestres au lieu
  // d'un. Le revenu de la ligne reste celui qu'il a déclaré.
  let minimale = 0.0;
  if (cotise && revenu > 0) {
    const regleMinimale = assietteMinimale(macro.paquet, affiliation, annee);
    if (regleMinimale !== null) {
      minimale = montantAssietteMinimale(regleMinimale,
        macro.plafond_securite_sociale.valeur(annee),
        macro.smic_horaire.valeur(annee), part);
    }
  }
  const trimestres = trimestresDeclares === null
    ? (cotise ? macro.trimestresValides(Math.max(revenu, minimale), annee)
      : (regle !== null ? regle[0] : 4))
    : trimestresDeclares;
  return new AnneeCarriere({
    annee,
    revenu: cotise ? revenu : 0.0,
    affiliation,
    type_periode: typePeriode,
    // Un trimestre s'acquiert par un montant cotisé — 150 fois le SMIC horaire
    // depuis 2014, 200 avant. Les périodes assimilées en valident quatre sans
    // condition de montant : c'est tout leur objet.
    // Le montant commande le nombre de trimestres, les mois en commandent le
    // plafond : on ne valide pas quatre trimestres en sept mois, si gros que
    // soit le salaire.
    trimestres_valides: Math.min(trimestresMaximum, trimestres),
    assiette_minimale_base: minimale,
    // Pendant une période indemnisée, les régimes complémentaires attribuent
    // des points sur le salaire d'avant. L'Unédic les paie pour le chômage ;
    // l'Agirc-Arrco les donne pour la maladie, sans contrepartie.
    revenu_reference: ouvreComplementaires ? revenu : 0.0,
    familles_cotisantes: ouvreComplementaires ? ["complementaire_prive"] : [],
    familles_financees: complementairesVersees ? ["complementaire_prive"] : [],
    cotisations_versees: cotise,
    fraction_annee: part,
    part_primes: partPrimes,
    // Assurance vieillesse des parents au foyer : la CNAF cotise au régime
    // général sur une assiette forfaitaire égale au SMIC — 1 820 heures, soit
    // le SMIC mensuel multiplié par douze.
    revenu_avpf: (!cotise && ouvreAvpf)
      ? 1820.0 * macro.smic_horaire.valeur(annee) * part
      : 0.0,
    services_fonction_publique: ouvreServices,
    services_plafond_trimestres_par_enfant: plafondServices,
    reputes_cotises_enveloppe: enveloppeReputes,
    reputes_cotises_plafond: plafondReputes,
  });
}

/**
 * Carrière complète d'un assuré.
 *
 * **Une ligne par année ET PAR ACTIVITÉ.** Une année ne porte d'ordinaire
 * qu'une ligne ; celle où l'assuré a exercé deux activités à la fois en porte
 * une par statut, et deux lignes de la même année ne partagent jamais leur
 * statut. La première ligne d'une année est l'activité PRINCIPALE, et c'est
 * elle que {@link ligne} rend. Ce que le droit compte TOUS RÉGIMES ne dépasse
 * jamais quatre trimestres par année civile : {@link trimestresCumules}.
 * Portage de `carriere.py`, qui porte les sources.
 */
export class Carriere {
  constructor({
    annee_naissance,
    sexe,
    lignes = [],
    //: Mois de naissance, 1 à 12. Le droit coupe deux générations en cours
    //: d'année — au 1er juillet 1951 et au 1er septembre 1961 — et l'âge à la
    //: liquidation ne se lit qu'à partir de lui.
    mois_naissance = 1,
    //: Âge de liquidation effectif (réel pour un retraité, souhaité sinon).
    age_liquidation = null,
    //: Sans effet notionnel : utilisé par le seul scénario « système actuel ».
    nombre_enfants = 0,
    identifiant = "assuré",
    dates_entree = {},
  }) {
    if (sexe !== "H" && sexe !== "F") {
      throw new Error(`sexe attendu 'H' ou 'F', reçu ${sexe}`);
    }
    if (!(mois_naissance >= 1 && mois_naissance <= 12)) {
      throw new Error(
        `mois de naissance attendu entre 1 et 12, reçu ${mois_naissance}`,
      );
    }
    this.mois_naissance = mois_naissance;
    this.annee_naissance = annee_naissance;
    this.sexe = sexe;
    this.lignes = [...lignes].sort((a, b) => a.annee - b.annee);
    this.age_liquidation = age_liquidation;
    this.nombre_enfants = nombre_enfants;
    this.identifiant = identifiant;
    // Mois d'entrée dans chaque statut, tel que le parcours le date. Les
    // lignes ne connaissent que l'année, et l'année d'un changement de métier
    // revient au métier qui en occupe le plus de mois : l'agent recruté à la
    // RATP en octobre 2022 n'y a sa première LIGNE qu'en 2023, quand le régime
    // est fermé aux recrutés depuis septembre 2023. C'est la date qui décide
    // de la clause du grand-père, pas la première ligne.
    this.dates_entree = dates_entree;
    // Tri STABLE : l'activité principale, donnée la première, reste en tête.
    this._parAnnee = new Map();
    const vues = new Set();
    for (const ligne of this.lignes) {
      const cle = `${ligne.annee}:${ligne.affiliation}`;
      if (vues.has(cle)) {
        throw new Error(
          `${identifiant} : deux lignes de ${ligne.annee} sous le même statut `
          + `'${ligne.affiliation}' — deux emplois du même statut font une `
          + "seule ligne, dont le revenu est la somme",
        );
      }
      vues.add(cle);
      if (!this._parAnnee.has(ligne.annee)) {
        this._parAnnee.set(ligne.annee, []);
      }
      this._parAnnee.get(ligne.annee).push(ligne);
    }
    this._plafonds = null;
  }

  // -- dates -----------------------------------------------------------------

  get premiereAnnee() {
    return Math.min(...this.lignes.map((ligne) => ligne.annee));
  }

  get derniereAnnee() {
    return Math.max(...this.lignes.map((ligne) => ligne.annee));
  }

  get dateNaissance() {
    return new DateMois(this.annee_naissance, this.mois_naissance);
  }

  /**
   * Génération, mois compris — la clé des tables par génération. Deux textes
   * ne coupent pas au 1er janvier : la loi du 9 novembre 2010 vise les assurés
   * nés à compter du 1er juillet 1951, celle du 14 avril 2023 ceux nés à
   * compter du 1er septembre 1961.
   *
   * L'ARRONDI À TROIS DÉCIMALES N'EST PAS COSMÉTIQUE : les tables écrivent le
   * 1er septembre `1961.667`, quand huit douzièmes valent 1961,666 666… Sans
   * lui, la lecture en escalier rendait à l'assuré né en septembre 1961 la
   * marche d'août — 168 trimestres au lieu de 169, et 62 ans au lieu de 62 ans
   * et trois mois, pour le mois-même que la loi du 14 avril 2023 désigne.
   */
  get generation() {
    return Math.round(
      (this.annee_naissance + (this.mois_naissance - 1) / 12) * 1000) / 1000;
  }

  /**
   * Mois où la pension prend effet.
   *
   * L'âge de liquidation est compté en mois depuis la date de naissance : né
   * en mars 1962, parti à soixante-quatre ans et six mois, l'assuré liquide en
   * septembre 2026. Le modèle arrondissait auparavant à l'année la plus
   * proche, et l'arrondi au pair déplaçait la liquidation selon la parité du
   * millésime.
   */
  get dateLiquidation() {
    if (this.age_liquidation === null) {
      throw new Error(`${this.identifiant} : âge de liquidation non renseigné`);
    }
    return this.dateNaissance.plusMois(enMois(this.age_liquidation));
  }

  get anneeLiquidation() {
    return this.dateLiquidation.annee;
  }

  get moisLiquidation() {
    return this.dateLiquidation.mois;
  }

  /** Part de l'année de liquidation qui précède le point de départ. */
  get fractionAnneeLiquidation() {
    return (this.moisLiquidation - 1) / 12;
  }

  // -- prolongation ----------------------------------------------------------

  /**
   * La même carrière, poursuivie jusqu'à un départ à `ageLiquidation`.
   *
   * C'est ce que fait l'âge légal de la proposition à qui serait parti plus
   * tôt sous le droit en vigueur : il travaille jusqu'à l'âge légal. Rien de
   * ce qui précède ne bouge. LA CONVENTION, ET IL N'Y EN A QU'UNE : la
   * dernière année se prolonge — même statut, même nature de période, même
   * salaire RELATIF, avancé chaque année au rythme du salaire moyen —, TOUTE
   * la dernière année : l'activité principale et chaque activité cumulée qui
   * court encore au départ, à son propre revenu. Une activité cumulée qui
   * s'arrête dans la dernière année, avant le départ, ne se prolonge pas. Une
   * carrière qui s'arrêtait avant son départ finissait sans activité, et le
   * report n'ajoute alors aucune ligne. Rend la carrière elle-même quand le
   * départ demandé ne tombe pas après le sien. `attenteTravaillee = false`
   * fait l'autre hypothèse : l'attente se passe sans activité, aucune ligne
   * ne s'ajoute. Voir `carriere.py`.
   */
  prolongee(ageLiquidation, macro, attenteTravaillee = true) {
    if (this.age_liquidation === null
        || enMois(ageLiquidation) <= enMois(this.age_liquidation)) {
      return this;
    }
    if (!attenteTravaillee) {
      return new Carriere({
        annee_naissance: this.annee_naissance,
        sexe: this.sexe,
        lignes: [...this.lignes],
        mois_naissance: this.mois_naissance,
        age_liquidation: ageLiquidation,
        nombre_enfants: this.nombre_enfants,
        identifiant: this.identifiant,
        dates_entree: { ...this.dates_entree },
      });
    }
    const initiale = this.dateLiquidation;
    const fin = this.dateNaissance.plusMois(enMois(ageLiquidation));
    const derniereAnnee = this.lignes[this.lignes.length - 1].annee;
    const finales = this.lignesDe(derniereAnnee);
    const principale = finales[0];
    const veille = new Set(this.lignesDe(derniereAnnee - 1).map((l) => l.affiliation));
    // L'activité de cette ligne court-elle encore au départ initial ?
    const poursuivie = (ligne) => ligne === principale
      || Math.round(ligne.fraction_annee * MOIS_PAR_AN)
        >= Math.round(principale.fraction_annee * MOIS_PAR_AN)
      || !veille.has(ligne.affiliation);
    const reference = salaireMoyenAnnuel(macro, derniereAnnee);

    // `source` poursuivie `mois` mois de `annee`.
    const ligne = (source, annee, mois) => {
      // Le revenu annualisé de la ligne : ce qui a été perçu pour une année
      // d'emploi, le salaire de référence pour une interruption.
      const percu = source.type_periode === "emploi"
        ? source.revenu : source.revenu_reference;
      const base = source.fraction_annee > 0 ? percu / source.fraction_annee : 0.0;
      const facteur = reference > 0
        ? salaireMoyenAnnuel(macro, annee) / reference : 1.0;
      return ligneAnnuelle({
        annee,
        revenu: base * facteur * mois / MOIS_PAR_AN,
        affiliation: source.affiliation,
        type_periode: source.type_periode,
        macro,
        part: mois / MOIS_PAR_AN,
        part_primes: source.part_primes,
        trimestresMaximum: trimestresCivils(mois),
      });
    };
    // Le mois de liquidation n'est pas travaillé.
    const finTravaillee = (annee, depart) => {
      if (annee < depart.annee) return MOIS_PAR_AN;
      if (annee === depart.annee) return depart.mois - 1;
      return 0;
    };

    const contigue = derniereAnnee === initiale.annee
      || (derniereAnnee === initiale.annee - 1 && initiale.mois === 1);
    const lignes = [...this.lignes];
    if (contigue) {
      const sources = finales.filter(poursuivie);
      const ajoutes = finTravaillee(derniereAnnee, fin)
        - finTravaillee(derniereAnnee, initiale);
      if (ajoutes > 0) {
        for (const source of sources) {
          const mois = Math.round(source.fraction_annee * MOIS_PAR_AN) + ajoutes;
          lignes[lignes.indexOf(source)] = ligne(
            source, derniereAnnee, Math.min(mois, MOIS_PAR_AN));
        }
      }
      // L'activité principale en tête de chaque année, les cumulées ensuite.
      for (let annee = derniereAnnee + 1; annee <= fin.annee; annee += 1) {
        const mois = finTravaillee(annee, fin);
        if (mois > 0) {
          for (const source of sources) lignes.push(ligne(source, annee, mois));
        }
      }
    }
    return new Carriere({
      annee_naissance: this.annee_naissance,
      sexe: this.sexe,
      lignes,
      mois_naissance: this.mois_naissance,
      age_liquidation: ageLiquidation,
      nombre_enfants: this.nombre_enfants,
      identifiant: this.identifiant,
      dates_entree: { ...this.dates_entree },
    });
  }

  // -- agrégats --------------------------------------------------------------

  /** Année d'entrée dans ce statut, ou null s'il ne figure pas dans la carrière.
   *
   * C'est elle qui décide de la CLAUSE DU GRAND-PÈRE : un régime fermé aux
   * nouveaux entrants reste celui de qui était déjà là. Les lignes étant
   * chronologiques, la première rencontre suffit.
   */
  entree(affiliation) {
    for (const ligne of this.lignes) {
      if (ligne.affiliation === affiliation) {
        return ligne.annee;
      }
    }
    return null;
  }

  /**
   * Mois d'entrée dans ce statut, ou null s'il n'y figure pas : celui que le
   * parcours a daté quand il en vient ; sinon janvier de la première ligne,
   * ce qui vaut pour une carrière construite ligne à ligne.
   */
  dateEntree(affiliation) {
    if (Object.prototype.hasOwnProperty.call(this.dates_entree, affiliation)) {
      return this.dates_entree[affiliation];
    }
    const annee = this.entree(affiliation);
    return annee === null ? null : new DateMois(annee, 1);
  }

  get anneesCotisees() {
    // Une année de deux activités reste UNE année cotisée.
    return [...new Set(
      this.lignes.filter((ligne) => ligne.cotise).map((ligne) => ligne.annee),
    )];
  }

  /**
   * Les années effectivement servies dans l'un de ces statuts.
   *
   * « Services effectifs » au sens du code des pensions : les années
   * travaillées, non les années validées. Une interruption ne sert pas, et
   * `cotise` la range déjà du bon côté.
   */
  _lignesDeService(affiliations, jusquA = null) {
    const codes = new Set(affiliations);
    // Une année ne sert qu'une fois, quand deux statuts de la liste s'y
    // cumulent : on garde celui qui en couvre le plus.
    const parAnnee = new Map();
    for (const ligne of this.lignes) {
      if (codes.has(ligne.affiliation) && ligne.cotise
          && (jusquA === null || ligne.annee <= jusquA)) {
        const retenue = parAnnee.get(ligne.annee);
        if (retenue === undefined || ligne.fraction_annee > retenue.fraction_annee) {
          parAnnee.set(ligne.annee, ligne);
        }
      }
    }
    return [...parAnnee.keys()].sort((a, b) => a - b).map((a) => parAnnee.get(a));
  }

  /**
   * Années de service accomplies dans ces statuts, bornes comprises.
   *
   * C'est la grandeur que le code des pensions oppose deux fois : dix-sept ans
   * de services ACTIFS pour ouvrir l'âge anticipé de la catégorie active
   * (L. 24, I, 1°), dix-sept ou vingt-sept ans de services EFFECTIFS pour
   * ouvrir la pension militaire (L. 24, II).
   */
  dureeDeService(affiliations, jusquA = null) {
    return this._lignesDeService(affiliations, jusquA).reduce(
      (total, ligne) => total + ligne.fraction_annee,
      0,
    );
  }

  /**
   * Première et dernière années servies dans ces statuts, null sans aucune.
   *
   * Le recrutement et la radiation, à l'année près : ce sont eux que les règles
   * des enfants opposent — une majoration « aux femmes ayant accouché
   * postérieurement à leur recrutement », une bonification pour les enfants nés
   * avant la radiation.
   *
   * @returns {[number, number]|null}
   */
  bornesDeService(affiliations, jusquA = null) {
    const lignes = this._lignesDeService(affiliations, jusquA);
    if (lignes.length === 0) {
      return null;
    }
    return [lignes[0].annee, lignes[lignes.length - 1].annee];
  }

  /**
   * Mois où la durée de service demandée est atteinte, null sinon.
   *
   * CONVENTION DE PLACEMENT DANS L'ANNÉE : une année pleine sert de janvier à
   * décembre ; une année tronquée sert à partir de son mois d'entrée quand elle
   * ouvre le statut, et à partir de janvier sinon — l'année de liquidation
   * étant tronquée par la fin.
   */
  dateDeService(affiliations, annees) {
    if (annees <= 0) {
      return null;
    }
    const lignes = this._lignesDeService(affiliations);
    if (lignes.length === 0) {
      return null;
    }
    const premiere = lignes[0].annee;
    let cumul = 0;
    for (const ligne of lignes) {
      const moisServis = Math.round(ligne.fraction_annee * MOIS_PAR_AN);
      if (moisServis <= 0) {
        continue;
      }
      let debut = 1;
      if (ligne.annee === premiere && moisServis < MOIS_PAR_AN) {
        const entree = this.dateEntree(ligne.affiliation);
        debut = entree !== null && entree.annee === ligne.annee
          ? entree.mois
          : MOIS_PAR_AN - moisServis + 1;
      }
      if (cumul + ligne.fraction_annee >= annees - 1e-9) {
        const manque = Math.max(1, enMois(annees - cumul));
        return new DateMois(ligne.annee, 1).plusMois(debut - 1 + manque - 1);
      }
      cumul += ligne.fraction_annee;
    }
    return null;
  }

  /** Âge auquel la durée de service demandée est atteinte. */
  ageDeService(affiliations, annees) {
    const date = this.dateDeService(affiliations, annees);
    return date === null
      ? null
      : (date.rang - this.dateNaissance.rang) / MOIS_PAR_AN;
  }

  /**
   * Trimestres validés au sens du droit en vigueur, tous régimes.
   *
   * Bornés à l'année de liquidation : une ligne postérieure décrit une activité
   * exercée APRÈS le départ, et le droit ne la fait pas entrer dans la durée
   * d'assurance qui commande la décote.
   */
  get trimestresActuels() {
    return this.trimestresCumules(this.lignes);
  }

  /**
   * Trimestres que ces lignes font entrer dans une durée, année par année :
   * quatre au plus par année civile, quel que soit le nombre d'activités
   * (R. 351-5, et le 2° de R. 173-4-4-1 pour les régimes alignés). Une année
   * d'une seule ligne n'est pas touchée.
   */
  trimestresParAnnee(lignes) {
    const sommes = new Map();
    for (const ligne of lignes) {
      const retenus = this.trimestresRetenus(ligne);
      if (retenus > 0) {
        sommes.set(ligne.annee, (sommes.get(ligne.annee) ?? 0) + retenus);
      }
    }
    const resultat = new Map();
    for (const [annee, somme] of sommes) {
      resultat.set(annee, Math.min(somme, this.plafondTrimestres(annee)));
    }
    return resultat;
  }

  /** Somme de {@link trimestresParAnnee} : une durée, tous régimes. */
  trimestresCumules(lignes) {
    let total = 0;
    for (const trimestres of this.trimestresParAnnee(lignes).values()) {
      total += trimestres;
    }
    return total;
  }

  /**
   * Trimestres civils que cette année peut valider, toutes activités
   * confondues : ceux de l'activité qui en couvre le plus. Quatre pour une
   * année pleine.
   */
  plafondTrimestres(annee) {
    if (this._plafonds === null) {
      this._plafonds = new Map();
      for (const ligne of this.lignes) {
        const part = this.partRetenueLigne(ligne);
        this._plafonds.set(ligne.annee, Math.max(
          this._plafonds.get(ligne.annee) ?? 0,
          part > 0 ? trimestresCivils(Math.round(part * 12)) : 0,
        ));
      }
    }
    return this._plafonds.get(annee) ?? 4;
  }

  /** Toutes les lignes d'une année, l'activité principale en tête. */
  lignesDe(annee) {
    return this._parAnnee.get(annee) ?? [];
  }

  /**
   * Part de l'année civile qui compte, une fois le départ pris en compte.
   *
   * Une ligne de carrière dit ce qui a été perçu dans l'année ; la date de
   * liquidation dit jusqu'où l'année compte. Les deux se rencontrent l'année
   * du départ, et c'est la plus courte qui l'emporte.
   */
  partRetenue(annee) {
    const ligne = this.ligne(annee);
    if (ligne === null) {
      return 0.0;
    }
    return this.partRetenueLigne(ligne);
  }

  /**
   * {@link partRetenue} d'une ligne précise : deux activités de la même année
   * n'en couvrent pas forcément les mêmes mois.
   */
  partRetenueLigne(ligne) {
    const annee = ligne.annee;
    if (this.age_liquidation === null || this.age_liquidation === undefined) {
      return ligne.fraction_annee;
    }
    const liquidation = this.anneeLiquidation;
    if (annee > liquidation) {
      return 0.0;
    }
    if (annee < liquidation) {
      return ligne.fraction_annee;
    }
    return Math.min(ligne.fraction_annee, this.fractionAnneeLiquidation);
  }

  /**
   * Trimestres qu'une ligne fait entrer dans la durée d'assurance, plafonnés
   * par les trimestres CIVILS écoulés avant le point de départ.
   */
  trimestresRetenus(ligne) {
    const part = this.partRetenueLigne(ligne);
    if (part <= 0) {
      return 0;
    }
    return Math.min(ligne.trimestres_valides,
                    trimestresCivils(Math.round(part * 12)));
  }

  /**
   * La ligne de l'activité PRINCIPALE de l'année, null s'il n'y en a pas. Les
   * activités cumulées se lisent par {@link lignesDe}.
   */
  ligne(annee) {
    const lignes = this._parAnnee.get(annee);
    return lignes ? lignes[0] : null;
  }

  affiliationsUtilisees() {
    return [...new Set(this.lignes.map((ligne) => ligne.affiliation))];
  }

  // -- constructeurs ---------------------------------------------------------

  /**
   * Construit une carrière à partir d'un relevé, ligne par ligne.
   *
   * C'est le chemin le plus exact, et le seul qui ne suppose rien : les deux
   * autres reconstituent un revenu à partir d'un niveau relatif et d'un profil
   * de progression, celui-ci le lit. Une ligne — `{ annee, affiliation,
   * revenu, trimestres, type_periode }` — par année civile, l'unité à laquelle
   * les régimes liquident.
   *
   * **Ce qui est lu, et ce qui ne l'est pas.** Le relevé donne l'année ; il ne
   * donne pas le mois. Chaque ligne vaut donc une année civile PLEINE, sauf
   * celle de la liquidation, dont la pension coupe le millésime à une date que
   * le modèle, lui, connaît. L'année d'entrée dans la vie active reste comptée
   * pour une année entière alors qu'elle est presque toujours tronquée : le
   * relevé n'en porte que ce qui a été gagné, et le modèle ne peut pas
   * l'annualiser sans savoir en quel mois elle a commencé.
   *
   * **Les années non cotisées** se déclarent par `type_periode`, ligne par
   * ligne, et non par les plages d'une carrière paramétrique : le relevé porte
   * des années, pas des intervalles. Le revenu d'une telle ligne n'est plus un
   * revenu perçu mais le salaire de référence d'avant l'interruption, celui sur
   * lequel les régimes complémentaires continuent d'acquérir des points.
   */
  static depuisReleve({
    annee_naissance,
    sexe,
    releve,
    age_liquidation,
    macro,
    mois_naissance = 1,
    nombre_enfants = 0,
    part_primes = 0.0,
    identifiant = "assuré",
  }) {
    if (!releve || releve.length === 0) {
      throw new Error("un relevé compte au moins une ligne");
    }
    const dateNaissance = new DateMois(annee_naissance, mois_naissance);
    // La pension prend effet ce mois-là : il n'est plus travaillé.
    const fin = dateNaissance.plusMois(enMois(age_liquidation));

    const lues = releve.map((ligne) => {
      const mois = ligne.annee < fin.annee ? MOIS_PAR_AN : fin.mois - 1;
      if (ligne.annee > fin.annee || mois <= 0) {
        throw new Error(
          `${identifiant} : l'année ${ligne.annee} du relevé est postérieure `
          + `au départ à la retraite (${fin})`,
        );
      }
      return ligneAnnuelle({
        annee: ligne.annee,
        revenu: ligne.revenu,
        affiliation: ligne.affiliation,
        type_periode: ligne.type_periode ?? "emploi",
        macro,
        part: mois / MOIS_PAR_AN,
        part_primes,
        trimestresMaximum: trimestresCivils(mois),
        trimestresDeclares: ligne.trimestres ?? null,
      });
    });
    const lignes = limiterChomageNonIndemnise(
      lues, annee_naissance,
      new Set(releve.filter((l) => l.trimestres !== null && l.trimestres !== undefined)
        .map((l) => l.annee)),
    );

    return new Carriere({
      annee_naissance, sexe, lignes, mois_naissance, age_liquidation,
      nombre_enfants, identifiant,
    });
  }

  /**
   * Carrière d'un seul métier, exercé du premier au dernier jour. C'est le cas
   * particulier de {@link depuisParcours} à un métier, et il se construit par
   * elle : les deux chemins ne peuvent donc pas diverger.
   */
  static depuisProfil({
    affiliation,
    age_debut,
    niveau_salaire = 1.0,
    ...reste
  }) {
    return Carriere.depuisParcours({
      ...reste,
      metiers: [{ affiliation, age_debut, niveau_salaire }],
    });
  }

  /**
   * Construit une carrière à partir de la suite des métiers exercés.
   *
   * Chaque métier — `{ affiliation, age_debut, niveau_salaire }` — court
   * jusqu'au début du suivant ; le dernier jusqu'à la liquidation. On faisait
   * autrefois le même métier toute sa vie, c'est devenu l'exception.
   *
   * ``niveau_salaire`` s'exprime en multiples du salaire moyen par tête de
   * l'année considérée : 1,0 = salaire moyen, 0,6 ≈ niveau du SMIC. Ce choix
   * d'unité évite d'avoir à convertir des francs de 1975 en euros.
   *
   * ``profilCarriere`` décrit la déformation du salaire relatif au cours de la
   * vie active, et il vaut pour la carrière ENTIÈRE, changements de métier
   * compris : le niveau propre à chaque métier s'y superpose, il ne remet pas
   * la progression à zéro. ``interruptions`` associe une année à une période
   * non cotisée.
   *
   * **Une activité CUMULÉE ne remplace pas, elle s'ajoute** : un métier qui
   * porte `cumul: true` court de `age_debut` à `age_fin` (ou jusqu'à la
   * liquidation) à côté de l'activité principale, sous son propre statut. Rien
   * n'est supposé : un métier qui ne le déclare pas succède au précédent.
   */
  static depuisParcours({
    annee_naissance,
    sexe,
    metiers,
    age_liquidation,
    macro,
    mois_naissance = 1,
    profil_carriere = PROFIL_AUTOMATIQUE,
    interruptions = null,
    nombre_enfants = 0,
    part_primes = 0.0,
    identifiant = "assuré",
  }) {
    if (!metiers || metiers.length === 0) {
      throw new Error("une carrière compte au moins un métier");
    }
    if (metiers[0].cumul) {
      throw new Error(
        "une activité cumulée s'ajoute à une activité principale : la "
        + "carrière ne peut pas commencer par elle",
      );
    }
    const cumuls = metiers.filter((metier) => metier.cumul);
    metiers = metiers.filter((metier) => !metier.cumul);

    const dateNaissance = new DateMois(annee_naissance, mois_naissance);
    const bornes = metiers.map(
      (metier) => dateNaissance.plusMois(enMois(metier.age_debut)),
    );
    const debut = bornes[0];
    // La pension prend effet ce mois-là : il n'est plus travaillé, la borne
    // est donc EXCLUE.
    const fin = dateNaissance.plusMois(enMois(age_liquidation));
    if (fin.rang <= debut.rang) {
      throw new Error("âge de liquidation antérieur à l'âge de début d'activité");
    }
    // Chaque métier s'arrête où commence le suivant : les périodes se touchent
    // bout à bout et couvrent la carrière exactement une fois. Un métier qui
    // commencerait avant le précédent, ou après la liquidation, laisserait un
    // trou ou un recouvrement — donc des mois comptés deux fois, ou pas du tout.
    for (let i = 1; i < bornes.length; i += 1) {
      if (bornes[i].rang <= bornes[i - 1].rang) {
        throw new Error(
          "les métiers doivent se suivre : chacun commence après le précédent",
        );
      }
    }
    if (bornes[bornes.length - 1].rang >= fin.rang) {
      throw new Error("le dernier métier commence après la liquidation");
    }
    const periodes = metiers.map((metier, i) => ({
      metier,
      ouverture: bornes[i],
      cloture: i + 1 < bornes.length ? bornes[i + 1] : fin,
    }));

    const anneeDebut = debut.annee;
    const annees = [];
    for (let annee = debut.annee; annee <= fin.annee; annee += 1) {
      if (moisTravailles(annee, debut, fin) > 0) {
        annees.push(annee);
      }
    }
    const anneeFin = annees[annees.length - 1];

    const plages = interruptions || new Map();
    // LE PROFIL SE LIT À UN ÂGE ET À UNE ANNÉE, et c'est tout ce dont il
    // dépend : le passé ne peut donc plus changer parce qu'on décide de
    // travailler plus longtemps, et la pente est celle que l'INSEE observe
    // pour la génération. Voir `carriere.py`, qui porte la mesure et le motif.
    const salaireMoyen = indiceSalaireMoyen(macro, anneeDebut, anneeFin);

    const lignes = [];
    for (const annee of annees) {
      const part = fractionAnnee(annee, debut, fin);
      const trimestresMaximum = trimestresCivils(moisTravailles(annee, debut, fin));
      // Le profil se lit MÉTIER PAR MÉTIER : l'affiliation peut changer en
      // cours de carrière, et c'est elle qui le choisit.
      const ageAnnee = annee - annee_naissance;
      // Ce que chaque métier a occupé de l'année. La somme vaut les mois
      // travaillés de l'année : les périodes la découpent sans reste.
      const moisParMetier = periodes.map(
        ({ ouverture, cloture }) => moisTravailles(annee, ouverture, cloture),
      );
      let revenu = 0;
      periodes.forEach(({ metier }, i) => {
        if (moisParMetier[i] > 0) {
          revenu += metier.niveau_salaire
            * profilSalaire(macro.paquet, profil_carriere, ageAnnee, annee,
              metier.affiliation)
            * salaireMoyen.get(annee)
            * (moisParMetier[i] / MOIS_PAR_AN);
        }
      });
      // Le moteur ne connaît qu'une ligne, donc qu'un statut, par année civile :
      // les régimes liquident à l'année. L'année d'un changement de métier est
      // donc rattachée à celui qui en occupe le plus de mois — et, à égalité, à
      // celui qui l'ouvre. Le revenu, lui, reste la somme de ce que les deux ont
      // réellement payé.
      let dominant = 0;
      moisParMetier.forEach((mois, i) => {
        if (mois > moisParMetier[dominant]) {
          dominant = i;
        }
      });
      const affiliation = periodes[dominant].metier.affiliation;

      lignes.push(ligneAnnuelle({
        annee,
        revenu,
        affiliation,
        type_periode: plages.get(annee) ?? "emploi",
        macro,
        part,
        part_primes,
        trimestresMaximum,
      }));
    }
    const limitees = limiterChomageNonIndemnise(lignes, annee_naissance);

    // LES ACTIVITÉS CUMULÉES, chacune sur ses propres mois. Elles ne
    // déplacent rien de l'activité principale : une ligne de plus par année
    // touchée, sous leur statut. Une interruption déclarée arrête l'activité
    // principale, pas celle-ci.
    const periodesCumulees = [];
    for (const metier of cumuls) {
      const ouverture = dateNaissance.plusMois(enMois(metier.age_debut));
      const cloture = metier.age_fin === null || metier.age_fin === undefined
        ? fin : dateNaissance.plusMois(enMois(metier.age_fin));
      if (ouverture.rang < debut.rang) {
        throw new Error(
          "une activité cumulée commence après le début de la carrière : elle "
          + "s'ajoute à une activité déjà là",
        );
      }
      if (cloture.rang > fin.rang) {
        throw new Error(
          "une activité cumulée s'arrête au plus tard à la liquidation",
        );
      }
      if (cloture.rang <= ouverture.rang) {
        throw new Error(
          "une activité cumulée doit s'arrêter après avoir commencé",
        );
      }
      periodesCumulees.push({ metier, ouverture, cloture });
      for (let annee = ouverture.annee; annee <= cloture.annee; annee += 1) {
        const mois = moisTravailles(annee, ouverture, cloture);
        if (mois <= 0) {
          continue;
        }
        const revenu = metier.niveau_salaire
          * profilSalaire(macro.paquet, profil_carriere, annee - annee_naissance,
            annee, metier.affiliation)
          * salaireMoyen.get(annee)
          * (mois / MOIS_PAR_AN);
        // Après la limite du chômage non indemnisé, qui ne regarde que
        // l'activité principale — comme en Python.
        limitees.push(ligneAnnuelle({
          annee,
          revenu,
          affiliation: metier.affiliation,
          type_periode: "emploi",
          macro,
          part: fractionAnnee(annee, ouverture, cloture),
          part_primes,
          trimestresMaximum: trimestresCivils(mois),
        }));
      }
    }

    const datesEntree = {};
    const toutes = [...periodes, ...periodesCumulees]
      .sort((a, b) => a.ouverture.rang - b.ouverture.rang);
    for (const { metier, ouverture } of toutes) {
      if (!Object.prototype.hasOwnProperty.call(datesEntree, metier.affiliation)) {
        datesEntree[metier.affiliation] = ouverture;
      }
    }

    return new Carriere({
      annee_naissance, sexe, lignes: limitees, mois_naissance, age_liquidation,
      nombre_enfants, identifiant, dates_entree: datesEntree,
    });
  }
}

/**
 * La catégorie socioprofessionnelle dont chaque profil emprunte sa FORME.
 * Portage de `PROFILS_CATEGORIE` de `carriere.py`, qui porte le motif.
 */
export const PROFILS_CATEGORIE = {
  plat: null,
  ascendant: "employe",
  fortement_ascendant: "cadre",
  ouvrier: "ouvrier",
  employe: "employe",
  profession_intermediaire: "profession_intermediaire",
  cadre: "cadre",
  public_etat: "public_etat",
  public_territoriale: "public_territoriale",
  public_hospitaliere: "public_hospitaliere",
  public_categorie_a: "public_categorie_a",
  public_categorie_b: "public_categorie_b",
  public_categorie_c: "public_categorie_c",
  public_non_titulaire: "public_non_titulaire",
};

/** Les groupes lus dans le fichier du public plutôt que dans celui du privé. */
const GROUPES_PUBLIC = new Set(
  Object.keys(PROFILS_CATEGORIE).filter((cle) => cle.startsWith("public_")),
);

/**
 * Le profil se choisit sur l'AFFILIATION. Portage de
 * `PROFIL_PAR_AFFILIATION` de `carriere.py`, qui porte le motif.
 */
export const PROFIL_PAR_AFFILIATION = {
  salarie_prive_cadre: "cadre",
  salarie_prive_cadre_entreprise_recente: "cadre",
  fonctionnaire_etat: "public_etat",
  fonctionnaire_etat_actif: "public_etat",
  fonctionnaire_etat_super_actif: "public_etat",
  fonctionnaire_pacifique: "public_etat",
  ouvrier_etat: "public_etat",
  ouvrier_etat_actif: "public_etat",
  militaire: "public_etat",
  militaire_officier: "public_etat",
  fonctionnaire_territorial_hospitalier: "public_territoriale",
  fonctionnaire_territorial_hospitalier_actif: "public_territoriale",
  fonctionnaire_territorial_hospitalier_super_actif: "public_territoriale",
  contractuel_public: "public_non_titulaire",
  maitre_enseignement_prive: "public_non_titulaire",
  profession_liberale: "cadre",
  liberal_non_reglemente: "cadre",
  avocat: "cadre",
  notaire: "cadre",
  medecin_liberal: "cadre",
  chirurgien_dentiste_ou_sage_femme: "cadre",
  pharmacien: "cadre",
  veterinaire: "cadre",
  expert_comptable: "cadre",
  auxiliaire_medical: "profession_intermediaire",
  officier_ministeriel: "cadre",
};

export const PROFIL_PAR_DEFAUT = "employe";
export const PROFIL_AUTOMATIQUE = "auto";

/**
 * La section d'activité dont chaque affiliation emprunte son facteur de pente.
 * Portage de `PROFIL_SECTEUR_PAR_AFFILIATION` de `carriere.py`, qui porte le
 * motif et l'hypothèse que ce facteur suppose.
 */
export const PROFIL_SECTEUR_PAR_AFFILIATION = {
  agent_ieg: "D",
  agent_sncf: "H",
  agent_ratp: "H",
  agent_chemins_fer_secondaires: "H",
  agent_port_strasbourg: "H",
  marin: "H",
  personnel_navigant: "H",
  agent_banque_de_france: "K",
};

const SECTION_ENSEMBLE = "B-S";
const TRANCHE_SECTEUR_JEUNE = "Y_LT30";
const TRANCHE_SECTEUR_AGEE = "Y_GE50";

/** De combien la pente d'un secteur s'écarte de celle de l'économie. */
function facteurSecteur(paquet, affiliation) {
  const section = PROFIL_SECTEUR_PAR_AFFILIATION[affiliation];
  if (section === undefined) {
    return 1.0;
  }
  const table = paquet.profil_salaire_secteur ?? {};
  const pente = (nom, vague) => {
    const profil = (table[nom] ?? {})[vague] ?? {};
    const jeune = profil[TRANCHE_SECTEUR_JEUNE];
    const agee = profil[TRANCHE_SECTEUR_AGEE];
    return jeune && agee ? agee / jeune : null;
  };
  const facteurs = [];
  for (const vague of Object.keys(table[section] ?? {}).sort()) {
    const secteur = pente(section, vague);
    const ensemble = pente(SECTION_ENSEMBLE, vague);
    if (secteur && ensemble) {
      facteurs.push(secteur / ensemble);
    }
  }
  return facteurs.length
    ? facteurs.reduce((a, b) => a + b, 0) / facteurs.length
    : 1.0;
}

/** Le groupe salarial que le modèle prête à une affiliation. */
export function profilDeLAffiliation(affiliation) {
  return PROFIL_PAR_AFFILIATION[affiliation] ?? PROFIL_PAR_DEFAUT;
}

/** Milieu prêté à chaque tranche du fichier par catégorie. */
export const TRANCHES_CATEGORIE = {
  Y_LT30: 26.0, Y30T39: 34.5, Y40T49: 44.5, Y50T59: 54.5, Y_GE60: 62.0,
};

/** Année de référence de la forme : la modulation y vaut un. */
export const ANNEE_FORME_CATEGORIE = 2024;

const TRANCHE_JEUNE = "Y26T30";
const TRANCHE_AGEE = "Y51T60";

/** Valeur d'un profil à un âge, interpolée entre les milieux de tranche. */
function interpoleTranches(profil, milieux, age) {
  const points = Object.entries(profil ?? {})
    .filter(([tranche]) => tranche in milieux)
    .map(([tranche, valeur]) => [milieux[tranche], valeur])
    .sort((a, b) => a[0] - b[0]);
  if (points.length === 0) {
    return 1.0;
  }
  if (age <= points[0][0]) {
    return points[0][1];
  }
  if (age >= points[points.length - 1][0]) {
    return points[points.length - 1][1];
  }
  for (let i = 0; i + 1 < points.length; i += 1) {
    const [ageBas, bas] = points[i];
    const [ageHaut, haut] = points[i + 1];
    if (ageBas <= age && age <= ageHaut) {
      return bas + (haut - bas) * ((age - ageBas) / (ageHaut - ageBas));
    }
  }
  return points[points.length - 1][1];
}

/** Pente de carrière de l'année, rapportée à celle de l'année de référence. */
function modulationAnnee(paquet, annee) {
  const table = paquet.profil_salaire_age ?? {};
  const annees = Object.keys(table).map(Number).sort((a, b) => a - b);
  if (annees.length === 0) {
    return 1.0;
  }
  const ecart = (millesime) => {
    const profil = table[String(millesime)] ?? {};
    const jeune = profil[TRANCHE_JEUNE];
    const agee = profil[TRANCHE_AGEE];
    return jeune === undefined || agee === undefined ? 0.0 : agee - jeune;
  };
  const reference = ecart(ANNEE_FORME_CATEGORIE);
  const borne = Math.min(Math.max(annee, annees[0]), annees[annees.length - 1]);
  return reference ? ecart(borne) / reference : 1.0;
}

/**
 * Ce que le profil fait du niveau saisi, à cet âge et cette année-là.
 * Portage de `profil_salaire` de `carriere.py`, qui porte le motif.
 */
export function profilSalaire(paquet, profil, age, annee, affiliation = null) {
  let categorie;
  if (profil === PROFIL_AUTOMATIQUE) {
    categorie = profilDeLAffiliation(affiliation ?? "");
  } else if (profil in PROFILS_CATEGORIE) {
    categorie = PROFILS_CATEGORIE[profil];
  } else {
    throw new Error(`profil de carrière inconnu : ${profil}`);
  }
  if (categorie === null) {
    return 1.0;
  }
  const table = GROUPES_PUBLIC.has(categorie)
    ? (paquet.profil_salaire_statut_public ?? {})
    : (paquet.profil_salaire_categorie ?? {});
  const forme = interpoleTranches(table[categorie], TRANCHES_CATEGORIE, age);
  const facteur = facteurSecteur(paquet, affiliation ?? "");
  return 1.0 + (forme - 1.0) * modulationAnnee(paquet, annee) * facteur;
}

/** Ce que le profil fait du niveau saisi, en début et en fin de carrière. */
export function bornesDeformation(paquet, profil, affiliation = null) {
  if (profil !== PROFIL_AUTOMATIQUE && !PROFILS_CATEGORIE[profil]) {
    return [1.0, 1.0];
  }
  return [
    profilSalaire(paquet, profil, 25.0, ANNEE_FORME_CATEGORIE, affiliation),
    profilSalaire(paquet, profil, 60.0, ANNEE_FORME_CATEGORIE, affiliation),
  ];
}

/**
 * Point d'ancrage du salaire moyen par tête, en euros bruts annuels courants.
 * Les comptes nationaux ne publient que des taux de croissance ; il faut un
 * niveau pour les cumuler. Il est ici, en un seul endroit, parce que le site
 * l'affiche désormais — dire « 1 = salaire moyen » sans dire combien cela fait
 * d'euros laissait toute la saisie dans le flou.
 */
export const ANCRAGE_SALAIRE_MOYEN = [2024, 40000.0];

/** Salaire moyen par tête d'une année, en euros BRUTS courants de cette année. */
export function salaireMoyenAnnuel(macro, annee) {
  return indiceSalaireMoyen(macro, annee, annee).get(annee);
}

/**
 * Salaire moyen par tête reconstitué en euros courants de chaque année.
 *
 * Le montant est un salaire BRUT : la série de comptes nationaux dont il dérive
 * est celle des salaires et traitements bruts (D11) rapportés à l'emploi
 * salarié, c'est-à-dire avant cotisations salariales, avant CSG et avant impôt
 * sur le revenu, cotisations patronales exclues. C'est la même assiette que
 * celle sur laquelle les régimes appellent leurs cotisations.
 *
 * La série de comptes nationaux ne donne que des TAUX DE CROISSANCE. On les
 * cumule à partir d'un point d'ancrage : le salaire moyen par tête du secteur
 * privé en 2024, arrondi à 40 000 € bruts annuels. Ce point d'ancrage est un
 * paramètre documenté, pas une donnée certifiée — il déplace proportionnellement
 * tous les revenus reconstitués, donc toutes les pensions, mais il est sans
 * effet sur les RAPPORTS entre scénarios, qui sont l'objet du modèle.
 */
export function indiceSalaireMoyen(macro, debut, fin) {
  const [ancrageAnnee, ancrageValeur] = ANCRAGE_SALAIRE_MOYEN;
  const valeurs = new Map([[ancrageAnnee, ancrageValeur]]);

  const borneHaute = Math.max(fin, ancrageAnnee);
  for (let annee = ancrageAnnee + 1; annee <= borneHaute; annee += 1) {
    valeurs.set(annee, valeurs.get(annee - 1) * (1 + macro.salaire_moyen.valeur(annee)));
  }

  const borneBasse = Math.min(debut, ancrageAnnee);
  for (let annee = ancrageAnnee - 1; annee >= borneBasse; annee -= 1) {
    valeurs.set(annee, valeurs.get(annee + 1) / (1 + macro.salaire_moyen.valeur(annee + 1)));
  }

  return valeurs;
}
