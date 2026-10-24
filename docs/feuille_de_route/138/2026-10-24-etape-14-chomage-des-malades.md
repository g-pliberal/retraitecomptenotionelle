# Étape 14, quatorzième partie : le chômage des malades, à la part de tous

**Le 24 octobre 2026 : la maladie a désormais son propre rang dans les
classes de nature des carrières pleines, et les malades ont le service,
l'AVPF et le chômage à la part de tous, quand la vingt-quatrième version les
mettait tous au chômage ; la vingt-cinquième version, sur `main`. Aucune
source ne croise les deux natures, mais la note de la Cnav au COR sur la
génération 1944 en borne le lien : de 29,7 à 58,5 % de ses malades ont été
au chômage, et non tous ; l'indépendance, 49,9 %, y tombe. Les hommes de la
génération 1950 partent en carrière longue pour 13,5 % et non 11,7 (EIR
18,3), ceux de 1955 pour 26,4 % et non 23,7 (28,6 chez les nés en 1953) :
plus que les 2,1 points que la convention leur avait pris le 23 octobre.
Leurs départs à l'âge légal s'éloignent d'autant de l'EIR ; les femmes et la
distribution de 2020 ne bougent presque pas. La version reste ; la page ne
bouge pas.**

Demande : la vague du 24 octobre 2026, une session par tâche, lancée par le
propriétaire : l'action 138, étape 14, le point suivant du bloc de l'étape,
et lui seul : « le chômage des malades, que les classes de nature donnent à
tous » (« Ce qui reste », point 1, de la note de la treizième partie,
`2026-10-24-etape-14-masse-apres-60-ans-et-autres-natures.md`).

- *Ce que les sources disent*, lu le 24 octobre 2026. L'échantillon
  interrégimes de cotisants publie, génération par génération, la part des
  affiliés qui ont validé chaque nature et leur cumul, non la part de ceux
  qui en ont deux ; la note de la douzième partie, qui avait le fichier en
  main, le disait. Le portail de la DREES coupant ce jour-là toute
  connexion, le fichier n'a pas été relu. Ailleurs, chaque nature se publie
  à part : la note de la Cnav au COR sur la génération 1950 (séance du
  22 mars 2018, document n° 10, note 2018-010) — 50,2 % des hommes au
  chômage, 42,1 % malades, 7,9 % invalides, toute période comprise, utile
  ou non —, le document de travail de la DREES n° 132 (Aubert et
  Croguennec, avril 2009 ; document n° 9 de la séance du 25 mai 2011). Une
  seule donne ce qui les lie : la note de la Cnav sur la génération 1944
  (séance du 25 mai 2011, document n° 10, note 2011-041, tableau 11), dont
  les retraités ayant validé quarante trimestres au moins sont 49,9 % au
  chômage, 38,1 % malades, 8,1 % invalides, 2,9 % à l'AVPF, et 76,7 % à
  avoir l'une au moins. Le chômage ou la maladie en tient donc de 76,7 −
  8,1 − 2,9 = 65,7 à 76,7 %, l'un et l'autre de 11,3 à 22,3 % : de 29,7 à
  58,5 % des malades ont été au chômage. Tous, la convention de la
  vingt-quatrième version, en sort ; la part de tous, l'indépendance, y
  tombe. Chez les femmes, la majoration de durée pour enfants, 89,3 %, ôte
  tout sens à leur 96,4 %. Le champ n'est pas celui de l'échantillon : des
  retraités, et toute période, quand l'échantillon ne compte que les
  trimestres utiles de ses affiliés d'avant 23 ans.
