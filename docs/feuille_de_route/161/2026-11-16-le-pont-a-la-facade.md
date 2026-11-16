# Le pont à la façade : `test_pont.py` et `test_avantages.py` quittent la liste des fichiers sur le moteur Python

Action 161, quatrième vague, après `2026-11-16-la-fin-du-moteur-au-portage.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé. La liste compte 4
fichiers, `test_cout.py` en étant sorti en même temps
(`2026-11-16-le-cout-a-la-facade.md`).

## Ce qui est fait

- **`test_pont.py` prend `Carriere` et `Simulateur` de la façade.** Dix
  tests rougissaient, et non quinze, comme la note
  `2026-11-16-la-quatrieme-vague-a-mi-chemin.md` le comptait. Six se
  réparent sur place :
  - la variante d'une étude (la proposition prospective) passe au portage
    par son calcul, résolu dans le test comme le simulateur Python le
    résout (`_univers_des_variantes`) ; le coût sous la variante la lit sur
    le simulateur de la façade, dont la propriété `univers_de_la_demande`
    est remplacée le temps du calcul ;
  - la carrière que le portage bâtit revient sous la classe du Python, dont
    celle de la façade dérive ;
  - le coût des avantages perd la garde sur `Simulateur.scenario_actuel`,
    que la façade sert par le portage ;
  - les deux lectures de la revalorisation servie et de l'histoire du droit
    lisent les régimes sur `simulateur.catalogue`.
- **Les gardes nomment les jumeaux sans les importer** : un chemin pointé à
  `monkeypatch.setattr` (l'indexation, les règles de l'histoire du droit, le
  scénario 1). `_interdire` et `_jumeaux_qui_datent_et_batissent` passent à
  `tests/outils_pont.py` (`interdire`, `jumeaux_qui_datent_et_batissent`) ;
  `test_pont.py` les réexporte sous leurs noms, que `test_grille_large.py`
  importe.
- **Quatre confrontations au jumeau passent à `test_facade_jumeau.py`** :
  les fonctions du droit au bit près, l'indexation au bit, le prêt d'une
  table (la moitié du test qui compare au Python ; l'autre reste au pont),
  et le refus du barème mal formé par le compte du jumeau.
- **`test_avantages.py`** bâtit son apprenti par la `Carriere` de la façade,
  maintenant que `test_pont.py` lui passe un simulateur de la façade : il
  sort de la liste.

## Ce qui reste

Le chantier du coût, mené à part : `test_cout_age_depart.py` et
`test_grille_large.py`. Puis `test_facade.py` et `test_facade_jumeau.py`, qui
partent avec le moteur Python.

**Tests.** `test_pont.py`, `test_avantages.py`,
`test_fichiers_sur_le_moteur_python.py` : 98 passés ; les quatre
confrontations déplacées et les deux tests de `test_grille_large.py` qui
importent les gardes : verts ; `python -m pytest -m rapide` : 5 381 passés,
64 sautés.
