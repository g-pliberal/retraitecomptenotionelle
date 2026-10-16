/**
 * L'impôt sur le revenu d'un foyer, de son barème à son montant, chaque
 * année — portage de `impot_revenu.py` et de `donnees/impot_revenu.py`, qui
 * font foi et disent le détail (action 138, étapes 5 et 9).
 *
 * Les barèmes de 1960 à la dernière loi de finances lue, marche par marche,
 * projetés au-delà sur les prix ou sur le salaire moyen ; l'impôt d'un foyer
 * — une personne seule ou un couple, des enfants à charge ou non, des
 * salaires, des bénéfices d'indépendant et des pensions imposables — étape par étape, dans l'ordre de
 * l'article 193 du code général des impôts, avec les arrondis du code et le
 * calcul en francs des années en francs. Les indicateurs de cycle de vie
 * (`cycle-de-vie.js`) en tirent leur convention après impôt. Le paquet porte
 * les marches telles que le Python les lit (`impot_revenu`,
 * `scripts/construire_donnees.py`), sans leurs clés de source.
 *
 * Ce que le module ne calcule pas : `HORS_CHAMP`, comme le Python. Le
 * `round(x, 6)` du Python, qui absorbe le bruit des flottants avant un
 * arrondi, s'écrit ici `toFixed(6)` : les deux ne diffèrent qu'à une moitié
 * exacte du septième chiffre, qu'aucun arrondi à l'unité ne voit.
 */

/** Un franc vaut 1/6,55957 euro (règlement (CE) n° 2866/98 du Conseil). */
export const FRANC = 6.55957;

/** Les revenus de 2000 sont les derniers imposés en francs. */
export const DERNIERE_ANNEE_EN_FRANCS = 2000;

/** Les deux façons de projeter le barème au-delà de la dernière loi de finances. */
export const INDEXATIONS = Object.freeze(["prix", "salaire_moyen"]);

/** Les clés des séries qui sont des montants, que la projection relève. */
export const MONTANTS = Object.freeze({
  plafonds_quotient_familial: ["general", "parent_isole_premier_enfant",
    "vivant_seul_ayant_eu_un_enfant", "reduction_complementaire_invalide",
    "reduction_complementaire_veuf"],
  decote: ["seuil_celibataire", "seuil_couple"],
  deductions: ["frais_professionnels_minimum", "frais_professionnels_maximum",
    "pensions_minimum", "pensions_maximum"],
  abattement_age_invalidite: ["abattement_plein", "seuil_plein", "abattement_reduit",
    "seuil_reduit"],
});

/** Les séries qu'une année porte, dans l'ordre du fichier. */
export const SERIES = Object.freeze([
  "bareme", "quotient_familial", "parts_par_rang_d_enfant",
  "plafonds_quotient_familial", "decote", "reduction_sous_condition_de_revenus",
  "recouvrement", "deductions", "abattement_age_invalidite",
  "abattement_exceptionnel_ages_invalides", "abattement_exceptionnel_personnes_seules",
  "majorations_exceptionnelles", "minorations_exceptionnelles",
  "reduction_exceptionnelle", "reduction_proportionnelle", "prime_pour_l_emploi",
  "credit_exceptionnel",
]);

/** Les clés qui ne sont pas des valeurs : elles disent d'où vient la marche. */
export const CLES_DE_SOURCE = Object.freeze(["annee", "texte", "note", "origine"]);

/** Ce que le module ne calcule pas : voir l'en-tête de `impot_revenu.py`. */
export const HORS_CHAMP = Object.freeze([
  "revenus autres que les salaires, les bénéfices et les pensions",
  "abattement forfaitaire des régimes micro : le bénéfice s'entend après lui",
  "revenus d'activité non salariée de la prime pour l'emploi",
  "limites de chiffre d'affaires de l'abattement des adhérents, de 1978 à 1982",
  "charges déductibles et pensions alimentaires",
  "réductions et crédits d'impôt autres que la prime pour l'emploi, les réductions de 2001 "
    + "et de 2013 et le crédit de 2008",
  "demi-parts des anciens combattants et de qui vit seul après avoir élevé un enfant (case L)",
  "enfants en résidence alternée ou majeurs rattachés",
  "abattement des départements d'outre-mer",
  "contribution exceptionnelle sur les hauts revenus",
  "temps partiel et activité sur une partie de l'année, pour la prime pour l'emploi",
  "seuil de restitution de l'article 1965 L (50 F, puis 8 €)",
]);

/** L'âge, au 31 décembre de l'année des revenus, qui ouvre l'abattement des personnes âgées. */
export const AGE_ABATTEMENT = 65;

/** Le mineur invalide a sa demi-part depuis les revenus de 1979. */
export const PREMIERE_ANNEE_ENFANT_INVALIDE = 1979;

/** La première année de revenus dont le barème plafonne l'avantage du quotient familial. */
export const PREMIERE_ANNEE_PLAFONNEMENT = 1981;

/** Depuis les revenus de 2005, le montant minimal de la prime pour l'emploi est un seuil. */
export const PREMIERE_ANNEE_SEUIL_DE_LA_PPE = 2005;

