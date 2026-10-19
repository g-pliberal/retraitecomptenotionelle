# Étape 5, quatrième partie : la grille du coût passe le pont, ses carrières en données

**La demande.** La suite de l'étape 5, sans `memoire.py`, qui suivra : la
grille du coût, sous les conventions de projection du COR, dont les carrières
se déforment en Python (`primes_projetees`, l'entrée tardive) et devaient
passer au portage en données, pour qu'il les lise au lieu d'en garder une
copie ; avec elle, l'engagement acquis du bilan, qui la lit. Un remaniement :
aucun résultat ne bouge.

**Ce que le coût lisait du moteur Python.** La grille (`cout._pensionnes`) lit
chaque comparaison en profondeur : la pension de chaque système en euros
constants ; la proposition sur la carrière où elle se calcule, sa garantie,
son compte et son pilier, et le report de l'âge légal ; ce que le droit en
vigueur prélève, année par année ; la part de chaque régime ; la population
de la mortalité du diviseur. Et la proposition seule sur des carrières qu'il
dérive de la case : l'attente de l'âge légal sans activité, et l'autre côté
de la bascule, sans report ou reporté.

**Les carrières en données.** Le pont relit une carrière telle que le Python
l'a faite (`pont.carriere_en_donnees`, `carriereDesDonnees` de `pont.mjs`) :
chacun de ses champs, chacune de ses lignes entière, et la chronologie dont
elle est la vue, déjà complétée. Le portage ne garde copie ni de
`primes_projetees` ni de l'entrée tardive : il simule les carrières qu'on lui
donne, et celles que le coût dérive de chaque case, que le Python construit
aussi. Les paramètres passent sous leurs noms (`pont.parametres_en_donnees`) :
les 74 du Python, hors la racine des données, sont ceux du portage, et ceux
de référence y valent `PARAMETRES_DEFAUT`, valeur pour valeur ; un paramètre
que le portage ne connaîtrait pas arrête le pont.

**Le contrat.** Une lecture nouvelle du pont, `grille_du_cout`, rend de chaque
case ce que le coût lit ; son jumeau Python, `cout._simulations_en_python`,
tire le même contrat du moteur Python. Le Python construit
(`_carrieres_du_cout` : les cases, les départs de leurs cohortes, les carrières
des propositions, `_propositions`), le portage simule (`_simulations`), le
Python assemble (`_volet`, `_reporte`, `_autre_volet`, `_survies`,
`_parts_regimes`, qui lisent le contrat). Seule la comparaison refuse une
case, comme avant. Les montants du contrat sont des flottants des deux
côtés : le moteur Python tenait pour entier le zéro des frais de gestion du
pilier l'année où il s'ouvre, que les masses ne lisaient qu'en le multipliant.

**Le moteur Python, quand le portage ne voit pas.** Trois scripts remplacent,
le temps d'un contexte, une fonction du moteur Python et lisent le coût qui
en sort : `solde_fusion.py`, le taux du régime unique ;
`proposition_prospective.py`, le scénario 6 ; `stock_age_legal.py`, les droits
figés. Et `facteurs_depense.py --sans-suspension` calcule sur une copie
retouchée des données. Le portage ne voit ni l'un ni l'autre : sous
`memoire.modele_modifie()`, que prennent aussi les tests qui demandent
`monkeypatch`, ou sur des données d'ailleurs, la grille se simule par le
moteur Python (`cout._par_le_portage`, `memoire.modele_intact`). Ce n'est pas
un repli : sans node, la grille du modèle intact s'arrête. `solde_fusion.py`
gardait la grille Python pour en relire le compte du scénario 4 ; il le relève
désormais au passage de la simulation, toujours une seule fois.

**Le paquet du jour.** Le portage simule la grille sur le paquet des données
du jour (`pont.paquet_des_donnees`), que la fabrique bâtit une fois par
processus, et non sur `moteur/donnees.json`. Celui du dépôt différait, au
début de cette session, de ce que les données donnaient, vingt-huit envois
après la dernière fabrique de GitHub ; et la fabrique l'écrit pendant que le
chiffrage calcule le coût, en parallèle (`regenerer.py`). Elle le bâtit dans
un processus à elle, comme node fait tourner le moteur JavaScript dans le
sien : ce qu'elle lit pour le site seul, les crédits des ministères et le
manifeste des sources, qu'aucun calcul ne lit, n'entre ni dans les mémoires
des chargeurs ni dans le relevé des lectures du modèle (`test_outillage.py`),
qui les avait vus tant qu'elle le bâtissait dans le processus du calcul ; des
fiches, elle ne lit aucun champ documentaire.

**Les six conditions, pour la grille du coût.** Les données : les carrières,
les paramètres et le contrat, chaque nombre sous son type (`test_pont.py`).
L'identité : la grille entière, sous sept variantes — centrale, départ à
l'âge écrit, reportés tous en emploi, bascule en 2030, sans âge légal,
espérance de vie basse, rattachement par la pension —, sort au bit près de
l'ancienne, ordre et types compris, ce zéro excepté ; les quatre fichiers de
la fabrique, bilan et engagement acquis, agrégats, paquet, calibrations, à
l'octet de l'ancien code ; `solde_fusion.py` sous les barèmes A et C, le coût
prospectif et le stock à l'âge légal, à l'identique. Le budget : la grille de
30 à 16 s, 18 avec le paquet du jour, dont 12 s de construction en Python, le
pilote des cohortes voisines surtout, et 4 s par le pont ; au départ à l'âge
écrit, de 20 à 7 s ; la fabrique sans mémoire, de 426 à 267 s ; les trois
scripts qui restent au moteur Python, de 36 à 34 s chacun. La mémoire : celle
de la fabrique suit `moteur/js` pour le chiffrage ; celle des calculs ne suit
encore ni le portage ni le paquet du jour, c'est la suite. Sans node :
`PontIndisponible`, sans repli. Aucune dépendance nouvelle.

**Tests.** Avant le premier envoi, 2 880 rapides, et un échec venu d'ailleurs,
le paquet du dépôt en retard sur les données, refait depuis. Avant le second,
2 886 rapides ; le pont, la fabrique, la carte des jumeaux et le relevé des
lectures du modèle ; les confrontations légères, 383 ; les fichiers du coût,
du bilan, des agrégats, des trois scripts, des facteurs de la dépense et des
contrôles par Ancetre et l'EACR, 256, et un échec antérieur à ce changement,
au même chiffre sans lui : la dette de 2070 que l'accueil cite, 75 %, quand le
modèle en donne 76, une mesure que la fabrique de GitHub récrit.

**Ce qui suit.** `memoire.py` indexée sur le portage : l'empreinte de
`moteur/js`, hors `pages.js`, et du paquet du jour, que bâtit
`scripts/construire_donnees.py`. D'ici là, une retouche du seul portage ne
refait pas en local un coût gardé ; GitHub, sans mémoire, refait tout. Puis le
test des références et le retrait de `cycle_de_vie.py`, qui l'attendaient. Le
pilote des départs et le coût des avantages restent au moteur Python ; les
contextes qui en remplacent une fonction devront, au retrait de leur paire
(étape 6), passer par des paramètres que le portage connaisse.
