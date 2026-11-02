# La note de décision 0006 : ce qui reste en Python, décidé par le propriétaire

**La demande.** Le 2 novembre 2026, le propriétaire répond « oui » aux trois
points que la note « Ce qui reste en Python » lui soumettait : faire de la
frontière une note de décision, le critère de la zone grise, le rangement
sous `donnees/` des chargeurs sortis des jumeaux.

**La décision.** La note 0006 (`docs/decisions/0006-ce-qui-reste-en-python.md`)
précise la règle de l'endroit, fonction par fonction, sans la récrire. Le
Python ne disparaît pas : la fabrique des données, ce qui calcule une
population, un agrégat ou une étude, ce qui fait tourner node, la carte des
règles, les tests et l'outillage y restent, et, de chaque jumeau du moteur,
ses chargeurs du paquet et les types du pont. Un retrait coupe le fichier :
les règles partent ; les chargeurs passent sous `donnees/`, sans méthode de
règle ; les types restent, un exemplaire par langage ; une étude demande au
pont, par lot, ce qu'elle appelait du moteur, et écrit en données la
variante qui en remplaçait une fonction ; `moteur/donnees.json` reste
identique à l'octet. Un calcul agrégé que le coût fait et que le site refait
ne s'écrit qu'en JavaScript si le lecteur peut en changer le résultat, qu'en
Python sinon, figé au paquet ; le propriétaire tranche chaque paire à sa
relecture.

**Où elle s'écrit.** En six endroits, comme la note le dit : la note ; le
principe 4, qui gagne une phrase, le § 7.1, qui gagne le paragraphe « Ce qui
reste en Python », et la table « Où va quoi », dont la ligne du retrait se
précise et qui gagne celle du calcul agrégé (`docs/architecture.md`) ; la
carte du dépôt, sa ligne « Modèle » et son entrée « Jumeaux » ; les
consignes de `src/` — le point « Ce qui reste en Python » et la liste « Un
retrait de jumeau » — et de `moteur/`, deux phrases de leur ouverture ; la
version de l'architecture `2026-11-02-ce-qui-reste-en-python.md` ; le bloc
« Reprise ».

**Ce qui ne change pas.** Aucun code, aucune donnée, aucune garde, aucune
règle du scénario 1, aucune dépendance, aucun chiffre ancré ; la règle de
l'endroit, les six conditions du pont et les six temps de la méthode.

**Tests.** `python scripts/verifier_prose.py --corriger` ; les tests de la
prose, de la carte du dépôt, de l'outillage, de la conservation, des
jumeaux et de l'envoi, 176 ; celui du journal de veille ; la suite rapide.

**Ce qui suit.** Le coût sous un modèle modifié : les trois études qui
remplacent une fonction du moteur Python (`solde_fusion.py`,
`proposition_prospective.py`, `stock_age_legal.py`) écrivent leur variante
en données ; puis les retraits, chacun coupant son fichier.
