# Étape 7, troisième partie : les hypothèses d'espérance de vie basse et haute de l'INSEE, dans le diviseur

**La demande.** Le propriétaire, le 13 octobre 2026 : « Action 138, étape 7 :
les variantes d'espérance de vie basse et haute de l'INSEE, dans le diviseur
seulement, dans les deux moteurs ; la page Coût viendra après l'action 147. »
En parallèle, l'action 152 tient `castypes.py`, `cas_types_csp.yaml` et
`grille_large.py`, l'action 147 tient `cout.py`, une seule session tient
`pages.js` et `index.html` : aucun n'est touché, et ce qui devrait s'écrire dans
les pages est plus bas. C'était le point 1 de « Ce qui reste » de la première
partie, moins la page Coût.

**Ce que la source publie, lu le jour même.** Le classeur des hypothèses de
mortalité des projections de population 2026 (`hyp_mortalite.xlsx`) porte,
à côté des feuilles `centralF` et `centralH`, les feuilles `basF`, `basH`,
`hautF` et `hautH`, de même disposition : les quotients pour 100 000 par âge
atteint dans l'année, de 0 à 120 ans et de 2023 à 2125, et sous chaque table
l'espérance de vie à la naissance, à 60 et à 65 ans. Les trois hypothèses sont
identiques en 2023 et 2024 et s'écartent dès 2025, que le dépôt tient pour
observée sous toutes. L'Insee Première n° 2108 (juin 2026), dans son encadré
des hypothèses : « les hypothèses basse et haute d'espérance de vie en 2070
s'écartent de ± 3,0 ans de cette hypothèse » — 86,5 et 92,5 ans pour les
femmes, 83,7 et 89,7 pour les hommes. Les deux feuilles de mortalité
constante sont une « hypothèse de travail », non une projection : elles ne
sont pas reprises.

**Ce qui est fait.**

- *Le récupérateur* (`scripts/fetch/insee_projections_mortalite.py`) lit les
  trois hypothèses, chacune comme la centrale, et les contrôle toutes : la
  somme des survies du classeur rend l'espérance à la naissance de 2070 que
  l'INSEE publie pour chacune (86,49 et 92,52 ans pour les femmes, 83,70 et
  89,72 pour les hommes, tolérance 0,1) ; la table convertie rend les
  espérances publiées à 60 et 65 ans, à 0,019 an au plus sous la basse,
  0,035 sous la haute (tolérance 0,05) ; chaque année, à 60 comme à 65 ans,
  la basse est sous la centrale, elle-même sous la haute. La centrale sort
  identique, valeur pour valeur.
- *La certification* écrit `quotients_projetes_basse.csv` et
  `quotients_projetes_haute.csv`, 24 200 quotients chacun, et
  `esperances_vie_variantes.csv`, les 1 200 espérances publiées sous les deux,
  au niveau `projetee`. Ces dernières ne sont lues par aucun calcul : elles
  contrôlent les tables, et `memoire.HORS_DU_MODELE` les écarte de
  l'empreinte du modèle. `sources.yaml`, la méthodologie et la ligne de la
  certification le disent.
- *Le paramètre* `hypothese_esperance_vie` (`centrale`, `basse`, `haute` ;
  `config.py`, `config.js`), rangé à côté de `scenario_projection`, choisit le
  fichier des années projetées (`donnees.mortalite.QUOTIENTS_PROJETES`). Toute
  la mortalité d'une simulation la suit, son diviseur d'abord ; une hypothèse
  inconnue est refusée, et une variante dont la table manque aussi, au lieu de
  retomber sur la loi, calée sur la centrale. La sortie d'une simulation dit
  sous laquelle elle a couru (`unite.hypothese_esperance_vie`). La fiche du
  diviseur (`coefficient_de_conversion.yaml`) le nomme parmi ses paramètres.
- *La page Coût refuse les variantes* : `Simulateur.pour_la_projection`, par
  où passent `cout.py`, `grille_large.py`, `solde_fusion.py` et
  `part_minimum_contributif.py`, lève une erreur sous la basse ou la haute.
  Sans quoi ses diviseurs et ses survies de cohortes suivraient la variante,
  et sa population, celle du scénario central, non.
- *Le paquet* (version 19) porte les deux variantes en écarts entiers à la
  centrale, en millionièmes, et d'une année sur l'autre
  (`_quotients_variantes`) : 44 Ko compressés, contre 89 pour les écarts
  bruts et 174 pour les deux tables entières. Le navigateur les cumule et les
  rajoute à la centrale (`quotientsProjetes`, `mortalite.js`) : tout se fait
  sur des entiers, et les 48 400 quotients se retrouvent au bit près. Le
  premier chargement du site passe de 1 480 à 1 525 Ko compressés.
- *Les tests* : les tables des variantes rendent leurs espérances publiées,
  ne changent que les années projetées, s'écartent de trois ans en 2070
  (`tests/test_donnees.py`) ; le diviseur encadre celui de la centrale,
  d'autant plus largement que la génération est jeune, et une génération
  éteinte avant 2026 a le même sous les trois ; le capital du compte
  rétroactif et la pension du système 1 ne bougent pas ; une hypothèse
  inconnue, une table absente et la
  page Coût sont refusées ; les deux moteurs rendent les mêmes 1 050 valeurs,
  trois carrières sous chacune des deux variantes — le test échoue de 384
  écarts si le simulateur JavaScript ignore la variante
  (`tests/test_moteur.py`) ; le
  portage refait les deux tables au bit près (`tests/js/moteur.test.js`).
