# L'inventaire des retraits : ce qui retient chaque paire, mesuré dans le code, et l'ordre pour finir

**La demande.** Le propriétaire veut la liste de ce qui reste à faire pour
finir l'action. La carte (`python scripts/jumeaux.py`) dit les 65 paires
« bloquées », 61 par le coût et 4 par la fabrique ; mais sa colonne ne mesure
que la fermeture des imports, quand le bloc « Reprise » du 3 novembre dit que
le coût date, bâtit et simule par le portage. Cette étape établit ce qui
retient réellement chaque paire : ce que son fichier Python porte encore, qui
appelle ses règles hors des confrontations, ce qui part avec elle, et ce que
le propriétaire tranche avant. Aucun code ne change, aucune paire ne part.

**La méthode.** Cinq mesures, sur 80a32b9, faites hors du dépôt, dans deux
copies de travail ; leurs scripts ne sont pas commités.

1. *Qui nomme quoi.* L'arbre syntaxique des fichiers Python suivis : pour
   chacune des 1 661 définitions de premier niveau des 65 jumeaux, les
   fichiers et les fonctions qui la nomment, imports et réexports suivis.
2. *Ce que la fabrique appelle.* `scripts/regenerer.py` entier, rejoué sous
   `sys.monitoring` : d'abord les lignes des jumeaux que chaque script
   exécute ; puis, sans mémoire des calculs, chaque entrée dans un jumeau
   depuis un fichier qui n'en est pas un ; enfin `construire_donnees.py`
   seul, sans mémoire, la pile du premier appel de chaque fonction.
3. *Ce que les tests exécutent.* La suite complète sous le même traceur,
   test par test : les lignes de chaque jumeau, et celles de `pont.py` ;
   7 996 tests tracés, en quarante-sept minutes.
4. *Ce que la concordance exécute* : `python scripts/jumeaux.py --couverture`.
5. *Ce qui est déjà relu* : la lecture des cinquante notes de l'action.

**Le constat : le coût ne retient plus le droit.** La fabrique du paquet et
des agrégats (`construire_donnees.py`, coût et coût des avantages compris,
sans mémoire) appelle 161 des 1 316 fonctions des 38 jumeaux du moteur, et
aucune de 29 d'entre eux, 21 641 lignes : rien de `moteur/compte.py`, de
`scenarios/notionnel.py`, de `echeancier.py`, de `pilote.py`, ni de vingt et
un des vingt-deux fichiers de `droit/` — de `droit/liquider.py`, la seule
`valeur_du_point`, par `RevalorisationServie`. Ce qu'elle appelle encore est
de trois sortes :

- *des chargeurs*, qui restent en Python, sous `donnees/` (note 0006) : 74 des
  177 fonctions de `scenarios/actuel.py` (ses tables), `Affiliations`
  (`carriere.py`), `charger_prelevements` et `PrelevementsPension`
  (`remuneration.py`), `RevalorisationsPensions` (`revalorisation.py`),
  `_charger_ages` (`moteur/age_reference.py`), `versions.preparer` ; et 18
  des 83 fonctions de `simulateur.py`, les accesseurs de `Simulateur`, qui
  ne font que rendre les données chargées (`macro`, `mortalite`,
  `effectifs`, `pour_la_projection`…) ;
- *des types du pont*, qui restent : `Parametres`, `Carriere`,
  `AnneeCarriere`, `DateMois`, `Fiabilite`, `Cumul`, `Reversion` ;
- *la zone grise*, des règles que le coût appelle en Python et que le site
  refait : `garantie.py` (cinq fonctions, par `cout._garantie_distribution`
  et `GarantieDistribution`), `impot_revenu.py` (34 de ses 39 fonctions, par
  `effet_retour.EffetRetour._impot`), `RevalorisationServie` (par
  `cout.coefficient_servi`, `_masses`, `calculer_cout` et
  `bilan_compte.py`), qui entraîne `Indexation.taux` et `valeur_du_point`,
  et `Indexation.coefficient` (`cout._capitaux_sous_la_variante`).

