/**
 * La saisie d'une simulation : ce que l'adresse dit, lu en carrière et en règles.
 *
 * Portage de ``src/retraite_notionnelle/saisie.py``, qui dit ce que chaque
 * champ borne, et pourquoi. La lecture de la saisie est du calcul : les deux
 * moteurs la font, et les témoins la rejouent des deux côtés. Le texte du site,
 * lui, n'est écrit qu'une fois : dans ``pages.js`` et ``gabarit.js``.
 */

import {
  DateMois, MOIS_PAR_AN, NOMS_DE_MOIS, enMois, formaterAge, moisTravailles,
} from "./calendrier.js";
import {
  AgeConversionDroitsAcquis, ContributionEtat, ModeAgeReference, ModeIndexation,
  PartCotisation, SituationFoyer, TableConversion, avec, sousRegimeFrais,
  sousRegimeTaux,
} from "./config.js";
import { naissanceDeclaree } from "./chronologie.js";
import { formatG } from "./format.js";
import * as g from "./gabarit.js";

export const PROFILS = [
  ["auto", "Déduit du statut (défaut)"],
  ["plat", "Plat — le salaire suit le salaire moyen"],
  ["ascendant", "Ascendant — profil employé/ouvrier"],
  ["fortement_ascendant", "Fortement ascendant — profil cadre"],
];

// La règle par défaut vient EN TÊTE : c'est celle que la simulation applique, et
// donc la première ligne du tableau « D'où vient l'écart ».
export const INDEXATIONS = [
  ["masse_salariale", "Masse salariale — règle d'équilibre (défaut)"],
  ["revalorisation_portee_au_compte", "Revalorisation réellement pratiquée (arrêtés Cnav)"],
  ["triple_lock_inverse", "Triple lock inversé (règle demandée)"],
  ["triple_lock_inverse_nominal", "Triple lock inversé, tout en nominal"],
  ["mediane_trois_taux", "Médiane des trois taux"],
  ["moyenne_trois_taux", "Moyenne des trois taux"],
  ["pib_nominal", "PIB nominal (assiette la plus large)"],
  ["prix", "Prix"],
  ["salaires", "Salaire moyen"],
];

// Fenêtre de lissage maximale acceptée par le formulaire, en années. La fenêtre
// se saisit librement — 1 pour aucun lissage, 5 pour la règle italienne. La
// borne est un garde-fou de sens, pas une limite du moteur : au-delà d'une
// trentaine d'années la moyenne couvre presque toute une carrière, et ce n'est
// plus un lissage mais un taux fixe reconstitué.
export const LISSAGE_MAXIMUM = 30;

export const AGES_REFERENCE = [
  ["fixe_apres_bascule", "65 ans à partir de la bascule (défaut)"],
  ["cliquet_legal", "Cliquet légal"],
  ["cliquet_puis_esperance_vie", "Cliquet puis espérance de vie"],
  ["legal_sans_cliquet", "Âge légal, sans cliquet"],
];

export const TABLES = [["unisexe", "Unisexe (défaut)"], ["par_sexe", "Par sexe"]];

/**
 * La population dont la mortalité entre dans le diviseur. « niveau_de_vie », le
 * défaut, rattache la carrière au vingtile de niveau de vie où son salaire la
 * place ; « commune » est la table de population générale, la même pour tout le
 * monde, et désactive la mesure ; les autres clés imposent une population.
 */
/** Par quoi la carrière est rattachée à son vingtile de niveau de vie. */
export const RATTACHEMENTS = [
  ["salaire", "Par le salaire (défaut)"],
  ["pension", "Par la pension"],
];

export const POPULATIONS = [
  ["niveau_de_vie", "Par niveau de vie (défaut)"],
  ["commune", "Population générale, la même pour tous"],
  ["fonctionnaires_civils_etat", "Fonctionnaires civils de l'État"],
  ["niveau_de_vie_v01", "Les 5 % les plus modestes (INSEE)"],
  ["niveau_de_vie_v10", "Niveau de vie médian (INSEE)"],
  ["niveau_de_vie_v20", "Les 5 % les plus aisés (INSEE)"],
];

export const PARTS_COTISATION = [
  ["salariale", "Part salariale seule (défaut)"],
  ["totale", "Salariale et patronale"],
  ["totale_alignee", "Salariale et patronale, public aligné sur le privé"],
];

// Ce que le compte d'un agent de l'État reçoit de son employeur, là où la part
// patronale y est portée : le taux versé, ou sa part « retraite ».
export const CONTRIBUTIONS_ETAT = [
  ["retraite_seule", "Sa part « retraite seule », selon la Cour des comptes (défaut)"],
  ["entiere", "Entière, telle que l'État l'a versée"],
];

export const CONVERSIONS_ACQUIS = [
  ["reference", "À l'âge de référence (défaut)"],
  ["liquidation", "À l'âge de départ effectif"],
];

// Situation de foyer de la garantie vieillesse du système 4. Elle ne joue que
// sur l'allocation d'isolement : la garantie est individualisée, et la pension
// du conjoint n'entre jamais dans le calcul.
export const SITUATIONS_FOYER = [
  ["seul", "Personne seule (défaut)"],
  ["couple", "En couple"],
];

export const PROJECTIONS = [
  ["cor_reference", "COR référence — productivité 0,7 %"],
  ["cor_productivite_basse", "COR variante basse — 0,4 %"],
  ["cor_productivite_haute", "COR variante haute — 1,0 %"],
];

// L'emploi au-delà de la dernière observation. Il ne compose que la masse
// salariale et le PIB projetés, donc l'indexation des comptes notionnels : les
// systèmes 2 à 6 le lisent, le système 1 ne lit ni l'une ni l'autre.
export const TRAJECTOIRES_EMPLOI = [
  ["cor_2026", "Trajectoire du COR — juin 2026 (défaut)"],
  ["constant", "Emploi constant"],
];

// Les pensions déjà servies à la bascule, sur la page Coût : elles gardent les
// prix que le droit leur promet, ou la réforme les réindexe sur la règle du
// compte le jour où elle s'applique. Systèmes 2 à 6 seulement.
export const REVALORISATIONS_STOCK = [
  ["prix", "Gardent les prix (défaut)"],
  ["reindexe", "Réindexées sur la règle du compte"],
];

// Les frais du pilier capitalisé du système 4 : les codes sont ceux de
// `sousRegimeFrais` (config.js), l'ordre est celui du menu.
export const REGIMES_FRAIS = [
  ["paliers", "Marché 2025, baisse par paliers (défaut)"],
  ["plafond", "Paliers, et tout le stock suit : un plafond"],
  ["contrats", "Paliers, le stock garde son tarif : des contrats"],
  ["figes", "Marché 2025, sans baisse"],
  ["detail", "PER vendu en 2025 : 2,20 % d'arrérages, sans frais de réserve, sans baisse"],
  ["aucun", "Aucun frais"],
];

// Les taux futurs auxquels le pilier du système 4 place ses versements. Les
// codes sont ceux de `sousRegimeTaux` (config.js), l'ordre est celui du menu.
export const REGIMES_TAUX = [
  ["forwards", "Taux à terme de la courbe (défaut)"],
  ["prime", "Prime de terme retirée : 0,50 point à 30 ans"],
  ["prime_haute", "Prime de terme haute : 1 point à 30 ans"],
];

// Les deux façons d'écrire un revenu. Le modèle n'en connaît qu'une — le
// multiple du salaire moyen, seule qui garde son sens sur quatre-vingts ans —,
// mais personne ne connaît son salaire dans cette unité-là : c'est l'euro qui
// est proposé d'abord, et le multiple reste à un clic pour qui raisonne en
// relatif. La liste ne s'affiche pas — on passe d'une unité à l'autre par un
// lien, qui convertit au passage — mais elle borne ce qu'une adresse peut dire.
export const UNITES_REVENU = [
  ["euros_mois", "€ bruts par mois"],
  ["moyen", "× le salaire moyen"],
];

// Ce que porte le champ tant que rien n'a été saisi, dans chaque unité. Un
// nombre rond proche du salaire moyen plutôt que le salaire moyen exact : le
// champ est fait pour être remplacé, et « 3 500 » se relit mieux que « 3 475 ».
export const SALAIRE_DEFAUT = { euros_mois: 3500.0, moyen: 1.0 };

/**
 * Où l'on en est de sa vie, et c'est la PREMIÈRE question du formulaire.
 *
 * Elle a remplacé « Je saisis : mon revenu / ma pension », qui était une
 * question de modélisation déguisée en question à l'utilisateur : elle
 * demandait de choisir une entrée du calcul, quand celle-ci se déduit de ce
 * qu'on est. Un actif ne connaît pas sa pension, un retraité ne se souvient
 * pas de son salaire : la situation commande la saisie, et non l'inverse.
 *
 * ELLE N'ENTRE DANS AUCUN CALCUL. Le modèle ne connaît que la date de départ,
 * et c'est elle qui dit, au jour près, si la pension est déjà servie ou non.
 * La situation n'oriente que le formulaire : ce qu'il demande, et comment il
 * le nomme. Deux réglages qui se contrediraient ne peuvent donc pas fausser un
 * chiffre, et le formulaire le signale au lieu de le corriger.
 */
export const SITUATIONS = [
  ["actif", "en activité"],
  ["retraite", "à la retraite"],
];

/**
 * Ce que chaque situation demande par défaut. Le lien de la bascule porte les
 * deux, si bien que choisir sa situation reconfigure le formulaire d'un coup.
 */
export const SAISIE_DE_LA_SITUATION = { actif: "revenu", retraite: "pension" };

