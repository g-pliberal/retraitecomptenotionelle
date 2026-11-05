# Relecture de B5 : la date d'effet écrite après « reclassés »

Vague 11, R-B5, le 5 novembre 2026. Relecture indépendante du commit e6e5163 (B5, note
`2026-11-05-b5-la-date-apres-reclasses.md`). Tout ce qui suit a été rouvert pendant la
relecture : l'index LEGI du dépôt (`dila_index.py legi --recuperer`, dump
`Freemium_legi_global_20250713-140000`, incrément 20261102-213929, le même que B5), par une
lecture directe de la table `doc` (identifiant d'article, début, fin, numéro, texte) et par
`dila_cherche.py legi --etat`. Rien n'est repris de la note de B5 ni de la mémoire de la
session : ses 36 citations ont été comparées une à une au texte de l'index. Ne sont pas
ouverts : le JORF (le LEGI consolide, il n'est pas le texte signé) ni aucun fac-similé ; les
dates ci-dessous sont celles du LEGI à l'incrément du 2 novembre 2026.

**Verdict : les 36 dates sont exactes, et aucune donnée écrite par B5 n'est fausse.** Trois
écarts, aucun grave : B5 tient pour « non tranchés » ou « non datés » deux reclassements que
le texte date, par un autre article du même décret (moyen) ; la raison de l'arrêté du
18 avril 1989 est incomplète (faible) ; le bloc « Reprise » ne dit plus qu'il reste des dates
d'effet non lues (faible). Le candidat du lecteur relancé : le compte est exact (540), mais
la description est inexacte, rien ne sort (point 5). Aucun test, aucune donnée ni aucune règle
n'est touché ici.

## 1. Les 36 dates : conformes

Pour chaque tableau changé entre e6e5163^ et e6e5163 (36 lignes de `tableaux.csv`, aucune
autre colonne ni autre ligne), on a ouvert l'article par son identifiant LEGIARTI :

- **Version.** Le début et la fin de la ligne sont ceux de l'index (36 sur 36) ; 33 articles
  sont en vigueur (fin 2999-01-01), trois sont clos au 2017-01-01 (n° 88-1077, art. 50-1 ;
  n° 2010-1139, art. 30 et 31), comme la note le dit. Chacun des 34 articles n'a qu'une
  version dans l'index, et aucun texte de l'index ne le modifie (recherche en plein texte
  du numéro du décret près de « article <n> » et d'un verbe de modification, sur les 34 :
  un seul résultat, l'arrêté du 3 juillet 2017, qui vise le n° 2017-593 (« notamment son
  article 6 ») sans le modifier).
  L'index est filtré par thème : un texte modificatif hors du filtre n'y serait pas, mais le
  LEGI ouvrirait alors une version de l'article, et il n'y en a pas.
- **Citation.** Les 36 phrases de la note, et celles de `tableaux.csv`, sont dans le texte de
  l'article, mot pour mot (espaces normalisés) : 36 sur 36, sans écart de ponctuation.
- **Date.** Relue sans le code de B5 : la date de la phrase est la dernière de l'`intro`,
  celle qui suit le verbe ; les dates qui la précèdent sont des textes cités (« décret du
  14 mars 1990 », « loi du 11 janvier 1984 »). Les 36 valeurs de `effet` sont celles que le
  texte écrit. Les comptes de la note tiennent : 22 avant l'entrée en vigueur de la version,
  10 le même jour, 4 après (n° 96-980, art. 10 ; n° 2010-1139, art. 30 et 31 ; n° 2016-1880,
  art. 11) ; 25 « reclassés, au », 4 « reclassés au », 1 « nommés et reclassés, au », 3 « avec
  effet au », 2 « Avec une date d'effet au », 1 « reclassés dans le grade de … au ».
- **Le n° 96-980, art. 10** (le seul où la date suit un grade d'accueil, et la plus éloignée
  de la version, un an) : l'art. 9 crée « au 1er août 1995 » un grade provisoire de chef
  dessinateur, d'une durée de deux ans en moyenne par échelon, et l'art. 10 en reclasse les
  titulaires « dans le grade de dessinateur projeteur en chef au 1er août 1996 » ; l'art. 13
  parle de « la date d'application de l'article 10 ». La date de 1996 est celle du
  reclassement.
- **Le n° 2010-1139, art. 31** : le droit d'option s'ouvre « à compter du 1er janvier 2012 » ;
  « Avec une date d'effet au 1er juillet 2012 » est cohérent. **Le n° 2017-297, art. 13**
  (« nommés et reclassés, au 1er janvier 2017 ») : la date vaut pour les deux verbes, et le
  reclassement est bien daté.

## 2. Les cas écartés : le texte les date, B5 ne le dit pas

- **« placés au » (n° 2001-325, art. 14, LEGIARTI000006567682).** La phrase de B5 est exacte,
  et « placés au 1er janvier 1997 dans l'une des positions » date bien la position. Mais le
  texte date aussi le reclassement, ailleurs : l'art. 17 du même décret (LEGIARTI000006567685,
  du 2001-04-15, en vigueur) dit : « Les dispositions des articles 1er, 4, 5, 6 du I de
  l'article 7, des articles 8, 9, 10, 11, 14 et 15 du présent décret prennent effet au 1er
  janvier 1997. » Le tableau de l'art. 14 prend effet au 1997-01-01 ; la donnée (`effet`
  vide) le date de l'entrée en vigueur de la version, le 2001-04-15, quatre ans plus tard.
  **Écart moyen** : la note écrit « le texte ne date pas le reclassement », ce qui est
  inexact, et la donnée reste fausse.
