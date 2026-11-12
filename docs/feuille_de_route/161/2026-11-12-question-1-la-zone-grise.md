# Question 1, la zone grise : ce que chaque élément devient, mesuré dans le code

**La recommandation.** Aucun élément de la zone grise ne passe en Python
seul. L'impôt sur le revenu et le cœur de `RevalorisationServie`, avec
`Indexation`, s'écrivent en JavaScript seul, le coût les demandant au pont
par lot : le lecteur en change le résultat, c'est vérifié. La garantie de
population aussi, en JavaScript seul — contre la lettre du critère, qui
dirait Python seul, et c'est le seul point où la session s'en écarte ; le
propriétaire tranche. La restitution n'est pas dans la zone grise : aucun
Python de production ne l'appellera plus, le moteur parti ; elle part avec
lui, sans pont. Les variantes des comptes restent des deux côtés, dites
« tenues » : trois lignes sur un chargeur qui reste. Le lot C tient en trois
à quatre sessions au lieu de quatre à cinq. Cette session n'a rien retiré ni
modifié.

**La demande.** L'inventaire du 9 novembre
(`2026-11-09-l-inventaire-des-retraits.md`) pose cinq questions au
propriétaire ; celle-ci est la première. La note de décision 0006 donne le
critère : en JavaScript seul si le lecteur du site peut changer le résultat,
le coût le demandant au pont par lot ; en Python seul sinon, le site lisant
le résultat figé. L'inventaire lisait l'impôt et `RevalorisationServie` du
côté du JavaScript, sans avoir vérifié la garantie, la restitution ni les
variantes des comptes.

**La méthode.** Sur cbd46ee, quatre essais jetables, hors du dépôt, non
commités : un coût de référence (`calculer_cout`, sans mémoire) sous
`cProfile`, pour compter les appels ; `pont.droit` chronométré, par lot et
demande par demande ; la garantie de population et la revalorisation servie
calculées dans les deux langages sur une même grille, comparées au bit ; et
la lecture du code, aux lignes citées. Deux recherches confiées à
l'éclaireur : les réglages que le lecteur atteint, les tests qui confrontent
les deux exemplaires. L'arbre de travail est propre à la fin.

## Élément par élément

| élément | le lecteur en change-t-il le résultat ? | appels dans un coût de référence | concordance aujourd'hui | recommandation |
|---|---|---:|---|---|
| l'impôt sur le revenu | oui : sa carrière (`cycle-de-vie.js`) | 18 830 | confrontée par un test | JavaScript seul, le pont par lot d'une année |
| `RevalorisationServie`, le cœur, et `Indexation` | oui : l'indexation, le stock, la bascule | 1 446 000 lectures, 129 taux | au bit, par l'essai ; aucun test direct | JavaScript seul, le pont rendant des séries |
| `RevalorisationServie`, l'histoire du droit | sans objet : le site ne l'a pas | 1 116 000 lectures, 11 232 valeurs du point | sans jumeau | reste en Python, au coût ; ses appels au droit par `pont.droit` |
| la garantie de population | non | 876 chiffrages | au bit, par l'essai ; aucun test direct | JavaScript seul, le pont à chaque chiffrage (Python seul selon le critère) |
| le complément de garantie d'une personne | oui : c'est le moteur | 21 195, par la garantie de population | par les témoins du moteur | JavaScript seul, comme le moteur |
| la restitution | non | 0 | par les témoins de la fiche de paie ; aucun test direct | JavaScript seul, sans pont : elle part avec le moteur |
| les variantes des comptes | oui, mais c'est un accesseur | 0 dans le coût, une par clé de la mémoire | aucun test direct | les deux, tenues ; `depense_maximale_toutes_variantes` quitte le Python |

