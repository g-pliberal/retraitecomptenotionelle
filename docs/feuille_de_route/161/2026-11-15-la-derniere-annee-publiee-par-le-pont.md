# La dernière année publiée d'un point par le pont : le coût la demande au moteur JavaScript, d'un lot

La classe du coût qui dit ce que devient une pension liquidée
(`RevalorisationServie`, `revalorisation_servie.py`) cherchait elle-même la
dernière année dont la valeur de service d'un point est publiée, au bout de
ses fusions. Elle la demande désormais au portage, et ne lit plus ni les
valeurs des points ni leurs fusions. Aucune règle, aucune donnée, aucun
témoin n'a bougé.

**La consigne.** Le point 2 de la note de décision 0008 : la voie 1 de
`2026-11-12-la-revalorisation-servie-dans-un-module-du-cout.md`, « Les
quatre tables ».

**Ce qui change.**

- `moteur/js/revalorisation.js` exporte `derniereValeurPubliee`.
- Le pont du droit la sert sous le nom
  `revalorisation.derniere_valeur_publiee` (`pont.mjs`,
  `FONCTIONS_DE_L_HISTOIRE_DU_DROIT` ; `pont.py`,
  `LECTURES_DE_L_HISTOIRE_DU_DROIT`, un entier ou `None`).
- La classe la demande d'un seul lot pour chaque barème du catalogue, codes
  et barèmes empruntés (`points_de`), à la première lecture d'un régime en
  points ; un barème hors du lot se demande seul. Une demande de plus par
  coût. Le champ `_moteur` part.
- L'exemplaire Python quitte `revalorisation_servie.py`, module sans jumeau,
  pour `revalorisation.py`, sous le nom `derniere_valeur_publiee` : c'est le
  jumeau de la fonction du portage, que `PensionServie` lit encore, et qui
  part avec ce module au retrait. La clôture le compte ainsi parmi les
  paires, au lieu qu'il y échappe.

**Les tests.** `test_le_pont_sert_la_derniere_annee_publiee_d_un_point`
(`tests/test_pont.py`), vu rouge avant le code : six barèmes, valeurs posées
depuis `valeurs_point.csv` et `conversions_points.csv` (l'Arrco, l'Agirc et
l'UNIRS remontent à 2026 par leurs fusions ; le régime général et un code
inconnu, `None`), le jumeau refaisant chaque appel. Le test du lot de
l'histoire du droit remplace aussi les lectures des valeurs et des fusions
des points par une erreur, et attend le lot de plus ; la confrontation au
bit compte ce lot. `-m rapide` : 5 079 réussis ; les fichiers de la zone
(`test_pont`, `test_oracle`, `test_destinie`, `test_estimation_officielle`,
`test_verification`, `test_revalorisation`) : 525 réussis.

**Ce qui reste.** Les étapes suivantes de l'action, dans l'ordre de
`2026-11-13-les-decisions-du-proprietaire.md` : le § 3 du README d'abord.
