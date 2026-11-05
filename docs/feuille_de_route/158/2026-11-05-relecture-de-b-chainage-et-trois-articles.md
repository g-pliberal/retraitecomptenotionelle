# Relecture de B : le chaînage corrigé et les trois articles

Vague 9, R-B2, le 5 novembre 2026. Relecture indépendante du commit d9bfae9 (B, note
`2026-11-05-chainage-corrige-et-trois-articles.md`) et, au passage, de la déclaration de
B-bis (b80f490, fiche `dila_legi_grilles` de `data/sources.yaml`). Tout ce qui suit a été
rouvert pendant la relecture, dans les index du dépôt récupérés par
`dila_index.py --recuperer` (LEGI à jour au 20261102-213929, JORF au 20261103-002311, les
mêmes que B), par `dila_cherche.py --texte` ou une lecture directe de la table `doc`.

**Verdict : conforme sur toutes les valeurs, toutes les dates et le code ; un écart moyen
(point 3 : ce que l'index JORF garde du n° 96-101) et deux écarts mineurs (points 2.1
et 2.2).**

## Ce qui a bougé, et rien d'autre

Les deux lecteurs (`dila_legi_grilles.py`, puis `dila_legi_chainage.py`) relancés, sur le
même index, dans deux arbres de travail tirés de b80f490 et de d9bfae9 : chacun refait à
l'octet près les fichiers commités à son commit. Le diff de d9bfae9 est donc tout ce que
le code change, et il se réduit à ce que B annonce : 31 lignes d'échelons (10 du chef de
projet SRIC, 6 et 9 des chargés de recherche de 2e et de 1re classe, 3 du directeur de
1re classe, le 7e du directeur de 2e classe, 2 de la classe exceptionnelle), 4 grilles,
2 lignes du chaînage ; `reclassements.csv` et `a_lire_au_jorf.csv` intacts ; 1794 grilles
et 21074 périodes avant comme après. Aucune ligne du chaînage ne cite les quatre versions
touchées (LEGIARTI000031948241, 034034477, 037538214, 037538231), ni plus
LEGIARTI000034034492. Dans `certification.json` et `moteur/donnees.json`, seules les
empreintes de `grilles_etat_legi_rang` et `_indice` changent (21067 et 19943 identiques).
Les cinq tests neufs passent.

## 1. Le chaînage lit `DATES_CORRIGEES` : conforme

- Le LEGI date LEGIARTI000034034492 du 2017-01-01 au 2018-01-01, LEGIARTI000037196211 du
  2017-01-01 au 2025-07-01, et l'art. 17 du n° 71-917 (LEGIARTI000037197020) du 2017-01-01
  au 2025-07-01 : les dates du test et de la ligne du chaînage sont exactes.
- Au JORF, mot pour mot : n° 2018-610, art. 1er (JORFARTI000037193171, publié le 14 juillet
  2018), « L'article 2 du décret n° 2009-1322 […] est remplacé par les dispositions
  suivantes », qui nomme « le décret du 8 novembre 1971 susvisé » ; art. 2
  (JORFARTI000037193174) : « Le présent décret entre en vigueur le 1er janvier 2017. » ;
  n° 2017-171, art. 39 (JORFARTI000034026752) et art. 126 (JORFARTI000034026585) : « Les
  dispositions du présent décret entrent en vigueur le 1er janvier 2017. »
- Les deux tests tirent leur attente du texte (la version du n° 2018-610 seule), non du
  code. La preuve de la hors classe ne cite plus que LEGIARTI000037196211.
- **La phrase de B-bis** (« de 0 à 43 points de plus ») : les 22 paires refaites à la main
  aux deux tableaux du JORF, toutes justes (hors classe 971 → 979, 1021 → 1022 ; principal
  566 → 609, 627 → 633, 691 → 697, 751 → 763, 811 → 821, 865 → 879, 920 → 929, 971 → 979,
  1021 → 1022 ; classe normale 483 = 483, 501 → 508, 515 → 525, 560 → 565, 600 → 610,
  639 → 649, 676 → 686, 713 → 727, 737 → 744, 767 → 774 ; élève 340, 359 égaux) ; le
  1er échelon de la classe normale du n° 2017-171 (421), que le n° 2018-610 n'a plus, B-bis
  l'apparie au stagiaire (434, + 13) et le déclare (« ce que le texte ne dit pas »).
