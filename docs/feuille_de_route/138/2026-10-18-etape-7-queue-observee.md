# Étape 7, dixième partie : la queue observée de 85 à 98 ans, et la loi raccordée à son dernier quotient

**La demande.** Vague du 18 octobre 2026, session 138.7 : la queue de
mortalité de 85 à 98 ans (première partie, « Ce qui reste », 5 ; deuxième
partie, 2). Les décès par année de naissance et les populations au
1er janvier d'Eurostat vont jusqu'à 99 ans atteints chaque année depuis 1986 ;
la table du dépôt s'arrêtait aux cases de celle d'Eurostat, à 84 ans avant
2014 et 94 ans ensuite, et la loi de Gompertz-Makeham tenait le reste. Aucune
règle du scénario 1 n'est en cause, ni aucun texte : ni veille du droit, ni
entrée au journal.

**Ce que la source donne, lu le jour même.** `demo_mager` et `demo_pjan`
portent chaque âge jusqu'à 99 ans, puis leur classe ouverte : le carré de
98 ans est le dernier qu'encadrent deux parallélogrammes. En France entière,
la population de 99 ans manque au 1er janvier 2006, 2007 et 2010, la classe
ouverte commençant à 99 ans : les tables de 2005, 2006 et 2009 s'arrêtent à
97 ans. Les quotients par âge atteint qu'on en tire retrouvent ceux de
l'INSEE (tableau 69) jusqu'à 99 ans : à l'arrondi près en métropole jusqu'à
98 ans, à 0,77 % près à 99 ans (1996, hommes) ; à 0,21 % près en médiane en
France entière, 2,7 % au plus (2019, femmes, 99 ans), les populations de 2019
ayant été révisées. Contre l'INED, qui donnait 95 à 98 ans de 1986 à 1997,
les carrés neufs concordent à 0,7 % près en médiane, de −14 à +27 % aux
extrêmes, sur des décès qui se comptent par centaines.

**Ce qui est fait.**

- *Le récupérateur* (`scripts/fetch/eurostat_mortalite.py`) calcule les
  carrés au-delà des cases d'Eurostat, jusqu'à 98 ans (`ages_des_carres`,
  `DERNIER_AGE`), et se contrôle contre l'INSEE jusqu'à 99 ans atteints. Sa
  première exécution a montré un panachage : en 2005, 2006 et 2009, le carré
  de 98 ans de la métropole survivait sous la France entière, qui n'en a pas ;
  la France entière remplace désormais l'année entière (`par_annee`).
