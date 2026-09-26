/**
 * Le pilote (docs/architecture.md, § 7.7) : ce que le droit ne décide pas.
 *
 * Jumeau de `src/retraite_notionnelle/pilote.py`. Le moteur ne devine rien :
 * il liquide la demande qu'on lui fait. Hors de lui, un pilote fixe le reste
 * — LES COMPORTEMENTS : partir au taux plein, à l'âge où le droit s'ouvre,
 * après une durée de services. `ageDeDepart` interroge le moteur, au besoin
 * plusieurs fois, jusqu'à un point fixe ; il ne lui faut qu'un âge, et il
 * n'interroge donc que l'étape « ouvrir le droit » (`droit/ouvrir.js`), sans
 * rien liquider. La date qu'il trouve devient celle du départ de la carrière,
 * que l'échéancier traite (`echeancier.js`). Les populations — les cas types
 * pondérés — restent dans `castypes.js`.
 */

import { carriereCasType } from "./castypes.js";
import * as ouvrir from "./droit/ouvrir.js";

/**
 * Les deux façons de dater le départ d'un cas type.
 *
 * `droit` est celle des résultats affichés : chaque génération liquide à l'âge
 * que SON droit lui ouvre. `absolu` est l'ancienne, gardée non comme repli mais
 * comme variante — l'âge écrit dans la grille, le même pour toutes les
 * générations, qui faisait partir celle de 1940 à soixante-quatre ans en 2004
 * alors que la loi ne les lui a jamais demandés.
 */
export const VARIANTES_LIQUIDATION = ["droit", "absolu"];

/**
 * Nombre de fois que l'âge de liquidation est rapproché de son âge de
 * référence. Il en faut plus d'une : l'âge qu'une fiche de régime oppose dépend
 * de l'ANNÉE de liquidation — celle de la SNCF et celle des IEG montent d'un
 * trimestre par millésime —, si bien que déplacer l'âge déplace la réponse.
 */
export const PASSES_LIQUIDATION = 4;

/**
 * L'âge auquel le cas type `cas` liquide, étant né en `generation`.
 *
 * **Pourquoi ce n'est pas un nombre.** Un cas type décrit une carrière, pas une
 * date : « le salarié au salaire moyen » n'est pas « celui qui part à
 * soixante-quatre ans », c'est celui qui part quand la loi le lui permet.
 * Écrire l'âge revenait à faire partir à soixante-quatre ans une génération née
 * en 1940 — c'est-à-dire en 2004, sous un droit qui en demandait soixante.
 *
 * **Comment la réponse est trouvée.** L'âge de référence dépend de la carrière,
 * laquelle dépend de l'âge de liquidation : la question tourne en rond, et on la
 * résout par un POINT FIXE. On part de l'âge écrit, on demande au scénario 1 ce
 * que le droit oppose à cette liquidation-là, on recommence. Deux garde-fous :
 * le nombre de passes est borné, et une descente n'est retenue que si l'âge plus
 * précoce est lui-même confirmé. Le second n'est pas décoratif — la CANCAVA
 * ouvrait à soixante-cinq ans jusqu'en 1972 et à soixante à partir de 1973, si
 * bien qu'un artisan né en 1910 « ouvre » à soixante ans un droit que son année
 * de départ lui refuse.
 */
export function ageDeDepart(simulateur, cas, generation, variante = "droit") {
  if (!VARIANTES_LIQUIDATION.includes(variante)) {
    throw new Error(
      `variante de liquidation inconnue : ${variante} `
      + `(attendu : ${VARIANTES_LIQUIDATION.join(", ")})`,
    );
  }
  if (variante === "absolu") {
    return cas.age_liquidation;
  }
  if (cas.regle_liquidation === "services") {
    return cas.age_debut + cas.ecart_liquidation;
  }
  if (!["ouverture", "taux_plein"].includes(cas.regle_liquidation)) {
    throw new Error(`règle de liquidation inconnue : ${cas.regle_liquidation}`);
  }
  let age = cas.age_liquidation;
  for (let passe = 0; passe < PASSES_LIQUIDATION; passe += 1) {
    const propose = agePropose(simulateur, cas, generation, age);
    if (propose === null || Math.abs(propose - age) < 1e-9) {
      break;
    }
    if (propose > age) {
      age = propose;
      continue;
    }
    const confirme = agePropose(simulateur, cas, generation, propose);
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
 * Ce que la règle du cas type oppose à sa carrière liquidée à `age`, décalé :
 * la seule question que le pilote pose au moteur, à l'étape « ouvrir le
 * droit », sans rien liquider.
 */
export function agePropose(simulateur, cas, generation, age) {
  const actuel = simulateur.scenarioActuel;
  const carriere = carriereCasType(cas, simulateur, generation, age);
  const reference = cas.regle_liquidation === "taux_plein"
    ? ouvrir.ageTauxPleinDroit(actuel, carriere)
    : ouvrir.ageOuvertureDroit(actuel, carriere);
  return reference === null ? null : reference + cas.ecart_liquidation;
}
