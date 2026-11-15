# Les minima agricoles à la façade : « faire vivre », les tables des deux minima et cinq règles servis par le portage

Dix-huitième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-le-chomage-des-complementaires-a-la-facade.md`, « Ce qui
reste », 1 et 2. Aucune règle, aucune donnée, aucun témoin n'a bougé. La
suite complète de GitHub était verte sur `ca030fa` au début de l'étape.

## Ce qui est fait

**`test_minima_agricoles.py` passe à la façade** : 59 de ses 62 tests y
tournent, inchangés hors de leurs imports et de trois aides — la période
lue sur `simulateur.catalogue`, la date d'effet des conjoints écrite en
clair, une `PensionRegime` presque nulle au lieu d'un `SimpleNamespace`.
Trois restent sur le moteur Python, marqués : les deux confrontations « les
deux moteurs », et l'échéancier (`echeancier.Echeancier`). Le fichier reste
dans `FICHIERS` par cet import, et entre dans `RESTES` (3). Aucun fichier
n'en emprunte de fonction.

**« Faire vivre »** (`facade.faire_vivre`, entrée
`revalorisation.faire_vivre`) rend la `Revalorisee` du Python, lue comme le
contenu du journal. Le portage refait le scénario 1 de la carrière : la
façade n'accepte qu'un résultat que son moteur a rendu pour cette carrière,
sous les drapeaux par défaut (`_CALCULES`, les 512 derniers).

**Les tables** `pension_majoree_reference` (`montant`, `regle`),
`complement_differentiel_rco` (`regle`, `smic_net`) et
`minimum_vieillesse.deux_etages` (`DeuxEtages`, en casse de chameau).

**Les règles** `completer.majoration_retraite_proportionnelle`,
`pension_majoree` (ses options passées par leur nom, dans
`MODULES_DU_DROIT` de `pont.mjs`), `points_rco_de_chef` (les droits du
relevé repassent au portage, `pont.DroitsDuReleve`, comme ses durées),
`liquider.valeur_point_fiche` ; un `EligibleAgricole` passe en argument.
**`commun.periode_de_liquidation`** rend la période du catalogue par son
rang. Une constante d'un module du droit (`completer.RCO`) se lit telle
quelle.

## Ce qui est mesuré

Six tests neufs dans `tests/test_facade.py`, quatre confrontations dans
`tests/test_facade_jumeau.py` (« faire vivre » de cinq carrières à
plusieurs échéances, les tables, les règles, la période). `-m rapide`
(5 172), `test_facade.py`, `test_facade_jumeau.py`,
`test_fichiers_sur_le_moteur_python.py`, le fichier, `test_pont.py` et les
confrontations légères : verts.

## Ce qui reste

1. `test_sections_liberales.py`, `test_temps_partiel.py`,
   `test_releve_lu.py`, `test_revenu_des_points.py`, `test_referents.py`,
   `test_oracle.py` : `releve.points_de_l_annee`,
   `releve.revenu_des_points`, l'échéancier, des tables du scénario.
2. « Faire vivre » servi ouvre la voie aux fichiers qui l'appellent :
   `test_departs.py`, `test_invalidite.py`, `test_pension_maximale.py`,
   `test_majoration_*`, `test_pension_minimum_avant_1983.py`, et le test
   marqué de `test_liquidation.py`.
3. Les 37 tests marqués de `test_simulateur.py`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance ; son verdict sur `83971c1` n'était pas
rendu au commit.
