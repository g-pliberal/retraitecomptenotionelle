# Le code mort : ce que rien n'atteint dans le portage, mesuré par l'arbre des appels et par l'exécution

**La conclusion.** Le portage JavaScript, qui reste et fait foi, ne porte
presque pas de code mort : 61 unités, 332 lignes sur 80 506 (0,4 %), que ni
le site, ni le pont, ni la fabrique n'atteignent — 40 fonctions que rien
n'exécute, 9 que seuls des tests exécutent, 12 constantes que nul ne lit.
S'y ajoutent 98 fonctions que la production nomme mais que ni la fabrique,
ni la suite, ni les tests d'écran n'exécutent : des chemins du site sans
test, ou des morts qu'un homonyme cache, à trancher une à une. Le moteur
Python d'une carrière n'a pas à être mesuré : par les noms, 1 % de ce qui
reste à relire. Rien n'est retiré ; le propriétaire tranche en fin de note.

**La demande.** L'inventaire du 9 novembre
(`2026-11-09-l-inventaire-des-retraits.md`) dit n'avoir pas mesuré le code
mort des jumeaux. Cette étape le mesure, là où la mesure permet de décider,
et commence par dire où elle le permet. Aucun code ne change, aucun test.

## La pertinence, avant la mesure

**Les règles du moteur Python d'une carrière (38 paires) : non.** Elles
partent d'un bloc au lot F ; ce qui y est mort part avec le reste, sans
décision à prendre. La seule question utile est celle du lot E : ce qui est
mort n'a pas à être relu. Une mesure par les noms, qui coûte un script,
suffit à y répondre : 46 des 1 444 définitions de ces fichiers ne sont
nommées par rien (16) ou par les seuls tests (30), 478 lignes, dont 381 dans
les fichiers qui restent à relire — 1 % des 37 004 lignes. La relecture n'en
est pas allégée ; la mesure par l'exécution, quarante-sept minutes de suite
tracée, n'a pas été refaite. La liste est donnée plus bas, pour ce qu'elle
vaut : elle évite de comparer 46 fonctions à leur portage.

**Le portage JavaScript : oui.** Il reste, il fait foi, et une fonction que
ni le site, ni le pont, ni un test n'appelle y est une charge : elle se relit
au lot E, elle compte parmi les fonctions en double de la question 4, et elle
laisse croire qu'une règle a un lecteur. C'est là que la mesure a été menée,
par l'arbre des appels et par l'exécution.

**Les 24 paires qui restent des deux côtés : la moitié JavaScript oui, la
moitié Python non.** La note de la question 4
(`2026-11-12-question-4-la-cloture.md`) estime, par les noms, que 79 à 125 de
leurs 291 fonctions en double n'auront plus de lecteur Python une fois le
moteur parti. La refaire par l'exécution aujourd'hui serait la refaire pour
rien, pour trois raisons. Ce qu'elle déciderait — le critère de clôture, par
fonction ou par paire — ne dépend pas de savoir si le nombre est 79 ou 125.
Son objet bouge : les lots A, B et C, ouverts ou à trancher, changent les
lecteurs Python de ces fichiers, et tant que la fabrique entre dans le moteur
Python, une trace doit trier chaque appel par sa pile, les chargeurs logés
dans `simulateur.py` et `scenarios/actuel.py` compris ; le lot A fini, une
trace simple de `regenerer.py` donnera la liste sans ce tri. Enfin la liste
par fonction, avec son lecteur, est exactement ce que le lot G dresse si le
propriétaire retient le critère de la question 4 : elle se fera alors une
fois, sur l'état qui compte. La mesure par les noms, sortie du même script
que pour le moteur, recoupe la fourchette sans la resserrer (voir « Le
Python »). En revanche la moitié JavaScript de ces paires relève du portage,
et la mesure y trouve le miroir de la question 4 : des fonctions en double
que le Python lit et que rien ne lit en JavaScript.

**Ce que la mesure permet de décider** : s'il faut une session de retrait du
code mort du portage, et quand ; ce que le lot E peut ne pas relire ; ce que
le lot D a devant lui de fonctions sans test ; ce qui sort de la liste des
fonctions en double avant qu'on la dresse.

## La méthode

Quatre mesures, sur 3944fdc, par des scripts écrits hors du dépôt et non
commités, dans deux clones neufs, sans mémoire des calculs.

