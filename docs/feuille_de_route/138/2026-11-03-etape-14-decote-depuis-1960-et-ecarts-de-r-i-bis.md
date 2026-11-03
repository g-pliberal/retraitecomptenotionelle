# Étape 14 : la décote des générations nées depuis 1960, et les quatre écarts de la relecture R-I-bis

**Le 3 novembre 2026 : la part de départs avec décote que la population prête
à toutes les générations nées depuis 1960, 13,0 % des hommes et 13,7 % des
femmes, est celle des liquidants de la Cnav de 2024 (régime général,
indépendants compris), non celle d'une génération ni de tous les régimes. Les
sources publient autre chose : la Cnav décote 11,2 % des hommes et 14,8 % des
femmes nés en 1957, la dernière génération vue à 67 ans ; l'État civil, 16,0 % ;
la CNRACL, 8,1 % ; les exploitants agricoles, 6,6 %. Le modèle tombe près du
total (génération 1960, 12,4 % tous régimes) par compensation : ses
fonctionnaires ne décotent jamais, son régime général et ses exploitants
décotent trop (16,1 % des nés en 1957 au régime général, pour 13,1 % ; 14,5 %
des exploitants, pour 6,6 %). C'est une hypothèse de la population, non une
règle : décrite et chiffrée, non corrigée. Les quatre écarts de R-I-bis sont
repris : la mesure complète tourne sur un commit publié (e12fe03) et sa
sortie est au dépôt.**

Demande : la sixième vague, lancée le 3 novembre 2026 par la session
d'orchestration, session I : action 138, étape 14 ; d'abord les quatre écarts
faibles de la relecture R-I-bis (fb55a58,
`2026-11-03-relecture-corrections-de-la-relecture-r-i.md`), puis la décision
17 du propriétaire, que la file D a écrite le même jour
(`docs/feuille_de_route/130/2026-11-03-decisions-du-proprietaire.md`, § 17) :
« faut-il revoir la part de départs avec décote que le modèle prête à tous
les retraités nés après 1960 ? Ce chiffre, 13 % des hommes, ne vient que des
salariés du privé » — la mesurer contre la source publiée, régime par régime
si elle le permet, dire d'où vient l'écart, et ce qu'une correction
demanderait, sans la faire. Ni règle ni paramètre du modèle ne change.

## Les sources, ouvertes pendant la session

Rien de mémoire, rien repris d'une note sans l'avoir rouvert :

- *Le panorama de la DREES*, « Les retraités et les retraites – Édition
  2026 », 14 octobre 2026 : le PDF du manifeste (`drees_panorama_retraites_2026`,
  servi par son miroir), 9 983 866 octets, SHA-256
  `9eb36a06639af0f4298d281b41acbde4236e47fc73e40c673f153ad86735e9be`,
  recalculée, celle de `data/sources.yaml`. Sa fiche 17, « Les taux de
  liquidation des pensions », p. 154 à 159 de l'ouvrage (p. 155 à 160 du PDF).
  Le graphique 4, p. 158, « Part des retraités ayant liquidé leurs droits avec
  une décote, par génération », s'arrête à la génération 1957 ; sa note :
  « pour les générations nées en 1953 ou avant, la part est calculée parmi
  les retraités pondérés pour être représentatifs des assurés ayant perçu une
  pension ; pour celles nées en 1954 ou après, elle est calculée à l'âge de
  67 ans. Il s'agit des âges où la quasi-totalité des personnes de chaque
  génération sont déjà parties à la retraite » ; son champ par régime :
  « Retraités […] ayant un droit direct dans le régime, vivants au
  31 décembre de l'année de leurs 67 ans ». La note 6, p. 155 : « La
  génération 1957 est ici prise en compte car elle a 68 ans révolus au
  1er janvier 2025 ». La série « tous régimes » ne passe pas 1953 (10,7 %,
  EIR 2020), où le régime général est à 11,6 %.
