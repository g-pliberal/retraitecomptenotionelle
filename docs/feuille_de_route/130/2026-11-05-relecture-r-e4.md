# Relecture de E3 et des chiffres de E2

File R-E4 de la vague 10, le 5 novembre 2026 : relecture indépendante, contre les sources, du
commit 0284e76 de la session E3 (la CARPIMKO lue au droit : `carpimko_ages_2015`,
`carpimko_assiette_2026`, note `2026-11-05-carte-des-fiches-carpimko-lue-au-droit.md`) et des
chiffres du commit 0e2a786 de la session E2 (note `2026-11-05-retouches-de-la-relecture-r-e3.md`,
la CAVOM). Ni règle, ni donnée, ni test n'est modifié.

**Méthode.** Les index de la DILA récupérés par `dila_index.py --recuperer` (JORF à jour au
3 novembre 2026, LEGI au 2 novembre), lus par `dila_cherche.py --texte`, `--num` et `--le`.
Chaque citation des quatre fiches touchées découpée à ses « [...] » et cherchée, espaces
ramenées, dans le texte qu'elle nomme, par un script ; les quatre fragments qu'il n'a pas
trouvés (les guillemets imbriqués le trompent) relus à la main. Chaque cas rejoué par
`servi_et_refait` (`tests/outils_pont.py`), le portage servi et le moteur Python refait au bit
près, sur la requête des deux notes (deux salaires moyens, naissance le 10 du mois sauf les
nés le 1er de E2). Chaque montant refait à la main à partir des valeurs servies.

## Le verdict

- **E2 : conforme.** Les quatre montants sont exacts dans les deux moteurs, la référence
  « article 3, II » aussi ; un écart faible sur l'arrondi des points.
- **E3 : les citations, les dates de publication et tous les montants sont exacts**, et
  l'erreur (3) est prouvée. Mais **l'erreur (2) n'est pas prouvée, le texte penchant pour le
  modèle (grave)**, et **l'erreur (1) n'est prouvée que de 1984 à 1987, non dans le cas de
  1990 que la fiche pose (moyen)**. Deux points que le texte ne tranche pas, non déclarés
  (un moyen, un faible).

## A. E3, la CARPIMKO

### Les textes et les citations : conformes

- **Les statuts de 1984**, articles 10 à 13 (LEGIARTI000006782879 à 006782882), dans LEGI du
  1er janvier 1984 au 1er janvier 2999, comme la note le dit : les citations des articles 10,
  11 et 12 sont mot pour mot. Les décrets n° 84-143, articles 1er et 6, de même.
- **Les arrêtés de 2015, 2019, 2023 et 2026** : publiés les 2 octobre 2015
  (JORFARTI000031255547), 30 mai 2019 (JORFARTI000038529117), 9 janvier 2024
  (JORFARTI000048880643) et 17 juillet 2026 (JORFARTI000054435915), comme
  `NAISSANCES_AU_JOURNAL_OFFICIEL` le porte ; chaque fragment cité s'y trouve. La mention et
  la note de l'arrêté du 20 novembre 1996 (JORFARTI000002184842, JORFARTI000001794714) aussi.
- **`carpimko_assiette_2026`** : chaque citation se trouve dans son texte (l'article 2 du
  décret n° 84-143, rédaction du 14 novembre 2025, LEGIARTI000052567938, relu à la main).

### L'erreur (1), de 1984 à 1996 : prouvée de 1984 à 1987 seulement — moyen

- **Ce qui est prouvé.** L'article 12 des statuts de 1984 minore selon l'âge seul, « 0,75 si la
  liquidation intervient à soixante ans », sans durée. Le modèle, lui, ne minore pas quand la
  durée est atteinte : l'erreur est réelle tant que ce texte est en vigueur.
