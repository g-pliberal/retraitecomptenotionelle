/**
 * Paramètres de configuration du modèle.
 *
 * Portage de ``src/retraite_notionnelle/config.py``. Toutes les décisions de
 * modélisation contestables sont réunies ici, en un seul endroit, pour qu'on
 * puisse les faire varier sans toucher au moteur. Les valeurs par défaut suivent
 * le cahier des charges à une exception près : l'indexation, où le défaut est la
 * croissance de la masse salariale — le taux d'équilibre de la répartition — et
 * non le « triple lock inversé » demandé, qui reste à un paramètre de distance.
 * Pour le reste : âge de référence à cliquet, neutralisation intégrale des
 * droits non contributifs, fusion des régimes au cas le plus défavorable.
 */

/** Règle de revalorisation des comptes et des pensions. */
export const ModeIndexation = Object.freeze({
  //: min(inflation, croissance du salaire moyen nominal, productivité réelle).
  //: C'est la règle demandée, littéralement. Elle mêle un taux réel à deux taux
  //: nominaux : en période de forte inflation, le minimum est presque toujours
  //: la productivité réelle, ce qui écrase la valeur réelle des comptes.
  TRIPLE_LOCK_INVERSE: "triple_lock_inverse",
  //: Variante homogène : les trois termes sont ramenés en nominal.
  TRIPLE_LOCK_INVERSE_NOMINAL: "triple_lock_inverse_nominal",
  //: Médiane des trois mêmes termes au lieu de leur minimum : le taux retenu
  //: reste l'un des trois, mais celui du milieu. Moins sévère que la règle
  //: littérale, et robuste à une série aberrante.
  MEDIANE_TROIS_TAUX: "mediane_trois_taux",
  //: Moyenne arithmétique des trois mêmes termes : poids égal à chacun, y
  //: compris au plus haut. Ce n'est plus une règle d'austérité, et le taux
  //: obtenu n'est celui d'aucun agrégat observé.
  MOYENNE_TROIS_TAUX: "moyenne_trois_taux",
  //: Croissance de la MASSE SALARIALE — l'assiette des cotisations, et le taux
  //: de rendement interne d'un système en répartition (Samuelson, Aaron) : le
  //: seul qui laisse le système en équilibre sans toucher au taux de
  //: cotisation. Salaire moyen + emploi salarié : nettement plus généreux que
  //: toutes les autres règles, l'emploi salarié ayant doublé depuis 1950.
  MASSE_SALARIALE: "masse_salariale",
  //: Croissance du PIB nominal. Assiette plus large que la masse salariale.
  //: L'Italie la LISSE sur cinq ans, et le lissage n'est pas un mode mais le
  //: paramètre `lissage_indexation`, applicable à n'importe quelle règle : la
  //: règle italienne s'écrit `pib_nominal` + lissage 5.
  PIB_NOMINAL: "pib_nominal",
  //: Revalorisation RÉELLEMENT PRATIQUÉE par le régime général : les
  //: coefficients des arrêtés annuels, ceux-là mêmes que le scénario 1
  //: applique aux salaires portés au compte. C'est ce mode, et non ``PRIX``,
  //: qui neutralise l'indexation quand on veut isoler l'effet propre des
  //: comptes notionnels.
  REVALORISATION_PORTEE_AU_COMPTE: "revalorisation_portee_au_compte",
  //: Indexation sur les seuls prix — la règle du régime général DEPUIS 1987
  //: seulement : avant, les arrêtés suivaient les salaires.
  PRIX: "prix",
  //: Indexation sur le salaire moyen (règle antérieure à 1987).
  SALAIRES: "salaires",
});

/**
 * Quelle part de la cotisation retraite alimente le compte notionnel.
 *
 * `salariale` (défaut, scénarios 2 et 3) : seule la part que l'assuré supporte
 * lui-même — pour un non-salarié, toute sa cotisation. `totale` (scénarios 4
 * et 5) : salariale et patronale, la part patronale du public étant celle qui
 * a été réellement versée. `totale_alignee` : salariale et patronale, mais la
 * part patronale du public est empruntée au statut pivot privé — l'ancienne
 * convention, conservée comme contrefactuel.
 */
