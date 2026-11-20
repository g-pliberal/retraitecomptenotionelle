# Les années 1930 à 1944 comptent à la durée du régime général

Le 20 novembre 2026, sur le constat d'une vérification de la couverture des
générations les plus âgées, et selon la règle du propriétaire (« on corrige
tout ce qui est faux »).

**Lu**, dans l'index LEGI. R. 351-9 du code de la sécurité sociale, rédaction
de 1985 à 2014 (LEGIARTI000006749353) : « Les périodes d'assurance accomplies
du 1er juillet 1930 au 31 décembre 1935 comptent pour autant de trimestres
d'assurance que […] », puis de 1936 à 1941 et de 1942 à 1945, à la suite des
périodes d'après. Avant 1985, la même phrase à l'article 71 du décret
n° 45-0179 (LEGIARTI000006760608, rédaction de 1983, la seule que l'index
porte), parmi les « trimestres d'assurance valables pour le calcul de la
pension » ; l'article 74 du même décret, rédaction de 1977
(LEGIARTI000006760676), compte les périodes « depuis le 1er juillet 1930 ».
Aux salariés agricoles, l'article 58 du décret n° 50-1225
(LEGIARTI000006774032) : un trimestre par cinquante jours de travail, du
1er juillet 1930 au 31 décembre 1945. Avant 1983, la règle est présumée la
même : ses montants sont écrits en anciens francs, et les 150 trimestres
exigés depuis 1975 n'étaient atteignables qu'avec ces années.

**Le moteur** route ces années vers le régime « assurances sociales », qui
sert 0 €. Leurs trimestres entraient à la durée tous régimes, donc au taux,
mais pas au numérateur de la proratisation du régime général : 128/150 à qui
avait cotisé de 1932 à 1976.

**Corrigé.** La fiche `assurances_sociales.yaml` nomme les régimes qui
reprennent sa durée (`duree_reprise_par: [regime_general, msa_salaries]`), et
la liquidation ajoute ces trimestres à la durée du régime qui liquide
(`regimesRepris`, `moteur/js/droit/liquider.js`) : au numérateur de la
proratisation, et aux durées que lit le minimum contributif. Quand la carrière
liquide les deux régimes, un seul les reprend, celui où l'assuré est entré le
premier. Le plafond de 22 trimestres de 1930 à 1935 tenait déjà : deux
trimestres en 1930, quatre ensuite.

**Ce qui bouge.** Né en 1912, salarié de 1932 à 1976, parti à 65 ans en 1977,
au salaire moyen : 150/150 et 3 302,00 € par an, le maximum des pensions, au
lieu de 128/150 et 3 096,23 €. Née en 1924, salariée de 1938 à 1950, partie à
65 ans en 1989 : 52/150 au lieu de 24/150. Né en 1922, parti à 60 ans en
1982 : 150/150 au lieu de 148/150. Dix des 937 témoins montent au scénario 1,
de 0,3 % à 17,5 %, 5,6 % en médiane ; aucun ne bouge aux scénarios 2, 4 et 6.
Le coût suit de peu : la dépense des systèmes notionnels baisse de 0,3 % au
plus la première année, le modèle se calant sur la dépense observée.

**Le test.** `test_les_annees_des_assurances_sociales_comptent_a_la_duree_du_regime`
(`tests/test_salaire_annuel_moyen.py`), posé à la main depuis le texte. Celui
de la loi Boulin (`tests/test_simulateur.py`) supposait que « le régime
commence en 1945 dans le modèle » : ses carrières commencent désormais en 1945.

**Reste.** Le salaire de référence d'une pension liquidée avant 1955, dont
les dix dernières années remontent avant 1945 ; le partage exact des
trimestres d'avant 1945 entre les deux régimes de salariés, selon le métier
de l'époque ; la rente des assurances sociales, servie pour zéro.
