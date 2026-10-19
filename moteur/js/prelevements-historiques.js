/**
 * L'histoire des prélèvements sur les pensions et sur les salaires —
 * portage de `donnees/prelevements_historiques.py`, qui fait foi et dit le
 * détail (action 138, étape 9).
 *
 * La CSG depuis 1991, la CRDS, la CASA, la maladie des pensions de chaque
 * régime ; sur les salaires, la maladie, le veuvage, l'assurance chômage, la
 * contribution de solidarité des agents publics ; les barèmes propres des
 * indépendants. Une année qui change de taux prélève la moyenne de ses douze
 * mois. Les indicateurs de cycle de vie nets (`cycle-de-vie.js`) en tirent
 * les revenus nets de chaque année et la pension nette de chaque année, donc
 * la convention du COR. Le paquet porte l'histoire telle que le Python la lit
 * (`prelevements_historiques`, `scripts/construire_donnees.py`) ; les dates
 * y sont des chaînes ISO, que l'ordre alphabétique range comme le calendrier.
 */

/** Les familles de la fiche de paie que l'histoire couvre, par leur profil. */
export const FAMILLES = Object.freeze({
  salarie_prive: "prive", salarie_ircantec: "contractuel", agent_seul: "agent",
});

/** Les familles d'indépendants. */
export const FAMILLES_INDEPENDANTES = Object.freeze(["artisan", "commercant", "liberal", "avocat"]);

const REGIMES_AVOCATS = new Set(["cnbf"]);
const REGIMES_LIBERAUX = new Set(["cnavpl"]);
const REGIMES_ARTISANS = new Set(["cancava", "cancava_avant_1973"]);

/** Les tranches d'un barème d'indépendant, en plafonds ; `null`, l'infini. */
export const TRANCHES = Object.freeze({
  tout_revenu: [0.0, null], sous_plafond: [0.0, 1.0],
  sous_trois_plafonds: [0.0, 3.0], sous_quatre_plafonds: [0.0, 4.0],
  sous_cinq_plafonds: [0.0, 5.0], au_dela_de_trois_plafonds: [3.0, null],
  au_dela_de_cinq_plafonds: [5.0, null],
});

/** La famille de l'indépendant qu'aucun de ses régimes ne range ailleurs. */
export const FAMILLE_PAR_DEFAUT = "commercant";

/** L'indemnité journalière : ses bornes, et les familles qui la paient. */
const INDEMNITES = Object.freeze({
  ij_sous_cinq_plafonds: [[0.0, 5.0], ["artisan", "commercant"]],
  ij_artisans_sous_cinq_plafonds: [[0.0, 5.0], ["artisan"]],
  ij_sous_trois_plafonds: [[0.0, 3.0], ["liberal"]],
});

function intersecte(regimes, groupe) {
  for (const regime of regimes) if (groupe.has(regime)) return true;
  return false;
}

/**
 * La famille dont l'histoire prélève une fiche de paie : celle du profil, ou,
 * pour un indépendant, celle de ses régimes de base de l'année ; `null` hors
 * de l'histoire.
 */
export function familleDeLaFiche(profil, regimes) {
  if (profil !== "independant") return FAMILLES[profil] ?? null;
  const codes = [...regimes];
  if (intersecte(codes, REGIMES_AVOCATS)) return "avocat";
  if (intersecte(codes, REGIMES_LIBERAUX)) return "liberal";
  if (intersecte(codes, REGIMES_ARTISANS)) return "artisan";
  return FAMILLE_PAR_DEFAUT;
}

function tranche(revenu, plafond, bas, haut) {
  const plusHaut = haut === null ? revenu : Math.min(revenu, haut * plafond);
  return Math.max(plusHaut - bas * plafond, 0.0);
}

/** Le taux réduit, sur tout le revenu, interpolé entre deux paliers. */
function tauxProgressif(paliers, enPlafonds) {
  let [precedentSeuil, precedentTaux] = paliers[0];
  if (enPlafonds <= precedentSeuil) return precedentTaux;
  for (const [seuil, taux] of paliers.slice(1)) {
    if (enPlafonds <= seuil) {
      const largeur = seuil - precedentSeuil;
      if (largeur <= 0) return taux;
      const part = (enPlafonds - precedentSeuil) / largeur;
      return precedentTaux + part * (taux - precedentTaux);
    }
    precedentSeuil = seuil;
    precedentTaux = taux;
  }
  return precedentTaux;
}

