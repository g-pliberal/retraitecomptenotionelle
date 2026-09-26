/**
 * Préparer la chronologie (docs/architecture.md, § 7.2).
 *
 * Jumeau de `src/retraite_notionnelle/droit/preparer.py` : la première des
 * quatre étapes qui construisent le relevé des droits. Ce que la saisie ne dit
 * pas, une présomption le pose, en son nom, sans jamais remplacer un fait
 * déclaré (§ 5.6). Son schéma est le contrat C.1
 * (`data/reference/etapes/preparer_la_chronologie.yaml`).
 */

import { completer } from "../chronologie.js";

/**
 * La chronologie complétée par les présomptions du paquet de données, ou par
 * celles que `presomptions` donne ({nom: {valeur}}).
 */
export function preparer(chronologie, presomptions = null) {
  return completer(chronologie, presomptions);
}
