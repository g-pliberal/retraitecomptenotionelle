# Étape 7, huitième partie : l'indexation de la proposition sous la variante démographique

**La demande.** Vague quinquies du 16 octobre 2026, session 3 : le point 2 de
« Ce qui reste » de la sixième partie (note « fécondité et migrations ») —
les comptes et les pensions de la proposition indexés sur la masse salariale
de la variante, et non plus du central, dans `memoire.cout(demographie=...)`.
Le simulateur du coût, non le diviseur ; ni `pages.js` ni la saisie.

**La règle.** La page fait déjà suivre au PIB de la variante ses 20-64 ans :
le PIB du COR multiplié par `f(t) = Population.facteur_actifs(t)`. La masse
salariale qui indexe la proposition suit la même règle : celle du central
multipliée par `f(t)`, un jusqu'en 2025. D'où, sans resimuler la grille :

- *Le compte* : une cotisation de l'année `a`, liquidée en `L`, gagne
  `f(L) / f(a)`. Le compte de chaque cohorte gagne la moyenne de ce rapport,
  pondérée par ce que chaque cotisation pèse dans le compte du central
  (`VoletLiberal.cotisations`, revalorisées par `simulateur.indexation`) ;
  la cohorte décalée cotise et part décalée d'autant
  (`_capitaux_sous_la_variante`, rangé dans `Pensionne.capitaux` par
  `_sous_la_demographie`, qui prend maintenant la population).
- *La pension servie* : l'index de `RevalorisationServie` multiplié par `f`,
  pour la proposition seule (`pour_la_proposition`, lu par `_masses` sous
  `revalorisation.proposition`) : la règle du stock suit, chaque coefficient
  étant un rapport de l'index à deux dates. La part notionnelle de ce que la
  garantie regarde suit les deux ; la rente du pilier, nominale, non.
- *Le champ* : toute variante, l'espérance de vie comprise (ses 20-64 ans
  bougent de quelques millièmes) ; sous une indexation sur la masse salariale
  ou le PIB seulement (`MODES_SUIVANT_L_EMPLOI`). Le central ne change pas, au
  bit près : les facteurs valent un, et la multiplication par un est exacte.
- *Les autres systèmes notionnels* (2 à 5) gardent l'indexation du central :
  la grille ne garde pas leurs cotisations. Les scénarios 2 et 4 sont dans les
  tableaux de la page ; la limite le dit (`limites/5-ter-trajectoire.md`).

**Ce que la variante déplace**, dépense du bilan de la proposition en 2070, en
part de PIB (basse / centrale / haute), avant et après :

| | avant | après |
|---|---|---|
| Fécondité | 8,73 / 8,16 / 7,63 | 8,19 / 8,16 / 8,11 |
| Migrations | 8,85 / 8,16 / 7,58 | 8,20 / 8,16 / 8,12 |
| Espérance de vie | 8,16 / 8,16 / 8,11 | 8,13 / 8,16 / 8,14 |

Le solde de 2070 de la proposition passe, sous la fécondité, de −0,58 et
+0,52 à −0,05 et +0,03 ; sous les migrations, de −0,70 et +0,57 à −0,05 et
+0,03 ; son solde moyen, de −1,23 et −0,93 à −1,08 et −1,07 sous la
fécondité, de −1,48 et −0,72 à −1,13 et −1,02 sous les migrations. Le système
actuel et les scénarios 2 et 4 ne bougent pas. *La proposition se protège
ainsi de la natalité et des migrations comme de la longévité* : ses pensions
suivent la masse salariale, et la masse le PIB. Ce qui reste, moins d'un
dixième de point, est le stock liquidé avant la bascule, sur les prix.

**Les tests.** `test_la_proposition_s_indexe_sur_la_masse_de_la_variante`
(`test_cout.py`) : le compte d'un volet à deux cotisations, la revalorisation
de la proposition et elle seule, les masses des autres systèmes inchangées ;
`test_agregats.py` : sous les trois composantes, la proposition bouge de
moins d'un dixième de point à l'horizon.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La page Coût*, à la session des pages : la phrase de la section
   « Naissances et migrations » (`coutDetailDemographie`, `pages.js`) dit
   encore que la proposition « n'en est pas protégée comme de la longévité »
   et que « ses comptes s'indexent ici sur la masse salariale du scénario
   central » : c'est désormais l'inverse. Ses écarts, calculés de la table,
   suivent seuls à la régénération.
2. *La mortalité différentielle* des cas types, *les départs qui suivent
   l'espérance de vie*, *la queue observée* de 85 à 98 ans, *2025* sous la
   loi seule : inchangés.
3. *Les scénarios 2 à 5* sous la variante : leur compte demanderait leurs
   cotisations dans la grille, ou le profil de la proposition pour les peser.
4. *Au propriétaire*, toujours : si le rapport de dépendance sous chaque
   variante doit s'écrire sur la page.
