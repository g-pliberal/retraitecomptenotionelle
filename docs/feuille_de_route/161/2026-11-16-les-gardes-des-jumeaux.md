# Les gardes des jumeaux : la carte nomme elle-même les fichiers de règles

Action 161, étape 5 de l'inventaire
(`2026-11-16-l-inventaire-du-retrait-des-regles.md`, section 5, « Les
gardes des jumeaux »), menée la nuit du 16 novembre 2026, sur la consigne du
propriétaire d'avancer ce qui ne demande pas son avis. Aucun chiffre, aucune
donnée, aucun résultat n'a bougé ; aucun fichier JavaScript ni module Python
n'est touché, hors de `scripts/jumeaux.py`.

- **Les fichiers de règles.** `scripts/jumeaux.py` les reconnaît à leur
  chemin (`est_une_regle`, `DOSSIERS_DE_REGLES`, `FICHIERS_DE_REGLES`), sans
  lire `scripts/sonde_moteur_python.py`, qui part avec eux ; un test
  vérifie que les deux s'accordent tant que la sonde existe.
- **La liste des fonctions gardées** (`scripts/jumeaux_gardees.yaml`) ne
  nommait déjà aucun fichier de règles. `ecarts_de_la_liste` le refuse
  désormais : une paire dont le Python est une règle, ou un lecteur qui en
  est une, même sans jumeau JavaScript.
- **Les paires du moteur** : `Carte.paires_du_moteur()` rend les 36 paires
  (sur 65) dont le Python est une règle, celles qui partent ; un test dit
  qu'aucune n'est dans la liste et que les 29 autres restent.
- **Les tests du dépôt** ne nomment plus un fichier de règles qui
  disparaîtra : le détail d'une paire s'imprime sur `calendrier` et non
  `simulateur` ; le test du coût et de la fabrique dit qu'ils n'atteignent
  d'autre règle que `carriere.py`, `droit/__init__.py` et
  `droit/preparer.py` (la carrière que le pont relit), liste qui ne peut que
  rétrécir ; celui des chiffres ancrés lit `est_une_regle`.

**Ce qui reste pour la suppression.** 35 des 36 paires du moteur se
déclarent par l'en-tête de leur JavaScript (« Jumeau de », « Portage de »).
Quand le Python partira, `test_chaque_declaration_de_jumeau_nomme_un_fichier_qui_existe`
rougira sur chacune : l'étape de la suppression récrit ces en-têtes
(fichiers du site, à ne pas toucher en parallèle d'une session sur les
pages). Avant elle : les chargements par chemin, puis la carrière que le pont relit sous la classe des
règles, qui videra `REGLES_ENCORE_ATTEINTES` de `tests/test_jumeaux.py`.

**Tests.** `python -m pytest -m rapide` : 5 693 passés.
`tests/test_jumeaux.py` (6 tests vus rouges d'abord) et
`tests/test_jumeaux_au_bit.py` : 146 passés.