**Ce que la concordance exécute.** Des 38 paires du moteur, les tests de
concordance et la fabrication des témoins exécutent 83 % des lignes du
Python et 90 % de celles du JavaScript ; 2 173 lignes du portage ne le sont
jamais, que le quatrième temps de la méthode fige par des témoins ou que
les tests portés du lot D couvriront. Les moins couvertes : `droit/releve.js`
(21 %), `journal.js` (60 %), `droit/categories.js` (67 %), `fusion.js`
(78 %). La mesure ne change pas l'ordre : elle dit où la relecture pèse.

**Ce qui retient réellement le moteur.** Les 38 paires du moteur d'une
carrière tiennent ensemble par le simulateur Python (`Simulateur.simuler`,
`ScenarioActuel.calculer`, `Simulateur.carriere_simple`,
`Carriere.depuis_parcours`) : tant qu'un seul appelant y entre, toutes ses
règles tournent, et aucune paire ne se libère avant les autres. L'ordre de
la carte, une paire à la fois, ne s'applique donc pas à elles : c'est un
sous-ensemble cohérent, au sens de la note 0005. Cinq choses y entrent
encore.

1. *Trois scripts de la fabrique*, à chaque régénération :
   `construire_tableaux_md.py` (`carriere_simple` puis `simuler`, lignes 136
   à 141 ; `cumuls`, `EcartAge`) ; `tableau_de_bord.py`
   (`releves_des_cas_types` : les carrières des cas types bâties en Python,
   `pilote.age_de_depart` compris, et `releve.construire`) ; et les sondes de
   la prose, `mesures_prose.py`, que `verifier_prose.py` lance : trois
   `simuler`, quatre carrières bâties, et une vingtaine d'appels directs —
   `salaire_de_reference`, `fusionner`, `AgeReference.age`,
   `Convertisseur.coefficient`, `ConstructeurCapitalisation.construire`,
   `ConstructeurCompte.parts_retraite_seule`, `Indexation.coefficient`,
   `RemunerationActif`, `FicheDePaie`, `Restitution`,
   `ActuelAujourdhui.pension_annuelle`,
   `ScenarioNotionnel._garantie_vieillesse`, `salaire_moyen_annuel`.
2. *Douze études hors de la fabrique* : `scenarios_meres.py`,
   `mortalite_population.py`, `lectures_decision_29.py`,
   `lectures_du_modele.py` et `budget_calcul.py` (`simuler`) ;
   `cout_avantages.py` (`scenario_actuel.calculer`) ;
   `flux_fonction_publique.py` et `age_conjoncturel.py`, par
   `castypes.calculer_cas_types`, qui simule en Python sans passer
   l'aiguillage ; `grille_large.py` (`carriere_parcours`,
   `_debut_de_la_surcote_en_python`) ; `solde_fusion.py` (`fusionner`),
   `garantie_par_sexe.py` (`cout_garantie`), `estimation_officielle.py`
   (`salaire_moyen_annuel`).
3. *Les branches Python de l'aiguillage*, que seul le levier ouvre :
   `cout._simulations_en_python`, la carrière bâtie par
   `castypes.carriere_de_la_grille` et `pilote.age_de_depart`,
   `avantages._decomposees_en_python`, `_voisines_en_python` et `recalculer`.
   Elles partent avec les douze confrontations déclarées
   (`CONFRONTATIONS_DU_JUMEAU`), les deux tests du levier et
   `pont.par_le_jumeau`.
4. *Les tests* : 2 083 tests, dans 130 fichiers, exécutent les règles du
   moteur Python. 608, dans 66 fichiers, passent aussi par le pont : des
   confrontations, qui gardent leur moitié portage (`tests/test_oracle.py`,
   237 ; `servi_et_refait` ; les « au bit près du jumeau » de
   `tests/test_pont.py`). Les 1 475 autres n'éprouvent que le Python, et sont
   à porter ou à retirer : `test_simulateur.py` (227), `test_reversion.py`
   (207), `test_emploi_retraite.py` (72), `test_referents.py` (58),
   `test_minima_agricoles.py` (53), puis une centaine de fichiers de moins
   de cinquante tests. Ils entrent surtout par `Simulateur.carriere_simple`
   (259 fonctions de test), `ScenarioActuel.calculer` (194) et
   `Carriere.depuis_parcours` (72) ; 112 fonctions de test appellent
   directement `droit/liquider.py`, 101 `remuneration.py`, 80
   `revalorisation.py`, 77 `chronologie.py`.
