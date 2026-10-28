/**
 * La saisie d'une simulation : ce que l'adresse dit, lu en carrière et en règles.
 *
 * Une simulation du site s'écrit tout entière dans son adresse — la naissance,
 * le statut, les dates, les revenus, les réglages — et ces paramètres sont
 * l'entrée de la surface publique (docs/architecture.md, annexe C.9). Ce module
 * les lit : il borne chaque champ, et dit pourquoi, refuse ce qui ne décrit
 * aucune carrière (`ErreurSaisie`, dont le message s'affiche tel quel), et tire
 * de la saisie la carrière et le jeu de paramètres que le moteur calcule. Le
 * texte du site, lui, s'écrit dans `pages.js` et `gabarit.js`.
 *
 * LE SEUL EXEMPLAIRE DE LA SAISIE (action 161). La saisie formait la première
 * moitié de `web/pages.py`, dont la phase 8 a retiré le texte du site ; son
 * calcul est resté en Python, dans `saisie.py`, que ce module portait, et les
 * témoins rejouaient la lecture des deux côtés. Depuis l'action 161, étape 6,
 * la fabrique bâtit ses carrières par ce module, au travers du pont
 * (`pont.carrieres_des_saisies`), et le moteur Python les simule : le Python,
 * que plus rien ne lisait, est parti, relu contre ce module, ses explications
 * passées ici, les témoins identiques à l'octet.
 */

import {
  DateMois, MOIS_PAR_AN, NOMS_DE_MOIS, enMois, formaterAge, moisTravailles,
  origineDesAges,
} from "./calendrier.js";
import {
  AgeConversionDroitsAcquis, ContributionEtat, ModeAgeReference, ModeIndexation,
  PartCotisation, SituationFoyer, TableConversion, avec, sousRegimeFrais,
  sousRegimeTaux,
} from "./config.js";
import {
  CATEGORIES_D_INVALIDITE, FORMES_D_UNION, MOTIFS_DE_PROLONGATION, dateDeclaree,
  naissanceDeclaree, plusAns, valeur as valeurPresumee,
} from "./chronologie.js";
import { CONJOINTS_COLLABORATEURS, anneeDEntree } from "./carriere.js";
import * as g from "./gabarit.js";
import { AGE_TERMINAL } from "./mortalite.js";
// Les motifs sans emploi et les clés des règles vivent dans `cles.js`, que le
// démarrage des pages lit sans charger la saisie (action 174, étape 5) : la
// saisie les reprend telles quelles, pour elle et pour ses lecteurs.
import { CLES_MODELISATION, CODES_SANS_EMPLOI, SANS_EMPLOI } from "./cles.js";

export { CLES_MODELISATION, CODES_SANS_EMPLOI, SANS_EMPLOI };

// Le profil de carrière se DÉDUIT du statut par défaut : on ne demande pas sa
// progression de carrière à quelqu'un qui a déjà dit qu'il était fonctionnaire
// de l'État ou cadre du privé, et le modèle lit chez l'INSEE le profil du
// groupe correspondant. Les trois autres restent, parce qu'une carrière au SMIC
// ne progresse pas comme la moyenne de son groupe et que la mesure d'une
// variante doit rester possible.
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

// Fenêtre de lissage maximale acceptée par le formulaire, en années. Le lissage
// s'applique au taux que la règle produit, quelle que soit la règle : ce qu'il
// vise est la loterie de cohorte. La fenêtre se saisit librement — 1 pour aucun
// lissage, 5 pour la règle italienne, ce qu'on veut entre les deux et au-delà.
// La borne est un garde-fou de sens, pas une limite du moteur : au-delà d'une
// trentaine d'années la moyenne couvre presque toute une carrière, tous les
// millésimes reçoivent à peu près le même taux, et ce n'est plus un lissage
// mais un taux fixe reconstitué.
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

