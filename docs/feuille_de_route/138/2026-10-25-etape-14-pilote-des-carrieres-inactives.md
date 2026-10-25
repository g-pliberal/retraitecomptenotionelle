# Étape 14, dix-neuvième partie : le pilote des carrières inactives

**Le 25 octobre 2026 : le pilote ne laisse plus une carrière sans activité
avant l'âge d'annulation de la décote, avec la décote que sa règle lui
refuse ; au modèle, sur `main` (63dbccd). Le droit date la durée comme si la
carrière validait encore quatre trimestres par an, et le pilote s'arrêtait au
bout de ses quatre passes : quand la montée s'arrête sans le taux plein, la
recherche reprend désormais de l'âge d'annulation. La population d'aujourd'hui
n'en bouge pas : aucun de ses 14 874 cas types ne part à un autre âge, à
aucune des dix-huit générations, de 1880 à 1965, dont la mesure lit les
départs — le calage de la vingt-huitième version avait éloigné de leur durée
les carrières où la dix-septième partie avait vu le défaut. En projection, il
en déplace vingt-trois, aux générations 1980 et 1985 : des femmes de trente à
quarante ans de carrière, à un trimestre de leur durée, qui partent à 67 ans
et non à 65 ; la page ne lit pas la population (action 157).
L'écart des femmes de 1955 n'est donc pas du pilote : étalées jusqu'à 60 ans,
leurs carrières courtes partent au taux plein à l'âge légal ou à l'âge
d'annulation, jamais entre les deux. Le site a le même défaut, dans
l'estimation : laissé au site.**

Demande : la seizième vague du 25 octobre 2026, une session par tâche, lancée
par le propriétaire : l'action 138, étape 14, le point suivant du bloc de
l'étape, et lui seul : le pilote des carrières inactives (« Ce qui reste »,
point 1, de la note de la dix-huitième partie,
`2026-10-25-etape-14-decote-selon-la-generation.md`), à reprendre au modèle
avec ce qu'il déplace ; le pic de mémoire de la mesure sous les 7,4 Go du
25 octobre, sans relâcher `CAS_TYPES_PAR_MORCEAU`.

- *Ce qui était.* Le pilote date le départ d'un cas type par un point fixe
  (`pilote.age_de_depart`, `point_fixe`) : parti de l'âge écrit, il demande
  au droit l'âge où la carrière liquidée là aurait le taux plein
  (`ouvrir.age_taux_plein_droit`), et recommence, quatre passes au plus
  (`PASSES_LIQUIDATION`). Le droit date la durée requise sans simuler : il
  manque à la carrière `requis − acquis` trimestres, « et une année pleine en
  rend quatre ». Une carrière sans activité n'en rend aucun : à deux
  trimestres de sa durée, elle montait d'un semestre à chaque passe, de
  64 ans, l'âge du gabarit, à 64 ans et demi, 65, 65 et demi et 66, où le
  pilote la laissait, au taux de 48,75 % qu'elle avait dès 62 ans ; à un
  trimestre, à 65 ans. La note de la dix-septième partie l'a vu chez la femme
  de la classe p50 des carrières de vingt à trente ans nées en 1955, à 164
  trimestres de 166 (`2026-10-25-etape-14-carrieres-allongees.md`). Le défaut
  ne mord que là où quatre passes ne mènent pas de l'âge écrit à l'âge
  d'annulation. La mesure rangeait ce départ au taux plein, sa règle étant
  celle du taux plein (`grille_large.condition_au_depart`) ; et sa jumelle
  partie à l'âge légal, au même taux, ne décotait pas à ses yeux :
  `avec_decote` compare le taux d'un départ à celui du départ que le pilote
  fixe au taux plein.
- *Le correctif* (`pilote.age_de_depart`, `pilote.age_annulation`,
  63dbccd). Sous la règle `taux_plein`, le pilote vérifie l'âge que le point
  fixe trouve : si le droit y oppose encore un âge plus tardif, la montée
  s'est arrêtée sans le taux plein, et la recherche reprend de l'âge
  d'annulation de la décote, où le droit le sert sans condition de durée
  (`ouvrir.age_annulation_droit`) ; elle en descend comme toute autre,
  jusqu'à l'âge où la carrière a sa durée, s'il en est un avant lui. Les
  réponses du droit sont gardées le temps d'un départ : la vérification ne
  coûte rien quand le point fixe a convergé. `point_fixe` ne change pas, ni
  son jumeau, `pointFixe` (`moteur/js/pilote.js`) : le départ des cas types
  n'a que son exemplaire Python. La documentation de `age_taux_plein_droit`
  renvoie au pilote.
