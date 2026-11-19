# La règle des mois du titulaire d'une pension militaire, nommée par la version qui vaut

Le 19 novembre 2026, sur l'accord du propriétaire (« Cumul emploi retraite :
oui sur tout »), le moteur nomme la règle des mois d'activité du titulaire
d'une pension militaire par la version de `droits_apres_la_premiere_pension`
qui vaut pour sa première pension. Il la nommait par la seule date du droit,
`loi_2014` avant 2023 et `loi_2023` ensuite : l'écart que l'étape 2 du cumul
avait trouvé, gardé et déclaré (`2026-11-19-etape-2-du-cumul.md`, « La
trouvaille »). Aucun droit ne bouge, aucune pension : seul ce nom.

## Ce qui change

- **Une première pension d'avant 2015**, pour un mois d'avant 2023 : la règle
  est `sans_regle_generale`, et non plus `loi_2014`. L'article L. 161-22-1 A
  est « applicable aux assurés dont la première pension prend effet à compter
  du 1er janvier 2015 » (loi n° 2014-40, article 19, VIII,
  `JORFARTI000028493657`).
- **Une première pension de 2027** : la règle est `lfss_2026`, et non plus
  `loi_2023`. La rédaction de 2026 « s'applique aux assurés qui entrent en
  jouissance de leur première pension de vieillesse de base à compter du
  1er janvier 2027 » (loi n° 2025-1403, article 102, XI).
- **Le motif reste `pension_militaire`** sous les quatre versions : L. 84 du
  code des pensions civiles et militaires de retraite retire à ces
  titulaires les articles du cumul (`LEGIARTI000028498621`). `motif`, dans
  `moteur/js/droit/seconde.js`, rend l'identifiant de la version lue aux deux
  dates, comme pour tout autre assuré ; il n'a plus de branche à lui pour le
  nom. Le moteur n'a pas de jumeau Python pour cette règle.
- **La fiche** perd l'approximation qui déclarait l'écart, et son historique
  dit la correction.

Les textes sont ceux que l'étape 2 a relus le même jour dans les index de la
DILA ; aucun n'a été relu une seconde fois.

## Ce qui est vérifié

- `tests/js/droits-apres-la-premiere-pension.test.js`, un essai de plus, vu
  rouge (`loi_2014` rendu, `sans_regle_generale` attendu) puis vert : cinq
  cas, dont les deux bornes, décembre 2014 et janvier 2027, et le mois de
  janvier 2023. Ses valeurs sont celles des deux lois citées.
- Les témoins refaits : un seul bouge sur 934, `cumul_militaire_2027`, par
  ce seul nom, `loi_2023` devenu `lfss_2026` ; aucune pension dans aucun des
  six scénarios, aucun des 86 rendus de page. Aucun témoin ne porte un
  militaire d'avant 2015 qui reprend une activité avant 2023 : ce cas-là
  n'est tenu que par l'essai.
- `python -m pytest -m rapide` (5 592 passés) ; les tests de la zone, dont
  `test_emploi_retraite.py`, `test_oracle.py`, `test_carte.py` et
  `test_cliquets_du_droit_date.py` ; les 268 essais de `tests/js/`. La suite
  complète est à GitHub.

## Ce qui reste

- Le cas de janvier 2023 pour une première pension d'avant 2015 suit la
  borne de la fiche, `loi_2023` dès le 1er janvier 2023. Cette borne est la
  question de lecture que l'étape 2 a relevée (XII de l'article 26 de la loi
  n° 2023-270). Le propriétaire a approuvé sa relecture, qui se fait par une
  session qui n'a pas vu celle-ci ; si la borne bouge, cet essai la suit, et
  la correction attend son accord, puisqu'elle déplace des résultats.

## Ce que la correction a coûté

Une heure environ, à la suite de l'étape 2, dans la même session ; un commit ;
quatre fichiers écrits à la main, et les témoins refaits.
