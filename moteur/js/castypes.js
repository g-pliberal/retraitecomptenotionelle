/**
 * Cas types — le « cas général », par opposition au cas particulier.
 *
 * Portage de ``src/retraite_notionnelle/castypes.py``. Une simulation
 * individuelle répond à « et moi ? » ; les cas types répondent à « et
 * globalement ? ». On croise un jeu de carrières représentatives avec un jeu de
 * générations, et l'on regarde comment la réforme déplace chacune d'elles.
 *
 * Les carrières retenues suivent l'esprit des cas types du Conseil
 * d'orientation des retraites : elles ne prétendent pas décrire un individu
 * réel, mais isoler l'effet des règles à comportement donné. Elles couvrent
 * volontairement les cas extrêmes du système — régime spécial à départ précoce,
 * carrière interrompue — parce que ce sont eux que la réforme déplace le plus.
 */

/** Jeu de cas types couvrant les principales configurations du système. */
export const CAS_TYPES = [
  {
    code: "smic_carriere_complete",
    libelle: "Salarié au niveau du SMIC, carrière complète",
    affiliation: "salarie_prive_non_cadre",
    age_debut: 18, age_liquidation: 64, niveau_salaire: 0.55,
    profil_carriere: "plat",
    caisses: ["cnav"],
    commentaire: "Carrière longue à bas salaire : le cas où les minima pèsent le plus.",
  },
  {
    code: "salaire_moyen",
    libelle: "Salarié au salaire moyen",
    affiliation: "salarie_prive_non_cadre",
    age_debut: 21, age_liquidation: 64, niveau_salaire: 1.0,
    caisses: ["cnav"],
    commentaire: "Référence centrale.",
  },
  {
    code: "cadre",
    libelle: "Cadre du privé",
    affiliation: "salarie_prive_cadre",
    age_debut: 23, age_liquidation: 64, niveau_salaire: 2.2,
    profil_carriere: "fortement_ascendant",
    caisses: ["cnav"],
    commentaire: "Forte part de rémunération au-dessus du plafond.",
  },
  {
    code: "carriere_interrompue",
    libelle: "Carrière interrompue (5 ans hors emploi)",
    affiliation: "salarie_prive_non_cadre",
    age_debut: 21, age_liquidation: 64, niveau_salaire: 0.9,
    sexe: "F", nombre_enfants: 2,
    caisses: ["cnav"],
    interruptions_relatives: [8, 9, 10, 11, 12].map((d) => [d, "education_enfant"]),
    commentaire: "Cinq années sans cotisation. Le système actuel les couvre par "
      + "des trimestres assimilés, par l'AVPF (qui porte au compte un salaire au SMIC) et par la majoration de durée d'assurance ; le compte notionnel ne "
      + "couvre rien. Les deux premiers ne se voient guère ici : sur une carrière "
      + "de plus de vingt-cinq années portées au compte, les années au SMIC "
      + "n'entrent pas dans les vingt-cinq meilleures, et les trimestres assimilés "
      + "ne servent que si la durée requise n'est pas atteinte. C'est un résultat, "
      + "pas une omission.",
  },
  {
    code: "fonctionnaire_sedentaire",
    libelle: "Fonctionnaire sédentaire (catégorie B)",
    affiliation: "fonctionnaire_etat",
    age_debut: 22, age_liquidation: 64, niveau_salaire: 1.2,
    part_primes: 0.18,
    caisses: ["fonction_publique_etat_civile"],
    commentaire: "Traitement indiciaire hors primes ; les primes relèvent du RAFP.",
  },
  {
    code: "fonctionnaire_actif",
    libelle: "Fonctionnaire de catégorie active (départ anticipé)",
    affiliation: "fonctionnaire_territorial_hospitalier_actif",
    age_debut: 22, age_liquidation: 57, niveau_salaire: 1.1,
    part_primes: 0.22,
    caisses: ["cnracl"],
    regle_liquidation: "ouverture",
    commentaire: "Aide-soignant, agent technique territorial : l'emploi est classé, "
      + "et le départ anticipé de cinq années est celui que l'article L. 24 lui "
      + "ouvre, non une anticipation sanctionnée. Le cas type était calculé comme "
      + "un sédentaire tant qu'aucun statut ne portait le classement. L'âge suit "
      + "sa génération : cinquante-cinq ans jusqu'à celle de 1956, cinquante-sept "
      + "ensuite, cinquante-neuf pour celles que la réforme de 2023 atteint.",
  },
  {
    code: "militaire",
    libelle: "Militaire non officier (radiation après vingt-cinq ans de services)",
    affiliation: "militaire",
    age_debut: 19, age_liquidation: 44, niveau_salaire: 0.95,
    part_primes: 0.25,
    caisses: ["fonction_publique_etat_militaire"],
    regle_liquidation: "services", ecart_liquidation: 25,
    commentaire: "La pension militaire ne s'ouvre pas à un âge mais à une durée : "
      + "dix-sept ans de services pour un non-officier. C'est le départ le plus "
      + "précoce du système, et celui qu'un compte notionnel déplace le plus : quarante ans de rente pour vingt-cinq ans de cotisations. La solde "
      + "indiciaire seule ouvre des droits ; les indemnités, plus lourdes que les "
      + "primes de la fonction publique civile, relèvent du RAFP.",
  },
  {
    code: "agent_sncf_conduite",
    libelle: "Agent de conduite SNCF",
    affiliation: "agent_sncf",
    age_debut: 20, age_liquidation: 52, niveau_salaire: 1.1,
    caisses: ["sncf"],
    regle_liquidation: "ouverture",
    commentaire: "Écart à l'âge de référence parmi les plus élevés du système : "
      + "cinquante ans jusqu'aux départs de 2016, cinquante-quatre au terme de la "
      + "montée en charge. Le régime est fermé aux embauches depuis 2020, et la "
      + "règle en tire la conséquence : la génération 2000, entrée après la "
      + "fermeture, relève du régime général et liquide à l'âge de celui-ci.",
  },
  {
    code: "agent_ieg",
    libelle: "Agent des industries électriques et gazières",
    affiliation: "agent_ieg",
    age_debut: 21, age_liquidation: 57, niveau_salaire: 1.4,
    caisses: ["cnieg"],
    regle_liquidation: "ouverture",
    commentaire: "Régime spécial fermé aux embauches depuis 2023. L'âge "
      + "d'ouverture y est celui du millésime de départ : cinquante-cinq ans "
      + "jusqu'en 2016, cinquante-neuf à compter de 2027.",
  },
  {
    code: "artisan",
    libelle: "Artisan",
    affiliation: "artisan",
    age_debut: 24, age_liquidation: 64, niveau_salaire: 0.9,
    caisses: ["rci_complementaire"],
    commentaire: "Assiette de cotisation plus faible que celle d'un salarié.",
  },
  {
    code: "exploitant_agricole",
    libelle: "Chef d'exploitation agricole",
    affiliation: "exploitant_agricole",
    age_debut: 20, age_liquidation: 64, niveau_salaire: 0.5,
    caisses: ["msa_exploitants"],
    commentaire: "Retraite majoritairement forfaitaire aujourd'hui : la part non "
      + "contributive disparaît intégralement dans les scénarios notionnels.",
  },
  {
    code: "profession_liberale",
    libelle: "Profession libérale",
    affiliation: "profession_liberale",
    age_debut: 27, age_liquidation: 66, niveau_salaire: 2.5,
    profil_carriere: "fortement_ascendant",
    caisses: ["cnavpl"],
    ecart_liquidation: 2,
    commentaire: "Régime de base CNAVPL et complémentaire Cipav, la section par "
      + "défaut. Un libéral d'une section spécialisée — auxiliaires médicaux, "
      + "pharmaciens, notaires — aurait un complémentaire différent, et celui-là "
      + "n'est pas paramétré. Seul cas type à partir APRÈS l'âge d'ouverture : "
      + "deux ans, l'écart que la grille lui donnait déjà quand les âges étaient "
      + "écrits.",
  },
  {
    code: "contractuel_public",
    libelle: "Agent contractuel de la fonction publique",
    affiliation: "contractuel_public",
    age_debut: 24, age_liquidation: 64, niveau_salaire: 0.85,
    caisses: ["ircantec"],
    commentaire: "Régime général + Ircantec.",
  },
].map((cas) => ({
  profil_carriere: "ascendant",
  sexe: "H",
  nombre_enfants: 0,
  part_primes: 0.0,
  interruptions_relatives: [],
  // Caisses de ``effectifs_retraites.csv`` dont ce cas type porte les retraités :
  // c'est par elles qu'il reçoit son POIDS dans les agrégats.
  caisses: [],
  // Ce qui DATE le départ, quand ce n'est pas un nombre. `taux_plein` : le
  // premier âge auquel la pension est servie entière — l'âge d'ouverture si la
  // durée requise y est atteinte, l'âge auquel elle l'est sinon, et pas au-delà
  // de l'âge d'annulation de la décote. `ouverture` : l'âge auquel le droit
  // ouvre la liquidation, sans égard à la durée, pour les carrières dont un
  // STATUT commande le départ. `services` : l'âge d'entrée augmenté de
  // `ecart_liquidation` années de services, pour la pension militaire, qui ne
  // s'ouvre pas à un âge mais à une durée.
  regle_liquidation: "taux_plein",
  ecart_liquidation: 0.0,
  ...cas,
}));

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
 * Générations couvertes par défaut : de la première génération entièrement
 * couverte par la Sécurité sociale aux actifs entrés récemment.
 */
