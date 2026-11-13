# Les règles du droit à la façade : vingt règles de `liquider` et d'`ouvrir` servies par le portage, 55 tests de plus l'éprouvent

`tests/test_simulateur.py` importe `liquider` et `ouvrir` de la façade. Les
règles que ses tests y appellent — `ouvrir.duree_requise(moteur, periode,
carriere)` — sont calculées par le moteur JavaScript. 55 fonctions de test
quittent la marque `sur_le_moteur_python` : il en reste 66 dans ce fichier,
contre 121. Aucune règle, aucune donnée, aucun témoin n'a bougé.

**La consigne.** « Ce qui reste », 1, de
`2026-11-12-les-tables-et-deux-fichiers-a-la-facade.md` : les règles de
`droit/` par la façade, `liquider` et `ouvrir` en tête, sans supprimer ni
affaiblir un test.

## Ce qui est fait

**L'entrée des règles.** `pont.regle_du_droit` et, dans `pont.mjs`, l'entrée
`droit.regle` de la façade : le portage appelle la règle de son module, sous
les paramètres du simulateur. Vingt règles sont déclarées
(`pont.REGLES_DE_LA_FACADE`) : quatorze de `liquider`, six d'`ouvrir`, celles
que les tests du fichier appellent et dont les arguments passent. Ce qu'une
règle rend revient sous le type que la règle du jumeau annonce, lu
strictement, comme une méthode de table.

**Le client.** `facade.liquider` et `facade.ouvrir` (`Regles`) se tiennent à
la place des deux modules. Les arguments se lient par la signature du
jumeau, ses valeurs par défaut comprises, et passent par leur rang. Passent :
le moteur d'un simulateur de la façade ; une période de son catalogue, par
son rang, comme pour les tables ; une carrière ; une date au mois, dont le
portage refait une `DateMois` ; une valeur simple ou une suite de valeurs
simples. Sont refusés (`NonTransmissible`) : une règle non déclarée, une
règle privée, une classe du module ; le moteur Python ; une période que le
test a retouchée ; tout autre objet, dont les durées d'un relevé ; tout appel
sous un modèle modifié. Un nom que le jumeau ne porte pas manque, comme à un
module (`AttributeError`) : pytest sonde ainsi ce qu'un fichier importe.

**La marque.** Sous `sur_le_moteur_python`, `liquider` et `ouvrir` d'un
fichier basculé redeviennent les modules Python (`facade.JUMEAUX`).

**Un test retouché.** `test_la_crpcen_liquide_les_dix_meilleures_annees_ecretees`
bâtissait sa carrière par `Carriere.depuis_releve` du moteur Python ; il la
bâtit par `simulateur.carriere_releve`, que la façade sert. Ce qu'il attend
est inchangé.

## Ce qui est mesuré

| `test_simulateur.py` | avant | après |
|---|---:|---:|
| fonctions de test marquées | 121 | 66 |
| tests marqués | 129 | 74 |
| tests par la façade | 208 | 263 |

Les huit tests marqués `liquider` ou `ouvrir` qui gardent une marque, chacun
sous sa raison : `liquider.repartir_les_annees` (2),
`liquider.majorer_les_points_de_1952_a_1972`,
`liquider.majoration_des_points_de_1952_a_1972_d_avant_2026` et
`liquider.duree_majoree_apres_taux_plein`, dont un argument est un
dictionnaire ou un objet du moteur ; `Simulateur.pour_la_projection`,
`minimum_garanti.ratio_point_indice` et `carriere_longue._portes`, que le
test lit à côté de la règle.

**Pourquoi 66 fonctions restent**, d'après la raison de leur marque :

| raison | fonctions |
|---|---:|
| une règle de `droit/` hors des vingt (`releve` 9, `completer` 4, `repartir_les_annees` 2, `coordonner` 2, les points de chef 2, `liquidation`, `acquerir`, `commun`, `_coefficient_anticipation`, `duree_majoree_apres_taux_plein`) | 24 |
| une règle du simulateur (`constructeur_employeur` 9, `indexation` 3, `niveau_pour_pension` 2, huit autres) | 22 |
| une table que le test bâtit lui-même, ou une méthode de table non servie (`ValeursPoint` 5, `_en_vigueur` 4, sept autres) | 16 |
| une règle de `carriere.py` (`salaire_moyen_annuel` 3, `Carriere.prolongee`) | 4 |

