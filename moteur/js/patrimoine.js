/**
 * Le patrimoine des ménages, et ce qu'une succession couvre d'une avance.
 *
 * Copie de `donnees/patrimoine.py`, qui dit les deux formes — quantiles
 * linéaires par morceaux, ou log-normale calée sur la médiane et la moyenne —
 * et ce que la convention fige. La fonction de répartition normale est la
 * formule 7.1.26 d'Abramowitz et Stegun des deux côtés, pour que les deux
 * moteurs rendent le même chiffre.
 */

export const RANGS = Object.freeze({
  d1: 0.1, d2: 0.2, d3: 0.3, d4: 0.4, mediane: 0.5, d6: 0.6,
  d7: 0.7, d8: 0.8, d9: 0.9, p95: 0.95, p99: 0.99,
});

export function repartitionNormale(x) {
  const signe = x >= 0.0 ? 1.0 : -1.0;
  const z = Math.abs(x) / Math.sqrt(2.0);
  const t = 1.0 / (1.0 + 0.3275911 * z);
  const poly = t * (0.254829592 + t * (-0.284496736 + t * (1.421413741
    + t * (-1.453152027 + t * 1.061405429))));
  const erf = 1.0 - poly * Math.exp(-z * z);
  return 0.5 * (1.0 + signe * erf);
}

export class DistributionPatrimoine {
  constructor(population, annee, patrimoine, quantiles, mediane, moyenne) {
    this.population = population;
    this.annee = annee;
    this.patrimoine = patrimoine;
    this.quantiles = quantiles;
    this.mediane = mediane;
    this.moyenne = moyenne;
  }

  get forme() {
    return this.quantiles.length >= 2 ? "quantiles" : "log-normale";
  }

  /** La part d'une avance qu'une succession couvre, en moyenne. */
  couverture(avance) {
    if (avance <= 0.0) return 1.0;
    const esperance = this.forme === "quantiles"
      ? this._esperanceMinQuantiles(avance)
      : this._esperanceMinLognormale(avance);
    return Math.min(1.0, Math.max(0.0, esperance / avance));
  }

  _esperanceMinQuantiles(avance) {
    const points = [[0.0, 0.0], ...this.quantiles];
    let total = 0.0;
    for (let i = 0; i + 1 < points.length; i += 1) {
      const [u0, q0] = points[i];
      const [u1, q1] = points[i + 1];
      const largeur = u1 - u0;
      if (largeur <= 0.0) continue;
      if (q1 <= avance) {
        total += 0.5 * (q0 + q1) * largeur;
      } else if (q0 >= avance) {
        total += avance * largeur;
      } else {
        const uCroise = u0 + largeur * (avance - q0) / (q1 - q0);
        total += 0.5 * (q0 + avance) * (uCroise - u0) + avance * (u1 - uCroise);
      }
    }
    const [uDernier, qDernier] = points[points.length - 1];
    total += Math.min(avance, qDernier) * (1.0 - uDernier);
    return total;
  }

  _esperanceMinLognormale(avance) {
    const sigma = Math.sqrt(2.0 * Math.log(this.moyenne / this.mediane));
    const mu = Math.log(this.mediane);
    const z = (Math.log(avance) - mu) / sigma;
    return this.moyenne * repartitionNormale(z - sigma)
      + avance * (1.0 - repartitionNormale(z));
  }
}

/** Le fichier, population par population, tel que le paquet le porte. */
export class PatrimoineMenages {
  constructor(paquet) {
    const brut = paquet.patrimoine_menages;
    this.patrimoine = brut.patrimoine;
    this._populations = brut.populations;
    this._distributions = new Map();
  }

  get populations() {
    return Object.keys(this._populations).sort();
  }

  annee(population) {
    const entree = this._populations[population];
    if (!entree) throw new Error(`population inconnue : ${population}`);
    return entree.annee;
  }

  statistiques(population) {
    return { ...this._populations[population].statistiques };
  }

  distribution(population) {
    if (this._distributions.has(population)) return this._distributions.get(population);
    const entree = this._populations[population];
    if (!entree) throw new Error(`population inconnue : ${population}`);
    const stats = entree.statistiques;
    const quantiles = Object.keys(stats)
      .filter((nom) => nom in RANGS)
      .map((nom) => [RANGS[nom], stats[nom]])
      .sort((a, b) => a[0] - b[0]);
    const mediane = stats.mediane ?? 0.0;
    const moyenne = stats.moyenne ?? 0.0;
    const distribution = new DistributionPatrimoine(
      population, entree.annee, this.patrimoine, quantiles, mediane, moyenne,
    );
    this._distributions.set(population, distribution);
    return distribution;
  }
}