/** Le bénéfice d'un indépendant (art. 158, 4 bis et 7) : voir `impot_revenu.py`. */
export const REGIMES_DU_BENEFICE = Object.freeze(["reel_adherent", "reel_non_adherent", "micro"]);
export const CATEGORIES_DU_BENEFICE = Object.freeze(["bic", "bnc", "ba"]);
export const PREMIERE_ANNEE_ABATTEMENT_ADHERENTS = 1978;
export const PREMIERE_ANNEE_ABATTEMENT_BNC = 1984;
export const DERNIERE_ANNEE_ABATTEMENT_ADHERENTS = 2005;
/** Le seuil, en francs, au-delà duquel l'abattement des adhérents tombe à 10 %, jusqu'en 1995. */
export const SEUILS_ABATTEMENT_REDUIT = Object.freeze({
  1978: 150000, 1979: 150000, 1980: 150000, 1981: 150000,
  1982: 165000, 1983: 165000, 1984: 182000, 1985: 192200, 1986: 250000,
  1987: 320000, 1988: 320000, 1989: 413200, 1990: 426400, 1991: 440000,
  1992: 440000, 1993: 440000, 1994: 469000, 1995: 469000,
});
/** La majoration du bénéfice au réel de qui n'adhère pas, de 2006 à 2022. */
export const PREMIERE_ANNEE_MAJORATION = 2006;
export const COEFFICIENT_MAJORATION = 1.25;
export const COEFFICIENTS_MAJORATION_DEGRESSIFS = Object.freeze({ 2020: 1.20, 2021: 1.15, 2022: 1.10 });
export const DERNIERE_ANNEE_MAJORATION = 2022;

/** Python `round(x, 6)`. */
function arrondi6(valeur) {
  return Number(valeur.toFixed(6));
}

/** `d.get(cle, defaut)` du Python : le défaut pour une clé absente seulement. */
function obtenir(serie, cle, defaut) {
  return cle in serie ? serie[cle] : defaut;
}

function vide(serie) {
  return Object.keys(serie).length === 0;
}

function somme(termes) {
  let total = 0;
  for (const terme of termes) total += terme;
  return total;
}

/** L'euro le plus proche, la moitié comptée pour un, comme le code arrondit. */
export function arrondiALEuro(valeur) {
  return Math.floor(arrondi6(valeur) + 0.5);
}

/** La monnaie dans laquelle les revenus d'`annee` sont imposés. */
export function monnaieDe(annee) {
  return annee <= DERNIERE_ANNEE_EN_FRANCS ? "FRF" : "EUR";
}

/** Les paramètres en vigueur pour les revenus d'une année, dans sa monnaie. */
export class ParametresImpot {
  constructor({
    annee, monnaie, seuils, taux, series, derniere_annee_lue, indexation = null,
    fiabilite = "haute",
  }) {
    Object.assign(this, {
      annee, monnaie, seuils, taux, series, derniere_annee_lue, indexation, fiabilite,
    });
    Object.freeze(this);
  }

  get projete() {
    return this.annee > this.derniere_annee_lue;
  }

  serie(nom) {
    return this.series[nom];
  }

  /** La part du `rang`-ième enfant à charge (le premier a le rang 1). */
  partsDEnfant(rang) {
    const parts = this.series.parts_par_rang_d_enfant.parts;
    return Number(parts[Math.min(rang, parts.length) - 1]);
  }
}

function marcheDe(marches, annee) {
  let retenue = {};
  for (const marche of marches) {
    if (marche.annee > annee) break;
    retenue = marche;
  }
  return retenue;
}

function valeursDe(marche) {
  if (marche.supprimee) return {};
  return Object.fromEntries(Object.entries(marche)
    .filter(([cle]) => !CLES_DE_SOURCE.includes(cle)));
}

function verifierLaProjection(annee, indexation, croissance) {
  if (!INDEXATIONS.includes(indexation)) {
    throw new Error(`indexation inconnue : '${indexation}' (${INDEXATIONS.join(", ")})`);
  }
  if (croissance === null || croissance === undefined) {
    throw new Error(`les revenus de ${annee} se projettent : il faut la croissance `
      + `des ${indexation === "prix" ? "prix" : "salaires"}`);
  }
}

/** L'année `annee` à partir de la précédente : chaque montant relevé de `facteur`. */
function projeter(precedents, annee, indexation, facteur) {
  const relever = (valeur) => arrondiALEuro(valeur * facteur);
  const series = Object.fromEntries(Object.entries(precedents.series)
    .map(([nom, valeurs]) => [nom, { ...valeurs }]));
  for (const [nom, cles] of Object.entries(MONTANTS)) {
    for (const cle of cles) {
      if (cle in series[nom]) series[nom][cle] = relever(series[nom][cle]);
    }
  }
  return new ParametresImpot({
    annee, monnaie: "EUR", seuils: precedents.seuils.map(relever), taux: precedents.taux,
    series, derniere_annee_lue: precedents.derniere_annee_lue, indexation,
    fiabilite: "estimee",
  });
}

/** Toutes les marches de l'impôt sur le revenu, de 1960 à la dernière loi de finances lue. */
export class BaremesImpotRevenu {
  constructor({ series, lu_le = "", premiere_annee }) {
    this.series = series;
    this.lu_le = lu_le;
    this.premiere_annee = premiere_annee;
    let derniere = -Infinity;
    for (const marche of series.bareme) derniere = Math.max(derniere, marche.annee);
    this.derniere_annee = derniere;
  }

