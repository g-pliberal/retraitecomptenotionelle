# Étape 6, la population : la pension des hommes manque de durée — les carrières statutaires à leur durée, la dixième version

**Le 12 octobre 2026 : la pension des hommes manquait de durée, non de
salaire. Décomposée, la neuvième version leur donnait 35,5 années validées,
pour 40,0 dans l'EIR, et 37 % à quarante ans et plus, pour 72 % ; dans les
trois quintiles du haut, leur proratisation était de 90 à 94 %, quand celle de
l'EIR est presque entière, et leur pension en manquait d'autant. Une des
causes était une erreur de convention : le calage des tranches tenait les
carrières statutaires pour entières, quand le militaire, l'agent de conduite,
l'agent des IEG et le fonctionnaire actif en ont de 25 à 36 ans. Corrigée, la
médiane des hommes passe de 1 570 à 1 622 € (1 745 dans l'EIR), leur premier
décile de 719 à 863 € (872), et la pension moyenne de tous est celle de l'EIR,
1 536 €. Reste l'âge d'entrée : les carrières pleines commencent à 21 ans, et
les hommes nés de 1938 à 1953 ne valident encore que 36 années, pour 40,5.**

Demande du propriétaire : « Fait la prochaine étape » — la pension des hommes,
« sous l'EIR du premier au neuvième décile » (note de la neuvième version).

- *Ce qui manque aux hommes* (essai, hors du dépôt : la population de 2020,
  sous les poids de la page, décomposée par sexe, groupe, tranche de durée et
  quintile de la pension en équivalent carrière complète). L'EIR compte tous
  les retraités, ceux de l'étranger compris ; ses durées, les majorations
  comprises :

  | | pension | proratisation | années validées | quarante ans et plus |
  |---|---|---|---|---|
  | hommes, EIR | 1 840 € | 90,4 % | 40,0 | 72,0 % |
  | hommes, neuvième version | 1 715 € | 89,7 % | 35,5 | 37,0 % |
  | hommes, dixième | 1 766 € | 92,0 % | 36,6 | 45,6 % |
  | femmes, EIR | 1 152 € | 83,3 % | 36,0 | 51,8 % |
  | femmes, neuvième version | 1 273 € | 85,2 % | 34,2 | 29,2 % |
  | femmes, dixième | 1 303 € | 86,1 % | 34,9 | 40,4 % |

  Aux trois quintiles du haut, la pension des hommes et leur proratisation,
  dans la neuvième version puis la dixième, contre l'EIR
  (`quintiles_eqcc.csv`) : 1 348 puis 1 400 € pour 1 404 au troisième, à 89,8
  puis 91,4 % pour 99,1 ; 1 739 puis 1 797 € pour 1 871 au quatrième, à 92,8
  puis 94,5 % pour 100,0 ; 2 882 puis 2 959 € pour 3 161 au cinquième, à 93,6
  puis 95,1 % pour 98,5. - *Par génération*, les années validées des hommes,
  contre la durée d'assurance que l'EIR mesure aux résidents
  (`duree_assurance_generations.csv`, certifiée de 1940 à 1953) :

  | | 1938 à 1941 | 1942 à 1945 | 1950 à 1953 |
  |---|---|---|---|
  | EIR | 40,5 | 40,4 | 40,6 |
  | neuvième version | 34,7 | 35,1 | 35,4 |
  | dixième | 35,8 | 36,3 | 36,7 |
  | carrières pleines du salariat privé, l'une et l'autre | 39,2 | 40,0 | 40,5 |

  Les carrières pleines elles-mêmes valident moins que la moyenne de tous les
  hommes de l'EIR : le gabarit commence à 21 ans, pour toutes les générations,
  et les générations nées avant 1951 partent à 60 ans. - *Trois causes.* Le
  calage des tranches, corrigé ici. L'âge d'entrée, unique. Les carrières
  statutaires sans la suite d'un second métier : le militaire part à 44 ans,
  et la grille ne mêle pas sa carrière (`GROUPES_MELES`), quand un tiers des
  militaires de l'EIR sont polypensionnés. - *La forme*
  (`STATUTAIRES_A_LEUR_DUREE`, `parts_tranches_de_tous`,
  `scripts/grille_large.py`). Pour redonner à tous les retraités de chaque
  sexe les parts des tranches de durée de l'EIR, la population comptait les
  carrières statutaires dans la tranche la plus longue : les autres groupes
  portaient seuls, grossie d'autant, celle de trente à quarante ans, que
  l'agent de conduite, l'agent des IEG et le fonctionnaire actif remplissaient
  aussi. Chaque carrière statutaire compte désormais dans la tranche de sa
  durée, et les autres groupes complètent chacune jusqu'à la part de l'EIR.
  Leurs parts, entières puis à leur durée :

  | | 40 et plus | 30 à 40 | 20 à 30 | 10 à 20 | moins de 10 |
  |---|---|---|---|---|---|
  | femmes, avant | 19,1 | 38,6 | 17,4 | 14,3 | 10,5 |
  | femmes, après | 31,8 | 26,5 | 16,9 | 14,3 | 10,5 |
  | hommes, avant | 56,5 | 28,6 | 6,8 | 4,7 | 3,5 |
  | hommes, après | 74,8 | 15,8 | 1,2 | 4,7 | 3,5 |

  Un test tient la forme : tous les retraités de chaque sexe retrouvent la
  part de chaque tranche que l'EIR publie
  (`test_les_carrieres_statutaires_comptent_a_leur_duree`). La composition
  compte désormais les carrières courtes de tous, le militaire compris : la
  durée moyenne passe de 30,6 à 31,4 années pour les femmes (32,0 dans l'EIR),
  de 36,3 à 37,8 pour les hommes (39,0). - *Les pensions de 2020 contre
  l'EIR*, en euros par mois ; Kolmogorov : le plus grand écart des
  répartitions, et la borne où il tombe :

  | | moyenne | d1 | d3 | médiane | d9 | Kolmogorov |
  |---|---|---|---|---|---|---|
  | ensemble, EIR | 1 536 | 402 | 933 | 1 382 | 2 730 | |
  | ensemble, neuvième version | 1 495 | 505 | 1 006 | 1 338 | 2 641 | −5,8 pt à 800 |
  | ensemble, dixième | 1 536 | 525 | 1 051 | 1 366 | 2 730 | −7,8 pt à 800 |
  | femmes, EIR | 1 177 | 283 | 703 | 1 013 | 2 229 | |
  | femmes, neuvième version | 1 273 | 409 | 844 | 1 219 | 2 164 | −11,8 pt à 1 100 |
  | femmes, dixième | 1 303 | 419 | 873 | 1 237 | 2 229 | −13,5 pt à 1 100 |
  | hommes, EIR | 1 957 | 872 | 1 374 | 1 745 | 3 242 | |
  | hommes, neuvième version | 1 715 | 719 | 1 206 | 1 570 | 2 808 | +10,4 pt à 1 400 |
  | hommes, dixième | 1 766 | 863 | 1 244 | 1 622 | 2 848 | +9,1 pt à 1 700 |

- *Le minimum contributif* (`part_minimum_contributif.py`) : les carrières
  plus longues en relèvent un peu moins. En 2023, 16,6 % des liquidants au
  lieu de 17,2 (EACR 18,8), les femmes à 22,3 % au lieu de 22,6 (25,2), les
  hommes à 8,9 % au lieu de 10,1 (12,2) ; en 2024, 20,4 % au lieu de 21,8
  (18,6 estimée) ; le minimum moyen ne bouge pas, 73 à 90 € de 2019 à 2023
  (134 à 139). - *La pension en équivalent carrière complète.* Au premier
  quintile, l'écart moyen des dix cases de tranche remonte de 6,3 à 7,0
  points. Les femmes de quarante ans et plus y sont 15,1 %, pour 10,1 dans
  l'EIR : leurs carrières pleines, plus nombreuses, prennent avec elles des
  rangs du bas. Les hommes de vingt à trente ans n'y sont plus que 5,6 %, pour
  29,8 : la tranche n'est plus guère faite que de militaires, que leur pension
  par année validée tient au-dessus. Au minimum de pension, 31,9 % des femmes
  de 2020 au lieu de 33,0 (38,5 dans l'EIR), 16,6 % des hommes au lieu de 17,1
  (12,4). - *Sur la page*, contre la neuvième version : l'écart des années
  observées passe de −1,38 à −1,52 point au scénario 2, de −3,11 à −3,42 aux
  scénarios 4 et 6 ; la part du PIB en 2070 de −0,10 à −0,17 point au scénario
  2, de 0,00 à −0,18 au scénario 3, de −0,51 à −0,66 au scénario 4 ; le solde
  moyen de 2026 à 2070 de +0,39 à +0,56 point au scénario 4 ; le coefficient
  de 2070 du scénario 2 de +0,055 à +0,099 ; la garantie de +0,102 à +0,088
  point ; le passé refait, au pire depuis 2000, de 12,0 à 12,7 %. - *Ce que la
  mesure accuse.* Il manque encore aux hommes quatre à cinq années par
  génération, majorations comprises — l'EIR leur en compte une en moyenne —,
  et les carrières pleines elles-mêmes en manquent : à 21 ans d'entrée et 60
  de départ, elles ne valident que 39 à 40,5 années, quand la moyenne de tous
  les hommes de l'EIR, carrières courtes comprises, en a 40,5. La durée
  d'assurance de l'EIR par génération et par sexe, certifiée, en est la
  mesure. Les femmes, elles, s'éloignent : plus longues, leurs carrières
  touchent davantage, quand leur pension par année validée est déjà trop haute
  au bas de l'échelle — 572 € au premier quintile pour 431, 997 € au deuxième
  pour 812.

**Ce qui reste** de l'étape, dans l'ordre : l'âge d'entrée des carrières
pleines selon la génération, sur la durée d'assurance que l'EIR mesure ; la
pension des femmes, trop haute par année validée au bas de l'échelle ; le
minimum selon la génération ; enfin, au propriétaire, la bascule de la page.
La dixième version reste en place, débrayable par sa constante.
