# Étape 14, suite de la neuvième partie : la mesure de l'entrée au premier trimestre cotisé, avec et sans

**Le 19 octobre 2026 : la population est mesurée avec et sans sa vingtième
version, sur le même modèle. Les carrières longues des hommes tombent sur la
borne basse que la neuvième partie en tirait : de 36,9 à 14,8 % des hommes de
la génération 1950 (EIR 18,3), de 37,0 à 22,2 % de ceux de la génération 1955
(28,6 chez les nés en 1953). Leur écart à l'EIR se resserre et change de
signe ; celui des deux sexes ensemble se creuse dans la génération 1955, de
−2,7 à −9,8 points, parce que l'excès des hommes masquait l'absence des
femmes. Les cinquièmes entrés tard partent trop tard, à 62 ans et demi par la
durée, et abaissent la durée validée des hommes ; la distribution de 2020 ne
bouge pas. La vingtième version reste ; la page ne bouge pas.**

Demande : la vague du 19 octobre 2026, première salve, lancée par la session
de suivi « Tâches restantes » sur la demande du propriétaire, « Lance les
sessions qui n'ont pas besoin de moi » : le premier point du bloc « Reprise »
de l'étape, « la mesure de cette entrée, avec et sans (commande dans la
note) » — le point 1 de « Ce qui reste » de la note de la neuvième partie
(`2026-10-18-etape-14-carrieres-longues.md`), par la commande qu'elle donne,
lancée en arrière-plan et attendue jusqu'au bout.

- *La mesure.* Deux arbres figés sur `121bd7c` (`git worktree add --detach`),
  dont le modèle est celui de `2422a20`, la neuvième partie : `python
  scripts/grille_large.py --grille population --distribution --processus 4
  --json avec.json` dans le premier ; la même dans le second, la constante
  `ENTREE_AU_PREMIER_TRIMESTRE` mise à `False`. Lancées l'une après l'autre,
  détachées, sans rien commiter de l'arbre du « sans » : 30 minutes avec la
  vingtième version (2 518 cas types), 24 sans (2 280), sur quatre cœurs. Les
  trois causes que la neuvième partie avait relevées étaient levées : l'arbre
  figé, que le hook de fin de tour ne touche pas ; la pesée, réparée ; et ce
  conteneur paie la mémoire neuve au prix ordinaire (512 Mo touchés en
  3 secondes, quand celui de la veille en demandait 31 à 35).
