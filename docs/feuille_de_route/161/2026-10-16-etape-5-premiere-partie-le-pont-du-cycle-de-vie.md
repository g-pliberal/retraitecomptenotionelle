# Étape 5, première partie : le pont du cycle de vie — le script des cas types lit le portage, le test des références attend le pont du coût

**La demande.** Dire si `scripts/cycle_de_vie.py` et le test des références
(`tests/test_cycle_de_vie_references.py`) peuvent lire le portage du cycle de
vie (`moteur/js/cycle-de-vie.js`) au lieu de son jumeau Python, et à quel prix
pour les cas types du COR, Python seul (`castypes.py`) ; le faire si le prix
est juste, une paire à la fois, chaque retrait relu et mesuré.

**Le script : oui, à petit prix.** Le portage n'a pas les cas types, mais il
n'en a pas besoin : un cas type n'est, sous les paramètres du script (jamais
`conventions_cor`), qu'une carrière d'un seul statut, que `carriereSimple`
bâtit des mêmes options que `carriere_simple`. Le Python résout donc chaque
case — ses options (`CasType.options`, que `_carriere` lit lui-même : une
seule source), l'âge où le pilote la fait partir, les écarts de la grille
(`carriere_de_la_grille`, que `calculer_cas_types` lit aussi, sans simuler) —
et un programme node, `scripts/cycle_de_vie.mjs`, fait le reste : les
indicateurs sous les quatre conventions, le balayage des âges de départ sous
les trois productivités, les âges d'équilibre de la table commune et des cas
types. Le pont générique `web/site.py` ne suffisait pas : il ne passe ni une
`Map` (les interruptions) ni une fonction (le `batir` du balayage). Sous
`conventions_cor`, où la carrière d'un cas type se déforme en Python
(`primes_projetees`, l'entrée tardive), le pont refuse ; sans node, le script
s'arrête, sans repli.

**Mesuré**, avant et après, sur la même tête de `main` (le hook de fin de tour
l'avait avancée au milieu de la première mesure : la PMR unique de 2022 des
exploitants, session 5, déplaçait le chef d'exploitation de 1950 ; la mesure
s'est refaite dans un arbre de travail de cette tête). Dix lancements : la
grille sous les conventions du dépôt, du COR, après impôt sur les prix, sur le
salaire moyen avec le COR, deux indicateurs et deux systèmes ; l'équilibre, en
entier et sur deux générations ; le balayage des treize cas types sur les sept
générations et les trois productivités, de six cas types sur trois générations
sous le COR après impôt, du cadre sous le salaire moyen. Les tableaux imprimés
sont identiques à l'octet, les dix ; les fichiers JSON, 701 838 nombres, ne
diffèrent qu'au dernier bit, de 2,3e-12 en relatif au plus, et aucune case n'y
manque. Le temps : la grille de 5 à 11 s à 2,4 à 3,5 s, l'équilibre de 2,4 à
1,5 s, le balayage complet de 435 à 74 s.

**Retiré**, relu : les noms du module que seul le script lisait, ceux des
cas types — `ages_de_depart`, `balayage`, `AgesDEquilibre`, `ages_d_equilibre`
(dont la remarque sur le rattachement par la pension passe au programme node)
et `hypotheses_de_productivite` (au script, `productivites`, une lecture de
`hypotheses_projection.yaml`). Leurs tests suivent : celui des âges d'un cas
type et des productivités dans `tests/test_cycle_de_vie_script.py`, qui lit le
pont et confronte, sur les treize cas types de 1960 et de 2000, sous deux
conventions, ce qu'il rend au jumeau Python — le profil au SMIC, les
interruptions, les primes, que les carrières de la concordance n'ont pas —, et
le balayage du salarié de 1970, dans `tests/test_cycle_de_vie.py`, par
`balayage_d_une_carriere`, qui a son jumeau. `python scripts/jumeaux.py
cycle_de_vie` le dit : aucun script n'atteint plus le module, six fichiers de
tests seulement.

**Le test des références : non, pas avant le pont du coût.** Sur ses vingt
tests, ceux du rendement par régime, du taux de cotisation de l'État et du
remplacement net rebâtissent un flux à la main (`replace(flux, …)`), lisent
les cotisations d'un compte régime par régime (`constructeur_employeur`,
`constructeur_de`), le coefficient des points de l'Agirc-Arrco du coût
(`coefficient_actuel`, Python seul, sans jumeau par la note 0003) et la
`Saisie` Python. Les faire lire au portage voudrait exposer à node les
régimes un à un et le coût : c'est le pont du coût et de la fabrique, la suite
de l'étape 5, et les paires du moteur, l'étape 6, non un retrait du cycle de
vie. Le module Python reste donc, que plus rien ne lit hors des tests, tenu
au portage par la concordance.

**Tests.** 2 495 rapides, 2 435 sous les présomptions décalées (les tests du
pont s'y taisent, comme toute confrontation au portage, par une fixture qui
nomme node), 134 de la zone ; le site ; après `regenerer.py`, les six fichiers
de la liste, 745. Aucun témoin de simulation ne bouge ; les quatre pages du
Coût que la régénération refait viennent de la session 3 (`cout.py`,
5f36320), et ne sont pas commitées.

**Ce qui suit.** La suite de l'étape 5 : le pont du coût et de la fabrique,
sous les six conditions de la note 0003. Le test des références, et avec lui
le retrait de `cycle_de_vie.py`, l'attendent.
