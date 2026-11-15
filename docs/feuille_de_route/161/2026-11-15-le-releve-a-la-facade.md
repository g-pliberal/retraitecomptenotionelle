# Le relevé à la façade : `releve.construire` rendu en données, et ses durées reçues par une règle ; huit tests de plus éprouvent le portage

Deuxième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-regles-de-completer-a-la-facade.md`, « Ce qui reste », 1.
`tests/test_simulateur.py` importe `releve` de la façade ; huit des neuf
fonctions de test marquées `droit.releve` quittent la marque : il en reste 54
dans ce fichier, contre 62. Aucune règle, aucune donnée, aucun témoin n'a
bougé.

## Ce qui est fait

**Le relevé en données.** Le relevé ne passe pas le pont : ses durées et ses
droits sont des objets du moteur. La voie retenue n'est pas une règle
composée par test, mais une entrée de plus de la façade,
`releve.construire` (`ENTREES_DE_LA_FACADE` de `pont.mjs`,
`pont.releve_des_donnees`), qui rend ce que les tests en lisent : les durées
par compte, régime et année ; le plafond de chaque année de la carrière, de
la première à celle de l'effet ; la durée de chaque régime et la durée tous
régimes ; les points, `(code, annee, points, taux)`. La façade les sert sous
les noms du jumeau (`facade.releve.construire(moteur, carriere).durees`,
`.droits.points`, `durees.plafond(compte, annee)`).

**Les durées repassent au portage.** `liquider.duree_du_regime_aligne`
rejoint les règles servies (vingt-six). Elle reçoit les durées : la façade
les transmet par la carrière dont elles viennent (`pont.DureesDuReleve`), et
le portage les refait du relevé de cette carrière, sur le moteur de la
demande (`durees_du_releve`, `argumentDuDroit`).

**Ce qui est refusé** (`NonTransmissible`) : un drapeau de `construire` posé ;
un moteur qui n'est pas celui de la façade ; le plafond de régimes nommés ;
une année hors de la carrière ; des durées passées à une règle avec une autre
carrière, ou sous d'autres paramètres que ceux du moteur ; toute retouche.

**Un test resté sur le moteur Python** : celui de l'exercice 1952, qui lit
aussi les cotisations du relevé et le constructeur du compte, que la façade
ne sert pas ; sa marque dit désormais ces deux raisons. Les huit autres
gardent leur moitié JavaScript, qui fait tourner le portage par node : elle
double à présent la moitié lue par la façade, et partira avec le jumeau.

## Ce qui est mesuré

| `test_simulateur.py` | avant | après |
|---|---:|---:|
| fonctions de test marquées | 62 | 54 |

**Contre le jumeau.** `tests/test_facade_jumeau.py` confronte le relevé d'un
salarié, d'un artisan d'avant 1973 et d'une fonctionnaire mère de trois
enfants, sous les réglages de référence et les conventions du COR : les mêmes
durées, plafonds, durées de régime et tous régimes, les mêmes points, au bit
près ; et deux appels de `duree_du_regime_aligne`.

**Les tests.** Deux tests neufs dans `tests/test_facade.py`, vus rouges avant
le code (la façade n'avait pas de `releve`) : le salarié né en 1955, 156
trimestres de 1978 à 2016 (R. 351-9), aucun en 2017 (R. 351-1), la même
durée alignée ; et ce que la façade refuse. `-m rapide`, `test_facade.py`,
`test_facade_jumeau.py`, `test_pont.py`, `test_oracle.py` : verts.

## Ce qui reste

1. `completer.avpf_retenue` et `commun.ligne_cotisee`, que lit le test de
   l'AVPF de septembre 2023 : `ligne_cotisee` reçoit une ligne de la
   carrière, que la façade ne transmet pas.
2. Les règles dont un argument est un dictionnaire que le portage lit en
   `Map` (`repartir_les_annees`, les points de chef).
3. `liquider.maximum_des_pensions` et `reversion.mois_de_mariage`
   (`test_reversion.py`) : le premier lit aussi deux méthodes de la table des
   réversions que la façade ne sert pas, le second se heurte au nom
   `reversion`, que la façade donne déjà à l'entrée de la réversion.
4. Les cotisations du relevé (`droits.cotisations`) et le constructeur du
   compte, pour le test de l'exercice 1952 et ses voisins marqués
   `Simulateur.constructeur_employeur`.
5. Puis les autres fichiers de tests qui lisent le relevé
   (`test_droit.py`, `test_liquidation.py`, `test_cultes.py`,
   `test_bonifications_emplois.py`…), et les règles du simulateur.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
