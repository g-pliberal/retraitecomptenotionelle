# Le rétablissement et le plafond de L. 18 à la façade : deux fichiers quittent le moteur Python

Action 161, étape 9i, après `2026-11-16-la-revalorisation-et-le-versement-unique.md`.
Aucune règle, aucune donnée de calcul, aucune page n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) passe de 14 à 12, la vague 4
comprise.

## Ce qui est fait

- **`test_retablissement.py`** quitte le moteur Python. La façade sert
  `coordonner.retablir` par la coordination du portage
  (`coordonner.coordonner(...).carriere`) : comme son jumeau, elle rend la
  carrière reçue elle-même quand rien n'est rétabli ni écarté, ce que les
  tests vérifient par identité. Les régimes d'une année rétablie, que le test
  lisait par `coordonner.regimes_de`, se lisent sur la même coordination,
  ligne par ligne ; le catalogue et les séries, sur le simulateur.
- **`test_plafond_majoration_enfants.py`** quitte le moteur Python. La façade
  sert `completer.majoration_sous_le_traitement` (règle) et
  `fiches_datees.version` (table), chacune confrontée au jumeau
  (`test_facade_jumeau.py`). La fiche retirée et la fiche altérée par
  `monkeypatch`, que le portage ne voyait pas, se lisent sur une copie
  retouchée des données (`facade.donnees_retouchees`) : « retirée » y devient
  une fiche dont aucune version n'existe, « altérée », une surcote `moitie`
  que le portage refuse. Le schéma de l'étape « liquider » se lit sur l'étape
  servie seule (`releve.construire`, `ouvrir.ouvrir`,
  `liquider.liquider_chaque_regime`), la liquidation entière n'en rendant que
  le contrat C.6.

## Ce qui reste de la vague 3

- `test_solde_fusion.py` : la grille sous une variante du coût
  (voir la note précédente).
- `test_retraite_progressive.py`, `test_controle_drees_panorama.py`,
  `test_donnees.py` : non regardés.

**Tests.** `python -m pytest -m rapide` : vert (5 388 tests). Les deux
fichiers, `test_facade.py`, `test_facade_jumeau.py` et
`test_fichiers_sur_le_moteur_python.py` : verts.
