/**
 * Le mois, seule unité de temps que le droit de la retraite manipule vraiment.
 *
 * Portage de ``src/retraite_notionnelle/calendrier.py``.
 *
 * Le pas du moteur reste l'année, parce que les données le sont : un salaire
 * est déclaré à l'année, le salaire moyen par tête est une moyenne annuelle, un
 * quotient de mortalité est publié par âge entier. Le mois sert là, et
 * seulement là, où le réel porte une date — les bornes de la carrière, l'âge à
 * la liquidation, les dates d'effet du droit.
 */

/** Mois par année. Nommé pour que les divisions par douze se lisent. */
export const MOIS_PAR_AN = 12;

export const NOMS_DE_MOIS = [
  "janvier", "février", "mars", "avril", "mai", "juin",
  "juillet", "août", "septembre", "octobre", "novembre", "décembre",
];

/**
 * Un mois d'une année civile — la plus fine des dates du modèle.
 *
 * Les pensions prennent effet le premier jour d'un mois : c'est la maille du
 * droit, et il n'y a rien à gagner à descendre au jour, que les données ne
 * portent pas.
 */
export class DateMois {
  constructor(annee, mois) {
    if (!(mois >= 1 && mois <= MOIS_PAR_AN)) {
      throw new Error(`mois attendu entre 1 et 12, reçu ${mois}`);
    }
    this.annee = annee;
    this.mois = mois;
  }

  /** Rang absolu du mois, pour additionner et soustraire sans cas particulier. */
  get rang() {
    return this.annee * MOIS_PAR_AN + (this.mois - 1);
  }

  static depuisRang(rang) {
    return new DateMois(Math.floor(rang / MOIS_PAR_AN),
                        ((rang % MOIS_PAR_AN) + MOIS_PAR_AN) % MOIS_PAR_AN + 1);
  }

  plusMois(mois) {
    return DateMois.depuisRang(this.rang + mois);
  }

  toString() {
    return `${NOMS_DE_MOIS[this.mois - 1]} ${this.annee}`;
  }
}

/**
 * Âge en années décimales -> âge en mois entiers.
 *
 * Les âges circulent en années décimales — 64,25 pour soixante-quatre ans et
 * trois mois — parce que c'est ainsi que le code de la sécurité sociale les
 * écrit et que les adresses du simulateur les portent.
 */
export function enMois(age) {
  return Math.round(age * MOIS_PAR_AN);
}

/** Âge en années décimales -> [années entières, mois]. */
export function decomposer(age) {
  const mois = enMois(age);
  return [Math.floor(mois / MOIS_PAR_AN), mois % MOIS_PAR_AN];
}

/** « 64,58 » -> « 64 ans et 7 mois ». */
export function formaterAge(age) {
  const [annees, mois] = decomposer(age);
  return mois === 0 ? `${annees} ans` : `${annees} ans et ${mois} mois`;
}

/**
 * Le mois d'où les âges se comptent, pour qui est né ce mois-là, ce jour-là :
 * celui de la naissance pour qui est né un 1er, le suivant pour les autres. La
 * pension prend effet le premier jour d'un mois, qui ne peut précéder l'âge
 * qui l'ouvre (R. 351-37) : né le 16 mai 1964, l'âge légal est atteint le
 * 16 février 2027, et la retraite prend effet au 1er mars 2027 au plus tôt
 * (circulaire Cnav n° 2026-07). Né le 15 mars, on a, à tout 1er du mois, l'âge
 * de qui est né le 1er avril. La génération ne se lit pas d'ici. Voir
 * `origine_des_ages` du Python.
 */
export function origineDesAges(naissance, jour) {
  return jour === 1 ? naissance : naissance.plusMois(1);
}

/**
 * Mois de l'année civile ``annee`` compris entre ``debut`` et ``fin``.
 *
 * ``debut`` est inclus, ``fin`` est EXCLUE : une pension prend effet le premier
 * du mois, et ce mois-là n'est plus travaillé.
 */
export function moisTravailles(annee, debut, fin) {
  const premier = new DateMois(annee, 1).rang;
  const dernier = new DateMois(annee, MOIS_PAR_AN).rang + 1;
  return Math.max(0, Math.min(dernier, fin.rang) - Math.max(premier, debut.rang));
}

/** Part de l'année civile réellement couverte par la carrière. */
export function fractionAnnee(annee, debut, fin) {
  return moisTravailles(annee, debut, fin) / MOIS_PAR_AN;
}

/**
 * Trimestres civils entiers contenus dans un nombre de mois.
 *
 * Le droit ne retient, l'année du point de départ, que les trimestres civils
 * ÉCOULÉS : un départ au 1er août en laisse deux derrière lui, quel que soit le
 * montant cotisé pendant ces sept mois.
 */
export function trimestresCivils(mois) {
  return Math.floor(mois / 3);
}
