# Étape 4 : les confrontations du panorama au modèle, et ce qu'elles laissent à l'étape 5

**Le 3 novembre 2026, ce qui est fait.** Les douze fiches que le suivi
renvoyait à l'étape 4 (04, 06, 07, 09, 11, 13, 18, 28 à 32) sont confrontées
au modèle, chacune par un test du niveau `controle`, dans
`tests/test_controle_drees_panorama.py` ; au suivi, elles passent au statut
`confronte`, nouveau, et nomment leurs tests (`confronte_par`) et ce qu'ils
trouvent (`confrontation`). Aucun écart n'est corrigé : chacun est déclaré
dans le test qui le mesure, borné, pour qu'un écart qui bouge se voie.

1. *Le témoin.* `tests/temoins/drees_panorama_2026_confrontations.json`
   porte les 207 valeurs confrontées, chacune avec son classeur, sa feuille et
   sa cellule, et sept phrases du PDF. Deux tests le recoupent à la source
   quand `data/brut/` porte l'archive et le PDF : chaque valeur au bit près,
   chaque phrase dans le texte lu dans l'ordre de lecture. Sans eux (GitHub),
   ils se sautent ; les confrontations lisent le témoin.
2. *Ce qui se retrouve.* L'érosion des pensions relativement aux prix (fiche
   4, graphique 4), sur les cas types 1 et 2 du COR que TRAJECTOiRE calcule :
   à trois dixièmes de point, générations 1940 à 1950, horizons de 5 à 20 ans,
   par les seules séries du dépôt. Les durées validées par sexe et par
   génération (fiche 11, graphique 3) : celles que le dépôt lit du COR,
   trimestre pour trimestre. Le taux de remplacement médian du privé (fiche
   6, graphique 4) : celui du cas type au SMIC, à deux points.
3. *Les écarts déclarés.* Le pouvoir d'achat des liquidants de 2000 (fiche 4,
   graphique 3) baisse au dépôt de 0,2 à 1,1 point de plus en vingt-cinq ans ;
   les prix de décembre ne le referment pas. Le salaire moyen et le
   fonctionnaire sédentaire sont de 4 à 11 points sous les médianes ; la seule
   femme de la grille n'a que le tiers ou la moitié de l'écart de pension
   publié (fiche 6, graphique 3). La grille ne compte aucun polyaffilié,
   quand 54 % de la génération 1957 le sont (fiche 13). La garantie sur
   succession lit le patrimoine des retraités de 2018, un quart sous celui de
   2024 (fiche 9). Le pilier sert tout en rente quand le compartiment 1 du PER
   laisse le capital, et son régime fiscal n'est pas écrit (fiche 29). Trois
   comparaisons, sans erreur : les 10 points capitalisés feraient plus du
   tiers des prélèvements de retraite, six fois et demie la part de la
   retraite supplémentaire (fiche 30) ; les 5 % volontaires, deux tiers d'un
   versement moyen à un contrat individuel (fiche 31) ; la rente du pilier à
   maturité, plus de trois fois la rente moyenne d'aujourd'hui (fiche 32).
4. *Une coquille de la DREES.* Sous le graphique 3 de la fiche 4, la lecture
   inverse le brut et le net (4,4 % et 3,7 %) ; le texte et le classeur
   disent −3,7 % brut et −4,4 % net pour le non-cadre. Le test suit le
   classeur.

**Ce qui revient à l'étape 5**, des erreurs du modèle, que l'étape 4 ne
corrige pas.

1. *Le recours à la garantie se compte en têtes, non en euros* (fiche 28).
   Le coût multiplie la dépense des ayants droit par 50 %
   (`GarantieDistribution`, `src/retraite_notionnelle/cout.py`). Le
   non-recours baisse avec le montant attendu, de 77 % sous 100 euros à 22 %
   entre 500 et 600 : les allocataires touchent 337 euros, les non-recourants
   en toucheraient 205, et le recours en euros est de 62 %. Le coût de la
   garantie est sous-estimé d'un cinquième.
2. *La complétude de la grille passe la proratisation* (fiche 11). La
   grille réduit la pension d'une génération par sa durée validée moyenne
   rapportée à la durée requise (`CarrieresIncompletes`,
   `src/retraite_notionnelle/donnees/population.py`) : 0,973 pour 1953,
   quand le coefficient moyen, que nul ne passe à 100 %, vaut 0,93. Quatre
   points de trop sur la pension des carrières incomplètes.
3. *La grille sert trop à ses nouveaux retraités* (fiche 7) : 2 102 euros en
   2024, 28 % de plus que les 1 637 publiés ; 13,5 % de femmes, dont la
   pension n'est que de 8,5 % sous celle des hommes, contre 29,4 %. *Et elle
   fait partir trop de carrières longues* (fiche 18) : 21,8 % des départs de
   la Cnav à 60 ans, contre 17,4 %. L'une et l'autre tiennent aux cas types
   de la grille, que la population de l'étape 14 de l'action 138 doit
   remplacer : les corriger dans la grille même, ou attendre cette
   population, est un choix que l'étape 5 soumet au propriétaire.

Ces trois corrections touchent au coût et à la population, non au droit du
scénario 1, et `cout.py` est cette nuit à la file C, la seule à y écrire :
l'étape 5 les consigne pour elle, ou attend la fin de la vague, plutôt que d'y
toucher hors de sa file.

**Ce qui reste**, et n'appelle pas de confrontation au modèle : les
pensions moyennes par génération et par régime (fiche 6, tableaux 1 et 2),
voisines de ce que `test_controle_ancetre.py` et `test_controle_eacr.py`
confrontent déjà ; l'équivalent carrière complète (fiche 11, tableaux 2 et 3)
et la proratisation par régime ; la polyaffiliation par âge (fiche 13,
graphiques 1 à 3) ; les départs anticipés par génération et par motif (fiche
18, graphiques 1 et 2, tableau 1) ; le profil des allocataires (fiche 28,
tableaux 1 à 5) ; l'érosion relativement au salaire moyen (fiche 4,
graphique 4), que les comptes notionnels, indexés sur les salaires, peuvent
affronter. La revalorisation par régime (fiche 4, tableau 1) est à l'étape 5.
