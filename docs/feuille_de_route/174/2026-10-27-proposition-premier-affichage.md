# La proposition du premier affichage en mobile

**Le 27 octobre 2026, la demande.** Le propriétaire, l'étape 5 publiée :
« Propose des solutions pour le premier affichage mobile. » Le détail de l'étape
5 est dans `2026-10-27-etape-5-le-moteur-a-la-demande.md`.

## Ce qui le retarde

- **Une seule ressource bloque l'affichage : la feuille de style.** En ligne
  (Lighthouse mobile, après l'étape 5), le premier contenu vient entre 1,2 et
  1,7 s, le plus grand entre 1,5 et 2,1 s. Avant de peindre, le navigateur
  attend `moteur/style.css`, 37 Ko compressés, dont 75 à 80 % ne servent qu'aux
  autres pages, aux résultats ou aux gestes ; Lighthouse estime le gain à 150 à
  300 ms. Avec elle partent les deux polices (48 Ko) et le routeur (60 Ko avec
  ses imports), qui se partagent le même réseau lent.
- **Le plus grand contenu** est le titre de l'accueil, et la note de résumé en
  tête des autres pages.
- **Ce que chaque page utilise de la feuille**, mesuré dans Chromium (les règles
  qui touchent un élément de la page ouverte, en mobile et au bureau, `@media` et
  `@font-face` compris) : de 4,3 à 6,8 Ko compressés, Coût le plus lourd.

## Les essais

Une copie jetable de l'arbre, Lighthouse en local, mobile, trois mesures par
page et par variante (six pour la première) ; médianes du premier contenu et du
plus grand, en secondes, et les notes de chaque mesure.

| Variante | Programme | Pourquoi changer | Méthode | Coût | Simuler |
|---|---|---|---|---|---|
| Aujourd'hui | 1,58 / 2,14 — 91, 98, 98 | 1,59 / 2,04 — 99, 97, 99 | 1,91 / 2,51 — 96, 96, 93 | 1,80 / 2,10 — 92, 95, 96 | 1,75 / 2,43 — 97, 96, 98 |
| Le CSS de la page en ligne, la feuille entière différée | 1,31 / 1,98 — 96 à 100 | 1,14 / 1,74 — 100 six fois | 1,31 / 1,91 — 98 à 99 | 1,71 / 2,48 — 90 à 98 | 1,22 / 1,90 — 96 à 100 |
| Les polices sans préchargement | 1,88 / 1,95 — 94 à 99 | 1,89 / 2,05 — 95 à 98 | 2,26 / 2,64 — 93 à 98 | 2,07 / 2,07 — 95 à 97 | 2,13 / 2,50 — 95 à 98 |
| Le routeur après l'événement `load` | 1,06 / 1,36 — 99 à 100 | 1,29 / 1,96 — 95 à 99 | 1,40 / 1,98 — 92 à 99 | 1,96 / 3,01 — 88 à 94 | 1,30 / 1,96 — 93 à 99 |
| Le CSS en ligne et le routeur après `load` | 1,66 / 2,60 — 95 à 100 | 1,54 / 2,52 — 94 à 97 | 1,97 / 2,79 — 92 | 1,79 / 2,87 — 90 à 96 | 1,74 / 2,57 — 93 à 98 |

- **Le CSS de la page en ligne** avance le premier contenu de 0,3 à 0,6 s
  partout sauf sur Coût, sans aucun décalage (CLS nul) : la page peint avec son
  HTML, la feuille entière arrive ensuite pour les gestes et les résultats. Coût
  y gagne peu : son HTML pèse 99 Ko compressés, et c'est lui qu'on attend.
- **Les polices sans préchargement** retardent le premier contenu de 0,3 s et
  ramènent les décalages que l'étape 2 avait supprimés (CLS de 0,014 à 0,042) :
  le préchargement reste.
- **Le routeur après `load`** aide l'accueil et nuit à Coût ; avec le CSS en
  ligne, il fait moins bien que le CSS en ligne seul : écarté.

## Ce que je propose

1. **Le CSS de chaque page dans son HTML, la feuille entière sans bloquer.**
   `construire_pages.py` écrit dans l'en-tête de chaque page les règles de
   `moteur/style.css` qui peuvent toucher cette page, et la feuille entière se
   charge sans retenir l'affichage (`media="print"` basculé au chargement, et
   le lien ordinaire dans un `<noscript>`). Le choix des règles se fait en
   Python, sans dépendance : une règle est gardée quand chaque classe, chaque
   identifiant et chaque balise de son sélecteur paraît dans la page — un
   sur-ensemble de ce que Chromium a mesuré, déterministe, qui ne demande pas
   de navigateur à la fabrique. Les tests des écrans (aucun décalage au
   chargement, rien qui déborde) jugent qu'il ne manque rien ; un test dit que
   chaque page porte sa feuille, et qu'elle est périmée si la feuille change.
   Coût : 5 à 7 Ko compressés de plus par page, que le cache ne partage pas ;
   la feuille entière reste téléchargée une fois, après la peinture. Gain
   attendu en ligne : de 95-99 à 98-100 en mobile, Coût excepté.
2. **En option, alléger Coût et Droits non cotisés.** Leurs tableaux de données,
   repliés sous chaque graphique, font les deux tiers de leur HTML. Ils
   pourraient se charger à l'ouverture de leur volet, depuis un fichier voisin
   fabriqué de même ; mais sans script, ils ne se liraient plus. C'est un choix
   sur l'accessibilité sans script, au propriétaire.
3. **Ne pas faire** : ôter le préchargement des polices, ni différer le
   routeur.

## Ce que le propriétaire tranche

- La proposition 1.
- La proposition 2 : des tableaux de données qui ne se lisent plus sans script
  sur Coût et Droits non cotisés, contre un premier affichage plus rapide sur
  ces deux pages.
