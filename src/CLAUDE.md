# Consignes de `src/` : le modèle

Claude Code les charge à la première lecture d'un fichier de `src/`, en plus
de `CLAUDE.md`. Le modèle a son portage dans `moteur/js/` et ses données dans
`data/`, qui ont leurs consignes. Ne s'écrivent pas ici : le texte du site,
qui s'écrit en JavaScript (`moteur/CLAUDE.md`), ni une variante de la
proposition, qui s'écrit en couche (`data/CLAUDE.md`).

- **Le Python de `src/` fait foi.** Toute modification du modèle se porte
  dans `moteur/js/`. Après elle, ou après toute modification des données,
  `python scripts/regenerer.py` refait tout ce qu'un script fabrique — le
  paquet, les témoins, le chiffrage, les tableaux, le tableau de bord, les
  chiffres ancrés —, dans l'ordre (`--verifier` dit ce qui est périmé sans
  rien écrire) ; `python scripts/resumer_temoins.py` dit ce qu'elle déplace,
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
  l'empreinte du modèle — `src/` et `data/`, hors de ce qu'aucun calcul ne
  lit (`HORS_DU_MODELE`, que `scripts/lectures_du_modele.py` relève) — et,
  pour un calcul écrit dans un script ou un test, de son code, un seul
  processus faisant chaque calcul pendant que les autres l'attendent
  (`CALCULS_SANS_MEMOIRE=1` s'en passe) et ne sert que sur le modèle intact :
  qui en remplace une fonction s'ouvre sous `memoire.modele_modifie()`, et
  `monkeypatch` la fait taire. `SerieAnnuelle` et
  `Carriere` sont immuables après leur constructeur : un champ réassigné
  après coup casserait leurs mémoires sans bruit.

## Liste de contrôle

- **Un changement du modèle** : le Python d'abord, puis son jumeau ;
  `python scripts/regenerer.py`, puis `python scripts/resumer_temoins.py`, pour
  voir ce qu'il déplace ; `-m rapide` et les tests de sa zone, puis le commit.
