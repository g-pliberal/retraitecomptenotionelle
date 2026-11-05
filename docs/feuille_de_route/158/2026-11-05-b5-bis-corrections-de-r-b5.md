# B5-bis : les corrections de la relecture R-B5 (les tableaux qu'un autre article date, « A la même date »)

Vague 11, B5-bis, le 5 novembre 2026. Les écarts de la relecture R-B5
(`2026-11-05-relecture-r-b5.md`, commit a900de4) sur B5 (e6e5163,
`2026-11-05-b5-la-date-apres-reclasses.md`), et les cas de même nature qu'elle relève. Tout
ce qui suit a été lu pendant la session dans l'index LEGI du dépôt (`dila_index.py legi
--recuperer`, dump `Freemium_legi_global_20250713-140000`, incréments jusqu'au
20261102-213929), à la table `doc` : chaque article, toutes ses versions (même titre de
texte, même numéro). Le JORF n'a pas été ouvert.

## 1. Les tableaux qu'un autre article du décret date (écart moyen de R-B5, et trois de plus)

La phrase du tableau n'écrit pas la date ; l'article du décret qui fixe son effet la donne,
en nommant l'article du tableau. Quatre tableaux, chacun lu avec l'article qui le date, à la
version qui couvre la sienne (même début, même fin ou plus tard), mot pour mot :

1. n° 98-268, art. 17, tableau 1 (LEGIARTI000006506606, du 2003-06-21 au 2012-09-01 ;
   « Les techniciens supérieurs et techniciens supérieurs principaux de l'industrie et des
   mines sont nommés au 1er août 1995 dans le nouveau grade de technicien supérieur principal
   et reclassés conformément aux dispositions ci-dessous ») → **1995-08-01**. Art. 28,
   dans ses deux versions (LEGIARTI000006506627, du 1998-04-09 au 2003-06-21 ;
   LEGIARTI000006506628, du 2003-06-21 au 2012-09-01) : « Les articles 17, 18, 21 et 22 du
   présent décret prennent effet au 1er août 1995. » La note de B5 tenait ce point pour non
   tranché : le texte le tranche, par la lecture a.
2. n° 2001-325, art. 14, tableau 1 (LEGIARTI000006567682, depuis le 2001-04-15) →
   **1997-01-01**. Art. 17 (LEGIARTI000006567685, depuis le 2001-04-15, seule version) :
   « Les dispositions des articles 1er, 4, 5, 6 du I de l'article 7, des articles 8, 9, 10,
   11, 14 et 15 du présent décret prennent effet au 1er janvier 1997. » La note de B5
   écrivait « le texte ne date pas le reclassement » : c'est faux, un autre article le date.
3. n° 2017-1367, art. 23, tableau 1 (LEGIARTI000035601659, depuis le 2017-09-23) →
   **2017-01-01**. Art. 28 (LEGIARTI000035601611, depuis le 2017-09-23, seule version) :
   « Le chapitre Ier, à l'exception du troisième alinéa de l'article 2, et les articles 23 à
   25 entrent en vigueur le 1er janvier 2017. »
4. n° 2017-1494, art. 13, tableau 1 (LEGIARTI000035900888, depuis le 2017-10-28) →
   **2017-01-01**. Art. 15 (LEGIARTI000035900898, depuis le 2017-10-28, seule version) :
   « Les dispositions du chapitre Ier et du II de l'article 13 entrent en vigueur le
   1er janvier 2016. Les dispositions du chapitre II, à l'exception de celles des articles 4,
   5 et 7, et les dispositions du I de l'article 13 entrent en vigueur le 1er janvier
   2017. » Le tableau est dans le I : l'article s'ouvre sur « I. - Les fonctionnaires
   appartenant au 7e échelon du grade de classe exceptionnelle […] », le tableau suit
   (« 7e échelon depuis 3 ans ou plus 8e échelon Sans ancienneté 7e échelon depuis moins de
   3 ans 7e échelon Ancienneté acquise »), puis vient « II. - Les techniciens supérieurs […]
   conservent les réductions et majorations d'ancienneté », sans tableau.

R-B5 demandait au propriétaire si « entrent en vigueur le » date le tableau d'un décret
rétroactif comme « prennent effet au ». Ma lecture : oui, ici, sans autre lecture qui tienne.
L'article du décret nomme l'article du tableau et lui donne une date, et le tableau n'en
écrit pas d'autre. Le début de la version au LEGI (2017-09-23, 2017-10-28) est la date de la
consolidation, non une date que le texte écrit. La question reste posée au propriétaire,
s'il veut la trancher autrement.

Les quatre dates sont entrées au lecteur, dans une table lue à la main, avec la preuve :
`DATES_D_UN_AUTRE_ARTICLE` (`scripts/fetch/dila_legi_reclassements.py`) donne, pour
l'article du tableau, la date, l'article qui la donne et ses mots. Elle sert quand la
phrase n'écrit pas de date (`effet_du_tableau`). La colonne `effet` de `tableaux.csv` a été
refaite par cette fonction sur la phrase stockée, comme dans B5 : quatre cases vides
prennent leur date, et les 446 autres se refont à l'identique. L'en-tête du fichier dit la
nouvelle source de date. Test, vu rouge puis vert :
`test_un_tableau_que_date_un_autre_article_de_son_decret_prend_cette_date`.

Le chaînage, relancé : les groupes des quatre tableaux portent leur date (`date_lue`
effet). Aucun rattachement de plus (13 rattachés, 849 déclarés). Les n° 2001-325, 2017-1367
et 2017-1494 passent à l'étape suivante (« la phrase ne nomme pas le statut du corps
reclassé », « le libellé ne se coupe pas en deux grades ») ; le n° 98-268, art. 17, était
déjà déclaré (« groupe vide »). Les tableaux de l'État déclarés faute de date passent de
158 à 155.

## 2. Deux cas de même nature, déclarés et non corrigés

- **n° 98-268, art. 20** (LEGIARTI000006506612, du 2003-06-21 au 2012-09-01), que R-B5 ne
  relève pas. L'art. 28 dit aussi : « Les articles 19 et 20 prennent effet au 1er août
  1994. » Mais l'art. 20 échelonne le passage : « Les titulaires du grade provisoire de
  technicien supérieur en chef de l'industrie et des mines qui ont été promus dans l'ancien
  grade de technicien supérieur en chef avant le 1er août 1994 accèdent au nouveau grade de
  technicien supérieur en chef au 1er août 1994, au 1er août 1995, au 1er août 1996 et au
  1er janvier 1997, dans la limite des emplois inscrits aux lois de finances afférentes aux
  années dont il s'agit […] », puis « Ces agents sont reclassés conformément au tableau
  ci-après ». Une seule date ne vaut pas pour tous les agents du tableau : 1994-08-01 n'est
  que la première. Je n'ai rien corrigé : `effet` reste vide, et le test le garde. *Candidat* :
  un tableau à plusieurs dates d'effet, que la donnée ne sait pas dire.
- **n° 98-896, art. 8** (LEGIARTI000006508629, depuis le 2002-03-21). L'art. 10
  (LEGIARTI000006508631, depuis le 1998-10-09, seule version) : « Les dispositions des
  articles 1er, 6, 7 et 8 du présent décret sont applicables à compter du 1er août 1996. »
  Mais la version du tableau que porte la donnée est celle du 2002-03-21 : l'art. 8 a été
  récrit par le décret n° 2002-378 du 19 mars 2002 (LEGITEXT000005632469). Son art. 1er
  (LEGIARTI000006209301) n'est au LEGI que « a modifié les dispositions suivantes », et son
  art. 2 (LEGIARTI000006209302) est l'article d'exécution. Aucun article du n° 2002-378 ne
  dit quand la rédaction nouvelle prend effet. La première rédaction (LEGIARTI000006508628,
  du 1996-08-01 au 2002-03-21, « Les lieutenants de port en fonctions à la date du présent
  décret sont reclassés conformément au tableau ci-après ») n'est pas dans la donnée. Point
  non tranché, deux lectures : a, la rédaction de 2002 reste l'art. 8 que l'art. 10 rend
  applicable au 1er août 1996 ; b, elle ne vaut que depuis sa publication, le 2002-03-21,
  faute d'une clause qui la rende rétroactive. Je n'ai rien corrigé : `effet` reste vide
  (2002-03-21, la lecture b), et le test le garde. *Candidat* : lire au JORF le n° 2002-378
  (son art. 1er, et ce que le texte signé dit de son effet).

## 3. « A la même date » (relevé par R-B5)

n° 2017-903, art. 12, deux versions (territoriale). LEGIARTI000034702202, du 2018-02-01 :
« Au 1er février 2018, les conseillers supérieurs socio-éducatifs sont reclassés […] » puis
« A la même date, les conseillers socio-éducatifs sont reclassés selon le tableau de
correspondance ci-après ». LEGIARTI000036440010, du 2017-12-24 : de même, « Au 1er février
2019 ». Les quatre phrases sont mot pour mot dans leur article. Le chaînage lisait la date
du tableau 1 (« phrase ») et laissait le tableau 2 sans date. Il lit maintenant « A la même
date » comme la date du tableau qui précède dans le même article (`MEME_DATE`,
`date_du_tableau`, `date_lue` « meme_date ») : tableau 2, 2018-02-01 et 2019-02-01. Les
groupes restent déclarés (versant territorial). Test, vu rouge puis vert :
`test_a_la_meme_date_prend_la_date_du_tableau_precedent`. La date est au chaînage, comme
celle qui ouvre la phrase : le lecteur ne lit pas les dates qui ouvrent une phrase, et
`effet` de `tableaux.csv` reste vide pour ces deux tableaux.

## 4. L'arrêté du 18 avril 1989 (écart faible)

La note de B5 écrivait qu'il « date un classement, non le reclassement ». La phrase entière
(LEGIARTI000006718191, art. 4, depuis le 1989-01-01, seule version) dit le contraire : « Les
fonctionnaires hospitaliers appartenant à un grade ou emploi classé dans les groupes IV, V
et VI au 1er janvier 1989 et ceux bénéficiant, à la même date, du classement dans les
groupes V, VI et VII, en application des dispositions de l'article 3 de l'arrêté du
21 décembre 1982 susvisé sont reclassés à cette même date dans les échelles 3, 4 et 5
conformément au tableau suivant ». « Cette même date » est le 1er janvier 1989, la date du
reclassement. La donnée est juste (`effet` vide : l'entrée en
vigueur de la version, le 1989-01-01). Seule la raison de B5 était incomplète.

## 5. Le candidat des 540 tableaux (correction de R-B5)

La note de B5 écrivait que des textes « sortent » à la relance du lecteur (n° 95-370,
2006-1732, 2007-1333). R-B5 l'a rejoué : aucun ne sort. Les 532 textes et les 450 tableaux
du dépôt sont tous dans la relance, identiques colonne par colonne, et 90 tableaux s'y
ajoutent (78 textes). Mon « d'autres sortent » venait d'une lecture trop rapide du
`git diff` de `textes.csv`, que je n'avais pas vérifiée ligne à ligne : les lignes
qu'il ôtait n'étaient pas des textes sortis. Ce n'est pas une divergence mais une extension : 90
tableaux à lire, certifier et chaîner, dans une étape à eux.

## Ce qui reste

Les cinq dates de R-B5 sont faites (quatre entrées, celle du n° 98-896 non tranchée), et
les deux « A la même date ». Restent : les plus de cent dates relatives au décret (« à la
date d'entrée en vigueur du présent décret », « à la date d'effet du présent décret »), à
lire décret par décret ; les décrets qui datent un « chapitre » plutôt qu'un article ; le
n° 98-268, art. 20, et le n° 98-896, art. 8 (ci-dessus) ; les 90 tableaux de l'index publié.
