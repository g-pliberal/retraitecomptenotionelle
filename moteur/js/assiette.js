/**
 * Sur quoi l'on prélève : l'assiette des revenus d'activité.
 *
 * Portage de ``src/retraite_notionnelle/donnees/assiette.py``.
 *
 * Le reste du dépôt travaille en RAPPORTS, parce qu'un rapport est robuste :
 * les erreurs de niveau se retrouvent des deux côtés et s'annulent. Ce module
 * porte la grandeur que le rapport ne donne pas, et dont on ne peut pas se
 * passer ici : le NIVEAU de ce sur quoi un taux de cotisation s'applique. Un
 * rapport de taux LÉGAUX appliqué à des ressources OBSERVÉES transporte avec
 * lui la structure de son dénominateur, exonérations comprises ; avec
 * l'assiette en niveau, on ne le devine plus, on le mesure.
 *
 * Les deux postes : `salaires_bruts` est l'assiette des salariés, c'est sur le
 * salaire brut que les deux parts de la cotisation sont calculées ;
 * `revenu_mixte` est celle des non-salariés. Les additionner suppose que l'on
 * tienne le revenu mixte pour un revenu du travail, ce qu'il n'est qu'en
 * partie — il rémunère aussi le capital de l'entrepreneur individuel. Le
 * compte national ne les sépare pas, l'assiette sociale non plus.
 */

import { SerieAnnuelle } from "./serie.js";

/** Les deux postes du fichier, dans l'ordre d'affichage. */
export const POSTES_ASSIETTE = [
  { code: "salaires_bruts", libelle: "Salaires et traitements bruts" },
  { code: "revenu_mixte", libelle: "Revenu mixte des ménages" },
];

/** L'assiette des revenus d'activité, en euros et en part du PIB. */
export class AssietteActivite {
  constructor(paquet) {
    const brut = paquet.comptes_retraite;
    this.postes = new Map(
      POSTES_ASSIETTE.map(({ code }) => [
        code,
        SerieAnnuelle.depuisPaquet(`assiette_${code}`, brut[`assiette_${code}`]),
      ]),
    );
    this.pib = SerieAnnuelle.depuisPaquet("pib_courant", paquet.depenses.pib_courant);
    const postes = [...this.postes.values()];
    this.premiereAnnee = Math.max(...postes.map((s) => s.premiereAnnee));
    // Dernière année où les DEUX postes et le PIB sont publiés : une assiette
    // amputée d'un de ses postes ne serait pas une assiette.
    this.derniereAnnee = Math.min(
      ...postes.map((s) => s.derniereAnnee), this.pib.derniereAnnee,
    );
  }

  /** Un poste de l'assiette, en millions d'euros courants. */
  poste(code, annee) {
    return this.postes.get(code).valeur(annee);
  }

  /** L'assiette entière, en millions d'euros courants. */
  montant(annee) {
    let somme = 0;
    for (const serie of this.postes.values()) somme += serie.valeur(annee);
    return somme;
  }

  /** L'assiette rapportée au PIB de la même année. */
  partPib(annee) {
    const pib = this.pib.valeur(annee);
    return pib ? this.montant(annee) / pib : 0.0;
  }

  /**
   * L'année dont le taux de prélèvement vaut pour `annee` : elle-même tant que
   * l'assiette est publiée, la dernière publiée ensuite. Ce détour existe
   * parce que `SerieAnnuelle` reconduit la valeur du bord, et que reconduire
   * un MONTANT en euros courants de 2025 jusqu'en 2070 ne veut rien dire.
   * C'est le taux qui est reconduit, et l'assiette s'en déduit.
   */
  anneeDeReference(annee) {
    return Math.min(annee, this.derniereAnnee);
  }

  /**
   * Ce que le système prélève, rapporté à l'assiette de la MÊME année. Les
   * deux termes sont en part du PIB : le rapport est sans dimension, et c'est
   * lui qui convertit un taux affiché en recette.
   *
   * CE QU'ELLE NE FAIT PAS : projeter. Reconduire ce taux tel quel au-delà de
   * la fenêtre publiée supposerait que tout le recul des ressources du COR
   * vient de l'assiette — l'inverse de ce qu'il projette. Le prolongement est
   * le travail de `ComptesRetraite.profilTaux`, qui lit la trajectoire chez le
   * producteur ; ici, on mesure une année, et une seule.
   */
  tauxPrelevement(ressourcesPartPib, annee) {
    const part = this.partPib(annee);
    return part ? ressourcesPartPib / part : 0.0;
  }

  fiabilite(annee) {
    const niveaux = [...this.postes.values()].map((s) => s.fiabilite(annee));
    niveaux.push(this.pib.fiabilite(annee));
    return Math.min(...niveaux);
  }
}
