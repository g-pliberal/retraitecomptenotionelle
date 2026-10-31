/**
 * Ce que les trois pages qui agrègent lisent du modèle, fabriqué sous la
 * référence. Sans jumeau depuis l'action 161 (note de décision 0005) : les
 * écrivains de `src/retraite_notionnelle/donnees/agregats.py` fabriquent la
 * table, et ses accesseurs n'ont que cet exemplaire.
 *
 * POURQUOI CE FICHIER EXISTE. Coût, Carrières types et Droits non cotisés
 * croisent treize carrières types avec sept générations, et chiffrent ce que
 * chaque système coûterait jusqu'en 2070. Elles se calculaient ici, chez le
 * lecteur, par le portage JavaScript du coût et sous les réglages de
 * l'adresse : de trois à huit secondes à la première visite. Elles ne montrent
 * plus que la référence depuis le 11 octobre 2026 (action 150), et ce qu'elles
 * lisent d'une règle du modèle vient de cette table, que
 * `scripts/construire_donnees.py` calcule une fois et que le paquet embarque
 * (`agregats`). Ce qui n'est qu'une donnée lue — les comptes du COR, les
 * dépenses publiées — reste où elle était.
 *
 * Le lecteur ne calcule rien qu'une règle décide : il rend ce que la table
 * porte, et lève une erreur sur ce qu'elle ne porte pas — une page qui lirait
 * un zéro ou `undefined` à la place se tromperait sans bruit. Le seul zéro
 * qu'il rende sans le lire sur une ligne est le stock de la dette jusqu'à son
 * année de départ, que la table porte. Une année ou une génération se demande
 * en nombre, comme la table la porte (`tests/js/agregats.test.js`).
 */

/**
 * La clé sous laquelle la table porte la garantie vieillesse, que le passé et
 * l'avenir de chaque système comptent à part : celle que le Python lui donne
 * (`cout.COMPOSANTE_GARANTIE`), et qu'un test tient égale.
 */
export const COMPOSANTE_GARANTIE = "garantie_vieillesse_liberal";

/** `table[cle]`, ou une erreur qui dit ce que la table ne porte pas. */
function lire(table, cle, quoi) {
  if (!Object.prototype.hasOwnProperty.call(table, cle)) {
    throw new Error(`${quoi} absent de la table figée : ${cle}`);
  }
  return table[cle];
}

/**
 * `table[annee]`, sous la clé de texte où la table écrit une année ou une
 * génération. Elle se demande en nombre, comme la table la porte : une
 * chaîne, même « 1960 », trahirait une adresse lue sans être convertie.
 */
function lireAnnee(table, annee, quoi) {
  if (!Number.isInteger(annee)) {
    throw new Error(`${quoi} absent de la table figée : ${JSON.stringify(annee)}`);
  }
  return lire(table, String(annee), quoi);
}

/** La première (`rang` 0) ou la dernière (`rang` -1) année d'une partie de la table. */
function borne(annees, rang) {
  if (!annees.length) {
    throw new Error("année absent de la table figée : la partie est vide");
  }
  return annees.at(rang).annee;
}

/**
 * `repr(float(x))` du Python : la clé sous laquelle `figer_cout` écrit un
 * écart de taux. Les chiffres sont ceux de JavaScript, les plus courts qui
 * redonnent le nombre ; la forme est celle du Python, en notation
 * scientifique sous 10⁻⁴ et dès 10¹⁶, et un « .0 » à un nombre entier.
 */
