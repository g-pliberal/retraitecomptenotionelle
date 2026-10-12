# Étape 6, la population : le deuxième quintile, et le temps partiel jusqu'au départ — la treizième version

**Le 12 octobre 2026 : le deuxième quintile ne manque pas de minimum, il a des
bornes plus hautes. Aux seuils de l'EIR — vers 880 et 1 240 € par mois en
équivalent carrière complète —, la douzième version mettait au minimum, entre
les deux, 11,6 % des femmes, l'EIR 12,6. Ce qui lui manquait était en
dessous : 14,5 % des femmes sous 880 €, pour 30,6, au minimum ou non ; et elle
en avait trop au-dessus de 1 240 €, 58,1 % pour 44,7. Une des causes : la
population rendait au temps complet, à cinquante ans, ses carrières à temps
partiel, quand l'INSEE trouve plus de femmes à temps partiel après cinquante
ans qu'avant ; ces années entières relevaient leur salaire annuel moyen
au-dessus du minimum. La treizième version les garde à temps partiel jusqu'au
départ : 32,8 % des femmes au minimum au lieu de 29,8 (38,5 dans l'EIR), une
médiane de 1 237 € au lieu de 1 302 (1 013), le minimum contributif à 22,0 %
des liquidantes de 2023 au lieu de 17,8 (25,2), à 108 € en moyenne au lieu de
88 (134 à 138).**

Demande du propriétaire : « Fait la prochaine étape » — « le deuxième quintile
— la pension par année validée des carrières presque entières, que l'EIR met
pour les trois cinquièmes au minimum » (note de la douzième version).

- *Les bornes du deuxième quintile* (essai, hors du dépôt : le classeur
  « Caractéristiques de tous les retraités résidant en France » de l'EIR 2020,
  diffusé par la DREES, feuilles « QuintilesEQCC » et « Minima », que le dépôt
  ne certifie pas encore ; la population de 2020, sous les poids de la page).
  La population ne compte que des résidents ; le classeur des résidents range
  les siens en quintiles, comme celui de tous les retraités, sans en publier
  les bornes. Il publie les déciles de la pension dans chaque quintile : le
  neuvième du premier est à 849 €, celui du deuxième à 1 213 € ; les carrières
  complètes qui les font, dont la pension est l'équivalent, mettent les bornes
  un peu au-dessus, vers 880 et 1 240 €. Celles de la population sont à 993 et
  1 335 €. Aux seuils de l'EIR, la part des femmes et leur part au minimum de
  pension :

  | | sous 880 € | 880 à 1 240 € | au-dessus |
  |---|---|---|---|
  | EIR, résidentes | 30,6 % | 23,9 % | 44,7 % |
  | au minimum, EIR | 65,9 % | 52,7 % | 10,5 % |
  | douzième version | 14,5 % | 27,4 % | 58,1 % |
  | au minimum, douzième | 82,1 % | 42,4 % | 10,9 % |
  | treizième | 16,0 % | 28,8 % | 55,2 % |
  | au minimum, treizième | 83,9 % | 45,6 % | 11,4 % |

  Les résidentes au minimum de leur régime principal touchent 662 € pour
  73,7 % de proratisation, de l'ordre de 900 € en équivalent carrière
  complète ; les carrières longues que la population met au minimum, 870 à
  902 € : elle leur donne le bon niveau. La douzième version en manquait :
  29,8 % des femmes au minimum, pour 37,7 chez les résidentes ; des salariées
  monopensionnées du régime général, 27,4 %, quand le classeur en met 43 %
  environ. Et elle n'a pas, sous 880 €, les pensions que le minimum ne relève
  pas, 2,6 % des femmes pour 10,4 : 8,8 % des résidentes sont parties avec une
  décote, 17,5 % de celles du premier quintile, 15 % de celles qu'aucun
  minimum ne relève — la population part au taux plein. - *Le temps partiel, à
  cinquante ans.* Les carrières à temps partiel l'étaient de 25 à 49 ans, la
  tranche dont la part sert à leur nombre, et à temps complet ensuite. L'INSEE
  publie aussi la part des 50 ans et plus (`temps_partiel.csv`), plus haute
  encore chez les femmes : 32,3 % en moyenne de 1975 à 2025, pour 25,4 de 25 à
  49 ans. Le salaire annuel moyen ne retenant que les vingt-cinq meilleures
  années, une carrière rendue au temps complet y comptait ses dernières années
  entières. - *La forme* (`PARTIEL_JUSQU_AU_DEPART`, `ages_du_partiel`,
  `scripts/grille_large.py`). La carrière à temps partiel le reste de 25 ans à
  son départ ; leur part reste celle des 25 à 49 ans. Simulées pour la
  génération 1950, à carrière pleine, les femmes à temps partiel touchent à
  leur départ 854 € au lieu de 889 dans la classe du vingt-cinquième centile,
  le minimum y portant 261 € au lieu de 136 ; 911 € au lieu de 964 dans la
  classe médiane, désormais au minimum ; 1 009 € au lieu de 1 281 dans celle
  du soixante-quinzième centile. Un test tient la forme
  (`test_le_temps_partiel_reduit_le_revenu_de_25_ans_au_depart`). - *Les
  pensions de 2020 contre l'EIR*, en euros par mois ; Kolmogorov : le plus
  grand écart des répartitions, et la borne où il tombe :

  | | moyenne | d1 | d3 | médiane | d9 | Kolmogorov |
  |---|---|---|---|---|---|---|
  | ensemble, EIR | 1 536 | 402 | 933 | 1 382 | 2 730 | |
  | ensemble, douzième version | 1 568 | 610 | 1 098 | 1 404 | 2 684 | −10,4 pt à 900 |
  | ensemble, treizième | 1 557 | 599 | 1 067 | 1 377 | 2 684 | −9,9 pt à 900 |
  | femmes, EIR | 1 177 | 283 | 703 | 1 013 | 2 229 | |
  | femmes, douzième version | 1 369 | 465 | 938 | 1 302 | 2 298 | −18,4 pt à 900 |
  | femmes, treizième | 1 348 | 465 | 928 | 1 237 | 2 294 | −17,4 pt à 900 |

  Les hommes ne bougent pas : 1 781 € en moyenne, 1 631 € de médiane. - *Le
  minimum.* Au minimum de pension, 32,8 % des femmes de 2020 au lieu de 29,8
  (38,5 dans l'EIR), 25,0 % des salariées de la classe médiane au lieu de
  11,8, et 31,8 % des monopensionnées du régime général ; 17,3 % des hommes au
  lieu de 17,0 (12,4). Le minimum contributif
  (`part_minimum_contributif.py`) : en 2023, 16,1 % des liquidants au lieu de
  13,6 (EACR 18,8), les femmes à 22,0 % au lieu de 17,8 (25,2) ; en 2024,
  20,0 % au lieu de 17,7 (18,6 estimée), les femmes à 27,0 % au lieu de 23,2
  (24,1), au-dessus désormais. Son montant moyen, 108 € en 2023 au lieu de 88
  (134 à 138), 131 € en 2019 au lieu de 101 (139 à 142). De 2012 à 2019, sa
  part perd toujours 18 points, celle de l'EACR 7. - *La pension en équivalent
  carrière complète.* Au premier quintile, les femmes de quarante ans et plus
  passent de 13,6 à 15,1 % (10,1 dans l'EIR) : les carrières pleines à temps
  partiel y descendent. L'écart moyen des dix cases de tranche remonte de 5,3
  à 5,6 points. - *Sur la page*, contre la douzième version : l'écart des
  années observées passe de −1,48 à −1,39 point au scénario 2, de −3,26 à
  −3,12 aux scénarios 4 et 6 ; la part du PIB en 2070 de −0,22 à −0,20 point
  au scénario 2, de −0,75 à −0,74 au scénario 4 ; le coefficient de 2070 du
  scénario 2 de +0,128 à +0,118 ; la garantie ne bouge pas ; le passé refait,
  au pire depuis 2000, de 17,0 à 17,1 %. - *Ce que la mesure accuse.* Sous
  880 €, la population n'a encore que 16,0 % des femmes pour 30,6 : au
  minimum, 13,4 % pour 20,2 ; hors du minimum, 2,6 % pour 10,4, les départs
  avec décote d'abord, que l'EIR des résidents mesure quintile par quintile.
  Au-dessus de 1 240 €, elle en a 55,2 % pour 44,7.

**Ce qui reste** de l'étape, dans l'ordre : certifier le classeur des
résidents de l'EIR, et y confronter la population, qui ne compte qu'eux ; les
départs avec décote ; le minimum selon la génération ; enfin, au propriétaire,
la bascule de la page — et, s'il le veut, une action à part pour les
catégories des régimes statutaires. La treizième version reste en place,
débrayable par sa constante.