- **L'ajout de B** : la colonne « A compter du 1er janvier 2018 » du n° 2017-171 dépasse le
  n° 2018-610 à six échelons, de 1 à 7 points (1027 contre 1022 deux fois, 698 contre 697,
  634 contre 633, 567 contre 565, 490 contre 483) : exact. Le n° 2017-1737, art. 17
  (JORFARTI000036250727), publié le 23 décembre 2017, écrit bien : « Aux articles 1er, 2,3
  et 5, les mots : « A compter du 1er janvier 2018 » sont remplacés par les mots : « A
  compter du 1er janvier 2019 » », et sa notice : « le décret entre en vigueur le 1er janvier
  2018 ». Remarque, sans conséquence : la borne « jusqu'au 31 décembre 2018 » est prudente ;
  aux colonnes de 2019 non plus, aucun indice du n° 2018-610 n'est inférieur (de 0 à
  48 points), et le n° 2018-610 était publié dès le 14 juillet 2018.

## 2. Les deux articles corrigés

### 2.1 N° 2008-836, art. 14-1-1 (le chef de projet SRIC) : conforme, un écart mineur

- Au JORF : n° 2016-82, art. 1er (JORFARTI000031942010), le tableau 650, 700, 750, 800, 850,
  901, 946, 985, 1015, échelon spécial HEA ; art. 3 : « Le présent décret entre en vigueur
  le 1er février 2016. » (la suite de l'article n'abroge que deux textes de NBI) ;
  n° 2017-171, art. 8 (JORFARTI000034026698), mot pour mot, colonne 2017 : 656, 705, 755,
  805, 855, 906, 951, 990, 1021, et « 10 HEA HEA » ; n° 2017-1381, art. 2
  (JORFARTI000035600863) : « la ligne : « 10 HEA HEA » est remplacée par la ligne : « ES HEA
  HEA » » ; art. 7 : « Les dispositions du présent décret entrent en vigueur le 1er janvier
  2017. » Aucun autre texte de l'index JORF ne nomme l'art. 14-1-1 de 2015 à 2019.
- Au LEGI : LEGIARTI000031948241 du 2016-02-01 au 2017-02-13, LEGIARTI000034034377 « jamais
  en vigueur » (2017-02-13 → 2017-01-01), LEGIARTI000035602721 du 2017-01-01 au 2018-01-01.
  La clôture au 31 décembre 2016 est juste ; les dix lignes et la grille l'ont.
- **Écart mineur.** Le test fige la grille du 15 janvier 2017 à neuf indices, sans
  l'échelon spécial HEA que porte la colonne même qu'il cite (« ES HEA HEA »). C'est le
  défaut que B déclare candidat (« ES HEA HEA » entré dans le libellé de la grille), mais le
  test le tient pour une valeur du texte : l'attente n'est pas tout à fait tirée de la
  source, et il faudra la changer avec le défaut. Effet de la correction : depuis le
  1er janvier 2017, et non plus depuis le 13 février, la grille n'a plus d'échelon HEA.

### 2.2 N° 2012-1058, art. 4 (les chercheurs du développement durable) : conforme, un écart mineur

- Au JORF, mot pour mot : n° 2017-171, art. 36 (JORFARTI000034026745), colonne 2017 :
  directeur de 2e classe 807, 857, 906, 962, 1021, HEA (six échelons) ; chargé de 1re
  classe 567, 605, 683, 760, 826, 887, 926, 971, 1021 ; de 2e classe 539, 547, 585, 622, 658,
  683. N° 2018-917, art. 1er (JORFARTI000037532992, publié le 27 octobre 2018), I : « Au
  1er janvier 2017, la rubrique relative aux chargés de recherche du tableau figurant à
  l'article 4 […] est remplacée par le tableau suivant » : 1re classe 574, 612, 690, 767,
  833, 894, 933, 978, 1021 ; 2e classe 544, 554, 592, 629, 664, 690 ; II : « Au
  1er septembre 2017, le tableau […] est remplacé par les tableaux suivants » : directeur de
  2e classe 807, 857, 906, 963, 1021, HEA, HEB ; chargé de classe normale 544, 592, 658,
  710, 767, 833, 894, 933, 978, 1021 ; hors classe 767, 814, 863, 918, 978, 1021, HEA. Son
  art. 2 est l'article d'exécution ; sa notice : « le texte entre en vigueur à compter du
  1er janvier 2017 ». N° 2017-1737, art. 31 (JORFARTI000036250775) : « A compter du 1er
  janvier 2018 » devient « 2019 » aux articles 1, 4, 16 à 18.