function reprFlottant(x) {
  if (x === 0) return Object.is(x, -0) ? "-0.0" : "0.0";
  const [mantisse, puissance] = Math.abs(x).toExponential().split("e");
  const exposant = Number(puissance);
  const chiffres = mantisse.replace(".", "");
  const signe = x < 0 ? "-" : "";
  if (exposant < -4 || exposant >= 16) {
    const tete = chiffres.length > 1 ? `${chiffres[0]}.${chiffres.slice(1)}` : chiffres;
    const puissanceEcrite = String(Math.abs(exposant)).padStart(2, "0");
    return `${signe}${tete}e${exposant < 0 ? "-" : "+"}${puissanceEcrite}`;
  }
  if (exposant < 0) return `${signe}0.${"0".repeat(-exposant - 1)}${chiffres}`;
  const entiers = chiffres.slice(0, exposant + 1).padEnd(exposant + 1, "0");
  return `${signe}${entiers}.${chiffres.slice(exposant + 1) || "0"}`;
}

// -- les carrières types ------------------------------------------------------

/** D'une carrière simulée, ce que les pages en lisent : l'année du départ. */
class CarriereFigee {
  constructor(anneeLiquidation) {
    this.anneeLiquidation = anneeLiquidation;
  }
}

/** Une case de la grille : ce qu'en lisent les pages, sous les accesseurs de `Comparaison`. */
class ComparaisonFigee {
  constructor(brut) {
    this.carriere = new CarriereFigee(brut.annee_liquidation);
    this._carrieres = Object.fromEntries(Object.entries(brut.annees_liquidation)
      .map(([scenario, annee]) => [scenario, new CarriereFigee(annee)]));
    this._variations = brut.variations;
  }

  carriereDe(scenario) {
    return lire(this._carrieres, scenario, "carrière du scénario");
  }

  variationTotale(scenario) {
    return lire(this._variations, scenario, "écart du scénario");
  }
}

/**
 * Un cas type, tel que les pages le nomment, les caisses dont il porte les
 * retraités, et l'âge où chaque génération le fait partir.
 */
class CasFige {
  constructor(brut, generations) {
    this.code = brut.code;
    this.libelle = brut.libelle;
    this.commentaire = brut.commentaire;
    this.caisses = brut.caisses;
    this._ages = Object.fromEntries(
      generations.map((generation, rang) => [generation, brut.ages[rang]]));
  }

  ageLiquidation(generation) {
    return lireAnnee(this._ages, generation, "âge de départ de la génération");
  }
}

/**
 * La grille cas type × génération, sous les accesseurs du résultat de la
 * grille — `resultats` et `echecs`, par « code|génération » —, et les cas qui
 * la composent.
 */
export class CasTypesFiges {
  constructor(brut) {
    this.generations = brut.generations;
    this.cas = brut.cas.map((cas) => new CasFige(cas, brut.generations));
    this.resultats = new Map(Object.entries(brut.resultats)
      .map(([cle, valeur]) => [cle, new ComparaisonFigee(valeur)]));
    this.echecs = new Map(Object.entries(brut.echecs));
  }

  casType(code) {
    const cas = this.cas.find((candidat) => candidat.code === code);
    if (cas === undefined) {
      throw new Error(`cas type absent de la table figée : ${code}`);
    }
    return cas;
  }
}

// -- les avantages non contributifs -------------------------------------------

/**
 * Une année de la décomposition. Les lignes sont des objets que la page lit
 * par leur code, une ligne absente y valant `undefined` ; les trois sommes sont
 * celles du modèle, dans son ordre d'addition, que la table porte plutôt que de
 * les refaire.
 */
class AnneeAvantagesFigee {
  constructor(brut) {
    this.annee = brut.annee;
    this.observee = brut.observee;
    this.lignes = brut.lignes;
    this.modele = brut.modele;
    this.anticipees = brut.anticipees;
    this.gratuit = brut.gratuit;
    this.gratuitModele = brut.gratuit_modele;
    this.anticipee = brut.anticipee;
  }
}

/**
 * Ce que les avantages non contributifs coûtent, année par année ; et la
 * nomenclature sous laquelle la page les lit : les lignes que les comptes
 * publient (`lignesLues`), les avantages mesurés par retrait
 * (`neutralisations`), les motifs d'un départ anticipé et leur libellé.
 */
