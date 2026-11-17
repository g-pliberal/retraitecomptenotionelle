# Ce que la carrière compte, au portage : 63 tests dépendent encore de la carrière des règles, au lieu de 125

Action 161, morceau 3 du plan de `2026-11-17-la-facade-transmet-la-carriere-nue.md`
(les tests qui lisent une propriété de règle), ses deux plus gros fichiers,
mené la nuit du 16 au 17 novembre 2026, sur la consigne du propriétaire
d'avancer ce qui ne demande pas son avis. Aucun fichier de `moteur/` n'est
touché, aucune règle ni donnée : aucun résultat, aucun témoin ne peut bouger.

- **D'où venaient les 62 échecs.** Sous la carrière nue, `test_simulateur.py`
  lisait sur la carrière `trimestres_retenus` (27), `prolongee` (6),
  `annee_de_cessation_agricole` (4), `trimestres_actuels` (2) et
  `trimestres_cumules` (1) ; `test_priorite_enfants.py`, `date_entree` (22,
  dans son aide `_regimes`).
- **Quatre entrées de la façade** (`tests/facade.py`), servies par le portage
  (`pont.mjs`, `pont.LECTURES_DE_LA_FACADE`) :
  `carriere.trimestres_retenus` (ceux de chaque ligne, dans leur ordre),
  `carriere.trimestres_cumules` (sur des lignes données par leur rang ;
  `trimestres_actuels`, le cumul de toutes, s'en déduit dans la façade),
  `carriere.annee_de_cessation_agricole` et `carriere.date_entree`. Une
  entrée par carrière et non par ligne : un appel au pont, pas quarante.
- **Les tests.** `test_facade.py`,
  `test_ce_que_la_carriere_compte_se_demande_au_portage`, aux valeurs posées
  à la main (né en mars 1962, entré en mars 1983, parti en avril 2024 : 3,
  puis quarante fois 4, puis 1, soit 164 ; 167 pour l'exploitant agricole,
  qui compte les quatre trimestres de l'année où il cesse), vu rouge puis
  vert ; `test_facade_jumeau.py`,
  `test_le_jumeau_compte_la_carriere_comme_la_facade_la_lit`, qui confronte
  les quatre lectures à celles du jumeau sur quatre carrières, recopiées sous
  la classe des règles : il ne dépend pas de la bascule.
- **Les deux fichiers.** `test_simulateur.py` passe par ces entrées, par
  `facade.prolongee` (déjà servie) pour les six tests de la prolongation, et
  par une aide, `_trimestres_cotises`, pour les huit sommes des trimestres
  cotisés ; `test_priorite_enfants.py` lit la date d'entrée de chaque statut
  au portage, une fois par statut. Aucune valeur attendue ne change. Les
  carrières que `test_simulateur.py` bâtit lui-même sous la classe des règles
  (`Carriere(**naissance, lignes=…)`, autour de la ligne 5640) n'en dépendent
  pas : elles partiront avec les règles.
- **Les vérifications.** Les deux fichiers : verts (337 et 43), et verts sous
  la carrière nue. `python -m pytest -m rapide` : vert (5 697).
- **Mesuré de nouveau** sous la carrière nue, par la recette de la note du
  matin : 63 échecs, au lieu de 125, dans 23 fichiers : six au plus
  par fichier (`test_invalidite.py`, `test_chronologie.py`), dont les trois
  du jumeau et les deux qui épinglent la classe des règles.

**Ce qui reste** : la traîne du morceau 3, d'un à six tests par fichier,
dont les lectures que la note des saisies relève (`date_de_service`,
`duree_de_service`, `reversion_agricole`, `retraite_progressive`,
`radiation_pour_invalidite`) ; les quatre entrées d'ici en servent une part.
Puis la bascule.