/**
 * Ce que le formulaire demande : un revenu d'activité, ou une pension. Ce
 * n'est plus un choix offert au lecteur mais la conséquence de sa situation :
 * les libellés ont disparu avec la bascule qui les portait, et il ne reste que
 * les deux codes, qui bornent ce qu'une adresse a le droit de dire.
 */
export const SAISIES = [["revenu", ""], ["pension", ""]];

/**
 * Pension mensuelle proposée par défaut, en euros NETS. Voisine de la pension
 * moyenne de droit direct des retraités de droit français, pour que le
 * formulaire s'ouvre sur un cas qui ressemble à celui de qui le lit.
 */
const PENSION_DEFAUT = 1500.0;

/**
 * Les bornes du niveau de revenu, en multiples du salaire moyen. Le formulaire
 * les impose au champ, et l'inversion balaie l'intervalle qu'elles ferment :
 * c'est le même domaine, et il n'y en a qu'un.
 */
export const NIVEAU_MINIMAL = 0.1;
export const NIVEAU_MAXIMAL = 10.0;

// Les deux façons de lire tout montant du simulateur — ce qu'on saisit comme
// ce qu'on affiche. Un seul réglage pour les deux : lire un salaire net et une
// pension brute sur la même page compare deux grandeurs différentes, et c'est
// exactement ce que le site faisait avant cette bascule. Le défaut est le NET,
// parce que c'est ce qu'on touche et ce qu'on connaît de soi ; le brut reste à
// un clic, et reste la langue des capitaux et des assiettes, bruts par nature.
export const MODES_MONTANT = [
  ["net", "net — ce qui arrive sur le compte"],
  ["brut", "brut — avant CSG et cotisations"],
];

// Durée mensuelle de référence du SMIC : 35 heures par semaine ramenées au
// mois, soit 151,67 heures. Elle ne sert qu'à écrire un repère à l'échelle d'un
// salaire mensuel.
export const HEURES_SMIC_PAR_MOIS = 151.67;

/**
 * Nombre maximal de métiers d'une carrière, le premier compris. Le formulaire
 * affiche toujours une ligne vide de plus que les métiers saisis : c'est ainsi
 * qu'on en ajoute un, sans une ligne de JavaScript. La borne n'est pas une
 * limite du moteur mais celle du formulaire : au-delà, ce n'est plus une suite
 * de métiers qu'on décrit, c'est un relevé de carrière année par année — et
 * celui-là a son propre champ, borné par `RELEVE_MAXIMUM`.
 */
export const METIERS_MAXIMUM = 6;

/**
 * La réponse qui dit qu'une activité S'AJOUTE à celle en cours. Toute autre
 * réponse que celle-ci ou le vide est refusée.
 */
export const CUMUL = "oui";

/**
 * Nombre de lignes qu'un relevé de carrière peut porter. Une carrière tient
 * entre quatorze ans — l'âge de début minimal — et soixante-quinze, soit
 * soixante et une années civiles au plus ; la borne laisse deux lignes de marge
 * et ferme surtout la porte que les interruptions avaient ouverte : le calcul
 * se fait chez le lecteur et l'adresse EST la saisie, si bien qu'un relevé de
 * cent mille lignes forgé dans un lien figeait l'onglet de celui qui le suivait.
 */
export const RELEVE_MAXIMUM = 63;

/**
 * Bornes des deux années que l'utilisateur peut choisir : celle de la bascule
 * au régime unique, et celle des euros constants dans lesquels les montants
 * sont exprimés. Elles étaient déclarées sur les champs du formulaire, donc
 * opposables au navigateur seulement : une adresse forgée à la main les
 * franchissait sans rien déclencher, et « ?euros=9999 » faisait afficher au
 * simulateur des pensions à soixante chiffres. La borne se dit ici, une fois,
 * et le formulaire la lit — les deux ne peuvent plus diverger.
 */
export const ANNEE_MINIMALE = 1941;
export const ANNEE_MAXIMALE = 2070;

/**
 * Un enfant de plus change la pension du système 1 par ses majorations. Le
 * champ était borné à douze dans le formulaire et nulle part ailleurs.
 */
export const ENFANTS_MAXIMUM = 12;

/**
 * Bornes de l'année de naissance et des deux âges saisis. Elles étaient écrites
 * deux fois — une fois dans `verifier`, une fois sur le champ du formulaire —,
 * comme l'étaient les années de bascule avant `ANNEE_MINIMALE`. Elles se disent
 * ici, une fois, et le formulaire les lit.
 */
export const NAISSANCE_MINIMALE = 1900;
export const NAISSANCE_MAXIMALE = 2020;
export const AGE_DEBUT_MINIMAL = 14;
export const AGE_DEBUT_MAXIMAL = 40;
export const AGE_LIQUIDATION_MINIMAL = 40;
export const AGE_LIQUIDATION_MAXIMAL = 75;

/**
 * Toute année qu'une carrière peut couvrir, quel qu'en soit l'auteur : né au
 * plus tôt et entré au plus jeune d'un côté, né au plus tard et parti au plus
 * vieux de l'autre. Sert à borner les interruptions, dont les années étaient
 * reprises telles quelles : « 0:999999999:chomage_indemnise » faisait boucler un
 * milliard de fois et figeait l'onglet. Une plage hors de cette fenêtre ne
 * décrit aucune carrière, et se refuse au lieu de se calculer.
 */
export const ANNEE_CARRIERE_MINIMALE = NAISSANCE_MINIMALE + AGE_DEBUT_MINIMAL;
export const ANNEE_CARRIERE_MAXIMALE = NAISSANCE_MAXIMALE + AGE_LIQUIDATION_MAXIMAL;

/**
 * Ce qu'une ligne de carrière peut décrire à la place d'un métier.
 *
 * Une carrière n'est pas faite que d'emplois, et le formulaire ne demandait que
 * ceux-là : entre le dernier métier et le départ, il supposait qu'on
 * travaillait. Qui s'arrête à 58 ans pour liquider à 64 voyait donc six années
 * cotisées qu'il n'avait pas vécues. Une ligne dont le statut est l'un de ces
 * motifs dit l'inverse : à partir de cette date, et jusqu'à la ligne suivante
 * ou jusqu'au départ, l'activité s'arrête. La DERNIÈRE ligne dit donc la date
 * de fin d'activité, quand elle est antérieure au départ.
 *
 * Les codes sont ceux de `legislation/periodes_non_travaillees.csv`, qui dit ce
 * que chacun ouvre — trimestres assimilés, points complémentaires financés par
 * l'UNEDIC ou la Sécurité sociale, AVPF, services de la fonction publique. Un
 * test vérifie qu'aucun code d'ici
 * n'est absent de là-bas : le menu ne peut pas proposer un motif que le moteur
 * traiterait en « sans activité » sans le dire.
 *
 * Les libellés sont des groupes nominaux : le menu les fait précéder de « Sans
 * emploi : », le résumé de carrière les emploie tels quels — « chômage
 * indemnisé de 58 ans à 62 ans ».
 */
export const SANS_EMPLOI = [
  ["chomage_indemnise", "chômage indemnisé"],
  ["chomage_non_indemnise", "chômage non indemnisé"],
  ["maladie", "arrêt maladie"],
  ["accident_travail", "accident du travail"],
  ["maternite", "congé de maternité"],
  ["invalidite", "invalidité"],
  ["education_enfant", "élever un enfant"],
  ["service_militaire", "service militaire"],
  ["sans_activite", "sans activité, ni chômage"],
];

/**
 * Les seuls codes de `SANS_EMPLOI`, pour reconnaître une ligne sans emploi.
 *
 * Ces codes ne valent que pour une ligne qui SUIT la première : une carrière
 * commence quand on commence à travailler, et la première ligne ne porte donc
 * qu'une affiliation. « sans_activite » fait exception d'un côté — c'est aussi
 * une affiliation, « Sans activité professionnelle », qui ne route vers aucun
 * régime, et une adresse qui la porte en premier métier décrit quelqu'un qui
 * n'a jamais travaillé. Les deux chemins donnent le même résultat au bit près :
 * une ligne suivante la lit comme un motif, la première comme l'affiliation
 * qu'elle a toujours été.
 */
export const CODES_SANS_EMPLOI = new Set(SANS_EMPLOI.map(([code]) => code));

/** Saisie inexploitable, à afficher telle quelle à l'utilisateur. */
export class ErreurSaisie extends Error {}

/**
 * Les clés de requête qui décrivent les RÈGLES, et non la carrière.
 *
 * Ce sont exactement les dix que `Saisie.parametres` lit pour fabriquer un jeu
 * de paramètres : tout le reste — naissance, statut, revenu, enfants, profil,
 * interruptions — décrit un individu, et un individu n'a pas sa place dans un
 * agrégat. C'est cette liste qui permet aux trois pages agrégées de lire une
 * adresse de simulateur sans rien en retenir d'autre que les règles, et aux
 * liens internes de ne porter que ce qui a un sens partout.
 *
 * Le sexe n'en est pas : il ne joue que sur la table de conversion « par sexe »
 * et sur les majorations pour enfants, deux réglages individuels. Les cas types
 * portent le leur.
 */
export const CLES_MODELISATION = Object.freeze([
  "indexation", "lissage", "age_reference", "table", "population",
  "rattachement", "conversion_acquis", "part_cotisation",
  "contribution_etat", "foyer", "projection", "emploi", "stock", "reprise",
  "frais", "taux", "bascule", "euros",
]);

