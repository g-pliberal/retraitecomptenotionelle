# Le témoin des sorties : plus aucun test marqué sur le moteur Python

Action 161, étape 8c, après `2026-11-15-les-servis-figes.md`. Aucune règle
du portage, aucune donnée n'a bougé ; un témoin naît.

## Ce qui est fait

- **Le témoin des sorties**, `tests/temoins/sorties.json` : pour chaque
  entrée qu'un test donne à un script de `tests/js/` (une liste d'entrées
  en fichier, une sortie par entrée), le script, l'entrée et l'empreinte de
  la sortie, chaque flottant lu à douze chiffres significatifs. L'empreinte
  seule : les sorties de `comparer-droit.mjs` sur un témoin sur cinq pèsent
  22 Mo, celles de `comparer-liquidation.mjs` 4 Mo. 638 entrées, 400 Ko,
  figées sur des sorties que le moteur Python refaisait au milliardième
  (les tests passaient avant la bascule, et le témoin, refait après le
  rebasage sur la carrière longue, n'a pas bougé).
- **`tests/outils_sorties.py`** : `sortie_figee(script, entrees)` lance le
  script et confronte chaque sortie au témoin ; une entrée absente arrête le
  test, `FIGER_SORTIES=1 python -m pytest <fichier>` l'ajoute (sous verrou) ;
  une sortie qui bouge l'arrête, et `python scripts/construire_temoins.py
  --sorties` (douze secondes) refait le témoin si le déplacement est voulu.
  La fabrique le refait avec les autres témoins (`regenerer.py`,
  `.gitattributes`). Tests : `tests/test_sorties_figees.py`.
- **Quatre scripts neufs** : `simuler.mjs` (la comparaison entière d'une
  requête, comme le site), `simuler-parcours.mjs`, `maximum-du-jour.mjs`,
  `faire-vivre-retouchee.mjs` (les deux derniers étaient en ligne dans
  `test_pension_maximale.py`).
- **Les dix-sept tests marqués** : treize au témoin ; l'oracle des périodes
  assimilées, les deux tests des périodes assimilées et la révision des
  minima agricoles confrontent le script à la façade, qui sert déjà tout.
  `RESTES` est vide ; `entrees_du_test` ne sert plus qu'à `test_facade.py`.
- **Dix confrontations cachées de même forme**, que la liste ne voyait pas
  (`_python` de `test_liquidation.py`) : coupures au mois, décompte des
  services, exonérations Agirc-Arrco, minima agricoles, minimum SNCF,
  réversion, simulateur, taux plein par catégorie, versements uniques au
  témoin ; l'Ircantec, dont les attendus viennent des textes, au portage
  seul. `_python` est retiré ; `test_liquidation.py` quitte `FICHIERS`.
- Un espion (`sys.setprofile` sur les modules de règles) a vérifié qu'aucun
  test converti n'exécute plus une règle du moteur Python.

## Ce qui reste

1. **`tests/test_pont.py`**, tel que la note de l'étape 8b le décrit.
2. **D'autres confrontations, que l'espion a vues** : les autres tests
   `les_deux_moteurs_*` de `test_reversion.py` (par une autre aide), le
   `_python` de `test_chronologie.py`, `test_age_conjoncturel.py`,
   `test_avantages.py`, et les `moitie_python` de `test_cumul_activites.py`,
   `test_cycle_de_vie_portage.py`, `test_moteur.py`, `test_web.py`. Même
   recette : un script de `tests/js/` et `sortie_figee`.
3. **Signalé par la session de la carrière longue** : sur `main`, la copie
   Python et le JavaScript diffèrent sur le témoin `rattachement_pension_smic`
   (réduction générale de la proposition, 3,45 € par an, années 11 à 13), ce
   que `test_facade_jumeau.py` révèle quand l'échantillon « un sur quarante »
   se décale. Non traité ici.

**Tests.** Les vingt-quatre fichiers touchés, `test_sorties_figees.py`,
`test_servis_figes.py`, `test_fabrique.py`, `test_niveaux.py` : 1 182
passés ; `python -m pytest -m rapide` : 5 380 passés ; `test_outillage.py`,
`test_pousser.py` : verts.
