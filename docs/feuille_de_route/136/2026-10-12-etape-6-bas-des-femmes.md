# Étape 6, la population : la pension des femmes au bas de l'échelle — une affaire de générations

**Le 12 octobre 2026 : la pension des femmes n'est pas trop haute par année
validée. Au bas de l'échelle, elle vaut ce que le droit lui donne : le minimum
contributif et la complémentaire, 780 à 840 € par année au premier quintile de
la pension en équivalent carrière complète. L'EIR y descend à 650 € parce
qu'il y compte des retraitées que le minimum ne relève pas — parties avant le
taux plein, ou résidant à l'étranger —, que la population, qui part au taux
plein et réside en France, n'a pas. Ce qui fausse le bas des femmes, c'est la
génération : la population donne à toutes les mêmes carrières, quand l'EIR
voit la durée des femmes monter de 33,2 années pour la génération 1940 à 39,5
pour 1953, et 41 pour les suivantes. Ses femmes valident 34,7 années à toutes
les générations, celles de l'EIR 33,8 autour de 1940, 36,2 autour de 1945,
38,2 autour de 1950 : les plus anciennes, aux carrières les plus courtes et
aux pensions les plus basses, manquent au bas de 2020. La population ne change
pas ; la mesure compte désormais la durée validée de chaque génération.**

Demande du propriétaire : « Fait la prochaine étape » — « la pension des
femmes, trop haute par année validée au bas de l'échelle » (note du haut de
l'échelle des hommes).

- *Le bas des femmes, décomposé* (essai, hors du dépôt : la population de 2020
  de la onzième version, sous les poids de la page). Au premier quintile, les
  tranches de durée y sont à peu près celles de l'EIR, et toutes valent la
  même chose par année validée, au minimum pour 70 à 88 % :

  | | moins de 10 ans | 10 à 20 | 20 à 30 | 30 à 40 | 40 et plus |
  |---|---|---|---|---|---|
  | part du premier quintile, EIR | 23,1 % | 24,1 % | 20,9 % | 19,5 % | 12,3 % |
  | part du premier quintile, population | 19,1 % | 21,0 % | 21,2 % | 19,7 % | 19,0 % |
  | pension, population | 180 € | 399 € | 617 € | 798 € | 838 € |
  | par année validée, population | 777 € | 812 € | 830 € | 822 € | 838 € |
  | au minimum, population | 77,3 % | 84,2 % | 88,3 % | 70,7 % | 79,5 % |

  Le minimum contributif de 2020, 645 € par mois pour une carrière entière,
  705 € majoré, et la complémentaire font ces 780 à 840 € ; les majorations de
  durée de deux enfants, quatre années, en relèvent d'autant la proratisation
  pour les carrières courtes. Au deuxième quintile, la population range pour
  38 % des salariées du privé de la classe médiane, à 1 155 € par année
  validée, quand l'EIR y est à 930 € environ en moyenne. - *Ce que l'EIR y
  compte de plus.* Son premier quintile, à 431 € de pension pour 66,5 % de
  proratisation, ne passe pas 650 € par année validée : il faut, à côté de ses
  64 % de retraitées au minimum, des pensions que le minimum ne relève pas,
  parties avec une décote avant le taux plein, ou servies à l'étranger — l'EIR
  des quintiles compte tous les retraités. La population part au taux plein,
  la convention du COR, et réside en France ; aucune série du dépôt ne dit la
  part des départs avec décote. - *La génération* (`grille_large.py --grille
  population`) : la durée validée moyenne de chaque génération de 2020, contre
  la durée d'assurance que l'EIR mesure aux résidents
  (`duree_assurance_generations.csv`), majorations comprises :

  | | 1940 | 1945 | 1950 | 1955 | 1960 |
  |---|---|---|---|---|---|
  | femmes, EIR | 33,8 | 36,2 | 38,2 | 40,6 | 41,2 |
  | femmes, population | 34,7 | 34,7 | 34,8 | 40,5 | 40,2 |
  | hommes, EIR | 40,4 | 40,8 | 40,6 | 40,9 | 40,5 |
  | hommes, population | 37,8 | 37,5 | 37,9 | 40,9 | 37,3 |

  Chaque génération simulée représente les cinq qui l'entourent. L'EIR n'est
  certifié que jusqu'à la génération 1953 ; au-delà, son prolongement par
  TRAJECTOiRE compte la génération entière, quand celles de 1955 et de 1960
  n'ont encore en 2020, dans la population, que leurs carrières déjà
  liquidées. Les femmes de 1925 à 1935 valident 34,6 à 34,7 années dans la
  population ; l'EIR ne les mesure pas, mais la pente de ses générations
  suivantes les met plus bas. L'écart des hommes, trois années à toutes les
  générations, est celui des carrières statutaires (note du haut de l'échelle
  des hommes).

- *Le stock de 2020.* Les carrières courtes, qui attendent le taux plein à 65
  ou 67 ans, ne sont encore en 2020 que celles des générations nées jusqu'en
  1955 : la population en compte 32,4 % parmi les retraitées nées jusqu'en
  1950, 11,8 % parmi celles de 1955, 2,2 % parmi celles de 1960, 27,6 % en
  tout, pour 33,7 dans l'EIR, qui compte aussi celles de l'étranger. - *La
  mesure.* La passe de la pension en équivalent carrière complète garde aussi
  la durée validée de chaque cohorte (`proratisations`), et la sortie la range
  par génération, contre celle de l'EIR (`durees_par_generation`,
  `durees_d_assurance`). Un test la tient
  (`test_la_duree_validee_se_lit_generation_par_generation`). - *Ce que la
  mesure accuse.* La grille ne sait pas donner à une carrière un poids qui
  dépende de sa génération : ses parts de tranches de durée sont celles des
  retraités de 2020, pour toutes. Les femmes de la population ont donc, à
  chaque génération, les carrières de la moyenne du stock — trop longues pour
  les plus anciennes, trop courtes pour les suivantes. Le bas de 2020 y perd
  les plus vieilles, aux carrières les plus courtes ; la projection, après la
  bascule, y perdrait les carrières pleines des femmes nées après 1955. Deux
  voies : des durées de carrière qui suivent la génération, les poids gardés —
  les carrières incomplètes des femmes s'allongent ou se raccourcissent pour
  redonner la durée de l'EIR de chaque génération, comme l'entrée des
  carrières pleines le fait déjà — ; ou des poids selon la génération, qui
  toucheraient la pondération de la page (`cout.py`). La première reste dans
  la population.

**Ce qui reste** de l'étape, dans l'ordre : les carrières des femmes selon la
génération, leurs durées calées sur celles de l'EIR ; le minimum selon la
génération ; enfin, au propriétaire, la bascule de la page — et, s'il le veut,
une action à part pour les catégories des régimes statutaires.
