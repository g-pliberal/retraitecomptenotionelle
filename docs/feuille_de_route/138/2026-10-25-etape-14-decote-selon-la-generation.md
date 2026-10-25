# Étape 14, dix-huitième partie : la décote selon la génération

**Le 25 octobre 2026 : la part des carrières incomplètes de la population qui
part avec une décote suit désormais la génération ; la vingt-neuvième version,
sur `main` (964023c). La quinzième donnait à toutes celle des retraités de
2020, 8,8 % des femmes et 4,5 % des hommes ; chaque génération a la sienne,
celle que l'EIR compte aux nés en 1950 et en 1953, 7,9 et 12,4 % des femmes,
5,6 et 8,6 % des hommes, celle des liquidants de la Cnav de 2024 dès la
génération 1960, 13,7 et 13,0 %, et, avant 1950, 8,3 et 3,6 %, ce qui garde au
stock de 2020 sa part. La grille 1955 part avec une décote pour 8,8 % de ses
départs et non 4,9 (nés en 1953 : 10,7) : 7,0 % des femmes et non 4,8 (12,5),
10,9 % des hommes et non 5,0 (8,7) ; elle attend moins l'âge d'annulation,
18,2 % et non 21,8 (8,3). Le flux du régime général de 2024 décote 15,1 % de
ses liquidants et non 7,1 (Cnav 13,4) ; les hommes de 2020, 8,1 % et non 6,6
(4,5). Une simulation, deux pesées : la mesure tient 5,7 Go au plus, sur trois
cœurs. La version reste ; la page ne bouge pas.**

Demande : la treizième vague du 24 octobre 2026, une session par tâche, lancée
par le propriétaire : l'action 138, étape 14, le point suivant du bloc de
l'étape, et lui seul : la décote selon la génération, que la note de la
dix-septième partie rend plus pressante (« Ce qui reste », point 1,
`2026-10-25-etape-14-carrieres-allongees.md`) ; le pic de mémoire de la mesure
sous les 7,4 Go de cette note, sans relâcher `CAS_TYPES_PAR_MORCEAU`.

- *Ce qui était.* Sous la quinzième version (`DEPARTS_AVEC_DECOTE`), chaque
  carrière incomplète du salariat et des non-salariés se dédouble : une part
  part à l'ouverture du droit, avec une décote, la même pour tout le sexe et
  pour toutes les générations — 14,4 % des carrières incomplètes des femmes,
  23,7 % de celles des hommes —, pour que ses départs pèsent la part que l'EIR
  mesure aux résidents de 2020, 8,8 et 4,5 % (`quintiles_eqcc_residents.csv`).
  L'EIR la voit croître d'une génération à l'autre : 7,9 % des femmes nées en
  1950, 12,4 % des nées en 1953, 5,6 et 8,6 % des hommes
  (`departs_generations.csv`). La note de la huitième partie le disait
  (`2026-10-18-etape-14-departs-choisis.md`) : « la décote, d'une part fixe
  (celle des retraités de 2020), quand elle croît d'une génération à
  l'autre ». La grille 1955 partait avec une décote pour 4,9 % de ses départs,
  pour 10,7 % des nés en 1953 dans l'EIR.
