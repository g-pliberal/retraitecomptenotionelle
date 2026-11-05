# Étape 14 : le calage de la durée des femmes, revu contre l'EIR de 2020 — il tient ; l'excès de l'âge légal n'est pas dans la durée

**Le 5 novembre 2026 : le calage de la durée des femmes, confronté au
classeur de la DREES des retraités nés en 1953 (EIR de 2020), ouvert pendant
la session, tient. Simulée au portage, la génération 1953 de la population a
la durée validée de ses résidentes à dix ans près : 65,6 % de 40 années et
plus, majorations comprises, pour 67,0 ; aucune tranche ne s'écarte de plus
de 2,8 points ; sa moyenne est sous la cible, non au-dessus. Ses femmes n'ont
donc pas des carrières trop longues ; et pourtant son âge légal en reçoit
61,3 % des départs, pour 37,5. La carrière de trente à quarante ans portée à
44 années en 1955 fait la part des 40 années et plus que l'EIR publie ; ce
qu'elle passe au-delà de la durée requise, la source ne le dit pas : sa
« carrière complète », 58,7 %, n'est pas la durée requise atteinte. Aucun
code ne change, rien ne bouge ; le point 3 de la trente-cinquième version
trouve là sa réponse, et deux questions vont au propriétaire.**

Demande : la vague 7, lancée le 5 novembre 2026 par la session
d'orchestration, file I : l'action 138, étape 14, le point 3 de « Ce qui
reste » de la trente-cinquième version
(`2026-11-03-etape-14-taux-plein-entre-les-deux-ages.md`) : « Le calage de la
durée des femmes, qui porte la carrière de trente à quarante ans des nées en
1955 à 44 années, et laisse l'âge légal trop chargé, 48,7 % pour 37,5 ; revu,
il rendra à l'âge d'annulation ce que cette version lui prend. » Le revoir
contre la source publiée qui fait foi.

- *Le calage* (`DUREE_DES_FEMMES_SELON_LA_GENERATION`, `ecarts_des_femmes`,
  `scripts/grille_large.py`, sur `main` à 319ee4b) : les carrières
  incomplètes des femmes, hors des régimes statutaires, gagnent les mêmes
  années à chaque génération, bornées par l'âge légal, pour que la durée
  moyenne des femmes, majorations comprises, soit celle de
  `duree_assurance_generations.csv` : 158 trimestres pour 1953 (l'EIR de
  2020, fiabilité haute), 162,7617 pour 1955 (le même EIR prolongé par
  TRAJECTOiRE, projetée). Il leur donne 4,97 années en 1950, 7,40 en 1953,
  9,76 en 1955 ; la carrière de trente à quarante ans du salariat privé,
  35 années dans la grille, entrée à 18 ans comme les carrières pleines de sa
  génération, en valide 44 en 1955 (62 − 18), les huit trimestres de chacun
  de ses deux enfants la portant à 48.
