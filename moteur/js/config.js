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
 * Ce que le compte d'un agent de l'État reçoit de son employeur, sous
 * `totale`.
 *
 * `entiere` (défaut) : le taux que l'État a versé au compte d'affectation
 * spéciale « Pensions », 78,28 % du traitement en 2025 pour un civil.
 * `retraite_seule` : la part de ce taux que la Cour des comptes rattache à la
 * retraite de l'agent lui-même — 44,1 % pour un civil et 51,2 % pour un
 * militaire en 2025, la même proportion du taux de l'année ailleurs.
 */
export const ContributionEtat = Object.freeze({
  ENTIERE: "entiere",
  RETRAITE_SEULE: "retraite_seule",
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
  //: Cliquet légal jusqu'à la bascule, puis un âge fixe — 65 ans, l'âge légal
  //: de départ de la proposition (`age_legal_liberal`). C'est le défaut.
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

/** Comment une carrière est rattachée à son vingtile : par son salaire ou par sa pension. */
export const RATTACHEMENT_SALAIRE = "salaire";
export const RATTACHEMENT_PENSION = "pension";

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
  //: La première année du régime fusionné : les droits acquis jusqu'à l'année
  //: qui la précède suivent les règles actuelles, ceux de l'année de bascule
  //: et des suivantes le compte notionnel. C'est aussi la première année de
  //: cotisation au pilier capitalisé : voir config.py.
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
  taux_cotisation_uniforme: 0.2574,
  // Il n'y a pas non plus de paramètre « le taux d'appel ouvre-t-il des
  // droits » : le compte porte ce qui a été PRÉLEVÉ, taux d'appel compris.
  //: Part de la cotisation portée au compte : celle de l'assuré seul, ou celle
  //: de l'assuré et de son employeur.
  part_cotisation: PartCotisation.SALARIALE,
  contribution_etat: ContributionEtat.ENTIERE,
  statut_pivot_cotisations: "salarie_prive_non_cadre",
  //: Plafonnement de l'assiette notionnelle, en multiples du plafond annuel de
  //: la Sécurité sociale. ``null`` = assiette déplafonnée, et c'est le défaut :
  //: le régime fusionné est déclaré déplafonné, et le site promet « au premier
  //: euro, sans plafond ». Les bornes des fiches, elles, continuent de rogner
  //: avant la bascule — c'est le droit. Voir `config.py`.
  plafond_assiette_en_pass: null,

  // --- Âge de référence -----------------------------------------------------
  mode_age_reference: ModeAgeReference.FIXE_APRES_BASCULE,
  //: Âge de référence servi à partir de la bascule en mode FIXE_APRES_BASCULE.
  //: 65 ans depuis le 22 septembre 2026, l'âge légal de la proposition ; 64,
  //: celui de la loi du 14 avril 2023, du 19 au 22. Il ne pèse que sur la
  //: conversion des droits acquis des scénarios prospectifs 3 et 5.
  age_reference_fixe: 65,
  ratio_cible_retraite_carriere: 0.5,

  // --- Conversion en rente --------------------------------------------------
  table_conversion: TableConversion.UNISEXE,
  //: Population dont la mortalité entre dans le diviseur. C'EST L'INTERRUPTEUR :
  //: `POPULATION_PAR_NIVEAU_DE_VIE` (le défaut) rattache chaque carrière au
  //: vingtile de niveau de vie où son salaire la place ; `null` est la table
  //: commune, la même pour tout le monde, et désactive la mesure ; une clé de
  //: `paquet.populations` vaut pour toutes les carrières, pour mesurer.
  population_conversion: "niveau_de_vie",
  //: Par quoi la carrière est rattachée à son vingtile : `salaire` (son
  //: salaire rapporté au salaire moyen) ou `pension` (sa pension nette,
  //: ramenée aux euros de l'année des vingtiles, résolue par point fixe).
  rattachement_niveau_de_vie: RATTACHEMENT_SALAIRE,
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
  //: même indexation — à trois différences près : à compter de la bascule, un
  //: TAUX UNIQUE, salariale et patronale additionnées, le même pour tous,
  //: prélevé une fois sur la rémunération (avant elle, les taux réels du
  //: scénario 4) ; une GARANTIE VIEILLESSE qui remplace l'ASPA,
  //: différentielle, individualisée, financée par l'impôt, ouverte à 65 ans ;
  //: et un ÂGE LÉGAL DE DÉPART de 65 ans (`age_legal_liberal`, plus bas).
  taux_cotisation_liberal: 0.18,
  //: Partage du taux unique entre l'assuré et son employeur. La proposition
  //: dit « 18 %, salariale et patronale additionnées » et ne dit pas qui porte
  //: quoi ; le programme a tranché le 20 septembre 2026 : la part PATRONALE ne
  //: bouge pas — 16,67 points, ce qu'elle vaut aujourd'hui — et toute la
  //: baisse va au salarié, dont la part tombe de 11,31 à 6,33 points sur 23.
  //: D'où `0.0633 / 0.23`, écrit ainsi pour qu'on lise d'où il vient. Ce
  //: paramètre ne touche à AUCUNE pension — le compte porte la somme des deux
  //: parts — mais il compte dans la fiche de paie : la CSG est assise sur le
  //: BRUT, que le partage déplace, et la réduction générale n'efface que des
  //: cotisations PATRONALES.
  part_salariale_taux_unique: 0.0633 / 0.23,
  //: Ce que la proposition REND aux salaires sur ce qu'elle cesse d'affecter à
  //: la retraite. Décision du Parti libéral, 20 septembre 2026 : la moitié est
  //: rendue aux salaires, la moitié éteint de la dette. Elle s'applique deux
  //: fois — aux impôts et taxes affectés, dont ce qui est assis sur une
  //: rémunération est supprimé et le solde rendu en points de CSG d'activité
  //: (`restitution.js`) ; et à la contribution d'équilibre d'un employeur
  //: public, dont la moitié remonte dans le traitement (`Incidence.PARTAGEE`).
  //: Zéro rend l'ancienne convention, où rien n'était rendu.
  part_rendue_aux_salaires: 0.5,
  //: Un TAUX UNIQUE DE TVA qui remplacerait, à compter de la bascule, les
  //: quatre taux d'aujourd'hui, ce qu'il rapporte de plus allant au scénario
  //: 6. ZÉRO, le défaut depuis le 24 septembre 2026 : la proposition ne réforme
  //: pas la TVA, les quatre taux restent et rien de la TVA ne va aux
  //: retraites. Un taux positif garde le mécanisme, comme variante. Zéro veut
  //: dire « la TVA n'est pas réformée », et non « une TVA à zéro ». Voir
  //: `config.py`.
  taux_tva_liberal: 0.0,
  //: Montants MENSUELS, en euros de `annee_euros_garantie_vieillesse`, ramenés
  //: à l'année de liquidation par l'indice des prix. 800 + 250 = 1 050 € seul,
  //: 800 € par personne à deux.
  garantie_vieillesse_mensuelle: 800.0,
  allocation_isolement_mensuelle: 250.0,
  //: La troisième : un ÂGE LÉGAL DE DÉPART DE 65 ANS à compter de la bascule
  //: (22 septembre 2026). Qui serait parti plus tôt sous le droit en vigueur
  //: part à cet âge sous la proposition, et travaille jusque-là dans la
  //: situation de sa dernière année (`Carriere.prolongee`) : des cotisations
  //: de plus, un diviseur plus petit, donc une pension mensuelle plus forte,
  //: servie moins longtemps. Qui partait à 65 ans ou après n'y gagne rien, qui
  //: a liquidé avant la bascule n'est pas touché. Seul le scénario 6 le porte ;
  //: `null` retire la mesure. Voir `config.py`.
  age_legal_liberal: 65.0,
  //: La PART DES REPORTÉS EN EMPLOI : de ceux que l'âge légal fait attendre,
  //: combien travaillent jusqu'à lui. Elle ne joue que sur la page Coût, où
  //: chaque cohorte reportée mêle ceux qui travaillent et cotisent jusqu'à
  //: l'âge légal et ceux qui l'attendent sans activité. Un par défaut : tous
  //: travaillent, un plafond. Voir `config.py`.
  part_reportes_en_emploi: 1.0,
  // Part des ayants droit qui réclament la garantie : l'hypothèse de l'ASPA,
  // un sur deux. Ne joue que sur le coût lu sur la distribution.
  taux_recours_garantie: 0.5,
  // Rapport des deux facteurs de déplacement, r = fF / fH : le scénario 6
  // retire les droits non cotisés, que les femmes détiennent plus souvent.
  // null fait LIRE ce rapport sur l'enquête, où il vaut 0,834 en 2020 ; 1.0
  // restitue l'ancienne convention, un facteur unique pour tous.
  rapport_deplacement_sexe: null,
  // Part de l'avance d'un bénéficiaire que sa succession couvre : null la
  // fait calculer sur le patrimoine des ménages retraités selon leur revenu.
  part_reprise_garantie: null,
  // Les trois règles de la reprise (action 47), qui ne jouent que sur la
  // couverture calculée : voir `Parametres` dans `config.py` pour les sources
  // et les hypothèses, et `recouvrement` dans `cout.js`.
  // 1. Le logement attend le décès du conjoint survivant qui l'occupe.
  reprise_report_logement: true,
  part_logement_proprietaires: 0.75,
  patrimoine_minimal_proprietaire: 80000.0,
  ecart_age_couple: 2.6,
  // 2. Les donations de la fenêtre (dix ans avant l'ouverture, et après) sont
  // réintégrées.
  reprise_donations: true,
  part_donateurs_modestes: 0.07,
  part_donateurs_retraites: 0.158,
  donation_moyenne_modestes: 60000.0,
  donation_moyenne_retraites: 100000.0,
  part_donations_fenetre: 0.85,
  part_donations_connues: 0.8,
  // 3. L'assurance-vie est hors succession ; la règle en reprend les primes
  // versées dans la même fenêtre.
  reprise_assurance_vie: true,
  part_assurance_vie_patrimoine: 0.10,
  part_assurance_vie_reprise: 0.6,
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
  //: Les frais du PER l'année de la bascule, aux vraies moyennes du marché de
  //: 2025 (OPEF, support en euros) : sur versement et sur encours, les
  //: moyennes pondérées ; sur arrérages, la moyenne sur TOUS les déclarants
  //: (0,99 %) et non celle des seuls facturants (2,20 %) ; et le frais annuel
  //: sur la réserve de la rente, que l'OPEF ne mesure pas et que le CCSF
  //: relevait sur 22 contrats sur 34 (0,60 à 1 % par an) : 0,52 % estimés.
  //: Sources, distributions et raisons : config.py et le fichier de frais.
  frais_versement_capitalisation: 0.0109,
  frais_gestion_capitalisation: 0.0076,
  frais_arrerages_capitalisation: 0.0099,
  frais_encours_rente_capitalisation: 0.0052,
  //: Les frais BAISSENT par paliers `[année, taux]` — le taux vaut de cette
  //: année au palier suivant, le niveau ci-dessus avant le premier —, comme
  //: partout où une épargne retraite obligatoire a mis les gérants sous
  //: plafond ou en concurrence (Royaume-Uni, Chili, Suède, États-Unis ; voir
  //: config.py). Un tableau vide fige le poste.
  frais_versement_paliers: [[2031, 0.0055], [2036, 0.0019], [2046, 0.0]],
  frais_gestion_paliers: [[2036, 0.0054], [2046, 0.0039], [2056, 0.0028], [2066, 0.0020]],
  frais_arrerages_paliers: [[2036, 0.0050], [2046, 0.0]],
  frais_encours_rente_paliers: [[2036, 0.0037], [2046, 0.0027], [2056, 0.0019], [2066, 0.0014]],
  //: Fraction de l'écart entre le tarif d'une cohorte placée et celui des
  //: nouveaux dépôts que le stock referme chaque année : la baisse porte
  //: surtout sur les nouveaux dépôts, un peu sur le stock.
  convergence_frais_stock: 0.10,
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
  //: Prime de terme retirée des forwards de la courbe sans risque, exprimée à
  //: trente ans et en rythme continu. ZÉRO par défaut, et c'est le réglage sous
  //: lequel le site publie : les versements futurs se placent aux forwards de
  //: la courbe du jour, hypothèse des anticipations pures. La relever retire
  //: cette hypothèse — le capital baisse — et fait travailler l'adossement à
  //: l'horizon, qui capte la prime une fois pour toutes là où un roulement la
  //: rachète à chaque échéance. Sous les anticipations pures, aucune allocation
  //: n'en vaut une autre : c'est l'arbitrage qui fixe le forward.
  prime_terme_trente_ans: 0.0,

  // --- Neutralisations ------------------------------------------------------
  neutralisations: NEUTRALISATIONS_DEFAUT,

  // --- Compartiments hors répartition ---------------------------------------
  isoler_capitalisation: true,

  // --- Contrôle qualité des données -----------------------------------------
  fiabilite_minimale: "estimee",
});

