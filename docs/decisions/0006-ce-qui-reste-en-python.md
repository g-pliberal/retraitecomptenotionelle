# Note de décision 0006 — ce qui reste en Python

*Décidée le 2 novembre 2026 par le propriétaire. Il avait demandé à la session
de l'action 161 : « Pour l'action 161, il faut bien séparer ce qui doit être
écrit en python de ce qui doit être écrit en JavaScript. Il ne faut pas
supprimer complètement le python. Analyse et regarde ce qui doit rester en
python. » La session a mesuré la frontière
(`docs/feuille_de_route/161/2026-11-02-ce-qui-reste-en-python.md`) et lui a
soumis trois points, qu'il a validés tels quels : faire de cette frontière une
note de décision, le critère de la zone grise, le rangement sous `donnees/`
des chargeurs sortis des jumeaux. Elle précise la règle de l'endroit
(principe 4, note 0003), fonction par fonction, et la méthode de retrait des
notes 0003 et 0005.*

## Le problème

La règle de l'endroit dit où s'écrit une étape ; l'action 161 l'applique par
paires de jumeaux, et parle de « retirer le jumeau Python ». Or un jumeau
Python du moteur n'est pas fait que de règles. La mesure du 2 novembre 2026,
au commit 25efe97, y trouve :

- **les chargeurs du paquet** : `scripts/construire_donnees.py` bâtit
  `moteur/donnees.json` par 43 des 53 classes de `scenarios/actuel.py` — les
  tables du droit en vigueur, âges, durées, décotes, minimum contributif,
  conversions de points —, et par `RevalorisationsPensions`,
  `_charger_ages`, `charger_prelevements`, `Affiliations`,
  `versions.preparer` ; la fabrique du paquet, la certification et les
  lecteurs de sources nomment directement 8 840 lignes de définitions des
  jumeaux, classes entières comptées ;
- **les types que le pont échange** : `Parametres`, que 26 fichiers sans
  jumeau lisent, `Carriere`, `AnneeCarriere`, `Metier`, `DateMois`, les
  énumérations des réglages ; le coût et les études décrivent en Python ce
  qu'ils confient au portage ;
- **les accesseurs que le coût et les études lisent**, sur le YAML et non sur
  le paquet : `ComptesRetraite`, `DepensesRetraite`, `AssietteActivite`,
  `DonneesMacro`, `DistributionPensions`…

Effacer un jumeau en entier casserait le paquet, le pont et le coût. Et des
calculs agrégés se font aux deux endroits sans être le moteur d'une
carrière : la garantie, la revalorisation servie, l'impôt sur le revenu, la
restitution, les variantes des comptes, que le coût fait en Python et que le
site refait. La règle de l'endroit les enverrait tous au JavaScript, quand
certains ne dépendent d'aucune saisie du lecteur.

Le Python garde de toute façon l'essentiel de ses lignes : 281 517 au
2 novembre 2026, dont 55 385 dans les jumeaux ; si les 38 paires du moteur
partaient entières, 240 413 resteraient.

## La décision

### Le Python ne disparaît pas

S'écrivent en Python, et y restent :

- **la fabrique des données** : acquérir, certifier, lire le YAML, fabriquer
  le paquet ;
- **ce qui calcule une population, un agrégat ou une étude** sous les
  réglages de référence : le coût, les carrières types, le coût des
  avantages, le bilan, les études ; le site lit leur résultat, figé au
  paquet ;
- **ce qui fait tourner node** : le pont, la mémoire des calculs, les
  témoins, les pages toutes faites ;
- **la carte des règles et ses contrats** (`noyau/`) ;
- **les tests et l'outillage** : pytest reste le banc, du moteur JavaScript
  aussi, qu'il fait tourner par le pont ;
- **dans chaque jumeau du moteur**, ses chargeurs du paquet et les types que
  le pont échange.

S'écrivent en JavaScript seul : ce que le navigateur exécute ; les règles du
moteur d'une carrière ; les accesseurs et les calculs exécutés sur le paquet
(note 0005).

### Le retrait coupe le fichier

Retirer un jumeau du moteur n'en ôte que les règles :

- ses **chargeurs** passent sous `src/retraite_notionnelle/donnees/`, sans
  méthode de règle : ils lisent le YAML, et la fabrique en écrit le paquet ;
- ses **types** restent, un exemplaire par langage, puisque chacun les lit :
  c'est le contrat du pont, qui les tient ensemble en les échangeant ;
- une **étude qui appelait une fonction du moteur** hors du simulateur la
  demande au pont, par lot ;
- une **étude qui remplace une fonction du moteur**, le temps d'une variante,
  l'écrit en données — une couche, ou un paramètre de la demande au pont —
  avant que la règle ne parte ;
- `moteur/donnees.json` reste **identique à l'octet**, comme les témoins et
  les agrégats : c'est la garde qui dirait qu'un chargeur est parti avec les
  règles.

Les accesseurs qui lisent le YAML pour la fabrique, le coût ou les études
restent en Python ; ne partent que ceux que seuls des tests lisent.

### La zone grise : un calcul agrégé que le site refait

Un calcul que le coût fait en Python et que le site refait :

- **ne s'écrit qu'en JavaScript si le lecteur peut en changer le résultat** —
  sa carrière, un réglage — ; le coût le demande alors au pont, en une fois
  pour toutes ses années et ses cohortes, et non appel par appel, qui
  ralentissait la population (la surcote, note de l'étape 7 de l'action
  161) ;
- **ne s'écrit qu'en Python sinon** : il se fabrique sous les réglages de
  référence, et le site lit son résultat figé au paquet, comme le bilan et
  les agrégats.

Le propriétaire tranche chaque paire à sa relecture, par ce critère : la
garantie, l'impôt sur le revenu, la restitution, la revalorisation servie,
les variantes des comptes.

## Ce qui ne change pas

La règle de l'endroit, que cette note précise sans la récrire ; le JavaScript
qui fait foi pour le moteur (note 0005) ; les six conditions du pont et les
six temps de la méthode (note 0003) ; le retrait par paire ou par
sous-ensemble cohérent ; les témoins et les agrégats identiques, à l'octet ;
une étape par session ; les dépendances, PyYAML seul en Python, aucune en
JavaScript.

## Les solutions écartées

- **Effacer chaque jumeau en entier** : le paquet, le pont et le coût ne se
  fabriqueraient plus.
- **Garder les chargeurs dans les fichiers du moteur**, amputés de leurs
  règles : un fichier du moteur sans moteur, où la session suivante
  chercherait la règle.
- **Envoyer au JavaScript tout calcul fait aux deux endroits**, sans
  critère : le coût paierait le pont pour ce que le site ne fait que lire.
- **Tout en JavaScript, la fabrique comprise** : déjà écartée par la note
  0003.

## La migration

Aucun script de conversion : ni donnée ni contrat ne bouge, et rien ne se
retire ici. Le dépôt change en six endroits : cette note ; le principe 4, le
§ 7.1 et la table « Où va quoi » (`docs/architecture.md`) ; la carte du
dépôt ; les consignes de `src/` et de `moteur/` ; une version de
l'architecture ; le bloc « Reprise » de l'action 161. Les chargeurs passent
sous `donnees/` au retrait de leur jumeau, chacun dans le commit qui retire
ses règles.