export class AvantagesFiges {
  constructor(brut) {
    this.annees = brut.annees.map((annee) => new AnneeAvantagesFigee(annee));
    this.lignes = brut.lignes;
    this.lignesModele = brut.lignes_modele;
    this.refus = brut.refus;
    this.ponderation = brut.ponderation;
    this.lignesLues = brut.lignes_lues;
    this.neutralisations = brut.neutralisations;
    this.motifs = brut.libelles_motifs.map(([motif]) => motif);
    this.libellesMotifs = Object.fromEntries(brut.libelles_motifs);
  }

  get derniere() {
    return this.annees.length > 0 ? this.annees[this.annees.length - 1] : null;
  }
}

// -- le classement de l'emploi ------------------------------------------------

/** D'une carrière simulée, ce que la page lit du système actuel. */
class DepartFige {
  constructor(brut) {
    this.pensionAnnuelle = brut.pension_annuelle;
    this.trimestresRequis = brut.trimestres_requis;
  }
}

/**
 * Le cas type `cas` parti à `age`, contre la même carrière sous
 * `declassement`, partie le même jour, pour chaque génération que la page
 * compare (`CLASSEMENT_COMPARE`, dans `pages.js`).
 */
export class ClassementFige {
  constructor(brut) {
    this.cas = brut.cas;
    this.age = brut.age;
    this.declassement = brut.declassement;
    this._departs = Object.fromEntries(Object.entries(brut.departs)
      .map(([generation, departs]) => [generation, departs.map((d) => new DepartFige(d))]));
  }

  get generations() {
    return Object.keys(this._departs).map(Number);
  }

  /** L'agent actif, puis l'agent déclassé. */
  departs(generation) {
    return lireAnnee(this._departs, generation, "départ de la génération");
  }
}

// -- le coût agrégé -----------------------------------------------------------
//
// La page Coût lit le coût entier : le passé de chaque système, son avenir, le
// bilan de chaque année et la dette qu'il accumule. Chaque ligne figée porte les
// champs de la ligne du modèle que la page lit, sous les noms que le portage
// leur donnait, et ce que ses accesseurs rendent pour les systèmes qu'elle leur
// demande — un autre lève une erreur. Un accesseur qui prend un nombre
// quelconque — le solde moyen d'une fenêtre, le pilier à un niveau de
// versements, le stock d'une année — se rend depuis ce que la ligne porte, par
// la même opération que le modèle.

/** `snake_case` -> `camelCase` : les noms que le portage donnait aux champs. */
function enCamel(nom) {
  return nom.replace(/_([a-z])/g, (_, lettre) => lettre.toUpperCase());
}

/** Les champs qu'une ligne de la table porte, sous leurs noms du portage. */
function champs(brut, cles) {
  const sortie = {};
  for (const cle of cles) {
    if (cle in brut) sortie[enCamel(cle)] = brut[cle];
  }
  return sortie;
}

const CHAMPS_SOLDE_ANNUEL = [
  "annee", "projete", "ressources", "depenses", "rapports", "pib", "retrait",
  "rapports_recettes", "part_contributive", "part_impots", "retrait_par_impot",
  "part_subventions", "taux_prelevement", "taux_liberal", "facteur_assiette",
  "annee_bascule", "convention_recette", "part_derives", "reversion_servie",
  "reforme_en_vigueur", "tva_liberal", "garantie_liberal", "majorations_stock",
  "taux_effectif", "annee_taux_effectif",
];
const CHAMPS_COUT_ANNUEL = [
  "annee", "observee", "coefficient_constants", "part_pib", "rapports", "pensionnes",
  "part_derives", "reversion_servie", "reforme_en_vigueur", "part_repartition",
];
const CHAMPS_AVENIR_ANNUEL = [
  "annee", "projete", "base", "coefficient_constants", "pib", "dependance",
  "facteur_assiette_liberal", "part_derives", "reversion_servie",
  "reforme_en_vigueur", "part_stock", "base_modele", "facteur_reversion", "tetes",
  "salaire_reel", "derive",
];