export const DEFAUTS = Object.freeze({
  naissance: 1975,
  naissance_mois: 1,
  //: Jour de naissance. Il n'entre dans aucun calcul — le modèle compte en
  //: mois, et le droit coupe ses générations au mois. Il est gardé parce que le
  //: calendrier en demande un : sans lui, le formulaire répondrait « 1er mars »
  //: à qui est né le 15, et ferait douter de ce qu'il a compris.
  naissance_jour: 1,
  sexe: "H",
  statut: "salarie_prive_non_cadre",
  debut: 21,
  liquidation: 64,
  //: Revenu du premier métier, dans l'unité choisie ci-dessous.
  salaire: SALAIRE_DEFAUT.euros_mois,
  //: Unité dans laquelle les revenus sont saisis, pour TOUS les métiers : un
  //: seul choix pour la carrière entière, parce qu'on décrit une même vie de
  //: travail et qu'un changement d'unité en cours de route n'est pas une
  //: information sur la carrière. Les euros sont ceux d'aujourd'hui : on saisit
  //: ce que le métier paie maintenant, et le modèle suit ensuite le salaire
  //: moyen d'une année à l'autre.
  unite_revenu: "euros_mois",
  montants: "net",
  //: Ce que le formulaire demande : `revenu` — ce qu'on gagne en travaillant,
  //: d'où le simulateur tire une pension — ou `pension` — ce qu'on touche déjà,
  //: d'où il remonte au revenu. Voir `SAISIES`.
  //: En activité ou à la retraite : la première question du formulaire, et la
  //: seule qui n'entre dans aucun calcul. Voir `SITUATIONS`.
  situation: "actif",
  saisie_par: "revenu",
  //: La pension mensuelle saisie, quand c'est elle qu'on saisit. Elle est dans
  //: la MÊME convention que les montants affichés : nette ou brute selon
  //: `montants`, et en euros constants de `euros`. C'est ce qui la rend
  //: comparable sans rien convertir. Pour un retraité, c'est la pension qu'il
  //: touche AUJOURD'HUI, et le simulateur la compare à sa pension de départ
  //: revalorisée comme le droit l'a fait. Voir `champPension`.
  pension: PENSION_DEFAUT,
  //: Les métiers exercés APRÈS le premier. Le premier, lui, est décrit par
  //: ``statut``, ``debut`` et ``salaire`` : une adresse d'avant les carrières
  //: multiples reste donc valide, et décrit la carrière d'un seul métier.
  metiers: Object.freeze([]),
  //: Le relevé de carrière, une ligne par année : « année:régime:revenu » et,
  //: si le relevé les porte, « :trimestres ». Non vide, il REMPLACE la carrière
  //: paramétrique — les métiers, le profil et le niveau de revenu ne servent
  //: plus à rien : plus rien n'est reconstitué, tout est lu.
  releve: "",
  profil: "auto",
  primes: 0.0,
  enfants: 0,
  //: Les naissances des premiers enfants, dans l'ordre : « 1995, 1998-06 ».
  //: Celles qui ne sont pas dites sont présumées. Voir `naissancesEnfants`.
  naissances: "",
  interruptions: "",
  indexation: "masse_salariale",
  lissage: 1,
  age_reference: "fixe_apres_bascule",
  table: "unisexe",
  population: "niveau_de_vie",
  rattachement: "salaire",
  conversion_acquis: "reference",
  part_cotisation: "salariale",
  contribution_etat: "retraite_seule",
  // Seul ou en couple : la situation de foyer de la garantie vieillesse du
  // système 4. Le défaut est la personne seule, comme pour l'ASPA.
  foyer: "seul",
  projection: "cor_reference",
  emploi: "cor_2026",
  stock: "prix",
  // Part de l'avance de la garantie que la succession couvre, en pour cent ;
  // null, elle est calculée sur le patrimoine des ménages retraités.
  reprise: null,
  // Les frais du pilier capitalisé : marché 2025 et baisse par paliers, ou
  // l'une des variantes qui disent ce que chaque hypothèse déplace.
  frais: "paliers",
  taux: "forwards",
  bascule: 2026,
  euros: 2026,
  //: Vrai si la requête portait des paramètres, donc s'il faut calculer.
  demandee: false,
});

/** Paramètres d'une simulation, tels que l'utilisateur les a saisis. */
export class Saisie {
  constructor(champs = {}) {
    Object.assign(this, DEFAUTS, champs);
  }

  /**
   * `tolerante` ne sert qu'à REMONTRER une saisie refusée : rien n'y est
   * vérifié, et une ligne de métier incomplète arrête la lecture des métiers
   * au lieu de la refuser. Une saisie lue ainsi ne se calcule jamais — voir
   * `saisieRefusee`.
   */
  static depuisRequete(parametres, tolerante = false) {
    // Le premier métier se lit d'abord : les suivants héritent de son niveau de
    // revenu quand ils n'en portent pas.
    const statut = parametres.statut || DEFAUTS.statut;
    // Une adresse d'avant les euros porte « salaire » sans unité, et son nombre
    // est un multiple du salaire moyen : la lire en euros en ferait un salaire
    // d'un euro par mois. Le défaut n'est donc l'euro que pour un formulaire
    // vierge — d'où le fait que `requete` écrive TOUJOURS l'unité, ce qui rend
    // la question sans objet pour les adresses neuves.
    const ancienne = !("unite_revenu" in parametres) && Object.keys(parametres)
      .some((cle) => cle === "salaire" || cle.endsWith("_salaire"));
    const unite = parmi(parametres, "unite_revenu", UNITES_REVENU,
      ancienne ? "moyen" : DEFAUTS.unite_revenu);
    const salaire = reel(parametres, "salaire", SALAIRE_DEFAUT[unite]);
    // La naissance se lit avant tout le reste : les dates de carrière ne valent
    // un âge que rapportées à elle.
    const situation = parmi(parametres, "situation", SITUATIONS,
      DEFAUTS.situation);
    const naissance = dateSaisie(parametres, "naissance");
    const anneeNaissance = naissance
      ? naissance.annee : entier(parametres, "naissance", DEFAUTS.naissance);
    const moisNaissance = naissance
      ? naissance.mois : entier(parametres, "naissance_mois", DEFAUTS.naissance_mois);
    const saisie = new Saisie({
      unite_revenu: unite,
      montants: parmi(parametres, "montants", MODES_MONTANT, DEFAUTS.montants),
      situation,
      // Ce que la situation demande, SAUF si l'adresse dit autre chose : un
      // retraité peut préférer saisir ce qu'il gagnait. Le défaut suit la
      // situation, l'explicite l'emporte — c'est ce qui fait qu'une adresse
      // réduite à « situation=retraite » ouvre le formulaire sur la pension.
      saisie_par: parmi(parametres, "saisie_par", SAISIES,
        SAISIE_DE_LA_SITUATION[situation]),
      pension: reel(parametres, "pension", DEFAUTS.pension),
      naissance: anneeNaissance,
      naissance_mois: moisNaissance,
      naissance_jour: naissance ? naissance.jour : DEFAUTS.naissance_jour,
      sexe: parametres.sexe === "F" ? "F" : "H",
      statut,
      debut: ageSaisi(parametres, "debut", DEFAUTS.debut,
        anneeNaissance, moisNaissance),
      liquidation: ageSaisi(parametres, "liquidation", DEFAUTS.liquidation,
        anneeNaissance, moisNaissance),
      salaire,
      metiers: metiersSaisis(parametres, salaire, anneeNaissance, moisNaissance,
        tolerante),
      releve: (parametres.releve || "").trim(),
      profil: parmi(parametres, "profil", PROFILS, DEFAUTS.profil),
      primes: reel(parametres, "primes", DEFAUTS.primes),
      enfants: entier(parametres, "enfants", DEFAUTS.enfants),
      naissances: (parametres.naissances || "").trim(),
      interruptions: (parametres.interruptions || "").trim(),
      indexation: parmi(parametres, "indexation", INDEXATIONS, DEFAUTS.indexation),
      lissage: entier(parametres, "lissage", DEFAUTS.lissage),
      age_reference: parmi(parametres, "age_reference", AGES_REFERENCE, DEFAUTS.age_reference),
      table: parmi(parametres, "table", TABLES, DEFAUTS.table),
      population: parmi(parametres, "population", POPULATIONS, DEFAUTS.population),
      rattachement: parmi(parametres, "rattachement", RATTACHEMENTS, DEFAUTS.rattachement),
      conversion_acquis: parmi(
        parametres, "conversion_acquis", CONVERSIONS_ACQUIS, DEFAUTS.conversion_acquis,
      ),
      part_cotisation: parmi(
        parametres, "part_cotisation", PARTS_COTISATION,
        DEFAUTS.part_cotisation,
      ),
      contribution_etat: parmi(
        parametres, "contribution_etat", CONTRIBUTIONS_ETAT,
        DEFAUTS.contribution_etat,
      ),
      foyer: parmi(parametres, "foyer", SITUATIONS_FOYER, DEFAUTS.foyer),
      projection: parmi(parametres, "projection", PROJECTIONS, DEFAUTS.projection),
      emploi: parmi(parametres, "emploi", TRAJECTOIRES_EMPLOI, DEFAUTS.emploi),
      stock: parmi(parametres, "stock", REVALORISATIONS_STOCK, DEFAUTS.stock),
      reprise: entier(parametres, "reprise", DEFAUTS.reprise),
      frais: parmi(parametres, "frais", REGIMES_FRAIS, DEFAUTS.frais),
      taux: parmi(parametres, "taux", REGIMES_TAUX, DEFAUTS.taux),
      bascule: entier(parametres, "bascule", DEFAUTS.bascule),
      euros: entier(parametres, "euros", DEFAUTS.euros),
      // Une adresse qui ne porte QUE des réglages de modélisation ne demande
      // pas de calcul : elle règle le modèle. C'est ce qui permet aux liens
      // internes de porter les réglages partout — y compris vers le
      // simulateur — sans que cliquer « Simuler » dans le bandeau ne lance
      // d'office le calcul d'une carrière que personne n'a saisie. Toute
      // adresse portant le moindre champ de carrière demande un calcul, comme
      // avant.
      demandee: Object.keys(parametres).some((cle) => !CLES_MODELISATION.includes(cle)),
    });
    if (!tolerante) { saisie.verifier(); }
    return saisie;
  }

