# Note de décision 0005 — le JavaScript fait foi

*Décidée le 31 octobre 2026 par le propriétaire, dans sa demande à la session
de l'action 161 : « Dès maintenant, pour toute règle du moteur de carrière
(`droit/`, `scenarios/`, `carriere`, `chronologie`, `calendrier`,
`revalorisation`, etc.), c'est le JavaScript de `moteur/js/` qui fait foi et
se modifie en premier. Aucune règle nouvelle ou modifiée ne doit plus
s'écrire dans les jumeaux Python de `src/retraite_notionnelle/` lorsqu'elle
est déjà couverte par le pont. » La même demande tranche les deux paires de
données et le rythme des retraits, et veut que rien ne casse : les témoins et
les agrégats identiques, à l'octet, à tout instant. La session a vérifié
chaque point contre le dépôt avant de l'écrire ; ce qu'elle a mesuré est dans
`docs/feuille_de_route/161/2026-10-31-etape-6-le-javascript-fait-foi.md`.
Elle récrit la dernière phrase du principe 4, et deux passages de la note
0003 : « Le temps de la migration » et « La méthode, une paire par étape ».*

## Le problème

La note 0003 laissait le Python faire foi, pendant la migration, pour chaque
étape qui garde ses deux jumeaux : une règle nouvelle du moteur s'écrivait
deux fois jusqu'au pont, le Python d'abord. Le propriétaire ne veut plus payer
chaque règle en double sur les autres chantiers — l'action 177, qui corrige
dans les deux moteurs les écarts que les barèmes de la Cnav ont trouvés. Et
le moteur qui restera est le JavaScript.

## Ce que la session a vérifié

- **Les deux moteurs calculent la même chose, au bit près.** Sur les 913
  témoins de simulations, 171 732 nombres, aucun écart ; mais le test ne
  l'exigeait pas, qui tolérait 1e-9 en relatif.
- **Le Python ne peut pas encore cesser de suivre.** Les témoins se simulent
  au moteur Python (`scripts/construire_temoins.py`), et le portage leur est
  confronté (`tests/js/moteur.test.js`). Le coût bâtit et date ses carrières
  par le moteur Python (`castypes.carriere_de_la_grille`,
  `pilote.age_de_depart`, qui interroge `droit/ouvrir.py`), puis fait simuler
  sa grille par le portage, et `tests/test_agregats.py` et
  `tests/test_cout.py` exigent les deux moteurs identiques sur elle. Les
  exemples officiels (`tests/test_oracle.py`) éprouvent les fonctions du
  moteur Python. Chaque paire du moteur est atteinte par le coût et par 94 à
  173 fichiers de tests (`python scripts/jumeaux.py`).
- **Une règle écrite d'un seul côté** rougirait donc la suite à son premier
  envoi ; et une suite qu'on desserrerait laisserait le coût calculer sous
  l'ancienne règle quand le simulateur montre la nouvelle. Aucune paire du
  moteur n'est « couverte par le pont », au sens où plus rien de ce qui se
  publie ou se vérifie ne lirait son jumeau Python.

## La décision

### Le principe 4, sa dernière phrase récrite

> Tant qu'une étape a encore ses deux jumeaux, le JavaScript fait foi pour
> elle, et le Python le suit, au bit près (§ 7.1).

### Le JavaScript d'abord, le Python au bit près

Une règle nouvelle ou modifiée du moteur d'une carrière s'écrit d'abord dans
`moteur/js/`, avec son test tiré de la source : un essai de `tests/js/`, ou un
test qui fait tourner le portage par le pont. Son jumeau Python la suit dans
le même commit, ligne pour ligne. La concordance des témoins en est le test,
que `tests/js/moteur.test.js` exige désormais au bit près sous Linux x86_64,
où GitHub fabrique les témoins — ailleurs, une autre libm garde la tolérance
d'avant ; quand la concordance ne rougit pas sans lui, un témoin de plus
exerce la règle. Le Python suit, il ne décide plus : une différence entre les
deux se tranche contre la source, et se corrige d'abord dans le JavaScript.

Ce qui n'a pas de jumeau garde son langage : le coût et les carrières types
en Python, le texte du site en JavaScript.

### Quand une règle ne s'écrit plus qu'une fois

Au retrait de sa paire, par la méthode de la note 0003 : quand plus rien —
les témoins, le coût, les confrontations, les tests — ne lit son jumeau
Python. C'est ce que veut dire « couverte par le pont ». Au 31 octobre 2026,
aucune paire du moteur ne l'est ; la note de l'étape dit ce qui reste, dans
l'ordre.

### Les deux paires de données

Le Python garde ce qui lit le YAML et fabrique le paquet
(`scripts/construire_donnees.py`) ; tout calcul ou accesseur exécuté sur le
paquet n'a qu'un exemplaire, dans `moteur/js/`.

- **Les crédits des ministères** (`donnees/credits_ministeres.py`) : le
  Python ne garde que le chargeur, dont la fabrique écrit les parts au
  paquet ; la contribution employeur, ce qui va au compte « Pensions » et
  l'ordre des ministères ne se calculent plus que dans
  `credits-ministeres.js`, et leurs tests passent au portage.
- **La table des agrégats** (`donnees/agregats.py`) : le Python garde ses
  écrivains, `figer_*`, que la fabrique appelle ; ses lecteurs, qui ne
  servent qu'aux tests, s'en vont, et ces tests lisent la table par
  `agregats.js`. Les écarts de refus et de forme que la relecture avait
  relevés (note du 23 octobre 2026) se tranchent dans le JavaScript, chacun
  par son test.

### Le retrait par sous-ensemble cohérent

La méthode de la note 0003 se mène par paire, ou par sous-ensemble cohérent
de paires — celles qu'une même étape du pont libère —, une fois le pont
branché pour elles, la couverture de la concordance mesurée
(`python scripts/jumeaux.py --couverture`) et chaque paire relue contre ses
fiches. Ses six temps valent pour chaque paire du sous-ensemble ; le retrait
se fait dans un commit à lui, les témoins identiques.

## Ce qui ne change pas

La règle de l'endroit ; les six conditions du pont ; les six temps de la
méthode ; les témoins et les agrégats identiques, à l'octet ; une étape par
session ; les dépendances.

## Les solutions écartées

- **Ne plus rien écrire en Python dès aujourd'hui** : la suite rougirait, ou
  le coût mentirait (« Ce que la session a vérifié »).
- **Garder le Python pour référence jusqu'au pont**, comme le voulait la note
  0003 : le propriétaire tranche pour le JavaScript dès maintenant. L'ordre
  ne coûte rien de plus, et la copie qui restera est celle dont le test vient
  de la source.
- **Faire simuler les témoins par le portage dès aujourd'hui** : les nombres
  sont les mêmes, mais le Python écrit 43 114 flottants entiers « 2.0 », que
  node écrit « 2 ». Il faut d'abord une table des types, pour des témoins
  identiques à l'octet : c'est l'étape suivante.

## La migration

Aucun script de conversion : ni donnée ni contrat ne bouge, et les témoins
restent identiques. Le dépôt change en huit endroits : cette note ; le
principe 4 et le § 7.1 (`docs/architecture.md`), avec la ligne « Où va
quoi » qui dit comment se retire un doublon ; la carte du dépôt ; les
consignes de `src/` et de `moteur/` ; les cinq en-têtes du portage qui
disaient leur jumeau Python « qui fait foi » ; `tests/js/moteur.test.js`, au
bit près ; et une version de l'architecture. La page « Méthode » du site, qui
dit le modèle Python « de référence », se récrit quand les confrontations
passeront au portage, par une session du site.
