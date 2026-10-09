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
 * liquidation avait écrite. Aujourd'hui, le départ, tiré de la carrière — un
 * par date quand les régimes ne liquident pas tous ensemble
 * (`droit/departs.js`) —, et, quand la chronologie les dit, le décès de
 * l'assuré et la réversion qu'il ouvre à son conjoint (`droit/reversion.js`),
 * ou, sans décès déclaré, une réversion d'essai, hors du journal ; l'échéance
 * est l'année courante : voir le Python.
 *
 * Chaque événement suit le contrat C.7 (`data/reference/contrats/evenement.yaml`).
 */

import * as chrono from "./chronologie.js";
import { formatFixe } from "./format.js";
import { MAJORATION_ENFANTS, dateDEffet, partsDeLaMajoration } from "./droit/commun.js";
import * as leCumul from "./droit/cumul.js";
import * as lesDeparts from "./droit/departs.js";
import { foyerEtNet } from "./droit/foyer.js";
import { ageDeLAspa } from "./droit/invalidite.js";
import * as liquidation from "./droit/liquidation.js";
import * as lesProgressives from "./droit/progressive.js";
import { moisSuivant, reversion } from "./droit/reversion.js";
import * as laSeconde from "./droit/seconde.js";
import { Entree, Journal } from "./journal.js";
import { aujourdHui, faireVivre, foyerALEcheance } from "./revalorisation.js";
import {
  etatDuDepart, progressiveServie, resultatActuel, resultatDesDeparts,
} from "./scenario-actuel.js";

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
    // La réversion que le décès de l'assuré ouvre à son conjoint, quand la
    // chronologie les dit.
    this.reversion = null;
    // La durée d'assurance de l'assuré dans chaque régime, enfants compris,
    // telle que ses départs l'ont comptée : le minimum de la réversion du
    // régime général la proratise (D. 353-1).
    this.dureesAuDepart = {};
    // La retraite progressive que la carrière demande, sa liquidation
    // provisoire, et, ouverte, le plancher que les départs gardent.
    this.progressive = null;
    this.provisoire = null;
    this.plancher = null;
    // Les composantes servies par la retraite progressive, que celles de la
    // pension complète remplacent dans leur lignée.
    this.progressives = new Map();
  }

  /**
   * Les événements de `carriere`, dans l'ordre, puis, s'il y en a une,
   * l'échéance `echeance` (une année), à laquelle les pensions liquidées sont
   * menées.
   */
  parcourir(carriere, echeance = null) {
    this._progresser(carriere);
    const [departs, demandes] = lesDeparts.departsEtDemandes(this.moteur, carriere);
    if (departs.length > 1 || (departs.length === 1 && !departs[0].unique)) {
      this._partir(carriere, departs);
    } else {
      let evenements = [departDe(carriere)].filter((e) => e !== null);
      if (this.plancher !== null) {
        evenements = evenements.map((e) => new Evenement({
          id: e.id, date: e.date, personnes: e.personnes, vise: e.vise,
          sorte: "pension_definitive", origine: e.origine, condition: e.condition,
          rang: e.rang,
        }));
      }
      evenements.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : a.rang - b.rang));
      for (const evenement of evenements) {
        this._traiter(evenement, carriere);
      }
    }
    if (this.auDepart !== null && this.progressive !== null) {
      this.auDepart.retraite_progressive = progressiveServie(this.progressive,
        this.provisoire, carriere.dateLiquidation);
    }
    if (this.auDepart !== null && demandes.length > 0) {
      this.auDepart.demandes = demandes;
    }
    if (this.auDepart !== null && carriere.conjoint !== null) {
      if (carriere.deces !== null) {
        this._reverser(carriere);
      } else {
        this._reverserALEssai(carriere);
      }
    }
    if (echeance !== null && this.auDepart !== null) {
      this._echeance(carriere, echeance);
    }
    if (this.auDepart !== null && carriere.emploiRetraite !== null) {
      this._cumuler(carriere);
      this._constituer(carriere);
      this._liquiderLesRegimesNouveaux(carriere);
    }
    return this.journal;
  }

  /**
   * Les pensions des régimes que l'activité après le départ ouvre, et qui n'en
   * servaient pas (`droit/seconde.js`) : chacune un départ induit, à sa date,
   * inscrit comme les autres.
   */
  _liquiderLesRegimesNouveaux(carriere) {
    const droits = this.auDepart.droits_apres_depart;
    const contexte = new liquidation.Contexte(this.moteur);
    const liquidations = laSeconde.liquiderLesRegimesNouveaux(this.moteur, carriere,
      this.auDepart, droits, this.auDepart.cumul, contexte, this.journal);
    const pensions = [];
    for (const [date, liquidee] of liquidations) {
      const quand = leCumul.jour(date);
      const evenement = new Evenement({
        id: `depart_${carriere.personne}_${quand}_regimes_nouveaux`, date: quand,
        personnes: [carriere.personne],
        vise: { regimes: liquidee.regimes.map((p) => p.regime) }, origine: "induit",
      });
      this._inscrire(evenement, evenement.id, "evenement", evenement, quand);
      this._inscrire(evenement, `liquidation_${evenement.id}`, "liquidation", liquidee, quand);
      this._composantes(evenement, liquidee);
      for (const p of liquidee.regimes) {
        if (p.montant > 0) {
          pensions.push(new laSeconde.PensionDeRegimeNouveau(p.regime, date, p.montant,
            p.detail));
        }
      }
    }
    if (pensions.length > 0) droits.regimes_nouveaux = pensions;
  }

  /**
   * Les droits de l'activité exercée après le départ (`droit/seconde.js`) :
   * éteints, ou constitués en une nouvelle pension, inscrite à sa date d'effet
   * dans une lignée à elle.
   */
  _constituer(carriere) {
    const droits = laSeconde.droits(this.moteur, carriere, this.auDepart, this.auDepart.cumul);
    this.auDepart.droits_apres_depart = droits;
    const pensions = droits.pensions.filter((p) => p.montant > 0);
    if (pensions.length === 0) return;
    const date = leCumul.jour(pensions[0].date_effet);
    const evenement = new Evenement({
      id: `seconde_pension_${carriere.personne}`, date, personnes: [carriere.personne],
      vise: { regimes: pensions.map((p) => p.regime) }, sorte: "seconde_pension",
    });
    this._inscrire(evenement, evenement.id, "evenement", evenement, date);
    for (const pension of pensions) {
      const ident = `seconde_${pension.regime}`;
      const detail = pension.points === 0
        ? `nouvelle pension, ${pension.trimestres} trimestres sur `
          + `${formatFixe(pension.salaire_mensuel, 2, true)} € par mois`
        : `seconde retraite complémentaire, ${formatFixe(pension.points, 2, true)} points`;
      this._inscrire(evenement, ident, "composante", {
        id: ident, beneficiaire: carriere.personne, regime: pension.regime,
        montant: { annuel: pension.montant, monnaie: "EUR" }, debut: date, detail,
      }, date);
    }
  }

  /**
   * L'activité exercée après le départ (`droit/cumul.js`) : ce que chaque
   * pension en garde, mois par mois, que le résultat du départ porte. Une
   * pension réduite, suspendue ou non due s'inscrit pour les mois où elle
   * l'est, dans sa lignée : voir le Python.
   */
  _cumuler(carriere) {
    const pensionsDe = (annee) => {
      const vivante = faireVivre(this.simulateur, carriere, this.auDepart, annee);
      const pensions = {};
      for (const regime of vivante.regimes) pensions[regime.regime] = regime.aujourd_hui;
      return [pensions, vivante.majoration_enfants * vivante.coefficient_majoration];
    };
    const cumul = leCumul.cumuler(this.moteur, carriere, this.auDepart, pensionsDe,
      this.simulateur.parametres.annee_courante);
    this.auDepart.cumul = cumul;
    const emploi = carriere.emploiRetraite;
    const debut = new Evenement({
      id: `emploi_retraite_${carriere.personne}`, date: leCumul.jour(cumul.debut),
      personnes: [carriere.personne],
      vise: { periode: "emploi_retraite", affiliation: emploi.affiliation,
        employeur: emploi.employeur },
      sorte: "debut_de_periode",
    });
    this._inscrire(debut, debut.id, "evenement", debut, debut.date);
    for (const tranche of cumul.tranches) {
      const depuis = leCumul.jour(tranche.debut);
      const jusqua = leCumul.jour(tranche.fin);
      for (const pension of tranche.par_regime) {
        if (pension.reduction <= 0) continue;
        const ident = `cumul_${pension.regime}_${depuis}`;
        this.journal.inscrire(new Entree({
          id: ident, evenement: debut.id, inscriteLe: debut.date, debut: depuis, fin: jusqua,
          sorte: "composante",
          contenu: {
            id: ident, regime: pension.regime,
            montant: { annuel: (pension.montant - pension.reduction) * 12.0, monnaie: "EUR" },
            debut: depuis, fin: jusqua,
            detail: `cumul emploi-retraite, ${pension.statut} (${pension.regle}) : `
              + `${formatFixe(pension.reduction, 2, true)} € par mois non servis`,
          },
          remplace: `pension_${pension.regime}`,
        }));
      }
    }
    const fin = new Evenement({
      id: `fin_emploi_retraite_${carriere.personne}`, date: leCumul.jour(cumul.fin),
      personnes: [carriere.personne], vise: { periode: "emploi_retraite" },
      sorte: "fin_de_periode",
    });
    this._inscrire(fin, fin.id, "evenement", fin, fin.date);
  }

  /**
   * Le décès de l'assuré, puis la réversion qu'il ouvre à son conjoint, dans
   * les régimes de sa liquidation (§ 7.3) : sa pension y est menée jusqu'à
   * l'année du décès — l'année courante pour un décès à venir, où s'arrêtent
   * les revalorisations publiées ; jamais avant le départ, dont les montants
   * sont les euros.
   */
  _reverser(carriere) {
    const deces = new Evenement({
      id: `deces_${carriere.personne}`, date: carriere.deces,
      personnes: [carriere.personne], vise: {}, sorte: "deces",
    });
    this._inscrire(deces, deces.id, "evenement", deces, deces.date);
    const [annee, pensions, enCapital, majorations, minima, maxima] = this._pensionsAuDeces(
      carriere, carriere.deces);
    this.reversion = reversion(this.moteur, pensions, carriere, annee, null, enCapital,
      majorations, this.dureesAuDepart, minima, maxima);
    const survivant = carriere.conjoint.personne;
    const evenement = new Evenement({
      id: `reversion_${survivant}`, date: moisSuivant(carriere.deces),
      personnes: [survivant], vise: { regimes: "du défunt" }, sorte: "reversion",
    });
    this._inscrire(evenement, evenement.id, "evenement", evenement, evenement.date);
    this._inscrire(evenement, `liquidation_${evenement.id}`, "reversion", this.reversion,
      evenement.date);
  }

  /**
   * Sans décès déclaré, la réversion d'un décès supposé juste après le départ,
   * ou au 1er janvier de l'année courante pour qui est déjà parti (présomption
   * `deces_apres_le_depart`) : ce que le conjoint recevrait. Elle ne
   * s'inscrit pas au journal, qui ne tient que ce qui arrive.
   */
  _reverserALEssai(carriere) {
    const liquidation = carriere.dateLiquidation;
    const depart = `${String(liquidation.annee).padStart(4, "0")}-`
      + `${String(liquidation.mois).padStart(2, "0")}-01`;
    const courante = `${String(this.simulateur.parametres.annee_courante).padStart(4, "0")}-01-01`;
    const deces = depart > courante ? depart : courante;
    const [annee, pensions, enCapital, majorations, minima, maxima] = this._pensionsAuDeces(
      carriere, deces);
    this.reversion = reversion(this.moteur, pensions, carriere, annee, deces, enCapital,
      majorations, this.dureesAuDepart, minima, maxima);
  }

  /**
   * Les pensions du défunt menées à l'année du décès — l'année courante pour
   * un décès à venir, jamais avant le départ —, cette année, les régimes qui
   * lui ont versé leur droit en capital avant son décès, sa majoration pour
   * enfants, régime par régime, menée comme la pension qui la porte, et de même
   * la part de chaque pension que le minimum contributif y ajoute ; enfin,
   * régime par régime, ce que le maximum des pensions en a retiré et ce que la
   * surcote y ajoute, menés de même, et le coefficient qui multiplie son
   * maximum.
   */
  _pensionsAuDeces(carriere, deces) {
    const annee = Math.max(carriere.anneeLiquidation, Math.min(
      Number(deces.slice(0, 4)), this.simulateur.parametres.annee_courante));
    const vivante = faireVivre(this.simulateur, carriere, this.auDepart, annee);
    const servies = vivante.regimes.map(
      // La réversion lit la pension sans la majoration pour conjoint à charge.
      (r) => [r.regime, r.conjoint_au_depart
        ? (r.au_depart - r.conjoint_au_depart) * r.coefficient
        : r.au_depart * r.coefficient, r.fiabilite]);
    // Une pension qu'un régime ne sert pas encore au décès est celle que le
    // défunt « eût obtenue » : la réversion la lit, au montant du départ
    // déclaré (`droit/departs.js`). Celle qu'il sert déjà, quand elle a été
    // versée en une fois, est soldée : le RAFP ne la reverse pas.
    const vues = new Set(servies.map(([regime]) => regime));
    const enCapital = new Set(this.auDepart.pensions_par_regime
      .filter((p) => p.capital !== undefined && p.capital !== null && vues.has(p.regime))
      .map((p) => p.regime));
    // La majoration pour enfants est hors des pensions de régime, le minimum
    // contributif dedans : la part de l'une et de l'autre dans chaque régime
    // (`par_regime`), en euros du départ, suit le rapport de la pension servie
    // à celle du départ — celle des enfants à charge n'en est pas : elle ne se
    // reverse pas.
    const auDepart = new Map(this.auDepart.pensions_par_regime.map((p) => [p.regime, p.montant]));
    const mener = (parts) => {
      const resultat = {};
      for (const r of vivante.regimes) {
        if (parts.get(r.regime) && auDepart.get(r.regime)) {
          resultat[r.regime] = parts.get(r.regime) * r.au_depart * r.coefficient
            / auDepart.get(r.regime);
        }
      }
      for (const p of this.auDepart.pensions_par_regime) {
        if (!vues.has(p.regime) && parts.get(p.regime)) {
          resultat[p.regime] = parts.get(p.regime);
        }
      }
      return resultat;
    };
    const menees = (code) => {
      const parts = new Map();
      const entrees = code === MAJORATION_ENFANTS
        ? partsDeLaMajoration(this.auDepart.avantages_appliques, null, false)
        : this.auDepart.avantages_appliques.filter((avantage) => avantage.code === code)
          .flatMap((avantage) => avantage.par_regime ?? []);
      for (const [regime, part] of entrees) {
        parts.set(regime, (parts.get(regime) ?? 0.0) + part);
      }
      return mener(parts);
    };
    // Ce que le maximum des pensions a retiré de chacune, et ce que la surcote
    // y ajoute, aux euros du départ, sont menés comme elle ; le coefficient de
    // l'ajournement, qui multiplie son maximum, reste le sien.
    const departs = this.auDepart.pensions_par_regime;
    const ecretements = mener(new Map(departs.map(
      (p) => [p.regime, p.ecretement_du_maximum ?? 0.0])));
    const surcotes = mener(new Map(departs.map((p) => [p.regime, p.surcote ?? 0.0])));
    const maxima = {};
    for (const p of departs) {
      const coefficient = p.coefficient_du_maximum ?? 1.0;
      if (p.regime in ecretements || p.regime in surcotes || coefficient !== 1.0) {
        maxima[p.regime] = [ecretements[p.regime] ?? 0.0, surcotes[p.regime] ?? 0.0,
          coefficient];
      }
    }
    return [annee, [...servies, ...this.auDepart.pensions_par_regime
      .filter((p) => !vues.has(p.regime))
      .map((p) => [p.regime, p.montant, p.fiabilite])], enCapital,
    menees(MAJORATION_ENFANTS), menees("minimum_contributif"), maxima];
  }

  /**
   * La retraite progressive que la carrière demande : examinée, et, ouverte,
   * liquidée à titre provisoire et inscrite, chaque composante pour la
   * fraction qu'elle sert (`droit/progressive.js`).
   */
  _progresser(carriere) {
    let progressive = lesProgressives.examiner(this.moteur, carriere);
    this.progressive = progressive;
    if (progressive === null || !progressive.ouverte) {
      return;
    }
    const contexte = new liquidation.Contexte(this.moteur);
    const provisoire = lesProgressives.liquider(this.moteur, carriere, contexte, progressive,
      this.journal);
    progressive = lesProgressives.avecLaDuree(progressive, provisoire);
    this.progressive = progressive;
    this.provisoire = provisoire;
    if (!progressive.ouverte) {
      return;
    }
    this.plancher = [progressive, provisoire];
    const evenement = new Evenement({
      id: `retraite_progressive_${carriere.personne}`, date: progressive.dateEffet,
      personnes: [carriere.personne], vise: { regimes: [...progressive.regimes].sort() },
      sorte: "retraite_progressive",
    });
    this._inscrire(evenement, evenement.id, "evenement", evenement, evenement.date);
    this._inscrire(evenement, `liquidation_${evenement.id}`, "liquidation", provisoire,
      evenement.date);
    const pourcent = formatFixe(progressive.fraction * 100, 0);
    for (const composante of provisoire.composantes()) {
      const entiere = composante.montant.annuel;
      const servie = {
        ...composante,
        id: `progressive_${composante.id}`,
        montant: { annuel: entiere * progressive.fraction, monnaie: "EUR" },
        detail: `${composante.detail} ; retraite progressive : ${pourcent} % de `
          + `${formatFixe(entiere, 2, true)} €`,
      };
      this._inscrire(evenement, servie.id, "composante", servie, evenement.date);
      const cle = composante.id.startsWith("majoration_enfants")
        ? "majoration_enfants" : composante.id;
      this.progressives.set(cle, servie.id);
    }
  }

  /**
   * Les composantes d'une liquidation définitive, inscrites : celles qu'une
   * retraite progressive servait déjà sont remplacées dans leur lignée.
   */
  _composantes(evenement, resultat) {
    for (const composante of resultat.composantes()) {
      const cle = composante.id.startsWith("majoration_enfants")
        ? "majoration_enfants" : composante.id;
      const remplace = this.progressives.get(cle) ?? null;
      this.progressives.delete(cle);
      this._inscrire(evenement, composante.id, "composante", composante, evenement.date,
        remplace);
    }
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
      demande, etatDuDepart(this.moteur, carriere, this.plancher, this.journal), contexte);
    const liquidee = resultat.carriere;
    const foyer = foyerEtNet(
      this.moteur, liquidee.personne, evenement.date, liquidee.anneeLiquidation,
      resultat.total, (liquidee.age_liquidation || 0.0) >= ageDeLAspa(this.moteur, liquidee),
      contexte, liquidee);
    this.auDepart = resultatActuel(resultat, foyer);
    this.dureesAuDepart = Object.fromEntries(resultat.releve.durees.trimestresParRegime);
    this._inscrire(evenement, `liquidation_${evenement.id}`, "liquidation", resultat,
      evenement.date);
    this._composantes(evenement, resultat);
    this._inscrire(evenement, `foyer_${evenement.id}`, "foyer", foyer, evenement.date);
  }

  /**
   * Un départ par date, quand les régimes ne liquident pas tous ensemble :
   * chacun liquide ses régimes, en voyant servies les pensions des précédents,
   * et s'inscrit au journal ; le scénario 1 du départ déclaré les réunit
   * (`resultatDesDeparts`), l'ASPA de ce jour-là comprise.
   */
  _partir(carriere, departs) {
    const declare = departDe(carriere);
    const contexte = new liquidation.Contexte(this.moteur);
    const liquidations = lesDeparts.liquiderLesDeparts(
      this.moteur, carriere, contexte, "definitive", departs, this.journal, this.plancher);
    departs.forEach((depart, rang) => {
      const resultat = liquidations[rang];
      const evenement = new Evenement({
        id: `depart_${carriere.personne}_${depart.dateEffet}`, date: depart.dateEffet,
        personnes: [carriere.personne], vise: { regimes: [...depart.regimes].sort() },
        // Le départ déclaré est un acte, comme la date qu'une personne
        // demande ; les autres dates, la présomption depart_de_chaque_regime
        // les induit.
        origine: depart.dateEffet === declare.date ? declare.origine
          : depart.motif === lesDeparts.MOTIF_DEMANDE ? "acte" : "induit",
      });
      this._inscrire(evenement, evenement.id, "evenement", evenement, evenement.date);
      this._inscrire(evenement, `liquidation_${evenement.id}`, "liquidation", resultat,
        evenement.date);
      this._composantes(evenement, resultat);
    });
    this.auDepart = resultatDesDeparts(this.moteur, carriere, departs, liquidations, contexte);
    // Chaque départ compte les durées de ses régimes : la plus longue que l'un
    // d'eux a comptée dans un régime est la sienne.
    this.dureesAuDepart = {};
    for (const resultat of liquidations) {
      for (const [code, trimestres] of resultat.releve.durees.trimestresParRegime) {
        this.dureesAuDepart[code] = Math.max(this.dureesAuDepart[code] ?? 0, trimestres);
      }
    }
    const pensions = this.auDepart.pensions_par_regime
      .reduce((somme, p) => somme + p.montant, 0.0);
    const majoration = this.auDepart.avantages_appliques
      .filter((a) => a.code === "majoration_enfants")
      .reduce((somme, a) => somme + a.montant, 0.0);
    const foyer = foyerEtNet(
      this.moteur, carriere.personne, declare.date, carriere.anneeLiquidation,
      pensions + majoration,
      (carriere.age_liquidation || 0.0) >= ageDeLAspa(this.moteur, carriere), contexte,
      carriere);
    this._inscrire(declare, `foyer_${declare.id}`, "foyer", foyer, declare.date);
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
    this._majorer(carriere, vivante);
    this._relever(carriere, vivante);
    this.journal.inscrire(new Entree({
      id: `revalorisation_${annee}`, evenement: ident, inscriteLe: date, debut: date,
      sorte: "revalorisation", contenu: vivante,
    }));
    for (const regime of vivante.regimes) {
      const origine = `pension_${regime.regime}`;
      let detail = `× ${regime.coefficient.toFixed(6)}, règle ${regime.regle}`;
      if ((regime.majoration ?? 0.0) > 0) {
        detail += ", majoration exceptionnelle de 2023 comprise "
          + `(${formatFixe(regime.majoration, 2, true)} €)`;
      }
      if ((regime.relevement ?? 0.0) > 0) {
        detail += ", relèvement de septembre 2023 compris "
          + `(${formatFixe(regime.relevement, 2, true)} €)`;
      }
      this.journal.inscrire(new Entree({
        id: `${origine}_${annee}`, evenement: ident, inscriteLe: date, debut: date,
        sorte: "composante",
        contenu: {
          id: `${origine}_${annee}`, regime: regime.regime,
          montant: { annuel: regime.aujourd_hui, monnaie: "EUR" }, debut: date,
          detail,
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

  /**
   * La majoration exceptionnelle des petites pensions, que « faire vivre » a
   * calculée : un début de composante, que la loi induit, au mois où elle est
   * due — ou à celui de sa révision —, chaque majoration servie inscrite à son
   * montant de ce mois-là. Voir `_majorer` du Python.
   */
  _majorer(carriere, vivante) {
    const servies = (vivante.majorations ?? []).filter((m) => m.servie > 0);
    if (servies.length === 0) return;
    const quand = servies[0].date;
    const evenement = new Evenement({
      id: `majoration_exceptionnelle_${carriere.personne}`, date: quand,
      personnes: [carriere.personne], vise: { regimes: servies.map((m) => m.regime) },
      sorte: "debut_de_composante", origine: "induit",
    });
    this._inscrire(evenement, evenement.id, "evenement", evenement, quand);
    for (const majoration of servies) {
      const ident = `majoration_exceptionnelle_${majoration.regime}`;
      this._inscrire(evenement, ident, "composante", {
        id: ident, beneficiaire: carriere.personne, regime: majoration.regime,
        montant: { annuel: majoration.servie * 12.0, monnaie: "EUR" }, debut: quand,
        detail: "majoration exceptionnelle des petites pensions (loi n° 2023-270, "
          + `article 18, V) : ${formatFixe(majoration.theorique, 2, true)} € par mois `
          + "au prorata de la durée cotisée, "
          + `${formatFixe(majoration.servie, 2, true)} € sous les plafonds`,
      }, quand);
    }
  }

  /**
   * Le relèvement des exploitants de septembre 2023, que « faire vivre » a
   * calculé : un début de composante, que la loi induit, ce jour-là, les points
   * gratuits et ceux du complément à leur valeur de ce jour. Voir `_relever` du
   * Python.
   */
  _relever(carriere, vivante) {
    const relevement = vivante.relevement ?? null;
    if (relevement === null) return;
    const evenement = new Evenement({
      id: `relevement_des_exploitants_${carriere.personne}`, date: relevement.date,
      personnes: [carriere.personne], vise: { regimes: ["msa_rco"] },
      sorte: "debut_de_composante", origine: "induit",
    });
    this._inscrire(evenement, evenement.id, "evenement", evenement, relevement.date);
    const points = relevement.points_gratuits + relevement.points_complement;
    this._inscrire(evenement, "relevement_msa_rco", "composante", {
      id: "relevement_msa_rco", beneficiaire: carriere.personne, regime: "msa_rco",
      montant: { annuel: points * relevement.valeur_point, monnaie: "EUR" },
      debut: relevement.date,
      detail: "relèvement des pensions prises avant le 1er septembre 2023 (loi "
        + `n° 2023-270, article 18, VI) : ${formatFixe(relevement.points_gratuits, 2, true)} `
        + `points gratuits et ${formatFixe(relevement.points_complement, 0, true)} points de `
        + "complément différentiel, au SMIC net agricole de "
        + `${formatFixe(relevement.smic_net, 4)} €`,
    }, relevement.date);
  }

  _inscrire(evenement, ident, sorte, contenu, debut, remplace = null) {
    this.journal.inscrire(new Entree({
      id: ident, evenement: evenement.id, inscriteLe: evenement.date, debut, sorte,
      contenu, remplace,
    }));
  }
}
