# L'arbre du dépôt, fichier par fichier

**Le 7 octobre 2026, à la demande du propriétaire** : « une liste de tous les
fichiers (un arbre du dépôt) avec pour chaque fichier le nombre de lignes et
de caractères », pour voir où sont les gros fichiers, et économiser enfin le
contexte.

- *Le script.* `python scripts/arbre.py` imprime l'arbre de ce que git suit,
  et de ce qu'un `git add -A` ajouterait : chaque fichier avec ses lignes et
  ses caractères, chaque dossier avec la somme des siens, chaque niveau du
  plus lourd au plus léger. Un dossier en argument, `--profondeur N` ou
  `--plus-gros N` n'en impriment qu'une part : l'arbre entier passe mille
  lignes. Un binaire donne ses octets ; une ligne de plus de dix mille
  caractères se signale, puisqu'un `grep` qui tombe dessus la rend entière.
  `tests/test_arbre.py` le tient, parmi les contrôles de l'outillage.
- *Aucun document.* Ces chiffres changent à chaque commit : comme le coût du
  travail, ils s'impriment à la demande, et `docs/architecture.md` (§ 9.3)
  nomme le script à côté de `tableau_de_bord.py --cout`. Un document que
  GitHub aurait refait à chaque envoi aurait été périmé, dans chaque session,
  dès sa première retouche, et aurait pesé lui-même 136 000 caractères.
- *Ce qu'il montrait ce jour-là.* 1 217 fichiers, dont 7 binaires, près de
  800 000 lignes et 49,5 millions de caractères. Près de la moitié tient en
  trois fichiers fabriqués : les témoins `pages.json` (9,9 millions) et
  `simulations.json` (9,2), et `moteur/donnees.json` (4,0), d'une seule
  ligne. Quatre fichiers ont une ligne démesurée : `moteur/donnees.json`, la
  police indexée d'Impeccable, `tests/temoins/pages.json` (766 761
  caractères) et `data/derive/equilibre.json`. Les plus lourds que la liste
  de `CLAUDE.md` (« ne se lisent jamais en entier ») ne nomme pas, outillage
  d'Impeccable à part : `data/reference/mortalite/quotients_periode.csv`,
  `data/reference/textes/redactions.csv`, `data/reference/referents.yaml`,
  `docs/limites.md`, `data/sources_a_explorer.yaml`,
  `src/retraite_notionnelle/cout.py`, `tests/test_cout.py` et
  `tests/test_web.py`, de 734 000 à 206 000 caractères.
