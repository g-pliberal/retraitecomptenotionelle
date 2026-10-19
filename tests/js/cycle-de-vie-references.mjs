/**
 * Le cycle de vie que `tests/test_cycle_de_vie_references.py` confronte au
 * COR, à TRAJECTOiRE, à l'OCDE, à l'ETK et au simulateur du COR, calculé par
 * le portage (`moteur/js/cycle-de-vie.js`), celui que le site fait tourner, au
 * lieu de son jumeau Python (action 161, étape 5).
 *
 * Le Python résout les carrières des références — la saisie que TRAJECTOiRE a
 * bâtie, les options d'un cas type et l'âge où le pilote le fait partir,
 * celles du salarié de l'OCDE — et ce qu'elles publient ; ce programme simule
 * et calcule le reste. Il lit sur son entrée standard `{paquet, demande}` :
 * `paquet`, celui des données du jour (`pont.paquet_des_donnees`), non celui
 * du dépôt, que seule la fabrique suivante refait ; `demande`, une ou
 * plusieurs de ces lectures, chacune sous son nom :
 *
 * - `indicateurs` : `{cas: [{cle, requete}], conventions}` — les indicateurs
 *   du scénario 1 de chaque saisie, simulée comme le site la simule, sous
 *   chacune des `conventions` : `ocde`, `cor`, ou `cor_brute`, celle du COR
 *   sur la pension brute ;
 * - `rendements_par_regime` : `{cas: [{cle, options}], agirc_arrco}` — le
 *   rendement interne net du scénario 1 de chaque carrière, aux options de
 *   `carriereSimple`, sous les conventions du COR : en tout, et celui de la
 *   Cnav et de l'Agirc-Arrco (les régimes `agirc_arrco`), avec et sans les
 *   contributions d'équilibre, chacun sur ses cotisations et sa pension ;
 * - `trajectoire` : `{cas: [{cle, requete, duree_relative, pension,
 *   pension_nette}], taux_moyens_arrco, regimes_arrco, regimes_etat}` — de
 *   chaque saisie, l'âge du départ et les années de carrière ; les indicateurs
 *   du scénario 1 sous le décès que la durée de retraite rapportée à la
 *   carrière (`duree_relative`) implique, les deux sexes réunis, et, sous la
 *   même convention, ceux du flux recalé sur la `pension` de départ, ceux des
 *   cotisations aux taux moyens de l'Arrco, ceux de la seule retenue de
 *   l'agent les années à l'État ; et le remplacement net de `pension_nette` ;
 * - `ocde` : `{projection, indexation, cas: [{cle, options, taux_brut}]}` —
 *   de chaque carrière, sous le jeu de projection `projection`, le taux de
 *   remplacement brut et le patrimoine retraite ; sous l'impôt au barème
 *   projeté sur `indexation`, le dernier revenu, brut, net et après impôt, la
 *   part de la pension que les prélèvements de l'année du départ retiennent,
 *   l'impôt d'une année entière de la pension brute de `taux_brut` fois le
 *   dernier revenu, le patrimoine et le taux de remplacement après impôt ;
 * - `diviseurs` : `{cas: [{cle, generation, age}]}` — le diviseur du compte ;
 * - `equilibres` : `{generations, age_minimal, majorations}` — l'âge
 *   d'équilibre du diviseur de chaque génération, et l'âge cible de l'ETK,
 *   compté depuis `age_minimal`, sous la majoration du compte, ce dont le
 *   diviseur baisse quand l'âge monte, et sous `majorations` ;
 * - `ages_cibles` : `{cas: [{cle, coefficient, majorations, age_minimal}]}` —
 *   l'âge cible de l'ETK ;
 * - `ages_de_deces_cor` : `{generations}` — l'âge de décès des cas types du COR ;
 * - `parts_de_vie` : `{cas: [{cle, age, debut}], cor}` — la part de la vie
 *   passée en retraite.
 *
 * Une majoration y est donnée mois par mois de report, du premier : celle que
 * le Python définit. Il écrit, sous le nom de chaque lecture, ce qu'elle rend,
 * chaque cas sous sa clé, chaque génération sous son année. Aucune carrière ne
 * s'y écarte : celle que le portage refuse arrête le programme, et le test.
 */

import { readFileSync } from "node:fs";

