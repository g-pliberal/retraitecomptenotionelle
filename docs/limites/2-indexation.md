# 2. La règle d'indexation domine le scénario rétroactif

Le modèle revalorise par défaut sur la croissance de la masse salariale — le
taux d'équilibre de la répartition. Ce qui suit décrit la règle demandée, le
triple lock inversé (`indexation=triple_lock_inverse`), parce que c'est elle
qui porte les écarts les plus lourds ; les limites propres à la règle par défaut
sont énoncées à la fin de cette section.

Le triple lock inversé, pris à la lettre, retient le minimum entre deux taux
**nominaux** (inflation, salaire moyen) et un taux **réel** (productivité). Dès
que l'inflation dépasse la croissance de la productivité, c'est cette dernière
qui l'emporte.

Sur 1941-2025, les comptes sont revalorisés ×<!--chiffre:mesure(cumul_indexation?regle=triple_lock_inverse&de=1940&a=2025)-->4,9<!--/--> quand les prix sont multipliés
par <!--chiffre:mesure(cumul_indexation?regle=prix&de=1940&a=2025)-->322,2<!--/--> : **un euro cotisé en 1940 conserve, en 2025, <!--chiffre:mesure(conserve?regle=triple_lock_inverse)-->1,5<!--/--> % de sa valeur
réelle.**

Conséquence : dans le scénario rétroactif, l'essentiel de la baisse affichée
vient de la règle d'indexation, pas du passage aux comptes notionnels. Les deux
effets ne sont pas séparables par lecture directe du tableau.

Pour les distinguer :

Comparer, sur la même carrière, la règle « triple lock inversé, tout en
nominal » et la règle « revalorisation portée au compte » — le sélecteur
d'indexation du formulaire, ou `mode_indexation` en Python.

La variante nominale conserve <!--chiffre:mesure(conserve?regle=triple_lock_inverse_nominal)-->69<!--/--> % du pouvoir d'achat sur la même période, tout
en restant plus sévère que l'indexation sur les prix. C'est probablement ce que
vise l'intention d'une règle d'indexation prudente ; le choix reste ouvert.
