# Étape 14 : les corrections de la relecture R-I — la mesure de la surcote refaisable au dépôt, le régime général de 2024, les départs après 67 ans

**Le 3 novembre 2026 : la mesure de la trente-septième version se refait
désormais au dépôt, par `scripts/mesurer_surcote.py` (3ddae71), une commande et
deux tests ; la relancer a dépassé les deux heures permises aux tâches de fond :
la simulation de la population est faite, les pesées non, et ses chiffres
restent à écrire. Les départs après 67 ans n'expliquent pas l'essentiel de
l'écart à la Cnav : au seul taux que l'EIR donne, 1,7 point sur 7,4 à 8,0, et
6,5 points au plus si tous surcotaient. Les 10,9 % de la file I et les 11,49 %
de R-I comptent différemment ses liquidants du régime général, à la condition
de leur départ et au drapeau des jumelles ; le bon chiffre est celui de la
condition, qu'aucune mesure du dépôt n'a encore refait. Trois points de R-I
déclarés au code (bd1c251) ; aucun paramètre ne change.**

Demande : la cinquième vague, lancée le 3 novembre 2026 par la session
d'orchestration, file I-bis : corriger la trente-septième version (624ec9f,
730a6bb ; note `2026-11-03-etape-14-surcote-du-salariat-selon-la-generation.md`)
d'après sa relecture indépendante R-I (490cb7a ; note
`2026-11-03-relecture-surcote-du-salariat.md`) : ses deux écarts moyens (points
4.4 et 5) et ses écarts faibles (point 2, la génération 1955 de la phrase au
propriétaire, points 4.1, 4.2 et 4.5). Ni paramètre de calage ni règle ne
change ; la part des départs avec décote des générations nées depuis 1960
reste à la session suivante de la file I.

Ouverts pendant la session, rien de mémoire : le jaune pensions annexé au PLF
2027, le PDF (branche `jaune-2027` du dépôt, `34465.pdf`, SHA-256
`73dd4a66051cd71bdf2c77eb5345a34f99f862330f0f20164c930492be2dbaf5`, celle de
`data/sources.yaml`), p. 182 (tableau 103 et sa note 154) et p. 210-211
(tableau B-3) ; l'EIR des nés en 1950 et en 1953, fichier certifié
`data/reference/macro/departs_generations.csv` ; les tables H, B et C de
l'EACR du 26 mai 2026, témoin `tests/temoins/drees_eacr_tables_2026.json`
(source `drees_eacr_tables` de `data/sources.yaml`). Les classeurs d'origine de
l'EIR et de l'EACR n'ont pas été rouverts : le fichier certifié et le témoin
sont ceux que `scripts/verifier_donnees.py` recontrôle.

## La mesure, refaisable au dépôt (R-I, point 4.4)

- *Le script* (`scripts/mesurer_surcote.py`, 3ddae71 ; son en-tête complété
  en bd1c251). Il fait ce que la note de la file I décrit de son pilote :
  la population construite comme `grille_large.mesurer` la construit, la
  constante `SURCOTE_SELON_LA_GENERATION` allumée puis éteinte, les deux
  grilles vérifiées identiques — mêmes cas types, mêmes poids —, simulée une
  fois (`en_tetes`, couples allégés), puis deux pesées de ses parts des
  générations. Chacune donne : les départs des générations 1950 et 1955
  contre l'EIR (`grille_large.departs`, le juge de la note) ; l'État et la
  CNRACL, leurs retraités de 2024 et leurs liquidants de chaque année de 2020
  à 2025 ; le régime général (le groupe `regime_general`, celui de
  `scripts/controle_eacr.py`), ses liquidants et ses retraités de 2024, la
  décote de ses liquidants, ses liquidants âge par âge ; les retraités de
  2020 sexe par sexe, de 70 à 74 ans, et les fonctionnaires civils parmi ceux
  qui ont surcoté ; l'âge des liquidants de 2024 contre la table C ; la
  distribution de 2020 contre l'EIR. Les sources en regard sont lues au
  témoin de l'EACR (tables H, B et C) et au fichier certifié de l'EIR.
- *Deux façons de compter une surcote*, que le script donne l'une et l'autre
  pour les liquidants, avec leur croisement : au drapeau, la jumelle qui
  surcote d'une génération simulée qui atteint son âge légal depuis 2004
  (`CasTypeLarge._attente_du_depart`, la règle même de son départ) ; à la
  condition de son départ (`condition_au_depart`), parmi les conditions qui
  se lisent, la part des autres dite à part.
