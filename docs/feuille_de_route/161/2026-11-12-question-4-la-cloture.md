# Question 4, la clôture : ce que portent les 24 paires qui restent, ce qui les tient, et le critère qu'un test peut vérifier seul

**La recommandation.** Clore l'action par fonction, non par paire : *aucune
fonction ne porte le même nom des deux côtés d'une paire, hors d'une liste
déclarée où chaque entrée nomme le lecteur Python qui reste et le test qui
confronte les deux exemplaires.* Un test de la carte le vérifie seul, et
rougit à la première fonction écrite deux fois sans être déclarée. Dire
« tenues » les 24 paires, comme le propose l'inventaire, ne suffit pas pour
deux raisons mesurées ici : ces paires logent des règles du moteur, entre 79
et 125 de leurs 291 fonctions en double, que plus rien ne lira en Python une
fois le moteur parti ; et 18 des 24 n'ont aucun test qui confronte leurs deux
exemplaires. Ce qui les accorde aujourd'hui est le moteur Python, que le lot
F retire : la liste et son test de confrontation doivent donc venir avant le
lot F, non après. Le lot G passe de 1 à 2 sessions à 3 ou 4, en deux temps.

**La demande.** Le propriétaire a demandé une session neuve par question en
suspens de l'inventaire du 9 novembre
(`2026-11-09-l-inventaire-des-retraits.md`), chacune analysant le meilleur
choix. Celle-ci instruit la quatrième : après le retrait des 38 paires du
moteur, 24 restent des deux côtés (note de décision 0006) ; faut-il que la
carte les dise « tenues », et que l'action se close quand plus aucune règle
du moteur n'a deux exemplaires ? Aucun code ne change, rien n'est mis en
œuvre : le propriétaire tranche.

**La méthode.** Quatre mesures, sur cbd46ee, par des scripts écrits hors du
dépôt et non commités.

1. *Les fonctions de chaque côté* : l'arbre syntaxique du jumeau Python, ses
   fonctions et ses méthodes hors `__init__` et consorts ; les fonctions et
   les méthodes du jumeau JavaScript, relevées par une expression régulière.
   Deux fonctions sont dites en double quand elles portent le même nom, au
   passage près de `nom_long` à `nomLong`, que l'architecture exige (§ 7.1 :
   « fonction par fonction, avec les mêmes noms »).
2. *Qui lit l'exemplaire Python* : pour chaque fonction en double, les
   fichiers Python suivis qui emploient son nom, rangés en quatre sortes — les
   41 jumeaux qui partent ou se tranchent (moteur et zone grise), le reste de
   `src/`, les scripts, les tests.
3. *Les fonctions en double hors de la paire* : les noms d'au moins douze
   lettres qu'un fichier Python partage avec un fichier JavaScript qui n'est
   pas son jumeau.
4. *Les tests de confrontation* : relevés par l'éclaireur dans `tests/`, les
   six qu'il a trouvés relus ensuite à leur ligne.

## 1. Ce que portent les 24 paires

Les 24 sont les 18 de `donnees/`, les 3 du socle (`config.py`,
`calendrier.py`, `noyau/versions.py`) et les 3 moitiés de la fabrique
(`contexte.py`, `frontiere.py`, `contributions_equilibre.py`) : 12 889 lignes
de Python, 10 943 de JavaScript. Elles comptent 493 fonctions en Python et
521 en JavaScript ; 291 portent le même nom des deux côtés, dont 142 font au
moins une opération arithmétique. Les comptes diffèrent de ceux de
l'inventaire, qui gardait les méthodes spéciales.

Aucune paire n'est d'une seule sorte. Chaque fichier mêle quatre choses :

- *le chargeur*, qui n'existe qu'en Python (`charger_*`, les `__init__` qui
  lisent le YAML) : 202 fonctions sans homonyme. Il n'est pas un doublon ;
- *ce que le site seul calcule*, qui n'existe qu'en JavaScript : 216
  fonctions, dont 123 dans `regimes.js` et 62 dans `contexte.js` ;
