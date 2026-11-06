# Relecture de E15 : les écarts de R-E15, et `cotisation_par_classes_liberales` lue au droit

File R-E16, le 6 novembre 2026 (action 130, vague 11, sur Opus) : relecture indépendante,
contre les sources, du commit 0909a3a de la session E15 (note
`2026-11-06-e15-cotisation-par-classes-liberales.md`). Ni règle, ni donnée, ni test n'est
modifié ; les écarts repartent à E16.

**Méthode.** Index de la DILA récupérés ce jour (`dila_index.py --recuperer`) : JORF à jour
du 3 novembre 2026, LEGI du 2 novembre. Requêtes SQL directes sur la table `doc`, sans
borne : dans LEGI, toutes les rédactions des articles 1, 2, 2 bis, 2-1 et 3 des décrets
n° 50-1318, 53-506 et 79-262 ; au JORF, tous les arrêtés de statuts des trois sections
depuis 2005 au titre, ceux de la CAVEC de 1948 au 1er mars 2008 au titre puis au texte
(FTS), les décrets dont le titre nomme l'un des trois décrets, ou « décret du 21 mai
1953 ». Chaque citation de la fiche comparée par script au texte de l'index (espaces
normalisés, coupée aux « […] »). Les moteurs : `servi_et_refait` (portage et Python), et
`ClassesCotisation` pour les grilles et l'année de revenu, sous les deux jeux.

## 1. Les écarts de R-E15 (`surcote_par_age_seul`, version `avant_2007`)

**(a) Les arrêtés de la CAVEC.** Conforme pour les six de 1980 à 2003 : 17 juin 1980
(JORFTEXT000000680010, « ART. 52,55,57,58 ET 61 AU REGIME D'ASSURANCE VIEILLESSE
COMPLEMENTAIRE », « CES ARRETES SERONT PUBLIES AU BULLETIN OFFICIEL DU MINISTERE DE LA SANTE
ET DE LA SECURITE SOCIALE ») ; 22 août 1986 (JORFTEXT000000862986, « (ART. 47 ET 55 ANNEXE
2) ») ; 9 mars 1987 (JORFTEXT000000321565, « 4EME PARTIE,TITRES XVI (ART. 52) ET XVII (ART.
57 ET 58) ») ; 23 juillet 1992 (JORFTEXT000000724876, « (art. 49 et 50) ») ; 27 février
2003 (JORFARTI000001710064, « du régime complémentaire d'assurance vieillesse (art. 58) »,
« Bulletin officiel n° 2003-14 »). La recherche au texte n'en trouve pas d'autre au
complémentaire : les autres arrêtés de la période portent sur l'allocation vieillesse
(base : 14 janvier 1980, 15 avril et 12 juillet 1983, 1er décembre 1986, 29 septembre
1993, 7 août 2001, 17 septembre 2002) ou l'invalidité-décès (6 décembre 1988, 26 mars 1998, 18 juillet 2006) ;
aucun au complémentaire du 28 février 2003 au 21 février 2008. Les dix de 1961 à 1977 :
conformes, titre pour titre (8 novembre 1961, « A L'ART. 57 » ; 7 novembre 1962 ; 3 février
1964, « AUX ART. 44 A 47,49,56,57 A 59 ET 61 » ; 22 juin 1964, « UN ART. 62 » ; 21 avril
1966, « A L'ART. 61 […] ET DE LA SUPPRESSION DE L'ART. 58 » ; 12 décembre 1967 ; 23 décembre
1970, « DE L'ART. 60 » ; 26 février 1974 ; 10 juin 1976 ; 25 mars 1977,
JORFTEXT000000312784).

- **Écart 1, mineur.** « 13 mai 1994 (JORFTEXT000000731984, son titre seul) » : l'index en
  porte aussi la mention, JORFARTI000001005266 : « sont approuvées les modifications
  apportées aux statuts du régime d'assurance vieillesse complémentaire de la caisse
  d'allocation vieillesse des experts-comptables, des comptables agréés et des commissaires
  aux comptes (art. 49 et 59) », et JORFARTI000001391556 : « L'arrêté du 13 mai 1994 sera
  publié intégralement au Bulletin officiel du ministère no 94-17 ». C'est l'écart que E15
  a corrigé pour 1992, resté pour 1994. Aucun effet servi.
