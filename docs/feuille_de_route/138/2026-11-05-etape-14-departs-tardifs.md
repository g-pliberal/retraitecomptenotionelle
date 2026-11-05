# Étape 14 : les départs tardifs — après l'âge d'annulation de la décote et après 67 ans, la population en a moins que l'EIR et le Panorama ; aucune source n'en donne la règle, rien ne change

**Le 5 novembre 2026 : la population ne fait partir personne à 68 ans ou
plus, des générations 1950 à 1960, quand le Panorama 2026 de la DREES compte
« environ 1 % » de départs entre 68 et 70 ans et « environ 0,2 % » entre 71 et
74 ans ; elle ne fait partir personne à 66 ans révolus en 1950 (l'EIR : 1,9 %
des femmes, 1,7 % des hommes), ni après l'âge d'annulation de la décote en
1953 (l'EIR : 3,3 et 2,8 %, dont 2,21 et 1,62 points au taux plein par l'âge).
Les trois sources ne comptent pas le même âge, et l'EIR s'arrête à 66 ans en
2016, à 67 en 2020. Aucune ne dit qui part tard, à quel âge ni sous quelle
condition : le Panorama donne un ordre de grandeur, les deux sexes ensemble ;
l'EIR, la place sans le mois. Aucun code, aucune donnée, aucun test ne change.
En chemin, un défaut de la mesure : à la génération 1953, que la grille ne
simule pas, les jumelles qui attendent comptent leur attente de l'âge légal
de 1950.**

Demande : la vague 10, lancée par la session d'orchestration le 5 novembre
2026 : un point de l'étape 14, et lui seul, la mesure d'abord — les départs
après l'âge du taux plein par l'âge et après 67 ans, que la note du taux plein
par l'âge laissait (`2026-11-05-etape-14-taux-plein-par-l-age.md`, « Ce qui
reste », point 1). Correction seulement si une source publiée la fonde. Ni les
artisans (décision 12), ni la grille du coût (décision 11).

- *Les sources*, ouvertes le 5 novembre 2026 :
  - les deux classeurs de l'EIR du jeu de la DREES
    `3013_donnees-statistiques-sur-les-caracteristiques-des-retraites`,
    « Caractéristiques des retraités nés en 1953 (EIR 2020) » et « … nés en
    1950 (EIR 2016) », pris par `curl` aux empreintes de la note du taux plein
    par l'âge (SHA-256 `d5e8b877…5e0` et `59f76598…1a8`, en entier dans la
    mesure), lus cellule par cellule ;
  - « Les retraités et les retraites, édition 2026 » (DREES, au manifeste sous
    `drees_panorama_retraites_2026`), pris à son miroir, SHA-256
    `9eb36a06639af0f4298d281b41acbde4236e47fc73e40c673f153ad86735e9be`, celle
    du manifeste ; fiche 16, « La diversité des âges de départ à la
    retraite », tableau 1 (page 150), encadré 2 (page 152), tableau 2 (page
    153), lus par `pdftotext -layout`, recopiés dans la mesure.

  Encadré 2, « Les départs à la retraite après 67 ans » : « Les résultats
  présentés dans cette fiche à partir des données de l'échantillon
  interrégimes de retraités (EIR) 2020 […] sont calculés en considérant les
  retraités nés en 1953, observés à l'âge de 67 ans. […] Les assurés qui
  liquideront leurs droits directs de retraite après cet âge ne sont donc, par
  construction, pas retenus […]. Si les premières liquidations d'un droit
  direct de retraite après 67 ans sont relativement rares, elles ne sont pour
  autant pas inexistantes (afin de bénéficier d'une surcote plus importante ou
  d'une majoration de durée d'assurance, par exemple). Sur la base des
  générations nées en 1950 (personnes âgées de 70 ans en 2020) et en 1946
  (personnes âgées de 74 ans en 2020), les départs à la retraite entre 68 et
  70 ans représentent environ 1 % des départs, et ceux qui ont lieu entre 71
  et 74 ans environ 0,2 %. La proportion des départs à 67 ans ou après est, en
  particulier, très élevée parmi les professions libérales (11 % de départs
  entre 67 et 70 ans). »
