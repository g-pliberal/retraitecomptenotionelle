# Étape 2, première moitié : le filtre de l'index élargi et l'index reconstruit, les grilles de l'État certifiées depuis le Noyau RH

**Le 2 novembre 2026 : le propriétaire a tranché le périmètre — « tout ce
qu'on peut trouver », les grilles de l'État, de la territoriale et de
l'hospitalière, et non l'État seul. Le filtre de l'index de la DILA garde
désormais les textes des grilles et des carrières : l'index LEGI, reconstruit
depuis le dump, en garde douze fois plus de versions d'articles qu'avant. Les grilles de l'État sont entrées dans le dépôt,
tirées du Noyau RH du CISIRH et certifiées : 2 105 grilles, 33 169 versions
d'échelons avec leur indice et leurs durées, le barème et les textes. Elles
recomposent au centime le traitement mensuel des 36 échelons que le ministère
de l'agriculture publie pour ses techniciens supérieurs au 1er juillet 2024.
Restent la territoriale et l'hospitalière, à tirer du LEGI.**

Demande : la session d'orchestration du 2 novembre 2026, file B, rapportant la
décision du propriétaire, à inscrire au bloc « Reprise » et dans cette note ;
l'étape 2 commence par élargir le filtre et faire reconstruire l'index par le
workflow `index-dila.yml`, lancé sans être modifié ; le pré-remplissage du
formulaire n'est pas pour cette session. Les autres questions de « Ce que le
propriétaire tranche » restent ouvertes : le chemin type, la part de primes
par période, les cas types de l'action 152, les entreprises à statut ; les
militaires, que la décision ne nomme pas, sont de l'État.

- *Le filtre de l'index* (`THEMATIQUE`, `scripts/fetch/dila_index.py`,
  commit 557d4c8). Il retient en plus : les indices bruts et majorés au
  pluriel, les indices nouveaux ou réels majorés et les indices nets d'avant
  1983, les indices de solde, « indices de la fonction publique » (le titre du
  décret n° 82-1105) ; l'échelonnement, le classement et la bonification
  indiciaires ; les grilles indiciaires ou de rémunération, les échelles de
  rémunération ; les statuts particuliers, les dispositions statutaires
  communes, l'organisation des carrières et l'avancement d'échelon, qui fixent
  les durées et les reclassements. Un article porte le titre de son texte, qui
  le fait entrer avec les autres. Le test (`tests/test_dila_index.py`) passe
  dix titres et contenus modelés sur des textes réels des trois versants et des
  militaires — n° 2016-604, 2010-330, 87-1108, 2016-596, 2006-1691, 2009-1388,
  2009-21, 82-1105, 93-863, 2021-1267 —, vus refusés par l'ancien filtre, et
  garde dehors l'avis de concours d'un de ces corps.
- *La reconstruction.* `index-dila.yml`, entrée `reconstruire`, lancé sans
  modification le 2 novembre 2026 à 20 h 54 UTC sur 557d4c8 (run
  41523537229), pour le JORF et le LEGI. Le LEGI, reconstruit en 1 h 10, est
  publié à 22 h 06 UTC : 325 879 documents au lieu de 246 302, 1,6 Go, sous le
  filtre du code ; le JORF tournait encore à 22 h 10.
- *Le Noyau RH, téléchargé.* La pièce `6_nomenclatures_noyau_xmlzip` du jeu de
  juillet 2026 (12 088 867 octets, empreinte SHA-256 `d5cf571b…a8f11f`,
  364 tableaux XML en ISO-8859-15). data.economie.gouv.fr coupe la plupart des
  connexions à travers le mandataire de la session (« tunnel closed »), et
  répond à une nouvelle tentative : le récupérateur retente trente fois.