- *Le test* (`test_liquidation.py`, au niveau rapide),
  `test_le_pilote_fait_attendre_l_age_d_annulation_a_une_carriere_qui_ne_valide_plus`,
  un cas posé à la main : né en 1955, entré à vingt ans, sans activité après
  quarante et une années, un salarié a 164 trimestres des 166 de sa
  génération dès l'âge légal ; il part avant 67 ans, l'âge d'annulation des
  nés depuis 1955 (L. 351-8, 1°), au taux de 50 − 2 × 0,625 = 48,75 %
  (R. 351-27) ; le pilote, qui ne liquide toujours rien, le fait partir à
  67 ans, au taux plein. Vu rouge, 66,0 pour 67,0 ; vert sous les
  présomptions décalées. La suite complète de GitHub est verte sur 63dbccd.
- *La classe.* Les carrières qui valident encore, mais moins de quatre
  trimestres par an — payées 2 à 8 % du salaire moyen après 56 à 60 ans,
  essayées une à une — convergent déjà : l'année de la liquidation se compte
  au prorata de ses mois, et la montée les rattrape. Les mères de
  `scripts/scenarios_meres.py`, qui ont leur propre boucle, travaillent
  jusqu'au départ. Sur la grille du coût, la carrière heurtée comprise, des
  générations 1920 à 2010, sous les conventions du dépôt et sous celles du
  COR, aucun âge ne bouge : ni la page, ni un témoin, ni un fichier fabriqué.
  Le site, lui, a le défaut : `agesDeLEstimation` (`moteur/js/pilote.js`),
  seul exemplaire depuis l'action 161, étape 6, date le départ « au taux
  plein » de « Mon estimation retraite » par le même point fixe borné. Une
  saisie née le 15 janvier 1966, entrée en juillet 1983, sans activité de
  2026 à 2045, a 170 trimestres des 172 de sa génération, et l'estimation la
  dit au taux plein à 65 ans et 3 mois ; entrée en octobre, à 169 trimestres,
  à 66 ans et 3 mois. L'une et l'autre n'ont le taux plein qu'à 67 ans. La
  reprise serait la même ; elle est au site.
- *La mesure*, couple par couple. Le correctif ne change aucune carrière,
  seulement l'âge où certaines partent ; un brouillon hors du dépôt a donc
  daté chaque couple de la population sous l'ancien point fixe et sous le
  pilote corrigé, au simulateur de la projection, comme `cout._pensionnes`,
  `_proratisations` et `_conditions` les datent : les 14 184 cas types qui
  partent au taux plein, et les 676 qui partent à l'ouverture — les jumelles
  qui décotent, les agents à statut —, dans la version au taux plein que
  `avec_decote` leur oppose ; les quatorze militaires partent à leurs
  services. Aux dix-huit générations simulées de
  1880 à 1965, celles des pensions de 2020, des départs des générations 1950
  et 1955 et des liquidants de 2024, aucun couple ne part à un autre âge.
  Aux onze générations de la projection, de 1970 à 2020, vingt-trois
  bougent, tous aux générations 1980 et 1985, tous des femmes de trente à
  quarante ans de carrière, à un trimestre de leur durée : seize cas types au
  taux plein partent à 67 ans et non à 65 ; sept jumelles partent toujours à
  l'âge légal, mais décotées désormais aux yeux de la mesure, la version au
  taux plein qu'elle leur oppose partant à 67 ans, au taux plein, et non à
  65, à leur taux. La simulation, déterministe, redonnerait donc au chiffre
  près la colonne « avec » de la note de la dix-huitième partie, prise sur
  964023c, le modèle n'ayant changé depuis qu'au registre et au pilote ;
  lancée sur l'arbre figé de 63dbccd (`CALCULS_SANS_MEMOIRE=1`, trois cœurs,
  des morceaux de cent cas types), elle a été arrêtée au bout de 110 minutes
  de simulation, à 5,0 Go au plus, l'arbre de ses processus compté entier.
