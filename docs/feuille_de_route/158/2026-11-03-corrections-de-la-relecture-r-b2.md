# Corrections de la relecture R-B2 des durées d'échelon (file B2-bis)

File B2-bis, le 3 novembre 2026 : les sept écarts de la relecture R-B2 (commit b121b49,
note `2026-11-03-relecture-durees-d-echelon.md`) sur les durées d'échelon de la session B2
(commit 04cbe34), chacun rouvert ici au LEGI avant d'être corrigé, et trois défauts de plus,
trouvés en contre-lisant. La source : l'index LEGI publié du dépôt, récupéré sans
reconstruction (`dila_index.py legi --recuperer`, à jour de l'incrément du 2 novembre 2026,
20261102-213929, le même que R-B2), interrogé par `dila_cherche.py legi` (`--texte`, `--num
… --titre`, `--diff`, `--le`, `--motif`) ; pour deux dates d'effet, l'index JORF publié (à
jour au 3 novembre 2026) ; pour le septième écart, le Noyau RH de l'État déjà au dépôt
(`data/reference/grilles/etat/`). Chaque correction commence par son test, vu rouge pour la
raison attendue, puis le code jusqu'au vert (`tests/test_durees_echelon.py`, de 21 à 35
tests). Les valeurs attendues sont lues dans les articles, recopiés mot pour mot de l'index.

**Le décompte, avant (b121b49) et après.**

| | Avant | Après |
|---|---|---|
| Textes | 720, dont 336 avec un tableau lu | 727, dont 340 |
| Tableaux lus | 762 (État 495, territoriale 172, hospitalière 78, militaires 17) | 777 (506, 178, 77, 16) |
| Lignes | 14 345 (8 154, 3 143, 1 820, 1 228) | 14 506 (8 400, 3 184, 1 787, 1 135) |
| Valeurs certifiées : rang, unique, moyenne, minimale, maximale | 14 345, 8 507, 3 323, 3 460, 1 058 | 14 506, 8 626, 3 323, 3 462, 1 060 |
| Non lus | 1 655, dont 1 155 avec un rang de tableau | 1 249, dont 750 |

Le passage, commit par commit : versions jamais en vigueur, −6 tableaux et −178 lignes,
+7 non lus ; le paragraphe « II.- », +14 tableaux et +268 lignes, −28 non lus ; la case
« Spécial » et « Avant le », +1 tableau et +26 lignes, −1 non lu ; l'emploi avant l'en-tête,
+6 tableaux et +45 lignes ; les fiches, −384 non lus (−409, +25), +7 textes. Toutes les
lignes restent certifiées, identiques à leur source (`verifier_donnees.py`).

## 1. Les versions jamais en vigueur (moyen)

Le LEGI date certaines versions d'une fin antérieure ou égale à leur début ;
`dila_cherche.py --num … --titre …` les marque « (jamais en vigueur) ». Rouvertes ici, elles
sont **sept**, et non six : R-B2 a relevé les six dont la période était impossible ; la
septième ouvrait une période réunie à la version suivante, qui redit son tableau, et sa
période paraissait donc juste.