import { PARAMETRES_DEFAUT } from "../../moteur/js/config.js";
import { Contexte } from "../../moteur/js/contexte.js";
import { contributionsDUneCarriere } from "../../moteur/js/contributions-equilibre.js";
import {
  ageCible, ageDeDecesCor, ageDEquilibre, Convention, conventionApresImpot, conventionCor,
  conventionNette, diviseurA, fluxDesSystemes, foyerDeLAnnee, indicateurs, partDeVie,
  partsImposablesParAnnee, remplacementApresImpot, remplacementNet, revenusNets,
} from "../../moteur/js/cycle-de-vie.js";
import {
  chargerBaremesImpotRevenu, croissanceMacro, impotDuFoyer,
} from "../../moteur/js/impot-revenu.js";
import { RevalorisationServie } from "../../moteur/js/revalorisation.js";
import { Saisie } from "../../moteur/js/saisie.js";

const { paquet, demande } = JSON.parse(readFileSync(0, "utf8"));
const contexte = new Contexte(paquet);

/** Ce que `calculer` rend de chaque cas, sous sa clé. */
function parCle(cas, calculer) {
  return Object.fromEntries(cas.map((un) => [un.cle, calculer(un)]));
}

/** La saisie d'une requête, simulée comme le site la simule. */
function simulerLaRequete(requete) {
  return contexte.simuler(Saisie.depuisRequete(requete, false, contexte.paquet.presomptions));
}

/** La carrière des options de `carriereSimple`, les interruptions en `Map` d'années. */
function carriereDesOptions(simulateur, options) {
  const interruptions = new Map(Object.entries(options.interruptions ?? {})
    .map(([annee, motif]) => [Number(annee), motif]));
  return simulateur.carriereSimple({ ...options, interruptions });
}

/** Une `Map` des années d'un objet JSON, dont les clés sont des chaînes. */
function parAnnee(objet) {
  return new Map(Object.entries(objet).map(([annee, valeur]) => [Number(annee), valeur]));
}

/** Ajoute `montant` à l'année `annee` de `sommes`. */
function ajouter(sommes, annee, montant) {
  sommes.set(annee, (sommes.get(annee) ?? 0.0) + montant);
}

/** Les conventions que les lectures nomment. */
const CONVENTIONS = {
  ocde: () => new Convention(),
  cor: (simulateur, comparaison) => conventionCor(simulateur, comparaison),
  // Celle du COR, sans les prélèvements : la pension brute.
  cor_brute: (simulateur, comparaison) => {
    const cor = conventionCor(simulateur, comparaison);
    return new Convention({
      age_deces: cor.age_deces, unisexe: cor.unisexe, taux_actualisation: cor.taux_actualisation,
    });
  },
};

function lireIndicateurs({ cas, conventions }) {
  const simulateur = contexte.simulateur();
  return parCle(cas, ({ requete }) => {
    const comparaison = simulerLaRequete(requete);
    const flux = fluxDesSystemes(simulateur, comparaison).actuel;
    return Object.fromEntries(conventions.map((nom) => [nom,
      indicateurs(flux, simulateur, CONVENTIONS[nom](simulateur, comparaison)).dictionnaire()]));
  });
}

/**
 * La carrière part après l'année courante : la pension de la Cnav suit les
 * prix, celle de l'Agirc-Arrco aussi, et sa valeur de service convenue, comme
 * `niveauxActuels` la fait jouer sur sa part (`coefficientPoints`).
 */
function lireRendementsParRegime({ cas, agirc_arrco: regimes }) {
  const simulateur = contexte.simulateur();
  const agircArrco = new Set(regimes);
  const famille = (regime) => (agircArrco.has(regime) ? "agirc_arrco" : "cnav");
  return parCle(cas, ({ cle, options }) => {
    const comparaison = simulateur.simuler(carriereDesOptions(simulateur, options));
    const flux = fluxDesSystemes(simulateur, comparaison).actuel;
    const { carriere } = comparaison;
    const liquidation = carriere.anneeLiquidation;
    if (liquidation <= simulateur.parametres.annee_courante) {
      throw new Error(`${cle} : parti en ${liquidation}, sa pension a vécu sous le droit`);
    }
    const compte = simulateur.constructeurEmployeur.construire(
      carriere, liquidation, carriere.premiereAnnee);
    const cotisations = { cnav: new Map(), agirc_arrco: new Map() };
    for (const ligne of compte.cotisations) {
      for (const [regime, montant] of ligne.par_regime) {
        ajouter(cotisations[famille(regime)], ligne.annee, montant);
      }
    }
    const avec = new Map(cotisations.agirc_arrco);
    for (const [annee, montant] of contributionsDUneCarriere(simulateur, carriere)) {
      ajouter(avec, annee, montant);
    }
    const pensions = { cnav: 0.0, agirc_arrco: 0.0 };
    for (const pension of comparaison.actuel.pensions_par_regime) {
      pensions[famille(pension.regime)] += pension.montant;
    }
    const annees = [...flux.niveaux.keys()];
    const revalorisation = new RevalorisationServie(
      simulateur, simulateur.parametres.annee_debut_repartition, Math.max(...annees));
    const prix = (annee) => simulateur.macro.coefficientPrix(liquidation, annee);
    const points = (annee) => revalorisation.coefficientPoints("agirc_arrco", liquidation, annee);
    const convention = conventionCor(simulateur, comparaison);
    const rendement = (versees, niveau) => indicateurs(flux.remplace({
      cotisations: versees, niveaux: new Map(annees.map((annee) => [annee, niveau(annee)])),
    }), simulateur, convention).rendement_smpt;
    const agircArrcoServie = (annee) => pensions.agirc_arrco * prix(annee) * points(annee);
    return {
      total: indicateurs(flux, simulateur, convention).rendement_smpt,
      cnav: rendement(cotisations.cnav, (annee) => pensions.cnav * prix(annee)),
      agirc_arrco: rendement(avec, agircArrcoServie),
      agirc_arrco_sans_contributions: rendement(cotisations.agirc_arrco, agircArrcoServie),
    };
  });
}

