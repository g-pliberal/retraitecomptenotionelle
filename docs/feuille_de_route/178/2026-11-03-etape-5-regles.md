# Étape 5 : les règles du panorama, confrontées aux tables du scénario 1

**Reprise, au 3 novembre 2026.** Fait : les tableaux de législation des
fiches 2, 4, 14, 24 et 26, confrontés aux tables du dépôt, et l'ASPA d'une
personne seule corrigée pour 2008, 2013 et 2015. Reste : les trois erreurs du
coût que l'étape 4 a relevées — le recours à la garantie compté en têtes, la
complétude de la grille au lieu de la proratisation, les nouveaux retraités
de 2024 à 28 % de trop —, qui touchent aux fichiers de la file C
(`cout.py`, `donnees/population.py`) : à reprendre après la vague de la nuit
du 2 au 3 novembre, par la première, la deuxième, puis la troisième selon la
réponse du propriétaire (ci-dessous, « La question »).

**Le 3 novembre 2026, ce qui est fait.** Cinq confrontations, chacune par un
test du niveau `controle` de `tests/test_controle_drees_panorama.py`, et une
correction du scénario 1. Au suivi, les fiches 14, 24 et 26 passent au statut
`confronte` ; la ligne de la fiche 4 nomme aussi le test de sa revalorisation.

1. *Le témoin.* `tests/temoins/drees_panorama_2026_regles.json` porte 822
   cellules des classeurs des fiches 2, 4, 14, 24 et 26, et dix phrases des
   encadrés 1 et 2 de la fiche 14. Les tableaux de législation fusionnent
   leurs cellules sur plusieurs générations : une cellule vide que couvre une
   fusion prend la valeur de la première, qu'elle nomme. Trois tests le
   recoupent à la source quand `data/brut/` porte l'archive et le PDF : chaque
   valeur à sa cellule, chaque fusion au XML de sa feuille, chaque phrase au
   texte du PDF.
2. *Ce qui se retrouve, mois de naissance par mois de naissance.* L'âge légal
   du privé, des actifs et des super-actifs, avant et après la loi de
   financement pour 2026 (fiche 14, tableau 1 et son complément) ; la durée
   requise du privé et des sédentaires (tableau 2) ; l'âge d'annulation de la
   décote du privé et des fonctionnaires, que le dépôt tire de la limite
   d'âge et de l'année où le droit s'ouvre (tableau 3) ; les quatre portes de
   la carrière longue, à la rédaction en vigueur quand la génération les
   atteint (tableau 4) ; les mois où chaque génération atteint l'âge légal,
   de 2022 à 2034 (fiche 2, encadré 1) ; le coefficient de minoration, la
   décote de la fonction publique et les taux de la surcote (fiche 14,
   encadrés 1 et 2) ; les bornes de la pension d'invalidité de 2026 (fiche
   24) ; les revalorisations de l'Agirc, de l'Arrco et du RAFP de 2008 à 2025
   (fiche 4, tableau 1 complémentaire) ; le minimum vieillesse d'un couple au
   31 décembre de chaque année depuis 2006 (fiche 26, graphique 2). Pour les
   actifs et les super-actifs, le dépôt ne porte que le calendrier de 2026 :
   là où celui de 2023 en diffère, l'âge de 2026 tombe après le 1er septembre
   2026, et aucune pension n'a pu prendre effet sous l'ancien ; le test le
   vérifie.
3. *La correction : l'ASPA d'une personne seule en 2008, 2013 et 2015.* La
   table les sautait, et le modèle les ramenait sur les prix depuis l'année
   d'avant, 2013 et 2015 sous le niveau `certifiee` de leur ancre : 7 664,96
   euros pour 2008, quand la caisse sert 7 597,59 euros depuis le 1er
   septembre ; 9 407,30 euros pour 2013, contre 9 447,21 euros depuis le 1er
   avril ; 9 603,84 euros pour 2015, que rien n'a revalorisé. Les trois ancres
   viennent du barème de la Cnav (circulaires 2008/45, 2013/29 et 2014/58),
   que le panorama redonne au centime. Le test d'abord, vu rouge dans les deux
   moteurs (`tests/test_liquidation.py`, `tests/js/moteur.test.js`), puis la
   table et le paquet refait ; la fiche `minimum_vieillesse` cite la lecture.
