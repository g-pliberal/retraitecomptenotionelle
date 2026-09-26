/**
 * Le relevé des droits (docs/architecture.md, § 7.2 et 7.6).
 *
 * Jumeau de `src/retraite_notionnelle/droit/releve.py` : `construire` enchaîne
 * les étapes de l'acquisition — coordonner les affiliations, compter les
 * durées, acquérir les droits —, puis réunit en groupes les régimes où un
 * droit est acquis ; la liquidation du scénario 1 lit ce qu'il rend. Le relevé
 * se publie en lignes, que le contrat C.5 décrit : `Releve.lignes`.
 */

import * as chrono from "../chronologie.js";
import { nomFiabilite } from "../serie.js";
import * as acquerirEtape from "./acquerir.js";
import { dateDEffet } from "./commun.js";
import * as compterEtape from "./compter.js";
import * as coordonnerEtape from "./coordonner.js";

/** La version du contrat C.5 que les lignes et l'enveloppe suivent. */
export const SCHEMA_VERSION = 1;

/** Les fiches de la carte que certaines lignes appliquent. */
export const FICHE_RETABLISSEMENT = "retablissement_fonction_publique";
export const FICHE_SERVICES = "services_et_duree_fonction_publique";
export const FICHE_ENFANTS = "majoration_duree_assurance_enfants";
export const FICHE_POINTS_GRATUITS = "rco_points_gratuits";

/** Les présomptions que chaque dispositif pour enfants applique dans le code. */
export const PRESOMPTIONS_ENFANTS = {
  mda: ["pas_d_accord_des_parents", "enfant_eleve_neuf_ans"],
  bonifications: ["interruption_d_activite_par_la_mere"],
};

/**
 * Le relevé des droits d'une demande : ce que chaque étape a écrit, et les
 * régimes que la coordination fait liquider ensemble.
 */
export class Releve {
  constructor(coordination, durees, droits, groupes, servicesLus = new Set()) {
    this.coordination = coordination;
    this.durees = durees;
    this.droits = droits;
    /** Pour chaque régime d'un groupe d'au moins deux, ses membres, le liquidateur en tête. */
    this.groupes = groupes;
    /** Les régimes dont la liquidation lit les services : seules leurs lignes se publient. */
    this.servicesLus = servicesLus;
  }

  /** La carrière que la liquidation lit, rétablissement fait. */
  get carriere() {
    return this.coordination.carriere;
  }

  /** Le relevé, tel que l'enveloppe du contrat C.5 le décrit. */
  donnees() {
    const groupes = [];
    const vus = new Set();
    for (const membres of this.groupes.values()) {
      const cle = membres.join(",");
      if (!vus.has(cle)) {
        vus.add(cle);
        groupes.push({ regimes: [...membres] });
      }
    }
    return {
      schema_version: SCHEMA_VERSION,
      personne: this.carriere.personne,
      date: dateDEffet(this.carriere),
      lignes: this.lignes(),
      groupes,
    };
  }