/** Ce qu'un barème d'indépendant prélève d'un revenu annuel, indemnité journalière à part. */
export function baremeIndependant(valeurs, revenu, plafond) {
  const paliers = valeurs.paliers;
  const jusquA = valeurs.progressif_jusqu_a;
  if (paliers && paliers.length && (!jusquA || revenu < jusquA * plafond)) {
    return tauxProgressif(paliers, revenu / plafond) * revenu;
  }
  let total = 0.0;
  for (const [cle, [bas, haut]] of Object.entries(TRANCHES)) {
    total += (valeurs[cle] ?? 0.0) * tranche(revenu, plafond, bas, haut);
  }
  const seuil = valeurs.seuil_euros ?? 0.0;
  return total + (valeurs.sous_seuil ?? 0.0) * Math.min(revenu, seuil)
    + (valeurs.du_seuil_au_plafond ?? 0.0) * Math.max(Math.min(revenu, plafond) - seuil, 0.0);
}

/** Les marches d'un prélèvement, de la plus ancienne à la plus récente. */
export class Serie {
  constructor(nom, marches, tenueAvant = false) {
    this.nom = nom;
    this.marches = marches;
    this.tenue_avant = tenueAvant;
  }

  /** Les taux en vigueur le `jour`, une date ISO. */
  enVigueur(jour) {
    let retenues = {};
    for (const [debut, valeurs] of this.marches) {
      if (debut > jour) break;
      retenues = valeurs;
    }
    // Comme le Python : une marche vide, sous une série tenue avant sa
    // première marche, rend la première.
    if (Object.keys(retenues).length === 0 && this.tenue_avant && this.marches.length) {
      return this.marches[0][1];
    }
    return retenues;
  }

  valeur(jour, cle = "taux") {
    return this.enVigueur(jour)[cle] ?? 0.0;
  }
}

/** Les douze premiers du mois de l'année, en dates ISO. */
function mois(annee) {
  const an = String(annee).padStart(4, "0");
  return Array.from({ length: 12 }, (_, rang) => `${an}-${String(rang + 1).padStart(2, "0")}-01`);
}

function moyenneAnnuelle(annee, f) {
  let total = 0.0;
  for (const jour of mois(annee)) total += f(jour);
  return total / 12.0;
}

/**
 * Les parts du mois de `jour` : celles de la première date de `avant` — des
 * couples [date, parts], dans l'ordre des dates — qu'il précède, sinon `parts`.
 */
function partsDuMois(jour, parts, avant) {
  for (const [jusquAu, partsAvant] of avant) if (jour < jusquAu) return partsAvant;
  return parts;
}

/** Ce que les parts retirent : chaque série sur sa part, dans l'ordre des noms. */
function surLesParts(series, jour, parts) {
  let total = 0.0;
  for (const serie of [...parts.keys()].sort()) {
    total += series[serie].valeur(jour) * parts.get(serie);
  }
  return total;
}

/** Les prélèvements des pensions et des salaires, date par date. */
export class PrelevementsHistoriques {
  constructor({ pensions, salaires, lu_le = "", independants = {}, regimes_des_pensions = new Map(),
    avant_l_age = new Map() }) {
    this.pensions = pensions;
    this.salaires = salaires;
    this.lu_le = lu_le;
    this.independants = independants;
    this.regimes_des_pensions = regimes_des_pensions;
    // Les cotisations qu'un âge borne : avant lui, chacune prend la part de ses
    // régimes aux autres ; à cet âge, plus rien.
    this.avant_l_age = avant_l_age;
  }

  // -- les pensions ----------------------------------------------------------

  /**
   * Ce que les prélèvements du `jour` retirent à une pension, en part du
   * brut, au taux plein de CSG ; `parts`, une `Map` de chaque cotisation
   * maladie à la part de la pension qu'elle prélève.
   */
  tauxPension(jour, parts) {
    const p = this.pensions;
    return p.csg_taux_plein.valeur(jour) + p.crds.valeur(jour) + p.casa.valeur(jour)
      + surLesParts(p, jour, parts);
  }

