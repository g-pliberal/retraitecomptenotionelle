/**
 * Les clés et les codes que la saisie partage avec le démarrage des pages
 * (action 174, étape 5).
 *
 * Une page toute faite se lit et s'anime sans la saisie, qui ne se charge qu'au
 * premier calcul. Le routeur y lit pourtant quelles clés d'une adresse décrivent
 * les règles, et quels motifs ne paient aucun revenu : ils vivent donc ici, sans
 * aucun import, et `saisie.js` les reprend pour ses autres lecteurs.
 */

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
  ["chomage_solidarite", "chômage en fin de droits (ASS)"],
  ["preretraite_fne", "préretraite du FNE"],
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

/**
 * Les clés de requête qui décrivent les RÈGLES, et non la carrière.
 *
 * Ce sont exactement les dix-neuf que `Saisie.parametres` lit pour fabriquer un jeu
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
  "frais", "taux", "bascule", "euros", "esperance_vie",
]);