- *Ses classeurs*, l'archive du manifeste
  (`drees_panorama_retraites_2026_classeurs`, release `documents-apportes`),
  SHA-256 `ec7503f8…aaf64911`, recalculée : `fiche_17.xlsx`, feuilles
  « F17_Graphique 4 » (les valeurs du graphique, celles de
  `data/reference/macro/retraites_generations.csv`) et « F17_Tableau compl -
  Decote », les nouveaux retraités de 2024 partis avec une décote : régime
  général 13,4 %, MSA salariés 6,6, MSA non-salariés 5,0, FPE civils 18,4,
  CNRACL 9,5, CRPCEN 12,3, SNCF 15,9, CNIEG 11,4, RATP 17,8, Banque de
  France 9,3.
- *L'EACR*, les deux classeurs de la version du 26 mai 2026, téléchargés du
  portail de la DREES (`donnes_eacr`) : « 62 EACR diffusée Part 1 »,
  24 070 107 octets, SHA-256 `b286834e5da0dcc37888d68c8d41d1b3c76578db586c7f05072e8266c7fb3cbe` ;
  « Part 2 », 15 724 957 octets,
  `d12f9f20c37ca4e5eedecb1f9607df23042d1140455ee35e3be16bbb057c2556` ; sa
  feuille « H-Conditions_liq », que le récupérateur lit désormais âge par âge
  (ci-dessous). Et la documentation du jeu, « Documentation EACR - version du
  18 mai 2026 », table H, p. 24 : la table « contient les effectifs et
  montants du stock de retraités selon les conditions de liquidation. Les
  données sont ventilées par sexe et âge » ; elle ne définit pas l'âge de la
  table H, quand elle dit, des tables B, C et D, « l'âge atteint au 31/12 à
  partir de 2009 ». Le stock de 2024 à 67 ans redonne au dixième chaque part
  de la génération 1957 du graphique 4 (Cnav 13,1 ; MSA salariés 5,1 ;
  exploitants 6,6), sauf l'État civil (16,0 pour 15,8) : c'est l'âge en fin
  d'année, la génération 2024 moins l'âge.
- *Au dépôt* : `data/reference/macro/departs_generations.csv` (EIR, nés en
  1953 : l. 1068, 1071, 1143) ; `data/reference/macro/conditions_selon_l_age_residents.csv`
  (le stock de 2020, recompté ci-dessous) ; le code,
  `scripts/grille_large.py` (`decote_du_flux`, `decotes_des_generations`),
  `src/retraite_notionnelle/facteurs_depense.py` (`part_decotee_du_flux`,
  `part_decotee_de_la_generation`, `parts_decotees`), `scripts/facteurs_depense.py`.

## La mesure complète, au dépôt (R-I-bis, point 5)

- *Ce qui a tourné* : `python scripts/mesurer_surcote.py --processus 4 --json …`,
  sur un worktree de **e12fe03** (`e12fe03a91eb14595f5d52387b030929453304c1`),
  arbre **adb1ff2f8caa67b29cd3c759576175b93a1dca4e**, sans fichier suivi
  modifié (`"modifie": false`) ; le commit est sur `main`. Lancée à 20 h 59,
  finie à 22 h 44 (« 6334.1 s » à son impression), sur quatre cœurs, sans
  mémoire des calculs ; la machine a eu jusqu'à 12,7 Go occupés. 19 408 cas
  types, 542 749 couples, 20 083 échecs (17 038 liquidations antérieures à la
  répartition, 3 045 carrières sans régime actif) ; 101 618 couples dont la
  condition de départ se lit, tous lus (17 090 liquidants, 78 456 des stocks,
  58 224 des générations comptées, en partie les mêmes) ; 32 094 couples
  pour la décote.
- *Sa sortie, au dépôt* : `docs/mesures/138/2026-11-03-etape-14-mesure-e12fe03.json`
  (89 348 octets, SHA-256 `2938c8ac…edf69e9`), qui porte son commit et son
  arbre (`depot`), et son impression, `…-mesure-e12fe03.txt` (21 047 octets,
  `47aea4b2…b545885`). Pour la refaire : `git worktree add x e12fe03`, puis,
  dans `x`, la même commande ; une heure trois quarts sur quatre cœurs.
