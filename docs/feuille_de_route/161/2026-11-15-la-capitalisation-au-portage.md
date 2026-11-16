# La capitalisation au portage : les identités du pilier éprouvées sur le constructeur du site

Action 161, quatrième vague, après
`2026-11-15-la-remuneration-et-la-limite-d-age-a-la-facade.md`. Aucune règle,
aucune donnée, aucun témoin n'a bougé. `test_capitalisation.py` quitte
`FICHIERS`.

## Ce qui est fait

- **`tests/js/capitalisation.test.js`**, neuf, que `test_web.py` lance avec
  les autres essais de node : les onze tests de `test_capitalisation.py` qui
  bâtissaient le constructeur Python à la main y passent, sur
  `ConstructeurCapitalisation` du portage. L'adossement et ses maturités
  cotées ; l'allocation sans effet sous les anticipations pures (quatre
  règles, l'ancienne échelle comprise, passées par l'argument `repartir` du
  constructeur, au lieu de remplacer `repartition` dans le module Python) ;
  l'adossement qui domine sous une prime de terme ; la forme close du capital
  sur une courbe plate, sans frais et avec ; le frais sur la réserve de la
  rente ; la baisse des frais sur les nouveaux dépôts et la convergence du
  stock ; l'espérance transmise refaite à la main. Les attendus sont ceux du
  Python, écrits de tête.
- **La séparation des deux courbes** (`courbeTaux`, `courbeTauxPilier`) se
  vérifie sur le simulateur du portage, au lieu du Python.
- **`test_le_reglage_des_taux_est_ce_qui_fait_peser_l_allocation`** est
  retiré : il remplaçait `repartition` dans le module Python, que le portage
  ne voit pas ; ce qu'il disait est tenu par les deux tests d'allocation de
  l'essai neuf et par le contrôle de l'affirmation de la page
  (`test_affirmations.py`, `capitalisation.construire`).
- Le reste du fichier — la courbe, un chargeur ; les paramètres de frais ;
  les piliers des simulations — passe au simulateur de la façade, tel quel.

## Ce qui reste de la vague 4

`test_emploi_retraite.py`, `test_independants.py`, `test_moteur.py`,
`test_pont.py` ; puis, après le coût, `test_cout.py` et
`test_grille_large.py`.

**Tests.** `test_capitalisation.py` (39), `node --test
tests/js/capitalisation.test.js` (11), `test_fichiers_sur_le_moteur_python.py` :
verts ; `python -m pytest -m rapide` avant l'envoi.

## La suite rouge qui a suivi, et sa réparation

`docs/methodologie.md` tient « à 0,01 € près » par
`tenu(test_sous_les_anticipations_pures_l_echelle_est_sans_effet)`, que la
vérification de la prose cherche dans les fichiers Python de `tests/` : le
retrait du test a rougi la fabrique de GitHub. Le test revient dans
`test_capitalisation.py`, sur le portage : les quatre allocations, décrites
en données, passent au pont (`capitalisation.construire`), et leurs capitaux
s'égalent à un centime près.
