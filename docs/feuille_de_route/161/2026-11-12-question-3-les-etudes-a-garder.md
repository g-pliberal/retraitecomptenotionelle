# Question 3 : les études à garder — aucune à archiver, une moitié qui part, six à porter en quatre sessions

**La recommandation.** Garder les douze, sauf la moitié Python de
`budget_calcul.py`, qui part avec le moteur. Aucune ne s'archive : chacune a
encore un lecteur — un chiffre ancré, une limite déclarée, un référent, une
décision ouverte de l'action 186 ou un test qui nomme son fichier. Six ne
demandent rien au lot B : trois passent déjà par le pont (`grille_large.py`,
`solde_fusion.py`, `estimation_officielle.py`), une ne tient qu'à la zone
grise (`garantie_par_sexe.py`), une observe ce que lit la mémoire
(`lectures_du_modele.py`), une part. Six se portent, en quatre sessions :
`age_conjoncturel.py` et `lectures_decision_29.py` d'abord, qui ne demandent
rien de neuf au pont ; puis `flux_fonction_publique.py` ; `scenarios_meres.py`
avec `cout_avantages.py` ; `mortalite_population.py` enfin, avec les sondes
du lot A. Cinq scripts que l'inventaire ne nomme pas entrent aussi dans le
moteur Python : ils sont listés plus bas, et le lot B doit les compter.

**La demande.** L'inventaire du 9 novembre
(`2026-11-09-l-inventaire-des-retraits.md`, lignes 86 à 95, 149 et 183 à 186)
nomme douze études hors de la fabrique qui entrent encore dans le simulateur
Python, et laisse au propriétaire de dire celles qu'il garde. Il avance, sans
l'avoir vérifié, que `budget_calcul.py` part avec le moteur et que quatre
autres « se portent ou s'archivent, selon qu'elles servent encore ». Cette
note instruit la question étude par étude. Elle ne porte ni n'archive rien.

**La méthode.** Quatre mesures, sur cbd46ee.

1. *La lecture* de chaque script, aux lignes où il entre dans le moteur, et
   du pont (`src/retraite_notionnelle/pont.py`), pour ce qu'il rend déjà.
2. *Qui la nomme* : `git grep` du nom de chaque script, hors des notes et des
   archives, puis la lecture de chaque citation.
3. *L'histoire* : `git log --follow` de chaque fichier, sur l'historique
   entier (3 124 commits), approfondi pour l'occasion.
4. *Deux essais.* Les tests des études (onze fichiers, 351 tests, verts en
   2 min 45) sous un greffon écrit hors du dépôt, qui note chaque entrée dans
   `Simulateur.simuler`, `Simulateur.carriere_simple`,
   `ScenarioActuel.calculer`, `Carriere.depuis_parcours`,
   `pilote.age_de_depart`, `castypes.calculer_cas_types`, `fusionner`,
   `cout_garantie` et dans le pont, avec la ligne du script qui l'appelle ;
   puis chaque étude lancée une fois en ligne de commande.

**Ce que la mesure change à l'inventaire.** Trois choses.

- *Trois des douze sont déjà au pont.* `grille_large.py` (étape 7, le
  2 novembre), `solde_fusion.py` (le 3 novembre) et `estimation_officielle.py`
  (le 31 octobre) n'entrent plus dans le moteur Python que par la branche
  d'un aiguillage ou par une confrontation déclarée : c'est le point 3 de
  l'inventaire, qui part au lot F, non le lot B.
- *Quatre n'y entrent que par une option.* `lectures_decision_29.py` par
  `--cas-types` seul, `cout_avantages.py` par `--par-carriere` seul,
  `mortalite_population.py` par sa mesure par cas type et par `--deficit`,
  `lectures_du_modele.py` par une boucle qui ne sert qu'à voir ce que le
  moteur Python lit. Leur chemin principal lit déjà le coût que le portage
  calcule (`memoire.cout`, `memoire.avantages`).
