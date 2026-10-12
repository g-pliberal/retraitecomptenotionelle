# Étape 6, la population : la seconde version, trois corrections mesurées une à une

**Le 11 octobre 2026 : la population reçoit trois corrections, chacune fondée
sur un fait ou une source et débrayable pour en mesurer l'effet. Elle rapproche
les pensions de 2020 de l'EIR, mais éloigne le minimum contributif de l'EACR :
le bas de l'échelle de la première version tenait lieu de ce que la
population n'a pas encore, des carrières durablement au Smic et un volume de
travail.**

Demande du propriétaire : « vas-y, fais la version 2 », sur les deux points
que la première version laissait — une dispersion de carrière, des parts par
génération.

- *Une dispersion de CARRIÈRE* (`DISPERSION_DE_CARRIERE`, 0,76). La coupe de
  l'année, tous âges, compte l'âge, que le profil de carrière du modèle porte
  déjà : 23 % de la variance du logarithme du salaire en 2024, d'après le
  profil par âge et les centiles certifiés, chaque tranche d'âge pesée de sa
  largeur. Et des chocs transitoires, qu'une carrière efface : pour le salaire
  journalier des hommes du privé de 36 à 54 ans, un cinquième à trois
  dixièmes de ce qui reste (Ceci-Renaud, Charnoz et Gaini, « Évolutions de la
  volatilité des revenus salariaux du secteur privé en France depuis 1968 »,
  Insee, document de travail G 2014/03, tableau 6 ; pour le revenu salarial
  annuel, au moins un tiers). Une carrière en garde les trois quarts de 77 % :
  chaque écart au centre du logarithme est ramené à 0,76 fois le sien, la
  moyenne de chaque sexe gardée (`resserrer`). Pour la génération 1955, le
  centile 10 des femmes passe de 0,43 à 0,51 fois le salaire moyen, le
  centile 99 des hommes de 4,29 à 3,17.
- *Aucun temps complet sous le Smic* (`PLANCHER_SMIC`). Le centile 10 des
  femmes était payé 0,43 fois le salaire moyen pour la génération 1950, quand
  le Smic en valait 0,535 : une carrière dont le rang tombe sous le Smic,
  l'année où sa génération a 45 ans, est désormais payée le Smic de chaque
  année. Après le resserrement, cela ne touche plus que le centile 10 des
  femmes des générations nées jusque vers 1950.
