# Les populations de la Cnav au portage : le panorama de la DREES quitte le moteur Python

Action 161, étape 9l, après `2026-11-16-les-donnees-et-le-solde-a-la-facade.md`.
Aucune règle du droit, aucune page n'a bougé ; le paquet gagne deux tables, et
les agrégats restent identiques à l'octet. `FICHIERS`
(`test_fichiers_sur_le_moteur_python.py`) passe de 9 à 8 : c'était le dernier
fichier de la troisième vague.

## Ce qui est fait

- **Les types de pension de la Cnav au portage.** Normale, pour inaptitude,
  d'ex-invalide : la Cnav publie leur espérance de vie de 62 à 85 ans, et le
  Python leur cale un facteur de mortalité par tranche d'âge
  (`facteurs_par_age`). Le paquet porte désormais ces espérances et ces
  facteurs (`populations.esperances_par_age`, `populations.facteurs_par_age`,
  `construire_donnees._populations`). `moteur/js/mortalite.js` les lit
  (`facteursParAge`), ou les recalibre à défaut (`_caler`, portage de la
  bissection), et `survieAnnuelle` applique à chaque cellule le facteur de son
  âge, comme le Python. `facteurPopulation` refuse une population publiée à
  plusieurs âges, comme son jumeau.
- **Les tests.** `tests/js/populations-cnav.test.js` vérifie, d'après le CSV
  de la Cnav, que la table corrigée rend chaque espérance publiée, que les
  facteurs viennent du paquet ou soient recalibrés. `test_jumeaux_au_bit.py`
  confronte au bit près `facteurs_par_age`, `_caler`, `_publiee_par_age` et
  les courbes des populations de la Cnav ; l'écart déclaré sur
  `populations` (21 au portage, 24 en Python) est levé, et la liste des
  fonctions gardées (`scripts/jumeaux_gardees.yaml`) les déclare.
- **La façade sert `mortalite.survie` et `mortalite.esperance_residuelle`**
  (`pont.MORTALITE_DE_LA_FACADE`), avec cinq appels confrontés au jumeau
  (`test_facade_jumeau.py`), et trois courbes de la Cnav de plus.
- **`test_controle_drees_panorama.py`** quitte le moteur Python. Les carrières
  de la grille, que le test datait par le pilote Python
  (`CasType.construire`), sont datées et bâties par le portage, d'une seule
  demande (`pont.carrieres_de_la_grille`, comme `cout._grille_batie`), pour
  chaque cas type des générations 1940 à 1980 : la grille va de cinq en cinq,
  et les fiches lisent 1950, 1953, 1954 et les départs de 2024 (le militaire
  né en 1975 en est). Vérifié égal, champ par champ, à ce que bâtissait le
  pilote Python sur les générations de la grille. L'âge d'ouverture de 1953
  se lit dans `age_ouverture_requis.csv`, au mois près.

## Ce qui reste

Huit fichiers, tous de la quatrième vague ou du coût : `test_moteur.py` et
`test_pont.py` (une autre session), `test_avantages.py`, `test_cout.py`,
`test_cout_age_depart.py`, `test_grille_large.py`, et les deux confrontations
de la façade, qui partent avec le moteur Python. Voir
`2026-11-16-la-quatrieme-vague-a-mi-chemin.md`, « Ce qui attend le coût ».

**Tests.** `python -m pytest -m rapide` : 5 379 passés, 64 sautés.
`test_controle_drees_panorama.py`, `test_facade.py`, `test_facade_jumeau.py`,
`test_jumeaux.py`, `test_jumeaux_au_bit.py`,
`test_fichiers_sur_le_moteur_python.py` et `node --test tests/js/` : verts.
