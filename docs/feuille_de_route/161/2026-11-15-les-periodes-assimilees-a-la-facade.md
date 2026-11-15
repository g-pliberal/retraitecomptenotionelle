# Les périodes assimilées à la façade : leurs lignes lues sur les durées, deux règles du compte servies, et le filtre d'années du cumul transmis

Quinzième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-trois-fichiers-du-releve-a-la-facade.md`, « Ce qui reste », 1,
premier tiret. Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Ce qui est fait

**Trois fichiers quittent `FICHIERS`**, leurs tests inchangés hors de leurs
imports et de leur confrontation : `test_periodes_assimilees.py` (9 tests),
`test_periodes_assimilees_exemples_officiels.py` (11) et
`test_oracle_periodes_assimilees.py` (9). Chacun garde une confrontation au
jumeau, marquée `sur_le_moteur_python`, comme `test_droit.py` : les trois
entrent dans `RESTES`, un test chacun. Ces tests tournaient déjà sur le
moteur Python ; leur nombre n'augmente pas.

**Les durées de la façade** (`facade.Durees`) servent de plus
`assimilees`, lues du schéma des durées (le texte n'en passe pas, et se
refuse). **Le filtre d'années** de `cumul_plafonne`, une fonction, ne passe
toujours pas le pont : la façade lui soumet les années que les régimes
nommés ont dans le compte, les seules que le Python lui soumet, et passe au
portage la liste de celles qu'il accepte (`compter.cumul_plafonne` de
`pont.mjs`, un argument de plus). Le refus qu'éprouvait
`test_une_etape_ne_sert_que_ce_qu_elle_transmet` est donc levé.

**Deux règles du compte** se servent par deux entrées neuves,
`compter.trimestres_du_contrat` et `compter.jours_par_annee` : la façade
passe leurs dates en jours depuis 1970, comme le portage les lit, et relit
les couples qu'il rend en dictionnaire. `_Module` laisse lire, copiée, une
table de valeurs simples : `compter.FICHES_DES_ASSIMILEES`.

## Ce qui est mesuré

**Les tests.** Deux tests neufs dans `tests/test_facade.py`, vus rouges :
l'exemple 4 de la circulaire Cnav n° 2016-41 (le complément, 1 en 2014 et 1
en 2015 ; l'assurance validée, 1, 4 et 3, et les trimestres cotisés, 0, 3 et
3, une année filtrée) ; l'exemple 3 du contrat et les jours d'une période.
**Contre le jumeau** (`tests/test_facade_jumeau.py`) : le cumul filtré, aux
deux comptes, sur les trois carrières du relevé ; les deux règles, sur cinq
bornes et trois nombres de jours. `-m rapide` (5 150), `test_facade.py`,
`test_facade_jumeau.py`, `test_pont.py`, `test_droit.py`,
`test_liquidation.py`, les trois fichiers de l'étape précédente et ceux-ci :
verts.

## Ce qui reste

1. Les fichiers du relevé que la façade ne sert pas encore :
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