/** Une ligne figée : ses champs, et ce que ses accesseurs rendent par système. */
class LigneFigee {
  constructor(brut, cles) {
    Object.assign(this, champs(brut, cles));
    this._brut = brut;
  }

  _parSysteme(cle, scenario) {
    return lire(this._brut[cle], scenario, `${cle} du système`);
  }
}

/**
 * Une année du bilan, sous les accesseurs de `SoldeAnnuel`. Celle de la
 * variante dérivée ne porte que son coefficient et son solde.
 */
class SoldeAnnuelFige extends LigneFigee {
  constructor(brut) {
    super(brut, CHAMPS_SOLDE_ANNUEL);
    if ("recette_par_assiette" in brut) this.recetteParAssiette = brut.recette_par_assiette;
  }

  coefficient(scenario) { return this._parSysteme("coefficients", scenario); }

  depense(scenario) { return this._parSysteme("depenses_par_systeme", scenario); }

  depenseNette(scenario) { return this._parSysteme("depenses_nettes_par_systeme", scenario); }

  solde(scenario) { return this._parSysteme("soldes", scenario); }

  ressourcesDe(scenario) { return this._parSysteme("ressources_par_systeme", scenario); }

  soldeMeur(scenario) { return this._parSysteme("soldes_meur", scenario); }

  depenseMeur(scenario) { return this._parSysteme("depenses_meur", scenario); }

  ressourcesMeur() { return lire(this._brut, "ressources_meur", "champ de l'année"); }

  tvaDe(scenario) { return this._parSysteme("tva", scenario); }

  tvaGarantie(scenario) { return this._parSysteme("tva_garantie", scenario); }

  postesRessources(scenario) { return { ...this._parSysteme("postes_ressources", scenario) }; }

  postesDepenses(scenario) { return { ...this._parSysteme("postes_depenses", scenario) }; }
}

/** Le bilan de chaque année, sous les accesseurs de `Solde`. */
export class SoldeFige {
  constructor(brut) {
    this.annees = brut.annees.map((ligne) => new SoldeAnnuelFige(ligne));
    this.premiereAnneeProjetee = brut.premiere_annee_projetee;
    this._equilibrees = brut.premieres_annees_equilibrees;
    this.derniereAnneeObservee = this.premiereAnneeProjetee - 1;
  }

  get premiereAnnee() { return borne(this.annees, 0); }

  get derniereAnnee() { return borne(this.annees, -1); }

  observees() {
    return this.annees.filter((ligne) => !ligne.projete);
  }

  projetees() {
    return this.annees.filter((ligne) => ligne.projete);
  }

  annee(millesime) {
    return this.annees.find((ligne) => ligne.annee === millesime) ?? null;
  }

  /**
   * La moyenne des soldes de la fenêtre, additionnés de gauche à droite ; une
   * fenêtre où la table n'a aucune année n'a pas de moyenne.
   */
  soldeMoyen(scenario, debut, fin) {
    const lignes = this.annees.filter((l) => l.annee >= debut && l.annee <= fin);
    if (!lignes.length) {
      throw new Error(`solde moyen absent de la table figée : de ${debut} à ${fin}`);
    }
    let somme = 0;
    for (const ligne of lignes) somme += ligne.solde(scenario);
    return somme / lignes.length;
  }

  premiereAnneeEquilibree(scenario) {
    return lire(this._equilibrees, scenario, "première année équilibrée du système");
  }
}

/**
 * Le pilier d'une année, par euro versé, sous les accesseurs de `PilierAnnuel`
 * — dont les noms n'ont jamais quitté le `snake_case` du modèle.
 */
class PilierFige {
  constructor(brut) {
    Object.assign(this, brut);
  }

