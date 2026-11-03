# Corrections de la relecture R-B3-bis du chaînage aux grilles (file B3-ter)

**Le 3 novembre 2026 : l'échelon exceptionnel des majors de police est mis à
son rang dans la grille d'accueil, le 5e ; les échelons des durées se
comparent date par date, et les 8 lignes que R-B3-bis relève sont coupées ; le
décret commun des infirmiers (n° 2012-762) rattache ses grades à chacun de ses
corps ; deux raisons et deux citations sont reprises. Durées : 511 grades de
tableaux rattachés sur 1 675, au lieu de 498 ; 613 lignes rattachées, au lieu
de 582. Reclassements : 13 groupes rattachés sur 862, comme avant.**

Demande : la session d'orchestration de la vague 6, file B3-ter, le 3 novembre
2026 : corriger, dans l'ordre et chaque fois par le test qui reproduit l'écart,
ce que la relecture R-B3-bis (`2026-11-03-relecture-corrections-r-b3.md`,
commit fd7dab8) relève ; ne rien rattacher de plus que ce que la correction
rend certain ; laisser à d'autres le sommet d'échelon non écrit, les autres
décrets communs et le n° 60-403 identifié par son numéro et sa date. Exigence
du propriétaire, le même jour : aucune erreur, tout prouvé par écrit, jamais de
mémoire.

- *La source.* L'index LEGI publié (`dila_index.py legi --recuperer`, dump du
  13 juillet 2025, à jour de l'incrément 20261102-213929, celui de B3, de R-B3,
  de B3-bis et de R-B3-bis), table `doc` ; le Noyau RH du CISIRH au dépôt
  (`data/reference/grilles/etat/`, juillet 2026). Chaque article et chaque
  notice cités ici ont été ouverts pendant la session ; le JORF ne l'a pas été.
- *L'état d'avant* est celui de fd7dab8, identique à 33b4ba7 (B3-bis) pour
  `chainage/`. Les comptes se refont en comparant les fichiers de `chainage/`
  de fd7dab8 à ceux de bbfdb76, ligne à ligne sur (texte, article, tableau,
  groupe, statut, début, fin, source, texte de grille, grille, corps, lien).
- *Les commits* : c5a1a54 (l'exceptionnel), c1ed16d (date par date), fe4e8dc
  (le n° 60-403), c3050f3 (les articles non lus), bbfdb76 (les infirmiers).
  Chaque test nouveau a été vu rouge, pour la raison de l'écart, avant le code,
  sauf `test_un_grade_se_rattache_les_jours_ou_sa_grille_a_ses_echelons`, écrit
  après la coupe pour garder les grades qu'elle gagne, et vu rouge sur le
  fichier de fd7dab8.

## 1. L'échelon exceptionnel des majors de police (moyen)

Décret n° 2004-1439, art. 23-1 (LEGIARTI000023734900, du 2011-07-01 au
2018-01-01) : « Major de police Major de police Echelon exceptionnel Echelon
exceptionnel Ancienneté acquise 3e échelon 3e échelon […] ». Décret
n° 2010-564, art. 5, la veille (LEGIARTI000023402803, du 2011-01-01 au
2011-07-01) : « Major de police Echelon exceptionnel (1) 3e échelon 2e échelon
1er échelon 630 615 597 579 » ; le jour (LEGIARTI000023750120, du 2011-07-01 au
2012-01-01) : « Major de police Echelon exceptionnel (1) 4e échelon 3e échelon
2e échelon 1er échelon 631 620 616 598 581 ». Le Noyau RH le dit de même :
grille 00420 le 2011-06-30, 579, 597, 615, puis 630 « exceptionnel » ; grille
02777 le 2011-07-01, 581, 598, 616, 620, puis 631 « exceptionnel ».
L'exceptionnel est le 4e à l'origine, le 5e à l'accueil ; le lecteur des
reclassements, qui le range au-dessus du plus haut échelon écrit de son côté du
tableau, le met au 4 des deux côtés (`reclassements/lignes.csv`, ligne 1).

*Le test, rouge* : `test_l_echelon_exceptionnel_se_range_a_sa_place_dans_la_grille`
(la fonction manquait) et
`test_l_echelon_exceptionnel_des_majors_de_police_est_le_cinquieme_a_l_accueil`
(la colonne manquait). *La correction* : le chaînage des reclassements place
chaque échelon du tableau dans sa grille par sa nature, non par le seul nombre
des rangs (`rang_dans_la_grille`) : un échelon numéroté garde son numéro, si la
grille l'a et qu'il n'y est pas l'exceptionnel ; le spécial ou l'exceptionnel
est l'unique échelon exceptionnel de la grille, à son rang (le noyau n'a pas de
nature « spécial » : `etat/echelons.csv` n'a que vide, élève, exceptionnel,
fonctionnel, provisoire, stagiaire). La colonne neuve `rangs_grille` de
`chainage/reclassements.csv` écrit ce rang, qui l'emporte sur celui de
`lignes.csv` : « origine exceptionnel 4 ; accueil exceptionnel 5 » pour les
majors, « origine exceptionnel 12 » pour les gardiens de la paix (la veille :
« Gardien de la paix Exceptionnel (4) 11e échelon […] 1er échelon »), vide pour
les 11 autres groupes, qui n'ont que des échelons numérotés. `lignes.csv` n'est
pas récrit : son lecteur ne connaît pas les grilles.

