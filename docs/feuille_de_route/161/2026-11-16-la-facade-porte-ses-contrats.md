# La façade porte ses contrats : signatures et types rendus sans le jumeau

Action 161, étape 2 du plan de `2026-11-16-l-inventaire-du-retrait-des-regles.md`.
Aucune règle n'a changé : le paquet et les témoins refaits sont identiques à
l'octet.

## Ce qui a bougé

**Les contrats.** `tests/contrats_de_la_facade.py` porte, sans corps, la
signature et le type rendu de chaque entrée que la façade sert : les 106
règles du droit (`REGLES_DE_LA_FACADE`), les 61 méthodes de tables, les
méthodes des quatre constructeurs du compte, les six de la mortalité, et la
signature seule de sept entrées (`scenario_actuel.calculer`,
`reversion.reversion`, `releve.construire`, les quatre `Carriere.depuis_*`),
dont le pont lit le rendu. Le fichier a été écrit une fois, par un script
jetable, depuis le jumeau ; il s'entretient désormais à la main. Les
annotations des arguments n'y sont pas : la façade ne lit que leurs noms,
leur genre et leurs valeurs par défaut. Une carrière s'y rend sous la
carrière nue, que le pont relit en carrière du moteur Python tant qu'il la
bâtit (`lu_strictement`, par `issubclass`) : même résultat.

**La façade.** Ses quatorze lectures (`inspect.signature`,
`typing.get_type_hints`) lisent ces contrats. `_type_de_la_table`, qui
bâtissait un simulateur Python pour lire le type d'une table, et
`_type_rendu` sont partis. `tests/test_facade_jumeau.py` lit le type rendu
d'une règle dans son contrat.

**Dix-sept types de plus sous `types_du_pont/`**, que rendent des règles
servies : `DureesDesCultes`, `EligibleMinimum`, `PrestationRafp`,
`PensionMajoree`, `MajorationEnfants` et `TrimestresEnfant`,
`PlancherDeLaSubstitution`, `Radiation` et `Recul` (avec
`FICHE_DE_LA_LIMITE`), `DepartParentTroisEnfants`, `Progressive`,
`RevenuDesPoints`, `Depart` (avec `MOTIF_DEPART`), `ConversionPoint`,
`DerogationActive`, `TrimestresAccordes` sous `droit.py`, `LigneRelevee`
sous `carriere.py`. L'étape 1 ne les avait pas vus : le pont ne les nomme
pas, la façade les lui passe. Les fichiers de règles les réimportent, comme
à l'étape 1. Trois fiches citaient l'un d'eux à son ancien fichier
(`minimum_contributif`, `minimum_contributif_international`,
`versement_forfaitaire_unique`) : elles le citent sous `types_du_pont/`, et
la dernière ne cite plus `PensionServie.date_effet`, un champ, que
`test_carte.py` ne trouvait que par le `def date_effet` de `Depart`.

## Ce que la façade lit encore du jumeau

Ni signature ni type rendu, mais : les constantes d'un module et la
présence d'un nom (`Regles.__getattr__`, `_Module.__getattr__`, par
`hasattr` et `getattr` sur le module) ; les types que `_Liquidation`,
`_Progressive`, `_Echeanciers` et `_Journaux` exposent ; la classe des
règles de `Carriere`, dont hérite la sienne ; `JUMEAUX`, que reprend un
test resté sur le moteur Python. Les constantes sont l'affaire de l'étape 4
ou de la suppression ; le reste part avec les fichiers de règles et leurs
tests. `Foyer.servie_avec`, que les deux notes d'avant renvoyaient ici, est
une méthode d'un type qui reste : elle ne bloque rien.

## Tests

`tests/test_contrats_de_la_facade.py` : les contrats, chargés seuls dans un
processus neuf, ne chargent aucun fichier de règles ; chaque lecture de
signature de la façade lit un contrat, ce qui était rouge avant le
changement de la façade. `tests/test_facade_jumeau.py` confronte chaque
contrat à son jumeau, y compris les tables qu'un droit contrefactuel
recouvre : ces confrontations partent avec lui, et la liste des fichiers sur
le moteur Python le nomme déjà, quand un fichier neuf n'y entre pas.
`tests/test_types_du_pont.py` compte les dix-sept types, vu rouge (17
échecs) avant leur déplacement. Zone : `test_facade`, `test_facade_jumeau`,
`test_types_du_pont`, `test_contrats_de_la_facade`, `test_jumeaux`, 604
réussis ; `test_carte`, 17. Suite rapide : 5 676 réussis.
