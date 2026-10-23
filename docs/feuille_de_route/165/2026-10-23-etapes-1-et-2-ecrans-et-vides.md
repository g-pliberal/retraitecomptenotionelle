# Les étapes 1 et 2 : rien ne déborde, ce qui va ensemble se voit ensemble, et les vides

**Ce qui a été mesuré d'abord**, le 23 octobre 2026, dans Chromium, les neuf
pages et les résultats d'une simulation, de 320 à 1 440 points. À 360 points,
la page Coût débordait de 169 points — la page entière glissait de gauche à
droite — et Droits non cotisés de 20 ; quarante cadres de Coût défilaient en
largeur, vingt-quatre de Droits non cotisés : chaque courbe, élargie à 30 rem
pour que ses textes restent lisibles ; chaque schéma de Sankey, à 42 rem ; la
cascade, à 40 ; la frise, longue de 11 732 points même au bureau ; chaque
tableau de quatre colonnes et plus ; les quatre cartes de Partager, à 36 rem.
Les quatre montants du simulateur s'étageaient sur 1 404 points à 390 de
large, 1 618 à 320 : jamais deux à la fois sous les yeux. La légende de la
cascade tombait à 67 points de son dessin, sous les libellés en biais, dont le
plus long était coupé, au bureau comme au téléphone.

**Le test**, `tests/test_ecrans.py`, vu rouge sur tout cela avant la première
retouche. Il pilote un Chromium sans fenêtre par le protocole des outils de
développement, sur le WebSocket de node (`tests/js/ecrans.mjs`) : aucune
bibliothèque, le dépôt n'en prend pas. Il sert le dépôt par
`http.server`, visite chaque route à 320, 390, 768, 1 024 et 1 440 points,
dépliants fermés puis ouverts, et mesure. Cinq tests : rien ne déborde ni ne
défile en largeur, rien ne sort de l'écran ; aucune exception ; chaque
légende touche son tracé et tient avec lui dans un écran ; les quatre
systèmes, du titre du premier au montant du dernier, dans un écran ; aucun
vide de plus de 40 points entre deux blocs voisins sur un téléphone, 56 au
large. Vingt-cinq secondes. Sans Chromium, ils sont passés — `NAVIGATEUR`
en désigne un ; GitHub a `google-chrome`. Ils sont du niveau complet et du
filet `site`.

**Les tableaux** se replient, sans changer une ligne de leur HTML : le
script d'`index.html` (`plierLesTableaux`) écrit sous chaque case le nom de
sa colonne, redit les rôles ARIA, et décide, à chaque changement de largeur de
leur cadre (`ResizeObserver`), si le tableau tient. En **rangée** — deux ou
trois colonnes de valeurs courtes —, l'intitulé de la rangée passe au-dessus et
les valeurs restent côte à côte sous l'en-tête ; en **fiche** — au-delà, ou
dès qu'une case porte une phrase —, chaque valeur sous le nom de sa colonne,
une phrase sur toute la largeur. Un tableau de nombres sur trois colonnes ne
se replie que s'il déborde ; une rangée qui déborde encore passe en fiche. Les
largeurs minimales qui faisaient défiler (`.dispositifs`, quatre colonnes et
plus, les inventaires de Méthode) ne valent plus que dépliés.

**Les graphiques** se dessinent à la largeur de la colonne. `pages.rendre`
reçoit cette largeur, que `index.html` mesure sur `<main>`, et la pose au
gabarit (`g.poserEcran`) ; sous 720 points, le cadre d'une courbe a autant
d'unités que la colonne a de points, des marges en points, ses textes à treize
pixels, et sa hauteur aux deux tiers de sa largeur ; au-delà, le cadre de
toujours, que les témoins figent — ils sont rendus sans écran, au large. Une
colonne qui change de largeur fait redessiner la page sur place. Le nom au
bout des courbes, qui demande cent unités à droite, ne s'écrit qu'au large ;
la légende le donne. **La légende** se pose à côté du tracé quand la place le
permet, au-dessus sinon, jamais dessous : une rangée qui se replie à rebours
(`wrap-reverse`), sans requête média. Sur un téléphone, la case où s'écrit la
valeur lue passe sous chaque libellé, qui reprend toute la largeur.

**Le schéma de Sankey**, dans une colonne étroite, coupe ses libellés en deux
lignes au plus et rapproche ses colonnes du bord, de la place exacte que leurs
étiquettes demandent. **La cascade** est couchée, à toutes les largeurs :
chaque marche sur sa ligne, libellé à gauche, montant à droite, barre dessous ;
plus de libellé en biais, plus de libellé coupé ; on la lit au doigt de haut
en bas, aux flèches haut et bas. **La frise des flux** montre une colonne tous
les cinq ans, la première et la dernière en plus, et ses colonnes passent à la
ligne ; chaque année reste dans son tableau. **Les cartes à publier** se
lisent partout comme celles de Le saviez-vous ? : à la largeur de l'écran,
en tailles de lecture, et au format de l'image le temps de la composer. **Les
bascules** de six années passent à la ligne ; celles de deux branches restent
insécables, plus serrées. **Le JSON** des résultats passe à la ligne.

**Les quatre systèmes du simulateur** sont quatre cartes, deux par deux sur un
téléphone, quatre de front dès 48 rem, réduites à ce qui se compare — le nom,
le salaire, la retraite, ce que les recettes en paient, la barre. Leurs
rangées s'alignent d'une carte à l'autre (`subgrid`). Ce que chaque système
mesure, sa composition et son taux de remplacement se déplient sous la carte
(« Ce qu'il mesure »). Du titre du premier au montant du dernier : 613 points
à 320, 518 à 390, 156 au bureau.

**Les vides** : quarante-huit points au-dessus de chaque titre de section sur
un téléphone, trente-six désormais ; soixante-quatre sous le formulaire de
l'accueil, quarante ; cinquante-six entre deux thèmes de Le saviez-vous ? et
entre les deux colonnes empilées d'une paire ; une ligne vide sous chaque
graphique, que réservait une aide au clavier invisible ; cinq rem sous le pied
de page. Les cartes rendent au texte une part de leurs marges sur un
téléphone.

**Ce que le propriétaire peut vouloir trancher.** La frise ne dessine plus
qu'une année sur cinq ; la cascade a quitté la forme debout, au bureau aussi ;
ce que mesure chaque système est replié sous sa carte. Les tableaux repliés
allongent certaines pages sur un téléphone : Carrières types de 4 553 à 6 551
points à 390, Droits non cotisés de 16 312 à 19 478 — ce qu'on lisait en
glissant de gauche à droite se lit en descendant. Moins de mots, aux étapes 3
à 10, les raccourcira.

**Les tests qui ont bougé.** Deux aides de `tests/test_web.py` lisaient la
composition d'un montant avant sa barre : elle est maintenant dans le
dépliant, sous la barre, et elles la lisent avant la glose. Les témoins de
pages sont refaits : 61 rendus sur 79 changent, aucune simulation.
