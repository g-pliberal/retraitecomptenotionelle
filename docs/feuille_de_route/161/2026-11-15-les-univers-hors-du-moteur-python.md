# Les univers hors du moteur Python : leur résolution rangée à la fabrique

Action 161, étape 9e, après `2026-11-15-la-fin-de-la-deuxieme-vague.md`.
Aucune règle, aucune donnée, aucune page n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) passe de 37 à 36.

## Ce qui est fait

- **La résolution des univers change de dossier.** Ce que le moteur tire
  d'un univers de la proposition (`calcul_notionnel`, `CalculNotionnel`,
  `FICHES_DU_MOTEUR`) n'est pas une règle du moteur : c'est la fabrique qui
  le tire, pour le paquet (`scripts/construire_donnees.py`) et pour la
  demande d'une étude. La note de décision 0006 garde la fabrique en
  Python ; le module passe donc de `scenarios/univers.py` à
  `noyau/calcul_notionnel.py`, à côté de `noyau/univers.py`, qui tient la
  pile. Ses deux importateurs suivent (`simulateur.py`,
  `construire_donnees.py`), et les mentions qui disent l'état présent :
  `noyau/univers.py`, `scenarios/notionnel.py`, `moteur/js/simulateur.js`,
  `data/CLAUDE.md` et la ligne de la table de l'architecture qui le nommait.
  Les récits qui citent l'ancien chemin restent tels quels.
- **`test_univers.py`** ne touche plus au simulateur Python :
  - le partage des comptes entre univers (2 et 3, 4 et 5) et le pilier
    réservé au scénario 6 se lisent sur le portage, dans
    `test_les_deux_moteurs_tirent_la_meme_chose_des_univers`, qui en vérifie
    désormais tout ce que le test Python vérifiait ;
  - une variante qui ne remplace aucun univers de la proposition est
    refusée par le portage, sous le pont (`pont.carrieres`), et non plus par
    `Simulateur(variantes=…)`. Que le portage prenne bien la variante à la
    place de son univers, `tests/js/univers.test.js` et
    `test_proposition_prospective.py` le tiennent déjà.

## Ce qui reste

- `test_effet_retour.py` attend que le coût cesse de lire le moteur Python.
- Les vagues 3 et 4 (`2026-11-15-les-temoins-sans-jumeau-et-l-inventaire.md`),
  la troisième commençant par `test_outre_mer.py` et
  `test_sections_juridiques.py`.
- `Simulateur.variantes` et `univers_de_la_demande` restent au simulateur
  Python, que `scripts/proposition_prospective.py` appelle encore ; ils
  partiront avec lui, l'étude passant alors `calcul_notionnel(…).donnees()`
  au pont elle-même.

**Tests.** `test_univers.py` et `test_fichiers_sur_le_moteur_python.py` :
verts ; `python -m pytest -m rapide` : vert (5 425 tests) ;
`test_proposition_prospective.py`, `test_carte_du_depot.py`,
`test_contrats.py` : verts ; le paquet refait est identique à l'octet.
