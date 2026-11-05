# Le chaînage lit les dates corrigées ; les trois articles que le LEGI date en vigueur ensemble

Vague 9, B, le 5 novembre 2026. Reprend le candidat de B-bis (`2026-11-05-b-bis.md`,
point 1) et les « autres articles que le LEGI date en vigueur ensemble » du bloc
« Reprise ». Tout ce qui est cité a été rouvert pendant la session, dans la table `doc` de
l'index LEGI (incrément 20261102-213929) et de l'index JORF (incrément 20261103-002311)
récupérés par `dila_index.py --recuperer`, par `dila_cherche.py` (`--num`, `--texte`) ou
par une lecture directe de la table.

## 1. Le chaînage lit `DATES_CORRIGEES`

`Index.versions_sur` (`scripts/fetch/dila_legi_chainage.py`) lisait les dates du LEGI ;
il lit désormais celles que corrige le lecteur des grilles. Valeur attendue, du n° 2018-610 :
son art. 1er (JORFARTI000037193171) « remplace » l'art. 2 du n° 2009-1322, et « Le présent
décret entre en vigueur le 1er janvier 2017. » (art. 2, JORFARTI000037193174) ; la version
du n° 2017-171 (art. 39, JORFARTI000034026752 ; art. 126 : « Les dispositions du présent
décret entrent en vigueur le 1er janvier 2017. »), LEGIARTI000034034492, ne vaut donc à
aucune date. Tests, vus rouges puis verts :
`test_le_chainage_lit_les_dates_corrigees_des_grilles` (un index de deux documents :
`versions_sur` ne rend que LEGIARTI000037196211, sur 2017-2025 comme sur 2017) et
`test_la_preuve_de_la_hors_classe_des_ieeac_ne_cite_pas_le_2017_171` (la ligne de
`chainage/durees.csv`).

Ce qui bouge, la seule ligne que B-bis attendait : n° 71-917, art. 17
(LEGIARTI000037197020), hors classe, du 2017-01-01 au 2025-07-01, dont la preuve citait
« (LEGIARTI000034034492, LEGIARTI000037196211) » et cite « (LEGIARTI000037196211) ». Les
reclassements et `a_lire_au_jorf.csv` ne bougent pas ; les deux autres numéros que
`DATES_CORRIGEES` portait alors ne sont cités par aucune ligne du chaînage.

**La phrase de B-bis** (`data/sources.yaml`, fiche `dila_legi_grilles`) : « aucun indice
du n° 2018-610 au 1er janvier 2017 n'est inférieur à celui du n° 2017-171 (de 0 à 43 points
de plus) ». Juste, relue aux deux articles du JORF : hors classe 971 → 979, 1021 → 1022 ;
principal 566 → 609 (+43), 627 → 633, 691 → 697, 751 → 763, 811 → 821, 865 → 879,
920 → 929, 971 → 979, 1021 → 1022 ; classe normale 483 = 483, 501 → 508, 515 → 525,
560 → 565, 600 → 610, 639 → 649, 676 → 686, 713 → 727, 737 → 744, 767 → 774 ; élève
340 = 340, 359 = 359. Complétée d'une phrase : la colonne « A compter du 1er janvier
2018 » du n° 2017-171 est plus haute que le n° 2018-610 à six échelons (1027 contre 1022,
deux fois ; 698 contre 697 ; 634 contre 633 ; 567 contre 565 ; 490 contre 483), mais elle
n'a jamais valu : le n° 2017-1737, publié le 23 décembre 2017 et « en vigueur le 1er
janvier 2018 » (sa notice), écrit à l'art. 2 du n° 2009-1322 : « les mots : « A compter du
1er janvier 2018 » sont remplacés par les mots : « A compter du 1er janvier 2019 » » (art.
17, JORFARTI000036250727). La phrase vaut donc jusqu'au 31 décembre 2018.

## 2. Les trois articles

**N° 2008-836, art. 14-1-1** (le chef de projet en systèmes et réseaux d'information et de
communication) :