  /** Chaque grandeur au niveau des `versements` donnés, même unité. */
  niveaux(versements) {
    return {
      versements,
      frais_versement: this.frais_versement * versements,
      frais_gestion: this.frais_gestion * versements,
      frais_accumulation: this.frais_accumulation * versements,
      encours: this.encours * versements,
      rentes_brutes: this.rentes_brutes * versements,
      rentes: this.rentes * versements,
      frais_rentes: this.frais_rentes * versements,
      frais: this.frais * versements,
    };
  }
}

/** La garantie d'une année : un objet de données, sous les noms du portage. */
function garantie(brut) {
  if (brut === null) return null;
  return Object.fromEntries(Object.entries(brut).map(([cle, valeur]) => [enCamel(cle), valeur]));
}

/** Une année passée, sous les accesseurs de `CoutAnnuel`. */
class CoutAnnuelFige extends LigneFigee {
  constructor(brut) {
    super(brut, CHAMPS_COUT_ANNUEL);
    this.garantie = garantie(brut.garantie);
    this.pensions = brut.pensions;
    this.partPibPensions = brut.part_pib_pensions;
    this.observeeConstants = brut.observee_constants;
  }

  cout(scenario) { return this._parSysteme("couts", scenario); }

  coutConstants(scenario) { return this._parSysteme("couts_constants", scenario); }

  /**
   * La part de PIB du système cette année, règle de la réversion comprise :
   * ce que la page tirait de `masseDuScenario`, que le Python applique.
   */
  partPibDe(scenario) { return this._parSysteme("parts_pib", scenario); }
}

/** Une année projetée, sous les accesseurs de `AvenirAnnuel`. */
class AvenirAnnuelFige extends LigneFigee {
  constructor(brut) {
    super(brut, CHAMPS_AVENIR_ANNUEL);
    this.garantie = garantie(brut.garantie);
    this.pilier = brut.pilier === null ? null : new PilierFige(brut.pilier);
  }

  coutConstants(scenario) { return this._parSysteme("couts_constants", scenario); }

  partPibDerive(scenario) { return this._parSysteme("parts_pib_derive", scenario); }

  partPib(scenario) { return this._parSysteme("parts_pib", scenario); }

  reprisesConstants() { return lire(this._brut, "reprises_constants", "champ de l'année"); }

  reprises() { return lire(this._brut, "reprises", "champ de l'année"); }

  partPibReprises() { return lire(this._brut, "part_pib_reprises", "champ de l'année"); }

  garantieNetteConstants() {
    return lire(this._brut, "garantie_nette_constants", "champ de l'année");
  }
}

/** L'avenir de chaque système, sous les accesseurs de `Avenir`. */
class AvenirFige {
  constructor(brut) {
    this.annees = brut.annees.map((ligne) => new AvenirAnnuelFige(ligne));
    this.premiereAnneeProjetee = brut.premiere_annee_projetee;
    this.anneeBascule = brut.annee_bascule;
    this.anneeEuros = brut.annee_euros;
    this._brut = brut;
  }

  get premiereAnnee() { return borne(this.annees, 0); }

  get derniereAnnee() { return borne(this.annees, -1); }

  projetees() {
    return this.annees.filter((ligne) => ligne.projete);
  }

  annee(millesime) {
    return this.annees.find((ligne) => ligne.annee === millesime) ?? null;
  }

  cumul(scenario) { return lire(this._brut.cumuls, scenario, "cumul du système"); }

  ecartCumule(scenario) {
    return lire(this._brut.ecarts_cumules, scenario, "écart cumulé du système");
  }

  cumulReprises() { return lire(this._brut, "cumul_reprises", "champ de l'avenir"); }

  /** Par année, les têtes et la pension relatives à `depuis`, en `Map`. */
  decomposition(depuis) {
    const table = lireAnnee(this._brut.decompositions, depuis, "décomposition depuis");
    return new Map(Object.entries(table).map(([annee, valeurs]) => [Number(annee), valeurs]));
  }
}