| Texte, article | Version jamais en vigueur, ses dates au LEGI | Ce que le dépôt en faisait | La version en vigueur à cette date |
|---|---|---|---|
| n° 99-669, art. 17 | LEGIARTI000034810141, du 1er janvier 2021 au 1er juin 2020 | 19 lignes | LEGIARTI000041916038, du 1er janvier 2021 au 1er janvier 2026, lue (25 lignes) : « Directeur technique de classe exceptionnelle Echelon spécial - 5e échelon - 4e échelon 3 ans 3e échelon 2 ans 6 mois 2e échelon 2 ans 1er échelon 2 ans », classe que la version jamais en vigueur n'écrit pas |
| n° 83-1260, art. 34 | LEGIARTI000027940471, du 8 janvier 1984 au 4 août 1980 | 15 lignes | aucune au LEGI avant le 4 août 1990 (LEGIARTI000027940483, lue) : voir la question plus bas |
| n° 91-868, art. 7 | LEGIARTI000035606585, du 1er janvier 2021 au 19 novembre 2018 | 36 lignes | LEGIARTI000037623417, du 1er janvier 2021 au 1er février 2024, lue (36 lignes) |
| n° 91-290, art. 14-4 | LEGIARTI000025845550, du 1er septembre 2014 au 30 août 2012 | 11 lignes | aucune : c'est la seule version de l'article |
| n° 2014-923, art. 25 | LEGIARTI000032578591, du 1er janvier 2017 au même jour | 4 lignes | LEGIARTI000037468710, depuis le 1er janvier 2017, lue : « 4e échelon provisoire 2 ans 3e échelon provisoire 2 ans 2e échelon provisoire 2 ans 1er échelon provisoire 2 ans » |
| n° 2014-1455, art. 22 | LEGIARTI000052465286, du 15 décembre 2025 au même jour | 93 lignes | LEGIARTI000053027219, depuis le 15 décembre 2025, lue (93 lignes) : « Général de brigade Echelle de solde n° 3 4 e échelon 3 e échelon 1 an 2 e échelon 1 an 1 er échelon 1 an » |
| n° 92-851, art. 14 | LEGIARTI000034434459, du 1er janvier 2017 au même jour | première version d'une période réunie à LEGIARTI000037468701 (21 lignes) | LEGIARTI000037468701, depuis le 1er janvier 2017 : la période porte désormais son nom ; « Médecin hors classe Echelon spécial - 5e échelon - 4e échelon 3 ans » |

*La correction.* Une version jamais en vigueur n'est plus ni lue ni réunie à la suivante ;
`non_lus.csv` la consigne, tableau par tableau, avec le motif « version jamais en vigueur :
le LEGI la date d'une fin antérieure ou égale à son début » (fonction `jamais_en_vigueur`).
Dix lignes de `non_lus.csv` portent ce motif : les sept, plus trois versions déjà refusées
pour une autre raison (n° 98-343, art. 39, un tableau en fiches ; n° 93-569, art. 12 ;
n° 2010-1239, art. 24), dont le motif devient celui-ci. Tests :
`test_une_version_jamais_en_vigueur_se_reconnait_a_ses_dates`, `…_n_est_pas_lue`,
`test_la_version_en_vigueur_a_ces_dates_est_lue`.

*Ce que le texte ne tranche pas.* Le n° 83-1260 : la fin « 4 août 1980 » précède le texte
lui-même (décret du 30 décembre 1983), et la version suivante commence le 4 août 1990 ; une
coquille pour 1990 est possible, mais l'index ne le dit pas, et le dépôt n'invente pas une
date. Le tableau reste hors des lignes, consigné.

## 2. Le tableau arrêté au paragraphe qui le suit (faible)

N° 72-583, art. 6, en vigueur depuis le 29 octobre 2021 (LEGIARTI000044268513) : « I.-La
durée du temps passé dans chacun des échelons du corps des adjoints d'enseignement est fixée,
sous réserve des dispositions du II, ainsi qu'il suit : ÉCHELON DURÉE 11e échelon - 10e
échelon 4 ans 6 mois 9e échelon 3 ans 6 mois 8e échelon 3 ans 6 mois 7e échelon 3 ans 6e
échelon 3 ans 5e échelon 3 ans 4e échelon 2 ans 3e échelon 1 an 2e échelon 1 an 1er échelon
1 an II.-Les anciennetés détenues dans les 6e et 8e échelons de la classe normale peuvent être
bonifiées de 9 mois. » Le « II.- » devenait un grade, et ses 6e et 8e échelons, des lignes :
d'où « un échelon manque ». N° 72-580, art. 13 (LEGIARTI000044268441) : « … 2e échelon 1 an
1er échelon 1 an Le ministre prononce les promotions des professeurs agrégés. II.-Les
anciennetés détenues dans les 6e et 8e échelons … ».

*La correction.* Un paragraphe numéroté (« II.- », « II. bis - »), au début d'un libellé ou
après un point, arrête le tableau, même s'il nomme des échelons (`PARAGRAPHE`), sans passer
par le refus « une phrase coupe le tableau ». Test :
`test_le_tableau_s_arrete_au_paragraphe_qui_le_suit` (adjoints : 54, 42, 42, 36, 36, 36,
24, 12, 12, 12 du 10e au 1er ; agrégés, trois grades, 18 lignes).

