# Version du 12 novembre 2026 : la mémoire des calculs, d'une course à l'autre

La course de GitHub partait sans mémoire à chaque envoi, et refaisait chaque
calcul lourd du coût. Lancée par un envoi sur `main`, elle reprend désormais
la mémoire des calculs (`.cache/calculs`) de la dernière course verte faite
sur le même modèle (§ 10 ; `actions/cache`). La clé est l'empreinte sous
laquelle `memoire.py` garde lui-même chaque calcul — le modèle, ses données
et le portage, octet par octet, Python et node — et la version de PyYAML :
une source retouchée, et rien ne se reprend. La mémoire de la fabrique et les
réussites gardées des tests, qui font sauter des étapes et des tests, ne se
reprennent pas : la course refait toute la fabrique et joue tous les tests.
Une course lancée à la main, ou par l'index de la DILA, ne reprend ni ne
garde rien : le passage sans mémoire reste à portée. `tests/test_outillage.py`
tient la clé, ce qui se reprend et ce qui se passe quand le modèle bouge
(action 135, à la décision du propriétaire).
