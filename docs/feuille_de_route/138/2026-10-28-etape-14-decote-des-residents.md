# Étape 14, suite : la décote des seuls résidents, et celle d'avant 1950 lue au stock de 2020 selon l'âge

**Le 28 octobre 2026 : la part des départs avec décote de chaque génération
est celle des seuls résidents en France, et, avant 1950, chaque génération
prend celle de sa tranche d'âge du stock des résidents de 2020 ; sur `main`,
les données (fcab957), puis la version (0386bb4). Les générations d'avant 1950
avaient toutes une part, 8,3 % des femmes et 3,6 % des hommes, celle qui ne
gardait au stock de 2020 la part de l'EIR qu'aux générations qu'il voit toutes
parties ; elles ont désormais celle que l'EIR mesure à leur tranche : 8,8,
6,3, 4,6 et 7,3 % des femmes nées en 1935 et avant, de 1936 à 1940, de 1941 à
1945, de 1946 à 1949 ; 1,8, 1,5, 1,9 et 3,7 % des hommes. Nés en 1950 et en
1953, les résidents décotent 7,5 et 11,9 % chez les femmes, et non 7,9 et
12,4 ; 4,5 et 7,7 % chez les hommes, et non 5,6 et 8,6. Les retraitées de
2020 décotent 8,6 % (EIR 8,8), et non 9,6 ; les retraités, 6,0 % (4,5), et
non 7,1, l'écart venant surtout des agents partis avant 60 ans. Une
simulation, quatre pesées. La version reste ; la page ne bouge pas.**

Demande : la vague du 28 octobre 2026, une session par tâche, lancée par le
propriétaire : l'action 138, étape 14, un point du bloc de l'étape, et lui
seul : la part d'avant 1950 sur le stock de 2020, qui ne garde la part de
l'EIR qu'aux générations qu'il voit toutes parties, sans celles de 1954 à 1958
— les retraitées de 2020 décotaient 10,5 %, pour 8,8 à l'EIR — ; avec elle,
les parts des nés en 1950 et en 1953 parmi les seuls résidents, si l'EIR les
publie (« Ce qui reste », point 1,
`2026-10-25-etape-14-decote-des-carrieres-qui-le-peuvent.md`).

- *Ce qui était.* Sous la vingt-neuvième version
  (`DECOTE_SELON_LA_GENERATION`), chaque génération part avec une décote pour
  la part que l'EIR compte aux nés en 1950 et en 1953, tous lieux de résidence
  (7,9 et 12,4 % des femmes, 5,6 et 8,6 % des hommes), en droite ligne entre
  eux, puis vers les liquidants de la Cnav de 2024 ; et, avant 1950, pour une
  seule part, celle qui donne aux générations jusqu'à 1953, chacune pesée de
  son effectif INSEE de 2020, la part des résidents de 2020, 8,8 et 4,5 %. Le
  stock de 2020 compte pourtant aussi les générations de 1954 à 1960, qu'il
  voit partir, et qui y décotent plus : 12,1 % des résidentes de 65 à 69 ans,
  11,5 % de celles de 60 à 64. La part d'avant 1950 portait donc la décote du
  stock à des générations qui décotent moins ; et les parts de 1950 et de
  1953, celles de tous les retraités, comptaient ceux de l'étranger, quand la
  population et le stock ne comptent que des résidents.
- *Ce que l'EIR publie.* Les deux classeurs d'une génération rangent aussi
  leurs retraités selon leur résidence (feuille « Naissance-Résidence ») :
  97,3 % des femmes nées en 1953 résident en France, et elles sont parties
  avec une décote pour 11,9 %, quand celles de l'étranger l'ont fait pour
  29,9 % ; les hommes, 7,7 et 33,1 % ; nés en 1950, 7,5 et 21,6 % des femmes,
  4,5 et 26,3 % des hommes. Et le classeur des résidents de 2020 dit l'âge, au
  31 décembre, des retraités de chaque condition de liquidation (feuille
  « CondLiquidation ») : la part des décotés dans chaque tranche de cinq ans
  s'en tire, l'effectif des décotés fois leur part dans la tranche, divisé
  par celui de tous fois la leur.

  | tranche d'âge en 2020 | générations | femmes | hommes |
  |---|---|---|---|
  | 50 à 59 ans | 1961 à 1970 | 18,4 | 5,7 |
  | 60 à 64 ans | 1956 à 1960 | 11,5 | 6,7 |
  | 65 à 69 ans | 1951 à 1955 | 12,1 | 7,5 |
  | 70 à 74 ans | 1946 à 1950 | 7,4 | 3,9 |
  | 75 à 79 ans | 1941 à 1945 | 4,6 | 1,9 |
  | 80 à 84 ans | 1936 à 1940 | 6,3 | 1,5 |
  | 85 ans et plus | 1935 et avant | 8,8 | 1,8 |
  | tous | | 8,8 | 4,5 |

  Les femmes décotent selon un U, les plus vieilles et les plus jeunes ; les
  hommes nés avant 1946 presque plus. Les résidents de 70 ans et plus, nés en
  1950 et avant, décotent 6,9 et 2,6 %, et non les 8,3 et 3,6 % que la
  population prêtait aux générations d'avant 1950.