- **Écart 2, mineur.** Avant 1961, l'arrêté du 14 septembre 1957 (JORFTEXT000000477655,
  « APPROBATION DES MODIFICATIONS APPORTEES A L'ART. 31 DU REGLEMENT D'ASSURANCE VIEILLESSE
  COMPLEMENTAIRE DES EXPERTS COMPTABLES ET COMPTABLES AGREES », titre seul) n'est pas nommé :
  onze, de 1957 à 1977, et non dix de 1961 à 1977. Aucun effet servi.

**(b) « un article 3.14 qui existait donc ».** Conforme : JORFARTI000018197775 approuve
« 3.1, 3.3, 3.4, 3.5, […] 3.20 », sans 3.2 ; JORFARTI000018197778 : « Article 3.14
Liquidation différée de la pension de retraite complémentaire L'article 3.14 est ainsi
rédigé » (dix-neuf articles 3.x « ainsi rédigés », de 3.1 à 3.20). La récriture s'en tient
aux indices.

**(c) Les statuts de la CAVP d'avant 2009.** Conforme : arrêté du 11 mai 2009, article 2
(JORFARTI000020694602), mot pour mot. Aucun des deux arrêtés n'est dans l'index du JORF
(recherche aux dates de 1948 à 1950 : seuls le décret n° 49-580 et l'arrêté du 14 décembre
1949 sur la cotisation) : « au fac-similé ou au seul Bulletin officiel » se tient.

## 2. `cotisation_par_classes_liberales`, lue au droit

**Les rédactions de l'article 2.** Conforme : LEGI en porte onze à la CARPV (du 24 octobre
1950 au 1er juillet 2026), six à la CAVEC (1er janvier 1980, 13 mars 1987, 28 janvier 2008,
30 décembre 2012, 14 novembre 2025, 1er juillet 2026), six à la Cipav (1er janvier 1979,
21 juin 1985, 30 décembre 2012, 1er janvier 2013, 1er janvier 2023, 1er juillet 2026), aux
dates de la fiche. Les 62 entrées `textes` des quinze versions sont dans l'index ; leurs
28 citations s'y retrouvent toutes, mot pour mot. Les dates d'entrée en vigueur des statuts
(CAVEC 2 mars 2008, 24 février et 15 avril 2012, 5 septembre 2018 ; CARPV 18 mai 2014,
2 décembre 2015, 1er janvier 2022 ; Cipav 1er janvier 2016, 31 mars 2021) : conformes, aucun
article de ces arrêtés ne fixant de date hors des deux qui le disent (« Le présent arrêté
entre en vigueur le 1er janvier 2016. », JORFARTI000031680316 ; « entrent en vigueur le
1er janvier 2022 », article 2 de l'arrêté du 18 octobre 2021) ; les autres valent le
lendemain de leur publication. Relus aussi : décret n° 98-599, article 4
(« Classe 1 : 3 406 F », à la section des architectes) ; décret n° 2025-1076, article 12
(« cotisation forfaitaire de la classe A : 782 euros ») ; décret n° 2015-1802, article 1er
(vétérinaires, « Taux d'appel de la cotisation : 104 % » ; experts-comptables, « Classe A :
600 euros ») ; décret n° 2024-1214, article 6 (« classe A : 760 euros »).

**Les textes manqués.** Des arrêtés de statuts ou de règlements des trois sections que
l'index titre depuis 2005, invalidité-décès compris, la fiche en cite neuf. Les autres
relus, ceux qui touchent aux classes :

- **Écart 3, mineur.** CAVEC, arrêté du 2 juillet 2024 (JORFARTI000049880543, II, 1°) :
  « Aux deuxième, quatrième et dixième alinéas, les mots : « l'exercice précédent » sont
  remplacés par les mots : « l'année précédente » » ; au septième, « le précédent
  exercice » de même ; l'option, « Le paiement de l'intégralité de la cotisation rend cette
  option définitive » ; « a la possibilité de maintenir » devient « indique s'il
  maintient ». Arrêté du 19 juin 2019 (JORFARTI000038689131, II, 2° et 3°) : des intitulés,
  et « non agricole de l'exercice précédent » au dernier alinéa de l'article 2 (les
  tranches). Ni l'un ni l'autre n'est cité (`cavec_de_2019`, `sans_la_cipav_2023`). Aucun
  effet : le modèle prend déjà l'année précédente.
- **Écart 4, mineur.** CARPV, arrêté du 11 janvier 2011 (JORFARTI000023448554), titre II,
  article 4 : « Dans la première colonne de chacun des deux tableaux, après le mot :
  « revenu », sont ajoutés les mots : « ou rémunération (définis ci-dessus) » » ; arrêté
  du 27 février 2006 (JORFARTI000002071126, « art. 4, 6, 7, 8, 8 bis, 10, 11, 13, 14, 22,
  27, 28, 29, 30 et 31 du titre II », « publié intégralement au Bulletin officiel »). Non
  cités ; l'approximation qui date de 2012 la rémunération du vétérinaire des 11°, 12° et
  23° de L. 311-3 (fiche, `approximations`) l'a dans les statuts depuis 2011. Les statuts
  de la CARPV d'avant 2014, que la fiche dit au seul Bulletin officiel, manquent à la liste
  du bloc « Reprise » et de « Pour la suite ». Aucun effet servi (statut non posé).
- **Écart 5, mineur.** Cipav : l'arrêté du 3 octobre 2006 (JORFARTI000002050100, la
  « troisième partie « Régime de retraite complémentaire » », au Bulletin officiel, l'arrêté
  du 21 mars 1979 « abrogé à compter du 1er janvier 2007 ») n'est pas nommé par la fiche,
  qui ne parle que des statuts « d'avant 2016 » ; l'arrêté du 16 décembre 2021
  (JORFARTI000044554134, 15° et 16°, en vigueur le 1er janvier 2022) corrige l'article 3.3
  (« invalidité-décès » devient « vieillesse complémentaire ») et titre l'article 3.4
  « Cotisations de début d'activité ». Aucun effet servi.
