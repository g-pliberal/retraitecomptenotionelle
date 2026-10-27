# Version du 27 octobre 2026 : le moteur à la demande

Le routeur n'importe, au démarrage d'une page, que de quoi animer la page toute
faite : `moteur/js/routeur.js`, `adresses.js`, `cles.js`, `gabarit.js`,
`format.js` et `calendrier.js` (action 174, étape 5). La saisie, le contexte du
moteur, le texte des pages et la lecture du relevé — et tout ce qu'ils importent,
le simulateur et les étapes du droit — se chargent au premier calcul, ou au
premier geste qui en a besoin (`lesModules`, que `moteur()` attend avec le paquet
de données).

Ce que le démarrage lit de la saisie, les clés des règles et les motifs sans
emploi, vit dans `moteur/js/cles.js`, sans import ; `saisie.js` le reprend pour
ses autres lecteurs. `tests/test_demarrage.py` tient la fermeture des imports
statiques du routeur ; `tests/test_adresses_navigateur.py`, ce que le navigateur
demande vraiment.

Une page toute faite convient à la colonne qu'on mesure quand rien de ce qu'elle
dessine n'en dépend (`dessinConvient`, `moteur/js/gabarit.js`) : une page sans
tracé, à toute colonne ; la demi-colonne du large ne compte que pour des schémas
de front.
