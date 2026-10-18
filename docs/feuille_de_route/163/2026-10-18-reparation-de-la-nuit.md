# La réparation de la nuit du 17 octobre

**Le 18 octobre 2026, la demande.** La session d'orchestration : remettre au
vert la suite complète, rouge depuis les envois de la nuit (course
39081914980, sur `3489eab`, verdict non publié, `main` ayant bougé). Les
quatre rouges se reproduisaient sur la tête, `50c6a0c`, la fabrique refaite.

**1. Le parcours, section Avantages** (`test_parcours`, « 99,8 Md € ») : un
chiffre que le parcours écrivait à la main, et que le changement déplace, la
première famille des rouges classés. Le coût que le modèle chiffre en 2024,
refait par la fabrique, passe à 99,6 Md €. Les trois montants de la section
et leur année se lisent désormais dans le paquet, où la page les lit
(`valeur(moteur/donnees.json:agregats.avantages.annees.-1.…)`) : GitHub les
récrit avec lui. Restent écrits à la main 28 chiffres à unité du Programme,
des Cas types, du Coût et du Risque, que la reprise de l'action nomme déjà.

**2. La distribution de la grille** (`test_grille_large`, 16 280 317 têtes
pour 16 280 845 en 2020) : un changement du modèle qui déplace une
confrontation, la troisième famille. `2534b02` (action 138, étape 7) fait
survivre chaque cas type au rythme de sa population dans `cout._masses`,
et `facteurs_depense.py` l'a suivi ; `grille_large.cohortes_de_l_annee`
pesait encore ses cohortes par la seule pyramide. Elle prend la même survie
(`cout._survies_alignees`), et c'était la seule pesée de ce genre du
script. Les autres pesées par la pyramide, que l'étape 7 laissait,
attendent à sa note (« Ce qui reste », 2).

**3 et 4. La garde des présomptions** (`test_minima_agricoles`, deux tests de
`d1377ff`, `f7945f3` et `83b03bd`) : un test qui raconte une date sans la
déclarer (action 135, levier 2). Né un 1er, le chef de décembre 1940 part le
1er décembre 2000, sous les 26,933 points de 1997, et non le 1er janvier
2001 ; celui de janvier 1932 part le 1er janvier 1994, sans l'année 1994
que L. 731-10-1 lui comptait : 36 ans d'activité agricole et non 37, un
coefficient d'anticipation de 0,85 et non 0,95, et sa durée reconstituée
tombe de 23,1 à 14,0 ans. Le chef du fichier, `_chef`, déclare le 15 du mois,
comme les aides du levier 2 : la classe tient à l'aide, non aux tests. La
garde jouée sur la tête en levait un cinquième, de la même classe, né après
la course : `test_limite_age`, de `29a1743` (action 151, étape 9), dont
l'agent des IEG né en novembre 1952 a cinquante-cinq ans « le 15 novembre
2007 » ; né un 1er, il est mis en inactivité en novembre et non en
décembre. L'aide `_simple` du fichier déclare le 15 de même.

**À trancher par le propriétaire.** La garde des présomptions ne se joue que
sur GitHub, et c'est son troisième rouge : `pousser.sh` pourrait la jouer
sur les fichiers de tests qu'un commit touche. C'est une garde ; cette
session n'y touche pas.

**Vérifié.** Les tests visés, sous les deux présomptions pour la garde ;
`test_minima_agricoles.py`, `test_limite_age.py`, `test_grille_large.py` et
`test_parcours.py` entiers, ce dernier sur le paquet du dépôt et sur celui
que la fabrique refait ; la suite rapide, 2 611 tests, et sa garde, 2 541 ;
les confrontations légères du modèle ; `test_prose.py`, sur la tête où
`a4b1e5e` venait de refaire les fichiers fabriqués, et dont le paquet donne
déjà 99,6 Md €.
