# Étape 14, septième partie : les indépendants de la population, à la dispersion de leurs revenus

**Le 17 octobre 2026 : l'artisan de la population prend la dispersion des
revenus des non-salariés de son sexe, que l'INSEE publie, et la part de
femmes de ses anciens dans l'EIR. Il avait la dispersion des salaires d'un
temps complet et la part de femmes du régime général, et aucun artisan
n'atteignait le minimum contributif. Les hommes des régimes alignés au
minimum passent, en 2023, de 9,9 à 11,4 % des liquidants, pour 12,2 dans
l'EACR. La même source le juge : sa pension moyenne est celle des anciens
artisans et commerçants de l'EIR, 1 234 € pour 1 230, mais le bas de ses
hommes descend trop, 794 € au premier quartile pour 1 030.**

Demande : la vague du 17 octobre 2026, session 7, « action 138, étape 14 : les
indépendants dans la population ». C'est, dans « Ce qui reste » de la note des
salariés agricoles, « la dispersion des revenus des indépendants, si une
source la publie » : l'INSEE la publie.

- *La source* (`scripts/fetch/insee_revenus_independants.py`,
  `macro/revenus_non_salaries.csv`, `macro/pensions_non_salaries.csv`,
  certifiés). « Emploi et revenus des indépendants », Insee Références,
  édition 2025, trois fiches lues dans leurs classeurs. La 1.6 : la
  distribution des revenus des non-salariés classiques par sexe en 2022, hors
  micro-entrepreneurs et hors agriculture, dont les rapports Q3/Q1 et D9/D1
  publiés contrôlent les quantiles. La 1.3 : la même par secteur, et le 99e
  centile. La 1.11 : la pension des anciens non-salariés selon leur régime
  principal dans l'EIR de 2020, que les classeurs de la DREES ne donnent pas.
  Le revenu est l'assiette des cotisations personnelles, annualisée, nulle en
  cas de déficit. Son premier décile vaut 0,23 fois la médiane des femmes et
  0,22 celle des hommes, quand celui du salaire d'un temps complet du privé
  en vaut 0,62 et 0,61. La ligne de tous les retraités de la fiche 1.11
  redonne les effectifs et les moyennes de la DREES, non ses quartiles des
  femmes : 730, 1 140 et 1 720 €, pour 598, 1 013 et 1 613. Un quartile de la
  fiche se compare donc aussi à ceux de tous les retraités de la fiche. Les
  tests (`test_revenus_non_salaries.py`) : le lecteur, sur des grilles
  rendues comme les classeurs, et les valeurs que les fiches impriment.
- *La dispersion* (`INDEPENDANTS_A_LEUR_DISPERSION`,
  `dispersion_des_independants`). L'artisan se décline aux sept centiles du
  revenu des non-salariés classiques de son sexe, resserrés en carrière et
  rapportés à la moyenne des deux sexes, comme ceux des salaires. Ses
  multiplicateurs, autour de son niveau :

  | | p10 | p25 | p50 | p75 | p90 | p95 | p99 | moyenne |
  |---|---|---|---|---|---|---|---|---|
  | femmes, revenus des non-salariés | 0,24 | 0,44 | 0,71 | 1,06 | 1,55 | 1,99 | 3,56 | 0,87 |
  | femmes, salaires (avant) | 0,57 | 0,69 | 0,82 | 1,03 | 1,32 | 1,58 | 2,35 | 0,92 |
  | hommes, revenus des non-salariés | 0,26 | 0,50 | 0,82 | 1,32 | 2,11 | 2,71 | 4,86 | 1,09 |
  | hommes, salaires (avant) | 0,63 | 0,75 | 0,92 | 1,17 | 1,55 | 1,87 | 2,97 | 1,05 |

  Trois conventions. Les revenus nuls ou déficitaires de l'année, un dixième
  des non-salariés, n'y sont pas. Le 95e et le 99e centile, que la fiche par
  sexe ne publie pas, prolongent le neuvième décile par la queue de Pareto de
  l'ensemble : son 99e centile vaut 3,0 fois son neuvième décile. Et la coupe
  se resserre comme celle des salaires (0,76 de ses écarts), faute d'une
  source sur la part passagère du revenu d'un indépendant.
- *La part de femmes* (`INDEPENDANTS_A_LEUR_PART_DE_FEMMES`,
  `femmes_des_independants`). L'artisan prenait celle du régime général,
  55 %, quand les anciens artisans et commerçants de l'EIR en comptent 28 %,
  140 milliers sur 500. Il prend la leur, et le salariat privé donne ce qui
  manque à celle du groupe, que le test tient. 3,8 % des femmes de la
  population étaient des artisanes, pour 1,7 % dans l'EIR ; elles sont 1,9 %,
  et les hommes 5,1 %, pour 5,0.
