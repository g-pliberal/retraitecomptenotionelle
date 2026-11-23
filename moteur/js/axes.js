/**
 * Les axes du fichier de régime, tels que le moteur les lit (note de décision
 * 0009, amendement du 22 novembre 2026 ; `donnees/axes.py`).
 *
 * Un régime range ses paramètres en quatre blocs, un par famille de champ :
 *
 * - `structure` : ce qui décrit le régime (`type_calcul`, `points_de`) ;
 * - `liquidation` : les règles choisies à la date d'effet de la pension, au
 *   jour, `[du, au)` ;
 * - `cotisation` : les paramètres choisis à l'année où le droit s'acquiert ;
 *   deux lignes qui couvrent la même année sont deux tranches, dans l'ordre ;
 * - `servi` : les montants que le service revalorise, au jour.
 *
 * Une liquidation lit la ligne de liquidation, la structure et la ligne servie
 * en vigueur à sa date d'effet (`aLaDate`) ; une année d'acquisition lit ses
 * lignes de cotisation (`deLAnnee`).
 *
 * Le paquet porte les quatre blocs (étape 4 de l'amendement) ; la vue des
 * périodes, qui les portait ensemble, est partie à l'étape 5.
 */

/** Ce qui décrit le régime. */
export const STRUCTURE = new Set(["type_calcul", "points_de"]);

/** Les montants que le service revalorise, et leur millésime. */
export const SERVI = new Set([
  "valeur_point_euros", "valeur_point_annee",
  "pension_forfaitaire_annuelle", "pension_forfaitaire_annee",
  "plafond_majoration_enfants", "plafond_majoration_annee",
]);

/**
 * Les paramètres de l'année où le droit s'acquiert : ceux de `donnees/axes.py`,
 * et les taux propres du non-salarié, que le chargeur date année par année
 * depuis `taux_cotisation_annuels.csv`.
 */
export const COTISATION = new Set([
  "assiette", "assiette_annee_de_revenu", "assiette_de_debut",
  "assiette_de_debut_en_bases_mensuelles", "assiette_facteur_revenu",
  "assiette_forfaitaire", "assiette_grille", "assiette_minimale_pass",
  "assiette_plancher", "assiette_repere_smic", "smic_du_mois",
  "borne_basse_euros", "borne_basse_par_annee", "borne_haute_euros",
  "borne_haute_par_annee", "plafond_primes_traitement",
  "taux_cotisation_retraite", "perimetre_taux", "part_salariale",
  "taux_cotisation_deplafonnee", "part_salariale_deplafonnee",
  "cotisation_forfaitaire_euros", "cotisation_forfaitaire_annee",
  "cotisation_par_classes", "part_assurance_maladie_forfait",
  "part_assurance_maladie_taux", "dispense_de_debut", "exemption_passe_l_age",
  "taux_calcul_points", "points_maximum", "points_au_prorata_des_cotisations",
  "points_minimum_annuels", "points_par_trimestre_valide",
  "points_ajustement_par_forfait", "points_ajustement_maximum",
  "points_ajustement_au_plafond", "points_invalidite", "bareme_points",
  "points_abattus_a_l_age", "duree_requise_des_annuites",
  "taux_cotisation_non_salarie", "taux_cotisation_deplafonnee_non_salarie",
]);

/** Le bloc d'un champ : ni structure, ni servi, ni cotisation, il est de la liquidation. */
export function famille(champ) {
  if (STRUCTURE.has(champ)) return "structure";
  if (SERVI.has(champ)) return "servi";
  if (COTISATION.has(champ)) return "cotisation";
  return "liquidation";
}

/** Le 1er janvier de l'année, en AAAA-MM-JJ. */
export function premierJanvier(annee) {
  return `${String(annee).padStart(4, "0")}-01-01`;
}

/** Le premier jour d'un mois (`DateMois`), en AAAA-MM-JJ. */
export function premierDuMois(date) {
  return `${String(date.annee).padStart(4, "0")}-${String(date.mois).padStart(2, "0")}-01`;
}

/** La ligne au jour en vigueur ce jour-là (AAAA-MM-JJ), ou `null`. */
export function enVigueurAuJour(lignes, jour) {
  for (const ligne of lignes) {
    if (ligne.du <= jour && (ligne.au === null || jour < ligne.au)) return ligne;
  }
  return null;
}

/** Les lignes de cotisation qui couvrent l'année, dans l'ordre : ses tranches. */
export function tranchesDeLAnnee(lignes, annee) {
  return lignes.filter((l) => l.du <= annee && (l.au === null || annee <= l.au));
}
