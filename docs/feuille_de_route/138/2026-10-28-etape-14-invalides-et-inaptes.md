# Étape 14, la trente-deuxième version : les invalides et les inaptes, au taux plein dès l'âge légal

**Le 28 octobre 2026 : une part des carrières incomplètes de la population
part au taux plein dès l'âge légal, reconnue inapte au travail ou ex-invalide,
au lieu d'attendre le taux plein ou de partir avec une décote — celle des
retraités que l'EIR voit partir pour invalidité ou pour inaptitude sans
carrière complète, 9,4 % des femmes et 7,6 % des hommes nés en 1953 ; la
trente-deuxième version, sur `main` (8d023b5). Les départs à l'âge
d'annulation rejoignent l'EIR : 7,5 % de ceux de la génération 1955, et non
15,4 (8,3) ; 9,6 % des femmes et non 17,9 (10,8), 5,1 % des hommes et non 12,5
(5,5) ; 15,3 % des femmes de 1950, comme l'EIR. Les hommes de 1955 partent à
l'âge légal pour 24,8 % et non 17,2 (24,4), les femmes pour 56,0 % et non 47,6
(37,5) ; le taux plein par l'âge passe sous l'EIR, 6,6 % et non 14,5 (10,0).
En 2024, 9,2 % des liquidants partent à 67 ans, et non 17,7 (EACR 10,6). La
distribution de 2020 ne bouge presque pas, sept euros de moins aux femmes.
Une simulation, deux pesées ; la mesure tient 7,6 Go au plus. La version
reste ; la page ne bouge pas.**

Demande : la vague du 28 octobre 2026, une session par tâche, lancée par le
propriétaire (« Lance une session par tâche qui n'a pas besoin de moi ») :
l'action 138, étape 14, un point du bloc de l'étape, et lui seul : les
invalides et les inaptes, au taux plein dès l'âge légal, dans la population
(« Ce qui reste », point 1, de la note de la vingtième partie,
`2026-10-25-etape-14-decote-des-carrieres-qui-le-peuvent.md`). Sept autres
sessions menaient en même temps les autres points de l'étape ; celle des
départs entre l'âge légal et l'âge d'annulation a publié la trente et unième
version (`DECOTE_ENTRE_LES_DEUX_AGES`, 57e195b) peu avant celle-ci, qui s'y
ajoute.

- *Ce qui était.* La population n'avait ni invalides ni inaptes : l'inapte et
  l'ex-invalide de la grille du coût (`INAPTE_CNAV`, `EX_INVALIDE_CNAV`,
  étape 7) cèdent leur part de la Cnav au gabarit du salariat privé
  (`reference_population`), et la mesure rangeait l'invalidité et
  l'inaptitude de l'EIR parmi les autres taux pleins. Ses carrières
  incomplètes attendaient toutes le taux plein, par la durée ou par l'âge, ou
  partaient avec une décote. Or l'assuré reconnu inapte au travail, et
  l'ex-invalide, dont la pension de vieillesse est « allouée en cas
  d'inaptitude au travail » (L. 341-15), a le taux plein quelle que soit sa
  durée (L. 351-8, 2°) dès l'âge légal, et dès 62 ans quand la réforme de
  2023 le relève (L. 351-1-5, D. 351-1-14). L'EIR compte 16,0 % des femmes et
  13,0 % des hommes nés en 1950 partis pour invalidité ou pour inaptitude,
  16,1 et 13,5 % des nés en 1953 (`departs_generations.csv`, certifié). La note
  des départs choisis le disait déjà : la population les fait « attendre l'âge
  d'annulation ou partir décotés : d'où le taux plein par l'âge trop haut ».
- *Trouvé en chemin : le gabarit perdait l'inaptitude.* Une carrière de la
  population (`CasTypeLarge`) se construit par `carriere_parcours`, sans ce
  que le cas type déclare de l'inaptitude (`CasType._invalidite`) : aucune ne
  pouvait être inapte, et l'homme d'une carrière de vingt-cinq années né en
  1955, déclaré inapte, partait à 67 ans. Elle le lui rend ; aucune carrière
  d'avant la version n'en déclarait, rien d'autre ne bouge.
