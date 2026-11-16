# L'inventaire du retrait des règles : ce que la suppression du moteur Python emporterait

Action 161, suite de `2026-11-16-la-fabrique-sur-le-simulateur-de-donnees.md`.
Le propriétaire a accepté, le 16 novembre 2026, qu'on prépare le retrait des
règles Python, sans rien supprimer : la suppression attend son accord final.
Aucun code, aucune donnée, aucun témoin n'a bougé dans cette étape.

## Le périmètre

Les fichiers de règles sont ceux que la sonde (`scripts/sonde_moteur_python.py`)
et la liste des fichiers de tests sur le moteur
(`tests/test_fichiers_sur_le_moteur_python.py`) nomment : `droit/` (23
fichiers, 23 020 lignes), `moteur/` (7, 3 037), `scenarios/` (3, 4 708),
`carriere.py` (3 677), `revalorisation.py` (1 462), `simulateur.py` (1 170),
`echeancier.py` (709), `pilote.py` (253), `journal.py` (127) : 39 fichiers,
38 163 lignes. Leurs jumeaux JavaScript restent.

## La méthode

Trois mesures, au commit `f89a786` :

- les imports de ces fichiers par tout `src/`, `scripts/`, `tests/` et
  `moteur/`, lus dans l'arbre syntaxique, chaque nom importé classé (type de
  données, constante, fonction, classe, module) ;
- la carte des jumeaux (`python scripts/jumeaux.py --json`) : fiches,
  chiffres ancrés, chargements par chemin et mentions qui nomment chaque
  fichier ;
- la lecture de ce que la façade des tests (`tests/facade.py`) et le pont
  prennent des jumeaux.

La sonde de la fabrique, à l'étape précédente, reste la mesure dynamique :
la fabrique n'exécute plus que 104 fonctions de chargeurs et de types logés
dans les fichiers de règles.

## Ce que la suppression casserait

### 1. Les types que le pont échange (`pont.py`)

Le pont relit ce que calcule le moteur JavaScript sous 22 types Python logés
dans les fichiers de règles : `Carriere`, `AnneeCarriere` (`carriere.py`) ;
`PensionRegime`, `AvantageApplique` (`droit/commun.py`) ; `Cumul`
(`droit/cumul.py`) ; `Demande`, `Mesure` (`droit/liquidation.py`) ;
`EligiblePlafondEnfants` (`droit/liquider.py`) ; `Reversion`
(`droit/reversion.py`) ; `Evenement` (`echeancier.py`) ; `Entree`, `Journal`
(`journal.py`) ; `RegimeFusionne` (`moteur/fusion.py`) ; `TauxIndexation`
(`moteur/indexation.py`) ; `ActuelAujourdhui`, `MajorationExceptionnelle`,
`RegimeServi` (`revalorisation.py`) ; `ResultatActuel`
(`scenarios/actuel.py`) ; `GarantieVieillesse`, `ResultatNotionnel`
(`scenarios/notionnel.py`) ; `Comparaison` (`simulateur.py`). D'autres
types n'ont que des lecteurs dans les tests ou les scripts : `Metier`,
`LigneRelevee` (que lit aussi `chronologie.py`), `PensionEtrangere`,
`PeriodeALEtranger`, `ReversionAgricole`, `PetitePension`,
`DureesDesCultes`, `CompteNotionnel`, `CotisationAnnuelle`,
`EligibleAgricole`, `EligibleMinimum`. En tout, 157 imports de types de
données et 107 de constantes. La note de décision 0006 les garde : ils
doivent changer de fichier avant la coupe, un exemplaire par langage.
`Carriere` porte aussi des méthodes de règle (`prolongee`, `depuis_profil`),
qu'il faut séparer du type.

### 2. Les chargeurs logés dans les fichiers de règles

- **La fabrique du paquet** (`scripts/construire_donnees.py`) lit 43
  classes de `scenarios/actuel.py` (âges, durées, décotes, minimum
  contributif, conversions de points, réversions…),
  `moteur/age_reference._charger_ages` et `carriere.Affiliations`. Ce sont
  les chargeurs que la note 0009, non adoptée, voulait reloger.
- **Le simulateur de données** (`donnees/simulateur.py`) et la fabrique des
  témoins (`scripts/construire_temoins.py`) lisent `carriere.Affiliations`.
- **Le coût des avantages** (`avantages.py`) lit `FichesDatees`,
  `CarriereLongue` et `ScenarioActuel` de `scenarios/actuel.py`, et les
  fiches des emplois (`droit/compter._contrats`, trois constantes) : ses
  variantes neutralisées (`scenarios_neutralises`) sont des `ScenarioActuel`
  retouchés.
- `tests/test_revalorisation.py` lit `revalorisation.RevalorisationsPensions`,
  qui a déjà son chargeur sous `donnees/revalorisations.py`.

`scenarios/actuel.py` importe dix modules de `droit/` en tête : ses
chargeurs ne peuvent pas rester dans le fichier une fois les règles parties.

### 3. La façade des tests

