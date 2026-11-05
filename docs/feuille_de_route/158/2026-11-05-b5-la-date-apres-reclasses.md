# B5 : la date d'effet écrite après « reclassés », lue par le lecteur des reclassements

Vague 11, B5, le 5 novembre 2026. Le premier point de la tâche : les dates d'effet que les
lecteurs ne lisent pas, à commencer par les reclassements datés après « reclassés »
(`2026-11-05-rattacher-plus-sans-deviner.md`, § 4 ; `2026-11-05-b-bis-preuves-de-r-b4.md`,
« Ce qui reste »). Tout ce qui suit a été lu pendant la session dans l'index LEGI du dépôt
récupéré par `dila_index.py legi --recuperer` (dump `Freemium_legi_global_20250713-140000`,
incréments jusqu'au 20261102-213929), par `dila_cherche.py legi --texte <article>`.

## Le défaut

`date_effet` (`scripts/fetch/dila_legi_reclassements.py`) ne lisait la date du reclassement
que dans « A compter du … », « à partir du … », « à la date du … », ou juste avant le verbe
(« sont, au 1er août 1993, intégrés »). Une phrase qui l'écrit après le verbe (« sont
reclassés, au 1er janvier 2017, conformément au tableau ») laissait `effet` vide : le tableau
valait alors à l'entrée en vigueur de l'article (`debut`), que le texte contredit.

## Le compte

Dans `reclassements/tableaux.csv` (450 tableaux), 30 tableaux sans `effet` écrivent la date
juste après le verbe : 25 « sont reclassés, au », 4 « sont reclassés au », 1 « sont nommés
et reclassés, au » (n° 2017-297). La note du 5 novembre en comptait 26 (22 et 4) parmi les
tableaux que le chaînage laissait sans date ; le compte ci-dessus part du lecteur, sur tous
les tableaux. Six autres écrivent la date d'effet sans ambiguïté sous une autre forme :
« reclassés avec effet au » (3), « Avec une date d'effet au » (2), « reclassés dans le grade
de dessinateur projeteur en chef au 1er août 1996 » (1). Chacune des 36 phrases a été
retrouvée mot pour mot dans l'article, à la version que porte la donnée (même `debut`) ;
toutes ces versions sont en vigueur sauf celles des n° 88-1077 et 2010-1139 (closes au
1er janvier 2017), comme la donnée le dit.

## Les 36 dates, lues au texte

La valeur attendue est la date que la phrase écrit, mise en AAAA-MM-JJ (« 1er janvier 2017 »
→ 2017-01-01). Vingt-deux précèdent l'entrée en vigueur de l'article (reclassement
rétroactif : le n° 2020-1362, en vigueur le 2020-11-09, reclasse au 1er janvier 2017), dix
la redisent, quatre la suivent (n° 2016-1880 ; n° 2010-1139, art. 30 et 31 ; n° 96-980,
art. 10, un an après).

1. n° 95-691, art. 6, tableau 1 (LEGIARTI000006479000, version du 1995-05-11, fin : en vigueur) → **1993-08-01** :
   « Les infirmiers de classe normale régis par le décret du 14 mars 1990 susvisé sont reclassés, au 1er août 1993, dans le nouveau grade d'infirmier de classe normale selon le tableau de correspondance ci-après »
2. n° 95-720, art. 15, tableau 1 (LEGIARTI000006479055, version du 1995-08-01, fin : en vigueur) → **1995-08-01** :
   « Les fonctionnaires titulaires des grades de greffier et de premier greffier, régis par le décret du 30 avril 1992 susvisé et placés dans l'une des positions prévues à l'article 32 de la loi du 11 janvier 1984 susvisée, sont reclassés, au 1er août 1995, dans le troisième grade conformément au tableau de correspondance ci-après »
3. n° 97-571, art. 3, tableau 1 (LEGIARTI000006484915, version du 1995-01-01, fin : en vigueur) → **1995-01-01** :
   « Les ingénieurs en chef sont reclassés au 1er janvier 1995, conformément au tableau suivant »
