# Étape 14, quinzième partie : des classes de nature plus fines

**Le 24 octobre 2026 : les classes de nature des carrières pleines sont
quinze par rang, et non plus cinq ; la vingt-sixième version, sur `main`.
Une classe a une nature quand le milieu de son rang passe la part que
l'échantillon interrégimes de cotisants publie : cinq classes arrondissaient
chaque part au cinquième, 40 % de chômeurs pour 30,2 à 41,0 % des hommes
des générations 1942 à 1956, 20 % de malades pour 10,5 à 14,6 % ; quinze
l'arrondissent au quinzième, à un trentième près, pour 11 188 cas types au
lieu de 5 000. Les hommes partent un peu plus en carrière longue, 14,1 % de
ceux de 1950 et non 13,5 (EIR 18,3), 27,4 % de ceux de 1955 et non 26,5
(28,6 chez les nés en 1953) ; les femmes de 1955 un peu moins, 5,1 % et non
5,8 (13,0) ; la distribution de 2020 ne bouge pas. La mesure ne tenait plus
dans la mémoire du conteneur : elle allège désormais les couples qu'elle
garde, cinq fois plus légers. La version reste ; la page ne bouge pas.**

Demande : la vague du 24 octobre 2026, une session par tâche, lancée par le
propriétaire : l'action 138, étape 14, le point suivant du bloc de l'étape,
et lui seul : « des classes de nature plus fines » (« Ce qui reste », point
1, de la note de la quatorzième partie,
`2026-10-24-etape-14-chomage-des-malades.md` : « cinq donnent 40 % de
chômeurs pour 30 à 41 %, 20 % de malades pour 6 à 15 %, sur chacun des deux
rangs désormais »).

- *Ce que cinq classes arrondissaient.* Une classe de nature a le chômage ou
  la maladie quand le milieu de son rang passe au-dessus de la part de ceux
  qui n'en ont pas, le service ou l'AVPF quand il passe au-dessous de la
  part de ceux qui en ont (`classes_de_nature`, `natures_a_leur_part`) : sur
  N classes, chaque part s'arrondit au N-ième le plus proche, à 1/(2N) près.
  Les parts de l'échantillon (`natures_assimilees.csv`), lues à 60 ans, puis
  ce qu'en donnaient cinq classes, et ce qu'en donnent quinze, en pour cent :

  | | 1942 | 1946 | 1950 | 1954 | 1956 |
  |---|---|---|---|---|---|
  | hommes au chômage | 30,2 : 40 · 33,3 | 32,9 : 40 · 33,3 | 32,5 : 40 · 33,3 | 36,9 : 40 · 40 | 41,0 : 40 · 40 |
  | hommes malades | 10,5 : 20 · 13,3 | 10,6 : 20 · 13,3 | 12,6 : 20 · 13,3 | 14,4 : 20 · 13,3 | 14,6 : 20 · 13,3 |
  | hommes à l'AVPF | 1,1 : 0 · 0 | 1,6 : 0 · 0 | 2,5 : 0 · 0 | 3,7 : 0 · 6,7 | 4,4 : 0 · 6,7 |
  | femmes au chômage | 30,0 : 20 · 26,7 | 34,1 : 40 · 33,3 | 37,6 : 40 · 40 | 43,1 : 40 · 40 | 48,2 : 40 · 46,7 |
  | femmes malades | 12,3 : 20 · 13,3 | 15,1 : 20 · 13,3 | 19,4 : 20 · 20 | 22,9 : 20 · 20 | 24,9 : 20 · 26,7 |
  | femmes à l'AVPF | 24,3 : 20 · 26,7 | 31,0 : 40 · 33,3 | 39,8 : 40 · 40 | 43,9 : 40 · 46,7 | 45,5 : 40 · 46,7 |

  Le service du premier cinquième des hommes, la part qui reste aux
  cinquièmes qui ne servent pas avant d'entrer : 18,9 % en 1950, 20 % sous
  cinq classes comme sous quinze ; 35,3 % en 1955, 40 % sous cinq, 33,3 %
  sous quinze. Les « 6 à 15 % » de malades de la note précédente sont, au
  fichier, 10,5 à 14,6 % des hommes et 12,3 à 24,9 % des femmes.
- *Combien de classes.* Le plus grand écart d'une part à celle de
  l'échantillon, en points, sur les générations 1930 à 1974 que la
  population simule, et le nombre de cas types de la population, les
  classes qui ont les mêmes natures à chaque génération n'en faisant
  qu'une :

  | classes par rang | 5 | 10 | 15 | 20 |
  |---|---|---|---|---|
  | chômage, hommes · femmes | 9,8 · 10,0 | 4,7 · 5,0 | 3,1 · 3,3 | 2,5 · 2,4 |
  | maladie, hommes · femmes | 9,5 · 7,7 | 4,6 · 4,9 | 2,8 · 2,9 | 2,4 · 2,3 |
  | AVPF, hommes · femmes | 4,4 · 9,3 | 4,4 · 4,7 | 3,3 · 2,9 | 2,5 · 2,4 |
  | cas types | 5 000 | 7 958 | 11 188 | 17 070 |

  Quinze : chaque classe de cinq se coupe en trois, l'écart tombe sous
  3,3 points, et le nombre impair garde une classe au milieu de chaque rang,
  qui garde le code de son cinquième (`natures_a_leur_part`, inchangée).
  Vingt ne gagnaient pas un point, pour moitié plus de cas types et une
  mesure de quatre heures ; dix laissaient cinq points. Neuf, onze et treize
  classes font 7 176, 10 542 et 10 168 cas types.
