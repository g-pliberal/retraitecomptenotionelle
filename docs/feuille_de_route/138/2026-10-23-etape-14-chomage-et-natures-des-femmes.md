# Étape 14, douzième partie : la part du chômage et les natures des femmes

**Le 23 octobre 2026 : les carrières pleines des deux sexes ont désormais les
natures assimilées que l'échantillon interrégimes de cotisants publie,
génération par génération — le service, l'AVPF, le chômage, la maladie —,
chacune à sa part et aux années qu'en a chacun de ceux qui en ont, sous la
masse que l'EIR donne à leur classe de centiles ; la vingt-quatrième version,
sur `main` avec le chômage et l'AVPF certifiés. Le chômage ne va plus qu'à
40 % des hommes (EIC 32,5 % des nés en 1950), l'AVPF à 40 % des femmes
(39,8). Les hommes de la génération 1950 partent en carrière longue pour
11,7 % et non 9,0 (EIR 18,3), avant l'âge légal pour 21,7 % et non 18,8
(27,6) ; ceux de 1955 en carrière longue pour 23,7 % et non 25,8 (28,6 chez
les nés en 1953). Les femmes ne bougent presque pas, ni la distribution de
2020. Répartir toute la masse de l'EIR entre les classes qui ont une nature,
la première forme, mesurée, multipliait leurs années par 1,3 à 2,9 : la
carrière longue des hommes de 1955 tombait à 19,6 %. La version reste ; la
page ne bouge pas.**

Demande : la vague du 23 octobre 2026, lancée par la session de suivi
« Qu'est-ce qu'il reste à faire ? » sur la demande du propriétaire, « Fait
ça », en réponse à l'offre d'une session par chantier qu'une session peut
mener seule : l'action 138, étape 14, le premier point du bloc de l'étape,
la part du chômage et les natures des femmes — le point 1 de « Ce qui
reste » de la note de la onzième partie
(`2026-10-22-etape-14-nature-des-periodes-assimilees.md`).

- *Les données* (`scripts/fetch/drees_natures_assimilees.py`,
  `natures_assimilees.csv`, `tests/test_natures_assimilees.py`). Le même
  fichier de la DREES, « eic2017_data_drees_er », deux types de plus : le
  chômage (« Chômage ») et l'assurance vieillesse des parents au foyer
  (« AVPF »), la part et le cumul des affiliés d'avant 23 ans, à 60 ans ou
  au dernier âge vu. 384 valeurs, les 192 d'avant identiques, certifiées par
  `scripts/verifier_donnees.py` (la seule série, le journal complété d'elle
  seule), la source au registre ; le portail a répondu au troisième essai.
  Ce qu'il dit : nés en 1950, 32,5 % des hommes ont validé du chômage,
  4,3 trimestres par homme, treize chacun, 41,0 % de ceux nés en 1956 ;
  39,8 % des femmes de l'AVPF, 10,5 trimestres par femme, vingt-six chacune,
  45,5 % de celles nées en 1956 ; 37,6 % des femmes du chômage, quatorze
  trimestres chacune ; 2,5 à 5,9 % des hommes de l'AVPF. À 60 ans, les
  hommes nés en 1950 ont validé 9,7 trimestres sans les cotiser — 4,3 de
  chômage, 2,2 de maladie, 1,4 de service, 0,2 d'AVPF, 1,6 d'autres
  natures — ; les femmes 19,8 — 10,5 d'AVPF, 5,4 de chômage, 2,2 de
  maladie, 1,7 d'autres.
