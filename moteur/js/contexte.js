/**
 * Le contexte du site : ses données, et le jeu de règles sous lequel il calcule.
 *
 * Portage de ``src/retraite_notionnelle/contexte.py``.
 */

import { DateMois, MOIS_PAR_AN } from "./calendrier.js";
import { prolongerReleve, salaireMoyenAnnuel } from "./carriere.js";
import { formaterBorne } from "./regimes.js";
import { PARAMETRES_DEFAUT, cleParametres } from "./config.js";
import { AssietteActivite } from "./assiette.js";
import { calculerAvantages, chargerAvantages } from "./avantages.js";
import { chargerFrontiere } from "./frontiere.js";
import { calculerCout } from "./cout.js";
import { chargerBilan } from "./bilan.js";
import { DistributionPensions } from "./distribution.js";
import { DepensesRetraite } from "./depenses.js";
import { ComptesRetraite, varianteDuScenario } from "./equilibre.js";
import { Restitution } from "./restitution.js";
import { Population } from "./population.js";
import { assietteMaladie, salaireBrutDepuisNet, salaireNetDepuisBrut } from "./remuneration.js";
import { Simulateur, niveauPourPension } from "./simulateur.js";
import { REGIMES_CODE_DES_PENSIONS } from "./droit/coordonner.js";
import * as g from "./gabarit.js";
import { agesDeLEstimation } from "./pilote.js";
import {
  AUTRE_ETAT, Echelle, ErreurSaisie, HEURES_SMIC_PAR_MOIS, NIVEAU_MAXIMAL, NIVEAU_MINIMAL,
  Saisie, refus,
} from "./saisie.js";

/**
 * Pourquoi aucune carrière ne sert la pension saisie, et ce qui la sert.
 *
 * Les trois refus disent une règle du droit, jamais une limite du calcul, et
 * c'est ce qui les rend utiles : celui qui les lit apprend pourquoi sa pension
 * ne se déduit pas d'un revenu, et ce qu'il faut changer — le montant, ou la
 * carrière décrite au-dessus.
 *
 * Les montants sont rendus dans la langue du formulaire — mensuels, nets si la
 * page est en net, en euros de l'année de référence —, faute de quoi le refus
 * opposerait des annuels bruts à quelqu'un qui vient de taper un net mensuel.
 */
function refusDePension(trouve, constants) {
  // La dichotomie les a déjà nettés : il ne reste que l'unité.
  const afficher = (annuel) => g.euros((annuel * constants) / MOIS_PAR_AN);
  if (trouve.sousLePlancher) {
    return "Aucune carrière de cette forme ne sert une pension si petite : au "
      + `revenu le plus bas que le formulaire accepte, elle sert déjà `
      + `${afficher(trouve.plancher)} par mois — le minimum contributif et `
      + "l'ASPA font ce plancher. Saisissez au moins ce montant, ou décrivez "
      + "une carrière plus courte ou plus interrompue.";
  }
  if (trouve.auDessusDuPlafond) {
    return "Aucune carrière de cette forme ne sert une pension si grande : le "
      + `système actuel plafonne à ${afficher(trouve.plafond)} par mois. `
      + "Au-delà du plafond de la tranche la plus haute de ce statut, cotiser "
      + "davantage n'acquiert plus rien, et toutes les carrières mieux payées "
      + "servent la même pension.";
  }
  return "Aucune carrière de cette forme ne sert exactement cette pension : "
    + `entre ${afficher(trouve.pension_dessous)} et ${afficher(trouve.pension)} `
    + "par mois, il n'y a rien. Une année ne valide quatre trimestres qu'à "
    + "partir de 150 heures de SMIC ; au-dessous, la carrière compte pour "
    + "moins qu'elle n'a duré et le minimum contributif est proratisé "
    + "d'autant, si bien que la pension saute dès que le seuil est franchi. "
    + "Saisissez l'un de ces deux montants, ou décrivez la carrière — sa "
    + "durée, ses interruptions — telle qu'elle a été.";
}

/**
 * Combien d'agrégats le contexte garde en mémoire, tous jeux de règles
 * confondus. Deux par jeu — le coût et les avantages —, donc trois jeux de
 * règles : celui par défaut, et les deux derniers essayés.
 */
const AGREGATS_MEMORISES = 6;

/**
 * Les données du site, et le jeu de règles sous lequel on les lit.
 *
 * Un contexte, c'est deux choses : des données coûteuses à charger, et UN jeu
 * de paramètres — `base` — sous lequel tout ce que la page demande est
 * calculé. `simulateur()`, `cout()` et `avantages()` répondent tous trois sous
 * ce jeu-là, sans qu'aucune page ait à le leur redire.
 *
 * Les trois pages qui AGRÈGENT — Cas types, Coût, Avantages — se rendent donc
 * sous un contexte dérivé par `pour`, portant les réglages que l'adresse
 * demande. Le corps des pages n'en sait rien : il lit `contexte.base` comme il
 * l'a toujours fait, et y trouve les règles en vigueur au lieu des règles par
 * défaut. C'est ce qui évite de faire passer un jeu de paramètres à la main
 * dans la trentaine d'endroits qui les lisent.
 *
 * Les mémoires sont des `Map` partagées, et c'est ce qui fait tenir la
 * dérivation : un contexte dérivé PARTAGE ce que le contexte d'origine a déjà
 * chargé. Le chargement des données coûte quelques dixièmes de seconde, une
 * simulation en coûte dix, un agrégat une seconde : rien de tout cela ne doit
 * se refaire parce qu'on a changé une règle.
 */
export class Contexte {
  constructor(paquet, base = PARAMETRES_DEFAUT, memoires = null) {
    this.paquet = paquet;
    this.base = base;
    // Un simulateur par jeu de paramètres rencontré.
    this._instances = memoires ? memoires.instances : new Map();
    // Ce qui ne dépend d'AUCUN paramètre : dépense observée, comptes du COR,
    // population, distribution des pensions, assiette, inventaire des
    // avantages. Ces séries sont lues, jamais calculées : un changement de
    // règle ne les déplace pas.
    this._donnees = memoires ? memoires.donnees : new Map();
    // Les agrégats, eux, dépendent des règles : un coût par jeu de paramètres.
    this._agregats = memoires ? memoires.agregats : new Map();
  }

  /**
   * Le même contexte, sous un autre jeu de règles.
   *
   * Les mémoires sont partagées, pas recopiées : dériver ne coûte rien, et ce
   * que l'un charge, l'autre le trouve chargé.
   */
  pour(parametres) {
    if (cleParametres(parametres) === cleParametres(this.base)) { return this; }
    return new Contexte(this.paquet, parametres, {
      instances: this._instances,
      donnees: this._donnees,
      agregats: this._agregats,
    });
  }

