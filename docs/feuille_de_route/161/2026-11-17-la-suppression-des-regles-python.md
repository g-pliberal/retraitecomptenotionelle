# La suppression des règles Python : les 40 fichiers partis, et ce qui les confrontait

Action 161, quatrième lot de la suppression
(`2026-11-17-l-essai-a-blanc-de-la-suppression.md`), mené le 17 novembre
2026, la suite complète verte sur `main` avant de commencer (la course de
f292163). Aucune règle, aucune donnée, aucune valeur attendue ne change.

## Fait

- **Les 40 fichiers de règles supprimés** : `droit/`, `moteur/`,
  `scenarios/` avec leurs `__init__.py`, et `carriere.py`, `echeancier.py`,
  `journal.py`, `pilote.py`, `revalorisation.py`, `simulateur.py`. Le paquet
  n'en charge plus rien ; le coût et la fabrique n'en chargeaient déjà plus.
- **Les confrontations au jumeau parties avec lui** :
  `tests/test_facade_jumeau.py`, `tests/jumeau_des_avantages.py`, la sonde du
  moteur Python (`scripts/sonde_moteur_python.py`), le relevé de ses entrées
  (`scripts/entrees_du_moteur.py`), leurs tests, et
  `tests/test_fichiers_sur_le_moteur_python.py`. Les tests qui faisaient
  tourner un script sous la sonde le font tourner seul, dans un processus
  neuf (`test_sondes_par_le_pont.py`, `test_mortalite_population.py`,
  `test_grille_large.py`, `test_le_portage_seul.py`, `test_outillage.py`).
- **`test_facade.py` garde ses tests**, sans les modules de règles : les
  types se lisent sous `types_du_pont`, les signatures des bâtisseurs et des
  règles dans leurs contrats (`tests/contrats_de_la_facade.py`), et « un
  autre moteur » refusé est un objet quelconque ou un simulateur de données
  seules. Deux confrontations au jumeau (la période et la valeur du point
  d'un chef agricole) deviennent des propriétés : la période est du régime et
  couvre 2002, la valeur est positive. Le garde de la façade qui refusait
  qu'une règle Python lise son moteur est parti, et son test.
- **Le coût des avantages, au portage** : les cinq tests de
  `test_avantages.py` qui liquidaient en Python sous les scénarios
  neutralisés les demandent au portage (`pont.avantages`, ou
  `pont.MOTEUR.neutralisant` par `pont.droit`), aux mêmes valeurs attendues
  (190 et 180 trimestres, 134 et 124, le rapport de 134 à 124).
- **Les gardes des jumeaux** (`tests/test_jumeaux.py`) : partis, l'accord
  avec la sonde, les règles encore atteintes par le coût, la liste des
  fichiers qui chargeaient une règle par son chemin, le classement des
  paires du moteur. Un test neuf,
  `test_aucun_fichier_de_regles_ne_reste`, rouge avant le lot : aucun
  fichier suivi n'est une règle, aucune paire n'a son Python parmi elles,
  aucun en-tête ne déclare un jumeau parti.
- **Les 35 en-têtes JavaScript** qui déclaraient leur jumeau (« Portage de »,
  « Jumeau de ») ne le déclarent plus ; le reste de chaque en-tête est gardé.
- **Les renvois** des docstrings vers une règle partie
  (`:func:`~retraite_notionnelle.droit.…``) nomment la fonction du portage et
  son fichier ; de même les commentaires des étapes et des contrats sous
  `data/reference/`, la carte du dépôt, la méthodologie et les limites.

## Ce qui reste

1. **Les fonctions `au_moteur` de `scripts/jumeaux_gardees.yaml`** : 121
   fonctions des paires qui restent, que seuls le moteur Python et des tests
   lisaient ; elles sont mortes, et partent avec leur entrée de la liste.
2. **Les consignes** (`src/CLAUDE.md`, `moteur/CLAUDE.md`) et
   `docs/architecture.md` parlent encore des jumeaux du moteur au présent.
3. Les étapes ouvertes de l'action, dont le défaut du relevé
   (note de décision 0008), qui se corrige maintenant.

**Tests.** Le test neuf vu rouge avant le lot, vert après ;
`python -m pytest -m rapide` : 5 450 réussis ; le reste de la suite, en
local : 3 470 réussis, quatre échecs vus et réparés (deux `monkeypatch`
d'un module parti, deux fichiers fabriqués refaits).