*Les comptes* : 13 groupes rattachés avant et après ; une raison récrite, celle
des brigadiers de police, déclarés avant comme après (« origine « 7-provisoire »
(rang 7) : la grille 00421 a 6 échelons hors élève, stagiaire et provisoires,
aucun exceptionnel ») : la grille 00421 a, le 2011-06-30, six échelons
ordinaires et le 7e provisoire (541), comme LEGIARTI000023402803 l'écrit
(« Brigadier de police 7e échelon provisoire (3) 6e échelon […] »).

## 2. Les échelons des durées, date par date (moyen)

*Le test, rouge* : `test_les_echelons_de_la_grille_sont_ceux_du_tableau_a_chaque_date`
reprend chaque ligne rattachée à chaque jour où sa grille change, et trouve, sur
le fichier de fd7dab8, les 8 lignes de R-B3-bis et elles seules ; puis
`test_un_grade_n_est_pas_rattache_les_jours_ou_sa_grille_n_a_pas_ses_echelons`
(greffiers, sapeurs-pompiers) et
`test_un_grade_se_rattache_les_jours_ou_sa_grille_a_ses_echelons` (les grades
gagnés), rouges tous trois sur ce fichier. *La correction* : la période commune
au tableau et à la grille se coupe à chaque jour où les échelons de la grille
changent (`periodes`) ; seuls les morceaux aux rangs du tableau se rattachent ;
le lien (visa ou article) se prouve, comme avant, sur toute la période, et la
preuve `article` cite les versions en vigueur sur le morceau rattaché. Les
jours où une grille rattachée ailleurs n'a pas les échelons du tableau, et
qu'aucun autre rattachement ne couvre, sont déclarés, en une ligne à eux ; les
jours où aucune grille candidate n'existe restent, comme avant, sans ligne.

*Les 8 lignes, coupées.*

- *Greffier, Greffier principal* (n° 2015-1275, art. 18, LEGIARTI000035606314,
  [2017-01-01, 2024-03-01)) : les versions de l'art. 3 du n° 2015-1277,
  LEGIARTI000035603091 (2016-01-01 au 2018-01-01) et LEGIARTI000036489952
  (2018-01-01 au 2023-11-01), ne sont pas lues (`etat_legi/non_lus.csv` :
  « valeurs hors des lignes, dans « Greffier principal Echelon spécial - 705 713
  723 11 ème échelon - 701 707 707 » ») ; la grille du dépôt n'a aucun échelon
  du 2016-01-01 au 2023-10-31. Rattachées du 2023-11-01 au 2024-03-01
  (LEGIARTI000048278636 : « Greffier 13e échelon 651 12e échelon 612 […] »),
  déclarées du 2017-01-01 au 2023-11-01.
