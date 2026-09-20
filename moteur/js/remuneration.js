/**
 * La fiche de paie : coût du travail, revenu brut, revenu net.
 *
 * Portage de ``src/retraite_notionnelle/remuneration.py``, dont il reproduit
 * les conventions au centime — les témoins de `tests/temoins/` le vérifient.
 * Le docstring du module Python porte le raisonnement complet ; ce qui suit
 * n'en garde que ce qu'il faut pour lire le code.
 *
 *     coût du travail = brut + cotisations patronales − réduction générale
 *     revenu net      = brut − cotisations salariales − CSG − CRDS
 *
 * QUATRE CHOSES À SAVOIR AVANT DE MODIFIER QUOI QUE CE SOIT ICI.
 *
 * 1. **L'incidence est intégrale quand l'employeur est connu.** Le coût du
 *    travail est tenu fixe, et le brut est celui qui l'épuise sous les
 *    nouveaux taux : ce que l'employeur ne verse plus en cotisations, il le
 *    verse en salaire. Quand il ne l'est pas — ou qu'il n'y en a pas —, c'est
 *    l'ASSIETTE qui est tenue fixe, et seule la part de l'assuré bouge.
 * 2. **Le partage salarial/patronal du taux unique n'est pas neutre**, bien
 *    qu'on l'attende. La CSG est assise sur le BRUT, que le partage déplace ;
 *    et la réduction générale n'efface que des cotisations patronales.
 * 3. **La réduction générale est recalculée**, pas figée. Son coefficient
 *    maximal est la somme des taux de son périmètre ; un scénario qui baisse la
 *    cotisation retraite patronale la baisse aussi. Au SMIC, où elle efface
 *    tout, baisser cette cotisation ne rend donc rien.
 * 4. **Quatre profils, et le découpage n'est pas celui des familles de
 *    statut** : c'est celui de ce que l'on sait de l'employeur. `salarie_prive`,
 *    `salarie_ircantec`, `agent_seul` — la fiche du régime ne porte que la
 *    retenue de l'agent, parce que ce que verse son employeur est un taux
 *    d'ÉQUILIBRE et non un prix du travail — et `independant`, qui n'a pas
 *    d'employeur du tout. Voir `profilDeLaFiche`.
 */

import { tauxCapitalisationVolontaireApplique } from "./config.js";
import { Fiabilite } from "./serie.js";

/** Heures d'un temps plein sur une année : 35 heures sur 52 semaines. */
export const HEURES_ANNUELLES_TEMPS_PLEIN = 1820.0;

/**
 * Familles de statuts dont ce module sait écrire la fiche de paie.
 *
 * Restent dehors `agricole` — la MSA a ses propres taux hors retraite —,
 * `outre_mer`, dont chaque collectivité a sa caisse, `elus`, dont l'indemnité
 * de fonction n'est pas un salaire, et `hors_emploi`, qui ne cotise pas.
 */
export const FAMILLES_COUVERTES = Object.freeze([
  "prive", "public", "special", "independant",
]);

/** Ce que le modèle tient FIXE quand il compare deux systèmes. */
export const Incidence = Object.freeze({
  COUT_DU_TRAVAIL: "cout_du_travail",
  ASSIETTE: "assiette",
});

/**
 * Somme des taux appliqués segment par segment à une assiette.
 *
 * Les segments peuvent se RECOUVRIR, et c'est voulu : la cotisation vieillesse
 * déplafonnée porte sur la totalité du salaire par-dessus la plafonnée.
 */
function montant(segments, assiette, plafondAnnuel) {
  let total = 0;
  for (const segment of segments) {
    if (segment.taux === 0) {
      continue;
    }
    const bas = segment.bas * plafondAnnuel;
    const haut = segment.haut === null
      ? assiette
      : Math.min(assiette, segment.haut * plafondAnnuel);
    if (haut > bas) {
      total += (haut - bas) * segment.taux;
    }
  }
  return total;
}

/**
 * Un taux qui dépend du NIVEAU de l'assiette, et porte sur sa totalité.
 *
 * C'est la forme qu'a prise la loi pour les indépendants, et elle n'est pas
 * celle d'un barème par tranches : « le taux de base […] fait l'objet d'une
 * réduction lorsque le montant annuel de leur assiette de cotisations est
 * inférieur à trois fois la valeur annuelle du plafond » (D. 621-2). Le taux
 * réduit s'applique alors à TOUT le revenu ; entre deux paliers il est
 * interpolé linéairement, et au-delà de `jusqu_en_plafonds` ce sont les
 * tranches du poste qui reprennent la main.
 */
