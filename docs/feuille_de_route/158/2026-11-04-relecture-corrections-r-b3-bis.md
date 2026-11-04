# Relecture des retouches du chaînage aux grilles

File R-B3-ter, du 3 au 4 novembre 2026 : relecture indépendante des commits
b15e055, 4361577, a7361b8, efeac83, b08843e, 5f11954 et 25f8b11 de la session
B3-ter (note `2026-11-03-corrections-de-la-relecture-r-b3-bis.md`), qui
corrigent le chaînage d'après la relecture R-B3-bis (fd7dab8, note
`2026-11-03-relecture-corrections-r-b3.md`). Rien n'est repris de B3-ter ni de
mémoire : chaque article et chaque notice cités ici ont été rouverts dans la
table `doc` de l'index LEGI publié (`dila_index.py legi --recuperer`, dump du
13 juillet 2025, à jour de l'incrément 20261102-213929, celui de B3, de R-B3, de
B3-bis, de R-B3-bis et de B3-ter), chaque ligne du Noyau RH dans
`data/reference/grilles/etat/` ; le JORF n'a pas été ouvert. Les contrôles sont
des scripts écrits pour la relecture, hors du dépôt, qui n'empruntent rien au
script du chaînage. L'état d'avant est celui de fd7dab8. Rien n'a été modifié
dans le dépôt, hors cette note.

**Verdict. Les retouches sont justes à la source, et chaque écart de R-B3-bis
est corrigé ; les cinq qui touchent au code ont un test, rouge sur l'arbre de
fd7dab8 pour la raison de l'écart.** L'échelon exceptionnel des majors de
police est au 5e rang de la grille 02777, à l'indice 631, comme le texte. Les
613 lignes de durées rattachées ont, chaque jour, les échelons de leur tableau ;
la coupe rattache 5 lignes de plus, justes au texte ; chaque citation de la
note de B3-ter est mot pour mot. Le décret commun des infirmiers rattache
chacun de ses corps sans erreur (10 lignes sur 26 contrôlées). Les comptes de la
note se refont à l'identique. **Aucun écart grave ni moyen. Deux écarts
faibles** : le « rang » de la colonne `rangs_grille` n'est pas celui du Noyau RH,
sans que l'en-tête le dise ; deux commentaires disent que le n° 91-783 a un
article qui énumère ses corps, et il n'en a pas. **Une remarque en amont**, hors
du chaînage : la grille du LEGI des ingénieurs des études et de l'exploitation
de l'aviation civile de classe normale mêle, en 2017, deux versions d'un même
article. **Un constat**, que ni B3-bis, ni R-B3-bis, ni B3-ter, ni cette
relecture ne pouvaient voir en local : la ligne 170 du script, écrite par
B3-bis, ne se compile pas sous Python 3.11, celui de GitHub (partie 5).

## 1. L'échelon exceptionnel des majors de police : conforme

*Le texte.* Décret n° 2004-1439, art. 23-1 (LEGIARTI000023734900, du 2011-07-01
au 2018-01-01) : « Au 1er juillet 2011, les membres du corps d'encadrement et
d'application de la police nationale sont reclassés conformément au tableau de
correspondance suivant : […] Major de police Major de police Echelon
exceptionnel Echelon exceptionnel Ancienneté acquise 3e échelon 3e échelon
[…] ». Décret n° 2010-564, art. 5, la veille (LEGIARTI000023402803, du
2011-01-01 au 2011-07-01) : « Major de police Echelon exceptionnel (1) 3e
échelon 2e échelon 1er échelon 630 615 597 579 » ; le jour (LEGIARTI000023750120,
du 2011-07-01 au 2012-01-01) : « Major de police Echelon exceptionnel (1) 4e
échelon 3e échelon 2e échelon 1er échelon 631 620 616 598 581 ». L'exceptionnel
est le 4e à l'origine, le 5e à l'accueil.

