# Étape 6, la population : le rang de salaire selon la durée, la sixième version

**Le 12 octobre 2026 : chaque tranche de durée prend les classes de salaire de
son sexe dans la proportion que l'EIR lui mesure, calée sur les marges de la
population ; et la mesure range désormais chaque grille par quintile de sa
pension en équivalent carrière complète. Les carrières courtes tombent où
l'EIR les met : l'écart moyen des dix cases du premier quintile passe de 15,6
à 6,5 points. Mais le minimum contributif ne bouge guère, 13,4 % des
liquidants de 2023 pour 18,8 : le rang le déplace des carrières longues vers
les courtes sans en changer la somme, que fixe le niveau du bas de l'échelle.**

Demande du propriétaire : « Fait l'étape suivante » — donner aux carrières
courtes le gain par année que l'EIR leur mesure, calé sur les quintiles en
équivalent carrière complète certifiés le même jour.

- *La forme* (`RANG_SELON_LA_DUREE`, `association_rang_duree`, `caler`,
  `rangs_selon_la_duree`, `scripts/grille_large.py`). Chaque quintile de
  l'EIR est lu comme une bande de rangs du sexe, de la largeur de sa part des
  retraités du sexe ; une classe de centiles reçoit, de la masse d'une tranche
  dans chaque bande, la part de ses rangs qui y tombe. Le tableau croisé qui
  en sort redonne le poids de chaque classe dans l'EIR ; la population, qui ne
  met ses carrières courtes que hors des régimes statutaires, en a davantage
  (10,5 % des femmes du privé à moins de dix ans, pour 8,4 %). Le tableau est
  donc calé, par la méthode des marges, sur les parts des tranches de la
  population et le poids des classes : la distribution des salaires de chaque
  sexe ne bouge pas, et ses rapports croisés — la façon dont la durée et le
  rang vont ensemble — restent ceux de l'EIR. Les femmes de moins de dix ans
  sont à 45,0 % dans la classe du bas (48,2 % dans le tableau de l'EIR), celles
  de quarante ans et plus à 4,5 % ; les hommes de moins de dix ans à 80,5 %
  (83,0 %). La part de la classe du bas payée le Smic toute la carrière la
  suit, et reste de 6,35 % des femmes du privé. Les artisans, les
  contractuels, les exploitants et les libéraux, qui ont aussi des tranches,
  prennent les mêmes poids. Débrayée, la cinquième version se redonne
  carrière par carrière.
- *La mesure* (`eqcc`, `proratisations`, `confronter_eqcc`). Celle de la
  note précédente, entrée au script : chaque cohorte de 2020 à sa pension,
  divisée par sa durée d'assurance tous régimes, enfants compris, rapportée à
  la durée requise et bornée à un ; les quintiles en têtes, les deux sexes
  réunis ; la part de chaque tranche au premier, contre l'EIR. Les carrières
  statutaires s'y rangent à leur durée, si bien que les chiffres de la
  cinquième version y changent un peu. `grille_large.py` l'imprime après la
  distribution, et `--distribution` aussi. Quatre tests tiennent le rang
  et la mesure (`tests/test_grille_large.py`).
- *Le premier quintile*, en pour cent de chaque tranche :

  | | femmes, moins de 10 ans | 10 à 20 | 20 à 30 | 30 à 40 | 40 et plus | hommes, moins de 10 ans | 10 à 20 | 20 à 30 | 30 à 40 | 40 et plus |
  |---|---|---|---|---|---|---|---|---|---|---|
  | EIR | 80,5 | 62,0 | 44,2 | 18,5 | 10,1 | 74,0 | 42,9 | 29,8 | 9,9 | 3,7 |
  | cinquième version | 64,2 | 47,3 | 41,4 | 27,5 | 19,3 | 21,7 | 20,0 | 9,8 | 6,7 | 9,3 |
  | sixième version | 94,1 | 69,4 | 50,7 | 19,5 | 9,9 | 67,9 | 38,4 | 12,0 | 6,4 | 8,2 |

  Les femmes de moins de dix ans y descendent trop, les hommes de vingt à
  trente ans pas assez.
- *Le minimum contributif* (`part_minimum_contributif.py`, en pour cent des
  liquidants, en euros de 2023 par mois) :

  | | 2019 | 2020 | 2021 | 2022 | 2023 | femmes 2023 | hommes 2023 | 2024 | femmes 2024 | minimum moyen, 2019-2023 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | cinquième version | 12,3 | 11,6 | 11,0 | 11,9 | 12,6 | 18,7 | 4,7 | 15,0 | 24,5 | 70 à 90 € |
  | sixième version | 13,3 | 12,2 | 11,8 | 12,5 | 13,4 | 19,9 | 4,9 | 15,8 | 26,1 | 59 à 74 € |
  | EACR, alignés | 20,4 | 18,4 | 17,9 | 18,9 | 18,8 | 25,2 | 12,2 | 18,6 (estimée) | 24,1 | 134 à 139 € |

- *D'où vient qu'il bouge si peu*, chez les liquidants de 2023 : le rang
  déplace le minimum d'une tranche à l'autre. Chez les femmes, moins de dix
  années validées passent de 29,5 à 57,4 % au minimum, de dix à vingt de 24,3
  à 41,5 %, de vingt à trente de 29,5 à 35,8 %, quand celles de trente à
  quarante descendent de 24,3 à 14,3 % et celles de quarante et plus de 4,8 à
  2,3 % ; chez les hommes, les trois tranches courtes montent de 5,9 % à 14,3,
  10,5 et 8,9 %, les longues baissent un peu. La distribution des salaires de
  chaque sexe étant gardée, la somme dépend de son bas : hors la part payée le
  Smic toute la carrière, la classe du bas des hommes l'est à 0,63 à 0,66 fois
  le salaire moyen, soit un quart au-dessus du Smic, pour les générations 1950
  à 1960, et passe le seuil ; celle des femmes l'est au Smic. Les compléments,
  servis à des carrières plus courtes, baissent encore.
- *Les pensions de 2020 contre l'EIR*, en euros par mois :

  | | moyenne | médiane | femmes, moyenne | femmes, médiane | femmes, premier décile | hommes, moyenne | hommes, médiane | hommes, premier décile | Kolmogorov, femmes | Kolmogorov, hommes |
  |---|---|---|---|---|---|---|---|---|---|---|
  | EIR | 1 536 | 1 382 | 1 177 | 1 013 | 283 | 1 957 | 1 745 | 872 | | |
  | cinquième version | 1 468 | 1 308 | 1 224 | 1 153 | 440 | 1 701 | 1 482 | 825 | −13,6 pt à 800 | +12,0 pt à 1 400 |
  | sixième version | 1 503 | 1 362 | 1 276 | 1 219 | 417 | 1 723 | 1 574 | 749 | −13,8 pt à 900 | +9,7 pt à 1 800 |

  L'ensemble et les hommes se rapprochent de l'EIR, sauf le premier décile
  des hommes ; les femmes s'en éloignent : leurs carrières longues, montées dans l'échelle, touchent plus,
  quand le minimum retient les courtes de descendre.
- *Sur la page*, contre celle du jour, les deux versions sur les mêmes
  données : l'écart des années observées passe de −0,94 et −2,64 points à
  −1,04 et −2,82 ; la part du PIB en 2070, au scénario 3, de +0,07 à +0,04
  point, à la proposition de −0,33 à −0,36 ; son solde moyen de 2026 à 2070,
  de +0,30 à +0,33 ; la garantie, de +0,104 à +0,102 point ; le passé refait,
  au pire depuis 2000, de 11,5 à 11,8 %.
- *Ce que la mesure accuse.* Le rang selon la durée est la pièce que l'EIR
  désignait : les carrières courtes vont au bas de l'échelle, les longues
  au-dessus, comme dans l'enquête. Il ne suffit pas au minimum, qui se joue
  sur le niveau du bas plus que sur qui l'occupe : la population n'a pas assez
  de carrières sous le seuil, et la classe du bas des hommes, resserrée en
  carrière, n'y descend pas. Les pensions des femmes, trop hautes au milieu de
  leur distribution — une médiane à 1 219 € pour 1 013 —, désignent l'autre
  bout.

**Ce qui reste** de l'étape, dans l'ordre : un bas d'échelle plus fin, sous la
classe du bas, celui que le minimum demande ; les pensions des femmes,
au-dessus de l'EIR au milieu de leur distribution, et celles des hommes,
en dessous ; enfin, au propriétaire, la bascule de la page. Le rang selon la
durée reste en place, débrayable par sa constante.
