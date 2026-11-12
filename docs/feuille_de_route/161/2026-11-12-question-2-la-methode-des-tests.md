# Question 2 : la méthode des tests du moteur Python — une façade au pont pour un tiers, le reste à la main, par fréquence

**La recommandation.** Une voie mixte, et non la voie (b) telle que
l'inventaire la formule. Faire de `Simulateur.simuler` et de
`ScenarioActuel.calculer` des clients du pont ne libère presque rien : les
tests bâtissent d'abord leur carrière en Python, et les deux tiers
n'entrent pas par là. Une façade plus large — `simuler`, `calculer`,
`reversion` et les bâtisseurs de carrière, huit entrées servies par le
pont sous leurs noms Python — fait passer, tests inchangés, les 530 tests
des deux fichiers instruits, sans rien coûter en durée ; mais sur la suite
entière elle ne libère du moteur Python que 672 des 1 958 tests qui
n'éprouvent que lui, 34 %. Le reste appelle lui-même une fonction du
droit, et se porte à la main : par fréquence, quarante entrées de plus au
pont en couvrent les deux tiers. Compter 11 à 16 sessions pour le lot D,
contre 13 à 28 par la seule voie (a). Le propriétaire tranche ; rien n'est
mis en œuvre ici.

**La demande.** L'inventaire du 9 novembre
(`2026-11-09-l-inventaire-des-retraits.md`) laisse au propriétaire le
choix de la méthode pour les tests qui n'éprouvent que le moteur Python :
(a) les porter au pont fichier par fichier ; (b) faire de `Simulateur` et
de `ScenarioActuel.calculer` des clients du pont, les tests inchangés,
sans savoir si le pont rend tout ce qu'ils lisent. Il proposait
d'instruire d'abord sur `tests/test_simulateur.py` et
`tests/test_reversion.py`. Cette session l'a fait, puis a rejoué la suite
entière pour mesurer l'extrapolation au lieu de la déduire.

**La méthode.** Tout s'est fait dans une copie du dépôt hors de lui, sur
cbd46ee ; les scripts et l'essai ne sont pas commités, et l'arbre est
resté intact. Trois traceurs : ce que le code des tests appelle dans le
paquet et lit de ses objets, test par test ; les fonctions des fichiers de
règles que chaque test exécute, et s'il passe par le pont ; les entrées
directes des tests dans les jumeaux, sous l'essai. « Fichier de règles »
veut dire ici `droit/`, `moteur/`, `echeancier.py`,
`scenarios/notionnel.py`, `journal.py` et `pilote.py`, dont la fabrique
du paquet n'appelle presque rien ; les fichiers mêlés de chargeurs et de
types (`carriere.py`, `simulateur.py`, `scenarios/actuel.py`…) ne comptent
pas. Un test « n'éprouve que le Python » s'il exécute une fonction de ces
fichiers sans jamais demander au pont.

L'essai de la voie (b) : quarante lignes de plus dans `pont.mjs`, qui
écrivent en données un objet du portage tel qu'il est, et un greffon de
pytest de deux cents lignes, qui remplace huit entrées du Python par un
client du pont — `Simulateur.simuler`, `ScenarioActuel.calculer`,
`droit.reversion.reversion`, `Simulateur.carriere_simple`,
`carriere_parcours` et `carriere_releve`, `Carriere.depuis_profil` et
`depuis_parcours` — et relit ce que le portage rend sous les types du
Python, d'après leurs annotations. Le lecteur est tolérant : il note les
écarts de champs au lieu de s'arrêter, ce que le pont ne fait pas.

## Ce qui est mesuré sur les deux fichiers

**Ce que les tests appellent.** 691 tests : 530 n'éprouvent que le Python
(287 et 243), 37 sont des confrontations, 124 n'exécutent aucune règle.
L'inventaire en comptait 434, à dix lignes d'un jumeau. Des 530 :

| le test entre par | tests |
|---|---:|
| `Simulateur.simuler` | 66 |
| `ScenarioActuel.calculer` | 99 |
| `reversion()`, appelée directement | 208 |
| aucune des trois : des fonctions du droit, une à une | 157 |

