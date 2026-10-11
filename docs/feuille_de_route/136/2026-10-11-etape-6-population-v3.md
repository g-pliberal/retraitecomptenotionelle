# Étape 6, la population : la persistance au Smic mesurée, la troisième version

**Le 11 octobre 2026 : une part de la classe du bas de chaque sexe est payée
le Smic toute la carrière, celle que la DG Trésor trouve encore au voisinage
du Smic six ans plus tard. Elle ne rend aux hommes que 0,4 à 1,4 point de
minimum contributif selon l'année : une carrière complète au Smic est au seuil
du minimum, qu'elle touche ou non selon l'année de son départ. La mesure
montre surtout qu'une classe de 17,5 % des carrières est trop large pour un
seuil : une seule case, posée à 11 € par mois sous lui, fait deux points.**

Demande du propriétaire : « vas-y, mesure la persistance dans la population »,
sur la série certifiée le même jour (`persistance_smic.csv`).

- *La forme* (`PERSISTANCE_SMIC`, `scripts/grille_large.py`). La part
  persistante de chaque sexe est celle de la coupe à temps complet sous 1,05
  Smic — le seuil de la DG Trésor —, interpolée au logarithme entre les
  centiles certifiés (`part_de_la_coupe_sous`), en moyenne de 1976 à 2024
  hors 2020 et 2021 : 21,4 % des femmes, 12,4 % des hommes ; multipliée par
  la part de ceux qui y sont encore six ans plus tard, parmi ceux restés
  salariés du privé : celle des 35-49 ans (25,0 %), l'âge où la population lit
  le rang, au rapport de chaque sexe à l'ensemble (22,4 et 13,4 % pour 18,8),
  que le document ne croise pas avec l'âge (`persistance_a_six_ans`) : 29,7 %
  des femmes et 17,9 % des hommes. Soit 6,35 % des carrières de femmes du
  salariat privé et 2,21 % de celles des hommes, prises dans la classe du bas
  (17,5 %). Elles sont payées le Smic de chaque année, leur niveau est celui
  du Smic, et le reste de la classe en garde la moyenne : la masse des
  salaires et la moyenne de chaque sexe ne bougent pas. Une grille ne sachant
  pas donner à une carrière un poids qui dépende de sa génération, la part est
  la même pour toutes. Trois tests la tiennent. Débrayée, la seconde version
  se redonne au chiffre près.
- *Une borne basse.* La coupe à temps complet met sous 1,05 Smic deux à
  trois fois plus de salariés que les DADS horaires de la DG Trésor, dont le
  texte en compte 9 à 11 % chez les femmes et 4 à 5 % chez les hommes. Au
  stock du texte (10 et 4,5 %), la part persistante tombe à 2,97 et 0,80 %.
- *Le minimum contributif* (`part_minimum_contributif.py`, en pour cent des
  liquidants, en euros de 2023 par mois) :

  | | 2019 | 2020 | 2021 | 2022 | 2023 | femmes 2023 | hommes 2023 | 2024 | hommes 2024 | minimum moyen, 2019-2023 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | seconde version | 12,6 | 12,0 | 12,1 | 13,6 | 14,7 | 22,0 | 5,2 | 16,8 | 5,0 | 60 à 78 € |
  | troisième version | 13,5 | 12,5 | 12,3 | 13,9 | 13,8 | 20,0 | 5,7 | 17,3 | 6,4 | 65 à 76 € |
  | au stock du texte | 13,0 | 12,2 | 12,1 | 13,7 | 14,8 | 22,0 | 5,4 | 17,0 | 5,5 | 60 à 76 € |
  | EACR, alignés | 20,4 | 18,4 | 17,9 | 18,9 | 18,8 | 25,2 | 12,2 | 18,6 (estimée) | 12,7 | 134 à 139 € |

  Par génération, les hommes gagnent de 0,1 point (1960) à 1,3 point (1961 à
  1963, 5,3 à 6,6 %) ; les femmes ne bougent pas de 1958 à 1963, et ailleurs
  vont dans les deux sens : 20,6 à 19,2 % pour 1975, 14,9 à 16,9 % pour 1980.
- *D'où viennent les bénéficiaires.* La carrière complète au Smic de bout en
  bout, celle des persistantes, est au seuil du minimum majoré : elle le
  touche quand elle part en 2019, pour une part en 2020, plus du tout de 2021
  à 2023, et toute en 2024, après le relèvement de septembre 2023 — elle fait
  alors 12,4 % des bénéficiaires hommes. En 2023, dans les deux versions,
  aucune carrière complète à temps complet du salariat privé ne touche le
  minimum ; ses bénéficiaires hommes sont à 70 % des carrières de moins de
  quarante années validées, à 29 % des carrières complètes des autres groupes
  — artisans, contractuels, polypensionnés — ; ses bénéficiaires femmes, à
  95 % des carrières courtes.
- *La baisse des femmes en 2023 est une marche, non un effet.* Elle tient
  tout entière à une case : les femmes de la génération 1956, de trente à
  quarante années validées, de la classe du bas, à temps complet, qui partent
  à 67 ans. La seconde version les payait 1,050 Smic, et le minimum leur
  servait 136 € par an. Gardant la moyenne de la classe, la troisième paie le
  reste 1,079 Smic : la case passe au-dessus du seuil et ne reçoit plus rien.
  Elle fait 8 % des carrières de sa tranche, et deux points des liquidantes
  de 2023. Le minimum se mesure donc à deux points près sur une grille de
  sept centiles : plus que l'effet de la persistance.
- *Les pensions de 2020 contre l'EIR, et la page*, les deux versions sur les
  mêmes données (celles de l'action 142, le même soir, comprises) : la
  moyenne reste à 1 488 € ; chez les hommes, le deuxième décile passe de
  1 085 à 1 072 €, le troisième de 1 231 à 1 225 € ; les femmes ne bougent
  pas ; l'écart de Kolmogorov de l'ensemble passe de −7,2 à −7,1 points. Sur
  la page : l'écart des années observées, −1,43 et −3,01 points (−3,00) ; la
  part du PIB en 2070 au scénario 3, +0,66 point (+0,65) ; le coefficient
  d'équilibre de 2070 au scénario 2, +0,017 (+0,016) ; la garantie, +0,089
  point ; le passé refait, au pire depuis 2000, 12,5 %.
- *Ce que la mesure accuse.* La persistance au Smic est réelle et petite :
  2,2 % des carrières d'hommes, au seuil du minimum. L'écart des hommes à
  l'EACR — 5,7 % pour 12,2 en 2023, 6,4 pour 12,7 en 2024 — tient à autre
  chose. Leurs bénéficiaires sont des carrières courtes et celles des autres
  groupes : ce qui manque à la population serait le volume de travail — les
  années incomplètes, le chômage, que le revenu salarial de l'INSEE compte à
  0,79 année d'équivalent temps plein par an pour les hommes en 2023 —
  plutôt que le niveau du salaire. Et la classe du bas est trop large : le
  seuil du minimum tombe dans les 17,5 % de carrières qu'elle réunit sous un
  seul niveau.

**Ce qui reste** de l'étape, dans l'ordre : le volume de travail des
carrières du bas, à chercher et certifier ; un bas d'échelle plus fin, qui
ne fasse plus basculer une classe entière d'un côté du seuil ; enfin, au
propriétaire, la bascule de la page. La persistance reste en place,
débrayable par sa constante.