  /** La moyenne des douze mois ; un mois d'avant une date de `avant` prend ses parts. */
  tauxPensionAnnuel(annee, parts, avant = []) {
    return moyenneAnnuelle(annee,
      (jour) => this.tauxPension(jour, partsDuMois(jour, parts, avant)));
  }

  tauxCsgPension(jour, taux) {
    return this.pensions[`csg_taux_${taux}`].valeur(jour);
  }

  csgDeductiblePension(jour, taux = "plein") {
    return this.pensions[`csg_taux_${taux}`].valeur(jour, "deductible");
  }

  /** Ce que le revenu imposable du `jour` déduit d'une pension, en part du brut. */
  tauxDeductiblePension(jour, parts) {
    return this.csgDeductiblePension(jour) + surLesParts(this.pensions, jour, parts);
  }

  tauxDeductiblePensionAnnuel(annee, parts, avant = []) {
    return moyenneAnnuelle(annee,
      (jour) => this.tauxDeductiblePension(jour, partsDuMois(jour, parts, avant)));
  }

  // -- les salaires ----------------------------------------------------------

  assietteCsg(jour, brut, plafond) {
    const csg = this.salaires.csg.enVigueur(jour);
    const abattement = (csg.abattement ?? 0.0) * brut
      + (csg.abattement_jusqu_a_quatre_plafonds ?? 0.0) * Math.min(brut, 4.0 * plafond);
    return brut - abattement;
  }

  maladie(jour, serie, brut, plafond) {
    const taux = this.salaires[serie].enVigueur(jour);
    return (taux.tout_salaire ?? 0.0) * brut
      + (taux.sous_plafond ?? 0.0) * Math.min(brut, plafond)
      + (taux.au_dela_du_plafond ?? 0.0) * Math.max(brut - plafond, 0.0);
  }

  chomage(jour, brut, plafond) {
    const taux = this.salaires.chomage_prive.enVigueur(jour);
    return (taux.tout_salaire ?? 0.0) * brut
      + (taux.sous_plafond ?? 0.0) * Math.min(brut, plafond)
      + (taux.de_un_a_quatre_plafonds ?? 0.0)
        * Math.min(Math.max(brut - plafond, 0.0), 3.0 * plafond);
  }

  /** La contribution exceptionnelle de solidarité des agents publics. */
  solidarite(jour, brut, plafond, cotisations) {
    const taux = this.salaires.solidarite_public.enVigueur(jour);
    if (!taux.taux || brut / 12.0 <= (taux.seuil_mensuel ?? 0.0)) return 0.0;
    return taux.taux * Math.min(Math.max(brut - cotisations, 0.0), 4.0 * plafond);
  }

  // -- les indépendants ------------------------------------------------------

  maladieIndependant(famille, jour, revenu, plafond) {
    const nom = famille === "liberal" || famille === "avocat"
      ? "maladie_professions_liberales" : "maladie_artisans_commercants";
    const valeurs = this.independants[nom].enVigueur(jour);
    let indemnites = 0.0;
    for (const [cle, [[bas, haut], familles]] of Object.entries(INDEMNITES)) {
      if (familles.includes(famille)) {
        indemnites += (valeurs[cle] ?? 0.0) * tranche(revenu, plafond, bas, haut);
      }
    }
    return baremeIndependant(valeurs, revenu, plafond) + indemnites;
  }

  familleIndependant(jour, revenu, plafond) {
    return baremeIndependant(this.independants.famille.enVigueur(jour), revenu, plafond);
  }

  assietteIndependant(famille, jour, revenu, plafond, cotisations) {
    const maladie = this.maladieIndependant(famille, jour, revenu, plafond);
    const allocations = this.familleIndependant(jour, revenu, plafond);
    let assiette = revenu;
    if (this.independants.assiette_csg.valeur(jour, "cotisations_ajoutees")) {
      assiette += cotisations + maladie + allocations;
    }
    return [maladie, allocations, assiette];
  }

