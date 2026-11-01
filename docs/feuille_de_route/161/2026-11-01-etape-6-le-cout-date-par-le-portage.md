# Étape 6 : le coût daté par le portage — ses cas types datés et sa grille bâtie au portage, la table des agrégats identique à l'octet

**La demande.** Le 1er novembre 2026, le propriétaire valide les deux choix
que la session du lot B lui soumettait — `tests/conftest.py` laissé intact, la
copie de `DECALAGES` dans `pont.mjs` tenue par `tests/test_pont.py` — et
demande l'étape suivante du bloc « Reprise » : que le coût date ses cas types
et bâtisse les carrières et les départs de sa grille par le portage, par
`pont.py` et `pont.mjs`, en s'appuyant sur `pointFixe`, avec la même méthode —
un commit au vert par sous-étape, chaque âge, chaque carrière et
`data/derive/agregats.json` identiques à l'octet, un test sans les jumeaux — ;
et, si la paire `point_fixe` / `pointFixe` s'en trouve libérée, d'en retirer
le jumeau Python selon la méthode des notes 0003 et 0005, sinon de le laisser
prêt pour l'étape des retraits.

**La datation** (861286b). `ageDeDepart` et `descendre` reviennent au pilote
du portage (`moteur/js/pilote.js`), jumeaux de `age_de_depart` et `descendre`
(`pilote.py`) : le départ des cas types en était parti le 11 octobre 2026 avec
le portage du coût (action 150). `agesDeLEstimation` emprunte désormais
`descendre`, la boucle de son premier âge, qui était la même. Le Python garde
la définition des cas types et leurs conventions : `CasType.pour_le_portage`
décrit au portage ce que la règle de départ lit et les options de la carrière
d'un seul statut, sans l'âge ; `castypes.primes_projetees_en_donnees` lui
passe, année par année, le traitement relatif que les conventions du COR font
lire à `primes_projetees` (`primesProjetees`, dans `pont.mjs`). `pont.ages_de_depart`
fait dater. Sur les 2 610 cohortes de la grille du coût — ses dix-huit cas
types, nés de 1878 à 2022 —, sous les paramètres de la projection comme sous
ceux de référence, et sous les deux variantes, aucun âge ne s'écarte de celui
du pilote Python, au bit près, et aucune cohorte n'est refusée ; le portage
date la grille en 5 secondes, le Python en 18. Quinze cohortes descendent d'un
an en un an sous l'âge écrit (l'artisan né en 1911, le contractuel né en
1884…). Deux chemins du pilote ne sont pris par aucune case — la reprise à
l'âge d'annulation de la décote, la descente à la carrière longue d'une
carrière qui ne valide plus — : le test les refait au portage sur les deux
carrières que `tests/test_liquidation.py` tire du texte, 67 ans (L. 351-8)
et 60 ans (L. 351-1-1). Le moteur du site pèse un kilo-octet compressé de
plus (903, puis 904, dans `README.md`), chargé à la demande : le pilote est
le lieu du départ des cas types, que la fabrique seule fait tourner, et
`descendre` y sert les deux départs.

**Les carrières** (bf19ad7). `pont.carrieres_de_la_grille` date et bâtit
chaque case : d'un seul statut, ou de deux métiers quand un fonctionnaire
entre tard dans son régime sous les conventions du COR — le Python les décrit
(`CasType._options_d_entree_tardive`, tiré de `_carriere_entree_tardive`) — ;
ses primes projetées ; les deux motifs de `castypes.carriere_de_la_grille`,
au mot près ; les deux carrières que l'âge légal de la proposition en dérive,
poursuivie jusqu'à lui ou attendue sans activité ; et, d'une cohorte voisine,
l'année et le mois de son départ. Sur toute la grille, 498 carrières, leurs
prolongations, 2 006 départs voisins et 106 motifs sont ceux du Python : une
carrière relue sous ses types (`carriere_des_donnees`) est égale, champ par
champ, à celle qu'il bâtit. Seul l'âge écrit en entier dans un cas type
(`age_liquidation=64`), que le pilote Python garde tel quel quand le droit ne
le déplace pas, revient en flottant : la valeur est la même, et node lit les
deux de même. 8,5 secondes, relecture comprise, contre 23.

