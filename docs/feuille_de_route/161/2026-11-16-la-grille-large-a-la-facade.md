# La grille large à la façade : `test_grille_large.py` quitte le moteur Python

Action 161, étape 9n, après `2026-11-16-le-cout-a-la-facade.md` et
`2026-11-16-le-pont-a-la-facade.md`. Aucune règle du droit, aucune donnée de
calcul, aucune page n'a bougé. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) perd `test_grille_large.py` : il en
reste trois.

## Ce qui est fait

- **`test_grille_large.py` prend le simulateur de la façade.** Ses 107 tests
  passent. Dix-neuf rougissaient, pour trois raisons.
- **Les cas types se datent au portage.** Le test appelait
  `CasTypeLarge.age_liquidation_pour` et `CasType.construire`, qui lisent
  `coordonner.regimes_interpenetres` ; deux aides, `_age` et `_construite`,
  les datent par `castypes.departs_au_portage`, comme `test_cout.py`.
  L'attente du départ passe au portage par `pour_le_portage`.
- **Les réglages du script ne marquent plus le modèle modifié.** Seize tests
  ne remplaçaient que des constantes du script (`G.CLASSES_DE_NATURE`…),
  mais par `monkeypatch`, sous lequel la façade refuse tout. Une fixture,
  `reglages`, les pose par `pytest.MonkeyPatch.context()` et tait la mémoire
  par `CALCULS_SANS_MEMOIRE` : le portage reçoit ce qu'ils changent dans les
  cas types qu'on lui demande. `monkeypatch` reste aux deux tests qui
  remplacent une fonction du coût.
- **La façade laisse lire les cotisants**, une donnée, à leur chargeur
  (`DONNEES`, `tests/facade.py`), comme les effectifs de retraités ;
  `test_facade.py` le dit.
- **Les deux gardes « sans les jumeaux »** prennent `outils_pont.interdire`
  et `jumeaux_qui_datent_et_batissent`, que l'étape du pont venait d'y
  mettre, avec des chemins pointés pour le scénario 1 et le simulateur
  Python, que le script bâtit encore lui-même sous les seuls paramètres.

## Ce qui reste

Trois fichiers : `test_cout_age_depart.py` (l'espion du plafond de décote,
tant que la décote sans plafond ne s'écrit pas en données), et
`test_facade.py` et `test_facade_jumeau.py`, qui partent avec le moteur
Python. `scripts/grille_large.py` bâtit encore des simulateurs Python
(`_proratisations`, `ouvertures_decotees`) ; la liste ne le voit pas, et son
retrait vient avec celui du moteur.

Le test d'écran de la page Coût (`test_ecrans.py`, un pixel de hauteur
d'un `span.mot`, 17 contre 16) a rougi la course de 02 h 31 sur GitHub.

**Tests.** `python -m pytest -m rapide` : 5 383 passés, 64 sautés.
`test_grille_large.py` (107), `test_facade.py`, `test_facade_jumeau.py`,
`test_fichiers_sur_le_moteur_python.py` : verts.
