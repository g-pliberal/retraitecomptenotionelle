# Le cycle de vie, déjà au portage : l'étape prévue était faite depuis le 12 novembre

Action 161, étape 6c, après `2026-11-15-le-cout-par-carriere-par-le-portage.md`,
qui donnait pour suite « `cycle_de_vie.py`, qui date encore ses cases au
pilote Python ». Aucun code, aucun test, aucune donnée, aucun témoin n'a bougé.

## Ce qui est vérifié

- **L'étape était faite.** `2026-11-12-lot-b-le-cycle-de-vie-date-au-portage.md`
  l'a menée : `scripts/cycle_de_vie.py` date la grille par
  `castypes.cases_de_la_grille`, les balayages et les âges d'équilibre par
  `castypes.ages_de_la_grille`, au portage (`pont.par_le_portage`, vrai hors
  des confrontations). Les lignes que citait la note de la question 3
  (`carriere_de_la_grille`, `age_liquidation_pour`) n'y sont plus.
- **Son test tient** sur `cb9d87f` :
  `test_l_etude_date_ses_cases_au_portage_sans_le_moteur_python`
  (`tests/test_cycle_de_vie_script.py`), jumeaux Python empêchés, vert en 10 s.
- **La méprise** venait de la section « Hors de l'inventaire » de
  `2026-11-12-question-3-les-etudes-a-garder.md`, écrite avant le lot B, que
  la note du coût par carrière a reprise. Les deux études « non instruites »
  de la table des décisions sont les deux autres de cette section, que la
  note du 12 novembre nomme : `part_minimum_contributif.py` et
  `partage_taux_unique.py`.

Ce que l'étude garde du Python, comme le disait déjà la note du 12 novembre :
un `Simulateur` bâti pour ses paramètres et le libellé de chaque hypothèse de
productivité, des données et aucune règle. Il partira avec la liste des
fonctions gardées des deux côtés.

## La suite GitHub

Verte sur `0cf0d2d` (la grille des mères) ; celle de `cb9d87f` tournait
encore à la fin de l'étape.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. **L'étape suivante** : `scripts/part_minimum_contributif.py`, qui bâtit
   et liquide encore ses cas types au moteur Python (`cas.construire` puis
   `simulateur.echeancier`, lignes 242 et 243). Non instruite : porter à
   sorties identiques, sans rien trancher de son contenu.
2. Puis `scripts/partage_taux_unique.py`, qui importe les règles de la fiche
   de paie (`remuneration`, ligne 77) ; la liste des fonctions gardées des
   deux côtés ; le retrait ; les périodes assimilées du relevé.