- **Écart 6, mineur.** Décret n° 79-262, article 2-1 (LEGIARTI000006767475, 2000 à 2023) :
  « A titre transitoire et pour les exercices 2000 à 2006 inclus, la cotisation mentionnée
  à l'article 2 est majorée de 33 % pour les personnes qui ont été affiliées à la Caisse
  autonome de retraite des géomètres experts et des experts agricoles et fonciers
  antérieurement au 1er janvier 2000. » Ni cité ni déclaré parmi les statuts que le
  simulateur ne pose pas. Effet non mesuré (le texte ne dit pas si la majoration donne des
  points).
- **Écart 7, mineur.** « les quinze décrets qui modifient l'article 2 de 1955 à 1974 »
  (version `avant_1979`, et `sources`, depuis 0036c11) : l'index en titre quatorze de 1955 à
  1974 (n° 55-188, 60-1123, 61-1214, 62-1257, 63-1170, 64-93, 66-867, 67-866, 68-342,
  70-270, 71-182, 72-206, 73-488, 74-199) ; le quinzième est le décret n° 77-313 du 25 mars
  1977 (JORFTEXT000000515110, « MODIFICATION D'ART. 2 (AL. 1) DU DECRET DU 21-05-1953 »,
  titre seul), qui n'est pas nommé. Aucun effet servi.

Relus sans écart : l'article 2 bis du décret n° 50-1318 (classes facultatives B, C, D de
1974, B et C de 1982 et 1993, en sus de la classe A ; exonérations depuis 1997), que les
« cotisations facultatives » et la « classe supérieure » des options déclarées couvrent sans
les citer ; l'article 2-1 du décret n° 53-506 (conjoint collaborateur, 2007), hors des
classes ; la CAVEC 2010, 2013 (l'indemnité journalière, partie 4), 2014, juillet et
décembre 2025, 10 juillet 2026, la CARPV février 2015, 2017 (trois), décembre 2025 (les
points de l'invalidité-décès), 10 juillet 2026, la Cipav 2007, 2012, 2014, 2016, 2017,
2020, 2023 (deux), 2025 : rien sur les classes du complémentaire,
l'année de revenu ou la classe de début. Les arrêtés de la CARPV du 28 août et du
9 octobre 2006, et de la Cipav du 28 décembre 2004, du 18 mars et du 26 mai 2005, n'ont au
JORF qu'une mention (articles 21, 23 et 24 du titre II ; 3 et 3 bis du titre Ier ;
article 7 ; statuts généraux) et renvoient au Bulletin officiel.
Candidat hors de la fiche : l'article 3.12 des statuts de la Cipav (arrêté du 3 décembre
2010, JORFARTI000023217549), les points du micro-entrepreneur « proportionnel[s] aux
cotisations effectivement réglées », qu'aucune fiche ne cite.