/** Une année du stock, sous les accesseurs de `DetteAnnuelle`. */
class DetteAnnuelleFigee {
  constructor(brut) {
    this.annee = brut.annee;
    this.croissance = brut.croissance;
    this.taux = brut.taux;
    this.stocks = brut.stocks;
    this.interets = brut.interets;
    this.soldes = brut.soldes;
  }

  stock(scenario) { return lire(this.stocks, scenario, "stock du système"); }

  interet(scenario) { return lire(this.interets, scenario, "intérêt du système"); }

  solde(scenario) { return lire(this.soldes, scenario, "solde du système"); }
}

/** Le stock que les soldes accumulent, sous les accesseurs de `Dette`. */
class DetteFigee {
  constructor(brut) {
    this.annees = brut.annees.map((ligne) => new DetteAnnuelleFigee(ligne));
    this.anneeDepart = brut.annee_depart;
    this.ecartTaux = brut.ecart_taux;
    this.dateCourbe = brut.date_courbe;
    this.derniereAnneeCotee = brut.derniere_annee_cotee;
    this.dettePubliqueObservee = brut.dette_publique_observee;
    this.anneeDettePublique = brut.annee_dette_publique;
    this._brut = brut;
  }

  get premiereAnnee() { return borne(this.annees, 0); }

  get derniereAnnee() { return borne(this.annees, -1); }

  /**
   * Ce que le pays doit au départ, en part de PIB, que la série publiée porte
   * pour l'année de départ : sans elle, la dette publique ne serait que le
   * stock du système, et la page le dirait sans bruit.
   */
  get dettePubliqueDepart() {
    return lireAnnee(this.dettePubliqueObservee, this.anneeDettePublique,
      "dette publique de l'année");
  }

  dettePublique(scenario, millesime) {
    return this.dettePubliqueDepart + this.stock(scenario, millesime);
  }

  annee(millesime) {
    return this.annees.find((ligne) => ligne.annee === millesime) ?? null;
  }

  /**
   * Le stock en fin d'année. Il est nul jusqu'à l'année de départ, que la
   * table porte : le seul zéro qu'elle rende sans le lire sur une ligne.
   */
  stock(scenario, millesime) {
    if (millesime <= this.anneeDepart) return 0.0;
    const ligne = this.annee(millesime);
    if (ligne === null) {
      throw new Error(`stock de l'année absent de la table figée : ${millesime}`);
    }
    return ligne.stock(scenario);
  }

  horizon(scenario) { return lire(this._brut.horizons, scenario, "horizon du système"); }

  cumulSoldes(scenario) {
    return lire(this._brut.cumuls_soldes, scenario, "cumul des soldes du système");
  }

  cumulInterets(scenario) {
    return lire(this._brut.cumuls_interets, scenario, "cumul des intérêts du système");
  }
}

/** Une dette réduite à ce que la page en cite : son stock à l'horizon. */
class HorizonsFiges {
  constructor(horizons) {
    this._horizons = horizons;
  }

  horizon(scenario) { return lire(this._horizons, scenario, "horizon du système"); }
}

/**
 * Le coût agrégé de tous les systèmes, sous les accesseurs de `Cout`, et la
 * dette sous un taux décalé (`detteDecalee`), que la page tirait de
 * `calculerDette`.
 */
export class CoutFige {
  constructor(brut) {
    this.annees = brut.annees.map((ligne) => new CoutAnnuelFige(ligne));
    this.avenir = new AvenirFige(brut.avenir);
    this.solde = new SoldeFige(brut.solde);
    this.soldeDerive = new SoldeFige(brut.solde_derive);
    this.dette = new DetteFigee(brut.dette);
    this.detteDerive = new HorizonsFiges(brut.dette_derive);
    this.anneeEuros = brut.annee_euros;
    this.generations = brut.generations;
    this.poids = brut.poids;
    this.poidsCotisants = brut.poids_cotisants;
    this._brut = brut;
  }

