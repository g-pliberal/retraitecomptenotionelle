# Étape 14, la trente-huitième version : les invalides et les inaptes ne partent pas tous à l'âge légal

**Le 5 novembre 2026 : les invalides et les inaptes de la population
partaient tous à l'âge où l'inaptitude leur ouvre le taux plein, l'âge légal,
ou 62 ans quand la réforme de 2023 le relève — 100 % de leurs départs, à
chaque génération et à chaque sexe —, quand l'EIR range entre l'âge légal et
l'âge d'annulation de la décote 34,5 % des femmes et 37,2 % des hommes nés en
1953 partis pour inaptitude, 12,4 et 8,8 % de ceux partis pour invalidité. La
trente-huitième version (`INAPTES_ENTRE_LES_DEUX_AGES`) les fait attendre
comme les nés en 1953 : 70,9 % des femmes et 71,3 % des hommes partent à cet
âge (EIR 70,8 et 71,3), les autres un an et un mois puis trois ans et
quatre mois plus tard ; leur âge moyen de départ passe de 61,17 à 61,83 ans
chez les femmes nées en 1953. Leur part ne bouge pas, 9,40 et 7,58 % des
départs. Aucune règle ne change ; la page ne bouge pas.**

Demande : la vague 9, lancée par la session d'orchestration le 5 novembre
2026 : un point de l'étape 14, et lui seul, la mesure d'abord — « les
inaptes partent-ils tous, dans la population, à l'âge légal ? », le point 2
de « Ce qui reste » de la trente-deuxième version
(`2026-10-28-etape-14-invalides-et-inaptes.md`).

