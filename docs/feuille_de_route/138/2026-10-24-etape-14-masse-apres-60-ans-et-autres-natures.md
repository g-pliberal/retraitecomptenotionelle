# Étape 14, treizième partie : ce que compte la masse assimilée des carrières pleines, après 60 ans et hors des quatre natures

**Le 24 octobre 2026 : la masse assimilée de l'EIR, qui plafonne depuis la
vingt-quatrième version les natures des carrières pleines, ne compte presque
rien d'après 60 ans, ni d'autre nature que la population puisse placer.
Après 60 ans, l'échantillon interrégimes de cotisants ne valide sans
cotisation que 0,4 à 0,9 trimestre par affilié, au chômage et malades qui
l'étaient déjà ; hors des quatre natures, il garde un reste de 1,0 à
2,4 trimestres à 60 ans, qu'aucune ne dit. L'excès est d'abord celui du
stock : prise aux quintiles que l'EIR publie pour les nés en 1950 et en 1953,
la masse des carrières pleines de la génération fait 2,6 et 3,2 années d'une
carrière d'homme de 42 ans, quand le stock des retraités de 2020 en donne
3,6, et l'échantillon trouve 2,6 années validées sans cotisation aux hommes
nés en 1950, à 67 ans ; chez les femmes, la génération vaut le stock. La
population ne change pas.**

Demande : la vague du 24 octobre 2026, une session par tâche, lancée par le
propriétaire : l'action 138, étape 14, le premier point de « Ce qui reste »
de la note de la douzième partie
(`2026-10-23-etape-14-chomage-et-natures-des-femmes.md`), et lui seul : la
masse assimilée des carrières pleines, « faite des retraités de 2020 et de
toute leur carrière, n'est plus qu'un plafond : ce qu'elle compte d'après
60 ans et des autres natures, génération par génération ».

- *Les données* (`scripts/fetch/drees_natures_assimilees.py`,
  `natures_assimilees.csv`, `tests/test_natures_assimilees.py`). Le même
  fichier de la DREES, « eic2017_data_drees_er » : les quatre natures au
  dernier âge vu quand il passe 60 ans — 71 ans, le dernier que le fichier
  publie, pour 1942 et 1946, 67 pour 1950, 63 pour 1954, 61 pour 1956 —, et,
  à chaque âge lu, le cumul de deux autres types, les trimestres validés
  (« Validé ») et ceux que l'activité cotise (« Cotisé »), dont l'écart, les
  quatre natures ôtées, est ce qu'aucune ne dit. 580 valeurs, les 384 d'avant
  identiques, certifiées par `scripts/verifier_donnees.py`, le journal
  complété de la seule série ; le lecteur vérifie qu'aucun cumul ne baisse
  après 60 ans, et que les validés ne passent ni sous les cotisés, ni au-delà
  de quatre par an depuis 14 ans, l'âge où finissait l'école avant 1959.
  `--fichier` lit le fichier déjà téléchargé : le portail a coupé quatre
  connexions sur cinq. La population ne lit que les quatre natures, à 60 ans
  au plus (`NATURES_DE_L_ECHANTILLON`, un test) : rien ne bouge.
- *Ce que l'échantillon voit après 60 ans*, par affilié d'avant 23 ans : les
  hommes nés en 1950 valident 9,7 trimestres sans les cotiser à 60 ans,
  10,3 à 67 ; ceux de 1942, 1946, 1954 et 1956, 0,6, 0,5, 0,7 et
  0,5 trimestre de plus jusqu'au dernier âge vu ; les femmes, 0,4 à 0,9. Du
  chômage surtout, 0,3 à 0,8 trimestre, puis de la maladie, 0,3 au plus. La
  part des chômeurs ne bouge presque pas — de 32,5 à 33,1 % des hommes nés en
  1950, de 36,9 à 37,9 % de ceux de 1954 — : ce sont les chômeurs de 60 ans
  qui le restent, 0,7 à 1,3 trimestre de plus chacun chez les hommes, 0,6 à
  2,7 chez les femmes.
- *Ce qu'aucune des quatre natures ne dit* : à 60 ans, 1,6 trimestre des
  hommes nés en 1950, de 1,0 (1956) à 2,3 (1946) selon la génération, 1,6 à
  2,4 chez les femmes ; il ne gagne plus que deux dixièmes au plus après
  60 ans, et décline avec les générations, quelques dixièmes au dernier âge vu
  des hommes nés après 1960. Le même fichier, âge par âge, dit qu'il se forme
  avant 20 ans — 2,4 trimestres aux hommes nés en 1950 —, retombe à 0,9 à
  25 ans, le cotisé et le service d'une année passant de 18 à 23 ans ce
  qu'elle valide, puis gagne 0,5 à 1,4 trimestre jusqu'à 60 ans. La DREES tient ses
  quatre types pour tout ce que les caisses enregistrent en cours de carrière,
  le chômage y comprenant la préretraite, la reconversion et la formation, la
  maladie l'invalidité (*Études et Résultats* n° 1239, août 2022, encadré 2) ;
  et ce que l'échantillon n'a pas, les caisses ne l'apprenant qu'à la
  liquidation, l'EIR le compte : les périodes validées à l'étranger, une
  partie du chômage non indemnisé, certaines périodes d'apprentissage (sa
  note 1).
