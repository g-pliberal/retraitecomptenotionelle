/**
 * Combien de retraités dans chaque caisse, et donc ce que chaque cas type pèse.
 *
 * Portage de ``src/retraite_notionnelle/donnees/effectifs.py``. C'est la pièce
 * qui manquait pour passer de douze carrières de référence à une masse de
 * pensions sans les peser À ÉGALITÉ : l'agent de conduite comptait autant que le
 * salarié au salaire moyen, alors qu'il y a près de cent fois moins de retraités
 * à la SNCF qu'à la Cnav.
 *
 * Un effectif de caisse n'est pas un effectif de personnes : un polypensionné
 * compte dans chacune des siennes, et la somme des caisses dépasse d'un tiers la
 * ligne « tous régimes ». Les poids qu'on en tire sont donc RELATIFS.
 */

import { SerieAnnuelle } from "./serie.js";

/** Effectifs de retraités de droit direct, par caisse et par année. */
export class EffectifsRetraites {
  constructor(paquet) {
    this._series = new Map(
      Object.entries(paquet.effectifs_retraites).map(([caisse, serie]) => [
        caisse, SerieAnnuelle.depuisPaquet(`effectifs_${caisse}`, serie),
      ]),
    );
  }

  caisses() {
    return [...this._series.keys()];
  }

  serie(caisse) {
    const serie = this._series.get(caisse);
    if (serie === undefined) {
      throw new Error(`caisse inconnue : ${caisse}`);
    }
    return serie;
  }

  effectif(caisse, annee) {
    return this.serie(caisse).valeur(annee);
  }

  fiabilite(caisse, annee) {
    return this.serie(caisse).fiabilite(annee);
  }
}