- *Lieutenant-colonel, Commandant* (n° 2016-2008, art. 12, LEGIARTI000033792383,
  [2017-01-01, 2025-06-14) au dépôt) : la grille a 7 et 8 échelons jusqu'au
  2020-12-31, le tableau 8 et 9. Rattachées du 2021-01-01 au 2025-06-14,
  déclarées avant. Le texte le confirme : la version de l'art. 12 en vigueur
  depuis le 2017-12-24 (LEGIARTI000036439942) s'ouvre sur « A compter du
  1er janvier 2021 : […] 2° Le grade de commandant comprend neuf échelons ;
  3° Le grade de lieutenant-colonel comprend huit échelons » (la première,
  LEGIARTI000033792383, disait « A compter du 1er janvier 2020 »). Le lecteur
  des durées date le tableau du 2017-01-01, l'entrée en vigueur de l'article,
  sans lire cette date.
- *Ingénieur des études et de l'exploitation de l'aviation civile de classe
  normale* (n° 71-917, LEGIARTI000037197020, [2017-01-01, 2025-07-01)) : du
  2018-01-01 au 2025-06-30, la grille du LEGI a les rangs 2 à 11, le 1er étant
  écrit sous le stagiaire (n° 2009-1322, art. 2, LEGIARTI000037196211 : « … de
  classe normale 11e 774 780 780 […] 2e 483 490 500 Ingénieur stagiaire des
  études et de l'exploitation de l'aviation civile 1er 434 441 444 »). Rattachée
  au LEGI du 2017-01-01 au 2018-01-01 ; le reste est couvert par le noyau
  (grille 03500, corps 00437), inchangé : rien à déclarer.
- *Technicien supérieur des études et de l'exploitation de l'aviation civile,
  classe principale et classe normale* (n° 93-622, LEGIARTI000006471150,
  [2007-01-01, 2013-11-15)) : au noyau, les grilles 00226 et 00227 n'ont aucun
  échelon avant le 2009-10-27 (premier `debut` de `etat/echelons.csv`).
  Rattachées au noyau du 2009-10-27 au 2013-11-15 ; avant, couvertes par le
  LEGI (rattachées du 2007-01-01 au 2009-10-31, inchangées).
- *Puéricultrice de classe normale* (n° 2014-923, LEGIARTI000032578561,
  [2017-01-01, 2022-01-01)) : la grille n'a aucun échelon du 2017-01-01 au
  2017-05-10 (n° 2014-925, art. 1 : LEGIARTI000029383562 jusqu'au 2016-01-01,
  LEGIARTI000034729358 depuis le 2017-05-11 ; la version d'entre deux,
  LEGIARTI000032546846, écrit « classenormale », que le lecteur des grilles
  range dans une autre grille, `puericultrice-de-classenormale`). Rattachée
  depuis le 2017-05-11, déclarée avant.

*Ce que la coupe rattache de plus*, chaque fois que la grille a les échelons
du tableau sur un morceau seulement, rouvert au texte :

- *Chargés de recherche hors classe* (n° 83-1260, art. 34, LEGIARTI000034794301,
  [2017-09-01, 2024-01-01) : « Chargés de recherche hors classe 7e échelon -
  6e échelon 5 ans […] 1er échelon 1 an ») : la grille du n° 2012-1162, art. 2
  (« régis par le décret du 30 décembre 1983 susvisé »), a sept échelons
  jusqu'au 2022-04-30 (LEGIARTI000034774290, LEGIARTI000036489856 : « Chargé de
  recherche hors classe 7e échelon HEA HEA HEA 6e échelon 1021 […] ») et huit
  ensuite (LEGIARTI000045731731 : « Chargé de recherche hors classe Echelon
  exceptionnel HEB 7e échelon HEA […] »). Rattachée du 2017-09-01 au
  2022-05-01, déclarée ensuite ; avant, déclarée en entier.
