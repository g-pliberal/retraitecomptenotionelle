# Étape 6, la population : le niveau du bas, contre la DG Trésor et les minima de l'EIR

**Le 12 octobre 2026 : le bas de l'échelle se resserre en carrière comme le
milieu. Six ans plus tard, les salariés payés au voisinage du Smic gagnent, au
milieu, ce que le resserrement prédit, à 3 % près : le resserrement reste, et
le niveau du bas avec lui. Ce qui manque au minimum est ailleurs.
Rangée comme l'EIR range les retraités, la population met ses minima de
pension au premier quintile de la pension en équivalent carrière complète,
quand l'EIR en met presque autant au deuxième : 59,9 % des femmes de ce
quintile y sont au minimum, 12,5 % dans la population. La population ne
change pas.**

Demande du propriétaire : « Fait l'étape suivante » — le niveau du bas : « le
resserrement en carrière y est-il le même qu'au milieu ? La persistance de la
DG Trésor, bande par bande, en est la mesure » (note de la septième version).

- *La persistance, refaite dans la population* (essai, hors du dépôt). Les
  carrières du salariat privé payées en 2007 de 0,80 à 1,05 Smic en équivalent
  temps plein, chaque âge de 18 à 65 ans pesant autant, et leur bande en 2013,
  en emploi et sous 60 ans ; hors du champ, en pour cent de tous, les bandes
  en pour cent de ceux qui y restent (`persistance_smic.csv`) :

  | | hors du champ | voisinage | 1,05 à 1,10 | 1,10 à 1,30 | 1,30 à 1,60 | plus de 1,60 |
  |---|---|---|---|---|---|---|
  | femmes, population | 54,1 | 76,1 | 9,6 | 14,3 | 0 | 0 |
  | femmes, DG Trésor | 40,5 | 22,4 | 15,2 | 34,8 | 17,7 | 9,9 |
  | hommes, population | 28,3 | 49,6 | 11,4 | 39,1 | 0 | 0 |
  | hommes, DG Trésor | 42,0 | 13,5 | 10,0 | 33,7 | 25,4 | 17,4 |
  | 35 à 49 ans, population | 35,0 | 100 | 0 | 0 | 0 | 0 |
  | 35 à 49 ans, DG Trésor | 37,7 | 25,0 | 16,9 | 34,0 | 16,2 | 7,9 |

  La table ne se compare pas bande par bande. Les carrières de la population
  sont des trajectoires lisses, chacune au niveau de sa classe : au voisinage
  du Smic à 35-49 ans, il n'y a que la part payée le Smic toute la carrière,
  qui y reste ; les autres classes n'y passent qu'en début de carrière, et en
  montent sur leur profil. La DG Trésor y voit les chocs transitoires d'une
  année, que le resserrement efface.
- *Ce qu'elle mesure : le resserrement au bas.* Qui est payé le Smic dans la
  coupe d'une année a pour salaire de carrière attendu la médiane, fois le Smic
  rapporté à elle à la puissance de la part de la variance qu'une carrière
  garde : 0,58 tous âges (0,76 au carré), 0,75 à âge donné. Six ans plus tard,
  les chocs passés, c'est le niveau qu'il retrouve. La médiane de la DG Trésor,
  les bandes interpolées, contre ce que prédit la coupe de 2007
  (`dispersion_salaires.csv`, `dispersion_salaires_sexe.csv`,
  `profil_salaire_age.csv`, le Smic rapporté au salaire moyen) :

  | | médiane de la coupe | prédit | DG Trésor | resserrement implicite |
  |---|---|---|---|---|
  | tous âges | 1,53 Smic | 1,20 | 1,20 | 0,75 |
  | femmes | 1,40 | 1,15 | 1,17 | 0,73 |
  | hommes | 1,60 | 1,22 | 1,26 | 0,72 |
  | 35 à 49 ans | 1,66 | 1,14 | 1,15 | 0,75 |

  Le bas se resserre comme le milieu, les hommes un peu plus : la persistance
  ne demande pas d'abaisser le bas, elle confirme son niveau. Le commentaire
  de `DISPERSION_DE_CARRIERE` le dit ; la coupe de 2013 donne les mêmes
  chiffres, à un centième près.
- *La part au minimum de pension, quintile par quintile*
  (`grille_large.py --grille population --distribution`) : la confrontation à
  l'EIR range aussi les carrières au minimum contributif, au minimum garanti
  ou à la pension majorée de référence ; l'EIR, au minimum de leur régime
  principal. En pour cent des retraités de 2020 de chaque quintile :

  | | q1 | q2 | q3 | q4 | q5 | ensemble |
  |---|---|---|---|---|---|---|
  | femmes, EIR | 64,3 | 59,9 | 18,4 | 9,9 | 1,1 | 38,5 |
  | femmes, population | 72,4 | 12,5 | 18,0 | 3,2 | 0,0 | 28,7 |
  | hommes, EIR | 51,5 | 32,6 | 6,2 | 3,9 | 0,4 | 12,4 |
  | hommes, population | 65,8 | 12,8 | 23,1 | 0,0 | 0,0 | 13,7 |

  Au deuxième quintile, de 1 006 à 1 319 € par mois dans la population, elle
  met des carrières longues payées au milieu de l'échelle : chez les femmes,
  40 % de salariées du privé de la classe médiane, aucune au minimum ; chez
  les hommes, 40 % de la classe du vingt-cinquième centile et 26 % de celle du
  bas, à 1 et 16 % au minimum. Ses minima de femmes du deuxième quintile sont
  ceux des fonctionnaires.
- *Ce que la mesure accuse : la convention de la sixième version.* Le deuxième
  quintile de l'EIR est, pour moitié, celui des carrières presque complètes au
  minimum : une pension moyenne de 818 € pour 87,6 % de proratisation, de
  l'ordre de 930 € en
  équivalent carrière complète, le minimum contributif et la complémentaire
  d'une carrière au Smic. La sixième version lit le rang du salaire dans le
  quintile, chaque quintile une bande de rangs (`association_rang_duree`). Or
  le quintile d'un retraité au minimum dit son minimum, non son salaire : les
  longues carrières que le minimum relève au deuxième quintile, elle les a
  payées comme les rangs de ce quintile, trop haut pour le minimum. La
  population y met des carrières du milieu de l'échelle, sans minimum, et des
  bornes plus hautes.

**Ce qui reste** de l'étape, dans l'ordre : le rang selon la durée, corrigé du
minimum — les retraités au minimum de chaque quintile, à la part que l'EIR
publie, rangés au bas de l'échelle et non dans la bande de leur quintile — ;
les pensions des femmes, au-dessus de l'EIR au milieu de leur distribution, et
celles des hommes, en dessous ; enfin, au propriétaire, la bascule de la page.