/**
 * Les cotisations du compte aux taux contractuels moyens de l'Arrco, que
 * TRAJECTOiRE prend : celles des régimes de `arrco`, multipliées par le
 * rapport du taux moyen au taux minimal de leur année (`moyens`), les autres
 * telles quelles, et les contributions d'équilibre.
 */
function auxTauxMoyens(simulateur, carriere, lignes, moyens, arrco) {
  const cotisations = new Map();
  for (const ligne of lignes) {
    for (const [regime, montant] of ligne.par_regime) {
      ajouter(cotisations, ligne.annee,
        arrco.has(regime) ? montant * (moyens.get(ligne.annee) ?? 1.0) : montant);
    }
  }
  for (const [annee, montant] of contributionsDUneCarriere(simulateur, carriere)) {
    ajouter(cotisations, annee, montant);
  }
  return cotisations;
}

/**
 * Les cotisations du compte (`entieres`), réduites à la seule retenue de
 * l'agent (`retenues`, le compte de la part salariale) les années où elles
 * vont à l'un des régimes de `etat`.
 */
function retenueDeLEtat(retenues, entieres, etat) {
  const cotisations = new Map();
  for (let rang = 0; rang < Math.min(retenues.length, entieres.length); rang += 1) {
    const [retenue, entiere] = [retenues[rang], entieres[rang]];
    if (retenue.annee !== entiere.annee) {
      throw new Error(`les deux comptes divergent : ${retenue.annee} et ${entiere.annee}`);
    }
    const aLEtat = entiere.regimes.some((regime) => etat.has(regime));
    ajouter(cotisations, entiere.annee, aLEtat ? retenue.cotisation : entiere.cotisation);
  }
  return cotisations;
}

function lireTrajectoire({ cas, taux_moyens_arrco: moyens, regimes_arrco: arrco,
  regimes_etat: etat }) {
  const simulateur = contexte.simulateur();
  const salariale = simulateur.constructeurDe(simulateur.calculs.notionnel_retroactif);
  const tauxMoyens = parAnnee(moyens);
  const [regimesArrco, regimesEtat] = [new Set(arrco), new Set(etat)];
  return parCle(cas, ({ requete, duree_relative: dureeRelative, pension,
    pension_nette: pensionNette }) => {
    const comparaison = simulerLaRequete(requete);
    const { carriere } = comparaison;
    const flux = fluxDesSystemes(simulateur, comparaison).actuel;
    const convention = new Convention({
      age_deces: flux.age + dureeRelative * flux.duree_carriere, unisexe: true,
    });
    const sous = (champs) => indicateurs(flux.remplace(champs), simulateur, convention)
      .dictionnaire();
    const rapport = pension / flux.niveaux.get(flux.annee_liquidation);
    const bornes = [carriere, carriere.anneeLiquidation, carriere.premiereAnnee];
    const entieres = simulateur.constructeurEmployeur.construire(...bornes).cotisations;
    const remplacement = remplacementNet(simulateur, carriere, revenusNets(simulateur, carriere),
      pensionNette);
    return {
      age: flux.age,
      duree_carriere: flux.duree_carriere,
      indicateurs: indicateurs(flux, simulateur, convention).dictionnaire(),
      recale: sous({ niveaux: new Map([...flux.niveaux]
        .map(([annee, niveau]) => [annee, niveau * rapport])) }),
      aux_taux_moyens: sous({
        cotisations: auxTauxMoyens(simulateur, carriere, entieres, tauxMoyens, regimesArrco),
      }),
      retenue_de_l_etat: sous({
        cotisations: retenueDeLEtat(salariale.construire(...bornes).cotisations, entieres,
          regimesEtat),
      }),
      remplacement_net: remplacement === null ? null
        : { constants: remplacement.constants, salaire_moyen: remplacement.salaire_moyen },
    };
  });
}

