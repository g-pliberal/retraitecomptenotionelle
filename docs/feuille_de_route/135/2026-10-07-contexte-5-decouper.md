# Le contexte, étape 5 : découper les gros fichiers les plus lus

**Reprise, au 7 octobre 2026.** Attend le verdict de l'étape 1, qui dira quels
gros fichiers les sessions lisent vraiment, et combien de fois. Candidats au
7 octobre, hors de la liste de `CLAUDE.md` : `data/reference/referents.yaml`
(473 000 caractères), `docs/limites.md` (305 000),
`data/sources_a_explorer.yaml` (267 000), `src/retraite_notionnelle/cout.py`
(229 000), `tests/test_cout.py` (226 000), `tests/test_web.py` (206 000). Ne
découper que ce que la mesure désigne, un fichier par session, et une seule
session à la fois qui déplace des fichiers (`CLAUDE.md`, « Rien ne se perd »).
Détail : ce fichier.

**Le 7 octobre 2026, ce que chaque découpage paierait.**

- *Un module du modèle* (`cout.py`, `droit/liquider.py` 186 000 caractères,
  `scenarios/actuel.py` 156 000) : ses imports, son jumeau de `moteur/js/` si
  le portage suit le même découpage, et la mémoire des calculs, indexée sur
  `src/`, qui se refait une fois.
- *Un fichier de tests* (`test_cout.py`, `test_web.py`, `test_donnees.py`
  164 000) : son niveau dans `tests/conftest.py`, que `tests/test_niveaux.py`
  tient, et son poids dans `POIDS_REPARTI`
  (`src/retraite_notionnelle/pytest_parallele.py`).
- *Un document* (`docs/limites.md`, `docs/methodologie.md` 191 000) : son
  régime dans `data/reference/prose/zones.yaml`, ses chiffres ancrés, et la
  conservation (`python scripts/conservation.py --depuis HEAD`).
- *Un registre* (`referents.yaml`, `sources_a_explorer.yaml`) : les
  identifiants de ses entrées, que la conservation tient (`REGISTRES`, dans
  `scripts/conservation.py`), et tous ses lecteurs.

Un découpage ne rapporte que si les sessions lisaient le fichier entier, ou en
lisaient beaucoup de fenêtres : une session qui cherche puis lit par fenêtre
paie déjà peu. C'est ce que l'étape 1 tranchera.

En finissant, la session ôte le bloc « Reprise » de cette note, et ne touche
à celui de l'action que si elle est la dernière des cinq étapes.
