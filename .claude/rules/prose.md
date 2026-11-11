---
paths:
  - "/README.md"
  - "CLAUDE.md"
  - ".claude/rules/**"
  - "docs/**"
  - "data/reference/prose/**"
---

# Règle de la prose : les documents, leurs chiffres, leur conservation

Claude Code charge cette règle à la première lecture ou écriture d'un
document — `README.md`, un `CLAUDE.md`, une règle de `.claude/rules/`, un
fichier de `docs/` — ou du zonage, `data/reference/prose/`, en plus de
`CLAUDE.md`. Ce qu'une étape écrit de sa documentation, et où :
`documentation.md`.

- **La prose** : chaque document a son régime, déclaré dans
  `data/reference/prose/zones.yaml` — `etat` (tout chiffre y est ancré sur une
  sonde), `recit` (vrai à sa date, gelé), `produit` ou `tenu` (par le test
  qu'il nomme, et lui seul) —, et ce qui s'en écarte s'y déclare un à un
  (`docs/fraicheur.md`). Un récit ne s'écrit pas au milieu d'un état : il va
  dans la feuille de route ou une archive. Après toute modification de la
  prose : `python scripts/verifier_prose.py --corriger`. Les tableaux de
  `docs/chiffrage_plf.md` s'écrivent par `python scripts/chiffrage_plf.py`,
  jamais à la main.
- **Rien ne se perd** (`docs/architecture.md`, § 12) : un récit ne se réécrit
  pas, et un déplacement de fichiers se vérifie avant d'être commité, par
  `python scripts/conservation.py --depuis HEAD`. Une seule session déplace
  des fichiers à la fois. À la fin de chaque domaine, la référence du test de
  conservation (`tests/temoins/conservation.json`) se refige, pour protéger
  les récits nés depuis : `python scripts/conservation.py --figer`, qui refuse
  s'il y a une perte.
- **Les conflits du rebasage.** `pousser.sh` règle seul, au rebasage, ce que
  les scripts écrivent : un fichier marqué `-merge` dans `.gitattributes`
  garde la version de `main` ; un conflit de prose qui ne porte que sur des
  chiffres ancrés (`<!--chiffre:…-->`) ou des blocs produits garde la valeur
  de `main` ; la référence de la conservation se fusionne par ensembles
  (`scripts/fusionner.py`, action 148, étape 3). Un conflit sur ce qui s'écrit
  à la main reste à résoudre ; à la main, un conflit d'ancres garde UN côté,
  jamais les deux, puis `python scripts/verifier_prose.py --corriger`.
