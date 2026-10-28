# Étape 14 : le juge propre des artisans, la part passagère des indépendants, la carrière saisonnière des salariés agricoles

**Le 28 octobre 2026 : les artisans de la population ont leur juge propre, le
minimum contributif que le RSI servait avant 2018. Nés en 1946, 34,6 % d'entre
eux ont une pension portée au minimum, quand l'EIR de 2012 en trouve 33 % chez
les artisans unipensionnés et 37 % chez les commerçants ; mais 36,4 % des
hommes, pour 23 et 34, et 20,5 % des femmes, pour 58 et 40. La part passagère
de leur revenu, qu'une source approche par la mobilité, reste en variante :
elle les ferait tomber à 15,5 %. La carrière saisonnière des salariés agricoles
a sa source, la MSA : parmi ses liquidants depuis 2017, un quart des hommes ont
moins de 48 trimestres aux régimes alignés ; parmi ceux de la population, 6,7 %
ont moins de dix ans. Rien ne change de la population.**

Demande : la vague du 28 octobre 2026, « action 138, étape 14 : les
indépendants et les agricoles », le point 1 de « Ce qui reste » de la note de
la vingtième partie : la part passagère du revenu des indépendants et la
carrière saisonnière des salariés agricoles, si une source les publie ; le
juge propre des artisans, la part des liquidants du RSI au minimum contributif
d'avant 2020.

- *Les sources.* Le site de la DREES ne répondait pas à la session ce jour-là
  (connexion coupée, 503 à la lecture en ligne), ni Internet Archive, ni
  data.gouv.fr : l'EACR, où la note de la septième partie voulait chercher le
  RSI, n'a pas pu être relue. Ses chiffres sont venus d'ailleurs, de cinq
  documents que la session atteint, inscrits au sas
  (`data/sources_a_explorer.yaml`) : deux documents du COR, qui reprennent le
  RSI (séance du 26 mars 2013, document n° 11) et la fiche 9 de l'édition 2018
  des « Retraités et les retraites » de la DREES (séance du 24 mai 2018,
  document n° 3) ; l'article de Loisel et Sicsic dans Économie et Statistique
  n° 545 ; deux études de la MSA.
- *Le juge propre des artisans* (`part_minimum_contributif.py --artisans`,
  `RSI`, `mesurer_artisans`, `parts_des_artisans`). Jusqu'en 2017, l'artisan
  du modèle liquide sa pension de base au RSI (`rsi.yaml`, fermé en 2018), et
  la mesure du régime général ne le voyait pas ; depuis 2019, l'EACR le compte
  à la Cnav, sans le distinguer. La mesure simule ses seuls cas types (378
  carrières, aux générations 1941 à 1961, quarante secondes sur quatre cœurs),
  avec les retraités de l'étranger, que ses trois juges comptent, et les pèse
  comme la mesure du minimum : servis l'année de leur départ, éligibles avant
  l'écrêtement (`part_eligible`, que `_part` rend désormais), ou au minimum dans
  leur génération. En pour cent :

  | | ensemble | femmes | hommes | publié : artisans ; commerçants |
  |---|---|---|---|---|
  | liquidants de 2011, servis | 32,2 | 25,0 | 34,7 | 40 ; 47 (le RSI, au COR) |
  | liquidants de 2016, éligibles | 32,5 | 30,6 | 33,5 | 44 ; 50 (l'EACR) |
  | nés en 1946, au minimum | 34,6 | 20,5 | 36,4 | unipensionnés : 33, F 58, H 23 ; 37, F 40, H 34 (l'EIR de 2012) |

  Les deux flux comptent tous les liquidants du RSI, et la plupart sont
  polypensionnés : avant 2012, chaque régime aligné servait son minimum, au
  prorata de ses trimestres, et un passage court au RSI, mal payé, y était
  relevé, quand l'artisan de la population l'est toute sa carrière. Ce sont
  les unipensionnés de l'EIR qui le jugent au plus près. Leur ensemble est
  juste ; leurs sexes ne le sont pas. Trop d'hommes au minimum, comme le
  premier quartile de leur pension de 2020, trop bas devant la fiche 1.11 de
  l'INSEE ; trop peu de femmes, comme leur pension, trop haute (1 058 € en
  moyenne en 2020, pour 820, à la note de la septième partie). La dispersion
  des revenus des non-salariées de 2022, que l'artisane prend, n'est sans
  doute pas celle des artisanes nées en 1946. En 2016, l'éligible est servi :
  seul au RSI, un artisan au minimum reste sous le plafond de l'écrêtement.
- *La part passagère du revenu des indépendants*, en variante
  (`PART_PASSAGERE_DES_INDEPENDANTS`, `CORRELATION_DES_RANGS`,
  `DISPERSION_DES_INDEPENDANTS` ; `resserrer` prend désormais le resserrement
  en argument). Aucune source ne sépare la part passagère du revenu d'un
  indépendant. L'article de Loisel et Sicsic s'en approche : dans le panel des
  déclarations de revenus, le rang de 2021 d'une personne de 25 à 49 ans en
  2003 se corrèle à 0,52 avec le sien de 2003 quand elle était indépendante, à
  0,70 quand elle était salariée (§ 3.1.6). La variante en tire le
  resserrement d'une carrière d'indépendant : ce que garde une carrière
  salariée de la variance de la coupe, 0,58, fois le rapport des deux
  corrélations ; ses écarts au centre en gardent 0,655, et non 0,76. Elle
  relève le premier décile de l'artisan de 0,232 fois le salaire moyen à
  0,294 chez les hommes, de 0,212 à 0,261 chez les femmes, la moyenne gardée.
  Elle reste débrayée, pour deux raisons. La première
  tient à la source : sa corrélation mêle à la part passagère les changements
  d'activité, plus fréquents chez les indépendants, et le passage à la
  retraite, son champ ayant 43 à 67 ans en 2021 ; sur 2003-2019, l'Insee
  Analyses n° 82 donnait 0,59 et 0,71, et les deux années où partent les plus
  âgés ôtent 0,07 à la corrélation des indépendants, 0,01 à celle des
  salariés. La seconde tient au juge propre, qui la dément :

  | | ensemble | femmes | hommes |
  |---|---|---|---|
  | liquidants de 2011, servis | 32,2 → 19,9 | 25,0 → 24,9 | 34,7 → 18,1 |
  | liquidants de 2016, éligibles | 32,5 → 21,6 | 30,6 → 30,6 | 33,5 → 17,4 |
  | nés en 1946, au minimum | 34,6 → 15,5 | 20,5 → 19,4 | 36,4 → 15,1 |

  Les hommes passent sous les artisans unipensionnés (23 %), l'ensemble sous
  la moitié de l'EIR, et les femmes ne bougent pas : le défaut est celui de
  l'écart entre les sexes, qu'un resserrement commun aux deux ne corrige pas.
  Son effet sur leur pension de 2020, que la fiche 1.11 juge, n'est pas
  mesuré : il y faut la population entière, plus de deux heures de
  simulation ; sur les seuls artisans, la pesée de la page se fausse, la
  pesée par caisse leur donnant les têtes d'autres carrières (1 861 € de
  moyenne, pour 1 234 à la mesure entière du 17 octobre).
