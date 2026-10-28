# Étape 6 : le calendrier et la chronologie relus contre leurs portages — le demi-mois, les dates déclarées, la naissance au jour présumé

**La demande.** La vague du 28 octobre 2026 : dix-sept sessions en
parallèle, une tâche chacune, que le propriétaire ne suit pas pas à pas.
Celle-ci tient le premier reste de la huitième partie : l'arrondi du
calendrier et la lecture des dates de la chronologie, à la relecture de leurs
paires (sixième partie). Aucune des deux ne se retire : le coût et la
fabrique les atteignent encore (`jumeaux.py` : rangs 58 et 60).

**Le calendrier, relu.** Fonction par fonction. Un écart réel : `en_mois`
arrondissait le demi-mois exact au pair, `enMois` vers le haut ; 64,375 ans
valaient 772 mois en Python, 773 dans le portage, et 64,125 ans 770 des deux
côtés. La fiche `date_effet_mois_suivant` tranche pour le portage : la
pension prend effet le premier jour du mois qui suit celui où l'âge est
atteint, et un âge atteint à la moitié d'un mois compte donc le mois qui
suit. L'arrondi au pair comptait ou perdait le demi-mois selon la parité du
mois, le défaut que le module reprochait déjà à l'arrondi à l'année. Le
Python suit le portage (8541183). Seule une adresse écrite à la main porte un
demi-mois exact (`liquidation=64.375`) : le formulaire donne des mois
entiers, et ni les fiches ni les 909 cas des témoins n'en portent.

Sans effet, faute d'entrée qui les atteigne : `decomposer` d'un nombre de
mois négatif (−1 an et −1 mois dans le portage, −1 an et 11 mois en Python),
qu'aucun appelant ne lui passe, les âges écrits étant ceux d'un assuré et
l'écart à l'âge de référence passant par `abs` ; un âge non fini, que le
Python refuse en levant, le portage par le calendrier, et que la saisie
refuse avant (huitième partie). `DateMois` s'ordonne et se compare par valeur
en Python, ni l'un ni l'autre dans le portage : une sonde sur `valueOf`, sur
les 909 cas et les 105 essais de node, ne voit aucune comparaison, le
portage comparant des rangs.

**La classe.** `limite_age._mois` et `reversion._atteint` arrondissent eux
aussi un âge au mois par `round`, leurs jumeaux par `Math.round` ; seules des
données y entrent, toutes en mois entiers.

**La chronologie, relue.** Fonction par fonction, par un agent, ses constats
vérifiés aux lignes citées et par un essai des deux côtés. Une date déclarée
— d'un enfant, du décès, du conjoint, du mariage… — s'écrit en chiffres,
AAAA, AAAA-MM ou AAAA-MM-JJ, et c'est une date du contrat C.1
(`date.fromisoformat`), de l'an 1 à 9999. Le Python lisait par `int`
« +962 », « 1_62 », les chiffres pleine chasse et un blanc entre deux
tirets ; le portage datait par `Date.UTC`, qui envoie les années 0 à 99 au
vingtième siècle, et disait « 0050 » impossible. Chacun corrigé (a1ef2e6) :
`_nombres` ne prend que des chiffres, `dateControlee` date les années de 1 à
9999, et les deux lecteurs du portage passent par elle. Au jour présumé,
`naissanceDeLAssure` rendait un fait de naissance sans date (`debut: null`,
que le contrat refuse) quand le calendrier ne la datait pas — un mois 13, un
jour présumé hors du mois, l'an 12 000 —, là où le Python lève : les deux
chemins passent par la même vérification (ad463e4).

Les autres écarts relevés, une quarantaine, tiennent à des entrées qu'aucun
appelant ne produit. La saisie du site, que les pages et le pont lisent
stricte (`depuisRequete(…, false, …)`), refuse le mois, le jour et l'année
hors du champ avant toute chronologie, et ne transmet que des nombres finis,
des booléens, des codes de listes fermées, des objets complets et des dates
qu'elle a déjà lues par le lecteur du portage ; côté Python, plus aucune
saisie ne nourrit les constructeurs, que le coût, les cas types et les
scripts appellent de valeurs typées, et la fabrique passe par le pont. Ce
sont des clés absentes (`KeyError` en Python, `undefined` dans le portage),
des types confondus (`float` et `Number`, `int` et `Math.trunc` ne lisent pas
les mêmes textes), des valeurs fausses (`[]`, vrai en JavaScript, faux en
Python), les blancs que `strip` et `trim` ôtent, la forme des messages
(`repr` ou guillemets), la table des présomptions absente (sixième partie),
un lien dont la fin serait une date nue, une pension étrangère au territoire
nul, que les constructeurs n'écrivent jamais. Rien n'est corrigé pour eux.

**Tests.** `tests/test_moteur.py` : le demi-mois, et 2 624 âges confrontés
aux deux moteurs. `tests/test_chronologie.py` : quinze dates déclarées, lues
par les deux lecteurs de chaque côté ; trois naissances impossibles au jour
présumé. Chacun vu rouge pour sa raison, puis vert. La suite rapide à chaque
commit ; les tests de la saisie, du pont et de la réversion ; le filet du
site ; les confrontations légères du modèle ; les 909 cas des témoins,
identiques au bit près dans le portage.

**Ce qui reste.**
1. `pages.js`, ligne 7, pour une session du site (sixième partie).
2. `point_fixe` et `pointFixe`, quand le coût datera ses cas types par le
   portage (septième partie) ; la paire de la carrière, sa propre note.
3. `limite_age._mois` et `reversion._atteint`, à la relecture de leurs
   paires.
4. Les paires suivantes de la carte attendent que le coût passe le pont ; deux
   paires de données, au propriétaire.
