# Le contexte, étape 4 : les lignes géantes

**Reprise, au 7 octobre 2026.** Attend le verdict de l'étape 1 : à faire si la
mesure montre des `grep`, des `sed` ou des diffs tombés sur ces lignes.
`moteur/donnees.json` tient sur une ligne de 4 millions de caractères,
`data/derive/equilibre.json` sur une de 55 000 ; dans
`tests/temoins/pages.json`, le HTML de chaque page tient sur une ligne, 63 de
plus de 10 000 caractères, jusqu'à 767 000. Les écrire une entrée par ligne,
et chaque page ligne à ligne : le diff d'un témoin montrera les lignes
changées d'une page, et non la page entière. Détail : ce fichier.

**Le 7 octobre 2026, ce qui est établi.**

- *Qui les écrit.* `scripts/construire_donnees.py` : `construire_bilan` pour
  `data/derive/equilibre.json`, `construire` pour `moteur/donnees.json`, tous
  deux par `json.dumps(…, sort_keys=True, separators=(",", ":"))`, sur une
  seule ligne. `moteur/donnees.json` est un objet de 90 clés, que le site
  charge par `fetch` puis `JSON.parse` (`index.html`) : des retours à la ligne
  ne lui changent rien. Les pages : `scripts/construire_temoins.py`, qui range
  le HTML de chacune dans une chaîne `corps` ; la lisent aussi
  `tests/test_affirmations.py` et `tests/test_outillage.py` (chercher `corps`
  partout avant de changer sa forme).
- *Ce qui est déjà protégé.* L'outil Grep omet les lignes trop longues (essayé
  le 7 octobre, étape 2). Restent le `grep`, le `sed` et le `cat` lancés par
  Bash, et `git diff` ou `git show`, que `CLAUDE.md` interdit sur un témoin sans
  pouvoir l'empêcher.

**Le plan.**

1. Un écrivain JSON compact qui passe à la ligne entre les éléments des deux
   premiers niveaux, sans indentation : le paquet ne grossit que d'un octet par
   élément. Le même pour le bilan.
2. Le témoin des pages : `corps` devient la liste de ses lignes, que ses
   lecteurs rejoignent ; `--verifier` reste à l'octet.
3. `python scripts/regenerer.py`, puis `python scripts/resumer_temoins.py` :
   aucune simulation ne bouge, seule la forme. Le poids du site, que la prose
   cite (sonde `poids` de `verifier_prose.py`), bouge de quelques octets, et
   GitHub le recalcule.

*Les pièges.* `.gitattributes` déclare ces fichiers fabriqués (`-merge`) : rien
à y changer. Vérifier qu'aucun lecteur, en Python comme dans le portage, ne
compare le texte brut plutôt que l'objet qu'il décode.

En finissant, la session ôte le bloc « Reprise » de cette note, et ne touche
à celui de l'action que si elle est la dernière des cinq étapes.