- Les lignes refaites à la main, toutes justes : les 15 des chargés de recherche, du
  2017-01-01 au 2017-08-31 (valeurs du I) ; le directeur de 2e classe, 962 jusqu'au
  2017-08-31, 963 et un 7e échelon (HEB) dès le 2017-09-01, puis 814, 863, 913, 969, 1027
  en 2019 ; la classe exceptionnelle (HED, HEE) close au 2017-08-31 sous son libellé de
  2017 et reprise au 2017-09-01 sous celui du II ; la classe normale et la hors classe
  dès le 2017-09-01 et en 2019.
- `RUBRIQUES_ECARTEES` n'écarte que ce que le texte écarte. Le LEGI, relu :
  LEGIARTI000034034477 porte, mot pour mot, le tableau du n° 2017-171 ; ses deux rubriques de
  chargés de recherche sont celles que le I remplace du jour même. LEGIARTI000037538214
  (2017-01-01 → 2017-09-01) mêle le II (directeur de 2e classe à sept échelons, 963 ;
  tableaux de la classe normale et de la hors classe) au I, et garde en colonne 2019 les
  anciens indices de 2018 du n° 2017-171 (1027, 977, 932…) : seule la rubrique du directeur
  de 2e classe est ôtée ; les tableaux datés du 1er septembre 2017 et la colonne 2019 n'y
  produisent rien, la version finissant le 1er septembre. Aucun autre article de l'index
  JORF, de juin 2016 à 2020, ne touche à l'art. 4 : les n° 2016-792, 2017-195, 2017-1381,
  2017-1506, 2017-1737 (art. 80), 2020-614 et 2020-1646, et les art. 35, 41 et 42 du
  n° 2017-171, visent d'autres articles.
- Remarque. Les lignes du directeur de 1re classe et de la classe exceptionnelle de 2017
  citent désormais LEGIARTI000037538214, la version du I, et non LEGIARTI000034034477 :
  mêmes indices, même rubrique, que le n° 2017-171, art. 36, écrit ; la citation reste
  défendable (la version consolidée en vigueur au LEGI), mais la source normative de cette
  rubrique est le n° 2017-171.
- **Écart mineur (déclaration).** La fiche ne nomme, entre l'effet et la publication du
  n° 2018-917, que « [une pension] de chargé de recherche du développement durable
  liquidée du 1er janvier 2017 au 27 octobre 2018 ». Le II touche aussi, dès le 1er septembre
  2017, le directeur de recherche de 2e classe (4e échelon de 962 à 963, un 7e échelon à
  HEB) : une pension de directeur liquidée du 1er septembre 2017 au 27 octobre 2018 est dans
  le même cas, et n'est pas nommée.

## 3. N° 87-1104, art. 1er : la conclusion tient, la description est fausse (écart moyen)

- Exact : LEGIARTI000006370685 (1987-12-31 → 1996-02-08 ; huit échelons, 342 à 620, et trois
  provisoires 274, 301, 328) ; LEGIARTI000006370686 (1995-08-01 → 2017-01-01 ; douze
  échelons, 374 à 695) ; les grilles gardent les trois provisoires jusqu'au 1996-02-07, à
  côté des douze échelons du 1995-08-01. Le LEGI n'a du n° 96-101 que son texte
  (LEGITEXT000005620312, visas et signature) et l'art. 38 (LEGIARTI000006377880, daté du
  1995-08-01). Ni l'un ni l'autre index n'a l'article du n° 96-101 qui récrit l'art. 1er du
  n° 87-1104, ni celui qui dit son entrée en vigueur : « non tranché » tient.
- **Faux** : « l'index JORF n'en garde que les visas et la signature » (note de B, fiche
  `dila_legi_grilles`, journal de veille ; « manque aux index », au bloc « Reprise »).
  L'index JORF garde, outre le texte (JORFTEXT000000191345), sept articles, rangés sans
  numéro mais qui le portent en tête : art. 1er (JORFARTI000001400977, n° 87-1099), art. 2
  (JORFARTI000001790554, n° 87-1103), art. 10, 25, 27, 33 et 38.