  /** Les paramètres d'une année lue. */
  lus(annee) {
    if (!(this.premiere_annee <= annee && annee <= this.derniere_annee)) {
      throw new Error(`aucun barème lu pour les revenus de ${annee} `
        + `(${this.premiere_annee}–${this.derniere_annee})`);
    }
    const series = {};
    for (const nom of SERIES) series[nom] = valeursDe(marcheDe(this.series[nom], annee));
    const bareme = series.bareme;
    delete series.bareme;
    const monnaie = monnaieDe(annee);
    for (const [nom, valeurs] of Object.entries(series)) {
      if (obtenir(valeurs, "monnaie", monnaie) !== monnaie) {
        throw new Error(`${nom} des revenus de ${annee} en ${valeurs.monnaie}, `
          + `quand l'année est en ${monnaie}`);
      }
    }
    if (bareme.monnaie !== monnaie) {
      throw new Error(`le barème des revenus de ${annee} n'est pas en ${monnaie}`);
    }
    return new ParametresImpot({
      annee, monnaie, seuils: bareme.seuils.map(Number), taux: bareme.taux.map(Number),
      series, derniere_annee_lue: this.derniere_annee,
    });
  }

  /**
   * Les paramètres des revenus d'`annee`, lus ou projetés : au-delà de la
   * dernière année lue, `croissance(t)` donne la croissance de l'année `t`.
   */
  parametres(annee, indexation = "prix", croissance = null) {
    if (annee <= this.derniere_annee) return this.lus(annee);
    verifierLaProjection(annee, indexation, croissance);
    let parametres = this.lus(this.derniere_annee);
    for (let suivante = this.derniere_annee + 1; suivante <= annee; suivante += 1) {
      parametres = projeter(parametres, suivante, indexation, 1.0 + Number(croissance(suivante)));
    }
    return parametres;
  }

  /**
   * Les paramètres de chaque année de revenus, de la première lue à
   * `derniere`, en une passe : une `Map` de l'année à ses paramètres.
   */
  chronique(derniere, indexation = "prix", croissance = null) {
    const annees = new Map();
    for (let annee = this.premiere_annee; annee <= Math.min(derniere, this.derniere_annee);
      annee += 1) {
      annees.set(annee, this.lus(annee));
    }
    if (derniere > this.derniere_annee) {
      verifierLaProjection(derniere, indexation, croissance);
      let parametres = annees.get(this.derniere_annee);
      for (let suivante = this.derniere_annee + 1; suivante <= derniere; suivante += 1) {
        parametres = projeter(parametres, suivante, indexation,
          1.0 + Number(croissance(suivante)));
        annees.set(suivante, parametres);
      }
    }
    return annees;
  }
}

/** La croissance qui projette le barème : l'inflation du scénario, ou son salaire moyen nominal. */
export function croissanceMacro(macro, indexation = "prix") {
  if (indexation === "prix") return (annee) => macro.inflation.valeur(annee);
  if (indexation === "salaire_moyen") return (annee) => macro.salaire_moyen.valeur(annee);
  throw new Error(`indexation inconnue : '${indexation}' (${INDEXATIONS.join(", ")})`);
}

const lus = new WeakMap();

/** Les barèmes que porte le paquet ; `null` s'il ne les porte pas. */
export function chargerBaremesImpotRevenu(paquet) {
  if (lus.has(paquet)) return lus.get(paquet);
  const brut = paquet.impot_revenu ?? null;
  const baremes = brut === null ? null : new BaremesImpotRevenu({
    series: Object.fromEntries(SERIES.map((nom) => [nom,
      [...brut.series[nom]].sort((a, b) => a.annee - b.annee)])),
    lu_le: brut.lu_le ?? "",
    premiere_annee: Number(brut.premiere_annee),
  });
  lus.set(paquet, baremes);
  return baremes;
}

// -- le foyer ----------------------------------------------------------------

/** Un déclarant du foyer, ses revenus imposables de l'année et sa situation. */
export class Declarant {
  constructor({
    salaires = 0.0, pensions = 0.0, age = null, invalide = false, benefices = 0.0,
    regime = "reel_adherent", categorie = "bic",
  } = {}) {
    if (!REGIMES_DU_BENEFICE.includes(regime)) {
      throw new Error(`régime du bénéfice inconnu : '${regime}'`);
    }
    if (!CATEGORIES_DU_BENEFICE.includes(categorie)) {
      throw new Error(`catégorie du bénéfice inconnue : '${categorie}'`);
    }
    Object.assign(this, { salaires, pensions, age, invalide, benefices, regime, categorie });
    Object.freeze(this);
  }
}

/** Un foyer fiscal : un déclarant, ou deux imposés en commun. */
export class Foyer {
  constructor({
    declarants, enfants = 0, enfants_invalides = 0, veuf = false, vit_seul = true,
  }) {
    if (declarants.length !== 1 && declarants.length !== 2) {
      throw new Error("un foyer a un déclarant, ou deux s'il est un couple");
    }
    if (veuf && declarants.length === 2) throw new Error("un couple n'est pas veuf");
    if (enfants < 0 || !(enfants_invalides >= 0 && enfants_invalides <= enfants)) {
      throw new Error("un nombre d'enfants négatif, ou plus d'enfants invalides que d'enfants");
    }
    Object.assign(this, { declarants, enfants, enfants_invalides, veuf, vit_seul });
    Object.freeze(this);
  }

  get couple() {
    return this.declarants.length === 2;
  }

  /** Les parts que le plafonnement ne touche pas : une, deux pour un couple. */
  get parts_de_base() {
    return this.couple ? 2.0 : 1.0;
  }
}

// -- les arrondis ------------------------------------------------------------

/** L'arrondi du code : la fraction égale à la moitié comptée pour un. */
function auPlusProche(valeur, pas = 1.0) {
  return Math.floor(arrondi6(valeur / pas) + 0.5) * pas;
}

