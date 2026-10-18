# Étape 14, neuvième partie : les carrières longues des hommes — les carrières pleines entrent au premier trimestre cotisé

**Le 18 octobre 2026 : les carrières pleines du salariat privé de la
population n'entrent plus toutes au même âge. Cinquième par cinquième, elles
entrent à l'âge où leur génération cotise son premier trimestre, que
l'échantillon interrégimes de cotisants de 2017 publie
(`premier_trimestre.csv`, certifié), jamais avant l'âge de la onzième
version : une carrière pleine d'homme sur cinq née en 1950 entrait jusqu'ici
à 16 ans au lieu de 22, et aucune ne manquait la condition d'entrée de la
carrière longue. La mesure de la population, avec et sans cette vingtième
version, n'a pas pu se faire dans cette session : elle reste à faire, sa
commande est plus bas. En chemin, la pesée de la page aligne la grille une
fois, et non une fois par cas type. La page ne bouge pas.**

Demande : la vague du 18 octobre 2026, lancée par la session d'orchestration
sur la demande du propriétaire, « Fait toutes les tâches qui n'ont pas besoin
de mes décisions » : le premier point du bloc « Reprise » de l'étape, « les
carrières longues des hommes, trop nombreuses » — le point 1 de « Ce qui
reste » de la note du 18 octobre (`2026-10-18-etape-14-departs-choisis.md`) :
« une part des carrières pleines des hommes qui entre plus tard, [...]
d'après l'âge du premier trimestre validé par génération, si une source le
publie (EIC) ». La session d'orchestration a demandé de conclure sans la
mesure, après huit heures.

- *La source* (`scripts/fetch/drees_premier_trimestre.py`,
  `macro/premier_trimestre.csv`, certifiée, `drees_eic_droits_valides`).
  L'échantillon lui-même ne se lit qu'au CASD (`drees_eic`) ; la DREES en
  publie les données détaillées de 2017, en accès libre, dans le jeu « Les
  droits validés au cours de la carrière » : génération par génération —
  1942, 1946, 1950, puis une sur deux de 1954 à 1994 —, sexe par sexe, âge
  par âge, le nombre et le cumul des trimestres de chaque nature, et la part
  des affiliés qui en ont validé. On en garde la part des affiliés d'avant
  23 ans qui avaient validé un trimestre, et cotisé un trimestre, à la fin de
  l'année de chaque âge de 16 à 23 ans : la loi de l'âge du premier
  trimestre. Le lecteur vérifie que chaque part cumule et que celle des
  trimestres cotisés reste sous celle des trimestres validés. 38,2 % des
  hommes nés en 1950 avaient cotisé un trimestre à la fin de l'année de leurs
  16 ans, 72,3 % à celle de leurs 19 ans ; 29,9 et 77,7 % de ceux nés en
  1954. Le service national sépare les deux séries : 93,4 % des hommes nés en
  1954 avaient validé un trimestre à 20 ans, 84,0 % en avaient cotisé un.
  Deux tests (`test_premier_trimestre.py`) : le lecteur, sur des lignes
  écrites comme celles du fichier, et les valeurs que le fichier publie.
- *La vingtième version* (`ENTREE_AU_PREMIER_TRIMESTRE`, `CLASSES_D_ENTREE`,
  `premiers_trimestres`, `age_du_premier_trimestre`, `classes_d_entree`,
  `entrees_au_premier_trimestre`). La condition d'entrée de la carrière
  longue se lit sur les trimestres cotisés à la fin de l'année des 16, 17 ou
  20 ans (D. 351-1-1, `CarriereLongue._entree_precoce`) ; la onzième version
  faisait entrer toutes les carrières pleines assez tôt pour y satisfaire.
  Chaque carrière pleine du salariat privé, hors des départs avec surcote, se
  décline désormais en cinq cinquièmes de poids égal, rangés par l'âge où
  leur génération cotise son premier trimestre : chacun entre, génération par
  génération, au premier âge où la part des affiliés d'avant 23 ans qui l'ont
  cotisé, rapportée à celle de 23 ans, atteint le milieu de son rang ; les
  parts s'interpolent entre les générations de l'échantillon. Trois
  conventions. Le cinquième n'entre jamais avant l'âge de la onzième version,
  qui donne aux carrières pleines la durée de celles de l'EIR : il entre plus
  tard quand l'EIC le dit, jamais plus tôt, et les générations nées après
  1965, que la onzième version fait entrer à 20 ou 21 ans, gardent presque
  toutes leur entrée. Les cinquièmes qui entrent au même âge à chaque
  génération n'en font qu'un : les deux premiers des hommes, sous le code de
  la carrière. Les départs avec surcote gardent leur entrée : ils renoncent à
  la carrière longue, et la population, que la page pèse à un coût qui croît
  comme le carré de ses cas types, passe déjà de 2 280 à 2 518. Les hommes
  nés en 1950 entrent à 16 ans pour deux cinquièmes, à 17, 19 et 22 ans pour
  un chacun ; nés en 1955, à 17 ans pour trois cinquièmes, à 18 et à 21 ans.
  Trois tests (`test_grille_large.py`) : l'âge du premier trimestre lu dans le
  fichier certifié, la déclinaison des carrières pleines, et l'homme né en
  1955 entré à 21 ans, qui part à 62 ans et demi au taux plein quand celui
  entré à 17 ans part en carrière longue.
