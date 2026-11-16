# Les replis Python retirés : la grille ne se date plus qu'au portage

Action 161, point 3 de « Ce qui reste » de
`2026-11-16-le-tri-des-scripts-et-des-modules.md`. Aucune règle, aucune
donnée, aucun témoin n'a bougé.

La grille se date, se bâtit et se liquide au portage depuis l'étape 6 ; le
moteur Python ne la refaisait plus qu'en repli, pour un cas type que le
portage ne date pas (`castypes.decrit_au_portage`), ce qu'aucun n'est. Ces
replis sont retirés : un tel cas type est refusé (`ValueError`), par
`castypes.exiger_le_portage`.

- `castypes` : `cases_de_la_grille` et `ages_de_la_grille` ; part
  `carrieres_de_la_grille`, qui ne servait qu'aux replis.
- `cout._grille_batie` ; partent `_prolongations` et `_carrieres_voisines`.
- `avantages.decomposer` et `ages_legaux` ; partent `_decomposees_en_python`
  et `_voisines_en_python`.
- `facteurs_depense.dates_des_departs` ; et `dates_a_l_age_legal` lit l'âge
  légal au portage (`pont.droit`, `scenario_actuel.ages_ouverture.age`, une
  demande pour toutes les cohortes), comme `avantages.ages_legaux`, au lieu
  du chargeur du scénario 1 : il n'exécute plus de règle (la sonde).

Restent, jumeaux que des tests éprouvent et qui partent avec les règles :
`castypes.calculer_cas_types` et `carriere_de_la_grille`
(`test_agregats.py`, `test_affirmations.py`), `avantages.recalculer`,
`scenarios_neutralises`, `carriere_variante` (`test_avantages.py`).

**Vérifié.** `dates_a_l_age_legal` sur toute la grille, sans et avec
l'entrée selon le premier trimestre (depuis 1950) : 655 et 756 départs,
identiques à l'octet avant et après. Les autres chemins sont ceux du
portage, que rien n'a touchés.

**Tests.** `tests/test_le_portage_seul.py` (6, rapide) : chaque entrée refuse
un cas type hors du portage ; `dates_a_l_age_legal` sans règle du moteur
Python, et le départ à l'âge légal du salarié né en janvier 1960
(février 2022) ; vus rouges puis verts. `test_pont.py` n'interdit plus ce qui
est parti. `python -m pytest -m rapide`, `test_pont.py`, `test_avantages.py`,
`test_facteurs_depense.py`, `test_cout_age_depart.py`,
`test_grille_large.py` : verts.

**Reste** : le point 4, les chargeurs du groupe 2 sous `donnees/`.