export const PartCotisation = Object.freeze({
  SALARIALE: "salariale",
  TOTALE: "totale",
  TOTALE_ALIGNEE: "totale_alignee",
});

/**
 * Origine du flux qui alimente le compte notionnel.
 *
 * `taux_uniforme` est un taux d'ACQUISITION COMMUN : un seul taux pour tout le
 * monde, prélevé une fois sur la rémunération. Ce qui est prélevé au-delà
 * finance les engagements du passé et n'ouvre aucun droit. Les scénarios 2 à 5
 * ne l'emploient pas.
 *
 * `taux_historiques_puis_uniforme` est le flux du scénario 6 : les taux
 * historiques JUSQU'À la bascule — ce qui a été cotisé sous le système actuel
 * est porté au compte tel qu'il a été prélevé, comme dans le scénario 4 — et
 * le taux uniforme (18 %) À COMPTER d'elle.
 */
export const SourceCotisations = Object.freeze({
  TAUX_HISTORIQUES: "taux_historiques",
  TAUX_UNIFORME: "taux_uniforme",
  TAUX_HISTORIQUES_PUIS_UNIFORME: "taux_historiques_puis_uniforme",
});

/** Construction de l'âge auquel une liquidation est réputée « à l'heure ». */
export const ModeAgeReference = Object.freeze({
  //: Cliquet sur l'âge du taux plein du régime général : l'âge de référence ne
  //: redescend jamais.
  CLIQUET_LEGAL: "cliquet_legal",
  //: Cliquet légal jusqu'à la bascule, puis indexation sur l'espérance de vie.
  CLIQUET_PUIS_ESPERANCE_VIE: "cliquet_puis_esperance_vie",
  //: Âge du taux plein de l'année de liquidation, sans cliquet — contrefactuel.
  LEGAL_SANS_CLIQUET: "legal_sans_cliquet",
  //: Cliquet légal jusqu'à la bascule, puis un âge fixe — 64 ans, l'âge légal
  //: d'ouverture des droits. C'est le défaut.
  FIXE_APRES_BASCULE: "fixe_apres_bascule",
});

/**
 * Âge auquel les droits figés à la bascule sont convertis en capital.
 *
 * ``REFERENCE`` valorise au diviseur de l'âge de référence : un assuré qui
 * liquide avant cet âge subit, sur ses droits déjà ouverts, un abattement égal
 * au rapport des deux diviseurs. ``LIQUIDATION`` valorise au diviseur de l'âge
 * effectif de départ, ce qui rend la conversion neutre.
 */
export const AgeConversionDroitsAcquis = Object.freeze({
  REFERENCE: "reference",
  LIQUIDATION: "liquidation",
});

/** Table de mortalité servant au coefficient de conversion. */
/**
 * La valeur de `population_conversion` qui rattache chaque carrière au vingtile
 * de niveau de vie où son salaire la place.
 */
export const POPULATION_PAR_NIVEAU_DE_VIE = "niveau_de_vie";

export const TableConversion = Object.freeze({
  UNISEXE: "unisexe",
  PAR_SEXE: "par_sexe",
});

/**
 * Situation de foyer retenue pour la garantie vieillesse du scénario 6. La
 * garantie est INDIVIDUALISÉE : chacun est comparé à son propre plancher, et
 * les revenus du conjoint n'entrent jamais dans le calcul. La situation ne
 * change qu'une chose — l'allocation d'isolement d'une personne vivant seule.
 */
/**
 * Ce que deviennent, à la bascule, les pensions DÉJÀ SERVIES : `prix`, elles
 * gardent l'indice des prix que le droit leur promet, et seuls les comptes
 * ouverts sous le nouveau régime suivent sa règle ; `reindexe`, la réforme
 * fait passer tout le stock à la règle du compte le jour de la bascule. Page
 * Coût seulement, systèmes 2 à 6 seulement.
 */
export const RevalorisationStock = Object.freeze({
  PRIX: "prix",
  REINDEXE: "reindexe",
});

export const SituationFoyer = Object.freeze({
  SEUL: "seul",
  COUPLE: "couple",
});

/**
 * Droits retirés du calcul, conformément au principe « seules les cotisations
 * comptent ». Chaque drapeau à ``true`` signifie : ce droit est SUPPRIMÉ dans
 * les scénarios notionnels. Le scénario « système actuel » les conserve tous.
 */
