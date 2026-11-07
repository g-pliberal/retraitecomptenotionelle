# Étape 2 : le partage entre le moteur et le site, gardé

**La liste des modules du site.** Le site, dans `moteur/js/`, c'est
`pages.js`, `gabarit.js`, `routeur.js` et `adresses.js` : ils montrent, et
importent le calcul. Tout autre module du dossier est du calcul. La liste
est `SITE`, dans `tests/test_moteur_a_part.py`, à côté de
`tests/test_demarrage.py`, dont il reprend la lecture des imports ; un module
neuf du site s'y ajoute, faute de quoi la garde le prendrait pour du calcul
et refuserait ses imports du gabarit.

**`cles.js` est du calcul.** Il ne porte que le vocabulaire de la saisie —
les motifs sans emploi, dont les codes sont ceux de
`legislation/periodes_non_travaillees.csv`, et les clés qui décrivent les
règles —, sans aucun import ; quiconque décrit une carrière au moteur en a
besoin. Le démarrage du site le lit, comme il lit `format.js` et
`calendrier.js`, et c'est le sens permis : le site importe le calcul. Le
ranger au site aurait obligé à remettre ses constantes dans `saisie.js`, que
le démarrage ne charge pas (action 174, étape 5), ou à les copier. Le lien
`saisie.js` → `cles.js` n'est donc pas un lien à couper.

**Le test, vu rouge.** Quatre gardes, et une cinquième sur la mise en forme :
aucun module du calcul n'importe un module du site, statiquement ou à la
demande, quel que soit le guillemet ; aucun `import(…)` du calcul n'a de
cible calculée, que la garde ne saurait lire ; la fermeture de `pont.mjs`,
imports à la demande compris, ne contient rien du site ; la liste nomme des
fichiers qui existent. Avant la coupure, la première rendait
`{contexte.js: [gabarit.js], saisie.js: [gabarit.js]}` et celle du pont
`[gabarit.js]`, les deux liens de l'étape 1 ; la cinquième, qui veut
`nombre` et `euros` dans `format.js`, avec le rendu que le gabarit leur
donnait, échouait faute d'export.

**Les liens coupés.** `nombre`, `euros` et l'espace fine (`FINE`) passent du
gabarit à `format.js`, sans aucun import, à la lettre ; le gabarit les
importe et réexporte `nombre` et `euros`, si bien que `g.nombre` et
`g.euros` restent ce qu'ils étaient pour `pages.js` et le routeur.
`contexte.js` (un `euros`) et `saisie.js` (douze `nombre`, deux `euros`) les
importent de `format.js`, et n'importent plus le gabarit. Le local `euros`
de `Echelle.eurosDansLesBornes` ombre l'import dans sa méthode, sans
l'appeler. Le démarrage n'importe rien de plus : `gabarit.js` lisait déjà
`format.js`.

**Rien n'a bougé.** `construire_pages.py` refait les neuf pages sans écrire
un fichier ; `-m site` est vert, témoins du portage compris ; `-m rapide`
garde, sur le poste Windows, ses échecs d'avant, les mêmes fichiers, sans un
de plus.

**La règle écrite.** Le § 8 de `docs/architecture.md` (« Le site ») la dit,
avec sa version, `docs/architecture/versions/2026-11-07-le-moteur-a-part-du-site.md`,
et `moteur/CLAUDE.md` en porte la consigne. Aucun fichier ne s'est déplacé.

**Ce qui reste.** L'étape 3, l'entrée publique : un module qui, d'une
carrière décrite en données et du paquet, rend les résultats en données, sa
forme écrite et versionnée, et le pont qui passe par elle.
