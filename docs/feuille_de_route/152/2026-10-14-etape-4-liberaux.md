# Étape 4, les professions libérales : le niveau tient en moyenne, c'est la forme du groupe qui manque

**Le 14 octobre 2026 : le cas type de la profession libérale garde son
niveau. Pesés comme la page les pèse, les libéraux hommes de la population
touchent 2 592 € par mois en 2020, quand la DREES en compte 2 700 aux
retraités dont les professions libérales sont le régime principal ; les femmes,
1 977 €, pour 1 650. Ce qui met 72 % des hommes au cinquième quintile, pour
45 dans l'EIR, c'est la forme du groupe : la population le resserre autour de
sa moyenne, de 1 693 € au dixième centile à 3 471 € au quatre-vingt-dixième,
quand l'EIR l'étale sur les cinq quintiles. Le cas type est un libéral de la
Cipav, la section la moins dotée, et sa pension plafonne vers 3 600 € : élargir
la dispersion de ses revenus n'y ajoute que le bas. L'EIR mêle dix sections,
des médecins aux libéraux de la Cipav ; il faudrait les décliner. La population
ne change pas ; la décision revient au propriétaire.**

Session de nuit du 14 octobre 2026, la tâche n° 9 : « Commence par leur ligne
dans les quintiles des résidents ; puis, si la session le permet, la place des
deux civils de l'État dans les quintiles. » Le propriétaire dort : aucune
décision n'est prise à sa place, et rien du modèle ni de la population n'est
changé.

- *Ce qui place le groupe.* La population remesurée ce jour, à l'identique
  de l'étape 3 (`grille_large.py --grille population`, 766 cas types, bornes
  989, 1 314, 1 651 et 2 190 €), contre l'EIR 2020 des résidents,
  monopensionnés et polypensionnés de deux régimes :

  | professions libérales | q1 | q2 | q3 | q4 | q5 |
  |---|---|---|---|---|---|
  | hommes, EIR | 0,9 | 5,8 | 17,5 | 30,7 | 45,1 |
  | hommes, population | 0,9 | 1,2 | 3,9 | 21,9 | 72,1 |
  | femmes, EIR | 4,3 | 16,9 | 37,0 | 28,3 | 13,5 |
  | femmes, population | 5,1 | 4,9 | 13,1 | 26,3 | 50,6 |

- *Le niveau, contre la DREES.* « Les effectifs de retraités, montants des
  pensions et âges de départ à la retraite fin 2020 » (data.drees, jeu
  `1393_les-effectifs-et-montants-de-pension-des-retraites`, classeur de fin
  2020, empreinte SHA-256 commençant par `e5b5ddc6b42b3123`), tableau 2.1-d :
  pension mensuelle brute moyenne de droit direct, majoration pour trois
  enfants comprise, des retraités dont les professions libérales sont le
  régime principal, 2 700 € chez les hommes, 1 650 chez les femmes ; à
  carrière complète, 3 130 et 2 060 (tableau 2.1-e : monopensionnés 2 320 €
  chez les hommes, polypensionnés 2 810). La population, sous les poids de la
  page, sert 2 592 € à ses hommes et 1 977 à ses femmes ; ses carrières de
  trente à quarante ans, 2 676 et 2 420. Le niveau moyen des hommes tient à
  4 % près ; celui des carrières complètes est même trop bas, celui des
  femmes trop haut d'un cinquième. Baisser le niveau du cas type pour le
  ramener au quatrième quintile casserait la moyenne.
- *La forme.* La population décline le cas type, à 2,5 salaires moyens, sur
  la dispersion des salaires du privé : ses hommes vont de 1 693 € au
  dixième centile à 3 471 € au quatre-vingt-dixième, médiane 2 619. L'EIR,
  pour une moyenne de 2 700 €, en met 24 % sous 1 651 € en équivalent
  carrière complète et 45 % au-dessus de 2 190 : une médiane vers 2 150 €,
  sous la moyenne, et une queue haute épaisse. Le recueil statistique 2025 de
  la CNAVPL (`recueil-statistique-2025`, SHA-256 `469fd853965824f1`, p. 17)
  dit d'où elle vient : en 2024, 171 265 titulaires d'une pension de base à
  la Cipav, 85 107 à la CARPIMKO, 92 648 à la CARMF, 28 885 à la CAVP,
  25 928 à la CARCDSF, 25 619 à la CAVAMAC, 11 991 à la CAVEC, 5 556 à la
  CPRN ; les avocats, à la CNBF, à part. La pension de base moyenne, carrières
  courtes comprises, va de 2 072 € par an à la Cipav à 7 780 à la CARMF et
  8 106 à la CPRN, et la complémentaire d'un médecin pèse plus que sa base
  (`affiliations.yaml`, `medecin_liberal`).
- *Ce que la dispersion n'y fait pas* (essai, hors du dépôt : la dispersion
  des libéraux seuls élevée à une puissance, leur revenu moyen gardé). À la
  puissance 1,6, les hommes passent à 2,3, 13,8, 7,4, 20,0 et 56,6 % ; à 2,2,
  à 9,0, 23,0, 6,6, 19,3 et 42,1 %, et leur pension moyenne tombe de 2 592 à
  2 282 puis 2 078 €. Le haut ne bouge pas : 3 569 et 3 593 € au
  quatre-vingt-dixième centile. Le cas type, un libéral de la Cipav, ne
  dépasse guère 3 600 € à 2,5 salaires moyens ou au-delà : base à son
  maximum, complémentaire de la section par défaut. L'élargir creuse le
  troisième quintile et remplit les deux premiers, sans peupler le haut.
- *Ce qu'il faudrait.* Décliner le groupe par section, au poids des
  titulaires de la CNAVPL : un libéral de la Cipav, plus bas qu'aujourd'hui,
  et un médecin de la CARMF (`medecin_liberal`, déjà au catalogue), au moins ;
  les auxiliaires médicaux de la CARPIMKO, nombreux, entre les deux. Ce qui
  manque est le revenu de chaque section : ni le recueil de la CNAVPL ni la
  DREES ne le donnent ; l'INSEE (« Emplois et revenus des indépendants ») et
  la DREES (le revenu des médecins libéraux, 2020 provisoire et marqué par la
  crise sanitaire) le donnent, à certifier. La page, elle, garde un seul cas
  type : la déclinaison serait celle de la population.
- *Les civils de l'État, même mesure.* Hommes, EIR 0,1, 0,5, 13,9, 27,6 et
  58,0 % ; population 0,0, 3,3, 20,4, 36,9 et 39,3. Femmes, EIR 0,0, 1,2,
  18,0, 32,0 et 48,8 ; population 0,0, 13,2, 23,9, 26,7 et 36,2. La
  population sert 2 376 € à ses hommes et 2 103 à ses femmes ; la DREES
  (tableau 2.1-d) 2 510 et 2 090, à carrière complète 2 630 et 2 280. Le
  niveau des hommes est bas de 5 % ; ce qui les écarte surtout est le bas de
  la dispersion du privé, 1 465 € au dixième centile, qu'une grille
  indiciaire n'a pas : le chantier de la dispersion des carrières
  statutaires, non un cas type à déplacer. Les femmes, 13 % au deuxième
  quintile pour 1 : même cause.

**Ce qui reste**, au propriétaire : décliner les libéraux de la population
par section (le revenu de chaque section à certifier d'abord), ou garder le
groupe tel quel et consigner l'écart ; pour les civils, la dispersion propre à
la fonction publique, chantier à part, que cette mesure rejoint.