/** Un abattement ou un revenu net : au plus proche depuis 1998, au centime inférieur avant. */
function arrondirElement(annee, valeur) {
  if (annee >= 1998) return auPlusProche(valeur);
  return Math.floor(arrondi6(valeur * 100)) / 100;
}

/** Le revenu imposable : à la dizaine de francs inférieure jusqu'en 1997, au plus proche ensuite. */
function arrondirRevenuImposable(annee, valeur) {
  if (annee >= 1998) return auPlusProche(valeur);
  return Math.floor(arrondi6(valeur / 10)) * 10.0;
}

/** Une cotisation, une décote, une réduction : à l'unité depuis 1979, au dixième avant. */
function arrondirImpot(annee, valeur) {
  if (annee >= 1979) return auPlusProche(valeur);
  return auPlusProche(valeur, 0.1);
}

// -- les étapes --------------------------------------------------------------

/** L'impôt du barème : celui d'une part, multiplié par les parts, arrondi. */
export function impotDuBareme(parametres, revenu, parts) {
  const quotient = revenu / parts;
  let impotParPart = 0.0;
  const { seuils, taux } = parametres;
  for (const [rang, seuil] of seuils.entries()) {
    const haut = rang + 1 < seuils.length ? seuils[rang + 1] : Infinity;
    if (quotient > seuil) impotParPart += (Math.min(quotient, haut) - seuil) * taux[rang];
  }
  return arrondirImpot(parametres.annee, impotParPart * parts);
}

function parentIsole(foyer) {
  return !foyer.couple && !foyer.veuf && foyer.enfants > 0 && foyer.vit_seul;
}

function invalidites(foyer, annee) {
  const enfants = annee >= PREMIERE_ANNEE_ENFANT_INVALIDE ? foyer.enfants_invalides : 0;
  return foyer.declarants.filter((d) => d.invalide).length + enfants;
}

/** Le quotient familial du foyer (art. 194 et 195). */
export function nombreDeParts(foyer, parametres) {
  const qf = parametres.serie("quotient_familial");
  let parts = foyer.parts_de_base;
  if (foyer.veuf && foyer.enfants) parts += obtenir(qf, "veuf_avec_enfant", 0.0);
  let enfants = 0;
  for (let rang = 1; rang <= foyer.enfants; rang += 1) enfants += parametres.partsDEnfant(rang);
  parts += enfants;
  if (parentIsole(foyer)) parts += obtenir(qf, "parent_isole", 0.0);
  parts += obtenir(qf, "invalide", 0.0) * invalidites(foyer, parametres.annee);
  return parts;
}

/** Les revenus nets de chaque déclarant après leurs abattements, et l'abattement de 20 %. */
function revenusNetsDuFoyer(foyer, parametres, salaires, pensions) {
  const annee = parametres.annee;
  const d = parametres.serie("deductions");
  const salairesNets = salaires.map((salaire) => {
    let deduction = obtenir(d, "frais_professionnels_taux", 0.0) * salaire;
    if ("frais_professionnels_minimum" in d) {
      deduction = Math.max(deduction, d.frais_professionnels_minimum);
    }
    if ("frais_professionnels_maximum" in d) {
      deduction = Math.min(deduction, d.frais_professionnels_maximum);
    }
    deduction = arrondirElement(annee, Math.min(deduction, salaire));
    return salaire - deduction;
  });
  let abattements = pensions.map((pension) => {
    let abattement = obtenir(d, "pensions_taux", 0.0) * pension;
    if ("pensions_minimum" in d) abattement = Math.max(abattement, d.pensions_minimum);
    return Math.min(abattement, pension);
  });
  const total = somme(abattements);
  if ("pensions_maximum" in d && total > d.pensions_maximum) {
    abattements = abattements.map((a) => a * d.pensions_maximum / total);
  }
  abattements = abattements.map((a) => arrondirElement(annee, a));
  const pensionsNettes = pensions.map((p, rang) => p - abattements[rang]);
  let vingt = 0.0;
  if (obtenir(d, "vingt_pour_cent_taux", 0)) {
    const n = Math.min(salairesNets.length, pensionsNettes.length);
    for (let rang = 0; rang < n; rang += 1) {
      const base = salairesNets[rang] + pensionsNettes[rang];
      const limite = obtenir(d, "vingt_pour_cent_plafond", null);
      const assiette = limite === null ? base : Math.min(base, limite);
      let abattement = d.vingt_pour_cent_taux * assiette;
      if (limite !== null && (annee === 1973 || annee === 1974)) {
        abattement += 0.10 * Math.max(base - limite, 0.0);
      }
      vingt += arrondirElement(annee, abattement);
    }
  }
  return [salairesNets, pensionsNettes, vingt];
}

/** L'abattement de l'article 157 bis, par déclarant de plus de 65 ans ou invalide. */
/** Le bénéfice d'un déclarant tel que l'impôt le retient : voir `benefice_retenu`. */
export function beneficeRetenu(declarant, parametres, benefice = null) {
  const annee = parametres.annee;
  const montant = benefice === null ? declarant.benefices : benefice;
  if (montant <= 0.0 || declarant.regime === "micro") return montant;
  if (declarant.regime === "reel_non_adherent") {
    if (annee < PREMIERE_ANNEE_MAJORATION || annee > DERNIERE_ANNEE_MAJORATION) return montant;
    const coefficient = obtenir(COEFFICIENTS_MAJORATION_DEGRESSIFS, annee, COEFFICIENT_MAJORATION);
    return arrondirElement(annee, montant * coefficient);
  }
  return montant - abattementAdherent(declarant, parametres, montant);
}

