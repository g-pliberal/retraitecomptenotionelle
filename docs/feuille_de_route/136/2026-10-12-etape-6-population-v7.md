# Étape 6, la population : le bas de l'échelle décliné, la septième version

**Le 12 octobre 2026 : le reste de la classe du bas — 17,5 % des carrières
du salariat privé, moins la part payée le Smic toute la carrière — ne tient
plus sous un seul niveau, mais se décline en quatre sous-classes de rang. Le
seuil du minimum contributif ne la fait plus basculer d'un bloc : la part des
hommes au minimum ne saute plus d'une année à l'autre. Mais le minimum ne
monte guère, 13,6 % des liquidants de 2023 pour 13,4 : la plus basse des
sous-classes des hommes est encore payée 1,10 à 1,18 Smic, au-dessus du
seuil. Ce qui manque est le niveau du bas, non sa finesse.**

Demande du propriétaire : « Fait l'étape suivante » — un bas d'échelle plus
fin, sous la classe du bas, celui que le minimum demande ; la note de la
troisième version le voulait tel qu'il « ne fasse plus basculer une classe
entière d'un côté du seuil ».

- *Ce qui le demandait.* Une variante d'essai, hors du dépôt : le reste de la
  classe du bas abaissé d'un dixième, la part des hommes au minimum passe, en
  2023, de 4,9 à 9,9 %, celle de tous les liquidants de 13,4 à 15,7 %. Le
  seuil tombe dans la classe, dont le reste est payé, pour les hommes des
  générations 1950 à 1975, de 1,19 à 1,26 Smic ; tout se joue sur un niveau.
- *La forme* (`SOUS_CLASSES_DU_BAS`, `ecarts_du_bas`, `sous_classes_du_bas`,
  `scripts/grille_large.py`). Le reste de la classe couvre les rangs de la
  coupe de l'année de la part payée le Smic toute la carrière au haut de la
  classe ; quatre sous-classes s'en partagent les rangs à parts égales, chacune
  au niveau que la coupe donne au milieu des siens — au logarithme, la droite
  des deux premiers centiles, prolongée sous le premier comme dans
  `part_de_la_coupe_sous` —, son écart resserré en carrière comme celui des
  classes, la moyenne du reste gardée : la masse des salaires ne bouge pas.
  Pour la génération 1960, les hommes vont de 1,18 à 1,34 Smic, au lieu de
  1,26 ; les femmes de 0,96 à 1,08, les deux premières payées au Smic. Le
  plancher et la part au Smic toute la carrière restent ce qu'ils étaient. Un
  test tient la déclinaison ; débrayée, la sixième version se redonne
  carrière par carrière. La population compte 766 carrières au lieu de 706.
- *Le minimum contributif* (`part_minimum_contributif.py`, en pour cent des
  liquidants, en euros de 2023 par mois) :

  | | 2019 | 2020 | 2021 | 2022 | 2023 | femmes 2023 | hommes 2023 | 2024 | hommes, 2019 à 2024 | minimum moyen, 2019-2023 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | sixième version | 13,3 | 12,2 | 11,8 | 12,5 | 13,4 | 19,9 | 4,9 | 15,8 | 4,5 à 5,9 | 59 à 74 € |
  | septième version | 13,3 | 12,2 | 11,8 | 13,3 | 13,6 | 19,8 | 5,5 | 16,3 | 5,5 à 5,9 | 59 à 74 € |
  | EACR, alignés | 20,4 | 18,4 | 17,9 | 18,9 | 18,8 | 25,2 | 12,2 | 18,6 (estimée) | 12,2 à 12,7, de 2022 | 134 à 139 € |

  La marche des hommes de 2022 à 2024 — 5,9 % en 2020, 4,5 % en 2022 — est
  passée : une classe entière qui franchissait le seuil.
- *Le reste*, contre la sixième version : les pensions de 2020 bougent de
  quelques euros (la médiane des hommes reste à 1 574 €, celle des femmes à
  1 219 €) ; au premier quintile de la pension en équivalent carrière
  complète, les hommes de moins de dix ans passent de 67,9 à 60,5 % (74,0
  dans l'EIR), les sous-classes hautes du reste en sortant, et l'écart moyen
  des dix cases de 6,5 à 7,3 points ; sur la page, rien ne bouge au-delà d'un
  centième de point.
- *Ce que la mesure accuse.* La finesse du bas rend le minimum robuste, non
  juste. Il se joue sur le niveau du bas, que le resserrement en carrière
  porte, pour les hommes, d'une coupe dont le dixième centile est au Smic à
  une classe payée un cinquième à un quart au-dessus. La DG Trésor, sur les
  mêmes salariés, dit l'inverse au bas : des hommes payés au voisinage du Smic
  en 2007 et restés salariés du privé, 13 % y sont encore six ans plus tard
  et 10 % de plus sous 1,10 Smic (`persistance_smic.csv`) — quand la
  population n'en garde au Smic que la première part, et paie tout le reste
  1,10 Smic au moins.

**Ce qui reste** de l'étape, dans l'ordre : le niveau du bas — le resserrement
en carrière y est-il le même qu'au milieu ? La persistance de la DG Trésor,
bande par bande, en est la mesure — ; les pensions des femmes, au-dessus de
l'EIR au milieu de leur distribution, et celles des hommes, en dessous ;
enfin, au propriétaire, la bascule de la page. Les sous-classes du bas restent
en place, débrayables par leur constante.
