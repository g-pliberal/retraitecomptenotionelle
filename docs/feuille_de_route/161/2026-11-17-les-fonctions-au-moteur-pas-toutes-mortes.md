# Les fonctions `au_moteur` ne sont pas toutes mortes : le relevé, et les consignes de `src/`

Action 161, nettoyage après la suppression des règles Python
(`2026-11-17-la-suppression-des-regles-python.md`), mené le 17 novembre
2026, arrêté à la demande du propriétaire (quota). Aucun code ne change.

## Fait

- **Les consignes de `src/`** (`src/CLAUDE.md`) ne parlent plus des jumeaux
  du moteur : le moteur d'une carrière n'a qu'un exemplaire, en JavaScript ;
  restent les fonctions écrites des deux côtés que déclare
  `scripts/jumeaux_gardees.yaml`, confrontées par
  `tests/test_jumeaux_au_bit.py`. La liste de contrôle perd l'étape du
  jumeau Python (la confrontation `test_pont.py -k refait` n'existe plus).

## Le relevé des 121 fonctions `au_moteur`

La note précédente les disait mortes. Un relevé par l'arbre syntaxique de
tous les fichiers Python suivis (noms, attributs, imports, chaînes) dit
autre chose. `ecarts_de_la_liste` ne vérifie jamais une entrée `au_moteur` :
la classification date du 15 novembre, avant la façade et la carrière nue.

1. **Sans aucun lecteur, hors de leur définition** (à supprimer d'abord,
   avec leur entrée, après grep des fiches qui les citent en prose) :
   `calendrier.trimestres_civils`,
   `contributions_equilibre.part_salariale_annualisee`,
   `DonneesMacro.productivite_nominale`, `.salaire_au_compte` (citée dans
   `trimestres_avant_1972.yaml`), `.smic_horaire_de` (citée dans
   `assiette_minimale_independants.yaml`), `.smic_horaire_en_vigueur`,
   `AssietteTva.variation_prix`, sans doute
   `CaracteristiquesRetraites.part_minimum_pension` (ses autres mentions
   sont des clés de données).
2. **Lues seulement par des tests** (une quarantaine) : config
   (`frais_capitalisation`, `sous_regime_frais`, `sous_regime_taux`,
   `taux_capitalisation_applique`, `taux_retraite_propose`), `Contexte.pour`
   et `.inventaire_avantages`, `contributions_d_une_carriere`, les
   accesseurs de `depenses.py` et `equilibre.py`, `fiabilite_sur` et
   `fiabilite_minimale_sur`, `repartition_normale`, tout
   `prelevements_historiques.py` sauf `famille_de_la_fiche`,
   `primes.part_comptee`, `.taux_annuel`, `.taux_au`, et dans `regimes.py`
   `ajustement_total`, `assiette_minimale`, `bornes_assiette_en_euros`,
   `liquide`, `periode_a_l_effet`, `revenu_retenu`. Chaque test se relit :
   il part s'il ne fait que confronter le Python mort, ou passe au portage
   par le pont, aux mêmes valeurs attendues.
3. **Encore lues par du code vivant** : `remuneration.py` (lu par
   `construire_donnees.py`) appelle `taux_capitalisation_volontaire_applique`,
   `famille_de_la_fiche`, `plafond_de_cotisations`, `bornes_en_euros`,
   `prise_en_charge`, `taux_du_cotisant`, `taux_supplementaires`,
   `annee_grille`, `contribution_de_solidarite` ; `chronologie.py` et
   `types_du_pont/carriere.py`, `plus_mois` et `origine_des_ages` ;
   `contributions_equilibre.py`, `fraction_annee`, `smic_horaire_du_forfait`,
   `repere_assiette` ; `tables_du_droit.py`, `coefficient_smic`,
   `points_garantis`, `versions.applicable` ; `mesures_prose.py`,
   `Contexte.restitution`. Celles-là ne partent pas : elles se déclarent
   `gardees`, avec lecteur et test de confrontation, ou leur lecteur passe au
   pont. Les noms courants (`bilan`, `solde`, `grille`, `annee`,
   `couverture`, `fiabilite`…) se confondent avec d'autres attributs : à
   trancher un par un.

Pour départager 2 et 3 à l'exécution, un traceur `sys.monitoring` (événement
`PY_START` limité aux 125 objets de code visés, appelant relevé) sous
`regenerer.py` dit lesquelles la fabrique exécute ; la course a été
interrompue avant la fin.

## Ce qui reste

1. Supprimer le groupe 1, puis relire le groupe 2 test par test.
2. Faire vérifier `au_moteur` par `ecarts_de_la_liste` (aucun lecteur hors
   des tests), le test d'abord, puis reclasser le groupe 3.
3. `moteur/CLAUDE.md` (lignes 8 à 21) et `docs/architecture.md` (principe 4
   et § 7.1) parlent encore des jumeaux au présent.