- *La vingt-cinquième version* (`MALADIE_INDEPENDANTE`, `rangs_de_nature`,
  dans `natures_a_leur_part`). La maladie se tire indépendamment des autres
  natures : chaque classe de nature d'un cinquième — le service et l'AVPF du
  bas de son rang, le chômage du haut — se décline en cinq classes de la
  maladie, de poids égal, dont celles dont le milieu du rang passe au-dessus
  de la part des malades le sont. Ce que les cinq classes arrondissent ne
  change pas — 40 % de chômeurs, 20 % de malades —, ni les années de
  chaque nature, ni le plafond de la classe de centiles, que les vingt-cinq
  classes se partagent comme les cinq : la masse de chaque cinquième reste
  la même. L'homme du premier cinquième né en 1950, de la classe p50, trois
  années assimilées : 20 % de malades, dont 8 au chômage et 4 au service, et
  non plus 20 au chômage ; 2,2 années par homme, comme avant. Les classes
  qui ont les mêmes natures à chaque génération n'en font qu'une : 5 000 cas
  types au lieu de 3 742, en vingt-cinq morceaux de deux cents.
- *Les tests.* Deux de plus. Les classes, posées à la main sur le fichier :
  l'homme né en 1950 de trois années, ses six classes, leurs codes et leurs
  parts, ses malades au chômage à 40 % ; la femme de huit années, ses
  5,0 années. L'homme né en 1955 de la classe p50, entré à 17 ans, jugé par
  la rédaction de D. 351-1-2 d'avril 2014, qui répute quatre trimestres de
  maladie et quatre de chômage : la classe malade sans chômage, que la
  vingt-quatrième version n'avait pas, quatre années de maladie, a
  172 − 16 + 4 = 160 trimestres cotisés ou réputés à 60 ans pour les 166 de
  sa génération, et part en carrière longue à 61 ans et demi ; la classe
  malade et au chômage, sept années, huit trimestres réputés, à 62 ans au
  taux plein ; la classe au chômage seul à 60 ans et demi, en carrière
  longue. Les deux tests de la vingt-quatrième version disent leur version
  seule, la vingt-cinquième ôtée.