- *Ce qu'elle redonne* : chaque chiffre de la mesure d'I-bis (8c93f72) au
  centième — les départs des générations 1950 et 1955 contre l'EIR, l'État et
  la CNRACL de 2020 à 2025, le régime général de 2024 (10,91 % à la
  condition, 11,49 au drapeau, 17,15 de décote), les retraités de 2020, les
  âges, les pensions et l'écart de Kolmogorov : ce que les autres files ont
  changé au modèle depuis 490cb7a ne les déplace pas.

## Les quatre écarts de R-I-bis

### 1. Les départs après 67 ans : selon les départs qu'ils remplacent (point 2)

La note d'I-bis calculait ce qu'ajouteraient des départs après 67 ans
« sans rien changer au taux m de ses départs de 67 ans et moins ». C'est une
hypothèse, qu'aucune source ne fonde. Le calcul exact est un mélange : si une
part a des liquidants part après 67 ans au taux s, à la place de départs qui
surcotaient au taux r, la part des surcotés gagne a × (s − r), r allant de 0
(ils remplacent des départs sans surcote) à m (des départs comme les autres) ;
les sources ne disent pas lequel. Les valeurs, refaites :
R = 122 368 / 648 346 = 18,874 % (table H, Cnav, flux de 2024) ;
a = (20 350 + 6 969 + 4 832 + 15 581) / 648 346 = 47 732 / 648 346 = 7,362 %
(table B, Cnav, 68 ans et plus) ; s = 34,6 % (EIR, nés en 1953 partis à
« 67 ans et plus », `departs_generations.csv`, l. 1068 ; 6,0 milliers sur
757,0, l. 1071 et 1143) ; m = 10,911 % (la mesure de e12fe03, comme celle
d'I-bis).

| | r = m (I-bis) | r = 0 (R-I) |
|---|---|---|
| gagné au taux de l'EIR, a × (s − r) | 0,07362 × 23,69 = 1,74 point | 0,07362 × 34,6 = 2,55 points |
| reste de l'écart R − m = 7,96 points | 6,22 | 5,42 |
| borne, tous surcotent, a × (1 − r) | 6,56 | 7,36 |
| reste, même alors | 1,40 | 0,60 |

**La phrase au propriétaire, corrigée** : les nouveaux retraités du privé de
2024 surcotent pour 10,9 % dans le modèle, 18,9 % à la Cnav ; l'absence de
départ après 67 ans en explique de 1,7 à 2,5 points au seul taux que l'enquête
donne aux départs tardifs, selon les départs qu'ils remplacent, et 7,4 au plus
si tous surcotaient ; le reste, de 5,4 à 6,2 points, les sources ouvertes ne
disent pas d'où il vient. La conclusion d'I-bis tient pour tout r : les départs
après 67 ans n'expliquent pas l'essentiel de l'écart. Vu de la Cnav, si ses 68
ans et plus surcotent pour 34,6 %, ses 67 ans et moins le font pour
(122 368 − 0,346 × 47 732) / 600 614 = 17,62 %, 6,71 points de plus que le
modèle.

### 2. Les trois mutations qui passaient (point 1)

Trois tests de plus, dans `tests/test_grille_large.py` (207cb53), vus rouges
faute du code, puis verts :

- `test_la_mesure_de_la_surcote_lit_ses_sources_annee_par_annee` pose à la
  main la table H de l'État année par année (19 278 / 52 693 en 2020,
  20 992 / 54 735, 20 893 / 54 666, 20 824 / 51 981, 17 547 / 45 078 en 2024,
  rien en 2025) et la décote de la Cnav de 2024 (86 776 / 648 346, non le taux
  plein, 439 202) ;