*Les autres refus « un échelon manque ».* Des 22, **21 rentrent** : n° 72-583, art. 6
(4 versions), n° 72-580, art. 13 (4), n° 90-680, art. 24 (7), n° 93-752, art. 17 (3),
n° 65-383, art. 10-7 (2), n° 96-1113, art. 14 (version du 1er septembre 2017,
LEGIARTI000042571613). Le 22e reste refusé, **à raison** : la version du 1er janvier 2021 du
même article (LEGIARTI000042571828), telle que la consolidation du LEGI l'écrit, saute le
5e échelon, que le décret publié au JORF écrit (n° 2020-1435, art. 8 : « 5e échelon 3 ans » ;
raison corrigée le 3 novembre 2026, note des retouches de R-B2-bis), « Professeur technique hors classe
7e échelon - 6e échelon 3 ans 4e échelon 2 ans 6 mois ». Rentrent aussi 7 refus « une phrase
coupe le tableau » au même paragraphe : n° 90-90, art. 18 (4 versions), n° 92-778,
art. 31-6 et 32 (3). En tout 14 tableaux, 268 lignes. *Contre-lecture* : pour chacune de leurs
28 versions, la suite (échelon, durée) relue dans le texte jusqu'au « II » par une autre
expression, et comparée aux lignes : toutes égales.

## 3. Le septième écart au Noyau RH (faible)

N° 2021-1550, art. 9, du 1er janvier 2022 au 1er janvier 2023 (LEGIARTI000044396371) :
« Administrateur général 6e échelon - 5e échelon 4 ans 4e échelon 3 ans 3e échelon 3 ans
2e échelon 3 ans 1er échelon 3 ans ». Au Noyau RH (`grades.csv`, `echelons.csv`), deux grades
portent ce libellé : 02979, « Administrateur général », du corps 00514 « Administrateurs
civils », du 13 février 2012 au 31 décembre 2021, grille 02929, qui cite le texte 7257
(n° 2021-1550) comme « abrogateur » ; et 05041, « Administrateur général de l'Etat », du
corps 01275 « Administrateurs de l'Etat », du 1er janvier 2022 au 1er janvier 2023,
grille 03742, texte 7257 « origine ». Le lien de B2 (le texte du grade et son libellé) a
pris le premier, où le rang 5 vaut 0. Au second, la grille 03742 donne, du 1er janvier 2022
au 1er janvier 2023, 36 mois aux rangs 1 à 4 et **48 au rang 5**, comme le texte.

*La correction.* Le test `test_les_administrateurs_generaux_recoupes_au_noyau_rh_a_leur_grade`
refait la comparaison au grade 05041 : les cinq durées sont égales. Le décompte de B2
devient : **six** écarts, tous des zéros du noyau (médecins inspecteurs de santé publique,
deux ; techniciens supérieurs de l'aviation civile, quatre) ; à ce grade, cinq valeurs
égales. Le total des égalités de B2 (2 563) ne se recompte pas : son script n'est pas au
dépôt. La note de B2, un récit, n'est pas récrite ; elle se lit avec celle-ci.

## 4. Un tableau en fiches compté une fois (faible)

N° 98-343, art. 39, du 1er août 2000 au 30 décembre 2006 (LEGIARTI000006506811) : « …
sont fixées ainsi qu'il suit : ÉCHELON : 5e échelon DURÉE Moyenne : 4 ans DURÉE Minimale :
3 ans ÉCHELON : 4e échelon … » ; n° 67-715, art. 13 (LEGIARTI000006508433) : « GRADE :
Ingénieur général, 1er et 2e échelon DUREE moyenne : 3 ans. DUREE minimum : 2 ans 3 mois. ».
Chaque « DURÉE Moyenne : » ouvrait un tableau : cinq, puis six, pour un seul.

*La correction.* Les deux points d'un champ de fiche (« … échelon DURÉE Moyenne : »,
`CHAMP_DE_FICHE`) n'ouvrent plus de tableau, et un tableau qui écrit au moins deux tels
champs se refuse sous son vrai motif, « un tableau écrit en fiches, un champ par case »
(`FICHES`). **409** lignes de `non_lus.csv` s'en vont (39 versions d'article). En contrôlant
le passage, trois versions disparaissaient de `non_lus.csv` : leurs fiches ne s'ouvrent par
aucune phrase à deux points (n° 89-750, art. 13, LEGIARTI000006457590 : « … sont fixées selon
les modalités ci-après. - CLASSES ET ECHELONS … 3e échelon DUREE moyenne : 3 ans DUREE
minimale : 2 ans 6 mois »). Un article sans tableau qui écrit au moins deux champs de fiche
se consigne donc aussi : elles reviennent, et **25** versions que rien ne consignait jusqu'ici
le sont (n° 69-222, art. 21-3 et 35-3 ; 77-906, art. 42-3 ; 90-360, art. 17 ; 90-852, art. 17 ;
98-1262, art. 38 et 54 ; 97-511, art. 17… ; dix-huit textes, dont sept qui n'avaient rien au
dépôt). 97 tableaux en fiches, à relire à la main. Tests : `test_un_tableau_en_fiches_est_un_seul_tableau_et_se_refuse`,
`test_un_tableau_en_fiches_n_est_compte_qu_une_fois`.

