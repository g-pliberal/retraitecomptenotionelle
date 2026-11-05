# Relecture de B : rattacher plus sans deviner

Vague 10, R-B4, le 5 novembre 2026. Relecture indépendante du commit 7114ee4 (B, note
`2026-11-05-rattacher-plus-sans-deviner.md`). Tout ce qui suit a été rouvert pendant la
relecture : l'index LEGI du dépôt (`dila_index.py legi --recuperer`, incrément
20261102-213929, le même que B), par `dila_cherche.py --texte`, `--num … --titre`, `--le`,
ou une lecture directe de la table `doc` ; les fichiers du Noyau RH (`grilles/etat/`) et des
grilles du LEGI (`grilles/etat_legi/`). Rien n'est repris de la note de B ni de la mémoire de
la session.

**Verdict : aucune erreur de donnée.** Pour les 13 grades relus (dix tirés au sort et les
trois que B cite), et au-delà pour les 43 que le seul sommet rattache, la grille retenue a,
sur toute la période, le nombre d'échelons que donne le texte. La règle n + 1 ne devine pas
(point 1), mais elle ne lit pas le statut : 34 des 43 ont un article qui compte n + 1
échelons, que la preuve ne cite pas ; 9 n'en ont pas dans l'index, et leur nombre ne repose
que sur le texte de la grille. Le n° 91-783, le n° 60-403 et le retrait de l'annexe II du
n° 94-1016 sont conformes. Les tests sont vus rouges sur le code d'avant, verts sur `main`,
et les CSV sont le produit exact du script. Trois écarts faibles, aucun grave ni moyen ;
trois candidats.

## 0. Le tirage

Les 45 grades gagnés sont les 45 clés (texte, article, tableau, groupe) de
`chainage/durees.csv` rattachées avec une preuve « sommet non écrit » ; ôtées les deux du
n° 91-783 (LEGIARTI000006461873), il en reste 43, ce que dit B. Triées par clé, ôtées les
trois que B cite, les 40 autres sont tirées par `random.Random(20261105).sample(…, 10)` :
n° 68-270, art. 21 (Ingénieur, Ingénieur en chef, Chef mécanicien, Maître graveur) ;
n° 2011-1672, art. 8 (Contrôleur divisionnaire) ; n° 2011-1673, art. 8, deux versions
(Technicien des installations, deux fois) ; n° 91-105, art. 18 (Réviseur) ; n° 2013-1146,
art. 9 (Lieutenant de port de première classe, version de 2016) ; n° 58-778, art. 16
(Directeur départemental adjoint).

## 1. La règle « n + 1 » devine-t-elle ?