5. *La relecture*, que la méthode exige de chaque paire avant son retrait
   (note 0003, temps 3) : faite pour `carriere.py`, `chronologie.py`,
   `pilote.py`, `calendrier.py` et `contexte.py` ; à faire pour 35 paires du
   moteur, 37 004 lignes de Python, dont aucune de `droit/`, et pour la zone
   grise.

**Les 65 paires, par ce qu'elles deviennent.**

- *Les 38 du moteur d'une carrière* (42 473 lignes) : les règles partent,
  d'un bloc, quand les cinq points ci-dessus sont défaits ; les chargeurs
  passent sous `donnees/`, les types restent. Avec elles part ce que seul le
  moteur Python lisait des jumeaux de données, à confirmer au retrait :
  treize des quinze méthodes de `PeriodeRegime` (`donnees/regimes.py`), que
  la fabrique du paquet n'appelle pas, et les règles d'assiette de
  `donnees/chargement.py` (`assiette_minimale`, `forfait_micro`…).
- *La zone grise* : `garantie.py`, `impot_revenu.py`, `restitution.py`, et
  deux morceaux, `RevalorisationServie` et les variantes des comptes
  (`donnees/equilibre.py`). Chacune attend la décision du propriétaire (note
  0006) ; les trois premières retiennent le coût, et `RevalorisationServie`
  retient avec elle `moteur/indexation.py` et `valeur_du_point`.
- *Les 18 de `donnees/`, les 3 du socle et les 3 moitiés de la fabrique*
  restent des deux côtés (note 0006) : le Python charge le YAML pour la
  fabrique, le coût et les études, le JavaScript lit le paquet. Rien n'en
  part, hors ce que le moteur seul lisait et les accesseurs que seuls des
  tests lisent ; la fabrique du paquet appelle 236 des 462 fonctions des
  dix-huit. Mais la carte les comptera « bloquées » pour toujours si elle
  ne dit pas qu'elles sont tenues.

**L'ordre, par lots, une session par ligne.**

| lot | ce qu'il fait | préalable | sessions |
|---|---|---|---:|
| A | La fabrique sans le moteur Python : `construire_tableaux_md.py` et `tableau_de_bord.py` (1), les sondes de `mesures_prose.py` (2) ; un test tient la liste, décroissante, de ce qui entre encore dans le moteur Python | aucun | 3 |
| B | Les études par le pont : `calculer_cas_types` et ses deux études ; `scenarios_meres.py` et `cout_avantages.py` ; les huit autres | aucun ; le propriétaire dit celles qu'il garde | 3 à 4 |
| C | La zone grise : la garantie ; l'impôt de l'effet retour ; `RevalorisationServie`, avec l'indexation et la valeur du point ; la restitution et les variantes des comptes | la décision du propriétaire, paire par paire | 4 à 5 |
| D | Les tests : les 1 475 qui n'éprouvent que le Python passent au pont, fichier par fichier ; les 608 confrontations perdent leur moitié Python au retrait | la méthode, tranchée par le propriétaire (ci-dessous) | 8 à 15 |
| E | La relecture des 35 paires du moteur et de la zone grise, par groupes de trois mille lignes | aucun ; se mène à côté des lots A à D | 12 à 14 |
| F | Le retrait : les branches du levier et ses confrontations ; les règles de `droit/`, `moteur/`, `scenarios/`, `echeancier.py`, `journal.py`, `pilote.py` ; `scenarios/actuel.py` coupé, ses 43 classes de tables sous `donnees/` ; `simulateur.py`, `carriere.py`, `remuneration.py`, `revalorisation.py`, `chronologie.py` coupés ; les fiches, les ancres et les consignes rebranchées | A à E | 5 à 6 |
| G | Les 24 paires qui restent : la carte les dit tenues, leurs accesseurs sans lecteur partent, l'action se clôt | F | 1 à 2 |

Entre 36 et 49 sessions, une quarantaine si le lot D prend sa voie courte.
Les lots A et B ne demandent rien au propriétaire et peuvent s'ouvrir tout
de suite ; A d'abord, parce que la fabrique tourne à chaque envoi.

**Ce qui peut partir tout de suite.** Aucune paire : chacune des 38 du
moteur est exécutée par au moins un script de la fabrique ou par des tests
qui n'ont pas d'autre moteur, et les 24 autres restent. La première session
utile est le lot A, première ligne.

**Ce que le propriétaire tranche.**

