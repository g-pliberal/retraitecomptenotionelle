/**
 * Le relevé des droits (docs/architecture.md, § 7.2 et 7.6).
 *
 * Jumeau de `src/retraite_notionnelle/droit/releve.py` : `construire` enchaîne
 * les étapes de l'acquisition — coordonner les affiliations, compter les
 * durées, acquérir les droits —, puis réunit en groupes les régimes où un
 * droit est acquis ; la liquidation du scénario 1 lit ce qu'il rend. Le relevé
 * se publie en lignes, que le contrat C.5 décrit : `Releve.lignes`. Lu à
 * rebours, il dit le revenu que des points supposent : `revenuDesPoints`.
 */

import { Carriere } from "../carriere.js";
import * as chrono from "../chronologie.js";
import { nomFiabilite } from "../serie.js";
import * as acquerirEtape from "./acquerir.js";
import { dateDEffet, ligneCotisee } from "./commun.js";
import * as compterEtape from "./compter.js";
import * as coordonnerEtape from "./coordonner.js";
import { indemnisationBornee } from "./ouvrir.js";

/** La version du contrat C.5 que les lignes et l'enveloppe suivent. */
export const SCHEMA_VERSION = 1;

/** Les fiches de la carte que certaines lignes appliquent. */
export const FICHE_RETABLISSEMENT = "retablissement_fonction_publique";
export const FICHE_SERVICES = "services_et_duree_fonction_publique";
export const FICHE_POINTS_GRATUITS = "rco_points_gratuits";

/** Les présomptions que chaque dispositif pour enfants applique dans le code. */
export const PRESOMPTIONS_ENFANTS = {
  mda: ["pas_d_accord_des_parents", "enfant_eleve_neuf_ans"],
  bonifications: ["interruption_d_activite_par_la_mere"],
  enfants_sncf: [],
  enfants_ratp: ["interruption_d_activite_par_la_mere"],
  enfants_ieg: ["interruption_d_activite_par_la_mere"],
  enfants_crpcen: ["interruption_d_activite_par_la_mere"],
};

/**
 * Le relevé des droits d'une demande : ce que chaque étape a écrit, et les
 * régimes que la coordination fait liquider ensemble.
 */