function tauxProgressif(bareme, assietteEnPlafonds) {
  const paliers = bareme.paliers;
  if (!paliers.length) {
    return 0;
  }
  if (assietteEnPlafonds <= paliers[0].en_plafonds) {
    return paliers[0].taux;
  }
  let precedent = paliers[0];
  for (const palier of paliers.slice(1)) {
    if (assietteEnPlafonds <= palier.en_plafonds) {
      const largeur = palier.en_plafonds - precedent.en_plafonds;
      if (largeur <= 0) {
        return palier.taux;
      }
      const part = (assietteEnPlafonds - precedent.en_plafonds) / largeur;
      return precedent.taux + part * (palier.taux - precedent.taux);
    }
    precedent = palier;
  }
  return precedent.taux;
}

/** Ce que l'assuré supporte au titre d'un poste, barème progressif compris. */
function montantSalarie(poste, assiette, plafondAnnuel) {
  const bareme = poste.progressif;
  if (bareme && assiette < bareme.jusqu_en_plafonds * plafondAnnuel) {
    return tauxProgressif(bareme, assiette / plafondAnnuel) * assiette;
  }
  return montant(poste.salarie, assiette, plafondAnnuel);
}

/** La réduction générale dégressive unique, et de quoi la recalculer. */
export class ReductionGenerale {
  constructor(fiche) {
    Object.assign(this, fiche);
  }

  /** Points de cotisation retraite patronale compris dans le coefficient. */
  get tauxRetraiteInclus() {
    return this.composantes_retraite.reduce(
      (total, code) => total + this.composantes[code], 0,
    );
  }

  /**
   * Le coefficient maximal quand la retraite patronale change de taux.
   *
   * « La valeur maximale du coefficient est fixée par décret, dans la limite
   * de la somme des taux des cotisations et contributions incluses dans le
   * périmètre de la réduction » (L. 241-13, III) : on retire la retraite
   * d'aujourd'hui, on ajoute celle du scénario.
   */
  coefficientMaximalAvec(tauxRetraiteEmployeur) {
    return Math.max(
      this.taux_minimum,
      this.coefficient_maximal - this.tauxRetraiteInclus + tauxRetraiteEmployeur,
    );
  }

  coefficient(brut, smicAnnuel, tauxRetraiteEmployeur) {
    if (brut <= 0 || smicAnnuel <= 0) {
      return 0;
    }
    if (brut >= this.plafond_en_smic * smicAnnuel) {
      return 0;
    }
    const maximal = this.coefficientMaximalAvec(tauxRetraiteEmployeur);
    const delta = maximal - this.taux_minimum;
    const rapport = Math.max(
      0, 0.5 * ((this.plafond_en_smic * smicAnnuel) / brut - 1),
    );
    const arrondi = Math.round(delta * rapport ** this.puissance * 1e4) / 1e4;
    return Math.min(maximal, this.taux_minimum + arrondi);
  }
}

/**
 * Tout ce que le droit prélève sur un revenu, hors retraite acquisitive, pour
 * une situation d'employeur donnée.
 *
 * `reduction_generale` est `null` quand l'employeur n'y a pas droit — ou qu'il
 * n'y en a pas.
 */
export class ProfilRemuneration {
  constructor(fiche) {
    this.code = fiche.code;
    this.libelle = fiche.libelle;
    this.libelle_assiette = fiche.libelle_assiette;
    this.libelle_net = fiche.libelle_net;
    this.cout_du_travail = fiche.cout_du_travail;
    this.incidence = fiche.incidence;
    this.annee = fiche.annee;
    this.fiabilite = fiche.fiabilite;
    this.csg_deductible = fiche.csg_deductible;
    this.csg_imposable = fiche.csg_imposable;
    this.crds = fiche.crds;
    this.abattement_frais = fiche.abattement_frais;
    this.postes = fiche.postes;
    this.reduction_generale = fiche.reduction_generale
      ? new ReductionGenerale(fiche.reduction_generale) : null;
  }

  get csg() {
    return this.csg_deductible + this.csg_imposable;
  }

  /** Ce poste est-il dû à ce revenu, pour cet assuré ? */
  static du(poste, brut, plafondAnnuel, cadre) {
    if (poste.cadres_seulement && !cadre) {
      return false;
    }
    if (poste.due_au_dela_de_un_plafond && brut <= plafondAnnuel) {
      return false;
    }
    return true;
  }
}

/**
 * Ce qu'on paie une fois retraité — et non plus en travaillant.
 *
 * Une pension n'est pas un salaire : aucune cotisation sociale, puisqu'on
 * n'acquiert plus de droits ; aucun abattement pour frais professionnels ; et
 * un taux de CSG propre. **Le dépôt retient le TAUX PLEIN pour tout le monde**,
 * faute de connaître le revenu fiscal du foyer dont la loi le fait dépendre :
 * la convention surestime donc le prélèvement sur les petites pensions, qui
 * seraient exonérées.
 */
