# Relecture des corrections du chaînage aux grilles

File R-B3-bis, le 3 novembre 2026 : relecture indépendante des commits c4b22e5,
88fe35f, a70ee6e, b07772f, a879ca2, a5fd9e7 et 33b4ba7 de la session B3-bis
(note `2026-11-03-corrections-de-la-relecture-r-b3.md`), qui corrigent le
chaînage de B3 (6774a5f) d'après la relecture R-B3 (e62dfc9, note
`2026-11-03-relecture-chainage-aux-grilles.md`). Rien n'est repris de B3-bis ni
de mémoire : chaque article et chaque notice cités ici ont été rouverts dans la
table `doc` de l'index LEGI publié du dépôt (`dila_index.py legi --recuperer`,
dump du 13 juillet 2025, à jour de l'incrément 20261102-213929, celui de B3, de
R-B3 et de B3-bis), chaque ligne du Noyau RH dans `data/reference/grilles/etat/`.
Les contrôles sont des scripts écrits pour la relecture, hors du dépôt ; ils
n'empruntent au script du chaînage que `normaliser_noyau` (l'égalité des
libellés, règle de B3). L'état d'avant est celui des
fichiers de `chainage/` au commit 6774a5f, identiques à e62dfc9. Rien n'a été
modifié dans le dépôt, hors cette note.

**Verdict. Les corrections sont justes au fond, et chaque écart de R-B3 est
corrigé, par un test qui échoue sur l'arbre de B3 pour la raison de l'écart.**
Les 13 reclassements qui restent nomment le bon statut, le bon corps, la bonne
date, et leurs preuves citent mot pour mot. Les 21 lignes de durées ajoutées,
les 11 grades gagnés, les 12 lignes ôtées et les 11 grades perdus sont justes à
la source ; l'échantillon de 20 grades rattachés est conforme sans exception.
**Deux écarts moyens**, que ni B3-bis ni R-B3 n'ont vus, nés tous deux du
contrôle des échelons, qui compare des nombres de rangs, et sur toute la
période à la fois. Dans le reclassement des majors de police (n° 2004-1439,
art. 23-1), la ligne « Echelon exceptionnel → Echelon exceptionnel » porte le
rang 4, qui est, dans la grille d'accueil, le 4e échelon (indice brut 620), non
l'échelon exceptionnel (631). Aux durées, 8 des 582 lignes rattachées, toutes
de B3, le sont sur des jours où la grille du dépôt n'a pas les échelons du
tableau, ou n'en a aucun : les greffiers (2017-2023), les lieutenants-colonels
et commandants de sapeurs-pompiers (2017-2020), d'autres (partie 2).
**Quatre écarts faibles** : une raison qui dit le n° 60-403 inconnu du Noyau
RH, qui le porte ; le compte « N article(s) » des cas `non_lu`, qui compte des
paires article-motif ; deux citations de la note de B3-bis qui ne sont pas mot
pour mot ; les infirmiers du n° 2012-762, dont la déclaration est vraie mais
perd un rattachement que l'art. 1 du décret rend certain.

## L'échantillon, pour le refaire

Graine 158113 (Python, `random.Random(158113)`). *Grades* : les 498 grades
(`texte`, `article`, `tableau`, `groupe`) des lignes `rattache` de
`chainage/durees.csv`, triés ; `sorted(rng.sample(range(498), 20))` : indices
60, 66, 119, 187, 194, 262, 272, 301, 324, 325, 336, 345, 356, 372, 382, 392,
433, 449, 465, 477, soit 23 lignes. *Non lus* : les 87 lignes `non_lu` de
`a_lire_au_jorf.csv` dans l'ordre du fichier, un générateur neuf à la même
graine, `sorted(rng.sample(range(87), 10))` : 15, 16, 29, 46, 48, 65, 68, 75,
81, 84. Les comptes de B3-bis se refont à l'identique : 573 lignes de durées
rattachées avant, 582 après, 12 ôtées, 21 ajoutées ; 498 grades rattachés sur
1 675 avant comme après, 11 perdus, 11 gagnés ; 862 groupes de reclassement,
13 rattachés, 849 déclarés, et leurs raisons (56 « le libellé ne se coupe
pas », 32 « la phrase ne nomme pas le statut du corps reclassé », 11 « le Noyau
RH ne cite, la veille ni le jour », 5 « par sa date », 1 « renvoie », 398, 134,
124, 86, 1 et 1 inchangées) ; 137 cas `abime`, 87 `non_lu`, 40 `manque`, les
127 de l'ancien `manque` et eux seuls.

