# Les chiffres à unité du parcours

**Le 18 octobre 2026, la demande.** La session d'orchestration, sur la
consigne du propriétaire, « Fait toutes les tâches qui n'ont pas besoin de mes
décisions » : les montants, âges et taux que le parcours écrivait encore à la
main, hors des carrières et de la section Avantages.

**Ce qui est ancré.** 52 ancres de plus, 99 en tout. Les trois chiffres en
tête des pages Coût et Pourquoi changer, sur ce qu'elles affichent ; les
taux, la garantie et les âges de la proposition, sur ses paramètres ; le taux
d'aujourd'hui, sur la constante de l'accueil (`TAUX_ACTUEL_TOTAL`) et sur la
fiche de paie du modèle ; les médianes de l'accueil, les cases et l'âge du
militaire de Cas types, sur le paquet, où les pages les lisent ; les
coefficients d'équilibre et le déficit de 2070, sur le modèle ; la part des
salaires et de l'impôt, sur la table des ressources.

**Trois sondes, testées d'abord** (`tests/test_prose.py`). `repere` lit les
fiches de tête d'une page, par leur rang : les pages retouchent leurs
étiquettes, rarement leur ordre, que le parcours suit. Un facteur négatif,
`…*-100`, dit sans signe une baisse que le paquet range en écart négatif,
comme l'accueil. `coefficient` prend `en=manque`, `1 − c` : la part de la
dépense que les recettes ne couvrent pas, et de combien le réglage
abaisserait les cases.

**Ce qui avait dérivé.** Le parcours donnait « 12 % » d'une baisse que
l'accueil chiffre à 13 ; le test passait sur un autre « 12 % » de la page, la
part des hommes sous le plancher. Les coefficients de la proposition, sans
unité, que rien ne confrontait : « inférieur à un 37 années sur 45, 0,90 au
plus bas en 2049, 1,06 en 2070 », pour 0,83 en 2048 et 0,998 en 2070 ; et,
dans les questions, « 8 % en 2070 », pour 17 % au plus en 2048. La phrase
suit désormais les chiffres, sans dire combien d'années passent sous un. En
lettres, « d'un quart à un tiers » devient « de l'ordre d'un quart », comme
l'accueil l'écrit.

**La garde.** `test_aucun_chiffre_a_unite_du_parcours_ne_s_ecrit_a_la_main`,
de la suite rapide, refuse tout montant ou taux écrit à la main hors de ceux
qu'`ECRITS_A_LA_MAIN` déclare, chacun avec sa raison : les saisies (les
quatre salaires, le foyer de 300 et 1 500 € que l'accueil pose en exemple),
le zoom de 125 ou 150 %, et deux chiffres qu'aucune sortie ne porte, le
« 100 % » de la quatrième promesse, que la page écrit sans le calculer, et le
« 30 % » de la question de la salle.

**Ce qui reste écrit à la main.** Les chiffres en lettres, que l'ancre ne sait
pas tenir, dont trois se déduisent de chiffres ancrés : « seize ans et demi »
(65 − 48,5), « dix points » (28 − 18), « cinq points rendus » ; les années ;
et les étiquettes du tableau de Pourquoi changer, que la page a récrites
(« VOS cotisations achèteraient ») et que le parcours paraphrase.

**Vérifié.** `tests/test_parcours.py` et `tests/test_prose.py` passent, sauf
deux rouges d'avant l'étape, périmés sur la tête propre : le poids du site au
README et `docs/etat.md`, que GitHub refait. La suite rapide, 2 631 tests, et
sa garde des présomptions, 2 558, ont un rouge chacune, d'avant l'étape
aussi : `test_micro_social.py`, dont le paquet n'a pas encore les seuils que
9052093 y attend.
