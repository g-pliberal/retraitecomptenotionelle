# Le levier 2, étape 3 : le deuxième lot, dix tests qui déclarent leur date

**Le 11 octobre 2026, la demande** : le lot suivant des 23 tests rapides qui
dépendent encore des présomptions, du plus chargé au moins chargé —
`test_parents_trois_enfants.py` (3), `test_oracle.py` (3),
`test_primes_soumises_a_retenue.py` (2), `test_departs.py` (2) —, la date des
trois exemples officiels relue à la source. Aucun montant ni aucune date
attendus n'ont changé.

- *Sept tiennent au jour de naissance*, que le test racontait sans le
  déclarer : les mères fonctionnaires de `test_parents_trois_enfants.py`, dont
  l'âge des conditions et le mois du départ, juillet ou août 2011, se comptent
  depuis lui ; le sapeur-pompier et l'aide-soignante de
  `test_primes_soumises_a_retenue.py`, « nés à la mi-janvier », dont le
  prorata se compte au mois ; l'aide-soignante de `test_departs.py`, partie en
  février 2022. Le 15 janvier se déclare dans l'outil qui construit la
  carrière : `_carriere`, `_parcours`, `_aide_soignante`. Le test de la
  demande d'avant l'âge légal recopiait la carrière de l'aide-soignante sans
  son jour, et ne tombait qu'une fois l'autre corrigée : il la reprend, avec
  sa demande.
- *Les exemples de la circulaire Cnav n° 22/83*, à 60 et 117 trimestres,
  tiennent aussi au jour, et celui de 145, du même assuré, le déclare avec
  eux. Relue par la recherche de la Cnav (`/api/v1/search/custom`), la
  circulaire dit « Assuré né en mars 1917 », sans le jour ; mais son « 60 +
  (60 x 12,50 %) = 67,5 arrondi à 68 » l'écarte du 1er : cinq trimestres
  postérieurs au soixante-cinquième anniversaire (point 312) jusqu'au 1er
  septembre 1983, quand l'assuré né le 1er mars en compterait six, la
  majoration partant alors de l'anniversaire même (circulaire n° 8/89, point
  12). Sous la présomption décalée, le modèle les comptait : 69 trimestres au
  lieu de 68, 135 au lieu de 132. Le témoin fait naître l'assuré le 15 mars et
  le dit ; les trois cas sont vérifiés du 11 octobre.
- *L'exemple F37311 des enfants nés depuis 2004.* Son énoncé tenait la
  naissance des enfants de la présomption, « à ses trente ans, donc en
  2004 » ; à vingt-sept ans, en 2001, ils rendaient 8 trimestres au lieu de
  4. La fiche, relue, toujours vérifiée le 1er septembre 2026, ne date aucun
  enfant : elle accorde deux trimestres « pour chacun de vos enfants nés
  depuis le 1er janvier 2004, et après votre recrutement ». Le témoin déclare
  deux naissances qui remplissent les deux conditions, mai 2004 et mai 2006,
  la mère recrutée à vingt-deux ans, en 1996.

**Mesuré** : sous les présomptions décalées, 13 tests rapides échouent, un dans
chacun de `test_versements_uniques.py`, `test_services_fonction_publique.py`,
`test_reversion.py`, `test_releve_prolonge.py`, `test_mines.py`,
`test_invalidite.py`, `test_interpenetration.py`,
`test_fonction_publique_etat.py`, `test_etranger.py`, `test_droit.py`,
`test_cultes.py`, `test_cnracl.py` et `test_chomage_complementaires.py` ; sous
celles du vocabulaire, tous passent.
