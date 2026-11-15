# L'oracle à la façade : rien à servir, quinze garde-fous du jumeau Python marqués

Vingt-quatrième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-trois-fichiers-de-la-carriere-a-la-facade.md`, « Ce qui
reste », 1 : mesurer ce qui manque à `test_oracle.py` et servir
l'échéancier. Aucune règle, aucune donnée, aucun témoin, aucune ligne de la
façade ni du pont n'a bougé : seuls les imports et quinze marques de
`test_oracle.py`, et le compte de `test_fichiers_sur_le_moteur_python.py`.
La suite complète de GitHub était verte sur `81eb574` ; celle de `8d38a63`
tournait à la fin de l'étape.

## Ce qui est mesuré

**L'échéancier n'avait pas à être servi.** La note précédente lisait dans les
imports de `test_oracle.py` que le fichier empruntait l'échéancier, `departs`,
`invalidite`, `ScenarioActuel` et trois tables du scénario. Lus usage par
usage (un parcours de l'arbre syntaxique, chaque nom hors des appels de
`_sans_les_jumeaux` et `_mesures_sans_les_jumeaux`), ces noms ne servent qu'à
une chose : être empêchés de calculer. Toutes les mesures du fichier passent
déjà par le pont (`pont.droit`, et `droit_et_refait`, qui y confronte le
jumeau tant qu'il reste), échéancier compris
(`echeancier.parcourir.reversion`, `echeancier.parcourir.au_depart.cumul`).

Hors de ces garde-fous, le fichier n'empruntait au moteur Python que
`Carriere`, comme constructeur d'une carrière posée à la main ; 29 tests y
entraient par lui, au travers de leurs fixtures (`nos_calculs`,
`nos_points_*`, `nos_pensions_alignees`).

## Ce qui est fait

- **`Carriere` vient de la façade**, avec la fixture `entrees_du_test` ; les
  45 tests sans marque n'entrent plus dans le moteur Python.
- **Les quinze tests « sans les jumeaux »** importent eux-mêmes les jumeaux
  qu'ils interdisent, et portent la marque `sur_le_moteur_python` : ce sont
  des garde-fous du jumeau, qui partiront avec lui au retrait. `RESTES` les
  compte (15).
- **`test_oracle.py` reste dans `FICHIERS`** : la liste lit les imports
  partout dans le fichier, ceux des tests marqués compris. Il la quittera
  avec ses garde-fous. Les cacher derrière la façade (`JUMEAUX`) l'en aurait
  sorti sans rien changer : la session ne l'a pas fait.

Le test vu rouge : `RESTES` portant `test_oracle.py` à 15, avant que le
fichier ne bascule.

`test_oracle.py` (277 cas), `test_fichiers_sur_le_moteur_python.py` et
`python -m pytest -m rapide` : verts.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.

## Ce qui attend le propriétaire

Les quinze garde-fous pourraient aussi être retirés dès maintenant, puisque
le portage ne peut appeler le jumeau qu'au travers de `droit_et_refait`, que
le pont ne voit pas. La session ne retire pas de test sans son accord : ils
restent, marqués, jusqu'au retrait.

## Ce qui reste

1. Les quatre autres fichiers d'oracle de `FICHIERS` :
   `test_oracle_carriere_longue_fonction_publique.py`,
   `test_oracle_categorie_active.py`, `test_oracle_points_enfants_arrco.py`,
   `test_oracle_salaire_annuel_moyen.py`. Ils n'empruntent que `Simulateur`,
   `Carriere`, `ouvrir` et `liquider`, que la façade sert déjà, et n'ont aucun
   garde-fou du jumeau : une étape devrait les passer tous quatre, en
   vérifiant d'abord que chaque règle qu'ils appellent est dans
   `pont.REGLES_DE_LA_FACADE`.
2. « Faire vivre » servi ouvre la voie aux fichiers qui l'appellent :
   `test_departs.py`, `test_invalidite.py`, `test_pension_maximale.py`,
   `test_majoration_*`, `test_pension_minimum_avant_1983.py`, et le test
   marqué de `test_liquidation.py`. Mesurer d'abord, usage par usage comme
   ici, ce que chacun emprunte vraiment : un import ne dit pas un calcul.
3. Les 37 tests marqués de `test_simulateur.py`.
