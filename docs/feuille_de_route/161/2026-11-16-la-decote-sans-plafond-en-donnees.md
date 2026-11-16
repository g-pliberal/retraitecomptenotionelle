# La décote sans plafond en données : `test_cout_age_depart.py` quitte le moteur Python

Action 161, étape 9o, après `2026-11-16-la-grille-large-a-la-facade.md`.
Aucune règle du droit, aucune donnée de calcul, aucune page n'a bougé.
`FICHIERS` (`test_fichiers_sur_le_moteur_python.py`) perd
`test_cout_age_depart.py` : il ne reste que `test_facade.py` et
`test_facade_jumeau.py`, qui partent avec le moteur Python.

## Ce qui est fait

- **L'espion de la décote cède la place à un paquet sans plafond.** Le test
  `test_le_plafond_de_decote_ne_mord_sur_aucune_liquidation_ouverte`
  remplaçait `liquider.trimestres_de_decote` du moteur Python pour voir si
  le plafond de vingt trimestres mordait. Il liquide désormais chaque
  carrière du balayage (13 cas types, générations 1950, 1970, 1990, départs
  de 58 à 68 ans au trimestre) par le portage, en un lot (`pont.droit`,
  `scenario_actuel.calculer`), une fois sur le paquet du dépôt, une fois sur
  une copie dont chaque `decote_trimestres_maximum` est mis à `null`, et
  refuse qu'une liquidation ouverte en soit changée : 1 081 ouvertes, aucune
  changée.
- **La comparaison n'est pas aveugle** : le même balayage, sur une copie
  plafonnée à quatre trimestres, voit 160 liquidations ouvertes changer ; le
  test l'exige.
- La variante s'écrit en données, dans le test seul : ni le modèle ni le
  paquet du dépôt ne changent. Le test prend environ 25 secondes.

## Ce qui reste

Le retrait du moteur Python lui-même. Plus aucun fichier de tests ne
l'exécute directement, hors `test_facade.py` et `test_facade_jumeau.py`.
Mais une trentaine de scripts (`grille_large.py`, `cout_avantages.py`,
`estimation_officielle.py`…) et plusieurs modules de `src/` (`memoire.py`,
`avantages.py`, `facteurs_depense.py`, `contexte.py`, `controle_eacr.py`,
`controle_ancetre.py`, `leviers.py`) bâtissent encore `Simulateur(...)` :
certains n'en lisent que les données (`macro`), d'autres calculent avec. Il
faut d'abord les classer, puis faire passer au pont ceux qui calculent, avant
de couper les règles d'un bloc (note des décisions du propriétaire, ligne
« le retrait »).

**Tests.** `python -m pytest -m rapide` : 5 385 passés, 64 sautés.
`test_cout_age_depart.py` (12) et
`test_fichiers_sur_le_moteur_python.py` : verts.