- *La mesure* (`confronter_non_salaries`, `grille_large.py --grille
  population --distribution`, nouveau tableau). L'artisan de 2020 contre les
  anciens artisans et commerçants de la fiche 1.11, en euros par mois ;
  « avant », la population d'hier, « dispersion », la seule dispersion,
  « après », les deux :

  | | part | moyenne | q1 | médiane | q3 |
  |---|---|---|---|---|---|
  | ensemble, EIR | 3,2 % | 1 230 | 870 | 1 300 | 1 720 |
  | ensemble, avant | 3,5 % | 1 178 | 811 | 1 176 | 1 543 |
  | ensemble, après | 3,5 % | 1 234 | 755 | 1 157 | 1 708 |
  | femmes, EIR | 1,7 % | 820 | 520 | 870 | 1 230 |
  | femmes, avant | 3,8 % | 1 057 | 654 | 1 033 | 1 468 |
  | femmes, dispersion | 3,8 % | 1 056 | 571 | 960 | 1 582 |
  | femmes, après | 1,9 % | 1 058 | 571 | 963 | 1 582 |
  | hommes, EIR | 5,0 % | 1 380 | 1 030 | 1 440 | 1 800 |
  | hommes, avant | 3,1 % | 1 328 | 1 010 | 1 300 | 1 642 |
  | hommes, dispersion | 3,2 % | 1 299 | 794 | 1 282 | 1 820 |
  | hommes, après | 5,1 % | 1 301 | 794 | 1 288 | 1 822 |

  Rapportés à ceux de tous les retraités du sexe, les quartiles des
  artisanes sont ceux de la fiche au premier quartile et à la médiane (0,70
  et 0,76, pour 0,71 et 0,76), non au troisième quartile (0,92 pour 0,72) ;
  ceux des artisans valent 0,67, 0,81 et 0,83, pour 0,81, 0,83 et 0,77.
- *Le minimum contributif* (`part_minimum_contributif.py --grille
  population`). La part des liquidants au minimum, en 2022, 2023 et 2024,
  entre parenthèses l'EACR :

  | | avant | après |
  |---|---|---|
  | alignés, hommes | 10,4 ; 9,9 ; 11,7 | 12,5 ; 11,4 ; 14,7 (12,2 ; 12,2 ; 12,7) |
  | alignés, femmes | 23,5 ; 24,7 ; 29,8 | 24,5 ; 25,9 ; 30,6 (25,2 ; 25,2 ; 24,1) |
  | Cnav, hommes | 10,3 ; 9,8 ; 11,6 | 12,6 ; 11,4 ; 14,7 (10,9 ; 10,7 ; 11,1) |

  La génération 1975 met 14,0 % de ses hommes au minimum, pour 11,1 avant ;
  TRAJECTOiRE, qui dit surestimer, 18,1.
- *Les artisans au minimum* (essai, hors du dépôt : les seuls artisans de la
  population, générations 1945 à 1960, au poids de la grille et non de la
  page). 32,4 % des artisanes et 35,1 % des artisans ont une pension portée
  à un minimum ; avant, 6,3 % et aucun.
- *Ce que cela dit.* La moyenne des artisans est juste, et leur part de chaque
  sexe ; leur dispersion va trop loin. Avant, le premier quartile des hommes
  était celui de l'EIR, 1 010 € pour 1 030, par des carrières toutes au-dessus
  du minimum ; il descend à 794 €, et la Cnav, qui compte les indépendants
  depuis 2019, met trop d'hommes au minimum (11,4 % en 2023, pour 10,7), quand
  elle en mettait trop peu (9,8). Le gain des alignés tient en partie à cet
  excès, qui compense le défaut des salariés agricoles. Le haut, lui, vient
  au bon niveau : 1 822 € au troisième quartile des hommes, pour 1 800 (1 642
  avant). Trois causes peuvent creuser le bas, qu'aucune source du dépôt ne
  sépare : la part passagère du revenu d'un indépendant, plus forte que
  celle d'un salaire, que le resserrement des salaires laisse dans la
  carrière ; la dispersion des hommes non salariés, qui mêle aux artisans les
  médecins et les conseils ; et les années de salariat des anciens artisans
  de l'EIR, souvent polypensionnés, quand l'artisan de la population l'est de
  toute sa carrière. Rien n'est recalé : ce serait se caler sur l'EIR.
- *La distribution de l'EIR* (même commande). Elle bouge à peine : les
  hommes de 2020 à 1 781 € en moyenne, pour 1 792 avant (EIR 1 957), leur
  médiane à 1 585 €, l'écart de Kolmogorov à +7,6 points à 1 700 € (+7,5) ;
  les femmes à −14,9 points à 900 € (−15,0). La part des hommes au minimum
  de pension passe de 13,0 à 14,3 % ; l'EIR en compte 9,8 % au minimum du
  régime principal, 26,1 % tous régimes.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur ni témoin ; les libéraux, qui gardent la dispersion des
  salaires en attendant leur déclinaison par section (action 152, au
  propriétaire), et l'exploitant agricole, hors du champ de l'INSEE ; les
  grilles autres que la population. Les tests (`test_grille_large.py`) : la
  dispersion de l'artisan lue dans la fiche, sa part de femmes, son groupe
  qui garde la sienne, et la mesure contre la fiche 1.11.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : la part passagère du revenu des indépendants,
   qui resserrerait leur carrière, et la carrière saisonnière des salariés
   agricoles, si une source les publie ; le juge propre des artisans, la part
   des liquidants du RSI au minimum contributif d'avant 2020, à chercher dans
   l'EACR ; la part des générations 1946 à 1953 au minimum, trop haute ; la
   fragmentation selon la génération ; la décote selon la tranche ou le rang.
   Les niveaux des cas types statutaires et non salariés, et la dispersion
   des libéraux, attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, au-delà de la décote : l'âge publié, la surcote.
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).