1. *L'arbre des appels du portage.* Les 79 fichiers de `moteur/js/`, les
   deux lanceurs que le Python tient ouverts (`pont.mjs`, `web/site.mjs`) et
   les trois de `scripts/`, lus par un analyseur syntaxique (acorn) : 3 762
   unités de premier niveau, dont 2 718 fonctions, méthodes, accesseurs et
   classes, et 1 044 constantes. Une unité vit si une racine, ou une unité
   vivante, la nomme. Les racines : `routeur.js`, seul module que
   `moteur/page.html` charge ; les lanceurs ; le code de premier niveau de
   chaque module ; et les noms qu'emploient les huit fichiers Python qui
   nomment le site (`web/site.py` et sept scripts, fabrique comprise). Un identifiant se
   résout par les imports du fichier ; un nom de propriété (`objet.nom`)
   tient en vie toute méthode et tout export de ce nom, quel que soit le
   fichier : la mesure pèche donc par défaut, jamais par excès.
2. *L'exécution*, fonction par fonction, par la couverture que V8 tient
   lui-même (`NODE_V8_COVERAGE`), fusionnée à mesure : la fabrique entière,
   `scripts/regenerer.py`, 575 secondes, 52 processus node ; la suite
   complète, 8 174 tests, dix-neuf minutes, 539 processus node ; et les 80
   tests d'écran rejoués, le pilote du clone retouché pour demander à
   Chromium sa couverture avant chaque changement de page. La suite tracée
   de l'inventaire n'a pas été relancée.
3. *Les noms dans la prose* : pour chaque candidat, les fiches, les données
   et les documents tenus qui portent son nom, sous ses deux casses.
4. *Le Python, par les noms* : l'arbre syntaxique de tous les fichiers
   Python suivis ; pour chacune des 2 081 fonctions, méthodes et classes des
   65 jumeaux, les sortes de fichiers qui emploient son nom.

Une unité est dite *atteinte par rien* quand la production ne la nomme pas
et que rien ne l'exécute, ni la fabrique, ni un test, ni un écran ; *atteinte
par les seuls tests* quand la production ne la nomme pas et que la suite
l'exécute ; *nommée, jamais exécutée* quand la production la nomme et que
rien ne l'exécute.

## Le constat, dans le portage

| groupe de fichiers | fonctions, méthodes, classes | atteintes par rien | par les seuls tests | constantes que nul ne lit | nommées, jamais exécutées |
|---|---:|---:|---:|---:|---:|
| les 38 du moteur d'une carrière | 1 093 | 14 | 2 | 4 | 10 |
| la zone grise | 71 | 1 | 1 | 1 | 0 |
| les 24 qui restent des deux côtés | 601 | 21 | 0 | 6 | 45 |
| sans jumeau (le site, les agrégats, le cycle de vie, les lecteurs) | 892 | 4 | 6 | 1 | 42 |
| les lanceurs | 61 | 0 | 0 | 0 | 1 |
| **total** | 2 718 | 40 | 9 | 12 | 98 |

Les trois mesures s'accordent : aucune unité que l'arbre dit hors d'atteinte
n'est exécutée par la fabrique ni par un écran, hors deux fonctions de
`gabarit.js` que `construire_pages.py` appelle par leur nom, et que la
racine Python rattrape. Aucun module n'est hors d'atteinte.

### Atteintes par rien : 40 fonctions, 193 lignes

Toutes : la production ne les nomme pas, et ni la fabrique, ni les 8 174
tests, ni les écrans ne les exécutent. La colonne du jumeau dit qui nomme
la fonction Python du même nom, par la mesure des noms : « ni script ni
coût » quand seuls le moteur, son propre fichier ou des tests l'emploient.

*Vingt-quatre sans lecteur d'aucun côté*, confiance haute : rien ne les
attend.

