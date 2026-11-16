# La grille large sans le moteur Python : ses âges aux données, son salaire moyen au pont, ses replis retirés

Action 161, point 2 de « Ce qui reste » de
`2026-11-16-le-tri-des-scripts-et-des-modules.md`. Aucune règle, aucune
donnée, aucun témoin n'a bougé.

`scripts/grille_large.py` n'exécute plus de règle du moteur Python :

- **Ses âges** (légal, d'annulation de la décote, douze lectures) se lisent
  aux tables de la législation par `donnees.chargement`
  (`TableDesAges`, `ages_ouverture`, `ages_annulation_decote`), au lieu des
  chargeurs `AgesOuverture` et `AgesAnnulationDecote` de `scenarios/actuel.py` :
  le même fichier, la même colonne, la même lecture en escalier.
- **Le salaire moyen** qui situe le Smic (`CasTypeLarge.au_smic`,
  `donnees_population`) se demande au pont (`salaire_moyen`, sur
  `pont.salaires_moyens`, de 1900 à 2120 d'une demande, gardé par paramètres).
- **Les replis « en Python sinon »** de `Departs` et de `debut_de_la_surcote`
  sont retirés : un cas type que le portage ne date pas est refusé
  (`ValueError`). Ils ne servaient plus : la grille élargie se date au portage
  depuis l'étape 7. `CasTypeLarge.age_liquidation_pour`, `_carriere` et
  `_debut_de_la_surcote_en_python` restent : ce sont les jumeaux que les tests
  de la grille éprouvent, qui partent avec les règles.

**La sonde** prend aussi, sans `sys.monitoring` (Python 3.11, celui de
GitHub), `sys.setprofile` : la suite était rouge sur ses tests et sur celui
du budget ; et elle relance ses événements à la fin d'un sondage, sans quoi
une règle relevée une fois ne l'était plus au sondage suivant.

**Vérifié.** Les deux tables d'âges rendent la même chose que les chargeurs
du scénario 1, mois par mois, de 1870 à 2069 ; le salaire moyen du pont est
celui de `carriere.salaire_moyen_annuel` au bit près, de 1900 à 2119, sous
les paramètres de référence et ceux de la projection. Le script, avant et
après, sur six grilles (`reference`, `personnes`, `melees`, `femmes`,
`interruptions`, `salaires`) : sorties identiques à l'octet, hors des
secondes mesurées. `ensemble` et `population` ne tenaient pas en mémoire
deux fois à la fois dans un conteneur de 15 Go (deux courses tuées), ni sous
la sonde en un seul processus en deux heures.

**Tests.** `tests/test_grille_large.py` : la sonde ne relève rien dans les
âges, les attentes, `au_smic` et `donnees_population` (âges de la loi de
2010) ; un cas type que le portage ne date pas est refusé ; vus rouges puis
verts. `tests/test_sonde_moteur_python.py` : la sonde sans `sys.monitoring`,
et d'un sondage à l'autre, vus rouges puis verts. `test_grille_large.py`,
`test_recours_aspa.py`, `test_part_minimum_contributif.py` et
`python -m pytest -m rapide` : verts.

**Reste** : le point 3, les replis de `avantages` et de `castypes`, et
`facteurs_depense.dates_a_l_age_legal`.
