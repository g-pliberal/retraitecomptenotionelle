# Étape 14, vingtième partie : la décote des carrières qui peuvent décoter

**Le 25 octobre 2026 : la part des départs avec décote de chaque génération se
rapporte aux seules carrières incomplètes qui peuvent décoter à l'ouverture du
droit, comme la grille du coût, et se prend sans ce que les agents des IEG et
de la conduite décotent déjà à l'ouverture de leur statut ; la trentième
version, sur `main` (bc72979). Les femmes rejoignent l'EIR : 12,9 % de celles
de 1955 partent avec une décote, et non 7,0 (12,5), 8,2 % de celles de 1950, et
non 4,6 (7,9) ; celles de 1955 attendent moins l'âge d'annulation, 17,9 % de
leurs départs et non 23,4 (10,8), mais partent plus à l'âge légal, 53,9 % et
non 49,1 (37,5). Les hommes de 1950 et de 1955 ne bougent pas : les agents ne
décotent qu'à partir des générations 1960 et 1965 ; les hommes qui liquident
au régime général en 2024 décotent 17,8 % et non 21,2 (Cnav 13,0). Les femmes
décotées du stock de 2020 et du flux de 2024 passent au-delà, 10,5 % pour 8,8
et 17,2 % pour 13,7. Une simulation, deux pesées ; la mesure tient 5,6 Go au
plus. La version reste ; la page ne bouge pas.**

Demande : la dix-neuvième vague du 25 octobre 2026, une session par tâche,
lancée par le propriétaire : l'action 138, étape 14, le point suivant du bloc
de l'étape, et lui seul : la décote rapportée aux carrières qui peuvent
décoter (« Ce qui reste », point 1, de la note de la dix-neuvième partie,
`2026-10-25-etape-14-pilote-des-carrieres-inactives.md`) ; le pic de mémoire
de la mesure sous les 7,4 Go du 25 octobre, sans relâcher
`CAS_TYPES_PAR_MORCEAU`.

- *Ce qui était.* Sous la vingt-neuvième version (`DECOTE_SELON_LA_GENERATION`),
  chaque génération fait partir avec une décote la part de ses retraités que
  l'EIR et l'EACR lui trouvent, rapportée, comme sous la quinzième, à toutes
  les carrières incomplètes du sexe (`part_des_incompletes`). La grille du
  coût la rapporte aux seules cohortes qui peuvent décoter
  (`facteurs_depense.part_avec_decote`, `dates_a_l_age_legal`). Or toutes ne
  le peuvent pas : née en 1955, la femme d'une carrière de trente à quarante
  ans, que sa génération porte à 44 années validées, en a 176 trimestres, 192
  avec les huit de chacun de ses deux enfants (L. 351-4), pour 166 requis ; sa
  jumelle « décotée » part à 62 ans au taux plein. La note de la dix-huitième
  partie le trouvait : les jumelles des femmes de 1955 pesaient 12,8 % de leur
  génération, et un peu plus de la moitié seulement partaient décotées. Les
  agents des IEG et de la conduite, qui partent à l'ouverture de leur statut,
  décotaient en plus des jumelles, quand les parts de l'EIR et de la Cnav que
  la population prête à tous les retraités du sexe les comptent déjà.