  /** Une donnée indépendante des règles, chargée une fois pour toutes. */
  _donnee(nom, fabrique) {
    if (!this._donnees.has(nom)) {
      this._donnees.set(nom, fabrique());
    }
    return this._donnees.get(nom);
  }

  /**
   * Un agrégat, mémorisé par jeu de règles — et en nombre borné.
   *
   * Sans borne, une adresse suffirait à faire enfler la mémoire de l'onglet
   * d'un jeu de règles à l'autre : le calcul se fait chez le lecteur, et
   * l'adresse EST la saisie. Le plus ancien s'en va ; revenir aux réglages par
   * défaut après en avoir essayé trois recalcule, une seconde.
   */
  _agregat(nom, fabrique) {
    const cle = `${nom}|${cleParametres(this.base)}`;
    if (!this._agregats.has(cle)) {
      if (this._agregats.size >= AGREGATS_MEMORISES) {
        this._agregats.delete(this._agregats.keys().next().value);
      }
      this._agregats.set(cle, fabrique());
    }
    return this._agregats.get(cle);
  }

  simulateur(parametres = null) {
    const retenus = parametres || this.base;
    const cle = cleParametres(retenus);
    if (!this._instances.has(cle)) {
      this._instances.set(cle, new Simulateur(this.paquet, retenus));
    }
    return this._instances.get(cle);
  }

  depenses() {
    return this._donnee("depenses", () => new DepensesRetraite(this.paquet));
  }

  /**
   * Le second terme du bilan : ce que le système de retraite encaisse.
   *
   * SOUS LA VARIANTE DES RÈGLES DE `base`. La page lisait le scénario de
   * référence du COR quel que soit le scénario demandé, si bien que la
   * croissance déplaçait la dépense des systèmes notionnels, qui est calculée,
   * sans déplacer celle du droit en vigueur, qui est empruntée.
   *
   * La mémoire porte le nom de la variante : deux jeux de règles qui ne
   * diffèrent que par leur scénario ne doivent pas se partager un compte.
   */
  comptes() {
    const variante = varianteDuScenario(
      this.base.scenario_projection, this.paquet);
    return this._donnee(`comptes:${variante}`,
                        () => new ComptesRetraite(this.paquet, variante));
  }

  /**
   * Ce que la proposition rend au salaire, et ce qu'elle éteint en dette.
   * Mémorisé par jeu de règles et non une fois pour toutes : le partage est un
   * RÉGLAGE, et deux contextes n'ont pas forcément le même.
   */
  restitution() {
    return this._agregat("restitution", () => new Restitution(
      this.paquet, this.base.part_rendue_aux_salaires,
    ));
  }

  population() {
    return this._donnee("population", () => new Population(this.paquet));
  }

  /** La distribution des pensions — elle seule chiffre un plancher. */
  distribution() {
    return this._donnee("distribution", () => new DistributionPensions(this.paquet));
  }

  /** Sur quoi l'on prélève : sans elle, un taux ne se convertit pas en recette. */
  assiette() {
    return this._donnee("assiette", () => new AssietteActivite(this.paquet));
  }

  /**
   * Le bilan des quatre systèmes, figé — une DONNÉE, pas un agrégat.
   *
   * La page des résultats en a besoin à chaque frappe, et le calculer coûte
   * une seconde : elle lit donc la table que `scripts/construire_donnees.py` a
   * écrite dans le paquet. `bilan.js` dit ce que ce figeage coûte — rien sur
   * le système actuel, dont le coefficient est le compte du COR, et une
   * dépendance aux réglages de référence sur les trois autres.
   */
  bilan() {
    return this._donnee("bilan", () => chargerBilan(this.paquet.bilan_equilibre));
  }

  /** L'inventaire des avantages non contributifs — une donnée, pas un calcul. */
  inventaireAvantages() {
    return this._donnee("inventaireAvantages", () => chargerAvantages(this.paquet));
  }

  /** Le versant inverse : ce qu'on cotise sans rien acquérir. Une donnée. */
  frontiere() {
    return this._donnee("frontiere", () => chargerFrontiere(this.paquet));
  }

  /** Ce que les avantages non contributifs coûtent — une seconde, une fois. */
  avantages() {
    return this._agregat("avantages", () => calculerAvantages(
      this.simulateur(), this.depenses(), this.population(),
    ));
  }

  /**
   * Le coût agrégé de tous les systèmes — une seconde de calcul, une fois.
   *
   * Sous les règles de `base`, et non sous celles par défaut : c'est ce qui
   * fait que la page Coût chiffre ce que le simulateur calcule.
   */
  cout() {
    return this._agregat("cout", () => calculerCout(
      this.simulateur(), this.depenses(), this.population(), this.comptes(),
      undefined, undefined, undefined, this.assiette(),
    ));
  }

  /**
   * L'échelle des salaires de l'année courante, pour cette saisie. L'année est
   * celle du modèle — on saisit un salaire d'aujourd'hui —, et les séries sont
   * CELLES DE LA SAISIE : au-delà de la dernière année observée, le salaire
   * moyen dépend du scénario de projection choisi.
   */
  echelle(saisie) {
    const parametres = saisie.parametres(this.base);
    const macro = this.simulateur(parametres).macro;
    const annee = parametres.annee_courante;
    const simulateur = this.simulateur(parametres);
    const bareme = simulateur.baremePrelevements;
    const versBrut = (netMensuel, statut) => salaireBrutDepuisNet(
      bareme, macro, simulateur.catalogue, simulateur.affiliations,
      statut, annee, netMensuel * MOIS_PAR_AN,
    ) / MOIS_PAR_AN;
    const versNet = (brutMensuel, statut) => salaireNetDepuisBrut(
      bareme, macro, simulateur.catalogue, simulateur.affiliations,
      statut, annee, brutMensuel * MOIS_PAR_AN,
    ) / MOIS_PAR_AN;
    return new Echelle({
      moyen: salaireMoyenAnnuel(macro, annee),
      smic: HEURES_SMIC_PAR_MOIS * macro.smic_horaire.valeur(annee),
      plafond: macro.plafond_securite_sociale.valeur(annee) / MOIS_PAR_AN,
      versBrut: saisie.saisieEnNet ? versBrut : null,
      versNet,
      versBrutDirect: versBrut,
    });
  }

