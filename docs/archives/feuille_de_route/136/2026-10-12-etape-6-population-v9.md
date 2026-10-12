# Étape 6, la population : le volume de travail selon le rang, la neuvième version

**Le 12 octobre 2026 : chaque classe de centiles du salariat privé travaille
désormais le volume de sa catégorie, les employés au bas, les cadres au haut.
Le minimum contributif gagne en profondeur : 17,2 % des liquidants de 2023 au
lieu de 13,6 (EACR 18,8), 10,1 % des hommes au lieu de 5,5 (12,2), un minimum
moyen de 73 à 90 € par mois au lieu de 62 à 78 (134 à 139). La distribution
des pensions de 2020 s'approche de l'EIR, celle des femmes surtout. Celle des
hommes, déjà sous l'EIR, s'en éloigne au bas, et leur part au minimum passe
au-dessus de l'EIR (17,1 % pour 12,4) : trop de minimum dans les générations
anciennes, pas assez dans les récentes.**


Demande du propriétaire : « Fait l'étape suivante » — le volume selon le rang,
remesuré sur la huitième version : « le minimum, les pensions, la page » (note
de la huitième version).

- *La forme* (`VOLUME_SELON_LE_RANG`, `scripts/grille_large.py`), la
  variante de la quatrième version, débrayée depuis. Chaque classe de
  centiles prend, en plus de la part de l'année travaillée à son âge, le
  volume de la catégorie qu'elle représente, rapporté à celui de l'ensemble
  (`volume_travail.csv`) : employés au dixième centile (0,88), ouvriers au
  vingt-cinquième (0,95), professions intermédiaires au soixante-quinzième
  (1,08), cadres au-delà (1,13), sans dépasser l'année entière. La part payée
  le Smic toute la carrière et les sous-classes du bas prennent celui de leur
  classe. Une convention : l'INSEE ne croise pas le rang du salaire et le
  volume, et celui des employés compte aussi leur temps partiel, que la
  population donne déjà à chaque sexe. Un test la tient
  (`test_chaque_classe_travaille_le_volume_de_sa_categorie`).
- *Le minimum contributif* (`part_minimum_contributif.py`, en pour cent des
  liquidants, en euros de 2023 par mois) — l'essai de la note précédente,
  redonné tel quel par la constante :

  | | 2019 | 2020 | 2021 | 2022 | 2023 | femmes 2023 | hommes 2023 | 2024 | hommes, 2019 à 2024 | minimum moyen, 2019-2023 |
  |---|---|---|---|---|---|---|---|---|---|---|
  | huitième version | 13,4 | 12,4 | 11,9 | 13,3 | 13,6 | 19,8 | 5,5 | 16,1 | 5,5 à 5,9 | 62 à 78 € |
  | neuvième version | 15,6 | 14,7 | 14,9 | 16,1 | 17,2 | 22,6 | 10,1 | 21,8 | 9,0 à 11,8 | 73 à 90 € |
  | EACR, alignés | 20,4 | 18,4 | 17,9 | 18,9 | 18,8 | 25,2 | 12,2 | 18,6 (estimée) | 12,2 à 12,7, de 2022 | 134 à 139 € |

  L'année 2024 passe au-dessus de l'EACR, qui ne fait encore que l'estimer :
  le minimum, relevé par la réforme de 2023, y saute dans la population
  quelle que soit sa version, de 13,6 à 16,1 % à la huitième.