- *La liste n'est pas close.* Cinq scripts hors de la fabrique, que
  l'inventaire ne nomme pas, datent, bâtissent ou liquident en Python (voir
  « Hors de l'inventaire »). Et un script de la fabrique, `mesures_accueil.py`,
  appelle `fusionner` par `solde_fusion.hypotheses`
  (`scripts/mesures_accueil.py:70`, `scripts/solde_fusion.py:146`) : il
  manque aux trois scripts du lot A.

## Étude par étude

Le 12 novembre 2026, dix lancements en ligne de commande ont fini sans
erreur : `scenarios_meres.py` et `--vie-entiere`, `cout_avantages.py` sous
ses trois chemins, `budget_calcul.py`, `age_conjoncturel.py`,
`mortalite_population.py` sous ses trois chemins. `lectures_decision_29.py
--cas-types` avait écrit ses tableaux de taux et calculait encore ses cas
types, treize minutes après son départ, quand cette note s'est écrite. Les
six autres études n'ont tourné que par leurs tests, verts. Les durées sont
celles d'un conteneur à quatre cœurs, la mémoire des calculs chaude.

### 1. `scenarios_meres.py` — porter (lot B, troisième session)

- *Ce qu'elle produit, qui la lit.* Ce que chaque système sert à une même
  femme selon ses enfants, et le bilan vie entière de l'aide à la naissance
  (`--vie-entiere`). L'action 186, en cours, s'en sert : sa note
  `186/2026-11-07-enfants-etude-et-couts.md` la cite deux fois, par un lien
  vers le fichier (lignes 348 et 463). Huit de ses douze tests la tiennent
  (`tests/test_scenarios_meres.py:22` à `90`) ; les quatre autres éprouvent
  des règles du droit sans le script (lignes 112 à 153) et sont du lot D.
  Deux fiches nomment le fichier de tests
  (`data/reference/regles/enfants_fonction_publique.yaml:341`,
  `majoration_duree_assurance_enfants.yaml:361`). Aucune page, aucun chiffre
  ancré.
- *Vraie et reproductible.* Née le 19 septembre 2026, retouchée le
  6 octobre ; tourne en 2 s.
- *Ce qu'elle appelle.* `carriere_simple` (ligne 242), deux `simuler` (293
  et 294), et sa propre boucle de l'âge sur `ouvrir.age_taux_plein_droit` et
  `ouvrir.age_ouverture_droit` (265 à 271) ; la trace compte 100 carrières
  bâties et 52 simulations. Elle lit du résultat ce que `pont.carrieres` ne
  rend pas : le complément de la garantie et sa date, l'espérance et le
  diviseur de la conversion, chaque avantage appliqué avec son libellé, la
  durée, le taux (300 à 330), et `Indexation.coefficient` (304).
- *Le coût.* Une session : `pont.carrieres` prend déjà ses options, mais
  doit rendre ces champs ; `ouvrir.age_taux_plein_droit` n'est pas dans
  `LECTURES_DU_DROIT` (`pont.py:1237`), quand le portage l'a
  (`moteur/js/droit/ouvrir.js:1126`). La voie courte : confier l'âge au
  pilote du portage (`pont.ages_de_depart`), dont sa boucle est une copie
  réduite, de son propre aveu (ligne 257).
- *Archiver* casserait deux liens d'un récit que rien ne récrit, et priverait
  l'action 186 d'un calcul qu'elle cite. Non.

### 2. `mortalite_population.py` — porter (lot B, quatrième session, avec le lot A)

- *Ce qu'elle produit, qui la lit.* Ce que la table de mortalité commune
  transfère, par cas type, et ce qu'elle coûte au régime (`--deficit`). Sa
  mesure par cas type est une sonde de la prose
  (`scripts/mesures_prose.py:1014` à `1042`), qui ancre onze chiffres de
  `docs/methodologie.md` (lignes 488 à 513) : elle tourne donc à
  chaque régénération, et relève du lot A, seconde ligne. Le déficit est
  écrit en toutes lettres, sans ancre, à `docs/methodologie.md:469` ; aucun
  fichier fabriqué ne le lit
  (`138/2026-10-19-etape-3-la-date-des-cohortes-du-deficit.md:23`). Huit
  tests, de la suite rapide, tiennent le déficit
  (`tests/test_mortalite_population.py`) ; `docs/limites/5-hors-du-modele.md:49`
  la cite.