- *Les tests* (`tests/test_grille_large.py`, vus rouges faute du script).
  `test_la_mesure_de_la_surcote_compte_les_jumelles_et_les_conditions` pose
  à la main un lot de cohortes et ce que chaque part en vaut — l'État de
  2024, 3 surcotés au drapeau sur 19 retraités, la jumelle née en 1940 non
  comptée (1940 + 60 < 2004) ; ses liquidants, 2 sur 13 au drapeau, 2 sur 8
  à la condition, 5 inconnus ; le régime général, 3 sur 15 au drapeau, 7 sur
  15 à la condition, 5 décotés ; les retraités de 2020, sexe par sexe.
  `test_la_mesure_de_la_surcote_se_refait_sur_un_cas_court` lance le script
  sur la grille de la page (`--grille reference`, 18 cas types, une minute) :
  aucune jumelle, d'où une part nulle au drapeau, deux pesées égales, et les
  sources posées à la main — 122 368 des 648 346 liquidants de la Cnav en
  2024 partis avec une surcote, 1 658 347 de ses 14 744 736 retraités,
  370 626 des 1 641 380 retraités civils de l'État (table H), 47 732
  liquidants de la Cnav de 68 ans et plus (table B), 14,3 / 99,1 de l'EIR.
- *La commande*, depuis la racine du dépôt :
  `python scripts/mesurer_surcote.py --processus 4 --json mesure.json`.
- *Le passage de ce jour, arrêté.* Lancée sur un arbre figé, le worktree de
  8c93f72 (490cb7a et le script ; le même que 3ddae71 sur `main`, aux deux
  docstrings de bd1c251 près), après une chauffe de la mémoire des calculs
  depuis 15 h 04 sur 490cb7a (`python scripts/controle_eacr.py --population
  --processus 4`, arrêtée à 15 h 31, le script faisant tout ce qu'elle
  faisait), la mesure est partie à 15 h 34 ; son dernier morceau de
  simulation est gardé à 17 h 22 (233 morceaux sous l'empreinte du modèle de
  490cb7a, ceux des tests compris) ; elle calculait les poids de la page
  quand la limite de deux heures des tâches de fond l'a arrêtée, à 17 h 34,
  avant toute pesée. La simulation a donc pris près de deux heures et quart
  sur quatre cœurs, chauffe comprise, la suite rapide et
  `test_grille_large.py` tournant à côté une demi-heure ; il restait les
  poids (14 minutes à la file I) et les pesées (4 à 8 minutes chacune). Ses
  chiffres ne sont donc pas écrits ici : ceux de la trente-septième version
  restent ceux de la note de la file I, que R-I a refaits au dixième par un
  pilote à lui (sa note, point 2), hors du dépôt l'un et l'autre. Relancée
  dans ce conteneur, sur le même modèle, la mesure reprendrait la simulation
  gardée ; sur `main`, où d'autres files ont changé depuis des données que
  le modèle lit (`data/reference/regles/retraite_proportionnelle_msa.yaml`,
  le paquet), elle la referait.

## Le régime général de 2024 : 10,9 % ou 11,49 %

La note de la file I compte « le stock de 2020 par tranche d'âge et les
retraités du régime général de 2024 […] au drapeau des jumelles […] ; le
reste, à la condition de départ de chaque couple (`condition_au_depart`) » :
ses liquidants du régime général de 2024, 10,9 % partis avec une surcote, sont
comptés à la condition. R-I tient pour surcotée toute jumelle qui surcote d'une
génération qui atteint son âge légal depuis 2004, liquidants compris (sa note,
point 2) : 11,49 %. Les stocks, comptés de même des deux côtés, s'accordent
(retraités du régime général de 2024 : 7,8 et 7,81 % ; retraitées de 2020 :
7,7 et 7,74 %), et les liquidants de l'État aussi (50,6 et 50,64 % en 2024).

Le code dit pourquoi le régime général s'en écarte, et l'État non.
`CasTypeLarge.age_liquidation_pour` fait partir la jumelle du salariat à l'âge
que le pilote fixe, son taux plein, ou à l'âge légal plus son attente, au plus
tard des deux : quand son taux plein vient après, elle part à son taux plein,
sans surcote, et le drapeau la compte quand même. La jumelle du fonctionnaire
(`depuis_la_surcote`) attend, elle, depuis le premier âge où le modèle lui
sert une surcote : elle surcote dès que le modèle lui en sert une. Et
`condition_au_depart` range d'abord le départ en carrière longue et avec
décote, et compte une surcote à toute carrière qui part après l'âge légal et
après son taux plein, jumelle ou non. Le bon chiffre est celui de la
condition : la table H compte les pensions liquidées avec une surcote, non
les départs qui l'attendaient. Mais il n'est pas refait : les 10,9 % sont ceux
du pilote de la file I, et le passage arrêté du script n'a pas donné le sien,
ni le croisement (`croisement_2024`) qui dirait combien de jumelles partent
sans surcote et combien de carrières surcotent sans être jumelles. Que l'écart
de 0,6 point tienne tout entier à cette façon de compter, et non aussi au
champ — la note de la file I ne dit pas quelles carrières elle range au
régime général —, reste à établir par la mesure.