- *La masse génération par génération*, lue le 24 octobre 2026 dans les
  classeurs de l'EIR que la DREES joint au jeu des caractéristiques des
  retraités : ceux des nés en 1950 (EIR 2016) et en 1953 (EIR 2020), feuille
  « QuintilesEQCC », non certifiés. La part de la durée validée qui n'est pas
  cotisée, majorations comprises : 10,9 % chez les hommes du stock de 2020,
  11,3 % chez ses résidents, 8,3 % chez les hommes nés en 1950, 9,5 % chez
  ceux de 1953 ; l'écart tient aux trois quintiles du haut de la pension en
  équivalent carrière complète, 8,7, 13,0 et 10,2 % chez les résidents de
  2020, 5,9 à 8,4 % dans les deux générations. Chez les femmes, 26,0 % dans
  le stock, 26,8 et 26,6 % dans les générations. Prise par la méthode de la
  population (`parts_assimilees_des_classes`), la masse d'une carrière pleine
  d'homme fait 6,2 % de la durée validée hors majorations dans la génération
  1950, 7,6 % dans celle de 1953, 8,6 % dans le stock des résidents : 2,6,
  3,2 et 3,6 années sur 42 ; celle d'une femme, 14,3 et 14,8 % contre 13,7.
  Les générations de l'EIR comptent leurs non-résidents, que la population
  laisse ; ils sont rares parmi les carrières pleines.
- *Ce que cela dit.*
  - La masse de la génération 1950 est ce que l'échantillon voit de toute la
    carrière des hommes nés en 1950 : 2,6 années à 67 ans, les quatre natures
    à 60 ans en faisant 2,0, le reste qu'aucune ne dit 0,4, l'après 60 ans
    0,15. Ce que la masse du stock a de plus, une année environ, tient à ses
    autres générations, plus anciennes pour la plupart — l'échantillon trouve
    déjà 2,8 et 2,9 années sans cotisation à 71 ans aux hommes nés en 1942 et
    en 1946 — ; les générations que la mesure juge, 1950 et 1955, ne l'ont
    pas, et le laisser cotisé ne touche, chez celles d'avant 1944, parties
    avant la carrière longue, ni l'âge ni la durée de leur départ.
  - L'après 60 ans ne déplace aucun départ : les carrières pleines de la
    population partent en carrière longue avant 60 ans ou à cet âge, au taux
    plein à leur âge légal sinon ; seules celles des générations nées après
    1950 qui vont jusqu'à cet âge ont des années d'après 60 ans, où le
    chômage ferait un trimestre par chômeur, sous l'année entière où la
    population compte. Il servira plutôt aux carrières incomplètes, qui vont
    au-delà de 60 ans attendre le taux plein par l'âge : le fichier le dit
    désormais.
  - Le reste n'est pas une nature qu'on puisse placer : il se forme avant
    20 ans, où l'échantillon compte autrement le validé et le cotisé, et ne
    gagne qu'un trimestre environ en cours de carrière ; ce que la DREES dit
    absent de l'échantillon, la population ne le modélise pas, ou le borne à
    quatre ou six trimestres (le chômage non indemnisé).
  - Sous le plafond de leur génération, les natures ne changeraient qu'au
    haut des rangs : celles des hommes de 1955, plafonnées par la masse de
    1953, ne perdraient d'années qu'aux classes p90 à p99, de 2,34 années en
    moyenne de leurs classes de nature à 1,83 ; celles de 1950, par la masse
    de 1950, aux classes p50 à p99, de 2,22 à 2,07 ; les femmes de 1950, aux
    classes p75 (de 2,80 à 2,20) et p90 (de 2,20 à 1,00), celles de 1955
    nulle part. Mesuré sur les classes le 24 octobre, non versé.
  - Chez les femmes, l'écart de la masse aux natures n'est pas un excès : la
    population ne leur en donne que 3,42 années sur 4,69 (génération 1950),
    quand l'échantillon trouve à ses affiliées 5,05 années sans cotisation à
    67 ans. La masse va au bas des rangs — l'EIR ne cotise pas 26 % de la
    durée validée hors majorations des résidentes du premier quintile, 3 % de
    celle du cinquième —, et les natures à chaque rang également : le haut
    est plafonné, le bas garde des années cotisées. C'est la répartition des
    natures selon le rang, que l'échantillon ne publie pas.
- *Ce qui ne bouge pas.* La population, ses versions, sa mesure, que rien ne
  refait ; la page, ni aucun moteur, témoin ou fichier fabriqué ; le
  registre. Aucune règle du scénario 1 ne change : pas d'entrée au journal de
  veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : le chômage des malades, que les classes de
   nature leur donnent à tous ; des classes de nature plus fines — cinq
   donnent 40 % de chômeurs pour 30 à 41 %, 20 % de malades pour 6 à 15 % — ;
   les natures selon le rang, quand la masse de l'EIR va au bas des rangs ;
   le plafond de chaque génération, que ses classeurs publient pour 1950 et
   1953, à certifier, s'il valait de couper le haut des rangs ; les natures
   des carrières incomplètes, qui gardent leur chômage quand l'AVPF des
   femmes qui ont cessé de travailler y est, avec son salaire au Smic dans le
   salaire annuel moyen, et le chômage d'après 60 ans de celles qui attendent
   le taux plein par l'âge ; la maternité, que l'échantillon range avec la
   maladie et que D. 351-1-2 répute sans limite depuis avril 2014, et que la
   population tient pour de la maladie, quatre trimestres ; les femmes en
   carrière longue, les carrières de trente à quarante années, allongées à
   l'âge légal, entrant toutes à 21 ans ; la durée des carrières pleines que
   la onzième version prend à l'EIR ; les invalides et les inaptes, au taux
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