**L'impôt sur le revenu.** Le site le calcule sur la carrière du lecteur :
`cycle-de-vie.js` importe `impot-revenu.js` (ligne 221) et appelle
`impotAuxParametres` année par année (lignes 1607, 1674, 1750). Le Python
seul est donc exclu. Côté Python, un seul appelant de production :
`effet_retour.EffetRetour._impot` (`effet_retour.py:304`), que
`cout._avenir` bâtit une fois (`cout.py:4724`) et chiffre chaque année
(`cout.py:4853`). Mesuré : 81 années chiffrées, 15 410 pensions prélevées,
18 830 impôts calculés, deux secondes des soixante du coût sous profileur ;
34 fonctions de `impot_revenu.py` exécutées, comme à l'inventaire. Par le pont : un lot par année,
et un second pour les années d'avant 2015, où l'impôt au taux plein décide
de la tranche de CSG avant d'être recalculé (`_preleve_historique`) ; moins
d'une seconde par coût, déduit du prix mesuré d'une demande. Demande par
demande, les 18 830 appels coûteraient huit secondes : le lot s'impose ici.
La concordance est tenue par un vrai test,
`test_l_impot_de_chaque_foyer_se_retrouve_en_javascript`
(`tests/test_cycle_de_vie_portage.py:222`), qui fait tourner node sur une
grille de foyers, d'années et de revenus. Le chargeur des barèmes
(`donnees/impot_revenu.py`, 274 lignes, que la carte ne compte pas parmi ses
65 paires) reste ; sa projection (`chronique`, `_projeter`), que le portage
refait dans `impot-revenu.js`, n'aura plus d'appelant de production et suit
la règle. Restent à porter les tests écrits contre le Python, tirés de la
brochure, d'OpenFisca et de l'IPP : `tests/test_impot_revenu.py`
(1 482 lignes) et `tests/test_referents.py`.

**`RevalorisationServie` est deux choses.** Le portage n'en porte que le
cœur (`revalorisation.js:1114` à 1238) : l'index du compte, bâti sur
`Indexation.taux` et le préfinancement, la valeur de service convenue, et
quatre lectures (`coefficient`, `coefficientStock`, `coefficientPoints`,
`regimeConvenu`). Le lecteur en change le résultat : sa saisie règle
`mode_indexation`, `lissage_indexation`, `revalorisation_stock` et
`annee_bascule` (`saisie.js:1803` à 1821), et son cycle de vie bâtit la
classe sur son simulateur (`cycle-de-vie.js:986`). Le Python y ajoute ce que
le coût seul lit, sans jumeau (`revalorisation.py:1747` à 1859, 1911 à
1955) : `coefficient_historique` et ses règles, `coefficient_nominal`,
`pour_la_proposition`, `regime_de_tete`.

- *Le cœur* : JavaScript seul. Mesuré dans un coût : 129 appels à
  `Indexation.taux`, tous au constructeur, puis 724 617 `coefficient_stock`,
  qui appellent 557 377 fois `coefficient`, et 163 961 `coefficient_points` :
  rien que des rapports de deux valeurs d'une série. Appel par appel, le pont y passerait
  dix minutes ; le lot est ici une demande par jeu de paramètres, qui rend
  les séries, et le Python garde une classe du même nom qui les lit — ses
  huit appelants hors du moteur (`cout.py:5152` et 5512,
  `bilan_compte.py:400`, `facteurs_depense.py:833`, les deux contrôles,
  `grille_large.py:5423`, `indexation_scenario_6.py:216`) ne changent pas. Reste la règle du stock à
  la bascule, dix lignes (`revalorisation.py:1957`) : la session du lot dira
  si elle se rend en séries, une par régime du stock, ou si elle se dit
  tenue. `Indexation.coefficient` (`cout.py:5361`), que le coût n'appelle que
  sous une variante démographique, est le produit des mêmes taux : il lit la
  même série. Les deux exemplaires concordent au bit sur 1 350 coefficients,
  sous les réglages de référence, le stock réindexé et le triple verrou
  inversé ; aucun test de la suite ne les confronte directement.
  `coefficient_points` n'est pas éprouvé : aucun régime n'a de valeur de
  service convenue sous les réglages de référence.
- *L'histoire du droit* : reste en Python, c'est du coût ; à la coupe de
  `revalorisation.py`, elle rejoint le coût. Elle appelle cinq règles du
  moteur pour bâtir ses moyennes annuelles : `liquider.valeur_du_point`
  (11 232 appels mesurés), `RevalorisationsPensions.generale` et `retenues`,
  `minimum_garanti.ratio_point_indice`, `conversions_points.echelle`. C'est le
  cas que la note 0006 a prévu, l'étude qui demande au pont, par lot, une
  fonction du moteur. Mesuré : 11 232 valeurs du point par `pont.droit` en
  0,2 seconde, d'une seule demande. `pont.droit` ne sert aujourd'hui que la
  première des cinq (`pont.py:1249`) ; les quatre autres sont à y déclarer.

