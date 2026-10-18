# Étape 7, suite : les départs qui suivent l'espérance de vie, coupés le 14 octobre, leur règle au propriétaire

**La demande.** Vague 2b du 17-18 octobre 2026, lancée par la session
d'orchestration sur la demande du propriétaire, « Fait toutes les tâches qui
n'ont pas besoin de mes décisions » : le premier point du bloc « Reprise » de
l'étape au 17 octobre, *les départs qui suivent l'espérance de vie* — le
point 4 de la première note, « en variante de comportement (mosart) » —, à
faire si la règle de départ ne relevait pas d'une hypothèse que le
propriétaire n'a pas tranchée, à lui poser sinon. Elle en relève, et le point
est coupé : rien n'est calculé.

**Le point est coupé depuis le 14 octobre.** Le classement du 9 octobre le
range au rang « léger ou nul », parmi les confrontations et les indicateurs
des étapes 3, 7, 9, 11 et 19, qui « ne changent aucun chiffre tant qu'ils ne
trouvent pas d'erreur » (`2026-10-09-classement-par-poids.md`) ; le
propriétaire a décidé, le 14, que ce rang se déclare sans se faire
(`2026-10-14-la-coupe.md`) ; la session de la coupe a passé le point de
MOSART à l'état `coupe`, sa raison écrite : « Une variante de comportement,
non une meilleure estimation » (`data/reference/referents.yaml`, `mosart`).
Les notes de l'étape jusqu'à celles du 16 octobre, puis le bloc « Reprise »
du 17, le comptaient encore parmi les restes, d'une liste recopiée de note en
note que le registre démentait : c'est par elle que le point a été confié à
cette session. Dans la même phrase du classement, *2025 sous la loi seule*,
qui attend la table d'Eurostat, est du même rang ; il n'a pas de point au
registre, et aucune fiche ne le déclare encore.

**Rouvert, il demanderait une hypothèse du propriétaire.** « L'âge de départ
est un choix du programme (65 ans au README) », écrit le registre
(`elinaikakerroin`) ; l'âge auquel chaque génération partirait, à mesure que
sa longévité croît, en est un autre, que rien dans le dépôt ne tranche.
Quatre choix, que cette session n'a pas faits :

1. *Hypothèse centrale ou variante.* MOSART en fait l'hypothèse principale de
   ses projections depuis 2011 ; le registre y voit une variante, qui « borne
   ce que le coût d'un système notionnel doit au comportement », MOSART
   jugeant l'effet « too early to validate ». Centrale, elle déplacerait les
   chiffres de la page Coût des systèmes qui la suivent ; en variante, elle
   s'y ajouterait sans les toucher.
2. *La règle*, qui donne à chaque génération son âge, et chacune un autre.
   Les deux tiers du gain d'espérance de vie, que MOSART juge assez pour
   garder sa pension ; la Suède indexe de même son âge cible, 65 ans plus les
   deux tiers du gain à 65 ans depuis 1994. Le gain entier, à cotisations
   égales : l'âge d'équilibre du diviseur, que le dépôt calcule déjà
   (`cycle_de_vie.age_d_equilibre`), tient constante la durée de la
   retraite — 65 ans et 2 mois pour la génération 1962, 69 ans pour 2000, sur
   la table commune. La part de la vie passée en retraite, tenue constante :
   la règle du simulateur du COR (`cycle_de_vie.age_de_part_de_vie_constante`).
3. *Les systèmes qui la suivent.* La proposition part à 65 ans au plus tôt
   (`Parametres.age_legal_liberal`) ; les scénarios 2 à 5 gardent les âges du
   droit en vigueur, « parce qu'ils mesurent ce que change le COMPTE, à
   carrière égale » (`config.py`) ; le scénario 1 est le droit, et chaque cas
   type y part à l'âge que sa loi lui ouvre (`pilote.age_de_depart`). Dans la
   seule proposition, le report la comparerait au droit en vigueur à
   comportements différents ; partout, il changerait aussi les âges du
   scénario 1.
4. *L'âge légal.* Fixe à 65 ans, il reste le plancher du départ. L'indexer
   sur l'espérance de vie, à la manière finlandaise, est le point
   `elinaikakerroin`, `a_trancher` : un des choix de l'étape 13.

**Au propriétaire.** Rouvrir ou non les départs qui suivent l'espérance de
vie ; rouverts, les quatre choix ci-dessus. La règle se pose sur les cas
types, sans microdonnées, comme le registre le dit de l'hypothèse des deux
tiers (`mosart`, bilan).

**Ce qui est fait.** Le bloc « Reprise » de l'étape, récrit au 18 octobre,
passe les départs de « Reste » à « Au propriétaire », et dit 2025 du rang
léger. Le registre ne change pas : le point y est coupé, sa raison écrite.
Aucun chiffre ne bouge, aucune règle du scénario 1 n'est en cause : ni veille
du droit, ni entrée au journal. Le bloc de la note « naissances et migrations
dans les pages » (16 octobre), que tient la session des pages, compte encore
les départs parmi ses restes, avec l'indexation et la mortalité
différentielle, faites depuis.

**Ce qui reste** de l'étape : la queue observée de 85 à 98 ans ; les inaptes
de la Cnav, que la grille n'a pas ; 2025, à déclarer ; les scénarios 2 à 5
sous la variante (note du 16 octobre, « indexation sous la variante ») ; à la
session des pages, les phrases de la page Coût (notes du 16 et du 17
octobre).