| LEGI | dates au LEGI | texte qui l'écrit, au JORF |
|---|---|---|
| LEGIARTI000031948241 | 2016-02-01 → 2017-02-13 | n° 2016-82, art. 1er (JORFARTI000031942010) ; « Le présent décret entre en vigueur le 1er février 2016. » (art. 3) |
| LEGIARTI000034034377 | 2017-02-13 → 2017-01-01, « jamais en vigueur » | n° 2017-171, art. 8 (JORFARTI000034026698) : « Le tableau figurant à l'article 14-1-1 du même décret est remplacé par le tableau suivant » ; en vigueur le 1er janvier 2017 (art. 126) |
| LEGIARTI000035602721 | 2017-01-01 → 2018-01-01 | n° 2017-1381, art. 2 (JORFARTI000035600863) : la ligne « 10 HEA HEA » « est remplacée par la ligne : « ES HEA HEA » » ; « Les dispositions du présent décret entrent en vigueur le 1er janvier 2017. » (art. 7) |
| LEGIARTI000036489603 | dès le 2018-01-01 | — (hors du chevauchement, non lue) |

Ce qui vaut : du 1er février au 31 décembre 2016, le n° 2016-82 ; dès le 1er janvier
2017, le tableau du n° 2017-171 tel que le n° 2017-1381 l'a corrigé. Les grilles gardaient
celle du n° 2016-82 jusqu'au 12 février 2017, à côté de la nouvelle. **Corrigé** :
`DATES_CORRIGEES` clôt LEGIARTI000031948241 au 2017-01-01. Test :
`test_la_grille_du_chef_de_projet_sric_de_2016_cesse_au_1er_janvier_2017` ; valeurs, du
n° 2016-82 au 31 décembre 2016 : 650, 700, 750, 800, 850, 901, 946, 985, 1015, échelon
spécial HEA ; rien le 1er janvier 2017 ; du n° 2017-171, colonne « A compter du 1er
janvier 2017 », le 15 janvier : 656, 705, 755, 805, 855, 906, 951, 990, 1021.

**N° 2012-1058, art. 4** (les chargés et directeurs de recherche du développement
durable) :

| LEGI | dates au LEGI | texte qui l'écrit, au JORF |
|---|---|---|
| LEGIARTI000034034477 | 2017-01-01 → 2018-01-01 | n° 2017-171, art. 36 (JORFARTI000034026745) : « L'article 4 du décret précité est remplacé par les dispositions suivantes » ; en vigueur le 1er janvier 2017 (art. 126) |
| LEGIARTI000036489841 | 2018-01-01 → 2017-01-01, « jamais en vigueur » | n° 2017-1737, art. 31 (JORFARTI000036250775) : « A compter du 1er janvier 2018 » devient « 2019 » |
| LEGIARTI000037538214 | 2017-01-01 → 2017-09-01 | n° 2018-917, art. 1er, I (JORFARTI000037532992) : « Au 1er janvier 2017, la rubrique relative aux chargés de recherche du tableau figurant à l'article 4 […] est remplacée par le tableau suivant » |
| LEGIARTI000037538231 | dès le 2017-09-01 | n° 2018-917, art. 1er, II : « Au 1er septembre 2017, le tableau figurant à l'article 4 […] est remplacé par les tableaux suivants » |

Le n° 2018-917 (JO du 27 octobre 2018) n'a pas d'article d'entrée en vigueur : ses dates
sont dans son art. 1er, et sa notice dit « le texte entre en vigueur à compter du 1er
janvier 2017 ». Les autres articles lus qui nomment le décret du 17 septembre 2012 ou ces grades
(n° 2017-171, art. 35, 41, 71, 72 ; n° 2017-1381 ; n° 2017-1506 ; n° 2017-195 ; n° 2017-561 ;
n° 2017-853) ne touchent pas l'art. 4. Ce qui vaut : du 1er janvier au
31 août 2017, la rubrique des directeurs de recherche du n° 2017-171 (colonne 2017) et
celle des chargés de recherche du I ; dès le 1er septembre 2017, les tableaux du II.

Deux écarts au LEGI. La rubrique des chargés de recherche de LEGIARTI000034034477 (1re
classe 567…, 2e classe 539…) ne vaut à aucune date : le I la remplace du jour où elle
entre en vigueur. LEGIARTI000037538214 écrit au 1er janvier 2017 le directeur de
recherche de 2e classe du II (« 7 HEB HEB […] 4 963 969 »), quand le n° 2017-171 lui
donne six échelons et un 4e à 962, et qu'aucun texte lu ne touche à cette rubrique avant le
1er septembre 2017. Les grilles mêlaient les deux : chargés de recherche du n° 2017-171
jusqu'au 31 décembre 2017, 7e échelon du directeur de 2e classe dès le 1er janvier 2017.
**Corrigé** : `DATES_CORRIGEES` clôt LEGIARTI000034034477 au 2017-09-01 ;
`RUBRIQUES_ECARTEES` (neuf, `dila_legi_grilles.py`) ôte la rubrique des chargés de
recherche de la première et celle du directeur de recherche de 2e classe de la seconde.
Test : `test_les_chercheurs_du_developpement_durable_en_2017_suivent_le_decret_2018_917` ;
valeurs du JORF, le 30 juin 2017 : 1re classe 574, 612, 690, 767, 833, 894, 933, 978,
1021 ; 2e classe 544, 554, 592, 629, 664, 690 ; directeur de 2e classe 807, 857, 906,
962, 1021, HEA ; le 1er septembre 2017 : plus de chargé de recherche de 1re ni de 2e
classe, plus de grille « Directeurs de recherche Directeur de recherche de classe
exceptionnelle », et le directeur de 2e classe à 807, 857, 906, 963, 1021, HEA, HEB.

