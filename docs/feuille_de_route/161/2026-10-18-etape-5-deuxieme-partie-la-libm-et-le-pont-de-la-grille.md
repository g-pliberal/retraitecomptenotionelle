# Étape 5, deuxième partie : le portage calcule ses exponentielles comme la libm de Linux, et la grille des carrières types des agrégats passe le pont

**La demande.** La suite de l'étape 5 : le pont du coût et de la fabrique,
sous les six conditions de la note 0003, en remaniement, sans qu'aucun
résultat ne bouge.

**Ce qui barrait la deuxième condition.** Des témoins et des agrégats
identiques à l'octet, quel que soit le moteur. Mesurée d'abord sur la plus
simple lecture de la fabrique, la grille des carrières types de la table des
agrégats, l'identité manquait sur 17 de ses 273 écarts, au dernier chiffre
(2,3 × 10⁻¹⁴ au plus). Le compte et les cotisations étaient identiques ;
seul le diviseur différait, par la survie, faite d'exponentielles et de
logarithmes. Le moteur Python tient `math.exp`, `math.log` et `**` de la
glibc ; le portage les tenait de V8, qui s'en écarte au dernier bit sur 7 %
des logarithmes, 12 % des exponentielles et 10 % des puissances, dans les
plages du moteur. Tous les écarts entre les deux moteurs venaient de là.

**La libm du portage.** `moteur/js/libm.js` refait au bit près l'exp, le log
et le pow de la glibc 2.28 et après, sur x86_64 avec FMA : la machine de
GitHub, et celle de ce conteneur (glibc 2.39). Ce sont les algorithmes d'Arm
Optimized Routines, sous leur licence (MIT ou Apache-2.0 avec l'exception
LLVM) ; leurs tables sont recopiées, vérifiées identiques à celles du binaire
`libm.so.6` ; les produits que le compilateur y a fusionnés, relevés au
désassemblage des variantes FMA, se refont par une FMA émulée (Dekker,
Knuth, l'arrondi à l'impair de Boldo et Melquiond), en entiers exacts hors
de [2⁻⁴⁰⁰, 2⁴⁰⁰]. Confronté à la libm, sous deux graines : 5 millions d'exp,
6,2 millions de log, 7,5 millions de pow ; la FMA à `math.fma` sur 5 millions
de cas tirés au hasard et 3 millions tout près d'un milieu d'arrondi : aucun
écart.

**Le moteur branché.** Les 36 appels du portage passent par lui, chacun en
face de son jumeau Python ; `distribution.js` élève au carré par `pow`, comme
`distribution.py` par `** 2`. Les 164 411 nombres des 883 témoins sont
devenus identiques au bit près (97,3 % avant, l'écart maximal tombant de
9,05 × 10⁻¹⁵ à zéro), et la grille des agrégats aussi. La présentation et la
lecture des documents gardent les fonctions du navigateur (`pages.js`,
`format.js`, `releve-lu.js`) ; une garde interdit au reste `Math.exp`,
`Math.log` et `**` (`tests/test_libm.py`).

**La grille des agrégats passe le pont.** La fabrique
(`scripts/construire_donnees.py`) fait simuler par le portage la grille des
carrières types et les quatre départs du classement : le Python fixe l'âge
de chaque départ et écarte ce que le droit écarte
(`castypes.cases_de_la_grille`), node simule (`retraite_notionnelle/pont.py`
et `pont.mjs`), sur le paquet du jour sans ses agrégats, que la fabrique
bâtit d'abord. La table et le bilan sortent identiques à l'octet, et
`tests/test_agregats.py`, qui exige à l'égalité exacte la table du moteur
Python, tient désormais la deuxième condition pour cette lecture.

**Les six conditions, pour cette lecture.** Les données : les options de
`carriere_simple` dans un sens, et dans l'autre ce que la table lit, chaque
nombre sous le type que le Python lui donne (`tests/test_pont.py`).
L'identité : ci-dessus. Le budget : le moteur JavaScript passe de 4,15 à
4,28 ms par carrière pour les six scénarios, le scénario 1 inchangé ; la
grille, de 3,4 à 4,8 s par le Python à 3,9 à 4,4 s par le pont, dont 1,5 s de
paquet provisoire. La mémoire : celle de la fabrique suit `moteur/js`, hors
`pages.js` (`fabrique.fichiers`) ; celle des calculs (`memoire.py`) attend
que le coût passe le pont. Sans node, le pont s'arrête (`PontIndisponible`).
Aucune dépendance nouvelle ; le site charge 38 Ko de plus, 13 compressés.

**Tests.** Avant le premier envoi : 2 755 rapides, le site, les 39 tests de
node. Avant le second : 2 805 rapides ; `test_agregats.py`, `test_pont.py`,
`test_fabrique.py`, `test_libm.py`, la carte des jumeaux, les niveaux et
l'outillage ; `construire_donnees.py --verifier` rend la table et le bilan à
l'octet, le paquet ne différant que des données que d'autres sessions
venaient d'envoyer. Le témoin de la surcote parentale (action 159) divergeait
déjà avant le premier envoi ; les témoins que d'autres sessions changent
attendent la fabrique de GitHub.

**Ce qui suit.** Le reste de la fabrique : la grille des écarts médians et
les trois exemples du bilan (`_bilan`), encore simulés en Python. Puis la
grille du coût, sous les conventions du COR, dont les carrières se déforment
en Python (`primes_projetees`, l'entrée tardive) et doivent passer en
données, et dont le coût lit les résultats en profondeur ; `memoire.py`
s'indexera alors sur le portage. Le test des références et le retrait de
`cycle_de_vie.py` l'attendent. Après la vague, le propriétaire peut faire
exiger des témoins l'égalité exacte (`tests/js/moteur.test.js` tolère
10⁻⁹) : le portage les rendait tous au bit près.
