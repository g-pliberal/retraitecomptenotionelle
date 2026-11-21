// Ce que le moteur rend, pour le contrôle Z3 (`scripts/regles_z3/moteur.py`).
//
//   node moteur.mjs <dépôt> extrait   les tables de la décote et de la
//       proratisation, par mois de naissance de 1900 à 2010 (âge d'ouverture et
//       d'annulation, coefficient de minoration, durée de proratisation), et
//       la pratique de la Cnav que le moteur garde au code
//       (`DUREES_AVANT_LE_DECRET`) : JSON.
//   node moteur.mjs <dépôt> durees    la durée requise du régime général, pour
//       chaque génération de 1900 à 1999 et chaque date d'effet (1er du mois)
//       de 1980 à 2040 : `DureesRequises.deLaPension` puis la pratique de la
//       caisse, comme `ouvrir.js`. Lignes « génération, AAAAMMJJ, trimestres ».
//   node moteur.mjs <dépôt> fiches    pour chaque génération de 1900 à 2010 et
//       chaque date d'effet de 1980 à 2045 : l'âge légal et l'âge du taux plein
//       de la version du jour (`aLEffet`), les portes de la carrière longue
//       (`CarriereLongue.portes`) ; et, par génération, l'âge légal et l'âge du
//       taux plein de la personne. Tout en mois.
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const [racine, quoi] = process.argv.slice(2);
const R = await import(pathToFileURL(join(racine, "moteur/js/regimes.js")));
const paquet = JSON.parse(readFileSync(join(racine, "moteur/donnees.json"), "utf8"));
const gen = (a, m) => Math.round((a + (m - 1) / 12) * 1000) / 1000;
const mo = (x) => (x === null || x === undefined ? -1 : Math.round(x * 12));
const ecrire = (lignes) => { for (const l of lignes) process.stdout.write(l + "\n"); };

if (quoi === "extrait") {
  const annulation = new R.AgesAnnulationDecote(paquet);
  const ouverture = new R.AgesOuverture(paquet);
  const coef = new R.CoefficientsMinoration(paquet);
  const prorat = new R.DureesProratisation(paquet);
  const tables = [];
  for (let a = 1900; a <= 2010; a++) for (let m = 1; m <= 12; m++) {
    const g = gen(a, m);
    const A = annulation.age(g, null), O = ouverture.age(g, null);
    const c = coef.coefficient(a), p = prorat.trimestres(g);
    tables.push({ mois: a * 12 + m - 1, annulation: A && A[0], ouverture: O && O[0],
                  coefficient: c && c[0], proratisation: p && p[0] });
  }
  process.stdout.write(JSON.stringify({ tables, durees_avant_le_decret: R.DUREES_AVANT_LE_DECRET }));
} else if (quoi === "durees") {
  const durees = new R.DureesRequises(paquet);
  for (let a = 1900; a <= 1999; a++) for (let m = 1; m <= 12; m++) {
    const g = gen(a, m), lignes = [];
    for (let ae = 1980; ae <= 2040; ae++) for (let me = 1; me <= 12; me++) {
      const lue = durees.deLaPension(`${ae}-${String(me).padStart(2, "0")}-01`, g);
      let t = lue === null ? 160 : lue[0];
      if (lue !== null) {
        const effet = ae * 12 + me;
        for (const [p, s, [an, mm], tr] of R.DUREES_AVANT_LE_DECRET) {
          if (g >= p && g < s && effet <= an * 12 + mm && tr < lue[0]) { t = tr; break; }
        }
      }
      lignes.push(`${a * 12 + m - 1}\t${ae * 10000 + me * 100 + 1}\t${t}`);
    }
    ecrire(lignes);
  }
} else if (quoi === "fiches") {
  const { DateMois } = await import(pathToFileURL(join(racine, "moteur/js/calendrier.js")));
  const legal = new R.AgesOuverture(paquet);
  const plein = new R.AgesAnnulationDecote(paquet);
  const cl = new R.CarriereLongue(paquet);
  const versionsL = new Map(), versionsP = new Map();
  for (let ae = 1980; ae <= 2045; ae++) for (let me = 1; me <= 12; me++) {
    const date = `${ae}-${String(me).padStart(2, "0")}-01`;
    versionsL.set(date, legal.aLEffet(date));
    versionsP.set(date, plein.aLEffet(date));
  }
  for (let a = 1900; a <= 2010; a++) for (let m = 1; m <= 12; m++) {
    const g = gen(a, m), rg = a * 12 + m - 1, lignes = [];
    lignes.push(`P\t${rg}\t${mo(legal.age(g)?.[0])}\t${mo(plein.age(g)?.[0])}`);
    for (let ae = 1980; ae <= 2045; ae++) for (let me = 1; me <= 12; me++) {
      const date = `${ae}-${String(me).padStart(2, "0")}-01`;
      const L = mo(versionsL.get(date).age(g)?.[0]);
      const T = mo(versionsP.get(date).age(g)?.[0]);
      const portes = cl.portes({ dateLiquidation: new DateMois(ae, me), generation: g });
      const p = portes === null ? "-" : portes.map(([ageMax, , ageDepart, supp]) =>
        `${ageMax}:${supp}:${mo(ageDepart)}`).sort().join(",");
      lignes.push(`D\t${rg}\t${ae * 12 + me - 1}\t${L}\t${T}\t${p}`);
    }
    ecrire(lignes);
  }
} else {
  process.stderr.write("usage : node moteur.mjs <dépôt> extrait|durees|fiches\n");
  process.exit(2);
}