- *Les données*, certifiées (fcab957). `departs_generations.csv` gagne un
  quatrième tableau, `residence` (216 valeurs) : la génération selon qu'elle
  réside en France ou à l'étranger, sans le lieu de naissance que la feuille
  croise avec elle, l'effectif, la part, celle des carrières complètes et de
  chaque condition de liquidation. `conditions_selon_l_age_residents.csv`
  naît (330 valeurs) : pour chaque condition de liquidation et pour tous,
  l'effectif, l'âge moyen et la part de chaque tranche d'âge. Les deux
  récupérateurs les lisent (`drees_departs_generations.py`,
  `drees_caracteristiques_retraites.py`), et vérifient ce qu'ils lisent : les
  colonnes de la résidence redonnent la génération, les tranches de chaque
  condition font cent, les conditions comptent les retraités de l'ensemble.
  Le serveur de la DREES coupait, ce jour-là, la liste des pièces jointes du
  jeu après quinze secondes, à chaque essai : les quatre classeurs se sont
  pris à leur adresse directe, et le `main()` des deux récupérateurs a tourné
  sur eux, leur téléchargement seul remplacé. La vérification redonne à
  l'identique toutes les séries que ces classeurs certifiaient déjà.
- *La version* (`DECOTE_DES_RESIDENTS`, `decotes_selon_l_age`,
  `decotes_des_tranches`, 0386bb4). Les nés en 1950 et en 1953 prennent la
  part des seuls résidents ; avant 1950, chaque génération celle de la tranche
  d'âge du stock des résidents de 2020 où elle tombe, la tranche des nés de
  1946 à 1950 sans les nés en 1950, qui ont la leur. Elle ne porte pas de
  numéro : trois sessions de la vague en prenaient un le même jour, la trente
  et unième, la trente-deuxième et la trente-troisième. Deux conventions : une
  tranche au 31 décembre 2020 compte les nés en 2020 moins ses âges, et sa
  part est celle de ses survivants de 2020 ; la tranche des nés de 1946 à 1950
  se prend sans ceux de 1950, chaque génération pesée de son effectif INSEE
  de 2020.
- *Les tests.* Des données : `test_departs_generations.py`, le lecteur de la
  résidence, et le fichier certifié, qui redonne ce que les classeurs
  impriment et compte la génération entière ; un fichier neuf,
  `test_conditions_selon_l_age.py`, le lecteur de l'âge, son refus d'une
  condition dont les tranches ne font pas cent, et le fichier certifié, dont les décotés redonnent la part
  des quintiles des résidents, 8,8 et 4,5 %. De la population
  (`test_grille_large.py`) : la part de chaque génération, refaite à la main
  des fichiers certifiés, avec et sans la version. Le test de la
  vingt-neuvième version la tient seule, sans celle-ci ; celui de la
  trentième s'étend aux nés de 1923 à 1927 et de 1938 à 1942, dont les
  départs avec décote pèsent la part de leur tranche. Vus rouges faute des
  fichiers, puis de la version ; `grille_large.py` avait déjà une
  `parts_des_tranches`, que la première écriture masquait, et que les tests
  de la population ont trouvée.
