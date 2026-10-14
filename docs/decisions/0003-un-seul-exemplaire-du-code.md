# Note de décision 0003 — un seul exemplaire du code

*Proposée le 14 octobre 2026 par la session de l'action 161, à valider par le
propriétaire. Elle récrit le principe 4 ; le reste du noyau ne bouge pas.*

*Validée le 14 octobre 2026 par le propriétaire, telle quelle.*

## Le problème

Le principe 4 veut qu'une implémentation fasse foi, aujourd'hui le Python, et
que le JavaScript du site en soit la copie, étape par étape. La carte des
jumeaux (`scripts/jumeaux.py`, étape 1 de l'action 161) compte, au commit
84efb56, 70 paires : 56 003 lignes de Python, 43 165 de JavaScript. Chaque
règle du moteur s'écrit donc deux fois, puis se prouve deux fois.

La copie est fidèle : sur les 845 cas des témoins, 157 418 valeurs, 97,3 %
sont identiques au bit près, et l'écart relatif le plus grand vaut
9 × 10⁻¹⁵, le bruit d'arrondi des flottants. Mais elle n'est prouvée que sur
ce que les tests de concordance exécutent : 81,8 % des lignes Python des
jumeaux, 88,3 % de leurs lignes JavaScript. Le reste n'a jamais été confronté
à son jumeau.

Le dépôt a déjà tranché un cas : le 10 octobre 2026, le propriétaire a décidé
que le coût ne se calculerait plus chez le lecteur, et son jumeau JavaScript
est parti — `cout.js`, `avantages.js`, `castypes.js`, `population.js` (action
150 ; version du 11 octobre 2026, « le coût sans jumeau »). Le 14 octobre, il demande la même chose du reste, « le meilleur au
cas par cas », sûrement, et en relisant chaque ligne retirée (action 161, « D'où
elle vient »).

## La décision

### Le principe 4, récrit

> 4. **Chaque étape s'écrit une fois, dans le langage de l'endroit où elle
>    tourne.** Ce que le site calcule chez son lecteur s'écrit en JavaScript,
>    le seul langage du navigateur. Ce qui ne tourne qu'à la fabrique —
>    acquérir, certifier et empaqueter les données, le coût, les études,
>    l'outillage — s'écrit en Python. Ce qui tourne aux deux endroits, le
>    moteur d'une carrière, n'a qu'un exemplaire, en JavaScript, que le Python
>    fait tourner par node. Les étapes s'échangent des données décrites par un
>    schéma, et les témoins gardent leurs chiffres. Tant qu'une étape a encore
>    ses deux jumeaux, le Python fait foi pour elle, et le JavaScript la copie
>    (§ 7.1).

### La règle de l'endroit

Elle tranche presque toujours seule. Le navigateur n'exécute que le
JavaScript : ce qu'il calcule ne peut s'écrire qu'en JavaScript. La fabrique
tourne hors du navigateur, sur GitHub à chaque envoi, où le Python a déjà ses
chargeurs, sa certification et ses tests : ce que seule la fabrique calcule
reste en Python, comme le coût depuis l'action 150. Pour ce qui tourne aux deux endroits, l'exemplaire unique est
celui du navigateur, puisque le navigateur ne peut pas faire tourner le Python
et que le Python, lui, fait déjà tourner node (`web/site.py`). Quand elle ne
suffit pas, le propriétaire tranche à la relecture de la paire. Deux cas sont
déjà connus : les données, dont le chargeur Python doit rester pour normaliser
et empaqueter le YAML (`scripts/construire_donnees.py`), et dont ce que les
deux côtés recalculent se tranche paire par paire ; et le lecteur de PDF
(`scripts/fetch/lecture_pdf.py`), dont quatorze scripts ont besoin à la
fabrique — douze lecteurs de sources, la certification des données et la
confrontation à « Mon estimation retraite » —, comme le site pour le relevé
d'un lecteur.

### Le temps de la migration

Rien ne change pour une étape tant qu'elle a ses deux jumeaux : le Python fait
foi, se modifie le premier, et le JavaScript le copie, sous la concordance des
témoins. Une règle nouvelle du moteur s'écrit donc encore deux fois, jusqu'au
pont. Un code neuf qui ne tourne qu'à un endroit s'écrit une seule fois, dès
la validation : une page du site en JavaScript, une étude ou un outil en
Python. Une paire perd son jumeau Python, une à une, par la méthode qui suit ;
dès lors, son exemplaire unique a pour références celles de tout le dépôt
(§ 3.1) — le texte, les exemples officiels, les autres modèles — et pour
filet ses témoins figés.

### La méthode, une paire par étape

1. **Relever** tout ce qui dépend du jumeau à retirer
   (`python scripts/jumeaux.py <nom>`) : les imports, les chargements par nom,
   les fiches, les chiffres ancrés, les mentions.
2. **Mesurer** ce que les tests de concordance en exécutent, des deux côtés
   (`--couverture`).
3. **Relire** la paire fonction par fonction. Chaque différence se tranche
   contre la source, la fiche et le texte : aucun jumeau n'a raison par défaut
   (§ 3.1). L'erreur se corrige dans celui qui reste, avec son test. Si elle
   déplace un résultat, elle suit la règle d'une correction de notre lecture :
   la fiche la note, avec son effet sur les témoins (§ 4.10), et ses témoins
   changent dans un commit à elle, avant le retrait, qui les laisse
   identiques.
4. **Figer** par des témoins ce que les tests n'exécutaient pas, et donner une
   référence figée aux tests qui comparaient au jumeau retiré.
5. **Brancher** les dépendants sur celui qui reste : scripts, tests, fiches,
   ancres, textes à tenir.
6. **Retirer**, dans un commit à part, les témoins identiques. La note de
   l'étape garde les erreurs trouvées.

La relecture vaut d'elle-même : elle se mène sur n'importe quelle paire, avant
tout retrait, et ce qu'elle trouve se corrige sans attendre.

### Ce que le pont devra tenir

Le pont est l'étape où le coût, la fabrique et les études font tourner le
moteur JavaScript par node au lieu du moteur Python. Avant qu'aucun jumeau du
moteur ne parte, il devra tenir six conditions :

- les données des contrats (annexe C), les mêmes, dans un sens et dans
  l'autre ;
- les témoins et les agrégats identiques, octet pour octet, à ceux du moteur
  Python ;
- le budget de calcul du § 7.8 tenu, mesuré avant et après sur le coût, ses
  variantes et le coût des avantages ; `APPELS_DECLARES` suit l'étape qui le
  porte ;
- la mémoire des calculs (`memoire.py`) indexée aussi sur l'empreinte du
  portage ;
- node absent, la fabrique qui s'arrête, sans repli sur un moteur périmé ;
- aucune dépendance nouvelle : node sert déjà à la fabrique et aux tests.

## Ce qui ne change pas

Les neuf contrats de données, les étapes nommées et les deux règles
d'exécution (§ 13.1) ; la hiérarchie des références ; les témoins, qui gardent
leurs chiffres à chaque retrait ; un site sans étape de construction, qu'ouvrir
l'adresse suffit à faire tourner ; les dépendances, PyYAML seul en Python,
aucune en JavaScript ; la surface publique.

## Les solutions écartées

- **Tout en JavaScript, la fabrique comprise** : récrire les 120 scripts de
  lecture des sources, la certification et l'outillage, sans rien que le
  lecteur voie ; et node ne lit pas le YAML sans une dépendance.
- **Garder les deux moteurs** : chaque règle se paie deux fois, et la
  concordance ne se prouve que sur ce que les tests exécutent.
- **Retirer le Python d'un coup** : la fabrique et le coût ne tourneraient plus,
  et la seule preuve que le JavaScript calcule juste, sa confrontation aux
  témoins du Python, partirait avant d'avoir été remplacée.
- **Une source commune**, Catala ou un JavaScript produit depuis le Python : un
  langage ou un traducteur de plus à tenir. La porte reste ouverte, étape par
  étape (§ 7.1), mais elle ne règle pas le double d'aujourd'hui.
- **Les données en JSON**, pour que la fabrique se passe du Python : leurs
  commentaires, qui portent les sources, se perdraient.

## La migration

Aucun script de conversion : la décision ne touche ni une donnée ni un contrat
(§ 13.3), et chaque retrait laisse les témoins identiques. Elle suit les étapes
de l'action 161, dans l'ordre de la carte : le pilote, le lecteur du relevé
(`web/releve_lu.py`), que ni le coût ni la fabrique n'atteignent ; les deux
autres paires dans ce cas, `cycle_de_vie.py` et `scripts/fetch/lecture_pdf.py`,
chacune tranchée à sa relecture ; le pont ; puis les paires du moteur, une à
une, relecture d'abord.

À la validation, le dépôt change en six endroits : cette note, sous
`docs/decisions/` ; le principe 4 (`docs/architecture.md`, L'essentiel) ; le
premier paragraphe du § 7.1, qui dit la règle de l'endroit et la migration ;
une ligne de la table « Où va quoi », « retirer un doublon entre le Python et
le JavaScript » ; une version de l'architecture ; et les consignes de `src/` et
de `moteur/`, qui disent où s'écrit un code neuf. À chaque retrait ensuite,
l'en-tête du JavaScript cesse de dire « qui fait foi » d'un fichier disparu
(`tests/test_jumeaux.py` le refuse), et les fiches, les ancres et les textes
qui nommaient le jumeau retiré nomment celui qui reste.
