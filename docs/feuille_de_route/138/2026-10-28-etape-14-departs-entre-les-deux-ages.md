# Étape 14, la trente et unième version : les départs entre l'âge légal et l'âge d'annulation

**Le 28 octobre 2026 : les départs avec décote se prennent aussi entre l'âge
légal et l'âge d'annulation de la décote, comme ceux des nés en 1953 ; la
trente et unième version, sur `main` (57e195b, puis 90e13aa, qui met l'attente
à l'échelle de l'écart des deux âges). Chez les femmes de 1955, la décote se
partage désormais comme dans l'EIR : 6,6 points à l'âge légal et 6,2 entre les
deux âges, pour 5,8 et 5,4 ; elles partent pour 14,7 % entre les deux âges et
non 8,5 (26,7), pour 47,6 % à l'âge légal et non 53,9 (37,5). Le reste de
l'écart n'est pas de la décote : il tient au taux plein entre les deux âges
— 0,5 point de femmes pour 8,3, dont 4,0 par la durée ; 17,2 d'hommes pour
8,9 — et à la surcote. Les décotés du stock de 2020 et les liquidants de 2024
se rapprochent de l'EIR et de l'EACR. Une simulation, quatre pesées, avec et
sans la trente-deuxième version. La version reste ; la page ne bouge pas.**

Demande : la vague du 28 octobre 2026, une session par tâche, lancée par le
propriétaire (« Lance une session par tâche qui n'a pas besoin de moi ») :
l'action 138, étape 14, le point du bloc de l'étape « les départs entre l'âge
légal et l'âge d'annulation », que la note de la vingtième partie détaille
(« Ce qui reste », point 1, `2026-10-25-etape-14-decote-des-carrieres-qui-le-peuvent.md`) ;
sept autres sessions mènent en même temps les autres points de l'étape, sur
la même population.

- *Ce qui était.* Étalées jusqu'à 60 ans (`AGE_FIN_ETALEMENT`), les carrières
  incomplètes ne valident plus rien à l'âge légal : leur jumelle qui décote y
  partait, à l'ouverture du droit ; celle du taux plein y part si sa durée y
  est, à l'âge d'annulation sinon ; aucune entre les deux. Entre les deux ne
  partaient que les départs avec surcote, et les carrières qui valident
  encore.
- *Ce que l'EIR dit de l'entre-deux* (`departs_generations.csv`). Des 26,7 %
  de femmes nées en 1953 parties entre l'âge légal et l'âge d'annulation,
  12,1 points surcotent, 5,4 décotent, 4,0 ont le taux plein par la durée,
  3,7 sont invalides ou inaptes ; des 26,4 % d'hommes, 12,4, 4,6, 5,7 et 2,9.
  Les départs avec décote se partagent entre l'âge légal (5,8 points de
  femmes, 2,7 d'hommes), l'entre-deux (5,4 et 4,6) et l'avant (1,2 et 1,3,
  des statuts qui ouvrent plus tôt) ; âge par âge, ceux de l'entre-deux
  s'étalent du reste de l'année de l'âge légal (0,5 point de femmes) à 62 ans
  (1,7), 63 (1,0), 64 (1,2), 65 (0,8) et aux deux mois de 66 ans d'avant
  l'annulation (0,3). Chez les nés en 1950, 60 % des femmes décotées partent à
  l'âge légal, 41 % des hommes ; chez les nés en 1953, 51 et 37 %.