function abattementAdherent(declarant, parametres, benefice) {
  const annee = parametres.annee;
  const premiere = declarant.categorie === "bnc"
    ? PREMIERE_ANNEE_ABATTEMENT_BNC : PREMIERE_ANNEE_ABATTEMENT_ADHERENTS;
  if (annee < premiere || annee > DERNIERE_ANNEE_ABATTEMENT_ADHERENTS) return 0.0;
  const plafond = obtenir(parametres.serie("deductions"), "vingt_pour_cent_plafond", Infinity);
  const seuil = Math.min(obtenir(SEUILS_ABATTEMENT_REDUIT, annee, plafond), plafond);
  const abattement = 0.20 * Math.min(benefice, seuil)
    + 0.10 * Math.max(Math.min(benefice, plafond) - seuil, 0.0);
  return arrondirElement(annee, abattement);
}

function abattementAgeInvalidite(foyer, parametres, revenuNetGlobal) {
  const a = parametres.serie("abattement_age_invalidite");
  if (vide(a)) return 0.0;
  const ayantsDroit = foyer.declarants
    .filter((d) => (d.age !== null && d.age >= AGE_ABATTEMENT) || d.invalide).length;
  let montant;
  if (revenuNetGlobal <= a.seuil_plein) montant = a.abattement_plein;
  else if (revenuNetGlobal <= a.seuil_reduit) montant = a.abattement_reduit;
  else montant = 0.0;
  return Number(montant * ayantsDroit);
}

/** L'impôt après plafonnement des effets du quotient familial : [retenu, supplément, réduction]. */
function plafonnement(foyer, parametres, revenu, parts, impotPlein) {
  const plafonds = parametres.serie("plafonds_quotient_familial");
  if (parametres.annee < PREMIERE_ANNEE_PLAFONNEMENT || !("general" in plafonds)) {
    return [impotPlein, 0.0, 0.0];
  }
  const base = foyer.parts_de_base;
  if (parts <= base) return [impotPlein, 0.0, 0.0];
  const demiParts = Math.round((parts - base) * 2);
  const general = plafonds.general;
  let avantage;
  if (parentIsole(foyer)) {
    const premier = obtenir(plafonds, "parent_isole_premier_enfant", 2 * general);
    avantage = premier + general * (demiParts - 2);
  } else {
    avantage = general * demiParts;
  }
  const impotDeBase = impotDuBareme(parametres, revenu, base);
  const plafonne = impotDeBase - avantage;
  if (plafonne <= impotPlein) return [impotPlein, 0.0, 0.0];
  const supplement = plafonne - impotPlein;
  let complement = obtenir(plafonds, "reduction_complementaire_invalide", 0.0)
    * invalidites(foyer, parametres.annee);
  if (foyer.veuf && foyer.enfants) {
    complement += obtenir(plafonds, "reduction_complementaire_veuf", 0.0);
  }
  const reduction = Math.min(complement, supplement);
  return [plafonne - reduction, supplement, reduction];
}

/** La décote, selon la règle de l'année : voir `decote` dans le Python. */
export function decote(foyer, parametres, impot, parts) {
  const d = parametres.serie("decote");
  const annee = parametres.annee;
  if (vide(d) || impot <= 0) return 0.0;
  if (annee <= 1972) {
    let franchise = d.seuil_celibataire;
    let limite = d.seuil_couple;
    if ("nombre_de_parts_limite" in d && parts <= d.nombre_de_parts_limite) {
      franchise = d.seuil_1_faible_nombre_de_parts;
      limite = d.seuil_2_faible_nombre_de_parts;
    }
    if (impot <= franchise) return impot;
    if (impot >= limite) return 0.0;
    const apres = (impot - franchise) * limite / (limite - franchise);
    return arrondirImpot(annee, impot - apres);
  }
  let seuil;
  let taux;
  if (annee <= 1985) {
    seuil = parts === 1.0 ? d.seuil_une_part : parts === 1.5 ? d.seuil_une_part_et_demie : null;
    taux = 1.0;
  } else {
    seuil = foyer.couple && "seuil_couple" in d ? d.seuil_couple : d.seuil_celibataire;
    taux = obtenir(d, "taux", annee <= 1999 ? 1.0 : 0.5);
  }
  if (!seuil) return 0.0;
  return Math.min(impot, Math.max(arrondirImpot(annee, seuil - taux * impot), 0.0));
}

/** La réduction de 20 % des revenus de 2016 à 2019, dégressive. */
function reductionSousCondition(foyer, parametres, impot, rfr, parts) {
  const r = parametres.serie("reduction_sous_condition_de_revenus");
  if (vide(r) || impot <= 0) return 0.0;
  const multiple = foyer.couple ? 2.0 : 1.0;
  const demiParts = (parts - foyer.parts_de_base) * 2;
  const bas = r.seuil_bas * multiple + r.majoration_par_demi_part * demiParts;
  const haut = r.seuil_haut * multiple + r.majoration_par_demi_part * demiParts;
  let taux;
  if (rfr <= bas) taux = r.taux;
  else if (rfr < haut) taux = r.taux * (haut - rfr) / (haut - bas);
  else return 0.0;
  return arrondirImpot(parametres.annee, taux * impot);
}

