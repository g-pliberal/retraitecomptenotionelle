# B-bis : les preuves que la relecture R-B4 demande (le compte des échelons, les versions du n° 2009-209, le corps 00653)

Vague 10, B-bis, le 5 novembre 2026. Reprend les trois écarts faibles de la relecture R-B4
(`2026-11-05-relecture-r-b4.md`) du travail de B (`2026-11-05-rattacher-plus-sans-deviner.md`,
commit 7114ee4). Chaque article a été rouvert dans l'index LEGI (incrément
20261102-213929), par une lecture de la table `doc`, à toutes ses versions, et chaque
citation recherchée dans le texte de chaque version en vigueur sur la période rattachée.

## Avant, après : aucun rattachement ne bouge

`chainage/durees.csv` : 1 808 lignes avant comme après, identiques colonne par colonne hors
`preuve` ; 54 preuves changent, toutes des lignes « sommet non écrit ». 555 grades de
durées rattachés avant comme après ; `chainage/reclassements.csv` inchangé (13 groupes).

## 1. La preuve cite l'article du statut qui compte les échelons (écart 1.a)

`COMPTES` (dila_legi_chainage.py) : pour chacun des 45 groupes rattachés par le sommet
(les 43 de R-B4, et les deux du n° 91-783, qui l'ont aussi), l'article du statut qui compte
leurs échelons, son nombre, sa citation. `Depot.compte_du_statut` ne la cite que si le nombre
est n + 1 et que chaque version de l'article en vigueur sur le morceau rattaché porte la
citation, sans jour sans version ; la preuve dit alors « le statut compte ses échelons,
<versions> : « … » ». Sinon : « aucun article du statut ne compte ses échelons, au relevé de
l'index du 5 novembre 2026 ».

*Les 36 groupes qui en ont un* (le nombre vaut n + 1 à chaque fois, le test le recompte sur
`durees/lignes.csv`) :

| Statut | Article, versions de la période | Citation |
|---|---|---|
| n° 94-1016 | art. 2, LEGIARTI000006476418 | « La classe exceptionnelle ou le grade assimilé comprend sept échelons pour les corps mentionnés à l'annexe I du présent décret » |
| n° 2003-676 | art. 1er, LEGIARTI000027246561 (2013-04-01 → 2022-01-01) | « Ce cadre d'emplois comprend un grade de cadre de santé comptant 8 échelons » |
| n° 2003-770 | art. 2, LEGIARTI000023593810 (2011-02-18 → 2016-05-09) | « Le grade de directeur du travail qui comprend six échelons » |
| n° 68-270 (dix grades) | art. 6, LEGIARTI000029572468 (depuis 2014-11-01) | « Le grade d'ingénieur comprend huit échelons » ; « d'ingénieur en chef comprend quatre » ; « de chef de fabrication comprend trois » ; « de chef de fabrication adjoint comprend onze » ; « de chef mécanicien », « de chef d'atelier principal », « de chef d'atelier », « d'adjoint technique mécanicien comprend treize » ; « de maître graveur comprend six » ; « de graveur comprend onze échelons » |
| n° 89-750 | art. 2, LEGIARTI000019149265 (2008-07-11 → 2017-01-01) | « un grade d'ingénieur d'études et de fabrications qui comporte onze échelons » ; « un grade d'ingénieur divisionnaire […] qui comporte huit échelons » |
| n° 90-973 | art. 3, LEGIARTI000006459927 (2000-10-06 → 2017-03-01) | « le grade d'ingénieur, qui comporte dix échelons », « d'ingénieur en chef, […] cinq », « d'ingénieur général, […] trois » |
| n° 90-975 | art. 3, LEGIARTI000006459973 (1994-08-01 → 2017-01-01) | « le grade d'ingénieur d'études principal, qui comporte huit échelons » |
| n° 91-13 | art. 2, LEGIARTI000032172681 (depuis 2016-02-29) | « le grade d'infirmier ou infirmière doté de quinze échelons » |
| n° 91-105 | art. 2, LEGIARTI000006460848 (1992-07-01 → 2021-04-11) | « Le grade de réviseur des travaux de bâtiment comporte douze échelons » ; « Le grade de réviseur en chef comporte cinq échelons » |
| n° 91-783 | art. 3, LEGIARTI000006461851 (1991-08-20 → 2007-05-03), puis LEGIARTI000006461852 (→ 2012-10-01) | « le grade d'assistant de service social qui comporte dix échelons » ; « le grade d'assistant de service social principal, qui comporte sept échelons » |
| n° 92-413 | art. 27, LEGIARTI000006468212 (2002-12-29 → 2015-11-01), le tableau lui-même | « Les emplois de chacune de ces deux catégories comprennent quatre échelons » (les « emplois de la 1re ou de la 2e des catégories des emplois classés ») |
| n° 2009-208 (trois grades) | art. 5, LEGIARTI000020289510 (2009-02-22 → 2023-01-01) et LEGIARTI000045656098 (depuis) | « Les grades d'administrateur des finances publiques et d'administrateur général des finances publiques de classe normale comprennent chacun cinq échelons » ; « Le grade d'administrateur général des finances publiques de 1re classe comprend trois échelons » |
| n° 2011-1678 | art. 2, LEGIARTI000024875131 (depuis 2011-12-01) | « le grade d'infirmier ou infirmière doté de quatorze échelons » |
| n° 2011-1672 | art. 2, LEGIARTI000024875248 (depuis 2011-12-01) | « le grade unique de contrôleur divisionnaire doté de dix échelons » |
| n° 2011-1673 (trois groupes) | art. 2, LEGIARTI000024876132 (2011-12-01 → 2020-12-01) ; LEGIARTI000042563214 (depuis) | « le grade de technicien des installations doté de quatorze échelons » ; depuis 2020, « le grade de chef technicien doté de neuf échelons » |
| n° 58-778 | art. 2, LEGIARTI000043384243 (2021-04-11 → 2025-03-01) et LEGIARTI000051204165 (depuis) | « Le grade de directeur départemental adjoint comprend quatre échelons » |
| n° 56-448 | art. 9, LEGIARTI000032192685 (depuis 2016-02-29), le tableau lui-même | « le grade de dessinateur-projeteur doté de quinze échelons » ; « le grade de chef dessinateur doté de huit échelons » |

Trois, vérifiés à la main jusqu'au rang du tableau : n° 68-270, « Ingénieur […] 7e échelon
3 ans » (art. 21, LEGIARTI000029572482), huit échelons, 7 + 1 = 8 ; n° 2009-208,
administrateur général de 1re classe, deux rangs dans le tableau (art. 16, LEGIARTI000020289530 :
2e et 1er échelons, 36 et 27 mois), trois échelons, 2 + 1 = 3 ; n° 2011-1673, chef technicien
depuis 2020 (LEGIARTI000042563216 : 8e échelon, 36 mois), neuf échelons, 8 + 1 = 9.

*Les 9 qui n'en ont aucun à l'index*, rouverts : n° 2013-1146, art. 2 (LEGIARTI000028321239,
2013-12-14 → 2024-08-01) : « Le corps des officiers de port adjoints comprend deux grades
ainsi dénommés : 1° Lieutenant de port de seconde classe ; 2° Lieutenant de port de première
classe, grade le plus élevé. », sans nombre d'échelons (ses deux tableaux, art. 9) ;
n° 83-1033, aucun article qui compte les échelons des conseillers (le seul qui compte, l'art. 58,
LEGIARTI000020091170, est l'emploi d'administrateur) ; n° 2011-1676, l'index n'a que ses art. 4,
10, 11, 13 et 16, aucun ne compte (trois groupes) ; n° 72-420, son art. 2 en vigueur en 2016
(LEGIARTI000032510148) ne parle pas des échelons (deux grades). Leur preuve le dit ; ils
restent rattachés sur la règle du sommet, comme R-B4 les a trouvés conformes.

Tests, vus rouges (la preuve ne citait rien), puis verts :
`test_la_preuve_du_sommet_cite_l_article_du_statut_qui_compte_ses_echelons` (36 et 9 ; le nombre
cité recompté contre n + 1 ; six citations exactes).

## 2. Chaque version de la grille du n° 2009-209 (écart 1.b)

`Depot.sommet_legi` cite chaque version de l'article de la grille en vigueur sur le morceau,
non la seule que garde `etat_legi/echelons.csv`. Décret n° 2009-209, art. 1er :
LEGIARTI000020289113 (2009-02-22 → 2017-01-01) : « Administrateur des finances publiques
5e échelon HEB […] Administrateur général des finances publiques de classe normale 5e échelon
HED […] de 1re classe 3e échelon HEE » ; LEGIARTI000034034531 (2017-01-01 → 2018-01-01) et
LEGIARTI000036489650 (depuis) : « Administrateur des finances publiques 5 HEB HEB », « […] de
classe normale 5 HED HED », « […] de 1re classe 3 HEE HEE ». Aucune n'est dans
`DATES_CORRIGEES`. Les trois grades citent désormais les trois versions. Tests, vus rouges puis
verts : `test_le_sommet_d_une_grille_du_legi_cite_chaque_version_de_la_periode`, et le test de
la règle (un index simulé à deux versions).

## 3. Le corps 00653 (écart 4.a)

Ma note écrivait « le 00653 (ses grades, « 166:origine ») ». Le Noyau RH : le corps 00653
(`corps.csv`) cite « 5414:origine » ; ses grades 01477 et 01478 (`grades.csv`) citent
« 166:origine 5329:modificatif » ; 01476 cite « 5329:modificatif 5330:modificatif
5414:origine ». Le 00653 ne cite donc pas le texte 166 lui-même ; deux de ses grades le citent,
ce qui suffit au chaînage (`_corps_du_reclassement` lit corps et grades). Corrigé dans le
commentaire du test du n° 60-403 ; la note de B, un récit, garde son texte, avec un renvoi
daté au bout. Rien ne bouge dans les données : les trois groupes restent déclarés.

## Ce qui reste

Les candidats de R-B4 et de B, hors de cette tâche : les jours sans grille de l'annexe I du
n° 94-1016 (1994-2006) ; la 1re catégorie du n° 92-413, non rattachée à cause de son libellé ;
l'annexe que nomment le tableau du n° 94-1016 et l'arrêté du 24 novembre 2006 ; les
26 reclassements datés après « reclassés ».
