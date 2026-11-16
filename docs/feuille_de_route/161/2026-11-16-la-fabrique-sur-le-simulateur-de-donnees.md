# La fabrique sur le simulateur de données : le contexte ne bâtit plus le simulateur Python

Action 161, suite de `2026-11-16-le-releve-des-lectures-au-moteur-javascript.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé ; aucune règle n'est
retirée, le moteur Python reste en place.

`Contexte.simulateur` (`src/retraite_notionnelle/contexte.py`), que lisent la
fabrique du paquet (`scripts/construire_donnees.py`) et le bilan du compte
(`bilan_compte.py`, le module et le script), bâtit désormais le simulateur de
données seules (`SimulateurDeDonnees`). Ses lecteurs n'en prenaient que des
données : les paramètres, la macro, la courbe des taux, les effectifs, la
projection ; la grille, ses âges, ses cases écartées et ses simulations
passaient déjà par le pont (`cases_de_la_grille`, `ages_de_la_grille`,
`pont.carrieres`), et la mémoire du coût bâtissait déjà le simulateur de
données. Le contexte était le dernier lecteur du `Simulateur` Python hors des
tests de la façade.

Trois fichiers de tests lisaient le contexte pour simuler en Python :

- `test_agregats.py` et `test_affirmations.py` refaisaient la grille par
  `castypes.calculer_cas_types`, sur le pilote et le moteur Python. Ils la
  refont par la façade (`tests/outils_grille.py`, `grille_a_la_facade`) :
  chaque case datée et écartée au portage (`cases_de_la_grille`), bâtie
  (`CasType.carriere_a`) et simulée par la façade, qui rend la
  `Comparaison` entière que lisent les affirmations. L'âge de chaque cas
  type se lit au `pilote` de la façade, les départs du classement à son
  simulateur.
- `test_web_revues.py` lisait le barème de l'ASPA sur
  `scenario_actuel.minimum_vieillesse` ; il le lit par le chargeur de
  `donnees/minimum_vieillesse.py`, comme `recours_aspa`.

`castypes.calculer_cas_types` n'a plus d'appelant ; il part avec les règles.

**Vérifié.** La fabrique lancée avant et après : `moteur/donnees.json`,
`agregats.json`, `equilibre.json`, `certification.json` et
`calibrations_mortalite.json` identiques à l'octet (trois minutes chacune).
Sous la sonde, après, elle n'exécute plus que des chargeurs logés dans les
fichiers du droit (les classes de `scenarios/actuel.py`,
`moteur/age_reference._charger_ages`) et des types du pont (`Carriere`,
`AnneeCarriere`, `Affiliations`), soit 104 fonctions, que la note de décision
0009 doit reloger : aucune règle de calcul.

**Tests.** `test_chargeurs_a_part.py` :
`test_le_contexte_de_la_fabrique_batit_le_simulateur_de_donnees` (neuf), vu
rouge, puis vert. `test_agregats.py` (19), `test_bilan_compte.py`, les
contrôles des affirmations qui lisent la grille, la colonne de l'ASPA :
verts. `python -m pytest -m rapide` : vert.

**Reste.** L'inventaire de ce que retirerait la suppression des règles
Python, sans rien supprimer ; le retrait lui-même, avec l'accord du
propriétaire.