  /**
   * Les lignes du relevé (contrat C.5), dans l'ordre des étapes : les durées,
   * compte par compte ; les trimestres des enfants ; les points ; les
   * cotisations ; les points gratuits. Voir `Releve.lignes` dans le Python.
   */
  lignes() {
    const carriere = this.carriere;
    const faits = new Faits(carriere);
    const lignes = [];
    const cotisees = new Set();
    const retablies = new Set();
    carriere.lignes.forEach((ligne, i) => {
      for (const code of this.coordination.regimes[i]) {
        if (ligne.cotise) {
          cotisees.add(`${code}|${ligne.annee}`);
        }
        if (ligne.revenu_retabli > 0) {
          retablies.add(`${code}|${ligne.annee}`);
        }
      }
    });
    for (const compte of compterEtape.COMPTES) {
      for (const [code, annees] of this.durees.parAnnee[compte]) {
        if (compte === "services" && !this.servicesLus.has(code)) {
          continue;
        }
        for (const [annee, trimestres] of annees) {
          const fait = faits.deLAnnee(annee, code, this.coordination);
          let fiche = null;
          if (compte === "services") {
            fiche = FICHE_SERVICES;
          } else if (retablies.has(`${code}|${annee}`)) {
            fiche = FICHE_RETABLISSEMENT;
          }
          lignes.push(ligneDuReleve(
            `${compte}_${code}_${annee}`, carriere.personne, fait,
            `${String(annee).padStart(4, "0")}-01-01`,
            { quantite: trimestres, unite: "trimestre", regime: code, compte },
            {
              fiche,
              contributive: cotisees.has(`${code}|${annee}`),
              origine: faits.observe(fait) ? "observee" : "calculee",
              presomptions: faits.presomptions(fait),
              fiabilite: faits.fiabilite(fait),
            },
          ));
        }
      }
    }
    const enfants = this.durees.enfants;
    if (enfants !== null && carriere.nombre_enfants > 0) {
      const parEnfant = {
        assurance: Math.floor(enfants.trimestres / carriere.nombre_enfants),
        services: Math.floor(enfants.services / carriere.nombre_enfants),
      };
      for (let rang = 1; rang <= carriere.nombre_enfants; rang += 1) {
        const naissance = faits.naissance(`enfant_${rang}`);
        const presomptions = [
          ...(naissance && naissance.presomption ? [naissance.presomption] : []),
          ...(PRESOMPTIONS_ENFANTS[enfants.dispositif] ?? []),
        ].sort();
        for (const [compte, trimestres] of Object.entries(parEnfant)) {
          if (trimestres <= 0 || (compte === "services" && !this.servicesLus.has(enfants.regime))) {
            continue;
          }
          lignes.push(ligneDuReleve(
            `enfants_${compte}_${enfants.regime}_${rang}`, carriere.personne,
            naissance ? naissance.id : null, naissance ? naissance.debut : null,
            { quantite: trimestres, unite: "trimestre", regime: enfants.regime, compte },
            {
              fiche: FICHE_ENFANTS, contributive: false, presomptions,
              fiabilite: nomFiabilite(enfants.fiabilite),
            },
          ));
        }
      }
    }
    const droits = this.droits;
    const vus = new Map();
    const identifiant = (cle) => {
      vus.set(cle, (vus.get(cle) ?? 0) + 1);
      return vus.get(cle) === 1 ? cle : `${cle}_${vus.get(cle)}`;
    };
    for (const [code, annee, points] of droits.points) {
      lignes.push(ligneDuReleve(
        identifiant(`points_${code}_${annee}`), carriere.personne,
        faits.deLAnnee(annee, code, this.coordination),
        `${String(annee).padStart(4, "0")}-01-01`,
        { quantite: points, unite: "point", regime: code },
        { fiabilite: nomFiabilite(droits.fiabilitePoints.get(code)) },
      ));
    }
    for (const [code, annee, montant] of droits.cotisations) {
      lignes.push(ligneDuReleve(
        identifiant(`cotisations_${code}_${annee}`), carriere.personne,
        faits.deLAnnee(annee, code, this.coordination),
        `${String(annee).padStart(4, "0")}-01-01`,
        { quantite: montant, unite: "euro", regime: code },
        { face: "cotisation" },
      ));
    }
    const date = dateDEffet(carriere);
    for (const [code, [points]] of droits.gratuits) {
      lignes.push(ligneDuReleve(
        `gratuits_${code}`, carriere.personne, faits.depart(), date,
        { quantite: points, unite: "point", regime: code },
        {
          fiche: FICHE_POINTS_GRATUITS, contributive: false,
          fiabilite: nomFiabilite(droits.fiabilitePoints.get(code)),
        },
      ));
    }
    return lignes;
  }
}

/**
 * Le relevé des droits que la demande portée par `carriere` fait valoir. Les
 * trois drapeaux sont ceux de `ScenarioActuel.calculer`. Voir `construire`
 * dans le Python.
 */
