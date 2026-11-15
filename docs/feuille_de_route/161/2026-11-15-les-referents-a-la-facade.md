# Les référents à la façade : trois tables de plus servies par le portage, et `test_referents.py` y passe

Vingtième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-le-releve-a-rebours-a-la-facade.md`, « Ce qui reste », 1 :
`test_referents.py`. Aucune règle, aucune donnée, aucun témoin n'a bougé. La
suite complète de GitHub était verte sur `83971c1` ; celle de `d09e207`,
annulée par la suivante, et celle de `dc1ede0` tournait au commit.

## Ce qui est fait

**Trois tables** entrent dans `pont.TABLES_DE_LA_FACADE` :
`ages_ouverture.age`, `ages_annulation_decote.age` et
`invalidites.version`. Le portage les tenait sous ces noms, la table
recouverte d'un droit contrefactuel comprise : rien n'a changé côté
JavaScript.

**`test_referents.py` passe à la façade** : 155 de ses 169 cas. Son
`Simulateur`, sa `Carriere`, `foyer` et `releve.points_de_l_annee` viennent
de `facade` ; il quitte `FICHIERS` et entre dans `RESTES`, deux
fonctions marquées. Trois retouches, sans changer ce qu'un
test éprouve :

- le test des âges de Catala ne bâtit plus la `TableRecouverte` à la main
  (les classes de `scenarios.actuel`) : il lit `ages_ouverture` d'un
  simulateur sous le droit contrefactuel, celle que
  `ScenarioActuel._sous_le_droit` bâtit de même ;
- les deux tests d'EDIFIS lisent les séries, les affiliations et le
  catalogue sur le simulateur, données que la façade sert, et non sur son
  moteur ;
- les deux tests de l'ASPA de Saphir et d'EUROMOD (14 cas), qui passent à
  `foyer.foyer_et_net` un moteur fait d'un barème posé à la main, restent
  sur le moteur Python, marqués : la façade ne transmet pas une table
  retouchée. Ils se porteront quand le barème passera en données, ou
  partiront avec le jumeau.

Aucun fichier n'emprunte de fonction à `test_referents.py`.

## Ce qui est mesuré

Un test neuf dans `tests/test_facade.py`, vu rouge (l'âge légal et celui du
taux plein de 1955, l'inapte de 2024, la génération 1968 au 31 août 2023) ;
sept appels confrontés au jumeau dans `tests/test_facade_jumeau.py`, sous un
troisième jeu de paramètres, le droit au 31 août 2023. `-m rapide`,
`test_referents.py`, `test_facade.py`, `test_facade_jumeau.py`,
`test_pont.py` et `test_fichiers_sur_le_moteur_python.py` : verts.

## Ce qui reste

1. `test_sections_liberales.py` (`compter`, `acquerir`, `coordonner`,
   `completer._taux_majoration_enfants`, `noyau.carte`),
   `test_temps_partiel.py` (`releve`, `chronologie`), `test_oracle.py`
   (l'échéancier, `departs`, `invalidite`, des tables du scénario).
2. « Faire vivre » servi ouvre la voie aux fichiers qui l'appellent :
   `test_departs.py`, `test_invalidite.py`, `test_pension_maximale.py`,
   `test_majoration_*`, `test_pension_minimum_avant_1983.py`, et le test
   marqué de `test_liquidation.py`.
3. Les 37 tests marqués de `test_simulateur.py`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance.
