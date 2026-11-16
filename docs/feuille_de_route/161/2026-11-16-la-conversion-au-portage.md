# La conversion au portage : les tests du diviseur de `test_moteur.py` éprouvés sur le module du site

Action 161, quatrième vague, après `2026-11-16-l-indexation-au-portage.md`.
Aucune règle, aucune donnée, aucun témoin n'a bougé. `test_moteur.py` reste
dans `FICHIERS` : il garde 41 tests sur 54 (la note précédente en comptait 53,
un test paramétré mis à part).

## Ce qui est fait

- **`tests/js/conversion.test.js`**, neuf, que `test_web.py` lance avec les
  autres essais de node : douze tests de `test_moteur.py` qui bâtissaient
  `Convertisseur` ou `DonneesMortalite` à la main passent sur les modules du
  portage (`moteur/js/conversion.js`, `moteur/js/mortalite.js`). Le diviseur
  qui décroît avec l'âge ; l'effet de l'anticipation ; le diviseur égal à
  l'espérance résiduelle sous un taux anticipé nul, et plus court sous un taux
  positif ; la table par sexe, qui pénalise les femmes et exige le sexe ; la
  table d'une population, fonctionnaires civils ou vingtiles extrêmes de
  niveau de vie ; l'absence de marche à l'anniversaire et au 1er janvier ; le
  diviseur sous les trois hypothèses d'espérance de vie, et le capital
  rétroactif qu'elles ne touchent pas, ce dernier par le simulateur du site.
  Les attendus sont des sens de variation, des identités ou des écarts
  d'espérance de vie, comme dans le Python.
- Un treizième, le préfinancement du diviseur rendu sur la pension servie,
  était déjà porté dans `tests/js/moteur.test.js` : son double Python est
  retiré.
- `test_moteur.py` n'importe plus `TableConversion`.

## Ce qui reste de `test_moteur.py`

Dans le bloc de la conversion, trois tests lisent ce que le site ne sert pas
encore : `test_la_population_ne_change_rien_au_scenario_1_et_baisse_les_notionnels`
et `test_le_rattachement_par_la_pension_est_un_point_fixe` bâtissent un cas
type (`CAS_TYPES`, que le portage ne tient que figé, dans les agrégats) ;
`test_une_hypothese_d_esperance_de_vie_hors_de_l_insee_est_refusee` éprouve
le chargeur Python des tables, et la population du coût. Ils partiront avec
les cas types et le coût. `test_le_compte_notionnel_se_recompose_a_la_main`
bâtit encore un `Convertisseur` Python, avec le compte.

Par module ensuite, une étape chacun : `AgeReference` (6) ; `fusionner` (7),
par `tests/js/fusion.test.js` ; le profil de rémunération (`profil_salaire`,
`_facteur_secteur`) ; les cas types et le mois, à la façade.

**Tests.** `node --test tests/js/conversion.test.js` (12), `test_moteur.py`
(41), `test_fichiers_sur_le_moteur_python.py` et l'essai de node de
`test_web.py` : verts ; `python -m pytest -m rapide` : vert.
