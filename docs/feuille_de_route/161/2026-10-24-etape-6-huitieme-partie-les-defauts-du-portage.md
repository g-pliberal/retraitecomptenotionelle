# Étape 6, huitième partie : les trois défauts que la relecture de `saisie.py` laissait au portage, corrigés chacun par son test

**La demande.** La septième vague du 24 octobre 2026 : six sessions en
parallèle, une tâche chacune, que le propriétaire ne suit pas pas à pas.
Celle-ci tient le premier reste sans propriétaire du bloc : les trois défauts
que la relecture de `saisie.py` laissait au portage (sixième partie), chacun
par son test, vu rouge d'abord.

**Ce que le calendrier ne date pas** (c80f7fe). `naissance=1e308` : le jour,
présumé au 15 (`jour_de_naissance`), compte les âges du mois suivant, et le
rang de ce mois, l'année fois douze, passait le plus grand nombre ; le
calendrier levait sa propre erreur, « mois attendu entre 1 et 12, reçu NaN »,
dans les deux lectures, et la page disait « Le calcul a échoué » au lieu du
refus. La classe est plus large que le cas relevé. Un mois de naissance hors
de l'année (13, 0, 1e21) faisait lever le calendrier au premier mois daté ;
le `DateMois` du Python levait un `ValueError`, que sa page prenait pour une
faute de saisie. Un âge de 1e308 ans, dans sept champs — l'emploi après le
départ et sa fin, l'invalidité, la radiation pour invalidité, le handicap,
les demandes, le début d'une période à l'étranger —, le faisait lever à la
vérification, `dateDe` datant l'âge avant d'en vérifier les bornes.

La naissance se vérifie désormais avant que rien n'en soit daté : un mois
hors de l'année, une année dont les mois ne se comptent plus, se refusent
dans les deux lectures ; une année hors du champ du modèle, dans la lecture
vérifiée seulement, la saisie refusée remontrant « 3000 », que le calendrier
date. `ageSaisi` refuse un âge dont les mois ne se comptent plus, en nommant
son champ : « « invalidite » : âge hors du calendrier (reçu : 1e308) ». Ce
refus de l'âge remplace, pour ces valeurs, celui des bornes dans les champs
qui le donnaient déjà (le début, le départ, le métier suivant, la pension
étrangère). L'année refusée se cite telle que l'adresse la porte, « 1e21 »,
que le portage citait « 1e+21 » ; en chiffres, comme le Python citait
l'entier lu, 1e23 se citerait 99999999999999991611392, le flottant le plus
proche, et 1e308 de trois cent neuf chiffres. Dans la lecture vérifiée, le
refus de l'année vient désormais à la lecture : une adresse qui porte aussi
une faute dans un champ lu après la naissance reçoit d'abord celui de l'année.

**L'adresse réécrite** (04327ce). `nombreBrut` écrivait six chiffres
significatifs (`formatG`, le `:g` du Python) ; il écrit le nombre le plus
court qui se relise le même, celui de JavaScript. Ce qui tient en six chiffres
s'écrit comme avant ; au-delà, chaque chiffre reste : un revenu fiscal de
1 234 567 € ne se relit plus 1 234 570, ni un salaire de 2 534,567 €
2 534,57, et le million s'écrit « 1000000 », non plus « 1e+06 ». Les champs
du formulaire, que `pages.js` remplit par la même fonction, gardent de même
leurs chiffres, la page n'étant pas touchée : tout ce qu'elle y met est saisi
ou déjà arrondi (`arrondir`, `Math.round`). Aucun témoin ne bouge :
`construire_temoins.py` ne refait `pages.json` que des textes de Droits non
cotisés (77548d3, action 173, étape 9).

**`DEFAUTS.demandes`** (8c429ec). Le seul tableau des défauts qui ne fût pas
gelé : une saisie reçoit les défauts tels quels (`Object.assign`), et une
saisie qui y aurait écrit l'aurait écrit pour toutes les suivantes. Rien n'y
écrivait, `demandesSaisies` bâtissant un tableau neuf : le défaut était
latent. Le tableau est gelé, et un essai de node exige chaque tableau des
défauts gelé, ce que le pont, qui rend des copies, ne voit pas.

**Tests.** `tests/test_saisie_de_l_adresse.py`, 37 cas, de la suite rapide :
la naissance que le calendrier ne date pas, dans les deux lectures ; chaque
âge que la saisie lit, à 1e308 et −1e308 ; l'année citée telle qu'écrite ;
l'adresse réécrite, relue. `tests/js/saisie.test.js`, un essai, que
`test_web.py` lance avec les 107 autres. Chacun vu rouge pour sa raison, puis
vert. La suite rapide ; les fichiers de la saisie (`test_web_saisie.py`,
`test_formulaire.py`, les six `test_saisie_*`), 277 tests avec les essais de
node ; le filet du site, vert sur des témoins refaits — sans eux, le
catalogue des affirmations et la fraîcheur des témoins rougissent du
`pages.json` que 77548d3 périme, et que GitHub refait avant sa suite.

**Ce qui reste.**
1. L'arrondi du calendrier et la lecture des dates de la chronologie, à la
   relecture de leurs paires (sixième partie).
2. `pages.js`, ligne 7, pour une session du site (sixième partie).
3. Le profil interpolé, avec la paire de la carrière ; `point_fixe` et
   `pointFixe`, quand le coût datera ses cas types par le portage (septième
   partie).
4. Les paires suivantes de la carte attendent que le coût passe le pont ; deux
   paires de données, au propriétaire.
