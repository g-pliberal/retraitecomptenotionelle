# Les chargements par chemin : plus aucun script ni test ne lit un fichier de règles par son nom

Action 161, étape 5 de l'inventaire
(`2026-11-16-l-inventaire-du-retrait-des-regles.md`, section 5, « Les
chargements par chemin »), menée la nuit du 16 novembre 2026, sur la consigne
du propriétaire d'avancer ce qui ne demande pas son avis. Aucun résultat,
aucune donnée, aucun témoin n'a bougé ; aucun fichier du moteur, Python ou
JavaScript, n'est touché.

- **La garde.** `tests/test_jumeaux.py`
  (`test_aucun_chargement_par_chemin_ne_vise_un_fichier_de_regles`, vu rouge
  d'abord) lit dans la carte des jumeaux chaque chaîne du code qui nomme un
  fichier Python, et refuse celles qui visent un fichier de règles, hors de
  `CHARGENT_ENCORE_UNE_REGLE` : la sonde du moteur Python
  (`scripts/sonde_moteur_python.py`) et le relevé de ce qui y entre
  (`scripts/entrees_du_moteur.py`), avec leurs tests. Leur objet est le moteur
  Python : ils partent avec lui, à la suppression, comme les gardes qui
  s'en servent (`tests/test_sondes_par_le_pont.py`,
  `tests/test_mortalite_population.py`, qui vérifient qu'une sonde n'entre
  plus dans le moteur Python).
- **Le tableau de bord** (`scripts/tableau_de_bord.py`, et `docs/etat.md`
  qu'il refait) nomme les étapes du relevé et de la liquidation par leur
  module du portage (`droit/ouvrir.js`, `moteur/js/droit/liquidation.js`,
  `moteur/js/echeancier.js`…), et non plus par leur jumeau Python. Le coût
  du travail (`--cout`) compte comme changement du moteur un commit qui
  touche `moteur/js/scenario-actuel.js` ou `moteur/js/droit/`, ou, dans
  l'historique, les dossiers `droit/` et `scenarios/` du paquet ; la taille
  du dépôt ne compte plus que les lignes du portage.
- **Deux tests.** `tests/test_univers.py` vérifie que le compte applique ses
  trois interrupteurs de cotisation dans `moteur/js/compte.js`, et non plus
  dans `moteur/compte.py` ; `tests/test_carte.py` illustre la clause
  `python` refusée d'une fiche par un fichier qui n'existe pas
  (`droit/chimere.py`), sans nommer un fichier de règles.

**Ce qui reste pour la suppression.** La carrière que le pont relit sous la
classe des règles (`carriere.py`, `droit/__init__.py`, `droit/preparer.py`,
que nomme `REGLES_ENCORE_ATTEINTES`), puis la suppression elle-même, sur
l'accord final du propriétaire, qui retirera aussi les deux sondes, leurs
tests et `CHARGENT_ENCORE_UNE_REGLE`.

**Tests.** `python -m pytest -m rapide` : 5 693 passés. `tests/test_carte.py`,
`test_univers.py`, `test_jumeaux.py`, `test_outillage.py`, `test_prose.py` :
216 passés.
