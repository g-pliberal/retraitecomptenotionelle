# Relecture de B5-bis : les quatre dates d'un autre article, « A la même date », les deux points déclarés

Vague 11, R-B6, le 6 novembre 2026. Relecture indépendante du commit 396d8b9 (B5-bis, note
`2026-11-05-b5-bis-corrections-de-r-b5.md`). Tout ce qui suit a été rouvert pendant la session,
sans rien reprendre de la note de B5-bis ni de la mémoire : l'index LEGI du dépôt (dump
`Freemium_legi_global_20250713-140000`, incrément 20261102-213929) **et l'index JORF**
(`Freemium_jorf_global_20250713-140000`, incrément 20261103-002311, que B5-bis n'avait pas
ouvert), par `dila_cherche.py` (`--texte`, `--num`, `--titre`) et par une lecture directe de la
table `doc`. Aucun fac-similé n'est lu. Les deux index sont effacés en finissant. Aucune règle,
aucune donnée, aucun test n'est touché ici.

**Verdict : les quatre dates et « A la même date » sont exacts, les comptes tiennent, les
tests tirent leurs valeurs du texte.** Trois écarts, aucun grave : le JORF, que B5-bis n'a pas
ouvert, tranche en grande partie le n° 98-896 art. 8 qu'elle tenait pour non tranché (moyen,
aucune donnée fausse) ; une version « jamais en vigueur » n'est pas dite (faible) ; aucun test
ne tient la citation et l'article d'effet de `DATES_D_UN_AUTRE_ARTICLE` au texte (faible).

## 1. Les quatre dates d'un autre article : conformes (4 sur 4)

Pour chaque tableau, on a ouvert l'article du tableau et l'article d'effet par leur
identifiant, lu toutes les versions de chacun (même titre de texte, même numéro), comparé la
citation de `DATES_D_UN_AUTRE_ARTICLE` au texte de l'index (la phrase citée est une sous-chaîne
du texte de l'article d'effet, espaces normalisés : 4 sur 4), et relu le même article au JORF
(le texte signé, non le consolidé).

Les identifiants LEGI sont abrégés : `…6506606` pour `LEGIARTI000006506606`.

| Tableau (LEGI, version) | Article d'effet (LEGI) | Ce que dit l'article d'effet | Date |
|---|---|---|---|
| n° 98-268 art. 17, `…6506606`, 2003-06-21 → 2012-09-01 | art. 28, `…6506627` (1998-04-09 → 2003-06-21) et `…6506628` (2003-06-21 → 2012-09-01), même phrase ; JORF `JORFARTI000001999730` | « Les articles 17, 18, 21 et 22 du présent décret prennent effet au 1er août 1995. Les articles 19 et 20 prennent effet au 1er août 1994. » | 1995-08-01 |
| n° 2001-325 art. 14, `…6567682`, depuis 2001-04-15 | art. 17, `…6567685`, seule version ; JORF `JORFARTI000002034636` | « Les dispositions des articles 1er, 4, 5, 6 du I de l'article 7, des articles 8, 9, 10, 11, 14 et 15 du présent décret prennent effet au 1er janvier 1997. » | 1997-01-01 |
| n° 2017-1367 art. 23, `…35601659`, depuis 2017-09-23 | art. 28, `…35601611`, seule version ; JORF `JORFARTI000035600301` | « Le chapitre Ier, à l'exception du troisième alinéa de l'article 2, et les articles 23 à 25 entrent en vigueur le 1er janvier 2017. » | 2017-01-01 |
| n° 2017-1494 art. 13, `…35900888`, depuis 2017-10-28 | art. 15, `…35900898`, seule version ; JORF `JORFARTI000035900572` | « Les dispositions du chapitre II, à l'exception de celles des articles 4, 5 et 7, et les dispositions du I de l'article 13 entrent en vigueur le 1er janvier 2017. » (la phrase d'avant date le II de l'article 13 et le chapitre Ier au 1er janvier 2016) | 2017-01-01 |

- **La date est la bonne.** Les quatre articles d'effet nomment l'article du tableau : « 17 » dans
  « 17, 18, 21 et 22 », « 14 » dans « 14 et 15 », « 23 à 25 », « le I de l'article 13 ». Le
  tableau de l'art. 13 du n° 2017-1494 est bien dans le I (l'article s'ouvre sur « I. - Les
  fonctionnaires appartenant au 7e échelon […] sont reclassés […] conformément au tableau »,
  le II, daté de 2016, ne porte pas de tableau). Les phrases des tableaux confirment :
  « nommés au 1er août 1995 » (n° 98-268), « placés au 1er janvier 1997 » (n° 2001-325), « les
  années antérieures à l'année 2017 » (n° 2017-1367).