- `test_la_mesure_de_la_surcote_construit_la_version_la_constante_allumee`
  fait porter à chaque grille la valeur de la constante sous laquelle elle
  s'est construite (`les_deux_grilles`, sorti de `mesurer`) ;
- les stocks à la condition (point 3) ont le leur, qui tient aussi la règle
  de 2004.

Rejouées une à une sur la copie du script, puis le script rendu, octet pour
octet : « la table H de l'État lue en 2024 chaque année », 1 échec ; « la
décote de la Cnav lue au taux plein », 1 échec ; « les pesées permutées »,
1 échec ; et une quatrième, « les stocks sans la règle de 2004 », d'abord
passée, puis prise quand le test a donné une condition « surcote » à deux
départs de 2000.

### 3. Les stocks à la condition (point 3)

Le script compte désormais aussi les stocks à la condition de leur départ,
parmi ceux dont elle se lit ; un départ d'avant 2004 (l'année de naissance
plus l'âge de liquidation, en années entières, avant
`ANNEE_DE_LA_SURCOTE`), que la loi ne surcotait pas, l'est sans condition.
Toutes les conditions se lisent (« inconnues » nulles partout).

| | source | au drapeau | à la condition |
|---|---|---|---|
| régime général, retraités de 2024 (table H, Cnav) | 11,25 | 7,81 | 7,07 |
| État civil, retraités de 2024 (table H) | 22,58 | 23,52 | 23,03 |
| CNRACL, retraités de 2024 | — | 13,09 | 12,91 |
| retraitées de 2020 (EIR, résidentes) | 7,83 | 7,74 | 7,33 |
| retraités de 2020 | 9,37 | 7,39 | 6,27 |
| retraitées de 2020 de 70 à 74 ans | 13,53 | 11,80 | 11,35 |
| retraités de 2020 de 70 à 74 ans | 16,15 | 12,55 | 10,85 |
| fonctionnaires civils parmi les retraitées surcotées | 32,4 | 42,59 | 43,56 |
| fonctionnaires civils parmi les retraités surcotés | 24,7 | 27,43 | 31,57 |

(Version de la trente-septième ; en pour cent.) Les sources de 2020, refaites
à `conditions_selon_l_age_residents.csv` : 662 surcotées sur 8 452 milliers de
résidentes, 7,83 % ; 674 sur 7 196, 9,37 % ; à 70-74 ans,
662 × 38,7 % / (8 452 × 22,4 %) = 13,53 % et 674 × 40,7 % / (7 196 × 23,6 %)
= 16,15 % ; parmi les surcotés, l'État civil et la CNRACL, mono et
polypensionnés, 9,2 + 2,1 + 8,8 + 12,3 = 32,4 % des femmes, 7,5 + 1,1 + 6,4
+ 9,7 = 24,7 % des hommes. Ce que R-I-bis pressentait se vérifie : le drapeau
était un plafond. Au régime général, l'écart à la table H passe de 3,44 à
4,18 points ; chez les hommes de 2020, de 2,0 à 3,1 points ; l'État civil
reste près de la table H (+0,45).

### 4. La sortie et l'arbre (point 5) ; les négligeables

La sortie et l'arbre sont au dépôt (ci-dessus). Les négligeables : le taux des
liquidants du régime général de 2024 à 67 ans, 6,58 % (Cnav 9,34 %, 60 530 /
648 346), est imprimé ; des nés en 1952 et 1953, seuls les nés en 1952 portent
le relèvement de 2012 du tableau 103 (2012,75) — les nés en 1953 atteignent
leur âge légal en 2014,17, entre deux années à 31 % ; la condition compte
toujours « surcote » un départ passé d'un rien le taux plein, sans vérifier
qu'il gagne un trimestre : non mesuré.

## La décote des générations nées depuis 1960 (décision 17)

### Où le chiffre est écrit, et d'où il vient

