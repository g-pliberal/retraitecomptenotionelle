# Les tables à la façade : un dictionnaire que le portage lit en `Map` passe en table, et trois règles de plus sont servies

Quatrième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-l-avpf-a-la-facade.md`, « Ce qui reste », 1. Quatre fonctions de
test de `tests/test_simulateur.py` quittent la marque
`sur_le_moteur_python` : il en reste 49 dans ce fichier, contre 53. Aucune
règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

**Trois règles de plus** : `liquider.repartir_les_annees`,
`liquider.majorer_les_points_de_1952_a_1972` et
`liquider.majoration_des_points_de_1952_a_1972_d_avant_2026` rejoignent
`pont.REGLES_DE_LA_FACADE` (trente et une règles servies).

**Une table passe en `Map`.** `pont.TABLES_DES_REGLES` déclare, règle par
règle, les arguments que le portage lit en `Map` : les durées et les minimums
de la répartition, les points annuels de la majoration. La façade les passe
en `pont.Table`, ses entrées dans l'ordre ; le pont les écrit sous la marque
`{"@": "table", entrees}`, et `argumentDeLaFacade` en refait une `Map`, les
clés sous leur type (une année reste un entier). `None`, que le Python
remplace par une table vide, passe en table vide. Une table dont une clé ou
une valeur n'est pas simple est refusée (`NonTransmissible`). Ce que la règle
rend en `Map` revenait déjà en dictionnaire (`telQuel`, `lu_strictement`).

**Des couples passent en liste.** Une suite de couples de valeurs simples —
les cotisations `(année, montant)` de la majoration d'avant 2026 — passe en
liste de listes, que le portage parcourt telle quelle.

**Le test des signatures** lit désormais un défaut écrit `new Map()` (son
expression régulière admettait mal les parenthèses) : il vaut le `None` d'un
argument déclaré en table ; `[]` vaut le `()` du Python.

## Ce qui est mesuré

| `test_simulateur.py` | avant | après |
|---|---:|---:|
| fonctions de test marquées | 53 | 49 |

**Contre le jumeau.** `tests/test_facade_jumeau.py` confronte six appels de
plus, sous les réglages de référence et les conventions du COR : deux
répartitions (minimums et priorité posés, durée nulle), deux majorations par
année, deux d'un seul taux.

**Les tests.** Trois tests neufs dans `tests/test_facade.py`, vus rouges
avant le code (la façade ne servait pas ces règles) : l'exemple de la MSA
(R. 173-3-2 : 6 et 19 ans, puis 13 et 6), les points de chef de 1960 et 1961
majorés de 5 % (R. 732-67 : 21 et 16 points), la majoration d'avant 2026 de
39,42 € (D. 732-77) ; et la table mal formée, refusée. `-m rapide` (5 101
tests), `test_facade.py`, `test_facade_jumeau.py`, `test_oracle.py`,
`test_pont.py`, `test_fichiers_sur_le_moteur_python.py` et les quatre tests
démarqués : verts.

## Ce qui reste

1. `liquider.maximum_des_pensions` et `reversion.mois_de_mariage`
   (`test_reversion.py`) : le premier lit aussi deux méthodes de la table des
   réversions que la façade ne sert pas, le second se heurte au nom
   `reversion`, que la façade donne déjà à l'entrée de la réversion.
2. Les cotisations du relevé (`droits.cotisations`) et le constructeur du
   compte, pour le test de l'exercice 1952 et ses voisins marqués
   `Simulateur.constructeur_employeur`.
3. Puis les autres fichiers de tests qui lisent le relevé
   (`test_droit.py`, `test_liquidation.py`, `test_cultes.py`,
   `test_bonifications_emplois.py`…), et les règles du simulateur.
   `completer.points_rco_de_chef`, que lit `test_minima_agricoles.py`,
   reçoit les droits du relevé entiers, dont des tables (`points_acquis`,
   `gratuits`) : il passera comme les durées, refaites par le portage du
   relevé de leur carrière, quand ce fichier basculera.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