- **« nommés au » (n° 98-268, art. 17, LEGIARTI000006506606, du 2003-06-21 au 2012-09-01).**
  B5 laisse la question ouverte (« la date de la nomination vaut-elle pour "reclassés" ? »).
  Le texte la tranche : l'art. 28 du même décret (LEGIARTI000006506627, du 1998-04-09 au
  2003-06-21, et LEGIARTI000006506628, du 2003-06-21 au 2012-09-01, même texte) dit : « Les
  articles 17, 18, 21 et 22 du présent décret prennent effet au 1er août 1995. Les articles 19
  et 20 prennent effet au 1er août 1994. » C'est la lecture a de B5 : 1995-08-01, et non
  2003-06-21. Pour le n° 97-1029, art. 4 (LEGIARTI000006505207, une seule version, depuis le
  1995-08-01), les deux lectures donnent la même date, et la citation de B5 est exacte. **Écart
  moyen** : un point donné pour « non tranché » que la source tranche.
- **L'arrêté du 18 avril 1989, art. 4 (LEGIARTI000006718191).** B5 écrit qu'il « date un
  classement, non le reclassement » et élide la fin de la phrase. Le texte dit : « […] sont
  reclassés à cette même date dans les échelles 3, 4 et 5 conformément au tableau suivant » :
  « cette même date » est le 1er janvier 1989, et c'est bien la date du reclassement. La
  donnée est juste (`effet` vide, version du 1989-01-01), seule la raison est incomplète.
  **Écart faible.**

## 3. Le lecteur, les tests, le chaînage : conformes

- **Le lecteur** ne date que ce qu'il doit. Sur les 450 tableaux du dépôt, seule la colonne
  `effet` change, et seulement sur les 36 cases vides ; les 414 autres sont identiques. Rejoué sur les 540 tableaux de
  l'index publié, les trois motifs nouveaux changent la date de 39 tableaux : les 36, et trois
  qui ne sont pas dans la donnée (LEGIARTI000035634088, « reclassés au 1er janvier 2017 » ;
  LEGIARTI000044845318 et LEGIARTI000044846944, 2022-01-01), tous du motif « reclassés (,)
  au <date> ». Aucune fausse date vue.
- **Les tests** : les valeurs de `DATES_APRES_LE_VERBE` sont les 36 du texte (point 1) ; les
  neuf phrases ajoutées à `test_la_date_du_reclassement_est_celle_que_la_phrase_ecrit`, dont
  celle qui reste sans date, sont dans leur article mot pour mot, avec la date que le texte
  écrit. Réserves faibles : le garde-fou final de `test_la_date_qui_suit_le_verbe…` répète le
  motif du lecteur, donc ne surprendrait pas une forme que le lecteur ignore (voir le point 4) ;
  le commentaire promet « nommés au » (n° 98-268, art. 17) « sans date » et ne le teste pas.
- **Le chaînage** : 862 groupes avant et après, 76 changent, 36 tableaux, uniquement `date` et
  `date_lue` (de vide à `effet`) et, pour 48 groupes, la raison ; aucun statut ne bouge (13
  rattachés, 849 déclarés). Le passage de 183 à 158 est exactement 25 tableaux, tous de
  l'État, qui cessent d'être déclarés « la phrase qui annonce le tableau n'écrit pas la date »
  et le sont pour la raison suivante (« la phrase ne nomme pas le statut du corps reclassé »,
  « plusieurs coupes du libellé », « le Noyau RH ne cite, la veille ni le jour du … ») ; aucun
  tableau n'y entre. Les 36 se répartissent en 30 de l'État, 3 territoriaux, 3 hospitaliers ;
  les 5 de l'État qui ne sont pas parmi les 25 étaient déjà déclarés pour une autre raison
  (« groupe vide »). La note du matin comptait 26 (22 + 4) ; B5 écrit 25 pour le chaînage,
  et 25 est le compte juste.

## 4. Ce que le texte ne tranche pas : à moitié déclaré

B5 déclare trois cas (point 2). Il en reste que le texte date et que ni la donnée ni la note
ne disent. En relisant les 365 tableaux restés sans `effet`, on trouve :

