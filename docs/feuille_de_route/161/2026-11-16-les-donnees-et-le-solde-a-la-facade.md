# Les données et le solde à la façade : deux fichiers de plus quittent le moteur Python

Action 161, étape 9k, après `2026-11-16-la-retraite-progressive-a-la-facade.md`.
Aucune règle, aucune donnée de calcul, aucune page n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) passe de 11 à 9.

## Ce qui est fait

- **`test_solde_fusion.py`** quitte le moteur Python. La grille sous les
  barèmes B et C se lit par `RegimeUniqueVariante._pensionnes`, appelée hors
  du contexte de la variante, sur le simulateur de la façade : plus de
  `monkeypatch`, donc plus de modèle modifié que la façade refuserait. Elle
  couvre désormais toutes les générations (le témoin des valeurs est refait :
  vérifié égal, au bit près, à ce que rend le simulateur Python sous la même
  lecture). Le contrôle « après la bascule » ne porte plus que sur les couples
  qui y cotisent, et exige que les générations 1965 à 2000 en soient.
- **La façade sert `mortalite.courbe`** (`pont.MORTALITE_DE_LA_FACADE`), que
  `cout._survies` lit, avec quatre appels confrontés au jumeau, et
  `Simulateur.univers_de_la_demande`, vide : la façade ne reçoit pas de
  variante.
- **`test_donnees.py`** quitte le moteur Python. Les affiliations et les
  valeurs du point se lisent sur le simulateur de la façade ; trois tables de
  plus sont servies (`ages_jouissance_militaire.age`,
  `durees_services_militaires` et `durees_services_actifs` :
  `annees_requises`, `duree_de_base`), confrontées au jumeau. Les clés des
  tables (classements, catégories), que le portage n'expose pas, se lisent
  dans leurs fichiers CSV ; `rang_borne` est refaite au test, sur `DateMois`.

## Ce qui reste : `test_controle_drees_panorama.py`

Passé à la façade à l'essai, il échoue sur trois points, du plus gros au plus
petit :

1. **Le portage n'a pas les populations de la Cnav par âge**
   (`esperances_vie_pensions_cnav.csv`, `facteurs_par_age` du Python) :
   `mortalite.courbe(…, "cnav_inaptitude")` lève « population inconnue » dans
   `moteur/js/mortalite.js`, et `cout._survies` le demande pour la grille
   entière (fixture `stock`). À porter d'abord, dans la zone du modèle.
2. **La grille datée par le pilote Python** : `cas.construire(projection, …)`
   et `projection.echeancier(…)` (fixture `au_minimum`, la fiche 12)
   appellent `pilote` et `coordonner` sur le simulateur de la façade. À lire
   plutôt dans la grille que le portage date (`cout._carrieres_du_cout`).
3. `mortalite.esperance_residuelle` et `mortalite.survie`, à servir
   (le portage les a).

**Tests.** `python -m pytest -m rapide` : vert. `test_solde_fusion.py`,
`test_donnees.py`, `test_facade.py`, `test_facade_jumeau.py` et
`test_fichiers_sur_le_moteur_python.py` : verts.
