/**
 * Calcule les indicateurs de cycle de vie avec le portage JavaScript.
 *
 * Reçoit un fichier JSON — `{cas: [{carriere, conventions}], equilibres:
 * [{generation, sexe}], remplacements: [scenario], impots: [{annee, foyer,
 * unite, indexation}], balayages: [{carriere, age, cor, pas, impot}]}` — et
 * écrit, pour chaque cas, les contributions
 * d'équilibre de la carrière, ses revenus nets et imposables, l'impôt de
 * chaque année et ses indicateurs sous chaque convention ; pour chaque
 * génération, ses âges d'équilibre ; pour chaque foyer, son impôt, étape par
 * étape ; pour chaque balayage, ses âges de départ et ce que chacun donne.
 * `tests/test_cycle_de_vie_portage.py` compare le tout au modèle
 * Python.
 *
 *     node tests/js/comparer-cycle-de-vie.mjs demande.json
 */

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { Contexte } from "../../moteur/js/contexte.js";
import { contributionsDUneCarriere } from "../../moteur/js/contributions-equilibre.js";
import {
  ageDeDecesCor, ageDEquilibre, ageDePartDeVieConstante, agesBalayes, balayageDUneCarriere,
  Convention, conventionApresImpot, conventionNette, fluxDesSystemes, indicateursDesSystemes, prelevementsParAnnee,
  remplacementApresImpot, revenusImposables, revenusNets, tauxDePrelevement,
} from "../../moteur/js/cycle-de-vie.js";
import {
  chargerBaremesImpotRevenu, croissanceMacro, Declarant, Foyer, impotDuFoyer,
} from "../../moteur/js/impot-revenu.js";

const RACINE = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const paquet = JSON.parse(readFileSync(join(RACINE, "moteur/donnees.json"), "utf8"));
const simulateur = new Contexte(paquet).simulateur();
const demande = JSON.parse(readFileSync(process.argv[2], "utf8"));

const parAnnee = (valeurs) => (valeurs === null ? null : Object.fromEntries(valeurs));

const cas = demande.cas.map(({ carriere: options, conventions }) => {
  try {
    const carriere = simulateur.carriereSimple(options);
    const comparaison = simulateur.simuler(carriere);
    const indicateurs = {};
    for (const [nom, champs] of Object.entries(conventions)) {
      const { construite = null, impot = null, ...reglages } = champs;
      if (reglages.age_deces === "cor") {
        reglages.age_deces = ageDeDecesCor(simulateur.mortalite, carriere.annee_naissance);
      }
      let convention;
      if (impot !== null) {
        convention = conventionApresImpot(simulateur, comparaison, construite === "cor", impot);
      } else if (construite !== null) {
        convention = conventionNette(simulateur, comparaison, construite === "cor");
      } else {
        convention = new Convention(reglages);
      }
      const systemes = indicateursDesSystemes(simulateur, comparaison, convention);
      indicateurs[nom] = Object.fromEntries(Object.entries(systemes)
        .map(([scenario, valeurs]) => [scenario, valeurs.dictionnaire()]));
    }
    const sousLImpot = fluxDesSystemes(simulateur, comparaison, { impot: "prix" });
    const actuel = sousLImpot.actuel;
    return {
      impots: Object.fromEntries([...actuel.impots].map(([annee, i]) => [annee,
        [i.salaire, i.pension, i.impot, i.sur_la_pension]])),
      revenus_apres_impot: parAnnee(actuel.revenus_apres_impot),
      dernier_revenu_apres_impot: actuel.dernier_revenu_apres_impot,
      remplacements_apres_impot: Object.fromEntries(demande.remplacements.map((scenario) => [
        scenario,
        remplacementApresImpot(simulateur, comparaison, scenario, "prix", sousLImpot)])),
      contributions: Object.fromEntries(contributionsDUneCarriere(simulateur, carriere)),
      taux_de_prelevement: tauxDePrelevement(simulateur, comparaison.actuel),
      revenus_nets: parAnnee(revenusNets(simulateur, carriere)),
      revenus_nets_proposition: parAnnee(revenusNets(simulateur, carriere, true)),
      revenus_imposables: parAnnee(revenusImposables(simulateur, carriere)),
      prelevements: parAnnee(prelevementsParAnnee(simulateur, comparaison)),
      indicateurs,
    };
  } catch (erreur) {
    return { erreur: String(erreur.stack ?? erreur) };
  }
});

const equilibres = demande.equilibres.map(({ generation, sexe }) => {
  const age = ageDEquilibre(simulateur, generation, sexe);
  return {
    age: age.age, au_mois: age.au_mois, coefficient: age.coefficient,
    part_de_vie: ageDePartDeVieConstante(simulateur, generation, sexe),
    part_de_vie_cor: ageDePartDeVieConstante(simulateur, generation, sexe, true),
  };
});

const baremes = chargerBaremesImpotRevenu(paquet);
const impots = (demande.impots ?? []).map(({ annee, foyer, unite, indexation }) => {
  const resultat = impotDuFoyer(new Foyer({
    ...foyer, declarants: foyer.declarants.map((d) => new Declarant(d)),
  }), annee, baremes, {
    unite, indexation, croissance: croissanceMacro(simulateur.macro, indexation),
  });
  return { ...resultat, remarques: [...resultat.remarques] };
});

const balayages = (demande.balayages ?? []).map(({ carriere: options, age, cor, pas, impot }) => {
  try {
    const batir = (a) => simulateur.carriereSimple({ ...options, age_liquidation: a });
    return {
      ages: agesBalayes(simulateur, batir, age, pas),
      departs: balayageDUneCarriere(simulateur, batir, age, cor, pas, impot).map((d) => ({
        ...d,
        indicateurs: Object.fromEntries(Object.entries(d.indicateurs)
          .map(([scenario, valeurs]) => [scenario, valeurs.dictionnaire()])),
        remplacements: Object.fromEntries(Object.entries(d.remplacements)
          .map(([scenario, r]) => [scenario, r === null ? null : { ...r }])),
      })),
    };
  } catch (erreur) {
    return { erreur: String(erreur.stack ?? erreur) };
  }
});

process.stdout.write(JSON.stringify({ cas, equilibres, impots, balayages }));
