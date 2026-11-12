# La façade sert les tables du moteur, et deux fichiers de tests y passent : 513 tests sur 691 éprouvent le portage, 178 restent marqués sur le moteur Python

`tests/test_simulateur.py` et `tests/test_reversion.py` importent leurs
entrées de la façade. 513 de leurs 691 tests font calculer le portage ; 178
gardent le moteur Python, sous une marque et sa raison. Les deux fichiers
restent dans `FICHIERS` : ils importent encore des règles Python pour ces
tests-là. Aucune règle, aucune donnée, aucun témoin n'a bougé.

**La consigne.** « Ce qui reste », 1 et 2, de
`2026-11-12-la-facade-des-tests.md` : servir les tables du moteur, puis
basculer les deux fichiers instruits, sans supprimer ni affaiblir un test.

## Ce que la mesure a corrigé

La note d'avant comptait 218 refus « sur une table ou un attribut du
moteur ». Relevés un à un, par celui qui lit la table :

| qui lit la table | refus |
|---|---:|
| le test lui-même (`scenario_actuel.reversions.minimum(2025)`) | 137 |
| une règle du moteur Python que le test appelle avec le moteur de la façade (`liquider.…(moteur, …)`, `ouvrir.…`, `revalorisation.majorations_forfaitaires`) | 81 |

Servir une table ne libère que les premiers. Les seconds appellent une règle
Python : lui servir les tables du portage les ferait verdir sans que le
portage soit éprouvé. Ils attendent que la règle elle-même soit servie
(« Les entrées par fréquence »).

## Ce qui est fait

**L'entrée des tables.** `pont.table_du_moteur` et, dans `pont.mjs`,
l'entrée `scenario_actuel.table` : le portage appelle la méthode de sa
table, sous les paramètres du simulateur. Dix-huit méthodes de neuf tables
sont déclarées (`pont.TABLES_DE_LA_FACADE`), celles que les tests des deux
fichiers appellent ; leurs arguments ont le même ordre des deux côtés, relu
méthode par méthode. Ce qu'une méthode rend revient sous le type que la
méthode du jumeau annonce, lu strictement. Les arguments se lient par la
signature du jumeau. Trois arguments passent par une marque : les séries du
simulateur ; une période de son catalogue, par son rang dans son régime,
l'année de début vérifiée par le portage ; une date, en texte. Une méthode
non déclarée, une méthode privée, une période qui n'est pas du catalogue
sont refusées.

**Une règle Python ne lit pas le moteur de la façade.** `ScenarioActuel`
regarde qui lit : un module de `retraite_notionnelle` est refusé, avec le
nom de la règle.

**La marque `sur_le_moteur_python`.** Un test marqué garde le moteur Python,
inchangé : le temps de ce test, `Simulateur`, `Carriere` et `reversion` de
son fichier redeviennent ceux du Python (`facade.entrees_du_test`), et son
simulateur aussi (`facade.simulateur_du_test`, qui tient un simulateur par
fichier, par moteur et par paramètres). Les fixtures des deux fichiers y
passent ; elles ne sont plus de portée module.

**Le compte tenu par un test.**
`tests/test_fichiers_sur_le_moteur_python.py` tient `RESTES`, le nombre de
fonctions de test marquées de chaque fichier basculé, qui ne fait que
décroître, et vérifie qu'un test sans marque n'entre pas dans le moteur
Python : ni par un import à lui, ni par un nom que son fichier importe, ni
par une aide ou une fixture.

## Ce qui est mesuré

| fichier | tests | par la façade | marqués | fonctions marquées |
|---|---:|---:|---:|---:|
| `test_simulateur.py` | 337 | 208 | 129 | 121 sur 302 |
| `test_reversion.py` | 354 | 305 | 49 | 6 sur 151 |

**Pourquoi 178 tests restent**, par fonction de test, 127 en tout, d'après
la raison de leur marque :

