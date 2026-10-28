# Étape 14, au modèle : la descente des cas types, et l'ouverture du militaire au mois près

**Le 28 octobre 2026 : le départ des cas types descend comme celui de « Mon
estimation retraite », d'un an plus tôt tant que le départ s'y ouvre (02f3ea9) ;
la pension du militaire s'ouvre le mois qui suit ses services, et non le mois
même où ils s'achèvent, dans les deux moteurs (6b60b75). Le défaut de la
descente était au modèle : il déplace 3 323 des quelque 431 000 couples de la
population, et trois départs anciens de la grille du coût, dont GitHub refait les
tables figées. Le balayage du militaire part de l'âge où sa pension s'ouvre, au
mois près, sans sonde au mois.**

**La demande.** Vague du 28 octobre 2026, une session par tâche, que le
propriétaire ne suit pas pas à pas : le point « au modèle, ce que laissent les
notes du site » du bloc de l'étape, que « Hors de l'étape » détaille dans la note
`2026-10-25-etape-14-decote-des-carrieres-qui-le-peuvent.md` — la descente vers
la carrière longue dans le départ des cas types, à vérifier
(`2026-10-25-etape-14-estimation-des-carrieres-inactives.md`), puis l'âge où
s'ouvre la pension du militaire, au mois près
(`2026-10-25-etape-14-descente-vers-la-carriere-longue.md`), hors des deux
questions que le bloc réserve au propriétaire.

**Ce qui est fait.**

- *La descente, vérifiée.* Le droit date la durée cotisée de la carrière longue,
  comme celle du taux plein, par une soustraction signée : liquidée à tout âge,
  une carrière sans activité depuis qu'elle a sa durée la réunit à l'âge même du
  départ, et le point fixe, parti de l'âge écrit, y reste. Le test
  (`test_liquidation.py`,
  `test_le_pilote_fait_descendre_a_la_carriere_longue_une_carriere_qui_ne_valide_plus`,
  au niveau rapide, sous les règles du taux plein et de l'ouverture), le cas du
  site : né en 1966, entré à seize ans et sans activité depuis 2025, l'année de
  ses 59 ans, un salarié a 43 × 4 = 172 trimestres cotisés à la fin de 2024 ; il
  en a validé cinq avant la fin de l'année de ses dix-huit ans, non de ses
  seize, et la carrière longue lui ouvre son départ à 60 ans, au taux plein
  (L. 351-1-1, D. 351-1-1 dans sa version du 1er septembre 2023). Vu rouge pour
  cette raison : le pilote le faisait partir à 64 ans, l'âge écrit, et à 63 ans
  et 3 mois, l'âge légal, sous la règle de l'ouverture.
- *Le correctif* (`pilote.descendre`, que `age_de_depart` appelle après le point
  fixe et la reprise de l'âge d'annulation) : la boucle du premier âge
  d'`agesDeLEstimation` (db3aef0), d'un an plus tôt tant que le départ s'y
  ouvre, que le droit lui oppose un âge qui ne le dépasse pas, qu'il se confirme
  ou non. `point_fixe` ne change pas, ni son jumeau, `pointFixe` ; `descendre`
  n'a pas de jumeau, le départ des cas types ne tournant qu'en Python. Il coûte
  au moins une interrogation du droit de plus à un départ qui ne descend pas,
  les réponses étant gardées le temps d'un départ. Aucun départ de la mesure ne
  sonde un âge que la carrière refuse : la garde du site (`sansRefus`) n'a pas
  de cas, et n'est pas reprise.
- *L'ouverture du militaire.* « Lorsqu'un militaire non officier est radié des
  cadres […] ou encore s'il réunit, à la date de son admission à la retraite,
  dix-sept ans de services effectifs » (L. 24, II, 2°, LEGIARTI000047452804 ;
  quinze ans jusqu'au 1er juillet 2011, LEGIARTI000006362730) ; sa mise en
  paiement « ne peut être antérieure à la date de la décision de radiation des
  cadres » (L. 26), et elle « est due à compter du premier jour du mois suivant
  la cessation de l'activité » (L. 90, I, LEGIARTI000023034140, pour les
  pensions liquidées depuis le 1er juillet 2011). Le modèle datait l'ouverture
  du mois même où les services s'achèvent (`Carriere.age_de_service`), un mois
  avant le premier départ qui les a : liquidée ce mois-là, la carrière n'en a
  pas le dernier, et aucun âge ne se confirmait. Le test
  (`test_simulateur.py`,
  `test_la_pension_militaire_s_ouvre_le_mois_qui_suit_ses_services`) : né le
  1er janvier 1972 et engagé en janvier 1990, un sous-officier réunit ses quinze
  ans fin décembre 2004 ; sa pension s'ouvre au 1er janvier 2005, à 33 ans, à
  quelque âge qu'il parte ensuite, et liquidée au 1er décembre 2004, avec
  quatorze ans et onze mois de services, elle ne l'est pas. Vu rouge à 32 ans
  et 11 mois. Le test de la durée selon l'année
  (`test_la_duree_militaire_se_lit_a_l_annee_ou_l_ancienne_est_atteinte`) passe
  de 32,92, 34,50 et 34,92 ans à 33 ans, 34 ans et 7 mois et 35 ans, chacun le
  mois qui suit ses services. Le correctif : l'âge du mois qui suit, en Python
  (`age_de_service`) puis en JavaScript (`ageDeService`), le cas du test
  reproduit dans `tests/js/moteur.test.js`, vu rouge de même. Les marins, dont
  l'ouverture passe par la même date (`ouverture_par_services`, R. 2 de leur
  code), le suivent : l'exemple de l'ENIM, Gaspard à 50 ans, ne bouge pas, ses
  25 ans de services s'achevant avant.
