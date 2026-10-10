# Le levier 2, étape 1 : mesurer les tests qui dépendent des présomptions

**Reprise, au 10 octobre 2026.** Fait : la mesure, et les tests du mécanisme
(`test_chronologie.py`, deux de `test_moteur.py`). Reste : 41 tests rapides
dans 20 fichiers, par lots, du plus chargé au moins chargé (liste plus bas) ;
puis, la liste vide, une garde sur GitHub. Commencer par
`PRESOMPTIONS_DECALEES=1 python -m pytest -m rapide --tb=no -rf`, qui en
donne la liste, et `test_emploi_retraite.py`. Les trois exemples officiels de
`test_oracle.py` touchent au scénario 1 : leur date se relit à la source.

**Le 10 octobre 2026, la demande** : l'étape suivante de l'action 135, le
levier 2 du diagnostic du 28 septembre. À l'action 132, le jour de naissance
présumé passé du 1er au 15 avait fait tomber près de 90 tests, qui écrivaient
en dur un montant ou une date ; chacun avait demandé une décision.

- *La mesure.* `PRESOMPTIONS_DECALEES=1` (`tests/conftest.py`) rejoue les
  tests sous d'autres présomptions que celles du vocabulaire : le jour de
  naissance au 1er du mois, l'autre branche de R. 351-37, les enfants à
  vingt-sept ans au lieu de trente, le mariage à trente au lieu de
  vingt-sept. C'est le vocabulaire lui-même qui les dit : un test qui y lit
  sa valeur passe, un test qui l'écrit en dur échoue. Les confrontations au
  portage sont sautées, le portage lisant ses présomptions dans le paquet,
  que la mesure ne décale pas ; les mémoires se taisent, rien de ce qui s'y
  calcule ne se garde. Les tests rapides s'y rejouent en 49 s.
- *Le premier relevé* : 60 tests rapides sur 2 119 échouaient, dont 7
  confrontations au portage, artefacts de la mesure. Les autres sont de deux
  sortes. Les tests du mécanisme, qui vérifient qu'une présomption pose son
  fait, mais en écrivent la valeur : `1965-03-15`, des enfants en
  `1995-03-15`, un mariage en `1987-05-15`. Et les tests qui racontent une
  date sans la déclarer : la mère partie en juillet 2011, le dernier
  employeur qui attend six mois, les exemples officiels de la Cnav.
- *Les deux façons d'y répondre.* Un test du mécanisme lit la valeur au
  vocabulaire (`chronologie.valeur`) : `test_chronologie.py` le fait par
  `_presume` et `_au_jour_presume`, et `test_moteur.py` compare le jour
  présumé au même jour déclaré. Un test qui raconte une date la déclare
  entière : `test_un_parcours_devient_des_faits_dates` déclare le 15 mars
  1965, et le test des enfants sous L. 12 b et L. 12 bis déclare leurs
  naissances, au lieu de les tenir de l'âge que la présomption donne aux
  parents. Aucun montant ni aucune date attendus n'ont changé.

**Mesuré** après ces corrections : 41 tests rapides échouent sous les
présomptions décalées, et tous passent sous celles du vocabulaire.
`test_emploi_retraite.py` 7, `test_simulateur.py` 6,
`test_retraite_progressive.py` 5, `test_parents_trois_enfants.py` 3,
`test_oracle.py` 3, `test_primes_soumises_a_retenue.py` 2, `test_departs.py`
2, et un dans chacun de `test_versements_uniques.py`,
`test_services_fonction_publique.py`, `test_reversion.py`,
`test_releve_prolonge.py`, `test_mines.py`, `test_invalidite.py`,
`test_interpenetration.py`, `test_fonction_publique_etat.py`,
`test_etranger.py`, `test_droit.py`, `test_cultes.py`, `test_cnracl.py` et
`test_chomage_complementaires.py`. Les tests complets et de contrôle n'ont
pas été mesurés : leurs agrégats se recalculent sans mémoire, et leurs
témoins suivent les présomptions par construction, les chiffres exacts du
modèle y vivant.
