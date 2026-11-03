# Étape 14, la trente-sixième version : les agents décotés avant 60 ans

**Le 3 novembre 2026 : les agents des IEG et de la conduite ne décotent plus
tous à l'ouverture de leur statut, mais pour la part que l'EIR trouve aux
retraités des régimes spéciaux de 2020 à qui la décote s'appliquait, 13,0 %
des hommes et 21,0 % des femmes ; le reste part à son taux plein. Sur `main`,
les données (467801f), puis la version (c8b7ddf). Les agents décotés pèsent
0,23 % des hommes du stock de 2020, et non 1,73 (EIR 0,25), 0,09 % des femmes,
comme l'EIR, et non 0,43 ; les hommes de 50 à 59 ans décotent pour 8,4 % (5,7)
et non 45,7, ceux de 60 à 64 ans pour 6,7 %, comme l'EIR, et non 9,0 ; tous
les retraités, pour 4,6 % (4,5) et non 6,0. Les jumelles des carrières
incomplètes gardent leur part : la décote des générations nées depuis 1960
tombe sous celle de la Cnav, une question au propriétaire. Ce que la version
découvre : la décote des fonctionnaires, que la population n'a pas, et le taux
plein tardif que le pilote fixe aux agents. Une simulation, deux pesées. La
version reste ; la page ne bouge pas.**

Demande : la troisième vague, lancée dans la nuit du 2 au 3 novembre 2026 par
la session d'orchestration, file I : l'action 138, étape 14, le point suivant
de la file, « les agents décotés avant 60 ans », que la note de la décote des
résidents détaille (« Ce qui reste », point 1,
`2026-10-28-etape-14-decote-des-residents.md`).

- *Ce qui était.* Les agents des IEG et de la conduite partent à l'ouverture
  de leur statut (`regle_liquidation="ouverture"`), et y décotent dès que la
  décote des régimes spéciaux mord : l'agent des IEG dès la génération 1960,
  à 55 ans au taux de 70,31 %, à 56 ans et 4 mois au taux de 60 % né en 1965 ;
  l'agent de conduite dès la génération 1965, à 50 ans au taux de 70,31 %, à
  51 ans et 4 mois au taux de 60 % né en 1970. Tous décotaient : les hommes de
  50 à 59 ans pesaient 3,0 % du stock de 2020, et décotaient pour 45,7 %, quand
  l'EIR compte 1,8 % de ses résidents à cet âge, et 5,7 % de décotés parmi
  eux ; les agents décotés pesaient 1,73 % des hommes du stock, 1,5 point de
  leur décote, 6,0 % pour 4,5. Les femmes de 50 à 59 ans, 0,7 % du stock,
  décotaient pour 51,9 % (EIR 1,0 et 18,4).
- *Ce que l'EIR publie.* La feuille « CondLiquidation » du classeur des
  résidents de 2020, que le dépôt lisait pour l'âge de chaque condition de
  liquidation, dit aussi, condition par condition, le régime de base principal
  des retraités : la part des monopensionnés et des polypensionnés de deux
  régimes de chaque régime. Les régimes spéciaux comptent 4,6 % des 321 000
  hommes partis avec une décote parmi leurs monopensionnés, 1,1 % parmi leurs
  polypensionnés, 18 300 en tout ; 17,0 et 30,0 % des 468 000 dont la décote
  est inapplicable, 220 000 ; 2,8 et 3,0 % de tous, 417 400. Leurs retraités
  de toutes les conditions connues, sans ceux dont la décote est inapplicable
  — partis avant juillet 2010, qu'elle ne touchait pas —, sont 140 300 :
  51 400 au taux plein par l'âge, 49 600 par la durée, 18 300 avec une décote,
  7 900 en carrière longue, 6 700 avec une surcote, 5 200 pour un autre motif,
  1 300 pour invalidité ; 57 000 n'ont pas de condition connue. Ceux à qui la
  décote s'appliquait sont partis avec une décote pour 13,0 % ; les femmes,
  7 400 sur 35 200, pour 21,0 %. Le même classeur range ses retraités par leur
  âge de liquidation (feuille « ÂgeLiq_Détails », lue, non certifiée) : les
  1,5 million d'hommes partis avant 60 ans, dont 23,9 % des régimes spéciaux,
  ne décotent que pour 3,6 % ; les 0,9 million de femmes, pour 7,2.
