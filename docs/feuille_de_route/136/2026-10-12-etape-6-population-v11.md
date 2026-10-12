# Étape 6, la population : les carrières pleines entrent selon leur génération, la onzième version

**Le 12 octobre 2026 : les carrières pleines du salariat privé commencent
désormais 44 années environ avant l'âge légal de leur génération — la durée
que l'EIR donne aux carrières de quarante ans et plus des retraités de 2020 —,
à 16 ans pour les générations parties à 60 ans, à 21 ans, comme avant, pour
celles qui partent à 64. Les hommes nés de 1938 à 1953 valident 37,5 à 37,9
années au lieu de 35,8 à 36,7 (40,4 à 40,6 dans l'EIR), ceux nés de 1954 à
1957 autant que dans l'EIR. Mais leur pension ne bouge pas : ces carrières
attendaient déjà la durée requise pour partir au taux plein, et elles partent
désormais plus tôt, non plus riches. Le passé refait gagne, lui : l'écart de
la projection à rebours à la dépense observée tombe de 12,7 à 10,9 % au pire
depuis 2000.**

Demande du propriétaire : « Fait la prochaine étape » — « l'âge d'entrée des
carrières pleines selon la génération, sur la durée d'assurance que l'EIR
mesure » (note de la dixième version).

- *La durée des carrières pleines* (`durees_pleines`,
  `scripts/grille_large.py`). L'EIR ne la publie pas ; elle se déduit de la
  durée validée moyenne hors majorations de chaque sexe, moins ce qu'en
  portent les tranches plus courtes, comptées à leur milieu, rapportée à la
  part de la tranche de quarante ans et plus
  (`caracteristiques_retraites.csv`) : 44,1 années pour les hommes, 44,0 pour
  les femmes. L'EIR arrondit ses durées moyennes à l'année : la mesure en
  tient à une année près. D'une génération à l'autre, elle suit la durée
  d'assurance des hommes autour de sa moyenne des générations certifiées
  (`duree_assurance_generations.csv`) — 44 années pour les générations 1940 à
  1958, 43 pour 1968, 42 pour 1980 à 2000 ; celle des femmes monte surtout de
  ce que leurs carrières courtes se raréfient, que la grille ne sait pas faire
  varier. - *La forme* (`ENTREE_SELON_LA_GENERATION`,
  `entrees_des_carrieres_pleines`, le champ `entrees` du cas type). La
  carrière pleine du salariat privé commence cette durée avant l'âge légal de
  sa génération (`age_ouverture_requis.csv`), à l'année près, et à 21 ans au
  plus tard : 16 ans pour les générations nées jusqu'en 1951, 17 de 1952 à
  1954, 18 jusqu'en 1961, 19 de 1962 à 1965, 20 en 1966 et 1967, 21 ensuite.
  Les années d'interruption, le temps partiel et le volume se comptent de
  cette entrée ; la part payée le Smic toute la carrière et les sous-classes
  du bas la suivent. Les tranches plus courtes et les autres groupes gardent
  leur entrée. Simulée, la carrière pleine d'un homme de la classe médiane
  valide 44,0 années, partie à 60 ans, pour la génération 1940, 43,5 partie à
  59 ans et demi pour 1950 — l'entrée à 16 ans lui ouvre la retraite anticipée
  des carrières longues —, 44,2 pour 1953, 44,0 pour 1960, 43,0 pour 1970, au
  lieu de 39 à 43. Un test tient la forme
  (`test_les_carrieres_pleines_entrent_selon_leur_generation`). - *Les années
  validées par génération*, contre la durée d'assurance que l'EIR mesure aux
  résidents (majorations comprises) :

  | | 1938 à 1941 | 1942 à 1945 | 1950 à 1953 | 1954 à 1957 |
  |---|---|---|---|---|
  | hommes, EIR | 40,5 | 40,4 | 40,6 | 40,9 |
  | hommes, dixième version | 35,8 | 36,3 | 36,7 | 39,3 |
  | hommes, onzième | 37,8 | 37,5 | 37,9 | 40,9 |
  | femmes, EIR | 33,2 | 34,8 | 38,9 | 40,8 |
  | femmes, dixième version | 33,7 | 33,7 | 33,8 | 39,4 |
  | femmes, onzième | 34,7 | 34,7 | 34,8 | 40,5 |

  Tous âges réunis, les hommes de 2020 valident 38,1 années au lieu de 36,6
  (40,0 dans l'EIR, qui compte aussi ceux de l'étranger), et 58,7 % ont
  quarante ans et plus, au lieu de 45,6 (72,0). - *Les pensions de 2020*
  bougent à peine. La médiane de tous passe de 1 366 à 1 379 € (1 382 dans
  l'EIR), le neuvième décile de 2 730 à 2 684 € ; celle des hommes de 1 622 à
  1 631 € (1 745), leur moyenne de 1 766 à 1 761 €, leur plus grand écart à
  l'EIR de 9,1 à 8,5 points ; celle des femmes reste à 1 237 € (1 013), leur
  moyenne passe de 1 303 à 1 312 €. Aux deux quintiles du haut de la pension
  en équivalent carrière complète, la proratisation des hommes reste à 94,4 et
  95,1 %, pour 100,0 et 98,5 dans l'EIR, et 60 % seulement y ont quarante ans
  et plus, pour 73 et 69 %. - *La pension en équivalent carrière complète.* Au
  premier quintile, l'écart moyen des dix cases de tranche redescend de 7,0 à
  6,4 points ; les femmes de quarante ans et plus y sont 13,5 %, au lieu de
  15,1 (10,1 dans l'EIR). Au minimum de pension, 31,6 % des femmes de 2020
  (38,5 dans l'EIR), 17,1 % des hommes (12,4). - *Le minimum contributif*
  (`part_minimum_contributif.py`) : 15,7 % des liquidants de 2023 au lieu de
  16,6 (EACR 18,8), les femmes à 21,8 % au lieu de 22,3 (25,2), les hommes à
  8,3 % au lieu de 8,9 (12,2) ; mais 22,6 % en 2024 au lieu de 20,4 (18,6
  estimée) — sans doute la majoration de la réforme de 2023, qui va aux
  carrières longuement cotisées ; le minimum moyen, 74 à 91 € de 2019 à 2023
  (134 à 139). - *Sur la page*, contre la dixième version : l'écart des années
  observées passe de −1,52 à −1,41 point au scénario 2, de −3,42 à −3,13 aux
  scénarios 4 et 6 ; la part du PIB en 2070, le solde moyen de 2026 à 2070 et
  les coefficients de 2070 ne bougent qu'au centième ; la garantie, de +0,088
  à +0,087 point. Le passé refait gagne : l'écart de 2009 passe de −12,6 à
  −9,3 %, le pire depuis 2000 de 12,7 à 10,9 % — les générations 1945 à 1952,
  entrées tôt, partent plus tôt, comme celles de la retraite anticipée de 2004
  à 2008. - *Ce que la mesure accuse.* La durée des carrières pleines n'était
  pas ce qui manquait à la pension des hommes : elles attendaient leur durée
  requise pour partir au taux plein, et la pension de base ne compte pas les
  années au-delà ; la complémentaire n'y gagne que des années de jeunesse, peu
  payées. L'écart des hommes tient aux deux quintiles du haut, où la
  population range 40 % de carrières de moins de quarante ans, proratisées :
  la tranche de trente à quarante ans y vaut 35 années, au milieu de la
  tranche, quand celles de l'EIR, proratisées à 98,5 % au cinquième quintile,
  sont pour la plupart presque entières ; et les carrières statutaires courtes
  de l'agent de conduite et de l'agent des IEG y sont proratisées à 78 et
  88 %.

**Ce qui reste** de l'étape, dans l'ordre : le haut de l'échelle des hommes —
la durée de la tranche de trente à quarante ans, et la proratisation des
carrières statutaires — ; la pension des femmes, trop haute par année validée
au bas de l'échelle ; le minimum selon la génération ; enfin, au propriétaire,
la bascule de la page. La onzième version reste en place, débrayable par sa
constante.
