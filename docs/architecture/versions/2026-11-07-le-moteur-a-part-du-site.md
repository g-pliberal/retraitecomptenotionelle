# Version du 7 novembre 2026 : le moteur à part du site

Le § 8 gagne une règle, sur la décision du propriétaire du 7 novembre 2026
(décisions 34 et 35 du programme, action 187) : le site importe le moteur, et
le moteur n'importe rien du site, pour servir sans lui — à la fabrique, par
`pont.mjs`, et à d'autres, qui l'appelleraient chez eux. Les modules du site,
dans `moteur/js/`, sont `pages.js`, `gabarit.js`, `routeur.js` et
`adresses.js` ; tout autre module du dossier est du calcul. `cles.js` en est :
il ne porte que le vocabulaire de la saisie — les motifs sans emploi, les clés
qui décrivent les règles —, sans aucun import, et quiconque décrit une
carrière au moteur en a besoin ; que le démarrage du site le lise ne le range
pas du côté du site, pas plus que `format.js` ou `calendrier.js`. Le nombre et
le montant à la française, dont la saisie et le contexte écrivent leurs refus,
passent du gabarit à `format.js`, que le gabarit reprend tels quels : les
pages restent identiques à l'octet. `tests/test_moteur_a_part.py` garde la
règle : aucun module du calcul n'importe un module du site, ni statiquement
ni à la demande ; aucun import du calcul n'a de cible calculée, qu'il ne
saurait lire ; rien du site n'entre dans ce que `pont.mjs` charge. Aucun
fichier ne se déplace. Un calcul neuf dont une page a besoin s'écrit dans un
module du calcul, avec son test, et la page le lit ; un module neuf du site
s'ajoute à la liste du test. Les consignes de `moteur/` suivent.
