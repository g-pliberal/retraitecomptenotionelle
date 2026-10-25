# Étape 14, seizième partie : les natures selon le rang

**Les 24 et 25 octobre 2026 : les natures des femmes d'une carrière pleine
suivent désormais leur rang ; la vingt-septième version, sur `main`. La
part de chaque classe de centiles qui a de la maladie, de l'AVPF ou du
chômage est celle de l'échantillon interrégimes de cotisants, multipliée par
le rapport de la masse assimilée que l'EIR mesure à ses rangs à celle de
toutes les carrières pleines des femmes : 1,80 aux classes p10 et p25, 0,24
aux classes p95 et p99. Le haut n'est plus plafonné, le bas ne garde presque
plus d'années cotisées : les femmes nées en 1950 comptent 4,60 années de ces
natures, et non 3,42, pour 4,53 que l'échantillon leur trouve et 4,69 que la
masse leur permet. Elles partent un peu moins en carrière longue, 2,3 % et
non 2,8 (EIR 5,1), celles de 1955 4,8 % et non 5,0 (13,0) ; la distribution
de 2020 ne bouge pas, à un euro près. Les hommes gardent la même part à
chaque rang : la masse du stock de 2020 remonte au haut des leurs, que ses
générations anciennes portent. La version reste ; la page ne bouge pas.**

Demande : la vague du 24 octobre 2026, une session par tâche, lancée par le
propriétaire : l'action 138, étape 14, le point suivant du bloc de l'étape,
et lui seul : « les natures selon le rang, quand la masse de l'EIR va au bas
des rangs » (« Ce qui reste », point 1, de la note de la quinzième partie,
`2026-10-24-etape-14-classes-de-nature-plus-fines.md`), « d'après la note du
24 octobre sur la masse après 60 ans », celle de la treizième partie.

- *Ce qui était.* La vingt-quatrième version donne leurs natures aux
  carrières pleines à la part de l'échantillon, la même à chaque classe de
  centiles, et la masse assimilée que la classe tient de l'EIR
  (`ASSIMILEES_SELON_LE_RANG`) en est le plafond. Or cette masse va au bas
  des rangs : l'EIR ne cotise pas 26,1 % de la durée validée hors
  majorations des résidentes du premier quintile, 2,6 % de celle du
  cinquième (`quintiles_eqcc_residents.csv`), et la carrière pleine d'une
  femme compte huit années assimilées aux classes p10 à p50, trois à la
  classe p75, deux à la classe p90, une aux classes p95 et p99. Le haut
  était plafonné, le bas gardait des années cotisées : nées en 1950, les
  femmes des classes p10 à p50 avaient 5,00 années de natures pour huit,
  celles des classes p95 et p99 une pour une, quand leurs natures, à la part
  de toutes, en demandaient 4,6 ; en tout 3,42 années, pour les 4,53 que
  l'échantillon trouve à ses affiliées à 60 ans — 2,63 d'AVPF, 1,35 de
  chômage, 0,55 de maladie — et les 4,69 de la masse. La note de la
  treizième partie le disait : « le haut est plafonné, le bas garde des
  années cotisées. C'est la répartition des natures selon le rang, que
  l'échantillon ne publie pas. »
- *La vingt-septième version* (`NATURES_SELON_LE_RANG`, `("F",)`). La part
  des femmes d'une classe qui ont de la maladie, de l'AVPF ou du chômage est
  celle de l'échantillon, multipliée par le rapport de la masse de sa classe
  à celle de toutes les carrières pleines des femmes, leurs classes pesées
  par leur poids (`masses_moyennes`) : 10,82 % de la durée validée hors
  majorations, les classes p10 à p99 en pesant 9,6, 11,0, 20,7, 32,6, 15,5,
  6,4 et 4,3 %. Le rapport vaut 1,80 aux classes p10 et p25, 1,65 à la
  classe p50, 0,63 à la classe p75, 0,38 à la classe p90, 0,24 aux classes
  p95 et p99. Chacune de celles qui en ont garde les années de
  l'échantillon, le cumul se multipliant comme la part (`natures_au_rang`) ;
  rien d'autre ne change — la règle de chaque nature, le rang propre de la
  maladie, les quinze classes, le plafond. Aucune part ne passe un : la plus
  haute, celle du chômage des nées en 1956 aux classes p10 et p25, fait
  86,7 %. L'autre convention, la même part à chaque rang et des années à
  proportion de la masse, aurait donné douze années d'AVPF à 39,8 % des
  femmes de la classe p10, quand l'échantillon en donne 6,6 à chacune de
  celles qui en ont. Les parts de la population en 1950, en pour cent,
  celle de l'échantillon entre parenthèses :

  | 1950 | p10, p25 | p50 | p75 | p90 | p95, p99 |
  |---|---|---|---|---|---|
  | AVPF (39,8) | 73,3 | 66,7 | 26,7 | 13,3 | 6,7 |
  | chômage (37,6) | 66,7 | 60,0 | 26,7 | 13,3 | 6,7 |
  | maladie (19,4) | 33,3 | 33,3 | 13,3 | 6,7 | 6,7 |
  | aucune des trois | 0 | 0 | 40,4 | 68,4 | 80,9 |
  | années de natures · masse | 8,07 · 8 | 8,07 · 8 | 2,80 · 3 | 1,67 · 2 | 0,93 · 1 |

  Nées en 1955, les femmes comptent 4,75 années de natures, et non 3,80,
  pour 5,11 que l'échantillon interpole entre 1954 et 1956 : la masse, 4,69,
  les plafonne désormais à chaque rang, et non plus au seul haut.
