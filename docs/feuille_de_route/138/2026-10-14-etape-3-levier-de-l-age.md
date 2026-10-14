# Étape 3, troisième partie : le levier de l'âge, le « tax gap » et le « pension gap » du COR

**La demande.** Session de nuit du 14 octobre 2026, la n° 8 de dix-huit :
« action 138, étape 3, le levier de l'âge, avec le "tax gap" et le "pension
gap" du COR, que la décomposition dépendance × couverture × prestation ×
marché du travail outille » — le premier reste du bloc de l'étape, le point 2
de « Ce qui reste » de sa première partie. La trajectoire (session 7) et les
cas types (session 9) étaient tenus par d'autres, les pages par la session
10 : rien n'est écrit dans `cout.py`, `pages.js` ni la saisie.

**Ce que le COR publie, lu le jour même.** Le rapport annuel de juin 2026
(partie 2, chapitre 6, p. 123-127) et son classeur de la partie 2
(`Données_RA2026_P2.xlsx`). La figure 2.24 donne, chaque année de 2024 à
2070, la trajectoire spontanée et le niveau d'équilibre de chacun des trois
leviers, les deux autres laissés à leur évolution : en 2070, la pension
relative de 45,3 à 37,9 %, l'âge effectif de 64,6 à 67,6 ans, le taux de
prélèvement de 30,0 à 35,6 %. Le tableau 2.11, l'ajustement immédiat qui
équilibrerait en moyenne de 2026 à 2030, 2045, 2050 et 2070 : la masse des
pensions de −1,4, −3,5, −4,5 et −8,6 % (pension gap), le taux de +0,4, +1,1,
+1,4 et +2,8 points (tax gap). Dans le classeur, le titre et les notes du
tableau 2.11 sont restés ceux de 2025 (une productivité de 1,0 %) ; ses
valeurs sont celles que le rapport de 2026 imprime. Le rapport ne dit pas
comment il passe d'un manque à un âge : il renvoie à l'abaque du COR (Lettre
n° 11, avril 2015).

**Le geste de l'âge, retrouvé.** Reculer l'âge de Δ ans retire des retraités
la population des âges franchis, de l'âge spontané à cet âge plus Δ, et en
compte une part parmi les cotisants ; Δ est celui qui multiplie le rapport des
cotisants aux retraités par la dépense sur les ressources. Appliqué aux
seules séries du COR — ses cotisants par retraité, le rapport de sa pension
relative spontanée à celle d'équilibre, son âge spontané —, avec la pyramide
de l'INSEE et 17,2 millions de retraités fin 2023 qui croissent comme le COR
les fait croître, il redonne son âge d'équilibre à moins de 0,08 an chaque
année de 2030 à 2070 quand les deux tiers des retenus cotisent ; tous, il en
demande jusqu'à 0,37 an de moins, la moitié jusqu'à 0,27 de plus. Le COR ne
publie ses retraités qu'en croissance : un demi-million de plus ou de moins
déplace la part qui refait ses âges de 0,6 à 0,7.

**Ce qui est fait.**

- *`src/retraite_notionnelle/leviers.py`*, à part de `cout.py`, dont il lit le
  bilan sans y toucher : `leviers` rend pour chaque année et chaque système la
  variation de la pension (le coefficient moins un), le relèvement du taux (le
  manque sur les revenus d'activité, la part de l'assiette mesurée dans le PIB
  de sa dernière année, comme `financer`) et le recul de l'âge (`releve_age`,
  le geste ci-dessus, avec la part des reportés en emploi des réglages, la
  moitié) ; `ecarts_sur_horizon`, le pension gap et le tax gap, cumulés en
  euros constants depuis 2026 ; `leviers_du_modele` assemble le tout sous des
  réglages. Les retraités sont ceux du modèle (`AvenirAnnuel.tetes`), les
  cotisants ancrés sur le rapport que le COR observe en 2024 puis croissant
  comme l'emploi (`indice_emploi`), la génération déplacée prise à 64 ans et
  demi, l'âge spontané du COR de 2040 à 2070. Un recul hors de −10 à +15 ans
  rend `None` : le scénario 2, qui encaisse trois fois ce qu'il sert.
- *Le témoin* `tests/temoins/cor_leviers_2026.json`, écrit par
  `scripts/fetch/cor_leviers.py` depuis les feuilles « Fig 2.24 » et
  « Tab 2.11 », qui contrôle ce que le rapport imprime ; au manifeste,
  `cor_leviers_equilibre`, au statut `controle`.
- *Les tests*, `tests/test_leviers.py` : en suite rapide, le témoin, le geste
  de l'âge sur une pyramide plate et sur les séries du COR, l'arithmétique des
  leviers et des écarts ; en contrôle, les leviers et les écarts du système
  actuel contre ceux du COR, et la proposition à l'équilibre en 2070.
- *`scripts/leviers.py`* imprime la confrontation en Markdown, et les six
  systèmes (`--systemes`).
