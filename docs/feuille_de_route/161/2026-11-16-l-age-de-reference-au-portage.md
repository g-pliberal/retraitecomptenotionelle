# L'âge de référence au portage : les tests du cliquet de `test_moteur.py` éprouvés sur le module du site

Action 161, quatrième vague, après `2026-11-16-la-conversion-au-portage.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé. `test_moteur.py` reste
dans `FICHIERS` : il garde 35 tests sur 41.

## Ce qui est fait

- **`tests/js/age-reference.test.js`**, neuf, que `test_web.py` lance avec
  les autres essais de node : les six tests de `test_moteur.py` qui bâtissaient
  `AgeReference` passent sur `moteur/js/age-reference.js`. Le cliquet qui ne
  redescend jamais ; le défaut, cliquet jusqu'à la bascule puis 65 ans,
  l'âge légal de la proposition ; l'abaissement de 1982 qui ne baisse pas la
  référence (cinq ans d'anticipation à 60 ans en 1990) ; la référence sans
  cliquet, qui suit le droit positif ; le départ à 50 ans d'un régime
  spécial ; le report compté négativement. Les attendus sont l'âge du taux
  plein que fixait le droit (65, 60, 67 ans) et des sens de variation, comme
  dans le Python. Le test du cliquet, lancé sous le mode sans cliquet, échoue
  bien en 1982.
- `test_moteur.py` n'importe plus `AgeReference` ni `ModeAgeReference`, et
  perd la fixture `mortalite`, qui ne servait plus.

## Ce qui reste de `test_moteur.py`

Par module, une étape chacun : `fusionner` (7), par
`tests/js/fusion.test.js` ; le profil de rémunération (`profil_salaire`,
`_facteur_secteur`) ; les cas types et le mois, à la façade. Les trois tests
de la conversion qui attendent les cas types et le coût, et le compte
recomposé à la main, restent tels que la note précédente les décrit.

**Tests.** `node --test tests/js/age-reference.test.js` (6), tous les essais
de node (230), `test_moteur.py` (35), `test_fichiers_sur_le_moteur_python.py`
: verts ; `python -m pytest -m rapide` : vert.
