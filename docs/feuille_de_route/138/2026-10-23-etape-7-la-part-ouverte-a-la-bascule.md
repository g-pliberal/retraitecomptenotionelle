# Étape 7, quinzième partie : le déficit des scénarios 3 et 5, le diviseur sur la seule part du compte ouverte à la bascule

**La demande.** Vague du 23 octobre 2026 : la session de suivi « Qu'est-ce
qu'il reste à faire ? » lance, sur la demande du propriétaire (« Fait ça »),
douze sessions en parallèle, une étape chacune ; celle-ci, l'action 138,
étape 7 : le premier point de « Ce qui reste » de la note « la prémisse du
déficit », le déficit des scénarios 3 et 5, en Python seul — n'appliquer le
rapport des diviseurs qu'à la part du compte ouverte à la bascule, que la
grille ne garde pas, puis remesurer contre la page. Ni les décimales du
coefficient au-dessus de un, qui attendent une session des pages, ni les
départs qui suivent l'espérance de vie, au propriétaire ; et rien de ce que
les actions 166 et 170 lui demandent de la bascule et de la page Coût des
scénarios 3 et 5 : la session mesure, sans rien en trancher. Aucune règle du
scénario 1 n'est en cause : ni veille du droit, ni entrée au journal.

**Ce que fait le script, désormais** (`e139c37`).
`scripts/mortalite_population.py --deficit` multipliait toute la pension des
scénarios 3 et 5 par le rapport des diviseurs de son vingtile. Ils gardent
pourtant à qui part au plus tard l'année de la bascule la pension du droit en
vigueur (`ScenarioNotionnel._deja_liquide`), et les droits acquis à la
bascule entrent au compte par le diviseur du vingtile et en sortent par lui
(`_droits_acquis`). Le rapport ne touche plus que la part de chaque pension
que porte le compte ouvert à la bascule : `_parts_ouvertes` la lit sur la
simulation de la carrière que la page construit, un moins la part de son
capital que portent les droits acquis (`capital_droits_acquis`,
`capital_notionnel`), et `_masses` applique `part × rapport + (1 − part)`.
La grille de la page ne garde pas ces capitaux, que le portage simule : le
moteur Python resimule ses carrières, une demi-minute de plus au script. La
part vaut zéro pour qui part au plus tard l'année de la bascule, un pour qui
entre au travail l'année de la bascule ou après, un aux scénarios 2, 4 et 6,
qui n'ont pas de droits acquis. Le salarié au salaire moyen né en 1965, parti en 2028, en a
2 % au scénario 3 et 5 % au scénario 5, dont le compte reçoit aussi la part
patronale, sur les mêmes droits acquis ; né en 1990, 40 % et 62 %.

Elle se lit, comme la page lit la pension, sur la génération de la grille,
pour ses cinq cohortes : quand la bascule en sépare une, la page lui sert la
pension de la grille (action 170, point 5), et le script lui donne la même
part. Elle se lit aussi sur la bascule telle que le modèle la fait
aujourd'hui, sa date, son diviseur, ce qu'elle fige (action 166) : ce qu'il
en sera décidé passera au script sans qu'on y touche.

**La mesure.** `python scripts/mortalite_population.py --deficit`, puis avec
`--depuis 2026`, sur `main` au 23 octobre (`b16b5ad`), avant et après. Baisse
de la dépense, à la survie de la page, et ce que le diviseur par vingtile
ajoute au solde moyen de 2026 à 2070, en points de PIB :

| | 2030 | 2050 | 2070 | Solde moyen |
|---|---:|---:|---:|---:|
| Scénario 3, avant | 3,1 % | 3,0 % | 2,9 % | +0,326 |
| Scénario 3, désormais | 0,0 % | 0,5 % | 1,7 % | +0,054 |
| Scénario 5, avant | 3,1 % | 3,1 % | 3,0 % | +0,386 |
| Scénario 5, désormais | 0,1 % | 1,0 % | 2,2 % | +0,114 |

À la mortalité générale, les scénarios 3 et 5 baissent désormais de 0,0 et
0,1 % en 2030, 0,5 et 0,9 % en 2050, 1,6 et 2,2 % en 2070. Le flux seul,
depuis 2026, dit pour eux la même chose que le stock compris : leur stock
d'avant la bascule ne sent plus le diviseur. Les scénarios 2, 4 et 6 ne
bougent pas : 3,6, 3,7 et 3,6 % en 2030, 3,3, 3,4 et 3,1 % en 2050, 3,1, 3,1
et 2,9 % en 2070, +0,149, +0,358 et +0,304 point de solde moyen ; depuis
2026, +0,11, +0,26 et +0,21. Le premier tableau du script, qui ne montre pas
les scénarios 3 et 5, ne bouge pas : la survie de la page déplace la masse du
système actuel de +2,3, +2,2 et +1,9 % en 2030, 2050 et 2070, le rapport de
masses des scénarios 2, 4 et 6 de +0,1 à +0,8 %.

