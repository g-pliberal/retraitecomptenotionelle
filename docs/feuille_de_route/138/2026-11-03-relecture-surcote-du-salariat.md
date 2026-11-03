# Relecture de la surcote du salariat selon la génération

File R-I, vague 4, le 3 novembre 2026 : relecture indépendante des commits 624ec9f
et 730a6bb (session `session_01FVFLAk9nrLFFojgxkLj1aS`, note
`2026-11-03-etape-14-surcote-du-salariat-selon-la-generation.md`), sur `main` à
730a6bb. Rouverts ici, sans rien reprendre de la session ni de mémoire : le jaune
pensions annexé au PLF 2027, le PDF lui-même (miroir `jaune-2027`, empreinte
SHA-256 73dd4a66…2dbaf5, celle de `data/sources.yaml`) ; les fichiers certifiés de
l'EIR des générations 1950 et 1953 (`departs_generations.csv`) et du stock de 2020
(`conditions_selon_l_age_residents.csv`) ; le témoin des tables H, B et C de l'EACR
du 26 mai 2026 (`tests/temoins/drees_eacr_tables_2026.json`). La population a été
reconstruite et recomptée par un script à moi ; la simulation, refaite par un
pilote à moi (hors dépôt, comme celui de la session). Rien n'a été modifié : ni
règle, ni donnée, ni test, ni code, ni bloc « Reprise ».

**Verdict.** **Conforme sur l'essentiel.** Chaque source citée dit le chiffre que
la note lui prête, pour la bonne population ; le code calcule ce que la note
décrit ; les valeurs attendues des tests se refont à la main, et les parts du
salariat par un recompte indépendant ; les tests sont verts ; la simulation, refaite
à part, redonne ses chiffres au dixième près — la génération 1950 surcote pour
11,28 % (EIR 11,8), la génération 1955 pour 14,06 % (14,4), le stock de l'État en
2024 pour 23,52 % (EACR 22,6), contre 15,79, 15,99 et 30,30 % avant. Le message de
624ec9f et la note disent juste l'un et l'autre (point 2). **Écarts**, par ordre de
gravité : deux moyens — au propriétaire, « surtout parce que personne n'y part
après 67 ans » n'est pas établi, la note n'y voyant qu'« une part » (point 5) ; les
mesures sortent d'un pilote hors du dépôt, qu'on ne peut refaire tel quel (point
4.4) ; cinq faibles — au propriétaire, « les nés en 1955 » qui retrouveraient
l'enquête, qui ne les voit pas (point 5) ; les liquidants du régime général de
2024, 11,49 % chez moi pour 10,9 (point 2) ; l'accord de l'État sur ses liquidants,
qui tient au champ (4.5) ; la rupture de 2011-2012 du jaune, non dite (4.1) ; la
cible et le juge, deux chiffres de l'EIR (4.2) ; des négligeables — cinq écarts au
dixième, le niveau du tableau 103 (4.3), deux en-têtes de fichiers certifiés.

## 1. Les sources, chiffre par chiffre

