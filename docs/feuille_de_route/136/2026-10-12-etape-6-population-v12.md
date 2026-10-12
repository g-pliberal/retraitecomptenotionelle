# Étape 6, la population : les carrières des femmes selon leur génération, la douzième version

**Le 12 octobre 2026 : les carrières incomplètes des femmes suivent désormais
leur génération. Hors des régimes statutaires, elles gagnent ou perdent,
génération par génération, les années qui portent la durée moyenne des femmes
à celle que l'EIR mesure aux résidentes : elles en perdent 2,3 jusqu'à la
génération 1940, en gagnent 8,3 pour 1950, 15 à 17 pour les générations 1955 à
1970. La population retrouve la durée de l'EIR — 33,5 années autour de 1940
(33,8), 35,1 autour de 1945 (36,2), 38,1 autour de 1950 (38,2) —, et la part
de chaque tranche de durée au premier quintile de la pension en équivalent
carrière complète. Mais la pension des femmes de 2020 s'éloigne de l'EIR :
leur moyenne passe de 1 312 à 1 369 € (1 177), leur médiane de 1 237 à 1 302 €
(1 013), et le passé refait recule, de 10,9 à 17,0 % d'écart au pire depuis
2000. Les carrières trop courtes des générations 1945 à 1957 cachaient une
pension trop haute par année validée au deuxième quintile, où l'EIR compte
60 % de femmes au minimum, la population 18. La douzième version reste en
place.**

Demande du propriétaire : « Fait l'étape suivante » — « les carrières des
femmes selon la génération, leurs durées calées sur celles de l'EIR » (note du
bas des femmes).