- *La population* (`scripts/grille_large.py`) : `decotes_des_generations`
  prête à chaque génération, parmi tous ses retraités, sexe par sexe, la part
  de `decote_du_flux`, depuis la génération 1960 (`GENERATION_DU_FLUX`), en
  droite ligne depuis celle des nés en 1953 de l'EIR ; `decote_du_flux` lit au
  témoin la table H de la Cnav, flux de 2024 : **40 139 / 308 706 = 13,00 %
  des hommes, 46 637 / 339 640 = 13,73 % des femmes**. Les jumelles des
  carrières incomplètes du salariat et des non-salariés la portent
  (`parts_des_jumelles`).
- *La grille du coût de l'étape 3* (`src/retraite_notionnelle/facteurs_depense.py`) :
  `part_decotee_du_flux` lit la même ligne, les deux sexes réunis,
  **86 776 / 648 346 = 13,38 %**, que `part_decotee_de_la_generation` prête
  dès la génération 1960 aux cohortes qui peuvent décoter à l'âge légal
  (`parts_decotees`), sous l'option `--decote-generation` de
  `scripts/facteurs_depense.py` (le départage de la couverture de 2022-2030) ;
  `GENERATION_DU_FLUX` y date ce flux à « l'âge moyen des nouveaux retraités
  de l'année, 63,6 ans ».
- *Ce que compte cette ligne* : les liquidants de la Cnav de l'année, tous
  âges, la caisse 0015 depuis 2020, qui « comprend également les travailleurs
  indépendants » (fiche 17, note 1 du graphique 4) ; chacun dès qu'il a une
  pension du régime, polypensionnés compris. Le privé, salariés et
  indépendants, donc : non tous les régimes, et non une génération.

### Ce que les sources publient, régime par régime

Table H, la part partie avec une décote (témoin refait,
`tests/temoins/drees_eacr_tables_2026.json`) ; « 64 ans » est le stock de 2024
à 64 ans, la génération 1960 (seuls ses retraités déjà partis), « 67 ans »
celui de la génération 1957, qui a passé l'âge d'annulation :

| caisse | flux de 2024 | génération 1960, à 64 ans | génération 1957, à 67 ans |
|---|---|---|---|
| Cnav, ensemble | 86 776 / 648 346 = 13,38 | 69 611 / 551 996 = 12,61 | 85 676 / 653 763 = 13,11 |
| Cnav, femmes | 46 637 / 339 640 = 13,73 | 40 845 / 285 736 = 14,29 | 51 069 / 344 675 = 14,82 |
| Cnav, hommes | 40 139 / 308 706 = 13,00 | 28 766 / 266 260 = 10,80 | 34 607 / 309 088 = 11,20 |
| État civil | 8 289 / 45 078 = 18,39 | 9 726 / 50 663 = 19,20 | 11 159 / 69 758 = 16,00 |
| État civil, femmes | 4 775 / 25 188 = 18,96 | 5 350 / 29 586 = 18,08 | 5 756 / 38 826 = 14,83 |
| État civil, hommes | 3 514 / 19 890 = 17,67 | 4 376 / 21 077 = 20,76 | 5 403 / 30 932 = 17,47 |
| État militaire | 1 101 / 9 603 = 11,47 | 107 / 11 568 = 0,92 | 21 / 11 011 = 0,19 |
| MSA salariés | 2 844 / 43 396 = 6,55 | 2 166 / 35 567 = 6,09 | 2 454 / 47 916 = 5,12 |
| MSA exploitants | 1 521 / 30 425 = 5,00 | 1 482 / 24 219 = 6,12 | 2 050 / 31 225 = 6,57 |