- *L'année de sa durée.* Le premier correctif déplaçait l'année où le modèle lit
  la durée du militaire né un 1er janvier : l'anniversaire de son âge
  d'ouverture tombe le mois de sa pension, et le sous-officier de 1972 se voyait
  opposer la durée de 2005, 154 trimestres. Jusqu'en 2008, elle se lit à
  l'« Année au cours de laquelle sont réunies les conditions mentionnées au I et
  au II de l'article L. 24 » (loi n° 2003-775, article 66, II), et L. 13 n'a pas
  de III de 2004 à 2014 (LEGIARTI000006362702) : 2004, 152 trimestres. Le test
  (`test_la_duree_du_militaire_se_lit_a_l_annee_ou_ses_services_s_achevent`),
  né le 1er ou le 15 janvier, vu rouge à 154 ; le correctif
  (`annee_ouverture_des_droits`, `anneeOuvertureDesDroits`) lit l'année du mois
  où les services s'achèvent, celui qui précède la pension, à quelque jour que
  le militaire soit né. La fiche `militaires_duree_requise` dit la correction,
  ses lectures et ce qu'elles laissent ; le cliquet des textes descend de deux
  rédactions, à 9 504.

**Ce que montrent les mesures.**

- *La grille du coût*, des générations 1880 à 2020, sous les conventions du
  dépôt et sous celles du COR : trois départs descendent, tous anciens — l'agent
  des IEG né en 1890, de 57 à 56 ans, en 1946, à la création de son régime ;
  l'artisan né en 1910, de 64 à 63 ans, en 1973, à l'alignement de la CANCAVA ;
  l'exploitant agricole né en 1925, de 64 à 61 ans, en 1986. La carrière
  heurtée, hors des grilles, née en 1880, de 65 à 60 ans. Les tables figées le
  disent : `test_agregats.py` (dix tests, « les … figés sont ceux que le modèle
  calcule »), `test_cout.py` et `test_affirmations.py` (le bilan figé : le
  coefficient du notionnel rétroactif en 2002 passe de 4,6484 à 4,6319) ;
  GitHub les refait. `test_grille_large.py` passe entier (76 tests), le reste de
  `test_cout.py`, `test_facteurs_depense.py` et `test_affirmations.py` aussi
  (865).
- *La population* : les 14 874 cas types, aux 29 générations de 1880 à 2020,
  sous l'ancien pilote et sous le nouveau, au simulateur de la projection. 3 323
  couples partent plus tôt : 2 311 d'un trimestre, 292 d'un semestre, 361 d'un
  an, 359 de deux à six ans ; 3 109 sous la règle du taux plein, 214 sous celle
  de l'ouverture ; 2 870 des générations 1910 à 1945, 413 de 1950 à 2020. Trois
  familles : les carrières fragmentées à temps partiel du salariat privé (2 601,
  dont 2 301 d'un trimestre et 292 d'un semestre), qui, ne validant pas quatre
  trimestres par an, ne descendent que d'une fraction par passe ; les fonctionnaires super-actifs
  polypensionnés de l'État (196), entrés dans leur corps après dix ans de privé
  (`ANNEES_PRIVE`), dont les services ne s'achèvent qu'à 59 ans quand le droit
  leur oppose 57 ans à tout âge plus tardif — de 65 à 59 ans, et de 63 ans et
  demi à 57 ans et demi pour les nés en 1955 — ; et les générations anciennes,
  sous un droit qui change avec la date (les artisans de 1910, les exploitants
  de 1925, les IEG de 1890, des salariés de 1910 de 62 à 60 ans).
- *Les témoins de simulation* (`construire_temoins.py`, refaits pour voir, non
  commités) : au scénario 1, l'âge d'ouverture des témoins militaires recule
  d'un mois, de 35 ans et 10 mois à 35 ans et 11 mois pour `statut_militaire`,
  et aucune durée ni aucune pension ne bouge ; aux scénarios 3 et 5, le
  notionnel prospectif, qui lit cet âge, sert de 0,55 à 0,60 % de moins à trois
  témoins (`statut_militaire`, `contribution_etat_entiere_militaire`,
  `statut_militaire_officier_1965`). Aucun rendu de page ne change.