- *Vraie et reproductible.* Née le 20 septembre, retouchée le 23 octobre
  (action 138, étape 7) ; 1 s par cas type, 10 s par vingtile.
- *Ce qu'elle appelle.* La mesure bâtit le cas type en Python
  (`cas_type.construire`, ligne 151) et le simule sous deux tables (152 et
  153). `--deficit` bâtit deux fois la grille par
  `castypes.carrieres_de_la_grille`, que seul le Python fait (262 et 290 :
  29 âges fixés par le pilote Python et 103 carrières à chaque fois, d'après
  la trace), et la simule en Python (294) pour lire
  `capital_droits_acquis` et `capital_notionnel`, que `pont.grille_du_cout`
  ne rend pas.
- *Le coût.* Une session. La mesure lit ce que `pont.grille_du_cout` rend
  déjà (la pension de chaque scénario en euros constants, le départ reporté
  de la proposition) ; le déficit demande une lecture de plus à cette
  demande, comme `comptes` l'a été pour `solde_fusion.py`. À mener avec la
  session des sondes du lot A, ou juste après elle : même fonction, même
  zone.
- *Archiver* laisserait onze ancres d'un document d'état sans leur sonde.
  Non.

### 3. `lectures_decision_29.py` — porter l'option, ou la retirer une fois la décision prise

- *Ce qu'elle produit, qui la lit.* Les deux lectures de la décision 29 du
  programme, sous le coût du modèle. `docs/feuille_de_route_programme.md:852`
  dit que « le calcul se refait par » elle, et que « le choix entre A et B
  reste au propriétaire » ; le bloc « Reprise » de l'action 186 commence par
  ce choix. Treize tests tiennent ses règles, sur un cas posé à la main,
  sans le moteur (aucune entrée dans la trace).
- *Vraie et reproductible.* Née le 7 novembre, retouchée le 10 : la plus
  jeune des douze. `--cas-types` est lent : le coût se recalcule sous
  chaque taux.
- *Ce qu'elle appelle.* Son chemin principal ne lit que `memoire.cout`
  (ligne 301), que le portage calcule. Seul `--cas-types` entre dans le
  moteur Python : `carriere_de_la_grille` puis `simuler` (399 et 400), sans
  aucun test.
- *Le coût.* Un quart de session : `pont.grille_du_cout` rend déjà les
  quatre valeurs lues (la pension du scénario 6 et celle de l'étalon en euros
  constants, l'année du départ, la carrière bâtie). Le test manque, et vient
  d'abord.
- *Archiver.* Seulement l'option, et seulement quand le propriétaire aura
  choisi entre A et B : ses sorties sont déjà dans le récit
  (`186/2026-11-07-deux-lectures-au-modele.md:146` à `152`), et la fonction
  `pensions_des_cas_types` se retirerait sans rien perdre. Tant que le choix
  est ouvert, la porter coûte moins que de la refaire.

### 4. `lectures_du_modele.py` — garder, ne pas porter ; sa boucle part au lot F

- *Ce qu'elle produit, qui la lit.* Le relevé de ce que lisent les calculs
  que la mémoire garde, qui tient `HORS_DU_MODELE`
  (`src/retraite_notionnelle/memoire.py:138`, `src/CLAUDE.md:71`). Deux
  tests de l'outillage l'exigent (`tests/test_outillage.py:885` et `903`).
- *Ce qu'elle appelle.* `simuler` sur deux carrières par statut (lignes 119
  à 130), non pour un résultat, mais pour voir ce que le moteur Python
  ouvre : « c'est ce qu'il lit qui compte » (ligne 118). Puis `memoire.cout`
  et `memoire.avantages` (131 et 132).