| Chiffre de la note ou du code | Source ouverte | Constat |
|---|---|---|
| Part des nouvelles pensions civiles de l'État qui surcotent : 14 % en 2004, 28 % en 2011, 36 % en 2012, 31 % de 2013 à 2015, 30 % en 2016, 28 % en 2017, 31, 32, 34, 36, 36, 38, 36 % de 2018 à 2024, 35 % en 2025 | jaune, tableau 103, p. 182 du PDF : « Part des agents bénéficiaires », champ « les nouvelles pensions civiles de droit direct » ; 2005 à 2010 non publiés (« … ») | **conforme**, les seize valeurs, au fichier certifié (lignes 406 à 436) et à `SURCOTES_DU_JAUNE_PAR_ANNEE` |
| CNRACL : 8 % en 2004, 19 % en 2013 et 2014, 20 % en 2015, 19, 17, 18, 18, 19, 21, 22, 24, 24 % de 2016 à 2024, 21,5 % en 2025 | jaune, tableau 105, p. 183, ligne « Ensemble », champ « nouvelles pensions de droit direct » ; 2005 à 2012 non publiés | **conforme**, les quatorze valeurs |
| « la part de tous les départs […], invalidité et motifs familiaux compris » | champs des tableaux 103 et 105, ci-dessus | **conforme** : toutes les nouvelles pensions de droit direct |
| Parts de 2025 par catégorie : sédentaire de l'État 15 956 / 32 913 = 48,5 % ; CNRACL sédentaire 27,2 % | jaune, B-3 (p. 210) : 41 812 départs pour ancienneté des pensions civiles, 42,7 % avec surcote ; B-4 (p. 213) : actifs à 57 ans 5 552, 29,3 % ; à 52 ans 3 347, 8,1 % | **conforme** : (41 812 × 0,427 − 5 552 × 0,293 − 3 347 × 0,081) / 32 913 = 48,48 % ; (27 477 × 0,303 + 15 054 × 0,215) / 42 531 = 27,18 % |
| L'âge légal de la génération date aussi la part des actifs | jaune, p. 103 : la surcote des fonctionnaires civils compte « tout trimestre supplémentaire travaillé après le 1er janvier 2004 au-delà de l'âge d'ouverture des droits à retraite (64 ans pour les assurés nés à compter du 1er janvier 1968) » | **conforme** : l'âge qui ouvre la surcote est l'âge légal commun, non celui de la catégorie active |
| EIR, résidents en France : nés en 1950, 11,2 % des femmes et 12,2 % des hommes partis avec une surcote ; nés en 1953, 14,2 et 14,4 % | `departs_generations.csv`, tableau `residence`, colonne `france`, lignes 756, 768, 1530, 1542 | **conforme**, au fichier, au code (`surcotes_des_generations`) et au test. Cohérent avec ses lignes de l'étranger : (14,2 × 383 + 13,6 × 11) / 394 = 14,18 (ensemble 14,2) ; (14,4 × 350 + 18,5 × 13) / 363 = 14,55 (14,5) ; de même pour 1950 |
| Colonne « EIR » du premier tableau de la note : 14,4 ; 14,3 ; 14,6 ; 11,8 ; 11,2 ; 12,3 | même fichier, tableau `condition`, toutes résidences, la surcote rapportée aux conditions connues (`confronter_departs`) | **conforme** : 14,3 / 99,1 = 14,43 ; 14,2 / 99,2 = 14,31 ; 14,5 / 99,0 = 14,65 ; 11,7 / 99,3 = 11,78 ; 11,2 / 99,6 = 11,24 ; 12,2 / 99,2 = 12,30. Les places : 31,2 ; 26,6 ; 37,5 ; 26,7 ; 40,0 ; 23,8, au fichier |
| Stock de 2020 : 7,8 % des retraitées et 9,4 % des retraités partis avec une surcote ; 13,5 et 16,2 % à 70-74 ans ; fonctionnaires civils, 32,4 et 24,7 % des surcotés | `conditions_selon_l_age_residents.csv` (feuille « CondLiquidation », résidents) | **conforme** : 662 / 8 452 = 7,83 ; 674 / 7 196 = 9,37 ; (662 × 38,7) / (8 452 × 22,4) = 13,53 ; (674 × 40,7) / (7 196 × 23,6) = 16,15 ; 9,2 + 12,3 + 2,1 + 8,8 = 32,4 et 7,5 + 9,7 + 1,1 + 6,4 = 24,7 (État civil et CNRACL, mono- et polypensionnés) |
| EACR, État, stock de 2024 : 22,6 % | témoin, table H, caisse 0012 (« Cube SRE 2024 ») : 370 626 surcotés sur 1 641 380 | **conforme**, 22,58 % |
| Cnav, liquidants de 2024 : 18,9 % (19,6 des femmes, 18,0 des hommes) ; stock, 11,2 % ; décote, 13,4 % | témoin, table H, caisse 0015 : 122 368 sur 648 346 ; 66 672 sur 339 640 | **conforme** : 18,87 ; 19,63 ; 18,04 ; 11,25 ; 13,38 |
| EACR, liquidants de 2024 : 26,0 % à 62 ans, âge moyen 63,60, 7,3 % après 67 ans | témoin, table C (« Ancêtre 2024 », tous régimes), par `controle_eacr` | **conforme** : 25,97 ; 63,60 ; 7,29 (68 ans et plus) |