- *La trente et unième version* (`DECOTE_ENTRE_LES_DEUX_AGES`,
  `attentes_des_decotes`, `ages_legaux`, `echelles_des_attentes` ; 57e195b,
  90e13aa). La jumelle qui décote de chaque carrière incomplète se décline en
  trois, comme les départs avec décote des nés en 1953 après leur âge légal :
  celle de l'âge légal même, qui garde son code et n'attend pas — 51,4 % du
  poids de la jumelle chez les femmes, 36,5 % chez les hommes — ; celle des
  deux premières années, qui attend un an et deux mois chez les femmes, un an
  et un mois chez les hommes — 19,6 et 21,7 % — ; celle des autres, jusqu'à
  l'âge d'annulation, trois ans et cinq mois, trois ans et sept mois — 29,1 et
  41,8 %. L'âge légal pèse sa place dans la génération fois sa part de
  décotés, au tableau des places de l'EIR ; chaque âge de liquidation de même,
  au tableau des âges, l'année de l'âge légal sans ses départs de l'âge légal
  même, au milieu de l'âge, borné par l'âge d'annulation l'année où il tombe ;
  les groupes sont ceux de la surcote (`PREMIERES_ANNEES`), le dernier
  réunissant l'année de l'annulation. Les trois jumelles partent à
  l'ouverture du droit, leur attente après l'âge légal de leur génération, à
  toute génération, quand la surcote n'attend que depuis 2004 ; ensemble,
  elles pèsent ce que pesait la jumelle, de la même part de leur génération.
  Deux conventions : la jumelle qui attend ne valide rien de plus, sa
  carrière restant celle de sa tranche, si bien que sa décote ne baisse que
  de l'âge, quand la durée ne la borne pas ; ses attentes sont celles des nés
  en 1953 à toutes les générations, et ne dépendent pas du rang. La population
  passe de 14 874 cas types à 16 114 (de 15 494 à 16 734 sous la
  trente-deuxième version).
- *Trouvé en chemin : l'écart des deux âges.* Nés depuis 1970, les retraités
  ont trois ans entre l'âge légal, 64 ans, et l'annulation de leur décote,
  67 ans ; nés en 1965, quatre ans et trois mois ; nés en 1953, cinq. La
  jumelle qui attendait trois ans et cinq mois partait à 67 ans et cinq mois,
  après l'âge d'annulation, au taux plein, et sa génération perdait de sa
  décote. Elle attend désormais la même part de l'écart des deux âges de sa
  génération que les nés en 1953 (`echelles_des_attentes`, 90e13aa) : trois
  cinquièmes chez les nés depuis 1970. Aucune génération que la mesure lit,
  de 1950 à 1960, n'en bouge : leur écart est de cinq ans.
- *Les tests* (`test_grille_large.py`, quatre de plus).
  `test_l_attente_des_departs_avec_decote_se_lit_dans_l_eir` refait à la main
  les trois attentes et leurs parts, des valeurs que les classeurs impriment ;
  `test_les_departs_avec_decote_attendent_comme_ceux_des_nes_en_1953`, la
  déclinaison : chaque jumelle qui attend a sa sœur immobile, sa part de
  génération et le rapport de poids de son attente ;
  `test_un_depart_avec_decote_qui_attend_decote_moins` pose la femme née en
  1955 d'une carrière de dix à vingt ans de la classe médiane : à 62 ans, elle
  liquide au taux de 50 − 20 × 0,625 = 37,5 % (R. 351-27, L. 351-8, 1°) ;
  après un an et deux mois, il lui manque seize trimestres, 40 % ; après trois
  ans et cinq mois, sept, 45,625 % ; ses trimestres ne bougent pas, et, née en
  1940, elle attend autant après 60 ans ;
  `test_l_attente_d_un_depart_avec_decote_suit_l_ecart_des_deux_ages`, la même
  née en 1970, qui attend trois cinquièmes et décote encore. Les trois
  premiers, vus rouges faute de la fonction et de la constante ; le
  quatrième, à 65,14 ans pour 64,68. Les 87 tests du fichier passent, mêlés à
  ceux de la trente-deuxième version et de la surcote des statutaires, arrivés
  le même jour ; la suite rapide a sept rouges qui ne sont pas d'elle, les deux
  moteurs confrontés sur le paquet du portage (`moteur/donnees.json`), fabriqué
  à 71bdc58 et que les points de chef majorés (e9316a5) ont devancé, rouges
  sans la version aussi : GitHub le refait.
