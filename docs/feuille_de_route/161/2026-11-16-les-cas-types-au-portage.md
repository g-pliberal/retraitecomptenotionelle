# Les cas types au portage : les quatre tests des cas types de `test_moteur.py` datés et bâtis par le site

Action 161, quatrième vague, après `2026-11-16-le-mois-au-portage.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé. `test_moteur.py` reste
dans `FICHIERS` : il garde 15 tests, dont ces quatre désormais au portage.

## Ce qui est fait

- **Les quatre tests des cas types** — le cas type au SMIC, la carrière
  heurtée de la maquette Osiris, l'inapte et l'ex-invalide de la Cnav — ne
  bâtissent plus leur carrière par `CasType.construire`, qui faisait tourner
  le pilote et le moteur Python. Le pilote du portage date chaque départ
  (`castypes.departs_au_portage`, comme la grille du coût), la façade bâtit la
  carrière de `cas.options(generation, age)` et la simule ; le niveau relatif
  du cas au SMIC se lit par `pont.droit` (`conversion.niveau_relatif`). Les
  attendus n'ont pas changé : ceux du droit et des études de la Cnav.
- L'égalité de `CasType.niveau_relatif` au niveau du simulateur est tombée :
  elle confrontait deux calculs du moteur Python.

## Ce qui reste de `test_moteur.py`

L'ancrage du salaire moyen (`pont.droit` sert `carriere.ancrage_salaire_moyen`) ;
le passé invariant de l'âge de départ, à la façade (`carriere_simple`) ; le
test des noms hérités du prototype, dont la place est
`test_facade_jumeau.py` ; les variantes d'espérance de vie ; les tests de la
conversion qui attendent le coût, et le compte recomposé à la main.

**Tests.** `test_moteur.py` (15) : vert ; `python -m pytest -m rapide` :
5 373 passés, 64 sautés.
