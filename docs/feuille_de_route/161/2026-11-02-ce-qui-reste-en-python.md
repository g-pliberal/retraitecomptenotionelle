# Ce qui reste en Python : la frontière des deux langages, mesurée dans les jumeaux

**La demande.** Le 2 novembre 2026, le propriétaire : « Pour l'action 161,
il faut bien séparer ce qui doit être écrit en python de ce qui doit être
écrit en JavaScript. Il ne faut pas supprimer complètement le python.
Analyse et regarde ce qui doit rester en python. » Une étape d'analyse :
aucun code ne change.

**Ce que les décisions disent déjà.** Retirer le Python entier n'a jamais été
le but : la note 0003 l'a écarté (« Tout en JavaScript, la fabrique
comprise »), et sa règle de l'endroit donne au Python ce que seule la
fabrique calcule — acquérir, certifier et empaqueter les données, le coût,
les études, l'outillage —, au JavaScript ce que le navigateur exécute, et au
JavaScript seul le moteur d'une carrière, qui tourne aux deux endroits, que
le Python fait tourner par node. La note 0005 ajoute, pour les données, que
le Python garde ce qui lit le YAML et fabrique le paquet. Ce qu'aucune ne
dit : un jumeau Python du moteur n'est pas fait que de règles, et « retirer
le jumeau » ne peut pas vouloir dire effacer son fichier.

**La mesure, sur 25efe97.** 281 517 lignes de Python : 72 368 dans `src/`
— 55 385 dans les 65 jumeaux, 16 983 sans jumeau —, 91 300 dans `scripts/`,
dont 47 056 pour les 142 fichiers de `scripts/fetch/`, et 117 849 dans les
202 fichiers de tests. Le portage, `moteur/js/`, compte 78 244 lignes, dont
17 169 pour `pages.js`. Si les 65 jumeaux partaient entiers, 226 132 lignes
de Python resteraient, 80 % ; si seules partaient les 38 paires du moteur,
240 413, 85 %.

**Ce qui reste en Python, entier.**
- *La fabrique des données* : acquérir — les lecteurs de `scripts/fetch/`,
  `simulateurs.py`, `textes.py`, `veille_droit.py` — ; certifier —
  `verifier_donnees.py` (12 018 lignes), `frontiere_contributive.py`,
  `calendrier_regimes.py` — ; lire le YAML et empaqueter —
  `donnees/chargement.py`, `construire_donnees.py`,
  `construire_inventaire.py`, `construire_regimes_md.py`. node ne lit pas le
  YAML sans une dépendance, et les commentaires du YAML portent les sources
  (note 0003).
- *Le coût, et tout ce qui calcule une population ou une étude* : `cout.py`
  (5 399), `avantages.py`, `castypes.py`, `facteurs_depense.py`,
  `effet_retour.py`, `bilan_compte.py`, `population.py`, `leviers.py`,
  `depense_nette.py`, les deux contrôles, les écrivains de
  `donnees/agregats.py`, et les vingt-neuf études de `scripts/`
  (`grille_large.py`, 5 766 ; `mesures_prose.py`, 2 168…). Le site n'en lit
  que le résultat, figé au paquet : « dix-huit secondes de calcul, que le
  Python fait une fois, pour le paquet » (`bilan.js`).
- *Ce qui fait tourner node* : `pont.py`, `memoire.py`, `fabrique.py`,
  `web/site.py`, `construire_temoins.py`, `construire_pages.py`,
  `regenerer.py`. C'est par eux que l'exemplaire unique du moteur sert la
  fabrique.
- *La carte des règles et ses contrats* : `noyau/` — `contrats`,
  `vocabulaire`, `textes`, `carte`, `partage`, `univers` — et
  `scenarios/univers.py`.
- *Les tests et l'outillage* : pytest reste le banc, du moteur JavaScript
  aussi, qu'il fait tourner par le pont ; `verifier_prose.py`,
  `conservation.py`, `fusionner.py`, `tableau_de_bord.py`, `jumeaux.py`,
  `reprise.py`, les hooks `lecture.py` et `tdd.py`.

**Ce qui reste en Python dans les jumeaux.** Le constat de la session.
- *Les chargeurs du paquet.* `construire_donnees.py` bâtit
  `moteur/donnees.json` par des classes qui vivent aujourd'hui dans les
  jumeaux du moteur : 43 des 53 classes de `scenarios/actuel.py`, 2 869 de
  ses 3 909 lignes — les tables du droit en vigueur, âges, durées, décotes,
  minimum contributif, conversions de points —, dont la fabrique écrit la
  table et la fiche au paquet ; à en juger par le nom de leurs méthodes,
  environ 1 500 de ces lignes chargent, et 1 000 calculent, des règles dont
  le portage a son exemplaire. De même `RevalorisationsPensions`,
  `_charger_ages`, `charger_prelevements`, `Affiliations`,
  `versions.preparer`. La fabrique du paquet, la certification et les
  lecteurs de sources nomment directement 8 840 lignes de définitions des
  jumeaux, classes entières comptées.
