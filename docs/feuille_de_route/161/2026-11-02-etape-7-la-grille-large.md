# Étape 7 : la grille élargie au portage — `CasTypeLarge` daté et bâti, et les mesures de `scripts/grille_large.py` par le pont

**La demande.** Le 2 novembre 2026, la suite verte sur b26f9fc, le
propriétaire demande de faire passer au portage la grille élargie
(`scripts/grille_large.py`, `CasTypeLarge`), en deux sous-étapes, chacune son
test vu rouge et son commit : la datation et la construction de ses cas
types, puis les mesures du script qui interrogent encore le pilote ou le
scénario 1 du moteur Python ; la table, `moteur/donnees.json` et les témoins
identiques à l'octet.

**Ce que `CasTypeLarge` ajoute.** Sa carrière est un parcours quand elle en
décrit un — les métiers bout à bout du polypensionné, le temps partiel et le
volume de travail, le niveau, l'entrée, le service national et les natures
des années assimilées de sa génération, le Smic —, que `carriere_parcours`
bâtit sans primes projetées ; le pilote la date sur ce parcours, et l'entrée
tardive d'un fonctionnaire, sous les conventions du COR, reste la carrière
finale (`carriere_a`). Son départ attend : un plancher, l'âge légal de sa
génération et l'attente à son échelle, ou, pour le fonctionnaire civil qui
surcote, l'attente comptée du premier âge où le modèle lui sert une surcote,
qu'une recherche sur l'échéancier trouve (`debut_de_la_surcote`).

**Sous-étape A : la grille élargie datée et bâtie au portage** (9992029).
`CasTypeLarge._carriere` et `age_liquidation_pour` se coupent en ce qu'ils
décrivent — `_options_du_parcours`, `_attente_du_depart` — et en ce qu'ils
calculent ; `pour_le_portage` passe le parcours, ses métiers en données, et
l'attente. Dans `pont.mjs`, `carriereDuCasType` bâtit le parcours,
`carriereFinale` la carrière de `carriere_a`, `debutDeLaSurcote` porte la
recherche, et `ageDuCas` pose l'attente sur l'âge du pilote, sauf sous l'âge
écrit ; `agesDeDepart` et `carrieresDeLaGrille` la lisent. Un âge que
l'attente fixe est un flottant en Python, même égal à l'âge écrit : le
portage le dit (`attendu`), et `castypes.age_lu` le garde tel quel ;
`pont.ages_de_depart` rend pour cela les clés des âges attendus. Le plancher
se calcule en Python, qui garde la définition du cas type ; la recherche et
le maximum, au portage. `castypes.batie_au_portage` ne demande plus
`type(cas) is CasType` : il suffit que chacune des méthodes qui datent et
bâtissent une carrière (`DATENT_ET_BATISSENT`) vienne de la classe qui écrit
`pour_le_portage`, ou d'une de ses parentes (`decrit_au_portage`) — une
sous-classe qui récrirait sa carrière sans lui resterait au Python. Le test :
neuf cas types de la grille élargie, un par mécanisme, sur trois
générations ; leurs cases et leurs âges, sous le droit et sous l'âge écrit,
chaque âge sous son type ; la grille bâtie du coût et sa simulation, sous les
conventions du COR : ceux du Python, au bit près, sans le pilote, l'ouverture
du droit, les constructeurs, l'échéancier ni le scénario 1 Python. L'attente
ou la recherche retirées du portage, il rougit.

**Sous-étape B : les mesures du script par le pont** (36e25f0). `Departs` lit les
départs qu'une mesure demande — l'âge, et ce que l'échéancier lit au départ
(`AuDepart`) — d'une seule demande au portage (`pont.departs_des_cas`), quand
la grille s'y date ; en Python sinon, paresseusement, dans l'ordre où la
mesure les lisait, chaque refus levé là où son calcul le levait. Une mesure
que la mémoire garde la fait sur le paquet des données du jour (`du_jour`) ;
un appel isolé, sur `moteur/donnees.json`, par le pont gardé ouvert, comme
`castypes.cases_de_la_grille` : sur le paquet du jour, chaque appel des
essais relançait node et relisait le paquet, et la course du fichier passait
dix minutes. Le pilote Python, de même, cherche sa surcote en Python
(`_debut_de_la_surcote_en_python`) : demandée au pont, appel par appel, elle
mêlait les deux moteurs et ralentissait la population. `decote_a_l_ouverture`, `ouvertures_decotees`,
`avance_par_l_inaptitude`, `avances_par_l_inaptitude`, `avec_decote`,
`_proratisations`, `condition_au_depart` et `_conditions` le lisent ;
`debut_de_la_surcote` passe au portage par sa demande
(`pont.debuts_de_la_surcote`), et `_depart_et_surcote`, dans le test, par
`Departs`. Les tables de l'âge légal et de l'âge d'annulation que
`condition_au_depart` lit restent des lectures de données. Le test : les dix
mesures sur l'échantillon et deux cas de plus — l'agent de conduite, qui
part à l'ouverture de son statut, une carrière courte —, une décote, une
avance, chaque condition et une surcote servie comprises : celles du
Python, chaque type compris, les jumeaux interdits. Les deux durées
échangées au portage, il rougit.

**Ce qui reste au Python dans le test de la grille élargie.** Ses autres
essais éprouvent les cas types eux-mêmes — la carrière qu'ils bâtissent,
l'âge que leur pilote fixe, un à un — par le moteur Python, qui garde ses
jumeaux ; ils passeront au portage avec le retrait de ces jumeaux.

**La table.** Refaite par `scripts/construire_donnees.py` après les deux
sous-étapes : `data/derive/agregats.json` et `moteur/donnees.json`
identiques à l'octet, et les témoins de simulations, que rien n'a refaits.
La grille élargie n'y entre pas ; les cas types du dépôt, qui passent par
les mêmes demandes du pont, s'y datent comme avant.

**Le temps.** `tests/test_grille_large.py` et `tests/test_pont.py` passaient
en 3 min 6 s pour 89 essais de la grille élargie, avant l'étape ; avec les
deux de l'étape, en 3 min 10 s puis 3 min 27 s, ce dernier en même temps
que les tests de la feuille de route. Les deux tests de l'étape prennent
ensemble 21 s, Python et portage compris.

**Ce qui ne change pas.** Aucune règle du moteur, ni en JavaScript ni en
Python ; aucun fichier de `moteur/js/` ; aucune garde ; aucune dépendance ;
aucune règle du scénario 1.

**Tests.** `node --test tests/js/*.test.js`, 115 ;
`tests/test_grille_large.py` et `tests/test_pont.py`, 127 après la
sous-étape A, 128 après la B ; `python -m pytest -m rapide`, 3 542 à chaque
sous-étape ; `tests/test_donnees.py`, `tests/test_outillage.py`,
`tests/test_prose.py` et `tests/test_carte_du_depot.py`, 270.

**Ce qui suit.** Le coût sous un modèle modifié ; puis les retraits, par
sous-ensemble cohérent.