Avant d'y entrer, ils bâtissent leur carrière en Python :
`Carriere.depuis_profil` (207 tests), `Simulateur.carriere_simple` (175),
`Carriere.depuis_parcours` (30), `carriere_parcours` (15),
`carriere_releve` (6). En tout, le code des deux fichiers appelle 130
fonctions du paquet. Aucun test n'y remplace une fonction par
`monkeypatch`.

**Ce qu'ils lisent du résultat.** 395 des 530 lisent un type du
résultat : 24 classes, 130 champs, et 26 attributs calculés — des
propriétés ou des méthodes —, que 25 tests seulement lisent. Les plus
lues : `ReversionRegime` (34 champs, 207 tests), `ResultatActuel` (12
champs, 123 tests), `Comparaison` (8 champs et 9 attributs calculés, 66
tests), `PensionRegime` (4 champs, 57 tests), `ResultatNotionnel` (11
champs, 49 tests), `GarantieVieillesse` (16 attributs, 8 tests). À côté du
résultat, ils lisent des données qui restent en Python : le catalogue, les
séries, les tables de la réversion.

**Ce que le pont rend aujourd'hui, et l'écart.**

- *La réversion* : `reversion.reversion` rend le type entier, relu
  strictement. Il suffit tel quel : `test_reversion.py` passe entier, 354
  tests, la seule `reversion()` branchée sur le pont, sans y toucher.
- *Le scénario 1* : `scenario_actuel.calculer` rend 10 des 23 champs de
  `ResultatActuel`, 4 des 15 de `PensionRegime`, 6 des 7 de
  `AvantageApplique`. Les tests en lisent 12, 4 et 5 : il manque
  `age_ouverture_opposable`, `minimum_applique`, `total_contributif`,
  `fiabilite` et `libelle`, que 15 tests lisent.
- *La comparaison* : rien ne simule une carrière que le Python a bâtie
  pour en rendre la comparaison entière. `pont.simulations` part d'une
  requête et rend `dictionnaire()` ; `pont.carrieres` part des options et
  rend une dizaine d'indicateurs. Les comptes, la garantie et les droits
  acquis que les tests lisent n'y sont pas.
- *Les carrières* : `carriere_simple` et `carriere_releve` y sont ;
  `carriere_parcours` non.

Les objets du portage, eux, portent presque partout les noms du Python :
l'écrivain générique de l'essai a suffi. Ce que le lecteur tolérant a
relevé, et qu'une lecture stricte aurait à régler : cinq classes aux
champs en casse de chameau (`AnneeComparee`, `FicheDePaie`,
`RemunerationActif`, `ExploitantAgricole`, `MajorationProportionnelle`, 22
champs) ; des champs absents quand ils ne s'appliquent pas (dix de
`PensionRegime`, trois d'`AvantageApplique`, `minimum_ecrete`) ; une
quarantaine de valeurs que le portage tient en champs et le Python en
propriétés (`pension_totale`, `servie`, `nulle`, `ecart`…) ; le journal,
qui pèse 114 Mo écrit tel quel pour une seule carrière, ses entrées tenant
des tables ; le type d'une erreur, que le pont ne rend pas.

**L'essai.**

| entrées servies par le pont | verts | les 530 qui n'exécutent plus aucune règle Python |
|---|---:|---:|
| aucune | 691 | 0 |
| `simuler` et `calculer` seuls | 681 | 7 |
| les huit | 679 | 339 |

Les 530 passent tous, sous les huit entrées. Les douze rouges sont hors
d'eux : dix lisent le journal, que l'essai écarte ; deux attendent un
`KeyError` pour une affiliation inconnue, et reçoivent l'erreur du pont.
Le portage a servi 2 390 appels et en a refusé 8, dont 6 que les tests
attendaient.

La durée ne bouge pas : 34,1 s puis 33,0 s en série, 13,7 s puis 13,2 s
sur quatre cœurs. Un pont reste ouvert par processus.

Avec `simuler` et `calculer` seuls, 7 tests sur 530 sont libérés : les
bâtisseurs de carrière exécutent des règles, et tous les tests y passent.
La voie (b) de l'inventaire, prise à la lettre, ne libère donc rien.

