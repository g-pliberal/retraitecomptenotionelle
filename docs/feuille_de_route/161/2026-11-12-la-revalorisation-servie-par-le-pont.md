# La revalorisation servie par le pont : la classe Python lit les séries du moteur JavaScript

La règle que les systèmes notionnels prêtent aux pensions servies n'a plus
qu'un exemplaire, `RevalorisationServie` de `moteur/js/revalorisation.js`.
La classe Python du même nom ne calcule plus : elle demande ses séries au
pont, une fois par jeu de paramètres, et les lit. Le coût demande aussi au
portage ce que l'indexation rend à ses cotisations sous une variante
démographique. Le coût de référence et celui d'une variante sont identiques
au bit, le paquet et les témoins à l'octet. L'histoire du droit, que la
classe porte sans jumeau, n'est pas jointe : c'est l'étape d'après. Rien
n'est gardé en correctif, et rien n'attend une décision du propriétaire.

**La demande.** La ligne « la revalorisation servie » de la table des
décisions du 12 novembre (`2026-11-12-les-decisions-du-proprietaire.md`), la
session C3 de la note de la question 1
(`2026-11-12-question-1-la-zone-grise.md`) : les séries par le pont, la
classe Python réduite à leur lecture, `Indexation.coefficient` sur la même
série. La note de décision 0007 dit que la confrontation écrite à ce passage
tient lieu de relecture de la revalorisation servie et de l'indexation.

## Ce qui change

- **Le pont** (`pont.py` et `pont.mjs`, un bloc à part des deux côtés, sous
  son titre) : deux demandes de plus. `revalorisation_servie` bâtit la
  classe du portage sous les paramètres du simulateur, d'une première année
  à une dernière. Elle rend ses séries (`pont.series_servies`) : l'index du
  compte et la valeur de service convenue de chaque régime, en euros
  constants, année par année, et le régime convenu de chaque régime du
  catalogue. Elle rend aussi, à la demande, ce que rend chaque lecture de
  la classe du portage (`pont.revalorisation_servie`), pour les confronter.
  `indexation` rend le taux d'une année ou le rendement cumulé d'une
  cotisation (`pont.indexation`), par lot.
- **La classe Python** (`revalorisation.py`, de 1 983 à 1 929 lignes) : son
  constructeur ne bâtit plus l'index ni la valeur de service, il les
  demande. `regime_convenu` lit une table au lieu de remonter les fusions.
  Trois lectures gardent leurs lignes : `coefficient` et
  `coefficient_points`, le rapport de deux valeurs d'une série, et
  `coefficient_stock`, la règle du stock à la bascule. Ce que le coût seul
  lit n'a pas bougé : `coefficient_historique` et ses règles,
  `coefficient_nominal`, `pour_la_proposition`, `regime_de_tete`.
- **Le coût** (`cout.py`) : `_sous_la_demographie` demande d'un seul lot ce
  que l'indexation a rendu à chaque cotisation de sa grille
  (`_rendements_des_cotisations`), chaque couple (année, liquidation) une
  fois ; `_capitaux_sous_la_variante` reçoit ce rendement au lieu du
  simulateur. Ses huit appelants de la classe ne changent pas.
- **Le portage** (`revalorisation.js`) : aucune ligne de code. Le
  raisonnement de la classe, que l'en-tête renvoyait au Python, y est
  reporté en commentaires, et l'en-tête dit ce qui lui reste de lecteur
  Python.
- **Les en-têtes** de `pont.py`, de `pont.mjs` et de `moteur/indexation.py`
  disent qui calcule quoi.

## Deux choix de la session

**La règle du stock se dit tenue, elle ne se rend pas en séries.** La note
de la question 1 laissait le choix. Une série par régime du stock ne suffit
pas : une pension liquidée après la bascule suit la règle du compte, et ce
test resterait en Python. Il faudrait une table de 130 années sur 130, par
régime du stock. Les dix lignes restent donc des deux côtés, confrontées.

**Le rendement d'une cotisation se demande couple par couple, non comme un
rapport de deux valeurs d'une série.** `Indexation.coefficient` multiplie les
taux un à un depuis l'année qui suit la cotisation. Le rapport de deux
valeurs d'un produit cumulé donnerait le même nombre au dernier bit près
seulement, et les agrégats d'une variante démographique cesseraient d'être
identiques. Le lot porte donc les couples eux-mêmes.

