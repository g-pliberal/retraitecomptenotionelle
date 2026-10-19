# Étape 7, onzième partie : les inaptes de la Cnav, dans la grille du coût

**La demande.** Vague du 19 octobre 2026, session 6 de la première salve,
lancée par la session de suivi sur la demande du propriétaire (« Lance les
sessions qui n'ont pas besoin de moi ») : le premier point de « Ce qui reste »
de la neuvième partie (note du 17 octobre), que la dixième reportait — les
inaptes de la Cnav, que Prisme fait vivre à part (registre, `prisme`,
chantier 138.7) et que la grille n'avait pas. Aucune règle du scénario 1
n'est en cause : la fiche `inaptitude_au_travail` sert déjà le taux plein à
l'inapte dès l'âge légal (L. 351-8, 2°), et le cas type ne fait que se
déclarer inapte ; ni veille du droit, ni entrée au journal.

**Ce que les sources donnent, lues le jour même.**

- *La mortalité* : le Cadr'@ge n° 40 de la Cnav (Goujon, juin 2019, données
  chiffrées du graphique 2) donne l'espérance de vie du moment de 2017 à 62,
  65, 70, 75, 80 et 85 ans des retraités du régime général par sexe et par
  type de pension, tirée des décès et des stocks du SNSP. À 62 ans, les
  inaptes vivent 4,7 ans de moins que les pensions normales chez les hommes
  (18,2 contre 22,9), 4,1 chez les femmes (23,4 contre 27,5) ; les
  ex-invalides, 6,2 et 4,4. C'est la mortalité que Prisme applique à ses
  retraités (COR, document n° 9 de mars 2020, p. 14 du PDF, qui y renvoie).
  L'ancienne adresse, sous `statistiques-recherches.cnav.fr`, ne répond plus ;
  le document est sous `statistiques-recherche.lassuranceretraite.fr`.
- *La part* : les séries labellisées de la Cnav (classeur des nouveaux
  retraités, février 2026) comptent les nouveaux retraités de droit direct
  du régime général par sexe et type de pension, de 2003 à 2024. De 2020 à
  2024, 284 204 des 3 397 470 partent pour inaptitude, 8,4 %, et 298 196 en
  ex-invalides, 8,8 %. Les trois types font le total, et les deux sexes
  l'ensemble, à l'unité. Le classeur du stock donne 8,2 % de pensions pour
  inaptitude et 6,4 % d'ex-invalides au 31 décembre 2025, 13,0 et 5,9 % en
  2009, quand les catégories « assimilées » vivaient encore.
- *La carrière* : l'étude 2023-014 de la Cnav (Couhin et Floderer, février
  2023, tableaux 2 à 4) décrit les nouveaux retraités de 2021 pour
  inaptitude : 56 914 ex-invalides, 19 358 anciens titulaires de l'AAH et
  27 332 autres inaptes. Ces deux derniers groupes ensemble : un premier
  trimestre à vingt ans, 116 trimestres, un salaire annuel moyen de 68 % du
  SMIC, un départ à 62 ans pour deux sur trois.

**Ce qui est fait.**

- *Les données* : `mortalite/esperances_vie_pensions_cnav.csv`, les
  trente-six espérances du Cadr'@ge ; `regimes/nouveaux_retraites_cnav.csv`,
  le flux par type de pension, extrait du classeur au format Excel 97 que la
  bibliothèque standard ne lit pas, et qu'aucun calcul ne lit
  (`memoire.HORS_DU_MODELE`) ; deux jeux au registre des sources,
  `cnav_cadrage_40` et `cnav_series_labellisees`.
- *Les populations* : `DonneesMortalite` lit le troisième fichier, et chaque
  type de pension y devient une population, `cnav_pension_normale`,
  `cnav_inaptitude`, `cnav_ex_invalide`, dont le facteur rend l'espérance à
  65 ans publiée sur la table générale de 2017, comme celle des pensionnés
  civils de l'État. Le facteur des inaptes vaut 1,48 pour les hommes et 1,34
  pour les femmes ; celui des ex-invalides, 1,81 et 1,42 ; celui des pensions
  normales, 0,87 et 0,81 : la Cnav mesure ses pensions normales plus
  longévives que la table du dépôt, d'un an à 65 ans pour les hommes (20,4
  contre 19,35), d'un an et demi pour les femmes (24,7 contre 23,20).
- *Le cas type* : `CasType.inaptitude`, que la carrière déclare
  (`invalidite`), et `CasType.mortalite`, la population qui le fait vivre sur
  la page Coût quand ce n'est pas celle de son diviseur. L'inapte de la Cnav
  (`castypes.INAPTE_CNAV`), variante du salarié au SMIC à qui la page
  rapporte son poids, travaille à 70 % du SMIC de vingt à quarante-neuf ans,
  puis n'a plus d'activité : 116 trimestres. Il part à 60 ans né en 1950, à
  62 né en 1955 et après, que la réforme de 2023 lui garde ; sans
  l'inaptitude, la même carrière attendrait 65 puis 67 ans. Sous la
  proposition, il part à l'âge légal de tous, comme le README le veut.
