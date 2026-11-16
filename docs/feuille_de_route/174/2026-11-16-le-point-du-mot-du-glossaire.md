# Le point du mot du glossaire : la comparaison du seul style rendue stable

**Le 16 novembre 2026, la demande.** `test_chaque_page_se_peint_avec_son_seul_style`
rougissait la suite de GitHub une course sur dix environ, pour un point : un
`span.mot` de Coût (16 contre 17 à 390 points), puis de Carrières types (17
contre 18, à 390 et à 1 440 points), et repassait au vert à la course suivante.

## La cause

- **Toujours le même élément, toujours la hauteur, toujours un point de
  moins** d'un côté ou de l'autre : le conteneur d'un mot du glossaire,
  `span.mot`, élément en ligne sans fond, bordure ni marge.
- **Chromium ne lui donne pas de boîte à lui** (« inline culled ») : son cadre
  est alors celui de ce qu'il porte, le mot et son pointillé d'un point
  (18 points à 15 px). **Mais il la lui donne parfois**, et ne la reprend
  plus : le cadre est alors la hauteur de la police seule (17 points). Un
  contour posé puis ôté suffit à la créer pour de bon ; en chargement, un
  état passager fait de même, au hasard du moment. La page est peinte
  pareil : ce cadre ne se peint pas.
- Ni la police, ni l'attente du chargement, ni la charge de la machine : la
  page retardée feuille, police, routeur ou données, le processeur ralenti
  vingt fois, la hauteur reste celle du conteneur sans boîte ici.

## Ce qui a changé

- **Le test d'abord** : `test_le_style_d_une_page_ne_tient_pas_aux_boites_que_chromium_donne_aux_mots`
  fait forcer par le pilote ces boîtes sur la page au seul style
  (`boites_forcees`, `FORCER_LES_BOITES` dans `tests/js/ecrans.mjs`) ; il
  rendait, rouge, l'écart exact de GitHub (`span.mot | 226 | 550 | 105 | 17`
  contre `18`). Il vérifie aussi que le forçage a bougé au moins un cadre.
- **La mesure** (`INSTANTANE`) : un élément en ligne sans décor — ni fond,
  ni bordure, ni marge, ni contour — se mesure sur son contenu (un `Range`),
  ce qu'il peint ; tout autre élément garde son cadre. Rien de ce que le test
  vérifie ne s'en affaiblit : les enfants, le texte, la police et la taille
  restent comparés, au point près, sans tolérance.
- `tests/test_ecrans.py` : 35 tests au vert ; `pytest -m rapide` au vert.