export const GENERATIONS = [1940, 1950, 1960, 1970, 1980, 1990, 2000];

/**
 * Poids de chaque cas type une année donnée, tirés des effectifs de caisse.
 *
 * La grille des cas types n'est pas un échantillon : elle couvre les
 * configurations du système, pas sa population. Rien ne s'oppose à ce qu'on
 * l'utilise pour un AGRÉGAT, à condition de rendre à chaque configuration son
 * poids réel — et c'est ce que les effectifs de la DREES donnent.
 *
 * Chaque cas type reçoit l'effectif de ses caisses ; une caisse réclamée par
 * plusieurs cas types se partage ÉGALEMENT entre eux — la Cnav est la caisse des
 * quatre carrières du privé, et rien ne dit combien de ses retraités ont été
 * cadres. C'est la seule part de convention égalitaire qui subsiste. Les poids
 * sont normalisés : seul leur rapport importe.
 */
export function poidsEffectifs(effectifs, annee, casTypes = CAS_TYPES) {
  const reclamants = new Map();
  for (const cas of casTypes) {
    for (const caisse of cas.caisses) {
      reclamants.set(caisse, (reclamants.get(caisse) || 0) + 1);
    }
  }
  const bruts = new Map();
  let total = 0;
  for (const cas of casTypes) {
    let poids = 0;
    for (const caisse of cas.caisses) {
      poids += effectifs.effectif(caisse, annee) / reclamants.get(caisse);
    }
    bruts.set(cas.code, poids);
    total += poids;
  }
  if (total <= 0) {
    throw new Error(`aucun effectif connu en ${annee} pour pondérer les cas types`);
  }
  const poids = {};
  for (const [code, brut] of bruts) poids[code] = brut / total;
  return poids;
}