1. *La zone grise*, que la note 0006 renvoie à la relecture de chaque paire,
   mais qui retient le coût dès maintenant. Le critère : en JavaScript seul
   si le lecteur peut en changer le résultat, le coût le demandant au pont
   par lot ; en Python seul sinon, le site lisant le résultat figé. La
   lecture de la session, à confirmer : l'impôt sur le revenu et
   `RevalorisationServie` servent le cycle de vie du lecteur
   (`cycle-de-vie.js`), donc JavaScript seul ; la garantie, la restitution
   et les variantes des comptes, non vérifiées.
2. *Les tests du moteur Python* : les porter au pont fichier par fichier
   (`pont.droit`, `pont.scenario_actuel`, `pont.simulations`), sûr et long ;
   ou faire de `Simulateur` et de `ScenarioActuel.calculer` des clients du
   pont, qui rendent les types du résultat relus des données, les tests
   inchangés — plus court, mais non instruit : il faut savoir si le pont rend
   tout ce que ces tests lisent du résultat. La session propose une session
   d'instruction sur `test_simulateur.py` et `test_reversion.py`, 434 tests,
   avant de choisir.
3. *Les études à garder* : `budget_calcul.py`, qui mesure la vitesse du
   moteur Python, part avec lui ; `lectures_decision_29.py`,
   `age_conjoncturel.py`, `flux_fonction_publique.py`, `scenarios_meres.py`
   se portent ou s'archivent, selon qu'elles servent encore.
4. *La clôture* : que la carte dise « tenues » les 24 paires qui restent des
   deux côtés, et que l'action se close quand plus aucune règle du moteur
   n'a deux exemplaires — et non quand la carte compte zéro paire.
5. *La relecture à côté* : une session de relecture, qui ne modifie rien
   tant qu'elle ne trouve rien, peut-elle s'ouvrir en parallèle des lots A à
   D, sur la même zone ?

**Ce qui est vérifié, ce qui est déduit.** Vérifié en faisant tourner le
code : ce que la fabrique appelle dans les jumeaux, script par script, et
d'où ; ce que chaque test exécute ; les appelants des tests. Vérifié en
lisant le code : l'aiguillage (`pont.par_le_portage`, `cout._simulations`,
`castypes.batie_au_portage`), `calculer_cas_types`, les appels `simuler` des
études. Déduit seulement : les études hors de la fabrique, que la mesure ne
voit que par leurs tests et par leurs imports — une étude sans test peut
manquer ; le partage entre chargeurs et règles dans chaque fichier, tenu de
ce que la fabrique du paquet appelle, non d'une relecture ; les nombres de
sessions, tirés du rythme des étapes 5 et 6, une paire relue ou un fichier
de tests porté par session. Non mesuré : le code mort des jumeaux, et ce que
les fiches et les ancres nomment des fichiers qui partent (la colonne
« noms » de la carte, 124 pour `scenarios/actuel.py`, 120 pour
`droit/liquider.py`), compté au lot F sans être relu.

**Ce qui ne change pas.** Aucun code, aucune donnée, aucune garde, aucune
règle du scénario 1, aucun chiffre publié. La régénération rejouée dans la
copie de travail a rendu les fichiers fabriqués identiques à ceux de
80a32b9.

**Tests.** Les tests de la feuille de route (`tests/test_prose.py`) et celui
du journal de veille (`tests/test_donnees.py`) ; la prose vérifiée. La suite
complète, tracée sur 80a32b9 : 7 892 verts, un rouge,
`test_chaque_chiffre_du_parcours_est_sur_sa_page` (`tests/test_parcours.py`,
l'accueil n'affiche plus « 1 600 € » ni « 100 % »), encore rouge sur ff8a6f3 ;
`-m rapide`, sur 410feb3 : 13 autres rouges, les pages toutes faites de
`tests/test_pages_en_dossier.py`, que GitHub n'a pas encore refaites. Les
quatorze sont rouges sans cette note, qui ne touche ni au site ni aux pages ;
ils sont signalés au propriétaire.

**Les 65 paires.** Le groupe dit ce que la paire devient ; « fabrique du
paquet », les fonctions du jumeau Python que `construire_donnees.py` appelle,
sans mémoire ; « tests », ceux qui exécutent au moins dix lignes du jumeau,
et leurs fichiers ; « concordance », la part des lignes de chaque jumeau que
les tests de concordance exécutent.

