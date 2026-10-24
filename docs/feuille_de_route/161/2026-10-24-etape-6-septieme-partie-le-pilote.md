# Étape 6, septième partie : le pilote, les départs de l'estimation relus contre leur portage, leur moitié Python retirée

**La demande.** La sixième vague du 24 octobre 2026 : sept sessions en
parallèle, une tâche chacune, que le propriétaire ne suit pas pas à pas.
Celle-ci tient la paire suivante du bloc : celle du pilote, avec les départs
de l'estimation (`ages_de_l_estimation`, `depart_estime`), que le pilote ne
gardait plus que pour confronter les deux moteurs.

**La relecture.** Fonction par fonction, chaque différence éprouvée :
- `point_fixe` et `pointFixe` sont la même boucle, ligne pour ligne. Rejoués
  sur huit règles synthétiques — une montée, une descente confirmée, une
  descente refusée, l'âge intermédiaire de la suspension de 2026, aucune
  réponse, aucune fin, un va-et-vient, NaN — depuis huit âges, ils rendent les
  mêmes âges. Seul `undefined`, que le Python ne connaît pas, les ferait
  diverger : les trois règles du portage rendent un nombre ou `null`.
- `ages_de_l_estimation` et `agesDeLEstimation` : les mêmes trois points
  fixes, `max` et `Math.max` ne différant que pour NaN.
- `depart_estime` et `departEstime` : le même chiffrage ; le Python lisait les
  régimes de la cotisation maladie et du régime général dans les données
  (`charger_prelevements`), le portage dans le paquet, qui les en tire.
- Autour, la seule différence déjà relevée à la première partie :
  `departsDeLEstimation` tait toute erreur qui n'est pas une faute de
  programme, le Python un refus seulement.

Rien n'a été corrigé : ce retrait ne change aucun comportement.

**Les tests** (8eb8b0f). `test_estimation_du_site.py` ne lit plus le pilote
Python. Chaque âge du portage est le point fixe de sa règle : l'âge que
l'étape « ouvrir le droit » du Python oppose à la carrière que le portage
bâtit à cet âge est celui du départ, et ceux qu'il réunit y sont atteints.
Chaque départ est ce que le Python simule de cette carrière : le mois, les
trimestres, ceux que le droit requiert, ce qui l'ouvre, et la pension étage
par étage, posée à la main sur la liquidation de son échéancier, avec les deux
assiettes (`assiette_maladie`), à un milliardième près. Les deux tiennent sous
les trois états du droit, sur les dix-sept requêtes ; les autres tests lisent
les départs du portage, et le dépliant des âges confronte ses deux bouts au
droit du Python. Des sept mutations passagères du portage, six rougissent :
la majoration pour enfants hors des étages, ou portée à la base, que seule la
comparaison étage par étage voit ; l'assiette maladie en euros courants ; un
point fixe qui ne descend jamais ; deux âges confondus en deux départs ; le
taux plein automatique daté par la règle du taux plein. La septième ôte le
maximum avec l'âge précédent : aucune carrière ne l'exerce, le taux plein ne
précédant jamais l'ouverture, ni ne l'exerçait la confrontation des jumeaux,
qui le portaient tous deux. 20 tests, contre 17, en 15 s.

**Le retrait** (80f4dc2). `pilote.py` passe de 271 lignes à 148 :
`DEPARTS_DE_L_ESTIMATION`, `ages_de_l_estimation`, `DepartEstime` et
`depart_estime` partent. Il garde le départ des cas types (`age_de_depart`,
`point_fixe`, `age_propose`), que seul le coût demande, à la fabrique. La paire
reste partielle : `pointFixe` est le jumeau de `point_fixe`. En Python,
`age_annulation_droit` n'est plus lu que par la confrontation des départs.

**Ce que le Python expliquait.** `pilote.js` et `contexte.js` y renvoyaient
trois fois ; chaque renvoi porte ce qu'il désignait : les règles des trois
âges, le point fixe « comme le départ d'un cas type », l'âge demandé d'où part
le premier, les âges confondus que la page réunit ; les montants bruts que la
page divise par douze, le minimum vieillesse que l'estimation ignore, le
`quoi` et la `date` ; les deux assiettes, avec leurs textes (L. 131-9 ;
D. 242-8). Les en-têtes disent l'histoire. `ouvrir.py`, dans son en-tête et
sous `age_annulation_droit`, nomme le pilote du portage ;
`comparer-estimation.mjs` dit ce que le test en fait. Le diff du portage ne
touche que des commentaires.

**Tests.** Le fichier, 20 ; la zone — `test_liquidation.py`,
`test_jumeaux.py`, `test_droits_contrefactuels.py` —, 86 en tout ; la suite
rapide, 3 103 ; les 107 essais de node ; les confrontations légères ;
`construire_temoins.py --verifier`, à jour ; la conservation, rien de perdu.
Les commentaires du portage montent de 2 Ko le poids du site que le README
cite, refait par `verifier_prose.py --corriger`.

**Ce qui reste.**
1. `pages.js`, ligne 7, pour une session du site (sixième partie).
2. Les trois défauts du portage, chacun par son test, l'arrondi du calendrier
   et la lecture des dates de la chronologie, à la relecture de leurs paires
   (sixième partie).
3. `point_fixe` et `pointFixe`, la seule paire du pilote : elle tombe quand le
   coût datera ses cas types par le portage ; `age_annulation_droit`, avec la
   paire de l'ouverture du droit.
4. Le centre du coût, sous le nom de `contexte.py` (cinquième partie).
5. Les paires suivantes de la carte attendent que le coût passe le pont ; deux
   paires de données, au propriétaire.