- *La source*, ouverte le 5 novembre 2026, deux pièces jointes du jeu de la
  DREES `3013_donnees-statistiques-sur-les-caracteristiques-des-retraites`
  (https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog/datasets/3013_donnees-statistiques-sur-les-caracteristiques-des-retraites/attachments/…),
  prises par la lecture web, le récupérateur du dépôt coupé :
  « Caractéristiques des retraités nés en 1953 (EIR 2020) »
  (`caracteristiques_des_retraites_nes_en_1953_eir_2020_xlsx`, 195 574
  octets, SHA-256
  `d5e8b8776768e31a3a8a0490bf749fc6615d12a8d25716e57a658dd16f94c5e0`, celle
  de la note du matin) et « nés en 1950 (EIR 2016) »
  (`caracteristiques_des_retraites_nes_en_1950_eir_2016_xlsx`, 194 522
  octets, SHA-256
  `59f76598591d20cb4704659a65ba30ce687ca8cb0a733198a3182c6bbaef61a8`). Lues
  cellule par cellule ; chacune est celle de `departs_generations.csv`.
  Classeur de 1953 :
  - feuille « ÂgeLiq », colonnes D (avant l'âge légal), E (à l'âge légal),
    F (entre lui et l'âge d'annulation de la décote), G (à l'âge
    d'annulation), H (après) : ligne 6, « Part parmi l'ensemble des
    retraités (en %) », femmes, 21,7, 37,5, 26,7, 10,8, 3,3 ; ligne 7,
    hommes, 40,8, 24,4, 26,4, 5,5, 2,8 ; ligne 285, « Part des retraités
    ayant liquidé pour invalidité (en %) », femmes, 1,6, 17,9, 3,8, 0,6,
    0,4 ; ligne 286, hommes, 1,4, 25,6, 2,5, 0,6, 0,1 ; ligne 291, « … pour
    inaptitude », femmes, 0,0, 13,7, 10,2, 0,3, 0,1 ; ligne 292, hommes, 0,0,
    15,2, 8,4, 0,5, 0,4 ;
  - feuille « ÂgeLiq_Détails », colonnes F à K, 61 à 66 ans : ligne 6,
    femmes, 42,1, 8,9, 5,0, 5,7, 2,9, 14,9 ; ligne 7, hommes, 29,7, 8,2,
    5,2, 6,1, 3,1, 9,1 ; ligne 285, femmes, invalidité, 16,1, 8,6, 1,7, 1,3,
    1,1, 0,6 ; ligne 286, hommes, 21,2, 6,3, 0,8, 0,7, 0,6, 0,5 ; ligne 291,
    femmes, inaptitude, 13,0, 9,7, 10,6, 10,7, 9,2, 0,9 ; ligne 292, hommes,
    13,3, 8,7, 7,8, 8,6, 6,5, 1,8 ;
  - feuille « CondLiquidation », colonnes H (taux plein invalidité) et I
    (taux plein inaptitude) : ligne 6, femmes, 8,2 et 7,9 % de la
    génération ; ligne 7, hommes, 7,5 et 6,0 ; ligne 18, « Part d'assurés à
    carrière complète (en %) », femmes, 67,6 et 14,7 ; ligne 19, hommes, 65,3
    et 17,1.

  Classeur de 1950, les mêmes lignes de « ÂgeLiq » aux lignes 6, 7, 282,
  283, 288 et 289 : femmes parties pour inaptitude, 14,4 % des départs de l'âge légal
  (E288), 11,0 % de ceux d'entre les deux âges (F288) ; hommes, 12,4 et 7,8
  (E289, F289) ; pour invalidité, 14,6 et 1,8 (E282, F282), 16,6 et 1,1
  (E283, F283) ; « CondLiquidation », ligne 18, 66,3 et 12,8 % à carrière
  complète chez les femmes, ligne 19, 62,4 et 18,5 chez les hommes.

  Les départs pour inaptitude des femmes nées en 1953, place par place,
  pèsent la part de la place fois celle de l'inaptitude parmi ses départs :
  37,5 × 13,7 = 513,75 à l'âge légal, 26,7 × 10,2 = 272,34 entre les deux
  âges, 10,8 × 0,3 = 3,24 et 3,3 × 0,1 = 0,33 ensuite, 789,66 en tout :
  34,5 % entre les deux âges. Les hommes : 370,88, 221,76, 2,75 et 1,12, soit
  37,2 %. L'invalidité, de même : 12,4 % des femmes (101,46 sur 815,23), 8,8 %
  des hommes (66,00 sur 751,34), avec 4,3 et 7,6 % avant l'âge légal.
- *La mesure, avant* (`docs/mesures/138/2026-11-05-etape-14-inaptes.txt`,
  son script et ses deux sorties), sur `main` à b80f490 : les jumelles
  inaptes de la population, cinq générations, chacune aux poids de
  retraités de l'année de ses 66 ou 67 ans, multipliés par la part que la
  génération donne à chaque variante, simulées au portage. Elles pèsent
  10,17 % des départs des femmes nées en 1950 et 7,65 % des hommes (EIR,
  sans carrière complète, 10,15 et 7,70), 9,40 et 7,58 % de ceux de 1953
  (9,40 et 7,58), 9,39 et 7,60 % de ceux de 1955, 9,38 et 7,66 de 1960, 9,36
  et 7,72 de 1965. Toutes partent à un seul âge : 60 ans en 1950, 61 ans et
  2 mois en 1953, 62 ans en 1955, 1960 et 1965 — l'âge légal, et, en 1965,
  62 ans, avant l'âge légal de 62 ans et 9 mois (L. 351-1-5, D. 351-1-14).
  Aucune entre les deux âges, quand l'EIR y range trois départs sur dix des
  invalides et des inaptes sans carrière complète.
- *Ce que la source permet* : la part de chaque place et de chaque âge dans
  les départs pour invalidité et pour inaptitude, aux nés en 1950 et en
  1953. Elle ne croise ni l'âge ni la place avec la carrière complète, quand
  l'inapte de la population n'en a pas : d'où la première convention.
- *La trente-huitième version* (`INAPTES_ENTRE_LES_DEUX_AGES`,
  `attentes_des_inaptes`). La jumelle inapte de chaque carrière incomplète
  se décline en trois, comme la jumelle qui décote (trente et unième
  version, `attentes_des_decotes`, dont la lecture devient commune,
  `_attentes_apres_l_age_legal`, au bit près pour la décote) : la part des
  invalides et des inaptes des nés en 1953 que l'EIR range à l'âge légal y
  part, sous son code ; le reste attend, en deux attentes — les âges de 61 et
  62 ans, puis de 63 ans à l'âge d'annulation —, chaque âge jusqu'à son
  milieu, chaque attente au milieu de ses âges, pondéré. Trois conventions :
  chaque condition pèse ses départs sans carrière complète, la part de
  celles-ci étant la même à tout âge et à toute place ; l'attente se compte
  de l'âge où l'inaptitude ouvre le taux plein, que le pilote fixe — le
  portage le lit (`apres_le_taux_plein`, `pont.mjs`) —, à toute génération,
  sans échelle : de lui à l'âge d'annulation de la décote, il y a cinq ans à
  chacune (60 et 65 ans, 61 ans et 2 mois et 66 ans et 2 mois, 62 et
  67 ans) ; l'inapte qui attend ne valide rien de plus, sa carrière étalée
  jusqu'à 60 ans, et ne surcote pas, n'ayant pas la durée requise
  (L. 351-1-2) — la mesure ne le range plus parmi les surcotes
  (`condition_au_depart`). Les départs d'avant l'âge légal, de l'invalidité
  surtout, des handicaps et des statuts qui ouvrent plus tôt, ne comptent
  pas, ni ceux de l'âge d'annulation et après (0,6 %).
- *Le calcul posé à la main* (`test_l_attente_des_invalides_et_des_inaptes_se_lit_dans_l_eir`).
  Femmes nées en 1953 : sans carrière complète, 1 − 0,676 = 0,324 des
  invalides, 1 − 0,147 = 0,853 des inaptes. À l'âge légal, 37,5 × (0,324 ×
  17,9 + 0,853 × 13,7) = 37,5 × 17,4857 = 655,714. Par âge : 61 ans, 42,1 ×
  (0,324 × 16,1 + 0,853 × 13,0) = 686,457, moins l'âge légal, 30,744 ;
  62 ans, 8,9 × 11,0605 = 98,438 ; 63 ans, 5,0 × 9,5926 = 47,963 ; 64 ans,
  5,7 × 9,5483 = 54,425 ; 65 ans, 2,9 × 8,2040 = 23,792 ; 66 ans, 14,9 ×
  0,9621 = 14,335 ; en tout 925,411. Attentes, du milieu de chaque âge à
  61 ans et 2 mois : 0,4167 (de 61 ans et 2 mois à 62 ans), 1,3333, 2,3333,
  3,3333, 4,3333, 4,9167 (de 66 ans à 66 ans et 2 mois). Première attente,
  (30,744 × 0,4167 + 98,438 × 1,3333) / 129,182 = 1,1152 an, pour
  129,182 / 925,411 = 13,96 % ; seconde, 466,911 / 140,515 = 3,3228 ans,
  pour 15,18 % ; à l'âge légal, 655,714 / 925,411 = 70,86 %. Hommes : 0,347
  et 0,829 ; à l'âge légal, 24,4 × 21,484 = 524,210 ; par âge, 21,739,
  77,067, 35,068, 44,971, 17,350, 15,158 ; en tout 735,562 : 71,27 % à
  l'âge légal, 13,43 % après 1,1317 an, 15,30 % après 3,3892 ans.
