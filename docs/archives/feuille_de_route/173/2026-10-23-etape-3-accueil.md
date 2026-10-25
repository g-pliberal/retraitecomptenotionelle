# L'étape 3 : l'accueil, la même chose en moins de mots

**La demande.** Vague du 23 octobre 2026 : la session de suivi « Qu'est-ce
qu'il reste à faire ? » lance, sur la demande du propriétaire (« Fait ça »),
douze sessions en parallèle, une étape chacune ; celle-ci mène l'étape 3 de
l'action 173, seule sur les pages : « l'accueil, moins de mots sans perdre une
idée ».

**Ce qui se lit sans déplier.** Le budget de lecture de l'accueil
(`BUDGETS_DE_LECTURE`, `tests/test_web.py`) passe de 470 à 390 mots de prose
et de 245 à 230 dans les tableaux, vu rouge à 439 et 238 ; la page en montre
387 et 226. N'est parti que ce qui se redisait : le chapeau disait comment le
compte devient une pension, que les trois gestes disent un écran plus bas ; la
carte des 18 % + 5 % redisait ce que deviennent les deux taux, que son chiffre
et sa promesse portent ; l'exemple du plancher, 300 € et 1 500 €, précédait le
tableau qui le donne à la ligne suivante ; cinq cases du tableau terme à terme
raccourcissent. « Rien n'est placé » devient « Rien n'y est placé » : la carte
voisine vient de dire que 5 % le sont.

**Ce qui se lit en dépliant.** Un second budget, `BUDGETS_DEPLIES`, borne la
page tout dépliée, sans les menus ni les bulles du glossaire : 4 920 mots au
matin, 4 856 après le premier lot, vu rouge pour 4 500 ; 4 489 le soir, dont
942 sous les petites retraites au lieu de 1 121. Cette réponse redisait trois
fois ses montants, deux fois que la garantie se refuse, et l'exemple du tableau
du haut ; ce que l'État cotisera se disait sous la fiche de paie et sous les
fonctionnaires, il ne se dit plus que là ; l'épargne à votre nom redisait
l'héritage, que « Et si je meurs ? » dit ; la phrase d'entrée des points de
blocage redisait leur titre et leur légende ; la licence, le pied de page la
porte. Les phrases du catalogue gardent leur texte, sauf deux extraits, qui
suivent les cartes de la garantie et des 18 % + 5 % ; « Pas de trimestres, pas
de barèmes, pas de surprise » n'est plus en gras. Aucun chiffre n'est récrit :
« deux femmes sur cinq », « aux deux tiers », « les cinq points » restent tels
quels. Laissé tel quel aussi, ce que l'accueil dit des systèmes que le
simulateur compare — « Quatre montants côte à côte », « les deux montants »,
les cinq points volontaires : l'action 172 le réserve au propriétaire.

**Ce qui se lit ensemble.** Sur un téléphone, trois rangées sur dix de « Ce que
cela change » empilaient la valeur d'aujourd'hui et la nôtre : le pli des
tableaux (`plierLesTableaux`, `index.html`) comptait dans la longueur d'une case
la définition cachée de ses mots du glossaire, et « des trimestres, et 80
barèmes » passait pour une phrase. Il mesure ce que la case montre ; le
tableau se replie en rangées, l'en-tête une fois, les deux valeurs côte à
côte. `test_deux_valeurs_courtes_d_une_rangee_repliee_se_lisent_cote_a_cote`
le tient, vu rouge sur 24 rangées, pour l'accueil seul (`COTE_A_COTE`,
`tests/test_ecrans.py`) : à 320 points, Droits non cotisés et les résultats du
simulateur empilent encore, en fiche, deux valeurs courtes que la colonne
minimale de 8,5 rem ne laisse pas tenir ensemble — à leurs étapes, 9 et 4.

**En chemin.** `tests/test_ecrans.py` cherchait le Chromium des sessions
Claude Code sous `chrome-linux`, et le leur est sous `chrome-linux64` : il
passait sans rien jouer. Il le trouve.

**Ce que le propriétaire peut vouloir trancher.** Trois choix de forme : le
chapeau ne dit plus « chaque cotisation y est inscrite ; à la retraite, il
devient votre pension » ; « C'est le système de la Suède, de l'Italie, de la
Pologne et de la Lettonie » devient « Ce compte existe déjà en Suède, en
Italie, en Pologne et en Lettonie » ; ce que l'État cotisera a quitté la
réponse sur la fiche de paie.
