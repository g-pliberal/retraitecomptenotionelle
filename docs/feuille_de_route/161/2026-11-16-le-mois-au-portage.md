# Le mois au portage : les tests du mois de la liquidation de `test_moteur.py` éprouvés sur le module du site

Action 161, quatrième vague, après `2026-11-16-le-profil-de-remuneration-au-portage.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé. `test_moteur.py` reste
dans `FICHIERS` : il garde 15 tests sur 23.

## Ce qui est fait

- **`tests/js/mois.test.js`**, neuf, tient sur `moteur/donnees.json` les
  huit tests du mois : la date de liquidation au mois (R. 351-37), l'origine
  des âges au mois qui suit la naissance (circulaire Cnav n° 2026-07,
  point 1.1), le demi-mois qui compte le mois suivant, l'année du départ au
  prorata, ses trimestres bornés aux trimestres civils (R. 351-9), le relevé
  tronqué au point de départ, le taux de remplacement annualisé (sur le
  simulateur du portage) et la circulaire de juillet 2022 (+3,9 %). Les
  attendus sont ceux du Python, posés sur le droit. Le jour présumé se lit
  dans `paquet.presomptions` : la carrière sans jour reçoit la chronologie de
  `duResume`, que le constructeur ne bâtit pas avec le paquet.
- **La confrontation de `en_mois` à `enMois`**, que le test du demi-mois
  menait par node, passe en grille dans `test_jumeaux_au_bit.py`, sur les
  mêmes âges ; `scripts/jumeaux_gardees.yaml` la nomme. Vu rouge en passant
  `enMois` à `Math.floor`, comme l'essai de node.

## Ce qui reste de `test_moteur.py`

Les cas types, à la façade ; le test des noms hérités du prototype, dont la
place est `test_facade_jumeau.py` ; les variantes d'espérance de vie ; les
tests de la conversion qui attendent les cas types et le coût, et le compte
recomposé à la main.

**Tests.** `node --test tests/js/mois.test.js` (8), `test_moteur.py` (15),
`test_jumeaux.py` et la grille de `en_mois` : verts ; `python -m pytest -m
rapide` : 5 373 passés, 64 sautés.