- *Les tests.* Trois de plus (`test_grille_large.py`) :
  `test_l_attente_des_invalides_et_des_inaptes_se_lit_dans_l_eir` refait le
  calcul ci-dessus des cellules ; `test_les_invalides_et_les_inaptes_attendent_comme_ceux_des_nes_en_1953`
  veut chaque jumelle inapte en trois, aux poids des trois parts, de mêmes
  parts de génération ; `test_un_inapte_qui_attend_part_apres_l_age_de_son_taux_plein`
  pose l'homme d'une carrière de vingt-cinq années, inapte : né en 1955, ses
  jumelles partent à 62 ans, 63 ans et 1,6 mois, 65 ans et 4,7 mois, au taux
  de 50 %, sur ses 100 trimestres, sans surcote, rangées au taux plein ; né
  en 1965, de 62 ans, et non de son âge légal, 62 ans et 9 mois ; né en
  1940, de 60 ans, avant que la surcote existe. Le premier vu rouge faute
  de la version (`attentes_des_inaptes` absente), les deux autres la lisant
  aussi ; verts avec elle. Un test de la trente-deuxième version lit
  désormais le code de la jumelle sans son attente. `-m rapide`, avec et
  sans `PRESOMPTIONS_DECALEES`, 4 411 et 4 206 passés ; les fichiers qui
  lisent `grille_large.py` (`test_grille_large.py`, `test_controle_eacr.py`,
  `test_part_minimum_contributif.py`, `test_recours_aspa.py`, 136 passés),
  `test_pont.py` et les confrontations légères (474 passés) ;
  `regenerer.py --verifier`, tout à jour.
