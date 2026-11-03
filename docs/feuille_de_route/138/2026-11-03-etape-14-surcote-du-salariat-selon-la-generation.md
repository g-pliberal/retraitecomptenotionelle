# Étape 14, la trente-septième version : la surcote du salariat sans les statutaires, et selon la génération

**Le 3 novembre 2026 : la part du salariat qui surcote se prend désormais sans
celle des fonctionnaires civils, et l'une et l'autre suivent la génération ;
la trente-septième version, sur `main` (624ec9f). La génération 1955 surcote
pour 14,0 % de ses départs (EIR 14,4) et non 16,0, ses femmes pour 14,8 %
(14,3) et non 17,4 ; la génération 1950, pour 11,3 % (11,8) et non 15,8 ; le
stock de l'État en 2024, pour 23,4 % (EACR 22,6) et non 30,1. Ce que le
double compte cachait s'éloigne : les hommes de 1955 surcotent pour 13,3 %
(14,6) ; les nouveaux retraités du régime général de 2024, pour 10,9 % et non
13,3, quand la Cnav en voit surcoter 18,9 %, faute de départs après 67 ans et
d'une source sur les générations d'après 1953 ; les femmes de 1955 partent à
l'âge légal pour 50,8 % (37,5) et non 48,7. Une simulation, trois pesées. La
version reste ; la page ne bouge pas.**

Demande : la troisième vague, lancée dans la nuit du 2 au 3 novembre 2026 par
la session d'orchestration, file I : l'action 138, étape 14, le point suivant
de la file, « la surcote du salariat, sans les statutaires, et selon la
génération », que la note de la surcote des statutaires détaille (« Ce qui
reste », point 1, `2026-10-28-etape-14-surcote-des-statutaires.md`) et que la
limite du coût agrégé reprend (`docs/limites/5-bis-cout-agrege.md`).

- *Ce qui était.* La dix-neuvième version (`DEPARTS_AVEC_SURCOTE`) fait
  surcoter le salariat et les non-salariés de trente années validées et plus
  dans la part que l'EIR voit surcoter parmi les carrières complètes des nés
  en 1953, 21,7 % des femmes et 17,7 % des hommes ; la trente-troisième
  (`SURCOTE_DES_STATUTAIRES`), les fonctionnaires civils dans la part de leur
  catégorie parmi les départs pour ancienneté de 2025 — 48,5 % des
  sédentaires de l'État, 27,2 % de ceux de la CNRACL. L'une et l'autre valent
  à toutes les générations qui atteignent leur âge légal depuis 2004, et la
  première, prise à l'EIR statutaires compris, compte une seconde fois leur
  surcote, désormais la leur. Au poids de retraité de 2020, les
  fonctionnaires civils surcotent pour 6,4 % de toutes les femmes, le
  salariat pour 10,3 %, 16,7 % ensemble, quand l'EIR voit surcoter 14,2 % des
  résidentes nées en 1953 ; la mesure du 28 octobre trouvait 17,4 % de femmes
  de 1955 parties avec une surcote (EIR 14,3), 15,7 % de la génération 1950
  (11,8), 30,3 % du stock de l'État en 2024 (EACR 22,6).
- *Les sources*, déjà certifiées. L'EIR des nés en 1950 et en 1953
  (`departs_generations.csv`), ses résidents en France : 11,2 % des femmes et
  12,2 % des hommes nés en 1950 sont partis avec une surcote, 14,2 et 14,4 %
  des nés en 1953. Le jaune pensions annexé au PLF 2027
  (`caracteristiques_fonction_publique.csv`), la part de tous les départs de
  chaque année qui surcotent : aux civils de l'État (tableau 103), 14 % en
  2004, où naît la surcote, 28 % en 2011, 36 % en 2012, 31 % de 2013 à 2015,
  28 % en 2017, 34 % en 2020, 38 % en 2023, 35 % en 2025 ; à la CNRACL
  (tableau 105), 8 % en 2004, 19 % en 2013, 17 % en 2017, 24 % en 2023 et en
  2024, 21,5 % en 2025 ; ni 2005 à 2010 à l'État, ni 2005 à 2012 à la CNRACL.
  Le fichier, qu'aucun calcul ne lit, le reste : ses deux séries sont
  recopiées (`SURCOTES_DU_JAUNE_PAR_ANNEE`), que le test relit, comme la
  trente-troisième version recopie `SURCOTES_DU_JAUNE`.
