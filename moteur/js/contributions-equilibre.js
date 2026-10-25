/**
 * Les contributions d'équilibre de l'Agirc-Arrco : prélevées pour la
 * retraite, sans points — portage de `contributions_equilibre.py`, qui fait
 * foi et dit le détail.
 *
 * L'ASF jusqu'au 31 mars 2001, l'AGFF jusqu'en 2018, la CET de l'Agirc de
 * 1997 à 2018, la CEG et la CET depuis 2019. Le compte notionnel ne les porte
 * pas (décision du 2 octobre 2026) ; les indicateurs de cycle de vie
 * (`cycle-de-vie.js`) les ajoutent à ce que la paie supporte pour la
 * retraite. Le paquet les porte telles que le Python les lit
 * (`contributions_equilibre`, `scripts/construire_donnees.py`).
 */

const regles = new WeakMap();

/** Les règles du paquet, lues une fois ; aucune contribution sans elles. */
export function chargerContributionsEquilibre(paquet) {
  if (regles.has(paquet)) return regles.get(paquet);
  const brut = paquet.contributions_equilibre ?? null;
  const lues = {
    contributions: (brut?.contributions ?? []).map((c) => ({
      ...c,
      regimes: new Set(c.regimes),
      statuts_exclus: new Set(c.statuts_exclus ?? []),
    })),
    regimes_cadres: new Set(brut?.regimes_cadres ?? []),
  };
  lues.regimes = new Set(lues.contributions.flatMap((c) => [...c.regimes]));
  regles.set(paquet, lues);
  return lues;
}

/**
 * Ce que prélèvent `tranches` sur `assiette`, sous un plafond de `plafond`
 * euros ; avec `salarie`, la seule part du salarié.
 */
export function prelevement(tranches, assiette, plafond, salarie = false) {
  let total = 0.0;
  let bas = 0.0;
  for (const tranche of tranches) {
    const haut = tranche.jusqu_en_plafonds === null
      ? Infinity : tranche.jusqu_en_plafonds * plafond;
    if (assiette > bas && haut > bas) {
      total += (Math.min(assiette, haut) - bas)
        * (salarie ? tranche.salarie : tranche.salarie + tranche.employeur);
    }
    bas = Math.max(bas, haut);
  }
  return total;
}

function jourIso(annee, mois) {
  return `${String(annee).padStart(4, "0")}-${String(mois).padStart(2, "0")}-01`;
}

/** Le barème d'une contribution en vigueur le `jour` (ISO), `null` hors de sa vie. */
function bareme(contribution, jour) {
  if (contribution.jusqu_au !== null && jour > contribution.jusqu_au) return null;
  let retenu = null;
  for (const b of contribution.baremes) {
    if (b.debut <= jour) retenu = b;
  }
  return retenu;
}

/**
 * Ce qu'une contribution prélève sur `assiette`, revenu d'une activité de
 * l'année `annee` : la moyenne des douze barèmes mensuels.
 */
export function montantDeLaContribution(contribution, annee, assiette, plafond, cadre,
  salarie = false) {
  const seuil = contribution.due_au_dela_de_plafonds;
  if (seuil !== null && assiette <= seuil * plafond) return 0.0;
  let somme = 0.0;
  for (let rang = 1; rang <= 12; rang += 1) {
    const b = bareme(contribution, jourIso(annee, rang));
    somme += b === null ? 0.0
      : prelevement(cadre ? b.cadres : b.non_cadres, assiette, plafond, salarie);
  }
  return somme / 12.0;
}

/** Le forfait d'un régime à assiette forfaitaire, proratisé ; `null` sans forfait. */
function forfait(catalogue, regimes, annee, macro, part) {
  for (const code of [...regimes].sort()) {
    const periode = catalogue.contient(code) ? catalogue.obtenir(code).periode(annee) : null;
    if (periode !== null && periode.assiette_forfaitaire) {
      return periode.repereAssiette(macro.plafond_securite_sociale.valeur(annee),
        macro.smic_horaire.valeur(annee)) * part;
    }
  }
  return null;
}

function dues(lues, simulateur, carriere, ligne) {
  const affiliations = simulateur.affiliations;
  const annee = ligne.annee;
  const entree = affiliations.dateEntree(carriere, ligne.affiliation, annee);
  const [services] = affiliations.servicesPasses(ligne.affiliation, annee, entree);
  const codes = new Set(affiliations.regimes(ligne.affiliation, annee, entree, ligne.revenu,
    simulateur.macro.plafond_securite_sociale.valeur(annee))
    .filter((code) => !services.has(code)));
  if (![...codes].some((code) => lues.regimes.has(code))) return null;
  const contributions = lues.contributions.filter(
    (c) => [...codes].some((code) => c.regimes.has(code))
      && !c.statuts_exclus.has(ligne.affiliation));
  const cadre = [...codes].some((code) => lues.regimes_cadres.has(code));
  return [codes, contributions, cadre];
}

function communs(codes, contribution) {
  return new Set([...codes].filter((code) => contribution.regimes.has(code)));
}

/**
 * Les contributions d'équilibre que verse `carriere`, année par année, en
 * euros courants, salariale et patronale réunies : `Map` année → montant.
 */
export function contributionsDUneCarriere(simulateur, carriere) {
  const lues = chargerContributionsEquilibre(simulateur.paquet);
  const sommes = new Map();
  if (lues.contributions.length === 0) return sommes;
  const macro = simulateur.macro;
  for (const ligne of carriere.lignes) {
    if (!ligne.cotise) continue;
    const part = carriere.partRetenueLigne(ligne);
    if (part <= 0 || ligne.fraction_annee <= 0) continue;
    const trouvees = dues(lues, simulateur, carriere, ligne);
    if (trouvees === null) continue;
    const [codes, contributions, cadre] = trouvees;
    const annee = ligne.annee;
    // Comme au compte : l'année du départ ne porte que les mois qui le
    // précèdent, et le plafond se proratise sur les mêmes mois.
    const assiette = ligne.revenu * Math.min(1.0, part / ligne.fraction_annee);
    const plafond = macro.plafond_securite_sociale.valeur(annee) * part;
    let montant = 0.0;
    for (const contribution of contributions) {
      const f = forfait(simulateur.catalogue, communs(codes, contribution), annee, macro, part);
      montant += montantDeLaContribution(contribution, annee, f === null ? assiette : f,
        plafond, cadre);
    }
    if (montant > 0.0) sommes.set(annee, (sommes.get(annee) ?? 0.0) + montant);
  }
  return sommes;
}

/**
 * La part salariale des contributions d'équilibre sur le revenu annualisé de
 * `ligne`, sous le plafond de l'année entière.
 */
export function partSalarialeAnnualisee(simulateur, carriere, ligne) {
  const lues = chargerContributionsEquilibre(simulateur.paquet);
  if (lues.contributions.length === 0 || !ligne.cotise) return 0.0;
  const trouvees = dues(lues, simulateur, carriere, ligne);
  if (trouvees === null) return 0.0;
  const [codes, contributions, cadre] = trouvees;
  const annee = ligne.annee;
  const macro = simulateur.macro;
  const plafond = macro.plafond_securite_sociale.valeur(annee);
  let somme = 0.0;
  for (const contribution of contributions) {
    const f = forfait(simulateur.catalogue, communs(codes, contribution), annee, macro, 1.0);
    somme += montantDeLaContribution(contribution, annee,
      f === null ? ligne.revenuAnnualise : f, plafond, cadre, true);
  }
  return somme;
}
