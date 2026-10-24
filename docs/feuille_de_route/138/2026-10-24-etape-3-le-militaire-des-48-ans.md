# Étape 3, vingtième partie : la forme des départs projetés, que rien ne publie d'ici ; le militaire, compté dès ses 48 ans

**La demande.** Deuxième vague du 24 octobre 2026, neuf sessions en
parallèle, une tâche chacune : celle-ci, le point 1 de « Ce qui reste » de la
note « l'âge de départ de chaque génération » (même jour), la part de chaque
génération projetée partie à chaque âge, que TRAJECTOiRE calcule, à confronter
à `parts_parties` ; faute de source lisible d'ici, le dire, et prendre le
point 2 : le militaire, que la pyramide ne comptait qu'à 50 ans, le test
d'abord. Au propriétaire, laissés : l'entrée selon la génération, l'Ircantec,
la table des poids.

**La forme des départs projetés : aucune source lisible d'ici.**

- *Le COR la calcule, sans la publier.* Son annexe méthodologique en ligne de
  juin 2026 (§ 1.2) : « L'âge effectif moyen de départ à la retraite une année
  donnée est calculé à partir d'une projection des taux de retraités à chaque
  âge entre 50 et 70 ans », et « le taux de retraités est également issu de
  ce modèle », TRAJECTOiRE. Les classeurs des quatre parties du rapport n'en
  gardent que des moyennes : l'âge conjoncturel de chaque année (figure 2.5),
  l'âge moyen de chaque génération (figures 3.28 et 4.5) ; les formes qu'ils
  publient sont observées (figures 4.6 et 4.7).
- *La DREES non plus.* Le panorama « Les retraités et les retraites » du 14
  octobre 2026, fiches 15, 16 et 18 (l'âge moyen, la diversité des âges, les
  départs anticipés), s'en tient à l'EIR et à Ancetre ; la page du modèle
  TRAJECTOiRE ne cite aucune publication qui la donne.
- *La seule forme projetée trouvée* est d'avant la réforme de 2023 : le
  document n° 2 de la séance du COR du 27 janvier 2022 (encadré 2, figure b)
  répartit les départs des générations 1940, 1960, 1980 et 2000, par sexe, en
  cinq classes — avant l'âge d'ouverture, à cet âge, entre lui et l'âge
  d'annulation de la décote, à ce dernier, après —, « calculs SG-COR à partir
  de DREES, modèle ANCETRE et projections COR – juin 2021 », en graphique,
  sans valeurs. Ni l'étude d'impact du projet de loi de financement
  rectificative pour 2023, ni les documents de la séance du 14 mars 2024
  (départs anticipés, carrières longues) n'en donnent.

La confrontation attend donc les taux de retraités à chaque âge, génération
par génération, de l'exercice de juin 2026, que seul le secrétariat général
du COR peut donner : au propriétaire (« Ce qui reste », point 1).

**Le militaire, compté dès ses 48 ans.**

- *Le défaut.* Radié à 48 ans et demi depuis l'action 152, le militaire de la
  grille part l'année de ses 48 ans, à chaque génération : chacune de ses
  cohortes, de celle de 1893 à celle de 2022, part en août de cette année-là
  (`dates_des_departs`). La pyramide commençait à 50 ans, et
  `Population.effectif` rendait zéro en deçà : ses deux premières années de
  pension ne comptaient ni en têtes ni en masses — au coût, aux avantages, à
  l'engagement, aux facteurs de la dépense, aux contrôles de l'EACR et
  d'Ancetre. Le relevé du 16 octobre (note « les tables de l'EACR ») l'avait
  vu, sans suite. Aucun autre cas type ne part avant 50 ans : l'agent de
  conduite de la SNCF y part au plus tôt, sous le droit des générations
  d'avant 1950.
- *La donnée.* L'INSEE publie tous les âges ; la pyramide en reprend
  désormais deux de plus, des mêmes sept classeurs des projections de
  population 2026 (`AGE_MINIMAL`, 48, dans `donnees/population.py` et dans le
  récupérateur) : 830 132 personnes de 48 ans et 871 081 de 49 ans au 1er
  janvier 2024. `scripts/verifier_donnees.py --appliquer` a ajouté 218 valeurs
  au central et 360 aux variantes, sans en corriger aucune : les 50 ans et
  plus sont ceux d'hier, à l'unité.
- *La même erreur, à l'horizon.* La dernière génération de la grille, 2015,
  avait été fixée pour un départ au plus tôt à 52 ans : les militaires nés de
  2018 à 2022, que porte la génération 2020, partent de 2066 à 2070, hors de
  la grille. Elle en est (`DERNIERE_GENERATION`) ; la suivante partirait au
  plus tôt en 2071.