*Le Noyau RH.* Grille 00420 le 2011-06-30 : rangs 1 à 3 (579, 597, 615), rang 4
« exceptionnel » (630). Grille 02777 le 2011-07-01 : rangs 1 à 4 (581, 598, 616,
620), rang **6** « exceptionnel » (631) ; le rang 5 n'existe pas ce jour-là. Il
naît le 2019-01-01 (échelon 19790, 680 ; 691 en 2020), l'exceptionnel restant au
rang 6 à chaque version. `chainage/reclassements.csv` écrit, pour les majors,
« origine exceptionnel 4 ; accueil exceptionnel 5 » : 5 est la place de
l'exceptionnel parmi les cinq échelons en vigueur le jour, à l'indice du texte,
631. Pour les gardiens de la paix, « origine exceptionnel 12 » : la grille 00422
le 2011-06-30 a, hors provisoire, élève et stagiaire (rangs 1 à 3), onze
échelons puis l'exceptionnel (rang 15, 500) ; le texte de la veille, « Gardien
de la paix Exceptionnel (4) 11e échelon […] 1er échelon […] 500 483 », en fait
le 12e. Les 11 autres groupes rattachés n'ont, au tableau, que des échelons
numérotés (`reclassements/lignes.csv`) : colonne vide, à raison.

*Les autres grilles à échelon exceptionnel ou spécial.* La colonne n'est écrite
que pour les deux groupes ci-dessus ; la règle qui la remplit
(`rang_dans_la_grille`) a été éprouvée sur cinq autres grilles du noyau, rouvertes
au texte quand il est au LEGI :

