# Le levier 2, étape 2 : le premier lot, dix-huit tests qui déclarent leur date

**Le 10 octobre 2026, la demande** : l'étape suivante du levier 2, corriger
un lot des 41 tests rapides qui dépendent des présomptions —
`test_emploi_retraite.py` (7), `test_simulateur.py` (6),
`test_retraite_progressive.py` (5) —, sans changer aucun montant ni aucune
date attendus. Les trois exemples officiels de `test_oracle.py` restent :
ils touchent au scénario 1, et leur date se relit à la source.

- *Une seule des deux façons a servi.* Aucun des dix-huit ne vérifie le
  mécanisme d'une présomption : tous racontent une date, et la déclarent
  désormais. Dix-sept tiennent au jour de naissance. Leurs assurés naissent
  en janvier sans dire le jour : présumé le 15, il fait compter les âges de
  février ; le 1er, de janvier (l'autre branche de R. 351-37), et chaque date
  racontée recule d'un mois — la pension de mai 2022 part en avril, le
  dernier employeur attend jusqu'à fin septembre. Le 15 se déclare là où la
  carrière se construit : `BASE` (« 1960-01-15 »), `_carriere` et `_cumul`
  de `test_emploi_retraite.py` ; `_carriere` et la saisie de
  `test_retraite_progressive.py` ; dans `test_simulateur.py`, la fixture du
  salarié moyen, l'agent SNCF à cheval sur 1992, la fonctionnaire du
  scénario 6, le cadre de la tranche C et l'exploitant agricole. Les
  commentaires qui disaient « le 15, faute de jour dit » disent le jour
  déclaré.
- *Les enfants de la fonctionnaire*
  (`test_les_trimestres_pour_enfants_suivent_la_date_le_sexe_et_le_regime`).
  La bonification se lit à l'année de naissance de l'enfant, que le test
  tenait de la présomption, aux trente ans de la mère ; à vingt-sept, les
  enfants de la fonctionnaire née en 1985 naissent avant son recrutement, et
  L. 12 bis ne lui accorde rien. Le test déclare leurs naissances, 1990 et
  2015, et la carrière sans enfant les retire.
- *Un défaut du modèle, que la mesure a levé.* Sous le 1er du mois,
  `test_le_fonctionnaire_liquide_son_traitement_a_temps_plein` échouait pour
  une autre raison qu'une date racontée. Le fonctionnaire en retraite
  progressive qui part un 1er janvier liquide un traitement de référence à
  temps partiel : née le 1er janvier 1963, à 70 % depuis ses 61 ans, partie
  au 1er janvier 2027, l'assurée liquide 29 631,12 € de traitement au lieu de
  42 330,16 €, et sa pension de l'État tombe à 19 347 €, contre 28 330 € sans
  retraite progressive. L'année du départ n'a pas de ligne :
  `salaire_de_reference` (`droit/liquider.py`, comme son portage
  `moteur/js/droit/liquider.js`) passe par la branche de la pension différée,
  qui rend le revenu de la dernière année sans le rapporter à la quotité. Né
  un 15 décembre, l'assuré qui part à un âge rond part aussi un 1er janvier :
  le défaut se voit sous les présomptions du vocabulaire. Le test déclare le
  15 janvier, comme les autres ; la correction, qui change des montants et le
  portage, revient au modèle, et n'est pas faite ici.

**Mesuré** : sous les présomptions décalées, 23 tests rapides échouent, et
aucun des trois fichiers du lot ; sous celles du vocabulaire, les 2 119
passent. Restent `test_parents_trois_enfants.py` 3, `test_oracle.py` 3,
`test_primes_soumises_a_retenue.py` 2, `test_departs.py` 2, et un dans
chacun de `test_versements_uniques.py`, `test_services_fonction_publique.py`,
`test_reversion.py`, `test_releve_prolonge.py`, `test_mines.py`,
`test_invalidite.py`, `test_interpenetration.py`,
`test_fonction_publique_etat.py`, `test_etranger.py`, `test_droit.py`,
`test_cultes.py`, `test_cnracl.py` et `test_chomage_complementaires.py`.
