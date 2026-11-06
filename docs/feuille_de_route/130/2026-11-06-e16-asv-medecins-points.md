# Les écarts de R-E16 repris, et `asv_medecins_points` lue au droit

File E16, le 6 novembre 2026 (action 130, vague 11, sur Opus). Index de la DILA récupérés
ce jour : JORF à jour du 3 novembre 2026, LEGI du 2 novembre ; requêtes SQL sur la table
`doc`, sans borne. Chaque citation ajoutée est comparée par script au texte de l'index
(espaces normalisés, coupée aux « […] » et aux « » ; « ») : 33 fragments, tous présents.
Aucun taux ni aucune valeur servie ne change ; le paquet (`construire_donnees.py`) ne
bouge pas.

## 1. Les écarts de R-E16

- **(a) 1994** (`surcote_par_age_seul`, `avant_2007`). Relu : JORFARTI000001005266,
  « (art. 49 et 59) » ; JORFARTI000001391556, « L'arrêté du 13 mai 1994 sera publié
  intégralement au Bulletin officiel du ministère no 94-17 ». Écrit à la place de « son
  titre seul ».
- **(b) 1957.** Au titre, de 1948 à 1961, les arrêtés des experts-comptables : celui du
  14 septembre 1957 (JORFTEXT000000477655, « APPROBATION DES MODIFICATIONS APPORTEES A
  L'ART. 31 DU REGLEMENT […] ») est le seul avant 1961. « onze de 1957 à 1977 ».
- **(c) Six arrêtés** (`cotisation_par_classes_liberales`), relus et cités chacun dans la
  version de sa date : CARPV 27 février 2006 (JORFARTI000002071126, mention seule,
  `carpv_de_1998`) et 11 janvier 2011 (JORFARTI000023448554, « ou rémunération (définis
  ci-dessus) », `cavec_de_2008`) ; Cipav 3 octobre 2006 (JORFARTI000002050100, l'arrêté de
  1979 « abrogé à compter du 1er janvier 2007 », `carpv_de_1998`) et 16 décembre 2021
  (JORFARTI000044554134, 15° et 16°, en vigueur le 1er janvier 2022 par son article 2,
  `carpv_de_2022`) ; CAVEC 19 juin 2019 (JORFARTI000038689131, II, 2° et 3°, `cavec_de_2019`)
  et 2 juillet 2024 (JORFARTI000049880543, II, 1°, « l'année précédente »,
  `sans_la_cipav_2023`). L'approximation du vétérinaire rémunéré dit les statuts de 2011.
- **(d) L'article 2-1 du décret n° 79-262** (LEGIARTI000006767475), cité à `carpv_de_1998`.
  Le modèle ne le sert pas : il ne pose pas l'ancien affilié de la caisse des géomètres.
  Le texte ne dit pas si la majoration donne des points (l'article 2 attache les points à
  la classe ; le résumé du décret n° 99-913, seul au Journal officiel, en fait une
  « MESURE TRANSITOIRE PREVUE PAR L'ACCORD D'INTEGRATION ») : point non tranché, déclaré à
  l'approximation de `carpv_de_1998` et à `sources.a_relire`. Cas posé, moteur Python :
  né en 1950, homme, `profession_liberale` (niveau 1) de 25 à 65 ans ; la Cipav sert
  3 560,7558 € (« cotisations revalorisées 57,432 € × rendement 6.20% »). Cotisations
  revalorisées de 2000 à 2006 : 1 393,6029 + 1 453,9028 + 1 512,0826 + 1 642,6116 +
  1 668,6090 + 1 720,1479 + 1 809,0320 = 11 199,9888 €. Lecture A : **0 €**. Lecture B :
  11 199,9888 × 0,33 = 3 695,9963 € ; × 0,062 = **229,15 €** par an servis en moins.
  Candidat hors de la fiche, non chiffré : le modèle ne connaît pas la caisse des
  géomètres ; un géomètre d'avant 2000 y est servi comme un affilié de la Cipav depuis
  1979, sans la reprise de ses droits ni son abattement selon l'âge (décret n° 99-913,
  article 3, au seul résumé).
- **(e) Le décret n° 77-313.** Au titre, de 1953 à 1980, les décrets qui nomment le décret
  du 21 mai 1953 : quatorze modifient l'article 2 de 1955 à 1974 ; le n° 77-313
  (JORFTEXT000000515110) modifie l'« ART. 2 (AL. 1) DU DECRET DU 21-05-1953 ». Seul décret
  du 21 mai 1953 des experts-comptables dans l'index : le n° 53-506 (des n° 53-494 à
  53-513). Corrigé aux trois endroits (`avant_1979`, deux `sources`).
