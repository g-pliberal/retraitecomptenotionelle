# La réversion à la façade : le maximum des pensions, la durée d'un mariage et deux méthodes de la table des réversions servis par le portage

Cinquième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-tables-a-la-facade.md`, « Ce qui reste », 1. Deux fonctions
de test de `tests/test_reversion.py` quittent la marque
`sur_le_moteur_python` (le barème du maximum, trente-trois cas, et la durée
d'un mariage) : il en reste 4 dans ce fichier, contre 6. Aucune règle, aucune
donnée, aucun témoin n'a bougé.

## Ce qui est fait

**Deux règles de plus** : `liquider.maximum_des_pensions` et
`reversion.mois_de_mariage` rejoignent `pont.REGLES_DE_LA_FACADE` (trente-trois
règles servies) ; `pont.mjs` ajoute le module `reversion` à ceux du droit.

**Deux méthodes de table de plus** : `reversions.fiche_du_regime` et
`reversions.version`. La fiche revient en dictionnaire, et repasse telle
quelle à `version`, que le portage lit en objet : elle n'a que des valeurs
JSON.

**Un nom à part.** `reversion` est, dans la façade, l'entrée de la
réversion ; les règles du module se demandent sous `regles_de_la_reversion`, dont le
jumeau, pour un test marqué, est le module Python (`facade.JUMEAUX`).

## Ce qui est mesuré

| `test_reversion.py` | avant | après |
|---|---:|---:|
| fonctions de test marquées | 6 | 4 |

**Contre le jumeau.** `tests/test_facade_jumeau.py` confronte neuf appels de
plus : deux fiches (dont un régime sans fiche), deux versions (le régime
général en 1985, l'État en 2026), trois maxima (1965, 2026, un régime sans
maximum), deux durées de mariage (dont une négative, ramenée à zéro).

**Les tests.** Trois tests neufs dans `tests/test_facade.py`, vus rouges
avant le code : la version de 2026 du régime général à 54 % (circulaire Cnav
n° 3/95, § 13), le maximum de 2026, 24 030 € (50 % du plafond, R. 351-29), et
la durée d'un mariage, 116 mois (R. 353-4). `-m rapide`, `test_facade.py`,
`test_facade_jumeau.py`, `test_reversion.py`, `test_pont.py`,
`test_oracle.py` et `test_fichiers_sur_le_moteur_python.py` : verts.
L'exemple d'une méthode refusée passe de `fiche_du_regime`, désormais
servie, à `fiche`.

## Ce qui reste

1. Les cotisations du relevé (`droits.cotisations`) et le constructeur du
   compte, pour le test de l'exercice 1952 et ses voisins marqués
   `Simulateur.constructeur_employeur` (`test_simulateur.py`).
2. Les quatre tests marqués de `test_reversion.py` : `droit.reversion._cumuler`
   (règle privée), `revalorisation._majorations_de_la_pension` (deux) et
   `droit.liquidation` ; chacun demande une entrée de plus, non instruite.
3. Puis les autres fichiers de tests qui lisent le relevé
   (`test_droit.py`, `test_liquidation.py`, `test_cultes.py`,
   `test_bonifications_emplois.py`…), et les règles du simulateur ;
   `completer.points_rco_de_chef` comme le dit la note précédente.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
