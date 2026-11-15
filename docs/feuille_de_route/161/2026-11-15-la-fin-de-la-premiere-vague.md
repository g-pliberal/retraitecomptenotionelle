# La fin de la première vague : l'estimation du site et les affirmations sortent du moteur Python

Action 161, étape 9b, après `2026-11-15-la-premiere-vague.md`. Aucune règle,
aucune donnée, aucun témoin, aucune page n'a bougé : des tests changent, et le
pont sert quatre règles de plus, que le portage portait déjà. La suite
complète de GitHub était rouge sur l'envoi des indépendants (trois valeurs
absentes du témoin des valeurs) ; l'envoi suivant, qui fait suivre au témoin
les fixtures et les aides, la répare : ces trois tests passent ici. Sa course
tournait encore.

## Ce qui est fait

Les deux fichiers restants de la vague 1 quittent `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) : 77 fichiers → 75.

- **`test_estimation_du_site.py`** simule par la façade : sa fixture
  `saisies` devient `Saisies(facade.Simulateur)`, et les règles d'ouverture
  viennent de `facade.ouvrir`. La façade sert désormais
  `ouvrir.age_annulation_droit` (`pont.REGLES_DE_LA_FACADE`,
  `LECTURES_DU_DROIT`), confrontée à son jumeau dans
  `test_facade_jumeau.py`. Les deux grandes confrontations gardent leur
  forme : chaque départ du pilote (`departEstime`) est tenu à l'âge que
  l'étape « ouvrir le droit » oppose à la carrière, et à la liquidation que
  l'échéancier simule, étage par étage — deux chemins distincts du portage.
  Le test de la carrière longue ne demande plus `periodes_parcourues` : le
  premier départ précède l'âge légal de la génération 1966, 63 ans et 3 mois
  (L. 161-17-2, après la loi n° 2025-1403, article 105).
- **`test_affirmations.py`** : `Modele` simule par `Saisies(facade.Simulateur)`.
  Ce que le moteur Python calculait seul passe au pont par `pont.droit`
  (une aide `du_portage`) : trois sondes de plus dans `pont.mjs`
  (`conversion.coefficient.diviseur`, `indexation.taux`,
  `carriere.ancrage_salaire_moyen`), et `indexation.coefficient` refait les
  cumuls que le site compare. L'allocation du pilier se compare par
  `capitalisation.construire`, le roulement à un an décrit en données, au
  lieu de remplacer `repartition` dans le module Python. `MinimumVieillesse`
  et `repartition` se lisent dans le portage (`module("regimes")`,
  `module("capitalisation")`), `_coefficient_anticipation` par
  `facade.liquider`. La façade laisse lire six chargeurs de données de plus
  (`effectifs`, `distribution`, `caracteristiques`, `patrimoine`,
  `vie_en_couple`, `courbe_taux` : `facade.DONNEES`). Les carrières types et
  la courbe de survie de la garantie se lisent au simulateur du contexte, en
  Python, comme le coût qui les calcule.

## Ce qui reste

La deuxième vague, 40 fichiers, telle que l'inventaire la range
(`2026-11-15-les-temoins-sans-jumeau-et-l-inventaire.md`, « Vague 2 »). L'angle
mort de l'inventaire demeure : `Saisies()` sans la façade, dans
`test_droits_contrefactuels.py` et ailleurs, entre dans le moteur Python sans
y être compté.

## Ce qui attend le propriétaire

L'écart `rattachement_pension_smic` (3,45 € par an), inchangé.

**Tests.** `python -m pytest -m rapide` : 5 417 passés, 64 sautés. Les deux
fichiers, `test_facade.py`, `test_facade_jumeau.py`, `test_pont.py`,
`test_droit_fige.py`, `test_sondes_par_le_pont.py` et
`test_fichiers_sur_le_moteur_python.py` : verts.