  simuler(saisie) {
    const simulateur = this.simulateur(saisie.parametres(this.base));
    // Les motifs viennent des données, pas d'une liste écrite ici : le moteur y
    // lit ce que chaque période ouvre, et une saisie refusée doit l'être sur la
    // même table que celle qui calcule.
    const motifs = Object.keys(this.paquet.periodes_non_travaillees ?? {});
    if (saisie.releveActif) {
      return simulateur.simuler(this.carriereRelevee(simulateur, saisie, motifs));
    }
    const [parcours, batir] = this._parcours(simulateur, saisie, motifs);
    if (saisie.parPension) {
      return this._simulerParPension(simulateur, saisie, batir, parcours);
    }
    return simulateur.simuler(carriereParcourue(simulateur, parcours, batir));
  }

  /**
   * La carrière que `simuler` calcule pour une saisie par le revenu : celle du
   * relevé, ou celle des métiers.
   */
  carriere(saisie) {
    const simulateur = this.simulateur(saisie.parametres(this.base));
    const motifs = Object.keys(this.paquet.periodes_non_travaillees ?? {});
    if (saisie.releveActif) {
      return this.carriereRelevee(simulateur, saisie, motifs);
    }
    const [parcours, batir] = this._parcours(simulateur, saisie, motifs);
    return carriereParcourue(simulateur, parcours, batir);
  }

  /**
   * Les départs que « Mon estimation retraite » chiffre — au plus tôt, au taux
   * plein, au taux plein automatique —, tels que le scénario 1 les sert à la
   * carrière de cette saisie : le brut de chaque étage, annuel, en euros
   * constants de l'année de référence. Deux âges confondus font un départ.
   * Vide pour une saisie par la pension, pour qui est déjà parti, pour une
   * carrière dont la saisie date elle-même des pensions — demandées régime par
   * régime, ouvertes par l'invalidité ou par la radiation —, quand le droit
   * n'oppose aucun âge, ou quand la saisie ou le modèle refusent la carrière à
   * l'un des âges ; un départ d'une année déjà passée est omis. Voir
   * `departs_de_l_estimation` (contexte.py).
   */
  departsDeLEstimation(saisie) {
    if (saisie.parPension || saisie.demandes.length > 0 || saisie.invalidite !== null
        || saisie.radiation_invalidite !== null) {
      return [];
    }
    const parametres = saisie.parametres(this.base);
    const simulateur = this.simulateur(parametres);
    const annee = parametres.annee_courante;
    if (saisie.dateLiquidation.annee < annee) {
      return [];
    }
    // La saisie refuse ce que sa date rend incohérent — un métier commencé
    // après le départ —, avec ses mots, avant le modèle.
    const batir = (age) => {
      const autre = new Saisie({ ...saisie, liquidation: age });
      autre.verifier();
      return this.carriere(autre);
    };
    const departs = [];
    try {
      const ages = agesDeLEstimation(simulateur.scenarioActuel, batir, saisie.liquidation);
      for (const [quoi, age] of Object.entries(ages ?? {})) {
        const dernier = departs[departs.length - 1];
        if (dernier !== undefined && Math.abs(dernier.age - age) < 1e-9) {
          dernier.quoi.push(quoi);
          continue;
        }
        const carriere = batir(age);
        if (carriere.anneeLiquidation >= annee) {
          departs.push(departEstime(simulateur, parametres, carriere, quoi));
        }
      }
    } catch (erreur) {
      // Une carrière que la saisie ou le modèle refusent à l'un des âges : le
      // bloc se tait plutôt que de chiffrer une autre carrière. Une faute de
      // programme, elle, remonte.
      if (erreur instanceof TypeError || erreur instanceof ReferenceError
          || erreur instanceof RangeError || erreur instanceof SyntaxError) {
        throw erreur;
      }
      return [];
    }
    return departs;
  }

  /**
   * Les métiers de la saisie, et de quoi bâtir leur carrière à des niveaux de
   * revenu donnés.
   */
  _parcours(simulateur, saisie, motifs) {
    const parcours = saisie.parcours(this.echelle(saisie));
    for (const metier of parcours) {
      if (!simulateur.affiliations.contient(metier.affiliation)) {
        throw new ErreurSaisie(
          `Statut d'affiliation inconnu : « ${metier.affiliation} ».`,
        );
      }
    }
    const emploiRetraite = this.emploiRetraite(simulateur, saisie);
    const demandes = demandesDePension(simulateur, saisie);
    const etranger = etrangerDeclare(simulateur, saisie);
    const batir = (niveaux) => simulateur.carriereParcours({
      annee_naissance: saisie.naissance,
      mois_naissance: saisie.naissance_mois,
      jour_naissance: saisie.jourDeclare,
      sexe: saisie.sexe,
      metiers: parcours.map((metier, rang) => ({
        ...metier,
        niveau_salaire: niveaux[rang],
      })),
      age_liquidation: saisie.liquidation,
      profil_carriere: saisie.profil,
      interruptions: saisie.interruptionsDeCarriere(motifs),
      nombre_enfants: saisie.enfants,
      naissances_enfants: saisie.naissancesEnfants(),
      conjoint: saisie.conjointDeclare(),
      deces: saisie.decesDeclare(),
      retraite_progressive: saisie.retraiteProgressiveDeclaree(),
      emploi_retraite: emploiRetraite,
      demandes_de_pension: demandes,
      invalidite: saisie.invaliditeDeclaree(),
      etranger,
      part_primes: saisie.primes,
      identifiant: "assuré",
    });
    return [parcours, batir];
  }

