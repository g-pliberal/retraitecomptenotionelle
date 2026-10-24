# Étape 3, vingt et unième partie : le poids du militaire, et de chaque caisse, divisé par les têtes de ses cas types

**La demande.** Quatrième vague du 24 octobre 2026, neuf autres sessions en
parallèle, une tâche chacune : celle-ci, le point 2 de « Ce qui reste » de la
note « le militaire dès 48 ans » (même jour), le poids du militaire, maintenant
que la pyramide le compte dès ses 48 ans, le test d'abord. Au propriétaire,
laissés : la forme des départs projetés, l'entrée selon la génération,
l'Ircantec, la table des poids.

**Le défaut.**

- *La part d'un stock, appliquée à des générations.* Le poids d'un cas type
  (`castypes.poids_effectifs`) est la part de ses caisses parmi les
  retraités : celle de l'enquête de la DREES jusqu'en 2024 ; au-delà, celle que
  le COR projette aux caisses de la fonction publique et à celles qui se
  ferment (`EffectifsRetraites.CAISSES_PROJETEES`, militaires compris : la
  note du militaire la disait reconduite, elle ne l'est pas), le bord pour les
  autres. `cout._masses` l'applique à chaque génération entière, à toutes ses
  cohortes parties : les têtes d'un cas type sont sa part fois l'effectif des
  âges qu'il passe en retraite. Pour un poids d'un, la pyramide de 2024 en
  donne 29,7 millions au militaire, radié à 48 ans, 26,2 à l'agent de
  conduite, 21,7 à l'agent des IEG et au super-actif de l'État, de 13,2 (le
  libéral) à 19,0 millions (le salarié au SMIC) aux autres cas types. Avant
  le calage par groupe, le militaire faisait ainsi 2,85 % des retraités de la
  grille en 2024 pour un poids de 1,62 % ; parmi ceux de l'État, 29,5 % pour
  18,7 % à la DREES, de 29 à 33 % de 2010 à 2030 pour 18,7 à 20,9 %, et
  44,5 % en 2070 pour 32,8 % au COR. L'agent de conduite, 1,03 % des têtes
  en 2025 et 0,16 % en 2070, quand le COR fait passer sa caisse de 0,65 à
  0,16 % des retraités : la grille le faisait reculer plus vite que le COR,
  son départ précoce s'effaçant avec les générations embauchées après 2020.
- *Ce que le dépôt en savait.* Les parts déclarées des caisses partagées sont
  des parts de départs — la CNRACL, les civils de l'État, la Cnav : « le poids
  d'un cas type est sa part de la caisse à la liquidation, sa mortalité faisant
  ensuite le stock » (`castypes.py`). La règle tenait à l'intérieur d'une
  caisse, non entre les caisses. `scripts/age_conjoncturel.py` le disait de son
  âge de départ (« Les poids sont des STOCKS », réserve 1), sans suite pour la
  page.

**La correction** (`poids_effectifs(..., tetes=)`, `cout._tetes_par_poids`).
Chaque caisse se divise par les têtes que la pyramide donne à ses cas types,
l'année même, pour un poids d'un, celles d'une caisse partagée pesées de leurs
parts : la grille compte à chaque caisse, chaque année, la part des retraités
qu'elle a, et ses cas types se la partagent toujours selon leurs départs. Le
poids d'un cas type devient une part de chaque génération, une part de ses
départs. Au-delà de 2070, dernière année de la pyramide, les têtes de 2070 :
l'engagement acquis et les facteurs de la dépense demandent leurs poids
jusqu'à l'horizon, et les effectifs des caisses y sont reconduits. Partout où
le dépôt pèse des retraités : la page Coût, l'engagement acquis, le coût des
avantages, le bilan du compte, les facteurs de la dépense, la grille large,
`scripts/cout_avantages.py` ; `_ponderation` refuse désormais de peser des
retraités sans les têtes. La grille large donne à chaque variante sa
pseudo-caisse, que ses seules têtes diviseraient : elle les divise par celles
de ses caisses réelles, la moyenne des têtes des variantes qui réclament
chacune, pesées de leurs parts positives (`tetes_des_caisses_reelles`, que
`calculer_cout` reçoit par `tetes_par_poids`), et la grille du dépôt redonne
la page. Les cotisants gardent la part de leurs caisses : le biais de ceux
de moins de cinquante ans, que la pyramide ne compte pas, est au propriétaire
(étape 19, « Trouvé en chemin » de la note du 14 octobre).

**Ce qui est fait.**

- *Les tests*, vus rouges pour la raison attendue avant le code : une caisse
  divisée par les têtes de ses cas types, posé à la main (300 et 100
  retraités, 1 000, 2 000 et 1 000 têtes, des poids de 0,84, 0,12 et 0,04), et
  les têtes d'un cas type, ses cohortes déjà parties, celles de 2070 au-delà
  (`tests/test_cout.py`) ; les militaires de la grille à la part que la table
  H de l'EACR leur donne parmi les retraités de l'État en 2024, 18,7 %
  (376 810 pensionnés pour 1 641 380 civils), à un point près : 30,1 % avant,
  19,2 % après, le calage par groupe donnant au militaire, qui ne sert que
  l'État, un coefficient un peu plus fort qu'aux civils, qui servent aussi le
  privé avant d'y entrer, 1,63 pour 1,57 (`tests/test_controle_eacr.py`) ;
  chaque caisse réelle de la grille large divisée par les têtes de ses
  variantes, posé à la main, et la grille du dépôt qui redonne la page, rouge
  avant `tetes_des_caisses_reelles`, à 0,06 de son plus grand indicateur
  (`tests/test_grille_large.py`).
- *Ce que la correction déplace, dit dans chaque test qu'elle touche* : les
  cliquets des groupes que la grille ne suit pas encore descendent, deux
  tolérances, la dérive et le cliquet de la reconstitution remontent, chacun
  avec sa raison (`tests/test_cout.py`) ; la convention égalitaire est un
  plancher pour les deux scénarios ; les bénéficiaires de la garantie
  reculent en part des retraités qui l'attendent, non plus en nombre ; l'âge de
  départ de chaque génération, pesé à ses poids (`tests/test_facteurs_depense.py`) ;
  l'âge moyen de liquidation de 2024 (`tests/test_controle_eacr.py`) ; la
  borne de l'affirmation « Point de vigilance » de la page Coût, six points et
  demi (`tests/test_affirmations.py`, `data/reference/site/affirmations.yaml`) ;
  le contrefactuel des âges par catégorie (`tests/test_cout_age_depart.py`).
- *La prose* : `README.md` et `docs/limites/5-bis-cout-agrege.md`, § 2, disent
  la division, et que la convention égalitaire faisait des deux scénarios un
  plancher ; elles faisaient du scénario 2 un plafond. Les commentaires de
  `scripts/age_conjoncturel.py` et `scripts/age_depart_csp.py`, qui disaient
  peser comme la page, disent qu'ils pèsent par le stock.

**Ce que ça déplace**, mesuré sous la référence, avant et après, sur `main`
à 07393af.

- *La page Coût.* La proposition (système 6) passe de 8,83 à 8,93 % du PIB en
  2030, de 9,68 à 9,75 en 2050, de 8,05 à 8,07 en 2070 ; le système 2 de 3,76
  à 3,83, de 4,52 à 4,60, de 4,65 à 4,73. Le système actuel, qui part de la
  dépense du COR, et le rapport de recettes ne bougent pas.
- *L'écart au COR à l'horizon, groupe par groupe.* La dépense de la fonction
  publique d'État passe de +26,5 à +17,6 %, sa pension relative de +6,1 à
  +4,9 % ; la dépense de la CNRACL de +10,3 à +8,4 % ; celle des régimes
  spéciaux de −32,5 à −4,5 %. Celle des non-salariés de +7,5 à +10,8 %, des
  complémentaires de +6,4 à +7,9 %, de LURA de +2,4 à +3,1 % : partis après
  les autres, l'artisan, le libéral et le contractuel de l'Ircantec pèsent
  plus en 2025 — 5,2, 2,0 et 9,1 % des têtes au lieu de 4,6, 1,6 et 8,1 —, et
  la reconduction de la part de leurs caisses davantage dans leurs groupes. La
  dérive de 2070 passe de 1,057 à 1,060 ; la reconstitution du passé, en
  2009, de −10,6 à −11,0 %, l'écart des têtes de −5,0 à −5,5 % : la part des
  départs précoces, qui reculait de 2009 à 2024, freinait d'autant la
  croissance des têtes du modèle.
- *La garantie.* Ses bénéficiaires reculaient de 0,6 % de 2025 à 2070, ils
  croissent de 0,2 % : en 2025, les départs précoces pèsent moins, et le
  facteur passe de 0,7440 à 0,7495.
- *La convention égalitaire.* Le rapport cumulé du scénario 2 vaut 0,1990 à
  poids égaux, 0,2012 aux effectifs (0,1953 avant) ; celui du scénario 4,
  0,4205 et 0,4642 (0,4582). Elle surreprésente les départs très précoces, et
  fait des deux scénarios un plancher.
- *L'EACR, en 2024.* L'âge moyen de liquidation de la grille passe de 61,9 à
  62,2 ans, pour 63,6 publié ; le militaire fait 1,8 % de ses nouveaux
  retraités au lieu de 2,8 %. Ses retraités de moins de 60 ans restent à
  35,4 % des siens : leur part ne tient qu'à ses âges.
- *L'âge de départ de chaque génération*, pesé à ses poids, ceux de l'année
  où elle atteint 65 ans (note « l'âge de départ de chaque génération »), de
  1975 à 2000 : la grille de `cout.py` part à 64,0 ans au lieu de 63,8, à
  −0,53 an du COR au lieu de −0,73, chaque génération avant lui ; l'entrée
  selon la génération à +0,19 au lieu de +0,01 ; les départs avec décote à
  −0,07 au lieu de −0,26 ; la décote selon la génération à −0,18 au lieu de
  −0,37 ; l'entrée selon la durée validée à −0,02 au lieu de −0,21. À 61 ans,
  les générations 1955 à 1960 sont parties à 16 à 20 % dans la grille, au lieu
  de 17 à 22 ; à 62 et 63 ans, en 2024, 34 et 54 % au lieu de 36 et 57.
- *Le contrefactuel des âges par catégorie* (`scripts/cout_age_depart.py`) : il
  déplace les scénarios notionnels de −0,07 à −0,16 point de PIB à l'horizon,
  au lieu de −0,01 à −0,10, et le système actuel de +0,31 au lieu de +0,36. La
  grille compte désormais à chaque caisse les retraités qu'elle a, quel que
  soit l'âge où ses cas types partent : un départ plus précoce n'en ajoute
  plus, et le compte notionnel ne s'en rattrape plus par le nombre. La borne
  absolue, deux dixièmes, tient ; la relative passe du tiers aux trois
  cinquièmes du système actuel. La raison chiffrée de ne pas corriger les âges
  s'en affaiblit : au propriétaire, avec l'entrée selon la génération.

Les tables figées du paquet, le bilan figé, les témoins et les chiffres
ancrés des autres documents, GitHub les refait.

**Le flux, qu'un poids par année ne tient pas.** La table H de l'EACR compte,
pour l'État, les pensionnés et les départs de chaque année : les militaires
font 18,7 à 19,6 % de ses pensionnés de 2015 à 2024, 14,9 à 17,7 % de ses
départs. Corrigée, la grille leur donne, avant le calage par groupe, la part
des pensionnés, et 11,8 à 13,5 % des départs de 2010 à 2023 ; la part du
stock leur en donnait 19,2 à 22,2 %. Le rapport des pensionnés aux départs,
de 32,9 à 39,2 chez les militaires de l'EACR, est celui de la grille, 35,8 ;
chez les civils, de 27,3 à 36,4, quand la grille en donne une vingtaine à
leurs cas types, celui de la pyramide. Un poids par année, le même pour toutes les générations vivantes,
ne peut pas tenir les deux à la fois ; la page compte la dépense, que fait le
stock, et c'est lui que les poids tiennent désormais.

**Ce qui reste**, de cette partie ; les points 1 de la note « le militaire
dès 48 ans », 3 de la note « l'âge de départ de chaque génération » et 1 de
la note « l'entrée dans l'emploi », au propriétaire, et les naissances de
l'année dans `cout.py`, le taux effectif, demeurent.

1. *Au propriétaire, avec l'entrée selon la génération* : ce qui la fondait a
   bougé. Pesée de la part des départs de chaque génération, la grille de
   `cout.py` ne précède plus le COR que d'un demi-an ; l'entrée selon la
   génération le dépasse de deux dixièmes, l'entrée selon la durée validée
   le rejoint, à deux centièmes près. Et la raison de ne pas corriger les
   âges par catégorie s'affaiblit : le contrefactuel déplace les scénarios
   notionnels de près de deux dixièmes de point.
2. *Les militaires de moins de 60 ans*, 35,4 % des siens dans la grille, 31,5
   % au jaune hors invalidité : le cas type part à 48 ans et demi, quand les
   officiers partent plus tard. Un second cas type militaire, l'officier, le
   départagerait ; au propriétaire, avec la table des poids.
3. *Pour une session du site* (action 173) : la table des poids de la page
   Coût (`coutDetailPoids`) montre désormais, dans sa colonne « Retraités »,
   des parts de départs, que sa phrase dit encore la part des retraités de
   chaque caisse ; à dire que chaque caisse se divise par les têtes de ses cas
   types.
4. *Le flux des civils de l'État* : un poids par génération, et non par année,
   tiendrait le stock et le flux ensemble. Un choix de modèle, au propriétaire.
5. `scripts/age_conjoncturel.py` et `scripts/age_depart_csp.py` pèsent
   toujours leurs départs par le stock, faute de la grille : leur réserve
   tient.