**Le coût branché** (02b0864). `cout._grille_batie` bâtit la grille d'une seule
demande au portage quand elle s'y simule (`_par_le_portage`) et que ses cas
types sont des `CasType` tels quels (`_batie_au_portage`) ; par le moteur
Python sinon, comme avant. `CasTypeLarge` (`scripts/grille_large.py`)
redéfinit la datation et la carrière, que le portage ne verrait pas : la
grille large reste datée et bâtie en Python, puis simulée au portage.
`_carrieres_du_cout`, `_departs`, `_propositions` et `_nees_toute_l_annee`
lisent la grille bâtie ; `_autre_volet` reçoit si l'âge légal reporte le
départ, au lieu de prolonger la carrière une seconde fois. Le test sans les
jumeaux (`test_le_cout_date_et_bat_sa_grille_par_le_portage_sans_les_jumeaux`)
interdit le pilote Python, l'ouverture du droit qu'il interroge, les
constructeurs de carrières, la projection des primes et le moteur Python : la
grille d'essai et ses cohortes nées toute l'année sont, couple pour couple,
celles que le Python date, bâtit et simule sous un modèle modifié. La table
des agrégats, refaite par `scripts/construire_donnees.py` sous le code
branché, sans rien de gardé pour lui dans la mémoire des calculs — la grille
du coût s'y recalcule par le portage —, est identique à l'octet, comme les
trois fichiers que l'étape écrit avec elle (`moteur/donnees.json`,
`equilibre.json`, `calibrations_mortalite.json`), en quatre minutes. Le
contrôle de toute la grille, que la session avait mené hors du dépôt, est
devenu un test du niveau complet, que GitHub joue
(`test_le_portage_bat_toute_la_grille_du_cout_comme_le_python`,
`tests/test_cout.py`, 35 secondes) : la grille bâtie au portage et celle que
le Python bâtit sous un modèle modifié sont égales, cohorte par cohorte.

**La paire du pilote n'est pas libérée.** Le Python date encore des cas types
là où le portage ne le fait pas : la grille des carrières types de la table
(`castypes.cases_de_la_grille`, et les âges qu'écrit `figer_cas_types`), le
coût des avantages (`avantages.py`, par `_carrieres_voisines` et
`age_liquidation_pour`), la grille large, les dates des départs des facteurs
de la dépense (`facteurs_depense.dates_des_departs`), les études
(`scripts/cycle_de_vie.py`, `cout_avantages.py`, `mortalite_population.py`…),
et le coût sous un modèle modifié ou sur des données d'ailleurs ;
`python scripts/jumeaux.py pilote` en compte 36 scripts et 96 fichiers de
tests. Le jumeau reste donc, prêt pour les retraits : `pointFixe`, `descendre`
et `ageDeDepart` font foi, tenus au bit près par `tests/test_pont.py`, et
chacun de ces chemins se branche sur `pont.ages_de_depart` ou
`pont.carrieres_de_la_grille` sans rien ajouter au portage.

**Ce qui ne change pas.** Aucune règle du moteur, ni en JavaScript ni en
Python ; aucun fichier fabriqué ; aucune garde, `tests/conftest.py` compris ;
aucune dépendance ; aucune règle du scénario 1.

**Tests.** `python -m pytest -m rapide`, 3 538, à chaque sous-étape ;
`python -m pytest -m site`, 36, et `node --test tests/js/*.test.js`, 115 —
le pilote du portage sert aussi « Mon estimation retraite » ;
`tests/test_pont.py`, `tests/test_jumeaux.py`, `tests/test_liquidation.py`,
`tests/test_estimation_du_site.py` ; dans `tests/test_cout.py`, le test de
toute la grille et les deux que le branchement touche, dont celui qui date
chaque cohorte au droit de sa génération, récrit sur la grille bâtie.

**Ce qui suit.** Un autre chemin pour ce que le Python date, bâtit et simule
encore — la grille des carrières types, le coût des avantages, la grille
large, ce que `_simulations_en_python` simule sous un modèle modifié — ; puis
les retraits, par sous-ensemble cohérent, la paire du pilote comprise.