## Les départs après 67 ans : ce qu'ils expliquent de l'écart à la Cnav

La file I a dit au propriétaire que les nouveaux retraités du privé de 2024
surcotent trop peu dans le modèle « surtout parce que personne n'y part après
67 ans ». R-I (point 5) le trouve non établi, avec une borne : « au taux des
nés en 1953 partis à 67 ans et plus (34,6 %, EIR), ce serait quelque 2,5
points ». Refait dans les sources :

- *La Cnav*, table H (caisse 0015, flux de 2024, ensemble) : 439 202 départs
  au taux plein, 86 776 avec une décote, 122 368 avec une surcote, 648 346 en
  tout ; la surcote, R = 122 368 / 648 346 = 18,874 %.
- *Ses liquidants de 68 ans et plus*, table B (caisse 0015, 2024) : 20 350 à
  68 ans, 6 969 à 69, 4 832 à 70, 15 581 au-delà de 70 ; 47 732, soit
  a = 47 732 / 648 346 = 7,362 % ; tous les âges de la table somment les
  648 346 de sa ligne « Ensemble ». À 67 ans, 60 530 (9,34 %). Le témoin ne
  dit pas à quelle date de l'année l'âge se compte.
- *L'EIR* (`departs_generations.csv`, lignes 1044 à 1072) : les nés en 1953
  partis à « 67 ans et plus », 0,8 % des départs de leur génération (6 000
  sur 757 000), dont s = 34,6 % avec une surcote (29,1 % des femmes, 40,6 %
  des hommes). L'enquête voit cette génération en 2020, à 67 ans : ses
  « 67 ans et plus » sont des départs à 67 ans, aucun plus tard. C'est le seul
  taux de surcote des départs tardifs que les sources ouvertes donnent.
- *Le modèle* : m = 10,9 % de ses liquidants du régime général de 2024
  surcotent selon la note de la file I (à la condition), 11,49 % selon R-I (au
  drapeau) ; il n'a de départ qu'à 67 ans et moins (les attentes des nés en
  1953 s'arrêtent à « 67 ans et plus », pris pour 67 ans), convention déclarée
  par la file I, que le passage arrêté du script n'a pas mesurée âge par âge.

Le calcul, posé à la main. Si la population faisait partir après 67 ans la
même part de ses liquidants que la Cnav, a, au taux s, sans rien changer au
taux m de ses départs de 67 ans et moins, sa part de liquidants avec surcote
serait (1 − a) × m + a × s, soit a × (s − m) de plus — et non a × s : ces
départs tardifs prendraient la place d'autant de départs de 67 ans et moins,
qui surcotent déjà pour m. Les 2,5 points de R-I sont a × s = 7,362 % × 34,6 %
= 2,55 points : la part des liquidants de la Cnav qui auraient 68 ans et plus
et surcoteraient, non ce qu'ils retranchent de l'écart.

| | m = 10,9 % (file I) | m = 11,49 % (R-I) |
|---|---|---|
| écart à la Cnav, R − m | 18,874 − 10,9 = 7,97 points | 18,874 − 11,49 = 7,38 points |
| expliqué au taux de l'EIR, a × (34,6 − m) | 0,07362 × 23,70 = 1,74 point, 21,9 % | 0,07362 × 23,11 = 1,70 point, 23,0 % |
| reste sans explication | 6,23 points | 5,68 points |
| borne, tous surcotent, a × (100 − m) | 0,07362 × 89,10 = 6,56 points | 0,07362 × 88,51 = 6,52 points |
| reste, même alors | 1,41 point | 0,87 point |

Vu de la Cnav : si ses liquidants de 68 ans et plus surcotent pour 34,6 %,
ceux de 67 ans et moins surcotent pour (122 368 − 0,346 × 47 732) / (648 346
− 47 732) = 105 852,7 / 600 614 = 17,62 % ; pour 20,37 % si aucun des plus
âgés ne surcote, 12,43 % si tous surcotent. Le modèle, qui n'a que des départs
de 67 ans et moins, en est à 10,9 ou 11,5 % : à âges comparables, l'écart
reste de 6,1 à 6,7 points au taux de l'EIR.

**Ce que la phrase au propriétaire aurait dû dire** : les nouveaux retraités du
privé de 2024 surcotent pour 11 % dans le modèle, 19 % à la Cnav ; l'absence de
départ après 67 ans en explique environ 1,7 point sur 7,4 à 8, au seul taux que
l'enquête donne pour les départs tardifs, et 6,5 points au plus si tous ces
départs surcotaient ; le reste, 5,7 à 6,2 points, les sources ouvertes ne
disent pas d'où il vient.

## La génération 1955, jugée sur les nés en 1953

L'EIR ne voit que les nés en 1950 (en 2016, à 66 ans) et les nés en 1953 (en
2020, à 67 ans) ; la grille simule ses générations de cinq en cinq ans. La
mesure juge donc la génération 1955 de la grille sur les nés en 1953
(`GENERATIONS_DES_DEPARTS = {1950: 1950, 1955: 1953}`, `scripts/grille_large.py`),
et la génération 1950 sur les nés en 1950. Partout où cette note, la note de
la file I et sa relecture écrivent un chiffre de la « génération 1955 », c'est
celui-là : celui de la grille, jugé sur l'enquête des nés en 1953, que personne
n'a menée sur les nés en 1955. Le script l'imprime en tête de son premier
tableau. La phrase de la file I au propriétaire, « les nés en 1950 et en 1955
retrouvent les chiffres de l'enquête (11 % et 14 %) », se dit juste ainsi : la
génération 1950 de la grille surcote pour 11,3 % de ses départs (11,28 %
refaits par R-I), quand l'EIR en voit 11,78 % des nés en 1950 (11,7 / 99,3,
parmi les conditions connues) ; la génération 1955 de la grille, jugée sur les
nés en 1953, pour 14,0 % (14,06 %), quand l'EIR en voit 14,43 % des nés en 1953
(14,3 / 99,1).