/**
 * L'ANCIENNE convention, gardée comme variante et non comme repli : elle ne sert
 * plus à calculer les résultats affichés, mais à dire de combien elle les
 * déplaçait, ce qu'aucun argument ne remplace.
 */
export function poidsEgaux(casTypes = CAS_TYPES) {
  const poids = {};
  for (const cas of casTypes) poids[cas.code] = 1 / casTypes.length;
  return poids;
}

/** La carrière d'un cas type, liquidée à l'âge qu'on lui passe. */
function carriereCasType(cas, simulateur, generation, ageLiquidation) {
  const interruptions = new Map(
    cas.interruptions_relatives.map(([decalage, motif]) => [
      Math.trunc(generation + cas.age_debut + decalage), motif,
    ]),
  );
  return simulateur.carriereSimple({
    annee_naissance: generation,
    sexe: cas.sexe,
    affiliation: cas.affiliation,
    age_debut: cas.age_debut,
    age_liquidation: ageLiquidation,
    niveau_salaire: cas.niveau_salaire,
    profil_carriere: cas.profil_carriere,
    interruptions,
    nombre_enfants: cas.nombre_enfants,
    part_primes: cas.part_primes,
    identifiant: `${cas.libelle} (génération ${generation})`,
  });
}

/** Ce que la règle de ce cas type oppose à cette carrière, décalé. */
function ageProposeCasType(cas, simulateur, generation, age) {
  const actuel = simulateur.scenarioActuel;
  const carriere = carriereCasType(cas, simulateur, generation, age);
  const reference = cas.regle_liquidation === "taux_plein"
    ? actuel.ageTauxPleinDroit(carriere)
    : actuel.ageOuvertureDroit(carriere);
  return reference === null ? null : reference + cas.ecart_liquidation;
}