- **Des tableaux que date l'article qui fixe l'entrée en vigueur du décret**, relu en entier
  pour chacun ; en plus des n° 2001-325, art. 14 (1997-01-01) et n° 98-268, art. 17
  (1995-08-01) ci-dessus : n° 98-896, art. 8, version du 2002-03-21 (LEGIARTI000006508629) :
  l'art. 10 (LEGIARTI000006508631) dit « Les dispositions des articles 1er, 6, 7 et 8 du
  présent décret sont applicables à compter du 1er août 1996 » ; n° 2017-1367, art. 23
  (LEGIARTI000035601659, début 2017-09-23) : l'art. 28 (LEGIARTI000035601611) dit « les
  articles 23 à 25 entrent en vigueur le 1er janvier 2017 » ; n° 2017-1494, art. 13, I
  (LEGIARTI000035900888, début 2017-10-28) : l'art. 15 (LEGIARTI000035900898) dit « les
  dispositions du I de l'article 13 entrent en vigueur le 1er janvier 2017 ». Cinq
  tableaux au moins, que la donnée date de leur version (de 8 mois à 8 ans d'écart), que le
  chaînage déclare ou laisse sans date. La recherche est un balayage, non une preuve
  d'exhaustivité : un décret qui parle d'un « chapitre » plutôt que d'un article n'y est pas.
- **« A la même date »** (LEGIARTI000036440010, tableau 2 ; LEGIARTI000034702202, tableau 2) :
  la date est celle du tableau 1 (« Au 1er février 2019 », « Au 1er février 2018 »), que le
  chaînage lit ; celle du tableau 2 reste vide. Territoriaux, déclarés de toute façon.
- **Des dates relatives au décret** (« à la date d'entrée en vigueur du présent décret », « à
  la date d'effet du présent décret », « à la date de publication ») : plus d'une centaine de tableaux ;
  la convention (`effet` vide : l'entrée en vigueur de l'article) les date juste quand l'article
  entre en vigueur avec le décret, moins sûrement pour « la date d'effet du présent décret »
  (un décret peut avoir un effet rétroactif) : à lire décret par décret, non fait ici.

**Écart faible** : l'ancien bloc « Reprise » comptait parmi ce qui reste « les dates d'effet
non lues (dont 26 reclassements datés après "reclassés") » ; le nouveau remplace la parenthèse
par les 36 lues et ne garde que « nommés au ». Les cinq tableaux ci-dessus, les « A la même
date » et les dates relatives restent à faire, et n'y sont plus.

## 5. Le candidat : le lecteur relancé écrit 540 tableaux

Rejoué en mémoire, sans rien écrire (`extraire(None)` de `dila_legi_reclassements.py`, sur
l'index publié) : **610 textes, 540 tableaux, 8 772 lignes, 533 tableaux non lus** ; la
donnée du dépôt en a 532, 450, 7 365 et 456. Le compte de B5 est exact. Sa description ne
l'est pas : « d'autres sortent (n° 95-370, 2006-1732, 2007-1333…) ». Aucun texte ne sort :
les 532 textes du dépôt et ses 450 tableaux sont tous dans la relance, et leurs colonnes sont
identiques une à une (`effet` compris) ; les n° 95-370, 2006-1732 et 2007-1333 sont dans les
deux. La relance ajoute 78 textes et 90 tableaux (76 dans des
textes neufs, 14 dans des textes déjà lus ; 9 avec une date, 81 sans), et 1 407 lignes.

Ce n'est donc pas une divergence à « comprendre » mais une extension. Hypothèse la plus simple,
que cette relecture n'a pas prouvée (l'ancien index n'est plus là) : la donnée a été lue sur
l'index d'avant sa reconstruction du 3 novembre, qui a ajouté 1 938 documents au LEGI (327 817
contre 325 879) sans en retirer un, comme le dit
`2026-11-03-index-durees-d-echelon-et-points-agricoles.md`. Ma réponse : relancer le lecteur
est sûr pour les 450, et ajoute 90 tableaux dont les lignes sont sans `fiabilite`, à certifier
et à chaîner avant qu'aucun test du dépôt ne les accepte ; ce n'est pas une raison de ne pas
la faire, mais c'est une étape, et non une retouche.

## Les preuves

`python -m pytest -m rapide` : 4 501 passés, 8 sautés (2 min 23) ;
`PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 4 296 passés, 213 sautés ;
`tests/test_reclassements.py` et `tests/test_chainage_grilles.py` en entier : 72 passés.
Aucun fichier du dépôt n'a changé pendant la relecture, hors cette note, l'entrée du journal
de veille et la ligne de renvoi au bout de la note de B5.

## Candidats (hors de la tâche, rien n'est corrigé)

1. Dater les cinq tableaux du point 4 (n° 2001-325 art. 14 : 1997-01-01 ; n° 98-268 art. 17 :
   1995-08-01 ; n° 98-896 art. 8 : 1996-08-01 ; n° 2017-1367 art. 23 : 2017-01-01 ; n° 2017-1494
   art. 13, I : 2017-01-01) par l'article « prend effet » / « entre en vigueur » de leur décret,
   et en faire une règle du lecteur, avec l'article cité en preuve ; puis relire les décrets
   qui parlent d'un chapitre. Le propriétaire dit si « entre en vigueur le … » date le tableau
   d'un décret rétroactif comme « prennent effet au … » le fait expressément (n° 98-268,
   n° 2001-325).
2. « A la même date » : lire la date du tableau précédent du même article.
3. Étendre le lecteur aux 90 tableaux de l'index publié, certifier et chaîner (point 5).