- *La mesure.* Une simulation, quatre pesées : la population de `main` figée à
  86349d8 (`CALCULS_SANS_MEMOIRE=1`, son `src/` sur le `PYTHONPATH`,
  détachée), avec et sans la trente et unième version, avec et sans la
  trente-deuxième (les invalides et les inaptes, 8d023b5, poussée le même
  matin par une autre session de la vague), chacune pesée comme
  `grille_large.py --grille population --distribution` et
  `controle_eacr.py --population` la mesurent ; les cas types de chacune
  contiennent ceux de la trentième, simulés une fois, et les couples, leurs
  proratisations et leurs conditions de départ, se calculent une fois pour
  les quatre (un pilote hors du dépôt, qui appelle leurs fonctions). Sur
  quatre cœurs, des morceaux de cent cas types : 208 minutes, dont 130 de
  simulation, 6,15 Go au plus, l'arbre de ses processus compté entier. La
  pesée de la trentième version redonne au dixième la colonne « trentième »
  de la note de la vingtième partie, 15 406 échecs compris : ni la
  trente-deuxième version éteinte, ni rien d'autre depuis bc72979 ne déplace
  la population. L'arbre figé précède la mise à l'échelle des attentes, qui
  ne touche aucune génération que la mesure lit.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 ; « dont », la part des départs de la génération pris à cette
  place dans cette condition (EIR : la place fois la part de la condition
  parmi ses départs) ; « taux plein, autrement » : par la durée, invalides,
  inaptes, décote inapplicable :

  | | EIR | trentième | trente et unième | trente-deuxième | les deux |
  |---|---|---|---|---|---|
  | femmes de 1955, à l'âge légal | 37,5 | 53,9 | 47,6 | 62,2 | 56,0 |
  | dont avec une décote | 5,8 | 12,9 | 6,6 | 12,8 | 6,6 |
  | dont au taux plein, autrement | 31,6 | 41,0 | 41,0 | 49,4 | 49,4 |
  | femmes de 1955, entre lui et l'âge d'annulation | 26,7 | 8,5 | 14,7 | 8,4 | 14,6 |
  | dont avec une décote | 5,4 | 0,0 | 6,2 | 0,0 | 6,2 |
  | dont avec une surcote | 12,1 | 8,0 | 8,0 | 8,0 | 8,0 |
  | dont au taux plein, autrement | 8,3 | 0,5 | 0,5 | 0,5 | 0,5 |
  | femmes de 1955, à l'âge d'annulation | 10,8 | 17,9 | 17,9 | 9,6 | 9,6 |
  | femmes de 1955, décote | 12,5 | 12,9 | 12,8 | 12,8 | 12,8 |
  | hommes de 1955, à l'âge légal | 24,4 | 24,1 | 17,2 | 31,7 | 24,8 |
  | dont avec une décote | 2,7 | 10,9 | 4,0 | 10,9 | 4,0 |
  | hommes de 1955, entre les deux âges | 26,4 | 24,2 | 31,0 | 24,3 | 31,1 |
  | dont avec une décote | 4,6 | 0,0 | 6,8 | 0,0 | 6,7 |
  | dont au taux plein, autrement | 8,9 | 17,2 | 17,2 | 17,3 | 17,3 |
  | hommes de 1955, à l'âge d'annulation | 5,5 | 12,5 | 12,5 | 5,1 | 5,1 |
  | ensemble de 1955, à l'âge légal | 31,2 | 39,7 | 33,1 | 47,6 | 41,1 |
  | ensemble de 1955, entre les deux âges | 26,6 | 16,0 | 22,5 | 16,0 | 22,5 |
  | femmes de 1950, à l'âge légal | 44,4 | 48,9 | 45,0 | 57,8 | 53,9 |
  | dont avec une décote | 4,8 | 8,2 | 4,2 | 8,2 | 4,2 |
  | femmes de 1950, entre les deux âges | 22,4 | 16,5 | 20,4 | 16,5 | 20,4 |
  | dont avec une décote | 3,1 | 0,0 | 3,9 | 0,0 | 3,9 |
  | hommes de 1950, à l'âge légal | 35,3 | 28,4 | 24,5 | 36,1 | 32,2 |
  | hommes de 1950, entre les deux âges | 25,4 | 30,7 | 34,6 | 30,7 | 34,6 |
  | dont au taux plein, autrement | 12,4 | 23,5 | 23,6 | 23,5 | 23,6 |

  Et les retraités de 2020 contre l'EIR, ceux de 2024 contre l'EACR (tables C
  et H ; la décote du régime général contre celle de la Cnav) :

  | | EIR, EACR | trentième | trente et unième | trente-deuxième | les deux |
  |---|---|---|---|---|---|
  | retraitées de 2020 parties avec une décote | 8,8 | 10,5 | 9,8 | 10,3 | 9,6 |
  | dont la génération simulée 1955 | | 15,0 | 13,4 | 14,1 | 12,6 |
  | retraités de 2020 partis avec une décote | 4,5 | 8,0 | 7,2 | 7,9 | 7,1 |
  | premier quintile des femmes, décote | 17,5 | 26,7 | 23,8 | 26,3 | 23,3 |
  | premier quintile des hommes, décote | 13,6 | 20,6 | 16,1 | 20,1 | 15,7 |
  | pension moyenne des femmes en 2020, € par mois | 1 177 | 1 325 | 1 332 | 1 318 | 1 325 |
  | premier décile des femmes | 283 | 393 | 405 | 393 | 404 |
  | pension moyenne des hommes en 2020 | 1 957 | 1 808 | 1 821 | 1 802 | 1 815 |
  | liquidants de 2024 du régime général, décote | 13,4 | 17,4 | 16,8 | 17,3 | 16,7 |
  | liquidants de 2024 partis à 62 ans | 26,0 | 59,3 | 51,7 | 67,9 | 60,5 |
  | à 63 ans | 18,6 | 3,5 | 6,4 | 3,5 | 6,4 |
  | à 65 ans | 7,1 | 7,3 | 11,8 | 7,2 | 11,6 |
  | à 67 ans | 10,6 | 17,6 | 17,7 | 9,1 | 9,2 |
  | âge moyen des liquidants de 2024 | 63,60 | 62,63 | 62,80 | 62,20 | 62,36 |

  L'écart de Kolmogorov des femmes passe de −14,7 à −15,2 points à 900 €,
  celui des hommes de +5,5 à +5,0 à 1 800 €. Les retraitées de 2020 nées avant
  1950 décotent 8,0 à 8,1 % sous toutes les versions.