- *Les carrières courtes à la part de tous* (`COURTES_A_LA_PART_DE_TOUS`). La
  grille donnait aux régimes non statutaires la part de carrières courtes que
  l'EIR donne à tous les retraités ; les régimes statutaires n'en ayant pas,
  la population comptait 26,9 % de femmes sous trente années validées, pour
  33,7 % dans l'EIR. Les autres régimes en portent désormais d'autant plus, et
  la composition redonne celle de l'EIR, 33,7 % des femmes et 11,5 % des
  hommes, la durée moyenne tombant à 30,6 et 36,3 années (32,0 et 39,0 dans
  l'EIR).
- *Les parts par génération, laissées.* La durée moyenne des générations
  (`duree_assurance_generations.csv`) ne pourrait passer que par la durée des
  carrières courtes, les poids d'une grille ne dépendant pas de la
  génération ; ce détour n'a pas été pris.
- *Le minimum contributif, correction par correction*
  (`part_minimum_contributif.py`, la première version redonnée au chiffre
  près ; en pour cent des liquidants, en euros de 2023 par mois) :

  | | 2019 | 2023 | femmes 2023 | hommes 2023 | 2024 | minimum moyen, 2019-2023 |
  |---|---|---|---|---|---|---|
  | première version | 17,4 | 20,1 | 27,4 | 10,4 | 24,3 | 78 à 91 € |
  | avec le plancher au Smic | 17,4 | 18,3 | 24,3 | 10,4 | 27,8 | 67 à 77 € |
  | avec la dispersion de carrière | 10,6 | 12,6 | 18,5 | 4,7 | 14,2 | 60 à 72 € |
  | avec les carrières courtes | 18,7 | 22,1 | 29,8 | 12,0 | 27,1 | 80 à 93 € |
  | seconde version, les trois | 12,6 | 14,7 | 22,0 | 5,2 | 16,8 | 60 à 78 € |
  | EACR, alignés | 20,4 | 18,8 | 25,2 | 12,2 | 18,6 (estimée) | 134 à 139 € |

  La dispersion de carrière fait presque tout : elle remonte le bas de
  l'échelle au-dessus du seuil, et la part tombe sous l'observé, celle des
  hommes à moins de la moitié. Le saut de la réforme de 2023 n'est plus que de
  2,1 points, entre l'estimation de l'EACR (−0,5) et TRAJECTOiRE (+4,3). Le
  minimum moyen ne remonte dans aucune version.
- *Les pensions de 2020 contre l'EIR* (`grille_large.py --grille population`),
  en euros par mois, la première version entre parenthèses :

  | | moyenne | d1 | médiane | d9 | Kolmogorov |
  |---|---|---|---|---|---|
  | EIR, ensemble | 1 536 | 402 | 1 382 | 2 730 | |
  | population | 1 488 (1 488) | 521 (582) | 1 322 (1 265) | 2 543 (2 532) | −7,2 pt à 900 € (−7,4 à 800) |
  | EIR, femmes | 1 177 | 283 | 1 013 | 2 229 | |
  | population | 1 229 (1 275) | 410 (427) | 1 158 (1 153) | 2 042 (2 217) | −12,3 à 900 (−14,4 à 800) |
  | EIR, hommes | 1 957 | 872 | 1 745 | 3 242 | |
  | population | 1 741 (1 715) | 785 (805) | 1 547 (1 389) | 2 848 (3 028) | +8,4 à 1 600 (+16,6 à 1 300) |

  La médiane des hommes se rapproche de 158 €, leur écart de Kolmogorov est
  divisé par deux ; les femmes ne touchent plus que 4 % de trop, et l'écart
  des pensions des sexes passe de 26 à 29 %, pour 40 dans l'EIR. Le haut,
  resserré lui aussi, s'éloigne : le neuvième décile des hommes perd 180 €.
  Les femmes ne font plus que 49,4 % des retraités de 2020 dans la
  population, pour 51,6 % : plus de carrières courtes, ce sont plus de femmes
  qui attendent l'âge du taux plein.
- *Ce que la page en dirait*, contre la page du jour : l'écart des années
  observées, −1,43 et −3,00 points ; la part du PIB en 2070, −0,02 point à la
  proposition ; son solde moyen de 2026 à 2070, de −0,89 à −0,79 ; la
  garantie en 2070, +0,089 point ; le passé refait, au pire depuis 2000, à
  12,5 %.
- *Ce que la mesure accuse.* Les deux validations ne disent plus la même
  chose : la dispersion de carrière, sourcée, rapproche les pensions et
  éloigne le minimum. Resserrée uniformément, la distribution met le centile
  10 des hommes à 0,62 fois le salaire moyen, bien au-dessus du Smic : il n'y
  a plus d'homme au Smic toute sa carrière, quand le minimum en vit, et les
  bénéficiaires restants — temps partiels, carrières courtes — ne reçoivent
  que de petits compléments. Le bas de la première version, la coupe de
  l'année entière, tenait lieu de deux choses que la population n'a pas : la
  persistance au Smic, dont aucune source certifiée ne dit la part par sexe ni
  la durée, et le volume de travail des carrières du bas — temps partiel et
  années incomplètes, que le revenu salarial de l'INSEE mesure en moyenne
  (0,74 année d'équivalent temps plein pour les femmes, 0,79 pour les hommes,
  en 2023) sans dire sur qui il pèse.

**Ce qui reste** de l'étape, dans l'ordre : le bas de l'échelle — la part des
salariés au Smic par sexe et leur persistance, le volume de travail des
carrières du bas, à chercher et certifier — ; puis la mesure ; enfin, au
propriétaire, la bascule de la page. Les trois corrections se débrayent par
leurs constantes : la première version se redonne au chiffre près.