4. n° 98-280, art. 4, tableau 1 (LEGIARTI000006506641, version du 1996-08-01, fin : en vigueur) → **1996-08-01** :
   « Les professeurs techniques hors classe régis par le décret du 19 décembre 1996 susvisé sont reclassés, au 1er août 1996, dans le grade de professeur technique hors classe selon le tableau de correspondance ci-après »
5. n° 98-416, art. 4, tableau 1 (LEGIARTI000006507125, version du 1996-09-01, fin : en vigueur) → **1996-09-01** :
   « Les professeurs des écoles nationales d'art hors classe sont reclassés au 1er septembre 1996 conformément au tableau de correspondance ci-après »
6. n° 2016-1798, art. 27, tableau 1 (LEGIARTI000033667099, version du 2017-01-01, fin : en vigueur) → **2017-01-01** :
   « Les attachés territoriaux ainsi que les fonctionnaires détachés dans le cadre d'emplois des attachés territoriaux sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
7. n° 2016-1881, art. 25, tableau 1 (LEGIARTI000033708276, version du 2017-01-01, fin : en vigueur) → **2017-01-01** :
   « Les attachés d'administrations parisiennes ainsi que les fonctionnaires détachés dans leur corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
8. n° 2016-1880, art. 11, tableau 1 (LEGIARTI000033711235, version du 2016-12-29, fin : en vigueur) → **2017-01-01** :
   « Les conseillers territoriaux des activités physiques et sportives ainsi que les fonctionnaires détachés dans le cadre d'emplois des conseillers territoriaux des activités physiques et sportives sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
9. n° 2017-194, art. 23, tableau 1 (LEGIARTI000034054785, version du 2017-02-18, fin : en vigueur) → **2017-01-01** :
   « Les ingénieurs des travaux de la météorologie ainsi que les fonctionnaires détachés dans ce corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
10. n° 2017-194, art. 46, tableau 1 (LEGIARTI000034054815, version du 2017-02-18, fin : en vigueur) → **2017-01-01** :
   « Les ingénieurs des travaux géographiques et cartographiques de l'Etat ainsi que les fonctionnaires détachés dans ce corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
11. n° 2017-194, art. 68, tableau 1 (LEGIARTI000034054841, version du 2017-02-18, fin : en vigueur) → **2017-01-01** :
   « Les ingénieurs de l'industrie et des mines ainsi que les fonctionnaires détachés dans ce corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
12. n° 2017-194, art. 117, tableau 1 (LEGIARTI000034054901, version du 2017-02-18, fin : en vigueur) → **2017-01-01** :
   « Les ingénieurs des travaux publics de l'Etat ainsi que les fonctionnaires détachés dans ce corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
13. n° 2017-194, art. 144, tableau 1 (LEGIARTI000034054935, version du 2017-02-18, fin : en vigueur) → **2017-01-01** :
   « Les ingénieurs de l'agriculture et de l'environnement ainsi que les fonctionnaires détachés dans ce corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
14. n° 2017-297, art. 13, tableau 1 (LEGIARTI000034158145, version du 2017-03-10, fin : en vigueur) → **2017-01-01** :
   « Les ingénieurs des systèmes d'information et de communication ainsi que les fonctionnaires détachés dans le corps des ingénieurs des systèmes d'information et de communication sont nommés et reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
15. n° 2017-310, art. 16, tableau 1 (LEGIARTI000034167768, version du 2017-03-12, fin : en vigueur) → **2017-01-01** :
   « Les ingénieurs territoriaux ainsi que les fonctionnaires détachés dans ce cadre d'emplois sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
16. n° 2017-418, art. 18, tableau 1 (LEGIARTI000034302299, version du 2017-03-30, fin : en vigueur) → **2017-01-01** :
   « Les chefs de travaux d'art sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
17. n° 2017-593, art. 6, tableau 1 (LEGIARTI000034460214, version du 2017-04-24, fin : en vigueur) → **2017-01-01** :
   « Les attachés principaux des systèmes d'information et de communication de 1re et de 2e classe ainsi que les fonctionnaires détachés dans ce corps sont reclassés au 1er janvier 2017, conformément au tableau de correspondance ci-après »
