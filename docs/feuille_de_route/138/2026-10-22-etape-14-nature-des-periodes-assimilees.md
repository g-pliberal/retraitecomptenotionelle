# Étape 14, onzième partie : la nature des périodes assimilées des hommes, le service national et la maladie

**Le 22 octobre 2026 : la population donne leur nature aux périodes assimilées
des carrières pleines des hommes, aux parts que l'échantillon interrégimes de
cotisants publie génération par génération ; la vingt-troisième version, sur
`main` avec la série qu'elle lit. Nés en 1950, 36 % des hommes y ont une année
de service national, 20 % de la maladie (EIC : 35,1 et 12,6 %), que la
rédaction de D. 351-1-2 de 2003 répute cotisés quand elle ne répute pas le
chômage. Les hommes de la génération 1950 partent en carrière longue pour
9,0 % et non 6,3 (EIR 18,3), avant l'âge légal pour 18,8 % et non 16,1
(27,6) ; ceux de 1955 en carrière longue pour 25,8 % et non 23,1 (28,6 chez
les nés en 1953). Ni les femmes, ni la distribution de 2020 ne bougent. La
version reste ; la page ne bouge pas.**

Demande : la vague du 22 octobre 2026, lancée par la session de suivi
« Qu'est-ce qu'il reste à faire ? » sur la demande du propriétaire, « Lance
une session par action qui n'a pas besoin de moi » : l'action 138, étape 14,
le point 1 de « Ce qui reste » de la note de la remesure
(`2026-10-19-etape-14-population-remesuree.md`) — la nature des périodes
assimilées des hommes, le service national et la maladie, chacun réputé
cotisé dans sa limite par chaque rédaction.

