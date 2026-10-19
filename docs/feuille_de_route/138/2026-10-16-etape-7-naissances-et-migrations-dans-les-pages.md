# Étape 7, septième partie : la fécondité et les migrations sur la page Coût

**Reprise, au 19 octobre 2026.** Fait : la page Coût montre, dans la section
« Naissances et migrations » (`cout-demographie`), le coût des quatre
systèmes sous les variantes de fécondité et de migrations de l'INSEE. Faits
depuis : l'indexation sous la variante (16 octobre), la mortalité
différentielle des cas types (17), la queue observée (18), les inaptes de la
Cnav (19) ; le 19 aussi, la phrase des poids de la page Coût, qui dit l'une et
les autres. Rien ne reste aux pages tant que la grille ne change pas. Au
propriétaire : la table des poids, ses lignes et sa phrase du partage, que
l'inapte dément ; le rapport de dépendance (point 3 ici) ; les départs qui
suivent l'espérance de vie. Détail : note « la phrase des poids ».

**La demande.** Vague quater du 16 octobre 2026, session 1 : le point 1 de
« Ce qui reste » de la sixième partie (note « fécondité et migrations ») —
leur affichage sur la page Coût, au modèle depuis le même jour
(`memoire.cout(demographie=...)`). Le simulateur n'a pas à suivre.

**Ce qui est fait.**

- *La table* : `figer_esperance_vie` devient `figer_variantes`, et
  `EsperanceVieFigee`, `VariantesFigees`, des deux côtés
  (`donnees/agregats.py`, `agregats.js`) : la même table sert aux trois
  composantes. `_agregats` en fige deux de plus, `fecondite` et `migrations`,
  sous les hypothèses `basse`, `centrale` et `haute`, la centrale étant le coût
  de la page ; le paquet passe à la version 23.
- *La page* : un constructeur commun, `tableauVariantes`, tire le tableau de
  chaque table et ce que chaque hypothèse déplace de la dépense à l'horizon ;
  l'espérance de vie l'emploie, et une section de plus,
  `coutDetailDemographie`, en porte deux tableaux, la fécondité puis les
  migrations, avec ce que chacune dit de la pyramide et ce que la proposition
  n'en absorbe pas. Une seule section, et non deux : le budget de lecture de
  Coût (970 mots, qui ne se desserre pas pour de la prose) ne laissait place
  qu'à un titre de trois mots, que le plan répète.
- *La note de l'espérance de vie* dit aussi que le PIB y suit les 20-64 ans de
  la variante, la règle valant pour toutes depuis la sixième partie.
- *Les tests* : les trois tables contre le modèle et entre les deux lecteurs
  (`test_agregats.py`, paramétrés par composante ; sous la fécondité et les
  migrations, la proposition bouge de plus d'un demi-dixième de point en
  2070, à rebours de la longévité) ; le plan de Coût et ses sept tableaux de
  systèmes (`test_web_revues.py`).

**Ce que la page montre**, en part de PIB, dépense du bilan en 2070
(basse / centrale / haute) : système actuel, 16,38 / 15,30 / 14,31 sous la
fécondité, 16,55 / 15,30 / 14,27 sous les migrations ; proposition,
8,73 / 8,15 / 7,63 et 8,85 / 8,15 / 7,58. Les chiffres de la sixième partie
ont bougé de quelques centièmes avec le modèle depuis.

**Ce qui reste** de l'étape, dans l'ordre :

1. *L'indexation sous la variante* : la masse salariale de la variante, au
   lieu de celle du central, pour les comptes et les pensions de la
   proposition — elle toucherait le simulateur, non le diviseur. La phrase de
   la page qui le dit (« Ses comptes s'indexent ici sur la masse salariale du
   scénario central ») se récrira alors.
2. *La mortalité différentielle* des cas types, *les départs qui suivent
   l'espérance de vie*, *la queue observée* de 85 à 98 ans, *2025* sous la
   loi seule : inchangés.
3. *Au propriétaire*, toujours : si le rapport de dépendance sous chaque
   variante doit s'écrire sur la page.