export class PrelevementsPension {
  constructor(fiche) {
    this.csg_taux_plein = fiche.csg_taux_plein;
    this.crds = fiche.crds;
    this.casa = fiche.casa;
    this.bareme_csg = fiche.bareme_csg;
  }

  /** Ce qui sépare une pension brute de sa nette : 9,1 %. */
  get tauxTotal() {
    return this.csg_taux_plein + this.crds + this.casa;
  }

  net(brut) {
    return brut * (1 - this.tauxTotal);
  }

  /** L'inverse, pour la saisie : quelle pension brute laisse ce net. */
  brut(net) {
    const reste = 1 - this.tauxTotal;
    return reste > 0 ? net / reste : net;
  }
}

/** Les quatre profils, tels que le paquet de données les porte, et les pensions. */
export class BaremePrelevements {
  constructor(paquet) {
    this.annee = paquet.annee;
    this.fiabilite = paquet.fiabilite;
    this.profils = new Map(
      Object.entries(paquet.profils).map(
        ([code, fiche]) => [code, new ProfilRemuneration(fiche)],
      ),
    );
    this.pensions = new PrelevementsPension(paquet.pensions);
  }

  profil(code) {
    return this.profils.get(code);
  }
}

/**
 * Un étage du financement de la retraite, avec ses deux barèmes.
 *
 * `dansLaReductionGenerale` est vrai de la vieillesse de base et de la
 * complémentaire légalement obligatoire, que le I de l'article L. 241-13 nomme
 * l'une et l'autre ; faux du pilier capitalisé de la proposition, qui n'est ni
 * l'une ni l'autre.
 */
export class ComposanteRetraite {
  constructor({ code, libelle, salarie, employeur, dansLaReductionGenerale = true }) {
    this.code = code;
    this.libelle = libelle;
    this.salarie = salarie;
    this.employeur = employeur;
    this.dansLaReductionGenerale = dansLaReductionGenerale;
  }

  /** Taux patronal sur la première tranche — celui qu'un décret additionne. */
  tauxEmployeurPremiereTranche() {
    return this.employeur
      .filter((s) => s.bas < 1)
      .reduce((total, s) => total + s.taux, 0);
  }
}

/** Ce qu'un système prélève pour la retraite, étage par étage. */
export class BlocRetraite {
  constructor({ libelle, composantes, remplaceLesContributionsDEquilibre = false }) {
    this.libelle = libelle;
    this.composantes = composantes;
    this.remplaceLesContributionsDEquilibre = remplaceLesContributionsDEquilibre;
  }

  /**
   * Points de retraite patronale que le coefficient maximal doit compter : les
   * étages de ce bloc qui sont dans le périmètre, plus les contributions
   * d'équilibre du barème quand le système les conserve.
   */
  tauxEmployeurDansLaReduction(profil) {
    let total = this.composantes
      .filter((c) => c.dansLaReductionGenerale)
      .reduce((somme, c) => somme + c.tauxEmployeurPremiereTranche(), 0);
    if (!this.remplaceLesContributionsDEquilibre) {
      for (const poste of profil.postes) {
        if (poste.retraite && poste.dans_la_reduction_generale) {
          total += poste.employeur
            .filter((s) => s.bas < 1)
            .reduce((somme, s) => somme + s.taux, 0);
        }
      }
    }
    return total;
  }
}

/** Une année de rémunération, décomposée. Montants ANNUELS, euros courants. */
export class FicheDePaie {
  constructor(fiche) {
    Object.assign(this, fiche);
  }

  get cotisationsSalariales() {
    return this.brut - this.net;
  }

  get cotisationsPatronales() {
    return this.coutDuTravail - this.brut;
  }

  get retraiteSalarie() {
    return this.lignes.filter((l) => l.retraite)
      .reduce((total, l) => total + l.salarie, 0);
  }

  get retraiteEmployeur() {
    return this.lignes.filter((l) => l.retraite)
      .reduce((total, l) => total + l.employeur, 0);
  }

  /**
   * Ce qui est prélevé pour la retraite, les deux parts réunies, NET de la
   * réduction générale : au voisinage du SMIC, l'employeur ne verse pas ce que
   * le barème affiche.
   */
  get retraiteTotale() {
    const impute = this.reductionGenerale * this.partRetraiteDansLaReduction;
    return Math.max(0, this.retraiteSalarie + this.retraiteEmployeur - impute);
  }

  get tauxRetraite() {
    return this.coutDuTravail ? this.retraiteTotale / this.coutDuTravail : 0;
  }

  get ecartBrutNet() {
    return this.brut ? this.cotisationsSalariales / this.brut : 0;
  }

  /** Ce que le salarié touche, rapporté à ce que son emploi coûte. */
  get partQuiArrive() {
    return this.coutDuTravail ? this.net / this.coutDuTravail : 0;
  }
}