**Contre le jumeau.** 47 appels, deux au moins par règle déclarée, sous les
réglages de référence et sous les conventions du COR : la même valeur au bit
près (`tests/test_facade_jumeau.py`). Le jumeau rend parfois un entier là où
il annonce un flottant (`trimestres_de_decote`, 18) ; la confrontation le
relit sous le type annoncé.

**Les signatures.** Pour chacune des vingt règles, un test lit la signature
du portage dans `moteur/js/droit/` : autant d'arguments que le jumeau, dans
le même ordre, sous les mêmes valeurs par défaut. Trois noms diffèrent d'un
côté à l'autre (`annees` et `anneesRetenues`, `carriere` et
`carriereSaisie`, `periode` et `periodeLiquidation`).

## Ce qui reste

1. **Les autres règles de `droit/`** que les deux fichiers appellent :
   `releve.construire` (9 fonctions), `completer` (4), puis celles dont un
   argument est un dictionnaire (`repartir_les_annees`, les points de chef) :
   le portage les lit en `Map`, la façade ne les transmet pas encore.
   `liquider.maximum_des_pensions` et `reversion.mois_de_mariage`, que
   `test_reversion.py` importe par leur nom.
2. **Les autres fichiers de tests**, un à un, comme la note d'avant le dit.
3. **Les règles du simulateur** (`constructeur_employeur`, `indexation`,
   `proposition`…).

## Ce qui attend le propriétaire

Posé au propriétaire le 13 novembre, dans la session. Trois questions, avec
ce que la session recommande :

1. *Le § 3 du README sans simulateur Python*
   (`2026-11-12-lot-a-les-sondes-par-le-pont.md`, lignes 69 à 84). Recommandé :
   garder le tableau à l'octet, refait de ce que le pont rend, et remplacer
   l'appel Python par l'adresse du simulateur du site.
2. *La dernière année publiée d'un point*
   (`2026-11-12-la-revalorisation-servie-dans-un-module-du-cout.md`, « Les
   quatre tables »). Recommandé : au pont.
3. *Le défaut du relevé* (`2026-11-12-les-lignes-du-portage-sans-test.md`,
   « Le défaut »). Recommandé : donner aux périodes assimilées leurs lignes,
   après le retrait du moteur Python, pour ne l'écrire qu'une fois.

Six autres, plus petites, relevées dans les notes du 12 novembre et qu'aucune
note ne dit tranchées : le retrait du code mort du portage
(`2026-11-12-le-code-mort.md`, « Ce que le propriétaire tranche ») ; le
moment de la liste de la clôture, lequel fait foi pour une fonction tenue des
données, et les calculs qui restent des deux côtés
(`2026-11-12-question-4-la-cloture.md`, points 2 à 4) ; la phrase à afficher
quand l'estimation ne se chiffre pas
(`2026-11-12-le-pilote-les-erreurs-tues.md`) ; la mesure de la carte, les
tests que le pont ne sait pas servir et la moyenne de la fusion
(`2026-11-12-les-lignes-du-portage-sans-test.md`, points 2 à 4) ; l'option
`--cas-types` (`2026-11-12-lot-b-deux-etudes-par-le-pont.md`). Hors de
l'action, de la zone des données : `ccss_regimes.py` et les branches
(`2026-10-15-etape-4-quatrieme-partie-les-defauts-du-lecteur.md`).

Aucune réponse n'était arrivée quand la session a publié son étape.

## Ce qui n'est pas vérifié

- La façade des règles sur d'autres fichiers, et sur d'autres règles que les
  vingt déclarées.
- Les huit tests qui gardent leur marque, un à un : chacun a été vu refusé
  par la façade, sous la raison que sa marque porte ; aucun n'a été porté.
- La suite complète, que GitHub lance.

**Ce qui ne change pas.** Aucune règle, aucune donnée, aucun témoin, aucun
script, aucune garde. Le reste du pont : la lecture des arguments marqués,
écrite pour les tables, sert désormais aux deux entrées.

**Tests.** `tests/test_facade.py`, 82 tests, les neuf nouveaux vus rouges
avant le code ; `tests/test_facade_jumeau.py` ;
`tests/test_fichiers_sur_le_moteur_python.py` ; `test_simulateur.py` et
`test_reversion.py` en entier, aussi sous `PRESOMPTIONS_DECALEES=1` (747
passés et 26 sautés, avec `test_facade.py`) ; la suite rapide, 4 929 passés,
64 sautés ; les confrontations légères, `tests/test_pont.py` et
`tests/test_outillage.py`, 572 passés.