| raison | fonctions |
|---|---:|
| une règle de `droit/`, appelée par le test ou par une aide du fichier (`liquider` 48, `ouvrir` 15, `releve` 9, `completer` 4, `liquidation` 2, `acquerir`, `maximum_des_pensions`, `mois_de_mariage`, `_cumuler`…) | 86 |
| une règle du simulateur (`constructeur_employeur` 9, `indexation` 3, `proposition`, `scenario_notionnel`, `mortalite`…) | 19 |
| une table que le test bâtit lui-même, ou une méthode privée d'une table (`ValeursPoint` 5, `_en_vigueur` 4, cinq autres) | 14 |
| une règle de `carriere.py` ou de `simulateur.py` (`salaire_moyen_annuel` 3, `niveau_pour_pension` 2, `Carriere.prolongee`) | 6 |
| `revalorisation.majorations_forfaitaires`, qui lit le moteur | 2 |

`Simulateur.echeancier` et le contenu d'une liquidation au journal, que la
consigne nommait, ne sont lus par aucun test des deux fichiers.

**Contre le jumeau.** 32 appels, un au moins par méthode déclarée, sous les
réglages de référence et sous les conventions du COR : la même valeur au
bit près, sous les mêmes types (`tests/test_facade_jumeau.py`).

**La durée.** Inchangée : `test_simulateur.py` 12,4 s avant et après,
`test_reversion.py` 8,7 s puis 9,0 s ; en série, 33 s puis 29 s, et 16 s
puis 16 s.

## Trouvé en chemin

- **`FICHIERS` ne dit pas l'avancée d'un fichier.** Un fichier n'en sort
  qu'à son dernier import du moteur Python : les deux fichiers y restent
  avec 74 % de leurs tests sur le portage. `RESTES` le dit à sa place.
- **Une règle sur un type de données ne se voit pas.**
  `carriere.prolongee(…)` est une règle Python portée par `Carriere`, que le
  pont échange : ni la liste ni le compte ne la voient dans le code. Un test
  la tient ici par sa marque ; d'autres fichiers peuvent en cacher.
- **`grilles.forfait`** prend une fonction en argument (l'indice de
  salaire) : non servie, un test.

## Ce qui reste

1. **Les règles de `droit/` par la façade**, `liquider` et `ouvrir` en
   tête : 63 des 127 fonctions marquées. `pont.droit` en sert déjà
   plusieurs ; un module `liquider` de la façade, lié par la signature du
   jumeau, les libérerait.
2. **Les autres fichiers.** Par fichier : ses imports, la fixture
   `entrees_du_test`, ses simulateurs par `facade.simulateur_du_test`, la
   marque sur ce qui reste, son compte dans `RESTES`.
3. **Les règles du simulateur** (`constructeur_employeur`, `indexation`,
   `proposition`…) et `releve.construire`.

## Ce qui n'est pas vérifié

- La façade des tables sur d'autres fichiers, et sur d'autres méthodes que
  les dix-huit déclarées.
- Que chaque test sans marque appelle bien le portage : le compte dit
  qu'il n'entre pas dans le moteur Python, non qu'il passe par le pont.
- Les 178 tests marqués un à un : ceux que la mesure voyait rouges ou
  entrants sont marqués ; aucun n'a été essayé sans sa marque après coup.
- La suite complète, que GitHub lance.

**Ce qui ne change pas.** Aucune règle, aucune donnée, aucun témoin, aucun
script, aucune garde. Le reste du pont : les ajouts sont en un bloc à la fin
de `pont.py` et un bloc de `pont.mjs`.

**Tests.** `tests/test_facade.py`, 54 tests, les neuf nouveaux vus rouges ;
`tests/test_facade_jumeau.py`, en entier ;
`tests/test_fichiers_sur_le_moteur_python.py` ; les deux fichiers en entier,
aussi sous `PRESOMPTIONS_DECALEES=1` (665 verts et 26 sautés, comme avant) ;
la suite rapide.
