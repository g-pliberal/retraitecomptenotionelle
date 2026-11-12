# La garantie d'une population par le pont : le coût la demande au moteur JavaScript, et son exemplaire Python part

Le barème de la garantie appliqué à la distribution des pensions n'a plus
qu'un exemplaire, `moteur/js/garantie.js`. Le coût, l'effet retour et
`scripts/garantie_par_sexe.py` le demandent au pont, par lot. Le coût de
référence, les lectures du script et le paquet refait sont identiques à
l'octet. `garantie.py` n'est pas supprimé : il garde le barème d'une
personne, quinze lignes, que le moteur Python d'une carrière lit encore.
Rien n'est gardé en correctif, et rien n'attend une décision du
propriétaire.

**La demande.** L'étape « la garantie » de la table des décisions du 12
novembre (`2026-11-12-les-decisions-du-proprietaire.md`), la session C1 de
la note de la question 1 : la confrontation, la demande au pont,
`GarantieDistribution` et `_garantie_distribution` branchés,
`garantie_par_sexe.py` suivi, `garantie.py` retiré. La relecture de la paire
était faite (`2026-11-12-relecture-la-garantie-et-l-impot.md`), et sa
confrontation directe écrite (`tests/test_relecture_zone_grise.py`).

## Ce qui change

- **Le pont** (`pont.py`, `garantie` ; `pont.mjs`, `garantieDePopulation`) :
  une demande de plus, `garantie`. Elle porte une liste d'appels,
  `(fonction, *arguments)`, parmi cinq fonctions du portage —
  `cout_garantie`, `cout_garantie_par_sexe`, `manque_moyen`,
  `facteurs_par_sexe`, `pension_moyenne` —, leurs arguments dans l'ordre du
  portage. Une distribution, tout ce qui porte des `tranches`, passe une
  fois, en données, et un argument la désigne par son rang : celles que
  l'effet retour déforme passent comme celles de l'enquête. Ce que chaque
  fonction rend revient dans l'ordre, sous le type du Python
  (`LECTURES_DE_LA_GARANTIE`). Un appel que le barème refuse arrête le lot
  et lève `ValueError`, du message du portage. Le barème ne lit que ses
  arguments : la demande se passe du paquet et va toujours au pont gardé
  ouvert, sur les données du dépôt comme sur des données d'ailleurs.
- **Le coût** (`cout.py`) : `GarantieDistribution.chiffrer_distribution`
  demande son barème au pont ; `appel_du_bareme`, une méthode de plus, rend
  l'appel sans le faire, pour qui en chiffre plusieurs d'un lot ;
  `facteurs_des_sexes` demande les deux pensions moyennes, puis les deux
  facteurs. `_garantie_distribution` et `_reprises_successions`, qui
  appelaient `_manque_moyen` tranche par tranche, demandent toutes leurs
  tranches d'un lot chacun, et la seconde ses quatre coûts d'un autre.
  `CoutGarantie`, le type de ce que le barème rend, vit désormais dans
  `cout.py`.
- **L'effet retour** (`effet_retour.py`) : `_aspas` chiffre d'un seul lot
  l'ASPA d'une année, le système actuel puis chaque scénario, sa
  distribution déplacée telle quelle et déformée, neuf appels ; `chiffrer`
  les lit ; `_aspa`, que les tests appellent, en est le cas d'un seul.
- **Le script** (`scripts/garantie_par_sexe.py`) : la pension moyenne de
  chaque sexe, les deux facteurs de chaque rapport et le coût de chaque
  plancher passent par le pont, d'un lot chacun. Il recopiait la pension
  moyenne et la contrainte de masse : ces deux copies sont parties.
- **`garantie.py`**, de 319 à 40 lignes : `_manque_moyen`, `cout_garantie`,
  `cout_garantie_par_sexe`, `facteurs_par_sexe`, `pension_moyenne`,
  `_verifier_forme` et `CoutGarantie` en sortent. Leurs explications sont
  passées dans les commentaires de `garantie.js` : ce que valent les trois
  conventions, ce que le facteur fait et ne fait pas, la contrainte de
  masse comme répartition, les deux planchers d'une population, la même
  forme aux deux. L'en-tête de `garantie.js` déclare ce qui lui reste de
  jumeau, et la carte (`python scripts/jumeaux.py garantie`) le lit.
- **La fiche** `garantie_vieillesse.yaml` ne nomme plus `cout_garantie`
  côté Python.

## Un comportement change

`GarantieDistribution` ne refuse plus à sa construction une forme qui n'est
pas un barème dégressif : c'est le barème qui la refuse, au premier
chiffrage, du même message. La garde vivait dans `_verifier_forme`, qui
n'aurait plus été qu'une seconde copie de celle de `coutGarantie`.
`tests/test_garantie_degressive.py` le dit
(`test_la_garantie_projetee_applique_la_forme_qu_on_lui_donne`).

## Les lots, mesurés

Un coût de référence, sans mémoire, 28 secondes : 233 demandes au pont,
1 113 appels du barème, 0,43 seconde dans le pont. Soit 876 coûts par sexe
— les 147 chiffrages de la garantie, un par demande, et les 729 de l'ASPA,
en 81 lots de neuf —, 230 manques moyens en deux lots, quatre coûts d'un
lot, deux pensions moyennes d'un lot et une paire de facteurs. Le chiffrage
annuel de la garantie reste une demande par année : la boucle de
`cout._avenir` n'est pas refaite en deux passes, comme la note de la
question 1 le prévoyait. Les 876 coûts par sexe sont ceux qu'elle comptait.