  verifier() {
    if (!(this.naissance_mois >= 1 && this.naissance_mois <= 12)) {
      throw new ErreurSaisie("Mois de naissance attendu entre 1 et 12.");
    }
    if (!(this.naissance_jour >= 1 && this.naissance_jour <= 31)) {
      throw new ErreurSaisie("Jour de naissance attendu entre 1 et 31.");
    }
    if (!(this.naissance >= NAISSANCE_MINIMALE && this.naissance <= NAISSANCE_MAXIMALE)) {
      throw new ErreurSaisie(
        `Année de naissance hors du champ du modèle : ${this.naissance}. `
        + `Attendu entre ${NAISSANCE_MINIMALE} et ${NAISSANCE_MAXIMALE}.`,
      );
    }
    if (!(this.debut >= AGE_DEBUT_MINIMAL && this.debut <= AGE_DEBUT_MAXIMAL)) {
      throw new ErreurSaisie(
        "Début d'activité : le modèle l'accepte de "
        + `${AGE_DEBUT_MINIMAL} à ${AGE_DEBUT_MAXIMAL} ans, soit `
        + `${this.fenetre(AGE_DEBUT_MINIMAL, AGE_DEBUT_MAXIMAL)}.`,
      );
    }
    if (!(this.liquidation >= AGE_LIQUIDATION_MINIMAL
          && this.liquidation <= AGE_LIQUIDATION_MAXIMAL)) {
      throw new ErreurSaisie(
        "Départ à la retraite : le modèle l'accepte de "
        + `${AGE_LIQUIDATION_MINIMAL} à ${AGE_LIQUIDATION_MAXIMAL} ans, soit `
        + `${this.fenetre(AGE_LIQUIDATION_MINIMAL, AGE_LIQUIDATION_MAXIMAL)}.`,
      );
    }
    if (this.liquidation <= this.debut) {
      throw new ErreurSaisie(
        "Le départ à la retraite doit suivre le début d'activité, "
        + `fixé en ${this.dateDe(this.debut)}.`,
      );
    }
    this.verifierRevenu(this.salaire, 1);
    if (!(this.primes >= 0 && this.primes <= 0.6)) {
      throw new ErreurSaisie("Part de primes attendue entre 0 et 0,6.");
    }
    if (!(this.enfants >= 0 && this.enfants <= ENFANTS_MAXIMUM)) {
      throw new ErreurSaisie(
        `Nombre d'enfants attendu entre 0 et ${ENFANTS_MAXIMUM}.`,
      );
    }
    this.verifierNaissances();
    if (!(this.bascule >= ANNEE_MINIMALE && this.bascule <= ANNEE_MAXIMALE)) {
      throw new ErreurSaisie(
        `Année de bascule attendue entre ${ANNEE_MINIMALE} et `
        + `${ANNEE_MAXIMALE}.`,
      );
    }
    if (!(this.euros >= ANNEE_MINIMALE && this.euros <= ANNEE_MAXIMALE)) {
      throw new ErreurSaisie(
        `Année des euros constants attendue entre ${ANNEE_MINIMALE} et `
        + `${ANNEE_MAXIMALE}.`,
      );
    }
    if (this.reprise !== null && !(this.reprise >= 0 && this.reprise <= 100)) {
      throw new ErreurSaisie(
        "Part de l'avance couverte par la succession attendue entre 0 et 100.",
      );
    }
    if (!(this.lissage >= 1 && this.lissage <= LISSAGE_MAXIMUM)) {
      throw new ErreurSaisie(
        `Fenêtre de lissage attendue entre 1 et ${LISSAGE_MAXIMUM} ans `
        + "(1 = aucun lissage).",
      );
    }
    this._verifierPension();
    // Les métiers se suivent sans se recouvrir : chacun commence après le
    // précédent et avant le départ à la retraite.
    let precedent = this.debut;
    this.metiers.forEach((metier, index) => {
      const rang = index + 2;
      if (metier.cumul) {
        this.verifierCumul(metier, rang);
        return;
      }
      if (!(metier.debut >= AGE_DEBUT_MINIMAL
            && metier.debut <= AGE_LIQUIDATION_MAXIMAL)) {
        throw new ErreurSaisie(
          `Métier n° ${rang} : il doit commencer `
          + `${this.fenetre(AGE_DEBUT_MINIMAL, AGE_LIQUIDATION_MAXIMAL)}, `
          + `soit de ${AGE_DEBUT_MINIMAL} à ${AGE_LIQUIDATION_MAXIMAL} ans.`,
        );
      }
      if (metier.debut <= precedent) {
        throw new ErreurSaisie(
          `Métier n° ${rang} : il doit commencer après le précédent, qui `
          + `commence en ${this.dateDe(precedent)}.`,
        );
      }
      if (metier.debut >= this.liquidation) {
        throw new ErreurSaisie(
          `Métier n° ${rang} : il doit commencer avant le départ à la retraite, `
          + `fixé en ${this.dateDe(this.liquidation)}.`,
        );
      }
      this.verifierRevenu(metier.salaire, rang);
      precedent = metier.debut;
    });
  }