- *La trentième version* (`DECOTE_DES_CARRIERES_QUI_LE_PEUVENT`,
  `decote_a_l_ouverture`, `ouvertures_decotees`, `parts_des_jumelles`,
  bc72979). Chaque carrière incomplète qui part au taux plein, et chaque
  carrière qui part à l'ouverture de son statut, se juge à chacune des
  vingt-neuf générations de la grille, de 1880 à 2020. La première décoterait
  à l'ouverture si le droit de sa génération l'y ouvre avant l'âge de son taux
  plein, que le pilote fixe : le critère d'âge d'`avec_decote`, celui de la
  grille du coût. La seconde y décote si elle y prend un taux plus bas que
  celui de son taux plein (`avec_decote`) : l'agent des IEG né en 1955 part à
  55 ans au taux de 75 %, né en 1965 à 56 ans et 4 mois au taux de 60 %. La
  part de chaque année de naissance — celle que l'EIR et l'EACR donnent à sa
  génération, fois le poids de tous les retraités du sexe, moins celui des
  agents qui y décotent — se rapporte au poids des carrières qui peuvent
  décoter à la génération simulée dont elle est une cohorte, une au plus ; la
  jumelle qui décote d'une carrière qui ne le peut pas ne pèse rien, celle du
  taux plein portant tout le poids de la carrière. Les deux jumelles gardent
  le poids de la quinzième version, que la page et la pesée des groupes du COR
  voient ; la population garde ses 14 874 cas types et chacune de ses
  carrières. Le jugement porte sur les 48 carrières incomplètes et les 8
  carrières des agents de la population avant sa déclinaison par le rang,
  vingt-deux secondes que la mémoire des calculs garde. Les agents pèsent 5,7 %
  des hommes et 1,3 % des femmes ; les jumelles des hommes nés depuis 1963 ne
  décotent plus que 7,3 % des hommes, et non 13,0. La génération 1880 n'a
  aucune carrière qui puisse décoter, et celle de 1905 trop peu : ses hommes
  décotent 3,0 % et non 3,6. Deux conventions. Une carrière peut décoter
  quand elle le peut au salaire de son cas type : 234 des 17 980 couples de
  ses déclinaisons — des femmes du salariat privé des classes p10 et p25, à
  l'emploi fragmenté, le plus souvent à temps partiel, et six artisanes de la
  classe p10 — le pourraient quand leur carrière ne le peut pas, et ne
  décotent pas ; aucun ne décote qui ne le pourrait pas. Et le critère d'âge
  rend le verdict d'`avec_decote` à 1 391 des 1 392 couples jugés, la carrière
  d'artisane de trente à quarante ans de la génération 1960 ayant le même taux
  aux deux âges.
- *Les tests.* Deux de plus (`test_grille_large.py`).
  `test_une_carriere_decote_a_l_ouverture_quand_le_droit_l_y_ouvre_avant_son_taux_plein`
  pose à la main l'homme de vingt-cinq années né en 1955 (100 trimestres sur
  166 à 62 ans, le taux plein à 67, L. 351-8, 1°), la femme de trente à
  quarante ans née en 1955 (192 trimestres) et en 1925 (144 des 150 que le
  taux plein demande à 60 ans depuis 1983), l'agent des IEG né en 1955 et en
  1965.
  `test_la_part_des_departs_avec_decote_se_rapporte_aux_carrieres_qui_peuvent_decoter`
  refait à la main la part de chaque année de naissance de 1953 à 1957 et de
  1963 à 1967 (`_decotes_attendues`, tirée du test de la vingt-neuvième
  version), juge les agents par `avec_decote` — aucun ne décote chez les nés
  de 1953 à 1957, tous chez ceux de 1963 à 1967 — et chaque jumelle qui pèse
  quelque chose par `decote_a_l_ouverture` : les départs avec décote, des
  jumelles et des agents, pèsent la part de leur génération, chaque carrière
  son poids. Vus rouges faute de la version et de la fonction. Le test de la
  vingt-neuvième version la tient seule ; les sept tests qui reconstruisent la
  population sous `monkeypatch` sans regarder la décote s'en passent
  (`sans_le_reperage_des_decotes`), la mémoire des calculs s'y taisant : le
  fichier tient 80 s sur quatre cœurs, et non 300. La suite complète de GitHub
  est verte sur bc72979, en 18 min 47 s (18 min 12 s sur 7abb4b9).
