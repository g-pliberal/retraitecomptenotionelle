# Étape 5, cinquième partie : la mémoire des calculs indexée sur le portage

**La demande.** La suite de l'étape 5 : `memoire.py` indexée sur le portage,
l'empreinte de `moteur/js`, hors de `pages.js`, et du paquet du jour
(`pont.paquet_des_donnees`, que bâtit `scripts/construire_donnees.py`). Ni le
test des références, ni le retrait de `cycle_de_vie.py`, qui suivent.

**Ce que l'empreinte suit.** `memoire.SOURCES` compte, outre `src/` et
`data/`, le moteur du portage, `moteur/js`, et la fabrique du paquet du jour,
`scripts/construire_donnees.py` ; le texte des pages, `moteur/js/pages.js`,
passe dans `HORS_DU_MODELE`, et la version de node entre dans l'empreinte avec
celle de Python. Au 19 octobre, 754 sources, dont 75 du portage. Le paquet du
jour se bâtit depuis `data/` et `src/`, que l'empreinte lisait déjà, par la
fabrique, qui seule y manquait. La version de node se lit par
`pont.version_de_node`, que la fabrique reprend au lieu de sa copie.

**Le paquet du jour, une fois par état des sources.** Il se bâtissait une
fois par processus (`functools.cache`) : une donnée retouchée pendant qu'un
processus de la suite calcule, et la mémoire aurait gardé, sous l'empreinte
des données nouvelles, une grille simulée sur le paquet des anciennes. Il se
rebâtit désormais quand la signature des sources bouge (`memoire.signature` :
le chemin, la taille et la date de chacune, en dix millièmes de seconde, sans
les lire). L'empreinte, qui les lit, aurait servi de clé ; mais le relevé de
ce que lisent les calculs gardés (`scripts/lectures_du_modele.py`), qui fait
simuler la grille au portage, les aurait toutes comptées pour lues, et chaque
fiche de règles pour lue en entier.

**Ce que le portage lit, et ce que l'empreinte ignore.** Un test nouveau
(`test_outillage.py`) suit les imports du pont (`jumeaux.JavaScript`) : chacun
des 69 modules de `moteur/js` qu'il atteint est dans l'empreinte, et aucun
n'importe `pages.js` ; six autres, hors de sa portée — les crédits des
ministères, les caractéristiques des retraités, la garantie, le lecteur PDF
et celui du relevé, la TVA —, y restent, par prudence. Une sonde de cette session, qui
n'est pas un test, a relevé ce qu'ouvre la fabrique du paquet du jour : 399
fichiers, dont deux seulement hors de l'empreinte, les crédits des ministères
et le manifeste des sources, d'où viennent les clés `credits_ministeres` et
`institutions_citees` du paquet ; le même test exige qu'aucun module atteint
ne les nomme. Un troisième fichier hors de l'empreinte qui entrerait au paquet
ne serait vu que par une sonde semblable.

**Les six conditions.** La quatrième de la note 0003, la mémoire des calculs
indexée aussi sur l'empreinte du portage, était la dernière qui manquait au
pont du coût. Le budget : l'empreinte passe, à chaud, de 36 à 46 millièmes de
seconde, la version de node et le portage compris ; la signature en prend
dix ; le paquet, trois secondes et sept dixièmes, ne se rebâtit qu'après une
retouche des sources. Pendant `regenerer.py`, le chiffrage calcule pendant que
la fabrique réécrit le bilan et les calibrations, sans condition : il rebâtit
son paquet une fois de plus, deux au pire, après ces écritures ; une lecture
des calibrations à demi écrites les fait recalibrer, sans échec (`mortalite.py`
rattrape l'erreur). Une retouche du seul portage refait désormais, en local,
les calculs gardés, le coût compris ; une retouche de `pages.js` n'en refait
aucun. Aucune dépendance nouvelle.

**Tests.** Les trois nouveaux, vus rouges pour la raison attendue : le paquet
resté celui du premier état, l'empreinte aveugle au portage, 69 modules du
pont hors d'elle. Puis, verts : la mémoire, le pont, la fabrique et la carte
des jumeaux, 88, le relevé des lectures du modèle compris, refait sous
l'empreinte nouvelle ; et 2 903 rapides.

**Ce qui suit.** Le test des références (`tests/test_cycle_de_vie_references.py`),
dont les tests rebâtissent des flux et lisent le coût en Python (première
partie de l'étape 5), à faire lire au portage ; puis le retrait de
`cycle_de_vie.py`, qui l'attend.