/**
 * L'âge auquel ce cas type liquide, étant né en `generation`.
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
export function ageLiquidationPour(cas, simulateur, generation, variante = "droit") {
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
    const propose = ageProposeCasType(cas, simulateur, generation, age);
    if (propose === null || Math.abs(propose - age) < 1e-9) {
      break;
    }
    if (propose > age) {
      age = propose;
      continue;
    }
    const confirme = ageProposeCasType(cas, simulateur, generation, propose);
    if (confirme === null || confirme > propose + 1e-9) {
      break;
    }
    age = propose;
  }
  return age;
}

/** Construit la carrière d'un cas type pour une génération donnée. */
export function construireCasType(cas, simulateur, generation, variante = "droit") {
  return carriereCasType(
    cas, simulateur, generation,
    ageLiquidationPour(cas, simulateur, generation, variante),
  );
}

/**
 * Calcule la grille complète cas type × génération.
 *
 * Les combinaisons impossibles — un régime qui n'existait pas encore, une
 * liquidation avant l'origine de la répartition — sont écartées avec leur motif
 * plutôt que de faire échouer l'ensemble.
 *
 * `liquidation` choisit à quel âge chaque cas type part : `droit`, celui que le
 * droit de sa génération lui ouvre, ou `absolu`, l'âge écrit dans la grille. Le
 * second n'existe que pour mesurer ce que le premier a déplacé.
 */
export function calculerCasTypes(simulateur, casTypes = CAS_TYPES,
                                 generations = GENERATIONS, liquidation = "droit") {
  if (!VARIANTES_LIQUIDATION.includes(liquidation)) {
    throw new Error(
      `variante de liquidation inconnue : ${liquidation} `
      + `(attendu : ${VARIANTES_LIQUIDATION.join(", ")})`,
    );
  }
  const resultats = new Map();
  const echecs = new Map();
  for (const cas of casTypes) {
    for (const generation of generations) {
      const cle = `${cas.code}|${generation}`;
      try {
        const carriere = construireCasType(cas, simulateur, generation, liquidation);
        if (carriere.anneeLiquidation <= simulateur.parametres.annee_debut_repartition) {
          echecs.set(cle, "liquidation antérieure à la répartition");
          continue;
        }
        const regimesConnus = carriere.lignes.some(
          (ligne) => simulateur.affiliations.regimes(cas.affiliation, ligne.annee).length > 0,
        );
        if (!regimesConnus) {
          echecs.set(cle, "aucun régime actif sur la période");
          continue;
        }
        resultats.set(cle, simulateur.simuler(carriere));
      } catch (erreur) {
        echecs.set(cle, erreur.message);
      }
    }
  }
  return { resultats, echecs };
}
