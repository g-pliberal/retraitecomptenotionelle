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
  jusqu'à refaire chaque nombre des témoins au bit près — les témoins, que le
  portage calcule (`scripts/construire_temoins.py`), le confrontent
  (`tests/test_pont.py`, les tests du moteur Python qui les « refait »), et
  un témoin de plus couvre la règle quand la confrontation ne rougit pas sans
  lui. Le Python ne cesse de suivre qu'au retrait de sa paire (action 161) :
  le coût date, bâtit et simule sa grille au portage, la table y date ses
  carrières types, le coût des avantages y date, bâtit et liquide la sienne,
  sous ses scénarios neutralisés, la grille large s'y date et s'y bâtit, et
  ses mesures s'y lisent, comme le coût sous un modèle modifié, ses variantes
  écrites en données ; mais les confrontations refont au jumeau ce que le
  portage calcule, et une règle portée d'un seul côté rougirait la suite ou
  les ferait mentir.
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
  elle, ou après toute modification des données, la session refait ce que
  ses tests lisent, et cela seul : le paquet
  (`python scripts/construire_donnees.py`), puis les témoins
  (`python scripts/construire_temoins.py`) ; si un test de la suite rapide ou
  de sa zone réclame un autre fichier fabriqué, elle refait celui-là, par son
  script. `python scripts/regenerer.py`
  refait tout ce qu'un script fabrique — le paquet, les témoins, le
  chiffrage, les tableaux, le tableau de bord, les chiffres ancrés —, dans
  l'ordre (`--verifier` dit ce qui est périmé sans rien écrire) : GitHub le
  lance après chaque envoi (`CLAUDE.md`, « Les fichiers fabriqués et la suite
  complète sont à GitHub »), et une session ne le lance pas avant le sien ;
  `python scripts/resumer_temoins.py` dit ce qu'elle déplace,
  scénario par scénario, et le diff des témoins, chiffre par chiffre. Une
  étape dont rien n'a bougé ne se relance pas, et la suite ne revérifie pas
  ce qu'elle vient de fabriquer (`.cache/fabrique.json`, que
  `FABRIQUE_SANS_MEMOIRE=1` ignore) ; GitHub, sans mémoire, refait tout.
- **Ce qui reste en Python** (note de décision 0006) : la fabrique des
  données — acquérir, certifier, lire le YAML, fabriquer le paquet —, ce qui
  calcule une population, un agrégat ou une étude sous les réglages de
  référence, ce qui fait tourner node, la carte des règles et ses contrats,
  les tests et l'outillage ; et, dans chaque jumeau du moteur, ses chargeurs
  du paquet et les types que le pont échange (`Parametres`, `Carriere`,
  `AnneeCarriere`, `DateMois`…). Les accesseurs qui lisent le YAML pour la
  fabrique, le coût ou les études restent ici. Un calcul agrégé que le coût
  fait et que le site refait ne s'écrit qu'en JavaScript si le lecteur peut
  en changer le résultat — le coût le demande alors au pont, en une fois
  pour toutes ses années et ses cohortes —, et qu'ici sinon, son résultat
  figé au paquet, à deux conditions : le site n'affiche que ce que la
  fabrique calcule déjà, et le calcul n'appelle aucune règle du moteur. La
  note de décision 0007 range ainsi en JavaScript l'impôt sur le revenu, la
  revalorisation servie et la garantie de population ; elle dit aussi que le
  retrait d'une paire n'attend plus sa relecture.
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
  qui en remplace une fonction du coût ou d'une étude s'ouvre sous
  `memoire.modele_modifie()`, et `monkeypatch` la fait taire ; une fonction
  du moteur, que le portage ne voit pas, ne se remplace pas : sa variante
  s'écrit en données (note de décision 0006). Seules les confrontations,
  déclarées une à une dans `tests/test_pont.py`
  (`CONFRONTATIONS_DU_JUMEAU`), s'ouvrent sous `pont.par_le_jumeau()`, qui
  fait aussi calculer le jumeau. `SerieAnnuelle` et
  `Carriere` sont immuables après leur constructeur : un champ réassigné
  après coup casserait leurs mémoires sans bruit.

## Liste de contrôle

- **Un changement du moteur d'une carrière** : le test d'abord, vu rouge —
  l'exemple publié de la règle, s'il existe
  (`tests/temoins/exemples_officiels.yaml`), sinon un cas posé à la main
  depuis le texte —, sur le portage : un essai de `tests/js/`, ou un test qui
  le fait tourner par le pont ; le JavaScript, jusqu'au vert ;
  `python scripts/construire_temoins.py`, qui fait calculer les témoins au
  portage ; puis son jumeau Python, s'il en a un
  (`python scripts/jumeaux.py <nom>`) : sa confrontation aux témoins vue
  rouge (`python -m pytest tests/test_pont.py -k refait`), au besoin par un
  témoin de plus, le Python porté ligne pour ligne, la confrontation verte,
  au bit près ; un nombre nouveau du résultat (`dictionnaire()`) déclare son
  type dans la table de `pont.py` (`ENTIERS_DU_RESULTAT`,
  `FLOTTANTS_DU_RESULTAT`). Ce qui n'a pas de jumeau — le coût, les carrières
  types — s'écrit en Python seul, son test d'abord. Puis le
  paquet et les témoins, une fois chacun (`python scripts/construire_donnees.py`,
  `python scripts/construire_temoins.py`), et
  `python scripts/resumer_temoins.py`,
  pour voir ce qu'il déplace ; `-m rapide` et les tests de sa zone, puis le
  commit. Le reste de la fabrique — l'accueil, le chiffrage, les tableaux, les
  pages, le tableau de bord, les chiffres ancrés — est à GitHub :
  `regenerer.py` ne se lance pas avant l'envoi.
  Les tests de sa zone comptent les confrontations légères, sept secondes
  sans mémoire : `python -m pytest tests/test_oracle.py tests/test_destinie.py
  tests/test_estimation_officielle.py tests/test_verification.py` ; elles ont
  rougi `main` quatre fois du 6 au 17 octobre 2026 (action 163, garde 4).
  L'estimation officielle et Destinie 2 y éprouvent le portage
  (`pont.scenario_actuel`), et y font refaire au moteur Python, au bit près,
  chaque cas qu'il sert (`servi_et_refait`, `tests/outils_pont.py`) ; les
  exemples d'OpenFisca et des caisses passent au pont, fonction par fonction,
  par `pont.droit` (action 161). Le
  coût et ses confrontations (`test_cout.py`, `test_facteurs_depense.py`,
  `test_affirmations.py` : huit minutes sans mémoire) restent à GitHub.
- **Un retrait de jumeau** (action 161) : la méthode des notes de décision
  0003 et 0005, de `python scripts/jumeaux.py <nom>` aux dépendants branchés
  sur le portage ; puis, dans un commit à lui, le fichier coupé (note 0006) :
  les règles partent ; les chargeurs passent sous `donnees/`, sans méthode de
  règle ; les types du pont restent ; une étude qui appelait une fonction du
  moteur hors du simulateur la demande au pont, par lot, et celle qui en
  remplaçait une le temps d'une variante l'a d'abord écrite en données, une
  couche ou un paramètre de la demande. Le paquet refait
  (`python scripts/construire_donnees.py`) reste identique à l'octet, comme
  les témoins et les agrégats.
- **Un défaut corrigé dans une règle** : la classe, pas le cas. Avant le
  commit, chercher la même erreur dans les autres régimes et les autres
  générations, et la corriger avec lui ou l'inscrire à la feuille de route
  (action 163, étape 4).
