# Étape 6, cinquième partie : le retrait de la saisie Python, le contexte réduit au centre du coût

**La demande.** La quatrième vague du 24 octobre 2026 : dix sessions en
parallèle, une tâche chacune, que le propriétaire ne suit pas pas à pas.
Celle-ci tient le point 3 de « Ce qui reste du premier lot » (note de la
deuxième partie) : le retrait — la référence de `test_pont.py` et de
`construire_temoins.py`, les gardes de la saisie Python, et `_depart_estime`,
que les départs de l'estimation demandent —, chaque retrait relu, les
témoins identiques à l'octet.

**Les départs de l'estimation** (4fc1fcd). `DepartEstime` et `_depart_estime`
quittent `contexte.py` pour le pilote, à côté de `ages_de_l_estimation`
(`pilote.depart_estime`) : la moitié Python des départs ne sert plus qu'à
confronter les deux moteurs (`test_estimation_du_site.py`), au bit près comme
avant. Elle se tranche avec la paire du pilote : seul le site chiffre ces
départs pour un lecteur.

**La référence** (573e981). Le pont bâtit aussi la carrière d'une saisie en
champs, comme `pont.saisies` la lit (`carrieres_des_saisies`,
`{"cle", "saisie"}`) : les carrières d'exemple du bilan figé se comparent, au
bit près, à ce que le moteur Python simule de la carrière que le portage
bâtit, et non plus à ce que la saisie Python en faisait. Le test qui
comparait au contexte Python les carrières et les paramètres des 889 témoins
se retire, avec son exception de niveau : les témoins le relaient,
identiques à l'octet (`test_les_temoins_du_portage_sont_a_jour`).
`construire_temoins.py` lit les bornes de la saisie dans le portage
(`AGE_DEBUT_MINIMAL`, `AGE_LIQUIDATION_MAXIMAL`) et ne charge plus
`saisie.py`.

**Le retrait** (be67006). Les trois gardes qui interdisaient la saisie Python tombent
avec elle : `test_estimation_officielle.py`, le budget de `test_outillage.py`,
les témoins de `test_pont.py`, qui simule désormais sans contexte.
`contexte.py` passe de 1 305 lignes à 201 : le centre du coût — les données,
un simulateur par jeu de règles, le coût, les avantages, la population —, que
la fabrique et les tests du coût lisent. Relue fonction par fonction contre
son jumeau avant de partir, de `_refus_de_pension` à `Montants`, la saisie ne
montre aucun écart de calcul ; la seule différence, déjà relevée à la
première partie, reste sans effet : `departsDeLEstimation` tait toute erreur
qui n'est pas une faute de programme, le Python seulement un refus.

**Ce que le Python expliquait.** `contexte.js` renvoyait vingt-trois fois au
Python ; chaque renvoi porte désormais ce qu'il désignait : le retraité qui
saisit sa pension d'aujourd'hui, le relevé prolongé jusqu'au départ, les
pensions étrangères qui suivent les prix, la radiation pour invalidité, la
couverture des non-résidents, la tranche du foyer et la pension saisie nette,
la cotisation de la SNCF et des mines. Son en-tête se dit « portage d'une
partie » de `contexte.py` — ce qui lit les données sous un jeu de règles — :
la saisie n'a que lui. Le commentaire de `AGREGATS_MEMORISES` en Python
comptait deux agrégats par jeu de règles ; la restitution en fait un
troisième, il le dit.

**Ce qui nommait le code.** Les trois fiches dont le champ `code` nommait les
fonctions retirées (`cotisation_maladie_des_non_residents`,
`cotisation_maladie_pensions_complementaires`,
`csg_des_pensions_selon_le_revenu`) n'y gardent, côté Python, que le barème ;
deux présomptions disent le net du portage (`valeurs.yaml`, et le tableau de
bord) ; le README, l'annexe B de l'architecture, les consignes du moteur, une
limite et deux tests disent le contexte réduit. Les entrées de
`referents.yaml` qui citent des lignes de `contexte.py` décrivent des écarts
repris, à leur date : elles restent.

**Tests.** La suite rapide, 3 060 ; les dix-neuf fichiers de la zone qui
lisent le contexte, le pont ou les fiches, 685 ; le filet du site ;
`construire_temoins.py --verifier`, à jour à chaque pas ; la conservation,
rien de perdu.

**Ce qui reste.**
1. `pages.js`, à sa ligne 7, dit encore `contexte.js` portage de
   `contexte.py` : pour une session du site.
2. `saisie.py`, la paire suivante, passe au rang 1 de la carte : rien ne
   l'importe plus, ni module, ni script, ni test. Cinq fiches le nomment
   (`python scripts/jumeaux.py saisie`), et quatre chiffres ancrés de la
   prose chargent ses constantes (`LISSAGE_MAXIMUM`, `HEURES_SMIC_PAR_MOIS`) :
   le README, `methodologie.md`, `limites/4-regimes-incomplets.md`.
3. La paire du pilote, avec les départs de l'estimation.
4. Le centre du coût garde le nom de `contexte.py`. Le mettre dans un module
   à lui toucherait `outils_web.py` et `test_web_revues.py`, que seule une
   session du site touche.