- *Ce que chacun compte.* Pas la même chose, sur trois points ; les écarts de
  définition se déclarent ici, ils ne se corrigent pas.
  - *L'âge de quoi.* La population : un âge par variante, celui où elle part,
    tous ses régimes ensemble (`condition_au_depart`). Le Panorama : « Âge
    atteint à la première liquidation d'une pension de base » (tableau 1,
    note) ; « l'âge de liquidation de la pension dans le régime pour lequel la
    durée validée est la plus importante, qui n'est pas nécessairement celui
    correspondant à la première liquidation » (tableau 2, note) ; « les
    premières liquidations d'un droit direct » (encadré 2). Le classeur de
    l'EIR ne dit pas le sien : ses en-têtes sont « Avant 60 ans » … « 67 ans
    et plus » et « Départ après l'âge d'annulation de la décote », sans
    régime ; le jeu nomme « âge de liquidation dans le régime principal » sa
    pièce de l'EIR 2012 seule, et l'en-tête de `departs_generations.csv` le
    prête aux deux classeurs. Ses chiffres de 1953 ne sont ni ceux du
    tableau 1 — à 60 ans, 9,4 % des femmes (ÂgeLiq_Détails, E6), 11 au
    tableau 1 —, ni ceux du tableau 2 — à 67 ans et plus, 0,8 % de tous
    (L5), 1,1 au tableau 2, résidents en France. La source ne tranche pas.
  - *La place.* L'EIR range le départ par rapport à l'âge d'annulation de son
    régime : en 1950, des départs des femmes au taux plein par l'âge pris de
    60 à 64 ans, 1,24 point sont rangés à l'annulation ou après par un régime
    qui l'annule avant 65 ans (la note du taux plein par l'âge, « par la
    place ») ; la
    population, par rapport aux âges de la génération (`position_du_depart`,
    `AgesOuverture`, `AgesAnnulationDecote`).
  - *La censure.* L'EIR de 2016 voit les nés en 1950 jusqu'à la fin de 2016,
    leur dernier âge étant « 66 ans » (ÂgeLiq_Détails, K1) ; celui de 2020,
    les nés en 1953 « observés à l'âge de 67 ans » (encadré 2), leur colonne
    « 67 ans et plus » (L1) ne comptant que les départs de 2020. Qui part plus
    tard n'est ni au numérateur ni au dénominateur. La population compte tous
    les départs de la génération.

  Ce qui se compare donc : à l'âge révolu, l'année qui suit celle de
  l'annulation (66 ans en 1950, 67 ans et plus en 1953, censurés) ; à la
  place, avec l'écart du régime ; à 68 ans et plus, le seul encadré 2, les
  deux sexes ensemble, sur deux générations plus anciennes.
- *La mesure* (`docs/mesures/138/2026-11-05-etape-14-departs-tardifs.txt`,
  ses deux scripts et leurs sorties), sur `main` à 205cc97, la méthode de la
  note du taux plein par l'âge : toutes les variantes de la population, cinq
  générations, aux poids de retraités d'une année, tous leurs départs. Part
  des départs, en % :

  | génération | après l'annulation, à la place | à 67 ans révolus | à 68 ans et plus |
  |---|---|---|---|
  | 1950, femmes | 1,20 (65,42 ans, surcote) | 0 | 0 |
  | 1950, hommes | 1,69 (65,45 ans, surcote) | 0 | 0 |
  | 1953, femmes | 0 | 0 | 0 |
  | 1953, hommes | 0 | 0 | 0 |
  | 1955, femmes | 1,66 (67,42 ans, surcote) | 8,99 | 0 |
  | 1955, hommes | 2,07 (67,45 ans, surcote) | 5,55 | 0 |
  | 1960, femmes | 1,38 (67,42 ans, surcote) | 8,11 | 0 |
  | 1960, hommes | 1,86 (67,45 ans, surcote) | 4,26 | 0 |
  | 1965, femmes | 1,41 (68,17 ans, surcote) | 9,85 | 1,41 |
  | 1965, hommes | 1,89 (68,20 ans, surcote) | 6,50 | 1,89 |

  Après l'annulation, la population ne fait partir que la jumelle qui
  surcote et attend le plus, 5,42 ans après l'âge légal chez les femmes, 5,45
  chez les hommes (`attentes_des_surcotes`, « 67 ans et plus » pris pour 67
  ans) : 60 + 5,42 = 65,42 en 1950, 62 + 5,42 = 67,42 en 1955 et 1960,
  62,75 + 5,42 = 68,17 en 1965. Les départs à 67 ans révolus des générations
  1955 à 1965 sont, pour le reste, ceux de l'âge d'annulation même, 67 ans.
