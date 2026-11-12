# L'histoire du droit par le pont : ses règles demandées au moteur JavaScript, par lot

Ce que le droit a servi aux pensions liquidées
(`RevalorisationServie.coefficient_historique`) reste au coût, en Python,
mais n'appelle plus aucune règle du moteur Python. Les cinq règles qu'il
appelait mois par mois, il les demande au moteur JavaScript, par le pont,
d'un seul lot par règle de revalorisation. L'histoire est identique au bit,
le coût de référence aussi, le paquet et les témoins à l'octet.

**L'étape s'arrête à mi-chemin.** La consigne en nommait deux moitiés : les
déclarations au pont avec `_nominal` par lot, puis la sortie de
`revalorisation.py` de la part du coût. Seule la première est faite. La
seconde est une étape entière, et elle pose une question que celle-ci
n'avait pas à trancher : voir « Ce qui reste ». Rien n'est gardé en
correctif, et rien n'attend une décision du propriétaire.

**La demande.** Le point 1 de « Ce qui reste » de
`2026-11-12-la-revalorisation-servie-par-le-pont.md`, la session C4 de la
note de la question 1 (`2026-11-12-question-1-la-zone-grise.md`). La note de
décision 0007 dit que l'histoire du droit reste en Python, au coût, et que
la confrontation écrite à ce passage tient lieu de relecture.

## Ce qui change

