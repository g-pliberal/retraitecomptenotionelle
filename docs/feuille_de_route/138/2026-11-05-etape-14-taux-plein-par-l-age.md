# Étape 14 : le taux plein par l'âge — à la même génération, la population y part comme l'EIR, sauf les hommes de 1953 ; rien ne change

**Le 5 novembre 2026 : la population fait partir au taux plein par l'âge,
à l'âge d'annulation de la décote de leur génération, 15,15 % des femmes et
7,30 % des hommes nés en 1950, 11,10 et 4,47 % de ceux nés en 1953 ; l'EIR,
aux mêmes générations, en voit partir 15,47 et 6,88 %, 11,63 et 5,78 %
à l'âge révolu de ce taux plein et après. L'âge est le bon, à l'année
révolue : 65 ans en 1950, 66 ans et 2 mois en 1953, 67 ans ensuite. Deux
écarts : les hommes de 1953, à qui manque 1,31 point ; et le mois du départ,
la population faisant partir tous ces départs à l'âge d'annulation même,
quand l'EIR en range un sur cinq chez les femmes nées en 1953, trois sur dix
chez les hommes, après lui. La génération 1955, que la mesure du dépôt juge
sur les nés en 1953, n'en a que 6,90 et 3,01 % ; aucune source ne dit ce
qu'ont les générations d'après 1953. Aucune source ne donne de quoi corriger
sans défaire un autre calage : aucun code, aucune donnée, aucun test ne
change.**

Demande : la vague 9, lancée par la session d'orchestration le 5 novembre
2026 : un point de l'étape 14, et lui seul, la mesure d'abord — le taux plein
par l'âge, les départs à l'âge où le taux plein vient de l'âge seul, hors
invalides et inaptes. Méthode, celle de la trente-huitième version
(`2026-11-05-etape-14-inaptes.md`).

- *Les sources*, ouvertes le 5 novembre 2026, deux pièces jointes du jeu de la
  DREES `3013_donnees-statistiques-sur-les-caracteristiques-des-retraites`
  (https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog/datasets/3013_donnees-statistiques-sur-les-caracteristiques-des-retraites/attachments/…),
  absentes du dépôt (`data/brut/` ne garde que son `.gitkeep`) :
  « Caractéristiques des retraités nés en 1953 (EIR 2020) »
  (`caracteristiques_des_retraites_nes_en_1953_eir_2020_xlsx`, prise par
  `curl`, 195 574 octets, SHA-256
  `d5e8b8776768e31a3a8a0490bf749fc6615d12a8d25716e57a658dd16f94c5e0`) et
  « … nés en 1950 (EIR 2016) »
  (`caracteristiques_des_retraites_nes_en_1950_eir_2016_xlsx`, `curl` coupé,
  prise par la lecture web, 194 522 octets, SHA-256
  `59f76598591d20cb4704659a65ba30ce687ca8cb0a733198a3182c6bbaef61a8`) : les
  empreintes de la note des inaptes. Lues cellule par cellule
  (`scripts/fetch/lecture_xlsx.py`, le lecteur et sa sortie dans la mesure) ;
  chaque valeur est celle de `departs_generations.csv`. Les lignes vont par
  trois, « Ensemble », « Femme », « Homme ».
  Classeur de 1953 :
  - « ÂgeLiq », colonnes D (avant l'âge légal), E (à lui), F (entre lui et
    l'âge d'annulation de la décote), G (à ce dernier), H (après), I
    (ensemble) : ligne 6, « Part parmi l'ensemble des retraités (en %) »,
    femmes, 21,7, 37,5, 26,7, 10,8, 3,3 ; ligne 7, hommes, 40,8, 24,4, 26,4,
    5,5, 2,8 ; ligne 294, « Part de départ au taux plein par l'âge (en %) »,
    femmes, 1,8, 0,0, 0,9, 86,3, 67,0, 12,2 ; ligne 295, hommes, 3,7, 0,0,
    0,7, 74,5, 57,7, 7,4 ;
  - « ÂgeLiq_Détails », colonnes D (avant 60 ans), E à K (60 à 66 ans), L
    (67 ans et plus), M (ensemble) : ligne 6, femmes, 10,2, 9,4, 42,1, 8,9,
    5,0, 5,7, 2,9, 14,9, 0,8 ; ligne 7, hommes, 20,2, 17,5, 29,7, 8,2, 5,2,
    6,1, 3,1, 9,1, 0,8 ; ligne 294, femmes, 3,2, 0,6, 0,1, 0,1, 0,1, 1,0,
    2,6, 74,8, 61,1, 12,2 ; ligne 295, hommes, 7,3, 0,2, 0,0, 0,1, 0,2, 0,9,
    1,8, 59,1, 49,8, 7,4 ;
  - « CondLiquidation », colonne K (« Taux plein par âge ») : K6, femmes,
    12,2 % de la génération ; K7, hommes, 7,4.

  Classeur de 1950, les mêmes intitulés aux lignes 6, 7, 291 et 292 :
  « ÂgeLiq », D à H, femmes, 13,0, 44,4, 22,4, 15,3, 4,9 et 10,4, 0,7, 2,1,
  88,5, 64,4 ; hommes, 27,6, 35,3, 25,4, 7,3, 4,4 et 6,6, 0,3, 1,3, 72,9,
  51,8 ; « ÂgeLiq_Détails », D (avant 60 ans) à K (66 ans, le dernier âge),
  femmes, 13,0, 50,5, 6,5, 3,8, 3,1, 5,0, 16,2, 1,9 et 10,4, 0,8, 1,5, 1,9,
  3,6, 26,7, 88,7, 58,0 ; hommes, 27,6, 41,3, 7,1, 4,8, 3,8, 5,4, 8,3, 1,7
  et 6,6, 0,3, 0,8, 0,7, 3,7, 13,8, 73,1, 47,6 ; « CondLiquidation », K6 et
  K7, 18,8 et 9,8.

  Le jeu ne porte aucune génération d'après 1953 : ses onze pièces jointes,
  listées le 5 novembre par la lecture web, ne nomment que les nés en 1950
  et en 1953.