- *Les cotisants restent comptés à partir de 50 ans.* La recette pèse ses
  cotisants par la même pyramide (`_masses_cotisations`, les versements et
  l'encours du pilier) : descendue à 48 ans, elle lui aurait fait compter les
  cotisants de 48 et 49 ans, et non les plus jeunes. Elle garde son plancher
  (`AGE_MINIMAL_DES_COTISANTS`, dans `cout.py`) : le biais des cotisants de
  moins de 50 ans est au propriétaire (étape 19, « Trouvé en chemin » de la
  note du 14 octobre), et le militaire ne le déplace pas. Le bilan du compte,
  qui compte les cotisants plus jeunes que la pyramide par l'effectif de leur
  génération à son plancher (`effectif_cotisant`), les compte à 48 ans.

**Ce qui est fait.**

- *Les tests*, vus rouges pour la raison attendue avant la donnée et le code :
  la pyramide commence à 48 ans, aux effectifs de l'INSEE, sous chaque
  variante (`tests/test_donnees.py`) ; chaque cohorte de la grille part à un
  âge que la pyramide compte, le militaire à 48 ans, l'agent de conduite à 50
  au plus tôt (`tests/test_facteurs_depense.py`) ; le militaire sert ses têtes
  dès l'année de ses 48 ans, 4 464 685 têtes pour 2 763 472 sur la génération
  1974 en 2024 ; la recette ne compte ses cotisants, à son compte et à son
  pilier, qu'à partir de 50 ans — vu rouge, à 2 612 799 pour 911 586, la
  donnée posée et le code non ; la grille s'arrête à la dernière génération
  dont une cohorte part avant l'horizon (`tests/test_cout.py`) ; le cotisant
  plus jeune que la pyramide, compté à 48 ans (`tests/test_bilan_compte.py`).
- *La donnée* : `population_par_age.csv` et ses variantes, leurs en-têtes, le
  récupérateur et ses contrôles, le gabarit de `verifier_donnees.py`, la note
  de la source (`data/sources.yaml`), la certification consignée
  (`data/derive/certification.json`) ; la pyramide du paquet commence au même
  âge (`construire_donnees.py`).
- *Quatre contrôles que les deux défauts avaient calés*, récrits sur ce que
  la grille compte désormais, chacun à ses valeurs publiées : en 2025, le
  militaire a 35,4 % de ses retraités sous 60 ans, entre les 31,5 % du jaune
  pensions hors invalidité et ses 39,2 % avec, quand la grille « tombait
  juste », à 31,6 %, sur le défaut (`tests/test_avantages.py`) ; en 2024,
  l'âge moyen de liquidation de la grille est de 61,9 ans, pour 63,6 à
  l'EACR, 62,3 jusque-là, le militaire y faisant 2,8 % des nouveaux retraités
  (`tests/test_controle_eacr.py`) ; à l'horizon, la fonction publique d'État
  s'écarte du COR de +26,5 % en dépense au lieu de +21,4, de +6,1 % en pension
  relative au lieu de +5,6, et ses deux cliquets remontent
  (`tests/test_cout.py`) ; la part stable de l'AWG refait l'effet de ses moins
  de 65 ans à 0,22 point au lieu de 0,16 (`tests/test_facteurs_depense.py`).

**Ce que ça déplace**, mesuré sous la référence, avant et après, sur `main`
à 99a4fde. La page Coût part de la dépense du COR, que le système actuel
garde ; le militaire ne change que les rapports de masses, et les autres
systèmes de quelques centièmes de point de PIB au plus : la proposition
(système 6) passe de 8,85 à 8,83 % du PIB en 2030, de 9,70 à 9,68 en 2050, de
8,09 à 8,05 en 2070 ; le système 2, de 4,67 à 4,65 % en 2070. Son rapport de
recettes ne bouge pas jusqu'en 2066 ; à l'horizon, il cesse de monter, la
génération 2020 y faisant compter ses cotisants de 50 à 52 ans : 0,652 de
2066 à 2070, quand il montait à 0,657. Les tables figées du paquet, le bilan
figé, les témoins et les chiffres ancrés, GitHub les refait.

**Ce qui reste**, de cette partie ; les points 3 de la note « l'âge de départ
de chaque génération » et 1 de la note « l'entrée dans l'emploi », au
propriétaire, et les naissances de l'année dans `cout.py`, le taux effectif,
demeurent.

1. *Au propriétaire : la forme des départs projetés.* Demander au secrétariat
   général du COR les taux de retraités à chaque âge, génération par
   génération, de l'exercice de juin 2026, que son annexe méthodologique dit
   tirés de TRAJECTOiRE ; puis les confronter à `parts_parties`.
2. *Le poids du militaire.* Compté désormais à tous ses âges, il met quatre
   points de trop de ses retraités sous 60 ans, fait 2,8 % des nouveaux
   retraités de la grille en 2024, et la dépense de la fonction publique
   d'État s'écarte du COR de 26,5 % à l'horizon. Chaque cohorte de la grille
   reçoit la part de sa caisse dans le stock des retraités de 2024, reconduite
   jusqu'en 2070, quand un militaire parti à 48 ans reste retraité plus
   longtemps qu'un autre : ce que cette part fait à son flux et à sa dépense
   est à mesurer, par une session du modèle, le test d'abord.
