# L'étape 9 : Droits non cotisés, la même chose en moins de mots

**La demande.** Lot du 24 octobre 2026, sixième vague : le propriétaire
demande une session par tâche, menée sans lui, sept en même temps ; celle-ci,
seule du lot sur les pages, mène l'étape 9 de l'action 173 : « Droits non
cotisés, moins de mots sans perdre une idée ».

**Ce qui se lit sans déplier.** Le budget de lecture de Droits non cotisés
(`BUDGETS_DE_LECTURE`, `tests/test_web.py`) passe de 1 300 à 1 070 mots de
prose : vu rouge pour 1 163, la page en montre 1 066. Les tableaux, qui sont
l'inventaire, gardent leur budget calculé, trente mots par ligne. Le résumé
« En clair » redisait les deux montants que les repères posent dessous, les
100,0 Md € chiffrés et les 11,1 Md € servis avant l'âge légal, et la part de
la réversion que la deuxième carte chiffre : il dit ce que le modèle chiffre,
dont la réversion, lue et non calculée. La carte de l'âge redisait que nulle
décote ne rattrape une annuité anticipée, ce que dit le résumé. Le chapeau de
l'inventaire redisait ses colonnes, le coût de l'année et la raison d'une case
vide ; la réponse de la carte, qu'il « nomme » les dispositifs sans chiffre ;
le chapeau du tracé long, son titre ; sa note finissait sur « ce tracé donne
une forme », que « long mais étroit » vient de dire ; le titre de la
complémentaire, « et elle est forte », que la phrase en gras sous son tableau
chiffre. « Pour aller plus loin » s'annonçait d'une phrase que son dépliant
titre. Le titre de la première carte se dit en six mots au lieu de onze, dans
le plan comme sur la carte : « Combien d'avantages ne sont pas cotisés ? ».

**Ce qui se lit en dépliant.** `BUDGETS_DEPLIES` prend Droits non cotisés :
7 617 mots, vu rouge pour 7 470 ; 7 430 après. Les vingt et un tableaux en
portent 4 927 : l'inventaire, ses bases légales et ses dates, et les chiffres
des tracés, que l'étape laisse. Le dépliant du plancher annonçait « trois
choses à savoir » et en disait cinq ; il renvoyait deux fois au tableau que la
carte venait de nommer ; il redisait que les comptes ne détaillent leurs
postes que depuis 2020, que dit le haut du tracé long, et que « le premier
graphique remonte à 1800 », quand il part de 1831 et que son titre le dit.
Sous la frontière, l'assiette redisait le salaire retenu pour la pension,
borné au plafond, que dit la réponse de la carte ; sous les réserves, les
écarts structurels « ne sont pas des dispositifs », que dit le chapeau de
l'inventaire. Aucun chiffre n'est récrit à la main, aucune simulation ne
bouge : seul le témoin de la page change.

**Ce qui se lit ensemble.** `COTE_A_COTE` (`tests/test_ecrans.py`) prend
Droits non cotisés : vert d'emblée, la fiche de l'étape 8 rangeant déjà le
coût d'un dispositif à côté de son origine. À 320 points, l'en-tête de cette
origine, « D'où vient le chiffre, ou pourquoi il manque », se répétait sur
quatre lignes au-dessus de chaque « lu » ou « calculé », quarante-neuf fois :
« Origine, ou pourquoi il manque » en prend trois, et une seule au-dessus d'une
raison. Coupes et en-tête ensemble, la page fermée passe de 19 043 pixels à
17 647 à 390 points.

**Ce qui ne se disait pas juste, trouvé en chemin.**
`test_droits_non_cotises_comptent_ce_que_leurs_phrases_disent`
(`tests/test_web_revues.py`), vu rouge deux fois. La réversion, que « 756
périodes du catalogue » annonçaient, l'est par 945 : la page comptait ces
périodes et n'écrivait pas son compte, qui passe dans le dépliant qui le dit.
La frise « ne redescend que trois fois » : elle baisse deux fois, en 2011 et
en 2024, trois dispositifs s'étant éteints, l'un l'année où un autre naissait ;
elle dit « Presque aucun n'a jamais été supprimé : trois en deux siècles »,
compté sur l'inventaire. « Et sur soixante-six ans ? » se calcule : « Et
depuis 1959 ? ». Les trois réserves en gras disaient « Elle » sous « Trois
choses que ces chiffres ne disent pas » : elles disent « Ils », et leurs
extraits suivent au catalogue des affirmations. Le titre ne peut pas dire
« que cette page ne dit pas » : c'est le patron de gabarit que
`test_la_rubrique_des_reserves_de_la_page_cout_ne_suit_plus_le_patron`
proscrit. Un `</p>` en double fermait le dépliant du plancher.

**Ce qui attendait GitHub.** Quatre tests de la zone tombent sur `main`, avec
le `pages.js` de `main` comme avec celui-ci : `test_le_paquet_est_a_jour`
(`equilibre.json` périmé), `test_cas_types_dit_du_reglage_ce_que_le_solde_dit`,
et les contrôles `simuler.horizon_des_comptes` et `cout.bilan_du_compte`. Le
modèle a changé depuis la dernière fabrique ; elle les refait.

**Ce que le propriétaire peut vouloir trancher.** La page appelle
« 49 dispositifs » les lignes de l'inventaire, dont les trois écarts
structurels qu'elle dit n'être pas des dispositifs ; le parcours de
présentation, qui cite ce compte, lit l'écart entre 43 et 49 comme « ceux
d'hier compris », quand trois seulement se sont éteints.

**Laissé tel quel.** Les tableaux et ce que les données y écrivent — les
familles, leurs descriptions, les raisons d'une case vide ; les phrases en
gras, au pronom près ; les sources ; « Et pour vous ? », qui dit, comme Coût,
que tout se calcule en quelques secondes dans le navigateur ; « d'un
trimestre pour la première, d'un trimestre pour la seconde », que le modèle
calcule et qui a déjà différé.