| fichier | unité, ligne | jumeau Python |
|---|---|---|
| `agregats.js` | `SoldeFige.observees` 335, `DetteFigee.cumulInterets` 552 | sans jumeau |
| `chronologie.js` | `presomptionsEmployees` 1249 | les seuls tests |
| `distribution.js` | `DistributionPensions.sommeDesParts` 70 | les seuls tests |
| `droit/compter.js` | `droitRegimeSpecial` 1445 | les seuls tests ; nommée par une fiche |
| `equilibre.js` | `ComptesRetraite.ressourceEec` 523, `anneesTransferts` 686 | rien ; les seuls tests |
| `impot-revenu.js` | `impotDUnRevenuImposable` 1003 | les seuls tests |
| `journal.js` | `Journal.etatAu` 126 | les seuls tests |
| `lecture-pdf.js` | `textePdf` 1194 | sans jumeau |
| `mortalite.js` | `LoiMortalite.force` 114, `DonneesMortalite.utiliseTablesReelles` 294 | ni script ni coût ; les seuls tests |
| `pages.js` | `partRepriseBascule` 14123 | sans jumeau |
| `regimes.js` | `AgesCategorieActive.classements` 448, `CatalogueRegimes.enRepartition` 2758, `resoudreSuccession` 2770, `ValeursPoint.aUneConvention` 3495, `ContributionsEmployeurPubliques.couvertureMilitaires` 3727 | ni script ni coût, pour les deux premières ; les seuls tests ; rien ; les seuls tests |
| `remuneration.js` | `FicheDePaie.cotisationsPatronales` 705, `tauxRetraite` 729, `ecartBrutNet` 733, `ficheDePaiePossible` 1420 | les seuls tests ; ni script ni coût ; rien ; les seuls tests |
| `simulateur.js` | `Comparaison.tauxRemplacementProspectif` 264 | ni script ni coût |
| `taux.js` | `CourbeTauxSansRisque.forwardContinu` 112 | les seuls tests |

*Dix dans les 24 paires qui restent, que le Python lit et que rien ne lit en
JavaScript*, confiance haute pour le portage, moyenne pour le lecteur
Python, tenu des noms : le coût, la fabrique ou une étude emploie le nom de
l'exemplaire Python, qui lit le YAML ; le site ne lit pas le sien. Ce sont
des fonctions en double dont un seul côté sert.

| fichier | unité, ligne |
|---|---|
| `depenses.js` | `DepensesRetraite.prestation` 215 |
| `frontiere.js` | `TrancheComplementaire.part_au_dessus` 46 |
| `mortalite.js` | `LoiMortalite.esperance` 130, `DonneesMortalite.esperancePubliee` 307, `anneeNiveauxDeVie` 356 |
| `prelevements-historiques.js` | `PrelevementsHistoriques.tauxCsgPension` 195 |
| `regimes.js` | `DureesServicesMilitaires.categories` 503, `CatalogueRegimes.ouverts` 2762 |
| `tva.js` | `AssietteTva.recette` 66, `tauxMoyen` 73 |

*Six dans le moteur, dont un script ou le coût nomme encore le jumeau
Python* : mortes aujourd'hui, mais le lot qui portera ce lecteur au pont
leur en donnera un. À ne pas retirer avant les lots A à C. Les deux
premières lignes sont relues ; les autres lecteurs sont tenus des noms.

| fichier | unité, ligne | qui nomme le jumeau |
|---|---|---|
| `conversion.js` | `Convertisseur.effetAnticipation` 220 | une sonde de la prose (`scripts/mesures_prose.py:834`), que le lot A porte |
| `simulateur.js` | `Comparaison.renteCapitalisee` 283 | une sonde de la prose (`scripts/mesures_prose.py:193`), que le lot A porte |
| `remuneration.js` | `FicheDePaie.cotisationsSalariales` 701 | un script |
| `droit/limite_age.js` | `classeDe` 154 | un script ; nommée par deux fiches |
| `indexation.js` | `Indexation.historique` 197, `tauxReel` 216 | un script et le coût ; le coût |

### Atteintes par les seuls tests : 9 fonctions, 77 lignes

La production ne les nomme pas ; la suite les exécute.

| fichier | unité, ligne | ce qui la nomme encore |
|---|---|---|
| `agregats.js` | `CasTypesFiges.casType` 143, `CoutFige.cumulObserve` 592 | |
| `cycle-de-vie.js` | `revenusImposables` 781, `remplacementApresImpot` 1718 | le journal des référents (`data/reference/referents.yaml`) |
| `format.js` | `formatG` 154, `_sansZerosInutiles` 173 | |
| `impot-revenu.js` | `impotDuFoyer` 961 | |
| `remuneration.js` | `ProfilRemuneration.assietteAbattue` 348, `revenuAvantAbattement` 363 | la fiche `assiette_sociale_independants.yaml`, l. 153 ; un script lit le jumeau de la première |