- *La mesure.* Une simulation, deux pesées : la version ne change aucune
  carrière, et la population, simulée une fois sur l'arbre figé de 49eb036
  (`CALCULS_SANS_MEMOIRE=1`, son `src/` sur le `PYTHONPATH`, détachée), se
  pèse deux fois, avec les parts de la vingt-neuvième version et avec celles
  de la trentième, comme `grille_large.py --grille population --distribution`
  et `controle_eacr.py --population` la mesurent, les proratisations et les
  conditions de départ de chaque couple calculées une fois pour les deux (un
  pilote hors du dépôt, qui appelle leurs fonctions). Sur trois cœurs, des
  morceaux de cent cas types : 163 minutes, dont 134 de simulation, 5,59 Go au
  plus, l'arbre de ses processus compté entier. La pesée de la vingt-neuvième
  version redonne au dixième la colonne « avec » de la note de la dix-huitième
  partie, prise sur 964023c — 15 406 échecs, 1 338 € de pension moyenne des
  femmes en 2020 — : ni le pilote (63dbccd), ni l'entrée d'un relevé (710b582)
  ne déplacent la population. Les parts de la tête de `main` (71bdc58), après
  le retour à la CRPCEN et aux IEG (b99d4d5), sont celles de la mesure.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 :

  | | EIR | vingt-neuvième | trentième |
  |---|---|---|---|
  | ensemble 1955, décote | 10,7 | 8,8 | 11,9 |
  | ensemble 1955, à l'âge d'annulation | 8,3 | 18,2 | 15,3 |
  | femmes de 1955, décote | 12,5 | 7,0 | 12,9 |
  | femmes de 1955, à l'âge légal | 37,5 | 49,1 | 53,9 |
  | femmes de 1955, entre lui et l'âge d'annulation | 26,7 | 7,5 | 8,5 |
  | femmes de 1955, à l'âge d'annulation | 10,8 | 23,4 | 17,9 |
  | femmes de 1955, taux plein par l'âge | 12,3 | 22,4 | 17,2 |
  | femmes de 1955, surcote | 14,3 | 8,6 | 9,8 |
  | hommes de 1955, décote | 8,7 | 10,9 | 10,9 |
  | femmes de 1950, décote | 7,9 | 4,6 | 8,2 |
  | femmes de 1950, à l'âge d'annulation | 15,3 | 27,6 | 24,3 |
  | hommes de 1950, décote | 5,6 | 6,2 | 6,2 |

  Et les retraités de 2020 contre l'EIR, ceux de 2024 contre l'EACR (tables C
  et H ; la décote du régime général contre celle de la Cnav) :

  | | EIR, EACR | vingt-neuvième | trentième |
  |---|---|---|---|
  | retraitées de 2020 parties avec une décote | 8,8 | 7,8 | 10,5 |
  | retraités de 2020 partis avec une décote | 4,5 | 8,1 | 8,0 |
  | premier quintile des femmes, décote | 17,5 | 19,4 | 26,7 |
  | quatre autres quintiles des femmes, décote | 4,6 à 5,4 | 2,2 à 4,0 | 2,5 à 5,4 |
  | premier quintile des hommes, décote | 13,6 | 20,5 | 20,6 |
  | pension moyenne des femmes en 2020, € par mois | 1 177 | 1 338 | 1 325 |
  | premier décile des femmes | 283 | 413 | 393 |
  | pension moyenne des hommes en 2020 | 1 957 | 1 807 | 1 808 |
  | femmes au minimum de pension | 37,7 | 30,4 | 29,4 |
  | liquidantes de 2024 du régime général, décote | 13,7 | 10,1 | 17,2 |
  | liquidants de 2024 du régime général, décote | 13,0 | 21,2 | 17,8 |
  | les deux sexes | 13,4 | 15,1 | 17,4 |
  | retraités de 2024 du régime général, décote | 9,4 | 10,8 | 12,7 |
  | liquidants de 2024 partis à 62 ans | 26,0 | 57,4 | 59,3 |
  | liquidants de 2024 partis à 67 ans | 10,6 | 20,2 | 17,6 |
  | âge moyen des liquidants de 2024 | 63,60 | 62,75 | 62,63 |

  L'écart de Kolmogorov des femmes passe de −15,6 à −14,7 points à 900 €,
  celui des hommes reste à +5,5 à 1 800 €. La durée validée des femmes de 1955
  et de 1960 passe de 42,0 à 41,4 et de 43,1 à 42,5 années (EIR 40,6 et 41,2) ;
  celle des hommes ne bouge pas. Les retraitées de 2020 nées avant 1950
  décotent 8,1 % sous les deux versions ; celles des générations simulées 1950
  et 1955, 9,1 et 15,0 % et non 5,1 et 8,4.