- *La vingt-quatrième version* (`NATURES_A_LEUR_PART`, `natures_a_leur_part`,
  `refaire_le_bloc`, `part_et_duree`, le champ `annees_par_nature` de
  `CasTypeLarge`). Sous la vingt-troisième, les années assimilées des
  carrières pleines qui n'étaient ni service ni maladie restaient du chômage,
  à tous les hommes, et toutes celles des femmes : depuis avril 2014, la
  carrière longue en réputait quatre trimestres à chacun. Chaque cinquième
  d'une carrière pleine des deux sexes se décline désormais en cinq classes de
  nature, chacune au milieu de son rang, qui ont les natures que leur
  génération donne à leur rang, chacune à la part des affiliés qui en ont : le
  service et l'AVPF du bas des rangs, le chômage et la maladie du haut — les
  malades sont aussi au chômage. Chaque nature y compte les années qu'a chacun
  de ceux qui en ont, arrondies, une au moins ; la classe qui n'en a aucune
  n'en compte aucune, ses années cotisées. Les années assimilées que la classe
  de centiles tient de l'EIR (la vingt-deuxième version) en sont le plafond :
  quand les classes d'un cinquième en demandent plus, ce que le service leur
  laisse se partage à proportion. Le chômage, l'AVPF et la maladie, qui
  croissent avec l'âge, se lisent à 60 ans, les générations d'après 1956 à la
  part de celle-ci. Nés en 1950, 40 % des hommes sont au chômage (EIC 32,5),
  20 % malades (12,6), 36 % au service (35,1) ; 40 % des femmes à l'AVPF
  (39,8), 40 % au chômage (37,6), 20 % malades (19,4) ; l'AVPF des hommes
  n'atteint pas la première classe. L'homme de la classe p50 né en 1950, trois
  années assimilées : son année de service dans la première classe, aucune
  dans les deux suivantes, trois de chômage dans les deux dernières, quatre de
  maladie de plus dans la dernière. La femme de la classe p50 née en 1950,
  huit années : sept d'AVPF dans les deux premières, quatre de chômage dans
  les deux dernières, trois de maladie de plus dans la dernière ; celle de la
  classe p75, trois années, n'en a que quinze pour les 23,2 que ses natures
  demandent, 0,65 fois chacune : quatre d'AVPF, deux de chômage, deux de
  maladie. La masse des carrières pleines passe de 3,47 à 1,96 années pour les
  hommes nés en 1950, 2,12 pour 1955, de 4,69 à 3,42 et 3,20 pour les femmes ;
  l'échantillon trouve à 60 ans, à tous les affiliés d'avant 23 ans nés en
  1950 et en 1956, 2,4 et 2,7 années aux hommes, 5,0 et 5,6 aux femmes. Chaque
  classe refait son bloc au milieu de sa carrière, centré sur l'ancien, le
  service, la maladie, l'AVPF puis le chômage ; l'AVPF d'avant 1972, qui
  n'existait pas, y reste du chômage. La classe du milieu du rang garde le
  code de son cinquième. 3 742 cas types au lieu de 3 062. Trois tests : le
  chômage et l'AVPF lus ; les classes, posées à la main sur le fichier —
  l'homme né en 1950 de trois années, la femme de huit, celle de trois — ;
  l'homme né en 1950 de la classe p50, entré à 16 ans, dont la classe du
  milieu, sans année assimilée, part en carrière longue à 59 ans et non plus à
  59 ans et demi, la classe au chômage à 59 ans et demi, ses trois années
  n'étant pas réputées cotisées en 2009, et la classe malade et au chômage,
  sept années, à 60 ans, l'âge légal. Deux tests d'avant, la femme du haut
  (vingt-deuxième version) et le service et la maladie (vingt-troisième),
  disent leur version seule, la vingt-quatrième ôtée.
- *La première forme, la masse répartie* (`b679ded`). Elle donnait aux
  classes qui ont une nature toutes les années de leur classe de centiles, à
  proportion des leurs : leurs années passaient celles de l'échantillon de
  1,27 fois pour l'homme de la classe p50 né en 1950 — dix années de chômage
  et de maladie à la classe qui a l'un et l'autre, quand l'échantillon en
  donne sept —, de 1,72 fois pour la femme de la classe p50, de 2,2 fois pour
  l'homme de la classe p10, de 2,9 fois pour la femme des classes du bas née
  en 1942, dix-sept années d'AVPF. La masse de l'EIR, faite de toute la
  carrière, passe ce que l'échantillon voit à 60 ans ; la répartir toute
  chargeait de cet écart les seules classes qui ont une nature. Mesurée, elle
  faisait tomber la carrière longue des hommes de 1955 à 19,6 % : le plafond
  la remplace (`a800a91`).