- *Les données*, certifiées (467801f). Le récupérateur
  (`drees_caracteristiques_retraites.py`) lit, dans la même feuille, les
  seize parts du régime principal de chaque condition — monopensionnés et
  polypensionnés du régime général, de l'État civil et militaire, de la MSA
  des salariés, de la CNRACL, des régimes spéciaux, de la MSA des
  non-salariés, des libéraux —, une case vide se lisant zéro, et vérifie que
  les retraités des deux sexes que chaque régime compte redonnent ceux de
  l'ensemble, à l'arrondi de ses parts près, et que ses parts ne passent pas
  cent. `conditions_selon_l_age_residents.csv` gagne 480 valeurs, 810 en
  tout ; les 330 qu'il certifiait se redonnent à l'identique. Le serveur de
  la DREES coupait, ce matin-là, la connexion du récupérateur après une
  dizaine de secondes, à chaque essai : les deux classeurs se sont pris à leur
  adresse directe, et le `main()` du récupérateur a tourné sur eux, leur
  téléchargement seul remplacé. Le journal de certification ne change qu'à
  cette série.
- *La version* (`DECOTE_DES_AGENTS`, `decote_des_agents`,
  `agents_a_leur_taux_plein`, c8b7ddf). Chaque agent qui décote à
  l'ouverture de son statut à une génération de la grille au moins
  (`ouvertures_decotees`) se décline en deux, après les jumelles des
  carrières incomplètes et avant la déclinaison par le rang : la part de son
  sexe y part, avec sa décote, sous son code ; le reste part à son taux
  plein, que le pilote fixe, sous son code suivi de « ~plein ». L'agent et sa
  sœur se partagent son poids à cette part ; aux générations où l'agent ne
  décote pas, il le porte seul, et elle ne pèse rien. La population passe de
  19 352 cas types à 19 408, 56 sœurs : les huit agents, mono et
  polypensionnés des deux sexes, chacun en sept rangs.
- *Ce qu'elle ne fait pas : les jumelles.* La trentième version prend la part
  de chaque génération sans ce que les agents y décotent
  (`parts_des_jumelles`). Les agents décotant moins, leur décote passerait aux
  jumelles des carrières incomplètes, qui la portent seules. Elles ne le
  peuvent pas : la part que la population prête à ses générations depuis 1960,
  celle des liquidants de la Cnav de 2024 (vingt-neuvième version), 13,0 % des
  hommes, ferait décoter 64,6 % des carrières incomplètes des hommes nés de
  1963 à 1987, et partir inaptes presque toutes les autres, la décote passant
  avant l'inaptitude : leurs inaptes n'y pèseraient plus que 6,5 % des hommes,
  et non les 7,6 % de l'EIR ; presque aucune ne partirait plus au taux plein.
  Les agents absorbaient 5,7 points de ces 13,0 en décotant tous. Les jumelles
  gardent donc la part de la trentième version : la version est dans un seul
  geste, après elles, et la décote des générations nées depuis 1960 tombe sous
  la part de la Cnav de ce que les agents ne décotent plus, 8,1 % des hommes
  au lieu de 13,0 dès la génération 1965, 12,7 % des femmes au lieu de 13,7.
  La part de la Cnav, qui ne compte que ses liquidants, ne tenait sur la
  population que par eux : une question au propriétaire (« Ce qui reste »,
  point 1).