- *Pourquoi les femmes seules.* La masse du stock de 2020 ne va pas au bas
  des rangs des hommes : 12,5 % de la durée validée hors majorations des
  résidents des deux premiers quintiles, 4,9 % du troisième, 7,5 du
  quatrième, 9,8 du cinquième, que la population lit 11,3 % à la classe
  p10, 7,4 et 6,5 % aux classes p25 et p50, 8,8 à la classe p75, 9,8 aux
  classes p90 à p99. Appliquée aux hommes, la règle mettrait aux classes
  p90 à p99 1,16 fois la part de chômeurs et de malades de l'échantillon, à
  la classe p50 0,77 fois. Or cette remontée tient aux générations
  anciennes du stock : aux trois quintiles du haut, les classeurs des nés en
  1950 et en 1953, non certifiés, trouvent aux hommes moins de durée non
  cotisée que le stock (note de la treizième partie) ; chez les femmes, la
  masse de la génération vaut celle du stock, à un point près. Les hommes
  gardent la même part à chaque rang, sous un plafond qui ne tient presque
  nulle part : 1,69 année de natures en 1950, pour 3,67 de masse. Leur pente
  attend les classeurs de leur génération, à certifier.
- *Les tests.* Un de plus,
  `test_les_natures_des_femmes_suivent_la_masse_de_leur_rang` : la masse
  moyenne des carrières pleines des femmes, 10,82 %, leurs têtes comptées ;
  les rapports de la classe p99, un trente-neuvième, 0,237, et de la classe
  p10, 1,80 ; les classes des nées en 1950, posées à la main — à la classe
  p99, 39,8 × 0,237 = 9,4 % d'AVPF, 37,6 × 0,237 = 8,9 % de chômage,
  19,4 × 0,237 = 4,6 % de maladie, une classe de quinze chacune, qui garde
  les années de l'échantillon, sept, quatre et trois ; à la classe p10, 71,6,
  67,6 et 34,9 %, onze, dix et cinq classes — ; à chaque génération de
  l'échantillon, de 1942 à 1956, la part de chaque nature à chaque classe et
  sur toutes, à un trentième près ; aux hommes, la même part à chaque rang.
  Vu rouge sans la version, la classe p99 gardant la part de toutes. Les
  autres tests de la population ne bougent pas : ceux des versions
  précédentes portent sur les hommes, ou ôtent la vingt-quatrième.
- *Trouvé en chemin : la population grandit.* Les classes qui ont les mêmes
  natures à chaque génération n'en faisant qu'une, des parts qui changent
  d'une classe de centiles à l'autre en font plus : 14 738 cas types, et non
  plus 11 188.
- *La mesure.* Deux arbres figés sur la tête du jour, a06f1cf, l'un portant
  la version : `python scripts/grille_large.py --grille population
  --distribution --processus 4 --json <fichier>`, leur `src/` sur le
  `PYTHONPATH`, l'un après l'autre : 93 minutes sans la version, 119 avec,
  sur les quatre cœurs du conteneur, 10,7 et 12,6 Go au plus. La grille du
  dépôt sort identique des deux arbres ; les échecs passent de 11 720 à
  15 270, un de plus par cas type ajouté, comme avant. « Sans » s'écarte de
  la mesure de la quinzième partie, faite sur dd83704, aux départs d'avant
  l'âge légal des hommes hors carrière longue — 22,1 % et non 23,9 en 1950,
  37,1 et non 38,6 en 1955 —, le modèle ayant bougé depuis, le poids du
  militaire de l'étape 3 (c90b82b) entre autres ; la carrière longue, à un
  dixième près. Près de deux heures, c'est la limite d'une tâche de fond de
  Claude Code, qui a coupé la mesure une fois, au bout de cinquante minutes,
  l'attente de la première comprise : la lancer détachée (`setsid nohup`),
  et l'attendre à part.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 :

  | | EIR | sans | avec |
  |---|---|---|---|
  | femmes de 1950, avant l'âge légal | 13,0 | 9,0 | 8,5 |
  | femmes de 1950, à l'âge légal | 44,4 | 46,0 | 46,5 |
  | femmes de 1950, carrière longue | 5,1 | 2,8 | 2,3 |
  | femmes de 1955, avant l'âge légal | 21,7 | 11,0 | 10,8 |
  | femmes de 1955, à l'âge légal | 37,5 | 54,1 | 54,4 |
  | femmes de 1955, carrière longue | 13,0 | 5,0 | 4,8 |
  | ensemble 1950, carrière longue | 11,6 | 8,3 | 8,0 |
  | ensemble 1955, carrière longue | 20,5 | 15,7 | 15,6 |

  Les hommes ne bougent pas : 14,2 % en carrière longue en 1950 (EIR 18,3),
  27,4 en 1955 (28,6). La décote, la surcote et le taux plein par l'âge ne
  bougent pas. La distribution de 2020 : la pension moyenne des femmes passe
  de 1 340 à 1 339 € (EIR 1 177), leur médiane de 1 276 à 1 275 € (1 013),
  l'écart de Kolmogorov reste de −15,8 points à 900 € ; celle des hommes ne
  bouge pas. La durée validée de chaque génération ne bouge pas, à 0,1 année
  près ; la part des femmes au minimum passe de 30,3 à 30,2 % (EIR 37,7).