function lireOcde({ projection, indexation, cas }) {
  const simulateur = contexte.simulateur({ ...PARAMETRES_DEFAUT, scenario_projection: projection });
  const baremes = chargerBaremesImpotRevenu(contexte.paquet);
  const croissance = croissanceMacro(simulateur.macro, indexation);
  return parCle(cas, ({ options, taux_brut: tauxBrut }) => {
    const comparaison = simulateur.simuler(carriereDesOptions(simulateur, options));
    const systemes = fluxDesSystemes(simulateur, comparaison, { impot: indexation });
    const flux = systemes.actuel;
    const depart = flux.annee_liquidation;
    const imposable = tauxBrut * flux.dernier_revenu
      * partsImposablesParAnnee(simulateur, comparaison).get(depart);
    return {
      taux_remplacement_actuel: comparaison.tauxRemplacementActuel,
      patrimoine: indicateurs(fluxDesSystemes(simulateur, comparaison).actuel, simulateur)
        .patrimoine,
      dernier_revenu: flux.dernier_revenu,
      dernier_revenu_net: flux.dernier_revenu_net,
      dernier_revenu_apres_impot: flux.dernier_revenu_apres_impot,
      retenu: conventionNette(simulateur, comparaison).retenu(depart),
      impot_de_la_pension_brute: impotDuFoyer(
        foyerDeLAnnee(comparaison.carriere, depart, 0.0, imposable), depart, baremes,
        { indexation, croissance }).impot,
      patrimoine_apres_impot: indicateurs(flux, simulateur,
        conventionApresImpot(simulateur, comparaison, false, indexation)).patrimoine,
      remplacement_apres_impot: remplacementApresImpot(simulateur, comparaison, "actuel",
        indexation, systemes),
    };
  });
}

function lireDiviseurs({ cas }) {
  const simulateur = contexte.simulateur();
  return parCle(cas, ({ generation, age }) => diviseurA(simulateur, generation, age));
}

function lireEquilibres({ generations, age_minimal: ageMinimal, majorations }) {
  const simulateur = contexte.simulateur();
  return Object.fromEntries(generations.map((generation) => {
    const equilibre = ageDEquilibre(simulateur, generation);
    const aLAgeMinimal = equilibre.diviseur_a_l_age_de_reference;
    return [generation, {
      ...equilibre,
      age_cible_des_diviseurs: ageCible(equilibre.coefficient,
        (mois) => aLAgeMinimal / diviseurA(simulateur, generation, ageMinimal + mois / 12),
        ageMinimal),
      age_cible_des_majorations: ageCible(equilibre.coefficient, (mois) => majorations[mois],
        ageMinimal),
    }];
  }));
}

function lireAgesCibles({ cas }) {
  return parCle(cas, ({ coefficient, majorations, age_minimal: ageMinimal }) => ageCible(
    coefficient, (mois) => majorations[mois], ageMinimal));
}

function lireAgesDeDecesCor({ generations }) {
  const { mortalite } = contexte.simulateur();
  return Object.fromEntries(generations.map((generation) => [generation,
    ageDeDecesCor(mortalite, generation)]));
}

function lirePartsDeVie({ cas, cor }) {
  const simulateur = contexte.simulateur();
  return parCle(cas, ({ age, debut }) => partDeVie(simulateur, age, debut, null, cor));
}

const LECTURES = {
  indicateurs: lireIndicateurs,
  rendements_par_regime: lireRendementsParRegime,
  trajectoire: lireTrajectoire,
  ocde: lireOcde,
  diviseurs: lireDiviseurs,
  equilibres: lireEquilibres,
  ages_cibles: lireAgesCibles,
  ages_de_deces_cor: lireAgesDeDecesCor,
  parts_de_vie: lirePartsDeVie,
};
const inconnues = Object.keys(demande).filter((lecture) => !(lecture in LECTURES));
if (inconnues.length > 0 || Object.keys(demande).length === 0) {
  throw new Error(`lectures attendues, parmi ${Object.keys(LECTURES).join(", ")} : `
    + `${inconnues.join(", ") || "aucune"}`);
}
process.stdout.write(JSON.stringify(Object.fromEntries(Object.entries(demande)
  .map(([lecture, lue]) => [lecture, LECTURES[lecture](lue)]))));
