# Étape 2, septième famille : le salaire annuel moyen, confronté à OpenFisca

**Le 16 octobre 2026, la demande.** La dixième de douze sessions parallèles,
le propriétaire absent : « action 153, étape 2, famille suivante. Le salaire
annuel moyen (153.2), confronté à OpenFisca dans un script et un test
frères. » Aucun fichier des pages ni de la saisie n'est touché, aucun
déplacé ; la liste des textes n'est pas inscrite, le modèle n'est pas touché.

**Ce qui a été lu.** OpenFisca-France-Pension 0.1.3, installé à part (avec un
`setuptools` d'avant 70) : `regime_general_cnav_salaire_de_reference` et ses
trois formules, `build_revalorisation_salaire_cummulee`, les paramètres
`revalorisation_salaire_cummulee`, `reval_s`, `sam` et le plafond annuel ;
`regime_general_cnav_decote_trimestres`. Au dépôt, `salaire_de_reference`,
`moyenne_selon_la_regle` et la fiche `salaire_annuel_moyen`. Le journal de
veille a son entrée (`2026-10-16-action-153-salaire-annuel-moyen.yaml`).

**La convention de traduction**, écrite en tête de
`scripts/fetch/openfisca_salaire_annuel_moyen.py` et portée par le témoin
(`tests/temoins/openfisca_salaire_annuel_moyen.json`) : des non-cadres nés un
1er janvier, au seul régime général, liquidant de 1994 à 2021 ; leurs salaires
année par année, écrits en clair ; au dépôt, chaque année valide les
trimestres que son salaire achète. Le témoin relève aussi ce qu'OpenFisca
forme chaque année — le salaire, le plafond, l'exclusion, le coefficient — et
le nombre d'années qu'il retient : rejouer sa règle sur ce détail rend son
salaire au centime, la rejouer sous nos paramètres rend le nôtre. La règle se
sépare ainsi des coefficients.

**Ce qui est fait.** Douze profils, des générations 1934 à 1955, liquidés de
1994 à 2017 : salaires croissants, décroissants, en dents de scie, dix ans
au-delà du plafond, trois années sous le salaire d'un trimestre depuis 2004 et
deux avant, une carrière plus courte que le nombre retenu, quatre générations,
un départ de 1994 avec une année de trois trimestres.
`tests/test_oracle_salaire_annuel_moyen.py`, au niveau des contrôles : dix
tests, la convention d'abord, et le jumeau JavaScript sur les douze pensions.
Le manifeste a sa ligne (`openfisca_salaire_annuel_moyen_oracle`) ; le
registre trois écarts et un précisé, et son point 153.2 ; la fiche
`salaire_annuel_moyen` son bloc `referents` ; les limites un paragraphe.
L'explication de `tests/test_oracle.py`, qui imputait l'écart du salaire
annuel moyen à la revalorisation de juillet 2022 sur des départs de 2007 à
2018, est corrigée.

**Ce que la confrontation a trouvé.** Rien chez nous, quatre écarts chez
OpenFisca.

| profil | le dépôt | OpenFisca | ce qui tranche |
|---|---|---|---|
| tous ; au départ de 2018, salaires de 1961 | 20,034 | 21,89, d'une série composée | la colonne de la circulaire Cnav du 1er octobre 2017 |
| né en 1938, parti en 1998, à coefficients égaux | plafond de 1960 : 6 840 F | 6 600 F, celui de janvier ; −101,73 € de salaire moyen | la somme des plafonds mensuels (décret n° 60-620) |
| né en 1934, parti en 1994, neuf ans dont un de trois trimestres | 9 654,86 € : la somme sur 35 trimestres | 9 493,69 € : sur neuf ans | circulaires Cnav 1/73 et 95/94 |
| né le 1er janvier 1950, parti le 1er janvier 2012 | douze trimestres de décote | treize : 743 mois au mois moyen de numpy | R. 351-27 |

Les meilleures années, l'écrêtement, l'exclusion des années sans trimestre
depuis 2004, le nombre par génération et la durée d'assurance concordent au
centime. L'oracle a donc trouvé vingt-six erreurs chez OpenFisca, trois à
cette famille, la quatrième, les coefficients, déjà au registre et précisée ;
et quatre chez nous.

**Ce qui reste douteux.** Les plafonds de 1960 et 1961 viennent de la
transcription d'OpenFisca-France (fiabilité « haute ») : les décrets n° 60-620
et n° 61-169 sont à lire au JORF pour les certifier.

**Ce qui devrait s'écrire dans les pages**, que cette session ne touche pas :
rien n'y devient faux.

**Ce qui reste.** L'étape 2 s'achève sur les périodes assimilées, après le
sixième domaine (action 130). Le propriétaire tranche le signalement à
OpenFisca, de vingt-six erreurs désormais.
