# Le tri des scripts et des modules : ce que chacun exécute encore du moteur Python

Action 161, après `2026-11-16-la-decote-sans-plafond-en-donnees.md`. Aucune
règle, aucune donnée, aucun témoin n'a bougé. Le moteur Python et ses
règles restent en place : leur retrait attend l'accord du propriétaire.

## La méthode : une sonde, plutôt que les imports

Lire les imports ne suffit pas : plusieurs modules gardent deux chemins, l'un
au portage, l'autre « en Python sinon » (`avantages.decomposer`), et
importent les règles sans les exécuter. `scripts/sonde_moteur_python.py`
lance un script tel quel, sous `sys.monitoring`, et relève chaque fonction des
fichiers de règles qui s'exécute — `droit/`, `moteur/`, `scenarios/`,
`echeancier.py`, `journal.py`, `pilote.py`, `carriere.py`,
`revalorisation.py`, `simulateur.py` —, hors de l'import des modules et hors
des chargeurs de données du simulateur. Elle a son test
(`tests/test_sonde_moteur_python.py`).

    python scripts/sonde_moteur_python.py --json scripts/stock_age_legal.py

Les 29 scripts qui bâtissent `Simulateur(...)` y sont passés, sans argument,
sur un clone neuf (sans mémoire des calculs, d'où les temps). Les modules de
`src/` (`memoire`, `leviers`, `facteurs_depense`, `controle_eacr`,
`controle_ancetre`, `contexte`) n'ont pas de point d'entrée : ils sont sondés
à travers les scripts qui les appellent.

## Ce que la sonde a trouvé

**1. Rien du moteur Python.** `age_conjoncturel`, `age_depart_csp`,
`cout_avantages`, `cycle_de_vie`, `garantie_par_sexe`,
`lectures_du_modele`, `part_minimum_contributif`, `mesures_prose` (une
bibliothèque, sans `main`), `estimation_officielle --modele`. Ils ne lisent
du simulateur que ses données.

**2. Seulement des chargeurs et des types logés dans des fichiers de
règles.** `controle_eacr`, `cout_age_depart`, `facteurs_depense`,
`flux_fonction_publique`, `indexation_scenario_6`, `mesures_accueil`,
`mortalite_population`, `proposition_prospective`, `sensibilite_comptes`,
`solde_fusion`, `stock_age_legal`, `tableau_de_bord`. C'est le chemin du coût
(`cout.calculer_cout`, `memoire.cout`), et tous y lisent les mêmes choses :

- `carriere.Carriere` et `AnneeCarriere`, types que le pont échange ;
- `revalorisation.RevalorisationsPensions` (le chargeur des
  revalorisations, logé dans le jumeau de la revalorisation servie) ;
- `scenarios.actuel.MinimumVieillesse` : le barème de l'ASPA, que le coût
  et l'effet retour lisent (`plafond`, `plafond_couple`) ;
- `simulateur.Simulateur.univers_de_la_demande`, les variantes d'une étude
  que le pont transmet ;
- `droit.liquidation.APPELS_DECLARES`, une constante que le tableau de bord
  cite.

Aucun ne calcule : au retrait, ces chargeurs passent sous `donnees/` et les
types restent (note de décision 0006). C'est la première chose à faire
avant de couper les règles, sans quoi la coupe emporterait le coût.

**3. Un vrai calcul en Python.**

- `budget_calcul` mesurait le temps du moteur Python : **réglé dans cette
  étape**, il ne mesure plus que le moteur du site
  (`scripts/budget_calcul.mjs`).
- `scenarios_meres` : `carriere.salaire_moyen_annuel` (avec
  `indice_salaire_moyen`, `ancrage_salaire_moyen`), que le pont sert déjà
  (`pont.droit`, `carriere.salaire_moyen_annuel`). Le reste de ce qu'il
  exécute est l'accès aux types du résultat (`Comparaison`,
  `ResultatNotionnel`, `GarantieVieillesse`, `Journal`).
- Hors du chemin sans argument, mais à la lecture : `estimation_officielle`
  et `fetch/destinie_2.py` importent `salaire_moyen_annuel` ;
  `grille_large` appelle `simulateur.carriere_parcours`,
  `simulateur.echeancier(…)` et lit `scenarios.actuel.AgesOuverture`,
  `AgesAnnulationDecote` ; `recours_aspa` lit
  `scenario_actuel.minimum_vieillesse` (le barème, donc un chargeur) ;
  `lectures_du_modele` appelle `simuler` sur l'un de ses chemins. Dans
  `src/` : `avantages._decomposees_en_python` et `_voisines_en_python`, le
  repli quand la grille ne se date pas au portage ;
  `facteurs_depense.dates_a_l_age_legal`, qui lit
  `scenario_actuel.ages_ouverture` ; `castypes.calculer_cas_types`, qui simule par le
  simulateur Python (`simulateur.simuler`).

**4. Pas sondés ici.** `grille_large`, `lectures_decision_29`,
`mesurer_surcote`, `recours_aspa` : plus de 25 minutes sans mémoire, arrêtés.
`fetch/destinie_2.py` et `fetch/trajectoire.py` : ils lancent `wsl`, absent
d'un conteneur. `estimation_officielle` sans argument : il en demande.

## Ce qui reste

Une étape par session, dans cet ordre :

1. `scenarios_meres`, `estimation_officielle`, `fetch/destinie_2.py` :
   `salaire_moyen_annuel` demandé au pont.
2. `grille_large` : ses carrières et ses échéanciers au portage, ses âges
   lus aux données ; le sonder avec la mémoire chaude.
3. Les replis « en Python sinon » de `avantages` et de `castypes`, et
   `facteurs_depense.dates_a_l_age_legal` : retirés, ou demandés au pont.
4. Les chargeurs du groupe 2 sous `donnees/` (`RevalorisationsPensions`,
   `MinimumVieillesse`, `APPELS_DECLARES`, `univers_de_la_demande`), puis
   un simulateur de données seules, que la façade des tests prend aussi.
5. Le retrait des règles d'un bloc, avec l'accord du propriétaire.

Chaque étape repasse ses scripts à la sonde, qui doit rendre `[]` hors des
chargeurs du groupe 2.

**Tests.** `tests/test_sonde_moteur_python.py` (5, sur un paquet factice, pour ne pas entrer lui-même dans le moteur) : vu rouge, puis vert. `python -m pytest -m rapide` : vert.
`test_outillage.py -k budget` : vu rouge (le script mesurait encore le
Python), puis vert.
