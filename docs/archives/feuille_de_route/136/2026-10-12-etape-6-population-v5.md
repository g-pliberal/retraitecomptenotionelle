# Étape 6, la population : les carrières courtes étalées sur la vie active, la cinquième version

**Le 12 octobre 2026 : les années validées d'une carrière courte ne sont plus
les premières, celles de la jeunesse, mais régulièrement espacées de l'entrée
à soixante ans, comme l'échantillon interrégimes de cotisants date celles de
tous les affiliés. Le minimum contributif passe sous l'EACR — 12,6 % des
liquidants de 2023 pour 18,8, les femmes à 18,7 % pour 25,2, les hommes à
4,7 % pour 12,2 — : bien datée, une carrière courte n'y va pas plus souvent
qu'une carrière de trente à quarante ans. La jeunesse tenait lieu de ce que la
population n'a pas, les années coupées des carrières intermittentes.**

Demande du propriétaire : « Reprise action 136 », sur la première chose qui
restait de l'étape : dater autrement les années des carrières courtes.

- *Ce que l'EIC en dit.* L'EIR ne date pas les années d'une carrière ;
  l'échantillon interrégimes de cotisants les date en moyenne, génération par
  génération (DREES, « Les droits validés au cours de la carrière », données
  détaillées de l'EIC 2017 : les trimestres validés dans l'année, par
  génération, âge et sexe). Les femmes des générations 1946 à 1958 en
  valident en moyenne 2,84 par an de 25 à 29 ans et 2,79 de 50 à 54 (un
  rapport de 0,98), et en cotisent 2,23 puis 2,52 (1,13) ; les hommes, 3,23
  et 3,09 (0,96). Les femmes affiliées avant 23 ans, sans les arrivées
  tardives, de même : 3,12 et 3,01 (0,97). Datées de la jeunesse, les
  carrières courtes de la population faisaient valider de 50 à 54 ans 0,70
  femme pour une de 25 à 29 ans, et 0,85 homme : elles s'arrêtaient, quand
  celles de l'EIC continuent ou reviennent.
- *La forme* (`COURTES_ETALEES`, `annees_etalees`, `scripts/grille_large.py`).
  Chaque année validée d'une tranche courte tombe au milieu de sa part égale
  de l'étendue, de l'entrée du cas type à soixante ans (`AGE_FIN_ETALEMENT`),
  le premier âge de départ des générations de la grille : une carrière de
  cinq ans travaille à 24, 32, 40, 48 et 56 ans ; ses périodes assimilées
  sont au milieu de ses années, l'inactivité entre elles et jusqu'au départ.
  Le profil redevient plat : de 50 à 54 ans, 1,08 femme pour une de 25 à 29
  ans, et 0,98 homme. Seule la population la reçoit ; débrayée, la quatrième
  version se redonne carrière par carrière, et sa page au chiffre près.
- *Le minimum contributif* (`part_minimum_contributif.py`, en pour cent des
  liquidants, en euros de 2023 par mois) :

  | | 2019 | 2020 | 2021 | 2022 | 2023 | femmes 2023 | hommes 2023 | 2024 | femmes 2024 | minimum moyen, 2019-2023 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | quatrième version | 20,0 | 19,0 | 18,8 | 21,4 | 22,8 | 33,1 | 9,4 | 25,7 | 40,5 | 80 à 94 € |
  | cinquième version | 12,3 | 11,6 | 11,0 | 11,9 | 12,6 | 18,7 | 4,7 | 15,0 | 24,5 | 70 à 90 € |
  | EACR, alignés | 20,4 | 18,4 | 17,9 | 18,9 | 18,8 | 25,2 | 12,2 | 18,6 (estimée) | 24,1 | 134 à 139 € |

- *D'où vient la chute*, chez les liquidants de 2023 du régime général :
  étalée, une carrière courte ne touche plus le minimum qu'aussi souvent
  qu'une carrière de trente à quarante ans. Chez les femmes, moins de dix
  années validées passent de 91,5 à 29,5 %, de dix à vingt de 67,0 à 24,3 %,
  de vingt à trente de 48,3 à 29,5 %, de trente à quarante de 29,5 à 24,3 % ;
  chez les hommes, les trois tranches courtes, de 82,6, 40,0 et 20,9 % à
  5,9 % chacune — dans chacune, les mêmes carrières, que leur seul salaire y
  met. Le minimum ne dépend plus de la durée, mais du salaire : la pension et
  le minimum, proratisés l'un et l'autre, se comparent par le salaire annuel
  moyen, que des années pleines, à leur âge et au volume de leur âge,
  tiennent au-dessus du seuil.
- *Les pensions de 2020 contre l'EIR*, en euros par mois :

  | | moyenne | médiane | femmes, moyenne | femmes, médiane | femmes, premier décile | hommes, moyenne | hommes, médiane | Kolmogorov, femmes | Kolmogorov, hommes |
  |---|---|---|---|---|---|---|---|---|---|
  | EIR | 1 536 | 1 382 | 1 177 | 1 013 | 283 | 1 957 | 1 745 | | |
  | quatrième version | 1 454 | 1 302 | 1 200 | 1 087 | 409 | 1 692 | 1 479 | −11,9 pt à 900 | +12,3 pt à 1 700 |
  | cinquième version | 1 468 | 1 308 | 1 224 | 1 153 | 440 | 1 701 | 1 482 | −13,6 pt à 800 | +12,0 pt à 1 400 |

  Les femmes s'éloignent de l'EIR par le bas de leur distribution, déjà trop
  haut ; les hommes ne bougent guère.
- *Sur la page*, contre celle du jour, les deux versions sur les mêmes
  données : l'écart des années observées passe de −1,02 et −2,87 points à
  −0,94 et −2,64 ; la part du PIB en 2070, au scénario 3, de +0,44 à +0,07
  point, à la proposition de −0,18 à −0,33 ; son solde moyen de 2026 à 2070,
  de +0,22 à +0,30 ; la garantie, de +0,098 à +0,104 point ; le passé refait,
  au pire depuis 2000, de 11,9 à 11,5 %.
- *Ce que la mesure accuse.* L'EIC contredit la jeunesse, et l'étalement la
  corrige ; mais la quatrième version tombait juste sur le minimum de 2019 à
  2021 par deux erreurs qui se compensaient : des années mal datées, et des
  années trop pleines. Une carrière courte est intermittente : ses trimestres
  viennent d'années coupées, que le salaire annuel moyen compte chacune pour
  une, et que le volume de la jeunesse, 0,53 de l'année, imitait. La
  population paie ses années à la part que l'INSEE mesure à leur âge, la
  moyenne de tous les salariés, dont la note du volume disait déjà qu'elle ne
  dit pas « si les années coupées reviennent aux mêmes ». Et les parts du
  stock en cachent une partie : les liquidants de 2019 à 2023, nés de 1952 à
  1961, ont moins de carrières courtes que les retraités dont la population
  tire ses parts — l'EIR de la génération 1953 compte 23,5 % de femmes sous
  trente années validées hors majorations, pour 33,7 % de tous les retraités
  de 2020 (8,5 et 11,5 % d'hommes), et 30,6 % de femmes au minimum de leur
  régime principal, pour 38,5 % ; à leurs parts, l'écart serait plus grand
  encore.

**Ce qui reste** de l'étape, dans l'ordre : le volume des années des carrières
courtes, leurs années coupées, à chercher et certifier ; la pension des
hommes, sous l'EIR ; un bas d'échelle plus fin ; enfin, au propriétaire, la
bascule de la page. L'étalement reste en place, débrayable par sa constante.
