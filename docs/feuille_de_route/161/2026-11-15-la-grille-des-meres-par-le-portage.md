# La grille des mères par le portage : `scenarios_meres.py` ne demande plus rien au moteur Python

Action 161, étape 6a, après `2026-11-15-les-fins-de-charge-a-la-facade.md`,
« Ce qui reste », 2 : la première des études de la table de
`2026-11-13-les-decisions-du-proprietaire.md`. Aucune règle, aucune donnée,
aucun témoin, ni le pont ni le portage n'ont bougé. Les suites complètes de
GitHub sur `3c5007c` et `14f43e8` tournaient encore au début de l'étape ; la
dernière connue, sur `04d0bec`, était verte.

## Ce qui est fait

- **Le pont servait déjà tout ce que l'étude lit**, contrairement à ce que
  craignait la note de la question 3 (§ 1) : la façade du pont
  (`pont.facade`) rend la carrière d'un seul statut et la comparaison
  entière, garantie vieillesse, conversion et avantages compris, sous les
  types du Python ; `pont.regle_du_droit` sert `ouvrir.age_taux_plein_droit`
  et `ouvrir.age_ouverture_droit` ; `pont.droit` l'âge de référence
  (`age_reference.age`) ; `pont.indexation` la revalorisation du compte.
- **`scripts/scenarios_meres.py`, `Grille`** : cinq appels au moteur Python
  remplacés par ces demandes, chacune dans une méthode à elle (`_batir`,
  `_simuler`, `_age_du_droit`, `_coefficient`, `age_reference`). La boucle de
  l'âge, à point fixe, est gardée telle quelle : confiée au pilote
  (`pont.ages_de_depart`), elle aurait pu changer un âge. Le simulateur
  Python ne prête plus que ses données : les séries (`salaire_moyen_annuel`)
  et les comptes de la retraite.
- **Le test, écrit d'abord et vu rouge** pour la raison attendue
  (`test_la_grille_passe_par_le_portage_sans_le_moteur_python`) : une
  sous-classe refait les mêmes appels au moteur Python ; puis ses jumeaux du
  coût, son âge de référence et son indexation sont empêchés, et les treize
  lignes de la grille doivent égaler les siennes. Elles les égalent au bit
  près. Cette confrontation part avec le moteur Python. Les douze autres tests
  du fichier éprouvent maintenant le portage.

## Les chiffres, inchangés

Avant et après, au même commit de `main` : la sortie par défaut avec
`--detail --vie-entiere`, identique ligne à ligne, son CSV identique à
l'octet ; la génération 1985, fonctionnaire d'État à 1,2 fois le salaire
moyen, avec `--detail`, identique. Le fichier de tests tourne en 10 s.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide`,
`test_scenarios_meres.py`, `test_fichiers_sur_le_moteur_python.py`.
`test_scenarios_meres.py` reste dans la liste de ce dernier : ses tests de
la bonification lisent la table des majorations du Python, et la
confrontation importe le moteur Python.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. **L'étape suivante** : `cout_avantages.py --par-carriere`, que la note de
   la question 3 (§ 6) décrit — l'âge par le pilote Python, deux
   `scenario_actuel.calculer`, puis `recalculer`. L'option n'a aucun test :
   il vient d'abord, pris sur ce que le moteur Python rend, puis l'option
   passe à `pont.ages_de_depart` et `pont.avantages`, ou à la façade du pont
   comme ici.
2. Puis les deux études non instruites (note de la question 3), la liste des
   fonctions gardées des deux côtés, le retrait, et les périodes assimilées
   du relevé.