export function construire(moteur, carriere, {
  avantagesNonContributifs = true, pointsGratuits = true, liquiderSuccessions = true,
} = {}) {
  const coordination = coordonnerEtape.coordonner(moteur, carriere);
  const durees = compterEtape.compter(moteur, coordination, avantagesNonContributifs);
  const droits = acquerirEtape.acquerir(moteur, coordination, durees, pointsGratuits);
  // Un régime et celui qui lui succède liquident ensemble, sous les règles de
  // la caisse qui aurait le dossier : les autres membres du groupe sont sautés
  // partout où un régime liquide.
  const groupes = liquiderSuccessions
    ? coordonnerEtape.groupesDeSuccession(
      moteur, droits.codes, coordination.carriere.anneeLiquidation,
      droits.derniereAnneeParRegime, coordination.carriere,
    )
    : new Map();
  const servicesLus = new Set([...durees.parAnnee.services.keys()].filter(
    (code) => moteur.catalogue.obtenir(code).famille === "fonction_publique",
  ));
  return new Releve(coordination, durees, droits, groupes, servicesLus);
}

/**
 * Une ligne du contrat C.5. Ce qui n'est pas encore su — la version de la
 * fiche, le texte appliqué, une fiche que la règle n'a pas encore — n'y figure
 * pas : c'est un manque, pas une erreur.
 */
function ligneDuReleve(ident, personne, fait, date, droit, {
  fiche = null, face = "droit", contributive = true, origine = "calculee",
  presomptions = [], fiabilite = null,
} = {}) {
  const ligne = { schema_version: SCHEMA_VERSION, id: ident, personne };
  if (fait !== null) {
    ligne.fait = fait;
  }
  if (date !== null) {
    ligne.date = date;
  }
  if (fiche !== null) {
    ligne.fiche = fiche;
  }
  Object.assign(ligne, {
    droit, face, contributive, nature: "ferme", origine, presomptions: presomptions ?? [],
  });
  if (fiabilite !== null && fiabilite !== undefined) {
    ligne.fiabilite = fiabilite;
  }
  return ligne;
}

/** Les faits de la chronologie qu'une ligne du relevé cite. */
class Faits {
  constructor(carriere) {
    const chronologie = carriere.chronologie ?? { faits: [] };
    this.personne = carriere.personne;
    this.parId = new Map((chronologie.faits ?? []).map((f) => [f.id, f]));
    this.periodes = chrono.faitsDe(chronologie, carriere.personne)
      .filter((f) => f.sorte === chrono.EMPLOI || f.sorte === chrono.INTERRUPTION);
    this.naissances = new Map();
    for (const f of chronologie.faits ?? []) {
      if (f.sorte === "naissance") {
        this.naissances.set(f.personne, f);
      }
    }
  }

  /**
   * Le fait qui ouvre ce que `code` reçoit en `annee` : la période qui couvre
   * l'année sous un statut que la coordination y route — une interruption,
   * quand l'année en est une —, la première dans l'ordre de la chronologie.
   */
  deLAnnee(annee, code, coordination) {
    const debut = `${String(annee).padStart(4, "0")}-01-01`;
    const fin = `${String(annee + 1).padStart(4, "0")}-01-01`;
    const statuts = new Set();
    coordination.carriere.lignes.forEach((ligne, i) => {
      if (ligne.annee === annee && coordination.regimes[i].includes(code)) {
        statuts.add(ligne.affiliation);
      }
    });
    const couvrent = this.periodes.filter(
      (f) => f.debut < fin && (f.fin === null || f.fin === undefined || f.fin > debut),
    );
    for (const f of couvrent) {
      if (f.sorte === chrono.INTERRUPTION && !("affiliation" in f.attributs)) {
        return f.id;
      }
    }
    for (const f of couvrent) {
      if (statuts.has(f.attributs.affiliation)) {
        return f.id;
      }
    }
    return null;
  }

  /** Un fait d'un relevé de carrière déposé fait foi : ses trimestres sont observés. */
  observe(fait) {
    return fait !== null && fait.startsWith("releve_");
  }

  presomptions(fait) {
    const element = fait ? this.parId.get(fait) : undefined;
    return element && element.presomption ? [element.presomption] : [];
  }

  fiabilite(fait) {
    const element = fait ? this.parId.get(fait) : undefined;
    return element ? (element.fiabilite ?? null) : null;
  }

  naissance(personne) {
    return this.naissances.get(personne) ?? null;
  }

  depart() {
    const fait = `depart_${this.personne}`;
    return this.parId.has(fait) ? fait : null;
  }
}
