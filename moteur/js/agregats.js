/**
 * Ce que les trois pages qui agrègent lisent du modèle, fabriqué sous la
 * référence. Lecteur de `src/retraite_notionnelle/donnees/agregats.py`, dont il
 * garde les accesseurs.
 *
 * POURQUOI CE FICHIER EXISTE. Coût, Carrières types et Droits non cotisés
 * croisent treize carrières types avec sept générations, et chiffrent ce que
 * chaque système coûterait jusqu'en 2070. Elles se calculaient ici, chez le
 * lecteur, par le portage JavaScript du coût et sous les réglages de
 * l'adresse : de trois à huit secondes à la première visite. Elles ne montrent
 * plus que la référence depuis le 10 octobre 2026 (action 150), et ce qu'elles
 * lisent d'une règle du modèle vient de cette table, que
 * `scripts/construire_donnees.py` calcule une fois et que le paquet embarque
 * (`agregats`). Ce qui n'est qu'une donnée lue — les comptes du COR, les
 * dépenses publiées — reste où elle était.
 *
 * Le lecteur ne calcule rien qu'une règle décide : il rend ce que la table
 * porte, et lève une erreur sur ce qu'elle ne porte pas — une page qui lirait
 * un zéro à la place se tromperait sans bruit.
 */

/** `table[cle]`, ou une erreur qui dit ce que la table ne porte pas. */
function lire(table, cle, quoi) {
  if (!Object.prototype.hasOwnProperty.call(table, cle)) {
    throw new Error(`${quoi} absent de la table figée : ${cle}`);
  }
  return table[cle];
}

// -- les carrières types ------------------------------------------------------

/** D'une carrière simulée, ce que les pages en lisent : l'année du départ. */
class CarriereFigee {
  constructor(anneeLiquidation) {
    this.anneeLiquidation = anneeLiquidation;
  }
}

/** Une case de la grille : ce qu'en lisent les pages, sous les accesseurs de `Comparaison`. */
class ComparaisonFigee {
  constructor(brut) {
    this.carriere = new CarriereFigee(brut.annee_liquidation);
    this._carrieres = Object.fromEntries(Object.entries(brut.annees_liquidation)
      .map(([scenario, annee]) => [scenario, new CarriereFigee(annee)]));
    this._variations = brut.variations;
  }

  carriereDe(scenario) {
    return lire(this._carrieres, scenario, "carrière du scénario");
  }

  variationTotale(scenario) {
    return lire(this._variations, scenario, "écart du scénario");
  }
}

/** Un cas type, tel que les pages le nomment, et l'âge où chaque génération le fait partir. */
class CasFige {
  constructor(brut, generations) {
    this.code = brut.code;
    this.libelle = brut.libelle;
    this.commentaire = brut.commentaire;
    this._ages = Object.fromEntries(
      generations.map((generation, rang) => [generation, brut.ages[rang]]));
  }

  ageLiquidation(generation) {
    return lire(this._ages, generation, "âge de départ de la génération");
  }
}

/**
 * La grille cas type × génération, sous les accesseurs du résultat de la
 * grille — `resultats` et `echecs`, par « code|génération » —, et les cas qui
 * la composent.
 */
export class CasTypesFiges {
  constructor(brut) {
    this.generations = brut.generations;
    this.cas = brut.cas.map((cas) => new CasFige(cas, brut.generations));
    this.resultats = new Map(Object.entries(brut.resultats)
      .map(([cle, valeur]) => [cle, new ComparaisonFigee(valeur)]));
    this.echecs = new Map(Object.entries(brut.echecs));
  }

  casType(code) {
    const cas = this.cas.find((candidat) => candidat.code === code);
    if (cas === undefined) {
      throw new Error(`cas type absent de la table figée : ${code}`);
    }
    return cas;
  }
}

// -- les avantages non contributifs -------------------------------------------

/**
 * Une année de la décomposition. Les lignes sont des objets que la page lit
 * par leur code, une ligne absente y valant `undefined` ; les trois sommes sont
 * celles du modèle, dans son ordre d'addition, que la table porte plutôt que de
 * les refaire.
 */
class AnneeAvantagesFigee {
  constructor(brut) {
    this.annee = brut.annee;
    this.observee = brut.observee;
    this.lignes = brut.lignes;
    this.modele = brut.modele;
    this.anticipees = brut.anticipees;
    this.gratuit = brut.gratuit;
    this.gratuitModele = brut.gratuit_modele;
    this.anticipee = brut.anticipee;
  }
}

/** Ce que les avantages non contributifs coûtent, année par année. */
export class AvantagesFiges {
  constructor(brut) {
    this.annees = brut.annees.map((annee) => new AnneeAvantagesFigee(annee));
    this.lignes = brut.lignes;
    this.lignesModele = brut.lignes_modele;
    this.refus = brut.refus;
    this.ponderation = brut.ponderation;
  }

  get derniere() {
    return this.annees.length > 0 ? this.annees[this.annees.length - 1] : null;
  }
}

// -- le classement de l'emploi ------------------------------------------------

/** D'une carrière simulée, ce que la page lit du système actuel. */
class DepartFige {
  constructor(brut) {
    this.pensionAnnuelle = brut.pension_annuelle;
    this.trimestresRequis = brut.trimestres_requis;
  }
}

/**
 * Le cas type `cas` parti à `age`, contre la même carrière sous
 * `declassement`, partie le même jour, pour chaque génération que la page
 * compare (`CLASSEMENT_COMPARE`, dans `pages.js`).
 */
export class ClassementFige {
  constructor(brut) {
    this.cas = brut.cas;
    this.age = brut.age;
    this.declassement = brut.declassement;
    this._departs = Object.fromEntries(Object.entries(brut.departs)
      .map(([generation, departs]) => [generation, departs.map((d) => new DepartFige(d))]));
  }

  get generations() {
    return Object.keys(this._departs).map(Number);
  }

  /** L'agent actif, puis l'agent déclassé. */
  departs(generation) {
    return lire(this._departs, generation, "départ de la génération");
  }
}

// -- la table -----------------------------------------------------------------

/** Ce que les trois pages qui agrègent lisent, tel que la table le porte. */
export class AgregatsFiges {
  constructor(casTypes, avantages, classement) {
    this.casTypes = casTypes;
    this.avantages = avantages;
    this.classement = classement;
  }
}

/** Reconstruit la table depuis la clé `agregats` du paquet. */
export function chargerAgregats(donnees) {
  return new AgregatsFiges(
    new CasTypesFiges(donnees.cas_types),
    new AvantagesFiges(donnees.avantages),
    new ClassementFige(donnees.classement),
  );
}