  /**
   * La carrière que la pension suppose, puis les quatre systèmes dessus.
   *
   * UN SEUL NIVEAU POUR TOUTE LA CARRIÈRE. Inverser une pension ne donne qu'un
   * nombre, et une carrière en compte autant qu'elle a de métiers : il faut
   * donc une convention, et la plus simple est la seule qui n'invente rien —
   * le même niveau partout, que le profil de carrière déforme ensuite comme il
   * le fait toujours. Qui veut un revenu par métier le saisit, ou dépose son
   * relevé.
   *
   * LA CIBLE EST RAMENÉE À CE QUE LE MODÈLE CALCULE, et dans cet ordre : la
   * pension saisie est mensuelle, nette peut-être, en euros constants de
   * l'année de référence ; le scénario 1 rend une pension annuelle, brute, en
   * euros de l'année de liquidation, que chaque tour nette quand la saisie
   * l'est. Le coefficient des euros constants ne
   * dépend que de l'année de liquidation, jamais du niveau de revenu : il se
   * calcule une fois, avant la dichotomie, et non à chaque tour.
   */
  _simulerParPension(simulateur, saisie, batir, parcours) {
    const montants = Montants.depuis(saisie, simulateur);
    // Pour un retraité, la cible est la pension d'AUJOURD'HUI : il saisit ce
    // qu'il touche, pas ce qu'il touchait le premier mois. Voir
    // `_simuler_par_pension` dans `contexte.py`.
    const parametres = simulateur.parametres;
    const retraite = saisie.dateDe(saisie.liquidation).annee < parametres.annee_courante;
    const constants = simulateur.macro.coefficientPrix(
      retraite ? parametres.annee_courante : saisie.dateDe(saisie.liquidation).annee,
      parametres.annee_euros_constants,
    );
    // La cible reste dans la langue de la saisie, nette peut-être : le taux
    // qui sépare une pension de sa nette dépend de sa part complémentaire,
    // donc du niveau cherché. Voir `_simuler_par_pension` dans `contexte.py`.
    const cible = saisie.pension * MOIS_PAR_AN / constants;
    const combien = parcours.length;
    const pensionDeNiveau = (niveau) => {
      const carriere = batir(new Array(combien).fill(niveau));
      if (retraite) {
        const echeancier = simulateur.echeancier(carriere);
        return montants.pensionServie(echeancier.auDepart, echeancier.aujourdhui);
      }
      return montants.pensionServie(simulateur.scenarioActuel.calculer(carriere));
    };

    const trouve = niveauPourPension(pensionDeNiveau, cible,
      NIVEAU_MINIMAL, NIVEAU_MAXIMAL);
    if (!trouve.atteinte) {
      throw new ErreurSaisie(refusDePension(trouve, constants));
    }
    const carriere = batir(new Array(combien).fill(trouve.niveau));
    verifierStatutsOuverts(simulateur.affiliations, carriere, parcours);
    verifierRadiationPourInvalidite(simulateur.affiliations, carriere);
    const comparaison = simulateur.simuler(carriere);
    comparaison.niveau_inverse = trouve;
    return comparaison;
  }

  /**
   * Le relevé que `simuler` calcule : celui de la saisie, puis les années qui
   * le séparent du départ (`releveJusquAuDepart`). La page dit celles qu'elle
   * a ajoutées. Voir `releve_prolonge` du Python.
   */
  releveProlonge(saisie) {
    const simulateur = this.simulateur(saisie.parametres(this.base));
    const motifs = Object.keys(this.paquet.periodes_non_travaillees ?? {});
    return releveJusquAuDepart(simulateur, saisie, saisie.releveAnalyse(motifs), motifs);
  }

  /**
   * La carrière telle que le relevé la donne, sans rien reconstituer.
   *
   * Aucune échelle des salaires n'intervient : le relevé est déjà en euros de
   * chaque année, quand le formulaire paramétrique saisit un revenu
   * d'aujourd'hui que le modèle promène ensuite le long du salaire moyen. C'est
   * ce qui fait de ce chemin le plus exact — et le seul où l'euro n'est pas
   * converti. Seules les années qui suivent le relevé, jusqu'au départ, se
   * projettent (`releveJusquAuDepart`) ; `prolonger = false` s'en tient au
   * relevé.
   */
  carriereRelevee(simulateur, saisie, motifs, prolonger = true) {
    let releve = saisie.releveAnalyse(motifs);
    for (const ligne of releve) {
      if (!simulateur.affiliations.contient(ligne.affiliation)) {
        throw new ErreurSaisie(
          `Relevé, année ${ligne.annee} : statut d'affiliation inconnu `
          + `« ${ligne.affiliation} ».`,
        );
      }
    }
    if (prolonger) {
      releve = releveJusquAuDepart(simulateur, saisie, releve, motifs);
    }
    const carriere = simulateur.carriereReleve({
      annee_naissance: saisie.naissance,
      mois_naissance: saisie.naissance_mois,
      jour_naissance: saisie.jourDeclare,
      sexe: saisie.sexe,
      releve,
      age_liquidation: saisie.liquidation,
      nombre_enfants: saisie.enfants,
      naissances_enfants: saisie.naissancesEnfants(),
      conjoint: saisie.conjointDeclare(),
      deces: saisie.decesDeclare(),
      retraite_progressive: saisie.retraiteProgressiveDeclaree(),
      emploi_retraite: this.emploiRetraite(simulateur, saisie),
      demandes_de_pension: demandesDePension(simulateur, saisie),
      invalidite: saisie.invaliditeDeclaree(),
      etranger: etrangerDeclare(simulateur, saisie),
      part_primes: saisie.primes,
      identifiant: "assuré",
    });
    verifierStatutsReleve(simulateur.affiliations, carriere);
    verifierRadiationPourInvalidite(simulateur.affiliations, carriere);
    return carriere;
  }

  /**
   * L'activité exercée après le départ que la saisie déclare, son revenu ramené
   * à l'unité du modèle, et son statut contrôlé comme ceux des métiers.
   */
  emploiRetraite(simulateur, saisie) {
    const emploi = saisie.emploiRetraiteDeclare(this.echelle(saisie));
    if (emploi !== null && !simulateur.affiliations.contient(emploi.affiliation)) {
      throw new ErreurSaisie(
        "Activité après le départ : statut d'affiliation inconnu "
        + `« ${emploi.affiliation} ».`,
      );
    }
    return emploi;
  }
}

/**
 * La carrière hors de France que la saisie déclare, telle que la chronologie la
 * reçoit. Chaque État s'y contrôle sur le tableau des accords, la saisie
 * n'ayant pas les données ; le montant de chaque pension étrangère, saisi en
 * euros d'aujourd'hui, y devient son montant `mensuel` en euros de l'année où
 * elle commence, sur les prix. Voir `_etranger` du Python.
 */
function etrangerDeclare(simulateur, saisie) {
  const etranger = saisie.etrangerDeclare();
  if (etranger === null) {
    return null;
  }
  const etats = simulateur.macro.paquet.accords_internationaux;
  const controler = (code, quoi) => {
    if (code !== AUTRE_ETAT && !Object.hasOwn(etats, code)) {
      throw new ErreurSaisie(
        `${quoi} : aucun État « ${code} » au tableau des accords. Un État qu'aucun `
        + `accord ne lie à la France s'écrit « ${AUTRE_ETAT} » ; une collectivité `
        + "d'outre-mer qui a son régime se déclare par ce régime, dans la carrière.",
      );
    }
  };
  etranger.periodes.forEach((periode, index) => {
    controler(periode.pays, `Période à l'étranger n° ${index + 1}`);
  });
  const courante = simulateur.parametres.annee_courante;
  const pensions = etranger.pensions.map((pension, index) => {
    controler(pension.pays, `Pension étrangère n° ${index + 1}`);
    const annee = saisie.dateDe(pension.age).annee;
    return { pays: pension.pays, age: pension.age,
      mensuel: pension.montant * simulateur.macro.coefficientPrix(courante, annee) };
  });
  const { residence } = etranger;
  if (residence !== null) {
    controler(residence, "Résidence après le départ");
    if (residence !== AUTRE_ETAT && etats[residence].accords.every(
      (accord) => accord.instrument === "organisation_internationale")) {
      throw new ErreurSaisie(
        "Résidence après le départ : on réside dans un État, non dans une "
        + "organisation internationale.",
      );
    }
  }
  return { ...etranger, pensions };
}

