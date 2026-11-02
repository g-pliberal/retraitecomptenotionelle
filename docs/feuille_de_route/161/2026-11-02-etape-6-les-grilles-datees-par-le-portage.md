# Étape 6 : les grilles datées par le portage — les carrières types de la table, les départs des facteurs de la dépense, les cohortes du coût des avantages

**La demande.** Le 2 novembre 2026, la course de GitHub sur 0454c0c verte
(9c13a09), le propriétaire valide les trois choix de l'étape précédente — la
projection des primes et les deux motifs d'écart dans `pont.mjs`, tenus par
les tests ; la garde sur `CasType`, qui laisse `CasTypeLarge` au Python ; le
moteur à 904 Ko — et demande de brancher sur `pont.ages_de_depart` et
`pont.carrieres_de_la_grille` ce qui n'ajoute rien au portage : la grille des
carrières types de la table, les dates des départs des facteurs de la
dépense, `_carrieres_voisines` qu'utilise le coût des avantages ; puis de
regarder ce que `avantages.py` date et simule encore en Python, et d'en faire
passer au portage ce qui tient proprement dans la session, ou d'ouvrir le
mécanisme de neutralisation dans le pont s'il demande une sous-étape à lui ;
un commit au vert par sous-étape, `agregats.json` et les témoins identiques à
l'octet.

**Le prédicat du portage.** `cout._par_le_portage` devient
`pont.par_le_portage`, que le coût, la table, les facteurs et les avantages
lisent ; `cout._batie_au_portage` devient `castypes.batie_au_portage`. Deux
fonctions de `castypes` servent les trois branchements :
`departs_au_portage`, l'âge, l'année et le mois du départ de chaque cohorte,
datée et bâtie au portage, les cases que le droit écarte sous leur motif ; et
`age_lu`, l'âge sous le type du Python. Le pilote Python rend l'âge écrit
lui-même quand le droit ne le déplace pas — un entier, souvent —, et la table
l'écrit sans décimale : treize des quatre-vingt-onze âges de la grille des
carrières types. `age_lu` rend l'âge écrit tel qu'il est écrit quand le
portage part à cet âge ; sur les 5 220 cohortes de la grille du coût, sous les
paramètres de référence et ceux de la projection, la règle refait chaque type
et chaque valeur du pilote Python. Sans paquet, la datation lit celui du
dépôt, comme le pont ; la fabrique lui passe le sien.

**La grille des carrières types** (e26f0a8). `cases_de_la_grille` date et
écarte ses cases au portage ; `ages_de_la_grille` donne à `figer_cas_types`,
qui ne calcule plus rien, l'âge de chaque case, celles que le droit écarte
comprises. Le test sans les jumeaux étend la grille aux générations 1880 et
1885, où le droit écarte des cases, sous chacun des deux motifs.

**Les départs des facteurs de la dépense** (ed2d727). `dates_des_departs`
fait dater et bâtir ses cohortes au portage, d'une demande, sous ses trois
formes — la grille, l'entrée dans l'emploi décalée comme celle de l'EIC, le
départ dès l'ouverture du droit. Les 2 490 dates de chaque forme, et les 724
de `dates_a_l_age_legal`, sont celles du Python ; le portage les date en six
à neuf secondes, le Python en dix-huit ou dix-neuf. Les facteurs n'entrent pas
dans la table.

**Les cohortes du coût des avantages** (98cbf50). `avantages.decomposer`
fait dater chaque case et ses cinq cohortes au portage, d'une demande, au lieu
du pilote Python et de `_carrieres_voisines` ; `_departs_des_cohortes` lit le
départ de chaque cohorte. Les 358 couples de la décomposition sont ceux du
Python, chaque âge sous son type. `_carrieres_voisines` ne sert plus que là où
la grille se date en Python.

**La table.** Refaite par `scripts/construire_donnees.py` après chacune des
deux sous-étapes qui la touchent, la grille des carrières types et le coût des
avantages : identique à l'octet, `moteur/donnees.json` aussi. Aucun fichier
de `moteur/js/` n'a changé, et les témoins non plus.

**Le coût des avantages : les neutralisations demandent une sous-étape à
elles.** `decomposer` bâtit encore en Python la carrière de chaque case
(`carriere_variante`), la liquide au scénario 1 (`total_contributif`,
`avantages_appliques`, `trimestres_requis`, `motif_ouverture`) et la
recalcule sous chaque neutralisation (`recalculer`) : par la carrière, ses
périodes non travaillées remplacées ; ou sous un scénario 1 que
`scenarios_neutralises` modifie — le catalogue privé de la déclaration
`categorie_active` (copie profonde), la date d'entrée en vigueur de
`PARENTS_MEILLEURES_ANNEES_DEPUIS` repoussée, le barème de la carrière longue
vidé, la fiche du handicap retirée (`Invalidites.sans`), celles des
bonifications des emplois classés et des militaires et celle de
l'apprentissage retirées (`FichesDatees.sans`). Le portage porte les mêmes
tables (`fichesDatees`, `invalidites`, `carriereLongue`,
`parentsMeilleuresAnneesDepuis` dans `scenario-actuel.js`), mais ni `sans`
sur ses fiches et ses invalidités, ni catalogue privé d'une déclaration, ni
barème vidé : ces leviers s'écrivent d'abord en JavaScript, jumeaux de ceux du
Python, puis une demande du pont rend, de chaque case, ses parts au scénario 1
et sa pension sous chaque neutralisation, le Python gardant la liste des
neutralisations, leurs conditions et la cascade. `masses_anticipees` ne lit du
moteur que l'âge légal de chaque génération (`scenario_actuel.ages_ouverture`),
que la même demande peut servir. Rien n'en est commencé : la sous-étape
s'ouvre dans une session neuve.

**Ce qui ne change pas.** Aucune règle du moteur, ni en JavaScript ni en
Python ; aucun fichier fabriqué ; aucune garde ; aucune dépendance ; aucune
règle du scénario 1.

**Tests.** `python -m pytest -m rapide`, 3 539, 3 540 puis 3 541, à chaque
sous-étape ; `tests/test_pont.py`, dont les trois tests sans les jumeaux de
l'étape ; `tests/test_avantages.py` et `tests/test_facteurs_depense.py`, 68.

**Ce qui suit.** Les neutralisations du coût des avantages au portage, leur
sous-étape ; puis la grille large et le coût sous un modèle modifié ; puis les
retraits, par sous-ensemble cohérent, la paire du pilote comprise.
