# Combien de retraités voient leur pension monter : le compte, au modèle tel qu'il est

**Reprise, au 13 novembre 2026.** Le compte est fait. Le propriétaire a
tranché le 13 novembre deux de ses cinq questions : les pensions des libéraux
montent, payées par leur caisse (décision 113) ; la baisse montrée à un
retraité est celle de ce qu'il touche en 2026 (décision 129). Restent pour lui
la phrase du site, et ce que la garantie regarde : la pension propre seule, ou
toutes les pensions de la personne. Le compte refait sur la grille large reste
à faire, s'il le veut.

*Le 9 novembre 2026, action 186, chantier 8, décision 90. Le modèle est celui
de `main` au commit `1c32439`, réglages de la page Coût, variante
rétroactive ; aucune ligne n'en change. Le calcul est un script tenu hors du
dépôt, qui relit la grille du coût cohorte par cohorte comme `cout._masses`
la somme. Chaque chiffre porte sa marque : (publié), lu à sa source par une
donnée certifiée du dépôt ; (dépôt), un réglage ou une sortie du modèle tel
qu'il est ; (calcul), fait ici.*

## La question

La décision 90 veut dire, sous « Chaque pension vaut ce qui a été cotisé »,
que certaines pensions montent. La page des carrières types n'en montre
qu'une aux générations déjà parties : le libéral né en 1940, + 19 %. Combien
de retraités sont dans ce cas ?

## Le calcul, posé en entier