**Ce qu'elle prouve.** `Depot.sommet_non_ecrit` (dila_legi_chainage.py, l. 520) demande
trois choses : la phrase du tableau dit le temps passé dans chaque échelon
(`TEMPS_DANS_L_ECHELON`), le n-ième rang porte une durée, la grille a exactement les échelons
1 à n + 1, le dernier ordinaire (au LEGI, numéroté n + 1 à toutes ses versions, non le
spécial ; au noyau, de nature vide à chaque date). Qu'un échelon n + 1 existe, c'est le
texte du tableau qui le dit (« le temps passé dans chacun des échelons […] pour accéder à
l'échelon immédiatement supérieur », n° 68-270) ; qu'il soit le dernier, c'est la grille.
Rien n'est inventé. Mais l'article du statut qui compte les échelons n'entre ni dans la règle
ni dans la preuve : B ne l'a lu que pour ses trois exemples et les deux grades du n° 91-783,
et sa note le dit (« les autres reposent sur la règle et ses tests »).

**Les 13 relus, au texte, à la version en vigueur sur la période rattachée.** Chaque fois :
le dernier rang du tableau et sa durée ; l'article qui compte les échelons ; la grille.

| Grade | Tableau | Le nombre d'échelons | La grille | |
|---|---|---|---|---|
| Ingénieur (n° 90-973) | art. 12, LEGIARTI000006459943 (2000-10-06 → 2017-03-01) : « Ingénieur 9e échelon 3 ans 2 ans 6 mois » | art. 3, LEGIARTI000006459927 (mêmes dates) : « le grade d'ingénieur, qui comporte dix échelons » | arrêté du 28 septembre 2000, art. 1er, LEGIARTI000019669918 (2000-10-07 → 2017-01-01) : « Ingénieur 10e échelon 901 […] 1er échelon 473 » | conforme |
| Directeur du travail (n° 2003-770) | art. 13, LEGIARTI000023593821 (2011-02-18 → 2016-05-09) : « Directeur du travail 5e échelon 3 ans 2 ans 3 mois » | art. 2, LEGIARTI000023593810 (mêmes dates) : « Le grade de directeur du travail qui comprend six échelons » | noyau 00568 : rangs 1 à 5 (801 à 1015), 6 hors échelle A (06022, nature vide), du 2000-08-07 au 2016-12-31 ; le rang 7, fonctionnel, finit le 2011-02-17 | conforme |
| Classe exceptionnelle, annexe I (n° 94-1016) | art. 9, LEGIARTI000006476438 (depuis 1994-11-26) : « Classe exceptionnelle 6e échelon 4 ans 3 ans » | art. 2, LEGIARTI000006476418 : « sept échelons pour les corps mentionnés à l'annexe I » | arrêté du 24 novembre 2006, art. 1er, LEGIARTI000019528377 (depuis 2006-11-26) : « annexe I […] Classe exceptionnelle 7e échelon 612 » | conforme |
| Ingénieur (n° 68-270) | art. 21, LEGIARTI000029572482 (depuis 2014-11-01) : « 7e échelon 3 ans » | art. 6, LEGIARTI000029572468 (depuis 2014-11-01) : « Le grade d'ingénieur comprend huit échelons » | n° 2014-1165, art. 1er, LEGIARTI000029563926 (depuis 2014-11-01) : « Ingénieur 8e échelon 811 » | conforme |
| Ingénieur en chef (n° 68-270) | idem : « 3e échelon 5 ans » | idem : « quatre échelons » | idem : « Ingénieur en chef 4e échelon 1015 » | conforme |
| Chef mécanicien (n° 68-270) | idem : « 11e et 12e échelons 4 ans » | idem : « treize échelons » | idem : « Chef mécanicien 13e échelon 614 » | conforme |
| Maître graveur (n° 68-270) | idem : « 1er, 2e, 3e, 4e et 5e échelons 2 ans » | idem : « six échelons » | idem : « Maître graveur 6e échelon 741 » | conforme |
| Contrôleur divisionnaire (n° 2011-1672) | art. 8, LEGIARTI000042563210 (depuis 2020-12-01) : « 9e échelon 3 ans » | art. 2, LEGIARTI000024875248 (depuis 2011-12-01) : « doté de dix échelons » | n° 2013-1070, art. 3, LEGIARTI000042563267 (depuis 2020-12-01) : « 10 e 707 » | conforme |
| Technicien des installations (n° 2011-1673, 2012-2017) | art. 8, LEGIARTI000024876144 (2011-12-01 → 2020-12-01) : « 13e et 12e échelons 4 ans » | art. 2, LEGIARTI000024876132 (mêmes dates) : « doté de quatorze échelons » | n° 2011-1683, art. 8, LEGIARTI000024878121 (2011-12-01 → 2013-06-19) : « 14e 622 » ; n° 2013-1070, art. 8, LEGIARTI000028248431 et LEGIARTI000032129001 (2013-11-30 → 2017-01-31) : « 14e échelon 622 » | conforme |
| Technicien des installations (n° 2011-1673, depuis 2020) | art. 8, LEGIARTI000042563216 (depuis 2020-12-01) : « 13e échelon 4 ans » | art. 2, LEGIARTI000042563214 (depuis 2020-12-01) : « quatorze échelons » | n° 2013-1070, art. 8, LEGIARTI000042563276 : « 14e 638 » | conforme |
| Réviseur (n° 91-105) | art. 18, LEGIARTI000006460868 (1992-07-01 → 2016-02-29) : « Réviseur 11e échelon 4 ans 3 ans » | art. 2, LEGIARTI000006460848 (1992-07-01 → 2021-04-11) : « Le grade de réviseur des travaux de bâtiment comporte douze échelons » | n° 2011-1683, art. 13, LEGIARTI000024878131 : « Réviseur 12e 780 » ; n° 2013-1070, art. 13, LEGIARTI000028248441 : « 12e échelon 780 » | conforme |
| Lieutenant de port de première classe (n° 2013-1146) | art. 9, LEGIARTI000035923294 (2016-01-01 → 2017-01-01) : « 6e échelon 4 ans » | aucun : art. 2, LEGIARTI000028321239 (2013-12-14 → 2024-08-01), ne nomme que les deux grades | noyau 03088 : sept échelons en 2016 (483 à 648), le 8e naît le 2017-01-01 ; au LEGI, n° 2012-1058, art. 10, LEGIARTI000035932371 (mêmes dates) : « Lieutenant de port de première classe 7e échelon 648 […] 1e échelon 483 » | conforme (écart 1.a) |
| Directeur départemental adjoint (n° 58-778) | art. 16, LEGIARTI000043384245 (depuis 2021-04-11) : « Directeur départemental adjoint 3e échelon 3 ans » | art. 2, LEGIARTI000043384243 (2021-04-11 → 2025-03-01) et LEGIARTI000051204165 (depuis) : « comprend quatre échelons » | n° 2013-1070, art. 1er, LEGIARTI000051198637 (depuis 2025-02-20) : « Directeur départemental adjoint 4e 1015 » | conforme |

**Les 30 autres, au-delà de l'échantillon.** Même recherche, par la table `doc`, des articles
qui comptent les échelons, en vigueur sur la période rattachée ; chaque nombre égale n + 1 :
n° 90-973, art. 3 (ingénieur en chef « cinq », ingénieur général « trois ») ; n° 68-270,
art. 6 (graveur et chef de fabrication adjoint « onze », chef de fabrication « trois », chef
d'atelier principal, chef d'atelier, adjoint technique mécanicien « treize ») ; n° 91-105,
art. 2 (réviseur en chef « cinq ») ; n° 2011-1673, art. 2 de 2020 (chef technicien
« neuf ») ; n° 2003-676, art. 1er, LEGIARTI000027246561 (« comptant 8 échelons ») ;
n° 89-750, art. 2, LEGIARTI000019149265 (« onze », « huit ») ; n° 90-975, art. 3,
LEGIARTI000006459973 (principal, « huit ») ; n° 91-13, art. 2, LEGIARTI000032172681
(« quinze ») ; n° 92-413, art. 27, le tableau lui-même (« Les emplois de chacune de ces deux
catégories comprennent quatre échelons ») ; n° 2009-208, art. 5, ses deux versions (« cinq »,
« trois ») ; n° 2011-1678, art. 2, LEGIARTI000024875131 (« quatorze ») ; n° 56-448, art. 9,
LEGIARTI000032192685 (« quinze », « huit »). En tout, 34 grades. Pour les 9 autres, l'index
n'a aucun article qui compte leurs échelons sur la période : n° 2013-1146 (les deux versions
de l'art. 9) ; n° 83-1033 (conseillers hors classe et de classe normale ; grille, n° 2009-1303,
art. 1er, LEGIARTI000021205658 : « 5e échelon 985 », « 11e échelon 871 ») ; n° 2011-1676
(trois grades ; l'index n'a de lui que ses art. 4, 10, 11, 13 et 16 ; grilles, art. 14 des
n° 2011-1683 et 2013-1070 : « 14e », « 9e ») ; n° 72-420 (deux grades ; son art. 2 en vigueur
ne dit rien des échelons ; grille, n° 2016-229, art. 8, LEGIARTI000032118612 et
LEGIARTI000037636697 : « 14e », « 8e »). Aucun texte ne contredit le nombre retenu.