### Atteintes par un seul nom dans une fiche

Trois fonctions que rien n'exécute et que seul le champ `code` d'une fiche
nomme encore : `droitRegimeSpecial` (`regles/priorite_majorations_enfants.yaml`,
l. 317 et 320, des deux côtés) ; `classeDe`
(`regles/limite_age_fonction_publique.yaml`, l. 372 et 376 ;
`regles/limite_age_militaires.yaml`, l. 176 et 180) ; et, en Python seul,
`PrelevementsPension.maladie_de_la_tranche`
(`regles/csg_des_pensions_selon_le_revenu.yaml`, l. 189). Aucune ancre de la
prose ne nomme un candidat ; une seule en dépend par son jumeau : celle de
`docs/methodologie.md`, l. 413, passe par la sonde qui appelle
`effet_anticipation`.

### Constantes que nul ne lit : 12, 62 lignes

Mesure statique seule : une constante s'évalue au chargement, l'exécution ne
dit rien d'elle. Sans aucun lecteur, tests compris : `PERIODES_NON_COTISEES`
(`carriere.js:45`), `FICHES_DES_PRIMES` (`droit/primes.js:17`), `ASSIETTES`
(`primes.js:16`). Nommées par des tests seulement : `REGIMES_FRAIS` et
`REGIMES_TAUX` (`config.js:543` et `556`), `CODES_SYSTEMES`
(`depenses.js:129`), `CONDITIONS` (`droit/compter.js:71`), `MOTIFS`
(`droit/reversion.js:51`), `CODES_POSTES` et `CODES_TRANSFERTS`
(`equilibre.js:95` et `206`), `SIGNATURE_SITE` (`gabarit.js:79`),
`HORS_CHAMP` (`impot-revenu.js:59`, 23 lignes).

### Nommées, jamais exécutées : 98 fonctions

La production les nomme — souvent par un nom de propriété, que la mesure ne
sait pas rattacher à sa classe —, et rien ne les exécute. Deux lectures, que
la mesure ne départage pas : un chemin du site qu'aucun test ne prend, ou une
morte qu'un homonyme tient. Les deux se voient à la main : `AssietteTva`
n'est bâtie que par la note de la TVA réformée (`pages.js:12198`), où ni la
page par défaut ni un test ne mène ; `PatrimoineMenages` est bâti par le
simulateur (`simulateur.js:602`) et lu à `pages.js:13407`, sans qu'aucune de
ses méthodes ne tourne jamais ; `fiabilite`, que douze unités portent, n'est
jamais exécutée sur sept d'entre elles.

- *`routeur.js`, 38 de ses 125 fonctions* : les gestes du lecteur que les 80
  tests d'écran ne font pas — la reprise et l'oubli de la saisie retenue
  (`reprendreLaSaisie` 1166, `oublierMemoire` 1073,
  `fusionnerAvecLaMemoire` 1380), la lecture au survol d'un tracé et de la
  cascade (`montrerLecture` 2187, `montrerCascade` 2369), la carte à publier
  (`imageDeCarteAPublier` 2904, `dessinerCarteAPublier` 2922), le filtre
  d'un tableau (`filtrer` 3263). Vivantes, sans test.
- *`patrimoine.js`, 11* : le module entier, hors ses constructeurs.
- *`tva.js`, 7 ; `effectifs.js`, 6 ; `regimes.js`, 6 ; `depenses.js`, 4 ;
  `assiette.js`, 3* : des accesseurs des données (`fiabilite`, `annees`,
  `caisses`, `fiche`, `serie`), pour la plupart en double avec le Python.
- *deux chacun* : `compte.js` (`ConstructeurCompte.fusionner` 460,
  `_baseSelonAssiette` 493), `equilibre.js`, `journal.js` (`length` 113,
  `entree` 117), `mortalite.js` (`populations` 301, `survie` 606),
  `remuneration.js` (`PrelevementsPension.net` 542, `brut` 547).
