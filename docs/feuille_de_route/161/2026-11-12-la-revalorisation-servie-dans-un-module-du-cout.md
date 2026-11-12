# Action 161 : la revalorisation servie du coût, dans un module à elle

Le 12 novembre 2026. Suite de `2026-11-12-l-histoire-du-droit-par-le-pont.md`,
points 1 et 2 de « Ce qui reste ». Le point 1 est fait : c'est un
remaniement, sans test neuf. Le point 2 est instruit, et rien n'en est mis en
œuvre : une de ses quatre questions attend le propriétaire.

## Ce qui est fait

La classe `RevalorisationServie` quitte `src/retraite_notionnelle/revalorisation.py`
pour `src/retraite_notionnelle/revalorisation_servie.py`, un module que le
coût seul lit. Elle y emporte :

- ses deux lectures de tables, `_derniere_valeur_publiee` et
  `_derniere_annee` ;
- les sept constantes qu'elle partage avec le moteur Python :
  `REGLE_GENERALE`, `REGLE_FONCTION_PUBLIQUE`, `REGLE_POINT`,
  `REGIMES_FONCTION_PUBLIQUE`, `FIN_PEREQUATION`,
  `DEBUT_REGLE_GENERALE_PUBLIC`, `DERNIERE_ANNEE_PEREQUATION`.

`revalorisation.py` reprend d'elle ces neuf noms, par un import. Les deux
fonctions, la pension servie du moteur Python (`PensionServie`) les lit
encore : elles suivent la classe pour la même raison que les constantes.
`droit/liquider.py` et `scenarios/actuel.py`, qui lisent deux de ces
constantes par `revalorisation.py`, ne sont pas touchés.

Le module neuf n'importe aucune règle du moteur Python : le calendrier, les
réglages, la somme ordonnée, et le pont à la demande. `revalorisation.py`
peut donc partir sans le casser, à ceci près qu'il faudra reprendre ailleurs
ce que la classe lit encore par le simulateur Python (voir « Les quatre
tables »).

## Ce qui a suivi le déplacement

**Les importeurs.** Neuf fichiers importent la classe du module neuf :
`simulateur.py`, `cout.py`, `facteurs_depense.py`, `bilan_compte.py`,
`scripts/grille_large.py`, `scripts/indexation_scenario_6.py`,
`tests/test_pont.py`, `tests/test_cout.py`,
`tests/test_indexation_programme.py`. La note d'avant en annonçait neuf, mais
pas les mêmes : les deux contrôles (`controle_ancetre.py`,
`controle_eacr.py`) atteignent la classe par `cout`, et n'avaient rien à
changer ; deux fichiers de tests l'importaient, que la note ne nommait pas.
Dans les tests, seule la ligne d'import change.

**Quatre fiches**, dont un test tient le code au dépôt
(`tests/test_carte.py`, `tests/test_univers.py`) : seul le nom du module y
change.

- `proposition/indexation_du_compte.yaml` : `RevalorisationServie`.
- `agirc_arrco_valeur_achat.yaml` : `RevalorisationServie.coefficient_points`.
- `pension_differee_fonction_publique.yaml` : `FIN_PEREQUATION`.
- `revalorisation_des_pensions.yaml` : `REGIMES_FONCTION_PUBLIQUE`.

Les deux dernières sont des fiches du droit, et nomment désormais un module
du coût pour une constante du moteur. C'est l'effet du choix de la note
d'avant, que les constantes suivent la classe. La ligne Python de ces fiches
part de toute façon avec le jumeau.

**Un commentaire du portage**, dans `moteur/js/revalorisation.js`, nommait le
fichier Python de la classe : il nomme le module neuf. Aucun code JavaScript
ne change, ni `pont.py`, ni `pont.mjs`.

## Les quatre tables : ce que je retiens

La classe lit encore quatre choses par le simulateur Python. Trois sont
réglées par la note de décision 0006, sans rien à faire maintenant. La
quatrième ne l'est pas.

**Le régime de tête et la période d'un régime** (`regime_de_tete`,
`_regle_historique`). Ils lisent le catalogue des régimes, `CatalogueRegimes`,
dont le chargeur est déjà sous `donnees/regimes.py`. Vérifié : le catalogue
du simulateur et celui de son scénario 1 sont le même objet. La note 0006 les
laisse en Python. Rien à déplacer.

**La dernière année du barème général**
(`simulateur.revalorisations.generales`). C'est une lecture du chargeur
`RevalorisationsPensions`, que la note 0006 nomme parmi les chargeurs du
paquet. Il passe sous `donnees/` dans le commit qui retire les règles de
`revalorisation.py`, comme elle le veut. La classe le lira là. Le déplacer
avant irait contre la note, qui écarte un fichier du moteur amputé.

**La dernière année publiée d'un point, au bout de ses fusions**
(`_derniere_valeur_publiee`). Deux parts.

- Ses deux lectures, `ValeursPoint.derniere_annee_servie` et
  `ConversionsPoints.fusion`, sont des lectures de chargeurs du paquet, dans
  `scenarios/actuel.py`. La note 0006 les règle comme le barème général :
  sous `donnees/`, au retrait de leur jumeau.
