# Étape 6 : les figures et la saisie au gabarit du site du parti

**D'où elle part.** Le corps des pages pris (étape 5), les deux sites, posés
côte à côte à 1280 et à 390 points, s'écartaient encore par leurs figures, leurs
tableaux et la saisie. Les valeurs se lisent dans la feuille de style du site
du parti (`assets/css/style.css` : `.figure`, `.choix`, `.legende`,
`.tableau-defilant`, `thead th`, `tbody tr:hover`, `input`, `select`).

**Ce qui est fait** (`moteur/style.css`, `moteur/js/gabarit.js`,
`moteur/js/routeur.js`). Aucun mot du site n'a changé, ni aucune teinte des
quatre systèmes.

- **La carte de figure** (`section.cle`) perd son filet safran : une carte
  blanche au filet neutre. Sa barre de partage prend la largeur de la carte,
  derrière un filet neutre, et non plus un trait d'or arrêté aux deux tiers.
- **La légende au-dessus du tracé, en ligne**, pour les courbes et la cascade ;
  elle était à droite, en colonne.
- **Le tracé sur toute la largeur de sa carte.** Tenu à 720 unités et étiré, ses
  textes de treize unités en auraient fait vingt à l'écran : au large, le
  gabarit dessine donc courbes et cascade à la largeur de la carte, la colonne
  moins ses deux retraits (`LARGE`, troisième valeur d'`ecransDe`), un peu plus
  haut (34 % de la largeur, entre 300 et 380 unités), et au plus à 1 100
  unités. La page toute faite, rendue pour une colonne de 1 040 points, porte
  un dessin de 984 unités, qui convient à 12 % près aux cartes des écrans de
  1 024 points et plus (`tracesConviennent`). Sans écran — les témoins, le
  Python qui lit la page —, le cadre reste celui de toujours, 720 sur 300.
- **Les choix en pastilles rondes** de 44 points (`.bascule`, `.onglets`), la
  cochée pleine de pétrole, texte blanc : celles des figures comme celles du
  simulateur.
- **Les tableaux dans un cadre** (`.defilant`) : filet, rayon de 8 points, fond
  blanc, en-tête teinté du ton d'appui et en gras, ligne survolée surlignée
  (`--surlignage`). Replié sur un téléphone, le tableau garde son cadre et son
  en-tête quitte sa teinte. Le seul tableau écrit sans cadre, sur Droits non
  cotisés, a pris le sien (`pages.js`).
- **Les champs** : 44 points de haut, au lieu de 54, retrait de 8 et 12 points,
  bord fort et rayon de 8 points, qu'ils avaient déjà. Sur l'accueil, le bouton
  « Calculer » prend la hauteur des champs de sa rangée : haut de 63 points, il
  les étirait.

**Ce qui s'écarte du site du parti, et pourquoi.**

- Le bord fort est le `--trait-champ` de ce site, un ton plus sombre que le
  `--bordure-forte` du parti : il tient 3 pour 1 sur les trois fonds clairs.
- Au bureau, un texte de tracé fait 15 pixels, contre 13 chez le parti : le
  dessin tout fait, de 984 unités, s'agrandit de 16 % dans une carte de 1 144
  points. Un seul dessin large sert ainsi tous les écrans de 1 024 points et
  plus, sans charger le moteur.
- La légende garde, à côté de chaque libellé, la case où s'écrit la valeur lue
  au survol : ses entrées sont plus espacées que celles du parti.
- La source et la réponse d'une carte gardent leur mesure de 46 rem : une note
  de 180 signes par ligne ne se lit pas.
- Les cartes `.points` (Méthode) gardent leur filet safran : ce ne sont pas des
  figures.

**Ce que l'étape coûte.** Entre 800 et 1 014 points d'écran — une tablette en
hauteur, une fenêtre étroite —, la carte est trop étroite pour le dessin de
984 unités : Coût et Droits non cotisés s'y redessinent par le moteur, comme
elles le faisaient déjà sous 800 points hors des téléphones. Le dessin de 720
unités y convenait.

**Un défaut du pont, vu en chemin.** L'écran est un état du gabarit, et
`site.rendre` le laissait posé : un graphique d'essai, appelé après une page
rendue au large, se dessinait à 984 unités. Le pont (`web/site.mjs`) le remet
à zéro après chaque rendu.

**Les tests.** `test_les_figures_et_la_saisie_sont_celles_du_site_du_parti`
(`tests/test_ecrans.py`, mesuré par `figures` dans `tests/js/ecrans.mjs`) ;
dans `tests/test_pre_rendu.py`, les constantes d'`ecransDe`,
`test_un_graphique_convient_a_sa_carte_dans_la_tolerance`,
`test_au_large_un_graphique_se_dessine_a_la_largeur_de_sa_carte` et
`test_une_page_rendue_pour_un_ecran_ne_le_laisse_pas_au_gabarit`. Vus rouges
d'abord. Vérifié à l'écran à 1280, 1024 et 390 points, à côté du site du
parti.

**Ce qui reste.** L'étape 7, le panneau « Affichage » : voir la note de
l'étape 4. Les témoins de pages et le paquet sont laissés à GitHub : ils
portaient déjà le retard d'autres actions (186, 191), et se refont après le
paquet.
