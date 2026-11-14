# Correction de la ligne 12 de la file : quatre complémentaires de libéraux servies au premier jour du trimestre civil qui suit

Douzième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, quatre caisses.

**Le texte, relu aux index JORF et LEGI** (à jour du 11 novembre 2026).

- CAVOM, statuts de 2016, article 14, II (arrêté du 30 décembre 2015,
  JORFARTI000031740853, en vigueur le 1er janvier 2016), repris par le règlement de
  2026 (arrêté du 10 juillet 2026, annexe I, article 1er, II, JORFARTI000054435969) :
  « La retraite prend effet au plus tôt au premier jour du trimestre civil qui suit le
  dernier des faits ci-après : - la demande [...] ; - la justification de la cessation
  d'activité ; - le paiement des cotisations et majorations exigibles ». L'arrêté du
  12 décembre 2024 ne récrit pas ce II.
- CARPIMKO, statuts de 1984, article 11 (LEGIARTI000006782880), et règlement de 2026,
  article 7 (JORFARTI000054435915) : « La date d'entrée en jouissance de la retraite
  est fixée au premier jour du trimestre civil qui suit la demande, sans pouvoir être
  antérieure » à l'âge. Entre les deux, l'article n'est pas lu : l'arrêté du 20 mai
  1987 et les statuts de 1996 ne sont pas au Journal officiel, et aucun arrêté publié
  de 1987 à 2025 ne le porte.
- CAVP, statuts du 11 mai 2009, article 14 (JORFARTI000020694605, en vigueur le 7 juin
  2009), et règlement de 2026, article 14 (JORFARTI000054436087) : « L'entrée en
  jouissance de la retraite de droits propres est fixée au premier jour du trimestre
  civil qui suit cette demande. »
- CARMF, règlement de 2026, I, article 24 (JORFARTI000054435859, en vigueur le
  18 juillet 2026) : « La date d'effet de l'allocation est fixée au premier jour du
  trimestre civil qui suit la réalisation de toutes les conditions d'ouverture des
  droits, sans pouvoir être antérieure à la date de la demande ».

Le texte tranche ce que la ligne dit, dans ces bornes.

**L'erreur.** Le modèle servait ces complémentaires le premier du mois qui suit l'âge,
avec la base : un mois trop tôt quand ce mois est le troisième d'un trimestre civil,
deux quand c'est le deuxième.

**Le test d'abord** (`tests/test_sections_liberales.py`), vu rouge, puis vert, chaque
cas servi par le portage et refait au bit près par le moteur Python
(`servi_et_refait`) :

- `test_les_quatre_caisses_portent_la_date_d_effet_au_trimestre_civil` : chaque premier
  du mois de 1949 à 2040, la période qui liquide dit si le texte lu reporte la pension,
  et aucun autre régime ne le dit ;
- `test_la_complementaire_prend_effet_au_trimestre_civil_qui_suit`, dix cas datés à la
  main : la date, le coefficient à cette date, deux départs dont le second porte le
  motif `trimestre_civil` ;
- `test_la_complementaire_reste_au_depart_quand_nul_texte_lu_ne_la_reporte`, sept cas :
  une date qui ouvre déjà un trimestre, ou une pension que le texte lu ne date pas ;
- `test_la_date_d_effet_au_trimestre_civil_se_pose_a_la_main` : les montants des fiches ;
- `test_la_page_dit_la_complementaire_servie_au_trimestre_civil`.

**L'effet aux cas posés** (double du salaire moyen, euros de 2026).

- CAVOM : né le 10 mai 1959, 62 ans le 10 mai 2021, servi le 1er juillet 2021 au lieu
  du 1er juin ; 13 580,64 € par an avant comme après, **un mois de trop, 1 131,72 €**.
- CARPIMKO : né le 10 novembre 1959, entré à 26 ans, demande à 67 ans : le 1er janvier
  2027 au lieu du 1er décembre 2026, **un mois de trop, 475,50 €**, puis trois
  trimestres civils d'ajournement au lieu de deux, 5 775,59 € par an au lieu de
  5 706,01 €.
- CAVP : né le 10 mai 1960, entré à 21 ans, demande à 67 ans : le 1er juillet 2027 au
  lieu du 1er juin ; 14 548,91 € par an, **un mois de trop, 1 212,41 €**.
- CARMF : né le 10 mai 1964, entré à 22 ans, parti à 63 ans : le 1er juillet 2027 au
  lieu du 1er juin ; 14 056,14 € par an, **un mois de trop, 1 171,35 €**. Né le 10 mars
  1964, parti à 63 ans et un mois : le 1er juillet au lieu du 1er mai, **deux mois de
  trop, 2 337,68 €**, puis 1,0625 au lieu de 1,05, 14 193,04 € par an au lieu de
  14 026,06 €.