/** Copie modifiée : les paramètres sont traités comme immuables. */
/** Les cinq points volontaires, ou zéro quand on les a retirés. */
/**
 * Le taux en vigueur en `annee` : `niveau` avant le premier palier, puis le
 * taux du dernier palier atteint, les paliers étant lus dans l'ordre des années.
 */
/** Le frais sur arrérages du PER tel qu'il est vendu en 2025 : la moyenne
 * des seuls assureurs qui facturent, que le régime `detail` redit. */
export const FRAIS_ARRERAGES_VENDU = 0.0220;

/** Les régimes de frais du site, dans l'ordre du menu ; le premier est le défaut. */
export const REGIMES_FRAIS = Object.freeze(
  ["paliers", "plafond", "contrats", "figes", "detail", "aucun"],
);

/**
 * La prime de terme à trente ans sous les deux régimes qui la retirent : le
 * milieu et le haut de la fourchette que la littérature retient pour les
 * maturités longues quand la courbe est ascendante (0,3 à 1 point).
 */
export const PRIME_TERME_MILIEU = 0.005;
export const PRIME_TERME_HAUTE = 0.010;

/** Les régimes de taux du site, dans l'ordre du menu ; le premier est le défaut. */
export const REGIMES_TAUX = Object.freeze(["forwards", "prime", "prime_haute"]);