/**
 * Le relevé, sa dernière année poursuivie jusqu'au départ (`prolongerReleve`) :
 * comme le dernier métier d'un parcours court jusqu'à lui, et comme « Mon
 * estimation retraite » prolonge les revenus. Les années ajoutées prennent leur
 * motif comme celles d'une carrière de métiers (`interruptionsApres`) ; la
 * retraite progressive les met à temps partiel ; la radiation pour invalidité
 * les arrête à sa date quand elle ne tombe pas avant la dernière année du
 * relevé. Rien ne s'ajoute à qui est parti une année déjà passée. Voir
 * `_releve_jusqu_au_depart` du Python.
 */
function releveJusquAuDepart(simulateur, saisie, releve, motifs) {
  const depart = saisie.dateLiquidation;
  if (depart.annee < simulateur.parametres.annee_courante) {
    return releve;
  }
  const derniere = Math.max(...releve.map((ligne) => ligne.annee));
  let fin = depart;
  if (saisie.radiation_invalidite !== null) {
    const radiation = saisie.dateDe(saisie.radiation_invalidite);
    if (radiation.annee >= derniere && radiation.rang < fin.rang) {
      fin = radiation;
    }
  }
  const declaree = saisie.retraiteProgressiveDeclaree();
  const progressive = declaree === null ? null
    : [saisie.dateDe(declaree.age, true), declaree.quotite];
  return prolongerReleve(releve, fin, simulateur.macro,
    saisie.interruptionsApres(new DateMois(derniere + 1, 1), motifs), progressive);
}

/**
 * Les dates de demande que la saisie dit, chacune pour un régime que le
 * catalogue connaît : c'est ici qu'un code inconnu se refuse, la saisie n'ayant
 * pas le catalogue. Voir `_demandes_de_pension` du Python.
 */
function demandesDePension(simulateur, saisie) {
  const demandes = saisie.demandesDePensionDeclarees();
  for (const code of Object.keys(demandes ?? {})) {
    if (!simulateur.catalogue.contient(code)) {
      throw new ErreurSaisie(
        `Pension demandée à une date : aucun régime « ${code} » dans le catalogue `
        + "du modèle.",
      );
    }
  }
  return demandes;
}

/**
 * Un statut ne se déclare qu'aux dates où son régime recrutait.
 *
 * Un jeune d'aujourd'hui ne peut pas se déclarer mineur : le régime des mines
 * est fermé aux recrutés depuis septembre 2010. Le routage le savait déjà —
 * il envoyait ce mineur-là au régime général, en silence, et la page
 * affichait « Mineur » au-dessus d'une pension de salarié du privé. Le refus
 * dit la date, et le statut de droit commun qui porte le même calcul.
 *
 * La date opposée est celle de l'ENTRÉE dans le statut, au mois près, telle
 * que le parcours l'a datée : un agent entré à la RATP en octobre 2022 n'y a
 * sa première ligne qu'en 2023, et n'est pas recruté après la fermeture pour
 * autant.
 */
/** La carrière des métiers, à leurs niveaux de revenu, contrôlée. */
function carriereParcourue(simulateur, parcours, batir) {
  const carriere = batir(parcours.map((metier) => metier.niveau_salaire));
  verifierStatutsOuverts(simulateur.affiliations, carriere, parcours);
  verifierRadiationPourInvalidite(simulateur.affiliations, carriere);
  return carriere;
}

/**
 * Un départ de « Mon estimation retraite », tel que le scénario 1 le sert :
 * le brut de chaque étage, annuel, en euros constants de l'année de référence
 * — la pension de chaque régime, minima compris, et la part qu'il sert de la
 * majoration pour enfants —, le minimum vieillesse à part. Voir `DepartEstime`
 * et `_depart_estime` (contexte.py).
 */
function departEstime(simulateur, parametres, carriere, quoi) {
  const resultat = simulateur.echeancier(carriere).auDepart;
  const passage = simulateur.macro.coefficientPrix(
    carriere.anneeLiquidation, parametres.annee_euros_constants);
  const etages = {};
  const prelevements = simulateur.baremePrelevements.pensions;
  const regimes = prelevements.regimes_maladie;
  let assiette = 0.0;
  let generale = 0.0;
  const porter = (code, montant) => {
    const etage = simulateur.catalogue.obtenir(code).etage;
    etages[etage] = (etages[etage] ?? 0.0) + montant * passage;
  };
  for (const pension of resultat.pensions_par_regime) {
    porter(pension.regime, pension.montant);
    if (regimes.has(pension.regime)) assiette += pension.montant * passage;
    if (prelevements.regimes_generaux.has(pension.regime)) generale += pension.montant * passage;
  }
  let minimum = 0.0;
  for (const avantage of resultat.avantages_appliques) {
    if (avantage.code === "majoration_enfants") {
      for (const [code, part] of avantage.par_regime ?? []) porter(code, part);
    } else if (avantage.code === "minimum_vieillesse") {
      minimum += avantage.montant;
    }
  }
  const date = carriere.dateLiquidation;
  return {
    quoi: [quoi],
    age: carriere.age_liquidation,
    date: `${String(date.annee).padStart(4, "0")}-${String(date.mois).padStart(2, "0")}`,
    etages,
    minimum_vieillesse: minimum * passage,
    trimestres: resultat.trimestres_valides,
    trimestres_requis: resultat.trimestres_requis,
    motif_ouverture: resultat.motif_ouverture,
    // Ce que la cotisation maladie de 1 % frappe dans `etages`. Voir
    // `DepartEstime.assiette_maladie` (contexte.py).
    assiette_maladie: assiette,
    assiette_regime_general: generale,
    get total() {
      return Object.values(this.etages).reduce((somme, montant) => somme + montant, 0.0);
    },
  };
}

/**
 * La radiation pour invalidité clôt un emploi de fonctionnaire civil — de
 * l'État, territorial, hospitalier, ouvrier de l'État —, et la carrière ne
 * reste pas dans la fonction publique après elle. Voir
 * `_verifier_radiation_pour_invalidite` du Python.
 */
