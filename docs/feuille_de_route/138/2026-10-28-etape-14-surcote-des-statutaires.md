# Étape 14, la population : la surcote des statutaires

**Le 28 octobre 2026 : les fonctionnaires civils de la population partent
aussi après leur taux plein, avec une surcote, dans la part et de la surcote
moyenne que le jaune pensions trouve à leur catégorie ; la trente-troisième
version, sur `main` (9e6dbbd). La génération 1955 surcote 15,9 % de ses
départs, et non 9,4 (EIR 14,4) : ses hommes au point près, 14,3 % (14,6), ses
femmes au-delà, 17,4 % (14,3). Elle part entre l'âge légal et l'âge
d'annulation pour 26,7 % (26,6), et non 22,5, à l'âge légal pour 37,6 % et non
41,1 (31,2). L'État surcote 42,4 % de ses liquidants de 2020 à 2025 (jaune
2025 : 42,7 % des départs pour ancienneté), la CNRACL 24,4 % (24,3) ; ils
partent à 63,0 et 62,7 ans en moyenne, et non à 62,1 et 62,2 (63,2 et 62,9).
Ce qui s'éloigne : les femmes, la génération 1950 (15,7 % pour 11,8) et le
stock de l'État en 2024 (30,3 % pour 22,6), que la part du salariat, comptée
avec les statutaires, et la part de 2025, prêtée à toutes les générations,
surchargent. Une simulation, deux pesées ; la mesure tient 5,1 Go au plus. La
version reste ; la page ne bouge pas.**