## 1. Les 13 reclassements qui restent : justes, sauf un échelon

Pour chacun : l'article rouvert, la phrase et sa date, le statut qu'elle nomme,
la notice et les visas, le corps qui cite ce statut, le grade et la grille la
veille et le jour (`grades.csv`), les échelons de ces grilles
(`etat/echelons.csv`), les lignes du tableau (`reclassements/lignes.csv`).

- *N° 2004-1439, art. 23-1* (LEGIARTI000023734900, du 2011-07-01 au
  2018-01-01) : « Au 1er juillet 2011, les membres du corps d'encadrement et
  d'application de la police nationale sont reclassés conformément au tableau
  de correspondance suivant ». Le texte est le statut (LEGITEXT000005971737,
  « Décret n°2004-1439 du 23 décembre 2004 portant statut particulier du corps
  d'encadrement et d'application de la police nationale. »). Deux corps citent
  le texte 296 : 00172 (« Corps d'encadrement et d'application de la police
  nationale », depuis le 2005-01-01) et 00867 (« … de police de la Polynésie
  française ») ; les grades du second s'écrivent « Major de police de la
  Polynésie française » : un seul corps porte les libellés du tableau. Majors
  02774, brigadiers-chefs 02779, gardiens de la paix 02780, grilles 00420,
  00423, 00422 le 2011-06-30, 02777, 02782, 02783 le 2011-07-01. Corps, grades,
  grilles et date conformes (3) ; un échelon faux, ci-dessous.
- *N° 2017-1031, art. 39* (LEGIARTI000034743634) : « régi par le décret
  n° 90-90 du 24 janvier 1990 susvisé » ; seul le corps 00003 cite le texte 71
  (n° 90-90). Conformes (2).
- *N° 2017-786, art. 139, 157, 36 et 123* (LEGIARTI000034750757, 034750857,
  034750953, 034751013) : la phrase nomme le statut par sa date ; les visas de
  LEGITEXT000034750633 portent un seul décret à chacune (« n° 90-680 du 1er août
  1990 », « n° 92-1189 du 6 novembre 1992 », « n° 70-738 du 12 août 1970 »,
  « n° 86-492 du 14 mars 1986 »), que le LEGI identifie (LEGITEXT000006076298,
  006080320, 006061762 et 006061763, 006065551). Les corps 00021, 00250, 00493,
  00490 citent les textes 160, 159, 162, 168. Deux autres corps citent les
  textes 160 et 159, 00616 et 00652, ceux de l'enseignement privé, dont les
  grades s'écrivent « Professeur des écoles enseignement privé hors classe »,
  « Professeur de lycée professionnel enseignement privé hors classe » : un
  seul corps porte le libellé. Conformes (6).
- *N° 2019-50, art. 24 et 37* (LEGIARTI000038076578, 038076610) : art. 24,
  « régis par le décret n° 2010-1639 du 23 décembre 2010 » (corps 01140, texte
  1310, du 2011-01-01 au 2019-01-31, suivi du 01230) puis « le corps régi par le
  présent décret » (01230, texte 6110, depuis le 2019-02-01) ; art. 37, le texte
  est le statut. Le tableau de l'art. 37 (« 9e échelon 14e échelon […] 1er
  échelon 6e échelon ») tombe sur la grille 03689, élève puis quatorze
  échelons, que le n° 2010-1641, art. 3 (LEGIARTI000042508218, depuis le
  2021-01-01), écrit « 14e échelon 776 […] 6e échelon 587 […] 1er échelon 449
  Elève 361 ». Conformes (2).