- *La mesure* (`docs/mesures/138/2026-11-05-etape-14-taux-plein-par-l-age.txt`,
  ses deux scripts et leurs sorties), sur `main` à 85599c6 : toutes les
  variantes de la population, cinq générations, chacune aux poids de
  retraités d'une année (2016, 2020, 2022, 2027, 2032), multipliés par la
  part que la génération donne à chaque variante, simulées au portage, tous
  leurs départs comptés. Un départ est au taux plein par l'âge quand il se
  prend à l'âge d'annulation de la décote, à un mois et demi près, ou après,
  sans la durée requise (`condition_au_depart`) ; les jumelles inaptes n'y
  sont jamais.

  | génération | femmes | hommes | âge de ces départs |
  |---|---|---|---|
  | 1950 | 15,15 | 7,30 | 65 ans, tous |
  | 1953 | 11,10 | 4,47 | 66 ans et 2 mois, tous |
  | 1955 | 6,90 | 3,01 | 67 ans, tous |
  | 1960 | 6,38 | 1,95 | 67 ans, tous |
  | 1965 | 9,54 | 6,02 | 67 ans, tous |

  Ces âges sont ceux de `age_annulation_decote.csv` (65,00 jusqu'en 1951,
  66,17 en 1953, 67,00 dès 1955). Aucun de ces départs ne se prend après
  l'âge d'annulation : la population n'y fait partir que des surcotes, 1,20
  et 1,69 % des départs des nés en 1950, aucun en 1953.
