# Étape 14, dix-septième partie : les carrières allongées des femmes, entrées comme les pleines

**Le 25 octobre 2026 : les carrières incomplètes des femmes du salariat privé
que leur génération allonge au-delà de 21 ans avant l'âge légal n'entrent
plus toutes à 21 ans ; la vingt-huitième version, sur `main`. Elles entrent
comme les carrières pleines : à l'âge légal moins leurs années, jamais avant
l'entrée des carrières pleines de leur génération, qui borne désormais leurs
années, puis cinquième par cinquième au premier trimestre cotisé. Nées en
1955, celle de trente à quarante ans valide 44 années, et non 41, entrée à
18 ans pour trois cinquièmes. Les femmes de 1955 partent en carrière longue
pour 12,4 % et non 4,8 (EIR 13,0), avant l'âge légal pour 18,4 % et non 10,8
(21,7) ; celles de 1950 ne bougent pas. Le calage de la durée des femmes ôte
aux carrières plus courtes les années que celles-ci prennent : celles de
vingt à trente ans nées en 1955 attendent désormais 67 ans, quand elles
partaient à 66, le pilote s'arrêtant au bout de ses quatre passes avec une
décote que la mesure ne voyait pas — 25,4 % des départs à l'âge
d'annulation, pour 10,8. La mesure tient sous 10 Go, 7,4 au plus : des morceaux de cent cas
types, la mémoire des calculs coupée. La version reste ; la page ne bouge
pas.**

Demande : la dixième vague du 24 octobre 2026, une session par tâche, lancée
par le propriétaire : l'action 138, étape 14, le point suivant du bloc de
l'étape, et lui seul : « les femmes de 30 à 40 années de carrière, entrées à
21 ans », que la population prend « allongées à l'âge légal, toutes entrées
à 21 ans » d'après la note du 23 octobre (« Ce qui reste », point 1, de la
note de la seizième partie, `2026-10-25-etape-14-natures-selon-le-rang.md`) ;
le pic de mémoire de la mesure sous les 10 Go de la session du 24 octobre.

- *Ce qui était.* Sous la douzième version
  (`DUREE_DES_FEMMES_SELON_LA_GENERATION`), les carrières incomplètes des
  femmes gagnent ou perdent, génération par génération, les années qui
  portent la durée moyenne des femmes à celle que l'EIR mesure aux
  résidentes, sans passer l'âge légal depuis leur entrée, 21 ans, celle du
  gabarit. Les générations récentes en gagnent beaucoup, 5,76 années en
  1950, 9,22 en 1953, 12,22 en 1955 : la carrière de trente à quarante ans,
  35 années pour les retraitées de 2020, en aurait validé 41 en 1950 et 47 en
  1955, et en validait 39, de 21 à 60 ans, et 41, de 21 à 62. Toutes ses
  années étaient prises, de 21 ans à l'âge légal : une carrière pleine,
  entrée à 21 ans, à qui la condition d'entrée de la carrière longue, des
  trimestres cotisés à la fin de l'année des 16, 17 ou 20 ans (D. 351-1-1),
  était fermée. Ces carrières sont 35 % des femmes du régime général de la
  population, 26 % de toutes. La note de la dixième partie le disait
  (`2026-10-19-etape-14-service-national-et-periodes-assimilees.md`) : « La
  femme née en 1953 de la classe p95 dans cette tranche valide 40 années,
  n'en compte qu'une d'assimilée, et part à 61 ans et deux mois au taux
  plein : la condition d'entrée de la carrière longue lui est fermée. »
