# Étape 14, dixième partie : le service national avant le premier trimestre cotisé, et les périodes assimilées selon le rang

**Le 19 octobre 2026 : deux versions de plus de la population, mesurées avec
et sans sur la même base. La vingt et unième fait précéder du service national
le cinquième d'homme qui valide un trimestre avant d'en cotiser un : 10,6 % des
hommes nés en 1950 partent à 62 ans, et non plus 17,8 (EIR 4,8). La
vingt-deuxième donne à chaque classe de centiles la part de périodes
assimilées des quintiles de la pension que ses rangs couvrent : les femmes
partent en carrière longue, 3,1 % des nées en 1950 (EIR 5,1) et 5,5 % de la
génération 1955 (13,0 chez les nées en 1953), quand aucune n'y partait. Les
hommes de la génération 1950 y partent un peu moins, 13,1 % au lieu de 14,8
(EIR 18,3), ceux de 1955 un peu plus, 23,1 au lieu de 22,2 (28,6). La
distribution de 2020 ne bouge pas. Les deux versions restent ; la page ne
bouge pas.**

Demande : la vague du 19 octobre 2026, cinquième salve, session 22, lancée par
la session de suivi « Tâches restantes » sur la demande du propriétaire,
« Lance les sessions qui n'ont pas besoin de moi » : le premier des restes
« une session par point » du bloc « Reprise » de l'étape, « la durée des
carrières pleines et les périodes assimilées, les femmes en carrière longue »
— le point 1 de « Ce qui reste » de la note de la mesure
(`2026-10-19-etape-14-mesure-des-carrieres-longues.md`).

- *La vingt et unième version : le service national avant le premier
  trimestre cotisé* (`SERVICE_AVANT_LE_PREMIER_TRIMESTRE`, le champ `services`
  et `service_de` de `CasTypeLarge`, `classes_d_entree`,
  `premiers_trimestres(racine, "valide")`). La série des trimestres validés de
  `premier_trimestre.csv`, certifiée avec celle des trimestres cotisés le
  18 octobre, n'était pas lue. Elle passe l'autre de ce qu'un affilié valide
  sans cotiser — chez les hommes, le service national : nés en 1950 et
  affiliés avant 23 ans, 93,2 % avaient validé un trimestre à la fin de
  l'année de leurs 21 ans, sur 99,2 à 23 ans, et 84,8 % en avaient cotisé un,
  sur 96,1. Chaque cinquième d'une carrière pleine d'homme lit les deux séries
  au milieu de son rang, l'entrée de la onzième version restant un plancher :
  celui dont le premier trimestre validé vient avant le premier cotisé fait
  son service (`service_militaire`) les années qui les séparent, avant
  d'entrer. C'est le dernier des hommes nés jusqu'aux années 1970, les
  générations d'avant 1942 lisant celle-ci : à 21 ans quand il cotise à 22
  dans la génération 1950, à 20 et 21 ans dans celle de 1946 ; le quatrième
  aussi dans la génération 1942 ; aucun dans la génération 1980. Le service allonge la durée
  d'assurance et compte, dans sa limite de quatre trimestres, dans la durée
  cotisée de la carrière longue (D. 351-1-2, 1°) ; la condition d'entrée, qui
  ne lit que les trimestres cotisés, ne change pas. Les femmes gardent leur
  entrée : un cinquième des générations 1942, 1946 et 1970 valide un an avant
  de cotiser, d'une nature que l'échantillon ne dit pas — ni service, ni
  chômage, ni maladie, ni AVPF à ces âges. Deux tests : les âges du premier
  trimestre validé et du premier cotisé, lus dans le fichier ; le dernier
  cinquième de la génération 1950, son service à 21 ans, son emploi dès 22 et
  son départ à 61 ans et demi, au taux plein par la durée, et non à 62 ans et
  demi. Le test de la neuvième partie sur l'homme de 1955 entré à 21 ans dit
  désormais qu'il part à 62 ans, l'âge légal : son service, à 20 ans, lui
  donne ses 166 trimestres à 61 ans et demi.
