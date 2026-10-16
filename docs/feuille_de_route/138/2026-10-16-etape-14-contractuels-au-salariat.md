# Étape 14, cinquième partie : les retraités de l'Ircantec, rendus au salariat privé

**Le 16 octobre 2026 : la population ne fait plus des retraités de l'Ircantec
des contractuels de toute une carrière (dix-septième version,
`CONTRACTUELS_AU_SALARIAT`). L'Ircantec ne leur sert que 161 € par mois en
moyenne, quand le contractuel de la population en liquidait 540 à 630 € ; à
années entières, sans le volume de travail ni l'emploi fragmenté du salariat
privé, aucun n'atteignait le minimum contributif. Rendus au salariat privé,
les hommes passent de 9,4 à 10,1 % des liquidants de 2023 au minimum, contre
10,7 à la Cnav, indépendants compris, et 12,2 aux régimes alignés ; les
femmes, de 22,7 à 24,8 % (25,2). Les trois écarts de Kolmogorov à l'EIR se
resserrent. Rien ne bouge sur la page.**

Demande : la vague quater du 16 octobre 2026, session 4, « action 138,
étape 14. La population, encore : le niveau des hommes au minimum
contributif, 8 % des liquidants de 2023 au modèle contre 12,2 % dans l'EACR,
jugé sur l'EIR sans s'y caler ». Le point 1 de « Ce qui reste », note de
l'emploi fragmenté.

- *Le point de départ, sur le `main` du jour.* La note de l'emploi fragmenté
  mettait les hommes à 8,0 % des liquidants de 2023 ; d'autres sessions ont
  changé la population depuis, et `part_minimum_contributif.py --grille
  population` les met à 9,4 % (2022 : 9,7 %), l'ensemble à 16,9 %, contre
  18,8 aux régimes alignés.
- *D'où vient le creux.* La décomposition des hommes liquidants de 2022 et
  2023, par cas type de départ : le salarié du privé, 65 % d'entre eux, au
  minimum pour 8,7 % ; l'exploitant polypensionné, 2,9 %, pour 86 % ; l'actif
  de la CNRACL polypensionné, pour 30 %. Deux cas types n'y sont jamais : le
  contractuel public, 9,5 % des hommes, et l'artisan, 3,9 %. Les femmes
  contractuelles le sont pour 6 %, les salariées du privé pour 27 %.
- *Le contractuel n'était pas celui des retraités de l'Ircantec.* La
  population donnait au contractuel l'effectif de l'Ircantec, qu'elle ôtait à
  celui de la Cnav, et une carrière entière de contractuel, aux sept centiles
  du salaire de son sexe, à années entières : ni le volume de travail, ni
  l'emploi fragmenté, ni le Smic persistant du gabarit. Or l'Ircantec a servi
  3 990 M€ en 2023 (`macro/depenses_retraite_regimes.csv`) à 2 066 393
  retraités (`regimes/effectifs_retraites.csv`) : 161 € par mois, réversions
  comprises. Le contractuel de la population en liquide 541 € dans la
  génération 1950, 634 € dans celle de 1958, trois à quatre fois plus : la
  plupart des retraités de l'Ircantec sont des salariés du privé passés par
  un contrat public, et leur pension de base est celle du régime général.
- *La règle* (`CONTRACTUELS_AU_SALARIAT`, `reference_population`,
  `personnes(…, retirer)`, `scripts/grille_large.py`). La population n'a plus
  de contractuel : la Cnav garde ceux qu'elle comptait aussi, et le gabarit du
  salariat privé les porte, avec tout ce que le salariat a appris depuis le
  9 octobre ; une pension de l'Agirc-Arrco tient lieu de leur petite pension
  de l'Ircantec. Chaque groupe garde sa part de l'EIR. Deux conventions : un
  retraité de l'Ircantec a la carrière d'un salarié du privé ; ceux qui ont
  aussi une pension de la fonction publique restent comptés à la Cnav, comme
  avant. La grille « ensemble » et celles de la page gardent leur
  contractuel, que l'étape 3 pèse sur ses départs (session parallèle).
