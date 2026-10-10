# Les tests du portage que node rejoue

**Le 10 octobre 2026, la mesure.** Trente et un tests lancent node pour
confronter le portage au modèle : 137 s de calcul en tout, sur quatre
processus, la machine chargée. Quatre en font les deux tiers : `node --test`
(37 s), les étapes de l'acquisition (`test_droit.py`, 21 s), les carrières
tirées au hasard (`test_web.py`, 18 s) et les étapes de la liquidation
(`test_liquidation.py`, 16 s). Dans `node --test`, un seul essai prenait 21 s
sur 29 : les pages, rendues et comparées à leurs témoins. Dans les trois
autres, node ne prend que 1 à 2,5 s ; le reste est le calcul Python des mêmes
saisies, 12,4 s, 9,0 s et 11,9 s.

- *Les pages, comparées deux fois.* Depuis la phase 8, le texte du site ne
  s'écrit qu'en JavaScript : `construire_temoins.py` fait rendre les pages par
  le portage, sur le paquet, et `test_les_temoins_du_portage_sont_a_jour` les
  fait rendre de nouveau et les compare, titre et corps. L'essai de
  `moteur.test.js` refaisait la même chose — même portage, même paquet, mêmes
  blocs retirés —, contre le même fichier : il ne confrontait plus deux
  moteurs, seulement le portage à lui-même. Il est ôté ; restent les deux
  pages rendues sur un paquet d'avant le 7 octobre, qui éprouvent autre chose.
  Le README, l'en-tête de `pages.js` et le contrôle
  `portage_compare_aux_temoins` des affirmations disent qui compare les pages.
- *La moitié Python, gardée.* Elle ne dépend que du modèle, du code du test et
  de ses requêtes. `moitie_python` (`tests/outils_portage.py`) la fait garder
  par la mémoire des calculs, sous l'empreinte de `src/`, `data/` et
  `scripts/`, et sous une clé qui porte le texte du fichier de test, que
  l'empreinte ne lit pas, et les arguments. Un fichier de test retouché depuis
  le chargement du modèle se calcule sans mémoire, comme `_code_retouche` le
  veut pour les sources. La moitié JavaScript, celle que ces tests éprouvent,
  se rejoue à chaque passage. `test_outillage.py` tient la mécanique, sur un
  test factice.

**Mesuré**, les mêmes trente et un tests, deux passages de suite : 38 s la
mémoire vide, au lieu de 53, puis 36 s. Au second passage, les quatre tests
lourds font 26 s de calcul au lieu de 93 : `node --test` 13 s, les étapes de
l'acquisition 6, celles de la liquidation 4, les carrières au hasard 3. Une
session qui change le modèle ne gagne que les vingt secondes des pages ; une
autre, l'essentiel.

**Ce qui reste.** Les pages au hasard (`test_web.py`, 7 s), qui mêlent les
deux moteurs requête par requête ; les cumuls tirés au hasard et le portage du
coût, 5 s chacun, à mesurer avant de les garder ; `node --test` lui-même,
13 s, qu'une empreinte du portage, du paquet et des témoins sauterait quand
rien n'a bougé, comme `ISOLES` le fait pour `test_pousser.py`, à condition
d'y déclarer des dossiers.
