# Les témoins sans jumeau, et l'inventaire des fichiers qui restent

Action 161, étape 8q, après
`2026-11-15-les-confrontations-des-independants-sans-python.md`. Aucune règle
du portage, aucune donnée n'a bougé ; seule la page Méthode change.

## Ce qui est fait

- **Les deux tests qui refaisaient les témoins au moteur Python**
  (`test_le_moteur_python_refait_des_temoins_de_chaque_forme`,
  `test_le_moteur_python_refait_chaque_temoin`, dans `test_pont.py`) sont
  retirés, avec leur aide `_au_moteur_python` et leur ligne de
  `tests/conftest.py`. Le portage reste tenu aux témoins par
  `test_le_portage_relu_par_la_table_redonne_les_temoins_a_l_octet` et
  `tests/js/moteur.test.js`.
- **La page Méthode** ne promet plus de jumeau Python identique au bit près :
  la phrase dit maintenant que ce que le moteur rend sur les carrières témoins
  est conservé dans le dépôt, et qu'un seul nombre qui change fait échouer
  les tests. Vraie pendant et après le retrait. Le contrôle
  `le_moteur_du_site_fait_foi` (`test_affirmations.py`), écrit d'abord et vu
  rouge, exige l'absence des deux tests et du mot « jumeau » sur la page ;
  l'affirmation du catalogue est récrite de même.
- **Un défaut de l'étape 8p, corrigé.** Les trois valeurs que la fixture
  `deux_moteurs` fige (`test_independants.py`) sortaient du témoin des
  valeurs à chaque refabrication : `outils_valeurs.tests_qui_figent` ne
  relançait que les tests dont le corps appelle `valeur_figee`, non ceux qui
  passent par une fixture ou une aide. `tests_qui_figent_dans` suit
  désormais les noms de proche en proche ; un test
  (`test_valeurs_figees.py`) le tient, et vérifie que chaque valeur figée
  sous un nom de test est relancée. La refabrication rend le témoin intact.

## L'inventaire des fichiers qui entrent encore dans le moteur Python

Mesuré par les fonctions de `test_fichiers_sur_le_moteur_python.py`
(`les_tests_dans_le_moteur`, à la lecture des imports, sans rien lancer) :
97 fichiers, 1 084 tests qui y entrent. Entre parenthèses, les tests du
fichier qui y entrent, sur ses tests. Ce qu'ils importent le plus :
`Simulateur` (79 fichiers), `Carriere` (40), `droit.liquider` (19),
`droit.ouvrir` (14), `Affiliations` (9), `ConstructeurCompte` (7). La façade
(`tests/facade.py`) sert déjà `Simulateur`, `Carriere` et `reversion` : pour
beaucoup de fichiers, le passage commence par `from facade import …`, puis
ce que la façade ne sert pas encore se voit au rouge.

Ordre proposé, du plus court au plus long, une vague par session ou
davantage :

**Vague 1, deux tests au plus dans le moteur Python** (22 fichiers, 24 tests) :
`test_versions.py` (0/4), `test_affirmations.py` (0/6),
`test_ouverture_des_navigants.py` (1/2), `test_taux_moyens.py` (1/4),
`test_majoration_enfants_agirc_1994_a_1996.py` (1/4),
`test_proposition_prospective.py` (1/5), `test_droits_contrefactuels.py`
(1/5), `test_stock_age_legal.py` (1/6), `test_age_conjoncturel.py` (1/6),
`test_ages_au_mois.py` (1/6), `test_cultes_au_droit.py` (1/6),
`test_destinie.py` (1/9), `test_cnav_exposes.py` (1/10),
`test_trajectoire.py` (1/13), `test_agirc_arrco_au_droit.py` (1/15),
`test_garantie_degressive.py` (1/16), `test_cnav_baremes.py` (1/27),
`test_outillage.py` (1/82), `test_ouverture_des_liberaux.py` (2/8),
`test_mortalite_population.py` (2/12), `test_estimation_du_site.py` (2/18),
`test_web_saisie.py` (2/131).

