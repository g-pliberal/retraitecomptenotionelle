# Étape 14, au site : la descente vers la carrière longue d'une carrière qui ne valide plus

**Le 25 octobre 2026 : « Mon estimation retraite » dit au plus tôt le départ
d'une carrière qui ne valide plus à l'âge où la carrière longue l'ouvre, non
plus à l'âge légal ; sur `main` (db3aef0). Le point fixe du premier âge fait,
la recherche reprend d'un an plus tôt tant que le départ s'y ouvre, et un âge
que la saisie refuse n'ouvre rien. Aucun témoin ne bouge. En chemin : le
balayage du cycle de vie du militaire des cas types part plus tôt, sans
atteindre l'âge où sa pension s'ouvre ; la recherche peut s'arrêter un mois
après le premier départ ouvert.**

**La demande.** Vingtième vague, le 25 octobre 2026 : une session par tâche,
que le propriétaire ne suit pas pas à pas, celle-ci seule du lot sur les pages
et sur `moteur/js/pilote.js`. Le point « au site » du paragraphe « Ce qui
reste » de la note de l'estimation des carrières inactives
(`2026-10-25-etape-14-estimation-des-carrieres-inactives.md`), que son
paragraphe « Trouvé en chemin : la descente » décrit.

**Ce qui est fait.**

- *Le test* (`tests/test_estimation_du_site.py`,
  `test_une_carriere_qui_ne_valide_plus_part_a_l_age_ou_la_carriere_longue_l_ouvre`,
  au niveau complet du fichier). Né le 15 janvier 1966, entré en janvier 1982,
  à seize ans, et sans activité de 2025 à 2045, un salarié a 43 × 4 = 172
  trimestres cotisés à la fin de 2024, ceux de sa génération. Il en a validé
  cinq avant la fin de l'année de ses dix-huit ans, non de ses seize — 1982
  n'en compte que quatre — : la carrière longue lui ouvre son départ à 60 ans,
  au taux plein (L. 351-1-1 et D. 351-1-1, version du 1er septembre 2023).
  Sous le droit au 31 août 2023, qui ne leur en requiert que 169, les deux
  saisies du test de la session d'avant ont leur durée cotisée à 60 ans, que
  leur début avant vingt ans leur ouvre (rédaction du décret du 2 juillet
  2012). Vu rouge pour cette raison : le portage disait le salarié au plus tôt
  à 63 ans et 3 mois, par l'âge légal, et les deux saisies à 61 ans et 3 mois
  et à 62 ans. La naissance se déclare entière ; sans enfant ni mariage, aucune
  présomption que la garde décale n'y entre.
- *Le trimestre de trop*
  (`test_une_carriere_longue_arretee_avec_un_trimestre_de_trop_y_descend_aussi`).
  Née le 15 janvier 1968, entrée en octobre 1983 et sans activité depuis 2027,
  une salariée a ses 172 trimestres cotisés à la fin de septembre 2026, et la
  carrière longue, par son début avant seize ans, lui ouvre son départ dès lors,
  avant ses 59 ans ; arrêtée avec 173, elle descendait d'un trimestre par passe
  et s'arrêtait à 63 ans. Les âges que la descente traverse s'ouvrent sans se
  confirmer — liquidée à 61 ans, la carrière s'ouvre à 60 ans et 9 mois — : le
  test tient la recherche à ce qu'elle reprenne d'un départ ouvert, non d'un
  âge confirmé. Écrit après le premier envoi, vu rouge sur le pilote d'avant,
  à 63 ans, vert sur celui de `main`.
- *La garde* (`test_un_depart_que_la_saisie_refuse_ne_tait_pas_l_estimation`).
  Chercher un départ plus précoce interroge le droit à des âges que la saisie
  peut refuser : un départ qui précède l'un de ses métiers. La saisie des trois
  âges, salariée cadre à compter de septembre 2031, six mois avant son âge
  légal, garde ses trois départs, aux mêmes âges et avec les mêmes trimestres.
  Verte sur le code d'avant ; rouge sous une première écriture de la
  correction, dont la sonde d'un an plus tôt tombait avant le second métier et
  faisait taire le bloc ; verte enfin.
- *La correction* (`agesDeLEstimation`, `moteur/js/pilote.js`). Le point fixe
  du premier âge fait, la recherche reprend d'un an plus tôt, tant que le
  départ s'y ouvre — le droit lui oppose un âge qui ne le dépasse pas — ;
  partie au-dessous de l'âge où la carrière longue ouvre le départ, elle y
  monte, comme toute autre. Les sondes passent par `sansRefus`, qui répond
  `null` à un départ que la saisie ou le modèle refusent, et laisse remonter
  une faute de programme, comme `departsDeLEstimation`. Les deux autres âges
  partent du premier, comme avant ; `pointFixe` ne change pas, ni son jumeau,
  `point_fixe`.