- *La vingt-deuxième version : les périodes assimilées selon le rang*
  (`ASSIMILEES_SELON_LE_RANG`, `parts_assimilees_des_classes`,
  `assimilees_selon_le_rang`). Chaque carrière du salariat et des
  non-salariés comptait la part de périodes assimilées que l'EIR mesure à
  tous les résidents de son sexe, 12,5 % de la durée validée hors majorations
  des femmes (32 années, dont 28 cotisées), 10 % de celle des hommes (40, dont
  36), toute au chômage indemnisé : cinq années de la carrière pleine d'une
  femme, dont quatre trimestres seulement réputés cotisés. Aucune femme ne
  pouvait partir en carrière longue : la femme née en 1953 entrée à 17 ans
  avait 156 trimestres cotisés ou réputés tels à 60 ans, pour 165. Or la part
  suit la pension, chez les femmes surtout : l'EIR mesure aux résidentes des
  cinq quintiles de la pension en équivalent carrière complète 23 années
  validées pour 17 cotisées, puis 34 pour 27, 38 pour 35, 38 pour 36 et 39
  pour 38 ; aux résidents, 32 pour 28, 40 pour 35, 41 pour 39, 40 pour 37, 41
  pour 37 (`quintiles_eqcc_residents.csv`). Chaque classe de centiles prend,
  dans chaque tranche de durée, la part des bandes de quintiles que ses rangs
  couvrent, chacune pesée par la masse de la tranche qui y tombe, les
  retraités au minimum portant celle de leur quintile dans la bande du
  premier, comme sous `RANG_SELON_LA_DUREE`. Dans la tranche de quarante ans
  et plus, les femmes vont de 19,5 % (p10 et p25) à 17,9 (p50), 6,8 (p75),
  4,2 (p90) et 2,6 % (p95 et p99) ; les hommes, de 11,3 % (p10) à 7,4 (p25),
  6,5 (p50), 8,8 (p75) et 9,8 % (au-delà). Pesées en 2020, les périodes
  assimilées passent de 11,9 à 13,9 % de la durée validée des femmes et de 9,8
  à 8,6 % de celle des hommes — l'échantillon interrégimes en compte 15,2 et
  6,6 % aux affiliés d'avant 23 ans nés en 1950, à 60 ans — ; celles des
  carrières pleines, de 5,1 à 4,7 années chez les femmes, de 4,0 à 3,7 chez
  les hommes. Deux conventions : la part d'un quintile vaut pour toutes ses
  tranches de durée — résoudre les cinq quintiles pour cinq parts de tranche
  en donne de négatives, l'EIR arrondissant ses durées à l'année — ; et cet
  arrondi met la part d'un quintile à une année près. Le calcul des bandes,
  que le tableau croisé de `RANG_SELON_LA_DUREE` faisait seul, passe à
  `BandesDesQuintiles`, au chiffre près. Deux tests : les parts des classes,
  posées à la main sur le fichier (1/39 et 4/41 aux classes du haut, 19,5 % à
  la classe p10 des femmes) ; la femme née en 1953 de la classe p95, entrée à
  17 ans, une année assimilée, 172 trimestres à 60 ans pour 165, qui part à
  60 ans en carrière longue, et à 61 ans et deux mois sans la version. Deux
  tests d'avant visaient la première carrière venue, désormais de la classe
  p10 et de ses cinq années assimilées : ils visent la classe médiane, qu'ils
  décrivaient ; un troisième lit les années assimilées d'une carrière courte
  à la part de sa classe.
- *La nature des périodes assimilées, lue et laissée telle.* L'échantillon
  interrégimes publie le cumul des trimestres de chaque nature, dans le même
  jeu de la DREES (« Les droits validés au cours de la carrière », fichier
  `eic2017_data_drees_er`, indicateurs `Cum_trim` et `Part_aff`, lu d'ici,
  non gardé). Les hommes nés en 1950 et affiliés avant 23 ans en ont validé
  9,7 sans les cotiser à 60 ans — 4,3 de chômage, 2,2 de maladie, 1,4 de
  service national, 0,2 d'AVPF — ; 35,1 % ont un trimestre de service, 32,5 %
  un de chômage, 12,6 % un de maladie : chacun au plus quatre réputés cotisés,
  soit 3,2 trimestres par homme au plus ; 3,8 pour ceux nés en 1954. La
  population en répute quatre, son chômage dans sa limite : le nombre des
  trimestres réputés est déjà celui de l'échantillon, et c'est la masse des
  autres, douze trimestres pour une carrière pleine d'homme, qui retenait la
  carrière longue. Donner une nature à chaque année assimilée en répute
  douze à l'homme qui aurait une année de service, une de maladie, une de
  chômage : la version ne le fait pas. Chez les femmes, l'AVPF fait 10,5 des
  19,8 trimestres des nées en 1950, et elle n'est réputée cotisée que depuis
  le 1er septembre 2023 (plus bas).
