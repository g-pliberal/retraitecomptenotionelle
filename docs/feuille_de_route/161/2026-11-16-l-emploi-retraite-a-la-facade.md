# L'emploi-retraite à la façade : le cumul prêté par le pont, ses constantes et deux règles servies

Action 161, quatrième vague, après `2026-11-16-les-independants-a-la-facade.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé. `test_emploi_retraite.py`
quitte `FICHIERS`.

## Ce qui est fait

- **`test_emploi_retraite.py`** importe `Carriere`, `Simulateur`, `liquider`,
  `cumul` et `seconde` de la façade.
- **Le cumul aux pensions prêtées** (`_cumul_prete`) se demande au pont,
  `cumul.cumuler.pensions_pretees`, comme l'exemple de la caisse dans
  `test_oracle.py`, au lieu de passer une fonction Python à `cumul.cumuler`.
- **`cumul.assiette_csg` et `cumul.jour`** entrent dans
  `pont.REGLES_DE_LA_FACADE` (le module `cumul.js` dans `MODULES_DU_DROIT`),
  confrontés au jumeau ; la façade sert `cumul` et `seconde`, dont les tests ne
  lisent sinon que des constantes. Un module que la façade sert sans règle
  (`seconde`) refuse ce qui n'est pas une constante (`REGLES.get`).
- **La table des sections** se confronte à la fiche
  `cumul_emploi_retraite_complementaires_des_liberaux` sur le portage
  (`REGLES_DES_SECTIONS` de `cumul.js`, lu par node), au lieu du Python.
- **Les règles citées par le cumul** se lisent par leur nom, une à une, au
  lieu de `vars(cumul)`.
- La nouvelle pension des régimes non liquidés se lit dans la demande de sa
  liquidation au journal (`donnees()["demande"]["regimes"]`).

## Ce qui reste de la vague 4

`test_moteur.py`, `test_pont.py` ; puis, après le coût, `test_cout.py` et
`test_grille_large.py`.

**Tests.** `python -m pytest -m rapide` : 5 419 passés, 64 sautés ;
`test_emploi_retraite.py` (91), les règles de `test_facade.py` et de
`test_facade_jumeau.py`, `test_fichiers_sur_le_moteur_python.py` : verts.
