# Relecture du chaînage des durées et des reclassements aux grilles

File R-B3, le 3 novembre 2026 : relecture indépendante du commit 6774a5f de la
session B3 (« Action 158, étape 3 : le chaînage des durées et des reclassements
aux grilles » ; note `2026-11-03-etape-3-chainage-aux-grilles.md`). Rien n'est
repris de la session ni de mémoire : chaque article et chaque notice cités
ci-dessous ont été rouverts ici, dans la table `doc` de l'index LEGI publié du
dépôt (`dila_index.py legi --recuperer`, dump du 13 juillet 2025, à jour de
l'incrément 20261102-213929, le même que B3), et chaque ligne du Noyau RH dans
`data/reference/grilles/etat/`. Les contrôles sont des scripts écrits pour la
relecture, hors du dépôt ; ils n'empruntent au script de B3 que `normaliser`
(l'égalité des libellés, règle de B3), `intersection` et la lecture des visas,
dans les seuls comptes qui le disent. Les échelons des tableaux et des grilles
sont ceux de `durees/lignes.csv` et de `grilles/<versant>/echelons.csv`,
certifiés et relus avant cette étape ; le texte a été rouvert pour le lien, le
libellé et la période, et pour les échelons des cas cités. Rien n'a été
modifié dans le dépôt, hors cette note.

**Verdict. Deux écarts graves, aux reclassements : 5 des 18 groupes rattachés
le sont au mauvais corps.** Le décret n° 2016-581, art. 12, reclasse les
géomètres de l'IGN ; le chaînage les rattache au corps des
géomètres-cadastreurs des finances publiques, avec ses grades et ses grilles
(3 groupes). Le décret n° 2017-786, art. 164, reclasse les professeurs des
écoles du corps créé pour la Polynésie française ; le chaînage les rattache au
corps métropolitain (2 groupes). **Des écarts moyens** : un défaut du script
écrase 654 des 971 corps du Noyau RH, d'où 10 rattachements que la règle « un
seul corps » aurait refusés et 20 raisons fausses ; 11 preuves disent « le
corps cite » ce que seul un de ses grades cite ; 87 des 127 cas `manque` de
`a_lire_au_jorf.csv` disent du LEGI ce qu'il ne dit pas. **Aux durées,
l'échantillon (32 rattachements) est juste au fond**, sans exception ; des
écarts faibles de preuve, comptés sur tout le fichier. Les 22 déclarations
tirées ont 21 raisons vraies. Le piège du n° 2017-171 et la date « Au
1er septembre 2017 » sont exacts à la source. Les lignes changées hors du
chaînage ne sont que de la documentation. Les tests sont verts et tirent
leurs valeurs des textes, mais aucun n'aurait vu les deux écarts graves.

## L'échantillon, pour le refaire

Graine 158003 (Python, `random.Random(158003)`). *Durées* : les lignes
`statut = rattache` de `chainage/durees.csv`, dans l'ordre du fichier,
groupées par (`source`, `lien`), les huit groupes pris dans l'ordre trié, et
dans chacun `sorted(rng.sample(indices, 4))` : 32 lignes. *Déclarés* : les
lignes `declare` de `durees.csv` rangées par famille de raison (groupe vide,
versions qui se chevauchent, plusieurs grilles, échelons, texte commun,
période, aucun texte, libellé), deux par famille dans l'ordre trié, puis
celles de `reclassements.csv` (date, coupe, aucun corps, plusieurs coupes,
versant, groupe vide), une par famille, du même générateur : 22 cas.
*A lire au JORF* : trois cas `abime` puis deux `manque`, `rng.sample`, du
même générateur remis à la graine : 5 cas. Les comptes de B3 se refont à
l'identique : 1 675 grades, 498 rattachés, 778 tableaux ; 862 groupes de
reclassement, 18 rattachés ; 137 cas `abime`, 127 `manque`.

## 1. Les rattachements

### 1 a. Les durées, 32 tirés : justes au fond

Chaque ligne : le statut, le grade, la grille (texte, article), le lien, la
période, puis ce qui a été lu.

- *Noyau.* (1) n° 91-1025, « Médecin inspecteur de santé publique », corps
  00040, grade 00089, grille 00097, [2000-10-01, 2017-01-01) : le corps cite le
  texte 250 (n° 91-1025), neuf échelons de part et d'autre. (2) n° 90-90,
  « Professeur de lycée professionnel agricole hors classe », grille 03351, le
  seul 2017-09-01 : six échelons ce jour-là, sept dès le lendemain (échelon 7
  sans indice jusqu'au 2020-12-31) ; juste, mais rattachement d'un jour, fait
  d'une version de grade d'un jour du noyau. (3) même statut, classe normale,
  grille 03352, [2021-01-01, 2023-09-01) : onze échelons, deux versions de
  l'article (LEGIARTI000034809942, LEGIARTI000044270202). (4) n° 2010-986,
  « Inspecteur des finances publiques », corps 01012 (cite le texte 737),
  grade 04326, grille 03404, [2017-01-01, 2021-01-01) : onze échelons et le
  stagiaire. Conformes.
- *État, lien `article`.* (5) n° 2003-770, « Directeur du travail hors
  classe » → n° 2017-132, art. 1 (LEGIARTI000033992431, LEGIARTI000036489986) :
  « aux membres du corps de l'inspection du travail régis par le décret du
  20 août 2003 susvisé ». (6) n° 83-1260, « Ingénieur de recherche de
  1re classe » → n° 2012-1162, art. 3 (trois versions) : « aux corps des
  ingénieurs de recherche régis par le décret du 30 décembre 1983 susvisé ».
  (7) n° 93-752, « Professeur technique de classe normale » → n° 2012-1058,
  art. 5 : « aux professeurs techniques de l'enseignement maritime régis par
  le décret du 29 mars 1993 susvisé » ; aucun autre visa du 29 mars 1993.
  (8) n° 2015-1275, « Greffier » → n° 2015-1277, art. 3 : « au corps des
  greffiers des services judiciaires régi par le décret n° 2015-1275 du
  13 octobre 2015 susvisé ». Conformes au fond ; (7) et (8) ont un écart de
  preuve, point 1 c.
- *État, lien `visa`.* (9) n° 94-464, « Educateur de 1re classe » → arrêté du
  3 juin 1994, qui ne vise que les n° 48-1108 et 94-464. (10, 11) n° 2002-811,
  « Ingénieur en chef », « Ingénieur principal » → n° 2017-1359, qui vise le
  n° 2002-811 et le n° 2013-1135, « relatif aux emplois de directeur et de
  directeur adjoint de laboratoire », statut d'emploi, non de corps ; l'art. 1
  fixe l'échelonnement « des emplois de directeur et directeur adjoint de
  laboratoire […] et du corps des ingénieurs de police technique et
  scientifique ». (12) n° 2016-1195, « Attaché statisticien principal » →
  n° 2016-1196. Conformes.
- *Hospitalière.* (13, 14, 15) n° 91-868, ingénieurs hospitaliers → arrêté du
  16 novembre 2018, art. 3 : « régis par le décret du 5 septembre 1991
  susvisé » ; les autres visas sont du 3 février 1993 et du 16 novembre 2018.
  (16) n° 2020-244, « Premier grade : classe normale » → n° 2021-1259, art. 1 :
  « régi par le décret du 12 mars 2020 susvisé ». (17) n° 91-936, « Agents-chefs
  de 1re catégorie » → arrêté du 4 avril 2008 (seul statut visé ; l'autre visa,
  le n° 2008-323, est « relatif au classement indiciaire »). (18) n° 2015-1048, « classe
  supérieure », tableau 3 → n° 2021-1264, art. 2. (19) n° 2017-984, « Premier
  grade » → arrêté du 10 mai 2017. (20) n° 2024-52, « Ingénieur » → n° 2024-53.
  Conformes ; (18) a un écart de preuve, point 1 c.
- *Militaires.* (21, 22, 24) n° 2008-944 et n° 2010-1239, « Ingénieur
  principal – Echelle de solde n° 2 », « Ingénieur – Echelle de solde n° 1 » →
  n° 2011-1235, art. 2 (LEGIARTI000052464840) : « L'échelonnement indiciaire
  applicable aux corps d'officiers de l'armement, régis par le décret
  n° 2008-944 […], et celui applicable au corps des ingénieurs militaires
  d'infrastructure de la défense, régis par le décret n° 2010-1239 […], sont
  fixés comme suit » : un tableau pour les deux statuts. (23) n° 2008-952,
  « Maréchal des logis-chef » → n° 2011-388, art. 2 : « régis par le décret
  n° 2008-952 du 12 septembre 2008 susvisé ». Conformes.
- *Territoriale.* (25, 26) n° 2010-329, « Troisième grade » → n° 2010-330,
  art. 1 : « aux membres des cadres d'emplois régis par le décret du 22 mars
  2010 susvisé ». (27) n° 2016-336, « Cadre de santé » → n° 2016-337, art. 1.
  (28) n° 2016-2008, « Lieutenant-colonel » → n° 2016-2007, art. 3 : « aux
  lieutenants-colonels de sapeurs-pompiers professionnels régis par le décret
  n° 2016-2008 ». (29) n° 2013-490 → n° 2013-493 ; (30) n° 2016-200,
  « INGENIEUR EN CHEF HORS CLASSE » → n° 2016-202 : huit échelons de part et
  d'autre (le 8e : « HEB bis »), lus à l'art. 18 et à l'art. 1 ; (31, 32)
  n° 2016-201, « Ingénieur » → n° 2016-203 (les visas : n° 85-730 et n° 85-1148,
  de rémunération, et le statut). Conformes ; (26) a un écart de preuve,
  point 1 c.

### 1 b. Les reclassements, les 18 : deux écarts graves

- *Conformes (13).* N° 2004-1439, art. 23-1 : « Au 1er juillet 2011, les
  membres du corps d'encadrement et d'application de la police nationale sont
  reclassés », corps 00172, qui cite le texte 296 (n° 2004-1439) ; majors,
  brigadiers-chefs, gardiens de la paix (3). N° 2017-1031, art. 39 : « le corps
  des professeurs de lycée professionnel agricole régi par le décret n° 90-90 »,
  corps 00003 (2). N° 2017-786 : art. 139, « le corps des professeurs des écoles
  régi par le décret du 1er août 1990 » (le visa : n° 90-680), corps 00021 (2) ;
  art. 157, « décret du 6 novembre 1992 » (n° 92-1189), corps 00250 (2) ;
  art. 36, « décret du 12 août 1970 » (n° 70-738), corps 00493 (1) ; art. 123,
  « décret du 14 mars 1986 » (n° 86-492), corps 00490 (1). N° 2019-50, art. 24
  (« Au 1er février 2019 », corps 01140 intégré au 01230, que le noyau donne
  pour suivant) et art. 37 (« Au 1er janvier 2021 ») (2). Grades d'origine et
  d'accueil en vigueur la veille et le jour, échelons des lignes parmi ceux des
  grilles.
- **Grave — les géomètres de l'IGN rattachés aux géomètres-cadastreurs (3
  groupes).** N° 2016-581, art. 12 (LEGIARTI000032523172) : « I. - Au
  1er janvier 2016, les fonctionnaires appartenant au corps des géomètres de
  l'Institut national de l'information géographique et forestière régi par le
  décret du 20 janvier 1967 susvisé […] sont reclassés dans ce même corps ». Le
  visa : « Vu le décret n° 67-91 du 20 janvier 1967 modifié relatif au statut
  particulier des géomètres de l'Institut national de l'information
  géographique et forestière ». Le chaînage rattache « Géomètre principal
  Géomètre principal », « Technicien géomètre Géomètre » et « Géomètre
  Géomètre principal » au corps 01005, « Géomètres-cadastreurs des finances
  publiques » (n° 2010-983, que le même décret vise aussi), grades 02699,
  02700, 02701, grilles 01924, 01925, 01926. Le corps de l'IGN est au noyau
  (00395, « Géomètres de l'Institut national de l'information géographique et
  forestière », du 1967-02-03 au 2024-12-31). Corps, grades et grilles faux.
- **Grave — les professeurs des écoles de Polynésie rattachés au corps
  métropolitain (2 groupes).** N° 2017-786, art. 164 (LEGIARTI000034750879) :
  « Au 1er septembre 2017, les fonctionnaires appartenant au corps des
  professeurs des écoles régi par le décret du 23 décembre 2003 susvisé […]
  sont reclassés ». Le visa : « Vu le décret n° 2003-1260 du 23 décembre 2003
  modifié fixant les dispositions statutaires applicables aux professeurs des
  écoles du corps de l'Etat créé pour la Polynésie française ». Le chaînage
  rattache « Professeur des écoles hors classe » et « … de classe normale » au
  corps 00021, « Professeurs des écoles de l'éducation nationale », grades
  00043 et 00042, comme l'art. 139. Le corps visé est au noyau : 00641 (et 00649,
  l'enseignement privé), grades 01451 et 01450, « Professeur des écoles du corps
  de l'Etat créé pour la Polynésie française hors classe ». Les grilles
  coïncident (00051 → 03312, 00050 → 03311), le corps et les grades sont faux.
- *La cause, commune aux deux.* Le corps se cherche parmi tous ceux que le
  noyau relie au texte du tableau, un décret qui modifie de nombreux statuts,
  et la phrase ne nomme le bon statut que par sa date, que le chaînage ne lit
  pas (`nomme` n'y est pas appelé ; seul un numéro restreint les corps). Le bon
  corps a des grades de libellé autre : le seul libellé qui se coupe est celui
  d'un autre corps. La règle sûre : quand la phrase nomme un statut, par son
  numéro ou par une date que les visas résolvent en un seul décret, ne chercher
  que les corps de ce statut ; sinon, déclarer.

### 1 c. Les écarts faibles de preuve, comptés sur tout le fichier

- *Un article cité qui ne vaut plus sur la période.* La preuve `article` cite
  les articles que le fichier des échelons nomme pour la grille, c'est-à-dire
  la version où l'indice apparaît, non celles qui valent sur la période (la
  règle écrite dit « à chacune de ses versions de la période »). Sur les 226
  liens `article`, 29 versions en vigueur sur la période ne sont pas citées, et
  12 lignes ne citent aucun article en vigueur sur leur période : (8),
  [2024-03-01, ∞), cite LEGIARTI000048278636, qui vaut du 2023-11-01 au
  2024-03-01 ; celle qui vaut, LEGIARTI000049196634, ôte au grade de greffier
  principal son échelon spécial, et redit le même « Greffier » ; (26),
  [2022-09-01, ∞), cite deux versions closes au 2022-09-01, non
  LEGIARTI000046248306 ; (7) ne cite pas LEGIARTI000051351757, en vigueur depuis
  le 2025-03-20. Les 29 versions non citées nomment toutes le statut, par son
  numéro ou par sa date : aucun rattachement n'est faux. Faible.
- *Deux grilles du même nom dans le même texte, départagées par les seuls
  échelons* : 19 rattachements (11 `article`, 8 `visa`). La preuve écrite ne dit
  pas pourquoi l'autre est écartée. Quatre vérifiés au texte, justes : (18), le
  II de l'art. 14 du n° 2015-1048 et l'art. 2 du n° 2021-1264 visent tous deux
  « les corps des masseurs-kinésithérapeutes et des orthophonistes » (neuf
  échelons ; l'art. 1, dix, pour les pédicures-podologues, ergothérapeutes,
  psychomotriciens, orthoptistes) ; aux n° 2016-202 et 2016-203, l'art. 2 est
  un « échelonnement indiciaire provisoire » pour l'intégration, au n° 2014-925
  celui « des échelons provisoires ». Faible.
- *Un jour.* Deux rattachements d'un jour, (2) et « Infirmier de classe
  supérieure » (n° 2012-762, grille 02948, le 2017-01-01), faits de versions de
  grade du noyau qui se touchent ; le second recouvre, ce même jour, le
  rattachement à la grille 03215 : deux grilles le même jour pour un grade, ce
  que la règle 5 exclut (le contrôle `_se_chevauchent` ne regarde que le
  LEGI). Faible.
- *Deux sources à la fois.* 63 paires de lignes rattachent le même grade, aux
  mêmes dates, à une grille du LEGI et à une grille du noyau : « une seule
  grille à la fois » vaut par source, non en tout. Ce n'est pas faux ; la note
  et l'en-tête de `durees.csv` ne le disent pas. Faible.
- *Une citation inexacte.* L'art. 116 du n° 2017-171 écrit « applicable au
  corps des ingénieurs de recherche régi par le décret du 31 décembre 1985
  susvisé » ; la note de B3 (« Ce qui prouve un rattachement ») et le
  commentaire du test du texte commun citent « le corps des ingénieurs de
  recherche régi par … », entre guillemets (le test de `nomme`, lui, cite
  juste). Faible. Les onze autres citations de la note de B3 rouvertes ici
  sont mot pour mot.

### 1 d. Le noyau : un défaut du script, et ce qu'il fausse — moyen

`Depot.__init__` construit `corps_citant` en parcourant
`{**self.noyau_corps, **self.noyau_grades}` : les deux dictionnaires sont
indexés par un code à cinq chiffres, et 654 des 971 codes de corps sont aussi
des codes de grade. Le grade écrase le corps : les textes que ces 654 corps
citent eux-mêmes sont perdus. 213 numéros de statut perdent un corps citant.
Effets, recomptés avec les corps et les grades réunis :

- *10 rattachements que la règle aurait refusés* : n° 2012-762, « Infirmier
  hors classe », « de classe supérieure », « de classe normale », du
  2012-06-01 au 2022-01-01, au corps 01102 (« Infirmiers des administrations de
  l'Etat ») ; le corps 01153 (« Infirmiers de la défense ») cite le même texte
  (1142, origine) et a les mêmes grades aux mêmes grilles. La grille est juste,
  le corps unique ne l'est pas.
- *20 raisons fausses* : « le Noyau RH ne cite le n° … pour aucun corps », pour
  les n° 2011-1317, 2012-1098, 2015-576 et 99-911, que des corps citent ; dans 6
  cas, un grade du même libellé existe à ces dates (n° 2011-1317, « Directeur
  de service », corps 01040 ; n° 2012-1098, assistants de service social, corps
  01114 ; n° 2015-576, ingénieurs des systèmes d'information et de
  communication, corps 01172) : rattachements peut-être manqués.
- *Une citation sans date.* Le lien `noyau` vaut pour toute la période dès
  qu'une version du corps ou d'un grade cite le statut. N° 83-1260,
  « Secrétaire d'administration de la recherche de classe exceptionnelle » et
  « … de classe normale », du 2002-02-03 au 2020-01-02, corps 00550 (INRA) : les
  seules versions de grade du corps qui citent le n° 83-1260 vont de 1984 à
  1995 (03762 à 03764) ; neuf corps d'établissements de recherche (00052,
  00085, 00356, 00399, 00414, 00430, 00433, 00499, 00550) ont ces deux grades,
  aux mêmes grilles 00665 et 01920, et citent tous le n° 95-83, qui modifie le
  n° 83-1260. Le corps unique tient à une citation de 1984 ; les grilles sont
  justes.
- *« Le corps cite » quand seul un grade cite* : 11 preuves (2 de durées, corps
  00550 et texte 1135 ; 9 de reclassements, corps 00021, 00490, 00493 et 01005,
  textes 5329 et 1578) disent « le corps … cite le texte … », que `corps.csv`
  dément : la citation est celle d'un grade. Moyen : la preuve écrite ne dit
  pas sa source.

## 2. Les déclarés, 22 tirés : 21 raisons vraies

Vrais, au texte ou au fichier qu'ils nomment : les versions de l'art. 7 du
n° 91-868 qui valent ensemble (LEGIARTI000033602862, du 2017-01-01 au
2017-09-23, et LEGIARTI000035742510, du 2017-01-01 au 2018-11-19) (2) ; le
n° 91-486 face au n° 2017-171, dont l'article ne nomme pas le statut, et au
noyau, dont les grades portent « du ministère chargé de la culture » ;
« Ingénieur d'études hors classe », neuf échelons, face à l'arrêté du
20 novembre 1991, quatre au fichier des grilles ; « Avant le 1er échelon de la classe supérieure »
(libellé d'en-tête) ; « Cadre de second niveau de La Poste » face à « Cadre de
second niveau » (n° 2016-227, LEGITEXT000032118258 : libellé autre, aucune
équivalence devinée) ; n° 92-453, l'en-tête « TABLEAU III GRADE » et des dates
qui ne se recouvrent pas ; n° 80-627, le noyau écrit « Professeur d'EPS classe
normale » ; « Chargé de recherche de 2e classe », grille de 2017 pour un
tableau clos en 2014 ; n° 92-364 et n° 96-1086, qu'aucun texte de grille ne
vise ; les deux « plusieurs grilles » (n° 2017-904, art. 1 et 2, deux
échelonnements datés, tous deux ouverts au LEGI ; arrêté du 17 janvier 1996,
art. 1 et l'art. 2 des « grades provisoires ») ; les trois groupes vides (le
grade est écrit avant l'en-tête : « du grade d'agent de maîtrise », « Le grade
d'aide technique principal comporte six échelons », « SITUATION DANS LE GRADE
de major pénitentiaire ») ; un reclassement hospitalier ; le n° 98-248, que le
noyau ne cite pas, ni le n° 92-551 que la phrase nomme par sa date ; « Ingénieur
principal », que le corps 00258 écrit « … de police technique et scientifique
de la police nationale » ; « A la date d'entrée en vigueur du présent
décret », sans date écrite ; « Infirmier hors classe », que deux corps
portent.

**Inexacte (faible).** N° 90-973, « Ingénieur » : « le texte
LEGITEXT000019669914 vise 2 décrets statutaires (2000-972, 90-973) ». L'arrêté
du 28 septembre 2000 ne vise qu'un statut : « Vu le décret n° 90-973 du
30 octobre 1990 portant statut particulier du corps des ingénieurs du génie
sanitaire, modifié par le décret n° 2000-972 du 28 septembre 2000 » ;
`_visas_statutaires` prend tous les numéros d'un visa, celui du décret qui l'a
modifié compris. Recompté sur les 40 raisons « texte commun » : 5 sont dans ce
cas (2 textes). Pour les ingénieurs du génie sanitaire, les échelons diffèrent
de toute façon ; pour le n° 97-364, « Contrôleurs du travail » de classe
exceptionnelle, supérieure et normale, du 2003-09-14 au 2013-10-01, les
échelons sont les mêmes : trois rattachements que la règle de B3 elle-même
aurait faits.

## 3. Le piège du n° 2017-171 et la date qui ouvre la phrase : conformes

N° 95-370, art. 25, LEGIARTI000034773631, en vigueur du 2017-09-01 au
2025-04-01 : « Ingénieur de recherche hors classe : Echelon spécial 4e échelon -
3e échelon 3 ans 2e échelon 3 ans 1er échelon 2 ans ». N° 2017-171
(LEGITEXT000034028389) : il vise le n° 95-370 (« fixant les dispositions
statutaires applicables aux ingénieurs et aux personnels techniques de
formation et de recherche du ministère de l'agriculture et de la pêche ») et
le n° 85-1534 ; son art. 116 (LEGIARTI000034028850, une version, du 2017-02-13
au 2018-01-01) fixe « Ingénieur de recherche hors classe 4 HEA HEA 3 1021 1027
2 906 912 1 807 813 » pour le corps du 31 décembre 1985 ; aucun article du
n° 2017-171 n'écrit « 95-370 » ni « 6 avril 1995 ». Le rattachement est refusé :
juste. Seul écart, la citation du point 1 c.

N° 2017-786, art. 81, LEGIARTI000034750747, en vigueur depuis le 2017-05-08 :
« Au 1er septembre 2017, les fonctionnaires appartenant au corps des
professeurs certifiés régi par le décret n° 72-581 du 4 juillet 1972 susvisé
[…] sont reclassés » ; le lecteur des reclassements n'y lit pas de date
(`effet` vide), le chaînage lit le 2017-09-01. Ce que B3 en dit est exact.

## 4. Les lignes changées hors du chaînage : documentation seule

`durees/tableaux.csv` : la seule ligne changée est l'en-tête en commentaire,
« le rattachement aux grilles choisit » devenu « ne choisit pas » ; aucune
ligne de donnée n'a bougé (`git diff --stat 6774a5f^ 6774a5f` sur `durees/`,
`reclassements/` et les dossiers de grilles : ce seul fichier, une ligne).
`dila_legi_durees.py` : la docstring et la constante `ENTETES` qui écrit cet
en-tête, rien d'autre. `dila_legi_reclassements.py` : la docstring. Les données
relues par R-B2-ter n'ont pas bougé. Une phrase est désormais fausse : la
docstring des reclassements dit que le chaînage les rattache « quand le texte
le prouve », ce que le point 1 b dément pour 5 groupes.

## 5. Les tests

`tests/test_chainage_grilles.py` : 11 tests, 11 passés. Les valeurs attendues
des tests 1 à 4 viennent des textes, rouverts ici : n° 2016-201, art. 24, et
n° 2016-203, art. 1 et visa (mot pour mot) ; n° 90-680, art. 24
(LEGIARTI000034948501, du 2021-01-01 au 2021-10-29, puis LEGIARTI000044268708
jusqu'au 2023-08-06), et le noyau : grade 04235 du corps 00021, grille 03313,
rangs 1 à 4 et 5 « exceptionnel » jusqu'au 2023-08-06, durées 24, 24, 30 et
0 ; le n° 2004-1439 (point 1 b) ; le n° 96-1113, art. 14. `paires == 6`
compte les trois paires dans les deux sens. Les tests lisent les fichiers
écrits, non le script relancé. Aucun ne vise un reclassement dont la phrase
nomme son statut par sa date dans un décret qui en modifie plusieurs, ni un
code de corps égal à un code de grade : les écarts des points 1 b et 1 d
passent la suite.

`python -m pytest -m rapide` : 4 328 passés, 8 sautés ;
`PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide` : 4 130 passés, 206
sautés ; aucun rouge. `python scripts/construire_donnees.py`, puis
`git status` : rien de changé, hors cette note ; le paquet ne bouge pas, comme
B3 le dit (ni le modèle ni son portage ne lisent `grilles/chainage/`).

## 6. Ce que le texte ne tranche pas, et `a_lire_au_jorf.csv`

Les déclarations disent ce que le texte ne rend pas certain (point 2).
Cinq cas de `a_lire_au_jorf.csv` rouverts. *Abîmés, vrais (3)* : n° 90-852,
art. 17, « GRADES ET ECHELONS : 6ème échelon. INDICES bruts : 638. », en
fiches ; n° 97-151, art. 21, « DURÉE MOYENNE : 3 ans DUREE MINIMALE : 2 ans
3 mois », en fiches ; n° 98-274, art. 20, « :----:----------: », dessiné en
caractères (le lecteur des durées le dit « en fiches » : son motif, non le
chaînage). *Manque, vrai (1)* : n° 72-503, aucun tableau au LEGI avant le
1992-07-01 ; de 1991 à 1992, l'art. 11 quater renvoie aux durées « fixées à
l'article 4 du décret du 20 septembre 1973 ». *Manque, faux (1), moyen* :
n° 87-1103, « son premier tableau de durées n'y vaut que depuis le
1995-08-01 » ; le LEGI porte l'art. 15, LEGIARTI000006370660, du 1987-12-31
au 1996-02-08 : « La durée maximale et la durée minimale du temps passé dans
chacun des échelons sont fixées ainsi qu'il suit : GRADES ET ÉCHELONS DUREE
Maximale Minimale 7e échelon 3 ans 6 mois 3 ans […] », que le lecteur des
durées n'a pas lu (`non_lus.csv` : « échelons dans le désordre »). Recompté :
87 des 127 cas `manque` ont, au LEGI, un article de durées antérieur au
premier tableau lu, que le lecteur a refusé ou qui écrit les durées en
phrases. Le cas `manque` ne compte que les tableaux lus ; sa phrase parle du
LEGI.

## Ce qui reste, pour le chaînage

Avant d'en rattacher plus : défaire les 5 reclassements faux et restreindre le
corps au statut que la phrase nomme, par son numéro ou par sa date (point 1 b) ;
réunir corps et grades sans écraser l'un par l'autre, puis refaire les 10
rattachements et les 20 raisons du point 1 d ; dater la citation du noyau ;
écrire « un grade du corps cite » quand c'est le cas ; ne compter, dans un
visa, que le décret visé ; citer dans la preuve `article` les versions qui
valent sur la période ; dire, dans `a_lire_au_jorf.csv`, si le LEGI porte un
article de durées non lu. Chaque correction, avec le test qui reproduit l'écart.
