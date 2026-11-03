# Corrections de la relecture R-B3 du chaînage aux grilles (file B3-bis)

**Le 3 novembre 2026 : les cinq reclassements rattachés au mauvais corps ne le
sont plus, et la règle qui les avait faits est corrigée ; le Noyau RH se lit par
ses corps et par ses grades, chaque citation datée ; les écarts faibles de
preuve sont repris. Reclassements : 13 groupes rattachés sur 862, au lieu de
18, chacun relu à la source. Durées : 498 grades de tableaux rattachés, comme
avant, mais 11 perdus et 11 gagnés, chacun relu à la source.**

Demande : la session d'orchestration de la vague 6, file B3-bis, le 3 novembre
2026 : corriger, dans l'ordre et chaque fois par le test qui reproduit l'écart,
ce que la relecture R-B3 (`2026-11-03-relecture-chainage-aux-grilles.md`,
commit e62dfc9) relève dans le chaînage de B3 (commit 6774a5f) ; ne rien
rattacher de plus que ce que la correction rend certain ; revérifier à la
source chaque reclassement qui reste et chaque durée que la correction du noyau
touche. Exigence du propriétaire, le même jour : aucune erreur, tout prouvé par
écrit, jamais de mémoire.

- *La source.* L'index LEGI publié (`dila_index.py legi --recuperer`, dump du
  13 juillet 2025, à jour de l'incrément 20261102-213929, celui de B3 et de
  R-B3), récupéré sans reconstruction : les notices LEGITEXT (titres et visas)
  et le texte de chaque article cité ci-dessous, rouverts dans la table `doc`.
  Le Noyau RH du CISIRH (juillet 2026), au dépôt (`grilles/etat/`). Le JORF n'a
  pas été ouvert.
- *Le script* : `scripts/fetch/dila_legi_chainage.py`, relancé ; ses trois
  fichiers sous `data/reference/grilles/chainage/` sont refaits. Ni le modèle,
  ni son portage, ni le paquet ne les lisent.
- *Les tests* : `tests/test_chainage_grilles.py`, de 11 à 25 ; chacun des
  nouveaux vu rouge pour la raison attendue, puis vert (sauf les deux gardes
  dites plus bas).

## 1. Grave : le corps d'un reclassement est celui du statut que la phrase nomme

*L'écart.* Le corps se cherchait parmi tous ceux que le noyau relie au texte
du tableau. Le décret n° 2016-581 « modifiant divers décrets relatifs à
l'organisation des carrières des fonctionnaires de catégorie B » est cité au
noyau par les grades de 47 corps ; le seul libellé qui s'y coupait était celui des
géomètres-cadastreurs (corps 01005), alors que l'art. 12
(LEGIARTI000032523172) écrit : « I. - Au 1er janvier 2016, les fonctionnaires
appartenant au corps des géomètres de l'Institut national de l'information
géographique et forestière régi par le décret du 20 janvier 1967 susvisé dans
sa rédaction antérieure au présent décret sont reclassés dans ce même corps ».
Le décret n° 2017-786, art. 164 (LEGIARTI000034750879) : « Au 1er septembre
2017, les fonctionnaires appartenant au corps des professeurs des écoles régi
par le décret du 23 décembre 2003 susvisé […] », rattaché au corps 00021 de
métropole.

*La règle, désormais* (`statuts_de_la_phrase`). Le corps se cherche parmi ceux
qui citent, la veille ou le jour du reclassement, le statut que la phrase
nomme : par son numéro (« régi par le décret n° 90-90 ») ; par sa date
(« régi par le décret du 20 janvier 1967 »), seulement si les visas du texte
portent un seul décret à cette date (`decrets_de_la_date` : le numéro qui
précède « du <date> », non celui du décret qui a modifié le statut) et si ce
décret est identifié, au LEGI par une notice dont le titre est « Décret n° <n>
du <date> » ou au Noyau RH par son NOR ; ou par « le présent décret » (« régi
par », « créé par »), quand le texte est lui-même un statut. Une phrase qui ne
nomme aucun statut vaut pour le texte s'il est lui-même un statut (titre
statutaire, sans « modifiant ») ; sinon, déclaré. « Décrets du … » au pluriel
et « le même décret » sont déclarés.

