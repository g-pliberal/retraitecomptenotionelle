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
 * Le paquet porte les quatre blocs (étape 4 de l'amendement). PENDANT LE GEL,
 * le pont et les tests lisent encore des périodes : `periodesDesAxes` en
 * refait la vue, et `axesDesPeriodes` les blocs des périodes que le taux moyen
 * de l'Agirc-Arrco redate et que `sansDeclaration` retouche. L'une et l'autre
 * partent avec la vue ancienne, à l'étape 5.
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

/** Ce qu'une période porte en plus de ses champs : ses bornes, sa note. */
const BORNES = new Set(["debut", "fin", "date_effet", "notes", "regime"]);

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

const jan = premierJanvier;

/** Les dates d'effet qu'une période liquide, `[début, fin)` : voir `PeriodeRegime.effet`. */
function effetDe(periode) {
  if (periode.date_effet !== null && periode.date_effet !== undefined) {
    return periode.date_effet;
  }
  return [jan(periode.debut), periode.fin === null ? null : jan(periode.fin + 1)];
}

function liquide(periode, jour) {
  const [debut, fin] = effetDe(periode);
  return debut <= jour && (fin === null || jour < fin);
}

function champsDe(periode, bloc) {
  const champs = {};
  for (const [champ, valeur] of Object.entries(periode)) {
    if (!BORNES.has(champ) && famille(champ) === bloc) champs[champ] = valeur;
  }
  return champs;
}

/** Une empreinte des champs d'une ligne, clés triées : deux lignes égales se fondent. */
function empreinte(champs) {
  return JSON.stringify(Object.keys(champs).sort().map((c) => [c, champs[c]]));
}

/**
 * Les lignes d'un bloc au jour, refaites des périodes : chaque intervalle entre
 * deux bornes d'effet prend la première période qui le liquide, comme
 * `Regime.periodeALEffet` ; deux intervalles contigus aux mêmes champs se
 * fondent. Un intervalle qu'aucune période ne liquide n'a pas de ligne.
 */
function lignesAuJour(periodes, bloc) {
  const bornes = new Set();
  for (const periode of periodes) {
    for (const borne of effetDe(periode)) if (borne !== null) bornes.add(borne);
  }
  const triees = [...bornes].sort();
  const lignes = [];
  let precedente = null;
  triees.forEach((du, rang) => {
    const au = rang + 1 < triees.length ? triees[rang + 1] : null;
    const periode = periodes.find((p) => liquide(p, du));
    if (periode === undefined) {
      precedente = null;
      return;
    }
    const champs = champsDe(periode, bloc);
    const cle = empreinte(champs);
    if (precedente !== null && precedente.cle === cle && precedente.ligne.au === du) {
      precedente.ligne.au = au;
      return;
    }
    const ligne = { du, au, ...champs };
    lignes.push(ligne);
    precedente = { cle, ligne };
  });
  return lignes.map((ligne) => Object.freeze(ligne));
}

/**
 * Les quatre blocs d'un régime, refaits des périodes de la vue ancienne que
 * le paquet porte encore. La cotisation garde une ligne par période, dans
 * l'ordre du paquet, bornée à ses années (`du`, `au` inclus) ; la
 * liquidation, le servi et la structure, des lignes au jour.
 */
export function axesDesPeriodes(periodes) {
  return {
    structure: lignesAuJour(periodes, "structure"),
    liquidation: lignesAuJour(periodes, "liquidation"),
    servi: lignesAuJour(periodes, "servi"),
    cotisation: periodes.map((p) => Object.freeze({
      du: p.debut, au: p.fin, ...champsDe(p, "cotisation") })),
  };
}

/**
 * La vue des périodes, refaite des blocs que porte le paquet : une période par
 * ligne de cotisation, dans leur ordre, ses années celles de la ligne, avec la
 * liquidation, la structure et le servi en vigueur au premier jour de sa date
 * d'effet. `datesDEffet` donne, au rang de sa ligne, la date d'effet qu'une
 * période déclarait. C'est la réciproque d'`axesDesPeriodes` ; elle part à
 * l'étape 5, avec la vue.
 */
export function periodesDesAxes(axes, datesDEffet = {}) {
  return axes.cotisation.map((cotisation, rang) => {
    const periode = { debut: cotisation.du, fin: cotisation.au };
    const dateEffet = datesDEffet[String(rang)];
    if (dateEffet !== undefined) periode.date_effet = dateEffet;
    const jour = dateEffet !== undefined ? dateEffet[0] : jan(cotisation.du);
    for (const ligne of [enVigueurAuJour(axes.liquidation, jour),
      enVigueurAuJour(axes.structure, jour), enVigueurAuJour(axes.servi, jour), cotisation]) {
      if (ligne === null) continue;
      for (const [champ, valeur] of Object.entries(ligne)) {
        if (champ !== "du" && champ !== "au") periode[champ] = valeur;
      }
    }
    return periode;
  });
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
