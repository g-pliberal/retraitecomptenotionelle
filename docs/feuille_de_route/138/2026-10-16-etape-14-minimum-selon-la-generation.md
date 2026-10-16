# Étape 14, troisième partie : le minimum contributif selon la génération, et les retraités de l'étranger

**Le 16 octobre 2026 : la part de la population au minimum contributif suit
désormais, depuis 2013, la pente de l'EACR — elle perd 7,1 points de 2013 à
2023, l'EACR de la Cnav 6,9 —, mais pas son niveau, de 3 à 5 points trop bas,
de 6 chez les hommes. Une part de l'écart tenait à la mesure : l'EACR compte
tous les liquidants, la population les seuls résidents. Les retraités de
l'étranger, que l'EIR donne par différence, s'y ajoutent : 15,9 % des
liquidants de 2023 au minimum au lieu de 15,2 (18,8 aux régimes alignés), les
hommes à 7,6 % au lieu de 6,4 (12,2). Le reste n'est pas dans la population :
ses carrières courtes atteignent le minimum moins souvent que celles de l'EIR.
Rien ne bouge sur la page.**

Demande : la vague bis du 16 octobre 2026, session 4, « action 138, étape 14.
La population, encore : une part au minimum contributif qui suive les
générations (le minimum contributif de 2023 : 15,3 % des liquidants au modèle
contre 18,8 % dans l'EACR, note du 12 octobre), jugée sur l'EIR sans s'y
caler ». Le point 1 de « Ce qui reste », note des départs avec décote.

- *Ce que la mesure accusait, relu sur la quinzième version.* La note de la
  neuvième version (action 136, 12 octobre) : de 2012 à 2019, la population
  perdait 14 points de liquidants au minimum, l'EACR 7. Sur la quinzième
  (`part_minimum_contributif.py --grille population`, avant ce changement),
  la pente se tient depuis 2013 : 22,3 % des liquidants de 2013 pour 24,8 à
  la Cnav, 15,2 % de ceux de 2023 pour 17,9, l'écart restant de −2,5 à
  −5,0 points chaque année, sauf 2016 (+0,7) et 2024 (+0,2, l'estimation de
  la DREES). Deux restes. 2012, à 29,7 % pour 27,1 : les femmes des
  générations 1946 à 1949, au minimum à 34 ou 35 %, quand celles de 1950 n'y
  sont qu'à 26 %. Et le niveau des hommes : 6,1 à 6,9 % des liquidants de
  2019 à 2023, pour 12,2 en 2022 et en 2023.
- *D'où vient le creux des hommes.* Les carrières complètes du bas de
  l'échelle, quatre sous-classes de 1,5 % des hommes chacune
  (`SOUS_CLASSES_DU_BAS`), sont au seuil du minimum : celle du bas, née en
  1958, liquide en 2020 une pension du régime général de 722 € par mois,
  pour un minimum majoré de 702,55 € ; née en 1955, elle l'avait. Une
  sous-classe entière passe d'un côté ou de l'autre d'une génération à la
  suivante : 6,3 à 8,3 % des hommes aux carrières complètes sont au minimum
  dans les générations 1946 à 1952, 1,5 % dans celles de 1957 à 1961, 4,9 %
  dans celle de 1962, qui a le relèvement de 2023. La population ne connaît
  qu'un volume de travail par âge et par rang (`VOLUME_DE_TRAVAIL`), le même
  pour tous : elle abaisse toutes les carrières un peu, quand l'emploi
  fragmenté en abaisse quelques-unes beaucoup — ce que le minimum relève.
  Aucune source du dépôt ne dit comment ce volume se répartit entre les
  personnes, ni comment il change d'une génération à l'autre.
- *Ce qui est fait : les retraités de l'étranger* (`NON_RESIDENTS`,
  `grille_large.non_residents`, `poids_des_non_residents`,
  `avec_les_non_residents`). L'EIR publie ses quintiles pour tous les
  retraités et pour les seuls résidents (`quintiles_eqcc.csv`,
  `quintiles_eqcc_residents.csv`, certifiés) : leur différence donne les
  retraités de l'étranger de 2020, 3,3 % des femmes et 7,9 % des hommes, aux
  carrières françaises courtes — 28 % de ces femmes et 22 % de ces hommes ont
  moins de dix années validées, pour 7,7 et 1,0 % des résidents —, et 62,3 %
  de ces femmes, 42,6 % de ces hommes au minimum de pension de leur régime
  principal. Le minimum contributif n'étant pas soumis à la résidence,
  l'EACR les compte. La mesure les ajoute : la population repesée, chaque
  tranche de durée à leur part, chaque variante gardant sa place dans sa
  tranche, et chaque sexe à leur part de 2020 ; les simulations servent aux
  deux, sans en refaire. Deux conventions : à durée égale, un retraité de
  l'étranger a la carrière d'un résident ; sa part parmi les liquidants de
  chaque année est celle du stock de 2020. La part de l'EIR au minimum juge,
  elle ne cale rien.