- **L'écart.** La fiche (hypothèse de `statuts_de_1984`, lectures) et la note affirment
  qu'« aucun autre arrêté de 1984 à 1996 ne touche les articles 10 à 12 », ceux de 1985 à 1998
  ayant été « lus à leur titre ». Or **l'arrêté du 20 mai 1987 (JORFTEXT000000844323, Journal
  officiel du 4 juin 1987)** porte « approbation des modifications apportées aux régimes
  complémentaires d'assurance vieillesse et d'invalidité-décès de la section professionnelle
  des auxiliaires médicaux et au régime des prestations supplémentaires de vieillesse des
  auxiliaires médicaux conventionnés » : son titre nomme le régime complémentaire
  d'assurance vieillesse, et l'index n'en garde que ce titre, sans article ni annexe. Rien ne
  dit qu'il laisse les articles 10 à 12. Il n'est ni dans `textes_sans_effet` ni dans la note.
  Les autres arrêtés de 1984 à 1996 qui nomment la section ont été rouverts : 5 juin 1985
  (prestations supplémentaires, articles 14 à 20), 13 août 1987 et 19 juin 1991
  (invalidité-décès), 17 novembre 1987 (statuts généraux, article 4), 30 décembre 1988
  (invalidité-décès et prestations supplémentaires), 24 janvier 1989 (article 13), 16
  décembre 1991 (régime complémentaire, article 22 seul, au Bulletin officiel n° 91-50), 29
  juillet 1993 (allocation de vieillesse), 2 octobre 1995 (statuts généraux) : aucun ne
  touche les articles 10 à 12, comme E3 le dit.
- **Conséquence.** La version `statuts_de_1984` n'est lue que jusqu'à l'entrée en vigueur de
  l'arrêté de 1987, que l'index ne date pas ; au-delà, jusqu'en 1996, elle est supposée. Le cas
  de la fiche, une pension prise le 1er avril 1990, tombe après : ses **116,44 € par an**
  (465,78 € servis, 0,75 × 465,78 = 349,33 €, chiffres justes) ne sont pas prouvés par un texte
  lu en vigueur ce jour-là.
- **Un cas prouvé.** Né le 10 mars 1925, entré à 20 ans, à 60 ans le 1er avril 1985 : les deux
  moteurs servent 114,27 € par an sans coefficient ; les statuts, 0,75 × 114,27 = 85,71 €,
  **28,57 € par an de trop**. Entré à 26 ans, les deux moteurs rendent 0,75, 85,71 €, comme les
  statuts.

### L'erreur (2), de 2015 à 2024 : non prouvée, le texte penche pour le modèle — grave

La fiche déclare, dans son intitulé, sa version de 2015, une approximation, et la note, au
propriétaire : les générations 1955 et antérieures perdent « 4 % par année d'anticipation »
avant 65 ans, « que la durée n'annule pas », et le modèle, qui ne les abat pas quand la durée
est atteinte, leur sert 862,45 € par an de trop dans le cas posé. Le texte de 2015
(JORFARTI000031255547) ne le dit pas, et dit plutôt le contraire :

- **L'article 11** attribue la retraite « à taux plein : [...] 2° A partir de 62 ans et avant
  67 ans au profit : a) Des assurés nés à compter du 1er janvier 1961 liquidant leur pension
  du régime de base sans abattement », et renvoie les nés avant 1961 à l'article 12 quater, 1°.
- **L'article 12 quater, 1°**, « Par dérogation aux dispositions de l'article 11 », donne aux
  générations 1960 et antérieures leurs âges, dont, pour la « GÉNÉRATION 1955 ET ANTÉRIEURE » :
  « Age prévu à l'article 11.1 65 ans » et « Age prévu à l'article 11.2 (a) 60 ans ». L'article
  11.2 (a) est une règle de **taux plein** : appliqué à la génération 1955, il sert à taux plein
  dès 60 ans qui liquide sa base sans abattement.
- **L'article 12 quater, 2°** déroge à l'article 12, non à l'article 11 : il fixe « les
  abattements qui sont appliqués en cas de départ anticipé ». Et l'article 12 définit
  l'abattement comme « fonction de l'âge auquel est demandée la liquidation et de la durée
  d'assurance lorsque l'assuré ne justifie pas de la durée prévue dans le régime de base ».
  Lu avec l'article 11, le départ anticipé est celui qui précède le taux plein : les 4 % par
  année et les 0,25 % par trimestre frappent qui n'a pas sa durée, non qui l'a.
- La fiche lit la ligne de l'article 11.2 (a) comme un « âge minimal » (son approximation des
  renvois inversés) ; l'article 11 en fait un âge de taux plein. La lecture de E3 n'est pas
  impossible, mais aucun texte lu ne l'impose, et elle contredit la lettre de l'article 11.

Les chiffres de E3 sont justes dans sa lecture : 5 681,23 € servis, 1,0375 ; 5 681,23 / 1,0375
× 0,88 = 4 818,78 € ; 862,45 €. Entré à 26 ans, 0,85, 4 654,51 € : les deux lectures s'y
accordent, faute de durée.