Ce qui n'a pas pu s'ouvrir : les classeurs d'origine de l'EIR et de l'EACR. Le site
de la DREES (`data.drees.solidarites-sante.gouv.fr`) a coupé la connexion deux fois
depuis le conteneur (« Connection reset by peer ») ; je n'ai lu que les fichiers
certifiés et le témoin, dont la certification (`scripts/verifier_donnees.py`) est
celle du dépôt, non la mienne. Les « statistiques de la Cnav » de la note sont la
ligne Cnav de la table H de l'EACR : aucune autre publication de la Cnav n'y est
citée.

## 2. Les calculs refaits

**Les valeurs attendues du premier test, à la main.** Les âges légaux, lus au
fichier certifié par `AgesOuverture` : 60 ans pour les nés en 1950, 61,17 en 1953,
62 en 1955 et 1960, 64 en 1975. Né en 1950, en 2010 : 0,14 + (0,28 − 0,14) × 6/7
= 0,26 à l'État, 0,08 + (0,19 − 0,08) × 6/9 = 0,1533 à la CNRACL ; né en 1953, en
2014,17, entre 2014 et 2015, tous deux à 31 % : 0,31 ; né en 1960, en 2022 : 0,36
et 0,22 ; né en 1975, en 2039, après 2025 : la part de 2025. Le sédentaire de
l'État né en 1950 : 0,4848 × 26/35 = 36,0 %. **Conforme**, et ce que la note en
dit (« 36,0 % au lieu de 48,5 », « né en 1955, en 2017, 28 % », « né en 1960 […]
la part de 2025 fois 1,03 » : 36/35 = 1,029).

**Les valeurs attendues du second test.** Nés en 1952 : 11,2 + (14,2 − 11,2) × 2/3
= 13,2 % des femmes, 12,2 + (14,4 − 12,2) × 2/3 = 13,67 % des hommes ; la part de
la dix-neuvième version, 14,2 × 87,4 / 57,3 = 21,66 % des femmes (`parts_avec_surcote` :
la surcote des nées en 1953, fois la part des carrières complètes parmi elles,
87,4 %, sur leur part parmi toutes, 57,3 %, au fichier) ; des hommes,
14,5 × 85,6 / 70,0 = 17,73 %. **Conforme.**

**La population, recomptée.** Un script à moi reconstruit la population
(`grille("population", …)`, la version allumée puis éteinte) et pèse, année de
naissance par année de naissance, chaque variante de son poids de retraitée de
2020 fois ce que l'année lui donne (`part_de_la_generation`), sans passer par
`parts_du_salariat_qui_surcote` : la part du salariat est celle de ses jumelles
qui surcotent parmi elles et leurs sœurs.

| | femmes, version | hommes, version | femmes, éteinte | hommes, éteinte |
|---|---|---|---|---|
| tous, surcote, nés en 1950 | 11,20 | 12,20 | 16,54 | 16,07 |
| tous, nés en 1952 | 13,20 | 13,67 | 16,51 | 15,78 |
| tous, nés en 1953 | 14,20 | 14,40 | 16,68 | 15,63 |
| tous, nés en 1955 | 14,20 | 14,40 | 16,67 | 15,41 |
| dont fonctionnaires civils, nés en 1955 | 5,10 | 3,84 | 6,40 | 4,81 |
| salariat, part des carrières qui le peuvent, nés en 1950 | 13,90 | 13,63 | 21,66 | 17,73 |
| nés en 1955 | 19,18 | 17,66 | 21,66 | 17,73 |
| nés en 1960 | 16,08 | 16,09 | 21,66 | 17,73 |
| sédentaire de l'État, nés en 1950 | 36,01 | 36,01 | 48,48 | 48,48 |

