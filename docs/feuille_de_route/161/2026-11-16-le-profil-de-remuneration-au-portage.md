# Le profil de rémunération au portage : les tests de `profil_salaire` et `_facteur_secteur` de `test_moteur.py` éprouvés sur le module du site

Action 161, quatrième vague, après `2026-11-16-la-fusion-au-portage.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé. `test_moteur.py` reste
dans `FICHIERS` : il garde 23 tests sur 28.

## Ce qui est fait

- **`tests/js/profil-salaire.test.js`**, neuf, tient sur `moteur/donnees.json`
  les quatre tests du profil : la pente qui suit la génération (×1,25 pour
  1940, ×1,38 pour 1960, le profil plat à un) ; les pentes de l'INSEE à
  l'année de la forme (×1,30, ×1,86) ; le facteur de secteur, à 1,38 pour
  les IEG, 0,93 pour la SNCF et à un partout ailleurs ; l'interpolation posée
  à la main, 0.9566764705882352. Les tolérances sont celles du Python.
- `facteurSecteur` est exporté de `moteur/js/carriere.js` pour être éprouvé
  seul ; rien d'autre n'y change. Le test, lancé avant l'export, échouait sur
  l'import.
- **La confrontation des deux jumeaux au bit près**
  (`test_les_deux_jumeaux_lisent_le_meme_profil_au_bit_pres`) passe telle
  quelle dans `test_facade_jumeau.py`, qui part avec le moteur Python.
- `test_moteur.py` n'importe plus `_facteur_secteur`,
  `ANNEE_FORME_CATEGORIE`, `TRANCHES_CATEGORIE` ni `TRANCHES_SERIE` ;
  `profil_salaire` y reste, que lit le test des noms hérités du prototype.

## Ce qui reste de `test_moteur.py`

Les cas types et le mois, à la façade ; le test des noms hérités du
prototype, qui confronte le portage au Python et dont la place est
`test_facade_jumeau.py` ; les trois tests de la conversion qui attendent les
cas types et le coût, et le compte recomposé à la main, tels que la note de
la conversion les décrit.

**Tests.** `node --test tests/js/profil-salaire.test.js` (4),
`test_moteur.py` (23) et le test déplacé : verts ; `python -m pytest -m
rapide` : 5 371 passés, 64 sautés.
