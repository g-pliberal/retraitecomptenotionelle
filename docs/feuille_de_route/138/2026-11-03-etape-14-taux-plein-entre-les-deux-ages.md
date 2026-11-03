# Étape 14, la trente-cinquième version : le taux plein entre les deux âges, les femmes qui complètent leur durée

**Le 3 novembre 2026 : une part des femmes à qui leur durée manque à l'âge
légal la complètent en validant encore, et partent au taux plein entre l'âge
légal et l'âge d'annulation de la décote ; la trente-cinquième version, sur
`main` (12645e5). Chez les nées en 1955, le taux plein entre les deux âges,
autrement que par la surcote ou la décote, passe de 0,5 point à 4,0, ce que
l'EIR trouve par la durée seule aux nées en 1953 (8,3 en tout), et
l'entre-deux, de 22,1 % des départs à 25,6 % (26,7). Mais ces femmes viennent
de l'âge d'annulation, qui tombe de 9,9 % à 6,4 % (10,8) ; l'âge légal garde
son excès, 48,7 % pour 37,5, et la somme des écarts des femmes, place par
place, ne bouge pas : leurs carrières sont trop longues (« Ce qui reste »,
point 3). Les hommes ne changent pas : leur taux plein entre les deux âges,
qui passe l'EIR, vient de l'artisan d'une carrière pleine, entré à 24 ans, et
des fonctionnaires, que cette version ne touche pas — une question au
propriétaire. Une simulation, deux pesées. La version reste ; la page ne
bouge pas.**

Demande : la troisième vague, lancée dans la nuit du 2 au 3 novembre 2026 par
la session d'orchestration, file I : l'action 138, étape 14, le premier point
de la file, « le taux plein entre les deux âges », que la note de la trente
et unième version détaille (« Ce qui reste », point 1,
`2026-10-28-etape-14-departs-entre-les-deux-ages.md`).

- *Ce qui était.* Étalées jusqu'à 60 ans (`AGE_FIN_ETALEMENT`), les
  carrières incomplètes ne valident plus rien après : la jumelle du taux plein
  de celle à qui sa durée manque à l'âge légal attend l'âge d'annulation,
  inactive, au taux plein par l'âge. Née en 1955, la femme d'une carrière de
  vingt à trente ans du salariat privé valide 35 années, celles que le calage
  de la durée des femmes donne à sa génération, et seize trimestres de ses
  deux enfants : à 62 ans, il lui en manque dix des 166 ; elle attend 67 ans.
  La note de la trente et unième version trouvait 0,5 point de femmes de 1955
  au taux plein entre les deux âges, autrement que par la surcote ou la
  décote, quand l'EIR en voit 8,3 chez les nées en 1953, dont 4,0 par la
  durée ; et 17,2 points d'hommes, pour 8,9, dont 5,7 par la durée.
- *Le diagnostic*, sur la population de `main` (203a549), chaque carrière de
  la génération 1955 datée au portage (48 secondes pour 18 946 carrières) et
  pesée de son poids de retraitée de 2022, sans le recalage de la page : 0,2
  point de femmes au taux plein entre les deux âges, autrement ; chez les
  hommes, 12,6, la surcote des statutaires (9e6dbbd) en ayant pris une part,
  dont 6,0 de l'artisan d'une carrière pleine, entré à 24 ans, au taux plein
  à 65 ans et demi, 3,6 des sédentaires de l'État, 2,5 des agents de la
  CNRACL, 0,4 du salariat privé. Les femmes que l'âge d'annulation retient,
  11,0 points (EIR 10,8), sont les jumelles du taux plein des carrières de
  vingt à trente ans (3,8), de dix à vingt (3,2), de moins de dix (2,2) ;
  celles de vingt à trente ans seules ont une durée à compléter avant lui.