- *Les types que le pont échange.* Le coût et les études décrivent en Python
  les réglages et les carrières qu'ils confient au portage : `Parametres`
  (`config.py`, que 26 fichiers sans jumeau lisent), `Carriere`,
  `AnneeCarriere`, `Metier` (`carriere.py`), `DateMois` (`calendrier.py`),
  les énumérations de `config.py`, et ce que `pont.py` en fait
  (`parametres_en_donnees`, `carriere_en_donnees`, `resultat_des_donnees`).
  Un contrat, non une règle — « des données décrites par un schéma » (note
  0003) —, qui a un exemplaire par langage parce que chacun le lit.
- *Les accesseurs que le coût et les études lisent* : `ComptesRetraite` (le
  coût et ses voisins, la mémoire, la fabrique, neuf études),
  `DepensesRetraite`, `AssietteActivite`, `DonneesMacro`,
  `EffectifsRetraites`, `DistributionPensions`, `CourbeTauxSansRisque`,
  `AssietteTva`. Ils lisent le YAML, non le paquet : la note 0005, qui ne
  garde qu'un exemplaire de ce qui s'exécute sur le paquet, ne les vise pas.
  Ne partent que ceux que seuls des tests lisent, comme les lecteurs des
  agrégats.

**Les 65 paires, par ce qu'elles deviennent.**
1. *Le moteur d'une carrière*, 38 paires, 41 104 lignes de Python : les 22
   de `droit/`, `scenarios/actuel.py` et `notionnel.py`, `carriere.py`,
   `remuneration.py`, `revalorisation.py`, `chronologie.py`,
   `simulateur.py`, `echeancier.py`, `pilote.py`, `journal.py`, et les six
   de `moteur/`. Leurs règles ne s'écrivent plus qu'en JavaScript ; leurs
   chargeurs et leurs types restent en Python, sortis du fichier qui part —
   sous `donnees/`, par exemple.
2. *Les données*, les 18 de `donnees/`, 10 228 lignes : le Python garde le
   chargeur et ce que la fabrique, le coût et les études en lisent ; le
   JavaScript, ce que le site lit au paquet.
3. *Le socle des échanges* : `config.py`, `calendrier.py`,
   `noyau/versions.py`, 1 592 lignes. Restent des deux côtés.
4. *Les moitiés de la fabrique* : `frontiere.py`, `contexte.py`,
   `contributions_equilibre.py`, 691 lignes. Le Python calcule ou charge à
   la fabrique — la masse de la frontière, le centre du coût, les taux des
   contributions —, le JavaScript lit le paquet ou calcule pour le lecteur :
   chacun garde sa moitié.
5. *La zone grise* : `garantie.py`, `impot_revenu.py`, `restitution.py`,
   1 770 lignes, et deux morceaux de jumeaux plus grands,
   `RevalorisationServie` (`revalorisation.py`) et les variantes des comptes
   (`donnees/equilibre.py`) : un calcul agrégé que le coût fait en Python et
   que le site refait — `coutGarantieParSexe` dans `pages.js`,
   `RevalorisationServie` et l'impôt dans `cycle-de-vie.js`.

**Le critère proposé pour la zone grise.** Si le lecteur peut en changer le
résultat — sa carrière, un réglage —, le calcul ne s'écrit qu'en
JavaScript, et le coût le demande au pont en une fois pour toutes ses
années et ses cohortes, comme `pont.departs_des_cas` : demandée appel par
appel, la surcote ralentissait la population (note de l'étape 7). Sinon, il
ne s'écrit qu'en Python, et le site lit son résultat figé au paquet, comme
le bilan et les agrégats. Le propriétaire tranche chaque paire à sa
relecture (note 0003).

**Le point dur qui vient.** Trois études remplacent une fonction du moteur
Python le temps de leur calcul, sous `memoire.modele_modifie()` :
`solde_fusion.py` (`ConstructeurCompte.taux_unifie`),
`proposition_prospective.py` (`ScenarioNotionnel.liberal`),
`stock_age_legal.py` (`ScenarioNotionnel.retroactif`, `_droits_acquis`).
Elles restent en Python, et leurs remplacements des fonctions du coût
aussi ; mais un remplacement de règle du moteur ne survivra pas au départ de
la règle : il devra se dire en données que le portage lit — une couche,
comme toute variante (`data/CLAUDE.md`), ou un paramètre de la demande au
pont. C'est l'étape « le coût sous un modèle modifié ».

**Ce que cela demande aux retraits.** Un retrait coupe le fichier : les
règles partent ; les chargeurs et les types restent ; les études qui
appellent une fonction du moteur hors du simulateur — `niveau_relatif`,
`fusionner`, `Indexation`, les blocs de `remuneration.py` — la demandent au
pont, par lot. `moteur/donnees.json` reste identique à l'octet, comme les
témoins : c'est la garde qui dirait qu'un chargeur est parti avec les
règles.

**Ce que le propriétaire tranche.** Faire de cette frontière une note de
décision, qui écrirait la règle de l'endroit fonction par fonction (le
principe 4, le § 7.1, les consignes de `src/` et de `moteur/`) ; la zone
grise, paire par paire ; le rangement des chargeurs sortis des jumeaux.

**Ce qui ne change pas.** Aucun code, aucune donnée, aucune garde, aucune
règle du scénario 1, aucune dépendance. Les mesures sont des lectures de
l'arbre syntaxique du code, faites hors du dépôt, à partir de la carte des
jumeaux (`python scripts/jumeaux.py --json`).

**Tests.** Les deux tests de la feuille de route (`tests/test_prose.py`) et
celui du journal de veille (`tests/test_donnees.py`).