  get premiereAnnee() { return borne(this.annees, 0); }

  get derniereAnnee() { return borne(this.annees, -1); }

  cumul(scenario) { return lire(this._brut.cumuls, scenario, "cumul du système"); }

  cumulObserve() { return lire(this._brut, "cumul_observe", "champ du coût"); }

  confondusAvecActuel() { return [...this._brut.confondus_avec_actuel]; }

  annee(millesime) {
    return this.annees.find((ligne) => ligne.annee === millesime) ?? null;
  }

  /**
   * Le taux de TVA unique qui couvrirait juste chaque année, garantie comprise,
   * et l'année qui le fixe : ce que la page tirait de `tauxTvaRequis`.
   */
  tauxTvaRequis() { return [...this._brut.taux_tva_requis]; }

  /** La dette au taux de la courbe décalé de `ecart`, citée à l'horizon. */
  detteDecalee(ecart) {
    return new HorizonsFiges(lire(this._brut.dettes_decalees, reprFlottant(ecart),
      "dette au taux décalé de"));
  }
}

// -- le coût sous les variantes de population de l'INSEE ---------------------

/**
 * Le coût sous les trois hypothèses d'une composante de la population de
 * l'INSEE (espérance de vie, fécondité, migrations), que la page Coût met
 * côte à côte (action 138, étape 7) : la dépense de chaque système à
 * quelques années, son solde à l'horizon, son solde moyen sur les années
 * projetées. `figer_variantes` (`donnees/agregats.py`) l'écrit.
 */
export class VariantesFigees {
  constructor(brut) {
    this._brut = brut;
    this.hypotheses = [...brut.hypotheses];
    this.annees = brut.annees.map(Number);
    [this.premiereAnnee, this.derniereAnnee] = brut.fenetre.map(Number);
  }

  /** La dépense d'un système une année, en part de PIB. */
  partPib(hypothese, scenario, annee) {
    const parts = lire(lire(this._brut.parts_pib, hypothese, "hypothèse"),
      scenario, "système");
    return Number(lireAnnee(parts, annee, "année"));
  }

  /** Le solde d'un système à l'horizon, en part de PIB. */
  solde(hypothese, scenario) {
    return Number(lire(lire(this._brut.soldes, hypothese, "hypothèse"),
      scenario, "système"));
  }

  /** Le solde moyen d'un système sur les années projetées, en part de PIB. */
  soldeMoyen(hypothese, scenario) {
    return Number(lire(lire(this._brut.soldes_moyens, hypothese, "hypothèse"),
      scenario, "système"));
  }
}

// -- le bilan du compte -------------------------------------------------------

/**
 * Ce que la table porte du bilan d'un système (`bilan_compte.BilanCompte`) :
 * ses champs, puis les indicateurs qu'il en tire, que le lecteur rend sans en
 * refaire aucune opération.
 */
const CHAMPS_BILAN_COMPTE = [
  "cotisations", "age_cotisations", "age_pensions", "reserves", "dette", "depense",
  "ressources", "assiette", "duree_rotation", "actif_cotisation", "actif",
  "ratio_equilibre", "taux_equilibre", "taux_cotisation", "taux_cotisation_equilibre",
];

/**
 * Le bilan du compte notionnel de chaque système, à la manière suédoise
 * (action 138, étape 19), une année : ce qu'il doit au titre des droits
 * acquis, et ce que ses cotisations et ses réserves peuvent porter.
 * `figer_bilan_compte` (`donnees/agregats.py`) l'écrit.
 */
export class BilanCompteFige {
  constructor(brut) {
    this._systemes = brut.systemes;
    this.annee = Number(brut.annee);
    this.rendement = brut.rendement;
  }

  /** Le bilan d'un système, sous les noms du portage : `dureeRotation`… */
  systeme(scenario) {
    return champs(lire(this._systemes, scenario, "système"), CHAMPS_BILAN_COMPTE);
  }
}

