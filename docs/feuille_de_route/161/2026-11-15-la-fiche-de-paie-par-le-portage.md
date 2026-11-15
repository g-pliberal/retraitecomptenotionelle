# La fiche de paie par le portage : `partage_taux_unique.py` ne demande plus rien au moteur Python, et les garde-fous de l'oracle partent

Action 161, étape 6e, après `2026-11-15-le-minimum-contributif-par-le-portage.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé.

## Les trois décisions du propriétaire, le 15 novembre 2026

1. **`partage_taux_unique.py`** : apprendre au pont à rendre des fiches de
   paie, pour que la fiche ne se calcule plus qu'en JavaScript
   (`remuneration.js`), puis porter l'étude à sorties identiques, le test
   d'abord. Fait, ci-dessous.
2. **Les quinze garde-fous « sans les jumeaux » de `test_oracle.py`**, marqués
   `sur_le_moteur_python` : supprimés maintenant. Fait, ci-dessous.
3. **L'ordre des portes de la carrière longue** (`_portes` du Python, rangées
   par génération puis par porte ; `portes` du portage, par âge maximal
   d'entrée ; note `2026-11-15-les-autres-oracles-a-la-facade.md`, « Un écart
   relevé, laissé ») : on ne le réordonne pas. Un audit séparé de cette table
   contre les textes est mené ailleurs, et ne touche pas à cette règle.

## Ce qui est fait

- **Les garde-fous de l'oracle** : les quinze tests partent, avec les trois
  aides qui ne servaient qu'à eux (`_sans_les_jumeaux`,
  `_exemples_de_chaque_forme`, `_mesures_sans_les_jumeaux`) et l'import de la
  fixture `entrees_du_test`. `test_oracle.py` n'entre plus dans le moteur
  Python : il quitte `RESTES` et `FICHIERS` de
  `tests/test_fichiers_sur_le_moteur_python.py`. Ses confrontations refont
  toujours chaque appel au jumeau (`outils_pont.droit_et_refait`).
- **Le test, écrit d'abord et vu rouge** pour la raison attendue
  (`tests/test_partage_taux_unique.py`) : `ConstructeurFiche` du Python
  empêché, l'étude doit imprimer ce que son docstring et la décision du
  20 septembre disent — 11,31 points salariés et 16,67 patronaux aujourd'hui,
  27,98 en tout ; le partage A à 6,33 et 16,67 ; C à 11,31 et 11,69 ; D à
  11,50 et 11,50.
- **Le pont** : une lecture de plus, `fiches_de_paie` (`fichesDePaie` de
  `pont.mjs`, `pont.fiches_de_paie` de `pont.py`). Sous des paramètres, un
  profil, un statut et une année, elle rend le plafond et le Smic de l'année,
  puis chaque appel : `fiche` (une `FicheLue`, ses montants et ses lignes),
  `brut_a_cout_donne`, `taux_du_bloc`. Le bloc retraite se nomme en données :
  `"droit_en_vigueur"`, ou les parts de la proposition, le pilier capitalisé
  partagé à part au besoin (`blocDeLaFiche`).
- **`scripts/partage_taux_unique.py`** : quatre demandes au pont (les repères,
  la fiche témoin, puis un lot par horizon) au lieu des chargeurs et du
  constructeur Python. Le Python ne garde que l'étude : le choix des
  partages, les écarts, l'impression.

## Les chiffres, inchangés

Avant et après, sorties identiques à l'octet sur quatre jeux d'options : par
défaut, `--volontaire`, `--statut salarie_prive_cadre --niveaux 0.8 1 1.3 2 5 8
--detail 5`, `--statut fonctionnaire_etat --volontaire --detail 1`.

## Ce qui n'est pas vérifié

La suite complète, que GitHub lance. Vérifiés : `-m rapide`,
`tests/test_oracle.py`, `tests/test_fichiers_sur_le_moteur_python.py`,
`tests/test_partage_taux_unique.py`.

## Ce qui reste

1. **L'étape suivante** : la liste de la clôture, les fonctions gardées des
   deux côtés et leur test (note de la question 4 de
   `2026-11-13-les-decisions-du-proprietaire.md`).
2. Puis le retrait des règles du moteur Python, d'un bloc, et les périodes
   assimilées du relevé, en JavaScript seul.