**Vague 2, de trois à neuf** (40 fichiers, 243 tests) :
`test_ieg.py` (3/3), `test_ircantec_minoration.py` (3/4),
`test_cultes_smic_du_mois.py` (3/4), `test_retour_crpcen_ieg.py` (3/4),
`test_decompte_des_services.py` (3/12), `test_ines.py` (3/12),
`test_regle_de_chacun.py` (4/5), `test_caisses_du_pacifique.py` (4/8),
`test_garantie_par_sexe.py` (4/9), `test_flux_fonction_publique.py` (4/14),
`test_web.py` (4/185), `test_duree_lue_a_soixante_ans.py` (5/5),
`test_services_fonction_publique.py` (5/7), `test_mines.py` (5/7),
`test_coupures_au_mois.py` (5/8), `test_indemnite_csg.py` (5/10),
`test_scenarios_meres.py` (5/13), `test_sncf_ratp.py` (6/6),
`test_coefficients_agirc_1947.py` (6/7), `test_exonerations_agirc_arrco.py`
(6/7), `test_rafp.py` (6/9), `test_cycle_de_vie_script.py` (6/10),
`test_prelevements_historiques.py` (6/43), `test_trimestres_enfants.py`
(7/7), `test_fonction_publique_etat.py` (7/7), `test_cumul_activites.py`
(7/15), `test_ircec_auteurs.py` (8/8), `test_fiche_des_liberaux.py` (8/8),
`test_pcv_sante.py` (8/9), `test_taux_plein_par_categorie.py` (8/10),
`test_minimum_pension_sncf.py` (8/10), `test_contributions_equilibre.py`
(8/11), `test_diviseur_exemples_officiels.py` (8/12), `test_marins.py`
(8/17), `test_interpenetration.py` (9/9), `test_parents_trois_enfants.py`
(9/9), `test_fiche_date_d_entree.py` (9/11),
`test_taux_plein_a_soixante_cinq_ans.py` (9/17), `test_effet_retour.py`
(9/18), `test_univers.py` (9/21).

**Vague 3, de dix à vingt-cinq** (24 fichiers, 343 tests) :
`test_outre_mer.py` (10/10), `test_sections_juridiques.py` (10/15),
`test_avantages.py` (10/30), `test_cnracl.py` (11/11),
`test_cout_age_depart.py` (11/12), `test_solde_fusion.py` (11/13),
`test_chronologie.py` (11/33), `test_facteurs_depense.py` (11/40),
`test_mayotte.py` (12/17), `test_indexation_programme.py` (12/35),
`test_plafond_majoration_enfants.py` (13/13), `test_retablissement.py`
(13/13), `test_cycle_de_vie_references.py` (13/21), `test_etranger.py`
(13/35), `test_estimation_officielle.py` (14/18),
`test_salaire_annuel_moyen.py` (15/15), `test_primes_soumises_a_retenue.py`
(16/18), `test_versements_uniques.py` (17/19),
`test_controle_drees_panorama.py` (17/49), `test_donnees.py` (17/151),
`test_sections_sante.py` (19/46), `test_retraite_progressive.py` (22/23),
`test_revalorisation.py` (22/26), `test_priorite_enfants.py` (23/23).

**Vague 4, plus de vingt-cinq** (9 fichiers, 415 tests) :
`test_independants.py` (26/49), `test_limite_age.py` (31/31), `test_pont.py`
(34/66), `test_cout.py` (38/193), `test_capitalisation.py` (39/52),
`test_remuneration.py` (49/49), `test_grille_large.py` (58/107),
`test_emploi_retraite.py` (67/69), `test_moteur.py` (73/77).

**En dernier, avec le moteur Python lui-même** : `test_facade_jumeau.py`
(25/30), `test_facade.py` (34/137).

`test_affirmations.py` et `test_versions.py` n'ont aucun test qui y entre
directement : c'est une classe ou une aide du fichier (la classe `Modele`,
pour le premier) qui importe une règle. Les fichiers de la vague 4 importent
aussi des modules que la façade ne sert pas (`moteur.capitalisation`,
`moteur.conversion`, `droit.cumul`, `droit.limite_age`) : ils demandent
d'abord d'étendre la façade.

## Ce qui reste avant de retirer les règles Python

1. **Les vagues ci-dessus**, la première d'abord.
2. `memoire.memoriser` garde son paramètre `fichiers_lus`, que plus rien
   n'emploie hors de son test.
3. **L'écart `rattachement_pension_smic`** (3,45 € par an), qui attend la
   décision du propriétaire.

**Tests.** `python -m pytest -m "rapide or site"` : 5 434 passés, 64 sautés.
`test_affirmations.py`, `test_fichiers_sur_le_moteur_python.py`,
`test_valeurs_figees.py`, `test_independants.py` (dispenses) : verts.
