# L'étape 5 : le moteur à la demande

**Le 26 octobre 2026, la demande.** Le propriétaire, l'étape 4 publiée : « On
peut regarder s'il n'y a pas des choses inutiles qui bloquent une meilleure
performance ? » ; puis, devant le constat, « Vas-y ». L'étape 4 (c) est dans
`2026-10-26-etape-4c-les-pages-toutes-faites.md`.

## Le constat

- **Le moteur entier partait avec chaque page.** Mesuré dans Chromium (la
  couverture du code, à l'ouverture de Pourquoi changer) : soixante-seize
  modules, 3,3 Mo bruts, environ 1 Mo compressé ; trois servaient — le routeur,
  quatre fonctions du gabarit, les tables de `libm.js`. Les soixante-treize
  autres — le simulateur, les étapes du droit, la saisie, le texte des neuf
  pages (`pages.js`, 840 Ko bruts) — étaient évalués sans qu'une seule de leurs
  fonctions soit appelée. Lighthouse, en ligne, comptait 1,1 Mo transférés par
  page et 347 Ko de JavaScript inutilisé. La cause : le routeur importait tout,
  et `adresses.js` tirait la saisie entière pour une liste de clés.
- **La feuille de style** bloque l'affichage, 37 Ko compressés dont 75 à 80 %
  ne servent pas à la page ouverte. Ce n'est pas du code mort — une seule règle
  orpheline, `.graphique .etiquette-serie` — : ce sont les styles des autres
  pages et des résultats. Laissée en l'état.
- **Un défaut de l'étape 4 (c), trouvé en route.** `peutHydrater` jugeait le
  dessin tout fait pour toute page, tracés ou non : sur un écran de 456 à
  1 017 points — les tablettes, un grand téléphone couché, une petite fenêtre —
  et de 320 à 357, chaque page se recalculait par le moteur. Le test du
  navigateur l'a montré, la fenêtre par défaut de Chromium (800 points) en
  étant : Pourquoi changer y demandait le paquet de données.

## Ce qui est fait

- **`moteur/js/cles.js`** porte ce que le démarrage lit de la saisie : les clés
  des règles (`CLES_MODELISATION`) et les motifs sans emploi (`SANS_EMPLOI`,
  `CODES_SANS_EMPLOI`), sans aucun import ; `saisie.js` les reprend pour ses
  autres lecteurs, et `adresses.js` les lit là.
- **Le routeur n'importe que six modules** : lui-même, `adresses.js`,
  `cles.js`, `gabarit.js`, `format.js`, `calendrier.js`. La saisie, le contexte
  du moteur, le texte des pages et la lecture du relevé viennent au premier
  calcul (`lesModules`), que `moteur()` attend en même temps que le paquet.
- **Les gestes qui en ont besoin l'attendent** : la reprise d'une saisie
  retenue, « Calculer » depuis l'accueil (qui fusionne avec la mémoire),
  « Retirer cette période », les bascules du simulateur après une saisie, le
  dépôt d'un relevé. Sur le simulateur, un brouillon retenu, comme une
  simulation, se reprend par le moteur : `peutHydrater` les refuse tous deux.
- **`dessinConvient`** (`gabarit.js`) dit si une page toute faite convient à la
  colonne : toujours sans tracé ; la demi-colonne ne compte que pour des schémas
  de front.
- **Les tests** : `tests/test_demarrage.py` (la fermeture des imports statiques
  du routeur, les imports à la demande, les clés reprises par la saisie) ;
  `test_adresses_navigateur.py` (ce que le navigateur demande vraiment : rien du
  moteur sur une page de texte, sur l'accueil, après un renvoi vers une section ;
  tout, pour des résultats) ; `test_pre_rendu.py` (`dessinConvient`, quinze
  cas) ; et la phrase du README sur le poids d'une page, dont la sonde nomme
  exactement ce que le démarrage importe.

## Les mesures, en local, le 27 octobre 2026

Lighthouse 13, l'arbre servi d'ici, une mesure par route et par profil, contre
celle de la fin de l'étape 4 (c). Accessibilité, Bonnes pratiques, SEO et Agentic
restent à 100 partout, le CLS nul.

| Page | Mobile 4 (c) → 5 | TBT mobile | Bureau 4 (c) → 5 |
|---|---|---|---|
| Programme | 97 → 98 | 179 → 0 ms | 99 → 100 |
| Simuler | 93 → 97 | 273 → 13 ms | 100 → 100 |
| Résultats | 67 → 73 | 4 524 → 1 353 ms | 71 → 76 |
| Coût | 92 → 97 | 298 → 38 ms | 100 → 100 |
| Pourquoi changer | 99 → 98 | 9 → 0 ms | 100 → 100 |
| Partager | 95 → 99 | 0 → 0 ms | 100 → 100 |
| Le saviez-vous ? | 99 → 99 | 70 → 0 ms | 100 → 100 |
| Carrières types | 97 → 99 | 0 → 0 ms | 100 → 100 |
| Droits non cotisés | 93 → 98 | 196 → 23 ms | 100 → 100 |
| Méthode et sources | 89 → 99 | 402 → 46 ms | 99 → 100 |

Trois mesures de chaque côté sur sept pages en mobile confirment l'écart, au-delà
du bruit : avant, de 88 à 99 et un TBT de 0 à 398 ms ; après, de 94 à 100 et un
TBT de 0 à 41 ms. Lire l'accueil transfère 146 Ko compressés au lieu de 1 033 ;
le premier calcul y ajoute 889 Ko de moteur et 788 de paquet. Les tests des
écrans passent de 87 s à 44 s.

## Ce qui reste

- **Le premier contenu en mobile**, de 1,3 à 1,9 s (le plus grand de 1,8 à
  2,4 s) : ce que le navigateur doit recevoir avant de peindre — la feuille de
  style, qui sert surtout aux autres pages, les deux polices, le HTML. Une feuille
  commune et une par page, ou le style critique en ligne, sont les pistes.
- **Les résultats d'une simulation** : 73 en mobile, 76 au bureau (décision 3,
  au propriétaire). Au bureau, leur plus grand contenu tombe à 2,5 s au lieu de
  0,5 : le formulaire tout fait cède plus tôt la place à l'écran d'attente, le
  routeur démarrant avant le moteur.
- **Mesurer en ligne**, la suite verte et la copie déployée.