Les 19 408 cas types et leurs effectifs sont les mêmes dans les deux versions.
**Conforme** à la note : 19,2, 13,9 et 16,1 % des femmes, 17,7, 13,6 et 16,1 % des
hommes ; « 6,4 % de toutes les femmes, le salariat pour 10,3 %, 16,7 % ensemble »
avant la version, quand l'EIR voit 14,2 %.

**Le message du commit et la note.** L'un et l'autre sont justes, sur deux choses
différentes. La *cible* est celle des résidents nés en 1950 et en 1953 : le code
lit `publies[(génération, "residence", "france", sexe, "condition_surcote")]` pour
1950 (`min(ENQUETES_DES_DEPARTS)`) et 1953 (`GENERATION_DES_SURCOTES`), les lignes
de la source (point 1) ; le message de 624ec9f le dit. La *génération 1955* de la
note est la génération simulée de la grille, de cinq en cinq ans, que la mesure
juge sur les nés en 1953 (`GENERATIONS_DES_DEPARTS = {1950: 1950, 1955: 1953}`) ;
la note le dit (« la grille 1955 jugée sur les nés en 1953 »). La cible est bien
celle de la source, pour la bonne population : résidents, génération, part des
départs pris avec une surcote à l'âge où l'enquête la voit, 66 ou 67 ans.

**Les chiffres simulés.** Mon pilote tourne depuis un worktree figé à 9689bd99,
dont `src/`, `scripts/grille_large.py` et `scripts/controle_eacr.py` sont ceux de
730a6bb (n'en diffèrent que deux fiches, des entrées du journal de veille,
`scripts/fetch/dila_cherche.py` et trois fichiers de tests). Il construit la
population, version allumée puis éteinte, comme `mesurer` la construit
(`grille("population", effectifs, eir, multiplicateurs(centiles))`), la simule une
fois (`en_tetes(…, 4, alleges=True)`, 96 minutes sur quatre cœurs, sans rien
reprendre de la mémoire des calculs), et pèse la version éteinte sur la même
simulation, en ne changeant que les parts des générations (`GrilleEnTetes.parts`).
Les départs se jugent par `departs()`, le juge de la note. Le stock et le flux de
2024 se comptent sur `controle_eacr.cohortes_de_la_population` : les civils de
l'État (affiliations `fonctionnaire_etat`, `_actif`, `_super_actif`), le groupe
`regime_general` ; une jumelle tenue pour surcotée quand sa génération simulée
atteint l'âge légal en 2004 ou après (`ANNEE_DE_LA_SURCOTE`, la règle de `elargi`) ;
le stock de 2020 de même, en 2020 ; la part à 62 ans et l'âge moyen, par
`controle_eacr.mesure`. 542 749 couples, 20 083 échecs (17 038 liquidations
antérieures à la répartition, 3 045 carrières sans régime actif) : ceux de la
note.