- *La mesure, après*, au même script, sur le même commit et les changements
  de cette version :

  | | EIR, nés en 1953 | population, avant | après |
  |---|---|---|---|
  | invalides et inaptes, part des départs des femmes | 9,40 | 9,40 | 9,40 |
  | des hommes | 7,58 | 7,58 | 7,58 |
  | femmes, à l'âge légal | 70,8 | 100 | 70,9 |
  | femmes, entre les deux âges | 28,6 | 0 | 29,1 |
  | hommes, à l'âge légal | 71,3 | 100 | 71,3 |
  | hommes, entre les deux âges | 28,1 | 0 | 28,7 |
  | femmes, âge moyen de départ | | 61,17 | 61,83 |

  La colonne de l'EIR pèse chaque condition de ses départs sans carrière
  complète, sans ceux d'avant l'âge légal (1,2 % des femmes, 2,6 % des
  hommes), le reste à l'âge d'annulation et après (0,6 %). Par âge révolu,
  les femmes nées en 1953 : 70,9 % à 61 ans, 14,0 à 62 et 15,2 à 64 ans
  dans la population ; 74,2, 10,6, 5,2, 5,9, 2,6 et 1,5 % de 61 à 66 ans
  dans l'EIR, la même moyenne aux milieux des âges. Chaque génération de 1950 à 1965 se décline
  de même, 70,9 et 29,1 % chez les femmes, 71,3 et 28,7 chez les hommes,
  chacune de l'âge où l'inaptitude lui ouvre le taux plein : 60, 61 ans et
  2 mois, puis 62 ans.
- *Ce que cela déplace.* Les autres variantes gardent leur poids : seuls
  les inaptes changent de place. Parmi tous les départs des femmes nées en
  1953, 9,40 × 0,291 = 2,7 points passent de l'âge légal à l'entre-deux :
  58,6 % à l'âge légal au lieu de 61,3, 17,6 % entre les deux âges au lieu
  de 14,9 (la mesure du matin, `2026-11-05-etape-14-duree-des-femmes.txt` ;
  EIR 37,5 et 26,7) ; de même 48,8 et 25,1 % pour la génération 1955, au
  lieu de 51,5 et 22,4. Les hommes, 7,58 × 0,287 = 2,2 points.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action
  157) ; aucun moteur, aucun témoin, aucun fichier fabriqué ; la part des
  invalides et des inaptes de chaque génération ; aucune règle du scénario
  1 : pas d'entrée au journal de veille.

**Ce qui reste**, de ce point :

1. *Les attentes de 1950.* L'EIR de 2016 range moins d'invalides et
   d'inaptes entre les deux âges : 22,7 % des femmes et 22,8 % des hommes
   nés en 1950, aux mêmes conventions, quand la version donne aux
   générations d'avant 1953 les attentes des nés en 1953, 29,1 et 28,7 %.
   Les attentes de chaque génération, en droite ligne de 1950 à 1953 comme
   la part des inaptes, demanderaient une jumelle par attente et par
   génération ; candidat, non fait.
2. *L'âge dans chaque attente.* La population fait partir à un seul âge les
   départs de 63 à 66 ans, à 64 ans et demi : la moyenne est celle de
   l'EIR, non la forme (5,2, 5,9, 2,6 et 1,5 % de 63 à 66 ans chez les
   femmes).
3. *Les invalides d'avant l'âge légal* (4,3 % des femmes, 7,6 % des hommes
   partis pour invalidité, nés en 1953), dont le classeur ne dit pas le
   motif ; la population les fait partir à l'âge où l'inaptitude ouvre le
   taux plein, ou plus tard.
4. Les points 1, 3 et 4 de la trente-deuxième version : la mortalité des
   inaptes, les générations hors de l'enquête, les exploitants et les
   libéraux.

Renvoi du 5 novembre 2026 : les 17,6 et 25,1 % entre les deux âges valent 17,7 et 25,2 (17,69 et 25,17, remesurés), dans `2026-11-05-retouches-6.md`.