- *Le balayage du militaire* (`cycle_de_vie.py --ages militaire`) part de 35 ans
  et 11 mois pour le né en 1960, en janvier 1996, et de 37 ans et 11 mois pour
  le né en 1990, en 2028 : l'âge où sa pension s'ouvre, que le point fixe trouve
  désormais seul. Il partait de 36 ans et demi et de 38 ans et demi.
- *Les deux moteurs* s'accordent : le cas de `moteur.test.js` passe, aucun
  témoin militaire refait ne s'écarte du portage, et les deux confrontations sur
  les requêtes des témoins (`test_droit.py`, `test_liquidation.py`) gardent le
  même nombre d'écarts avec et sans le changement, 29 et 36, ceux qu'elles
  impriment étant des libéraux (« Trouvé en chemin »).

**Trouvé en chemin.**

- *La même classe* (`src/CLAUDE.md`), laissée, chacune à une session :
  - le parent de trois enfants (`depart_parent_trois_enfants`) s'ouvre le mois
    même où ses conditions sont réunies (`age_au(reunies)`) : quand ses quinze
    ans de services les réunissent, la carrière liquidée ce mois-là ne les a
    pas, et aucun âge ne se confirme, comme le militaire. Le test de la mère née
    en 1950 tient 39 ans et 10 mois, « l'ouverture à la date des conditions » de
    Destinie 2, et `test_oracle_familles.py` compare l'année à OpenFisca : à
    reprendre avec eux ;
  - l'emploi classé (`derogation_active`) s'ouvre à son âge anticipé si ses
    services sont réunis à la liquidation : quand ils s'achèvent plus tard, le
    droit propose l'âge anticipé, et la descente ne trouve l'ouverture qu'à
    l'année près — exacte pour le super-actif polypensionné, dont les services
    s'achèvent à un nombre entier d'années de l'âge écrit. Le droit pourrait
    proposer le mois qui suit les services, comme il le fait des marins ;
  - l'année de la durée sous le III de L. 13 (2014 à 2023), « l'année à compter
    de laquelle la liquidation peut intervenir », et sous le XXIV, C, de la loi
    de 2023, « ceux pouvant liquider leur pension à compter du 1er septembre
    2023 » : le modèle les compare au mois de l'anniversaire de l'âge d'ouverture
    (`duree_requise_avant_soixante_ans`), celui des services pour qui est né en
    cours de mois, le suivant pour qui est né un premier ; l'article 5 de la loi
    de 2003, de 2009 à 2013, reste à lire (fiche `militaires_duree_requise`).
- *Les générations anciennes* descendent sur la lecture que le modèle fait de
  leur droit, que la session n'a pas relue : l'exploitant de 1925 sur la loi
  n° 86-19 (`age_60_agricole_1986`, 60 ans dès le 1er janvier 1986), dont
  l'index ne garde pas l'article de l'âge ; l'artisan et le salarié nés en 1910,
  au taux plein à 63 et à 60 ans en 1973 et en 1970.
- *Les libéraux*, sur `main` : sept tests de la suite rapide (`test_pont.py`,
  `test_coupures_au_mois.py`, `test_cycle_de_vie_script.py`, la surcote
  parentale des deux moteurs) échouent chez moi avec et sans ce changement, sur
  les cotisations revalorisées des libéraux, de l'ordre de 10⁻⁵, que le portage
  lit au paquet du site : aucune course de GitHub n'est allée au bout depuis
  18d7da2, chaque envoi de la vague annulant la précédente, et le paquet n'a pas
  été refait.

**Ce qui ne bouge pas.** La page, qui ne lit pas la population (action 157) ;
`point_fixe` et `pointFixe`, ni l'estimation du site, qui se tait pour une
saisie militaire ; les pages, le style. La descente n'est pas une règle du
scénario 1 ; l'ouverture du militaire en est une, et l'entrée du journal de
veille la dit (`2026-10-28-action-138-etape-14-ouverture-du-militaire.yaml`).

**Ce qui reste.** Au propriétaire : la question du balayage du militaire —
partir de son âge de radiation « tant que l'âge où sa pension s'ouvre n'est pas
trouvé au mois » — perd sa condition, cet âge étant trouvé au mois : à lui de la
clore ; la sonde au mois demeure, pour le mois que la recherche manque à la
carrière longue et pour l'ouverture que la descente ne trouve qu'à l'année
(l'emploi classé). Une session par point : le parent de trois enfants, l'emploi
classé, l'année de la durée sous L. 13, III (« Trouvé en chemin ») ; les
limites, en fin d'étape.
