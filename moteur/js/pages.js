/**
 * Contenu des pages : formulaire, résultats, cas types, méthode, données.
 *
 * Portage de ``src/retraite_notionnelle/web/pages.py``. Le rendu doit être
 * identique à celui de la référence Python au caractère près : c'est ce que
 * vérifient les témoins de ``tests/temoins/pages.json``.
 */

import {
  MOIS_PAR_AN, NOMS_DE_MOIS, DateMois, enMois, formaterAge, moisTravailles,
} from "./calendrier.js";
import { bornesDeformation, salaireMoyenAnnuel } from "./carriere.js";
import { MATURITES, repartition } from "./capitalisation.js";
import { CourbeTauxSansRisque } from "./taux.js";
import { FAMILLES_STATUT, formaterBorne } from "./regimes.js";
import {
  CAS_TYPES, GENERATIONS, ageLiquidationPour, calculerCasTypes,
} from "./castypes.js";
import {
  AgeConversionDroitsAcquis, ModeAgeReference, ModeIndexation, PARAMETRES_DEFAUT, PartCotisation,
  SituationFoyer, TableConversion, avec, cleParametres,
  tauxCapitalisationApplique, tauxCapitalisationVolontaireApplique,
  tauxRetraitePropose,
  sousRegimeFrais,
} from "./config.js";
import { AssietteActivite } from "./assiette.js";
import {
  LIBELLES_MOTIFS, LIGNES_LUES, MOTIFS, NEUTRALISATIONS, calculerAvantages,
  chargerAvantages,
} from "./avantages.js";
import {
  COMPOSANTE_GARANTIE,
  SCENARIOS,
  calculerCout,
  calculerDette,
  masseDuScenario,
} from "./cout.js";
import { DistributionPensions } from "./distribution.js";
import { coutGarantie } from "./garantie.js";
import { SYSTEMES, DepensesRetraite } from "./depenses.js";
import {
  GROUPES,
  ORGANISMES,
  POSTES,
  POSTES_TRANSFERTS,
  ComptesRetraite,
} from "./equilibre.js";
import { Indexation } from "./indexation.js";
import { Population } from "./population.js";
import { echapper, formatFixe, formatG } from "./format.js";
import * as g from "./gabarit.js";
import { nomFiabilite } from "./serie.js";
import { salaireBrutDepuisNet, salaireNetDepuisBrut } from "./remuneration.js";
import { Simulateur } from "./simulateur.js";

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
  ["fixe_apres_bascule", "64 ans à partir de la bascule (défaut)"],
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

// Précision du multiple du salaire moyen, en décimales et en pas. Les deux
// doivent rester d'accord : le lien de bascule écrit un multiple arrondi à
// DECIMALES_MULTIPLE, et un navigateur refuse de soumettre un nombre qui ne
// tombe pas sur le `step` déclaré par le champ. Le millième n'est pas gratuit :
// il vaut trois euros cinquante par mois, ce qui borne la fidélité d'un
// aller-retour entre les deux unités — au centième, l'écart atteignait vingt
// euros.
export const DECIMALES_MULTIPLE = 3;
export const PAS_MULTIPLE = 10 ** -DECIMALES_MULTIPLE;

// Décimales des coefficients qui font une CHAÎNE DE CALCUL affichée : le
// diviseur de conversion, le coefficient de revalorisation, le rendement
// cumulé. Elles ne sont pas décoratives — elles sont mesurées, et mesurées SUR
// LES VALEURS AFFICHÉES : calibrées sur les valeurs exactes du modèle, elles
// paraissaient suffire une décimale plus tôt, parce que la mesure ignorait
// l'arrondi des lignes que le lecteur, lui, a sous les yeux.
//
// Écart maximal de la ligne reconstituée, sur cinquante-deux carrières :
//
//                       4 déc.    5 déc.    6 déc.
//   a) × diviseur       2,70 €    0,57 €    0,57 €
//   capital ÷ diviseur  0,10 €    0,02 €    0,02 €
//   b) × revalorisation 62,27 €   6,47 €    1,23 €
//   cotisations × rendt 50,92 €   5,09 €    1,07 €
//
// Au-delà, le gain s'arrête : ce qui reste vient de ce que les capitaux
// s'affichent à l'euro, ce qui borne toute reconstitution à un demi-euro par
// terme, et cette borne-là ne se rachète pas par des décimales.
export const DECIMALES_DIVISEUR = 5;
export const DECIMALES_FACTEUR = 6;

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
 * Nombre de lignes qu'un relevé de carrière peut porter. Une carrière tient
 * entre quatorze ans — l'âge de début minimal — et soixante-quinze, soit
 * soixante et une années civiles au plus ; la borne laisse deux lignes de marge
 * et ferme surtout la porte que les interruptions avaient ouverte : le calcul
 * se fait chez le lecteur et l'adresse EST la saisie, si bien qu'un relevé de
 * cent mille lignes forgé dans un lien figeait l'onglet de celui qui le suivait.
 */
export const RELEVE_MAXIMUM = 63;

/**
 * Âge auquel s'arrête la trajectoire individuelle. Les tables de mortalité du
 * modèle vont jusqu'à 120 ans : ce n'est pas la table qui s'arrête tôt, c'est
 * la MOYENNE par laquelle le capital notionnel est divisé. Un graphique qui
 * s'arrêterait à cette moyenne cacherait justement ce qu'il doit montrer — que
 * la moitié d'une génération lui survit. À 105 ans, le modèle donne encore une
 * personne sur dix vivante parmi celles parties à 64 ans : la borne n'est pas
 * une fantaisie, elle est le bout de la distribution, pas son milieu.
 */
export const AGE_MAXIMUM_TRAJECTOIRE = 105;

/**
 * Les six courbes : attribut du modèle, variable CSS de couleur — la même que
 * la barre du haut, pour qu'une couleur désigne partout le même scénario — et
 * le chiffre posé au bout de la courbe. Ce chiffre n'est pas décoratif : la
 * palette à quatre systèmes tient le contrôle de séparation daltonienne, ce
 * (pire paire voisine : ΔE 4,3 sous deutéranopie), et six courbes qui se
 * croisent ne peuvent pas être identifiées par la couleur seule.
 */
/**
 * LES QUATRE SYSTÈMES QUE LE SITE COMPARE, dans l'ordre où il les montre.
 *
 * Le modèle en calcule six et continue de le faire : ses deux variantes
 * « dès la bascule » restent dans `Comparaison` et dans `cout.SCENARIOS`.
 * Elles ne sont plus MONTRÉES — le site ne pose plus la question à laquelle
 * elles répondaient. Copie de `SCENARIOS_MONTRES` dans `web/pages.py`.
 */
export const SCENARIOS_MONTRES = [
  "actuel",
  "notionnel_retroactif",
  "notionnel_retroactif_employeur",
  "notionnel_liberal",
];

/**
 * Le libellé de chaque système partout où le site le NOMME. La nomenclature du
 * modèle, elle, ne bouge pas : `cout.SCENARIOS` numérote toujours de 1 à 6.
 * Copie de `LIBELLES_SYSTEMES` dans `web/pages.py`.
 */
const LIBELLES_SYSTEMES = {
  actuel: "1. Système de répartition actuel",
  notionnel_retroactif: "2. Compte notionnel, part salariale",
  notionnel_retroactif_employeur: "3. Compte notionnel, les deux parts",
  notionnel_liberal: "4. La proposition libérale",
};

/** Les mêmes, appariés et dans l'ordre. */
const SCENARIOS_COMPARES = SCENARIOS_MONTRES.map(
  (scenario) => [scenario, LIBELLES_SYSTEMES[scenario]],
);

/**
 * Les quatre courbes : attribut du modèle, variable CSS de couleur, et le
 * chiffre posé au bout de la courbe.
 */
export const TRAJECTOIRE = [
  ["actuel", "--actuel", "1"],
  ["notionnel_retroactif", "--retroactif", "2"],
  ["notionnel_retroactif_employeur", "--retroactif-employeur", "3"],
  ["notionnel_liberal", "--liberal", "4"],
];

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
// L'année où le routage commence : la première période de tout statut. Un
// statut dont le régime naît plus tard le dit dans le menu — « (depuis
// 1977) » —, celui de 1930 n'a rien à dater.
export const ANNEE_MODELE = 1930;
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

/** Rang de chaque métier, tel que le formulaire l'annonce. */
export const RANGS_METIER = ["premier", "deuxième", "troisième", "quatrième",
  "cinquième", "sixième", "septième", "huitième"];

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
 * l'UNEDIC ou la Sécurité sociale, AVPF. Un test vérifie qu'aucun code d'ici
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

/** Le libellé d'un motif, pour le résumé de carrière. */
const LIBELLES_SANS_EMPLOI = Object.fromEntries(SANS_EMPLOI);

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
  "rattachement", "conversion_acquis", "part_cotisation", "foyer",
  "projection", "emploi", "stock", "reprise", "frais", "bascule", "euros",
]);

const DEFAUTS = Object.freeze({
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
  interruptions: "",
  indexation: "masse_salariale",
  lissage: 1,
  age_reference: "fixe_apres_bascule",
  table: "unisexe",
  population: "niveau_de_vie",
  rattachement: "salaire",
  conversion_acquis: "reference",
  part_cotisation: "salariale",
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

  static depuisRequete(parametres) {
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
    const naissance = dateSaisie(parametres, "naissance");
    const anneeNaissance = naissance
      ? naissance.annee : entier(parametres, "naissance", DEFAUTS.naissance);
    const moisNaissance = naissance
      ? naissance.mois : entier(parametres, "naissance_mois", DEFAUTS.naissance_mois);
    const saisie = new Saisie({
      unite_revenu: unite,
      montants: parmi(parametres, "montants", MODES_MONTANT, DEFAUTS.montants),
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
      metiers: metiersSaisis(parametres, salaire, anneeNaissance, moisNaissance),
      releve: (parametres.releve || "").trim(),
      profil: parmi(parametres, "profil", PROFILS, DEFAUTS.profil),
      primes: reel(parametres, "primes", DEFAUTS.primes),
      enfants: entier(parametres, "enfants", DEFAUTS.enfants),
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
      foyer: parmi(parametres, "foyer", SITUATIONS_FOYER, DEFAUTS.foyer),
      projection: parmi(parametres, "projection", PROJECTIONS, DEFAUTS.projection),
      emploi: parmi(parametres, "emploi", TRAJECTOIRES_EMPLOI, DEFAUTS.emploi),
      stock: parmi(parametres, "stock", REVALORISATIONS_STOCK, DEFAUTS.stock),
      reprise: entier(parametres, "reprise", DEFAUTS.reprise),
      frais: parmi(parametres, "frais", REGIMES_FRAIS, DEFAUTS.frais),
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
    saisie.verifier();
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
    // Les métiers se suivent sans se recouvrir : chacun commence après le
    // précédent et avant le départ à la retraite.
    let precedent = this.debut;
    this.metiers.forEach((metier, index) => {
      const rang = index + 2;
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
        sans_emploi: false,
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
      const cloture = index + 1 < lignes.length
        ? this.dateDe(lignes[index + 1].debut) : fin;
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
      situation_foyer: SituationFoyer[cleEnum(SituationFoyer, this.foyer)],
      scenario_projection: this.projection,
      trajectoire_emploi: this.emploi,
      revalorisation_stock: this.stock,
      part_reprise_garantie: this.reprise === null ? null : this.reprise / 100,
      annee_bascule: this.bascule,
      annee_euros_constants: this.euros,
    });
    return sousRegimeFrais(regle, this.frais);
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

  requete(remplacements = {}) {
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
      interruptions: this.interruptions, indexation: this.indexation,
      lissage: this.lissage,
      age_reference: this.age_reference, table: this.table,
      population: this.population, rattachement: this.rattachement,
      conversion_acquis: this.conversion_acquis,
      part_cotisation: this.part_cotisation,
      foyer: this.foyer,
      projection: this.projection, emploi: this.emploi, stock: this.stock,
      reprise: this.reprise === null ? "" : this.reprise,
      frais: this.frais,
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
    // Les métiers qui suivent le premier, un groupe de trois champs chacun. Une
    // ligne vide du formulaire n'en produit aucun : l'adresse ne porte que ce
    // qui a été saisi.
    this.metiers.forEach((metier, index) => {
      const rang = index + 2;
      champs[`metier${rang}_debut`] = this.moisDe(metier.debut);
      champs[`metier${rang}_statut`] = metier.statut;
      champs[`metier${rang}_salaire`] = nombreBrut(metier.salaire);
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
function metiersSaisis(parametres, salairePrecedent, naissance, naissanceMois) {
  const metiers = [];
  let salaire = salairePrecedent;
  for (let rang = 2; rang <= METIERS_MAXIMUM; rang += 1) {
    const debutBrut = String(parametres[`metier${rang}_debut`] ?? "").trim();
    const statut = String(parametres[`metier${rang}_statut`] ?? "").trim();
    const salaireBrut = String(parametres[`metier${rang}_salaire`] ?? "").trim();
    if (!debutBrut && !statut && !salaireBrut) {
      continue;
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
    if (!sansEmploi) {
      salaire = reel(parametres, `metier${rang}_salaire`, salaire);
    }
    metiers.push({
      debut: ageSaisi(parametres, `metier${rang}_debut`, 0.0,
        naissance, naissanceMois),
      statut,
      salaire,
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

function estEntier(texte) {
  return /^\s*[+-]?\d+\s*$/.test(String(texte ?? ""));
}

function entier(parametres, nom, defaut) {
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

function reel(parametres, nom, defaut) {
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

function parmi(parametres, nom, options, defaut) {
  const valeur = parametres[nom];
  return options.some(([code]) => code === valeur) ? valeur : defaut;
}

/** Valeur telle qu'elle est réinjectée dans un champ de formulaire. */
function nombreBrut(valeur) {
  return formatG(valeur);
}

/** Le premier du mois est un ORDINAL en français : « 1er », et non « 1 ». */
/** « 2026-09-13 » -> « 13 septembre 2026 », la date telle qu'on la lit. */
function dateEnClair(iso) {
  const [annee, mois, jour] = iso.split("-").map(Number);
  return `${jourEnClair(jour)} ${NOMS_DE_MOIS[mois - 1]} ${annee}`;
}

function jourEnClair(jour) {
  return jour === 1 ? "1er" : String(jour);
}

/**
 * Ce que `round(valeur, decimales)` fait en Python : l'arrondi au pair, sur le
 * développement décimal exact du flottant. `Math.round` monterait les demis,
 * là où Python les envoie au chiffre pair — et le rendu des deux moteurs est
 * comparé caractère par caractère.
 */
function arrondir(valeur, decimales) {
  return Number(formatFixe(valeur, decimales));
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
// Ce que le COR projette pour le système actuel, en part du PIB : le repère
// extérieur auquel la page se compare. Rapport annuel de juin 2025, champ
// « ensemble des régimes légalement obligatoires, y compris FSV, hors RAFP ».
const COR_2024 = 0.139;
const COR_2070 = 0.142;

function age(valeur) {
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
 * Combien d'agrégats le contexte garde en mémoire, tous jeux de règles
 * confondus. Deux par jeu — le coût et les avantages —, donc trois jeux de
 * règles : celui par défaut, et les deux derniers essayés.
 */
const AGREGATS_MEMORISES = 6;

/**
 * Les données du site, et le jeu de règles sous lequel on les lit.
 *
 * Un contexte, c'est deux choses : des données coûteuses à charger, et UN jeu
 * de paramètres — `base` — sous lequel tout ce que la page demande est
 * calculé. `simulateur()`, `cout()` et `avantages()` répondent tous trois sous
 * ce jeu-là, sans qu'aucune page ait à le leur redire.
 *
 * Les trois pages qui AGRÈGENT — Cas types, Coût, Avantages — se rendent donc
 * sous un contexte dérivé par `pour`, portant les réglages que l'adresse
 * demande. Le corps des pages n'en sait rien : il lit `contexte.base` comme il
 * l'a toujours fait, et y trouve les règles en vigueur au lieu des règles par
 * défaut. C'est ce qui évite de faire passer un jeu de paramètres à la main
 * dans la trentaine d'endroits qui les lisent.
 *
 * Les mémoires sont des `Map` partagées, et c'est ce qui fait tenir la
 * dérivation : un contexte dérivé PARTAGE ce que le contexte d'origine a déjà
 * chargé. Le chargement des données coûte quelques dixièmes de seconde, une
 * simulation en coûte dix, un agrégat une seconde : rien de tout cela ne doit
 * se refaire parce qu'on a changé une règle.
 */
export class Contexte {
  constructor(paquet, base = PARAMETRES_DEFAUT, memoires = null) {
    this.paquet = paquet;
    this.base = base;
    // Un simulateur par jeu de paramètres rencontré.
    this._instances = memoires ? memoires.instances : new Map();
    // Ce qui ne dépend d'AUCUN paramètre : dépense observée, comptes du COR,
    // population, distribution des pensions, assiette, inventaire des
    // avantages. Ces séries sont lues, jamais calculées : un changement de
    // règle ne les déplace pas.
    this._donnees = memoires ? memoires.donnees : new Map();
    // Les agrégats, eux, dépendent des règles : un coût par jeu de paramètres.
    this._agregats = memoires ? memoires.agregats : new Map();
  }

  /**
   * Le même contexte, sous un autre jeu de règles.
   *
   * Les mémoires sont partagées, pas recopiées : dériver ne coûte rien, et ce
   * que l'un charge, l'autre le trouve chargé.
   */
  pour(parametres) {
    if (cleParametres(parametres) === cleParametres(this.base)) { return this; }
    return new Contexte(this.paquet, parametres, {
      instances: this._instances,
      donnees: this._donnees,
      agregats: this._agregats,
    });
  }

  /** Une donnée indépendante des règles, chargée une fois pour toutes. */
  _donnee(nom, fabrique) {
    if (!this._donnees.has(nom)) {
      this._donnees.set(nom, fabrique());
    }
    return this._donnees.get(nom);
  }

  /**
   * Un agrégat, mémorisé par jeu de règles — et en nombre borné.
   *
   * Sans borne, une adresse suffirait à faire enfler la mémoire de l'onglet
   * d'un jeu de règles à l'autre : le calcul se fait chez le lecteur, et
   * l'adresse EST la saisie. Le plus ancien s'en va ; revenir aux réglages par
   * défaut après en avoir essayé trois recalcule, une seconde.
   */
  _agregat(nom, fabrique) {
    const cle = `${nom}|${cleParametres(this.base)}`;
    if (!this._agregats.has(cle)) {
      if (this._agregats.size >= AGREGATS_MEMORISES) {
        this._agregats.delete(this._agregats.keys().next().value);
      }
      this._agregats.set(cle, fabrique());
    }
    return this._agregats.get(cle);
  }

  simulateur(parametres = null) {
    const retenus = parametres || this.base;
    const cle = cleParametres(retenus);
    if (!this._instances.has(cle)) {
      this._instances.set(cle, new Simulateur(this.paquet, retenus));
    }
    return this._instances.get(cle);
  }

  depenses() {
    return this._donnee("depenses", () => new DepensesRetraite(this.paquet));
  }

  /** Le second terme du bilan : ce que le système de retraite encaisse. */
  comptes() {
    return this._donnee("comptes", () => new ComptesRetraite(this.paquet));
  }

  population() {
    return this._donnee("population", () => new Population(this.paquet));
  }

  /** La distribution des pensions — elle seule chiffre un plancher. */
  distribution() {
    return this._donnee("distribution", () => new DistributionPensions(this.paquet));
  }

  /** Sur quoi l'on prélève : sans elle, un taux ne se convertit pas en recette. */
  assiette() {
    return this._donnee("assiette", () => new AssietteActivite(this.paquet));
  }

  /** L'inventaire des avantages non contributifs — une donnée, pas un calcul. */
  inventaireAvantages() {
    return this._donnee("inventaireAvantages", () => chargerAvantages(this.paquet));
  }

  /** Ce que les avantages non contributifs coûtent — une seconde, une fois. */
  avantages() {
    return this._agregat("avantages", () => calculerAvantages(
      this.simulateur(), this.depenses(), this.population(),
    ));
  }

  /**
   * Le coût agrégé de tous les systèmes — une seconde de calcul, une fois.
   *
   * Sous les règles de `base`, et non sous celles par défaut : c'est ce qui
   * fait que la page Coût chiffre ce que le simulateur calcule.
   */
  cout() {
    return this._agregat("cout", () => calculerCout(
      this.simulateur(), this.depenses(), this.population(), this.comptes(),
      undefined, undefined, undefined, this.assiette(),
    ));
  }

  /**
   * L'échelle des salaires de l'année courante, pour cette saisie. L'année est
   * celle du modèle — on saisit un salaire d'aujourd'hui —, et les séries sont
   * CELLES DE LA SAISIE : au-delà de la dernière année observée, le salaire
   * moyen dépend du scénario de projection choisi.
   */
  echelle(saisie) {
    const parametres = saisie.parametres(this.base);
    const macro = this.simulateur(parametres).macro;
    const annee = parametres.annee_courante;
    const simulateur = this.simulateur(parametres);
    const bareme = simulateur.baremePrelevements;
    const versBrut = (netMensuel, statut) => salaireBrutDepuisNet(
      bareme, macro, simulateur.catalogue, simulateur.affiliations,
      statut, annee, netMensuel * MOIS_PAR_AN,
    ) / MOIS_PAR_AN;
    const versNet = (brutMensuel, statut) => salaireNetDepuisBrut(
      bareme, macro, simulateur.catalogue, simulateur.affiliations,
      statut, annee, brutMensuel * MOIS_PAR_AN,
    ) / MOIS_PAR_AN;
    return new Echelle({
      moyen: salaireMoyenAnnuel(macro, annee),
      smic: HEURES_SMIC_PAR_MOIS * macro.smic_horaire.valeur(annee),
      plafond: macro.plafond_securite_sociale.valeur(annee) / MOIS_PAR_AN,
      versBrut: saisie.saisieEnNet ? versBrut : null,
      versNet,
      versBrutDirect: versBrut,
    });
  }

  simuler(saisie) {
    const simulateur = this.simulateur(saisie.parametres(this.base));
    // Les motifs viennent des données, pas d'une liste écrite ici : le moteur y
    // lit ce que chaque période ouvre, et une saisie refusée doit l'être sur la
    // même table que celle qui calcule.
    const motifs = Object.keys(this.paquet.periodes_non_travaillees ?? {});
    if (saisie.releveActif) {
      return simulateur.simuler(this.carriereRelevee(simulateur, saisie, motifs));
    }
    const parcours = saisie.parcours(this.echelle(saisie));
    for (const metier of parcours) {
      if (!simulateur.affiliations.contient(metier.affiliation)) {
        throw new ErreurSaisie(
          `Statut d'affiliation inconnu : « ${metier.affiliation} ».`,
        );
      }
    }
    const carriere = simulateur.carriereParcours({
      annee_naissance: saisie.naissance,
      mois_naissance: saisie.naissance_mois,
      sexe: saisie.sexe,
      metiers: parcours,
      age_liquidation: saisie.liquidation,
      profil_carriere: saisie.profil,
      interruptions: saisie.interruptionsDeCarriere(motifs),
      nombre_enfants: saisie.enfants,
      part_primes: saisie.primes,
      identifiant: "assuré",
    });
    verifierStatutsOuverts(simulateur.affiliations, carriere, parcours);
    return simulateur.simuler(carriere);
  }

  /**
   * La carrière telle que le relevé la donne, sans rien reconstituer.
   *
   * Aucune échelle des salaires n'intervient : le relevé est déjà en euros de
   * chaque année, quand le formulaire paramétrique saisit un revenu
   * d'aujourd'hui que le modèle promène ensuite le long du salaire moyen. C'est
   * ce qui fait de ce chemin le plus exact — et le seul où l'euro n'est pas
   * converti.
   */
  carriereRelevee(simulateur, saisie, motifs) {
    const releve = saisie.releveAnalyse(motifs);
    for (const ligne of releve) {
      if (!simulateur.affiliations.contient(ligne.affiliation)) {
        throw new ErreurSaisie(
          `Relevé, année ${ligne.annee} : statut d'affiliation inconnu `
          + `« ${ligne.affiliation} ».`,
        );
      }
    }
    const carriere = simulateur.carriereReleve({
      annee_naissance: saisie.naissance,
      mois_naissance: saisie.naissance_mois,
      sexe: saisie.sexe,
      releve,
      age_liquidation: saisie.liquidation,
      nombre_enfants: saisie.enfants,
      part_primes: saisie.primes,
      identifiant: "assuré",
    });
    verifierStatutsReleve(simulateur.affiliations, carriere);
    return carriere;
  }
}

/** Titre de chaque page, dans l'ordre de la navigation. */
/**
 * La description de chaque page, pour la balise `<meta name="description">`
 * que le routeur d'`index.html` réécrit à chaque rendu. Copie de
 * `DESCRIPTIONS` dans `web/pages.py`.
 */
export const DESCRIPTIONS = {
  "/": "Le programme du Parti libéral français pour les retraites : un régime "
    + "unique en comptes notionnels, un taux de 18 % pour tous, une garantie "
    + "vieillesse individualisée — et le simulateur qui le chiffre, carrière "
    + "par carrière, dans votre navigateur.",
  "/simuler": "Votre carrière calculée de quatre façons : le système actuel, et "
    + "les comptes notionnels appliqués depuis 1941 ou à partir de la "
    + "bascule. Tout se calcule dans votre navigateur, rien n'est envoyé.",
  "/trajectoire": "Ce que chaque système aura versé, du départ à 105 ans : "
    + "le cumul, et non la pension d'un mois — c'est là que la "
    + "durée de la retraite entre dans le calcul.",
  "/cas-types": "Treize carrières types sur sept générations : ce que chaque "
    + "pension deviendrait, par rapport à aujourd'hui, sous la "
    + "proposition et sous quatre contrefactuels.",
  "/cout": "Ce que la retraite coûte, d'où vient l'argent, et ce qui manque, "
    + "de 1959 à 2070 — et ce que chacun des quatre systèmes coûterait.",
  "/avantages": "Tous les avantages non contributifs du système actuel : "
    + "lesquels, depuis quand, et ce que le modèle sait en chiffrer.",
  "/methode": "Comment une pension en comptes notionnels se calcule, en trois "
    + "opérations, et pourquoi la règle de revalorisation décide de "
    + "presque tout.",
  "/donnees": "D'où viennent les chiffres du site, série par série et régime "
    + "par régime, et ce qui a été recontrôlé contre sa source.",
  "/partager": "Les chiffres du programme au format des réseaux sociaux, "
    + "1200 × 675, en filigrane @pliberal : le plancher, le taux, "
    + "le déficit, et l'appel au simulateur.",
};

export const TITRES = {
  "/": "Programme",
  "/simuler": "Simuler",
  "/trajectoire": "Trajectoire",
  "/cas-types": "Cas types",
  "/cout": "Coût",
  "/avantages": "Avantages",
  "/methode": "Méthode",
  "/donnees": "Données",
  "/partager": "Partager",
};

/**
 * Contenu d'une page : ``[titre, corps HTML]``. Les erreurs de saisie sont
 * rendues dans la page, jamais levées : une adresse mal formée doit afficher un
 * message, pas une trace d'exécution.
 *
 * `/simuler` et `/trajectoire` lisent `parametres` en entier : ce sont les deux
 * pages que l'adresse paramètre carrière comprise, et elles portent le même
 * formulaire. Les trois pages qui AGRÈGENT — Cas types, Coût, Avantages — n'en
 * lisent que les RÈGLES, et se calculent sous elles. Toute adresse inconnue
 * retombe sur l'accueil.
 *
 * C'est ici, et nulle part ailleurs, que les réglages sont posés pour les liens
 * de la page à venir : `rendre` est le point d'entrée unique du rendu, et les y
 * poser à chaque appel — fût-ce à vide — garantit qu'aucune page n'hérite des
 * réglages de la précédente.
 */
export function rendre(contexte, chemin, parametres = null) {
  const requete = parametres || {};
  let regles;
  let refus = "";
  try {
    regles = Saisie.modelisation(requete);
  } catch (erreur) {
    if (fauteDeProgramme(erreur)) throw erreur;
    // Un réglage hors bornes ne doit pas emporter la page : elle se rend sous
    // les règles par défaut, précédée de la phrase qui dit pourquoi.
    regles = new Saisie();
    refus = messageErreur(erreur.message);
  }
  g.poserOptions(regles.requeteModelisation());

  if (chemin === "/trajectoire") {
    return [TITRES[chemin], refus + pageTrajectoire(contexte, requete)];
  }
  if (chemin === "/partager") {
    return [TITRES[chemin], partager(contexte)];
  }
  if (chemin in PAGES_AGREGEES) {
    return [TITRES[chemin], refus + agregee(chemin, contexte, regles)];
  }
  if (chemin === "/methode") {
    return [TITRES[chemin], methode(contexte)];
  }
  if (chemin === "/donnees") {
    return [TITRES[chemin], donnees(contexte)];
  }
  if (chemin !== "/simuler") {
    return [TITRES["/"], programme(contexte)];
  }

  let saisie;
  try {
    saisie = Saisie.depuisRequete(requete);
  } catch (erreur) {
    if (!(erreur instanceof ErreurSaisie)) {
      throw erreur;
    }
    // Le formulaire repart de ses valeurs par défaut — c'est ce qui permet de
    // le réafficher quoi qu'ait porté l'adresse —, mais il garde l'unité de
    // saisie : sans cela, une faute de frappe sur l'année de naissance
    // renverrait en euros quelqu'un qui raisonnait en multiples, avec des
    // nombres de l'autre unité sous les yeux.
    const unite = parmi(requete, "unite_revenu", UNITES_REVENU,
      DEFAUTS.unite_revenu);
    // La saisie de repli sert au chapeau ET au formulaire : « saisie » est
    // resté indéfini, la construction ayant échoué.
    saisie = new Saisie({
      demandee: false, unite_revenu: unite, salaire: SALAIRE_DEFAUT[unite],
    });
    return [TITRES["/simuler"],
      messageErreur(erreur.message) + formulaire(saisie, contexte)];
  }

  let corps = formulaire(saisie, contexte);
  if (saisie.demandee) {
    try {
      corps += resultats(contexte, saisie);
    } catch (erreur) {
      // Saisie refusée, données insuffisantes, régime inconnu : le message est
      // rendu dans la page. Une adresse mal formée doit afficher une phrase,
      // pas une trace d'exécution. Une faute de programme, elle, n'est pas une
      // faute de saisie et ne doit pas être présentée comme telle.
      if (fauteDeProgramme(erreur)) throw erreur;
      corps += messageErreur(erreur.message);
    }
  }
  return [TITRES["/simuler"], corps];
}

/**
 * Une page qui agrège, calculée sous les règles que l'adresse demande.
 *
 * Le corps de la page n'en sait rien : il reçoit un contexte DÉRIVÉ, dont
 * `base` porte ces règles, et lit `contexte.base`, `contexte.cout()` ou
 * `contexte.simulateur()` comme il l'a toujours fait. C'est le contexte qui
 * sait sous quelles règles on l'interroge, et non chacune des trente lignes qui
 * l'interrogent.
 */
/**
 * Les trois pages qui AGRÈGENT : elles ne calculent aucune carrière saisie,
 * mais elles obéissent aux mêmes règles que le simulateur. Voir `agregee`.
 */
const PAGES_AGREGEES = {
  "/cas-types": casTypes,
  "/cout": cout,
  "/avantages": avantages,
};

function agregee(chemin, contexte, saisie) {
  return avertissementReglages(saisie, chemin)
    + PAGES_AGREGEES[chemin](contexte.pour(saisie.parametres(contexte.base)))
    + reglages(saisie, chemin);
}

/**
 * Un statut ne se déclare qu'aux dates où son régime recrutait.
 *
 * Un jeune d'aujourd'hui ne peut pas se déclarer mineur : le régime des mines
 * est fermé aux recrutés depuis septembre 2010. Le routage le savait déjà —
 * il envoyait ce mineur-là au régime général, en silence, et la page
 * affichait « Mineur » au-dessus d'une pension de salarié du privé. Le refus
 * dit la date, et le statut de droit commun qui porte le même calcul.
 *
 * La date opposée est celle de l'ENTRÉE dans le statut, au mois près, telle
 * que le parcours l'a datée : un agent entré à la RATP en octobre 2022 n'y a
 * sa première ligne qu'en 2023, et n'est pas recruté après la fermeture pour
 * autant.
 */
function verifierStatutsOuverts(affiliations, carriere, parcours) {
  parcours.forEach((metier, index) => {
    const ferme = statutFerme(affiliations, carriere, metier.affiliation);
    if (ferme === null) {
      return;
    }
    const [fermeture, entree] = ferme;
    throw refus(index + 1, phraseStatutFerme(
      affiliations, metier.affiliation, fermeture,
      `ce métier commence en ${entree}`,
    ));
  });
}

/**
 * Le même refus, opposé à un relevé de carrière.
 *
 * Le relevé ne compte pas de métiers : il porte des ANNÉES, dont chacune nomme
 * son statut. La date opposée à la fermeture est donc la première année
 * déclarée sous ce statut — janvier, faute d'un mois que le relevé ne donne
 * pas —, et la phrase le dit plutôt que de parler d'un « métier n° 2 » qui
 * n'existe nulle part sur la page.
 */
function verifierStatutsReleve(affiliations, carriere) {
  for (const code of carriere.affiliationsUtilisees()) {
    const ferme = statutFerme(affiliations, carriere, code);
    if (ferme === null) {
      continue;
    }
    const [fermeture, entree] = ferme;
    throw new ErreurSaisie(phraseStatutFerme(
      affiliations, code, fermeture,
      `la première année déclarée sous ce statut est ${entree.annee}`,
    ));
  }
}

/** `[fermeture, entrée]` si ce statut se déclare trop tard, sinon `null`. */
function statutFerme(affiliations, carriere, code) {
  const fermeture = affiliations.fermetureEntrants(code);
  if (fermeture === null) {
    return null;
  }
  const entree = carriere.dateEntree(code);
  if (entree === null || entree.rang < fermeture.rang) {
    return null;
  }
  return [fermeture, entree];
}

/**
 * Le refus, écrit une fois pour les deux formes de saisie. `quand` est la seule
 * chose qui les sépare : un métier commence à un mois, une ligne de relevé n'a
 * qu'une année. Écrire les deux phrases en entier les laisserait diverger.
 */
function phraseStatutFerme(affiliations, code, fermeture, quand) {
  const releve = affiliations.relevePar(code);
  return `Le statut « ${affiliations.libelle(code)} » est `
    + `fermé aux recrutés depuis ${formaterBorne(fermeture)} ; ${quand}. `
    + `Depuis cette date, il relève des mêmes régimes que `
    + `« ${affiliations.libelle(releve)} » : choisir ce statut.`;
}

/**
 * Le libellé d'un statut, et les dates entre lesquelles il se déclare :
 * « (depuis 1977) » pour un régime né après 1930, l'année où le modèle
 * commence ; « (recrutés avant septembre 2010) » pour un régime fermé.
 */
function libelleDate(affiliations, code) {
  const libelle = affiliations.libelle(code);
  const ouverture = affiliations.ouverture(code);
  const fermeture = affiliations.fermetureEntrants(code);
  const precisions = [];
  if (ouverture > ANNEE_MODELE) {
    precisions.push(`depuis ${ouverture}`);
  }
  if (fermeture !== null) {
    precisions.push(`recrutés avant ${formaterBorne(fermeture)}`);
  }
  if (precisions.length === 0) {
    return libelle;
  }
  return `${libelle} (${precisions.join(", ")})`;
}

/**
 * Les statuts du menu, ceux que la date d'entrée ferme désactivés. `entree`
 * est le mois où la période commence ; sans lui — la ligne vide du
 * formulaire —, tout est proposé. Chaque option fermée porte sa date en
 * `data-fermeture` : c'est ce que la page lit, dans le navigateur, pour
 * refaire ce tri quand la date de naissance ou celle du début change sous ses
 * yeux, sans attendre le calcul.
 *
 * `sansEmploi` ajoute, à la suite des métiers, les motifs de `SANS_EMPLOI` :
 * ce sont les lignes qui ne décrivent pas un emploi. La première ligne ne les
 * reçoit pas — une carrière commence quand on commence à travailler —, et
 * aucune date ne les ferme : on peut être au chômage en 1950 comme en 2050.
 */
function optionsStatuts(affiliations, entree, sansEmploi = false) {
  // Les statuts sont rendus PAR FAMILLE — un `<optgroup>` par valeur de
  // FAMILLES_STATUT, dans l'ordre de cette table — : soixante-deux options à
  // la file ne se parcourent pas. Les périodes sans emploi forment le
  // dernier groupe.
  const parFamille = Object.fromEntries(
    Object.keys(FAMILLES_STATUT).map((famille) => [famille, []]),
  );
  for (const code of affiliations.codes) {
    // « Sans activité professionnelle » est une affiliation, mais c'est la même
    // chose que le motif du même nom : elle rejoint le groupe plutôt que d'y
    // figurer deux fois, sous deux libellés, pour le même résultat.
    if (sansEmploi && CODES_SANS_EMPLOI.has(code)) {
      continue;
    }
    const fermeture = affiliations.fermetureEntrants(code);
    const disponible = entree === null || fermeture === null
      || entree.rang < fermeture.rang;
    const attributs = fermeture === null
      ? {}
      : { "data-fermeture": `${fermeture.annee}-${String(fermeture.mois).padStart(2, "0")}` };
    parFamille[affiliations.famille(code)].push(
      [code, libelleDate(affiliations, code), disponible, attributs],
    );
  }
  const groupes = Object.entries(FAMILLES_STATUT)
    .filter(([famille]) => parFamille[famille].length)
    .map(([famille, libelle]) => [libelle, parFamille[famille]]);
  if (sansEmploi) {
    groupes.push(["Sans emploi", SANS_EMPLOI.map(([code, libelle]) => [code, libelle])]);
  }
  return groupes;
}

function borneTexte(date) {
  return date === null ? null : `${date.annee}-${String(date.mois).padStart(2, "0")}`;
}

export function statuts(contexte) {
  const affiliations = contexte.simulateur().affiliations;
  return affiliations.codes.map((code) => ({
    code,
    libelle: affiliations.libelle(code),
    ouverture: affiliations.ouverture(code),
    fermeture_entrants: borneTexte(affiliations.fermetureEntrants(code)),
    releve_par: affiliations.relevePar(code),
  }));
}

// -- fragments ---------------------------------------------------------------

/**
 * Vrai si l'exception est une faute de PROGRAMME, non une faute de saisie.
 *
 * Le portage attrapait tout et affichait « Saisie refusée » : un TypeError du
 * moteur accusait donc le lecteur d'une erreur qui n'était pas la sienne — et
 * un bug du portage passait pour une adresse mal formée. Le Python de
 * référence, lui, ne nomme dans son « except » que les fautes prévues :
 * ErreurSaisie, DonneeInsuffisante, KeyError, ValueError. Les exceptions
 * ci-dessous sont l'équivalent JavaScript de ce que Python ne rattrape pas ;
 * elles remontent jusqu'à index.html, qui dit « Le calcul a échoué » et en
 * montre le détail, sans mettre la faute sur personne.
 */
function fauteDeProgramme(erreur) {
  return erreur instanceof TypeError
    || erreur instanceof ReferenceError
    || erreur instanceof RangeError
    || erreur instanceof SyntaxError;
}

function messageErreur(message) {
  return `<div class="erreur"><strong>Saisie refusée.</strong> ${echapper(message)}</div>`;
}

/**
 * Ce que le simulateur calcule, et ce que ses nombres sont.
 *
 * Deux conventions gouvernent tout ce que la page affiche, et le lecteur ne
 * peut deviner ni l'une ni l'autre : le moteur ne calcule que la pension du
 * PREMIER mois de retraite, et il l'écrit dans deux unités. Elles se disent ici
 * en deux paragraphes séparés, un par convention — les mêler en un seul les
 * rendait indémêlables.
 *
 * Le mot « aujourd'hui » n'y paraît qu'une fois, et pour la date. Il servait
 * aussi pour l'unité, et la page enchaînait « jamais la pension d'aujourd'hui »
 * et « en euros d'aujourd'hui » à une phrase d'intervalle : deux sens du même
 * mot dans un paragraphe qui prétendait lever une confusion.
 *
 * Les deux années citées sont celles de la saisie, et non des constantes
 * écrites dans le texte : le chapeau annonçait « à compter de 2026 » quand le
 * scénario 3 était calculé, à la demande du lecteur, à compter de 2035.
 */
/**
 * Ce que le simulateur calcule, sous le titre du formulaire.
 *
 * C'était un chapeau, un encadré et un dépliant — quatre-vingt-dix mots avant
 * le premier champ. Or on vient ici remplir des champs : tout ce qui s'y
 * interpose est du temps pris à quelqu'un qui a déjà décidé, et rien de ce qui
 * était écrit là n'est nécessaire pour remplir le formulaire. Ce qui compte
 * n'est pas perdu pour autant — il s'ouvre sous le point d'interrogation, et
 * les réserves qui pèsent sur un chiffre sont répétées à côté de ce chiffre, là
 * où elles servent.
 */
function bulleDuTitre(saisie) {
  return g.bulle(
    "Ce que ce formulaire calcule",
    "Votre carrière, calculée de quatre façons : le système actuel, et les "
    + `<a href="${g.lien("/")}">comptes notionnels</a> — appliqués depuis 1941, `
    + `ou à partir de ${saisie.bascule}. Tout se calcule dans votre navigateur : `
    + "rien n'est envoyé nulle part.",
  );
}

/**
 * Ce qu'une ligne de carrière peut décrire, sous le titre de la section.
 *
 * Deux paragraphes tenaient là ce que la section montre déjà : des lignes qu'on
 * remplit. Ce qui ne se voit pas — qu'une ligne peut n'être pas un emploi, et
 * que la dernière dit alors quand l'activité s'arrête — est la seule chose qui
 * méritait d'être écrite, et elle est ici.
 */
function bulleDesPeriodes() {
  return g.bulle(
    "Ce qu'une période peut être",
    "Un métier : chaque changement fait passer d'un régime à un autre, donc "
    + "d'un taux et d'un barème à un autre. Ou une période <strong>sans "
    + "emploi</strong> — chômage, maladie, élever un enfant, rien du tout —, "
    + "qui ne demande pas de revenu : c'est celui d'avant qui sert de "
    + "référence là où le droit ouvre malgré tout des points. La dernière "
    + "ligne dit donc aussi quand l'activité s'arrête, si elle s'arrête avant "
    + "le départ : sans elle, le calcul suppose qu'on a travaillé jusqu'au "
    + "dernier mois.",
  );
}

/**
 * Le nom de chaque réglage en français, et la liste où lire le libellé de sa
 * valeur quand elle en a un. Elle sert à DIRE ce que la page a fait : « la
 * page a été calculée sous d'autres règles » n'apprend rien si l'on ne dit pas
 * lesquelles.
 */
const LIBELLES_MODELISATION = Object.freeze({
  indexation: ["règle d'indexation", INDEXATIONS],
  lissage: ["lissage de l'indexation, en années", null],
  age_reference: ["âge de référence", AGES_REFERENCE],
  table: ["table de conversion", TABLES],
  population: ["population de la table de conversion", POPULATIONS],
  rattachement: ["rattachement au niveau de vie", RATTACHEMENTS],
  conversion_acquis: ["âge de conversion des droits acquis", CONVERSIONS_ACQUIS],
  part_cotisation: ["part de la cotisation portée au compte", PARTS_COTISATION],
  foyer: ["situation de foyer", SITUATIONS_FOYER],
  projection: ["scénario macroéconomique", PROJECTIONS],
  emploi: ["emploi projeté", TRAJECTOIRES_EMPLOI],
  stock: ["pensions en cours à la bascule", REVALORISATIONS_STOCK],
  reprise: ["part de l'avance couverte par la succession", null],
  frais: ["frais du pilier capitalisé", REGIMES_FRAIS],
  bascule: ["année de bascule", null],
  euros: ["euros constants de", null],
});

/** Ce que le lecteur a changé, écrit en toutes lettres. */
function reglagesEnClair(saisie) {
  const dits = [];
  for (const cle of CLES_MODELISATION) {
    const valeur = saisie[cle];
    if (valeur === DEFAUTS[cle]) { continue; }
    const [nom, choix] = LIBELLES_MODELISATION[cle];
    const trouve = choix
      ? (choix.find(([code]) => code === valeur) || [null, String(valeur)])[1]
      : String(valeur);
    dits.push(`${nom} : ${trouve}`);
  }
  return dits.join(" ; ");
}

/**
 * Un encadré, en tête de page, dès que les chiffres ne sont plus ceux du défaut.
 *
 * Sans lui, une adresse partagée afficherait des chiffres qui ne sont pas ceux
 * du site sans que rien ne le dise — exactement la faute que cette page
 * reproche au reste du débat public. Il ne paraît que si quelque chose a été
 * changé : tant que tout est au défaut, la page est celle d'avant, au
 * caractère près.
 */
function avertissementReglages(saisie, chemin) {
  if (!saisie.requeteModelisation()) { return ""; }
  return `<div class="encadre">
<p><strong>Ces chiffres ne sont pas ceux des réglages par défaut.</strong>
La page a été calculée sous les règles que vous avez choisies —
${echapper(reglagesEnClair(saisie))}. Tous les liens du site les emportent
tant que vous ne les remettez pas :
<a href="${g.route(chemin)}">revenir aux réglages par défaut</a>.</p>
</div>`;
}

/**
 * Les règles du calcul, et de quoi les changer sans quitter la page.
 *
 * C'est le même jeu de champs que les options du simulateur, et c'est le même
 * code qui les écrit : une page qui agrège et une page qui simule ne peuvent
 * pas proposer deux jeux de règles différents.
 *
 * Le formulaire vise la ROUTE et non le lien — voir `gabarit.route` : il écrit
 * lui-même sa requête, à partir de ses champs.
 */
function reglages(saisie, chemin) {
  // Les deux réglages sans champ voyagent cachés : le formulaire les perdrait,
  // et une adresse qui les portait se retrouverait silencieusement ramenée au
  // défaut au premier « Recalculer ».
  const caches = ["age_reference", "conversion_acquis"]
    .filter((cle) => saisie[cle] !== DEFAUTS[cle])
    .map((cle) => g.cache(cle, String(saisie[cle])))
    .join("");
  const change = Boolean(saisie.requeteModelisation());
  return `
<details class="section options reglages"${change ? " open" : ""}>
  ${g.sommaire("Les règles du calcul (indexation, projection, bascule…)")}
  <p class="discret">Cette page croise des carrières types avec des
  générations : elle ne calcule aucune carrière saisie. Mais elle obéit aux
  mêmes règles que le simulateur, et ces règles se changent ici. La page est
  recalculée, et l'adresse les emporte vers les autres pages.</p>
  <form class="carte" method="get" action="${g.route(chemin)}">
    ${caches}
    <div class="grille">${champsModelisation(saisie)}</div>
    <p style="margin-top:1.4rem"><button type="submit">Recalculer cette page</button></p>
  </form>
</details>
`;
}

/**
 * Les huit réglages qui décrivent les RÈGLES, et non la carrière.
 *
 * Ils sont écrits ici une fois, et servent deux fois : dans les options du
 * simulateur, et dans le bloc de réglages des trois pages agrégées. Les écrire
 * deux fois aurait suffi à les faire diverger — un libellé ici, une borne là —,
 * et deux pages du même site auraient alors proposé deux jeux de règles qui
 * n'en sont qu'un.
 *
 * Les deux réglages restants — l'âge de référence et l'âge de conversion des
 * droits acquis — n'ont jamais eu de champ : ils ne se règlent que par
 * l'adresse. Le bloc de réglages les emporte en champs cachés pour ne pas les
 * perdre au passage du formulaire.
 */
function champsModelisation(saisie) {
  return [
    g.liste("indexation", "Règle d'indexation", INDEXATIONS, saisie.indexation,
      "revalorisation des comptes et des pensions", {},
      g.GLOSSAIRE["indexation"]),
    g.champ("lissage", "Lissage de l'indexation", saisie.lissage,
      "en années : 1 = aucun",
      "number", { min: "1", max: String(LISSAGE_MAXIMUM), step: "1" },
      "Une moyenne glissante appliquée à la règle choisie, quelle qu'elle "
      + "soit : 5 ans, c'est la fenêtre italienne."),
    g.liste("table", "Table de conversion", TABLES, saisie.table,
      "", {}, g.GLOSSAIRE["table de conversion"]),
    g.liste("population", "Population de la table", POPULATIONS, saisie.population,
      "", {}, "Par défaut, le diviseur suit la mortalité du vingtile de niveau "
      + "de vie où votre salaire vous place, d'après les tables de l'INSEE : "
      + "les 5 % les plus aisés vivent sept ans de plus à 65 ans que les 5 % "
      + "les plus modestes chez les hommes, et une table commune le leur "
      + "transférerait. « Population générale » revient à cette table "
      + "commune ; les autres imposent une population."),
    g.liste("rattachement", "Rattachement au niveau de vie", RATTACHEMENTS,
      saisie.rattachement,
      "", {}, "Ce qui vous place dans un vingtile : votre salaire rapporté au "
      + "salaire moyen, ou le rang de votre pension parmi les retraités, dans "
      + "la distribution de la DREES. Par la pension, le vingtile dépend de la "
      + "pension qui dépend du diviseur : le modèle itère jusqu'au point fixe."),
    g.liste("part_cotisation", "Part de la cotisation portée au compte",
      PARTS_COTISATION, saisie.part_cotisation,
      "salariale seule, ou salariale et patronale", {},
      g.GLOSSAIRE["part patronale"]),
    g.liste("foyer", "Situation de foyer",
      SITUATIONS_FOYER, saisie.foyer,
      "la proposition libérale seulement", {},
      "Elle ne joue que sur l'allocation d'isolement de la garantie "
      + "vieillesse : 1 050 € par mois pour qui vit seul, 800 € par personne "
      + "à deux."),
    g.liste("projection", "Scénario macroéconomique", PROJECTIONS, saisie.projection,
      "au-delà de la dernière observation"),
    g.liste("emploi", "Emploi projeté", TRAJECTOIRES_EMPLOI, saisie.emploi,
      "systèmes 2 à 6 seulement", {},
      "Au-delà de la dernière observation, la masse des salaires, qui est le "
      + "rendement des comptes notionnels, est le salaire moyen composé avec "
      + "l'emploi. Par défaut, l'emploi suit le scénario de référence du COR "
      + "de juin 2026 : chômage ramené à 7 % en 2040, population active en "
      + "hausse jusque vers 2040 puis en recul. Le système 1 n'en lit rien : "
      + "il revalorise sur les prix."),
    g.liste("stock", "Pensions en cours à la bascule", REVALORISATIONS_STOCK,
      saisie.stock, "page Coût seulement", {},
      "Ce que la réforme fait des pensions déjà servies le jour où elle "
      + "s'applique. Par défaut elles gardent l'indice des prix que le droit "
      + "leur promet, et seuls les comptes ouverts sous le nouveau régime "
      + "suivent sa règle : personne ne reçoit un demi-point par an qu'il n'a "
      + "pas cotisé. En variante, la réforme réindexe tout le stock sur la "
      + "règle du compte, comme les réformes réelles l'ont fait pour les prix "
      + "en 1987 : c'est la bosse de 2026-2040 sur la page Coût, le stock "
      + "recevant alors un demi-point par an que personne n'a cotisé, et rien "
      + "ne change à l'horizon, où ce stock est éteint. Le système 1 n'est "
      + "pas concerné : il est le droit."),
    g.champ("reprise", "Part de l'avance couverte par la succession",
      saisie.reprise === null ? "" : saisie.reprise,
      "page Coût seulement, en pour cent ; vide : calculée", "number",
      { min: "0", max: "100" },
      "La garantie du système 4 est une avance reprise sur la succession, dès le premier euro et avec intérêts. Ce que les successions en rendent dépend du patrimoine des bénéficiaires. Vide, la part est calculée sur le patrimoine des ménages retraités selon leur revenu (COR, enquête Patrimoine 2018) : les plus petites pensions au quart le plus modeste, les autres à l'ensemble des retraités. Un nombre remplace ce calcul : zéro éteint la reprise, cent suppose que toute avance est remboursée."),
    g.liste("frais", "Frais du pilier capitalisé", REGIMES_FRAIS, saisie.frais,
      "système 4 seulement", {},
      "Ce que l'enveloppe du pilier prélève, et comment cela bouge. Par "
      + "défaut, les vraies moyennes du marché du PER en 2025 (1,09 % sur "
      + "versement, 0,76 % par an sur l'encours, 0,99 % sur arrérages, 0,52 % "
      + "par an sur la réserve de la rente), qui baissent ensuite par paliers "
      + "comme partout où une épargne retraite obligatoire a mis les gérants "
      + "sous plafond ou en concurrence ; chaque versement entre au tarif de "
      + "son année et le stock ne rejoint le tarif du jour que de 10 % de "
      + "l'écart par an. « Plafond » fait suivre tout le stock d'un coup, "
      + "« contrats » lui fait garder son tarif ; « sans baisse » fige 2025 ; "
      + "« PER vendu » est l'ancien réglage, aux 2,20 % d'arrérages des seuls "
      + "assureurs qui facturent. La page Méthode et les limites disent d'où "
      + "viennent les paliers."),
    g.champ("bascule", "Année de bascule", saisie.bascule,
      "passage au régime unique", "number",
      { min: String(ANNEE_MINIMALE), max: String(ANNEE_MAXIMALE) }),
    g.champ("euros", "Euros constants de", saisie.euros,
      "l'année dont les montants prennent le pouvoir d'achat", "number",
      { min: String(ANNEE_MINIMALE), max: String(ANNEE_MAXIMALE) }),
  ].join("");
}

function formulaire(saisie, contexte) {
  const affiliations = contexte.simulateur().affiliations;
  const echelle = contexte.echelle(saisie);

  // Trois champs là où il en fallait cinq : une date de naissance porte son
  // mois, une date de départ porte l'âge qu'on écrivait en deux fois. Les
  // bornes des calendriers sont celles du modèle, comptées depuis la naissance
  // saisie ; le script de la page les refait à chaque frappe, sans attendre le
  // calcul.
  const identite = [
    // `autocomplete` n'est pas là pour épargner une frappe : il donne au
    // navigateur — et aux outils qui s'appuient sur lui, dont les aides à la
    // saisie — le moyen de reconnaître ce que le champ demande.
    g.champDate("naissance", "Date de naissance", saisie.naissanceIso,
      "seul le mois compte", saisie.naissanceEnClair,
      {
        min: `${NAISSANCE_MINIMALE}-01-01`, max: `${NAISSANCE_MAXIMALE}-12-31`,
        autocomplete: "bday",
      },
      "Le calcul n'en retient que le mois : c'est la maille du droit, qui coupe "
      + "deux générations en cours d'année — au 1<sup>er</sup> juillet 1951 et "
      + "au 1<sup>er</sup> septembre 1961."),
    g.champDate("liquidation", "Départ à la retraite",
      saisie.jourDe(saisie.liquidation),
      "effectif, ou souhaité",
      saisie.calculDe(saisie.liquidation),
      {
        min: saisie.jourDe(AGE_LIQUIDATION_MINIMAL),
        max: saisie.jourDe(AGE_LIQUIDATION_MAXIMAL),
        data_age_min: String(AGE_LIQUIDATION_MINIMAL),
        data_age_max: String(AGE_LIQUIDATION_MAXIMAL),
      },
      "C'est la date à laquelle tout le calcul se place. La pension prend effet "
      + "le premier du mois, et c'est celle du premier mois que vous "
      + "obtiendrez — jamais ce qu'elle devient ensuite."),
  ].join("");

  const avance = [
    // Le sexe ne change RIEN par défaut : la table de conversion est unisexe,
    // et les majorations pour enfants — les seules du système 1 qui
    // distinguent le père de la mère — ne jouent qu'à partir d'un enfant. Or
    // ces deux réglages sont ici. Le champ les rejoint : il est sans effet tant
    // qu'on n'y a pas touché, et à côté d'eux dès qu'on y touche.
    g.liste("sexe", "Sexe", [["H", "Homme"], ["F", "Femme"]], saisie.sexe,
      "sans effet par défaut", { autocomplete: "sex" },
      "Il ne compte que de deux façons, toutes deux réglées ici : si la table "
      + "de conversion est « par sexe », et si la carrière porte des enfants — "
      + "le système actuel réserve à la mère la majoration de durée "
      + "d'assurance."),
    g.liste("profil", "Profil de carrière", PROFILS, saisie.profil,
      aideProfil(contexte.paquet, saisie.profil, saisie.statut)),
    g.champ("primes", "Part de primes", nombreBrut(saisie.primes),
      "fonction publique : assiette du RAFP", "number",
      { min: "0", max: "0.6", step: "0.01" }),
    g.champ("enfants", "Nombre d'enfants", saisie.enfants,
      "sans effet notionnel : les majorations sont supprimées", "number",
      { min: "0", max: String(ENFANTS_MAXIMUM), step: "1" }),
    g.champ("interruptions", "Interruptions", saisie.interruptions,
      "« 1995:1999:education_enfant », séparées par des virgules"),
  ].join("") + champsModelisation(saisie);

  const tete = g.affiche(
    "Le simulateur",
    "Votre carrière, calculée "
    + '<span class="cle-texte">quatre fois.</span>',
    "Le système actuel, les comptes notionnels appliqués depuis 1941 ou à "
    + "partir de la bascule, et notre proposition. Tout se calcule dans "
    + "votre navigateur : rien n'est envoyé, rien n'est conservé.",
  );
  return tete + `
<form class="carte" method="get" action="${g.route("/simuler")}">
  ${g.cache("unite_revenu", saisie.unite_revenu)}
  ${g.cache("montants", saisie.montants)}
  <h2 class="serif" style="margin-top:0">Votre carrière${bulleDuTitre(saisie)}</h2>
  <p style="margin-top:0.3rem">L'exemple est déjà rempli. Calculez-le tel
  quel, ou saisissez la vôtre.</p>
  <div class="grille">${identite}</div>
  <h3>La carrière, période par période${bulleDesPeriodes()}</h3>
  ${metiersFormulaire(saisie, affiliations, echelle)}
  ${basculeUnite(saisie, echelle)}
  ${basculeMontants(saisie, echelle)}
  ${mentionConversion(saisie, echelle)}
  ${releveFormulaire(saisie)}
  <details class="options">
    ${g.sommaire("Options de modélisation (sexe, profil, indexation, "
      + "projection)")}
    <div class="grille">${avance}</div>
  </details>
  <p style="margin-top:1.4rem"><button type="submit">Calculer les quatre systèmes</button></p>
</form>
`;
}

/**
 * Les trois premières lignes d'un relevé, montrées dans le formulaire. Elles
 * disent le format mieux qu'une phrase : une année, un statut, ce qui a été
 * gagné cette année-là, et les trimestres que le relevé porte en face.
 */
export const EXEMPLE_RELEVE = "1998:salarie_prive_non_cadre:14200:4\n"
  + "1999:salarie_prive_non_cadre:15100:4\n"
  + "2000:salarie_prive_cadre:19800:4";

/**
 * Le relevé de carrière : la saisie exacte, celle qui ne suppose rien.
 *
 * Elle est repliée sous un dépliant, et non offerte d'emblée : la carrière
 * paramétrique reste la porte d'entrée — on la remplit en trente secondes, sans
 * rien avoir sous les yeux. Le relevé, lui, demande d'avoir ouvert son compte
 * Info-Retraite, et il s'adresse à qui veut confronter le simulateur à SON
 * estimation plutôt qu'à une carrière type. Le dépliant s'ouvre de lui-même
 * quand un relevé est saisi : sinon, l'adresse porterait une carrière que la
 * page ne montrerait pas.
 */
function releveFormulaire(saisie) {
  const bulle = g.bulle(
    "Ce que le relevé remplace, et comment il se lit",
    "Sans les trimestres, le modèle les déduit du montant. Le revenu est celui "
    + "de l'année entière, en euros de cette année-là ; un relevé antérieur à "
    + "2002 est en francs, à diviser par 6,55957. Les codes de régime sont ceux "
    + "du menu ci-dessus. Rempli, ce champ <strong>remplace</strong> les "
    + "métiers, le profil et le niveau de revenu : rien n'est plus reconstitué. "
    + "Naissance, date de départ, enfants, primes et interruptions continuent "
    + "de valoir.",
  );
  return `
<details class="releve"${saisie.releveActif ? " open" : ""}>
  ${g.sommaire("Coller un relevé de carrière — la saisie exacte")}
  <p class="discret">Une ligne par année : <strong>année:régime:revenu</strong>,
  et <strong>:trimestres</strong> si le relevé les porte.${bulle}</p>
  ${g.zone("releve", "Relevé de carrière", saisie.releve,
    `au plus ${RELEVE_MAXIMUM} lignes ; vide, la carrière est celle des `
    + "métiers ci-dessus", 10,
    { placeholder: EXEMPLE_RELEVE, spellcheck: "false" })}
</details>
`;
}

/**
 * Un refus, daté du métier qu'il concerne quand il y en a plusieurs. La phrase
 * est écrite une fois, avec sa majuscule ; le rang la fait passer au milieu
 * d'une autre, où la majuscule n'a plus lieu d'être. Écrire les deux versions à
 * la main les laisserait diverger.
 */
function refus(rang, phrase) {
  if (rang === 1) {
    return new ErreurSaisie(phrase);
  }
  return new ErreurSaisie(
    `Métier n° ${rang} : ${phrase.charAt(0).toLowerCase()}${phrase.slice(1)}`,
  );
}

/**
 * Le champ « combien gagnez-vous », dans l'unité choisie. Le libellé porte le
 * mot « brut » et l'aide dit où le lire : c'est la question qui revenait le plus
 * souvent devant ce formulaire, et elle se règle là, sur le champ, plutôt que
 * dans un encadré qu'on lit après avoir répondu.
 */
function champRevenu(nom, saisie, echelle, valeur, bref = false) {
  if (!saisie.revenu_en_euros) {
    const aideMultiple = bref
      ? "en multiples du salaire moyen brut"
      : `1 = salaire moyen, soit ${g.euros(echelle.mensuel(1))} bruts par mois`;
    return g.champ(nom, "Niveau de revenu", valeur, aideMultiple, "number",
      { min: "0.1", max: "10", step: nombreBrut(PAS_MULTIPLE) },
      bref ? ""
        : "Le modèle raisonne en multiples du salaire moyen par tête : c'est "
          + "l'unité qui garde son sens sur quatre-vingts ans, quand un montant "
          + "n'en a que rapporté à son année.");
  }
  // « Revenu » et non « salaire » : douze des vingt-deux statuts ne sont pas
  // salariés, et un artisan n'a ni salaire ni fiche de paie. Le brut garde le
  // même sens pour lui — ce sur quoi ses cotisations sont assises —, et la
  // fiche de paie n'est plus donnée que comme l'exemple qu'elle est.
  // Le libellé suit la bascule : demander un « revenu brut » sous un réglage
  // qui annonce le net ferait taper l'un pour l'autre. Les repères chiffrés —
  // SMIC, salaire moyen — sont bruts par nature et sont convertis eux
  // aussi, ou laissés tels quels quand on ne sait pas les convertir. Le
  // plafond de la Sécurité sociale n'en fait plus partie : sous un champ
  // numérique, « plafond 4 005 € » se lit comme le maximum que le champ
  // accepte, et c'est ainsi qu'un lecteur l'a lu.
  const enNet = saisie.saisieEnNet;
  const mot = enNet ? "net" : "brut";
  // Le statut dont le dépôt n'a pas les prélèvements hors retraite : le nombre
  // y est lu tel quel. L'aide doit le dire ELLE AUSSI, et non promettre une
  // conversion que l'avertissement voisin viendra démentir.
  const converti = enNet && echelle.convertit(saisie.statut);
  const repere = converti
    ? ((montant) => echelle.netMensuel(montant, saisie.statut))
    : ((montant) => montant);
  const aide = bref
    ? `en euros ${mot}s par mois`
    : `Repères : SMIC ${g.euros(repere(echelle.smic))}, salaire moyen `
      + `${g.euros(repere(echelle.mensuel(1)))}`;
  let complement;
  if (converti) {
    complement = "En euros d'aujourd'hui, tels qu'ils arrivent sur le compte — "
      + "pour un salarié, la ligne « net à payer » de la fiche de paie. Le "
      + "modèle remonte au brut par les prélèvements de votre statut, puis le "
      + "suit le long du salaire moyen, année après année.";
  } else if (enNet) {
    complement = "En euros d'aujourd'hui. Le modèle n'a pas les prélèvements "
      + "hors retraite de ce statut : il ne peut pas remonter au brut, et lit "
      + "donc le nombre tel quel, puis le suit le long du salaire moyen, "
      + "année après année.";
  } else {
    complement = "En euros d'aujourd'hui, avant cotisations et impôt — pour un "
      + "salarié, la ligne « brut » de la fiche de paie. Le modèle le suit "
      + "ensuite le long du salaire moyen, année après année.";
  }
  return g.champ(nom, `Revenu ${mot} mensuel`, valeur, aide, "number",
    { min: "0", step: "1" }, bref ? "" : complement);
}

/**
 * Ce que le profil fait du salaire saisi, en toutes lettres. Sans elle, saisir
 * « 2 900 € par mois » se lit comme la promesse de gagner 2 900 € chaque année
 * de sa vie, alors que le revenu saisi est celui du milieu de carrière et que
 * le profil le déforme aux deux bouts.
 */
function aideProfil(paquet, profil, affiliation = null) {
  const [debut, fin] = bornesDeformation(paquet, profil, affiliation);
  if (debut === fin) {
    return "le revenu saisi vaut pour toutes les années de la carrière";
  }
  return `le revenu saisi est celui du milieu de carrière : ×${g.nombre(debut, 2)} `
    + `au premier emploi, ×${g.nombre(fin, 2)} après une carrière complète`;
}

/**
 * Le lien qui change l'unité de saisie, montants déjà convertis.
 *
 * Un lien, et non un menu : un formulaire HTML ne convertit rien quand on change
 * un menu, si bien que le nombre resterait celui de l'ancienne unité —
 * « 3 500 » deviendrait 3 500 fois le salaire moyen, et la page refuserait la
 * saisie au lieu de la traduire. Le lien, lui, porte l'adresse complète, unité
 * ET montants déjà traduits : la page revient dans l'autre unité en décrivant
 * exactement la même carrière. C'est la façon dont tout le reste du site
 * navigue, et elle ne demande pas une ligne de JavaScript.
 *
 * L'unité vaut pour toute la carrière : une unité par métier n'aurait décrit
 * aucune carrière réelle, et aurait posé six fois la même question.
 */
function basculeUnite(saisie, echelle) {
  const versLesEuros = !saisie.revenu_en_euros;
  const autre = versLesEuros ? "euros_mois" : "moyen";
  // `niveaux` ramène les montants à l'unité du modèle quelle que soit celle de
  // la saisie : la traduction dans l'autre sens part donc toujours de là.
  const valeurs = saisie.niveaux(echelle).map((niveau) => nombreBrut(
    versLesEuros ? arrondir(echelle.mensuel(niveau), 0)
      : arrondir(niveau, DECIMALES_MULTIPLE),
  ));
  const remplacements = { unite_revenu: autre, salaire: valeurs[0] };
  valeurs.slice(1).forEach((valeur, index) => {
    remplacements[`metier${index + 2}_salaire`] = valeur;
  });
  const cible = `#/simuler?${echapper(saisie.requete(remplacements))}`;
  // Le MÊME composant que la bascule des montants, juste au-dessus d'elle :
  // deux réglages de même nature n'avaient pas la même forme, et l'un des deux
  // ne se voyait pas.
  const euros = "€ par mois";
  const multiple = "× salaire moyen";
  const branches = versLesEuros
    ? [[euros, cible], [multiple, "#"]]
    : [[euros, "#"], [multiple, cible]];
  return g.bascule("Unité", branches, versLesEuros ? multiple : euros);
}

/**
 * Une ligne par période, plus une ligne vide pour en ajouter une.
 *
 * C'est ce qui permet d'allonger la carrière sans une ligne de JavaScript : la
 * ligne vide est renvoyée avec le reste du formulaire, et devient une période
 * dès qu'on la remplit. Une ligne de plus apparaît alors à sa suite, jusqu'à
 * ``METIERS_MAXIMUM``.
 *
 * Une période est un métier, ou une période sans emploi : le menu de chaque
 * ligne suivante propose les deux, et la dernière dit donc, quand elle est sans
 * emploi, la date à laquelle l'activité s'arrête.
 */
function metiersFormulaire(saisie, affiliations, echelle) {
  // Le menu des statuts de chaque ligne est daté de l'entrée dans cette
  // période : un statut que le droit ferme avant cette date y est grisé.
  const lignes = [ligneMetier(
    1,
    g.champDate("debut", "Début d'activité", saisie.jourDe(saisie.debut),
      "le premier mois cotisé",
      saisie.calculDe(saisie.debut),
      {
        min: saisie.jourDe(AGE_DEBUT_MINIMAL),
        max: saisie.jourDe(AGE_DEBUT_MAXIMAL),
        data_age_min: String(AGE_DEBUT_MINIMAL),
        data_age_max: String(AGE_DEBUT_MAXIMAL),
      },
      "L'année d'entrée n'est complète que si l'on entre en janvier : elle est "
      + "portée au compte au prorata de ses mois, comme celle du départ.")
    + g.liste("statut", "Statut d'affiliation",
      optionsStatuts(affiliations, saisie.dateDe(saisie.debut)),
      saisie.statut,
      "proposé aux seules dates où son régime recrutait", {},
      g.GLOSSAIRE["statut d'affiliation"])
    + champRevenu("salaire", saisie, echelle, nombreBrut(saisie.salaire)),
  )];

  saisie.metiers.forEach((metier, index) => {
    const rang = index + 2;
    lignes.push(ligneMetier(rang, champsMetier(
      rang, saisie.jourDe(metier.debut), saisie.calculDe(metier.debut),
      metier.statut, nombreBrut(metier.salaire),
      optionsStatuts(affiliations, saisie.dateDe(metier.debut), true),
      saisie, echelle,
    ), false, metier.sans_emploi));
  });

  // La ligne vide : elle n'existe que tant qu'il reste de la place, et son
  // statut n'est pas présélectionné — un statut choisi par défaut ferait naître
  // un métier que personne n'a demandé.
  const rang = saisie.metiers.length + 2;
  if (rang <= METIERS_MAXIMUM) {
    lignes.push(ligneMetier(
      rang,
      champsMetier(rang, "", "", "", "", optionsStatuts(affiliations, null, true),
        saisie, echelle),
      true,
    ));
  }

  return `<div class="metiers">${lignes.join("")}</div>`;
}

/**
 * Les trois champs d'un métier qui suit le premier.
 *
 * Le changement se date au mois comme le reste, depuis que le calendrier a
 * remplacé les âges : il n'en coûte pas un champ de plus, et une carrière qui
 * change de régime en cours d'année se décrit telle qu'elle a eu lieu.
 */
function champsMetier(rang, debut, calcul, statut, salaire, statuts, saisie, echelle) {
  // Une période sans emploi n'a que deux champs : elle ne paie aucun revenu, et
  // celui d'avant lui sert de référence là où le droit lui ouvre des points. Le
  // champ disparaît donc plutôt que de demander un nombre dont rien ne serait
  // fait.
  const revenu = CODES_SANS_EMPLOI.has(statut)
    ? ""
    : champRevenu(`metier${rang}_salaire`, saisie, echelle, salaire, true);
  return g.champDate(`metier${rang}_debut`, "Début de cette période", debut,
    "le mois où elle commence", calcul,
    {
      min: saisie.jourDe(AGE_DEBUT_MINIMAL),
      max: saisie.jourDe(AGE_LIQUIDATION_MAXIMAL),
      data_age_min: String(AGE_DEBUT_MINIMAL),
      data_age_max: String(AGE_LIQUIDATION_MAXIMAL),
    })
    + g.liste(`metier${rang}_statut`, "Métier, ou période sans emploi",
      [["", "— aucun —"], ...statuts], statut)
    + revenu;
}

/**
 * Une période : un `<fieldset>`, et son rang en `<legend>`.
 *
 * « Revenu brut mensuel » et « Métier, ou période sans emploi » sont les mêmes
 * libellés dans chaque bloc ; seul le rang les distingue. Un intertitre
 * ordinaire le montrerait à l'œil sans le dire à personne d'autre : la légende
 * d'un groupe, elle, est énoncée avec chacun des champs qu'elle couvre.
 *
 * La ligne VIDE, elle, est repliée : trois champs offerts à qui n'en veut pas
 * occupaient un tiers du formulaire pour la plupart des carrières, qui n'ont
 * qu'un métier. Il n'en reste que la demande — « Ajouter une période » —, et
 * les champs ne paraissent que si on la suit. Un `<details>` plutôt qu'un
 * `<fieldset>` : c'est le résumé qui nomme le groupe, et le nommer deux fois
 * ferait lire deux titres pour une ligne qui n'existe pas encore.
 */
function ligneMetier(rang, champs, vide = false, sansEmploi = false) {
  const rangs = majuscule(RANGS_METIER[rang - 1]);
  if (vide) {
    return '<details class="metier facultatif">'
      + g.sommaire("Ajouter une période — un métier, une interruption")
      + `<div class="grille">${champs}</div></details>`;
  }
  const titre = sansEmploi ? `${rangs} période, sans emploi` : `${rangs} métier`;
  return `<fieldset class="metier"><legend class="rang">${echapper(titre)}</legend>`
    + `<div class="grille">${champs}</div></fieldset>`;
}

function majuscule(texte) {
  return texte.charAt(0).toUpperCase() + texte.slice(1);
}

/**
 * La suite des métiers, en une phrase — et la convention qui la borne. Muet
 * pour une carrière d'un seul métier : il n'y a rien à récapituler, le
 * formulaire juste au-dessus le dit déjà.
 */
function resumeParcours(contexte, saisie) {
  if (saisie.releveActif) {
    return resumeReleve(contexte, saisie);
  }
  const lignes = saisie.lignesCarriere;
  if (lignes.length < 2) {
    return "";
  }
  // Le parcours est calculé pour ses refus : un revenu hors bornes doit être
  // signalé ici comme il l'est ailleurs, avant que la page ne le résume.
  saisie.parcours(contexte.echelle(saisie));
  const affiliations = contexte.simulateur().affiliations;
  const bornes = [...lignes.map((ligne) => ligne.debut), saisie.liquidation];
  const etapes = lignes.map((ligne, rang) => (
    (ligne.sans_emploi
      ? LIBELLES_SANS_EMPLOI[ligne.statut]
      : echapper(affiliations.libelle(ligne.statut)))
    + ` de ${age(bornes[rang])} à ${age(bornes[rang + 1])}`
  ));
  const convention = lignes.some((ligne) => ligne.sans_emploi)
    ? "L'année d'un changement revient à ce qui en occupe le plus de mois "
      + "— les régimes liquident à l'année, et une année n'a qu'un statut — "
      + "mais le revenu porté au compte reste la somme de ce qui a été payé."
    : "L'année d'un changement revient au métier qui en occupe le plus de "
      + "mois — les régimes liquident à l'année, et une année n'a qu'un "
      + "statut — mais le revenu porté au compte reste la somme de ce que les "
      + "deux ont payé.";
  return `<p class="discret">Carrière en ${lignes.length} périodes : `
    + etapes.join(", puis ") + ". " + convention + "</p>";
}

/**
 * Ce que le relevé a remplacé, et ce qu'il n'a pas remplacé.
 *
 * La phrase importe plus que le décompte : les champs du formulaire restent
 * affichés au-dessus, avec le statut et le revenu qu'ils portaient, et rien ne
 * dirait qu'ils n'ont pas servi. La lecture du relevé se termine donc par ce
 * qu'aucun relevé ne donne — le mois d'entrée dans la vie active —, parce que
 * c'est la seule approximation que ce chemin conserve.
 */
function resumeReleve(contexte, saisie) {
  const releve = saisie.releveAnalyse(
    Object.keys(contexte.paquet.periodes_non_travaillees ?? {}),
  );
  const affiliations = contexte.simulateur().affiliations;
  const statutsLus = [...new Set(releve.map((ligne) => ligne.affiliation))];
  const cotisees = releve.filter((ligne) => ligne.type_periode === "emploi");
  const libelles = statutsLus
    .map((code) => echapper(affiliations.libelle(code))).join(", ");
  const annees = releve.map((ligne) => ligne.annee);
  return '<p class="discret">Carrière <strong>lue sur un relevé</strong> : '
    + `${releve.length} années de ${Math.min(...annees)} à `
    + `${Math.max(...annees)}, dont ${cotisees.length} cotisées, sous `
    + `${statutsLus.length} statut${statutsLus.length > 1 ? "s" : ""} — `
    + `${libelles}. Les métiers, le profil de carrière et le niveau de revenu `
    + "du formulaire n'ont pas servi : aucun revenu n'est reconstitué, ils "
    + "sont lus un par un. Une ligne vaut une année civile entière, sauf "
    + "celle du départ, que la date de liquidation tronque : le relevé donne "
    + "l'année, jamais le mois, et l'année d'entrée dans la vie active reste "
    + "donc comptée pour une année pleine.</p>";
}

/**
 * À quelle date se rapportent les montants affichés, et en quels euros.
 *
 * C'est la première question que pose un lecteur devant les quatre barres :
 * « ce nombre, c'est celui de quand ? ». Deux conventions y répondent, dont
 * aucune ne va de soi. Le moteur ne calcule qu'une pension AU MOMENT DE LA
 * LIQUIDATION — il n'existe aucune phase postérieure qu'il revaloriserait —,
 * et il l'exprime en euros constants. Autrement dit : jamais la pension
 * d'aujourd'hui d'un retraité, toujours celle de son premier mois de retraite ;
 * et jamais le montant nominal que porte un relevé bancaire, toujours son
 * pouvoir d'achat ramené à une année de référence.
 *
 * Les deux conventions se disent différemment selon que le départ est passé ou
 * à venir, parce que ce qu'elles écartent n'est pas le même : pour un actif,
 * les revalorisations à venir de sa pension ; pour un retraité, celles qu'il a
 * déjà reçues. La seconde n'a plus qu'un chiffre à expliquer : la page
 * n'affiche que le pouvoir d'achat de l'année de référence, jamais la somme
 * nominale du mois du départ, et ce paragraphe dit d'où il vient.
 */
function lectureDesMontants(comparaison, saisie) {
  const carriere = comparaison.carriere;
  const annee = carriere.anneeLiquidation;
  const date = echapper(String(carriere.dateLiquidation));
  const courante = comparaison.parametres.annee_courante;

  let quand;
  if (annee > courante) {
    quand = "Vous n'êtes pas encore à la retraite : ces montants sont ceux de "
      + "votre <strong>première pension</strong>, celle du mois où vous "
      + `partiriez — ${date} —, et non d'une pension que vous toucheriez `
      + "aujourd'hui.";
  } else if (annee < courante) {
    quand = "Vous êtes déjà à la retraite : ces montants sont ceux de votre "
      + `pension <strong>au moment du départ</strong> — ${date} —, et non `
      + `de celle que vous touchez aujourd'hui. Depuis ${annee}, votre `
      + "pension a été revalorisée chaque année ; le simulateur s'arrête au "
      + "jour de la liquidation et ne suit aucune de ces revalorisations.";
  } else {
    quand = "Vous liquidez cette année : ces montants sont ceux de votre "
      + `<strong>première pension</strong>, celle de ${date}. Le simulateur `
      + "s'arrête là et ne suit pas les revalorisations des années "
      + "suivantes.";
  }

  let unites;
  if (annee > saisie.euros) {
    unites = `Ils sont donnés en euros de ${saisie.euros}, et dans cette unité `
      + `seulement : la somme telle qu'elle serait versée en ${annee}, `
      + "l'inflation d'ici là comprise, est ramenée au pouvoir d'achat de "
      + `${saisie.euros} — plus petite, sans rien acheter de moins. C'est ce `
      + "pouvoir d'achat, et non le nombre qui sera inscrit sur le virement, "
      + "qui dit ce que vaut la pension : le nombre nominal n'est pas "
      + "affiché.";
  } else if (annee < saisie.euros) {
    unites = `Ils sont donnés en euros de ${saisie.euros}, et dans cette unité `
      + `seulement : la somme telle qu'elle a été versée en ${annee}, en `
      + "euros de l'époque, est ramenée au pouvoir d'achat de "
      + `${saisie.euros}, le seul qui se compare aux prix que vous `
      + "connaissez ; le montant de l'époque n'est pas affiché.";
  } else {
    unites = `Le départ tombe sur ${saisie.euros}, l'année de référence : les `
      + "euros du départ et ceux dans lesquels la page compte sont les mêmes, "
      + "et il n'y a rien à convertir.";
  }

  // La clé de lecture SUIT LE MODE, sous peine de démentir les chiffres
  // qu'elle explique : elle a dit « montants bruts, avant CSG » au-dessus de
  // montants nets, et « un brut sur un brut, donc plus bas qu'un taux calculé
  // sur des nets » au-dessus d'un taux calculé, précisément, sur des nets.
  const prelevements = saisie.enNet
    ? "Montants <strong>nets</strong> et au centime, tels qu'ils arrivent sur "
      + "le compte : après CSG, CRDS et Casa — 9,10 %, le taux plein, appliqué "
      + "ici à tout le monde — et avant impôt sur le revenu, comme le revenu "
      + "d'activité saisi plus haut. Le <strong>taux de remplacement</strong> "
      + "rapporte la pension annuelle au dernier revenu d'activité ramené à "
      + "l'année pleine — un net sur un net, donc plus haut qu'un taux calculé "
      + "sur des bruts."
    : "Montants <strong>bruts</strong> et au centime, comme la caisse les "
      + "verse : avant CSG, CRDS et impôt, comme le revenu d'activité saisi "
      + "plus haut. Le <strong>taux de remplacement</strong> rapporte la "
      + "pension annuelle au dernier revenu d'activité ramené à l'année "
      + "pleine — un brut sur un brut, donc plus bas qu'un taux calculé sur "
      + "des nets.";

  return g.bulle(
    "De quand sont ces chiffres, et en quels euros",
    `${quand} ${unites} Ce que compare cette page, ce sont quatre façons de `
    + "CALCULER une pension de départ, pas quatre façons de la revaloriser "
    + `ensuite. ${prelevements}`,
  );
}

/**
 * Le cumul versé par chaque scénario, du départ à 105 ans.
 *
 * Les quatre barres du haut donnent la pension d'UN mois — le premier. Elles ne
 * disent donc rien de ce qu'une retraite finit par verser, ni de ce que la
 * durée y change. Or c'est là que la mécanique notionnelle se joue : la pension
 * vaut le capital divisé par l'espérance de vie, si bien que vivre au-delà de
 * cette moyenne, c'est toucher plus que ce que la carrière a financé, et mourir
 * avant, moins. Un graphique arrêté à l'espérance de vie cacherait exactement
 * cela ; celui-ci va jusqu'à 105 ans.
 *
 * Ce que le cumul suppose, et que la page dit : la pension garde son pouvoir
 * d'achat après le départ. Le moteur ne simule aucune revalorisation
 * postérieure à la liquidation — additionner en euros constants est la
 * convention la plus neutre dont on dispose, ce n'est pas une prévision.
 */
function corpsTrajectoire(contexte, comparaison, saisie, seul = false) {
  const carriere = comparaison.carriere;
  const depart = carriere.age_liquidation || 0.0;
  if (!(depart > 0 && depart < AGE_MAXIMUM_TRAJECTOIRE)) return "";

  const annuel = {};
  for (const [cle] of TRAJECTOIRE) {
    annuel[cle] = comparaison.enEurosConstants(comparaison[cle].pension_annuelle);
  }
  if (Math.max(...Object.values(annuel)) <= 0) return "";

  const ages = [];
  for (let a = Math.floor(depart); a <= AGE_MAXIMUM_TRAJECTOIRE; a += 1) ages.push(a);
  const titres = new Map(titresScenarios(saisie));
  const series = TRAJECTOIRE.map(([cle, couleur]) => new g.Serie(
    titres.get(cle),
    // En milliers : l'axe monterait sinon à sept chiffres, illisibles dans la
    // marge d'un graphique qui doit tenir sur un téléphone.
    // Rien avant le départ : pour une liquidation en cours d'année,
    // « max(0, âge - départ) » faisait partir la courbe de l'âge entier
    // précédent, soit jusqu'à onze mois de pension qui n'ont pas été versés.
    // La courbe commence maintenant au premier âge atteint.
    ages.map((age) => (age < depart ? null : annuel[cle] * (age - depart) / 1000)),
    `var(${couleur})`,
  ));
  const etiquettes = TRAJECTOIRE.map(([, , chiffre]) => chiffre);

  const conversion = comparaison.notionnel_retroactif.conversion;
  const esperance = conversion.esperance_residuelle;
  const ageEsperance = depart + esperance;
  const survie = courbeDeSurvie(contexte, carriere, conversion.table);
  const vivants = (age) => g.pourcentage(partVivante(survie, age - depart), false, 0);

  // Le système 2 passe au-dessus du système 1 pour qui a beaucoup cotisé sans
  // que le droit en vigueur le lui rende — un libéral à quatre fois le salaire
  // moyen, par exemple. La phrase disait « l'écart se creuse » en affichant
  // « -45 575 € par an » : un signe moins au milieu d'un texte qui affirmait le
  // contraire.
  const ecart = annuel.actuel - annuel.notionnel_retroactif;
  const phraseEcart = `Le système 2 verse ${g.euros(Math.abs(ecart))} par an de `
    + (ecart >= 0 ? "moins" : "plus")
    + " que le système 1 ; l'écart se creuse ici d'autant d'années que la "
    + "retraite dure";
  // Unité brève : le libellé est ancré à gauche de l'axe et déborderait du
  // cadre au-delà d'une poignée de caractères — « milliers d'euros de 2026,
  // cumulés » sortait du viewBox par la gauche, et « k€ 2026 » y perdait encore
  // son « k » sur téléphone, où les textes du repère sont grossis. Le texte
  // sous le graphique dit ce que « k€ » désigne, et de quelle année.
  const unite = "k€";
  return `
<p>${seul
    ? "Chaque système sert une pension mensuelle ; ce graphique"
    : "Les quatre montants du haut sont ceux d'un seul mois, le premier. Ce graphique"}
les additionne, année après année, à mesure que le retraité vieillit.${g.bulle(
    "Ce que ce graphique ajoute aux quatre montants",
    "C'est là que la durée entre dans le calcul. Une pension "
    + "notionnelle vaut le capital divisé par l'espérance de vie, donc "
    + "<strong>vivre plus longtemps que la moyenne, c'est toucher plus que ce "
    + "que la carrière a financé</strong> — et mourir avant, moins. Cumuls "
    + `bruts, en milliers d'euros constants de ${saisie.euros} : ils supposent `
    + "que la pension garde son pouvoir d'achat après le départ, le moteur ne "
    + "simulant aucune revalorisation postérieure à la liquidation. Une "
    + "indexation qui décrocherait des prix ferait fléchir les quatre courbes à "
    + "la fois, sans changer leur ordre.",
  )}</p>
${g.graphique(
    "Cumul versé par chaque système, du départ à "
    + `${AGE_MAXIMUM_TRAJECTOIRE} ans`,
    ages, series, unite, false, 0, true, ageEsperance,
    `espérance de vie : ${g.nombre(ageEsperance, 1)} ans`, etiquettes, "Âge",
  )}
<p>Trait vertical : l'espérance de vie à ${age(depart)} —
<strong>${g.nombre(esperance, 1)} ans</strong>, soit ${g.nombre(ageEsperance, 1)}
ans d'âge, le nombre par lequel le capital notionnel est divisé.
${phraseEcart}.${g.bulle(
    "Une moyenne, et non une échéance",
    "D'après la même table, "
    + `<strong>${vivants(ageEsperance)}</strong> de ceux qui partent à `
    + `${age(depart)} sont encore en vie à cet âge : ils dépassent donc le `
    + "nombre qui a servi à calculer leur pension, et touchent plus que ce que "
    + `leur carrière a financé. Plus loin encore, ${vivants(100)} atteignent `
    + `100 ans et ${vivants(AGE_MAXIMUM_TRAJECTOIRE)} atteignent `
    + `${AGE_MAXIMUM_TRAJECTOIRE} ans, où le graphique s'arrête — c'est pour `
    + "eux qu'il va si loin.",
  )}</p>
`;
}

/**
 * Le même cumul, replié, pour le bas de la page Simuler.
 *
 * Là-bas il vient après quatre montants et trois tableaux : le déplier d'office
 * ferait un septième bloc à traverser. Il a sa propre page, en revanche, où il
 * est le sujet et s'ouvre donc de lui-même.
 */
function trajectoire(contexte, comparaison, saisie) {
  const corps = corpsTrajectoire(contexte, comparaison, saisie);
  if (!corps) return "";
  return g.depliant("Ce que chaque système finit par verser", corps);
}

/**
 * Ce que chaque système vous AURA versé, du départ à 105 ans.
 *
 * Un montant mensuel ne dit rien de la durée : les barres de la page Simuler
 * donnent la pension d'un mois, le premier. Ici on additionne, et c'est là que
 * la mécanique notionnelle devient visible. Un graphique, et un seul : c'est
 * la règle du site.
 *
 * Copie de `_page_trajectoire` dans `web/pages.py`.
 */
function pageTrajectoire(contexte, parametres) {
  const tete = g.affiche(
    "Trajectoire",
    "Ce que chaque système vous "
    + '<span class="cle-texte">aura versé.</span>',
    "La même carrière, suivie année après année depuis le départ. Pas une "
    + "pension mensuelle, mais le cumul : ce que vous aurez réellement "
    + "touché à 75, à 86, à 95 ans.",
  );
  const form = simulateurCourt(contexte, "/trajectoire");

  let saisie;
  try {
    saisie = Saisie.depuisRequete(parametres);
  } catch (erreur) {
    if (fauteDeProgramme(erreur)) throw erreur;
    return tete + form + messageErreur(erreur.message);
  }

  let corps;
  try {
    corps = corpsTrajectoire(contexte, contexte.simuler(saisie), saisie, true);
  } catch (erreur) {
    if (fauteDeProgramme(erreur)) throw erreur;
    return tete + form + messageErreur(erreur.message);
  }
  if (!corps) {
    return tete + form + messageErreur(
      "Cette carrière ne verse aucune pension : il n'y a pas de cumul "
      + "à tracer.",
    );
  }

  // Le graphique est monté en CARTE : c'est elle qui lui donne sa question, sa
  // réponse en une phrase, sa source — et sa barre de partage. Sans elle, la
  // Trajectoire aurait été la seule page à graphique dont on ne puisse rien
  // publier.
  const carte = g.cle(
    "Au total, combien chaque système aura-t-il versé ?",
    "À âge de départ identique, l'écart entre deux courbes est ce que le "
    + "système choisi vous coûte ou vous rapporte, année après année.",
    corps,
    "Cumuls bruts, en euros constants, sur la carrière saisie. "
    + "Modèle ouvert : "
    + `<a href="${g.DEPOT}">le dépôt</a>.`,
    "cumul",
  );

  return `
${tete}

${form}

${carte}

<div class="paire">
  <div>
    <h2 style="margin-top:0">Pourquoi le cumul, et pas le mois</h2>
    <p>Une pension mensuelle ne dit rien de la durée. Le graphique montre les
    quatre systèmes à âge de départ identique : l'écart entre deux courbes est ce
    que le système choisi vous coûte ou vous rapporte, année après année.</p>
    <p>Les scénarios qui ne portent au compte que la <strong>part
    salariale</strong> restent sous le système actuel ; ceux qui y ajoutent la
    <strong>part patronale</strong> passent au-dessus. <span class="cle-texte">La
    proposition libérale se place entre les deux, avec un taux de
    ${g.pourcentage(contexte.base.taux_cotisation_liberal, false, 0)} au lieu
    de ${g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0)}.</span></p>
  </div>
  <div class="encadre">
    <h2 class="serif" style="margin-top:0">Le repère de l'espérance de vie</h2>
    <p>C'est la durée que le modèle lit sur la table de la génération
    concernée, et par laquelle le compte notionnel divise. Celui qui vit plus
    longtemps touche davantage que ce qu'il a cotisé, celui qui vit moins
    longtemps touche moins — comme dans tout système par répartition.</p>
    <p class="discret">Le trait vertical du graphique la marque. La courbe
    continue au-delà : c'est là que se lit ce qu'une longue vieillesse
    change.</p>
  </div>
</div>
`;
}

/**
 * Une carte 1200 × 675, au format de X et de LinkedIn. Ce que la page montre
 * est l'APERÇU de la carte, réduit à la largeur de sa colonne ; ce qui se
 * publie est l'image composée par le bouton, aux vraies dimensions. Le pied est
 * ce qui compte le plus — une image qui quitte le site n'a plus ni barre
 * d'adresse ni page autour —, et le filigrane de l'image le redit en travers du
 * cadre : le pied se recadre tout seul, le filigrane coûte la carte.
 *
 * Copie de `_carte_partage` dans `web/pages.py`.
 */
function cartePartage(nom, surtitre, chiffre, phrase, detail, classes = "") {
  const boite = `carte-partage ${classes}`.trim();
  const pied = `<div class="pied"><span class="compte">${g.SIGNATURE}</span>`
    + `<span class="adresse">${g.ADRESSE_SITE}</span></div>`;
  const corps = `<div class="${boite}">`
    + `<p class="surtitre">${surtitre}</p>`
    + `<div><div class="chiffre">${chiffre}</div>`
    + `<div class="phrase">${phrase}</div>`
    + `<div class="detail">${detail}</div></div>${pied}</div>`;
  return `<figure class="carte"><figcaption>${nom}</figcaption>`
    + `<div class="cadre-carte">${corps}</div>${g.barrePartage()}</figure>`;
}

/**
 * Les chiffres du programme, au format des réseaux sociaux.
 *
 * Cette page a d'abord été LE dispositif de partage, et c'était une erreur :
 * personne ne la trouvait. Le partage est descendu sur les pages elles-mêmes ;
 * ce qui reste ici est ce que la barre de partage ne peut pas donner — les
 * chiffres du programme, qui ne sont le résultat d'aucun graphique. Elle
 * demandait encore une capture d'écran ; elle porte maintenant la même barre
 * que les graphiques du site.
 *
 * Copie de `_partager` dans `web/pages.py`.
 */
function partager(contexte) {
  const base = contexte.base;
  const solde = contexte.cout().solde;
  const horizon = solde.annee(solde.derniereAnnee);
  const taux = g.pourcentage(base.taux_cotisation_liberal, false, 0);
  const capitalise = g.pourcentage(base.taux_capitalisation_obligatoire, false, 0);
  const volontaire = g.pourcentage(
    tauxCapitalisationVolontaireApplique(base), false, 0,
  );
  const propose = g.pourcentage(tauxRetraitePropose(base), false, 0);
  const garantie = base.garantie_vieillesse_mensuelle;
  const isolement = base.allocation_isolement_mensuelle;
  const manque = Math.abs(horizon.solde("actuel"));
  const depense = horizon.depense("actuel");

  const tete = g.affiche(
    "Partager",
    "Quatre cartes, "
    + '<span class="cle-texte">prêtes à publier.</span>',
    "Un bouton par carte : l'image part au format des réseaux sociaux, "
    + "avec son message déjà rédigé. "
    + `<strong class="cle-texte">${g.SIGNATURE}</strong> y est posé en `
    + "filigrane, en travers de l'image et non dans un coin : le recadrer "
    + "revient à recadrer la carte.",
  );

  const cartes = [
    cartePartage(
      "Le plancher",
      "Notre programme pour les retraites",
      g.euros(garantie + isolement),
      "par mois au minimum, pour une personne seule.<br>"
      + `${g.euros(2 * garantie)} pour un couple.`,
      `${g.euros(garantie)} par personne, plus ${g.euros(isolement)} `
      + "d'allocation d'isolement. Payés par l'impôt, dès "
      + `${AGE_OUVERTURE_GARANTIE} ans.`,
    ),
    cartePartage(
      "Le taux",
      "Baisse des prélèvements",
      `${taux} + ${capitalise}`,
      "de cotisation retraite, pour tout le monde.",
      `${g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0)} aujourd'hui pour `
      + `un salarié du privé (${g.pourcentage(TAUX_ACTUEL_SALARIAL, false, 1)} + `
      + `${g.pourcentage(TAUX_ACTUEL_PATRONAL, false, 1)}). Les ${volontaire} rendus `
      + `peuvent aller au même compte : ${propose} en tout, comme `
      + "aujourd'hui, pour une retraite qui vous appartient.",
    ),
    cartePartage(
      "Le déficit",
      "Ce que le système actuel ne paie plus",
      `${g.nombre(manque * 100, 1)} points de PIB`,
      `c'est l'écart annuel à combler en ${solde.derniereAnnee}, sans `
      + "réforme.",
      `${g.pourcentage(depense, false, 1)} du PIB de dépenses contre `
      + `${g.pourcentage(depense - manque, false, 1)} de ressources. `
      + "Source : COR, comptes du système de retraite.",
      "deficit",
    ),
    cartePartage(
      "L'appel au simulateur",
      "Le simulateur",
      "Et vous, ça donne combien ?",
      "Votre carrière, calculée quatre fois : les règles d'aujourd'hui, et "
      + "les nôtres.",
      "Modèle ouvert, données publiques. Tout se calcule dans votre "
      + "navigateur : rien n'est envoyé.",
      "claire appel",
    ),
  ].join("");

  return `
${tete}

<div class="cartes">${cartes}</div>

<div class="paire">
  <div>
    <h2 style="margin-top:0">Texte prêt à coller</h2>
    <p>« Un minimum de ${g.euros(garantie + isolement)}/mois, ${taux} de
    cotisation au lieu de
    ${g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0)}, ${capitalise} capitalisés
    à votre nom et ${volontaire} rendus que vous placez où vous voulez, et un
    compte de retraite en euros que chacun peut lire. Vérifiez sur votre
    carrière : ${g.ADRESSE_SITE} — ${g.SIGNATURE} »</p>
    <p class="discret">Le bouton de chaque carte met déjà ce message dans le
    presse-papiers avec l'image.</p>
  </div>
  <div class="encadre">
    <h2 class="serif" style="margin-top:0">Et depuis les pages du site</h2>
    <p>Inutile de repasser par ici pour partager un graphique : sous chacun, la
    même barre <span class="cle-texte">Partager</span> compose l'image de ce
    que vous venez de lire et le message qui va avec. Toutes portent le
    filigrane <span class="cle-texte">${g.SIGNATURE}</span>, en travers du
    cadre.</p>
  </div>
</div>
`;
}

/** Le libellé de chaque scénario, dans l'ordre des barres. */
function titresScenarios(saisie) {
  return [
    ["actuel", "1. Système de répartition actuel"],
    ["notionnel_retroactif", "2. Compte notionnel, part salariale seule"],
    ["notionnel_retroactif_employeur",
      "3. Compte notionnel, part salariale + patronale"],
    ["notionnel_liberal", "4. La proposition du Parti libéral français"],
  ];
}

/**
 * Courbe de survie EXACTEMENT celle dont le coefficient a été tiré.
 *
 * Le sexe et le type de table se relisent sur le libellé que porte le
 * coefficient, plutôt que d'être recalculés depuis les paramètres : deux
 * chemins de décision pour une seule table finiraient par diverger, et le
 * graphique annoncerait alors une espérance de vie qui ne serait pas celle
 * ayant servi à diviser le capital.
 */
function courbeDeSurvie(contexte, carriere, table) {
  const sexe = table.startsWith("unisexe") ? null : table.split("_")[0];
  const generation = table.endsWith("_generation");
  return contexte.simulateur().mortalite.courbe(
    carriere.age_liquidation || 0.0,
    carriere.anneeLiquidation + (carriere.moisLiquidation - 1) / 12,
    sexe, generation,
  );
}

/**
 * Part encore en vie ``duree`` années après la liquidation.
 *
 * Conditionnelle au fait d'être vivant AU DÉPART : la courbe part de 1 à l'âge
 * de liquidation. Ce n'est donc pas une part de la génération née la même année
 * — celle-là a déjà perdu des siens avant la retraite —, et la page dit « de
 * ceux qui partent à tel âge », non « de la génération ».
 *
 * Interpolée entre deux âges entiers : l'espérance de vie tombe rarement sur un
 * anniversaire, et arrondir la durée à l'année déplacerait le chiffre cité d'un
 * point ou deux.
 */
function partVivante(survie, duree) {
  if (duree <= 0) return 1.0;
  const rang = Math.floor(duree);
  if (rang + 1 >= survie.length) return survie.length ? survie[survie.length - 1] : 0.0;
  const fraction = duree - rang;
  return survie[rang] * (1 - fraction) + survie[rang + 1] * fraction;
}

function resultats(contexte, saisie) {
  const comparaison = contexte.simuler(saisie);
  const carriere = comparaison.carriere;
  const retro = comparaison.notionnel_retroactif;
  const conversion = retro.conversion;

  // Le moteur ne calcule qu'un montant, en euros de l'année de liquidation. La
  // page n'en affiche qu'un, et ce n'est pas celui-là : le même ramené au
  // pouvoir d'achat de l'année de référence, seul à se comparer à un salaire ou
  // à un loyer que le lecteur connaît. La somme nominale du mois du départ —
  // des euros d'une année que personne n'a en poche — paraissait à côté : elle
  // doublait chaque ligne d'un second chiffre qu'il fallait une légende pour
  // distinguer du premier.
  const courants = {
    actuel: comparaison.actuel.pension_annuelle,
    retroactif: retro.pension_annuelle,
    "retroactif-employeur":
      comparaison.notionnel_retroactif_employeur.pension_annuelle,
    // La proposition sert DEUX lignes : la pension de répartition issue du
    // compte notionnel, et la rente du pilier capitalisé obligatoire. Le
    // montant affiché est leur somme — c'est ce qui tombe sur le compte du
    // retraité —, et la barre comme la glose disent aussitôt ce qui vient de
    // l'une et ce qui vient de l'autre.
    liberal: comparaison.notionnel_liberal.pension_totale,
  };
  const constants = {};
  for (const [cle, montant] of Object.entries(courants)) {
    constants[cle] = comparaison.enEurosConstants(montant);
  }
  const capitalise = comparaison.enEurosConstants(
    comparaison.notionnel_liberal.rente_capitalisation_obligatoire,
  );
  // La part de cette rente qui vient des cinq points VOLONTAIRES, nommée à
  // part sous la barre : c'est la seule ligne de la page que personne
  // n'impose, et le lecteur doit pouvoir la retrancher de l'œil.
  const capitaliseVolontaire = comparaison.enEurosConstants(
    comparaison.notionnel_liberal.rente_capitalisation_volontaire,
  );
  const reference = Math.max(...Object.values(constants)) || 1.0;

  const anneeDepart = carriere.anneeLiquidation;
  const uniteReference = saisie.euros === comparaison.parametres.annee_courante
    ? "par mois, en euros d'aujourd'hui"
    : `par mois, en euros de ${saisie.euros}`;

  // Le salaire net que chaque système laisse PENDANT la carrière, à côté de la
  // pension qu'il servira APRÈS. Les trois premiers prélèvent la même chose :
  // le même nombre y paraît donc trois fois, et c'est le propos — seul le
  // système 4 déplace la fiche de paie.
  const remuneration = comparaison.remuneration;
  const montants = Montants.depuis(
    saisie, contexte.simulateur(comparaison.parametres), comparaison);
  const nets = {};
  if (remuneration !== null) {
    const referencePaie = remuneration.reference;
    nets.actuel = montants.salaire(referencePaie.droitEnVigueur);
    nets.retroactif = montants.salaire(referencePaie.droitEnVigueur);
    nets["retroactif-employeur"] = montants.salaire(referencePaie.droitEnVigueur);
    nets.liberal = montants.salaire(referencePaie.proposition);
  }

  /**
   * Le second chiffre de la ligne : ce qu'on touche en travaillant.
   *
   * Volontairement plus petit que la pension — la page compare des pensions, et
   * le salaire est ce qu'on met EN REGARD. L'écart n'est écrit que là où il y
   * en a un, pour que les trois premières lignes se lisent comme ce qu'elles
   * sont : le même salaire net.
   */
  const salaire = (cle) => {
    if (!(cle in nets)) {
      return "";
    }
    const net = nets[cle];
    const ecart = net - nets.actuel;
    const mention = Math.abs(ecart) >= 0.005
      ? `<span class="ecart">${eurosSigne(ecart / 12)} par mois</span>`
      : "";
    return `
      <span class="chiffre salaire">
        <span class="categorie">salaire</span>
        <span class="somme">${g.nombre(net / 12)}</span>
        <span class="unite">${montants.uniteSalaire}</span>
        ${mention}
      </span>`;
  };


  const bloc = (cle, titre, glose, variation, tauxRemplacement,
                partCapitalisee = 0.0, partVolontaire = 0.0) => {
    const montant = constants[cle];
    const variationHtml = variation === null
      ? '<span class="discret">référence</span>'
      : `<strong>${g.pourcentage(variation, true)}</strong>`;
    // La barre du système qui porte un pilier capitalisé est coupée en deux :
    // la répartition pleine, la capitalisation hachurée. Même couleur — c'est
    // le même système —, autre texture — ce n'est pas la même promesse.
    const repartition = montant - partCapitalisee;
    let barre = `<span style="width:${formatFixe(repartition / reference * 100, 1)}%"></span>`;
    let partage = "";
    if (partCapitalisee > 0) {
      barre += `<span class="capitalise" style="width:${formatFixe(partCapitalisee / reference * 100, 1)}%"></span>`;
      // Trois montants nommés plutôt que deux dès qu'il y a du volontaire :
      // additionner en silence une épargne facultative à une cotisation
      // obligatoire ferait promettre un montant que le lecteur n'aura que s'il
      // la verse.
      const detail = partVolontaire > 0 ? `
        ${g.eurosCentimes(montants.pension(partCapitalisee - partVolontaire) / 12)}
        de rente capitalisée obligatoire +
        ${g.eurosCentimes(montants.pension(partVolontaire) / 12)} de rente
        des cinq points volontaires, par mois` : `
        ${g.eurosCentimes(montants.pension(partCapitalisee) / 12)} de rente
        capitalisée, par mois`;
      partage = `
      <span class="composition">${g.eurosCentimes(montants.pension(repartition) / 12)}
        de pension par répartition +${detail}</span>`;
    }
    return `
<div class="scenario">
  <div class="entete">
    <span class="titre">${echapper(titre)}</span>
    <span class="montant">${salaire(cle)}
      <span class="chiffre principal">
        <span class="categorie">retraite</span>
        <span class="somme">${g.nombre(montants.pension(montant) / 12)}</span>
        <span class="unite">${montants.unitePension}</span>
      </span>
    </span>
  </div>${partage}
  <div class="barre ${cle}">${barre}</div>
  <div class="glose">${glose} · ${g.terme("taux de remplacement")}
    ${g.pourcentage(montants.tauxRemplacement(tauxRemplacement))} ·
    écart au système actuel : ${variationHtml}</div>
</div>`;
  };

  // La glose porte ce que le titre ne dit plus : DEPUIS QUAND la carrière est
  // recalculée, et à quel taux. C'est ce qui explique l'ordre des montants.
  const scenarios = bloc("actuel", "1. Système de répartition actuel",
    "le droit en vigueur, minima et majorations compris",
    null, comparaison.tauxRemplacementActuel)
    + bloc("retroactif", "2. Compte notionnel, part salariale seule",
      "toute la carrière recalculée depuis 1941, sur la seule part "
      + "salariale — 11,3 % du brut pour un salarié du privé",
      comparaison.variation("notionnel_retroactif"),
      comparaison.tauxRemplacementRetroactif)
    + bloc("retroactif-employeur",
      "3. Compte notionnel, part salariale + patronale",
      "la même carrière recalculée depuis 1941, les deux parts "
      + "comprises — les 28 % prélevés aujourd'hui",
      comparaison.variation("notionnel_retroactif_employeur"),
      comparaison.tauxRemplacement("notionnel_retroactif_employeur"))
    + bloc("liberal",
      "4. La proposition du Parti libéral français",
      `le système 3 jusqu'à ${saisie.bascule}, puis `
      + `${g.pourcentage(comparaison.parametres.taux_cotisation_liberal, false, 0)} `
      + "pour tous en répartition, "
      + `${g.pourcentage(comparaison.parametres.taux_capitalisation_obligatoire, false, 0)} `
      + "capitalisés par-dessus et "
      + `${g.pourcentage(tauxCapitalisationVolontaireApplique(comparaison.parametres), false, 0)} `
      + "que vous ajoutez librement pour cotiser autant qu'aujourd'hui "
      + `(${g.pourcentage(tauxRetraitePropose(comparaison.parametres), false, 0)} `
      + "en tout) — plus une garantie vieillesse payée par l'impôt",
      comparaison.variationTotale("notionnel_liberal"),
      comparaison.tauxRemplacementTotal("notionnel_liberal"),
      capitalise, capitaliseVolontaire);

  const fiches = [
    g.fiche("années cotisées", String(carriere.anneesCotisees.length)),
    // La date, et pas seulement l'année : la pension prend effet le premier du
    // mois, et c'est ce mois que l'utilisateur vient de choisir.
    g.fiche("liquidation", `${age(carriere.age_liquidation)} `
      + `<span class="discret">en ${carriere.dateLiquidation}</span>`),
    // Deux décimales, et non une : le lecteur qui refait la division
    // « capital ÷ coefficient » doit retrouver la pension affichée. À 25,7 au
    // lieu de 25,67 il tombait un euro à côté, et doutait du reste.
    g.fiche("coefficient de conversion",
      g.nombre(conversion.diviseur, DECIMALES_DIVISEUR), "",
      g.GLOSSAIRE["coefficient de conversion"]),
    // Le capital est un montant de l'année de liquidation, quand les six
    // pensions ci-dessous sont mises en avant en euros de l'année de
    // référence : sans l'unité, deux grandeurs de nature différente se
    // touchaient sans que rien ne les distingue.
    g.fiche(`capital notionnel rétroactif, en euros de ${anneeDepart}`,
      g.euros(retro.capital_notionnel), "",
      g.GLOSSAIRE["capital notionnel"]),
  ].join("");

  let capitalisation = "";
  if (comparaison.actuel.pension_hors_repartition > 0) {
    const montant = comparaison.enEurosConstants(
      comparaison.actuel.pension_hors_repartition,
    );
    capitalisation = '<p class="discret">Hors répartition, servi à part : '
      + `${g.eurosCentimes(montant / 12)} par mois de RAFP, en euros de ${saisie.euros} `
      + "comme les quatre montants ci-dessus."
      + g.bulle(
        "Pourquoi le RAFP est servi à part",
        "Ce régime est PROVISIONNÉ — sa rente sort d'un placement, non de la "
        + "cotisation des actifs —, si bien qu'une réforme de la répartition "
        + "ne l'atteint pas. Il est donc retiré des six totaux et servi à "
        + "l'identique dans les quatre systèmes : c'est la seule façon de "
        + "comparer ce qui est comparable.",
      )
      + "</p>";
  }

  let minimum = "";
  if (comparaison.actuel.minimum_applique) {
    minimum = '<p class="discret">Le minimum contributif s\'applique dans le '
      + "système 1 ; il est supprimé dans les systèmes notionnels, et la "
      + "proposition lui substitue sa garantie vieillesse.</p>";
  }

  let ouverture = "";
  if (!comparaison.actuel.liquidation_ouverte) {
    const age = comparaison.actuel.age_ouverture_opposable;
    const attente = age === null ? "" : ` — il faut attendre ${g.nombre(age, 2)} ans`;
    ouverture = '<p class="note avertissement">'
      + g.icone("triangle-alert", "Avertissement")
      + "<span>Le droit en vigueur <strong>n'ouvre pas"
      + "</strong> cette liquidation à "
      + `${g.nombre(comparaison.carriere.age_liquidation, 2)} ans${attente}. `
      + "Ni l'âge légal du régime, ni le départ anticipé pour carrière longue "
      + "ne le permettent. Le montant du système 1 reste calculé, parce qu'il "
      + "faut bien comparer les quatre systèmes sur la même carrière, mais il "
      + "ne décrit aucune pension que le système actuel servirait.</span></p>";
  }

  const fiabilite = '<p class="discret" style="margin-top:1.5rem">Fiabilité du '
    + 'résultat : <span class="etiquette-fiabilite">'
    + `${echapper(g.fiabiliteEnClair(nomFiabilite(comparaison.fiabilite)))}</span></p>`;
  // La clé de lecture, avant les chiffres. Les six blocs portent des titres
  // exacts ; aucun ne disait qu'il n'y a qu'une carrière, ni que le premier
  // est la référence des cinq autres. Cinq phrases, en clair.
  const lecture = `
<p class="note resume"><strong>Quatre calculs pour votre carrière.</strong>
Le système 1 applique les règles d'aujourd'hui. C'est la référence.
Les trois autres appliquent chacun d'autres règles à la même carrière.
Deux chiffres par ligne : à gauche votre <strong>salaire</strong> pendant que
vous cotisez, à droite votre <strong>pension</strong> une fois retraité — en
${montants.mot}, l'un comme l'autre, ${uniteReference}.
${noteDuMode(montants)}
Le pourcentage en fin de ligne : l'écart avec le système 1.</p>`;

  // Les montants d'abord, les repères techniques ensuite. Dans l'autre ordre,
  // un téléphone montrait après le calcul un coefficient de conversion, un
  // capital et une note sur l'âge de référence, et pas un euro de pension.
  return `
<h2 id="resultats" tabindex="-1">Résultats\
${lectureDesMontants(comparaison, saisie)}</h2>
${lecture}
<div class="carte">
  ${basculeMontants(saisie, contexte.echelle(saisie))}
  ${scenarios}
  ${fiabilite}
  ${capitalisation}
  ${minimum}
  ${ouverture}
</div>
<div class="carte">
  <div class="fiches">${fiches}</div>
  ${resumeParcours(contexte, saisie)}
</div>
${salaireNet(comparaison, saisie)}
<h2>Pour aller plus loin</h2>
<p class="chapeau">Les quatre montants ci-dessus sont le résultat ; tout ce qui
suit est le détail du calcul, rangé par question. Ouvrez ce que vous voulez
voir.</p>
${trajectoire(contexte, comparaison, saisie)}
${fourchette(contexte, saisie, comparaison)}
${decomposition(contexte, saisie, comparaison)}
${contributionEmployeur(comparaison)}
${garantieVieillesse(comparaison, saisie)}
${pilierCapitalise(comparaison, saisie)}
${detail(contexte, comparaison)}
`;
}

/**
 * Les quatre systèmes, dans l'ordre où la page les affiche, avec le libellé
 * court que la fourchette leur donne.
 */
const SCENARIOS_AFFICHES = SCENARIOS_COMPARES;

/**
 * Ce que l'hypothèse de productivité pèse dans le résultat affiché.
 *
 * Un montant unique se lit comme une prévision. Il n'en est pas une dès qu'une
 * année de la carrière tombe après la dernière observation : il est alors la
 * conséquence d'un scénario, et le lecteur doit voir laquelle.
 *
 * Le bloc rejoue donc la même carrière sous les trois hypothèses du COR et
 * donne l'écart. Quand la liquidation précède la dernière année observée, il
 * n'y a rien à faire varier — et c'est la chose la plus utile qu'on puisse dire
 * à quelqu'un qui redoute les hypothèses : son chiffre n'en contient aucune.
 */
function fourchette(contexte, saisie, comparaison) {
  const macro = contexte.simulateur(saisie.parametres(contexte.base)).macro;
  const derniereObservee = macro.derniereAnneeObservee;
  const carriere = comparaison.carriere;
  const cotisees = carriere.anneesCotisees;
  const liquidation = carriere.anneeLiquidation;
  const debut = cotisees.length ? Math.min(...cotisees) : liquidation;
  const total = liquidation - debut + 1;
  const projetees = Math.max(0, liquidation - Math.max(debut - 1, derniereObservee));

  if (!projetees) {
    return g.depliant("Ce que l'hypothèse pèse", `
<p class="note">Rien, ici : la carrière s'achève en ${liquidation}, et les séries
sont observées jusqu'en ${derniereObservee}. <strong>Aucune année projetée
n'entre dans ce calcul</strong> — les montants ci-dessus sont identiques dans
les trois scénarios macroéconomiques, parce qu'aucun d'eux ne s'y applique.</p>`);
  }

  const montants = new Map();
  for (const [code] of PROJECTIONS) {
    let variante;
    try {
      variante = code === saisie.projection
        ? comparaison
        : contexte.simuler(new Saisie({ ...saisie, projection: code }));
    } catch (erreur) {
      if (fauteDeProgramme(erreur)) throw erreur;
      continue;
    }
    const par_scenario = {};
    for (const [scenario] of SCENARIOS_AFFICHES) {
      par_scenario[scenario] = variante.enEurosConstants(
        variante[scenario].pension_annuelle,
      );
    }
    montants.set(code, par_scenario);
  }

  const basse = montants.get("cor_productivite_basse");
  const haute = montants.get("cor_productivite_haute");
  if (!basse || !haute) {
    return "";
  }
  const retenus = montants.get(saisie.projection);

  const lignes = SCENARIOS_AFFICHES.map(([scenario, libelle]) => {
    const bas = basse[scenario];
    const haut = haute[scenario];
    const amplitude = bas > 0 ? haut / bas - 1 : NaN;
    return [
      echapper(libelle),
      g.eurosCentimes(bas / 12),
      retenus ? g.eurosCentimes(retenus[scenario] / 12) : "—",
      g.eurosCentimes(haut / 12),
      g.pourcentage(amplitude),
    ];
  });

  const retenu = (PROJECTIONS.find(([code]) => code === saisie.projection)
    || [null, ""])[1];
  const reference = comparaison.enEurosConstants(
    comparaison.notionnel_retroactif.pension_annuelle,
  ) / 12;
  const ecart2 = basse.notionnel_retroactif > 0
    ? haute.notionnel_retroactif / basse.notionnel_retroactif - 1
    : NaN;

  // L'emploi projeté, rejoué sous l'autre trajectoire : il ne déplace que les
  // systèmes 2 à 6, par l'indexation, et le lecteur doit le voir.
  const autreEmploi = saisie.emploi !== "constant" ? "constant" : "cor_2026";
  let poidsEmploi = "";
  try {
    const sousAutre = contexte.simuler(new Saisie({ ...saisie, emploi: autreEmploi }));
    const autre2 = sousAutre.enEurosConstants(
      sousAutre.notionnel_retroactif.pension_annuelle,
    ) / 12;
    const ecartEmploi = reference > 0 ? autre2 / reference - 1 : NaN;
    poidsEmploi = `
<p>L'emploi projeté pèse à part. Avec un ${autreEmploi === "constant" ? "emploi constant" : "emploi suivant la trajectoire du COR"}
après ${derniereObservee}, au lieu de ${autreEmploi === "constant" ? "la trajectoire du COR" : "l'emploi constant"} retenu${autreEmploi === "constant" ? "e" : ""} ici, le système 2
donnerait ${g.eurosCentimes(autre2)} par mois, soit
${g.pourcentage(ecartEmploi, true)}. Le système 1 ne bouge pas : il
revalorise sur les prix et ne lit pas l'emploi.</p>`;
  } catch (erreur) {
    if (fauteDeProgramme(erreur)) throw erreur;
  }

  return g.depliant("Ce que l'hypothèse pèse", `
<p>La même carrière, rejouée sous les trois hypothèses du COR. Le système 2
passe de ${g.eurosCentimes(basse.notionnel_retroactif / 12)} à
${g.eurosCentimes(haute.notionnel_retroactif / 12)} par mois, soit
<strong>${g.pourcentage(ecart2)} d'amplitude</strong> autour des
${g.eurosCentimes(reference)} affichés plus haut.${g.bulle(
    "Ce que la fourchette fait varier, et ce qu'elle laisse fixe",
    `Le compte est revalorisé chaque année de ${debut} à ${liquidation}, soit `
    + `${total} années — dont <strong>${projetees} après ${derniereObservee}`
    + "</strong>, la dernière année observée. Ces "
    + `${g.pourcentage(projetees / total)} du calcul ne reposent sur aucune `
    + "mesure, mais sur l'hypothèse de croissance de la productivité que le "
    + "Conseil d'orientation des retraites fixe et révise : 0,4 %, 0,7 % et "
    + "1,0 % par an, le jeu retenu depuis juin 2025. La fourchette laisse "
    + "fixes les autres hypothèses — inflation à 1,75 %, "
    + (saisie.emploi === "constant"
      ? "emploi constant" : "emploi suivant la trajectoire du COR")
    + ", législation inchangée : c'est une mesure de sensibilité à un "
    + "paramètre, non un intervalle de confiance, et l'avenir peut en sortir.",
  )}</p>
${g.tableau(
    ["Système", "Productivité 0,4 %", echapper(retenu), "Productivité 1,0 %",
      "Amplitude"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
    "Pension mensuelle de chaque système sous les trois hypothèses de "
      + "productivité du COR",
    true,
  )}${poidsEmploi}
<p class="discret">Montants mensuels bruts, en euros constants de
${saisie.euros}.</p>`);
}

const NATURES_PART_EMPLOYEUR = {
  appelee: "contribution appelée par décret ou par arrêté",
  implicite: "taux implicite reconstitué par les documents budgétaires",
  repli: "aucune série publiée : effort du privé de la même année",
};

/**
 * Un montant qui est un ÉCART : il se lit avec son signe, positif compris.
 */
function eurosSigne(montant, centimes = true) {
  const signe = montant > 0 ? "+" : "";
  return `${signe}${centimes ? g.eurosCentimes(montant) : g.euros(montant)}`;
}

/**
 * Le mode net/brut, et ce qu'il fait à chaque montant affiché.
 *
 * Un seul objet, construit une fois par rendu, pour que la bascule n'existe
 * qu'à un endroit. Deux grandeurs n'ont pas le même barème — un salaire
 * supporte des cotisations, une pension n'en supporte plus — et deux autres
 * n'ont pas de net du tout : un CAPITAL notionnel et une ASSIETTE de cotisation
 * sont bruts par nature, et le site les laisse tels quels.
 */
export class Montants {
  constructor(net, tauxPension, rapportNetBrutSalaire = 0) {
    this.net = net;
    this.tauxPension = tauxPension;
    // Ce qu'un euro de salaire brut laisse en net, au DERNIER revenu
    // d'activité. Zéro quand le statut n'a pas de fiche de paie : le taux
    // reste alors brut, faute de pouvoir le netter honnêtement.
    this.rapportNetBrutSalaire = rapportNetBrutSalaire;
  }

  static depuis(saisie, simulateur, comparaison = null) {
    // Le rapport net/brut du salaire se lit sur la DERNIÈRE fiche de paie de
    // la carrière, celle de l'année du départ : c'est l'année dont le revenu
    // sert de dénominateur au taux de remplacement.
    let rapport = 0;
    const remuneration = comparaison ? comparaison.remuneration : null;
    if (remuneration !== null && remuneration !== undefined) {
      const derniere = remuneration.annees[remuneration.annees.length - 1]
        .droitEnVigueur;
      if (derniere.brut > 0) {
        rapport = derniere.net / derniere.brut;
      }
    }
    return new Montants(saisie.enNet,
      simulateur.baremePrelevements.pensions.tauxTotal, rapport);
  }

  /**
   * Le taux de remplacement, dans la langue du mode.
   *
   * Le modèle le calcule brut sur brut. Affiché à côté de montants NETS, il
   * serait le seul chiffre de la page à parler l'autre langue — et il
   * mentirait dans un sens précis : une pension est moins prélevée qu'un
   * salaire, 9,1 % contre une vingtaine de points, si bien que le taux NET
   * dépasse le taux brut de plusieurs points. C'est un fait connu, et rarement
   * montré.
   */
  tauxRemplacement(tauxBrut) {
    if (!this.net || this.rapportNetBrutSalaire <= 0) {
      return tauxBrut;
    }
    return tauxBrut * (1 - this.tauxPension) / this.rapportNetBrutSalaire;
  }

  /** Une pension, une rente, une garantie : tout ce qui se sert après. */
  pension(brut) {
    return this.net ? brut * (1 - this.tauxPension) : brut;
  }

  /** Un salaire, lu sur la fiche de paie qui porte déjà les deux. */
  salaire(fiche) {
    return this.net ? fiche.net : fiche.brut;
  }

  get mot() {
    return this.net ? "net" : "brut";
  }

  get uniteSalaire() {
    return this.net ? "€ net/mois" : "€ brut/mois";
  }

  get unitePension() {
    return this.net ? "€ net/mois" : "€ brut/mois";
  }
}

/**
 * Ce que le mode courant suppose, en une phrase, là où il s'applique.
 *
 * En NET, c'est la convention de CSG qu'il faut dire : la loi fait dépendre le
 * taux du revenu fiscal du foyer, que le simulateur ne demande pas, et le dépôt
 * retient le taux plein. En BRUT, c'est le rappel qu'un brut n'est pas ce qu'on
 * touche.
 */
function noteDuMode(montants) {
  if (montants.net) {
    return "La pension est nette de "
      + `${g.pourcentage(montants.tauxPension, false, 1)} : CSG, CRDS `
      + "et contribution de solidarité, au <strong>taux plein</strong>. La "
      + "loi fait dépendre ce taux du revenu fiscal du foyer, que ce "
      + "simulateur ne demande pas : une petite pension, exonérée en "
      + "réalité, est donc ici un peu sous-estimée.";
  }
  return "Le brut n'est pas ce qui arrive sur le compte : il reste à en "
    + "retirer les cotisations pour un salaire, la CSG pour une pension.";
}

/**
 * Le statut dont le modèle ne sait pas faire la fiche de paie, s'il y en a.
 *
 * L'exploitant agricole relève de la MSA, l'élu touche une indemnité de
 * fonction, l'ultramarin a la caisse de sa collectivité. Le nombre saisi est
 * alors lu comme un brut, et le taire ferait croire à une conversion qui n'a
 * pas eu lieu.
 */
function mentionConversion(saisie, echelle) {
  if (!saisie.saisieEnNet) {
    return "";
  }
  const sans = saisie.lignesCarriere.filter(
    (ligne) => !ligne.sans_emploi && !echelle.convertit(ligne.statut),
  );
  if (!sans.length) {
    return "";
  }
  return '<p class="note avertissement" style="margin-top:0.6rem">'
    + g.icone("triangle-alert", "Avertissement")
    + "<span>Le modèle ne connaît pas les prélèvements hors retraite "
    + "de l'un de vos statuts : pour lui, le montant saisi est lu "
    + "<strong>tel quel</strong>, comme un brut. La pension, elle, reste "
    + "affichée en net.</span></p>";
}

/**
 * Le lien qui passe de net à brut, et retour — montants déjà traduits.
 *
 * LES MONTANTS SAISIS SONT TRADUITS, et c'est tout l'enjeu : en mode net, le
 * nombre du formulaire est un net. Le recopier tel quel dans l'autre mode le
 * ferait relire comme un brut, et la page reviendrait en décrivant une AUTRE
 * carrière — mieux payée d'un quart.
 */
function basculeMontants(saisie, echelle) {
  const versLeNet = !saisie.enNet;
  const remplacements = { montants: versLeNet ? "net" : "brut" };
  // Seule la saisie EN EUROS porte un net ou un brut : un multiple du salaire
  // moyen est un rapport entre deux bruts, que le mode ne touche pas.
  if (saisie.revenu_en_euros) {
    const lignes = saisie.lignesCarriere;
    const traduits = lignes.map((ligne) => nombreBrut(Math.round(
      versLeNet
        ? echelle.netMensuel(ligne.salaire, ligne.statut)
        : echelle.brutMensuelDirect(ligne.salaire, ligne.statut),
    ), 0));
    remplacements.salaire = traduits[0];
    traduits.slice(1).forEach((valeur, index) => {
      remplacements[`metier${index + 2}_salaire`] = valeur;
    });
  }
  // PAS D'ANCRE AU BOUT DE L'ADRESSE : la route vit déjà dans le fragment,
  // et un second `#` allonge la dernière valeur de la requête au lieu de
  // désigner une section — `montants=brut#resultats` n'est pas un mode.
  const cible = `#/simuler?${echapper(saisie.requete(remplacements))}`;
  // L'état courant n'a pas d'adresse : c'est celle où l'on est déjà.
  const branches = versLeNet
    ? [["net", cible], ["brut", "#"]]
    : [["net", "#"], ["brut", cible]];
  return g.bascule("Montants", branches, saisie.enNet ? "net" : "brut");
}

/**
 * Ce qu'un actif touche PENDANT qu'il cotise, dans les deux systèmes.
 *
 * Portage de `_salaire_net` de `web/pages.py`. Le reste de la page compare des
 * pensions, c'est-à-dire des montants qu'on touchera dans trente ans ; ce bloc
 * compare des salaires, c'est-à-dire des montants qu'on touche le mois
 * prochain. C'est la seule ligne du site où une réforme des retraites se lit
 * sur une fiche de paie.
 *
 * Trois chiffres ouverts, le reste replié : la page de résultats tient un
 * budget de mots et n'ouvre aucun tableau.
 *
 * Quatre profils, et un libellé par profil : ce qui s'écrit « salaire » pour un
 * salarié du privé s'écrit « traitement » pour un fonctionnaire et « revenu
 * professionnel » pour un indépendant ; et la ligne « coût du travail » ne
 * s'affiche que là où ce que verse l'employeur est un prix du travail, non un
 * taux d'équilibre.
 */
function salaireNet(comparaison, saisie) {
  const remuneration = comparaison.remuneration;
  if (remuneration === null) {
    return "";
  }
  const reference = remuneration.reference;
  const avant = reference.droitEnVigueur;
  const apres = reference.proposition;
  const gain = remuneration.gainNetMensuel;

  const net = echapper(remuneration.libelleNet.toLowerCase());
  const ouverture = [
    g.fiche(`votre ${net} en ${reference.annee}`, g.eurosCentimes(avant.net / 12)),
    g.fiche("avec le système 4", g.eurosCentimes(apres.net / 12)),
    g.fiche("par mois", eurosSigne(gain)),
  ].join("");
  const sens = gain >= 0 ? "de plus" : "de MOINS";
  const duree = remuneration.annees.length;
  const cumul = remuneration.gainNetCumule;
  const reste = duree > 1
    ? ` Sur les ${duree} années qui vous séparent de la retraite : `
      + `${eurosSigne(cumul, false)} en euros de ${saisie.euros}.`
    : "";
  // Deux hypothèses, et il faut dire laquelle vaut ici : le coût du travail
  // tenu fixe quand l'employeur verse des taux de droit commun, l'assiette
  // tenue fixe quand il verse un taux d'équilibre — ou qu'il n'y en a pas.
  const sousQuelleHypothese = remuneration.afficheCoutDuTravail
    ? "à coût du travail inchangé pour votre employeur"
    : `à ${echapper(remuneration.libelleAssiette.toLowerCase())} inchangé`;
  // LE CHIFFRE DU MILIEU EST LE NET PLEIN : ce que la proposition laisse quand
  // elle a prélevé ses 23 points, et rien d'autre. Les cinq points que
  // personne n'impose n'en sont pas retirés — une épargne qu'on décide seul
  // n'est pas une retenue sur salaire —, mais la rente du système 4 affichée
  // plus haut les suppose placés, et il faut le dire dans la même phrase.
  let volontaire = "";
  if (remuneration.verseLeVolontaire) {
    const parametres = comparaison.parametres;
    const impose = tauxRetraitePropose(parametres)
      - tauxCapitalisationVolontaireApplique(parametres);
    const resteApres = reference.netApresVolontaire / 12;
    const ecartApres = remuneration.gainNetMensuelApresVolontaire;
    volontaire = ` C'est votre ${net} plein : le système 4 prélève
  ${g.pourcentage(impose, false, 0)} pour la retraite, et rien d'autre. La
  rente qu'il affiche plus haut suppose en plus que vous placez les
  <strong>${g.pourcentage(tauxCapitalisationVolontaireApplique(parametres), false, 0)}
  de capitalisation volontaire</strong> que la proposition vous rend — soit
  ${g.eurosCentimes(remuneration.epargneVolontaireMensuelle)} par mois virés
  de votre ${net} sur un compte à votre nom, pas une retenue —, pour cotiser
  ${g.pourcentage(tauxRetraitePropose(parametres), false, 0)} en tout, comme
  aujourd'hui. Il vous reste alors ${g.eurosCentimes(resteApres)} par mois,
  soit ${eurosSigne(ecartApres)} par rapport à aujourd'hui. Si vous ne les
  placez pas, vous gardez le ${net} plein, et la rente du système 4 baisse de la
  part nommée « des cinq points volontaires ».`;
  }

  return `
<h2 id="salaire-net">Et pendant que vous cotisez</h2>
<p class="chapeau">Une réforme des retraites ne change pas que votre pension :
elle change ce qui est prélevé sur votre travail, donc ce que vous touchez
chaque mois. Les systèmes 1, 2 et 3 prélèvent la même chose — ils ne changent
que ce qui est porté au compte. Le système 4, lui, y touche.</p>
<div class="carte">
  <div class="fiches">${ouverture}</div>
  <p>Soit <strong>${eurosSigne(gain)} ${sens} sur votre fiche de paie</strong>,
  ${sousQuelleHypothese}.${reste}${volontaire}</p>
  ${salaireNetDetail(comparaison, remuneration, saisie)}
</div>`;
}

/** La fiche de paie entière, et ce qu'il faut savoir pour la discuter. */
function salaireNetDetail(comparaison, remuneration, saisie) {
  const reference = remuneration.reference;
  const avant = reference.droitEnVigueur;
  const apres = reference.proposition;
  const mois = (montant) => g.eurosCentimes(montant / 12);
  // TROIS COLONNES, ET NON QUATRE. Une colonne « écart » de plus forçait le
  // tableau à défiler latéralement sur un téléphone, et l'écart qui compte —
  // celui du net — est déjà le chiffre de tête.
  //
  // LA PREMIÈRE LIGNE N'EST PAS TOUJOURS LÀ. Le coût du travail suppose de
  // savoir ce que l'employeur verse ; quand ce qu'il verse est un taux
  // d'équilibre, ce n'est pas un prix du travail, et l'afficher tromperait.
  const avecCout = remuneration.afficheCoutDuTravail;
  const assiette = echapper(remuneration.libelleAssiette);
  const libelleNet = echapper(remuneration.libelleNet);
  const lignes = [];
  if (avecCout) {
    // Le mot s'affiche avec sa capitale, comme les autres intitulés de ligne,
    // mais renvoie à la même entrée du glossaire.
    lignes.push([g.terme("Coût du travail", "coût du travail"),
      mois(avant.coutDuTravail), mois(apres.coutDuTravail)]);
  }
  // Ce qu'on met sous « dont pour la retraite » suit la même logique : les deux
  // parts réunies quand la colonne part d'un coût du travail, la seule part de
  // l'assuré quand elle part de son assiette.
  const retraiteAvant = avecCout ? avant.retraiteTotale : avant.retraiteSalarie;
  const retraiteApres = avecCout ? apres.retraiteTotale : apres.retraiteSalarie;
  lignes.push(
    [assiette, mois(avant.brut), mois(apres.brut)],
    [`<strong>${libelleNet}</strong>`, `<strong>${mois(avant.net)}</strong>`,
      `<strong>${mois(apres.net)}</strong>`],
    [avecCout ? "Dont pour la retraite" : "Dont pour la retraite, à votre charge",
      mois(retraiteAvant), mois(retraiteApres)],
  );
  // Le placement que l'assuré décide seul. Il est SOUS le net, et non dans le
  // prélèvement retraite : rien ne l'impose, la fiche ne le retient pas, et le
  // net écrit au-dessus est le net plein. La colonne « Systèmes 1 à 3 » y porte
  // un tiret, et la ligne suivante dit ce qui reste à qui le fait.
  if (reference.epargneVolontaire > 0) {
    lignes.push(
      ["Placé volontairement sur un compte à votre nom, les points rendus",
        "—", mois(reference.epargneVolontaire)],
      [`${libelleNet} restant si vous les placez`, mois(avant.net),
        mois(reference.netApresVolontaire)],
    );
  }
  lignes.push(
    [avecCout ? "Ce qui vous arrive, sur 100 € coûtés"
      : `Ce qui vous reste, sur 100 € de ${assiette.toLowerCase()}`,
    g.pourcentage(avecCout ? avant.partQuiArrive : avant.net / avant.brut),
    g.pourcentage(avecCout ? apres.partQuiArrive : apres.net / apres.brut)],
  );
  const grille = g.tableau(
    ["Par mois", "Systèmes 1 à 3", "Système 4"],
    lignes, ["", "nombre", "nombre"],
    `Votre fiche de paie en ${reference.annee}, sous les quatre systèmes — `
    + `${remuneration.libelleStatut}`,
    true,
  );
  const lecture = avecCout
    ? "<p>Le coût du travail ne bouge pas : c'est l'hypothèse. Le "
      + `prélèvement retraite, lui, passe de ${mois(retraiteAvant)} à `
      + `${mois(retraiteApres)} par mois, soit `
      + `<strong>${eurosSigne((retraiteApres - retraiteAvant) / 12)}`
      + "</strong> ; le salaire brut monte de "
      + `${eurosSigne((apres.brut - avant.brut) / 12)}, et le net de `
      + `${eurosSigne((apres.net - avant.net) / 12)}.</p>`
    : `<p>Le ${assiette.toLowerCase()} ne bouge pas : c'est l'hypothèse, et ici `
      + "c'est la seule disponible. Ce que vous versez pour votre retraite "
      + `passe de ${mois(retraiteAvant)} à ${mois(retraiteApres)} par mois, `
      + `soit <strong>${eurosSigne((retraiteApres - retraiteAvant) / 12)}`
      + "</strong> ; votre net bouge donc de "
      + `${eurosSigne((apres.net - avant.net) / 12)}.</p>`;

  const alerte = remuneration.buteSurLeSmic
    ? '<p class="note avertissement">'
      + g.icone("triangle-alert", "Avertissement")
      + "<span>À ce niveau de salaire, le calcul ci-dessus suppose un "
      + "salaire brut <strong>inférieur au SMIC</strong>, ce que la loi "
      + "interdit. Dans la réalité, c'est le coût du travail qui monterait, "
      + "et non le salaire qui baisserait : l'emploi coûterait plus cher à "
      + "l'employeur, pour un net inchangé.</span></p>"
    : "";

  return g.depliant("Votre fiche de paie, ligne à ligne", `
${grille}
${lecture}
${alerte}
${salaireNetEpargne(reference.epargneAVotreNom / 12, remuneration,
    comparaison.parametres, saisie)}
${salaireNetMethode(comparaison, remuneration)}`);
}

/**
 * Les cinq points capitalisés : prélevés sur le net, mais acquis à l'assuré.
 *
 * Les compter dans le gain serait faux — ils ne tombent pas sur le compte en
 * banque. Les taire le serait aussi : contrairement à une cotisation, ce que ce
 * prélèvement achète reste au nom de l'assuré et se transmet.
 */
function salaireNetEpargne(epargne, remuneration, parametres, saisie) {
  if (epargne <= 0) {
    return "";
  }
  const taux = g.pourcentage(parametres.taux_capitalisation_obligatoire, false, 0);
  const volontaire = g.pourcentage(
    tauxCapitalisationVolontaireApplique(parametres), false, 0,
  );
  const repartition = g.pourcentage(parametres.taux_cotisation_liberal, false, 0);
  const total = g.pourcentage(tauxRetraitePropose(parametres), false, 0);
  const ajout = remuneration.verseLeVolontaire
    ? ` Les ${volontaire} <strong>volontaires</strong> n'y sont pas : la `
      + "fiche de paie ne les retient pas, personne ne les impose. Ce sont "
      + "les points que la proposition vous rend, et que le site suppose "
      + "placés sur le même compte, pris sur votre net — soit "
      + `${g.eurosCentimes(remuneration.epargneVolontaireMensuelle)} `
      + `par mois et ${g.euros(remuneration.epargneVolontaireCumulee)} `
      + `d'ici votre départ. Vous cotisez alors ${total} en tout, `
      + "c'est-à-dire ce que vous versez déjà aujourd'hui — c'est à ce "
      + "prix-là que la rente du système 4 est calculée, et la part qui "
      + "en vient est nommée à côté d'elle."
    : "";
  return `<p class="note resume"><strong>${g.eurosCentimes(epargne)} par mois `
    + "de ce prélèvement est de l'épargne à votre nom.</strong> Le système 4 "
    + `prélève ${taux} par-dessus les ${repartition} de répartition, et ces `
    + "cinq points ne partent pas : ils alimentent un compte qui reste le "
    + "vôtre, transmissible à vos héritiers tant qu'il n'est pas liquidé — "
    + `${g.euros(remuneration.epargneCumulee)} d'ici votre départ, en euros `
    + `de ${saisie.euros}.${ajout} `
    + (remuneration.afficheCoutDuTravail
      ? "Sans eux, le salaire net monterait à tous les niveaux de salaire ; "
        + "avec eux, il baisse au voisinage du SMIC."
      : "Sans eux, le chiffre du haut remonterait de la part que vous en "
        + "supportez : ce que vous perdez en net, vous le retrouvez sur ce "
        + "compte.")
    + "</p>";
}

/**
 * Ce qu'il faut savoir pour discuter le chiffre plutôt que le croire.
 *
 * Le premier paragraphe est celui qui change d'un profil à l'autre, et c'est le
 * plus important : il dit ce que le modèle tient FIXE, et pourquoi il n'a pas
 * le choix quand l'employeur verse un taux d'équilibre.
 */
function salaireNetMethode(comparaison, remuneration) {
  const parametres = comparaison.parametres;
  const part = g.pourcentage(parametres.part_salariale_taux_unique, false, 0);
  const assiette = echapper(remuneration.libelleAssiette.toLowerCase());
  return `
<h3>Comment ce chiffre est calculé, et ce qu'il suppose</h3>
${salaireNetIncidence(remuneration, assiette)}
${salaireNetPartage(remuneration, parametres, part)}
${salaireNetAllegement(remuneration)}
${salaireNetPerimetre(remuneration)}
<p class="discret">Taux hors retraite : millésime ${remuneration.millesimeBareme},
appliqué tel quel aux années à venir — le modèle ne prévoit pas la prochaine loi
de financement. Fiabilité : ${g.fiabiliteEnClair(nomFiabilite(remuneration.fiabilite))}. Les taux de
retraite, eux, sont ceux des fiches de régime : la fiche de paie prélève
exactement ce que le compte notionnel encaisse.</p>`;
}

/** Ce que le modèle tient fixe — et, pour le public, pourquoi il le doit. */
function salaireNetIncidence(remuneration, assiette) {
  if (remuneration.afficheCoutDuTravail) {
    return `<p><strong>Le coût du travail est tenu fixe.</strong> C'est ce que votre
employeur a budgété pour votre poste, et aucune réforme des retraites ne le
change. Ce qu'il ne verse plus en cotisations, il le verse en salaire : le brut
monte, et le net avec lui. C'est ce que veut dire « réduire l'écart entre le net
et le brut », et c'est l'hypothèse la plus favorable à une baisse de cotisation
— une cotisation patronale est du salaire différé, mais rien n'oblige un
employeur à le rendre du jour au lendemain.</p>`;
  }
  if (remuneration.profil === "independant") {
    return `<p><strong>Votre ${assiette} est tenu fixe, et il n'y a pas de coût du
travail à afficher</strong> : vous n'avez pas d'employeur, et votre cotisation
est intégralement personnelle. Ce qu'une baisse de taux vous rend vous revient
donc en entier, sans qu'il faille supposer qui que ce soit pour le répercuter —
c'est le seul des quatre profils où l'incidence n'est pas une hypothèse.
L'assiette retenue est l'assiette sociale unique : votre revenu professionnel
après l'abattement de 26 %, qui sert depuis 2025 aux cotisations comme à la
CSG.</p>`;
  }
  return `<p><strong>Votre ${assiette} est tenu fixe, et le site n'affiche pas de
coût du travail pour votre statut.</strong> Ce n'est pas un oubli, c'est un
refus. Ce que verse votre employeur n'est pas le prix de votre travail mais un
<strong>taux d'équilibre</strong> — jusqu'à 82,28 % du traitement pour l'État en
2026 —, fixé pour que le compte « Pensions » tombe juste, c'est-à-dire pour
payer les pensions d'aujourd'hui, et non parce que vous acquerriez 82 % de votre
traitement en droits nouveaux. Le traiter comme un coût du travail et supposer
qu'une baisse vous reviendrait en salaire afficherait une augmentation de
soixante-dix points qui n'existe pas : cette contribution finance une dette de
pensions qui, elle, reste à payer. C'est la page <a href="${g.lien("/cout")}">Coût</a>
qui en traite.</p>
<p>Le chiffre ci-dessus est donc la lecture <strong>prudente</strong> : seule la
part que vous supportez bouge. Il n'est pas comparable, terme à terme, au gain
d'un salarié du privé, dont le site fait remonter la part patronale dans le
brut.</p>`;
}

/** Le partage des 18 %, et ce qu'il pèse — ou ne pèse pas, sans employeur. */
function salaireNetPartage(remuneration, parametres, part) {
  const repartition = g.pourcentage(parametres.taux_cotisation_liberal, false, 0);
  const capitalise = g.pourcentage(
    parametres.taux_capitalisation_obligatoire, false, 0,
  );
  const volontaire = g.pourcentage(
    tauxCapitalisationVolontaireApplique(parametres), false, 0,
  );
  // Les cinq points volontaires échappent au partage : personne ne cofinance
  // une épargne que l'assuré décide seul. Ils ne sont donc pas sur la fiche —
  // le net affiché est le net plein — et, placés, ils pèsent leur montant
  // entier là où les points imposés n'en coûtent que la moitié.
  const horsPartage = (remuneration.verseLeVolontaire
    && remuneration.profil !== "independant")
    ? `
<p><strong>Les ${volontaire} volontaires, eux, ne sont sur la fiche de paie de
personne.</strong> Aucun employeur ne cofinance une épargne que son salarié
décide seul : le site les compte comme un placement pris sur votre net, porté
en entier par vous, et ni le coût du travail, ni le brut, ni le net ne bougent
quand vous le faites. C'est pourquoi, si vous les placez, ils pèsent leur
montant entier, quand les ${capitalise} imposés ne vous en coûtent que la
moitié.</p>` : "";
  if (remuneration.profil === "independant") {
    return `<p><strong>Les ${repartition} et les ${capitalise} capitalisés sont à votre
charge en entier.</strong> La proposition les annonce « salariale et patronale
additionnées » ; vous êtes les deux à la fois, comme vous l'êtes déjà des
vingt-six points que vous versez aujourd'hui. Vous prêter un employeur pour la
moitié de la charge fabriquerait un gain qui n'existe pas. Les ${volontaire}
volontaires, eux, ne sont pas sur la fiche : c'est un placement pris sur votre
revenu net, à votre charge en entier, et pour une autre raison — personne ne
cofinance une épargne qu'on décide seul. Votre profil est le seul où les trois
taux pèsent de la même façon.</p>`;
  }
  if (!remuneration.afficheCoutDuTravail) {
    return `<p><strong>Les ${repartition} sont partagés moitié-moitié</strong> entre
vous et votre employeur, comme les ${capitalise} capitalisés : votre part est
donc de ${part} de chacun. La proposition ne dit pas
qui porte quoi, et ce partage commande directement le chiffre ci-dessus —
puisque seule votre part y figure, tout déplacer vers l'employeur ferait
disparaître la hausse, et tout déplacer vers vous la doublerait.</p>${horsPartage}`;
  }
  return `<p><strong>Les ${repartition}
sont partagés moitié-moitié</strong> entre vous et votre employeur, comme les
${capitalise}
capitalisés. La proposition ne dit pas qui porte quoi, et ce partage n'est pas
neutre : la CSG est assise sur le brut, et l'allègement sur les bas salaires ne
porte que sur la part patronale. Tout mettre côté employeur donnerait un gain
bien plus gros, tout mettre côté salarié le rendrait négatif. Le chiffre affiché
est le partage du milieu (${part} pour vous).</p>${horsPartage}`;
}

/** L'allègement sur les bas salaires — quand il s'applique, et sinon pourquoi. */
function salaireNetAllegement(remuneration) {
  if (remuneration.afficheCoutDuTravail) {
    return `<p><strong>L'allègement sur les bas salaires est calculé, pas ignoré.</strong>
Depuis 2026, il efface au niveau du SMIC la totalité des cotisations patronales
qu'il vise — son coefficient, 40,21 %, est exactement leur somme — et s'éteint à
trois SMIC. Conséquence, et elle va à contre-courant : <strong>au SMIC, baisser
la cotisation retraite de l'employeur ne rend rien</strong>, puisqu'il n'en
versait déjà plus. La loi fixe ce coefficient « dans la limite de la somme des
taux » du périmètre ; le modèle refait donc l'addition sous la proposition au
lieu de garder le chiffre d'aujourd'hui.</p>`;
  }
  return `<p><strong>L'allègement sur les bas salaires ne joue pas ici.</strong> La
réduction générale de l'article L. 241-13 n'efface que des cotisations
patronales du régime général ; elle ne s'applique ni à la retenue d'un
fonctionnaire, ni aux cotisations personnelles d'un indépendant. C'est pourtant
elle qui commande le résultat d'un salarié du privé, chez qui elle rend nul, au
voisinage du SMIC, le gain d'une baisse de cotisation patronale — une raison de
plus de ne pas comparer les deux chiffres sans précaution.</p>`;
}

/** Ce que la fiche ne porte pas, et qui n'est pas le même selon le profil. */
function salaireNetPerimetre(remuneration) {
  if (remuneration.profil === "independant") {
    return `<p><strong>Ce que la fiche ne porte pas</strong> : la contribution à la
formation professionnelle, qui est un forfait de 0,25 % du plafond et non un
taux, et l'assiette minimale que la loi impose aux très bas revenus — le net
affiché en bas de barème est donc un plafond. Vos cotisations de retraite sont
celles des fiches de régime, qui alignent l'artisan et le commerçant sur le
régime général : c'est la convention du modèle entier, et elle vaut ici comme
pour la pension.</p>`;
  }
  if (!remuneration.afficheCoutDuTravail) {
    return `<p><strong>Ce que la fiche ne porte pas</strong> : la retraite
additionnelle de la fonction publique, assise sur les PRIMES, que l'assiette de
ce modèle — le traitement indiciaire brut et la nouvelle bonification
indiciaire — exclut par construction. Un agent dont les primes pèsent lourd voit
donc ici une fraction de sa rémunération, et non sa feuille de paie entière. Les
autres prélèvements salariaux sont nuls, et c'est un résultat : la cotisation
maladie salariale a disparu en 2018 comme dans le privé, un titulaire n'est pas
assuré contre le chômage, et la contribution exceptionnelle de solidarité de 1 %
a été supprimée la même année.</p>`;
  }
  return `<p><strong>Ce que la fiche ne porte pas</strong> : la taxe
d'apprentissage, la formation professionnelle, la participation à la
construction, le versement mobilité, la prévoyance et la mutuelle d'entreprise.
Aucune ne bouge d'un système à l'autre, et plusieurs dépendent de la commune ou
de la taille de l'entreprise. Le coût du travail affiché est donc un plancher.
L'employeur type est une entreprise de cinquante salariés et plus.</p>`;
}

/**
 * Qui verse la cotisation : l'assuré, son employeur, dans quelle proportion.
 *
 * C'est la mesure directe de ce qui sépare les scénarios 2 et 3 des scénarios 4
 * et 5. Le bloc ne s'affiche pas pour un non-salarié, qui n'a pas d'employeur.
 */
function contributionEmployeur(comparaison) {
  const employeur = comparaison.contributionEmployeur;
  if (!(employeur.a_un_employeur || employeur.concerne_un_regime_public)) {
    return "";
  }

  const partage = employeur.a_un_employeur
    ? g.tableau(
      ["Part", "Ce qu'elle recouvre", "Montant"],
      [
        ["Part salariale", "ce que l'assuré supporte — système 2",
          g.euros(employeur.agent)],
        ["Part patronale", "ce que verse l'employeur", g.euros(employeur.employeur)],
        ["Total", "système 3", g.euros(employeur.total)],
      ],
      ["", "", "nombre"],
      "Cotisations versées sur toute la carrière, en euros courants cumulés",
      true,
    ) + `<p>L'employeur verse ici <strong>${g.pourcentage(employeur.part)}`
      + "</strong> du total.</p>"
    : "";

  // La part patronale d'un agent public n'est dans aucune fiche : elle vient
  // d'une série à part, qui ne couvre pas tous les régimes ni toutes les
  // années. Le dire est le prix de s'en servir.
  let public_ = "";
  if (employeur.concerne_un_regime_public) {
    const origines = Object.entries(employeur.annees_par_origine)
      .sort((a, b) => (a[0] < b[0] ? -1 : 1))
      .map(([origine, nombre]) => `<li>${
        echapper(NATURES_PART_EMPLOYEUR[origine] ?? origine)
      } — ${nombre} année${nombre > 1 ? "s" : ""}</li>`)
      .join("");
    public_ = `
<p>Les fiches de la fonction publique et des régimes spéciaux ne portent que la
<strong>retenue de l'agent</strong>. La part de l'employeur vient d'une série à
part — reconstituée par les documents budgétaires de 1995 à 2005, appelée par
décret depuis 2006 pour l'État, versée à une caisse depuis 1948 pour la fonction
publique territoriale et hospitalière. Origine, année par année :</p>
<ul class="serree">${origines}</ul>
<p class="discret">Et c'est la limite de ces deux scénarios pour un agent
public. Un taux de 82,28 % ne signifie pas qu'un fonctionnaire acquiert 82 % de
son traitement en droits nouveaux : il est fixé pour que le compte
d'affectation spéciale « Pensions » soit à l'équilibre, donc pour payer les
pensions d'aujourd'hui. Le porter au compte répond à une question précise —
« et si tout ce qui a été consacré aux pensions avait été porté au compte des
actifs ? » — et à elle seule.</p>`;
  }

  return g.depliant("Qui verse la cotisation", `
<p>Une cotisation retraite a deux parts : ce que l'assuré supporte, et ce que
son employeur verse.${g.bulle(
    "Ce que les scénarios portent au compte",
    "Le système 2 ne porte au compte que la première ; le système 3 "
    + "y ajoute la seconde, et ne change rien d'autre.",
  )}</p>
${partage}${public_}`);
}

/** Sépare l'effet de la règle d'indexation de celui des comptes notionnels. */
// Les couples du tableau de la proposition, en euros mensuels : deux pensions,
// ou une seule pour une personne seule. La page les recalcule avec la règle que
// le scénario applique, plutôt que de les recopier.
const EXEMPLES_GARANTIE = [
  [[300.0, 300.0], "300 € et 300 €"],
  [[300.0, 1500.0], "300 € et 1 500 €"],
  [[900.0, 900.0], "900 € et 900 €"],
  [[300.0, 5000.0], "300 € et 5 000 €"],
  [[300.0], "personne seule, 300 €"],
];

/**
 * Le pilier capitalisé : ce qu'il reçoit, ce qu'il rend, ce qu'il lègue.
 *
 * Portage de `_pilier_capitalise`. C'est la seule ligne de tout le site où de
 * l'argent est réellement placé : le bloc doit donc dire où va l'argent, ce
 * qu'il coûte, et ce qu'il devient si l'assuré meurt avant d'avoir liquidé.
 * La dernière n'est pas un détail de présentation : c'est ce que la
 * capitalisation donne et que la répartition ne donne pas, et c'est aussi ce
 * qui explique qu'elle rapporte moins à rente égale.
 */
function pilierCapitalise(comparaison, saisie) {
  const liberal = comparaison.notionnel_liberal;
  const pilier = liberal.capitalisation;
  if (pilier === null || pilier === undefined) return "";

  const parametres = comparaison.parametres;
  const taux = g.pourcentage(pilier.taux_cotisation, false, 0);
  const tauxImpose = g.pourcentage(pilier.taux_cotisation_obligatoire, false, 0);
  const tauxVolontaire = g.pourcentage(
    pilier.taux_cotisation_volontaire, false, 0,
  );
  const avecVolontaire = pilier.taux_cotisation_volontaire > 0;
  const depart = comparaison.carriere.anneeLiquidation;
  const titre = `Le pilier capitalisé : ${taux} placés dès `
    + `${parametres.annee_debut_capitalisation}`;

  if (!pilier.actif) {
    return g.depliant(titre, `
<p>Cette carrière ne cotise pas au pilier : elle s'achève en ${depart}, et la
cotisation capitalisée n'est due qu'à compter de
${parametres.annee_debut_capitalisation}. La proposition ne demande rien au
passé — ni ce taux, ni un autre —, et qui a liquidé avant la bascule reçoit
donc, du système 4, la seule pension de répartition.</p>`);
  }

  const premiere = pilier.annees[0];
  const derniere = pilier.annees[pilier.annees.length - 1];

  // Les frais sont des paramètres, et ils bougent : chaque ligne de la
  // cascade dit le tarif de la première année et celui de la dernière, tels
  // que le pilier les a effectivement subis. Changer le barème change la page.
  const fourchette = (debut, fin) => (
    Math.abs(debut - fin) < 5e-7
      ? g.pourcentage(debut, false, 2)
      : `de ${g.pourcentage(debut, false, 2)} à ${g.pourcentage(fin, false, 2)}`
  );
  const renteBrute = pilier.capital / pilier.conversion.diviseur;
  const renteApresReserve = renteBrute * pilier.facteur_encours_rente;

  // Ce que devient un euro versé : la cascade complète, du prélèvement à la
  // rente. Chaque ligne est une opération, et la suivante part du résultat de
  // la précédente — c'est la seule façon de rendre un capital vérifiable.
  const cascade = g.tableau(
    ["", "Ce qui se passe", `Montant, en euros de ${depart}`],
    [
      [`a) Cotisation de ${taux}`,
        (avecVolontaire
          ? `${tauxImpose} imposés et ${tauxVolontaire} volontaires, ` : "")
        + "prélevés sur la même assiette que la cotisation notionnelle, de "
        + `${premiere.annee} à ${derniere.annee}, EN PLUS d'elle`,
        g.euros(pilier.versements)],
      ["b) − frais sur versement",
        `${fourchette(premiere.taux_frais_versement, derniere.taux_frais_versement)} `
        + `de chaque versement, de ${premiere.annee} à ${derniere.annee}`,
        `− ${g.euros(pilier.frais_versement)}`],
      ["c) + intérêts",
        "placés sur des titres sans risque, à des maturités qui raccourcissent "
        + "à l'approche du départ",
        `+ ${g.euros(pilier.interets)}`],
      ["d) − frais de gestion",
        `${fourchette(premiere.taux_frais_gestion, derniere.taux_frais_gestion)} `
        + "par an sur l'encours, chaque versement gardant le tarif de son année",
        `− ${g.euros(pilier.frais_gestion)}`],
      ["e) = capital au départ",
        "ce que vaut le compte le jour de la liquidation",
        g.euros(pilier.capital)],
      ["f) ÷ coefficient de conversion",
        `${g.nombre(pilier.conversion.diviseur, DECIMALES_DIVISEUR)}, la même `
        + "table de mortalité que la pension notionnelle",
        `${g.euros(renteBrute)} par an`],
      ["g) − frais sur la réserve de rente",
        `${g.pourcentage(pilier.frais_encours_rente, false, 2)} par an `
        + "sur la réserve qui porte la rente, au tarif de l'année du départ",
        `− ${g.euros(renteBrute - renteApresReserve)} par an`],
      ["h) − frais sur arrérages",
        `${g.pourcentage(pilier.frais_arrerages, false, 2)} `
        + "de chaque versement de rente, au tarif de l'année du départ",
        `− ${g.euros(renteApresReserve - pilier.rente_annuelle)} par an`],
      ["i) = rente servie", "à vie, et qui s'éteint avec le rentier",
        `${g.eurosCentimes(pilier.rente_annuelle)} par an`],
    ],
    ["", "texte", "nombre"],
    "D'un euro cotisé à un euro de rente",
    true,
  );

  // L'échelle de maturités, telle qu'elle a effectivement servi : le premier
  // versement et le dernier. Deux lignes suffisent à montrer le glissement.
  const placements = (annee) => {
    if (annee.placements.length === 0) {
      return "gardé disponible : le départ a lieu dans l'année";
    }
    return annee.placements.map(([maturite, part]) => `${g.pourcentage(part / annee.versement_net)} à `
      + `${maturite} an${maturite > 1 ? "s" : ""}`).join(", ");
  };

  const echelle = g.tableau(
    ["Versement", "Années avant le départ", "Placé"],
    [
      [String(premiere.annee), `${premiere.horizon}`, placements(premiere)],
      [String(derniere.annee), `${derniere.horizon}`, placements(derniere)],
    ],
    ["", "nombre", "texte"],
    "Où va un versement, au début et à la fin de la carrière",
    true,
  );

  const transmission = `
<p><strong>Ce qui se transmet, et ce qui ne se transmet pas.</strong> Tant que
le compte n'est pas liquidé, il est un capital, et un décès le fait passer aux
héritiers : l'encours de l'année, tel que le relevé le porterait ce jour-là. À
la veille du départ, il vaudrait ${g.euros(pilier.capital)}, le capital entier de
la ligne e) ; plus tôt dans la carrière, il vaudrait moins. Vu de
${pilier.annee_ouverture}, l'année où le pilier s'ouvre, la probabilité de mourir
avant d'avoir liquidé est de
${g.pourcentage(pilier.probabilite_deces_avant_liquidation)}, et l'espérance de
ce qui serait alors transmis de
${g.euros(pilier.esperance_capital_transmis)}. Après la liquidation, en revanche,
la rente est viagère : elle s'éteint avec le rentier, et rien n'est transmis.
C'est le prix de son montant, une rente qui se transmettrait étant plus
faible.</p>
<p>Le compte notionnel, lui, ne transmet rien à aucun moment : il n'est pas un
capital, il est un droit. C'est la différence de nature entre les deux lignes
du système 4, et elle ne se lit pas sur les montants.</p>`;

  // Une carrière qui s'arrête l'année même de la bascule n'a pas eu d'année
  // pour rapporter : parler de rendement n'aurait pas de sens, et le taux
  // affiché serait un artefact.
  const rendement = pilier.interets > 0 ? `
<p><strong>Ce que le pilier rapporte, frais compris :</strong>
${g.pourcentage(pilier.taux_rendement_annuel, false, 2)} par an. C'est le
taux qui, appliqué aux versements aux mêmes dates, donnerait le même capital.
Les frais coûtent ${g.euros(pilier.cout_des_frais)}, davantage que les
${g.euros(pilier.frais_preleves)} prélevés, parce que ce qui est prélevé ne
produit plus d'intérêts.</p>` : `
<p><strong>Ce pilier n'a pas eu d'année pour rapporter :</strong> le seul
versement tombe l'année du départ, et il est porté tel quel. Seuls les
${g.euros(pilier.frais_preleves)} de frais sur versement le grèvent.</p>`;

  // Ce que servent les cinq points volontaires, nommé à part : le pilier est
  // exactement proportionnel à son taux, si bien que la moitié volontaire rend
  // la moitié de la rente. Le lecteur doit pouvoir retrancher cette ligne, qui
  // est la seule de la page que personne ne lui impose.
  const partageVolontaire = avecVolontaire ? `
<p><strong>Sur cette rente, ${g.eurosCentimes(pilier.rente_volontaire)} par an
viennent des ${tauxVolontaire} que vous versez librement</strong>, et
${g.eurosCentimes(pilier.rente_obligatoire)} des ${tauxImpose} que la
proposition impose. Le compte ne les distingue nulle part ailleurs : même
assiette, même placement, mêmes frais, même table — la rente se partage donc
dans le rapport exact des deux taux. Si vous ne versez pas ces
${tauxVolontaire}, retranchez cette part du total du système 4, et gardez-la
sur votre fiche de paie : c'est le même argent, et c'est vous qui
choisissez.</p>` : "";

  return g.depliant(titre, `
<p>À compter de ${parametres.annee_debut_capitalisation}, ${taux} de la
rémunération sont prélevés <strong>en plus</strong> de la cotisation de
répartition, et placés. Ils ne passent pas par le compte notionnel : ils
constituent un capital, au nom du cotisant, dans un plan d'épargne retraite —
l'enveloppe qui existe déjà. Deux choses seulement l'en distinguent : ${tauxImpose}
sont obligatoires, et l'argent n'en sort qu'à la retraite, sous forme
de rente, ou au décès, par l'héritage.${g.bulle(
    "Pourquoi ce n'est pas la même chose qu'une pension",
    "Une pension de répartition est un droit sur les cotisations des actifs de "
    + "demain : elle ne dépend d'aucun marché, elle est revalorisée par une règle "
    + "collective, et elle ne se lègue pas. Une rente capitalisée sort d'un "
    + "capital réellement placé : elle dépend des taux du jour où l'argent a été "
    + "placé, elle supporte des frais, et le capital se transmet tant qu'il n'a "
    + "pas été converti en rente. Les deux sont additionnées sur la ligne du "
    + "système 4, jamais confondues.")}</p>
${cascade}
${partageVolontaire}
${rendement}
${echelle}
${transmission}
<p class="discret">Les taux employés sont ceux de la courbe des titres
souverains les mieux notés de la zone euro, relevée le
${echapper(dateEnClair(pilier.date_courbe))} et publiée par la Banque centrale
européenne ; les versements des années suivantes emploient les taux à terme
que cette même courbe implique. Les frais partent des moyennes 2025 du marché
des plans d'épargne retraite individuels, mesurées par l'Observatoire des
produits d'épargne financière, et baissent ensuite par paliers. La page <a href="${g.lien("/methode/")}">Méthode</a>
dit ce que ces choix supposent, et la page <a href="${g.lien("/donnees/")}">Données</a>
d'où ils viennent. Fiabilité de ce compartiment :
<span class="etiquette-fiabilite">${echapper(g.fiabiliteEnClair(nomFiabilite(pilier.fiabilite)))}</span>, le
barème de frais étant saisi, confronté au rapport à la main et non recontrôlé
automatiquement.</p>`);
}

/**
 * Ce que le système 4 change, et ce que l'impôt y paie.
 *
 * Deux choses, et le bloc les sépare. Le taux unique change ce que le compte
 * reçoit : il se lit dans le capital, contre celui du système 3. La garantie
 * vieillesse change ce qui est servi par-dessus : différentielle,
 * individualisée, financée par l'impôt — et c'est elle que le tableau détaille,
 * étape par étape, parce qu'elle est la seule ligne de toute la page qui ne
 * vienne pas d'une cotisation.
 */
function garantieVieillesse(comparaison, saisie) {
  const liberal = comparaison.notionnel_liberal;
  const garantie = liberal.garantie_vieillesse;
  if (garantie === null) return "";
  const parametres = comparaison.parametres;
  const annee = comparaison.carriere.anneeLiquidation;
  const bascule = parametres.annee_bascule;
  const capital4 = comparaison.notionnel_retroactif_employeur.capital_notionnel;
  const taux = g.pourcentage(parametres.taux_cotisation_liberal, false, 0);
  // Les années cotisées à 18 % : celles de la bascule au départ. Avant, le
  // compte est celui du système 3, et le capital ne s'en écarte pas.
  const annees18 = liberal.compte.cotisations
    .filter((c) => c.annee >= bascule && !c.nulle)
    .map((c) => c.annee);
  const tauxUnique = annees18.length
    ? `Ici, les années ${annees18[0]} à ${annees18[annees18.length - 1]} sont cotisées à `
      + `${taux} ; celles d'avant ${bascule} le sont aux taux réels, et le `
      + `capital vaut ${g.euros(liberal.capital_notionnel)} contre `
      + `${g.euros(capital4)} pour le système 3.`
    : `Ici, la carrière s'achève avant ${bascule} : aucune année n'est `
      + `cotisée à ${taux}, et le compte est exactement celui du `
      + `système 3, ${g.euros(liberal.capital_notionnel)}.`;
  const baseMensuelle = parametres.garantie_vieillesse_mensuelle;
  const isolementMensuel = parametres.allocation_isolement_mensuelle;
  const seul = garantie.situation === "seul";
  const situation = seul ? "une personne seule" : "une personne en couple";

  const lignes = [
    ["a) Garantie de base",
      `${g.euros(baseMensuelle)} par mois en euros de `
      + `${parametres.annee_euros_garantie_vieillesse}, soit `
      + `×${g.nombre(garantie.coefficient_prix, DECIMALES_FACTEUR)} en ${annee}`,
      `${g.eurosCentimes(garantie.base_annuelle)} par an`],
    ["b) + allocation d'isolement",
      `${g.euros(isolementMensuel)} par mois pour une personne seule, `
      + (seul ? "servie ici" : "rien à deux"),
      `${g.eurosCentimes(garantie.isolement_annuel)} par an`],
    ["c) = plancher",
      `ce qu'${situation} doit percevoir au minimum`,
      `${g.eurosCentimes(garantie.plancher_annuel)} par an`],
    ["d) Pension contributive",
      `le compte notionnel du système 4 — taux réels avant ${bascule}, `
      + `${taux} pour tous ensuite — divisé par `
      + `${g.nombre(liberal.conversion.diviseur, DECIMALES_DIVISEUR)}`,
      `${g.eurosCentimes(garantie.pension_contributive)} par an`],
    ["e) + rente du pilier capitalisé",
      `les ${g.pourcentage(tauxCapitalisationApplique(parametres), false, 0)} `
      + "capitalisés, volontaires compris : une allocation différentielle "
      + "compte les ressources et non leur origine",
      `${g.eurosCentimes(garantie.rente_capitalisee)} par an`],
    ["f) = ressources examinées", "d + e",
      `${g.eurosCentimes(garantie.ressources)} par an`],
  ];
  if (!garantie.age_atteint) {
    lignes.push([
      `f′) ressources en ${garantie.annee_ouverture}`,
      "la pension notionnelle est revalorisée sur la masse salariale, le "
      + "plancher sur les prix comme l'ASPA : l'écart entre les deux se réduit "
      + `de ${g.pourcentage(garantie.revalorisation_differee - 1.0)} d'ici l'ouverture`,
      `${g.eurosCentimes(garantie.ressources_a_l_ouverture)} par an`,
    ]);
  }
  const reference = garantie.age_atteint ? "f" : "f′";
  lignes.push(
    ["g) Garantie vieillesse",
      `max(0, c − ${reference}), financée par l'impôt, servie à partir de 65 ans`
      + (garantie.age_atteint
        ? "" : ` — soit ici à compter de ${garantie.annee_ouverture}`),
      `${g.eurosCentimes(garantie.complement)} par an`],
    ["h) = pension du système 4",
      garantie.age_atteint
        ? "d + g dès le départ"
        : `d seul jusqu'à 65 ans, puis d + g à partir de ${garantie.annee_ouverture}`,
      `${g.eurosCentimes(liberal.pension_annuelle)} par an`],
  );

  let lecture;
  if (garantie.servie_a_la_liquidation) {
    lecture = "<p>Ici, la pension obligatoire de "
      + `${g.eurosCentimes(garantie.ressources / 12)} par mois `
      + `reste sous le plancher de ${g.eurosCentimes(garantie.plancher_annuel / 12)} : `
      + `l'impôt en finance <strong>${g.eurosCentimes(garantie.complement / 12)} `
      + `par mois</strong>, soit ${g.pourcentage(garantie.complement / liberal.pension_annuelle)} `
      + "de ce que le système 4 verse.</p>";
  } else if (garantie.differee) {
    lecture = "<p>Ici, la liquidation a lieu à "
      + `${age(comparaison.carriere.age_liquidation || 0.0)}, avant les 65 ans `
      + `de l'allocation : rien n'est servi jusqu'en ${garantie.annee_ouverture}. `
      + "À partir de là, la pension obligatoire — "
      + `${g.eurosCentimes(garantie.ressources / 12)} par mois au départ, `
      + `${g.eurosCentimes(garantie.ressources_a_l_ouverture / 12)} à l'ouverture, `
      + "parce qu'elle suit la masse salariale quand le plancher suit les prix — "
      + `reste sous le plancher de ${g.eurosCentimes(garantie.plancher_annuel / 12)} : `
      + `l'impôt en finance <strong>${g.eurosCentimes(garantie.complement / 12)} par `
      + "mois</strong>. Le montant affiché plus haut est celui du départ, sans "
      + "la garantie.</p>";
  } else {
    lecture = "<p>Ici, la pension obligatoire de "
      + `${g.eurosCentimes(garantie.ressources / 12)} par mois `
      + `dépasse le plancher de ${g.eurosCentimes(garantie.plancher_annuel / 12)} : `
      + "la garantie ne sert rien, et le système 4 est un compte notionnel "
      + "à taux unique, sans plus.</p>";
  }

  // Le tableau de la proposition, recalculé avec la règle du scénario — en
  // euros mensuels de l'année où la proposition fixe ses montants, sans l'âge :
  // il illustre le mécanisme, pas cette carrière.
  const plancherSeul = baseMensuelle + isolementMensuel;
  const exemples = EXEMPLES_GARANTIE.map(([pensions, libelle]) => {
    const plancher = pensions.length === 1 ? plancherSeul : baseMensuelle;
    const aides = pensions.map((pension) => Math.max(0.0, plancher - pension));
    const detail = aides.length > 1 ? aides.map((aide) => g.euros(aide)).join(" + ") : "";
    return [
      libelle,
      g.euros(aides.reduce((somme, aide) => somme + aide, 0)),
      detail ? detail : "—",
    ];
  });

  return g.depliant(
    "Le système 4 : un taux pour tous, et une garantie payée par l'impôt",
    `
<p>La garantie vieillesse, étape par étape, en euros de ${annee} — l'année du
départ.${g.bulle(
    "Ce que le système 4 change au système 3",
    "Il est le système 3 — même compte rétroactif, cotisation salariale et "
    + "patronale confondues, mêmes âges, même indexation, même liquidation — à "
    + `deux différences près. La première : à compter de ${bascule}, un taux `
    + `unique de ${taux}, parts salariale et patronale additionnées, le même `
    + "pour tous les statuts, prélevé une fois sur la rémunération. Ce qui a "
    + `été cotisé avant ${bascule} reste porté au compte tel qu'il a été `
    + "prélevé, aux taux réels de chaque régime : sur ces années-là, le 6 est "
    + `le 4. ${tauxUnique} La seconde : une garantie vieillesse qui remplace `
    + "l'ASPA.",
  )}</p>
${g.tableau(
    ["Étape", "Ce qu'elle fait", "Résultat"],
    lignes,
    ["", "texte", "nombre"],
    `La garantie vieillesse du système 4, étape par étape, en euros de ${annee}`,
    true,
  )}
${lecture}
<p>Ce que la garantie sert à un foyer, en euros de
${parametres.annee_euros_garantie_vieillesse} et par mois.${g.bulle(
    "Ce qui la sépare de l'ASPA",
    "Un mot : elle est <strong>individualisée</strong>. L'ASPA regarde les "
    + "ressources du foyer, et son plafond de couple n'est pas le double de "
    + "celui d'une personne seule ; la garantie compare chacun à son propre "
    + `plancher — ${g.euros(baseMensuelle)} par mois, plus `
    + `${g.euros(isolementMensuel)} d'allocation d'isolement pour qui vit seul `
    + "— sans jamais regarder la pension du conjoint.",
  )}</p>
${g.tableau(
    ["Pensions des deux personnes", "Aide totale du foyer", "Détail"],
    exemples,
    ["", "nombre", ""],
    "Ce que la garantie individualisée sert à un foyer, selon les deux pensions",
    true,
  )}
<p class="discret">Garantie calculée ici pour ${situation}.${g.bulle(
    "Comment la garantie est financée",
    "Par l'<strong>impôt</strong>, non par les cotisations : la page Coût la "
    + "sort du compte des cotisants et la compte à part. Elle garde de l'ASPA "
    + "son âge — 65 ans — et sa place, une ligne servie en dernier, après la "
    + "pension contributive. L'option « situation de foyer » du formulaire ne "
    + "change qu'une chose : l'allocation d'isolement.",
  )}</p>`,
  );
}


function decomposition(contexte, saisie, comparaison) {
  // Le défaut est lu sur DEFAUTS, non écrit en dur : ailleurs, l'utilisateur a
  // choisi lui-même sa ligne de comparaison.
  if (saisie.indexation !== DEFAUTS.indexation) {
    return "";
  }

  const loterie = loterieDeCohorte(contexte);
  const lignes = [];
  for (const [code, libelle] of INDEXATIONS) {
    let variante;
    try {
      variante = code === saisie.indexation
        ? comparaison
        : contexte.simuler(new Saisie({ ...saisie, indexation: code }));
    } catch (erreur) {
      if (fauteDeProgramme(erreur)) throw erreur;
      continue;
    }
    const mensuel = variante.enEurosConstants(
      variante.notionnel_retroactif.pension_annuelle,
    ) / 12;
    lignes.push([
      echapper(libelle),
      `×${g.nombre(variante.notionnel_retroactif.compte.rendement_cumule, 2)}`,
      g.eurosCentimes(mensuel),
      g.pourcentage(variante.variation("notionnel_retroactif"), true),
    ]);
  }

  return g.depliant("D'où vient l'écart", `
<p>La même carrière, le même calcul notionnel rétroactif, sous neuf règles de
revalorisation. La colonne « rendement » est le facteur par lequel les
cotisations ont été multipliées entre leur versement et la liquidation.${g.bulle(
    "Ce que chaque règle de revalorisation vaut",
    "La <strong>première ligne est celle que la simulation applique</strong> : "
    + "la croissance de la masse salariale, c'est-à-dire le rendement qu'un "
    + "système en répartition peut servir sans changer son taux de cotisation. "
    + "C'est la seule règle du tableau qui repose sur un argument théorique et "
    + "non sur un choix, et la plus généreuse — elle vaut salaire moyen + "
    + "emploi salarié, et l'emploi salarié a doublé depuis 1950. Son "
    + "incohérence, à garder en tête : elle crédite le compte du rendement que "
    + "le système ENTIER dégage, quand le système 2 n'y verse que la "
    + "part salariale ; c'est au système 3 qu'elle se compare sans "
    + "biais. La deuxième ligne n'est pas une hypothèse mais un relevé — le "
    + "coefficient que les arrêtés ont réellement appliqué, celui dont le "
    + "système 1 se sert : l'écart entre elle et le système actuel mesure "
    + "l'effet propre des comptes notionnels, et tout ce qui sépare les autres "
    + "lignes de celle-là mesure l'effet de la règle. Le triple lock inversé "
    + "compare deux taux nominaux à un taux réel : dès que l'inflation dépasse "
    + "la productivité — presque toute la période 1945-1985 — c'est la "
    + "productivité qui l'emporte, et la valeur réelle des comptes s'effondre.",
  )}</p>
${g.tableau(
    ["Règle d'indexation", "Rendement cumulé",
      `Pension mensuelle, en euros de ${saisie.euros}`,
      "Écart au système actuel"],
    lignes,
    ["", "nombre", "nombre", "nombre"],
    "Ce que la même carrière donne sous chaque règle d'indexation",
    true,
  )}
<p class="discret">Le <strong>lissage</strong>, dans les options, s'applique à
toutes ces lignes à la fois.${g.bulle(
    "Ce que le lissage vise",
    "Il applique une moyenne glissante au taux que la règle produit, quelle "
    + "qu'elle soit. Ce qu'il vise n'est pas le niveau mais la loterie de "
    + "cohorte : sur le PIB nominal brut, une cotisation de "
    + `${ANNEE_COTISATION_LOTERIE} vaut ${loterie.get("1|2019")} à une `
    + `liquidation de 2019 et ${loterie.get("1|2020")} en 2020 — attendre un an `
    + "fait perdre, parce que l'année traversée s'est mal passée. Lissée sur "
    + `cinq ans, la même cotisation vaut ${loterie.get("5|2019")} puis `
    + `${loterie.get("5|2020")}, et le recul disparaît. « PIB nominal » lissé `
    + "sur cinq ans, c'est la règle italienne ; le modèle en reprend le taux, "
    + "pas le reste du système italien.",
  )}</p>
`);
}

function detail(contexte, comparaison) {
  const retro = comparaison.notionnel_retroactif;
  const catalogue = contexte.simulateur().catalogue;
  const pensions = comparaison.actuel.pensions_par_regime;

  const nomRegime = (code) => (catalogue.contient(code) ? catalogue.obtenir(code).nom : code);

  const actuel = comparaison.actuel;
  // Tout ce tableau est en euros de l'année de liquidation : c'est la seule
  // unité dans laquelle la chaîne de calcul s'additionne. Les six blocs du
  // haut, eux, mettent en avant les euros de l'année de référence. Sans dire
  // laquelle est laquelle, la dernière ligne prétendait valoir « le montant de
  // la ligne 1 ci-dessus » en désignant un nombre que la ligne 1 n'affichait
  // pas.
  const annee = comparaison.carriere.anneeLiquidation;
  const anneeReference = comparaison.parametres.annee_euros_constants;
  const renvoi = annee !== anneeReference
    ? "Ce n'est pas l'unité des quatre montants affichés plus haut, qui les "
      + `ramène au pouvoir d'achat de ${anneeReference}.`
    : "Le départ tombant sur l'année de référence, c'est aussi l'unité des "
      + "quatre montants affichés plus haut.";
  // Les régimes PROVISIONNÉS sont sortis du tableau principal : leur rente ne
  // fait pas partie du total, et une ligne posée au-dessus d'un total qui
  // l'ignore fait un tableau qui ne s'additionne pas — 33 176,69 + 667,12
  // valait 33 176,69 à l'écran, sous une phrase affirmant le contraire. Elle est
  // reportée sous le total, où son exclusion se lit.
  const ligne = (pension) => [
    echapper(nomRegime(pension.regime)),
    g.eurosCentimes(pension.montant),
    g.franciser(echapper(pension.detail)),
  ];
  const repartis = pensions.filter((p) => !catalogue.obtenir(p.regime).hors_repartition);
  const provisionnes = pensions.filter((p) => catalogue.obtenir(p.regime).hors_repartition);
  const lignesActuel = repartis.map(ligne);
  if (lignesActuel.length > 0 && actuel.avantages_appliques.length > 0) {
    lignesActuel.push([
      "<strong>Sous-total contributif</strong>",
      `<strong>${g.eurosCentimes(actuel.total_contributif)}</strong>`,
      '<span class="discret">ce que la carrière a ouvert par ses seules '
      + "cotisations</span>",
    ]);
  }
  for (const avantage of actuel.avantages_appliques) {
    lignesActuel.push([
      `+ ${echapper(avantage.libelle)}`,
      g.eurosCentimes(avantage.montant),
      `<span class="discret">${echapper(avantage.detail)}</span>`,
    ]);
  }
  if (lignesActuel.length > 0) {
    lignesActuel.push([
      "<strong>Pension du système actuel</strong>",
      `<strong>${g.eurosCentimes(actuel.pension_annuelle)}</strong>`,
      '<span class="discret">c\'est le système 1 ci-dessus, pris dans les '
      + "euros de son année de départ</span>",
    ]);
  }
  for (const pension of provisionnes) {
    const [libelle, montant, detail] = ligne(pension);
    lignesActuel.push([
      `hors total — ${libelle}`, montant,
      '<span class="discret">régime PROVISIONNÉ, servi à part et retiré des '
      + "quatre systèmes</span> · " + detail,
    ]);
  }

  const regimes = lignesActuel.length > 0
    ? g.tableau(
      ["Régime, puis avantage", `Pension annuelle, en euros de ${annee}`,
        "Calcul"],
      lignesActuel,
      ["", "nombre", "texte"],
      "Pension du système actuel, régime par régime",
      true,
    )
    : "<p>Aucun droit liquidé dans le système actuel.</p>";

  let part = "";
  if (actuel.avantages_appliques.length > 0 && actuel.pension_annuelle > 0) {
    const gratuit = actuel.avantages_appliques
      .reduce((somme, a) => somme + a.montant, 0.0);
    part = `<p>Les avantages non contributifs pèsent ${g.eurosCentimes(gratuit)} par an, `
      + `soit ${g.pourcentage(gratuit / actuel.pension_annuelle)} de la `
      + "pension. C'est exactement ce que les deux scénarios notionnels "
      + "retirent : ils ne conservent que le sous-total contributif, et le "
      + "recalculent sur les cotisations réellement versées.</p>";
  }

  const compte = g.tableau(
    ["Poste", "Montant"],
    [
      ["Cotisations effectivement versées, sommées aux euros de chaque année",
        g.euros(retro.compte.cotisations_versees)],
      ["Rendement cumulé appliqué à ces cotisations",
        `×${g.nombre(retro.compte.rendement_cumule, DECIMALES_FACTEUR)}`],
      [`Capital notionnel à la liquidation, en euros de ${annee}`,
        g.euros(retro.capital_notionnel)],
      ["Divisé par le coefficient de conversion",
        `${g.nombre(retro.conversion.diviseur, DECIMALES_DIVISEUR)} `
        + `(${echapper(retro.conversion.table)})`],
      [`Pension annuelle, en euros de ${annee}`,
        g.eurosCentimes(retro.pension_annuelle)],
    ],
    ["", "nombre"],
    "Construction du compte notionnel rétroactif, poste par poste",
    true,
  );

  return g.depliant("Le détail du calcul", `
<p>Tous les montants de cette section sont en <strong>euros de ${annee}</strong>,
l'année du départ.${g.bulle(
    "L'unité de cette section",
    `${renvoi} C'est la seule unité dans laquelle une chaîne de `
    + "calcul s'additionne : convertir chaque ligne au pouvoir d'achat d'une "
    + "autre année ferait des totaux faux.",
  )}</p>
<h4>Système 1 — de quoi votre pension actuelle est faite${g.bulle(
    "Comment lire ce tableau",
    "Chaque régime d'abord, puis les avantages que le droit en vigueur ajoute "
    + "par-dessus ; le total est la pension du système 1. Un minimum est déjà "
    + "compris dans la ligne du régime qui le sert : le sous-total contributif "
    + "l'en retire, et la ligne suivante le rend visible — c'est la même "
    + "somme, comptée une fois.",
  )}</h4>
${regimes}
${part}
<h4>Système 2 — construction du compte notionnel rétroactif</h4>
${compte}
<details>
  ${g.sommaire("Les résultats complets en JSON")}
  <pre class="json">${echapper(JSON.stringify(comparaison.dictionnaire(), null, 2))}</pre>
</details>
<p class="discret">L'adresse de cette page contient tous les paramètres :
elle peut être citée ou partagée telle quelle.</p>
`);
}
/**
 * Les trois grilles de la page Cas types, dans l'ordre d'affichage : le code du
 * scénario, le titre de sa section, le titre accessible de sa grille, et la
 * phrase qui dit ce qu'on y voit. Le premier est CELUI QUI S'AFFICHE — la seule
 * réforme applicable qui crédite ce qui est réellement prélevé —, les cinq
 * autres sont repliés ensemble.
 */
/**
 * Les cinq grilles de la page Cas types, dans l'ordre des onglets : le code du
 * scénario, le libellé de son onglet, le titre de sa section, le titre
 * accessible de sa grille, et la phrase qui dit ce qu'on y voit. Le premier
 * est celui qui s'affiche à l'ouverture — le système 4, la proposition.
 */
const GRILLES_CAS_TYPES = [
  [
    "notionnel_liberal",
    "4. La proposition",
    "La proposition du Parti libéral français, par rapport à aujourd'hui",
    "La proposition libérale : taux unique de 18 % et garantie vieillesse",
    "Le même compte rétroactif que le système 3 jusqu'à la bascule, puis "
    + "un taux unique de 18 % — salariale et patronale confondues —, une "
    + "cotisation de 5 % capitalisée par-dessus, et une garantie vieillesse "
    + "individualisée financée par l'impôt. Les lignes qui cotisaient au-delà "
    + "de 18 % descendent sous le système 3, celles qui cotisaient en deçà "
    + "remontent. L'écart affiché comprend la rente du pilier capitalisé : "
    + "elle ne joue que pour qui cotise après la bascule, et d'autant plus "
    + "qu'il lui reste d'années à courir — la page Simuler en donne le "
    + "partage, carrière par carrière. La garantie, elle, ne se voit que sur "
    + "les cas dont la pension reste sous le plancher, à partir de 65 ans.",
  ],
  [
    "notionnel_retroactif",
    "2. Part salariale seule",
    "Le compte notionnel sur la seule part salariale, par rapport à "
    + "aujourd'hui",
    "Compte notionnel, part salariale seule, carrière recalculée depuis 1941",
    "Les générations anciennes sont les plus touchées : leurs cotisations, "
    + "versées quand l'inflation dépassait la productivité, ont été "
    + "revalorisées à un taux très inférieur à la hausse des prix.",
  ],
  [
    "notionnel_retroactif_employeur",
    "3. Les deux parts",
    "Le compte notionnel sur les deux parts, par rapport à aujourd'hui",
    "Compte notionnel, part salariale et patronale, carrière recalculée "
    + "depuis 1941",
    "Toutes les lignes bougent, sauf celles des non-salariés — artisan, "
    + "exploitant agricole, profession libérale — qui n'ont pas d'employeur "
    + "et pour qui ce système est le système 2. Les lignes publiques "
    + "bougent le plus : la contribution de leur employeur est un taux "
    + "d'équilibre, sans commune mesure avec la part patronale d'un salarié.",
  ],
];

/**
 * Treize carrières types croisées avec sept générations.
 *
 * LA PAGE NE MONTRE QU'UNE GRILLE À LA FOIS, ET C'EST LA PROPOSITION : les
 * cinq grilles sont derrière des onglets — des boutons radio, dont le panneau
 * suit en CSS —, et l'onglet ouvert est le système 4. Voir `_cas_types` dans
 * `web/pages.py`.
 *
 * CE QU'ELLE DIT EST UN ÉCART ENTRE LIGNES, JAMAIS UN NIVEAU. Le modèle calcule
 * ce que chaque carrière acquiert ; il n'applique pas le coefficient
 * d'équilibre, qui déplacerait toute la grille en bloc. C'est écrit en tête, et
 * non en note de bas de page.
 */
/**
 * « proposition » sur le système 4, « contrefactuel » sur les autres, rien
 * sur le système actuel : le badge redit là où l'erreur de lecture se produit
 * ce que le préambule a dit.
 */
function badgeScenario(scenario) {
  if (scenario === "actuel") {
    return "";
  }
  if (scenario === "notionnel_liberal") {
    return '<span class="badge proposition">proposition</span>';
  }
  return '<span class="badge contrefactuel">contrefactuel</span>';
}

/** Le libellé d'un scénario en tête de ligne, avec son badge. */
function nomScenario(scenario, libelle) {
  const badge = badgeScenario(scenario);
  return echapper(libelle) + (badge ? ` ${badge}` : "");
}

function casTypes(contexte) {
  const simulateur = contexte.simulateur();
  const resultat = calculerCasTypes(simulateur);
  const montre = GRILLES_CAS_TYPES[0][0];
  // Le solde du système actuel, observé puis projeté par le COR : il est dans
  // les comptes, et ne coûte rien — à la différence du coût agrégé.
  const comptes = contexte.comptes();
  const obs = comptes.derniereAnneeObservee;
  const horizon = comptes.derniereAnnee;

  const grille = (scenario, intitule) => {
    const lignes = CAS_TYPES.map((cas) => {
      // Le libellé seul : ce qu'il recouvre est dit une fois pour toutes sous
      // la grille, et non dans une infobulle de survol.
      const cellules = [echapper(cas.libelle)];
      for (const generation of GENERATIONS) {
        const comparaison = resultat.resultats.get(`${cas.code}|${generation}`);
        if (comparaison === undefined) {
          cellules.push("—");
          continue;
        }
        // L'écart porte sur ce que le système SERT, pilier capitalisé
        // compris. Il ne joue que sur le système 4 — les autres n'en ont pas.
        const variation = comparaison.variationTotale(scenario);
        cellules.push(new g.Cellule(
          g.pourcentage(variation, true, 0), variation,
        ));
      }
      return cellules;
    });
    return g.tableau(
      ["Cas type"].concat(GENERATIONS.map(String)),
      lignes,
      [""].concat(GENERATIONS.map(() => "nombre")),
      `${intitule} : écart de pension au système actuel, par cas `
      + "type et par génération",
      true,
    );
  };

  // Les trois chiffres d'ouverture : l'ÉCART entre les carrières, qui est ce
  // que la grille mesure, et non son niveau, qu'elle ne mesure pas. Ils sont
  // lus sur la dernière génération, et sur la grille qui s'affiche à
  // l'ouverture.
  const derniere = GENERATIONS[GENERATIONS.length - 1];
  const ecarts = [];
  for (const cas of CAS_TYPES) {
    const comparaison = resultat.resultats.get(`${cas.code}|${derniere}`);
    if (comparaison !== undefined) {
      ecarts.push([comparaison.variationTotale(montre), cas.libelle]);
    }
  }
  ecarts.sort((a, b) => (a[0] - b[0]) || (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0));
  let reperes = "";
  if (ecarts.length) {
    const bas = ecarts[0];
    const haut = ecarts[ecarts.length - 1];
    reperes = g.fiche(
      "La carrière la mieux traitée", echapper(haut[1].split(" (")[0]),
      `${g.pourcentage(haut[0], true, 0)} par rapport à aujourd'hui, `
      + `génération ${derniere}, système 4`,
    ) + g.fiche(
      "La moins bien traitée", echapper(bas[1].split(" (")[0]),
      `${g.pourcentage(bas[0], true, 0)} par rapport à aujourd'hui, `
      + `génération ${derniere}, système 4`,
    ) + g.fiche(
      "Ce qui les sépare",
      `${g.nombre((haut[0] - bas[0]) * 100, 0)} points`,
      "à carrière et à durée identiques",
    );
  }

  // Les onglets, puis les panneaux : deux frères, pour que la feuille de
  // style lise l'onglet coché et montre le panneau qui lui répond.
  const onglets = GRILLES_CAS_TYPES.map(([scenario, onglet], rang) => (
    `<input type="radio" name="grille" id="grille-${scenario}"`
    + (rang === 0 ? " checked" : "")
    + `><label for="grille-${scenario}">${echapper(onglet)}</label>`
  )).join("");
  const panneaux = GRILLES_CAS_TYPES.map(([scenario, , titre, alt, lecture], rang) => (
    `<div class="panneau" data-onglet="${scenario}"`
    + (rang === 0 ? "" : " hidden") + ">"
    + `<h3>${echapper(titre)} ${badgeScenario(scenario)}</h3>${grille(scenario, alt)}`
    + `<p class="discret">${echapper(lecture)}</p></div>`
  )).join("");

  const ages = g.tableau(
    ["Cas type"].concat(GENERATIONS.map(String)),
    CAS_TYPES.map((cas) => [echapper(cas.libelle)].concat(
      GENERATIONS.map((generation) => age(
        ageLiquidationPour(cas, simulateur, generation),
      )),
    )),
    [""].concat(GENERATIONS.map(() => "nombre")),
    "Âge de liquidation de chaque cas type, par génération",
    true,
  );

  let echecs = "";
  if (resultat.echecs.size) {
    const elements = [...resultat.echecs.entries()]
      .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
      .map(([cle, motif]) => {
        const [code, generation] = cle.split("|");
        return `<li>${echapper(code)} / ${generation} : ${echapper(motif)}</li>`;
      }).join("");
    echecs = g.depliant(
      "Combinaisons que le modèle a refusé de calculer",
      `<ul class='serree'>${elements}</ul>`,
    );
  }

  const depliantCas = g.depliant(
    "Qui sont ces treize carrières",
    g.gloses(CAS_TYPES.map((cas) => [cas.libelle, cas.commentaire])),
  );
  const depliantAges = g.depliant(
    "À quel âge chacun part, et pourquoi ce n'est pas le même",
    '<p class="discret">Un cas type ne porte pas un âge de départ mais une '
    + "RÈGLE, et chaque génération liquide donc au sien. La plupart partent "
    + "au taux plein, le premier âge auquel la pension est servie entière, "
    + "qui dépend à la fois de l'âge légal et de la durée requise de la "
    + "génération. Ceux dont un statut commande le départ (catégorie active, agent de conduite, agent des IEG) partent à l'âge que ce statut leur "
    + "ouvre. Le militaire, lui, part à une DURÉE de services, pas à un âge.</p>" + ages,
  );

  const tete = g.affiche(
    "Cas types",
    'Treize carrières, <span class="cle-texte">sept générations.</span>',
    "Chaque case dit ce que la pension deviendrait, par rapport à "
    + "aujourd'hui, pour la même carrière. <strong>Rouge : moins "
    + "qu'aujourd'hui. Vert : plus.</strong>",
  );

  return `
${tete}

<div class="note"><strong>Ces pourcentages ne sont pas des baisses de
pension.</strong> Chaque case compare deux carrières calculées sous la même
règle, et ce que la grille mesure est l'écart entre ses lignes : ce qu'un
militaire touche de plus ou de moins qu'un artisan, à cotisation égale. Le
niveau général, lui, dépend d'un
${g.terme("réglage annuel", "coefficient d'équilibre")} que le modèle calcule
mais n'applique jamais : il multiplierait toutes les cases par le même facteur.
Pour la proposition, ce facteur est supérieur à un chaque année : à
prélèvement égal, le système aurait de quoi servir davantage que ces cases
n'affichent. <strong>Un coefficient supérieur à un est une marge</strong>,
de quoi relever toutes les cases d'autant.
<a href="${g.lien("/cout")}" data-vers="cout-equilibre">La page Coût le chiffre</a>.</div>

<div class="fiches reperes">${reperes}</div>

<p class="discret">Le <strong>système 4</strong> est
<a href="${g.lien("/")}">la proposition</a> ; les systèmes 2 et 3 sont des
contrefactuels, qui mesurent ce que chaque ingrédient déplace : la part
patronale, puis le taux unique. Le modèle calcule deux variantes de plus —
celles où les droits acquis sont conservés à la bascule —, que le site ne
compare pas.</p>
<fieldset class="onglets"><legend>Système affiché</legend>${onglets}</fieldset>
<div class="panneaux">${panneaux}</div>
<p class="discret">« Aujourd'hui » n'est pas un point fixe. Le système actuel,
colonne de référence de ces grilles, manque déjà de
${g.pourcentage(-comptes.solde(obs), false, 2)} du PIB en ${obs}, et le
Conseil d'orientation des retraites projette qu'il en manquera
${g.pourcentage(-comptes.solde(horizon), false, 2)} en ${horizon}. Le choix
réel se joue entre le notionnel et un système
qui dérive ; le système stable, lui, n'existe pas.</p>

<p class="actions"><a class="bouton" href="${g.lien("/simuler")}">Calculer sur ma
carrière</a><a href="${g.lien("/methode")}">Comment c'est calculé</a></p>

<h2>Pour aller plus loin</h2>

${depliantCas}
${depliantAges}
${echecs}
`;
}

// Bandes du graphique par système : les six plus lourdes gardent leur couleur,
// le reste de la répartition est réuni, et ce qui n'en relève pas forme la
// dernière bande. Huit bandes se lisent ; treize ne se lisent plus.
const BANDES_COUT = [
  ["regime_general", "var(--serie-1)"],
  ["agirc_arrco", "var(--serie-2)"],
  ["fonction_publique_etat", "var(--serie-3)"],
  ["regimes_speciaux", "var(--serie-4)"],
  ["exploitants_agricoles", "var(--serie-5)"],
  ["professions_liberales", "var(--serie-6)"],
];

// Couleur de chacun des quatre systèmes — les mêmes que sur la page de
// résultats, pour qu'un lecteur qui passe de l'une à l'autre les reconnaisse.
const COULEURS_SCENARIOS = {
  actuel: "var(--actuel)",
  notionnel_retroactif: "var(--retroactif)",
  notionnel_retroactif_employeur: "var(--retroactif-employeur)",
  notionnel_liberal: "var(--liberal)",
};

/** Un montant en millions d'euros, écrit en milliards. */
function milliards(millions, decimales = 0) {
  return `${g.nombre(millions / 1000, decimales)} Md €`;
}
/**
 * Ce que la retraite coûte, d'où vient l'argent, et ce qui manque.
 *
 * CETTE PAGE S'ADRESSE À QUELQU'UN QUI N'A PAS FAIT D'ÉCONOMIE ET QUI N'A PAS LE
 * TEMPS. C'est une contrainte de construction, pas un vœu, et elle décide de
 * tout ce qui suit :
 *
 *  * **Une question par carte, une réponse par carte**, en deux phrases courtes,
 *    avant le tracé. La carte se télécharge en image, signée, pour être postée.
 *  * **Deux graphiques, et pas un de plus.** Les trois qui traçaient une part du
 *    PIB dans le temps — l'histoire depuis 1959, le bilan jusqu'en 2070, l'effet
 *    de la réforme — n'en font plus qu'un : ils répondaient à la même question
 *    sur trois fenêtres.
 *  * **Tout le reste est replié.** Rien n'est retiré — une page qui ne peut pas
 *    se justifier n'est pas honnête —, mais rien n'oblige à le traverser.
 *  * **Les phrases sont courtes**, et les mots de spécialiste portent leur
 *    définition, ouvrable sur place.
 *
 * LE PÉRIMÈTRE DU GRAPHIQUE DE TÊTE EST CELUI DU COR : c'est le seul jeu de
 * comptes où les dépenses ET les ressources du même ensemble de régimes soient
 * publiées sous la même convention. Le modèle n'y intervient que par un RAPPORT
 * sans dimension, jamais par un niveau.
 *
 * LA COURBE D'AVANT 2002 VIENT D'AILLEURS, et c'est pourquoi elle s'arrête là où
 * celle du COR commence : un demi-point de PIB les sépare, celui de la
 * dépendance et de l'épargne retraite. Le décrochement se voit, et c'est bien
 * ainsi — le masquer collerait deux séries qui ne mesurent pas la même chose.
 */
function cout(contexte) {
  const comptes = contexte.comptes();
  const c = contexte.cout();
  const solde = c.solde;
  const depenses = contexte.depenses();
  const bascule = contexte.base.annee_bascule;

  const obs = solde.derniereAnneeObservee;
  const observe = solde.annee(obs);
  const horizon = solde.annee(solde.derniereAnnee);
  const effectifs = contexte.simulateur().effectifs;
  // La dernière année que la DREES publie, et non celle du compte : le nombre
  // de retraités n'a pas la même fenêtre que les comptes du COR, et inventer un
  // effectif pour l'année manquante ne vaudrait rien.
  const anneeEffectifs = effectifs.serie("tous_regimes").derniereAnnee;
  const retraites = effectifs.effectif("tous_regimes", anneeEffectifs);

  // -- les trois chiffres d'ouverture --------------------------------------
  //
  // Ce qu'on emporte si on ne lit rien d'autre. En EUROS et non en part de
  // PIB : une part de PIB ne parle qu'à qui sait déjà ce qu'est le PIB, et
  // c'est précisément le lecteur que cette page ne suppose pas.
  const manque = -observe.soldeMeur("actuel");
  const partManquante = -observe.solde("actuel") / observe.depense("actuel");
  const reperes = g.fiche(
    `Versé aux retraités en ${obs}`,
    milliards(observe.depenseMeur("actuel"), 0),
    `à ${g.nombre(retraites / 1e6, 1)} millions de personnes`,
  ) + g.fiche(
    "Encaissé pour le payer",
    milliards(observe.ressourcesMeur(), 0),
    "cotisations et impôts",
  ) + g.fiche(
    manque > 0 ? "Manquant" : "Reste",
    milliards(Math.abs(manque), 1),
    `${g.pourcentage(Math.abs(partManquante), false, 1)} de la facture`,
  );

  // -- le graphique de tête : cent onze ans en un seul cadre ----------------
  //
  // Il en remplace trois. Les fenêtres se recouvraient — 1959-2024 pour
  // l'histoire, 2002-2070 pour le bilan, 2025-2070 pour la réforme — et la même
  // grandeur y était tracée trois fois, à trois échelles différentes. Les séries
  // ne se recouvrent pas, elles : chacune vaut `null` hors de la plage que sa
  // source publie, et la courbe s'y interrompt plutôt que de prolonger une
  // mesure que personne n'a faite.
  const anneesToutes = [];
  for (let a = c.premiereAnnee; a <= solde.derniereAnnee; a += 1) {
    anneesToutes.push(a);
  }
  const rang = new Map(anneesToutes.map((annee, position) => [annee, position]));

  const serie = (libelle, couleur, valeurs, tirets = false, glose = "") => {
    const colonne = anneesToutes.map(() => null);
    for (const [annee, valeur] of valeurs) { colonne[rang.get(annee)] = valeur; }
    return new g.Serie(libelle, colonne, couleur, tirets, glose);
  };

  // Avant 2002, le COR n'a rien : c'est la DREES qui porte l'histoire, sur un
  // périmètre un peu plus large. La courbe s'arrête à 2001, là où l'autre
  // commence, et le décrochement entre les deux se voit — il vaut le demi-point
  // que les deux comptes ne comptent pas pareil.
  const avant = [];
  for (let a = c.premiereAnnee; a < solde.premiereAnnee; a += 1) {
    avant.push([a, depenses.partPib(a) * 100]);
  }
  const sortie = solde.annees.map((ligne) => [ligne.annee, ligne.depense("actuel") * 100]);
  const entree = solde.annees.map((ligne) => [ligne.annee, ligne.ressources * 100]);
  // La troisième courbe est LA PROPOSITION, et non plus une variante que le
  // site ne compare plus. Elle ne commence qu'à la bascule — non parce qu'elle
  // ne changerait rien avant, elle est rétroactive et change tout, mais parce
  // que c'est de là que la décision se prend. Pas à l'année observée non
  // plus : l'année d'avant la bascule, la proposition n'est pas encore
  // appliquée, son point est celui du système actuel, et la courbe faisait un
  // à-pic qui ne mesurait rien.
  const reforme = "notionnel_liberal";
  const departReforme = Math.max(obs, bascule);
  const apres = solde.annees.filter((ligne) => ligne.annee >= departReforme)
    .map((ligne) => [ligne.annee, ligne.depense(reforme) * 100]);
  // Et ce qu'elle encaisserait : 18 % sur les revenus d'activité, sans la
  // contribution d'équilibre de l'État ni ce que la CNAF et l'Unédic versent
  // pour des droits qu'elle ne sert plus. Deux courbes pour la proposition
  // comme pour le système actuel, sinon on ne voit qu'une moitié de son
  // compte : ce qu'elle coûte, jamais ce qu'elle rapporte.
  const encaisse = solde.annees.filter((ligne) => ligne.annee >= departReforme)
    .map((ligne) => [ligne.annee, ligne.ressourcesDe(reforme) * 100]);
  const tauxLiberal = contexte.simulateur().parametres.taux_cotisation_liberal;

  // L'ordre est celui de la lecture, de gauche à droite : la légende se
  // parcourt alors dans l'ordre où l'œil rencontre les courbes.
  const courbes = [
    serie(`Avant ${solde.premiereAnnee}`, "var(--serie-1)", avant, false,
      "autre source, périmètre un peu plus large"),
    serie("Ce qui sort : les pensions versées", "var(--serie-2)", sortie),
    serie("Ce qui rentre : cotisations et impôts", "var(--serie-5)", entree),
    serie(`Ce que coûterait notre proposition, dès ${bascule}`,
      "var(--liberal)", apres, true),
    serie("Ce qu'elle encaisserait", "var(--liberal)", encaisse, false,
      `${g.pourcentage(tauxLiberal, false, 0)} sur les `
      + "revenus d'activité, sans la contribution de l'État"),
  ];
  const bilan = g.graphique(
    "Ce que la retraite verse et ce qu'elle encaisse, de "
    + `${c.premiereAnnee} à ${solde.derniereAnnee}, en part du PIB`,
    anneesToutes, courbes, "% du PIB", false, 0, true, obs, "projection", [],
    "Année", [2, 1], "L'écart : vert s'il en reste, rouge s'il en manque",
    // L'axe gradue de quatre en quatre ; les chiffres, eux, portent le dixième.
    // Sans lui, l'écart entre les deux courbes — un point et demi de PIB, tout
    // le sujet de la carte — se lirait « 14 » contre « 13 ».
    1,
  );
  const equilibre = solde.premiereAnneeEquilibree(reforme);
  // « en 2043 » et « jamais » ne se branchent pas au même endroit de la
  // phrase : l'un complète le verbe, l'autre le nie, et le repli posé sur le
  // seul millésime donnait « les comptes se rééquilibrent en jamais ».
  const retourEquilibre = equilibre
    ? `les comptes se rééquilibrent en ${equilibre}`
    : "les comptes ne se rééquilibrent jamais";

  // -- le second graphique : d'où vient l'argent ---------------------------
  const anneesVentilees = comptes.anneesVentilees();
  const premiereVentilee = anneesVentilees[0];
  const derniereVentilee = anneesVentilees[anneesVentilees.length - 1];
  const bandes = GROUPES.map((groupe) => new g.Serie(
    groupe.libelle,
    anneesVentilees.map((annee) => comptes.ressourceGroupe(groupe.code, annee) * 100),
    groupe.couleur,
  ));
  const provenance = g.graphique(
    "D'où viennent les ressources du système de retraite, de "
    + `${premiereVentilee} à ${derniereVentilee}, en part du PIB`,
    anneesVentilees, bandes, "% du PIB", true, 0, true, null, "", [], "Année",
    null, "", 1,
  );
  const partSalaires = comptes.partGroupe("salaires", derniereVentilee);
  const partImpotsDebut = comptes.partGroupe("impots", premiereVentilee);
  const partImpotsFin = comptes.partGroupe("impots", derniereVentilee);

  // -- les deux cartes -----------------------------------------------------
  const carteBilan = g.cle(
    "La retraite coûte-t-elle plus qu'elle ne rapporte ?",
    `Oui, un peu : ${milliards(Math.abs(manque), 1)} de trop en ${obs}.
<strong>L'écart va se creuser</strong> : en ${solde.derniereAnnee} il
manquerait
${g.pourcentage(Math.abs(horizon.solde("actuel") / horizon.depense("actuel")), false, 0)}
de la facture. En comptes notionnels dès ${bascule}, ${retourEquilibre}.`,
    bilan,
    `Sources : DREES jusqu'en ${solde.premiereAnnee - 1}, Conseil
d'orientation des retraites ensuite — c'est lui qui projette, pas nous. En
${g.terme("part du PIB")} : sur 100 € produits en France, combien vont aux
retraites.`,
    "cout-bilan",
  );

  const carteProvenance = g.cle(
    "Qui paie ?",
    `Les salaires, pour ${g.pourcentage(partSalaires, false, 0)} :
c'est ce qui est prélevé sur chaque fiche de paie. Le reste vient surtout de
l'impôt, et <strong>cette part a doublé en vingt ans</strong> :

${g.pourcentage(partImpotsDebut, false, 0)} en ${premiereVentilee},
${g.pourcentage(partImpotsFin, false, 0)} en ${derniereVentilee}.`,
    provenance + g.depliant(
      "Ce que contient chaque part",
      g.gloses(GROUPES.map((groupe) => [groupe.libelle, groupe.explication])),
    ),
    `Source : Conseil d'orientation des retraites. Ce détail n'est publié
que de ${premiereVentilee} à ${derniereVentilee}.`,
    "cout-provenance",
  );

  // Le détail est rendu AVANT le gabarit final : c'est de lui, et des deux
  // cartes, que le plan de la page se déduit.
  // -- ce que personne n'a cotisé -------------------------------------------
  //
  // UN CHIFFRE, ET SON DÉNOMINATEUR AVEC LUI. La part des avantages non
  // contributifs se lit sur le risque vieillesse-survie des comptes de la
  // protection sociale, à la dernière année que la DREES publie ; les trois
  // chiffres d'ouverture sont ceux du COR, à une autre année, sur un compte
  // plus étroit. La phrase porte donc son propre total, et dit qu'il n'est
  // pas celui des cartes. Le détail par famille est dans le dépliant des
  // dépenses, sur ce même total, et le dispositif par dispositif sur la page
  // Avantages.
  const avantages = contexte.avantages().derniere;
  let nonCotise = "";
  if (avantages && avantages.observee > 0) {
    nonCotise = `
<div class="note"><strong>Ce que personne n'a cotisé.</strong> Réversion,
minima, trimestres pour enfants : ${milliards(avantages.gratuit, 1)} en
${avantages.annee}, soit
${g.pourcentage(avantages.gratuit / avantages.observee, false, 1)} de la
dépense vieillesse-survie (${milliards(avantages.observee, 1)}, un périmètre
plus large que les cartes).
<a href="${g.lien("/avantages")}">La page Avantages</a> les détaille.</div>
`;
  }

  const detail = [
    coutDetailDepense(contexte),
    coutDetailRessources(contexte),
    coutDetailTransferts(contexte),
    coutDetailScenarios(contexte),
    coutDetailEquilibre(contexte),
    coutDetailPostes(contexte),
    coutDetailDette(contexte),
    coutDetailFrise(contexte),
    coutDetailGarantie(contexte),
    coutDetailCapitalisation(contexte),
    coutDetailPoids(contexte),
    coutDetailSources(contexte),
    coutDetailLimites(contexte),
  ].join("");
  const plan = g.plan(carteBilan + carteProvenance + detail, "/cout");

  const tete = g.affiche(
    "Le coût",
    'Ce qui rentre, ce qui sort, '
    + '<span class="cle-texte">ce qui manque.</span>',
    "Vos cotisations ne sont pas mises de côté. Elles paient aussitôt les "
    + "pensions de ceux qui sont déjà retraités : c'est la "
    + g.terme("répartition") + ".",
  );

  return `
${tete}

<div class="note resume"><strong>En clair.</strong> En ${obs}, les retraites
ont coûté un peu plus qu'elles n'ont rapporté : il a manqué
${milliards(manque, 1)}, soit ${g.pourcentage(partManquante, false, 1)} de la
facture. L'argent vient des cotisations pour l'essentiel, et de plus en plus
de l'impôt. Sans rien changer, il manquerait en ${solde.derniereAnnee}
${g.pourcentage(Math.abs(horizon.solde("actuel") / horizon.depense("actuel")), false, 0)}
de la facture. Un système en comptes notionnels ne dépenserait pas moins : il
servirait le même argent, réparti autrement, et se réglerait chaque année au
lieu d'attendre une réforme.</div>

<div class="fiches reperes">${reperes}</div>

${plan}

${carteBilan}

${carteProvenance}
${nonCotise}
<div class="note"><strong>Dépenser moins n'est pas économiser.</strong> Un
système en ${g.terme("comptes notionnels", "compte notionnel")} ne laisse pas d'argent
dormir : il remonte les pensions jusqu'à l'équilibre. La courbe en pointillés
ne dit donc pas « on dépenserait moins ». Elle dit : <em>avec le même argent,
on servirait autant, mais réparti autrement entre les carrières</em>. La
courbe jaune pleine dit ce que la proposition encaisserait, et l'écart entre
les deux jaunes est son solde.</div>

<h2>Et pour vous ?</h2>
<p>Tout cela est un total national. Ce que chaque règle donne sur votre
carrière se calcule en quelques secondes, dans votre navigateur.</p>
<p class="actions"><a class="bouton" href="${g.lien("/simuler")}">Calculer ma
retraite</a><a href="${g.lien("/cas-types")}">Voir treize carrières types</a></p>

<h2>Pour aller plus loin</h2>
<p class="chapeau">Tout ce que cette page doit pouvoir justifier est ici.</p>

${detail}
`;
}

/** Le détail de la dépense : en euros, puis système par système. */
/**
 * La couleur de chaque famille de l'inventaire, dans l'ordre où le comptage les
 * empile. Les écarts structurels n'y sont pas : ils ne sont pas des
 * dispositifs, ils ne se comptent pas avec eux, et l'inventaire le dit.
 */
const COULEURS_FAMILLES = [
  ["age_et_bonifications", "var(--serie-2)"],
  ["droits_familiaux", "var(--serie-3)"],
  ["minima_de_pension", "var(--serie-4)"],
  ["droits_derives", "var(--serie-5)"],
  ["periodes_non_cotisees", "var(--serie-6)"],
  ["autres_avantages", "var(--serie-7)"],
];

/** Les couleurs des lignes de coût, dans l'ordre de la légende. */
const COULEURS_LIGNES = [
  "var(--serie-2)", "var(--serie-3)", "var(--serie-4)", "var(--serie-5)",
  "var(--serie-6)", "var(--serie-7)", "var(--serie-8)", "var(--serie-9)",
  "var(--serie-1)",
];

/** La couleur de chaque motif de départ anticipé. */
const COULEURS_MOTIFS = {
  regime_special: "var(--serie-2)",
  classement: "var(--serie-4)",
  carriere_longue: "var(--serie-5)",
};

/** Ce que chacun des quatre états du modèle veut dire, en français courant. */
const LIBELLES_ETATS = {
  chiffre: "chiffré",
  integre: "servi, chiffré à part",
  declare: "déclaré, non servi",
  absent: "absent",
};

/**
 * Tous les avantages non contributifs, depuis quand, et ce qu'ils coûtent.
 *
 * TROIS GRAPHIQUES, ET ILS N'ONT PAS LE MÊME STATUT. C'est la contrainte de
 * construction de cette page, et elle décide de l'ordre : le premier est une
 * DONNÉE — combien de dispositifs existent chaque année —, le deuxième une
 * MESURE et un plancher très bas, le troisième mesure autre chose, les annuités
 * servies avant l'âge légal. Voir la référence Python pour le détail.
 */
function avantages(contexte) {
  const inventaire = contexte.inventaireAvantages();
  const c = contexte.avantages();
  const derniere = c.derniere;
  // Ce que la page annonce est ce que son tableau montre : les dispositifs qui
  // PORTENT un chiffre, et non ceux que le modèle sait chiffrer. Voir pages.py.
  const total = inventaire.avantages.length;
  const chiffres = inventaire.avantages.filter(
    (avantage) => c.derniere
      && c.derniere.lignes[avantage.ligne_cascade || avantage.code],
  ).length;
  // Combien de périodes du catalogue déclarent la réversion : le chiffre est
  // COMPTÉ et non écrit, pour qu'une fiche ajoutée le déplace.
  let declarations = 0;
  for (const regime of contexte.simulateur().catalogue) {
    for (const periode of regime.periodes) {
      if ((periode.avantages_non_contributifs || []).includes("reversion")) {
        declarations += 1;
      }
    }
  }

  // -- premier graphique : combien existent, et depuis quand ---------------
  //
  // Les bornes sont LUES et non écrites : ajouter à l'inventaire un dispositif
  // plus ancien doit déplacer le bord du cadre, et pas seulement une ligne de
  // tableau.
  const dispositifs = inventaire.avantages.filter(
    (a) => a.famille !== "ecarts_structurels",
  );
  const premiereFrise = Math.min(...dispositifs.map((a) => a.creation));
  const derniereFrise = contexte.base.annee_courante;
  const anneesFrise = [];
  for (let annee = premiereFrise; annee <= derniereFrise; annee += 1) {
    anneesFrise.push(annee);
  }
  const familles = {};
  for (const famille of inventaire.familles) familles[famille.code] = famille.libelle;
  const bandes = COULEURS_FAMILLES.map(([code, couleur]) => new g.Serie(
    familles[code],
    anneesFrise.map((annee) => dispositifs.filter(
      (a) => a.famille === code && a.creation <= annee
        && (a.fin === null || a.fin >= annee),
    ).length),
    couleur,
  ));
  const enVigueur = bandes.reduce(
    (somme, bande) => somme + bande.valeurs[bande.valeurs.length - 1], 0,
  );
  const frise = g.graphique(
    `Nombre d'avantages non contributifs en vigueur chaque année, par famille, `
    + `de ${premiereFrise} à ${derniereFrise}`,
    anneesFrise, bandes, "dispositifs", true,
  );

  // -- les trois chiffres d'ouverture --------------------------------------
  const reperes = g.fiche(
    "Avantages non contributifs recensés",
    String(total),
    "du minimum vieillesse à la bonification du cinquième",
  ) + g.fiche(
    "Ce que le modèle sait en chiffrer",
    milliards(derniere.gratuit, 1),
    `${chiffres} d'entre eux, en ${derniere.annee}`,
  ) + g.fiche(
    "Servi avant l'âge légal",
    milliards(derniere.anticipee, 1),
    `${g.pourcentage(derniere.anticipee / derniere.observee, false, 1)} de la dépense`,
  );

  // -- deuxième graphique : ce qu'ils coûtent ------------------------------
  // LA FENÊTRE EST CELLE OÙ TOUTES LES LIGNES SONT PUBLIÉES, et non celle de
  // la plus ancienne. Les lignes calculées remontent à 1959 ; la réversion,
  // qui est lue et non calculée, commence en 2004. Les empiler sur la fenêtre
  // longue dessinerait une falaise de vingt-cinq milliards cette année-là, et
  // le lecteur y verrait un saut de dépense là où il n'y a qu'un début de
  // publication.
  //
  // La fenêtre se CALCULE au lieu de s'écrire : elle est l'intersection des
  // fenêtres de publication des lignes LUES — 2004 pour la réversion, 2020
  // pour les sous-postes des comptes. Elle s'est resserrée d'elle-même le jour
  // où huit postes publiés ont rejoint la réversion. Voir pages.py.
  const anneesCout = c.annees.map((ligne) => ligne.annee);
  const lues = LIGNES_LUES.filter((ligne) => c.lignes.includes(ligne));
  const fenetre = c.annees.filter(
    (ligne) => lues.every((lue) => ligne.lignes[lue] !== undefined));
  const anneesPubliees = fenetre.map((ligne) => ligne.annee);
  // Le tracé empile les FAMILLES, pas les lignes : quinze lignes pour neuf
  // couleurs, c'est six bandes qui portent la couleur d'une autre. Voir
  // pages.py pour le raisonnement complet.
  const parFamille = new Map();
  for (const ligne of c.lignes) {
    const famille = inventaire.familleDeLigne(ligne);
    if (famille === null) continue;
    if (!parFamille.has(famille)) parFamille.set(famille, new Map());
    const cumul = parFamille.get(famille);
    for (const annee of fenetre) {
      cumul.set(annee.annee,
        (cumul.get(annee.annee) || 0) + (annee.lignes[ligne] || 0));
    }
  }
  const ordonnees = inventaire.familles
    .filter((f) => [...(parFamille.get(f.code) || new Map()).values()]
      .some((v) => v))
    .sort((a, b) => (parFamille.get(b.code).get(derniere.annee) || 0)
      - (parFamille.get(a.code).get(derniere.annee) || 0));
  const couts = [...ordonnees].reverse().map((famille, rang) => new g.Serie(
    famille.libelle,
    fenetre.map((annee) => (parFamille.get(famille.code).get(annee.annee) || 0) / 1000),
    COULEURS_LIGNES[rang % COULEURS_LIGNES.length],
  ));
  const reversion = derniere.lignes.reversion || 0;
  const courbeCout = anneesPubliees.length === 0 ? "" : g.graphique(
    `Coût des avantages non contributifs que l'on sait chiffrer, par `
    + `famille, de ${anneesPubliees[0]} à ${anneesPubliees[anneesPubliees.length - 1]}`,
    anneesPubliees, couts, "Md€ courants", true, 0, true, null, "", [], "Année",
    null, "", 1,
  );

  // -- graphique long : le modèle seul, sur toute sa longueur --------------
  // Le tracé précédent est juste mais court, celui-ci long mais étroit : les
  // deux ne s'additionnent jamais. Voir pages.py pour le raisonnement complet.
  const anneesModele = c.annees.map((a) => a.annee);
  const famillesModele = new Map();
  for (const ligne of c.lignesModele) {
    const famille = inventaire.familleDeLigne(ligne);
    if (famille === null) continue;
    if (!famillesModele.has(famille)) famillesModele.set(famille, new Map());
    const cumul = famillesModele.get(famille);
    for (const a of c.annees) {
      cumul.set(a.annee, (cumul.get(a.annee) || 0) + (a.modele[ligne] || 0));
    }
  }
  const finModele = anneesModele[anneesModele.length - 1];
  const ordreModele = inventaire.familles
    .filter((f) => [...(famillesModele.get(f.code) || new Map()).values()].some((v) => v))
    .sort((x, y) => (famillesModele.get(y.code).get(finModele) || 0)
      - (famillesModele.get(x.code).get(finModele) || 0));
  const bandesModele = [...ordreModele].reverse().map((famille, rang) => new g.Serie(
    famille.libelle,
    anneesModele.map((a) => (famillesModele.get(famille.code).get(a) || 0) / 1000),
    COULEURS_LIGNES[rang % COULEURS_LIGNES.length],
  ));
  const courbeLongue = anneesModele.length === 0 ? "" : g.graphique(
    `Ce que le modèle reconstitue seul, par famille, de `
    + `${anneesModele[0]} à ${finModele}`,
    anneesModele, bandesModele, "Md€ courants", true, 0, true, null, "", [],
    "Année", null, "", 1,
  );
  const partDebutModele = c.annees[0].observee
    ? c.annees[0].gratuitModele / c.annees[0].observee : 0;
  const partFinModele = derniere.observee
    ? derniere.gratuitModele / derniere.observee : 0;

  // -- troisième graphique : les annuités servies trop tôt -----------------
  const anticipees = MOTIFS.map((motif) => new g.Serie(
    LIBELLES_MOTIFS[motif],
    c.annees.map((annee) => (annee.anticipees[motif] || 0) / 1000),
    COULEURS_MOTIFS[motif],
  ));
  const courbeAge = g.graphique(
    `Pensions servies avant l'âge légal, par ce qui ouvre le départ, de `
    + `${anneesCout[0]} à ${anneesCout[anneesCout.length - 1]}`,
    anneesCout, anticipees, "Md€ courants", true, 0, true, null, "", [],
    "Année", null, "", 1,
  );

  const carteFrise = g.cle(
    "Combien le système compte-t-il d'avantages qui ne sont pas cotisés ?",
    `<strong>${enVigueur} aujourd'hui, contre un seul en
${premiereFrise}.</strong> Presque aucun n'a jamais été supprimé : la courbe
monte pendant deux siècles et ne redescend que trois fois.`,
    frise,
    `Source : inventaire du dépôt, base légale lue article par article
dans la base LEGI. Ce graphique ne calcule rien : il compte des lignes.`,
    "avantages-frise",
  );

  const carteCout = g.cle(
    "Combien coûtent ceux que l'on sait chiffrer ?",
    `<strong>${milliards(derniere.gratuit, 1)} en ${derniere.annee}, soit
${g.pourcentage(derniere.gratuit / derniere.observee, false, 1)} de la
dépense</strong>, dont ${milliards(reversion, 1)} pour la seule
<strong>réversion</strong>. Le COR chiffre les droits de solidarité à « de
l'ordre d'un cinquième » des retraites : on y est. ${chiffres} des ${total}
dispositifs portent un chiffre ; le tableau ci-dessous nomme les autres et dit
ce qui manque à chacun.`,
    courbeCout
    + "<h3>Et sur soixante-six ans ?</h3>"
    + `<p class="chapeau">Le tracé ci-dessus est juste mais court : les
comptes ne détaillent leurs postes que depuis ${anneesPubliees[0]}. Celui-ci est
long mais étroit. Il porte les ${ordreModele.length} familles que le modèle
reconstitue seul, de ${anneesModele[0]} à ${finModele}, calculées de la
même façon d'un bout à l'autre.</p>
<p><strong>Les deux ne s'additionnent pas et ne se comparent pas :</strong>
${g.pourcentage(partFinModele, false, 1)} de la dépense ici,
${g.pourcentage(derniere.gratuit / derniere.observee, false, 1)} au-dessus.
C'est le champ de la mesure qui change, et ce tracé donne une forme.</p>`
    + courbeLongue
    + "<h3>Tous les dispositifs, un par un</h3>"
    + `<p class="chapeau">Ce que chacun coûte en ${derniere.annee}, et,
quand la case est vide, pourquoi elle l'est. La dernière famille ne s'additionne
pas aux autres : elle n'est pas faite de dispositifs.</p>`
    + avantagesTableComplete(contexte)
    + g.depliant(
      "Pourquoi ce chiffre est un plancher, et de combien",
      `<p>Trois choses à savoir avant de citer ce chiffre.</p>
<p><strong>Les plus grosses lignes sont lues, pas calculées.</strong> La
réversion, le minimum vieillesse, la majoration pour enfants, les pensions
d'orphelin, celles servies pour inaptitude ou invalidité : leur montant vient
des comptes de la protection sociale et de l'enquête annuelle de la DREES
auprès des caisses, poste par poste. Ce sont des comptes de personnes réelles,
et ce sont les chiffres les plus sûrs de la page. Le tableau ci-dessus le dit
case par case.</p>
<p><strong>Là où les deux existaient, le poste publié a remplacé la ligne
calculée</strong>, et l'écart entre les deux était énorme. Un seul des treize
cas types de la grille a des enfants (deux, quand le seuil de la majoration
est à trois), et le modèle chiffrait donc à zéro un avantage qui pèse
7,8 milliards. Une grille de cas types sert à <em>comparer</em> des systèmes
sur une même carrière, où les erreurs de niveau s'annulent au dénominateur ; le
coût d'un avantage est un compte de <em>population</em>, et il se lit chez celui
qui compte.</p>
<p><strong>La fenêtre est courte parce que les postes publiés le sont.</strong>
Les lignes calculées remontent à 1959 et la réversion à 2004, mais les
sous-postes des comptes ne sont publiés que depuis 2020 : le tracé s'arrête là
où <em>chaque</em> terme est observé. Les empiler plus tôt dessinerait une
falaise de quarante milliards, qui ne serait qu'un début de publication. Le
premier graphique de la page, lui, remonte à 1800.</p>
<p><strong>Et la forme longue parle.</strong> Le minimum vieillesse faisait
${g.pourcentage(partDebutModele, false, 0)} de la dépense en
${c.annees[0].annee}, quand il y avait peu de pensions et beaucoup de
vieillards sans droits ; il s'est éteint à mesure que les carrières se
complétaient. La courbe remonte ensuite, à partir des années 1980 : les minima
de pension et les périodes assimilées rattrapent des carrières incomplètes là
où l'on secourait des carrières absentes.</p>
<p><strong>Et ce total reste un plancher.</strong> Les bonifications de service
des militaires et des corps actifs, les départs anticipés pour handicap, la
majoration de durée au titre du congé parental ne sont ni calculés par le
modèle ni isolés par les comptes. Le tableau ci-dessus les nomme et dit, pour
chacun, ce qui manque.</p></p>`,
    ),
    `Sources : pour les lignes lues, les comptes de la protection
sociale de la DREES, sous-postes du risque vieillesse-survie, et son enquête
annuelle auprès des caisses de retraite ; pour les lignes calculées,
décomposition du scénario 1 sur la grille de carrières types, rapportée à la
dépense observée, dont seule la part est modélisée. Toutes certifiées, année
par année.`,
    "avantages-cout",
  );

  const partClassement = derniere.anticipee > 0
    ? (derniere.anticipees.classement || 0) / derniere.anticipee
    : 0;
  const carteAge = g.cle(
    "Et partir plus tôt, combien cela coûte-t-il ?",
    `<strong>${milliards(derniere.anticipee, 1)} de pensions servies avant
l'âge légal en ${derniere.annee}</strong>, soit treize fois ce que les mêmes
dispositifs ajoutent au <em>montant</em> des pensions. Une annuité versée avant
l'âge légal n'est rattrapée par aucune décote.`,
    courbeAge + g.depliant(
      "Pourquoi le montant ne suffit pas à le dire",
      `<p>La décote est <strong>plafonnée à vingt trimestres</strong>.
Un agent de catégorie active parti à 57 ans et un agent sédentaire parti le même
jour butent donc tous deux sur le même plafond : leurs pensions ne diffèrent que
de 868 € par an. Le montant ne sait pas distinguer celui qui part cinq ans trop
tôt ; la durée le sait.</p>
<p>Le classement de l'emploi en porte
${g.pourcentage(partClassement, false, 0)}. Le reste se partage entre les
âges propres des régimes spéciaux et la <strong>carrière longue</strong>, qui
n'apparaît qu'après 2010 : mécaniquement, à mesure que l'âge légal monte
au-dessus de l'âge auquel une carrière commencée tôt réunit sa durée.</p>
<p><strong>Réserve.</strong> Ce sont des annuités <em>anticipées</em>, non un
surcoût <em>net</em> : partir tôt, c'est aussi cotiser moins et mourir plus tôt
en moyenne. C'est exactement l'arbitrage qu'un coefficient de conversion
notionnel rend automatique, et que le droit actuel ne rend nulle part.</p>`,
    ),
    `Source : même décomposition, comparée à l'âge légal de chaque
génération plutôt qu'à un âge fixe, qui compterait comme anticipé un départ que
le droit de l'époque disait à l'heure.`,
    "avantages-age",
  );

  const detail = avantagesDetailListe(contexte)
    + avantagesDetailEtats(contexte)
    + avantagesDetailLimites(contexte);
  const plan = g.plan(carteFrise + carteCout + carteAge + detail, "/avantages");

  const tete = g.affiche(
    "Les avantages",
    'Ce que la retraite verse <span class="cle-texte">sans que personne '
    + "l'ait cotisé.</span>",
    "Un compte notionnel ne sert que ce qui a été versé. Le système actuel "
    + "sert bien davantage, et ce qui les sépare porte des noms : minimum "
    + "contributif, trimestres gratuits, départ anticipé, réversion.",
  );

  return `
${tete}

<div class="note resume"><strong>En clair.</strong> Le système actuel compte
${enVigueur} dispositifs qui ajoutent à une pension sans qu'aucune cotisation
les ait payés, contre un seul en ${premiereFrise}. Le modèle sait en chiffrer
${chiffres} : ${milliards(derniere.gratuit, 1)} en ${derniere.annee}, dont
${milliards(derniere.lignes.reversion || 0, 1)} de réversion, qui est lue
et non calculée. Il mesure à
part ${milliards(derniere.anticipee, 1)} de pensions servies avant l'âge légal,
que nulle décote ne rattrape. Les deux chiffres sont des planchers, et cette
page dit de combien.</div>

<div class="fiches reperes">${reperes}</div>

${plan}

${carteFrise}

${carteCout}

${carteAge}

<div class="note"><strong>Aucun de ces dispositifs n'est illégitime.</strong>
Chacun a été voté pour une raison, et plusieurs corrigent de vraies injustices.
Ce qui pose problème est leur opacité. Personne ne reçoit le décompte de ce
qu'il a cotisé puis de ce qu'on lui ajoute. Un compte notionnel ne les interdit
pas : il oblige à les payer par l'impôt, sous leur nom, plutôt que par une
formule que nul ne lit.</div>

<h2>Et pour vous ?</h2>
<p>Ce que ces règles donnent sur votre carrière se calcule en quelques secondes,
dans votre navigateur : la simulation affiche votre part cotisée, puis chaque
avantage, ligne à ligne.</p>
<p class="actions"><a class="bouton" href="${g.lien("/simuler")}">Calculer ma
retraite</a><a href="${g.lien("/cout")}">Voir ce que tout cela coûte</a></p>

<h2>Pour aller plus loin</h2>
<p class="chapeau">Les mêmes dispositifs, avec leurs textes et leurs dates.</p>

${detail}
`;
}

/**
 * Chaque dispositif sur sa ligne, avec son coût ou la raison qui l'en prive.
 *
 * C'EST LE CŒUR DE LA PAGE. Les graphiques ne portent que ce qui se chiffre ;
 * une page qui affirme qu'il existe quarante-deux avantages doit les NOMMER tous,
 * et dire pour chacun ce qu'on en sait. Un blanc sans raison est une dette ;
 * une raison écrite est une limite.
 */
function avantagesTableComplete(contexte) {
  const inventaire = contexte.inventaireAvantages();
  const c = contexte.avantages();
  const derniere = c.derniere;
  const montants = derniere === null ? {} : derniere.lignes;

  // Deux dispositifs peuvent partager une ligne, et le montant ne doit alors
  // paraître qu'une fois : voir pages.py.
  const vues = new Set();

  const blocs = [];
  for (const famille of inventaire.familles) {
    const lignes = [];
    for (const avantage of inventaire.parFamille(famille.code)) {
      const ligne = avantage.ligne_cascade || avantage.code;
      const montant = montants[ligne];
      if (montant && vues.has(ligne)) {
        // Deux dispositifs peuvent partager une ligne : le premier porte le
        // chiffre, le second dit où il est. Voir pages.py.
        const porteur = inventaire.avantages.find(
          (a) => (a.ligne_cascade || a.code) === ligne).libelle;
        lignes.push([
          avantage.libelle, "—",
          "le modèle n'en tient qu'une seule ligne, celle de « "
          + echapper(porteur) + " » : le chiffre ci-dessus les porte toutes les deux",
        ]);
      } else if (montant) {
        vues.add(ligne);
        const origine = LIGNES_LUES.includes(ligne) ? "lu" : "calculé";
        lignes.push([
          avantage.libelle,
          milliards(montant, 2),
          `<span class="discret">${origine}</span>`,
        ]);
      } else {
        lignes.push([avantage.libelle, "—", echapper(avantage.sans_chiffre || "")]);
      }
    }
    if (lignes.length === 0) continue;
    blocs.push(
      '<div class="dispositifs">'
      + `<h4>${echapper(famille.libelle)}</h4>`
      + g.tableau(
        ["Dispositif", `Coût en ${derniere.annee}`,
          "D'où vient le chiffre, ou pourquoi il manque"],
        lignes, ["", "nombre", "texte"],
        `${famille.libelle} : ${lignes.length} dispositifs et leur coût`, true,
      )
      + "</div>"
    );
  }
  return blocs.join("");
}

/** L'inventaire entier, famille par famille, avec sa base légale. */
function avantagesDetailListe(contexte) {
  const inventaire = contexte.inventaireAvantages();
  const blocs = [];
  for (const famille of inventaire.familles) {
    const lignes = inventaire.parFamille(famille.code).map((avantage) => [
      avantage.libelle,
      avantage.base_legale.join("; ") || "—",
      String(avantage.creation),
      avantage.fin === null ? "en vigueur" : String(avantage.fin),
      LIBELLES_ETATS[avantage.etat_modele],
    ]);
    if (lignes.length === 0) continue;
    blocs.push(
      `<h4>${echapper(famille.libelle)}</h4><p>${echapper(famille.quoi)}</p>`
      + g.tableau(["Dispositif", "Base légale", "Depuis", "Jusqu'à",
        "Dans le modèle"], lignes, ["", "texte", "nombre", "texte", "texte"],
      `${famille.libelle} : ${lignes.length} dispositifs`, true),
    );
  }
  return g.depliant(
    `Les ${inventaire.avantages.length} dispositifs, avec leur base légale et leurs dates`,
    blocs.join(""),
    "avantages-liste",
  );
}

/** Ce que le modèle sait de chacun, et ce qu'il n'en sait pas. */
function avantagesDetailEtats(contexte) {
  const inventaire = contexte.inventaireAvantages();
  const c = contexte.avantages();
  const lignes = [
    ["chiffré", String(inventaire.compte("chiffre")),
      "La cascade du scénario 1 en isole le montant en euros. La somme de "
      + "ces lignes vaut exactement la pension moins sa part cotisée."],
    ["servi, chiffré à part", String(inventaire.compte("integre")),
      "Le scénario 1 les sert, mais l'effet passe par un trimestre, un âge "
      + `ou une assiette. ${NEUTRALISATIONS.length} sont mesurés par retrait : on `
      + "refait la pension sans l'avantage, et l'écart est le chiffre. Les "
      + `${inventaire.compte("integre") - NEUTRALISATIONS.length} derniers ne sont `
      + "pas des dispositifs, et se lisent ailleurs."],
    ["déclaré, non servi", String(inventaire.compte("declare")),
      "Une fiche de régime les déclare, aucun code ne les sert. La "
      + "réversion est de ceux-là : 756 périodes du catalogue l'annoncent, et "
      + "le modèle ne la produira jamais, faute de décrire un ménage. Son coût "
      + "est donc LU dans l'enquête de la DREES auprès des caisses, et c'est "
      + "le chiffre le plus sûr de cette page."],
    ["absent", String(inventaire.compte("absent")),
      "Ni déclarés ni servis : les bonifications de service, les départs "
      + "pour handicap ou inaptitude, l'allocation veuvage. C'est un écart au "
      + "droit positif, et le dépôt le nomme plutôt que de l'estimer."],
  ];
  const clesRefus = Object.keys(c.refus).sort();
  const refus = clesRefus.map(
    (ligne) => `<p><strong>${echapper(ligne)}</strong> — ${echapper(c.refus[ligne])}</p>`,
  ).join("");
  const note = refus
    ? `<h4>Ce que le modèle a refusé de mesurer</h4><p>Un refus est un `
      + `résultat : il dit qu'une contrefactuelle existe mais ne vaut rien, `
      + `ce qui est plus sûr qu'un chiffre plausible.</p>${refus}`
    : "";
  return g.depliant(
    "Ce que le modèle sait de chacun",
    g.tableau(["État", "Combien", "Ce que cela veut dire"], lignes, ["", "nombre", "texte"],
      "Ce que le modèle sait de chaque avantage", true) + note,
    "avantages-etats",
  );
}

/** Les trois réserves de la page, et pourquoi elles y sont. */
function avantagesDetailLimites(contexte) {
  // Le compte des lignes « à certifier » se calcule : voir pages.py.
  const aCertifier = contexte.inventaireAvantages().avantages.filter(
    (avantage) => avantage.base_legale.some((t) => t.includes("certifier")),
  ).length;
  // Zéro est un résultat, et il demande une autre phrase. Voir pages.py.
  const reserveLegale = aCertifier
    ? `${aCertifier} lignes portent encore la mention « à certifier » :
leurs textes vivent dans des statuts de corps ou des lois de circonstance qui
n'ont pas tous été lus. Une déduction n'est pas une lecture.`
    : `Aucune ne porte plus la mention « à certifier » : les
bonifications des corps actifs renvoyaient encore, il y a peu, à des « statuts
particuliers » que personne n'avait ouverts. Lire n'est pas appliquer.`;
  return g.depliant(
    "Trois choses que ces chiffres ne disent pas",
    `<p><strong>Elle ne dit pas ce que le système économiserait.</strong>
Supprimer un avantage ne rend pas son coût : il faudrait décider ce que
l'assuré aurait fait sans lui — travailler plus longtemps, partir avec moins, ne
pas partir. Le dépôt ne tranche pas à sa place, et ces chiffres disent ce qui
est <em>versé</em>, non ce qui serait <em>épargné</em>.</p>
<p><strong>Elle ne compte pas deux fois la même chose.</strong> Les trois
« écarts structurels » de l'inventaire (une décote qui n'est pas actuarielle,
un rendement supérieur à ce que l'assiette porte, un financement par l'impôt)
ne sont pas des dispositifs et ne figurent donc pas dans le comptage. Ils
portent sur la même pension, vue sous un autre angle, et les additionner serait
un double compte.</p>
<p><strong>Elle ne remplace pas la loi.</strong> Chaque base légale a été lue
dans la base LEGI, version par version. ${reserveLegale}</p>`,
    "avantages-limites",
  );
}

function coutDetailDepense(contexte) {
  const depenses = contexte.depenses();
  const c = contexte.cout();
  const euros = c.anneeEuros;
  const derniere = depenses.derniereAnnee;
  const annees = c.annees.map((ligne) => ligne.annee);
  const ventilees = depenses.anneesVentilees();
  const premiereVentilee = ventilees[0];
  const total = depenses.depense(derniere);
  const repartition = depenses.repartition(derniere);
  const autres = {};
  for (const systeme of SYSTEMES) {
    if (!systeme.repartition) {
      autres[systeme.code] = depenses.depenseSysteme(systeme.code, derniere);
    }
  }

  const courbeConstants = new g.Serie(
    `En euros constants de ${euros}`,
    c.annees.map((ligne) => ligne.observeeConstants / 1000),
    "var(--serie-1)",
  );
  const courbeCourants = new g.Serie(
    "En euros courants de chaque année",
    c.annees.map((ligne) => ligne.observee / 1000),
    "var(--serie-2)", true,
  );

  const reunies = BANDES_COUT.map(([code]) => code);
  const bandes = BANDES_COUT.map(([code, couleur]) => new g.Serie(
    SYSTEMES.find((s) => s.code === code).libelle,
    ventilees.map((annee) => depenses.depenseSysteme(code, annee) / 1000),
    couleur,
  ));
  bandes.push(new g.Serie(
    "Autres régimes par répartition",
    ventilees.map((annee) => SYSTEMES
      .filter((s) => s.repartition && !reunies.includes(s.code))
      .reduce((somme, s) => somme + depenses.depenseSysteme(s.code, annee), 0) / 1000),
    "var(--serie-7)",
  ));
  bandes.push(new g.Serie(
    "Hors répartition obligatoire",
    ventilees.map((annee) => SYSTEMES
      .filter((s) => !s.repartition)
      .reduce((somme, s) => somme + depenses.depenseSysteme(s.code, annee), 0) / 1000),
    "var(--serie-9)", false,
    "capitalisation, dépendance, minimum vieillesse",
  ));

  // -- ce que personne n'a cotisé, par famille ------------------------------
  //
  // MÊME TOTAL QUE LE PREMIER PARAGRAPHE DU DÉPLIANT : `observee` est la
  // dépense du risque vieillesse-survie de l'année, celle-là même que `total`
  // porte. C'est ce qui autorise une part ici, et l'interdit sous les cartes
  // du haut, qui suivent le périmètre du COR à une autre année.
  const avantages = contexte.avantages().derniere;
  const inventaire = contexte.inventaireAvantages();
  let nonCotise = "";
  if (avantages && avantages.observee > 0) {
    const parFamille = {};
    for (const [ligne, montant] of Object.entries(avantages.lignes)) {
      const famille = inventaire.familleDeLigne(ligne);
      if (famille !== null) {
        parFamille[famille] = (parFamille[famille] || 0) + montant;
      }
    }
    const ordonnees = [...inventaire.familles]
      .filter((f) => (parFamille[f.code] || 0) > 0)
      .sort((a, b) => (parFamille[b.code] || 0) - (parFamille[a.code] || 0)
        || (a.code < b.code ? -1 : a.code > b.code ? 1 : 0));
    const lignesFamilles = ordonnees.map((famille) => [
      echapper(famille.libelle),
      milliards(parFamille[famille.code], 1),
      g.pourcentage(parFamille[famille.code] / avantages.observee, false, 1),
    ]);
    const partGratuite = g.pourcentage(avantages.gratuit / avantages.observee,
                                       false, 1);
    lignesFamilles.push([
      "<strong>Ensemble des avantages chiffrés</strong>",
      `<strong>${milliards(avantages.gratuit, 1)}</strong>`,
      `<strong>${partGratuite}</strong>`,
    ]);
    nonCotise = `
<h4>Ce que personne n'a cotisé</h4>
<p>Sur ces ${milliards(avantages.observee, 1)} de ${avantages.annee},
${milliards(avantages.gratuit, 1)}, soit ${partGratuite}, servent des droits
qu'aucune cotisation n'a ouverts : la pension du conjoint survivant, les
minima, les trimestres accordés pour un enfant ou une période de chômage, les
départs avant l'âge. La part se lit sur ce total-là, le risque
vieillesse-survie entier. Les cartes du haut suivent un autre compte, celui du
COR, en ${c.solde.derniereAnneeObservee} : elle ne s'y rapporte pas.</p>
${g.tableau(
    ["Famille", `${avantages.annee}`, "Part de la dépense"],
    lignesFamilles,
    ["", "nombre", "nombre"],
    `Avantages non contributifs chiffrés en ${avantages.annee}, par famille, `
    + "et part de la dépense vieillesse-survie",
    true,
  )}
<p class="discret">C'est un plancher : les plus grosses lignes sont lues dans
les comptes de la protection sociale et l'enquête de la DREES auprès des
caisses, les autres calculées sur la grille de cas types, et les dispositifs
que ni l'un ni l'autre ne mesurent restent sans chiffre.
<a href="${g.lien("/avantages")}">La page Avantages</a> les nomme un par un,
dit d'où vient chaque montant et pourquoi une case reste vide.</p>
`;
  }

  const duree = derniere - premiereVentilee;
  const macro = contexte.simulateur().macro;
  const lignesSystemes = SYSTEMES.map((systeme) => {
    const debut = depenses.depenseSysteme(systeme.code, premiereVentilee);
    const fin = depenses.depenseSysteme(systeme.code, derniere);
    const coefficient = macro.coefficientPrix(premiereVentilee, derniere);
    const croissance = debut > 0
      ? (fin / (debut * coefficient)) ** (1 / duree) - 1
      : 0.0;
    const cumul = ventilees.reduce((somme, annee) => somme
      + depenses.depenseSysteme(systeme.code, annee)
        * macro.coefficientPrix(annee, euros), 0);
    return [
      echapper(systeme.libelle),
      milliards(fin, 1),
      g.pourcentage(fin / total, false, 1),
      milliards(cumul, 0),
      g.pourcentage(croissance, true, 1),
      systeme.repartition ? "oui" : "non",
    ];
  });

  return g.depliant(`Le détail des dépenses, de ${c.premiereAnnee} à ${derniere}`, `
<p>Les ${milliards(total, 1)} de ${derniere} sont le risque
<strong>vieillesse-survie tout entier</strong> : les pensions, mais aussi le
minimum vieillesse, l'aide sociale aux personnes âgées et la retraite
supplémentaire par capitalisation. La <strong>répartition obligatoire</strong>
seule en fait ${milliards(repartition, 1)} : c'est cette grandeur-là qu'il faut
rapprocher des quelque 420 milliards que l'on cite d'ordinaire. Le reste est
${milliards(autres.aide_sociale_locale, 1)} de dépendance,
${milliards(autres.supplementaire, 1)} de capitalisation et
${milliards(autres.solidarite_etat, 1)} de solidarité de l'État.</p>

<h4>La même dépense, en euros</h4>
${g.graphique(
    `Dépenses du risque vieillesse-survie de ${c.premiereAnnee} à ${derniere}, `
    + "en milliards d'euros",
    annees, [courbeConstants, courbeCourants], "Md €")}
<p class="discret">Deux lectures de la même série. En euros courants, la
dépense est multipliée par cent quatre-vingt-treize depuis
${c.premiereAnnee} . Mais les prix aussi ont été multipliés par treize. En
euros constants, la multiplication est par quinze : c'est celle-là qui est
réelle. C'est pour éviter ce genre de piège que les cartes du haut sont en part
du PIB.</p>

<h4>Système par système</h4>
${g.graphique(
    `Dépenses de vieillesse-survie par système, ${premiereVentilee}-${derniere}, `
    + "en milliards d'euros courants",
    ventilees, bandes, "Md €", true)}
<p class="discret">La ventilation ne commence qu'en ${premiereVentilee} : de 1981
à 1989 la DREES publie une autre nomenclature, dont les périmètres ne se
raccordent pas à ceux-ci, et personne n'a publié le raccord. Le total, lui,
remonte à ${c.premiereAnnee}.</p>

${g.tableau(
    ["Système", `${derniere}`, "Part", `Cumul ${premiereVentilee}-${derniere}`,
      "Croissance réelle", "Répartition"],
    lignesSystemes,
    ["", "nombre", "nombre", "nombre", "nombre", ""],
    `Dépense de vieillesse-survie par système en ${derniere}, et cumul `
    + `depuis ${premiereVentilee}`,
    true,
  )}
${g.gloses(SYSTEMES.map((systeme) => [systeme.libelle, systeme.glose]))}
<p class="discret">Le cumul est en euros constants de ${euros} : additionner des
euros de 1990 et de ${derniere} n'aurait aucun sens. La croissance réelle est
celle de la dépense annuelle, déflatée, de ${premiereVentilee} à ${derniere}.
Deux chiffres se lisent en connaissant le découpage : le régime général absorbe
en 2020 les artisans et les commerçants, dont le régime a été adossé à la Cnav,
et les « régimes spéciaux » de la comptabilité nationale contiennent la CNRACL,
c'est-à-dire la fonction publique territoriale et hospitalière.</p>
${nonCotise}`, "cout-depenses");
}

/** La ventilation des ressources au découpage du COR, poste par poste. */
function coutDetailRessources(contexte) {
  const comptes = contexte.comptes();
  const ventilees = comptes.anneesVentilees();
  const premiere = ventilees[0];
  const derniere = ventilees[ventilees.length - 1];
  const lignes = POSTES.map((poste) => [
    echapper(poste.libelle),
    g.pourcentage(comptes.part(poste.code, premiere), false, 1),
    g.pourcentage(comptes.part(poste.code, derniere), false, 1),
    poste.contributive ? "oui" : "non",
  ]);
  const partCotisee = comptes.partContributive(derniere);
  return g.depliant("D'où vient l'argent, poste par poste", `
<p>Le graphique du haut regroupe les six postes du COR en quatre parts, parce
qu'un empilement à six bandes ne se lit pas. Les voici tels qu'ils sont
publiés.</p>

${g.tableau(
    ["Poste", `Part en ${premiere}`, `Part en ${derniere}`, "Cotisée"],
    lignes, ["", "nombre", "nombre", ""],
    `Structure des ressources du système de retraite, ${premiere} et ${derniere}`,
    true,
  )}
${g.gloses(POSTES.map((poste) => [poste.libelle, poste.glose]))}
<p class="discret">La colonne « cotisée » dit si le poste est un prélèvement
assis sur un revenu d'activité — la seule ressource qu'un compte notionnel
sache porter au crédit de quelqu'un. ${g.pourcentage(partCotisee, false, 0)}
des ressources de ${derniere} le sont, en comptant la contribution d'équilibre
que l'État verse au régime de ses propres fonctionnaires : le modèle la porte
déjà au compte du système 3, et c'est à ce titre qu'elle est comptée
ici, malgré un taux fixé pour équilibrer plutôt que pour acquérir. La part
cotisée <em>recule</em> : elle était de
${g.pourcentage(comptes.partContributive(premiere), false, 0)} en ${premiere}.</p>
`, "cout-ressources");
}

/**
 * Ce que la branche famille et l'assurance chômage versent, et à qui cela
 * revient. Le poste « transferts » de la structure des ressources est un
 * agrégat ; ce dépliant le ventile par celui qui paie, et dit la chose que le
 * coefficient d'équilibre ne dit pas : les scénarios notionnels suppriment les
 * droits que la branche famille finance, et comptent pourtant sa recette.
 */
function coutDetailTransferts(contexte) {
  const comptes = contexte.comptes();
  const solde = contexte.cout().solde;
  const premiere = comptes.premiereAnneeTransferts;
  // La dernière année où tout est connu : les quatre lignes de transfert, et
  // le compte observé qui leur donne un coefficient.
  const derniere = Math.min(comptes.derniereAnneeTransferts, solde.derniereAnneeObservee);
  const ligneSolde = solde.annee(derniere);
  const montant = (code, annee) => milliards(comptes.transfert(code, annee), 1);

  const lignes = [];
  for (const organisme of ORGANISMES) {
    for (const poste of POSTES_TRANSFERTS) {
      if (poste.organisme !== organisme.code) continue;
      lignes.push([
        echapper(poste.libelle), montant(poste.code, premiere),
        montant(poste.code, derniere),
        g.pourcentage(comptes.transfert(poste.code, derniere)
                      / comptes.pib.valeur(derniere) / comptes.ressource(derniere),
                      false, 1),
      ]);
    }
    lignes.push([
      `<strong>${echapper(organisme.libelle)}, ensemble</strong>`,
      milliards(comptes.transfertOrganisme(organisme.code, premiere), 1),
      milliards(comptes.transfertOrganisme(organisme.code, derniere), 1),
      g.pourcentage(comptes.transfertPartRessources(organisme.code, derniere), false, 1),
    ]);
  }

  const partPoste = comptes.part("transferts", derniere);
  let partVentilee = 0;
  for (const o of ORGANISMES) partVentilee += comptes.transfertPartRessources(o.code, derniere);
  const supprime = comptes.transfertSupprimePartPib(derniere);
  // Ce que la recette vaut en part des ressources, l'année où on la connaît ;
  // retirée à part CONSTANTE, elle multiplie tout coefficient par le même
  // facteur, et c'est la seule façon de la porter jusqu'à l'horizon du COR
  // sans projeter ce que personne ne projette.
  const partSupprimee = supprime / ligneSolde.ressources;
  const horizon = solde.annee(solde.derniereAnnee);
  // Le coefficient qu'on lirait si la recette restait comptée.
  // Le coefficient qu'on lirait si cette recette-là restait comptée. Celle-là
  // SEULE : la réaction des recettes au taux de la proposition reste en place,
  // sans quoi ce dépliant lui attribuerait un écart qui n'est pas le sien.
  const sansRetrait = (ligne, scenario) => (
    (ligne.ressourcesDe(scenario) + ligne.retrait) / ligne.depense(scenario)
  );

  return g.depliant("Ce que la branche famille et l'assurance chômage versent", `
<p>Le poste « transferts d'organismes extérieurs » du tableau précédent est un
agrégat. Le voici ventilé par celui qui paie, lu dans les rapports à la
Commission des comptes de la Sécurité sociale, du côté de la caisse qui verse.</p>

${g.tableau(
    ["Ce qui est versé", `En ${premiere}`, `En ${derniere}`,
     `Part des ressources ${derniere}`],
    lignes, ["", "nombre", "nombre", "nombre"],
    `Ce que d'autres caisses versent à la retraite, ${premiere} et ${derniere}`,
    true,
  )}
${g.gloses(POSTES_TRANSFERTS.map((poste) => [poste.libelle, poste.glose]))}
<p class="discret">Les deux caisses expliquent
${g.pourcentage(partVentilee, false, 1)} des ressources de ${derniere}, sur les
${g.pourcentage(partPoste, false, 1)} du poste « transferts » ; le reste est
fait de versements plus petits, de l'assurance maladie et de l'État pour
l'essentiel. Le COR ventile ce poste pour la dernière année de chaque rapport
depuis 2023 : son « dont Unédic » est exactement la somme des deux lignes de
l'assurance chômage, son « dont CNAF » s'écarte de quelques pour cent de ce que
la branche famille déclare verser, consolidé du côté des régimes qui
reçoivent.</p>

<div class="note"><strong>Ces recettes financent des droits que les scénarios
notionnels ne servent pas.</strong> Les systèmes notionnels suppriment l'assurance
vieillesse des parents au foyer et les majorations pour enfants, et ne portent
rien au compte pendant une année de chômage. Ils comptent pourtant, dans les
ressources qu'ils supposent inchangées, les
${milliards(comptes.transfertOrganisme("famille", derniere), 1)} de la branche
famille et les ${milliards(comptes.transfertOrganisme("chomage", derniere), 1)}
de l'assurance chômage de ${derniere} — ${g.pourcentage(supprime, false, 2)}
du PIB, ${g.pourcentage(partSupprimee, false, 1)} des ressources. <strong>Le
coefficient d'équilibre du dépliant suivant les leur retire</strong> : année
par année là où on les connaît, à part constante des ressources avant et
après, jusqu'à l'horizon du COR. Sans ce retrait, la proposition afficherait
${g.nombre(sansRetrait(horizon, "notionnel_liberal"), 2)} en
${solde.derniereAnnee} au lieu de
${g.nombre(horizon.coefficient("notionnel_liberal"), 2)}, et le système 2
${g.nombre(sansRetrait(horizon, "notionnel_retroactif"), 2)} au lieu
de ${g.nombre(horizon.coefficient("notionnel_retroactif"), 2)} ; en
${derniere}, l'écart est du même ordre :
${g.nombre(sansRetrait(ligneSolde, "notionnel_liberal"), 2)} contre
${g.nombre(ligneSolde.coefficient("notionnel_liberal"), 2)}. Ce que la
branche famille cesserait de verser à la retraite ne disparaît pas : il lui
reste, et ce qu'elle en fait est une décision de programme, pas un résultat de
ce modèle.</div>
`, "cout-transferts");
}

/** Les quatre systèmes : ce qu'ils auraient coûté, ce qu'ils coûteraient. */
function coutDetailScenarios(contexte) {
  const c = contexte.cout();
  const avenir = c.avenir;
  const soldeActuel = c.solde;
  const depenses = contexte.depenses();
  const euros = c.anneeEuros;
  const derniere = depenses.derniereAnnee;
  const annees = c.annees.map((ligne) => ligne.annee);
  const bascule = contexte.base.annee_bascule;

  // Un scénario dont la courbe est exactement celle du système actuel serait
  // tracé PAR-DESSUS elle et la ferait disparaître : le graphique montrerait
  // alors une seule courbe en prétendant en montrer trois. On ne trace donc que
  // les scénarios qui s'en écartent, et la légende nomme les autres.
  const confondus = c.confondusAvecActuel();
  const numeros = SCENARIOS_COMPARES.filter(([scenario]) => confondus.includes(scenario))
    .map(([, libelle]) => libelle.split(".")[0]);
  const gloseActuel = numeros.length
    ? `et les scénarios ${numeros.join(" et ")}, qui lui sont confondus`
    : "";
  const courbes = SCENARIOS_COMPARES
    .filter(([scenario]) => !confondus.includes(scenario))
    .map(([scenario, libelle]) => new g.Serie(
      libelle,
      c.annees.map((ligne) => ligne.coutConstants(scenario) / 1000),
      COULEURS_SCENARIOS[scenario],
      scenario === "notionnel_liberal",
      scenario === "actuel" ? gloseActuel : "",
    ));
  const reference = c.cumul("actuel");
  const dernier = c.annee(derniere);
  const lignesPasse = SCENARIOS_COMPARES.map(([scenario, libelle]) => {
    const cumul = c.cumul(scenario);
    return [
      nomScenario(scenario, libelle),
      milliards(cumul, 0),
      scenario !== "actuel"
        ? g.pourcentage(cumul / reference - 1, true, 1)
        : "réf.",
      milliards(dernier.cout(scenario), 1),
      // La part de PIB suit la même règle que le coût : le rapport ne
      // multiplie que les droits directs de la base.
      g.pourcentage(masseDuScenario(dernier.partPib, dernier.partDerives,
                                    dernier.rapports[scenario], scenario,
                                    dernier.reversionServie,
                                    dernier.reformeEnVigueur), false, 1),
    ];
  });
  lignesPasse.push([
    "<em>dont garantie vieillesse du système 4, financée par l'impôt</em>",
    milliards(c.cumul(COMPOSANTE_GARANTIE), 0),
    "—",
    milliards(dernier.cout(COMPOSANTE_GARANTIE), 1),
    g.pourcentage(masseDuScenario(dernier.partPib, dernier.partDerives,
                                  dernier.rapports[COMPOSANTE_GARANTIE],
                                  COMPOSANTE_GARANTIE, dernier.reversionServie),
                  false, 1),
  ]);

  const horizon = avenir.annee(avenir.derniereAnnee);
  const depart = avenir.annee(derniere);
  const referenceAvenir = avenir.cumul("actuel");
  const lignesAvenir = SCENARIOS_COMPARES.map(([scenario, libelle]) => {
    const cumul = avenir.cumul(scenario);
    return [
      nomScenario(scenario, libelle),
      milliards(horizon.coutConstants(scenario), 0),
      g.pourcentage(horizon.partPib(scenario), false, 1),
      milliards(cumul, 0),
      scenario === "actuel" ? "réf."
        : g.pourcentage(cumul / referenceAvenir - 1, true, 1),
      scenario === "actuel" ? "—" : milliards(avenir.ecartCumule(scenario), 0),
    ];
  });
  lignesAvenir.push([
    "<em>dont garantie vieillesse du système 4, financée par l'impôt</em>",
    milliards(horizon.coutConstants(COMPOSANTE_GARANTIE), 0),
    g.pourcentage(horizon.partPib(COMPOSANTE_GARANTIE), false, 1),
    milliards(avenir.cumul(COMPOSANTE_GARANTIE), 0),
    "—",
    "—",
  ]);
  // La garantie est une avance : ce que les successions en rendent vient en
  // moins, et la ligne nette est ce que l'impôt finance pour de bon.
  const reprisesHorizon = horizon.reprisesConstants();
  const reprisesCumul = avenir.cumulReprises();
  lignesAvenir.push([
    "<em>dont reprises sur les successions, au décès des bénéficiaires</em>",
    milliards(reprisesHorizon ? -reprisesHorizon : 0.0, 0),
    g.pourcentage(reprisesHorizon ? -horizon.partPibReprises() : 0.0, false, 1),
    milliards(reprisesCumul ? -reprisesCumul : 0.0, 0),
    "—",
    "—",
  ]);
  lignesAvenir.push([
    "<em>garantie nette des reprises</em>",
    milliards(horizon.garantieNetteConstants(), 0),
    g.pourcentage(horizon.partPib(COMPOSANTE_GARANTIE) - horizon.partPibReprises(),
                  false, 1),
    milliards(avenir.cumul(COMPOSANTE_GARANTIE) - reprisesCumul, 0),
    "—",
    "—",
  ]);

  const horizons = [];
  for (let millesime = 2030; millesime <= avenir.derniereAnnee; millesime += 10) {
    const ligne = avenir.annee(millesime);
    if (!ligne) continue;
    horizons.push([
      String(millesime),
      g.nombre(ligne.dependance, 2),
      g.pourcentage(ligne.partPib("actuel"), false, 1),
      g.pourcentage(ligne.partPib("notionnel_retroactif_employeur"),
        false, 1),
      g.pourcentage(ligne.partPib("notionnel_liberal"), false, 1),
    ]);
  }

  return g.depliant("Les quatre systèmes comparés, du passé jusqu'à 2070", `
<p>La carte du haut ne montre que la proposition. Voici les quatre systèmes que
le site compare, sur le passé puis sur l'avenir. Le
« système actuel » de ces tableaux est la ligne de référence, pas un
équilibre : il manque de
${g.pourcentage(-soldeActuel.annee(soldeActuel.derniereAnneeObservee).solde("actuel"), false, 2)}
du PIB en ${soldeActuel.derniereAnneeObservee}, et de
${g.pourcentage(-soldeActuel.annee(soldeActuel.derniereAnnee).solde("actuel"), false, 2)}
en ${soldeActuel.derniereAnnee} — comparer un scénario à lui, c'est le
comparer à un système qui dérive.</p>

<h4>Ce qu'ils auraient coûté depuis ${c.premiereAnnee}</h4>
<p>La dépense observée n'est pas modélisée : elle est ce qu'elle est. Ce qui est
modélisé, c'est le <strong>rapport</strong> entre ce qui a été versé et ce que
chaque système aurait versé aux mêmes retraités — la moyenne des écarts de
pension, pondérée par le poids de chaque génération dans la masse de l'année.
Les poids sont les effectifs réels de chaque génération, lus dans la pyramide
des âges de l'INSEE ; les écarts viennent des treize cas types croisés avec
${c.generations.length} générations, de ${c.generations[0]} à
${c.generations[c.generations.length - 1]}.</p>

${g.graphique(
    `Coût annuel des quatre systèmes, ${c.premiereAnnee}-${derniere}, `
    + `en milliards d'euros constants de ${euros}`,
    annees, courbes, `Md € ${euros}`)}

${g.tableau(
    ["Système", `Cumul ${c.premiereAnnee}-${derniere}`, "Écart",
      `Coût ${derniere}`, `Part du PIB ${derniere}`],
    lignesPasse,
    ["", "nombre", "nombre", "nombre", "nombre"],
    `Ce que les quatre systèmes auraient coûté de ${c.premiereAnnee} à ${derniere}`,
    true,
  )}


<p>Le système 2 aurait coûté ${milliards(c.cumul("notionnel_retroactif"), 0)}
au lieu de ${milliards(reference, 0)}. Cet écart mesure tout autre chose que l'effet des
comptes notionnels. Il mesure deux choses qui n'ont rien à voir avec eux : ce
scénario ne porte au compte que la <strong>part salariale</strong> de la
cotisation, là où le système 3 y ajoute la part patronale et coûte
${milliards(c.cumul("notionnel_retroactif_employeur"), 0)}, et il applique une
<a href="${g.lien("/methode", "indexation")}">règle d'indexation</a> dont la page
Méthode montre qu'elle domine tout le reste.</p>

<h4>Ce qu'ils coûteraient d'ici ${avenir.derniereAnnee}</h4>
<div class="note vigilance"><strong>Point de vigilance : notre projection
s'écarte de celle du COR.</strong> L'assiette de cette section n'est pas celle
des cartes du haut. Le modèle décrit ici des <strong>pensions de répartition
obligatoire</strong> — ${milliards(depenses.repartition(derniere), 1)} en
${derniere} —, il porte son propre niveau de dépense, et ce niveau s'écarte de
celui du COR : il donne ${g.pourcentage(horizon.partPib("actuel"), false, 1)} du PIB pour le
système actuel en ${avenir.derniereAnnee}, quand le COR en projette
${g.pourcentage(COR_2070, false, 1)}. L'écart est de
${g.nombre((horizon.partPib("actuel") - COR_2070) * 100, 1)} points, et il n'est
pas flatteur : notre ${g.terme("taux de remplacement")} ne recule pas, celui du
COR recule. <a href="${g.DEPOT}/blob/main/docs/limites.md">Le § 5 ter des
limites</a> porte la mesure. C'est pourquoi les cartes
du haut n'utilisent du modèle que son <strong>rapport</strong> entre systèmes,
sans dimension, appliqué aux dépenses du COR.</div>

${g.tableau(
    ["Système", `Coût ${avenir.derniereAnnee}`,
      `Part du PIB ${avenir.derniereAnnee}`,
      `Cumul ${avenir.premiereAnneeProjetee}-${avenir.derniereAnnee}`, "Écart",
      "Dont économie"],
    lignesAvenir,
    ["", "nombre", "nombre", "nombre", "nombre", "nombre"],
    `Ce que chaque système coûterait d'ici ${avenir.derniereAnnee}`,
    true,
  )}
<p class="discret">Le cumul porte sur les seules années projetées, en euros
constants de ${euros}. <strong>Les trois systèmes notionnels comparés ici sont
des contrefactuels</strong> : ils supposent
recalculées les pensions de gens qui les perçoivent depuis trente ans, ce
qu'aucun droit ne permettrait. Ils répondent à « qu'aurait donné cette règle
si elle avait toujours été la nôtre ? », pas à « que se passerait-il si on la
votait demain ? ». Le modèle sait aussi calculer la seconde question — des
variantes où les droits acquis sont conservés et la règle nouvelle ne vaut que
pour la suite —, mais le site ne les compare plus : la proposition du parti est
rétroactive, et c'est elle qu'il s'agit de chiffrer.</p>

<h4>Ce qui pousse la dépense, et ce qui la retient</h4>
${g.tableau(
    ["Horizon", "65 ans et plus par 20-64 ans", "Système actuel",
      "Compte notionnel, les deux parts", "La proposition libérale"],
    horizons,
    ["", "nombre", "nombre", "nombre", "nombre"],
    "Dépendance démographique et part de la dépense dans le PIB, par horizon",
    true,
  )}
<p class="discret">La première colonne est le rapport de dépendance
démographique de l'INSEE : ${g.nombre(depart.dependance, 2)} personne de 65 ans
ou plus par personne de 20 à 64 ans en ${derniere},
${g.nombre(horizon.dependance, 2)} en ${avenir.derniereAnnee}. C'est lui qui
pousse la dépense, et il n'est l'objet d'aucun choix. Ce qui la retient, dans le
système actuel, est l'indexation sur les prix : elle fait décrocher les pensions
des salaires, génération après génération. Les comptes notionnels font la même
chose autrement, par le diviseur d'espérance de vie, mais ils le font
<em>explicitement</em>, et à l'acquisition plutôt qu'au versement.</p>
`, "cout-scenarios");
}

/** Le coefficient d'équilibre : de combien il faudrait rogner, ou pouvoir servir. */
function coutDetailEquilibre(contexte) {
  const c = contexte.cout();
  const solde = c.solde;
  const assiette = contexte.assiette();
  const anneeAssiette = assiette.derniereAnnee;
  const obs = solde.derniereAnneeObservee;
  const observe = solde.annee(obs);
  const horizon = solde.annee(solde.derniereAnnee);
  const lignes = SCENARIOS_COMPARES.map(([scenario, libelle]) => {
    const equilibre = solde.premiereAnneeEquilibree(scenario);
    return [
      nomScenario(scenario, libelle),
      g.pourcentage(observe.solde(scenario), true, 2),
      g.pourcentage(
        solde.soldeMoyen(scenario, solde.premiereAnneeProjetee, solde.derniereAnnee),
        true, 2,
      ),
      g.nombre(observe.coefficient(scenario), 2),
      g.nombre(horizon.coefficient(scenario), 2),
      equilibre ? String(equilibre) : "jamais",
    ];
  });
  return g.depliant(
    "Le coefficient d'équilibre : de combien faudrait-il rogner ?", `
<p>Un système en comptes notionnels se pilote par un seul chiffre : le facteur
par lequel il faut multiplier <em>toutes</em> les pensions pour que l'année
tombe juste. Il vaut un quand le système s'équilibre, moins de un quand il faut
rogner, plus de un quand il pourrait servir davantage.</p>

${g.tableau(
      ["Système", `Solde ${obs}`,
        `Solde moyen ${solde.premiereAnneeProjetee}-${solde.derniereAnnee}`,
        `Coefficient ${obs}`, `Coefficient ${solde.derniereAnnee}`,
        "Équilibre atteint en"],
      lignes,
      ["", "nombre", "nombre", "nombre", "nombre", "nombre"],
      "Solde et coefficient d'équilibre de chaque système, en part du PIB",
      true,
    )}
<p class="discret">Les deux premières colonnes sont en part du PIB. Le
coefficient vaut ${g.nombre(observe.coefficient("actuel"), 2)} pour le système
actuel en ${obs} (il faudrait rogner de

${g.pourcentage(1 - observe.coefficient("actuel"), false, 1)}), et
${g.nombre(horizon.coefficient("actuel"), 2)} en ${solde.derniereAnnee}. La
dernière colonne ne regarde que les années projetées : le passé est ce qu'il a
été. Pour le système actuel, dont le rapport vaut un par construction, ces
colonnes redonnent exactement le solde publié par le COR, ce qui dit que
le raccord ne triche pas. Les trois autres systèmes ne comptent pas tout ce que
le système actuel encaisse : ce que la branche famille et l'assurance chômage
versent pour des droits qu'ils ne servent pas, soit

${g.pourcentage(observe.retrait, false, 2)} du PIB en ${obs}, leur est
retiré, à part constante des ressources sur les années projetées. C'est ce
retrait qui creuse leur solde : un système notionnel qui ne sert plus ces
droits ne peut pas en garder les recettes.</p>

<div class="note"><strong>Dix-huit pour cent de quoi ?</strong> Le système 4
remplace tous les taux de cotisation par un seul, parts salariale et patronale
additionnées, et ce taux s'applique à l'ASSIETTE des revenus d'activité : les
salaires et traitements bruts, plus le revenu mixte des non-salariés, soit
${milliards(assiette.montant(anneeAssiette), 0)} en ${anneeAssiette},
${g.pourcentage(assiette.partPib(anneeAssiette), false, 1)} du PIB. Le
système de retraite y prélève aujourd'hui
${g.pourcentage(horizon.tauxPrelevement, false, 1)} de ressources en tout, et
la proposition en prélèverait 18 : c'est le rapport de ces deux nombres qui fait
sa recette. Elle ne touche aucune compensation d'allègement, n'en accordant
aucun, et cela ne lui retire rien ici : cette compensation passe par la TVA, qui
finance la branche maladie et n'apparaît pas au compte de la retraite.</div>

<div class="note"><strong>L'autre lecture, plus sévère d'un point de
PIB.</strong> Le modèle sait aussi appliquer aux 18 % la DÉPERDITION du système
actuel : les allègements généraux et les assiettes réduites font qu'un taux
légal proche de
${g.pourcentage(0.18 / horizon.rapportsRecettes.notionnel_liberal, false, 0)}
ne rentre pas en entier. Compter ainsi revient à supposer que la proposition
garde la même architecture d'exonérations, ce que son texte ne dit pas. Les deux
lectures se défendent, elles sont toutes deux calculées, et la page a retenu la
première.</div>

<div class="note"><strong>Un coefficient supérieur à un est une marge, et
une marge se sert.</strong> Lire les
${g.nombre(horizon.coefficient("notionnel_liberal"), 2)} de la proposition comme
une économie de ${g.pourcentage(
      1 - 1 / horizon.coefficient("notionnel_liberal"), false, 0)} serait un
contresens : à ces recettes-là, ce système servirait davantage que ce que la
colonne « dépense » lui prête, et autrement réparti entre les carrières. Le
modèle calcule ce facteur ; il ne l'applique jamais, et toutes les courbes de
coût de cette page sont celles d'un système qui ne se pilote pas. L'appliquer changerait toutes les pensions par un même facteur, donc
tous les niveaux de cette page, sans toucher aux écarts entre carrières,
qui sont la seule chose que ce site mesure.</div>
`, "cout-equilibre");
}

/**
 * L'écart de taux de la sensibilité, en fraction : un point de plus, un de
 * moins. Le seul réglage que la section montre, parce que le taux est la
 * seule chose qu'elle LIT au lieu de la calculer.
 */
const ECART_TAUX_DETTE = 0.01;

// Les systèmes que le graphique de la dette publique trace : le droit en
// vigueur et la proposition, ceux entre lesquels la décision se prend. Copie
// de `SYSTEMES_DETTE_PUBLIQUE` dans `web/pages.py`, qui dit pourquoi les deux
// notionnels « à droits constants » n'y sont pas.
const SYSTEMES_DETTE_PUBLIQUE = ["actuel", "notionnel_liberal"];

/**
 * Ce que le déficit accumule : la dette, si rien ne s'ajuste.
 *
 * LE SOLDE DIT LE FLUX, CETTE SECTION DIT LE STOCK : le cumul des soldes
 * projetés, avec intérêts, rapporté à un PIB qui grandit — la récurrence de
 * toute dette publique. Elle part de zéro à la dernière année observée ; un
 * stock négatif est une réserve, et le graphique descend sous l'axe pour le
 * montrer. Le taux est le forward à un an de la courbe sans risque, celui du
 * pilier capitalisé. Copie de `_cout_detail_dette` dans `web/pages.py`.
 */
/**
 * Les lignes du tableau poste par poste, dans l'ordre du tableau 2.2 du
 * rapport annuel du COR, puis les dépenses en face. Chaque ligne porte son
 * code dans `postesRessources` ou `postesDepenses`, son libellé et son rang :
 * `poste` s'ajoute au total, `dont` ventile la ligne du dessus.
 */
const LIGNES_RECETTES = [
  ["cotisations", "Cotisations sociales", "poste"],
  ["contribution_equilibre_etat", "Contribution d'équilibre de l'État", "poste"],
  ["subventions_equilibre", "Subventions d'équilibre aux régimes spéciaux", "poste"],
  ["impots_et_taxes", "Impôts et taxes affectés, dont CSG", "poste"],
  ["impots_solidarite", "Dont fonds de solidarité vieillesse", "dont"],
  ["transferts", "Transferts d'organismes extérieurs", "poste"],
  ["transferts_famille", "Dont branche famille", "dont"],
  ["transferts_chomage", "Dont assurance chômage", "dont"],
  ["transferts_autres", "Dont autres transferts", "dont"],
  ["autres_produits", "Autres produits", "poste"],
];
const LIGNES_DEPENSES = [
  ["droits_directs", "Pensions de droit direct", "poste"],
  ["droits_derives", "Pensions de réversion (droit dérivé)", "poste"],
];

/** « 4. La proposition libérale » → « La proposition libérale ». */
function sansNumero(libelle) {
  const coupe = libelle.indexOf(". ");
  return coupe >= 0 ? libelle.slice(coupe + 2) : libelle;
}

/**
 * Recettes et dépenses poste par poste, le système actuel et la proposition :
 * le tableau 2.2 du rapport annuel du COR refait pour deux systèmes, la même
 * année, avec les dépenses en face et le solde en bas. `ressourcesDe` et
 * `depense` y sont écrits ligne à ligne, et les lignes somment au total.
 * L'année est celle de la bascule ; le PIB n'y est pas publié, et les
 * milliards sont ceux d'un point de PIB de la dernière année publiée.
 */
function coutDetailPostes(contexte) {
  const comptes = contexte.comptes();
  const c = contexte.cout();
  const solde = c.solde;
  const base = contexte.base;
  const annee = Math.min(Math.max(base.annee_bascule, solde.premiereAnnee),
                         solde.derniereAnnee);
  const ligne = solde.annee(annee);
  const anneePib = comptes.pib.derniereAnnee;
  const pib = comptes.pib.valeur(anneePib);
  const derniereVentilee = comptes.anneesVentilees().at(-1);
  const systemes = ["actuel", "notionnel_liberal"];
  const recettes = Object.fromEntries(systemes.map((s) => [s, ligne.postesRessources(s)]));
  const depenses_ = Object.fromEntries(systemes.map((s) => [s, ligne.postesDepenses(s)]));
  const totalRecettes = Object.fromEntries(systemes.map((s) => [s, ligne.ressourcesDe(s)]));
  const totalDepenses = Object.fromEntries(systemes.map((s) => [s, ligne.depense(s)]));

  // La garantie vieillesse, lue sur la vraie distribution des pensions comme
  // le fait le dépliant qui lui est consacré — plancher de base, pensions de
  // la proposition : la lecture la plus basse des deux qu'il donne.
  const distribution = contexte.distribution();
  const simulateur = contexte.simulateur();
  const versEnquete = simulateur.macro.coefficientPrix(
    base.annee_euros_garantie_vieillesse, distribution.millesime,
  );
  // Le facteur est celui de la trajectoire : la pension moyenne que la garantie
  // regarde, sur celle du système actuel l'année de l'enquête — le même que le
  // dépliant de la garantie (voir `GarantieDistribution` dans cout.js).
  const anneeEnquete = c.annee(distribution.millesime);
  const facteurContributif = anneeEnquete && anneeEnquete.garantie
    ? anneeEnquete.garantie.facteur : 1.0;
  const garantie = coutGarantie(
    distribution,
    simulateur.effectifs.effectif("tous_regimes", distribution.millesime),
    base.garantie_vieillesse_mensuelle * versEnquete, facteurContributif,
  );
  // Un ayant droit sur deux réclame : le même recours que le dépliant.
  const garantieMeur = garantie.coutAnnuelMeur * base.taux_recours_garantie / versEnquete;
  // Le pilier capitalisé : 5 % de la même assiette que les 18 %.
  const capitalise = ligne.recetteParAssiette
    ? recettes.notionnel_liberal.cotisations
      * base.taux_capitalisation_obligatoire / base.taux_cotisation_liberal
    : 0.0;

  // Milliards, part de PIB, part du total — ou trois tirets.
  const cellules = (valeur, total, absent = false) => {
    if (absent) return ["—", "—", "—"];
    return [
      milliards(valeur * pib, 1),
      g.pourcentage(valeur, false, 2),
      total ? g.pourcentage(valeur / total, false, 1) : "—",
    ];
  };
  const rangee = (libelle, rang, valeurs, totaux) => {
    let texte;
    if (rang === "total") texte = `<strong>${echapper(libelle)}</strong>`;
    else if (rang === "dont") texte = `<span class="dont">${echapper(libelle)}</span>`;
    else texte = echapper(libelle);
    const cellules_ = [texte];
    for (const s of systemes) {
      // Un poste que la proposition ne reconduit pas se lit comme absent, et
      // non comme un zéro : la note dit pourquoi il est parti.
      cellules_.push(...cellules(valeurs[s], totaux[s],
                                 rang !== "total" && valeurs[s] === 0.0));
    }
    return cellules_;
  };

  const lignes = [];
  for (const [code, libelle, rang] of LIGNES_RECETTES) {
    lignes.push(rangee(libelle, rang,
      Object.fromEntries(systemes.map((s) => [s, recettes[s][code]])), totalRecettes));
  }
  lignes.push(rangee("Total des ressources", "total", totalRecettes, totalRecettes));
  for (const [code, libelle, rang] of LIGNES_DEPENSES) {
    lignes.push(rangee(libelle, rang,
      Object.fromEntries(systemes.map((s) => [s, depenses_[s][code]])), totalDepenses));
  }
  lignes.push(rangee("Total des dépenses", "total", totalDepenses, totalDepenses));
  lignes.push(["<strong>Solde</strong>", ...systemes.flatMap((s) => [
    milliards(ligne.solde(s) * pib, 1),
    g.pourcentage(ligne.solde(s), true, 2), "—",
  ])]);
  lignes.push([
    '<span class="dont">Pour mémoire, hors du compte : garantie vieillesse, '
    + "financée par l'impôt</span>", "—", "—", "—",
    milliards(garantieMeur, 1),
    g.pourcentage(garantieMeur / pib, false, 2), "—",
  ]);
  lignes.push([
    '<span class="dont">Pour mémoire, hors du système : pilier capitalisé '
    + "obligatoire</span>", "—", "—", "—",
    ...(capitalise ? cellules(capitalise, 0.0) : ["—", "—", "—"]),
  ]);

  return g.depliant(
    "Recettes et dépenses, poste par poste", `
<p>Le Conseil d'orientation des retraites publie chaque année la structure des
ressources du système de retraite : sept lignes, en milliards d'euros et en
pourcentage du total. Voici le même tableau pour le système actuel et pour la
proposition, en ${annee}, l'année de la bascule, avec les dépenses en face et le
solde en bas. Chaque ligne applique à son poste la règle que le bilan du haut
applique au total : les lignes somment aux totaux, et les totaux sont ceux des
courbes.</p>

${g.tableau(
      ["Poste", `${sansNumero(LIBELLES_SYSTEMES.actuel)}, Md €`, "% du PIB", "Part",
        `${sansNumero(LIBELLES_SYSTEMES.notionnel_liberal)}, Md €`, "% du PIB", "Part"],
      lignes,
      ["", "nombre", "nombre", "nombre", "nombre", "nombre", "nombre"],
      `Ressources et dépenses du système de retraite en ${annee}, système `
      + "actuel et proposition, en milliards d'euros et en part du PIB",
      true,
    )}

<p class="discret">Les parts de PIB sont celles du compte du COR pour ${annee},
année projetée. Le PIB de ${annee} n'est pas publié : les milliards sont ceux
d'un point de PIB de ${anneePib}, dernière année connue
(${milliards(pib, 0)}), et donnent l'ordre de grandeur, pas la valeur de
${annee}. La structure des ressources du système actuel est celle de
${derniereVentilee}, dernière année que le COR ventile, reconduite ; les
« dont » sont ce que chaque payeur a réellement versé la dernière année connue,
à part constante des ressources. « Part » rapporte chaque ligne au total des
ressources, ou des dépenses, de son système. Un tiret est un poste que le
système ne compte pas.</p>

<div class="note"><strong>Ce que la proposition change, ligne à ligne.</strong>
Les cotisations deviennent
${g.pourcentage(base.taux_cotisation_liberal, false, 0)} de l'assiette des
revenus d'activité, parts salariale et patronale additionnées, pour tous les
statuts. Trois postes disparaissent : la contribution d'équilibre de l'État,
remplacée par ces ${g.pourcentage(base.taux_cotisation_liberal, false, 0)}
appliqués aux traitements des fonctionnaires ; les subventions d'équilibre,
dont la fusion des régimes supprime l'objet ; les impôts et taxes affectés, qui
n'acquièrent de droits à personne. Des transferts, seule reste la part qui ne
paie pas un droit supprimé : la branche famille et l'assurance chômage
financent des droits que le compte notionnel ne sert plus. Côté dépenses, les
pensions sont recalculées au franc le franc des cotisations, et la réversion
n'est plus servie, ce que la dernière note détaille. La garantie vieillesse qui remplace l'ASPA est financée par l'impôt,
hors du compte des cotisants ; le dépliant qui lui est consacré en donne
quatre lectures, et la ligne pour mémoire porte la plus basse. Le pilier
capitalisé ne passe pas par les caisses et n'est ni une ressource ni une
dépense du système : il est rappelé pour que rien ne manque.</div>

<div class="note"><strong>La recette réagit sur trois points, et sur trois
seulement.</strong> Elle suit le droit : ce que la branche famille, l'assurance
chômage et le fonds de solidarité vieillesse versent pour des droits que les
systèmes notionnels ne servent pas leur est retiré, un peu plus d'un point de
PIB. Elle suit le taux : le système 4 prélève ses ${g.pourcentage(base.taux_cotisation_liberal, false, 0)} sur
l'assiette mesurée des revenus d'activité au lieu de la part cotisée des
ressources d'aujourd'hui. Elle suit enfin le principe, et pour le seul
système 4 : un compte notionnel ne crédite que ce qui est assis sur un revenu
d'activité, et ce système ne reconduit donc aucune des trois ressources qui
n'acquièrent de droits à personne, celles que la note du dessus nomme. Trois
postes : 27 % des ressources en 2024, 29 % en 2070. Les cinq autres systèmes
les encaissent tous, faute qu'aucun programme dise ce qu'il en ferait.</div>

<div class="note"><strong>Seul le système actuel sert la pension de
réversion.</strong> Une réversion est ce qu'un conjoint survivant reçoit de la
carrière d'un autre : la première dépense non contributive du système, un
dixième environ de tout ce qui est versé. Les systèmes notionnels comparés ici
retirent tous les avantages non contributifs, et celui-là comme les autres :
ils ne rendent que ce qui a été cotisé, et c'est précisément ce qu'ils servent
à mesurer. Le système actuel, lui, la sert, puisqu'il est le droit en vigueur.
Les systèmes qui ne valent que pour l'avenir la servent jusqu'à leur bascule,
n'étant jusque-là rien d'autre que le système actuel. Ensuite ils ne la
servent plus, aux veuves d'avant comme à celles d'après.</div>
`, "cout-postes");
}


function coutDetailDette(contexte) {
  const c = contexte.cout();
  const dette = c.dette;
  if (!dette.annees.length) return "";
  const solde = c.solde;
  const avenir = c.avenir;
  const courbe = contexte.simulateur().courbeTaux;
  const depart = dette.anneeDepart;
  const fin = dette.derniereAnnee;
  const moins = calculerDette(solde, avenir, courbe, -ECART_TAUX_DETTE);
  const plus = calculerDette(solde, avenir, courbe, ECART_TAUX_DETTE);
  const annees = [];
  for (let annee = depart; annee <= fin; annee += 1) annees.push(annee);
  const series = SCENARIOS_COMPARES.map(([scenario, libelle]) => new g.Serie(
    libelle,
    annees.map((annee) => dette.stock(scenario, annee) * 100),
    COULEURS_SCENARIOS[scenario],
    scenario === "notionnel_liberal",
  ));
  const trace = g.graphique(
    `Ce que le solde de chaque système accumule de ${depart} à ${fin}, `
    + "en part du PIB — une dette au-dessus de l'axe, une réserve en dessous",
    annees, series, "% du PIB", false, 0, true, null, "",
    SCENARIOS_COMPARES.map(([, libelle]) => libelle.split(".")[0]),
    "Année", null, "", 1,
  );
  const derniere = dette.annees[dette.annees.length - 1];
  const lignes = SCENARIOS_COMPARES.map(([scenario, libelle]) => [
    nomScenario(scenario, libelle),
    g.pourcentage(dette.horizon(scenario), true, 0),
    g.pourcentage(derniere.interet(scenario), true, 1),
    g.pourcentage(moins.horizon(scenario), true, 0),
    g.pourcentage(plus.horizon(scenario), true, 0),
  ]);
  const premiere = dette.annees[0];
  const cotee = dette.annee(dette.derniereAnneeCotee) || derniere;
  const publique = coutDettePublique(dette, fin);
  return g.depliant(
    "Ce que le déficit accumule : la dette, si rien ne s'ajuste", `
<p>Un solde est un flux : ce qui manque une année, ou ce qui reste. Un déficit
qui se répète devient un <strong>stock</strong>, et un stock porte intérêt.
Cette section cumule, à compter de ${depart}, le solde de chaque système :
chaque année, ce qui manque est emprunté et ce qui reste est placé, au taux à
un an que la courbe des taux sans risque de la zone euro cote pour cette
année-là ; le stock est rapporté au PIB, qui grandit au rythme de la
projection. Il part de zéro. Ni la dette ni les réserves que le système porte
aujourd'hui n'y sont : la courbe dit ce que les soldes à venir ajoutent, jamais
ce que le système détient.</p>

${trace}

<p><strong>Les déficits du système actuel, simplement additionnés de
${premiere.annee} à ${fin}, font
${g.pourcentage(dette.cumulSoldes("actuel"), false, 0)} du PIB.</strong>
Avec les intérêts, et une fois le tout rapporté à un PIB qui grandit, la dette
atteint ${g.pourcentage(dette.horizon("actuel"), false, 0)} du PIB en ${fin},
et ses seuls intérêts coûtent cette année-là
${g.pourcentage(derniere.interet("actuel"), false, 1)} du PIB. Elle
s'ajouterait à celle que le pays porte déjà, que le second graphique pose
dessous. La proposition, qui fixe le taux à 18 % et ne fixe pas les pensions,
en accumule ${g.pourcentage(dette.horizon("notionnel_liberal"), false, 0)} du
PIB au même horizon.</p>

${g.tableau(
    ["Système", `Dette en ${fin}`, `Intérêts de l'année ${fin}`,
      "Taux un point plus bas", "Taux un point plus haut"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
    `Stock accumulé par chaque système en ${fin}, en part du PIB, `
    + "et ce qu'un point de taux y change",
    true,
  )}
<p class="discret">Tout est en part du PIB. Un chiffre négatif est une
réserve : le système a encaissé plus qu'il n'a servi, et le stock lui rapporte
au lieu de lui coûter. Les deux dernières colonnes refont le calcul avec un
taux plus bas, puis plus haut, d'un point sur toute la période.</p>

<div class="note"><strong>Un système notionnel n'accumule ni cette dette ni
cette réserve.</strong> Il se règle chaque année par le coefficient
d'équilibre, que la section précédente calcule et que cette page n'applique
jamais. La courbe d'un système qui plonge sous l'axe mesure la marge que ce
coefficient aurait à distribuer, celle d'un système qui monte mesure ce qu'il
faudrait rogner, ou financer autrement. Le système actuel, lui, ne se règle
pas : il attend une réforme, et la courbe dit ce que coûte l'attente.</div>
${publique}
<div class="note"><strong>Le taux est lu, pas choisi.</strong> C'est le taux à
un an que la courbe des souverains les mieux notés de la zone euro, publiée par
la Banque centrale européenne le ${dateEnClair(dette.dateCourbe)}, implique pour
chaque année : ${g.pourcentage(premiere.taux, false, 1)} en
${premiere.annee}, ${g.pourcentage(cotee.taux, false, 1)} en ${cotee.annee}, la
dernière année que la courbe cote ; au-delà, il est prolongé à plat. C'est la
même courbe qui fait le rendement du pilier capitalisé du système 4 : la dette
et le pilier lisent le même marché, et personne n'a eu à prévoir un taux. Un
point de plus ou de moins déplace la dette du système actuel en ${fin} de
${g.pourcentage(moins.horizon("actuel"), false, 0)} à
${g.pourcentage(plus.horizon("actuel"), false, 0)} du PIB.</div>
`,
    "cout-dette",
  );
}

/**
 * La dette du pays, et ce que chaque système y ajoute : l'échelle du stock.
 * Copie de `_cout_dette_publique` dans `web/pages.py`.
 */
function coutDettePublique(dette, fin) {
  const observee = dette.dettePubliqueObservee;
  const anneesObservees = Object.keys(observee).map(Number);
  if (!anneesObservees.length) return "";
  const depart = dette.anneeDepart;
  const anneeDette = dette.anneeDettePublique;
  const premiereObservee = Math.min(...anneesObservees);
  const annees = [];
  for (let annee = premiereObservee; annee <= fin; annee += 1) annees.push(annee);
  const courbes = [new g.Serie(
    "Dette publique observée, toutes administrations",
    annees.map((annee) => (annee in observee ? observee[annee] * 100 : null)),
    "var(--serie-1)",
    false,
    "INSEE, au sens de Maastricht",
  )];
  for (const scenario of SYSTEMES_DETTE_PUBLIQUE) {
    courbes.push(new g.Serie(
      LIBELLES_SYSTEMES[scenario],
      annees.map((annee) => (
        annee >= depart ? dette.dettePublique(scenario, annee) * 100 : null
      )),
      COULEURS_SCENARIOS[scenario],
      scenario === "notionnel_liberal",
      "la dette tenue à plat, plus le stock du système",
    ));
  }
  const trace = g.graphique(
    `La dette publique de ${premiereObservee} à ${anneeDette}, puis ce `
    + `que le système actuel et la proposition y ajoutent jusqu'en ${fin}, `
    + "en part du PIB",
    annees, courbes, "% du PIB", false, 0, true, depart, "projection",
    ["", ...SYSTEMES_DETTE_PUBLIQUE.map(
      (scenario) => LIBELLES_SYSTEMES[scenario].split(".")[0],
    )],
    "Année", null, "", 0,
  );
  const actuel = dette.dettePublique("actuel", fin);
  const proposition = dette.dettePublique("notionnel_liberal", fin);
  const ecart = proposition - actuel;
  let lecture;
  if (Math.abs(ecart) < 0.005) {
    lecture = "la proposition et le système actuel laissent le pays au même point";
  } else if (ecart > 0) {
    lecture = `la proposition laisse le pays ${g.pourcentage(ecart, false, 0)} `
      + "du PIB plus endetté que le système actuel";
  } else {
    lecture = `la proposition laisse le pays ${g.pourcentage(-ecart, false, 0)} `
      + "du PIB moins endetté que le système actuel";
  }
  return `
<p>Ce stock ne part pas de rien : le pays porte déjà une dette. Le graphique
suivant la pose dessous. D'abord la dette des administrations publiques au
sens de Maastricht (État, collectivités, Sécurité sociale), telle que
l'INSEE la publie de ${premiereObservee} à ${anneeDette} ; puis, à compter de
${depart}, cette dette tenue à son niveau de ${anneeDette} en part du PIB, à
laquelle chaque système ajoute son seul stock, tel que le graphique du dessus
le cumule. C'est l'échelle qui manquait : ce que le système de retraite
ajoute se lit à côté de ce que le pays doit déjà.</p>

${trace}

<p><strong>La dette publique faisait
${g.pourcentage(dette.dettePubliqueDepart, false, 0)} du PIB fin
${anneeDette}.</strong> Si rien d'autre ne bougeait, le système actuel la
porterait à ${g.pourcentage(actuel, false, 0)} du PIB en ${fin}, et la
proposition à ${g.pourcentage(proposition, false, 0)} : ${lecture}. L'écart
entre les deux courbes est exactement l'écart entre les deux stocks du
graphique précédent, et c'est lui qui se lit ici, à l'échelle du pays.</p>

<div class="note"><strong>Ce n'est pas une prévision de la dette
publique.</strong> Le reste des administrations publiques (l'État hors
retraite, les collectivités, l'assurance maladie) a son propre solde, que ce
site ne modélise pas. La dette est donc tenue à plat, en part du PIB, à son
niveau de ${anneeDette}, et seule la retraite la déplace. Une dette qui
monterait, ou baisserait, pour d'autres raisons décalerait les deux courbes
d'un même bloc sans changer leur écart. Les systèmes 2 et 3 ne sont pas
tracés : leur réserve, posée sous cette dette, dessinerait un pays qui l'a
remboursée plusieurs fois, ce qu'aucun système notionnel ne ferait puisque le
coefficient d'équilibre rend cette marge aux pensions ; et son échelle
écraserait l'écart qui compte. Leur stock est dans le tableau.</div>
`;
}

/**
 * La frise des flux : chaque année, ce qui rentre, ce qui sort, ce qui reste.
 * Une colonne par année et par système, un système à la fois par les onglets
 * des grilles de Cas types. Copie de `_cout_detail_frise` dans `web/pages.py`.
 */
function coutDetailFrise(contexte) {
  const c = contexte.cout();
  const dette = c.dette;
  if (!dette.annees.length) return "";
  const solde = c.solde;
  const depart = dette.anneeDepart;
  const fin = dette.derniereAnnee;

  const frise = (scenario, libelle) => {
    const lignes = [];
    let precedent = 0.0;
    for (const ligne of dette.annees) {
      const bilan = solde.annee(ligne.annee);
      lignes.push(new g.AnneeFrise(
        ligne.annee,
        bilan.ressourcesDe(scenario) * 100,
        bilan.depense(scenario) * 100,
        ligne.interet(scenario) * 100,
        precedent / (1.0 + ligne.croissance) * 100,
        ligne.stock(scenario) * 100,
        ligne.croissance,
      ));
      precedent = ligne.stock(scenario);
    }
    return g.friseFlux(
      "Ce qui rentre, ce qui sort et ce qui s'accumule chaque année de "
      + `${dette.premiereAnnee} à ${fin}, ${libelle}`,
      lignes,
    );
  };

  const court = (libelle) => libelle.split(". ").slice(1).join(". ");
  const onglets = SCENARIOS_COMPARES.map(([scenario, libelle], rang) => (
    `<input type="radio" name="grille" id="grille-${scenario}"`
    + (rang === 0 ? " checked" : "")
    + `><label for="grille-${scenario}">${echapper(court(libelle))}</label>`
  )).join("");
  const panneaux = SCENARIOS_COMPARES.map(([scenario, libelle], rang) => (
    `<div class="panneau" data-onglet="${scenario}"`
    + (rang === 0 ? "" : " hidden") + ">"
    + `<h3>${echapper(libelle)} ${badgeScenario(scenario)}</h3>`
    + frise(scenario, court(libelle).toLowerCase()) + "</div>"
  )).join("");
  return g.depliant(
    "La frise des flux : chaque année, ce qui rentre, ce qui sort, ce qui reste", `
<p>La courbe de la section précédente se lit ici colonne par colonne, une par
année, comme un registre. À gauche <strong>ce qui rentre</strong> dans la
caisse, à droite <strong>ce qui sort</strong>, au milieu la caisse elle-même,
aussi haute que le plus grand des deux : son pied est rouge quand il manque de
l'argent, et cet argent est emprunté ; vert quand il en reste, et cet argent
est placé. Dessous, en chiffres, le stock : ce qu'il était au 1er janvier,
les intérêts de l'année, l'emprunt ou le placement, et ce qu'il est au 31
décembre. Chaque colonne tombe juste : le 31 décembre d'une année, rapporté au
PIB de la suivante, est son 1er janvier.</p>
<p class="discret">Tout est en part du PIB de l'année, comme sur la courbe. Le
stock n'est pas dessiné à l'échelle des flux, dont il vaut jusqu'à cinquante
fois la hauteur : il est écrit. Un stock négatif est une réserve, et ses intérêts lui
rapportent au lieu de lui coûter. La frise défile de ${depart + 1} à ${fin} ;
ses chiffres sont redits, ligne par ligne, dans le tableau replié dessous.</p>
<fieldset class="onglets"><legend>Système affiché</legend>${onglets}</fieldset>
<div class="panneaux">${panneaux}</div>
`,
    "cout-frise",
  );
}

/** Ce que la garantie vieillesse coûterait, lue sur la vraie distribution. */
function coutDetailGarantie(contexte) {
  const c = contexte.cout();
  const distribution = contexte.distribution();
  const simulateur = contexte.simulateur();
  const base = contexte.base;
  const millesime = distribution.millesime;
  const effectifRetraites = simulateur.effectifs.effectif("tous_regimes", millesime);
  const versEnquete = simulateur.macro.coefficientPrix(
    base.annee_euros_garantie_vieillesse, millesime,
  );
  const anneeEnquete = c.annee(millesime);
  const facteur = anneeEnquete && anneeEnquete.garantie ? anneeEnquete.garantie.facteur : 1.0;
  const taux = base.taux_recours_garantie;
  const seul = base.situation_foyer === "seul";
  const planchers = [
    ["Plancher de base, 800 € (vie à deux)", base.garantie_vieillesse_mensuelle],
    ["Plancher majoré, 1 050 € (personne seule)",
      base.garantie_vieillesse_mensuelle + base.allocation_isolement_mensuelle],
  ];
  const assiettes = [
    [`Pensions de ${millesime}`, 1.0],
    [`Pensions du système 4 en ${millesime}`, facteur],
  ];
  const lignes = [];
  for (const [titreAssiette, facteurAssiette] of assiettes) {
    for (const [titrePlancher, mensuel] of planchers) {
      const chiffre = coutGarantie(
        distribution, effectifRetraites, mensuel * versEnquete, facteurAssiette,
      );
      lignes.push([
        echapper(`${titreAssiette} — ${titrePlancher}`),
        g.pourcentage(chiffre.partBeneficiaires, false, 1),
        `${g.nombre(chiffre.beneficiaires * taux / 1e6, 1)} M`,
        g.euros(chiffre.complementMoyenMensuel / versEnquete),
        milliards(chiffre.coutAnnuelMeur * taux / versEnquete, 1),
      ]);
    }
  }
  const garantieBasse = coutGarantie(
    distribution, effectifRetraites,
    base.garantie_vieillesse_mensuelle * versEnquete, 1.0,
  );
  const garantieScenario = coutGarantie(
    distribution, effectifRetraites,
    base.garantie_vieillesse_mensuelle * versEnquete, facteur,
  );

  // La trajectoire, à quelques dates : ce que la ligne « dont garantie » des
  // tableaux du haut contient, et pourquoi elle décroît.
  const derniere = contexte.depenses().derniereAnnee;
  const etapes = [];
  for (const millesimeEtape of [millesime, derniere, 2030, 2050, c.avenir.derniereAnnee]) {
    const ligne = c.avenir.annee(millesimeEtape);
    if (ligne === null || !ligne.garantie || etapes.some(([a]) => a === millesimeEtape)) {
      continue;
    }
    etapes.push([millesimeEtape, ligne]);
  }
  const lignesEtapes = etapes.map(([annee, ligne]) => [
    String(annee),
    g.nombre(ligne.garantie.facteur, 2),
    `${g.nombre(ligne.garantie.effectif / 1e6, 1)} M`,
    `${g.nombre(ligne.garantie.ayantsDroit / 1e6, 1)} M`,
    `${g.nombre(ligne.garantie.beneficiaires / 1e6, 1)} M`,
    milliards(ligne.coutConstants(COMPOSANTE_GARANTIE), 1),
    g.pourcentage(ligne.partPib(COMPOSANTE_GARANTIE), false, 2),
  ]);

  // La reprise sur succession, année par année : les avances que la garantie
  // constitue à compter de la bascule, ce que les décès libèrent, ce que les
  // successions rendent, et ce qui reste à l'impôt.
  const etapesReprises = [];
  for (const millesimeEtape of [base.annee_bascule, 2030, 2040, 2050, 2060,
    c.avenir.derniereAnnee]) {
    const ligne = c.avenir.annee(millesimeEtape);
    if (ligne === null || !ligne.garantie || millesimeEtape < base.annee_bascule
        || etapesReprises.some(([a]) => a === millesimeEtape)) {
      continue;
    }
    etapesReprises.push([millesimeEtape, ligne]);
  }
  const lignesReprises = etapesReprises.map(([annee, ligne]) => [
    String(annee),
    milliards(ligne.coutConstants(COMPOSANTE_GARANTIE), 1),
    milliards(ligne.garantie.avancesLibereesConstants, 1),
    milliards(ligne.reprisesConstants(), 1),
    milliards(ligne.garantieNetteConstants(), 1),
    g.pourcentage(ligne.partPib(COMPOSANTE_GARANTIE) - ligne.partPibReprises(),
                  false, 2),
    milliards(ligne.garantie.stockAvancesConstants, 0),
  ]);
  // La part que la succession couvre, telle que la trajectoire l'a retenue :
  // calculée sur le patrimoine des retraités, ou réglée.
  const ligneBascule = c.avenir.annee(base.annee_bascule);
  const garantieBascule = ligneBascule !== null ? ligneBascule.garantie : null;
  const partReprise = garantieBascule ? garantieBascule.partReprise : 0.0;
  const dureeAvances = garantieBascule ? garantieBascule.dureeAvances : 0.0;
  const repriseCalculee = base.part_reprise_garantie === null
    || base.part_reprise_garantie === undefined;
  const patrimoine = simulateur.patrimoine;
  const modestes = patrimoine.statistiques("retraites_q1");
  const retraites = patrimoine.statistiques("retraites");

  // Ce que la garantie remplace : les trois minima, tels qu'ils coûtent la
  // dernière année observée. Le minimum garanti de la fonction publique n'y
  // est pas : il est payé par les régimes de la fonction publique, dans la
  // dépense que la trajectoire remplace, pas par un transfert de l'impôt.
  const avantages = contexte.avantages().derniere;
  const montants = avantages ? avantages.lignes : {};
  const anneeMinima = avantages ? avantages.annee : derniere;
  const remplaces = [
    ["Minimum vieillesse (ASPA)", "minimum_vieillesse", "lu dans les comptes"],
    ["Minimum contributif", "minimum_contributif", "calculé sur la grille"],
    ["Pension majorée de référence des exploitants", "pension_majoree_reference",
      "non chiffrée"],
  ];
  let totalRemplace = 0;
  for (const [, code] of remplaces) totalRemplace += montants[code] || 0;
  const lignesRemplaces = remplaces.map(([libelle, code, source]) => [
    libelle, source, montants[code] ? milliards(montants[code], 2) : "—",
  ]);
  const garantieBrute = c.annee(anneeMinima).cout(COMPOSANTE_GARANTIE);
  lignesRemplaces.push(["<strong>Ce que ces trois minima coûtent</strong>", "",
    `<strong>${milliards(totalRemplace, 1)}</strong>`]);
  lignesRemplaces.push([`Garantie vieillesse, aux pensions du système 4 en ${anneeMinima}`,
    "distribution, ci-dessus", milliards(garantieBrute, 1)]);
  lignesRemplaces.push(["<strong>Ce que l'impôt paierait en plus</strong>", "",
    `<strong>${milliards(garantieBrute - totalRemplace, 1)}</strong>`]);

  return g.depliant("Ce que coûte la garantie vieillesse", `
<p>La garantie du système 4 est <strong>différentielle</strong> : elle ne verse
que ce qui manque à une pension pour atteindre son plancher. Son coût est donc
tout entier celui de la <strong>queue basse de la distribution</strong> des
pensions, et treize carrières de référence ne décrivent pas une distribution.
La ligne « dont garantie vieillesse » des deux tableaux du haut n'est donc pas
tirée des cas types : elle est lue sur la distribution que l'échantillon
interrégimes de retraités de la DREES publie, par tranches de cent euros, pour
${millesime}. Les cas types ne servent qu'à dire <em>de combien cette
distribution bouge</em> d'une année à l'autre : la pension moyenne que la
garantie regarde (le compte notionnel plus la rente du pilier capitalisé, à
partir de 65 ans), rapportée à la pension moyenne du système actuel en
${millesime}. Ce facteur vaut ${g.nombre(facteur, 2)} en ${millesime} : les
pensions du système 4 y sont plus basses que celles servies, parce que le
compte rétroactif ne rend que ce qui a été cotisé. Il monte ensuite avec les
salaires, face à un plancher indexé sur les prix, et la garantie décroît.</p>

${g.tableau(
    ["Année", "Facteur de déplacement", "Retraités de 65 ans et plus",
      "Sous le plancher", "Bénéficiaires",
      `Coût annuel, milliards d'euros ${c.anneeEuros}`,
      "Part du PIB"],
    lignesEtapes,
    ["nombre", "nombre", "nombre", "nombre", "nombre", "nombre", "nombre"],
    `La garantie vieillesse dans la trajectoire, plancher ${
      seul ? "majoré (personne seule)" : "de base (vie à deux)"}`,
    true,
  )}

<p><strong>Ce que les successions rendent.</strong> La garantie est une
avance : chaque euro versé depuis la bascule porte intérêt au taux réel que la
courbe des taux sans risque implique, une fois l'inflation retirée, et devient
une créance sur la succession. Le modèle suit ces avances par âge et les
libère au décès, avec la mortalité du vingtile de niveau de vie où la pension
moyenne des bénéficiaires les place : une avance dure ${g.nombre(dureeAvances, 1)} ans en moyenne.
La succession en couvre ${g.pourcentage(partReprise, false, 0)}, ${repriseCalculee ? "calculés sur le patrimoine des ménages retraités selon leur revenu" : "le réglage « Part de l'avance couverte par la succession »"}. Ce que la succession ne couvre pas
est abandonné : c'est cette part-là, et elle seule, que l'impôt finance pour
de bon. Les lignes « dont reprises » et « garantie nette » des tableaux du
haut en viennent.</p>

<p class="discret">Le patrimoine des retraités selon leur pension n'est publié
nulle part. Le COR a publié, sur l'enquête Histoire de vie et Patrimoine 2018,
le patrimoine brut des ménages retraités selon leur revenu disponible : une
médiane de ${g.euros(modestes.mediane)} pour le quart le plus modeste, de ${g.euros(retraites.mediane)} pour
l'ensemble. Chaque tranche de pension sous le plancher reçoit l'avance qu'elle
constituerait, et la part que la succession en couvre est celle du quart le
plus modeste pour le premier quart des retraités, celle de l'ensemble à partir
de la médiane, et le mélange entre les deux ; la part retenue est la moyenne,
pesée par les avances. Un couple de deux bénéficiaires pèse deux avances sur
une succession, ce que ce calcul ne voit pas ; il surestime donc la
couverture. Le réglage « Part de l'avance couverte par la succession »
remplace ce calcul par un nombre.</p>

${g.tableau(
    ["Année", "Versé", "Avances libérées par les décès", "Reprises",
      "Garantie nette", "Net en part du PIB", "Avances en cours"],
    lignesReprises,
    ["nombre", "nombre", "nombre", "nombre", "nombre", "nombre", "nombre"],
    `La reprise sur succession dans la trajectoire, milliards d'euros `
      + `${c.anneeEuros}`,
    true,
  )}

<p>Deux lectures à la date de l'enquête, et deux planchers. Ce que la garantie
coûterait <strong>aux pensions d'aujourd'hui</strong>, en remplacement de
l'ASPA, est un calcul qui ne doit rien au modèle ; ce qu'elle coûterait
<strong>aux pensions du système 4</strong> déplace toute la distribution du
facteur ci-dessus. Le plancher de base vaut pour qui vit à deux, le plancher
majoré pour qui vit seul, et l'enquête ne dit pas avec qui l'on vit : le coût
réel est entre les deux. La trajectoire retient
${seul ? "le plancher majoré" : "le plancher de base"}, celui que le
simulateur applique.</p>

<p><strong>Un ayant droit sur deux réclame.</strong> La garantie se demande,
comme l'ASPA, et le programme retient l'hypothèse que la DREES mesure sur
celle-ci : une personne seule éligible sur deux ne la réclame pas, la crainte
de la reprise sur succession étant le premier motif donné. Une avance reprise
dès le premier euro ne se réclamera pas davantage. Les bénéficiaires et les
coûts de ce dépliant, la ligne « dont garantie » des tableaux du haut et le
tableau poste par poste comptent donc ${g.pourcentage(taux, false, 0)} des ayants droit ; la part des
retraités sous le plancher, elle, est donnée entière. Le paramètre
<code>taux_recours_garantie</code> porte cette hypothèse, et un rend le recours
complet.</p>

${g.tableau(
    ["Assiette et plancher", "Sous le plancher", "Bénéficiaires",
      "Complément moyen",
      `Coût annuel, milliards d'euros ${base.annee_euros_garantie_vieillesse}`],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre"],
    `Coût annuel de la garantie vieillesse, barème appliqué à la `
      + `distribution des pensions de l'EIR ${millesime}`,
    true,
  )}

<p class="discret">Pensions <strong>brutes de droit direct</strong>, la seule des
huit distributions publiées qui soit dans la même grandeur que celles du modèle.
Les pensions d'une tranche de cent euros sont supposées y être réparties
uniformément, et la tranche ouverte du haut est traitée comme une masse
ponctuelle. Le déplacement est <em>proportionnel et uniforme</em>, alors que le
scénario ne déplace pas toutes les carrières du même rapport ; la forme de la
distribution est celle de ${millesime}, tenue constante sur toute la série, le
passé comme l'avenir. Ce tableau applique le barème à tous les retraités de
${millesime} ; la trajectoire ne l'applique qu'à ceux de 65 ans et plus, d'où un
coût plus bas la même année.</p>

<p><strong>Ce qu'elle remplace.</strong> La garantie succède à l'ASPA, et le
système 4 ne sert plus le minimum contributif ni la pension majorée de
référence : trois planchers que l'impôt et les caisses paient déjà. Ce que
l'impôt paierait <em>en plus</em> est la garantie moins ces trois-là. Le
minimum garanti de la fonction publique disparaît aussi, mais il n'est pas
compté ici : les régimes de la fonction publique le servent dans leur dépense
de pensions, que la trajectoire remplace déjà.</p>

${g.tableau(
    ["Ligne", "D'où vient le chiffre", `En ${anneeMinima}`],
    lignesRemplaces,
    ["", "texte", "nombre"],
    `Ce que la garantie vieillesse remplace, en ${anneeMinima}`,
    true,
  )}

<p class="discret">Le minimum vieillesse est le poste des comptes de la
protection sociale ; le minimum contributif est calculé sur la grille des cas
types, qui n'est pas une population et le sous-estime : il est réclamé par des
carrières courtes que la grille ne compte guère. La pension majorée de
référence n'est pas chiffrée, aucun code du
moteur ne la servant. Le total est donc une borne basse, et l'écart une borne
haute.</p>

<div class="note"><strong>Deux corrections, et les deux sont dans la
page.</strong> L'ASPA est réclamée par <strong>une personne seule éligible
sur deux</strong> : fin 2016, 321 200 personnes vivaient sous son plafond sans
la demander, pour 790 millions d'euros non versés, soit 59 % des sommes servies
(DREES, <em>Les dossiers de la DREES</em> n° 97, mai 2022). Le tableau applique
le même recours à la garantie, un ayant droit sur deux : ce qu'elle coûte en
plus est compté ainsi, et le recours complet le doublerait. Dans le même sens,
la garantie est une <strong>avance reprise sur la succession</strong>, dès le
premier euro et avec intérêts, là où l'ASPA n'est récupérée qu'au-delà d'un
seuil d'actif net : le Fonds de solidarité vieillesse en a retiré 108,7
millions d'euros en 2024 (143,9 en 2023, avant le relèvement du seuil), deux
pour cent de ce qu'elle verse. La garantie touche une population bien plus
large, et souvent propriétaire : la trajectoire suit ces avances et ce que
les successions en rendent, au taux de couverture du réglage, qui est une
hypothèse et non une donnée. La ligne « dont garantie » reste
<strong>brute, avant reprise</strong> ; les lignes « dont reprises » et
« garantie nette » disent le reste.</div>

<div class="note"><strong>La garantie n'est pas l'ASPA à un autre
montant.</strong> L'ASPA regarde <em>toutes les ressources du foyer</em> et ne
sert rien à un couple à 300 € et 1 500 € ; la garantie ne regarde que la pension
d'une personne, et sert 500 € au premier. C'est ce changement d'assiette, plus
encore que le montant, qui fait passer d'une allocation servie à quelques
centaines de milliers de personnes à une allocation ouverte à
${g.nombre(garantieBasse.beneficiaires / 1e6, 1)} millions de retraités aux
pensions d'aujourd'hui, et à
${g.nombre(garantieScenario.beneficiaires / 1e6, 1)} millions à celles du
système 4, dont la moitié la réclamerait.</div>
`, "cout-garantie");
}

/**
 * Le pilier capitalisé n'est pas dans ce bilan, et il faut dire pourquoi.
 *
 * Une page qui compte ce qui rentre et ce qui sort d'un système en répartition
 * doit dire ce qu'elle fait d'un prélèvement qui n'y entre pas. Le pilier ne
 * finance aucune pension d'aujourd'hui : il constitue un capital, au nom de
 * celui qui verse. Copie de `_cout_detail_capitalisation` dans `web/pages.py`.
 */
// Les années où la trajectoire du pilier est lue : la bascule, puis tous les
// dix ans jusqu'à l'horizon.
const ETAPES_PILIER = [0, 4, 14, 24, 34, 44];

/**
 * Ce que le pilier de TOUS les cotisants collecte, prélève, détient et sert,
 * année par année, sous le régime de frais réglé. Portage de
 * `_cout_pilier_trajectoire` : le niveau vient du compte du COR, la grille ne
 * fournit que des rapports par euro versé.
 */
function coutPilierTrajectoire(contexte) {
  const base = contexte.base;
  const cout = contexte.cout();
  const { avenir, solde } = cout;
  const tauxLiberal = base.taux_cotisation_liberal;
  if (!avenir.annees.length || !solde.annees.length || tauxLiberal <= 0) return "";
  const facteur = tauxCapitalisationApplique(base) / tauxLiberal;
  if (facteur <= 0) return "";

  const niveaux = (ligne) => {
    const bilan = solde.annee(ligne.annee);
    if (!ligne.pilier || !bilan || ligne.pib <= 0) return null;
    const part = bilan.postesRessources("notionnel_liberal").cotisations * facteur;
    const montants = ligne.pilier.niveaux(part * ligne.pib * ligne.coefficientConstants);
    montants.part_pib_versements = part;
    montants.part_pib_encours = part * ligne.pilier.encours;
    return montants;
  };

  const bascule = base.annee_debut_capitalisation;
  const lignes = [];
  for (const ecart of ETAPES_PILIER) {
    const ligne = avenir.annee(bascule + ecart);
    const montants = ligne ? niveaux(ligne) : null;
    if (!montants) continue;
    lignes.push([
      String(ligne.annee),
      milliards(montants.versements, 0),
      milliards(montants.frais, 1),
      g.pourcentage(ligne.pilier.taux_frais_encours, false, 2),
      `${milliards(montants.encours, 0)} (${g.pourcentage(montants.part_pib_encours, false, 0)} du PIB)`,
      milliards(montants.rentes, 0),
    ]);
  }
  const cumuls = { versements: 0.0, frais: 0.0, frais_accumulation: 0.0,
    frais_rentes: 0.0, rentes: 0.0 };
  for (const ligne of avenir.projetees()) {
    const montants = niveaux(ligne);
    if (!montants) continue;
    for (const cle of Object.keys(cumuls)) cumuls[cle] += montants[cle];
  }
  if (!lignes.length || cumuls.versements <= 0) return "";
  const derniere = avenir.derniereAnnee;
  const partFrais = cumuls.frais / cumuls.versements;
  return `
<p><strong>Ce que le pilier collecte, ce que l'enveloppe prélève, ce qu'il
sert.</strong> Ce dépliant, lui, compte le pilier : pas dans le solde, qui
reste celui de la répartition, mais pour lui-même. Les versements sont les
cotisations du système 4 telles que le compte du COR les ancre, multipliées par
le rapport des deux taux (${g.pourcentage(tauxCapitalisationApplique(base), false, 0)}
contre ${g.pourcentage(tauxLiberal, false, 0)}) ; frais, encours et rentes
viennent des carrières types, par euro versé, sous le réglage « Frais du
pilier capitalisé » de cette page : chaque versement entre au tarif de son
année, les paliers font baisser les tarifs, et la rente garde les frais de
l'année où elle est souscrite.</p>

${g.tableau(
    ["Année", "Versements", "Frais prélevés dans l'année", "Frais de gestion, en part de l'encours", "Encours", "Rentes servies"],
    lignes,
    ["", "nombre", "nombre", "nombre", "nombre", "nombre"],
    `Le pilier de tous les cotisants, milliards d'euros de ${cout.anneeEuros}`,
    true,
  )}

<p>De ${avenir.premiereAnneeProjetee} à ${derniere}, le pilier collecte
${milliards(cumuls.versements, 0)} et l'enveloppe en prélève
${milliards(cumuls.frais, 0)}, soit
${g.pourcentage(partFrais, false, 1)} des versements :
${milliards(cumuls.frais_accumulation, 0)} pendant l'accumulation, sur les
versements et sur l'encours, et ${milliards(cumuls.frais_rentes, 0)} sur les
rentes, qui totalisent ${milliards(cumuls.rentes, 0)} servis. Le taux de
frais rapporté à l'encours baisse au fil du tableau : c'est la trajectoire des
frais, et la part du stock qui la suit. Changer le réglage change ce tableau,
et lui seul sur cette page.</p>`;
}

function coutDetailCapitalisation(contexte) {
  const base = contexte.base;
  const repartition_ = base.taux_cotisation_liberal;
  const capitalise = base.taux_capitalisation_obligatoire;
  const volontaire = tauxCapitalisationVolontaireApplique(base);
  const impose = repartition_ + capitalise;
  const total = impose + volontaire;
  // La ligne volontaire ne paraît que si elle existe : la retirer des
  // paramètres doit rendre au tableau la forme qu'il avait à deux lignes.
  const ligneVolontaire = volontaire
    ? [["Placé volontairement, les points rendus", "—",
      g.pourcentage(volontaire, false, 0)]]
    : [];
  const trajectoire = coutPilierTrajectoire(contexte);
  return g.depliant(
    "Ce que le pilier capitalisé prélève, et pourquoi il n'est pas dans ce bilan",
    `
<p>À compter de ${base.annee_debut_capitalisation}, le système 4 prélève
${g.pourcentage(capitalise, false, 0)} de la rémunération <strong>en plus</strong>
des ${g.pourcentage(repartition_, false, 0)} de la répartition. Ces
${g.pourcentage(capitalise, false, 0)} ne paient aucune pension : ils
constituent un capital au nom de celui qui verse. Ils ne sont donc ni une
ressource ni une dépense du système de retraite, et <strong>aucun des chiffres
de cette page ne les compte</strong> — le solde du système 4 est celui de sa
répartition, comme celui des trois autres. Il en va de même des
${g.pourcentage(volontaire, false, 0)} que le cotisant peut ajouter de
lui-même : ils ne passent pas davantage par les caisses.</p>

${g.tableau(
    ["", "Aujourd'hui", "Système 4"],
    [
      ["Prélevé pour la répartition",
        g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0),
        g.pourcentage(repartition_, false, 0)],
      ["Prélevé pour la capitalisation, obligatoire", "—",
        g.pourcentage(capitalise, false, 0)],
      ...ligneVolontaire,
      ["Total imposé", g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0),
        g.pourcentage(impose, false, 0)],
      ["Total versé si les points rendus sont replacés",
        g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0),
        `<strong>${g.pourcentage(total, false, 0)}</strong>`],
    ],
    ["", "nombre", "nombre"],
    "Ce que coûte la retraite à celui qui travaille, part salariale et "
    + "patronale additionnées",
    true,
  )}

<p>Ce qui est <strong>imposé</strong> baisse de
${g.nombre((TAUX_ACTUEL_TOTAL - impose) * 100, 0)} points :
${g.pourcentage(impose, false, 0)} contre
${g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0)} aujourd'hui pour un salarié du
privé. La part qui finance les pensions des autres passe de
${g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0)} à
${g.pourcentage(repartition_, false, 0)} ; ce qui reste,
${g.pourcentage(capitalise, false, 0)}, revient à celui qui l'a versé — sous
forme de rente à la retraite, ou de capital à ses héritiers s'il meurt
avant.</p>

<p><strong>Le simulateur, lui, montre la seconde ligne du total.</strong> Les
${g.nombre((TAUX_ACTUEL_TOTAL - impose) * 100, 0)} points rendus, il les suppose
remis au même compte, et l'effort revient alors à
${g.pourcentage(total, false, 0)}, ce qu'il est déjà. C'est la seule façon de
comparer deux systèmes sans comparer en même temps deux niveaux d'effort : à ce
prix-là, ${g.pourcentage(tauxCapitalisationApplique(base), false, 0)} des
${g.pourcentage(total, false, 0)} appartiennent au cotisant et se
transmettent, contre rien aujourd'hui. Qui préfère garder ces points les garde,
et sa rente baisse de ce qu'ils auraient rapporté : la page de résultats écrit
les deux montants.</p>

${trajectoire}

<div class="note"><strong>Ce que cela ne dit pas.</strong> Le pilier est neutre
pour les comptes publics au moment où il se remplit, mais il ne l'est pas pour
toujours : les versements sont déductibles à l'entrée et la rente imposable à la
sortie, et le modèle ne calcule aucune fiscalité. Il ne dit rien non plus du
coût de transition : un euro prélevé pour être placé cesse d'être disponible
pour payer les pensions d'aujourd'hui. C'est vrai de toute capitalisation, et
c'est ce que ce prélèvement supplémentaire évite, puisqu'il ne prend rien à la
répartition.</div>`,
    "cout-capitalisation",
  );
}

/** Ce que chaque carrière type pèse dans les agrégats de la page. */
function coutDetailPoids(contexte) {
  const c = contexte.cout();
  const derniere = contexte.depenses().derniereAnnee;
  const lignes = [...CAS_TYPES]
    .sort((a, b) => (c.poids[b.code] || 0) - (c.poids[a.code] || 0))
    .map((cas) => [
      echapper(cas.libelle),
      cas.caisses.map((caisse) => caisse.replace(/_/g, " ")).join(", "),
      g.pourcentage(c.poids[cas.code] || 0, false, 1),
      g.pourcentage(c.poidsCotisants[cas.code] || 0, false, 1),
      g.pourcentage(1 / CAS_TYPES.length, false, 1),
    ]);
  return g.depliant("Ce que chaque carrière type pèse dans ces chiffres", `
<p><strong>Deux pondérations se composent.</strong> Celle de la génération est
démographique, et vient de l'INSEE. Celle du <strong>cas type</strong> est
sociologique, et elle se lit des deux côtés du bilan : dans les
<strong>dépenses</strong>, un cas type pèse les retraités de sa caisse (combien
ont eu cette carrière-là), publiés par la DREES ; dans les
<strong>recettes</strong>, il pèse ses cotisants, publiés et projetés par le
COR. La colonne de droite rappelle ce que valait la convention antérieure, qui
les pesait à égalité.</p>

${g.tableau(
    ["Cas type", "Caisse dont il porte les effectifs",
      `Retraités en ${derniere}`, `Cotisants en ${derniere}`, "Ancienne convention"],
    lignes,
    ["", "texte", "nombre", "nombre", "nombre"],
    `Ce que chaque cas type pèse dans les agrégats de cette page, en ${derniere}`,
    true,
  )}
<p class="discret">Une caisse réclamée par plusieurs cas types se partage
également entre eux : la Cnav est celle des quatre carrières du privé, et aucune
source ne dit combien de ses retraités ont été cadres. Hors de la fenêtre que la
DREES publie (2004 à 2024), la répartition du bord est reconduite : la France
de 1960 comptait plus d'exploitants agricoles que ces poids ne le disent. Les
cotisants, eux, sont projetés jusqu'en 2070, et les régimes fermés s'y
éteignent : la SNCF n'en a plus aucun à cette date. La fonction publique d'État
n'y est publiée que d'un seul tenant, et se partage entre civils et militaires
à la clé du jaune budgétaire « Pensions », tenue constante.</p>
`, "cout-poids");
}

/** Trois séries, trois périmètres, et pourquoi ils ne se confondent pas. */
function coutDetailSources(contexte) {
  const comptes = contexte.comptes();
  const depenses = contexte.depenses();
  const c = contexte.cout();
  const solde = c.solde;
  const derniere = depenses.derniereAnnee;
  return g.depliant("D'où viennent ces chiffres", `
<p>Cette page croise deux producteurs de comptes, et ils ne comptent pas la
même chose. Rien n'est mélangé pour autant : du modèle, les deux premières
cartes n'empruntent qu'un <strong>rapport</strong> entre systèmes, qui est sans
dimension.</p>

<h4>Le compte du système de retraite — Conseil d'orientation des retraites</h4>
<p>Dépenses, ressources et solde du même ensemble de régimes, sous la même
convention, de ${solde.premiereAnnee} à ${solde.derniereAnnee}. Champ : régimes
légalement obligatoires, FSV compris, RAFP exclu — ni dépendance, ni
capitalisation. ${g.pourcentage(comptes.depense(derniere), false, 2)} du PIB
en ${derniere}. C'est la source des deux premières cartes et de celle sur la
réforme.</p>
<p class="discret">On lui prend les DEUX colonnes, jamais une seule : un solde
ne se fabrique pas en soustrayant deux périmètres. On aurait voulu les
ressources du même producteur que la dépense ci-dessous ; elles n'existent
pas. <strong>Les comptes de la protection sociale ne ventilent pas leurs
ressources par risque</strong> — une « recette du risque vieillesse » est une
donnée sans définition comptable, les cotisations d'un régime polyvalent
n'étant affectées à aucun risque.</p>

<h4>Ce que d'autres caisses versent — rapports à la Commission des comptes de
la Sécurité sociale</h4>
<p>Le poste « transferts » du compte du COR, ventilé par celui qui paie, de
${comptes.premiereAnneeTransferts} à ${comptes.derniereAnneeTransferts} :
la fiche de la CNAF pour l'assurance vieillesse des parents au foyer et les
majorations pour enfants, celles de l'Agirc-Arrco et de l'Ircantec pour les
points des chômeurs que l'Unédic paie. C'est la source du dépliant « Ce que la
branche famille et l'assurance chômage versent ».</p>
<p class="discret">Un rapport n'est lu que pour ses comptes arrêtés, et le
premier qui arrête une année l'emporte. Les rapports d'avant 2013 sont chiffrés
ou compressés d'une façon que le lecteur du dépôt n'ouvre pas : la série
commence là.</p>

<h4>Les comptes de la protection sociale — DREES</h4>
<p>La dépense, risque par risque, depuis ${c.premiereAnnee}. Le risque
<strong>vieillesse-survie</strong> entier vaut
${g.pourcentage(depenses.partPib(derniere), false, 2)} du PIB en ${derniere},
et la <strong>répartition obligatoire</strong> seule
${g.pourcentage(depenses.repartition(derniere) / depenses.pib.valeur(derniere), false, 2)}.
C'est la source de la carte « est-ce que ça a toujours coûté autant ».</p>
<p class="discret">Moins de trois dixièmes de point séparent cette répartition
obligatoire du périmètre du COR : c'est le meilleur recoupement dont ces deux
séries disposent, et un test du dépôt le tient.</p>

<h4>Le modèle du dépôt</h4>
<p>Treize carrières types croisées avec ${c.generations.length} générations, de
${c.generations[0]} à ${c.generations[c.generations.length - 1]}, pesées par les effectifs réels
de l'INSEE et par les effectifs de retraités que la DREES publie caisse par
caisse. Il ne produit qu'un rapport de masses de pension — jamais un niveau de
dépense dans les cartes du haut.</p>
<p class="discret">Fiabilité : la dépense observée est
<strong>certifiée</strong>, recontrôlée contre l'API de la DREES à chaque
exécution ; le compte du COR est <strong>de niveau haut</strong>, consolidé par
lui depuis les rapports à la Commission des comptes de la Sécurité sociale ; et
tout ce qui passe par un rapport de masses est <strong>estimé</strong>, sans
pouvoir être autre chose — aucune institution ne publie ce qu'aurait coûté un
système qui n'a pas existé. Tout est détaillé sur la page
<a href="${g.lien("/donnees")}">Données</a>.</p>
`, "cout-sources");
}

/** Tout ce que cette page ne dit pas, en une seule liste. */
/**
 * La part de l'avance que la succession couvre, telle que la trajectoire l'a
 * retenue l'année de la bascule — calculée ou réglée.
 */
function partRepriseBascule(contexte) {
  const ligne = contexte.cout().avenir.annee(contexte.base.annee_bascule);
  return ligne !== null && ligne.garantie ? ligne.garantie.partReprise : 0.0;
}

function coutDetailLimites(contexte) {
  const c = contexte.cout();
  const solde = c.solde;
  const avenir = c.avenir;
  const observe = solde.annee(solde.derniereAnneeObservee);
  return g.depliant("À lire avant de citer ces chiffres", `
<p>Une page de chiffres vaut par ce qu'elle laisse de côté. Rien de ce qui
suit n'est certifié, et ne peut l'être : une projection est une hypothèse,
celle de l'INSEE pour la démographie, celle du COR pour la macroéconomie,
celle du modèle pour les pensions, jusqu'en ${avenir.derniereAnnee}, horizon des
projections de population, et pas un an de plus. Ce qui se règle est dit sous
son réglage : les pensions en cours à la bascule, la part de l'avance que la
succession couvre. Ce qui décrit un système est dans le dépliant de ce
système : ce que la recette suit, à qui la réversion est servie, ce que le
coefficient d'équilibre ferait. Restent ici les réserves que le lecteur ne
peut ni changer ni lire ailleurs.</p>
<ul class="serree">
  <li><strong>La projection est celle du COR</strong>, scénario de référence,
  avec ses hypothèses : démographie de l'INSEE, productivité, chômage. Ses
  ressources reculent en part de PIB parce que l'assiette des cotisations y
  progresse moins vite que le PIB : cette hypothèse est la sienne, et personne
  ne l'a mesurée. Seize autres scénarios démographiques existent, dont l'écart
  mesurerait l'incertitude ; cette page n'en montre aucun.</li>
  <li><strong>Les réserves d'aujourd'hui ne sont pas comptées.</strong> Le
  système de retraite détient des réserves financières que le COR chiffre à
  part ; un solde annuel négatif peut être couvert par elles pendant des
  années. La dette de la section « ce que le déficit accumule » part de zéro à
  ${solde.derniereAnneeObservee} : elle dit ce que les soldes à venir
  ajoutent, jamais ce que le système détient.</li>
  <li><strong>L'assiette est supposée insensible au taux.</strong> Un taux de
  cotisation plus bas déforme l'offre de travail et la structure des
  rémunérations ; aucune élasticité n'est posée ici, et le sens de l'effet
  joue plutôt en faveur du système 4. Au-delà de la dernière année où
  l'assiette est publiée, c'est le TAUX DE PRÉLÈVEMENT qui est reconduit et
  non la part de PIB de l'assiette : celle-ci suit alors les ressources
  projetées par le COR, dont la baisse en part de PIB tient précisément à une
  assiette qui progresse moins vite que le PIB.</li>
  <li><strong>La grille échantillonne une génération sur cinq, et l'année du
  retour à l'équilibre se lit à quelques années près.</strong> Une cohorte qui
  part juste avant la bascule est représentée par une génération qui part
  juste après : les courbes de réforme s'écartent d'un ou deux dixièmes de
  point avant même la bascule, et un test borne l'effet à un demi-point. Le
  déficit actuel vaut ${g.pourcentage(Math.abs(observe.solde("actuel")), false, 2)} du PIB, c'est-à-dire
  l'ordre de grandeur de l'écart que ce pas introduit à lui seul autour de la
  bascule : l'année où une courbe repasse zéro en dépend.</li>
  <li><strong>Le modèle compte des générations, non des personnes.</strong> Il
  suppose que la même proportion de chaque génération perçoit une pension, et
  que la carrière type ne change pas : un recul de l'âge de départ, une
  carrière plus longue ou plus hachée déplaceraient la trajectoire. Ses
  effectifs sont ceux des caisses, où un polypensionné compte dans chacune des
  siennes, ce qui gonfle le poids des régimes dont les affiliés ont
  typiquement aussi une carrière au régime général. Et avant 1975 la
  reconstitution est mince : la répartition ne commence qu'en
  ${contexte.base.annee_debut_repartition} ; les générations antérieures à
  ${c.generations[0]} n'ont, dans ce modèle, aucune pension, plusieurs
  régimes n'existaient pas encore, et les premières années reposent sur deux
  ou trois générations et la moitié des cas types.</li>
</ul>
<p class="discret">Les limites du modèle dans son ensemble sont dans
<a href="${g.DEPOT}/blob/main/docs/limites.md">docs/limites.md</a>, et la
méthode sur la page <a href="${g.lien("/methode")}">Méthode</a>.</p>
`, "cout-limites");
}

/**
 * Les neuf règles que compare la page Méthode, dans l'ordre d'affichage :
 * libellé, mode, fenêtre de lissage. L'ordre n'est pas celui des valeurs — il
 * va de la règle demandée à celle que la théorie désigne, en passant par celle
 * que le droit applique.
 */
const REGLES_COMPAREES = [
  ["Triple lock inversé, littéral", ModeIndexation.TRIPLE_LOCK_INVERSE, 1],
  ["Moyenne des trois taux", ModeIndexation.MOYENNE_TROIS_TAUX, 1],
  ["Triple lock inversé, tout en nominal",
    ModeIndexation.TRIPLE_LOCK_INVERSE_NOMINAL, 1],
  ["Indexation sur les prix", ModeIndexation.PRIX, 1],
  ["Médiane des trois taux", ModeIndexation.MEDIANE_TROIS_TAUX, 1],
  ["Revalorisation réellement pratiquée",
    ModeIndexation.REVALORISATION_PORTEE_AU_COMPTE, 1],
  ["Masse salariale (règle d'équilibre)", ModeIndexation.MASSE_SALARIALE, 1],
  ["PIB nominal", ModeIndexation.PIB_NOMINAL, 1],
  ["PIB nominal lissé sur 5 ans (Italie)", ModeIndexation.PIB_NOMINAL, 5],
];

/**
 * Bornes du cumul comparé. Une somme versée en 1940 est revalorisée à partir de
 * l'année SUIVANTE : les taux appliqués sont donc ceux de 1941 à 2025 inclus,
 * ce que l'intitulé de la colonne appelle « appliquée 1941-2025 ».
 */
const ANNEE_VERSEMENT_COMPARE = 1940;
const ANNEE_ARRIVEE_COMPAREE = 2025;

/**
 * La cotisation et les deux liquidations qui illustrent la loterie de cohorte.
 * 2020 est l'année du trou ; liquider un an plus tard rapportait alors moins.
 */
const ANNEE_COTISATION_LOTERIE = 1980;
const LIQUIDATIONS_LOTERIE = [2019, 2020];

/**
 * Ce que vaut une même cotisation selon l'année où l'on liquide.
 *
 * Quatre coefficients : la cotisation de 1980 portée à 2019 puis à 2020, sans
 * lissage puis lissée sur cinq ans. Deux passages du site les citent en toutes
 * lettres pour montrer qu'attendre un an pouvait faire perdre — autant qu'ils
 * les lisent au même endroit, et que cet endroit soit le modèle.
 */
function loterieDeCohorte(contexte) {
  const simulateur = contexte.simulateur();
  const valeurs = new Map();
  for (const lissage of [1, 5]) {
    const parametres = avec(simulateur.parametres, {
      mode_indexation: ModeIndexation.PIB_NOMINAL, lissage_indexation: lissage,
    });
    const indexation = new Indexation(simulateur.macro, parametres);
    for (const arrivee of LIQUIDATIONS_LOTERIE) {
      const coefficient = indexation.coefficient(ANNEE_COTISATION_LOTERIE, arrivee);
      valeurs.set(`${lissage}|${arrivee}`, `×${g.nombre(coefficient, 2)}`);
    }
  }
  return valeurs;
}

/**
 * Rendement cumulé de chaque règle comparée, sur 1941-2025.
 *
 * Ces neuf nombres étaient écrits à la main dans la page — les seuls du site à
 * ne pas sortir du modèle. Ils ne dépendent d'aucune carrière, ce qui les
 * rendait faciles à recopier, et l'un d'eux avait fini par mentir de trois
 * dixièmes de point.
 */
function cumulsIndexation(contexte) {
  const simulateur = contexte.simulateur();
  const cumuls = new Map();
  for (const [libelle, mode, lissage] of REGLES_COMPAREES) {
    const parametres = avec(simulateur.parametres, {
      mode_indexation: mode, lissage_indexation: lissage,
    });
    cumuls.set(libelle, new Indexation(simulateur.macro, parametres)
      .coefficient(ANNEE_VERSEMENT_COMPARE, ANNEE_ARRIVEE_COMPAREE));
  }
  return cumuls;
}

/**
 * Comment une pension est calculée, et ce qui décide du résultat.
 *
 * C'est la page la plus technique du site, et c'est celle qui avait le plus
 * besoin d'un ordre de lecture. Elle alignait huit sections de même poids, et
 * rien n'y disait laquelle compte.
 *
 * Une seule compte, et la page le dit maintenant en tête : LA RÈGLE
 * D'INDEXATION DOMINE TOUT LE RESTE. C'est elle qui explique l'essentiel de
 * l'écart affiché par les scénarios rétroactifs, et non le passage aux comptes
 * notionnels. Elle est donc seule visible ; le reste est replié.
 */
function methode(contexte) {
  const cumuls = cumulsIndexation(contexte);
  const prix = cumuls.get("Indexation sur les prix");
  const lignesIndexation = REGLES_COMPAREES.map(([libelle]) => {
    const valeur = cumuls.get(libelle);
    let conserve = g.pourcentage(valeur / prix, false, 1);
    if (libelle === REGLES_COMPAREES[0][0]) {
      // La règle demandée est celle que la page vient d'annoncer : c'est son
      // chiffre qu'on vient lire, et il est mis en valeur.
      conserve = `<strong>${conserve}</strong>`;
    }
    return [libelle, `×${g.nombre(valeur, 1)}`, `×${g.nombre(prix, 1)}`, conserve];
  });
  const conserveLitteral = g.pourcentage(
    cumuls.get(REGLES_COMPAREES[0][0]) / prix, false, 1);
  const revalPratiquee = cumuls.get("Revalorisation réellement pratiquée");
  const masseSalariale = cumuls.get("Masse salariale (règle d'équilibre)");
  const loterie = loterieDeCohorte(contexte);

  const calcul = g.points([
    ["1. On inscrit",
      "Chaque cotisation retraite réellement versée est portée au compte, "
      + "au premier euro et sans plafond."],
    ["2. On revalorise",
      "Le solde est augmenté chaque année d'un taux fixé par la règle "
      + "collective : par défaut, le rythme auquel progresse la masse des "
      + "salaires."],
    ["3. On divise",
      "Au départ, <code>pension = solde ÷ espérance de vie restante</code>, "
      + "lue sur la table de votre génération."],
  ]);

  const tableauIndexation = g.tableau(
    ["Règle appliquée 1941-2025", "Comptes", "Prix",
      "Pouvoir d'achat conservé"],
    lignesIndexation,
    ["", "nombre", "nombre", "nombre"],
    "Ce que chaque règle d'indexation aurait conservé du pouvoir "
    + "d'achat, 1941-2025",
    true,
  );

  const carte = g.cle(
    "Qu'est-ce qui décide du résultat ?",
    `La règle de revalorisation, et de très loin. Selon celle qu'on
retient, une cotisation de 1950 conserve ${conserveLitteral} de sa valeur, ou
onze fois plus. <strong>C'est de là que vient l'essentiel de l'écart affiché par
les scénarios rétroactifs</strong>, bien plus que du passage aux comptes notionnels.`,
    tableauIndexation,
    `La règle appliquée par défaut est la croissance de la masse des
salaires : ce qu'un système en répartition peut servir sans toucher à son taux.
Les huit autres restent à un clic, dans les options du simulateur.`,
  );

  const tete = g.affiche(
    "La méthode",
    "Comment c'est calculé, "
    + '<span class="cle-texte">en trois opérations.</span>',
    "Un compte notionnel est un compte <em>virtuel</em> : rien n'est "
    + "placé, les cotisations de l'année paient les pensions de l'année. "
    + "Ce qui change, c'est le calcul du droit.",
  );

  return `
${tete}

<div class="note resume"><strong>En clair.</strong> Votre pension serait votre
compte divisé par le nombre d'années qu'il vous reste à vivre, en moyenne.
Chaque euro cotisé compte, et rien d'autre : ni trimestres, ni minimum, ni
majoration. Le compte grossit chaque année au rythme de la masse des
salaires, c'est-à-dire de ce que la répartition peut promettre sans mentir.
Le système actuel, lui, est recalculé règle par règle sur la même carrière,
pour servir de point de comparaison.</div>

${calcul}

<p>Trois conséquences. La pension est exactement proportionnelle aux
cotisations. Partir tôt coûte deux fois : moins de cotisations, et une pension à
servir plus longtemps. Et aucun droit qu'une cotisation n'a pas financé
n'existe. C'est la règle que <a href="${g.lien("/")}">le programme</a> propose,
et <a href="${g.lien("/cas-types")}">treize carrières types</a> montrent ce
qu'elle déplace, génération par génération.</p>

${carte}

<p class="actions"><a class="bouton" href="${g.lien("/simuler")}">Voir le calcul
sur une carrière</a><a href="${g.DEPOT}/blob/main/docs/methodologie.md">La
méthodologie complète</a></p>

<h2>Pour aller plus loin</h2>

${methodeIndexation(contexte, revalPratiquee, masseSalariale, loterie)}
${methodeCapitalisation(contexte)}
${methodeDroitPositif()}
${methodeSuppressions()}
${methodeCarriere(contexte)}
${methodeUnites()}
${methodeConstruction()}
`;
}

/**
 * Le pilier capitalisé : où va l'argent, à quel taux, à quel prix.
 *
 * Portage de `_methode_capitalisation`. C'est la seule partie du modèle qui
 * place réellement de l'argent, et donc la seule qui dépende d'un marché :
 * elle doit dire d'où viennent les taux, ce que le placement suppose, et ce
 * que la transmission change à la comparaison avec la répartition.
 */
function methodeCapitalisation(contexte) {
  const base = contexte.base;
  const courbe = new CourbeTauxSansRisque(contexte.paquet);
  const taux = g.pourcentage(base.taux_capitalisation_obligatoire, false, 0);
  const volontaire = g.pourcentage(
    tauxCapitalisationVolontaireApplique(base), false, 0,
  );
  const totalCapitalise = g.pourcentage(
    tauxCapitalisationApplique(base), false, 0,
  );

  const comptants = g.tableau(
    ["Maturité", "Taux zéro-coupon, en rythme annuel"],
    MATURITES.map((maturite) => [`${maturite} ans`,
      g.pourcentage(courbe.placement(courbe.annee, maturite).taux, false, 2)]),
    ["", "nombre"],
    `La courbe employée, au ${dateEnClair(courbe.date)}`,
    true,
  );

  // L'allocation, telle que la règle la produit : ce sont les poids que le
  // moteur applique, lus par le même code. Une table écrite à la main pourrait
  // se désaccorder du calcul ; celle-ci ne le peut pas.
  const horizons = [40, 30, 20, 10, 5, 2];
  const glissement = g.tableau(
    ["Années avant le départ", "Répartition du versement par maturité"],
    horizons.map((horizon) => [String(horizon),
      repartition(horizon).map(([maturite, poids]) => `${g.pourcentage(poids)} à ${maturite} an`
        + `${maturite > 1 ? "s" : ""}`).join(", ")]),
    ["nombre", ""],
    "Où va un versement selon ce qu'il reste à courir",
    true,
  );

  return g.depliant(
    `Le pilier capitalisé : ${totalCapitalise} placés, ce que cela suppose`,
    `
<p>La proposition ajoute, à compter de ${base.annee_debut_capitalisation}, une
cotisation de ${taux} prélevée sur la même assiette que la cotisation de
répartition, <strong>en plus</strong> d'elle : elle ne s'y substitue pas. Elle
n'entre pas au compte notionnel, elle constitue un capital au nom du cotisant,
dans un plan d'épargne retraite. Les années antérieures gardent les taux qui étaient les
leurs et ne versent rien.</p>

<h3>Les ${volontaire} qui ne sont imposés par personne</h3>
<p>${g.pourcentage(base.taux_cotisation_liberal, false, 0)} de répartition et
${taux} capitalisés font
${g.pourcentage(base.taux_cotisation_liberal + base.taux_capitalisation_obligatoire, false, 0)},
quand le système actuel en prélève
${g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0)} pour un salarié du privé. La
proposition rend donc ${volontaire}, et le modèle suppose qu'ils sont
<strong>replacés sur le même compte</strong>, aux mêmes conditions : le pilier
reçoit ${totalCapitalise} en tout, et l'effort de retraite revient à
${g.pourcentage(tauxRetraitePropose(base), false, 0)}, exactement celui
d'aujourd'hui. Le modèle ne prétend pas prévoir que les cotisants le feront : il
pose une <strong>convention de comparaison</strong>. Sans elle, le site
opposerait deux systèmes qui ne coûtent pas le même prix, et l'écart de pension
se lirait pour partie comme un effet des règles alors qu'il viendrait d'un
effort moindre.</p>
<p>Le compartiment ne distingue ces points nulle part ailleurs qu'en proportion
— même assiette, même échelle de maturités, mêmes frais, même table de
mortalité —, si bien que la rente se partage dans le rapport exact des deux
taux. Deux endroits les séparent, et deux seulement. Sur la <strong>fiche de
paie</strong>, les ${volontaire} volontaires sont portés en entier par l'assuré,
là où les ${taux} imposés sont partagés avec l'employeur : personne ne cofinance
une épargne qu'on décide seul, et le coût du travail ne bouge pas quand on la
verse. Dans les <strong>résultats</strong>, la rente qu'ils servent est écrite
sur sa propre ligne, pour que le lecteur qui ne les verserait pas puisse la
retrancher.</p>
<p>Un troisième endroit aurait pu les séparer, et ne les sépare pas : la
<strong>garantie vieillesse</strong>. Elle est différentielle, elle compte les
ressources et non leur origine, et cette rente-là en est une. Une épargne que
personne n'oblige réduit donc l'allocation, exactement comme une pension
personnelle réduit l'ASPA d'aujourd'hui. Pour qui reste sous le plancher après
avoir versé, ces cinq points ne rapportent <strong>rien du tout</strong> en
pension : la garantie les reprend euro pour euro. Il leur reste ce que la
répartition ne donne à personne, un capital qui se transmet.</p>

<h3>Où l'argent est placé</h3>
<p>Sur des titres sans risque, portés jusqu'à leur échéance. La courbe retenue
est celle des souverains les mieux notés de la zone euro, que la Banque centrale
européenne publie chaque jour ouvré : c'est la définition opérationnelle du taux
sans risque en euro. L'OAT française rend davantage : une cinquantaine de points
de base au dix ans. Cet écart rémunère un risque de crédit, et un régime
obligatoire qui promet une rente ne peut pas le compter comme un rendement
acquis. Retenir la courbe la mieux notée est donc le choix prudent, et il
réduit la rente affichée.</p>
${comptants}
<p>Les versements des années suivantes ne se placent pas à ces taux-là, mais aux
taux À TERME que cette même courbe implique, ceux que le marché cote déjà pour
une période future. C'est ce qui dispense le modèle d'une prévision de taux :
le forward n'est pas une opinion, il est arbitré. <strong>Ce qu'il suppose</strong>
tient en une phrase : que le taux futur sera, en moyenne, le forward
d'aujourd'hui. C'est l'hypothèse des anticipations pures, et elle ignore la
prime de terme, c'est-à-dire le supplément qu'un prêteur exige pour immobiliser
son argent. Quand la courbe monte, elle flatte donc légèrement le pilier.
Au-delà de trente ans, la courbe ne dit plus rien : le taux est prolongé à plat,
et tout résultat qui en dépend est déclaré « estimé ».</p>

<h3>Selon quelle règle les maturités sont choisies</h3>
<p>Longues tant que le départ est loin, courtes à l'approche : c'est
l'allocation par horizon que toute épargne à échéance pratique. Aucune ligne
n'arrive à échéance après le départ, car il faudrait la vendre avant terme, à un
prix qui n'est plus sans risque ; à l'échéance d'une ligne, son produit est
replacé selon la même règle, pour ce qu'il reste à courir. Aucune maturité
ne dépasse les trois quarts du versement : une épargne obligatoire ne se
concentre pas sur un seul point de la courbe.</p>
${glissement}

<h3>Ce que l'enveloppe coûte</h3>
<p>Quatre prélèvements, aux <strong>vraies moyennes du marché</strong> du plan
d'épargne retraite individuel en 2025, mesurées par l'Observatoire des
produits d'épargne financière sur les remises de l'ACPR :
${g.pourcentage(base.frais_versement_capitalisation, false, 2)} sur chaque
versement, ${g.pourcentage(base.frais_gestion_capitalisation, false, 2)} par
an sur l'encours, ${g.pourcentage(base.frais_arrerages_capitalisation, false, 2)}
sur chaque arrérage de rente, moyenne sur tous les assureurs et non sur les
seuls neuf sur vingt qui facturent, et
${g.pourcentage(base.frais_encours_rente_capitalisation, false, 2)} par an
sur la réserve qui porte la rente, un frais que l'Observatoire ne mesure pas et
que le CCSF relevait sur vingt-deux contrats sur trente-quatre.</p>

<p><strong>Ils baissent ensuite, par paliers.</strong> Partout où une épargne
retraite obligatoire existe, la concurrence ou la règle ont fait tomber les
frais bien au-dessous de ceux d'un produit vendu au détail, et par à-coups : un
plafond au Royaume-Uni, un appel d'offres tous les deux ans au Chili, une
remise imposée aux gérants en Suède ; et là où seule la concurrence joue, aux
États-Unis, une baisse de 3,3 % par an pendant trente ans. Le modèle fait
suivre ce rythme au frais de gestion, par marches de dix ans, jusqu'à
${g.pourcentage(base.frais_gestion_paliers.at(-1)[1], false, 2)} en
${base.frais_gestion_paliers.at(-1)[0]} ; le frais sur versement rejoint
l'assurance-vie, puis le contrat de capitalisation, puis
${g.pourcentage(base.frais_versement_paliers.at(-1)[1], false, 2)} en
${base.frais_versement_paliers.at(-1)[0]} ; le frais sur arrérages s'éteint en
${base.frais_arrerages_paliers.at(-1)[0]}. <strong>La baisse porte surtout sur
les nouveaux dépôts</strong> : chaque versement entre au tarif de son année et
le garde, et ne se rapproche du tarif du jour que de
${g.pourcentage(base.convergence_frais_stock, false, 0)} de l'écart par an.
La rente garde les frais de l'année où elle est souscrite. Les sources de
chaque palier, et ce que d'autres trajectoires déplaceraient, sont dans les
limites du modèle.</p>

<h3>Comment le capital devient une rente</h3>
<p>Par le mécanisme du plan d'épargne retraite : le capital est divisé par un
coefficient actuariel, puis chaque arrérage supporte ses frais. Le coefficient
est celui du modèle (table de génération, unisexe par défaut), et le taux
technique est nul, comme dans la plupart des contrats. Les deux lignes du
système 4 partagent alors le MÊME diviseur, et deviennent comparables au
centime : à capital égal elles servent le même montant, et tout écart vient
d'ailleurs.</p>

<h3>Ce qui se transmet</h3>
<p>Le capital, intégralement, si le cotisant meurt avant d'avoir liquidé. C'est
la règle du plan d'épargne retraite, et c'est ce que la répartition ne fait
pas : un compte notionnel n'est pas un capital, il est un droit, et il s'éteint
avec son titulaire sans rien laisser. Après la liquidation, la rente est
viagère et ne se transmet pas davantage : une rente réversible ou à annuités
garanties serait plus faible, et le modèle ne la retient pas.</p>

<h3>Ce que le modèle ne fait pas</h3>
<p>Il ne simule aucun risque de marché : le pilier est placé sans risque par
construction, et le seul aléa qui subsiste, celui de taux futurs s'écartant des
forwards d'aujourd'hui, n'est pas chiffré. Il ne calcule aucune fiscalité :
tous les montants du site sont bruts, ici comme ailleurs, alors que les
versements au plan sont déductibles et la rente imposable. Et la garantie
vieillesse ne regarde pas cette rente : elle est servie sur la seule pension
contributive de répartition. Savoir si un pilier capitalisé doit réduire une
allocation différentielle est une question de droit, pas de modèle.</p>`,
    "capitalisation",
  );
}

/**
 * Le détail du tableau d'indexation, ligne par ligne.
 *
 * Cinq paragraphes qui ne se lisent qu'une fois qu'on a vu le tableau, et qui
 * répondent chacun à une question précise.
 */
function methodeIndexation(contexte, revalPratiquee, masseSalariale, loterie) {
  return g.depliant("Le détail des neuf règles d'indexation", `
<p><strong>Le triple lock inversé</strong> —
<code>min(inflation, croissance du salaire moyen, productivité réelle)</code> —
est la règle qui a donné son cahier des charges à ce simulateur. Prise à la
lettre, elle compare deux taux nominaux à un taux réel, et c'est ce qui la rend
si sévère.</p>

<p><strong>« Revalorisation réellement pratiquée » est la seule ligne qui ne soit
pas une hypothèse</strong> : c'est le coefficient que les arrêtés annuels ont
appliqué aux salaires portés au compte, celui dont le système 1 se sert pour
calculer le ${g.terme("salaire de référence")}. Il vaut
<strong>×${g.nombre(revalPratiquee, 0)}</strong> sur la période, près de cinq
fois les prix, parce que le régime général a revalorisé sur les SALAIRES
jusqu'en 1986 et sur les prix seulement depuis 1987. C'est donc elle, plutôt que
« Indexation sur les prix », qui neutralise la question de l'indexation quand on
veut isoler l'effet propre des comptes notionnels. Sur une carrière
(un salarié du privé non cadre au salaire moyen, entré à 20 ans et parti
à 62), la correction reste modeste : +5,0 points pour la génération 1920,
+0,0 pour 1945, -0,5 pour 1958. Les cotisations se concentrent sur les dernières années, là où
les deux règles coïncident.</p>

<p><strong>« Masse salariale » est ce que la théorie désigne.</strong> En
répartition, le rendement qu'un système peut servir sans changer son taux est la
croissance de son assiette, le salaire moyen multiplié par l'emploi salarié
(Samuelson 1958, Aaron 1966). C'est le taux d'indexation des comptes notionnels
suédois, italiens, polonais et lettons, à des variantes près. Sur 1941-2025 il
vaut ×${g.nombre(masseSalariale, 0)}, onze fois les prix : l'emploi salarié a
doublé depuis 1950, et cette croissance-là s'ajoute chaque année à celle des
salaires. Une réserve : ce rendement est celui du système ENTIER, alors que les
le système 2 ne porte au compte que la part salariale de la cotisation.
C'est au système 3 qu'il faut le comparer.</p>

<p><strong>Le PIB nominal</strong> pousse la même idée à l'assiette la plus
large : il gagne ce que la masse salariale perd quand la valeur ajoutée se
déplace vers les revenus non salariaux. La dernière ligne y ajoute un
<strong>lissage sur cinq ans</strong>, comme le fait l'Italie.</p>

<p><strong>Le lissage est un réglage à part</strong>, qui s'ajoute à n'importe
quelle règle : une moyenne glissante du taux qu'elle produit. Il vise moins
le niveau que la <strong>loterie de
cohorte</strong> : sur le PIB nominal brut, une cotisation de
${ANNEE_COTISATION_LOTERIE} vaut ${loterie.get("1|2019")} à une liquidation de 2019 et
${loterie.get("1|2020")} en 2020 : attendre un an fait <em>perdre</em>, parce que
l'année traversée s'est mal passée. Lissée sur cinq ans, elle vaut
${loterie.get("5|2019")} puis ${loterie.get("5|2020")} : le trou de 2020 est absorbé par
les quatre années qui l'entourent au lieu d'être porté en entier par qui a eu le
tort de liquider cette année-là. Sur 1950-2025, le PIB nominal brut compte deux
années où liquider plus tard rapporte moins ; lissé sur trois ou cinq ans,
aucune.</p>

<p class="discret">Deux réserves pour lire le tableau. Sur quatre-vingts ans, une
moyenne glissante n'est pas neutre : elle mesure la croissance depuis une base
reculée d'environ la moitié de la fenêtre, ce qui gonfle le cumul d'une
vingtaine de pour cent à cinq ans, sans qu'aucune série ait changé ; sur une
carrière, l'écart reste d'un à deux points. Et la règle italienne n'est reprise
ici que par son taux, non par le reste du système italien. Enfin, le minimum
n'est pas la seule statistique possible sur ces trois séries : la
<strong>médiane</strong> est un taux nominal trois années sur quatre, donc elle
suit les prix et cesse d'être une règle d'austérité ; la <strong>moyenne</strong>
est plus sévère que les prix, parce qu'elle incorpore un tiers de productivité
réelle <em>chaque</em> année. Les deux sont dans les options.</p>`);
}

/** Ce que l'étalon reproduit du droit en vigueur. */
function methodeDroitPositif() {
  return g.depliant("Ce que le système 1 applique du droit en vigueur", `
<p>L'étalon ne vaut que par ce qu'il reproduit. Il applique la
${g.terme("décote")} et la ${g.terme("surcote")}, la proratisation par la
${g.terme("durée", "durée d'assurance")}, le ${g.terme("salaire de référence")}
de chaque régime (sur ses seules années, jamais sur toute la carrière), et cinq
paramètres lus à la génération plutôt qu'à l'année de liquidation : durée requise,
âge légal, âge d'annulation de la décote, coefficient de minoration, nombre
d'années retenues au salaire de référence.</p>
<p>Il applique aussi, dans l'ordre où le droit les applique, les avantages non
contributifs que la carrière suffit à déterminer :</p>
<ul>
  <li><strong>l'assurance vieillesse des parents au foyer</strong>, qui porte au
  compte un salaire forfaitaire égal au SMIC — c'est ce qui la distingue d'une
  période assimilée, laquelle valide des trimestres sans jamais ajouter de
  salaire ;</li>
  <li><strong>les trimestres accordés au titre des enfants</strong>, datés : la
  majoration de durée d'assurance du régime général et des régimes alignés naît
  en 1972 à un an par enfant, passe à deux ans en 1975 et va à la mère ; la
  fonction publique et les régimes spéciaux servent leur bonification, un an par
  enfant né avant 2004 et deux trimestres pour les enfants nés depuis. Ils sont
  attribués à l'intérieur d'un régime, jamais au-dessus des régimes : ils comptent donc aussi dans
  sa proratisation ;</li>
  <li><strong>le minimum contributif</strong>, réservé aux pensions liquidées au
  taux plein, proratisé par la durée d'assurance acquise dans le régime, et sa
  majoration au titre des périodes cotisées proratisée par la seule durée
  cotisée, puis écrêté quand le total des pensions personnelles dépasse le
  plafond de l'article L. 173-2 ;</li>
  <li><strong>le minimum garanti</strong> de la fonction publique, barème en
  escalier sur la durée de services — 57,5 % de la référence à quinze ans, 95 %
  à trente, la totalité à quarante ;</li>
  <li><strong>la surcote parentale</strong>, créée par la loi du 14 avril 2023 :
  1,25 % par trimestre acquis entre 63 ans et l'âge légal, quatre au plus, à qui
  justifie de la durée requise à 63 ans et détient un trimestre de majoration
  pour enfants. C'est la contrepartie du recul de l'âge légal, et elle se cumule
  avec la surcote ordinaire, qui ne compte qu'au-delà de cet âge ;</li>
  <li><strong>la majoration pour trois enfants</strong>, calculée sur le montant
  déjà relevé par les minima, et plafonnée en euros à la complémentaire ;</li>
  <li><strong>le minimum vieillesse</strong>, allocation différentielle servie à
  partir de 65 ans sous le barème d'une personne seule. Ce n'est pas une
  pension : elle apparaît toujours comme une ligne séparée de la cascade.</li>
</ul>
<p>Deux barèmes propres complètent l'ensemble : la décote de la fonction
publique, dont le coefficient et l'âge d'annulation montent en charge de 2006 à
2020 et dont l'âge d'annulation est la limite d'âge du grade et non 67 ans ; et
la garantie minimale de points de l'Agirc, 120 points par an de 1989 à 2018
même quand la tranche B est nulle.</p>
<p>Enfin, le système dit si le droit <strong>ouvre</strong> la liquidation
demandée : âge légal du régime, ou départ anticipé pour carrière longue. Quand
il ne l'ouvre pas, le montant reste calculé, parce qu'il faut comparer les
quatre systèmes sur la même carrière, mais la page le signale : il ne décrit alors
aucune pension que le système actuel servirait.</p>`);
}

/** Ce que les scénarios notionnels retirent, et la seule exception. */
function methodeSuppressions() {
  return g.depliant("Ce que les comptes notionnels suppriment", `
<p>Le principe « seules les cotisations comptent » est appliqué sans exception :
ni minimum contributif, ni minimum garanti, ni ASPA, ni majoration pour enfants,
ni majoration de durée d'assurance, ni AVPF, ni bonifications, ni catégorie
active, ni périodes assimilées, ni réversion, ni décote ni surcote. Le
système 1 les conserve tous, puisqu'il décrit le droit en vigueur.</p>
<p>Une exception : le <strong>système 4</strong>, la
<a href="${g.lien("/")}">proposition du Parti libéral français</a>, remet un
plancher, et un seul. C'est le système 3, à deux différences près : un taux
unique de 18 % pour tous à compter de la bascule, salariale et patronale
additionnées, les années antérieures restant portées au compte aux taux réels ;
et une garantie vieillesse, différentielle et servie à 65 ans comme l'ASPA, mais
individualisée — 800 € par personne, plus 250 € pour qui vit seul, en euros de
2026 — et financée par l'impôt. La page de simulation en détaille chaque étape,
et la page Coût compte cette part à part.</p>`);
}

/** La fusion des régimes, et comment une carrière se décrit. */
function methodeCarriere(contexte) {
  const fusionne = contexte.simulateur().regimeFusionne;
  const nombreRegimes = contexte.simulateur().catalogue.taille;
  return g.depliant("Comment une carrière est décrite", `
<h4>La fusion des régimes</h4>
<p>À compter de l'année de bascule, les ${nombreRegimes} régimes du catalogue
sont remplacés par un régime unique dont chaque paramètre est le plus
défavorable de l'ensemble : ouverture à ${age(fusionne.age_ouverture)}, taux
plein à ${age(fusionne.age_taux_plein)},
${fusionne.duree_requise_trimestres} trimestres requis, cotisation de
${g.pourcentage(fusionne.taux_cotisation_retraite, false, 2)} sur assiette
déplafonnée.</p>

<h4>Une carrière, plusieurs métiers</h4>
<p>Une carrière se décrit comme une <strong>suite de métiers</strong> : chacun
porte un statut d'affiliation, un âge de début et un niveau de revenu, et court
jusqu'au début du suivant. Chaque changement fait passer d'un régime à un
autre, donc d'un taux, d'une assiette et d'un barème à un autre.</p>
<p>Deux conventions le bornent, imposées par la maille des données. Le
<strong>profil de carrière</strong> vaut pour la vie active entière : c'est une
progression de carrière, quel que soit l'emploi, et le niveau propre à chaque métier s'y
superpose au lieu de la remettre à zéro. Et une <strong>année civile n'a qu'un
statut</strong> : l'année d'un changement revient au métier qui en occupe le
plus de mois, et à égalité à celui qui l'ouvre, tandis que le revenu porté au
compte reste la somme de ce que les deux ont réellement payé.</p>
<p>Un statut ne se déclare qu'<strong>aux dates où son régime recrutait</strong>.
Le menu date chacun (« depuis 1977 » pour l'artiste-auteur, « recrutés avant
septembre 2010 » pour le mineur) et grise ceux que l'entrée saisie ferme. La
date opposée est celle de l'entrée dans le métier, au mois près : qui est entré
à la RATP en octobre 2022 garde son régime, fermé aux recrutés du
1<sup>er</sup> septembre 2023. C'est la clause du grand-père.</p>`);
}

/** Brut et pas net, multiples du salaire moyen, et le périmètre. */
/**
 * Comment ce site est construit, et comment on le vérifie : l'argument de
 * confiance d'un public technique, là où le lecteur est déjà dans le détail.
 * Voir `_methode_construction` dans `web/pages.py`.
 */
function methodeConstruction() {
  return g.depliant("Comment ce site est construit, et comment on le vérifie", `
<p>Le modèle de référence est écrit en Python, dans
<a href="${g.DEPOT}/tree/main/src">le dossier <code>src/</code> du dépôt</a> : c'est
lui qui fait foi, et c'est lui qui est testé contre les sources — les textes,
les barèmes, et des calculateurs extérieurs comme OpenFisca, qui servent
d'oracle au système 1.</p>
<p>Ce que vous lisez ici est un <strong>portage en JavaScript</strong> de ce
modèle, sans aucune bibliothèque, qui tourne entièrement dans votre navigateur
: rien de ce que vous saisissez n'est envoyé nulle part. Le portage ne s'écarte
pas du modèle, et ce n'est pas une promesse : des centaines de carrières
témoins (chaque statut d'affiliation, à six générations) sont calculées par
les deux, et comparées nombre par nombre ; chaque page du site est rendue par
les deux, et comparée caractère par caractère. Toute divergence fait échouer
les tests.</p>
<p>Les données que le site charge sont produites par un script à partir des
mêmes fichiers que le modèle, et un test refuse un paquet périmé. Les séries
sont recontrôlées contre le fichier de l'institution qui les produit — la
page <a href="${g.lien("/donnees")}">Données</a> dit lesquelles, et à quelle
date.</p>
<p class="discret"><a href="${g.DEPOT}">Le dépôt</a> ·
<a href="${g.DEPOT}/blob/main/README.md">ce qu'il contient, et combien de tests
le tiennent</a> · <a href="${g.DEPOT}/tree/main/tests">les tests</a></p>`);
}

function methodeUnites() {
  return g.depliant("En quelles unités, et sur quel périmètre", `
<h4 id="unites">Brut, et pas net</h4>
<p>Tout ce que le modèle manipule est <strong>brut</strong> : le revenu saisi,
les cotisations versées, le capital notionnel, les quatre pensions. « Brut » a ici
le sens des comptes nationaux : <em>salaires et traitements bruts</em> (D11)
rapportés à l'emploi salarié intérieur. C'est-à-dire <strong>avant</strong>
cotisations salariales, CSG, CRDS et impôt sur le revenu, et <strong>hors</strong>
cotisations patronales. C'est l'assiette sur laquelle les régimes appellent leurs
cotisations, donc la seule grandeur qu'un compte notionnel puisse enregistrer.
Le simulateur sait néanmoins AFFICHER des nets : une bascule convertit les
pensions et les salaires au moment de les écrire, le calcul restant brut de bout
en bout. Le taux de remplacement suit cette bascule — un brut sur un brut, plus
bas qu'un taux calculé sur des nets, ou un net sur un net.</p>
<p>Le revenu d'activité se saisit en <strong>euros d'aujourd'hui</strong>. Le
modèle, lui, ne connaît que le <strong>multiple du salaire moyen</strong>, seule
unité qui garde son sens sur quatre-vingts ans. La page fait donc une division,
et une seule : <code>niveau = revenu mensuel × 12 ÷ salaire moyen annuel</code>.
Ce niveau suit ensuite le salaire moyen d'une année à l'autre, déformé par le
profil de carrière : le revenu saisi est celui du milieu de carrière. Un lien
sous les métiers bascule entre les deux unités, montants convertis.</p>
<p>Reste que les comptes nationaux ne publient que des <em>taux de croissance</em>
du salaire moyen. Les niveaux en sont reconstitués à partir d'un point
d'ancrage — <strong>40 000 € bruts annuels en 2024</strong> —, paramètre
documenté et non donnée certifiée. Il déplace proportionnellement tous les
revenus reconstitués, donc toutes les pensions, mais il est sans effet sur les
<strong>rapports</strong> entre scénarios, qui sont l'objet du modèle.</p>

<h4>Périmètre</h4>
<p>Origine 1941 (allocation aux vieux travailleurs salariés), premier dispositif
où les cotisations des actifs financent les prestations des retraités. Les
assurances sociales de 1930, en capitalisation individuelle, et le RAFP sont
isolés dans un compartiment séparé, jamais converti.</p>
<p class="discret"><a href="${g.DEPOT}/blob/main/docs/methodologie.md">Méthodologie
complète</a> · <a href="${g.DEPOT}/blob/main/docs/limites.md">Limites
connues</a></p>`);
}

/** Libellés des familles de régimes, tels que la page « Données » les affiche. */
const FAMILLES_INVENTAIRE = {
  base_prive: "base, privé",
  complementaire_prive: "complémentaire, privé",
  fonction_publique: "fonction publique",
  special: "spécial",
  non_salarie: "non-salariés",
  agricole: "agricole",
  liberal: "libéral",
  additionnel_capitalise: "additionnel, capitalisé",
};

/**
 * Les cinq couvertures, dans l'ordre du menu de filtre : la clé de
 * l'inventaire, ce qu'on lit dans la cellule, et le pluriel de la phrase de
 * compte. Une couverture qu'aucune ligne ne porte ne s'affiche nulle part.
 */
/** Les quatre niveaux de fiabilité, du meilleur au moins bon. */
const NIVEAUX_FIABILITE = ["certifiee", "haute", "moyenne", "estimee"];

const COUVERTURES_INVENTAIRE = [
  ["modelise", "modélisé", "modélisés"],
  ["partiel", "partiel", "partiels"],
  ["a_modeliser", "à modéliser", "à modéliser"],
  ["routage", "porté par un statut", "portés par un statut"],
  ["hors_champ", "hors champ", "hors champ"],
];

function periodeInventaire(creation, fermeture, extinction) {
  if (creation === null || creation === undefined) {
    return "—";
  }
  if (extinction !== null && extinction !== undefined) {
    return `${creation}-${extinction}`;
  }
  if (fermeture !== null && fermeture !== undefined) {
    return `depuis ${creation}, fermé en ${fermeture}`;
  }
  return `depuis ${creation}`;
}

/**
 * Tous les régimes, calculés ou non — la liste qui manquait au dépôt.
 *
 * UNE SEULE TABLE, et non cinq, qui se filtre et se trie sur place : le
 * comportement est dans `index.html`, en écoute déléguée ; sans lui, la table
 * se lit entière, dans l'ordre du fichier. Voir `_inventaire_section` dans
 * `web/pages.py`. `catalogue` donne la fiabilité des fiches calculées.
 */
function inventaireSection(lignes, catalogue) {
  const fiabilites = new Map();
  for (const regime of catalogue) {
    fiabilites.set(regime.code, nomFiabilite(regime.fiabilite));
  }
  const comptes = {};
  for (const [cle] of COUVERTURES_INVENTAIRE) {
    comptes[cle] = lignes.filter((l) => l.couverture === cle).length;
  }
  const phrase = COUVERTURES_INVENTAIRE
    .filter(([cle]) => comptes[cle])
    .map(([cle, , pluriel]) => `${comptes[cle]} ${pluriel}`).join(", ");
  const lecture = Object.fromEntries(
    COUVERTURES_INVENTAIRE.map(([cle, singulier]) => [cle, singulier]),
  );
  const cellule = (texte) => (texte ? echapper(texte) : "—");

  const corps = [];
  const attributs = [];
  for (const ligne of lignes) {
    corps.push([
      echapper(ligne.nom),
      echapper(FAMILLES_INVENTAIRE[ligne.famille]),
      echapper(lecture[ligne.couverture]),
      cellule(g.fiabiliteEnClair(fiabilites.get(ligne.code) ?? "")),
      echapper(periodeInventaire(ligne.creation, ligne.fermeture, ligne.extinction)),
      cellule((ligne.statuts || []).join(", ")),
      cellule(ligne.couverture === "hors_champ" ? ligne.raison_hors_champ : ligne.manque),
    ]);
    attributs.push({
      "data-famille": ligne.famille,
      "data-couverture": ligne.couverture,
      "data-fiabilite": fiabilites.get(ligne.code) ?? "",
    });
  }

  const filtres = '<div class="filtres" role="group" aria-label="Filtrer les régimes" '
    + 'data-cible="inventaire">'
    + g.champ("inventaire-recherche", "Chercher un régime", "",
      "un nom, un statut, une caisse…", "search",
      { data_filtre: "texte", autocomplete: "off" })
    + g.liste("inventaire-famille", "Famille",
      [["", "Toutes"]].concat(Object.entries(FAMILLES_INVENTAIRE)), "",
      "", { data_filtre: "famille" })
    + g.liste("inventaire-couverture", "Dans le modèle",
      [["", "Tous"]].concat(COUVERTURES_INVENTAIRE
        .filter(([cle]) => comptes[cle])
        .map(([cle, singulier]) => [cle, singulier])), "",
      "", { data_filtre: "couverture" })
    + g.liste("inventaire-fiabilite", "Fiabilité de la fiche",
      [["", "Toutes"]].concat(NIVEAUX_FIABILITE
        .filter((niveau) => [...fiabilites.values()].includes(niveau))
        .map((niveau) => [niveau, g.fiabiliteEnClair(niveau)])), "",
      "", { data_filtre: "fiabilite" })
    + "</div>"
    + '<p class="compte discret" aria-live="polite" data-compte-de="inventaire" '
    + `data-unite="régimes">${lignes.length} régimes</p>`;
  const table = g.tableau(
    ["Régime", "Famille", "Dans le modèle", "Fiabilité", "Période", "Statuts",
      "Ce qui manque, ou pourquoi"],
    corps,
    ["", "texte", "texte", "texte", "texte", "texte", "texte long"],
    `Les ${lignes.length} régimes de l'inventaire`,
    true,
    attributs,
    true,
    "inventaire",
  );
  return g.depliant(`Les ${lignes.length} régimes, un par un`, `
<p>L'inventaire compte ${lignes.length} régimes de retraite obligatoires, actuels
et disparus : ${phrase}. Il fait foi dans
<a href="${g.DEPOT}/blob/main/data/reference/regimes/inventaire.yaml">inventaire.yaml</a>,
où chaque ligne cite son texte fondateur, et un test le tient aligné sur le
catalogue : une fiche sans ligne d'inventaire, ou une ligne qui prétend calculer
ce qu'aucune fiche ne calcule, fait échouer les tests. Un régime « partiel » est
calculé, mais un étage, un barème ou une période lui manque, et la dernière
colonne dit lequel ; un régime « à modéliser » n'a pas de fiche ; une ligne
« portée par un statut » n'est pas un régime mais une affiliation (l'élu
local, le micro-entrepreneur), que le statut nommé route vers les régimes du
catalogue. La fiabilité est celle de la fiche du catalogue, quand il y en a
une. Cherchez, filtrez, ou triez en cliquant un en-tête de colonne.</p>
${filtres}
${table}`, "donnees-inventaire");
}

/**
 * Ce que valent les chiffres du site.
 *
 * LA PAGE RÉPOND À UNE SEULE QUESTION, ET ELLE Y RÉPOND EN TROIS CHIFFRES :
 * combien de valeurs ont été recontrôlées contre le fichier de l'institution qui
 * les produit, combien de régimes sont recensés, et à quelle date. Tout le reste
 * est une pièce justificative, et une pièce justificative se range.
 *
 * Elle pesait 5 851 mots et huit tableaux dépliés. Rien n'en est retiré : ce qui
 * rend un chiffre vérifiable doit rester lisible, et l'est, à un clic.
 */
function donnees(contexte) {
  const simulateur = contexte.simulateur();
  const macro = simulateur.macro;

  const periodes = [];
  for (let debut = 1940; debut < 2030; debut += 10) {
    const fin = debut + 9;
    periodes.push([
      `${debut}-${fin}`,
      echapper(g.fiabiliteEnClair(nomFiabilite(macro.inflation.fiabiliteMinimaleSur(debut, fin)))),
      echapper(g.fiabiliteEnClair(nomFiabilite(macro.salaire_moyen.fiabiliteMinimaleSur(debut, fin)))),
      echapper(g.fiabiliteEnClair(nomFiabilite(macro.productivite.fiabiliteMinimaleSur(debut, fin)))),
      `<strong>${echapper(g.fiabiliteEnClair(nomFiabilite(macro.fiabiliteSur(debut, fin))))}</strong>`,
    ]);
  }

  const parNiveau = new Map();
  for (const regime of simulateur.catalogue) {
    const niveau = nomFiabilite(regime.fiabilite);
    if (!parNiveau.has(niveau)) {
      parNiveau.set(niveau, []);
    }
    parNiveau.get(niveau).push(regime.code);
  }
  const regimes = ["certifiee", "haute", "moyenne", "estimee"]
    .filter((niveau) => parNiveau.has(niveau))
    .map((niveau) => [
      niveau,
      String(parNiveau.get(niveau).length),
      echapper([...parNiveau.get(niveau)].sort().join(", ")),
    ]);

  const journal = contexte.paquet.certification || {};
  const series = journal.series || {};
  const certifications = Object.entries(series)
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([nom, trace]) => [
      echapper(nom), String(trace.valeurs),
      echapper(g.fiabiliteEnClair(trace.niveau ?? "certifiee")), echapper(trace.verifiee_le),
      echapper(trace.source),
    ]);
  // La table des séries se cherche et se trie comme l'inventaire : c'est une
  // base, pas un article.
  const niveauxSeries = new Set(Object.values(series).map((trace) => trace.niveau ?? "certifiee"));
  const attributsSeries = Object.entries(series)
    .sort(([a], [b]) => (a < b ? -1 : a > b ? 1 : 0))
    .map(([, trace]) => ({ "data-niveau": trace.niveau ?? "certifiee" }));
  const filtresSeries = certifications.length
    ? '<div class="filtres" role="group" aria-label="Filtrer les séries" '
      + 'data-cible="series">'
      + g.champ("series-recherche", "Chercher une série", "",
        "un nom, une source…", "search",
        { data_filtre: "texte", autocomplete: "off" })
      + g.liste("series-niveau", "Niveau",
        [["", "Tous"]].concat(NIVEAUX_FIABILITE
          .filter((niveau) => niveauxSeries.has(niveau))
          .map((niveau) => [niveau, g.fiabiliteEnClair(niveau)])), "",
        "", { data_filtre: "niveau" })
      + "</div>"
      + '<p class="compte discret" aria-live="polite" data-compte-de="series" '
      + `data-unite="séries">${certifications.length} séries</p>`
    : "";
  const valeursCertifiees = Object.values(series)
    .reduce((somme, trace) => somme + Number(trace.valeurs), 0);
  const inventaire = (contexte.paquet.inventaire || []).length;
  // Ce que les fiches SOUTIENNENT : la plus ancienne relecture, la plus récente.
  const datesVerification = Object.values(series).map((trace) => trace.verifiee_le).sort();

  let reperes;
  let bandeau;
  if (certifications.length) {
    reperes = g.fiche(
      "Valeurs recontrôlées contre leur source",
      g.nombre(valeursCertifiees, 0),
      `sur ${certifications.length} séries ; la vérification la plus ancienne `
      + `remonte au ${dateEnClair(datesVerification[0])}`,
    ) + g.fiche(
      "Régimes recensés", String(inventaire),
      `dont ${simulateur.catalogue.taille} calculés`,
    ) + g.fiche(
      "Institutions citées", "28",
      "INSEE, COR, DREES, Cnav, Légifrance…",
    );
    bandeau = `<div class="note"><strong>Les séries macroéconomiques sont
certifiées de 1950 à 2025</strong>, les tables de mortalité sont celles
réellement observées depuis 1986, et le plafond de la Sécurité sociale remonte à
1931 daté décret par décret. Le tout est recontrôlé contre les sources, série
par série : la vérification la plus ancienne remonte au
${dateEnClair(datesVerification[0])}, la plus récente au
${dateEnClair(datesVerification[datesVerification.length - 1])}. Ce qui précède 1950 et les
paramètres propres à chaque régime restent saisis à la main : les
<em>niveaux</em> de pension des carrières les plus anciennes gardent une marge,
les <em>écarts entre scénarios</em>, qui sont l'objet du modèle, sont plus
robustes encore.</div>`;
  } else {
    reperes = g.fiche(
      "Valeurs recontrôlées contre leur source", "0",
      "la certification n'a pas encore été lancée",
    ) + g.fiche(
      "Régimes recensés", String(inventaire),
      `dont ${simulateur.catalogue.taille} calculés`,
    ) + g.fiche(
      "Institutions citées", "28",
      "INSEE, COR, DREES, Cnav, Légifrance…",
    );
    bandeau = `<div class="note avertissement"><strong>Aucune série n'a
encore été recontrôlée contre sa source.</strong> Lancer <code>scripts/fetch/</code>
puis <code>scripts/verifier_donnees.py --appliquer</code>.</div>`;
  }

  const depliantSeries = g.depliant("Quelles séries, et contre quelle source", `
${filtresSeries}
${g.tableau(["Série", "Valeurs", "Niveau", "Vérifiée le", "Source"], certifications,
    ["", "nombre", "", "texte date", "texte"],
    "Séries recontrôlées contre la source qui les produit", true,
    attributsSeries, true, "series")}
<p class="discret">Une valeur n'est « certifiée » que si elle a été confrontée au
fichier téléchargé depuis le <em>producteur</em> de la donnée. Une transcription
tierce, même sourcée et reprise automatiquement, plafonne à « haute ». Hors de
cette liste : les séries d'avant 1950, les taux de cotisation d'avant 1967, le
plafond d'avant 2002 et le point d'indice de la fonction publique, repris
d'OpenFisca, les montants servis du minimum contributif, du minimum garanti et
du minimum vieillesse — transcrits de leur publication, et préférés à toute
projection parce qu'ils disent ce qui a été payé —, et les âges, durées et
coefficients propres à chaque régime, repris des textes.</p>`, "donnees-series");

  const depliantFiabilite = g.depliant("Ce que vaut chaque décennie, et chaque régime", `
<h4>Les séries macroéconomiques, décennie par décennie</h4>
${g.tableau(
    ["Période", "Inflation", "Salaire moyen", "Productivité", "Ensemble"],
    periodes,
    ["", "", "", "", ""],
    "Fiabilité des séries macroéconomiques, décennie par décennie",
    true,
  )}
<p class="discret">Une projection ne se fait jamais passer pour une observation :
au-delà de la dernière année observée, la fiabilité retombe à « estimée ».</p>

<h4>Les ${simulateur.catalogue.taille} régimes calculés</h4>
${g.tableau(["Niveau", "Nombre", "Régimes"], regimes, ["", "nombre", "texte"],
    "Nombre de régimes par niveau de fiabilité", true)}`, "donnees-fiabilite");

  const depliantSources = g.depliant("D'où viennent les chiffres, et comment on arbitre", `
<p>Trente institutions sont recensées dans
<a href="${g.DEPOT}/blob/main/data/sources.yaml">data/sources.yaml</a> : INSEE,
COR, Comité de suivi des retraites, DREES, CNAV, Service des retraites de l'État,
Caisse des dépôts, Direction de la Sécurité sociale, Cour des comptes,
Agirc-Arrco, Assemblée nationale, Union Retraite, CCMSA, CNAVPL, CNBF, DGAFP,
Direction du Budget, ERAFP, Ircantec, caisses des régimes spéciaux, Urssaf,
Légifrance, INED, Eurostat, OCDE, OpenFisca-France, IPP, CEPII, Banque centrale
européenne, Observatoire des produits d'épargne financière.</p>
<p><strong>Les deux sources du pilier capitalisé.</strong> Les taux auxquels il
place sont la courbe zéro-coupon des souverains les mieux notés de la zone euro,
que la <strong>Banque centrale européenne</strong> publie chaque jour ouvré :
c'est le producteur, la récupération est automatique, et les trente maturités
sont recontrôlées comme n'importe quelle série
(<code>courbe_taux_sans_risque</code> dans le tableau ci-dessus). Les frais de
l'enveloppe sont les moyennes 2025 des plans d'épargne retraite individuels,
mesurées par l'<strong>Observatoire des produits d'épargne financière</strong> —
le CCSF, à la Banque de France — sur les remises de l'ACPR. Ces trois valeurs
sont <code>haute</code> et non <code>certifiee</code> : le rapport est un PDF que
le dépôt ne sait pas récupérer automatiquement, et la règle du manifeste plafonne
à ce niveau ce qui n'a pas été confronté au document du producteur.</p>
<p>Chaque valeur porte son niveau de fiabilité, <code>certifiee</code>,
<code>haute</code>, <code>moyenne</code> ou <code>estimee</code>, et la fiabilité
d'un résultat est celle de son maillon le plus faible.</p>
<p>Quand deux institutions publient le même chiffre, quatre critères disent
laquelle aller chercher : le <strong>producteur</strong> prime sur le repreneur,
l'<strong>observé</strong> sur le projeté, le <strong>montant servi</strong> sur
le montant calculé, le <strong>recontrôlable</strong> sur le saisi. Ce n'est pas
un classement d'institutions mais de natures de données : l'INSEE pour ce qu'il
mesure, le COR pour ce qu'il décide.</p>
<p class="discret"><a href="${g.DEPOT}/blob/main/docs/limites.md">Limites
détaillées</a></p>`, "donnees-sources");

  // La réutilisation se range ici plutôt que sur une page à elle : qui vient
  // chercher d'où sort un chiffre est celui-là même qui s'apprête à le
  // reprendre, et la règle de citation ne se comprend qu'à côté de la liste des
  // producteurs. Ce n'est pas une mention légale — l'éditeur du site d'accueil
  // porte les siennes —, c'est la licence de ce dépôt.
  const depliantReutilisation = g.depliant("Licences et réutilisation", `
<p>Le code du modèle et du site est publié sous
<a href="${g.DEPOT}/blob/main/LICENSE">licence Apache 2.0</a> : réutilisable, y
compris commercialement, à condition d'en conserver la mention. Les pictogrammes
viennent de <a href="https://lucide.dev">Lucide</a> (licence ISC) ; ils sont
recopiés dans le dépôt, et le site ne les charge donc chez personne.</p>
<p>Les infographies, graphiques, tableaux et textes que le site affiche sont
sous licence <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.fr">Creative
Commons Attribution – Partage dans les mêmes conditions 4.0</a> (CC BY-SA) :
libres de reprise et d'adaptation, à condition de citer ce site et d'en indiquer
l'adresse, de signaler les modifications, et de republier toute version modifiée
sous la même licence. Le nom et le logo du Parti Libéral Français ne sont
couverts par aucune de ces licences.</p>
<p>Les données, elles, ne sont pas la propriété de l'éditeur. Les séries
françaises reprises ici — INSEE, DREES, DILA et Légifrance, Service des
retraites de l'État, caisses — sont des informations publiques, réutilisables
au titre des articles L321-1 et suivants du code des relations entre le public
et l'administration, le plus souvent sous Licence Ouverte (Etalab). Eurostat et
l'OCDE posent leurs propres conditions de réutilisation. Toutes imposent la
citation de la source : chaque valeur du dépôt porte la sienne dans
<a href="${g.DEPOT}/blob/main/data/sources.yaml">data/sources.yaml</a>.
<strong>Qui reprend un chiffre d'ici cite le producteur, pas ce site.</strong></p>`, "donnees-reutilisation");

  const detail = depliantSeries + depliantFiabilite
    + inventaireSection(contexte.paquet.inventaire || [], simulateur.catalogue)
    + depliantSources + depliantReutilisation;

  const tete = g.affiche(
    "Les données",
    "Rien ici n'est "
    + '<span class="cle-texte">à croire sur parole.</span>',
    "Chaque série est recontrôlée, automatiquement, contre le fichier de "
    + "l'institution qui la produit. Ce qui ne l'est pas est dit.",
  );

  return `
${tete}

<div class="note resume"><strong>En clair.</strong> Les chiffres de ce site
viennent des institutions qui les produisent : l'INSEE pour les prix et les
salaires, le Conseil d'orientation des retraites pour les comptes, les caisses
pour leurs barèmes. Un programme les retélécharge et les compare, valeur par
valeur, à ce que le site utilise. Ce qui n'a pas pu être vérifié ainsi est
marqué comme tel, et les règles de chaque régime sont lues dans les textes.
Cette page dit, série par série et régime par régime, ce qui est vérifié et ce
qui ne l'est pas.</div>

<div class="fiches reperes">${reperes}</div>

${g.plan(detail, "/donnees")}

${bandeau}

<h2>Le détail</h2>

${detail}
`;
}

/**
 * Mentions légales, données personnelles, accessibilité.
 *
 * Trois obligations distinctes tiennent sur une seule page parce qu'un lecteur
 * qui cherche l'une y cherche souvent les autres : dire qui édite le site et
 * qui l'héberge (LCEN, art. 6-III), dire ce qu'on fait des données — ici,
 * rien, et c'est précisément ce qu'il faut écrire —, et déclarer où en est
 * l'accessibilité. Les champs que l'éditeur doit renseigner lui-même sont
 * marqués en clair : mieux vaut un trou signalé qu'une mention inventée.
 *//**
 * Le programme du Parti libéral français pour les retraites.
 *
 * C'est l'accueil du site, et la seule page qui ne calcule rien pour elle-même :
 * elle expose une proposition, et renvoie aux cinq autres pour les chiffres.
 * Elle n'appelle donc ni `contexte.cout()` ni aucune simulation — deux secondes
 * de calcul sur la première page ouverte seraient deux secondes de page blanche.
 *
 * ELLE SE LIT EN UNE MINUTE. C'est la contrainte, et elle tient à ce qu'est
 * cette page : un programme politique, lu par quelqu'un qui n'a pas demandé à le
 * lire. Quatre propositions, un tableau qui les oppose terme à terme au système
 * actuel, et un lien pour vérifier. Le reste est replié : présent pour qui veut,
 * hors du chemin pour qui n'a que trente secondes.
 */
function programme(contexte) {
  const base = contexte.base;
  const simulateur = contexte.simulateur();
  const regimes = simulateur.catalogue.taille;
  const inventaire = (contexte.paquet.inventaire || []).length;
  const comptes = contexte.comptes();
  const anneeSolde = comptes.derniereAnneeObservee;
  const taux = g.pourcentage(base.taux_cotisation_liberal, false, 0);
  const plancher = g.euros(base.garantie_vieillesse_mensuelle);

  const differences = g.tableau(
    ["", "Aujourd'hui", "Avec notre programme"],
    [
      ["Ce qui ouvre un droit",
        `des ${g.terme("trimestres")}, et ${regimes} barèmes différents`,
        "une cotisation versée, et elle seule"],
      ["Ce qui fait le montant",
        `vos ${g.terme("25 meilleures années", "salaire de référence")}, `
        + "un taux, une durée",
        "votre compte, divisé par votre espérance de vie"],
      ["Partir un an plus tôt",
        `une ${g.terme("décote")}, dont le barème change à chaque réforme`,
        "un an de cotisation en moins, un an de pension en plus"],
      ["Changer de métier",
        "changer de régime, et de règle de calcul",
        "rien : le compte est le même"],
      ["Savoir où vous en êtes",
        "un relevé en trimestres et en points",
        "un solde, en euros"],
      ["Tenir l'équilibre",
        "une réforme, tous les huit ans en moyenne",
        "un chiffre publié chaque année"],
      // La transmission est le seul point où les deux systèmes ne promettent
      // pas la même NATURE de droit : une pension s'éteint, un capital se
      // lègue. Le dire ici, et non dans un dépliant.
      ["Si vous mourez avant la retraite",
        "vos cotisations restent au système",
        "le capital de la part capitalisée revient à vos héritiers"],
    ],
    ["", "texte", "texte"],
    "Le système actuel et notre programme, terme à terme",
    true,
  );

  // Les dépliants sont bâtis à part, comme en Python, pour que les deux
  // portages se lisent de la même façon.
  const depliantActuel = g.depliant("Pourquoi le système actuel ne va pas", `
<p>La retraite française ? Un empilement de régimes, plus qu'un système.
Ce site en <a href="${g.lien("/donnees")}">recense ${inventaire}</a>, actuels et
disparus, et en calcule ${regimes}. Chacun a son âge de départ, son assiette, son
taux, sa durée exigée et son minimum.</p>
<ul class="serree">
  <li><strong>Illisible, d'abord.</strong> Le montant dépend de sept règles qui ne
  se lisent sur aucune fiche de paie. Personne, pas même les caisses, ne sait
  dire à un actif ce qu'il a acquis, autrement qu'en trimestres et en points.</li>
  <li><strong>Inégal, ensuite.</strong> À salaire et à durée égaux, la pension
  change selon le statut, et l'écart ne vient d'aucune différence de cotisation.
  <a href="${g.lien("/cas-types")}">Treize carrières le mesurent</a>.</li>
  <li><strong>Et personne ne le pilote.</strong> L'équilibre se rattrape par
  des réformes (1993, 2003, 2010, 2014, 2023), qui déplacent chaque fois
  l'effort sur ceux qui n'ont pas encore pris leur retraite.
  <a href="${g.lien("/cout")}">Le solde est ici</a>.</li>
</ul>`);

  const depliantCalcul = g.depliant("Comment une pension serait calculée", `
<p>Un compte notionnel est un compte <em>virtuel</em> : aucun capital n'est
placé, les cotisations de l'année paient les pensions de l'année. C'est toujours
de la répartition. Ce qui change, c'est le calcul du droit.</p>
<ol>
  <li><strong>On inscrit</strong> chaque cotisation versée sur le compte, au
  premier euro et sans plafond.</li>
  <li><strong>On revalorise</strong> le compte chaque année, au rythme auquel
  progresse la masse des salaires, c'est-à-dire au rendement que la
  répartition peut servir sans changer son taux.</li>
  <li><strong>On divise</strong>, au départ en retraite, le solde du compte par
  le nombre d'années qu'il reste statistiquement à vivre, lu sur la table de
  votre propre génération. Le résultat est la pension.</li>
</ol>
<p>Un âge minimum subsiste, on ne part pas à trente ans. Mais il n'y a plus
d'âge du ${g.terme("taux plein")}, ni ${g.terme("décote")}, ni
${g.terme("surcote")} : partir plus tôt donne une pension
plus faible, partir plus tard une pension plus forte, dans le rapport exact de
ce que l'un et l'autre coûtent.
<a href="${g.lien("/methode")}">Le détail du calcul</a>.</p>`);

  const depliantVerifier = g.depliant("Tout vérifier, page par page", `
<div class="note signee">
<p><strong>Pourquoi ce site.</strong> Nous avons choisi de publier un modèle
plutôt qu'un slogan. Une proposition de retraite se juge sur ce qu'elle verse
à chacun et sur ce qu'elle coûte à tous, et nous voulions que n'importe qui
puisse le vérifier sur sa propre carrière. Nos réserves sont écrites page par
page : le modèle reste un modèle, ses séries d'avant 1950 sont fragiles, et le
niveau des pensions notionnelles dépend d'un réglage annuel qu'il calcule sans
l'appliquer. Nous préférons un chiffre discutable à une promesse qu'on ne peut
pas discuter.</p>
<p class="discret">Le Parti libéral français, septembre 2026.</p>
</div>
<ul class="serree">
  <li><a href="${g.lien("/simuler")}">Simuler</a> : votre carrière, ou votre
  relevé collé tel quel, sous les quatre systèmes.</li>
  <li><a href="${g.lien("/cas-types")}">Cas types</a> : treize carrières sur sept
  générations.</li>
  <li><a href="${g.lien("/cout")}">Coût</a> : ce qui rentre, ce qui sort, et ce
  qui manque, de 1959 à 2070.</li>
  <li><a href="${g.lien("/methode")}">Méthode</a> : ce que le modèle calcule, et
  ce qu'il supprime.</li>
  <li><a href="${g.lien("/donnees")}">Données</a> : l'état de fiabilité de chaque
  série, source par source.</li>
</ul>
<p class="discret">Le modèle, les données et cette page sont publiés sous
licence libre : <a href="${g.DEPOT}">le dépôt</a>. Solde du système de retraite
en ${anneeSolde} :
${g.pourcentage(comptes.solde(anneeSolde), true, 2)} du PIB.</p>`);

  // Les trois gestes du calcul. Ils étaient au format du texte courant, et se
  // lisaient comme une note de bas de page à côté du tableau qui leur fait
  // face — alors qu'ils pèsent autant.
  const gestes = [
    "<strong>On inscrit</strong> chaque cotisation sur votre compte, "
    + "au premier euro, sans plafond.",
    "<strong>On revalorise</strong> le compte chaque année, au rythme "
    + "des salaires du pays.",
    "<strong>On divise</strong>, au départ, par les années qu'il vous "
    + "reste à vivre en moyenne. C'est votre pension.",
  ].map((texte, index) => (
    `<li><span class="rang">${index + 1}</span><span>${texte}</span></li>`
  )).join("");

  const tete = g.affiche(
    "Notre programme pour les retraites",
    'La seule retraite qui vous rend <span class="cle-texte">vraiment</span> '
    + "ce que vous avez cotisé.",
    '<strong class="cle-texte">Un compte à votre nom, en euros.</strong> '
    + "Chaque cotisation y est inscrite ; à la retraite, il devient votre "
    + 'pension. <strong class="cle-texte">Pas de trimestres, pas de barèmes, '
    + "pas de surprise.</strong>",
  );

  return `
${tete}

${simulateurCourt(contexte)}

${engagements(contexte)}

<div class="paire">
  <div>
    <p class="surtitre">Le calcul</p>
    <h2 style="margin-top:0">Comment ça marche, en trois gestes</h2>
    <ol class="gestes">${gestes}</ol>
    <p class="discret">Rien n'est placé : les cotisations de l'année paient
    les pensions de l'année. C'est toujours la ${g.terme("répartition")}.</p>
  </div>
  <div class="encadre">
    <h2 class="serif" style="margin-top:0">Le plancher regarde chacun, pas le
    couple</h2>
    <p>Aujourd'hui, l'ASPA regarde les ressources du couple : à 300 € et
    1 500 € de pension, il ne reçoit rien. La garantie regarde chacun :</p>
    ${tableauGarantie()}
  </div>
</div>

<h2>Ce que cela change</h2>
${differences}
<p class="discret">C'est le système de la Suède, de l'Italie, de la Pologne et
de la Lettonie.</p>

<div class="creme">
<p class="surtitre">Vérifiez plutôt que de nous croire</p>
<h2 class="serif" style="margin:0">Tout est chiffré, sur des données publiques
et un modèle ouvert.</h2>
<p class="actions"><a class="bouton" href="${g.lien("/simuler")}">Simuler ma
retraite</a><a href="${g.lien("/cout")}">Ce que ça coûte, et qui paie</a></p>
</div>

<h2>Pour aller plus loin</h2>

${depliantActuel}

${depliantCalcul}

${programmeJustice(contexte)}
${programmeGarantie(contexte)}
${programmeCapitalisation(contexte)}
${programmeTransition(contexte)}
${programmeBlocages(contexte)}

${depliantVerifier}
`;
}

/**
 * En quoi le compte notionnel est plus juste, entre métiers et entre âges.
 *
 * Deux questions qu'on pose toujours, et dont les réponses tiennent chacune en
 * quatre lignes. Elles sont repliées ensemble parce qu'elles se répondent :
 * l'une regarde deux carrières de la même génération, l'autre deux générations
 * de la même carrière.
 */
function programmeJustice(contexte) {
  const regimes = contexte.simulateur().catalogue.taille;
  return g.depliant("En quoi ce serait plus juste", `
<h4>Entre deux personnes</h4>
<ul class="serree">
  <li><strong>À cotisation égale, pension égale.</strong> Un fonctionnaire, un
  artisan et un salarié qui versent la même somme acquièrent le même droit. Les
  ${regimes} barèmes disparaissent, et avec eux les comparaisons que personne ne
  sait trancher.</li>
  <li><strong>Une carrière hachée n'est plus punie deux fois.</strong>
  Aujourd'hui, une interruption fait perdre des trimestres, donc le taux plein,
  donc une décote qui s'applique à <em>toute</em> la pension. Avec un compte,
  elle fait perdre les cotisations de ces années-là, et rien de plus.</li>
  <li><strong>La solidarité devient visible.</strong> Ce que la collectivité
  ajoute ne se cache plus dans un barème : c'est une allocation votée, chiffrée
  et financée par l'impôt.</li>
</ul>

<h4>Entre deux générations</h4>
<p>C'est ce que le système actuel tient le plus mal. Une pension y est promise
par une règle et payée par la génération suivante ; quand le compte n'y est pas,
la règle change, toujours au détriment de ceux qui n'ont pas encore
liquidé. Ce qu'un euro cotisé rapporte dépend ainsi de l'année de naissance,
sans que personne ne l'ait voté.</p>
<ul class="serree">
  <li><strong>Le rendement est le même pour tous</strong> : la croissance de la
  masse des salaires, c'est-à-dire exactement ce que la répartition peut payer à
  taux inchangé.</li>
  <li><strong>Chacun est divisé par sa propre espérance de vie.</strong> Vivre
  plus longtemps étale le même capital sur plus d'années, au lieu d'envoyer la
  facture à la génération d'après.</li>
  <li><strong>Le taux ne bouge pas.</strong> Fixé une fois, il retire aux actifs
  d'aujourd'hui le moyen de s'accorder des droits que les actifs de demain
  devraient financer.</li>
  <li><strong>L'écart se solde chaque année</strong>, au lieu de s'accumuler en
  silence jusqu'à la réforme suivante.</li>
</ul>`);
}

/**
 * Le plancher, et le seul changement qui compte : il regarde une personne.
 *
 * Le tableau fait le travail que trois paragraphes faisaient mal. Quatre
 * couples, deux colonnes : ce que l'ASPA sert aujourd'hui, ce que la garantie
 * servirait. La ligne « 300 € et 1 500 € » dit tout.
 */
/**
 * Le taux de cotisation retraite d'aujourd'hui, parts salariale et patronale
 * additionnées. Copie de `TAUX_ACTUEL_*` dans `web/pages.py`, où la
 * décomposition ligne à ligne est écrite.
 */
const TAUX_ACTUEL_SALARIAL = 0.1131;
const TAUX_ACTUEL_PATRONAL = 0.1667;
const TAUX_ACTUEL_TOTAL = TAUX_ACTUEL_SALARIAL + TAUX_ACTUEL_PATRONAL;

/** L'âge d'ouverture de la garantie, celui de l'ASPA. */
const AGE_OUVERTURE_GARANTIE = 65;

/**
 * Les quatre engagements du programme, chiffrés, numérotés 01 à 04.
 *
 * Trois niveaux par carte : le CHIFFRE en or attire l'œil, la PROMESSE en
 * serif porte le message — c'est elle qui se perdait quand les cartes n'en
 * avaient que deux —, le DÉTAIL technique répond à qui veut savoir comment. Un
 * ou deux passages en or par carte, jamais plus, et doublés d'un demi-gras
 * pour survivre en niveaux de gris.
 *
 * Copie de `_engagements` dans `web/pages.py`.
 */
function engagements(contexte) {
  const base = contexte.base;
  const taux = g.pourcentage(base.taux_cotisation_liberal, false, 0);
  const capitalise = g.pourcentage(base.taux_capitalisation_obligatoire, false, 0);
  const volontaire = g.pourcentage(
    tauxCapitalisationVolontaireApplique(base), false, 0,
  );
  const garantie = base.garantie_vieillesse_mensuelle;
  const isolement = base.allocation_isolement_mensuelle;
  const seul = g.euros(garantie + isolement);
  const couple = g.euros(2 * garantie);

  const cartes = [
    [seul,
      "par mois au minimum, seul.<br>"
      + `<strong class="cle-texte">${couple}</strong> pour un couple.`,
      `<strong class="cle-texte">${g.euros(garantie)} par personne</strong>, `
      + `plus <strong class="cle-texte">${g.euros(isolement)} d'allocation `
      + "d'isolement</strong> pour qui vit seul. Payés par l'impôt, dès "
      + `${AGE_OUVERTURE_GARANTIE} ans.`],
    [`${taux} + ${capitalise}`,
      "de cotisation : la répartition, "
      + '<strong class="cle-texte">plus un capital à votre nom</strong>.',
      `${taux} au compte de retraite — part salariale et patronale `
      + "additionnées, contre "
      + `${g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0)} aujourd'hui `
      + `(${g.pourcentage(TAUX_ACTUEL_SALARIAL, false, 1)} + `
      + `${g.pourcentage(TAUX_ACTUEL_PATRONAL, false, 1)} pour un salarié du privé), `
      + 'et <strong class="cle-texte">le même taux pour tout le monde</strong>. '
      + `Par-dessus, ${capitalise} placés sur des titres sans risque, `
      + '<strong class="cle-texte">qui vous appartiennent</strong> et se '
      + `transmettent. Restent ${volontaire} rendus : le simulateur montre ce `
      + "qu'ils donnent si vous les placez au même endroit, "
      + '<strong class="cle-texte">à effort inchangé</strong>.'],
    ["1 compte",
      '<strong class="cle-texte">en euros</strong>, lisible par tous.',
      "Un compte personnel de retraite : vous voyez "
      + '<strong class="cle-texte">votre solde comme sur un relevé '
      + "bancaire</strong>."],
    ["100 %",
      "de ce que vous avez cotisé "
      + '<strong class="cle-texte">vous revient</strong>.',
      "Partir plus tôt donne moins, plus tard donne plus — "
      + '<strong class="cle-texte">dans le rapport exact de ce que ça '
      + "coûte</strong>."],
  ];
  const corps = cartes.map(([chiffre, promesse, detail], index) => (
    `<div class="engagement"><div class="rang">${String(index + 1).padStart(2, "0")}</div>`
    + `<div class="chiffre">${chiffre}</div>`
    + `<div class="promesse">${promesse}</div>`
    + `<div class="detail">${detail}</div></div>`
  )).join("");
  return '<section class="engagements" aria-label="Nos quatre engagements">'
    + `<div class="grille">${corps}</div></section>`;
}

/**
 * Le formulaire court de l'accueil : quatre champs, et « Calculer ».
 *
 * Il est SOUS LE TITRE, avant même les engagements : la preuve est mise à
 * hauteur de la promesse. Les noms des champs sont exactement ceux du grand
 * formulaire, parce que c'est la même adresse qui les reçoit.
 *
 * `vers` est la page qui reçoit la saisie : l'accueil renvoie au simulateur,
 * la page Trajectoire se renvoie à elle-même.
 *
 * Copie de `_simulateur_court` dans `web/pages.py`.
 */
function simulateurCourt(contexte, vers = "/simuler") {
  const saisie = new Saisie();
  const affiliations = contexte.simulateur().affiliations;
  const champs = [
    g.champDate("naissance", "Date de naissance", saisie.naissanceIso,
      "seul le mois compte", saisie.naissanceEnClair,
      { min: `${NAISSANCE_MINIMALE}-01-01`, max: `${NAISSANCE_MAXIMALE}-12-31`,
        autocomplete: "bday" }),
    g.champDate("debut", "Début de carrière", saisie.jourDe(saisie.debut),
      "le premier mois cotisé", saisie.calculDe(saisie.debut),
      { min: saisie.jourDe(AGE_DEBUT_MINIMAL),
        max: saisie.jourDe(AGE_DEBUT_MAXIMAL) }),
    g.liste("statut", "Statut",
      optionsStatuts(affiliations, saisie.dateDe(saisie.debut)),
      saisie.statut, "celui du premier emploi"),
    g.champDate("liquidation", "Départ souhaité",
      saisie.jourDe(saisie.liquidation), "effectif, ou souhaité",
      saisie.calculDe(saisie.liquidation),
      { min: saisie.jourDe(AGE_LIQUIDATION_MINIMAL),
        max: saisie.jourDe(AGE_LIQUIDATION_MAXIMAL) }),
  ].join("");
  return `
<form class="creme simulateur-court" method="get" action="${g.route(vers)}">
  <div class="tete">
    <h2 class="serif">Et vous, ça donne combien&nbsp;?</h2>
    <span class="etiquette">Le simulateur</span>
  </div>
  <div class="grille">${champs}
    <div class="action"><button type="submit">Calculer →</button></div>
  </div>
  <p class="discret" style="margin:0.9rem 0 0">Quatre montants côte à côte :
  les règles d'aujourd'hui, et les nôtres. Tout se calcule dans votre
  navigateur, rien n'est envoyé.</p>
</form>`;
}

/**
 * Ce que le plancher individualisé change, en cinq lignes : l'argument le
 * plus immédiatement parlant du site, en haut de l'accueil.
 */
function tableauGarantie() {
  return g.tableau(
    ["Pensions des deux personnes", "Aujourd'hui (ASPA)", "Avec la garantie"],
    [
      ["300 € et 300 €", "1 000 €", "1 000 €"],
      ["300 € et 1 500 €", "0 €", "500 €"],
      ["900 € et 900 €", "0 €", "0 €"],
      ["300 € et 5 000 €", "0 €", "500 €"],
      ["Personne seule, 300 €", "750 €", "750 €"],
    ],
    ["", "nombre", "nombre"],
    "Ce que le plancher individualisé change, par mois",
    true,
  );
}

function programmeGarantie(contexte) {
  const base = contexte.base;
  const plancherSeul = base.garantie_vieillesse_mensuelle
    + base.allocation_isolement_mensuelle;
  return g.depliant("Le plancher, et ce qu'il change pour les petites pensions", `
<p>Le système actuel superpose l'ASPA, le minimum contributif, le minimum
garanti de la fonction publique, l'assurance vieillesse des parents au foyer,
les majorations de durée et la majoration pour trois enfants. Chacun a son
barème, son âge et sa condition. Ensemble, ils rendent toute pension modeste
impossible à prévoir.</p>
<p>Nous les remplaçons par <strong>une seule prestation</strong> : différentielle
comme l'ASPA, servie à partir de 65 ans comme elle, financée par l'impôt. Mais
<strong>individualisée</strong>. Chacun est comparé à son propre plancher, sans
que la pension du conjoint entre dans le calcul.</p>
<ul class="serree">
  <li>${g.euros(base.garantie_vieillesse_mensuelle)} par mois et par personne ;</li>
  <li>${g.euros(base.allocation_isolement_mensuelle)} de plus pour qui vit seul,
  soit ${g.euros(plancherSeul)} ;</li>
  <li>en euros de ${base.annee_euros_garantie_vieillesse}, revalorisés sur les
  prix.</li>
</ul>
<p><strong>Une avance, pas un don.</strong> Ce que la garantie verse est une
créance de l'État sur celui qui la reçoit. Elle porte intérêt au taux auquel
l'État emprunte, pour que les finances publiques n'y perdent rien, et elle est
<strong>reprise sur la succession dès le premier euro</strong>, là où l'ASPA
n'est récupérée qu'au-delà d'un seuil d'actif net. Quatre règles l'encadrent
:</p>
<ul class="serree">
  <li>elle ne s'exerce que sur ce que la succession contient : les héritiers
  ne paient jamais de leur poche, et ce que l'actif ne couvre pas est
  abandonné — c'est cette part-là, et elle seule, que l'impôt finance ;</li>
  <li>le logement est repris comme le reste, mais la reprise attend le décès
  du conjoint survivant qui l'occupe, les intérêts courant entre-temps ;</li>
  <li>les donations faites depuis l'ouverture de la garantie, ou dans les dix
  ans qui l'ont précédée, sont réintégrées : la créance se poursuit contre le
  donataire, à hauteur de ce qu'il a reçu et jamais au-delà, comme l'aide
  sociale départementale le fait déjà ; les primes d'assurance-vie versées
  après 65 ans de même, contre leur bénéficiaire ;</li>
  <li>la créance est garantie par une hypothèque légale inscrite dès le
  premier versement, de sorte qu'un bien donné la porte avec lui.</li>
</ul>
<p>Elle se demande, comme l'ASPA, et se refuse : personne ne se voit imposer
une dette. Le programme retient qu'un ayant droit sur deux la réclame, ce que
la DREES observe sur l'ASPA, et chiffre son coût ainsi.</p>
<p>Le tableau du haut de page le montre : l'ASPA regarde les ressources du
foyer, et à 300 € et 1 500 € le couple dépasse son plafond et ne reçoit rien.
La garantie regarde chacun, et sert 500 € au premier. C'est ce changement
d'assiette, plus que le montant, qui fait la différence pour les femmes aux
pensions les plus faibles.
<a href="${g.lien("/cout")}">Ce qu'elle coûterait</a> est calculé sur la
distribution réelle des pensions, non sur des cas types.</p>`);
}

/**
 * La part capitalisée, expliquée à qui n'a pas ouvert la page Méthode.
 *
 * Trois questions et trois seulement : ce que c'est, ce que cela change pour
 * celui qui cotise, et ce que cela ne fait pas. Copie de
 * `_programme_capitalisation` dans `web/pages.py`.
 */
function programmeCapitalisation(contexte) {
  const base = contexte.base;
  const taux = g.pourcentage(base.taux_capitalisation_obligatoire, false, 0);
  const volontaire = g.pourcentage(base.taux_capitalisation_volontaire, false, 0);
  const total = g.pourcentage(tauxCapitalisationApplique(base), false, 0);
  const repartition_ = g.pourcentage(base.taux_cotisation_liberal, false, 0);
  const impose_ = g.pourcentage(
    base.taux_cotisation_liberal + base.taux_capitalisation_obligatoire, false, 0,
  );
  const propose = g.pourcentage(tauxRetraitePropose(base), false, 0);
  return g.depliant(
    `La part capitalisée : ${total} qui vous appartiennent`,
    `
<p>À compter de ${base.annee_debut_capitalisation}, ${taux} de votre rémunération
sont prélevés <strong>en plus</strong> des ${repartition_} de la répartition, et
placés à votre nom sur des titres sans risque. Ce capital ne passe pas par le
compte notionnel : il vous revient, dans un plan d'épargne retraite, l'enveloppe
qui existe déjà et que des millions de Français détiennent. Les années d'avant
ne changent pas :
elles gardent les taux qui étaient les leurs, et qui a déjà liquidé ne cotise
rien.</p>
<p><strong>À ces ${taux} s'ajoutent ${volontaire} que personne ne vous
impose.</strong> Le système actuel prélève
${g.pourcentage(TAUX_ACTUEL_TOTAL, false, 0)} de la rémunération d'un salarié
du privé pour la retraite ; ${repartition_} et ${taux} en font ${impose_}, et la
proposition vous rend donc les cinq points qui restent. Le site suppose que vous
les remettez au même endroit, sur le même compte, aux mêmes conditions : votre
effort revient alors à ${propose}, c'est-à-dire à ce qu'il est déjà aujourd'hui,
et les deux systèmes se comparent enfin <strong>à prix égal</strong>. Vous êtes
libre de ne pas le faire : les montants du simulateur disent aussi ce que vous
toucheriez sans.</p>
<ul class="serree">
  <li><strong>Il vous appartient.</strong> Si vous mourez avant d'avoir liquidé,
  le capital revient à vos héritiers, intégralement. Une pension de répartition,
  elle, s'éteint avec vous sans rien laisser.</li>
  <li><strong>Il ne sort qu'à la retraite.</strong> Pas d'achat de résidence
  principale, pas de sortie anticipée : l'argent n'en sort qu'en rente viagère,
  ou par l'héritage. C'est vrai des ${taux} obligatoires comme des ${volontaire}
  que vous ajoutez.</li>
  <li><strong>Il est placé sans risque.</strong> Des titres d'État parmi les
  mieux notés de la zone euro, portés jusqu'à leur échéance : longue tant que la
  retraite est loin, courte à l'approche du départ. Aucune action, aucun pari.</li>
  <li><strong>Il ne remplace rien.</strong> La retraite par répartition reste ce
  qu'elle est, et le compte notionnel la calcule sans regarder ce capital. Les
  deux montants sont affichés côte à côte, jamais confondus.</li>
</ul>
<p>Ce que cela coûte est chiffré : l'enveloppe prélève des frais, et le
simulateur les montre euro par euro, comme il montre le rendement qui reste. La
page <a href="${g.lien("/methode/")}">Méthode</a> dit à quels
taux l'argent est placé, d'où ils viennent et ce qu'ils supposent.</p>`,
  );
}

/** Les six étapes, et l'année où chacune produit son effet. */
function programmeTransition(contexte) {
  const base = contexte.base;
  const fusionne = contexte.simulateur().regimeFusionne;
  const etapes = g.tableau(
    ["Étape", "Ce qu'elle fait"],
    [
      ["1. Le compte unique",
        "Ce que chacun a cotisé est rassemblé sur un compte unique et "
        + "converti en euros. Les régimes continuent de liquider selon leurs "
        + "règles : rien ne change encore pour personne, mais le relevé de "
        + "carrière devient lisible. Les données existent déjà."],
      [`2. La bascule (${base.annee_bascule})`,
        "Les droits déjà acquis sont figés, réduits à leur part "
        + "contributive et convertis en capital. Les pensions déjà versées "
        + "ne sont pas touchées. Les régimes fusionnent en un seul."],
      ["3. Le taux unique",
        "Toute cotisation postérieure à la bascule est prélevée à "
        + `${g.pourcentage(base.taux_cotisation_liberal, false, 0)} de la `
        + "rémunération, parts salariale et patronale additionnées, quel que "
        + "soit le statut. Les taux qui dépassaient ce niveau baissent, ceux "
        + "qui restaient en deçà montent."],
      ["4. La garantie vieillesse",
        "Elle remplace l'ASPA, le minimum contributif et le minimum "
        + "garanti le jour de la bascule, et passe au budget de l'État. "
        + "Aucun minimum ne se calcule plus dans le barème de la pension."],
      ["5. Le pilotage",
        "Le chiffre qui ramène l'année à zéro est publié et appliqué "
        + "chaque année. C'est ce qui remplace les réformes."],
      ["6. Le régime de croisière",
        "La dernière pension calculée en partie sous l'ancien barème est "
        + "versée une quarantaine d'années après la bascule. D'ici là, les "
        + "deux systèmes coexistent dans chaque pension."],
    ],
    ["", "texte"],
    "Du système actuel au régime unique",
    true,
  );
  return g.depliant("Comment on y va, étape par étape", `
<p>La bascule fige ce qui est acquis.</p>
${etapes}
<p>Après la bascule, un seul régime : départ possible à
${age(fusionne.age_ouverture)}, assiette déplafonnée, même taux pour tous.</p>`);
}


/**
 * Les points de blocage regardés avant de choisir, et ce qu'on en a fait.
 *
 * Les chiffres sont DATÉS, et la page le dit : ils viennent de trois scripts
 * du dépôt que le portage ne porte pas. La page d'accueil ne calcule rien, et
 * cette section pas davantage.
 */
function programmeBlocages(contexte) {
  const points = g.tableau(
    ["Le point", "Ce que nous avons regardé", "Ce que nous en retenons"],
    [
      ["La fusion des régimes",
        "Quatre barèmes possibles pour le régime unique : le taux d'aujourd'hui "
        + "déplafonné, le statut du salarié du privé avec ses tranches, le régime "
        + "général seul, la moyenne des régimes. Un taux plus bas n'est pas plus "
        + "négociable, il est impayable : les pensions déjà acquises sont servies "
        + "avec moins de cotisations, et sous les deux derniers barèmes le déficit "
        + "dépasse cinq points de PIB par an jusqu'en 2050.",
        "Un régime unique se vote par une loi ordinaire : le projet de 2020 l'a "
        + "établi, et le Conseil d'État n'y a vu aucun obstacle de principe, ni "
        + "pour les fonctionnaires ni pour les complémentaires. Le taux, lui, est "
        + "le nôtre, et son coût est chiffré deux lignes plus bas."],
      ["Les pensions déjà servies, recalculées",
        "C'est le point que le juge constitutionnel regarderait en premier : une "
        + "pension liquidée est une situation acquise, et la loi qui la touche doit "
        + "le justifier et rester proportionnée. Nous ne retirons que ce qui n'a "
        + "pas été cotisé, l'indexation sur les prix est conservée, la garantie est "
        + "relevée dans le même texte. L'objection la plus forte, celle de l'assuré "
        + "parti à l'âge que sa loi lui ouvrait, a été chiffrée : lui prendre le "
        + "diviseur de 64 ans plutôt que celui de son âge coûte un dixième de point "
        + "de PIB par an, et plus rien en 2050.",
        "Le recalcul est maintenu. La version qui laisse le stock intact a été "
        + "chiffrée et écartée : −3,9 points de PIB par an en moyenne jusqu'en "
        + "2070, elle n'est pas finançable."],
      ["Le taux de 18 %",
        "Face au taux d'aujourd'hui, 25,8 % part patronale comprise, les 18 % "
        + "coûtent 2,3 points de PIB par an sur 2026-2070, sous les mêmes règles de "
        + "recette. Le solde de la proposition est de −1,5 point par an en moyenne "
        + "contre −1,1 pour le système actuel, et la dette qu'elle accumule en 2070 "
        + "vaut 103 % du PIB contre 66 %.",
        "C'est le prix d'un prélèvement plus bas, et il est écrit sur la page "
        + "Coût plutôt que caché. Le pilotage annuel, que ces chiffres n'appliquent "
        + "pas, est ce qui le tient : le coefficient d'équilibre de 2070 est de "
        + "0,92."],
      ["La garantie vieillesse",
        "Le préambule de 1946 garantit aux vieux travailleurs des moyens "
        + "convenables d'existence, et un compte purement contributif y répond mal.",
        "La garantie est relevée par rapport à l'ASPA, individualisée, et portée "
        + "dans la même loi que le régime : le juge lira les deux ensemble."],
      ["Le chemin législatif",
        "Une réforme systémique n'entre pas dans une loi de financement de la "
        + "sécurité sociale, où le Conseil constitutionnel écarte les cavaliers. Il "
        + "faut une loi ordinaire, une étude d'impact que le Conseil d'État lira "
        + "ligne à ligne, et une trajectoire qui s'explique devant la procédure "
        + "européenne pour déficit excessif.",
        "Nous publions l'étude d'impact avant le texte : c'est ce site, ses "
        + "réserves comprises."],
    ],
    ["", "texte", "texte"],
    "Cinq points de blocage, regardés avant de choisir",
    true,
  );
  return g.depliant("Ce qui pouvait nous arrêter, et ce que nous en avons fait", `
<p>Nous avons cherché ce qui arrêterait cette proposition avant de la défendre. Voici les cinq points, ce que nous avons mesuré, et ce que nous en faisons.</p>
${points}
<p class="discret">Mesures des 20 et 21 septembre 2026, par trois scripts du dépôt : le solde sous quatre régimes uniques, le stock à l'âge légal, la proposition prospective. Cette page ne les recalcule pas ; leur détail, décision par décision, est dans la feuille de route du <a href="${g.DEPOT}/blob/main/docs/feuille_de_route.md">dépôt</a>.</p>`);
}