function verifierRadiationPourInvalidite(affiliations, carriere) {
  const radiation = carriere.radiationPourInvalidite;
  if (radiation === null) {
    return;
  }
  const civile = (affiliation, annee) => affiliations.pensionMilitaire(affiliation) === null
    && affiliations.regimes(affiliation, annee).some((r) => REGIMES_CODE_DES_PENSIONS.has(r));
  // La dernière année que l'emploi clos touche : celle d'avant, quand la
  // radiation tombe en janvier.
  const annee = radiation.date.mois > 1 ? radiation.date.annee : radiation.date.annee - 1;
  if (!radiation.affiliations.some((affiliation) => civile(affiliation, annee))) {
    throw new ErreurSaisie(
      `Radiation pour invalidité en ${radiation.date} : elle clôt un emploi de `
      + "fonctionnaire civil — de l'État, territorial, hospitalier, ouvrier de "
      + "l'État —, et la carrière n'en exerce pas à cette date.",
    );
  }
  for (const ligne of carriere.lignes) {
    if (ligne.annee > annee && ligne.type_periode === "emploi"
        && civile(ligne.affiliation, ligne.annee)) {
      throw new ErreurSaisie(
        `Radiation pour invalidité en ${radiation.date} : la carrière reste dans la `
        + `fonction publique en ${ligne.annee}. Déclarez à la date de la radiation la `
        + "période qui la suit.",
      );
    }
  }
}

function verifierStatutsOuverts(affiliations, carriere, parcours) {
  parcours.forEach((metier, index) => {
    const ferme = statutFerme(affiliations, carriere, metier.affiliation);
    if (ferme === null) {
      return;
    }
    const [fermeture, entree] = ferme;
    throw refus(index + 1, phraseStatutFerme(
      affiliations, metier.affiliation, fermeture,
      `ce métier commence en ${entree}`,
    ));
  });
}

/**
 * Le même refus, opposé à un relevé de carrière.
 *
 * Le relevé ne compte pas de métiers : il porte des ANNÉES, dont chacune nomme
 * son statut. La date opposée à la fermeture est donc la première année
 * déclarée sous ce statut — janvier, faute d'un mois que le relevé ne donne
 * pas —, et la phrase le dit plutôt que de parler d'un « métier n° 2 » qui
 * n'existe nulle part sur la page.
 */
function verifierStatutsReleve(affiliations, carriere) {
  for (const code of carriere.affiliationsUtilisees()) {
    const ferme = statutFerme(affiliations, carriere, code);
    if (ferme === null) {
      continue;
    }
    const [fermeture, entree] = ferme;
    throw new ErreurSaisie(phraseStatutFerme(
      affiliations, code, fermeture,
      `la première année déclarée sous ce statut est ${entree.annee}`,
    ));
  }
}

/** `[fermeture, entrée]` si ce statut se déclare trop tard, sinon `null`. */
function statutFerme(affiliations, carriere, code) {
  const fermeture = affiliations.fermetureEntrants(code);
  if (fermeture === null) {
    return null;
  }
  const entree = carriere.dateEntree(code);
  if (entree === null || entree.rang < fermeture.rang) {
    return null;
  }
  return [fermeture, entree];
}

/**
 * Le refus, écrit une fois pour les deux formes de saisie. `quand` est la seule
 * chose qui les sépare : un métier commence à un mois, une ligne de relevé n'a
 * qu'une année. Écrire les deux phrases en entier les laisserait diverger.
 */
function phraseStatutFerme(affiliations, code, fermeture, quand) {
  const releve = affiliations.relevePar(code);
  return `Le statut « ${affiliations.libelle(code)} » est `
    + `fermé aux recrutés depuis ${formaterBorne(fermeture)} ; ${quand}. `
    + `Depuis cette date, il relève des mêmes régimes que `
    + `« ${affiliations.libelle(releve)} » : choisir ce statut.`;
}

/** Les parts du foyer : une, deux avec un conjoint déclaré (CGI, art. 194). */
function partsDuFoyer(saisie) {
  return saisie.conjoint ? 2 : 1;
}

/** Les pensions du foyer, une par pensionné, et celles du conjoint déclaré. */
function foyer(saisie, pension) {
  const pensions = [pension];
  if (saisie.conjoint && saisie.ressources_conjoint) pensions.push(saisie.ressources_conjoint);
  return pensions;
}

/**
 * La pension saisie, annuelle et brute. Voir `_pension_saisie_brute` dans
 * `contexte.py`.
 */
function pensionSaisieBrute(saisie, pensions) {
  const annuelle = saisie.pension * MOIS_PAR_AN;
  if (!saisie.enNet) return annuelle;
  const parts = partsDuFoyer(saisie);
  for (const tranche of pensions.bareme_csg) {
    const brute = annuelle / (1 - pensions.tauxDeLaTranche(tranche));
    const revenu = pensions.revenuFiscalPresume(foyer(saisie, brute));
    if (pensions.tranche(revenu, parts) === tranche) return brute;
  }
  return annuelle
    / (1 - pensions.tauxDeLaTranche(pensions.bareme_csg[pensions.bareme_csg.length - 1]));
}

/**
 * Le revenu fiscal de référence du foyer, et s'il est présumé. Voir
 * `revenu_fiscal_du_foyer` dans `contexte.py`.
 */
function revenuFiscalDuFoyer(saisie, pensions, pension) {
  if (saisie.revenu_fiscal !== null && saisie.revenu_fiscal !== undefined) {
    return [saisie.revenu_fiscal, false];
  }
  let annuelle = pension;
  if (saisie.saisie_par === "pension") annuelle = pensionSaisieBrute(saisie, pensions);
  if (annuelle === null) return [null, false];
  return [pensions.revenuFiscalPresume(foyer(saisie, annuelle)), true];
}

/** L'instrument des accords qui coordonne aussi l'assurance maladie. */
const REGLEMENTS_EUROPEENS_SANTE = "reglements_europeens";

/** Les règlements européens s'appliquent-ils à cet État à cette date ? */
function reglementsEuropeens(accords, pays, date) {
  for (const accord of (accords[pays] ?? {}).accords ?? []) {
    if (accord.instrument === REGLEMENTS_EUROPEENS_SANTE && accord.de <= date
        && (accord.a === null || accord.a === undefined || date < accord.a)) {
      return true;
    }
  }
  return false;
}

/**
 * Si la France prend en charge les frais de santé de qui réside hors de
 * France (L. 160-3), et pourquoi. Voir `couverture_francaise` dans
 * `contexte.py`.
 */
