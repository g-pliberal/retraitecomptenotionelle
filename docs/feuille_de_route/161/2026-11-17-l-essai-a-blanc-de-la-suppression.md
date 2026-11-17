# L'essai à blanc de la suppression : ce qui casse encore, et les types importés de leur module

Action 161, étape 6 de `2026-11-16-l-inventaire-du-retrait-des-regles.md`,
menée le 17 novembre 2026. Le propriétaire a donné son accord à la
suppression des fichiers de règles Python, une fois la suite complète verte
(elle l'était, à 8f09f4b). Aucune règle, aucune donnée, aucune valeur
attendue ne change ; aucun fichier de règles n'est encore supprimé.

## L'essai à blanc

Dans un worktree jetable, les 40 fichiers de règles supprimés (`droit/`,
`moteur/`, `scenarios/` avec leurs `__init__.py`, et `carriere.py`,
`echeancier.py`, `journal.py`, `pilote.py`, `revalorisation.py`,
`simulateur.py`), puis `python -m pytest --co` : 137 fichiers de tests ne se
chargent plus. Rangés par la première importation qui casse :

- 54 par `tests/facade.py`, 18 par `tests/outils_pont.py` ;
- 63 parce qu'ils importent eux-mêmes d'un fichier de règles, presque
  toujours un type (`Metier`, `AnneeCarriere`, `PensionRegime`…) ou une
  constante que le fichier de règles reprend d'ailleurs ;
- 2, `test_facade.py` et `test_facade_jumeau.py`, qui partent ou se
  récrivent avec la façade.

Hors des tests : `chronologie.py`, `scripts/mortalite_population.py`,
`scripts/scenarios_meres.py` (des types et une constante),
`scripts/mesures_prose.py` (la classe `Carriere` des règles), et le pont,
dont `OBJETS_DU_RESULTAT` lit `EligibleAgricole` dans `droit/liquider.py`
par son nom, sans import que l'arbre syntaxique voie.

## Fait : les types et les constantes importés de leur module

124 imports de 81 fichiers passaient par un fichier de règles pour un nom
qu'il importe lui-même d'ailleurs (`types_du_pont`, `donnees`,
`revalorisation_servie`). Ils importent désormais de ce module ; chacun des
150 noms est le même objet des deux côtés (vérifié par `is`). Un outil
jetable a récrit les imports, d'après les imports des fichiers de règles.

Le nouveau test
`test_hors_des_regles_un_type_ou_une_constante_s_importe_de_son_module`
(`tests/test_fichiers_sur_le_moteur_python.py`) tient la liste, qui ne fait
que décroître, des 13 fichiers qui importent encore quelque chose d'un
fichier de règles (`IMPORTEURS_DES_REGLES`). Refait après ce lot, l'essai à
blanc ne casse plus que par eux : 106 fichiers par la façade, 20 par
`outils_pont.py`, 11 par leurs propres imports.

## Ce qui reste, lot par lot

Chaque lot dans une session à lui, vert sous `-m rapide`, aucune valeur
attendue changée.

1. **Les constantes que seul un fichier de règles tient**, lues par sept
   tests (`test_capitalisation.py`, `test_coefficients_agirc_1947.py`,
   `test_fonction_publique_etat.py`, `test_ircantec_minoration.py`,
   `test_majoration_exceptionnelle.py`, `test_oracle_minima.py`,
   `test_revalorisation.py`) : les lire au portage
   (`pont.constante_du_droit`) ou dans leurs données ; `EligibleAgricole`
   sous `types_du_pont/droit.py` ; `mesures_prose.py` sur la carrière nue.
2. **`tests/outils_pont.py`** sans le simulateur Python : `Saisies`, la
   copie sous la classe des règles (`des_regles`) et les gardes qui
   empêchent les jumeaux du coût de calculer
   (`empecher_les_jumeaux_du_cout`, `jumeaux_qui_datent_et_batissent`),
   qui n'ont plus d'objet une fois les jumeaux partis.
3. **`tests/facade.py`** sans les modules de règles : `Regles` et
   `_Module` lisent l'existence et les constantes d'un nom sur le jumeau
   (`_jumeau`), à lire sur les contrats et au portage ; `Carriere` hérite
   de la classe des règles ; `JUMEAUX`, la marque `sur_le_moteur_python`
   et `simulateur_du_test` retombent sur le Python, alors que plus aucun
   test ne porte la marque (`RESTES` est vide).
4. **La suppression** : les 40 fichiers ; les confrontations au jumeau,
   qui partent avec lui (`test_facade_jumeau.py`,
   `tests/jumeau_des_avantages.py` et ce que `test_avantages.py` en tire,
   la confrontation des contrats à leur jumeau dans
   `test_contrats_de_la_facade.py`) ; la sonde du moteur Python et ses
   tests, et `test_fichiers_sur_le_moteur_python.py`, dont l'objet
   disparaît ; les gardes des jumeaux (`scripts/jumeaux.py`,
   `tests/test_jumeaux.py`, `scripts/jumeaux_gardees.yaml`) ; les en-têtes
   des 35 JavaScript qui déclarent un jumeau ; `MOTEUR_PYTHON` du tableau
   de bord ; les mentions à tenir dans les docstrings.

**Tests.** Un test neuf, vu rouge avant le lot (les importeurs
d'alors), vert après ; `python -m pytest -m rapide` : 5 703 réussis ; toute
la suite se charge (9 289 tests).