// L'espérance de vie des projections de population 2026 de l'INSEE : la
// centrale, ou l'une des deux hypothèses qui en ôtent ou y ajoutent trois ans à
// l'horizon 2070 (action 138, étape 7). Elle décide des quotients projetés,
// donc du diviseur : les systèmes 2 à 6 la lisent, le système 1 n'en lit rien.
export const HYPOTHESES_ESPERANCE_VIE = [
  ["centrale", "INSEE, hypothèse centrale (défaut)"],
  ["basse", "INSEE, espérance de vie basse (trois ans de moins en 2070)"],
  ["haute", "INSEE, espérance de vie haute (trois ans de plus en 2070)"],
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
// Le défaut prend les taux à terme de la courbe du jour ; les deux autres en
// retirent une prime de terme, au milieu puis au haut de la fourchette de la
// littérature.
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
 *
 * Le simulateur va du revenu à la pension, et c'est le sens du droit : on
 * cotise, puis on liquide. Mais celui qui est déjà à la retraite connaît sa
 * pension au centime et ne se souvient pas de ce qu'il gagnait il y a trente
 * ans — lui demander un revenu, c'est lui demander d'estimer ce que le
 * simulateur sait calculer. Le second mode prend donc la pension et cherche le
 * revenu dont le SCÉNARIO 1 la tire : le droit en vigueur est le seul des
 * quatre systèmes qu'il ait un sens d'inverser, puisque c'est le seul que
 * l'assuré a réellement subi.
 */
export const SAISIES = [["revenu", ""], ["pension", ""]];

/**
 * Pension mensuelle proposée par défaut, en euros BRUTS, comme les montants par
 * défaut. Voisine de la pension moyenne de droit direct des retraités de droit
 * français, pour que le formulaire s'ouvre sur un cas qui ressemble à celui de
 * qui le lit.
 */
const PENSION_DEFAUT = 1500.0;

/**
 * Ce que « Mon estimation retraite » affiche à chaque âge — le total brut
 * mensuel de sa synthèse —, recopié pour être comparé à celui du simulateur :
 * un champ par départ de `DEPARTS_DE_L_ESTIMATION` (pilote.js), au plus tôt,
 * au taux plein, au taux plein automatique. Ils n'entrent dans aucun calcul,
 * et restent dans le navigateur avec le reste de la saisie.
 */
export const CHAMPS_ESTIMATION = Object.freeze(
  ["estimation_legal", "estimation_taux_plein", "estimation_automatique"]);

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
// exactement ce que le site faisait avant cette bascule. Le défaut est le BRUT,
// depuis le 4 octobre 2026 : c'est la langue de l'estimation officielle (« Mon
// estimation retraite », sur info-retraite.fr), celle des chiffres que chacun
// connaît déjà, et le propriétaire l'a voulu « en tête » pour qu'on puisse les
// comparer. Le net avant impôt reste à un clic. Les capitaux, les assiettes et
// les tableaux de détail sont bruts par nature et ne bougent pas : on ne
// « nette » pas un capital notionnel.
export const MODES_MONTANT = [
  ["brut", "brut — avant CSG et cotisations"],
  ["net", "net avant impôt — après CSG"],
];

// Durée mensuelle de référence du SMIC : 35 heures par semaine pendant 52
// semaines, ramenées au mois. Le barème l'écrit « 151,67 heures » et calcule sur
// 151,666… : 11,88 € de l'heure font 1 801,80 € par mois, non 1 801,84. Elle ne
// sert qu'à écrire un repère à l'échelle d'un salaire mensuel.
export const HEURES_SMIC_PAR_MOIS = (35 * 52) / 12;

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
/** La réponse d'une case cochée : l'inaptitude reconnue, la radiation imputable
 * au service. La case vide n'envoie rien. */
export const OUI = "oui";

/**
 * Chez qui l'activité exercée après le départ s'exerce : le droit du cumul
 * emploi-retraite distingue le dernier employeur, auprès duquel la reprise
 * n'est libre qu'après six mois (L. 161-22), de tous les autres.
 */
export const EMPLOYEURS_APRES_DEPART = [
  ["autre", "un autre employeur que le dernier"],
  ["dernier", "le dernier employeur"],
];

/**
 * Le travail manuel exercé cinq ans au moins au cours des quinze années qui
 * précèdent le départ : ouvrier, ce que la mère de famille ouvrière doit avoir
 * exercé (R. 351-23) ; en continu, en semi-continu, à la chaîne, au four ou aux
 * intempéries, ce que le travailleur manuel devait avoir exercé de 1976 à 1983
 * (décret n° 45-0179, articles 70-2 et 70-3), et qui est aussi un travail
 * ouvrier (fiches `taux_plein_meres_de_famille_ouvrieres` et
 * `taux_plein_travailleurs_manuels`). Le vide dit qu'il n'y en a pas.
 */
export const TRAVAUX_MANUELS = [
  ["", "non"],
  ["ouvrier", "ouvrier"],
  ["penible", "en continu, à la chaîne, au four ou aux intempéries"],
];

/**
 * Les catégories de la pension d'invalidité, qui en fixent le taux (L. 341-4) :
 * le menu du formulaire, que la saisie lit en entier (`CATEGORIES_D_INVALIDITE`
 * de la chronologie). Sans réponse, la présomption
 * `categorie_de_la_pension_d_invalidite` la pose, selon que l'invalide
 * travaille ou non quand la pension de vieillesse la remplace.
 */
export const CATEGORIES_INVALIDITE = [
  ["", "présumée selon votre activité"],
  ["1", "première : capable d'une activité rémunérée"],
  ["2", "deuxième : incapable de toute profession"],
  ["3", "troisième : aidé d'une tierce personne"],
];

/**
 * L'activité du micro-entrepreneur, qui fait lire son revenu comme un CHIFFRE
 * D'AFFAIRES (action 138, étape 12 ; fiche `micro_social_abattement`). Ses
 * droits « sont calculés sur la base de leur chiffre d'affaires ou de leurs
 * recettes après application d'un taux d'abattement de 71 % » pour la vente,
 * « de 50 % » pour les services commerciaux ou artisanaux, « de 34 % » pour les
 * recettes libérales (L. 613-7, II ; L. 133-6-8 jusqu'en 2017), les abattements
 * du micro-fiscal (CGI, 50-0 et 102 ter), les mêmes depuis 2007. Le vide garde
 * le sens d'avant : le revenu saisi est déjà abattu. La Cipav route la ligne
 * vers les régimes du libéral (CNAVPL et Cipav) : ses micro-entrepreneurs sont
 * ceux des professions qu'elle garde, et ceux qui y étaient affiliés avant 2019
 * (D. 613-4, b).
 */
export const ACTIVITES_MICRO = [
  ["", "revenu déjà abattu"],
  ["vente", "vente de marchandises : chiffre d'affaires"],
  ["services", "services commerciaux ou artisanaux : chiffre d'affaires"],
  ["liberal", "activité libérale : recettes"],
  ["cipav", "activité libérale à la Cipav : recettes"],
];

/**
 * L'abattement de chaque activité, la part du chiffre d'affaires qui ne compte
 * pas dans les droits.
 */
export const ABATTEMENTS_MICRO = { vente: 0.71, services: 0.50, liberal: 0.34, cipav: 0.34 };

/** Le statut lu en chiffre d'affaires, et celui vers qui la Cipav le route. */
export const STATUT_MICRO = "micro_entrepreneur";
export const STATUT_MICRO_CIPAV = "profession_liberale";

/**
 * Ce que saisit le fonctionnaire (action 138, étape 10 ; registre,
 * `simulateur_sud_education`) : sa rémunération, comme tout le monde, ou
 * l'INDICE MAJORÉ de son bulletin de paie, qui fait lire comme un indice le
 * revenu de ses périodes payées à l'indice. Son traitement brut est cet indice
 * fois la valeur du point (décret n° 85-1148 du 24 octobre 1985, article 3),
 * celle de l'année du modèle, comme les euros saisis sont ceux d'aujourd'hui ;
 * ses primes s'y ajoutent, à la part que la saisie en dit (`primes`), que le
 * traitement laisse. Le vide garde le sens d'avant.
 */
export const INDICES = [
  ["", "votre rémunération"],
  ["majore", "votre indice majoré"],
];

/**
 * Les statuts payés à l'indice : ceux dont le régime de base est celui de
 * l'État ou la CNRACL, les fonctionnaires titulaires, civils et militaires, des
 * trois versants, que le décret n° 85-1148 paie au point. Ni l'ouvrier de
 * l'État, payé au salaire de sa profession, ni le fonctionnaire de
 * Nouvelle-Calédonie, à son propre point, ni l'agent non titulaire, que son
 * contrat paie. Le test les recoupe aux affiliations.
 */
export const STATUTS_A_L_INDICE = Object.freeze([
  "fonctionnaire_etat", "fonctionnaire_etat_actif", "fonctionnaire_etat_super_actif",
  "policier", "militaire", "militaire_officier",
  "fonctionnaire_territorial_hospitalier", "fonctionnaire_territorial_hospitalier_actif",
  "fonctionnaire_territorial_hospitalier_super_actif", "fonctionnaire_hospitalier_actif",
  "aide_soignant", "sapeur_pompier_professionnel",
]);
const A_L_INDICE = new Set(STATUTS_A_L_INDICE);

/**
 * Le barème de la Lodeom que l'employeur applique, en Guadeloupe, en Guyane, en
 * Martinique ou à La Réunion, à la place de la réduction générale (L. 752-3-2,
 * III ; action 138, étape 18) : ceux du bloc `lodeom` de
 * `legislation/prelevements_remuneration.yaml`, sous leur libellé, qu'un test y
 * tient. Le vide, « non », est la réduction générale. Chaque emploi le porte, et
 * seule la fiche de paie du salarié du privé le lit.
 */
export const BAREMES_LODEOM = [
  ["", "non"],
  ["competitivite", "barème de compétitivité"],
  ["competitivite_renforcee", "barème de compétitivité renforcée"],
  ["innovation_et_croissance", "barème d'innovation et de croissance"],
];

/**
 * L'option du conjoint collaborateur d'un artisan ou d'un commerçant (fiche
 * `conjoint_collaborateur_independants` ; action 138, étape 18) : il cotise « à
 * sa demande » sur un forfait égal au tiers du plafond, ou sur 33,33 % ou 50 %
 * du revenu d'activité du chef d'entreprise (D. 633-19-2, 1° à 3°), la même
 * fraction pouvant se partager avec le chef ; le forfait « si aucun autre choix
 * n'est effectué » (R. 662-1), qui est le défaut. Le revenu de ses périodes est
 * alors celui du chef, dont la ligne ne cotise que la part de l'option
 * (`PARTS_COLLABORATEUR`) ; un relevé, qui porte l'assiette, n'en dépend pas.
 */
export const ASSIETTES_COLLABORATEUR = [
  ["", "le forfait, le tiers du plafond"],
  ["tiers", "33,33 % du revenu du chef d'entreprise"],
  ["moitie", "50 % du revenu du chef d'entreprise"],
];
/**
 * La part du revenu du chef que chaque option cotise. Le forfait n'en cotise
 * rien : la ligne sans revenu prend le tiers du plafond depuis l'affiliation
 * obligatoire de 2007, et n'a pas souscrit l'assurance volontaire avant
 * (`assietteDuConjointCollaborateur`, dans `carriere.js`).
 */
export const PARTS_COLLABORATEUR = { "": 0.0, tiers: 0.3333, moitie: 0.5 };

/**
 * La durée de captivité et de services militaires en temps de guerre que la
 * saisie admet, en mois : de un à vingt ans.
 */
export const MOIS_DE_GUERRE_MAXIMUM = 240;

/**
 * Le préfixe des champs qui disent la date où l'assuré demande la pension d'un
 * régime : « demande_regime_general=2031-05 ». Le code du régime suit, en
 * minuscules, chiffres et soulignés ; qu'il existe, c'est au calcul de le dire,
 * sur le catalogue.
 */
export const PREFIXE_DEMANDE = "demande_";
const CODE_DE_REGIME = /^[a-z][a-z0-9_]*$/;

/**
 * Combien de périodes hors de France, et combien de pensions étrangères,
 * l'adresse peut porter : « etranger1_pays » à « etranger4_… », et
 * « pension_etrangere1 » à « pension_etrangere4… ». Comme celle des métiers, la
 * borne est celle du formulaire, pas du moteur.
 */
export const ETRANGER_MAXIMUM = 4;

/**
 * Les précédents conjoints de l'assuré, divorcés, que l'adresse peut porter :
 * « ex1 » à « ex2_… ». La réversion se partage entre eux et le conjoint
 * survivant au prorata de la durée de chaque mariage (L. 353-3, R. 353-4).
 */
export const EX_CONJOINTS_MAXIMUM = 2;

/**
 * L'État que la personne ne nomme pas, parce que le tableau des accords ne le
 * nomme pas : aucun accord ne le lie à la France. Tout autre État s'écrit par
 * son code à deux majuscules, celui du tableau ; qu'il y soit, c'est au
 * contexte de le dire, qui a les données.
 */
export const AUTRE_ETAT = "autre";
const CODE_D_ETAT = /^[A-Z]{2}$/;

/**
 * La nature de l'activité exercée hors de France : une convention bilatérale ne
 * coordonne souvent que les salariés (`personnes` au tableau des accords). La
 * première est celle d'une ligne qui ne la dit pas.
 */
export const ACTIVITES_A_L_ETRANGER = [
  ["salariee", "salariée"],
  ["non_salariee", "non salariée"],
];

/**
 * Combien de périodes assimilées l'adresse peut porter : « assimilee1_motif » à
 * « assimilee4_… » (action 130, sixième domaine, étape 5). La borne est celle du
 * formulaire, pas du moteur.
 */
export const ASSIMILEES_MAXIMUM = 4;

/**
 * Les motifs d'une période assimilée que la saisie déclare, dans l'ordre de
 * `MOTIFS_D_ASSIMILATION` de la chronologie (`chronologie.js`), et ce que le
 * formulaire en dit. Ce que chacun valide, et depuis quand, ce sont les fiches
 * qui le disent : la saisie ne fait que déclarer la période.
 */
export const MOTIFS_D_ASSIMILATION = [
  ["stage_de_formation_professionnelle", "stage de formation professionnelle"],
  ["stage_d_insertion", "TUC ou stage d'insertion"],
  ["sportif_de_haut_niveau", "sportif de haut niveau"],
  ["conge_supplementaire_de_naissance", "congé supplémentaire de naissance"],
];

/** Les dispositifs d'un stage d'insertion, que ce motif, et lui seul, nomme. */
export const DISPOSITIFS_D_INSERTION = [
  ["tuc", "travaux d'utilité collective (TUC)"],
  ["stage_pratique_en_entreprise", "stage pratique en entreprise"],
  ["stage_jeunes_volontaires", "stage jeunes volontaires"],
  ["programme_d_insertion_locale", "programme d'insertion locale"],
  ["stage_d_initiation_a_la_vie_professionnelle",
    "stage d'initiation à la vie professionnelle"],
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
 *
 * Le départ le plus tardif est le dernier âge entier que les tables de mortalité
 * convertissent en rente : à leur âge terminal, cent vingt ans, nul ne survit
 * plus, et le diviseur du compte notionnel est nul. La borne valait
 * soixante-quinze ans depuis le premier commit, sans que rien ne le justifie :
 * le moteur calculait au-delà. Elle suit les tables depuis le 10 octobre 2026
 * (action 151), pour qu'on puisse simuler qui travaille très tard.
 */
export const NAISSANCE_MINIMALE = 1900;
export const NAISSANCE_MAXIMALE = 2020;
export const AGE_DEBUT_MINIMAL = 14;
export const AGE_DEBUT_MAXIMAL = 40;
export const AGE_LIQUIDATION_MINIMAL = 40;
export const AGE_LIQUIDATION_MAXIMAL = Math.trunc(AGE_TERMINAL) - 1;

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
 * Nombre de lignes qu'un relevé de carrière peut porter. Une carrière tient
 * entre l'âge de début minimal et le départ le plus tardif, soit cent cinq
 * années civiles au plus ; la borne laisse deux lignes de marge et ferme
 * surtout la porte que les interruptions avaient ouverte : le calcul se fait
 * chez le lecteur et l'adresse EST la saisie, si bien qu'un relevé de cent
 * mille lignes forgé dans un lien figeait l'onglet de celui qui le suivait.
 */
export const RELEVE_MAXIMUM = AGE_LIQUIDATION_MAXIMAL - AGE_DEBUT_MINIMAL + 2;

/**
 * Les variations des ressources du conjoint qu'une liste de la saisie porte au
 * plus : cinq ans de changements, un chaque mois. Elles sont comptées avant
 * d'être lues, comme les lignes d'un relevé : chacune révise la réversion, et
 * une adresse forgée qui en porterait cent mille ne doit coûter que son
 * découpage.
 */
export const VARIATIONS_MAXIMUM = 60;

/** Ce que fait varier chaque liste de variations, dans ses refus. */
const VARIATIONS_DE = Object.freeze({
  activite_conjoint_variations: "des revenus d'activité du conjoint",
  ressources_nouveau_conjoint_variations: "des ressources du nouveau conjoint",
});

/** Saisie inexploitable, à afficher telle quelle à l'utilisateur. */
export class ErreurSaisie extends Error {}

/** Le refus d'un mois de naissance hors de l'année. */
function refusDuMoisDeNaissance() {
  return new ErreurSaisie("Mois de naissance attendu entre 1 et 12.");
}

/**
 * Le refus d'une année de naissance hors du champ du modèle, citée telle
 * qu'elle a été reçue.
 */
function refusDeLAnneeDeNaissance(annee) {
  return new ErreurSaisie(
    `Année de naissance hors du champ du modèle : ${annee}. `
    + `Attendu entre ${NAISSANCE_MINIMALE} et ${NAISSANCE_MAXIMALE}.`,
  );
}

export const DEFAUTS = Object.freeze({
  naissance: 2000,
  naissance_mois: 1,
  //: Jour de naissance. Il décide du mois d'où les âges se comptent
  //: (`origineDesAges`), et donc de l'âge que vaut une date de carrière ; la
  //: génération, elle, se coupe au mois. Le calendrier du formulaire le demande
  //: toujours ; une adresse qui ne le porte pas — « naissance=1975 »,
  //: « naissance=1975-03 » — le laisse à la présomption `jour_de_naissance`
  //: (§ 5.6), et le dit ci-dessous.
  naissance_jour: 1,
  //: Vrai quand l'adresse portait la naissance sans son jour, que la
  //: présomption a posé : la carrière le présume alors à son tour.
  naissance_jour_presume: false,
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
  montants: "brut",
  //: Les totaux bruts mensuels de « Mon estimation retraite », recopiés pour
  //: être comparés (`CHAMPS_ESTIMATION`) ; `null` quand rien ne l'est.
  estimation_legal: null,
  estimation_taux_plein: null,
  estimation_automatique: null,
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
  //: Celles qui ne sont pas dites sont présumées (docs/architecture.md,
  //: § 5.6) ; celles qui le sont choisissent, enfant par enfant, la version des
  //: règles qui lui accordent des trimestres. Voir `naissancesEnfants`.
  naissances: "",
  //: Ce qui prolonge jusqu'à vingt ans la charge des enfants dont la naissance
  //: est dite, pour la majoration de la réversion (action 138, étape 4) :
  //: « 1:etudes:2009-07, 2:infirmite », le rang de chacun, son motif et, pour
  //: les études ou l'apprentissage, le mois où ils cessent, s'il le dit. Voir
  //: `prolongationsDeLaChargeDeclarees`.
  charge_enfants: "",
  //: Le conjoint, pour la réversion (docs/architecture.md, § 5.1) : sa
  //: naissance (AAAA ou AAAA-MM), son sexe — l'autre que celui de l'assuré
  //: s'il n'est pas dit (présomption `conjoint_de_l_autre_sexe`) —, la date du
  //: mariage, présumée sinon, ses ressources annuelles et ce qu'en rapporte son
  //: activité, l'union où il vit après le décès — `mariage`, `pacs` ou
  //: `concubinage` — et les ressources annuelles de son nouveau conjoint, et le
  //: mois où son invalidité est reconnue, s'il les dit. Voir `conjointDeclare`.
  conjoint: "",
  conjoint_sexe: "",
  mariage: "",
  ressources_conjoint: null,
  activite_conjoint: null,
  //: Le mois où cesse l'activité du conjoint, s'il le dit : sa réversion se
  //: révise le mois qui suit.
  activite_conjoint_fin: "",
  //: Ses revenus d'activité qui varient ensuite, s'il le dit : « date:montant »
  //: chacun, ses revenus annuels à partir de cette date — un salaire qui
  //: change, une activité reprise, 0 quand elle cesse —, séparés de virgules :
  //: sa réversion se révise le mois qui suit chacun. Voir `variationsAnalysees`.
  activite_conjoint_variations: "",
  nouvelle_union: "",
  ressources_nouveau_conjoint: null,
  //: Le mois où cette nouvelle union commence, s'il le dit ; sans lui, au décès.
  nouvelle_union_depuis: "",
  //: Celui où elle se défait, s'il le dit : il revit seul.
  nouvelle_union_fin: "",
  //: Les ressources de son nouveau conjoint qui varient pendant leur union, de
  //: même.
  ressources_nouveau_conjoint_variations: "",
  conjoint_invalidite: "",
  //: Le mois où la propre retraite du conjoint prend effet (AAAA ou AAAA-MM),
  //: s'il le dit : la limite de cumul de sa réversion d'avant juillet 2004
  //: s'applique alors, et sa majoration pour enfant à charge s'arrête.
  conjoint_retraite: "",
  //: Les précédents conjoints de l'assuré, divorcés, entre qui et le conjoint
  //: la réversion se partage : la naissance de chacun, le mariage, le divorce
  //: (AAAA ou AAAA-MM), et son remariage s'il le dit — que la réversion de la
  //: fonction publique et des complémentaires ne lui laisse pas, quand il
  //: précède le décès de l'assuré.
  ex_conjoints: Object.freeze([]),
  //: Le décès de l'assuré (AAAA ou AAAA-MM), qui ouvre la réversion de son
  //: conjoint : au départ ou après lui.
  deces: "",
  //: La retraite progressive (fiche `retraite_progressive`) : l'âge où elle
  //: prend effet, que l'adresse porte en date comme le départ, et la quotité du
  //: temps partiel gardé jusqu'au départ, en pour cent. Nul sans retraite
  //: progressive, et la quotité nulle quand l'adresse ne la porte pas : une
  //: quotité de zéro se refuse, elle ne vaut pas absence.
  progressive: null,
  quotite_progressive: null,
  //: L'activité exercée après le départ, le cumul emploi-retraite (fiche
  //: `cumul_emploi_retraite_et_retraite_progressive`) : l'âge où elle commence
  //: et celui où elle finit, que l'adresse porte en dates comme le départ ; son
  //: statut et son revenu, dans l'unité de la saisie — ceux du dernier métier
  //: quand ils ne sont pas dits — ; et l'employeur, le dernier ou un autre. Nul
  //: sans activité après le départ.
  emploi_retraite: null,
  emploi_retraite_fin: null,
  emploi_retraite_statut: "",
  emploi_retraite_salaire: null,
  emploi_retraite_employeur: "autre",
  //: Les pensions dont l'assuré dit la date de demande : pour chaque régime,
  //: `[code, âge]`, l'âge où il la demande, que l'adresse porte en date comme
  //: le départ (`PREFIXE_DEMANDE`). Vide, la présomption
  //: `depart_de_chaque_regime` date chaque pension (fiche
  //: `liquidation_regime_par_regime`).
  demandes: Object.freeze([]),
  //: L'invalidité et l'inaptitude (fiches `pension_d_invalidite_substituee`,
  //: `inaptitude_au_travail` et `retraite_pour_invalidite_fonction_publique`) :
  //: l'âge où la pension d'invalidité de la Sécurité sociale a commencé, que
  //: l'adresse porte en date comme un début d'activité, nul sans elle, et sa
  //: catégorie, 1, 2 ou 3 (L. 341-4), nulle quand elle n'est pas dite ;
  //: l'inaptitude au travail, reconnue ou que la loi présume ; l'âge de la
  //: radiation des cadres pour invalidité d'un fonctionnaire, en date lui
  //: aussi, son imputabilité au service et le taux d'invalidité reconnu, en
  //: pour cent ; l'âge depuis lequel l'incapacité permanente atteint 50 %
  //: (fiche `retraite_anticipee_handicap`), en date lui aussi. Voir
  //: `invaliditeDeclaree`.
  invalidite: null,
  categorie_invalidite: null,
  inaptitude: false,
  radiation_invalidite: null,
  invalidite_imputable: false,
  taux_invalidite: null,
  handicap: null,
  //: Les autres titres au taux plein de L. 351-8 (fiches `taux_plein_*` ;
  //: `droit/categories.js`) : la carte de déporté ou interné (3°), les mois de
  //: captivité et de services militaires en temps de guerre de l'ancien
  //: prisonnier ou combattant (5°), nuls sans eux, et le travail manuel des
  //: quinze années qui précèdent le départ (4°, et l'article 70-2 du décret de
  //: 1945 avant 1983), vide sans lui.
  deporte: false,
  mois_de_guerre: null,
  travail_manuel: "",
  //: L'activité du micro-entrepreneur, qui fait lire le revenu de ses lignes
  //: comme un chiffre d'affaires (`ACTIVITES_MICRO`) ; vide, comme un revenu
  //: déjà abattu.
  micro: "",
  //: « majore » fait lire le revenu des périodes payées à l'indice comme un
  //: indice majoré (`INDICES`) ; vide, comme une rémunération.
  indice: "",
  //: Le barème de la Lodeom de l'employeur d'outre-mer (`BAREMES_LODEOM`), que
  //: portent tous les emplois, métiers et lignes du relevé ; vide, la réduction
  //: générale.
  lodeom: "",
  //: L'option du conjoint collaborateur (`ASSIETTES_COLLABORATEUR`) ; vide, le
  //: forfait. Voir `assietteDuCollaborateur`.
  collaborateur: "",
  //: La réversion que le régime des non-salariés agricoles sert à l'assuré,
  //: veuf d'un de ses assurés (fiche `pension_majoree_reference` ; action 138,
  //: étape 8) : le mois où elle commence (AAAA ou AAAA-MM) et son montant
  //: mensuel brut de ce mois, en euros, nul quand les ressources l'absorbent ;
  //: vide, la présomption
  //: `pas_de_reversion_agricole`. Voir `reversionAgricoleDeclaree`.
  reversion_agricole: "",
  reversion_agricole_mensuel: null,
  //: Les carrières hors de France (fiches
  //: `totalisation_des_periodes_etrangeres`, `pension_proratisee`,
  //: `minimum_contributif_international` et `residence_et_minimum_vieillesse`) :
  //: les périodes passées hors de France
  //: — `{pays, debut, fin, activite}`, les âges comptés comme un début
  //: d'activité —, les pensions étrangères — `{pays, montant, debut}` —,
  //: l'État où la personne réside après son départ, vide quand c'est la
  //: France, et, pour qui y réside, les mois qu'elle y passe chaque année,
  //: `null` quand elle ne le dit pas. Voir `etrangerDeclare`.
  etranger: Object.freeze([]),
  pensions_etrangeres: Object.freeze([]),
  residence: "",
  mois_en_france: null,
  //: Les périodes assimilées que la personne déclare (fiches
  //: `stages_formation_professionnelle`, `tuc_stages_insertion`,
  //: `sportifs_haut_niveau` et `conge_supplementaire_naissance`) — `{motif,
  //: debut, fin, dispositif, jours}`, les dates telles qu'elles sont dites —, et
  //: le rang de la ligne de carrière qui est un contrat d'apprentissage (fiche
  //: `apprentissage`), `null` sans lui. Voir `periodesAssimileesDeclarees`.
  assimilees: Object.freeze([]),
  apprentissage: null,
  // Le revenu fiscal de référence du foyer, en euros, s'il le dit : il fixe le
  // taux de CSG de sa pension (action 138, étape 2). `null` : la présomption
  // `aucun_autre_revenu_que_ses_pensions`.
  revenu_fiscal: null,
  interruptions: "",
  // Les années travaillées à temps partiel et leur quotité, en pour cent :
  // « 2005:2014:80 » (fiche `temps_partiel_fonction_publique`). Les revenus
  // saisis sont ceux d'un temps plein, que ces années touchent à leur quotité ;
  // la fonction publique les compte à leur quotité dans ses services, en entier
  // dans la durée d'assurance. Voir `tempsPartielAnalyse`.
  temps_partiel: "",
  // Les années où l'indépendant est dispensé de l'assiette minimale, et le
  // motif de la dispense : « 2016:2019:rsa » (fiche
  // `assiette_minimale_independants` ; les motifs sont ceux de
  // `legislation/dispenses_assiette_minimale.yaml`). Toute activité de ces
  // années le porte, d'un relevé ou des métiers, et la règle ne le retient que
  // là où le texte dispense le statut. Voir `dispensesAnalysees`.
  dispenses: "",
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
  // système 4. Le défaut est la personne seule, comme pour l'ASPA du système 1,
  // de sorte que les deux planchers se comparent.
  foyer: "seul",
  projection: "cor_reference",
  //: L'hypothèse d'espérance de vie de l'INSEE, que le diviseur lit.
  esperance_vie: "centrale",
  //: L'emploi projeté : la trajectoire du COR par défaut, ou constant.
  emploi: "cor_2026",
  //: Les pensions déjà servies à la bascule : sur les prix, ou réindexées.
  stock: "prix",
  // Part de l'avance de la garantie que la succession couvre, en pour cent ;
  // null, elle est calculée sur le patrimoine des ménages retraités.
  reprise: null,
  // Les frais du pilier capitalisé : marché 2025 et baisse par paliers, ou
  // l'une des variantes qui disent ce que chaque hypothèse déplace.
  frais: "paliers",
  //: Les taux futurs du pilier : les taux à terme de la courbe, ou l'une des
  //: deux variantes qui en retirent une prime de terme. C'est le seul réglage
  //: sous lequel l'allocation des maturités change quelque chose.
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
   * `saisieRefusee`. `presomptions` est la table du paquet où lire ce que la
   * saisie présume — le jour de naissance, l'âge du mariage — ; la page et le
   * pont la passent toujours. Sans elle, une naissance sans jour ne se lit pas,
   * et le décès ne se confronte pas au mariage présumé.
   */
  static depuisRequete(parametres, tolerante = false, presomptions = null) {
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
    // La naissance se vérifie avant que le calendrier n'en date rien. Un mois
    // hors de l'année, une année dont le rang des mois — l'année fois douze —
    // passe le plus grand nombre (« naissance=1e308 ») faisaient lever au
    // calendrier sa propre erreur, « mois attendu entre 1 et 12, reçu NaN », et
    // la page disait « Le calcul a échoué » au lieu du refus : ils ne se lisent
    // pas, même sans rien vérifier. Une année hors du champ que le calendrier
    // sait dater ne se refuse que vérifiée : la saisie refusée la remontre.
    // L'année se cite telle que l'adresse la porte : « 1e21 », que JavaScript
    // écrirait « 1e+21 », et que ses chiffres trahiraient au-delà de 2⁵³.
    if (!(moisNaissance >= 1 && moisNaissance <= 12)) {
      throw refusDuMoisDeNaissance();
    }
    const horsDuChamp = !(anneeNaissance >= NAISSANCE_MINIMALE
      && anneeNaissance <= NAISSANCE_MAXIMALE);
    if ((horsDuChamp && !tolerante) || !Number.isFinite(anneeNaissance * MOIS_PAR_AN)) {
      throw refusDeLAnneeDeNaissance(
        naissance ? anneeNaissance : String(parametres.naissance).trim());
    }
    // Le jour, s'il est dit ; présumé si l'adresse porte la naissance sans lui
    // (`presomptions`, la table du paquet) ; celui du formulaire vierge si elle
    // ne la porte pas du tout.
    let jourNaissance = DEFAUTS.naissance_jour;
    let jourPresume = false;
    const porte = (cle) => parametres[cle] !== undefined && parametres[cle] !== null
      && parametres[cle] !== "";
    if (naissance && naissance.jour !== null) {
      jourNaissance = naissance.jour;
    } else if (porte("naissance") || porte("naissance_mois")) {
      jourNaissance = valeurPresumee("jour_de_naissance", presomptions);
      jourPresume = true;
    }
    const moisDeNaissance = new DateMois(anneeNaissance, moisNaissance);
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
      ...Object.fromEntries(CHAMPS_ESTIMATION.map((nom) => [nom,
        [undefined, null, ""].includes(parametres[nom]) ? null : reel(parametres, nom, 0.0)])),
      naissance: anneeNaissance,
      naissance_mois: moisNaissance,
      naissance_jour: jourNaissance,
      naissance_jour_presume: jourPresume,
      sexe: parametres.sexe === "F" ? "F" : "H",
      statut,
      debut: ageSaisi(parametres, "debut", DEFAUTS.debut, moisDeNaissance),
      liquidation: ageSaisi(parametres, "liquidation", DEFAUTS.liquidation,
        origineDesAges(moisDeNaissance, jourNaissance)),
      salaire,
      metiers: metiersSaisis(parametres, salaire, moisDeNaissance, tolerante),
      releve: (parametres.releve || "").trim(),
      profil: parmi(parametres, "profil", PROFILS, DEFAUTS.profil),
      primes: reel(parametres, "primes", DEFAUTS.primes),
      enfants: entier(parametres, "enfants", DEFAUTS.enfants),
      naissances: (parametres.naissances || "").trim(),
      charge_enfants: String(parametres.charge_enfants ?? "").trim(),
      conjoint: (parametres.conjoint || "").trim(),
      conjoint_sexe: (parametres.conjoint_sexe || "").trim().toUpperCase(),
      mariage: (parametres.mariage || "").trim(),
      ressources_conjoint: [undefined, null, ""].includes(parametres.ressources_conjoint)
        ? null : reel(parametres, "ressources_conjoint", 0.0),
      activite_conjoint: [undefined, null, ""].includes(parametres.activite_conjoint)
        ? null : reel(parametres, "activite_conjoint", 0.0),
      activite_conjoint_fin: String(parametres.activite_conjoint_fin ?? "").trim(),
      activite_conjoint_variations: String(parametres.activite_conjoint_variations ?? "")
        .trim(),
      nouvelle_union: (parametres.nouvelle_union || "").trim(),
      ressources_nouveau_conjoint: [undefined, null, ""].includes(
        parametres.ressources_nouveau_conjoint)
        ? null : reel(parametres, "ressources_nouveau_conjoint", 0.0),
      nouvelle_union_depuis: String(parametres.nouvelle_union_depuis ?? "").trim(),
      nouvelle_union_fin: String(parametres.nouvelle_union_fin ?? "").trim(),
      ressources_nouveau_conjoint_variations: String(
        parametres.ressources_nouveau_conjoint_variations ?? "").trim(),
      ex_conjoints: exConjointsSaisis(parametres, tolerante),
      revenu_fiscal: [undefined, null, ""].includes(parametres.revenu_fiscal)
        ? null : reel(parametres, "revenu_fiscal", 0.0),
      conjoint_invalidite: (parametres.conjoint_invalidite || "").trim(),
      conjoint_retraite: (parametres.conjoint_retraite || "").trim(),
      deces: (parametres.deces || "").trim(),
      progressive: [undefined, null, ""].includes(parametres.progressive) ? null
        : ageSaisi(parametres, "progressive", 0.0,
          origineDesAges(moisDeNaissance, jourNaissance)),
      quotite_progressive: [undefined, null, ""].includes(parametres.quotite)
        ? null : entier(parametres, "quotite", 0),
      emploi_retraite: [undefined, null, ""].includes(parametres.emploi_retraite) ? null
        : ageSaisi(parametres, "emploi_retraite", 0.0,
          origineDesAges(moisDeNaissance, jourNaissance)),
      emploi_retraite_fin: [undefined, null, ""].includes(parametres.emploi_retraite_fin)
        ? null
        : ageSaisi(parametres, "emploi_retraite_fin", 0.0,
          origineDesAges(moisDeNaissance, jourNaissance)),
      emploi_retraite_statut: (parametres.emploi_retraite_statut || "").trim(),
      emploi_retraite_salaire: [undefined, null, ""].includes(
        parametres.emploi_retraite_salaire)
        ? null : reel(parametres, "emploi_retraite_salaire", 0.0),
      emploi_retraite_employeur: parmi(parametres, "emploi_retraite_employeur",
        EMPLOYEURS_APRES_DEPART, "autre"),
      demandes: demandesSaisies(parametres, origineDesAges(moisDeNaissance, jourNaissance)),
      invalidite: [undefined, null, ""].includes(parametres.invalidite) ? null
        : ageSaisi(parametres, "invalidite", 0.0, moisDeNaissance),
      categorie_invalidite: [undefined, null, ""].includes(parametres.categorie_invalidite)
        ? null : entier(parametres, "categorie_invalidite", 0),
      inaptitude: oui(parametres, "inaptitude"),
      radiation_invalidite: [undefined, null, ""].includes(parametres.radiation_invalidite)
        ? null : ageSaisi(parametres, "radiation_invalidite", 0.0, moisDeNaissance),
      invalidite_imputable: oui(parametres, "invalidite_imputable"),
      taux_invalidite: [undefined, null, ""].includes(parametres.taux_invalidite)
        ? null : entier(parametres, "taux_invalidite", 0),
      handicap: [undefined, null, ""].includes(parametres.handicap) ? null
        : ageSaisi(parametres, "handicap", 0.0, moisDeNaissance),
      deporte: oui(parametres, "deporte"),
      mois_de_guerre: [undefined, null, ""].includes(parametres.guerre) ? null
        : entier(parametres, "guerre", 0),
      travail_manuel: parmi(parametres, "travail_manuel", TRAVAUX_MANUELS, ""),
      micro: parmi(parametres, "micro", ACTIVITES_MICRO, ""),
      indice: parmi(parametres, "indice", INDICES, ""),
      lodeom: parmi(parametres, "lodeom", BAREMES_LODEOM, ""),
      collaborateur: parmi(parametres, "collaborateur", ASSIETTES_COLLABORATEUR, ""),
      reversion_agricole: (parametres.reversion_agricole || "").trim(),
      reversion_agricole_mensuel: [undefined, null, ""].includes(
        parametres.reversion_agricole_mensuel)
        ? null : reel(parametres, "reversion_agricole_mensuel", 0.0),
      etranger: periodesEtrangeresSaisies(parametres, moisDeNaissance, tolerante),
      pensions_etrangeres: pensionsEtrangeresSaisies(parametres, moisDeNaissance, tolerante),
      residence: (parametres.residence || "").trim(),
      mois_en_france: [undefined, null, ""].includes(parametres.mois_en_france)
        ? null : entier(parametres, "mois_en_france", MOIS_PAR_AN),
      assimilees: periodesAssimileesSaisies(parametres, tolerante),
      apprentissage: [undefined, null, ""].includes(parametres.apprentissage)
        ? null : entier(parametres, "apprentissage", 1),
      interruptions: (parametres.interruptions || "").trim(),
      temps_partiel: (parametres.temps_partiel || "").trim(),
      dispenses: (parametres.dispenses || "").trim(),
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
      esperance_vie: parmi(parametres, "esperance_vie", HYPOTHESES_ESPERANCE_VIE,
        DEFAUTS.esperance_vie),
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
    // La table des présomptions, que la vérification du décès lit : hors des
    // champs, elle ne passe pas dans l'adresse.
    Object.defineProperty(saisie, "presomptions", { value: presomptions, enumerable: false });
    if (!tolerante) { saisie.verifier(); }
    return saisie;
  }

  verifier() {
    if (!(this.naissance_mois >= 1 && this.naissance_mois <= 12)) {
      throw refusDuMoisDeNaissance();
    }
    if (!(this.naissance_jour >= 1 && this.naissance_jour <= 31)) {
      throw new ErreurSaisie("Jour de naissance attendu entre 1 et 31.");
    }
    if (!(this.naissance >= NAISSANCE_MINIMALE && this.naissance <= NAISSANCE_MAXIMALE)) {
      throw refusDeLAnneeDeNaissance(this.naissance);
    }
    // Le jour compte désormais : un 31 février, qu'aucun calendrier ne propose
    // mais qu'une adresse peut porter, se refuse ici.
    const date = new Date(Date.UTC(this.naissance, this.naissance_mois - 1,
      this.naissance_jour));
    if (date.getUTCMonth() !== this.naissance_mois - 1) {
      throw new ErreurSaisie(
        `Date de naissance impossible : le ${this.naissance_jour} `
        + `${NOMS_DE_MOIS[this.naissance_mois - 1]} ${this.naissance} n'existe pas.`,
      );
    }
    // Une carrière commencée hors de France commence à sa première période à
    // l'étranger : le premier emploi en France peut alors venir après l'âge de
    // début le plus tardif.
    const commencee = Math.min(this.debut, ...this.etranger
      .filter((periode) => periode.debut >= AGE_DEBUT_MINIMAL).map((periode) => periode.debut));
    if (!(this.debut >= AGE_DEBUT_MINIMAL && commencee <= AGE_DEBUT_MAXIMAL)) {
      throw new ErreurSaisie(
        "Début d'activité : le modèle l'accepte de "
        + `${AGE_DEBUT_MINIMAL} à ${AGE_DEBUT_MAXIMAL} ans, soit `
        + `${this.fenetre(AGE_DEBUT_MINIMAL, AGE_DEBUT_MAXIMAL)}, et plus tard `
        + "quand la carrière a commencé hors de France dans ces âges.",
      );
    }
    if (!(this.liquidation >= AGE_LIQUIDATION_MINIMAL
          && this.liquidation <= AGE_LIQUIDATION_MAXIMAL)) {
      throw new ErreurSaisie(
        "Départ à la retraite : le modèle l'accepte de "
        + `${AGE_LIQUIDATION_MINIMAL} à ${AGE_LIQUIDATION_MAXIMAL} ans, soit `
        + `${this.fenetre(AGE_LIQUIDATION_MINIMAL, AGE_LIQUIDATION_MAXIMAL, true)}.`,
      );
    }
    const depart = this.dateDe(this.liquidation, true);
    if (depart.rang <= this.dateDe(this.debut).rang) {
      throw new ErreurSaisie(
        "Le départ à la retraite doit suivre le début d'activité, "
        + `fixé en ${this.dateDe(this.debut)}.`,
      );
    }
    this.verifierRevenu(this.salaire, 1, this.statut);
    if (!(this.primes >= 0 && this.primes <= 0.6)) {
      throw new ErreurSaisie("Part de primes attendue entre 0 et 0,6.");
    }
    if (!(this.enfants >= 0 && this.enfants <= ENFANTS_MAXIMUM)) {
      throw new ErreurSaisie(
        `Nombre d'enfants attendu entre 0 et ${ENFANTS_MAXIMUM}.`,
      );
    }
    if (this.revenu_fiscal !== null && this.revenu_fiscal < 0) {
      throw new ErreurSaisie("Revenu fiscal de référence : un montant annuel positif.");
    }
    this.tempsPartielAnalyse();
    this.dispensesAnalysees();
    this.verifierNaissances();
    this.prolongationsDeLaChargeDeclarees();
    this.verifierConjoint();
    this.verifierReversionAgricole();
    this.verifierProgressive();
    this.verifierEmploiRetraite();
    this.verifierDemandes();
    this.verifierInvalidite();
    this.verifierEtranger();
    this.verifierAssimilees();
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
    this._verifierEstimation();
    // Les métiers se suivent sans se recouvrir : chacun commence après le
    // précédent et avant le départ à la retraite. C'est la seule chose que le
    // moteur exige, et elle se dit ici plutôt que par une exception remontée du
    // modèle.
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
      if (this.dateDe(metier.debut).rang >= depart.rang) {
        throw new ErreurSaisie(
          `Métier n° ${rang} : il doit commencer avant le départ à la retraite, `
          + `fixé en ${depart}.`,
        );
      }
      this.verifierRevenu(metier.salaire, rang, metier.statut);
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
    const depart = this.dateDe(this.liquidation, true);
    if (this.dateDe(metier.debut).rang >= depart.rang) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : il doit commencer avant le départ à la retraite, `
        + `fixé en ${depart}.`,
      );
    }
    if (metier.fin !== null
        && !(metier.debut < metier.fin && this.dateDe(metier.fin).rang <= depart.rang)) {
      throw new ErreurSaisie(
        `Métier n° ${rang} : il doit s'arrêter après avoir commencé, et au plus `
        + `tard au départ, fixé en ${depart}.`,
      );
    }
    this.verifierRevenu(metier.salaire, rang, metier.statut);
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

  /**
   * L'estimation officielle recopiée : des montants mensuels, que le
   * formulaire borne à un euro au moins. Rien d'autre : c'est la page
   * officielle qui les a calculés, et la comparaison dira l'écart.
   */
  _verifierEstimation() {
    for (const nom of CHAMPS_ESTIMATION) {
      if (this[nom] !== null && !(this[nom] >= 1)) {
        throw new ErreurSaisie(
          "Votre estimation officielle : un montant brut mensuel, d'un euro au moins.");
      }
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
   * entendu parler de cette unité. Un indice majoré n'a pas d'unité : seul le
   * zéro s'y refuse ici, et ses bornes, au calcul (`verifierNiveau`).
   */
  verifierRevenu(valeur, rang, statut = "") {
    if (this.enIndice(statut)) {
      if (!(valeur > 0)) {
        throw refus(rang, "L'indice majoré doit être strictement positif.");
      }
      return;
    }
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

  /**
   * Le revenu de chaque métier, ramené à l'unité du modèle. C'est ici, et nulle
   * part ailleurs, que l'euro entre dans le modèle. Le moteur ne connaît que le
   * multiple du salaire moyen : il garde son sens sur quatre-vingts ans, quand
   * un montant n'en a que rapporté à son année.
   */
  niveaux(echelle) {
    return this.lignesCarriere.map((ligne) => this.niveauDe(ligne.salaire, ligne.statut,
      echelle));
  }

  /**
   * Le nombre saisi d'une ligne de ce statut, ramené à l'unité du modèle. Un
   * indice majoré vaut la rémunération de son traitement, en toute unité et en
   * tout mode : il n'est ni un brut ni un net.
   */
  niveauDe(valeur, statut, echelle) {
    if (this.enIndice(statut)) {
      return echelle.niveau(echelle.remuneration(valeur, this.primes));
    }
    if (!this.revenu_en_euros) {
      return valeur;
    }
    // En mode net, le nombre saisi n'est pas encore un brut : on remonte
    // d'abord jusqu'à lui, statut par statut, PUIS on ramène à l'unité du
    // modèle. L'ordre compte — le salaire moyen de l'échelle est un brut.
    // Un chiffre d'affaires n'est ni brut ni net : il se lit tel quel.
    if (this.saisieEnNet && !this.enChiffreDAffaires(statut)) {
      return echelle.niveau(echelle.brutMensuel(valeur, statut));
    }
    return echelle.niveau(valeur);
  }

  /**
   * Le revenu d'une ligne de ce statut est-il un chiffre d'affaires ? Celui du
   * micro-entrepreneur qui dit son activité. Une activité dite sans ligne de
   * micro-entrepreneur ne change rien : le formulaire la garde d'une saisie à
   * l'autre, et elle ne se refuse pas.
   */
  enChiffreDAffaires(statut) {
    return Boolean(this.micro) && statut === STATUT_MICRO;
  }

  /**
   * Le revenu d'une ligne de ce statut est-il un indice majoré ? Celui d'une
   * période payée à l'indice (`STATUTS_A_L_INDICE`), quand la saisie le dit.
   * Comme l'activité du micro-entrepreneur, le choix dit sans une telle période
   * ne change rien et ne se refuse pas.
   */
  enIndice(statut) {
    return this.indice === "majore" && A_L_INDICE.has(statut);
  }

  /**
   * Ce que cotise une ligne de ce statut au niveau du revenu saisi. Celle du
   * conjoint collaborateur porte le revenu du chef d'entreprise, dont elle ne
   * cotise que la part de son option (`PARTS_COLLABORATEUR`) : rien au forfait,
   * que le modèle donne alors au tiers du plafond. Le contrôle des bornes se
   * fait avant, sur le revenu saisi : c'est le nombre que le champ porte. Les
   * autres lignes gardent leur niveau.
   */
  assietteDuCollaborateur(niveau, statut) {
    if (!CONJOINTS_COLLABORATEURS.has(statut)) {
      return niveau;
    }
    return niveau * PARTS_COLLABORATEUR[this.collaborateur];
  }

  /**
   * Le niveau qu'essaie l'inversion par la pension, sur chaque métier : le même
   * revenu partout, que la ligne du conjoint collaborateur cotise comme un
   * revenu saisi (`assietteDuCollaborateur`) — au forfait, le niveau n'y change
   * rien.
   */
  niveauxDeLaPension(niveau, parcours) {
    return parcours.map((metier) => this.assietteDuCollaborateur(niveau, metier.affiliation));
  }

  /**
   * Ce qu'une ligne donne au modèle, `[niveau, statut]` : son revenu et son
   * statut. LE CHIFFRE D'AFFAIRES S'ABAT ICI, au seuil du modèle, et nulle part
   * avant : `niveaux` garde le nombre saisi, ramené à l'unité du modèle, pour
   * que la bascule d'unité le traduise sans le toucher. Le micro-entrepreneur de
   * la Cipav prend le statut du libéral, dont il a les régimes.
   */
  abattu(niveau, statut) {
    if (!this.enChiffreDAffaires(statut)) {
      return [niveau, statut];
    }
    return [niveau * (1.0 - ABATTEMENTS_MICRO[this.micro]), this.affiliationDe(statut)];
  }

  /** L'affiliation d'une ligne de ce statut, celle que `parcours` lui donne. */
  affiliationDe(statut) {
    return this.enChiffreDAffaires(statut) && this.micro === "cipav"
      ? STATUT_MICRO_CIPAV : statut;
  }

  /**
   * Le mois d'entrée dans cette affiliation, tel que la carrière le datera
   * (`Carriere.dateEntree`) : l'ouverture du premier métier qui la porte, ou
   * janvier de sa première année d'emploi sur le relevé (`anneeDEntree`), une
   * année d'interruption ne l'ouvrant pas ; `null` si elle n'y figure pas, ou
   * tant que le relevé ne se lit pas. C'est lui qui choisit la fiche de paie
   * d'un régime fermé aux nouveaux entrants, par laquelle un net remonte au
   * brut (`Contexte.echelle`) : l'agent de la SNCF entré avant 2020 garde sa
   * retenue, et non les cotisations d'un salarié du privé.
   */
  dateEntree(affiliation) {
    if (this.releveActif) {
      let lignes;
      try {
        lignes = this.releveAnalyse();
      } catch (erreur) {
        if (!(erreur instanceof ErreurSaisie)) throw erreur;
        return null;
      }
      const annee = anneeDEntree(lignes, affiliation);
      return annee === null ? null : new DateMois(annee, 1);
    }
    const debuts = this.lignesCarriere.filter((ligne) => !ligne.sans_emploi
      && this.affiliationDe(ligne.statut) === affiliation).map((ligne) => ligne.debut);
    return debuts.length ? this.dateDe(Math.min(...debuts)) : null;
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
      const micro = this.enChiffreDAffaires(ligne.statut) ? this.micro : "";
      const [niveau, statut] = this.abattu(niveaux[index], ligne.statut);
      this.verifierNiveau(niveau, index + 1, echelle, ligne.statut);
      metiers.push({
        affiliation: statut,
        age_debut: ligne.debut,
        niveau_salaire: this.assietteDuCollaborateur(niveau, statut),
        cumul: ligne.cumul,
        age_fin: ligne.fin,
        micro,
        apprentissage: index + 1 === this.apprentissage,
        lodeom: this.lodeom,
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
   * Une période passée hors de France en est une aussi, de motif
   * `sans_activite` : la carrière française n'y voit aucune activité, et ce que
   * la période vaut ailleurs, c'est son fait daté qui le porte, avec son État
   * (`etrangerDeclare`). Elle prend le pas sur une période sans emploi de la
   * même année, qu'elle précise.
   *
   * Le champ « Interruptions » garde le dernier mot : il désigne des années une
   * à une, et c'est l'outil le plus fin des deux.
   */
  interruptionsDeCarriere(motifsConnus = null) {
    const debut = this.dateDe(this.debut);
    const fin = this.dateDe(this.liquidation, true);
    const lignes = this.lignesCarriere;
    const creuxDeCarriere = [];
    lignes.forEach((ligne, index) => {
      if (!ligne.sans_emploi) { return; }
      // Une activité ajoutée ne clôt pas l'interruption : elle se tient à
      // côté. C'est la période principale suivante qui la clôt.
      const suivante = lignes.slice(index + 1).find((autre) => !autre.cumul);
      creuxDeCarriere.push([ligne.statut, this.dateDe(ligne.debut),
        suivante ? this.dateDe(suivante.debut) : fin]);
    });
    creuxDeCarriere.push(...this.creuxALEtranger(debut, fin));
    const annees = anneesCreuses(creuxDeCarriere, debut, fin);
    this.interruptionsAnalysees(motifsConnus).forEach((motif, annee) => {
      annees.set(annee, motif);
    });
    return annees;
  }

  /**
   * Les années non cotisées d'une carrière qui se poursuit de `depuis` au
   * départ : celle d'un relevé, dont la dernière année se prolonge
   * (`prolongerReleve`). Ce sont celles d'une carrière de métiers, moins les
   * métiers, qu'un relevé remplace : une période passée hors de France, puis
   * le champ « Interruptions », qui garde le dernier mot.
   */
  interruptionsApres(depuis, motifsConnus = null) {
    const fin = this.dateLiquidation;
    const annees = anneesCreuses(this.creuxALEtranger(depuis, fin), depuis, fin);
    this.interruptionsAnalysees(motifsConnus).forEach((motif, annee) => {
      annees.set(annee, motif);
    });
    return annees;
  }

  /**
   * Les périodes passées hors de France, en creux `sans_activite` de la
   * carrière qui court de `debut` à `fin`. Une période ne compte que pour les
   * mois de la carrière qu'elle couvre : celle qui précède le premier emploi
   * en France n'en interrompt aucun.
   */
  creuxALEtranger(debut, fin) {
    const creux = [];
    for (const periode of this.etranger) {
      const debutPeriode = this.dateDe(periode.debut);
      const finPeriode = this.dateDe(periode.fin);
      const ouverture = debutPeriode.rang > debut.rang ? debutPeriode : debut;
      const cloture = finPeriode.rang < fin.rang ? finPeriode : fin;
      if (cloture.rang > ouverture.rang) {
        creux.push(["sans_activite", ouverture, cloture]);
      }
    }
    return creux;
  }

  /**
   * Le salaire converti tient-il dans ce que le modèle sait décrire ? Le
   * contrôle ne peut se faire qu'ici : « 0,1 à 10 fois le salaire moyen » ne
   * devient un intervalle d'euros qu'une fois la série chargée. Le refus redit
   * donc les bornes en euros, faute de quoi il n'indiquerait pas quoi corriger.
   */
  verifierNiveau(niveau, rang, echelle, statut = "") {
    if (niveau >= 0.1 && niveau <= 10) {
      return;
    }
    if (this.enIndice(statut)) {
      // Les bornes valent pour la rémunération : le refus les redit en indices,
      // le nombre que le champ porte, et ceux qu'il nomme sont acceptés.
      const [bas, haut] = echelle.indicesDansLesBornes(this.primes);
      throw refus(
        rang,
        `Cet indice majoré vaut ${g.nombre(niveau, 2)} fois le salaire moyen, `
        + "primes comprises ; le modèle en accepte de 0,1 à 10 fois, soit un indice "
        + `majoré de ${g.nombre(bas, 0)} à ${g.nombre(haut, 0)}.`,
      );
    }
    if (this.enChiffreDAffaires(statut)) {
      // Les bornes valent pour le revenu abattu : le refus les redit en chiffre
      // d'affaires, le nombre que le champ porte.
      const part = 1.0 - ABATTEMENTS_MICRO[this.micro];
      if (!this.revenu_en_euros) {
        throw refus(
          rang,
          `Ce chiffre d'affaires, abattu à ${g.nombre(100 * part, 0)} %, `
          + `vaut ${g.nombre(niveau, 2)} fois le salaire moyen ; le modèle `
          + "en accepte de 0,1 à 10 fois, soit un chiffre d'affaires de "
          + `${g.nombre(NIVEAU_MINIMAL / part, 2)} à `
          + `${g.nombre(NIVEAU_MAXIMAL / part, 2)} fois le salaire moyen.`,
        );
      }
      throw refus(
        rang,
        `Ce chiffre d'affaires, abattu à ${g.nombre(100 * part, 0)} %, `
        + `vaut ${g.nombre(niveau, 2)} fois le salaire moyen ; le modèle en `
        + "accepte de 0,1 à 10 fois, soit un chiffre d'affaires de "
        + `${g.nombre(Math.ceil(echelle.mensuel(NIVEAU_MINIMAL) / part), 0)} à `
        + `${g.euros(Math.floor(echelle.mensuel(NIVEAU_MAXIMAL) / part))} par mois.`,
      );
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
      + `${g.nombre(echelle.eurosDansLesBornes(NIVEAU_MINIMAL), 0)} à `
      + `${g.euros(echelle.eurosDansLesBornes(NIVEAU_MAXIMAL))} bruts par mois.`,
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
      hypothese_esperance_vie: this.esperance_vie,
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
      // `Number`, et le refus nommerait une année que personne n'a écrite.
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

  /**
   * « 2005:2014:80, 2016:2016:50 » → `Map` année → quotité, entre zéro et un.
   * La forme est celle des interruptions, la quotité en pour cent à la place
   * du motif : un entier de 1 à 99, cent étant le temps plein, que rien ne
   * déclare. Les refus sont les leurs — une ligne mal formée, une année hors de
   * toute carrière possible, une plage à l'envers —, et un de plus : deux
   * quotités pour une même année, que rien ne départage. Une année
   * d'interruption n'a pas de quotité : l'interruption la prend tout entière
   * (fiche `temps_partiel_fonction_publique`).
   */
  tempsPartielAnalyse() {
    const quotites = new Map();
    for (const brut of this.temps_partiel.replace(/\n/g, ",").split(",")) {
      const morceau = brut.trim();
      if (!morceau) {
        continue;
      }
      const parties = morceau.split(":");
      if (parties.length !== 3 || !parties.every((partie) => estEntier(partie))) {
        throw new ErreurSaisie(
          `Temps partiel mal formé : « ${morceau} ». Attendu `
          + "« année_début:année_fin:quotité », par exemple 2005:2014:80.",
        );
      }
      const [debut, fin, quotite] = parties.map(Number);
      // Les années sont citées telles qu'elles ont été écrites, comme celles
      // d'une interruption : les deux moteurs disent la même phrase.
      for (const [texte, annee] of [[parties[0], debut], [parties[1], fin]]) {
        if (!(annee >= ANNEE_CARRIERE_MINIMALE && annee <= ANNEE_CARRIERE_MAXIMALE)) {
          throw new ErreurSaisie(
            `Temps partiel « ${morceau} » : ${texte.trim()} ne tombe dans aucune `
            + `carrière possible. Attendu entre ${ANNEE_CARRIERE_MINIMALE} et `
            + `${ANNEE_CARRIERE_MAXIMALE}.`,
          );
        }
      }
      if (fin < debut) {
        throw new ErreurSaisie(
          `Temps partiel « ${morceau} » : il finit (${fin}) avant de `
          + `commencer (${debut}).`,
        );
      }
      if (!(quotite >= 1 && quotite <= 99)) {
        throw new ErreurSaisie(
          `Temps partiel « ${morceau} » : quotité attendue entre 1 et `
          + "99 %, le temps plein n'ayant rien à déclarer.",
        );
      }
      for (let annee = debut; annee <= fin; annee += 1) {
        if (quotites.has(annee)) {
          throw new ErreurSaisie(
            `Temps partiel « ${morceau} » : l'année ${annee} a déjà `
            + "sa quotité.",
          );
        }
        quotites.set(annee, quotite / 100.0);
      }
    }
    return quotites;
  }

  /**
   * « 2016:2019:rsa, 2020:2020:activite_saisonniere » → `Map` année → motif.
   * La forme est celle des interruptions, et leurs refus — une ligne mal formée
   * ou sans motif, une année hors de toute carrière possible, une plage à
   * l'envers, un motif inconnu de `motifsConnus`, que l'appelant lit dans le
   * paquet et sans lesquels le motif n'est pas contrôlé —, et un de plus : deux
   * motifs pour une même année. Un motif dit hors des années où le texte
   * dispense ne se refuse pas : il est sans effet (`dispenseAssietteMinimale`,
   * `carriere.js`).
   */
  dispensesAnalysees(motifsConnus = null) {
    const connus = motifsConnus === null ? null : [...motifsConnus].sort();
    const motifs = new Map();
    for (const brut of this.dispenses.replace(/\n/g, ",").split(",")) {
      const morceau = brut.trim();
      if (!morceau) {
        continue;
      }
      const parties = morceau.split(":");
      if (parties.length !== 3 || !parties.slice(0, 2).every((partie) => estEntier(partie))
        || !parties[2].trim()) {
        throw new ErreurSaisie(
          `Dispense mal formée : « ${morceau} ». Attendu `
          + "« année_début:année_fin:motif », par exemple 2016:2019:rsa.",
        );
      }
      const [debut, fin] = parties.slice(0, 2).map(Number);
      const motif = parties[2].trim();
      // Les années sont citées telles qu'elles ont été écrites, comme celles
      // d'une interruption : les deux moteurs disent la même phrase.
      for (const [texte, annee] of [[parties[0], debut], [parties[1], fin]]) {
        if (!(annee >= ANNEE_CARRIERE_MINIMALE && annee <= ANNEE_CARRIERE_MAXIMALE)) {
          throw new ErreurSaisie(
            `Dispense « ${morceau} » : ${texte.trim()} ne tombe dans aucune `
            + `carrière possible. Attendu entre ${ANNEE_CARRIERE_MINIMALE} et `
            + `${ANNEE_CARRIERE_MAXIMALE}.`,
          );
        }
      }
      if (fin < debut) {
        throw new ErreurSaisie(
          `Dispense « ${morceau} » : elle finit (${fin}) avant de `
          + `commencer (${debut}).`,
        );
      }
      if (connus !== null && !connus.includes(motif)) {
        throw new ErreurSaisie(
          `Dispense « ${morceau} » : motif inconnu « ${motif} ». `
          + `Attendu l'un de : ${connus.join(", ")}.`,
        );
      }
      for (let annee = debut; annee <= fin; annee += 1) {
        if (motifs.has(annee)) {
          throw new ErreurSaisie(
            `Dispense « ${morceau} » : l'année ${annee} a déjà son motif.`,
          );
        }
        motifs.set(annee, motif);
      }
    }
    return motifs;
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
    return this.dateDe(this.liquidation, true);
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
   * référence d'avant l'interruption. **Les années à temps partiel** se
   * déclarent de même, dans le champ « Temps partiel » : la ligne en prend la
   * quotité, et garde son revenu, que le relevé porte déjà réduit. **Les
   * dispenses de l'assiette minimale**, dans le leur : la ligne d'emploi en
   * prend le motif (`dispensesAnalysees`, que `dispensesConnues` contrôle).
   */
  releveAnalyse(motifsConnus = null, dispensesConnues = null) {
    const interruptions = this.interruptionsAnalysees(motifsConnus);
    const tempsPartiel = this.tempsPartielAnalyse();
    const dispenses = this.dispensesAnalysees(dispensesConnues);
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
      // passé par `Number`, et le refus nommerait une année que personne n'a
      // écrite.
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
        // Une fraction se déclare des services de la fonction publique, qui
        // se comptent au jour : « 3.33 » dit dix mois (R. 26). Le contexte
        // refuse la fraction d'un autre statut.
        const valeur = versFlottant(parties[3]);
        if (valeur === null || !(valeur >= 0 && valeur <= 4)) {
          throw new ErreurSaisie(
            `Relevé « ${morceau} » : trimestres attendus entre 0 et 4.`,
          );
        }
        trimestres = valeur;
      }
      const typePeriode = interruptions.get(annee) ?? "emploi";
      lignes.push({
        annee,
        affiliation: parties[1],
        revenu,
        trimestres,
        type_periode: typePeriode,
        quotite: typePeriode === "emploi" ? tempsPartiel.get(annee) ?? 1.0 : 1.0,
        dispense_assiette_minimale: typePeriode === "emploi" ? dispenses.get(annee) ?? "" : "",
        lodeom: typePeriode === "emploi" ? this.lodeom : "",
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

  /**
   * Le mois où la carrière atteint cet âge : celui d'un début d'activité,
   * compté du mois de naissance, ou, avec `depart`, celui du départ, compté du
   * mois où l'âge est révolu ({@link origineDesAges}) : né le 15 mars 1962, on
   * part à soixante-quatre ans au 1er avril 2026 (R. 351-37). Un âge de départ
   * et un âge de début ne se comparent donc qu'en dates.
   */
  dateDe(age_, depart = false) {
    const origine = depart
      ? this.origineDesAges
      : new DateMois(this.naissance, this.naissance_mois);
    return origine.plusMois(enMois(age_));
  }

  /**
   * Le jour de naissance tel que la carrière le reçoit : nul quand il est
   * présumé, pour que la chronologie le présume en son nom.
   */
  get jourDeclare() {
    return this.naissance_jour_presume ? null : this.naissance_jour;
  }

  /** Le mois d'où les âges se comptent : voir `origineDesAges` du calendrier. */
  get origineDesAges() {
    return origineDesAges(new DateMois(this.naissance, this.naissance_mois),
      this.naissance_jour);
  }

  /** Le même mois, tel que l'adresse le porte : « 1996-09 ». */
  moisDe(age_, depart = false) {
    const date = this.dateDe(age_, depart);
    return `${cadrer(date.annee, 4)}-${cadrer(date.mois, 2)}`;
  }

  /** Le même mois au premier jour : ce qu'un champ date, lui, exige. */
  jourDe(age_, depart = false) {
    return `${this.moisDe(age_, depart)}-01`;
  }

  /**
   * « de septembre 1989 à septembre 2015 » : deux bornes d'âge, en dates.
   *
   * Un refus qui ne parlerait que d'âges laisserait au lecteur la soustraction
   * à faire, alors que le champ qu'il vient de remplir porte une date.
   */
  fenetre(ageMinimal, ageMaximal, depart = false) {
    return `de ${this.dateDe(ageMinimal, depart)} à ${this.dateDe(ageMaximal, depart)}`;
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
      + `${NOMS_DE_MOIS[this.naissance_mois - 1]} ${this.naissance}`
      + (this.naissance_jour_presume ? " — jour présumé : l'adresse ne le disait pas" : "");
  }

  /** « en septembre 1984, soit 22 ans et 6 mois » : une date de carrière. */
  calculDe(age_, depart = false) {
    if (age_ < 0) {
      return `en ${this.dateDe(age_, depart)}, avant la date de naissance`;
    }
    return `en ${this.dateDe(age_, depart)}, soit ${age(age_)}`;
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
   * la naissance de l'assuré. Elle peut suivre son départ : la majoration pour
   * enfant à charge de la réversion compte l'enfant né après lui (R. 353-10) ;
   * c'est le décès qui la borne (`verifierConjoint`).
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
    }
  }

  /**
   * Ce qui prolonge la charge des enfants, tel que `avecProlongationsDeLaCharge`
   * le reçoit, une entrée du champ `charge_enfants` après l'autre, séparées
   * d'une virgule ou d'un point-virgule : le rang de l'`enfant`, de un au
   * nombre des enfants, dont la naissance est dite ; son `motif`, écrit avec
   * ses accents ou sans, une fois par enfant ; et la `fin` des études ou de
   * l'apprentissage, s'il la dit, après la naissance — l'infirmité ne finit
   * pas. Vide quand rien n'est dit, et la présomption
   * `charge_jusqu_a_l_age_limite` tient.
   */
  prolongationsDeLaChargeDeclarees() {
    const naissances = this.naissancesEnfants();
    const motifs = `${MOTIFS_DE_PROLONGATION.slice(0, -1).join(", ")} ou `
      + `${MOTIFS_DE_PROLONGATION.at(-1)}`;
    const dits = new Set();
    return this.charge_enfants.split(/[,;]/).map((entree) => entree.trim())
      .filter((entree) => entree)
      .map((entree) => {
        const refus = (raison) => new ErreurSaisie(
          `Enfant aux études, apprenti ou infirme « ${entree} » : ${raison}`);
        const morceaux = entree.split(":").map((morceau) => morceau.trim());
        if (morceaux.length < 2 || morceaux.length > 3 || !/^\d+$/.test(morceaux[0])) {
          throw refus("attendu en rang:motif ou rang:motif:fin, par exemple 1:etudes:2009-07.");
        }
        const enfant = Number(morceaux[0]);
        if (!(enfant >= 1 && enfant <= this.enfants)) {
          throw refus(`vous déclarez ${this.enfants} enfant${this.enfants > 1 ? "s" : ""}.`);
        }
        if (enfant > naissances.length) {
          throw refus("dites d'abord sa naissance, dans « Naissance des enfants ».");
        }
        const motif = morceaux[1].normalize("NFD").replace(/[\u0300-\u036f]/g, "")
          .toLowerCase();
        if (!MOTIFS_DE_PROLONGATION.includes(motif)) {
          throw refus(`son motif est ${motifs}.`);
        }
        if (dits.has(`${enfant}:${motif}`)) {
          throw refus(`ce motif est déjà dit pour l'enfant n° ${enfant}.`);
        }
        dits.add(`${enfant}:${motif}`);
        if (morceaux.length === 2) {
          return { enfant, motif, fin: null };
        }
        if (motif === "infirmite") {
          throw refus("l'infirmité ne finit pas ; seules les études et l'apprentissage "
            + "se datent.");
        }
        let fin;
        try {
          [fin] = dateDeclaree(morceaux[2], "sa fin");
        } catch {
          throw refus("sa fin attendue en AAAA, AAAA-MM ou AAAA-MM-JJ, par exemple 2009-07.");
        }
        if (fin <= naissanceDeclaree(naissances[enfant - 1])[0]) {
          throw refus("elle finit avant sa naissance.");
        }
        return { enfant, motif, fin: morceaux[2] };
      });
  }

  /**
   * Le conjoint que la saisie déclare, tel que la chronologie le reçoit
   * (`personne`, dans `chronologie.js`) ; `null` sans conjoint.
   */
  conjointDeclare() {
    if (!this.conjoint) {
      return null;
    }
    return {
      naissance: this.conjoint,
      sexe: this.conjoint_sexe || (this.sexe === "F" ? "H" : "F"),
      mariage: this.mariage || null,
      ressources: this.ressources_conjoint,
      revenus_d_activite: this.activite_conjoint,
      fin_d_activite: this.activite_conjoint_fin || null,
      variations_d_activite: this.variationsAnalysees("activite_conjoint_variations"),
      nouvelle_union: this.nouvelle_union || null,
      ressources_du_nouveau_conjoint: this.ressources_nouveau_conjoint,
      nouvelle_union_depuis: this.nouvelle_union_depuis || null,
      nouvelle_union_fin: this.nouvelle_union_fin || null,
      variations_du_nouveau_conjoint: this.variationsAnalysees(
        "ressources_nouveau_conjoint_variations"),
      invalidite: this.conjoint_invalidite || null,
      retraite: this.conjoint_retraite || null,
      ex_conjoints: this.ex_conjoints.map((ex) => ({
        naissance: ex.naissance, mariage: ex.mariage, divorce: ex.divorce,
        remariage: ex.remariage || null,
      })),
    };
  }

  /**
   * « 2032-06:9500, 2035-01:12000 » → `[[date, montant], …]`, dans l'ordre des
   * dates : les variations que dit le champ `nom` — les revenus d'activité du
   * conjoint (`activite_conjoint_variations`), ou les ressources de son nouveau
   * conjoint (`ressources_nouveau_conjoint_variations`) —, chacune une date, en
   * AAAA ou AAAA-MM, et le montant annuel, positif ou nul, à partir d'elle ;
   * au plus `VARIATIONS_MAXIMUM`, comptées avant d'être lues.
   */
  variationsAnalysees(nom) {
    const quoi = VARIATIONS_DE[nom];
    const morceaux = this[nom].replace(/\n/g, ",").split(",")
      .map((brut) => brut.trim())
      .filter((brut) => brut.length > 0);
    if (morceaux.length > VARIATIONS_MAXIMUM) {
      throw new ErreurSaisie(
        `Variations ${quoi} : ${morceaux.length}, le modèle en accepte `
        + `${VARIATIONS_MAXIMUM} au plus.`,
      );
    }
    const lues = [];
    for (const morceau of morceaux) {
      const parties = morceau.split(":").map((partie) => partie.trim());
      if (parties.length !== 2 || !parties[0]) {
        throw new ErreurSaisie(
          `Variation ${quoi} mal formée : « ${morceau} ». Attendu `
          + "« date:montant annuel », par exemple 2031-04:18000.",
        );
      }
      let jour;
      try {
        [jour] = dateDeclaree(parties[0], `la variation ${quoi}`);
      } catch {
        throw new ErreurSaisie(
          `La variation ${quoi} « ${parties[0]} » : attendu en AAAA ou AAAA-MM, `
          + "par exemple 1962 ou 1962-03.",
        );
      }
      const montant = versFlottant(parties[1]);
      if (montant === null || montant < 0) {
        throw new ErreurSaisie(
          `Variation ${quoi} « ${morceau} » : un montant annuel positif ou nul.`);
      }
      lues.push([jour, parties[0], montant]);
    }
    return lues.sort((a, b) => (a[0] < b[0] ? -1 : a[0] > b[0] ? 1 : 0))
      .map(([, date, montant]) => [date, montant]);
  }

  /** Le décès de l'assuré que la saisie déclare, ou `null`. */
  decesDeclare() {
    return this.deces || null;
  }

  /**
   * La réversion du régime des non-salariés agricoles que la saisie déclare,
   * telle que la chronologie la reçoit (`reversionAgricoleDeclaree`, dans
   * `chronologie.js`) : son `debut` et son montant `mensuel` en euros de ce
   * mois ; `null` sans elle.
   */
  reversionAgricoleDeclaree() {
    if (!this.reversion_agricole) {
      return null;
    }
    return { debut: this.reversion_agricole, mensuel: this.reversion_agricole_mensuel };
  }

  /**
   * La retraite progressive que la saisie déclare, telle que la chronologie la
   * reçoit : son âge et sa quotité, entre zéro et un ; `null` sans elle.
   */
  retraiteProgressiveDeclaree() {
    if (this.progressive === null) {
      return null;
    }
    return { age: this.progressive, quotite: this.quotite_progressive / 100.0 };
  }

  /**
   * La retraite progressive : une quotité de temps partiel, et une date entre
   * le début de la carrière et le départ. Que le droit l'ouvre — son âge, sa
   * durée, sa quotité —, c'est au calcul de le dire.
   */
  verifierProgressive() {
    if (this.progressive === null) {
      if (this.quotite_progressive !== null) {
        throw new ErreurSaisie(
          "« quotite » ne sert qu'à la retraite progressive : dites aussi sa date "
          + "(« progressive »).",
        );
      }
      return;
    }
    if (this.quotite_progressive === null
        || !(this.quotite_progressive >= 1 && this.quotite_progressive <= 99)) {
      throw new ErreurSaisie(
        "Quotité de la retraite progressive : le temps partiel gardé, en pour cent "
        + "d'un temps plein, entre 1 et 99.",
      );
    }
    if (enMois(this.progressive) >= enMois(this.liquidation)) {
      throw new ErreurSaisie(
        `Retraite progressive en ${this.dateDe(this.progressive, true)} : elle précède `
        + `le départ, fixé en ${this.dateDe(this.liquidation, true)}.`,
      );
    }
    if (this.dateDe(this.progressive, true).rang <= this.dateDe(this.debut).rang) {
      throw new ErreurSaisie(
        `Retraite progressive en ${this.dateDe(this.progressive, true)} : elle suit le `
        + "début de la carrière.",
      );
    }
  }

  /**
   * Le dernier métier de la carrière, hors activité ajoutée et hors période
   * sans emploi : celui que l'activité d'après le départ continue quand elle ne
   * dit pas son statut ou son revenu.
   */
  get dernierMetier() {
    const principaux = this.lignesCarriere.filter((ligne) => !ligne.cumul
      && !ligne.sans_emploi);
    return principaux.length ? principaux[principaux.length - 1] : this.lignesCarriere[0];
  }

  /**
   * L'activité exercée après le départ que la saisie déclare, telle que la
   * chronologie la reçoit : ses deux âges, son statut, son revenu en multiples
   * du salaire moyen, et l'employeur ; `null` sans elle. En euros ou en indice,
   * le revenu se convertit sur `echelle`, comme ceux des métiers (`niveaux`).
   */
  emploiRetraiteDeclare(echelle = null) {
    if (this.emploi_retraite === null) {
      return null;
    }
    const dernier = this.dernierMetier;
    const statut = this.emploi_retraite_statut || dernier.statut;
    const herite = this.emploi_retraite_salaire === null;
    let salaire = herite ? dernier.salaire : this.emploi_retraite_salaire;
    // Un revenu hérité se lit comme sur la ligne qui le porte : l'indice du
    // dernier métier reste un indice.
    const indice = this.enIndice(herite ? dernier.statut : statut);
    let niveau = salaire;
    if ((indice || this.revenu_en_euros) && echelle === null) {
      throw new Error("un revenu en euros ou en indice se convertit sur une échelle");
    }
    if (indice) {
      niveau = echelle.niveau(echelle.remuneration(salaire, this.primes));
    } else if (this.revenu_en_euros) {
      if (this.saisieEnNet && !this.enChiffreDAffaires(statut)) {
        salaire = echelle.brutMensuel(salaire, statut);
      }
      niveau = echelle.niveau(salaire);
    }
    const micro = this.enChiffreDAffaires(statut) ? this.micro : "";
    const [abattu, route] = this.abattu(niveau, statut);
    return {
      age: this.emploi_retraite, fin: this.emploi_retraite_fin, affiliation: route,
      niveau_salaire: this.assietteDuCollaborateur(abattu, route),
      employeur: this.emploi_retraite_employeur,
      ...(micro ? { micro } : {}),
    };
  }

  /**
   * L'activité exercée après le départ : une date qui ne précède pas le départ,
   * une fin qui la suit, un statut qui n'est pas une période sans emploi, un
   * revenu. Ce que le droit en fait — la pension servie pendant qu'elle dure,
   * les droits qu'elle ouvre —, c'est au calcul de le dire.
   */
  verifierEmploiRetraite() {
    const precisions = [
      ["emploi_retraite_fin", this.emploi_retraite_fin],
      ["emploi_retraite_statut", this.emploi_retraite_statut || null],
      ["emploi_retraite_salaire", this.emploi_retraite_salaire],
    ].filter(([, valeur]) => valeur !== null).map(([nom]) => nom);
    if (this.emploi_retraite_employeur !== "autre") {
      precisions.push("emploi_retraite_employeur");
    }
    if (this.emploi_retraite === null) {
      if (precisions.length) {
        throw new ErreurSaisie(
          `« ${precisions[0]} » ne sert qu'à une activité exercée après le départ : `
          + "dites aussi quand elle commence (« emploi_retraite »).",
        );
      }
      return;
    }
    const depart = this.dateDe(this.liquidation, true);
    const debut = this.dateDe(this.emploi_retraite, true);
    if (enMois(this.emploi_retraite) < enMois(this.liquidation)) {
      throw new ErreurSaisie(
        `Activité après le départ, en ${debut} : elle suit le départ, fixé en `
        + `${depart} ; l'activité d'avant le départ se dit dans la carrière.`,
      );
    }
    if (this.emploi_retraite_fin === null) {
      throw new ErreurSaisie(
        `Activité après le départ, en ${debut} : dites quand elle finit `
        + "(« emploi_retraite_fin »).",
      );
    }
    if (enMois(this.emploi_retraite_fin) <= enMois(this.emploi_retraite)) {
      throw new ErreurSaisie(
        `Activité après le départ, en ${debut} : elle finit après avoir commencé, `
        + `pas en ${this.dateDe(this.emploi_retraite_fin, true)}.`,
      );
    }
    if (CODES_SANS_EMPLOI.has(this.emploi_retraite_statut)) {
      throw new ErreurSaisie(
        `Activité après le départ, en ${debut} : « ${this.emploi_retraite_statut} » `
        + "n'est pas une activité, mais une période sans emploi.",
      );
    }
    if (this.emploi_retraite_salaire !== null) {
      const statut = this.emploi_retraite_statut || this.dernierMetier.statut;
      if (this.revenu_en_euros || this.enIndice(statut)) {
        if (!(this.emploi_retraite_salaire > 0)) {
          throw new ErreurSaisie(
            `Activité après le départ, en ${debut} : son `
            + `${this.enIndice(statut) ? "indice majoré" : "revenu"} doit être strictement `
            + "positif.",
          );
        }
      } else if (!(this.emploi_retraite_salaire >= NIVEAU_MINIMAL
          && this.emploi_retraite_salaire <= NIVEAU_MAXIMAL)) {
        throw new ErreurSaisie(
          `Activité après le départ, en ${debut} : niveau de revenu attendu entre 0,1 `
          + "et 10 fois le salaire moyen.",
        );
      }
    }
  }

  /**
   * L'invalidité et l'inaptitude que la saisie déclare, telles que la
   * chronologie les reçoit : l'âge où la `pension` d'invalidité a commencé, et
   * sa `categorie` quand elle est dite, l'`inaptitude`, et la `radiation` pour
   * invalidité d'un fonctionnaire — son
   * âge, son imputabilité, son taux en pour cent —, et l'âge depuis lequel
   * l'incapacité permanente atteint 50 % (`handicap`) ; et les autres titres au
   * taux plein de L. 351-8 (`deporte`, `mois_de_guerre`, `travail_manuel`).
   * `null` quand rien n'est dit.
   */
  invaliditeDeclaree() {
    if (this.invalidite === null && !this.inaptitude && this.radiation_invalidite === null
        && this.handicap === null && !this.deporte && this.mois_de_guerre === null
        && !this.travail_manuel) {
      return null;
    }
    const radiation = this.radiation_invalidite === null ? null : {
      age: this.radiation_invalidite,
      imputable: this.invalidite_imputable,
      taux: this.taux_invalidite,
    };
    const declaree = {
      pension: this.invalidite, inaptitude: this.inaptitude, radiation,
      handicap: this.handicap,
    };
    // La catégorie, seulement quand elle est dite : sinon, la présomption
    // `categorie_de_la_pension_d_invalidite` la pose.
    if (this.categorie_invalidite !== null) {
      declaree.categorie = this.categorie_invalidite;
    }
    // Les autres titres, seulement quand ils sont dits.
    for (const [nom, valeur] of [["deporte", this.deporte || null],
      ["mois_de_guerre", this.mois_de_guerre], ["travail_manuel", this.travail_manuel || null]]) {
      if (valeur !== null) {
        declaree[nom] = valeur;
      }
    }
    return declaree;
  }

  /**
   * La pension d'invalidité commence dans la carrière, avant le départ, et sa
   * catégorie, l'une des trois de L. 341-4, ne sert qu'à elle, datée : la
   * pension que la présomption `pension_d_invalidite_de_la_periode` tire d'une
   * période d'invalidité n'a pas de fait qui la porte. La radiation pour
   * invalidité d'un fonctionnaire tombe dans la carrière, au plus tard au
   * départ ; son imputabilité et son taux ne servent qu'à elle.
   * Que la radiation tombe dans un emploi de fonctionnaire, c'est au contexte
   * de le dire, qui a les affiliations ; ce que le droit fait de tout cela —
   * l'âge de la substitution, le taux plein, la pension du fonctionnaire —, au
   * calcul.
   */
  verifierInvalidite() {
    const precisions = [
      ["invalidite_imputable", this.invalidite_imputable || null],
      ["taux_invalidite", this.taux_invalidite],
    ].filter(([, valeur]) => valeur !== null).map(([nom]) => nom);
    if (this.radiation_invalidite === null && precisions.length > 0) {
      throw new ErreurSaisie(
        `« ${precisions[0]} » ne sert qu'à la retraite pour invalidité d'un `
        + "fonctionnaire : dites aussi la date de sa radiation des cadres "
        + "(« radiation_invalidite »).",
      );
    }
    if (this.taux_invalidite !== null
        && !(this.taux_invalidite >= 1 && this.taux_invalidite <= 100)) {
      throw new ErreurSaisie("Taux d'invalidité : en pour cent, entre 1 et 100.");
    }
    if (this.categorie_invalidite !== null && this.invalidite === null) {
      throw new ErreurSaisie(
        "« categorie_invalidite » ne sert qu'à la pension d'invalidité : dites aussi le "
        + "mois où elle a commencé (« invalidite »).",
      );
    }
    if (this.categorie_invalidite !== null
        && !CATEGORIES_D_INVALIDITE.includes(this.categorie_invalidite)) {
      throw new ErreurSaisie("Catégorie de la pension d'invalidité : 1, 2 ou 3 "
        + `(reçu : ${this.categorie_invalidite}).`);
    }
    if (this.mois_de_guerre !== null
        && !(this.mois_de_guerre >= 1 && this.mois_de_guerre <= MOIS_DE_GUERRE_MAXIMUM)) {
      throw new ErreurSaisie("Captivité et services de guerre : en mois, entre 1 et "
        + `${MOIS_DE_GUERRE_MAXIMUM}.`);
    }
    const debut = this.dateDe(this.debut);
    const depart = this.dateDe(this.liquidation, true);
    if (this.invalidite !== null) {
      const date = this.dateDe(this.invalidite);
      if (date.rang <= debut.rang) {
        throw new ErreurSaisie(
          `Pension d'invalidité en ${date} : elle suit le début de la carrière, `
          + `fixé en ${debut}.`,
        );
      }
      if (date.rang >= depart.rang) {
        throw new ErreurSaisie(
          `Pension d'invalidité en ${date} : elle précède le départ à la retraite, `
          + `fixé en ${depart}.`,
        );
      }
    }
    if (this.radiation_invalidite !== null) {
      const date = this.dateDe(this.radiation_invalidite);
      if (date.rang <= debut.rang) {
        throw new ErreurSaisie(
          `Radiation pour invalidité en ${date} : elle suit le début de la carrière, `
          + `fixé en ${debut}.`,
        );
      }
      if (date.rang > depart.rang) {
        throw new ErreurSaisie(
          `Radiation pour invalidité en ${date} : elle ne suit pas le départ à la `
          + `retraite, fixé en ${depart}.`,
        );
      }
    }
    if (this.handicap !== null) {
      // L'incapacité peut précéder la carrière — un handicap de naissance ou de
      // l'enfance —, mais ni la naissance ni le départ.
      const date = this.dateDe(this.handicap);
      const naissance = this.dateDe(0.0);
      if (date.rang <= naissance.rang) {
        throw new ErreurSaisie(
          `Incapacité d'au moins 50 % en ${date} : elle suit la naissance, `
          + `en ${naissance}.`,
        );
      }
      if (date.rang > depart.rang) {
        throw new ErreurSaisie(
          `Incapacité d'au moins 50 % en ${date} : elle ne suit pas le départ à la `
          + `retraite, fixé en ${depart}.`,
        );
      }
    }
  }

  /**
   * La carrière hors de France que la saisie déclare : les `periodes` — l'État,
   * les âges du début et de la fin, l'`activite` —, les `pensions` étrangères —
   * l'État, l'`age` où elle commence, son `montant` mensuel en euros
   * d'aujourd'hui —, l'État de `residence` après le départ, `null` en France,
   * et les `mois_en_france` de chaque année, `null` quand ils ne sont pas dits.
   * Le contexte ramène chaque montant à la date de sa pension avant que la
   * chronologie le reçoive (`personne`, dans `chronologie.js`). `null` quand
   * rien n'est dit.
   */
  etrangerDeclare() {
    if (this.etranger.length === 0 && this.pensions_etrangeres.length === 0
        && !this.residence && this.mois_en_france === null) {
      return null;
    }
    return {
      periodes: this.etranger.map((periode) => ({
        pays: periode.pays, debut: periode.debut, fin: periode.fin,
        activite: periode.activite })),
      pensions: this.pensions_etrangeres.map((pension) => ({
        pays: pension.pays, age: pension.debut, montant: pension.montant })),
      residence: this.residence || null,
      mois_en_france: this.mois_en_france,
    };
  }

  /**
   * Les périodes assimilées que la saisie déclare, telles que
   * `avecPeriodesAssimilees` les reçoit : vide quand rien n'est dit, et la
   * présomption `pas_de_periode_assimilee` tient.
   */
  periodesAssimileesDeclarees() {
    return this.assimilees.map((periode) => ({
      motif: periode.motif, debut: periode.debut, fin: periode.fin,
      ...(periode.dispositif ? { dispositif: periode.dispositif } : {}),
      ...(periode.jours !== null ? { jours: periode.jours } : {}),
    }));
  }

  /**
   * Une période assimilée : un motif connu, le dispositif d'un stage
   * d'insertion et de lui seul, deux dates que la chronologie sait lire, la fin
   * après le début, un début après la naissance et avant le départ, et des
   * jours, s'ils sont dits, entre un et ceux de ses dates. Le contrat
   * d'apprentissage : une ligne de carrière qui est un emploi, et une carrière
   * qui n'est pas lue sur un relevé, dont les lignes n'ont pas d'attribut pour
   * lui.
   */
  verifierAssimilees() {
    const motifs = MOTIFS_D_ASSIMILATION.map(([code]) => code);
    const dispositifs = DISPOSITIFS_D_INSERTION.map(([code]) => code);
    const depart = this.dateDe(this.liquidation, true);
    const departIso = `${String(depart.annee).padStart(4, "0")}-`
      + `${String(depart.mois).padStart(2, "0")}-01`;
    this.assimilees.forEach((periode, index) => {
      const quoi = `Période assimilée n° ${index + 1}`;
      if (!motifs.includes(periode.motif)) {
        throw new ErreurSaisie(
          `${quoi} : « ${periode.motif} » n'est pas un motif possible — `
          + `${motifs.join(", ")}.`);
      }
      if (periode.motif === "stage_d_insertion") {
        if (!dispositifs.includes(periode.dispositif)) {
          throw new ErreurSaisie(
            `${quoi} : un stage d'insertion nomme son dispositif — `
            + `${dispositifs.join(", ")}.`);
        }
      } else if (periode.dispositif) {
        throw new ErreurSaisie(`${quoi} : seul un stage d'insertion nomme un dispositif.`);
      }
      const dates = {};
      for (const [nom, valeur] of [["debut", periode.debut], ["fin", periode.fin]]) {
        try {
          [dates[nom]] = dateDeclaree(valeur, nom);
        } catch (erreur) {
          if (erreur instanceof ErreurSaisie) { throw erreur; }
          throw new ErreurSaisie(
            `${quoi} : « ${valeur} » attendu en AAAA, AAAA-MM ou AAAA-MM-JJ, `
            + "par exemple 1986-03-01.");
        }
      }
      if (dates.fin <= dates.debut) {
        throw new ErreurSaisie(
          `${quoi} : elle finit (${dates.fin}) après avoir commencé (${dates.debut}).`);
      }
      if (dates.debut <= this.naissanceIso) {
        throw new ErreurSaisie(`${quoi} : elle commence après la naissance.`);
      }
      if (dates.debut >= departIso) {
        throw new ErreurSaisie(
          `${quoi} : elle commence avant le départ à la retraite, fixé en ${depart}.`);
      }
      if (periode.jours !== null) {
        const duree = Math.round((Date.parse(`${dates.fin}T00:00:00Z`)
          - Date.parse(`${dates.debut}T00:00:00Z`)) / 86400000);
        if (!(periode.jours >= 1 && periode.jours <= duree)) {
          throw new ErreurSaisie(
            `${quoi} : ses jours se comptent de 1 à ${duree}, ceux de ses dates ; `
            + `reçu ${periode.jours}.`);
        }
      }
    });
    if (this.apprentissage !== null) {
      const lignes = this.lignesCarriere;
      if (this.releve) {
        throw new ErreurSaisie(
          "Contrat d'apprentissage : un relevé de carrière ne le porte pas, et ses "
          + "trimestres font foi ; il se déclare sur une ligne de métier.");
      }
      if (!(this.apprentissage >= 1 && this.apprentissage <= lignes.length)) {
        throw new ErreurSaisie(
          `Contrat d'apprentissage : le métier n° ${this.apprentissage} n'existe pas ; `
          + `la carrière en compte ${lignes.length}.`);
      }
      if (lignes[this.apprentissage - 1].sans_emploi) {
        throw new ErreurSaisie(
          `Contrat d'apprentissage : la ligne n° ${this.apprentissage} est une période `
          + "sans emploi, pas un contrat de travail.");
      }
    }
  }

  /**
   * Une période hors de France : un État qui n'est pas la France, un début
   * après quatorze ans, une fin qui le suit sans dépasser le départ, et aucune
   * autre période hors de France qui la chevauche — elle ne se compte qu'une
   * fois. Elle peut précéder le premier emploi en France. Une pension
   * étrangère : un État, un montant, et un début entre quatorze ans et l'âge de
   * départ le plus tardif que le modèle accepte (`AGE_LIQUIDATION_MAXIMAL`),
   * avant ou après le départ en France. La résidence : un
   * État étranger ; les mois en France, de zéro à douze. Que le tableau des
   * accords connaisse l'État, c'est au contexte de le dire, qui a les données ;
   * ce que chaque accord fait des périodes, au calcul.
   */
  verifierEtranger() {
    const depart = this.dateDe(this.liquidation, true);
    const bornes = [];
    this.etranger.forEach((periode, index) => {
      const rang = index + 1;
      const quoi = `Période à l'étranger n° ${rang}`;
      verifierEtat(periode.pays, quoi);
      const debut = this.dateDe(periode.debut);
      const fin = this.dateDe(periode.fin);
      if (periode.debut < AGE_DEBUT_MINIMAL) {
        throw new ErreurSaisie(
          `${quoi} : elle commence au plus tôt à ${AGE_DEBUT_MINIMAL} ans, en `
          + `${this.dateDe(AGE_DEBUT_MINIMAL)}.`,
        );
      }
      if (fin.rang <= debut.rang) {
        throw new ErreurSaisie(
          `${quoi} : elle finit (${fin}) après avoir commencé (${debut}).`,
        );
      }
      if (fin.rang > depart.rang) {
        throw new ErreurSaisie(
          `${quoi} : elle finit au plus tard au départ à la retraite, fixé en `
          + `${depart}.`,
        );
      }
      bornes.push([debut.rang, fin.rang, rang]);
    });
    bornes.sort((a, b) => a[0] - b[0] || a[1] - b[1] || a[2] - b[2]);
    for (let i = 1; i < bornes.length; i += 1) {
      const [, finPremiere, premiere] = bornes[i - 1];
      const [debutSeconde, , seconde] = bornes[i];
      if (debutSeconde < finPremiere) {
        throw new ErreurSaisie(
          `Périodes à l'étranger n° ${premiere} et n° ${seconde} : elles se `
          + "chevauchent, et un mois passé hors de France ne se compte qu'une fois.",
        );
      }
    }
    this.pensions_etrangeres.forEach((pension, index) => {
      const quoi = `Pension étrangère n° ${index + 1}`;
      verifierEtat(pension.pays, quoi);
      if (!(pension.montant > 0)) {
        throw new ErreurSaisie(`${quoi} : son montant mensuel est strictement positif.`);
      }
      if (!(pension.debut >= AGE_DEBUT_MINIMAL && pension.debut <= AGE_LIQUIDATION_MAXIMAL)) {
        throw new ErreurSaisie(
          `${quoi} : elle commence `
          + `${this.fenetre(AGE_DEBUT_MINIMAL, AGE_LIQUIDATION_MAXIMAL)}, soit de `
          + `${AGE_DEBUT_MINIMAL} à ${AGE_LIQUIDATION_MAXIMAL} ans.`,
        );
      }
    });
    if (this.residence) {
      verifierEtat(this.residence, "Résidence après le départ");
    }
    if (this.mois_en_france !== null
        && !(this.mois_en_france >= 0 && this.mois_en_france <= MOIS_PAR_AN)) {
      throw new ErreurSaisie(
        `Mois en France chaque année : de 0 à ${MOIS_PAR_AN}, reçu ${this.mois_en_france}.`);
    }
  }

  /**
   * Les pensions dont la saisie dit la date, telles que la chronologie les
   * reçoit : l'âge de chaque demande, par régime, dans l'ordre de leurs codes ;
   * `null` sans elles.
   */
  demandesDePensionDeclarees() {
    return this.demandes.length > 0 ? Object.fromEntries(this.demandes) : null;
  }

  /**
   * La date où l'assuré demande une pension : après le début de la carrière,
   * et pas au-delà de l'âge de départ le plus tardif que le modèle accepte. Que
   * le régime existe, que la carrière y ouvre une pension, et que la date la
   * retarde ou non, c'est au calcul de le dire.
   */
  verifierDemandes() {
    for (const [code, age_] of this.demandes) {
      const date = this.dateDe(age_, true);
      if (date.rang <= this.dateDe(this.debut).rang) {
        throw new ErreurSaisie(
          `Pension « ${code} » demandée en ${date} : la demande suit le début de la `
          + "carrière.",
        );
      }
      if (age_ > AGE_LIQUIDATION_MAXIMAL) {
        throw new ErreurSaisie(
          `Pension « ${code} » demandée en ${date} : le modèle ne liquide pas au-delà `
          + `de ${AGE_LIQUIDATION_MAXIMAL} ans.`,
        );
      }
    }
  }

  /**
   * Le conjoint et le décès : des dates lisibles, dans l'ordre de la vie — les
   * naissances, le mariage, le décès, l'invalidité du conjoint après sa
   * naissance, les enfants nés au plus tard trois cents jours après le décès.
   * Un décès avant le départ ouvre la réversion de la pension que
   * l'assuré eût obtenue (R. 353-6), pourvu qu'il suive le début de sa
   * carrière. Ses ressources, positives : ses revenus d'activité en sont une
   * part, et celles d'un nouveau conjoint supposent l'union où il vit, qui suit
   * le décès ; la fin de son activité suppose ses revenus, et celle de son union
   * l'union, chacune après ce qu'elle finit ; les variations de ses revenus
   * d'activité suivent le décès, celles des ressources de son nouveau conjoint
   * tombent dans l'union, et deux ne tombent pas le même jour
   * (`variationsAnalysees`). Les précédents conjoints, chacun
   * marié après les deux naissances, divorcé avant le mariage suivant — celui
   * du conjoint, qu'il faut alors dater —, remarié après son divorce
   * (`verifierExConjoints`).
   */
  verifierConjoint() {
    if (!this.conjoint) {
      const orphelins = [
        ["conjoint_sexe", this.conjoint_sexe], ["mariage", this.mariage],
        ["ressources_conjoint", this.ressources_conjoint],
        ["activite_conjoint", this.activite_conjoint],
        ["activite_conjoint_fin", this.activite_conjoint_fin],
        ["activite_conjoint_variations", this.activite_conjoint_variations],
        ["nouvelle_union", this.nouvelle_union],
        ["ressources_nouveau_conjoint", this.ressources_nouveau_conjoint],
        ["nouvelle_union_depuis", this.nouvelle_union_depuis],
        ["nouvelle_union_fin", this.nouvelle_union_fin],
        ["ressources_nouveau_conjoint_variations", this.ressources_nouveau_conjoint_variations],
        ["conjoint_invalidite", this.conjoint_invalidite],
        ["conjoint_retraite", this.conjoint_retraite], ["deces", this.deces],
        ["ex1", this.ex_conjoints.length > 0 ? true : null],
      ].filter(([, valeur]) => valeur !== "" && valeur !== null && valeur !== undefined)
        .map(([nom]) => nom);
      if (orphelins.length) {
        throw new ErreurSaisie(
          `« ${orphelins[0]} » ne sert qu'à la réversion : dites aussi la `
          + "naissance du conjoint (« conjoint »).",
        );
      }
      return;
    }
    const dates = {};
    for (const [nom, valeur, quoi] of [
      ["conjoint", this.conjoint, "la naissance du conjoint"],
      ["mariage", this.mariage, "le mariage"],
      ["conjoint_invalidite", this.conjoint_invalidite, "l'invalidité du conjoint"],
      ["conjoint_retraite", this.conjoint_retraite, "la retraite du conjoint"],
      ["nouvelle_union_depuis", this.nouvelle_union_depuis, "le début de sa nouvelle union"],
      ["nouvelle_union_fin", this.nouvelle_union_fin, "la fin de la nouvelle union du conjoint"],
      ["activite_conjoint_fin", this.activite_conjoint_fin, "la fin de l'activité du conjoint"],
      ["deces", this.deces, "le décès"],
    ]) {
      if (!valeur) {
        continue;
      }
      try {
        [dates[nom]] = dateDeclaree(valeur, quoi);
      } catch {
        throw new ErreurSaisie(
          `${quoi[0].toUpperCase()}${quoi.slice(1)} « ${valeur} » : attendu en AAAA ou `
          + "AAAA-MM, par exemple 1962 ou 1962-03.",
        );
      }
    }
    if (!["", "H", "F"].includes(this.conjoint_sexe)) {
      throw new ErreurSaisie("Sexe du conjoint : H ou F.");
    }
    if (this.ressources_conjoint !== null && this.ressources_conjoint < 0) {
      throw new ErreurSaisie("Ressources du conjoint : un montant annuel positif.");
    }
    if (this.activite_conjoint !== null) {
      if (this.activite_conjoint < 0) {
        throw new ErreurSaisie("Revenus d'activité du conjoint : un montant annuel positif.");
      }
      if (this.ressources_conjoint === null
          || this.activite_conjoint > this.ressources_conjoint) {
        throw new ErreurSaisie(
          "Revenus d'activité du conjoint : une part de ses ressources, à dire "
          + "aussi et au moins égales (« ressources_conjoint »).",
        );
      }
    }
    if (!["", ...FORMES_D_UNION].includes(this.nouvelle_union)) {
      throw new ErreurSaisie(
        "Union du conjoint après le décès : mariage, pacs ou concubinage.");
    }
    if (this.ressources_nouveau_conjoint !== null) {
      if (this.ressources_nouveau_conjoint < 0) {
        throw new ErreurSaisie("Ressources du nouveau conjoint : un montant annuel positif.");
      }
      if (!this.nouvelle_union) {
        throw new ErreurSaisie(
          "« ressources_nouveau_conjoint » ne sert qu'au ménage du conjoint : "
          + "dites aussi l'union où il vit (« nouvelle_union »).",
        );
      }
    }
    for (const nom of ["nouvelle_union_depuis", "nouvelle_union_fin",
      "ressources_nouveau_conjoint_variations"]) {
      if (this[nom] && !this.nouvelle_union) {
        throw new ErreurSaisie(
          `« ${nom} » ne sert qu'au ménage du conjoint : dites aussi l'union `
          + "où il vit (« nouvelle_union »).",
        );
      }
    }
    if (this.activite_conjoint_fin && this.activite_conjoint === null) {
      throw new ErreurSaisie(
        "« activite_conjoint_fin » ne sert qu'aux revenus d'activité du conjoint : "
        + "dites aussi ce qu'ils rapportent (« activite_conjoint »).",
      );
    }
    // Ce que chaque fin finit commence au décès, ou à la naissance du conjoint
    // sans lui ; l'union, au mois qu'il dit, s'il le dit.
    let [debut, quoi] = "deces" in dates
      ? [dates.deces, "votre décès"] : [dates.conjoint, "sa naissance"];
    if ("activite_conjoint_fin" in dates && dates.activite_conjoint_fin <= debut) {
      throw new ErreurSaisie(`La fin de l'activité du conjoint précède ${quoi} : elle le suit.`);
    }
    // Chaque variation suit ce qu'elle fait varier — ses revenus d'activité,
    // déclarés au décès ; les ressources de son nouveau conjoint, à leur union,
    // jusqu'à sa fin —, et deux ne tombent pas le même jour : voir `_variations`
    // de la chronologie, en Python.
    const changements = new Map(this.activite_conjoint !== null
      && "activite_conjoint_fin" in dates
      ? [[dates.activite_conjoint_fin, this.activite_conjoint_fin]] : []);
    for (const [date] of this.variationsAnalysees("activite_conjoint_variations")) {
      const [jour] = dateDeclaree(date, "la variation");
      if (jour <= debut) {
        throw new ErreurSaisie(`La variation des revenus d'activité du conjoint du ${date} `
          + `précède ${quoi} : elle le suit.`);
      }
      if (changements.has(jour)) {
        throw new ErreurSaisie("Deux changements des revenus d'activité du conjoint tombent "
          + `le même jour : ${changements.get(jour)} et ${date}.`);
      }
      changements.set(jour, date);
    }
    if ("nouvelle_union_depuis" in dates) {
      [debut, quoi] = [dates.nouvelle_union_depuis, "son début"];
    }
    if ("nouvelle_union_fin" in dates && dates.nouvelle_union_fin <= debut) {
      throw new ErreurSaisie(
        `La fin de la nouvelle union du conjoint précède ${quoi} : elle le suit.`);
    }
    const apports = new Map();
    for (const [date] of this.variationsAnalysees("ressources_nouveau_conjoint_variations")) {
      const [jour] = dateDeclaree(date, "la variation");
      if (jour <= debut) {
        throw new ErreurSaisie(`La variation des ressources du nouveau conjoint du ${date} `
          + "précède le début de leur union : elle le suit.");
      }
      if ("nouvelle_union_fin" in dates && jour >= dates.nouvelle_union_fin) {
        throw new ErreurSaisie(`La variation des ressources du nouveau conjoint du ${date} `
          + "ne précède pas la fin de leur union : elle la précède.");
      }
      if (apports.has(jour)) {
        throw new ErreurSaisie("Deux changements des ressources du nouveau conjoint tombent "
          + `le même jour : ${apports.get(jour)} et ${date}.`);
      }
      apports.set(jour, date);
    }
    if ("mariage" in dates) {
      const aine = dates.conjoint > this.naissanceIso ? dates.conjoint : this.naissanceIso;
      if (dates.mariage <= aine) {
        throw new ErreurSaisie("Le mariage précède la naissance d'un des époux.");
      }
    }
    if ("conjoint_invalidite" in dates && dates.conjoint_invalidite <= dates.conjoint) {
      throw new ErreurSaisie("L'invalidité du conjoint précède sa naissance.");
    }
    if ("conjoint_retraite" in dates && dates.conjoint_retraite <= dates.conjoint) {
      throw new ErreurSaisie("La retraite du conjoint précède sa naissance.");
    }
    if ("deces" in dates) {
      if ("mariage" in dates && dates.mariage >= dates.deces) {
        throw new ErreurSaisie("Le mariage suit le décès.");
      }
      if (dates.deces <= this.naissanceIso) {
        throw new ErreurSaisie("Le décès précède la naissance de l'assuré.");
      }
      // Le mariage que la saisie ne date pas est présumé, à l'âge que la table
      // du paquet porte : la saisie la reçoit de la page (`depuisRequete`).
      const presume = this.presomptions
        ? valeurPresumee("mariage_des_conjoints", this.presomptions) : null;
      if (presume !== null && !("mariage" in dates)
          && dates.deces <= plusAns(this.naissanceIso, Math.trunc(Number(presume)))) {
        throw new ErreurSaisie(
          `Décès « ${this.deces} » : il précède le mariage, que le modèle `
          + `présume à vos ${presume} ans faute de date ; dites-la (« mariage »).`,
        );
      }
      if (!this.releveActif && dates.deces <= this.jourDe(this.debut)) {
        throw new ErreurSaisie(
          `Décès « ${this.deces} » : il précède le début de la carrière, en `
          + `${this.dateDe(this.debut)} ; l'assuré n'aurait aucun droit à `
          + "reverser.",
        );
      }
      if ("nouvelle_union_depuis" in dates && dates.nouvelle_union_depuis <= dates.deces) {
        throw new ErreurSaisie(
          "La nouvelle union du conjoint précède votre décès : elle le suit.");
      }
      // L'enfant naît au plus tard trois cents jours après le décès, compté de
      // son dernier jour possible quand il n'est dit qu'à l'année ou au mois :
      // la loi le présume conçu au plus tôt trois cents jours avant sa
      // naissance (code civil, article 311).
      const [, precision] = dateDeclaree(this.deces, "le décès");
      const limite = new Date(`${dates.deces}T00:00:00Z`);
      if (precision === "annee") {
        limite.setUTCFullYear(limite.getUTCFullYear() + 1, 0, 0);
      } else if (precision === "mois") {
        limite.setUTCMonth(limite.getUTCMonth() + 1, 0);
      }
      limite.setUTCDate(limite.getUTCDate() + 300);
      for (const valeur of this.naissancesEnfants()) {
        if (new Date(`${naissanceDeclaree(valeur)[0]}T00:00:00Z`) > limite) {
          throw new ErreurSaisie(
            `Naissance d'un enfant « ${valeur} » : elle suit de plus de trois cents `
            + `jours votre décès, « ${this.deces} » ; l'enfant serait conçu après lui `
            + "(code civil, article 311).",
          );
        }
      }
    }
    this.verifierExConjoints(dates);
  }

  /**
   * La réversion des non-salariés agricoles se dit entière : le mois où elle
   * commence, après la naissance, comme la chronologie l'exige, et son
   * montant, positif ou nul. Qu'une période agricole la lise, c'est au calcul
   * de le dire : sans elle, la réversion ne change rien.
   */
  verifierReversionAgricole() {
    if (!this.reversion_agricole) {
      if (this.reversion_agricole_mensuel !== null) {
        throw new ErreurSaisie(
          "« reversion_agricole_mensuel » ne sert qu'à la réversion de la MSA : "
          + "dites aussi le mois où elle commence (« reversion_agricole »).",
        );
      }
      return;
    }
    const quoi = `Réversion de la MSA « ${this.reversion_agricole} »`;
    let debut;
    try {
      [debut] = dateDeclaree(this.reversion_agricole, "le début de la réversion");
    } catch {
      throw new ErreurSaisie(
        `${quoi} : le mois où elle commence, attendu en AAAA ou AAAA-MM, par `
        + "exemple 2010 ou 2010-03.",
      );
    }
    if (debut <= this.naissanceIso) {
      throw new ErreurSaisie(`${quoi} : elle suit votre naissance.`);
    }
    if (this.reversion_agricole_mensuel === null) {
      throw new ErreurSaisie(
        `${quoi} : dites aussi son montant mensuel brut à ce mois `
        + "(« reversion_agricole_mensuel »), zéro si vos ressources l'absorbent.",
      );
    }
    if (this.reversion_agricole_mensuel < 0) {
      throw new ErreurSaisie("Réversion de la MSA : son montant mensuel est positif ou nul.");
    }
  }

  /**
   * Les précédents conjoints : des dates lisibles, un mariage après les deux
   * naissances, un divorce après lui et avant le mariage suivant, un remariage
   * après le divorce ; leur mariage avec l'assuré précède celui du conjoint,
   * qu'il faut dater, et donc le décès.
   */
  verifierExConjoints(dates) {
    if (this.ex_conjoints.length === 0) {
      return;
    }
    if (!("mariage" in dates)) {
      throw new ErreurSaisie(
        "Avec un précédent conjoint, dites aussi la date du mariage avec votre "
        + "conjoint (« mariage »), que le partage de la réversion compte.",
      );
    }
    let finPrecedente = null;
    this.ex_conjoints.forEach((ex, i) => {
      const rang = i + 1;
      const jours = {};
      for (const [nom, valeur, quoi] of [
        ["naissance", ex.naissance, "la naissance"], ["mariage", ex.mariage, "le mariage"],
        ["divorce", ex.divorce, "le divorce"], ["remariage", ex.remariage, "le remariage"],
      ]) {
        if (!valeur) {
          continue;
        }
        try {
          [jours[nom]] = dateDeclaree(valeur, quoi);
        } catch {
          throw new ErreurSaisie(
            `Précédent conjoint n° ${rang}, ${quoi} « ${valeur} » : attendu en `
            + "AAAA ou AAAA-MM, par exemple 1962 ou 1962-03.",
          );
        }
      }
      const aine = jours.naissance > this.naissanceIso ? jours.naissance : this.naissanceIso;
      if (jours.mariage <= aine || (finPrecedente !== null && jours.mariage < finPrecedente)) {
        throw new ErreurSaisie(
          `Précédent conjoint n° ${rang} : le mariage suit les deux naissances `
          + "et le divorce d'avant.",
        );
      }
      if (jours.divorce <= jours.mariage) {
        throw new ErreurSaisie(`Précédent conjoint n° ${rang} : le divorce suit le mariage.`);
      }
      if ("remariage" in jours && jours.remariage <= jours.divorce) {
        throw new ErreurSaisie(
          `Précédent conjoint n° ${rang} : son remariage suit le divorce.`);
      }
      finPrecedente = jours.divorce;
    });
    if (dates.mariage < finPrecedente) {
      throw new ErreurSaisie(
        "Le mariage avec votre conjoint précède le divorce d'un précédent "
        + "mariage : il le suit.",
      );
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
      liquidation: this.moisDe(this.liquidation, true),
      salaire: nombreBrut(this.salaire), profil: this.profil,
      releve: this.releve,
      primes: nombreBrut(this.primes), enfants: this.enfants,
      ...(naissances.length ? { naissances: naissances.join(",") } : {}),
      ...(this.charge_enfants ? { charge_enfants: this.charge_enfants } : {}),
      ...Object.fromEntries([
        ["conjoint", this.conjoint], ["conjoint_sexe", this.conjoint_sexe],
        ["mariage", this.mariage],
        ["ressources_conjoint", this.ressources_conjoint === null
          ? "" : nombreBrut(this.ressources_conjoint)],
        ["activite_conjoint", this.activite_conjoint === null
          ? "" : nombreBrut(this.activite_conjoint)],
        ["activite_conjoint_fin", this.activite_conjoint_fin],
        ["activite_conjoint_variations", this.activite_conjoint_variations],
        ["nouvelle_union", this.nouvelle_union],
        ["ressources_nouveau_conjoint", this.ressources_nouveau_conjoint === null
          ? "" : nombreBrut(this.ressources_nouveau_conjoint)],
        ["nouvelle_union_depuis", this.nouvelle_union_depuis],
        ["nouvelle_union_fin", this.nouvelle_union_fin],
        ["ressources_nouveau_conjoint_variations", this.ressources_nouveau_conjoint_variations],
        ["conjoint_invalidite", this.conjoint_invalidite],
        ["conjoint_retraite", this.conjoint_retraite],
        ["deces", this.deces],
      ].filter(([, valeur]) => valeur !== "" && valeur !== null)),
      ...Object.fromEntries(this.ex_conjoints.flatMap((ex, i) => [
        [`ex${i + 1}`, ex.naissance], [`ex${i + 1}_mariage`, ex.mariage],
        [`ex${i + 1}_divorce`, ex.divorce], [`ex${i + 1}_remariage`, ex.remariage],
      ]).filter(([, valeur]) => valeur)),
      ...(this.progressive !== null
        ? { progressive: this.moisDe(this.progressive, true),
          quotite: this.quotite_progressive }
        : {}),
      ...(this.emploi_retraite !== null
        ? Object.fromEntries([
          ["emploi_retraite", this.moisDe(this.emploi_retraite, true)],
          ["emploi_retraite_fin", this.emploi_retraite_fin === null
            ? null : this.moisDe(this.emploi_retraite_fin, true)],
          ["emploi_retraite_statut", this.emploi_retraite_statut || null],
          ["emploi_retraite_salaire", this.emploi_retraite_salaire === null
            ? null : nombreBrut(this.emploi_retraite_salaire)],
          ["emploi_retraite_employeur", this.emploi_retraite_employeur === "autre"
            ? null : this.emploi_retraite_employeur],
        ].filter(([, valeur]) => valeur !== null))
        : {}),
      ...Object.fromEntries(this.demandes.map(
        ([code, age_]) => [`${PREFIXE_DEMANDE}${code}`, this.moisDe(age_, true)])),
      ...Object.fromEntries([
        ["invalidite", this.invalidite === null ? null : this.moisDe(this.invalidite)],
        ["categorie_invalidite", this.categorie_invalidite],
        ["inaptitude", this.inaptitude ? OUI : null],
        ["radiation_invalidite", this.radiation_invalidite === null
          ? null : this.moisDe(this.radiation_invalidite)],
        ["invalidite_imputable", this.invalidite_imputable ? OUI : null],
        ["taux_invalidite", this.taux_invalidite],
        ["handicap", this.handicap === null ? null : this.moisDe(this.handicap)],
        ["deporte", this.deporte ? OUI : null],
        ["guerre", this.mois_de_guerre],
        ["travail_manuel", this.travail_manuel || null],
      ].filter(([, valeur]) => valeur !== null)),
      ...(this.micro ? { micro: this.micro } : {}),
      ...(this.indice ? { indice: this.indice } : {}),
      ...(this.lodeom ? { lodeom: this.lodeom } : {}),
      ...(this.collaborateur ? { collaborateur: this.collaborateur } : {}),
      ...Object.fromEntries([
        ["reversion_agricole", this.reversion_agricole || null],
        ["reversion_agricole_mensuel", this.reversion_agricole_mensuel === null
          ? null : nombreBrut(this.reversion_agricole_mensuel)],
      ].filter(([, valeur]) => valeur !== null)),
      ...(this.residence ? { residence: this.residence } : {}),
      ...(this.mois_en_france !== null ? { mois_en_france: this.mois_en_france } : {}),
      ...(this.apprentissage !== null ? { apprentissage: this.apprentissage } : {}),
      ...(this.revenu_fiscal !== null ? { revenu_fiscal: nombreBrut(this.revenu_fiscal) } : {}),
      ...(this.temps_partiel ? { temps_partiel: this.temps_partiel } : {}),
      ...(this.dispenses ? { dispenses: this.dispenses } : {}),
      interruptions: this.interruptions, indexation: this.indexation,
      lissage: this.lissage,
      age_reference: this.age_reference, table: this.table,
      population: this.population, rattachement: this.rattachement,
      conversion_acquis: this.conversion_acquis,
      part_cotisation: this.part_cotisation,
      contribution_etat: this.contribution_etat,
      foyer: this.foyer,
      projection: this.projection, emploi: this.emploi, stock: this.stock,
      // L'espérance de vie ne s'écrit qu'écartée de la centrale : les adresses
      // d'avant elle restent celles qu'elles étaient.
      ...(this.esperance_vie !== "centrale" ? { esperance_vie: this.esperance_vie } : {}),
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
    // L'estimation officielle recopiée, seulement ce qui l'a été.
    for (const nom of CHAMPS_ESTIMATION) {
      if (this[nom] !== null) champs[nom] = nombreBrut(this[nom]);
    }
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
    // Les périodes hors de France et les pensions étrangères, de même : une
    // ligne par période, une par pension, et l'activité salariée, celle d'une
    // ligne qui ne la dit pas, ne s'écrit pas.
    this.etranger.forEach((periode, index) => {
      const rang = index + 1;
      champs[`etranger${rang}_pays`] = periode.pays;
      champs[`etranger${rang}_debut`] = this.moisDe(periode.debut);
      champs[`etranger${rang}_fin`] = this.moisDe(periode.fin);
      if (periode.activite !== ACTIVITES_A_L_ETRANGER[0][0]) {
        champs[`etranger${rang}_activite`] = periode.activite;
      }
    });
    this.pensions_etrangeres.forEach((pension, index) => {
      const rang = index + 1;
      champs[`pension_etrangere${rang}_pays`] = pension.pays;
      champs[`pension_etrangere${rang}`] = nombreBrut(pension.montant);
      champs[`pension_etrangere${rang}_debut`] = this.moisDe(pension.debut);
    });
    // Les périodes assimilées, une ligne chacune, leurs dates telles qu'elles
    // ont été dites : la chronologie les lit au jour.
    this.assimilees.forEach((periode, index) => {
      const rang = index + 1;
      champs[`assimilee${rang}_motif`] = periode.motif;
      champs[`assimilee${rang}_debut`] = periode.debut;
      champs[`assimilee${rang}_fin`] = periode.fin;
      if (periode.dispositif) {
        champs[`assimilee${rang}_dispositif`] = periode.dispositif;
      }
      if (periode.jours !== null) {
        champs[`assimilee${rang}_jours`] = periode.jours;
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
 * Le motif de chaque année qu'un creux occupe plus qu'à moitié, rapporté aux
 * mois que la carrière, de `debut` à `fin`, y travaille ; à égalité, l'année
 * reste travaillée. Un creux suivant l'emporte sur le précédent la même année.
 */
function anneesCreuses(creux, debut, fin) {
  const annees = new Map();
  for (const [motif, ouverture, cloture] of creux) {
    for (let annee = ouverture.annee; annee <= cloture.annee; annee += 1) {
      const occupes = moisTravailles(annee, ouverture, cloture);
      const portee = moisTravailles(annee, debut, fin);
      if (portee && occupes * 2 > portee) {
        annees.set(annee, motif);
      }
    }
  }
  return annees;
}

/**
 * Les métiers qui suivent le premier, lus dans « metier2_… », « metier3_… ».
 *
 * Le formulaire affiche toujours une ligne de plus qu'il n'y a de métiers : tant
 * qu'elle reste vide, elle ne décrit rien. Une ligne partiellement remplie, en
 * revanche, est une intention manquée — elle est refusée, avec ce qui lui manque.
 */
function metiersSaisis(parametres, salairePrecedent, moisDeNaissance, tolerante = false) {
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
      debut: ageSaisi(parametres, `metier${rang}_debut`, 0.0, moisDeNaissance),
      statut,
      salaire: salaireLigne,
      // Vrai si l'activité S'AJOUTE à celle en cours au lieu de la remplacer.
      cumul: Boolean(cumul),
      // Âge auquel une activité ajoutée s'arrête ; null la mène au départ.
      fin: finBrut
        ? ageSaisi(parametres, `metier${rang}_fin`, 0.0, moisDeNaissance)
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

/**
 * Les précédents conjoints, lus dans « ex1… » et « ex2… » : la naissance
 * (« ex1 »), le mariage (« _mariage »), le divorce (« _divorce ») et le
 * remariage (« _remariage »). Une ligne commencée se refuse sans l'un des trois
 * premiers.
 */
function exConjointsSaisis(parametres, tolerante = false) {
  const exConjoints = [];
  for (let rang = 1; rang <= EX_CONJOINTS_MAXIMUM; rang += 1) {
    const [naissance, mariage, divorce, remariage] = ["", "_mariage", "_divorce", "_remariage"]
      .map((suffixe) => String(parametres[`ex${rang}${suffixe}`] ?? "").trim());
    if (!naissance && !mariage && !divorce && !remariage) {
      continue;
    }
    if (tolerante && (!naissance || !mariage || !divorce)) {
      break;
    }
    if (!naissance || !mariage || !divorce) {
      throw new ErreurSaisie(
        `Précédent conjoint n° ${rang} : indiquer sa naissance, la date du `
        + "mariage et celle du divorce, ou laisser sa ligne entièrement vide.",
      );
    }
    exConjoints.push({ naissance, mariage, divorce, remariage });
  }
  return exConjoints;
}

/**
 * Les périodes passées hors de France, lues dans « etranger1_… » à
 * « etranger4_… » : l'État, le mois où elle commence, celui où elle finit, et
 * l'activité. Les âges se comptent comme ceux d'un métier, du mois de
 * naissance ; la fin est exclue, comme celle d'une activité ajoutée : la période
 * court du mois où elle commence au mois qui précède celui où elle finit. Une
 * ligne vide ne dit rien ; une ligne commencée sans son État ou
 * ses deux dates se refuse, comme une ligne de métier, et une activité que la
 * saisie ne connaît pas aussi, au lieu de valoir salariée en silence.
 */
function periodesEtrangeresSaisies(parametres, moisDeNaissance, tolerante = false) {
  const activites = ACTIVITES_A_L_ETRANGER.map(([code]) => code);
  const periodes = [];
  for (let rang = 1; rang <= ETRANGER_MAXIMUM; rang += 1) {
    const pays = String(parametres[`etranger${rang}_pays`] ?? "").trim();
    const debut = String(parametres[`etranger${rang}_debut`] ?? "").trim();
    const fin = String(parametres[`etranger${rang}_fin`] ?? "").trim();
    const activite = String(parametres[`etranger${rang}_activite`] ?? "").trim();
    if (!pays && !debut && !fin && !activite) {
      continue;
    }
    // Remontrée, la ligne incomplète n'est pas une période : la lecture s'y
    // arrête, et c'est la ligne vide du formulaire qui la reçoit.
    if (tolerante && (!pays || !debut || !fin)) {
      break;
    }
    if (!pays) {
      throw new ErreurSaisie(
        `Période à l'étranger n° ${rang} : indiquer l'État, ou laisser sa ligne `
        + "entièrement vide.",
      );
    }
    if (!debut || !fin) {
      throw new ErreurSaisie(
        `Période à l'étranger n° ${rang} : indiquer le mois où elle commence et celui `
        + "où elle finit.",
      );
    }
    if (activite !== "" && !activites.includes(activite)) {
      throw new ErreurSaisie(
        `Période à l'étranger n° ${rang} : « ${activite} » n'est pas une activité `
        + `possible — ${activites.join(" ou ")}.`,
      );
    }
    periodes.push({
      pays,
      debut: ageSaisi(parametres, `etranger${rang}_debut`, 0.0, moisDeNaissance),
      fin: ageSaisi(parametres, `etranger${rang}_fin`, 0.0, moisDeNaissance),
      activite: activite || activites[0],
    });
  }
  return periodes;
}

/**
 * Les périodes assimilées, lues dans « assimilee1_… » à « assimilee4_… » : le
 * motif, ses deux dates, en AAAA, AAAA-MM ou AAAA-MM-JJ, la fin exclue, le
 * dispositif d'un stage d'insertion, et les jours qu'elle compte quand ce ne
 * sont pas tous ceux de ses dates.
 * Une ligne vide ne dit rien ; une ligne commencée sans son motif ou ses deux
 * dates se refuse, comme une ligne de métier.
 */
function periodesAssimileesSaisies(parametres, tolerante = false) {
  const periodes = [];
  for (let rang = 1; rang <= ASSIMILEES_MAXIMUM; rang += 1) {
    const [motif, debut, fin, dispositif, jours] = ["motif", "debut", "fin", "dispositif",
      "jours"].map((suffixe) => String(parametres[`assimilee${rang}_${suffixe}`] ?? "").trim());
    if (!motif && !debut && !fin && !dispositif && !jours) {
      continue;
    }
    if (tolerante && (!motif || !debut || !fin)) {
      break;
    }
    if (!motif) {
      throw new ErreurSaisie(
        `Période assimilée n° ${rang} : indiquer son motif, ou laisser sa ligne `
        + "entièrement vide.");
    }
    if (!debut || !fin) {
      throw new ErreurSaisie(
        `Période assimilée n° ${rang} : indiquer le jour où elle commence et celui où `
        + "elle finit.");
    }
    periodes.push({
      motif, debut, fin, dispositif,
      jours: jours ? entier(parametres, `assimilee${rang}_jours`, 0) : null,
    });
  }
  return periodes;
}

/**
 * Les pensions étrangères, lues dans « pension_etrangere1… » à
 * « pension_etrangere4… » : l'État qui la sert (« _pays »), son montant brut
 * mensuel, et le mois où elle commence (« _debut »). Une ligne commencée se
 * refuse sans l'un des trois. Une pension que le régime d'un autre État sert,
 * ou celui d'une organisation internationale, est une liquidation observée
 * (docs/architecture.md, § 5.4 et 5.5) ; son montant est en euros
 * d'aujourd'hui — de l'année courante du modèle, comme les revenus saisis —, et
 * le contexte le ramène à sa date.
 */
function pensionsEtrangeresSaisies(parametres, moisDeNaissance, tolerante = false) {
  const pensions = [];
  for (let rang = 1; rang <= ETRANGER_MAXIMUM; rang += 1) {
    const pays = String(parametres[`pension_etrangere${rang}_pays`] ?? "").trim();
    const montant = String(parametres[`pension_etrangere${rang}`] ?? "").trim();
    const debut = String(parametres[`pension_etrangere${rang}_debut`] ?? "").trim();
    if (!pays && !montant && !debut) {
      continue;
    }
    if (tolerante && (!pays || !montant || !debut)) {
      break;
    }
    if (!pays) {
      throw new ErreurSaisie(
        `Pension étrangère n° ${rang} : indiquer l'État qui la sert, ou laisser sa `
        + "ligne entièrement vide.",
      );
    }
    if (!montant) {
      throw new ErreurSaisie(
        `Pension étrangère n° ${rang} : indiquer son montant brut mensuel, en euros.`,
      );
    }
    if (!debut) {
      throw new ErreurSaisie(
        `Pension étrangère n° ${rang} : indiquer le mois où elle commence.`,
      );
    }
    pensions.push({
      pays,
      montant: reel(parametres, `pension_etrangere${rang}`, 0.0),
      debut: ageSaisi(parametres, `pension_etrangere${rang}_debut`, 0.0, moisDeNaissance),
    });
  }
  return pensions;
}

/**
 * Un État étranger, tel que la saisie l'écrit : son code à deux majuscules, ou
 * `AUTRE_ETAT` ; jamais la France.
 */
function verifierEtat(code, quoi) {
  if (code === "FR") {
    throw new ErreurSaisie(`${quoi} : la France n'est pas un État étranger.`);
  }
  if (code !== AUTRE_ETAT && !CODE_D_ETAT.test(code)) {
    throw new ErreurSaisie(
      `${quoi} : « ${code} » n'est pas un État — son code à deux majuscules, comme `
      + `DE ou MA, ou « ${AUTRE_ETAT} ».`,
    );
  }
}

function cleEnum(enumeration, valeur) {
  const cle = Object.keys(enumeration).find((nom) => enumeration[nom] === valeur);
  if (cle === undefined) {
    throw new ErreurSaisie(`valeur inconnue : ${valeur}`);
  }
  return cle;
}

/**
 * Ce qu'un nombre saisi a le droit de s'écrire — et rien d'autre : des chiffres
 * décimaux, une virgule à l'anglaise et un exposant. `Number` lirait aussi
 * « 0x10 », « 0b1 » ou « Infinity », qu'une adresse forgée porterait et que
 * personne ne tire au hasard.
 */
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

/**
 * Un entier saisi, bornes d'une plage d'interruption comprises : « 1995 » oui,
 * « 1995,0 » non.
 */
export function estEntier(texte) {
  return /^\s*[+-]?\d+\s*$/.test(String(texte ?? ""));
}

/**
 * Une case cochée : « oui », ou rien. Toute autre réponse se refuse, au lieu de
 * valoir non en silence.
 */
export function oui(parametres, nom) {
  const valeur = parametres[nom];
  if (valeur === undefined || valeur === null || valeur === "") {
    return false;
  }
  if (valeur !== OUI) {
    throw new ErreurSaisie(`« ${nom} » : « ${valeur} » n'est pas une réponse possible `
      + `— « ${OUI} », ou rien.`);
  }
  return true;
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

/**
 * Valeur telle qu'elle est réinjectée dans un champ de formulaire, et écrite
 * dans l'adresse réécrite : l'écriture la plus courte qui se relise en ce même
 * nombre, celle de JavaScript. Six chiffres significatifs (`formatG`, le `:g`
 * du Python) relisaient un revenu fiscal de 1 234 567 € 1 234 570.
 */
export function nombreBrut(valeur) {
  return String(valeur);
}

/** Le premier du mois est un ORDINAL en français : « 1er », et non « 1 ». */
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
 * ayant aucun rôle. Le jour est nul quand la date n'en dit pas.
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
  const jour = trouve[3] === undefined ? null : Number(trouve[3]);
  if (!(mois >= 1 && mois <= 12)) {
    throw new ErreurSaisie(`« ${nom} » : mois attendu entre 01 et 12 (reçu : ${brut}).`);
  }
  // Le jour n'est borné ici que grossièrement ; celui de la naissance, le seul
  // qui compte, se contrôle au calendrier près avec elle (`verifier`).
  if (jour !== null && !(jour >= 1 && jour <= 31)) {
    throw new ErreurSaisie(`« ${nom} » : jour attendu entre 01 et 31 (reçu : ${brut}).`);
  }
  return { annee, mois, jour };
}

/**
 * Les pensions dont l'adresse dit la date de demande, une par régime, dans
 * l'ordre de leurs codes : « demande_<régime> », en date comme le départ. Un
 * champ vide ne dit rien.
 */
function demandesSaisies(parametres, origine) {
  const demandes = [];
  for (const cle of Object.keys(parametres).sort()) {
    if (!cle.startsWith(PREFIXE_DEMANDE) || [undefined, null, ""].includes(parametres[cle])) {
      continue;
    }
    const code = cle.slice(PREFIXE_DEMANDE.length);
    if (!CODE_DE_REGIME.test(code)) {
      throw new ErreurSaisie(
        `« ${cle} » : le code d'un régime s'écrit en minuscules, chiffres et `
        + "soulignés, comme « demande_regime_general ».",
      );
    }
    demandes.push([code, ageSaisi(parametres, cle, 0.0, origine)]);
  }
  return demandes;
}

/**
 * L'âge qu'une date de carrière vaut, rapportée à la naissance.
 *
 * Le formulaire demande une date — celle du premier mois cotisé, celle du
 * départ —, parce que c'est ce dont on se souvient ; le modèle, lui, ne connaît
 * que des âges. La soustraction se fait ici, en mois, depuis `origine` — le mois
 * de naissance pour un début ou une fin d'activité, celui d'où les âges de
 * départ se comptent pour le départ —, et le résultat est l'âge en années
 * décimales que le moteur attend : le moteur, qui compte de même, retombe sur
 * la date saisie.
 *
 * Les adresses d'avant le calendrier continuent d'être lues telles quelles :
 * `liquidation=64` et `liquidation_mois=7` valent soixante-quatre ans et sept
 * mois, `liquidation=64.5` vaut ce qu'il a toujours valu.
 */
function ageSaisi(parametres, nom, defaut, origine) {
  const date = dateSaisie(parametres, nom);
  if (date !== null) {
    return (new DateMois(date.annee, date.mois).rang - origine.rang) / MOIS_PAR_AN;
  }
  const annees = reel(parametres, nom, defaut);
  // Un âge dont les mois passent le plus grand nombre ne tombe sur aucun mois :
  // le calendrier, qui le datait avant que ses bornes ne soient vérifiées,
  // levait sa propre erreur au lieu d'un refus. Il se refuse où il entre.
  if (!Number.isFinite(annees * MOIS_PAR_AN)) {
    throw new ErreurSaisie(`« ${nom} » : âge hors du calendrier (reçu : ${parametres[nom]}).`);
  }
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
    versBrutDirect = null, point = null, annee = null }) {
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
    // Valeur annuelle du point d'indice de la fonction publique, la même année,
    // et cette année-là : le traitement d'un indice majoré en est le produit.
    this.point = point;
    this.annee = annee;
  }

  /** Le traitement brut mensuel d'un indice majoré, au point de l'année. */
  traitement(indice) {
    if (!(this.point > 0)) {
      throw new Error("un indice se convertit au point d'indice de l'année");
    }
    return (indice * this.point) / MOIS_PAR_AN;
  }

  /**
   * La rémunération brute mensuelle d'un indice majoré, primes comprises : le
   * traitement n'en est que la part que les primes laissent, `1 − primes`,
   * comme la fiche de paie le partage.
   */
  remuneration(indice, primes) {
    return this.traitement(indice) / (1.0 - primes);
  }

  /** L'opération inverse : l'indice qu'une rémunération brute mensuelle suppose. */
  indice(remuneration, primes) {
    return remuneration / this.traitement(1.0) * (1.0 - primes);
  }

  /**
   * Le plus petit et le plus grand indice ENTIERS que le modèle accepte à cette
   * part de primes, de 0,1 à 10 fois le salaire moyen : ceux que le refus
   * nomme, et que la reprise d'une pension ne quitte pas (`eurosDansLesBornes`).
   */
  indicesDansLesBornes(primes) {
    const niveau = (indice) => this.niveau(this.remuneration(indice, primes));
    let bas = Math.ceil(this.indice(this.mensuel(NIVEAU_MINIMAL), primes));
    while (niveau(bas) < NIVEAU_MINIMAL) bas += 1;
    while (bas > 1 && niveau(bas - 1) >= NIVEAU_MINIMAL) bas -= 1;
    let haut = Math.floor(this.indice(this.mensuel(NIVEAU_MAXIMAL), primes));
    while (niveau(haut) > NIVEAU_MAXIMAL) haut -= 1;
    while (niveau(haut + 1) <= NIVEAU_MAXIMAL) haut += 1;
    return [bas, haut];
  }

  /** Un salaire mensuel brut, en multiples du salaire moyen. */
  niveau(eurosMensuels) {
    return (eurosMensuels * MOIS_PAR_AN) / this.moyen;
  }

  /** L'opération inverse : un multiple, en euros bruts par mois. */
  mensuel(niveau) {
    return (niveau * this.moyen) / MOIS_PAR_AN;
  }

  /**
   * Un multiple en euros bruts mensuels ENTIERS, sans sortir des bornes :
   * l'euro le plus proche, sauf aux bords. 0,1 fois le salaire moyen ne fait
   * pas un nombre rond d'euros, et l'arrondi peut tomber du mauvais côté —
   * 355 € pour 355,34, que le modèle refuse ensuite : il est alors poussé d'un
   * euro vers l'intérieur. C'est ce que la bascule d'unité écrit et ce que le
   * refus nomme : un montant qu'on montre est un montant accepté.
   */
  eurosDansLesBornes(niveau) {
    let euros = Math.round(this.mensuel(niveau));
    while (this.niveau(euros) < NIVEAU_MINIMAL) {
      euros += 1;
    }
    while (this.niveau(euros) > NIVEAU_MAXIMAL) {
      euros -= 1;
    }
    return euros;
  }

  /**
   * Le brut mensuel d'un montant saisi, quel que soit le mode. En mode brut,
   * c'est le montant lui-même ; en mode net, ce que la fiche de paie du statut
   * laisse. Les statuts que le modèle ne sait pas décrire rendent le montant
   * inchangé : voir `convertit`.
   */
  brutMensuel(montant, statut) {
    if (this.versBrut === null || montant <= 0) {
      return montant;
    }
    return this.versBrut(montant, statut);
  }

  /**
   * Le net vers le brut, quel que soit le mode courant. `brutMensuel` ne
   * convertit qu'en mode net — c'est ce qui le rend sûr au milieu du calcul. La
   * bascule, elle, doit convertir depuis le mode où l'on est vers celui où l'on
   * va, donc sans condition.
   */
  brutMensuelDirect(net, statut) {
    if (this.versBrutDirect === null || net <= 0) {
      return net;
    }
    return this.versBrutDirect(net, statut);
  }

  /**
   * Le sens direct : ce qu'un brut mensuel laisse, statut par statut. Sert à la
   * BASCULE, et non au calcul : passer du brut au net doit traduire le nombre
   * saisi, pour que la page revienne en décrivant la même carrière.
   */
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