## 5. Les trois chevauchements (faible)

Deux versions du même article en vigueur ensemble, aux dates du LEGI. Le dépôt garde ces
dates ; la colonne `chevauche` de `tableaux.csv` nomme, pour chaque tableau, celui de
l'autre version (sa première), pour que le rattachement aux grilles sache choisir. Test :
`test_les_periodes_qui_se_chevauchent_sont_marquees` (trois paires, et aucune autre).

- **N° 91-868, art. 7.** LEGIARTI000033602862, du 1er janvier au 23 septembre 2017 (« L'ancienneté
  moyenne pour accéder à l'échelon supérieur … ANCIENNETÉ MOYENNE », réunie à la version
  de 2007, LEGIARTI000006711235, qui redit son tableau), et LEGIARTI000035742510, depuis le
  1er janvier 2017 (« La durée du temps passé dans chacun des échelons des différents grades
  est ainsi fixée : … DUREES »). *Ce que le texte tranche* : le décret n° 2017-1374 du
  20 septembre 2017, publié au JORF du 22 septembre 2017 (JORFTEXT000035600463), écrit en
  son article 9 « L'article 7 est remplacé par les dispositions suivantes : « Art. 7.-La
  durée du… » », et sa notice : « Entrée en vigueur : les articles 3 et 8 à 12, à l'exception
  du II de l'article 6-3 du décret n° 91-868 du 5 septembre 1991 dans sa rédaction issue de
  l'article 8 du présent décret, entrent en vigueur le 1er janvier 2017. » La notice n'est
  pas la règle : l'article du décret qui fixe cette date n'est pas dans l'index, et n'est
  pas lu. Si la notice dit vrai, la version de 2017 s'applique depuis le 1er janvier 2017.
- **N° 96-366, art. 5.** LEGIARTI000006482187, du 1er août 1995 au 24 juin 1998, et
  LEGIARTI000006482188, depuis le 24 juin 1996. Les deux écrivent « Il est créé au 1er août
  1995 un grade provisoire de chef chiffreur » et le même tableau ; la seconde n'en diffère
  que par l'écriture (« 6e » devenu « 6 e », « DURÉE » « DUREE ») et une phrase ajoutée sur
  la situation au 1er août 1995 (`--diff`). *Ce que le texte tranche* : rien n'est à choisir
  pour les durées, identiques dans les deux versions.
- **N° 92-847, art. 14.** LEGIARTI000006374721, du 30 août 1992 au 8 février 1996 (11 échelons),
  et LEGIARTI000006374722, depuis le 1er août 1995 (13 échelons : « {+12e échelon 3 ans 2 mois
  3 ans 11e échelon 3 ans 2 mois 3 ans+} »). Le décret modificatif est le n° 96-101 du
  6 février 1996 (JORF du 8 février 1996, JORFTEXT000000191345), qui vise le n° 92-847 ; son
  résumé au JORF dit « des modifications statutaires interviennent également au bénéfice …
  des moniteurs-éducateurs dont la grille indiciaire est revalorisée », sans date pour eux, et
  son article 38, que le LEGI date du 1er août 1995 (LEGIARTI000006377880), reclasse les
  moniteurs-éducateurs « d'échelon à échelon ». *Ce que le texte tranche* : rien de lu ne
  fixe la date d'effet de l'article 14 nouveau ; l'article d'entrée en vigueur du n° 96-101
  n'est pas dans l'index. La date du LEGI, le 1er août 1995, reste la seule.