Les preuves de ces 13 lignes : chaque passage entre guillemets se retrouve mot
pour mot dans la notice, l'article ou le titre du Noyau RH qu'elles nomment.
Les cinq groupes défaits sont déclarés, à raison (« le libellé ne se coupe pas
en deux grades des corps 00395 », n° 67-91 ; « … 00641, 00649 », n° 2003-1260) :
les grades de ces corps s'écrivent « Géomètre principal de l'institut national
de l'information géographique et forestière », « Professeur des écoles du corps
de l'Etat créé pour la Polynésie française hors classe ».

**Moyen — l'échelon exceptionnel des majors de police.** Le n° 2010-564,
art. 5, en vigueur du 2011-07-01 au 2012-01-01 (LEGIARTI000023750120), fixe
pour le grade d'accueil : « Major de police Echelon exceptionnel (1) 4e échelon
3e échelon 2e échelon 1er échelon 631 620 616 598 581 ». Le Noyau RH le dit
de même : grille 02777 le 2011-07-01, 581, 598, 616, 620, puis 631 de nature
« exceptionnel ». Le tableau de l'art. 23-1 écrit « Echelon exceptionnel
Echelon exceptionnel Ancienneté acquise 3e échelon 3e échelon […] » : la
colonne d'accueil ne montre pas de 4e échelon. Le lecteur des reclassements
range l'exceptionnel au-dessus du plus haut échelon écrit de son côté
(`_rangs`, `dila_legi_reclassements.py`) : rang 4 à l'origine, juste (la grille
00420 a trois échelons et l'exceptionnel, 630), rang 4 à l'accueil, faux (le
rang 4 de la grille 02777 est le 4e échelon, 620 ; l'exceptionnel est le 5e).
Le chaînage vérifie seulement que les rangs du tableau sont parmi `1..n`, n le
nombre d'échelons de la grille (`rangs_noyau_au`) : 4 parmi 1 à 5, la ligne
passe, et B3-bis la dit conforme. Le rattachement du groupe (corps, grades,
grilles) est juste ; une ligne, si on la lisait, placerait l'agent à l'indice
620 au lieu de 631. Rien ne la lit encore : ni `src/`, ni `moteur/`, ni
`construire_donnees.py` n'ouvrent `reclassements/` ni `chainage/`. Les autres
rangs des 13 groupes sont justes, rouverts aux tableaux (les gardiens de la
paix : « Echelon exceptionnel 12e échelon », rang 12, le 12e des treize
échelons de la grille 02783 hors provisoire, élève et stagiaire).

## 2. Ce qui s'ajoute : les 21 lignes, les 11 grades, les dates

*Les 21 lignes ajoutées, toutes rouvertes.* Pour chacune : la version du
tableau (`durees/tableaux.csv`, ses versions), la période, les rangs du tableau
et de la grille à chaque date où la grille change, puis, au noyau, les versions
du corps et de ses grades qui citent le statut et leur union sur la période,
les corps qui le citent et ceux d'entre eux qui ont un grade du même libellé ;
au LEGI, les visas du texte de grille et les articles de la grille.

- *Noyau (13).* N° 96-158 (corps 01282, depuis le 2022-01-01, 8 et 11
  échelons) ; n° 97-364 (corps 00195, texte 141, grilles 00479, cinq échelons
  après deux provisoires, 00480, six, 00481, douze) ; n° 84-238 (corps 00409,
  « Ingénieurs des systèmes d'information et de communication du ministère de
  l'intérieur », texte 387, jusqu'au 2015-05-31 ; 10 et 12 échelons) ;
  n° 2011-1317 (corps 01040, grade 03408, 14 échelons) ; n° 2012-1098 (corps
  01114 ; 11 et 13) ; n° 2015-576 (corps 01172 ; 03106, sept échelons et
  l'exceptionnel, comme le tableau, sept et le spécial ; 10 ; 12). Chaque fois
  un seul corps qui cite le statut a le grade, les citations couvrent toute la
  période, les échelons sont ceux du tableau à chaque date. Une précision :
  pour les contrôleurs du travail, le tableau écrit « Contrôleurs du travail de
  classe exceptionnelle » et le noyau « Contrôleur du travail de classe
  exceptionnelle » ; « le libellé est le même » s'entend après la mise au
  singulier de `normaliser`.
- *Visa (8).* Arrêté du 11 septembre 2003 (LEGITEXT000019591150), arrêté du
  29 septembre 2000 (LEGITEXT000019668607), arrêté du 2 mai 2007
  (LEGITEXT000019420380) : leurs visas mot pour mot comme la preuve les cite ;
  les autres numéros visés sont le n° 48-1108 (rémunération) et les décrets qui
  ont modifié le statut (n° 2003-870 ; n° 2000-956 ; n° 99-142 et n° 2007-671).
  Articles LEGIARTI000019591152, 019668611, 019420383 : 5, 6 et 12 ; 3 et 9 ;
  6, 11 et 11 échelons, comme les tableaux. Conformes.
- *Les deux raisons du n° 90-973* : « les échelons diffèrent : le tableau a les
  rangs [1 … 9], la grille ingenieur […] [1 … 10] », et [1 … 4] contre
  [1 … 5]. Vrai au texte : LEGIARTI000006459943 écrit « Ingénieur 9e échelon
  3 ans 2 ans 6 mois […] », LEGIARTI000019669918 « Ingénieur 10e échelon 901 ».

*Les cas « date résolue par les visas ».* Aux reclassements, les quatre
rattachés du n° 2017-786 (partie 1) ; les cinq déclarés « par sa date » : deux
au n° 2017-1031 (LEGIARTI000034743616, « régis par le décret du 24 janvier
1990 » ; les visas portent le n° 90-89 et le n° 90-90 à cette date : vrai) et
trois au n° 2017-786, art. 12 (LEGIARTI000034750817), écart faible ci-dessous ;
les géomètres de l'IGN et les professeurs des écoles de Polynésie, résolus et
identifiés, puis déclarés pour le libellé (partie 1). Aux durées, les 226 liens
`article` : 123 nomment le statut par sa date, 103 par son numéro ; pour tous,
chaque version de l'article (même titre, même numéro) en vigueur sur la
période est citée, aucune autre, et chacune nomme le statut ; pour les 123, les
visas du texte de grille ne portent qu'un décret à cette date, et le visa cité
s'y lit mot pour mot. Conformes.

*L'échantillon de 20 grades (23 lignes).* Noyau : n° 2003-770, « Directeur
adjoint du travail » (corps 00234) ; n° 70-738, CPE hors classe (00493) ;
n° 90-90, classe exceptionnelle (00003) ; n° 2010-986, inspecteur principal et
administrateur adjoint (01012 ; le corps 00162 cite aussi le texte 737, sans ce
libellé) ; n° 2012-1098 ; n° 2013-974 (01193) ; n° 2014-847 (01192 ; 00702
cite aussi, sans ce libellé) ; n° 2021-1869 (01278). LEGI, `article` : n° 70-738
→ n° 2017-789 ; n° 91-868 → arrêté du 16 novembre 2018 ; n° 92-1432 →
n° 2017-171 ; n° 2008-952 → n° 2011-388 ; n° 2010-986 → n° 2017-1392 (deux) ;
n° 2014-923 → n° 2014-925. LEGI, `visa` : n° 2002-811 → n° 2017-1359 (l'autre
visa, n° 2013-1135, est un statut d'emploi, R-B3 l'a lu) ; n° 92-859 →
n° 92-860 (le n° 90-830 « fixant divers échelonnements indiciaires ») ;
n° 2012-1420 → n° 2012-1421 ; n° 2013-489 → n° 2013-492 ; n° 2016-201 →
n° 2016-203 (le n° 2004-809 est une loi) ; n° 2016-1177 → n° 2016-1180 ;
n° 2017-984 → arrêté du 10 mai 2017 (le n° 2017-988, « relatif au classement
indiciaire »). Statut, corps, libellé, période et échelons conformes, 23 sur 23.

**Moyen — les échelons comparés sur toute la période à la fois.** Au-delà de
l'échantillon, les 582 lignes rattachées ont été reprises date par date : à
chaque jour où la grille change, ses rangs (au LEGI, ceux de son fichier
d'échelons ; au noyau, leur nombre, élève, stagiaire et provisoires mis à part)
face à ceux du tableau. Le script réunit les échelons de toute la période
(`rangs_legi`, `rangs_noyau` : `intersection(debut, fin, …)`) ; 8 lignes, 8
grades, toutes déjà dans le fichier de B3 et inchangées depuis, ont des jours
où la grille n'a pas les rangs du tableau :

- *Greffier, Greffier principal* (n° 2015-1275 → LEGITEXT000031320442,
  [2017-01-01, 2024-03-01)) : du 2017-01-01 au 2023-10-31, les grilles
  `greffier` et `greffier-principal` n'ont aucun échelon ; les versions de
  l'art. 3 de ces années, LEGIARTI000035603091 et LEGIARTI000036489952, que la
  preuve cite, sont au fichier des non lus du lecteur des grilles
  (`etat_legi/non_lus.csv` : « valeurs hors des lignes, dans « Greffier
  principal Echelon spécial - 705 713 723 11 ème échelon - 701 707 707 » »).
- *Lieutenant-colonel, Commandant* (n° 2016-2008 → LEGITEXT000033792720,
  [2017-01-01, 2025-06-14)) : la grille a 7 et 8 échelons jusqu'au 2020-12-31,
  le tableau 8 et 9. Le tableau (art. 12, LEGIARTI000033792383) s'ouvre sur
  « A compter du 1er janvier 2020 : 1° Le grade de capitaine comprend dix
  échelons. 2° Le grade de commandant comprend neuf échelons » ; le lecteur des
  durées le date du 2017-01-01, l'entrée en vigueur de l'article. La grille du
  dépôt (n° 2016-2007, art. 3) ne donne un 8e échelon aux lieutenants-colonels
  qu'au 2021-01-01 (LEGIARTI000036490570 : « 8 1015 », une seule valeur sous
  quatre colonnes datées de 2017 à 2021).
- *Ingénieur des études et de l'exploitation de l'aviation civile de classe
  normale* (n° 71-917 → LEGITEXT000021214923, [2017-01-01, 2025-07-01)) : du
  2018-01-01 au 2025-06-30, la grille a les rangs 2 à 11, le tableau 1 à 11 ;
  LEGIARTI000037196211 écrit « … de classe normale 11e 774 780 780 […] 2e 483
  490 500 Ingénieur stagiaire des études et de l'exploitation de l'aviation
  civile 1er 434 441 444 ».
- *Techniciens supérieurs des études et de l'exploitation de l'aviation civile,
  classe principale et classe normale* (n° 93-622, noyau, grilles 00226 et
  00227, [2007-01-01, 2013-11-15)) : le Noyau RH ne donne aucun échelon à ces
  grilles avant le 2009-10-27.
- *Puéricultrice de classe normale* (n° 2014-923 → LEGITEXT000029383554,
  [2017-01-01, 2022-01-01)) : la grille n'a aucun échelon du 2017-01-01 au
  2017-05-10 (ses articles valent jusqu'au 2015-12-31, puis depuis le
  2017-05-11).

Le grade et la grille de ces lignes sont les bons ; l'égalité des échelons, qui
fonde le rattachement, ne tient pas ces jours-là, ou ne se vérifie pas. Pour
les greffiers et les sapeurs-pompiers, la cause est en amont (une version de la
grille non lue, une date d'effet non lue) ; le chaînage rattache sans le voir.
Aucun test ne regarde la grille date par date.

**Faible — le n° 60-403, que le Noyau RH porte.** Les trois groupes des
chargés d'enseignement d'éducation physique et sportive (n° 2017-786,
LEGIARTI000034750817 : « régi par le décret du 22 avril 1960 susvisé ») sont
déclarés : « que le visa résout en n° 60-403, décret que ni le LEGI ni le Noyau
RH n'identifient ». Le visa : « Vu le décret n° 60-403 du 22 avril 1960 modifié
relatif aux dispositions statutaires applicables aux chargés d'enseignement de
l'éducation physique et sportive » ; aucune notice du LEGI, vrai. Mais le Noyau
RH porte le texte 166, « Décret n° 60-403 du 22 avril 1960 relatif aux
dispositions statutaires applicables aux chargés d'enseignement de l'éducation
physique et sportive. », JORFTEXT000000501563, sans NOR : la règle n'identifie
au noyau que par le NOR. Aucun rattachement n'est perdu : le corps 00448, qui
cite ce texte, écrit ses grades « Chargé d'enseignement de l'éducation physique
et sportive hors classe », que le libellé du tableau (« Chargé d'enseignement
d'éducation physique et sportive hors classe ») ne coupe pas. La raison dit
faux du noyau.

## 3. Ce qui se retire : vrai, une perte

- *Les secrétaires d'administration de la recherche (n° 83-1260, 2 lignes).* Le
  corps 00550 cite le texte 1216 (n° 84-1207) ; ses grades 01272 et 01274, du
  2002-02-03 au 2020-01-01, citent le texte 1212 (n° 95-83, « modifiant le
  décret n° 83-1260 ») ; seuls 03762 à 03764, du 1984-01-01 au 1995-07-31,
  citent le texte 1135. Neuf corps (00052, 00085, 00356, 00399, 00414, 00430,
  00433, 00499, 00550) portent ces deux libellés aux grilles 00665 et 01920.
  Raison vraie ; aucun rattachement certain perdu.
- *Les infirmiers (n° 2012-762, 9 grades, 10 lignes).* `corps.csv` : 01102 et
  01153, « 1142:origine », depuis le 2012-06-01 ; leurs grades ont les mêmes
  libellés et les mêmes grilles (02947 à 02949 puis 03214 à 03216). La raison,
  « plusieurs corps du Noyau RH ont ce grade aux mêmes dates : 01102, 01153 »,
  est vraie.

**Faible — une perte que le texte ne justifie pas.** L'art. 1 du n° 2012-762
(LEGIARTI000025855207) : « Sont classés dans la catégorie A […] et sont régis
par le présent décret les corps ci-dessous énumérés : 1° Le corps des
infirmiers de l'Etat […] ; 2° Le corps des infirmiers de la défense ; 3° Le
corps des infirmiers de l'éducation nationale et de l'enseignement supérieur. »
Le tableau de durées du décret vaut pour chacun ; les deux corps du noyau ont
la même grille à chaque date : la grille de chaque grade est certaine, pour
l'un et l'autre corps. La règle « un seul corps » déclare au lieu d'écrire une
ligne par corps. Ce n'est pas faux, c'est moins que ce que le texte prouve.

*Les 87 cas `non_lu`.* Pour les 87 : chaque article nommé est au LEGI, et
commence avant le premier tableau lu. Les 10 tirés, rouverts : n° 58-778,
65-306, 86-492, 96-1113, 97-511, 2016-200, 87-1103, 91-847, 92-857, 92-871.
Chaque article est un article de durées, aux dates dites, et son motif se voit
au texte : « :----------------------------: : Grade et échelons » (n° 91-847,
art. 16), « :-----------------------------: : GRADES » (n° 92-857, art. 15) ; « I = ÉCHELON II = DUREE MOYENNE » (n° 97-511, art. 17) ; « sont
celles fixées à l'article 2 du décret du 27 janvier 1970 susvisé » (n° 65-306,
art. 2) ; « ECHELONS : Du 1er au 2e échelon DUREE D'ECHELON : 3 ans » (n° 86-492,
art. 19-2) ; « Echelon d'élève - échelon unique 1 an » (n° 2016-200, art. 18).
Raisons vraies ; aucun rattachement en jeu.

**Faible — « N article(s) ».** La phrase « le LEGI porte N article(s) de durées
que le lecteur n'a pas lus » compte les paires distinctes (article, motif) de
`durees/non_lus.csv` (`dila_legi_chainage.py`, `vus`), non les articles : dans 7
des 87 cas, N n'est pas le nombre d'articles de la colonne `articles`, qui est
juste. N° 58-778 : 6 pour 5 articles ; n° 86-492 : 4 pour 1 (l'art. 19-2, quatre
tableaux) ; n° 96-1113 : 5 pour 2 ; n° 84-135 : 13 pour 5.

## 4. Les écarts de R-B3, un à un

Chaque test nouveau de B3-bis (14) a été lancé, dans un arbre de travail
détaché au commit e62dfc9 (les fichiers et le script de B3), avec le fichier de
tests d'aujourd'hui : 14 rouges, 11 verts (les anciens). La raison de chaque
rouge :

- *Grave, les cinq reclassements faux.* Corrigés (partie 1). Rouges :
  `test_les_geometres_de_l_ign_ne_se_rattachent_pas_aux_geometres_cadastreurs`
  et `…_de_polynesie_…` (« 'rattache' == 'declare' »),
  `test_le_statut_nomme_par_sa_date_est_identifie_dans_la_preuve` (la preuve
  citait le texte 5329, n° 2017-786, non « décret du 1er août 1990 »),
  `test_une_phrase_qui_ne_nomme_pas_le_statut_d_un_decret_modificatif_est_declaree`
  (n° 95-108). `test_les_visas_resolvent_la_date_d_un_statut_en_son_numero`
  échoue faute de la fonction (`decrets_de_la_date`) : c'est le test d'une
  fonction neuve, l'écart est reproduit par les quatre autres.
- *Moyen, les corps écrasés par les grades.* Corrigé : les 20 raisons (6
  rattachements, 14 raisons refaites), les 10 lignes des infirmiers (partie 3).
  Rouges : `test_le_noyau_cite_un_statut_par_ses_corps_comme_par_ses_grades`
  (« ('99-911', ['le corps 00454']) »),
  `test_deux_corps_qui_citent_le_statut_et_ont_les_memes_grades_ne_se_rattachent_pas`
  (les lignes du n° 2012-762).
- *Moyen, la citation sans date et « le corps cite ».* Corrigé : chacune des
  154 lignes du lien `noyau` repose sur des versions du corps qui citent le
  statut et, réunies, couvrent toute la période (recompté sur les 154).
  Rouges : `test_la_preuve_du_noyau_dit_qui_cite_le_statut_et_vaut_sur_toute_la_periode`
  (corps 00550, texte 1135),
  `test_la_preuve_d_un_reclassement_dit_qui_cite_le_statut_a_sa_date` (corps
  01005, texte 1578 : la garde, verte quand B3-bis l'écrit, est rouge sur
  l'arbre de B3).
- *Moyen, les 87 cas `manque`.* Corrigé (partie 3). Rouge :
  `test_un_article_de_durees_que_le_lecteur_n_a_pas_lu_ne_se_dit_pas_absent_du_legi`
  (« 'manque' == 'non_lu' »).
- *Faible, les versions de la période.* Corrigé (partie 2 : 226 liens). Rouge :
  `test_la_preuve_article_cite_les_versions_en_vigueur_sur_la_periode`
  (LEGIARTI000049196634 absent de la preuve des greffiers).
- *Faible, deux grilles du même nom.* Corrigé : 19 preuves nomment l'autre
  grille et la raison, 11 par les échelons, 8 par l'article ; recomptées. Rouge :
  `test_la_preuve_dit_pourquoi_la_grille_du_meme_nom_est_ecartee`
  (n° 2021-1264).
- *Faible, un jour et deux grilles.* Corrigé : aucun grade n'a deux grilles
  d'une même source à la fois ; reste la ligne d'un jour du n° 90-90 (grille
  03351, le 2017-09-01), juste. Rouge :
  `test_un_grade_n_a_qu_une_grille_a_la_fois_par_source` (infirmier de classe
  supérieure, 02948 et 03215 le 2017-01-01).
- *Faible, deux sources à la fois.* Corrigé par la documentation : l'en-tête de
  `durees.csv` écrit « Une seule grille à la fois par source : un grade peut
  avoir, aux mêmes dates, une grille du LEGI et une du noyau. » ; 70 paires qui
  se chevauchent (63 avant, le compte de R-B3), dont 61 aux mêmes bornes.
- *Faible, la citation de l'art. 116 du n° 2017-171.* Corrigée : le
  commentaire du test du texte commun cite « L'échelonnement indiciaire
  applicable au corps des ingénieurs de recherche régi par le décret du
  31 décembre 1985 susvisé est fixé ainsi qu'il suit », mot pour mot
  (LEGIARTI000034028850) ; un renvoi daté est au bout de la note de B3.
- *Faible, le décret qui a modifié le statut visé (R-B3, partie 2).* Corrigé
  (partie 2). Rouge : `test_le_decret_qui_a_modifie_le_statut_n_est_pas_un_second_statut`
  (« {'2000-972', '90-973'} == {'90-973'} »).
- *La docstring des reclassements* (R-B3, partie 4), « quand le texte le
  prouve » : redevenue vraie, les cinq groupes défaits.

**Faible — deux citations de la note de B3-bis.** « au LEGI
LEGITEXT000006061489 et LEGITEXT000024751171 (« Décret n° 67-91 du 20 janvier
1967 relatif au statut particulier des géomètres de l'Institut national de
l'information géographique et forestière ») » : la première notice s'intitule
« Décret n°67-91 du 20 janvier 1967 relatif au statut particulier des géomètres
de l'institut géographique national *IGN* », la seconde « … des géomètres de
l' Institut national … ». Corps 00409, cité « Ingénieurs des systèmes
d'information et de communication du ministère », sans la fin, « de
l'intérieur », ni la marque d'une coupe. Les autres citations de la note,
rouvertes, sont exactes ; celles des fichiers (preuves des 13 reclassements,
visas des 226 liens `article`), mot pour mot.

## 5. Les tests et le paquet

`tests/test_chainage_grilles.py` : 25 passés. `python -m pytest -m rapide` :
4 342 passés, 8 sautés, 13 rouges ; `PRESOMPTIONS_DECALEES=1 python -m pytest
-m rapide` : 4 143 passés, 207 sautés, les mêmes 13 rouges ; tous de
`test_pages_en_dossier.py`, les pages toutes faites que GitHub refait quand
`main` bouge. `python scripts/construire_donnees.py`, puis `git status` : rien
de changé hors cette note ; le paquet ne bouge pas.

## Ce que la relecture laisse

- Comparer, au chaînage des reclassements, la nature des échelons (spécial,
  exceptionnel) à celle de la grille, et non leur seul nombre ; refaire le rang
  de la ligne des majors de police, avec son test (n° 2010-564, art. 5).
- Comparer les échelons de la grille à ceux du tableau à chaque date où l'un
  ou l'autre change, et couper ou déclarer la période où ils diffèrent (les 8
  lignes de la partie 2) ; un test qui le garde.
- Identifier au Noyau RH un décret par son numéro et sa date, quand il n'a pas
  de NOR (n° 60-403), ou corriger la raison.
- Les décrets communs à plusieurs corps qu'ils énumèrent (n° 2012-762, art. 1) :
  une ligne par corps, quand les grilles coïncident.
- Pour rattacher plus, sans deviner : 68 raisons « les échelons diffèrent »
  (52 grades) opposent un tableau de n rangs, dont le dernier porte une durée, à
  une grille de n + 1 échelons, le sommet que le tableau n'écrit pas (n° 90-973,
  « Ingénieur 9e échelon 3 ans » ; la grille, « 10e échelon 901 ») : une règle à
  écrire et à tester, non un rattachement à faire de mémoire.