- *Le verdict.* Rien à porter : le pont rendrait un résultat dont elle ne
  fait rien. Quand le moteur Python part, plus aucun calcul gardé ne le fait
  tourner, et sa boucle part avec lui ; restent le coût, les avantages et la
  fabrique du paquet, que le relevé suit déjà. Les deux seuils du test
  (`> 100` fichiers lus, `> 50` fiches) sont à revoir ce jour-là. Lot F, une
  fraction de session.

### 5. `budget_calcul.py` — la moitié Python part avec le moteur

- *Ce qu'elle produit, qui la lit.* Le temps de calcul par carrière dans les
  deux moteurs, que `docs/architecture.md:1510` demande à chaque phase. Un
  test tient la façon dont elle bâtit ses carrières
  (`tests/test_outillage.py:909`).
- *Ce qu'elle appelle.* `scenario_actuel.calculer` et `simuler` (lignes 65
  et 66), pour les chronométrer ; puis `scripts/budget_calcul.mjs`, qui
  mesure le portage sans le Python.
- *Le verdict.* L'inventaire a raison. Au lot F : le fichier Python et son
  test partent, `budget_calcul.mjs` reste, et la phrase de l'architecture,
  un état, nomme le fichier qui reste. Rien ne se perd : la dernière mesure
  est ici — Python, 932 carrières, 5,94 ms pour le scénario 1 et 29,58 ms
  pour les six ; JavaScript, 166 carrières, 2,54 ms et 10,62 ms. Les deux
  moitiés ne mesurent déjà plus les mêmes carrières : à dire au retrait.

### 6. `cout_avantages.py` — porter l'option (lot B, troisième session)

- *Ce qu'elle produit, qui la lit.* Le coût de chaque avantage non
  contributif, par année. Onze avantages la déclarent
  (`chiffre_par: scripts/cout_avantages.py`, dans
  `data/reference/legislation/avantages_non_contributifs.yaml`), et un test
  exige que ce fichier existe (`tests/test_avantages.py:215` à `220`).
  `docs/avantages_non_contributifs.md:131` et `226` et
  `docs/limites/5-hors-du-modele.md:142` la citent. Aucun test n'importe le
  script : `tests/test_avantages.py` éprouve le module `avantages`.
- *Vraie et reproductible.* Née le 19 septembre, retouchée le 24 octobre ;
  23 s par année, 13 s pour `--duree`, 3 s pour `--par-carriere`.
- *Ce qu'elle appelle.* Son chemin principal et `--duree` passent par le
  module `avantages`, que le portage sert (`pont.avantages`). Seul
  `--par-carriere` entre dans le moteur Python : l'âge par le pilote Python
  (ligne 151), deux `scenario_actuel.calculer` (167 et 169), puis
  `recalculer` (176 et 177), l'une des branches Python de l'aiguillage.
- *Le coût.* Une demi-session : `pont.ages_de_depart` et `pont.avantages`
  rendent ce que l'option lit (la pension, chaque contrefactuelle, le
  refus). L'option n'a aucun test : il vient d'abord.
- *Archiver* demanderait de récrire onze déclarations et le test qui les
  tient. Non.

### 7. `flux_fonction_publique.py` — porter (lot B, deuxième session)

- *Ce qu'elle produit, qui la lit.* Les trois cas types statutaires face
  aux départs de 2025 du jaune pensions. Douze tests, dont trois tiennent
  des fourchettes déclarées (`tests/test_flux_fonction_publique.py:161`,
  `263`, `297`) ; deux référents et une source les nomment
  (`data/reference/referents.yaml:7016` et `7146`, `data/sources.yaml:2760`) ;
  deux limites s'y appuient (`docs/limites/5-bis-cout-agrege.md:325`,
  `docs/limites/5-hors-du-modele.md:177`).