- *La mesure.* Deux arbres figés sur `868a5f6` (`git worktree add
  --detach`), leur `src/` sur le `PYTHONPATH` : `python scripts/grille_large.py
  --grille population --distribution --processus 4 --json`, avec les deux
  versions, puis sans elles, leurs deux constantes mises à `False`. 14 minutes
  chacune sur quatre cœurs, 2 518 cas types ; la mesure « sans » redonne au
  dixième celle du matin.
- *Ce qu'elle trouve*, les départs de deux générations de la population, en
  part des départs déjà pris à l'âge où l'enquête voit la sienne, la grille
  1955 jugée sur les nés en 1953 :

  | | 1950, EIR | sans | avec | 1955, EIR 1953 | sans | avec |
  |---|---|---|---|---|---|---|
  | femmes, avant l'âge légal | 13,0 | 6,2 | 9,4 | 21,7 | 6,1 | 11,6 |
  | femmes, à l'âge légal | 44,4 | 49,2 | 46,0 | 37,5 | 59,2 | 53,6 |
  | femmes, carrière longue | 5,1 | 0,0 | 3,1 | 13,0 | 0,0 | 5,5 |
  | femmes, taux plein, autrement | 56,8 | 61,3 | 58,0 | 47,9 | 73,0 | 67,4 |
  | hommes, avant l'âge légal | 27,6 | 24,6 | 23,0 | 40,8 | 33,4 | 34,4 |
  | hommes, à l'âge légal | 35,3 | 26,7 | 28,3 | 24,4 | 16,3 | 22,8 |
  | hommes, entre lui et l'âge d'annulation | 25,4 | 29,4 | 29,3 | 26,4 | 30,7 | 23,4 |
  | hommes, carrière longue | 18,3 | 14,8 | 13,1 | 28,6 | 22,2 | 23,1 |
  | ensemble, carrière longue | 11,6 | 7,1 | 8,0 | 20,5 | 10,7 | 13,9 |
  | ensemble, avant l'âge légal | 20,1 | 15,1 | 16,0 | 30,9 | 19,3 | 22,5 |

  Âge par âge, les hommes de la génération 1950 partent à 61 ans pour 9,9 %
  (2,6 sans ; EIR 7,1), à 62 ans pour 10,6 (17,8 ; 4,8), à 60 ans pour 28,4
  (26,7 ; 41,3) ; à 65 ans pour 19,4, avec ou sans (8,3). La durée validée
  moyenne de chaque génération ne bouge pas de plus d'un dixième d'année,
  sauf celle des hommes nés en 1960, de 37,3 à 37,8 (40,5), et des femmes nées
  en 1960, de 42,2 à 42,5 (41,2). La distribution de
  2020 : la pension moyenne des femmes passe de 1 330 à 1 331 € (EIR 1 177),
  leur médiane de 1 284 à 1 274 € (1 013), l'écart de Kolmogorov reste de
  −15,9 à −15,8 points à 900 € ; celle des hommes reste à 1 806 € (1 957),
  +5,9 points à 1 800 €. La part des femmes du premier quintile au minimum
  passe de 66,5 à 63,5 % (EIR 65,9), celle de toutes de 31,0 à 30,7 (37,7).
