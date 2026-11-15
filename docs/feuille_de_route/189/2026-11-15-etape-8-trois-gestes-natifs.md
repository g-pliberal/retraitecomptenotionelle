# Étape 8 : le panneau et les bulles tenus par le navigateur

**D'où elle part.** Le 14 novembre 2026, le propriétaire demande si le dépôt
`GoogleChrome/modern-web-guidance` (fiches des équipes de Chrome, Edge,
Firefox et MDN : le geste d'interface fait par le HTML et le CSS
d'aujourd'hui) peut servir au site. Lu, il en retient trois points, qu'il
demande de reprendre : le panneau « Affichage », les bulles du glossaire, les
tableaux qui défilent.

**Ce qui est fait** (`moteur/js/gabarit.js`, `moteur/js/routeur.js`,
`moteur/style.css`, les neuf pages refaites).

- **Le panneau « Affichage »** porte `closedby="any"` (fiche « light-dismiss a
  dialog ») : le navigateur le ferme d'un clic sur le fond. Le routeur ne le
  rattrape plus que là où l'attribut manque (`FOND_QUI_FERME` ; Safari, au
  15 novembre 2026). Le pilote des écrans (`tests/js/ecrans.mjs`) sait
  désormais un vrai clic de souris (`cliquer`) et une vraie touche
  (`touche`) : un geste que le navigateur tient seul ne répond pas à un clic
  simulé par script.
- **Les bulles du glossaire** (`mot`, `bulle`) sont des `popover` (fiche
  « toggletip ») : la couche du dessus, où ni un tableau qui défile ni une
  carte ne les rognent ; une seule ouverte ; fermées d'un clic ailleurs ou par
  Échap, par le navigateur. Le routeur ne fait plus que l'ouverture — un mot
  est un `<span role="button">`, que `popovertarget` ne connaît pas — et
  `aria-expanded`, tenu sur `beforetoggle`, que la feuille lit pour ancrer la
  bulle sous son mot (`anchor-name`, `position-try-fallbacks`, au-delà de
  34 rem). Sans ancrage, ou sur un téléphone, la bulle se pose en bas de
  l'écran, comme avant sur un téléphone. Un second clic sur le mot la
  referme : l'appui hors d'une bulle la ferme d'abord, et le routeur retient à
  l'appui laquelle était ouverte (`ouverteALAppui`).
  `test_une_bulle_du_glossaire_est_tenue_par_le_navigateur` le joue au
  téléphone et au bureau.
- **Les tableaux qui défilent** restent tels quels. La fiche « scrollability
  hints » dessine l'ombre par une requête `scroll-state`, que seul Chromium
  connaît : l'ombre actuelle, en fond attaché, resterait pour les autres, et
  la nouvelle demanderait de passer `.defilant` en boîte flexible autour de
  son tableau. Et un tableau trop large se replie désormais plus qu'il ne
  défile (`plierLesTableaux`). À reprendre quand `scroll-state` sera partout.
