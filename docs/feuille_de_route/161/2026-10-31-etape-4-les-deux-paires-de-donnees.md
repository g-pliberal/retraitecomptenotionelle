# Étape 4 : les deux paires de données — les crédits des ministères et la table des agrégats, lues par le seul portage

**La demande.** Le 31 octobre 2026, le propriétaire ouvre l'étape 4 de
l'action 161 : les deux paires de données, selon la note de décision 0005,
par la méthode de la note 0003, en parallèle de l'étape 1 (les témoins
simulés par le portage), que mène une autre session et dont cette étape ne
touche aucun fichier. Le Python garde ce qui lit le YAML et fabrique le
paquet ; tout calcul ou accesseur exécuté sur le paquet n'a qu'un exemplaire,
dans `moteur/js/`. Les tests passent au portage, vus verts avant tout
retrait, chaque assertion gardant sa force ; les écarts du 23 octobre se
tranchent dans `agregats.js`, chacun par son test vu rouge, sans qu'une page
change ; les écrivains, le paquet et les témoins restent identiques à
l'octet.

**Le relevé et la mesure.** `python scripts/jumeaux.py`, puis
`--couverture`, mesurée en 4 min 51, au début de l'étape : des crédits, les tests
de concordance exécutaient 14 lignes Python sur 38 (37 %) et 22 lignes
JavaScript sur 24 (92 %) ; de la table, 383 sur 722 (53 %) et 409 sur 434
(94 %) — ce qu'ils n'exécutaient pas, côté JavaScript, était presque tout
refus. Les lecteurs Python n'avaient d'autres lecteurs que les tests : six
de `test_agregats.py`, `test_bilan_compte.py`, trois de `test_web.py` ; la
fabrique n'importe que les écrivains (`_agregats`), et des crédits, le
chargeur (`_credits_ministeres`). Dans `moteur/js/`, seul `pages.js` lit la
table, par `contexte.js` : chaque appel des accesseurs que les écarts
touchent demande ce que la table porte, une année ou une génération en
nombre — les générations de `CLASSEMENT_COMPARE`, les années des leviers et
des variantes, la décomposition depuis la première année projetée, le stock
de la première à la dernière année de la dette, les fenêtres du solde moyen
dans la table, `ressourcesMeur` sur le bilan, non sur le solde dérivé.

**Les crédits des ministères.** Les deux tests passent au portage (e6a38fb) :
`test_sre_jaune_ministeres.py` calcule l'attendu sur le fichier certifié, dans
l'ordre d'addition du portage (la contribution, T2 puis T3 CAS depuis zéro ;
puis la retenue), et vérifie que le paquet porte ce que lit le chargeur ;
`test_web.py` prend le sien dans les parts du paquet. Verts, et rouges sous
trois mutations du portage : la contribution sans le T3 CAS, l'ordre
renversé, une part absente qui ne vaut plus zéro. Le retrait (2f4a6b9) laisse
au Python le chargeur seul — l'année, la fiabilité, les parts —, de 69 à
47 lignes ; `credits-ministeres.js` se dit sans jumeau. La carte des jumeaux
appariait encore les deux fichiers par leur nom : un en-tête qui se dit
« sans jumeau » ne s'apparie plus (3743ddc, son test d'abord), et chacun
passe parmi les « seuls ».

**La table des agrégats : les tests** (4ef6bd0). `test_agregats.py` confronte
au modèle la table que lit le portage (`charger_agregats` de `agregats.js`,
sur `data/derive/agregats.json`) : les gardes-fous restent, leurs assertions
inchangées, les tableaux du portage remis en n-uplets, les clés de la grille
en « code|génération », celles de la dette publique en entiers. Les six tests
« les deux lecteurs lisent… » s'en vont : il n'y a plus qu'un lecteur, et
c'est lui que le modèle juge, chaque année au lieu d'une sur dix. Un test
neuf vérifie que le paquet porte la table telle que la fabrique l'a écrite.
Les trois pages de `test_web.py` prennent leur attendu dans la table brute,
lue en attributs (`Donnee`), et non par le lecteur dont la page se sert ; le
bilan du compte pèse sa grille sur le coût que lit le portage. Les 19 tests
de `test_agregats.py`, verts en 3 min 35, sans mémoire.

**Les écarts du 23 octobre, tranchés** (c9003dc ; `tests/js/agregats.test.js`,
six essais vus rouges, puis le lecteur). La promesse de l'en-tête — rendre ce que
la table porte, refuser ce qu'elle ne porte pas — tranche chacun.
1. Une ligne de la dette refuse un système qu'elle ne porte pas, au lieu de
rendre `undefined`, puis `NaN` dans la dette publique.
2. `ressourcesMeur` sur le solde dérivé est refusé ; de même, la classe
entière : chaque accesseur qui rend un champ de sa ligne (les reprises, la
garantie nette, les cumuls observé et des reprises).
3. Une table vide n'a ni première ni dernière année : le coût, le bilan,
l'avenir et la dette le refusent, au lieu de rendre 0.
4. La dette au taux décalé se lit sous la clé que la fabrique écrit,
`repr(float(ecart))`, que le portage reproduit (`reprFlottant`) : « 1.0 »,
« 1e-05 », « 1e+16 », la notation scientifique sous 10⁻⁴ et dès 10¹⁶ ; pour
±0,01, la clé ne change pas.
5. Une génération demandée en chaîne est refusée, comme le Python le
faisait ; la classe aussi : une année des leviers, des variantes et de la
décomposition, que le Python acceptait en chaîne par `str()`. Le portage est
plus strict que lui sur ce point, pour une seule règle : la table porte ses
années en nombres.
6. La promesse elle-même : le stock au-delà de la dernière année de la dette,
le solde moyen d'une fenêtre sans année, la dette publique sans la série de
son année de départ sont refusés. Le seul zéro que le lecteur rende sans le
lire sur une ligne est le stock jusqu'à l'année de départ, que la table porte
par elle — le modèle rendait aussi 0 au-delà, et pour une fenêtre vide.
Aucun ne change une page : `construire_pages.py` n'écrit aucun fichier — une
casse volontaire du lecteur le fait échouer —, et le test des témoins de
pages reste vert.

**Le retrait** (2ff11fb). `donnees/agregats.py` ne garde que ses écrivains,
`figer_*`, leurs champs et ce qu'ils appellent, identiques à l'octet : de
1 211 à 493 lignes. `agregats.js` se
dit sans jumeau, et les mentions des lecteurs Python — les consignes de `src/`
et de `moteur/`, l'architecture, le commentaire de la fabrique — disent qu'ils
sont partis. `data/derive/agregats.json`, `moteur/donnees.json` et les
témoins ne bougent pas.

**Tests.** 3 527 rapides ; 36 du site ; 115 essais node, par
`node --test tests/js/*.test.js` — node 22 ne prend pas le dossier seul ;
les fichiers touchés, `test_agregats.py`, `test_bilan_compte.py`,
`test_sre_jaune_ministeres.py`, `test_jumeaux.py`, avec `test_outillage.py` :
118.

**Ce qui suit.** Rien pour cette étape. Les paires de données ne sont plus
des paires : `python scripts/jumeaux.py` ne les montre plus. L'action reprend
où son bloc « Reprise » la laisse.
