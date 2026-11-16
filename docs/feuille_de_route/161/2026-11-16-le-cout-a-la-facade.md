# Le coût à la façade : `test_cout.py` quitte le moteur Python

Action 161, étape 9m, après `2026-11-16-les-populations-cnav-au-portage.md`,
premier pas de ce qui attendait le coût
(`2026-11-16-la-quatrieme-vague-a-mi-chemin.md`). Aucune règle du droit,
aucune donnée de calcul, aucune page n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) perd `test_cout.py` : 6 fichiers
avec la sortie de `test_moteur.py`, menée en parallèle.

## Ce qui est fait

- **`test_cout.py` prend le simulateur et `ouvrir` de la façade.** Ses 193
  tests passent. Les cas types n'y sont plus datés par le pilote Python
  (`CasType.age_liquidation_pour`, `CasType.construire`), qui lisait
  `coordonner.regimes_interpenetres` : deux aides du fichier, `_age` et
  `_construite`, les datent par le portage (`castypes.departs_au_portage`),
  la variante « absolu » comprise, comme `test_cout_age_depart.py`. Le test
  du minimum vieillesse simule ses quatre cases par la façade, au lieu de
  `calculer_cas_types`.
- **La façade sert de plus**, à la mortalité, `courbe_survie` et
  `population_niveau_de_vie_euros` (`pont.MORTALITE_DE_LA_FACADE`), que la
  garantie du coût lit, et l'année des niveaux de vie, une donnée lue par son
  chargeur ; au convertisseur, `population_de`
  (`pont.CONSTRUCTEURS_DE_LA_FACADE`, l'entrée des constructeurs du
  `pont.mjs`). Chaque appel est confronté au jumeau
  (`test_facade_jumeau.py`), et la source le dit dans `test_facade.py`
  (l'Insee, vingtiles 2020-2024 en euros de 2022).
- **La mortalité se sert sous un coût modifié.** Trois tests de
  l'engagement remplacent une fonction du coût (`monkeypatch`), que le
  portage ne lit pas ; la façade refusait pourtant toute mortalité sous un
  modèle modifié. Elle ne la refuse plus que si la mortalité du Python
  elle-même est remplacée (`_mortalite_remplacee`, qui compare ses fonctions
  à celles de l'import).

## Ce qui reste

Six fichiers : `test_pont.py` (une autre session),
`test_avantages.py` (sort quand `test_pont.py` bâtit son apprenti
lui-même), `test_cout_age_depart.py` (l'espion du plafond de décote, tant
que la décote sans plafond ne s'écrit pas en données),
`test_grille_large.py` (19 tests rouges à la façade : `scripts/grille_large.py`
appelle `coordonner.regimes_interpenetres` sur le moteur, retouche le modèle,
lit `Simulateur.univers_de_la_demande`), et les deux confrontations de la
façade, qui partent avec le moteur Python. Prochaine étape :
`test_grille_large.py`, en commençant par ce que `scripts/grille_large.py`
demande au moteur.

**Tests.** `python -m pytest -m rapide` : 5 382 passés, 64 sautés.
`test_cout.py` (193), `test_facade.py`, `test_facade_jumeau.py` et
`test_fichiers_sur_le_moteur_python.py` : verts.
