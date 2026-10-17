# Version du 17 octobre 2026 : le test d'abord

Le dépôt se développe piloté par les tests, à la demande du propriétaire
(« Sur ce dépôt, je veux utiliser le TDD ») : tout changement de
comportement commence par le test qui le dit, vu échouer pour la raison
attendue, puis vient le code qui le fait passer, puis le remaniement (§ 10).
La valeur attendue vient de la source, jamais du code ; un témoin refait par
un script n'en tient pas lieu ; test et code se commitent ensemble, au vert,
et `main` ne reçoit jamais de rouge. Un hook de Claude Code,
`.claude/hooks/tdd.py`, refuse une fois par commit la première retouche du
code — `src/`, `moteur/`, `scripts/`, `.claude/hooks/` — tant que pytest n'a
vu échouer aucun test en train de s'écrire, ce que `tests/conftest.py` lui
note ; refaite telle quelle, elle passe, un remaniement n'ayant pas de test
neuf (action 162).