- *Vraie et reproductible.* Née le 13 octobre, retouchée le 18.
- *Ce qu'elle appelle.* `calculer_cas_types` (ligne 221), qui bâtit et
  simule en Python sans passer l'aiguillage (`castypes.py:978` et `979`) :
  la trace y compte six simulations et six âges fixés par le pilote Python.
  Elle lit le journal de la liquidation — le traitement de l'article L. 15
  et la pension avant tout complément (lignes 237 à 242) —, qu'aucune
  demande du pont ne rend.
- *Le coût.* Une session : une lecture de plus à `pont.departs_des_cas`, le
  portage tenant déjà le journal (`moteur/js/simulateur.js:917`).
  `calculer_cas_types` n'a plus alors, hors des tests, que
  `age_conjoncturel.py`.
- *Archiver* ôterait le contrôle de deux référents. Non.

### 8. `age_conjoncturel.py` — porter (lot B, première session)

- *Ce qu'elle produit, qui la lit.* L'âge de départ de la grille face à
  l'âge conjoncturel de la DREES. Trois de ses cinq tests tiennent la limite
  qu'écrit `docs/limites/5-hors-du-modele.md:184` ; `data/sources.yaml:1865`
  la nomme. Deux autres scripts importent sa fonction
  (`scripts/age_depart_csp.py:71`, `scripts/cout_age_depart.py:79`), avec
  leurs tests.
- *Vraie et reproductible.* Née le 21 septembre, retouchée le 24 octobre ;
  20 s.
- *Ce qu'elle appelle.* `calculer_cas_types` (ligne 126), dont elle ne lit
  que l'année et l'âge du départ (130 à 136).
- *Le coût.* Une demi-session, la moins chère des six : le pont rend déjà
  l'âge et l'année de chaque case (`castypes.departs_au_portage`,
  `pont.carrieres_de_la_grille` sous `"rendre": "depart"`). Une seule
  fonction change, et les trois scripts passent ensemble. À vérifier en
  portant : `calculer_cas_types` écarte aussi les cases dont la simulation
  échoue, ce que la datation seule ne voit pas.

### 9. `grille_large.py` — garder ; rien au lot B

Déjà portée (`161/2026-11-02-etape-7-la-grille-large.md`) : ses mesures
passent par `pont.departs_des_cas` (ligne 3675 ; 7 119 demandes dans la
trace) et `pont.debuts_de_la_surcote` (4606). Ce qui reste est la branche
Python de quatre aiguillages (lignes 1571, 1707, 3706, 3719 et 4613), que
seuls ses tests ouvrent encore : « ses autres essais éprouvent les cas types
eux-mêmes par le moteur Python » (même note, lignes 70 à 73). C'est du lot D
pour ces tests, du lot F pour les branches. C'est aussi la plus lue des
douze : 107 tests, quatre scripts qui l'importent (`mesurer_surcote.py`,
`recours_aspa.py`, `part_minimum_contributif.py`, `controle_eacr.py`), les
mesures de `docs/mesures/138/`.

### 10. `solde_fusion.py` — garder ; une fonction, à passer au pont avec le lot A