export const NEUTRALISATIONS_DEFAUT = Object.freeze({
  minimum_contributif: true,
  minimum_garanti: true,
  minimum_vieillesse_aspa: true,
  pension_majoree_reference: true,
  majoration_enfants: true,
  majoration_duree_assurance: true,
  assurance_vieillesse_parents_au_foyer: true,
  reversion: true,
  bonifications: true,
  categorie_active: true,
  periodes_assimilees: true,
  garantie_minimale_points: true,
  carriere_longue: true,
  decote_surcote: true,
  coefficient_solidarite: true,
});

/** Jeu complet de paramètres d'une simulation. */
export const PARAMETRES_DEFAUT = Object.freeze({
  // --- Bornes temporelles ---------------------------------------------------
  //: Année d'origine du système par répartition. 1941 = allocation aux vieux
  //: travailleurs salariés, premier mécanisme financé par les cotisations.
  annee_debut_repartition: 1941,
  //: Les droits acquis jusqu'à cette année incluse suivent les règles
  //: actuelles, les droits postérieurs le compte notionnel du régime fusionné.
  annee_bascule: 2026,
  annee_courante: 2026,
  //: Année dans les euros de laquelle les résultats sont exprimés.
  annee_euros_constants: 2026,
  //: Scénario de projection macroéconomique au-delà de la dernière observation.
  scenario_projection: "cor_reference",
  //: Trajectoire de l'emploi au-delà de la dernière observation. Elle ne
  //: compose que la masse salariale et le PIB projetés, donc l'indexation des
  //: comptes notionnels : les systèmes 2 à 6 la lisent, pas le système 1.
  trajectoire_emploi: "cor_2026",
  //: Les pensions déjà servies à la bascule : sur les prix, comme le droit le
  //: leur promet, ou réindexées sur la règle du compte.
  revalorisation_stock: RevalorisationStock.PRIX,

  // --- Indexation -----------------------------------------------------------
  //: Le défaut est la règle d'ÉQUILIBRE, pas le triple lock inversé qui a donné
  //: son cahier des charges au modèle : un défaut doit être ce qu'on retient
  //: faute d'instruction contraire, pas ce qu'on veut démontrer.
  mode_indexation: ModeIndexation.MASSE_SALARIALE,
  //: Fenêtre de la moyenne glissante appliquée au taux d'indexation, en années.
  //: 1 = aucun lissage. Orthogonal à la règle : ce qu'il vise est la loterie de
  //: cohorte, pas le niveau. La règle italienne, c'est PIB nominal + 5.
  lissage_indexation: 1,
  //: ``null`` = aucun plancher : le triple lock inversé peut être négatif, ce
  //: qui est sa conséquence logique et non un défaut.
  plancher_indexation: null,
  // Il n'y a pas de paramètre « indexer les pensions liquidées » : le moteur
  // ne calcule qu'une pension AU MOMENT DE LA LIQUIDATION, et il n'existe
  // aucune phase postérieure à revaloriser.

  // --- Cotisations ----------------------------------------------------------
  source_cotisations: SourceCotisations.TAUX_HISTORIQUES,
  taux_cotisation_uniforme: 0.2531,
  // Il n'y a pas non plus de paramètre « le taux d'appel ouvre-t-il des
  // droits » : le compte porte ce qui a été PRÉLEVÉ, taux d'appel compris.
  //: Part de la cotisation portée au compte : celle de l'assuré seul, ou celle
  //: de l'assuré et de son employeur.
  part_cotisation: PartCotisation.SALARIALE,
  statut_pivot_cotisations: "salarie_prive_non_cadre",
  //: Plafonnement de l'assiette notionnelle, en multiples du plafond annuel de
  //: la Sécurité sociale. ``null`` = assiette déplafonnée.
  plafond_assiette_en_pass: 8.0,

  // --- Âge de référence -----------------------------------------------------
  mode_age_reference: ModeAgeReference.FIXE_APRES_BASCULE,
  //: Âge de référence servi à partir de la bascule en mode FIXE_APRES_BASCULE.
  age_reference_fixe: 64,
  ratio_cible_retraite_carriere: 0.5,

  // --- Conversion en rente --------------------------------------------------
  table_conversion: TableConversion.UNISEXE,
  //: Population dont la mortalité entre dans le diviseur. C'EST L'INTERRUPTEUR :
  //: `POPULATION_PAR_NIVEAU_DE_VIE` (le défaut) rattache chaque carrière au
  //: vingtile de niveau de vie où son salaire la place ; `null` est la table
  //: commune, la même pour tout le monde, et désactive la mesure ; une clé de
  //: `paquet.populations` vaut pour toutes les carrières, pour mesurer.
  population_conversion: "niveau_de_vie",
  //: Taux de préfinancement incorporé au diviseur. 0 : le diviseur est
  //: l'espérance de vie résiduelle actualisée au même taux que l'indexation,
  //: les deux se compensant exactement.
  taux_anticipe_conversion: 0.0,
  //: Âge de conversion des droits figés à la bascule, dans le scénario
  //: prospectif. ``reference`` fait payer l'anticipation une seconde fois sur
  //: des droits déjà ouverts ; ``liquidation`` rend la conversion neutre.
  age_conversion_droits_acquis: AgeConversionDroitsAcquis.REFERENCE,
  //: Table de génération plutôt que table du moment.
  table_generation: true,
  // L'âge terminal des tables est une constante du module de mortalité
  // (AGE_TERMINAL), pas un paramètre de simulation.

  // --- Fusion des régimes ---------------------------------------------------
  fusion_au_plus_defavorable: true,

  // --- Scénario « système actuel » ------------------------------------------
  //: Le minimum vieillesse (ASPA) fait-il partie de l'étalon ? C'est le dernier
  //: plancher du système actuel et le seul qui ne suppose aucune cotisation :
  //: l'omettre sous-estime le système en vigueur là même où l'écart avec un
  //: compte notionnel est le plus grand. Mais ce n'est pas une pension — âge de
  //: 65 ans, ressources DU FOYER, demande à faire, non-recours de moitié,
  //: récupération sur succession. Servie par défaut sous le barème d'une
  //: personne seule sans autre ressource, et toujours comme une ligne SÉPARÉE
  //: de la cascade.
  minimum_vieillesse_dans_le_scenario_actuel: true,

  // --- Scénario 6 : la proposition libérale ----------------------------------
  //: Le scénario 6 est le scénario 4 — compte rétroactif, cotisation entière,
  //: mêmes âges, même indexation — à deux différences près : à compter de la
  //: bascule, un TAUX UNIQUE, salariale et patronale additionnées, le même
  //: pour tous, prélevé une fois sur la rémunération (avant elle, les taux
  //: réels du scénario 4) ; et une GARANTIE VIEILLESSE qui remplace l'ASPA,
  //: différentielle, individualisée, financée par l'impôt, ouverte à 65 ans.
  taux_cotisation_liberal: 0.18,
  //: Partage du taux unique entre l'assuré et son employeur. La proposition
  //: dit « 18 %, salariale et patronale additionnées » et ne dit pas qui porte
  //: quoi ; le dépôt partage MOITIÉ-MOITIÉ. Ce paramètre ne touche à AUCUNE
  //: pension — le compte porte la somme des deux parts — mais il compte dans
  //: la fiche de paie : la CSG est assise sur le BRUT, que le partage déplace,
  //: et la réduction générale n'efface que des cotisations PATRONALES.
  part_salariale_taux_unique: 0.5,
  //: Montants MENSUELS, en euros de `annee_euros_garantie_vieillesse`, ramenés
  //: à l'année de liquidation par l'indice des prix. 800 + 250 = 1 050 € seul,
  //: 800 € par personne à deux.
  garantie_vieillesse_mensuelle: 800.0,
  allocation_isolement_mensuelle: 250.0,
  // Part des ayants droit qui réclament la garantie : l'hypothèse de l'ASPA,
  // un sur deux. Ne joue que sur le coût lu sur la distribution.
  taux_recours_garantie: 0.5,
  // Part de l'avance d'un bénéficiaire que sa succession couvre : une
  // hypothèse, la moitié, faute de distribution de patrimoine.
  part_reprise_garantie: 0.5,
  annee_euros_garantie_vieillesse: 2026,
  //: Seul ou à deux : ne joue que sur l'allocation d'isolement. Le défaut est
  //: la personne seule, comme pour l'ASPA du scénario 1.
  situation_foyer: SituationFoyer.SEUL,

  // --- Pilier de capitalisation obligatoire (proposition) --------------------
  //: La troisième pièce de la proposition : une cotisation OBLIGATOIRE, placée
  //: et non mutualisée, qui S'AJOUTE au compte notionnel au lieu de s'y
  //: substituer. Elle ne change rien à ce que la répartition sert — le compte
  //: notionnel est calculé sans elle et affiché sans elle —, d'où le
  //: compartiment distinct de `capitalisation.js`. La mettre à `false` retire
  //: le pilier sans toucher au reste.
  capitalisation_obligatoire: true,
  //: Prélevé sur la MÊME assiette que la cotisation notionnelle de l'année, EN
  //: PLUS d'elle : l'effort monte de cinq points à compter de la bascule.
  taux_capitalisation_obligatoire: 0.05,
  //: Première année de cotisation au pilier. Les années antérieures gardent
  //: leurs taux et ne versent rien : qui a liquidé avant n'a pas de pilier.
  annee_debut_capitalisation: 2026,
  //: Les trois frais du PER, mesurés par l'Observatoire des produits d'épargne
  //: financière pour 2025 sur le support en euros — le seul qui corresponde à
  //: un placement sans risque. Ce sont les frais d'un produit vendu à des
  //: volontaires : une borne haute, assumée comme telle.
  frais_versement_capitalisation: 0.0109,
  frais_gestion_capitalisation: 0.0076,
  frais_arrerages_capitalisation: 0.0220,
  // --- Capitalisation volontaire : les cinq points rendus ---------------------
  //: Le quatrième terme, et le seul que personne n'impose. Le système actuel
  //: prélève près de 28 % du salaire ; la proposition en prélève 23. Elle rend
  //: donc CINQ POINTS, et le modèle suppose qu'ils sont remis au même compte :
  //: l'effort revient à ce qu'il est aujourd'hui, et les deux systèmes se
  //: comparent à prix égal. Sur la fiche de paie, cette cotisation est
  //: entièrement à la charge de l'assuré, puisque personne ne la lui impose.
  capitalisation_volontaire: true,
  taux_capitalisation_volontaire: 0.05,
  //: Taux technique de la rente, nul par défaut comme dans la plupart des PER :
  //: le diviseur de la rente est alors EXACTEMENT celui de la pension
  //: notionnelle, et les deux compartiments deviennent comparables au centime.
  taux_technique_rente_capitalisation: 0.0,

  // --- Neutralisations ------------------------------------------------------
  neutralisations: NEUTRALISATIONS_DEFAUT,

  // --- Compartiments hors répartition ---------------------------------------
  isoler_capitalisation: true,

  // --- Contrôle qualité des données -----------------------------------------
  fiabilite_minimale: "estimee",
});