- **(f) 29 textes à rattacher, non 31.** La note de E15 le dit à tort ; c'est un récit, il
  ne se récrit pas : le compte juste est ici.
- **(g) Le renvoi de `decret_2026_418_liberaux`.** Aucune fiche de règle ne porte les
  classes de la section B de la CPRN : `cotisation_par_classes_liberales` ne lit que la
  CARPV, la CAVEC et la Cipav, et `cprn_ages_decote_enfants` range le décret n° 2013-1157
  parmi ses textes sans effet. Le renvoi le dit ; la forme de la fiche reste au
  propriétaire (question 32).
- **(h) La CARPV d'avant 2014** entre à la liste du bloc « Reprise ».
- **Le point non tranché du cumul à la CAVEC**, porté à la fiche avec ses deux précisions,
  refaites à la main. Même cas que E15 (née en mars 1960, salariée non cadre dès 22 ans,
  expert-comptable en cumul de 55 ans à 65 ans, niveau 0,1), cotisations revalorisées
  par année : 2015 604,7516 ; 2016 735,2640 ; 2017 738,1780 ; 2018 733,8017 ; 2019
  741,5099 ; 2020 748,3616 ; 2021 741,9531 ; 2022 723,4815 ; 2023 732,0660 ; 2024
  767,1668 ; 2025 195,5000 ; total 7 462,03 € ; servi 621,5875 € (8,33 %). La classe C
  vaut 284 / 48 de la classe A, soit 236 / 48 = 4,9167 de plus.
  - Sans les deux années d'office (2015, 2016 : 1 340,0157 €) : 7 462,03 − 1 340,02 =
    6 122,02 ; × 4,9167 = 30 099,93 ; × 0,0833 = **2 507,32 €** (3 128,91 € servis).
  - Le minimum du décret de 2015 à 2018, l'option ensuite : 604,7516 + 735,2640 +
    738,1780 + 733,8017 = 2 812,00 ; × 4,9167 = 13 825,64 ; × 0,0833 = **1 151,68 €**
    (1 773,26 € servis). Les statuts de 2012 ne disent rien du cumul (relus : « cumul »
    n'y est que « cumul emploi-retraite » ou « de manière cumulative »).
  - Sous `PRESOMPTIONS_DECALEES=1`, le pont (requête du site, naissance « 1960-03 ») sert
    616,1591 € (« 7,397 € »), contre 621,5875 € ; la lecture A sur toute la carrière,
    616,1591 × 4,9167 = **3 029,45 €** de plus.

## 2. `asv_medecins_points`, lue au droit

**La fiche choisie.** Des cinq, c'est la première ; l'éclaireur n'a trouvé qu'une question
au propriétaire qui la touche, la 22 (les statuts de la CARMF d'avant 2017), qui vise les
articles 12 ter et 15 des statuts de l'ASV : la majoration et les enfants, que portent
`surcote_par_age_seul` et `carmf_asv_minoration_enfants`, non les points ni la valeur de
service. Elle ne la bloque pas.

**Les rédactions.** `textes.py --non-lues` en comptait trente ; toutes lues, dix
citées aux versions, vingt déclarées sans effet (la cotisation annuelle de D. 645-2,
qui ne décide pas des points ; la dispense et les praticiens hospitaliers, que le
simulateur ne pose pas) : il en reste 0. Le cliquet du périmètre descend de 9 305 à 9 283
(une rédaction pour l'article 2-1, vingt et une pour l'ASV). Lues en plus : les cinq
rédactions de l'article 2 de 1981 à 2006 et l'article 7 du décret n° 71-542.

**Ce que disent les textes, et ce que le modèle sert.**
- Les points : 30,16 de 1972 à 1993, 27 depuis, au prorata des trimestres (article 2,
  depuis le 8 juillet 1994) : servis (7,54 et 6,75 par trimestre).
- Jusqu'au 8 juillet 1994, l'article 2 ne compte pas en points : « une prestation
  supplémentaire annuelle correspondant à 1055 fois la valeur du tarif de la
  consultation », « après trente-cinq années de cotisations » ; 35 × 30,16 = 1 055,6 :
  la conversion de 1994 le garde. La rédaction de 1972 n'est pas dans LEGI.
- La valeur de service : la consultation jusqu'en 1993 ; 100 F au 1er janvier 1994,
  « revalorisée chaque année dans les conditions prévues pour les pensions du régime
  général » ; 102 F du 28 mars 1999 au premier semestre 2012 (rédactions de 1999, 2004,
  2006 ; 102 / 6,55957 = 15,5498 €) ; puis les valeurs fixes du décret n° 2011-1644,
  article 4, toutes relues (2012, 2016, 2021, 2022, 2023, 2025), que la fiche citait juste.
  **Erreur neuve, déclarée et non corrigée** : le modèle porte la valeur d'une année
  d'ancrage aux prix de l'année de liquidation (`valeur_point_annee`,
  `valeur_point_fiche`). Cas posés, moteur Python, hommes nés en janvier,
  `medecin_liberal` (niveau 1) de 30 à 65 ans :
  - né en 1937, liquidation 2002 : 879,52 × 13,313333 = 11 709,34 € servis ; le texte
    879,52 × 15,5498 = 13 676,36 € ; **1 967,02 €** par an en moins ;
  - né en 1940 (2005) : 960,52 × (15,5498 − 14,133314) = 960,52 × 1,416486 =
    **1 360,56 €** en moins ;
  - né en 1950 (2015) : 994,46 × (13,184592 − 13) = **183,57 €** de trop (le décret :
    13 € de 2012 à 2020) ;
  - né en 1953 (2018) : 998,37 × (11,518896 − 11,31) × 1,15 = 998,37 × 0,208896 × 1,15 =
    **239,84 €** de trop (11,31 € jusqu'en 2020) ;
  - né en 1959 (2024) : 1 014,99 × (11,944317 − 11,71) × 1,15 = **273,50 €** de trop
    (11,71 € en 2023 et 2024).
  Le coefficient de 1,15 est celui que le modèle sert (candidat 41 et `surcote_par_age_seul`
  pour ce qu'il vaut) ; il multiplie les deux montants. Avant 1999 : non mesuré.
- La durée minimale : dix ans jusqu'au 15 février 1985 (décret n° 71-542, article 7), un an
  depuis (« pendant au moins un an », article 7 du décret n° 72-968, en vigueur depuis le
  15 février 1985, et non depuis 2026 comme la fiche le laissait entendre). **Erreur
  neuve, déclarée et non corrigée** : le modèle ne pose aucune durée minimale. Cas posé :
  homme né en janvier 1960, salarié non cadre de 22 à 40 ans et de 40 ans 9 mois à 65 ans,
  médecin libéral de 40 ans à 40 ans 9 mois : le modèle sert 27 points × 11,82 € × 1,15 =
  **367,01 €** par an ; le texte, rien. Le modèle compte là quatre trimestres pour neuf
  mois, et rien pour six mois à cheval sur deux années ; l'article 3 (l'affiliation au
  premier jour du trimestre civil suivant) n'est pas confronté : non mesuré.
- Le cumul : depuis 2004, « aucun nouveau droit à retraite au titre des cotisations
  versées » (article 2) ; 3 % de cotisation depuis 2011 (D. 645-2) : cité, hors de cette
  fiche (`cumul_emploi_retraite_complementaires_des_liberaux`).

**`LUES_AU_DROIT`.** La fiche n'y entre pas. `test_carte` l'admettrait déjà (ni manque ni
écart), mais elle n'est pas écrite au droit en entier : restent la rédaction de 1972 de
l'article 2 et l'arrêté de 1972 de la cotisation, la coupe des versions à la date de
liquidation (qui décide de la valeur de service et de la durée minimale), et les
liquidations d'avant 1999. Arrêt au contexte, comme la consigne le prévoit.

## Tests

`tests/test_sections_liberales.py`, `tests/test_carte.py`, `tests/test_textes.py`,
`tests/test_regle_de_chacun.py` : 100 verts ; sous `PRESOMPTIONS_DECALEES=1`, 99 verts et
1 sauté. `python -m pytest -m rapide` : 4 589 verts, 9 sautés ; sous
`PRESOMPTIONS_DECALEES=1` : 4 384 verts, 214 sautés.

## Pour la suite

`asv_medecins_points` : couper les versions à `liquidation.date_effet` ; lire l'arrêté de
1972 et la rédaction d'origine de l'article 2 (fac-similé : file des fac-similés) ;
chiffrer les liquidations de 1994 à 1998 et d'avant 1994. Au propriétaire, avec les
autres : les deux erreurs de l'ASV et le point non tranché de l'article 2-1.