Le SRE ne donne pas la ligne « Ensemble » : elle se refait de la somme du taux
plein, de la décote et de la surcote. La CNRACL et les régimes spéciaux ne
sont pas dans la table H : le panorama leur donne la génération 1957 (CNRACL
8,1 %, graphique 4) et les nouveaux retraités de 2024 (CNRACL 9,5 ; SNCF 15,9 ;
CNIEG 11,4 ; RATP 17,8 ; CRPCEN 12,3 ; Banque de France 9,3 ; tableau
complémentaire). Des professions libérales, la table H ne porte que la CNBF,
les avocats, que le témoin ne garde pas : lue au classeur (caisse 2201,
« EACR 2024 »), 123 décotés sur 1 120 liquidants de 2024 (10,98 %), 103 sur
421 à 64 ans (24,47 %), 119 sur 811 à 67 ans (14,67 %) — de petits
effectifs, et une section seulement ; la feuille porte aussi la Cnav d'avant
2020 (0010) et les complémentaires (CNBF, Agirc-Arrco). Aucune source ouverte
ne donne de part tous régimes après la génération 1953 (10,7 %, où le régime
général est à 11,6 %).

En 2022 et 2023, les deux sexes de la Cnav ne redonnent pas l'ensemble
(343 013 + 327 327 = 670 340, non 693 238 ; 265 596 + 203 090 = 468 686, non
692 416) : la mesure n'en donne aucune part par sexe.

### Ce que le modèle en fait (mesure de e12fe03, version)

Les départs de chaque génération de la grille pris à 67 ans, à la condition
de leur départ, comme `grille_large.departs` les compte (survie propre, poids
de l'année de leurs 67 ans, parts des générations) :

| génération | tous régimes | femmes (cible) | hommes (cible) | régime général |
|---|---|---|---|---|
| 1955 | 11,28 | 12,40 (12,42) | 10,04 (9,21) | 14,69 (DREES, 1955 : 12,8) |
| 1960 | 12,42 | 13,10 (13,73) | 11,66 (13,00) | 16,02 |
| 1965 | 10,74 | 12,59 (13,73) | 8,65 (13,00) | 13,73 |

Chaque groupe de la population en 2024, à la condition, contre sa caisse :

| groupe | liquidants de 2024 | génération 1960, à 64 ans | génération 1957, à 67 ans |
|---|---|---|---|
| régime général (Cnav) | 17,15 (13,38) | 13,36 (12,61) | 16,12 (13,11) |
| — femmes | 17,27 (13,73) | 15,21 (14,29) | 17,00 (14,82) |
| — hommes | 16,99 (13,00) | 11,23 (10,80) | 15,15 (11,20) |
| État civil | 0,00 (18,39) | 0,00 (19,20) | 0,00 (16,00) |
| CNRACL | 0,00 (9,5, panorama) | 0,00 (—) | 0,00 (8,1, génération 1957) |
| État militaire | 0,00 (11,47) | 0,00 (0,92) | 0,00 (0,19) |
| exploitants agricoles (MSA non-salariés) | 15,18 (5,00) | 12,22 (6,12) | 14,49 (6,57) |
| professions libérales | 19,16 (—) | 35,09 (—) | 18,90 (—) |
| régimes spéciaux | 77,92 (9,3 à 17,8, panorama) | 7,62 (—) | 0,00 (—) |

Au régime général, les deux façons de lire la décote s'accordent (17,15 % à la
condition de départ comme à la proratisation). Ses liquidants, année par
année, décotent pour 14,93, 16,63, 20,05, 14,55 et 17,15 % de 2020 à 2024,
quand la Cnav en compte 12,82, 13,15, 13,72, 13,68 et 13,38 : la grille, qui
simule une génération sur cinq, fait partir ses départs avec décote par
paquets (à 63 et 65 ans en 2024, aucun à 64, 66 et 67 ans ; la Cnav en a à
chaque âge, 22,15 % à 64 ans), et le flux d'une année n'est pas une mesure
qu'elle tienne. Les 77,92 % des régimes spéciaux en 2024 sont du même ordre :
quelques cohortes, d'une génération qui ouvre son droit cette année-là.

### D'où vient l'écart