- *La vingt-sixième version* (`CLASSES_DE_NATURE`, quinze). Rien d'autre ne
  change : la règle de chaque nature, ses années, le plafond de la classe de
  centiles, que les 225 classes d'un cinquième se partagent comme les 25.
  L'homme né en 1950 du premier cinquième, trois années assimilées : trois
  classes du rang servent, une année ; cinq sont au chômage, trois années ;
  deux classes de la maladie sont malades, quatre années ; le tiers des
  malades est au chômage, la part de tous. 26/15 = 1,73 année par homme, et
  non plus 2,2 ; l'échantillon en donne 1,86 (0,19 de service, 1,08 de
  chômage, 0,55 de maladie, 0,05 d'AVPF), et les années de chaque nature
  s'arrondissent à l'unité.
- *Trouvé en chemin : la mémoire de la mesure.* La mesure garde tous les
  couples simulés de sa grille, chacun entier : la proposition, son autre
  côté, ses cotisations année par année, la survie de ses cinq cohortes en
  n-uplets — 32 Ko le couple, 177 Mo le morceau de deux cents cas types de
  28 générations. La population de quinze classes en fait 56 : au 33e, au
  bout de 53 minutes, le processus qui mesure tenait 6,4 Go, ses quatre
  workers et leurs portages 8 de plus, et le noyau l'a tué, le conteneur
  plafonnant à 15 Go ; ses workers lui ont survécu, à arrêter à la main. Les
  têtes ne lisent d'un couple que son code, sa génération, ses départs, sa
  pension du scénario 1, les parts de ses régimes, sa complétude et sa
  survie (`cohortes_de_l_annee`, `cout._survies_alignees`,
  `cout._masses_regimes`, `controle_eacr.cohortes`) : `en_tetes(alleges=True)`,
  que la mesure et `controle_eacr.py` demandent, les leur donne sans le
  reste, et leurs survies en tableaux de flottants (`alleger`), 6,5 Ko le
  couple, 36 Mo le morceau. La mémoire des calculs garde le morceau entier,
  et la page, `cout._masses`, les couples entiers. Reste ce qu'un worker
  garde, sans borne, des octets de chaque calcul qu'il a fait
  (`memoire._EN_MEMOIRE`), 29 Mo par morceau.
- *Les tests.* Deux de plus, et six épinglés. Les classes de l'homme né en
  1950, posées à la main sur le fichier, et la part de chaque nature des
  deux sexes, aux générations de l'échantillon, à un trentième près de la
  sienne (`test_les_classes_de_nature_plus_fines_…`) ; les têtes de la grille
  du dépôt, ses poids, ses pensions et ses départs, les mêmes sur des couples
  allégés que sur des couples entiers. Les six tests des vingt-troisième à
  vingt-cinquième versions disent leur version seule, cinq classes rendues.
- *La mesure.* Deux arbres figés sur la tête du jour, dd83704, qui porte la
  carrière longue au texte de l'étape 21, l'un rendu à cinq classes :
  `python scripts/grille_large.py --grille population --distribution
  --processus 4 --json <fichier>`, leur `src/` sur le `PYTHONPATH`, l'un
  après l'autre : 101 minutes avec la version, 46 sans, sur les quatre cœurs
  du conteneur, 10,0 et 7,6 Go au plus. « Sans » redonne au dixième la
  mesure de la quatorzième partie : la carrière longue au texte ne déplace
  presque pas la population. La grille du dépôt sort identique des deux
  arbres. Les échecs passent de 5 532 à 11 720, un de plus par cas type
  ajouté, comme avant.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 :

  | | EIR | sans | avec |
  |---|---|---|---|
  | hommes de 1950, avant l'âge légal | 27,6 | 23,4 | 23,9 |
  | hommes de 1950, à l'âge légal | 35,3 | 27,7 | 27,1 |
  | hommes de 1950, carrière longue | 18,3 | 13,5 | 14,1 |
  | hommes de 1955, avant l'âge légal | 40,8 | 37,7 | 38,6 |
  | hommes de 1955, à l'âge légal | 24,4 | 19,2 | 18,3 |
  | hommes de 1955, carrière longue | 28,6 | 26,5 | 27,4 |
  | femmes de 1950, avant l'âge légal | 13,0 | 9,2 | 9,2 |
  | femmes de 1950, carrière longue | 5,1 | 2,9 | 2,9 |
  | femmes de 1955, avant l'âge légal | 21,7 | 11,9 | 11,2 |
  | femmes de 1955, à l'âge légal | 37,5 | 53,2 | 54,0 |
  | femmes de 1955, carrière longue | 13,0 | 5,8 | 5,1 |
  | ensemble 1950, carrière longue | 11,6 | 8,0 | 8,3 |
  | ensemble 1955, carrière longue | 20,5 | 15,7 | 15,8 |

  La décote, la surcote et le taux plein par l'âge ne bougent pas. La
  distribution de 2020 : la pension moyenne des hommes passe de 1 818 à
  1 819 € (EIR 1 957), leur médiane de 1 601 à 1 602 € (1 745), l'écart de
  Kolmogorov reste de +5,3 points à 1 800 € ; celle des femmes reste à
  1 332 € (1 177), à −15,6 points à 900 €. La durée validée de chaque
  génération ne bouge pas, à 0,04 année près ; la part des femmes au
  minimum reste à 30,5 % (EIR 37,7).