- *La trente-cinquième version* (`DUREES_COMPLETEES`, `SEXES_QUI_COMPLETENT`,
  `GENERATION_DES_DUREES_COMPLETEES`, `par_la_duree_entre_les_deux_ages`,
  `peut_completer`, `qui_complete`, `durees_completees`,
  `parts_qui_completent`, `completer_les_durees`, `CasTypeLarge.completee`,
  `Variante.complete` ; 12645e5). Après la décote, avant la déclinaison par le
  rang, la jumelle du taux plein de chaque carrière incomplète de femme se
  décline : une part, la même chez toutes, valide chaque année depuis l'âge
  légal de sa génération, l'année où elle l'atteint comprise, jusqu'à son
  taux plein, sous son code suivi de « ~complete » ; le reste attend comme
  avant. Elle ne le fait qu'aux générations simulées où elle part ainsi entre
  les deux âges, à un mois et demi près (`TOLERANCE_DE_PLACE`) : sa durée lui
  manque à l'âge légal, et elle la complète avant l'âge d'annulation ;
  ailleurs, elle a la carrière et le départ de sa sœur. Le jugement se fait
  au portage, aux vingt-neuf générations de la grille, au salaire du cas
  type : la carrière de vingt à trente ans du salariat privé complète de 1955
  à 1970 — à 64 ans et demi en 1955, 63 ans et trois quarts en 1960 —, non en
  1950, où elle n'a que 30 années et en manque six et demie ; celle de trente
  à quarante ans, de 1930 à 1945 ; l'artisane, l'exploitante et la libérale
  de même, la libérale de trente à quarante ans, entrée à 27 ans, depuis
  1950. La part, 90,15 %, donne à la génération simulée 1955, au poids de
  1953 de ses jumelles, les départs par la durée entre les deux âges que
  l'EIR trouve aux nées en 1953, 26,7 % fois 15,1 %, parmi toutes les
  retraitées, comme la trentième version rapporte la décote. La population
  passe de 18 946 cas types à 19 352, 406 jumelles. Trois conventions : la
  jumelle garde les années de sa sœur, inactive entre la fin de leur
  étalement et l'âge légal ; elle se juge au salaire de son cas type, comme
  la décote ; sa part ne dépend ni de la tranche, ni du rang, ni de la
  génération.
- *Les hommes* (`SEXES_QUI_COMPLETENT`) n'en reçoivent pas : leurs carrières
  incomplètes, à 35 années et moins, n'ont rien à compléter avant l'âge
  d'annulation, et leur taux plein entre les deux âges passe déjà l'EIR, par
  des carrières pleines. L'artisan entre à 24 ans, l'âge du cas type du dépôt,
  sans années salariées avant, quand les carrières pleines du salariat
  entrent à celui de leur génération : 38 années à 62 ans. L'y faire entrer
  le ferait partir à l'âge légal, où le salariat donne déjà aux hommes de
  1955, au diagnostic, les départs par la durée de l'EIR (10,9 points pour
  11,6), ou en carrière longue ; aucune source d'ici ne dit la durée des
  anciens artisans, ni leur âge de départ. Les sédentaires de l'État partent
  à l'âge et avec la surcote que le jaune leur trouve, mais sans décote, quand
  il en voit 18 % de ses liquidants civils de 2025 (tableau 104).
- *Les tests* (`test_grille_large.py`, trois de plus).
  `test_le_taux_plein_par_la_duree_entre_les_deux_ages_se_lit_dans_l_eir`
  relit au fichier certifié les 26,7 % et 15,1 % des femmes, les 26,4 % et
  21,7 % des hommes. `test_une_femme_qui_complete_sa_duree_part_entre_les_deux_ages`
  pose à la main la femme de 1955 de la classe médiane : 4 × 35 + 2 × 8 = 156
  trimestres à 62 ans (L. 351-4), dix de moins que les 166 de sa génération
  (L. 161-17-3) ; sa sœur part à 67 ans au taux plein par l'âge (L. 351-8,
  1°), avec 156 trimestres ; elle, à 64 ans et demi, avec 166 ; née en 1940,
  elle a la carrière et l'âge de sa sœur ; aucun homme ne complète.
  `test_les_femmes_qui_completent_leur_duree_pesent_la_part_de_l_eir` refait
  la part sur la population : la même pour toutes les jumelles, celle qui
  donne à la génération 1955 les 4,0 % de l'EIR. Vus rouges faute de la
  version. Deux tests anciens comptent désormais la jumelle qui complète :
  celui des invalides et des inaptes, dont la jumelle qui complète n'a pas
  d'inapte, celle-ci étant prise avant elle, et celui des carrières allongées,
  dont le poids se lit avec elle. Les 94 tests du fichier passent en 97 s ;
  la suite rapide, 3 726 tests.