Demande : la vague du 28 octobre 2026, une session par tâche, lancée par le
propriétaire (« Lance une session par tâche qui n'a pas besoin de moi ») :
l'action 138, étape 14, un point du bloc de l'étape, la surcote des
statutaires dans la population (« Ce qui reste », point 1, de la note de la
vingtième partie, `2026-10-25-etape-14-decote-des-carrieres-qui-le-peuvent.md`) ;
ni les limites, ni ce que le bloc réserve au propriétaire.

- *Ce qui était.* La dix-neuvième version (`DEPARTS_AVEC_SURCOTE`) fait
  surcoter le salariat et les non-salariés de trente années validées et plus ;
  « les statutaires gardent leur départ », au taux plein ou à l'ouverture de
  leur statut. La note de la huitième partie le relevait, des départs d'entre
  l'âge légal et l'âge d'annulation : « Il en manque un tiers : les
  statutaires gardent leur départ, quand l'État surcote deux fois plus que la
  Cnav », 38,9 % de ses liquidants civils de 2024 pour 18,9 % (EACR, table H).
  La population compte cinq fonctionnaires civils — le sédentaire, l'actif et
  le super-actif de l'État, le sédentaire et l'actif de la CNRACL —, chacun
  seul de son régime ou polypensionné, à sept rangs et des deux sexes : 140
  carrières, 18,6 % des femmes et 13,0 % des hommes ; puis le militaire et les
  agents de la conduite et des IEG.
- *La source* : le jaune pensions annexé au PLF 2027
  (`macro/caracteristiques_fonction_publique.csv`, certifié, qu'aucun calcul
  ne lit), qui dit des départs pour ancienneté de 2025 de chaque catégorie
  combien surcotent et de combien, leur taux moyen de surcote
  (`SURCOTES_DU_JAUNE`, recopié et relu au fichier par le test) :

  | | départs | surcotent | taux moyen | attente |
  |---|---:|---:|---:|---:|
  | État, tous (B-3) | 41 812 | 42,7 % | 10,6 % | |
  | État, actifs (B-4) | 5 552 | 29,3 % | 9,7 % | 1,94 an |
  | État, super-actifs (B-4) | 3 347 | 8,1 % | 12,0 % | 2,40 ans |
  | État, sédentaires et carrières longues | 32 913 | 48,5 % | 10,7 % | 2,13 ans |
  | CNRACL, sédentaires (B-5) | 27 477 | 30,3 % | 10,2 % | |
  | CNRACL, carrières longues (B-5) | 15 054 | 21,5 % | 12,0 % | |
  | CNRACL, sédentaires et carrières longues | 42 531 | 27,2 % | 10,7 % | 2,14 ans |
  | CNRACL, actifs (B-5) | 10 597 | 13,8 % | 8,4 % | 1,68 an |

  Le sédentaire de chaque caisse porte ses carrières longues (`castypes`,
  `DEPARTS_ETAT_CIVILS_2025`, `DEPARTS_CNRACL_2025`) : à la CNRACL, le B-5
  dit leur surcote ; à l'État, le B-4 ne la dit pas, et tous les départs pour
  ancienneté du B-3, moins les deux catégories actives, donnent celle des
  sédentaires et des carrières longues ensemble, 15 956 des 32 913 départs.
  L'attente compte autant de trimestres que la surcote moyenne, à 1,25 % le
  trimestre depuis 2009 (L. 14, III ; barème `fonction_publique` de
  `surcote_baremes.csv`, que le test relit aussi).
- *La trente-troisième version* (`SURCOTE_DES_STATUTAIRES`,
  `surcotes_des_fonctionnaires`, `debut_de_la_surcote`,
  `departs_des_fonctionnaires_avec_surcote`, `CasTypeLarge.depuis_la_surcote`,
  9e6dbbd, 3bded86). Chaque carrière de fonctionnaire civil qui part au taux
  plein se décline : la part de sa catégorie attend, après le premier âge où
  le modèle sert une surcote à sa pension de fonctionnaire, l'attente de sa
  catégorie ; le reste part au taux plein. Ce premier âge se cherche dans les
  liquidations du modèle lui-même, de trimestre en trimestre à partir du taux
  plein, en doublant le pas puis par dichotomie, sur ce que la surcote ajoute
  à la pension (`PensionRegime.surcote`) : sans réécrire ce que le droit
  oppose à l'emploi classé, son âge de la surcote (`ouvrir.age_surcote`) et
  sa durée requise. Le plus souvent, c'est le taux plein : le sédentaire de
  l'État né en 1960, entré à 22 ans, a ses 167 trimestres à 63 ans et 9 mois,
  et part 2,13 années plus tard. L'actif a le taux plein à sa limite d'âge,
  sans la durée : l'actif de l'État né en 1960 l'a à 62 ans et ne surcote
  qu'à partir de 63 ans et demi. Quand le modèle surcote déjà au taux plein
  que le pilote fixe, la recherche redescend : le sédentaire polypensionné
  né en 1945, au taux plein à 62 ans, surcote dès 60 ans et demi. Elle se
  fait au moment de simuler, 0,14 seconde par carrière et génération : la
  construction de la population n'en coûte rien. Le militaire, à qui ni le
  modèle ni la table H ne comptent de surcote, et les agents de la conduite
  et des IEG, qui partent à l'ouverture de leur statut, gardent leur départ.
  Cinq conventions : la part et l'attente de 2025 à toutes les générations,
  sans égard au sexe ni au rang ; une attente par catégorie, celle de la
  surcote moyenne, le jaune ne publiant pas leur distribution ; le sédentaire
  porte ses carrières longues ; le début de la surcote au trimestre près ;
  une génération à l'âge légal avant 2004 n'attend pas, comme au salariat
  (`ANNEE_DE_LA_SURCOTE`).
- *Les tests* (`test_grille_large.py`), trois de plus, vus rouges faute de
  la version. `test_la_surcote_des_fonctionnaires_civils_se_lit_dans_le_jaune`
  relit au fichier certifié chaque ligne de `SURCOTES_DU_JAUNE` et le barème
  de 1,25 %, et refait à la main la part et l'attente de chaque catégorie.
  `test_une_part_de_chaque_categorie_de_fonctionnaires_civils_part_avec_une_surcote`
  pèse, catégorie par catégorie et sexe par sexe, les jumelles qui surcotent
  contre toutes les carrières de leur catégorie, et vérifie que le militaire
  et les agents de la conduite et des IEG n'en ont pas.
  `test_un_fonctionnaire_civil_qui_surcote_part_avec_la_surcote_moyenne_de_sa_categorie`
  fait partir la jumelle de la classe médiane née en 1960 de chaque
  catégorie, seule de son régime ou polypensionnée, des deux sexes : le modèle
  lui sert la surcote moyenne de sa catégorie au trimestre près, et la mesure
  des départs la range parmi les surcotes ; le sédentaire de l'État part à
  22 ans plus 167 trimestres plus 2,13 années ; et la recherche, partie d'un
  taux plein trop tardif, 65 ans, retrouve ses 63 ans et 9 mois. Le test de
  la dix-neuvième version ne pèse plus que le salariat et les non-salariés.
  Le troisième figeait d'abord le super-actif polypensionné né en 1960, au
  taux plein à 63 ans et 9 mois, qui surcotait dès 62 ans et demi : le pilote
  du jour (02f3ea9) l'a fait partir au taux plein à 59 ans et 9 mois, et
  l'assertion a rougi la suite complète de GitHub (course 40708735615) ;
  l'épreuve du sédentaire, qui ne dépend pas du pilote, la remplace
  (3bded86). Le fichier passe en 3 min 55 s sur quatre cœurs, 89 tests.
- *La mesure.* Une simulation, deux pesées : la version ne change aucune
  autre carrière, et la population de 9e6dbbd, sous laquelle la trente et
  unième et la trente-deuxième versions des autres sessions du jour — la
  décote entre les deux âges, les invalides et les inaptes — sont déjà, se
  simule une fois sur l'arbre figé de ce commit (`CALCULS_SANS_MEMOIRE=1`, son
  `src/` sur le chemin), avec les 140 jumelles, puis se pèse sans elles et
  avec elles, comme `grille_large.py --grille population --distribution` et
  `controle_eacr.py --population` la mesurent, les conditions de départ et
  les proratisations de chaque couple calculées une fois pour les deux (un
  pilote hors du dépôt, qui appelle leurs fonctions). La surcote des
  fonctionnaires civils se lit de plus sur leurs liquidants de chaque année
  de 2020 à 2025, et sur leur stock de 2024, chaque couple rangé par la
  condition de son départ (`condition_au_depart`). Sur quatre cœurs : 186
  minutes, dont 125 de simulation, 16 874 cas types, 471 944 couples ; 5,1 Go
  au plus, la mémoire de tous les processus relevée toutes les vingt secondes.
  Elle précède le pilote du jour (02f3ea9) et les versions poussées depuis
  par les autres sessions : la population de `main` n'est plus tout à fait
  celle qu'elle mesure.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 :

  | | EIR | sans | avec |
  |---|---|---|---|
  | ensemble 1955, surcote | 14,4 | 9,4 | 15,9 |
  | femmes de 1955, surcote | 14,3 | 9,8 | 17,4 |
  | hommes de 1955, surcote | 14,6 | 9,1 | 14,3 |
  | ensemble 1955, à l'âge légal | 31,2 | 41,1 | 37,6 |
  | ensemble 1955, entre lui et l'âge d'annulation | 26,6 | 22,5 | 26,7 |
  | femmes de 1955, à l'âge légal | 37,5 | 56,0 | 49,3 |
  | femmes de 1955, entre les deux | 26,7 | 14,6 | 22,2 |
  | ensemble 1955, taux plein, autrement | 44,4 | 52,9 | 46,3 |
  | ensemble 1950, surcote | 11,8 | 9,4 | 15,7 |
  | femmes de 1950, surcote | 11,2 | 9,6 | 16,9 |
  | hommes de 1950, surcote | 12,3 | 9,3 | 14,4 |
  | ensemble 1950, entre les deux âges | 23,8 | 27,2 | 29,6 |

  Les fonctionnaires civils, leurs liquidants de 2020 à 2025 contre le jaune
  de 2025 (tableaux B-3 et B-3bis, départs pour ancienneté) et l'EACR de 2020
  à 2024 (table H, tous les départs), puis les liquidants de 2024 de tous les
  régimes contre l'EACR (table C) et les retraités de 2020 contre l'EIR :

  | | jaune, EACR, EIR | sans | avec |
  |---|---|---|---|
  | État, liquidants partis avec une surcote | 42,7 ; EACR 38,4 | 0 | 42,4 |
  | État, leur âge moyen | 63,2 | 62,1 | 63,0 |
  | CNRACL, liquidants partis avec une surcote | 24,3 | 0 | 24,4 |
  | CNRACL, leur âge moyen | 62,9 | 62,2 | 62,7 |
  | État, retraités de 2024 partis avec une surcote | EACR 22,6 | 0 | 30,3 |
  | liquidants de 2024 partis à 62 ans | 26,0 | 60,5 | 54,6 |
  | partis à 64 ans | 7,0 | 0,3 | 4,4 |
  | partis à 66 ans | 5,8 | 0,3 | 2,6 |
  | âge moyen des liquidants de 2024 | 63,60 | 62,36 | 62,56 |
  | pension moyenne des femmes en 2020, € par mois | 1 177 | 1 325 | 1 334 |
  | pension moyenne des hommes en 2020 | 1 957 | 1 815 | 1 823 |
  | neuvième décile des hommes | 3 242 | 2 956 | 3 015 |

  Année par année, l'État surcote 41,9, 44,9, 42,7, 30,5, 51,2 et 43,3 % de
  ses liquidants de 2020 à 2025 : la grille simule ses générations de cinq en
  cinq ans, et les jumelles d'une génération partent d'autres années civiles
  que ses carrières au taux plein ; les hommes surcotent 7,0 % en 2023, 74,0 %
  en 2024. La moyenne des six années le dit, non une année seule. L'écart de
  Kolmogorov des femmes passe de −14,6 à −14,3 points à 900 €, celui des
  hommes de +5,1 à +4,7 à 1 800 €. La décote du régime général ne bouge pas.