18. n° 2017-593, art. 7, tableau 1 (LEGIARTI000034460216, version du 2017-04-24, fin : en vigueur) → **2017-01-01** :
   « Les secrétaires des affaires étrangères, les attachés des systèmes d'information et de communication ainsi que les fonctionnaires détachés dans ces corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
19. n° 2017-1350, art. 15, tableau 1 (LEGIARTI000035590914, version du 2017-09-01, fin : en vigueur) → **2017-09-01** :
   « Les professeurs de sport ainsi que les fonctionnaires détachés dans le corps des professeurs de sport sont reclassés, au 1er septembre 2017, conformément au tableau de correspondance suivant »
20. n° 2017-1351, art. 14, tableau 1 (LEGIARTI000035591052, version du 2017-09-21, fin : en vigueur) → **2017-09-01** :
   « Les conseillers d'éducation populaire et de jeunesse ainsi que les fonctionnaires détachés dans le corps des conseillers d'éducation populaire et de jeunesse sont reclassés, au 1er septembre 2017, conformément au tableau de correspondance suivant »
21. n° 2017-1352, art. 15, tableau 1 (LEGIARTI000035591460, version du 2017-09-01, fin : en vigueur) → **2017-09-01** :
   « Les conseillers techniques et pédagogiques supérieurs ainsi que les fonctionnaires détachés dans le corps des conseillers techniques et pédagogiques supérieurs sont reclassés, au 1er septembre 2017, conformément au tableau de correspondance suivant »
22. n° 2017-1376, art. 20, tableau 1 (LEGIARTI000035603897, version du 2017-09-23, fin : en vigueur) → **2017-01-01** :
   « Les ingénieurs d'études sanitaires ainsi que les fonctionnaires détachés dans ce corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
23. n° 2017-1404, art. 20, tableau 1 (LEGIARTI000035646727, version du 2017-01-01, fin : en vigueur) → **2017-01-01** :
   « Les fonctionnaires appartenant au corps des attachés économiques ou détachés dans ce corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
24. n° 2017-1405, art. 16, tableau 1 (LEGIARTI000035646835, version du 2017-09-28, fin : en vigueur) → **2017-01-01** :
   « Les attachés statisticiens de l'Institut national de la statistique et des études économiques ainsi que les fonctionnaires détachés dans le corps des attachés statisticiens de l'Institut national de la statistique et des études économiques sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
25. n° 2018-188, art. 13, tableau 1 (LEGIARTI000036729702, version du 2018-03-22, fin : en vigueur) → **2017-01-01** :
   « Les administrateurs adjoints de 2e classe et les administrateurs adjoints de 1re classe du Conseil économique, social et environnemental, ainsi que les fonctionnaires détachés dans le corps des administrateurs adjoints en fonctions à la date du présent décret sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
26. n° 2018-282, art. 4, tableau 1 (LEGIARTI000036821740, version du 2018-04-21, fin : en vigueur) → **2017-01-01** :
   « Les inspecteurs des affaires maritimes intégrés dans le corps des ingénieurs des travaux publics de l'Etat sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
27. n° 2018-282, art. 4, tableau 2 (LEGIARTI000036821740, version du 2018-04-21, fin : en vigueur) → **2017-01-01** :
   « Les inspecteurs des affaires maritimes intégrés dans le corps interministériel des attachés d'administration de l'Etat sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
28. n° 2018-619, art. 19, tableau 1 (LEGIARTI000037214195, version du 2018-07-19, fin : en vigueur) → **2017-01-01** :
   « Les ingénieurs-économistes de la construction et les ingénieurs des services culturels et du patrimoine ainsi que les fonctionnaires détachés dans ces corps sont reclassés, au 1er janvier 2017, conformément au tableau de correspondance suivant »
29. n° 2020-1362, art. 9, tableau 1 (LEGIARTI000042506911, version du 2020-11-09, fin : en vigueur) → **2017-01-01** :
   « Les membres des corps des traducteurs et les agents détachés dans ces corps sont reclassés au 1er janvier 2017 conformément au tableau de correspondance ci-dessous »