| | note : version, éteinte | refait : version, éteinte | constat |
|---|---|---|---|
| ensemble de 1955, surcote | 14,0 ; 16,0 | 14,06 ; 15,99 | **conforme** |
| femmes de 1955 | 14,8 ; 17,4 | 14,76 ; 17,44 | **conforme** |
| hommes de 1955 | 13,3 ; 14,4 | 13,29 ; 14,40 | **conforme** |
| ensemble de 1950 | 11,3 ; 15,8 | 11,28 ; 15,79 | **conforme** |
| femmes de 1950 | 11,6 ; 17,0 | 11,58 ; 17,00 | **conforme** |
| hommes de 1950 | 10,9 ; 14,5 | 10,96 ; 14,48 | 11,0 et non 10,9 |
| ensemble de 1955, à l'âge légal | 38,4 ; 37,3 | 38,40 ; 37,30 | **conforme** |
| ensemble de 1955, entre les deux âges | 26,8 ; 28,2 | 26,77 ; 28,12 | 28,1 et non 28,2 |
| femmes de 1955, à l'âge légal | 50,8 ; 48,7 | 50,78 ; 48,68 | **conforme** |
| femmes de 1955, entre les deux âges | 23,2 ; 25,6 | 23,18 ; 25,65 | **conforme** |
| ensemble de 1950, à l'âge légal | 43,8 ; 41,2 | 43,88 ; 41,24 | 43,9 et non 43,8 |
| ensemble de 1950, entre les deux âges | 26,7 ; 29,4 | 26,68 ; 29,35 | 29,3 et non 29,4 |
| État, retraités de 2024, surcote | 23,4 ; 30,1 | 23,52 ; 30,30 | à 0,1 et 0,2 point ; à l'année de naissance plutôt qu'à la génération simulée, 23,11 ; 29,28 |
| État, liquidants de 2024 | 50,6 ; 50,2 | 50,64 ; 50,25 | **conforme** |
| régime général, liquidants de 2024 | 10,9 ; 13,3 | 11,49 ; 13,92 | **écart** de 0,6 point des deux côtés, pour la même baisse (2,4 points) |
| régime général, retraités de 2024 | 7,8 ; 9,3 | 7,81 ; 9,32 | **conforme** |
| liquidants de 2024 partis à 62 ans | 58,4 ; 56,9 | 58,42 ; 56,96 | 57,0 et non 56,9 |
| âge moyen des liquidants de 2024 | 62,63 ; 62,68 | 62,63 ; 62,68 | **conforme** |
| retraitées de 2020, surcote ; de 70 à 74 ans | 7,7 et 11,8 ; 10,2 et 17,0 | 7,74 et 11,80 ; 10,21 et 16,99 | **conforme** |
| retraités de 2020 ; de 70 à 74 ans | 7,4 et 12,6 ; 9,1 et 16,7 | 7,39 et 12,55 ; 9,13 et 16,73 | **conforme**, à l'arrondi |
| fonctionnaires civils parmi les retraitées surcotées ; les retraités | 42,6 et 27,4 ; 45,9 et 32,0 | 42,59 et 27,43 ; 45,86 et 31,98 | **conforme** |

Les cinq écarts au dixième (0,05 à 0,08 point) ne changent rien à ce que la note
en tire ; leur cause n'est pas établie : la session a simulé sur un arbre d'avant
la version (a229ec1), moi sur 9689bd99. L'écart du régime général, 0,6 point, tient
au champ : je compte le groupe `regime_general` de la population, et la note ne dit
pas quelles carrières elle range au régime général ; il ne touche pas la
conclusion, 11,5 ou 10,9 % contre 18,9 % à la Cnav. *Poids : faible.* Non refaits :
l'État année par année de 2020 à 2023 et en 2025, la CNRACL, la décote des
liquidants du régime général de 2024, les pensions moyennes et l'écart de
Kolmogorov, et la troisième pesée (la part du salariat figée).

## 3. Les tests

Sur `main` à 730a6bb, `pip install -e '.[dev]'` fait par le hook :

