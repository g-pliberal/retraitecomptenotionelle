# Étape 4 : la coquille du site du parti

**D'où elle part.** Le propriétaire, le 9 novembre 2026 : « J'aimerais que le
site reprenne encore plus l'aspect de mon autre site :
Nombre-de-fonctionnaires. Fait un plan pour effectuer cela. » L'étape 1 en
avait pris les couleurs, Jost et le logo ; les deux sites, posés côte à côte
à 1280 et à 390 points, s'écartaient encore par la mise en page. Le plan
tient en quatre étapes (4 à 7), qu'il a approuvées le même jour avec trois
décisions : les six engagements de l'accueil passent en grille de cartes ; le
titre surligne son passage au safran au lieu de l'écrire en safran ; le
panneau « Affichage » se reprend pour la taille, la police très lisible et
l'interligne, sans le thème sombre.

**Ce qui est fait.** La coquille, que les neuf pages partagent
(`moteur/js/gabarit.js`, `moteur/style.css`).

- **La lueur turquoise** de l'en-tête du parti (`--lueur`), sur le bandeau et
  sur l'affiche. Celle du parti est un cercle posé en haut à droite d'un
  en-tête d'un seul tenant ; ici le bandeau colle en haut et l'affiche défile
  dessous : la lueur ne dépend donc que de l'abscisse, pour que les deux se
  raccordent sans couture à toute hauteur, et l'affiche l'éteint vers le bas.
  Chacune est peinte par un `::before` : le fond reste le pétrole uni, et le
  contraste des textes s'y mesure encore. L'affiche atteint les bords de
  l'écran par ce `::before`, et non plus par une ombre portée, qui ne sait
  peindre qu'un aplat.
- **L'affiche** : le surtitre en Jost gras, en capitales espacées, en
  safran ; le titre à 700, son passage clé surligné au safran.
- **Le bandeau** : le nom du parti en gras, un filet entre la marque et les
  onglets, les onglets en demi-gras ; sur un téléphone, le bouton du menu
  porte les trois traits de Lucide (`moteur/icones/menu.svg`), seuls sous
  36 rem. Quand le bandeau ne colle plus, il reste positionné, sans quoi sa
  lueur prendrait la hauteur de l'écran.
- **Le pied** : une bande pétrole foncé d'un bord à l'autre, trois colonnes
  sous leur titre en safran — le site et ce qu'il ne vaut pas, le modèle
  ouvert, avant de citer un chiffre —, les liens en turquoise, puis le pont
  vers le site du parti sous un filet. Il dit ce qu'il disait. La liste des
  pages du pied du parti n'y est pas : le pied ne dépend pas de la page, et
  le bandeau la tient sous les yeux.

**La règle du 5 novembre, amendée.** `test_l_accueil_se_compose_sur_une_seule_echelle`
refusait toute capitale par le style et toute graisse au-delà de 600. Le site
du parti a son surtitre en capitales et ses titres à 700 : le test admet
désormais ces deux points (`SURTITRE_DE_L_AFFICHE`, `GRAISSE_MAXIMALE`), et
tient le reste — ni italique, ni taille hors de l'échelle, ni marge hors de
la grille.

**Les tests.** `test_la_coquille_est_celle_du_site_du_parti`
(`tests/test_ecrans.py`, mesuré par `tests/js/ecrans.mjs`), dont les valeurs
viennent de la feuille de style du parti ; `test_le_pied_se_range_en_trois_colonnes`
et `test_le_menu_du_telephone_porte_son_pictogramme` (`tests/test_web.py`).
Vus rouges d'abord.

**Ce qui reste, étape par étape.** Une session chacune, jamais en même temps
que celle du texte (étape 2), qui retouche les mêmes pages.

- **Étape 5, le corps des pages** (`pages.js`, `style.css`) : les boutons
  d'action de l'affiche (un safran, les autres au filet blanc), que
  `affiche` ne sait pas encore porter ; des bandes alternées d'un bord à
  l'autre (`--fond`, `--fond-appui`), chacune ouverte par un surtitre en
  capitales turquoise et un `h2` à 700 ; les chiffres clés au gabarit
  `.chiffre` du parti — barre safran de 6 points à gauche, la valeur, le
  libellé en gras, le détail —, dont les six engagements de l'accueil en
  grille de trois par deux et les cartes de Coût, valeur d'abord ; les
  encadrés teintés, turquoise pour l'information, ambre pour l'attention
  (« En clair ») ; le plan d'une page en carte « Sur cette page » ; l'appel
  final en carte pétrole à la lueur.
- **Étape 6, les figures et la saisie** : la carte de figure sans filet
  safran, ses contrôles en pastilles rondes (cochée : pétrole plein), la
  légende au-dessus, le graphique sur toute la largeur de la carte ; les
  tableaux dans un cadre arrondi à l'en-tête teinté ; les bascules et les
  champs du simulateur au même gabarit. Les teintes des quatre systèmes ne
  changent pas.
- **Étape 7, le panneau « Affichage »** : la taille du texte, la police très
  lisible (Atkinson Hyperlegible) et l'interligne, retenus dans le
  navigateur. Le thème sombre n'en est pas : il referait chaque couleur de
  graphique et doublerait les mesures de contraste.

Public Sans reste la police du texte : le site du parti prend celle du
système, l'écart se voit peu, et la changer déplacerait toutes les mesures
d'écran.