- *Le registre* : les cinq points sur ce que le diviseur absorbe d'un choc de
  longévité (modello_rgs, modele_lettonie, ageing_report, fus23,
  maquette_globale_cor) restent `a_reprendre`, tous confrontés au coût ; leur
  vérification dit que le diviseur lit désormais les variantes.

**Ce que la variante déplace, mesuré le jour même.** Rien sous la centrale,
défaut : aucune pension des témoins ne bouge. Sous les variantes :

- *le diviseur à 64 ans*, table commune de génération : −0,7 % sous la basse
  et +0,7 % sous la haute pour la génération 1940, dont seuls les grands âges
  tombent après 2025 ; −3,3 % et +4,8 % pour 1960 ; −6,6 % et +8,2 % pour
  1975 ; −10,6 % et +12,5 % pour 2000. La haute pèse plus que la basse : à
  65 ans, en 2070, elle ajoute 2,4 à 2,5 ans d'espérance de vie quand la
  basse en retire 2,2 ;
- *une salariée non cadre née en 1975, partie à 64 ans* (vingtile 14) : son
  diviseur passe de 25,72 à 24,07 et à 27,81 ; sa pension du système 1 ne
  bouge pas ; celle du compte rétroactif, de même capital, en suit l'inverse,
  +6,9 % et −7,5 % ; celle du prospectif deux fois moins, +3,4 % et −3,2 %,
  son capital d'ouverture, que la bascule tire de ses droits acquis par un
  diviseur, bougeant dans le même sens que lui, −3,7 % et +5,3 % ; celle de la
  proposition, pilier capitalisé compris, +7,1 % et −7,7 % ;
- *ce que le diviseur absorbe*, sur la même carrière : sa durée de retraite
  espérée passe de 26,2 ans à 24,6 et à 28,4. Le taux de récupération du
  système 1, même pension servie plus ou moins longtemps, passe de 1,28 à
  1,21 et à 1,37 ; celui du compte rétroactif reste entre 0,414 et 0,419,
  celui de la proposition entre 0,984 et 0,998. C'est le stabilisateur que
  les cinq points du registre demandaient de montrer, vu d'une carrière ; vu
  de la dépense, il attend la page Coût.

**Ce qui devrait s'écrire dans les pages**, pour la session qui les tient. Le
réglage n'a ni champ de saisie ni contrôle de formulaire : l'adresse ne le
porte pas encore, et le site calcule sous la centrale.

1. *Les deux saisies* (`saisie.py`, `saisie.js`) : un champ, `esperance_vie`
   par exemple, lu parmi `centrale`, `basse`, `haute`, centrale par défaut,
   écrit dans `hypothese_esperance_vie` par la conversion en paramètres, et
   réécrit dans l'adresse ; puis la liste de contrôle d'un champ de saisie de
   plus (`moteur/CLAUDE.md`). Il se range dans `CLES_MODELISATION`, des deux
   côtés, avec son libellé dans `LIBELLES_MODELISATION` (`pages.js`) au même
   commit : la page lit le libellé de chaque clé (ligne 708) et tomberait sur
   une clé sans libellé. C'est pourquoi cette session n'a pas ajouté la clé.
2. *Le contrôle des réglages* (`pages.js`), à côté du scénario
   macroéconomique : trois choix, « centrale », « basse — trois ans de moins
   en 2070 », « haute — trois ans de plus », pour les systèmes 2 à 6 ; le
   système 1 n'en lit rien.
3. *`courbeDeSurvie`* (`pages.js`) lit la mortalité de `contexte.simulateur()`,
   le simulateur par défaut : sous une variante, la courbe de survie et la
   part encore en vie que la page cite ne seraient pas celles du diviseur. Elle
   doit lire le simulateur de la simulation.
4. *Les pages qui agrègent* lisent les clés de modélisation d'une adresse : la
   page Coût, dont le Python refuse les variantes, doit dire qu'elle reste
   sous la centrale, ou ne pas recevoir la clé, jusqu'à ce qu'elle les lise.

**Ce qui reste** de l'étape, dans l'ordre :

1. *Les variantes dans la page Coût*, après l'action 147 : sa population sous
   les scénarios « espérance de vie basse » et « haute » des projections de
   population 2026 (`insee_projections_population`), ses diviseurs et ses
   survies de cohortes sous les tables de ce jour, puis lever le refus de
   `pour_la_projection` ; c'est là que se chiffre ce que le diviseur absorbe
   en points de PIB (les cinq points du registre, dont le COR, ±1 point en
   2070). Et les pages du simulateur, par la session des pages, ci-dessus.
2. *La fécondité et les migrations* de la page Coût, *la mortalité
   différentielle* de ses cas types, *les départs qui suivent l'espérance de
   vie*, *la queue observée* de 85 à 98 ans, *2025* sous la loi seule : les
   points 2 à 5 de la première partie et 2 et 3 de la deuxième, inchangés.