- *des accesseurs et des calculs que les deux côtés exécutent*, le Python
  sur le YAML pour le coût, la fabrique et les études, le JavaScript sur le
  paquet pour le site : les vrais doublons qui restent par décision ;
- *des règles du moteur logées là*, que seuls le moteur Python et des tests
  lisent en Python : elles partent avec lui, par la note 0006 (« ne partent
  que ceux que seuls des tests lisent »).

Le tableau donne, pour chaque paire : ses fonctions en Python et en
JavaScript ; celles en double, et combien calculent ; combien n'ont plus de
lecteur Python qui reste, du plancher au plafond ; le test qui confronte les
deux exemplaires. Le plancher compte une fonction lue dès qu'un fichier qui
reste emploie son nom, ou qu'une fonction lue de son fichier l'appelle ; le
plafond écarte ce ricochet. Le vrai nombre est entre les deux.

| paire | Python, JavaScript | en double, dont calculs | sans lecteur qui reste | confrontation directe |
|---|---:|---:|---:|---|
| `contributions_equilibre.py` | 14, 10 | 8, 5 | 4 | une fonction |
| `contexte.py` | 15, 76 | 14, 1 | 2 à 4 | aucune |
| `frontiere.py` | 9, 5 | 5, 4 | 0 | aucune |
| `donnees/bilan.py` | 21, 19 | 14, 3 | 1 à 2 | aucune |
| `donnees/tva.py` | 11, 8 | 9, 5 | 1 à 2 | aucune |
| `donnees/depenses.py` | 18, 12 | 11, 4 | 2 | aucune |
| `donnees/vie_en_couple.py` | 2, 2 | 2, 1 | 0 | aucune |
| `donnees/caracteristiques.py` | 7, 7 | 7, 5 | 1 à 3 | aucune |
| `noyau/versions.py` | 3, 1 | 1, 1 | 1 | aucune |
| `donnees/distribution.py` | 8, 3 | 3, 2 | 1 | aucune |
| `donnees/effectifs.py` | 10, 8 | 4, 0 | 0 | aucune |
| `donnees/taux.py` | 13, 7 | 7, 6 | 1 à 3 | aucune |
| `donnees/patrimoine.py` | 12, 11 | 11, 6 | 0 à 4 | aucune |
| `donnees/indemnite_csg.py` | 6, 6 | 5, 4 | 1 à 3 | aucune |
| `donnees/assiette.py` | 8, 6 | 6, 2 | 0 | aucune |
| `donnees/equilibre.py` | 42, 30 | 30, 12 | 8 à 14 | aucune |
| `donnees/prelevements_historiques.py` | 29, 31 | 28, 19 | 21 | quatre méthodes |
| `calendrier.py` | 10, 11 | 10, 8 | 3 à 5 | une fonction |
| `donnees/primes.py` | 12, 11 | 10, 5 | 1 à 4 | aucune |
| `donnees/mortalite.py` | 39, 29 | 26, 14 | 1 à 10 | une fonction |
| `donnees/macro.py` | 69, 30 | 24, 16 | 8 à 16 | aucune |
| `donnees/chargement.py` | 51, 9 | 4, 2 | 0 | aucune |
| `donnees/regimes.py` | 75, 180 | 44, 15 | 16 à 20 | une constante |
| `config.py` | 9, 9 | 8, 2 | 6 | les valeurs de référence |
| **total** | 493, 521 | 291, 142 | 79 à 125 | 6 paires sur 24 |

**Les paires qui portent des règles du moteur, à couper plutôt qu'à dire
tenues.** Vérifié en lisant qui les importe hors du moteur.

- `donnees/prelevements_historiques.py` : les prélèvements d'une paie et
  d'une pension (`hors_retraite`, l. 347 ; `non_deductibles`, l. 382 ;
  `bareme_independant`, l. 134 ; `taux_pension`, l. 221). Hors du moteur
  (`remuneration.py:249`, `scenarios/actuel.py:83`), le Python n'en lit que
  le chargeur (`scripts/construire_donnees.py:1445`, `effet_retour.py:101`)
  et un accesseur d'une ligne, `csg_deductible_pension`
  (`effet_retour.py:298`). 21 de ses 28 fonctions en double partent.
