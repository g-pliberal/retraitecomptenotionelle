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
 */

import { DateMois, enMois } from "./calendrier.js";
import { assietteMinimale, salaireMoyenAnnuel } from "./carriere.js";
import { formatFixe, formatPourcentage } from "./format.js";
import {
  AgesAnnulationDecote, AgesCategorieActive, AgesJouissanceMilitaire,
  AgesOuverture, AgesRegimes, AgesSurcoteRegimesSpeciaux, AnneesSalaireReference,
  BaremesTrimestre, CarriereLongue,
  CoefficientsMinoration, DecoteFonctionPublique, DecoteRegimesSpeciaux,
  DureesProratisation, DureesRequises, DureesRequisesAvantSoixanteAns,
  DureesRequisesAvantReforme2023, DureesRequisesAvantSuspension,
  DureesRequisesFonctionPublique, DureesRequisesRegimes, CalendriersDureeRequise,
  GENERATIONS_SUSPENSION, SUSPENSION_2026_EFFET,
  GENERATION_REFORME_2023, REFORME_2023_EFFET,
  DureesServicesMilitaires,
  MajorationsPourEnfants, MinimumContributif, MinimumGaranti, MinimumVieillesse,
  ClassesCotisation, ConversionsPoints, Rendements, SalairesForfaitaires,
  MajorationsEnfantsPoints, SurcoteBaremes, SurcoteParentale, ValeursPoint,
} from "./regimes.js";
import { Fiabilite } from "./serie.js";

/** Premier trimestre que la surcote puisse compter (loi du 21 août 2003). */
const SURCOTE_DEPUIS = new DateMois(2004, 1);
/**
 * L'âge avant lequel un droit ouvert fait lire la durée à l'année d'ouverture
 * plutôt qu'à la génération : « avant l'âge de soixante ans » (L. 13, III).
 */
const AGE_DUREE_A_L_OUVERTURE = 60.0;
/** Le XXIV, C, de la loi du 14 avril 2023 ne vise que ceux qui peuvent liquider depuis ce mois. */
const DUREE_XXIV_C_DEPUIS = new DateMois(2023, 9);
/** Les régimes que L. 13 du code des pensions et le XXIV visent. */
const REGIMES_CODE_DES_PENSIONS = new Set(["fonction_publique_etat", "cnracl", "fspoeie"]);
/** Âge au-delà duquel le barème de 2007-2008 sert 1,25 %. */
const SURCOTE_AGE_MAJORE = 65;

/**
 * Les trois régimes que la liquidation unique des régimes alignés réunit — le
 * régime général, les salariés agricoles et la sécurité sociale des
 * indépendants sous ses trois noms. Les exploitants agricoles n'en sont pas :
 * la LURA ne vise que les SALARIÉS agricoles.
 */
const REGIMES_ALIGNES = new Set([
  "regime_general", "msa_salaries", "cancava", "organic", "rsi",
]);
/** La clé sous laquelle ils se réunissent : ce n'est pas un régime. */
const REGIMES_ALIGNES_TETE = "regimes_alignes";
/** Assurés nés à compter de 1953 (article 51 de la LFSS pour 2016). */
const LURA_PREMIERE_GENERATION = 1953;
/** Pensions prenant effet au 1er juillet 2017 (décret n° 2017-737, art. 4). */
const LURA_DATE_EFFET = 2017 * 12 + 6;
/** Rang du mois de septembre 2026 : premières pensions des parents à 24/23 ans. */
const PARENTS_MEILLEURES_ANNEES_DEPUIS = 2026 * 12 + 8;

/** Ce que chaque dispositif s'appelle dans la cascade des avantages. */
const LIBELLE_MAJORATION = {
  mda: "Majoration de durée d'assurance",
  bonifications: "Bonification pour enfants",
};

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
 * Durée minimale de services qui ouvre une pension militaire, même différée :
 * « lorsqu'ils ont accompli […] moins de quinze ans de services effectifs »,
 * dit le 5° de l'article L. 25, la pension n'est due qu'à l'âge légal.
 */
const SERVICES_MINIMAUX_MILITAIRES = 15.0;

/**
 * Trimestres de services que le II de l'article L. 14 ajoute à la durée
 * d'ouverture pour borner la décote militaire, et plafond de celle-ci.
 */
const TRIMESTRES_DECOTE_MILITAIRE = 10;

/**
 * Trimestres dont l'âge d'annulation de la décote est minoré pour ouvrir le
 * minimum garanti sans la durée, selon l'année où l'âge d'ouverture est
 * atteint : article 3 du décret n° 2010-1744 du 30 décembre 2010. Aucun à
 * partir de 2016.
 */
const MINORATION_AGE_MINIMUM_GARANTI = { 2011: 9, 2012: 7, 2013: 5, 2014: 3, 2015: 1 };

/**
 * Surcote de l'emploi classé de la fonction publique (loi n° 2023-270, article
 * 10, XXIV, D) : première génération des marches de 2023, et années ajoutées à
 * l'âge anticipé ou minoré.
 */
const SURCOTE_EMPLOIS_CLASSES = {
  active: [1966 + 8 / 12, 5.0],
  super_active: [1971 + 8 / 12, 10.0],
};

/** Âge de la surcote d'avant la réforme de 2023, laissé aux classés plus âgés. */
const AGE_SURCOTE_AVANT_2023 = 62.0;

/**
 * Le seul dispositif pour enfants qu'un régime EN POINTS puisse porter : une
 * majoration de durée d'assurance ne touche que la durée, qu'il oppose aussi ;
 * une bonification entre aux services, qu'il n'a pas.
 */
const MAJORATION_DE_DUREE = "mda";