- **La version couvre le tableau.** Pour le n° 98-268, la version de l'art. 17 de la donnée
  (2003-06-21 → 2012-09-01) est couverte, à la même borne, par la seconde version de l'art. 28,
  et les deux versions de l'art. 28 disent la même chose. Pour les trois autres, article du
  tableau et article d'effet ont une seule version, du même jour.
- **Tous les textes modificatifs, cherchés par titre (JORF et LEGI), par numéro dans le plein
  texte du LEGI, et par version d'article.** n° 98-268 : deux décrets le modifient, n° 2003-527
  (18 juin 2003) et n° 2006-1122 (6 septembre 2006). Le premier a quatre articles de fond (art. 1,
  l'intitulé ; art. 2, le renommage ; art. 3, l'art. 4, 3° ; art. 4, le dernier alinéa de
  l'art. 8) : l'art. 2 remplace, « dans tous les textes réglementaires », les noms de grades
  (« technicien(s) de l'industrie et des mines » devient « technicien(s) supérieur(s) […] »,
  etc.), d'où la version du 2003-06-21 des art. 17 et 20 (le diff du LEGI n'y change que les
  noms de grades) ; ni lui ni le n° 2006-1122 (qui refait les art. 3 à 11) ne datent autrement
  les art. 17, 20 ou 28. La date ne bouge pas.
  Aucun texte ne modifie les n° 2001-325, 2017-1367, 2017-1494 ni 2017-903 (aucun titre ne le
  dit, aucune version de leurs articles d'effet ne change). L'index est filtré par thème : un
  texte modificatif hors filtre ne serait pas là, mais il ouvrirait une version de l'article,
  et il n'y en a pas.
- **Les versions de LEGI recoupent la date.** Le LEGI ouvre la version antérieure de l'art. 17
  du n° 98-268 (`LEGIARTI000006506605`) au 1995-08-01, celle de l'art. 18 au 1995-08-01 aussi,
  celles des art. 19 et 20 au 1994-08-01 : les dates de l'art. 28. Ces versions-là
  (tableaux en « :-----: », texte d'avant le renommage de 2003) ne sont pas dans la donnée ;
  elles sont du côté des versions hors du motif, non de B5-bis.
- **La donnée.** Entre 396d8b9^ et 396d8b9, `tableaux.csv` ne change que ces quatre cellules
  `effet` (vides → les quatre dates), sur 450 lignes ; aucune autre colonne, aucune autre ligne.
- **Réserve de l'auteur de B5-bis, reprise telle quelle.** Le propriétaire n'a pas dit si « entrent
  en vigueur le » date le tableau d'un décret comme « prennent effet au » : B5-bis écrit sa lecture
  (oui) et laisse la question ouverte. Rien ne la contredit ici : les deux décrets de 2017 écrivent
  une date antérieure à leur publication (22 septembre et 27 octobre 2017), et la donnée porte la
  date qu'ils écrivent, non un jugement sur la rétroactivité.

## 2. « A la même date » (n° 2017-903, art. 12) : conforme, une omission faible

- **Les quatre phrases sont dans leur article, mot pour mot.** `LEGIARTI000034702202` :
  « I. - Au 1er février 2018, les conseillers supérieurs socio-éducatifs sont reclassés […] »
  puis « II. - A la même date, les conseillers socio-éducatifs sont reclassés selon le tableau de
  correspondance ci-après » ; `LEGIARTI000036440010` : de même avec « Au 1er février 2019 ». Le II
  suit le I dans le même article, et le tableau 1 est celui du I, le tableau 2 celui du II :
  la date reprise (2018-02-01, 2019-02-01) est bien celle du tableau que la phrase désigne.
- **Le champ de la règle.** Dans les 450 tableaux, « A la même date » n'ouvre la phrase que de
  ces deux tableaux (`MEME_DATE` s'ancre au début de la phrase). Les neuf autres phrases qui
  contiennent « même date » l'ont au milieu : cinq après une date écrite (« en fonctions au
  1er août 1995 […] reclassés à cette même date »), qui portent déjà leur `effet` ; quatre sans
  `effet` : trois après une date relative au décret (« à la date d'entrée en vigueur du présent
  décret […] à cette même date »), une après « au 1er janvier 1989 » (l'arrêté du 18 avril 1989,
  que B5-bis traite à son point 4). `MEME_DATE` ne les touche pas.
  Dans `chainage/reclassements.csv`, seules ces deux lignes passent à `date_lue = meme_date` ;
  les huit lignes que B5-bis change sont les attendues (`date`, `date_lue`, et la `raison` des
  cinq lignes des trois tableaux désormais datés), avec les mêmes 862 clés.
- **Omission (faible).** `LEGIARTI000034702202` est « jamais en vigueur » : son début
  (2018-02-01) est postérieur à sa fin (2017-12-24), la version du 2017-12-24 (« Au 1er février
  2019 ») l'ayant remplacée avant qu'elle ne prenne effet. La note la présente comme une version
  ordinaire (« du 2018-02-01 »), et le chaînage lui donne la date 2018-02-01 pour un reclassement
  qui n'a pas eu lieu. Sans conséquence ici : le groupe est déclaré (versant territorial) et rien
  ne le consomme. *Candidat* : avant tout rattachement du versant territorial, ne pas lire
  comme un reclassement une version dont la fin précède le début.

## 3. Les deux points déclarés sans correction

### 3.1 n° 98-268 art. 20 : fondé

`LEGIARTI000006506612` (2003-06-21 → 2012-09-01), relu : les titulaires du grade provisoire
« accèdent au nouveau grade […] au 1er août 1994, au 1er août 1995, au 1er août 1996 et au
1er janvier 1997, dans la limite des emplois inscrits aux lois de finances afférentes aux années
dont il s'agit, selon une liste d'aptitude » ; la phrase suivante, que la note ne cite pas, fait
de même pour ceux promus « entre le 1er août 1994 et le 31 juillet 1995 » (au 1er août 1995, au
1er août 1996 et au 1er janvier 1997) ; puis « Ces agents sont reclassés conformément au tableau
ci-après ». L'art. 28 (« Les articles 19 et 20 prennent effet au 1er août 1994 ») date l'article,
non chaque agent. Le JORF de 1998 (`JORFARTI000001809061`, avant le renommage de 2003) dit la même
chose. Le tableau a donc plusieurs dates, `effet` vide est la seule valeur exacte, et le test la
garde. Le candidat de la note (un tableau à plusieurs dates d'effet) est fondé.

### 3.2 n° 98-896 art. 8 : le JORF tranche la plus grande part (écart moyen, aucune donnée fausse)

Ce que B5-bis a lu est exact : art. 10 (`LEGIARTI000006508631`, JORF `JORFARTI000002486581`,
seule version) : « Les dispositions des articles 1er, 6, 7 et 8 du présent décret sont
applicables à compter du 1er août 1996 » ; le n° 2002-378 n'a que deux articles au LEGI, dont
l'un d'exécution ; la version de la donnée (`LEGIARTI000006508629`, depuis 2002-03-21) est
celle qu'il a refaite. Ce que le JORF ajoute, et que la note renvoie à une lecture à faire :

- **Le texte signé du n° 2002-378, art. 1er** (`JORFARTI000002416455`) tient en une phrase :
  « A l'article 8 du décret du 7 octobre 1998 susvisé, les mots : « en fonctions à la date du
  présent décret » sont supprimés. » L'art. 2 est l'exécution (`JORFARTI000002195228`). Il n'y a
  pas d'autre article, donc aucune clause d'effet, comme B5-bis l'écrit.
- **Le décret ne change donc pas le tableau.** Les deux rédactions du LEGI portent les mêmes
  lignes : classe fonctionnelle, 4e échelon après / avant 1 an, 3e, 2e après / avant 1 an, 1er ;
  classe normale, 4e, 3e après / avant 2 ans, 2e, 1er ; stage. Mêmes cases d'arrivée et mêmes
  règles d'ancienneté, 11 lignes de part et d'autre. La version de 1996
  (`LEGIARTI000006508628`, 1996-08-01 → 2002-03-21, « en fonctions à la date du présent
  décret », tableau en « :---: ») est ouverte par le LEGI au 1996-08-01, la date de l'art. 10.
  Le 2002-03-21 est le début de la version consolidée, non la date du tableau.
- **Conclusion de lecture, pour qui décidera.** Pour le tableau, la lecture a de B5-bis (la
  rédaction de 2002 reste l'art. 8 que l'art. 10 rend applicable au 1er août 1996) est celle que
  les textes portent ; la lecture b (« ne vaut que depuis sa publication ») ferait du tableau de
  1996 un tableau de 2002, alors que le décret de 2002 ne le touche pas. Ce que le décret de
  2002 élargit, c'est le champ : il retire la condition d'être « en fonctions à la date du
  présent décret » ; que cet élargissement soit lui-même rétroactif au 1996, le texte ne le dit
  pas. Le dernier point reste donc ouvert, mais plus la date du tableau. C'est la date que R-B5
  proposait (son entrée du journal de veille : « 98-896 art. 8 (1996-08-01) »).
- **Ce qui n'est pas lu.** Le tableau d'origine du n° 98-896, art. 8, est au JORF « dans le
  JO n° 234 du 09/10/1998 page 15305 à 15307 » (`JORFARTI000002094938`, « Vous pouvez consulter le
  tableau dans le JO ») : un fac-similé, à ajouter à
  `docs/feuille_de_route/138/2026-11-05-la-file-des-fac-similes.md`, où ce JO n'est pas.
- **Gravité.** `effet` vide laisse l'entrée en vigueur de la version (2002-03-21) comme date par
  défaut ; le chaînage, lui, ne lit que `effet` et la date qui ouvre la phrase, et déclare les
  deux groupes « faute de date ». Rien dans le dépôt ne consomme `tableaux.csv` hors les trois
  scripts de `scripts/fetch/`. Aucune valeur fausse n'est écrite ; la conclusion « non tranché »
  est trop prudente d'une lecture, que B5-bis annonçait elle-même (« Candidat : lire au JORF »).
- **Suite proposée** (non faite ici) : dater `LEGIARTI000006508629` du 1996-08-01, par
  `DATES_D_UN_AUTRE_ARTICLE` (art. 10 du n° 98-896, ses mots ci-dessus, et l'art. 1er du
  n° 2002-378 en preuve que le tableau n'a pas changé), et changer en conséquence l'assertion
  `effet == ""` de `test_un_tableau_que_date_un_autre_article_de_son_decret_prend_cette_date`,
  qui garde aujourd'hui l'état non tranché. Le propriétaire dit s'il veut la lecture a.

## 4. Les tests et le compte : conformes, une garde manque (faible)

- **Les valeurs viennent du texte.** `DATES_D_UN_AUTRE_ARTICLE` du test écrit en dur les quatre
  dates et la phrase de chaque article d'effet en commentaire ; elles sont celles du texte relu
  ci-dessus, non celles que rend le code (le test compare la donnée `tableaux.csv` à ces valeurs).
  `test_a_la_meme_date_prend_la_date_du_tableau_precedent` écrit en dur 2018-02-01 et 2019-02-01,
  qui sont les dates des phrases « Au 1er février 2018 » et « Au 1er février 2019 ». Les deux
  assertions `effet == ""` (n° 98-268 art. 20, n° 98-896 art. 8) gardent les points déclarés.
- **158 → 155 est cohérent.** Recompté dans `chainage/reclassements.csv` : 155 tableaux distincts
  dont la raison commence par « la phrase qui annonce le tableau n'écrit pas la date ». Le
  diff de 396d8b9 ôte exactement trois tableaux de ce compte (n° 2001-325, 2017-1367, 2017-1494,
  dont la raison devient « la phrase ne nomme pas le statut… » ou « le libellé ne se coupe pas
  en deux grades… ») ; le n° 98-268 art. 17 était déjà déclaré pour une autre raison (« groupe
  vide »), les deux « A la même date » aussi (versant territorial). 849 déclarés et 13
  rattachés, comme avant : aucun rattachement de plus, comme la note le dit.
- **Garde manquante (faible).** `set(rec.DATES_D_UN_AUTRE_ARTICLE) == {…}` ne compare que les
  clés : l'article d'effet et la phrase citée de `DATES_D_UN_AUTRE_ARTICLE` (le module) ne sont
  confrontés au texte par aucun test (la CI n'a pas l'index). On l'a fait ici : la phrase citée
  est dans le texte de l'article d'effet, qui est du même décret, 4 sur 4. *Candidat* : un test
  qui le refait quand l'index est présent (comme les tests de `test_grilles_legi.py`), et passe
  sinon.
- **Les tests, lancés.** `tests/test_reclassements.py` et `tests/test_chainage_grilles.py`,
  en entier : 74 passés. `python -m pytest -m rapide` : 4 506 passés, 8 ignorés.
  `PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 4 303 passés, 211 ignorés. Aucun rouge.

## Ce qui reste (suite de B5-bis)

Inchangé, sauf le n° 98-896 art. 8 (point 3.2) : les plus de cent dates relatives au décret,
les décrets qui datent un chapitre, le n° 98-268 art. 20 à plusieurs dates, les 90 tableaux de
l'index publié ; et, nouveaux ou précisés par cette relecture, la version « jamais en vigueur »
(point 2), la garde de la citation (point 4), le fac-similé du JO n° 234 du 9 octobre 1998
(point 3.2).