4. *Ce que le texte tranche contre la DREES.* Le tableau 4 de la fiche 14
   donne 60 ans et 9 mois à tous les nés de 1965 et 1966 après la loi de
   financement ; le 4° du II de D. 351-1-1, rédaction du 1er septembre 2026
   (décret n° 2026-345), donne « soixante ans et huit mois » aux nés de
   décembre 1965, comme le dépôt. L'encadré 1 écrit « 2,5 % pour la génération
   1944 » ; R. 351-27 le donne aux nés avant 1944, et 2,375 % à ceux de 1944,
   comme le dépôt. La revalorisation des régimes de base de 2008 est de 1,8 %
   au tableau de la fiche 4, de 1,9 % aux arrêtés et à l'indice de la fiche 26
   du même panorama ; celle de l'Ircantec de 2019, de 1,0 % au tableau, de
   0,3 % au point de l'Ircantec. La lecture du graphique 2 de la fiche 26 dit
   « fin 2025 » le montant du couple de 2026, 1 620 euros, quand sa cellule
   de 2025 porte 1 605,73 euros.
5. *Ce que le dépôt laisse ouvert, déjà inscrit.* L'ASPA d'une personne seule
   de 2022 est celle de janvier, quand le couple et le panorama prennent celle
   du 1er juillet ; et la table porte douze fois le mensuel arrondi en 2007,
   2017, 2021 et de 2023 à 2026, quelques centimes sous l'annuel du barème. Les
   deux sont inscrits à l'action 138, étape 2 (`tests/test_ines.py`), « à
   reprendre » et « à décider » ; le test les déclare, bornés.
6. *Hors du modèle.* La majoration pour tierce personne (fiche 24) et
   l'allocation supplémentaire d'invalidité (fiche 26) : le modèle ne les sert
   pas.
7. *Une comparaison, sans erreur.* De 2000 à 2025, le minimum vieillesse
   d'une personne seule a monté de 89,7 %, les prix de 50,2 %, les pensions du
   régime général de 45,8 % (fiche 26, graphique 1) : 26 % de gain sur les prix,
   par les hausses de 2009 à 2012 et de 2018 à 2020. La garantie de la
   proposition, indexée sur les prix, n'en suivrait aucune.

**Ce qui reste à l'étape 5.** Les trois erreurs que l'étape 4 a consignées
(`178/2026-11-03-etape-4-confrontations.md`, « Ce qui revient à l'étape 5 »),
toutes au coût et à la population, dans les fichiers de la file C cette nuit :
le recours à la garantie, à compter en euros, 62 % et non 50 % des ayants
droit (`GarantieDistribution`, `cout.py`) ; la complétude des carrières
incomplètes, à prendre au coefficient de proratisation, 0,93 et non 0,973 pour
1953 (`CarrieresIncompletes`, `donnees/population.py`) ; la pension des
nouveaux retraités de 2024 et les départs en carrière longue de la grille.

**La question.** Les nouveaux retraités de la grille et ses carrières longues
tiennent à ses cas types, que la population de l'étape 14 de l'action 138
doit remplacer. Faut-il les corriger dans la grille même, sans attendre cette
population ? L'avis de l'étape : non — la file I la mène cette nuit, et une
correction de la grille serait défaite par elle.

**Pour les autres files.** La file D, qui tient les règles des indépendants :
la valeur de 2022 de la RCI (`valeurs_point.csv`) est celle de janvier, la
hausse de 4 % du 1er juillet ne paraissant qu'en 2023 ; et le panorama prête
à la RCI, en 2024 et 2025, la revalorisation des régimes de base (5,3 et
2,2 %), quand le barème de la Cnav lui donne 3,7 et 0,6 % : à vérifier.
La file A a confié l'encadré 1 de la fiche 2 à l'étape 5, qui l'a confronté
(`test_les_mois_de_depart_de_l_encadre_de_la_fiche_2_sont_ceux_de_l_age_legal`) ;
elle a renvoyé les fiches 8 et 15 à l'étape 4, qui était close : le test de
l'étape 4 les compte, `a_confronter`, et elles attendent une session.
La file H : le barème `aspa_montant_bar` du registre de la Cnav nourrit
désormais aussi `minimum_vieillesse.csv`, pour trois années.