- *Ce que cela dit.*
  - La décote se partage comme dans l'EIR. Chez les femmes de 1955, 6,6 points
    à l'âge légal et 6,2 entre les deux âges, pour 5,8 et 5,4 ; chez celles de
    1950, 4,2 et 3,9, pour 4,8 et 3,1 ; chez les hommes de 1950, 2,3 et 3,8,
    pour 2,3 et 3,3. Les hommes de 1955 décotent trop aux deux places, 4,0 et
    6,8 pour 2,7 et 4,6 : c'est leur décote entière, 10,8 % pour 8,7, que la
    note de la vingtième partie impute à la génération.
  - Les femmes de 1955 partent pour 6,2 points de plus entre les deux âges, et
    autant de moins à l'âge légal ; il en manque encore 12 entre les deux, et
    l'âge légal en a 10 de trop, 18,5 sous la trente-deuxième version. Ni
    l'un ni l'autre n'est de la décote : au taux plein, 41,0 points partent à
    l'âge légal pour 31,6, 0,5 entre les deux âges pour 8,3. Les femmes dont
    la carrière a sa durée à l'âge légal y partent, quand l'EIR en voit
    surcoter, ou n'avoir la durée qu'en travaillant au-delà : le calage de la
    durée des femmes porte leur tranche de trente à quarante ans, chez les
    nées en 1955, à 44 années, tout ce que l'âge légal laisse depuis leur
    entrée (`annees_incompletes`), et l'étalement ne laisse aucune carrière
    incomplète valider après l'âge légal. La trente-deuxième version fait
    partir à l'âge légal tous les invalides et les inaptes, dont l'EIR voit
    3,7 points de femmes entre les deux âges.
  - Les hommes passent au-delà de l'EIR entre les deux âges, 31,0 % pour 26,4
    en 1955, 34,6 pour 25,4 en 1950 : leur taux plein y était déjà deux fois
    trop fréquent, 17,2 points pour 8,9 en 1955. Un échantillon de 320 cas
    types d'hommes de 1955, tirés selon leur poids sur l'arbre du jour, qui a
    la surcote des statutaires (9e6dbbd) et le juge propre des artisans
    (ca3ff73), le trouve à l'artisan d'une carrière pleine, entré à 24 ans,
    qui n'a sa durée qu'à 65 ans et demi, et aux fonctionnaires civils de
    l'État et des collectivités, qui partent pour 40 et 65 % entre les deux
    âges au taux plein, quand l'EIR voit les retraités de l'entre-deux
    surcoter pour moitié ; non aux carrières pleines du salariat privé, qui
    partent en carrière longue ou à l'âge légal. Leur âge légal tombe à
    17,2 % pour 24,4, 24,8 sous la trente-deuxième version.
  - L'âge d'annulation ne bouge pas : la jumelle du taux plein y attend
    toujours. C'est la trente-deuxième version qui le ramène à l'EIR, 9,6 %
    des femmes de 1955 pour 10,8, 5,1 % des hommes pour 5,5.
  - Le stock de 2020 et le flux de 2024 se rapprochent. Les plus jeunes de
    2020 n'ont plus toutes leurs jumelles décotées parties quand celles du
    taux plein attendent : la génération simulée 1955 décote 13,4 % dans le
    stock, et non 15,0, les retraitées de 2020 9,8 % (8,8), les retraités
    7,2 (4,5), le premier quintile des femmes 23,8 (17,5). Les liquidants de
    2024 partent pour 51,7 % à 62 ans et non 59,3 (26,0), à 62,80 ans en
    moyenne (63,60), décotent 16,8 % au régime général (Cnav 13,4). Mais
    65 ans en prend 11,8 % pour 7,1, et 63 ans 6,4 pour 18,6 : la seconde
    attente réunit à 65 ans et cinq mois les départs de 63 à 66 ans.
  - Les pensions montent un peu, les jumelles qui attendent décotant moins :
    sept euros aux femmes de 2020, treize aux hommes.
  - La version reste : elle donne aux départs avec décote la place où l'EIR
    les voit, aux deux générations qu'il suit et aux deux sexes. Ce qu'elle
    éloigne — les hommes entre les deux âges, 65 ans en 2024, la pension des
    femmes — tient au taux plein des hommes entre les deux âges, que la
    décote laissait voir moins, et au regroupement en trois attentes.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles, qui n'ont
  pas de décote ; les carrières, toutes, et le poids de chacune, la jumelle
  qui décote gardant le sien en trois ; le pilote et le modèle ; le registre,
  dont les points sur les départs (PRISME, TRAJECTOiRE, T-DYMM) parlent du
  départ qui suit l'incitation, au propriétaire, que cette version ne fait
  pas. Aucune règle du scénario 1 ne change : pas d'entrée au journal de
  veille.

