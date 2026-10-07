# Étape 7, première partie : les quotients projetés de l'INSEE au lieu de la loi de Gompertz-Makeham

**Reprise, au 7 octobre 2026.** Fait : les quotients de l'hypothèse centrale
de l'INSEE, de 2026 à 2125, convertis à l'âge exact et lus âge par âge par les
deux moteurs au lieu de la loi de Gompertz-Makeham ; les espérances projetées
reprises telles que l'INSEE les publie. Reste, dans cet ordre : les variantes
d'espérance de vie basse et haute, dans le diviseur et la page Coût (le même
classeur) ; la fécondité et les migrations dans la population de la page Coût
(seize scénarios de l'INSEE) ; la mortalité différentielle des cas types de la
page Coût ; les départs qui suivent l'espérance de vie ; 2025, sous la loi
seule. Commencer par les variantes d'espérance de vie. Détail : « Ce qui reste ».

**Le 7 octobre 2026, la demande.** Le propriétaire : « 138.7 ». L'étape 7 de
l'action : « La démographie en variantes : les quotients projetés âge par âge
au lieu de la loi de Gompertz-Makeham, les variantes de l'INSEE de 2026 —
fécondité, espérance de vie, migrations —, dans la population du Coût et dans
le diviseur. » Le registre y range dix-huit points, chez dix-sept modèles ;
cette première partie fait le premier volet, que trois modèles font mieux que
le dépôt : Destinie 2, Typfallsmodellen et les coefficients italiens.

**Ce que la source publie, lu le jour même.** Le classeur des hypothèses de
mortalité des projections de population 2026 (`hyp_mortalite.xlsx`) porte huit
feuilles — hypothèses centrale, basse, haute et mortalité constante, par
sexe —, les quotients pour 100 000 par **âge atteint dans l'année**, de 0 à
120 ans et de 2023 à 2125, et, sous chaque table, l'espérance de vie à la
naissance, à 60 et à 65 ans de chaque année. Le dépôt écrivait que l'INSEE ne
publie jamais e65 et la dérivait des quotients, par la somme des survies de la
table par âge atteint : juste à la naissance, elle sous-estimait e60 et e65
jusqu'à 0,09 et 0,12 an en 2026, chez les hommes, l'écart s'effaçant vers 2125.

**Ce qui est fait.**

- *Le récupérateur* (`scripts/fetch/insee_projections_mortalite.py`) lit les
  quotients centraux et les espérances publiées. Il convertit chaque quotient
  à l'âge exact : le quotient de l'âge atteint x couvre un parallélogramme du
  diagramme de Lexis, de l'âge exact x − 1 à x + 1, et la cellule du modèle est
  un carré, de x à x + 1 ; le carré prend la moyenne géométrique des survies
  des deux parallélogrammes qui l'encadrent, et 120 ans garde le sien. Deux
  contrôles l'autorisent : la somme des survies du classeur retrouve
  l'espérance à la naissance publiée pour 2070 (89,50 et 86,71 ans pour 89,5
  et 86,7), et la table convertie les espérances publiées à 60 et 65 ans, à
  0,018 an au plus sur cent ans et deux sexes (tolérance 0,05). À la
  naissance, l'écart passe le dixième : les décès de la première année
  tombent dans ses premières semaines, ce qu'aucun calcul du modèle ne lit.
- *La certification* écrit `data/reference/mortalite/quotients_projetes.csv`,
  24 200 quotients au niveau `projetee`, et reprend les 600 espérances
  publiées (508 corrigées) ; `sources.yaml`, l'en-tête des espérances, le
  README, les limites et la méthodologie le disent.
- *Les deux moteurs* lisent, cellule par cellule, le quotient observé, puis le
  projeté, puis la loi : de 2026 à 2125, la loi ne sert plus à aucun âge ; au-
  delà de 2125, les quotients de 2125 ; en 2025, que ni Eurostat ni la
  projection ne couvrent, la loi garde la main. Le paquet porte
  `quotients_projetes` (version 17) : 354 Ko bruts de plus, 84 Ko compressés.
- *Les tests* : la table projetée prime sur la loi et rend les espérances
  publiées (`tests/test_donnees.py`), son portage aussi
  (`tests/js/moteur.test.js`).

**Ce que la loi rendait, mesuré.** Sur la table du moment, de 2026 à 2125, la
loi calée sur e60 et e65 rendait ces deux espérances à deux centièmes près,
mais surestimait l'espérance à 75 ans de 0,1 à 0,3 an, à 85 ans de 0,6 à
1,0 an, à 90 ans de 0,9 à près de 1,5 an, à 95 ans de 0,8 à 1,6 an. Elle
faisait vivre les très vieux trop longtemps, et, pour tenir ses deux cibles,
mourir un peu trop tôt entre 65 et 80 ans. Ce que le passage déplace :