/** Construit une fiche de paie sous un bloc retraite donné, pour un profil. */
export class ConstructeurFiche {
  constructor(profil) {
    this.profil = profil;
  }

  _lignes(bloc, brut, plafond, cadre) {
    const lignes = bloc.composantes.map((composante) => ({
      code: composante.code,
      libelle: composante.libelle,
      retraite: true,
      salarie: montant(composante.salarie, brut, plafond),
      employeur: montant(composante.employeur, brut, plafond),
    }));
    for (const poste of this.profil.postes) {
      if (poste.retraite && bloc.remplaceLesContributionsDEquilibre) {
        continue;
      }
      if (!ProfilRemuneration.du(poste, brut, plafond, cadre)) {
        continue;
      }
      lignes.push({
        code: poste.code,
        libelle: poste.libelle,
        retraite: poste.retraite,
        salarie: montantSalarie(poste, brut, plafond),
        employeur: montant(poste.employeur, brut, plafond),
      });
    }
    const taux = this.profil.csg + this.profil.crds;
    if (taux > 0) {
      const abattement = montant(this.profil.abattement_frais, brut, plafond);
      lignes.push({
        code: "csg_crds", libelle: "CSG et CRDS", retraite: false,
        salarie: (brut - abattement) * taux, employeur: 0,
      });
    }
    return lignes;
  }

  /** Cotisations patronales que la réduction générale peut effacer. */
  _perimetreReduction(bloc, brut, plafond, cadre) {
    let total = bloc.composantes
      .filter((c) => c.dansLaReductionGenerale)
      .reduce((somme, c) => somme + montant(c.employeur, brut, plafond), 0);
    for (const poste of this.profil.postes) {
      if (!poste.dans_la_reduction_generale) {
        continue;
      }
      if (poste.retraite && bloc.remplaceLesContributionsDEquilibre) {
        continue;
      }
      if (!ProfilRemuneration.du(poste, brut, plafond, cadre)) {
        continue;
      }
      total += poste.taux_dans_la_reduction !== null
        && poste.taux_dans_la_reduction !== undefined
        ? brut * poste.taux_dans_la_reduction
        : montant(poste.employeur, brut, plafond);
    }
    return total;
  }

  _reduction(bloc, brut, plafond, smicAnnuel, cadre) {
    const reduction = this.profil.reduction_generale;
    if (reduction === null) {
      return 0;
    }
    const coefficient = reduction.coefficient(
      brut, smicAnnuel, bloc.tauxEmployeurDansLaReduction(this.profil),
    );
    if (coefficient <= 0) {
      return 0;
    }
    // Une réduction ne peut pas excéder ce qui est dû.
    return Math.min(
      coefficient * brut,
      this._perimetreReduction(bloc, brut, plafond, cadre),
    );
  }

  fiche(annee, brut, plafondAnnuel, smicAnnuel, bloc, cadre = false) {
    const lignes = this._lignes(bloc, brut, plafondAnnuel, cadre);
    const reduction = this._reduction(bloc, brut, plafondAnnuel, smicAnnuel, cadre);
    const salariales = lignes.reduce((total, l) => total + l.salarie, 0);
    const patronales = lignes.reduce((total, l) => total + l.employeur, 0);
    let partRetraite = 0;
    if (this.profil.reduction_generale !== null) {
      const tauxRetraite = bloc.tauxEmployeurDansLaReduction(this.profil);
      const maximal = this.profil.reduction_generale
        .coefficientMaximalAvec(tauxRetraite);
      partRetraite = maximal > 0 ? Math.min(1, tauxRetraite / maximal) : 0;
    }
    return new FicheDePaie({
      annee,
      coutDuTravail: brut + patronales - reduction,
      brut,
      net: brut - salariales,
      lignes,
      reductionGenerale: reduction,
      fiabilite: this.profil.fiabilite,
      partRetraiteDansLaReduction: partRetraite,
    });
  }

  /**
   * Le salaire brut qui épuise un coût du travail donné — l'incidence
   * intégrale. Le coût croît strictement avec le brut, si bien qu'une
   * dichotomie converge sans hypothèse supplémentaire.
   */
  brutACoutDonne(cout, plafondAnnuel, smicAnnuel, bloc, cadre = false) {
    if (cout <= 0) {
      return 0;
    }
    let bas = 0;
    let haut = cout;
    for (let pas = 0; pas < 80; pas += 1) {
      const milieu = (bas + haut) / 2;
      const fiche = this.fiche(0, milieu, plafondAnnuel, smicAnnuel, bloc, cadre);
      if (fiche.coutDuTravail < cout) {
        bas = milieu;
      } else {
        haut = milieu;
      }
    }
    return (bas + haut) / 2;
  }