- *une chacun* : `age-reference.js` (`fiabilite` 121), `agregats.js`
  (`SoldeFige.projetees` 339), `bilan.js` (`EngagementFige.sensibilite` 119),
  `caracteristiques.js` (`partFemmes` 37), `cycle-de-vie.js`
  (`AnneeAutourDuDepart.dictionnaire` 2301), `distribution.js` (`partFemmes`
  93, 37 lignes), `droit/departs.js` (`demandes` 378), `droit/reversion.js`
  (`servieAu` 737), `fusion.js` (`partSalarialeMoyenne` 88),
  `lecture-pdf.js` (`plagesDe` 368, 36 lignes), `regimes.js` (`_jan` 2609),
  `saisie.js` et `serie.js` (deux classes d'erreur, jamais levées sous
  test), `scripts/budget_calcul.mjs` (`mesurer`, une étude hors de la suite).

Quatre d'entre elles, hors de `patrimoine.js`, sont nommées par un
identifiant résolu, non par une propriété, et ont donc un appelant certain
qui ne tourne jamais : `servieAu`, `partSalarialeMoyenne`, `plagesDe`,
`_jan`.

### Les exports

Des 1 521 unités de premier niveau que le portage exporte, 611 sont
importées par un autre module de la production et 85 lues par la fabrique à
travers `web/site.py`. Les 825 autres n'ont d'importeur que des tests — 68
par un fichier de `tests/js/`, 284 au plus par un nom dans un test Python,
le nom du jumeau y comptant à tort — ou n'en ont aucun : 473, dont 469
vivent dans leur fichier. Le portage exporte tout, comme un module Python
laisse tout lire. Ce n'est pas du code mort : le mot `export` de trop ne
coûte rien, et la liste n'est pas reproduite ici.

## Le Python

Par les noms seuls, sans exécution : une définition est dite sans lecteur
quand aucun fichier Python suivi n'emploie son nom hors de son propre corps.

| groupe | définitions | nommées par rien | par les seuls tests | par le moteur et les tests seuls |
|---|---:|---:|---:|---:|
| les 38 du moteur | 1 444 | 16, 84 lignes | 30, 394 lignes | — |
| la zone grise | 57 | 0 | 3, 40 lignes | — |
| les 24 qui restent | 580 | 5, 65 lignes | 25, 261 lignes | 41, 497 lignes |

**Le moteur, nommées par rien** : `carriere.py` `formater_borne` 3312 ;
`moteur/capitalisation.py` `rente_volontaire_mensuelle` 292 ;
`moteur/conversion.py` `taux_de_rente` 103 ; `remuneration.py`
`taux_retraite_du_droit_en_vigueur` 740, `maladie_de_la_tranche` 890,
`ecart_brut_net` 1333, `part_qui_arrive` 1338, `indemnites_des_lignes` 2147,
`gain_net_cumule` 2459, `epargne_cumulee` 2464,
`epargne_volontaire_mensuelle` 2470, `conversion_possible` 2778 ;
`scenarios/actuel.py` `a_une_convention` 3243 ; `simulateur.py`
`aujourd_hui_en_euros_constants` 229, `financement_regimes` 934,
`scenario_employeur` 1151.

**Le moteur, par les seuls tests** : `carriere.py` `depuis_lignes` 2206,
`prolonger_releve` 2624 (70 lignes), `bornes_deformation` 3216,
`hors_routage` 3465 ; `chronologie.py` `presomptions_employees` 1235 ;
`droit/compter.py` `droit_regime_special` 1503 ; `droit/releve.py`
`revenu_des_points` 339 ; `journal.py` `etat_au` 109 ;
`moteur/capitalisation.py` `capital_transmissible` 203,
`taux_cotisation_obligatoire` 261, `capital_obligatoire` 283,
`rente_obligatoire` 296 ; `remuneration.py` `revenu_avant_abattement` 733,
`maladie_des_regimes_speciaux` 894, `assiette_maladie` 925,
`cotisations_patronales` 1295, `fiche_de_paie_possible` 2264,
`gain_net_mensuel` 2455, `epargne_volontaire_cumulee` 2475,
`gain_net_mensuel_apres_volontaire` 2481, `verse_le_volontaire` 2486,
`bute_sur_le_smic` 2491, `salaire_brut_depuis_net` 2651 (59 lignes),
`salaire_net_depuis_brut` 2726 ; `simulateur.py` `taux_remplacement_total`
332, `constructeur_liberal` 1125, `scenario_notionnel` 1146,
`sous_le_plancher` 1490, `au_dessus_du_plafond` 1495, `niveau_pour_pension`
1500 (42 lignes). La zone grise : `impot_revenu.py`
`taxe_complementaire_des_revenus` 1100, `impot_du_foyer` 1163,
`impot_d_un_revenu_imposable` 1217.

