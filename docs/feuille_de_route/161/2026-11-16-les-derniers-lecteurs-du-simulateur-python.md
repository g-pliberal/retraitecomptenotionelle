# Les derniers lecteurs du simulateur Python : six scripts de plus sur le simulateur de données

Action 161, suite de `2026-11-16-les-scripts-sur-le-simulateur-de-donnees.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé ; aucune règle n'est
retirée, le moteur Python reste en place.

Des huit scripts que la note précédente laissait sur le simulateur Python,
six ne lui demandaient plus aucun calcul : leurs carrières, leurs simulations
et leurs règles passent déjà par le pont. Ils n'en lisaient que des données,
et bâtissent désormais un `SimulateurDeDonnees` :

- `fetch/trajectoire.py` : la macro ;
- `lectures_decision_29` : les paramètres et la macro que lisent les cas
  types (`pour_le_portage`, `primes_projetees_en_donnees`) ;
- `mesurer_surcote` : les effectifs de la population ;
- `mesures_prose` : la macro et la mortalité (`_simulateur`) ; ses
  simulations passaient déjà par `pont.facade` ;
- `recours_aspa` : les effectifs, et le barème de l'ASPA lu par le chargeur
  de `donnees/minimum_vieillesse.py` au lieu de
  `scenario_actuel.minimum_vieillesse` ;
- `scenarios_meres` : les paramètres et la macro ; il garde le type
  `Comparaison`, que la façade du pont rend, importé pour les annotations
  seules.

Restent sur le simulateur Python : `grille_large`, dont les jumeaux
(`age_liquidation_pour`, `_carriere`, `_debut_de_la_surcote_en_python`) sont
éprouvés par ses tests et partent avec les règles, et dont le reste ne lit
que des données ; `lectures_du_modele`, qui simule exprès par le moteur
Python pour relever ce qu'il lit (à refaire sur ce que lit le portage) ;
`contexte.simulateur`, que la fabrique et le bilan du compte lisent, laissé à
leur zone.

**Vérifié.** `scenarios_meres` sous la sonde, avant et après : sortie
identique à l'octet, même liste relevée (les seules méthodes du type
`Comparaison` que la façade rend). Pour les autres, trop longs à lancer en
entier dans un conteneur : le `Simulateur` hérite du simulateur de données,
dont `macro`, `mortalite` et `effectifs` sont les mêmes propriétés (vérifié
par identité) ; le barème de l'ASPA rend les mêmes plafonds, seul et en
couple, de 2007 à 2070.

**Tests.** `tests/test_chargeurs_a_part.py` (1 de plus) : aucun de ces six
scripts n'importe ni ne bâtit le `Simulateur` ; vu rouge, puis vert. Les
tests de `scenarios_meres`, `recours_aspa`, `lectures_decision_29` et
`trajectoire` : verts. `python -m pytest -m rapide` : vert.

**Reste.** `grille_large`, puis `lectures_du_modele` ; le retrait des
règles, avec l'accord du propriétaire.
