# Les servis figés : `servi_et_refait` ne fait plus rien refaire au moteur Python

Action 161, étape 8b, après `2026-11-15-le-solveur-de-l-inversion-retire.md`.
Aucune règle du portage, aucune donnée n'a bougé ; un témoin naît.

## Ce qui est fait

- **Le témoin des servis**, `tests/temoins/servis.json` : les 352 cas que
  les confrontations du scénario 1 demandent au portage (quatorze fichiers,
  dont l'estimation officielle et Destinie 2), chacun sous l'empreinte de ce
  que le portage lit (`empreinte_du_cas`, sa clé ôtée : dix-neuf clés
  nommaient deux cas différents d'un fichier à l'autre), avec sa clé, sa
  requête et ce qui en est servi, ou le motif du refus. Figé juste après une
  course verte de `servi_et_refait` : chaque valeur est celle que le moteur
  Python refaisait au bit près.
- **`servi_et_fige`** (`tests/outils_pont.py`) remplace `servi_et_refait` :
  il sert par le portage, puis confronte chaque cas au témoin, au bit près
  sous Linux x86_64. Un cas absent arrête le test ; `FIGER_SERVIS=1 python
  -m pytest <fichier>` l'ajoute (sous verrou, le fichier remplacé d'un coup :
  les processus de xdist figent ensemble).
- **La fabrique le refait** : `construire_temoins.py` sert de nouveau chaque
  requête du témoin et le réécrit, avec les deux autres témoins ;
  `--servis` ne refait que lui, en quatre secondes, ce qu'une session dont la
  règle déplace un cas lance pour remettre ses tests au vert. Il est
  `-merge` (`.gitattributes`), déclaré dans l'étape « témoins » de
  `regenerer.py` et de `fabrique.py`.
- **`tests/test_servis_figes.py`** : l'empreinte, le refus d'un cas absent,
  l'ajout sous `FIGER_SERVIS`, le moteur Python interdit, et le témoin
  resservi à l'octet (quatre secondes, au niveau rapide).

## Ce qui reste de l'étape

1. **Les dix-sept tests marqués `sur_le_moteur_python`** (douze fichiers,
   `RESTES` de `tests/test_fichiers_sur_le_moteur_python.py`). Leurs formes :
   les sorties de `tests/js/comparer-liquidation.mjs` (invalidité,
   liquidation, majoration exceptionnelle, minima agricoles, pension
   maximale, pension minimum avant 1983), de `comparer-droit.mjs` (droit),
   de `comparer-assimilees.mjs` (périodes assimilées, deux fichiers), de
   `comparer.mjs` (majorations du conjoint et des enfants à charge, qui
   simulent tout), et un script JS en ligne (oracle des périodes
   assimilées). Piste : un témoin générique des sorties, sur le modèle de
   celui des servis — le script, son entrée figée, sa sortie —, que
   `construire_temoins.py` refait en relançant le script ; les assertions
   que le test portait sur la moitié Python passent à la sortie JS. Les
   tests de `test_droit.py` et `test_liquidation.py` portent sur un
   cinquième des témoins de simulations, déjà figés en entier : mesurer la
   taille avant de figer leurs étapes.
2. **Les confrontations de `tests/test_pont.py`** : `CONFRONTATIONS_DU_JUMEAU`
   (onze), `TESTS_DU_LEVIER` (deux), le levier `pont.par_le_jumeau`,
   `cout._simulations_en_python`, et trois tests non déclarés qui refont au
   Python : `Saisies().scenario_actuel` (vers la ligne 789),
   `test_le_moteur_python_refait_des_temoins_de_chaque_forme`,
   `test_le_moteur_python_refait_chaque_temoin`. `Saisies.scenario_actuel`
   et `scenario_actuel_en_donnees` partiront avec le premier.

**Tests.** Les quatorze fichiers et `test_servis_figes.py` : 821 passés ;
`python -m pytest -m rapide` : 5 370 passés, le seul échec (le nouveau
fichier importait `Simulateur`) corrigé et relancé ; `test_outillage.py`,
`test_pousser.py`, `test_pages_en_dossier.py`, `test_fabrique.py`,
`test_niveaux.py` : verts.