- *La vingt-neuvième version* (`DECOTE_SELON_LA_GENERATION`,
  `decotes_des_generations`, `decote_du_flux`, `parts_des_jumelles`,
  `Variante.parts_des_generations`, `GrilleEnTetes.parts`, 964023c). La part
  des départs avec décote de chaque génération, parmi tous les retraités du
  sexe : celle que l'EIR compte aux nés en 1950 et en 1953, en droite ligne
  entre eux ; celle des liquidants de la Cnav de 2024, 13,7 % des femmes et
  13,0 % des hommes (EACR, table H, `controle_eacr.conditions_publiees`), dès
  la génération 1960, en droite ligne depuis 1953, comme la grille du coût de
  l'étape 3, qui réunit les deux sexes (`part_decotee_de_la_generation`, note
  du 23 octobre) ; avant 1950, une seule, celle qui garde aux générations que
  2020 voit toutes parties, jusqu'à celle de 1953, chacune pesée de son
  effectif INSEE de 2020, la part que l'EIR mesure aux résidents : 8,3 % des
  femmes, 3,6 % des hommes. Rapportée comme avant aux carrières incomplètes,
  elle en fait partir avec une décote, chez les femmes, 13,6 % avant 1950,
  12,9 en 1950, 20,2 en 1953, 20,9 en 1955 et 22,4 dès 1960 ; chez les
  hommes, 19,0, 29,5, 45,3, 51,9 et 68,5 %. Aucune carrière ne change : les
  deux jumelles gardent le poids de la quinzième version, et chacune porte ce
  que chaque génération y change, en paires (génération, part) — nées en
  1955, la jumelle qui décote pèse 1,45 fois son poids chez les femmes et 2,19
  fois chez les hommes, celle qui part au taux plein 0,92 et 0,63 fois. La
  mesure pèse chaque cohorte de la part de sa génération, à son année de
  naissance : les pensions de l'année, les départs des générations 1950 et
  1955, et, hors de `grille_large.py`, les liquidants de 2024
  (`controle_eacr.py --population`, `cohortes_de_la_population`) et la part au
  minimum contributif (`part_minimum_contributif.py`). La population garde
  ses 14 874 cas types. Trois conventions : les parts des nés en 1950 et en
  1953 sont celles de tous les retraités, résidents ou non, quand la
  population et le stock de 2020 ne comptent que des résidents ; les
  générations d'avant 1950 ont toutes la même ; la page, et la pesée qui
  recale chaque groupe du COR sur sa dépense, voient la population sans ces
  parts, au poids de la quinzième version.
