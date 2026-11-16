# Le simulateur de données seules : ses chargeurs et les variantes d'une étude, hors du moteur Python

Action 161, fin du point 4 de « Ce qui reste » de
`2026-11-16-le-tri-des-scripts-et-des-modules.md`. Aucune règle, aucune
donnée, aucun témoin n'a bougé.

- `donnees/simulateur.py` : `SimulateurDeDonnees`, ce que le `Simulateur`
  chargeait sans règle, déplacé tel quel — son constructeur et ses
  `variantes`, ses séries, sa mortalité, ses deux courbes de taux, son
  catalogue, ses effectifs, ses distributions, les revalorisations, les
  univers de la proposition, `univers_de_la_demande` (les variantes d'une
  étude que le pont passe au portage, calculées par le noyau) et
  `pour_la_projection`, qui rend un simulateur du même type. Il n'importe
  aucun module du moteur Python. Ses affiliations, logées avec leurs règles
  de routage dans `carriere.py` (la date d'entrée, les régimes de chaque
  statut), s'y lisent à la demande, par un import différé : les déplacer
  serait couper une règle, et non un chargeur.
- `simulateur.py` : `Simulateur` en hérite, sans rien redéfinir de ces
  chargeurs ; il ne garde que ses règles.
- `memoire.cout` et `memoire.grille_du_cout` bâtissent un
  `SimulateurDeDonnees` ; `cout.py` l'annonce dans ses signatures et
  n'importe plus `simulateur.py`. `memoire.avantages` garde le `Simulateur` :
  le coût des avantages n'a pas été sondé ici.
- La façade des tests (`tests/facade.py`) lit ses données sur un
  `SimulateurDeDonnees`. Le simulateur Python ne lui sert plus qu'à lire le
  type d'une table du moteur, dont elle tire la signature et le rendu d'une
  méthode (`_type_de_la_table`, une fois par jeu de paramètres) : une table
  s'y recouvre selon les paramètres, son type se lit sur l'instance.
- La sonde (`scripts/sonde_moteur_python.py`) n'excepte plus que
  `Simulateur.__init__` : les chargeurs sont hors des fichiers de règles.

**Vérifié.** Le coût de la page, `memoire.cout()` sans mémoire, sérialisé
(`pickle`) avant et après : même empreinte SHA-256, sur deux tirages avant.
La sonde, sur `solde_fusion` : seules des méthodes du type `Carriere`.

**Reste.** Le retrait des règles (point 5), avec l'accord du propriétaire.
Avant lui, sans attendre : les scripts des groupes 1 et 2 du tri, et
`memoire.avantages`, peuvent bâtir un `SimulateurDeDonnees` au lieu du
`Simulateur`, chacun repassé à la sonde ; les chargeurs logés dans
`scenarios/actuel.py` attendent la note de décision 0009.

**Tests.** `tests/test_chargeurs_a_part.py` (3 de plus, rapides) : le
simulateur de données se bâtit, se lit, se projette et passe ses variantes
sans importer le moteur Python ; le `Simulateur` en hérite sans redéfinir
ses chargeurs ; la façade et la mémoire ne bâtissent plus le simulateur
Python, et le coût n'importe plus `simulateur.py`. Vus rouges, puis verts.
`test_sonde_moteur_python.py` suit l'exception réduite. `python -m pytest -m
rapide` (5 407), `test_pont.py`, `test_facade.py`,
`test_proposition_prospective.py`, `test_carte.py` : verts.
