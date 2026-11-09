# Étape 5 : le corps des pages au gabarit du site du parti

**D'où elle part.** La coquille prise (étape 4), les deux sites, posés côte à
côte à 1280 et à 390 points, s'écartaient encore par le corps des pages. Le
propriétaire avait tranché le 9 novembre 2026 : les six engagements de
l'accueil passent en grille de cartes, trois par deux au large, au gabarit des
« Quatre chiffres pour commencer » de son autre site. Le reste se lit dans la
feuille de style de ce site (`assets/css/style.css`).

**Ce qui est fait** (`moteur/js/gabarit.js`, `moteur/js/pages.js`,
`moteur/style.css`). Aucun mot du site n'a changé.

- **Les chiffres clés** au gabarit `.chiffre` : une carte blanche, une barre
  safran de 6 points à gauche, la valeur en Jost gras, le libellé en gras
  dessous, le détail en texte doux. Les six engagements de l'accueil sont six
  cartes, trois par deux au large, deux de front sur une tablette, une colonne
  sur un téléphone ; leur rang (« 01 » à « 06 ») est parti avec la pile de
  lignes. Les cartes d'ouverture de Coût, Pourquoi changer, Carrières types,
  Droits non cotisés et Méthode donnent la valeur d'abord.
- **Les tranches** (`g.tranche`, `.tranche`, `.tranche.alt`) : le corps se
  range en bandes d'un bord à l'autre de l'écran, une sur deux sur le ton
  d'appui. La tranche reste dans la colonne ; son `::before` porte le ton
  jusqu'aux bords, comme celui de l'affiche, et son fond reste uni, où le
  contraste se mesure. L'accueil en a cinq ; « Pour aller plus loin » en est
  une sur chaque page qui le porte ; chaque thème de « Le saviez-vous ? » et
  les deux blocs de Partager aussi.
- **Les surtitres** en Jost gras, en capitales espacées, en turquoise sombre,
  derrière le tiret safran ; **les titres** `h2` et `h3` à 700 partout.
- **Les encadrés** (`.note`) teintés, à barre de 5 points : turquoise pour
  l'information, « En clair » compris, ambre pour l'attention
  (`.avertissement`, `.vigilance`). « En bref », sur les résultats, suit.
- **Le plan d'une page longue** : une carte blanche aux liens nus, son titre en
  Jost gras, à la place des pastilles.
- **L'appel** (`.carte-appel`) : une carte pétrole à la lueur turquoise, bouton
  safran, second bouton au filet blanc — l'appel final de l'accueil, et « Et
  pour vous ? » sur Coût et Droits non cotisés.
- **Les boutons de l'affiche** : `affiche(surtitre, titre, chapeau, actions)`
  en porte sous le chapeau, le premier en safran, les suivants au filet blanc
  (`a.bouton.clair`). L'accueil porte les deux de son appel final, dans les
  mêmes mots : « Simuler ma retraite », « Ce que ça coûte, et qui paie ».
- **Un défaut d'avant l'étape, vu à l'écran** : sur un téléphone, la valeur et
  le libellé des cartes de chiffres passaient sous la barre safran, coupés par
  le bord de la carte — une règle du temps où ces cartes étaient une frise.

**Ce qui s'écarte du site du parti, et pourquoi.**

- Une section du parti s'ouvre sur un surtitre. Ici, seules celles qui en
  portaient un le gardent (« Le calcul », « Vérifiez plutôt que de nous
  croire ») : en ajouter serait écrire des mots, que le propriétaire arrête.
- Le plan s'intitule toujours « Dans cette page », et non « Sur cette page ».
- Le blanc d'une tranche est de 48 points au large, 32 sur un téléphone, contre
  64 chez le parti : `test_aucune_page_ne_laisse_de_grand_vide` tient 56.
- La valeur d'une carte garde l'échelle du site (`--t-chiffre`, 48 points au
  large), l'accueil ne comptant que neuf tailles.
- Le simulateur n'a pas de tranche : sa page est à l'étape 6.

**Les tests.** `test_le_corps_des_pages_est_celui_du_site_du_parti`
(`tests/test_ecrans.py`, mesuré par `corps` dans `tests/js/ecrans.mjs`), dont
les valeurs viennent de la feuille de style du parti ;
`test_l_accueil_dit_son_principe_puis_six_arguments_sans_jargon`
(`tests/test_web_revues.py`), qui lit six cartes sans rang et les deux boutons
de l'affiche. Vus rouges d'abord.

**Ce qui reste.** L'étape 6, les figures et la saisie, puis l'étape 7, le
panneau « Affichage » : voir la note de l'étape 4. Un nom s'évite : `bande`
est une fonction du gabarit (les graphiques empilés) et `.appel` une classe
du glossaire — d'où `tranche` et `.carte-appel`.
