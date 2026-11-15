# Trois fichiers du relevé à la façade : les emplois classés, les services et les enfants de chaque régime lus sur les durées, trois règles de plus servies

Quatorzième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-etapes-seules-a-la-facade.md`, « Ce qui reste », 2. Aucune
règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

**Trois fichiers quittent `FICHIERS`**, leurs tests inchangés hors de leurs
imports : `test_bonifications_emplois.py` (20 tests),
`test_trimestres_utiles.py` (10) et `test_oracle_familles.py` (15). Aucun
n'entre dans `RESTES` : aucun test n'y garde le moteur Python.

**Les durées de la façade** (`facade.Durees`) servent de plus :
`emplois`, lus du schéma des durées (le texte de la version n'en passe pas,
et se refuse) ; et, demandés au portage par une entrée neuve,
`compter.des_regimes` (`pont.mjs`, lue strictement par
`des_regimes_des_donnees`), `services_effectifs`, `services_liquidables`,
`services_des_emplois`, `majorations_des_emplois`,
`bonifications_des_emplois` et `duree_hors_surcote`. Les trimestres des
enfants rendent `par_regime()`, que le portage écrit avec eux.

**Trois règles du droit de plus** (`pont.REGLES_DE_LA_FACADE`, 39 en tout) :
`liquider.coefficient_surcote_datee`, `ouvrir.depart_parent_trois_enfants`
et `ouvrir.derogation_active`. Les deux dernières rendent un type que le
portage écrit en casse de chameau (`CLASSES_EN_CHAMEAU`) ; `DerogationActive`,
que `ouvrir.py` n'importe que pour l'annoncer, se lit dans
`scenarios.actuel` (`facade._type_rendu`).

## Ce qui est mesuré

**Contre le jumeau.** Six appels de plus dans `APPELS_DES_REGLES`
(`tests/test_facade_jumeau.py`) : la surcote datée du salarié et de la
fonctionnaire, le départ du parent de trois enfants de la fonctionnaire et
du salarié, la dérogation du policier et de la sédentaire ; au bit près,
sous la référence et sous les conventions du COR.

**Les tests.** Un test neuf dans `tests/test_facade.py`, vu rouge : le
policier né en 1960, entré à 19 ans, parti à 52, a vingt trimestres de
bonification (loi du 8 avril 1957), et 132 de services ; une assertion de
plus, la mère de trois enfants porte 24 trimestres et 24 services au régime
général. `-m rapide` (5 147), `test_facade.py`, `test_facade_jumeau.py`,
`test_pont.py`, `test_fichiers_sur_le_moteur_python.py`, `test_droit.py`,
`test_liquidation.py` et les trois fichiers : verts.

## Ce qui reste

1. Les fichiers du relevé que la façade ne sert pas encore, chacun avec ce
   qui lui manque :
   - les périodes assimilées (`test_periodes_assimilees.py`,
     `test_periodes_assimilees_exemples_officiels.py`,
     `test_oracle_periodes_assimilees.py`) : `Durees.assimilees`,
     `compter.FICHES_DES_ASSIMILEES`, `jours_par_annee`,
     `trimestres_du_contrat`, et le filtre d'années de `cumul_plafonne` ;
   - `test_cultes.py` et `test_services_passes.py` : le module
     `droit.cultes` et un `ConstructeurCompte` sous d'autres paramètres ;
   - `test_chomage_complementaires.py`, `test_minima_agricoles.py`,
     `test_sections_liberales.py`, `test_temps_partiel.py`,
     `test_releve_lu.py`, `test_revenu_des_points.py`, `test_referents.py`,
     `test_oracle.py` : des règles hors de la façade
     (`ouvrir.fin_indemnisation`, `releve.points_de_l_annee`,
     `releve.revenu_des_points`, l'échéancier, des tables du scénario).
2. Puis `completer.points_rco_de_chef` ; les 37 tests marqués de
   `test_simulateur.py`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
