# Étape 6 : les neutralisations du coût des avantages au portage — les leviers en JavaScript, la demande du pont, la décomposition sans le moteur Python

**La demande.** Le 2 novembre 2026, le propriétaire demande de faire passer
au portage ce que `avantages.decomposer` bâtit et liquide encore en Python —
la carrière de chaque case, sa liquidation au scénario 1, ses recalculs sous
les scénarios neutralisés — et la lecture des âges légaux de
`masses_anticipees`, pour que `calculer_avantages` ne bâtisse ni ne liquide
plus aucune carrière en Python quand la grille se date au portage : les
leviers en JavaScript d'abord, éprouvés par un test vu rouge, puis une
demande du pont et le branchement, chacun son commit au vert ; la table et
`moteur/donnees.json` identiques à l'octet.

**La course rouge de cd035a7.** `test_aucune_page_ne_se_decale_en_se_chargeant`
a rougi la course de GitHub sans que rien de `moteur/` ni de `donnees.json`
ait changé. Il passe trois fois sur trois ici (57, 50 et 55 s) : un aléa du
chargement dans Chromium, rien à réparer ; la course de cette session le
redira.

**Les leviers** (0192d4c). Dans `moteur/js/regimes.js`, `FichesDatees.sans`
et `Invalidites.sans`, jumeaux de ceux du Python — la copie de `Invalidites`
repart d'une mémoire des régimes vide, que le Python n'a pas ; et
`CatalogueRegimes.sansDeclaration`, jumeau de `_catalogue_sans` : chaque
période qui déclare l'avantage remplacée par une copie qui ne le déclare
plus, les autres partagées, là où le Python copie tout. Le barème de
carrière longue vidé est `new CarriereLongue({})`, un paquet sans barème ni
fiche des périodes réputées cotisées, comme le Python le lit d'un fichier
absent ; la date de la règle des parents était déjà une propriété de
l'instance (`parentsMeilleuresAnneesDepuis`). `scenariosNeutralises`, dans
`pont.mjs`, assemble les variantes comme `scenarios_neutralises`, une fois
par simulateur ; `pont.MOTEUR.neutralisant(code)` les fait appeler par
`pont.droit`, et `tests/outils_pont.py` en fait refaire chaque appel au
Python. Le test : une carrière où mord chaque levier — l'agent classé et le
militaire partis avant l'âge légal, la mère de deux enfants partie en 2030,
le salarié entré à seize ans parti à soixante, l'assuré handicapé parti à
cinquante-six, le policier, l'apprenti de trente mois —, liquidée sous
chacune des huit variantes au bit près comme le Python. Et chacune mord : le
montant, ou, pour la carrière longue, le seul motif de l'ouverture — le
scénario 1 calcule la pension d'un départ que rien n'ouvre, et ce que coûte
la carrière longue se lit dans les masses anticipées, non dans le montant.
Le levier des parents retiré, la confrontation rougit de cinq écarts. Le
moteur reste à 904 Ko compressés.

**La demande du pont** (7151b1f). `pont.avantages` reçoit de chaque case les options
de sa carrière (`_options_de_la_variante`, que `carriere_variante` lit
aussi) et les contrefactuelles que le cas type demande
(`_variantes_demandees`) : ses périodes non travaillées changées, sous le
code de chaque retrait dans la carrière qui en vise une, et les codes des
scénarios neutralisés. Le portage bâtit la carrière, l'écarte sous le motif
du Python, la liquide au scénario 1 et rend ce que la décomposition en lit
(`_Liquidee`), puis la pension et la durée requise de chaque contrefactuelle,
sur une carrière rebâtie, comme le Python la rebâtit pour chaque retrait.
Les gardes qui lisent le moteur ou la carrière bâtie — les statuts que
bonifient les fiches retirées, l'incapacité déclarée, le contrat
d'apprentissage — sont au portage (`carriereQuiPerd`) ; celles qui lisent
le cas type, son affiliation et ses interruptions, restent au Python, avec la
liste des neutralisations et la mesure : l'écart, l'AVPF retranchée, le
garde-fou de la durée requise et sa raison (`_ecarts`), que le chemin Python
partage (`recalculer`). Une contrefactuelle qui faillit arrête la demande,
comme elle arrête le Python. L'âge légal de chaque génération, que
`masses_anticipees` oppose aux départs, passe par `pont.droit`
(`scenario_actuel.ages_ouverture.age`, `ages_legaux`), une demande pour
toutes. `decomposer` n'a plus qu'un assemblage, que l'une ou l'autre voie
nourrit (`_decomposees_au_portage`, `_decomposees_en_python`).

**Le test sans les jumeaux.** Il remplace celui des cohortes datées au
portage, qu'il contient : sept cas types — dont un policier, qu'aucun cas
type de la grille n'est —, sur cinq générations ; le pilote, l'ouverture du
droit, les constructeurs de carrières, les scénarios neutralisés et le
scénario 1 du moteur Python — son constructeur, son calcul, l'accès du
simulateur — interdits ; la décomposition, ses types et ses refus, et le
coût, année par année, ceux du Python, une mesure de chaque sorte comprise,
et le refus de la jouissance militaire. Vu rouge sur `scenarios_neutralises`,
que `decomposer` bâtissait encore.

**La table.** Refaite par `scripts/construire_donnees.py` après la
sous-étape B : `data/derive/agregats.json` et `moteur/donnees.json`
identiques à l'octet, et les témoins de simulations, que rien n'a refaits.
Le coût des avantages y venait de la mémoire des calculs, qu'un test avait
remplie sous l'empreinte du code de l'étape, donc au portage ; refait à neuf
hors d'elle, au portage puis en Python, il est le même, et celui de la
mémoire aussi.

**Le temps.** Sur la grille entière — 358 couples, la jouissance militaire
refusée —, la décomposition prend 9,2 s au portage et 28,5 s en Python ; le
coût entier, 9,1 s et 27,4 s.

**Ce qui ne change pas.** Aucune règle du moteur, ni en JavaScript ni en
Python ; aucun fichier fabriqué ; aucune garde ; aucune dépendance ; aucune
règle du scénario 1. `scripts/cout_avantages.py`, qui étudie la mesure cas
par cas, garde le moteur Python.

**Tests.** `python -m pytest -m rapide`, 3 542 à chaque sous-étape, et
3 375 sous `PRESOMPTIONS_DECALEES=1` ; `node --test tests/js/*.test.js`,
115 ; les confrontations légères, 423 ; `tests/test_pont.py` et
`tests/test_avantages.py`, 66, dont les deux tests de l'étape.

**Ce qui suit.** La grille large et le coût sous un modèle modifié ; puis les
retraits, par sous-ensemble cohérent : le chemin Python de la décomposition
(`_decomposees_en_python`, `recalculer`, `scenarios_neutralises`) ne sert
plus que sous un modèle modifié, sur des données d'ailleurs, et à
`scripts/cout_avantages.py`.