30. n° 2020-1435, art. 9, tableau 1 (LEGIARTI000042559783, version du 2020-11-26, fin : en vigueur) → **2017-09-01** :
   « Les professeurs techniques de la protection judiciaire de la jeunesse et les agents détachés dans ce corps sont reclassés, au 1er septembre 2017, conformément au tableau de correspondance suivant »
31. n° 2017-182, art. 3, tableau 1 (LEGIARTI000034036681, version du 2017-02-16, fin : en vigueur) → **2017-01-01** :
   « Les fonctionnaires relevant du premier grade mentionné à l'article 2 des décrets du 30 avril 2012 susvisés sont reclassés avec effet au 1er janvier 2017 dans leur grade conformément au tableau de correspondance suivant »
32. n° 2017-182, art. 3, tableau 3 (LEGIARTI000034036681, version du 2017-02-16, fin : en vigueur) → **2017-01-01** :
   « Les fonctionnaires relevant du troisième grade mentionné au même article sont reclassés avec effet au 1er janvier 2017 dans leur grade conformément au tableau de correspondance suivant »
33. n° 88-1077, art. 50-1, tableau 1 (LEGIARTI000022913217, version du 2010-12-01, fin : 2017-01-01) → **2010-12-01** :
   « I.-Les membres du corps des infirmiers qui ont opté pour leur maintien dans ce corps dans les conditions définies aux I et II de l'article 30 du décret n° 2010-1139 du 29 septembre 2010 portant statut particulier du corps des infirmiers en soins généraux et spécialisés de la fonction publique hospitalière sont reclassés avec effet au 1er décembre 2010 selon les tableaux de correspondance suivants »
34. n° 2010-1139, art. 30, tableau 1 (LEGIARTI000022869520, version du 2010-10-01, fin : 2017-01-01) → **2010-12-01** :
   « Avec une date d'effet au 1er décembre 2010, les personnels mentionnés au I qui auront accepté la proposition d'intégration prévue au II sont reclassés conformément aux tableaux de correspondance ci-après »
35. n° 2010-1139, art. 31, tableau 1 (LEGIARTI000022869523, version du 2010-12-01, fin : 2017-01-01) → **2012-07-01** :
   « Avec une date d'effet au 1er juillet 2012, les personnels mentionnés au I qui auront accepté la proposition d'intégration prévue au II sont reclassés conformément aux tableaux de correspondance suivants »
36. n° 96-980, art. 10, tableau 1 (LEGIARTI000006483170, version du 1995-08-01, fin : en vigueur) → **1996-08-01** :
   « Les titulaires du grade provisoire de chef dessinateur prévu à l'article 9 ci-dessus, placés dans une situation prévue à l'article 32 de la loi du 11 janvier 1984 susvisée, sont reclassés dans le grade de dessinateur projeteur en chef au 1er août 1996, conformément au tableau de correspondance ci-après »

## Ce qui change