  /**
   * Le revenu brut dont il reste `net` une fois tout retiré — l'inverse de la
   * fiche de paie, et il sert à la SAISIE : le lecteur qui connaît son net le
   * tape tel quel, et le modèle, qui ne raisonne qu'en brut, remonte jusqu'à
   * lui. Le net croît strictement avec le brut, donc une dichotomie suffit ;
   * la borne haute part de trois fois le net, aucun profil ne prélevant deux
   * tiers d'un revenu.
   */
  brutANetDonne(net, plafondAnnuel, smicAnnuel, bloc, cadre = false) {
    if (net <= 0) {
      return 0;
    }
    let bas = net;
    let haut = net * 3;
    for (let pas = 0; pas < 80; pas += 1) {
      const milieu = (bas + haut) / 2;
      const fiche = this.fiche(0, milieu, plafondAnnuel, smicAnnuel, bloc, cadre);
      if (fiche.net < net) {
        bas = milieu;
      } else {
        haut = milieu;
      }
    }
    return (bas + haut) / 2;
  }

  /**
   * Le brut à retenir sous le nouveau système, selon l'incidence du profil :
   * le coût du travail tenu fixe quand l'employeur est connu, l'assiette tenue
   * fixe quand il ne l'est pas. Une ligne, mais c'est là que se joue la
   * décision du module.
   */
  brutSousLaProposition(actuelle, plafondAnnuel, smicAnnuel, bloc, cadre = false) {
    if (this.profil.incidence === Incidence.ASSIETTE) {
      return actuelle.brut;
    }
    return this.brutACoutDonne(
      actuelle.coutDuTravail, plafondAnnuel, smicAnnuel, bloc, cadre,
    );
  }
}

// -- les blocs retraite des scénarios ---------------------------------------

/**
 * Ce que le droit en vigueur prélève pour la retraite, régime par régime.
 *
 * Construit depuis les FICHES DE RÉGIME : la fiche de paie prélève exactement
 * ce que le compte notionnel encaisse. Vaut pour les systèmes 1, 2 et 3, qui ne
 * changent pas ce qui est prélevé — seulement ce qui est porté au compte.
 */
export function blocDroitEnVigueur(catalogue, affiliations, statut, annee) {
  // Un non-salarié paie tout : la fiche d'un régime partagé avec des salariés
  // — un artisan relève du régime général — porte la répartition 45/55 d'un
  // salarié, et elle ne le concerne pas. `moteur/compte.js` en tire déjà la
  // même conséquence pour le compte notionnel.
  const sansEmployeur = affiliations.sansEmployeur(statut);
  const composantes = [];
  for (const code of affiliations.regimes(statut, annee)) {
    if (!catalogue.contient(code)) {
      continue;
    }
    const regime = catalogue.obtenir(code);
    if (regime.hors_repartition) {
      continue;
    }
    const salarie = [];
    const employeur = [];
    for (const periode of regime.periodesActives(annee)) {
      const [basse, haute] = periode.bornesAssietteEnPass();
      const part = sansEmployeur ? 1 : periode.part_salariale;
      const taux = periode.taux_cotisation_retraite;
      if (taux) {
        salarie.push({ bas: basse, haut: haute, taux: taux * part });
        employeur.push({ bas: basse, haut: haute, taux: taux * (1 - part) });
      }
      // La part déplafonnée porte sur la totalité du salaire, PAR-DESSUS la
      // précédente : c'est un segment de plus, non une tranche.
      const deplafonne = periode.taux_cotisation_deplafonnee;
      if (deplafonne) {
        const partDeplafonnee = sansEmployeur
          ? 1 : periode.part_salariale_deplafonnee;
        salarie.push({ bas: 0, haut: null, taux: deplafonne * partDeplafonnee });
        employeur.push({
          bas: 0, haut: null, taux: deplafonne * (1 - partDeplafonnee),
        });
      }
    }
    if (!salarie.length && !employeur.length) {
      continue;
    }
    composantes.push(new ComposanteRetraite({
      code, libelle: regime.nom, salarie, employeur,
      dansLaReductionGenerale: true,
    }));
  }
  return new BlocRetraite({
    libelle: "Retraite (droit en vigueur)",
    composantes,
    remplaceLesContributionsDEquilibre: false,
  });
}

/**
 * Le bloc de la proposition : un taux unique, au premier euro, sans plafond.
 *
 * Le pilier capitalisé est un étage à part, et hors du périmètre de la
 * réduction générale : il n'est ni une assurance sociale, ni un régime
 * complémentaire légalement obligatoire au sens de l'article L. 921-4.
 *
 * LES CINQ POINTS VOLONTAIRES N'Y SONT PAS. Le bloc ne porte que ce que la
 * proposition impose : une épargne que l'assuré décide seul n'est pas une
 * retenue sur salaire, et la mettre ici ferait baisser un net que la
 * proposition ne baisse pas. Elle est chiffrée à part, sur le net, par
 * `AnneeComparee.epargneVolontaire`.
 */