- *Les tests.* Des données (`test_conditions_selon_l_age.py`, trois de plus) :
  le lecteur du régime principal, sur la feuille telle qu'elle se lit — 4,6 et
  1,1 % des décotés, 17,0 et 30,0 % des décotes inapplicables, une case vide
  lue zéro ; son refus d'un régime que les deux sexes ne redonnent pas, ou
  absent ; le fichier certifié, qui redonne ce que le classeur imprime, les
  18,3 milliers de décotés des régimes spéciaux, et chaque régime de chaque
  condition des deux sexes. De la population (`test_grille_large.py`, deux de
  plus) : `test_la_part_des_agents_qui_decotent_se_lit_dans_l_eir` refait à la
  main, des effectifs et des parts que le classeur imprime, les 13,0 et 21,0 % ;
  `test_une_part_des_agents_part_a_son_taux_plein` tient la déclinaison — la
  sœur de chaque agent, au taux plein, à sa part du poids, l'agent et elle
  redonnant son poids à chaque année de naissance de 1878 à 2022 —, et pose à
  la main l'agent de conduite né en janvier 1965 : son droit s'ouvre à 50 ans,
  en 2015, où la décote des régimes spéciaux vaut cinq dixièmes de 1,25 % par
  trimestre manquant et s'annule à 55 ans moins dix trimestres ; il lui en
  manque dix, et son taux est de 75 % fois (1 − 10 × 0,625 %), 70,31 %
  (`decote_regimes_speciaux.csv`) ; sa sœur part plus tard, au taux de 75 %,
  sans décote. Vus rouges faute du lecteur et des données, puis de la version.
  Un test ancien compte désormais les sœurs : celui de la trentième version,
  dont la part de chaque génération se refait avec les agents tenus pour tous
  décotés, comme les jumelles la prennent. Les 96 tests du fichier passent ;
  la suite rapide, 3 867 tests.