- *La mesure.* Une simulation, deux pesées, sur un arbre figé : 203a549 et la
  version (223f0f4, dont la grille et ses tests sont ceux de 12645e5). La
  population de la trente-cinquième version, 19 352 cas types, qui contient
  celle de la trente-quatrième (18 946), se simule une fois au portage, en 25
  tranches de 800 cas types gardées sur le disque, un redémarrage du
  conteneur ayant emporté une première course après 22 minutes : 98 minutes
  sur quatre cœurs, 541 265 couples, 19 943 échecs (16 926 liquidations
  antérieures à la répartition, 3 017 carrières sans régime actif). Puis elle
  se pèse deux fois, `DUREES_COMPLETEES` éteinte puis allumée, 33 minutes
  chacune (un pilote hors du dépôt, qui appelle les fonctions du script, sans
  la mémoire des calculs) ; 10,2 Gio au plus, l'arbre de ses processus compté
  entier. La pesée rapide du diagnostic trouvait les mêmes déplacements, à
  deux dixièmes près.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 ; « dont », la part des départs de la génération pris à cette
  place dans cette condition ; « taux plein, autrement » : par la durée,
  invalides, inaptes, décote inapplicable :

  | | EIR | trente-quatrième | trente-cinquième |
  |---|---|---|---|
  | femmes de 1955, avant l'âge légal | 21,7 | 17,5 | 17,5 |
  | femmes de 1955, à l'âge légal | 37,5 | 48,8 | 48,7 |
  | dont au taux plein, autrement | 31,6 | 42,3 | 42,3 |
  | femmes de 1955, entre lui et l'âge d'annulation | 26,7 | 22,1 | 25,6 |
  | dont avec une décote | 5,4 | 6,0 | 6,0 |
  | dont avec une surcote | 12,1 | 15,6 | 15,7 |
  | dont au taux plein, autrement | 8,3 | 0,5 | 4,0 |
  | femmes de 1955, à l'âge d'annulation | 10,8 | 9,9 | 6,4 |
  | dont au taux plein par l'âge | 9,3 | 9,2 | 5,8 |
  | femmes de 1955, après lui | 3,3 | 1,8 | 1,8 |
  | hommes de 1955, à l'âge légal | 24,4 | 24,8 | 24,8 |
  | hommes de 1955, entre les deux âges | 26,4 | 30,9 | 31,0 |
  | dont au taux plein, autrement | 8,9 | 12,3 | 12,4 |
  | hommes de 1955, à l'âge d'annulation | 5,5 | 5,7 | 5,7 |
  | ensemble de 1955, à l'âge légal | 31,2 | 37,4 | 37,3 |
  | ensemble de 1955, entre les deux âges | 26,6 | 26,3 | 28,2 |
  | ensemble de 1955, à l'âge d'annulation | 8,3 | 7,9 | 6,0 |
  | femmes de 1950, à l'âge légal | 44,4 | 50,4 | 50,4 |
  | femmes de 1950, entre les deux âges | 22,4 | 24,3 | 25,0 |
  | dont au taux plein, autrement | 10,1 | 5,5 | 6,1 |
  | femmes de 1950, à l'âge d'annulation | 15,3 | 15,7 | 15,1 |
  | hommes de 1950, entre les deux âges | 25,4 | 34,3 | 34,3 |
  | dont au taux plein, autrement | 12,4 | 18,9 | 18,9 |

  Les 3,5 points de jumelles de 1955 sont des salariées du privé pour 2,95,
  des libérales pour 0,33, des exploitantes pour 0,14, des artisanes pour
  0,10 ; les hommes de 1955 au taux plein entre les deux âges, autrement,
  l'artisan pour 5,0, les fonctionnaires sédentaires pour 3,6 et actifs pour
  3,4, le salariat privé pour 0,3. Et les retraités de 2020 contre l'EIR,
  ceux de 2024 contre l'EACR (la décote du régime général contre celle de la
  Cnav) :

  | | EIR, EACR | trente-quatrième | trente-cinquième |
  |---|---|---|---|
  | retraitées de 2020 parties avec une décote | 8,8 | 8,7 | 8,6 |
  | retraités de 2020 partis avec une décote | 4,5 | 6,0 | 6,0 |
  | premier quintile des femmes, décote | 17,5 | 21,0 | 20,8 |
  | part des femmes parmi les retraités de 2020 | 54,0 | 50,3 | 50,5 |
  | pension moyenne des femmes en 2020, € par mois | 1 177 | 1 336 | 1 348 |
  | premier décile des femmes | 283 | 406 | 408 |
  | pension moyenne des hommes en 2020 | 1 957 | 1 829 | 1 831 |
  | liquidants de 2024 du régime général, décote | 13,4 | 17,1 | 17,1 |
  | liquidants de 2024 partis à 62 ans | 26,0 | 53,9 | 55,5 |
  | à 63 ans | 18,6 | 6,5 | 6,6 |
  | à 64 ans | 7,0 | 4,4 | 4,7 |
  | à 65 ans | 7,1 | 11,6 | 11,6 |
  | à 67 ans | 10,6 | 9,3 | 7,4 |
  | âge moyen des liquidants de 2024 | 63,60 | 62,56 | 62,47 |

  L'écart de Kolmogorov des femmes passe de −14,5 points à 900 € à −15,4 à
  1 200 €, celui des hommes de +4,5 à +4,4 à 1 800 €. Les artisanes et
  commerçantes retraitées de 2020 touchent 1 111 € par mois en moyenne, et
  non 1 093 ; les hommes, 1 330, comme avant.