- `python -m pytest -m rapide` : 4 185 réussis, 33 sautés, en 2 min 22 s ;
- `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 3 990 réussis, 228 sautés,
  en 1 min 8 s ;
- `python -m pytest tests/test_grille_large.py` : 98 réussis, en 2 min 21 s ;
- les trois tests que l'étape touche, sous la garde des présomptions décalées
  (`PRESOMPTIONS_DECALEES=1 PYTEST_SANS_XDIST=1`, `-k` sur leurs noms) : 3 réussis.

**Conforme.** Une précision : `test_grille_large.py` n'est pas du niveau rapide
(`tests/conftest.py`, ligne 85) ; la suite rapide sous la garde ne l'éprouve donc
pas, d'où la quatrième commande, que la note dit aussi avoir lancée. La session
d'orchestration signale, sur `main` après 7621be3 (file K), un échec de
`tests/test_simulateur.py`, le paquet `moteur/donnees.json` restant à refaire :
étranger à l'étape, postérieur à 730a6bb, il n'est pas dans mes essais.

## 4. Ce que les sources ne tranchent pas

**Déclaré, conforme** : les générations d'avant 1950 prennent la part des nés en
1950, celles d'après 1953 celle des nés en 1953, et toutes les attentes des nés en
1953 (convention de la note et du code ; « Ce qui reste », points 1 et 2, le second
au propriétaire) ; l'année où la génération atteint l'âge légal date la part de sa
caisse, deux à quatre ans avant ses départs ; la part de chaque catégorie suit
celle de tous les départs de sa caisse ; la part se calcule au poids des retraités
de 2020, la mesure pèse chaque génération au sien ; pas de départ après 67 ans ;
les fonctionnaires parmi les surcotés (« Ce qui reste », point 3).

**Non déclaré** :

1. *La rupture de 2011-2012 du tableau 103.* Sa note 154 (p. 182) dit qu'en 2012
   « l'effectif de nouveaux retraités avait connu une forte baisse (-34 %),
   principalement liée au contrecoup des départs anticipés massifs pour parents
   de trois enfants de 2011 », d'où une part de surcotés relevée. Le code prend
   28 % en 2011 et 36 % en 2012 tels quels : le sédentaire de l'État né en 1951
   (60 ans en 2011) surcote pour 48,48 × 28 / 35 = 38,8 %, celui né en 1952
   (60 ans et 9 mois, fin 2012) pour 44,7 %, celui né en 1953 pour 42,9 %, celui
   né en 1955 pour 38,8 % (les trois derniers, mon recompte de la population,
   point 2). La suite non monotone vient de la source, et la note
   ne le dit pas. *Poids : faible* (deux années de naissance, deux points au plus
   sur le sédentaire de l'État ; celle de 1955, que la mesure juge, tient au creux
   de 2017, 28 %, que l'EACR voit aussi : 29,6 % des liquidants de l'État en 2017,
   table H).
2. *La cible et le juge ne sont pas le même chiffre de l'EIR.* Le code vise la part
   des résidents, conditions inconnues comprises au dénominateur (nés en 1953 :
   14,2 % des femmes, 14,4 % des hommes) ; la mesure juge contre toutes les
   résidences, parmi les conditions connues (14,31 et 14,65 %). *Poids : faible*,
   0,1 à 0,25 point, une part de l'écart des hommes de 1955 (13,3 contre 14,6).
3. *Le niveau du tableau 103 n'est pas celui du B-3 du même jaune* : en 2025,
   (41 812 × 42,7 % + 2 545 × 16,5 % + 2 747 × 11,9 %) / 47 104 = 39,5 % des
   nouvelles pensions civiles surcotent au B-3 (p. 210 : ancienneté, motifs
   familiaux, invalidité), 35 % au tableau 103 ; la table H de l'EACR en voit
   38,9 % en 2024, le tableau 103 36 %. Le code ne prend que le rapport de chaque
   année à 2025 : l'écart de niveau s'annule s'il est constant, ce que rien ne
   dit. *Poids : négligeable à faible.*
4. *Le pilote des mesures est hors du dépôt.* Les deux tableaux de la note sortent
   d'« un pilote hors du dépôt » : rien, dans le dépôt, ne permet de les refaire
   tels quels. Le propriétaire veut pouvoir « justifier avec preuve à l'écrit » ;
   pour ces chiffres, la preuve est la note seule, que mon pilote, lui aussi hors
   du dépôt, recoupe (point 2). *Poids : moyen* au regard de cette exigence.
5. *L'accord de l'État sur ses liquidants tient au champ.* La ligne « État,
   liquidants de 2020 à 2025 » du second tableau met tous les liquidants civils
   du modèle en regard des seuls départs pour ancienneté de 2025 (B-3, p. 210 :
   42,7 % ; de même la CNRACL, B-3bis, p. 211 : 24,3 %). La note dit ce champ, et
   que la population prête la part de l'ancienneté à toutes ses carrières ; mais
   le chiffre de même champ est au dépôt et n'est pas montré : la table H de
   l'EACR voit surcoter 36,6, 38,4, 38,2, 40,1 et 38,9 % de tous les liquidants
   civils de l'État de 2020 à 2024, le tableau 103 de 34 à 38 % ; le modèle, 50,6 %
   en 2024 (refait ici), 41,6 % en moyenne de 2020 à 2025. L'accord de 41,6 à 42,7
   est celui de deux champs différents. *Poids : faible.*

Hors du périmètre de l'étape, *négligeable* : l'en-tête de
`departs_generations.csv` dit encore « l'un des trois tableaux » et ne décrit pas
le tableau `residence`, dont le code tire sa cible, quand le gabarit de
`scripts/verifier_donnees.py` (ligne 8289) en nomme quatre ; celui de
`caracteristiques_fonction_publique.csv` ne décrit pas ses tableaux 101 à 105.

## 5. Ce que la session a dit au propriétaire

| Phrase, mot pour mot | Constat |
|---|---|
| « la part des salariés qui partent plus tard pour toucher un bonus (la surcote) ne recompte plus celle des fonctionnaires » | **conforme** : à chaque année de naissance, tous les retraités du sexe surcotent la part de l'EIR, fonctionnaires civils compris, et non plus la leur en plus (femmes nées en 1955 : 5,10 + 9,10 = 14,2 %, contre 6,40 + 10,27 = 16,67 % avant ; point 2) |
| « et chaque génération a la sienne » | **conforme, simplifié** : chaque année de naissance a sa part, mais la cible ne change qu'entre 1950 et 1953 ; avant, celle de 1950, après, celle de 1953, convention que la phrase tait. *Poids : négligeable* |
| « Les nés en 1950 et en 1955 retrouvent les chiffres de l'enquête de la DREES (11 % et 14 %, contre 16 % avant) » | **écart.** L'enquête ne voit pas les nés en 1955 : la génération 1955 du modèle se juge sur les nés en 1953 (`GENERATIONS_DES_DEPARTS`), ce que la note dit et la phrase non. Et « 11 % » est le chiffre du modèle (11,3), non celui de l'enquête (11,8, soit 12 %) : la génération 1950 s'en approche sans le retrouver. Les chiffres du modèle, eux, se refont : 11,28 et 14,06 %, contre 15,79 et 15,99 % avant (point 2). *Poids : faible* |
| « et l'État les siens (23 % de ses retraités de 2024, contre 30 % avant) » | **conforme** : 23,52 % refait, 30,30 % avant ; l'EACR, 22,58 % |
| « les nouveaux retraités du privé de 2024 prennent trop peu ce bonus (11 % dans le modèle, 19 % à la Cnav) » | **conforme** à l'arrondi : Cnav, 18,87 % (table H) ; modèle, 10,9 % dans la note, 11,49 % refait (point 2) |
| « surtout parce que personne n'y part après 67 ans » | **écart.** La note donne deux causes — pas de départ après 67 ans, et pas de source sur les générations d'après 1953, qui gardent la surcote des nés en 1953 — et dit que la première « en explique une part », non l'essentiel. Une borne, à la table B de l'EACR : 47 732 des 648 346 liquidants de la Cnav en 2024 ont 68 ans et plus, 7,36 %. Pour combler l'écart — 8,0 points dans la note, 7,4 dans ma mesure —, il faudrait que tous, ou presque, partent avec une surcote ; au taux des nés en 1953 partis à 67 ans et plus (34,6 %, EIR), ce serait quelque 2,5 points. « Surtout » n'est pas établi. *Poids : moyen* : la phrase oriente la décision que la note réserve au propriétaire (« Ce qui reste », point 2) |
| « et les femmes partent trop souvent à 62 ans (défaut connu de leur durée de carrière) » | **conforme** : 50,78 % des femmes de la génération 1955 du modèle partent à l'âge légal, 62 ans pour elles (refait), contre 37,5 % des femmes nées en 1953 dans l'EIR, dont l'âge légal est 61 ans et 2 mois. « Défaut connu » : **conforme**, le calage de la durée des femmes est un point ouvert de plusieurs notes (`2026-10-25-etape-14-carrieres-allongees.md`, « Ce qui reste » ; `2026-11-03-etape-14-taux-plein-entre-les-deux-ages.md`, point 3) |