## Un comportement change

Le moteur Python d'une carrière lit, lui aussi, les séries du portage : sa
« pension d'aujourd'hui » des systèmes notionnels passe par
`Simulateur.revalorisation_servie`, qui est la même classe. Sous
`pont.par_le_jumeau()`, une demande part donc encore au portage, celle des
séries. `test_sous_le_jumeau_le_cout_simule_sa_grille_en_python` coupait
node pour le prouver ; il vérifie maintenant que cette demande est la seule.
Le jumeau ne confronte donc plus l'index de façon indépendante : la
confrontation écrite avant la coupe l'a fait, puis est partie avec le calcul.

## Les lots, mesurés

Un coût de référence, sans mémoire : 341 demandes au pont au lieu de 340,
celle des séries, 0,03 seconde. Sous la fécondité basse : 342, la seconde
étant le lot de l'indexation, 3 760 couples en 0,24 seconde.

| | avant | après |
|---|---:|---:|
| le coût de référence, deux mesures | 30,4 et 29,7 s | 28,9 et 29,5 s |
| le coût sous la fécondité basse, une mesure | 29,4 s | 27,5 s |

## Ce qui est vérifié

*En faisant tourner le code.*
- Avant la coupe, sous vingt-quatre jeux de paramètres — chaque règle
  d'indexation, son lissage, son plancher, le préfinancement, les deux
  règles du stock, trois bascules, trois scénarios de projection, l'emploi
  constant, le simulateur de la page Coût — : l'index et la valeur de
  service que le pont rend, de 1941 à 2070, au bit ceux que le jumeau
  bâtissait. Cette partie de la confrontation, commitée avec la demande au
  pont, est partie avec le calcul.
- L'indexation, sous les mêmes jeux : le taux de chaque année de 1941 à
  2070, avec son terme et ses trois séries, et 952 rendements cumulés,
  25 968 comparaisons au bit entre `indexation.py` et `indexation.js`.
- Les quatre lectures que le Python garde, contre celles du portage : 62 235
  comparaisons au bit, sur une grille qui déborde la série des deux côtés et
  sur chaque régime du catalogue. La valeur de service n'est convenue que
  sous les conventions du COR : trois jeux l'éprouvent, ce qu'aucun essai
  n'avait fait.
- Un écart d'un dernier chiffre posé dans le jumeau rougit chaque
  confrontation, lecture par lecture (essai jetable, hors du dépôt).
- Le coût de référence et celui de la fécondité basse, comptes compris,
  écrits nombre par nombre par un essai jetable : 25 353 nombres chacun, la
  même empreinte avant et après.
- Le paquet refait par `python scripts/construire_donnees.py`, en 3 minutes
  29 : `data/derive/agregats.json`, `moteur/donnees.json`,
  `data/derive/equilibre.json` et les calibrations, identiques à l'octet.
  Les témoins refaits par `construire_temoins.py` : aucun déplacé.

*Posé à la main, depuis les données.* Le coefficient de 2022 à 2023,
1,05625 / 1,04875, la masse salariale sur les prix ; le préfinancement de
1,6 %, 1,016 puissance dix en dix ans ; la valeur de service de
l'Agirc-Arrco de 2026 à 2040, 0,9469 ; les quatre cas de la règle du stock ;
le taux de 2023 sous trois règles ; le rendement d'une cotisation de 2021
arrêtée en 2023, 1,07838 × 1,05625.

*Non mesuré.* Les six autres coûts que la fabrique fige, et les quatre
autres variantes démographiques, ne sont vérifiés que par le paquet
identique. Le coût sur des données d'ailleurs : voir plus bas.

## Tests

Dans `tests/test_pont.py`, sept tests neufs, tous de la suite rapide :

- le pont rend les séries, lit la classe du portage, rend les taux de
  l'indexation — valeurs posées à la main, types relus, refus d'une lecture
  inconnue ;
- `test_l_indexation_du_portage_est_celle_du_jumeau_au_bit` et
  `test_les_lectures_python_de_la_revalorisation_servie_sont_celles_du_portage`,
  les deux confrontations ;
