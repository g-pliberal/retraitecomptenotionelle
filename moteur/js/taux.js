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
 * L'alternative — une prévision de taux — supposerait davantage.
 *
 * UNITÉS. La BCE publie des taux à composition CONTINUE, et le paquet de
 * données les garde tels quels. Toute sortie de ce module est en revanche un
 * taux ANNUEL, `exp(r) − 1`, parce que c'est ce qu'une accumulation année par
 * année consomme.
 */

import { Fiabilite } from "./serie.js";

export class CourbeTauxSansRisque {
  constructor(paquet) {
    const courbe = paquet.courbe_taux_sans_risque;
    this.date = courbe.date;
    this.annee = Number.parseInt(courbe.date.slice(0, 4), 10);
    this.maturites = courbe.maturites;
    this.tauxContinus = courbe.taux_continus;
    this.fiabilitePubliee = courbe.fiabilite;
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
    const tauxContinu = this.forwardContinu(differe, duree);
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