- 00422 (gardiens de la paix, origine) : ci-dessus, conforme.
- 00613 (professeurs de lycée professionnel hors classe, le 2017-08-31, origine
  d'un des 13 groupes) : rangs 1 à 7 ordinaires (615 à 979), puis rangs 8 à 14
  « exceptionnel », aux mêmes indices. Le tableau (n° 2017-786, art. 157,
  LEGIARTI000034750857) n'a que des échelons numérotés, 7 à 1, placés aux
  rangs 1 à 7 : conforme. Un exceptionnel n'y trouverait pas de place unique, et
  la règle rendrait « aucune » : elle déclarerait, sans deviner.
- 03703 (directeur technique de classe exceptionnelle, le 2020-06-01) : rangs
  1 à 5 (850 à 1027), rang 6 « exceptionnel », hors échelle A ; n° 2010-1641,
  art. 4 (LEGIARTI000041901573) : « Directeur technique de classe exceptionnelle
  Echelon spécial HEA HEA 5ème échelon 1027 1027 […] 1er échelon 850 850 ». Le
  spécial est le 6e : la règle (le spécial est l'unique exceptionnel de la
  grille) le place au 6, juste.
- 02459 (général de brigade de gendarmerie) : un seul échelon, rang 1, hors
  échelle C, de nature « exceptionnel » ; n° 2011-388, art. 1
  (LEGIARTI000023855592) : « Général de brigade Echelon unique HE C ». Le
  lecteur des reclassements écrit l'échelon unique `unique`, au rang 1, qui
  n'est pas dans `NON_NUMEROTES` : la règle le chercherait comme un échelon
  numéroté, trouverait l'exceptionnel et rendrait « aucune ». Un tel groupe
  serait déclaré, non rattaché à tort ; aucun des 862 n'est dans ce cas.
- 00420 (majors, origine) : ci-dessus, conforme.

Les grilles 03703 et 02459 sont tirées au hasard (graine 158114, parmi les 214
grilles du noyau qui ont un échelon « exceptionnel » : 00705, 01289, 01411,
02459, 03703, 03775 ; les quatre autres, hors échelle ou contractuelles, n'ont
pas été rouvertes).

**Faible — le « rang » de `rangs_grille` n'est pas celui du Noyau RH.** L'en-tête
écrit : « rangs_grille : le rang, dans sa grille (élève, stagiaire et
provisoires mis à part), de chaque échelon du groupe que le tableau ne numérote
pas (« accueil exceptionnel 5 ») ». Le chiffre est la place de l'échelon parmi
ceux que la grille a le jour du reclassement ; la colonne `rang` de
`etat/echelons.csv` en dit un autre : 6 pour l'exceptionnel de la grille 02777,
15 pour celui de la grille 00422. Qui joindrait les deux fichiers par le rang
ne trouverait rien pour 02777 le 2011-07-01, et, à partir de 2019, un échelon
ordinaire (680). Rien ne lit encore la colonne ; la docstring de
`periodes_noyau` (« le n-ième rang est donc l'échelon n ») est de même trop
générale : la grille 02777 saute le rang 5 jusqu'en 2019. Le calcul est juste ;
c'est la définition qui manque d'un mot (« sa place ce jour-là, non le rang du
noyau »).

*Le test.* `test_l_echelon_exceptionnel_se_range_a_sa_place_dans_la_grille` et
`test_l_echelon_exceptionnel_des_majors_de_police_est_le_cinquieme_a_l_accueil`
(partie 4).

## 2. Les durées, date par date : conforme

*Le contrôle.* Pour chacune des 613 lignes rattachées de `chainage/durees.csv`,
à chaque jour où l'un de ses échelons commence ou finit sur la période, les
rangs de la grille en vigueur (au LEGI, ceux du fichier d'échelons de son
versant, `etat_legi`, `territoriale`, `hospitaliere` ou `militaires`, rang zéro
mis à part ; au noyau, leur nombre, élève, stagiaire et provisoires mis à part)
face à ceux du tableau (`durees/lignes.csv`, rang zéro mis à part). Aucun jour
ne diffère. Le même script, sur le fichier de fd7dab8, trouve les 8 lignes de
R-B3-bis et elles seules (14 jours). Les comptes se refont : de fd7dab8 à
4361577, rattachées 582 → 587, déclarées 1 185 → 1 190, grades 498 → 502 ; les 8
lignes ôtées et les 13 ajoutées sont celles que la note nomme.

*Les 8 lignes coupées*, chaque morceau rattaché rouvert :

- *Greffier, Greffier principal* : rattachées du 2023-11-01 au 2024-03-01, sur
  LEGIARTI000048278636 (n° 2015-1277, art. 3, du 2023-11-01 au 2024-03-01 :
  « Greffier 13e échelon 651 12e échelon 612 […] »), seule version de ces jours
  (la suivante, LEGIARTI000049196634, vaut depuis le 2024-03-01) ; déclarées du
  2017-01-01 au 2023-11-01, où les deux versions de l'art. 3
  (LEGIARTI000035603091, du 2016-01-01 au 2018-01-01 ; LEGIARTI000036489952, du
  2018-01-01 au 2023-11-01) sont aux non lus du lecteur des grilles
  (`etat_legi/non_lus.csv`, lignes 305 et 306 : « valeurs hors des lignes, dans
  « Greffier principal Echelon spécial - 705 713 723 11 ème échelon - 701 707
  707 » »).
- *Lieutenant-colonel, Commandant* (n° 2016-2008, art. 12) : rattachées du
  2021-01-01 au 2025-06-14, sur LEGIARTI000036490570 et LEGIARTI000036490574
  (n° 2016-2007, art. 3 et 2, du 2018-01-01 au 2025-06-14), où la grille a 8 et
  9 échelons, comme le tableau ; déclarées avant, où elle en a 7 et 8.
  LEGIARTI000036439942 (art. 12, depuis le 2017-12-24) : « A compter du
  1er janvier 2021 : […] 2° Le grade de commandant comprend neuf échelons ;
  3° Le grade de lieutenant-colonel comprend huit échelons » ;
  LEGIARTI000033792383 (du 2017-01-01 au 2017-12-24) : « A compter du
  1er janvier 2020 ». Mot pour mot.
- *Ingénieur des études et de l'exploitation de l'aviation civile de classe
  normale* : rattachée au LEGI du 2017-01-01 au 2018-01-01 ; du 2018-01-01 au
  2025-06-30, la grille a les rangs 2 à 11, et la ligne du noyau (grille 03500,
  corps 00437, du 2017-01-01 au 2025-07-01) couvre ces jours : rien à déclarer.
  La citation de LEGIARTI000037196211 est exacte. Voir la remarque ci-dessous.
- *Technicien supérieur des études et de l'exploitation de l'aviation civile,
  classe principale et classe normale* : au noyau, le premier `debut` des
  grilles 00226 et 00227 est le 2009-10-27 ; rattachées au noyau depuis ce jour,
  au LEGI du 2007-01-01 au 2009-10-31 (LEGITEXT000019798583) : les jours d'avant
  sont couverts.
- *Puéricultrice de classe normale* : déclarée du 2017-01-01 au 2017-05-11,
  rattachée ensuite. Le n° 2014-925, art. 1 : LEGIARTI000029383562 (du
  2014-09-01 au 2016-01-01), LEGIARTI000032546846 (du 2016-01-01 au 2017-05-11,
  qui écrit « classenormale »), LEGIARTI000034729358 (depuis le 2017-05-11).

*Les 5 lignes ajoutées*, rouvertes :

- *Chargés de recherche hors classe* (n° 83-1260, art. 34, LEGIARTI000034794301,
  du 2017-09-01 au 2024-01-01 : « Chargés de recherche hors classe 7e échelon -
  6e échelon 5 ans […] 1er échelon 1 an ») : rattachée du 2017-09-01 au
  2022-05-01 ; le n° 2012-1162, art. 2, LEGIARTI000034774290 (du 2017-09-01 au
  2018-01-01) et LEGIARTI000036489856 (du 2018-01-01 au 2022-05-01) : « régis par
  le décret du 30 décembre 1983 susvisé », « Chargé de recherche hors classe 7e
  échelon HEA HEA HEA 6e échelon 1021 […] » ; LEGIARTI000045731731 (du
  2022-05-01 au 2025-01-01) : « Chargé de recherche hors classe Echelon
  exceptionnel HEB 7e échelon HEA […] » : huit échelons, déclarée ensuite. La
  preuve ne cite que les deux versions du morceau rattaché, comme la note le dit.
- *Infirmier en soins généraux hors classe*, territorial (n° 2012-1420, art. 18,
  LEGIARTI000026796816, du 2013-01-01 au 2016-05-15) : deux lignes, l'une sur la
  grille au singulier (LEGIARTI000026797761, du 2013-01-01 au 2016-01-01 :
  « Infirmier en soins généraux hors classe 11e échelon 700 730 […] »), l'autre
  sur la grille au pluriel (LEGIARTI000032546841, du 2016-01-01 au 2018-01-01 :
  « Infirmiers en soins généraux hors classe 11e échelon 736 - - - […] »).
  Onze échelons chacune, sur son morceau.
- *Lieutenant-colonel, Commandant*, art. 24 du n° 2016-2008
  (LEGIARTI000033792407, du 2017-01-01 au 2017-12-24 : « Jusqu'au 31 décembre
  2019 : […] 2° Le grade de commandant comprend huit échelons ; 3° Le grade de
  lieutenant-colonel comprend sept échelons » ; LEGIARTI000036439940, depuis le
  2017-12-24 : « Jusqu'au 31 décembre 2020 ») : rattachées du 2017-01-01 au
  2021-01-01, sur LEGIARTI000033792732 et 036490570, 033792730 et 036490574,
  déclarées ensuite.

*Les preuves de ces 13 lignes.* Chaque visa cité est dans la notice du texte de
grille, mot pour mot (LEGITEXT000031320442, 033792720, 021214923, 029383554,
026508262, 026797753) ; chaque version nommée nomme le statut, par son numéro ou
par « régis par le décret du … susvisé ». *Le lycée agricole* (n° 90-90,
art. 18, LEGIARTI000034798803) : la grille 03351 a six échelons le seul
2017-09-01, un 7e, sans indice, du 2017-09-02 au 2020-12-31, puis 1015 : la
ligne d'un jour et la déclaration qui la suit sont justes.

**Remarque, en amont du chaînage (faible).** Le LEGI porte, pour l'art. 2 du
n° 2009-1322, deux versions en vigueur ensemble en 2017 : LEGIARTI000034034492
(du 2017-01-01 au 2018-01-01 : « Ingénieur des études et de l'exploitation de
l'aviation civile de classe normale 11 767 774 […] ») et LEGIARTI000037196211
(du 2017-01-01 au 2025-07-01, colonne « Au 1er janvier 2017 » : « 11e 774 780
780 […] », le 1er sous le stagiaire). La grille du dépôt, en 2017, prend le rang
1 (421) à la première et les rangs 2 à 11 à la seconde (`etat_legi/echelons.csv` :
11e à 774, non 767). Le rattachement de 2017 tient (la première version a
onze échelons, comme le tableau) ; les indices de 2017 de cette grille sont un
mélange, que le lecteur des grilles aurait à trancher.

## 3. Le décret commun des infirmiers : conforme ; le n° 91-783 : un commentaire faux

*Le n° 2012-762.* Art. 1 (LEGIARTI000025855207, seule version, depuis le
2012-05-11) : « Sont classés dans la catégorie A prévue à l'article 29 de la loi
du 11 janvier 1984 susvisée et sont régis par le présent décret les corps
ci-dessous énumérés : 1° Le corps des infirmiers de l'Etat qui constitue un
corps à vocation interministérielle relevant du ministre chargé de la santé ;
2° Le corps des infirmiers de la défense ; 3° Le corps des infirmiers de
l'éducation nationale et de l'enseignement supérieur. » Art. 14, à ses quatre
versions (LEGIARTI000025855171, 032526045, 032526029, 044635065) : « […] du temps
passé dans chacun des échelons des grades des corps d'infirmiers régis par le
présent décret est fixée ainsi qu'il suit ». Mot pour mot. Le tableau vaut donc
pour chacun des trois corps : le rattachement à chacun est certain, dès que le
grade du corps porte le libellé du tableau. Au noyau, les corps 01102, 01144 et
01153 ont « 1142:origine » depuis le 2012-06-01 (texte 1142 : n° 2012-762,
MFPF1209447D) ; le seul autre corps qui cite le texte 1142, 00011 (« Infirmiers
des services déconcentrés de la protection judiciaire de la jeunesse »), le cite
comme « abrogateur », et ses grades s'écrivent « Infirmier classe normale PJJ » :
écarté, à raison. Les comptes se refont : de efeac83 à b08843e, 26 lignes
rattachées de plus, 9 grades, 9 déclarations ôtées, 1 ajoutée.

*Dix des 26 lignes* (graine 158115 ; les 26 dans l'ordre du fichier, indices 4,
7, 8, 10, 16, 17, 18, 20, 22, 23) : pour chacune, le grade appartient au corps,
porte le libellé du tableau, a la grille de la ligne, et couvre la période ; le
corps cite le texte 1142 sur toute la période ; 10 sur 10. Le 2017-01-01, deux
grades d'un même libellé valent ensemble dans 01102 et 01153 (les anciens
finissent ce jour-là, inclus) : pour la hors classe et la classe normale,
l'ancienne grille (02947, 02949) a 11 et 9 échelons, la nouvelle (03214, 03216)
10 et 8, comme le tableau de 2017 : seule la nouvelle convient. Pour la classe
supérieure, 7 et 7 : déclaré (« le chaînage ne choisit pas »). Les grades du
01144 s'écrivent, jusqu'en 2021, « … de l'éducation nationale et de
l'enseignement supérieur » : non rattachés, ce que la note dit.

*Le n° 91-783.* La raison écrite dans `durees.csv` (« plusieurs corps du Noyau
RH ont ce grade aux mêmes dates : 00671, 00873 ») est vraie : les deux corps ont
« 112:origine » (n° 91-783) du 1991-08-01 au 2012-09-30. Le rattachement n'est
pas fait parce que `COMMUNS` ne porte que le n° 2012-762 : vrai.

**Faible — le n° 91-783 n'a pas d'article qui énumère ses corps.** Le
commentaire de `COMMUNS` (« Les autres décrets communs (le n° 91-783, les
assistants de service social) ne sont pas lus ») et celui de
`test_deux_corps_qui_citent_le_statut_et_ont_les_memes_grades_ne_se_rattachent_pas`
(« L'article qui énumère les corps de ce décret n'est pas lu ici ») supposent un
tel article. Le n° 91-783 n'en a pas : son art. 1 (LEGIARTI000006461848, du
1992-02-08 au 2007-05-03, puis LEGIARTI000006461849) désigne les corps par leur
catégorie : « Les corps d'assistants de service social des administrations de
l'Etat, classés dans la catégorie B prévue à l'article 29 de la loi du
11 janvier 1984 susvisée, sont soumis aux dispositions communes du présent
décret. » Son tableau (art. 15, LEGIARTI000006461873) s'ouvre sur « La durée
moyenne et la durée minimale du temps passé dans chaque échelon sont fixées
ainsi qu'il suit », sans « régis par le présent décret ». La règle du
n° 2012-762 ne s'y appliquera pas telle quelle ; la session qui rattachera ce
décret aura à écrire la sienne.

*Une précision, non un écart* : la preuve des lignes du n° 2012-762 écrit « les
corps 01102, 01153 ont ce décret pour texte d'origine au Noyau RH » ; c'est vrai
des corps rattachés, et le 01144 l'a aussi.

## 4. Les écarts de R-B3-bis, un à un

Le fichier de tests d'aujourd'hui, lancé dans un arbre de travail détaché au
commit fd7dab8 (script et fichiers d'avant) : **8 rouges, 24 verts**. Chaque
rouge, et sa raison :

- *Moyen, l'exceptionnel des majors.* Corrigé (partie 1). Rouges :
  `test_l_echelon_exceptionnel_se_range_a_sa_place_dans_la_grille`
  (« module 'dila_legi_chainage' has no attribute 'rang_dans_la_grille' ») et
  `test_l_echelon_exceptionnel_des_majors_de_police_est_le_cinquieme_a_l_accueil`
  (« KeyError: 'rangs_grille' »). L'un et l'autre échouent faute de la fonction
  ou de la colonne, non sur une valeur : avant, le seul rang écrit était le 4 de
  `lignes.csv`, faux, et rien ne pouvait dire le 5. La reproduction est juste.
- *Moyen, les échelons date par date.* Corrigé (partie 2). Rouges :
  `test_les_echelons_de_la_grille_sont_ceux_du_tableau_a_chaque_date` (les 8
  lignes, dont « ('Puéricultrice de classe normale', …, '2017-01-01') »),
  `test_un_grade_n_est_pas_rattache_les_jours_ou_sa_grille_n_a_pas_ses_echelons`
  (les greffiers), `test_un_grade_se_rattache_les_jours_ou_sa_grille_a_ses_echelons`
  (« [] == [('charge-de-…', … '2022-05-01')] »).
- *Faible, le n° 60-403.* Corrigé : les trois raisons disent « décret qu'aucune
  notice du LEGI n'identifie, et que le Noyau RH porte sans NOR (texte 166) : le
  chaînage ne l'y identifie que par son NOR » ; `etat/textes.csv`, texte 166 :
  n° 60-403, JORFTEXT000000501563, NOR vide. Rouge :
  `test_la_raison_ne_dit_pas_inconnu_du_noyau_un_decret_qu_il_porte_sans_nor`
  (l'ancienne raison, « ni le LEGI ni le Noyau RH n'identifient »).
- *Faible, « N articles ».* Corrigé : dans les 87 cas `non_lu`, N est le nombre
  des articles de la colonne `articles`, sans exception ; les 7 cas qui changent
  sont ceux que la note nomme (n° 58-778, 6 → 5 ; 84-135, 13 → 5 ; 86-492, 4 →
  1 ; 90-90, 4 → 3 ; 92-1432, 6 → 3 ; 96-1113, 5 → 2 ; 92-843, 3 → 1). Rouge :
  `test_un_article_de_durees_que_le_lecteur_n_a_pas_lu_ne_se_dit_pas_absent_du_legi`
  (« ('58-778', '6', …) assert 6 == 5 »).
- *Faible, deux citations de la note de B3-bis.* Corrigé par un renvoi daté au
  bout de la note (5f11954 n'y ajoute que 13 lignes, n'en ôte aucune) : les
  titres de LEGITEXT000006061489 (jusqu'au 2012-01-01) et LEGITEXT000024751171
  (depuis le 2012-01-01) et le libellé du corps 00409 y sont mot pour mot. Une
  citation de prose n'a pas de test : rien à reproduire.
- *Faible, les infirmiers du n° 2012-762.* Corrigé (partie 3). Rouge :
  `test_un_decret_commun_qui_enumere_ses_corps_rattache_le_grade_a_chacun`
  (« assert set() == {('LEGIARTI00…', …) …} »).

*Les reclassements*, de fd7dab8 à aujourd'hui : 862 groupes, les mêmes, 13
rattachés et 849 déclarés ; seules 4 raisons changent (les brigadiers, les trois
du n° 60-403) et la colonne `rangs_grille` est écrite pour 2 groupes. La
nouvelle raison des brigadiers (« origine « 7-provisoire » (rang 7) : la grille
00421 a 6 échelons hors élève, stagiaire et provisoires, aucun exceptionnel ») est
vraie : le 2011-06-30, rangs 1 à 6 (419 à 533), rang 7 provisoire (541).
`a_lire_au_jorf.csv` : 137 `abime`, 87 `non_lu`, 40 `manque`, avant et après ;
les 87 `non_lu` changent de texte. *Les durées*, de fd7dab8 à aujourd'hui :
1 767 → 1 795 lignes ; rattachées 582 → 613 (+39, −8) ; déclarées 1 185 → 1 182
(+10, −13) ; grades rattachés 498 → 511, 13 gagnés, aucun perdu.

## 5. Les tests et le paquet

Sous Python 3.13, celui du conteneur : `tests/test_chainage_grilles.py`, 32
passés. `python -m pytest -m rapide` : 4 367 passés, 8 sautés, 13 rouges ;
`PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 4 168 passés, 207 sautés,
les mêmes 13 rouges ; tous de `test_pages_en_dossier.py`, les pages toutes
faites que GitHub refait quand `main` bouge. `python scripts/construire_donnees.py`,
puis `git status` : rien de changé ; le paquet ne lit pas `chainage/`.

**Constat — la suite de GitHub est rouge.** `.github/etat_suite.yaml`, sources
cd360d1, le 2026-11-03 à 23 h 36 UTC : « ERROR tests/test_chainage_grilles.py
[…] python3.11 […] in importtestmodule », dans la course ordinaire comme dans
celle des présomptions. La ligne 170 de `scripts/fetch/dila_legi_chainage.py`,
`return rf"{r'1(?:\s*er)?' if jour == 1 else jour}\s+{nom}\s+{annee}"`, met une
barre oblique inverse dans l'expression d'une f-string, ce que Python n'admet
que depuis 3.12. `python3.11 -c "import ast; ast.parse(…)"` sur le fichier :
« SyntaxError: f-string expression part cannot include a backslash » ;
`python3.12` : accepté. GitHub lance la suite sous Python 3.11
(`.github/workflows/tests.yml` : `python-version: "3.11"`) ; `pyproject.toml`
promet `requires-python = ">=3.10"`. La ligne vient de c4b22e5 (B3-bis), non des
commits relus ici ; B3-bis, R-B3-bis, B3-ter et cette relecture ont lancé leurs
tests sous Python 3.13, qui l'accepte. Une session (B3-quater) la répare ; rien
n'est corrigé ici.

## Ce que la relecture laisse

- Dire, dans l'en-tête de `chainage/reclassements.csv` et la docstring de
  `periodes_noyau`, que le rang est la place de l'échelon parmi ceux de la
  grille ce jour-là, non la colonne `rang` du noyau (6, non 5, pour la grille
  02777).
- Récrire les deux commentaires sur le n° 91-783 : pas d'article qui énumère les
  corps ; un art. 1 qui les désigne par catégorie, un tableau sans « régis par le
  présent décret ».
- Ranger l'échelon `unique` du lecteur des reclassements avec l'exceptionnel du
  noyau, quand la grille n'a que lui (n° 2011-388, art. 1, « Echelon unique HE
  C » ; grille 02459), si un groupe en a un jour besoin.
- Trancher, au lecteur des grilles, les versions qui se chevauchent d'un même
  article (n° 2009-1322, art. 2, en 2017).
- Compiler le code sous Python 3.11 avant d'envoyer : `python3.11` est dans le
  conteneur.
