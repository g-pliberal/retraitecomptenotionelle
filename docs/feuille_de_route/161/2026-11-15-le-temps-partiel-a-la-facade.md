# Le temps partiel à la façade : le relevé prolongé et le salaire moyen d'une année servis par le portage

Vingt-deuxième tranche de l'étape « les tests » (table de
`2026-11-13-les-decisions-du-proprietaire.md`), sur la consigne de
`2026-11-15-les-sections-liberales-a-la-facade.md`, « Ce qui reste », 1 :
`test_temps_partiel.py`. Aucune règle, aucune donnée, aucun témoin n'a
bougé. La suite complète de GitHub était verte sur `dc1ede0` ; celles de
`e4919b8` et `413398f` tournaient au début de l'étape.

## Ce qui est fait

**Ce qu'il fallait n'était pas où la note l'annonçait.** Le relevé
(`releve.construire`, ses durées et leurs services) et la chronologie de la
carrière bâtie passaient déjà : les seize tests verdissent sous la façade
dès ses imports changés. Ce qui manquait, ce sont deux fonctions de
`carriere.py` que le fichier importait : `prolonger_releve` et
`salaire_moyen_annuel`.

**Deux règles hors du droit** entrent dans `pont.REGLES_DE_LA_FACADE`, sous
un module `carriere` (`moteur/js/carriere.js`, que `MODULES_DU_DROIT` de
`pont.mjs` ouvre à ces deux-là seules). La façade les sert sous leurs noms
(`facade.prolonger_releve`, `facade.salaire_moyen_annuel`, et leurs jumeaux
dans `JUMEAUX`) :

- les séries passent par leur marque (`pont.SERIES`), celles d'un simulateur
  de la façade seulement, dont la règle prend les paramètres ; d'autres
  séries sont refusées ;
- un relevé saisi, une suite de `LigneRelevee`, passe champ à champ ; les
  trois dictionnaires de `prolonger_releve` (`interruptions`,
  `temps_partiel`, `dispenses`) passent en table (`TABLES_DES_REGLES`) ;
  une retraite progressive, un couple dont une `DateMois`, est refusée ;
- les lignes rendues se lisent sous `LigneRelevee` ; leurs trimestres,
  `int | float | None`, que la lecture stricte ne départage pas, gardent le
  type que JSON leur rend (`pont.NOMBRES_TELS_QUELS`), comme ceux de la
  chronologie.

**`test_temps_partiel.py` passe entier à la façade** : ses seize cas, sans
test marqué ; il quitte `FICHIERS` et n'entre pas dans `RESTES`. Ses imports
seuls changent. Les fonctions qu'en empruntent d'autres fichiers : aucune.

## Ce qui est mesuré

Un test neuf dans `tests/test_facade.py`, vu rouge : un relevé de 2024 à
80 % prolongé au 1er juillet 2026, ramené au temps plein (20 000 €) puis
avancé au rythme du salaire moyen, six mois en 2026 à la quotité déclarée ;
le refus de séries d'un autre simulateur et d'une retraite progressive.
Quatre appels confrontés au jumeau (`tests/test_facade_jumeau.py`), dont un
relevé à deux lignes la même année et des trimestres fractionnaires.
`-m rapide`, `test_temps_partiel.py`, `test_facade.py`, `test_pont.py`,
`test_facade_jumeau.py -k regle` et `test_fichiers_sur_le_moteur_python.py` :
verts.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance ; `test_facade_jumeau.py` en entier.
`Carriere.duree_de_service`, qu'un test appelle sur la carrière rendue,
reste une méthode Python du type que le pont échange : la liste des fichiers
ne voit pas une méthode appelée sur un type de données.

## Ce qui reste

1. `test_oracle.py` (l'échéancier, `departs`, `invalidite`, des tables du
   scénario) ; `test_releve_prolonge.py`, `test_lodeom.py` et
   `test_micro_social.py`, qui empruntent aussi `prolonger_releve` ou
   `salaire_moyen_annuel`, désormais servis.
2. « Faire vivre » servi ouvre la voie aux fichiers qui l'appellent :
   `test_departs.py`, `test_invalidite.py`, `test_pension_maximale.py`,
   `test_majoration_*`, `test_pension_minimum_avant_1983.py`, et le test
   marqué de `test_liquidation.py`.
3. Les 37 tests marqués de `test_simulateur.py`.