- *La vingt-huitième version* (`ALLONGEES_COMME_LES_PLEINES`,
  `debut_des_annees`, `allongees_au_premier_trimestre`, le paramètre
  `au_plus_tard` de `classes_d_entree`, 91d7404). La carrière incomplète
  d'une femme du salariat privé compte les années qu'elle peut valider avant
  l'âge légal depuis l'entrée des carrières pleines de sa génération
  (`ENTREE_SELON_LA_GENERATION`) — 16 ans pour les nées avant 1951, 17 en
  1953, 18 en 1955 et en 1960, 21 pour celles qui partent à 64 ans —, et non
  plus depuis 21 ans ; celle dont les années ne tiennent pas entre 21 ans et
  l'âge légal entre à l'âge légal moins ses années, à l'année près. Puis,
  comme les carrières pleines (`ENTREE_AU_PREMIER_TRIMESTRE`), elle se
  décline en cinquièmes, chacun entrant à l'âge où sa génération cotise le
  premier trimestre de son rang s'il vient plus tard, jamais après 21 ans, et
  validant d'autant moins d'années : sa carrière finit où elle finissait.
  Elle garde sa part assimilée, au chômage, comme toute carrière incomplète,
  sans classes de nature ; ses départs avec surcote gardent l'entrée de leur
  génération, sans cinquièmes, comme ceux des carrières pleines. Le calage de
  la durée des femmes (`ecarts_des_femmes`) la compte à l'entrée de sa
  génération, comme il compte les carrières pleines : ce que ses cinquièmes
  tardifs lui ôtent, il ne le voit pas. Les écarts du calage baissent
  d'autant, à 4,97 années en 1950, 7,40 en 1953, 9,76 en 1955, 10,56 en 1960
  et non 13,02 ; les carrières plus courtes en perdent autant, celles des
  non-salariées comprises, qui gardent leur entrée. La carrière de la classe
  p95 de la tranche entre à 20 ans en 1950 pour 40 années, à 19 ans en 1953
  pour 42, à 18 ans en 1955 et en 1960 pour 44, à 19 ans en 1965 pour 44
  encore, à 21 ans en 1970 pour 43, où les carrières pleines entrent aussi à
  21 ans ; nées en 1955, ses
  cinquièmes entrent à 18 ans pour trois — les nées en 1955 cotisent leur
  premier trimestre aux rangs 0,1 à 0,9 à 16, 17, 18, 19 et 21 ans —, à 19 et
  à 21 ans, pour 44, 43 et 41 années. Les 34 carrières de la tranche et leurs
  départs avec décote en font trois classes chacune : 14 874 cas types, et non
  14 738.
- *Les tests.* Un de plus,
  `test_les_carrieres_allongees_entrent_comme_les_pleines` : nées en 1955,
  l'entrée des carrières pleines à 18 ans, 62 − 44,4 arrondi ; l'âge du
  premier trimestre cotisé de chaque cinquième, de 16 à 21 ans, lu dans le
  fichier certifié ; la carrière de la classe p95, 44, 43 et 41 années, à 18
  ans pour trois cinquièmes, à 19 et à 21 ; simulée, son premier cinquième
  valide de 18 à 61 ans, dont une année au chômage, et part à 60 ans en
  carrière longue — 168 trimestres cotisés ou réputés tels, quarante-deux
  années dont les quatre trimestres de chômage que D. 351-1-2 répute depuis
  avril 2014, pour 166 —, le dernier à 62 ans au taux plein, comme avant ;
  la carrière de dix à vingt ans et celle de l'homme gardent leur entrée ;
  sans la version, la carrière entre à 21 ans pour 41 années, du même poids ;
  les carrières pleines sortent identiques. Vu rouge sans la version, la
  carrière entrant à 21 ans pour 41 années. Le test des morceaux de la grille
  en demande cent cas types au plus, et non deux cents (4ad9382).
- *Trouvé en chemin : la masse des natures.* La masse moyenne qui règle les
  natures des femmes selon leur rang (`masses_moyennes`, la vingt-septième
  version) reconnaissait les carrières pleines à leur entrée selon la
  génération : les carrières allongées, qui en ont désormais une, s'y
  mêlaient, et changeaient les natures des carrières pleines — la population
  tombait à 11 974 cas types. Elle ne compte plus que les carrières pleines ;
  le test le tient, les carrières pleines sortant identiques avec et sans la
  version, vu rouge avant.
- *Trouvé en chemin : la mémoire de la mesure.* Un morceau de deux cents cas
  types de la population, simulé seul, tenait 2,63 Go au plus, le worker et
  son portage réunis, en 308 secondes ; un de cent, 1,69 Go en 165. Quatre
  workers qui culminent ensemble, avec les couples allégés que garde le
  processus qui mesure, 2,7 Go à la fin, et ce que chaque worker garde des
  octets de ses calculs (`memoire._EN_MEMOIRE`), un demi-gigaoctet chacun,
  passaient les 10 Go : la mesure de la seizième partie en avait tenu 12,6.
  Les morceaux font désormais cent cas types (`CAS_TYPES_PAR_MORCEAU`, son
  test), et la mesure se lance sans la mémoire des calculs
  (`CALCULS_SANS_MEMOIRE=1`), qui ne lui sert pas : chaque morceau ne s'y
  calcule qu'une fois, et deux arbres figés ne partagent pas leurs calculs.
  Elle tient 6,86 et 7,43 Go au plus, l'arbre de ses processus compté
  entier, en autant de temps.
