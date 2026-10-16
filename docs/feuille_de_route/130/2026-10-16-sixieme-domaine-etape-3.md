# Le sixième domaine, étape 3 : les fonctions de « compter les durées »

Session 8 de la vague ter du 16 octobre 2026, sans le propriétaire. L'étape 3
du gabarit (`2026-10-14-sixieme-domaine-mesure.md`) : compter, dans les deux
moteurs, les périodes que l'étape 2 a données à la chronologie. Aucune saisie
ne les déclare encore : aucun témoin ne bouge, ni de simulation ni de page.

## Ce qui est fait

- **Les fiches lues par le moteur** : chaque version des quatre fiches porte
  ses `contenu.parametres` — `existe`, le `decompte` (`duree_du_contrat`,
  `jours_dans_l_annee`, `periodes_continues`), les `regimes`, les `motifs`
  qu'elle vise, les jours par trimestre (50, 90, 58), l'âge, les ressources et
  le plafond des sportifs (16, puis 32). `FichesDatees` les charge, et sa
  méthode neuve `version_aux_dates` (`versionAuxDates`) choisit la version au
  début de la période et à la date d'effet, la fiche ne lisant que les dates
  qu'elle déclare. Le motif départage les deux stages : la version des TUC ne
  vise que `stage_d_insertion`.
- **`compter_les_durees`, schéma 6** (`droit/compter.py` et `compter.js`) :
  `trimestres_assimiles` rend, par motif, régime et année, les trimestres de
  `trimestres_de_l_apprentissage` — le contrat compté par D. 373-3
  (`trimestres_du_contrat`), moins ce que l'année a validé dans le régime —
  et de `trimestres_des_periodes` — les jours de l'année par fiche, sans
  report, ou les tranches continues des sportifs après vingt ans, sous
  condition de ressources, jusqu'au plafond. Ils vont à l'assurance du
  régime, donc au prorata et à la durée tous régimes, dans les trimestres
  civils que l'année laisse libres (`plafonds_assimilees`) ; ni aux cotisés,
  ni aux services. Une période commencée sous une version fermée compte du
  1er janvier où une version l'ouvre ; une année qu'un relevé déposé porte
  n'en reçoit aucun ; `avantages_non_contributifs` à faux les retire.
- **Les fiches** passent de `pas_encore_modelisee` à `approchee`, leurs
  écarts déclarés (`approximations`), leur `code` dit.
- **Les tests** (`tests/test_periodes_assimilees.py`, rapide) : D. 373-3 et
  la répartition des jours ; l'apprenti, payé peu puis bien ; l'année pleine ;
  les stages de 2014-2015 ; les TUC avant et après septembre 2023 ; le
  sportif et son plafond ; le schéma ; la concordance des deux moteurs sur
  dix chronologies (`tests/js/comparer-assimilees.mjs`).

## Ce que l'étape laisse aux suivantes

- **Étape 4**, les exemples : les quatre de la circulaire 2016-41 (le
  troisième, du 15 novembre 2014 au 14 février 2016, donne ici quatre
  trimestres en 2015 et un en 2016, à confronter au texte de la circulaire),
  les quatre de la 2024-18.
- **Étape 5**, la saisie, à la session des pages : `avec_periodes_assimilees`
  et `Metier.apprentissage` ; le relevé déposé n'a pas d'attribut
  d'apprentissage, et ses années portées font foi.
- **L'inventaire des avantages non contributifs** garde `etat_modele: absent`
  pour l'apprentissage, et la frontière contributive ses marques : à revoir
  quand la saisie les fera jouer, avec le coût, à l'étape 6.
- Le paquet du site porte les quatre fiches au prochain `regenerer.py` :
  GitHub le refait après l'envoi ; la concordance du portage le lit.

## Ce qui attend le propriétaire

Rien de neuf : la décision de la proposition, à l'étape 7.