- `donnees/indemnite_csg.py` et `donnees/primes.py` : l'indemnité
  compensatrice et les primes soumises à retenue, que seuls lisent le moteur
  (`remuneration.py`, `droit/primes.py`, `droit/acquerir.py`,
  `droit/liquider.py`, `moteur/compte.py`) et le chargeur de la fabrique
  (`construire_donnees.py:1524` et `1550`) ; `scripts/mesures_prose.py`
  nomme aussi la première.
- `noyau/versions.py` : `applicable` (l. 60), la seule fonction en double,
  n'est appelée que du moteur (`droit/limite_age.py:228`,
  `scenarios/actuel.py:1338` et `1349`) ; la fabrique n'en lit que
  `preparer`. La paire n'en est plus une après le lot F.
- `contributions_equilibre.py` : `contributions_d_une_carriere` (l. 242) et
  `part_salariale_annualisee` (l. 278), que le cycle de vie du site calcule
  (`contributions-equilibre.js:119` et `151`), n'ont pour lecteurs Python
  que des tests ; le reste du dépôt n'en lit que le chargeur
  (`integration_complementaires.py:69`, `construire_donnees.py:1498`).
- `donnees/regimes.py` : les méthodes de `PeriodeRegime` (`part_du_revenu`,
  l. 951 ; `points_garantis`, l. 935 ; `bornes_assiette_en_euros`, l. 985),
  que l'inventaire donnait déjà au moteur, et `ClassesCotisation.revenu_retenu`
  (l. 1469) : 16 à 20 fonctions.
- `donnees/macro.py` : la validation des trimestres et les repères du droit
  (`revenu_avpf`, l. 521 ; `seuil_d_un_trimestre`, l. 749 ;
  `smic_horaire_de`, l. 737 ; `coefficient_smic`, l. 982) : 8 à 16.
- `config.py` : six des huit méthodes en double de `Parametres`
  (`taux_capitalisation_applique`, l. 1401 ; `sous_regime_taux`, l. 1267)
  ne sont lues que du moteur et des tests. Le type reste ; ces méthodes sont
  des règles.
- `calendrier.py` : hors du moteur, le Python n'en importe que `DateMois`
  (`pont.py:89`, `avantages.py:57`, `facteurs_depense.py:141`),
  `decomposer` et `formater_age` (`scripts/cycle_de_vie.py:83`) et une
  constante ; `trimestres_civils` (l. 156) et `mois_travailles` (l. 138)
  sont au moteur.
- `donnees/chargement.py` : ses règles d'assiette ont leur double dans
  `carriere.js`, non dans `serie.js`, son jumeau — `assiette_minimale`
  (l. 690, `carriere.js:434`), `forfait_micro` (l. 910, `carriere.js:659`),
  `ChomageComplementaires.part_validee` (l. 1162, `carriere.js:337`), dix
  fonctions en tout. La carte, qui apparie des fichiers, ne les voit pas.

**Les paires dont les calculs restent des deux côtés**, parce que le coût
les lit en Python et le site en JavaScript : `donnees/mortalite.py` (la
survie, l'espérance, le raccord de la loi : 26 en double) ;
`donnees/taux.py` (la courbe des taux, `placement`, l. 230) ;
`donnees/patrimoine.py` (`quantile_normal`, l. 80 ; `grille`, l. 132) ;
`donnees/distribution.py` (`part_sous`, l. 225 ; `part_femmes`, l. 259) ;
`donnees/equilibre.py` (les comptes, dont les variantes relèvent de la
question 1) ; le reste de `macro.py` et de `regimes.py`. Ce sont elles qu'il
faut tenir.

**Les paires qui ne portent qu'un chargeur, des accesseurs et des rapports
d'une ligne** : `contexte.py`, `frontiere.py` (dont le JavaScript dit
lui-même ne rien recalculer, `frontiere.js:4`), `donnees/effectifs.py`,
`assiette.py`, `depenses.py`, `vie_en_couple.py`, `caracteristiques.py`,
`tva.py`, `bilan.py`, et `SerieAnnuelle` dans `chargement.py`.