- *La source*, ouverte le 5 novembre 2026 : « Caractéristiques des retraités
  nés en 1953 (EIR 2020).xlsx », pièce jointe du jeu de la DREES
  `3013_donnees-statistiques-sur-les-caracteristiques-des-retraites`
  (https://data.drees.solidarites-sante.gouv.fr/api/explore/v2.1/catalog/datasets/3013_donnees-statistiques-sur-les-caracteristiques-des-retraites/attachments/caracteristiques_des_retraites_nes_en_1953_eir_2020_xlsx),
  191 Ko, empreinte SHA-256 `d5e8b877…d16f94c5e0`
  (`d5e8b8776768e31a3a8a0490bf749fc6615d12a8d25716e57a658dd16f94c5e0`). Le
  récupérateur du dépôt n'a pu l'atteindre, la connexion coupée ; la lecture
  web l'a pris. Feuille « Naissance-Résidence », colonne « Retraités résidents
  en France », lignes « Femme », mot pour mot :

  | ligne | Intitulé | résidentes |
  |---|---|---|
  | 17 | Part d'assurés à carrière complète (en %) | 58,7 |
  | 185 | Moyenne de la durée validée (en années) | 40,0 |
  | 188 | Proportion d'assurés dont la durée validée est inférieure à 10 ans | 1,8 |
  | 191 | Proportion d'assurés dont la durée validée est comprise entre 10 et 20 ans | 6,0 |
  | 194 | Proportion d'assurés dont la durée validée est comprise entre 20 et 30 ans | 8,5 |
  | 197 | Proportion d'assurés dont la durée validée est comprise entre 30 et 40 ans | 16,8 |
  | 200 | Proportion d'assurés dont la durée validée est supérieure ou égale à 40 ans | 67,0 |
  | 272 | Part de départs anticipés pour carrière longue (en %) | 13,2 |
  | 275 | Part de départ avec décote (en %) | 11,9 |
  | 278 | Part de départ où la décote est inapplicable (en %) | 2,4 |
  | 281 | Part de départ avec surcote (en %) | 14,2 |
  | 284 | Part des retraités ayant liquidé pour invalidité (en %) | 8,3 |
  | 287 | Part de départ au taux plein pour un autre motif que l'âge, la durée, l'invalidité ou l'inaptitude (en %) | 1,2 |
  | 290 | Part des retraités ayant liquidé pour inaptitude (en %) | 8,0 |
  | 293 | Part de départ au taux plein par l'âge (en %) | 11,7 |
  | 296 | Part de départ au taux plein par la durée (hors surcote et carrière longue, en %) | 28,3 |

  La durée validée de ces lignes est celle des majorations comprises : celle
  qui les exclut a ses lignes à part (221 à 236 ; 50,0 % de 40 années et
  plus). Feuille « CondLiquidation », ligne 17, « Part d'assurés à carrière
  complète (en %) », femmes de tous lieux de résidence : 95,6 parmi les
  départs pour carrière longue, 87,4 avec surcote, 84,4 au « Taux plein par
  la durée (hors surcote et RACL) », 57,3 en tout. Les départs placés selon
  l'âge légal et l'âge d'annulation (feuille « ÂgeLiq ») sont ceux du dépôt,
  certifiés (`departs_generations.csv`) : 21,7 % avant l'âge légal, 37,5 à
  lui, 26,7 entre les deux âges, 10,8 à l'âge d'annulation, 3,3 après, tous
  lieux de résidence.
- *La mesure* (`docs/mesures/138/2026-11-05-etape-14-duree-des-femmes.txt`,
  son script et sa sortie) : la population de `main`, 19 408 variantes ; les
  femmes de deux générations simulées au portage, 1953, qui n'est pas une
  génération de la grille mais que le calage date comme les autres, à ses
  poids de retraitées de 2020, et 1955, la génération de la grille que la
  mesure des départs juge sur les nées en 1953, à ses poids de 2022 ; chaque
  variante pesée de la part que la génération lui donne
  (`part_de_la_generation`), tous les départs comptés, sans le recalage de la
  page ni l'âge où l'enquête voit la génération. Elle redonne, pour 1955, les
  places de la dernière mesure du dépôt à un point près : 51,5 % à l'âge
  légal et 22,4 entre les deux âges, pour 50,78 et 23,18
  (`2026-11-03-etape-14-mesure-e12fe03.txt`). La durée est le nombre de trimestres validés
  au départ, majorations comprises (`trimestres_valides`), divisé par quatre.

  | | EIR, résidentes de 1953 | population, 1953 | population, 1955 |
  |---|---|---|---|
  | durée validée, moins de 10 ans | 1,8 | 0,0 | 0,0 |
  | de 10 à 20 ans | 6,0 | 7,9 | 7,8 |
  | de 20 à 30 ans | 8,5 | 11,3 | 11,1 |
  | de 30 à 40 ans | 16,8 | 15,2 | 11,6 |
  | 40 ans et plus | 67,0 | 65,6 | 69,5 |
  | dont sous la durée requise | — | 0,2 | 2,9 |
  | moyenne, en trimestres | 160 (40,0 ans) ; 158 au fichier | 155,5 | 162,1 |
  | départs pour carrière longue | 13,2 | 6,6 | 12,1 |
  | avec décote | 11,9 | 11,9 | 12,4 |
  | avec surcote | 14,2 | 11,2 | 14,1 |
  | au taux plein par l'âge | 11,7 | 11,1 | 6,9 |
  | au taux plein, autrement | 48,2 | 59,3 | 54,5 |
  | dont jumelles inaptes | 16,3 | 9,4 | 9,4 |
  | avant l'âge légal | 21,7 | 11,5 | 17,1 |
  | à l'âge légal | 37,5 | 61,3 | 51,5 |
  | entre les deux âges | 26,7 | 14,9 | 22,4 |
  | à l'âge d'annulation | 10,8 | 12,3 | 7,3 |
  | après lui | 3,3 | 0,0 | 1,7 |

  Calculs posés à la main. Les tranches de l'EIR font 1,8 + 6,0 + 8,5 +
  16,8 + 67,0 = 100,1, à l'arrondi près. Le modèle compte en 40 ans et plus
  0,2 + 65,4 = 65,6 en 1953, 2,9 + 66,6 = 69,5 en 1955 ; sous 20 ans,
  0,0 + 7,9 = 7,9, pour 1,8 + 6,0 = 7,8. Le taux plein « autrement » de
  l'EIR réunit la durée, l'invalidité, l'inaptitude, la décote inapplicable
  et les autres motifs : 28,3 + 8,3 + 8,0 + 2,4 + 1,2 = 48,2 ; ses
  invalides et inaptes, 8,3 + 8,0 = 16,3 ; celui du modèle, 49,9 + 9,4 =
  59,3 en 1953, 45,1 + 9,4 = 54,5 en 1955 (la ligne « dont » du modèle ne
  compte que ses jumelles inaptes, que son code marque). Les conditions de l'EIR font
  13,2 + 11,9 + 14,2 + 11,7 + 48,2 = 99,2, un retraité sur cent n'en ayant
  pas de connue. La moyenne de l'EIR est arrondie à l'année : 40,0 ans,
  160 trimestres, que les 158 du fichier, 39,5 ans, arrondissent aussi.
  1955 a 162,7617 − 158 = 4,76 trimestres de plus que 1953 au fichier, la
  projection de TRAJECTOiRE.
- *Ce que cela dit.*
  - Le calage tient contre la source, à la seule génération qu'elle mesure
    entière avec ses durées : les femmes de 1953 de la population ont, à dix
    ans près, la durée validée des résidentes de l'EIR, et leur moyenne
    simulée, 155,5 trimestres, est sous la cible du calage, 158, non
    au-dessus. Ce que la note de la trente-cinquième version lui prêtait,
    des femmes qui ont leur durée à l'âge légal quand celles de l'EIR en
    manquent encore, ne se lit pas dans ce que l'EIR publie.
  - La carrière de trente à quarante ans à 44 années, en 1955, et à 42 en
    1953, est ce qui donne à la génération ses 40 années et plus : la grille
    garde les parts des tranches des résidentes retraitées en 2020, 36,2 % à
    40 années et plus hors majorations (`quintiles_eqcc_residents.csv`),
    quand la génération 1953 en compte 50,0 (ligne 236) ; les années que le calage ajoute font
    passer la tranche de trente à quarante ans au-dessus. Restée sous 40
    années, elle ôterait à la génération plus de la moitié de ses 40 années
    et plus.
  - Ce que la source ne tranche pas : combien des 67,0 % de 40 années et
    plus restent sous la durée requise, 165 trimestres en 1953, soit 41,25
    années. Le classeur s'arrête à « 40 ans et plus ». Sa « carrière
    complète », 58,7 %, ne le dit pas : elle n'est pas la durée requise
    atteinte, puisque seuls 84,4 % des départs au taux plein par la durée,
    87,4 % des départs avec surcote et 95,6 % des départs pour carrière
    longue l'ont, et le classeur n'en donne pas la définition. Les 67,0 −
    58,7 = 8,3 points ne sont donc pas des femmes à qui leur durée manque à
    l'âge légal ; elles sont entre zéro et 8,3 points, et le modèle en a
    0,2 en 1953. La définition de la DREES n'a pu être lue : la page du
    panorama de 2026 répondait 503 le 5 novembre, et celle du jeu n'en porte
    aucune.
  - L'excès de l'âge légal tient donc aux conditions de départ, non à la
    durée. En 1953, avec la durée de l'EIR, l'âge légal reçoit 61,3 % des
    femmes pour 37,5 : la carrière longue n'en prend que 6,6 pour 13,2,
    l'entre-deux 14,9 pour 26,7. En 1955, la
    génération jugée, 69,5 % de ses femmes ont 40 années et plus, 2,5 points
    de plus que les nées en 1953, ce que la projection de leur durée leur
    donne ; à l'âge légal, 51,5 %, partent au taux plein, autrement, 35,8
    points, dont 14,4 de la carrière de trente à quarante ans du salariat
    privé, 9,0 de sa carrière pleine, 10,4 des fonctionnaires civils de
    l'État et de la CNRACL ; 9,4 de jumelles inaptes, toutes à l'âge légal,
    quand l'EIR en place une part entre les deux âges (point 4 de la
    trente-cinquième version) ; 6,4 avec une décote. Le taux plein par l'âge
    n'a que 6,9 % de ses départs, pour 11,7.
  - Ce qui rendrait l'âge légal à l'EIR n'est pas un autre calage de la
    durée, mais la place des départs des femmes qui ont la leur : la
    carrière longue, l'invalidité et l'inaptitude entre les deux âges, et le
    juge lui-même, la génération 1955 de la grille jugée sur les nées en
    1953 (`GENERATIONS_DES_DEPARTS`), quand le fichier lui donne 4,76
    trimestres de plus.