- *La mesure.* Une simulation, deux pesées, sur l'arbre de la version
  (c8b7ddf) : la population de la trente-sixième version, 19 408 cas types,
  qui contient celle de la trente-cinquième (19 352), se simule une fois au
  portage, en 25 tranches de 800 cas types gardées sur le disque, sans la
  mémoire des calculs : 74 minutes sur quatre cœurs, 542 749 couples, 20 083
  échecs (17 038 liquidations antérieures à la répartition, 3 045 carrières
  sans régime actif). Les proratisations et les décotes de chaque couple se
  calculent une fois pour les deux pesées, en 11 minutes ; puis la population
  se pèse deux fois, `DECOTE_DES_AGENTS` éteinte puis allumée, 11 et 12
  minutes (un pilote hors du dépôt, qui appelle les fonctions du script et de
  `controle_eacr.py`, et compte de plus la décote du stock de 2020 par tranche
  d'âge et celle des agents) ; 8 Go au plus, vus de `free`.
- *Ce qu'elle trouve*, d'abord le stock de 2020 par tranche d'âge, contre les
  résidents de l'EIR ; « des régimes spéciaux », la part des agents et de
  leurs sœurs parmi les retraités de la tranche :

  | stock de 2020 | EIR | trente-cinquième | trente-sixième |
  |---|---|---|---|
  | hommes de 50 à 59 ans, part du stock | 1,8 | 3,0 | 2,2 |
  | dont partis avec une décote | 5,7 | 45,7 | 8,4 |
  | dont des régimes spéciaux | | 53,9 | 35,1 |
  | hommes de 60 à 64 ans, décote | 6,7 | 9,0 | 6,7 |
  | hommes de 65 à 69 ans, décote | 7,5 | 8,3 | 8,3 |
  | femmes de 50 à 59 ans, part du stock | 1,0 | 0,7 | 0,5 |
  | dont parties avec une décote | 18,4 | 51,9 | 15,2 |
  | femmes de 60 à 64 ans, décote | 11,5 | 10,5 | 10,0 |
  | agents décotés, parmi tous les hommes | 0,25 | 1,73 | 0,23 |
  | parmi toutes les femmes | 0,09 | 0,43 | 0,09 |
  | décote des retraités des régimes spéciaux, hommes | 4,4 | 25,9 | 3,9 |
  | femmes | 6,7 | 25,9 | 6,1 |

  Le stock par tranche se pèse comme celui de l'EACR
  (`controle_eacr.cohortes`), sans la survie propre de chaque cas type que la
  distribution lui donne : les hommes y décotent pour 6,2 % puis 4,7 %, et non
  6,0 et 4,6 ; les femmes, 8,8 puis 8,5 %. Les autres tranches ne bougent pas,
  à un dixième près. Puis le reste, contre l'EIR et contre l'EACR, les
  quintiles étant ceux de la pension en équivalent carrière complète :

  | | EIR, EACR | trente-cinquième | trente-sixième |
  |---|---|---|---|
  | retraités de 2020 partis avec une décote | 4,5 | 6,0 | 4,6 |
  | retraitées de 2020 parties avec une décote | 8,8 | 8,6 | 8,3 |
  | premier quintile des hommes, décote | 13,6 | 12,6 | 12,7 |
  | quatrième et cinquième quintiles des hommes | 3,1 ; 4,3 | 5,8 ; 5,6 | 3,7 ; 2,9 |
  | premier quintile des femmes, décote | 17,5 | 20,8 | 20,9 |
  | quatrième et cinquième quintiles des femmes | 4,8 ; 5,4 | 2,7 ; 2,5 | 2,2 ; 1,2 |
  | part des femmes parmi les retraités de 2020 | 54,0 | 50,5 | 50,6 |
  | pension moyenne des femmes en 2020, € par mois | 1 177 | 1 349 | 1 349 |
  | pension moyenne des hommes en 2020 | 1 957 | 1 831 | 1 833 |
  | retraités de 2024 de moins de 60 ans, tous régimes | 1,2 | 1,6 | 1,2 |
  | liquidants de 2024 partis avant 60 ans | 4,0 | 5,3 | 2,7 |
  | âge moyen des liquidants de 2024 | 63,60 | 62,47 | 62,68 |
  | retraités du régime général en 2024, décote | 9,4 | 10,3 | 10,3 |
  | liquidants de 2024 du régime général, décote | 13,4 | 17,1 | 17,1 |

  L'écart de Kolmogorov des femmes reste à −15,4 points à 1 200 €, celui des
  hommes passe de +4,4 à +4,3 à 1 800 € ; les artisans et commerçants ne
  bougent pas.
- *Ce que cela dit.*
  - Les agents décotent comme l'EIR le dit de leurs régimes : 0,23 % de tous
    les hommes du stock (0,25), 0,09 % des femmes (0,09), 3,9 et 6,1 % des
    retraités de ces régimes (4,4 et 6,7). Avec eux tombe la décote des
    hommes de 50 à 59 ans, 8,4 % et non 45,7 (5,7), et celle des hommes de 60
    à 64 ans, nés de 1956 à 1960, que les agents des IEG de la génération 1960
    portaient : 6,7 %, celle de l'EIR. Tous les retraités de 2020 décotent pour
    4,6 % (4,5), et non 6,0.
  - Les hommes de 50 à 59 ans pèsent 2,2 % du stock, et non 3,0 (1,8) : les
    sœurs partent à l'âge que le pilote fixe à leur taux plein, cinq ans après
    l'ouverture de leur statut, que les nés de 1961 à 1970 n'ont pas tous
    atteint fin 2020 ; les agents n'y sont plus que 35,1 % de la tranche. Les
    femmes de cet âge s'éloignent, 0,5 % du stock et non 0,7 (1,0) : l'EIR
    range parmi ses femmes parties avant 60 ans 34,9 % de fonctionnaires de
    l'État, 36,6 % de la CNRACL et 9,2 % des régimes spéciaux (feuille
    « ÂgeLiq_Détails »), des mères de trois enfants et des catégories
    actives, que la population ne fait pas partir si tôt : ses fonctionnaires
    actifs partent à leur taux plein, vers 61 ou 62 ans.
  - Ce qui s'éloigne, la décote des femmes et des quintiles du haut — les
    retraitées décotent pour 8,3 % et non 8,6 (8,8), le cinquième quintile
    des femmes pour 1,2 % (5,4), celui des hommes pour 2,9 (4,3) —, tient aux
    fonctionnaires, dont les agents décotés tenaient la place : l'EIR en
    compte 24,3 % parmi les hommes partis avec une décote et 16,6 % parmi les
    femmes (l'État civil et la CNRACL, mono et polypensionnés), qui décotent,
    parmi ceux à qui la décote s'appliquait, pour 12,3 et 7,8 % des hommes,
    10,8 et 14,4 % des femmes ; la population n'en fait décoter aucun (point
    4). Et les liquidants de 2024 partis avant 60 ans, 2,7 % et non 5,3
    (4,0), tiennent au taux plein que le pilote fixe aux sœurs, après l'âge
    où la montée en charge annule déjà leur décote (point 2).
  - Le régime général ne bouge pas, ses jumelles gardant leur part : 17,1 %
    de décotés parmi ses liquidants de 2024 (13,4), 10,3 % de ses retraités
    (9,4).
  - La distribution de 2020 en dit peu : deux euros de plus aux hommes ;
    l'âge moyen des liquidants de 2024 monte de 62,47 ans à 62,68 (63,60).
  - La version reste : les agents décotent comme l'EIR le mesure de leurs
    régimes, et ce qu'elle éloigne tient à ce qu'elle découvre.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les jumelles des carrières
  incomplètes, leurs parts, leurs inaptes, leurs attentes ; les carrières
  pleines, les fonctionnaires et les non-salariés ; le registre. Aucune règle
  du scénario 1 ne change : pas d'entrée au journal de veille. Aucun fichier
  d'une autre file n'est touché.