Portée le 3 novembre (`161/2026-11-03-le-regime-unique-par-bareme.md`) : son
coût se simule au portage, et le moteur Python n'y tourne que sous la
confrontation déclarée de `tests/test_solde_fusion.py:100`. Reste
`fusionner`, deux appels (lignes 146 et 147) qui lisent le taux du régime
unique du modèle. Or la fabrique passe par là à chaque régénération
(`scripts/mesures_accueil.py:70`, quatre mesures de l'accueil), et les
sondes de la prose appellent `fusionner` aussi : la demande au pont se fait
une fois, au lot A, et `solde_fusion.py` la prend.

### 11. `garantie_par_sexe.py` — garder ; suit la garantie, au lot C

N'entre pas dans le moteur d'une carrière : elle lit `memoire.cout` et
`memoire.avantages`, des chargeurs, et appelle `cout_garantie` (ligne 235 ;
192 appels dans la trace), une règle de `garantie.py`, que l'inventaire range
dans la zone grise. Son sort est celui de la garantie, que tranche la
question 1 : si elle reste en Python, rien ne change ; si elle passe au
JavaScript seul, le script la demande au pont comme le coût le fera. Huit
tests ; l'action 186 l'a retouchée le 9 novembre.

### 12. `estimation_officielle.py` — garder ; un import à suivre, au lot F

Portée le 31 octobre : elle bâtit et liquide par `pont.carrieres_des_saisies`
et `pont.scenario_actuel` (lignes 583, 638 et 647), et le moteur Python n'y
tourne que sous la confrontation de ses tests (`servi_et_refait`,
`tests/test_estimation_officielle.py:99`). Reste `salaire_moyen_annuel`
(lignes 72 et 607), une série tirée des données macroéconomiques, que
`scenarios_meres.py` lit aussi : son import suivra la fonction là où le lot
F la range. C'est l'outil qui confronte une carrière réelle à « Mon
estimation retraite ».

## Le tableau des douze

| étude | verdict | où | sessions du lot B |
|---|---|---|---:|
| `age_conjoncturel.py` | porter, avec `age_depart_csp.py` et `cout_age_depart.py` | lot B, session 1 | ½ |
| `lectures_decision_29.py` | porter `--cas-types`, ou le retirer si A ou B est choisi avant | lot B, session 1 | ¼ |
| `flux_fonction_publique.py` | porter ; le pont rend le journal de la liquidation | lot B, session 2 | 1 |
| `scenarios_meres.py` | porter ; le pont rend ce qu'elle lit du résultat | lot B, session 3 | ¾ |
| `cout_avantages.py` | porter `--par-carriere`, le test d'abord | lot B, session 3 | ½ |
| `mortalite_population.py` | porter ; sa sonde avec le lot A | lot B, session 4 | 1 |
| `solde_fusion.py` | garder ; `fusionner` au pont | lot A | 0 |
| `grille_large.py` | garder ; déjà au pont | lots D et F | 0 |
| `estimation_officielle.py` | garder ; déjà au pont | lot F | 0 |
| `garantie_par_sexe.py` | garder ; suit la garantie | lot C | 0 |
| `lectures_du_modele.py` | garder ; sa boucle part | lot F | 0 |
| `budget_calcul.py` | la moitié Python part ; `budget_calcul.mjs` reste | lot F | 0 |

## L'ordre du lot B, et son coût

Quatre sessions, cinq si les scripts hors de l'inventaire en demandent une ;
l'inventaire en comptait trois à quatre.

1. *Ce que le pont rend déjà* : `age_conjoncturel.py` et ses deux scripts,
   `lectures_decision_29.py --cas-types`, et la datation de
   `cycle_de_vie.py`. Aucune demande nouvelle au pont.
2. *Le journal de la liquidation* : `flux_fonction_publique.py`.
   `calculer_cas_types` n'a plus alors que des tests pour appelants.
3. *La carrière d'un seul statut, lue en détail* : `scenarios_meres.py` et
   `cout_avantages.py --par-carriere`, que l'inventaire groupait déjà.
4. *La mortalité* : `mortalite_population.py`, après la session des sondes
   du lot A ou avec elle.

Les sessions 1 à 3 ne se gênent pas entre elles sur les scripts, mais
toutes écrivent dans `pont.py` et `pont.mjs` : une à la fois.

## Ce qu'« archiver » voudrait dire, si le propriétaire en décidait autrement

Aucune étude n'est à archiver, mais la recette vaut pour la moitié de
`budget_calcul.py`, pour l'option `--cas-types`, et pour toute étude que le
propriétaire écarterait. Le dépôt n'a pas d'archive de scripts :
`docs/archives/` tient des documents, et la règle
(`docs/architecture.md`, § 12) dit qu'un fichier ne se retire que si son
contenu existe ailleurs, vérifié, l'historique git gardant le reste.

- *Le résultat* : l'étude tourne une dernière fois, et sa sortie se dépose
  telle quelle sous `docs/mesures/161/`, avec le commit et la commande, comme
  l'action 138 l'a fait (`docs/mesures/138/2026-11-05-etape-14-inaptes.txt`).
- *Le script* : retiré ; la note du retrait nomme son dernier commit.
- *Ses lecteurs* : le test qui l'importe part avec lui ; une fiche, un
  référent ou une déclaration qui nomme ce test ou ce script se corrige au
  même commit ; un document d'état perd la phrase, ou cite la mesure
  déposée. Un récit ne se récrit pas : un lien qu'il porte vers le script
  se déclare, ou le script reste.
- *La vérification* : `python scripts/conservation.py --depuis HEAD` avant
  le commit, une seule session déplaçant des fichiers à la fois.

## Hors de l'inventaire

L'inventaire prévenait qu'« une étude sans test peut manquer ». Un balayage
de `scripts/` sur les entrées du moteur en trouve cinq, lues mais non
instruites.

- `age_depart_csp.py` (ligne 122) et `cout_age_depart.py` (ligne 144), par
  `age_conjoncturel.departs_de_la_grille` : elles passent avec elle.
- `cycle_de_vie.py` : il date encore ses cases en Python
  (`carriere_de_la_grille`, ligne 174 ; `age_liquidation_pour`, 370 et 442),
  quand `castypes.cases_de_la_grille` le fait au portage.
- `part_minimum_contributif.py` : `cas.construire` puis
  `simulateur.echeancier` (lignes 242 et 243), sans aiguillage. C'est elle
  qui peut demander la cinquième session.
- `partage_taux_unique.py` : il importe les règles de la fiche de paie
  (`remuneration`, ligne 77).

Deux lectures voisines, pour mémoire : `indexation_scenario_6.py:212`
(`RevalorisationServie`, zone grise) et `recours_aspa.py:429` (le minimum
vieillesse du scénario 1, une table).

## Ce qui est vérifié, ce qui est déduit

*Vérifié en faisant tourner le code* : que cinq des douze tournent encore
en ligne de commande, six autres par leurs tests, et
`lectures_decision_29.py` par son chemin principal ; les entrées dans le moteur Python de `scenarios_meres.py`,
`flux_fonction_publique.py`, `mortalite_population.py --deficit`,
`grille_large.py`, `solde_fusion.py`, `estimation_officielle.py` et
`garantie_par_sexe.py`, à la ligne, par la trace de leurs tests ; que les
tests de `lectures_decision_29.py` n'y entrent pas.

*Vérifié en lisant le code* : les entrées de `age_conjoncturel.py`, dont la
mesure était déjà en mémoire quand la trace a tourné ; celles des options
sans test (`--cas-types`, `--par-carriere`) ; ce que le pont rend ; chaque
citation donnée ici.

*Déduit seulement* : les coûts en sessions, tirés de ce que chaque étude lit
et de ce que le pont rend, sans qu'aucune demande n'ait été essayée ; que le
portage date les cases de `age_conjoncturel.py` comme `calculer_cas_types`
les garde ; que le relevé de `lectures_du_modele.py` reste complet sans sa
boucle ; le sort de `salaire_moyen_annuel`. Non instruits : les cinq scripts
hors de l'inventaire, relevés par motif — un script qui entrerait dans le
moteur sous un autre nom manquerait encore.

**Ce qui ne change pas.** Aucun code, aucune donnée, aucun test, aucun
fichier déplacé, aucun chiffre publié ; le bloc « Reprise » de l'action
n'est pas récrit, la session d'orchestration le tient.

**Tests.** La prose vérifiée (`python scripts/verifier_prose.py --corriger`)
et les tests de la feuille de route (`tests/test_prose.py`). Les 351 tests
des études, verts, sous le greffon de mesure.
