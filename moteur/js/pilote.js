/**
 * Le pilote (docs/architecture.md, § 7.7) : ce que le droit ne décide pas.
 *
 * Portage d'une partie de `src/retraite_notionnelle/pilote.py`. Le moteur ne
 * devine rien : il liquide la demande qu'on lui fait. Hors de lui, un pilote
 * fixe le reste — LES COMPORTEMENTS : partir au taux plein, à l'âge où le
 * droit s'ouvre. Il interroge le moteur, au besoin plusieurs fois, jusqu'à un
 * point fixe ; il ne lui faut qu'un âge, et il n'interroge donc que l'étape
 * « ouvrir le droit » (`droit/ouvrir.js`), sans rien liquider. Ces points
 * fixes datent les trois départs que « Mon estimation retraite » chiffre, pour
 * la carrière d'une saisie (`agesDeLEstimation`).
 *
 * Le départ des cas types (`age_de_depart` du Python) n'est plus porté depuis
 * le 11 octobre 2026 : il ne servait qu'au portage du coût, parti avec lui
 * (action 150), et la table figée porte l'âge de chaque case de la grille.
 * Seul `pointFixe` garde donc son jumeau, `point_fixe`, dont le Python date les
 * cas types. Les départs de l'estimation, eux, n'ont que cet exemplaire depuis
 * l'action 161, étape 6 : seul le site les chiffre, et leur moitié Python, qui
 * ne servait plus qu'à confronter les deux moteurs, est retirée.
 */

import * as ouvrir from "./droit/ouvrir.js";

/**
 * Nombre de fois que l'âge de liquidation est rapproché de son âge de
 * référence. Il en faut plus d'une : l'âge qu'une fiche de régime oppose dépend
 * de l'ANNÉE de liquidation — celle de la SNCF et celle des IEG montent d'un
 * trimestre par millésime —, si bien que déplacer l'âge déplace la réponse.
 */
export const PASSES_LIQUIDATION = 4;

/**
 * L'âge que `proposer` confirme, en partant de `age` : la boucle de
 * `age_de_depart` (pilote.py), que `agesDeLEstimation` emprunte. Une montée se
 * suit ; une descente ne se retient que si l'âge plus précoce se confirme
 * lui-même. Voir `point_fixe` (pilote.py).
 */
export function pointFixe(depart, proposer) {
  let age = depart;
  for (let passe = 0; passe < PASSES_LIQUIDATION; passe += 1) {
    const propose = proposer(age);
    if (propose === null || Math.abs(propose - age) < 1e-9) {
      break;
    }
    if (propose > age) {
      age = propose;
      continue;
    }
    const confirme = proposer(propose);
    if (confirme === null) {
      break;
    }
    if (confirme > propose + 1e-9) {
      // L'âge plus précoce n'est pas ouvert sous SES règles, mais le droit peut
      // s'ouvrir entre les deux (durée datée par la date d'effet depuis la
      // suspension de 2026) : on essaie l'âge qu'il oppose alors.
      if (confirme < age - 1e-9) {
        age = confirme;
        continue;
      }
      break;
    }
    age = propose;
  }
  return age;
}

/**
 * Les départs que « Mon estimation retraite » chiffre, dans l'ordre de sa
 * synthèse : au plus tôt — l'âge légal, ou la carrière longue qui le devance —,
 * au taux plein, au taux plein automatique.
 */
export const DEPARTS_DE_L_ESTIMATION = Object.freeze(["legal", "taux_plein", "automatique"]);

/**
 * Les trois âges de « Mon estimation retraite », pour la carrière que
 * `batir(age)` rend liquidée à `age` : au plus tôt (`ageOuvertureDroit`), au
 * taux plein (`ageTauxPleinDroit`), au taux plein automatique
 * (`ageAnnulationDroit`).
 *
 * Chacun est un point fixe, comme le départ d'un cas type : la carrière dépend
 * de l'âge, et ce que le droit lui oppose dépend de la carrière. Le premier
 * part de `depart`, l'âge que la saisie demande ; chacun des suivants part du
 * précédent, et ne le précède jamais. Le droit date la durée requise comme si
 * la carrière validait encore quatre trimestres par an (`ageTauxPleinDroit`) :
 * sans activité, à deux trimestres de sa durée, elle montait d'un semestre à
 * chaque passe sans en gagner aucun, et le taux plein s'arrêtait au bout des
 * passes, décoté. Quand la montée s'arrête sans lui, la recherche reprend donc
 * de l'âge d'annulation de la décote, comme `age_de_depart` (pilote.py ;
 * action 138, étape 14). La carrière longue date de même la durée cotisée
 * (`ageOuvertureDroit`) : sans activité depuis qu'elle l'a réunie, la carrière
 * la réunissait à chaque passe à l'âge même du départ, et la descente
 * s'arrêtait au-dessus de l'âge où la carrière longue ouvre le départ. Tant
 * qu'un départ un an plus tôt s'ouvre encore, la recherche du premier âge en
 * reprend donc ; un départ que la saisie refuse n'ouvre rien (`sansRefus`).
 * Deux âges peuvent se confondre : la page les réunit (`departsDeLEstimation`,
 * contexte.js). `null` quand le droit n'oppose aucun âge à cette carrière.
 */
export function agesDeLEstimation(actuel, batir, depart) {
  // Les trois règles répondent `null` dans le même cas : aucun régime retenu.
  // Une question suffit donc à le savoir.
  if (ouvrir.ageOuvertureDroit(actuel, batir(depart)) === null) {
    return null;
  }
  const regles = [ouvrir.ageOuvertureDroit, ouvrir.ageTauxPleinDroit,
    ouvrir.ageAnnulationDroit];
  const ages = {};
  let age = depart;
  DEPARTS_DE_L_ESTIMATION.forEach((quoi, rang) => {
    const proposer = (a) => regles[rang](actuel, batir(a));
    let trouve = pointFixe(age, proposer);
    const propose = quoi === "taux_plein" ? proposer(trouve) : null;
    if (propose !== null && propose > trouve + 1e-9) {
      const annulation = ouvrir.ageAnnulationDroit(actuel, batir(trouve));
      if (annulation !== null) {
        trouve = pointFixe(annulation, proposer);
      }
    }
    if (quoi === "legal") {
      const sonder = sansRefus(proposer);
      for (;;) {
        const essai = pointFixe(trouve - 1, sonder);
        const confirme = essai < trouve - 1e-9 ? sonder(essai) : null;
        if (confirme === null || confirme > essai + 1e-9) {
          break;
        }
        trouve = essai;
      }
    }
    age = rang > 0 ? Math.max(age, trouve) : trouve;
    ages[quoi] = age;
  });
  return ages;
}

/**
 * `proposer`, qui répond `null` à un départ que la saisie ou le modèle
 * refusent — un départ qui précède l'un des métiers — : il n'ouvre rien. Une
 * faute de programme remonte, comme dans `departsDeLEstimation` (contexte.js).
 */
function sansRefus(proposer) {
  return (age) => {
    try {
      return proposer(age);
    } catch (erreur) {
      if (erreur instanceof TypeError || erreur instanceof ReferenceError
          || erreur instanceof RangeError || erreur instanceof SyntaxError) {
        throw erreur;
      }
      return null;
    }
  };
}