- *Ce qui en est tiré* (`scripts/fetch/cisirh_grilles.py`), sous
  `data/reference/grilles/etat/` : 1 089 versions de corps, avec leur
  catégorie et le chaînage des fusions ; 5 897 versions de grades, avec leur
  corps, leur grille et leurs codes PCS et NNE ; 2 105 grilles, avec leur type
  d'indice — 2 034 en indice brut, 18 en majoré, 34 en « autre valeur du
  point », 19 sans objet —, leurs grilles d'avant et d'après et leurs textes ;
  33 169 versions de 16 730 échelons, avec leur rang, leur indice (31 459), la
  lettre de hors-échelle (1 546), le chevron (58), la nature — stagiaire,
  élève, exceptionnel, fonctionnel, provisoire —, les trois durées en mois
  (32 198) et l'échelon suivant ; les 5 426 lignes du barème ; les 1 539
  textes que corps, grades et grilles citent. Le noyau est sous licence
  ouverte 2.0 : le dépôt republie, en citant la source.
- *La certification.* `scripts/verifier_donnees.py` relit
  `data/brut/cisirh_grilles.json`, que le récupérateur écrit, et certifie six
  colonnes : le rang (33 169 valeurs), l'indice (31 459), les durées minimale,
  moyenne et maximale (32 198 chacune) des échelons, l'indice majoré du barème
  (5 426) ; toutes identiques. L'indice brut se trie en nombre
  (`CLES_NUMERIQUES`), pour que la certification ne déplace aucune ligne. Le
  journal (`data/derive/certification.json`) ne reçoit que ces six traces ;
  `tests/test_donnees.py` les rattache à leurs fichiers.
- *Le recoupement à une source publiée* (`tests/test_grilles_etat.py`). La
  grille des techniciens supérieurs du ministère de l'agriculture,
  « Données actualisées au 1er juillet 2024 » (infoma.agriculture.gouv.fr,
  `grille_remu_tsma.pdf`, lue le 2 novembre 2026), donne pour chacun des
  36 échelons de ses trois grades l'indice majoré, la durée moyenne et le
  traitement mensuel brut. Le noyau donne l'indice brut ; son barème, l'indice
  majoré, égal au publié pour les 36 ; la valeur annuelle du point du dépôt,
  59,0734 €, le traitement : le traitement annuel arrondi à l'euro, divisé par
  douze, redonne chaque montant au centime — 592 × 59,0734 = 34 971,45, soit
  34 971 €, 2 914,25 € par mois au 11e échelon de chef technicien —, quand
  l'en-tête annonce un point de 4,923 €. Les durées concordent. Ces trois
  grades partagent leurs grilles avec les techniciens de formation et de
  recherche de l'agriculture et ceux de l'INRAE.
- *Ce que le noyau ne porte pas.* Les grilles commencent avec leur corps, ou
  avec sa dernière refonte : celle des instituteurs, corps de 1961, en août
  1993 seulement ; celles des adjoints administratifs de l'État et des agents
  administratifs des impôts, en novembre 2006 ; 245 grilles commencent avant
  1990, dont certaines au 1er janvier 1900, date qui veut dire « depuis
  toujours ». Le barème mêle le minimum de traitement — l'indice majoré 366 à
  tout indice brut jusqu'à 367 depuis le 1er janvier 2024 — et n'a qu'une ligne
  avant novembre 2006. Les tableaux de reclassement, échelon par échelon, n'y
  sont pas : seulement la grille d'avant et d'après, et le chaînage des grades
  et des corps.