## 6. L'emploi nommé avant l'en-tête (faible)

N° 2016-2003, art. 13, en vigueur depuis le 17 avril 2022 (LEGIARTI000045657613) : « … en
application du tableau suivant : Directeur départemental des services d'incendie et de
secours de catégorie A : ÉCHELONS DURÉE 7e échelon - 6e échelon 3 ans … 1er échelon 1 an
6 mois Directeur départemental des services d'incendie et de secours de catégorie B :
ÉCHELONS DURÉE … ». Les six tableaux avaient un `groupe` vide.

*La correction.* Le grade écrit devant l'en-tête (« … de catégorie A : ÉCHELONS DURÉE »), ou à
la fin de la phrase d'annonce quand elle est la queue du tableau précédent (« … 1 an 6 mois
Directeur … de catégorie B : »), devient le groupe ; l'en-tête est « ÉCHELONS DURÉE ».
Conséquence fidèle au texte : la version du 17 avril 2022, qui renomme les emplois (« du
service » devenu « des services »), fait désormais sa propre période ; six tableaux et
45 lignes de plus. Aucun autre tableau lu ne change. Test :
`test_l_emploi_nomme_avant_l_en_tete_est_le_groupe`.

## 7. La règle du quart (faible)

N° 2014-99, art. 10, du 7 février 2014 au 22 mai 2016 (LEGIARTI000028566814), son II : « La
durée maximale du temps passé dans chaque échelon est égale à la durée moyenne majorée du
quart. La durée minimale du temps passé dans chaque échelon est égale à la durée moyenne
réduite du quart. Cette durée ne peut être inférieure à un an. »

*La correction.* La colonne `regle_du_quart` de `tableaux.csv` cite, mot pour mot, la règle
que l'article du tableau écrit, depuis « La durée maxim… » jusqu'à « … réduite (ou minorée)
du quart. », avec « Cette durée ne peut être inférieure à un an. » quand elle suit ; aucune
durée maximale ou minimale n'en est déduite. La règle entre dans ce qui réunit deux
versions : aucune période n'en est coupée. Tests : `test_la_regle_du_quart_se_cite_mot_pour_mot`,
`test_la_regle_du_quart_est_consignee_avec_la_moyenne`.

*Les 36 tableaux de moyenne seule, d'après leur texte.* **Dix** écrivent la règle dans leur
propre article, tous de l'hospitalière : n° 2001-1207, art. 12 (« … majorée du quart. … réduite
du quart. », sans le plancher d'un an) ; n° 2010-1139, art. 19 ; n° 2011-661, art. 24 (deux
versions) ; n° 2012-1466, art. 16 ; n° 2014-99, art. 10 ; n° 2014-100, art. 11 ; n° 2014-101,
art. 11 ; n° 2014-1585, art. 19 ; n° 2015-1048, art. 14 (« minorée du quart »). Les **26**
autres n'écrivent la règle ni dans leur article ni dans aucun autre article de leur texte que
l'index garde : n° 95-1272 (art. 52, 59, 70, 76), 2001-1375 (art. 19), 2003-770 (art. 13),
65-184 (art. 16, 17), 68-270 (art. 21), 91-868 (art. 7), 91-936 (art. 6), 91-45 (art. 6),
93-145 (art. 6, quatre versions), 2009-1388 (art. 24, deux), 2012-762 (art. 14, trois),
2013-1146 (art. 9), 2014-847 (art. 20), 2015-303 (art. 18), 2015-576 (art. 14), 2016-1195
(art. 17). Le texte ne dit pas, pour eux, ce que sont les durées maximale et minimale. Des
27 articles de l'index qui écrivent « majorée du quart » et « réduite du quart » (28 avec
« minorée »), les 18 autres ne sont pas des tableaux lus : 8 sont consignés non lus
(n° 2000-232, 2001-1343, 2005-921 : en phrases ; 88-163, deux versions, 94-948 : un libellé
qui porte une durée ; 96-113, art. 40 : en caractères ; 2001-1207, art. 14 : une case de
trop), 10 n'ont pas de tableau de durées que le lecteur trouve (n° 60-805, deux versions ;
64-942 ; 69-662, deux ; 72-361 ; 80-253 ; 96-113, art. 22 ; 2011-746 ; 2011-748), à relire.