- *La mesure.* Deux arbres figés sur la tête du jour, 4ad9382, qui porte la
  version, l'un la constante à `False` : `CALCULS_SANS_MEMOIRE=1 python
  scripts/grille_large.py --grille population --distribution --processus 4
  --json <fichier>`, leur `src/` sur le `PYTHONPATH`, l'un après l'autre,
  détachés (`setsid nohup`) : 116 minutes chacun sur les quatre cœurs du
  conteneur, 6,86 et 7,43 Go au plus. « Sans » redonne au dixième la mesure
  de la seizième partie, celle de la vingt-septième version : ni ce qui
  s'est commité depuis, ni les morceaux de cent cas types, ni la mémoire
  coupée ne déplacent la population. La grille du dépôt sort identique des
  deux arbres ; les échecs passent de 15 270 à 15 406, un de plus par cas type
  ajouté, comme avant.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 :

  | | EIR | sans | avec |
  |---|---|---|---|
  | femmes de 1955, avant l'âge légal | 21,7 | 10,8 | 18,4 |
  | femmes de 1955, à l'âge légal | 37,5 | 54,4 | 46,8 |
  | femmes de 1955, entre lui et l'âge d'annulation | 26,7 | 17,1 | 7,8 |
  | femmes de 1955, à l'âge d'annulation | 10,8 | 16,1 | 25,4 |
  | femmes de 1955, carrière longue | 13,0 | 4,8 | 12,4 |
  | femmes de 1955, décote | 12,5 | 3,1 | 4,8 |
  | femmes de 1955, taux plein par l'âge | 12,3 | 15,1 | 24,4 |
  | femmes de 1955, taux plein, autrement | 47,9 | 68,0 | 49,4 |
  | femmes de 1950, carrière longue | 5,1 | 2,3 | 2,3 |
  | ensemble 1955, avant l'âge légal | 30,9 | 23,4 | 27,3 |
  | ensemble 1955, carrière longue | 20,5 | 15,6 | 19,6 |

  Les femmes de 1950 ne bougent pas de plus d'un demi-point : 46,9 % à l'âge
  légal, et non 46,5 (EIR 44,4). Les hommes non plus : 14,1 % en carrière
  longue en 1950 (18,3), 27,5 en 1955 (28,6). La distribution de 2020 : la
  pension moyenne des femmes passe de 1 339 à 1 342 € (EIR 1 177), leur
  médiane de 1 275 à 1 280 € (1 013), l'écart de Kolmogorov reste de −15,8
  points à 900 € ; celle des hommes, que la version ne touche pas, de 1 824 à
  1 818 € (1 957), par la pesée de la page, qui recale chaque groupe sur sa
  dépense. La part des femmes au minimum passe de 30,2 à 30,6 % (EIR 37,7),
  celle des retraitées de 2020 parties avec une décote de 6,7 à 7,3 % (8,8).
  La durée validée de la génération 1950 ne bouge pas, 38,1 années (EIR
  38,2) ; celles de 1955 et de 1960, que 2020 ne voit pas toutes parties,
  passent de 41,9 à 42,2 et de 42,5 à 43,4 (40,6 et 41,2).
- *Ce que cela dit.*
  - La carrière longue des femmes de 1955 rejoint l'EIR, 12,4 % pour 13,0 :
    l'entrée à 21 ans était bien ce qui la leur fermait. Elle vient des
    classes du haut de la tranche, dont les années assimilées sont peu
    nombreuses : relus par `condition_au_depart`, les cinquièmes des classes
    p95 et p99, une année au chômage, partent à 60 ans entrés à 18 ans, à
    60 ans et demi entrés à 19 ; ceux de la classe p90, deux années, à 60 ans
    et demi et à 61 ans et demi ; celui de la classe p75, trois années, à
    61 ans et demi, entré à 18 ans ; le cinquième entré à 21 ans, à 62 ans,
    comme avant. Les classes p10 à p50, huit à dix années au chômage, que la
    carrière longue ne répute que pour quatre trimestres, partent à 62 ans :
    la nature de leurs années assimilées, le chômage de toute carrière
    incomplète, les retient désormais, et non plus leur entrée.
  - Celles de 1950 ne bougent pas : allongées de cinq années, à 40, elles
    entrent à 20 ans, quand la rédaction de 2003, que suivent leurs départs
    d'avant 60 ans, demande des trimestres cotisés à la fin de l'année des
    16 ou 17 ans et 168 trimestres validés. Leur écart à l'EIR, 2,3 % pour
    5,1, n'est pas dans cette tranche.
  - Le calage, lui, ôte deux années et demie aux carrières de vingt à trente
    ans nées en 1955 : 35 années, et non 37. La femme de la classe p50 en a
    156 trimestres, enfants compris, pour 166, et part à 67 ans, au taux plein
    par l'âge. Avec 164, elle partait à 66 ans, non qu'elle y eût le taux
    plein — elle y avait le taux de 48,75 %, deux trimestres de décote, qu'elle
    avait dès 62 ans —, mais parce que le pilote date le taux plein d'une
    carrière comme si elle validait encore quatre trimestres par an
    (`ouvrir.age_taux_plein_droit`), et qu'il s'arrête au bout de quatre passes
    (`pilote.PASSES_LIQUIDATION`) : de 64 ans, l'âge du gabarit, à 64 ans et
    demi, 65, 65 et demi et 66. Sa jumelle qui part décotée, à 62 ans, au même
    taux, était rangée au taux plein elle aussi. La tranche faisait ainsi
    partir un dixième des femmes de 1955 entre l'âge légal et l'âge
    d'annulation, au taux plein, qui n'y avaient pas le taux plein ; elles
    attendent désormais l'âge d'annulation, et la population y en compte 25,4
    %, pour 10,8, et 7,8 % entre les deux âges, pour 26,7. L'écart n'est pas
    de la version, que la mesure d'avant cachait : les carrières courtes des
    femmes, inactives après leurs années, n'ont d'autre taux plein que l'âge
    d'annulation, et la population n'en fait partir que 4,8 % avec une décote,
    quand l'EIR en compte 12,5 % chez les nées en 1953 — la décote selon la
    génération, qui reste.
  - La distribution de 2020 n'en dit presque rien : trois euros.
  - La version reste : elle donne aux femmes de 1955 la carrière longue que
    l'EIR leur trouve, sans rien changer aux carrières pleines ni à celles
    des hommes ; ce qu'elle déplace d'autre, les départs à l'âge d'annulation
    des carrières courtes, découvre le défaut du pilote et la décote qui
    manque, qu'elle ne fait pas.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles ; les
  carrières des hommes et les carrières pleines ; le pilote et le modèle ; le
  registre. Aucune règle du scénario 1 ne change : pas d'entrée au journal de
  veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : la décote selon la génération, que la version
   rend plus pressante — les carrières courtes des femmes de 1955 attendent
   l'âge d'annulation, 25,4 % des départs pour 10,8, et ne partent décotées
   qu'à 4,8 % pour 12,5 — ; le pilote, qui date le taux plein d'une carrière
   inactive comme si elle validait encore et la laisse au bout de quatre
   passes avant l'âge d'annulation, avec une décote que la mesure ne voit pas
   (`ouvrir.age_taux_plein_droit`, `pilote.PASSES_LIQUIDATION`), à reprendre
   au modèle avec ce qu'il déplace ; les natures des carrières incomplètes,
   qui gardent leur chômage — huit à dix années ferment la carrière longue
   aux classes p10 à p50 des carrières allongées — quand l'AVPF des femmes
   qui ont cessé de travailler y est, avec son salaire au Smic dans le salaire
   annuel moyen, et le chômage d'après 60 ans de celles qui attendent le taux
   plein par l'âge ; le plafond de chaque génération, que ses classeurs
   publient pour 1950 et 1953, à certifier, s'il valait de couper le haut des
   rangs, et avec eux la pente des natures des hommes selon le rang ; la
   maternité, que l'échantillon range avec la maladie et que D. 351-1-2
   répute sans limite depuis avril 2014, et que la population tient pour de
   la maladie, quatre trimestres, indépendante de l'AVPF, que rien ne croise
   avec elle ; le calage de la durée des femmes, qui compte les carrières
   pleines et allongées à l'entrée de leur génération, non à celle de leurs
   cinquièmes ; la durée des carrières pleines que la onzième version prend à
   l'EIR ; les invalides et les inaptes, au taux plein dès l'âge légal ; la
   surcote des statutaires ; la part passagère du revenu des indépendants et
   la carrière saisonnière des salariés agricoles, si une source les publie ;
   le juge propre des artisans, la part des liquidants du RSI au minimum
   contributif d'avant 2020 ; la part des générations 1946 à 1953 au minimum ;
   la fragmentation selon la génération ; la décote selon la tranche ou le
   rang. Les niveaux des cas types statutaires et non salariés, et la
   dispersion des libéraux, attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, encore : le départ qui suivrait l'incitation, au
   propriétaire (note de la huitième partie).
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire ; les
   microdonnées de l'échantillon y diraient aussi combien de malades sont au
   chômage, et la part de chaque nature selon le rang.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).

Hors de l'étape : le VI de D. 634-1, la rédaction propre aux artisans et aux
commerçants, à lire rédaction par rédaction (note de la datation) ; ce que
chaque worker garde des calculs qu'il a faits, sans borne
(`memoire._EN_MEMOIRE`) : la mesure s'en passe désormais, sous
`CALCULS_SANS_MEMOIRE=1`.
