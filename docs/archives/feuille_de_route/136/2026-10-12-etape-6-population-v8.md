# Étape 6, la population : les retraités au minimum rangés au premier quintile, la huitième version

**Le 12 octobre 2026 : les retraités que l'EIR trouve au minimum lisent
désormais leur rang de salaire au premier quintile, non au leur. Les longues
carrières de femmes descendent dans la classe du bas, les courtes en
remontent : au premier quintile de la pension en équivalent carrière
complète, les femmes de moins de dix années validées passent de 94,1 à
87,1 % (80,5 dans l'EIR). Mais le minimum contributif ne bouge pas, 13,6 %
des liquidants de 2023 : ce n'est pas le rang des longues carrières qui le
retient, c'est la profondeur du bas. Ses bénéficiaires reçoivent 62 à 78 €
par mois, quand l'EACR en compte 134 à 139. Le volume de travail selon le
rang, essayé sur cette version, porte le minimum de 2023 à 17,2 % (EACR
18,8).**

Demande du propriétaire : « Fait l'étape suivante » — le rang selon la durée,
corrigé du minimum : « les retraités au minimum de chaque quintile, à la part
que l'EIR publie, rangés au bas de l'échelle et non dans la bande de leur
quintile » (note du niveau du bas).

- *La forme* (`MINIMUM_AU_PREMIER_QUINTILE`, `association_rang_duree`,
  `scripts/grille_large.py`). La sixième version lit le rang de salaire de
  chaque tranche de durée dans les quintiles de la pension en équivalent
  carrière complète, chaque quintile une bande de rangs. La part de chaque
  quintile que l'EIR trouve au minimum de pension de son régime principal
  quitte désormais sa bande pour celle du premier, avec ses tranches : le
  minimum contributif ne relève que la pension d'un salaire annuel moyen
  inférieur au double de son montant, et le quintile d'un retraité au minimum
  dit le minimum, non son salaire. Une convention : au minimum ou non, les
  retraités d'un quintile ont les mêmes tranches de durée, que l'EIR ne croise
  pas avec le minimum. La bande du bas passe de 29,2 à 48,9 % des rangs des
  femmes, de 9,7 à 17,0 % de ceux des hommes ; calée comme avant sur les
  marges de la population, la classe du bas prend, en part de chaque tranche :

  | | moins de 10 ans | 10 à 20 | 20 à 30 | 30 à 40 | 40 et plus |
  |---|---|---|---|---|---|
  | femmes, septième version | 45,0 | 32,8 | 22,3 | 8,6 | 4,5 |
  | femmes, huitième | 31,5 | 26,4 | 21,5 | 12,6 | 9,3 |
  | hommes, septième version | 80,5 | 49,4 | 38,5 | 15,7 | 9,4 |
  | hommes, huitième | 78,2 | 48,1 | 36,6 | 15,4 | 10,0 |

  Les longues carrières de femmes descendent, les courtes montent à la classe
  médiane ; les hommes, peu au minimum hors du premier quintile, ne bougent
  guère. Un test tient la forme ; débrayée, la septième version se redonne.
- *Le minimum contributif* (`part_minimum_contributif.py`, en pour cent des
  liquidants, en euros de 2023 par mois) :

  | | 2019 | 2020 | 2021 | 2022 | 2023 | femmes 2023 | hommes 2023 | 2024 | hommes, 2019 à 2024 | minimum moyen, 2019-2023 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | septième version | 13,3 | 12,2 | 11,8 | 13,3 | 13,6 | 19,8 | 5,5 | 16,3 | 5,5 à 5,9 | 59 à 74 € |
  | huitième version | 13,4 | 12,4 | 11,9 | 13,3 | 13,6 | 19,8 | 5,5 | 16,1 | 5,5 à 5,9 | 62 à 78 € |
  | huitième, volume selon le rang (essai) | 15,6 | 14,7 | 14,9 | 16,1 | 17,2 | 22,6 | 10,1 | 21,8 | 9,0 à 11,8 | 73 à 90 € |
  | EACR, alignés | 20,4 | 18,4 | 17,9 | 18,9 | 18,8 | 25,2 | 12,2 | 18,6 (estimée) | 12,2 à 12,7, de 2022 | 134 à 139 € |

- *La part au minimum de pension, quintile par quintile*
  (`grille_large.py --grille population`), en pour cent des retraités de 2020
  de chaque quintile :

  | | q1 | q2 | q3 | q4 | q5 | ensemble |
  |---|---|---|---|---|---|---|
  | femmes, EIR | 64,3 | 59,9 | 18,4 | 9,9 | 1,1 | 38,5 |
  | femmes, septième version | 72,4 | 12,5 | 18,0 | 3,2 | 0,0 | 28,7 |
  | femmes, huitième | 72,5 | 13,6 | 18,2 | 3,2 | 0,0 | 29,1 |
  | hommes, EIR | 51,5 | 32,6 | 6,2 | 3,9 | 0,4 | 12,4 |
  | hommes, septième version | 65,8 | 12,8 | 23,1 | 0,0 | 0,0 | 13,7 |
  | hommes, huitième | 66,0 | 13,5 | 22,5 | 0,0 | 0,0 | 13,6 |

  Les bornes des quintiles restent à 1 003, 1 319, 1 630 et 2 129 € par mois,
  pour 1 006, 1 319, 1 630 et 2 131.
- *Le reste*, contre la septième version. Au premier quintile, la part de
  chaque tranche de durée :

  | | moins de 10 ans | 10 à 20 | 20 à 30 | 30 à 40 | 40 et plus |
  |---|---|---|---|---|---|
  | femmes, EIR | 80,5 | 62,0 | 44,2 | 18,5 | 10,1 |
  | femmes, septième version | 94,1 | 69,4 | 50,7 | 19,5 | 9,9 |
  | femmes, huitième | 87,1 | 64,9 | 50,1 | 20,5 | 12,2 |
  | hommes, EIR | 74,0 | 42,9 | 29,8 | 9,9 | 3,7 |
  | hommes, septième version | 60,5 | 36,6 | 13,1 | 6,7 | 8,3 |
  | hommes, huitième | 59,1 | 33,3 | 12,4 | 6,3 | 8,3 |

  L'écart moyen des dix cases passe de 7,3 à 7,0 points : celui des femmes
  baisse d'un tiers, de 5,7 à 3,9, celui des hommes monte de 8,9 à 10,0. Les
  pensions de 2020 bougent peu : le troisième décile des femmes descend de
  881 à 865 € (703 dans l'EIR), leur plus grand écart à l'EIR de 13,8 à
  12,8 points ; le troisième décile des hommes, de 1 238 à 1 228 € (1 374).
  Sur la page, rien ne bouge au-delà d'un centième de point.
- *Ce que la mesure accuse.* La note du niveau du bas attendait le minimum
  au deuxième quintile des longues carrières descendues : il n'y vient pas.
  Le minimum ne bouge ni en part ni guère en montant : ses bénéficiaires ne
  reçoivent toujours que la moitié du minimum moyen de l'EACR. Il se joue
  sur ce que contiennent les années du bas, non sur le rang de qui y tombe.
  La variante de la quatrième version, débrayée depuis
  (`VOLUME_SELON_LE_RANG`), donne à chaque classe le volume de travail de sa
  catégorie, au bas celui des employés et des ouvriers, 0,88 et 0,95 de celui
  de tous : essayée sur la huitième version
  (hors du dépôt, la constante embrayée pour la seule mesure), elle porte le
  minimum de 2023 à 17,2 %, celui des hommes de 5,5 à 10,1 %, et le minimum
  moyen à 73 à 90 € ; mais celui de 2024 à 21,8 %, au-dessus de l'EACR. En
  quatrième version, elle abaissait aussi la pension des hommes, déjà sous
  l'EIR ; c'est à remesurer.

**Ce qui reste** de l'étape, dans l'ordre : le volume selon le rang, remesuré
sur la huitième version — le minimum, les pensions, la page — ; les pensions
des femmes, au-dessus de l'EIR du bas au milieu de leur distribution, et
celles des hommes, en dessous ; enfin, au propriétaire, la bascule de la page.
La huitième version reste en place, débrayable par sa constante.