- *Ce qu'elle trouve*, part des liquidants au minimum contributif, sans puis
  avec les retraités de l'étranger, contre l'EACR (Cnav jusqu'en 2018,
  régimes alignés depuis 2019, par sexe depuis 2022) :

  | | 2012 | 2016 | 2019 | 2021 | 2022 | 2023 | 2024 |
  |---|---|---|---|---|---|---|---|
  | résidents seuls | 29,7 % | 22,8 | 14,8 | 13,3 | 13,7 | 15,2 | 17,6 |
  | avec l'étranger | 31,1 % | 23,7 | 15,4 | 14,0 | 14,4 | 15,9 | 18,6 |
  | EACR | 27,1 % | 22,1 | 20,4 | 17,9 | 18,9 | 18,8 | 18,6* |
  | femmes, avec l'étranger | 38,8 % | 30,9 | 20,9 | 19,2 | 20,1 | 22,4 | 25,4 |
  | femmes, EACR | | | | | 25,2 | 25,2 | 24,1* |
  | hommes, avec l'étranger | 20,0 % | 13,8 | 8,0 | 7,3 | 7,4 | 7,6 | 11,8 |
  | hommes, EACR | | | | | 12,2 | 12,2 | 12,7* |

  \* l'estimation de la DREES. Les retraités de l'étranger seuls : 25 à 30 %
  au minimum parmi les liquidants de 2019 à 2023, 39 à 48 % de 2012 à 2016 ;
  35,4 % de la génération 1950, 24,6 % de celle de 1960, 21 à 22 % de leurs
  hommes des générations 1960 à 1975. L'EIR en met 42,6 % de leurs hommes et
  62,3 % de leurs femmes au minimum de pension, toutes générations du stock
  de 2020 et tous minima confondus. Le minimum moyen d'un bénéficiaire baisse
  de 3 à 5 € : 106 € de 2023 en 2023 au lieu de 109 (134 aux régimes alignés).
- *Ce que la mesure accuse.* Les carrières courtes de la population
  atteignent le minimum moins souvent que celles de l'EIR : ses retraités de
  l'étranger, faits surtout d'elles, y sont à 35 % dans la génération 1950 et
  à 25 % dans celle de 1960, quand l'EIR en met 49 % au minimum, les deux
  sexes réunis, dans un stock fait des générations anciennes. Une part de
  ces carrières part avec une décote, et perd le minimum (quinzième version).
  Le rang n'en est pas la cause : la population range au premier quintile
  82,6 % de ses femmes de moins de dix années validées, l'EIR 83,5 % de ses
  résidentes. Et le niveau des hommes reste à moitié de l'EACR : ce sont les
  carrières complètes et fragmentées qu'elle n'a pas.
- *Ce qui ne bouge pas.* La population elle-même : aucune page, aucun
  moteur, aucun témoin ; `grille_large.py` ne lit pas les retraités de
  l'étranger, que seule la mesure du minimum ajoute. La page ne lit pas la
  population (action 157), dont la dépense paie pourtant les pensions
  servies à l'étranger : la bascule pourra reprendre les mêmes poids. Le
  registre non plus : aucun de ses points « 138.14 » ne nomme les
  non-résidents. Les tests (`test_part_minimum_contributif.py`) : les parts
  de l'EIR, et la repesée, qui garde le total de chaque sexe.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : un emploi fragmenté concentré sur une part des
   carrières complètes du bas de l'échelle, s'il se trouve une source qui
   dise comment le volume de travail se répartit entre les personnes ou
   change d'une génération à l'autre (l'enquête Emploi, les panels de la
   DADS) ; à défaut, des sous-classes du bas plus fines, que le seuil du
   minimum ne fasse plus basculer par blocs ; les femmes des générations
   1946 à 1949, au minimum à 34 % ; la décote selon la tranche ou le rang,
   si une source la publie par durée. Les niveaux des cas types statutaires
   et non salariés attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), retraités de l'étranger
   compris, au propriétaire.
3. *Les départs choisis*, au-delà de la décote (PRISME, SESIM, T-DYMM) :
   l'âge publié (`age_conjoncturel_depart.csv`), la surcote.
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension* (CALIPER, Oscar), au CASD, sur une
   habilitation que seul le propriétaire peut demander.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).