**La correction.** Un paramètre de période, `effet_au_trimestre_civil` (schéma,
chargeur, paquet du portage) : les dates présumées, [début, fin) au jour, que le texte
lu reporte — la CAVOM depuis le 1er janvier 2016, la CARPIMKO du 1er janvier 1984 au
4 juin 1987 et depuis le 18 juillet 2026, la CAVP depuis le 7 juin 2009, la CARMF
depuis le 18 juillet 2026. Les bornes sont celles du texte, non celles de la période.
`departsEtDemandes` et son jumeau reportent la date de chaque régime qui le porte, un
premier du mois, au premier jour du trimestre civil qui commence ce jour-là ou après,
sous un motif neuf, `trimestre_civil`, que la page du simulateur dit. La pension s'y
liquide dans un départ à elle, à l'âge et sous la rédaction de ce jour.

**Deux défauts que le report aurait étendus, corrigés avec lui** dans `ouvrir`, des
deux côtés. Une complémentaire liquidée sans sa base ne voyait plus aucun régime qui
oppose une durée ou un âge. La durée requise retombait sur 160 trimestres : la CARPIMKO
majorait depuis une durée que la génération 1959 n'a pas (1,05 au lieu de 1,0375 au cas
posé). Et la CAVP perdait le motif de la carrière longue : elle minorait par ses deux
pentes (0,81 au lieu de 0,85, né le 10 janvier 1962, servi le 1er avril 2024). Depuis,
la complémentaire qui suit sa base s'ouvre aux conditions des régimes de base de la
carrière ; celle qui se demande à son âge, sans la base, ne leur doit que leur durée
requise. Le premier défaut existait déjà pour qui demandait sa CARPIMKO avant sa base :
c'est l'écart que l'étape 3 de l'action 192 avait relevé sans l'expliquer.

**Deux essais anciens remis à leur texte.** L'inapte de la CAVOM né le 10 novembre
1962 est servi le 1er janvier 2025, sous les statuts de 2025, à 0,75, et non plus le
1er décembre 2024 sans coefficient ; le cas né le 10 septembre 1962 garde la dernière
pension des statuts de 2016. L'auxiliaire médical né en janvier 1960, demandant à
67 ans, est servi le 1er avril 2027 : deux trimestres civils d'ajournement, 1,025.

**Ce que la correction déplace.** 16 témoins de simulation sur 933, tous de libéraux :
un départ de plus, aucune pension annuelle. Une page témoin, celle du cumul. Les pages
toutes faites ne bougent pas.

**La base des libéraux reste au mois, et c'est à dire au propriétaire.** L'article
R. 643-6 du code de la sécurité sociale date la pension de base des libéraux au même
trimestre civil ; le modèle la sert au premier du mois (fiche
`cnavpl_allocation_avant_2004`, étape 3 de l'action 192, dont la règle est écrite et
gardée, en attente de sa décision). Tant qu'elle n'est pas publiée, le simulateur
montre deux dates à ces libéraux — la base à leur départ, la complémentaire un ou deux
mois après — là où leur caisse sert les deux le même jour. Cette correction lève les
deux obstacles de l'étape : la date d'effet de la CAVOM et de la CARPIMKO est lue, et
l'écart de la CARPIMKO liquidée sans sa base est expliqué et corrigé. Son correctif
gardé ne s'applique plus tel quel : `departs` et la page portent déjà le motif
`trimestre_civil`.

**La classe, pas le cas.** Le même report est écrit, et non servi, dans des textes que
la file ne porte pas :

- la CAVAMAC (règlement de 2026, article 9, JORFARTI000054436046) et la CARCDSF
  (règlement de 2026, article 24, JORFARTI000054435749) ;
- les prestations complémentaires de vieillesse des auxiliaires médicaux (règlement de
  2026, article 2), la capitalisation de la CAVP (article 23) et ses biologistes
  (III, article 3) ;
- la base des libéraux (R. 643-6), dite plus haut ;
- la CARPV, la CAVEC et la CPRN, dont l'article n'est pas lu.

**Ce qui reste déclaré** dans les fiches : la demande, que le modèle ne connaît pas et
tient pour faite à temps ; la CARPIMKO du 5 juin 1987 au 17 juillet 2026 et la CAVOM
d'avant 2016, non lues ; la CARMF de 2017 au 17 juillet 2026, que son guide donne au
trimestre civil sans que l'article soit lu ; l'ASV des médecins, que son règlement ne
date pas ; à la CAVOM, la cessation à effet rétroactif ; à la CARMF, le formulaire reçu
dans les douze mois. Le polypensionné dont les bases liquident à des dates différentes
voit sa complémentaire reportée s'ouvrir aux conditions de toutes ses bases.
