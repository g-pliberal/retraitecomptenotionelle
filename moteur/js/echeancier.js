/**
 * L'échéancier (docs/architecture.md, § 7.4).
 *
 * Jumeau de `src/retraite_notionnelle/echeancier.py`. Il parcourt les
 * ÉVÉNEMENTS dans l'ordre des dates, et ceux d'une même date dans l'ordre de
 * leur rang. Aux événements qui ouvrent, révisent ou transforment un droit, il
 * appelle `liquider` : le vocabulaire dit, pour chaque sorte, si elle
 * l'appelle, et avec quel motif et quelle nature — la liste
 * `sortes_d_evenement`, que le paquet porte. Puis, après les liquidations du
 * jour, et à l'échéance qu'on lui demande, il applique les deux étapes qui ne
 * liquident rien : « faire vivre » (`faireVivre`, dans `revalorisation.js`)
 * et « foyer et net » (`droit/foyer.js`).
 *
 * Tout ce qu'il calcule s'inscrit au JOURNAL (`journal.js`), qui est l'état.
 * Une composante revalorisée remplace, dans sa lignée, celle que la
 * liquidation avait écrite. Aujourd'hui, le seul événement est le départ, tiré
 * de la carrière, et l'échéance est l'année courante : voir le Python.
 *
 * Chaque événement suit le contrat C.7 (`data/reference/contrats/evenement.yaml`).
 */

import * as chrono from "./chronologie.js";
import { dateDEffet } from "./droit/commun.js";
import { foyerEtNet } from "./droit/foyer.js";
import * as liquidation from "./droit/liquidation.js";
import { Entree, Journal } from "./journal.js";
import { MinimumVieillesse } from "./regimes.js";
import { aujourdHui, faireVivre, foyerALEcheance } from "./revalorisation.js";
import { resultatActuel } from "./scenario-actuel.js";

/** La version du contrat C.7 que `Evenement.donnees` suit. */
export const SCHEMA_VERSION = 1;

/** Un événement (contrat C.7). */
export class Evenement {
  /**
   * `date` : sa date (AAAA-MM-JJ) ; `personnes` : les personnes concernées ;
   * `vise` : ce qu'il vise, un régime, une liquidation, une allocation ;
   * `origine` : `acte`, `simule`, `observe`, `induit` ou `publication` ;
   * `rang` : l'ordre dans la journée.
   */
  constructor({ id, date, personnes, vise, sorte = "depart", origine = "acte",
    condition = null, rang = 0 }) {
    this.id = id;
    this.date = date;
    this.personnes = [...personnes];
    this.vise = vise;
    this.sorte = sorte;
    this.origine = origine;
    this.condition = condition;
    this.rang = rang;
    Object.freeze(this);
  }

  /** L'événement, tel que le contrat C.7 le décrit. */
  donnees() {
    const donnee = {
      schema_version: SCHEMA_VERSION, id: this.id, date: this.date, sorte: this.sorte,
      personnes: [...this.personnes], vise: this.vise, origine: this.origine,
      rang: this.rang,
    };
    if (this.condition !== null) {
      donnee.condition = this.condition;
    }
    return donnee;
  }
}

/**
 * Le départ que la carrière déclare, à sa date d'effet : un acte de la
 * personne, ou le choix du pilote quand la chronologie le dit simulé.
 */
export function departDe(carriere) {
  const date = dateDEffet(carriere);
  if (date === null) {
    return null;
  }
  const fait = carriere.chronologie
    ? chrono.depart(carriere.chronologie, carriere.personne) : null;
  const origine = fait !== null && fait.origine === "simule" ? "simule" : "acte";
  return new Evenement({
    id: `depart_${carriere.personne}`, date, personnes: [carriere.personne],
    vise: { regimes: "tous" }, origine,
  });
}

/** L'échéancier du droit réel, pour une personne. */
export class Echeancier {
  constructor(simulateur) {
    this.simulateur = simulateur;
    this.moteur = simulateur.scenarioActuel;
    this.journal = new Journal();
    // Ce que chaque sorte d'événement appelle : `liquider`, avec quel motif
    // et quelle nature.
    this.sortes = this.moteur.macro.paquet.sortes_d_evenement;
    // Le scénario 1 à la date d'effet du départ : la liquidation, puis
    // l'ASPA de ce jour-là.
    this.auDepart = null;
    // Le scénario 1 à l'échéance : ce que le droit sert l'année courante.
    this.aujourdhui = null;
  }