/** Les minorations exceptionnelles, selon les notes de l'IPP. */
function minoration(parametres, impot, revenu, parts) {
  const m = parametres.serie("minorations_exceptionnelles");
  const annee = parametres.annee;
  if (vide(m) || impot <= 0) return 0.0;
  if (annee <= 1972) {
    const base = annee <= 1967 ? revenu : impot;
    const s2 = m.seuil_impot_2;
    const s3 = m.seuil_impot_3;
    const s4 = m.seuil_impot_4;
    const haut = m.taux_1;
    const bas = obtenir(m, "taux_5", 0.0);
    let taux;
    if (base <= s2) taux = haut;
    else if (base <= s3) taux = haut + (bas - haut) * (base - s2) / (s3 - s2);
    else if (base <= s4) taux = bas;
    else taux = 0.0;
    return arrondirImpot(annee, taux * impot);
  }
  const s = [1, 2, 3, 4, 5].map((rang) => obtenir(m, `seuil_impot_${rang}`, null));
  let montant;
  if (impot <= s[1]) montant = m.taux_1 * impot;
  else if (s[2] !== null && impot <= s[2]) montant = m.formule_seuil_2 - m.taux_formule * impot;
  else if (s[3] !== null && impot <= s[3]) montant = m.taux_3 * impot;
  else if (s[4] !== null && impot <= s[4]) montant = m.formule_seuil_4 - m.taux_formule * impot;
  else if (s[4] !== null && revenu / parts <= obtenir(m, "revenu_par_part_maximum", Infinity)) {
    montant = m.taux_5 * impot;
  } else {
    montant = 0.0;
  }
  return arrondirImpot(annee, Math.max(montant, 0.0));
}

/** Les paliers des majorations de 1968 et de 1969. */
function paliersDe1968(impot, pas, tauxHaut) {
  if (impot > 14000) return tauxHaut;
  const palier = Math.floor((Math.min(impot, 13999.99) - 6000) / 1000) + 1;
  return pas * Math.min(palier, 7);
}

/** Les majorations exceptionnelles, selon les notes de l'IPP. */
function majoration(parametres, impot, revenu) {
  const m = parametres.serie("majorations_exceptionnelles");
  const annee = parametres.annee;
  if (vide(m) || impot <= 0) return 0.0;
  if ("seuil_revenu" in m) {
    const taux = revenu > m.seuil_revenu ? m.taux_1 : 0.0;
    return arrondirImpot(annee, taux * impot);
  }
  if (annee === 1968) {
    const taux = impot > m.seuil_1 ? paliersDe1968(impot, 0.02, m.taux_3) : 0.0;
    return arrondirImpot(annee, taux * impot);
  }
  if (annee === 1969) {
    if (impot <= m.seuil_1) return 0.0;
    const taux = impot <= 14000 ? paliersDe1968(impot, 0.02, 2 * m.taux_3) / 2 : m.taux_3;
    return arrondirImpot(annee, taux * impot);
  }
  if (annee <= 1971 || annee === 1983) {
    let taux = 0.0;
    for (const rang of [1, 2, 3]) {
      if (`seuil_${rang}` in m && impot > m[`seuil_${rang}`]) taux = m[`taux_${rang}`];
    }
    return arrondirImpot(annee, taux * impot);
  }
  if (annee === 1981 && impot <= 25000) return 0.0;
  return arrondirImpot(annee, m.taux_1 * Math.max(impot - m.seuil_1, 0.0));
}

/** La réduction exceptionnelle des revenus de 2013 (loi n° 2014-891, art. 1). */
function reductionExceptionnelle(foyer, parametres, impot, rfr, parts) {
  const r = parametres.serie("reduction_exceptionnelle");
  if (vide(r) || impot <= 0) return 0.0;
  const multiple = foyer.couple ? 2.0 : 1.0;
  const seuil = r.seuil * multiple
    + r.majoration_par_demi_part * (parts - foyer.parts_de_base) * 2;
  const montant = r.montant * multiple;
  const reduction = rfr <= seuil ? montant : Math.max(seuil + montant - rfr, 0.0);
  return arrondirImpot(parametres.annee, Math.min(reduction, impot));
}

/** Les 5 % retranchés de l'impôt des revenus de 2001. */
function reductionProportionnelle(parametres, impot) {
  const r = parametres.serie("reduction_proportionnelle");
  if (vide(r) || impot <= 0) return 0.0;
  return arrondirImpot(parametres.annee, impot * r.taux);
}

/** Le crédit d'impôt exceptionnel des revenus de 2008 (loi n° 2009-431, art. 1). */
function creditExceptionnel(foyer, parametres, impot, revenu, rfr, parts) {
  const c = parametres.serie("credit_exceptionnel");
  if (vide(c) || impot <= 0) return 0.0;
  const plein = c.revenu_par_part_plein;
  const maximum = c.revenu_par_part_maximum;
  const parPart = revenu / parts;
  if (parPart >= maximum || rfr / parts > maximum) return 0.0;
  if (parPart <= plein) return arrondirImpot(parametres.annee, impot * c.taux);
  let auSeuil = impotDuBareme(parametres, plein * parts, parts);
  [auSeuil] = plafonnement(foyer, parametres, plein * parts, parts, auSeuil);
  auSeuil -= decote(foyer, parametres, auSeuil, parts);
  const creditMaximum = arrondirImpot(parametres.annee, auSeuil * c.taux);
  return arrondirImpot(parametres.annee,
    creditMaximum * (maximum - parPart) / (maximum - plein));
}

