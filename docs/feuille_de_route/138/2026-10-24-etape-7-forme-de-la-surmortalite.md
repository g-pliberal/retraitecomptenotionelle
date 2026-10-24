# Étape 7, seizième partie : la forme de la surmortalité des inaptes et des ex-invalides

**La demande.** Lot du 24 octobre 2026 : onze sessions en parallèle, une
tâche chacune, sur la demande du propriétaire ; celle-ci, l'action 138,
étape 7, le point 2 de « Ce qui reste » de la note du 23 octobre (« la part
ouverte à la bascule ») : la forme de la surmortalité des inaptes et des
ex-invalides de la Cnav (onzième partie, point 2). Ni les décimales du
coefficient au-dessus de un, aux pages, ni les départs qui suivent
l'espérance de vie, au propriétaire. Aucune règle du scénario 1 n'est en
cause : ni veille du droit, ni entrée au journal.

**Ce que la source donne.** Le Cadr'@ge n° 40, déjà au dépôt
(`esperances_vie_pensions_cnav.csv`) : l'espérance de vie du moment de 2017
à 62, 65, 70, 75, 80 et 85 ans, par sexe et par type de pension. Prisme
applique à ses retraités des quotients à chaque âge, que la Cnav ne publie
pas : six espérances, c'est tout ce que la source dit de la forme.

**Ce qui est fait.**

- *La forme* : `DonneesMortalite.facteurs_par_age`. Un facteur sur la force
  de mortalité de la table générale par tranche d'âge, de chaque âge publié
  au suivant, la première prolongée avant 62 ans, la dernière jusqu'au bout
  de la table ; calées de la plus âgée à la plus jeune, chacune sur
  l'espérance publiée à son âge, sur la table du moment de 2017, les plus
  âgées déjà calées ; tenues constantes ensuite sur toutes les années, comme
  l'était le facteur unique. La table corrigée rend les six espérances
  publiées, au centième, des trois types et des deux sexes. Le facteur
  unique, calé à 65 ans, rendait aux inaptes 18,55 ans à 62 ans pour 18,2
  chez les hommes, 23,71 pour 23,4 chez les femmes, et à 85 ans 4,82 pour
  6,3, 6,50 pour 8,2 ; aux ex-invalides, 17,04 pour 16,7 et 23,29 pour 23,1
  à 62 ans, 4,19 pour 5,7 et 6,27 pour 7,3 à 85.
- *Les facteurs*, sur la table générale du dépôt :

  | | avant 65 ans | 65 | 70 | 75 | 80 | 85 et plus | facteur unique |
  |---|---:|---:|---:|---:|---:|---:|---:|
  | Inaptes, hommes | 2,06 | 2,06 | 1,70 | 1,39 | 1,28 | 0,98 | 1,48 |
  | Inaptes, femmes | 2,20 | 2,18 | 1,73 | 1,49 | 1,36 | 0,89 | 1,34 |
  | Ex-invalides, hommes | 2,42 | 2,27 | 2,14 | 1,79 | 1,45 | 1,15 | 1,81 |
  | Ex-invalides, femmes | 1,96 | 1,79 | 1,70 | 1,68 | 1,36 | 1,10 | 1,42 |

  La surmortalité s'éteint avec l'âge, comme la Cnav le dit : deux fois la
  force de la table générale avant 65 ans, la même à 85 ans à un sixième
  près. Les espérances publiées sont arrondies au dixième : en déplacer une
  d'un vingtième d'année déplace le facteur de la première tranche, la plus
  courte, de 0,08 à 0,14, ceux des autres de 0,01 à 0,08. Les pensions
  normales, qu'aucun cas type ne suit (les quatre carrières du privé vivent
  au rythme de leur vingtile), en tirent des facteurs de 0,47 à 0,91 qui ne
  montent pas tous vers un, 0,85 à 75 ans après 0,88 chez les hommes, 0,71
  après 0,81 chez les femmes : déplacées chacune d'un vingtième d'année au
  plus, dans leur arrondi, les espérances publiées les feraient tous monter.
- *La règle* (`survie_annuelle`) : chaque cellule (âge entier × millésime)
  reçoit le facteur de la tranche de son âge ; une année qui franchit l'âge
  d'une tranche en partage l'exposition, comme elle partage déjà celle de
  deux millésimes. Sous un facteur unique, l'arithmétique est la même,
  opération par opération : le diviseur, les vingtiles et les pensionnés
  civils de l'État ne bougent pas d'un bit, ni le portage.