- *La carrière saisonnière des salariés agricoles.* Deux études de la MSA la
  décrivent. Le bilan du minimum contributif de 2005 à 2015 (Synthèses,
  janvier 2018) attribue le nombre de ses bénéficiaires « à la forte présence
  de saisonniers » : des polypensionnés, trois nouveaux pensionnés sur quatre
  à moins de 40 trimestres au régime, aux salaires agricoles « peu élevés et
  non représentatifs des autres revenus perçus dans la carrière ». Mais tout y
  précède la liquidation unique de 2017, après laquelle le dernier régime
  aligné liquide pour tous, et l'EACR de 2019 à 2024, que la population
  confronte, ne compte plus que ses liquidants. L'étude de la liquidation
  unique au 31 décembre 2021 (janvier 2023) les décrit : 69,1 % des nouveaux
  retraités de la MSA salariés liquident en Lura, et parmi eux 25,7 % des
  hommes ont moins de 48 trimestres aux régimes alignés, 12,3 % des femmes ;
  42,1 et 47,9 % plus de 155. Les salariés agricoles de la population (un
  pilote hors du dépôt : les poids de 2020 fois la part agricole de chaque
  carrière, retraités de l'étranger compris, par tranche de durée) :

  | | moins de 10 ans | 10 à 20 | 20 à 30 | 30 à 40 | 40 et plus |
  |---|---|---|---|---|---|
  | hommes | 6,7 | 6,8 | 3,6 | 21,6 | 61,3 |
  | femmes | 11,9 | 13,2 | 15,9 | 36,1 | 22,9 |

  Les tranches ne tombent pas sur les seuils de la MSA, mais l'écart est net
  chez les hommes : la population a quatre fois moins de carrières courtes
  parmi ses salariés agricoles que la MSA parmi ses liquidants, et c'est là
  que le minimum proratisé se sert, à l'âge du taux plein. Elle les prend
  comme le salariat privé, dont elle leur donne une part de chaque carrière
  selon son rang (note de la sixième partie), et non selon sa durée. Les
  donner selon la durée ne suffirait pas : l'EIR les compte par régime
  principal, la MSA par régime qui liquide, et leurs salaires agricoles, que
  rien ne publie, ne sont pas ceux du reste de leur carrière. La population
  n'est donc pas changée.
- *Ce qui ne bouge pas.* La population, ni ses poids ni ses carrières ; la
  page, qui ne la lit pas (action 157) ; aucun moteur, aucun témoin. Aucune
  règle du scénario 1 ne change : pas d'entrée au journal de veille. Les tests
  (`test_part_minimum_contributif.py`, `test_grille_large.py`) : le minimum du
  RSI lu dans le scénario 1, avant et après l'écrêtement, que la mesure du
  régime général ne voit pas ; la pesée des artisans sur les trois juges ; la
  variante et son resserrement, débrayée et embrayée.

**Ce qui reste** de ce point, le reste de l'étape étant au bloc « Reprise » :

1. *Les sexes des artisans* : trop d'hommes au minimum, trop peu de femmes,
   devant le juge propre ; la dispersion des revenus des non-salariés de
   chaque sexe, prise en 2022, n'est pas celle des générations parties.
2. *La carrière saisonnière des salariés agricoles* : leur part selon la
   durée, que la MSA publie pour ses liquidants, et leurs salaires agricoles,
   que rien ne publie.
3. *La part passagère des indépendants*, si une source la mesure chez ceux
   qui restent à leur compte, hors du passage à la retraite.