  independant(famille, jour, revenu, plafond, cotisations) {
    const [maladie, allocations, assiette] = this.assietteIndependant(
      famille, jour, revenu, plafond, cotisations);
    const taux = this.salaires.csg.valeur(jour) + this.salaires.crds.valeur(jour);
    return maladie + allocations + taux * assiette;
  }

  /**
   * Ce que les prélèvements salariaux hors retraite du `jour` retirent d'un
   * brut annuel, sous un plafond annuel ; pour un indépendant, `brut` est son
   * revenu, et `retraiteSalarie` ses cotisations que l'histoire ne refait pas.
   */
  horsRetraite(famille, jour, brut, plafond, retraiteSalarie = 0.0) {
    if (FAMILLES_INDEPENDANTES.includes(famille)) {
      return this.independant(famille, jour, brut, plafond, retraiteSalarie);
    }
    const assiette = this.assietteCsg(jour, brut, plafond);
    let total = (this.salaires.csg.valeur(jour) + this.salaires.crds.valeur(jour)) * assiette;
    let maladie;
    if (famille === "prive" || famille === "contractuel") {
      maladie = this.maladie(jour, "maladie_prive", brut, plafond);
      total += maladie + this.maladie(jour, "veuvage_prive", brut, plafond);
    } else {
      maladie = this.maladie(jour, "maladie_etat", brut, plafond);
      total += maladie;
    }
    if (famille === "prive") {
      total += this.chomage(jour, brut, plafond);
    } else {
      total += this.solidarite(jour, brut, plafond, retraiteSalarie + maladie);
    }
    return total;
  }

  horsRetraiteAnnuel(famille, annee, brut, plafond, retraiteSalarie = 0.0) {
    return moyenneAnnuelle(annee,
      (jour) => this.horsRetraite(famille, jour, brut, plafond, retraiteSalarie));
  }

  // -- le net imposable ------------------------------------------------------

  /**
   * Ce que les prélèvements du `jour` retirent d'un brut annuel sans que le
   * revenu imposable le déduise : la CSG au-delà de sa part déductible, et la
   * CRDS. Une famille que l'histoire ne connaît pas (`null`) a l'assiette d'un
   * salarié.
   */
  nonDeductibles(famille, jour, brut, plafond, retraiteSalarie = 0.0) {
    const csg = this.salaires.csg.enVigueur(jour);
    const taux = (csg.taux ?? 0.0) - (csg.deductible ?? 0.0) + this.salaires.crds.valeur(jour);
    if (!taux) return 0.0;
    const assiette = FAMILLES_INDEPENDANTES.includes(famille)
      ? this.assietteIndependant(famille, jour, brut, plafond, retraiteSalarie)[2]
      : this.assietteCsg(jour, brut, plafond);
    return taux * assiette;
  }

  nonDeductiblesAnnuel(famille, annee, brut, plafond, retraiteSalarie = 0.0) {
    return moyenneAnnuelle(annee,
      (jour) => this.nonDeductibles(famille, jour, brut, plafond, retraiteSalarie));
  }
}

function lireSeries(groupe) {
  return Object.fromEntries(Object.entries(groupe ?? {}).map(([nom, serie]) => [
    nom, new Serie(nom, serie.marches.map(([debut, valeurs]) => [debut, valeurs]),
      serie.tenue_avant)]));
}

const lues = new WeakMap();

/** L'histoire du paquet, lue une fois ; `null` quand le paquet ne la porte pas. */
export function chargerPrelevementsHistoriques(paquet) {
  if (lues.has(paquet)) return lues.get(paquet);
  const brut = paquet.prelevements_historiques ?? null;
  const historique = brut === null ? null : new PrelevementsHistoriques({
    pensions: lireSeries(brut.pensions),
    salaires: lireSeries(brut.salaires),
    lu_le: brut.lu_le ?? "",
    independants: lireSeries(brut.independants),
    regimes_des_pensions: new Map(Object.entries(brut.regimes_des_pensions ?? {})
      .map(([serie, regimes]) => [serie, new Set(regimes)])),
    avant_l_age: new Map(Object.entries(brut.avant_l_age ?? {})),
  });
  lues.set(paquet, historique);
  return historique;
}
