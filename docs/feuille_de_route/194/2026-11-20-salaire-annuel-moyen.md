# Action 194 : le salaire annuel moyen, deux parties prouvées

Le 20 novembre 2026. Deuxième usage du format de preuve de l'étape A.

## Ce qui est fait

**Deux grilles indépendantes**, 78 cas (`data/reference/preuves/
grille_salaire_annuel_moyen_1995.yaml` et `_2004.yaml`), pour les versions
`moyenne_des_salaires_annuels_1995` et `annees_validantes_2004` de la fiche
`salaire_annuel_moyen`. Le moteur rend les 78 valeurs au centime. Un cas se
donne par son relevé (`carriere.releve_entier`, des paires année, salaire) et
mesure `salaire_annuel_moyen` (`tests/test_oracle.py`).

**L'indépendance**, mieux tenue qu'à la première grille : la session
indépendante a cherché elle-même ses textes dans une copie de l'index LEGI,
écrit son calcul et proposé 33 des 78 cas ; un guetteur (inotify) a journalisé
les ouvertures de fichiers sous le dépôt pendant ses deux passages, et n'en a
vu aucune. Elle n'a reçu du dépôt que trois barèmes : les tableaux de
coefficients de la Cnav, le plafond annuel, le SMIC horaire. Un article lui
avait échappé, R. 351-39, signalé ensuite sans en dire l'effet.

**Une erreur corrigée.** Le moteur classait les années d'avant 1948 avec les
autres. R. 351-29 ne les prend qu'à défaut d'assez d'années postérieures, « en
remontant à partir de cette date » ; R. 351-39 le garde depuis 2026 à qui a des
périodes de plus de soixante ans. Trois cas sur 78 s'en écartaient : né en
avril 1930, 1947 au plafond puis douze années à mi-plafond, effet d'octobre
1995, le salaire annuel moyen passe de 6 511,54 à 4 062,55 euros. La version de
la fiche porte l'année (`derniere_annee_a_defaut: 1947`). Les agrégats du coût
bougent pour les générations qui ont travaillé avant 1948 : le cumul du
scénario libéral de 0,04 %.

**La fiche ne déclare plus de simplification sans version.** Les indemnités
journalières de maternité ont leur fiche, `sam_indemnites_de_maternite`, qui
les dit manquantes ; les salaires d'avant 1947, `sam_annees_d_avant_1947`,
approchée ; les années de rachat relèvent de `rachats_et_versements`.

**Les coefficients.** De 1990 à 2026, le rapport de deux tableaux successifs
de la Cnav redonne le coefficient légal des pensions (L. 351-11, L. 161-23-1)
à chaque date, à l'arrondi du millième, sauf 2019 et 2020 où la loi a dérogé
pour les seules pensions. La série `revaloSam` de TRAJECTOiRE 3.3.2 n'est pas
celle du texte : de 2018 à 2024, elle porte chaque revalorisation un an trop
tôt (celle du 1er janvier 2025 à l'année 2024), sans l'arrondi légal (5,24 %
pour 5,3 %), et rien en 2025 ; un départ de 2024 y reçoit donc la hausse de
janvier 2025.

## Ce que le texte ne tranche pas, et la lecture retenue

L'année de l'effet avant 2026 (écartée, comme la caisse) ; le diviseur quand il
y a moins d'années que le nombre retenu (les années retenues) ; le plafond des
salaires d'avant février 1991 pour les pensions d'avant novembre 2005
(appliqué) ; aucun arrondi. Chaque autre lecture est chiffrée dans l'énoncé du
cas qu'elle change.

## Ce qui reste

- Écrire les indemnités de maternité : le forfait des naissances d'avant 2012
  (il faut l'arrêté du salaire médian) et les 125 % des congés depuis 2012.
- Les versions d'avant juillet 1995, où les salaires se rapportent aux
  trimestres : leurs simplifications restent déclarées.
- Les barèmes eux-mêmes (coefficients, plafond, SMIC) : un autre étage de la
  carte.
- Un témoin : aucun exemple officiel ne porte encore un salaire annuel moyen.
