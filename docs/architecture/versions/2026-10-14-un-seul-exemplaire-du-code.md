# Version du 14 octobre 2026 : un seul exemplaire du code

Le principe 4 change, sur la décision du propriétaire du 14 octobre 2026
(note de décision 0003, action 161). Une implémentation ne fait plus foi pour
toutes les autres : chaque étape s'écrit une fois, dans le langage de
l'endroit où elle tourne — le JavaScript pour ce que le site calcule chez son
lecteur, le Python pour ce que seule la fabrique calcule, comme le coût depuis
l'action 150, et le JavaScript pour le moteur d'une carrière, que le Python
fera tourner par node. Tant qu'une étape a ses deux jumeaux, le Python fait
foi pour elle : rien ne bouge avant qu'une paire soit relue et l'un des deux
retiré, les témoins identiques, par la méthode de la note. Le § 7.1 dit la
règle et la migration, et cesse de promettre que le principe 4 n'aura pas à
changer ; la table « Où va quoi » dit comment se retire un doublon ; les
consignes de `src/` et de `moteur/` disent où s'écrit un code neuf, et que le
Python fait foi pour une étape tant qu'elle a son jumeau. La carte des paires,
de leurs dépendants et de ce que les tests de concordance en exécutent est
`scripts/jumeaux.py`.