**Les 24, nommées par rien** : `contributions_equilibre.py`
`part_salariale_annualisee` 278 ; `donnees/equilibre.py` `ressource_eec`
755 ; `donnees/mortalite.py` `enregistrer_cache` 699 ; `donnees/tva.py`
`variation_prix` 135 ; `frontiere.py` `frontiere_depuis_paquet` 130.

**Les 24, par les seuls tests** : `config.py` `sous_regime_frais` 1234,
`sous_regime_taux` 1267, `taux_retraite_propose` 1415 ; `contexte.py`
`inventaire_avantages` 187 ; `contributions_equilibre.py`
`contributions_d_une_carriere` 242 ; `donnees/depenses.py`
`annees_ventilees` 238, `pensions_droit` 299 ; `donnees/distribution.py`
`somme_des_parts` 248 ; `donnees/equilibre.py`
`depense_maximale_toutes_variantes` 396, `premiere_annee_eec` 748,
`derniere_annee_eec` 752, `solde_eec` 781, `ressource_groupe` 856,
`annees_ventilees` 881, `transfert_part_ressources` 900, `annees_transferts`
1005 ; `donnees/macro.py` `delai_entree_fonction_publique` 946,
`derniere_liquidation_revalorisee` 1195 ; `donnees/mortalite.py`
`utilise_tables_reelles` 622 ; `donnees/prelevements_historiques.py`
`taux_deductible_pension_annuel` 263, `hors_retraite_annuel` 374,
`non_deductibles_annuel` 405 ; `donnees/regimes.py` `couverture_militaires`
1186, `resoudre_succession` 2489 ; `donnees/taux.py` `forward_continu` 217.

**Ce que la mesure recoupe de la question 4.** Par les noms, 71 des 580
définitions des 24 fichiers n'ont de lecteur ni dans le reste de `src/` ni
dans un script : 30 dès aujourd'hui, 41 que le moteur seul lit. La question 4
en compte 79 à 125, sur les seules 291 fonctions en double. Les deux mesures
sont du même ordre et ont le même défaut, la centaine de fonctions qu'un
autre nom de leur fichier tient (100 ici, le « ricochet » de la question 4) :
celle-ci confirme le plancher et ne dit rien du plafond. Elle ajoute deux
choses. Trente de ces définitions n'attendent pas le lot F : elles sont sans
lecteur aujourd'hui, le moteur compris. Et le portage en porte le miroir :
dix fonctions en double que seul le Python lit, plus les 45 nommées et
jamais exécutées de la moitié JavaScript, où la liste des fonctions « tenues »
de la question 4 se raccourcirait d'autant.

## Ce qui est recommandé, lot par lot

- **Lot A, en cours** : rien à retirer. Ses sondes portées donneront un
  lecteur à `Convertisseur.effetAnticipation` et à
  `Comparaison.renteCapitalisee` : ne pas y toucher.
- **Lot B** : même réserve pour `classeDe`, `cotisationsSalariales`,
  `Indexation.historique` et `tauxReel`, jusqu'à ce que le script qui lit
  leur jumeau soit porté ou tranché.
- **Lot C** : la paire de l'impôt se tranche avec ses trois morts du portage
  (`impotDUnRevenuImposable`, `impotDuFoyer`, `HORS_CHAMP`) et les trois
  fonctions Python que seuls des tests lisent.
- **Lot D** : les 9 fonctions que seuls des tests atteignent se décident
  avec leurs tests — une interface éprouvée qu'on garde, ou un test qui part
  avec elle. Les 60 nommées et jamais exécutées hors du routeur sont la
  liste de ce que les tests portés doivent couvrir, ou révéler mort ; les 38
  du routeur, celle des gestes sans test d'écran.
- **Lot E** : ne rien retrancher de la relecture du Python au titre du code
  mort, 1 % ne le vaut pas ; mais la session qui relit une paire part de
  cette liste : une fonction morte des deux côtés ne se compare pas, elle se
  note à retirer.
