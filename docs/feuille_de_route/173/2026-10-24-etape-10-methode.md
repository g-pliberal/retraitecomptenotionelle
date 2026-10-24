# L'étape 10 : Méthode et sources, la même chose en moins de mots

**La demande.** Lot du 24 octobre 2026, septième vague : le propriétaire
demande une session par tâche, menée sans lui, six en même temps ; celle-ci,
seule du lot sur les pages, mène l'étape 10 de l'action 173 : « Méthode et
sources, moins de mots sans perdre une idée ». Les deux schémas de la carte
des flux de Coût sont laissés à une session suivante.

**Ce qui se lit sans déplier.** Le budget de lecture de Méthode et sources
(`BUDGETS_DE_LECTURE`, `tests/test_web.py`) passe de 600 à 470 mots de prose :
vu rouge pour 557, la page en montre 469. Le tableau ouvert passe de 120 à
90 mots, qu'il montre : sa colonne des prix répétait neuf fois le même cumul,
×322,2, que la ligne « Indexation sur les prix » donne, et que le pouvoir
d'achat conservé divise. La règle par défaut, la masse salariale, se disait
trois fois, dans l'« En clair », dans la deuxième des trois opérations et sous
le tableau, et sa raison deux fois : la deuxième opération ne la dit plus, et
la note du tableau la nomme sans la justifier, avec les huit autres à un clic.
La troisième conséquence, « aucun droit qu'une
cotisation n'a pas financé », était la deuxième phrase du résumé ; la
première opération redisait « porté au compte » sous son titre, « On
inscrit ». Sous « D'où viennent les chiffres », la note redisait la date de la
plus ancienne vérification que la fiche voisine porte : la fiche dit les deux,
« vérifiées entre le 13 septembre 2026 et le 24 octobre 2026 », et la note ne
les redit plus ; l'introduction redisait que les règles des régimes se lisent
dans les textes, ce que dit le dépliant des séries.

**Ce qui se lit en dépliant.** `BUDGETS_DEPLIES` prend Méthode et sources :
5 944 mots hors ses deux bases, vu rouge pour 5 650 ; 5 618 après, et 17 608
tout compris au lieu de 17 934. Les bases ne comptent pas, et c'est une règle
du test, non de la page : les 176 séries recontrôlées et les 114 régimes de
l'inventaire, les deux seules tables du site qu'un champ cherche et que des
menus filtrent, en portent douze mille mots, qu'on cherche ligne à ligne, et
que le dépôt allonge à chaque série certifiée, à chaque régime recensé ; les
compter aurait fait payer à la prose le travail des sessions de données. Le
dépliant du pilier disait trois fois que le choix des maturités ne change rien
tant que les taux futurs sont ceux de la courbe, et deux fois qu'au-delà de
trente ans elle ne cote plus : une fois chacun, sous la règle des maturités.
Celui des neuf règles annonçait « deux réserves » et en disait trois, et
redisait le lissage italien que la ligne du tableau nomme ; celui des unités,
deux fois ce qu'est le salaire moyen des comptes nationaux. « L'étalon ne vaut
que par ce qu'il reproduit », « il vaut mieux le dire que de l'effacer », « le
système 1 les conserve tous » sous le titre qui le dit : partis. Aucun chiffre
n'est récrit à la main, aucune simulation ne bouge : seul le témoin de la page
change.

**Ce qui se lit ensemble.** `COTE_A_COTE` (`tests/test_ecrans.py`) prend
Méthode et sources : vert d'emblée, comme Droits non cotisés, et la liste
porte désormais toutes les pages du site. Sans sa colonne des prix, le tableau
de l'indexation tient en ligne à 390 points, chaque règle à côté de ses deux
valeurs, et se replie en grille à 320. La page fermée passe de 5 714 pixels à
5 502 à 390 points, et de 6 453 à 6 066 à 320.

**Ce qui ne se disait pas juste, trouvé en chemin.**
`test_la_methode_dit_ce_que_le_modele_compte` (`tests/test_web_revues.py`),
vu rouge. La carte prêtait son tableau à « une cotisation de 1950 », quand il
cumule les taux d'une somme versée en 1940 (`ANNEE_VERSEMENT_COMPARE`) : l'année
se lit à la constante. Le dépliant des sources recensait « trente
institutions », et en nommait trente, quand le manifeste en cite 42, que la
fiche du haut compte : il dit le compte de la fiche et renvoie au manifeste
pour les noms. Le dépliant du pilier finissait sur une garantie vieillesse qui
« ne regarde pas cette rente », servie sur la seule pension de répartition,
quand il venait de dire, comme le modèle, qu'elle la reprend euro pour euro
(contrôle `garantie_compte_la_rente_volontaire`) : la phrase est partie. Et la
proposition était « le système 3, à deux différences près », le taux et la
garantie : le pilier capitalisé, que seule elle construit, en est une
troisième, nommée. Au catalogue des affirmations, l'extrait de la première
opération suit sa phrase, et « lissage sur cinq ans », qui n'est plus en gras,
quitte le catalogue ; deux autres extraits portent le même contrôle.

**Ce qui attendait GitHub.** Le témoin des pages date d'avant l'étape 9 : les
trois réserves de Droits non cotisés y disent encore « Elle », et quatre tests
du catalogue tombent sur `main` tant que la fabrique ne l'a pas refait. Refait
ici, il les rend verts. `test_le_paquet_est_a_jour` tombe aussi, sans rien de
cette étape : du paquet, seules les `versions_des_fiches` diffèrent, celles
des fiches que d'autres sessions ont retouchées depuis la dernière fabrique ;
elle les refait.

**Ce que le propriétaire peut vouloir trancher.** Les noms des institutions ne
sont plus sur la page : le paquet n'en porte que le compte
(`institutions_citees`), et les y mettre est un chiffre de plus d'une page qui
agrège, dans la zone des données. « Onze fois », « près de cinq fois », les
18 % et les 800 et 250 € de la garantie restent écrits à la main : les
contrôles du catalogue les tiennent, ou les paramètres par défaut les
portent.

**Laissé tel quel.** Les deux bases et leurs lignes ; les tableaux du pilier
et de la fiabilité ; la liste de ce que le système 1 applique du droit en
vigueur, une ligne par avantage ; les licences ; « Pour aller plus loin » et
les titres des dépliants, qu'aucune phrase n'annonçait.