- *La trente-septième version* (`SURCOTE_SELON_LA_GENERATION`,
  `surcotes_des_fonctionnaires_selon_la_generation`, `surcote_du_jaune_en`,
  `surcotes_des_generations`, `parts_du_salariat_qui_surcote`,
  `jumelles_selon_la_generation`, `surcote_au_statut`, `naissances_simulees`,
  `aux_naissances`, `parts_multipliees` ; 624ec9f). Les jumelles qui surcotent
  et leurs sœurs sont celles des deux versions, à leur poids ; chaque année
  de naissance leur donne désormais la part de sa génération
  (`Variante.parts_des_generations`), comme la décote selon la génération :
  - au fonctionnaire civil, la part de sa catégorie en 2025, fois ce que la
    part de tous les départs de sa caisse qui surcotent est à celle de 2025,
    l'année où sa génération atteint son âge légal, en droite ligne entre
    deux années publiées : né en 1950, à 60 ans en 2010, 26 % à l'État, et
    le sédentaire surcote pour 36,0 % au lieu de 48,5 ; né en 1955, en 2017,
    28 % ; né en 1960, en 2022, 36 %, la part de 2025 fois 1,03 ;
  - au salariat et aux non-salariés, ce qui manque aux fonctionnaires civils
    qui surcotent pour que tous les retraités du sexe surcotent la part que
    l'EIR mesure aux résidents de leur génération — celle des nés en 1950,
    en droite ligne jusqu'à celle des nés en 1953, celle de 1950 avant,
    celle de 1953 après —, divisé par le poids des carrières qui peuvent
    surcoter, chacune à son poids de retraitée de 2020, comme la trentième
    version prend la décote sans les agents. Les femmes nées en 1955
    surcotent ainsi pour 19,2 % des carrières du salariat qui le peuvent, et
    non 21,7 ; celles de 1950, 13,9 % ; de 1960, 16,1 % ; les hommes de 1955,
    17,7 %, comme avant, ceux de 1950, 13,6 %, de 1960, 16,1 %.

  La population garde ses 19 408 cas types, leurs carrières et leurs poids :
  la version éteinte redonne les mêmes, et une même simulation sert chaque
  pesée.
- *Trois conventions.* L'année où la génération atteint son âge légal date
  la part de sa caisse, celle qui dit déjà qu'elle n'attend pas avant 2004
  (`ANNEE_DE_LA_SURCOTE`) ; ses départs avec surcote tombent deux à quatre
  ans plus tard, et la montée de 2004 à 2012 en est avancée d'autant. La part
  de chaque catégorie suit celle de tous les départs de sa caisse, invalidité
  et motifs familiaux compris, la seule que le jaune publie chaque année.
  L'EIR ne voyant que les nés en 1950 et en 1953, les générations d'avant
  1950 prennent la part de 1950, celles d'après 1953 celle de 1953, et
  toutes gardent les attentes des nés en 1953.