- *Ce que cela dit.*
  - Les femmes partent en carrière longue : la classe du haut entrée à 17 ou
    18 ans, une à trois années assimilées, réunit la durée à 60 ans. L'écart
    des femmes à l'EIR se resserre de 5,1 à 2,0 points dans la génération
    1950, de 13,0 à 7,5 dans la génération 1955, et celui des deux sexes
    ensemble de 4,5 à 3,6 et de 9,8 à 6,6 points.
  - Ce qui manque encore aux femmes est ailleurs : les carrières de trente à
    quarante années, que la douzième version allonge jusqu'à l'âge légal pour
    les générations nées après 1950, entrent toutes à 21 ans, l'entrée du
    gabarit. La femme née en 1953 de la classe p95 dans cette tranche valide
    40 années, n'en compte qu'une d'assimilée, et part à 61 ans et deux mois
    au taux plein : la condition d'entrée de la carrière longue lui est
    fermée. Ces carrières sont 37 % des femmes du régime général de la
    population.
  - Les hommes de la génération 1950 partent un peu moins en carrière longue,
    ceux de la classe p10 ayant désormais cinq années assimilées et non
    quatre ; ceux de 1955 un peu plus, ceux des classes du milieu en ayant
    trois. L'écart de la génération 1950 passe de −3,5 à −5,2 points ; celui
    de la génération 1955, de −6,4 à −5,5.
  - Le service national déplace le départ du dernier cinquième des hommes,
    non sa condition : celui de la génération 1950 part à 61 ans et demi, et
    celui de 1955 à l'âge légal, 62 ans. Les départs à 62 ans des hommes de
    la génération 1950 passent de 17,8 à 10,6 %, ceux de 1955 à l'âge légal
    de 16,3 à 22,8 % (EIR 24,4).
  - La durée validée des hommes n'en reçoit presque rien : une année du
    dernier cinquième des carrières pleines, et plus de départs avant l'âge
    légal. L'écart de 1,6 à 2,0 années à l'EIR des générations 1940 à 1950
    reste à accorder avec la durée des carrières pleines que la onzième
    version prend à l'EIR.
  - Les deux versions restent : elles rapprochent de l'EIR la condition des
    départs des femmes et des deux sexes ensemble, et la place des départs
    des hommes, sans déplacer la distribution de 2020 ; la carrière longue des
    hommes de la génération 1950 s'en éloigne de 1,7 point.
- *Trouvé en chemin : D. 351-1-2, lu dans sa seule version de 2026.* Le
  modèle répute cotisées les périodes de la version en vigueur depuis le
  1er janvier 2026 (LEGIARTI000053356011), pour toutes les dates d'effet.
  L'index LEGI en garde cinq autres : celle du 31 octobre 2003
  (LEGIARTI000006736522) ne répute que le service national et l'incapacité
  temporaire, quatre trimestres chacun, et aucun chômage ; celle du
  1er novembre 2012 (LEGIARTI000026139944), deux trimestres de chômage
  indemnisé et six d'incapacité, dont quatre de maladie et d'accident du
  travail ; celle du 1er avril 2014 (LEGIARTI000028751938), quatre de
  chômage, la maternité sans limite, deux d'invalidité ; puis celles du
  16 mai 2021 (LEGIARTI000043506391) et du 1er septembre 2023
  (LEGIARTI000047634564), qui ajoute l'AVPF (L. 381-1 et L. 381-2). Un
  départ en carrière longue d'avant novembre 2012 comptait donc à tort le
  chômage indemnisé : les hommes de la génération 1950 de la population, qui
  partent à 59 ans et demi en 2009 et 2010, en comptent quatre trimestres. La
  règle est celle du scénario 1, hors de cette étape : la session du modèle
  la date, en suivant `docs/veille_droit.md`.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles, dont
  « interruptions » et « ensemble », qui gardent la part de leur sexe ; le
  contrôle des liquidants de 2024 sur l'EACR (`scripts/controle_eacr.py
  --population`), que la commande ne refait pas ; le registre. Aucune règle
  du scénario 1 ne change : pas d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : les femmes en carrière longue, 5,5 % de la
   génération 1955 pour 13,0 % des nées en 1953 — les carrières de trente à
   quarante années, allongées à l'âge légal, entrent toutes à 21 ans ; la
   durée des carrières pleines que la onzième version prend à l'EIR, et que
   l'entrée au premier trimestre cotisé abaisse ; la part assimilée selon la
   génération, que l'échantillon interrégimes donne au dixième (15,2 % des
   femmes nées en 1950, 6,6 % des hommes), quand l'EIR la donne à l'année
   près ; les invalides et les inaptes, au taux plein dès l'âge légal ; la
   surcote des statutaires ; la décote selon la génération ; la part
   passagère du revenu des indépendants et la carrière saisonnière des
   salariés agricoles, si une source les publie ; le juge propre des
   artisans, la part des liquidants du RSI au minimum contributif d'avant
   2020 ; la part des générations 1946 à 1953 au minimum ; la fragmentation
   selon la génération ; la décote selon la tranche ou le rang. Les niveaux
   des cas types statutaires et non salariés, et la dispersion des libéraux,
   attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, encore : le départ qui suivrait l'incitation, au
   propriétaire (note de la huitième partie).
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).

Hors de l'étape, à la session du modèle : D. 351-1-2 daté (plus haut).