- *Ce que cela dit.*
  - Le défaut était au modèle, et n'est plus à la population. Sous la
    vingt-huitième version, le calage de la durée des femmes a mis la
    carrière de la classe p50 à 156 trimestres, dix de moins que sa durée :
    elle montait de deux ans et demi à la première passe, et l'âge
    d'annulation bornait la deuxième. Jusqu'à la génération 1965, aucune
    carrière de la population ne s'arrête plus à un ou deux trimestres de sa
    durée là où les passes ne suffisent pas.
  - L'écart des femmes de 1955 — 23,4 % des départs à l'âge d'annulation
    pour 10,8, 7,5 % entre lui et l'âge légal pour 26,7 — n'est donc pas du
    pilote, qui datait déjà leurs départs à l'âge de leur taux plein. Les
    carrières courtes sont étalées jusqu'à 60 ans (`AGE_FIN_ETALEMENT`), et
    ne valident plus rien à l'âge légal : au taux plein, elles partent à
    l'âge légal si leur durée y est, à l'âge d'annulation sinon, jamais entre
    les deux ; leurs jumelles partent décotées à l'âge légal. Entre les deux
    âges ne partent que des carrières qui valident encore, ou qui attendent
    une surcote. Rapporter la décote aux carrières qui peuvent décoter en
    ferait partir plus à l'âge légal, non entre les deux.
  - En projection, le défaut mordait encore, sur vingt-trois couples des
    générations 1980 et 1985 que le pilote montait de 64 ans à 65, d'un
    trimestre par passe, et y laissait décotés : la page les verra quand elle
    lira la population (action 157), au taux plein de leur règle.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué : aucun cas type du dépôt ne
  part à un autre âge ; les carrières de la population, toutes, leurs poids
  et leurs âges de départ jusqu'à la génération 1965 ; le registre. Aucune
  règle du scénario 1 ne change — le pilote dit quand un cas type part, non
  ce que le droit lui sert — : pas d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : la part des départs avec décote rapportée aux
   carrières qui peuvent décoter à l'ouverture, comme la grille du coût
   (`facteurs_depense.part_avec_decote`), et non à toutes les carrières
   incomplètes, et, chez les hommes, sans ce que les agents des IEG et de la
   conduite décotent déjà à l'ouverture de leur statut ; les départs entre
   l'âge légal et l'âge d'annulation, que les carrières courtes, étalées
   jusqu'à 60 ans, ne prennent jamais au taux plein — les femmes de 1955 y
   partent pour 7,5 % (EIR 26,7) et attendent l'âge d'annulation pour 23,4
   (10,8) — ; les parts des nés en 1950 et en 1953 parmi les seuls résidents,
   si l'EIR les publie ; les natures des carrières incomplètes, qui gardent
   leur chômage — huit à dix années ferment la carrière longue aux classes
   p10 à p50 des carrières allongées — quand l'AVPF des femmes qui ont cessé
   de travailler y est, avec son salaire au Smic dans le salaire annuel
   moyen, et le chômage d'après 60 ans de celles qui attendent le taux plein
   par l'âge ; le plafond de chaque génération, que ses classeurs publient
   pour 1950 et 1953, à certifier, s'il valait de couper le haut des rangs, et
   avec eux la pente des natures des hommes selon le rang ; la maternité, que
   l'échantillon range avec la maladie et que D. 351-1-2 répute sans limite
   depuis avril 2014, et que la population tient pour de la maladie, quatre
   trimestres, indépendante de l'AVPF, que rien ne croise avec elle ; le
   calage de la durée des femmes, qui compte les carrières pleines et
   allongées à l'entrée de leur génération, non à celle de leurs cinquièmes ;
   la durée des carrières pleines que la onzième version prend à l'EIR ; les
   invalides et les inaptes, au taux plein dès l'âge légal ; la surcote des
   statutaires ; la part passagère du revenu des indépendants et la carrière
   saisonnière des salariés agricoles, si une source les publie ; le juge
   propre des artisans, la part des liquidants du RSI au minimum contributif
   d'avant 2020 ; la part des générations 1946 à 1953 au minimum ; la
   fragmentation selon la génération ; la décote selon la tranche ou le rang.
   Les niveaux des cas types statutaires et non salariés, et la dispersion
   des libéraux, attendent l'action 152, au propriétaire.
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

Hors de l'étape : *au site*, le même défaut dans l'estimation
(`agesDeLEstimation`, `moteur/js/pilote.js`), qui date le départ « au taux
plein » d'une saisie sans activité jusqu'au départ avant l'âge où elle l'a, à
reprendre de même dans le portage, par une session du site, la saisie née le
15 janvier 1966 pour test ; le VI de D. 634-1, la rédaction propre aux
artisans et aux commerçants, à lire rédaction par rédaction (note de la
datation) ; ce que chaque worker garde des calculs qu'il a faits, sans borne
(`memoire._EN_MEMOIRE`) : la mesure s'en passe, sous `CALCULS_SANS_MEMOIRE=1`.