- La remontée elle-même, douze lignes, existe des deux côtés : ici, et dans
  `moteur/js/revalorisation.js` (`derniereValeurPubliee`, non exportée),
  outre la même chaîne dans `valeurDuPoint`. La note 0006 ne la règle pas :
  ce n'est ni un chargeur ni un calcul agrégé. La clôture de la note 0007
  compte les fonctions de même nom des deux côtés d'une paire ; or la
  remontée Python est maintenant dans un module sans jumeau, et échapperait
  à ce compte en restant un doublon.

Deux voies pour cette remontée, **à trancher par le propriétaire** :

1. *Au pont.* Le portage exporte sa fonction, le pont la sert parmi les
   lectures du droit, et la classe la demande d'un seul lot pour tous les
   barèmes du catalogue, à sa première lecture de l'histoire : une demande de
   plus par coût. La classe ne lit alors plus ni `ValeursPoint` ni
   `ConversionsPoints`. C'est un changement de comportement du pont : son
   test d'abord, une étape à elle.
2. *En Python, déclarée.* Elle reste, et entre dans la liste de la clôture
   avec le test qui la confronte au portage. Ce test demande lui aussi que
   le pont serve la fonction du portage.

Je recommande la première : la seconde paie la même entrée au pont et garde
deux exemplaires.

**Ce que ces quatre lectures ont en commun.** La classe reçoit un
`Simulateur` Python, et y prend ses séries macroéconomiques, ses paramètres,
son scénario 1 et ses revalorisations. Quand ce simulateur partira, elle
devra recevoir autre chose : les paramètres, les séries, le catalogue et les
chargeurs. Cela tient au coût entier, qui reçoit le même simulateur, et
relève de l'étape du retrait.

## Mesures

Un essai jetable, hors du dépôt, avant et après, sans mémoire des calculs.

| | avant | après |
|---|---:|---:|
| le coût de référence, deux mesures | 24,7 et 22,0 s | 25,3 et 21,8 s |
| l'histoire entière, 80 régimes de 1940 à 2070 | 3,9 s | 3,6 s |

## Ce qui est vérifié

*En faisant tourner le code.*
- Le coût de référence, comptes compris : la même empreinte avant et après.
- L'histoire de chaque régime du catalogue, pour chaque année de liquidation
  et chaque année de 1940 à 2070, sous les réglages de référence, avec la
  règle retenue, le régime de tête, le régime convenu, la valeur de service
  convenue et les trois coefficients des systèmes notionnels : 2 814 404
  coefficients, la même empreinte avant et après.
- `python scripts/regenerer.py --verifier` : tout est à jour. Le paquet, les
  mesures de l'accueil, les témoins, le chiffrage, les tableaux, les pages,
  le tableau de bord, la prose et la conservation ne bougent pas. Zéro
  témoin déplacé, zéro chiffre de la prose.

*Non mesuré.* Les deux autres jeux de réglages que la note d'avant passait à
l'histoire (ceux de la page Coût, une série courte). Les six autres coûts
que la fabrique fige ne sont vérifiés que par le paquet identique.

## Tests

Aucun test neuf, aucun test retouché hors de sa ligne d'import. Le commit du
déplacement le déclare par `Sans-test`.

La suite rapide : 4 898 passés, 64 sautés. Les fichiers du coût et de la
zone : 1 815 passés, 6 sautés, en 12 minutes 24 — ceux de la note d'avant,
et `test_univers.py`. Un rouge en chemin, réparé avant le commit :
`test_le_code_de_chaque_fiche_tient`, par les deux fiches du droit
ci-dessus.

`tests/test_facade_jumeau.py` n'a pas été lancé : il ne lit pas la classe.

## Ce qui reste

1. **La remontée des fusions**, une fois tranchée : au pont, ou déclarée.
2. **Quatre lectures restent des deux côtés**, à déclarer à la clôture :
   `coefficient`, `coefficient_stock`, `coefficient_points`,
   `regime_convenu`.
3. **La suite de l'action** : les règles de `droit/` à la façade des tests,
   les études, le retrait.

## Vu sans le traiter

- **Trois renvois de la classe au jumeau** : ses commentaires citent
  `PensionServie`, `PensionServie.coefficient` et
  `PensionServie._fonction_publique`, qui partiront avec `revalorisation.py`.
- **`Simulateur`**, dans la signature du constructeur de la classe, n'est
  importé nulle part : l'annotation n'est jamais évaluée. C'était déjà le
  cas dans `revalorisation.py`.
- **`REGLE_REGIME_SPECIAL`, `REGLE_PAR_DEFAUT` et `REGIMES_REGLE_GENERALE`**
  restent dans le jumeau : la classe ne les lit pas.

**Ce qui ne change pas.** Aucune règle, aucune donnée, aucun témoin, aucun
agrégat, aucun chiffre du site ni de la prose ; aucune règle du scénario 1 ;
aucune garde.