**Contre la page.** `calculer_cout` sous son défaut, le diviseur par vingtile
(`population_conversion="niveau_de_vie"`), et sous la table commune, même
`main`, par un script de travail non commité ; ce que le diviseur par vingtile
ajoute au solde moyen de 2026 à 2070, en points de PIB :

| Scénario | La page | Le script, avant | Le script, désormais | Au rapport des pensions de la page | Avec la survie de la page |
|---|---:|---:|---:|---:|---:|
| 2 | +0,130 | +0,149 | +0,149 | +0,149 | +0,133 |
| 3 | +0,017 | +0,326 | +0,054 | +0,047 | +0,013 |
| 4 | +0,323 | +0,358 | +0,358 | +0,359 | +0,310 |
| 5 | +0,090 | +0,386 | +0,114 | +0,107 | +0,077 |
| 6 | +0,283 | +0,304 | +0,304 | +0,307 | +0,266 |

Le script dépassait la page de 0,31 et 0,30 point aux scénarios 3 et 5 ; il
la dépasse désormais de 0,037 et 0,024, comme des 0,019 à 0,035 des scénarios
2, 4 et 6. L'avant-dernière colonne remplace le rapport de chaque couple par
celui de ses pensions sur la page, sous ses deux réglages, le même pour ses
cinq cohortes : ce que la règle simplifie, des droits acquis qui entrent au
diviseur de 65 ans en 2026 et sortent à celui du départ, coûte 0,007 point
aux scénarios 3 et 5, trois millièmes au plus ailleurs. La dernière ajoute au
script ce que la survie de la page déplace du rapport de masses (sa
dépense multipliée par `1 − ρ σₛ/σₐ`, où `ρ` est le rapport des masses sous
les deux diviseurs, `σ` celui de la survie de la page à la mortalité
générale, du scénario et du système actuel) : elle tombe à 0,017 point au
plus de la page, dans les cinq scénarios, à 0,004 au scénario 3 et 0,013 au
5. L'écart qui restait au script est donc, aux scénarios 3 et 5 comme aux
autres, la survie, que la page compte et que son solde n'ajoute pas ; le
reste, les poids de chaque année, la revalorisation des pensions servies
que les masses du script ne portent pas, la règle simplifiée, tient en moins
de deux centièmes de point.

**Les tests** (`tests/test_mortalite_population.py`, suite rapide) :
`test_aux_scenarios_3_et_5_le_diviseur_ne_touche_que_le_compte_ouvert_a_la_bascule`,
un couple posé à la main, dont le rapport des diviseurs vaut un demi et dont
le compte ouvert à la bascule porte le quart de la pension au scénario 3, les
trois quarts au 5 — il en garde 0,875 et 0,625, la moitié au scénario 2, toute
partie avant la bascule, et le flux de 2030 n'en touche que la cohorte de
1966 ; `test_la_part_ouverte_a_la_bascule_se_lit_sur_le_compte_de_la_simulation`,
le salarié au salaire moyen né en 1955, 1965 et 2005. Chacun vu rouge sur le
comportement : la forme neuve d'abord écrite sous la règle d'avant — 524 pour
917, une part de un pour celle de zéro —, puis corrigée.

**Ce qui reste**, dans l'ordre :

1. *Aux pages, le coefficient au-dessus de un* (douzième partie, point 2) :
   une session des pages.
2. *La forme de la surmortalité* (onzième partie, point 2), pour les inaptes
   et les ex-invalides.
3. *La limite, à la fin de l'étape* (note « la prémisse du déficit »,
   point 3) : le paragraphe d'état pourra dire, aux scénarios 2, 4 et 6, une
   baisse de 2,9 à 3,7 % et +0,15 à +0,36 point de solde moyen ; aux
   scénarios 3 et 5, rien en 2030, 1,7 et 2,2 % en 2070, +0,05 et +0,11
   point ; une survie qui déplace le rapport de masses de moins de 1 %, et
   qui fait la différence avec la page.
4. *Léger, à déclarer sans le faire* (la coupe du 14 octobre), avec la
   limite du point 3 : les poids de chaque année (note « la prémisse du
   déficit », point 2, que les « Ce qui reste » suivants n'avaient pas
   repris) et les droits acquis au diviseur de la bascule, que la règle
   laisse hors du rapport. Avec la revalorisation des pensions servies,
   l'écart qu'ils laissent du script à la page, la survie comptée, tient en
   moins de deux centièmes de point de solde moyen, sans que la mesure les
   sépare.
5. *Au propriétaire* : les départs qui suivent l'espérance de vie.
