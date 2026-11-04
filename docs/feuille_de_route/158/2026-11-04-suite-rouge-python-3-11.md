# La suite de GitHub rouge sous Python 3.11 (file B3-quater)

**La cause.** À la course du 3 novembre 2026, 23 h 36 UTC, `tests/test_chainage_grilles.py`
ne s'importait plus sur GitHub : `scripts/fetch/dila_legi_chainage.py`, ligne 170, portait
une barre oblique inverse dans l'expression d'une f-string
(`rf"{r'1(?:\s*er)?' if jour == 1 else jour}…"`). Python 3.12 (PEP 701) l'accepte, 3.11 —
celui de `tests.yml` — et 3.10 — le plancher de `requires-python` — la refusent
(`SyntaxError: f-string expression part cannot include a backslash`). La suite des
sessions, sous 3.13, restait verte.

**La correction.** Le motif brut passe dans une variable, `premier`, avant la f-string ;
la fonction rend la même chaîne, vérifiée avant et après sur six dates dont trois premiers
du mois. Aucune garde touchée, `tests.yml` reste en 3.11.

**Le test.** `tests/test_syntaxe_ancien_python.py`, de la suite rapide. Il compile les
`.py` de `scripts/`, `src/`, `tests/`, `moteur/`, `docs/` et `.claude/` avec le plus ancien
Python de la machine (`python3.10` ou `python3.11`, ou celui qui court s'il est antérieur à
3.12) : vu rouge avant la correction, seul ce fichier fautif. Faute d'ancien interprète, il
saute ; un second test, valable sous 3.12 et plus, cherche alors dans l'arbre toute
f-string dont une expression porte une barre oblique inverse (`ast.feature_version`, lui,
n'oppose rien à 3.12 : il accepte la faute). Ce second test est plus étroit : il ne voit
pas les autres nouveautés de 3.12, comme les guillemets réemployés dans une expression.