1. *Le flux n'est pas une génération.* Une même caisse, la Cnav, décote
   13,00 % de ses liquidants hommes de 2024, mais 11,20 % des hommes nés en
   1957, vus à 67 ans, et 10,80 % des nés en 1960 déjà partis à 64 ans ;
   13,73 % des femmes du flux, mais 14,82 % des nées en 1957 et 14,29 % des
   nées en 1960 à 64 ans. Prise à la génération 1957, la cible des hommes
   serait de 1,80 point plus basse (13,00 − 11,20), celle des femmes de 1,09
   point plus haute (14,82 − 13,73). Pourquoi le flux de 2024 s'écarte de la
   génération, la table ne le dit pas : la composition par âge des départs de
   l'année (la Cnav en compte 184 872 à 62 ans en 2024, 261 708 en 2022) en est
   une piste, non chiffrée.
2. *Le privé n'est pas tous les régimes.* Les autres caisses décotent
   autrement : plus à l'État civil (16,0 % de la génération 1957), moins à la
   CNRACL (8,1), à la MSA (5,1 et 6,6), presque jamais chez les militaires
   (0,19) ; et, en 2024, de 9,3 à 17,8 % dans les régimes spéciaux. La seule
   part tous régimes publiée, celle des nés en 1953, est de 0,9 point sous celle
   du régime général (10,7 et 11,6 %). Les parts par régime comptent chaque
   retraité qui a un droit dans le régime, les polypensionnés dans chacun ;
   leur moyenne n'est pas une part tous régimes, et aucune source ne la donne.
3. *La population ne la porte que par le privé et les non-salariés.* Ses
   fonctionnaires ne décotent jamais (0,00 % à l'État, à la CNRACL, chez les
   militaires ; la note des agents décotés le disait déjà) ; toute la décote
   de la génération passe par les jumelles des carrières incomplètes du
   salariat et des non-salariés, qui décotent donc trop. Dans la génération
   1960, à 67 ans, sa décote tous régimes, 12,42 %, se fait de 10,96 points au
   régime général (68,42 % de la génération, à 16,02 %), 0,67 aux professions
   libérales (3,55 %, à 18,92 %), 0,59 aux exploitants (4,09 %, à 14,44 %),
   0,19 aux régimes spéciaux (2,48 %, à 7,83 %) et rien ailleurs. Un calcul,
   non une source : aux poids de cette génération, les parts publiées de la
   génération 1957 (régime général 13,11 ; État civil 16,00 ; CNRACL 8,1 ;
   exploitants 6,57 ; militaires 0,19) donneraient 11,64 points sur les
   93,97 % de la génération qu'elles couvrent, de 11,6 à 12,8 % en tout si les
   libéraux et les régimes spéciaux, qui n'en ont pas, décotaient de 0 à 20 % ;
   le modèle, 12,42 %, est dans cette fourchette, par compensation : il manque
   à la fonction publique 9,69 % × 16,00 + 10,54 % × 8,1 = 2,40 points, que
   le régime général (68,42 % × (16,02 − 13,11) = 1,99 point) et les
   exploitants (4,09 % × (14,44 − 6,57) = 0,32) rendent à peu près.
4. *La génération 1965 tombe sous sa cible*, chez les hommes surtout (8,65 %
   pour 13,00) : les agents des régimes spéciaux, qui décotaient tous avant la
   trente-sixième version, n'en portent plus que leur part, et les jumelles ne
   peuvent porter le reste (note des agents décotés, « Ce qui reste »,
   point 1).

La mesure ne montre l'erreur d'aucune règle du modèle : la décote de la
fonction publique est une règle du dépôt (`data/reference/legislation/decote_fonction_publique.csv`,
source `dila_legi_decote_fonction_publique`), mais la population n'a pas de
fonctionnaire dont la carrière la déclenche. L'écart est dans les hypothèses
de la population et de la grille du coût de l'étape 3.

### Ce qu'une correction demanderait (non faite)

- *Une cible par génération, non par année* : la part de la Cnav à 67 ans de
  la dernière génération vue, 1957 (14,82 % des femmes, 11,20 % des hommes ;
  13,11 % ensemble pour la grille du coût, qui réunit les sexes), ou celle des
  nés en 1960 à 64 ans (14,29 et 10,80 ; 12,61), au lieu du flux de 2024. Un
  paramètre de données, `decote_du_flux` et `part_decotee_du_flux` lisant le
  stock par âge du témoin, que le récupérateur garde désormais.
