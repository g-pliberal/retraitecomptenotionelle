# Étape 6, la paire de la carrière : relue fonction par fonction, le profil interpolé au bit près

**La demande.** La vague du 28 octobre 2026 : une session par tâche, que le
propriétaire ne suit pas pas à pas. Celle-ci tient le reste « le profil
interpolé, avec la paire de la carrière » (huitième partie) : la relecture de
`carriere.py` et de `carriere.js` d'abord, chaque différence tranchée contre
la source et la fiche, l'erreur corrigée dans le jumeau qui reste par son
test, vu rouge ; aucun jumeau retiré.

**Le relevé.** `python scripts/jumeaux.py carriere` : 3 579 lignes de Python,
2 885 de JavaScript, rang 62 sur 70. Le Python est atteint par le coût et par
la fabrique, par quarante scripts et cent quarante-huit fichiers de tests.
Les tests de concordance en exécutent 91 % des lignes Python (1 525 sur
1 685) et 94 % des lignes JavaScript (1 737 sur 1 845), au commit 30717ac.
Jamais confrontés côté Python : la boucle de `limiter_chomage_non_indemnise`,
`_lignes_apres_depart`, le profil plat, le profil inconnu et
`bornes_deformation` ; côté JavaScript, l'attente sans activité de
`prolongee`, l'année de deux statuts agricoles et celle du décès de
l'exploitant.

**La relecture.** Fonction par fonction, avec la classe `Affiliations`, dont
le jumeau est dans `regimes.js`, et les jumeaux de `chargement.py` que
`carriere.js` porte : le chômage aux complémentaires, l'assiette minimale et
ses dispenses, le micro-entrepreneur. Tout concorde, aux structures près
(tuples et tableaux, dictionnaires et `Map`), sauf le profil interpolé et les
noms hérités du prototype, tranchés ci-dessous, et six écarts qu'aucune donnée
n'atteint, laissés :
- `round` arrondit une moitié au pair, `Math.round` vers le haut, dans
  `prolongee`, `date_de_service`, `duree_de_service_avant`, les plafonds et les
  trimestres écoulés ; mais une part d'année y vaut des mois sur douze, et
  `part × 12` n'est jamais une moitié. `en_mois` est à la paire du calendrier.
- `trimestres_par_annee` lit le plafond d'une année absente de la carrière par
  un `KeyError` en Python, quatre dans le portage : chaque appelant passe des
  lignes de la carrière.
- Une table vide (`seuil_pass`, `services_passes`) est fausse en Python, vraie
  en JavaScript : les données n'en écrivent aucune.
- `rapport_validation_micro` : une année manquante entre la première et la
  dernière ferait un `KeyError` d'un côté, NaN de l'autre ; les tables sont
  contiguës, de 2018 (2023 pour la Cipav) à 2026.
- `depuis_chronologie` : le portage bâtit les lignes d'après le départ avant de
  refuser des périodes sans départ ; seul le message différerait, si les deux
  fautes se rencontraient.
- `Carriere.__post_init__` trie en place la liste qu'il reçoit, le portage la
  copie : aucun résultat n'en dépend.

**Le profil interpolé** (117bdbe). Entre deux milieux de tranche, le Python
écrivait `bas + (haut − bas) × (âge − âge_bas) / (âge_haut − âge_bas)`,
multipliant avant de diviser ; le portage divise d'abord, la position de l'âge
dans la tranche. Aucune source ne tranche : ce sont deux écritures de
l'interpolation linéaire que la docstring dit, exactes aux milieux de tranche,
à 0,65 ulp au plus de la valeur exacte. La mesure tranche. Sur les onze
profils publiés, aux âges entiers de 14 à 80 ans, ceux des lignes, elles
diffèrent à quatre âges : le cadre à 28 ans, la profession intermédiaire à 33,
l'État à 31, l'hospitalière à 61. Contre l'interpolation exacte des décimales
publiées, chacune tombe deux fois sur le flottant le plus proche ; contre
celle des flottants qu'on en lit, le portage trois fois, le Python une. Aux
demi-années, sept écarts : cinq au portage, deux au Python, des deux façons ;
l'agent de catégorie A, à 43 ans et demi, vaut 0,96135 dans le portage et
0.9613499999999999 dans le Python. L'écriture du portage n'est jamais exacte
moins souvent, et c'est le jumeau qui reste : le Python la prend. Elle
n'arrondit pas au plus près partout — à 31 ans, l'agent de l'État reçoit du
portage le flottant voisin —, et le test ne le prétend pas.

Ce que l'alignement déplace, mesuré par `regenerer.py` dans un worktree au
commit de l'alignement : rien de ce qu'un script fabrique, ni le paquet et
ses agrégats, ni les témoins, ni le chiffrage, ni les pages, ni la prose.
Les carrières types que le Python bâtit pour le coût changent au dernier bit
dix-neuf lignes — le cadre et le libéral à 28 ans, le militaire à 31, à
chaque génération —, et deux de leurs simulations un détail, au dernier bit
aussi : le capital Agirc et la pension d'un régime du cadre de 1990, les
cotisations employeur du militaire de 1990 ; aucun total que la table garde. Les carrières du site, que bâtit le portage, ne
bougent pas, ni donc les témoins des simulations : aucun commit de témoins.
Aucune fiche ne porte le profil, convention du modèle et non règle de droit.

**Les noms hérités du prototype** (ea0e60b). Le portage lit ses tables dans
des objets de JavaScript, qui héritent de leur prototype : `constructor`,
`toString`, `__proto__` y sont des clés, que `table[nom]` et `nom in table`
trouvent, quand les dictionnaires du Python ne les connaissent pas. Sous un
tel nom, `profilSalaire` calculait au lieu de refuser le profil ; la dispense
de l'assiette minimale, la part validée et le taux de solidarité du chômage,
le forfait du micro-entrepreneur levaient une `TypeError` ; la nature du
chômage était une fonction ; une année de relevé valait NaN trimestres, que le
Python tient sans activité ; une affiliation de ce nom avait un libellé et
des régimes. Aucune saisie n'y mène : la page ne laisse passer que les noms
de ses listes, `contient` vérifie chaque statut avant `periodes`, et les
carrières du pont arrivent avec leurs lignes. Le portage ne lit plus que les
clés propres de ses tables (`propre`, le `dict.get` du Python), et
`Affiliations` refuse un statut que le fichier ne nomme pas (`_profil`),
comme le Python.

**Tests.** `tests/test_moteur.py`, trois, de la suite rapide : la valeur posée
à la main, 0,7909 + 0,2013 × 7 / 8,5 pour la profession intermédiaire de
33 ans ; les deux jumeaux au bit près, à chaque demi-année de 14 à 80 ans,
sous huit années, pour chaque profil et chaque affiliation que les tables
nomment, et leurs bornes, 313 écarts avant ; les cinq noms hérités sous onze
lectures, 55 écarts avant. Chacun vu rouge pour sa raison, puis vert. La suite
rapide, 3 410 ; celle du site, 36 ; les confrontations légères, 405.

**Ce qui reste.**
1. La paire ne se retire pas : le coût bâtit ses carrières types par le
   Python (`castypes.py`) avant de les simuler au pont.
2. Avant le retrait, figer par des témoins ce que la concordance n'exécute pas
   côté Python (le relevé, ci-dessus).