*Les deux cas, à la source.* Les visas du n° 2016-581 (LEGITEXT000032523056) :
« Vu le décret n° 67-91 du 20 janvier 1967 modifié relatif au statut
particulier des géomètres de l'Institut national de l'information géographique
et forestière » et « Vu le décret n° 2010-983 du 26 août 2010 portant statut
particulier du corps des géomètres-cadastreurs des finances publiques » : la
date résout le n° 67-91, au LEGI LEGITEXT000006061489 et LEGITEXT000024751171
(« Décret n° 67-91 du 20 janvier 1967 relatif au statut particulier des
géomètres de l'Institut national de l'information géographique et
forestière ») ; au noyau, le texte 944, cité par les grades du corps 00395
(« Géomètre de l'institut national de l'information géographique et
forestière », « Géomètre principal de l'institut… », « Technicien géomètre de
l'institut… ») et par le corps 01329 (depuis le 2024-05-25). Le libellé du
tableau, « Géomètre principal Géomètre principal », ne se coupe pas en ces
grades : les trois groupes sont déclarés. Le visa du n° 2017-786
(LEGITEXT000034750633) : « Vu le décret n° 2003-1260 du 23 décembre 2003
modifié fixant les dispositions statutaires applicables aux professeurs des
écoles du corps de l'Etat créé pour la Polynésie française » ; LEGITEXT000005739967 ;
au noyau, le texte 180, cité par les corps 00641 et 00649, dont les grades
s'écrivent « Professeur des écoles du corps de l'Etat créé pour la Polynésie
française hors classe » : les deux groupes sont déclarés.

*Tests* : `test_les_visas_resolvent_la_date_d_un_statut_en_son_numero`,
`test_les_geometres_de_l_ign_ne_se_rattachent_pas_aux_geometres_cadastreurs`,
`test_les_professeurs_des_ecoles_de_polynesie_ne_se_rattachent_pas_a_la_metropole`,
`test_le_statut_nomme_par_sa_date_est_identifie_dans_la_preuve`,
`test_une_phrase_qui_ne_nomme_pas_le_statut_d_un_decret_modificatif_est_declaree`
(n° 95-108, LEGIARTI000006476949 : « A compter du 1er août 1993, les
inspecteurs de 1re et de 2e classe des affaires maritimes sont reclassés dans
le grade d'inspecteur » ; le texte « modifiant le décret n° 92-1204 »).

*Le compte.* 18 groupes rattachés avant, 13 après : les 5 faux défaits, aucun
ajouté. Déclarés, 844 puis 849. Les raisons, avant → après : « le libellé ne
se coupe pas » 66 → 56 ; « aucun corps » 34 → 0, remplacé par « la phrase ne
nomme pas le statut, et le texte n'est pas un statut » (32) et « le Noyau RH ne
cite, la veille ni le jour, pour aucun corps ni aucun grade, le statut que
nomme la phrase » (11) ; « la phrase nomme le statut par sa date, que les
visas ne résolvent pas en un seul décret » (5) ; « la phrase renvoie à … » (1) ;
inchangées : date non écrite 398, territoriale 134, groupe vide 124,
hospitalière 86, échelons 1, plusieurs coupes 1.

### Les 13 reclassements qui restent, relus un à un

Pour chacun : l'article, rouvert ; le statut ; la citation du noyau ; le grade
et la grille la veille et le jour (`grades.csv`), le nombre d'échelons de la
grille ces jours-là (élève, stagiaire, provisoires mis à part) ; les échelons
des lignes du tableau, tous parmi ceux des grilles.

- *N° 2004-1439, art. 23-1* (LEGIARTI000023734900, du 2011-07-01 au
  2018-01-01) : « Au 1er juillet 2011, les membres du corps d'encadrement et
  d'application de la police nationale sont reclassés conformément au tableau
  de correspondance suivant ». La phrase ne nomme aucun statut ; le texte en est
  un : « Décret n°2004-1439 du 23 décembre 2004 portant statut particulier du
  corps d'encadrement et d'application de la police nationale. » Le corps 00172
  cite le texte 296 (n° 2004-1439) depuis le 2005-01-01. Major de police,
  02774 : grille 00420 (4) → 02777 (5) ; lignes 1-4 → 1-4. Brigadier-chef de
  police, 02779 : 00423 (5) → 02782 (6) ; 1-5 → 1-5. Gardien de la paix,
  02780 : 00422 (12) → 02783 (13) ; 1-12 → 1-12. Conformes (3).
- *N° 2017-1031, art. 39* (LEGIARTI000034743634, depuis le 2017-05-12) : « Au
  1er septembre 2017, les fonctionnaires appartenant au corps des professeurs
  de lycée professionnel agricole régi par le décret n° 90-90 du 24 janvier
  1990 susvisé, dans sa rédaction antérieure au présent décret, et les agents
  détachés dans ce corps sont reclassés dans ce même corps ». Le corps 00003
  cite le texte 71 (« Décret n° 90-90 du 24 janvier 1990 relatif au statut
  particulier des professeurs de lycée professionnel agricole ») depuis le
  1989-09-01. Hors classe, 00007 : 00015 (7) → 03351 (6 ; la version du grade
  ne vaut que le 2017-09-01, R-B3 l'a dit) ; 1-7 → 1-6. Classe normale, 00006 :
  00014 (11) → 03352 (11) ; 1-11 → 1 et 3-11. Conformes (2).
- *N° 2017-786, art. 139* (LEGIARTI000034750757, depuis le 2017-05-08) : « Au
  1er septembre 2017, les fonctionnaires appartenant au corps des professeurs
  des écoles régi par le décret du 1er août 1990 susvisé, dans sa rédaction
  antérieure au présent décret, et les agents détachés dans ce corps sont
  reclassés dans ce même corps ». Le visa : « Vu le décret n° 90-680 du
  1er août 1990 modifié relatif au statut particulier des professeurs des
  écoles », seul à cette date ; LEGITEXT000006076298, « Décret n°90-680 du
  1 août 1990 relatif au statut particulier des professeurs des écoles ». Le
  corps 00021 cite le texte 160 depuis le 1990-09-01. Hors classe, 00043 :
  00051 (7) → 03312 (6) ; 1-7 → 1-6. Classe normale, 00042 : 00050 (11) →
  03311 (11) ; 1-11 → 1 et 3-11. Conformes (2).
- *N° 2017-786, art. 157* (LEGIARTI000034750857) : « … au corps des
  professeurs de lycée professionnel régi par le décret du 6 novembre 1992
  susvisé dans sa rédaction antérieure au présent décret … ». Le visa : « Vu le
  décret n° 92-1189 du 6 novembre 1992 modifié relatif au statut particulier
  des professeurs de lycée professionnel » ; LEGITEXT000006080320. Le corps
  00250 cite le texte 159 depuis le 1992-11-08. Hors classe, 00605 : 00613 →
  03316 (6) ; 1-7 → 1-6 ; le 2017-08-31, la grille 00613 a sept échelons, aux
  rangs 1 à 7, et redit leurs sept indices aux rangs 8 à 14, de nature
  « exceptionnel » (`etat/echelons.csv`, échelons 14988 à 14994) : les sept de
  l'origine en sont. Classe normale, 00606 : 00614 (11) → 03315 (11) ; 1-11 →
  1 et 3-11. Conformes (2).
- *N° 2017-786, art. 36* (LEGIARTI000034750953) : « … au corps des conseillers
  principaux d'éducation régi par le décret du 12 août 1970 susvisé … ». Le
  visa : « Vu le décret n° 70-738 du 12 août 1970 modifié relatif au statut
  particulier des conseillers principaux d'éducation » ; LEGITEXT000006061762,
  LEGITEXT000006061763. Le corps 00493 cite le texte 162 depuis le 1989-09-01.
  Hors classe, 01155 : 01163 (7) → 03292 (6) ; 1-7 → 1-6. Conforme (1).
- *N° 2017-786, art. 123* (LEGIARTI000034751013) : « … au corps des
  professeurs d'enseignement général de collège régi par le décret du 14 mars
  1986 susvisé … ». Le visa : « Vu le décret n° 86-492 du 14 mars 1986 modifié
  relatif au statut particulier des professeurs d'enseignement général de
  collège » ; LEGITEXT000006065551. Le corps 00490 cite le texte 168 depuis le
  1986-09-01. Hors classe, 01150 : 01158 (6) → 03309 (6) ; 1-6 → 1-6.
  Conforme (1).
- *N° 2019-50, art. 24* (LEGIARTI000038076578, depuis le 2019-02-01) : « I. -
  Au 1er février 2019, les fonctionnaires relevant du corps des conseillers
  pénitentiaires d'insertion et de probation régis par le décret n° 2010-1639
  du 23 décembre 2010 portant statut particulier du corps des conseillers
  pénitentiaires et de probation sont intégrés dans le corps régi par le
  présent décret ». Le texte : « Décret n° 2019-50 du 30 janvier 2019 portant
  statut particulier du corps des conseillers pénitentiaires d'insertion et de
  probation ». Le corps 01140 cite le texte 1310 (n° 2010-1639) du 2011-01-01
  au 2019-01-31 ; le corps 01230, le texte 6110 (n° 2019-50) depuis le
  2019-02-01. Hors classe, 03193 du corps 01140 (03325, 9) → première classe,
  04558 du corps 01230 (03594, 9) ; 1-9 → 1-9. Conforme (1).
- *N° 2019-50, art. 37* (LEGIARTI000038076610, depuis le 2021-01-01) : « Au
  1er janvier 2021, les fonctionnaires titulaires du premier grade du corps des
  conseillers pénitentiaires d'insertion et de probation sont reclassés
  conformément au tableau de correspondance suivant ». Le texte est le statut ;
  le corps 01230 cite le texte 6110. 04558 (03594, 9) → 04699 (03689, 14) ;
  1-9 → 6-14. Conforme (1).

## 2. Moyen : le Noyau RH, par ses corps et par ses grades, chaque citation datée

*L'écart.* `{**noyau_corps, **noyau_grades}`, deux dictionnaires indexés par le
code du corps : les grades écrasaient le corps, et ce que le corps citait
lui-même était perdu. Une citation valait pour toute la période, quelle que
soit la date de la version qui citait ; la preuve disait « le corps cite » ce
qu'un grade citait.

*La correction.* `corps.csv` puis `grades.csv`, lus l'un après l'autre ; chaque
citation garde qui cite (« le corps 00021 », « le grade 03762 du corps
00550 ») et les dates de sa version (`Depot.citations`). Une durée se rattache
au noyau sur les seuls jours où une version du corps ou de l'un de ses grades
cite le statut (`citations_sur`) ; un reclassement, si le corps cite le statut
nommé la veille ou le jour (`cite_au`). La preuve nomme qui cite, le texte et
les dates ; le corps d'abord, ses grades seulement là où il ne cite pas.

*Tests* : `test_le_noyau_cite_un_statut_par_ses_corps_comme_par_ses_grades`
(rouge : 20 raisons), `test_deux_corps_qui_citent_le_statut_et_ont_les_memes_grades_ne_se_rattachent_pas`
(rouge : 10 lignes), `test_la_preuve_du_noyau_dit_qui_cite_le_statut_et_vaut_sur_toute_la_periode`
(rouge : 2 lignes), et `test_la_preuve_d_un_reclassement_dit_qui_cite_le_statut_a_sa_date`,
une garde, verte d'emblée : les 13 reclassements de la partie 1 citaient déjà
un corps qui cite à la date.

*Le compte, durées.* Lignes rattachées : 573 avant, 582 après (12 ôtées, 21
ajoutées, dont 8 par la partie 3) ; grades de tableaux rattachés : 498, et 498
(11 perdus, 11 gagnés).

- *Ôtées, 12 lignes.* N° 2012-762 (texte 1142, « Décret n° 2012-762 du 9 mai
  2012 portant dispositions statutaires communes aux corps d'infirmiers de
  catégorie A des administrations de l'Etat ») : `corps.csv` le cite pour le
  corps 01102 (« Infirmiers des administrations de l'Etat ») et pour le corps
  01153 (« Infirmiers de la défense »), « 1142:origine », tous deux depuis le
  2012-06-01 ; les grades du 01153 (03248 à 03250, puis 04154 à 04156) ont les
  libellés et les grilles de ceux du 01102 (02947 à 02949, puis 03214 à 03216).
  Les 10 lignes (9 grades de tableaux, et la ligne d'un jour de R-B3) sont
  déclarées : « plusieurs corps du Noyau RH ont ce grade aux mêmes dates :
  01102, 01153 ». N° 83-1260, « Secrétaire d'administration de la recherche de
  classe exceptionnelle » et « … de classe normale », corps 00550 (2 lignes) :
  le corps cite le texte 1216 (n° 84-1207) ; les grades 01272 et 01274, du
  2002-02-03 au 2020-01-01, citent le texte 1212 (n° 95-83, qui modifie le
  n° 83-1260) ; seuls les grades 03762 à 03764, du 1984-01-01 au 1995-07-31,
  citent le texte 1135 (n° 83-1260). Déclarées : « … mais le Noyau RH n'y cite
  le n° 83-1260 ni pour le corps ni pour l'un de ses grades ».
- *Ajoutées par le noyau, 13 lignes (11 grades de tableaux qui n'étaient que
  déclarés ; les 2 du n° 96-158 l'étaient déjà au LEGI).* Chaque fois : le corps
  cite le statut à ces dates, le libellé est le même, les échelons aussi, un
  seul corps.
  - N° 96-158, art. 15, LEGIARTI000044467398, depuis le 2022-01-01 : « La durée
    du temps passé dans chacun des échelons des grades du corps de psychologue
    du ministère de la justice est fixée ainsi qu'il suit : GRADES ET ÉCHELONS
    DUREE Psychologue hors classe 8e échelon - 7e échelon 3 ans […] Psychologue
    de classe normale 11e échelon - 10e échelon 4 ans […] ». Corps 01282
    (« Psychologues du ministère de la justice », depuis le 2022-01-01,
    « 566:origine 7260:modificatif » ; texte 566 : n° 96-158). Grades 05071
    (03769, 8) et 05070 (03768, 11).
  - N° 97-364, LEGIARTI000006484256, du 2003-09-13 au 2013-10-01 : « GRADES ET
    ECHELONS DUREE Moyenne Minimale Contrôleurs du travail de classe
    exceptionnelle 5e échelon - - 4e échelon 2 ans 6 mois 2 ans […] Contrôleurs
    du travail de classe supérieure 6e échelon - - […] Contrôleurs du travail de
    classe normale 12e échelon - - […] ». Corps 00195 (« Contrôleurs du
    travail », depuis le 1997-01-01, « 141:origine 1416:modificatif » ; texte
    141 : n° 97-364). Grades 00471 (00479 : sept rangs, dont les deux premiers
    « provisoire », cinq échelons), 00472 (00480, 6), 00473 (00481, 12), du
    2003-09-14 au 2013-09-30.
  - N° 84-238, LEGIARTI000006507979, du 2007-01-01 au 2015-06-01 : « GRADES
    DUREE Moyenne Minimum Ingénieur principal des systèmes d'information et de
    communication 10e échelon - - […] Ingénieur des systèmes d'information et
    de communication 12e échelon - - […] ». Corps 00409 (« Ingénieurs des
    systèmes d'information et de communication du ministère », du 1983-01-01
    au 2015-05-31, « 387:origine 1458:abrogateur » ; texte 387 : n° 84-238).
    Grades 00988 (00996, 10) et 00990 (00998, 12).
  - N° 2011-1317, LEGIARTI000028020179, du 2013-10-02 au 2015-01-01 : « GRADE
    EN VOIE D'EXTINCTION ÉCHELONS DURÉE Directeur de service 14e échelon ――
    13e échelon 2 ans […] 1er échelon 1 an ». Corps 01040 (« Attachés
    d'administration de l'Etat », depuis le 2011-10-20, « 871:origine » ; texte
    871 : n° 2011-1317). Grade 03408 « Directeur de service » (03083, 14).
  - N° 2012-1098, LEGIARTI000026428751, du 2012-10-01 au 2016-01-01, redit par
    LEGIARTI000032719204 jusqu'au 2017-01-01 : « GRADE ÉCHELON DURÉE Assistant
    principal de service social 11e ― 10e 3 ans […] Assistant de service social
    13e ― 12e 4 ans […] ». Corps 01114 (« Assistants de service social des
    administrations de l'Etat », du 2012-10-01 au 2019-01-31, « 1177:origine » ;
    texte 1177 : n° 2012-1098). Grades 03081 (02987, 11) et 03080 (02977, 13).
  - N° 2015-576, LEGIARTI000030646858, du 2015-06-01 au 2017-01-01 : « GRADES ET
    ÉCHELONS DURÉE MOYENNE Ingénieur hors classe des systèmes d'information et
    de communication Echelon spécial 7e échelon - 6e échelon 3 ans […]
    Ingénieur principal des systèmes d'information et de communication 10e
    échelon - […] Ingénieur des systèmes d'information et de communication 12e
    échelon - […] ». Corps 01172 (depuis le 2015-06-01, « 1458:origine » ;
    texte 1458 : n° 2015-576). Grades 03700 (03106 : sept échelons et un
    « exceptionnel », 8, comme le tableau, sept et le spécial), 03701 (03107,
    10), 03702 (03108, 12).
- *Les 20 raisons fausses de R-B3* : 6 deviennent des rattachements (ci-dessus :
  n° 2011-1317, « Directeur de service » ; n° 2012-1098, deux ; n° 2015-576,
  trois) ; les 14 autres disent désormais « aucun grade des corps du Noyau RH
  qui citent le n° … (00454 ; 01040 ; 00409, 01172) ne porte ce libellé »
  (n° 99-911, 1 ; n° 2011-1317, 7 ; n° 2015-576, 6, dont les tableaux écrivent
  « Ingénieur hors classe » sans « des systèmes d'information et de
  communication »).
- *La preuve dit qui cite.* Des 154 lignes du lien `noyau`, aucune ne repose
  plus sur la seule citation d'un grade : le corps cite à chaque fois. Les 11
  preuves de R-B3 (2 de durées, 9 de reclassements) : les 2 durées sont ôtées
  (le n° 83-1260, ci-dessus) ; des 9 reclassements, 5 sont les rattachements
  faux, défaits, et 4 (n° 2017-786, art. 139, 36 et 123) ont désormais pour
  preuve le statut nommé, que le corps cite lui-même.

*`a_lire_au_jorf.csv`.* Le cas `manque` disait du LEGI ce qu'il ne dit pas.
87 des 127 textes ont, avant leur premier tableau de durées lu, un article de
durées que le lecteur n'a pas lu (`durees/non_lus.csv`, recompté ici comme
R-B3 : 87) : ils passent au cas `non_lu`, avec ces articles et leur motif ; les
40 autres restent `manque`, et leur phrase ne dit que ce que les fichiers du
dépôt disent. Exemple, à la source : n° 87-1103, art. 15
(LEGIARTI000006370660, du 1987-12-31 au 1996-02-08) : « La durée maximale et
la durée minimale du temps passé dans chacun des échelons sont fixées ainsi
qu'il suit : GRADES ET ÉCHELONS DUREE Maximale Minimale 7e échelon 3 ans
6 mois 3 ans […] » (`test_un_article_de_durees_que_le_lecteur_n_a_pas_lu_ne_se_dit_pas_absent_du_legi`).
Comptes : 137 `abime`, 87 `non_lu`, 40 `manque` (264, comme avant).

## 3. Faible : les preuves

- *Les versions de la période* (`Index.versions_sur`) : le lien `article` lit
  et cite chaque version de l'article en vigueur sur la période (même texte,
  même numéro d'article, comme les relie le lecteur des grilles), non la seule
  que nomme le fichier des échelons. Avant : 226 liens `article`, 12 lignes sans
  version en vigueur citée, 43 versions citées hors de leur période ; après :
  226, 0, 0 ; 48 preuves refaites, aucun rattachement déplacé (les versions de
  la période nomment toutes le statut). À la source : l'art. 3 de
  LEGITEXT000031320442 (greffiers), LEGIARTI000048278636 du 2023-11-01 au
  2024-03-01 puis LEGIARTI000049196634 depuis, chacune « régi par le décret
  n° 2015-1275 du 13 octobre 2015 susvisé est fixé ainsi qu'il suit » ; l'art. 5
  de LEGITEXT000026383946, LEGIARTI000041912445 jusqu'au 2025-03-20 puis
  LEGIARTI000051351757, chacune « régis par le décret du 29 mars 1993 susvisé »
  (`test_la_preuve_article_cite_les_versions_en_vigueur_sur_la_periode`).
- *Deux grilles du même nom dans un texte* : la preuve nomme l'autre et dit
  pourquoi elle est écartée. 19 preuves : 11 par les échelons, 8 parce que
  l'article de l'autre ne nomme pas le statut. À la source, n° 2021-1264
  (LEGITEXT000044130353) : art. 1 (LEGIARTI000044130360), « L'échelonnement
  indiciaire applicable aux grades des corps de pédicures-podologues,
  ergothérapeutes, psychomotriciens et orthoptistes […] Classe supérieure 10
  886 9 836 […] » ; art. 2 (LEGIARTI000044130362), « … des corps de
  masseurs-kinésithérapeutes et d'orthophonistes […] Classe supérieure 9 940
  8 906 […] » (`test_la_preuve_dit_pourquoi_la_grille_du_meme_nom_est_ecartee`).
- *Le décret qui a modifié le statut* n'est plus un second statut
  (`MODIFIE_PAR`). 32 textes de grilles voient leur liste de statuts réduite ;
  8 lignes s'ajoutent, par le visa, toutes à des grades déjà rattachés au
  noyau, relues à la source :
  - n° 97-364 (3) : « Arrêté du 11 septembre 2003 relatif à l'échelonnement
    indiciaire applicable au corps des contrôleurs du travail »
    (LEGITEXT000019591150), visa « Vu le décret n° 97-364 du 18 avril 1997
    portant statut particulier du corps des contrôleurs du travail, modifié par
    le décret n° 2003-870 du 11 septembre 2003, Arrêtent : » ; art.
    LEGIARTI000019591152 : « L'échelonnement indiciaire dans le corps des
    contrôleurs du travail est fixé comme suit : GRADES ET ECHELONS INDICES
    BRUTS Contrôleurs du travail de classe exceptionnelle 5e échelon 638 4e
    échelon 603 3e échelon 572 2e échelon 542 1er échelon 516 2e échelon
    provisoire 482 […] » ; 5, 6 et 12 échelons, comme le tableau ;
  - n° 91-1025 (2) : « Arrêté du 29 septembre 2000 fixant l'échelonnement
    indiciaire applicable au corps des médecins inspecteurs de santé publique »
    (LEGITEXT000019668607), visa « Vu le décret n° 91-1025 du 7 octobre 1991
    relatif au statut particulier des médecins inspecteurs de santé publique,
    modifié par le décret n° 2000-956 du 29 septembre 2000, Arrêtent : » ; art.
    LEGIARTI000019668611 : « … Médecin général de santé publique 3e échelon HEC
    2e échelon HEB 1er échelon HEA […] Médecin inspecteur de santé publique 9e
    échelon 966 […] » ; 3 et 9 échelons, comme le tableau
    (LEGIARTI000006711476) ;
  - n° 98-385 (3) : « Arrêté du 2 mai 2007 fixant l'échelonnement indiciaire
    applicable au corps des personnels scientifiques de laboratoire de l'Agence
    française de sécurité sanitaire des produits de santé »
    (LEGITEXT000019420380), visa « Vu le décret n° 98-385 du 18 mai 1998,
    modifié par le décret n° 99-142 du 4 mars 1999 et par le décret
    n° 2007-671 du 2 mai 2007, portant statut particulier des personnels
    scientifiques de laboratoire de l'Agence française de sécurité sanitaire
    des produits de santé, Arrêtent : » ; art. LEGIARTI000019420383, du
    2007-05-05 au 2017-01-01 : « Chef de laboratoire de 1re classe 6e échelon
    HEB 5e échelon HEA 4e échelon 1015 3e échelon 935 2e échelon 852 1er
    échelon 801 », « Assistant 11e échelon 801 10e échelon 780 […] » ; 6, 11 et
    11 échelons, comme le tableau (LEGIARTI000006507038).

  Les deux raisons du n° 90-973 (ingénieurs du génie sanitaire) deviennent « les
  échelons diffèrent » (`test_le_decret_qui_a_modifie_le_statut_n_est_pas_un_second_statut`).
- *La citation inexacte* : le commentaire du test du texte commun cite
  désormais l'art. 116 du n° 2017-171 (LEGIARTI000034028850) mot pour mot :
  « L'échelonnement indiciaire applicable au corps des ingénieurs de recherche
  régi par le décret du 31 décembre 1985 susvisé est fixé ainsi qu'il suit ».
  La note de B3, un récit, n'est pas récrite : un renvoi daté y est ajouté.
- *Une grille à la fois, par source* : le cas d'un jour des infirmiers est ôté
  avec eux ; aucun grade n'a plus deux grilles d'une même source le même jour
  (`test_un_grade_n_a_qu_une_grille_a_la_fois_par_source`, une garde, verte).
  Reste un rattachement d'un jour, juste à la source (R-B3, cas 2 : n° 90-90,
  hors classe, grille 03351, le 2017-09-01). 70 paires rattachent un grade, aux
  mêmes dates, à une grille du LEGI et à une du noyau : l'en-tête de
  `durees.csv` le dit désormais.

## Ce que le texte ne tranche pas

- Le noyau double parfois les échelons d'une grille de lignes « exceptionnel »
  aux mêmes indices (00613, ci-dessus) : la règle « les échelons des lignes
  sont parmi ceux de la grille » les accepte ; elle ne prouve pas que le noyau
  a raison de les écrire.
- Un décret qui modifie un seul statut (« modifiant le décret n° 92-1204 … »)
  et dont la phrase ne nomme pas le corps est désormais déclaré (32 groupes) :
  son titre nomme le statut, mais le chaînage ne lit pas les titres. Les
  rattacher demanderait cette règle, et son test.
- Choisir entre deux grilles du même nom par les échelons seuls (11 preuves)
  reste un choix de la règle : il est écrit, non tranché par le texte.

## Les tests et le paquet

`tests/test_chainage_grilles.py` : 25 passés. `python -m pytest -m rapide` :
4 338 passés, 8 sautés, 13 rouges ; `PRESOMPTIONS_DECALEES=1 python -m pytest
-m rapide` : 4 139 passés, 207 sautés, les mêmes 13 rouges ; tous de
`test_pages_en_dossier.py` (10 « page toute faite à jour », 3 « corps de la
page »), les pages que GitHub refait quand `main` bouge, hors de cette file.
Aucun autre fichier de tests ne lit `grilles/chainage/` ni le script
(`grep -l` sur `tests/*.py`). `python scripts/construire_donnees.py`, puis
`git status` : le paquet ne bouge pas.

## Ce qui reste

Les rattachements à faire sans deviner, que B3 dresse ; la règle du décret qui
modifie un seul statut, nommé dans son titre ; les 40 cas `manque` et les 87
`non_lu`, à lire ; une relecture indépendante de ces corrections, contre les
sources.