- *Les tests* (`test_grille_large.py`, deux de plus, vus rouges faute de la
  version). `test_la_surcote_des_fonctionnaires_suit_l_annee_ou_leur_generation_atteint_l_age_legal`
  relit au fichier certifié les deux séries, et pose à la main la part de
  chaque catégorie : nés en 1950, à 60 ans en 2010 (L. 161-17-2),
  0,14 + 0,14 × 6/7 = 26 % à l'État, 0,08 + 0,11 × 6/9 = 15,3 % à la CNRACL ;
  nés en 1953, à 61 ans et 2 mois, 31 % à l'État ; nés en 1960, à 62 ans en
  2022, 36 et 22 % ; nés en 1975, la part de 2025.
  `test_la_surcote_du_salariat_se_prend_sans_celle_des_statutaires` pèse la
  population, année de naissance par année de naissance de 1946 à 1970 :
  tous les retraités de chaque sexe surcotent la part de l'EIR — 11,2 et
  12,2 % des nés en 1950, 13,2 et 13,7 % en 1952, 14,2 et 14,4 % des nés en
  1953 et après —, chaque catégorie de fonctionnaire civil la sienne, le
  salariat ni rien ni tout, les femmes de 1955 moins que les 21,7 % de la
  dix-neuvième version ; chaque carrière garde son poids ; la version éteinte
  redonne les mêmes cas types, aux mêmes poids. Un test ancien éteint la
  version, celui de la décote selon la génération, qui éprouve la décote
  seule et lisait une part de un à toute carrière complète. Les 98 tests du
  fichier passent en 3 min 9 s sur quatre cœurs ; la suite rapide, 4 165
  tests ; les trois tests touchés, et la suite rapide, sous la garde des
  présomptions décalées.
- *La mesure.* Une simulation, trois pesées. La population de la version,
  19 408 cas types, est celle de la trente-sixième, aux parts des générations
  près : simulée
  une fois au portage, sur un arbre figé d'avant la version (a229ec1),
  en 25 tranches de 800 cas types gardées sur le disque, sans la mémoire des
  calculs, en 124 minutes sur quatre cœurs, les tests de la version tournant
  à côté : 542 749 couples, 20 083 échecs (17 038 liquidations antérieures à
  la répartition, 3 045 carrières sans régime actif), ceux de la
  trente-sixième. Les conditions de départ de 77 730 couples — les
  générations 1950 et 1955, le régime général de 1960 et 1965, les
  fonctionnaires civils nés depuis 1940 — se lisent une fois, en 4 minutes ;
  les poids de la page une fois, en 14 minutes, les parts des générations
  changeant seules d'une pesée à l'autre ; chaque pesée prend 4 à 8 minutes
  (un pilote hors du dépôt, qui appelle les fonctions du script et de
  `controle_eacr.py`, sur 624ec9f) ; moins de 4 Go, vus de `free`. La
  troisième pesée éprouve une autre convention, la part propre du salariat
  figée hors des nés de 1950 à 1953 au lieu de leur surcote entière. Le stock
  de 2020 par tranche d'âge et les retraités du régime général de 2024 se
  comptent au drapeau des jumelles, celle qui surcote d'une génération qui
  atteint son âge légal depuis 2004 tenue pour surcotée ; le reste, à la
  condition de départ de chaque couple (`condition_au_depart`).