**La garantie.** `garantie.py` porte deux choses. Le complément d'une
personne (`complement_garantie`, quinze lignes) est une règle du moteur, que
le portage sert au lecteur (`scenario-notionnel.js:294`,
`revalorisation.js:1081`) : JavaScript seul, sans débat. La garantie de
population — `cout_garantie`, `cout_garantie_par_sexe`, `_manque_moyen`,
`facteurs_par_sexe`, `pension_moyenne` — intègre ce barème sur la
distribution des pensions. Le site la refait onze fois, dans deux
fonctions : `coutDetailGarantie` (`pages.js:13236`, la page « Coût ») et
`programmeGarantie` (`pages.js:16902`, l'accueil). Aucun de leurs arguments
ne vient du lecteur : ils lisent `contexte.base`, qui est `PARAMETRES_DEFAUT`
(`contexte.js:118`), le paquet et le coût figé ; et aucun des quatre
paramètres de la garantie n'est un réglage de la saisie (`saisie.js:1801` à
1824). Le critère dit donc : Python seul, le site lisant onze résultats
figés.

La session recommande pourtant le JavaScript seul, pour quatre raisons
mesurées.

1. Le Python seul garde le barème en deux exemplaires : `_manque_moyen`
   appelle `complement_garantie` 21 195 fois par coût, au fond de son
   intégrale, et le moteur du lecteur garde le sien.
2. Le site ne relit pas ce que le coût produit : il chiffre d'autres cas,
   deux planchers sous deux assiettes, trois rapports entre les sexes. Les
   figer, c'est récrire en Python une centaine de lignes de `pages.js`
   (13255 à 13350), ajouter un bloc aux agrégats et retoucher deux pages,
   dans la zone du site.
3. Le pont ne coûte presque rien ici : 876 chiffrages par coût (147 par
   `GarantieDistribution.chiffrer`, 729 par l'ASPA de l'effet retour,
   `effet_retour.py:266`), à 0,44 milliseconde la demande mesurée, soit une
   demi-seconde sur soixante. Le coût passe déjà par node pour sa grille.
   La boucle de `cout._avenir` n'a pas à être refaite en deux passes.
4. Les deux exemplaires concordent au bit sur 1 200 nombres : cinq
   facteurs, quatre planchers, trois formes du barème, l'ensemble et les
   deux sexes. Les agrégats resteront donc identiques à l'octet, ce qui est
   la garde du retrait.

Ce que le JavaScript seul coûte : une part du coût, intégrer un barème sur
une population, se lit alors dans le portage et non dans `cout.py`. Aucun
test de la suite ne confronte les deux garanties de population :
`tests/js/garantie-degressive.test.js` n'éprouve que le portage, sur des
valeurs posées à la main, et
`test_le_moteur_python_sert_le_meme_bareme_que_le_portage`
(`tests/test_garantie_degressive.py:77`), que `jumeaux.py --couverture`
compte par son nom, n'appelle pas node. La confrontation s'écrit avant le
retrait ; l'essai montre qu'elle sera verte.

**La restitution.** Elle n'est pas dans la zone grise au sens de la note
0006 : le coût ne l'appelle pas (zéro appel mesuré ; « 0 sur 9 » à
l'inventaire). Ses trois appelants Python hors des tests sont
`remuneration.py:2569`, une règle du moteur, qui part avec lui ;
`contexte.py:157`, que rien n'appelle hors des tests ; et la sonde de
`mesures_prose.py:1625`, que le lot A passe au portage. Le portage, lui, la
calcule sur le paquet pour la fiche de paie du lecteur
(`remuneration.js:1898`) et pour trois passages des pages
(`contexte.js:212`). Le lecteur n'en change pas le résultat —
`part_rendue_aux_salaires` n'est pas un réglage de la saisie —, et le
critère dirait Python seul : il faudrait alors écrire dans le paquet une
table que la fabrique ne calcule pas aujourd'hui, pour retirer un calcul
que le navigateur fait sur trois séries. Le JavaScript seul ne coûte rien :
`restitution.py` part au lot F, ses huit tests portés au lot D. Aucun test
ne confronte les deux directement ; les témoins du moteur les tiennent par
la fiche de paie, ce qui est déduit.

**Les variantes des comptes.** Trois fonctions de `donnees/equilibre.py`,
une paire de données, qui reste des deux côtés. `variantes_disponibles` est
un chargeur, que la fabrique appelle (`construire_donnees.py:347`) : il
reste. `variante_du_scenario`, trois lignes, choisit le compte du COR sous
le scénario de projection, que le lecteur règle ; le Python l'appelle pour
la clé de la mémoire (`memoire.py:673`), les facteurs de la dépense
(`facteurs_depense.py:839`), le contexte et la grille large. La demander au
pont coûterait plus que ses trois lignes : les deux, dites tenues, sous un
test de confrontation qui manque aujourd'hui. `depense_maximale_toutes_variantes`
n'a plus qu'un test pour lecteur côté Python (`tests/test_cout.py:5019`),
quand le site s'en sert (`pages.js:9378`) : elle quitte le Python, selon la
règle des accesseurs de la note 0006.