| paire | lignes | groupe | fabrique du paquet | tests | concordance, Python et JavaScript | relue |
|---|---:|---|---:|---:|---:|---|
| `contributions_equilibre.py` | 297 | fabrique | 3 sur 15 | 55 dans 6 | 85 % et 98 % |  |
| `contexte.py` | 201 | fabrique | 9 sur 15 | 12 dans 5 | 46 % et 89 % | oui |
| `frontiere.py` | 194 | fabrique | 4 sur 9 | 6 dans 3 | 42 % et 93 % |  |
| `donnees/bilan.py` | 340 | données | 1 sur 21 | 7 dans 5 | 48 % et 98 % |  |
| `donnees/tva.py` | 140 | données | 6 sur 10 | 28 dans 12 | 39 % et 6 % |  |
| `donnees/depenses.py` | 364 | données | 16 sur 19 | 35 dans 16 | 88 % et 85 % |  |
| `pilote.py` | 229 | moteur | 0 sur 5 | 91 dans 18 | 83 % et 85 % | oui |
| `garantie.py` | 244 | zone grise | 5 sur 7 | 34 dans 12 | 29 % et 94 % |  |
| `impot_revenu.py` | 1320 | zone grise | 34 sur 39 | 164 dans 12 | 96 % et 95 % |  |
| `donnees/vie_en_couple.py` | 78 | données | 3 sur 3 | 28 dans 12 | 30 % et 100 % |  |
| `donnees/caracteristiques.py` | 155 | données | 7 sur 8 | 86 dans 13 | 28 % et 80 % |  |
| `noyau/versions.py` | 90 | socle | 2 sur 3 | 2139 dans 134 | 88 % et 71 % |  |
| `donnees/distribution.py` | 321 | données | 7 sur 10 | 203 dans 68 | 80 % et 45 % |  |
| `journal.py` | 127 | moteur | 0 sur 10 | 559 dans 73 | 57 % et 60 % |  |
| `donnees/effectifs.py` | 270 | données | 8 sur 11 | 63 dans 17 | 89 % et 53 % |  |
| `moteur/age_reference.py` | 190 | moteur | 2 sur 11 | 451 dans 68 | 85 % et 92 % |  |
| `droit/cultes.py` | 237 | moteur | 0 sur 4 | 17 dans 7 | 95 % et 95 % |  |
| `moteur/fusion.py` | 242 | moteur | 0 sur 5 | 173 dans 58 | 82 % et 78 % |  |
| `donnees/taux.py` | 257 | données | 12 sur 14 | 332 dans 68 | 88 % et 82 % |  |
| `moteur/indexation.py` | 261 | moteur | 5 sur 10 | 526 dans 78 | 92 % et 91 % |  |
| `droit/progressive.py` | 278 | moteur | 0 sur 15 | 21 dans 4 | 43 % et 92 % |  |
| `moteur/conversion.py` | 288 | moteur | 0 sur 12 | 469 dans 67 | 92 % et 86 % |  |
| `donnees/patrimoine.py` | 250 | données | 9 sur 13 | 28 dans 12 | 28 % et 19 % |  |
| `simulateur.py` | 1541 | moteur | 18 sur 83 | 1326 dans 138 | 76 % et 95 % |  |
| `droit/releve.py` | 461 | moteur | 0 sur 14 | 1442 dans 113 | 35 % et 21 % |  |
| `moteur/capitalisation.py` | 700 | moteur | 0 sur 28 | 450 dans 67 | 97 % et 100 % |  |
| `droit/primes.py` | 206 | moteur | 0 sur 5 | 356 dans 56 | 85 % et 90 % |  |
| `droit/foyer.py` | 271 | moteur | 0 sur 8 | 1352 dans 109 | 89 % et 93 % |  |
| `droit/etranger.py` | 513 | moteur | 0 sur 21 | 1444 dans 110 | 92 % et 91 % |  |
| `droit/liquidation.py` | 467 | moteur | 0 sur 15 | 1361 dans 109 | 89 % et 89 % |  |
| `scenarios/notionnel.py` | 791 | moteur | 0 sur 21 | 443 dans 67 | 98 % et 99 % |  |
| `droit/categories.py` | 364 | moteur | 0 sur 13 | 1305 dans 100 | 46 % et 67 % |  |
| `droit/seconde.py` | 556 | moteur | 0 sur 13 | 81 dans 6 | 70 % et 99 % |  |
| `droit/invalidite.py` | 697 | moteur | 0 sur 25 | 1429 dans 110 | 85 % et 90 % |  |
| `droit/cumul.py` | 1228 | moteur | 0 sur 45 | 93 dans 6 | 72 % et 94 % |  |
| `droit/commun.py` | 229 | moteur | 0 sur 9 | 1469 dans 109 | 78 % et 88 % |  |
| `droit/coordonner.py` | 635 | moteur | 0 sur 18 | 1755 dans 117 | 94 % et 95 % |  |
| `droit/reversion.py` | 2256 | moteur | 0 sur 60 | 305 dans 11 | 62 % et 90 % |  |
| `droit/limite_age.py` | 681 | moteur | 0 sur 24 | 1367 dans 108 | 91 % et 94 % |  |
| `revalorisation.py` | 1979 | moteur | 26 sur 57 | 952 dans 132 | 75 % et 87 % |  |
| `droit/departs.py` | 615 | moteur | 0 sur 20 | 1346 dans 108 | 84 % et 95 % |  |
| `echeancier.py` | 709 | moteur | 0 sur 20 | 557 dans 73 | 74 % et 92 % |  |
| `moteur/compte.py` | 1281 | moteur | 0 sur 27 | 535 dans 75 | 88 % et 89 % |  |
| `droit/compter.py` | 1621 | moteur | 0 sur 52 | 1515 dans 115 | 93 % et 93 % |  |
| `droit/acquerir.py` | 1177 | moteur | 0 sur 14 | 1471 dans 114 | 83 % et 86 % |  |
| `droit/completer.py` | 3072 | moteur | 0 sur 49 | 1374 dans 109 | 73 % et 87 % |  |
| `droit/ouvrir.py` | 1687 | moteur | 0 sur 36 | 1545 dans 111 | 89 % et 93 % |  |
| `droit/liquider.py` | 4867 | moteur | 2 sur 79 | 1761 dans 123 | 91 % et 93 % |  |
| `scenarios/actuel.py` | 3974 | moteur | 74 sur 177 | 2184 dans 138 | 92 % et 97 % |  |
| `donnees/indemnite_csg.py` | 168 | données | 1 sur 6 | 73 dans 26 | 96 % et 86 % |  |
| `donnees/assiette.py` | 151 | données | 6 sur 9 | 296 dans 54 | 83 % et 74 % |  |
| `restitution.py` | 206 | zone grise | 0 sur 9 | 267 dans 48 | 96 % et 97 % |  |
| `donnees/equilibre.py` | 1010 | données | 28 sur 44 | 116 dans 24 | 68 % et 93 % |  |
| `droit/preparer.py` | 23 | moteur | 0 sur 1 | 0 dans 0 | 100 % et 100 % |  |
| `donnees/prelevements_historiques.py` | 435 | données | 6 sur 29 | 70 dans 30 | 98 % et 99 % |  |
| `calendrier.py` | 165 | socle | 6 sur 12 | 1727 dans 93 | 85 % et 96 % | oui |
| `donnees/primes.py` | 209 | données | 2 sur 12 | 441 dans 63 | 97 % et 99 % |  |
| `chronologie.py` | 1563 | moteur | 3 sur 66 | 2274 dans 127 | 83 % et 91 % | oui |
| `remuneration.py` | 2780 | moteur | 12 sur 115 | 427 dans 60 | 89 % et 93 % |  |
| `carriere.py` | 3677 | moteur | 19 sur 129 | 2537 dans 142 | 91 % et 96 % | oui |
| `donnees/mortalite.py` | 894 | données | 30 sur 40 | 533 dans 77 | 85 % et 84 % |  |
| `donnees/chargement.py` | 1287 | données | 34 sur 55 | 2802 dans 165 | 83 % et 92 % |  |
| `donnees/macro.py` | 1247 | données | 23 sur 69 | 2266 dans 137 | 92 % et 94 % |  |
| `donnees/regimes.py` | 2866 | données | 37 sur 89 | 1974 dans 142 | 80 % et 93 % |  |
| `config.py` | 1386 | socle | 1 sur 9 | 451 dans 67 | 88 % et 98 % |  |
