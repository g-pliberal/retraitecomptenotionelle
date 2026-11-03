# Le coût sous un modèle modifié, sixième sous-étape : le levier du jumeau réservé aux confrontations, qu'un test tient

**La demande.** La sous-étape 6 du plan
(`2026-11-02-le-cout-sous-un-modele-modifie.md`), la dernière, une par
session : le levier `pont.par_le_jumeau()`, qui fait calculer le jumeau
Python et taire la mémoire des calculs, réservé aux seules vérifications —
les confrontations, qui font refaire au jumeau ce que le portage calcule —,
qu'un test le tienne, et qu'il parte avec la dernière paire qu'il confronte.
Depuis la sous-étape 5 (0cbc065), plus aucune étude ne l'ouvrait, mais rien
ne l'empêchait d'y revenir. La décision du propriétaire, du 2 novembre 2026,
tient : le JavaScript pour ce que le visiteur utilise ; les grands totaux
fabriqués en Python et lus au paquet (notes de décision 0005 et 0006).

**Le relevé.** Lu dans l'arbre syntaxique des 526 fichiers Python du dépôt :
quatorze tests ouvrent le levier, tous sous `tests/` ; aucun module de
`src/`, aucun script. Douze confrontations : sept de `tests/test_pont.py` —
la grille de la table, les départs des facteurs de la dépense, le coût des
avantages, la grille du coût datée, bâtie et simulée, sous une variante
d'univers, sous la règle du stock, sur des données d'ailleurs —, deux de
`tests/test_grille_large.py`, une de `tests/test_cout.py`, de
`tests/test_solde_fusion.py` et de `tests/test_stock_age_legal.py`. Et les
deux tests du levier lui-même, dans `tests/test_pont.py` : ce qu'il aiguille,
et le moteur Python qui calcule sous lui, node absent.

**Le test.** `test_seules_les_confrontations_ouvrent_le_jumeau`
(`tests/test_pont.py`, suite rapide, moins d'une seconde) lit chaque fichier
Python du dépôt, suivi ou nouveau (`git ls-files`), dans son arbre
syntaxique : une fonction ou une classe de premier niveau ouvre le levier si
son code le nomme, par l'attribut ou l'import, ou touche son compteur
(`pont._JUMEAU`) ; une mention dans une chaîne n'en est pas une. Il exige :
rien hors de `tests/` ; sous `tests/`, les seuls tests déclarés un à un,
`CONFRONTATIONS_DU_JUMEAU` et `TESTS_DU_LEVIER`, chaque déclaré ouvrant
encore le levier ; et, plus aucune confrontation déclarée, le levier parti.
Une confrontation part avec la paire qu'elle confronte, au retrait de son
jumeau ; la dernière partie, le test rougit tant que restent le levier, ses
deux tests et l'aiguillage de `pont.par_le_portage`.

**La contre-épreuve.** Le test vu rouge pour la raison attendue, deux fois,
sur des fichiers temporaires que rien n'a commités : un script d'étude qui
ouvre le levier (« une étude n'ouvre pas pont.par_le_jumeau() », le script et
sa fonction nommés) ; un fichier de tests qui l'importe et l'ouvre sans être
déclaré (« ouvrent pont.par_le_jumeau() sans être déclarées »). Les deux
ôtés, vert.

**La prose.** Ce qui disait encore qu'un contexte qui remplace une fonction
du moteur s'ouvre sous le levier dit qu'une telle variante s'écrit en
données, et que seules les confrontations l'ouvrent : `par_le_jumeau` et
`par_le_portage` (`pont.py`), la règle de la mémoire et `modele_modifie`
(`memoire.py`), `test_sous_le_jumeau_le_cout_simule_sa_grille_en_python`, et
les consignes de `src/` (« Les temps tiennent à des mémoires »).

**Ce qui ne change pas.** Aucun calcul, aucune règle, aucune donnée, aucun
chiffre publié, aucune garde : les études, la fabrique et les confrontations
calculent par le même chemin qu'avant ; le paquet, les témoins et les
agrégats ne passent pas par le levier.

**Tests.** Le test neuf, seul, vu rouge deux fois, puis vert ; ceux du levier
et des confrontations de `tests/test_pont.py` qui le touchent
(`-k "jumeau or ailleurs or monkeypatch or repli"`, 19) ; `-m rapide`
(3 859) ; `tests/test_niveaux.py`, `tests/test_jumeaux.py` et les deux tests
des contextes de `tests/test_outillage.py` ; les confrontations légères, et
les tests des deux études dont une confrontation ouvre le levier,
`tests/test_solde_fusion.py` et `tests/test_stock_age_legal.py`.

**Ce qui reste.** Le coût sous un modèle modifié est au bout de son plan :
aucune étude ne remplace plus une fonction du moteur, et le levier ne sert
plus qu'aux confrontations. Suivent les retraits, une paire à la fois, dans
l'ordre de la carte (`python scripts/jumeaux.py`), chacun coupant son
fichier (note de décision 0006) et ôtant de `CONFRONTATIONS_DU_JUMEAU` les
confrontations de sa paire ; le levier part avec la dernière.
