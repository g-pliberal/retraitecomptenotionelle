/**
 * Les primes que la loi assujettit à la retenue pour pension, année par année
 * (`legislation/primes_soumises_a_retenue.yaml`) : l'indemnité de sujétions
 * spéciales des policiers, la prime spéciale de sujétion des aides-soignants,
 * l'indemnité de feu des sapeurs-pompiers professionnels.
 *
 * La part de primes d'une ligne reste l'assiette du RAFP ; le reste de la
 * rémunération est le traitement et la part soumise de la prime, qui se
 * partagent au taux de la prime et à la part que l'année en compte.
 *
 * Jumeau de `src/retraite_notionnelle/donnees/primes.py`, qui fait foi.
 */

/** Les assiettes d'une retenue ou d'une contribution supplémentaire. */
export const ASSIETTES = ["remuneration_soumise", "traitement_et_prime", "traitement",
  "prime_soumise"];

/** Ce que la rémunération d'une ligne porte, en parts d'elle. */
export class Parts {
  constructor(traitement, prime = 0.0, soumise = 0.0) {
    this.traitement = traitement;
    this.prime = prime;
    this.soumise = soumise;
  }

  /** La part de la rémunération qu'une assiette supplémentaire prend. */
  assiette(nom) {
    if (nom === "remuneration_soumise") return this.traitement + this.soumise;
    if (nom === "traitement_et_prime") return this.traitement + this.prime;
    if (nom === "traitement") return this.traitement;
    if (nom === "prime_soumise") return this.soumise;
    throw new Error(`assiette inconnue : ${nom}`);
  }
}

function premiersDuMois(annee) {
  const jours = [];
  for (let mois = 1; mois <= 12; mois += 1) {
    jours.push(`${String(annee).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`);
  }
  return jours;
}

/** Une prime soumise à retenue. */
export class Prime {
  constructor(brute) {
    this.code = brute.code;
    this.fiche = brute.fiche;
    this.statuts = new Set(brute.statuts);
    this.regime = brute.regime;
    this.taux = brute.taux.map(([depuis, taux]) => [depuis, taux]);
    this.integration = brute.integration.map(([depuis, part]) => [depuis, part]);
  }

  /** Le taux en vigueur ce jour (AAAA-MM-JJ) ; nul avant le premier. */
  tauxAu(jour) {
    let valeur = 0.0;
    for (const [depuis, taux] of this.taux) {
      if (depuis <= jour) valeur = taux;
    }
    return valeur;
  }

  /** La moyenne des taux en vigueur au premier de chaque mois de l'année. */
  tauxAnnuel(annee) {
    let somme = 0;
    for (const jour of premiersDuMois(annee)) somme += this.tauxAu(jour);
    return somme / 12.0;
  }

  /** La part de la prime que l'année compte ; nulle avant l'intégration. */
  partComptee(annee) {
    let part = 0.0;
    for (const [depuis, valeur] of this.integration) {
      if (depuis <= annee) part = valeur;
    }
    return part;
  }
}

/** Une retenue, ou une contribution, supplémentaire du statut. */
export class Supplementaire {
  constructor(brute) {
    this.statuts = new Set(brute.statuts);
    this.regime = brute.regime;
    this.motif = brute.motif;
    this.assiette = brute.assiette;
    this.taux = brute.taux.map(([depuis, salarie, employeur]) => [depuis, salarie, employeur]);
  }

  tauxAu(jour) {
    let valeur = [0.0, 0.0];
    for (const [depuis, salarie, employeur] of this.taux) {
      if (depuis <= jour) valeur = [salarie, employeur];
    }
    return valeur;
  }

  /** Les taux salarié et employeur, en moyenne des mois de l'année. */
  tauxAnnuels(annee) {
    const mois = premiersDuMois(annee).map((jour) => this.tauxAu(jour));
    let salarie = 0;
    let employeur = 0;
    for (const [s] of mois) salarie += s;
    for (const [, e] of mois) employeur += e;
    return [salarie / 12.0, employeur / 12.0];
  }
}

/** La table des primes soumises à retenue et des retenues supplémentaires. */
export class PrimesSoumises {
  constructor(paquet) {
    const brut = paquet.primes_soumises_a_retenue ?? {};
    this.primes = (brut.primes ?? []).map((p) => new Prime(p));
    this.supplementaires = (brut.supplementaires ?? []).map((s) => new Supplementaire(s));
  }

  /** La prime soumise à retenue que ce statut perçoit, ou `null`. */
  prime(statut) {
    return this.primes.find((p) => p.statuts.has(statut)) ?? null;
  }

  /** Le partage de la rémunération d'une année : voir le Python. */
  parts(statut, annee, partPrimes) {
    const reste = 1.0 - partPrimes;
    const prime = this.prime(statut);
    if (prime === null) return new Parts(reste);
    const taux = prime.tauxAnnuel(annee);
    const comptee = prime.partComptee(annee);
    if (taux <= 0.0 || comptee <= 0.0) return new Parts(reste);
    const traitement = reste / (1.0 + taux * comptee);
    return new Parts(traitement, taux * traitement, taux * comptee * traitement);
  }

  /** Ce que les retenues et contributions supplémentaires du statut
   * prélèvent pour ce régime, en taux salarié et employeur de la
   * rémunération entière. */
  tauxSupplementaires(statut, regime, annee, partPrimes) {
    let salarie = 0.0;
    let employeur = 0.0;
    let parts = null;
    for (const supplement of this.supplementaires) {
      if (!supplement.statuts.has(statut) || supplement.regime !== regime) continue;
      const [tauxSalarie, tauxEmployeur] = supplement.tauxAnnuels(annee);
      if (!(tauxSalarie || tauxEmployeur)) continue;
      if (parts === null) parts = this.parts(statut, annee, partPrimes);
      const assiette = parts.assiette(supplement.assiette);
      salarie += tauxSalarie * assiette;
      employeur += tauxEmployeur * assiette;
    }
    return [salarie, employeur];
  }
}

const PRIMES_PAR_PAQUET = new WeakMap();

/** La table du paquet, construite une fois par paquet. */
export function primesSoumises(paquet) {
  let table = PRIMES_PAR_PAQUET.get(paquet);
  if (table === undefined) {
    table = new PrimesSoumises(paquet);
    PRIMES_PAR_PAQUET.set(paquet, table);
  }
  return table;
}