- *Le défaut de la mesure, à la génération 1953.* Elle y part, la même jumelle,
  à 65,42 et 65,45 ans, pour 1,52 % des départs des femmes et 1,84 % de ceux
  des hommes (`pilote_surcotes_1953.py`) : 60 + 5,42, l'âge légal de 1950, et
  non 61,17 + 5,42 = 66,59. L'attente se compte de l'âge légal que
  `ages_legaux` donne aux générations de la grille, de cinq en cinq, et
  `_par_generation` prête à 1953 celui de 1950. Comptée de 61 ans et 2 mois,
  la jumelle partirait à 66,59 et 66,62 ans, après l'annulation : 1,52 et
  1,84 % au lieu de 0. Ni la page, ni la mesure du dépôt, qui simule les
  générations 1950 et 1955 (`GENERATIONS_DES_DEPARTS`), n'en sont touchées ;
  les mesures de session qui simulent 1953, celle-ci et la note du taux plein
  par l'âge, le sont pour leurs jumelles qui attendent : le même plancher sert
  aussi les jumelles qui décotent, dont l'âge en 1953 n'est pas mesuré ici.
- *L'EIR, et le calcul posé à la main.* La part de la colonne, fois celle de
  la condition parmi ses départs, sur cent.
  - *À la place, après l'annulation* (ÂgeLiq, colonne H). 1950, femmes : H6 =
    4,9 % ; au taux plein par l'âge, H6 × H291 = 4,9 × 64,4 = 315,56, soit
    3,16 points ; avec surcote, H6 × H279 = 4,9 × 27,8 = 136,22, 1,36. Hommes :
    H7 = 4,4 ; 4,4 × 51,8 = 227,92, 2,28 ; 4,4 × 38,5 = 169,40, 1,69. 1953,
    femmes : H6 = 3,3 ; H6 × H294 = 3,3 × 67,0 = 221,10, 2,21 ; H6 × H282 =
    3,3 × 25,1 = 82,83, 0,83. Hommes : H7 = 2,8 ; 2,8 × 57,7 = 161,56, 1,62 ;
    2,8 × 33,4 = 93,52, 0,94.
  - *À l'âge révolu qui suit l'annulation* (ÂgeLiq_Détails). 1950, à 66 ans
    (K) : femmes, K6 = 1,9, dont K6 × K291 = 1,9 × 58,0 = 110,20, 1,10 au taux
    plein par l'âge, et K6 × K279 = 1,9 × 30,8 = 58,52, 0,59 avec surcote ;
    hommes, K7 = 1,7, dont 1,7 × 47,6 = 80,92, 0,81, et 1,7 × 39,7 = 67,49,
    0,67. 1953, à 67 ans et plus (L), censurés : femmes, L6 = 0,8, dont
    L6 × L294 = 0,8 × 61,1 = 48,88, 0,49, et L6 × L282 = 0,8 × 29,1 = 23,28,
    0,23 ; hommes, L7 = 0,8, dont 0,8 × 49,8 = 39,84, 0,40, et 0,8 × 40,6 =
    32,48, 0,32.
  - *Le Panorama* : 67 ans ou plus, nés en 1953, femmes 1, hommes 1
    (tableau 1, colonnes « Ensemble ») ; 68 à 70 ans, « environ 1 % », 71 à 74
    ans, « environ 0,2 % », soit environ 1 + 0,2 = 1,2 % à 68 ans et plus,
    les deux sexes ensemble, nés en 1950 et en 1946 (encadré 2) ; chez les
    professions libérales, 11 % de 67 à 70 ans (encadré 2), et, nés en 1953,
    3,7 % à 67 ans ou plus dans leur régime principal (tableau 2).

  | | EIR, à la place | dont taux plein par l'âge | dont surcote | EIR, à l'âge révolu suivant | population, à la place | population, à l'âge révolu suivant |
  |---|---|---|---|---|---|---|
  | femmes nées en 1950 | 4,9 | 3,16 | 1,36 | 1,9 (66 ans) | 1,20 | 0 |
  | hommes nés en 1950 | 4,4 | 2,28 | 1,69 | 1,7 (66 ans) | 1,69 | 0 |
  | femmes nées en 1953 | 3,3 | 2,21 | 0,83 | 0,8 (67 et plus) | 0 (1,52 sans le défaut) | 0 |
  | hommes nés en 1953 | 2,8 | 1,62 | 0,94 | 0,8 (67 et plus) | 0 (1,84 sans le défaut) | 0 |