- *Ce que cela dit.*
  - Les natures des femmes sont désormais celles de l'échantillon en somme,
    4,60 années pour 4,53 en 1950, et, rang par rang, celles que la masse de
    l'EIR permet : chaque classe en remplit de 0,83 à 1,01 fois la sienne,
    quand les versions précédentes laissaient aux classes du bas trois
    années cotisées sur huit.
  - Leurs départs anticipés s'éloignent un peu de l'EIR, d'un demi-point au
    plus : l'AVPF et le chômage, que la carrière longue ne répute pas
    cotisés, ou dans une limite, vont au bas des rangs, où toutes les femmes
    des classes p10 à p50 ont désormais l'un ou l'autre, et ce que le haut,
    qui en est presque libre, y gagne ne le compense pas. Leurs départs à
    l'âge légal s'en éloignent d'autant.
  - La distribution de 2020 n'en dit rien : un euro.
  - La version reste : la convention — la part de chaque nature à proportion
    de la masse de son rang — tient à la fois l'échantillon, à un trentième
    près, et la masse de l'EIR, rang par rang, quand la vingt-quatrième ne
    tenait que le premier ; l'écart des femmes en carrière longue à l'EIR est
    ailleurs, les carrières de trente à quarante années entrant toutes à
    21 ans.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles ; les
  hommes ; les carrières incomplètes et les départs avec surcote, qui n'ont
  pas de classes de nature ; le registre. Aucune règle du scénario 1 ne
  change : pas d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : le plafond de chaque génération, que ses
   classeurs publient pour 1950 et 1953, à certifier, s'il valait de couper
   le haut des rangs, et avec eux la pente des natures des hommes selon le
   rang ; les natures des carrières incomplètes, qui gardent leur chômage
   quand l'AVPF des femmes qui ont cessé de travailler y est, avec son salaire
   au Smic dans le salaire annuel moyen, et le chômage d'après 60 ans de
   celles qui attendent le taux plein par l'âge ; la maternité, que
   l'échantillon range avec la maladie et que D. 351-1-2 répute sans limite
   depuis avril 2014, et que la population tient pour de la maladie, quatre
   trimestres, indépendante de l'AVPF, que rien ne croise avec elle ; les
   femmes en carrière longue, les carrières de trente à quarante années,
   allongées à l'âge légal, entrant toutes à 21 ans ; la durée des carrières
   pleines que la onzième version prend à l'EIR ; les invalides et les
   inaptes, au taux plein dès l'âge légal ; la surcote des statutaires ; la
   décote selon la génération ; la part passagère du revenu des indépendants
   et la carrière saisonnière des salariés agricoles, si une source les
   publie ; le juge propre des artisans, la part des liquidants du RSI au
   minimum contributif d'avant 2020 ; la part des générations 1946 à 1953 au
   minimum ; la fragmentation selon la génération ; la décote selon la
   tranche ou le rang. Les niveaux des cas types statutaires et non salariés,
   et la dispersion des libéraux, attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, encore : le départ qui suivrait l'incitation, au
   propriétaire (note de la huitième partie).
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire ; les
   microdonnées de l'échantillon y diraient aussi combien de malades sont au
   chômage, et la part de chaque nature selon le rang.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).

Hors de l'étape : le VI de D. 634-1, la rédaction propre aux artisans et aux
commerçants, à lire rédaction par rédaction (note de la datation) ; ce que
chaque worker garde des calculs qu'il a faits, sans borne
(`memoire._EN_MEMOIRE`) : la population a grandi d'un tiers, la mesure tient
12,6 Go au plus sous les 15 du conteneur, et une version qui la grandirait
encore d'un quart n'y tiendrait plus sans le borner.
