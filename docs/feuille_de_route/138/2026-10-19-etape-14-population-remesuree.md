# Étape 14, suite de la dixième partie : la population remesurée sous D. 351-1-2 daté

**Le 19 octobre 2026 : la population est remesurée sur `main`, avec et sans la
datation de D. 351-1-2, sur la même base. Les hommes de la génération 1950 ne
partent plus en carrière longue que pour 6,3 %, et non 13,1 (EIR 18,3) : leurs
départs de 2009 et 2010 relèvent de la rédaction de 2003, qui ne répute pas le
chômage cotisé, et la population met au chômage toutes leurs périodes
assimilées. Ceux des classes p75 à p99 partent à l'âge légal, où la population
rejoint l'EIR (35,1 % pour 35,3) ; ceux des classes p25 et p50, et les femmes
de la classe p75, six mois plus tard qu'avant, toujours en carrière longue. Ni
la part des femmes en carrière longue, ni la génération 1955, ni la
distribution de 2020 ne bougent. La datation est le droit, et reste ; ce
qu'elle découvre, c'est la nature des périodes assimilées des hommes, service
national et maladie, que la rédaction de 2003 répute seuls.**

Demande : la vague B du 19 octobre 2026, troisième salve, session 17, lancée
par la session de suivi « Tâches restantes » sur la demande du propriétaire,
« Vas-y, lance ce qui n'a pas besoin de ma décision » : le premier des restes
« une session par point » du bloc « Reprise » de l'étape, « remesurer » — la
population, que la note de la datation (`2026-10-19-etape-14-d-351-1-2-date.md`)
disait bouger sans être mesurée.

- *La mesure.* Deux arbres figés sur `ff822c1` (`git worktree add --detach`),
  leur `src/` sur le `PYTHONPATH` : le premier tel quel ; le second sans la
  datation, le modèle de `c2e5452` y étant retiré sans commit — le Python, la
  fiche datée, la table des motifs, le portage et la fabrique du paquet. La
  grille simule ses cas types par le portage, sur le paquet du jour : retirée
  du seul Python, la mesure s'arrêtait d'emblée, le paquet ne se bâtissant
  plus. La méthode `avant` de `CarriereLongue`, venue depuis avec les droits
  contrefactuels, reste. Dans cet arbre, les douze tests de la datation
  échouent pour la raison attendue — le portage y répute quatre trimestres de
  chômage en 2009, et non aucun —, et les trois cent un autres de
  `tests/test_simulateur.py` passent. Puis `python scripts/grille_large.py
  --grille population --distribution --processus 4 --json` dans chacun, l'un
  après l'autre, en arrière-plan : 28 minutes avec la datation, 15 sans, sur
  quatre cœurs, 2 518 cas types, chacune sous son empreinte dans la mémoire
  des calculs (38 calculs chacune). La mesure « sans » redonne au dixième la
  mesure « avec » de la dixième partie, sur `868a5f6` : rien de ce qui s'est
  commité depuis, hors la datation, ne déplace la population.
- *Ce qu'elle trouve*, les départs de la génération 1950, en part des départs
  déjà pris à 66 ans, l'âge où l'enquête voit la sienne ; ceux de la grille
  1955, jugée sur les nés en 1953, ne bougent pas d'un dixième de point (la
  carrière longue des deux sexes, 13,95 % avec et sans, pour 20,5) :

  | génération 1950 | EIR | sans | avec |
  |---|---|---|---|
  | hommes, avant l'âge légal | 27,6 | 23,0 | 16,1 |
  | hommes, à l'âge légal | 35,3 | 28,3 | 35,1 |
  | hommes, carrière longue | 18,3 | 13,1 | 6,3 |
  | hommes, taux plein, autrement | 53,8 | 56,6 | 63,5 |
  | hommes, à 60 ans | 41,3 | 28,4 | 35,2 |
  | femmes, carrière longue | 5,1 | 3,1 | 3,1 |
  | ensemble, avant l'âge légal | 20,1 | 16,0 | 12,7 |
  | ensemble, à l'âge légal | 40,0 | 37,5 | 40,8 |
  | ensemble, carrière longue | 11,6 | 8,0 | 4,7 |

  Cas type par cas type — relus, dans chaque arbre, de la mémoire des calculs
  de sa mesure, par les fonctions mêmes de `grille_large.py` —, dix-sept
  bougent, tous de la génération 1950, du salariat privé, de quarante années et
  plus, entrés à 16 ans. Les hommes des classes p75 à p99, 6,8 % des hommes de
  la génération, partaient en carrière longue à 59 ans et demi : ils partent à
  60 ans, l'âge légal, au taux plein. Ceux des classes p25 et p50, 6,3 %,
  partaient en carrière longue à 59 ans, et y partent à 59 ans et demi, comme
  les femmes de la classe p75, 1,6 % des femmes ; celles des classes p90 à p99
  y partent toujours à 59 ans. Les cinquièmes entrés à 17 et 19 ans partent à
  60 ans, et celui entré à 22 ans, après son service, à 61 ans et demi, avec
  ou sans. Dans la grille 1955, la carrière longue part à 60 ans et plus, en
  2015 et après, sous la rédaction de 2014, qui répute le chômage comme celle
  de 2026.

  La distribution de 2020 : la pension moyenne des hommes passe de 1 806 à
  1 807 € (EIR 1 957), leur médiane de 1 589 à 1 592 € (1 745), l'écart de
  Kolmogorov de +5,9 à +6,0 points à 1 800 € ; celle des femmes ne bouge pas
  d'un euro, 1 331 € (1 177), à −15,8 points à 900 €. La durée validée des
  hommes des générations 1945 et 1950 gagne 0,07 année, de 38,8 à 38,9 et de
  39,0 à 39,1 (EIR 40,8 et 40,6) : leurs départs reculent.
