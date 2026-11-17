# La note de décision 0009, adoptée : le droit daté dans les versions de fiche

Le 16 novembre 2026, le propriétaire adopte la note de décision 0009
(`docs/decisions/0009-le-droit-date-dans-les-versions-de-fiche.md`). Elle
est née d'un diagnostic de l'architecture, et a été éprouvée sur quatre
fiches écrites en versions sur le papier (`docs/decisions/0009/`). Elle
s'applique dans cette action.

**Ce qu'elle décide.** Une règle que plusieurs textes réécrivent vit dans les
versions de sa fiche, une par réforme et par public. Une version porte ce que
son texte écrit : une table, une valeur, un renvoi daté à une autre fiche ou
à sa propre rédaction antérieure, chaque partie avec le texte qui la décide.
Ses bornes se lisent dans la disposition d'application de son texte. Elle a
deux preuves, la certification et l'exemple officiel, ou dit ce qui manque.
Les fichiers de régime gardent leurs renvois, qui deviennent datés au jour,
cités et sans valeur de repli. Le champ `code` nomme les fonctions qui
appliquent la fiche. Le document d'architecture le dit depuis la version du
16 novembre 2026 (contrat C.2, table datée, annexe B, ligne 6 du chemin).

**L'ordre.** Une étape par session, sur Fable 5.2 : les cinq cliquets que la
note nomme ; l'âge légal, avec la recherche de la première date de départ et
la fin des deux copies d'avant réforme ; l'âge du taux plein, la durée
requise, la carrière longue et la surcote ; les renvois des régimes, en
commençant par les dix dates de bascule qui peuvent changer un résultat.
Aucun résultat ne doit bouger.

**Ce qui reste ouvert.** Le droit d'avant 1985 reste un chantier de
données : 100 versions y sont `supposée`.

**Le rectificatif du même jour.** Relue par un avis extérieur, la note a reçu
à sa fin un rectificatif, que le propriétaire a adopté. Trois phrases y sont
corrigées. Le champ `code` est déjà confronté au dépôt, dans un sens
(`tests/outils_carte.py`). legiretraite a un fichier par paramètre, et non
par loi. La surcote des trimestres de 2004 à 2006 est tranchée : l'article 3
du décret n° 2006-1611 vise les pensions prenant effet à compter du
1er janvier 2007, auxquelles le dépôt sert 0,75 % là où le texte donne 1 % ou
1,25 %. Sa correction déplace des résultats : elle attend l'accord du
propriétaire, et passe avant l'étape de la surcote, qui n'en déplace aucun.
Cinq précisions s'y ajoutent : le renvoi daté et le renvoi à une version
nommée, dont la forme s'écrit au début de l'étape de l'âge légal ; l'arrêt du
calcul sur un renvoi sans cible ou qui boucle ; la recherche bornée du
premier départ ; la fin de l'étape de l'âge légal, avec un vrai consommateur,
un scénario qui garde une loi passée et une réforme fictive ; la table
fusionnée, fabriquée et jamais écrite à la main.

**Ce que la note ne dit pas.** Si le domaine `cumul`, dont l'étape 2 attend,
passe avant ou après cet ordre : au propriétaire. Il a tranché le 17 novembre,
ni avant ni après : l'étape 2 du `cumul` se mène en parallèle, chacune dans sa
session, sur Fable 5.2, une fois la suite verte, avec des sources officielles
seulement ; et la correction de la surcote de 2004 à 2006 est approuvée.
