/**
 * Ce que la pension fait de la prime soumise à retenue, à sa date d'effet :
 * le traitement majoré (le policier, le sapeur-pompier professionnel), ou un
 * supplément de pension (l'aide-soignant). Voir le module Python.
 *
 * Jumeau de `src/retraite_notionnelle/droit/primes.py`, qui fait foi.
 */

import { formatFixe, formatPourcentage } from "../format.js";
import { primesSoumises } from "../primes.js";
import { fiabiliteDepuisTexte } from "../serie.js";
import * as compter from "./compter.js";
import * as coordonner from "./coordonner.js";

/** Les fiches des primes, que `FichesDatees` porte. */
export const FICHES_DES_PRIMES = ["indemnite_sujetions_speciales_police",
  "prime_speciale_sujetion_aides_soignants", "indemnite_de_feu_sapeurs_pompiers"];

/** Ce que la pension fait de la prime. */
export const NATURES_DES_PRIMES = ["traitement", "supplement"];

/** Comment la prime se proratise : voir le Python. */
export const PRORATAS_DES_PRIMES = ["aucun", "services_du_statut",
  "services_du_statut_hors_maximum", "services_du_statut_depuis_2004"];

/** Les conditions qu'une version peut poser. */
export const CONDITIONS_DES_PRIMES = ["aucune", "durees_et_age_de_l_emploi"];

/** La bonification dont les services comptent pour le pourcentage maximum. */
export const BONIFICATION_DU_STATUT = "bonification_cinquieme_sapeurs_pompiers";

/** Ce que la prime d'une pension ajoute, et d'où. */
export class PrimeDeLaPension {
  constructor({ fiche, version, texte, nature, taux, comptee, prorata, fiabilite }) {
    this.fiche = fiche;
    this.version = version;
    this.texte = texte;
    this.nature = nature;
    this.taux = taux;
    this.comptee = comptee;
    this.prorata = prorata;
    this.fiabilite = fiabilite;
  }

  /** La part du traitement de référence que la prime ajoute. */
  get part() {
    return this.taux * this.comptee * this.prorata;
  }

  /** Ce que la page en écrit. */
  detail(montant = null) {
    const prorata = this.prorata >= 1.0 ? "" : ` × ${formatFixe(this.prorata, 4)}`;
    const comptee = this.comptee >= 1.0 ? "" : ` × ${formatFixe(this.comptee, 4)}`;
    if (this.nature === "traitement") {
      return `+ prime de ${formatPourcentage(this.taux, 2)}${comptee}${prorata}`;
    }
    return `supplément de ${formatPourcentage(this.taux, 2)} du traitement${comptee}${prorata}`
      + (montant === null ? "" : `, ${formatFixe(montant, 2, true)} €`);
  }
}

/** La veille d'un jour AAAA-MM-JJ. */
function veille(jour) {
  const [annee, mois, quantieme] = jour.split("-").map(Number);
  const date = new Date(Date.UTC(annee, mois - 1, quantieme - 1));
  return date.toISOString().slice(0, 10);
}

function ligneDeReference(moteur, code, carriere, anneeLiquidation) {
  for (let i = carriere.lignes.length - 1; i >= 0; i -= 1) {
    const ligne = carriere.lignes[i];
    if (!ligne.cotise || ligne.annee > anneeLiquidation) continue;
    const regimes = moteur.affiliations.regimes(
      ligne.affiliation, ligne.annee, carriere.dateEntree(ligne.affiliation));
    if (regimes.includes(code)) return ligne;
  }
  return null;
}

/** La prime que la pension de `code` compte, ou `null`. Voir le Python. */
export function primeDeLaPension(moteur, code, carriere, anneeLiquidation, durees,
  proratisation) {
  const table = primesSoumises(moteur.macro.paquet);
  const ligne = ligneDeReference(moteur, code, carriere, anneeLiquidation);
  if (ligne === null) return null;
  const prime = table.prime(ligne.affiliation);
  if (prime === null || prime.regime !== code) return null;
  const mois = carriere.age_liquidation !== null && carriere.age_liquidation !== undefined
    ? carriere.dateLiquidation.mois : 1;
  const effet = `${String(anneeLiquidation).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`;
  const version = moteur.fichesDatees.version(prime.fiche, effet);
  if (version === null || !version.parametres.existe) return null;
  const parametres = version.parametres;
  const nature = parametres.nature;
  if (!NATURES_DES_PRIMES.includes(nature)) {
    throw new Error(`${prime.fiche}.${version.id} : nature inconnue, ${nature}`);
  }
  const statuts = [...parametres.statuts];
  const borne = coordonner.borneCarriere(carriere);
  const servies = carriere.dureeDeService(statuts, borne);
  const condition = parametres.condition;
  if (!CONDITIONS_DES_PRIMES.includes(condition)) {
    throw new Error(`${prime.fiche}.${version.id} : condition inconnue, ${condition}`);
  }
  let fiabilite = fiabiliteDepuisTexte(parametres.fiabilite);
  if (condition !== "aucune") {
    const ouverte = compter.conditionDUnEmploi(moteur, carriere, condition, parametres,
      servies);
    if (ouverte === null) return null;
    fiabilite = Math.min(fiabilite, ouverte);
  }
  let taux = prime.tauxAu(veille(effet));
  if (parametres.plafond !== null && parametres.plafond !== undefined) {
    taux = Math.min(taux, Number(parametres.plafond));
  }
  const comptee = prime.partComptee(anneeLiquidation);
  if (taux <= 0.0 || comptee <= 0.0) return null;
  const prorata = proratiser(moteur, carriere, code, parametres, servies, durees,
    proratisation, borne);
  if (prorata <= 0.0) return null;
  return new PrimeDeLaPension({
    fiche: prime.fiche, version: version.id, texte: version.texte, nature, taux,
    comptee, prorata, fiabilite,
  });
}

/** Le coefficient de proratisation que la version nomme. Voir le Python. */
export function proratiser(moteur, carriere, code, parametres, servies, durees,
  proratisation, borne) {
  const regle = parametres.prorata;
  if (!PRORATAS_DES_PRIMES.includes(regle)) {
    throw new Error(`prorata inconnu : ${regle}`);
  }
  if (regle === "aucun") return 1.0;
  const statuts = [...parametres.statuts];
  if (regle === "services_du_statut_depuis_2004") {
    const premiere = carriere.bornesDeService(statuts, borne);
    if (premiere !== null && premiere[0] < 2004) return 1.0;
  }
  if (regle === "services_du_statut_hors_maximum") {
    let bonification = 0;
    for (const e of durees.emplois) {
      if (e.fiche === BONIFICATION_DU_STATUT && e.regime === code) bonification += e.services;
    }
    if (servies * 4.0 + bonification + 1e-9 >= proratisation) return 1.0;
  }
  let total = durees.joursDeServices([code]) / compter.JOURS_PAR_AN;
  if (total <= 0.0) {
    // Avant le décompte au jour, les services en trimestres entiers.
    let trimestres = 0;
    for (const nombre of (durees.parAnnee.services.get(code) ?? new Map()).values()) {
      trimestres += nombre;
    }
    total = trimestres / 4.0;
  }
  if (total <= 0.0) return 0.0;
  return Math.min(1.0, servies / total);
}