C'est la plus grosse dépendance. 114 fichiers de tests importent la façade,
153 la façade ou `tests/outils_pont.py`. La façade sert, sous leurs noms
Python, 106 règles du droit (19 modules), 61 méthodes de tables (34 tables)
et 10 constructeurs du compte (`pont.REGLES_DE_LA_FACADE`,
`TABLES_DE_LA_FACADE`, `CONSTRUCTEURS_DE_LA_FACADE`). Pour lier les
arguments et relire le résultat, elle lit la signature et le type de retour
de chaque jumeau Python (`inspect.signature`, `typing.get_type_hints`,
quatorze endroits de `tests/facade.py`). Supprimer les règles lui ôterait
ces contrats : il faut d'abord qu'elle les porte elle-même, ou qu'un
fichier de signatures sans corps les lui donne. `tests/outils_pont.py`
importe aussi `Simulateur`, `pilote` et `droit.ouvrir`.

### 4. Du code Python seul, encore branché aux règles

- `castypes.py` : `calculer_cas_types`, qui n'a plus d'appelant, et
  `carriere_de_la_grille`, qu'il est seul à appeler ; `CasType.age_de_depart` (par
  `pilote.age_de_depart`, lu par `tests/test_agregats.py`),
  `CasType.niveau_relatif` (par `moteur/conversion.niveau_relatif`, que
  surchargent `scripts/grille_large.py` et `scripts/mesures_prose.py`).
  Le module importe `Simulateur`, `pilote` et les types de `carriere.py`.
- `avantages.recalculer`, qui liquide par
  `simulateur.scenario_actuel.calculer` : seul `tests/test_avantages.py`
  l'appelle.
- `remuneration.py`, jumeau hors du périmètre, appelle
  `carriere.salaire_moyen_annuel` dans `indemnite_stylisee` ; il importe
  aussi le simulateur Python, qui l'importe.
- `scripts/grille_large.py` appelle `simulateur.carriere_parcours` dans une
  sous-classe (ligne 1744) : à vérifier sous la sonde.

### 5. Ce qui nomme les fichiers de règles sans les importer

- **Les fiches** : 244 des 267 fiches de `data/reference/regles/` nomment
  un fichier de règles Python dans leur champ `code.python` (118 pour
  `droit/liquider.py`, 121 pour `scenarios/actuel.py`), que
  `tests/test_carte.py` (`test_le_code_de_chaque_fiche_tient`) confronte
  au dépôt. Il faut décider si ce champ disparaît, ou s'il nomme désormais
  ce qui reste en Python.
- **Les chiffres ancrés** : 22, dans sept documents (`README.md`,
  `docs/methodologie.md`, `docs/parcours_presentation.md`, quatre parties
  de `docs/limites/`), chargent un module de règles par son nom.
- **Les chargements par chemin** : `scripts/sonde_moteur_python.py`,
  `scripts/entrees_du_moteur.py`, `scripts/tableau_de_bord.py`,
  `tests/test_carte.py`, `tests/test_entrees_du_moteur.py`,
  `tests/test_sonde_moteur_python.py`, `tests/test_univers.py`.
- **Les mentions à tenir** : 142 textes, dont `data/reference/referents.yaml`
  et les étapes de `data/reference/etapes/`.
- **Les gardes des jumeaux** : `scripts/jumeaux.py`, `tests/test_jumeaux.py`
  et `scripts/jumeaux_gardees.yaml` comptent les paires ; une paire sans
  Python doit en sortir.

### 6. Les tests qui partent avec les règles

`tests/test_facade.py` et `tests/test_facade_jumeau.py`, qui confrontent la
façade au jumeau ; les tests de la sonde et de la liste des fichiers sur le
moteur, dont l'objet disparaît.

## Le plan de retrait proposé

Une étape par session, chacune vérifiée par la fabrique (paquet, agrégats,
témoins identiques à l'octet) et par `python -m pytest -m rapide` :

1. **Les types du pont** sortent des fichiers de règles vers un module à
   eux, sans corps de règle ; les fichiers de règles les réimportent le
   temps du retrait.
2. **La façade porte ses contrats** : signature et type de retour de chaque
   règle, table et constructeur qu'elle sert, sans lire le jumeau.
3. **Les chargeurs** sortent vers `donnees/` (note 0006). Pour ceux de
   `scenarios/actuel.py`, c'est la question que posait la note 0009, à
   trancher par le propriétaire avant cette étape.
4. **Le Python seul encore branché** (section 4) passe au pont ou part.
5. **Les fiches, les ancres et les gardes** cessent de nommer les fichiers
   de règles.
6. **La suppression** des 39 fichiers, avec `test_facade.py` et
   `test_facade_jumeau.py`, sur l'accord final du propriétaire.

## Les deux choix du propriétaire

Il a tranché le 16 novembre 2026, en suivant les deux recommandations de
cette note (« On applique tes recommandations ») :

- **Les chargeurs de `scenarios/actuel.py`** se relogent tels quels sous
  `donnees/`, comme le veut la note 0006, sans attendre la décision qui
  remplacera la note 0009. Aucune donnée ne bouge : le paquet reste
  identique à l'octet.
- **Le champ `code.python` des fiches** se retire, avec la confrontation
  que `tests/test_carte.py` en fait.

La suppression finale des fichiers de règles attend toujours son accord.

**Tests.** Aucun code n'a changé ; aucun test neuf.