**Les versions `supposee`.** Conforme. Les statuts manquent bien à l'index : la Cipav de
1979 (aucun arrêté de 1979), de 2006 (Bulletin officiel, ci-dessus) ; la CAVEC d'avant 2008
(titres et mentions seuls) ; la CARPV, l'acte vétérinaire que rien ne publie. Les six `lue`
reposent sur des textes lus.

**Les 31 textes à rattacher.** Écart 8, mineur (dans la note, un récit) : la liste ôtée en
avait 29, et non 31 (les vingt et une rédactions de LEGI, le décret de 1953, sept arrêtés) ;
toutes sont citées par les versions (les arrêtés, par leur article : JORFARTI000018197778,
025395367, 037363871, 028939421, 044220745, 031680320, 043302736), aux dates de l'index.
Rien n'est perdu.

**Ce que les moteurs servent.** Conforme. Les grilles de `ClassesCotisation`, rapport au
premier montant : Cipav 1, 2, 3 en 1979, puis 5 en 1980, 7 en 1981, 10 en 1982, huit
classes de 1 à 13 de 2013 à 2022 ; CAVEC 1 ; 1,25 ; 1,75 ; 2,5 ; 3 ; 3,75 de 1980 (48 à 180
points), 4,5 en sus de 1987 (216), 1 à 31,25 de 2008 (48 à 1 500), neuf en 2026 ; CARPV
1 ; 1,25 ; 1,5 jusqu'en 2025, 17/21/25/28 en 2026. L'année de revenu et la classe de début,
essayées à chaque début d'activité de 2005 à 2022 : celles que la fiche dit (CAVEC N − 2
de 2008 à 2018, N − 1 depuis, A deux ans de 2012 à 2018, un an depuis ; CARPV N − 2 de 1998
à 2021, N − 1 depuis, B deux ans de 2014 à 2021, un an depuis ; Cipav N − 1 et A deux ans
de 2016 à 2020, l'année même depuis). `servi_et_refait`, 21 cas (trois sections, débuts de
1980 à 2022) : le portage sert, le Python refait au bit près, sous les deux jeux.