/** La prime pour l'emploi (art. 200 sexies), de 2000 à 2015, d'un travail à temps plein. */
export function primePourLEmploi(foyer, parametres, salaires, rfr, parts) {
  const p = parametres.serie("prime_pour_l_emploi");
  if (vide(p)) return 0.0;
  const base = foyer.couple ? p.rfr_couple : p.rfr_personne_seule;
  if (rfr > base + p.rfr_par_demi_part * (parts - foyer.parts_de_base) * 2) return 0.0;
  const actifs = salaires.filter((s) => s >= p.revenu_minimum);
  const monoEmploi = foyer.couple && actifs.length === 1;
  let prime = 0.0;
  let forfaitFamille = false;
  for (const salaire of actifs) {
    let individuelle;
    if (salaire <= p.revenu_taux_plein) individuelle = p.taux_entree * salaire;
    else if (salaire < p.revenu_maximum) individuelle = p.taux_sortie * (p.revenu_maximum - salaire);
    else individuelle = 0.0;
    if (monoEmploi) {
      if (salaire <= p.revenu_maximum) {
        individuelle += p.majoration_mono_emploi;
      } else if (salaire <= p.revenu_taux_plein_mono_emploi) {
        individuelle = p.majoration_mono_emploi;
        forfaitFamille = true;
      } else if (salaire < p.revenu_maximum_mono_emploi) {
        individuelle = p.taux_sortie_mono_emploi * (p.revenu_maximum_mono_emploi - salaire);
        forfaitFamille = true;
      } else {
        individuelle = 0.0;
      }
    }
    prime += individuelle;
  }
  if (actifs.length === 0) return 0.0;
  const totalActif = somme(actifs);
  if (parentIsole(foyer) && p.revenu_maximum < totalActif
    && totalActif < p.revenu_maximum_mono_emploi) {
    forfaitFamille = true;
  }
  if (foyer.enfants && (prime > 0 || forfaitFamille)) {
    const premier = parentIsole(foyer)
      ? p.majoration_parent_isole : p.majoration_par_personne_a_charge;
    if (forfaitFamille) prime += premier;
    else prime += premier + p.majoration_par_personne_a_charge * (foyer.enfants - 1);
  }
  prime = arrondirImpot(parametres.annee, prime);
  if (parametres.annee < PREMIERE_ANNEE_SEUIL_DE_LA_PPE) {
    prime = prime > 0 ? Math.max(prime, p.montant_minimum) : 0.0;
  } else if (prime < p.montant_minimum) {
    prime = 0.0;
  }
  if (parametres.annee === 2000) prime *= 2;
  return prime;
}

function remarquesDe(foyer, parametres, laDecote, laMinoration, laMajoration, ppe,
  benefices = []) {
  const annee = parametres.annee;
  const remarques = [];
  if (parametres.projete) {
    remarques.push(`barème projeté (${parametres.indexation}) au-delà des revenus de `
      + `${parametres.derniere_annee_lue}`);
  }
  if (laDecote && annee <= 1972) {
    remarques.push("franchise et décote des années 1960 : une lecture des colonnes de "
      + "l'IPP, sans texte lu");
  }
  if (laMinoration || laMajoration) {
    remarques.push("minoration ou majoration exceptionnelle : la règle des notes de "
      + "l'IPP, sans texte lu");
  }
  if (ppe) remarques.push("prime pour l'emploi d'un travail à temps plein toute l'année");
  if (annee < PREMIERE_ANNEE_PLAFONNEMENT && foyer.declarants.some((d) => d.invalide)) {
    remarques.push("invalide : les régimes des couples d'avant 1981 ne sont pas repris");
  }
  const adherents = benefices.filter((b, i) => b > 0
    && foyer.declarants[i].regime === "reel_adherent");
  if (adherents.length && annee < PREMIERE_ANNEE_ABATTEMENT_ADHERENTS) {
    remarques.push("bénéfice d'un adhérent d'avant 1978 : l'abattement de sa rédaction, "
      + "que l'index n'a pas, n'est pas appliqué");
  }
  if (adherents.some((b) => b > obtenir(SEUILS_ABATTEMENT_REDUIT, annee, Infinity))) {
    remarques.push("abattement des adhérents : le seuil de sa fraction à 10 % est celui de "
      + "la rédaction de l'année, sans l'indexation que le code prescrit, "
      + "et sa limite celle des salaires");
  }
  return remarques;
}

// -- le calcul ---------------------------------------------------------------

function conversion(parametres, unite) {
  if (unite !== "euro" && unite !== "monnaie") throw new Error(`unité inconnue : '${unite}'`);
  return unite === "euro" && parametres.monnaie === "FRF" ? FRANC : 1.0;
}

/** L'impôt du `foyer` sur ses revenus d'`annee` : voir `impot_du_foyer`. */
export function impotDuFoyer(foyer, annee, baremes, {
  unite = "euro", indexation = "prix", croissance = null,
} = {}) {
  return impotAuxParametres(foyer, baremes.parametres(annee, indexation, croissance), { unite });
}