- *Les tests.* Quatre de plus.
  `test_la_part_des_departs_avec_decote_suit_la_generation` refait à la main,
  des fichiers certifiés, du témoin de l'EACR et de la pyramide, la part de
  chaque génération — 7,9 % des femmes nées en 1950, 8,3 % de celles d'avant,
  l'homme né en 1980 au flux de la Cnav — ; génération par génération, les
  départs avec décote de la population la pèsent parmi tous les retraités du
  sexe, chaque sexe gardant son poids ; sans la version, une part partout, et
  la part de 2020 à la génération 1955.
  `test_la_mesure_pese_chaque_cohorte_de_la_part_de_sa_generation`, sur la
  grille du dépôt : les pensions de l'année et les départs pèsent chaque
  cohorte de la part de son année de naissance. Et, dans `test_controle_eacr.py`
  (au niveau rapide, comme ses voisins sur une grille d'essai) et
  `test_part_minimum_contributif.py`, les deux mesures qui lisent la
  population hors de `grille_large.py`. Vus rouges avant la version, faute de
  la fonction, du champ et de la part.
- *La mesure.* Une simulation, deux pesées : la version ne change aucune
  carrière, et la population, simulée une fois sur l'arbre figé de 964023c
  (`CALCULS_SANS_MEMOIRE=1`, son `src/` sur le `PYTHONPATH`, détachée), se
  mesure deux fois, avec ses parts et sans elles — la pesée de la
  vingt-huitième version —, comme `grille_large.py --grille population
  --distribution` et `controle_eacr.py --population` la mesurent, les
  proratisations et les conditions de départ de chaque couple calculées une
  fois pour les deux (un pilote hors du dépôt, qui appelle leurs fonctions).
  Sur trois cœurs et non quatre, pour garder le pic loin des 7,4 Go de la
  dix-septième partie : 174 minutes, dont 143 de simulation, 5,67 Go au plus,
  l'arbre de ses processus compté entier. « Sans » redonne au dixième la
  mesure de la dix-septième partie — 4,8 % des femmes de 1955 décotées,
  1 342 € de pension moyenne des femmes en 2020, 15 406 échecs — : ni ce qui
  s'est commité depuis, ni la mesure sur trois cœurs ne déplacent la
  population.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 :

  | | EIR | sans | avec |
  |---|---|---|---|
  | ensemble 1955, décote | 10,7 | 4,9 | 8,8 |
  | ensemble 1955, à l'âge d'annulation | 8,3 | 21,8 | 18,2 |
  | femmes de 1955, décote | 12,5 | 4,8 | 7,0 |
  | femmes de 1955, à l'âge légal | 37,5 | 46,8 | 49,1 |
  | femmes de 1955, entre lui et l'âge d'annulation | 26,7 | 7,8 | 7,5 |
  | femmes de 1955, à l'âge d'annulation | 10,8 | 25,4 | 23,4 |
  | femmes de 1955, taux plein par l'âge | 12,3 | 24,4 | 22,4 |
  | hommes de 1955, décote | 8,7 | 5,0 | 10,9 |
  | hommes de 1955, à l'âge légal | 24,4 | 18,2 | 24,1 |
  | hommes de 1955, à l'âge d'annulation | 5,5 | 17,9 | 12,5 |
  | hommes de 1955, taux plein par l'âge | 7,5 | 16,7 | 11,5 |
  | femmes de 1950, décote | 7,9 | 5,1 | 4,6 |
  | hommes de 1950, décote | 5,6 | 5,0 | 6,2 |

  Et les retraités de 2020 contre l'EIR, ceux de 2024 contre l'EACR (tables C
  et H ; la décote du régime général contre celle de la Cnav) :

  | | EIR, EACR | sans | avec |
  |---|---|---|---|
  | retraitées de 2020 parties avec une décote | 8,8 | 7,3 | 7,8 |
  | retraités de 2020 partis avec une décote | 4,5 | 6,6 | 8,1 |
  | premier quintile des femmes, décote | 17,5 | 18,0 | 19,4 |
  | premier quintile des hommes, décote | 13,6 | 16,9 | 20,5 |
  | pension moyenne des femmes en 2020, € par mois | 1 177 | 1 342 | 1 338 |
  | pension moyenne des hommes en 2020 | 1 957 | 1 818 | 1 807 |
  | femmes au minimum de pension | 37,7 | 30,6 | 30,4 |
  | liquidants de 2024 du régime général, décote | 13,4 | 7,1 | 15,1 |
  | retraités de 2024 du régime général, décote | 9,4 | 8,0 | 10,8 |
  | liquidants de 2024 partis à 62 ans | 26,0 | 51,6 | 57,4 |
  | liquidants de 2024 partis à 67 ans | 10,6 | 25,3 | 20,2 |
  | âge moyen des liquidants de 2024 | 63,60 | 63,01 | 62,75 |

  L'écart de Kolmogorov des femmes passe de −15,8 à −15,6 points à 900 €,
  celui des hommes de +5,1 à +5,5 à 1 800 €. La durée validée des femmes de
  1955 et de 1960 passe de 42,2 à 42,0 et de 43,4 à 43,1 années (EIR 40,6 et
  41,2) ; celle des hommes de 1955, de 40,4 à 39,9 (40,9).
- *Ce que cela dit.*
  - La décote de la grille 1955 rejoint presque l'EIR, 8,8 % pour 10,7, et
    ses départs à l'âge d'annulation baissent d'un sixième : la part fixe de
    2020 était bien ce qui la tenait à moitié. Les hommes de 1955 partent
    désormais à l'âge légal comme dans l'EIR, 24,1 % pour 24,4 (18,2 avant).
  - Les femmes de 1955 restent loin, 7,0 % pour 12,5 : leurs jumelles qui
    décotent pèsent 12,8 % de leur génération, mais un peu plus de la moitié
    seulement d'entre elles partent décotées, les autres ayant le taux plein
    dès l'ouverture — la durée requise, leurs enfants compris —, comme la note
    de la deuxième partie le trouvait déjà
    (`2026-10-16-etape-14-departs-avec-decote.md`). La grille du coût rapporte
    sa part aux seules cohortes qui peuvent décoter
    (`facteurs_depense.part_avec_decote`) ; la population, à toutes ses
    carrières incomplètes. Chez les femmes de 1950, dont la part baisse de 8,8
    à 7,9 %, la décote mesurée s'éloigne d'autant, 4,6 % pour 7,9.
  - Les hommes de 1955 passent au-delà, 10,9 % pour 8,7 : leurs carrières
    incomplètes portent la part de toute leur génération, 9,9 %, et presque
    toutes décotent, sans enfants qui les complètent ; s'y ajoutent les agents
    des IEG et de la conduite nés depuis 1955, qui partent décotés à
    l'ouverture de leur statut (note de la deuxième partie), quand la part de
    l'EIR les compte déjà.
  - Le stock de 2020 s'en ressent : les générations d'avant 1954 y gardent en
    moyenne la part de l'EIR, par construction, mais celles de 1954 à 1958, que
    2020 voit partir, y prennent la leur, 12,6 à 13,3 % des femmes, 9,2 à 11,7 %
    des hommes, et leurs jumelles qui décotent, parties à l'ouverture, y sont
    déjà quand celles du taux plein attendent l'âge d'annulation. Les femmes
    décotées de 2020 s'approchent de l'EIR, 7,8 % pour 8,8 ; les hommes s'en
    éloignent, 8,1 % pour 4,5.
  - Le flux du régime général de 2024 prend la décote de la Cnav, 15,1 % pour
    13,4, ses générations portant la part de ses liquidants ; ses départs à
    62 ans gonflent d'autant, 57,4 % pour 26,0, ceux de 63 à 66 ans restant
    rares, 10,7 % pour 38,5 : la population part à l'âge légal ou à l'âge
    d'annulation, rarement entre les deux (le pilote, note de la dix-septième
    partie).
  - La distribution de 2020 n'en dit presque rien : quatre euros de moins aux
    femmes, onze aux hommes.
  - La version reste : elle donne à chaque génération la décote que l'EIR et
    l'EACR lui trouvent, rapproche de l'EIR la décote, les départs à l'âge
    légal des hommes et à l'âge d'annulation de la grille 1955, et le flux de
    2024 de la Cnav ; ce qu'elle éloigne — les femmes de 1950, les hommes de
    1955 et de 2020 — tient à ce qu'elle ne fait pas : rapporter la part aux
    carrières qui peuvent décoter, en ôter ce que les statutaires décotent
    déjà.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles, qui n'ont
  pas de décote ; les carrières, toutes, et leurs cas types ; le pilote et le
  modèle ; le registre, dont aucun point « 138.14 » ne nomme la décote. Aucune
  règle du scénario 1 ne change : pas d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : le pilote, qui date le taux plein d'une carrière
   inactive comme si elle validait encore et la laisse au bout de quatre
   passes avant l'âge d'annulation, avec une décote que la mesure ne voit pas
   (`ouvrir.age_taux_plein_droit`, `pilote.PASSES_LIQUIDATION`), à reprendre
   au modèle avec ce qu'il déplace — les femmes de 1955 attendent l'âge
   d'annulation pour 23,4 % de leurs départs (10,8), et ne partent entre lui
   et l'âge légal que pour 7,5 % (26,7) — ; la part des départs avec décote
   rapportée aux carrières qui peuvent décoter à l'ouverture, comme la grille
   du coût (`facteurs_depense.part_avec_decote`), et non à toutes les
   carrières incomplètes, et, chez les hommes, sans ce que les agents des IEG
   et de la conduite décotent déjà à l'ouverture de leur statut ; les parts
   des nés en 1950 et en 1953 parmi les seuls résidents, si l'EIR les publie ;
   les natures des carrières incomplètes, qui gardent leur chômage — huit à
   dix années ferment la carrière longue aux classes p10 à p50 des carrières
   allongées — quand l'AVPF des femmes qui ont cessé de travailler y est, avec
   son salaire au Smic dans le salaire annuel moyen, et le chômage d'après
   60 ans de celles qui attendent le taux plein par l'âge ; le plafond de
   chaque génération, que ses classeurs publient pour 1950 et 1953, à
   certifier, s'il valait de couper le haut des rangs, et avec eux la pente
   des natures des hommes selon le rang ; la maternité, que l'échantillon
   range avec la maladie et que D. 351-1-2 répute sans limite depuis avril
   2014, et que la population tient pour de la maladie, quatre trimestres,
   indépendante de l'AVPF, que rien ne croise avec elle ; le calage de la
   durée des femmes, qui compte les carrières pleines et allongées à l'entrée
   de leur génération, non à celle de leurs cinquièmes ; la durée des
   carrières pleines que la onzième version prend à l'EIR ; les invalides et
   les inaptes, au taux plein dès l'âge légal ; la surcote des statutaires ;
   la part passagère du revenu des indépendants et la carrière saisonnière
   des salariés agricoles, si une source les publie ; le juge propre des
   artisans, la part des liquidants du RSI au minimum contributif d'avant
   2020 ; la part des générations 1946 à 1953 au minimum ; la fragmentation
   selon la génération ; la décote selon la tranche ou le rang. Les niveaux
   des cas types statutaires et non salariés, et la dispersion des libéraux,
   attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire : elle pèserait
   aussi chaque cohorte de la part de sa génération, que ni la page ni sa
   pesée des groupes du COR ne voient.
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
(`memoire._EN_MEMOIRE`) : la mesure s'en passe, sous `CALCULS_SANS_MEMOIRE=1`.
