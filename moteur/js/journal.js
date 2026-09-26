/**
 * Le journal de l'échéancier (docs/architecture.md, § 7.4 et annexe C.8).
 *
 * Jumeau de `src/retraite_notionnelle/journal.py`. LE JOURNAL EST L'ÉTAT. On
 * y ajoute, on n'efface jamais, et chaque entrée porte deux dates : son
 * INSCRIPTION — l'événement qui l'a écrite, et sa date — et sa période
 * d'EFFET, [début, fin). Une entrée contient un événement traité, une
 * liquidation, une composante — y compris celles des étapes qui ne liquident
 * rien, la revalorisation de « faire vivre » et l'ASPA de « foyer et net » —,
 * ou une décision figée.
 *
 * Une composante a un identifiant stable, et l'entrée qui la révise la
 * REMPLACE : une composante et ses révisions forment une lignée, où la plus
 * récente l'emporte. Le journal se lit de deux façons, et de deux seulement :
 * `etatAu`, l'état à une date, et `servi`, ce qui est servi pour une période.
 *
 * Chaque entrée suit le contrat C.8 (`data/reference/contrats/entree_journal.yaml`).
 */

/** La version du contrat C.8 que `Entree.donnees` suit. */
export const SCHEMA_VERSION = 1;

/** Une entrée du journal (contrat C.8). */
export class Entree {
  /**
   * `evenement` et `inscriteLe` : l'événement qui l'a écrite, et sa date
   * (AAAA-MM-JJ). `debut` et `fin` : sa période d'effet, [début, fin) ; une
   * fin nulle ne borne rien. `sorte` : `evenement`, `liquidation`,
   * `composante`, `revalorisation`, `foyer` ou `decision`. `remplace` :
   * l'entrée qu'elle révise, dont elle prend la lignée ; `annule` :
   * l'événement en attente qu'elle annule.
   */
  constructor({ id, evenement, inscriteLe, debut = null, fin = null, sorte, contenu,
    remplace = null, annule = null }) {
    this.id = id;
    this.evenement = evenement;
    this.inscriteLe = inscriteLe;
    this.debut = debut;
    this.fin = fin;
    this.sorte = sorte;
    this.contenu = contenu;
    this.remplace = remplace;
    this.annule = annule;
    Object.freeze(this);
  }

  /** Son effet couvre-t-il la période [debut, fin) ? */
  couvre(debut, fin) {
    if (this.debut !== null && this.debut > debut) {
      return false;
    }
    if (this.fin === null) {
      return true;
    }
    return fin !== null && fin <= this.fin;
  }

  /**
   * L'entrée, telle que le contrat C.8 la décrit ; son contenu est la donnée
   * qu'elle porte, décrite par son propre contrat ou schéma.
   */
  donnees() {
    const contenu = typeof this.contenu?.donnees === "function"
      ? this.contenu.donnees() : this.contenu;
    const donnee = {
      schema_version: SCHEMA_VERSION,
      id: this.id,
      inscrite: { evenement: this.evenement, date: this.inscriteLe },
      effet: [this.debut, this.fin],
      contenu: { sorte: this.sorte, donnee: contenu },
    };
    if (this.remplace !== null) {
      donnee.remplace = this.remplace;
    }
    if (this.annule !== null) {
      donnee.annule = this.annule;
    }
    return donnee;
  }
}

/** Le journal : une liste d'entrées où l'on ajoute sans jamais effacer. */
export class Journal {
  constructor() {
    this._entrees = [];
    this._parId = new Map();
    // Pour chaque entrée, la racine de sa lignée.
    this._lignee = new Map();
  }

  /**
   * Ajoute `entree`. Un identifiant déjà pris, ou une révision d'une entrée
   * inconnue, est refusé : le journal ne se corrige pas en place.
   */
  inscrire(entree) {
    if (this._parId.has(entree.id)) {
      throw new Error(`entrée déjà inscrite : ${entree.id}`);
    }
    if (entree.remplace !== null && !this._parId.has(entree.remplace)) {
      throw new Error(`${entree.id} remplace une entrée inconnue : ${entree.remplace}`);
    }
    this._entrees.push(entree);
    this._parId.set(entree.id, entree);
    this._lignee.set(entree.id, entree.remplace !== null
      ? this._lignee.get(entree.remplace) : entree.id);
    return entree;
  }

  [Symbol.iterator]() {
    return this._entrees[Symbol.iterator]();
  }

  get length() {
    return this._entrees.length;
  }

  entree(ident) {
    const entree = this._parId.get(ident);
    if (entree === undefined) {
      throw new Error(`entrée inconnue : ${ident}`);
    }
    return entree;
  }

  /** L'état à `date` : tout ce qui a été inscrit au plus tard ce jour-là. */
  etatAu(date) {
    return this._entrees.filter((e) => e.inscriteLe <= date);
  }

  /**
   * Ce qui est servi pour la période [debut, fin) : pour chaque lignée, la
   * dernière entrée inscrite dont l'effet la couvre — une entrée sans
   * montant, qui éteint sa composante, compte comme les autres.
   */
  servi(debut, fin = null, sorte = null) {
    const retenues = new Map();
    for (const entree of this._entrees) {
      if (sorte !== null && entree.sorte !== sorte) {
        continue;
      }
      if (entree.couvre(debut, fin)) {
        retenues.set(this._lignee.get(entree.id), entree);
      }
    }
    return [...retenues.values()];
  }

  donnees() {
    return this._entrees.map((e) => e.donnees());
  }
}
