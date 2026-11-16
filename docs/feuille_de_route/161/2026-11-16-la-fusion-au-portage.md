# La fusion au portage : les tests de `fusionner` de `test_moteur.py` éprouvés sur le catalogue des fiches du site

Action 161, quatrième vague, après `2026-11-16-l-age-de-reference-au-portage.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé. `test_moteur.py` reste
dans `FICHIERS` : il garde 28 tests sur 35.

## Ce qui est fait

- **`tests/js/fusion.test.js`**, qui éprouvait déjà la fusion sur un
  catalogue posé à la main, la fusionne aussi sur celui des fiches
  (`moteur/donnees.json`), en 2026 : les sept tests de `test_moteur.py`. Les
  âges les plus élevés de tous les régimes vivants en répartition ; aucun
  avantage non contributif ; la carrière entière comme salaire de référence ;
  l'assiette déplafonnée ; le taux du statut pivot, régime général et
  tranche 1 de l'Agirc-Arrco, cotisation déplafonnée comprise ; le RAFP hors
  de la fusion ; « le plus élevé », la caisse la plus chère. Les attendus se
  relisent sur les périodes des fiches, comme dans le Python. Sans la
  déplafonnée dans `tauxTotal`, le test du statut pivot échoue bien.
- `test_moteur.py` n'importe plus `fusionner`, `RegleFusion` ni
  `CritereTaux`, et perd la fixture `catalogue`, qui ne servait plus.

## Ce qui reste de `test_moteur.py`

Par module, une étape chacun : le profil de rémunération (`profil_salaire`,
`_facteur_secteur`) ; les cas types et le mois, à la façade. Les trois tests
de la conversion qui attendent les cas types et le coût, et le compte
recomposé à la main, restent tels que la note de la conversion les décrit.

**Tests.** `node --test tests/js/fusion.test.js` (14), `test_moteur.py` (28),
`test_fichiers_sur_le_moteur_python.py` : verts.
