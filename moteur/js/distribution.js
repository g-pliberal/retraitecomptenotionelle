/**
 * Combien de retraités touchent combien : la distribution des pensions.
 *
 * Portage de ``src/retraite_notionnelle/donnees/distribution.py``. Une grille de
 * douze cas types suffit à comparer des systèmes — un rapport de masses est
 * robuste — mais pas à chiffrer un PLANCHER : une allocation différentielle ne
 * coûte que ce que coûte la queue basse de la distribution, et douze carrières
 * ne la décrivent pas.
 *
 * La source est l'échantillon interrégimes de retraités de la DREES, qui apparie
 * tous les quatre ans les fichiers de toutes les caisses sur un même échantillon
 * d'individus.
 */

/** Répartition des pensions brutes de droit direct, pour un millésime d'EIR. */
export class DistributionPensions {
  constructor(paquet, sexe = "ensemble") {
    // Femmes et hommes à part, pour peser les sexes parmi les bénéficiaires
    // de la garantie ; l'ensemble, sinon.
    const brut = sexe === "ensemble" ? paquet.distribution_pensions
      : paquet.distribution_pensions_sexes[sexe];
    this.millesime = brut.millesime;
    this.sexe = sexe;
    this.fiabilite = brut.fiabilite;
    this.tranches = brut.parts.map((part, rang) => ({
      borneInferieure: brut.bornes_inferieures[rang],
      // ``null`` pour la dernière, que l'enquête laisse ouverte.
      borneSuperieure: brut.bornes_superieures[rang],
      part,
    }));
    // Le paquet porte la distribution des RÉSIDENTS en France, que la
    // garantie sert : la part des résidents met l'effectif à l'échelle, et
    // celle des femmes parmi eux pèse les deux sexes. Voir distribution.py.
    this.partResidents = brut.part_residents ?? 1.0;
    this.partFemmesResidents = brut.part_femmes_residents ?? null;
  }

  /**
   * Doit valoir un, aux arrondis de publication près. La DREES publie ses parts
   * arrondies au centième de point : leur somme vaut 100,01 % et non 100 %.
   * L'écart est réel et ne se corrige pas — redresser les parts inventerait une
   * précision que la source ne donne pas.
   */
  /**
   * La part des retraités dont la pension est inférieure à un montant, en euros
   * du millésime : le rang d'une pension parmi les retraités. Portage de
   * `part_sous` — linéaire dans la tranche, le seuil de la dernière au-delà.
   */
  partSous(montantMensuel) {
    let cumul = 0.0;
    for (const tranche of this.tranches) {
      if (montantMensuel < tranche.borneInferieure) {
        return cumul;
      }
      const ouverte = tranche.borneSuperieure === null || tranche.borneSuperieure === undefined;
      if (ouverte || montantMensuel < tranche.borneSuperieure) {
        if (ouverte) {
          return cumul;
        }
        const largeur = tranche.borneSuperieure - tranche.borneInferieure;
        return cumul + tranche.part * (montantMensuel - tranche.borneInferieure) / largeur;
      }
      cumul += tranche.part;
    }
    return cumul;
  }

  get sommeDesParts() {
    return this.tranches.reduce((somme, tranche) => somme + tranche.part, 0);
  }
}

/**
 * La part des femmes dans la population que l'enquête décrit, lue sur elle.
 * Portage de ``donnees.distribution.part_femmes``.
 *
 * Le dépôt ne porte aucun effectif de retraités par sexe — ni la pyramide des
 * âges de l'INSEE, qui ignore la retraite, ni les effectifs de la DREES, qui
 * ignorent le sexe. Mais l'enquête publie trois colonnes, et la troisième est
 * le mélange des deux premières : il existe un poids, et un seul, tel que
 * `w·F + (1−w)·H` redonne l'ensemble tranche par tranche. Ce poids EST la
 * part des femmes dans sa population, et vaut 52,8 % en 2020.
 *
 * Le modèle prenait jusqu'au 21 septembre 2026 la part des femmes parmi les
 * 65 ans et plus que les courbes de survie donnent en population
 * stationnaire, 56,0 % : un poids qui ne recomposait pas la colonne dont le
 * coût est tiré, et faisait dire au modèle deux choses de la même population.
 *
 * `tolerance` borne le résidu du mélange : cinq fois l'arrondi de la source.
 */
export function partFemmes(paquet, tolerance = 5e-4) {
  const colonnes = ["F", "H", "ensemble"].map(
    (sexe) => new DistributionPensions(paquet, sexe).tranches.map((t) => t.part),
  );
  const [femmes, hommes, ensemble] = colonnes;
  if (femmes.length !== hommes.length || femmes.length !== ensemble.length) {
    throw new Error(
      "les trois colonnes de la distribution n'ont pas le même découpage",
    );
  }
  // Moindres carrés sur le seul inconnu : le poids qui mélange les deux sexes.
  let numerateur = 0.0;
  let denominateur = 0.0;
  for (let rang = 0; rang < femmes.length; rang += 1) {
    const ecart = femmes[rang] - hommes[rang];
    numerateur += (ensemble[rang] - hommes[rang]) * ecart;
    denominateur += ecart * ecart;
  }
  if (denominateur <= 0) {
    throw new Error(
      "les distributions des deux sexes sont identiques : aucun poids ne s'en déduit",
    );
  }
  const poids = numerateur / denominateur;
  let residu = 0.0;
  for (let rang = 0; rang < femmes.length; rang += 1) {
    residu = Math.max(residu, Math.abs(
      poids * femmes[rang] + (1.0 - poids) * hommes[rang] - ensemble[rang],
    ));
  }
  if (residu > tolerance) {
    throw new Error(
      `la colonne « ensemble » n'est pas le mélange des deux sexes : résidu de ${residu}`,
    );
  }
  return poids;
}
