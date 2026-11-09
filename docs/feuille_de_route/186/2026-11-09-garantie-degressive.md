# Une garantie vieillesse dégressive, pour que le travail paie toujours : les précédents lus aux sources, et chaque option chiffrée

**Reprise, au 9 novembre 2026.** Tranché (décisions 100 à 102) et écrit au
modèle, au scénario 6 seul : la forme suédoise, tout repris sur la
succession, l'isolement dans la même règle
(`2026-11-09-garantie-degressive-au-modele.md`, qui dit ce que le changement
déplace ; le coût de l'étude y est retrouvé). Par quoi commencer : le recours
de 100 % (décision 20), étape 3 du plan de la réversion ; puis le site, qui
dit encore la garantie différentielle (chantier 9). Restent ouverts, au
propriétaire : ce qui paie le surcoût, l'export dans l'Union, la CSG du
complément.

Le propriétaire, le 9 novembre 2026 : la garantie (800 € plus 250 €
d'isolement) est différentielle ; un salarié au SMIC à carrière complète,
parti à 65 ans, touche 1 125 €, soit 75 € de plus que quelqu'un qui n'a rien
cotisé. La note étudie une garantie dont la pension contributive ne retire
qu'une fraction, jusqu'à un point de sortie. Elle propose ; le propriétaire
tranche.

**Les marques.** **(publié)** : un chiffre lu dans le document cité, par la
session ou par l'agent de lecture qu'elle a lancé, citation à l'appui ;
**(publié, non ouvert)** : un chiffre que le moteur de recherche rapporte
d'une page que la session n'a pas pu ouvrir, à vérifier avant de s'en
servir. **(dépôt)** : une valeur d'un fichier du dépôt, ou une sortie du
modèle sous ses réglages par défaut, au commit `1c32439`. **(calcul)** : un
calcul de la session, posé à la fin de la note ; quand il change le barème
du modèle en mémoire, il le dit.

## L'essentiel

1. **Le constat tient, et il est plus large que le SMIC.** Sous la garantie
   différentielle, tout euro de pension en deçà du plancher est retiré de la
   garantie : la carrière à mi-temps, la carrière courte et la carrière
   hachée touchent 1 050 € seules, exactement ce que touche qui n'a jamais
   cotisé (calcul). Le droit actuel, lui, vise 85 % du SMIC net pour une
   carrière complète au SMIC, soit 18 % au-dessus du minimum vieillesse
   (publié, calcul) ; la proposition en donne 7 % (calcul).
2. **Une garantie dégressive le règle sans seuil.** Le complément devient
   max(0, plancher − t × pension) : chaque euro de pension rapporte 1 − t,
   jusqu'à la sortie, plancher / t. La Suède (48 %), le Chili (50 %), la
   Norvège (80 %), le Danemark (30,9 %) le font, chacun à sa manière
   (publié).
3. **Elle coûte cher, parce que la sortie monte dans le gros des
   pensions.** En moyenne 2026-2070, face à la garantie d'aujourd'hui et au
   recours de moitié que le modèle retient : + 0,21 point de PIB versé à
   70 %, + 0,48 à 50 %, + 1,01 à 30 % ; servie d'office (décision 20), le
   double : + 0,42, + 0,96, + 2,02 points, soit 15, 35 et 73 Md€ de 2026 par
   an (calcul sur le modèle). À 30 %, 93 % des retraités de 65 ans et plus
   la toucheraient : ce n'est plus un minimum.
4. **La reprise sur succession en rend deux cinquièmes, et change de
   nature.** Elle ramène le surcoût net à + 0,13, + 0,28 et + 0,59 point
   (recours de moitié). Mais la prime du travail devient alors un prêt :
   l'État serait créancier de la succession de 8 à 16 millions de retraités
   au lieu de 5 (d'office), et le smicard propriétaire rendrait à sa mort ce
   que son travail lui a valu.
5. **Ce que la session propose** : le taux de 70 % — le smicard à carrière
   complète y gagne 263 € par mois, 337 € de plus que qui n'a rien cotisé —,
   la prime acquise et non reprise ; à défaut, la forme suédoise, deux fois
   moins chère, qui ne paie pas les très petites carrières. Le taux de 30 %
   est à écarter.

## Le constat, vérifié

La garantie du scénario 6 porte à 800 € par mois, plus 250 € pour qui vit
seul, « l'ENSEMBLE des retraites obligatoires », compte notionnel et rente
du pilier réunis (`GarantieVieillesse.ressources`, `scenarios/notionnel.py`)
(dépôt). Elle verse max(0, plancher − pension) : en deçà du plancher, un
euro de pension de plus est un euro de garantie de moins.

Cinq carrières, nées en 2008 pour que leur compte soit plein, parties à
65 ans, sous 18 points de répartition et les 5 points obligatoires du pilier
(`capitalisation_volontaire=False`, en mémoire), en euros de 2026 par mois
(dépôt pour la pension, calcul pour le reste) :

| Carrière | Compte | Rente | Pension P | Garantie versée, seul | Total, seul | De plus que sans avoir cotisé |
|---|---:|---:|---:|---:|---:|---:|
| SMIC, carrière complète (18 à 65 ans) | 823 | 302 | **1 125** | 0 | 1 125 | **+ 75** |
| SMIC à mi-temps, complète | 434 | 159 | 593 | 457 | 1 050 | 0 |
| Carrière courte : vingt ans au SMIC | 343 | 143 | 485 | 565 | 1 050 | 0 |
| Carrière hachée : un an sur trois hors emploi | 604 | 206 | 810 | 240 | 1 050 | 0 |
| 1,2 SMIC, complète | 967 | 355 | 1 321 | 0 | 1 321 | + 271 |

Le chiffre du propriétaire est celui du modèle : 823 + 302 = 1 125 €. Les
trois carrières du milieu ont cotisé 23 % de leur salaire pendant vingt à
quarante-sept ans, et touchent ce que touche qui n'a rien versé. En couple
(plancher de 800 €), le smicard complet a 325 € de plus que son plancher,
la carrière hachée 10 €, les deux autres rien (calcul).

Deux lectures voisines, pour mesure. Sous les réglages par défaut du
modèle, qui ajoutent les 5 points volontaires du pilier, le smicard complet
a 1 427 € (dépôt). Né en 1965 et parti en 2030, son pilier n'a que quatre
ans : 1 172 € (dépôt). Le constat vaut donc surtout pour les premières
décennies de la réforme, et pour qui ne verse pas les points volontaires.

## Ce que font les autres

### La Suède : la garantipension, retirée en entier puis à 48 %

Lu dans la fiche de l'agence des pensions, « Garantipension », mise à jour
le 1er janvier 2026, et sur sa page « Garantipension – om du har låg
pension » (publié) :

- **Le montant** : « Som mest kan garantipensionen bli 11 988 kronor för
  ensamstående och 10 853 kronor i månaden för gifta » ; le prisbasbelopp
  vaut 59 200 couronnes en 2026.
- **Le barème, pour une personne seule** : jusqu'à 6 216 couronnes de
  pension contributive (1,26 prisbasbelopp), la garantie est de « 11 988
  kronor per månad […] minus din inkomstgrundade pension » — un retrait
  entier. Au-delà, elle est de 5 772 couronnes « minus 48 procent av den del
  […] som överstiger 6 216 kronor ». Elle s'éteint à 18 241 couronnes.
  L'exemple de la fiche : « 5 772 - 0,48 (9 840 – 6 216) = 4 032 kronor per
  månad ». Mariés : 10 853, 5 624 et 16 518 couronnes, même taux.
- **Ce qui la retire** : les pensions publiques contributives et les
  pensions étrangères ; ni le capital, ni les retraites d'entreprise, ni
  l'épargne privée (« Garantipensionen påverkas däremot inte av dina
  eventuella kapitalinkomster, tjänstepensioner eller privata pensioner »),
  ni la pension en capitalisation (premiepension).
- **Les conditions** : quarante ans de résidence pour le taux plein, un
  quarantième de moins par année manquante ; l'âge de référence, 67 ans
  pour les natifs de 1960 à 1964 ; examinée d'office à cet âge pour qui a
  déjà liquidé ; servie aux seuls résidents (« Garantipension kan du bara
  få utbetald om du är bosatt i Sverige »).

Ce qu'on en tire (calcul) : le pivot est à 52 % du montant maximal
(6 216 / 11 988), la sortie à 1,52 fois ce montant (18 241 / 11 988). En
deçà du pivot, la Suède a le défaut que le propriétaire décrit : la très
petite carrière ne gagne rien. Elle paie le travail à partir d'une
demi-garantie de pension, non dès le premier euro. La Suède a ajouté en
septembre 2021 un supplément de 25 à 600 couronnes par mois pour les
longues carrières à petite pension (inkomstpensionstillägg), et son budget
de 2026 inscrit 29,8 milliards de couronnes de garantipension (publié, non
ouvert) : le pays qui a inventé le compte notionnel a dû, lui aussi,
rajouter une prime au travail au-dessus de sa garantie.

### Le Chili : la PGU, entière jusqu'à un seuil, puis retirée à 50 %

Lu dans la « Nota Ciudadana Pensión Garantizada Universal 2025 » du
ministère du travail et de la prévoyance, et dans la foire aux questions de
la Superintendencia de Pensiones (publié) :

- **Le barème de 2025** : 224 004 pesos par mois, entiers pour une pension
  de base d'au plus 762 822 pesos (« pensión inferior ») ; entre ce seuil et
  1 210 828 pesos (« pensión superior »), « Monto PGU = 224.004 × (pensión
  superior − pensión base) / (pensión superior − pensión inferior) » ; rien
  au-delà. « Este monto se suma a la pensión autofinanciada ». En 2026 :
  231 732, 789 139 et 1 252 602 pesos.
- **Les conditions** : 65 ans ; vingt ans de résidence depuis l'âge de vingt
  ans, dont quatre des cinq derniers ; ne pas appartenir au dixième le plus
  riche des ménages, revu tous les trois ans ; elle se demande (« La PGU es
  un beneficio que se debe solicitar ») ; elle se cumule avec un salaire.
- **Son ampleur** : « El año 2025, son más de dos millones de personas las
  que reciben este beneficio ». La réforme de 2025 (loi n° 21.735) la porte
  à 250 000 pesos par étapes.

Ce qu'on en tire (calcul) : la pente de la zone dégressive est de
224 004 / (1 210 828 − 762 822) = 50 %, la même en 2026 (231 732 / 463 463).
Sous le seuil, le retrait est nul : la PGU est une pension forfaitaire
ouverte à neuf personnes âgées sur dix, que la pension contributive ne
réduit qu'à partir de 3,4 fois son montant (762 822 / 224 004). C'est l'autre bout
de l'éventail : le travail y paie entièrement, et la garantie y est presque
universelle. Son coût public n'a pas été trouvé.

### Les autres

- **La Norvège** : la garantipensjon du régime en comptes est retirée à
  80 % de la pension contributive (« Garantipensjonen avkortes med 80
  prosent mot inntektspensjonen », ministère) ; quarante ans de résidence
  (publié, non ouvert : la page du ministère a refusé la lecture, et les
  taux de 2026 lus chez l'administration se contredisent).
- **Le Danemark** : la pension de base (7 544 couronnes par mois en 2026)
  n'est pas réduite par les autres pensions ; le supplément (8 729
  couronnes pour une personne seule) est retiré à 30,9 % des autres revenus
  au-delà d'une franchise de 99 200 couronnes par an, et s'éteint à 438 200
  couronnes (publié, sur le site de l'association Ældre Sagen, non sur
  celui de l'État ; la même page écrit ailleurs 95 800 pour la franchise).
  Il regarde tous les revenus, non les seules pensions.
- **Le Canada** : le supplément de revenu garanti, au plus 1 138,90 dollars
  par mois pour une personne seule, s'éteint à 23 112 dollars de revenu
  annuel (publié, page du gouvernement au 13 octobre 2026) : une pente
  moyenne de 59 % (calcul). La règle de retrait n'est pas sur la page.
- **La Finlande** : non obtenue, les deux pages de la caisse étant
  introuvables.

### La France : le minimum contributif

Lu dans le document n° 4 de la séance du Conseil d'orientation des
retraites du 16 février 2023, « Les dispositifs de minima de pension et le
minimum vieillesse » (publié), et dans les barèmes du dépôt (dépôt).

**Son intention** est celle du propriétaire. « L'objectif initial –
permettre aux assurés du régime général ayant cotisé toute leur carrière
sur des faibles salaires de bénéficier d'une pension minimale – a évolué
depuis sa mise en place en 1983 » : en 2004, une majoration « au titre des
seuls trimestres d'assurance ayant donné lieu au versement de cotisations à
la charge de l'assuré », après la réforme de 2003 « fixant pour objectif de
garantir pour la pension totale un taux de remplacement net de 85 % après
une carrière complète au SMIC » ; en 2009, la condition de 120 trimestres
cotisés ; en 2012, un plafond de pension tous régimes (publié).

**Sa forme** est un seuil et non une pente : il relève la pension de base à
un minimum (756 € par mois en 2026, 904 € majoré), au prorata des
trimestres, à la condition du taux plein et, pour la majoration, de 120
trimestres cotisés, et il est écrêté quand le total des pensions dépasse
1 445 € (`minimum_contributif.csv`) (dépôt). Il n'est pas repris sur la
succession, et il est imposable ; l'ASPA, 1 043,59 € en 2026, est
« quérable et recouvrable sur succession » (publié, dépôt).

**L'écart visé** : au 1er janvier 2023, 85 % du SMIC net font 1 138,63 € et
l'ASPA 961,08 € (publié) : 177,55 € de plus pour la carrière complète au
SMIC, soit 18 % (calcul). La proposition en donne 75 sur 1 050, soit 7 %
(calcul).

**Son bilan** :
- Il coûte plus de 11 Md€ par an au régime général
  (`2026-11-07-planchers-etude.md`, calcul de cette note-là) (dépôt).
- Il est compliqué : trois conditions, deux proratas, un écrêtement tous
  régimes. Le COR en donne l'exemple d'un fonctionnaire qui touche « une
  fraction du MICO très faible » pour une année de jeunesse au régime
  général (publié).
- La revalorisation de 2023 a moins donné qu'annoncé : 1,8 million de
  retraités annoncés, environ 500 000 revalorisés en septembre 2024, 45 €
  par mois en moyenne, selon la presse qui rapporte la Cour des comptes du
  27 mai 2026 ; 185 000 nouveaux retraités aidés en 2024 selon la DREES
  (publié, non ouvert : les pages de la DREES ne répondaient pas ce jour).
- Il ne dit rien à qui n'a pas le taux plein, et son plafond crée, à
  1 445 €, la zone où un euro de pension complémentaire de plus retire un
  euro de minimum.

**Le non-recours**, qui pèse sur tout ce qui suit : « la DREES estime ainsi
qu'en 2016, 50 % des personnes seules potentiellement éligibles au minimum
vieillesse n'y ont pas recouru » ; ce taux est de « 77 % pour des montants
attendus inférieurs à 100 euros par mois », de 69 % pour les carrières
complètes, et « nettement plus élevé pour les propriétaires (72 %) que pour
les locataires (36 %), ce qui indiquerait un effet de la récupération sur
succession » (publié).

### Ce que les précédents enseignent

1. **Aucun des deux pays à comptes notionnels lus ne retire tout sur
   toute la plage** : la Suède retire 48 % au-delà d'un pivot, la Norvège
   80 %. Le retrait entier de la garantie française est l'héritage de
   l'ASPA, un minimum social, non d'un minimum de pension.
2. **Le taux fait la taille.** À 80 %, la garantie reste un filet ; à 50 %
   et sans retrait sous un seuil, elle couvre presque tout le monde
   (Chili). Entre les deux, la Suède a déplacé le pivot plutôt que le taux.
3. **Aucune des pages lues ne parle d'une reprise sur la succession**, et
   la Suède écarte expressément le capital de son barème. Parmi les pays
   lus, la France est seule à joindre un retrait entier et une reprise.
4. **La dégressivité se sert d'office ou ne se sert pas** : les petits
   montants qu'elle crée en haut de la pente sont ceux que l'on ne réclame
   pas (77 % de non-recours sous 100 €). La décision 20 y répond d'avance.

## Les options

Une seule formule, à un paramètre, le taux de retrait t :

> complément = max(0, plancher − t × pension), et il s'éteint à plancher / t.

En deçà de la sortie, le total touché vaut plancher + (1 − t) × pension :
qui n'a rien cotisé garde le plancher entier (décision 45, « personne ne
vivra sous 800 € par mois »), et chaque euro de pension en rapporte 1 − t.
Le plancher reste celui des décisions 62 et 65 : 800 € par personne, 1 050 €
seul, à 65 ans (décision 68). La forme suédoise y ajoute un pivot : retrait
entier jusqu'à la moitié du plancher, de moitié au-delà.

| Option | Un euro de pension rapporte | Sortie, seul | Sortie, en couple | Retraités de 65 ans et plus sous la sortie, en 2030 |
|---|---:|---:|---:|---:|
| Aujourd'hui, t = 100 % | 0 | 1 050 € | 800 € | 35 % |
| **A**, t = 70 % | 0,30 € | 1 500 € | 1 143 € | 52 % |
| **B**, t = 50 % | 0,50 € | 2 100 € | 1 600 € | 71 % |
| **C**, t = 30 % | 0,70 € | 3 500 € | 2 667 € | 93 % |
| **S**, suédoise : entier jusqu'à 525 € (400 €), puis 50 % | 0 puis 0,50 € | 1 575 € | 1 200 € | 55 % |

Les sorties sont des calculs (1 050 / 0,7 ; 800 / 0,7 ; …) ; les parts, des
calculs sur le modèle : les ayants droit de chaque barème sur les 15,91
millions de retraités de 65 ans et plus que le modèle compte en 2030.

## Ce que chaque option coûte

**La méthode, en une phrase.** Le coût du scénario 6 est calculé une fois
par le modèle (`memoire.cout()`, réglages par défaut) ; puis le barème de la
garantie (`garantie._manque_moyen`) est remplacé en mémoire par le barème
dégressif, et les fonctions du modèle refont, sur les mêmes masses et les
mêmes têtes, le calage sur la distribution des pensions de la DREES, le
coût année par année, les avances et les reprises sur succession. À
t = 100 %, le calcul redonne le modèle au dix-millième de point, chaque
année (contrôle, en fin de note).

**Deux recours.** Le modèle tel qu'il est suppose qu'un ayant droit sur
deux réclame la garantie (`taux_recours_garantie = 0,5`, d'après la DREES
sur l'ASPA) (dépôt). La décision 20 la sert d'office, ce que le modèle ne
porte pas encore (`2026-11-07-reversion-scenario-6-plan.md`, étape 3). Les
deux sont donnés : d'office, tout double exactement.

### En moyenne sur 2026-2070

Points de PIB, et milliards d'euros de 2026 par an (calcul sur le modèle).
« Versé » est ce que l'impôt paie chaque année ; « net », le versé moins ce
que les successions rendent (décision 30).

| | Versé | Repris | Net | Versé en plus | Net en plus |
|---|---:|---:|---:|---:|---:|
| **Recours de moitié (le modèle)** | | | | | |
| Aujourd'hui | 0,38 pt, 13,5 Md€ | 0,13 pt, 4,9 Md€ | 0,25 pt, 8,6 Md€ | — | — |
| A, 70 % | 0,59 pt, 21,0 Md€ | 0,21 pt, 7,9 Md€ | 0,37 pt, 13,1 Md€ | **+ 0,21 pt, + 7,5 Md€** | + 0,13 pt, + 4,5 Md€ |
| B, 50 % | 0,86 pt, 30,7 Md€ | 0,33 pt, 12,3 Md€ | 0,53 pt, 18,5 Md€ | **+ 0,48 pt, + 17,2 Md€** | + 0,28 pt, + 9,9 Md€ |
| C, 30 % | 1,39 pt, 49,9 Md€ | 0,56 pt, 20,7 Md€ | 0,83 pt, 29,2 Md€ | **+ 1,01 pt, + 36,4 Md€** | + 0,59 pt, + 20,6 Md€ |
| S, suédoise | 0,51 pt, 18,1 Md€ | 0,20 pt, 7,3 Md€ | 0,31 pt, 10,8 Md€ | **+ 0,13 pt, + 4,6 Md€** | + 0,06 pt, + 2,2 Md€ |
| **D'office (décision 20)** | | | | | |
| Aujourd'hui | 0,75 pt, 27,0 Md€ | 0,26 pt, 9,8 Md€ | 0,49 pt, 17,2 Md€ | — | — |
| A, 70 % | 1,17 pt, 42,0 Md€ | 0,43 pt, 15,8 Md€ | 0,75 pt, 26,2 Md€ | **+ 0,42 pt, + 15,0 Md€** | + 0,26 pt, + 9,0 Md€ |
| B, 50 % | 1,71 pt, 61,5 Md€ | 0,66 pt, 24,5 Md€ | 1,05 pt, 37,0 Md€ | **+ 0,96 pt, + 34,5 Md€** | + 0,56 pt, + 19,8 Md€ |
| C, 30 % | 2,78 pt, 99,8 Md€ | 1,11 pt, 41,3 Md€ | 1,67 pt, 58,5 Md€ | **+ 2,02 pt, + 72,8 Md€** | + 1,18 pt, + 41,3 Md€ |
| S, suédoise | 1,01 pt, 36,2 Md€ | 0,39 pt, 14,5 Md€ | 0,62 pt, 21,6 Md€ | **+ 0,26 pt, + 9,2 Md€** | + 0,13 pt, + 4,5 Md€ |

Pour mesure : la garantie d'aujourd'hui, nette, coûte 0,25 point ; la
servir d'office en coûte autant de plus, avant toute dégressivité. Le
passage à 70 % coûte, versé, un peu plus que la moitié de la garantie
d'aujourd'hui ; à 50 %, plus qu'elle ; à 30 %, près de trois fois.

### Année par année

Recours de moitié ; versé puis net, en points de PIB, et versé en milliards
d'euros de 2026 (calcul sur le modèle). D'office : le double.

| | 2026 | 2030 | 2040 | 2050 | 2060 | 2070 |
|---|---:|---:|---:|---:|---:|---:|
| Aujourd'hui | 0,46 / 0,45 ; 14,1 | 0,44 / 0,40 ; 14,2 | 0,38 / 0,27 ; 13,5 | 0,35 / 0,18 ; 12,9 | 0,35 / 0,17 ; 13,3 | 0,36 / 0,17 ; 14,1 |
| A, 70 % | 0,70 / 0,69 ; 21,6 | 0,68 / 0,62 ; 21,8 | 0,59 / 0,42 ; 20,9 | 0,54 / 0,28 ; 20,1 | 0,55 / 0,25 ; 20,8 | 0,57 / 0,26 ; 22,0 |
| B, 50 % | 1,01 / 0,99 ; 30,9 | 0,98 / 0,89 ; 31,4 | 0,87 / 0,60 ; 30,7 | 0,80 / 0,39 ; 29,6 | 0,80 / 0,34 ; 30,7 | 0,83 / 0,35 ; 32,4 |
| C, 30 % | 1,53 / 1,50 ; 47,0 | 1,52 / 1,38 ; 48,7 | 1,41 / 0,97 ; 49,6 | 1,32 / 0,63 ; 49,0 | 1,33 / 0,54 ; 50,9 | 1,38 / 0,55 ; 53,5 |
| S, suédoise | 0,61 / 0,59 ; 18,6 | 0,59 / 0,53 ; 18,7 | 0,51 / 0,35 ; 18,1 | 0,47 / 0,23 ; 17,3 | 0,47 / 0,20 ; 17,9 | 0,49 / 0,20 ; 19,0 |

Le versé est plat ; le net baisse jusqu'en 2050, à mesure que les premières
successions rendent. Les dix premières années coûtent donc presque le versé
entier : la reprise ne finance pas le démarrage.

### Les bénéficiaires

Ceux dont la pension est sous la sortie, en millions (calcul sur le
modèle). D'office, tous sont servis ; au recours de moitié, la moitié.

| | 2030 | 2070 | Moyenne 2026-2070 | En plus, en moyenne |
|---|---:|---:|---:|---:|
| Aujourd'hui | 5,57 | 5,60 | 5,35 | — |
| A, 70 % | 8,25 | 8,54 | 8,10 | **+ 2,75** |
| B, 50 % | 11,36 | 12,08 | 11,36 | **+ 6,01** |
| C, 30 % | 14,76 | 17,58 | 16,04 | **+ 10,69** |
| S, suédoise | 8,67 | 9,01 | 8,53 | **+ 3,18** |

Au recours de moitié, les bénéficiaires en plus sont 1,37, 3,01, 5,35 et
1,59 million. Les femmes font 80 % des ayants droit d'aujourd'hui, 70 % à
70 %, 62 % à 50 %, 56 % à 30 % (calcul sur le modèle) : la dégressivité
ajoute surtout des hommes, dont les pensions sont au-dessus du plancher.

### Ce que valent ces chiffres

- **Le modèle déplace la distribution de 2020 d'un seul facteur**, sans la
  déformer (`cout.py`, `GarantieDistribution`) (dépôt) : il le dit un ordre
  de grandeur pour la queue basse, et la dégressivité fait monter le barème
  dans le milieu de la distribution, où la convention est moins éprouvée.
- **La distribution est celle des droits directs** : ni la réversion gardée
  du stock (décision 16) ni les pensions étrangères n'y sont. La garantie
  compte les secondes (`ressources`) ; pour la première, rien ne le dit
  encore. Si elle compte, le coût est surestimé, surtout pour les veuves.
- **Les réglages par défaut comptent les 5 points volontaires** du pilier.
  Sans eux, le versé monte de 0,02 à 0,05 point selon l'option, et les
  surcoûts de 0,01 à 0,03 (+ 0,22, + 0,50, + 1,04 au recours de moitié)
  (calcul sur le modèle).
- **Aucun effet de comportement** : ni le travail en plus que la prime
  appelle, ni le temps partiel qu'une sortie plus haute rend moins coûteux.

## L'effet sur la reprise sur succession

La décision 30 reprend la garantie « à hauteur de ce qu'elle a avancé, et
de rien d'autre » ; l'action 47 en fait une créance au taux de l'État,
reprise dès le premier euro, sur ce que la succession contient, le logement
attendant le décès du conjoint (dépôt). Le modèle la suit, et la
dégressivité y change quatre choses (calcul sur le modèle, année 2050) :

| | Créance de l'État en cours, moitié / d'office | Part des avances que les successions rendent | Successions grevées, d'office |
|---|---:|---:|---:|
| Aujourd'hui | 193 / 385 Md€ | 40,4 % | 5,1 millions de retraités |
| A, 70 % | 294 / 588 Md€ | 41,8 % | 7,8 |
| B, 50 % | 418 / 836 Md€ | 44,2 % | 11,0 |
| C, 30 % | 636 / 1 273 Md€ | 45,2 % | 16,1 |
| S, suédoise | 252 / 505 Md€ | 44,5 % | 8,2 |

1. **La créance double ou triple.** D'office et à 50 %, l'État tiendrait en
   2050 une créance de 836 Md€ de 2026 sur les successions de onze millions
   de retraités, sept sur dix.
2. **Elle se recouvre un peu mieux**, les nouveaux bénéficiaires ayant plus
   de patrimoine : de 40 % à 42-45 % des avances. C'est ce qui ramène le
   surcoût net aux trois cinquièmes du versé.
3. **La prime du travail devient un prêt.** Le smicard à carrière complète
   reçoit, à 70 %, 263 € par mois : en vingt ans, 63 000 € de 2026 hors
   intérêts ; à 50 %, 488 € et 117 000 € (calcul). S'il laisse un logement,
   sa succession les rend, intérêts compris. Le travail ne paie alors que
   pour qui ne laisse rien — l'inverse du message. Et le premier motif de
   non-recours est déjà la reprise (72 % chez les propriétaires) : d'office,
   elle s'imposerait à des millions de gens qui ne l'auraient pas demandée.
4. **Une autre lecture de la décision 30 existe** : reprendre ce qui porte
   au plancher, l'aide, et tenir pour acquise la prime au-dessus, qui
   récompense des cotisations — comme le minimum contributif, que nul ne
   reprend. Les reprises restent alors celles d'aujourd'hui (0,13 point au
   recours de moitié, 0,26 d'office), et le surcoût net est le surcoût
   versé. Net, la garantie coûterait alors (calcul) :

| Prime acquise | Net, recours de moitié | Net, d'office |
|---|---:|---:|
| A, 70 % | 0,45 pt, 16,1 Md€ | 0,91 pt, 32,2 Md€ |
| B, 50 % | 0,73 pt, 25,8 Md€ | 1,45 pt, 51,7 Md€ |
| C, 30 % | 1,26 pt, 45,0 Md€ | 2,51 pt, 90,0 Md€ |
| S, suédoise | 0,37 pt, 13,2 Md€ | 0,75 pt, 26,4 Md€ |

## Ce que chaque option donne à cinq carrières

Les cinq carrières du constat, nées en 2008, parties à 65 ans, 18 + 5
points, en euros de 2026 par mois. Le gain est ce que l'option ajoute à ce
que la garantie d'aujourd'hui leur laisse (dépôt pour la pension, calcul
pour le gain). Sous le plancher, il vaut (1 − t) × pension ; entre le
plancher et la sortie, plancher − t × pension.

**Seul (plancher de 1 050 €) :**

| Carrière | Pension | Aujourd'hui, total | A, 70 % | B, 50 % | C, 30 % | S, suédoise |
|---|---:|---:|---:|---:|---:|---:|
| SMIC, complète | 1 125 | 1 125 | **+ 263** | **+ 488** | **+ 713** | + 225 |
| SMIC à mi-temps | 593 | 1 050 | + 178 | + 297 | + 415 | + 34 |
| Courte, vingt ans au SMIC | 485 | 1 050 | + 146 | + 243 | + 340 | 0 |
| Hachée, un an sur trois | 810 | 1 050 | + 243 | + 405 | + 567 | + 142 |
| 1,2 SMIC, complète | 1 321 | 1 321 | + 125 | + 389 | + 654 | + 127 |

**En couple (plancher de 800 €) :**

| Carrière | Pension | Aujourd'hui, total | A, 70 % | B, 50 % | C, 30 % | S, suédoise |
|---|---:|---:|---:|---:|---:|---:|
| SMIC, complète | 1 125 | 1 125 | + 13 | + 238 | + 463 | + 38 |
| SMIC à mi-temps | 593 | 800 | + 178 | + 297 | + 415 | + 97 |
| Courte, vingt ans au SMIC | 485 | 800 | + 146 | + 243 | + 340 | + 43 |
| Hachée, un an sur trois | 810 | 810 | + 233 | + 395 | + 557 | + 195 |
| 1,2 SMIC, complète | 1 321 | 1 321 | 0 | + 139 | + 404 | 0 |

Trois lectures :
- **Le smicard seul passe de 75 € à 337, 562 ou 787 € au-dessus de qui n'a
  rien cotisé** (1 387, 1 612, 1 837 € contre 1 050 €) ; l'écart de 18 %
  que vise le droit actuel est dépassé dès 70 % (32 %) (calcul).
- **Le travail paie partout sous A, B et C** : la carrière courte gagne 146
  à 340 €. Sous la forme suédoise, elle ne gagne rien seule, et le mi-temps
  34 € : la forme paie les carrières longues, non le travail en général.
- **En couple, à 70 %, le smicard complet ne gagne presque rien** (13 €) :
  sa pension touche déjà la sortie du plancher de 800 €.

Né en 1965, parti en 2030, le smicard complet a 1 172 € : il gagne 230,
464 et 699 € (calcul). Sous les réglages par défaut (dix points au pilier),
né en 2008, il a 1 427 € et gagne 51, 337 et 622 €.

## Le point de sortie, et les seuils qu'il crée

**Pas de marche.** Le complément s'éteint en pente : à la sortie il vaut
zéro, et un euro de pension de plus n'y fait rien perdre. C'est l'avantage
de la pente sur le seuil du minimum contributif. Le seul pli est celui du
taux : 1 − t par euro sous la sortie, un euro au-dessus.

Mais la dégressivité déplace ou crée cinq seuils qu'il faut voir :

1. **L'isolement pèse sur bien plus de monde.** Aujourd'hui, se mettre en
   couple ne coûte les 250 € qu'à qui est sous 1 050 €. Sous une pente,
   toute pension sous 800 / t les perd en entier, et en partie jusqu'à
   1 050 / t : à 50 %, le smicard complet gagne 488 € seul et 238 € en
   couple, et deux smicards qui s'installent ensemble perdent 500 € par
   mois (calcul). C'est, à grande échelle, l'incitation à se déclarer seul
   que l'on reproche aux minima sociaux, et un contrôle de la vie commune
   étendu à la moitié des retraités.
2. **L'âge de 65 ans.** La garantie s'ouvre à 65 ans (décision 68). Plus
   elle est large, plus l'attente coûte à qui part avant : à 70 %, le
   smicard complet attend jusqu'à 65 ans une prime de l'ordre de 263 € par
   mois.
3. **La résidence.** La garantie ne se sert qu'en France, comme l'ASPA. Un
   complément dont le montant dépend de la pension cotisée ressemble
   davantage à une pension qu'à un minimum social, et les pensions
   s'exportent dans l'Union. La Suède ne sert sa garantipension qu'à ses
   résidents (publié) ; que le droit de l'Union laisse faire de même pour
   une garantie dégressive française n'a pas été instruit ici : c'est à
   vérifier avant de décider (règlement n° 883/2004, article 70 et annexe X,
   cités de mémoire).
4. **Les prélèvements.** La garantie, si elle suit l'ASPA, ne paie pas de
   CSG (`2026-11-07-planchers-etude.md`, une inférence) (dépôt) ; la
   pension en paie. Un complément de 263 à 713 € exonéré, à côté d'une
   pension qui ne l'est pas, pèse sur les seuils de CSG et d'impôt des
   retraités : non chiffré.
5. **Les planchers des caisses** (décisions 42, 62, 65). Le minimum garanti
   des fonctionnaires et ses voisins ne tiennent que tant que leur caisse a
   des réserves ; la garantie les relaie ensuite. Dégressive, elle les
   relaie mieux : à 70 %, un fonctionnaire au minimum garanti (1 366 € seul,
   `2026-11-07-planchers-etude.md`) toucherait 94 € de complément au lieu
   de rien (1 050 − 0,7 × 1 366) (calcul).

## Ce que la session propose

1. **Retenir le principe.** Le défaut est réel, il touche toutes les
   petites carrières et non le seul SMIC, et ni la Suède ni la Norvège ne
   retirent tout. Une pente vaut mieux qu'un seuil : le minimum contributif
   montre ce qu'un seuil à conditions devient en quarante ans.
2. **Le taux de 70 %** (option A). Il est le moins cher qui paie le travail
   dès le premier euro : + 0,21 point versé au recours de moitié, + 0,42
   d'office. Il donne au smicard complet 337 € de plus qu'à qui n'a rien
   cotisé, près du double de l'écart que vise le droit actuel. Sa sortie,
   1 500 € seul, reste sous la pension moyenne de droit direct (1 693 € en
   2024, `pensions_brutes_nettes.csv`) (dépôt) : la garantie demeure un
   minimum.
3. **Écarter 30 %**, qui sert neuf retraités sur dix et coûte 2 points
   d'office ; **tenir 50 % pour le plafond** de ce qui se discute : il sert
   sept retraités sur dix.
4. **Si le coût de A est trop haut, la forme suédoise** : moitié moins
   chère, elle donne presque autant au smicard seul (225 €), mais rien à la
   carrière courte. Elle répond au constat du propriétaire, non au mot
   « toujours ».
5. **Tenir la prime pour acquise**, et ne reprendre que ce qui porte au
   plancher : sans cela, le travail paierait par un prêt. Cela coûte, pour
   A, 0,08 point de plus au recours de moitié et 0,16 d'office (0,45 contre
   0,37 ; 0,91 contre 0,75) (calcul).
6. **Servir d'office**, ce que la décision 20 a déjà dit : la pente crée de
   petits montants, que l'on ne réclame pas.

## Ce qui reste, après la réponse

- **Au modèle, au scénario 6 seul** (décision 28), une session du modèle,
  le test d'abord : le taux de retrait en paramètre, dans `_manque_moyen`
  et dans `_garantie_vieillesse` et leurs jumeaux du portage ; la reprise
  bornée à la part différentielle, si elle est retenue ; le recours de
  100 % (étape 3 du plan de la réversion).
- **À instruire aux textes** : l'export dans l'Union ; la CSG et l'impôt
  sur le complément ; ce que la reprise devient pour un couple dont un seul
  touche la prime.
- **À lire quand la DREES répondra** : la fiche 8 de son panorama des
  retraites et son étude n° 1297 sur le minimum contributif ; le rapport
  de la Cour des comptes du 27 mai 2026.
- **Le site** : la page Coût et le simulateur ne changent qu'après le
  modèle (chantier 9).

## Les sources

- Pensionsmyndigheten, fiche « Garantipension », PM 7615, mise à jour le
  1er janvier 2026 (lue en entier) ; page « Garantipension – om du har låg
  pension », mise à jour le 3 novembre 2026 :
  `pensionsmyndigheten.se/forsta-din-pension/sa-fungerar-pensionen/garantipension-om-du-har-lag-pension`.
- Chili, Subsecretaría de Previsión Social, « Nota Ciudadana Pensión
  Garantizada Universal 2025 » (lue en entier) :
  `previsionsocial.gob.cl/wp-content/uploads/2025/12/Nota-Ciudadana-Pension-Garantizada-Universal-2025.pdf` ;
  Superintendencia de Pensiones, questions fréquentes sur la PGU :
  `spensiones.cl/portal/institucional/594/w3-article-15170.html`.
- Canada, « Supplément de revenu garanti : montant de la prestation » :
  `canada.ca/en/services/benefits/publicpensions/old-age-security/guaranteed-income-supplement/benefit-amount.html`.
- Danemark, Ældre Sagen, « Folkepension », mise à jour le 22 octobre 2026 :
  `aeldresagen.dk/viden-og-raadgivning/penge-og-pension/folkepension`.
- Norvège : `nav.no/garantipensjon` (taux contradictoires à la lecture) ;
  `regjeringen.no`, « Viktige begreper om pensjon » (non ouvert).
- Conseil d'orientation des retraites, séance du 16 février 2023, document
  n° 4, « Les dispositifs de minima de pension et le minimum vieillesse »
  (lu en entier) :
  `cor-retraites.fr/sites/default/files/2023-02/Doc_04_Minima%20de%20pension%20et%20Aspa.pdf` ;
  il cite P. Meinzel, « Le non-recours au minimum vieillesse des personnes
  seules », Les dossiers de la DREES, n° 97, mai 2022.
- Non ouverts ce jour : DREES, « Les retraités et les retraites », fiche 8,
  et Études et résultats n° 1297 (le site répondait 503) ; la loi chilienne
  n° 21.419 ; le budget suédois de 2026 (utgiftsområde 11).

## Les calculs, en entier

Faits le 9 novembre 2026 au commit `1c32439`, sans qu'une ligne du dépôt
change. Deux scripts du bac à sable de la session, qui ne sont pas au
dépôt ; ce qui suit suffit à les refaire.

**1. Le barème.** Le modèle chiffre la garantie sur la distribution des
pensions de la DREES par tranches de 100 € (`garantie.py`) : pour chaque
tranche, `_manque_moyen(inférieure, supérieure, plancher)` rend la part de
la tranche sous le plancher et le manque moyen, pensions uniformes dans la
tranche. Le barème dégressif le remplace, mêmes conventions :

```python
def bareme(taux, pivot=0.0):
    def complement(pension, plancher):
        p0 = pivot * plancher
        if pension <= p0:
            return plancher - pension
        return max(0.0, plancher - p0 - taux * (pension - p0))

    def manque(inferieure, superieure, plancher):
        p0 = pivot * plancher
        sortie = p0 + (plancher - p0) / taux
        if superieure is None:            # tranche ouverte : masse ponctuelle
            m = complement(inferieure, plancher)
            return (1.0, m) if m > 0 else (0.0, 0.0)
        if inferieure >= sortie:
            return 0.0, 0.0
        bornes = sorted({inferieure, superieure,
                         *(b for b in (p0, sortie) if inferieure < b < superieure)})
        aire = sum((b - a) * (complement(a, plancher) + complement(b, plancher)) / 2
                   for a, b in zip(bornes, bornes[1:]))
        largeur = superieure - inferieure
        return (min(superieure, sortie) - inferieure) / largeur, aire / largeur
    return manque
```

Options A, B, C : `bareme(0.7)`, `bareme(0.5)`, `bareme(0.3)` ; S :
`bareme(0.5, 0.5)` ; le contrôle : `bareme(1.0)`.

**2. Le coût.** Sous `memoire.modele_modifie()` :
1. `memoire.cout(Parametres())`, en gardant ce que `calculer_cout` passe à
   `_garantie_distribution` (ses arguments) et à `_reprises_successions`
   (les lignes d'avenir avant les reprises, et le simulateur).
2. Pour chaque option : `garantie._manque_moyen` et `cout._manque_moyen`
   remplacés par le barème ; `_garantie_distribution` rappelée, qui recale
   la distribution, la mortalité des bénéficiaires et la part de qui vit
   seul ; son `taux_recours` mis à 0,5 ou à 1.
3. Pour chaque année, sur le facteur et l'effectif de la ligne du modèle
   (qui ne dépendent pas du barème) : `chiffrer_distribution(effectif,
   facteur)`, d'où les ayants droit, les bénéficiaires (× recours) et le
   versé (`cout_annuel_meur × vers_constants × recours`).
4. `_reprises_successions` du modèle sur ces lignes : avances, part
   reprise, reprises, créance en cours.
5. Points de PIB : montant en euros constants / `coefficient_constants` /
   `pib` de la ligne. Milliards de 2026 : le montant constant
   (`annee_euros_constants = 2026`). Moyenne : la moyenne simple des 45
   années 2026 à 2070, comme `scripts/indexation_scenario_6.py`.

**Le contrôle.** À t = 100 % et au recours de 0,5, versé puis net, en
points de PIB, le modèle intact puis ce calcul : 2026, 0,4603 / 0,4522 et
0,4603 / 0,4522 ; 2040, 0,3817 / 0,2718 et 0,3817 / 0,2718 ; 2070, 0,3616 /
0,1718 et 0,3616 / 0,1718. Identiques aux six années de vue.

**Ce que le calage porte** (dépôt) : la distribution de 2020 ; le plancher
de 800 € de 2026, soit 680,80 € de 2020, et 893,55 € seul ; vivent seuls
56,0 % des femmes et 29,0 % des hommes bénéficiaires ; le facteur de
déplacement, 0,805 en 2030 et 0,979 en 2070 ; 15,91 millions de retraités de
65 ans et plus en 2030 ; un PIB de 3 065 Md€ en 2026.

**3. La prime acquise.** Net = versé de l'option − reprises de la garantie
d'aujourd'hui, à recours égal. À 70 %, recours de moitié : 0,585 − 0,132 =
0,453 point, 21,0 − 4,9 = 16,1 Md€ ; d'office : 1,171 − 0,264 = 0,907
point, 42,0 − 9,8 = 32,2 Md€. À 50 % : 0,857 − 0,132 = 0,725 ; 1,714 −
0,264 = 1,450. À 30 % : 1,388 − 0,132 = 1,256 ; 2,777 − 0,264 = 2,513.
Suédoise : 0,505 − 0,132 = 0,373 ; 1,009 − 0,264 = 0,745. C'est une
approximation : elle suppose que la part différentielle se recouvre comme
aujourd'hui.

**4. Les cinq carrières.** `Simulateur(replace(Parametres(),
capitalisation_volontaire=False))` ; le cas type `smic_carriere_complete`
(`castypes.py`, profil au SMIC, début à 18 ans) et quatre variantes par
`dataclasses.replace` : `niveau_salaire=0.5` (mi-temps) ; `niveau_salaire=
1.2` ; la carrière courte, `interruptions_relatives` = `inactivite` aux
années 20 à 46 de la carrière ; la carrière hachée, une interruption aux
années 2, 5, 8, …, 44, tour à tour `chomage_indemnise` et `inactivite`.
Pour chacune : `cas.carriere_a(sim, 2008, 65)`, `sim.simuler(carriere)`,
puis, dans `notionnel_liberal.garantie_vieillesse`, `pension_contributive`,
`rente_capitalisee` et `ressources`, multipliées par
`macro.coefficient_prix(annee_ouverture, 2026) / 12`.

| Carrière | Compte | Rente | P = ressources |
|---|---:|---:|---:|
| SMIC, complète | 822,91 | 301,93 | 1 124,85 |
| SMIC à mi-temps | 433,87 | 159,32 | 593,19 |
| Courte | 342,51 | 142,97 | 485,48 |
| Hachée | 604,15 | 205,56 | 809,71 |
| 1,2 SMIC | 966,83 | 354,62 | 1 321,45 |

Gain = complément de l'option − complément d'aujourd'hui, par la fonction
`complement` ci-dessus. Le smicard seul : aujourd'hui max(0, 1 050 −
1 124,85) = 0 ; à 70 %, 1 050 − 0,7 × 1 124,85 = 262,6 ; à 50 %, 1 050 −
562,4 = 487,6 ; à 30 %, 1 050 − 337,5 = 712,5 ; suédoise, 525 − 0,5 ×
(1 124,85 − 525) = 225,1. La carrière courte seule : aujourd'hui 1 050 −
485,48 = 564,5 ; à 70 %, 1 050 − 339,8 = 710,2, soit + 145,6 = 0,3 ×
485,48 ; suédoise, pension sous le pivot de 525 : + 0. Le smicard en
couple, à 70 % : 800 − 787,4 = 12,6.

**5. Les autres calculs.** Sorties : 1 050 / 0,7 = 1 500 ; 1 050 / 0,5 =
2 100 ; 1 050 / 0,3 = 3 500 ; 800 / 0,7 = 1 142,9 ; 800 / 0,5 = 1 600 ;
800 / 0,3 = 2 666,7 ; suédoise, 525 + 525 / 0,5 = 1 575 et 400 + 400 / 0,5
= 1 200. Parts sous la sortie en 2030 : 5,57 / 15,91 = 35 % ; 8,25 / 15,91
= 52 % ; 11,36 / 15,91 = 71 % ; 14,76 / 15,91 = 93 % ; 8,67 / 15,91 = 55 %.
Suède : 6 216 / 11 988 = 0,52 ; 6 216 + 5 772 / 0,48 = 18 241 ; 18 241 /
11 988 = 1,52. Chili : 224 004 / (1 210 828 − 762 822) = 224 004 / 448 006
= 0,500 ; 231 732 / (1 252 602 − 789 139) = 0,500 ; 762 822 / 224 004 =
3,4. Canada : 1 138,90 × 12 / 23 112 = 0,591. France : 1 138,63 − 961,08 =
177,55, et 177,55 / 961,08 = 18,5 % ; 75 / 1 050 = 7,1 % ; 337 / 1 050 =
32 %. Minimum contributif de 2026 : 9 075,50 / 12 = 756,29 ; 10 847,22 /
12 = 903,94 ; 17 338,68 / 12 = 1 444,89. La prime en vingt ans : 262,6 ×
12 × 20 = 63 024 ; 487,6 × 12 × 20 = 117 024. Le fonctionnaire au minimum
garanti : 1 050 − 0,7 × 1 366,35 = 93,6. Successions grevées en 2050,
d'office : les ayants droit de l'année.

## Ce que le propriétaire tranche

1. **Le principe** : la garantie cesse-t-elle d'être différentielle ? Elle
   coûte alors, d'office, de 0,26 à 2,0 points de PIB de plus par an.
2. **La forme et le taux** : une pente dès le premier euro, à 70 % (ce que
   la session propose), 50 % ou 30 % ; ou la forme suédoise, moitié moins
   chère, qui ne paie pas les très petites carrières.
3. **La reprise** (décision 30) : la prime du travail est-elle reprise sur
   la succession comme le reste, ou acquise ? Reprise, elle coûte moins
   (0,26 point net de plus à 70 %, d'office, contre 0,42) mais fait de
   l'État le créancier de huit millions de successions, et du gain un prêt.
4. **L'isolement** : les 250 € restent-ils dans la pente, où ils pèsent sur
   tout couple de petits retraités jusqu'à la sortie, ou deviennent-ils un
   montant à part, retiré en entier ?
5. **Le recours** : confirmer que la garantie dégressive est servie
   d'office (décision 20), et donc que ses chiffres sont ceux de la seconde
   moitié du tableau.
6. **Le financement** : ce qui paie le surcoût — la TVA, qui paie déjà la
   garantie, ou la part de l'économie des droits familiaux qui va au
   déficit (chantier 3).

## Ce que le propriétaire a tranché

Le 9 novembre 2026, après deux explications demandées — le principe, « un
concept nouveau de mon côté », puis la forme suédoise et ses seuils — :
« Ça me plaît, j'aimerais mettre ça en place ». Trois réponses, devenues
les décisions 100 à 102 du programme.

1. **La forme** : « Forme suédoise », et non la pente à 70 % que la session
   proposait. La pension est retirée en entier jusqu'à la moitié du
   plancher, de moitié au-delà ; le complément s'éteint à une fois et demie
   le plancher.
2. **La reprise** : « Tout est repris avec intérêt ». La décision 30 vaut
   pour le supplément comme pour le reste.
3. **L'isolement** : « La même règle que pour les 800€ ». Le plancher d'une
   personne seule reste 1 050 €, la forme s'y applique en entier.

Aux deux dernières questions, le propriétaire a d'abord demandé : « Que
fait la Suède ? » Ce qui lui a été répondu :

- **La succession.** Aucune des sources lues ne parle d'une reprise de la
  garantipension sur l'héritage ; la fiche de l'agence écarte le capital du
  barème, et les seules reprises trouvées sont celles des trop-perçus
  (publié, non ouvert, pour ces dernières). Aucun texte lu ne dit pour
  autant « jamais reprise ». Suivre la Suède aurait voulu dire ne rien
  reprendre : 1,01 point net d'office, contre 0,62 tout repris (calcul sur
  le modèle). Le propriétaire ne la suit pas.
- **L'isolement.** La Suède tient deux barèmes de même forme : 11 988
  couronnes, pivot à 6 216 et sortie à 18 241 pour qui n'est pas marié ;
  10 853, 5 624 et 16 518 pour qui l'est (publié). L'écart, 1 135 couronnes,
  fait 10 % du barème des mariés, contre 31 % pour les 250 € (calcul) ; il
  reste dans la pente, 827 couronnes au-dessus des pivots (calcul). Et le
  critère est l'état civil : « Som gifta räknas även registrerade partners
  och sammanboende som har gemensamma barn eller tidigare har varit gifta
  med varandra » (publié) — deux concubins sans enfant commun y restent
  « seuls ». La décision 102 suit la forme suédoise, non son montant ni son
  critère, que le propriétaire n'a pas retenus.

**Ce que la forme retenue donne**, d'après les tableaux de la note (calcul
sur le modèle, moyenne 2026-2070, d'office) : 1,01 point de PIB versé par
an, 36,2 Md€ de 2026, dont 0,39 repris ; 0,62 net. En plus de la garantie
d'aujourd'hui servie d'office : 0,26 point versé, 9,2 Md€ ; 0,13 net,
4,5 Md€ ; 3,2 millions de bénéficiaires de plus, 8,5 millions en tout. La
créance de l'État sur les successions atteint 505 Md€ de 2026 en 2050,
contre 385. Le smicard seul gagne 225 € par mois ; le mi-temps, 34 € ; la
carrière hachée, 142 € ; la carrière courte, rien.

**Ce qui reste ouvert**, des six questions : ce qui paie le surcoût (la
sixième), que le propriétaire n'a pas tranché ; et, à instruire aux textes
avant de publier, l'export dans l'Union et la CSG du complément.

## La consigne de la session du modèle

Une session neuve, de la zone du modèle, au scénario 6 seul (décision 28),
le test d'abord. Elle lit ce bloc, `src/CLAUDE.md` et `moteur/CLAUDE.md`.

**La règle à écrire.** Deux paramètres de plus, à côté de
`garantie_vieillesse_mensuelle` (`config.py`, et son miroir de
`moteur/js/config.js`) : la part du plancher jusqu'où la pension est
retirée en entier, 0,5 ; le taux de retrait au-delà, 0,5. À un et un, la
règle redonne la garantie différentielle. Avec p0 = part × plancher :

> complément = plancher − ressources, si ressources ≤ p0 ;
> sinon max(0, plancher − p0 − taux × (ressources − p0)).

Les ressources, le plancher (800 €, plus 250 € seul), l'âge, la résidence
et l'indexation ne changent pas.

**Où.** Pour une carrière : `_garantieVieillesse` de
`moteur/js/scenario-notionnel.js`, qui fait foi, puis son jumeau
`_garantie_vieillesse` (`scenarios/notionnel.py`), au bit près. Pour le
coût, en Python seul : `_manque_moyen` (`garantie.py`), que lisent
`cout_garantie`, `_garantie_distribution` et `_reprises_successions`
(`cout.py`) ; le barème de « Les calculs, en entier », point 1, en est la
forme, à reprendre et non à copier. La fiche
`data/reference/regles/proposition/garantie_vieillesse.yaml` et la limite
qui dit la garantie différentielle suivent.

**Les tests, posés à la main** (euros par mois). Seul, plancher de 1 050 €,
p0 de 525 € : ressources 0 → 1 050 ; 400 → 650 ; 525 → 525 ; 600 →
525 − 0,5 × 75 = 487,50 ; 1 124,85 → 525 − 0,5 × 599,85 = 225,08 ;
1 575 → 0 ; 1 600 → 0. En couple, plancher de 800 €, p0 de 400 € : 0 →
800 ; 400 → 400 ; 593,19 → 400 − 0,5 × 193,19 = 303,41 ; 1 124,85 →
400 − 0,5 × 724,85 = 37,58 ; 1 200 → 0. Le complément ne croît jamais avec
les ressources, et le total ne décroît jamais.

**Ce que le coût doit redonner**, au recours de 0,5 que le modèle porte
encore : versé 0,505 point de PIB en moyenne 2026-2070, net 0,309 ; en
2030, versé 0,59 et 8,67 millions d'ayants droit. Un écart dirait une
erreur, ici ou là-bas.

**Ce qui n'est pas dans cette étape** : le recours de 100 % (décision 20),
étape 3 du plan de la réversion (`2026-11-07-reversion-scenario-6-plan.md`),
à mener avec elle ou juste après, qui double ces chiffres ; le site, qui
dit encore la garantie différentielle, après le modèle (chantier 9).