- *Ce que cela dit.*
  - Les départs de la génération 1955 rejoignent l'EIR : la surcote de ses
    hommes au point près, ses départs d'entre l'âge légal et l'âge
    d'annulation au dixième, ceux de l'âge légal à 6 points et non 10. Ce
    qui manquait aux départs d'entre les deux âges, que la note de la
    huitième partie prêtait aux statutaires, leur revenait bien.
  - Les fonctionnaires civils surcotent comme le jaune le dit, l'État 42,4 %
    de ses liquidants pour 42,7, la CNRACL 24,4 pour 24,3, et partent à l'âge
    qu'il leur trouve, à trois mois près : la recherche du début de la
    surcote fait partir chacun du jour où sa surcote court, l'actif comme le
    sédentaire. L'EACR, qui compte aussi leurs départs pour invalidité et pour
    motifs familiaux, en voit 38,4 % : la population n'a pas ces départs-là
    chez les fonctionnaires.
  - Ce qui s'éloigne tient à ce que la version ne fait pas. Les femmes de
    1955 surcotent 17,4 % (14,3) : la part du salariat que la dix-neuvième
    version prend à l'EIR est celle de tous les retraités, statutaires
    compris, et compte une seconde fois leur surcote, désormais la leur ;
    prise sans elle, comme la trentième version prend la décote sans les
    agents, elle laisserait au salariat 6,7 points des femmes de 1955 et non
    9,8. La génération 1950 surcote 15,7 % (11,8), et le stock de l'État en
    2024, 30,3 % (22,6) : la part de 2025 vaut pour toutes les générations,
    quand l'État surcotait 14 % de ses liquidants civils en 2004, 28 % en
    2011, 31 % en 2015, 35 % en 2025 (jaune, tableau 103, tous les départs).
  - Les liquidants de 2024 partent un peu plus tard, à 62,56 ans et non
    62,36 (63,60), moins à 62 ans, plus à 64 et 66 : le reste de leur écart
    à l'EACR est ailleurs, aux départs de 63 ans (6,5 % pour 18,6) et de
    68 ans et plus (aucun pour 7,3).
  - La distribution de 2020 en dit peu : neuf euros de plus aux femmes, huit
    aux hommes, dont le neuvième décile monte de 59 €.
  - La version reste : elle donne aux fonctionnaires civils la surcote et
    l'âge que le jaune leur trouve, et aux départs de la génération 1955 leur
    place dans l'EIR.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles, dont les
  fonctionnaires gardent leur départ ; le modèle ; le registre, dont aucun
  point « 138.14 » ne nomme la surcote des statutaires. Aucune règle du
  scénario 1 ne change : pas d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore — sans la surcote des statutaires, désormais
   faite : les départs entre l'âge légal et l'âge d'annulation ; la part
   d'avant 1950 sur le stock de 2020 ; les parts des nés en 1950 et en 1953
   parmi les seuls résidents, si l'EIR les publie ; les déclinaisons du bas
   qui pourraient décoter quand leur carrière ne le peut pas ; les natures
   des carrières incomplètes ; le plafond de chaque génération ; la
   maternité ; le calage de la durée des femmes ; la durée des carrières
   pleines que la onzième version prend à l'EIR ; les invalides et les
   inaptes ; la part passagère du revenu des indépendants et la carrière
   saisonnière des salariés agricoles, si une source les publie ; le juge
   propre des artisans, la part des liquidants du RSI au minimum contributif
   d'avant 2020 ; la part des générations 1946 à 1953 au minimum ; la
   fragmentation selon la génération ; la décote selon la tranche ou le rang
   (le détail de chacun : note de la vingtième partie). La part du
   salariat qui surcote, prise sans ce que les fonctionnaires surcotent
   désormais, comme la trentième version prend la décote sans les agents :
   les femmes de 1955 surcotent 17,4 % (EIR 14,3). La surcote des
   fonctionnaires selon la génération, que le jaune donne année par année de
   2004 à 2025 (tableaux 103 et 105) : la génération 1950 surcote 15,7 %
   (11,8), le stock de l'État en 2024, 30,3 % (EACR 22,6). La surcote des
   agents des régimes spéciaux, si une source en publie la part.
   Les niveaux des cas types statutaires et non salariés, et la dispersion
   des libéraux, attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, encore : le départ qui suivrait l'incitation, au
   propriétaire (note de la huitième partie).
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).