- *Ce que cela dit.*
  - La décote des femmes rejoint l'EIR aux deux générations qu'il suit :
    12,9 % des femmes de 1955 pour 12,5, 8,2 % de celles de 1950 pour 7,9.
    Les jumelles des carrières qui ne pouvaient pas décoter — celles de trente
    à quarante ans, qui ont leur durée à 62 ans avec leurs enfants — ne pèsent
    plus rien, et la décote de leur génération tombe sur des carrières qui
    décotent. L'ensemble de 1955 passe au-delà, 11,9 % pour 10,7, les hommes
    restant à 10,9.
  - Les départs bougent comme la note de la dix-neuvième partie l'annonçait :
    de l'âge d'annulation (23,4 % des départs des femmes de 1955, 17,9
    désormais ; EIR 10,8) vers l'âge légal (49,1, puis 53,9 ; 37,5), à peine
    entre les deux (7,5, puis 8,5 ; 26,7). Les carrières qui peuvent décoter
    partent décotées à l'âge légal ; celles qui ne le peuvent pas y partent au
    taux plein, ou plus tard avec une surcote, 9,8 % et non 8,6 (14,3), tout
    leur poids leur revenant.
  - Les hommes de 1950 et de 1955 ne bougent pas : leurs carrières
    incomplètes pouvaient toutes décoter, sans enfants ; et les agents ne
    décotent pas encore à ces générations — `avec_decote` trouve ceux des IEG
    au taux de 75 % jusqu'à la génération 1955, ceux de la conduite jusqu'à
    celle de 1960, la décote des régimes spéciaux ne mordant qu'aux départs
    de juillet 2010 et progressivement. L'écart des hommes de 1955, 10,9 %
    pour 8,7, n'est donc pas d'eux, quoi qu'en présumait la note de la
    dix-huitième partie : il tient d'abord à la génération, la part des nés en
    1955, 9,9 %, jugée sur celle des nés en 1953, 8,6. Les agents décotent
    dès la génération 1960 : les hommes qui liquident au régime général en
    2024 décotent 17,8 % et non 21,2 (Cnav 13,0).
  - Ce qui s'éloigne : le stock de 2020 et le flux de 2024. Les retraitées de
    2020 décotent 10,5 % (8,8), les liquidantes du régime général de 2024
    17,2 % (13,7). Les générations que 2020 et 2024 voient partir ont déjà
    leurs jumelles décotées, parties à l'âge légal, quand celles du taux plein
    attendent l'âge d'annulation : la génération simulée 1955 décote 15,0 %
    dans le stock de 2020, pour 12,8 % de toute la génération ; et la part
    d'avant 1950 ne garde la part de l'EIR qu'aux générations que 2020 voit
    toutes parties, jusqu'à celle de 1953, sans compter celles de 1954 à 1958
    qu'il voit partir. Le premier quintile des femmes décote
    26,7 % (17,5) : la décote ne tombe plus que sur les carrières qui
    peuvent décoter, les plus courtes, au bas ; les quatre autres quintiles
    s'approchent de l'EIR.
  - La distribution de 2020 en dit peu : treize euros de moins aux femmes,
    leur premier décile à 393 € et non 413 (283).
  - La version reste : elle donne à chaque génération de femmes la décote que
    l'EIR lui trouve, compte la population comme la grille du coût, et ôte aux
    jumelles ce que les agents décotent déjà ; ce qu'elle éloigne — le stock
    de 2020, le flux de 2024, le premier quintile, l'âge légal — tient à ce
    qu'elle ne fait pas : les départs entre l'âge légal et l'âge
    d'annulation, la part d'avant 1950 sur le stock que 2020 voit, la décote
    selon la tranche ou le rang.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles, qui n'ont
  pas de décote ; les carrières, toutes, leurs cas types et leurs poids de
  base ; le pilote et le modèle ; le registre, dont aucun point « 138.14 » ne
  nomme la décote. Aucune règle du scénario 1 ne change : pas d'entrée au
  journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : les départs entre l'âge légal et l'âge
   d'annulation, que les carrières courtes, étalées jusqu'à 60 ans, ne
   prennent jamais au taux plein — les femmes de 1955 y partent pour 8,5 %
   (EIR 26,7), à l'âge légal pour 53,9 (37,5) — ; la part d'avant 1950, qui
   ne garde au stock de 2020 la part de l'EIR qu'aux générations qu'il voit
   toutes parties, sans celles de 1954 à 1958, dont les jumelles décotées
   sont déjà parties quand celles du taux plein attendent — les retraitées de
   2020 décotent 10,5 % (8,8) — ; les parts des nés en 1950 et en 1953
   parmi les seuls résidents, si l'EIR les publie ; les déclinaisons du bas
   qui pourraient décoter quand leur carrière ne le peut pas ; les natures des
   carrières incomplètes, qui gardent leur chômage — huit à dix années ferment
   la carrière longue aux classes p10 à p50 des carrières allongées — quand
   l'AVPF des femmes qui ont cessé de travailler y est, avec son salaire au
   Smic dans le salaire annuel moyen, et le chômage d'après 60 ans de celles
   qui attendent le taux plein par l'âge ; le plafond de chaque génération,
   que ses classeurs publient pour 1950 et 1953, à certifier, s'il valait de
   couper le haut des rangs, et avec eux la pente des natures des hommes selon
   le rang ; la maternité, que l'échantillon range avec la maladie et que
   D. 351-1-2 répute sans limite depuis avril 2014, et que la population tient
   pour de la maladie, quatre trimestres, indépendante de l'AVPF, que rien ne
   croise avec elle ; le calage de la durée des femmes, qui compte les
   carrières pleines et allongées à l'entrée de leur génération, non à celle
   de leurs cinquièmes ; la durée des carrières pleines que la onzième version
   prend à l'EIR ; les invalides et les inaptes, au taux plein dès l'âge
   légal ; la surcote des statutaires ; la part passagère du revenu des
   indépendants et la carrière saisonnière des salariés agricoles, si une
   source les publie ; le juge propre des artisans, la part des liquidants du
   RSI au minimum contributif d'avant 2020 ; la part des générations 1946 à
   1953 au minimum ; la fragmentation selon la génération ; la décote selon la
   tranche ou le rang. Les niveaux des cas types statutaires et non salariés,
   et la dispersion des libéraux, attendent l'action 152, au propriétaire.
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

Hors de l'étape : *au modèle*, ce que les deux notes du site laissent — la
descente vers la carrière longue dans le départ des cas types, à vérifier
(`2026-10-25-etape-14-estimation-des-carrieres-inactives.md`), et l'âge où
s'ouvre la pension du militaire, au mois près, que son balayage devrait
atteindre (`2026-10-25-etape-14-descente-vers-la-carriere-longue.md`) ; au
propriétaire, les deux questions de la seconde : le balayage du militaire
doit-il partir de son âge de radiation tant que cet âge n'est pas trouvé au
mois, et l'écart d'un mois que la recherche manque vaut-il une sonde au mois.
Le VI de D. 634-1, la rédaction propre aux artisans et aux commerçants, à lire
rédaction par rédaction (note de la datation) ; ce que chaque worker garde des
calculs qu'il a faits, sans borne (`memoire._EN_MEMOIRE`) : la mesure s'en
passe, sous `CALCULS_SANS_MEMOIRE=1`.
