# Étape 14, sixième partie : les salariés agricoles de la population, distingués

**Le 16 octobre 2026 : la mesure du minimum contributif distingue maintenant
les salariés agricoles de la Cnav (`SALARIES_AGRICOLES`). Ils ne se
distinguent presque pas. Les hommes salariés agricoles de la population sont
au minimum pour 10,5 % des liquidants de 2023, ceux de la Cnav pour 10,0 % ;
l'EACR en compte 29,6 et 10,7. Leur rang dans l'EIR n'explique pas cet
écart : il tient à leur carrière, qu'aucune source du dépôt ne mesure. La
part des régimes alignés ne bouge pas, ni la page, ni la distribution de
l'EIR.**

Demande : la vague quinquies du 16 octobre 2026, session 2, « action 138,
étape 14. La population, encore : les salariés agricoles, que l'EACR met au
minimum contributif trois fois plus que ceux de la Cnav ». C'est le point 1 de
« Ce qui reste » dans la note des contractuels.

- *Le droit ne les distingue pas.* Douze carrières du salariat privé de la
  population, prises aux générations 1950, 1958 et 1962, ont été affiliées
  comme `salarie_agricole` au lieu de `salarie_prive_non_cadre`. Elles
  liquident au moteur la même pension de base, sous `msa_salaries` au lieu de
  `regime_general`, la même complémentaire et le même minimum, au centime.
  Une carrière propre ne servirait donc à rien. La population leur donne une
  part de chacune des siennes.
- *La part* (`parts_agricoles`, `fractions_agricoles`, `classe_de`). C'est
  celle de la MSA salariés parmi les retraités du régime général et d'elle,
  dans l'EIR de 2020, au régime principal, monopensionnés et polypensionnés
  de deux régimes compris. Parmi les résidents, chaque quintile de la pension
  en équivalent carrière complète est lu sur la bande de rangs de chaque
  classe de centiles, comme sous `RANG_SELON_LA_DUREE`. On obtient 4,5 % des
  hommes résidents, dont 6,4 % au dixième centile et 3,6 % à la médiane ;
  2,2 % des femmes, mais plus en haut de l'échelle (1,6 % au dixième
  centile, 4,2 % au-delà du quatre-vingt-dixième). Parmi les retraités de
  l'étranger, la part se déduit de tous les retraités moins les résidents :
  12,5 % des hommes, 15,3 % des femmes. Seul le salariat privé en a.
- *La mesure* (`part_minimum_contributif.py --grille population`, nouveau
  tableau). Chaque liquidant se partage entre la Cnav et la MSA salariés. Ce
  qui suit porte sur 2023, entre parenthèses l'EACR :

  | | Cnav | MSA salariés | agricoles parmi les liquidants |
  |---|---|---|---|
  | ensemble | 18,3 % (17,9) | 14,7 % (33,1) | 2,8 % (6,1*) |
  | femmes | 24,8 % (24,5) | 21,6 % (38,3) | 2,0 % (4,7*) |
  | hommes | 10,0 % (10,7) | 10,5 % (29,6) | 3,9 % (7,6*) |

  \* la part que l'EACR laisse déduire : celle des alignés est la moyenne de
  la Cnav et de la MSA salariés, pesée par leurs liquidants. De 2019 à 2024,
  le même dessin revient chaque année : la Cnav de la population est à un
  point au plus de celle de l'EACR, et sa MSA salariés deux à trois fois sous
  celle de l'EACR.
- *Ce que cela dit.* Dans l'EIR, la place des salariés agricoles sur
  l'échelle des pensions par année validée ne diffère guère de celle du
  régime général. L'EACR, lui, les met trois fois plus au minimum, et pèse
  leurs liquidants deux fois plus que l'EIR ses retraités résidents. Les deux
  constats vont ensemble : les liquidants de la MSA salariés ne sont pas ses
  retraités de 2020. Deux pistes l'expliqueraient, et le dépôt n'a de source
  pour aucune. Depuis la liquidation unique de juillet 2017, le dernier
  régime aligné liquide pour tous, et une fin de carrière agricole en fait
  liquider. Et le travail saisonnier, fragmenté bien plus que les bas revenus
  salariaux de la Dares, n'a pas de source. Si la population donnait aux
  agricoles le minimum de l'EACR au poids qu'il en déduit, les hommes des
  alignés passeraient de 10,1 à 11,5 % : cela couvre les deux tiers de leur
  écart à l'EACR, 12,2. Cette part n'est pas recalée : ce serait se caler sur
  l'EACR.
- *Le niveau des hommes, jugé sur l'EIR* (`grille_large.py --grille
  population --distribution`, inchangé par ce qui précède). La population
  met 13,1 % des hommes de 2020 au minimum de pension, l'EIR 9,8 % au
  minimum du régime principal et 26,1 % tous régimes. Au premier quintile,
  c'est 61,2 % contre 48,7 ; aux deuxième et troisième, 18,2 et 14,9 contre
  25,2 et 6,2. L'écart de Kolmogorov reste de +7,5 points à 1 700 €, la
  médiane de 1 585 € contre 1 745. Le stock de l'EIR ne demande donc pas plus
  d'hommes au minimum. Le creux qui reste devant l'EACR est celui des
  liquidants agricoles, non celui des résidents.
- *Ce qui ne bouge pas.* Aucune carrière, aucun poids de la population ;
  la part des alignés, au dixième près ; la distribution ; la page, qui ne
  lit pas la population (action 157) ; aucun moteur ni témoin. Les tests (`test_part_minimum_contributif.py`) : les
  parts de l'EIR, le salariat privé seul, la part déduite de l'EACR.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : la carrière saisonnière des salariés
   agricoles, si une source la publie (MSA, statistiques des salariés
   agricoles ; Dares) ; la dispersion des revenus des indépendants, si une
   source la publie ; la part des générations 1946 à 1953 au minimum, trop
   haute ; la fragmentation selon la génération ; la décote selon la tranche
   ou le rang. Les niveaux des cas types statutaires et non salariés
   attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, au-delà de la décote : l'âge publié, la surcote.
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).