- *Trouvé en chemin : la mesure de la population s'arrêtait.* Le pont passe
  au portage la demande d'un morceau de la grille d'un seul bloc, que node ne
  lit pas au-delà de 512 Mo, à 1,4 à 1,7 Mo par cas type ; les huit
  morceaux de 468 cas types de la première forme sur quatre cœurs la
  passaient, au bout de 23 minutes, et ceux de 383 de la vingt-troisième
  tenaient de peu. `simuler` coupe désormais ses morceaux à 200 cas types
  (`CAS_TYPES_PAR_MORCEAU`, `morceaux_de`, un test), poussé aussitôt pour ne
  pas laisser la mesure cassée sur `main` (`c722744`).
- *La mesure.* Trois arbres figés sur `b679ded`, leur `src/` sur le
  `PYTHONPATH` : `python scripts/grille_large.py --grille population
  --distribution --processus 4 --json`, l'un après l'autre. Sans la version,
  la constante à `False`, 27 minutes ; la masse répartie, ses morceaux coupés
  à 200 cas types, 29 ; la masse en plafond, de plus, la seule ligne que
  `a800a91` change, 29. « Sans » redonne au dixième la mesure du 22 octobre :
  rien de ce qui s'est commité depuis ne déplace la population.
  Les échecs passent de 3 594 à 4 274, un de plus par cas type ajouté, comme
  avant.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 :

  | | EIR | sans | masse répartie | à leurs années |
  |---|---|---|---|---|
  | hommes de 1950, avant l'âge légal | 27,6 | 18,8 | 18,6 | 21,7 |
  | hommes de 1950, à l'âge légal | 35,3 | 32,4 | 32,5 | 29,4 |
  | hommes de 1950, carrière longue | 18,3 | 9,0 | 8,7 | 11,7 |
  | hommes de 1955, avant l'âge légal | 40,8 | 37,1 | 30,9 | 35,0 |
  | hommes de 1955, à l'âge légal | 24,4 | 20,0 | 26,1 | 21,9 |
  | hommes de 1955, carrière longue | 28,6 | 25,8 | 19,6 | 23,7 |
  | femmes de 1950, avant l'âge légal | 13,0 | 9,4 | 9,2 | 9,2 |
  | femmes de 1950, carrière longue | 5,1 | 3,1 | 2,9 | 2,9 |
  | femmes de 1955, avant l'âge légal | 21,7 | 11,6 | 11,0 | 11,6 |
  | femmes de 1955, carrière longue | 13,0 | 5,5 | 4,9 | 5,4 |
  | ensemble 1950, carrière longue | 11,6 | 6,0 | 5,7 | 7,2 |
  | ensemble 1955, carrière longue | 20,5 | 15,2 | 12,0 | 14,2 |

  Cas type par cas type, relus par `condition_au_depart` : dans la classe
  p10 des hommes nés en 1950, cinq années assimilées, toutes au chômage que
  la rédaction de 2003 ne répute pas, aucune classe ne partait en carrière
  longue ; les trois classes sans chômage du premier cinquième, entrées à
  16 ans, partent désormais à 59 ans en carrière longue, la classe au
  chômage, trois années, à 59 ans et demi. Dans la classe p50, la classe
  malade et au chômage, sept années, perd la carrière longue qu'elle avait à
  59 ans avec trois années de maladie. En 1955, la rédaction de 2014 répute
  quatre trimestres de chômage, que la population donnait à tous : la classe
  malade et au chômage n'en a que huit réputés sur vingt-huit, et part à
  62 ans au taux plein, et non à 60 ans et demi en carrière longue. Les
  femmes : l'AVPF, qui n'est réputée cotisée que depuis septembre 2023, prend
  aux deux premières classes le chômage que les rédactions de 2012 et 2014
  réputaient, et la classe du milieu, sans année assimilée, part plus tôt.

  La distribution de 2020 : la pension moyenne des hommes passe de 1 807 à
  1 819 € (EIR 1 957), leur médiane de 1 591 à 1 601 € (1 745), l'écart de
  Kolmogorov de +5,9 à +5,3 points à 1 800 € ; celle des femmes, de 1 332 à
  1 333 € (1 177), de −15,8 à −15,6 points à 900 €. La durée validée de
  chaque génération ne bouge pas de plus de 0,2 année ; la part des femmes au
  minimum passe de 30,6 à 30,5 % (EIR 37,7).