function couvertureFrancaise(saisie, actuel, europeen, dureeMinimale) {
  if (europeen) {
    if (saisie.pensions_etrangeres.some((pension) => pension.pays === saisie.residence)) {
      return [false, "residence_competente"];
    }
    return [true, "france_competente"];
  }
  if (actuel === null) return [true, "quinze_ans"];
  const trimestres = actuel.trimestres_valides - actuel.trimestres_etrangers;
  return [trimestres >= dureeMinimale,
    trimestres >= dureeMinimale ? "quinze_ans" : "moins_de_quinze_ans"];
}

/** Le minimum vieillesse que le scénario 1 sert, à l'échéance ou au départ. */
function minimumVieillesseServi(actuel, aujourdhui = null) {
  if (aujourdhui !== null) return aujourdhui.minimum_vieillesse;
  let total = 0;
  for (const avantage of actuel.avantages_appliques) {
    if (avantage.code === "minimum_vieillesse") total += avantage.montant;
  }
  return total;
}

/**
 * Le mode net/brut, et ce qu'il fait à chaque montant affiché.
 *
 * Un seul objet, construit une fois par rendu, pour que la bascule n'existe
 * qu'à un endroit. Deux grandeurs n'ont pas le même barème — un salaire
 * supporte des cotisations, une pension n'en supporte plus — et deux autres
 * n'ont pas de net du tout : un CAPITAL notionnel et une ASSIETTE de cotisation
 * sont bruts par nature, et le site les laisse tels quels.
 */
export class Montants {
  constructor(net, tauxPension, rapportNetBrutSalaire = 0, rapportNetBrutProposition = 0,
    maladie = null) {
    this.net = net;
    // Le taux de CETTE PERSONNE : 9,1 %, et la cotisation maladie de 1 % sur la
    // part de sa pension du scénario 1 que des complémentaires servent. Les
    // cinq autres scénarios le gardent : la réforme ne change pas ses
    // prélèvements, par hypothèse. Voir `Montants` dans `contexte.py`.
    this.tauxPension = tauxPension;
    // Le taux d'une pension de base, la cotisation maladie, la part de la
    // pension du scénario 1 qui la paie, et les régimes qui la prélèvent.
    this.tauxSansMaladie = maladie?.tauxSansMaladie ?? tauxPension;
    this.tauxMaladie = maladie?.tauxMaladie ?? 0;
    this.partMaladie = maladie?.partMaladie ?? 0;
    this.regimesMaladie = maladie?.regimesMaladie ?? new Set();
    // La tranche de CSG du foyer, son taux, le revenu fiscal qui la fixe et
    // s'il est présumé, l'exonération de l'allocataire de l'ASPA, les parts du
    // foyer ; le barème et la saisie, pour la tranche d'un autre départ.
    this.tranche = maladie?.tranche ?? "taux plein";
    this.tauxCsg = maladie?.tauxCsg ?? 0;
    this.revenuFiscal = maladie?.revenuFiscal ?? null;
    this.revenuPresume = maladie?.revenuPresume ?? false;
    this.aspa = maladie?.aspa ?? false;
    this.parts = maladie?.parts ?? 1;
    this.bareme = maladie?.bareme ?? null;
    this.saisie = maladie?.saisie ?? null;
    // Qui réside hors de France : la cotisation maladie sur la base du régime
    // général, sa part, et si la France prend en charge ses soins.
    this.tauxRegimeGeneral = maladie?.tauxRegimeGeneral ?? 0;
    this.partRegimeGeneral = maladie?.partRegimeGeneral ?? 0;
    this.regimesGeneraux = maladie?.regimesGeneraux ?? new Set();
    this.nonResident = maladie?.nonResident ?? false;
    this.couvert = maladie?.couvert ?? false;
    this.motifCouverture = maladie?.motifCouverture ?? "";
    // Ce qu'un euro de salaire brut laisse en net, au DERNIER revenu
    // d'activité. Zéro quand le statut n'a pas de fiche de paie : le taux
    // reste alors brut, faute de pouvoir le netter honnêtement.
    this.rapportNetBrutSalaire = rapportNetBrutSalaire;
    // Le même, sur la fiche de paie de la PROPOSITION.
    this.rapportNetBrutProposition = rapportNetBrutProposition;
  }

  static depuis(saisie, simulateur, comparaison = null) {
    // Le rapport net/brut du salaire se lit sur la DERNIÈRE fiche de paie de
    // la carrière, celle de l'année du départ : c'est l'année dont le revenu
    // sert de dénominateur au taux de remplacement.
    // La proposition a SA fiche de paie : elle prélève moins sur le même
    // brut, et le dernier salaire net auquel sa pension se compare est le sien.
    let rapport = 0;
    let rapportProposition = 0;
    const remuneration = comparaison ? comparaison.remuneration : null;
    if (remuneration !== null && remuneration !== undefined) {
      const derniere = remuneration.annees[remuneration.annees.length - 1];
      if (derniere.droitEnVigueur.brut > 0) {
        rapport = derniere.droitEnVigueur.net / derniere.droitEnVigueur.brut;
      }
      if (derniere.proposition.brut > 0) {
        rapportProposition = derniere.proposition.net / derniere.proposition.brut;
      }
    }
    // LE TAUX DE LA PERSONNE, lu sur sa pension du scénario 1 telle que la page
    // l'affiche, en euros de l'année de référence. Voir `Montants.depuis` dans
    // `contexte.py`.
    const pensions = simulateur.baremePrelevements.pensions;
    const actuel = comparaison ? (comparaison.actuel ?? null) : null;
    let servie = null;
    let coefficient = 1;
    if (actuel !== null) {
      const aujourdhui = comparaison.aujourd_hui ?? null;
      servie = aujourdhui === null ? null : aujourdhui.actuel;
      coefficient = servie !== null ? comparaison.coefficient_euros_aujourd_hui
        : comparaison.coefficient_euros_constants;
    }
    // QUI RÉSIDE HORS DE FRANCE : l'accord que le tableau donne à son État
    // aujourd'hui dit si les règlements européens décident de ses soins.
    const europeen = Boolean(saisie.residence) && reglementsEuropeens(
      simulateur.macro.paquet.accords_internationaux ?? {}, saisie.residence,
      `${String(simulateur.parametres.annee_courante).padStart(4, "0")}-01-01`);
    return Montants.duFoyer(saisie, pensions, actuel, servie, coefficient,
      rapport, rapportProposition, europeen);
  }

