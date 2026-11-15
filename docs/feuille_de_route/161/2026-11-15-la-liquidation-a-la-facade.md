# La liquidation à la façade : son contrat, ses neutralisations, ses mesures et ses appels servis par le portage, et `test_liquidation.py` y passe en partie

Onzième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-le-releve-entier-a-la-facade.md`, « Ce qui reste », 1.
`tests/test_liquidation.py` passe à la façade : il entre dans `RESTES` avec
13 tests marqués sur 22 (`tests/test_fichiers_sur_le_moteur_python.py`), et
reste dans `FICHIERS`, ses tests marqués important encore le foyer, le
journal, l'échéancier et le pilote. Aucune règle, aucune donnée, aucun témoin
n'a bougé.

## Ce qui est fait

**Le relevé de ce que chaque test lit.** Neuf tests ne lisent que la
liquidation d'une carrière seule : son contrat C.6, ses totaux, ses mesures,
ses avantages, le contexte et ses neutralisations, les appels de `liquider`,
une table du minimum vieillesse, le journal d'une simulation, deux
constantes. Ils passent à la façade, inchangés. Les treize autres appellent ce
que la façade ne sert pas, et gardent le moteur Python sous leur marque :

| tests | ce qu'ils appellent |
|---|---|
| les étapes seules (1) | `ouvrir.ouvrir`, `liquider.liquider_chaque_regime`, `completer.completer`, `foyer.foyer_et_net` |
| l'ASPA du couple, le minimum vieillesse d'avant 2007 (2) | `foyer.foyer_et_net` et l'objet qu'il rend |
| la liquidation pure (1) | un `journal.Journal` dans l'état, que le portage ne verrait pas |
| faire vivre (1) | `revalorisation.faire_vivre`, `actuel_aujourd_hui` |
| le journal (2) | `journal.Journal`, ses entrées et ses lignées |
| l'échéancier (2) | `echeancier.Echeancier`, `depart_de`, `SORTES` |
| le pilote (3) | `pilote.age_de_depart`, `CasType.age_liquidation_pour` |
| la confrontation (1) | le jumeau refait la liquidation et le journal du portage |

**La liquidation entière.** `liquidation.liquider` rend, en plus du taux et
des pensions, ses trois totaux, ses mesures (`Mesure`), ses avantages
(`AvantageApplique`), les lignes du relevé qu'elle a lues, ce que le contrat
C.6 en décrit (`donnees()`), la demande et le contexte reçus. Les
neutralisations du contexte passent au portage, qui les refusait. Chaque
liquidation dit combien d'appels de `liquider` elle a coûtés, essais compris ;
`liquidation.appels()` en tient le compte, pour les liquidations de la façade.

**La demande.** `liquidation.demande_de_depart` est servie par le portage
(`demandeDeDepart`), sous le type `Demande` du Python. Les constantes du
module (`APPELS_DECLARES`, `NEUTRALISATIONS`) se lisent : ce ne sont pas des
règles.

**Ce qui reste refusé.** Un journal dans l'état, des pensions servies, une
pension provisoire, une date d'observation, une hypothèse.

**Une retouche d'aide.** `_python`, que trois autres fichiers importent pour
leur confrontation, prend le jumeau `liquidation` lui-même, et non le nom du
fichier, que la façade sert désormais : sans cela, leurs appels Python
valaient zéro.

## Ce qui est mesuré

| `test_liquidation.py` | avant | après |
|---|---:|---:|
| tests sur le moteur Python | 22 | 13 |

**Contre le jumeau.** `tests/test_facade_jumeau.py` confronte la demande et
la liquidation de six carrières, une mère avec l'AVPF comprise, sous quatre
jeux de neutralisations, sous la référence et sous les conventions du COR : le
contrat C.6, les lignes lues, les totaux, les mesures, les avantages et les
appels, au bit près.

**Les tests.** Deux tests neufs dans `tests/test_facade.py`, vus rouges ; le
test des refus retouché, la neutralisation n'étant plus refusée. `-m rapide`
(5 135), `test_facade.py`, `test_facade_jumeau.py`, `test_liquidation.py`,
`test_droit.py`, `test_reversion.py`, `test_simulateur.py`, `test_pont.py`,
`test_fichiers_sur_le_moteur_python.py`, et les confrontations qui importent
`_python` : verts.

## Ce qui reste

1. `test_liquidation.py`, ses 13 tests marqués. Le plus gros lot, le foyer
   (trois tests) : servir `foyer.foyer_et_net` en entier, que le pont lit
   déjà sous le type `Foyer` du journal, et la méthode `plafond_couple` de la
   table du minimum vieillesse. Puis les étapes seules (`ouvrir.ouvrir`,
   `liquider_chaque_regime`, `completer.completer`), sur le modèle du relevé.
   Le journal, l'échéancier et le pilote attendent la liste des fonctions
   gardées des deux côtés : le journal du Python lit déjà celui du portage
   (`journal_des_donnees`), et pourrait rester comme type.
2. Puis `test_cultes.py`, `test_bonifications_emplois.py` et les autres
   fichiers qui lisent le relevé ; `completer.points_rco_de_chef` ; les 37
   tests marqués de `test_simulateur.py`.
3. Les confrontations marquées partent avec le moteur Python.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
