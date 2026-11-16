# La quatrième vague à mi-chemin : ce qu'il reste à faire de `test_moteur.py` et de `test_pont.py`

Action 161, quatrième vague, note de passation de la session qui l'a menée
en parallèle de la troisième. Cinq fichiers en sont sortis, chacun avec sa
note : `test_remuneration.py` et `test_limite_age.py`
(`2026-11-15-la-remuneration-et-la-limite-d-age-a-la-facade.md`),
`test_capitalisation.py` (`2026-11-15-la-capitalisation-au-portage.md`),
`test_independants.py` (`2026-11-16-les-independants-a-la-facade.md`),
`test_emploi_retraite.py` (`2026-11-16-l-emploi-retraite-a-la-facade.md`).

## `test_moteur.py` (73 tests sur 77)

Des tests unitaires des modules Python que la façade ne sert pas :
`Indexation` (38 appels), `Convertisseur` (16), `AgeReference` (6),
`fusionner` (7), `profil_salaire` et `_facteur_secteur` (10), quelques
`ancrage_salaire_moyen`, `bornes_deformation`, `niveau_relatif`. La voie de
`test_capitalisation.py` s'y prête : ce qui bâtit un objet du moteur à la
main sous d'autres données passe en essai de node (`tests/js/`), sur le
module du portage, ses attendus écrits de tête ; ce qui lit le simulateur
passe à la façade ; ce que le pont sert déjà (`indexation.taux`,
`indexation.coefficient`, `conversion.coefficient.diviseur`,
`age_reference.age`, `fusion.fusionner`, `carriere.ancrage_salaire_moyen`),
par `pont.droit`. Plusieurs étapes, par module.

## `test_pont.py` (34 tests sur 66)

Passé à la façade (`Carriere`, `Simulateur`), il garde quinze tests rouges,
de deux sortes :

- **Les confrontations au jumeau** (« au bit près de leur jumeau »,
  « celle du jumeau au bit », les lectures Python de la revalorisation
  servie, la classe Python des séries, l'histoire du droit) : leur place
  est `test_facade_jumeau.py`, qui part avec le moteur Python.
- **Le coût** (`test_le_cout_*`, la grille des carrières, les variantes,
  le barème du régime unique, la table prêtée) : le coût prend encore un
  simulateur Python. Ils peuvent rejoindre `test_cout.py`, qui attend la
  même chose, avec `_interdire` et `_jumeaux_qui_datent_et_batissent`, que
  `test_grille_large.py` importe de `test_pont.py`.

## Ce qui attend le coût

`test_cout.py`, `test_grille_large.py` (19 tests rouges à la façade :
`scripts/grille_large.py` appelle `coordonner.regimes_interpenetres` sur le
moteur, retouche le modèle, lit `Simulateur.univers_de_la_demande`), et
`test_effet_retour.py`.

**Tests.** Rien de neuf depuis la note précédente ; `python -m pytest -m
rapide` : 5 422 passés, 64 sautés, après le rebasage sur la troisième vague.