  /**
   * Une activité ajoutée : dans la carrière, et payée de son revenu. Elle ne
   * suit pas la précédente — elle l'accompagne. Elle ne se décrit pas par la
   * pension, qui ne dit qu'un niveau pour toute la carrière.
   */
  verifierCumul(metier, rang) {
    if (this.parPension) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : une activité qui s'ajoute à celle en cours se `
        + "décrit par son revenu. La saisie par la pension ne cherche qu'un "
        + "niveau pour toute la carrière, et ne dirait rien de celui de cette "
        + "activité-là.",
      );
    }
    if (metier.debut < this.debut) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : une activité qui s'ajoute commence pendant la `
        + `carrière, qui commence en ${this.dateDe(this.debut)}.`,
      );
    }
    if (metier.debut >= this.liquidation) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : il doit commencer avant le départ à la retraite, `
        + `fixé en ${this.dateDe(this.liquidation)}.`,
      );
    }
    if (metier.fin !== null
        && !(metier.debut < metier.fin && metier.fin <= this.liquidation)) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : il doit s'arrêter après avoir commencé, et au plus `
        + `tard au départ, fixé en ${this.dateDe(this.liquidation)}.`,
      );
    }
    this.verifierRevenu(metier.salaire, rang);
  }

  /**
   * Vrai si c'est la pension qui est saisie, et le revenu qui se cherche. Le
   * relevé l'emporte sur elle comme il l'emporte sur les revenus : il donne la
   * carrière année par année, il n'y a plus rien à inverser.
   */
  get parPension() {
    return this.saisie_par === "pension" && !this.releveActif;
  }

  /**
   * La pension saisie, contrôlée avant qu'on cherche ce qu'elle suppose. Une
   * borne haute serait un chiffre inventé : c'est le PLAFOND DU STATUT qui dit
   * ce qu'une carrière peut acquérir, il se lit sur la courbe, et l'inversion
   * le rapporte elle-même. Seul le zéro est refusé ici.
   */
  _verifierPension() {
    if (this.saisie_par !== "pension") return;
    if (!(this.pension > 0)) {
      throw new ErreurSaisie("La pension doit être strictement positive.");
    }
  }

  /** Vrai si les revenus sont saisis en euros, faux si c'est un ratio. */
  get revenu_en_euros() {
    return this.unite_revenu === "euros_mois";
  }

  /** Vrai si tout — saisie et affichage — se lit en net. */
  get enNet() {
    return this.montants === "net";
  }

  /**
   * Vrai si le nombre saisi est un NET à convertir. Le mode ne change la
   * SAISIE que lorsqu'elle est en euros : un multiple du salaire moyen est un
   * rapport entre deux bruts, et le convertir n'aurait pas de sens — le
   * salaire moyen publié par l'INSEE est brut.
   */
  get saisieEnNet() {
    return this.enNet && this.revenu_en_euros;
  }

  /**
   * Un revenu saisi, contrôlé dans l'unité où il a été écrit. Le message parle
   * la langue du champ : refuser « 2 500 € par mois » au motif qu'il faut
   * « entre 0,1 et 10 fois le salaire moyen » ne dirait rien à qui n'a jamais
   * entendu parler de cette unité.
   */
  verifierRevenu(valeur, rang) {
    if (this.revenu_en_euros) {
      if (!(valeur > 0)) {
        throw refus(rang, "Le revenu doit être strictement positif.");
      }
      return;
    }
    if (!(valeur >= 0.1 && valeur <= 10)) {
      throw refus(
        rang, "Niveau de revenu attendu entre 0,1 et 10 fois le salaire moyen.",
      );
    }
  }

  /**
   * Le revenu de chaque métier, ramené à l'unité du modèle. C'est ici, et nulle
   * part ailleurs, que l'euro entre dans le modèle. Le moteur ne connaît que le
   * multiple du salaire moyen : il garde son sens sur quatre-vingts ans, quand
   * un montant n'en a que rapporté à son année.
   */
  /**
   * Toutes les lignes du formulaire, la première comprise.
   *
   * Le premier métier vit dans des champs à part — `statut`, `debut`,
   * `salaire` —, parce que l'adresse les portait ainsi avant qu'une carrière
   * puisse en compter plusieurs. Il n'y a pourtant aucune raison de le traiter
   * autrement que les suivants, et tout ce qui parcourt la carrière passe ici.
   */
  get lignesCarriere() {
    return [
      {
        debut: this.debut, statut: this.statut, salaire: this.salaire,
        sans_emploi: false, cumul: false, fin: null,
      },
      ...this.metiers,
    ];
  }

  niveaux(echelle) {
    const lignes = this.lignesCarriere;
    let saisis = lignes.map((ligne) => ligne.salaire);
    if (!this.revenu_en_euros) {
      return saisis;
    }
    // En mode net, le nombre saisi n'est pas encore un brut : on remonte
    // d'abord jusqu'à lui, statut par statut, PUIS on ramène à l'unité du
    // modèle. L'ordre compte — le salaire moyen de l'échelle est un brut.
    if (this.saisieEnNet) {
      saisis = saisis.map(
        (valeur, index) => echelle.brutMensuel(valeur, lignes[index].statut),
      );
    }
    return saisis.map((valeur) => echelle.niveau(valeur));
  }

  /**
   * La carrière comme suite de MÉTIERS, le premier compris. C'est sous cette
   * forme que le modèle la reçoit ; le formulaire, lui, garde le premier métier
   * dans ses champs historiques.
   *
   * Les périodes sans emploi n'en sont pas : elles ne portent ni régime ni
   * cotisation, et le métier qui les précède court, pour le modèle, jusqu'au
   * métier suivant. Ce qu'elles changent — l'année ne cotise pas — passe par
   * `interruptionsDeCarriere`, qui est le seul chemin que le moteur connaisse
   * pour une année non travaillée.
   */
  parcours(echelle) {
    const niveaux = this.niveaux(echelle);
    const metiers = [];
    this.lignesCarriere.forEach((ligne, index) => {
      if (ligne.sans_emploi) { return; }
      this.verifierNiveau(niveaux[index], index + 1, echelle);
      metiers.push({
        affiliation: ligne.statut,
        age_debut: ligne.debut,
        niveau_salaire: niveaux[index],
        cumul: ligne.cumul,
        age_fin: ligne.fin,
      });
    });
    return metiers;
  }

  /**
   * Les années non cotisées : celles des lignes, et celles du champ.
   *
   * Une période sans emploi est bornée au MOIS sur le formulaire ; le modèle,
   * lui, ne connaît qu'un statut par année civile — les régimes liquident à
   * l'année. L'année où l'activité s'arrête revient donc à ce qui en occupe le
   * plus de mois, exactement comme l'année d'un changement de métier revient au
   * métier qui en occupe le plus ; à égalité, elle reste travaillée.
   *
   * Le champ « Interruptions » garde le dernier mot : il désigne des années une
   * à une, et c'est l'outil le plus fin des deux.
   */
  interruptionsDeCarriere(motifsConnus = null) {
    const annees = new Map();
    const debut = this.dateDe(this.debut);
    const fin = this.dateDe(this.liquidation);
    const lignes = this.lignesCarriere;
    lignes.forEach((ligne, index) => {
      if (!ligne.sans_emploi) { return; }
      const ouverture = this.dateDe(ligne.debut);
      // Une activité ajoutée ne clôt pas l'interruption : elle se tient à
      // côté. C'est la période principale suivante qui la clôt.
      const suivante = lignes.slice(index + 1).find((autre) => !autre.cumul);
      const cloture = suivante ? this.dateDe(suivante.debut) : fin;
      for (let annee = ouverture.annee; annee <= cloture.annee; annee += 1) {
        const creux = moisTravailles(annee, ouverture, cloture);
        const portee = moisTravailles(annee, debut, fin);
        if (portee && creux * 2 > portee) {
          annees.set(annee, ligne.statut);
        }
      }
    });
    this.interruptionsAnalysees(motifsConnus).forEach((motif, annee) => {
      annees.set(annee, motif);
    });
    return annees;
  }

  /**
   * Le salaire converti tient-il dans ce que le modèle sait décrire ? Le
   * contrôle ne peut se faire qu'ici : « 0,1 à 10 fois le salaire moyen » ne
   * devient un intervalle d'euros qu'une fois la série chargée. Le refus redit
   * donc les bornes en euros, faute de quoi il n'indiquerait pas quoi corriger.
   */
  verifierNiveau(niveau, rang, echelle) {
    if (niveau >= 0.1 && niveau <= 10) {
      return;
    }
    if (!this.revenu_en_euros) {
      throw refus(
        rang, "Niveau de revenu attendu entre 0,1 et 10 fois le salaire moyen.",
      );
    }
    throw refus(
      rang,
      `Ce revenu vaut ${g.nombre(niveau, 2)} fois le salaire moyen ; le `
      + "modèle en accepte de 0,1 à 10 fois, soit de "
      + `${g.nombre(echelle.mensuel(0.1), 0)} à `
      + `${g.euros(echelle.mensuel(10))} bruts par mois.`,
    );
  }

  parametres(base) {
    const regle = avec(base, {
      mode_indexation: ModeIndexation[cleEnum(ModeIndexation, this.indexation)],
      lissage_indexation: this.lissage,
      mode_age_reference: ModeAgeReference[cleEnum(ModeAgeReference, this.age_reference)],
      table_conversion: TableConversion[cleEnum(TableConversion, this.table)],
      population_conversion: this.population === "commune" ? null : this.population,
      rattachement_niveau_de_vie: this.rattachement,
      age_conversion_droits_acquis:
        AgeConversionDroitsAcquis[cleEnum(AgeConversionDroitsAcquis, this.conversion_acquis)],
      part_cotisation: PartCotisation[
        cleEnum(PartCotisation, this.part_cotisation)],
      contribution_etat: ContributionEtat[
        cleEnum(ContributionEtat, this.contribution_etat)],
      situation_foyer: SituationFoyer[cleEnum(SituationFoyer, this.foyer)],
      scenario_projection: this.projection,
      trajectoire_emploi: this.emploi,
      revalorisation_stock: this.stock,
      part_reprise_garantie: this.reprise === null ? null : this.reprise / 100,
      annee_bascule: this.bascule,
      annee_euros_constants: this.euros,
    });
    return sousRegimeTaux(sousRegimeFrais(regle, this.frais), this.taux);
  }

  /**
   * La saisie réduite à ses RÈGLES, pour les pages qui agrègent.
   *
   * Les pages Cas types, Coût et Avantages ne calculent aucune carrière
   * saisie : elles croisent des carrières types avec des générations. Ce
   * qu'elles doivent retenir d'une adresse, ce sont les réglages de
   * modélisation — et eux seuls. Une adresse de simulateur collée sur la page
   * Coût y décrit donc un jeu de règles, jamais un individu : la naissance, le
   * statut et le revenu qu'elle porte sont ignorés, et une faute dans l'un
   * d'eux ne peut pas faire échouer la page.
   */
  static modelisation(parametres) {
    const retenus = {};
    for (const cle of CLES_MODELISATION) {
      if (cle in parametres) { retenus[cle] = parametres[cle]; }
    }
    return Saisie.depuisRequete(retenus);
  }

  /**
   * Les réglages qui s'écartent du défaut, écrits comme une requête.
   *
   * Vide tant que rien n'a été changé : les adresses du site restent alors
   * celles d'avant, au caractère près, et un lien partagé ne porte que ce que
   * son auteur a effectivement réglé.
   */
  requeteModelisation() {
    return CLES_MODELISATION
      .filter((cle) => this[cle] !== DEFAUTS[cle])
      .map((cle) => `${encodeURIComponent(cle).replace(/%20/g, "+")}`
        + `=${encodeURIComponent(String(this[cle])).replace(/%20/g, "+")}`)
      .join("&");
  }

  /**
   * « 1995:1999:education_enfant, 2003:2004:chomage » -> Map année → motif.
   *
   * Trois contrôles s'ajoutent à celui de la forme, parce que les trois fautes
   * qu'ils attrapent étaient muettes.
   *
   * Une plage sans borne bouclait autant de fois qu'elle comptait d'années :
   * « 0:999999999:chomage_indemnise » remplissait la mémoire et figeait
   * l'onglet. Le calcul se fait chez le lecteur, et l'adresse EST la saisie :
   * le lien suffisait donc à figer l'onglet de quelqu'un d'autre. Les années
   * sont désormais tenues dans la fenêtre que n'importe quelle carrière peut
   * couvrir.
   *
   * Une plage à l'envers — « 2004:2003 » — ne décrivait rien : la boucle ne
   * tournait pas, et l'interruption saisie n'existait nulle part.
   *
   * Un motif mal orthographié, enfin, retombait sur `sans_activite` :
   * « educaton_enfant » validait zéro trimestre au lieu de quatre et changeait
   * la pension affichée, sans un mot. Se tromper de touche ne doit pas donner
   * un autre chiffre, mais un refus.
   *
   * `motifsConnus` est la liste que porte le paquet de données. Une saisie ne
   * connaît pas les données : l'appelant la fournit, et le contrôle du motif
   * n'a lieu que s'il l'a fait.
   */
  interruptionsAnalysees(motifsConnus = null) {
    const plages = new Map();
    const connus = motifsConnus === null ? null : [...motifsConnus].sort();
    for (const brut of this.interruptions.replace(/\n/g, ",").split(",")) {
      const morceau = brut.trim();
      if (!morceau) {
        continue;
      }
      const parties = morceau.split(":");
      if (parties.length !== 3 || !estEntier(parties[0]) || !estEntier(parties[1])) {
        throw new ErreurSaisie(
          `Interruption mal formée : « ${morceau} ». Attendu `
          + "« année_début:année_fin:motif », par exemple "
          + "1995:1999:education_enfant.",
        );
      }
      const debut = Number(parties[0]);
      const fin = Number(parties[1]);
      const motif = parties[2].trim();
      // L'année est citée TELLE QU'ELLE A ÉTÉ ÉCRITE, et non relue du nombre :
      // « 999999999999999999999 » s'écrit « 1e+21 » une fois passé par
      // `Number`, et reste un entier côté Python, si bien que les deux moteurs
      // refusaient la même saisie par deux phrases différentes.
      for (const [texte, annee] of [[parties[0], debut], [parties[1], fin]]) {
        if (!(annee >= ANNEE_CARRIERE_MINIMALE && annee <= ANNEE_CARRIERE_MAXIMALE)) {
          throw new ErreurSaisie(
            `Interruption « ${morceau} » : ${texte.trim()} ne tombe dans aucune `
            + `carrière possible. Attendu entre ${ANNEE_CARRIERE_MINIMALE} et `
            + `${ANNEE_CARRIERE_MAXIMALE}.`,
          );
        }
      }
      if (fin < debut) {
        throw new ErreurSaisie(
          `Interruption « ${morceau} » : elle finit (${fin}) avant de `
          + `commencer (${debut}).`,
        );
      }
      if (connus !== null && !connus.includes(motif)) {
        throw new ErreurSaisie(
          `Interruption « ${morceau} » : motif inconnu « ${motif} ». `
          + `Attendu l'un de : ${connus.join(", ")}.`,
        );
      }
      for (let annee = debut; annee <= fin; annee += 1) {
        plages.set(annee, motif);
      }
    }
    return plages;
  }

  /** Vrai si la carrière est LUE plutôt que reconstituée. */
  get releveActif() {
    return this.releve.trim().length > 0;
  }

  /**
   * Le mois où la pension prend effet — la borne du relevé.
   *
   * La même arithmétique que `Carriere.dateLiquidation`, en amont du modèle :
   * le refus d'une année postérieure au départ doit se prononcer sur la saisie,
   * avec le vocabulaire du formulaire, et non remonter du moteur sous la forme
   * d'une exception.
   */
  get dateLiquidation() {
    return this.dateDe(this.liquidation);
  }

  /**
   * « 2005:salarie_prive_non_cadre:24000:4, … » -> lignes de relevé.
   *
   * Le format est celui du relevé lui-même, dans l'ordre où il l'imprime :
   * l'année, le régime, le revenu de l'année, les trimestres qu'elle a validés.
   * Les trois premiers champs sont exigés ; le quatrième est facultatif — sans
   * lui, le modèle déduit les trimestres du montant cotisé, comme il le fait
   * d'une carrière paramétrique.
   *
   * **Le revenu est celui de l'année, en euros de cette année-là**, et non un
   * multiple du salaire moyen ni un montant mensuel : c'est ce que le relevé
   * porte, et l'unité du modèle. Un relevé antérieur à 2002 est en francs, à
   * diviser par 6,55957.
   *
   * **Les années non cotisées** se déclarent dans le champ « Interruptions »,
   * qui reste lu quand un relevé est saisi : il associe une année à un motif,
   * ce que le relevé ne sait pas dire. La ligne de l'année garde alors ses
   * trimestres — le relevé fait foi — et son revenu devient le salaire de
   * référence d'avant l'interruption.
   */
  releveAnalyse(motifsConnus = null) {
    const interruptions = this.interruptionsAnalysees(motifsConnus);
    const depart = this.dateLiquidation;
    // Les lignes sont COMPTÉES avant d'être lues : le refus doit coûter le
    // découpage du texte, et rien de plus. Les analyser d'abord pour les
    // compter ensuite ferait payer au lecteur le relevé de cent mille lignes
    // qu'un lien lui aurait tendu — c'est la faute que les plages
    // d'interruption avaient déjà commise.
    const morceaux = this.releve.replace(/\n/g, ",").replace(/;/g, ",").split(",")
      .map((brut) => brut.trim())
      .filter((brut) => brut.length > 0);
    if (morceaux.length === 0) {
      throw new ErreurSaisie(
        "Relevé de carrière vide : le laisser entièrement vide pour décrire la "
        + "carrière par ses métiers.",
      );
    }
    if (morceaux.length > RELEVE_MAXIMUM) {
      throw new ErreurSaisie(
        `Relevé de ${morceaux.length} lignes : le modèle en accepte `
        + `${RELEVE_MAXIMUM} au plus, ce qu'aucune carrière ne dépasse.`,
      );
    }
    const lignes = [];
    const vues = new Set();
    for (const morceau of morceaux) {
      const parties = morceau.split(":").map((partie) => partie.trim());
      if (parties.length < 3 || parties.length > 4 || !estEntier(parties[0])) {
        throw new ErreurSaisie(
          `Ligne de relevé mal formée : « ${morceau} ». Attendu `
          + "« année:régime:revenu » ou « année:régime:revenu:trimestres », "
          + "par exemple 2005:salarie_prive_non_cadre:24000:4.",
        );
      }
      const annee = Number(parties[0]);
      // L'année est citée TELLE QU'ELLE A ÉTÉ ÉCRITE, comme pour les
      // interruptions : « 999999999999999999999 » s'écrit « 1e+21 » une fois
      // passé par `Number`, et reste un entier côté Python, si bien que les deux
      // moteurs refuseraient la même saisie par deux phrases différentes.
      if (!(annee >= ANNEE_CARRIERE_MINIMALE && annee <= ANNEE_CARRIERE_MAXIMALE)) {
        throw new ErreurSaisie(
          `Relevé « ${morceau} » : ${parties[0]} ne tombe dans aucune carrière `
          + `possible. Attendu entre ${ANNEE_CARRIERE_MINIMALE} et `
          + `${ANNEE_CARRIERE_MAXIMALE}.`,
        );
      }
      if (vues.has(annee)) {
        throw new ErreurSaisie(
          `Relevé : l'année ${annee} est déclarée deux fois. Une année civile `
          + "ne porte qu'une ligne — les régimes liquident à l'année.",
        );
      }
      vues.add(annee);
      if (annee < this.naissance + AGE_DEBUT_MINIMAL) {
        throw new ErreurSaisie(
          `Relevé « ${morceau} » : l'assuré, né en ${this.naissance}, n'a pas `
          + `${AGE_DEBUT_MINIMAL} ans en ${annee}.`,
        );
      }
      if (annee > depart.annee || (annee === depart.annee && depart.mois === 1)) {
        throw new ErreurSaisie(
          `Relevé « ${morceau} » : l'année ${annee} est postérieure au départ `
          + `à la retraite, fixé au ${depart}.`,
        );
      }
      if (!parties[1]) {
        throw new ErreurSaisie(
          `Relevé « ${morceau} » : indiquer le statut d'affiliation.`,
        );
      }
      const revenu = versFlottant(parties[2]);
      if (revenu === null || revenu < 0) {
        throw new ErreurSaisie(
          `Relevé « ${morceau} » : revenu de l'année attendu positif ou nul, `
          + "en euros de cette année-là.",
        );
      }
      let trimestres = null;
      if (parties.length === 4 && parties[3]) {
        if (!estEntier(parties[3])
            || !(Number(parties[3]) >= 0 && Number(parties[3]) <= 4)) {
          throw new ErreurSaisie(
            `Relevé « ${morceau} » : trimestres attendus entre 0 et 4.`,
          );
        }
        trimestres = Number(parties[3]);
      }
      lignes.push({
        annee,
        affiliation: parties[1],
        revenu,
        trimestres,
        type_periode: interruptions.get(annee) ?? "emploi",
      });
    }
    return lignes;
  }

  // -- les dates --------------------------------------------------------------
  //
  // Le formulaire ne demande plus d'âges mais des dates : c'est la même
  // information — un âge est une date rapportée à la naissance —, mais celle
  // que le lecteur connaît sans la calculer. Le modèle, lui, continue de
  // recevoir des âges : la conversion tient dans les méthodes qui suivent, et
  // nulle part ailleurs.

  /** Le mois où la carrière atteint cet âge. */
  dateDe(age_) {
    return new DateMois(this.naissance, this.naissance_mois).plusMois(enMois(age_));
  }

  /** Le même mois, tel que l'adresse le porte : « 1996-09 ». */
  moisDe(age_) {
    const date = this.dateDe(age_);
    return `${cadrer(date.annee, 4)}-${cadrer(date.mois, 2)}`;
  }

  /** Le même mois au premier jour : ce qu'un champ date, lui, exige. */
  jourDe(age_) {
    return `${this.moisDe(age_)}-01`;
  }

  /**
   * « de septembre 1989 à septembre 2015 » : deux bornes d'âge, en dates.
   *
   * Un refus qui ne parlerait que d'âges laisserait au lecteur la soustraction
   * à faire, alors que le champ qu'il vient de remplir porte une date.
   */
  fenetre(ageMinimal, ageMaximal) {
    return `de ${this.dateDe(ageMinimal)} à ${this.dateDe(ageMaximal)}`;
  }

  /** La naissance telle qu'un champ date la porte : « 1975-03-15 ». */
  get naissanceIso() {
    return `${cadrer(this.naissance, 4)}-${cadrer(this.naissance_mois, 2)}`
      + `-${cadrer(this.naissance_jour, 2)}`;
  }

  // -- ce qu'on écrit sous un calendrier ---------------------------------------
  //
  // Un champ date s'affiche dans l'ordre de la langue du NAVIGATEUR, que la page
  // ne choisit pas : « 15/03/1962 » ici, « 03/15/1962 » sur un navigateur
  // anglophone, et rien ne dit lequel des deux nombres est le mois. La date est
  // donc redite en toutes lettres sous le champ, où aucun ordre ne se devine —
  // et, pour une date de carrière, avec l'âge qu'elle fait, qui est ce que le
  // formulaire demandait avant elle.

  /** « le 15 mars 1962 » : la date de naissance, sans ordre à deviner. */
  get naissanceEnClair() {
    return `le ${jourEnClair(this.naissance_jour)} `
      + `${NOMS_DE_MOIS[this.naissance_mois - 1]} ${this.naissance}`;
  }

  /** « en septembre 1984, soit 22 ans et 6 mois » : une date de carrière. */
  calculDe(age_) {
    if (age_ < 0) {
      return `en ${this.dateDe(age_)}, avant la date de naissance`;
    }
    return `en ${this.dateDe(age_)}, soit ${age(age_)}`;
  }

  /**
   * Les naissances déclarées des premiers enfants, dans l'ordre :
   * « 1995, 1998-06 » → `["1995", "1998-06"]`. Une virgule, un point-virgule ou
   * un blanc les sépare.
   */
  naissancesEnfants() {
    return this.naissances.split(/[\s,;]+/).filter((morceau) => morceau);
  }

  /**
   * Pas plus de naissances que d'enfants ; chacune une année ou un mois, après
   * la naissance de l'assuré et avant son départ. Voir `_verifier_naissances`
   * du Python.
   */
  verifierNaissances() {
    const naissances = this.naissancesEnfants();
    if (naissances.length > this.enfants) {
      throw new ErreurSaisie(
        `Naissances des enfants : ${naissances.length} déclarée`
        + `${naissances.length > 1 ? "s" : ""} pour ${this.enfants} enfant`
        + `${this.enfants > 1 ? "s" : ""}.`,
      );
    }
    for (const valeur of naissances) {
      let jour;
      try {
        [jour] = naissanceDeclaree(valeur);
      } catch {
        throw new ErreurSaisie(
          `Naissance d'un enfant « ${valeur} » : attendue en AAAA ou `
          + "AAAA-MM, par exemple 1995 ou 1995-06.",
        );
      }
      if (jour <= this.naissanceIso) {
        throw new ErreurSaisie(
          `Naissance d'un enfant « ${valeur} » : elle précède la vôtre.`,
        );
      }
      if (jour >= this.jourDe(this.liquidation)) {
        throw new ErreurSaisie(
          `Naissance d'un enfant « ${valeur} » : elle suit le départ à la `
          + `retraite, fixé en ${this.dateDe(this.liquidation)}.`,
        );
      }
    }
  }

  requete(remplacements = {}) {
    const naissances = this.naissancesEnfants();
    const champs = {
      naissance: this.naissanceIso,
      sexe: this.sexe, statut: this.statut,
      // Les dates remplacent les âges, et l'adresse y perd trois paramètres :
      // « debut=1996-09 » dit d'un coup ce que « debut=21 » et « debut_mois=8 »
      // disaient à deux, sans que personne ait à refaire l'addition. Une
      // adresse d'ancienne forme reste lue — les âges y sont reconnus tels
      // quels, voir `ageSaisi`.
      debut: this.moisDe(this.debut),
      liquidation: this.moisDe(this.liquidation),
      salaire: nombreBrut(this.salaire), profil: this.profil,
      releve: this.releve,
      primes: nombreBrut(this.primes), enfants: this.enfants,
      ...(naissances.length ? { naissances: naissances.join(",") } : {}),
      interruptions: this.interruptions, indexation: this.indexation,
      lissage: this.lissage,
      age_reference: this.age_reference, table: this.table,
      population: this.population, rattachement: this.rattachement,
      conversion_acquis: this.conversion_acquis,
      part_cotisation: this.part_cotisation,
      contribution_etat: this.contribution_etat,
      foyer: this.foyer,
      projection: this.projection, emploi: this.emploi, stock: this.stock,
      reprise: this.reprise === null ? "" : this.reprise,
      frais: this.frais,
      taux: this.taux,
      bascule: this.bascule, euros: this.euros,
    };
    // L'unité s'écrit TOUJOURS, y compris quand c'est celle par défaut : c'est
    // ce qui distingue une adresse neuve d'une adresse d'avant les euros, dont
    // le « salaire » nu est un multiple du salaire moyen.
    champs.unite_revenu = this.unite_revenu;
    // Le mode s'écrit toujours lui aussi : il gouverne l'interprétation du
    // nombre « salaire », et une adresse partagée qui l'omettrait décrirait une
    // autre carrière que celle qu'on a calculée.
    champs.montants = this.montants;
    // Ce que le formulaire demande s'écrit toujours, pour la même raison : une
    // adresse qui l'omettrait décrirait une saisie par le revenu, et le nombre
    // « pension » n'y servirait plus à rien.
    champs.situation = this.situation;
    champs.saisie_par = this.saisie_par;
    champs.pension = nombreBrut(this.pension);
    // Les métiers qui suivent le premier, un groupe de trois champs chacun. Une
    // ligne vide du formulaire n'en produit aucun : l'adresse ne porte que ce
    // qui a été saisi.
    this.metiers.forEach((metier, index) => {
      const rang = index + 2;
      champs[`metier${rang}_debut`] = this.moisDe(metier.debut);
      champs[`metier${rang}_statut`] = metier.statut;
      champs[`metier${rang}_salaire`] = nombreBrut(metier.salaire);
      if (metier.cumul) {
        champs[`metier${rang}_cumul`] = CUMUL;
        if (metier.fin !== null) {
          champs[`metier${rang}_fin`] = this.moisDe(metier.fin);
        }
      }
    });
    Object.assign(champs, remplacements);
    return Object.entries(champs)
      .map(([cle, valeur]) => `${encodeURIComponent(cle).replace(/%20/g, "+")}`
        + `=${encodeURIComponent(String(valeur)).replace(/%20/g, "+")}`)
      .join("&");
  }
}