- *La trente-deuxième version* (`INVALIDES_ET_INAPTES`,
  `inaptes_des_generations`, `avance_par_l_inaptitude`,
  `avances_par_l_inaptitude`, `parts_des_inaptes`, 8d023b5). Chaque carrière
  incomplète qui part au taux plein a une troisième jumelle, l'inapte,
  reconnue inapte au travail (`inaptitude`), qui part au taux plein dès l'âge
  légal. Sa génération en fait partir la part des retraités du sexe que l'EIR
  voit partir pour invalidité ou pour inaptitude sans carrière complète — la
  part de chaque condition fois celle de ses retraités sans carrière complète
  —, aux nés en 1950 et en 1953 : 7,1 % des femmes nées en 1950 parties pour
  invalidité, dont 66,3 % à carrière complète, et 8,9 % pour inaptitude, dont
  12,8 %, font 10,15 % ; les nées en 1953, 9,40 % ; les hommes, 7,70 et
  7,58 %. En droite ligne entre les deux, celle des nés en 1950 avant eux,
  celle des nés en 1953 après. Comme la décote, elle se rapporte, génération
  simulée par génération simulée, aux seules carrières dont l'inaptitude
  avance le départ (`avance_par_l_inaptitude`) : celles qui n'ont pas le taux
  plein à l'âge où l'inaptitude le donne — 31,6 % des femmes de la génération
  1955, 59,8 % de celle de 1965, que l'âge légal de 62 ans et 9 mois fait
  attendre quand l'inapte garde 62 ans ; 18,5 % des hommes. Elle se prend sur
  la jumelle du taux plein, jamais au-delà de ce que la décote lui laisse ;
  les trois jumelles gardent le poids de la carrière. La page et la pesée des
  groupes du COR voient l'inapte au poids de la génération 1953 : 15,3 % des
  carrières incomplètes des femmes, 39,9 % de celles des hommes. Trois
  conventions : une seule jumelle pour les invalides et les inaptes, que le
  droit fait partir de même, à la mortalité de sa carrière ; l'inaptitude
  avance une carrière quand elle l'avance au salaire de son cas type, avant sa
  déclinaison par le rang, comme la décote ; la décote passe avant elle. La
  cible est tenue à toutes les générations que la mesure lit ; elle manque à
  la génération 1880, où l'inaptitude n'avance aucune carrière, à celle de
  1905 chez les hommes, et aux hommes des générations 2000 et suivantes, à
  qui la décote ne laisse que 7,05 puis 5,82 %. Les exploitants et les
  libéraux d'un seul régime n'ont pas d'inapte qui avance : la fiche
  `inaptitude_au_travail` ne nomme pas leurs régimes, et le dit (son écart
  des « régimes que la fiche ne nomme pas »).
- *Les tests.* Trois de plus (`test_grille_large.py`).
  `test_les_invalides_et_les_inaptes_sans_carriere_complete_se_lisent_dans_l_eir`
  refait à la main la part de chaque sexe des nés en 1950 et en 1953, et la
  droite entre eux. `test_l_inaptitude_avance_le_depart_au_taux_plein_des_l_age_legal`
  pose à la main l'homme de vingt-cinq années né en 1955 (100 trimestres sur
  166, le taux plein à 67 ans ; inapte, à 62 ans, au taux de 50 %, rangé au
  taux plein), la femme de trente à quarante ans née en 1955 (sa durée dès
  62 ans) et en 1965 (son âge légal à 62 ans et 9 mois, D. 161-2-1-9 ; inapte,
  62 ans). `test_les_invalides_et_les_inaptes_partent_au_taux_plein_des_l_age_legal`
  veut une inapte par jumelle du taux plein, qui ne décote ni ne surcote, et,
  à chaque année de naissance de 1953 à 1957 et de 1963 à 1967, des inaptes
  qui pèsent la part de l'EIR parmi tous les retraités du sexe, chaque
  carrière son poids. Vus rouges faute de la version, et, le second, de
  l'inaptitude que le gabarit perdait (67 ans et non 62). Le fichier, avec les
  trois tests de la trente et unième version, tient 115 s sur quatre cœurs.