export class Releve {
  constructor(coordination, durees, droits, groupes, servicesLus = new Set(),
    gratuites = new Set()) {
    this.coordination = coordination;
    this.durees = durees;
    this.droits = droits;
    /** Pour chaque régime d'un groupe d'au moins deux, ses membres, le liquidateur en tête. */
    this.groupes = groupes;
    /** Les régimes dont la liquidation lit les services : seules leurs lignes se publient. */
    this.servicesLus = servicesLus;
    /**
     * Les années d'emploi que leur régime valide sans cotisation, « régime|année » :
     * l'activité cultuelle d'avant 1979 (`ligneCotisee`). Leurs lignes ne sont pas
     * contributives.
     */
    this.gratuites = gratuites;
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
        if (ligne.cotise && !this.gratuites.has(`${code}|${ligne.annee}`)) {
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
    for (const ouvre of enfants !== null ? enfants.enfants : []) {
      const naissance = faits.naissance(ouvre.enfant);
      const rang = ouvre.enfant.slice(ouvre.enfant.lastIndexOf("_") + 1);
      const presomptions = [
        ...(naissance && naissance.presomption ? [naissance.presomption] : []),
        ...(PRESOMPTIONS_ENFANTS[ouvre.dispositif] ?? []),
      ].sort();
      for (const [compte, trimestres] of [["assurance", ouvre.trimestres],
        ["services", ouvre.services]]) {
        if (trimestres <= 0 || (compte === "services" && !this.servicesLus.has(ouvre.regime))) {
          continue;
        }
        lignes.push(ligneDuReleve(
          `enfants_${compte}_${ouvre.regime}_${rang}`, carriere.personne,
          naissance ? naissance.id : null, naissance ? naissance.debut : null,
          { quantite: trimestres, unite: "trimestre", regime: ouvre.regime, compte },
          {
            fiche: ouvre.fiche, version: ouvre.version, texte: ouvre.texte,
            contributive: false, presomptions, fiabilite: nomFiabilite(ouvre.fiabilite),
          },
        ));
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
export function construire(moteur, carriereSaisie, {
  avantagesNonContributifs = true, pointsGratuits = true, liquiderSuccessions = true,
} = {}) {
  // Le chômage que le relevé lit cesse d'être indemnisé au taux plein.
  const carriere = indemnisationBornee(moteur, carriereSaisie);
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
  const gratuites = new Set();
  coordination.carriere.lignes.forEach((ligne, i) => {
    if (ligne.cotise && !ligneCotisee(moteur, coordination.carriere, ligne)) {
      for (const code of coordination.regimes[i]) {
        gratuites.add(`${code}|${ligne.annee}`);
      }
    }
  });
  return new Releve(coordination, durees, droits, groupes, servicesLus, gratuites);
}

// -- Le relevé à rebours : le revenu que des points supposent ----------------
//
// Voir le Python, qui dit pourquoi : un relevé de carrière chiffre en points,
// non en euros, les années d'un régime qui compte en points, et celles que
// seule la complémentaire chiffre. Le revenu rendu est le plus bas, en euros
// entiers, dont une année du statut crédite au moins ces points dans les
// régimes de l'étage, cherché par dichotomie sur le relevé des droits
// lui-même ; `null` quand les points ne disent aucun revenu.

/** Les étages dont les points disent un revenu. */
export const ETAGES_CONVERTIS = ["base", "complementaire"];

/** L'assuré fictif qui cotise l'année : quarante ans, parti à soixante-sept. */
export const AGE_DANS_L_ANNEE = 40;
export const AGE_DE_DEPART_FICTIF = 67.0;

/** La borne haute de la recherche, en plafonds de la Sécurité sociale. */
export const PLAFONDS_AU_PLUS = 16;

/** Ce dont des points lus peuvent dépasser le plus haut du barème. */
export const DEMI_POINT = 0.5;

/** Le bruit du calcul en virgule flottante, en points. */
export const EPSILON_POINTS = 1e-6;

/**
 * Les points qu'une année de `statut`, au revenu `revenu`, ouvre dans les
 * régimes de cet étage que le statut cotise cette année-là — les siens, et non
 * ceux où la coordination route une carrière d'un an.
 */
export function pointsDeLAnnee(moteur, statut, annee, etage, revenu, trimestres = null) {
  const regimes = new Set(moteur.affiliations.regimes(statut, annee).filter(
    (code) => moteur.catalogue.contient(code)
      && moteur.catalogue.obtenir(code).etage === etage,
  ));
  if (regimes.size === 0) {
    return 0.0;
  }
  const carriere = Carriere.depuisReleve({
    annee_naissance: annee - AGE_DANS_L_ANNEE,
    sexe: "H",
    releve: [{ annee, affiliation: statut, revenu, trimestres, type_periode: "emploi" }],
    age_liquidation: AGE_DE_DEPART_FICTIF,
    macro: moteur.macro,
    identifiant: `points de ${annee}`,
  });
  const releve = construire(moteur, carriere, {
    avantagesNonContributifs: false, pointsGratuits: false, liquiderSuccessions: false,
  });
  let somme = 0.0;
  for (const [code, an, points] of releve.droits.points) {
    if (an === annee && regimes.has(code)) {
      somme += points;
    }
  }
  return somme;
}

/**
 * Le revenu entier le plus bas dont une année de `statut` ouvre au moins
 * `points` dans les régimes de l'étage `etage`, et s'il est au plafond du
 * barème : `{ revenu, auPlafond }`, ou `null` quand ces points ne disent aucun
 * revenu.
 */
export function revenuDesPoints(moteur, statut, annee, etage, points, trimestres = null) {
  if (!ETAGES_CONVERTIS.includes(etage) || !(points > 0)) {
    return null;
  }
  let haut = Math.ceil(PLAFONDS_AU_PLUS * moteur.macro.plafond_securite_sociale.valeur(annee));
  if (!(haut >= 2)) {
    return null;
  }
  const vus = new Map();
  const acquis = (revenu) => {
    if (!vus.has(revenu)) {
      vus.set(revenu, pointsDeLAnnee(moteur, statut, annee, etage, revenu, trimestres));
    }
    return vus.get(revenu);
  };
  // Le plus petit revenu qui cotise ouvre déjà le plancher : des points qui ne
  // le dépassent pas ne disent pas le revenu, ni ceux d'un barème que le
  // revenu ne fait pas bouger.
  const plancher = acquis(1);
  const plusHaut = acquis(haut);
  if (plusHaut <= plancher + EPSILON_POINTS || points <= plancher + EPSILON_POINTS
      || points > plusHaut + DEMI_POINT) {
    return null;
  }
  const cible = Math.min(points, plusHaut) - EPSILON_POINTS;
  let bas = 1;
  while (haut - bas > 1) {
    const milieu = Math.floor((bas + haut) / 2);
    if (acquis(milieu) >= cible) {
      haut = milieu;
    } else {
      bas = milieu;
    }
  }
  return { revenu: haut, auPlafond: plusHaut <= acquis(haut) + EPSILON_POINTS };
}

/**
 * Une ligne du contrat C.5. Ce qui n'est pas encore su — la version de la
 * fiche, le texte appliqué, une fiche que la règle n'a pas encore — n'y figure
 * pas : c'est un manque, pas une erreur.
 */
function ligneDuReleve(ident, personne, fait, date, droit, {
  fiche = null, version = null, texte = null, face = "droit", contributive = true,
  origine = "calculee", presomptions = [], fiabilite = null,
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
  if (version !== null) {
    ligne.version = version;
  }
  if (texte !== null) {
    ligne.texte = texte;
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
