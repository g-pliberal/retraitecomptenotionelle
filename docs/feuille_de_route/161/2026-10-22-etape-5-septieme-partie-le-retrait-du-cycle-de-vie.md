# Étape 5, septième partie : le retrait de `cycle_de_vie.py` — ses tests au portage, ses explications dans le JavaScript

**La demande.** La vague du 22 octobre 2026 : la session de suivi « Qu'est-ce
qu'il reste à faire ? » lance, sur la demande du propriétaire (« Lance une
session par action qui n'a pas besoin de moi »), une session par action
qu'une session peut avancer sans lui. Celle-ci tient l'action 161 : le retrait
de `cycle_de_vie.py`, que sept fichiers de tests lisaient encore, après avoir
vérifié qu'il ne gêne ni l'indice majoré ni le solveur inverse, que le bloc de
l'étape 10 de l'action 138 place avant lui.

**Ce que le retrait ne gêne pas.** Ni le coût, ni la fabrique, ni aucun
script n'atteignaient le module : sept fichiers de tests seuls l'importaient.
L'indice majoré est un champ de la saisie des fonctionnaires (`saisie.py`,
`saisie.js`, le traitement indiciaire du droit), le solveur inverse celui des
leviers budgétaires que la page Coût résoudrait à l'envers (le registre, au
chantier « 138.10 ») : ni l'un ni l'autre n'atteint le cycle de vie. Le
dépliant « Partir plus tôt ou plus tard », s'il gagne les conventions du COR
ou les systèmes 5 et 6 (point 5 de l'étape 10), se testera contre le portage.

**Brancher** (e79e721, b642ebd). Les prélèvements historiques, la date
d'entrée, la fiche des libéraux et le dépliant des âges de départ lisent le
portage par le pont du site (`web/site.py`), qui bâtit les carrières chez lui
et rend ses `Map` en dictionnaires ; leurs valeurs attendues ne changent pas.
Une mutation passagère du portage fait rougir six tests des pensions et quatre
des nets. Le test du dépliant, lui, compare désormais la page à la fonction
qu'elle appelle : il ne tient plus que le rendu et les âges, que le pilote du
Python confronte ; les valeurs, les essais du portage. Le script des cas types
se confrontait au jumeau ; il se confronte à la simulation du Python, qui
garde ses deux moteurs (`pont.carrieres`), à ses années cotisées, et à ses
étages du départ, posés à la main sur elle — une mutation des étages rougit.
La concordance (`tests/test_cycle_de_vie_portage.py`) ne garde que ses trois
paires vivantes, les contributions d'équilibre, l'impôt et l'histoire des
prélèvements, dont la fabrique et le coût lisent le Python : de 30 à 3 s.

**Les tests du module.** 52 de ses 54 tests, traduits contre le portage dans
`tests/js/cycle-de-vie.test.js`, que `node --test` fait tourner avec les autres
essais, au filet du site et non plus à la suite rapide : une retouche du module
se teste par `node --test tests/js/cycle-de-vie.test.js`. Mêmes valeurs
attendues, mêmes tolérances, et des assistants qui
rendent ce que le Python écrit sans y penser — `pytest.approx`, la somme
compensée de `sum`, l'arrondi au pair de `round`, une clé absente qui lève.
Deux adaptations : le refus d'une convention après impôt cite l'appel du
portage, `{impot: 'prix'}` ; la part de l'impôt que supporte la pension,
privée dans le portage, se pose à la main d'après sa définition. Les deux cas
types qu'ils balaient, que seul `castypes.py` porte, y sont recopiés avec leur
source. Les deux tests du jeu de l'OCDE, qui ne portent que sur `DonneesMacro`,
vont à `tests/test_donnees.py`, et ce que la concordance exigeait de ses
carrières devient quatre essais. 56 essais, 8 s. De 53 valeurs attendues
altérées une à une, 50 font rougir leur essai ; les trois autres sont
équivalentes sur les données.

**Les explications.** Le JavaScript se disait « portage de
`cycle_de_vie.py`, qui fait foi et dit le détail » : le détail passe chez lui.
Le docstring du module Python devient son en-tête, et son histoire de portage
un dernier paragraphe, « Le seul exemplaire du cycle de vie » ; 95 de ses 107
blocs de documentation reprennent le docstring de leur jumeau, dont 10
nouveaux ; ses commentaires de corps passent de 16 à 30 lignes. Plus une ligne
« Jumeau de … » ni « Voir … dans le Python » : les noms sont ceux du portage.
Ne passe que la mécanique du Python — le cache, la somme ordonnée, le
dataclass gelé. Les commentaires du module vont de 15 800 à 56 800 caractères,
le Python en portait 54 700 ; le code, commentaires et blancs ôtés, est le même
au jeton près, 5 925 jetons, et le fichier passe de 1 791 à 2 522 lignes. La
relecture a trouvé deux phrases du Python que le code dément, corrigées dans
celui qui reste : l'indépendant ne garde de l'année courante que son
invalidité-décès, sa maladie, sa famille et sa CSG se refaisant à l'année ; le
module de l'impôt reçoit le bénéfice tel quel, sans le calculer.

**Retirer.** `cycle_de_vie.py` (2 301 lignes) et ses tests Python
(`tests/test_cycle_de_vie.py`, 1 136 lignes) sont partis. Les renvois qui les
nommaient nomment le portage : six entrées du registre des autres modèles
(0941421), les en-têtes de `prelevements_historiques.yaml`, que réécrit
`scripts/fetch/ipp_prelevements_sociaux.py`, et de
`contributions_equilibre_agirc_arrco.yaml`, les docstrings de
`impot_revenu.py`, de `contributions_equilibre.py` et de
`donnees/prelevements_historiques.py`, ceux des scripts du cycle de vie et du
COR, l'exemple de `scripts/jumeaux.py`. La carte compte 68 paires, et
`cycle-de-vie.js` est du JavaScript seul. Aucun témoin ne bouge.

**Tests.** 2 931 rapides, 54 de moins : ceux du module, passés au portage, et
les deux du jeu de l'OCDE, passés au contrôle des données. 138 de la zone — la
prose, les références, le script, la concordance, l'estimation du site, la
carte des jumeaux, les niveaux ; le filet du site, essais de node compris ;
sous les présomptions décalées, les quatre fichiers branchés, dont 22 tests se
taisent, qui nomment node. Le site charge 44 Ko de plus, 14 Ko compressés : les
commentaires du seul exemplaire, que `verifier_prose.py` récrit au README.

**Ce qui suit.** L'étape 5 est close. L'étape 6 : les paires du moteur, une à
une, dans l'ordre de la carte (`python scripts/jumeaux.py`), relecture
d'abord ; chacune attend que la fabrique ou le coût, qui la calculent encore en
Python, passent par le pont. La phrase du bloc de l'étape 10 de l'action 138
qui place ce retrait après l'indice majoré et le solveur inverse est caduque :
la session qui avancera l'étape 10 l'ôtera de son bloc.