/** Dernière année à compter dans les services, null si sans objet. */
function borneCarriere(carriere) {
  return carriere.age_liquidation === null || carriere.age_liquidation === undefined
    ? null
    : carriere.anneeLiquidation;
}

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

  // -- valorisation des points -----------------------------------------------

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
  valeurDuPoint(code, anneeLiquidation) {
    let conversion = 1.0;
    let courant = code;
    let fiabilite = Fiabilite.CERTIFIEE;
    for (let garde = 0; garde < this.catalogue.taille + 1; garde += 1) {
      const derniere = this.valeursPoint.derniereAnneeServie(courant);
      if (derniere === null) {
        return null;
      }
      if (anneeLiquidation <= derniere) {
        const valeur = this.valeursPoint.service(courant, anneeLiquidation);
        if (valeur === null) {
          // Liquidation antérieure au premier barème publié. Symétrique du cas
          // ci-dessous : la première valeur connue est ramenée en euros de la
          // liquidation par l'indice des prix, et la fiabilité tombe pour le dire.
          const premiereConnue = this.valeursPoint.premiereAnneeServie(courant);
          const ancienne = this.valeursPoint.service(courant, premiereConnue);
          return [
            conversion * ancienne[0]
              * this.macro.coefficientPrix(premiereConnue, anneeLiquidation),
            Math.min(fiabilite, ancienne[1], Fiabilite.MOYENNE),
          ];
        }
        return [conversion * valeur[0], Math.min(fiabilite, valeur[1])];
      }

      const successeur = this.catalogue.contient(courant)
        ? this.catalogue.obtenir(courant).integre_dans
        : null;
      const reprise = successeur
        ? this.conversionsPoints.fusion(courant, successeur)
        : null;
      if (reprise === null) {
        // AVEC UN AN DE RETARD : la revalorisation du 1er janvier suit les prix
        // de l'année écoulée (L. 161-25). Voir le Python.
        const ancienne = this.valeursPoint.service(courant, derniere);
        return [
          conversion * ancienne[0]
            * this.macro.coefficientPrix(derniere - 1, anneeLiquidation - 1),
          Math.min(fiabilite, ancienne[1], Fiabilite.MOYENNE),
        ];
      }

      conversion *= reprise.coefficient;
      fiabilite = Math.min(fiabilite, reprise.fiabilite);
      courant = successeur;
    }
    return null;
  }

  // -- salaire de référence --------------------------------------------------

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
   * La rémunération que ce régime liquide : `assietteDeReference`, et, pour un
   * régime à grille, le salaire forfaitaire de la catégorie — le marin liquide
   * « sur le salaire forfaitaire de la catégorie dans laquelle il a été
   * classé » (R. 11), non sur sa paie. Proratisé sur les mois de l'année.
   */
  /**
   * L'assiette minimale que la ligne oppose à l'un de ces régimes : celle du
   * régime de BASE d'un indépendant (D. 633-2, D. 642-4), nulle ailleurs.
   */
  assietteMinimale(codes, ligne) {
    if (!(ligne.assiette_minimale_base > 0)) {
      return 0.0;
    }
    const regle = assietteMinimale(this.macro.paquet, ligne.affiliation, ligne.annee);
    if (regle === null || !codes.some((c) => regle[1].includes(c))) {
      return 0.0;
    }
    return ligne.assiette_minimale_base;
  }

  assietteDeReference(periode, ligne) {
    if (periode.assiette_grille) {
      const forfaitGrille = this.grilles.forfait(
        periode.assiette_grille, ligne.annee, ligne.revenuAnnualise,
        (a) => salaireMoyenAnnuel(this.macro, a),
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
      const annuelle = this.catalogue.obtenir(periode.regime).periode(ligne.annee) ?? periode;
      if (annuelle.assiette_repere_smic !== null && annuelle.assiette_repere_smic !== undefined) {
        return annuelle.assiette_repere_smic
          * this.macro.smic_horaire.valeur(ligne.annee) * ligne.fraction_annee;
      }
    }
    return assietteDeReference(periode, ligne);
  }

  /**
   * Salaire de référence, en euros de l'année de liquidation. Il porte sur les
   * seules années passées dans ce régime — ou dans l'un des `membres` de sa
   * chaîne de succession, quand `code` liquide pour un régime qu'il a
   * absorbé : les années CANCAVA d'un artisan sont des années du RSI, puis du
   * régime général, et n'entrent qu'une fois dans un seul salaire annuel
   * moyen. Voir `groupesDeSuccession`.
   */
  salaireDeReference(code, carriere, periode, anneeLiquidation, plafonner,
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
      && this.catalogue.contient(code)
      && this.catalogue.obtenir(code).famille === "fonction_publique";
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
      ? (depart, arrivee) => this.macro.coefficientRevalorisationPorteeAuCompte(
        depart, arrivee, moisLiquidation)
      : (depart, arrivee) => {
        if (suitLePoint) {
          const ratio = this.minimumGaranti.ratioPointIndice(depart, arrivee);
          if (ratio !== null) {
            return ratio;
          }
        }
        return this.macro.coefficientRevalorisationSalaires(depart, arrivee);
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
      if (!this.affiliations.regimes(
        ligne.affiliation, ligne.annee, carriere.dateEntree(ligne.affiliation),
        ligne.cotise ? ligne.revenu : ligne.revenu_reference,
        this.macro.plafond_securite_sociale.valeur(ligne.annee),
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
        revenu = Math.max(this.assietteDeReference(periode, ligne),
          this.assietteMinimale([...codesAdmis], ligne));
      }
      // TRANCHE DE SALAIRE. Un régime qui liquide tranche par tranche — le
      // personnel navigant, 1,85 % par annuité sur la première et 1,4 % sur la
      // seconde (R. 426-16-1) — a besoin du salaire de SA tranche, sans quoi
      // les deux périodes simultanées calculeraient le même salaire moyen.
      // N'affecte que les assiettes à borne basse non nulle : celles qui
      // partent de zéro passent par `plafonner` comme avant.
      const [borneBasse, borneHaute] = periode.bornesAssietteEnEuros(
        this.macro.plafond_securite_sociale.valeur(ligne.annee)
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
    for (const annee of [...parAnnee.keys()].sort((a, b) => a - b)) {
      let [revenu, fraction] = parAnnee.get(annee);
      if (plafonner) {
        // Le plafond se proratise sur les mois travaillés : l'année d'entrée
        // dans la vie active n'est pas pleine.
        revenu = Math.min(
          revenu, this.macro.plafond_securite_sociale.valeur(annee) * fraction,
        );
      }
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
        const parGeneration = this.anneesSalaireReference.annees(generation);
        if (parGeneration !== null) {
          annees = parGeneration[0];
        }
        // LES PARENTS : vingt-quatre années pour qui bénéficie d'une
        // majoration ou d'une bonification au titre d'un enfant, vingt-trois
        // pour deux enfants et plus, pensions prenant effet à compter du
        // 1er septembre 2026 (R. 173-3-2, décret n° 2026-699).
        if (enfantsMajores > 0 && carriere.age_liquidation !== null
            && carriere.dateLiquidation.rang >= this.parentsMeilleuresAnneesDepuis) {
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
        (ligne) => this.affiliations.regimes(
          ligne.affiliation, anneeLiquidation,
          carriere.dateEntree(ligne.affiliation),
          ligne.revenu, this.macro.plafond_securite_sociale.valeur(anneeLiquidation))
          .some((c) => codesAdmis.has(c)),
      ) ?? null;
      if (derniere !== null && derniere.cotise && derniere.fraction_annee > 0) {
        let traitement = this.assietteDeReference(periode, derniere)
          / derniere.fraction_annee;
        if (plafonner) {
          traitement = Math.min(
            traitement,
            this.macro.plafond_securite_sociale.valeur(anneeLiquidation),
          );
        }
        return traitement;
      }
      return revenus[revenus.length - 1];
    } else {
      retenus = revenus;
    }
    return retenus.reduce((total, valeur) => total + valeur, 0.0) / retenus.length;
  }

  // -- calcul ----------------------------------------------------------------

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
  /** @returns {[number, number|null]} durée requise opposable, et fiabilité. */
  dureeRequise(periode, carriere) {
    // UN RÉGIME SPÉCIAL QUI ÉCRIT SES TABLES PASSE AVANT LA TABLE COMMUNE : la
    // SNCF, la RATP et les IEG — tables par génération à compter de leur date
    // d'effet, puis calendrier de 2008 lu au mois où les conditions sont réunies.
    const propre = this.dureePropre(periode, carriere);
    if (propre !== null) {
      return [propre[0], propre[2]];
    }
    // La fonction publique a sa propre montée en charge, 2004-2008, lue à
    // l'année d'ouverture du droit ; elle passe avant la table par génération.
    if (periode.bareme_decote === "fonction_publique") {
      const transitoire = this.dureesRequisesFonctionPublique.trimestres(
        this.anneeOuvertureDesDroits(
          periode, carriere,
          (carriere.age_liquidation !== null && carriere.age_liquidation !== undefined)
            ? carriere.anneeLiquidation : 9999,
        ),
      );
      if (transitoire !== null) {
        return transitoire;
      }
    }
    // ET UN EMPLOI CLASSÉ N'A PAS LA DURÉE DE SA GÉNÉRATION : le XXIV, B de
    // l'article 10 de la loi du 14 avril 2023 pour l'État, et le II, B de
    // l'article 13 du décret n° 2023-435 pour la CNRACL et le FSPOEIE, lui en
    // fixent une propre « par dérogation à l'article L. 13 ».
    const derogation = this.derogationActive(periode, carriere);
    if (derogation !== null && derogation.dureeRequise !== null) {
      return [derogation.dureeRequise, derogation.fiabilite];
    }
    // Et ceux que ces marches ne visent pas — l'emploi classé né avant elles,
    // le militaire — n'ont pas davantage la durée de leur génération.
    const avantSoixanteAns = this.dureeRequiseAvantSoixanteAns(periode, carriere, derogation);
    if (avantSoixanteAns !== null) {
      return avantSoixanteAns;
    }
    if (periode.duree_requise_par_generation) {
      // LA RÉFORME DE 2023 NE VAUT QU'À COMPTER DU 1er SEPTEMBRE 2023 : avant,
      // les nés à compter du 1er septembre 1961 doivent la durée de la version
      // de 2014 de L. 161-17-3. Voir le Python.
      const [anneeReforme, moisReforme] = REFORME_2023_EFFET;
      if (carriere.age_liquidation !== null && carriere.age_liquidation !== undefined
          && carriere.generation >= GENERATION_REFORME_2023
          && (carriere.anneeLiquidation < anneeReforme
            || (carriere.anneeLiquidation === anneeReforme
              && carriere.moisLiquidation < moisReforme))) {
        const avant = this.dureesRequisesAvantReforme2023.trimestres(carriere.generation);
        if (avant !== null) {
          return avant;
        }
      }
      // LA SUSPENSION NE VAUT QU'À COMPTER DU 1er SEPTEMBRE 2026 : avant, les
      // nés en 1964 et 1965 doivent la durée de la loi de 2023.
      const [anneeEffet, moisEffet] = SUSPENSION_2026_EFFET;
      if (carriere.age_liquidation !== null && carriere.age_liquidation !== undefined
          && carriere.generation >= GENERATIONS_SUSPENSION[0]
          && carriere.generation < GENERATIONS_SUSPENSION[1]
          && (carriere.anneeLiquidation < anneeEffet
            || (carriere.anneeLiquidation === anneeEffet
              && carriere.moisLiquidation < moisEffet))) {
        const avant = this.dureesRequisesAvantSuspension.trimestres(carriere.generation);
        if (avant !== null) {
          return avant;
        }
      }
      const parGeneration = this.dureesRequises.trimestres(carriere.generation);
      if (parGeneration !== null) {
        return parGeneration;
      }
    }
    return [periode.duree_requise_trimestres || 160, null];
  }

  /**
   * La durée d'un droit qui s'ouvre avant soixante ans, ou null.
   *
   * Le militaire qui réunit ses services, l'emploi classé qui atteint son âge
   * anticipé ou minoré ne se voient pas opposer la durée de leur génération,
   * mais « celle exigée des fonctionnaires atteignant [soixante ans] l'année à
   * compter de laquelle la liquidation peut intervenir » — article 5, VI, de
   * la loi du 21 août 2003, puis L. 13, III, du code des pensions, que le XXIV
   * de la loi du 14 avril 2023 garde en vigueur par renvoi. Le militaire qui
   * peut liquider à compter du 1er septembre 2023 relève du C, 2°, du même
   * XXIV. Avant 2004, c'est la durée que la fiche portait l'année d'ouverture.
   * ``derogation`` est celle que dureeRequise vient de lire.
   *
   * @returns {[number, number|null] | null}
   */
  dureeRequiseAvantSoixanteAns(periode, carriere, derogation) {
    if (periode.bareme_decote !== "fonction_publique") {
      return null;
    }
    const militaire = this.droitMilitaire(periode, carriere);
    let age;
    let carriereLongue = false;
    if (militaire !== null) {
      age = militaire.ageOuverture;
    } else if (derogation !== null) {
      age = derogation.ageOuverture;
    } else if (REGIMES_CODE_DES_PENSIONS.has(periode.regime)) {
      // Le fonctionnaire sédentaire dont la carrière longue ouvre le droit
      // avant soixante ans relève du même C du XXIV : voir le Python.
      age = this.ouvertureCarriereLongue(periode, carriere);
      if (age === null) {
        return null;
      }
      carriereLongue = true;
    } else {
      return null;
    }
    if (age >= AGE_DUREE_A_L_OUVERTURE) {
      return null;
    }
    let ouverture = carriere.dateNaissance.plusMois(enMois(age));
    if (carriere.age_liquidation !== null && carriere.age_liquidation !== undefined) {
      ouverture = DateMois.depuisRang(Math.min(
        ouverture.rang,
        carriere.dateNaissance.plusMois(enMois(carriere.age_liquidation)).rang,
      ));
    }
    if ((militaire !== null || carriereLongue) && ouverture.rang >= DUREE_XXIV_C_DEPUIS.rang) {
      return this.dureesRequisesAvantSoixanteAns.depuis2023(ouverture);
    }
    const transitoire = this.dureesRequisesFonctionPublique.trimestres(ouverture.annee);
    if (transitoire !== null) {
      return transitoire;
    }
    const parAnnee = this.dureesRequisesAvantSoixanteAns.parAnnee(ouverture.annee);
    if (parAnnee !== null) {
      return parAnnee;
    }
    const enVigueur = this.catalogue.obtenir(periode.regime).periode(ouverture.annee);
    if (enVigueur === null || enVigueur === undefined
        || enVigueur.duree_requise_trimestres === null
        || enVigueur.duree_requise_trimestres === undefined) {
      return null;
    }
    return [enVigueur.duree_requise_trimestres, null];
  }

  /**
   * L'âge où la carrière longue ouvre le droit de ce fonctionnaire, s'il l'ouvre
   * au plus tard à la liquidation ; `null` sinon. La condition de durée est
   * celle de la génération (D. 16-1 du code des pensions) : pendant qu'on la
   * lit, `dureeRequise` ne rend pas la durée que ce droit fait opposer ensuite.
   */
  ouvertureCarriereLongue(periode, carriere) {
    if (this.ouvertureCarriereLongueEnCours
        || carriere.age_liquidation === null || carriere.age_liquidation === undefined) {
      return null;
    }
    this.ouvertureCarriereLongueEnCours = true;
    let age;
    try {
      age = this.ageCarriereLongue(carriere, [[periode.regime, periode]]);
    } finally {
      this.ouvertureCarriereLongueEnCours = false;
    }
    if (age === null || age === undefined || age > carriere.age_liquidation + 1e-9) {
      return null;
    }
    return age;
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
  dureeProratisation(periode, carriere, requis) {
    // La table est celle du CODE DE LA SÉCURITÉ SOCIALE, et la fiche dit qui la
    // suit : le régime général et les régimes alignés. La fonction publique et
    // les régimes spéciaux ont la leur, calendaire (article L. 13 du code des
    // pensions) ; elle n'est pas modélisée, et leur durée requise y fait office.
    if (!periode.duree_proratisation_par_generation) {
      return [requis, null];
    }
    const parGeneration = this.dureesProratisation.trimestres(carriere.generation);
    if (parGeneration === null) {
      return [requis, null];
    }
    // Elle ne dépasse jamais la durée requise : les périodes anciennes, dont la
    // durée maximale est plus courte que 150 trimestres, gardent la leur.
    return [Math.min(parGeneration[0], requis), parGeneration[1]];
  }

  // -- succession de régimes -------------------------------------------------

  /**
   * Le régime au bout de la chaîne d'absorption de `code`, tant que la chaîne
   * reste en annuités : `cancava` et `rsi` rendent `regime_general`,
   * `pensions_civiles_1853` rend `fonction_publique_etat`. Un régime en points
   * au bout de la chaîne l'arrête, et un régime en points n'y entre jamais :
   * ses points se convertissent et s'additionnent déjà (voir `valeurDuPoint`).
   *
   * L'absorption ne se suit qu'à partir de l'année où le régime FERME à ses
   * affiliés — celle où l'absorbant commence à recevoir leurs années. Avant,
   * ce sont deux régimes distincts, et un polypensionné en a deux.
   */
  teteDeSuccession(code, anneeLiquidation) {
    const vu = new Set([code]);
    let courant = code;
    for (;;) {
      const regime = this.catalogue.obtenir(courant);
      const suivant = regime.integre_dans;
      const borne = regime.fermeture !== null && regime.fermeture !== undefined
        ? regime.fermeture
        : regime.extinction;
      if (suivant === null || suivant === undefined
          || borne === null || borne === undefined || anneeLiquidation < borne
          || !this.catalogue.contient(suivant) || vu.has(suivant)) {
        return courant;
      }
      const absorbant = this.catalogue.obtenir(suivant);
      const periode = absorbant.periode(
        Math.min(anneeLiquidation, derniereAnnee(absorbant)),
      );
      if (periode === null || periode.type_calcul !== "annuites") {
        return courant;
      }
      vu.add(suivant);
      courant = suivant;
    }
  }

  /**
   * Les régimes d'annuités que la carrière a traversés, groupés par chaîne de
   * succession : pour chaque code d'un groupe d'au moins deux, les membres du
   * groupe, LE PREMIER ÉTANT CELUI QUI LIQUIDE.
   *
   * Un régime et celui qui lui succède ne sont pas deux régimes. La CANCAVA,
   * le RSI et le régime général sont trois NOMS du même droit pour un
   * artisan : sa caisse calcule un seul salaire annuel moyen sur toute la
   * carrière et un seul coefficient de proratisation. Liquider chaque nom sur
   * ses seules années calculait deux salaires de référence là où la caisse
   * n'en calcule qu'un : « 30 077 € × 120/165 » plus « 36 778 € × 40/165 » au
   * lieu de « 34 152 € × 160/165 », de −7,2 % à +0,3 % contre l'oracle du
   * régime général.
   *
   * Le groupe est liquidé par le membre de la DERNIÈRE période active de la
   * carrière — à égalité, par l'absorbant —, dont la fiche donne les règles,
   * et c'est aussi ce que la LURA prescrit.
   *
   * ET LES RÉGIMES ALIGNÉS DISTINCTS SE RÉUNISSENT AUSSI, DEPUIS 2017. La
   * liquidation unique des régimes alignés (L. 173-1-2 CSS) donne une seule
   * retraite à qui a cotisé à deux des trois régimes alignés : un revenu
   * annuel moyen formé de la somme des salaires et revenus d'une même année,
   * sur les vingt-cinq meilleures, et une proratisation qui tient compte de
   * tous leurs trimestres (R. 173-4-4-1, 1° et 4°). Le modèle y arrivait pour
   * le couple régime général / indépendants par la chaîne d'absorption, qui
   * ne ferme le RSI qu'en 2018, et pas du tout pour les salariés agricoles.
   *
   * @returns {Map<string, string[]>}
   */
  groupesDeSuccession(codes, anneeLiquidation, derniereAnneeParRegime, carriere = null) {
    const parTete = new Map();
    const lura = carriere !== null
      && carriere.generation >= LURA_PREMIERE_GENERATION
      && carriere.dateLiquidation.rang >= LURA_DATE_EFFET;
    for (const code of codes) {
      const regime = this.catalogue.obtenir(code);
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
      if (periode === null || periode.type_calcul !== "annuites") {
        continue;
      }
      const tete = lura && REGIMES_ALIGNES.has(code)
        ? REGIMES_ALIGNES_TETE
        : this.teteDeSuccession(code, anneeLiquidation);
      if (!parTete.has(tete)) {
        parTete.set(tete, []);
      }
      parTete.get(tete).push(code);
    }
    const groupes = new Map();
    for (const membres of parTete.values()) {
      if (membres.length < 2) {
        continue;
      }
      const rang = new Map(this.chaineDepuis(membres).map((code, i) => [code, i]));
      let liquidateur = membres[0];
      for (const code of membres) {
        const derniere = derniereAnneeParRegime.get(code) ?? 0;
        const reference = derniereAnneeParRegime.get(liquidateur) ?? 0;
        if (derniere > reference
            || (derniere === reference && rang.get(code) > rang.get(liquidateur))) {
          liquidateur = code;
        }
      }
      const ordonnes = [
        liquidateur,
        ...[...membres].sort((a, b) => rang.get(a) - rang.get(b))
          .filter((code) => code !== liquidateur),
      ];
      for (const code of membres) {
        groupes.set(code, ordonnes);
      }
    }
    return groupes;
  }

  /** Les membres dans l'ordre de la chaîne, du plus ancien à l'absorbant. */
  chaineDepuis(membres) {
    const restants = new Set(membres);
    let ordre = [];
    for (const depart of [...membres].sort()) {
      let courant = depart;
      const chaine = [];
      while (restants.has(courant) && !ordre.includes(courant)) {
        chaine.push(courant);
        courant = this.catalogue.obtenir(courant).integre_dans;
      }
      if (chaine.length > ordre.length) {
        ordre = chaine;
      }
    }
    return [...ordre, ...[...restants].filter((c) => !ordre.includes(c)).sort()];
  }

  // -- catégorie active et pension militaire ---------------------------------

  /**
   * Le classement que la carrière a exercé le plus longtemps.
   *
   * La règle est celle du code : quand plusieurs emplois classés se succèdent,
   * « la catégorie applicable pour bénéficier de l'âge de départ minoré est
   * celle associée à l'emploi que le fonctionnaire a occupé le plus longtemps »
   * (L. 24, I, 1°). À égalité, le classement le plus favorable l'emporte,
   * parce que la durée qu'il exige est la plus longue.
   */
  statutDominant(carriere, classements) {
    const durees = new Map();
    const borne = borneCarriere(carriere);
    for (const [statut, classement] of Object.entries(classements)) {
      const duree = carriere.dureeDeService([statut], borne);
      if (duree > 0) {
        durees.set(classement, (durees.get(classement) ?? 0) + duree);
      }
    }
    if (durees.size === 0) {
      return null;
    }
    let meilleur = null;
    let reference = [-1, 0];
    for (const cle of [...durees.keys()].sort()) {
      const rang = [durees.get(cle),
        (cle === "super_active" || cle === "officier") ? 1 : 0];
      if (rang[0] > reference[0] || (rang[0] === reference[0] && rang[1] > reference[1])) {
        meilleur = cle;
        reference = rang;
      }
    }
    return meilleur;
  }

  /**
   * Les régimes que ces statuts atteignent, une année au moins.
   *
   * C'est la seconde garde du droit dérogatoire, et elle n'est pas de confort.
   * Plusieurs régimes SPÉCIAUX servent eux aussi une catégorie active — leur
   * fiche le déclare, et c'est exact : la SNCF a ses agents de conduite. Mais
   * la catégorie active de la fonction publique n'a rien à y voir : sans cette
   * garde, un assuré ayant fait vingt ans d'emploi classé après une carrière à
   * la SNCF aurait vu son régime SNCF liquidé à l'âge de la fonction publique.
   */
  regimesRoutes(statuts) {
    const codes = new Set();
    for (const statut of statuts) {
      for (const periode of this.affiliations.periodes(statut)) {
        for (const code of periode.regimes ?? []) {
          codes.add(code);
        }
      }
    }
    return codes;
  }

  /**
   * L'âge anticipé que le classement de l'emploi ouvre, ou null.
   *
   * Quatre conditions, et la fiche en porte une : le régime doit servir la
   * catégorie active — l'avoir dans ses `avantages_non_contributifs` —, le
   * statut déclaré doit être classé, le régime doit être l'un de ceux que ce
   * statut route (cf. `regimesRoutes`), et la carrière doit porter la durée de
   * services classés que l'article L. 24 exige. Sans elle, l'assuré reste au
   * droit commun : la faculté « est ouverte à la condition que le fonctionnaire
   * puisse se prévaloir, au total, d'au moins dix-sept ans de services […] dits
   * services actifs ».
   */
  derogationActive(periode, carriere) {
    if (!periode.avantages_non_contributifs.includes("categorie_active")) {
      return null;
    }
    const classements = this.affiliations.classementsActifs;
    const classement = this.statutDominant(carriere, classements);
    if (classement === null) {
      return null;
    }
    const derogation = this.agesCategorieActive.derogation(
      classement, carriere.generation,
    );
    if (derogation === null) {
      return null;
    }
    const statuts = Object.keys(classements)
      .filter((code) => classements[code] === classement);
    if (!this.regimesRoutes(statuts).has(periode.regime)) {
      return null;
    }
    const servies = carriere.dureeDeService(statuts, borneCarriere(carriere));
    if (servies + 1e-9 < derogation.servicesRequis) {
      return null;
    }
    return derogation;
  }

  /**
   * Ce que la pension militaire oppose à cet assuré, ou null.
   *
   * Elle ne s'ouvre pas à un âge mais à une DURÉE — dix-sept ans de services
   * effectifs pour un non-officier, vingt-sept pour un officier (L. 24, II).
   * Qui la réunit liquide aussitôt ; qui ne la réunit pas mais a quinze ans de
   * services attend l'âge de jouissance différée de l'article L. 25 ; qui a
   * moins de quinze ans n'a pas de pension militaire.
   */
  droitMilitaire(periode, carriere) {
    if (!periode.avantages_non_contributifs.includes("categorie_active")) {
      return null;
    }
    const categories = this.affiliations.categoriesMilitaires;
    const categorie = this.statutDominant(carriere, categories);
    if (categorie === null) {
      return null;
    }
    const statuts = Object.keys(categories)
      .filter((code) => categories[code] === categorie);
    if (!this.regimesRoutes(statuts).has(periode.regime)) {
      return null;
    }
    const base = this.dureesServicesMilitaires.dureeDeBase(categorie);
    if (base === null) {
      return null;
    }
    const dateBase = carriere.dateDeService(statuts, base);
    const anneeBase = dateBase === null
      ? 9999.0
      : dateBase.annee + (dateBase.mois - 1) / 12;
    const requises = this.dureesServicesMilitaires.anneesRequises(categorie, anneeBase);
    if (requises === null || requises === undefined) {
      return null;
    }
    const [anneesRequises] = requises;
    let fiabilite = requises[1];
    const servies = carriere.dureeDeService(statuts, borneCarriere(carriere));
    const ageRequis = carriere.ageDeService(statuts, anneesRequises);
    let ageOuverture;
    let differee;
    if (servies + 1e-9 >= anneesRequises && ageRequis !== null) {
      ageOuverture = ageRequis;
      differee = false;
    } else if (servies + 1e-9 >= SERVICES_MINIMAUX_MILITAIRES) {
      const parGeneration = this.agesJouissanceMilitaire.age(carriere.generation);
      if (parGeneration === null) {
        return null;
      }
      ageOuverture = parGeneration[0];
      differee = true;
      fiabilite = Math.min(fiabilite, parGeneration[1]);
    } else {
      return null;
    }
    return {
      ageOuverture,
      trimestresServis: Math.round(servies * 4),
      trimestresCible: Math.round(anneesRequises * 4) + TRIMESTRES_DECOTE_MILITAIRE,
      jouissanceDifferee: differee,
      fiabilite,
    };
  }

  /**
   * Âge légal opposable à cet assuré dans ce régime.
   *
   * Trois droits se superposent, du plus particulier au plus général : la
   * pension militaire, qui s'ouvre à une durée de services ; la catégorie
   * active, qui avance l'âge de cinq ou de dix années ; le droit commun.
   */
  ageOuverture(periode, carriere) {
    const militaire = this.droitMilitaire(periode, carriere);
    if (militaire !== null) {
      return militaire.ageOuverture;
    }
    const derogation = this.derogationActive(periode, carriere);
    if (derogation !== null) {
      return derogation.ageOuverture;
    }
    const commun = this.ageOuvertureCommun(periode, carriere);
    const speciale = this.ouverturePensionSpeciale(periode, carriere);
    if (speciale !== null) {
      return speciale;
    }
    const parServices = this.ouvertureParServices(periode, carriere);
    if (parServices !== null && parServices < commun) {
      return parServices;
    }
    return commun;
  }

  /** Les statuts que le régime route, et les années servies dans ceux-ci. */
  servicesDansLeRegime(periode, carriere) {
    const statuts = this.affiliations.codes
      .filter((code) => this.regimesRoutes([code]).has(periode.regime));
    return { statuts, servies: carriere.dureeDeService(statuts, borneCarriere(carriere)) };
  }

  /**
   * L'âge de la pension SPÉCIALE des marins, ou null si l'assuré a les quinze
   * ans de services qui ouvrent une autre pension. Elle entre en jouissance
   * avec la pension de base d'un autre régime, jamais avant cinquante-cinq ans,
   * et à défaut à soixante ans (L. 5552-12 du code des transports, R. 5 du code
   * des pensions de retraite des marins). Le modèle liquidant tout à la même
   * date, elle suit le plus précoce des AUTRES régimes de base traversés.
   */
  ouverturePensionSpeciale(periode, carriere) {
    const seuil = periode.pension_speciale_services_annees;
    const isole = periode.pension_speciale_age_sans_autre_pension;
    if (seuil == null || isole == null) {
      return null;
    }
    const { servies } = this.servicesDansLeRegime(periode, carriere);
    if (servies + 1e-9 >= seuil) {
      return null;
    }
    const { annuites, autres } = this.periodesParcourues(carriere);
    const bases = [...annuites, ...this.periodesOpposantUneDuree(autres)]
      .filter(([code]) => code !== periode.regime)
      .map(([, p]) => p);
    if (bases.length === 0) {
      return isole;
    }
    return Math.max(periode.age_ouverture,
      Math.min(...bases.map((p) => this.ageOuverture(p, carriere))));
  }

  /**
   * L'âge que la durée de services dans le régime ouvre, ou null.
   *
   * Les marins acquièrent la pension d'ancienneté « lorsque se trouve remplie
   * la double condition de cinquante ans d'âge et de vingt-cinq années de
   * services » (R. 2 de leur code) ; les cinquante-cinq ans que le même article
   * fixe ensuite ne bornent que l'entrée en jouissance de celui qui continue à
   * naviguer (L. 5552-5 du code des transports). L'âge est le plus tardif de
   * l'âge écrit et de celui où la durée est atteinte.
   */
  ouvertureParServices(periode, carriere) {
    if (periode.age_ouverture_services == null
        || periode.services_ouverture_annees == null) {
      return null;
    }
    const { statuts, servies } = this.servicesDansLeRegime(periode, carriere);
    const requis = periode.services_ouverture_annees;
    if (servies + 1e-9 < requis) {
      return null;
    }
    const atteint = carriere.ageDeService(statuts, requis);
    if (atteint === null) {
      return null;
    }
    return Math.max(periode.age_ouverture_services, atteint);
  }

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
   * Âge au-delà duquel les trimestres cotisés ouvrent la surcote : l'âge légal
   * de droit commun, sauf la SNCF et la RATP, qui ont leur calendrier, et
   * l'emploi classé de la fonction publique. Pour lui, le D du XXIV de
   * l'article 10 de la loi du 14 avril 2023 (et le II, D, de l'article 13 du
   * décret n° 2023-435) donne l'âge anticipé majoré de cinq années aux actifs
   * nés à compter du 1er septembre 1966, l'âge minoré majoré de dix aux
   * super-actifs nés à compter du 1er septembre 1971, et soixante-deux ans
   * avant — et non l'âge légal de leur génération.
   */
  ageSurcote(periode, carriere) {
    if (periode.age_surcote_regimes_speciaux) {
      const propre = this.agesSurcoteRegimesSpeciaux.age(carriere.generation);
      if (propre !== null) {
        return propre[0];
      }
    }
    const commun = this.ageOuvertureCommun(periode, carriere);
    if (this.catalogue.obtenir(periode.regime).famille !== "fonction_publique") {
      return commun;
    }
    const derogation = this.derogationActive(periode, carriere);
    if (derogation === null) {
      return commun;
    }
    const classement = this.statutDominant(carriere, this.affiliations.classementsActifs);
    const marche = SURCOTE_EMPLOIS_CLASSES[classement ?? ""];
    if (marche === undefined) {
      return commun;
    }
    const [premiereGeneration, majoration] = marche;
    if (carriere.generation + 1e-9 >= premiereGeneration) {
      return derogation.ageOuverture + majoration;
    }
    return Math.min(commun, AGE_SURCOTE_AVANT_2023);
  }

  ageOuvertureCommun(periode, carriere) {
    if (periode.age_table) {
      const propres = this.agesRegimes.ages(periode.age_table, carriere.generation);
      // Un âge vide renvoie au droit commun, que les tables communes portent.
      if (propres !== null && propres[0] !== null) {
        return propres[0];
      }
    }
    if (periode.age_ouverture_par_generation) {
      const parGeneration = this.agesOuverture.age(carriere.generation);
      if (parGeneration !== null) {
        return parGeneration[0];
      }
    }
    return periode.age_ouverture;
  }

  /**
   * Les régimes que cette carrière traverse, séparés en deux paquets.
   *
   * Le premier est celui des régimes en ANNUITÉS, qui commandent le taux plein
   * et l'ouverture du droit ; le second recueille les autres. C'est la même
   * énumération que celle de `calculer`, mais tirée de la seule carrière : elle
   * répond donc AVANT que la pension ne soit calculée, ce qu'il faut pour dater
   * un départ.
   *
   * @returns {{annuites: Array, autres: Array}}
   */
  periodesParcourues(carriere) {
    const anneeLiquidation = carriere.anneeLiquidation;
    const codes = new Set();
    for (const ligne of carriere.lignes) {
      if (ligne.annee > anneeLiquidation) {
        continue;
      }
      for (const code of this.affiliations.regimes(
        ligne.affiliation, ligne.annee, carriere.dateEntree(ligne.affiliation),
        ligne.cotise ? ligne.revenu : ligne.revenu_reference,
        this.macro.plafond_securite_sociale.valeur(ligne.annee),
      )) {
        codes.add(code);
      }
    }
    const annuites = [];
    const autres = [];
    for (const code of [...codes].sort()) {
      if (!this.catalogue.contient(code)) {
        continue;
      }
      const regime = this.catalogue.obtenir(code);
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
      if (periode === null) {
        continue;
      }
      (periode.type_calcul === "annuites" ? annuites : autres).push([code, periode]);
    }
    return { annuites, autres };
  }

  /**
   * L'âge auquel le droit OUVRE la liquidation de cette carrière.
   *
   * C'est la même question que celle posée dans `calculer` — le plus précoce
   * des régimes de base parcourus, chacun lisant l'âge que sa génération lui
   * oppose —, mais posée AVANT la pension et sans la calculer. Elle a un usage
   * propre : dater le départ d'un cas type. Une grille qui fait partir toutes
   * les générations au même âge fait partir celle de 1940 à un âge que la loi
   * de 2023 lui opposera soixante ans plus tard.
   *
   * Ce sont les régimes en ANNUITÉS qui commandent. Quand la carrière n'en a
   * aucun — le libéral, dont le régime de base est en points —, les autres
   * répondent. `null` quand aucun régime connu n'est parcouru.
   */
  ageOuvertureDroit(carriere) {
    const { annuites, autres: enPoints } = this.periodesParcourues(carriere);
    const autres = this.sansAgesPropres(enPoints);
    const retenues = annuites.length > 0 ? annuites : autres;
    if (retenues.length === 0) {
      return null;
    }
    const ouverture = Math.min(
      ...retenues.map(([, periode]) => this.ageOuverture(periode, carriere)),
    );
    // Les deux régimes de base en POINTS ouvrent la carrière longue :
    // L. 732-18-1 du code rural pour les non-salariés agricoles, le II de
    // L. 643-3 du code de la sécurité sociale pour les professions libérales,
    // par renvoi à L. 351-1-1. Les deux règles d'âge la lisent sur la même
    // liste, sans quoi elles se contrediraient.
    const anticipe = this.ageCarriereLongue(
      carriere,
      annuites.length > 0 ? annuites : this.periodesOpposantUneDuree(autres),
    );
    if (anticipe !== null && anticipe < ouverture) {
      return anticipe;
    }
    return ouverture;
  }

  /**
   * L'âge que le départ anticipé pour carrière longue proposerait à cette
   * carrière, ou `null` s'il ne lui ouvre rien.
   *
   * `calculer` la connaissait déjà, mais comme une dérogation qu'on lui
   * demande à un âge donné, pas comme un âge qu'il propose : un salarié entré à
   * dix-huit ans et né en 1965 partait, en cas type, à l'âge légal quand le
   * droit lui ouvre soixante-deux ans au taux plein. La durée requise et les
   * trimestres cotisés sont ceux que `calculer` oppose au même départ.
   */
  ageCarriereLongue(carriere, annuites) {
    if (annuites.length === 0) {
      return null;
    }
    const requis = Math.max(
      ...annuites.map(([, periode]) => this.dureeRequise(periode, carriere)[0]),
    ) || 160;
    const anneeLiquidation = carriere.anneeLiquidation;
    let cotises = carriere.trimestresCumules(carriere.lignes.filter(
      (ligne) => ligne.cotise && ligne.annee <= anneeLiquidation,
    ));
    const majoration = this.majorationPourEnfants(
      carriere, new Map(annuites.map(([code]) => [code, cotises])), anneeLiquidation,
    );
    cotises = this.carriereLongue.cotisesReputes(
      carriere, cotises, majoration !== null ? majoration.trimestres : 0,
    );
    return this.carriereLongue.agePropose(
      carriere, anneeLiquidation, cotises, requis, carriere.age_liquidation,
    );
  }

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
   * Parmi des périodes NON annuitaires, celles qui opposent une durée.
   *
   * L'Agirc-Arrco et l'Ircantec sont écartées : elles ont leurs propres
   * coefficients d'anticipation, et ne sont jamais seules sur une carrière.
   */
  periodesOpposantUneDuree(periodes) {
    return periodes.filter(([, periode]) =>
      periode.abattement_points !== "agirc_arrco"
      && periode.abattement_points !== "ircantec");
  }

  /**
   * Les périodes en points, moins les complémentaires qui ont leurs âges : une
   * complémentaire qui a SES âges ne dit pas quand le droit s'ouvre ni quand il
   * est entier, c'est le régime de base qu'elle accompagne qui le dit, et
   * `calculer` l'écarte déjà. Si rien d'autre ne reste, on la garde. Voir le
   * modèle Python.
   */
  sansAgesPropres(periodes) {
    const communes = periodes.filter(([, periode]) => !periode.age_table);
    return communes.length > 0 ? communes : periodes;
  }

  ageTauxPleinDroit(carriere) {
    const { annuites, autres: enPoints } = this.periodesParcourues(carriere);
    const autres = this.sansAgesPropres(enPoints);
    const retenues = annuites.length > 0 ? annuites : autres;
    if (retenues.length === 0) {
      return null;
    }
    const ouverture = Math.min(
      ...retenues.map(([, periode]) => this.ageOuverture(periode, carriere)),
    );
    // Une carrière entière en points n'a aucune période en annuités, et la
    // règle rendait alors l'âge d'OUVERTURE — elle faisait donc liquider au
    // taux plein des carrières que `abattementPoints` servait minorées. Le
    // droit oppose bien la durée aux régimes en points : L. 643-3 du code de
    // la sécurité sociale pour les professions libérales, L. 732-24 II du code
    // rural pour les non-salariés agricoles. L'Agirc-Arrco et l'Ircantec sont
    // écartées : elles ont leurs propres coefficients d'anticipation, et ne
    // sont jamais seules sur une carrière.
    const opposent = annuites.length > 0
      ? annuites
      : this.periodesOpposantUneDuree(autres);
    if (opposent.length === 0) {
      return ouverture;
    }
    const annulation = Math.min(
      ...retenues.map(([, periode]) => this.ageTauxPlein(periode, carriere)),
    );
    const requis = Math.max(
      ...opposent.map(([, periode]) => this.dureeRequise(periode, carriere)[0]),
    );
    if (!requis) {
      return ouverture;
    }
    const anneeLiquidation = carriere.anneeLiquidation;
    let acquis = carriere.trimestresCumules(carriere.lignes.filter(
      (ligne) => ligne.annee <= anneeLiquidation,
    ));
    // Les trimestres accordés au titre des enfants comptent dans la durée,
    // lus au régime qui les porte comme `calculer` le fait : sans eux, une
    // mère de deux enfants était datée trois ans après l'âge où sa pension
    // est entière.
    const majoration = this.majorationPourEnfants(
      carriere, new Map(opposent.map(([code]) => [code, acquis])), anneeLiquidation,
    );
    if (majoration !== null) {
      acquis += majoration.trimestres;
    }
    const duree = carriere.age_liquidation + (requis - acquis) / 4.0;
    const tauxPlein = Math.min(annulation, Math.max(ouverture, duree));
    // Le départ anticipé pour carrière longue passe avant les trois termes :
    // il n'ouvre qu'à qui a sa durée COTISÉE, donc au taux plein.
    const anticipe = this.ageCarriereLongue(carriere, opposent);
    if (anticipe !== null && anticipe < tauxPlein) {
      return anticipe;
    }
    return tauxPlein;
  }

  /**
   * Âge d'annulation de la décote opposable à cet assuré.
   *
   * Pour un emploi classé, ce n'est pas soixante-sept ans mais la limite d'âge
   * du grade — soixante-deux ans en catégorie active, cinquante-sept en
   * super-active —, puis l'âge que l'article L. 14 bis attache au classement.
   */
  ageTauxPlein(periode, carriere) {
    const derogation = this.derogationActive(periode, carriere);
    if (derogation !== null) {
      return derogation.ageAnnulation;
    }
    if (periode.age_table) {
      const propres = this.agesRegimes.ages(periode.age_table, carriere.generation);
      if (propres !== null && propres[1] !== null) {
        return propres[1];
      }
    }
    if (periode.age_taux_plein_par_generation) {
      const parGeneration = this.agesAnnulationDecote.age(carriere.generation);
      if (parGeneration !== null) {
        return parGeneration[0];
      }
    }
    return periode.age_taux_plein;
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
  decote(periode, carriere, anneeLiquidation) {
    const ageAnnulation = this.ageTauxPlein(periode, carriere);
    if (BAREMES_DECOTE_EN_TABLE.has(periode.bareme_decote)) {
      const table = periode.bareme_decote === "fonction_publique"
        ? this.decoteFonctionPublique
        : this.decoteRegimesSpeciaux;
      const parametres = table.parametres(
        this.anneeOuvertureDesDroits(periode, carriere, anneeLiquidation),
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
      const propre = this.agesRegimes.decote(periode.age_table, carriere.generation);
      if (propre !== null) {
        return [propre[0], ageAnnulation, propre[1]];
      }
    }
    if (periode.decote_par_generation) {
      const parGeneration = this.coefficientsMinoration.coefficient(
        carriere.annee_naissance,
      );
      if (parGeneration !== null) {
        return [parGeneration[0], ageAnnulation, parGeneration[1]];
      }
    }
    return [periode.decote_par_trimestre, ageAnnulation, null];
  }

  /**
   * Année où les conditions d'ouverture du droit sont réunies.
   *
   * C'est le millésime auquel se lisent les barèmes de décote en table. L'assuré
   * les réunit quand il atteint l'âge d'ouverture de son régime, au mois près ;
   * s'il liquide avant — carrière longue, catégorie active —, il les réunit au
   * plus tôt à la liquidation, et c'est cette année-là qui vaut.
   */
  anneeOuvertureDesDroits(periode, carriere, anneeLiquidation) {
    const ouverture = carriere.dateNaissance
      .plusMois(enMois(this.ageOuverture(periode, carriere))).annee;
    return Math.min(anneeLiquidation, ouverture);
  }

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
  /** Trimestres retranchés à la durée requise pour compter la décote. */
  retrancheDecote(periode, carriere) {
    const propre = this.dureePropre(periode, carriere);
    return propre === null ? 0 : propre[1];
  }

  /** Rang du mois où l'assuré réunit les conditions : l'âge d'ouverture
   * atteint, ou la liquidation si elle vient avant. */
  moisOuvertureDesDroits(periode, carriere) {
    let rang = carriere.dateNaissance.plusMois(
      enMois(this.ageOuverture(periode, carriere)),
    ).rang;
    if (carriere.age_liquidation !== null && carriere.age_liquidation !== undefined) {
      rang = Math.min(rang, carriere.dateLiquidation.rang);
    }
    return rang;
  }

  /** Durée requise propre au régime : [trimestres, retranchés, fiabilité] ou null. */
  dureePropre(periode, carriere) {
    const tables = periode.duree_requise_table ?? [];
    if (tables.length === 0 && !periode.duree_requise_calendrier) {
      return null;
    }
    const ouverture = this.moisOuvertureDesDroits(periode, carriere);
    for (const table of tables) {
      const ligne = this.dureesRequisesRegimes.ligne(table, carriere.generation, ouverture);
      if (ligne !== null) {
        return ligne;
      }
    }
    if (periode.duree_requise_calendrier) {
      const lu = this.calendriersDureeRequise.trimestres(
        periode.duree_requise_calendrier, ouverture,
      );
      if (lu !== null) {
        return [lu[0], 0, lu[1]];
      }
    }
    return null;
  }

  trimestresDeDecote(periode, carriere, trimestres, requis, ageLiquidation,
    ageAnnulation) {
    // LE MILITAIRE A LA SIENNE, et elle ne compte pas des âges. Le II de
    // l'article L. 14 lui oppose « le nombre de trimestres manquants […] pour
    // atteindre […] la durée de services militaires effectifs nécessaire pour
    // pouvoir bénéficier d'une liquidation de la pension […] augmentée d'une
    // durée de services effectifs de dix trimestres », dans la limite de dix
    // trimestres et non de vingt.
    const militaire = this.droitMilitaire(periode, carriere);
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
    const cible = requis - this.retrancheDecote(periode, carriere);
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

  /**
   * Abattement d'un régime en points liquidé avant le taux plein.
   *
   * « Avant le taux plein » est une condition de DURÉE autant que d'âge : une
   * complémentaire est servie sans abattement dès que l'assuré a le taux plein
   * au régime de base. L'Agirc-Arrco, elle, ne reprend pas la décote du régime
   * de base : elle publie ses propres COEFFICIENTS D'ANTICIPATION, en deux
   * tables — trimestres manquants, et âge — et retient la plus avantageuse.
   */
  /** Valeur de service du point écrite dans la fiche, à l'année demandée.
   *
   * La MSA est seule à publier celle de sa retraite proportionnelle. Une ancre
   * datée suffit : la loi (L. 161-23-1) la revalorise sur les prix.
   */
  valeurPointFiche(periode, annee) {
    if (periode.valeur_point_euros === null || periode.valeur_point_euros === undefined) {
      return 0.0;
    }
    return periode.valeur_point_euros * this.macro.coefficientPrix(
      periode.valeur_point_annee ?? annee, annee,
    );
  }

  /** Points de retraite proportionnelle agricole d'une année (R. 732-71).
   *
   * Escalier à quatre marches : quinze points jusqu'à 400 SMIC horaires, une
   * pente jusqu'à trente à 800 SMIC, un plateau à trente jusqu'à deux fois le
   * minimum contributif, puis une pente jusqu'au maximum M de l'année, que
   * R. 732-70 définit par (PM − AVTS) / (37,5 × valeur du point).
   */
  pointsMsa(periode, annee, revenu) {
    const smic = this.macro.smic_horaire.valeur(annee);
    const passAnnuel = this.macro.plafond_securite_sociale.valeur(annee);
    const valeurPoint = this.valeurPointFiche(periode, annee);
    if (smic <= 0 || passAnnuel <= 0 || valeurPoint <= 0) {
      return 0.0;
    }
    const avts = (periode.pension_forfaitaire_annuelle ?? 0.0)
      * this.macro.coefficientPrix(periode.pension_forfaitaire_annee ?? annee, annee);
    const minimumContributif = this.minimumContributif.valeurs(annee)[0];
    const maximum = (0.5 * passAnnuel - avts) / (37.5 * valeurPoint);
    if (revenu <= 400 * smic) {
      return 15.0;
    }
    if (revenu <= 800 * smic) {
      return Math.min(30.0, 15.0 + 15.0 * (revenu - 400 * smic) / (400 * smic));
    }
    if (revenu <= 2 * minimumContributif || passAnnuel <= 2 * minimumContributif) {
      return 30.0;
    }
    return Math.min(maximum, 30.0 + (maximum - 30.0)
      * (revenu - 2 * minimumContributif)
      / (passAnnuel - 2 * minimumContributif));
  }

  /**
   * Coefficient qui reprend la décote du régime de base — à deux pentes quand
   * la fiche en écrit deux : la CAVP minore de 1,25 % par trimestre jusqu'à
   * 65 ans et de 0,5 % de 65 ans à l'âge du taux plein. Les trimestres d'avant
   * le palier se comptent au premier taux. Voir le modèle Python.
   */
  abattementRegimeDeBase(periode, carriere, trimestres, requis, ageLiquidation,
    anneeLiquidation) {
    const [decote, ageAnnulation] = this.decote(periode, carriere, anneeLiquidation);
    if (decote === null) {
      return 1.0;
    }
    const trimestresDecote = this.trimestresDeDecote(
      periode, carriere, trimestres, requis, ageLiquidation, ageAnnulation,
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
  tauxPleinAnticipe(periode, carriere, ageLiquidation) {
    const parEnfant = periode.taux_plein_anticipe_par_enfant_annees ?? null;
    if (parEnfant === null || carriere.sexe !== "F" || carriere.nombre_enfants <= 0) {
      return false;
    }
    let anticipation = carriere.nombre_enfants * parEnfant;
    const maximum = periode.taux_plein_anticipe_maximum_annees ?? null;
    if (maximum !== null) {
      anticipation = Math.min(anticipation, maximum);
    }
    return ageLiquidation >= this.ageTauxPlein(periode, carriere) - anticipation - 1e-9;
  }

  /**
   * Minoration des trois régimes de l'IRCEC : 2,5 % pour chacune des deux
   * premières années manquantes jusqu'à l'âge du taux plein, 5 % au-delà, une
   * année entamée comptant entière ; ou la décote du régime de base si elle
   * est plus favorable. `ircec_age_seul` est le RACL de 2014 à 2024 : 5 % par
   * année, sans autre voie que l'âge. Voir le docstring du modèle Python.
   */
  abattementIrcec(periode, carriere, trimestres, requis, ageLiquidation,
    anneeLiquidation) {
    const ageTauxPlein = this.ageTauxPlein(periode, carriere);
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
    return Math.max(propre, this.abattementRegimeDeBase(
      periode, carriere, trimestres, requis, ageLiquidation, anneeLiquidation,
    ));
  }

  abattementPoints(periode, carriere, trimestres, requis, ageLiquidation,
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
          0.0, (this.ageTauxPlein(periode, carriere) - ageLiquidation) * 4,
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
      abattement = this.abattementIrcec(
        periode, carriere, trimestres, requis, ageLiquidation, anneeLiquidation,
      );
    } else {
      abattement = this.abattementRegimeDeBase(
        periode, carriere, trimestres, requis, ageLiquidation, anneeLiquidation,
      );
    }
    if (abattement < 1.0 && this.tauxPleinAnticipe(periode, carriere, ageLiquidation)) {
      abattement = 1.0;
    }

    // Abattu et majoré ne se rencontrent pas : les deux majorations de
    // l'arrêté supposent l'âge du taux plein ou la durée requise dépassés,
    // c'est-à-dire un coefficient d'anticipation déjà revenu à 1.
    if (abattement < 1.0) {
      return abattement;
    }
    return this.surcotePoints(
      periode, carriere, trimestres, requis, ageLiquidation, anneeLiquidation,
      trimestresRegime,
    );
  }

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
  coefficientSurcoteDatee(periode, carriere, trimestres, requis, supplementaires,
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
    if (!this.surcoteBaremes.connait(periode.surcote_bareme ?? "")) {
      return [1.0 + (periode.surcote_par_trimestre ?? 0.0) * dates.length, null];
    }
    return this.surcoteBaremes.coefficient(periode.surcote_bareme, dates);
  }

  surcotePoints(periode, carriere, trimestres, requis, ageLiquidation,
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
      return this.surcoteIrcantec(
        periode, carriere, trimestres, requis, ageLiquidation, anneeLiquidation,
      );
    }
    const taux = periode.surcote_par_trimestre;
    if (!taux) {
      return 1.0;
    }
    if (mode === "regime_general") {
      let supplementaires = Math.max(0, trimestres - requis);
      const ageOuverture = this.ageOuvertureCommun(periode, carriere);
      if (supplementaires <= 0 || ageLiquidation < ageOuverture
          || this.droitMilitaire(periode, carriere) !== null) {
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
      debut = this.ageTauxPlein(periode, carriere);
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
  surcoteIrcantec(periode, carriere, trimestres, requis, ageLiquidation,
    anneeLiquidation) {
    const ageTauxPlein = this.ageTauxPlein(periode, carriere);
    // 1° — le temps écoulé, en trimestres ENTIERS.
    const ecoules = Math.floor(
      (Math.max(0.0, ageLiquidation - ageTauxPlein) + 1e-9) * 4,
    );
    // 2° — la durée cotisée en deçà. Les trimestres au-delà de la durée
    // requise sont les DERNIERS de la carrière : les compter ici suppose que
    // la durée requise était atteinte avant l'âge du taux plein, sans quoi ils
    // tombent dans la fenêtre du 1° et y sont déjà payés.
    let supplementaires = 0;
    const ageOuverture = this.ageOuvertureCommun(periode, carriere);
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
   * Plafond en euros de la majoration pour enfants, ou ``null``.
   *
   * Les régimes de base servent 10 % sans plafond ; l'Agirc-Arrco borne la
   * majoration en euros — 2 367 € par an depuis le 1er novembre 2025 — et le
   * plafond suit la valeur de service du point. Il ne s'oppose qu'aux assurés
   * nés à compter du 2 août 1951 ; le modèle ne connaît que l'année de
   * naissance et retient les générations à partir de 1952.
   */
  plafondMajoration(code, periode, carriere, anneeLiquidation) {
    if (periode.plafond_majoration_enfants === null
        || periode.plafond_majoration_enfants === undefined) {
      return null;
    }
    if (carriere.annee_naissance < 1952) {
      return null;
    }
    const plafond = periode.plafond_majoration_enfants;
    const anneeReference = periode.plafond_majoration_annee;
    if (anneeReference === null || anneeReference === anneeLiquidation) {
      return plafond;
    }
    const servie = this.valeurDuPoint(code, anneeLiquidation);
    const publiee = this.valeurDuPoint(code, anneeReference);
    if (servie === null || publiee === null || publiee[0] <= 0) {
      return plafond * this.macro.coefficientPrix(anneeReference, anneeLiquidation);
    }
    return plafond * servie[0] / publiee[0];
  }

  /**
   * Trimestres dus au titre des enfants, et régime qui les porte.
   *
   * Le droit n'attribue pas ces trimestres au-dessus des régimes : il les donne
   * DANS un régime, et ils comptent donc aussi dans sa proratisation. On retient
   * celui qui accorde le plus ; à égalité, celui où l'assuré a validé le plus de
   * trimestres ; à égalité encore, le dernier code par ordre alphabétique, pour
   * que le résultat ne dépende pas de l'ordre d'une table de hachage.
   *
   * @returns {{regime: string, dispositif: string, trimestres: number,
   *            fiabilite: number}|null}
   */
  majorationPourEnfants(carriere, trimestresParRegime, anneeLiquidation) {
    if (carriere.nombre_enfants <= 0) {
      return null;
    }
    const candidats = [];
    for (const [code, valides] of trimestresParRegime) {
      if (!this.catalogue.contient(code)) {
        continue;
      }
      const regime = this.catalogue.obtenir(code);
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
      if (periode === null) {
        continue;
      }
      for (const dispositif of periode.avantages_non_contributifs) {
        // Un régime EN POINTS ne porte que la majoration de DURÉE, qui ne joue
        // que sur la durée d'assurance : la CNAVPL depuis 2010 (L. 643-1-1).
        // Une bonification entre aux services, qu'il n'a pas.
        if (periode.type_calcul !== "annuites" && dispositif !== MAJORATION_DE_DUREE) {
          continue;
        }
        const accorde = this.majorationsEnfants.parEnfant(
          dispositif, carriere.sexe, carriere.annee_naissance, anneeLiquidation,
          carriere.nombre_enfants,
        );
        if (accorde === null) {
          continue;
        }
        candidats.push([
          accorde[0] * carriere.nombre_enfants, valides, dispositif, code,
          accorde[2], accorde[1] * carriere.nombre_enfants,
        ]);
      }
    }
    if (candidats.length === 0) {
      return null;
    }
    candidats.sort((a, b) => (a[0] - b[0]) || (a[1] - b[1])
      || (a[3] < b[3] ? -1 : 1));
    const retenu = candidats[candidats.length - 1];
    return {
      regime: retenu[3], dispositif: retenu[2], trimestres: retenu[0],
      services: retenu[5], fiabilite: retenu[4],
    };
  }

  /**
   * Points que ce régime attribue sans cotisation à la liquidation, et la
   * fiabilité de la durée requise qui les conditionne : cent points par année
   * de chef d'exploitation d'avant 2003 à la RCO agricole (D. 732-154), dans
   * la limite de 37,5 ans moins les années de RCO, à qui a dix-sept ans et
   * demi comme chef (D. 732-151) et le taux plein de son régime de base
   * (L. 732-56, II, 2°) — la durée requise jusqu'au 31 août 2023, la pension
   * liquidée au taux plein depuis. Voir `_points_gratuits` dans le Python.
   */
  pointsGratuits(periode, carriere, assurance, trimestres, ageLiquidation) {
    const regle = periode.points_gratuits;
    const base = this.catalogue.obtenir(regle.regime);
    const periodeBase = base.periode(
      Math.min(carriere.anneeLiquidation, derniereAnnee(base)));
    if (periodeBase === null) {
      return [0.0, null];
    }
    const valides = (code, avant = null) => {
      let total = 0;
      for (const [annee, nombre] of assurance.get(code) ?? []) {
        if (avant === null || annee < avant) {
          total += Math.min(nombre, carriere.plafondTrimestres(annee));
        }
      }
      return total;
    };
    if (valides(regle.regime) < regle.annees_minimum * 4) {
      return [0.0, null];
    }
    const [requis, fiabilite] = this.dureeRequise(periodeBase, carriere);
    let tauxPlein = trimestres >= requis;
    const [anneeDepuis, moisDepuis] = regle.taux_plein_depuis;
    if (!tauxPlein
        && carriere.dateLiquidation.rang >= new DateMois(anneeDepuis, moisDepuis).rang) {
      tauxPlein = ageLiquidation >= this.ageTauxPlein(periodeBase, carriere);
    }
    if (!tauxPlein) {
      return [0.0, fiabilite];
    }
    const retenus = Math.min(
      valides(regle.regime, regle.avant),
      Math.max(0.0, regle.annees_maximum * 4 - valides(periode.regime)),
    );
    return [regle.points_par_annee * retenus / 4, fiabilite];
  }

  calculer(carriere, ignorerPenaliteAge = false, avantagesNonContributifs = true,
    avpf = true, liquiderSuccessions = true, pointsGratuits = null) {
    // `pointsGratuits` nul suit `avantagesNonContributifs` : voir le Python.
    const avecPointsGratuits = pointsGratuits ?? avantagesNonContributifs;
    const anneeLiquidation = carriere.anneeLiquidation;
    const ageLiquidation = carriere.age_liquidation || 0.0;

    let trimestres = carriere.trimestresActuels;

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

    // Cotisations cumulées par régime, pour les régimes en points dont on n'a
    // pas le prix d'achat du point ; points acquis pour les autres.
    const cumulCotisations = new Map();
    const pointsAcquis = new Map();
    // La majoration pour enfants des points de l'Agirc-Arrco dépend de leur
    // année d'ACQUISITION : voir `crediter` dans le Python.
    const majorationPoints = new Map();
    const pointsMajores = new Map();
    const crediter = (code, annee, points) => {
      pointsAcquis.set(code, (pointsAcquis.get(code) ?? 0.0) + points);
      const taux = this.majorationsEnfantsPoints.taux(code, annee, carriere.nombre_enfants);
      if (taux !== null) {
        majorationPoints.set(code, (majorationPoints.get(code) ?? 0.0) + points * taux);
        pointsMajores.set(code, (pointsMajores.get(code) ?? 0.0) + points);
      }
    };
    const fiabilitePoints = new Map();
    // Trimestres qu'un régime à la durée crédite, et ceux d'entre eux
    // accomplis avant l'âge qui lève son plafond : voir le Python.
    const trimestresPlafonnables = new Map();
    // Durée d'assurance validée dans chaque régime, PÉRIODES ASSIMILÉES
    // COMPRISES : le coefficient de proratisation porte sur la durée
    // d'assurance, pas sur les seules années cotisées.
    const trimestresParRegime = new Map();
    // SERVICES accomplis dans chaque régime. La fonction publique ne proratise
    // pas sa pension sur la durée d'assurance mais sur les services et
    // bonifications (L. 13 du code des pensions), et l'article L. 9 écarte « le
    // temps passé dans une position statutaire ne comportant pas
    // l'accomplissement de services effectifs au sens de l'article L. 5 », hors
    // la liste fermée qu'il énumère. Le moteur créditait ce prorata de TOUTE
    // période validée : une carrière de fonctionnaire coupée de cinq ans de
    // chômage servait exactement la même pension qu'une carrière pleine.
    const servicesParRegime = new Map();
    // Ce qui reste du budget de services que L. 9 ouvre dans une limite — trois
    // ans par enfant pour le congé parental. Il se tient sur toute la carrière,
    // et non année par année.
    const budgetServicesPlafonnes = new Map();
    // Durée COTISÉE dans chaque régime : c'est elle, et non la durée
    // d'assurance, qui proratise la majoration du minimum contributif au titre
    // des périodes cotisées (D. 351-2-2).
    const trimestresCotisesParRegime = new Map();
    // Dernière année cotisée dans chaque régime : elle désigne, dans une
    // chaîne de succession, la caisse qui liquide.
    const derniereAnneeParRegime = new Map();
    // Les trois mêmes, ANNÉE PAR ANNÉE. Deux activités cumulées peuvent
    // verser au même régime, ou à deux régimes liquidés ensemble : leurs
    // trimestres s'y additionnent sans dépasser les trimestres civils de
    // l'année. Une année d'une seule activité n'est pas touchée.
    const parAnnee = { assurance: new Map(), services: new Map(), cotises: new Map() };
    // Ce qui ne tient à aucune année — la majoration pour enfants — et
    // s'ajoute donc hors plafond annuel.
    const horsAnnee = { assurance: new Map(), services: new Map(), cotises: new Map() };
    const crediterTrimestres = (table, code, annee, trimestres) => {
      if (!parAnnee[table].has(code)) {
        parAnnee[table].set(code, new Map());
      }
      const annees = parAnnee[table].get(code);
      annees.set(annee, (annees.get(annee) ?? 0) + trimestres);
    };
    const cumulPlafonne = (table, membres) => {
      const sommes = new Map();
      let total = 0;
      for (const membre of membres) {
        for (const [annee, trimestres] of parAnnee[table].get(membre) ?? []) {
          sommes.set(annee, (sommes.get(annee) ?? 0) + trimestres);
        }
        total += horsAnnee[table].get(membre) ?? 0;
      }
      for (const [annee, somme] of sommes) {
        total += Math.min(somme, carriere.plafondTrimestres(annee));
      }
      return total;
    };
    for (const ligne of carriere.lignes) {
      const retenusLigne = carriere.trimestresRetenus(ligne);
      if (retenusLigne <= 0) {
        continue;
      }
      let servicesLigne = ligne.services_fonction_publique ? retenusLigne : 0;
      const plafond = ligne.services_plafond_trimestres_par_enfant;
      if (servicesLigne > 0 && plafond > 0) {
        const restant = budgetServicesPlafonnes.get(plafond)
          ?? plafond * carriere.nombre_enfants;
        servicesLigne = Math.min(servicesLigne, restant);
        budgetServicesPlafonnes.set(plafond, restant - servicesLigne);
      }
      for (const code of this.affiliations.regimes(
        ligne.affiliation, ligne.annee, carriere.dateEntree(ligne.affiliation),
        ligne.cotise ? ligne.revenu : ligne.revenu_reference,
        this.macro.plafond_securite_sociale.valeur(ligne.annee),
      )) {
        if (!this.catalogue.contient(code)) {
          continue;
        }
        crediterTrimestres("assurance", code, ligne.annee, retenusLigne);
        if (servicesLigne > 0) {
          crediterTrimestres("services", code, ligne.annee, servicesLigne);
        }
        if (ligne.cotise) {
          crediterTrimestres("cotises", code, ligne.annee, retenusLigne);
        }
      }
    }
    for (const [table, cible] of [["assurance", trimestresParRegime],
      ["services", servicesParRegime], ["cotises", trimestresCotisesParRegime]]) {
      for (const code of parAnnee[table].keys()) {
        cible.set(code, cumulPlafonne(table, [code]));
      }
    }

    // Les trimestres accordés au titre des enfants ne flottent pas au-dessus des
    // régimes : le droit les attribue DANS un régime, et ils comptent donc aussi
    // dans sa proratisation, pas seulement dans la décote tous régimes
    // confondus. Le régime retenu est celui qui accorde le plus — exact pour une
    // carrière mono-affiliée, approché pour un polypensionné.
    const majorationEnfants = avantagesNonContributifs
      ? this.majorationPourEnfants(carriere, trimestresParRegime, anneeLiquidation)
      : null;
    // Les BONIFICATIONS, à part des services : seules elles peuvent porter le
    // taux au-delà du maximum (`taux_maximum_bonifie`).
    const bonificationsParRegime = new Map();
    if (majorationEnfants !== null) {
      bonificationsParRegime.set(majorationEnfants.regime, majorationEnfants.services);
    }
    if (majorationEnfants !== null) {
      // LA DURÉE ET LES SERVICES NE SONT PAS LA MÊME CASE, et la majoration se
      // range dans les deux : tout ce qui est accordé joue sur la durée
      // d'assurance, tous régimes et dans le régime ; la seule part `services`
      // entre aux services, qui proratisent la pension de la fonction publique.
      trimestres += majorationEnfants.trimestres;
      trimestresParRegime.set(
        majorationEnfants.regime,
        trimestresParRegime.get(majorationEnfants.regime) + majorationEnfants.trimestres,
      );
      servicesParRegime.set(
        majorationEnfants.regime,
        (servicesParRegime.get(majorationEnfants.regime) ?? 0)
          + majorationEnfants.services,
      );
      horsAnnee.assurance.set(majorationEnfants.regime, majorationEnfants.trimestres);
      horsAnnee.services.set(majorationEnfants.regime, majorationEnfants.services);
      fiabiliteGlobale = Math.min(fiabiliteGlobale, majorationEnfants.fiabilite);
    }

    for (const ligne of carriere.lignes) {
      // Une ligne postérieure à la liquidation décrit une activité exercée
      // APRÈS le départ : elle n'ouvre pas de droits dans la pension qu'on
      // liquide. L'année du départ, elle, ouvre ceux de ses mois qui l'ont
      // précédé — ni zéro ni douze, mais le compte juste.
      const part = carriere.partRetenueLigne(ligne);
      if (part <= 0) {
        continue;
      }
      if (!ligne.cotise && ligne.familles_cotisantes.length === 0) {
        continue;
      }
      // Pendant une période indemnisée, seuls les régimes complémentaires
      // encaissent, et sur le salaire d'avant l'interruption.
      let baseLigne = ligne.cotise ? ligne.revenu : ligne.revenu_reference;
      if (part < ligne.fraction_annee) {
        baseLigne *= part / ligne.fraction_annee;
      }
      const famillesAdmises = ligne.cotise ? null : new Set(ligne.familles_cotisantes);
      for (const code of this.affiliations.regimes(
        ligne.affiliation, ligne.annee, carriere.dateEntree(ligne.affiliation),
        ligne.cotise ? ligne.revenu : ligne.revenu_reference,
        this.macro.plafond_securite_sociale.valeur(ligne.annee),
      )) {
        if (!this.catalogue.contient(code)) {
          continue;
        }
        const regime = this.catalogue.obtenir(code);
        if (famillesAdmises !== null && !famillesAdmises.has(regime.famille)) {
          continue;
        }
        derniereAnneeParRegime.set(
          code, Math.max(derniereAnneeParRegime.get(code) ?? 0, ligne.annee),
        );
        for (const periode of regime.periodesActives(ligne.annee)) {
          // BARÈME D'UN AUTRE RÉGIME : une tranche que tous les affiliés ne
          // cotisent pas forme une fiche à part, dont les points restent ceux
          // du régime d'origine. Voir `points_de`.
          const bareme = periode.points_de ?? code;
          // Les bornes d'assiette et le repère en points sont ANNUELS : une
          // année incomplète ne les atteint qu'à proportion de ses mois, comme
          // le plafond lui-même.
          const passPlein = this.macro.plafond_securite_sociale.valeur(ligne.annee);
          const pass = passPlein * part;
          let [borneBasse, borneHaute] = periode.bornesAssietteEnEuros(passPlein);
          if (part < 1.0) {
            borneBasse *= part;
            borneHaute = borneHaute === null ? null : borneHaute * part;
          }
          // Traitement seul, primes seules — celles du RAFP dans la limite de
          // 20 % du traitement : voir `partDuRevenu`.
          let base = periode.partDuRevenu(baseLigne, ligne.part_primes);
          // Commissions de la CAVAMAC, produits de l'office de la CPRN : le
          // facteur reconstitue l'assiette depuis le revenu, avant les bornes.
          if (periode.assiette_facteur_revenu !== null
              && periode.assiette_facteur_revenu !== undefined) {
            base *= periode.assiette_facteur_revenu;
          }
          // Le marin cotise sur le salaire forfaitaire de sa catégorie : voir
          // `ConstructeurCompte.cotisationAnnuelle`.
          if (periode.assiette_grille) {
            const forfaitGrille = this.grilles.forfait(
              periode.assiette_grille, ligne.annee, ligne.revenuAnnualise,
              (a) => salaireMoyenAnnuel(this.macro, a),
            );
            if (forfaitGrille !== null) {
              base = forfaitGrille[0] * part;
            }
          }
          // L'assiette minimale du régime de base d'un libéral : 450 SMIC
          // horaires depuis 2023 (D. 642-4), qui ouvrent leurs points.
          base = Math.max(base, this.assietteMinimale([code], ligne));
          const plafond = borneHaute === null ? base : borneHaute;
          let assiette = Math.max(0.0, Math.min(base, plafond) - borneBasse);
          const repere = periode.repereAssiette(
            pass, this.macro.smic_horaire.valeur(ligne.annee),
          ) * (periode.assiette_repere_smic !== null
            && periode.assiette_repere_smic !== undefined ? part : 1.0);
          if (periode.assiette_forfaitaire) {
            // Assiette FORFAITAIRE : le régime des cultes cotise sur un
            // forfait égal au SMIC mensuel, quel que soit le revenu —
            // inconditionnel, là où assiette_plancher ne relève que les
            // assiettes trop basses.
            assiette = repere;
          } else if (periode.assiette_plancher && assiette < repere) {
            // Assiette minimale : la complémentaire agricole cotise sur
            // 1 820 SMIC même quand le revenu est en dessous.
            assiette = repere;
          }
          if (!periode.assiette_forfaitaire) {
            // Assiette minimale en plafonds : la CARPIMKO appelle depuis 2026
            // sa cotisation sur un demi-plafond au moins, et les points suivent
            // ce qui est appelé. Le plafond est déjà proratisé sur les mois.
            assiette = Math.max(assiette, periode.assietteMinimale(pass));
          }
          // La cotisation forfaitaire s'ajoute à la proportionnelle, et elle est
          // due quel que soit le revenu — même convention que dans compte.js.
          let forfait = 0.0;
          if (periode.cotisation_forfaitaire_euros !== null
              && periode.cotisation_forfaitaire_euros !== undefined) {
            const reference = periode.cotisation_forfaitaire_annee || ligne.annee;
            forfait = periode.cotisation_forfaitaire_euros
              * this.macro.coefficientPrix(reference, ligne.annee);
          }
          let cotisation = assiette * periode.taux_cotisation_retraite + forfait;
          // COTISATION PAR CLASSES : la Cipav, avant 2023, appelait le montant
          // du palier où tombait le revenu, et non une fraction d'une assiette.
          // Ce montant achète des points comme n'importe quelle cotisation —
          // « 3 600 € / 47,40 € = 75,9 points », écrit la caisse —, et c'est
          // donc ici, avant la conversion, qu'il se substitue.
          if (periode.cotisation_par_classes) {
            const millesime = this.classes.anneeGrille(code, ligne.annee);
            const reference = millesime === null
              ? 0.0
              : this.macro.plafond_securite_sociale.valeur(millesime);
            const parClasse = reference <= 0 ? null : this.classes.cotisation(
              code, ligne.annee, base,
              this.macro.plafond_securite_sociale.valeur(ligne.annee) / reference,
            );
            if (parClasse !== null) {
              cotisation = parClasse[0] * part;
            }
          }
          if (periode.bareme_points === "msa_proportionnelle") {
            // BARÈME NOMMÉ : R. 732-71 écrit l'escalier, `pointsMsa` le sert.
            // C'est l'ASSIETTE qui y entre : la cotisation est due sur six
            // cents SMIC horaires au moins et sur un plafond au plus.
            const [echelleMsa, fiabiliteEchelleMsa] = this.conversionsPoints
              .echelle(bareme, ligne.annee, anneeLiquidation);
            crediter(code, ligne.annee,
              this.pointsMsa(periode, ligne.annee, assiette) * part * echelleMsa);
            fiabilitePoints.set(code, Math.min(
              fiabilitePoints.get(code) ?? Fiabilite.CERTIFIEE, regime.fiabilite,
              fiabiliteEchelleMsa,
            ));
            continue;
          }
          if (periode.points_par_trimestre_valide !== null
              && periode.points_par_trimestre_valide !== undefined) {
            // POINTS PAR TRIMESTRE VALIDÉ, sans égard au montant. Le régime de
            // base des libéraux d'avant 2004 ne servait pas une pension
            // proportionnelle au revenu mais une ALLOCATION : un quinzième de
            // l'AVTS par année cotisée, la même pour tous. La réforme de 2003
            // l'a convertie en points « à raison de cent points par trimestre »
            // (D. 643-1), et c'est cette conversion qui porte le droit
            // d'avant 2004.
            const [echelleTrim, fiabiliteEchelleTrim] = this.conversionsPoints
              .echelle(bareme, ligne.annee, anneeLiquidation);
            let points = periode.points_par_trimestre_valide
              * carriere.trimestresRetenus(ligne);
            if (periode.trimestres_maximum !== null
                && periode.trimestres_maximum !== undefined) {
              // Le plafond se lit sur toute la durée : on note ici les
              // trimestres de la ligne, et ceux d'entre eux qui précèdent l'âge
              // qui le lève.
              if (!trimestresPlafonnables.has(code)) {
                trimestresPlafonnables.set(code, [0.0, 0.0]);
              }
              const suivi = trimestresPlafonnables.get(code);
              suivi[0] += carriere.trimestresRetenus(ligne);
              if (periode.trimestres_maximum_leve_avant_age !== null
                  && periode.trimestres_maximum_leve_avant_age !== undefined) {
                suivi[1] += trimestresDeLaLigneEntre(
                  carriere, ligne, new DateMois(carriere.annee_naissance, 1),
                  carriere.dateNaissance.plusMois(
                    enMois(periode.trimestres_maximum_leve_avant_age)),
                );
              }
            }
            if (periode.points_ajustement_par_forfait !== null
                && periode.points_ajustement_par_forfait !== undefined
                && forfait > 0) {
              // Les points d'AJUSTEMENT de l'ASV des médecins : 18 fois la
              // cotisation proportionnelle sur le forfait, neuf au plus
              // (décret n° 2011-1644, art. 3). Ils suivent le revenu, là où
              // les 27 points du forfait ne suivent que la durée.
              let ajustement = periode.points_ajustement_par_forfait * assiette
                * periode.taux_cotisation_retraite / forfait;
              if (periode.points_ajustement_maximum !== null
                  && periode.points_ajustement_maximum !== undefined) {
                ajustement = Math.min(ajustement,
                  periode.points_ajustement_maximum * part);
              }
              points += ajustement;
            }
            crediter(code, ligne.annee, points * echelleTrim);
            fiabilitePoints.set(code, Math.min(
              fiabilitePoints.get(code) ?? Fiabilite.CERTIFIEE, regime.fiabilite,
              fiabiliteEchelleTrim,
            ));
            continue;
          }
          if (periode.points_maximum !== null && periode.points_maximum !== undefined
              && repere > 0) {
            // Barème écrit en POINTS et non en prix d'achat : le régime annonce
            // combien de points ouvre une assiette donnée. Le nombre de points
            // ne dépend alors pas du taux de cotisation, et c'est heureux : ce
            // sont les barèmes qui sont publiés, pas les prix d'achat.
            const [echelleBareme, fiabiliteEchelleBareme] = this.conversionsPoints
              .echelle(bareme, ligne.annee, anneeLiquidation);
            crediter(code, ligne.annee,
              periode.points_maximum * assiette / repere * echelleBareme);
            fiabilitePoints.set(code, Math.min(
              fiabilitePoints.get(code) ?? Fiabilite.CERTIFIEE, regime.fiabilite,
              fiabiliteEchelleBareme,
            ));
            continue;
          }
          const achat = (periode.type_calcul === "points" || periode.type_calcul === "mixte")
            ? this.valeursPoint.achat(bareme, ligne.annee)
            : null;
          if (achat !== null) {
            const [reference, tauxAppel, fiabiliteAchat] = achat;
            let pointsAnnee = cotisation / (tauxAppel * reference);
            if (periode.points_minimum_annuels !== null
                && periode.points_minimum_annuels !== undefined) {
              // Garantie minimale de points de l'Agirc : tout cadre cotisant en
              // acquiert au moins 120 par an de 1989 à 2018, même quand sa
              // tranche B est nulle.
              pointsAnnee = Math.max(pointsAnnee, periode.points_minimum_annuels);
            }
            // Changement d'unité entre l'achat et le service : les points
            // Arrco d'avant 1999 sont ceux de l'UNIRS, et valent 0,387464 point
            // du régime unifié. Sans cette conversion, cent euros cotisés en
            // 1998 produisaient 30,31 € de pension quand les mêmes cent euros
            // de 1999 n'en produisaient que 11,15.
            const [echelle, fiabiliteEchelle] = this.conversionsPoints
              .echelle(bareme, ligne.annee, anneeLiquidation);
            crediter(code, ligne.annee, pointsAnnee * echelle);
            fiabilitePoints.set(code, Math.min(
              fiabilitePoints.get(code) ?? Fiabilite.CERTIFIEE, fiabiliteAchat,
              fiabiliteEchelle,
            ));
          } else {
            cumulCotisations.set(code, (cumulCotisations.get(code) ?? 0.0)
              + cotisation * this.macro.coefficientPrix(ligne.annee, anneeLiquidation));
          }
        }
      }
    }

    // LE PLAFOND DE LA DURÉE, LEVÉ AVANT UN ÂGE : cent vingt trimestres au plus
    // aux mines, sauf ceux accomplis avant cinquante-cinq ans (article 136 du
    // décret n° 46-2769). Voir le Python.
    for (const [code, [total, avantAge]] of trimestresPlafonnables) {
      const regime = this.catalogue.obtenir(code);
      const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
      if (periode === null || periode.trimestres_maximum === null
          || periode.trimestres_maximum === undefined || total <= 0) {
        continue;
      }
      const retenus = Math.min(total, Math.max(periode.trimestres_maximum, avantAge));
      if (retenus < total && pointsAcquis.has(code)) {
        const rapport = retenus / total;
        pointsAcquis.set(code, pointsAcquis.get(code) * rapport);
        if (majorationPoints.has(code)) {
          majorationPoints.set(code, majorationPoints.get(code) * rapport);
          pointsMajores.set(code, pointsMajores.get(code) * rapport);
        }
      }
    }

    // POINTS GRATUITS : la RCO agricole attribue à la liquidation des points
    // pour les années de chef d'exploitation d'avant sa création. Ils entrent au
    // compte de points du régime comme des points acquis, et la cascade les
    // isole plus bas. Voir `pointsGratuits`.
    // Points attribués, et année avant laquelle comptent les années.
    const gratuitsAttribues = new Map();
    if (avecPointsGratuits) {
      for (const [base, attribuants] of this.pointsGratuitsParBase) {
        if (!parAnnee.assurance.has(base)) {
          continue;
        }
        for (const code of attribuants) {
          const regime = this.catalogue.obtenir(code);
          const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
          if (periode === null || periode.points_gratuits === null
              || periode.points_gratuits === undefined) {
            continue;
          }
          const [gratuits, fiabiliteDuree] = this.pointsGratuits(
            periode, carriere, parAnnee.assurance, trimestres, ageLiquidation,
          );
          if (gratuits <= 0) {
            continue;
          }
          gratuitsAttribues.set(code, [gratuits, periode.points_gratuits.avant]);
          pointsAcquis.set(code, (pointsAcquis.get(code) ?? 0.0) + gratuits);
          fiabilitePoints.set(code, Math.min(
            fiabilitePoints.get(code) ?? Fiabilite.CERTIFIEE,
            regime.fiabilite,
            fiabiliteDuree === null ? Fiabilite.CERTIFIEE : fiabiliteDuree,
          ));
        }
      }
    }

    const codes = [...new Set([...cumulCotisations.keys(), ...pointsAcquis.keys()])].sort();

    // Durée requise de référence : celle du régime de base. C'est elle qui
    // commande le taux plein, donc aussi l'abattement des complémentaires —
    // un assuré au taux plein liquide sa complémentaire sans abattement, quel
    // que soit son âge.
    let requisReference = 0;
    // Âge d'ouverture des droits le plus précoce parmi les régimes de base de
    // la carrière. Un polypensionné liquide en réalité chaque pension à l'âge
    // de son régime ; le modèle liquide tout à la fois, et retient donc l'âge
    // du régime le plus précoce.
    let ageOuvertureReference = null;
    // Un régime et celui qui lui succède liquident ensemble, sous les règles
    // de la caisse qui aurait le dossier : les autres membres du groupe sont
    // sautés partout où un régime liquide. À FAUX, chaque nom de caisse est
    // liquidé sur ses seules années — variante qui ne sert qu'à mesurer.
    const groupes = liquiderSuccessions
      ? this.groupesDeSuccession(codes, anneeLiquidation, derniereAnneeParRegime,
                                 carriere)
      : new Map();
    // DEUX PASSES, ET LA SECONDE NE SERT QU'À QUI N'A QUE DES POINTS. Les
    // régimes en annuités commandent ; mais une carrière entière en points
    // n'en a aucun, et `ageOuvertureReference` restait nul — aucun âge ne lui
    // était opposé, et un chef d'exploitation pouvait liquider à cinquante ans
    // sans que rien ne le refuse. `requisReference` retombait de son côté sur
    // 160, une durée que plus aucune génération ne doit, et c'est elle que
    // l'abattement du régime en points opposait.
    for (const calculs of [["annuites"], ["points", "mixte"]]) {
      for (const code of codes) {
        if ((groupes.get(code) ?? [code])[0] !== code) {
          continue;
        }
        const regime = this.catalogue.obtenir(code);
        const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
        if (periode === null || !calculs.includes(periode.type_calcul)) {
          continue;
        }
        if (periode.abattement_points === "agirc_arrco"
          || periode.abattement_points === "ircantec") {
          continue;
        }
        // Une complémentaire qui a SES âges ne dit pas quand le droit s'ouvre :
        // c'est le régime de base qu'elle accompagne qui le dit. Un régime de
        // base en annuités qui a les siens — SNCF, RATP, IEG — le dit, lui.
        if (periode.age_table && periode.type_calcul !== "annuites") {
          continue;
        }
        requisReference = Math.max(requisReference, this.dureeRequise(periode, carriere)[0]);
        const ageRegime = this.ageOuverture(periode, carriere);
        ageOuvertureReference = ageOuvertureReference === null
          ? ageRegime
          : Math.min(ageOuvertureReference, ageRegime);
      }
      if (ageOuvertureReference !== null) {
        break;
      }
    }
    requisReference = requisReference || 160;

    // Trimestres réellement COTISÉS, tous régimes : ils commandent la carrière
    // longue et la majoration du minimum contributif.
    const trimestresCotises = carriere.trimestresCumules(carriere.lignes.filter(
      (ligne) => ligne.cotise && ligne.annee <= anneeLiquidation,
    ));

    // Le droit ouvre-t-il cette liquidation à cet âge ? La question n'était pas
    // posée : le modèle servait une pension décotée à qui ne pouvait pas encore
    // liquider, ce qui n'est ni le droit ni un contrefactuel utile.
    let motifOuverture = "age_legal";
    let liquidationOuverte = true;
    if (ageOuvertureReference !== null && ageLiquidation < ageOuvertureReference) {
      const anticipe = this.carriereLongue.ageDeDepart(
        carriere, anneeLiquidation,
        this.carriereLongue.cotisesReputes(
          carriere, trimestresCotises,
          majorationEnfants !== null ? majorationEnfants.trimestres : 0,
        ),
        requisReference,
      );
      if (anticipe !== null && ageLiquidation >= anticipe[0]) {
        motifOuverture = "carriere_longue";
        ageOuvertureReference = anticipe[0];
        fiabiliteGlobale = Math.min(fiabiliteGlobale, anticipe[1]);
      } else {
        motifOuverture = "non_ouverte";
        liquidationOuverte = false;
      }
    }

    for (const code of codes) {
      const cumul = cumulCotisations.get(code) ?? 0.0;
      const regime = this.catalogue.obtenir(code);
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
          ? this.baremesTrimestre.valeurs(periode.bareme_trimestre, carriere.dateLiquidation)
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
          let valeur = this.valeurDuPoint(periode.points_de ?? code, anneeLiquidation);
          if (valeur === null && periode.valeur_point_euros !== null
              && periode.valeur_point_euros !== undefined) {
            // Valeur de service écrite dans la fiche, faute d'une série
            // certifiable dans `valeurs_point.csv`.
            valeur = [
              this.valeurPointFiche(periode, anneeLiquidation), Fiabilite.MOYENNE,
            ];
          }
          if (valeur !== null) {
            const [service, fiabiliteService] = valeur;
            // COEFFICIENT DE DURÉE de la proportionnelle agricole : la pension
            // vaut « points × valeur du point × 37,5 / durée requise ».
            let coefficientDuree = 1.0;
            if (periode.bareme_points === "msa_proportionnelle") {
              const [requisMsa, fiabiliteDureeMsa] = this.dureeRequise(periode, carriere);
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
          const requisForfait = this.dureeRequise(periode, carriere)[0];
          const [proratisationForfait, fiabiliteProrataForfait] = this
            .dureeProratisation(periode, carriere, requisForfait);
          if (fiabiliteProrataForfait !== null) {
            fiabiliteRegime = Math.min(fiabiliteRegime, fiabiliteProrataForfait);
          }
          const acquis = Math.min(
            trimestresParRegime.get(code) ?? 0, proratisationForfait,
          );
          if (proratisationForfait > 0 && acquis > 0) {
            const forfait = periode.pension_forfaitaire_annuelle
              * this.macro.coefficientPrix(
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
          const [rendement, fiabiliteRendement] = this.rendements.rendement(
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
          abattement = this.abattementPoints(
            periode, carriere, trimestres, requisReference, ageLiquidation,
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
          const valeurSeuil = this.valeurDuPoint(periode.points_de ?? code, anneeLiquidation);
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
        ? periode.pension_forfaitaire_annuelle * this.macro.coefficientPrix(
          periode.pension_forfaitaire_annee ?? anneeLiquidation, anneeLiquidation,
        )
        : this.salaireDeReference(
          code, carriere, periode, anneeLiquidation, plafonner,
          carriere.annee_naissance, avpf, membres,
          majorationEnfants !== null ? carriere.nombre_enfants : 0,
        );
      const [requis, fiabiliteDuree] = this.dureeRequise(periode, carriere);
      if (fiabiliteDuree !== null) {
        fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteDuree);
      }
      trimestresRequis = Math.max(trimestresRequis, requis);
      // Le dénominateur de la PRORATISATION n'est pas la durée requise :
      // l'article R. 351-6 en fixe une autre, plus courte pour les générations
      // d'avant 1949. Confondre les deux retirait à un assuré né en 1945 avec
      // 156 trimestres les 2,5 % que 156/160 lui coûte, là où 156/154 lui donne
      // le coefficient plein.
      const [proratisation, fiabiliteProratisation] = this.dureeProratisation(
        periode, carriere, requis,
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
        this.catalogue.obtenir(code).famille === "fonction_publique"
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
        const [decote, ageAnnulationPeriode, fiabiliteDecote] = this.decote(
          periode, carriere, anneeLiquidation,
        );
        ageAnnulation = ageAnnulationPeriode;
        trimestresDecote = this.trimestresDeDecote(
          periode, carriere, trimestres, requis, ageLiquidation, ageAnnulation,
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
        const ageOuverture = this.ageSurcote(periode, carriere);
        if (periode.surcote_par_trimestre && supplementaires > 0
            && ageLiquidation >= ageOuverture
            && this.droitMilitaire(periode, carriere) === null) {
          if (periode.surcote_bareme) {
            // Barème DATÉ : chaque trimestre civil de surcote au taux en
            // vigueur quand il a été accompli, depuis le trimestre qui suit
            // l'âge légal (D. 351-1-4).
            const [coefficient, fiabiliteSurcote] = this.coefficientSurcoteDatee(
              periode, carriere, trimestres, requis, supplementaires, ageOuverture,
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
            || ageLiquidation >= this.ageTauxPlein(periode, carriere),
          surcote: coefficientSurcote,
        });
      }
      if (periode.avantages_non_contributifs.includes("minimum_garanti")) {
        // Depuis la loi du 9 novembre 2010, le minimum garanti n'est dû qu'au
        // taux plein. Les assurés qui atteignaient l'âge d'ouverture de leurs
        // droits avant 2011 gardent le droit inconditionnel, et le c de L. 17
        // sous quinze ans ; les autres ont le d.
        const ageOuverturePeriode = this.ageOuverture(periode, carriere);
        const ancienDroit = carriere.annee_naissance + ageOuverturePeriode < 2011;
        // L'âge d'annulation de la décote qui ouvre le minimum est minoré à
        // titre transitoire, selon l'année où l'âge d'ouverture est atteint
        // (décret n° 2010-1744, article 3).
        const fonctionPublique = this.catalogue.obtenir(code).famille === "fonction_publique";
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
        fiabilite: Math.min(...membres.map((m) => this.catalogue.obtenir(m).fiabilite)),
      });
    }

    let total = pensions.reduce((somme, p) => somme + p.montant, 0.0);

    // CE QUI N'EST PAS DE LA RÉPARTITION EST SERVI À PART. Le RAFP et les
    // anciennes assurances sociales sont des régimes PROVISIONNÉS : leur rente
    // sort d'un placement, pas de la cotisation des actifs. Une réforme qui
    // remplace la répartition par des comptes notionnels ne les atteint pas, et
    // les scénarios notionnels les isolent déjà. Les laisser dans le total du
    // scénario 1 revenait à comparer un total qui les contient à quatre totaux
    // qui ne les contiennent pas.
    //
    // Le calcul lui-même n'est pas touché : l'écrêtement du minimum contributif
    // et l'ASPA continuent de regarder TOUTES les pensions, comme le fait le
    // droit. Seul le total rendu est celui de la répartition.
    const horsRepartition = this.parametres.isoler_capitalisation
      ? pensions.reduce(
        (somme, p) => somme + (this.catalogue.obtenir(p.regime).hors_repartition
          ? p.montant : 0.0), 0.0)
      : 0.0;

    let totalContributif = total - horsRepartition;
    const avantages = [];

    // Avantages non contributifs du droit positif, DANS L'ORDRE OÙ LE DROIT
    // LES APPLIQUE, et l'ordre commande le résultat : les points gratuits de la
    // RCO et l'AVPF d'abord, qui déplacent le compte de points et le salaire
    // annuel moyen ; la majoration de durée d'assurance ensuite, qui change la
    // décote et la proratisation ; puis le minimum
    // contributif, qui porte la pension de base à son plancher ; puis seulement
    // la majoration pour enfants, qui se calcule SUR CE plancher ; l'ASPA
    // enfin, qui est différentielle et complète tout le reste.
    let minimumApplique = false;

    if (avantagesNonContributifs && majorationEnfants !== null) {
      // Effet des trimestres accordés au titre des enfants : la même carrière
      // sans eux, tout le reste égal.
      const sansMda = this.calculer(
        carriere, ignorerPenaliteAge, false, avpf, liquiderSuccessions,
        avecPointsGratuits,
      );
      // Les deux termes doivent porter sur le même périmètre : celui d'en
      // face est déjà net de la capitalisation.
      const effet = (total - horsRepartition) - sansMda.total_contributif;
      // Ces trimestres sont déjà incorporés aux pensions de régime : la base
      // contributive de la cascade est celle d'AVANT.
      totalContributif = sansMda.total_contributif;
      if (Math.abs(effet) > 1e-9) {
        avantages.push({
          code: "majoration_duree_assurance",
          libelle: LIBELLE_MAJORATION[majorationEnfants.dispositif],
          montant: effet,
          detail: `${majorationEnfants.trimestres} trimestres pour `
            + `${carriere.nombre_enfants} enfant`
            + `${carriere.nombre_enfants > 1 ? "s" : ""}, `
            + `au titre du régime « ${majorationEnfants.regime} »`,
        });
      }
    }

    if (avantagesNonContributifs && avpf
        && carriere.lignes.some((ligne) => ligne.revenu_avpf > 0)) {
      // Effet de l'AVPF, mesuré comme celui de la MDA : la même carrière sans
      // le salaire forfaitaire porté au compte. Il joue en amont de tout le
      // reste, et peut jouer dans les deux sens — il relève une carrière longue
      // à bas salaire, il abaisse la moyenne d'une carrière courte et bien
      // payée, où les années au SMIC s'ajoutent aux années retenues.
      const sansAvpf = this.calculer(
        carriere, ignorerPenaliteAge, false, false, liquiderSuccessions,
        avecPointsGratuits,
      );
      const effetAvpf = totalContributif - sansAvpf.total_contributif;
      totalContributif = sansAvpf.total_contributif;
      if (Math.abs(effetAvpf) > 1e-9) {
        avantages.unshift({
          code: "avpf",
          libelle: "Assurance vieillesse des parents au foyer",
          montant: effetAvpf,
          detail: "salaire forfaitaire au SMIC porté au compte",
        });
      }
    }

    if (avantagesNonContributifs && avecPointsGratuits && gratuitsAttribues.size > 0) {
      // Effet des POINTS GRATUITS de la RCO agricole, mesuré comme celui de
      // l'AVPF : la même carrière sans eux, la MDA et l'AVPF déjà retirées. Si
      // retirer la MDA les a fait tomber, leur effet est dans celui de la MDA,
      // qui les a ouverts, et ce recalcul n'en trouve plus rien.
      const sansGratuits = this.calculer(
        carriere, ignorerPenaliteAge, false, false, liquiderSuccessions, false,
      );
      const effetGratuits = totalContributif - sansGratuits.total_contributif;
      totalContributif = sansGratuits.total_contributif;
      if (Math.abs(effetGratuits) > 1e-9) {
        let pointsCites = 0.0;
        let avant = Infinity;
        for (const [points, annee] of gratuitsAttribues.values()) {
          pointsCites += points;
          avant = Math.min(avant, annee);
        }
        avantages.unshift({
          code: "points_gratuits_rco",
          libelle: "Points gratuits de la complémentaire agricole",
          montant: effetGratuits,
          detail: `${formatFixe(pointsCites, 2, true)} points pour les années de chef `
            + `d'exploitation d'avant ${avant}`,
        });
      }
    }

    if (avantagesNonContributifs && eligiblesMinimum.length > 0) {
      // Le minimum contributif ne relève que les pensions liquidées AU TAUX
      // PLEIN (L. 351-10). Sa majoration au titre des périodes cotisées demande
      // en outre 120 trimestres cotisés tous régimes ; elle se proratise
      // ensuite sur la durée cotisée DANS le régime, quand le montant de base
      // se proratise sur sa durée d'assurance (D. 351-2-2).
      const [montantBase, montantMajore, plafond, fiabiliteMinimum] = this
        .minimumContributif.valeurs(anneeLiquidation);
      const majorationOuverte = trimestresCotises >= TRIMESTRES_COTISES_MINIMUM_MAJORE;
      const complements = new Map();
      for (const eligible of eligiblesMinimum) {
        if (!eligible.tauxPlein) {
          continue;
        }
        const pension = pensions[eligible.indice];
        // Le minimum se compare à la pension AVANT surcote, et la surcote,
        // calculée sur cette pension nue, s'ajoute au minimum (D. 351-2-1) :
        // voir `complementMinimum`, qui porte aussi la règle d'avant 2009.
        const nue = pension.montant / eligible.surcote;
        let plancher = montantBase * Math.min(1.0, eligible.prorataAssurance);
        if (majorationOuverte) {
          plancher += (montantMajore - montantBase)
            * Math.min(1.0, eligible.prorataCotise);
        }
        const complement = complementMinimum(
          nue, plancher, eligible.surcote,
          [anneeLiquidation, carriere.moisLiquidation],
        );
        if (complement > 0) {
          complements.set(eligible.indice, complement);
        }
      }
      let releve = [...complements.values()].reduce((a, b) => a + b, 0.0);
      if (releve > 0) {
        // Écrêtement de l'article L. 173-2 : le complément est rogné de ce qui
        // dépasse le plafond, tous régimes confondus, et jamais au-delà. La
        // comparaison porte sur les pensions PERSONNELLES, majorations pour
        // enfants exclues — raison de plus pour les calculer après.
        const admissible = Math.max(0.0, Math.min(releve, plafond - total));
        if (admissible < releve) {
          const facteur = admissible / releve;
          for (const [indice, complement] of complements) {
            complements.set(indice, complement * facteur);
          }
        }
        releve = admissible;
      }
      if (releve > 0) {
        for (const [indice, complement] of complements) {
          // Le complément est DIT, pas seulement annoncé : sans lui, refaire la
          // formule donnait la pension d'avant le minimum et l'écart restait
          // inexpliqué — deux mille euros par an sur une petite retraite, ce
          // qui n'est pas un détail.
          pensions[indice] = {
            ...pensions[indice],
            montant: pensions[indice].montant + complement,
            detail: `${pensions[indice].detail} = `
              + `${formatFixe(pensions[indice].montant, 2, true)} €, porté au `
              + `minimum contributif par + ${formatFixe(complement, 2, true)} €`,
          };
        }
        total += releve;
        minimumApplique = true;
        fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteMinimum);
        avantages.push({
          code: "minimum_contributif",
          libelle: "Minimum contributif",
          montant: releve,
          detail: "porté au plancher, au prorata de la durée acquise"
            + (majorationOuverte ? ", majoration des périodes cotisées comprise" : ""),
        });
      }
    }

    if (avantagesNonContributifs && eligiblesGaranti.length > 0) {
      // Le minimum garanti n'est pas un minimum proratisé mais un BARÈME sur la
      // durée de services : quinze ans en ouvrent 57,5 % de la référence,
      // trente ans 95 %, quarante ans la totalité. Il ne s'ajoute pas à la
      // pension, il s'y substitue quand il lui est supérieur.
      let releveGaranti = 0.0;
      for (const eligible of eligiblesGaranti) {
        if (!eligible.ouvert) {
          continue;
        }
        const plancher = this.minimumGaranti.montant(
          anneeLiquidation, eligible.trimestresServices, eligible.dureeMaximum,
        );
        if (plancher === null) {
          continue;
        }
        const pension = pensions[eligible.indice];
        if (pension.montant > 0 && pension.montant < plancher[0]) {
          // Le complément était calculé en ligne et jamais nommé, alors que la
          // phrase juste dessous le cite : `complement` n'existait pas dans
          // cette portée — seulement dans la boucle du minimum contributif, au
          // -dessus — et toute carrière passant ici faisait tomber le moteur
          // JavaScript sur « complement is not defined » quand le Python, lui,
          // rendait sa pension. Le Python nomme la variable ; le portage ne le
          // faisait pas.
          const complement = plancher[0] - pension.montant;
          releveGaranti += complement;
          fiabiliteGlobale = Math.min(fiabiliteGlobale, plancher[1]);
          pensions[eligible.indice] = {
            ...pension,
            montant: plancher[0],
            // Le complément est DIT, comme pour le minimum contributif :
            // sans lui, refaire la formule donnait la pension d'avant le
            // plancher, et l'écart restait sans explication.
            detail: `${pension.detail} = `
              + `${formatFixe(pension.montant, 2, true)} €, porté au minimum `
              + `garanti par + ${formatFixe(complement, 2, true)} €`,
          };
        }
      }
      if (releveGaranti > 0) {
        total += releveGaranti;
        avantages.push({
          code: "minimum_garanti",
          libelle: "Minimum garanti de la fonction publique",
          montant: releveGaranti,
          detail: "barème de l'article L. 17, sur la durée de services",
        });
      }
    }

    // Surcote parentale (L. 351-1-2-1) : après les minima, avant la majoration
    // pour enfants qui se calcule sur la pension surcotée. Elle ne compte pas
    // les mêmes trimestres que la surcote ordinaire — celle-ci au-delà de l'âge
    // légal, celle-là dans l'année qui le précède — et les deux se cumulent.
    const parametresParentale = (avantagesNonContributifs
      && majorationEnfants !== null && !ignorerPenaliteAge)
      ? this.surcoteParentale.parametres(anneeLiquidation)
      : null;
    if (parametresParentale !== null) {
      const [ageLegalMinimal, tauxParental, maximum, fiabiliteParentale] = parametresParentale;
      let gainParental = 0.0;
      let trimestresParentaux = 0;
      for (let indice = 0; indice < pensions.length; indice += 1) {
        const pension = pensions[indice];
        const regime = this.catalogue.obtenir(pension.regime);
        const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
        if (periode === null
            || !periode.avantages_non_contributifs.includes("surcote_parentale")) {
          continue;
        }
        const ageLegal = this.ageOuverture(periode, carriere);
        const requis = this.dureeRequise(periode, carriere)[0];
        // LA FENÊTRE EST L'ANNÉE QUI PRÉCÈDE L'ÂGE LÉGAL, dès que cet âge
        // atteint 63 ans (L. 351-1-2-1) : voir le Python, qui cite le texte.
        if (ageLegal < ageLegalMinimal) {
          continue;
        }
        // Au MOIS près : l'âge légal tombe en cours d'année depuis 2026.
        const dateLegale = carriere.dateNaissance.plusMois(enMois(ageLegal));
        const debutFenetre = dateLegale.plusMois(-12);
        // Seuls comptent les trimestres cotisés de la fenêtre accomplis « au
        // delà de la limite » de durée, trimestres pour enfants compris.
        if (requis <= 0) {
          continue;
        }
        const avant = majorationEnfants.trimestres + trimestresEntreDates(
          carriere, new DateMois(carriere.annee_naissance, 1), debutFenetre, false,
        );
        const validesFenetre = trimestresEntreDates(
          carriere, debutFenetre, dateLegale, false,
        );
        const trimestres = Math.min(
          maximum,
          trimestresEntreDates(carriere, debutFenetre, dateLegale, true),
          Math.max(0, avant + validesFenetre - requis),
        );
        if (trimestres <= 0) {
          continue;
        }
        const supplement = pension.montant * tauxParental * trimestres;
        pensions[indice] = {
          ...pension,
          montant: pension.montant + supplement,
          detail: `${pension.detail}, surcote parentale `
            + `${formatPourcentage(tauxParental * trimestres, 2)}`,
        };
        gainParental += supplement;
        trimestresParentaux = Math.max(trimestresParentaux, trimestres);
      }
      if (gainParental > 0) {
        total += gainParental;
        fiabiliteGlobale = Math.min(fiabiliteGlobale, fiabiliteParentale);
        avantages.push({
          code: "surcote_parentale",
          libelle: "Surcote parentale",
          montant: gainParental,
          detail: `${formatPourcentage(tauxParental * trimestresParentaux, 2)} pour `
            + `${trimestresParentaux} trimestre`
            + `${trimestresParentaux > 1 ? "s" : ""} dans `
            + "l'année qui précède l'âge légal",
        });
      }
    }

    if (avantagesNonContributifs && carriere.nombre_enfants >= 2) {
      let majoration = 0.0;
      let tauxCite = 0.0;
      // Le plafond de l'Agirc-Arrco s'oppose à la majoration de LA
      // complémentaire, pas à celle de chacune de ses fiches : les points d'un
      // salarié du privé sont répartis entre l'Agirc, l'Arrco et le régime
      // unifié, et plafonner chacun séparément triplerait le plafond.
      let majorationPlafonnee = 0.0;
      let plafondCommun = null;
      // [régime, part, soumise au plafond], dans l'ordre des pensions.
      const parts = [];
      for (const pension of pensions) {
        if (pension.montant <= 0.0) {
          continue;
        }
        const regime = this.catalogue.obtenir(pension.regime);
        const periode = regime.periode(Math.min(anneeLiquidation, derniereAnnee(regime)));
        if (periode === null
            || !periode.avantages_non_contributifs.includes("majoration_enfants")) {
          continue;
        }
        let taux = tauxMajorationEnfants(regime, carriere.nombre_enfants, periode);
        const points = pointsAcquis.get(pension.regime) ?? 0.0;
        const majores = pointsMajores.get(pension.regime) ?? 0.0;
        if (majores > 0.0 && points > 0.0) {
          // CHAQUE POINT À SON TAUX, celui de son année d'acquisition.
          taux = (majorationPoints.get(pension.regime) + taux * (points - majores)) / points;
        }
        if (taux <= 0) {
          continue;
        }
        const part = pension.montant * taux;
        const plafond = this.plafondMajoration(
          pension.regime, periode, carriere, anneeLiquidation,
        );
        if (plafond === null) {
          majoration += part;
        } else {
          majorationPlafonnee += part;
          plafondCommun = plafondCommun === null ? plafond : Math.max(plafondCommun, plafond);
        }
        parts.push([pension.regime, part, plafond !== null]);
        tauxCite = Math.max(tauxCite, taux);
      }
      const plafonnee = plafondCommun !== null;
      let retenuePlafonnee = 1.0;
      if (plafondCommun !== null) {
        majoration += Math.min(majorationPlafonnee, plafondCommun);
        if (majorationPlafonnee > plafondCommun) {
          retenuePlafonnee = plafondCommun / majorationPlafonnee;
        }
      }
      if (majoration > 0) {
        total += majoration;
        let detail = `jusqu'à ${formatPourcentage(tauxCite, 0)} selon le régime`;
        if (plafonnee) {
          detail += ", plafonnée en euros à la complémentaire";
        }
        avantages.push({
          code: "majoration_enfants",
          libelle: carriere.nombre_enfants >= 3
            ? "Majoration pour trois enfants et plus"
            : "Bonification pour deux enfants",
          montant: majoration,
          detail,
          par_regime: parts.map(([code, part, soumise]) => [
            code, part * (soumise ? retenuePlafonnee : 1.0),
          ]),
        });
      }
    }

    if (avantagesNonContributifs
        && this.parametres.minimum_vieillesse_dans_le_scenario_actuel
        && ageLiquidation >= MinimumVieillesse.AGE_OUVERTURE) {
      // L'ASPA vient en DERNIER, et pour cause : elle est différentielle. Elle
      // complète tout le reste, majorations comprises, jusqu'au montant du
      // barème — c'est la seule prestation du système actuel qui ne suppose
      // aucune cotisation.
      const bareme = this.minimumVieillesse.plafond(anneeLiquidation);
      if (bareme !== null && total < bareme[0]) {
        const complement = bareme[0] - total;
        total = bareme[0];
        fiabiliteGlobale = Math.min(fiabiliteGlobale, bareme[1]);
        avantages.push({
          code: "minimum_vieillesse",
          libelle: "Minimum vieillesse (ASPA)",
          montant: complement,
          detail: "allocation différentielle, barème d'une personne seule",
        });
      }
    }

    return {
      pension_annuelle: Math.max(0.0, total - horsRepartition),
      pension_hors_repartition: horsRepartition,
      pensions_par_regime: pensions,
      trimestres_valides: trimestres,
      trimestres_requis: trimestresRequis,
      taux_liquidation: tauxRetenu,
      minimum_applique: minimumApplique,
      age_ouverture_opposable: ageOuvertureReference,
      liquidation_ouverte: liquidationOuverte,
      motif_ouverture: motifOuverture,
      avantages_appliques: avantages,
      total_contributif: totalContributif,
      fiabilite: fiabiliteGlobale,
      // Comme la pension annuelle : hors capitalisation.
      pension_mensuelle: Math.max(0.0, total - horsRepartition) / 12.0,
    };
  }
}

/**
 * Durée cotisée, tous régimes, qui ouvre la majoration du minimum contributif
 * au titre des périodes cotisées (article L. 351-10). En deçà, seul le montant
 * de base est dû.
 */
const TRIMESTRES_COTISES_MINIMUM_MAJORE = 120;

/**
 * Première date d'effet, [année, mois], où la surcote s'AJOUTE au minimum
 * contributif au lieu d'entrer dans la pension qu'on lui compare : décret
 * n° 2008-1509, dernier alinéa de D. 351-2-1.
 */
const SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS = [2009, 4];

/**
 * Ce que le minimum contributif ajoute à une pension, surcote comprise —
 * portage de `complement_minimum` : depuis avril 2009, `plancher − nue` (la
 * surcote, calculée sur la pension nue, s'ajoute au minimum) ; avant,
 * `max(0, plancher − nue × coefficient)`. Circulaire Cnav 2018-04, 3.4.
 */
export function complementMinimum(nue, plancher, coefficientSurcote, dateEffet) {
  if (nue <= 0) {
    return 0.0;
  }
  const [annee, mois] = dateEffet;
  const [anneeRegle, moisRegle] = SURCOTE_AJOUTEE_AU_MINIMUM_DEPUIS;
  if (annee > anneeRegle || (annee === anneeRegle && mois >= moisRegle)) {
    return Math.max(0.0, plancher - nue);
  }
  return Math.max(0.0, plancher - nue * coefficientSurcote);
}

/** Dernière année pour laquelle le régime a des paramètres. */
function derniereAnnee(regime) {
  if (regime.periodes.length === 0) {
    return 2100;
  }
  const annees = regime.periodes.map((p) => (p.fin === null ? 9999 : p.fin));
  return Math.min(Math.max(...annees), 2100);
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

/**
 * Taux de majoration pour enfants, régime par régime. Le régime général et les
 * régimes spéciaux servent 10 % à partir de trois enfants ; la fonction
 * publique y ajoute 5 % par enfant au-delà du troisième. Les complémentaires
 * servent 10 % aussi, mais plafonnés en euros : le taux est le même, c'est
 * `plafondMajoration` qui borne. Une fiche qui porte son propre barème — les
 * marins, qui bonifient dès deux enfants — l'emporte.
 */
function tauxMajorationEnfants(regime, nombreEnfants, periode = null) {
  const bareme = periode?.taux_majoration_enfants;
  if (bareme && bareme.length > 0) {
    return bareme[Math.min(nombreEnfants, bareme.length - 1)];
  }
  if (nombreEnfants < 3) {
    return 0.0;
  }
  if (regime.famille === "fonction_publique") {
    return 0.1 + 0.05 * (nombreEnfants - 3);
  }
  return 0.1;
}

/** Part de la rémunération que ce régime prend en compte. */
function assietteDeReference(periode, ligne) {
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
 * Trimestres acquis entre deux DATES, au mois près — `fin` exclue. Portage de
 * `_trimestres_entre_dates` : chaque ligne répartit ses trimestres sur ses
 * mois (les premiers de l'année du départ, les derniers de celle de
 * l'entrée), seuls comptent ceux de la plage, arrondi au trimestre inférieur.
 */
function trimestresEntreDates(carriere, debut, fin, cotisesSeulement) {
  let total = 0.0;
  for (const ligne of carriere.lignes) {
    if (cotisesSeulement && !ligne.cotise) {
      continue;
    }
    total += trimestresDeLaLigneEntre(carriere, ligne, debut, fin);
  }
  return Math.floor(total + 1e-9);
}

/**
 * Part des trimestres d'UNE ligne acquise entre deux dates, `fin` exclue : ses
 * trimestres sont répartis sur ses mois, comme le fait `trimestresEntreDates`,
 * qui en fait la somme.
 */
function trimestresDeLaLigneEntre(carriere, ligne, debut, fin) {
  const retenus = carriere.trimestresRetenus(ligne);
  const moisLigne = Math.round(carriere.partRetenue(ligne.annee) * 12);
  if (retenus <= 0 || moisLigne <= 0) {
    return 0.0;
  }
  const premier = (moisLigne === 12 || ligne.annee === carriere.anneeLiquidation)
    ? new DateMois(ligne.annee, 1)
    : new DateMois(ligne.annee, 13 - moisLigne);
  const dernier = premier.plusMois(moisLigne);
  const recouvrement = Math.min(fin.rang, dernier.rang) - Math.max(debut.rang, premier.rang);
  return recouvrement > 0 ? retenus * recouvrement / moisLigne : 0.0;
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