## 2. Ce qui tient chaque paire aujourd'hui

« Tenue » veut dire ici qu'un test échoue si les deux exemplaires
divergent. Trois mécanismes existent ; aucun ne le garantit pour les 24.

- *Le paquet identique à l'octet* tient le chargeur, qui n'a pas de double.
  Il ne dit rien d'un accesseur JavaScript qui lirait le paquet autrement
  que son jumeau Python ne lit le YAML. Et GitHub refait les fichiers
  fabriqués à chaque envoi (`tests.yml`) : un témoin refait suit une
  divergence, il ne l'arrête pas.
- *Les tests de confrontation directe*, six paires sur 24, chacune sur une
  part de ses fonctions :
  `tests/test_cycle_de_vie_portage.py:207`, `contributions_d_une_carriere`
  seule ; `tests/test_cycle_de_vie_portage.py:302`, quatre méthodes annuelles
  des prélèvements historiques, sur une grille ; `tests/test_moteur.py:1365`,
  `en_mois` seule ; `tests/test_donnees.py:2684`, `_calibrer` seule, à 1e-9
  et non au bit près ; `tests/test_pont.py:1420`, les valeurs de référence de
  `Parametres` contre `PARAMETRES_DEFAUT`, non ses méthodes ;
  `tests/test_web.py:3627`, une constante de `regimes.py`, lue dans le texte
  du JavaScript par une expression régulière.
- *Le moteur Python lui-même* : `tests/test_pont.py` lui fait refaire au bit
  près les témoins que le portage calcule (`docs/architecture.md`, § 7.1).
  Les deux moteurs lisant chacun ses données, la confrontation éprouve au
  passage `macro`, `mortalite`, `regimes`, `chargement` — d'où les 92 % et
  94 % de `macro` à l'inventaire. C'est le seul accord des paires de données
  qu'un test exige, et il est indirect.

Les 18 autres paires n'ont aucun test qui confronte leurs deux exemplaires.
Pour quatorze, la carte ne relève aucun test qui importe ou charge le
jumeau JavaScript : `frontiere.js`, `tva.js`, `depenses.js`,
`vie-en-couple.js`, `caracteristiques.js`, `versions.js`, `distribution.js`,
`effectifs.js`, `taux.js`, `patrimoine.js`, `indemnite_csg.js`,
`assiette.js`, `equilibre.js`, `primes.js` ; ils ne tournent dans la suite
que par les pages et le simulateur qui les chargent. La
couverture de l'inventaire le disait à sa façon : 6 % de `tva.js`, 19 % de
`patrimoine.js`, 45 % de `distribution.js`.

**Ce que le lot F défait.** Déduit : le retrait du moteur Python ôte le
troisième mécanisme. Après lui, le coût mêle le Python et le portage — sa
population par `DonneesMortalite` sur le YAML, ses carrières par
`mortalite.js` sur le paquet — sans qu'aucun test n'exige que les deux
rendent la même survie. Une retouche d'un seul côté ne rougirait rien.

## 3. Le critère de clôture

Trois critères, par ce qu'un test peut en vérifier et ce qu'ils coûtent.

**« Zéro paire »** : la carte ne compte plus aucune paire. Le test tient en
une ligne. Mais 0006 garde les chargeurs et les accesseurs du coût en
Python : pour vider la carte, il faudrait soit faire passer par le pont
chaque lecture de données du coût, que la note 0006 écarte et dont le coût
en temps a été mesuré sur la surcote (étape 7), soit écrire « sans jumeau »
en tête de chaque fichier JavaScript, comme `agregats.js:3`. Or cette phrase
n'est vérifiée par aucun test : la carte la croit (`scripts/jumeaux.py:115`
et `469`). Le critère serait atteint par déclaration, les doublons restant.

