# Six fichiers et les régimes au bit près : le calendrier, les paramètres, la macro, les prélèvements d'hier, la frontière et le catalogue des régimes confrontés à leur double, vingt fonctions renvoyées au moteur

Action 161, étape 7d, après `2026-11-15-sept-fichiers-de-donnees-au-bit-pres.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

- **24 fonctions de plus confrontées au bit près**, toutes identiques, par
  `tests/test_jumeaux_au_bit.py` : quatre de `calendrier.py` (`decomposer`,
  `formater_age`, `depuis_rang`, `rang`), `avec` des paramètres, sept de
  `macro.py` (prix, salaire moyen, SMIC annuel, les trois revalorisations
  des salaires portés au compte et la colonne en vigueur, sous trois
  scénarios de projection), trois des prélèvements d'hier (`en_vigueur` et
  `valeur` de chacune des 31 séries, `csg_deductible_pension`), la frontière
  chargée, et huit du catalogue des régimes (`periode` et
  `periodes_actives` de chacun des 80 régimes, sous les taux de la fiche et
  sous les taux moyens ; `couvre`, `effet`, `taux_cotisation_salarie`,
  `bornes_assiette_en_pass` de ses 972 périodes ; `morceau_d_annees` ; le
  `taux` des employeurs publics). 81 grilles en tout.
- **Le test sait davantage** : un jour (`Jour`, date en Python, chaîne ISO
  au portage) ; un objet passé en argument (`Objet`) ; des arguments nommés
  reçus en une table (`EnTable`) ; une fonction de module au portage pour
  une méthode en Python (`module_js`) ; une valeur rendue sous deux formes
  (`lire`, `en_liste`), comme la colonne de revalorisation, que le portage
  rend avec sa date d'effet, ou la contribution d'un employeur, tableau au
  portage ; des champs lus en profondeur, et sur une liste.
- **La carte des jumeaux lit une méthode JavaScript dont la signature tient
  sur deux lignes** (`METHODE_SUR_DEUX_LIGNES_JS`, dans `scripts/jumeaux.py`,
  avec son test) : `trimestresValides` de `macro.js` lui échappait, et la
  liste ne déclarait pas `trimestres_valides`. C'était la seule.

## La relecture des lecteurs

Par leurs appels, l'arbre syntaxique de chaque fichier qui reste, hors des
tests et des jumeaux du moteur ; un nom ambigu (`rang`, `periode`,
`grille`, `cotisation`), relu à la main.

- **7 lecteurs corrigés** : `decomposer`, par `cycle_de_vie.py` ; `rang`,
  par `facteurs_depense.py` ; `bareme` des contributions d'équilibre, par
  `integration_complementaires.py` ; `valeur` d'une série des prélèvements
  d'hier, par son propre fichier ; `periode`, par
  `revalorisation_servie.py` ; `taux` des employeurs publics, par
  `mesures_prose.py` ; `effet`, par `morceau_d_annees`, dans son fichier.
- **20 fonctions passent au moteur** : aucun fichier qui reste ne les
  appelle, ou seulement une fonction qui part. `taux_au` de `config.py`,
  que seule `frais_capitalisation` appelle ; `prelevement` des
  contributions ; six de `macro.py` (`_assujetti`,
  `_salaire_validant_du_departement`, `_trimestres_de_la_retenue`,
  `seuil_d_un_trimestre`, que seuls `trimestres_valides` et
  `salaire_au_compte` appellent, et les deux SMIC du forfait, que seul
  `contributions_d_une_carriere` lit), plus `trimestres_valides` ; onze de
  `regimes.py` (`_regle`, `annee_grille`, `annees`, `cotisation`,
  `couverture`, `forfait`, `grille`, `montants`, `regimes`,
  `repere_assiette`, `vivant`) : les classes de cotisation, les salaires
  forfaitaires et les cotisations des cultes ne sont lus, hors du moteur,
  que par la fabrique, qui lit leurs tables.

La liste compte 129 fonctions gardées, dont 82 confrontées (81 ici, et
`en_mois` par `test_moteur.py`), et 109 au moteur.

## Ce qui reste

1. **Les grilles des 47 autres**, avec la même relecture : `contexte.py`
   (10), `bilan.py` (11), `equilibre.py` (21) ; et cinq que leur forme
   rend malaisées : les deux chargeurs `charger_contributions_equilibre` et
   `charger_prelevements_historiques`, dont le portage rend des tables
   brutes, `bareme` des contributions, que `contributions-equilibre.js`
   n'exporte pas, `_en_vigueur` de `regimes.py`, dont les deux côtés n'ont
   pas la même signature (confrontée par `taux`), et `dater_les_taux_moyens`,
   confrontée par les périodes du catalogue aux taux moyens. Pour celles-là,
   une confrontation par leur appelant, déclarée comme telle. Puis la
   colonne `test` rendue obligatoire dans `jumeaux.ecarts_de_la_liste`.
2. Puis le retrait des règles du moteur Python, avec les fonctions
   `au_moteur` ; puis les périodes assimilées du relevé.

**Tests.** `tests/test_jumeaux_au_bit.py` (83, un écart attendu) et
`tests/test_jumeaux.py` (22) ; `python -m pytest -m rapide` : 5 335
passés, un écart attendu.