**Les huit cas n / n + 1 restés déclarés** (B : « tous de ceux-là ») : dans `durees/lignes.csv`,
le dernier rang de chacun n'a aucune durée (directeurs des services pénitentiaires, deux
tableaux ; ingénieur des sciences géographiques ; chargés de recherche hors classe ;
professeur de lycée professionnel ; professeur technique hors classe ; commandant et
lieutenant-colonel du n° 2016-2008). **Conforme.**

- **Écart 1.a, faible.** La preuve « sommet non écrit » ne cite pas l'article qui compte les
  échelons, alors que 34 des 43 en ont un ; pour le lieutenant de port, elle cite le noyau,
  quand le LEGI a le texte de la grille (n° 2012-1058, art. 10). Rien n'est faux ; la preuve
  écrite est moins forte qu'elle pourrait l'être. *Candidat* : citer, quand il existe,
  l'article du statut qui dit n + 1.
- **Écart 1.b, faible.** Le sommet d'une grille du LEGI dont le fichier fusionne les versions
  inchangées cite le seul premier article : les trois grades du n° 2009-208 (rattachés
  depuis le 2009-02-22, sans fin) citent LEGIARTI000020289113, en vigueur jusqu'au
  2017-01-01 seulement. Les versions suivantes (LEGIARTI000034034531, 2017-01-01 →
  2018-01-01 ; LEGIARTI000036489650, depuis) gardent « 5 HEB », « 3 HEE », « 5 HED », et
  l'art. 5 du statut, à ses deux versions, « cinq » et « trois » : le rattachement est juste,
  sa référence incomplète. La fusion est celle de `etat_legi/echelons.csv`, antérieure à B.