- *La mesure.* Une simulation, quatre pesées : la version ne change aucune
  carrière, et la population, simulée une fois sur l'arbre figé de bbf267e —
  avec la trente et unième et la trente-deuxième version, sans les suivantes
  —, sous `CALCULS_SANS_MEMOIRE=1`, se pèse sous les parts d'avant la version
  (« avant »), sous les seules parts des résidents de 1950 et de 1953, la part
  d'avant 1950 refaite comme avant (« résidents »), sous une seule part
  d'avant 1950, celle des résidents de 70 ans et plus moins les nés en 1950
  (« unique »), et sous celles de la version (« après ») ; les proratisations
  et les conditions de départ de chaque couple se calculent une fois pour les
  quatre (un pilote hors du dépôt, qui appelle les fonctions de
  `grille_large.py` et de `controle_eacr.py`, et compte de plus la décote du
  stock de 2020 par tranche d'âge). Le code du dépôt redonne exactement les
  parts de la dernière pesée, et, sans la version, celles de la première. Sur
  trois cœurs, 16 734 cas types, 468 024 couples : 212 minutes, dont 165 de
  simulation et 38 pour la première pesée ; 5 Go au plus, vus de `free`.
- *Ce qu'elle trouve*, d'abord la décote du stock de 2020 par tranche d'âge,
  contre les résidents de l'EIR :

  | tranche d'âge en 2020 | femmes, EIR | avant | après | hommes, EIR | avant | après |
  |---|---|---|---|---|---|---|
  | 50 à 59 ans | 18,4 | 51,9 | 51,9 | 5,7 | 44,9 | 44,9 |
  | 60 à 64 ans | 11,5 | 10,3 | 10,2 | 6,7 | 8,9 | 8,6 |
  | 65 à 69 ans | 12,1 | 11,9 | 11,5 | 7,5 | 9,2 | 8,3 |
  | 70 à 74 ans | 7,4 | 8,2 | 7,3 | 3,9 | 4,4 | 4,2 |
  | 75 à 79 ans | 4,6 | 8,2 | 4,5 | 1,9 | 3,9 | 2,0 |
  | 80 à 84 ans | 6,3 | 8,1 | 6,2 | 1,5 | 3,9 | 1,6 |
  | 85 ans et plus | 8,8 | 7,7 | 8,1 | 1,8 | 3,8 | 2,0 |
  | tous | 8,8 | 9,6 | 8,6 | 4,5 | 7,1 | 6,0 |

  Les retraités de 50 à 59 ans pèsent 0,7 % des femmes du stock et 2,9 % des
  hommes (EIR 1,0 et 1,8). Puis le reste de la mesure, contre l'EIR, les résidents
  entre parenthèses, et contre l'EACR :

  | | EIR, EACR | avant | après |
  |---|---|---|---|
  | femmes de 1950, décote | 7,9 (7,5) | 8,1 | 7,7 |
  | hommes de 1950, décote | 5,6 (4,5) | 6,1 | 4,9 |
  | femmes de la grille 1955, décote, contre les nées en 1953 | 12,5 (11,9) | 12,8 | 12,4 |
  | hommes de la grille 1955, décote | 8,7 (7,7) | 10,7 | 10,0 |
  | premier quintile des femmes, décote | 17,5 | 23,3 | 20,8 |
  | premier quintile des hommes, décote | 13,6 | 15,7 | 12,6 |
  | retraités du régime général en 2024, décote | 9,4 | 11,4 | 10,3 |
  | liquidants du régime général de 2024, décote | 13,4 | 16,7 | 16,6 |
  | pension moyenne des femmes en 2020, € par mois | 1 177 | 1 325 | 1 328 |
  | premier décile des femmes | 283 | 404 | 408 |
  | pension moyenne des hommes en 2020 | 1 957 | 1 815 | 1 819 |

  Les deux autres pesées : la part unique donne au stock le même total, 8,7 et
  6,1 %, mais 6,8 % de décotées de 75 à 79 ans (4,6) et 6,4 % de 85 ans et plus
  (8,8) ; les seules parts des résidents de 1950 et de 1953, la part d'avant
  1950 refaite comme avant, la relèvent, 8,5 et 4,0 %, et le stock reste à 9,6
  et 7,0 %.
- *Ce que cela dit.*
  - Le stock de 2020 rejoint l'EIR chez les femmes, 8,6 % pour 8,8, chaque
    tranche d'avant 1950 décotant comme la sienne à un dixième près, sauf les
    plus vieilles, 8,1 % pour 8,8 : les générations simulées de 1915 à 1930,
    qui partent avec 8,8 % de décotées, n'en gardent en 2020 que 6,3 à 8,1 %,
    de moins en moins à mesure qu'elles vieillissent ; les hommes du même âge
    en gardent un peu plus que leur part, 2,0 % pour 1,8. Le 25 octobre, ce
    stock décotait 10,5 % ; les versions poussées depuis, dont la trente et
    unième et la trente-deuxième, l'ont mené à 9,6, celle-ci à 8,6.
  - Les hommes s'en approchent, 6,0 % pour 4,5, et non 7,1 ; leurs tranches
    d'avant 1950 rejoignent les leurs. Ce qui reste tient d'abord aux
    retraités de 50 à 59 ans : les seuls que la population fasse décoter avant
    l'âge légal sont les agents des IEG et de la conduite, qui partent à
    l'ouverture de leur statut et y décotent tous depuis la génération 1960 ou
    1965 (`avec_decote`) ; les hommes de cet âge pèsent 2,9 % du stock et
    décotent pour 45 %, quand l'EIR compte 1,8 % de ses résidents à cet âge, et
    5,7 % de décotés parmi eux : 1,2 point des 1,5 d'écart. Puis aux hommes de
    60 à 69 ans, 8,6 et 8,3 % pour 6,7 et 7,5.
  - La part unique, celle des 70 ans et plus, aurait donné le même total ;
    les tranches le répartissent comme l'EIR. Le résidu de la vingt-neuvième
    version, lui, prenait aux générations d'avant 1950 ce que les autres
    décotaient en moins : les parts des résidents de 1950 et de 1953, plus
    basses, l'auraient relevé.
  - Les générations que l'EIR suit décotent comme leurs résidents : 7,7 % des
    femmes de 1950 (7,5), 4,9 % des hommes (4,5), 12,4 % des femmes de la
    grille 1955 (11,9) ; les hommes de la grille 1955 restent au-delà, 10,0 %
    pour 7,7, la génération portant la part des nés en 1955, 9,2 %, jugée sur
    celle des nés en 1953.
  - Le premier quintile s'approche de l'EIR, 20,8 % des femmes pour 17,5, et
    12,6 % des hommes pour 13,6 ; le régime général de 2024 aussi, 10,3 % de
    ses retraités pour 9,4. Le flux de 2024 ne bouge pas, 16,6 % pour 13,4 :
    ses générations, de 1957 à 1964, gardent à peu près la leur.
  - La distribution de 2020 en dit peu : trois euros de plus aux femmes,
    quatre aux hommes, le premier décile des femmes à 408 € et non 404 (283).
  - La version reste : les parts de chaque génération sont celles de ses
    résidents, et celles d'avant 1950 sont lues, non plus déduites.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les carrières, toutes, leurs
  cas types et leurs poids de base ; la grille du coût, qui garde la part de
  tous les nés en 1953 (`facteurs_depense`) ; le registre, dont aucun point
  « 138.14 » ne nomme la décote. Aucune règle du scénario 1 ne change : pas
  d'entrée au journal de veille.

**Ce qui reste**, de ce point (le reste de l'étape est au bloc « Reprise » de
sa note) :

1. *Les agents des IEG et de la conduite nés depuis 1960*, partis avant 60
   ans, qui décotent tous : 1,2 point de la décote des hommes du stock de
   2020, et la moitié des femmes de 50 à 59 ans du stock, décotées (EIR
   18,4 %). Leur part dans le stock, 2,9 % des hommes pour 1,8 % des résidents
   de 50 à 59 ans, et leur décote, à juger sur ce que l'EIR dit des régimes
   spéciaux.
2. *Les plus vieilles* : leur génération part avec la part de leur tranche,
   8,8 %, et ses survivantes de 2020 n'en gardent que 6,3 % (génération
   simulée 1915) à 8,1 % (1930), quand les hommes gardent la leur. La survie
   propre de chaque cas type, ou la décote que la mesure reconnaît aux
   départs d'avant 1983 (`avec_decote`), à démêler ; la part d'une tranche
   pourrait se prendre à son départ plutôt qu'en 2020.
3. *Les hommes de 60 à 69 ans*, 8,6 et 8,3 % pour 6,7 et 7,5, et ceux de la
   grille 1955 contre les nés en 1953 : la part des nés de 1954 à 1959 suit
   la droite qui mène des résidents de 1953 aux liquidants de la Cnav de 2024,
   tous lieux de résidence, l'EACR ne les séparant pas.
4. *La mesure des départs* (`confronter_departs`) juge toujours la
   population, qui ne compte que des résidents, sur toute la génération : le
   tableau `residence` permettrait de la juger sur ses résidents pour la
   décote, non pour les âges et les places, que l'EIR ne croise pas avec la
   résidence.
5. *La grille du coût* prend la décote de toute la génération 1953, résidents
   ou non (`facteurs_depense.part_decotee_des_l_age_legal`) : 10,6 % des nés
   en 1953 sont partis avec une décote, 9,9 % de leurs résidents ; au modèle,
   s'il le faut.
