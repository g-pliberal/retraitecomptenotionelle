# La rémunération et la limite d'âge à la façade : deux fichiers de la vague 4 quittent le moteur Python

Action 161, quatrième vague de l'inventaire
(`2026-11-15-les-temoins-sans-jumeau-et-l-inventaire.md`), menée en parallèle
de la session qui tient les univers et la troisième vague. Aucune règle,
aucune donnée, aucun témoin n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) perd deux fichiers.

## Ce qui est fait

- **`test_remuneration.py`** : le simulateur est celui de la façade, et les
  affiliations du module se lisent sur lui (`Simulateur(PARAMETRES).affiliations`),
  au lieu du chargeur `Affiliations` du moteur Python. Les 54 tests passent
  tels quels.
- **`test_limite_age.py`** : `limite_age.radiation` et `limite_age.radier`
  entrent dans `pont.REGLES_DE_LA_FACADE`, le module `limite_age.js` dans
  `MODULES_DU_DROIT` de `pont.mjs`, et la façade sert le module sous son nom
  (`facade.limite_age`). Le fichier importe `Carriere`, `Simulateur`,
  `departs` et `limite_age` de la façade ; ses 31 tests passent tels quels.
  Les deux règles sont confrontées au jumeau dans `test_facade_jumeau.py`
  (un sédentaire maintenu jusqu'à soixante-dix ans, un policier, une
  carrière qui finit avant sa limite), et leurs arguments à ceux du portage
  dans `test_facade.py`.

## Ce que la vague 4 a montré

- **`test_grille_large.py` et `test_cout.py` attendent le coût** : passé à
  la façade, le simulateur fait tomber 19 tests de la grille élargie, parce
  que `scripts/grille_large.py` appelle des règles Python sur le moteur
  (`coordonner.regimes_interpenetres`), retouche le modèle sous
  `monkeypatch`, ou lit `Simulateur.univers_de_la_demande`. C'est le même
  verrou que `test_effet_retour.py` : le coût et la grille doivent d'abord
  cesser de lire le moteur Python.
- **`test_emploi_retraite.py`** demande `droit.cumul` et `droit.seconde` à
  la façade ; `cumul.cumuler` y reçoit une fonction Python (`pensions_de`),
  que le pont ne transmet pas : à servir sous une table de pensions.

## Ce qui reste de la vague 4

`test_capitalisation.py`, `test_emploi_retraite.py`, `test_independants.py`,
`test_moteur.py`, `test_pont.py` ; puis, après le coût, `test_cout.py` et
`test_grille_large.py`.

**Tests.** `python -m pytest -m rapide` : 5 426 passés, 64 sautés ;
`test_remuneration.py`, `test_limite_age.py`, `test_facade.py`,
`test_facade_jumeau.py`, `test_fichiers_sur_le_moteur_python.py` : verts.