- *La mesure.* Deux arbres figés sur la tête du jour, la version ôtée de
  l'un : `python scripts/grille_large.py --grille population --distribution
  --processus 4 --json`, leur `src/` sur le `PYTHONPATH`, l'un après l'autre :
  49 minutes sans la version, 68 avec, sur les quatre cœurs du conteneur.
  « Sans » redonne au dixième la mesure du 23 octobre : rien de ce qui s'est
  commité depuis ne déplace la population. Les échecs passent de 4 274 à
  5 532, un de plus par cas type ajouté, comme avant.
- *Ce qu'elle trouve*, les départs de deux générations, en part des départs
  déjà pris à l'âge où l'enquête voit la sienne, la grille 1955 jugée sur les
  nés en 1953 :

  | | EIR | sans | avec |
  |---|---|---|---|
  | hommes de 1950, avant l'âge légal | 27,6 | 21,7 | 23,5 |
  | hommes de 1950, à l'âge légal | 35,3 | 29,4 | 27,6 |
  | hommes de 1950, carrière longue | 18,3 | 11,7 | 13,5 |
  | hommes de 1955, avant l'âge légal | 40,8 | 35,0 | 37,7 |
  | hommes de 1955, à l'âge légal | 24,4 | 21,9 | 19,2 |
  | hommes de 1955, carrière longue | 28,6 | 23,7 | 26,4 |
  | femmes de 1950, avant l'âge légal | 13,0 | 9,2 | 9,2 |
  | femmes de 1950, carrière longue | 5,1 | 2,9 | 2,9 |
  | femmes de 1955, avant l'âge légal | 21,7 | 11,6 | 12,0 |
  | femmes de 1955, carrière longue | 13,0 | 5,4 | 5,8 |
  | ensemble 1950, carrière longue | 11,6 | 7,2 | 8,0 |
  | ensemble 1955, carrière longue | 20,5 | 14,2 | 15,7 |

  La distribution de 2020 : la pension moyenne des hommes passe de 1 819 à
  1 818 € (EIR 1 957), leur médiane de 1 601 à 1 600 € (1 745), l'écart de
  Kolmogorov reste de +5,3 points à 1 800 € ; celle des femmes reste à
  1 333 € (1 177), à −15,6 points à 900 €. La durée validée de chaque
  génération ne bouge pas, au dixième d'année ; la part des femmes au
  minimum reste à 30,5 % (EIR 37,7).
- *Ce que cela dit.*
  - Les malades sans chômage retrouvent la carrière longue. En 1950, la
    rédaction de 2003 répute quatre trimestres de maladie, aucun de
    chômage : le malade sans chômage, quatre années, a douze trimestres non
    réputés, comme le chômeur de trois années, et part comme lui à 59 ans et
    demi ; le malade au chômage, sept années, vingt-quatre, à 60 ans. En
    1955, la rédaction de 2014 répute quatre trimestres de chacune : le
    malade sans chômage part à 61 ans et demi en carrière longue, le malade
    au chômage à 62 ans. L'écart à l'EIR de la carrière longue des hommes
    passe de −6,6 à −4,8 points en 1950, de −4,9 à −2,2 en 1955 ; celui des
    départs d'avant l'âge légal, de −5,9 à −4,1, et de −5,8 à −3,1.
  - Les départs à l'âge légal s'en éloignent d'autant, de −5,9 à −7,7 points
    en 1950, de −2,5 à −5,2 en 1955 : ceux qui partent désormais en carrière
    longue partaient à l'âge légal. L'excès de la population est ailleurs, à
    l'âge d'annulation de la décote, que la version ne touche pas : 17,2 % des
    hommes de 1950 y partent (EIR 7,3), 17,4 % de ceux de 1955 (5,5), au taux
    plein par l'âge.
  - Les femmes ne bougent presque pas : leur carrière longue gagne
    0,4 point en 1955. Leur écart est ailleurs, les carrières de trente à
    quarante années entrant toutes à 21 ans.
  - La distribution de 2020 n'en dit rien : un euro aux hommes.
  - La version reste : la convention de la vingt-quatrième, que rien ne
    fondait, contredit la seule source qui lie les deux natures, que
    l'indépendance respecte ; et elle rapproche de l'EIR les départs
    anticipés des hommes des deux générations.
- *Ce qui ne bouge pas.* La page, qui ne lit pas la population (action 157),
  ni aucun moteur, témoin ou fichier fabriqué ; les autres grilles ; les
  carrières incomplètes et les départs avec surcote, qui n'ont pas de classes
  de nature ; le registre. Aucune règle du scénario 1 ne change : pas
  d'entrée au journal de veille.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La population*, encore : des classes de nature plus fines — cinq donnent
   40 % de chômeurs pour 30 à 41 %, 20 % de malades pour 6 à 15 %, sur
   chacun des deux rangs désormais — ; les natures selon le rang, quand la
   masse de l'EIR va au bas des rangs ; le plafond de chaque génération, que
   ses classeurs publient pour 1950 et 1953, à certifier, s'il valait de
   couper le haut des rangs ; les natures des carrières incomplètes, qui
   gardent leur chômage quand l'AVPF des femmes qui ont cessé de travailler
   y est, avec son salaire au Smic dans le salaire annuel moyen, et le
   chômage d'après 60 ans de celles qui attendent le taux plein par l'âge ;
   la maternité, que l'échantillon range avec la maladie et que D. 351-1-2
   répute sans limite depuis avril 2014, et que la population tient pour de
   la maladie, quatre trimestres, indépendante de l'AVPF désormais, que
   rien ne croise avec elle ; les femmes en carrière longue, les carrières
   de trente à quarante années, allongées à l'âge légal, entrant toutes à
   21 ans ; la durée des carrières pleines que la onzième version prend à
   l'EIR ; les invalides et les inaptes, au taux plein dès l'âge légal ; la
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
5. *La confrontation pension par pension*, au CASD, au propriétaire ; les
   microdonnées de l'échantillon y diraient aussi combien de malades sont au
   chômage.
6. *Les limites*, à la fin de l'étape (`docs/limites/5-bis-cout-agrege.md`).

Hors de l'étape : le VI de D. 634-1, la rédaction propre aux artisans et aux
commerçants, à lire rédaction par rédaction (note de la datation).