- *Ce que cela dit.*
  - Le chômage à sa part rend aux hommes de 1950 2,7 points de carrière
    longue : ceux qui n'en ont pas n'ont plus d'années assimilées, que la
    rédaction de 2003 ne réputait pas. L'écart à l'EIR passe de −9,3 à −6,6
    points ; celui des départs d'avant l'âge légal, de −8,8 à −5,9.
  - Ceux de 1955 perdent 2,1 points, qui tiennent à la classe malade et au
    chômage : les classes de nature mettent le chômage et la maladie au haut
    des rangs, et tous les malades au chômage, quand l'échantillon ne dit pas
    combien le sont. L'écart à l'EIR passe de −2,8 à −4,9 points ; les
    départs à l'âge légal s'en rapprochent, de −4,4 à −2,5.
  - Les femmes ne bougent pas : ce que leur carrière longue perd de chômage
    réputé à l'AVPF, la classe sans nature le regagne. Leur écart est
    ailleurs : les carrières de trente à quarante années entrent toutes à
    21 ans.
  - La masse de l'EIR passe les natures de l'échantillon d'une année et demie
    environ par carrière pleine, d'homme comme de femme ; la répartir toute
    sur ceux qui ont une nature contredisait l'échantillon et faisait perdre
    6,2 points de carrière longue aux hommes de 1955. Sous le plafond, ce
    qu'elle a de plus est cotisé : ce qu'elle compte d'après 60 ans, ou des
    autres natures, reste à lire.
  - La distribution de 2020 n'en dit presque rien : douze euros aux hommes.
  - La version reste : elle donne aux deux sexes les natures et les années
    que l'échantillon publie, sous la masse de l'EIR, et rapproche de l'EIR
    les départs d'avant l'âge légal des hommes de 1950 ; ceux de 1955 s'en
    éloignent par la convention des malades au chômage.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles ; les
  carrières incomplètes, qui gardent leur chômage, et les départs avec
  surcote ; le contrôle des liquidants de 2024 sur l'EACR, que la commande ne
  refait pas ; le registre. Aucune règle du scénario 1 ne change : pas
  d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : la masse assimilée des carrières pleines — celle
   de l'EIR, faite des retraités de 2020 et de toute leur carrière, n'est plus
   qu'un plafond, et passe d'une année et demie environ les natures que
   l'échantillon voit à 60 ans : ce qu'elle compte d'après 60 ans et des
   autres natures, génération par génération — ; le chômage des malades, que
   les classes de nature leur donnent à tous ; des classes de nature plus
   fines — cinq donnent 40 % de chômeurs pour 30 à 41 %, 20 % de malades pour
   6 à 15 % — ; les natures des carrières incomplètes, qui gardent leur
   chômage quand l'AVPF des femmes qui ont cessé de travailler y est, avec son
   salaire au Smic dans le salaire annuel moyen ; la maternité, que
   l'échantillon range avec la maladie et que D. 351-1-2 répute sans limite
   depuis avril 2014, et que la population tient pour de la maladie, quatre
   trimestres ; les femmes en carrière longue, les carrières de trente à
   quarante années, allongées à l'âge légal, entrant toutes à 21 ans ; la
   durée des carrières pleines que la onzième version prend à l'EIR ; les
   invalides et les inaptes, au taux plein dès l'âge légal ; la surcote des
   statutaires ; la décote selon la génération ; la part passagère du revenu
   des indépendants et la carrière saisonnière des salariés agricoles, si une
   source les publie ; le juge propre des artisans, la part des liquidants du
   RSI au minimum contributif d'avant 2020 ; la part des générations 1946 à
   1953 au minimum ; la fragmentation selon la génération ; la décote selon la
   tranche ou le rang. Les niveaux des cas types statutaires et non salariés,
   et la dispersion des libéraux, attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, encore : le départ qui suivrait l'incitation, au
   propriétaire (note de la huitième partie).
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).

Hors de l'étape : le VI de D. 634-1, la rédaction propre aux artisans et aux
commerçants, à lire rédaction par rédaction (note de la datation).