/** Copie modifiée : les paramètres sont traités comme immuables. */
/** Les cinq points volontaires, ou zéro quand on les a retirés. */
export function tauxCapitalisationVolontaireApplique(parametres) {
  return parametres.capitalisation_volontaire
    ? parametres.taux_capitalisation_volontaire : 0.0;
}

/**
 * Ce que le pilier capitalisé encaisse en tout, obligatoire et volontaire.
 *
 * Un seul taux en sort : le placement, les frais et la rente ne distinguent pas
 * les deux origines. Ce qui les distingue est sur la fiche de paie, où l'une est
 * partagée avec l'employeur et l'autre pas.
 */
export function tauxCapitalisationApplique(parametres) {
  const obligatoire = parametres.capitalisation_obligatoire
    ? parametres.taux_capitalisation_obligatoire : 0.0;
  return obligatoire + tauxCapitalisationVolontaireApplique(parametres);
}

/** Tout ce que la proposition prélève sur la rémunération, en un taux. */
export function tauxRetraitePropose(parametres) {
  return parametres.taux_cotisation_liberal
    + tauxCapitalisationApplique(parametres);
}

export function avec(parametres, modifications) {
  return Object.freeze({ ...parametres, ...modifications });
}

/** Clé stable d'un jeu de paramètres, pour mémoriser un simulateur par jeu. */
export function cleParametres(parametres) {
  return JSON.stringify(parametres, Object.keys(parametres).sort());
}