**« Tenues », par paire** (l'inventaire) : la carte dit tenues les 24, et
l'action se clôt quand plus aucune règle du moteur n'a deux exemplaires.
Une à deux sessions. Deux défauts : « règle du moteur » n'y a pas de
définition qu'un test lise — par la liste des 38 fichiers, les 79 à 125
règles logées dans les 24 passent pour tenues ; et « tenue » y serait un
mot, puisque 18 paires n'ont pas de test et que les six autres n'en
confrontent qu'une fonction ou une constante.

**« Aucune fonction en double hors d'une liste déclarée et tenue »** (la
recommandation). Quatre conditions, que `tests/test_jumeaux.py` vérifie
sur le dépôt réel :

1. aucune paire hors de la liste déclarée des paires qui restent ;
2. dans chaque paire déclarée, toute fonction qui porte le même nom des
   deux côtés est dans la liste, avec le fichier Python qui la lit et qui
   n'est ni un test ni un jumeau, et le test qui la confronte ; une
   fonction en double non déclarée rougit ;
3. chaque entrée est vivante : la fonction existe des deux côtés, son
   lecteur l'emploie, son test existe ; une entrée périmée rougit, et la
   liste ne peut que décroître sans qu'on le voie ;
4. un test de confrontation, un seul, paramétré par la liste : pour chaque
   entrée, sur une grille d'arguments déclarée avec elle, le Python sur le
   YAML et le JavaScript sur le paquet rendent la même valeur, au bit près.

L'action se clôt quand ces quatre conditions sont vertes et que la liste ne
porte plus que ce que le propriétaire a voulu garder. Le critère se vérifie
seul, il attrape la règle qu'une session écrirait demain des deux côtés, et
il donne à « tenue » son sens. Il coûte : la lecture des fonctions par la
carte ; la liste, de 166 à 212 entrées si tout ce qui a un lecteur reste ;
les grilles d'arguments ; et le retrait des 79 à 125 fonctions sans lecteur,
dont une part revient au lot F. Trois à quatre sessions au lieu d'une à
deux.

Une variante moins chère — la liste par paire, chacune avec un test nommé —
laisserait `mortalite` tenue par le seul `_calibrer` : elle n'est pas
recommandée.

**Ce que le critère ne voit pas.** Il lit les noms : une fonction renommée
d'un côté lui échappe, comme un doublon entre deux fichiers qui ne sont pas
jumeaux. La mesure 3 en relève dix dans `chargement.py`, qui partent avec le
moteur, et une vingtaine de noms communs entre un fichier Python sans jumeau
et le portage — `cout.py` et `cycle-de-vie.js` (`coefficient_actuel`,
`parts_convenues`), `effet_retour.py` et `droit/completer.js`
(`complement_minimum`), `avantages.py` et `pilote.js` (`age_de_depart`),
`indexation_programme.py` et `revalorisation.js` (`coefficient_stock`),
`depense_nette.py` et `compte.js` (`taux_du_bareme`). Ce sont des noms
communs, non des doublons établis : aucun n'a été relu.

## 4. Ce que cela changerait, sans l'écrire

**`scripts/jumeaux.py`.** Lire les fonctions de chaque jumeau — l'arbre
syntaxique pour le Python, qu'il lit déjà pour les imports ; pour le
JavaScript, une lecture à écrire et à éprouver, l'expression régulière de
cette session n'étant qu'un outil de mesure. Lire la liste déclarée. Dans la
carte, une colonne « en double » par paire, et pour les paires déclarées
« tenue » au lieu de « bloqué », que `_bloque` (l. 1023) tire aujourd'hui de
la seule fermeture des imports. Vérifier ce que dit « sans jumeau » : un
fichier qui le déclare ne partage plus aucun nom de fonction avec son ancien
jumeau. Signaler la paire formée par le nom seul : `regimes.js` ne déclare
pas `donnees/regimes.py` dans son en-tête.

