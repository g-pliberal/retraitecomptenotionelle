# L'indexation au portage : les règles d'indexation de `test_moteur.py` éprouvées sur le module du site

Action 161, quatrième vague, après
`2026-11-16-la-quatrieme-vague-a-mi-chemin.md`. Aucune règle, aucune donnée,
aucun témoin n'a bougé. `test_moteur.py` reste dans `FICHIERS` : il garde
53 tests sur 77.

## Ce qui est fait

- **`tests/js/indexation.test.js`**, neuf, que `test_web.py` lance avec les
  autres essais de node : les 25 tests de `test_moteur.py` qui bâtissaient
  `Indexation` à la main sous un mode, un lissage ou un plancher passent sur
  le module du portage (`moteur/js/indexation.js`) et sur `DonneesMacro` du
  site. Le minimum, la médiane et la moyenne des trois taux ; la règle
  littérale et sa variante nominale ; les arrêtés de revalorisation et leur
  composition ; la masse salariale, la plus généreuse, certifiée depuis
  1950 ; le lissage, moyenne géométrique de sa fenêtre, tronquée au début des
  séries, neutre à un an, et le plancher posé après lui ; le coefficient qui
  ne revalorise pas l'année du versement ; le SMIC annuel et la durée légale.
  Les attendus sont des identités de la règle, des ordres entre règles sur
  1941-2025, ou les niveaux que l'INSEE publie, comme dans le Python.
- `test_moteur.py` n'importe plus `Indexation` ni `ModeIndexation`.

## Ce qui reste de `test_moteur.py`

Par module, une étape chacun : `Convertisseur` (16 appels) et `AgeReference`
(6), par un essai de node ou par `pont.droit` (`conversion.coefficient.diviseur`,
`age_reference.age`) ; `fusionner` (7), par `fusion.fusionner` du pont ou
`tests/js/fusion.test.js` ; le profil de rémunération (`profil_salaire`,
`_facteur_secteur`) ; les cas types et le mois, qui lisent le simulateur, à
la façade. Le salaire moyen refait de l'INSEE
(`test_le_salaire_moyen_refait_les_niveaux_que_l_insee_publie`) lit
`carriere.ancrage_salaire_moyen`, que le pont sert.

**Tests.** `node --test tests/js/indexation.test.js` (25),
`test_moteur.py` (53) et `test_fichiers_sur_le_moteur_python.py` : verts ;
`python -m pytest -m rapide` avant l'envoi.