- *Une cible par groupe* : la part de la Cnav pour le régime général, celle de
  l'État civil (table H, 0012 : 14,83 % des femmes, 17,47 % des hommes nés en
  1957), de la CNRACL (8,1 %, graphique 4, sans les sexes), des exploitants
  (8,52 et 5,27 %), des militaires (0,19 %) ; les régimes spéciaux n'ont que
  leurs nouveaux retraités de 2024, et les libéraux la seule CNBF.
- *Des fonctionnaires qui décotent* : des carrières statutaires incomplètes,
  que la population n'a pas, pour que la fonction publique porte sa part ; et
  les jumelles du salariat et des non-salariés recalées sur la leur. C'est un
  changement de la population (étape 14), et, pour la grille du coût, de
  `parts_decotees`, qui prête aujourd'hui une seule part aux cohortes qui
  peuvent décoter, à décider avec la décision 11 : au propriétaire.

## Ce que les sources ne tranchent pas

- La part des nés en 1960 et après une fois toute la génération partie : elle
  ne se publie qu'à 67 ans, en 2027 pour la génération 1960 ; la table H n'en
  dit que les retraités déjà partis.
- Une part tous régimes après 1953 : aucune source ouverte ; les parts par
  régime ne s'additionnent pas, à cause des polypensionnés.
- Pourquoi le flux de la Cnav de 2024 décote plus d'hommes, et moins de
  femmes, que ses générations : non établi.
- L'écart de l'État civil entre la table H (16,0 %, « Cube SRE 2024 ») et le
  graphique 4 (15,8 %) pour la génération 1957, comme celui de sa surcote déjà
  déclaré (`test_drees_panorama_2024.py`) : non expliqué.
- L'âge de la table H : la documentation ne le définit pas pour elle ; le
  recoupement à la génération 1957 le donne en fin d'année.

## Les tests

Trois commits sur `main`, test et code ensemble : 207cb53, 3a04aeb, e12fe03.
Vus rouges faute du code : `test_le_temoin_garde_les_conditions_de_la_cnav_age_par_age`
(`tests/test_controle_eacr.py`), puis les cinq de `tests/test_grille_large.py`
— les sources année par année, la constante allumée, les stocks à la
condition et la décote d'après 1960, les départs de chaque génération par
classe, et le cas court, qui tient désormais le commit et l'arbre de la sortie.
Sur 9342f25 (207cb53 une fois rebasé) : `python -m pytest -m rapide`, 4 269
réussis, 56 sautés ; `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide`,
4 071 réussis, 254 sautés ; `tests/test_controle_eacr.py`,
`tests/test_drees_panorama_2024.py`, `tests/test_facteurs_depense.py` et
`tests/test_grille_large.py`, qui lisent le témoin ou le script, 173 réussis.
Sur e12fe03 : ces trois premiers fichiers, 69 réussis, et les neuf tests de la
mesure de `test_grille_large.py`, réussis. Le témoin refait ne change que par
ses clés neuves et sa date de lecture : les valeurs que le modèle en lit sont
les mêmes. `python scripts/conservation.py --depuis HEAD` ne dit perdu que le
bloc « Reprise » de l'étape, récrit. Aucun texte de droit lu : pas d'entrée au
journal de veille.

## Ce qui reste

1. *La décote d'après 1960, au propriétaire* : prendre la cible à une
   génération plutôt qu'au flux ; la prendre par groupe ; faire décoter des
   fonctionnaires. La décision 11 (la grille du coût) attend la même réponse.
2. *La surcote d'après 1953 et les départs après 67 ans* (note d'I-bis) : de
   1,7 à 2,5 points de l'écart à la Cnav ; le reste, non expliqué.
3. Les autres points de l'étape, une session chacun : les artisans, les
   saisonniers agricoles ; les femmes âgées ; la durée des femmes.