  /**
   * Les événements de `carriere`, dans l'ordre, puis, s'il y en a une,
   * l'échéance `echeance` (une année), à laquelle les pensions liquidées sont
   * menées.
   */
  parcourir(carriere, echeance = null) {
    const evenements = [departDe(carriere)].filter((e) => e !== null);
    evenements.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : a.rang - b.rang));
    for (const evenement of evenements) {
      this._traiter(evenement, carriere);
    }
    if (echeance !== null && this.auDepart !== null) {
      this._echeance(carriere, echeance);
    }
    return this.journal;
  }

  _traiter(evenement, carriere) {
    const sorte = this.sortes[evenement.sorte];
    this._inscrire(evenement, evenement.id, "evenement", evenement, evenement.date);
    if (!sorte.liquider) {
      return;
    }
    const demande = new liquidation.Demande({
      personne: evenement.personnes[0], dateEffet: evenement.date,
      evenement: evenement.sorte, dateEvenement: evenement.date,
      motif: sorte.motif ?? "vieillesse", nature: sorte.nature ?? "definitive",
    });
    const contexte = new liquidation.Contexte(this.moteur);
    const resultat = liquidation.liquider(
      demande, new liquidation.Etat(carriere, this.journal), contexte);
    const liquidee = resultat.carriere;
    const foyer = foyerEtNet(
      this.moteur, liquidee.personne, evenement.date, liquidee.anneeLiquidation,
      resultat.total, (liquidee.age_liquidation || 0.0) >= MinimumVieillesse.AGE_OUVERTURE,
      contexte);
    this.auDepart = resultatActuel(resultat, foyer);
    this._inscrire(evenement, `liquidation_${evenement.id}`, "liquidation", resultat,
      evenement.date);
    for (const composante of resultat.composantes()) {
      this._inscrire(evenement, composante.id, "composante", composante, evenement.date);
    }
    this._inscrire(evenement, `foyer_${evenement.id}`, "foyer", foyer, evenement.date);
  }

  /**
   * Faire vivre, puis foyer et net, à l'échéance : les composantes
   * revalorisées remplacent celles du départ, dans leur lignée.
   */
  _echeance(carriere, annee) {
    const date = `${String(annee).padStart(4, "0")}-12-31`;
    const ident = `echeance_${annee}`;
    const vivante = faireVivre(this.simulateur, carriere, this.auDepart, annee);
    const foyer = foyerALEcheance(this.simulateur, carriere, vivante);
    this.aujourdhui = aujourdHui(vivante, foyer, this.auDepart);
    this.journal.inscrire(new Entree({
      id: `revalorisation_${annee}`, evenement: ident, inscriteLe: date, debut: date,
      sorte: "revalorisation", contenu: vivante,
    }));
    for (const regime of vivante.regimes) {
      const origine = `pension_${regime.regime}`;
      this.journal.inscrire(new Entree({
        id: `${origine}_${annee}`, evenement: ident, inscriteLe: date, debut: date,
        sorte: "composante",
        contenu: {
          id: `${origine}_${annee}`, regime: regime.regime,
          montant: { annuel: regime.aujourd_hui, monnaie: "EUR" }, debut: date,
          detail: `× ${regime.coefficient.toFixed(6)}, règle ${regime.regle}`,
        },
        remplace: origine,
      }));
    }
    const depart = [...this.journal].find((e) => e.sorte === "foyer");
    this.journal.inscrire(new Entree({
      id: `foyer_${annee}`, evenement: ident, inscriteLe: date, debut: date,
      sorte: "foyer", contenu: foyer, remplace: depart.id,
    }));
  }

  _inscrire(evenement, ident, sorte, contenu, debut) {
    this.journal.inscrire(new Entree({
      id: ident, evenement: evenement.id, inscriteLe: evenement.date, debut, sorte,
      contenu,
    }));
  }
}
