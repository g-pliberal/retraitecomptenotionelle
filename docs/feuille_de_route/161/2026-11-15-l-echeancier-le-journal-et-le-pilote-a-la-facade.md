# L'échéancier, le journal et le pilote à la façade : huit tests de `test_liquidation.py` quittent le moteur Python

Action 161, étape 5f, après
`2026-11-15-la-garantie-et-les-durees-posees-a-la-facade.md`, « Ce qui
reste », 2. Aucune règle, aucune donnée, aucun témoin n'a bougé. La suite
complète de GitHub était verte sur `03f9ea9`, l'étape précédente.

## Ce qui est fait

- **L'échéancier** (`facade.Echeancier`, `facade.echeancier`) : `parcourir`,
  servi par le portage, l'échéance comprise (entrée `echeancier.parcourir` de
  `pont.mjs`) ; `Simulateur.echeancier`, qui date l'échéance au portage
  (`simulateur.echeancier`) ; `depart_de` ; `SORTES`, telles que le paquet
  les tient — sans le texte qui dit chaque sorte, que le paquet ne garde pas.
  Ce que les tests en lisent : le journal, le scénario 1 au départ et à
  l'échéance, et les appels de `liquider`, comptés dans
  `liquidation.appels()`. Une entrée « liquidation » du journal, dont le
  contenu ne passe pas le pont, y vient par ce que son contrat C.6 en décrit
  (`donnees()`).
- **Le journal** (`facade.Journal`, `facade.journal`) : ses entrées, sous le
  type `Entree` du Python, tenues dans la façade ; chaque inscription, ce
  qu'il sert pour une période et son état à une date, demandés au portage
  (`journal.operer`), qui refait le journal de ce qui date chaque entrée. Un
  refus d'inscription y est la `ValueError` du Python.
- **La liquidation** reçoit un journal vide de la façade, et rend ce qu'elle
  y a écrit — rien, elle est pure — et sa fiabilité.
- **Le pilote** (`facade.pilote.age_de_depart`) : l'âge d'un cas type, par
  ce que le portage en lit (`CasType.pour_le_portage`), et les appels de
  `liquider` qu'il a coûtés (`pilote.age_de_depart`).
- **`test_liquidation.py`** : huit tests quittent la marque (9 → 1). Le test
  du pilote ne compare plus son âge à `CasType.age_liquidation_pour`, qui
  appelle le pilote Python, mais à celui que le coût retient
  (`pont.ages_de_depart`).
- **Contre le jumeau** (`test_facade_jumeau.py`) : l'échéancier de cinq
  carrières, son journal entrée par entrée, ce qu'il sert à trois dates, le
  scénario 1 au départ, les appels ; les sortes ; l'âge de six cas types,
  trois générations, deux variantes, sous la référence et les conventions du
  COR ; la fiabilité de la liquidation.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide` (5 243), les
fichiers de la façade, `test_liquidation.py`, `test_droit.py`,
`test_reversion.py`, `test_simulateur.py`, `test_pont.py`, les
confrontations légères et les quatorze fichiers qui importent les aides de
`test_liquidation.py`.

## Ce qui attend le propriétaire

Toujours les quinze garde-fous « sans les jumeaux » de `test_oracle.py`, et
l'ordre des portes de la carrière longue.

## Ce qui reste

1. La confrontation de `test_liquidation.py` garde sa marque, comme celle de
   `test_droit.py` : elle refait au jumeau ce que le portage calcule, et part
   avec lui.
2. Les deux tests du solveur `niveau_pour_pension` de `test_simulateur.py`.
3. `Saisies.simuler` et `Saisies.simulateur` (`test_reversion.py`).
4. Les autres fichiers de `RESTES` (`tests/test_fichiers_sur_le_moteur_python.py`),
   d'abord `test_pension_maximale.py` (5) et `test_invalidite.py` (4).
