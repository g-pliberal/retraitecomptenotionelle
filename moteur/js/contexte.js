/**
 * Le contexte du site : ses données, et le jeu de règles sous lequel il calcule.
 *
 * Portage d'une partie de ``src/retraite_notionnelle/contexte.py`` : ce qui lit
 * les données sous un jeu de règles, dont le Python garde le centre du coût,
 * que le site lit dans son paquet. La saisie — d'une requête, la carrière,
 * l'échelle des salaires, les montants nets — n'a que cet exemplaire depuis
 * l'action 161, étape 6 : la fabrique la fait tourner par le pont
 * (`src/retraite_notionnelle/pont.mjs`).
 */

import { DateMois, MOIS_PAR_AN } from "./calendrier.js";
import { prolongerReleve, salaireMoyenAnnuel } from "./carriere.js";
import { formaterBorne } from "./regimes.js";
import { PARAMETRES_DEFAUT, cleParametres } from "./config.js";
import { AssietteActivite } from "./assiette.js";
import { chargerAvantages } from "./inventaire.js";
import { chargerFrontiere } from "./frontiere.js";
import { chargerBilan } from "./bilan.js";
import { chargerAgregats } from "./agregats.js";
import { DistributionPensions } from "./distribution.js";
import { DepensesRetraite } from "./depenses.js";
import { ComptesRetraite, varianteDuScenario } from "./equilibre.js";
import { Restitution } from "./restitution.js";
import { assietteMaladie, salaireBrutDepuisNet, salaireNetDepuisBrut } from "./remuneration.js";
import { Simulateur, niveauPourPension } from "./simulateur.js";
import { REGIMES_CODE_DES_PENSIONS } from "./droit/coordonner.js";
import * as g from "./gabarit.js";
import { agesDeLEstimation } from "./pilote.js";
import { agesBalayes, depart as departDuCycle } from "./cycle-de-vie.js";
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
 * La version du paquet que ce code lit (`VERSION`, dans
 * `scripts/construire_donnees.py`).
 *
 * Le site lit son paquet en `force-cache` : un lecteur peut recevoir ce code et
 * un paquet plus ancien, que son navigateur a gardé. Les pages qui le lisaient
 * le rattrapaient chacune à sa façon — « Pourquoi changer » et « Partager »
 * refaisaient le calcul que le paquet ne portait pas encore. Depuis le
 * 11 octobre 2026, `index.html` redemande au serveur tout paquet qui n'a pas
 * cette version, et aucune page n'a plus à savoir qu'il en existe d'autres.
 */
export const VERSION_PAQUET = 33;

/**
 * Combien d'agrégats le contexte garde en mémoire, tous jeux de règles
 * confondus. Il n'en reste qu'un par jeu, la restitution, depuis que le coût et
 * les avantages sont lus dans la table figée (11 octobre 2026) : la borne n'est
 * plus atteinte qu'au sixième jeu de règles essayé.
 */
const AGREGATS_MEMORISES = 6;