- Ce que B n'a pas vu, et qui touche la question :
  - L'art. 2 récrit le statut des secrétaires de mairie (n° 87-1103) : « catégorie B »
    devient « catégorie A » (I, V) ; « huit échelons » devient « douze échelons » (IX) ;
    XII : « Sont créés, à la base du grade de secrétaire de mairie, des 1er, 2e et 3e
    échelons provisoires, dotés respectivement des indices bruts 301, 328 et 342 […]. Le
    reclassement dans ces échelons s'effectue conformément au tableau fixé par l'article 37
    du décret no 96-101 » ; XIII, à l'art. 28-1 : « Pour l'application de l'article 16 bis
    du décret no 65-773 […] relatif au régime de retraite des fonctionnaires affiliés à la
    C.N.R.A.C.L., les assimilations […] sont effectuées […] à compter de la date de
    publication du décret no 96-101 du 6 février 1996 ».
  - Le LEGI date ces articles du statut comme l'art. 1er du n° 87-1104 : art. 14, huit
    échelons jusqu'au 1996-02-08 (LEGIARTI000006370658), douze dès le 1995-08-01
    (LEGIARTI000006370659) ; art. 25-1 dès le 1995-08-01 (LEGIARTI000006370673) ; l'art. 28-1,
    lui, dès le 1996-02-08 (LEGIARTI000006370679).
  - La fiche du texte au JORF porte un résumé analytique, qui n'est pas le texte : « LA
    PRINCIPALE MODIFICATION INTERESSE LE CADRE D'EMPLOIS DES SECRETAIRES DE MAIRIE,CLASSE EN
    CATEGORIE A,A COMPTER DU 01-08-1995. »
  - L'index renvoie les tableaux au papier : « JO no 0033 du 08/02/96 Page 2070 a 2077 ».
- Gravité : moyenne. Aucune valeur ni date n'est fausse, et rien n'est tranché par ce qui
  précède : le résumé n'est pas normatif, et l'article qui récrit le n° 87-1104 reste
  introuvable. Mais un fait écrit en quatre endroits est faux, et la question au
  propriétaire se resserre : lire, au JO n° 33 du 8 février 1996 (p. 2070 à 2077),
  l'article du n° 96-101 qui récrit l'art. 1er du n° 87-1104, son art. 37 (le tableau de
  reclassement) et l'article qui dit son entrée en vigueur. Et la fiche, qui déclare ce que
  les textes ne tranchent pas des pensions, se tait sur une règle écrite : pour la
  péréquation des pensions de la CNRACL, l'assimilation part de la publication du
  n° 96-101 (art. 2, XIII).

## 4. Ce que les textes ne tranchent pas : déclaré, à deux omissions près

- Exact : le n° 2017-171 publié le 12 février 2017 pour un effet au 1er janvier (six
  semaines), le n° 2018-917 publié le 27 octobre 2018 pour un effet au 1er janvier 2017
  (vingt-deux mois) ; ni « pension » ni « rétroactif » (toutes casses, « rétroacti » compris)
  dans les 5 documents du n° 2016-82, les 128 du n° 2017-171, les 9 du n° 2017-1381, les 3
  du n° 2018-917 ; ni dans les 4 du n° 2018-610. Les indices du I dépassent ceux du
  n° 2017-171 de 0 à 7 points : exact.
- Omissions : le directeur de recherche de 2e classe (point 2.2) ; la règle de péréquation
  du n° 96-101 (point 3).

## 5. La déclaration de B-bis (b80f490) : conforme

Les citations du n° 2018-610 et du n° 2017-171 (point 1) ; les 128 documents du
n° 2017-171 et les quatre du n° 2018-610 (le texte et trois articles), sans « pension » ni
« rétroactif » ; les délais (six semaines, plus de dix-huit mois) ; la grille 03500 du Noyau
RH (`grilles/etat`), du 2017-01-01 au 2018-12-31 : 434, 483, 508, 525, 565, 610, 649, 686,
727, 744, 774, ses textes (n° 2009-1322, 71-917, 2018-610, 2018-609) sans le n° 2017-171.

## Candidats (hors de la tâche)

- Les échelons provisoires du statut des secrétaires de mairie (n° 87-1103, art. 25-1,
  LEGIARTI000006370673 : 301, 328, 342, du 1995-08-01 au 2017-01-01) ne sont pas dans la
  grille du n° 87-1104 de ces années, que les grilles ne lisent qu'au décret
  d'échelonnement. À vérifier.
- Les trois candidats de B, relus : l'échelon spécial du chef de projet SRIC (confirmé, et
  figé par le test, point 2.1) ; les grilles des directeurs de recherche closes au
  31 décembre 2019 ; le n° 87-1104 rangé à l'État.