- *Ce qui ne bouge pas.* Aucun code, aucune donnée, aucun test : le calage
  reste, et rien ne se remesure. La page, qui ne lit pas la population
  (action 157), la grille du coût (décision 11), les témoins, le paquet. Aucune
  règle du scénario 1 : pas d'entrée au journal de veille.

**Ce qui reste**, de ce point :

1. *Au propriétaire* : la définition de la « carrière complète » de la DREES
   (le panorama « Les retraités et les retraites », édition 2026, inaccessible
   le 5 novembre), et une source qui dise, génération par génération, la
   durée validée des femmes autour de la durée requise, plus fine que
   « 40 ans et plus » : sans elle, la part des femmes à qui leur durée manque
   d'un ou deux ans à l'âge légal reste une convention à choisir, non une
   mesure.
2. *Au propriétaire* : le juge des départs de la génération 1955 de la
   grille, les nées en 1953 de l'EIR, deux ans et 4,76 trimestres de durée
   plus tôt ; les départs de la génération 1955 elle-même, quand une enquête
   les publiera.
3. *Les places des départs des femmes* qui ont leur durée, une session :
   la carrière longue des femmes de 1953 de la population, 6,6 % pour 13,2,
   hors de la grille ; les invalides et les inaptes entre les deux âges
   (point 4 de la trente-cinquième version).