export function blocTauxUnique(tauxRepartition, tauxCapitalisation = 0,
  partSalariale = 0.5) {
  const composantes = [new ComposanteRetraite({
    code: "regime_unifie",
    libelle: "Retraite, compte notionnel",
    salarie: [{ bas: 0, haut: null, taux: tauxRepartition * partSalariale }],
    employeur: [{ bas: 0, haut: null, taux: tauxRepartition * (1 - partSalariale) }],
    dansLaReductionGenerale: true,
  })];
  if (tauxCapitalisation) {
    composantes.push(new ComposanteRetraite({
      code: "capitalisation",
      libelle: "Retraite, part capitalisée",
      salarie: [{ bas: 0, haut: null, taux: tauxCapitalisation * partSalariale }],
      employeur: [{
        bas: 0, haut: null, taux: tauxCapitalisation * (1 - partSalariale),
      }],
      dansLaReductionGenerale: false,
    }));
  }
  return new BlocRetraite({
    libelle: "Retraite (proposition)",
    composantes,
    remplaceLesContributionsDEquilibre: true,
  });
}

/**
 * Le bloc de la proposition pour qui n'a pas d'employeur : il porte les 18 %
 * en entier. La proposition additionne « salariale et patronale » ; un
 * indépendant est les deux à la fois, et lui prêter un employeur pour la
 * moitié de la charge fabriquerait un gain qui n'existe pas.
 */
export function blocTauxUniqueSansEmployeur(tauxRepartition, tauxCapitalisation = 0) {
  return blocTauxUnique(tauxRepartition, tauxCapitalisation, 1);
}

/** La fiche de paie sait-elle décrire ce statut ? */
export function ficheDePaiePossible(affiliations, statut) {
  try {
    return FAMILLES_COUVERTES.includes(affiliations.famille(statut));
  } catch {
    return false;
  }
}

/**
 * Le profil de fiche de paie d'un statut, ou `null` si aucun ne convient.
 *
 * Le découpage est celui de ce que l'on SAIT de l'employeur, et non celui des
 * familles de statut — parce que c'est cela qui décide si une ligne « coût du
 * travail » veut dire quelque chose :
 *
 * 1. pas d'employeur du tout → `independant` ;
 * 2. au moins un régime dont la fiche ne porte que la retenue de l'agent
 *    (`perimetre_taux === "agent_seul"`) → `agent_seul` : la part employeur
 *    existe, mais c'est un taux d'équilibre ;
 * 3. la famille `public` sans régime à retenue, c'est l'agent non titulaire
 *    → `salarie_ircantec`, qui ne doit ni CEG, ni CET, ni APEC ;
 * 4. le reste → `salarie_prive`, où tombent les statuts de la famille
 *    `special` que la fermeture des régimes spéciaux a versés au régime
 *    général et à l'Agirc-Arrco.
 */
export function profilDeLaFiche(affiliations, catalogue, statut, annee) {
  let famille;
  try {
    famille = affiliations.famille(statut);
  } catch {
    return null;
  }
  if (!FAMILLES_COUVERTES.includes(famille)) {
    return null;
  }
  if (famille === "independant" || affiliations.sansEmployeur(statut)) {
    return "independant";
  }
  for (const code of affiliations.regimes(statut, annee)) {
    if (!catalogue.contient(code)) {
      continue;
    }
    const regime = catalogue.obtenir(code);
    if (regime.hors_repartition) {
      continue;
    }
    for (const periode of regime.periodesActives(annee)) {
      if (periode.perimetre_taux === "agent_seul") {
        return "agent_seul";
      }
    }
  }
  return famille === "public" ? "salarie_ircantec" : "salarie_prive";
}

/** SMIC annuel d'un temps plein, en euros courants de l'année. */
export function smicAnnuel(macro, annee) {
  return macro.smic_horaire.valeur(annee) * HEURES_ANNUELLES_TEMPS_PLEIN;
}

// -- ce qu'un actif touche, système par système ------------------------------

//: Code de la ligne capitalisée de la fiche : celle que la proposition impose.
//: La volontaire n'a pas de ligne, elle n'est pas prélevée.
const CODE_CAPITALISATION = "capitalisation";

/**
 * Une année d'activité, sous le droit en vigueur et sous la proposition.
 * `tauxEpargneVolontaire` est le taux des cinq points rendus que le site
 * suppose placés : il n'est PAS dans `proposition`, la fiche s'arrête à ce que
 * la proposition impose, et ce placement se chiffre à côté, pris sur le net.
 */
export class AnneeComparee {
  constructor(fiche) {
    Object.assign(this, fiche);
  }