- *le diviseur de la population générale* à 64 ans : −2,1 % pour la
  génération 1940, dont les grands âges tombent dans les années projetées,
  −0,4 % pour 1960, −0,1 % pour 1975, +0,2 % pour 2000 ;
- *les vingtiles de niveau de vie*, davantage et en sens contraire, parce
  qu'un même facteur sur la force de mortalité porte sur les grands âges des
  plus aisés et sur les âges de 65 à 80 ans des plus modestes. Génération
  1975, à 64 ans : +2,1 % pour le premier vingtile, −1,4 % pour le dernier,
  −0,7 % pour les fonctionnaires civils de l'État ; l'écart entre le premier
  et le dernier diviseur passe de 7,1 à 6,2 ans. Les transferts que le
  diviseur commun opère entre populations, chiffrés au §5 de la
  méthodologie, baissent d'autant — de 10 à 13 % ;
- *les témoins* : aucune pension du scénario 1 ne bouge ; celles des
  scénarios notionnels, de +0,3 à +0,4 % en médiane sous les rétroactifs, de
  −0,1 à −0,2 % sous les prospectifs, de −2,3 % (le premier vingtile) à
  +2,3 % (un artisan né en 1940) aux extrêmes ;
- *la page Coût*, au dixième de point de PIB : la dépense du système actuel
  ne bouge pas jusqu'en 2070, où la pyramide de l'INSEE la porte ; son
  engagement acquis en 2021, qui prolonge les cohortes au-delà par la table
  du dépôt, passe de 481 à 479 % du PIB ; le système 6 voit son solde moyen
  de 2026 à 2070 passer de −0,90 à −0,94 % du PIB, et sa dette en 2070 de 59
  à 62 %, la moitié des reportés travaillant (étape 3) ;
- *la confrontation de l'étape 9*, l'espérance de vie à 60 ans de chaque
  génération contre celle de l'INSEE que publie le COR, se resserre : à
  0,02 an près dès 1960, à 0,08 avant, et la génération 1941, dont les
  quotients observés font une marche, passe de +0,62 à +0,32 an chez les
  hommes ; la session de l'étape 9 a resserré son test d'autant (0,05 et
  0,15 an, au lieu de 0,1 et 0,45) ;
- *l'accueil* : la baisse médiane des pensions à venir passe de 22,6 à
  22,5 %, et la phrase calculée dit désormais « de l'ordre d'un cinquième à un
  quart » au lieu d'« un quart » ; le budget de lecture de ses tableaux passe
  de 240 à 245 mots, pour les trois mots de la seconde fraction.

**Le parcours de présentation** suit ses pages : trois carrières, la part
financée de l'exemple (2 510 €), la ligne des fonctionnaires sédentaires et
l'ordre de grandeur de l'accueil. Ses comptes de la page Données étaient déjà
périmés sur `main` depuis l'étape 4 (45 576 valeurs et 129 séries, quand la
page en écrivait 45 679 et 131) : ils disent désormais 70 149 et 138, avec
les séries que les autres étapes du jour ont ajoutées. La
référence de la conservation est refigée en acceptant ces paragraphes, comme
à l'étape 16 de l'action 147.

**Le registre** passe trois points à `repris` : Destinie 2 (les quotients
projetés, et l'écart à la queue, désormais mesuré), Typfallsmodellen et les
coefficients italiens (la mortalité âge par âge ; leur réversion tarifée dans
le diviseur reste un choix de l'étape 13).

**Ce qui reste** de l'étape, dans l'ordre :

1. *Les variantes d'espérance de vie*, dans le diviseur et la page Coût : les
   feuilles `bas` et `haut` du même classeur, à porter comme la centrale, et
   une variante démographique à côté de `scenario_projection`. C'est la seule
   façon de montrer ce que le diviseur de génération absorbe d'un choc de
   longévité (modello_rgs, modele_lettonie, ageing_report, fus23,
   maquette_globale_cor, qui chiffre ±1 point de PIB en 2070).
2. *La fécondité et les migrations*, dans la population de la page Coût et
   son dénominateur : les seize autres scénarios des projections de
   population 2026, à lire comme le central (`insee_projections_population`)
   — destinie_2, trajectoire, retraites_cor2026, aphrodite, pensionsmodellen.
3. *La mortalité différentielle* des cas types de la page Coût, qui vivent
   tous comme la population générale (`cout.py`) quand le diviseur connaît
   déjà les vingtiles et les fonctionnaires : misraa, pablo, canopee, prisme
   (les inaptes de la Cnav).
4. *Les départs qui suivent l'espérance de vie*, en variante de comportement
   (mosart).
5. *2025*, sous la loi seule jusqu'à ce qu'Eurostat publie sa table ; et la
   queue au-delà de 94 ans des années 2014 à 2024, que les tables TD/TV de
   l'INSEE (`insee_tables_mortalite`, à faire) couvriraient.