**`docs/architecture.md`.** Le § 7.1 dit ce qu'est une paire qui garde ses
deux jumeaux pendant la migration ; il lui manque ce qu'elle est après : une
fonction tenue, qui la lit en Python, quel test la confronte, et lequel des
deux fait foi — le JavaScript, par la note 0005, si le propriétaire le
confirme pour les données. La ligne « retirer un doublon » de la table « Où
va quoi » (l. 114) renverrait à la liste. Une version de l'architecture à la
clôture, comme le veut la règle.

**Le lot G**, en deux temps :

- *avant le lot F* : la carte lit les fonctions, la liste est déclarée, le
  test de confrontation est écrit, pendant que le moteur Python accorde
  encore les deux côtés et peut servir à trancher un écart. Deux sessions ;
- *après le lot F* : les fonctions sans lecteur partent, les paires réduites
  à leur chargeur se disent « sans jumeau » — `versions`, `indemnite_csg`,
  `primes`, `prelevements_historiques`, `contributions_equilibre`
  vraisemblablement —, l'action se clôt. Une à deux sessions.

**Le lot F** gagne les règles du moteur logées dans les 24, que son énoncé
ne nomme qu'en partie (`PeriodeRegime`, les règles d'assiette de
`chargement.py`) : celles de `prelevements_historiques.py`,
`indemnite_csg.py`, `donnees/primes.py`, `macro.py`, `config.py`,
`calendrier.py`, et `versions.applicable`.

## Ce que le propriétaire tranche

1. Le critère : par fonction, avec une liste déclarée et un test de
   confrontation (recommandé) ; par paire, comme l'inventaire ; ou zéro
   paire.
2. Le moment : la liste et son test avant le lot F (recommandé), ou après.
3. Lequel fait foi pour une fonction tenue des données : le JavaScript,
   comme pour le moteur (note 0005), ou le Python, qui lit la source.
4. Si les calculs qui restent des deux côtés — la mortalité, la courbe des
   taux, le patrimoine, la distribution — doivent le rester, tenus, ou n'être
   faits qu'une fois et portés au paquet, comme la frontière. La clôture
   n'en dépend pas ; la taille de la liste, si.

## Ce qui est vérifié, ce qui est déduit

*Vérifié en lisant le code* : les fonctions de chaque côté et leurs lignes ;
les importeurs de chaque jumeau, par la carte ; les lecteurs hors du moteur
de `prelevements_historiques`, `indemnite_csg`, `primes`, `versions`,
`contributions_equilibre` et `calendrier` ; les six tests de confrontation,
relus à leur ligne ; les quatorze jumeaux JavaScript qu'aucun test ne
charge, par la carte ;
le sens de « sans jumeau » dans la carte.

*Déduit* : le partage de chaque fonction entre « lue » et « sans lecteur »,
tiré des noms et non de l'exécution — d'où la fourchette de 79 à 125 ; un
nom commun (`taux`, `part`, `annee`) compte à tort un lecteur. L'effet du
lot F sur l'accord des données. Les nombres de sessions.

*Non vérifié* : qu'un test rougit réellement quand on fausse une fonction
d'un seul côté — aucune mutation n'a été essayée, et les tests lancés par
node n'ont pas été rejoués ; les dix-huit paires « sans confrontation »
reposent sur le relevé de l'éclaireur, recoupé pour quatorze par la carte ; les confrontations indirectes par les carrières
(`tests/js/comparer*.mjs`) n'ont pas été relues assertion par assertion ; la
lecture du JavaScript par expression régulière peut manquer une fonction
fléchée ou un accesseur ; les doublons hors des paires ne sont que des noms.

**Ce qui ne change pas.** Aucun code, aucune donnée, aucun test, aucun
script, aucune garde, aucune règle du scénario 1, aucun chiffre publié. Le
bloc « Reprise » de l'action n'est pas récrit : la session d'orchestration
le tient.

**Tests.** `python -m pytest -m rapide` et les tests de la prose
(`tests/test_prose.py`) ; la prose vérifiée.