- *Le registre* : `maquette_globale_cor` (les leviers du tableau 2.11 et de la
  figure 2.24) et `retraites_scherrer` (le pilotage par l'âge), repris.

**Ce que la confrontation montre.** Le système actuel, sous la référence du
COR, celle de la page Coût (`python scripts/leviers.py`) :

| Système actuel | 2030 | 2045 | 2050 | 2070 |
|---|---|---|---|---|
| Âge, en années, modèle | +0,23 | +1,15 | +1,59 | +3,06 |
| Âge, en années, COR | +0,27 | +1,16 | +1,59 | +3,02 |
| Taux de prélèvement, en points, modèle | +0,47 | +2,08 | +2,87 | +5,63 |
| Taux de prélèvement, en points, COR | +0,46 | +2,06 | +2,84 | +5,56 |
| Pension, en %, modèle | −1,4 | −6,2 | −8,5 | −15,6 |
| Pension, en %, COR | −1,7 | −6,6 | −8,9 | −16,3 |
| Tax gap depuis 2026, en points, modèle | +0,47 | +1,08 | +1,39 | +2,78 |
| Tax gap depuis 2026, en points, COR | +0,45 | +1,09 | +1,40 | +2,76 |
| Pension gap depuis 2026, en %, modèle | −1,41 | −3,26 | −4,19 | −8,16 |
| Pension gap depuis 2026, en %, COR | −1,42 | −3,49 | −4,45 | −8,61 |

- *L'âge et le taux* sont ceux du COR à quelques centièmes : le bilan de la
  page reprend sa dépense et ses ressources, et le geste de l'âge, avec la
  moitié des reportés en emploi au lieu des deux tiers, ne lui ajoute qu'un
  vingtième en 2070.
- *Le tax gap* ne se refait qu'en euros constants : en euros courants, qui
  pèsent davantage les dernières années, il ferait 3,14 points en 2070. C'est
  donc ainsi que le COR cumule.
- *La pension* recule un peu moins chez le modèle, d'un demi-point de 2030 à
  2070, et son pension gap de 0,2 à 0,45 point : la dépense que le
  coefficient rogne compte, avec les pensions, des charges que la pension
  relative du COR ne porte pas, et l'assiette mesurée est de 3,7 % sous celle
  que le tableau 2.11 laisse déduire (`assiette_activite.csv`) — à
  départager si une page l'affiche.

**Les six systèmes** (`--systemes`), en 2070 et sur 2026-2070 :

| | Âge 2045 | Âge 2070 | Pension 2070 | Taux 2070 | Pension gap | Tax gap |
|---|---|---|---|---|---|---|
| 1. | +1,15 | +3,06 | −15,6 | +5,63 | −8,2 | +2,78 |
| 2. | — | — | +159,9 | −17,30 | +185,6 | −18,78 |
| 3. | −0,97 | — | +70,2 | −11,60 | +16,3 | −4,07 |
| 4. | −3,03 | −2,79 | +16,2 | −3,91 | +20,5 | −4,92 |
| 5. | +0,61 | −1,41 | +7,9 | −2,06 | +0,0 | −0,01 |
| 6. | +2,96 | −0,18 | +1,0 | −0,19 | −10,3 | +2,19 |

La proposition (6) finit sa trajectoire à l'équilibre, sans levier ; son
manque est celui de la transition, 3,0 ans d'âge en 2045, et sur 2026-2070 un
tax gap de 2,19 points, sous celui du système actuel. Pour les systèmes
notionnels, ces leviers sont plus mécaniques encore que ceux du COR : reculer
l'âge y relève aussi la pension, par le diviseur, ce que le geste ignore.

**Ce que ça déplace.** Rien : aucun chiffre de page, aucun témoin du site ; un
témoin de plus, celui du COR, que rien ne lit hors des tests.

**Ce qui devrait s'écrire dans les pages**, pour la session qui tient
`pages.js` et `index.html`. Sur la page Coût, à côté du coefficient et des
points d'assiette, l'âge : « Pour équilibrer le système actuel en 2070 par
l'âge seul, il faudrait partir 3,1 ans plus tard qu'à droit constant ; le COR
dit 3,0. » ; et, pour la proposition, l'âge de sa transition, 3,0 ans en
2045. Il faudrait d'abord les leviers dans le paquet : `construire_donnees.py`
les figerait dans `data/derive/agregats.json` sous les réglages de référence,
comme le reste du coût, qui ne se calcule qu'en Python.

**Ce qui reste**, de cette partie ; le reste de l'étape 3 est dans la note de
la première.

1. *Les leviers dans le paquet et sur la page Coût*, ci-dessus.
2. *L'âge spontané du modèle* : la génération déplacée se prend à 64 ans et
   demi, l'âge du COR ; l'âge moyen de départ des cas types, pesé comme les
   têtes, le remplacerait, et ferait de l'âge d'équilibre un âge, non un
   recul. Avec les têtes de la proposition (point 2 de la deuxième partie).
3. *Le niveau de vie relatif et la part de la vie en retraite* comme leviers
   (`retraites_scherrer`), et le levier de l'âge qui relève aussi la pension
   notionnelle.
4. *L'écart de la pension* au COR, un demi-point : la dépense que le
   coefficient rogne, et l'assiette.