- *Infirmier en soins généraux hors classe*, territorial (n° 2012-1420, art. 18,
  LEGIARTI000026796816, [2013-01-01, 2016-05-15) : « Infirmier en soins
  généraux hors classe 11e échelon ― ― 10e échelon 4 ans 3 ans 8 mois […] ») :
  le n° 2012-1421, art. 1, l'écrit au singulier jusqu'au 2016-01-01
  (LEGIARTI000026797761 : « Infirmier en soins généraux hors classe 11e échelon
  700 730 […] ») et au pluriel ensuite (LEGIARTI000032546841 : « Infirmiers en
  soins généraux hors classe 11e échelon 736 - - - […] ») ; le lecteur en fait
  deux grilles, qui, réunies sur toute la période, se chevauchaient (déclaré :
  « plusieurs grilles du LEGI prouvées aux mêmes dates »). Date par date,
  chacune a les onze échelons sur son morceau et l'autre aucun : deux lignes.
- *Lieutenant-colonel, Commandant*, art. 24 du n° 2016-2008 (LEGIARTI000033792407,
  « Jusqu'au 31 décembre 2019 : […] 2° Le grade de commandant comprend huit
  échelons ; 3° Le grade de lieutenant-colonel comprend sept échelons » ; depuis
  le 2017-12-24, LEGIARTI000036439940, « Jusqu'au 31 décembre 2020 ») : la
  grille a 7 et 8 échelons jusqu'au 2020-12-31. Rattachées du 2017-01-01 au
  2021-01-01, déclarées du 2021-01-01 au 2025-06-14 ; avant, déclarées en
  entier. Le lecteur des durées laisse ce tableau ouvert, sans lire « Jusqu'au
  31 décembre 2020 » ; la coupe tombe sur cette date.

*Déclarés, sans rien perdre* : la classe hors classe des professeurs de lycée
professionnel agricole (n° 90-90, art. 18, LEGIARTI000034798803), rattachée le
seul 2017-09-01 (grille 03351, six échelons, comme le tableau), est déclarée du
2017-09-02 au 2021-01-01, où le noyau donne à la grille 03351 un 7e échelon,
sans indice.

*Les comptes, durées* (fd7dab8 → c1ed16d) : lignes rattachées 582 → 587 (8
coupées, remplacées par 8 plus courtes ; 5 gagnées : chargés de recherche 1,
infirmiers territoriaux 2, art. 24 2) ; lignes déclarées 1 185 → 1 190 (+6 :
greffiers 2, art. 12 2, puéricultrice 1, lycée agricole 1 ; −1 : les
infirmiers territoriaux ; les déclarations entières des chargés de recherche et
de l'art. 24, 3, deviennent 3 déclarations partielles) ; grades rattachés
498 → 502.
Huit raisons de lignes restées déclarées gagnent leurs dates ou « n'a aucun
échelon » ; quatre preuves écrivent « elle n'a aucun échelon » au lieu de
« ses échelons [] ne sont pas ceux du tableau ».

## 3. Les écarts faibles

*Le n° 60-403* (`test_la_raison_ne_dit_pas_inconnu_du_noyau_un_decret_qu_il_porte_sans_nor`,
rouge). N° 2017-786, art. 12 (LEGIARTI000034750817) : « régi par le décret du
22 avril 1960 susvisé » ; le visa : « Vu le décret n° 60-403 du 22 avril 1960
modifié relatif aux dispositions statutaires applicables aux chargés
d'enseignement de l'éducation physique et sportive » ; aucune notice du LEGI
(`notices_du_decret` : vide) ; le Noyau RH : texte 166, « Décret n° 60-403 du
22 avril 1960 relatif aux dispositions statutaires applicables aux chargés
d'enseignement de l'éducation physique et sportive. », JORFTEXT000000501563,
NOR vide. Les trois groupes restent déclarés ; leur raison dit désormais
« décret qu'aucune notice du LEGI n'identifie, et que le Noyau RH porte sans NOR
(texte 166) : le chaînage ne l'y identifie que par son NOR ». L'identifier par
son numéro et sa date n'est pas fait ici.

*« N article(s) »* (`test_un_article_de_durees_que_le_lecteur_n_a_pas_lu_ne_se_dit_pas_absent_du_legi`,
rouge sur le n° 58-778, 6 pour 5). Le nombre dit est celui des articles
distincts ; celui des relevés (article, motif) de `durees/non_lus.csv` s'écrit
à part : n° 86-492, art. 19-2 (LEGIARTI000006505183, du 1997-05-31 au
1998-09-04 : « ECHELONS : Du 1er au 2e échelon DUREE D'ECHELON : 3 ans ECHELONS
: Du 2e au 3e échelon […] »), « 1 article de durées que le lecteur n'a pas lu
(durees/non_lus.csv, 4 relevés) ». Sept cas sur 87 changent de nombre : n°
58-778 (6 → 5), 84-135 (13 → 5), 86-492 (4 → 1), 90-90 (4 → 3), 92-1432 (6 →
3), 96-1113 (5 → 2), 92-843 (3 → 1) ; les 87 changent de texte.

*Deux citations de la note de B3-bis*, qui est un récit : un renvoi daté, au
bout de la note, donne les titres exacts (LEGITEXT000006061489 : « Décret
n°67-91 du 20 janvier 1967 relatif au statut particulier des géomètres de
l'institut géographique national *IGN* » ; LEGITEXT000024751171 : « Décret
n° 67-91 du 20 janvier 1967 relatif au statut particulier des géomètres de l'
Institut national de l'information géographique et forestière » ; corps 00409 :
« Ingénieurs des systèmes d'information et de communication du ministère de
l'intérieur »).

*Les infirmiers du n° 2012-762*
(`test_un_decret_commun_qui_enumere_ses_corps_rattache_le_grade_a_chacun`,
rouge). Art. 1 (LEGIARTI000025855207, seule version, depuis le 2012-05-11) :
« Sont classés dans la catégorie A prévue à l'article 29 de la loi du 11
janvier 1984 susvisée et sont régis par le présent décret les corps ci-dessous
énumérés : 1° Le corps des infirmiers de l'Etat qui constitue un corps à
vocation interministérielle relevant du ministre chargé de la santé ; 2° Le
corps des infirmiers de la défense ; 3° Le corps des infirmiers de l'éducation
nationale et de l'enseignement supérieur. » Art. 14, à ses quatre versions
(LEGIARTI000025855171, 032526045, 032526029, 044635065) : « La durée [moyenne]
du temps passé dans chacun des échelons des grades des corps d'infirmiers
régis par le présent décret est fixée ainsi qu'il suit ». Au noyau, trois corps
ont le texte 1142 (n° 2012-762) pour origine (« 1142:origine »), depuis le
2012-06-01 : 01102 (« Infirmiers des administrations de l'Etat »), 01144
(« Infirmiers de l'éducation nationale et de l'enseignement supérieur »), 01153
(« Infirmiers de la défense ») ; ce sont donc les trois corps de l'art. 1, et
le tableau vaut pour chacun. C'est certain ; le rattachement se fait, corps par
corps, par la même règle (libellé, période, citation, échelons date par date).

La règle est écrite pour ce seul décret : `COMMUNS` porte l'article et la
citation, que le script vérifie au LEGI (seule version en vigueur sur la
période, citation mot pour mot), avec la phrase du tableau (« régis par le
présent décret ») et l'origine de chaque corps au noyau. Le n° 91-783 (corps
00671 et 00873, assistants de service social), autre décret commun, n'est pas
lu : ses deux grades restent déclarés, et un test le garde. Au noyau, la classe
supérieure a, le 2017-01-01, deux grades en vigueur dans chaque corps (03043 et
04074 au 01102, 03249 et 04155 au 01153), aux grilles 02948 et 03215, de sept
échelons l'une et l'autre, comme le tableau : ce jour-là n'est rattaché à
aucune, il est déclaré (« le chaînage ne choisit pas »).

*Les comptes, durées* (c3050f3 → bbfdb76) : 26 lignes rattachées de plus, au
noyau. Les 9 grades des art. 14 de 2012 à 2021, déclarés pour « plusieurs
corps », se rattachent aux corps 01102 et 01153, 18 lignes ; ceux du 01144
s'écrivent « Infirmier hors classe de l'éducation nationale et de
l'enseignement supérieur », que le libellé du tableau ne porte pas. Les 2
grades de l'art. 14 de 2022 (LEGIARTI000044635065 : « Infirmier hors classe
11e échelon - […] Infirmier 11e échelon - […] »), déjà rattachés au LEGI depuis
le 2024-04-01, se rattachent au noyau depuis le 2022-01-01 aux trois corps,
dont les grades portent depuis 2022 les mêmes libellés : 8 lignes (grilles 03752
et 03751, de onze échelons ; au 01144, depuis le 2024-05-01, 03923 et 03922, de
onze échelons). Lignes déclarées : −9 (les « plusieurs corps »), +1 (le
2017-01-01). Grades rattachés 502 → 511.

## 4. Les comptes, d'un bout à l'autre

fd7dab8 → bbfdb76. Durées : 1 767 → 1 795 lignes ; rattachées 582 → 613 (+39,
−8) ; déclarées 1 185 → 1 182 (+10, −13) ; grades rattachés 498 → 511 (13
gagnés, aucun perdu). Reclassements : 862 groupes, 13 rattachés, 849 déclarés,
avant et après ; 4 raisons récrites (les brigadiers, les trois groupes du
n° 60-403) ; `rangs_grille` écrit pour 2 groupes. `a_lire_au_jorf.csv` : 137
`abime`, 87 `non_lu`, 40 `manque`, avant et après ; les 87 `non_lu` changent de
texte, 7 de nombre.

## 5. Les tests et le paquet

`tests/test_chainage_grilles.py` : 32 passés (25 avant), dont 7 nouveaux. Trois
sont récrits : celui qui gardait l'unicité du corps au noyau sur le n° 2012-762
la garde désormais sur le n° 91-783 ; celui d'une grille à la fois compte, au
noyau, par corps ; celui des cas `non_lu` compte les articles. Aucun autre
fichier de tests ne lit `chainage/` (`grep -l chainage tests/*.py`).
`python -m pytest -m rapide` : 4 349 passés, 8 sautés, 13 rouges, tous de
`test_pages_en_dossier.py`, les pages toutes faites que GitHub refait quand
`main` bouge (les 13 de R-B3-bis) ; `PRESOMPTIONS_DECALEES=1 python -m pytest
-m rapide` : 4 150 passés, 207 sautés, les mêmes 13 rouges.
`python scripts/construire_donnees.py`, puis `git status` : rien de changé hors
les fichiers de cette étape ; le paquet ne lit pas `chainage/`.

## Ce qui reste

- Les causes en amont : la version des grilles des greffiers non lue
  (2016-2023) ; la date d'effet des art. 12 et 24 du n° 2016-2008 (« A compter
  du 1er janvier 2021 », « Jusqu'au 31 décembre 2020 »), que le lecteur des
  durées ne lit pas ; « classenormale », que le lecteur des grilles ne recoud
  pas.
- Rattacher plus sans deviner : le sommet d'échelon non écrit ; les autres
  décrets communs (n° 91-783), chacun par son article lu ; le n° 60-403 par son
  numéro et sa date ; la date qui ouvre la phrase, le grade avant l'en-tête, le
  décret modifiant un seul statut.
- Une relecture indépendante de ces corrections, contre les sources.
