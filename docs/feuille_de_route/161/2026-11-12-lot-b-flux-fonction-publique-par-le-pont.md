# Lot B, deuxième session : `flux_fonction_publique.py` demande ses liquidations au portage, le pont rend le journal de la liquidation

L'étude des trois cas types statutaires face aux départs que décrit le jaune
pensions ne fait plus rien dater, bâtir ni simuler au moteur Python. Ses
sorties sont identiques à l'octet. Rien n'est gardé en correctif, et rien
n'attend une décision du propriétaire.

**Ce que l'étude lisait du moteur Python.** `depart_en` appelait
`calculer_cas_types` sur une case à la fois (ligne 221 d'alors), et lisait
de la comparaison rendue : l'année et l'âge du départ, la durée validée du
scénario 1, et, dans le journal de l'échéancier, la première pension du code
des pensions de la liquidation avec le traitement de l'article L. 15 qui la
liquide (`pension_et_traitement`). Aucune demande du pont ne rendait ce
dernier couple.

**Ce qui change.**

- `src/retraite_notionnelle/pont.mjs`, `departsDesCas` : une lecture de plus,
  `"lire": "liquidation"`. Le cas y est une case de la grille, que le droit
  écarte comme `carriere_de_la_grille` l'écartait (`verifierLaCase`, sous le
  même motif) ; son départ porte de plus son année et ce que le journal garde
  de sa liquidation (`liquidationAuJournal`, une fonction à part) : chaque
  pension du code des pensions, `[regime, montant, traitement]`, dans l'ordre
  du journal. Les deux lectures que `scripts/grille_large.py` fait, `"age"`
  et `"depart"`, rendent ce qu'elles rendaient.
- `src/retraite_notionnelle/pont.py`, `departs_des_cas` : sous cette lecture,
  `"annee"` en entier et `"liquidation"` en flottants s'ajoutent au départ.
- `scripts/flux_fonction_publique.py` : `Departs` lit les départs au portage,
  sur le paquet des données du jour, comme le coût bâtit sa grille ;
  `departs_annonces` lui annonce d'une seule demande les générations d'où la
  recherche de chaque année peut passer, deux de part et d'autre de celle
  d'où elle part. `depart_en` garde sa marche, génération par génération, sur
  ce que `Departs` a lu ; `pension_et_traitement` et `mesures_du_cas` lisent
  un `Depart` au lieu d'une comparaison. Le stock ne change pas : il passait
  déjà par la grille du coût (`cout._pensionnes`).
- `castypes.calculer_cas_types` ne change pas. Il n'a plus d'appelant hors
  des tests (`grep` sur `scripts/` et `src/`).

**Les tests, écrits d'abord et vus rouges**, dans
`tests/test_flux_fonction_publique.py`.

- `test_le_pont_rend_le_journal_de_la_liquidation_au_bit_pres_du_moteur_python`,
  la confrontation, avant le branchement : les trois cas types sur les 29
  générations du coût et les trois que l'étude fait partir en 2025, sous les
  deux conventions. Les 182 cases que le moteur Python simulait rendent la
  même année, le même âge, type compris, la même durée et les mêmes pensions
  du code des pensions, au bit près ; les 10 qu'il écartait le sont sous le
  même motif. Vu rouge : le pont n'écartait aucune case.
- `test_l_etude_mesure_ses_cas_types_au_portage_sans_le_moteur_python` : la
  génération et les cinq mesures de chaque cas type, en 2025 sous les deux
  conventions puis chaque année de 2016 à 2025, égales à ce que la marche de
  l'étude rendait au moteur Python, les jumeaux empêchés
  (`outils_pont.empecher_les_jumeaux_du_cout`). Vu rouge : « un jumeau Python
  date, bâtit ou simule la grille du coût ».

Aucun des deux n'ouvre `pont.par_le_jumeau()` : le moteur Python qu'ils
confrontent se calcule sans aiguillage. Ils partent avec lui, au lot F.

**Les chiffres, inchangés.** `python scripts/flux_fonction_publique.py
--json`, la mémoire des calculs coupée (`CALCULS_SANS_MEMOIRE=1`), avant et
après : le fichier JSON et le texte imprimé sont identiques à l'octet — le
flux de 2025, les dix années, le stock. Onze secondes avant, neuf après.
L'étude fait une demande au pont par mesure, de 15 puis de 42 cases, et
aucune de plus : la marche ne sort pas des générations annoncées. Toute
l'étude, stock compris, tourne les jumeaux empêchés.

**Ce qui n'est pas vérifié, ou diffère.**

- Le journal ne rend que les liquidations inscrites avec leur résultat
  entier. Celle d'un régime que l'activité après le départ ouvre s'inscrit
  autrement, sans ses plafonds : la lecture la passe. Aucun cas type de la
  grille n'en a ; l'étude Python, elle, aurait levé une erreur en la
  rencontrant avant une pension du code des pensions.
- `calculer_cas_types` simulait les six scénarios, et écartait une case dont
  l'un échouait. La lecture ne liquide que le scénario 1, le seul que l'étude
  lit. Sur les 192 cases confrontées, les écartées sont les mêmes.

**Ce qui reste.** Le lot B continue par `scenarios_meres.py` avec
`cout_avantages.py --par-carriere`, puis `mortalite_population.py` ; la
datation de `cycle_de_vie.py`, que la première session n'a pas faite, reste
aussi.

**Tests.** `python -m pytest -m rapide` (4 794 passés, 64 sautés) ; les
fichiers de la zone, `test_flux_fonction_publique.py`,
`test_age_conjoncturel.py`, `test_pont.py` et `test_outillage.py` (192
passés) ; les deux lectures de `test_grille_large.py` par le portage ; les
essais de `tests/js/`.