**Ce que montrent les mesures.** Sous les trois états du droit, les départs
des dix-sept requêtes de `test_estimation_du_site.py`, du même salarié s'il
travaille jusqu'au départ — 60 ans, déjà — et de la saisie passée cadre ne
bougent pas, montants compris. Ne bougent que ceux du test : le salarié passe
de 63 ans et 3 mois à 60 ans sous le droit qui s'applique, de 63 ans et 6 mois
à 60 ans sous la loi de 2023 sans la suspension ; les deux saisies de 1983,
sous le droit au 31 août 2023, de 61 ans et 3 mois et de 62 ans à 60 ans. Ni
les témoins de simulation ni ceux des pages (`construire_temoins.py`), ni aucun
fichier que `regenerer.py --verifier` fabrique, hors deux chiffres ancrés du
README, le poids du site, d'un kilo-octet de plus, que GitHub récrit. Le
balayage du cycle de vie (`agesBalayes`) part du premier âge : il commence à
60 ans pour le salarié ; des 91 cases de la grille des cas types
(`cycle_de_vie.py`, `balayer`, productivité de référence), seules les sept du
militaire bougent (« Trouvé en chemin »). Une saisie dont le premier âge ne
descend pas paie deux interrogations du droit de plus, de 5 à 10
millisecondes mesurées sur les saisies du test, et celle qui descend deux par
année descendue. La suite rapide, le filet du site, les tests JavaScript, ceux
du cycle de vie et de l'estimation passent.

**Trouvé en chemin : le militaire.** Le militaire non officier des cas types,
radié à 48 ans et demi, a sa pension dès quinze ans de services avant juillet
2011, dix-sept depuis 2015 (L. 24, II, du code des pensions civiles et
militaires ; `duree_services_militaires.csv`). Le droit la lui ouvre à 35 ans
et 10 mois, né en 1960, à 37 ans et 10 mois, né en 1990, à quelque âge qu'on
la liquide ensuite ; mais la carrière liquidée à cet âge-là n'a pas encore ses
services, et ne s'ouvre qu'un mois plus tard. Aucun âge ne s'y confirme donc :
l'ancienne descente, qui ne retient l'âge proposé que s'il se confirme, laissait
le balayage de son cycle de vie partir de son âge de radiation ; il part
maintenant de 36 ans et demi, et de 38 ans et demi depuis la génération 1980 :
le dernier âge ouvert de la grille des années que la recherche sonde, plus près
de l'âge où sa pension s'ouvre, sans l'atteindre. Ne retenir qu'un âge que le
droit confirme l'aurait laissé à 48 ans et demi, mais n'aurait plus corrigé la
carrière longue au trimestre de trop (« Ce qui est fait ») ; aucun test tiré de
la source n'en demande davantage. L'estimation du site se tait pour une saisie
militaire, avant comme après.

**Trouvé en chemin : le mois.** Le droit date la durée de trimestre en
trimestre à partir de l'âge qu'on lui soumet, non par trimestres civils, et
la recherche peut s'arrêter un mois après le premier départ ouvert. La
salariée au trimestre de trop a sa durée à la fin de septembre 2026 et part en
octobre, à 58 ans et 8 mois, âge que le droit confirme : l'estimation, qui la
disait à 63 ans, la dit en novembre. Née le 15 mars 1965, entrée en mars 1981
et sans activité depuis 2024, une autre a 171 trimestres cotisés : sa
génération en doit 172 sous la loi de 2023, et 170 aux pensions qui prennent
effet depuis le 1er septembre 2026, après la suspension (loi n° 2025-1403,
article 105). La carrière longue lui ouvre son départ en septembre 2026, à
61 ans et 5 mois ; l'estimation le disait à 62 ans, au bout des passes de la
descente, et le dit en octobre : le droit y propose 61 ans et 3 mois, que la
loi de 2023 ferme, puis 61 ans et 6 mois, et `pointFixe` ne cherche pas le mois
qui les sépare.

**Ce qui ne bouge pas.** Aucune règle du scénario 1 — le pilote dit quand la
saisie part, non ce que le droit lui sert — : pas d'entrée au journal de
veille. Le taux plein de 279a48a, dont le test passe. Le bloc « Reprise » de
l'étape 14, que la session de la population tient.

**Ce qui reste**, une session par point : au modèle, la même descente dans le
départ des cas types, à vérifier (la note de l'estimation des carrières
inactives), et l'âge où s'ouvre la pension du militaire, au mois près, que son
balayage devrait atteindre (« Trouvé en chemin ») ; le mois que la recherche
manque (« Trouvé en chemin »), au site par une sonde au mois dans
`agesDeLEstimation`, qui coûterait des interrogations à chaque saisie, ou au
modèle par la datation de la durée et par `point_fixe` et son jumeau. Au
propriétaire : dire si le balayage du militaire doit partir de son âge de
radiation tant que l'âge où sa pension s'ouvre n'est pas trouvé au mois, et si
l'écart d'un mois vaut ce coût.