- *La mesure.* Une simulation, deux pesées : la version n'ajoute que les
  inaptes, chaque autre carrière restant ce qu'elle était, et la population,
  simulée une fois sur l'arbre figé de 8d023b5 (`CALCULS_SANS_MEMOIRE=1`,
  détaché), se pèse sans eux — la trente et unième version — puis avec eux,
  comme `grille_large.py --grille population --distribution` et
  `controle_eacr.py --population` la mesurent, les proratisations et les
  conditions de départ de chaque couple calculées une fois pour les deux (un
  pilote hors du dépôt, qui appelle leurs fonctions). 16 114 cas types sans
  les inaptes, 16 734 avec ; sur quatre cœurs, des morceaux de cent cas
  types : 170 minutes, dont 117 de simulation, 7,6 Go au plus, l'arbre de ses
  processus compté entier. Les versions que la vague a publiées depuis
  8d023b5 n'y sont pas — la décote des résidents, l'attente de la décote
  selon l'écart des deux âges, les natures des hommes selon le rang, la
  surcote des statutaires, les artisans — : la mesure dit ce que les inaptes
  déplacent, sur la population d'avant elles.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 :

  | | EIR | sans les inaptes | avec |
  |---|---|---|---|
  | ensemble 1955, à l'âge légal | 31,2 | 33,1 | 41,1 |
  | ensemble 1955, à l'âge d'annulation | 8,3 | 15,4 | 7,5 |
  | ensemble 1955, taux plein par l'âge | 10,0 | 14,5 | 6,6 |
  | ensemble 1955, autre taux plein | 44,4 | 44,7 | 52,9 |
  | ensemble 1955, décote | 10,7 | 11,8 | 11,8 |
  | femmes de 1955, à l'âge légal | 37,5 | 47,6 | 56,0 |
  | femmes de 1955, entre lui et l'âge d'annulation | 26,7 | 14,7 | 14,6 |
  | femmes de 1955, à l'âge d'annulation | 10,8 | 17,9 | 9,6 |
  | femmes de 1955, taux plein par l'âge | 12,3 | 17,2 | 8,9 |
  | hommes de 1955, à l'âge légal | 24,4 | 17,2 | 24,8 |
  | hommes de 1955, à l'âge d'annulation | 5,5 | 12,5 | 5,1 |
  | hommes de 1955, taux plein par l'âge | 7,5 | 11,6 | 4,1 |
  | femmes de 1950, à l'âge légal | 44,4 | 45,0 | 53,9 |
  | femmes de 1950, à l'âge d'annulation | 15,3 | 24,3 | 15,3 |
  | hommes de 1950, à l'âge légal | 35,3 | 24,5 | 32,2 |
  | hommes de 1950, à l'âge d'annulation | 7,3 | 16,5 | 9,0 |

  Et les retraités de 2020 contre l'EIR, ceux de 2024 contre l'EACR (tables C
  et H ; la décote du régime général contre celle de la Cnav) :

  | | EIR, EACR | sans les inaptes | avec |
  |---|---|---|---|
  | pension moyenne des femmes en 2020, € par mois | 1 177 | 1 332 | 1 325 |
  | premier décile des femmes | 283 | 405 | 404 |
  | pension moyenne des hommes en 2020 | 1 957 | 1 821 | 1 815 |
  | femmes au minimum de pension | 37,7 | 29,7 | 29,9 |
  | retraitées de 2020 parties avec une décote | 8,8 | 9,8 | 9,6 |
  | retraités de 2020 partis avec une décote | 4,5 | 7,2 | 7,1 |
  | liquidants de 2024 du régime général, décote | 13,4 | 16,8 | 16,7 |
  | retraités de 2024 du régime général, décote | 9,4 | 11,7 | 11,4 |
  | liquidants de 2024 partis à 62 ans | 26,0 | 51,7 | 60,5 |
  | liquidants de 2024 partis à 67 ans | 10,6 | 17,7 | 9,2 |
  | âge moyen des liquidants de 2024 | 63,60 | 62,80 | 62,36 |

  L'écart de Kolmogorov des femmes passe de −15,2 à −14,6 points à 900 €,
  celui des hommes de +5,0 à +5,1 à 1 800 €. La durée validée des femmes de
  1955 et de 1960 passe de 41,6 à 41,0 et de 43,2 à 42,3 années (EIR 40,6 et
  41,2), celle des hommes de 40,2 à 39,7 et de 39,0 à 38,5 (40,9 et 40,5). Les
  inaptes pèsent 8,9 % des retraitées de 2020 et 7,5 % des retraités, 9,3 %
  des liquidants de 2024. Des 17 980 couples des 620 inaptes, 12 802 pèsent,
  et l'inaptitude en avance 12 796 ; les six autres, des déclinaisons du haut
  de la femme de trente à quarante ans née en 1965, en leur premier
  cinquième, partent en carrière longue dès 62 ans.