/**
 * Les métiers qui suivent le premier, lus dans « metier2_… », « metier3_… ».
 *
 * Le formulaire affiche toujours une ligne de plus qu'il n'y a de métiers : tant
 * qu'elle reste vide, elle ne décrit rien. Une ligne partiellement remplie, en
 * revanche, est une intention manquée — elle est refusée, avec ce qui lui manque.
 */
function metiersSaisis(parametres, salairePrecedent, naissance, naissanceMois,
  tolerante = false) {
  const metiers = [];
  let salaire = salairePrecedent;
  for (let rang = 2; rang <= METIERS_MAXIMUM; rang += 1) {
    const debutBrut = String(parametres[`metier${rang}_debut`] ?? "").trim();
    const statut = String(parametres[`metier${rang}_statut`] ?? "").trim();
    const salaireBrut = String(parametres[`metier${rang}_salaire`] ?? "").trim();
    const cumul = String(parametres[`metier${rang}_cumul`] ?? "").trim();
    const finBrut = String(parametres[`metier${rang}_fin`] ?? "").trim();
    if (!debutBrut && !statut && !salaireBrut && !cumul && !finBrut) {
      continue;
    }
    // Remontrée, la ligne incomplète n'est pas un métier : la lecture s'y
    // arrête, et c'est la ligne vide du formulaire qui la reçoit.
    if (tolerante && (!debutBrut || !statut)) {
      break;
    }
    if (!debutBrut) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : indiquer la date à laquelle il commence, ou `
        + "laisser sa ligne entièrement vide.",
      );
    }
    if (!statut) {
      throw new ErreurSaisie(`Métier n° ${rang} : indiquer le statut d'affiliation.`);
    }
    // Une période sans emploi ne lit pas le champ de revenu : elle hérite de
    // celui d'avant, et la ligne suivante en hérite à son tour. Ce n'est pas ce
    // qu'elle paie — elle ne paie rien — mais le salaire de référence sur
    // lequel l'UNEDIC cotise aux régimes complémentaires.
    const sansEmploi = CODES_SANS_EMPLOI.has(statut);
    // LE CUMUL SE DÉCLARE, et ne se déduit de rien : une activité qui ne dit
    // pas s'ajouter à celle en cours la remplace, comme toujours.
    if (cumul !== "" && cumul !== CUMUL) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : « ${cumul} » n'est pas une réponse possible — `
        + "l'activité remplace la précédente, ou s'y ajoute.",
      );
    }
    if (cumul && sansEmploi) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : une période sans emploi ne s'ajoute pas à une `
        + "activité — elle l'interrompt.",
      );
    }
    if (finBrut && !cumul) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : une date de fin ne se donne qu'à une activité qui `
        + "s'ajoute à celle en cours ; celle qui la remplace s'arrête où "
        + "commence la période suivante.",
      );
    }
    // Une activité ajoutée garde son propre revenu, mais n'en passe pas à la
    // ligne suivante : c'est l'activité principale qu'elle continue.
    let salaireLigne = salaire;
    if (!sansEmploi) {
      salaireLigne = reel(parametres, `metier${rang}_salaire`, salaire);
      if (!cumul) {
        salaire = salaireLigne;
      }
    }
    metiers.push({
      debut: ageSaisi(parametres, `metier${rang}_debut`, 0.0,
        naissance, naissanceMois),
      statut,
      salaire: salaireLigne,
      // Vrai si l'activité S'AJOUTE à celle en cours au lieu de la remplacer.
      cumul: Boolean(cumul),
      // Âge auquel une activité ajoutée s'arrête ; null la mène au départ.
      fin: finBrut
        ? ageSaisi(parametres, `metier${rang}_fin`, 0.0, naissance, naissanceMois)
        : null,
      // Vrai si `statut` est un motif de `SANS_EMPLOI` et non une affiliation.
      // Décidé à la LECTURE, et non déduit plus tard du statut : la première
      // ligne de la carrière n'est jamais une période sans emploi, et
      // « sans_activite » y garde le sens d'affiliation qu'il a toujours eu.
      sans_emploi: sansEmploi,
    });
  }
  return metiers;
}