- Le lecteur : trois motifs de plus dans `EFFETS` — la date juste après « reclassés » ou
  « intégrés » ; « avec effet au » et « Avec une date d'effet au », où qu'ils soient ;
  « reclassés dans le grade de … au <date> ». Tests, vus rouges puis verts :
  `test_la_date_du_reclassement_est_celle_que_la_phrase_ecrit` (huit phrases de plus, dont
  une qui reste sans date) et `test_la_date_qui_suit_le_verbe_est_la_date_du_reclassement`
  (les 36 dates ; aucun autre tableau sans date n'écrit la sienne après le verbe).
- La donnée : la colonne `effet` de `tableaux.csv` refaite par `date_effet` sur la phrase
  stockée, que le lecteur écrit telle qu'il l'a lue : 36 cases vides prennent leur date ;
  les 414 autres se refont à l'identique. Le lecteur n'a pas été relancé en entier : voir
  le candidat ci-dessous.
- Le chaînage, relancé (`dila_legi_chainage.py`) : les 76 groupes des 36 tableaux portent
  leur date (`date_lue` effet). Aucun rattachement de plus (13 groupes rattachés, 849
  déclarés) : les 25 tableaux de l'État qui attendaient leur date s'arrêtent à l'étape
  suivante (« la phrase ne nomme pas le statut du corps reclassé, et le texte n° … n'est pas
  lui-même un statut », « plusieurs coupes du libellé », « le Noyau RH ne cite, la veille ni
  le jour du 1995-08-01, … »). Les tableaux de l'État déclarés faute de date passent de 183
  à 158 (`test_aucune_phrase_restee_sans_date_ne_s_ouvre_sur_une_date`).
- Ni `lignes.csv` ni sa certification ne bougent ; le paquet (`moteur/donnees.json`) ne lit
  pas les reclassements : reconstruit, inchangé.

## Ce que le texte ne date pas, déclaré

Une date écrite après un autre mot que le verbe du reclassement ne se lit pas :

- « nommés au » : n° 97-1029, art. 4 (LEGIARTI000006505207, depuis le 1995-08-01) :
  « […] sont nommés au 1er août 1995 dans le grade de secrétaire de protection de classe
  normale […] » ; n° 98-268, art. 17 (LEGIARTI000006506606, du 2003-06-21 au 2012-09-01) :
  « Les techniciens supérieurs et techniciens supérieurs principaux de l'industrie et des
  mines sont nommés au 1er août 1995 dans le nouveau grade de technicien supérieur principal
  et reclassés conformément aux dispositions ci-dessous ». Point non tranché : la date de la
  nomination vaut-elle pour « reclassés », coordonné ? Lecture a : oui, le reclassement
  accompagne la nomination (1995-08-01) ; lecture b : le texte ne date que la nomination, et
  le tableau garde l'entrée en vigueur de l'article. Pour le n° 97-1029, les deux donnent le
  1995-08-01 ; pour la version du n° 98-268 que la donnée porte, 1995-08-01 ou 2003-06-21.
  *Candidat.*
- « placés au » : n° 2001-325, art. 14 (LEGIARTI000006567682, depuis le 2001-04-15) : « Les
  bibliothécaires de 1re et de 2e classes, placés au 1er janvier 1997 dans l'une des
  positions prévues à l'article 32 de la loi du 11 janvier 1984 susvisée, sont reclassés
  dans le grade de bibliothécaire conformément au tableau » : la date est celle de la
  position ; le texte ne date pas le reclassement. Gardé dans les tests, sans date.
- L'arrêté du 18 avril 1989, art. 4 (LEGIARTI000006718191, hospitalière, depuis le
  1989-01-01) : « Les fonctionnaires hospitaliers appartenant à un grade ou emploi classé
  dans les groupes IV, V et VI au 1er janvier 1989 […] » date un classement, non le
  reclassement ; la version commence d'ailleurs ce jour-là.

## Candidat : le lecteur relancé ne refait pas la donnée

Relancé sur l'index publié (incréments jusqu'au 20261102-213929), `dila_legi_reclassements.py`
écrit 610 textes et 540 tableaux, non 450 : des textes entrent (n° 76-195, 83-1033, 91-393…),
d'autres sortent (n° 95-370, 2006-1732, 2007-1333…), et le diff de `lignes.csv` compte
5 477 lignes.
La donnée du dépôt ne vient donc pas de l'index publié tel qu'il est. Hors de cette tâche :
rien n'a été écrit de cette relance (fichiers rendus à leur état), et c'est pourquoi la
colonne `effet` a été refaite seule. À comprendre avant toute relance du lecteur.

## Ce qui reste

Les 97 versions hors du motif (durées d'échelon, point 5 de
`2026-11-03-retouches-de-la-relecture-r-b2-bis.md`) : non entamées, une étape à elles.
Le reste du bloc « Reprise » est inchangé.

*Relu le 5 novembre 2026 (R-B5, `2026-11-05-relecture-r-b5.md`) : les 36 dates sont exactes ; deux écarts à cette note : « nommés au » (n° 98-268, art. 17) et « placés au » (n° 2001-325, art. 14) sont datés par un autre article du même décret, et le candidat du lecteur relancé n'est pas une divergence (rien ne sort, 90 tableaux s'ajoutent).*