- *La table* (`quotients_periode.csv`) : 770 quotients de plus — 85 à 94 ans
  de 1986 à 1997, 85 à 98 ans de 1998 à 2013, 95 à 98 ans depuis —, et 96
  corrigés, ceux de l'INED de 95 à 98 ans de 1986 à 1997, qu'Eurostat donne
  désormais. L'INED ne complète plus qu'à partir de 99 ans
  (`PREMIER_AGE_COMPLEMENT`, et un filtre dans `source_quotients_anciens` pour
  un fichier brut d'avant). Son serveur refusant la session, sa trace au
  journal de certification est refaite à la main, de 18 466 à 18 370
  valeurs : son empreinte se recalcule des valeurs que la table garde, la
  même méthode retrouvant l'ancienne au caractère près, et sa date, le
  10 octobre, ne change pas.
- *La calibration* (`_calibrer`, et son jumeau `calibrer`) : le niveau de la
  loi se recalait pour que la table raccordée rende l'espérance à 60 ans de
  l'INSEE. Sous une table qui va jusqu'à 98 ans, la queue ne pèse presque plus
  rien, et la bissection, pour quelques centièmes d'une espérance arrondie au
  dixième, menait la loi à l'absurde : multiplié par 716 en 1986 (femmes),
  par 569 en 2015 (hommes), le niveau faisait mourir tout le monde à 99 ans ;
  ramené à zéro en 1986 (hommes), plus personne ne mourait. Soixante et une
  des lois de 1946 à 1985, où l'INED va jusqu'à 104 ans, l'étaient déjà. La
  forme de la loi reste calée sur e60 et e65 de la loi seule ; son niveau se
  raccorde au dernier quotient observé qui ne vaille ni zéro ni un
  (`_niveau_raccorde`, `niveauRaccorde`, qui passe par `libm.js` depuis le
  rebasage sur l'étape 5 de l'action 161) ; sans table, en 2025, rien ne
  change. `VERSION_CALIBRATION` passe à 3, `TOLERANCE_CALIBRATION` disparaît.
  Le niveau raccordé vaut de 0,1 à 3,1 fois celui de la loi seule.
- *Les tests* : les carrés, la fusion par année et le filtre de l'INED
  (`tests/test_verification.py`) ; la couverture jusqu'à 98 ans, le relais
  entre Eurostat et l'INED, les diagonales de guerre jusqu'à 98 ans, le relais
  de la loi sans marche, la queue contre l'INED, le portage, l'espérance à
  60 ans contre l'INSEE chaque année de 1986 à 2024 (`tests/test_donnees.py`).

**Le raccord, choisi contre l'observation.** De 1986 à 1997, l'INED observe
au-delà de 98 ans : le seul endroit où éprouver une queue. Prolongeant la
table d'Eurostat à 98 ans, chaque règle s'y compare aux 144 quotients de 99 à
104 ans : la loi seule, −19 % en moyenne ; la loi raccordée au quotient de
98 ans, +4,9 % (+3,0 % en médiane) ; raccordée en moyenne sur 94 à 98 ans,
+6,6 % ; une loi de Gompertz ajustée de 85 à 98 ans, +12 %, de 90 à 98 ans,
+7,6 % ; le modèle de Kannisto ajusté de 80 à 98 ans, comme la Human
Mortality Database, +3,4 %. Le raccord au dernier quotient garde la loi du
dépôt et sa continuité, à 1,5 point de Kannisto, qui serait une loi de plus.
La pente de la loi seule (k de 0,07 à 0,11) reste sous celle qu'on observe de
85 à 98 ans (0,11 à 0,14) : c'est ce qui convient à la mortalité des très
vieux, qui croît moins vite au-delà.

**Ce que la table rend.** L'espérance à 60 ans de la table que le modèle lit
ne vise plus celle de l'INSEE, qu'elle rendait par construction : elle la
retrouve à 0,12 an près chaque année de 1986 à 2024, le plus loin en 2022 et
2023, où l'INSEE précède la révision des données — pour 2022, Eurostat
publie 23,0 et 27,3 ans, la table en rend 22,99 et 27,28, l'INSEE en écrit
23,1 et 27,4. L'espérance à 85 ans retrouve celle d'Eurostat à 0,11 an près
depuis 2014, quand l'ancienne queue la dépassait jusqu'à 0,16 an (2024,
hommes : 6,86 pour 6,7) ; celle à 95 ans, qui allait de 2,4 à 4,8 ans selon
les années de 2010 à 2024, se tient entre 2,6 et 2,9 ans pour les hommes, 3,2
et 3,5 pour les femmes.

**Ce que la queue déplace**, mesuré sur la même base, la tête refaite avec et
sans elle.

- *Le diviseur de la population générale*, à 62 ans : les seules générations
  d'avant 1930, dont les grands âges tombent dans les années observées —
  −0,56 % pour 1915, +0,66 % pour 1925 ; rien pour 1930 et après.
- *Les populations particulières*, à toutes les générations : leur facteur se
  cale sur la table générale de 2022 (vingtiles) ou de 2024 (fonctionnaires
  civils de l'État), dont la queue change. Génération 1975, à 64 ans : −0,37 %
  pour le premier vingtile, +0,49 % pour le dernier, +0,28 % pour les
  fonctionnaires civils ; l'écart entre le premier et le dernier diviseur
  passe de 6,15 à 6,36 ans.
- *Les témoins* : aucune pension du scénario 1 ne bouge ; celles des
  scénarios rétroactifs (2, 4 et 6), de −0,14 % en médiane, de −1,12 % (la
  réversion au maximum) à +0,52 % (un sédentaire né en 1912) ; celles des
  prospectifs (3 et 5), d'un centième au plus en médiane, de −0,27 à +0,18 %.
- *La page Coût* : rien pour le système actuel ; pour la proposition, le
  solde moyen de 2026 à 2070 passe de −1,080 à −1,065 % du PIB, la dette de
  2070 de 73,1 à 72,1 %, le creux du coefficient d'équilibre de 0,831 à 0,832.

**Le paquet** : sans lui, le portage lit encore l'ancienne table et les
anciens facteurs, et trente confrontations des deux moteurs de la suite rapide
échouent, de l'ordre de 0,2 % sur les pensions notionnelles. Refait avec le
changement, il s'est perdu au rebasage, la session de l'étape 6 ayant publié
le sien entre-temps (`-merge` garde celui de `main`) ; refait sur `main`, il
est publié juste après.

**Ce qui reste** de l'étape :

1. *Les inaptes de la Cnav*, *2025* à déclarer, *les scénarios 2 à 5* sous la
   variante : inchangés.
2. *La trace de l'INED* au journal de certification se refera d'elle-même au
   prochain passage de son récupérateur, quand son serveur répondra. Les
   tables TD/TV de l'INSEE (`insee_tables_mortalite`, à faire) ne
   couvriraient plus que les âges de 99 à 105 ans.