**Ce qui reste** de l'étape : les autres points du bloc de l'étape, et, de
celui-ci :

1. *La décote des générations nées depuis 1960*, au propriétaire : la part
   des liquidants de la Cnav de 2024, 13,0 % des hommes et 13,7 % des femmes,
   que la population prête à tous les retraités de ces générations
   (`decotes_des_generations`, vingt-neuvième version), ne tenait que par les
   agents, qui en prenaient 5,7 points chez les hommes ; les jumelles des
   carrières incomplètes ne peuvent la porter seules, les carrières de
   quarante années et plus ne décotant jamais dans la population. La
   rapporter aux seuls retraités du régime général, ou laisser décoter les
   carrières pleines à qui des trimestres manquent, est un choix de modèle.
2. *Le taux plein des agents dans le pilote*, hors de la file :
   `droit.ouvrir.age_taux_plein`, que le pilote lit, rend aux agents des
   régimes spéciaux l'âge d'annulation de leur décote au terme de la montée
   en charge — l'ouverture plus cinq ans —, quand le barème de leur décote en
   retranche la diminution de l'année : l'agent de conduite né en 1965 a son
   taux de 75 % dès 52 ans et demi, et le pilote le fait partir au taux plein
   à 55 ans ; l'agent des IEG né en 1960, à 57 ans et demi, et non 60. Les
   sœurs de cette version partent donc plus tard que leur taux plein. C'est
   le moteur d'une carrière, dans ses deux langages (`src/`, `moteur/js/`),
   hors de cette file : au propriétaire, qui la confiera.
3. *La part des agents selon la génération* : celle du stock de 2020, la même
   à toutes les générations, quand la décote des droits ouverts de 2010 à 2019
   montait d'un dixième par an ; la table H de l'EACR ne la donne pas aux
   régimes spéciaux, et les rapports de leurs caisses (CNIEG, CPRP SNCF) la
   diraient de leurs départs, s'ils la publient.
4. *La décote des fonctionnaires*, que la population n'a pas : les
   fonctionnaires de l'État et de la CNRACL partent à leur taux plein, ou
   après lui avec une surcote, quand l'EIR en voit décoter, parmi ceux de 2020
   à qui la décote s'appliquait, 12,3 et 7,8 % des hommes, 10,8 et 14,4 % des
   femmes, les données certifiées le disant désormais
   (`conditions_selon_l_age_residents.csv`) ; la même lecture que celle des
   agents, et la même déclinaison. Elle rejoint la question des hommes entre
   les deux âges, au propriétaire (note du taux plein entre les deux âges,
   « Ce qui reste », point 1).
5. *L'âge de liquidation selon le régime* : la feuille « ÂgeLiq_Détails »
   dit le régime principal et la condition des retraités de 2020 selon l'âge
   de leur départ, avant 60 ans, à 60 ans, de 61 à 67 ans et plus ; certifiée,
   elle jugerait les départs d'avant l'âge légal de la population, régime par
   régime.