- *L'index, avant la reconstruction* (mesure de la session, par des scripts
  qu'elle n'a pas versés : un texte de grille est celui dont le titre dit
  échelonnement indiciaire, échelle de rémunération, classement indiciaire,
  grille indiciaire ou indices de la fonction publique ; un décret se
  reconnaît à son numéro en tête de titre, un arrêté aux 90 premiers caractères
  du sien ; le versant, aux mots du titre). L'index publié le 2 novembre à
  11 h 55 UTC, 246 302 documents, avait 517 textes de grilles de l'État, dont
  109 avec des articles, 384 versions d'articles en tout ; 33 de la
  territoriale, 24 avec articles, 47 versions ; 67 de l'hospitalière, 60 avec
  articles, 144 versions ; 8 des militaires, 3 avec articles, 4 versions. Des
  488 textes de grilles que le noyau cite, 219 manquaient, 194 n'y avaient que
  leur texte, sans article, 75 avaient des articles. Aucun article des décrets
  n° 2016-604 (échelles C1 à C3 de la territoriale), 2010-330 (sa catégorie
  B), 2021-1267 (aides-soignants), 82-1105 (le barème) ; 40 versions de cinq
  articles pour le n° 2009-21 (indices de solde des militaires non officiers),
  21 de sept articles pour le n° 2008-836.
- *L'index, après la reconstruction* (même mesure). 841 textes de grilles
  de l'État, dont 829 avec des articles, 4 374 versions d'articles ; 142 de la
  territoriale, tous avec articles, 878 versions ; 312 de l'hospitalière, 311
  avec articles, 1 750 versions ; 13 des militaires, 51 versions : douze fois
  plus de versions qu'avant. Des 488 textes de grilles du noyau, 395 ont leurs
  articles, 93 manquent encore. La première version d'article des textes de la
  territoriale date des années 1980 pour 14 d'entre eux, 1990 pour 41, 2000
  pour 15, 2010 pour 55, 2020 pour 17 ; de l'hospitalière, des années 1950 à
  1980 pour 61, puis 79, 55, 95 et 21. Les textes attendus y sont, chacun
  depuis son entrée en vigueur : le n° 82-1105, le barème, 43 versions de
  quatre articles du 27 décembre 1982 au 1er janvier 2024 ; le n° 87-1108,
  les échelles de la catégorie C de la territoriale d'avant 2017, 13 versions
  de deux articles du 31 décembre 1987 à 2014 ; le n° 2016-604, ses échelles
  C1 à C3, quatre articles depuis le 1er janvier 2017, modifiés par le
  n° 2021-1819 ; le n° 2010-330, sa catégorie B, quatre articles et neuf
  versions depuis le 27 mars 2010 ; les n° 2016-594, 2016-596 et 2016-636,
  carrières de la territoriale et de l'hospitalière, 17, 29 et 39 articles ;
  les n° 2021-1267, 2022-1207 et 2021-1262, aides-soignants, corps
  paramédicaux et infirmiers, depuis le 1er octobre 2021 ; les n° 2008-836
  (26 articles, 93 versions) et 2009-21 (8 articles, 43 versions). Le LEGI
  garde donc chaque version d'article depuis l'entrée en vigueur de son texte,
  pour ceux qu'il consolide ; ce que les plus anciens écrivaient avant leur
  première version consolidée reste au JORF.

*Pour les autres files.* Rien pour le site (file C) : le pré-remplissage est
l'étape 4. Deux fichiers partagés ont reçu des lignes :
`scripts/verifier_donnees.py` (six certifications, à côté de celles du point
d'indice, et `indice_brut` dans `CLES_NUMERIQUES`) et `tests/test_donnees.py`
(les six séries et leurs fichiers).

*Ce qui reste de l'étape 2.* Les grilles de la territoriale et de
l'hospitalière, tirées du LEGI par l'index reconstruit : les échelles C1 à C3
(n° 2016-604, 2021-1819) et celles d'avant 2017, la catégorie B (n° 2010-330),
puis les cadres d'emplois et les corps les plus nombreux de la note de
l'étape 1 — aides-soignants (n° 2021-1267, 2022-1207), infirmiers
(n° 2021-1262, après le n° 2016-647), catégorie C de l'hospitalière
(n° 2016-636). L'histoire du barème avant novembre 2006, au décret n° 82-1105.
Les grilles d'avant le noyau : les instituteurs avant 1993, la catégorie C de
l'État avant 2006. Les reclassements d'une version à la suivante, que les
décrets écrivent. Les indices de solde des militaires.
