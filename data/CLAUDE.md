# Consignes de `data/` : les données et la certification

Claude Code les charge à la première lecture d'un fichier de `data/`, en plus
de `CLAUDE.md`. Une donnée modifiée déplace des résultats :
`python scripts/regenerer.py` refait ce qu'un script en fabrique, et
`python scripts/resumer_temoins.py` dit ce qui a bougé (`src/CLAUDE.md`). Une
règle du scénario 1 ne s'écrit qu'en suivant `docs/veille_droit.md`.

- **Les données** sont dans `data/`. Tous les régimes, calculés ou non : un
  fichier par régime dans `data/reference/regimes/`, qui porte sa ligne
  d'inventaire ; `inventaire.yaml`, qui les énumère, s'en fabrique par
  `python scripts/construire_inventaire.py`. L'histoire des règles :
  `reformes.yaml` et `pivots.yaml` ;
  `python scripts/calendrier_regimes.py --regime X` dit ce qu'une fiche ne
  coupe pas, `--carte` imprime le tableau des jeux de règles, et toute
  réforme qui touche un régime est coupée, absorbée ou déclarée
  `non_appliquee`.
- **La proposition** : ses scénarios sont des univers de droit
  (`data/reference/univers/`), piles de couches (`data/reference/couches/`)
  posées sur le droit réel ; ce qu'elles ajoutent a sa fiche dans
  `data/reference/regles/proposition/`, qui cite le README. Une variante
  s'écrit en couche, jamais dans le code, et le moteur refuse ce qu'il ne
  sait pas calculer (`scenarios/univers.py`).
