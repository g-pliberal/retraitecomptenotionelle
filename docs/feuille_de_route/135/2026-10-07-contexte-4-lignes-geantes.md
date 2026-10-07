# Le contexte, étape 4 : les lignes géantes

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

**Le 7 octobre 2026, ce qui est fait.** Sur la demande du propriétaire, sans
attendre le verdict de l'étape 1. Le plan, à une correction près, que la mesure
a imposée.

- *Deux niveaux ne suffisaient pas.* Passé à la ligne entre les éléments de
  ses deux premiers niveaux, le paquet gardait 62 lignes de plus de 10 000
  caractères, dont 57 régimes entiers, jusqu'à 156 000 pour la complémentaire
  de la CARMF. Et une page coupée à ses seuls retours à la ligne en gardait
  152, jusqu'à 424 000 : les six pages Coût écrivent leurs panneaux, frises et
  tableaux d'un seul tenant. La coupe suit donc la taille, non la profondeur.
- *L'écrivain*, `src/retraite_notionnelle/lignes.py`. `json_en_lignes` écrit
  le JSON compact, clés triées, et passe à la ligne, sans indentation, entre
  les éléments de tout objet ou tableau de plus de 300 caractères
  (`LARGEUR`), en descendant ; ce qui tient reste entier, et ôter ses retours
  à la ligne redonne le JSON compact à l'octet. `html_en_morceaux` garde une
  page ligne à ligne, coupe une ligne trop longue entre ses éléments, et un
  élément trop long entre ses enfants ; une balise ou un texte ne se coupent
  pas, et la concaténation des morceaux redonne la page. Les coupes ne
  dépendent que du contenu : un chiffre qui change ne déplace que sa ligne.
  Trois cents caractères : chaque année du bilan y tient, et neuf lignes de
  tableau du site sur dix, quand deux cents en coupaient plus d'une sur
  trois. Fabriquer le paquet prend moins d'une seconde de plus, sur
  cinquante ; les témoins, une demi-seconde, sur soixante-quinze.
- *Les fichiers.* Le paquet passe d'une ligne à 130 295, dont la plus longue,
  5 957 caractères, est une chaîne : toute ligne de plus de 330 caractères
  n'en porte qu'une. Il grossit de 3,2 %, de 4 065 348 octets à 4 195 642, et
  de 1,9 % compressé. Le bilan tient en 741 lignes, de 182 caractères au plus.
  Dans le témoin des pages, `corps` devient la liste des morceaux, 115 642
  pour les 74 pages, en 117 484 lignes, dont la plus longue, 5 135
  caractères, est un tracé SVG ; le fichier grossit de 7,9 %, de 10 248 081
  octets à 11 057 723. Ses lecteurs le recousent : `tests/js/moteur.test.js`,
  `test_affirmations.py`, et `resumer_temoins.py`, pour qui une page en une
  chaîne et la même en morceaux sont le même rendu. Le paquet et le bilan,
  eux, n'avaient aucun lecteur de leur texte brut : tous les décodent, en
  Python comme sous node. `scripts/arbre.py` ne signale plus aucune de ces
  lignes, et `tests/test_lignes.py`, dans la suite rapide, le dirait si l'une
  revenait.
- *Rien n'a bougé que la forme.* Le paquet et le bilan se relisent en objets
  identiques, chaque page recousue est celle d'avant à l'octet, et
  `resumer_temoins.py` ne voit bouger aucun témoin ni changer aucune page. Le
  poids du site, que le README cite sous sonde, prend les 127 Ko du paquet,
  6 Ko compressés. `.ignore` garde les trois fichiers hors des recherches
  larges ; nommés, ils ne rendent plus que des lignes courtes. Ce que
  l'étape rapporte, seul le relevé du poste le dira (étape 1) : combien de
  `grep`, de `sed` et de diffs tombaient sur ces lignes.