function cleEnum(enumeration, valeur) {
  const cle = Object.keys(enumeration).find((nom) => enumeration[nom] === valeur);
  if (cle === undefined) {
    throw new ErreurSaisie(`valeur inconnue : ${valeur}`);
  }
  return cle;
}

const NOMBRE = /^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$/;

/**
 * Une date de formulaire ou d'adresse : « 1975-03-15 », ou « 1996-09 » quand le
 * jour ne sert à rien. Rien d'autre n'en est une — un âge nu, « 64 », est une
 * adresse d'avant le calendrier, et se lit comme tel.
 */
const DATE = /^\s*(\d{4})-(\d{2})(?:-(\d{2}))?\s*$/;

/** Un nombre cadré à droite sur autant de chiffres : « 3 » -> « 03 ». */
function cadrer(valeur, chiffres) {
  return String(valeur).padStart(chiffres, "0");
}

/**
 * Le nombre écrit dans ce texte, ou `null` s'il n'y en a pas.
 *
 * L'infini n'en est pas un : « 1e400 » passe l'expression ci-dessus et vaut
 * `Infinity`, que la suite du calcul propage sans jamais échouer — le
 * simulateur affichait « Ce revenu vaut inf fois le salaire moyen ». Il se
 * refuse ici, là où le nombre entre, plutôt qu'à chacun des contrôles qui le
 * liraient ensuite.
 */