- *Les pensions de 2020 contre l'EIR*, en euros par mois ; Kolmogorov : le
  plus grand écart des répartitions, et la borne où il tombe :

  | | d1 | d3 | médiane | d9 | Kolmogorov |
  |---|---|---|---|---|---|
  | ensemble, EIR | 402 | 933 | 1 382 | 2 730 | |
  | ensemble, huitième version | 525 | 1 047 | 1 362 | 2 567 | −7,2 pt à 900 |
  | ensemble, neuvième | 505 | 1 006 | 1 338 | 2 641 | −5,8 pt à 800 |
  | femmes, EIR | 283 | 703 | 1 013 | 2 229 | |
  | femmes, huitième version | 421 | 865 | 1 219 | 2 137 | −12,8 pt à 900 |
  | femmes, neuvième | 409 | 844 | 1 219 | 2 164 | −11,8 pt à 1 100 |
  | hommes, EIR | 872 | 1 374 | 1 745 | 3 242 | |
  | hommes, huitième version | 753 | 1 228 | 1 574 | 2 848 | +9,7 pt à 1 800 |
  | hommes, neuvième | 719 | 1 206 | 1 570 | 2 808 | +10,4 pt à 1 400 |

  Le bas descend, le haut des femmes monte ; les hommes perdent au bas,
  leur deuxième décile de 1 087 à 1 018 € (1 148 dans l'EIR).
- *La pension en équivalent carrière complète.* Au premier quintile, la part
  de chaque tranche de durée s'approche de l'EIR : l'écart moyen des dix
  cases passe de 7,0 à 6,3 points, celui des femmes de 3,9 à 2,8, celui des
  hommes de 10,0 à 9,7. Les bornes descendent à 973, 1 306, 1 638 et
  2 127 € par mois. La part au minimum de pension, en pour cent des retraités
  de 2020 de chaque quintile :

  | | q1 | q2 | q3 | q4 | q5 | ensemble |
  |---|---|---|---|---|---|---|
  | femmes, EIR | 64,3 | 59,9 | 18,4 | 9,9 | 1,1 | 38,5 |
  | femmes, huitième version | 72,5 | 13,6 | 18,2 | 3,2 | 0,0 | 29,1 |
  | femmes, neuvième | 81,0 | 19,9 | 24,0 | 2,7 | 0,0 | 33,0 |
  | hommes, EIR | 51,5 | 32,6 | 6,2 | 3,9 | 0,4 | 12,4 |
  | hommes, huitième version | 66,0 | 13,5 | 22,5 | 0,0 | 0,0 | 13,6 |
  | hommes, neuvième | 72,4 | 25,1 | 21,8 | 0,0 | 0,0 | 17,1 |

- *Sur la page*, contre la huitième version : l'écart des années observées
  passe de −1,05 à −1,38 point au scénario 2, de −2,83 à −3,11 aux
  scénarios 4 et 6 ; la part du PIB en 2070, au scénario 2, de −0,04 à
  −0,10 point, les autres à quelques centièmes près ; le coefficient de 2070
  du scénario 2, de +0,024 à +0,055 ; la garantie ne bouge pas ; le passé
  refait, au pire depuis 2000, de 11,7 à 12,0 %.
- *Ce que la mesure accuse.* Le minimum se contredit d'une génération à
  l'autre. Avant 2017, la neuvième version passe au-dessus de l'EACR (29,9 %
  des liquidants de 2012, pour 27,1 à la Cnav) ; depuis 2019, elle reste en
  dessous : de 2012 à 2019, elle en perd 14 points, l'EACR 7. Chez les
  hommes, 14,5 à 16 % des générations 1944 à 1950 y sont, 10 % des
  générations 1956 à 1960 ; le stock de 2020, fait des générations
  anciennes, en compte trop, les liquidants récents pas assez. La population
  prête à toutes les générations les durées et les interruptions des
  retraités de 2020, et ne sait pas fragmenter davantage les carrières des
  plus jeunes. Et la pension des hommes reste sous l'EIR de 10 à 18 % d'un
  bout à l'autre de leur distribution : ce manque n'est pas celui du bas.

**Ce qui reste** de l'étape, dans l'ordre : la pension des hommes, sous l'EIR
du premier au neuvième décile ; celle des femmes, au-dessus du premier décile
à la médiane ; le minimum selon la génération, que la grille ne sait pas
faire varier ; enfin, au propriétaire, la bascule de la page. La neuvième
version reste en place, débrayable par sa constante.
