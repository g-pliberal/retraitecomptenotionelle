# Les fiches de la proposition sans Python : l'étape 5 achevée

Action 161, fin de l'étape 5 de l'inventaire
(`2026-11-16-l-inventaire-du-retrait-des-regles.md`, section 5), menée la
nuit du 16 novembre 2026, sur la consigne du propriétaire d'avancer ce qui ne
demande pas son avis. Elle suit `2026-11-16-le-code-python-hors-des-fiches.md`,
qui avait laissé de côté les neuf fiches de la proposition parce que leur test
importait les modules Python. Aucune donnée, aucune règle, aucun résultat n'a
bougé : les fiches n'entrent pas dans le paquet, et aucun module Python n'est
supprimé.

- **Les fiches.** Les neuf fiches de `data/reference/regles/proposition/`
  perdent leur clause `python` (25 lignes) ; chacune, relue par YAML, est
  celle d'avant moins cette clause. Toutes gardent leur clause `javascript`,
  la liste des fonctions de la règle selon la note de décision 0009.
- **Le test** (`tests/test_univers.py`,
  `test_chaque_fiche_de_la_proposition_dit_son_code`). Il n'importe plus les
  modules Python : il refuse une clause `python`, vu rouge d'abord sur les
  neuf fiches, et vérifie comme avant les fonctions JavaScript, les
  paramètres et les tests nommés.
- **Ce que l'étape déplace ailleurs.** Le relevé des jumeaux
  (`scripts/jumeaux.py`) ne voit plus ces fiches nommer les modules Python
  du modèle notionnel ; c'est le sujet des gardes des jumeaux, plus loin dans
  l'inventaire.

**Ce qui reste.** Les 22 chiffres ancrés qui chargent un module de règles,
les chargements par chemin et les gardes des jumeaux ; puis la carrière que
le pont relit sous la classe des règles.

**Tests.** `python -m pytest -m rapide` : 5 693 passés. `test_univers.py`,
`test_carte.py`, `test_jumeaux.py`, `test_donnees.py` : 211 passés.