- **Le pont** (`pont.py` et `pont.mjs`, un bloc à part des deux côtés, sous
  son titre, « l'histoire du droit ») : quatre fonctions de plus au pont du
  droit (`pont.droit`), sur le moteur du scénario 1.
  `scenario_actuel.revalorisations_pensions.generale` rend le coefficient de
  l'article L. 161-23-1 entre deux dates.
  `scenario_actuel.revalorisations_pensions.retenues.fonction_publique.produit`
  rend le produit des décrets de la fonction publique entre deux dates.
  `scenario_actuel.minimum_garanti.ratio_point_indice` rend ce que devient
  un traitement indiciaire entre deux années.
  `scenario_actuel.conversions_points.echelle` rend le changement d'unité
  des points d'un régime entre deux années. Les dates passent en texte,
  « AAAA-MM-JJ », comme le portage les lit. La cinquième règle,
  `liquider.valeur_du_point`, y était déjà.
- **Leurs jumeaux** (`tests/outils_pont.py`,
  `JUMEAUX_DE_L_HISTOIRE_DU_DROIT`) : la règle Python de chacune, que
  `droit_et_refait` confronte au portage tant qu'elle reste.
- **La classe** (`revalorisation.py`) : `_nominal` relève d'abord les appels
  d'une règle de revalorisation, les demande d'une seule fois (`_lot`), puis
  en fait les moyennes annuelles comme avant. Le régime général : chaque
  mois depuis 1949. La fonction publique : le point d'indice de chaque
  année jusqu'en 2003, les décrets de chaque mois de 2004 à 2008, le
  coefficient général de chaque mois depuis 2009. Un régime en points : la
  valeur de service de chaque mois, et le changement d'unité entre chaque
  couple d'années de son histoire, que `_historique` lit ensuite dans une
  table au lieu de le demander couple par couple.
- **L'en-tête** de `pont.py` et la description de la classe disent qui
  calcule quoi.

## Un choix de la session

**Le changement d'unité se demande pour tous les couples d'années, avec les
valeurs du point.** `_historique` le demandait au fil des lectures, un couple
(liquidation, année) à la fois, et rien ne dit d'avance lesquels le coût
lira. Le lot d'un barème porte donc chaque couple de son histoire : 3 003
de 1949 à 2026, en 0,05 seconde. Deux autres voies ont été écartées.
Demander le facteur de chaque année et les multiplier en Python aurait
récrit la règle ici, et ne tient au bit que tant qu'un régime ne change pas
deux fois d'unité la même année. Une fonction du pont qui rendrait la table
d'un coup serait plus rapide, mais ajouterait au pont une fonction que rien
d'autre ne lit.

## Les lots, mesurés

Un coût de référence, sans mémoire : 355 demandes au pont au lieu de 341,
une par règle de revalorisation que sa grille rencontre.

| | avant | après |
|---|---:|---:|
| le coût de référence, deux mesures | 27,4 et 28,4 s | 27,1 et 26,6 s |
| l'histoire entière de chaque régime, de 1941 à 2070 | 3,5 s | 3,7 s |

Un lot de 936 valeurs du point : 0,03 seconde. Un lot de 3 003 changements
d'unité : 0,05 seconde.

## Ce qui est vérifié

*En faisant tourner le code.*
- L'histoire avant et après, écrite nombre par nombre par un essai jetable,
  hors du dépôt : `coefficient_historique` de chaque régime du catalogue,
  pour chaque année de liquidation et chaque année depuis 1940, et les
  moyennes annuelles de chaque règle. Trois jeux : les réglages de
  référence de 1941 à 2070, ceux de la page Coût de 1960 à 2070, une série
  courte de 1990 à 2010. 1 668 960 coefficients, la même empreinte.
- Le coût de référence, comptes compris, écrit de même : 40 251 valeurs, la
  même empreinte avant et après.
- Chaque appel de chaque lot refait par le jumeau Python, au bit : c'est le
  test de confrontation, qui reste dans la suite. Un dernier chiffre déplacé
  dans le jumeau de chacune des cinq règles le rougit, règle par règle
  (essai jetable).
- Les témoins et le paquet refaits : voir « Tests ».

*Posé à la main, depuis les barèmes.* Les seize valeurs du premier test,
lues dans `revalorisation_pensions.csv`,
`revalorisation_pensions_fonction_publique.csv`,
`point_indice_fonction_publique.csv` et `conversions_points.csv`. Les cinq
coefficients du second : le régime général de 2022 à 2023, la fonction
publique de 2002 à 2003 puis de 2007 à 2008, l'Agirc-Arrco de 2023 à 2024,
l'Arrco de 1998 à 1999, à travers son changement d'unité ; les prix sont
lus à la série du dépôt.

*Non mesuré.* Les six autres coûts que la fabrique fige ne sont vérifiés que
par le paquet identique. Le coût sur des données d'ailleurs lance node à
chaque demande, donc quatorze fois de plus par coût : non chronométré.

## Tests

Dans `tests/test_pont.py`, trois tests neufs, tous de la suite rapide, sous
le titre « l'histoire du droit » :

- `test_le_pont_sert_les_regles_de_l_histoire_du_droit` : les quatre
  fonctions neuves, seize appels aux valeurs posées à la main, un refus, et
  le jumeau qui les refait ;
- `test_l_histoire_du_droit_demande_ses_regles_au_portage_par_lot` : les
  cinq règles du moteur Python remplacées par une erreur, cinq coefficients
  aux valeurs posées à la main, un lot par règle de revalorisation, aucune
  redemande, l'arrêt sans node ;
- `test_les_regles_de_l_histoire_du_droit_sont_celles_du_jumeau_au_bit` :
  la confrontation, sur chaque régime du catalogue.

Les deux premiers ont été vus rouges pour la raison attendue ; le troisième,
une confrontation, a passé d'emblée, puis rougi sous l'essai du dernier
chiffre déplacé. Sous `PRESOMPTIONS_DECALEES=1`, le premier et le troisième
passent ; la suite saute elle-même le second (« le portage lit ses
présomptions dans le paquet »).

La suite rapide, 4 898 passés. Les fichiers du coût et de la zone, 1 798
passés et 6 sautés, en un lancement de 12 minutes 45 : `test_cout.py`,
`test_facteurs_depense.py`, `test_affirmations.py`,
`test_controle_drees_panorama.py`, `test_agregats.py`, `test_pont.py` en
entier, `test_revalorisation.py`, `test_moteur.py`,
`test_indexation_programme.py`, `test_effet_retour.py`,
`test_bilan_compte.py`, les deux contrôles, `test_grille_large.py`,
`test_indexation_scenario_6.py`, les confrontations légères, la carte,
`test_jumeaux.py`, `test_fichiers_sur_le_moteur_python.py`.

Le paquet refait par `python scripts/construire_donnees.py` et les témoins
par `construire_temoins.py` : aucun fichier déplacé, ni
`data/derive/agregats.json`, ni `moteur/donnees.json`, ni
`data/derive/equilibre.json`, ni les calibrations, ni un témoin. Aucun
chiffre de la prose ne bouge.

## Ce qu'un test existant prouve, inchangé

Aucun test existant n'a été retouché. `tests/test_cout.py`
(`test_le_scenario_1_sert_les_revalorisations_de_son_droit`) éprouve
toujours l'histoire sur la grille du coût, qui y passe maintenant par le
pont. `tests/test_facade_jumeau.py` n'a pas été lancé : il ne lit pas
l'histoire du droit.

## Ce qui reste

1. **Sortir de `revalorisation.py` la part du coût.** La classe
   `RevalorisationServie` et ce qu'elle seule lit vont dans un module du
   coût, que neuf fichiers importeront à la place : `simulateur.py`,
   `cout.py`, `facteurs_depense.py`, `bilan_compte.py`, les deux contrôles
   (`controle_ancetre.py`, `controle_eacr.py`), `scripts/grille_large.py`,
   `scripts/indexation_scenario_6.py`, `tests/test_pont.py`. Les constantes
   qu'elle partage avec le moteur (`REGLE_GENERALE`,
   `REGLE_FONCTION_PUBLIQUE`, `REGLE_POINT`, `REGIMES_FONCTION_PUBLIQUE`,
   `FIN_PEREQUATION`, `DEBUT_REGLE_GENERALE_PUBLIC`,
   `DERNIERE_ANNEE_PEREQUATION`) la suivent, et `revalorisation.py` les
   reprend d'elle : le jumeau peut alors partir sans rien casser. C'est un
   remaniement, sous les tests qui sont là.
