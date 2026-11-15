# L'arrondi de la réduction générale : l'écart du témoin au SMIC

Action 161, à côté des étapes 9 : l'écart que les notes de l'étape 8c
signalaient sur `rattachement_pension_smic` (3,45 € par an de réduction
générale sous la proposition, années 11 à 13), et sur trois autres témoins
(`FICHES_QUE_LE_JUMEAU_NE_REFAIT_PAS`, `tests/test_facade_jumeau.py`).

## La cause

Le décret arrondit le coefficient « à quatre décimales, au dix-millième le
plus proche » (D. 241-7, I). Le portage l'arrondissait par
`Math.round(x * 1e4) / 1e4` : la multiplication arrondit déjà, et une valeur
juste sous la moitié d'un dix-millième, 0,21284999999999998, y devenait
2128,5, que `Math.round` montait à 0,2129. Le Python, `round(x, 4)`, rendait
0,2128, le bon. La valeur tombe si près de la moitié parce que le brut de la
proposition se cherche par dichotomie (`brutACoutDonne`) : le coût du travail
fait un saut de 0,0001 × brut (3,45 €) à chaque pas du coefficient, et la
dichotomie s'arrête au bord de ce saut. Même défaut, même correction, dans le
coefficient de la Lodeom.

## Ce qui est fait

- `arrondiAuDixMillieme` (`moteur/js/remuneration.js`), par `toFixed(4)`,
  qui arrondit la valeur exacte du nombre, pour la réduction générale et la
  Lodeom ; son test, `tests/js/reduction-generale.test.js`, vu rouge.
- Les quatre témoins concordent au bit près avec le jumeau ; la liste
  d'exceptions de `test_facade_jumeau.py` part.
- `construire_temoins.py` : aucun des 933 témoins de simulation ni des 85
  rendus de page ne bouge. Le coût agrégé, qui simule au portage, peut
  bouger de quelques euros sur un cas tombé au bord d'un saut : GitHub le
  refait.

**Tests.** `node --test tests/js/reduction-generale.test.js` : 2 passés ;
`test_facade_jumeau.py -k "comparaison or parts_couvrent"` : 10 passés ;
`python -m pytest -m rapide` : 5 426 passés.