- *Ce que cela dit.*
  - Le taux plein par la durée entre les deux âges des femmes de 1955 est
    celui de l'EIR, 4,0 points, la part les y mettant à la génération qui la
    fixe. Ce n'est pas tout leur taux plein entre les deux âges, 8,3 points :
    3,7 sont des invalides et des inaptes, que la trente-deuxième version
    fait partir à l'âge légal (« Ce qui reste », point 4), le reste, de la
    décote inapplicable et d'autres motifs.
  - Ces femmes viennent de l'âge d'annulation, non de l'âge légal : il perd
    3,5 points, 6,4 % pour 10,8, le taux plein par l'âge 5,8 pour 9,3 ; l'âge
    légal garde les siens, 48,7 % pour 37,5, dont 42,3 au taux plein
    autrement pour 31,6. Sur les cinq places, la somme des écarts à l'EIR des
    femmes de 1955 ne bouge pas, 22,5 points puis 22,4 ; celle des femmes de
    1950 croît d'un demi-point, 16,7 puis 17,2 ; celle de l'ensemble de 1955,
    de 12,5 à 15,6, l'excès des hommes entre les deux âges ne compensant plus
    le manque des femmes. Les femmes du modèle ont leur durée à l'âge légal
    quand celles de l'EIR en manquent encore : la jumelle ne trouve à
    compléter que celles qui attendent. Le calage de la durée des femmes en
    est la cause (point 3) ; revu, il ferait manquer leur durée à l'âge légal
    à des femmes qui l'y ont ; la part, recalculée sur ce vivier plus grand,
    baisserait, et le reste attendrait l'âge d'annulation.
  - La version reste, pour cette raison : elle tient le taux plein par la
    durée entre les deux âges à celui de l'EIR, tant que le vivier y suffit,
    et le calage de la durée, qui doit vider l'âge légal, remplira par elle
    l'âge d'annulation. Éteinte, ce calage remplirait l'âge d'annulation
    seul, et l'entre-deux resterait vide.
  - Son prix : la jumelle part avec sa durée entière, et non 156 trimestres
    sur 166, après deux ans et demi de plus validés. La pension moyenne des
    retraitées de 2020 monte de 12 €, 1 348 pour 1 177, celle des artisanes
    et commerçantes de 18 €. Elles partent plus tôt : leur part parmi les
    retraités de 2020 monte de 50,3 % à 50,5 % (54,0) ; les liquidants de
    2024 à 67 ans passent de 9,3 % à 7,4 % (10,6), la jumelle de la
    génération 1955 de la grille, partie à 64 ans et demi, l'étant avant
    2024, et leur âge moyen descend de 62,56 ans à 62,47 (63,60). Les hommes
    ne bougent que d'un dixième.
  - Les femmes de 1950 gagnent 0,6 point au taux plein entre les deux âges,
    l'artisane et la libérale de trente à quarante ans, que l'âge
    d'annulation perd ; leur salariée de vingt à trente ans, 30 années, n'en
    gagne pas : il lui manque six années et demie à 60 ans, plus que les cinq
    qui la séparent de l'âge d'annulation.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les hommes, les carrières
  pleines et les statutaires ; la décote, ses parts et ses attentes ; le
  registre. Aucune règle du scénario 1 ne change : pas d'entrée au journal de
  veille. Aucun fichier d'une autre file n'est touché.

**Ce qui reste** de l'étape : les autres points du bloc de l'étape, et, de
celui-ci :

1. *Les hommes entre les deux âges* : 12,4 points au taux plein autrement
   pour 8,9 — l'artisan d'une carrière pleine, entré à 24 ans (5,0), les
   fonctionnaires sédentaires (3,6) et actifs (3,4), sans décote quand le
   jaune en voit 18 % chez ses liquidants civils de 2025 ; au propriétaire,
   faute de source sur la carrière des anciens artisans (la question du
   compte rendu).
2. *Les femmes de 1950* : 6,1 points au taux plein autrement entre les deux
   âges pour 10,1, dont 6,5 par la durée ; leurs carrières de vingt à trente
   ans et de dix à vingt ne complètent pas avant 65 ans.
3. *Le calage de la durée des femmes*, qui porte la carrière de trente à
   quarante ans des nées en 1955 à 44 années, et laisse l'âge légal trop
   chargé, 48,7 % pour 37,5 ; revu, il rendra à l'âge d'annulation ce que
   cette version lui prend.
4. *Les invalides et les inaptes entre les deux âges*, que la trente-deuxième
   version fait partir à l'âge légal (note de la trente et unième version,
   point 2).