  get gainNet() {
    return this.proposition.net - this.droitEnVigueur.net;
  }

  get gainNetConstant() {
    return this.gainNet * this.coefficientEurosConstants;
  }

  /**
   * Le pilier capitalisé imposé : prélevé sur le net, mais acquis à l'assuré.
   * Compté à part du gain, parce que le confondre avec lui serait compter deux
   * fois, et le taire serait compter une fois de trop. Seule la cotisation
   * obligatoire y est : c'est la seule que la fiche prélève.
   */
  get epargneAVotreNom() {
    return this.proposition.lignes
      .filter((l) => l.code === CODE_CAPITALISATION)
      .reduce((total, l) => total + l.salarie + l.employeur, 0);
  }

  /**
   * Les cinq points rendus, si l'assuré les place : pris sur le net. Ce n'est
   * pas une ligne de la fiche, c'est un virement que l'assuré décide, chiffré
   * sur l'assiette de la proposition — la même que le pilier — et entièrement
   * à sa charge. Il ne touche ni au coût du travail, ni au brut, ni à la CSG.
   */
  get epargneVolontaire() {
    return this.proposition.brut * (this.tauxEpargneVolontaire ?? 0);
  }

  /** Ce qui reste du net PLEIN une fois les cinq points rendus placés. */
  get netApresVolontaire() {
    return this.proposition.net - this.epargneVolontaire;
  }

  /** Ce que la proposition ajoute au net de qui place les points rendus. */
  get gainNetApresVolontaire() {
    return this.netApresVolontaire - this.droitEnVigueur.net;
  }

  /**
   * L'incidence intégrale ferait-elle passer le brut sous le SMIC ? Le cas est
   * impossible en droit : le salaire minimum est un plancher.
   */
  get brutSousLeSmic() {
    return this.proposition.brut < this.droitEnVigueur.brut
      && this.proposition.brut < this.smic;
  }
}

/** Ce qu'un actif touche entre la bascule et son départ, dans les deux systèmes. */
export class RemunerationActif {
  constructor(fiche) {
    Object.assign(this, fiche);
  }

  get reference() {
    return this.annees[0];
  }

  get gainNetMensuel() {
    return this.reference.gainNet / 12;
  }

  get gainNetCumule() {
    return this.annees.reduce((total, a) => total + a.gainNetConstant, 0);
  }

  get epargneCumulee() {
    return this.annees.reduce(
      (total, a) => total + a.epargneAVotreNom * a.coefficientEurosConstants, 0,
    );
  }

  /** Les cinq points rendus de l'année de référence, par mois, s'ils sont placés. */
  get epargneVolontaireMensuelle() {
    return this.reference.epargneVolontaire / 12.0;
  }

  /** Ce que les seuls points rendus auront placé, en euros constants. */
  get epargneVolontaireCumulee() {
    return this.annees.reduce(
      (total, a) => total + a.epargneVolontaire * a.coefficientEurosConstants, 0,
    );
  }

  /** Le gain de net de qui place les points rendus, par mois. */
  get gainNetMensuelApresVolontaire() {
    return this.reference.gainNetApresVolontaire / 12.0;
  }

  /** Y a-t-il seulement des points rendus à montrer ? */
  get verseLeVolontaire() {
    return this.annees.some((a) => a.epargneVolontaire > 0);
  }

  get buteSurLeSmic() {
    return this.annees.some((a) => a.brutSousLeSmic);
  }
}

/**
 * Les fiches de paie d'une carrière, de la bascule au départ.
 *
 * `null` quand il n'y a rien à montrer : aucune année d'activité après la
 * bascule — la personne a déjà liquidé —, ou un statut que ce module ne sait
 * pas décrire.
 */