- *Ce qu'elle trouve*, les départs des hommes de deux générations de la
  population, en part des départs déjà pris à l'âge où l'enquête voit la
  sienne ; la grille 1955 se juge sur les nés en 1953, la plus proche
  génération que l'EIR voie presque toute partie :

  | hommes | 1950, EIR | sans | avec | 1955, EIR 1953 | sans | avec |
  |---|---|---|---|---|---|---|
  | avant l'âge légal | 27,6 | 46,7 | 24,6 | 40,8 | 48,2 | 33,4 |
  | à l'âge légal | 35,3 | 12,1 | 26,7 | 24,4 | 9,1 | 16,3 |
  | entre lui et l'âge d'annulation | 25,4 | 21,8 | 29,4 | 26,4 | 23,2 | 30,7 |
  | à l'âge d'annulation | 7,3 | 17,0 | 17,0 | 5,5 | 17,1 | 17,2 |
  | après lui | 4,4 | 2,4 | 2,4 | 2,8 | 2,3 | 2,3 |
  | carrière longue | 18,3 | 36,9 | 14,8 | 28,6 | 37,0 | 22,2 |
  | décote | 5,6 | 4,9 | 4,9 | 8,7 | 4,9 | 4,9 |
  | surcote | 12,3 | 9,5 | 9,5 | 14,6 | 9,4 | 9,4 |
  | taux plein par l'âge | 9,9 | 15,8 | 15,8 | 7,5 | 16,0 | 16,0 |
  | taux plein, autrement | 53,8 | 33,0 | 55,0 | 40,6 | 32,7 | 47,4 |

  Âge par âge, les hommes de la génération 1950 partent avant 60 ans pour
  24,6 % (46,7 sans ; EIR 27,6), à 60 ans pour 26,7 % (12,1 ; 41,3), à
  62 ans pour 17,8 % (10,5 ; 4,8), à 65 ans pour 19,4 % (19,3 ; 8,3). Les
  femmes ne bougent pas : aucune ne part en carrière longue, avec ou sans
  (5,1 % des nées en 1950 dans l'EIR, 13,0 % des nées en 1953). Les deux
  sexes ensemble, la carrière longue passe de 17,8 à 7,1 % dans la
  génération 1950 (EIR 11,6), de 17,8 à 10,7 % dans la génération 1955
  (20,5) ; le départ avant l'âge légal, de 25,8 à 15,1 % (20,1) et de 26,4 à
  19,3 % (30,9).

  La durée validée moyenne, génération par génération, en années, sans puis
  avec, l'EIR entre parenthèses (la durée d'assurance des résidents,
  majorations comprises) : les hommes, 39,1 puis 38,3 (40,4) en 1940, 39,2
  puis 38,8 (40,8) en 1945, 39,5 puis 39,0 (40,6) en 1950, 40,9 puis 40,6
  (40,9) en 1955, 37,5 puis 37,3 (40,5) en 1960 ; les femmes perdent une à
  trois dixièmes d'année, 38,4 puis 38,2 (38,2) en 1950. Par quintile de
  pension en équivalent carrière complète, les hommes des trois derniers
  passent de 39,7, 39,7 et 40,0 années à 39,1, 39,2 et 39,4 (42 dans l'EIR).

  La distribution de 2020, en euros de 2020 par mois : la pension moyenne des
  hommes passe de 1 803 à 1 806 € (EIR 1 957), leur médiane de 1 592 à
  1 594 € (1 745), leur neuvième décile de 2 944 à 2 943 € (3 242), et
  l'écart de Kolmogorov reste de +5,9 points à 1 800 € ; celle des femmes, de
  1 332 à 1 329 € (1 177), son écart de −16,0 à −15,9 points à 900 €.
- *Ce que cela dit.*
  - La déclinaison fait ce que les cas types annonçaient, et rien de plus :
    la carrière longue des hommes tombe aux deux cinquièmes de ce qu'elle
    était dans la génération 1950, aux trois cinquièmes dans la génération
    1955 : elle venait presque toute des carrières pleines. L'écart des
    hommes à l'EIR se resserre et change de signe : de +18,5 à −3,6 points en
    1950, de +8,4 à −6,4 en 1955. Leur départ avant l'âge légal passe de
    +19,1 à −3,0 points et de +7,4 à −7,4 ; à l'âge légal, de −23,2 à −8,6
    et de −15,3 à −8,1 ; le taux plein, autrement, de −20,9 à +1,2 et de
    −7,9 à +6,8.
  - Les deux sexes ensemble, l'écart se creuse dans la génération 1955, de
    −2,7 à −9,8 points : l'excès des hommes masquait l'absence des femmes,
    13,0 % des nées en 1953 parties en carrière longue, aucune dans la
    population. Dans la génération 1950, il passe de +6,3 à −4,4. Les femmes
    en carrière longue deviennent le premier écart des départs.
  - Les cinquièmes entrés tard partent trop tard. Celui des hommes de la
    génération 1950 entré à 22 ans attend le taux plein par la durée,
    62 ans et demi : 17,8 % des hommes de la génération partent à 62 ans,
    quand l'EIR en compte 4,8. Sa durée validée commence à son premier
    trimestre cotisé, et aucun trimestre validé ne la précède ; l'EIC en voit
    pourtant avant — le service national — : 93,2 % des hommes nés en 1950 et
    affiliés avant 23 ans avaient validé un trimestre à la fin de l'année de
    leurs 21 ans, 84,8 % en avaient cotisé un. Sur la série des trimestres
    validés, que le même fichier publie (`premier_trimestre.csv`), ce dernier
    cinquième entrerait à 21 ans et non à 22, les quatre autres aux mêmes
    âges : il aurait sa durée à 61 ans et demi, sans rejoindre les départs à
    60 ans.
  - Les départs à 60 ans manquent ailleurs : 26,7 % des hommes de la
    génération 1950 partent à 60 ans, pour 41,3 dans l'EIR, et 19,4 % à
    65 ans, l'âge d'annulation, pour 8,3. L'âge d'annulation reste deux à
    trois fois trop chargé chez les hommes (17,0 % pour 7,3 ; 17,2 pour 5,5),
    avec ou sans : ce sont, pour la note de la huitième partie, les invalides
    et les inaptes, au taux plein dès l'âge légal, que la population fait
    attendre.
  - La durée validée des hommes s'éloigne de l'EIR, jusqu'à 0,8 année dans la
    génération 1940 : la vingtième version ne fait jamais entrer plus tôt que
    la onzième, qui donnait aux carrières pleines la durée de celles de
    l'EIR ; elle ne peut que l'abaisser. Les trimestres validés avant le
    premier cotisé n'en rendraient qu'une petite part, dans la génération
    1950 une année d'un cinquième des carrières pleines : la durée des
    carrières pleines que la onzième version prend à l'EIR et l'âge du
    premier trimestre que la vingtième prend à l'EIC restent à accorder.
  - La distribution de 2020 n'en dit rien : ni la moyenne ni l'écart de
    Kolmogorov d'aucun sexe ne bougent de plus de trois euros ou d'un
    dixième de point.
  - La vingtième version reste : sexe par sexe, elle rapproche de l'EIR la
    condition et la place des départs des hommes. Ce qu'elle éloigne, la
    durée validée et le départ à 62 ans de la génération 1950, passe au
    point suivant.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin, script ou test : rien d'autre ne se commite que
  cette note et le bloc « Reprise » de l'étape. Les autres grilles ; le
  contrôle des liquidants de 2024 sur l'EACR (`scripts/controle_eacr.py
  --population`), que la commande ne refait pas ; le registre. Aucune règle
  du scénario 1 : pas d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : la durée des carrières pleines des hommes, que
   l'entrée au premier trimestre cotisé abaisse sous celle de l'EIR — les
   trimestres validés avant le premier cotisé, que la série des trimestres
   validés de l'EIC dit (le dernier cinquième de la génération 1950 entrerait
   à 21 ans et non à 22), et la nature des périodes assimilées, toutes au
   chômage, quand le service national et la maladie sont réputés cotisés pour
   la carrière longue chacun dans sa limite ; l'EIC publie, génération par
   génération, la part des affiliés qui en ont validé de chaque nature, dans
   le même jeu de la DREES — ; les femmes qui ont droit à la carrière longue,
   13,0 % des nées en 1953, devenues le premier écart des départs ; les
   invalides et les inaptes, au taux plein dès l'âge légal ; la surcote des
   statutaires ; la décote selon la génération ; la part passagère du revenu
   des indépendants et la carrière saisonnière des salariés agricoles, si une
   source les publie ; le juge propre des artisans, la part des liquidants du
   RSI au minimum contributif d'avant 2020 ; la part des générations 1946 à
   1953 au minimum ; la fragmentation selon la génération ; la décote selon
   la tranche ou le rang. Les niveaux des cas types statutaires et non
   salariés, et la dispersion des libéraux, attendent l'action 152, au
   propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, encore : le départ qui suivrait l'incitation, au
   propriétaire (note de la huitième partie).
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).
