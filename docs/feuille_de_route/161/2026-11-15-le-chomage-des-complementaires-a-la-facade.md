# Le chômage des complémentaires à la façade : la coupure de l'indemnisation servie par le portage, et le bâtisseur d'un relevé

Dix-septième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-cultes-et-les-services-passes-a-la-facade.md`, « Ce qui
reste », 1, premier fichier. Aucune règle, aucune donnée, aucun témoin n'a
bougé.

## Ce qui est fait

**`test_chomage_complementaires.py` quitte `FICHIERS`**, ses 18 tests
inchangés hors de ses imports et de sa fixture. Aucun autre fichier n'en
emprunte de fonction (`from test_chomage_complementaires import` : rien).

**Deux règles d'`ouvrir`** se servent par la façade : `fin_indemnisation`,
qui rend une `DateMois`, et `indemnisation_bornee`, qui rend une
`Carriere`. Une règle qui rend la carrière qu'elle reçoit, intacte, la rend
elle-même, comme le jumeau (`_demander_la_regle`) : le pont n'en transmet
qu'une copie, et un test lit `is`.

**`Carriere.depuis_releve`** se sert par le portage
(`carriere.depuis_releve`), comme les deux autres bâtisseurs : la façade
l'héritait du Python.

## Ce qui est mesuré

Deux tests neufs dans `tests/test_facade.py` : la coupure au 1er février
2020 pour un cadre né le 15 janvier 1958 qui a la durée, à 65 ans pour un
assuré de 1950 qui ne l'a pas, la carrière bornée et la carrière rendue
elle-même ; le bâtisseur du relevé. Contre le jumeau : les deux règles, sur
six appels, la carrière bornée comparée champ par champ ; le bâtisseur du
relevé. `-m rapide` (5 160), `test_facade.py`, `test_facade_jumeau.py`,
`test_pont.py`, `test_fichiers_sur_le_moteur_python.py`, le fichier, et les
quatre fichiers d'oracle réparés juste avant (43) : verts.

## Ce qui reste

1. Les fichiers du relevé que la façade ne sert pas encore :
   `test_minima_agricoles.py`, `test_sections_liberales.py`,
   `test_temps_partiel.py`, `test_releve_lu.py`,
   `test_revenu_des_points.py`, `test_referents.py`, `test_oracle.py` :
   des règles hors de la façade (`releve.points_de_l_annee`,
   `releve.revenu_des_points`, l'échéancier, des tables du scénario).
   `test_cultes_au_droit.py` et `test_cultes_smic_du_mois.py` trouvent déjà
   le module des cultes.
2. Puis `completer.points_rco_de_chef` ; les 37 tests marqués de
   `test_simulateur.py`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance ; son verdict sur la réparation des
trois fichiers d'oracle n'était pas rendu au commit.