- *La forme* (`DUREE_DES_FEMMES_SELON_LA_GENERATION`, `ecarts_des_femmes`,
  `femmes_selon_la_generation`, le champ `cibles` du cas type,
  `scripts/grille_large.py`). Les poids et les tranches restent ceux des
  retraitées de 2020 ; seules changent les années validées des carrières
  incomplètes des femmes hors des régimes statutaires, 54 % des femmes sous
  les poids de l'EIR. À chaque génération, un même écart d'années s'ajoute à
  toutes ou s'en retranche, qu'une bissection cale sur la durée d'assurance de
  l'EIR, majorations comprises (`duree_assurance_generations.csv`, certifiée
  de 1940 à 1953, projetée par TRAJECTOiRE au-delà ; les générations d'avant
  1940 gardent la durée de 1940). La durée moyenne s'y compte comme la
  simulation la fait : une carrière incomplète à ses années, une carrière
  pleine de son entrée à l'âge légal de sa génération, les deux avec les
  majorations de deux enfants, quatre années ; une carrière statutaire à sa
  durée. Une carrière incomplète garde une année au moins, ne passe pas l'âge
  légal, et place ses années comme celles de sa tranche
  (`decalages_de_tranche`), étalées de l'entrée à soixante ans. Les hommes
  n'en reçoivent pas : leur durée, dans l'EIR, ne change guère d'une
  génération à l'autre. Un test tient la forme
  (`test_les_carrieres_des_femmes_suivent_la_duree_de_leur_generation`). Les
  carrières incomplètes du salariat privé, entrées à 21 ans, en années
  validées hors majorations :

  | | 1940 | 1945 | 1950 | 1955 | 1960 | 1970 | 1990 |
  |---|---|---|---|---|---|---|---|
  | moins de dix ans (5) | 3 | 6 | 13 | 20 | 21 | 20 | 16 |
  | dix à vingt (15) | 13 | 16 | 23 | 30 | 31 | 30 | 26 |
  | vingt à trente (25) | 23 | 26 | 33 | 40 | 41 | 40 | 36 |
  | trente à quarante (35) | 33 | 36 | 39 | 41 | 41 | 43 | 43 |

  La tranche de trente à quarante ans, bornée par l'âge légal, ne prend que
  quelques années ; les plus courtes portent le reste. Pour les générations
  nées après 1955, les tranches perdent leur sens : la plus courte des
  carrières des femmes y valide quinze à vingt-deux années. Des poids selon la
  génération garderaient les carrières courtes, mais toucheraient la
  pondération de la page (note du bas des femmes). - *Les années validées par
  génération* (`grille_large.py --grille population`) : la population de 2020,
  sous les poids de la page, contre la durée d'assurance de l'EIR ; et la part
  de chaque génération parmi les retraitées :

  | | 1925 | 1930 | 1935 | 1940 | 1945 | 1950 | 1955 | 1960 |
  |---|---|---|---|---|---|---|---|---|
  | EIR | — | — | — | 33,8 | 36,2 | 38,2 | 40,6 | 41,2 |
  | onzième version | 34,7 | 34,6 | 34,7 | 34,7 | 34,7 | 34,8 | 40,5 | 40,2 |
  | douzième | 33,6 | 33,5 | 33,5 | 33,5 | 35,1 | 38,1 | 42,9 | 41,1 |
  | part, onzième version | 2,4 % | 6,5 % | 11,0 % | 13,5 % | 18,3 % | 26,4 % | 15,6 % | 4,9 % |
  | part, douzième | 2,2 % | 6,0 % | 10,1 % | 12,4 % | 16,7 % | 24,1 % | 21,1 % | 6,1 % |

  Au-delà de 1953, l'EIR compte la génération entière, la population de 2020
  ses seules retraitées. Les carrières des femmes nées de 1953 à 1957, dont
  les plus longues atteignent désormais la durée requise à l'âge légal,
  n'attendent plus toutes l'âge du taux plein automatique : elles font 21,1 %
  des retraitées de 2020 au lieu de 15,6, et, sous les poids de la page, les
  femmes 51,8 % des retraités au lieu de 49,8 (54,0 dans l'EIR, qui compte
  aussi celles de l'étranger). - *Les pensions de 2020 contre l'EIR*, en euros
  par mois ; Kolmogorov : le plus grand écart des répartitions, et la borne où
  il tombe :

  | | moyenne | d1 | d3 | médiane | d9 | Kolmogorov |
  |---|---|---|---|---|---|---|
  | ensemble, EIR | 1 536 | 402 | 933 | 1 382 | 2 730 | |
  | ensemble, onzième version | 1 537 | 525 | 1 052 | 1 379 | 2 684 | −7,9 pt à 1 000 |
  | ensemble, douzième | 1 568 | 610 | 1 098 | 1 404 | 2 684 | −10,4 pt à 900 |
  | femmes, EIR | 1 177 | 283 | 703 | 1 013 | 2 229 | |
  | femmes, onzième version | 1 312 | 421 | 878 | 1 237 | 2 235 | −13,7 pt à 1 100 |
  | femmes, douzième | 1 369 | 465 | 938 | 1 302 | 2 298 | −18,4 pt à 900 |
  | hommes, EIR | 1 957 | 872 | 1 374 | 1 745 | 3 242 | |
  | hommes, onzième version | 1 761 | 857 | 1 245 | 1 631 | 2 848 | +8,5 pt à 1 400 |
  | hommes, douzième | 1 781 | 871 | 1 245 | 1 631 | 2 892 | +7,9 pt à 1 400 |

  Par génération, la pension moyenne des femmes de 2020, onzième puis douzième
  version (essai, hors du dépôt : la population de 2020, sous les poids de la
  page, décomposée) : 1 138 puis 1 124 € pour les générations nées jusqu'en
  1937, 1 246 puis 1 229 de 1938 à 1942, 1 274 puis 1 302 de 1943 à 1947,
  1 283 puis 1 393 de 1948 à 1952, 1 619 puis 1 651 de 1953 à 1957. Les
  carrières des hommes ne changent pas ; leur pension ne bouge que par la
  pondération de la page. - *La pension en équivalent carrière complète.* Au
  premier quintile, la part de chaque tranche de durée des femmes est
  désormais celle de l'EIR, à quatre points près : 81,3 % de celles de moins
  de dix ans (80,5 dans l'EIR), 65,7 % de dix à vingt (62,0), 44,5 % de vingt
  à trente (44,2), 19,1 % de trente à quarante (18,5), 13,6 % de quarante et
  plus (10,1). L'écart moyen des cinq cases des femmes tombe de 4,1 à 1,8
  point, celui des dix cases des deux sexes de 6,4 à 5,3. Au minimum de
  pension, 29,8 % des femmes de 2020 au lieu de 31,6 (38,5 dans l'EIR). La
  proratisation des femmes passe, du premier quintile au cinquième, de 70,1,
  86,8, 92,7, 96,4 et 97,1 % à 75,7, 89,1, 94,4, 97,1 et 97,7 % (66,5, 87,0,
  96,0, 98,6 et 98,2 dans l'EIR). - *Le minimum contributif*
  (`part_minimum_contributif.py`) : en 2023, 13,6 % des liquidants au lieu de
  15,7 (EACR 18,8), les femmes à 17,8 % au lieu de 21,8 (25,2), les hommes à
  8,3 % ; en 2024, 17,7 % au lieu de 22,6 (18,6 estimée), les femmes à 23,2 %
  au lieu de 30,3 (24,1). Le minimum moyen d'une bénéficiaire monte avec sa
  durée, que le minimum proratise : 88 € en 2023 au lieu de 74 (134 à 138 dans
  l'EACR). De 2012 à 2019, la part de la population perd toujours 19 points,
  celle de l'EACR 7. - *Sur la page*, contre la onzième version : l'écart des
  années observées passe de −1,41 à −1,48 point au scénario 2, de −3,13 à
  −3,26 aux scénarios 4 et 6 ; la part du PIB en 2070 de −0,17 à −0,22 point
  au scénario 2, de −0,66 à −0,75 au scénario 4 ; le solde moyen de 2026 à
  2070 de +0,18 à +0,23 point au scénario 2, de +0,57 à +0,70 au scénario 4 ;
  le coefficient de 2070 du scénario 2 de +0,100 à +0,128 ; la garantie de
  +0,087 à +0,050 point. Le passé refait recule : l'écart de 2000 passe de
  −10,9 à −17,0 %, celui de 2009 de −9,3 à −13,6 %, le pire depuis 2000 de
  10,9 à 17,0 % (16,6 pour les treize cas types). Lancée à rebours de la
  dernière année publiée, la projection voit désormais la pension des femmes
  monter d'une génération à l'autre avec leur durée, et la dépense du modèle
  monter plus vite que la dépense observée ; la mesure ne dit pas encore
  pourquoi. - *Ce que la mesure accuse.* La pension des femmes de 2020 dépasse
  celle de l'EIR à tous les quintiles de la pension en équivalent carrière
  complète, et le plus aux deux premiers (essai, hors du dépôt : la population
  de 2020, sous les poids de la page, décomposée ; l'EIR compte aussi les
  retraitées de l'étranger) :

  | | q1 | q2 | q3 | q4 | q5 |
  |---|---|---|---|---|---|
  | pension, EIR | 431 € | 812 € | 1 297 € | 1 726 € | 2 593 € |
  | pension, onzième version | 565 € | 1 019 € | 1 381 € | 1 798 € | 2 719 € |
  | pension, douzième | 633 € | 1 055 € | 1 407 € | 1 830 € | 2 745 € |
  | au minimum, EIR | 64,3 % | 59,9 % | 18,4 % | 9,9 % | 1,1 % |
  | au minimum, douzième | 80,1 % | 18,4 % | 17,5 % | 1,0 % | 0,0 % |

  Au deuxième quintile, l'EIR range des carrières presque entières — 32 années
  validées hors majorations, proratisées à 87 % — et les trois cinquièmes au
  minimum : des pensions assez basses pour que le minimum les relève. La
  population y range, proratisées à 89 %, des carrières que le minimum ne
  relève pas, dont 42,7 % de salariées du privé de la classe médiane et
  au-dessus. Chez les hommes, l'EIR met au minimum 32,6 % de son deuxième
  quintile, la population 18,8 %. Le salaire des carrières presque entières au
  bas de l'échelle, ou le niveau du minimum qui les relève : c'est là que la
  mesure accuse désormais ; les carrières trop courtes des générations 1945 à
  1957 le cachaient.

**Ce qui reste** de l'étape, dans l'ordre : le deuxième quintile — la pension
par année validée des carrières presque entières, que l'EIR met pour les trois
cinquièmes au minimum — ; le minimum selon la génération ; enfin, au
propriétaire, la bascule de la page — et, s'il le veut, une action à part pour
les catégories des régimes statutaires. La douzième version reste en place,
débrayable par sa constante.