2. **La question que ce déplacement pose.** Sans règle du moteur, la classe
   lit encore quatre tables sur le moteur Python du simulateur. La dernière
   année dont la valeur d'un point est publiée, au bout de ses fusions
   (`_derniere_valeur_publiee` : `valeurs_point.derniere_annee_servie`,
   `conversions_points.fusion`, `integre_dans` du catalogue). La dernière
   année du barème général (`simulateur.revalorisations.generales`). La
   période d'un régime à une année (`_regle_historique`). Le régime de tête
   (`regime_de_tete`). Ce sont des lectures de données, que la note de
   décision 0006 laisse en Python, sous `donnees/`, au retrait. Mais les
   deux premières remontent une chaîne que `valeur_du_point` remonte aussi :
   la session qui déplace la classe dira si elles se demandent au pont, ou
   si leurs chargeurs passent sous `donnees/` avant le retrait.
3. **Quatre lectures restent des deux côtés**, à déclarer à la clôture
   (`2026-11-12-question-4-la-cloture.md`) : `coefficient`,
   `coefficient_stock`, `coefficient_points` et `regime_convenu`.
4. **La suite de l'action** : les règles de `droit/` à la façade des tests,
   les études, le retrait.

## Vu sans le traiter

- **`tests/test_controle_drees_panorama.py`** (ligne 216) appelle
  `conversions_points.echelle` et `liquider.valeur_du_point` sur le moteur
  Python. Le pont sert maintenant les deux : le passage de ce fichier à la
  façade des tests n'a plus rien à y déclarer.
- **Sur des données d'ailleurs**, le pont lance node à chaque demande, comme
  la note d'avant le dit : cette étape en ajoute une par règle de
  revalorisation.
- **`PensionServie`**, la revalorisation d'une pension dans le moteur Python
  d'une carrière, appelle les mêmes cinq règles, en Python : elle part avec
  le moteur, et n'a pas été touchée.