**Ce qui reste faux dans les deux lectures : la majoration.** L'article 12 ter la fait courir
« au-delà de l'âge auquel elle aurait pu être liquidée sans abattement ». Dans la lecture de E3,
c'est 65 ans ; dans celle de l'article 11, il faut liquider la base sans abattement, ce que
l'assuré né le 10 décembre 1954 ne peut qu'à l'âge légal de la base, 61 ans et 7 mois
(D. 161-2-1-9, 5°, LEGIARTI000025089933), le 10 juillet 2016 : un seul trimestre civil entier
avant le 1er janvier 2017, octobre à décembre, 1,0125. Le modèle en compte trois (avril à
décembre 2016), depuis l'âge où la durée est atteinte, avant l'âge légal de la base :
5 681,23 / 1,0375 × 1,0125 = 5 544,34 €, **136,90 € par an de trop** dans cette lecture, au
lieu de 862,45 €.

**À faire, pour la file E et le propriétaire** : ne plus présenter l'erreur (2) comme prouvée ;
la déclarer comme un point que le texte ne tranche pas, avec ses deux lectures (862,45 € ou
136,90 € par an dans le cas posé), jusqu'à un exemple de la caisse — une pension d'un assuré
né avant 1956, liquidée de 2016 à 2023 avec sa durée. Corriger le modèle sur la lecture de E3
lui ferait perdre 12 % de pension à des assurés que l'article 11 sert à taux plein.

### L'erreur (3), la date d'effet : conforme

L'article 11 de 1984 et l'article 7 du règlement de 2026 fixent l'entrée en jouissance « au
premier jour du trimestre civil qui suit la demande ». Les deux moteurs servent l'assuré né le
10 novembre 1959, entré à 26 ans, dès le 1er décembre 2026, 1,025, 5 706,01 € par an : une date
qui n'est le premier jour d'aucun trimestre civil, d'où une erreur prouvée quelle que soit la
date de la demande. Les montants le sont dans le cas posé, la demande en novembre 2026 :
5 706,01 / 1,025 × 1,0375 = 5 775,59 € ; 5 706,01 / 12 = 475,50 € ; 69,59 € par an. La fiche
dit bien que l'article qui date la pension de 1996 à 2026 n'est pas lu (l'article 11 de 1984
est remplacé en 2015 par un article qui ne la date plus).

### Les autres valeurs : conformes

L'assuré né en 1958, entré à 30 ans, à 62 ans : 0,80, 4 764,36 €, seize trimestres jusqu'à
66 ans. Le test `test_chaque_version_de_la_carpimko_est_portee_par_le_modele` vérifie les
paramètres de chaque version chaque premier du mois, non les écarts que la fiche déclare,
comme sa docstring le dit.

### Ce que le texte ne tranche pas

Déclarés, et justes : l'âge entamé de 1984, l'année d'anticipation de 2015, l'âge de l'inapte
né avant 1961, la majoration pour trois enfants des pensions déjà servies, les renvois inversés.
Non déclarés :

- **La majoration avant l'âge légal de la base — moyen.** Depuis 2015, le modèle fait courir
  la majoration depuis l'âge où la durée est atteinte, cherché depuis l'âge minimal de la caisse
  (`age_ouverture_commun`), même quand la base ne peut pas encore être liquidée ; l'article 11
  lie le taux plein avant l'âge de la table à la liquidation de la base sans abattement. 136,90 €
  par an dans le cas de 1954 ci-dessus. Candidat, à vérifier pour toutes les versions depuis 2015.
- **« L'âge du taux plein » de l'article 12 ter (2015) et de l'article 5 (2026) — faible.** La
  majoration se compte par trimestre « postérieur à l'âge du taux plein », quand l'article 12
  borne l'abattement à « l'âge du taux plein sans condition » : l'âge où l'assuré atteint le
  taux plein, comme le modèle le lit, ou celui de la table. Né le 10 novembre 1959, entré à 20
  ans, à 67 ans : les deux moteurs servent 1,25, vingt trimestres, 7 022,19 € ; compté de 66 ans
  et 4 mois, 1,025, 5 758,20 €, 1 263,99 € par an. La première phrase de l'article, « au-delà
  de l'âge auquel elle aurait pu être liquidée sans abattement », soutient la lecture du modèle.

## B. E2, les chiffres de la CAVOM : conformes