- *Ce que cela dit.*
  - La datation éloigne de l'EIR la carrière longue des hommes de la
    génération 1950, dont l'écart passe de −5,2 à −12,0 points, et celle des
    deux sexes, de −3,6 à −6,9 ; elle en rapproche leur départ à l'âge légal,
    de −7,0 à −0,2 point, et de −2,5 à +0,8 pour les deux sexes. Ce qui
    manque désormais aux hommes de 1950, ce sont les départs d'avant l'âge
    légal, 16,1 % pour 27,6.
  - Ce n'est pas le droit qui les en éloigne, mais la nature de leurs périodes
    assimilées, toutes au chômage indemnisé : la rédaction de 2003 n'en répute
    aucun trimestre cotisé, quand celle de 2026, lue à toute date, leur en
    réputait quatre. Leurs semblables de l'échantillon interrégimes, lu à la
    dixième partie, en avaient d'autres : 35,1 % des hommes nés en 1950 et
    affiliés avant 23 ans avaient validé un trimestre de service national,
    12,6 % un de maladie, que la rédaction de 2003 répute cotisés, quatre au
    plus de chacun — 1,9 trimestre par homme au plus, pour 3,2 sous celle de
    2026, le chômage compris. La population n'en répute plus aucun à ceux de
    1950 qui partent en carrière longue, entrés à 16 ans : son service
    national ne précède que l'entrée du cinquième entré à 22 ans.
  - La dixième partie avait lu cette nature et l'avait laissée telle : sous
    la rédaction de 2026, le chômage réputé dans sa limite donnait à peu près
    le nombre de trimestres de l'échantillon. Datées, les rédactions d'avant
    novembre 2012 n'en réputent plus rien, quand l'échantillon en garde 1,9
    par homme au plus : l'approximation ne tient plus. Elle ne disait pas
    tout non plus : les quatre trimestres que la rédaction de 2026 réputait à
    chacun ne menaient la carrière longue des hommes de 1950 qu'à 13,1 %
    (EIR 18,3) ; le reste de l'écart tient ailleurs, à l'entrée et à la durée
    des carrières pleines (point 1 de « Ce qui reste »).
  - La distribution de 2020 n'en dit rien : moins d'un euro en moyenne, trois
    à la médiane des hommes.
  - La datation reste : c'est le droit applicable, et elle rapproche de l'EIR
    la place des départs des hommes de 1950. Donner leur nature aux périodes
    assimilées passe en tête des restes de la population.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin, script ou test : rien ne se commite que cette note
  et le bloc « Reprise » de l'étape ; les deux arbres et leurs mesures restent
  hors du dépôt. Les autres grilles ; le contrôle des liquidants de 2024 sur
  l'EACR (`scripts/controle_eacr.py --population`), que la commande ne refait
  pas, et que la datation ne touche pas, ces départs relevant de la rédaction
  de 2023, que celle de 2026 reprend mot pour mot ; le registre. Aucune règle
  du scénario 1 ne change : pas d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : la nature des périodes assimilées des hommes — le
   service national et la maladie, chacun réputé cotisé dans sa limite par
   chaque rédaction, dans les parts que l'échantillon interrégimes publie
   génération par génération (« Les droits validés au cours de la carrière »,
   `eic2017_data_drees_er`, `Cum_trim` et `Part_aff`, lu à la dixième partie,
   non gardé) —, qui rendrait aux hommes de 1950 entrés à 16 ans une part de
   la carrière longue que la datation leur ôte ; les femmes en carrière
   longue, 5,5 % de la génération 1955 pour 13,0 % des nées en 1953 — les
   carrières de trente à quarante années, allongées à l'âge légal, entrent
   toutes à 21 ans ; la durée des carrières pleines que la onzième version
   prend à l'EIR, et que l'entrée au premier trimestre cotisé abaisse ; la
   part assimilée selon la génération ; les invalides et les inaptes, au taux
   plein dès l'âge légal ; la surcote des statutaires ; la décote selon la
   génération ; la part passagère du revenu des indépendants et la carrière
   saisonnière des salariés agricoles, si une source les publie ; le juge
   propre des artisans, la part des liquidants du RSI au minimum contributif
   d'avant 2020 ; la part des générations 1946 à 1953 au minimum ; la
   fragmentation selon la génération ; la décote selon la tranche ou le rang.
   Les niveaux des cas types statutaires et non salariés, et la dispersion
   des libéraux, attendent l'action 152, au propriétaire.
2. *La page qui lit ses agrégats* (action 157), au propriétaire.
3. *Les départs choisis*, encore : le départ qui suivrait l'incitation, au
   propriétaire (note de la huitième partie).
4. *Le recours à l'ASPA* par type de ménage (Ines), sur la population.
5. *La confrontation pension par pension*, au CASD, au propriétaire.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).

Hors de l'étape : le VI de D. 634-1, la rédaction propre aux artisans et aux
commerçants, à lire rédaction par rédaction (note de la datation).