export function remunerationDeLaCarriere(carriere, macro, catalogue, affiliations,
  parametres, bareme) {
  const debut = Math.max(parametres.annee_bascule, carriere.premiereAnnee);
  const anneesActives = [];
  for (let annee = debut; annee <= carriere.anneeLiquidation; annee += 1) {
    const ligne = carriere.ligne(annee);
    if (ligne && ligne.cotise && ligne.revenu > 0) {
      anneesActives.push(annee);
    }
  }
  if (!anneesActives.length) {
    return null;
  }
  const statut = carriere.ligne(anneesActives[0]).affiliation;
  const codeProfil = profilDeLaFiche(
    affiliations, catalogue, statut, anneesActives[0],
  );
  if (codeProfil === null) {
    return null;
  }
  const profil = bareme.profil(codeProfil);

  const constructeur = new ConstructeurFiche(profil);
  // « Cadre » n'est pas une famille d'affiliation : c'est la seule chose qui
  // sépare deux statuts du privé pour la cotisation APEC, qui vaut 0,024 %.
  const cadre = statut.includes("cadre") && !statut.includes("non_cadre");
  const capitalisation = parametres.capitalisation_obligatoire
    ? parametres.taux_capitalisation_obligatoire : 0;
  // Les cinq points rendus ne sont pas dans le bloc : la fiche s'arrête à ce
  // que la proposition impose, et leur placement se chiffre sur chaque année,
  // pris sur le net.
  const volontaire = tauxCapitalisationVolontaireApplique(parametres);
  const propose = affiliations.sansEmployeur(statut)
    ? blocTauxUniqueSansEmployeur(
      parametres.taux_cotisation_liberal, capitalisation,
    )
    : blocTauxUnique(
      parametres.taux_cotisation_liberal, capitalisation,
      parametres.part_salariale_taux_unique,
    );

  const comparees = [];
  for (const annee of anneesActives) {
    const ligne = carriere.ligne(annee);
    const part = carriere.partRetenue(annee);
    if (part <= 0) {
      continue;
    }
    // Une année incomplète ne se compare pas à une année pleine : on annualise
    // le revenu, le plafond et le SMIC restant annuels.
    const brut = part < 1 ? ligne.revenu / part : ligne.revenu;
    const plafond = macro.plafond_securite_sociale.valeur(annee);
    const smic = smicAnnuel(macro, annee);
    const blocActuel = blocDroitEnVigueur(catalogue, affiliations, statut, annee);
    const ficheActuelle = constructeur.fiche(
      annee, brut, plafond, smic, blocActuel, cadre,
    );
    const brutPropose = constructeur.brutSousLaProposition(
      ficheActuelle, plafond, smic, propose, cadre,
    );
    comparees.push(new AnneeComparee({
      annee,
      droitEnVigueur: ficheActuelle,
      proposition: constructeur.fiche(
        annee, brutPropose, plafond, smic, propose, cadre,
      ),
      coefficientEurosConstants: macro.coefficientPrix(
        annee, parametres.annee_euros_constants,
      ),
      tauxEpargneVolontaire: volontaire,
      smic,
    }));
  }
  if (!comparees.length) {
    return null;
  }
  return new RemunerationActif({
    statut,
    libelleStatut: affiliations.libelle(statut),
    cadre,
    annees: comparees,
    millesimeBareme: profil.annee,
    fiabilite: profil.fiabilite,
    profil: profil.code,
    libelleProfil: profil.libelle,
    libelleAssiette: profil.libelle_assiette,
    libelleNet: profil.libelle_net,
    afficheCoutDuTravail: profil.cout_du_travail,
    incidence: profil.incidence,
  });
}

export { Fiabilite };


/**
 * Le revenu brut annuel dont il reste `netAnnuel` — ou lui-même.
 *
 * C'est l'entrée du mode « net » de la saisie. Rend le net INCHANGÉ quand le
 * statut n'a pas de fiche de paie — l'exploitant agricole, l'élu, l'outre-mer :
 * mieux vaut un brut approché par un net qu'un refus de calculer, et le site
 * dit alors qu'il n'a pas su convertir.
 */
export function salaireBrutDepuisNet(bareme, macro, catalogue, affiliations,
  statut, annee, netAnnuel) {
  if (netAnnuel <= 0) {
    return netAnnuel;
  }
  const codeProfil = profilDeLaFiche(affiliations, catalogue, statut, annee);
  if (codeProfil === null) {
    return netAnnuel;
  }
  const cadre = statut.includes("cadre") && !statut.includes("non_cadre");
  return new ConstructeurFiche(bareme.profil(codeProfil)).brutANetDonne(
    netAnnuel,
    macro.plafond_securite_sociale.valeur(annee),
    smicAnnuel(macro, annee),
    blocDroitEnVigueur(catalogue, affiliations, statut, annee),
    cadre,
  );
}

/**
 * Le sens direct : le revenu net annuel que laisse `brutAnnuel`, ou lui-même.
 * Sert à la BASCULE, qui doit traduire le nombre saisi et non le relire.
 */
export function salaireNetDepuisBrut(bareme, macro, catalogue, affiliations,
  statut, annee, brutAnnuel) {
  if (brutAnnuel <= 0) {
    return brutAnnuel;
  }
  const codeProfil = profilDeLaFiche(affiliations, catalogue, statut, annee);
  if (codeProfil === null) {
    return brutAnnuel;
  }
  const cadre = statut.includes("cadre") && !statut.includes("non_cadre");
  return new ConstructeurFiche(bareme.profil(codeProfil)).fiche(
    annee, brutAnnuel,
    macro.plafond_securite_sociale.valeur(annee),
    smicAnnuel(macro, annee),
    blocDroitEnVigueur(catalogue, affiliations, statut, annee),
    cadre,
  ).net;
}