- *Ce que cela dit.*
  - Les hommes de 1950 comptent moins de chômeurs, 33,3 % et non 40
    (échantillon 32,5), dont la rédaction de D. 351-1-2 de 2003 ne répute
    pas le chômage cotisé, et moins de malades : 0,6 point de plus en
    carrière longue, l'écart à l'EIR passant de −4,8 à −4,2 points. Ceux de
    1955 comptent moins de malades, 13,3 % et non 20 (14,5), et parmi eux
    moins de malades au chômage, dont les huit trimestres réputés ne
    suffisaient pas : 0,9 point de plus, l'écart passant de −2,1 à −1,2
    point ; avant l'âge légal, de −3,1 à −2,2.
  - Leurs départs à l'âge légal s'en éloignent d'autant, de −7,6 à −8,2
    points en 1950, de −5,2 à −6,1 en 1955 : ceux qui partent désormais en
    carrière longue partaient à l'âge légal. L'excès de la population reste
    à l'âge d'annulation de la décote, que la version ne touche pas.
  - Les femmes de 1955 comptent plus d'AVPF, de chômage et de maladie,
    46,7, 46,7 et 26,7 % et non 40, 40 et 20 (échantillon 44,7, 45,7 et
    23,9), que la carrière longue ne répute pas, ou dans une limite : 0,7
    point de moins en carrière longue, l'écart à l'EIR passant de −7,2 à
    −7,9 points. Celles de 1950, dont les parts arrondies ne changent pas,
    ne bougent pas. Leur écart est ailleurs, les carrières de trente à
    quarante années entrant toutes à 21 ans.
  - Des parts fausses de dix points ne déplaçaient les départs que d'un
    point au plus ; la distribution de 2020 n'en dit rien, un euro.
  - La version reste : chaque part est celle de l'échantillon à un trentième
    près, quand cinq classes s'en écartaient de dix points, et les départs
    anticipés des hommes s'approchent de l'EIR ; ce qui s'en éloigne, chez
    les femmes de 1955, suit des natures désormais plus près de
    l'échantillon.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles ; les
  carrières incomplètes et les départs avec surcote, qui n'ont pas de classes
  de nature ; le registre. Aucune règle du scénario 1 ne change : pas
  d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : les natures selon le rang, quand la masse de
   l'EIR va au bas des rangs ; le plafond de chaque génération, que ses
   classeurs publient pour 1950 et 1953, à certifier, s'il valait de couper
   le haut des rangs ; les natures des carrières incomplètes, qui gardent
   leur chômage quand l'AVPF des femmes qui ont cessé de travailler y est,
   avec son salaire au Smic dans le salaire annuel moyen, et le chômage
   d'après 60 ans de celles qui attendent le taux plein par l'âge ; la
   maternité, que l'échantillon range avec la maladie et que D. 351-1-2
   répute sans limite depuis avril 2014, et que la population tient pour de
   la maladie, quatre trimestres, indépendante de l'AVPF, que rien ne croise
   avec elle ; les femmes en carrière longue, les carrières de trente à
   quarante années, allongées à l'âge légal, entrant toutes à 21 ans ; la
   durée des carrières pleines que la onzième version prend à l'EIR ; les
   invalides et les inaptes, au taux plein dès l'âge légal ; la surcote des
   statutaires ; la décote selon la génération ; la part passagère du revenu
   des indépendants et la carrière saisonnière des salariés agricoles, si une
   source les publie ; le juge propre des artisans, la part des liquidants du
   RSI au minimum contributif d'avant 2020 ; la part des générations 1946 à
   1953 au minimum ; la fragmentation selon la génération ; la décote selon la
   tranche ou le rang. Les niveaux des cas types statutaires et non salariés,
   et la dispersion des libéraux, attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, encore : le départ qui suivrait l'incitation, au
   propriétaire (note de la huitième partie).
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire ; les
   microdonnées de l'échantillon y diraient aussi combien de malades sont au
   chômage.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).

Hors de l'étape : le VI de D. 634-1, la rédaction propre aux artisans et aux
commerçants, à lire rédaction par rédaction (note de la datation) ; ce que
chaque worker garde des calculs qu'il a faits, sans borne
(`memoire._EN_MEMOIRE`), si la population grandit encore.
