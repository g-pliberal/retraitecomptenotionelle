# Note de décision 0007 — les arbitrages du retrait du moteur Python

*Décidée le 12 novembre 2026 par le propriétaire, qui a tranché les cinq
questions de l'inventaire du 9 novembre
(`docs/feuille_de_route/161/2026-11-09-l-inventaire-des-retraits.md`),
chacune instruite dans une note `2026-11-12-question-<n>-…` du même dossier.
Il a suivi la recommandation des quatre premières, et allégé la relecture,
contre celle de la cinquième. Elle précise le critère de la note 0006 et
amende le troisième temps de la méthode de la note 0003.*

## Le problème

L'inventaire comptait de 36 à 49 sessions pour finir l'action 161, dont 12 à
14 pour relire 35 paires avant tout retrait, et 8 à 15 pour les 1 475 tests
qui n'éprouvent que le moteur Python. Tant que ce moteur existe, chaque règle
s'écrit deux fois. Cinq questions retenaient la suite : ce que deviennent les
calculs que le coût fait en Python et que le site refait, comment porter les
tests, quelles études garder, quand dire l'action close, et si la relecture
se mène à côté des autres lots.

## La décision

### La zone grise : en JavaScript seul

L'impôt sur le revenu, le cœur de `RevalorisationServie` avec `Indexation`,
et la garantie de population s'écrivent en JavaScript seul ; le coût les
demande au pont, par lot. L'histoire du droit que `RevalorisationServie`
porte sans jumeau reste en Python, au coût. La restitution part avec le
moteur, sans pont : aucun Python de production ne l'appellera plus. Les
variantes des comptes restent des deux côtés, déclarées tenues.

Le critère de la note 0006 se précise ainsi. Une question le précède : le
moteur parti, un Python de production appelle-t-il encore le calcul ? Sinon,
il part avec le moteur. Il se pose par fonction, non par fichier. Et sa
seconde branche se borne : un calcul agrégé reste en Python seul, son
résultat figé au paquet, si le site n'affiche que ce que la fabrique calcule
déjà et si le calcul n'appelle aucune règle du moteur ; en JavaScript seul
sinon. La mesure du 12 novembre
(`161/2026-11-12-ce-que-le-site-calcule-sans-le-lecteur.md`) n'a trouvé aucun
autre calcul du site à figer.

### Les tests : la façade d'abord

Huit entrées du moteur Python — `simuler`, `calculer`, `reversion` et les
bâtisseurs de carrière — gardent leurs noms et sont servies par le pont,
dans un module à elles. Les tests qui n'entrent que par là passent sans être
touchés ; ceux qui appellent une règle directement se portent ensuite,
fichier par fichier (`161/2026-11-12-question-2-la-methode-des-tests.md`).

### Les études : gardées

Les douze études restent, sauf la moitié Python de `budget_calcul.py`, qui
part avec le moteur ; celles qui entrent encore dans le moteur Python
passent par le pont (`161/2026-11-12-question-3-les-etudes-a-garder.md`).

### La clôture : par fonction

L'action se clôt quand aucune fonction ne porte le même nom des deux côtés
d'une paire, hors d'une liste déclarée où chaque entrée nomme le lecteur
Python qui reste et le test qui confronte les deux exemplaires. Un test de
la carte le vérifie (`161/2026-11-12-question-4-la-cloture.md`).

### La relecture : allégée, et plus un préalable

Le troisième temps de la méthode (note 0003) demandait de relire chaque
paire, fonction par fonction, avant son retrait. Il ne vaut plus que pour
les fichiers du portage que la concordance exécute peu : `droit/releve.js`,
`journal.js`, `droit/categories.js` et `fusion.js`, à 21, 60, 67 et 78 % de
leurs lignes à l'inventaire. Pour les autres, le retrait n'attend pas de
relecture : la concordance au bit près des témoins et la lecture au droit de
l'action 130 en tiennent lieu. La raison : deux exemplaires qui rendent les
mêmes valeurs ne se départagent pas en les comparant ligne à ligne, et ce
sont les lectures des textes qui ont trouvé les règles manquantes
(actions 184 et 192).

Le quatrième temps reste entier : ce que les tests n'exécutaient pas se fige
par des témoins avant le retrait. Une session reste libre de relire une
paire, et ce qu'elle trouve se corrige sans attendre.

## Ce qui ne change pas

La règle de l'endroit et le JavaScript qui fait foi (notes 0003 et 0005) ; ce
qui reste en Python (note 0006) ; les six conditions du pont ; les temps 1,
2, 4, 5 et 6 de la méthode ; les témoins et les agrégats identiques, à
l'octet ; une étape par session.

## Les solutions écartées

- **La garantie de population en Python seul**, comme le disait la lettre du
  critère : le barème resterait en deux exemplaires, et le site chiffre
  d'autres cas que le coût.
- **Porter les tests fichier par fichier, sans façade** : jusqu'à quinze
  sessions, quand 530 tests passent tels quels par la façade.
- **La relecture complète avant tout retrait**, demandée le 14 octobre 2026 :
  12 à 14 sessions pendant lesquelles chaque règle s'écrit deux fois.

## La migration

Rien ne se retire ici. Le dépôt change en six endroits : cette note ; la
table « Où va quoi » (`docs/architecture.md`) ; les consignes de `src/` et
de `moteur/` ; une version de l'architecture ; le bloc « Reprise » de
l'action 161 et la note de l'étape.