- *L'EIR, et le calcul posé à la main.* Le classeur ne croise pas l'âge au
  mois avec la condition. Deux lectures :
  - *par l'âge révolu*, le taux plein par l'âge à l'âge révolu de
    l'annulation et après — la part de l'âge, fois celle du taux plein par
    l'âge parmi ses départs, sur cent. 1950, femmes : J6 × J291 = 16,2 ×
    88,7 = 1 436,94 à 65 ans, K6 × K291 = 1,9 × 58,0 = 110,20 à 66 ans,
    1 547,14, soit **15,47 %** ; hommes : 8,3 × 73,1 = 606,73 et 1,7 × 47,6
    = 80,92, 687,65, **6,88 %**. 1953, femmes : K6 × K294 = 14,9 × 74,8 =
    1 114,52 à 66 ans, L6 × L294 = 0,8 × 61,1 = 48,88 à 67 ans et plus,
    1 163,40, **11,63 %** ; hommes : 9,1 × 59,1 = 537,81 et 0,8 × 49,8 =
    39,84, 577,65, **5,78 %**. La colonne des 66 ans compte aussi ceux
    partis à 66 ans et 0 ou 1 mois, avant l'annulation ; le classeur ne les
    sépare pas ;
  - *par la place*, à l'âge d'annulation et après. 1953, femmes : G6 × G294
    = 10,8 × 86,3 = 932,04, H6 × H294 = 3,3 × 67,0 = 221,10, 1 153,14,
    **11,53 %**, dont 221,10 / 1 153,14 = **19,2 %** après l'annulation ;
    hommes : 5,5 × 74,5 = 409,75 et 2,8 × 57,7 = 161,56, 571,31, **5,71 %**,
    dont 161,56 / 571,31 = **28,3 %** après. 1950, femmes : 15,3 × 88,5 =
    1 354,05 et 4,9 × 64,4 = 315,56, 1 669,61, 16,70 % ; hommes : 7,3 × 72,9
    = 532,17 et 4,4 × 51,8 = 227,92, 760,09, 7,60 %. Les places se comptent
    aux âges du régime principal (en-tête de `departs_generations.csv`) : en
    1950, les femmes de 60 à 64 ans au taux plein par l'âge font 40,40 +
    9,75 + 7,22 + 11,16 + 133,50 = 202,03 (E6 × E291 … I6 × I291), dont les
    places de l'âge légal et d'entre les deux âges ne gardent que 44,4 × 0,7
    = 31,08 et 22,4 × 2,1 = 47,04 : 123,91, soit 1,24 point, sont rangés à
    l'annulation ou après par un régime qui annule la décote avant 65 ans.
    La lecture par l'âge révolu est celle du point : 65 à 67 ans.

  Ce que l'EIR range aussi au taux plein par l'âge, et que le point ne
  compte pas : avant l'âge légal, 21,7 × 1,8 = 39,06, soit 0,39 point des
  départs des femmes nées en 1953, et 40,8 × 3,7 = 150,96, soit 1,51 point
  de ceux des hommes (20,2 × 7,3 = 147,46 avant 60 ans, ÂgeLiq_Détails D7 ×
  D295) : des départs que la population fait prendre au taux plein d'un
  statut, et range au taux plein « autrement ». D'où les 12,2 et 7,4 % de
  « CondLiquidation », au-dessus des deux lectures.

  | | EIR, l'âge révolu et après | EIR, la place et après | population | écart à l'âge révolu |
  |---|---|---|---|---|
  | femmes nées en 1950 | 15,47 | 16,70 | 15,15 | −0,32 |
  | hommes nés en 1950 | 6,88 | 7,60 | 7,30 | +0,42 |
  | femmes nées en 1953 | 11,63 | 11,53 | 11,10 | −0,53 |
  | hommes nés en 1953 | 5,78 | 5,71 | 4,47 | −1,31 |
  | femmes, génération 1955 jugée sur 1953 | 11,63 | 11,53 | 6,90 | −4,73 |
  | hommes, génération 1955 jugée sur 1953 | 5,78 | 5,71 | 3,01 | −2,77 |

  L'âge, à l'année révolue : les départs de la première lecture se prennent
  à l'âge révolu de l'annulation pour 1 436,94 / 1 547,14 = 92,9 % des
  femmes nées en 1950 et 606,73 / 687,65 = 88,2 % des hommes, pour
  1 114,52 / 1 163,40 = 95,8 % des femmes nées en 1953 et 537,81 / 577,65 =
  93,1 % des hommes ; le reste, l'année d'après. La population les fait
  tous partir à l'âge d'annulation même.