**La grille.** Celle du coût (`castypes.GRILLE_DU_COUT`) : les treize
carrières types de la page et cinq variantes (l'agent sédentaire de la
CNRACL, les catégories active et super-active de l'État, le salarié inapte,
l'ex-invalide), à vingt-neuf générations de cinq en cinq ans, chacune
valant pour les cinq classes d'âge qui l'entourent (dépôt). Une cellule est
une carrière type, une année de naissance.

**Les têtes d'une cellule.** Le poids du cas type l'année du compte — les
retraités de sa caisse (DREES), divisés par les têtes de ses cas types,
recalés sur la dépense des six groupes du COR (`cout._ponderation`,
`cout._poids_par_groupe`) — fois l'effectif de la classe d'âge à la pyramide
de l'INSEE, fois sa survie propre (`cout._survies_alignees`). C'est le poids
que le coût lui donne. Les têtes sont mises à l'échelle des retraités de la
DREES : 17 298 245 retraités de droit direct en 2024 (publié), pour
16 858 130 têtes de la grille la même année (calcul), soit un facteur de
1,0261 (calcul).

**Les deux populations.**
- *Le stock* : les cohortes parties avant 2026, année de la bascule (dépôt),
  vivantes en 2026. 16 814 000 têtes (calcul).
- *Le flux* : les cohortes qui partent, sous le droit en vigueur, de 2026 à
  2040, comptées l'année de leur départ. 12 275 000 têtes (calcul).

**Les deux pensions du stock, en 2026.** Celle du droit en vigueur : la
pension du scénario 1 à la liquidation, menée à 2026 comme chaque régime l'a
revalorisée (`cout.coefficient_servi`). Celle de la proposition : la pension
du scénario 4, le compte rétroactif, part patronale comprise — c'est ce que
le coût sert à qui est parti avant la bascule (`cout._avant_la_bascule`) —,
menée à 2026 sous la règle du compte, la masse salariale
(`RevalorisationServie.coefficient_stock`). La pension est la part
contributive : la garantie vieillesse se compte à part, plus bas.

**Les deux pensions du flux, à leur départ, en euros de 2026.** Celle du
scénario 1 ; celle de la proposition, la pension contributive plus la rente
des cinq points capitalisés (`VoletLiberal.ressources_garantie`), à l'âge où
la proposition fait partir : 65 ans au plus tôt.

**Le classement.** Le rapport des deux pensions : « monte » au-dessus de
+ 2 %, « baisse » sous − 2 %, « stable » entre les deux.

**Un exemple, de bout en bout.** Le libéral né en 1940, parti en 2005.
À la liquidation, la proposition lui sert 18,9 % de plus que le droit en
vigueur (calcul ; c'est le + 19 % de la page). De 2005 à 2026, sa pension
actuelle a perdu 4,4 % sur les prix (coefficient 0,956), et celle de la
proposition, revalorisée sur la masse salariale, en a gagné 26,3 %
(coefficient 1,263). En 2026 : 1,189 × 1,263 ÷ 0,956 = 1,571, soit + 57 % :
2 813 € par mois au lieu de 1 791 € (calcul). Le salarié au salaire moyen né
en 1950 : − 41,4 % à la liquidation, 0,586 × 1,178 ÷ 0,955 = 0,723 en 2026,
soit − 27,7 % (calcul).

**Un contrôle.** La masse des pensions du stock ainsi comptées baisse de
27,6 % (calcul) ; la masse du scénario 4 que `cout._masses` rend pour 2026
vaut 0,7254 fois celle du scénario 1 (dépôt), soit − 27,5 %.

## Le stock : les retraités de la bascule

Pension contributive servie en 2026, la proposition face au droit en
vigueur. Têtes en milliers ; tous les chiffres (calcul).

| Régime du cas type | Têtes | Monte | Stable | Baisse | Monte | Stable | Baisse | Écart moyen |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Privé (Cnav et Agirc-Arrco) | 8 677 | 0 | 0 | 8 677 | 0,0 % | 0,0 % | 100,0 % | − 30,0 % |
| Fonction publique de l'État, civils | 1 899 | 0 | 95 | 1 803 | 0,0 % | 5,0 % | 95,0 % | − 25,4 % |
| CNRACL | 2 061 | 0 | 0 | 2 061 | 0,0 % | 0,0 % | 100,0 % | − 17,6 % |
| Militaires | 456 | 0 | 0 | 456 | 0,0 % | 0,0 % | 100,0 % | − 56,8 % |
| SNCF | 318 | 0 | 0 | 318 | 0,0 % | 0,0 % | 100,0 % | − 41,0 % |
| IEG | 292 | 0 | 0 | 292 | 0,0 % | 0,0 % | 100,0 % | − 46,9 % |
| Indépendants (artisans) | 792 | 3 | 2 | 787 | 0,4 % | 0,2 % | 99,4 % | − 23,1 % |
| Exploitants agricoles | 634 | 0 | 1 | 633 | 0,0 % | 0,2 % | 99,8 % | − 46,4 % |
| Professions libérales | 316 | 247 | 34 | 35 | 78,1 % | 10,9 % | 11,0 % | + 27,1 % |
| Contractuels publics (Ircantec) | 1 369 | 0 | 0 | 1 369 | 0,0 % | 0,0 % | 100,0 % | − 34,2 % |
| **Ensemble** | **16 814** | **250** | **133** | **16 432** | **1,5 %** | **0,8 %** | **97,7 %** | **− 28,8 %** |

Par décile de la pension actuelle — les déciles de la grille, qui ne sont
pas ceux des retraités (« Ce que la grille ne permet pas ») :

| Décile de la grille | Pension moyenne, € par mois | Monte | Stable | Baisse | Écart moyen |
|---|---:|---:|---:|---:|---:|
| D1 (sous 1 135 €) | 884 | 0,3 % | 0,2 % | 99,5 % | − 36,2 % |
| D2 | 1 176 | 0,0 % | 0,0 % | 100,0 % | − 30,4 % |
| D3 | 1 534 | 2,2 % | 0,0 % | 97,8 % | − 29,7 % |
| D4 | 1 741 | 2,2 % | 0,0 % | 97,8 % | − 17,1 % |
| D5 | 1 913 | 0,0 % | 0,0 % | 100,0 % | − 35,3 % |
| D6 | 2 061 | 0,0 % | 0,0 % | 100,0 % | − 33,1 % |
| D7 | 2 204 | 3,3 % | 0,0 % | 96,7 % | − 30,3 % |
| D8 | 2 401 | 3,8 % | 0,7 % | 95,5 % | − 30,1 % |
| D9 | 2 778 | 3,0 % | 7,0 % | 90,1 % | − 21,8 % |
| D10 (au-dessus de 3 456 €) | 4 241 | 0,0 % | 0,0 % | 100,0 % | − 23,7 % |

Ce qu'il faut en lire :

- **Qui monte.** 250 000 têtes, dont 247 000 sont le cas type du libéral,
  né de 1920 à 1957 : de + 7 % pour les plus jeunes à plus du double pour
  les plus âgés, sur des pensions de 1 130 à 3 150 € par mois (calcul). Le
  reste, 3 000 têtes, ce sont des artisans nés avant 1928, et quelques
  centaines de têtes de la génération 1920.
- **Qui reste stable.** 133 000 têtes : des fonctionnaires de l'État nés
  autour de 1960 et 1965, et les libéraux nés après 1955.
- **Le seuil ne fait pas le résultat.** À ± 1 %, 98,3 % baissent ; à ± 5 %,
  96,6 % ; à ± 10 %, 91,5 %, et 1,3 % montent encore (calcul).
- **L'ampleur.** La baisse médiane est de 28,4 % ; la moitié des têtes perd
  entre 22,6 % et 36,7 %, une sur dix plus de 45,3 %, et 82,9 % plus d'un
  cinquième (calcul).
- **La mesure, si.** La page des carrières types compare les pensions à la
  liquidation ; le coût les sert en 2026, la pension de la proposition
  revalorisée sur la masse salariale depuis le départ (+ 19,2 % en moyenne
  sur le stock) quand celle du droit en vigueur a suivi les prix, ou moins
  (− 3,4 %) (calcul). À la liquidation, 131 000 têtes montent (0,8 %),
  85 000 restent stables et 98,7 % baissent, de 40,8 % en moyenne, contre
  28,8 % en 2026 (calcul). Les deux mesures sont au modèle ; le site montre
  la première, le coût paie la seconde.
- **La première année, par cinquièmes.** Si un cinquième de chaque écart est
  fait en 2026 (décisions 3 et 87, que le coût ne porte pas), 1,3 % montent
  de plus de 2 %, 7,2 % bougent de moins de 2 %, 91,5 % baissent (calcul).

## Le flux : ceux qui partent de 2026 à 2040

Pension contributive et rente du pilier, à l'âge où la proposition fait
partir, face à la pension du droit en vigueur à son âge. Têtes en milliers ;
tous les chiffres (calcul).

| Régime du cas type | Têtes | Monte | Stable | Baisse | Monte | Stable | Baisse | Écart moyen | Départ reporté |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Privé (Cnav et Agirc-Arrco) | 6 507 | 0 | 0 | 6 507 | 0,0 % | 0,0 % | 100,0 % | − 22,0 % | 5 214, de 2,3 ans |
| Fonction publique de l'État, civils | 1 283 | 1 209 | 75 | 0 | 94,2 % | 5,8 % | 0,0 % | + 9,0 % | 591, de 2,9 ans |
| CNRACL | 1 766 | 440 | 83 | 1 242 | 24,9 % | 4,7 % | 70,3 % | − 1,3 % | 790, de 2,1 ans |
| Militaires | 202 | 202 | 0 | 0 | 100,0 % | 0,0 % | 0,0 % | + 26,2 % | tous, de 17 ans |
| SNCF | 121 | 121 | 0 | 0 | 100,0 % | 0,0 % | 0,0 % | + 31,8 % | tous, de 11,7 ans |
| IEG | 137 | 46 | 0 | 91 | 33,4 % | 0,0 % | 66,6 % | − 1,7 % | tous, de 6,7 ans |
| Indépendants (artisans) | 584 | 0 | 0 | 584 | 0,0 % | 0,0 % | 100,0 % | − 21,5 % | aucun |
| Exploitants agricoles | 392 | 0 | 0 | 392 | 0,0 % | 0,0 % | 100,0 % | − 34,8 % | tous, de 2,2 ans |
| Professions libérales | 269 | 0 | 0 | 269 | 0,0 % | 0,0 % | 100,0 % | − 11,5 % | aucun |
| Contractuels publics (Ircantec) | 1 012 | 0 | 0 | 1 012 | 0,0 % | 0,0 % | 100,0 % | − 30,4 % | aucun |
| **Ensemble** | **12 275** | **2 018** | **158** | **10 099** | **16,4 %** | **1,3 %** | **82,3 %** | **− 15,1 %** | **7 446** |

Sans la rente du pilier, la pension contributive seule : 1 085 000 montent
(8,8 %), 783 000 restent stables (6,4 %), 10 407 000 baissent (84,8 %), de
20,7 % en moyenne (calcul).

Par décile de la pension du droit en vigueur au départ (déciles de la
grille, bornes de 1 320 à 4 537 € par mois), la part qui monte : aucune aux
déciles 1, 2, 6 et 10 ; 52,9 % au décile 3 (les agents de catégorie active
de la CNRACL), 3,5 % au 4, 9,5 % au 5, 19,0 % au 7, 30,6 % au 8, 49,8 % au 9
(les fonctionnaires de l'État) (calcul).

Ce qu'il faut en lire :

- **Trois hausses qui ne se valent pas.** Des 2 018 000 têtes qui montent,
  693 000 partent la même année sous les deux droits : des fonctionnaires
  sédentaires de l'État nés autour de 1965 à 1975, de + 2 à + 8 %. 847 000
  partent un à trois ans plus tard : les catégories actives, et des
  sédentaires reportés d'un an. 478 000 partent cinq
  ans plus tard ou davantage : les militaires à 65 ans au lieu de 48 ans et
  demi, les agents de conduite au lieu de 52 ans, les super-actifs, les
  agents des IEG (calcul). Leur pension mensuelle monte parce qu'ils
  travaillent et cotisent douze à dix-sept ans de plus, pour une retraite
  d'autant plus courte : ce n'est pas la hausse que la décision 90 veut
  dire.
- **La hausse des fonctionnaires tient à une convention.** Le compte ne
  reçoit de la contribution de l'État employeur que la part que la Cour des
  comptes tient pour de la retraite, 56,3 % du taux pour un civil (dépôt,
  `docs/limites/4-regimes-incomplets.md`, hypothèse qualifiée d'`estimee`).
  Sans la rente du pilier, ils ne sont plus que 43,6 % à monter (calcul).
- **Six départs sur dix sont reportés** par l'âge légal de 65 ans (7 446 000
  sur 12 275 000), dans le privé de 2,3 ans en moyenne (calcul) : leur
  pension mensuelle baisse quand même.

## La garantie, que la grille ne sait pas compter

La grille n'a pas de queue basse, et le coût le sait : il chiffre la
garantie sur la distribution des pensions de l'échantillon interrégimes de
2020, par tranches de cent euros, non sur les cas types
(`cout.GarantieDistribution`). Le même calcul, relu pour 2026 :

- 14 831 000 retraités de 65 ans et plus en 2026, à l'échelle de l'enquête
  (dépôt, calcul du coût) ;
- 19,4 % ont une pension de droit direct sous 800 € par mois de 2026
  (680,80 € de 2020), 29,7 % sous 1 050 € (893,55 € de 2020) (publié pour
  la distribution, calcul pour l'interpolation) : 2 880 000 et 4 400 000
  personnes (calcul) ;
- au mélange des deux planchers que le recensement donne, sexe par sexe
  (« La pondération du recensement » de `docs/chiffrage_plf.md` ; 56,0 % des
  femmes et 29,0 % des hommes vivant seuls, dépôt) : **3 995 000 personnes,
  26,9 %, ont aujourd'hui une pension propre sous leur plancher** (calcul,
  par `GarantieDistribution.chiffrer_distribution` au facteur un) ;
- après la baisse — le coût déplace toute la distribution du facteur 0,7632
  (dépôt) —, 5 538 000 personnes sont sous leur plancher, 37,3 % : les
  3 995 000 d'avant, et 1 542 000 que la baisse y ramène, pour qui la
  garantie borne la perte (calcul) ;
- la page Coût n'en sert que la moitié, 2 769 000 (dépôt) : elle suppose le
  recours de l'ASPA, un ayant droit sur deux
  (`Parametres.taux_recours_garantie`).

Ces 3 995 000 personnes sont celles dont le versement mensuel peut monter.
Ce n'en est pas le compte, pour quatre raisons, toutes ouvertes :

1. Une partie touche déjà l'ASPA, dont le montant pour une personne seule,
   1 043,59 € en 2026 (dépôt, note du 7 novembre sur le message), vaut la
   garantie à 6 € près. Leur nombre n'est pas au dépôt.
2. La distribution est celle des pensions de droit direct. Si la garantie
   compte aussi la réversion gardée (décision 16), une veuve à petite
   pension propre n'y gagne rien ; le modèle ne lui oppose que la pension
   contributive et la rente du pilier.
3. Le coût suppose que la moitié ne la demande pas ; la décision 20 la sert
   d'office. À un recours entier, tous la touchent ; à un demi, 2 000 000.
4. Elle est une avance, reprise sur la succession (décisions 30 et 66). Un
   adversaire dira qu'une avance n'est pas une pension qui monte.

Sur la grille elle-même, le plancher appliqué cellule par cellule aux
retraités de 65 ans et plus fait monter 5,5 % du stock à 800 €, 8,1 % à
1 050 € — les exploitants agricoles et les salariés au SMIC les plus âgés
(calcul). Le chiffre ne vaut rien de plus : le scénario 1 de la grille ne
sert pas l'ASPA, et la grille n'a personne sous 472 € par mois.

## Les décisions que le modèle n'a pas reçues, et leur sens sur ce compte

Le relevé est celui d'une recherche par l'éclaireur, les points repris ici
relus au code. « Coût » : le coût agrégé ; « moteur » : la pension d'une
carrière, que la grille lit.

| Décision | Où en est le modèle | Sens probable sur le compte |
|---|---|---|
| 3 et 87, la baisse par cinquièmes | Ni au coût ni au moteur ; la page Coût baisse d'un coup | Rien au terme, 2030. La première année, les « stables » passent de 0,8 % à 7,2 % (calcul). |
| 43 et 71, l'Agirc-Arrco garde ses pensions jusqu'à son intégration (2032) | `integration_complementaires.py` existe, aucun calcul du coût ni du moteur ne l'appelle | Le nombre ne bouge pas : la base baisse seule de plus de 2 %. L'ampleur, si : dans le privé, − 30,0 % devient − 19,6 %, si l'écart est le même aux deux étages, ce que le modèle ne dit pas (calcul, part de l'Agirc-Arrco : 36,0 %). Avec un cinquième la première année : 15,7 % de stables. |
| 43, 70 et 86, les complémentaires que l'État règle : « baisse » des seules pensions servies ; celles qui ont des réserves restent à part | Non portée | **La seule hausse du stock est là.** La pension du libéral de la grille vient de sa complémentaire pour 15 à 69 % selon la génération, 53 % pour celui de 1940 (calcul). Les décisions ne parlent que de baisse : si une caisse à part ne remonte pas ses pensions, la hausse du libéral se réduit à sa part de base, ou disparaît. Pour le flux, les pensions liquidées après la bascule ne baissent pas : moins de baisses chez les libéraux, les artisans et les contractuels. |
| 57, l'AVPF gardée | Le modèle la retire (couche `comptes_notionnels.yaml`, « vise: avpf ») | Baisses moindres pour les parents au foyer ; aucun cas type de la grille n'en a, le compte ne bouge pas. |
| 7, les accidents de la vie gardés ; 58, la MDA d'enfant handicapé | Le compte ne crédite aucune période non travaillée | Baisses moindres pour la carrière interrompue (− 35 % à − 37 % au stock), l'inapte, l'ex-invalide ; peu de passages au-dessus de − 2 %. |
| 20, la garantie servie d'office | Le moteur la sert à la carrière ; le coût garde un recours d'un demi | Double le nombre de ceux que la garantie relève : jusqu'à 5 538 000 au lieu de 2 769 000 en 2026 (dépôt, calcul). |
| 78, la garantie dès l'invalidité | Non portée, elle s'ouvre à 65 ans | Relève avant 65 ans des invalides à petite pension ; 1 341 000 têtes du stock ont moins de 65 ans (calcul), dont les ex-invalides. |
| 16 et 56, les réversions servies gardées, sans leur majoration | Au coût, pas au moteur | Rien sur les droits directs comptés ici. Sur la pension totale, la baisse d'une veuve est moindre ; son plancher aussi, si la garantie compte la réversion. |
| 41, 44 à 46, 73 à 77, l'indexation : α = 1, plancher en euros, prime de 2,15 % | En option du coût (`indexation_liberale`) ; le défaut est la règle d'avant | La prime retenue dès la bascule retire environ 2 % à chaque pension du stock : les 133 000 « stables » passent à la baisse, les hausses du libéral restent. Ensuite, la pension servie suit les prix moins la démographie : le compte de 2026 se dégrade d'année en année. |
| 48, 25,83 % tant que l'Agirc-Arrco n'est pas intégrée | Non portée ; le moteur crédite 18 % dès la bascule | Comptes du privé un peu plus hauts pour le flux d'ici 2032 : baisses moindres, nombre inchangé. |
| 29, les lectures A et B | En étude (`scripts/lectures_decision_29.py`), pas au défaut | Rien sur le stock. Sur le flux, le taux crédité change avec la lecture : sens à lire dans la note des deux lectures. |
| 62, 65 et 69, les planchers de caisse | Le compte n'en sert déjà aucun | Neutre. |
| 79 à 81, 88 et 89, TVA, LVT, CTA, petites baisses | Recettes, hors de la pension | Aucun sur ce compte ; la décision 89 joue sur ce que le retraité paie, non sur ce qu'il touche. |

Hors des décisions : la parade du diviseur à l'âge légal
(`Parametres.stock_age_legal`, `scripts/stock_age_legal.py`), qui n'est pas
décidée, relèverait les pensions du stock parties tôt ; elle n'est pas
comptée ici.

## Ce que la grille permet d'affirmer

- **Presque toutes les pensions contributives des retraités d'aujourd'hui
  baissent.** 97,7 % au seuil de 2 %, 91,5 % à celui de 10 % ; aucun régime
  n'y échappe, sauf les libéraux. Le résultat tient à toutes les générations
  et à tous les déciles de la grille.
- **L'ordre de grandeur de la baisse, par régime**, pour une carrière
  complète : un quart à un tiers dans le privé et chez les fonctionnaires
  civils, près de la moitié pour les régimes à départ précoce et les
  exploitants agricoles.
- **Il n'y a pas, dans le stock, de hausse du côté des petites pensions
  contributives** : le décile le plus bas de la grille est celui qui baisse
  le plus (− 36,2 %). Ce qui les protège est la garantie, non le compte.

## Ce que la grille ne permet pas

- **Un nombre de personnes.** Un effectif de caisse n'est pas un effectif
  de personnes (`docs/chiffrage_plf.md`, hypothèse fragile n° 6) : le
  polypensionné compte dans chacune de ses caisses, et 1 369 000 têtes de la
  grille ont la carrière entière d'un contractuel, que presque personne n'a
  eue. Les 250 000 « libéraux qui montent » sont les 316 000 têtes que la
  grille donne à la caisse des libéraux, fois un seul cas type.
- **Le bas de la distribution.** Les déciles publiés de la pension de droit
  direct (échantillon interrégimes de 2020, résidents en France), portés aux
  prix de 2026 par le coefficient 1,1751 (dépôt) : 472 € au premier décile,
  857 € au deuxième, 1 096 € au troisième, 1 624 € à la médiane, 3 208 € au
  neuvième (publié, calcul pour les prix). La grille n'a aucune tête sous le
  premier décile publié, 4,5 % sous le deuxième, 9,2 % sous le troisième,
  26,2 % sous la médiane (calcul). Sa pension moyenne est de 2 094 € par
  mois, pour 1 805 € publiés (1 536 € de 2020) (calcul, publié). Les
  carrières incomplètes, les femmes à petite pension, les polypensionnés à
  deux demi-carrières n'y sont pas : ce sont eux que la garantie relève.
- **Le haut.** Aucun cas type au-dessus de 2,5 fois le salaire moyen ; la
  plus haute pension de la grille est de 4 635 € par mois (calcul), et 1,5 %
  des retraités de l'enquête dépassent 4 500 € de 2020 (publié).
- **La dispersion dans une cellule.** Une carrière type monte ou baisse
  tout entière. Les 95 000 fonctionnaires « stables » sont une cellule à
  − 2 % près ; autour d'elle, des carrières réelles montent et d'autres
  baissent, que le compte ne voit pas.
- **Les libéraux.** Un seul cas type, à 2,5 fois le salaire moyen — le
  plafond de la grille —, affilié à la Cipav, pour toutes les sections de
  la caisse des libéraux, dont les complémentaires n'ont ni les mêmes taux
  ni les mêmes rendements. Que toutes montent n'est pas établi.

## La phrase que le site peut écrire

Ce qu'il ne peut pas écrire sans être démenti : « certaines pensions
montent », sans dire lesquelles. Au modèle, pour les retraités
d'aujourd'hui, ce sont celles d'un cas type de profession libérale, à
2 470 € par mois en moyenne (calcul) ; un adversaire le lirait en une
minute sur la page des carrières types, et le dirait : « les seules pensions
qui montent sont celles des médecins et des avocats ». Pour un parti des
cotisants et des petites pensions, c'est la phrase à ne pas offrir.

Ce qu'il peut écrire, à la question « Ma retraite va-t-elle baisser ? » :

> Oui, pour presque tous les retraités d'aujourd'hui : la pension est
> recalculée sur ce qui a été cotisé, et sur nos carrières types elle baisse
> d'un peu plus d'un quart en moyenne. Les plus petites sont protégées : à
> 65 ans, personne ne reste sous 800 € par mois, 1 050 € pour qui vit seul.

Chaque membre de la phrase tient : « presque tous », par les 97,7 % de la
grille, à tout seuil ; « un peu plus d'un quart en moyenne », par l'écart
moyen, − 28,8 %, et l'écart médian, − 28,4 % — servis en 2026 : à la
liquidation, la mesure de la page, ce serait « quatre dixièmes » (question
4) ; le plancher, par la règle elle-même (décision 45, promesse 5), non
par un compte. Elle ne dit pas « montent », et n'a pas à compter ceux que la
garantie relève.

Si le propriétaire tient à dire qu'on y gagne, la forme qui tient est celle
de la règle, sans nombre : « Les plus petites pensions sont complétées
jusqu'à ce plancher, sans démarche. » « Sans démarche » suppose la décision
20 portée au coût ; un nombre — « quatre millions de retraités ont
aujourd'hui une pension sous ce plancher » — suppose les questions 2 et 3
ci-dessous tranchées, et le nombre des allocataires de l'ASPA lu à sa
source.

## Ce que le propriétaire tranche

1. **La phrase.** Celle proposée, qui ne dit pas « montent » ; ou la même,
   suivie de « Les plus petites pensions sont complétées jusqu'à ce
   plancher, sans démarche » ; ou « certaines pensions montent », que le
   modèle ne soutient que pour les libéraux. Piste : la première, la
   deuxième quand le coût portera la garantie d'office.
2. **La hausse des libéraux.** Le compte recalculé leur sert plus que leur
   pension. Les décisions 2, 43 et 86 ne parlent que de baisse, et la 70
   laisse leur complémentaire à part. Leurs pensions montent-elles au
   niveau du compte, ou la règle ne joue-t-elle qu'à la baisse ? La
   question était déjà ouverte (note
   `2026-11-07-complementaires-baisse-avant-integration.md`). Elle pèse
   0,45 % de la masse des pensions du stock, pour 28,1 % de baisses
   (calcul).
3. **Ce que la garantie regarde.** La pension propre seule, comme au
   modèle, ou aussi la réversion gardée et les autres pensions ? Et le
   recours : d'office, donc entier (décision 20), ou la moitié que la page
   Coût suppose encore ? Le nombre de ceux qui touchent plus en dépend : de
   2 à 4 millions, avant d'en retirer les allocataires de l'ASPA.
4. **La mesure que le site montre à un retraité.** À la liquidation, comme
   la page des carrières types (− 40,8 % en moyenne sur le stock), ou servie
   en 2026, comme le coût la paie (− 28,8 %) ? L'écart est la revalorisation
   sur la masse salariale que le compte rétroactif donne depuis le départ.
5. **Le compte sur la grille large.** `scripts/grille_large.py` décline la
   grille en personnes, en femmes, en polypensionnés, en salaires, sur les
   distributions publiées. Y refaire ce compte donnerait un nombre de
   personnes et de vrais déciles ; c'est une session d'étude, sans
   changement du modèle. Piste : oui, avant tout nombre au site.

## Sources

- DREES, échantillon interrégimes de retraités 2020 : la distribution des
  pensions par tranches de cent euros et les déciles des résidents en
  France (`data/reference/macro/pensions_residence.csv`, certifiée) ; les
  effectifs de retraités par caisse, 2004-2024.
- INSEE, projections de population 2021-2070 ; recensement 2021 pour la vie
  en couple.
- COR, rapport de juin 2026 : la dépense des six groupes de régimes, sur
  laquelle les poids de la grille sont recalés.
- Le dépôt : `src/retraite_notionnelle/cout.py` (`_pensionnes`, `_masses`,
  `_ponderation`, `_poids_par_groupe`, `GarantieDistribution`),
  `castypes.py` (`GRILLE_DU_COUT`), `docs/chiffrage_plf.md` (« La
  pondération du recensement », hypothèse fragile n° 6),
  `docs/limites/4-regimes-incomplets.md` (la contribution de l'État).