/**
 * Les mêmes paramètres, sous l'un des régimes de taux du site. Portage de
 * `Parametres.sous_regime_taux`. Il ne touche que `prime_terme_trente_ans`,
 * mais cette chose gouverne à elle seule ce que l'allocation des maturités
 * peut valoir : sous `forwards`, qui est le défaut et vaut zéro, aucune
 * allocation n'en vaut une autre.
 */
export function sousRegimeTaux(parametres, regime) {
  const regimes = {
    forwards: 0.0,
    prime: PRIME_TERME_MILIEU,
    prime_haute: PRIME_TERME_HAUTE,
  };
  if (!(regime in regimes)) {
    throw new Error(`régime de taux inconnu : ${regime} `
      + `(attendu : ${Object.keys(regimes)})`);
  }
  return { ...parametres, prime_terme_trente_ans: regimes[regime] };
}

/**
 * Les mêmes paramètres, sous l'un des régimes de frais du site. Portage de
 * `Parametres.sous_regime_frais`, qui dit ce que chacun fait.
 */
export function sousRegimeFrais(parametres, regime) {
  const figes = {
    frais_versement_paliers: [], frais_gestion_paliers: [],
    frais_arrerages_paliers: [], frais_encours_rente_paliers: [],
  };
  const regimes = {
    paliers: {},
    plafond: { convergence_frais_stock: 1.0 },
    contrats: { convergence_frais_stock: 0.0 },
    figes,
    detail: {
      frais_arrerages_capitalisation: FRAIS_ARRERAGES_VENDU,
      frais_encours_rente_capitalisation: 0.0, ...figes,
    },
    aucun: {
      frais_versement_capitalisation: 0.0, frais_gestion_capitalisation: 0.0,
      frais_arrerages_capitalisation: 0.0, frais_encours_rente_capitalisation: 0.0,
      ...figes,
    },
  };
  if (!(regime in regimes)) {
    throw new Error(`régime de frais inconnu : ${regime}`);
  }
  return avec(parametres, regimes[regime]);
}

export function tauxAu(niveau, paliers, annee) {
  let taux = niveau;
  for (const [debut, valeur] of [...(paliers || [])].sort((a, b) => a[0] - b[0])) {
    if (annee >= debut) taux = valeur;
  }
  return taux;
}

/** Le taux d'un poste de frais du pilier (`versement`, `gestion`, `arrerages`,
 * `encours_rente`) l'année `annee`. */
export function fraisCapitalisation(parametres, poste, annee) {
  return tauxAu(
    parametres[`frais_${poste}_capitalisation`],
    parametres[`frais_${poste}_paliers`],
    annee,
  );
}

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