- *Ce que cela dit.*
  - Aux générations que l'EIR voit, et que la population simule comme
    telles, la part des départs au taux plein par l'âge est celle de l'EIR à
    un demi-point près, sauf chez les hommes de 1953 : 4,47 % pour 5,78. De
    1950 à 1953, elle baisse dans la population de 2,83 points chez les
    hommes (7,30 à 4,47), de 1,10 dans l'EIR (6,88 à 5,78) ; chez les femmes,
    de 4,05 et de 3,84. Qui y part, chez les hommes de 1953 : les carrières
    de trente à quarante ans du régime général pour 58,3 % de ces départs,
    les libéraux de quarante années et plus pour 22,4 %. La cause de l'écart
    n'est pas mesurée ici.
  - L'âge est celui de la loi de chaque génération, à l'année près ; au mois
    près, non : l'EIR range après l'âge d'annulation 19,2 % des femmes et
    28,3 % des hommes nés en 1953 partis au taux plein par l'âge, la
    population aucun. Le classeur ne dit pas de combien de mois.
  - La génération 1955, que la mesure du dépôt juge sur les nés en 1953
    (`GENERATIONS_DES_DEPARTS`), y part pour 6,90 et 3,01 %, loin des 11,63
    et 5,78 % ; c'est le « juge de 1955 », déjà au propriétaire. Chez les
    femmes, ce qu'elle perd sur la génération 1953 de la population, 4,20
    points, tient presque tout aux carrières de vingt à trente ans du régime
    général : 37,6 % de ces départs en 1953, soit 4,17 points, 7,6 % en 1955,
    0,52. Aucune source ouverte ne dit la part des générations d'après 1953.
  - Pourquoi rien ne se corrige. La jumelle du taux plein d'une carrière
    incomplète, celle qui attend l'âge d'annulation, n'a pas de part à
    elle : elle garde ce que lui laissent la jumelle qui décote, l'inapte et,
    chez les femmes, celle qui complète sa durée, chacune calée sur sa propre
    case de l'EIR. Rendre aux hommes de 1953 leur 1,31 point demanderait de
    l'ôter à l'une d'elles, ou d'avoir plus de carrières incomplètes
    d'hommes en 1953, ce que l'EIR ne donne pas par génération (sa « carrière
    complète » n'est pas la durée requise atteinte :
    `2026-11-05-etape-14-calage-de-la-duree-des-femmes.md`). Faire attendre
    après l'âge d'annulation une part de ces départs, la part se lit (19,2 et
    28,3 % en 1953), mais non l'attente, et elle ferait partir après 67 ans
    les générations nées depuis 1955 : c'est le point des départs après
    67 ans, que l'EACR mesure (table B, 68 ans et plus).
- *Ce qui ne bouge pas.* Aucun code, aucune donnée, aucun test : rien ne se
  remesure. La page, qui ne lit pas la population (action 157), la grille du
  coût (décision 11), les témoins, le paquet. Aucune règle du scénario 1 :
  pas d'entrée au journal de veille.

**Ce qui reste**, de ce point :

1. *Les départs après l'âge d'annulation* : 19,2 % des femmes et 28,3 % des
   hommes nés en 1953 partis au taux plein par l'âge, sans le mois ; à
   prendre avec les départs après 67 ans, qui en sont la suite dès la
   génération 1955.
2. *Les hommes de 1953* : 4,47 % au taux plein par l'âge pour 5,78 ; il
   faudrait d'abord décomposer, de 1950 à 1953, ce que chaque jumelle des
   carrières incomplètes d'hommes prend à celle du taux plein. Candidat.
3. *Les générations d'après 1953* : 6,90 et 3,01 % en 1955, 6,38 et 1,95 en
   1960, 9,54 et 6,02 en 1965, sans source ; il faudrait la part des départs
   au taux plein par l'âge d'une génération plus jeune, qu'aucune pièce du
   jeu de la DREES ne donne au 5 novembre.
4. *La mesure du dépôt* (`confronter_departs`) compare la classe du taux
   plein par l'âge de la population à tout le taux plein par l'âge de
   l'EIR, 12,30 % des femmes nées en 1953 et 7,47 % des hommes parmi les
   conditions connues (12,2 / 99,2 et 7,4 / 99,0), y compris les départs
   d'avant l'âge légal que la population range ailleurs, 1,51 point chez les
   hommes. Candidat, pour la mesure et non pour la population.
5. *Les libéraux de quarante années et plus* partent au taux plein par
   l'âge sans la durée requise : 22,4 % de ces départs chez les hommes de
   1953, 35,4 % en 1955, 60,8 % en 1960, 20,0 % en 1965. Candidat, non
   examiné.