## 8. Trouvé en contre-lisant, et corrigé

- **La case « Spécial ».** N° 90-680, art. 24, du 1er septembre 2017 au 1er janvier 2021
  (LEGIARTI000034947965) : « Professeur des écoles de classe exceptionnelle Spécial ― 4e
  échelon ― 3e échelon 2 ans 6 mois » ; n° 87-1099, art. 17 (LEGIARTI000033677396) : « Attaché
  hors classe Spécial 6e échelon - 5e échelon 3 ans ». La case de l'échelon spécial restait au
  bout du libellé du grade (« Attaché hors classe Spécial »), et l'échelon spécial manquait :
  28 tableaux certifiés. Elle devient une ligne `special`, sans durée, au rang au-dessus du
  plus haut échelon (`SPECIAL`, `_special`) ; aucune durée ne change. Test :
  `test_la_case_special_est_l_echelon_special`, `test_aucun_libelle_ne_garde_la_case_d_un_echelon`.
- **« Avant le 1er échelon de … ».** N° 2014-923, art. 25 (LEGIARTI000037468710) : « ÉCHELONS
  PROVISOIRES dans le grade de puéricultrice DURÉE Avant le 1er échelon de la classe
  supérieure 4e échelon provisoire 2 ans … » : le « 1er échelon » du libellé faisait une
  fausse ligne, sans durée, sous le groupe « Avant le » (4 tableaux : n° 2014-923, trois
  versions ; n° 2016-336, art. 25, LEGIARTI000032578363). Un échelon nommé après « avant le »
  ou « après le » reste du libellé (`NOMME_UN_ECHELON`). Le même défaut faisait refuser
  LEGIARTI000032276890 (n° 2016-336, art. 25, du 1er avril au 15 mai 2016), « l'en-tête change
  d'ordre » : il se lit, « DURÉE MAXIMALE DURÉE MINIMALE 2e échelon provisoire 2 ans 1 an
  10 mois 1er échelon provisoire 1 an 1 an », soit 24 et 22, 12 et 12. Test :
  `test_avant_le_1er_echelon_n_est_pas_une_ligne`.

## Ce qui reste, et ce qui n'a pas été vérifié

- « Echelon fonctionnel » (12 lignes, deux tableaux de l'inspection du travail, n° 2000-747
  et n° 2003-770) reste dans le libellé du grade, comme B2 l'a dit : c'est la même
  forme que « Spécial », pour un échelon que le lecteur ne nomme pas encore. À corriger avec
  le chaînage.
- Les 97 tableaux en fiches, les 115 dessinés en caractères, et les 10 articles qui écrivent la
  règle du quart sans tableau trouvé : à relire.
- Le n° 83-1260, art. 34 (question ci-dessous).
- La phrase d'annonce (`intro`) des tableaux 2 à 6 du n° 2016-2003 reste la queue du tableau
  précédent : elle n'est pas une phrase du texte, et n'est pas corrigée ici.

*Le site.* Les durées ne servent pas au calcul des pensions. La construction du paquet
(`construire_donnees.py`) ne change que la trace de certification des cinq séries
`durees_echelon_*` dans `moteur/donnees.json` ; sur le site, seule la page des sources en
montre les comptes (valeurs recontrôlées, série par série), qui suivent ceux-ci. Aucun
autre chiffre ne bouge.

*Question au propriétaire.* N° 83-1260, art. 34 : faut-il lire au JORF du 8 janvier 1984 la
rédaction d'origine, et dater la version LEGIARTI000027940471 du 8 janvier 1984 au
4 août 1990, ce que le LEGI ne dit pas ? Jusque-là, ses 15 lignes restent hors des données.