- *Ce que disent les cas types*, sans la mesure : l'homme médian d'une
  carrière pleine (`salarie_prive~h~40_plus~p50`), cinquième par cinquième,
  au scénario 1 de la page (`condition_au_depart`).

  | génération | entré à | part à | condition |
  |---|---|---|---|
  | 1950 | 16 ans (deux cinquièmes) | 59 ans et demi | carrière longue |
  | 1950 | 17 ou 19 ans | 60 ans | taux plein, à l'âge légal |
  | 1950 | 22 ans | 62 ans et demi | taux plein, par la durée |
  | 1955 | 17 ans (trois cinquièmes) | 61 ans et demi | carrière longue |
  | 1955 | 18 ans | 62 ans | taux plein, à l'âge légal |
  | 1955 | 21 ans | 62 ans et demi | taux plein, par la durée |

  Deux cinquièmes des carrières pleines des hommes nés en 1950 partent en
  carrière longue, trois de ceux nés en 1955, quand toutes le faisaient. Si
  les carrières longues de la population venaient toutes de ces carrières,
  elles passeraient de 37,0 à 15 % des hommes de la génération 1950 (EIR 18,3)
  et de 37,1 à 22 % de ceux de la génération 1955 (EIR 28,6) : une borne
  basse, que la mesure doit dire. L'homme entré à 18 ans en 1955 rate la carrière
  longue de deux trimestres : ses seize trimestres assimilés sont tous du
  chômage, dont quatre seulement sont réputés cotisés, quand ceux d'un homme
  de sa génération sont aussi du service national et de la maladie, réputés
  cotisés chacun dans sa limite (D. 351-1-2, `_reputes_assimiles`).
- *La mesure, laissée à une autre session.* Trois mesures de la population
  sont mortes à la limite de deux heures des commandes de fond, deux autres
  ont été arrêtées après 1 h 44, encore à simuler. Trois causes. Le hook de
  fin de tour rapatrie `main` : qu'un fichier Python du modèle change en
  cours de calcul, et la mémoire ne garde plus rien (`memoire._code_retouche`) ;
  la mesure se lance donc dans un arbre figé (`git worktree add --detach
  <dossier> HEAD`). La pesée réalignait toute la grille pour chaque cas type :
  réparé, plus bas. Et ce conteneur paie cent fois chaque page de mémoire
  neuve (512 Mo touchés en 31 à 35 secondes, puis en 3) : la simulation de
  la population, qui avait pris 25 minutes sur quatre cœurs l'après-midi,
  n'avait pas fini en 1 h 44 sur deux fois deux. La commande, dans l'arbre
  figé, pour la mesure avec la vingtième version : `python
  scripts/grille_large.py --grille population --distribution --processus 4
  --json avec.json` ; puis la même, la constante
  `ENTREE_AU_PREMIER_TRIMESTRE` mise à `False` le temps de la mesure, pour
  celle d'avant sur la même base : le modèle a changé depuis la mesure de la
  huitième partie. À lire : la condition des départs des générations 1950
  et 1955 contre l'EIR, par sexe, et leur place ; la durée validée par
  génération, que les cinquièmes tardifs abaissent ; la distribution de 2020.
- *Trouvé en chemin : la pesée réalignait toute la grille pour chaque cas
  type.* `cout._poids_par_groupe` pèse chaque cas type seul, ses survivants
  alignés sur toute la grille ; il refaisait cet alignement, le même, pour
  chacun : 2 518 alignements de 67 454 pensionnés, de 100 à 400 secondes
  chacun dans ce conteneur. L'alignement se fait désormais une fois, et passe
  à `_masses_regimes` (`alignees`) : les poids sont les mêmes,
  `test_cout.py` entier est vert (178 tests). La pesée reste quadratique dans
  ses boucles, non plus dans ses alignements.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur ni témoin ; les autres grilles ; le registre, où aucun
  point ne porte sur l'âge du premier trimestre — celui de TRAJECTOiRE, ses
  750 000 carrières de l'EIC, reste `a_reprendre`, l'échantillon ne se lisant
  qu'au CASD. Aucune règle du scénario 1 : l'entrée du journal de veille ne
  consigne que la source.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La mesure de la vingtième version*, avec et sans, comme dit plus haut.
2. *La population*, encore : la nature des périodes assimilées, toutes au
   chômage, quand le service national et la maladie sont réputés cotisés pour
   la carrière longue chacun dans sa limite — l'EIC publie, génération par
   génération, la part des affiliés qui en ont validé de chaque nature, dans
   le même fichier —, et les femmes qui ont droit à la carrière longue, 13,0 %
   des nées en 1953 ; les invalides et les inaptes, au taux plein dès l'âge
   légal ; la surcote des statutaires ; la décote selon la génération ; la
   part passagère du revenu des indépendants et la carrière saisonnière des
   salariés agricoles, si une source les publie ; le juge propre des
   artisans, la part des liquidants du RSI au minimum contributif d'avant
   2020 ; la part des générations 1946 à 1953 au minimum ; la fragmentation
   selon la génération ; la décote selon la tranche ou le rang. Les niveaux
   des cas types statutaires et non salariés, et la dispersion des libéraux,
   attendent l'action 152, au propriétaire.
3. *La page qui lit ses agrégats* (action 157), au propriétaire.
4. *Les départs choisis*, encore : le départ qui suivrait l'incitation, au
   propriétaire (note de la huitième partie).
5. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
6. *La confrontation pension par pension*, au CASD, au propriétaire.
7. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).