**Le point non tranché du cumul à la CAVEC.** Le texte : conforme. Décret n° 53-506,
article 2, onzième alinéa (« En cas de cumul de l'activité libérale et salariée, les
cotisations afférentes au présent régime sont appelées dans les conditions prévues à
l'alinéa précédent, sans pouvoir être inférieures à la cotisation en classe C. »), en
vigueur le 1er janvier 2013 (note (1), décret n° 2012-1485, article 20), dans ses trois
rédactions (LEGIARTI000026885098, 052567925, 054168240) ; statuts de 2018, partie 2,
article 3, 5 : mot pour mot. La lecture contraire est tenable : point non tranché, à bon
droit. Deux pièces de plus, qui ne le tranchent pas :
- pour la lecture B, les statuts de 2008 (JORFARTI000018197778, article 3.7) distinguent
  « les experts-comptables salariés n'exerçant pas d'activités libérales » : le cumul d'un
  exercice salarié et libéral de la profession est prévu, ce qui rend plausible que le
  décret vise ce cumul-là ;
- contre l'argument des statuts de la lecture B : ceux de 2012, en vigueur de 2013 à 2018
  (JORFARTI000025395367 et 025687514), ne disent rien du cumul (« cumul » n'y désigne que
  le cumul emploi-retraite) ; l'option de la classe C n'existe qu'aux statuts de 2018.

Les montants, refaits par le même cas (`Simulateur.carriere_parcours`, née en mars 1960,
salariée du privé non cadre dès 22 ans au niveau 1, expert-comptable en cumul de 55 ans à
la liquidation à 65 ans au niveau 0,1) et par le pont (même requête) : 621,5875 € servis
par les deux moteurs (« cotisations revalorisées 7,462 € × rendement 8.33% ») ; chaque
année en classe A (2024 : revenu de 2023, 5 353,54 € ; 760 € ; borne du modèle, 16 190 €).
- Lecture A, toute la carrière : le moteur, la classe C imposée de 2013 à 2025, sert
  3 677,7260 € (« 44,150 € ») ; 3 677,7260 − 621,5875 = **3 056,14 €** ; à la main,
  (44 150 − 7 462) × 0,0833 = 36 688 × 0,0833 = 3 056,11 € (cotisations arrondies à
  l'euro). Conforme.
- Lecture A, 2024 seule : 284 × 760 / 48 = 4 496,67 ; 4 496,67 − 760 = 3 736,67 ;
  × 0,0833 = **311,26 €** avant revalorisation : conforme ; revalorisée à la liquidation,
  le moteur sert 935,79 €, soit 314,20 € de plus.
- Précision, à ajouter : la lecture A, sans les deux années de classe A d'office (2015 et
  2016) : 3 128,91 € servis (« 37,562 € »), **2 507,32 €** de plus ; à la main,
  (37 562 − 7 462) × 0,0833 = 30 100 × 0,0833 = 2 507,33 €. La lecture A va donc de
  2 507,32 à 3 056,14 € au cas posé.
- Précision, une troisième lecture : le minimum du décret tant que les statuts se taisent
  (2013 à 2018), l'option des statuts depuis 2019 : 1 773,26 € servis (« 21,288 € »),
  **1 151,68 €** de plus ; à la main, (21 288 − 7 462) × 0,0833 = 13 826 × 0,0833 =
  1 151,71 €.
- Lecture B : 0 €. Sous `PRESOMPTIONS_DECALEES=1`, le pont sert 616,16 € au même cas ; la
  lecture A, à la même proportion (236 / 48), 616,16 × 4,9167 = 3 029,45 €.

**La classe 3 de la CAVP et la classe des notaires.** Conforme : décret n° 2026-418,
article 4 (JORFARTI000054153444) : « La cotisation est appelée en classe 3 pendant les deux
premières années de son affiliation » ; article 2 (JORFARTI000054153399), article 2-3 du
décret n° 49-578 : « Chaque notaire est affecté, au 1er janvier de chaque année (n), dans la
classe de cotisation correspondant à la moyenne de ses produits de base pour les années
N - 4 à N - 2 ». `decret_2026_418_liberaux` porte bien la classe 3 de la CAVP.
- **Écart 9, mineur.** La même fiche, au même article 2, renvoie les classes de la
  section B de la CPRN à cette fiche-ci : « article 2-3 et annexe 1, les classes de la
  section B, que le modèle ne porte pas (même fichier, `manque` ;
  `cotisation_par_classes_liberales`) ». E15 laisse les notaires hors de la fiche
  (« aucune fiche de règle ne la porte ») sans reprendre ce renvoi, qui ne mène plus à
  rien.

## 3. `LUES_AU_DROIT`, le bloc « Reprise », « Pour la suite »

Conforme. `tests/test_carte.py` n'exige d'une fiche lue au droit que l'absence de manque,
d'écart (`outils_carte.ecarts`) et de rédaction à la fois citée et à rattacher ; il ne
borne pas les `supposee`. Les fiches admises en ont : `surcote_par_age_seul` 8 sur 18,
`carpv_minoration_age_seul` 4 sur 6, `sections_liberales_majoration_enfants` 4 sur 5. Le
bloc « Reprise » de l'action 130 est récrit par la session qui a avancé l'action, daté du
jour, en huit lignes ; « Pour la suite » ne dit que ce qui reste. Sauf l'oubli de la CARPV
(écart 4), ni l'un ni l'autre n'est instruit ici.

## Tests

`tests/test_sections_liberales.py`, `tests/test_carte.py`, `tests/test_textes.py`,
`tests/test_regle_de_chacun.py` : 100 verts ; sous `PRESOMPTIONS_DECALEES=1`, 99 verts et
1 sauté. `python -m pytest -m rapide` : 4 589 verts, 9 sautés.

## Pour E16

Neuf écarts, tous mineurs, aucun sur une valeur servie : les mentions de 1994 et l'arrêté
de 1957 (1, 2) ; les arrêtés de 2006, 2011, 2019, 2021 et 2024 et l'article 2-1 de la
Cipav, à citer ou déclarer (3 à 6) ; le décret n° 77-313 (7) ; le compte des textes à
rattacher (8, la note seule) ; le renvoi de `decret_2026_418_liberaux` (9). Au point non
tranché, les deux précisions (2 507,32 € sans les années d'office ; 1 151,68 € en lisant
les statuts année par année), à porter à la fiche avec les deux lectures de E15.