- **L'inapte né avant 1959, 3 207,53 € par an** : né le 10 mars 1955, inapte, entré à 25 ans,
  à 61 ans ; les deux moteurs servent la CAVOM dès le 1er avril 2016, 0,80, 12 830,11 € ;
  12 830,11 / 0,80 = 16 037,64 € ; 3 207,53 €.
- **L'âge de la demande, 1 128,73 € par an** : né le 10 février 1960, à 65 ans ; servie dès le
  1er mars 2025, 0,90, 20 317,08 €. Les âges refaits au jour : la demande du 15 janvier 2025 à
  64 ans, 11 mois et 5 jours ; l'effet au 1er avril 2025, à 65 ans, 1 mois et 22 jours ; 1 an,
  10 mois et 9 jours jusqu'à 67 ans à l'effet, 2 ans et 26 jours à la demande. 20 317,08 / 0,90
  × 0,05 = 1 128,73 €.
- **L'assuré né le 1er, jusqu'à 2 257,69 €** : nés en 1959, à 62 ans, les deux moteurs servent
  le né le 1er mai dès mai 2021, 13 546,16 €, × 2 / 12 = 2 257,69 € ; le né le 1er mars dès
  mars, 13 529,99 €, / 12 = 1 127,50 € ; le né le 1er avril dès avril (13 538,08 €), comme le
  texte. Le premier jour de trimestre civil qui suit l'anniversaire est le plus tôt possible,
  quelle que soit la date de la demande : la condition de (c) est prouvée.
- **« Article 3, II »** : la dérogation de quatre à sept plafonds est bien au II de l'article 3
  du décret n° 2015-1875 (JORFARTI000031740735) ; la note de LEGI à l'article 2 du décret n°
  79-265 (LEGIARTI000038427708) écrit bien « Conformément à l'article 1 II ». Les lignes 110, 172,
  195 et 218 de `regimes/cavom_complementaire.yaml` portent « article 3, II » ; aucune ne garde
  « article 1er, II ».
- **L'arrondi des points, « 0,03 € au plus » — faible.** L'article 4-2 du décret n° 79-265,
  rédaction du décret n° 2026-418 (JORFARTI000054153714), arrête les points « à la deuxième
  décimale par excès » : citation exacte. Mais 0,01 × 3,3745 = 0,0337 € : la borne, arrondie
  vers le bas, est 0,034 € ; elle vaut par cotisation annuelle et s'additionne d'une année à
  l'autre depuis 2026 ; et l'arrondi par excès veut que le modèle serve moins que le texte, ce
  que l'approximation ne dit pas.

## Les tests

`python -m pytest tests/test_carte.py tests/test_sections_liberales.py tests/test_sections_sante.py` :
109 réussis. Sous `PRESOMPTIONS_DECALEES=1`, `test_sections_liberales.py` et
`test_sections_sante.py` : 92 réussis, 1 sauté. Les cas de cette relecture, nés un jour donné,
ne dépendent pas des présomptions ; ceux de E2 nés le 1er ont été joués.

## Ce que la relecture laisse

- **À la file E** : récrire l'erreur (2) en point non tranché, avec ses deux lectures ; borner
  la version `statuts_de_1984` lue à l'arrêté du 20 mai 1987, la suite supposée, et poser le
  cas de l'erreur (1) avant 1987 (28,57 € par an en 1985) ; déclarer la majoration avant l'âge
  légal de la base et « l'âge du taux plein » de l'article 12 ter ; préciser la borne et le
  sens de l'arrondi des points de la CAVOM. Le bloc « Reprise » de l'action 130, qui annonce
  trois erreurs de la CARPIMKO au propriétaire, est à reprendre de même par la file E.
- **Au seul Bulletin officiel, ou à la caisse** : le texte de l'arrêté du 20 mai 1987, en plus
  de celui du 20 novembre 1996.

Sources : index JORF de la DILA (3 novembre 2026) : JORFTEXT000000844323,
JORFTEXT000000292638, 000475761, 000500969, 000498997, 000666704, 000685640, 000685179,
000480553, 000372435 ; JORFARTI000031255547, 038529117, 048880643, 054435915, 002184842,
001794714, 031740735, 054153714. Index LEGI (2 novembre 2026) : LEGIARTI000006782879 à
006782882, 052567938, 054168585, 038427708, 025089933 (D. 161-2-1-9), 025014605 (L. 161-17-2).