- *Ce que cela dit.*
  - L'âge d'annulation se vide de ce qui n'y était pas. La population y
    faisait attendre les invalides et les inaptes de ses carrières
    incomplètes ; ils partent désormais à l'âge légal, et l'âge d'annulation
    rejoint l'EIR aux deux sexes et aux deux générations : 9,6 et 5,1 % des
    femmes et des hommes de 1955 (10,8 et 5,5), 15,3 et 9,0 % de ceux de 1950
    (15,3 et 7,3). Le flux de 2024 de même : 9,2 % de ses liquidants partent à
    67 ans (10,6).
  - L'âge légal se partage selon le sexe. Les hommes le rejoignent, 24,8 %
    des départs de 1955 (24,4), 32,2 % de ceux de 1950 (35,3) ; les femmes
    s'en éloignent, 56,0 % (37,5) et 53,9 % (44,4). Ce qui manque aux femmes
    est entre l'âge légal et l'âge d'annulation, 14,6 % de leurs départs de
    1955 pour 26,7, que la trente et unième version commence à combler ;
    l'EIR y range aussi un gros tiers de ses départs pour inaptitude, quand
    l'inapte de la population part toujours à l'âge légal.
  - Le taux plein par l'âge passe sous l'EIR, 6,6 % des départs de 1955 pour
    10,0, et l'autre taux plein au-dessus, 52,9 % pour 44,4. Les carrières qui
    n'ont pas le taux plein à l'âge légal sont trop peu : l'EIR compte 42,7 %
    des femmes et 30,0 % des hommes nés en 1953 sans carrière complète, la
    population 32,4 et 19,0 % de carrières qui peuvent décoter à la génération
    1955. La décote y prenait déjà sa part de l'EIR ; les inaptes prennent la
    leur, et ce qui reste n'attend plus assez l'âge d'annulation.
  - La distribution de 2020 en dit peu : sept euros de moins aux femmes, six
    aux hommes, le premier décile des femmes à 404 € (283).
  - La version reste : elle donne à la population les invalides et les inaptes
    que l'EIR compte, à l'âge où le droit les fait partir, et l'âge
    d'annulation y gagne ce que la note des départs choisis lui reprochait.
    Ce qu'elle éloigne — l'âge légal des femmes, le taux plein par l'âge, le
    flux à 62 ans — tient à ce qu'elle ne fait pas : les départs entre les
    deux âges, et des carrières incomplètes trop peu nombreuses.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles, qui n'ont
  pas d'inaptes, sinon la grille du coût, qui a les siens ; les carrières
  d'avant la version, leurs cas types et leurs poids de base ; le registre,
  dont aucun point « 138.14 » ne nomme l'invalidité ni l'inaptitude. Aucune
  règle du scénario 1 ne change : pas d'entrée au journal de veille.

**Ce qui reste**, de ce point :

1. *La mortalité des invalides et des inaptes*, que la grille du coût leur
   donne (Cadr'@ge n° 40, `esperances_vie_pensions_cnav.csv`) et que l'inapte
   de la population n'a pas : le stock en garderait moins aux grands âges.
2. *Les inaptes entre l'âge légal et l'âge d'annulation* : l'EIR range un
   gros tiers des départs pour inaptitude des nés en 1953 entre les deux âges
   (34,5 % chez les femmes, 37,2 chez les hommes), un sur dix de ceux pour
   invalidité, quand l'inapte part toujours à l'âge légal.
3. *Les générations hors de l'enquête* : la part des nés en 1953 à toutes les
   générations suivantes, quand la Cnav en compte plus depuis la réforme de
   2023 (9,1 % de départs pour inaptitude et 9,4 % d'ex-invalides en 2024,
   8,1 et 8,7 % en 2020 ; `nouveaux_retraites_cnav.csv`, d'une fiabilité
   moyenne) ; celle des nés en 1950 aux précédentes, quand la Cnav comptait
   de 9,8 à 12,9 % de départs pour inaptitude de 2003 à 2010.
4. *Les inaptes des exploitants et des libéraux*, que le modèle n'avance pas
   tant que la fiche `inaptitude_au_travail` ne lit pas leurs textes (L. 732-23
   du code rural pour les premiers).

Le reste de l'étape est au bloc « Reprise » de la première note
(`2026-10-07-etape-14-la-distribution-de-2020.md`) : chaque point s'y mène en
parallèle, une session chacun.