- *Ce qu'elle trouve*, d'abord les départs de deux générations, en part des
  départs déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée
  sur les nés en 1953 :

  | | EIR | trente-sixième | trente-septième |
  |---|---|---|---|
  | ensemble de 1955, surcote | 14,4 | 16,0 | 14,0 |
  | femmes de 1955, surcote | 14,3 | 17,4 | 14,8 |
  | hommes de 1955, surcote | 14,6 | 14,4 | 13,3 |
  | ensemble de 1950, surcote | 11,8 | 15,8 | 11,3 |
  | femmes de 1950, surcote | 11,2 | 17,0 | 11,6 |
  | hommes de 1950, surcote | 12,3 | 14,5 | 10,9 |
  | ensemble de 1955, à l'âge légal | 31,2 | 37,3 | 38,4 |
  | ensemble de 1955, entre lui et l'âge d'annulation | 26,6 | 28,2 | 26,8 |
  | femmes de 1955, à l'âge légal | 37,5 | 48,7 | 50,8 |
  | femmes de 1955, entre les deux âges | 26,7 | 25,6 | 23,2 |
  | ensemble de 1950, à l'âge légal | 40,0 | 41,2 | 43,8 |
  | ensemble de 1950, entre les deux âges | 23,8 | 29,4 | 26,7 |

  Puis les fonctionnaires civils contre le jaune (départs pour ancienneté de
  2025) et l'EACR (table H), les retraités de 2020 contre les résidents de
  l'EIR (feuille « CondLiquidation »), ceux du régime général de 2024 contre la
  Cnav (table H), les liquidants de 2024 contre l'EACR (table C) :

  | | jaune, EIR, EACR | trente-sixième | trente-septième |
  |---|---|---|---|
  | État, liquidants de 2020 à 2025, surcote | 42,7 | 42,2 | 41,6 |
  | État, retraités de 2024, surcote | 22,6 | 30,1 | 23,4 |
  | CNRACL, liquidants de 2020 à 2025, surcote | 24,3 | 24,4 | 23,1 |
  | retraitées de 2020, surcote | 7,8 | 10,2 | 7,7 |
  | dont de 70 à 74 ans | 13,5 | 17,0 | 11,8 |
  | retraités de 2020, surcote | 9,4 | 9,1 | 7,4 |
  | dont de 70 à 74 ans | 16,2 | 16,7 | 12,6 |
  | fonctionnaires civils parmi les retraitées surcotées | 32,4 | 45,9 | 42,6 |
  | parmi les retraités surcotés | 24,7 | 32,0 | 27,4 |
  | régime général, liquidants de 2024, surcote | 18,9 | 13,3 | 10,9 |
  | régime général, retraités de 2024, surcote | 11,2 | 9,3 | 7,8 |
  | liquidants de 2024 partis à 62 ans | 26,0 | 56,9 | 58,4 |
  | âge moyen des liquidants de 2024 | 63,60 | 62,68 | 62,63 |
  | pension moyenne des femmes en 2020, € par mois | 1 177 | 1 349 | 1 345 |
  | pension moyenne des hommes en 2020 | 1 957 | 1 833 | 1 829 |

  Année par année, l'État surcote pour 37,2, 42,4, 41,9, 31,9, 50,6 et 45,3 %
  de ses liquidants de 2020 à 2025 (41,8, 44,8, 42,6, 30,4, 50,2 et 43,2
  avant) : la grille simule ses générations de cinq en cinq ans. La décote
  des liquidants du régime général de 2024 ne bouge pas, 17,1 % (Cnav 13,4).
  L'écart de Kolmogorov des femmes reste à −15,4 points, à 900 € et non plus
  1 200 ; celui des hommes passe de +4,3 à +4,5 points à 1 800 €. La
  troisième pesée, la part du salariat figée, fait surcoter la génération
  1955 pour 13,5 %, ses femmes pour 14,2, ses hommes pour 12,7, les
  retraitées de 2020 pour 7,2 % et les retraités pour 7,1, le régime général
  de 2024 pour 11,6 % ; la génération 1950, comme la version.