- *Le portage n'en sait rien* : `facteur_population` refuse une population
  publiée à plusieurs âges, et `facteurs_populations`, ce que le paquet
  porte au navigateur, la laisse de côté. Le portage ne sert qu'un facteur
  par population, celui du diviseur, et le formulaire n'offre au diviseur
  aucun type de pension de la Cnav ; seul le coût, que le navigateur ne
  calcule pas, fait vivre l'inapte et l'ex-invalide de la grille
  (`CasType.mortalite`, `cout._survies`). Les six facteurs uniques de la
  Cnav sortent du paquet ; une ligne de commentaire dans `mortalite.js` le
  dit.

**Ce que la forme déplace**, les tables du coût d'avant (`4ce44e4`) contre
celles que `python scripts/regenerer.py` en refait. L'inapte de la
génération 1960, parti en 2022, vit 22,08 ans en moyenne des deux sexes, au
lieu de 22,30, quand la table générale de génération en donne 25,04 ; parti
en 2050, 25,50 au lieu de 25,21 : la mortalité baissant, sa vie se passe
davantage aux âges où sa surmortalité s'éteint. Trente ans après son départ
de 2022, il survit à 0,82 fois la population générale, au lieu de 0,67.
L'ex-invalide, de même : 21,10 ans au lieu de 21,26 pour un départ en 2022,
24,47 au lieu de 24,20 en 2050. Le système actuel reste calé sur la dépense
du COR, 15,30 % du PIB en 2070 ; sa dérive reste à 1,0199 en 2030, passe de
1,0314 à 1,0301 en 2050, de 1,0549 à 1,0530 en 2070. La proposition passe
de 8,848 à 8,850 % du PIB en 2030, de 9,702 à 9,701 % en 2050, de 8,095 à
8,089 % en 2070 ; son solde moyen de 2026 à 2070, de −1,0285 à −1,0271
point ; sa garantie en 2070, de 13,95 à 13,99 Md€ constants, les petites
pensions survivant davantage aux grands âges. Le scénario 2 passe de 4,668 à
4,666 % du PIB en 2070, le scénario 4 de 10,293 à 10,288 %. Le poids de 2024
que la page affiche pour le salarié au SMIC, qui compte l'inapte et
l'ex-invalide, passe de 20,58 à 20,60 %.

Les 892 témoins de simulation ne bougent pas ; 29 des 79 rendus de page
changent, par les chiffres du coût qu'ils citent — l'engagement acquis passe
de 498 à 497 % du PIB ; à la pension de la proposition du simulateur par
défaut, il manque 143 € par mois au lieu de 144 pour être financée. Aucun
cliquet ni aucune tolérance du coût n'a bougé :
`test_cout.py`, `test_facteurs_depense.py`, `test_affirmations.py`,
`test_mortalite_population.py` et `test_controle_eacr.py` passent sur les
tables refaites, 869 tests, comme les confrontations légères et la suite du
site.

**Les tests** (`tests/test_donnees.py`) :
`test_les_inaptes_de_la_cnav_vivent_au_moins_quatre_ans_de_moins`, récrit :
les six espérances publiées de chaque type et de chaque sexe, au centième, au
lieu de celle de 65 ans et de la limite du facteur unique ; vu rouge sur la
première, 22,72 ans pour 22,9 à 62 ans aux pensions normales des hommes.
`test_la_surmortalite_des_inaptes_et_des_ex_invalides_suit_l_age`, neuf : les
tranches aux âges publiés, la surmortalité forte avant 70 ans et presque
éteinte à 85, le refus du facteur unique et le paquet qui n'en porte rien ;
la règle posée à la main — une cellule de 2040 à son facteur, l'année de 64
ans et demi à cheval sur deux tranches, la courbe de génération d'un inapte
parti en 2030 sur trente ans. Vu rouge, `facteurs_par_age` manquant.

**Le registre** : `prisme` passe à `repris` au chantier 138.7 ; chaque type
de pension de la Cnav vit à son rythme dans la grille, et à chaque âge que
la Cnav publie.

**Ce qui reste**, dans l'ordre :

1. *Aux pages, le coefficient au-dessus de un* (douzième partie, point 2) :
   une session des pages.
2. *La limite, à la fin de l'étape* (note du 23 octobre, points 3 et 4) :
   elle pourra dire, de l'inapte et de l'ex-invalide, une surmortalité par
   tranche d'âge, calée sur les six espérances de 2017 et tenue constante
   dans le temps, comme le facteur des vingtiles.
3. *Au propriétaire* : les départs qui suivent l'espérance de vie.