Des 191 qui exécutent encore des règles sous les huit entrées, 139
appellent eux-mêmes une fonction du droit — 50 fonctions, dont 8 sont déjà
au pont : `liquider.maximum_des_pensions` (33 tests),
`liquider.abattement_points` (22), `releve.construire` (17) — et 52 y
viennent par une méthode d'un type ou d'une table
(`Carriere.trimestres_retenus`, `CarriereLongue.cotises_reputes`, 22
chacune).

## Ce qui est mesuré sur la suite entière

La suite, 8 173 tests, a tourné deux fois sous le traceur léger : telle
quelle, en 20 min 25 s ; les huit entrées servies par le pont, en
20 min 40 s.

2 593 tests, dans 143 fichiers, exécutent une fonction des fichiers de
règles ; 635, dans 70 fichiers, passent aussi par le pont ; 1 958, dans
115 fichiers, n'éprouvent que le Python. L'inventaire disait 2 083, 608 et
1 475 : il comptait à dix lignes d'un jumeau, sur 80a32b9. Des 1 958,
1 414 exécutent plus de dix fonctions de règles, et 379 trois au plus,
dont 169 le seul `preparer`.

Sous l'essai, les 1 958 se partagent ainsi, selon l'entrée de la façade
que le test exécute :

| entrée exécutée | tests | libérés | méthodes de classes seules | règles encore | rouges |
|---|---:|---:|---:|---:|---:|
| `simuler` | 168 | 75 | 34 | 35 | 24 |
| `calculer` | 534 | 291 | 1 | 203 | 39 |
| `reversion` | 208 | 208 | 0 | 0 | 0 |
| un bâtisseur seul | 609 | 97 | 0 | 507 | 5 |
| aucune | 439 | 1 | 71 | 365 | 2 |
| ensemble | 1 958 | 672 | 106 | 1 110 | 70 |

« Libéré » : vert, et plus aucune fonction des fichiers de règles
exécutée. « Méthodes de classes seules » : il n'en reste que des méthodes,
celles d'`Indexation` pour 44 tests, des propriétés des résultats pour
les autres. 54 fichiers sur 115 ont au moins un test libéré, 11 le sont
en entier (65 tests), 56 n'en ont aucun (393 tests). Les deux fichiers
instruits étaient donc les plus favorables : 64 % de libérés, contre 34 %
sur la suite, et les 208 tests de la réversion y pèsent près du tiers du
total.

Des 70 rouges, cinquante-cinq tiennent à l'essai lui-même : 31 lisent
une propriété d'un objet que son lecteur n'a pas su typer, une quinzaine
un champ en casse de chameau, 4 le journal, et 5 donnent à
`depuis_profil` une affiliation que le client de l'essai vérifiait à
tort. Les quinze autres n'ont pas été lus un à un. Six des 1 958 tests se
servent de `monkeypatch`, aucun parmi les libérés.

**Ce qui reste à porter à la main.** Sous l'essai, 1 247 tests non
libérés ont été tracés (tous, hors `test_affirmations.py`, qui tient au
coût). 933 appellent eux-mêmes une fonction des fichiers de règles : 232
entrées distinctes, 133 fonctions et 99 méthodes, dont 14 sont au pont.
110 de ces tests n'ont besoin de rien de plus. En ajoutant les entrées
par fréquence :

| entrées ajoutées au pont | tests dont toutes les entrées y sont |
|---:|---:|
| 0 | 110 |
| 10 | 348 |
| 20 | 465 |
| 40 | 641 |
| 80 | 781 |
| 218 | 933 |

Les 138 dernières entrées ne servent que 152 tests. 519 tests n'appellent
qu'une fonction, 262 deux. Par fichier, la médiane est de deux entrées à
ajouter ; `test_simulateur.py` en demande 46, `test_liquidation.py` 28,
`test_capitalisation.py` 20. Les 314 autres tests n'entrent dans aucune
règle eux-mêmes : ils y viennent par `Simulateur.echeancier` (52),
`Carriere.depuis_releve` (43), que l'essai n'a pas servi,
`revalorisation.faire_vivre` (17), ou par des méthodes de types.

## Ce qui est déduit

