# Étape 8, neuvième partie : les points des conjoints et des aides familiaux dans les plans de revalorisation de 1998 à 2008

**Le 16 octobre 2026, la demande.** Le premier reste de l'étape : « les points
des conjoints et aides familiaux des plans » (point 3 de « Ce qui reste » de
la note du 14 octobre sur les plans). Le modèle ne servait les plans qu'aux
années de chef : une conjointe collaboratrice partie de 1998 à 2008 n'en
recevait rien. Session du modèle, une de douze.

**Ce que dit le droit** (journal de veille du 16 octobre, index LEGI et JORF).

- *Pensions prises depuis 2002* (L. 732-54-8 ; D. 732-141 à D. 732-146) : au
  taux plein, avec dix-sept ans et demi d'activité agricole, chaque année de
  conjoint collaborateur depuis 1999 reçoit B - 16 points, B = (MV2 - AVTS) /
  (37,5 × VP) aux montants du 1er janvier, la formule de C ; chaque année de
  conjoint participant aux travaux d'avant 1999, sans points, reçoit B, leur
  nombre minoré d'une année par année d'écart entre l'année d'effet et 1999,
  dans la limite de 37,5 moins l'écart avec 1998 ; toutes, chef d'abord, 37,5
  au plus ; une pension du 1er janvier compte de l'année d'avant. 8,63 points
  seulement à qui est resté conjoint participant en 1999 sans opter.
- *Pensions prises de 1998 à 2001* (L. 732-54-2 ; D. 732-118 à D. 732-131 ;
  décret n° 2002-297, articles 6 et 8) : la même chose depuis les pensions dues
  en 2002, sans condition de taux plein, à 32,5 ans d'activité agricole (27,5 à
  quinze ans de conjoint sans autre pension), minorée de 15, 15, 10, 10, 10 et
  40 % par année manquante sous 37,5 ; depuis 2007, 22,5 ans, et 5,5 % par
  année manquante, 4 % en 2008 (D. 732-131). Avant 2002, d'autres montants :
  8,63 points en 1998, 11,44 par année de conjoint en 1999 (décret n° 99-875),
  puis les décrets n° 2000-261 et 2001-170.

**Ce qui est fait**, dans les deux moteurs.

- *L'éligible agricole* porte `conjoint_avant_1999` (`conjointAvant1999`), les
  trimestres de collaborateur d'avant 1999 ; le schéma de l'étape « liquider »
  le nomme.
- *`majoration_retraite_proportionnelle`* sert, après les années de chef,
  `_points_des_conjoints` (`pointsDesConjoints`) : B - 16 par année retenue, la
  minoration des pensions d'avant 2002 ; la majoration en porte le détail
  (`conjoint_minimum`, `conjoint_annees`, `conjoint_points`). La révision des
  pensions déjà liquidées les relit chaque année jusqu'en 2008, comme les points
  du chef. Toutes les années de collaborateur sont présumées régularisées et,
  avant 1999, non rachetées.
- *La fiche* `majoration_retraite_proportionnelle` : un paramètre `conjoints`
  par version, la version de 2002 coupée en 2007 et en 2008 pour la minoration
  de D. 732-131, onze rédactions de plus citées ; le cliquet des textes descend
  à 9 723.
- *Les tests* (`test_minima_agricoles.py`, trois de plus, trois cas de plus dans
  la comparaison des deux moteurs) : B - 16 sur trente-six ans, B égal au C du
  chef ; une conjointe de trente ans partie en 2000, rien avant 2002, puis
  minorée à 60 %, 5,5 % et 4 % par année manquante ; la limite de 37,5 moins
  l'écart avec 1998 ; une pension du 1er janvier, que la garde des présomptions
  fait naître, compte de l'année d'avant.

**Les mesures.** Une conjointe collaboratrice de quarante-deux ans, partie en
2005 : 286 points, environ 950 € par an de plus jusqu'en 2008, que la PMR de
2009 relaie. Trente ans de conjointe, partie en 2000 : rien de 2000 à 2001,
97 points en 2002, 147 en 2008. Un seul témoin de simulation bouge.

**Ce que la vérification a trouvé.**

- *Le modèle dote de seize points* une année de conjoint d'avant 1999, que la
  loi ne dote d'aucun (plancher de R. 732-73), et de plus quand le revenu saisi
  d'avant 2004 en ouvre davantage : B - 16 la porte à B dans le premier cas, au
  delà dans le second. Déclaré dans la fiche.
- *Le différentiel peut reculer* d'une année sur l'autre, B suivant MV2 moins
  vite que la valeur du point (24,03 en 2006, 23,26 en 2008), comme A.

**Ce qui reste**, de cette partie :

1. Les pensions dues de 1998 à 2001 des pensions prises alors : 8,63 points en
   1998, 11,44 et 16 en 1999 (décret n° 99-875, articles 1er à 4), les décrets
   n° 2000-261 et 2001-170, avec leurs minorations.
2. Les années de chef des pensions prises de 1998 à 2001 sous dix-sept ans et
   demi de chef (D. 732-119, 4°, D. 732-125), sans condition de taux plein.
3. Ce que la saisie ne distingue pas : l'aide familial (dont les années d'avant
   1999 ne se minorent pas), le rachat, l'option tardive (8,63 points), la
   réversion à la date d'effet (D. 732-118) et sa majoration (D. 732-147) — avec
   le point 2 de la note « DM1 et points de chef ».
4. Les restes de l'étape, inchangés : la PMR unique de 2022 aux pensions prises
   depuis 2009 ; avant 1997, la révision des plans ; un montant de la MSA pour
   2015 à 2017 et 2019 ; le 2° de D. 732-110, II.