- **Lot F** : le moteur Python part entier, ses morts avec lui ; les fiches
  qui nomment `droit_regime_special`, `classe_de` et
  `maladie_de_la_tranche` se rebranchent sans ces noms.
- **Lot G** : avant de dresser la liste des fonctions en double, retirer ce
  qui est mort des deux côtés des 24 paires — 21 fonctions et 6 constantes du
  portage, 30 définitions du Python — et trancher les 45 jamais exécutées :
  la liste en sort plus courte.

**Une session de retrait, courte, peut s'ouvrir sans attendre** : les 24
fonctions sans lecteur d'aucun côté, les 10 que seul le Python lit, les 3
constantes sans aucun lecteur, et les jumeaux Python des 24 paires que rien
ne nomme — une quarantaine d'unités du portage, moins de 200 lignes. Elle ne
croise ni le lot A ni le lot B si elle laisse les six fonctions réservées. Le
gain est mince : c'est la netteté de la liste de la question 4 qu'elle sert,
plus que la taille du dépôt.

## Ce que le propriétaire tranche

1. Le retrait du code mort du portage : une session dès maintenant
   (recommandé, hors les six fonctions réservées), ou au fil des lots, chaque
   session retirant les morts de la paire qu'elle relit.
2. Les 9 fonctions que seuls des tests atteignent, et les 9 constantes que
   seuls des tests nomment : gardées comme interface éprouvée, ou retirées
   avec leurs tests.
3. Les 98 nommées et jamais exécutées : laissées au lot D, qui les couvre ou
   les révèle (recommandé), ou instruites à part, une à une.
4. Les exports sans importeur : laissés tels quels (recommandé).

## Ce qui est vérifié, ce qui est déduit

*Vérifié en faisant tourner le code* : qu'aucune des 40 n'est exécutée par
la fabrique, par la suite ni par les tests d'écran ; que les 9 le sont par
la suite et non par la fabrique ; que les 98 ne le sont par rien.

*Vérifié en lisant le code* : onze candidats relus par leurs occurrences
(`partRepriseBascule`, `textePdf`, `PERIODES_NON_COTISEES`,
`FICHES_DES_PRIMES`, `ASSIETTES`, `ressourceEec`, `part_au_dessus`,
`enRepartition`, `aUneConvention`, `tauxRemplacementProspectif`,
`ecartBrutNet`) ; les mentions des fiches, à leur ligne ; les deux chemins
du site sans test, `pages.js:12198` et `13407` ; quatre exports sans
importeur ; les noms que les scripts de la fabrique lisent du site.

*Déduit* : pour les autres candidats, « la production ne la nomme pas »
tient à la résolution des noms par le script, non à une relecture. Un accès
calculé (`objet[nom]`) lui échapperait, mais non à l'exécution, et les deux
s'accordent. Le pont est compté comme une racine : que chacune de ses douze
lectures et de ses 42 fonctions du droit ait un appelant hors des tests
n'est pas mesuré. Les études hors de la fabrique ne font tourner le portage
que par leurs tests. Le partage des 98 entre chemin sans test et morte sous
un homonyme n'est pas fait. Toute la mesure du Python est par les noms : un
nom commun compte à tort un lecteur, et rien n'y est exécuté.

*Non mesuré* : ce qu'un lecteur fait dans son navigateur au-delà des 80
tests d'écran ; le code mort à l'intérieur d'une fonction vivante, branche
par branche ; les constantes, par l'exécution.

**Ce qui ne change pas.** Aucun code, aucune donnée, aucun test, aucun
script, aucune garde, aucune règle du scénario 1, aucun chiffre publié. Le
bloc « Reprise » de l'action n'est pas récrit. La régénération rejouée dans
le clone a rendu les fichiers fabriqués de 3944fdc, à un fichier près, que
la session n'a pas relevé avant d'effacer le clone.

**Tests.** `python -m pytest -m rapide` et les tests de la feuille de route
(`tests/test_prose.py`) ; la prose vérifiée. La suite complète, rejouée dans
le clone sur 3944fdc : 8 100 verts, 73 sautés, un rouge,
`test_le_tableau_de_bord_n_est_pas_perime` (`docs/etat.md`, que GitHub
refait), sans rapport avec cette note.