- la classe Python lit des séries posées à la main, sans appeler
  l'indexation du Python, et s'arrête sans node ;
- le coût demande ses rendements d'un seul lot, et s'arrête sans node.

`tests/test_cout.py` suit la signature de `_capitaux_sous_la_variante`.

Chaque test neuf a été vu rouge pour la raison attendue. Sous
`PRESOMPTIONS_DECALEES=1`, cinq passent ; la suite saute elle-même les deux
derniers, et le test du levier retouché (« le portage lit ses présomptions
dans le paquet »). La suite rapide, 4 895 passés ; les fichiers du coût et
de la zone, 1 957 passés en quatre lancements, le premier avant la retouche
du test du levier, relancé seul ensuite : `test_cout.py`,
`test_facteurs_depense.py`, `test_affirmations.py`,
`test_controle_drees_panorama.py`, `test_agregats.py`, `test_pont.py` en
entier, `test_revalorisation.py`, `test_moteur.py`,
`test_indexation_programme.py`, `test_effet_retour.py`,
`test_bilan_compte.py`, les deux contrôles, `test_grille_large.py`,
`test_indexation_scenario_6.py`, `test_facade_jumeau.py`, les confrontations
légères, la carte.

## Ce qui reste

1. **L'histoire du droit, l'étape d'après.** `_nominal` appelle encore cinq
   règles du moteur Python, mois par mois : `liquider.valeur_du_point`,
   `RevalorisationsPensions.generale` et `retenues`,
   `minimum_garanti.ratio_point_indice`, `conversions_points.echelle`.
   `pont.droit` ne sert que la première. Elle n'est pas jointe ici : il
   faut déclarer les quatre autres avec leur confrontation, refaire
   `_nominal` et `_historique` pour qu'ils demandent par lot — `echelle` se
   demande aujourd'hui couple par couple, au fil des lectures —, puis sortir
   de `revalorisation.py` la part du coût, que neuf fichiers importent,
   tests compris.
   C'est une étape entière.
2. **Quatre lectures restent des deux côtés**, à déclarer à la clôture
   (`2026-11-12-question-4-la-cloture.md`) : `coefficient`,
   `coefficient_stock`, `coefficient_points` et `regime_convenu`, leur
   lecteur Python dans `revalorisation.py`, leur confrontation dans
   `tests/test_pont.py`.
3. **`moteur/indexation.py` part avec le moteur Python.** Le lisent encore
   `moteur/compte.py`, `scenarios/notionnel.py` et le simulateur, et deux
   scripts : `scenarios_meres.py` (ligne 304) et, par `cumuls`,
   `construire_tableaux_md.py` (ligne 95).
4. **La suite de l'action** : les règles de `droit/` à la façade des tests,
   les études, le retrait.

## Vu sans le traiter

- **Sur des données d'ailleurs** (`Parametres(racine_donnees=…)`), le pont
  lance node à chaque demande. Cette étape en ajoute une par classe bâtie,
  et une par coût sous une variante démographique.
- **Cinq commentaires de `impot-revenu.js` renvoient au Python**, comme la
  note de l'impôt le dit déjà.
- **Une phrase n'a pas été reportée dans le portage** : le coefficient
  vaudrait « ×1,15 au bout de vingt ans de projection — 2,45 % contre
  1,75 % ». Mesuré de 2050 à 2070 sous les réglages de référence : 1,05, la
  masse salariale projetée portant l'emploi, qui baisse. La phrase datait
  d'avant la trajectoire d'emploi du COR.
- **La fiche `proposition/indexation_du_compte.yaml`** ne nomme pas
  `tests/test_pont.py` parmi ses tests.

**Un chiffre de la prose bouge.** Le poids du moteur que le README annonce
au lecteur passe de 934 à 936 Ko compressés : ce sont les explications de la
classe reportées dans les commentaires de `revalorisation.js`, que le
navigateur charge avec le moteur.

**Ce qui ne change pas.** Aucune règle, aucune donnée, aucun témoin, aucun
agrégat, aucun chiffre du site ; aucune règle du scénario 1 ; aucune garde.
