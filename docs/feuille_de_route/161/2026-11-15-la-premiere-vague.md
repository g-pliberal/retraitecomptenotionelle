# La première vague : vingt fichiers de tests sortis du moteur Python

Action 161, étape 9a, après `2026-11-15-les-temoins-sans-jumeau-et-l-inventaire.md`,
« L'inventaire », vague 1. Aucune règle, aucune donnée, aucun témoin, aucune
page n'a bougé : seuls des tests changent. La suite complète de GitHub était
verte sur `be3d269` ; celles des deux envois suivants tournaient encore.

## Ce qui est fait

Vingt des vingt-deux fichiers de la vague 1 n'importent plus rien du moteur
Python et quittent `FICHIERS` (`test_fichiers_sur_le_moteur_python.py`) :
97 fichiers → 77.

- **Par la façade** (`from facade import …`, tests inchangés) :
  `test_ouverture_des_navigants.py` et `test_ouverture_des_liberaux.py`
  (`departs.departs`, `ouvrir.age_ouverture_droit`), `test_taux_moyens.py`,
  `test_trajectoire.py`, `test_cultes_au_droit.py` (le catalogue et les séries
  seuls), `test_majoration_enfants_agirc_1994_a_1996.py` (la table
  `majorations_enfants_points`), `test_stock_age_legal.py`,
  `test_age_conjoncturel.py`, `test_mortalite_population.py` (le simulateur
  dont les études lisent les paramètres), `test_cnav_exposes.py` (la carrière
  posée à la main), `test_garantie_degressive.py` (la garantie vieillesse ; le
  test s'appelle désormais `test_le_portage_sert_le_bareme_a_soixante_six_ans`),
  `test_cnav_baremes.py` (`liquider.duree_majoree_apres_taux_plein`, ses
  durées posées par `pont.DureesPosees`, qui existait pour ce cas).
- **`test_droits_contrefactuels.py`** : le test de l'âge légal et de la durée
  de chaque état du droit passe par une fixture `du_portage`
  (`Saisies(facade.Simulateur)`). Les quatre autres gardent `Saisies()`, le
  simulateur Python : la carrière longue (`carriere_longue.age_de_depart`)
  n'est pas une méthode que la façade sert.
- **Lus dans le paquet du portage** (`moteur/donnees.json`), et non plus dans
  les tables Python qui le fabriquent : les âges ramenés au mois
  (`test_ages_au_mois.py` ; les tables écrivent 50,33, que le chargeur ramène
  à 50 ans et 4 mois, d'où le paquet plutôt que les CSV), la fiche datée de la
  majoration Agirc-Arrco (`test_agirc_arrco_au_droit.py`), et les fiches dont
  les versions se lisent (`test_versions.py`). Ce dernier éprouve désormais
  les 24 fiches du paquet, et non les six des enfants : la réversion de la
  SNCF y a fait voir que le test ignorait les exceptions ; il les compte
  maintenant, comme `versions.applicable`.
- **Par le pont** : `test_web_saisie.py` demande le coefficient de
  conversion au portage (`conversion.coefficient.esperance_residuelle`), qui
  le rend au dernier âge saisissable et refuse un an plus tard (« diviseur
  nul ») ; les affiliations se lisent sur le simulateur de la façade.
- **`test_destinie.py`** empêche le moteur Python de simuler par
  `empecher_les_jumeaux_du_cout`, sans l'importer. **`test_outillage.py`**
  vérifie le type de la carrière par son nom.
- **`test_proposition_prospective.py`** ne vérifie plus que le contexte
  laisse intact `ScenarioNotionnel.liberal`, une classe du moteur Python qui
  part avec lui ; il garde la liste du coût, et lit l'univers par défaut
  dans les fiches (`noyau.univers.charger`).

## Ce qui reste de la vague 1

- **`test_estimation_du_site.py`** : l'inventaire y comptait deux tests ; en
  vérité tout le fichier confronte le portage au Python (`REGLES`, une table
  de règles Python lue par quatre tests, et `_liquidation_du_python`). Il
  demande `ouvrir.age_annulation_droit` et `periodes_parcourues` à la façade,
  ou un passage au témoin, comme les confrontations des étapes 8o et 8p.
- **`test_affirmations.py`** : la classe `Modele` simule par `Saisies()`.
  Essayé sous `Saisies(facade.Simulateur)` : 364 contrôles passent, 6 tombent
  sur ce que la façade ne sert pas (`courbe_taux`, `convertisseur`,
  `coordonner.regimes_interpenetres`) ; ses imports du moteur
  (`capitalisation`, `Indexation`, `cumuls`, `MinimumVieillesse`, …) restent
  à remplacer.

**Un angle mort de l'inventaire.** Il lit les imports : un test qui simule
par `Saisies()` (`tests/outils_pont.py`) ou par `outils_web.saisies` entre
dans le moteur Python sans y être compté. Les autres tests de
`test_droits_contrefactuels.py` en sont, comme `Modele`.

## Ce qui attend le propriétaire

L'écart `rattachement_pension_smic` (3,45 € par an), inchangé.

**Tests.** `python -m pytest -m rapide` : 5 416 passés, 64 sautés. Les vingt
fichiers et `test_fichiers_sur_le_moteur_python.py` : 668 passés, 2 sautés.