## Le critère

Il trie bien ce que le coût appelle encore, et la vérification le confirme
pour l'impôt et la revalorisation servie. Deux précisions le rendraient
exact.

- *Une question le précède* : le moteur parti, un Python de production
  appelle-t-il encore le calcul ? Sinon, il n'est pas dans la zone grise, et
  part avec le moteur. C'est la restitution, que le critère enverrait à tort
  au Python.
- *Il se pose par fonction, non par fichier.* `garantie.py`,
  `RevalorisationServie` et `donnees/equilibre.py` portent chacun une part
  qui est du moteur, une qui est du coût, parfois un chargeur.

Sa seconde branche, « en Python seul sinon », suppose que le site relit ce
que le coût produit. La garantie de population montre le cas contraire : le
site chiffre d'autres cas, et le calcul repose sur une règle du moteur. La
session propose de la borner ainsi : en Python seul si le site n'affiche que
ce que la fabrique calcule déjà, et si le calcul n'appelle aucune règle du
moteur ; en JavaScript seul sinon. Aucun élément de la zone grise ne passe
alors en Python seul.

## Ce que cela change au lot C

| session | ce qu'elle fait |
|---|---|
| C1 | La garantie : sa confrontation, la demande au pont, `GarantieDistribution` et `_garantie_distribution` branchés, `garantie_par_sexe.py` suivi, `garantie.py` retiré |
| C2 | L'impôt de l'effet retour : la demande au pont, par année, `EffetRetour` branché |
| C3 | `RevalorisationServie` : les séries par le pont, la classe Python réduite à leur lecture, `Indexation.coefficient` sur la même série |
| C4 | L'histoire du droit : quatre fonctions de plus à `pont.droit`, `_nominal` par lot, la part du coût sortie de `revalorisation.py` ; à joindre à C3 si elle tient |

La restitution et les variantes des comptes ne demandent plus de session au
lot C : la première part au lot F, les secondes se disent tenues au lot G.
Le lot D gagne les tests de l'impôt à porter, le lot E la relecture de
`impot_revenu.py`, 1 320 lignes. Si le propriétaire retient le Python seul
pour la garantie, C1 devient deux sessions, l'une sur les agrégats, l'autre
sur les pages, à ne pas mener en même temps qu'une session du site.

## Ce qui est vérifié, ce qui est déduit

*Vérifié en faisant tourner le code* : les comptes d'appels d'un coût de
référence, 59,5 secondes sous profileur ; le prix du pont, 11 232 appels en
0,2 seconde d'un lot, 1 824 demandes d'un appel en 0,8 seconde ; la
concordance au bit de la garantie de population (1 200 nombres) et du cœur
de la revalorisation servie (1 350 coefficients, trois jeux de paramètres).

*Vérifié en lisant le code* : les appelants de chaque élément, aux lignes
citées ; ce que la saisie règle ; que `contexte.base` est le jeu de
référence ; le test de l'impôt.

*Rapporté par l'éclaireur, relu aux lignes citées seulement* : la liste des
dix-neuf réglages du lecteur ; l'absence de test confrontant pour la
garantie de population, la revalorisation servie, la restitution et les
variantes, cherchée par leurs noms — un test qui les confronterait sous un
autre nom a pu échapper.

*Déduit* : les temps par le pont de l'impôt et de la garantie, tirés du prix
d'une demande et non d'une demande écrite ; la concordance de la restitution
et du complément par les témoins ; les nombres de sessions.

*Non mesuré* : les six autres coûts que la fabrique fige (les variantes
d'espérance de vie, de fécondité et de migrations, `construire_donnees.py`
vers la ligne 2565), le coût des avantages et le bilan du compte ;
`Indexation.coefficient`, que seule une variante appelle ; les études hors de
la fabrique.

**Ce qui ne change pas.** Aucun code, aucune donnée, aucun test, aucune
garde, aucune règle du scénario 1, aucun chiffre publié ; le bloc
« Reprise » de l'action, que la session d'orchestration tient.

**Tests.** Aucun n'est ajouté : la session instruit. La prose vérifiée
(`python scripts/verifier_prose.py --corriger`), et les tests de la feuille
de route (`tests/test_prose.py`).