## Ce qui est vérifié

*En faisant tourner le code.*
- Avant tout branchement, ce que le pont relit confronté au jumeau Python,
  au bit et sous le même type : 375 demandes, les trois colonnes de
  l'enquête sous quatre formes, cinq facteurs et quatre planchers, d'un sexe
  ou de deux. Un ulp déplacé dans le jumeau la rougissait. Cette
  confrontation, commitée avec la demande au pont, est partie avec le
  jumeau.
- Le coût de référence, comptes compris, écrit nombre par nombre par un
  essai jetable hors du dépôt : 19 227 nombres, la même empreinte avant le
  branchement, après lui et après la coupe.
- Les lectures de `garantie_par_sexe.py`, dix-huit lignes et ses minima :
  identiques au bit, avant et après.
- Le paquet refait par `python scripts/construire_donnees.py`, en 2 minutes
  51 : `data/derive/agregats.json`, `moteur/donnees.json`,
  `data/derive/equilibre.json` et les calibrations, identiques à l'octet.
  Aucun témoin déplacé, aucun fichier fabriqué modifié.

*En lisant le code.* Les neuf messages de refus, relevés dans `garantie.py`
avant sa coupe, que la confrontation de la relecture tenait égaux à ceux du
portage.

*Non mesuré.* Les six autres coûts que la fabrique fige ne sont vérifiés que
par le paquet identique, non nombre par nombre. JSON n'écrit pas le zéro
négatif : le barème n'en rend aucun sur les demandes confrontées, et la
confrontation comparait les écritures, non les égalités.

## Tests

- `tests/test_pont.py` : le pont chiffre la garantie d'une population,
  valeurs posées à la main (9 000 M€, 12 000 M€, 750 €, 0,6 et 1,2) et types
  relus ; la demande se passe du paquet ; les neuf refus et leur message ;
  le coût chiffre sa garantie par le portage, et s'arrête sans node.
- `tests/test_effet_retour.py` : l'ASPA d'une année se demande d'un seul
  lot de neuf appels, et rend les mêmes taux que chiffrage par chiffrage.
- `tests/test_garantie_par_sexe.py` : le script demande le barème au
  portage, et s'arrête sans node.
- `tests/test_garantie_degressive.py` : la garantie d'une population ne
  s'écrit qu'en JavaScript — `garantie.py` ne définit plus que
  `complement_garantie`.
- `tests/outils_garantie.py`, un module d'aide : le barème sous les
  signatures que le Python lui donnait, servi par le pont. Les tests tirés
  des sources ou posés à la main (`test_garantie_degressive.py`,
  `test_cout.py`, `test_affirmations.py`, `test_controle_drees_panorama.py`,
  `test_effet_retour.py`) y passent sans que leurs valeurs changent ; le
  test du manque moyen « au bit près d'avant », 5 520 appels, les demande en
  deux lots.
- `tests/test_relecture_zone_grise.py` ne confronte plus de la garantie que
  le barème d'une personne, 648 demandes, et garde le cas de la tranche sans
  borne.

Chaque test neuf a été vu rouge pour la raison attendue. La suite rapide,
4 798 passés ; les fichiers du coût et de la zone (`test_cout.py`,
`test_facteurs_depense.py`, `test_affirmations.py`,
`test_controle_drees_panorama.py`, `test_agregats.py`, `test_pont.py`, la
carte), verts.

## Ce qui reste

1. **`garantie.py` part avec le moteur Python.** `complement_garantie` y
   reste, avec son jumeau `complementGarantie`, tant que
   `scenarios/notionnel.py` et `revalorisation.py` l'appellent : le lot F.
   La lettre de l'étape disait « `garantie.py` retiré » ; il est réduit.
2. **`garantie_par_sexe.py` refait encore à la main le mélange des sexes et
   des planchers**, en additionnant les coûts, quand `coutGarantieParSexe`
   additionne les manques : le remplacer par un seul appel déplacerait ses
   chiffres au dernier bit. Laissé tel quel.
3. **La convention du milieu de tranche reste écrite en Python là où le
   coût s'en sert pour autre chose que le barème** : la pension moyenne des
   bénéficiaires (`_garantie_distribution`, `_reprises_successions`) et la
   déformation de l'effet retour (`_deformer`). Trois lignes chacune, qui ne
   sont pas des fonctions de la garantie.
4. **Action 167, point 10.** La phrase de l'en-tête de `garantie.py` qu'elle
   relève (« cinq pour les générations récentes, aucun pour celles d'avant
   1955 », d'avant l'âge légal) est partie avec l'en-tête et n'a pas été
   reportée dans `garantie.js` : l'action peut la rayer.
5. **La suite de l'action** : la façade des tests, puis l'impôt de l'effet
   retour, qui trouvera dans `pont.garantie` le modèle d'une demande par lot
   sans paquet.

**Un chiffre de la prose bouge.** Le poids du moteur que le README annonce
au lecteur passe de 933 à 934 Ko compressés : ce sont les explications de
`garantie.py` reportées dans les commentaires de `garantie.js`, que le
navigateur charge avec le moteur.

**Ce qui ne change pas.** Aucune règle, aucune donnée, aucun témoin, aucun
agrégat, aucun chiffre du site ; aucune règle du scénario 1 ; aucune garde.
