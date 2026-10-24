# Étape 6, sixième partie : `saisie.py` retiré, relu contre son portage, ses explications passées dans `saisie.js`

**La demande.** La cinquième vague du 24 octobre 2026 : huit sessions en
parallèle, une tâche chacune, que le propriétaire ne suit pas pas à pas.
Celle-ci tient la paire suivante du bloc : `saisie.py`, au rang 1 de la
carte, que plus rien n'importait ; cinq fiches le nommaient, et quatre
chiffres ancrés chargeaient ses constantes.

**La relecture.** Fonction par fonction, par un agent, ses constats vérifiés
aux lignes citées et par un essai des deux saisies. Sur les 904 requêtes des
témoins, l'adresse réécrite et douze déclarations — le conjoint, le décès,
l'invalidité, l'étranger, les périodes assimilées, les demandes, le temps
partiel, les dispenses… — sont les mêmes des deux côtés, hors des deux champs
que seul le portage lit depuis a2ded25 (`activite_conjoint_fin`,
`nouvelle_union_fin`) ; aucun autre champ n'est dans ce cas. Les écarts que la
lecture trouve tiennent à des entrées que le site ne produit pas, hors d'un
défaut commun aux deux saisies :
- sans la table des présomptions, le portage ne présume pas le jour de
  naissance (une `Error`, non un refus) et ne confronte pas le décès au
  mariage présumé, quand le Python lisait le vocabulaire ; la page et le pont
  la passent toujours ;
- le `\d` et le `strip` du Python lisaient les chiffres pleine chasse et
  quelques blancs de contrôle, que le portage refuse (« ３５００ ») ;
- `naissance=1e308` fait lever au portage une erreur du calendrier (« mois
  attendu entre 1 et 12, reçu NaN ») au lieu de son refus, et `1e21` s'y cite
  « 1e+21 » ;
- l'adresse réécrite garde six chiffres significatifs, des deux côtés
  (`formatG`, le `:g` du Python) — le défaut commun : un revenu fiscal de
  1 234 567 € s'y relit 1 234 570 ; l'écart n'est qu'au demi exact
  (1 000 005 : « 1e+06 » en Python, « 1.00001e+06 » dans le portage) ;
- l'encodage de l'adresse (`! ' ( ) *`) et l'ordre des clés hors du plan de
  base : sans effet sur ce qu'elle dit.

Le reste est sans effet sur aucune entrée possible (des comparaisons qui ne
diffèrent que pour NaN, que les lecteurs ne rendent jamais, des égalités de
rang) ou de forme (des classes en Python, des objets littéraux dans le
portage). Hors du module, deux paires qui restent : le calendrier arrondit un
âge décimal au mois au pair en Python, vers le haut dans le portage
(`liquidation=64.375` : 772 mois contre 773) ; la chronologie du Python lit
des dates que le portage refuse (« 0050 », « +962 », « 1_62 »). Rien n'a été
corrigé : ce retrait ne change aucun comportement.

**Ce que le Python expliquait.** `saisie.js` renvoyait 53 fois au Python
(« Voir … du Python », « Voir `saisie.py` », « côté Python ») ; chaque renvoi
porte désormais ce qu'il désignait, et 36 autres blocs reprennent ce que le
Python disait de plus : les sources (R. 351-23, L. 613-7, D. 633-19-2,
R. 662-1, L. 353-3, R. 353-4, R. 351-37…), les fiches, la raison des bornes,
le sens de l'inversion par la pension. Quatre phrases que le code dément sont
corrigées : le décès avant le départ, que le portage disait refusé, quand il
ouvre la réversion (R. 353-6) ; « les dix » clés des règles, qui sont
dix-neuf ; la pension étrangère, bornée à `AGE_LIQUIDATION_MAXIMAL` et non à
soixante-quinze ans ; le bloc de `niveaux`, égaré au-dessus de celui de
`lignesCarriere`. L'en-tête dit l'histoire du module, « le seul exemplaire de
la saisie ». Le diff ne touche que des commentaires : de 55 100 à 67 100
caractères (le Python en portait 69 300), le fichier de 3 510 à 3 700 lignes.

**Ce qui nommait le module.** Les cinq fiches, le temps partiel de la
fonction publique et la présomption du conjoint de l'autre sexe, que le
tableau de bord reprend ; les quatre chiffres ancrés lisent les constantes du
portage (`de=moteur/js/saisie.js`) ; l'arbre de `src/` du README, le § 12 et
l'annexe B de l'architecture, les consignes du moteur, le docstring du
contexte, les exemples de `jumeaux.py` et de `mesures_prose.py` ; le garde des
lectures ne nomme plus que le contexte. La carte compte 67 paires.

**Tests.** Le garde des déclarations, vu rouge au retrait (l'en-tête nommait
encore `saisie.py`), puis vert ; la carte, les fiches, les lectures ; les
107 essais de node ; la suite rapide et le filet du site ;
`construire_temoins.py --verifier`, à jour ; la conservation, rien de perdu
hors des paragraphes d'état récrits.

**Ce qui reste.**
1. `pages.js`, à sa ligne 7, dit encore `contexte.js` portage de
   `contexte.py` et de `saisie.py` : pour une session du site.
2. Les défauts du portage que la relecture laisse, chacun par son test :
   `naissance=1e308`, les six chiffres de l'adresse réécrite, et
   `DEFAUTS.demandes`, le seul tableau des défauts qui ne soit pas gelé.
3. L'arrondi du calendrier et la lecture des dates de la chronologie, à la
   relecture de leurs paires.
4. La paire du pilote, avec les départs de l'estimation ; le centre du coût,
   sous le nom de `contexte.py` (point 4 de la cinquième partie).
