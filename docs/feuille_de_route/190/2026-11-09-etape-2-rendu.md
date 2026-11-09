# Étape 2 : le rendu des pages

**Le 9 novembre 2026, ce qui est fait.** Les machines 1 et 6 de
l'inventaire, dans `moteur/js/routeur.js` : chaque défaut reproduit par son
test, vu rouge dans Chromium, puis corrigé ; puis le rendu passé à un seul
état, sous des tests verts. Commit 195b1b6.

**Les courses.** Le pilote du navigateur (`tests/js/ecrans.mjs`) joue un
plan de plus, `courses` : une page ouverte au bureau, sans mémoire, des
requêtes retenues par la fin de leur adresse, puis des étapes — attendre une
requête, la refuser comme un réseau coupé ou la laisser passer, un geste joué
dans la page, une condition attendue, une pause. Deux gestes s'y chevauchent
à coup sûr, sans dépendre des délais du réseau. `tests/test_ecrans.py` en
joue quatre, en cinq secondes ; ses deux tests qui les jugent sont au niveau
`site` (`tests/conftest.py`).

**Le double message, corrigé.** Reproduit tel que l'inventaire le dit : sur
`simuler/#naissance=1980`, le paquet retenu, l'adresse changée, puis le
paquet refusé, la page portait deux `#contenu > .erreur` ; un rendu seul, un.
Le rendu dépassé ne dit plus rien : le dernier, qui attend le même
chargement, le dit. Un cas voisin, relevé en écrivant le test, puis
reproduit : sur une page toute faite recalculée sur place (Coût, sous un
réglage), deux échecs l'un après l'autre empilaient deux messages, chacun
posé devant la page. Le message d'un échec remplace désormais celui d'avant
(`data-echec`).

**Le relevé déposé, à moitié.** Deux fichiers : reproduit. Un PDF déposé,
dont le module de lecture est retenu ; puis un relevé en texte, lu jusqu'au
bout ; puis le module : le compte rendu du PDF (« Ce PDF ne porte aucun
texte ») s'écrivait le dernier, au-dessus d'une carrière remplie par le
second relevé. Un numéro par dépôt (`lectureDuReleve`) : la lecture dépassée
s'arrête à sa prochaine attente, sans rien écrire. Un rendu pendant la
lecture : ne se reproduit pas comme défaut. Joué dans les deux ordres — le
rendu attendant le même moteur que la lecture, ou fini avant elle —, la page
montre le formulaire de la nouvelle adresse, son compte rendu vide, et la
saisie retenue n'a rien reçu : le routeur ne la note que du formulaire
affiché. La lecture se perd en silence, comme tout ce qu'un rendu remplace ;
rien n'est corrigé.

**Le rendu en un seul état.** `rendu` tient l'état — `toute-faite`,
`demandee`, `occupee`, `posee`, `rendue`, `en-echec` —, le numéro du dernier
rendu commencé, la route et la requête affichées, et la route de la page
toute faite tant que c'en est une. Seule `passer(numero, etat, changements)`
le change, et elle porte la garde : un rendu dépassé n'avance plus, et chaque
reprise après une attente y repasse. `body[data-pret]`,
`body.calcul-en-cours`, `#contenu[aria-busy]` et `#contenu[data-prerendu]` ne
sont plus que sa projection (`marquer`), que lisent les tests et la feuille
de style ; `routeAffichee`, `requeteAffichee`, `numeroDeRendu` et `pret` sont
partis. Ce que la page montre ne change pas : les marques tombent aux mêmes
moments ; la page prête rend sa hauteur au même endroit, après qu'on a mesuré
où poser la lecture, d'où `posee`, distinct de `rendue` ; un rendu qui en
dépasse un autre en plein calcul laisse la page estompée.
`construire_pages.py` ne refait aucune page.

**Ce qui reste.** Rien de l'étape. Relevé à la lecture du code, non
reproduit : un calcul en échec laisse à `rendu.prerendu` la route d'une page
qui n'est plus toute faite, et le rendu suivant de la même route se fait
alors sur place, le message estompé, au lieu de l'écran d'attente.