**N° 87-1104, art. 1er** (les secrétaires de mairie) : **non tranché, le texte manque.**
LEGIARTI000006370685 (1987-12-31 → 1996-02-08 ; huit échelons et trois provisoires) et
LEGIARTI000006370686 (1995-08-01 → 2017-01-01 ; douze échelons). La seconde vient du
décret n° 96-101 du 6 février 1996, publié le 8 février (JORFTEXT000000191345) ; l'index
JORF n'en garde que les visas et la signature, l'index LEGI que l'article 38 (daté du
1er août 1995), et Légifrance a répondu 403, en ligne de commande comme dans un navigateur
sans tête. Rien n'est corrigé : les grilles gardent les trois échelons provisoires de 1987
(274, 301, 328) jusqu'au 7 février 1996, à côté de la grille à douze échelons du 1er août
1995. **Question au propriétaire** : le n° 96-101 est à lire au JORF (son article qui
modifie le n° 87-1104, sa date d'entrée en vigueur), sur un poste qui ouvre Légifrance.

**Ce que les textes ne tranchent pas** (déclaré dans la fiche `dila_legi_grilles`) : le
n° 2017-171 prend effet six semaines avant sa publication, le n° 2018-917 près de
vingt-deux mois avant ; ni eux ni les n° 2016-82 et 2017-1381 ne contiennent « pension »
ni « rétroactif ». Une pension liquidée entre l'effet et la publication a pu l'être sur la
grille appliquée alors ; sa révision, aucun texte lu ne la dit. Le reclassement des
chargés de recherche dans les grades du II relève de leur statut (n° 2014-1324), non lu.

## Ce qui bouge

| | avant | après |
|---|---|---|
| `etat_legi/echelons.csv` | — | 31 lignes : 10 du chef de projet SRIC closes au 2016-12-31 ; 15 des chargés de recherche (valeurs du I, closes au 2017-08-31) ; le 7e du directeur de 2e classe dès le 2017-09-01 ; 5 du directeur de 1re classe et de classe exceptionnelle (article cité, fin) |
| `etat_legi/grilles.csv` | — | 4 grilles, leur fin |
| `chainage/durees.csv` | — | 2 lignes : la preuve de la hors classe des IEEAC (point 1) ; la raison d'une durée déclarée du n° 94-943, statut de ces chercheurs (LEGIARTI000006473717, « Chargé de recherche de 2e classe »), dont la grille du même nom finit au 2017-09-01 et non au 2018-01-01 |
| `grilles_etat_legi_rang`, `_indice` | 21067, 19943 | 21067, 19943 (empreintes seules) |

`verifier_donnees.py --appliquer` recertifie ; seules les empreintes de ces deux séries
sont gardées dans `certification.json` (les autres sources de `data/brut/` manquent ici),
et `moteur/donnees.json` ne change que par elles. Le nombre de grilles (1794) et de
périodes (21074) de l'État au LEGI ne change pas.

## Candidats pour le propriétaire

- Le chef de projet SRIC : depuis 2017, « ES HEA HEA » entre dans le libellé de sa grille
  (`…-de-l-etat-es-hea-hea`), et l'échelon spécial (HEA) n'y est plus.
- Les grilles des directeurs de recherche du développement durable (n° 2012-1058, art. 4)
  s'arrêtent au 31 décembre 2019 : le II du n° 2018-917 n'a pour elles que deux colonnes
  (1er septembre 2017, 1er janvier 2019), et le lecteur borne la seconde à la colonne 2020
  des tableaux des chargés de recherche.
- Le n° 87-1104 (un cadre d'emplois de la territoriale, que vise le n° 96-101 « relatif à
  la fonction publique territoriale ») est rangé dans `etat_legi`.