- *Ce que cela dit.*
  - Les générations que l'EIR voit surcotent comme elle : 11,3 % des départs
    de la génération 1950 (11,8), 14,0 % de ceux de la génération 1955
    (14,4) ; les femmes de 1955 ne surcotent plus pour 17,4 %, mais 14,8. Le
    double compte est levé. Les hommes de 1955, 13,3 % pour 14,6, gardent le
    point qui leur manquait déjà au regard de la part prêtée, 15,4 % au poids
    de 2020 avant la version : la part se calcule au poids des retraités de
    2020, la mesure pèse la génération au sien, en 2022.
  - Les fonctionnaires suivent l'histoire du jaune : le stock de l'État en
    2024 surcote pour 23,4 % (EACR 22,6), et non 30,1 ; ses liquidants de
    2020 à 2025, pour 41,6 % (42,7 en 2025). Les fonctionnaires civils
    tiennent une moindre part des retraités surcotés de 2020, 42,6 % des
    femmes et 27,4 % des hommes, sans rejoindre les 32,4 et 24,7 % de l'EIR :
    la part du jaune est celle des départs pour ancienneté, que la population
    prête à toutes ses carrières de fonctionnaire, sans les départs pour
    motifs familiaux ni pour invalidité, qu'elle ne distingue pas.
  - Ce qui s'éloigne, le double compte le cachait. La surcote du salariat des
    générations récentes : les liquidants du régime général de 2024
    surcotent pour 10,9 % et non 13,3, quand ceux de la Cnav surcotent pour
    18,9 % ; ses retraités de 2024, pour 7,8 % (11,2). La population n'a aucun
    départ après 67 ans, quand l'EACR en compte 7,3 % de ses liquidants de
    2024 : les attentes des nés en 1953 s'arrêtent à « 67 ans et plus », et
    les hommes de 70 à 74 ans de 2020, nés de 1946 à 1950, ont surcoté pour
    16,2 %, quand les nés en 1950 ne l'avaient fait que pour 12,2 % à 66 ans.
    Et l'EIR ne voit pas les générations d'après 1953, dont la version garde
    la surcote entière de 1953, quand leurs fonctionnaires surcotent
    davantage. L'âge légal des femmes, ensuite : 50,8 % des femmes de 1955 y
    partent (37,5), et non 48,7 ; leurs départs avec surcote en cachaient une
    part de l'excès que le calage de leur durée leur donne.
  - L'autre convention, la part propre du salariat figée hors des nés de 1950
    à 1953, fait moins bien partout, sinon chez les femmes de 1955 et au
    régime général de 2024 : la génération 1955 surcote pour 13,5 %, les
    retraités de 2020 pour 7,1 et 7,2 %. La version garde la surcote entière
    des nés en 1950 avant eux, celle des nés en 1953 après.
  - La distribution de 2020 en dit peu : quatre euros de moins aux femmes,
    quatre aux hommes ; les liquidants de 2024 partent à 62 ans pour 58,4 %
    et non 56,9 (26,0), à 62,63 ans en moyenne et non 62,68 (63,60).
  - La version reste : elle lève un double compte, donne aux fonctionnaires
    l'histoire que le jaune leur trouve et à chaque génération que l'EIR voit
    sa surcote ; ce qu'elle éloigne tient à ce qu'elle découvre.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les cas types, leurs
  carrières et leurs poids ; la décote, ses parts et ses attentes ; les
  attentes des surcotes ; le registre. Aucune règle du scénario 1 ne change,
  aucune source ne s'ajoute : pas d'entrée au journal de veille. Aucun
  fichier d'une autre file n'est touché.

**Ce qui reste** de l'étape : les autres points du bloc de l'étape, et, de
celui-ci :

1. *Les départs après 67 ans*, que la population n'a pas, quand l'EACR en
   compte 7,3 % de ses liquidants de 2024 : les attentes des nés en 1953
   s'arrêtent à « 67 ans et plus », pris pour 67 ans. Le stock de 2020 par
   tranche d'âge et la table C de l'EACR diraient ce qui surcote au-delà :
   les hommes nés de 1946 à 1950 ont surcoté pour 16,2 % à la fin de 2020,
   quand la génération 1950 n'en était qu'à 12,2 % à 66 ans.
2. *La surcote des générations nées après 1953*, que l'EIR ne voit pas, au
   propriétaire : la version leur garde la surcote entière des nés en 1953,
   14,2 % des femmes et 14,4 % des hommes, quand leurs fonctionnaires
   surcotent davantage ; les liquidants du régime général de 2024 surcotent
   pour 10,9 %, ceux de la Cnav pour 18,9 % (19,6 % des femmes, 18,0 % des
   hommes). Leur prêter la surcote de la Cnav, comme la vingt-neuvième
   version prête sa décote aux générations nées depuis 1960, est un choix de
   modèle, qui rejoint celui de la décote d'après 1960 (note des agents
   décotés avant 60 ans, « Ce qui reste », point 1). Il vaut mieux le
   trancher après le point 1, qui en explique une part.
3. *Les fonctionnaires parmi les retraités surcotés* : 42,6 % des femmes et
   27,4 % des hommes de 2020, pour 32,4 et 24,7 % dans l'EIR ; la part du
   jaune, celle des départs pour ancienneté, vaut pour toutes leurs
   carrières, et les départs pour motifs familiaux et pour invalidité, que le
   tableau B-3 du jaune compte, les distingueraient.
4. *La surcote des agents des régimes spéciaux*, si une source en publie la
   part.
