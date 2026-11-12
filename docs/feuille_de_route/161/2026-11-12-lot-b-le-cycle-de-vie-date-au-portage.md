# Lot B : `cycle_de_vie.py` date ses cases au portage, plus au pilote Python

**La pertinence, vérifiée avant d'agir.** Sur 7d8d67e, la tête de `main` le
12 novembre 2026.

1. *L'étape était-elle faite ou entamée ?* Non. Le dernier commit à toucher
   `scripts/cycle_de_vie.py` était celui de la note de la question 3 ; la
   première session du lot B l'avait laissée de côté, et l'avait dit
   (`2026-11-12-lot-b-deux-etudes-par-le-pont.md`, « Ce qui reste »).
2. *Où l'étude datait-elle en Python ?* En trois endroits, ceux que la note
   de la question 3 cite : `_cases`, par `carriere_de_la_grille`, pour la
   grille et ses étages ; `balayer`, par `age_liquidation_pour`, pour les
   balayages de `--ages` ; `equilibres`, par `age_liquidation_pour`, pour les
   âges d'équilibre. Chacun faisait tourner le pilote Python, qui bâtit et
   liquide la carrière pour chercher son âge.
3. *Le pont rend-il déjà ce qu'il faut ?* Oui, sans demande nouvelle : ni
   `pont.py` ni `pont.mjs` ne changent. `castypes.cases_de_la_grille` rend
   les options de chaque case datée, et écarte celles que le droit écarte
   (`pont.carrieres_de_la_grille`) ; `castypes.ages_de_la_grille` rend l'âge
   de chaque case (`pont.ages_de_depart`). La table du paquet et deux études
   s'en servaient déjà.

**Ce qui change.** `scripts/cycle_de_vie.py` seul.

- `_cases` lit `cases_de_la_grille` ; `balayer` et `equilibres` lisent
  `ages_de_la_grille`, par une aide commune, `_ages`. L'âge revient sous le
  type que le pilote Python lui donnait (`castypes.age_lu`).
- Le portage date sur le paquet des données du jour
  (`pont.paquet_des_donnees`), comme le pilote Python lisait les données du
  jour, et non sur `moteur/donnees.json`. `cycle_de_vie.mjs`, lui, calcule
  toujours sur `moteur/donnees.json` : ce partage existait déjà, il n'est
  pas touché.
- L'étude bâtit encore un `Simulateur` Python, pour ses paramètres et pour
  le libellé de chaque hypothèse de productivité : des données, aucune
  règle. Elle garde ses imports de `calendrier`, de `config` et des
  chargeurs.

**Le test, écrit d'abord et vu rouge** pour la raison attendue — « un jumeau
Python date, bâtit ou simule la grille du coût »
(`outils_pont.empecher_les_jumeaux_du_cout`), levé depuis `_cases`.
`tests/test_cycle_de_vie_script.py`,
`test_l_etude_date_ses_cases_au_portage_sans_le_moteur_python` : il bâtit,
par le pilote Python, les quatre demandes que l'étude envoyait à
`cycle_de_vie.mjs` — la grille entière, 91 cases, deux fois, pour les
indicateurs et pour les étages ; 27 balayages, trois cas types que le droit
ne fait pas partir à l'âge écrit, sur trois générations, sous les trois
hypothèses de productivité ; 26 cases pour les âges d'équilibre —, puis
empêche les jumeaux et compare ce que l'étude envoie, écrit en JSON : à
l'octet, type de l'âge compris. Sept secondes : il est rangé au niveau
complet (`tests/conftest.py`, `EXCEPTIONS`), le reste du fichier restant
rapide. Sous les présomptions décalées il se tait, comme toute confrontation
au portage.

Il reste dans un fichier qui entre dans le moteur Python
(`test_fichiers_sur_le_moteur_python.py`, `FICHIERS`), et ne passe pas par
la façade des tests : sa valeur attendue est ce que le pilote Python
rendait, et la façade ne sert pas le pilote. Il part avec le moteur Python,
ou se récrit alors sur des âges posés à la main.

**Les chiffres, inchangés.** Vérifié en faisant tourner le code avant et
après.

- Les demandes entières, sans faire tourner node : la grille (91 cases), les
  balayages des treize cas types sur les sept générations sous les trois
  hypothèses (273), les âges d'équilibre (91). Le fichier qui les écrit est
  identique à l'octet. La grille des sept générations ne perd aucune case :
  le droit n'en écarte pas.
- Dix sorties de bout en bout, texte et JSON : la grille par défaut ;
  `--cor --impot` ; `--etages --impot` ; `--equilibre` ; `--ages
  salaire_moyen,militaire,fonctionnaire_actif --generations 1950,1970,2000`.
  Identiques à l'octet.
- L'étude ne fabrique aucun fichier du dépôt : `regenerer.py` ne la lance
  pas, et rien n'est à refaire.

**Ce qui n'est pas vérifié.** Les balayages de `--ages` sous `--cor` ou
`--impot`, de bout en bout : ces options ne changent que ce que
`cycle_de_vie.mjs` calcule de la même demande. Un cas type que le portage
refuserait de dater arrête maintenant l'étude par une `ValueError` qui le
nomme (`ages_de_la_grille`), là où le pilote Python levait la sienne : aucune
case de la grille n'est dans ce cas, et le chemin n'a pas de test.

**Ce qui reste des études.**

- Du lot B : `scenarios_meres.py` (`simulateur.simuler`, lignes 293 et 294,
  et `droit.ouvrir`, ligne 81) et `cout_avantages.py --par-carriere`
  (`age_liquidation_pour`, ligne 153), qui demandent au pont la carrière
  d'un seul statut lue en détail.
- Hors de l'inventaire : `part_minimum_contributif.py` (`cas.construire`
  puis `simulateur.echeancier`, lignes 242 et 243) et
  `partage_taux_unique.py` (les règles de `remuneration`, ligne 77), lues
  mais non instruites.
- `cout_avantages.py --par-carriere` ne lit qu'un âge de départ : il passe
  par `ages_de_la_grille` sans demande nouvelle, si le reste de l'option ne
  demande rien d'autre au pont. Non vérifié.

**Tests.** `python -m pytest -m rapide` (4 885 passés, 64 sautés) ; le test
neuf par son nom, puis sous `PRESOMPTIONS_DECALEES=1` (sauté) ; les fichiers
de la zone, `test_cycle_de_vie_script.py`, `test_cycle_de_vie_portage.py`,
`test_controle_drees_panorama.py`, qui lit les étages de l'étude, et
`test_fichiers_sur_le_moteur_python.py` (77 passés, 5 sautés).
