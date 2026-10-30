# Étape 2 : les barèmes du modèle, confrontés à leurs séries

**Reprise, au 30 octobre 2026.** Faits : le droit commun, les taux, l'assiette
minimale et le revenu validant des indépendants, les micro-entrepreneurs, la
minoration, le plafond, le Smic, la base des points RVB, les dix éditions des
coefficients, la majoration pour conjoint (35 barèmes, 46 documents). Reste,
dans l'ordre : les indépendants (assiette maximale, début d'activité, DOM,
cotisations volontaires) ; les salaires forfaitaires et l'assurance
volontaire ; Mayotte, par un récupérateur ; le cumul emploi-retraite des
indépendants ; la récupération de l'ASPA, avec l'action 47. À la session du
modèle : le RCO de 2008-2009, l'assiette minimale avant 1985 et en 2022.

**Le 30 octobre 2026, ce qui est fait.**

- *Un trou du registre, comblé d'abord.* Treize pages jointes chargent un
  script de valeurs (`js/declare/dec*.js`) qui déclare, par période ou par
  pays, la page qui porte les valeurs : les taux de cotisation d'avant 2014,
  période par période, les gens de maison, les rachats, les taux de change.
  `cnav_legislation.py` les suit désormais (`script_de_valeurs`,
  `declarees`) : 471 documents de plus, 605 en tout. Un script chargé par une
  autre page que la sienne compose des chemins faux
  (`listes_baremes/change/change/…`) et en déclare que le site n'a pas : une
  page que seul un script déclare n'entre au registre que si le site la sert
  (`sans_les_pages_declarees_absentes`, 475 chemins écartés). 29 références
  gagnent un thème par ces pages.
- *Les confrontations*, `tests/test_cnav_baremes.py` : chaque barème
  recopié, à la version que le registre date, et confronté à la série qu'il
  double ; un écart s'y déclare avec sa raison, et le test échoue s'il change
  ou disparaît. Concordent : le taux de droit commun de 1945 à 2026, sous le
  plafond et sur la totalité, partage compris, et le taux des assurances
  sociales de 1930 ; les taux de base des artisans et des commerçants depuis
  1973, et ceux de leurs régimes complémentaires, RCO, NRCO et RCI, plafond
  propre du RCI compris ; l'assiette minimale depuis 1985 ; le revenu qui
  valide un trimestre depuis 2014 ; les taux globaux, la répartition et les
  seuils des micro-entrepreneurs ; le coefficient de minoration par
  génération ; le plafond de 1931 à 2026, mois par mois, et celui
  d'assujettissement d'avant 1947 ; le Smic horaire depuis 1971 et le Smic
  annuel depuis 2006 ; la base des points RVB des commerçants, un vingtième
  du plafond de janvier ; les montants de la majoration pour conjoint à
  charge depuis 1948.
- *Les dix éditions des coefficients de revalorisation des salaires*
  (octobre 2017 à janvier 2026) : `cnav_revalorisation_salaires.py` les lit
  avec ses circulaires, les confronte depuis 1947, et n'écrit rien si elles
  se contredisent ; relancé, il a réécrit la série à l'identique. Elles sont
  `branche` sur lui.
- *Les sorts* : 21 barèmes et 44 documents `recoupe`, 10 barèmes `branche` ;
  `limite`, renvoyés à la fiche qui le dit, le plafond de ressources de la
  majoration pour conjoint, le point du RCE BTP (`organic_conjoints_batiment`)
  et le point RVB par rachat global (`points_avant_1973_independants`) ;
  `hors_modele`, le plafond d'une période de paie (le modèle le proratise au
  mois) et les taux de maladie des indépendants d'avant 2007.

**Ce que la confrontation a trouvé.**

- *Deux écarts qui changent le calcul, à la session du modèle.* Le RCO des
  artisans : le décret n° 2007-1900 réécrit D. 635-7 à 7,2 % et 7,6 % au
  1er janvier 2008, mais son article 1er (III et IV) fixe « par dérogation »
  7 % et 7 % pour 2008, 7,1 % et 7,5 % pour 2009 ; la fiche `rco_artisans`,
  qui ne lit que l'article codifié, applique 7,2 % et 7,6 % dès 2008.
  L'assiette minimale des indépendants : la caisse applique 200 heures du
  Smic depuis 1973, la série commence en 1985 ; et le décret n° 2022-1438
  fixe pour 2022 une assiette de 4 758 €, de quoi valider trois trimestres,
  quand la série garde 11,5 % du plafond, 4 731 €, qui n'en valident que
  deux — déclarés aussi dans la fiche `assiette_minimale_independants`.
- *Des conventions de la série, déclarées.* 1966 prend le taux du
  1er septembre et 1967 le partage d'octobre (le régime général) ; en 1991,
  la caisse étale sur l'année la hausse de février, 16,16 % pour l'artisan
  et 16,26 % pour le commerçant au 1er janvier, quand la série garde 15,80 % ;
  le NRCO de 2004 est la moyenne de l'année ; le taux de 2012 des
  indépendants, 16,68 % sur l'année, reste à 16,65 %, celui du 1er janvier.
- *Des coquilles de la caisse*, que les tests disent : dans le tableau de la
  minoration, 29,6875 % pour 39,6875 % (né en 1948, onze trimestres) et
  45,5625 % pour 42,5625 % (né en 1946, sept) ; dans l'édition « de 2006 à
  2019 » des taux des indépendants, la ligne de 2014 recopie 2015 (le PDF
  joint dit 17,15 % et 0,20 %) ; dans l'édition de janvier 2024 des
  coefficients, 1955 recopie 2023 (40,887 pour 43,054) ; dans l'assiette
  maximale de 2024, 125 628 € pour 142 526 €, et des cotisations maximales de
  2025 calculées aux taux de 2024.

**Ce qui reste**, dans l'ordre de l'étape, par `grep ',a_lire,'` au thème.

1. *Les indépendants* : l'assiette maximale et sa table de 1973 à 2019 ; le
   début d'activité (douze barèmes et leurs tables), dont il faut lire, par
   période, si les forfaits étaient régularisés sur le revenu ou définitifs ;
   les DOM (taux, assiettes, exonérations) ; les cotisations volontaires, le
   plafond d'exonération, la régularisation de l'aide familial artisan ; les
   micro-entrepreneurs d'outre-mer, l'ACRE, le seuil fiscal, et les tables
   d'avant 2020 et d'avant 2016.
2. *Les salaires forfaitaires* : les apprentis, neuf barèmes depuis 1948, la
   série que la fiche `apprentissage` attend (« parametres: existe: false ») ;
   puis les artistes, les journalistes, les gens de maison (32 pages), la
   vente à domicile (41 barèmes) et les autres catégories, que le modèle,
   sans statut pour elles, ne sert pas ; l'assurance volontaire et sa page
   des montants (`BNL-L_B_MONTANTCV.htm`).
3. *Mayotte* : le Smig, le Smic mensuel, le plafond et le salaire validant
   mahorais, que `cssm_mayotte` dit lui manquer, par un récupérateur ; les
   colonnes mahoraises des barèmes du Smic depuis 2021 vont avec eux.
4. *Le cumul emploi-retraite des indépendants*, le minimum garanti, et la
   récupération de l'ASPA sur succession, que le modèle ne sert pas, avec
   l'action 47.
