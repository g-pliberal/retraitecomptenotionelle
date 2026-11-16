# Le salaire moyen au pont : trois scripts ne l'exécutent plus en Python

Action 161, point 1 de « Ce qui reste » de
`2026-11-16-le-tri-des-scripts-et-des-modules.md`. Aucune règle, aucune
donnée, aucun témoin n'a bougé.

`pont.salaires_moyens(annees, parametres)` demande au portage
(`carriere.salaire_moyen_annuel` de `moteur/js/carriere.js`) le salaire moyen
de toutes les années d'un lot, en une demande. `scenarios_meres`,
`estimation_officielle` et `fetch/destinie_2.py` le lui demandent au lieu
d'importer `carriere.salaire_moyen_annuel` ; les deux premiers gardent ce
qu'ils ont lu d'un appel à l'autre, `destinie_2` demande d'un coup les années
de toutes les périodes des cas (`salaires_des_cas`) et ne bâtit plus de
`Simulateur`.

**Vérifié.** Les requêtes et les tables que `destinie_2` écrit pour R sont
identiques à l'octet avant et après ; l'aide par enfant de `scenarios_meres`
aussi, sur quatre années. La sonde ne relève plus, dans `scenarios_meres`,
que l'accès aux types du résultat (`Carriere`, `Journal`, `Comparaison`,
`ResultatNotionnel`, `GarantieVieillesse`).

**Tests.** `tests/test_pont.py` : le salaire moyen par lot (40 897 € en 2024,
39 845,61 € en 2023, de `salaire_moyen_niveau.csv`) et aucun des trois
scripts n'importe plus `salaire_moyen_annuel`, vus rouges puis verts ;
`test_estimation_officielle.py` lit le salaire moyen au pont.
`python -m pytest -m rapide` et les confrontations légères : verts.

**Reste** : le point 2, la grille large.
