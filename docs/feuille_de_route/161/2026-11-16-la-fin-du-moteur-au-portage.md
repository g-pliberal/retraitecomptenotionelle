# La fin du moteur au portage : `test_moteur.py` quitte la liste des fichiers sur le moteur Python

Action 161, quatrième vague, après `2026-11-16-les-cas-types-au-portage.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé. `test_moteur.py` sort de
`FICHIERS` : il garde 15 tests, tous sur le portage ; la liste en compte 7.

## Ce qui est fait

- **Le simulateur** de `test_moteur.py` est celui de la façade : le passé
  invariant de l'âge de départ, les variantes d'espérance de vie et le
  partage du capital entre régimes y passent tels quels. Ce dernier bâtit
  un simulateur sous la source des cotisations voulue, et prend son
  constructeur et son régime unique, au lieu d'un `ConstructeurCompte` bâti
  à la main, que la façade refuse sous un autre régime unique.
- **Le salaire moyen** se lit par `pont.droit`
  (`carriere.ancrage_salaire_moyen`, `carriere.salaire_moyen_annuel`, année
  par année), et non plus par `indice_salaire_moyen`.
- **Le compte recomposé à la main** lit les taux d'indexation au pont
  (`indexation.taux`), et le diviseur sans actualisation aussi
  (`conversion.coefficient.diviseur` et `.esperance_residuelle`, sous
  `taux_anticipe_conversion=0`). La sonde de l'espérance résiduelle ne lit
  que l'âge et l'année : le diviseur se demande à la même date, sans le
  mois, sans quoi ils diffèrent de 0,008 an.
- **La population et le rattachement par la pension** bâtissent le cas type
  au portage (`_carrieres`). Le point fixe du rattachement se vérifie en
  recalculant le vingtile de la pension servie par sa définition — la
  pension ramenée au millésime de la DREES au rythme du salaire moyen, lu au
  pont, rangée par `distribution.part_sous` — et non plus par
  `Convertisseur.population_par_pension`. Les assertions sur
  `rattache_par_pension`, un attribut du convertisseur Python, sont tombées.
- **Les noms hérités du prototype**, qui confrontent le portage au Python,
  passent à la fin de `test_facade_jumeau.py`, qui part avec le jumeau.

## Ce qui reste

`test_pont.py` (voir `2026-11-16-la-quatrieme-vague-a-mi-chemin.md`), puis
ce qui attend le coût.

**Tests.** `test_moteur.py` (15) et `test_fichiers_sur_le_moteur_python.py` :
verts ; le test des noms hérités, vert dans `test_facade_jumeau.py`.
