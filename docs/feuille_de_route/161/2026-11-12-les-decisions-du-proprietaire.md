# Les décisions du propriétaire du 12 novembre 2026 : les cinq questions tranchées, et l'ordre de la suite

**Ce qui est décidé.** Le propriétaire a répondu aux cinq questions de
l'inventaire du 9 novembre ; la note de décision 0007
(`docs/decisions/0007-les-arbitrages-du-retrait.md`) les porte, avec leurs
raisons.

1. *La zone grise* : l'impôt sur le revenu, le cœur de la revalorisation
   servie avec l'indexation, et la garantie de population en JavaScript
   seul, comme le recommandait la note de la question 1.
2. *Les tests du moteur Python* : la façade d'abord, comme le recommandait
   la note de la question 2.
3. *Les études* : les douze gardées, sauf la moitié Python de
   `budget_calcul.py`.
4. *La clôture* : par fonction, non par paire.
5. *La relecture* : allégée. Elle n'est plus un préalable au retrait, et ne
   vaut que pour `droit/releve.js`, `journal.js`, `droit/categories.js` et
   `fusion.js`. La note de la question 5 recommandait de relire toutes les
   paires à côté des autres lots ; le propriétaire a retenu ce que la
   session du jour lui proposait à la place. La relecture de la
   revalorisation servie et de l'indexation, que le bloc « Reprise »
   annonçait, n'est donc plus due : le test de confrontation que leur
   passage au pont écrit en tient lieu.

**Ce qui a précédé la décision.** La mesure de ce que le site calcule sans
le lecteur (`2026-11-12-ce-que-le-site-calcule-sans-le-lecteur.md`),
demandée par le propriétaire pour savoir s'il restait des calculs à garder
en Python : aucun.

**L'ordre de la suite**, une étape par session. Les étapes qui écrivent dans
le pont ou dans le coût se mènent une à la fois ; celles de la fabrique et
des études peuvent se mener à côté.

| étape | ce qu'elle fait | sa consigne |
|---|---|---|
| la garantie | sa confrontation, la demande au pont, le coût branché, `garantie.py` retiré | note de la question 1, session C1 |
| la façade | les huit entrées servies par le pont, dans un module à elles | note de la question 2, « L'ordre proposé » |
| les sondes | `mesures_prose.py` et `mesures_accueil.py` sans le moteur Python | inventaire, lot A |
| les études | `flux_fonction_publique.py`, puis les autres à porter | note de la question 3 |
| l'impôt | la demande au pont par année, l'effet retour branché | note de la question 1, session C2 |
| la revalorisation servie | le cœur et l'indexation au pont, leur confrontation | note de la question 1 |
| les tests | ceux qui appellent une règle directement, fichier par fichier | note de la question 2 |
| les quatre fichiers peu éprouvés | relus, ou figés par des témoins | `2026-11-12-les-lignes-du-portage-sans-test.md` |
| le retrait | les règles du moteur Python, d'un bloc | inventaire, lot F |
| la clôture | le test de la carte, par fonction | note de la question 4 |

Aucun code ne change dans cette étape : la note de décision, la table « Où
va quoi » de l'architecture, les consignes de `src/` et de `moteur/`, une
version de l'architecture et le bloc « Reprise ».