- *Les données* (`scripts/fetch/drees_natures_assimilees.py`,
  `natures_assimilees.csv`, `tests/test_natures_assimilees.py`). Le fichier
  de `premier_trimestre.csv`, « eic2017_data_drees_er », d'autres colonnes :
  parmi les affiliés d'avant 23 ans, la part de ceux qui ont validé un
  trimestre de service national (« SN »), ou de maladie (« Maladie »,
  maternité, invalidité et accidents du travail compris), et le cumul de ces
  trimestres par affilié, deux sexes, vingt-quatre générations, à 60 ans ou
  au dernier âge que l'échantillon voit, 2017 moins la génération : le
  fichier y met le cumul des trimestres cotisés à zéro, et y reporte la part
  de l'âge d'avant. Des trimestres « utiles », ceux qui portent l'année vers
  ses quatre trimestres. 192 valeurs, certifiées par
  `scripts/verifier_donnees.py` (la seule série neuve, le journal complété
  d'elle seule), la source `drees_eic_natures_assimilees` au registre. Le
  portail de la DREES ne répondait pas d'ici : la poignée de main tombait,
  et le fichier n'est venu qu'au neuvième essai, une demi-heure plus tard.
  Ce qu'il dit des hommes : nés en 1950, 35,1 % ont servi, 1,4 trimestre par
  homme, quatre chacun ; 12,6 % ont été malades, 2,2 trimestres par homme,
  dix-sept et demi chacun ; nés en 1942, 49,7 % et 10,5 % ; 1954, 45,9 et
  14,4 % ; 1974, 63,0 % de service ; 1978, 22,0 ; 1980, 0,2. La maladie croît
  avec l'âge : 6,4 % des nés en 1976, vus jusqu'à 41 ans.
- *La vingt-troisième version* (`NATURES_SELON_LA_GENERATION`,
  `classes_de_nature`, `natures_assimilees`, `part_et_annees`, le champ
  `natures` de `CasTypeLarge`). Chaque cinquième d'une carrière pleine d'homme
  se décline en cinq classes de poids égal, au milieu de leur rang, comme les
  cinquièmes de l'entrée. Une classe sert quand son rang passe sous la part de
  sa génération qui a servi, moins celle des cinquièmes qui servent avant
  d'entrer (la vingt et unième version), rapportée aux autres : (35,1 − 20) /
  80 = 18,9 % en 1950, la première classe ; 35,3 % en 1955, les deux premières
  ; jusqu'à 63 % pour les générations 1973 et 1974, les trois premières de
  1964 à 1975 ; aucune après 1979. Elle fait de sa première année assimilée
  son service, une année, le cumul de ceux qui ont servi sur leur part. Une
  classe est malade quand son rang passe au-dessus de la part des autres : la
  dernière, dans toutes les générations, la maladie passant un dixième des
  hommes ; autant de ses années assimilées que chacun de ceux qui le sont en
  compte, quatre ou cinq. La part et le cumul s'interpolent entre deux
  générations de l'échantillon ; la maladie se lit à 60 ans, celle des
  générations nées après 1956 à celle de 1956, 14,6 %. Les classes de mêmes
  natures n'en font qu'une, et celle qui n'en a aucune garde le code de son
  cinquième : chaque carrière pleine d'homme en a cinq, 3 062 cas types au
  lieu de 2 518. Les années gardent leur place au milieu de la carrière, où la
  population met ses périodes assimilées ; la carrière longue n'en compte que
  le nombre. Trois tests : les parts lues ; celles des classes, posées à la
  main sur le fichier ; l'homme né en 1950 de la classe p50, entré à 16 ans,
  172 trimestres à 59 ans dont 160 cotisés, qui part en carrière longue à 59
  ans s'il a servi ou été malade — quatre trimestres réputés, 164 pour 162 —,
  et à 59 ans et demi sinon. Deux tests d'avant comptaient les codes des
  cinquièmes : ils regroupent leurs classes de nature.
- *La mesure.* Deux arbres figés sur `a15e18a`, le second la constante mise à
  `False`, leur `src/` sur le `PYTHONPATH` : `python scripts/grille_large.py
  --grille population --distribution --processus 4 --json`, l'un après
  l'autre, 28 et 23 minutes. La mesure « sans » redonne au dixième celle du
  19 octobre : rien de ce qui s'est commité depuis, la condition d'entrée
  lue sur la durée validée comprise, ne déplace la population. Les échecs
  passent de 3 050 à 3 594, un de plus par cas type ajouté : ceux des
  carrières pleines d'hommes, déclinées.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 :

  | | 1950, EIR | sans | avec | 1955, EIR 1953 | sans | avec |
  |---|---|---|---|---|---|---|
  | hommes, avant l'âge légal | 27,6 | 16,1 | 18,8 | 40,8 | 34,4 | 37,1 |
  | hommes, à l'âge légal | 35,3 | 35,1 | 32,4 | 24,4 | 22,8 | 20,0 |
  | hommes, carrière longue | 18,3 | 6,3 | 9,0 | 28,6 | 23,1 | 25,8 |
  | hommes, taux plein, autrement | 53,8 | 63,5 | 60,7 | 40,6 | 46,5 | 43,8 |
  | ensemble, avant l'âge légal | 20,1 | 12,7 | 14,0 | 30,9 | 22,5 | 23,8 |
  | ensemble, carrière longue | 11,6 | 4,7 | 6,0 | 20,5 | 13,9 | 15,2 |

  Les femmes ne bougent pas d'un dixième. Cas type par cas type, relus par
  `condition_au_depart` : en 1950, sous la rédaction de 2003, les classes qui
  servent ou sont malades des hommes entrés à 16 ans gagnent un semestre —
  celles des classes p25 et p50 partent en carrière longue à 59 ans et non à
  59 ans et demi, celles des classes p75 à p99 à 59 ans et demi en carrière
  longue, et non à 60 ans au taux plein, 40 % de leurs 6,8 % d'hommes, les
  2,7 points mesurés. Les entrés à 17 ans partent à 60 ans, avec ou sans,
  comme la classe p10 et ses cinq années assimilées. En 1955, sous la
  rédaction de 2014, qui répute aussi quatre trimestres de chômage, les deux
  classes qui servent gagnent un semestre — 60 ans pour 60 ans et demi, aux
  classes p25 et p50 — ou une année — 60 ans et demi pour 61 ans et demi, de
  p75 à p99 — ; la classe p10 part en carrière longue à 61 ans et demi, et
  non à 62 ans au taux plein. La classe malade n'y gagne rien, sauf en p10 :
  ses années de maladie prennent la place d'un chômage que la rédaction
  répute déjà.

  La distribution de 2020 : la pension moyenne des hommes passe de 1 806 à
  1 807 € (EIR 1 957), leur médiane de 1 592 à 1 591 € (1 745), l'écart de
  Kolmogorov de +6,0 à +5,9 points à 1 800 € ; celle des femmes, de 1 331 à
  1 332 € (1 177), à −15,8 points à 900 €. La durée validée des hommes de la
  génération 1950 perd 0,1 année, 39,0 (EIR 40,6) : leurs départs avancent ;
  celle des hommes nés en 1960 gagne 0,4 année, 38,2 (40,5), qui partent plus
  tôt en carrière longue et sont plus nombreux parmi les retraités de 2020.
- *Ce que cela dit.*
  - Le service et la maladie rendent aux hommes de 1950 2,7 des 6,8 points
    de carrière longue que la datation de D. 351-1-2 leur avait ôtés : la
    rédaction de 2003 répute cotisés quatre trimestres de l'un et de l'autre,
    à 56 % des hommes de la population, à 48 % de ceux de l'échantillon
    (35,1 et 12,6 %, l'un sans l'autre ici). L'écart à l'EIR passe de −12,0
    à −9,3 points ; celui des départs d'avant l'âge légal, de −11,5 à −8,8.
  - Ce qui manque encore aux hommes de 1950 tient à l'entrée et à la durée
    des carrières pleines : les entrés à 17 ans, un cinquième, n'atteignent
    pas les 162 trimestres cotisés à 59 ans, service compris, et les classes
    qui ne servent ni ne sont malades, trois sur cinq, restent à 60 ans ou à
    59 ans et demi.
  - Ceux de 1955 se rapprochent de l'EIR de 2,7 points, à −2,8 ; la
    rédaction de 2014 leur répute déjà le chômage, que la population leur
    donne à tous quand l'échantillon n'en trouve qu'à un homme sur trois :
    le service s'y ajoute, et leur carrière longue est un peu forte de ce
    côté-là, un peu faible de l'autre.
  - Leur départ à l'âge légal s'éloigne de l'EIR, de 0,2 à 2,9 points en
    1950 : les départs qui avancent sont ceux qui partaient à 60 ans.
  - La distribution de 2020 n'en dit rien : un euro.
  - La version reste : elle donne aux hommes les natures que l'échantillon
    publie, et rapproche de l'EIR leurs départs d'avant l'âge légal.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles ; les
  autres carrières des hommes, et toutes celles des femmes, qui gardent leur
  chômage ; le contrôle des liquidants de 2024 sur l'EACR, que la commande
  ne refait pas ; le registre. Aucune règle du scénario 1 ne change : pas
  d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : la part du chômage selon la génération — la
   population en met à tous les hommes qui ne sont pas malades, quand
   l'échantillon n'en trouve qu'à 32,5 % des hommes nés en 1950, treize
   trimestres chacun : sous les rédactions d'après avril 2014, quatre
   trimestres réputés à chacun, au lieu de 1,3 en moyenne ; la nature des
   périodes assimilées des femmes — l'AVPF, 39,8 % des nées en 1950, dix
   trimestres et demi par femme, réputée cotisée depuis septembre 2023
   seulement, et la maladie, 19,4 % — ; les femmes en carrière longue, 5,5 %
   de la génération 1955 pour 13,0 % des nées en 1953 — les carrières de
   trente à quarante années, allongées à l'âge légal, entrent toutes à
   21 ans ; la durée des carrières pleines que la onzième version prend à
   l'EIR, et que l'entrée au premier trimestre cotisé abaisse — la carrière
   longue des hommes de 1950 reste à 9,0 % pour 18,3 ; la part assimilée
   selon la génération ; les invalides et les inaptes, au taux plein dès
   l'âge légal ; la surcote des statutaires ; la décote selon la génération ;
   la part passagère du revenu des indépendants et la carrière saisonnière
   des salariés agricoles, si une source les publie ; le juge propre des
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

Hors de l'étape : le VI de D. 634-1, la rédaction propre aux artisans et aux
commerçants, à lire rédaction par rédaction (note de la datation).
