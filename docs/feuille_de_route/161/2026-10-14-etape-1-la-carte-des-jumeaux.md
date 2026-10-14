# Étape 1 : la carte des jumeaux, et ce qu'elle montre au 14 octobre 2026

**La demande.** L'outil que la méthode de l'action suppose avant tout retrait :
pour chaque paire Python–JavaScript, tout ce qui dépend de chacun des deux
jumeaux, et ce que les tests de concordance en exécutent, des deux côtés ; les
paires rangées de la plus facile à retirer à la plus difficile. Rien n'est
retiré à cette étape.

**Ce qui est fait.**

- `scripts/jumeaux.py`, la carte. Une paire se déclare par l'en-tête du
  fichier JavaScript (« Portage de », « Jumeau de », « Copie de », « Lecteur
  de ») : 69 le sont, dont `pilote.js`, jumeau partiel, et `regimes.js`, qui
  ne le dit pas, s'apparie à `donnees/regimes.py` par le nom. La carte relève
  six sortes de dépendants : les imports Python, lus dans l'arbre syntaxique,
  ceux d'une fonction compris, résolus comme `sys.path` le ferait (un script
  se lance depuis son dossier, et `from lecture_pdf import …` y trouve son
  voisin), puis leur fermeture jusqu'à la fabrique (`regenerer.py`) et au coût
  (`cout.py`) ; les imports JavaScript depuis `index.html` ; les chargements
  par nom, un fichier qu'une chaîne du code nomme (un script qu'un test charge
  par son chemin, un module du portage que le Python fait lire à node) ou que
  `site().module("pages")` désigne ; le champ `code` des fiches ; les
  chiffres ancrés qui chargent un module par son nom ; les mentions, en récits
  ou en textes à tenir. Elle signale aussi ce qui nomme un fichier de code
  introuvable.
- `--couverture` rejoue les tests de concordance — `node --test tests/js/`,
  les 45 tests pytest qui confrontent les deux moteurs, la fabrication des
  témoins —, sans mémoire de calcul, et relève les lignes exécutées : celles
  du JavaScript par la couverture de V8, celles du Python par
  `sys.monitoring`. Deux minutes ; la mesure se garde dans `.cache/jumeaux/`.
  Le lecteur de la couverture de V8 a été confronté au rapport de node
  lui-même, sur la même exécution : 1,75 point d'écart en moyenne sur les 70
  fichiers, jamais au-dessus de node, parce qu'il compte non exécutée la ligne
  qui déclare une fonction jamais appelée.
- `tests/test_jumeaux.py`, au niveau contrôle avec l'outillage du dépôt : ses
  règles sur des dépôts miniatures, et, sur le dépôt, aucune déclaration de
  jumeau qui nomme un fichier disparu — la dépendance qu'un retrait casse en
  premier.

**Ce que la carte montre**, au commit 84efb56.

- **70 paires**, 56 003 lignes de Python et 43 165 de JavaScript. Trois ne
  sont atteintes ni par le coût ni par la fabrique : `web/releve_lu.py`,
  `cycle_de_vie.py`, `scripts/fetch/lecture_pdf.py`. Sept le sont par la
  fabrique seule : `donnees/agregats.py`, `donnees/credits_ministeres.py`,
  `contributions_equilibre.py`, `contexte.py`, `saisie.py`, `frontiere.py`,
  `donnees/bilan.py`. Les soixante autres, tout le moteur d'une carrière, le
  sont par le coût : aucune ne se retire avant le pont.
- **Aucun jumeau Python ne sert qu'aux tests**, et tout import d'un module du
  paquet exécute `retraite_notionnelle/__init__.py`, qui importe `config.py` :
  129 fichiers de tests atteignent celui-ci.
- **27 modules Python sans jumeau**, le coût en tête (`cout.py`, 4 589
  lignes), et **4 fichiers JavaScript sans jumeau**, ceux du site : `pages.js`,
  `gabarit.js`, `format.js`, `inventaire.js`.
- **Rien ne nomme un fichier de code introuvable** : ni en-tête, ni fiche, ni
  ancre.
- **Les trois modules écrits dans la nuit** (action 138, étape 9 :
  `cycle-de-vie.js`, `contributions-equilibre.js`,
  `prelevements-historiques.js`) sont préchargés par `index.html`, et aucune
  page ne les charge encore.

**La couverture**, mesurée le 14 octobre 2026. Les tests de concordance
exécutent 81,8 % des lignes Python des jumeaux (23 171 sur 28 331) et 88,3 %
de leurs lignes JavaScript (25 333 sur 28 695) ; 10 jumeaux Python et 15
jumeaux JavaScript le sont à 95 % ou plus. Les moins couverts, là où la
relecture commence : côté JavaScript, `tva.js` (6 %), `patrimoine.js`
(19 %), `droit/releve.js` et `journal.js` (37 %), `distribution.js` (44 %),
`effectifs.js` (53 %) ; côté Python, `scripts/fetch/lecture_pdf.py` (13 %),
`donnees/effectifs.py` (21 %), `pilote.py` (23 %),
`donnees/caracteristiques.py` et `donnees/patrimoine.py` (28 %),
`garantie.py` (29 %). Une ligne qu'aucun de ces tests n'exécute n'a jamais
été confrontée à son jumeau.

**Le pilote, relevé.** `web/releve_lu.py` (1 112 lignes) et `releve-lu.js`
(990), que le site charge pour lire le relevé qu'un lecteur dépose. Les tests
de concordance en exécutent 97 % et 99 %. Le jumeau Python est importé par
`scripts/estimation_officielle.py` (ligne 75), `tests/test_affirmations.py`
(2849) et `tests/test_releve_lu.py` (30) ; six textes à tenir le citent :
`README.md`, `data/reference/referents.yaml`, `docs/architecture.md`,
`docs/limites/5-hors-du-modele.md`, l'en-tête de `releve-lu.js` et
`web/__init__.py`. Côté JavaScript, `tests/test_affirmations.py` (2902) le
nomme, et `tests/test_releve_lu.py` le fait lire à node par
`tests/js/comparer-releve.mjs`, contre le Python : ce test devra trouver une
autre référence, les relevés d'exemple figés en témoins.

**Ce que la carte ne voit pas.** Un import dont le nom se calcule (une chaîne
qu'on assemble, un `import()` de gabarit) ; un sous-processus Python qu'un
test lance, que la sonde ne suit pas ; un test de concordance qui ne dit ni
« javascript », ni « portage », ni « jumeau » dans son nom. Une mention par un
nom seul, que plusieurs fichiers portent, compte pour chacun et se dit
ambiguë ; un récit se reconnaît à son dossier. Une ligne exécutée n'est pas
une ligne comparée : la couverture dit ce qui n'a jamais été confronté, non ce
qui l'a été.

**Ce qui reste.** L'étape 2, la note de décision ; puis le pilote, qui commence
par `python scripts/jumeaux.py releve_lu` et par la relecture de la paire,
fonction par fonction.
