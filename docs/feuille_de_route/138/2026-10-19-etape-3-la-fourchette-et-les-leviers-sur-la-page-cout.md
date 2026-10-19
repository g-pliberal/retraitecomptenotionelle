# Étape 3, quatorzième partie : la fourchette et les leviers sur la page Coût

**La demande.** Vague du 19 octobre 2026, session 20 de la quatrième salve,
la seule des pages : « Action 138, étape 3, ce qui revient aux pages : la
fourchette « étroite » de la page Coût, contredite, les leviers, le taux
effectif » — le point 4 de « Ce qui reste » de la note « la date de chaque
cohorte », et le point 1 de la note du 14 octobre sur le levier de l'âge. Les
chiffres viennent du modèle, qui ne bouge pas ; la table des poids de
`pages.js` reste au propriétaire.

**La fourchette.** Depuis le 18 octobre, la page disait en gras « Les chiffres
de la proposition ont une fourchette, étroite. », que le catalogue tenait
`contredite` : seize points de dette séparent les deux lectures en 2070 (76 et
92 % du PIB), un quart de point de solde moyen (−1,12 et −1,37 %), et la
seconde alourdit la proposition sur les quatre lignes du tableau de la
fourchette — sa dépense de 2070, 8,2 et 8,6 % du PIB, son coefficient, 1,00
et 0,95, aussi. La phrase devient « Les chiffres de la proposition sont la
plus favorable de deux lectures. », dans la liste des limites et au README ;
`cout.borne_basse` revient à `verifiee`, sous le contrôle
`fourchette_favorable` — les quatre lignes, dans le sens dit —, qui remplace
`fourchette_elargie`. C'est, à peu de chose près, la phrase de l'action 147
(étape 3), « la borne basse d'une fourchette », que l'identifiant garde. Le
dépliant de la fourchette perd « qui se tiennent de près » et « l'écart est
petit, et il change de signe », et ne dit plus « elle ne l'allège que en 2026,
de 0,1 % au plus en 2026 », mais « qu'en 2026, de 0,1 % ». Publié à part
(b207e0f).

**Les leviers.** `leviers.py` (14 octobre) chiffre, pour chaque système et
chaque année, ce que la pension, le taux de prélèvement ou l'âge devrait
faire, seul, pour que l'année tombe juste, et le pension gap et le tax gap sur
les horizons du COR ; aucune page ne les montrait. La table du paquet les fige
sous la référence (`leviers`, paquet en version 28 : `figer_leviers` et
`LeviersFiges` dans `donnees/agregats.py`, leur jumeau dans `agregats.js`),
avec les bornes du recul cherché, de dix ans plus tôt à quinze ans plus tard,
hors desquelles l'âge vaut `None`. La page Coût les met dans le dépliant du
coefficient d'équilibre, sous « Rogner, prélever plus ou partir plus tard » :
un tableau des quatre systèmes en 2050 et en 2070 (`ANNEES_LEVIERS`), le tax
gap de 2026 à 2070 du système actuel et de la proposition, et une phrase en
gras, « Pour le système actuel, le COR trouve les mêmes leviers. »
(`cout.leviers_du_cor`), que le contrôle `leviers_du_cor` confronte, chaque
année de 2030 à 2070, au témoin du COR : un point de pension, un dixième de
point de taux, un dixième d'année au plus (0,7 point, 0,07 point et 0,05 an ce
jour). Le classeur du COR reste au statut `controle` : aucun de ses chiffres
ne s'affiche.

| Sous la référence, le 19 octobre | Pension 2050 | Taux 2050 | Âge 2050 | Pension 2070 | Taux 2070 | Âge 2070 |
|---|---|---|---|---|---|---|
| 1. Système actuel | −8 % | +2,9 points | +1,6 an | −16 % | +5,6 points | +3,0 ans |
| 2. Part salariale | +167 % | −17,9 points | — | +153 % | −17,0 points | — |
| 3. Les deux parts | +13 % | −3,2 points | −2,2 ans | +14 % | −3,5 points | −2,5 ans |
| 4. La proposition | −17 % | +3,9 points | +3,3 ans | 0 % | +0,1 point | +0,1 an |

Le tax gap de 2026 à 2070 vaut 2,8 points pour le système actuel (2,76 au
COR), 2,6 pour la proposition. Ce que la note du 14 octobre proposait d'écrire,
3,1 ans pour le système actuel en 2070 et 3,0 ans pour la proposition en 2045,
est devenu 3,0 et 3,3 depuis que chaque cohorte de la grille part l'année que
le droit de sa génération lui donne (18 octobre).

**Le taux effectif attend le modèle.** La CSG effective de la quatrième
partie (`depense_nette.py`) n'a pas de place dans le modèle : le module ne lit
ses séries que du témoin de la DREES (`tests/temoins/drees_pension_nette.json`),
et sa note renvoyait d'abord à la session du Coût « un fichier de
`data/reference/macro/`, avec sa ligne de vérification, que `cout.py` lirait
pour l'effet retour et la page Coût pour une dépense nette ». La page ne
pourra montrer une dépense nette qu'ensuite : rien n'en est écrit ici.

**Ce que ça déplace.** La page Coût en ses quatre états (`cout`,
`cout_cascade_horizon`, `cout_cascade_hors_liste`, `cout_flux_horizon`), et
elle seule ; aucun des 888 témoins de simulation. Le paquet gagne la table des
leviers sans qu'aucun autre de ses chiffres bouge de ce fait ; refait sur
`main`, il prend aussi les marches de la cotisation maladie que l'étape 9 venait
d'ajouter à ses sources, comme GitHub l'aurait fait. Les chiffres ancrés de son
poids suivent.

**Les tests.** `test_agregats.py` : les leviers figés sont ceux du modèle, et
les deux lecteurs lisent les mêmes ; `test_web.py` : la page donne les trois
leviers, cellule par cellule, la phrase du tax gap, et les bornes quand une
case est vide ; `test_web_revues.py` compte neuf tableaux de systèmes sur
Coût, et non huit ; `test_affirmations.py` : `fourchette_favorable` et
`leviers_du_cor`, `fourchette_elargie` retiré.

**Ce qui reste**, de cette partie ; le reste de l'étape est dans son bloc.

1. *Le taux effectif* : au modèle d'abord, ci-dessus ; puis, à une session
   des pages, la dépense nette à côté de la brute.
2. *Les points 2 à 4 de la note du 14 octobre*, au modèle : l'âge spontané du
   modèle, le niveau de vie relatif et la part de la vie en retraite comme
   leviers, l'écart de la pension au COR, un demi-point. La page suivra la
   table.