- *Sa part* : 8,37 % de la Cnav (`PART_INAPTES_CNAV`), la part du flux, comme
  pour l'agent actif de la CNRACL : le poids d'un cas type est sa part de la
  caisse à la liquidation, sa mortalité faisant ensuite le stock. Les quatre
  carrières du privé se partagent le reste, 22,9 % chacune ; la page Cas
  types, qui n'a pas l'inapte, garde le partage égal. Son poids de 2024 sur
  la page Coût est de 4,6 % ; celui du salarié au SMIC passe de 13,5 à
  12,4 %.
- *Sa survie* (`cout._survies`) : celle de `cnav_inaptitude` rapportée à la
  population générale, et non celle du vingtile de son salaire, que son
  diviseur garde ; à nombre de décès égal, comme les autres. Sous la table
  commune, la pyramide seule, comme tous : l'interrupteur reste celui du
  diviseur.
- *La population de l'étape 14* (`scripts/grille_large.py`) : son gabarit
  du salariat privé prend toute la Cnav, et l'inapte la lui cède, comme les
  quatre carrières dont il est la variante (`reference_population`, une
  ligne). La population ne change pas ; ses inaptes restent à faire, à sa
  manière (étape 14, « Reste »).

**Ce que l'inapte déplace**, mesuré sur `da51e82`, la grille d'avant contre
celle d'après. Le système actuel reste calé sur la dépense du COR, 15,30 % du
PIB en 2070 ; sa dérive, ce que ses masses font seules, passe de 1,0172 à
1,0177 en 2030, de 1,0262 à 1,0255 en 2050, de 1,0504 à 1,0483 en 2070. La
proposition passe de 8,922 à 8,928 % du PIB en 2030, de 9,779 à 9,798 % en
2050, de 8,168 à 8,186 % en 2070 ; son solde moyen de 2026 à 2070, de −1,104
à −1,119 point ; sa garantie en 2070, de 13,72 à 13,79 Md€ constants. Le
scénario 2 passe de 4,683 à 4,711 % du PIB en 2070, le scénario 4 de 10,421 à
10,435 %. L'inapte part trois ans plus tard sous la proposition ; mais
l'année de pension que son compte lui sert vaut de 0,75 à 0,83 de celle du
droit en vigueur pour les générations 1965 à 1980, quand celle du salarié au
salaire moyen en vaut de 0,63 à 0,75, et la garantie complète la sienne : la
proposition s'en trouve un peu plus chère.

**Les tests** : `test_les_inaptes_de_la_cnav_vivent_au_moins_quatre_ans_de_moins`
(`test_donnees.py`), les trente-six espérances relues, les écarts d'au moins
quatre ans, les facteurs, et la limite du facteur constant ;
`test_l_inapte_de_la_cnav_part_au_taux_plein_des_l_age_legal`
(`test_moteur.py`), sa carrière et son départ, avec et sans l'inaptitude ;
`test_l_inapte_porte_la_part_de_la_cnav_que_ses_departs_lui_donnent` et
`test_l_inapte_vit_au_rythme_des_inaptes_de_la_cnav` (`test_cout.py`), le
flux recoupé par ses totaux, les parts et les poids, la survie et
l'interrupteur. Le test de la CNRACL disait la Cnav partagée également : elle
l'est entre ses quatre carrières du privé, une fois ses inaptes servis. Deux
cliquets de `test_l_ecart_au_cor_groupe_par_groupe` descendent, leur écart
au COR à l'horizon étant passé d'un point sous eux : la dépense de la FPE, de
0,23 à 0,22 (de +22,4 à +22,0 %), celle de la CNRACL, de 0,12 à 0,11 (de
+11,2 à +10,9 %). D'autres écarts bougent sans cliquet : la pension relative
de la Cnav, de +0,5 à −0,1 % ; la dépense des non-salariés, de +3,1 à
+6,0 %.

**Le registre** : `prisme` reste `a_reprendre` au chantier 138.7 ; reste
l'ex-invalide.

**Ce qui reste** du point, dans l'ordre :

1. *Les ex-invalides de la Cnav*, 8,8 % du flux, que les quatre carrières
   du privé portent encore : leur mortalité (`cnav_ex_invalide`) et leur part
   (`DEPARTS_CNAV_2020_2024`) sont au dépôt ; restent leur carrière — la
   pension d'invalidité, vers cinquante ans, et ses trimestres assimilés,
   171 trimestres en 2021 pour un salaire annuel moyen de 97 % du SMIC — et
   ce que la proposition leur fait : l'invalidité ne cotise pas, et le compte
   se liquide à l'âge légal de tous.
2. *La forme de la surmortalité* : un facteur constant, calé à 65 ans, rend
   l'espérance des inaptes à 62 ans à quatre dixièmes près (18,55 pour 18,2
   chez les hommes), mais les fait mourir trop vite au-delà de 80 ans, où la
   Cnav les voit rejoindre la population générale (4,8 ans à 85 ans pour 6,3).
3. *La page Coût*, à une session des pages : le poids qu'elle affiche pour le
   salarié au SMIC compte désormais l'inapte (`cas_type_affiche`), et sa
   phrase sur les poids pourrait le nommer.
4. *La carrière heurtée*, au propriétaire (étape 19, note du 18 octobre) :
   la grille a désormais l'inaptitude, l'un des départs anticipés que la
   seconde option attendait ; la carrière longue et l'ex-invalide manquent
   encore.