  /**
   * Le mode, et le taux du foyer : la CSG, la CRDS et la CASA de sa tranche,
   * et la cotisation maladie de la part complémentaire de sa pension du
   * scénario 1 ; l'allocataire de l'ASPA exonéré de tout. Voir
   * `Montants.du_foyer` dans `contexte.py`.
   */
  static duFoyer(saisie, pensions, actuel = null, aujourdhui = null, coefficient = 1,
    rapport = 0, rapportProposition = 0, europeen = false) {
    let part = 0;
    let minimum = 0;
    let pension = null;
    let partGenerale = 0;
    if (actuel !== null) {
      const [assiette, total] = assietteMaladie(pensions.regimes_maladie, actuel, aujourdhui);
      part = total > 0 ? assiette / total : 0;
      minimum = minimumVieillesseServi(actuel, aujourdhui);
      pension = total * coefficient;
      const [generale] = assietteMaladie(pensions.regimes_generaux, actuel, aujourdhui);
      partGenerale = total > 0 ? generale / total : 0;
    }
    if (saisie.residence) {
      const [couvert, motif] = couvertureFrancaise(
        saisie, actuel, europeen, pensions.non_residents_duree_minimale);
      const tauxGeneral = couvert ? pensions.non_residents_regime_general : 0;
      const maladie = couvert ? pensions.non_residents_complementaires : 0;
      return new Montants(saisie.enNet, maladie * part + tauxGeneral * partGenerale,
        rapport, rapportProposition, {
          tauxSansMaladie: 0, tauxMaladie: maladie, partMaladie: part,
          regimesMaladie: pensions.regimes_maladie,
          tauxRegimeGeneral: tauxGeneral, partRegimeGeneral: partGenerale,
          regimesGeneraux: pensions.regimes_generaux,
          tranche: "non-résident", nonResident: true, couvert, motifCouverture: motif,
          bareme: pensions, saisie,
        });
    }
    const [revenu, presume] = revenuFiscalDuFoyer(saisie, pensions, pension);
    const parts = partsDuFoyer(saisie);
    let tranche;
    if (minimum > 0) {
      tranche = pensions.bareme_csg[0];
    } else if (revenu === null) {
      tranche = pensions.bareme_csg[pensions.bareme_csg.length - 1];
    } else {
      tranche = pensions.tranche(revenu, parts);
    }
    const taux = pensions.tauxDeLaTranche(tranche);
    const maladie = pensions.maladieDeLaTranche(tranche);
    return new Montants(saisie.enNet, taux + maladie * part, rapport, rapportProposition, {
      tauxSansMaladie: taux, tauxMaladie: maladie, partMaladie: part,
      regimesMaladie: pensions.regimes_maladie,
      tranche: tranche.libelle, tauxCsg: tranche.taux, revenuFiscal: revenu,
      revenuPresume: presume, aspa: minimum > 0, parts, bareme: pensions, saisie,
    });
  }

  /**
   * Le taux de remplacement, dans la langue du mode.
   *
   * Le modèle le calcule brut sur brut. Affiché à côté de montants NETS, il
   * serait le seul chiffre de la page à parler l'autre langue — et il
   * mentirait dans un sens précis : une pension est moins prélevée qu'un
   * salaire, 9,1 % contre une vingtaine de points, si bien que le taux NET
   * dépasse le taux brut de plusieurs points. C'est un fait connu, et rarement
   * montré.
   */
  tauxRemplacement(tauxBrut, proposition = false) {
    // `proposition` prend le rapport de SA fiche de paie : le même brut y
    // laisse un net plus élevé. Voir `Montants.taux_remplacement`.
    const rapport = proposition ? this.rapportNetBrutProposition : this.rapportNetBrutSalaire;
    if (!this.net || rapport <= 0) {
      return tauxBrut;
    }
    return tauxBrut * (1 - this.tauxPension) / rapport;
  }

  /**
   * Une pension, une rente, une garantie : tout ce qui se sert après, au taux
   * de la personne — celui de sa pension du scénario 1, que les cinq autres
   * gardent.
   */
  pension(brut) {
    return this.net ? brut * (1 - this.tauxPension) : brut;
  }

  /**
   * Une part de pension dont `assiette` paie aussi la cotisation maladie : un
   * étage ou une ligne du scénario 1, et non plus un total.
   */
  pensionDAssiette(brut, assiette, assietteGenerale = 0) {
    return this.net ? this.netDAssiette(brut, assiette, assietteGenerale) : brut;
  }

  /**
   * La même, nette quel que soit le mode : la colonne du net d'un tableau qui
   * montre les deux.
   */
  netDAssiette(brut, assiette, assietteGenerale = 0) {
    return brut * (1 - this.tauxSansMaladie) - this.tauxMaladie * assiette
      - this.tauxRegimeGeneral * assietteGenerale;
  }

  /**
   * La pension d'un seul régime : la cotisation maladie y est toute ou rien,
   * 10,1 % pour une complémentaire qui la prélève, 9,1 % sinon.
   */
  pensionDuRegime(brut, regime) {
    return this.pensionDAssiette(brut, this.regimesMaladie.has(regime) ? brut : 0,
      this.regimesGeneraux.has(regime) ? brut : 0);
  }

  /**
   * La nette d'un autre départ du scénario 1, quel que soit le mode, à SA
   * tranche. Voir `Montants.net_d_un_depart` dans `contexte.py`.
   */
  netDUnDepart(total, assiette, minimum = 0, generale = 0) {
    const bareme = this.bareme;
    if (bareme === null || this.nonResident) return this.netDAssiette(total, assiette, generale);
    let tranche;
    if (minimum > 0) {
      tranche = bareme.bareme_csg[0];
    } else {
      const revenu = !this.revenuPresume && this.revenuFiscal !== null
        ? this.revenuFiscal : bareme.revenuFiscalPresume(foyer(this.saisie, total));
      tranche = bareme.tranche(revenu, this.parts);
    }
    return total * (1 - bareme.tauxDeLaTranche(tranche))
      - bareme.maladieDeLaTranche(tranche) * assiette;
  }

  /**
   * La pension du scénario 1 — du départ, ou d'aujourd'hui pour qui est déjà
   * parti —, nette de sa propre cotisation maladie.
   */
  pensionServie(actuel, aujourdhui = null) {
    const [assiette, total] = assietteMaladie(this.regimesMaladie, actuel, aujourdhui);
    const [generale] = assietteMaladie(this.regimesGeneraux, actuel, aujourdhui);
    return this.pensionDAssiette(total, assiette, generale);
  }

  /** Un salaire, lu sur la fiche de paie qui porte déjà les deux. */
  salaire(fiche) {
    return this.net ? fiche.net : fiche.brut;
  }

  get mot() {
    return this.net ? "net" : "brut";
  }

  get uniteSalaire() {
    return this.net ? "€ net/mois" : "€ brut/mois";
  }

  get unitePension() {
    return this.net ? "€ net/mois" : "€ brut/mois";
  }
}

