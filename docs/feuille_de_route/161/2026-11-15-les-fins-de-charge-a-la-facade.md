# Les fins de charge à la façade : la date où chaque enfant cesse d'être à charge, et les parts de la majoration à une date

Action 161, étape 5l, après `2026-11-15-les-departs-a-la-facade.md`,
« Ce qui reste », 2. Aucune règle, aucune donnée du dépôt, aucun témoin n'a
bougé. La suite complète de GitHub était verte sur `a08f52e` ; celles de
`04d0bec` et de `3c5007c` tournaient encore au début de l'étape, celle de
`ebe8d2b` ayant été annulée par la suivante.

## Ce qui est fait

- **Trois règles de plus servies par le portage** (`pont.REGLES_DE_LA_FACADE`) :
  `completer.fins_de_charge`, `commun.parts_de_la_majoration` et
  `commun.fusionner_les_charges`, chacune confrontée au jumeau
  (`test_facade_jumeau.py`, sept appels : deux âges de fin de charge, les
  parts à la date d'effet, à une date ultérieure et sans les enfants à
  charge, deux réunions d'étapes).
- **Ce que la façade transmet de plus** : un `AvantageApplique`
  (`pont.TYPES_DE_LA_FACADE`), seul ou en liste, champ à champ ; une suite de
  valeurs simples à toute profondeur, comme les étapes d'une majoration à
  charge (`_suite_simple`, `_en_listes` de `tests/facade.py`).
- **`fusionner_les_charges`** annonce le type qu'elle rend, celui du champ
  `a_charge` de l'avantage : la façade lit ainsi la réponse du portage.
- **Les deux noms qui diffèrent** : le troisième argument de
  `parts_de_la_majoration` s'appelle `a_charge` en Python et `avecACharge`
  dans le portage, déclaré dans `test_facade.py`.
- **`test_majoration_enfants_a_charge.py`** (3 → 1 marqué) : la fin de charge
  se lit sur une vraie carrière que la saisie bâtit (quatre naissances,
  datées comme l'ancienne carrière de fortune) ; les parts et la réunion des
  étapes passent par la façade, avec leurs valeurs. Reste la confrontation
  des deux moteurs.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide`,
`test_majoration_enfants_a_charge.py`, `test_facade.py`,
`test_facade_jumeau.py`, `test_fichiers_sur_le_moteur_python.py`.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. Les tests encore marqués `sur_le_moteur_python` sont tous des
   confrontations des deux moteurs, le solveur `niveau_pour_pension`
   (`test_simulateur.py`) et les quinze de `test_oracle.py` : le point 2 de
   la note précédente est clos.
2. L'étape suivante ouvre les études de la table de
   `2026-11-13-les-decisions-du-proprietaire.md` : d'abord
   `scenarios_meres.py`, puis `cout_avantages.py --par-carriere`, puis deux
   non instruites (note de la question 3).