- *Le minimum contributif* (`part_minimum_contributif.py --grille
  population`, retraités de l'étranger compris), avant puis après :

  | | 2013 | 2016 | 2019 | 2021 | 2022 | 2023 | 2024 |
  |---|---|---|---|---|---|---|---|
  | avant | 23,8 % | 20,6 | 16,4 | 16,0 | 16,7 | 16,9 | 19,7 |
  | après | 25,0 % | 22,0 | 17,9 | 16,6 | 17,4 | 18,3 | 21,1 |
  | EACR | 24,8 % | 22,1 | 20,4 | 17,9 | 18,9 | 18,8 | 18,6* |
  | femmes, avant | 32,0 % | 27,3 | 20,6 | 21,1 | 22,4 | 22,7 | 28,9 |
  | femmes, après | 33,8 % | 29,5 | 22,4 | 20,9 | 23,3 | 24,8 | 29,9 |
  | femmes, EACR | | | | | 25,2 | 25,2 | 24,1* |
  | hommes, avant | 13,3 % | 12,0 | 10,2 | 9,4 | 9,7 | 9,4 | 10,5 |
  | hommes, après | 13,7 % | 12,9 | 11,2 | 10,4 | 10,6 | 10,1 | 11,7 |
  | hommes, EACR | | | | | 12,2 | 12,2 | 12,7* |
  | hommes, Cnav | | | | | 11,0 | 10,7 | 11,1 |

  \* l'estimation de la DREES. L'EACR : la Cnav jusqu'en 2018, les régimes
  alignés depuis 2019. Le minimum moyen d'un bénéficiaire de 2023 passe de
  122 à 128 € de 2023 (134 aux régimes alignés). L'année 2012 s'éloigne :
  37,4 % au lieu de 33,0, pour 27,1 : l'année des générations 1946 à
  1949, déjà trop haute.
- *Le crible de l'EIR* (`grille_large.py --grille population
  --distribution`, avant puis après) :

  | | avant | après | EIR |
  |---|---|---|---|
  | ensemble, Kolmogorov | −9,6 pt à 800 € | −9,2 pt à 800 € | |
  | femmes, Kolmogorov | −16,5 pt à 900 € | −14,9 pt à 900 € | |
  | hommes, Kolmogorov | +7,8 pt à 1 800 € | +7,4 pt à 1 700 € | |
  | hommes, médiane | 1 583 € | 1 585 € | 1 745 € |
  | femmes au minimum de pension | 31,7 % | 32,2 % | 37,7 % |
  | hommes au minimum de pension | 12,8 % | 13,1 % | 9,8 % |

  La part des hommes au minimum s'éloigne d'un peu de l'EIR, mais les deux
  ne comptent pas la même chose : la population compte un minimum de
  n'importe quel régime, l'EIR celui du régime principal ; tous régimes
  confondus, il met 26,1 % des hommes au minimum
  (`macro/caracteristiques_retraites.csv`).
- *Ce qui reste de l'écart des hommes.* Contre la Cnav, indépendants compris
  depuis 2019, il n'est plus que de 0,6 point en 2023 ; contre les régimes
  alignés, de 2,1. La différence des deux est la MSA salariés : 29,6 % de ses
  hommes liquidants de 2023 au minimum, pour 10,7 à la Cnav, que la
  population ne distingue pas du régime général. Et l'artisan, 3,9 % des
  hommes, n'y est jamais : ses revenus ont la dispersion de ceux des salariés
  de son sexe, et aucune source du dépôt ne publie celle des revenus des
  indépendants.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur ni témoin. La population passe de 1 494 à 1 396 carrières.
  Les tests (`test_grille_large.py`) : la population sans contractuel, la
  Cnav qui les garde, et les 161 € lus dans les deux fichiers.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : les salariés agricoles, au minimum trois fois
   plus que ceux de la Cnav, s'ils se distinguent ; la dispersion des revenus
   des indépendants, si une source la publie ; la part des générations 1946 à
   1953 au minimum, trop haute ; la fragmentation selon la génération ; la
   décote selon la tranche ou le rang. Les niveaux des cas types statutaires
   et non salariés attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, au-delà de la décote : l'âge publié, la surcote.
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).