// -- les leviers de l'équilibre ------------------------------------------------

/**
 * Ce que la table porte des leviers d'une année (`leviers.Leviers`) et des
 * écarts d'un horizon (`leviers.EcartsSurHorizon`).
 */
const CHAMPS_LEVIERS = ["pension", "prelevement", "age"];
const CHAMPS_ECARTS_HORIZON = ["pension_gap", "tax_gap"];

/**
 * Ce que chaque levier, seul, devrait faire pour équilibrer chaque système
 * chaque année — rogner la pension, relever le taux de prélèvement, reculer
 * l'âge —, et l'ajustement immédiat qui l'équilibrerait en moyenne depuis
 * `debut` jusqu'à chaque horizon du COR (action 138, étape 3). L'âge d'une
 * année que nul recul de `recul` n'équilibre vaut `null`. Puis ceux qui
 * porteraient chaque système à un autre solde, chacun de `soldesVises` aux
 * années `anneesVisees` (action 138, étape 10). `figer_leviers`
 * (`donnees/agregats.py`) l'écrit.
 */
export class LeviersFiges {
  constructor(brut) {
    this._systemes = brut.systemes;
    this.debut = Number(brut.debut);
    this.annees = brut.annees.map(Number);
    this.horizons = brut.horizons.map(Number);
    /** Les bornes du recul cherché, en années, hors desquelles l'âge vaut `null`. */
    this.recul = brut.recul.map(Number);
    /**
     * Les soldes que la page propose de viser, en part de PIB, et les années
     * où elle montre les leviers qui y portent.
     */
    this.soldesVises = brut.soldes_vises.map(Number);
    this.anneesVisees = brut.annees_visees.map(Number);
  }

  /** Les leviers d'un système une année : `pension`, `prelevement`, `age`. */
  annee(scenario, annee) {
    const annuels = lire(this._systemes, scenario, "système").annuels;
    return champs(lireAnnee(annuels, annee, "année"), CHAMPS_LEVIERS);
  }

  /** Les leviers qui portent un système au solde visé `solde` une année. */
  vise(scenario, solde, annee) {
    const rang = this.soldesVises.indexOf(solde);
    if (rang < 0) { throw new Error(`solde visé absent de la table figée : ${solde}`); }
    const vises = lire(this._systemes, scenario, "système").vises;
    return champs(lireAnnee(vises[rang], annee, "année"), CHAMPS_LEVIERS);
  }

  /** Les écarts d'un système sur un horizon : `pensionGap`, `taxGap`. */
  horizon(scenario, fin) {
    const horizons = lire(this._systemes, scenario, "système").horizons;
    return champs(lireAnnee(horizons, fin, "horizon"), CHAMPS_ECARTS_HORIZON);
  }
}

// -- la table -----------------------------------------------------------------

/** Ce que les trois pages qui agrègent lisent, tel que la table le porte. */
export class AgregatsFiges {
  constructor(casTypes, avantages, classement, cout, esperanceVie, fecondite, migrations,
    bilanCompte, leviers) {
    this.casTypes = casTypes;
    this.avantages = avantages;
    this.classement = classement;
    this.cout = cout;
    this.esperanceVie = esperanceVie;
    this.fecondite = fecondite;
    this.migrations = migrations;
    this.bilanCompte = bilanCompte;
    this.leviers = leviers;
  }
}

/** Reconstruit la table depuis la clé `agregats` du paquet. */
export function chargerAgregats(donnees) {
  return new AgregatsFiges(
    new CasTypesFiges(donnees.cas_types),
    new AvantagesFiges(donnees.avantages),
    new ClassementFige(donnees.classement),
    new CoutFige(donnees.cout),
    new VariantesFigees(donnees.esperance_vie),
    new VariantesFigees(donnees.fecondite),
    new VariantesFigees(donnees.migrations),
    new BilanCompteFige(donnees.bilan_compte),
    new LeviersFiges(donnees.leviers),
  );
}