/** L'impôt du `foyer` sur ses revenus de l'année de `parametres`, lus ou projetés. */
export function impotAuxParametres(foyer, parametres, { unite = "euro" } = {}) {
  const annee = parametres.annee;
  const vers = conversion(parametres, unite);
  const salaires = foyer.declarants.map((d) => auPlusProche(d.salaires * vers));
  const pensions = foyer.declarants.map((d) => auPlusProche(d.pensions * vers));
  const [salairesNets, pensionsNettes, vingt] = revenusNetsDuFoyer(
    foyer, parametres, salaires, pensions);
  const benefices = foyer.declarants.map((d) => auPlusProche(d.benefices * vers));
  const retenus = foyer.declarants.map((d, i) => beneficeRetenu(d, parametres, benefices[i]));
  const abattementAdherents = somme(benefices.map((b, i) => Math.max(b - retenus[i], 0.0)));
  const majorationBenefices = somme(benefices.map((b, i) => Math.max(retenus[i] - b, 0.0)));
  let revenuNetGlobal = Math.max(somme(salairesNets) + somme(pensionsNettes) - vingt
    + somme(retenus), 0.0);
  revenuNetGlobal = arrondirElement(annee, revenuNetGlobal);
  const abattement = Math.min(abattementAgeInvalidite(foyer, parametres, revenuNetGlobal),
    revenuNetGlobal);
  const revenu = arrondirRevenuImposable(annee, revenuNetGlobal - abattement);
  return liquider(foyer, parametres, revenu, salaires, {
    salaires_nets: salairesNets, pensions_nettes: pensionsNettes,
    abattement_vingt_pour_cent: vingt, benefices, benefices_retenus: retenus,
    abattement_adherents: abattementAdherents, majoration_des_benefices: majorationBenefices,
    revenu_net_global: revenuNetGlobal, abattement_age_invalidite: abattement,
  }, unite, vers);
}

/** L'impôt d'un foyer dont on connaît le revenu net imposable, sans prime pour l'emploi. */
export function impotDUnRevenuImposable(foyer, annee, revenuNetImposable, baremes, {
  unite = "euro", indexation = "prix", croissance = null,
} = {}) {
  const parametres = baremes.parametres(annee, indexation, croissance);
  const vers = conversion(parametres, unite);
  const revenu = arrondirRevenuImposable(annee, revenuNetImposable * vers);
  return liquider(foyer, parametres, revenu, [], {
    salaires_nets: [], pensions_nettes: [], abattement_vingt_pour_cent: 0.0,
    benefices_retenus: [], abattement_adherents: 0.0, majoration_des_benefices: 0.0,
    revenu_net_global: revenu, abattement_age_invalidite: 0.0,
  }, unite, vers);
}

/** Du revenu net imposable à l'impôt, dans la monnaie de l'année. */
function liquider(foyer, parametres, revenu, salaires, assiette, unite, vers) {
  const annee = parametres.annee;
  const rfr = revenu;
  const parts = nombreDeParts(foyer, parametres);
  const impotPlein = impotDuBareme(parametres, revenu, parts);
  const [impotBrut, supplement, reductionComplementaire] = plafonnement(
    foyer, parametres, revenu, parts, impotPlein);
  const laDecote = decote(foyer, parametres, impotBrut, parts);
  let impot = impotBrut - laDecote;
  const reductionScr = reductionSousCondition(foyer, parametres, impot, rfr, parts);
  impot -= reductionScr;
  const laMinoration = minoration(parametres, impot, revenu, parts);
  impot -= laMinoration;
  const laMajoration = majoration(parametres, impot, revenu);
  impot += laMajoration;
  const reductionExc = reductionExceptionnelle(foyer, parametres, impot, rfr, parts);
  impot = Math.max(impot - reductionExc, 0.0);
  const reductionProp = reductionProportionnelle(parametres, impot);
  impot -= reductionProp;

  const ppe = salaires.length ? primePourLEmploi(foyer, parametres, salaires, rfr, parts) : 0.0;
  const credit = creditExceptionnel(foyer, parametres, impotBrut - laDecote, revenu, rfr, parts);
  const recouvrement = parametres.serie("recouvrement");
  const misEnRecouvrement = impot > 0 && impot >= obtenir(recouvrement, "seuil", 0.0);
  let net = (misEnRecouvrement ? impot : 0.0) - ppe - credit;
  if (net >= 0 && net < obtenir(recouvrement, "seuil_apres_credits", 0.0)) net = 0.0;
  const retour = 1.0 / vers;
  return Object.freeze({
    annee,
    monnaie: parametres.monnaie,
    unite,
    parts,
    salaires_nets: assiette.salaires_nets.map((s) => s * retour),
    pensions_nettes: assiette.pensions_nettes.map((p) => p * retour),
    abattement_vingt_pour_cent: assiette.abattement_vingt_pour_cent * retour,
    benefices_retenus: assiette.benefices_retenus.map((b) => b * retour),
    abattement_adherents: assiette.abattement_adherents * retour,
    majoration_des_benefices: assiette.majoration_des_benefices * retour,
    revenu_net_global: assiette.revenu_net_global * retour,
    abattement_age_invalidite: assiette.abattement_age_invalidite * retour,
    revenu_net_imposable: revenu * retour,
    revenu_fiscal_de_reference: rfr * retour,
    impot_sans_plafonnement: impotPlein * retour,
    impot_brut: impotBrut * retour,
    plafonnement: supplement * retour,
    reduction_complementaire: reductionComplementaire * retour,
    decote: laDecote * retour,
    reduction_sous_condition_de_revenus: reductionScr * retour,
    minoration_exceptionnelle: laMinoration * retour,
    majoration_exceptionnelle: laMajoration * retour,
    reduction_exceptionnelle: reductionExc * retour,
    reduction_proportionnelle: reductionProp * retour,
    impot_avant_credits: impot * retour,
    prime_pour_l_emploi: ppe * retour,
    credit_exceptionnel: credit * retour,
    mis_en_recouvrement: misEnRecouvrement,
    impot: net * retour,
    fiabilite: parametres.fiabilite,
    remarques: remarquesDe(foyer, parametres, laDecote, laMinoration, laMajoration, ppe,
      assiette.benefices || []),
  });
}