/**
 * Les données du site, et le jeu de règles sous lequel on les lit.
 *
 * Un contexte, c'est deux choses : des données coûteuses à charger, et UN jeu
 * de paramètres — `base` — sous lequel tout ce que la page demande est
 * calculé. `simulateur()` et `restitution()` répondent sous ce jeu-là, sans
 * qu'aucune page ait à le leur redire ; `cout()`, `avantages()` et
 * `casTypes()` rendent la table que le Python a fabriquée sous la référence.
 *
 * Les trois pages qui AGRÈGENT — Cas types, Coût, Avantages — se rendaient
 * sous un contexte dérivé par `pour`, portant les réglages de l'adresse. Elles
 * ne montrent plus que la référence depuis le 11 octobre 2026, et lisent ce que
 * le Python a fabriqué sous elle (`agregats()`) : seul le simulateur dérive
 * encore un contexte.
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
    // distribution des pensions, assiette, inventaire des avantages, et les
    // deux tables figées. Ces séries sont lues, jamais calculées : un
    // changement de règle ne les déplace pas.
    this._donnees = memoires ? memoires.donnees : new Map();
    // Les agrégats, eux, dépendent des règles : une restitution par jeu de
    // paramètres.
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

  /**
   * Ce que les trois pages qui agrègent lisent du modèle — une DONNÉE, pas un
   * agrégat : la table que `scripts/construire_donnees.py` a fabriquée sous les
   * réglages de référence (`agregats.js`), quels que soient ceux de `base`.
   */
  agregats() {
    return this._donnee("agregats", () => chargerAgregats(this.paquet.agregats));
  }

  /** La grille des carrières types, figée sous la référence. */
  casTypes() {
    return this.agregats().casTypes;
  }

  /** L'inventaire des avantages non contributifs — une donnée, pas un calcul. */
  inventaireAvantages() {
    return this._donnee("inventaireAvantages", () => chargerAvantages(this.paquet));
  }

  /** Le versant inverse : ce qu'on cotise sans rien acquérir. Une donnée. */
  frontiere() {
    return this._donnee("frontiere", () => chargerFrontiere(this.paquet));
  }

  /**
   * Ce que les avantages non contributifs coûtent, année par année : figé sous
   * la référence comme la grille (`agregats()`). Il se calculait ici, sous les
   * règles de `base`, jusqu'au 11 octobre 2026.
   */
  avantages() {
    return this.agregats().avantages;
  }

  /**
   * Le coût agrégé de tous les systèmes : figé sous la référence comme la
   * grille (`agregats()`). Il se calculait ici, sous les règles de `base` —
   * cinq secondes chez le lecteur —, jusqu'au 11 octobre 2026.
   */
  cout() {
    return this.agregats().cout;
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
    // La part de primes de la saisie : la retenue d'un fonctionnaire n'est
    // assise que sur son traitement (`blocDroitEnVigueur`).
    const versBrut = (netMensuel, statut) => salaireBrutDepuisNet(
      bareme, macro, simulateur.catalogue, simulateur.affiliations,
      statut, annee, netMensuel * MOIS_PAR_AN, saisie.primes,
    ) / MOIS_PAR_AN;
    const versNet = (brutMensuel, statut) => salaireNetDepuisBrut(
      bareme, macro, simulateur.catalogue, simulateur.affiliations,
      statut, annee, brutMensuel * MOIS_PAR_AN, saisie.primes,
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
   * carrière de cette saisie (`agesDeLEstimation`, pilote.js). Chaque départ
   * refait la carrière à sa date, comme la saisie la ferait si on y écrivait
   * cette date, et la liquide : le brut de chaque étage, annuel, en euros
   * constants de l'année de référence, la convention de l'estimation
   * indicative globale. Deux âges confondus font un départ.
   * Vide pour une saisie par la pension, pour qui est déjà parti, pour une
   * carrière dont la saisie date elle-même des pensions — demandées régime par
   * régime, ouvertes par l'invalidité ou par la radiation —, quand le droit
   * n'oppose aucun âge, ou quand la saisie ou le modèle refusent la carrière à
   * l'un des âges ; un départ d'une année déjà passée est omis.
   */
  departsDeLEstimation(saisie) {
    const estimation = this._estimation(saisie);
    if (estimation === null) {
      return [];
    }
    const { parametres, simulateur, batir } = estimation;
    const annee = parametres.annee_courante;
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
   * La carrière de la saisie à plusieurs âges de départ, et ce qu'en donne,
   * en net et après impôt, chacun des six systèmes : à chaque âge de
   * `agesBalayes` (cycle-de-vie.js), de `pas` en `pas`, de l'âge d'ouverture
   * à l'âge d'annulation de la décote, `depart`, le `Depart` de
   * `balayageDUneCarriere` sous la convention de l'OCDE, ou du COR avec
   * `cor`, et `comparaison`, qui en passe les montants aux euros de la page
   * (`enEurosConstants`). Vide dans les cas où `departsDeLEstimation` l'est ;
   * un départ d'une année déjà passée est omis. Le site seul le montre ; les
   * cas types du COR passent par `scripts/cycle_de_vie.mjs`.
   */
  balayageDeLEstimation(saisie, pas = 1.0, cor = false) {
    const estimation = this._estimation(saisie);
    if (estimation === null) {
      return [];
    }
    const { parametres, simulateur, batir } = estimation;
    try {
      return agesBalayes(simulateur, batir, saisie.liquidation, pas)
        .map((age) => {
          const comparaison = simulateur.simuler(batir(age));
          return {
            depart: departDuCycle(simulateur, comparaison, cor, age, "prix"), comparaison,
          };
        })
        .filter(({ depart: lui }) => lui.annee >= parametres.annee_courante);
    } catch (erreur) {
      // Comme `departsDeLEstimation` : une carrière refusée à l'un des âges
      // tait le bloc ; une faute de programme remonte.
      if (erreur instanceof TypeError || erreur instanceof ReferenceError
          || erreur instanceof RangeError || erreur instanceof SyntaxError) {
        throw erreur;
      }
      return [];
    }
  }

  /**
   * Ce que les départs d'une saisie demandent — ses paramètres, son
   * simulateur, et `batir(age)`, sa carrière liquidée à `age` —, ou `null`
   * quand ils ne se chiffrent pas : une saisie par la pension, des pensions
   * que la saisie date elle-même, un départ d'une année déjà passée.
   */
  _estimation(saisie) {
    if (saisie.parPension || saisie.demandes.length > 0 || saisie.invalidite !== null
        || saisie.radiation_invalidite !== null) {
      return null;
    }
    const parametres = saisie.parametres(this.base);
    if (saisie.dateLiquidation.annee < parametres.annee_courante) {
      return null;
    }
    // La saisie refuse ce que sa date rend incohérent — un métier commencé
    // après le départ —, avec ses mots, avant le modèle.
    const batir = (age) => {
      const autre = new Saisie({ ...saisie, liquidation: age });
      autre.verifier();
      return this.carriere(autre);
    };
    return { parametres, simulateur: this.simulateur(parametres), batir };
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
    const dispenses = saisie.dispensesAnalysees(dispensesConnues(this.paquet));
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
      temps_partiel: saisie.tempsPartielAnalyse(),
      nombre_enfants: saisie.enfants,
      naissances_enfants: saisie.naissancesEnfants(),
      conjoint: saisie.conjointDeclare(),
      deces: saisie.decesDeclare(),
      retraite_progressive: saisie.retraiteProgressiveDeclaree(),
      emploi_retraite: emploiRetraite,
      demandes_de_pension: demandes,
      invalidite: saisie.invaliditeDeclaree(),
      etranger,
      periodes_assimilees: saisie.periodesAssimileesDeclarees(),
      dispenses,
      reversion_agricole: saisie.reversionAgricoleDeclaree(),
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
   * le fait toujours, et dont le conjoint collaborateur ne cotise que la part de
   * son option (`niveauxDeLaPension`). Qui veut un revenu par métier le saisit,
   * ou dépose son relevé.
   *
   * LA CIBLE EST RAMENÉE À CE QUE LE MODÈLE CALCULE, et dans cet ordre : la
   * pension saisie est mensuelle, nette peut-être, en euros constants de
   * l'année de référence ; le scénario 1 rend une pension annuelle, brute, en
   * euros de l'année de liquidation, que chaque tour nette quand la saisie
   * l'est. Le coefficient des euros constants ne
   * dépend que de l'année de liquidation, jamais du niveau de revenu : il se
   * calcule une fois, avant la dichotomie, et non à chaque tour.
   *
   * POUR UN RETRAITÉ, LA CIBLE EST LA PENSION D'AUJOURD'HUI. Il saisit ce qu'il
   * touche, pas ce qu'il touchait le premier mois : la dichotomie compare donc
   * au montant saisi la pension du départ revalorisée comme le droit l'a fait
   * depuis — l'échéance de l'année courante de `Simulateur.echeancier` —, en
   * euros de l'année courante. Cette revalorisation-là dépend du niveau, par la
   * tranche de 2020 et par le poids de la complémentaire : elle se refait à
   * chaque tour, et c'est le prix de l'exactitude.
   */
  _simulerParPension(simulateur, saisie, batir, parcours) {
    const montants = Montants.depuis(saisie, simulateur);
    // Pour un retraité, la cible est la pension d'AUJOURD'HUI : il saisit ce
    // qu'il touche, pas ce qu'il touchait le premier mois.
    const parametres = simulateur.parametres;
    const retraite = saisie.dateDe(saisie.liquidation).annee < parametres.annee_courante;
    const constants = simulateur.macro.coefficientPrix(
      retraite ? parametres.annee_courante : saisie.dateDe(saisie.liquidation).annee,
      parametres.annee_euros_constants,
    );
    // La cible reste dans la langue de la saisie, nette peut-être : le taux
    // qui sépare une pension de sa nette dépend de sa part complémentaire,
    // donc du niveau cherché. C'est la pension de chaque niveau qu'on nette, et
    // non la cible qu'on remonte au brut.
    const cible = saisie.pension * MOIS_PAR_AN / constants;
    const pensionDeNiveau = (niveau) => {
      const carriere = batir(saisie.niveauxDeLaPension(niveau, parcours));
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
    const carriere = batir(saisie.niveauxDeLaPension(trouve.niveau, parcours));
    verifierStatutsOuverts(simulateur.affiliations, carriere, parcours);
    verifierRadiationPourInvalidite(simulateur.affiliations, carriere);
    const comparaison = simulateur.simuler(carriere);
    comparaison.niveau_inverse = trouve;
    return comparaison;
  }

  /**
   * Le relevé que `simuler` calcule : celui de la saisie, puis les années qui
   * le séparent du départ (`releveJusquAuDepart`). La page dit celles qu'elle
   * a ajoutées.
   */
  releveProlonge(saisie) {
    const simulateur = this.simulateur(saisie.parametres(this.base));
    const motifs = Object.keys(this.paquet.periodes_non_travaillees ?? {});
    return releveJusquAuDepart(simulateur, saisie,
      saisie.releveAnalyse(motifs, dispensesConnues(this.paquet)), motifs);
  }

  /**
   * Le contrôle du relevé de la saisie (action 138, étape 10) : chacune de ses
   * années de salarié du régime général ou des salariés agricoles dont il
   * porte les trimestres (`auRevenu`), avec ceux que le calcul en `retenus`,
   * ceux que son revenu `valides` — ceux de la carrière du même relevé rebâtie
   * sans ses trimestres, que le modèle déduit du revenu, sous les mêmes bornes,
   * dont celle de l'année du départ — et le `seuil` d'un trimestre de l'année
   * (`seuilDUnTrimestre`, R. 351-9). Le calcul, lui, garde les trimestres du
   * relevé. Vide quand la saisie n'est pas un relevé, qu'aucune année ne se
   * contrôle, ou que la saisie refuse la carrière. Le site seul le montre.
   */
  controleDuReleve(saisie) {
    if (!saisie.releveActif) {
      return [];
    }
    try {
      const simulateur = this.simulateur(saisie.parametres(this.base));
      const motifs = Object.keys(this.paquet.periodes_non_travaillees ?? {});
      const releve = saisie.releveAnalyse(motifs, dispensesConnues(this.paquet));
      const controlees = releve.filter((ligne) => ligne.trimestres !== null
        && ligne.type_periode === "emploi"
        && simulateur.affiliations.contient(ligne.affiliation)
        && auRevenu(simulateur.affiliations, ligne.affiliation, ligne.annee));
      if (controlees.length === 0) {
        return [];
      }
      const compter = (relevee) => {
        const parAnnee = new Map();
        for (const ligne of this.carriereRelevee(simulateur, relevee, motifs, false).lignes) {
          if (ligne.type_periode === "emploi" && !parAnnee.has(ligne.annee)) {
            parAnnee.set(ligne.annee, ligne.trimestres_valides);
          }
        }
        return parAnnee;
      };
      const retenus = compter(saisie);
      const valides = compter(new Saisie({
        ...saisie,
        releve: releve.map((ligne) => `${ligne.annee}:${ligne.affiliation}:${ligne.revenu}`)
          .join("\n"),
      }));
      return controlees
        .filter((ligne) => retenus.has(ligne.annee) && valides.has(ligne.annee))
        .map((ligne) => ({
          annee: ligne.annee,
          affiliation: ligne.affiliation,
          revenu: ligne.revenu,
          retenus: retenus.get(ligne.annee),
          valides: valides.get(ligne.annee),
          seuil: simulateur.macro.seuilDUnTrimestre(ligne.annee),
        }));
    } catch (erreur) {
      // Comme `departsDeLEstimation` : une carrière que la saisie refuse tait
      // le contrôle ; une faute de programme remonte.
      if (erreur instanceof TypeError || erreur instanceof ReferenceError
          || erreur instanceof RangeError || erreur instanceof SyntaxError) {
        throw erreur;
      }
      return [];
    }
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
   * relevé, pour qui l'a déjà prolongé à sa façon
   * (`scripts/estimation_officielle.py`, par le pont), et pour le contrôle du
   * relevé.
   */
  carriereRelevee(simulateur, saisie, motifs, prolonger = true) {
    let releve = saisie.releveAnalyse(motifs, dispensesConnues(this.paquet));
    for (const ligne of releve) {
      if (!simulateur.affiliations.contient(ligne.affiliation)) {
        throw new ErreurSaisie(
          `Relevé, année ${ligne.annee} : statut d'affiliation inconnu `
          + `« ${ligne.affiliation} ».`,
        );
      }
      if (ligne.trimestres !== null && !Number.isInteger(ligne.trimestres)
          && !auJour(simulateur.affiliations, ligne.affiliation, ligne.annee)) {
        throw new ErreurSaisie(
          `Relevé, année ${ligne.annee} : une fraction de trimestre ne se `
          + "déclare que des services de la fonction publique, qui se "
          + `comptent au jour ; « ${ligne.affiliation} » valide des `
          + "trimestres entiers.",
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
      periodes_assimilees: saisie.periodesAssimileesDeclarees(),
      reversion_agricole: saisie.reversionAgricoleDeclaree(),
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
 * reçoit. Chaque État s'y contrôle sur le tableau des accords : c'est ici qu'un
 * code inconnu se refuse, la saisie n'ayant pas les données. Le montant de
 * chaque pension étrangère, saisi en euros d'aujourd'hui, y devient son montant
 * `mensuel` en euros de l'année où elle commence : il suit les prix, faute de
 * connaître la revalorisation de l'autre État.
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
 * estimation retraite » prolonge les revenus jusqu'au départ qu'elle chiffre.
 * Sans cela, qui dépose son relevé à quarante ans recevait la pension de qui
 * cesserait de travailler le jour même.
 *
 * Les années ajoutées prennent leur motif comme celles d'une carrière de
 * métiers (`interruptionsApres`) : une période à l'étranger, puis le champ
 * « Interruptions », qui garde le dernier mot — `sans_activite` pour qui ne
 * travaille plus. Le champ « Temps partiel » et la retraite progressive les
 * mettent à temps partiel ; celui des dispenses de l'assiette minimale leur
 * donne son motif. La radiation pour invalidité, qui clôt l'emploi de
 * fonctionnaire, les arrête à sa date quand elle ne tombe pas avant la
 * dernière année du relevé : ce qui la suit, le relevé ne le dit pas.
 *
 * Rien ne s'ajoute à qui est parti une année déjà passée : son relevé dit
 * toute sa carrière, et ce qui y manque n'a pas été travaillé.
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
    saisie.interruptionsApres(new DateMois(derniere + 1, 1), motifs), progressive,
    saisie.tempsPartielAnalyse(), saisie.dispensesAnalysees());
}

/**
 * Les motifs de dispense de l'assiette minimale que le paquet connaît : la
 * saisie refuse les autres sur la table même qui calcule, comme les motifs
 * d'interruption (`legislation/dispenses_assiette_minimale.yaml`).
 */
function dispensesConnues(paquet) {
  return Object.keys(paquet.dispenses_assiette_minimale ?? {}).sort();
}

/**
 * Les dates de demande que la saisie dit, chacune pour un régime que le
 * catalogue connaît : c'est ici qu'un code inconnu se refuse, la saisie n'ayant
 * pas le catalogue.
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

/** La carrière des métiers, à leurs niveaux de revenu, contrôlée. */
function carriereParcourue(simulateur, parcours, batir) {
  const carriere = batir(parcours.map((metier) => metier.niveau_salaire));
  verifierStatutsOuverts(simulateur.affiliations, carriere, parcours);
  verifierRadiationPourInvalidite(simulateur.affiliations, carriere);
  return carriere;
}

/**
 * Le départ `quoi` de « Mon estimation retraite », tel que le scénario 1 le
 * sert : la carrière liquidée à l'âge que `agesDeLEstimation` (pilote.js) a
 * trouvé, chiffrée étage par étage. Les montants sont bruts, annuels, en euros
 * constants de l'année de référence : la page les divise par douze. `etages`
 * additionne, étage par étage (base, complémentaire, intégré, additionnel), la
 * pension de chaque régime, minima compris, et la part qu'il sert de la
 * majoration pour enfants ; le minimum vieillesse, qu'aucun régime ne sert et
 * que l'estimation ignore, reste à part. Le `quoi` rendu porte les âges de
 * `DEPARTS_DE_L_ESTIMATION` (pilote.js) que le départ réunit : le sien, puis
 * ceux que `departsDeLEstimation` y ajoute, qui se confondent avec lui ;
 * `date`, son mois, « AAAA-MM ».
 * Le seul exemplaire depuis l'action 161, étape 6 : son jumeau Python, qui ne
 * servait plus qu'à confronter les deux moteurs, est retiré.
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
    // Ce que la cotisation maladie de 1 % frappe dans `etages` : les lignes des
    // complémentaires qui la prélèvent, sans leur majoration pour enfants
    // (`assietteMaladie`, remuneration.js).
    assiette_maladie: assiette,
    // La pension de base du régime général, qu'un non-résident paie à son
    // propre taux (L. 131-9 ; D. 242-8).
    assiette_regime_general: generale,
    get total() {
      return Object.values(this.etages).reduce((somme, montant) => somme + montant, 0.0);
    },
  };
}

/**
 * La radiation pour invalidité clôt un emploi de fonctionnaire civil — de
 * l'État, territorial, hospitalier, ouvrier de l'État —, et la carrière ne
 * reste pas dans la fonction publique après elle : c'est ici qu'elle se
 * contrôle, la saisie n'ayant pas les affiliations. Le militaire radié par
 * suite d'infirmités relève d'autres règles, que le modèle ne sert pas (fiche
 * `retraite_pour_invalidite_fonction_publique`).
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

/**
 * Ce statut verse-t-il, cette année-là, à un régime du code des pensions, qui
 * compte ses services au jour (R. 26) ? Seule sa ligne de relevé peut alors
 * porter une fraction de trimestre.
 */
function auJour(affiliations, affiliation, annee) {
  return affiliations.periodes(affiliation).some((periode) => periode.debut <= annee
    && (periode.fin === null || periode.fin === undefined || annee <= periode.fin)
    && (periode.regimes ?? []).some((code) => REGIMES_CODE_DES_PENSIONS.has(code)));
}

/** Les régimes de base qui valident l'année d'un salarié à son revenu. */
const REGIMES_AU_REVENU = new Set(["regime_general", "msa_salaries"]);

/**
 * L'année d'un statut se contrôle-t-elle au revenu ? Celle d'un salarié du
 * régime général ou des salariés agricoles : R. 351-9 lui compte autant de
 * trimestres que son revenu atteint de fois le seuil de l'année. Ni la
 * fonction publique et les régimes spéciaux, qui comptent leurs services au
 * temps, ni l'indépendant, qui valide aussi par son assiette minimale et les
 * cotisations qu'il a payées (`controleDuReleve`).
 */
function auRevenu(affiliations, affiliation, annee) {
  return !affiliations.sansEmployeur(affiliation)
    && affiliations.periodes(affiliation).some((periode) => periode.debut <= annee
      && (periode.fin === null || periode.fin === undefined || annee <= periode.fin)
      && (periode.regimes ?? []).some((code) => REGIMES_AU_REVENU.has(code)));
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

/**
 * Les pensions du foyer, une par pensionné : la sienne, et les ressources que
 * la saisie prête au conjoint déclaré.
 */
function foyer(saisie, pension) {
  const pensions = [pension];
  if (saisie.conjoint && saisie.ressources_conjoint) pensions.push(saisie.ressources_conjoint);
  return pensions;
}

/**
 * La pension que la personne saisit, annuelle et brute, en euros de l'année de
 * référence. Nette, elle remonte au brut par la tranche où ce brut tombe : la
 * première dont le revenu présumé est bien le sien — la nette baisse d'un cran
 * à chaque seuil, si bien qu'une nette peut avoir deux bruts, et c'est le plus
 * petit. La cotisation maladie, qui dépend de la part complémentaire, n'y
 * entre pas.
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
 * Le revenu fiscal de référence du foyer, et s'il est présumé.
 *
 * Le revenu que la saisie dit l'emporte. Sinon, la présomption
 * `aucun_autre_revenu_que_ses_pensions` : la pension du système 1 — celle que
 * la personne saisit quand elle saisit sa pension, sinon `pension`, celle que
 * la simulation lui sert, annuelle, en euros de l'année de référence —, et les
 * ressources du conjoint, abattues de 10 %. `null` quand il n'y a encore ni
 * l'une ni l'autre.
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

/**
 * L'instrument des accords qui coordonne aussi l'assurance maladie : les
 * règlements européens (le tableau des accords).
 */
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
 * France (L. 160-3), et pourquoi. Sous les règlements européens, l'État de
 * résidence est compétent s'il sert lui-même une pension (règlement (CE)
 * n° 883/2004, art. 23), la France sinon (art. 24). Ailleurs, la pension
 * française doit rémunérer quinze années d'assurance (L. 160-3, b) — les
 * conventions bilatérales, qui peuvent rendre la France seule compétente (a),
 * ne sont pas lues. Sans carrière calculée, la prise en charge est présumée.
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

/**
 * Le minimum vieillesse que le scénario 1 sert : l'ASPA de l'échéance pour qui
 * est déjà parti, celle du départ sinon.
 */
function minimumVieillesseServi(actuel, aujourdhui = null) {
  if (aujourdhui !== null) return aujourdhui.minimum_vieillesse;
  let total = 0;
  for (const avantage of actuel.avantages_appliques) {
    if (avantage.code === "minimum_vieillesse") total += avantage.montant;
  }
  return total;
}

/**
 * La cotisation maladie de la SNCF et des mines en part de la pension du
 * scénario 1, au taux plein, ou aux taux du `nonResident` : chaque pension de
 * leurs régimes, menée par `coefficient` en euros de l'année de référence,
 * celle des plafonds, majoration pour enfants exclue (`assietteMaladie`, dans
 * remuneration.js) : aux mines, l'article 91 du décret n° 46-2769 l'excepte
 * lui-même des avantages accessoires qu'il prélève (art. 139, comme
 * l'allocation pour enfant à charge de l'art. 141), et ceux qu'il prend, le
 * dixième du fond (art. 138) et le conjoint à charge (art. 140), le modèle ne
 * les sert pas.
 */
export function partDesRegimesSpeciaux(pensions, actuel, aujourdhui = null, coefficient = 1,
  nonResident = false) {
  if (pensions.regimes_speciaux.length === 0) return 0;
  const [, total] = assietteMaladie(new Set(), actuel, aujourdhui);
  if (total <= 0) return 0;
  const montants = new Map();
  for (const special of pensions.regimes_speciaux) {
    for (const regime of [...special.regimes].sort()) {
      montants.set(regime, assietteMaladie(new Set([regime]), actuel, aujourdhui)[0] * coefficient);
    }
  }
  return pensions.maladieDesRegimesSpeciaux(montants, false, nonResident) / (total * coefficient);
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
    // Ce qui sépare une pension brute de sa nette, POUR CETTE PERSONNE : CSG
    // 8,30 %, CRDS 0,50 %, CASA 0,30 %, et la cotisation maladie de 1 % sur la
    // part de sa pension du scénario 1 que des complémentaires servent. Les
    // cinq autres scénarios le gardent : la réforme ne change pas ses
    // prélèvements, par hypothèse. Voir `PrelevementsPension` (remuneration.js).
    this.tauxPension = tauxPension;
    // Le taux d'une pension de base, la cotisation maladie, la part de la
    // pension du scénario 1 qui la paie, et les régimes qui la prélèvent.
    this.tauxSansMaladie = maladie?.tauxSansMaladie ?? tauxPension;
    this.tauxMaladie = maladie?.tauxMaladie ?? 0;
    this.partMaladie = maladie?.partMaladie ?? 0;
    this.regimesMaladie = maladie?.regimesMaladie ?? new Set();
    // La cotisation maladie de la SNCF et des mines, en part de la pension du
    // scénario 1 : au taux plein, et telle que la tranche du foyer la prélève ;
    // au non-résident que la France couvre, à ses taux de L. 131-9. Un autre
    // départ garde la part du sien (`netDUnDepart`).
    this.partRegimesSpeciaux = maladie?.partRegimesSpeciaux ?? 0;
    this.tauxRegimesSpeciaux = maladie?.tauxRegimesSpeciaux ?? 0;
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
    // Qui réside hors de France : la cotisation maladie sur la pension de base
    // du régime général, et la part de celle-ci dans la pension ; si la France
    // prend en charge ses soins, et pourquoi (`couvertureFrancaise`).
    this.tauxRegimeGeneral = maladie?.tauxRegimeGeneral ?? 0;
    this.partRegimeGeneral = maladie?.partRegimeGeneral ?? 0;
    this.regimesGeneraux = maladie?.regimesGeneraux ?? new Set();
    this.nonResident = maladie?.nonResident ?? false;
    this.couvert = maladie?.couvert ?? false;
    this.motifCouverture = maladie?.motifCouverture ?? "";
    // Ce qu'un euro de salaire brut laisse en net, au DERNIER revenu
    // d'activité — le dénominateur du taux de remplacement. Zéro quand le
    // statut n'a pas de fiche de paie : le taux reste alors brut, faute de
    // pouvoir le netter honnêtement.
    this.rapportNetBrutSalaire = rapportNetBrutSalaire;
    // Le même, sur la fiche de paie de la PROPOSITION.
    this.rapportNetBrutProposition = rapportNetBrutProposition;
  }

  static depuis(saisie, simulateur, comparaison = null) {
    // Le rapport net/brut du salaire se lit sur la DERNIÈRE fiche de paie de
    // la carrière, celle de l'année du départ : c'est l'année dont le revenu
    // sert de dénominateur au taux de remplacement.
    // La proposition a SA fiche de paie : elle prélève moins sur le même
    // brut, et le dernier salaire net auquel sa pension se compare est le sien
    // — celui que la ligne affiche à côté de sa pension.
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
    // LE TAUX DE LA PERSONNE, lu sur SA pension du scénario 1 telle que la page
    // l'affiche — au départ, ou aujourd'hui pour qui est déjà parti —, en euros
    // de l'année de référence.
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
   * Le mode, et le taux du foyer (action 138, étape 2) : la CSG, la CRDS et la
   * CASA de SA tranche de L. 136-8, et la cotisation maladie de la part
   * complémentaire de sa pension du scénario 1 — `actuel` au départ,
   * `aujourdhui` pour qui est déjà parti, que `coefficient` mène en euros de
   * l'année de référence. Un allocataire de l'ASPA est exonéré de tout
   * (L. 136-1-2, II 1° ; D. 242-9, 2°). Sans pension, ni saisie qui en dise
   * une, ni revenu fiscal dit : le taux plein, comme avant toute simulation.
   * Les cinq autres scénarios gardent ce taux : la réforme, par hypothèse, ne
   * change pas les prélèvements de la personne.
   *
   * QUI RÉSIDE HORS DE FRANCE ne doit ni CSG, ni CRDS, ni CASA (L. 136-1) ; si
   * la France prend en charge ses soins (`couvertureFrancaise`), une
   * cotisation maladie à ses taux particuliers, sur la pension de base du
   * régime général et sur les complémentaires (L. 131-9 ; D. 242-8), et sur
   * celles de la SNCF et des mines, aux leurs.
   *
   * LA SNCF ET LES MINES prélèvent encore leur propre cotisation maladie sur
   * leurs pensions (`maladie_regimes_speciaux`), 0,70 % sous un plafond et
   * 0,50 %, aux mêmes tranches que celle des complémentaires :
   * `partRegimesSpeciaux` est ce qu'elle prend à la pension, au taux plein.
   */
  static duFoyer(saisie, pensions, actuel = null, aujourdhui = null, coefficient = 1,
    rapport = 0, rapportProposition = 0, europeen = false) {
    let part = 0;
    let minimum = 0;
    let pension = null;
    let partGenerale = 0;
    let speciaux = 0;
    let speciauxNonResident = 0;
    if (actuel !== null) {
      const [assiette, total] = assietteMaladie(pensions.regimes_maladie, actuel, aujourdhui);
      part = total > 0 ? assiette / total : 0;
      minimum = minimumVieillesseServi(actuel, aujourdhui);
      pension = total * coefficient;
      const [generale] = assietteMaladie(pensions.regimes_generaux, actuel, aujourdhui);
      partGenerale = total > 0 ? generale / total : 0;
      speciaux = partDesRegimesSpeciaux(pensions, actuel, aujourdhui, coefficient);
      if (saisie.residence) {
        speciauxNonResident = partDesRegimesSpeciaux(
          pensions, actuel, aujourdhui, coefficient, true);
      }
    }
    if (saisie.residence) {
      const [couvert, motif] = couvertureFrancaise(
        saisie, actuel, europeen, pensions.non_residents_duree_minimale);
      const tauxGeneral = couvert ? pensions.non_residents_regime_general : 0;
      const maladie = couvert ? pensions.non_residents_complementaires : 0;
      const speciauxDus = couvert ? speciauxNonResident : 0;
      return new Montants(saisie.enNet,
        maladie * part + tauxGeneral * partGenerale + speciauxDus,
        rapport, rapportProposition, {
          tauxSansMaladie: 0, tauxMaladie: maladie, partMaladie: part,
          regimesMaladie: pensions.regimes_maladie,
          tauxRegimeGeneral: tauxGeneral, partRegimeGeneral: partGenerale,
          regimesGeneraux: pensions.regimes_generaux,
          partRegimesSpeciaux: speciauxDus, tauxRegimesSpeciaux: speciauxDus,
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
    const regimesSpeciaux = tranche.maladie ? speciaux : 0;
    return new Montants(saisie.enNet, taux + maladie * part + regimesSpeciaux, rapport,
      rapportProposition, {
      tauxSansMaladie: taux, tauxMaladie: maladie, partMaladie: part,
      regimesMaladie: pensions.regimes_maladie,
      partRegimesSpeciaux: speciaux, tauxRegimesSpeciaux: regimesSpeciaux,
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
    // laisse un net plus élevé, et le taux de la proposition se comparait
    // jusqu'au 22 septembre 2026 au net du droit en vigueur, qu'elle ne
    // prélève pas.
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
   * Une part de pension dont `assiette` paie aussi la cotisation maladie des
   * complémentaires, et `assietteGenerale` celle d'un non-résident sur la base
   * du régime général : un étage ou une ligne du scénario 1, et non plus un
   * total ; `lignes` (une `Map`), la pension de chaque régime qu'elle contient.
   */
  pensionDAssiette(brut, assiette, assietteGenerale = 0, lignes = null) {
    return this.net ? this.netDAssiette(brut, assiette, assietteGenerale, lignes) : brut;
  }

  /**
   * La même, nette quel que soit le mode : la colonne du net d'un tableau qui
   * montre les deux. La cotisation de la SNCF et des mines s'y prend sur les
   * `lignes` de leurs régimes, majoration pour enfants exclue, sous le
   * plafond : celle d'un étage, la sienne ; sans `lignes`, au prorata de
   * `brut`, exacte sur un total.
   */
  netDAssiette(brut, assiette, assietteGenerale = 0, lignes = null) {
    const prorata = lignes === null ? this.tauxRegimesSpeciaux : 0;
    const speciale = lignes === null ? 0 : this._maladieDesRegimesSpeciaux(lignes);
    return brut * (1 - this.tauxSansMaladie - prorata) - speciale
      - this.tauxMaladie * assiette
      - this.tauxRegimeGeneral * assietteGenerale;
  }

  /**
   * La pension d'un seul régime : chaque cotisation maladie y est toute ou
   * rien ; celle de la SNCF, sous son plafond, de moitié pour une `reversion`.
   * La `majoration` pour enfants que `brut` contient paie la CSG, la CRDS et la
   * CASA, mais aucune cotisation maladie (L. 131-2, 1°), comme celle d'un
   * étage.
   */
  pensionDuRegime(brut, regime, reversion = false, majoration = 0) {
    if (!this.net) return brut;
    const assiette = brut - majoration;
    const net = brut * (1 - this.tauxSansMaladie)
      - this.tauxMaladie * (this.regimesMaladie.has(regime) ? assiette : 0)
      - this.tauxRegimeGeneral * (this.regimesGeneraux.has(regime) ? assiette : 0);
    return net - this._maladieDesRegimesSpeciaux(new Map([[regime, assiette]]), reversion);
  }

  /**
   * La cotisation de la SNCF et des mines sur `lignes`, due quand la tranche
   * du foyer prélève la maladie des complémentaires, même si sa propre pension
   * n'en sert pas : la réversion d'un autre ; au non-résident que la France
   * couvre, à ses taux de L. 131-9.
   */
  _maladieDesRegimesSpeciaux(lignes, reversion = false) {
    if (this.tauxMaladie <= 0 || this.bareme === null) return 0;
    return this.bareme.maladieDesRegimesSpeciaux(lignes, reversion, this.nonResident);
  }

  /**
   * La nette d'un autre départ du scénario 1 — un âge de l'estimation
   * officielle —, quel que soit le mode, à SA tranche : sous la présomption,
   * son revenu fiscal est fait de sa propre pension. `total`, `assiette` et
   * `minimum` sont annuels, en euros de l'année de référence.
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
    const speciaux = tranche.maladie ? this.partRegimesSpeciaux : 0;
    return total * (1 - bareme.tauxDeLaTranche(tranche) - speciaux)
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

