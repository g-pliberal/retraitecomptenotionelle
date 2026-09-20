/**
 * Courbe des taux sans risque, et taux forward qui s'en déduisent.
 *
 * Portage de ``src/retraite_notionnelle/donnees/taux.py``. Le pilier de
 * capitalisation obligatoire a besoin de deux choses, et cette seule courbe les
 * donne toutes les deux : le taux d'aujourd'hui pour chaque maturité, et le
 * taux auquel se placeront les versements des années suivantes — le taux
 * FORWARD, entièrement déterminé par la courbe :
 *
 *     f(T1, T2) = (z(T2)·T2 − z(T1)·T1) / (T2 − T1)
 *
 * Prendre le forward pour le taux futur, c'est l'hypothèse des anticipations
 * pures : elle ignore la prime de terme, et flatte donc légèrement le pilier.
 *
 * LA PRIME DE TERME, QUAND ON LA RETIRE. `primeTerme` décompose le taux observé
 * en z(T) = z*(T) + phi(T), où z* est la moyenne des taux courts attendus et
 * phi le supplément exigé pour immobiliser son argent T années — proportionnel
 * à la maturité, plafonné au bout de courbe. Les forwards se calculent sur z*,
 * et la prime de la maturité ACHETÉE se rajoute au résultat. À différé nul on
 * retrouve donc exactement le taux coté du jour ; à différé non nul, la
 * maturité cesse d'être neutre, et bloquer celle de l'horizon capte la prime
 * une fois pour toutes là où le roulement la rachète à chaque échéance. Zéro
 * par défaut : c'est le réglage sous lequel le site publie.
 *
 * UNITÉS. La BCE publie des taux à composition CONTINUE, et le paquet de
 * données les garde tels quels. Toute sortie de ce module est en revanche un
 * taux ANNUEL, `exp(r) − 1`, parce que c'est ce qu'une accumulation année par
 * année consomme.
 */

import { Fiabilite } from "./serie.js";

/**
 * Maturité à laquelle `primeTerme` est exprimée : trente ans, le bout de la
 * courbe publiée par la BCE.
 */
export const MATURITE_PRIME = 30;

export class CourbeTauxSansRisque {
  constructor(paquet, primeTerme = 0.0, maturitePrime = MATURITE_PRIME) {
    const courbe = paquet.courbe_taux_sans_risque;
    this.date = courbe.date;
    this.annee = Number.parseInt(courbe.date.slice(0, 4), 10);
    this.maturites = courbe.maturites;
    this.tauxContinus = courbe.taux_continus;
    this.fiabilitePubliee = courbe.fiabilite;
    if (maturitePrime <= 0) {
      throw new Error("la maturité de référence de la prime doit être positive");
    }
    this.primeTerme = primeTerme;
    this.maturitePrime = maturitePrime;
  }

  /**
   * Prime de terme portée par un taux de maturité `duree` : proportionnelle à
   * la maturité, plafonnée au-delà de `maturitePrime` — la courbe ne cote rien
   * de plus loin.
   */
  prime(duree) {
    if (this.primeTerme === 0.0) return 0.0;
    return this.primeTerme * Math.min(duree, this.maturitePrime) / this.maturitePrime;
  }

  /** Le taux zéro-coupon, sa prime de terme retirée. */
  zeroNeutre(horizon) {
    return this.zeroContinu(horizon) - this.prime(horizon);
  }

  /** Forward de `zeroNeutre` : le taux court attendu, sans prime. */
  forwardNeutre(differe, duree) {
    if (duree <= 0) {
      throw new Error("la durée d'un placement doit être strictement positive");
    }
    const arrivee = differe + duree;
    return (this.zeroNeutre(arrivee) * arrivee - this.zeroNeutre(differe) * differe)
      / duree;
  }

  get maturiteMaximale() {
    return this.maturites[this.maturites.length - 1];
  }

  /**
   * Taux zéro-coupon continu à `horizon` années, interpolé linéairement.
   *
   * En deçà de la première maturité publiée et au-delà de la dernière, le taux
   * est prolongé à plat : la courbe ne dit rien de ces horizons, et une
   * extrapolation de pente en dirait davantage qu'elle ne sait.
   */
  zeroContinu(horizon) {
    const maturites = this.maturites;
    if (horizon <= maturites[0]) return this.tauxContinus[0];
    if (horizon >= maturites[maturites.length - 1]) {
      return this.tauxContinus[maturites.length - 1];
    }
    let indice = 0;
    while (indice + 1 < maturites.length && maturites[indice + 1] < horizon) {
      indice += 1;
    }
    const basse = maturites[indice];
    const haute = maturites[indice + 1];
    if (basse === haute) return this.tauxContinus[indice];
    const poids = (horizon - basse) / (haute - basse);
    return this.tauxContinus[indice] * (1 - poids) + this.tauxContinus[indice + 1] * poids;
  }

  /**
   * Taux forward continu d'un placement différé de `differe` années.
   * `differe = 0` rend le taux comptant, sans cas particulier.
   */
  forwardContinu(differe, duree) {
    if (duree <= 0) {
      throw new Error("la durée d'un placement doit être strictement positive");
    }
    const arrivee = differe + duree;
    return (this.zeroContinu(arrivee) * arrivee - this.zeroContinu(differe) * differe)
      / duree;
  }

  /**
   * Taux annuel d'un placement fait en `anneePlacement` pour `duree` années.
   *
   * Le différé se compte en années pleines depuis l'année de la courbe : les
   * versements étant crédités en fin d'année, la courbe est rapportée à la fin
   * de son année d'observation.
   */
  placement(anneePlacement, duree) {
    const differe = Math.max(0, anneePlacement - this.annee);
    const tauxContinu = this.forwardNeutre(differe, duree) + this.prime(duree);
    return {
      taux: Math.exp(tauxContinu) - 1.0,
      differe,
      duree,
      fiabilite: differe + duree <= this.maturiteMaximale
        ? this.fiabilitePubliee
        : Fiabilite.ESTIMEE,
    };
  }
}
