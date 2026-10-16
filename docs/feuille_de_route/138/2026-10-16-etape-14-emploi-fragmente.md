# Étape 14, quatrième partie : l'emploi fragmenté, concentré sur une part des carrières du bas

**Le 16 octobre 2026 : le volume de travail plus faible des classes du bas ne
pèse plus sur toutes leurs carrières un peu, mais sur une part d'entre elles
beaucoup — 22,8 % des employés et 10,1 % des ouvriers, fragmentés toute la
carrière au volume des bas revenus salariaux (seizième version,
`EMPLOI_FRAGMENTE`). Le seuil du minimum contributif ne fait plus basculer les
hommes par blocs d'une génération à l'autre : 11,9 % de la génération 1950 au
minimum, puis 8,6 à 9,1 % de chacune de 1955 à 1990, au lieu de 14,6, 7,9 et
11,2 %. Leur niveau monte d'un point, de 2019 à 2023, mais reste aux deux
tiers de l'EACR. Rien ne bouge sur la page.**

Demande : la vague ter du 16 octobre 2026, session 2, « action 138, étape 14.
La population, encore : un emploi fragmenté concentré sur une part des
carrières complètes du bas de l'échelle, s'il se trouve une source […] ; à
défaut, des sous-classes du bas plus fines ». Le point 1 de « Ce qui reste »,
note du minimum selon la génération.

- *La source.* Elle était au dépôt, certifiée, et rien ne la lisait :
  `heures_salariees.csv` (INSEE, « Emploi, chômage, revenus du travail »,
  édition 2024, dossier de la Dares sur les bas revenus salariaux, panel Tous
  salariés), les heures salariées de 2019, centile par centile, des salariés
  du privé de 24 à 62 ans et de ceux d'entre eux dans les 20 % des revenus
  salariaux les plus bas deux années de suite. Les seconds travaillent
  748 heures en moyenne de leurs centiles, les premiers 1 536 : 0,487 fois.
  Le titre du dossier dit la persistance : la moitié des bas revenus de 2011
  le sont encore en 2019. Ni l'enquête Emploi ni les panels de la DADS ne
  publient comment ce volume change d'une génération à l'autre.
- *La règle* (`volume_fragmente`, `fragmentees`, `scripts/grille_large.py`).
  Sous `VOLUME_SELON_LE_RANG`, chaque classe de centiles travaille le volume
  de sa catégorie : les employés au dixième centile 0,883 fois l'ensemble,
  les ouvriers au vingt-cinquième 0,948. Une classe sous un se scinde : une
  part, fragmentée, à 0,487 fois le volume de l'ensemble à chaque âge ; le
  reste au volume de l'ensemble ; la part, (1 − 0,883) / (1 − 0,487), garde
  le volume de la catégorie, et la masse des salaires ne bouge pas. Chaque
  sous-classe du bas se scinde, la part au Smic toute la carrière comprise,
  et le temps partiel des femmes s'y ajoute comme avant. Deux conventions :
  la fragmentation dure toute la carrière, et elle est la même pour toutes
  les générations. Une carrière fragmentée valide moins de trimestres avant
  2014, quand il fallait 200 heures au Smic pour un trimestre : trois par an,
  puis quatre.
- *Le crible de l'EIR* (`grille_large.py --grille population
  --distribution`, sans puis avec) :

  | | sans | avec | EIR |
  |---|---|---|---|
  | ensemble, Kolmogorov | −9,9 pt à 800 € | −9,6 pt à 800 € | |
  | hommes, Kolmogorov | +7,9 pt à 1 800 € | +7,8 pt à 1 800 € | |
  | hommes, d2 / d3 / médiane | 1 073 / 1 224 / 1 583 € | 1 111 / 1 269 / 1 584 € | 1 148 / 1 374 / 1 745 € |
  | femmes, Kolmogorov | −16,0 pt à 800 € | −16,4 pt à 900 € | |
  | hommes au minimum de pension | 12,9 % | 11,5 % | 9,8 % |
  | femmes au minimum de pension | 31,1 % | 29,6 % | 37,7 % |
  | hommes de moins de dix ans au 1er quintile | 74,3 % | 65,6 % | 73,1 % |

  Les hommes s'en rapprochent, au bas de la distribution surtout ; les femmes
  s'en écartent un peu ; la part au minimum de pension, tous minima
  confondus, s'approche de l'EIR chez les hommes, s'en éloigne chez les
  femmes.
- *Le minimum contributif* (`part_minimum_contributif.py --grille
  population`, retraités de l'étranger compris), sans puis avec :

  | | 2013 | 2016 | 2019 | 2021 | 2022 | 2023 | 2024 |
  |---|---|---|---|---|---|---|---|
  | sans | 23,3 % | 23,7 | 15,4 | 14,0 | 14,4 | 15,9 | 18,6 |
  | avec | 20,8 % | 19,8 | 15,3 | 14,0 | 14,6 | 15,8 | 17,9 |
  | EACR | 24,8 % | 22,1 | 20,4 | 17,9 | 18,9 | 18,8 | 18,6* |
  | hommes, sans | 15,7 % | 13,8 | 8,0 | 7,3 | 7,4 | 7,6 | 11,8 |
  | hommes, avec | 12,2 % | 10,7 | 8,8 | 8,3 | 8,4 | 8,0 | 9,1 |
  | hommes, EACR | | | | | 12,2 | 12,2 | 12,7* |

  \* l'estimation de la DREES. Le minimum moyen d'un bénéficiaire de 2023
  passe de 106 à 126 € de 2023 (134 aux régimes alignés) ; celui des hommes,
  de 68 à 138 € : les carrières fragmentées en reçoivent un gros, quand les
  sous-classes entières n'en recevaient qu'un petit. De 2013 à 2016, la part
  perd 2,5 à 4 points, et s'éloigne de l'EACR : les sous-classes entières des
  générations 1950 à 1953, qui touchaient le minimum, travaillent désormais
  le volume de l'ensemble et le passent.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur ni témoin. La population passe de 1 278 à 1 494 carrières,
  sa mesure de 404 à 454 s sur quatre cœurs. Les sous-classes du bas restent
  quatre : la fragmentation, qui lisse déjà le seuil, en tient lieu. Les tests
  (`test_grille_large.py`) : le volume relatif lu dans le fichier, la part
  de chaque classe, et le volume de chaque catégorie gardé en moyenne de ses
  carrières.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : le niveau des hommes au minimum contributif,
   8 % des liquidants de 2023 pour 12,2 ; la fragmentation selon la
   génération, si une source la publie ; la part des générations 1950 à 1953
   au minimum, que la fragmentation abaisse ; les femmes des générations 1946
   à 1949 ; la décote selon la tranche ou le rang, si une source la publie
   par durée. Les niveaux des cas types statutaires et non salariés attendent
   l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, au-delà de la décote : l'âge publié, la surcote.
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).