- *Ce que cela dit.*
  - L'écart est réel. Après l'annulation, la population n'a que des
    surcotes, au nombre de l'EIR en 1950 (1,20 pour 1,36 chez les femmes,
    1,69 pour 1,69 chez les hommes) ; il lui manque le taux plein par l'âge
    qui attend après l'annulation, 3,16 et 2,28 points en 1950, dont une part,
    au plus 1,24 point chez les femmes, tient au régime, 2,21 et 1,62 en
    1953. À
    l'âge révolu, il lui manque toute l'année qui suit l'annulation : 1,9 et
    1,7 % en 1950. Après 67 ans, il lui manque, jusqu'à la génération 1960,
    l'environ 1,2 % du Panorama ; la génération 1965 en a 1,41 et 1,89 %, à
    68,17 et 68,20 ans, par l'âge légal plus tardif et non par une source.
  - Pourquoi rien ne se corrige. Une variante demande un sexe, une carrière,
    une condition et un âge. L'encadré 2 donne un ordre de grandeur, « environ
    1 % » et « environ 0,2 % », les deux sexes ensemble, sur les générations
    1950 et 1946, à la première liquidation, et ses motifs « par exemple » ; il
    ne dit ni qui, ni à quel âge dans ses tranches, hors des libéraux, dont la
    tranche part de 67 ans. L'EIR donne, par sexe, la part et la condition des
    départs d'après l'annulation, mais non leur mois, et s'arrête à 67 ans.
    Faire attendre une jumelle du taux plein par l'âge, ou faire partir à 68
    ans et plus une part des carrières, demanderait une convention — le
    milieu de la tranche, comme les attentes des surcotes —, non une source :
    la décision est au propriétaire.
- *Ce qui ne bouge pas.* Aucun code, aucune donnée, aucun test : rien ne se
  remesure. La page, qui ne lit pas la population (action 157), la grille du
  coût (décision 11), les témoins, le paquet. Aucune règle du scénario 1 ;
  aucune source ne s'ajoute au manifeste, où le Panorama est déjà : pas
  d'entrée au journal de veille. Le chantier du Panorama
  (`data/reference/drees_panorama_2026.yaml`, fiche 16, action 178) garde
  l'encadré 2 « pour la clôture » ; cette note en dit les chiffres.

**Ce qui reste**, de ce point :

1. *Au propriétaire* : faire attendre après l'âge d'annulation une jumelle du
   taux plein par l'âge (en 1953, 2,21 et 1,62 points des départs), et faire
   partir à 68 ans et plus environ 1,2 % des départs, sans source pour le sexe,
   la carrière ni l'âge exact : une convention, à décider avant toute version.
2. *Le défaut de la mesure à la génération 1953* : les jumelles qui attendent
   y comptent leur attente de l'âge légal de 1950. Candidat : à vérifier dans
   les mesures de session qui simulent 1953, puis à corriger dans
   `_attente_du_depart`, ou à déclarer, le test d'abord.
3. *La génération 1965* part pour 1,41 et 1,89 % à 68 ans passés, par
   l'attente des nés en 1953 comptée de 62 ans et 9 mois ; aucune source ne dit
   ce que font les générations d'après 1953.
