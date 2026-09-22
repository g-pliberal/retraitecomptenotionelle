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

/** Le nombre de rangs sur lesquels `grille` pose une distribution. */
export const RANGS_GRILLE = 1000;

const ACKLAM_A = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
  1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00];
const ACKLAM_B = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
  6.680131188771972e+01, -1.328068155288572e+01];
const ACKLAM_C = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
  -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00];
const ACKLAM_D = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
  3.754408661907416e+00];

/** Φ⁻¹(p) par l'approximation d'Acklam : copie de `quantile_normal`. */
export function quantileNormal(p) {
  const [a, b, c, d] = [ACKLAM_A, ACKLAM_B, ACKLAM_C, ACKLAM_D];
  const bas = 0.02425;
  if (p < bas) {
    const q = Math.sqrt(-2.0 * Math.log(p));
    return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
      / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0);
  }
  if (p > 1.0 - bas) {
    const q = Math.sqrt(-2.0 * Math.log(1.0 - p));
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
      / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0);
  }
  const q = p - 0.5;
  const r = q * q;
  return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
    / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0);
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

  /** Le patrimoine au milieu de chaque rang : copie de `grille`. */
  get grille() {
    if (this._grille) return this._grille;
    const valeurs = [];
    if (this.forme === "quantiles") {
      const points = [[0.0, 0.0], ...this.quantiles];
      const [uDernier, qDernier] = points[points.length - 1];
      for (let i = 0; i < RANGS_GRILLE; i += 1) {
        const u = (i + 0.5) / RANGS_GRILLE;
        if (u >= uDernier) { valeurs.push(qDernier); continue; }
        for (let j = 0; j + 1 < points.length; j += 1) {
          const [u0, q0] = points[j];
          const [u1, q1] = points[j + 1];
          if (u <= u1) { valeurs.push(q0 + (q1 - q0) * (u - u0) / (u1 - u0)); break; }
        }
      }
    } else {
      const sigma = Math.sqrt(2.0 * Math.log(this.moyenne / this.mediane));
      const mu = Math.log(this.mediane);
      for (let i = 0; i < RANGS_GRILLE; i += 1) {
        valeurs.push(Math.exp(mu + sigma * quantileNormal((i + 0.5) / RANGS_GRILLE)));
      }
    }
    this._grille = valeurs;
    return valeurs;
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