**La valeur des tests sous la façade.** Un test qui passe par elle éprouve
le moteur JavaScript contre la valeur que la source donne — le décret,
l'exemple, le calcul posé —, mot pour mot celle qu'il éprouvait sur le
Python. Les confrontations ne le font pas : elles disent que deux moteurs
s'accordent, et partent avec le jumeau ; les témoins, que le portage
calcule, disent ce qui a bougé. Ces tests gardent donc ce que rien
d'autre ne garde, avec `test_oracle.py` et `tests/js/`, et la voie (a)
n'y ajoute rien : elle récrit la même assertion, au risque de
l'affaiblir, sans qu'on puisse la voir rouge pour la bonne raison. Ce
qu'ils cessent d'éprouver, ce sont les règles Python, qui partent. Les
778 tests libérés ou réduits à des méthodes sont verts au premier essai :
le portage tient déjà chacune de leurs valeurs attendues.

**Ce que la façade laisse en Python.** Les types du résultat, comme
contrat du pont : une vingtaine de classes de plus que la liste de la
note 0006. Leurs attributs calculés sont de petites règles en double ; le
portage en tient déjà la plupart en champs, et le type Python peut les
lire au lieu de les calculer. Les méthodes à argument de `Comparaison`
(`variation`, `en_euros_constants`) se portent à la main, pour une
dizaine de tests.

**Les sessions.** Le rythme vient des notes de l'étape 6 :
`test_oracle.py`, 277 tests et 42 lectures du pont en quatre sessions,
soit 10 à 16 entrées et 70 tests par session ; un portage mécanique, 562
tests du site en une session.

| voie | ce qu'elle fait | sessions |
|---|---|---:|
| (a) seule | 1 958 tests récrits, quelque 230 entrées au pont | 13 à 28 |
| (b) de l'inventaire | 366 tests libérés au plus, par `simuler` ou `calculer`, les bâtisseurs servis aussi | ne suffit pas |
| mixte | la façade, lue strictement, le journal et les erreurs compris (2) ; ses fichiers basculés et ses rouges réglés (1 à 2) ; les 40 entrées les plus appelées (3 à 4) ; la traîne, 650 tests (5 à 8) | 11 à 16 |

L'inventaire donnait 8 à 15 : la voie courte qu'il espérait n'existe pas,
et la suite compte un tiers de tests de plus qu'il ne disait. La traîne
est le poste qui se discute : 138 entrées pour 152 tests, souvent des
fonctions privées, dont l'essai JavaScript serait mieux dans `tests/js/`.

**L'ordre proposé.** La façade d'abord, dans un module à elle tant que le
jumeau vit : l'essai remplaçait les entrées du Python partout, et les
confrontations y comparaient le portage à lui-même. Un client refuse ce
qu'il ne sait pas transmettre — un moteur modifié, une série passée en
argument — au lieu de l'ignorer. Un test tient la liste, décroissante,
des fichiers de tests qui exécutent encore une règle Python. Puis les
entrées par fréquence, `releve.construire`, `ConstructeurCompte`,
`liquider.abattement_points` en tête.

## Ce qui n'est pas vérifié

- La façade à côté du jumeau : l'essai ne l'a pas bâtie, et un test
  basculé changerait au moins son import ou sa fixture.
- Les verts trompeurs : un client qui ignore un état que le test a posé
  en Python. L'essai ignore la série passée à `depuis_profil` et tout
  moteur qui n'est pas celui du simulateur ; aucun test libéré n'emploie
  `monkeypatch`, mais une table modifiée autrement n'a pas été cherchée.
- Quinze des 70 rouges, les 45 confrontations et les 56 autres tests
  que l'essai rougit, non lus.
- Le coût de la lecture stricte, estimé des écarts relevés, non essayé.
- Les 314 tests sans entrée directe, et ce que deux entrées de plus
  (`echeancier`, `depuis_releve`) en libéreraient.
- Si les tests de la traîne doublent des essais de `tests/js/`.
- Les nombres de sessions, tous déduits.

**Ce qui ne change pas.** Aucun code, aucun test, aucune donnée, aucun
script, aucune garde. Le bloc « Reprise » de l'action n'est pas récrit :
la session d'orchestration le tient.

**Tests.** Ceux de la feuille de route (`tests/test_prose.py`) et la
prose vérifiée. Dans la copie, la suite telle quelle : 8 089 verts, 74
sautés, 10 rouges, qui tiennent à la copie — pas de `.git`, `pont.mjs`
retouché pour l'essai.