## Trois points déclarés

1. *La rupture de 2011-2012 du tableau 103* (R-I, point 4.1). Relu au PDF,
   p. 182 : le tableau 103 donne 28 % en 2011, 36 % en 2012, 31 % en 2013 ; sa
   note 154 : « En 2012, l'effectif de nouveaux retraités avait connu une
   forte baisse (-34 %), principalement liée au contrecoup des départs
   anticipés massifs pour parents de trois enfants de 2011 et à la montée en
   charge de la mesure d'âge. De ce fait, alors que l'effectif de surcotés se
   réduisait à 16 910 concernés contre 21 000 en 2011, la part des surcotés
   avait progressée. » La version prend la série telle quelle. La part du
   sédentaire de l'État, relue à `surcotes_des_fonctionnaires_selon_la_generation`
   (48,48 % en 2025, fois la part de l'année où la génération atteint son âge
   légal, sur 35 %) : né en 1951, à 60 ans, en 2011, 48,48 × 28 / 35 = 38,8 % ;
   en 1952, à 60 ans et 9 mois, en 2012,75, 48,48 × (36 − 5 × 0,75) / 35 =
   44,7 % ; en 1953, à 61 ans et 2 mois, en 2014,17, 48,48 × 31 / 35 = 42,9 % ;
   en 1954, 42,1 % ; en 1955, en 2017, 48,48 × 28 / 35 = 38,8 % ; en 1956,
   42,9 % ; en 1957, 44,3 %. La suite n'est pas monotone, et c'est la source
   qui le veut. Déclaré au code, au-dessus de `SURCOTES_DU_JAUNE_PAR_ANNEE`
   (bd1c251). *Poids : faible* : les nés en 1952 et 1953 portent le
   relèvement de 2012.
2. *La cible et le juge, deux chiffres de l'EIR* (R-I, point 4.2). Relus au
   fichier certifié : la cible de la version est la part des résidents en
   France, conditions inconnues comprises (tableau `residence`, colonne
   `france`, lignes 1530 et 1542 : 14,2 % des femmes et 14,4 % des hommes nés
   en 1953 ; 11,2 et 12,2 % des nés en 1950) ; le juge de la mesure
   (`confronter_departs`) prend toutes les résidences, parmi les conditions
   connues (tableau `condition`) : nées en 1953, 14,2 / 99,2 = 14,31 % ; nés
   en 1953, 14,5 / 99,0 = 14,65 % ; nées en 1950, 11,2 / 99,6 = 11,24 % ; nés
   en 1950, 12,2 / 99,2 = 12,30 %. Le juge passe la cible de 0,04 à 0,25
   point, que la version ne vise pas. Déclaré au code, sous
   `SURCOTE_SELON_LA_GENERATION` (bd1c251). *Poids : faible.*