function versFlottant(texte) {
  const propre = String(texte).trim();
  if (!NOMBRE.test(propre)) {
    return null;
  }
  const valeur = Number(propre);
  return Number.isFinite(valeur) ? valeur : null;
}

export function estEntier(texte) {
  return /^\s*[+-]?\d+\s*$/.test(String(texte ?? ""));
}

export function entier(parametres, nom, defaut) {
  const valeur = parametres[nom];
  if (valeur === undefined || valeur === null || valeur === "") {
    return defaut;
  }
  const flottant = versFlottant(valeur);
  if (flottant === null) {
    throw new ErreurSaisie(`« ${nom} » doit être un nombre entier (reçu : ${valeur}).`);
  }
  return Math.trunc(flottant);
}

export function reel(parametres, nom, defaut) {
  const valeur = parametres[nom];
  if (valeur === undefined || valeur === null || valeur === "") {
    return defaut;
  }
  const flottant = versFlottant(String(valeur).replace(/,/g, "."));
  if (flottant === null) {
    throw new ErreurSaisie(`« ${nom} » doit être un nombre (reçu : ${valeur}).`);
  }
  return flottant;
}

export function parmi(parametres, nom, options, defaut) {
  const valeur = parametres[nom];
  return options.some(([code]) => code === valeur) ? valeur : defaut;
}

/** Valeur telle qu'elle est réinjectée dans un champ de formulaire. */
export function nombreBrut(valeur) {
  return formatG(valeur);
}

export function jourEnClair(jour) {
  return jour === 1 ? "1er" : String(jour);
}

/**
 * La date écrite dans ce champ, ou `null` s'il n'en porte pas.
 *
 * Le formulaire envoie « 1975-03-15 » : c'est la forme qu'un `<input
 * type="date">` renvoie partout, quelle que soit celle — « 15/03/1975 » en
 * français — sous laquelle le navigateur l'a affichée. L'adresse, elle, s'en
 * tient au mois pour les dates de carrière : « debut=1996-09 », le jour n'y
 * ayant aucun rôle.
 *
 * Une adresse d'avant le calendrier porte des âges et une année nus —
 * « naissance=1975 », « liquidation=64 » : rien ici ne les reconnaît, et `null`
 * renvoie le lecteur aux champs numériques d'alors.
 */
function dateSaisie(parametres, nom) {
  const brut = parametres[nom];
  if (brut === undefined || brut === null || brut === "") {
    return null;
  }
  const trouve = DATE.exec(String(brut));
  if (trouve === null) {
    return null;
  }
  const [annee, mois] = [Number(trouve[1]), Number(trouve[2])];
  const jour = trouve[3] === undefined ? 1 : Number(trouve[3]);
  if (!(mois >= 1 && mois <= 12)) {
    throw new ErreurSaisie(`« ${nom} » : mois attendu entre 01 et 12 (reçu : ${brut}).`);
  }
  // Le jour n'est borné que grossièrement : il ne sert à aucun calcul, et le
  // refuser au calendrier près — un 31 février — n'épargnerait rien à personne,
  // puisque aucun champ date ne le propose.
  if (!(jour >= 1 && jour <= 31)) {
    throw new ErreurSaisie(`« ${nom} » : jour attendu entre 01 et 31 (reçu : ${brut}).`);
  }
  return { annee, mois, jour };
}

/**
 * L'âge qu'une date de carrière vaut, rapportée à la naissance.
 *
 * Le formulaire demande une date — celle du premier mois cotisé, celle du
 * départ —, parce que c'est ce dont on se souvient ; le modèle, lui, ne connaît
 * que des âges. La soustraction se fait ici, en mois, et le résultat est l'âge
 * en années décimales que le moteur attend.
 *
 * Les adresses d'avant le calendrier continuent d'être lues telles quelles :
 * `liquidation=64` et `liquidation_mois=7` valent soixante-quatre ans et sept
 * mois, `liquidation=64.5` vaut ce qu'il a toujours valu.
 */
function ageSaisi(parametres, nom, defaut, naissance, naissanceMois) {
  const date = dateSaisie(parametres, nom);
  if (date !== null) {
    const rang = new DateMois(date.annee, date.mois).rang
      - new DateMois(naissance, naissanceMois).rang;
    return rang / MOIS_PAR_AN;
  }
  const annees = reel(parametres, nom, defaut);
  const cle = `${nom}_mois`;
  const brut = parametres[cle];
  if (brut === undefined || brut === null || brut === "") {
    return annees;
  }
  const mois = entier(parametres, cle, 0);
  if (!(mois >= 0 && mois <= 11)) {
    throw new ErreurSaisie(`« ${cle} » doit être compris entre 0 et 11 mois.`);
  }
  return Math.floor(annees) + mois / 12;
}

/**
 * Âge à la française, en ans et en mois : « 64 ans », « 64 ans et 9 mois ».
 *
 * Le modèle date la liquidation au mois : l'écrire « 64,75 » demanderait au
 * lecteur de multiplier par douze pour retrouver ce qu'il a saisi.
 */
export function age(valeur) {
  return formaterAge(valeur);
}

// -- fabrique ----------------------------------------------------------------

/**
 * L'échelle des salaires d'une année : le repère, et les conversions.
 *
 * Le modèle raisonne en multiples du salaire moyen ; le formulaire, en euros.
 * Tout le passage de l'un à l'autre tient dans cet objet, construit une fois par
 * rendu, pour que la conversion n'existe qu'à un seul endroit et que ce qui
 * s'affiche soit exactement ce qui se calcule.
 */
export class Echelle {
  constructor({ moyen, smic, plafond, versBrut = null, versNet = null,
    versBrutDirect = null }) {
    // Ce qui remonte d'un net mensuel au brut qui le laisse, statut par
    // statut. `versBrut` est nul en mode brut — il n'y a rien à convertir —,
    // les deux autres sont toujours là : la bascule doit traduire quel que
    // soit le mode où l'on se trouve.
    this.versBrut = versBrut;
    this.versNet = versNet;
    this.versBrutDirect = versBrutDirect;
    // Salaire moyen par tête, en euros BRUTS annuels de l'année de référence.
    this.moyen = moyen;
    // SMIC mensuel brut de la même année, sur 151,67 heures.
    this.smic = smic;
    // Plafond mensuel de la Sécurité sociale de la même année.
    this.plafond = plafond;
  }

  /** Un salaire mensuel brut, en multiples du salaire moyen. */
  niveau(eurosMensuels) {
    return (eurosMensuels * MOIS_PAR_AN) / this.moyen;
  }

  /** L'opération inverse : un multiple, en euros bruts par mois. */
  mensuel(niveau) {
    return (niveau * this.moyen) / MOIS_PAR_AN;
  }

  /** Le brut mensuel d'un montant saisi, quel que soit le mode. */
  brutMensuel(montant, statut) {
    if (this.versBrut === null || montant <= 0) {
      return montant;
    }
    return this.versBrut(montant, statut);
  }

  /** Le net vers le brut, quel que soit le mode courant — pour la bascule. */
  brutMensuelDirect(net, statut) {
    if (this.versBrutDirect === null || net <= 0) {
      return net;
    }
    return this.versBrutDirect(net, statut);
  }

  /** Le sens direct : ce qu'un brut mensuel laisse — pour la bascule. */
  netMensuel(brut, statut) {
    if (this.versNet === null || brut <= 0) {
      return brut;
    }
    return this.versNet(brut, statut);
  }

  /**
   * La conversion a-t-elle un effet pour ce statut ? Faux pour un exploitant
   * agricole, un élu, un ultramarin : le modèle n'a pas leurs prélèvements
   * hors retraite, et le nombre saisi est alors lu comme un brut.
   */
  convertit(statut) {
    if (this.versNet === null) {
      return false;
    }
    return this.netMensuel(1000.0, statut) !== 1000.0;
  }
}

/**
 * Un refus, daté du métier qu'il concerne quand il y en a plusieurs. La phrase
 * est écrite une fois, avec sa majuscule ; le rang la fait passer au milieu
 * d'une autre, où la majuscule n'a plus lieu d'être. Écrire les deux versions à
 * la main les laisserait diverger.
 */
export function refus(rang, phrase) {
  if (rang === 1) {
    return new ErreurSaisie(phrase);
  }
  return new ErreurSaisie(
    `Métier n° ${rang} : ${phrase.charAt(0).toLowerCase()}${phrase.slice(1)}`,
  );
}