## 2. Le n° 91-783

L'art. 1er, LEGIARTI000006461848 (1992-02-08 → 2007-05-03) et LEGIARTI000006461849
(2007-05-03 → 2012-10-01), porte mot pour mot la citation ; aucune version avant le
1992-02-08 (`--num 1 --titre 91-783`). L'art. 15, LEGIARTI000006461873 (1991-08-20 →
2012-10-01), et l'art. 3, LEGIARTI000006461851 puis LEGIARTI000006461852 (« dix échelons »,
« sept échelons ») : exacts. Noyau : texte 112 (n° 91-783, fin 2012-10-01) ; corps 00671 et
00873, du 1991-08-01 au 2012-09-30, « 112:origine » ; grades 01523 et 02075 (grille 00092,
sept échelons, 422 à 638) et 01522 et 02076 (grille 00091, dix échelons, 322 à 593), mêmes
dates. Les durées de ces grilles au noyau sont celles du tableau (00092 : 24, 24, 36, 36, 36,
48 mois ; 00091 : 12, puis 24, 36, 48). Période [1992-02-08, 2012-10-01) ; le reste du
tableau, déclaré. **Conforme.**

## 3. L'annexe II du n° 94-1016, ôtée

L'art. 10, LEGIARTI000006476440 (depuis 1994-11-26) : « annexe II […] Classe exceptionnelle
7e échelon 4 ans 3 ans » ; l'art. 2 : « huit échelons pour les corps mentionnés à
l'annexe II » ; l'arrêté du 24 novembre 2006, art. 2, LEGIARTI000019528379 : « annexe II […]
Classe exceptionnelle 8e échelon 612 7e échelon 581 ». L'ancien rattachement à l'art. 1er
(annexe I, sept échelons) était faux ; il n'est plus dans le CSV, et la ligne est déclarée
(« plusieurs grilles du LEGI prouvées aux mêmes dates »). Les classes supérieure (« huit »)
et normale (« treize ») des deux annexes sont déclarées pour la même raison. **Conforme.**

