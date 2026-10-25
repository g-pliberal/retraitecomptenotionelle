# L'étape 8 : Carrières types, la même chose en moins de mots

**La demande.** Lot du 24 octobre 2026, cinquième vague : le propriétaire
demande une session par tâche, menée sans lui, huit en même temps ; celle-ci,
seule du lot sur les pages, mène l'étape 8 de l'action 173 : « Carrières types,
moins de mots sans perdre une idée ».

**Ce qui se lit sans déplier.** Le budget de lecture de Carrières types
(`BUDGETS_DE_LECTURE`, `tests/test_web.py`) passe de 500 à 450 mots de prose,
et de 310 à 270 dans la grille : vu rouge pour 497, la page en montre 448, et
la grille 270 au lieu de 279. La clé de lecture redisait le chapeau de
l'affiche, ce que chaque case rapporte : elle dit les pourcentages lus « contre
une promesse, celle que le système actuel fait à la même carrière », la phrase
même que cite le parcours de présentation. Deux repères redisaient « par
rapport à aujourd'hui », que l'affiche dit ; le troisième, « à carrière
identique jusqu'au départ », ce que disent l'affiche et le panneau de la
proposition. La légende de la grille redisait le titre de son panneau, et la
lecture qui la suit ; les trois titres, « par rapport à aujourd'hui ». « Le
système 4 est la proposition » redisait son onglet ; la lecture de la
proposition renvoyait à Simuler, ce que fait le bouton de la page. Elle dit en
revanche, calculé sur l'âge légal de la proposition, ce que seul un dépliant
complétait : nul n'y part avant 65 ans après la bascule, et qui partait plus
tôt travaille jusque-là — ce qui éclaire les cases vertes du militaire et de
l'agent de conduite.

**Ce qui se lit en dépliant.** `BUDGETS_DEPLIES` prend Carrières types :
2 844 mots, vu rouge pour 2 750 ; 2 701 après. Les quatre tableaux en portent
1 161, les gloses des treize carrières 637, que le modèle écrit
(`castypes.py`) : l'étape les laisse. Sous « Fonctionnaire et salarié », la
grille redisait ce que rapporte chaque case avant de dire ce qu'elle ne
compare pas ; le taux de remplacement et le taux plein se définissaient en
toutes lettres, quand le glossaire les définit : ils en prennent la bulle.
Sous les âges, la proposition redisait son âge légal, que son panneau dit
désormais ; le dépliant dit seulement que son tableau est celui des systèmes
1 à 3, et son titre perd « ce n'est pas le même ». Aucun chiffre n'est récrit,
aucune phrase en gras ne change, aucune simulation ne bouge : seul le témoin
de la page change.

**Ce qui se lit ensemble.** `COTE_A_COTE` (`tests/test_ecrans.py`) prend
Carrières types. Sa règle ne comptait que les rangées de deux valeurs, quand
une rangée de la grille en porte sept : elle demande deux valeurs courtes par
ligne au moins, jamais une. Vu rouge à 320 points sur la grille et sur les
âges, dépliés, mais aussi sur Coût, Pourquoi changer et les résultats du
simulateur, que la liste tenait déjà : la colonne d'une fiche, de 8,5 rem,
n'en laissait tenir qu'une. Elle ne demande plus que la moitié de la rangée
(`moteur/style.css`). Aucune page n'en est plus longue : à 320 points, tout
déplié, Coût passe de 116 658 pixels à 108 384, Méthode et sources de 151 071
à 130 668, Droits non cotisés de 46 158 à 42 762 ; rien ne bouge à 390. Un nom
de colonne d'un seul long mot, « Complémentaire » dans les résultats, se coupe
à sa césure, et non n'importe où.

**Ce qui ne se voyait pas, trouvé en chemin.** Une grille se lit en colonnes,
la génération 1940 d'une carrière sous celle de la carrière d'avant. Repliée
en fiche, celle de Carrières types mettait à 390 points chaque carrière sur
quatre lignes de deux valeurs, 247 pixels par carrière et 3 210 pour la
grille ; à 320, une valeur par ligne, 5 199 pixels.
`test_une_grille_repliee_garde_ses_colonnes` exige qu'une grille — plus de
trois colonnes de nombres courts sous des en-têtes courts, la seule du site —
mette sur une ligne autant de valeurs d'une rangée que la largeur en tient :
vu rouge à 320 et 390 points. Le pli d'`index.html` la reconnaît
(`data-grille`) et la replie en rangée, ses valeurs serrées sous la ligne des
années ; il ne la passe en fiche, quatre valeurs par ligne, que si elles n'y
tiennent pas. La grille tient en 1 018 pixels à 390 points, la page en 4 128
au lieu de 6 475 ; en 2 015 à 320, la page en 5 664 au lieu de 9 068. Dès 768
points, elle reste un tableau.

**Ce qui attendait GitHub.** L'envoi de l'action 138, étape 3 (`c90b82b`),
juste avant celui-ci, change le coût que calcule le modèle, que le paquet figé
ne dit pas encore : quatre tests en tombaient ici, avec le `pages.js` de `main`
comme avec celui-ci, dont `test_cas_types_dit_du_reglage_ce_que_le_solde_dit`
(0,83 au plus bas, quand la page dit 0,84) et `test_le_paquet_est_a_jour`. La
fabrique les refait, comme les chiffres ancrés que l'envoi déplace.

**Ce que le propriétaire peut vouloir trancher.** À 390 points, les valeurs de
la grille se serrent à un tiers de rem l'une de l'autre. À 320, une fiche de
valeurs longues de trente à soixante signes, l'inventaire de Droits non
cotisés, les range aussi deux par ligne, en colonnes de huit rem.

**Laissé tel quel.** Les gloses des treize carrières, qui sont au modèle et non
au site : celle de la profession libérale raconte la règle « ouverture plus
deux ans » qu'elle a portée jusqu'au 22 septembre 2026, un récit dans une page,
que la zone du modèle peut ôter. La phrase du réglage de la proposition,
calculée et tenue par son test ; « « Aujourd'hui » n'est pas un point fixe »,
tenu par le sien ; les deux variantes que le site ne compare pas, que Coût dit
avec leur raison et cette page en une ligne ; les tableaux.