3. *L'État, ses liquidants contre le jaune : deux champs* (R-I, point 4.5). La
   file I opposait aux liquidants civils de l'État du modèle, de 2020 à 2025,
   les seuls départs pour ancienneté de 2025 du jaune : tableau B-3, p. 210 et
   211 du PDF, colonne « Pensions civiles », « pour ancienneté », 41 812
   départs, « Part des pensions avec surcote » 42,7 % (16,5 % des 2 545
   départs pour motifs familiaux, 11,9 % des 2 747 pour invalidité). Le
   chiffre du même champ est la table H de l'EACR (caisse 0012, « Cube SRE »,
   flux), qui compte tous les liquidants civils de l'État : 19 278 / 52 693 =
   36,59 % en 2020 ; 20 992 / 54 735 = 38,35 % en 2021 ; 20 893 / 54 666 =
   38,22 % en 2022 ; 20 824 / 51 981 = 40,06 % en 2023 ; 17 547 / 45 078 =
   38,93 % en 2024 ; 38,43 % en moyenne. Le modèle, selon la note de la file I
   (2024 seul refait par R-I, 50,64 %) : 37,2, 42,4, 41,9, 31,9 et 50,6 % de
   2020 à 2024, 40,8 % en moyenne ; 2,4 points de plus que la table H en
   moyenne, 11,7 en 2024. L'accord de 41,6 à 42,7 que la note y voyait tenait
   au champ. C'est la table H que le script met en regard ; déclaré dans son
   en-tête (bd1c251).

## Les tests

Sur 8c93f72, la simulation tournant à côté : `python -m pytest -m rapide`,
4 215 réussis, 33 sautés, en 6 min 24 s ; `PRESOMPTIONS_DECALEES=1 python -m
pytest -m rapide`, 4 017 réussis, 231 sautés ; `python -m pytest
tests/test_grille_large.py`, 100 réussis, en 6 min 13 s ; les deux tests
nouveaux sous la garde des présomptions décalées, réussis. Sur bd1c251, les
deux tests de la mesure et les deux de la version, réussis.

## Ce que les sources ne tranchent pas

- Le taux de surcote des liquidants de 68 ans et plus de la Cnav en 2024 :
  l'EIR ne voit aucun départ des nés en 1953 après 67 ans, et la table H ne
  dit pas la surcote par âge. Le calcul ci-dessus prend 34,6 %, le taux des
  départs à 67 ans, et donne la borne de 100 %.
- D'où viennent les 5,7 à 6,2 points qui restent. Trois pistes, aucune
  établie : les générations nées après 1953, que la version fait surcoter
  comme les nés en 1953, quand la part des liquidants de la Cnav qui surcotent
  monte d'année en année (table H : 16,56 % en 2021, 17,02 en 2022, 18,55 en
  2023, 18,87 en 2024 ; 2020 n'a pas de surcote au témoin), sans que la table
  dise la génération ; le champ, la Cnav comptant tous ses liquidants,
  polypensionnés compris, la population son seul groupe du régime général ;
  la façon de compter, au drapeau ou à la condition.
- Si l'écart de 10,9 à 11,49 % tient tout entier à la façon de compter : le
  code le rend vraisemblable, aucune mesure du dépôt ne l'a encore montré.
- La date à laquelle la table B compte l'âge : le témoin ne la dit pas.

**Ce qui reste**, de ce point :

1. *Lancer la mesure jusqu'au bout* — `python scripts/mesurer_surcote.py
   --processus 4 --json mesure.json`, près de trois heures sur quatre cœurs
   sans mémoire des calculs —, puis écrire, dans une note neuve, ses deux
   tableaux, le chiffre des liquidants du régime général de 2024 à la
   condition et son croisement avec le drapeau, et la part de ces liquidants
   à 68 ans et plus dans le modèle. Il faut une session qui puisse attendre
   au-delà des deux heures d'une tâche de fond, ou le découpage de la mesure
   en étapes gardées.
2. *Les départs après 67 ans* et *la surcote des générations nées après
   1953*, ceux de la note de la file I (« Ce qui reste », points 1 et 2) :
   le premier explique 1,7 point de l'écart, non l'essentiel ; la file I
   conseillait de trancher le second, au propriétaire, après le premier, « qui
   en explique une part » : une part de 1,7 point sur 7,4 à 8.
