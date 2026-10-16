# Étape 4, septième partie : le cycle de vie — relevé, mesuré, et pourquoi ses deux jumeaux restent

**La demande.** Retirer de `cycle_de_vie.py` ce que son jumeau
`moteur/js/cycle-de-vie.js` couvre, maintenant que le site l'affiche
(action 138, étape 10, dépliant « Partir plus tôt ou plus tard ») ; dire ce
qui doit rester au Python, et pourquoi.

**Relever** (`python scripts/jumeaux.py cycle_de_vie`). Ni le coût ni la
fabrique n'atteignent le module. Il est importé par `scripts/cycle_de_vie.py`
et cinq fichiers de tests : `test_cycle_de_vie.py`, `test_cycle_de_vie_portage.py`
(la concordance), `test_cycle_de_vie_references.py` (le COR, l'OCDE, l'ETK),
`test_estimation_du_site.py`, `test_prelevements_historiques.py`. Le graphe
des appels du module, fermé depuis ses lecteurs, dit le reste : sur ses 88
noms (fonctions, classes, constantes), le script en atteint 84, et les tests
autres que ceux du module et de la concordance, 86. Deux seulement ne
servaient qu'aux tests du module ou à personne : `grille`, et `ages_de_depart`.

**Mesurer** (`python scripts/jumeaux.py --couverture cycle_de_vie`, au commit
7cf1ef0). Les tests de concordance exécutent 851 lignes Python sur 913
(93 %) et 998 lignes JavaScript sur 1 026 (97 %). Les lignes Python jamais
confrontées sont, pour l'essentiel, celles qui n'ont pas de jumeau : les cas
types (`ages_de_depart`, `balayage`, `ages_d_equilibre`,
`hypotheses_de_productivite`) et `grille`.

**Pourquoi le Python reste.** Les cas types du COR se bâtissent en Python seul
(`castypes.py`, que le coût lit, et qui n'a pas de jumeau) ; le script les
mène sous les six systèmes — indicateurs, balayage des âges de départ, âges
d'équilibre de chaque cas type — par 84 des noms du module, et le test des
références confronte aux publications du COR et de l'OCDE des carrières bâties
en Python (dont `remplacement_apres_impot`, sur les cas de l'OCDE). Retirer un
nom couvert par le portage voudrait que ces lecteurs passent par node, cas
types compris : c'est le pont (étape 5), ou un jumeau de `castypes.py`, pas un
retrait. Les seuls noms couverts par le portage et lus des seuls tests,
`remplacement_apres_impot` et `revenus_imposables`, sont l'un lu par le test
des références, l'autre une enveloppe de deux lignes du chemin que le script
prend : rien à y gagner.

**Retirer.** `grille`, que rien n'appelait depuis que le script mène ses cas
types un à un, et qui n'avait pas de jumeau. `ages_de_depart` reste : c'est
l'âge de départ d'un cas type, au même titre que `balayage`. Le docstring du
module, qui le disait absent du site, dit désormais que le site l'affiche par
son jumeau, et pourquoi les deux restent.

**Tests.** 2 462 rapides, 2 408 sous les présomptions décalées, 126 de la
zone (cycle de vie, concordance, références, jumeaux, prélèvements
historiques) ; la prose dit le vrai. Aucun témoin n'a bougé.

**Ce qui suit.** L'étape 4 est close : des trois paires que ni le coût ni la
fabrique n'atteignaient, le lecteur du relevé et le lecteur PDF sont devenus
du JavaScript seul, et le cycle de vie garde ses deux jumeaux, tenus par la
concordance, jusqu'au pont. L'étape 5, le pont, vient ensuite ; c'est elle
qui dira si `scripts/cycle_de_vie.py` et le test des références peuvent lire
le portage, et à quel prix pour les cas types.
