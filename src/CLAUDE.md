# Consignes de `src/` : le modèle

Claude Code les charge à la première lecture d'un fichier de `src/`, en plus
de `CLAUDE.md`. Le moteur d'une carrière fait foi dans `moteur/js/`, dont
`src/` garde des jumeaux jusqu'à leur retrait ; le coût n'est qu'ici, et les
données sont dans `data/`, qui ont leurs consignes. Ne s'écrivent pas ici : le
texte du site, qui s'écrit en JavaScript (`moteur/CLAUDE.md`), ni une variante
de la proposition, qui s'écrit en couche (`data/CLAUDE.md`).

- **Le JavaScript de `moteur/js/` fait foi pour chaque étape du moteur qui a
  encore son jumeau ici** (principe 4, notes de décision 0003 et 0005) : une
  règle nouvelle ou modifiée s'y écrit d'abord, avec son test tiré de la
  source ; son jumeau Python la suit dans le même commit, ligne pour ligne,
  jusqu'à rendre chaque nombre des témoins au bit près — la concordance
  (`tests/js/moteur.test.js`) en est le test, et un témoin de plus
  (`scripts/construire_temoins.py`) couvre la règle quand la concordance ne
  rougit pas sans lui. Le Python ne cesse de suivre qu'au retrait de sa paire
  (action 161) : tant que les témoins se simulent au moteur Python et que le
  coût bâtit et date ses carrières par lui, une règle portée d'un seul côté
  rougirait la suite ou ferait mentir le coût.
  `python scripts/jumeaux.py <nom>` dit si une étape a son jumeau et tout ce
  qui en dépend. Un code neuf
  s'écrit une fois, dans le langage de l'endroit où il tourne : ici, ce que
  seule la fabrique calcule, comme le coût, qui ne se calcule qu'ici : le
  coût agrégé, celui des avantages, les carrières types et leurs départs,
  que `scripts/construire_donnees.py` fige sous les réglages de référence
  dans la table du paquet (`data/derive/agregats.json`), par les écrivains
  de `donnees/agregats.py`, et que lisent les accesseurs de
  `moteur/js/agregats.js`, ses seuls lecteurs : ceux du Python sont partis
  (note de décision 0005), et aucun ne s'y ajoute. Après
  elle, ou après toute modification des données, `python scripts/regenerer.py`
  refait tout ce qu'un script fabrique — le paquet, les témoins, le
  chiffrage, les tableaux, le tableau de bord, les chiffres ancrés —, dans
  l'ordre (`--verifier` dit ce qui est périmé sans rien écrire) ;
  `python scripts/resumer_temoins.py` dit ce qu'elle déplace,
  scénario par scénario, et le diff des témoins, chiffre par chiffre. Une
  étape dont rien n'a bougé ne se relance pas, et la suite ne revérifie pas
  ce qu'elle vient de fabriquer (`.cache/fabrique.json`, que
  `FABRIQUE_SANS_MEMOIRE=1` ignore) ; GitHub, sans mémoire, refait tout.
- **Les temps tiennent à des mémoires** qu'il ne faut pas contourner :
  `charger_yaml` (qui rend une copie), `charger_serie_annuelle` et la table
  des quotients de mortalité, indexées sur la signature du fichier, partagées
  et jamais modifiées ; le temps d'un calcul, les chargeurs marqués
  `une_fois_par_instantane` ne regardent le disque qu'une fois
  (`chargement.instantane`), un `stat` coûtant cher sous Windows ; les lois
  de mortalité calibrées, gardées dans
  `data/derive/calibrations_mortalite.json` et reprises seulement si
  l'empreinte de leurs entrées est celle du jour ; le coût agrégé, ses
  variantes et le coût des avantages, que `memoire.py` garde dans le
  `.cache/calculs/` du dépôt principal, commun à tous ses worktrees, sous
  l'empreinte du modèle — `src/` et `data/`, et le portage par lequel le coût
  simule sa grille, `moteur/js` hors des pages et la fabrique du paquet du
  jour, hors de ce qu'aucun calcul ne lit (`HORS_DU_MODELE`, que
  `scripts/lectures_du_modele.py` relève) — et,
  pour un calcul écrit dans un script ou un test, de son code, un seul
  processus faisant chaque calcul pendant que les autres l'attendent
  (`CALCULS_SANS_MEMOIRE=1` s'en passe) et ne sert que sur le modèle intact :
  qui en remplace une fonction s'ouvre sous `memoire.modele_modifie()`, et
  `monkeypatch` la fait taire. `SerieAnnuelle` et
  `Carriere` sont immuables après leur constructeur : un champ réassigné
  après coup casserait leurs mémoires sans bruit.

## Liste de contrôle

- **Un changement du moteur d'une carrière** : le test d'abord, vu rouge —
  l'exemple publié de la règle, s'il existe
  (`tests/temoins/exemples_officiels.yaml`), sinon un cas posé à la main
  depuis le texte —, sur le portage : un essai de `tests/js/`, ou un test qui
  le fait tourner par le pont ; le JavaScript, jusqu'au vert ; puis son
  jumeau Python, s'il en a un (`python scripts/jumeaux.py <nom>`) : la
  concordance des témoins vue rouge, au besoin par un témoin de plus, le
  Python porté ligne pour ligne, `python scripts/construire_temoins.py`, la
  concordance verte, au bit près ; un nombre nouveau du résultat
  (`dictionnaire()`) déclare son type dans la table de `pont.py`
  (`ENTIERS_DU_RESULTAT`, `FLOTTANTS_DU_RESULTAT`), que `tests/test_pont.py`
  confronte aux témoins. Ce qui n'a pas de jumeau — le coût, les carrières
  types — s'écrit en Python seul, son test d'abord. Puis
  `python scripts/regenerer.py`, et `python scripts/resumer_temoins.py`,
  pour voir ce qu'il déplace ; `-m rapide` et les tests de sa zone, puis le
  commit.
  Les tests de sa zone comptent les confrontations légères, sept secondes
  sans mémoire : `python -m pytest tests/test_oracle.py tests/test_destinie.py
  tests/test_estimation_officielle.py tests/test_verification.py` ; elles ont
  rougi `main` quatre fois du 6 au 17 octobre 2026 (action 163, garde 4). Le
  coût et ses confrontations (`test_cout.py`, `test_facteurs_depense.py`,
  `test_affirmations.py` : huit minutes sans mémoire) restent à GitHub.
- **Un défaut corrigé dans une règle** : la classe, pas le cas. Avant le
  commit, chercher la même erreur dans les autres régimes et les autres
  générations, et la corriger avec lui ou l'inscrire à la feuille de route
  (action 163, étape 4).