**Ce qui reste** de l'étape : les points du bloc de l'étape que les autres
sessions de la vague mènent en même temps, et, de celui-ci :

1. *Le taux plein entre les deux âges.* Chez les femmes, celles dont la
   carrière n'a sa durée qu'après l'âge légal, en validant encore — 4,0 points
   des nées en 1953 par la durée —, que le calage de la durée des femmes et
   l'étalement excluent ; chez les hommes, deux fois trop de taux plein entre
   les deux âges, 17,2 points pour 8,9 : l'artisan d'une carrière pleine,
   entré à 24 ans, au taux plein à 65 ans et demi, et les fonctionnaires
   civils qui n'ont leur durée qu'après l'âge légal, quand l'EIR voit la
   moitié de l'entre-deux surcoter.
2. *Les invalides et les inaptes entre les deux âges*, 3,7 points des femmes et
   2,9 des hommes nés en 1953, que la trente-deuxième version fait partir à
   l'âge légal.
3. *La surcote entre les deux âges*, 8,0 points des femmes de 1955 pour 12,1,
   7,1 des hommes pour 12,4, sur l'arbre de la mesure, avant la surcote des
   statutaires (9e6dbbd).
4. *Les attentes de la décote* : une par âge plutôt que trois, chacune au prix
   de 620 cas types de plus, si la page doit voir le flux de 2024 âge par âge ;
   celles des nés en 1950 aux générations qui les précèdent, 60 % des femmes
   décotées y partant à l'âge légal, 51 % chez les nés en 1953 ; la jumelle qui
   attend en validant, au travail ou au chômage, dont la décote par la durée
   baisserait aussi.
5. *Les attentes de la surcote*, de la même classe que l'écart trouvé ici :
   comptées de l'âge légal, aux durées des nés en 1953, leur troisième, celle
   des départs de l'année de l'annulation et d'après, tombe plus de deux ans
   après l'âge d'annulation chez les nés depuis 1970, qui n'ont que trois ans
   entre leurs deux âges.
