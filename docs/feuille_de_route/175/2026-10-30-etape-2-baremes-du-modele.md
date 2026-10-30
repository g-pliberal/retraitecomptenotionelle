# Étape 2 : les barèmes du modèle, confrontés à leurs séries

**Reprise, au 30 octobre 2026.** Faits : le droit commun ; des indépendants,
les taux, les assiettes, le revenu validant, les points, le cumul, les DOM,
le début d'activité, les micro-entrepreneurs ; la minoration, le plafond, le
Smic, Mayotte, les coefficients, le conjoint, les dernières valeurs. Reste :
l'Acre (plafond d'exonération, micro-entrepreneurs avant 2020), l'activité
de faible importance, les tables des DOM de 2007 à 2019 et des micro avant
2020, le prix du point du NRCO avant 2013. À la session du modèle : le RCO de
2008-2009 et sur quatre plafonds dès 1997, huit valeurs de point, l'assiette
minimale avant 1985 et en 2022, Mayotte, et l'assiette d'avant 2007, que
`cotisation_vieillesse_independants` met à relire.

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

**La suite, le même jour.**

- *Les tables de l'ex-RSI*, confrontées à `valeurs_point.csv` et aux fiches :
  le prix et la valeur du point du RCO des artisans (1979-2012), la valeur
  du point du NRCO des commerçants (2004-2012) et ceux du RCI (2013-2019) ;
  l'assiette maximale de chaque régime des indépendants ; le plafond du
  cumul emploi-retraite des artisans et des commerçants ; le plafond de la
  réversion du RCI.
- *Mayotte* : `scripts/fetch/cnav_mayotte.py` lit le Smig mahorais (depuis
  2002), le plafond de la caisse de Mayotte (depuis 2005) et le salaire qui
  y valide un trimestre, et n'écrit `mayotte_smig_et_plafond.csv` que si le
  Smig du 1er janvier, fois 200 heures puis 150 depuis 2017, redonne les
  seize salaires validants publiés. Le Smic mensuel mahorais que la caisse
  publie est ce Smig fois les heures du mois. Les trois barèmes sont
  `branche` sur lui.
- *Des limites* : les assiettes forfaitaires des salariés (apprentis avant
  2014, vendeurs à domicile, employés de maison, artistes, journalistes),
  dans `docs/limites/3-systeme-actuel.md` ; l'assurance volontaire, au champ
  de `caisse_francais_etranger` ; la récupération de l'ASPA sur la
  succession, dans la fiche `minimum_vieillesse`, avec l'action 47.
- *Les dernières valeurs* de 2026, le récapitulatif de la caisse, sont
  celles des séries, AVTS comprise ; l'ASPA d'un allocataire y garde l'écart
  que sa fiche déclare.
- *Les sorts*, depuis la note : 70 barèmes (6 `recoupe`, 3 `branche`,
  58 `limite`, 3 `hors_modele`) et 46 documents (9 `recoupe`, 36 `limite`,
  1 `hors_modele`).

**Ce que la suite a trouvé, à la session du modèle.** Huit valeurs de point
de `valeurs_point.csv`, tirées de l'IPP, ne sont pas celles de la caisse :
le prix du point du RCO en 1997, 1998, 2002 et 2009, sa valeur de service en
1996 et 2007, celle du NRCO en 2008 et 2010 (`ECARTS_POINTS`). D. 635-4,
dans sa rédaction du 26 février 1997 (LEGIARTI000006738337), assied le RCO
des artisans sur quatre plafonds, quand la fiche `rco_artisans` en garde
trois jusqu'en 2004 (`ECARTS_ASSIETTE_MAXIMALE`). La fiche `cssm_mayotte`
valide au Smic national et plafonne au plafond national : la série de
Mayotte est à lui faire lire, les deux moteurs ensemble.

**Ce qui reste** : les 26 barèmes `a_lire` des indépendants. Le début
d'activité (douze barèmes, métropole et DOM), dont il faut lire d'abord, par
période, si les forfaits étaient régularisés sur le revenu ou définitifs
(D. 633-2 et l'arrêté qu'il nomme ; décret n° 78-351, article 3) ; les taux,
les assiettes et l'exonération des DOM ; le plafond d'exonération, la
régularisation de l'aide familial artisan, l'activité de faible importance
des commerçants ; l'ACRE et les DOM des micro-entrepreneurs. Les barèmes des
indépendants de Mayotte vont à l'étape 4, avec son thème.

**Puis les indépendants, le même jour.**

- *Les DOM* : leurs taux de 2020 à 2024, leurs assiettes minimale (2020 à
  2025) et maximale (2020 à 2022) sont ceux de la série et de la fiche du RCI
  (`test_l_independant_des_dom_cotise_aux_taux_et_aux_assiettes_de_la_metropole`).
  Une limite, « indépendants des DOM » (`docs/limites/3-systeme-actuel.md`),
  dit ce que le modèle ne leur applique pas : l'abattement de L. 756-4,
  depuis 2017, l'exonération de L. 756-5, II, et celle des créateurs depuis
  2018, dont les cotisations des deux premières années restent définitives
  sur la base forfaitaire ; le début d'activité des DOM et la table
  d'exonération d'avant 2020 y renvoient. L'édition des DOM garde pour 2022
  une assiette minimale de 11,5 % du plafond, comme la série, quand celle de
  la métropole et le décret n° 2022-1438 portent 4 758 €.
- *Le début d'activité* : depuis 2007, ses forfaits sont des acomptes,
  régularisés sur le revenu de l'année (`hors_modele`). Avant 2007, D. 633-5
  calcule la cotisation « à titre provisionnel » sur un revenu antérieur
  (déclaré l'année précédente en 1985, de l'année précédente en 1995, de
  l'avant-dernière année en 2004), D. 633-6 celle des deux premières années
  sur un forfait, et L. 131-6 prévoit depuis 1995 une régularisation. Que le
  revenu porté au compte soit celui de l'année même, comme le modèle le
  prend, reste à établir : la fiche `cotisation_vieillesse_independants` le
  met à relire, pour la session du modèle.
- *Les micro-entrepreneurs* : leurs taux réduits des DOM et de l'Acre, depuis
  2020, n'entrent pas dans les droits, que la caisse calcule à taux plein
  (circulaire Cnav 2026/12, § 2.3) : `hors_modele`.
- *L'aide familial artisan*, dont la caisse publie le prix du point de
  régularisation : un rachat, `limite` (`ecarts-au-droit-positif.md`).
- *Les sorts* : 24 barèmes (8 `recoupe`, 6 `limite`, 10 `hors_modele`) et
  6 documents (5 `limite`, 1 `hors_modele`).

**Ce qui reste**, des indépendants : l'Acre et l'Accre — le plafond
d'exonération du début d'activité, les tables des micro-entrepreneurs
d'avant 2020 —, que le modèle ne sert pas et que décrit l'exposé « Aide aux
chômeurs créateurs d'entreprise », à déclarer ; l'activité de faible
importance des commerçants retraités avant 2004, avec la fiche du cumul ; les
tables des DOM de 2007 à 2019, à joindre au test ; celles des
micro-entrepreneurs d'avant 2016 et d'avant 2020 ; le prix du point du NRCO
avant 2013.