## 4. Le n° 60-403 et la date qui ouvre la phrase

Le n° 2017-786, art. 12 (LEGIARTI000034750817, depuis 2017-05-08) et son visa
(LEGITEXT000034750633) : citations exactes ; le noyau, texte 166 : numéro, date, titre et
JORFTEXT000000501563 exacts, NOR vide. Les libellés des grades 01072 à 01074 et 01476 à
01478 : exacts.

- **Écart 4.a, faible.** La note écrit « le 00653 (ses grades, « 166:origine ») » : le corps
  00653 cite « 5414:origine », et de ses grades, seuls 01477 et 01478 citent le texte 166 ;
  01476 ne cite que 5329, 5330 et 5414. Sans effet : le groupe reste déclaré.

Les trois phrases datées (n° 2017-194, LEGIARTI000034054901 ; n° 98-416,
LEGIARTI000006507125 ; n° 95-720, LEGIARTI000006479055) : exactes. **Conforme.**

## 5. Les tests

Sur un arbre au commit d'avant (7114ee4^), le fichier de tests de `main` : quatre échouent,
pour la raison attendue (`test_le_sommet_que_le_tableau_n_ecrit_pas_se_rattache`,
`test_un_tableau_dont_le_dernier_rang_n_a_pas_de_duree_n_a_pas_de_sommet_non_ecrit`,
`test_le_decret_commun_des_assistants_de_service_social_rattache_chacun_de_ses_corps`,
`test_le_noyau_identifie_par_son_numero_et_sa_date_un_decret_sans_nor`) ; deux passent,
`test_aucune_phrase_restee_sans_date_ne_s_ouvre_sur_une_date`, que B dit vert d'emblée, et
`test_les_echelons_de_la_grille_sont_ceux_du_tableau_a_chaque_date`. Sur `main` :
`tests/test_chainage_grilles.py`, 38 verts. Le chaînage refait sur un arbre de `main` avec le
même index ne change aucun fichier (555 grades, 665 lignes, 13 reclassements). Les valeurs
des tests (dates, 36 et 30 mois, indices 901 et 612, rangs) sont celles des textes relus
ci-dessus. Le test d'invariant admet n + 1 quand la preuve dit le sommet : il ne prouve donc
pas le sommet ; c'est le test du sommet, tiré des textes, qui le fait. **Conforme.**

## Ce qui reste douteux, et les candidats

Ce que B laisse est déclaré dans sa note (« Ce qui n'a pas été vérifié, ce qui reste »).
Trois candidats, hors de sa tâche :

- La preuve du sommet pourrait citer l'article du statut qui compte les échelons (écart 1.a).
- *Une période de tableau sans grille ne se déclare pas.* Avant 7114ee4, la classe
  exceptionnelle de l'annexe I du n° 94-1016 était déclarée depuis le 1994-11-26 ; elle n'est
  plus que rattachée, depuis le 2006-11-26, et aucune ligne ne dit [1994-11-26, 2006-11-26).
  De même pour les réviseurs (n° 91-105) avant le 2011-12-01 et du 2013-06-19 au 2013-11-30.
  C'est la règle de R-B3-bis (seuls les jours où une grille rattachée n'a pas les échelons
  se déclarent), non une faute de B ; le chaînage ne distingue pas « aucune grille » de
  « oubli ».
- La 1re catégorie du n° 92-413 (art. 27 : quatre échelons ; grille, arrêté du 24 décembre
  2002, art. 1er : « 1re catégorie : 4e échelon HEA […] ») est déclarée « aucune grille […] ne
  porte ce libellé » : le lecteur des grilles l'a nommée
  `greffier-en-chef-du-premier-grade-nomme-dans-certains-emplois-…-1re-categorie`, quand la
  2e est `2e-categorie`. Un rattachement perdu, non faux.
