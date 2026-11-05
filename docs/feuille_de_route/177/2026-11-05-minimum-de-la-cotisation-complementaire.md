# Le minimum de la cotisation complémentaire des artisans et des commerçants, jusqu'en 2015 (file D)

**Le 5 novembre 2026, ce qui est fait.** Le minimum que le bloc « Reprise »
nommait, « D. 633-2, D. 612-6 », est celui de la COMPLÉMENTAIRE : celui du
régime de base, de 1973 à nos jours, est écrit depuis l'étape 2
(`assiette_minimale_independants.csv`). La complémentaire des artisans (RCO),
celle des commerçants (NRCO), puis le RCI ne l'opposaient pas
(`177/2026-11-03-etape-9-assiette-du-rco-ecrite.md`, « ce qui reste ») : c'est
écrit, dans les deux moteurs, le test d'abord.

**Ce que disent les textes**, lus dans l'index LEGI à jour du 4 novembre 2026,
version par version (`dila_cherche.py legi --num … --diff` et `--le`).

- *1979 à 1985.* Décret n° 78-351, article 3, I (LEGIARTI000006766103, seule
  rédaction, du 19 mars 1978 au 21 décembre 1985) : « Toutefois, le montant de
  cette cotisation ne peut être inférieur à celui qui serait dû au titre d'un
  revenu égal au revenu minimum prévu à l'article 2 du décret du 22 janvier
  1973 susvisé », 200 heures du Smic du 1er janvier. La phrase est au I, qui
  vise les assurés « autres que ceux visés aux II et III » : celui qui commence
  (le forfait d'un tiers, puis de la moitié du plafond) et l'aide familial.
- *1985 à 2004.* D. 635-4, ses quatre rédactions (LEGIARTI000006738335 à
  LEGIARTI000006738338) : la même phrase, « prévu à l'article D. 633-2 », au
  premier alinéa, qui vise les assurés « autres que ceux qui sont mentionnés
  aux troisième et quatrième alinéas ci-après ».
- *2004 à 2012.* D. 635-2, ses trois rédactions (LEGIARTI000006738016,
  LEGIARTI000006738017, LEGIARTI000020032159), pour les deux régimes que D. 635-1
  confie aux deux caisses : la même phrase, après « sous réserve des
  dispositions des articles D. 635-7 et D. 635-10 », qui portent les forfaits
  de début ; ni l'un ni l'autre ne pose d'autre minimum (toutes leurs
  rédactions de 1985 à 2013 relues). D. 633-2 dit alors 200 heures
  (LEGIARTI000006737879).
- *2012 à 2014.* D. 635-2 (LEGIARTI000025629861 au 5 avril 2012,
  LEGIARTI000025263548 au 1er janvier 2013) : « Pour les travailleurs
  indépendants dont la durée d'affiliation est au moins égale à
  quatre-vingt-dix jours au cours de l'année au titre de laquelle la
  cotisation est due, ladite cotisation ne peut être calculée sur une assiette
  inférieure à celle mentionnée au dernier alinéa de l'article D. 633-2 » ; et
  D. 633-2 (LEGIARTI000025629830, LEGIARTI000028435877) : 5,25 % du plafond
  « sans application du deuxième alinéa de l'article D. 612-6 », le prorata.
  C'est l'article 5 du décret n° 2012-443 qui modifie D. 635-2
  (LEGIARTI000025628394).
- *2015.* D. 635-2 (LEGIARTI000030034575) : « 5,25 % de la valeur du plafond
  mentionné au premier alinéa de l'article L. 241-3. La valeur de ce plafond
  est déterminée conformément au premier alinéa de l'article D. 612-6 », soit
  (LEGIARTI000025629812) « la valeur annuelle de ce plafond [...] en vigueur
  au 1er janvier de l'année au titre de laquelle la cotisation annuelle est
  due », sans le second alinéa, qui la réduit « au prorata de la durée
  d'affiliation ». La base, elle, passe à 7,70 % (LEGIARTI000030034546).
- *Depuis 2016.* La phrase est supprimée (LEGIARTI000031799392).
- *Le garde-fou.* Le décret n° 2012-443, article 4, V (LEGIARTI000025628392,
  puis LEGIARTI000030034758 en 2015), relève le pourcentage si l'assiette de
  D. 635-2 passe sous 200 heures du Smic du 1er janvier. Elle ne l'a jamais
  fait : 1 909,53 € contre 200 × 9,22 = 1 844 € en 2012, 1 944,18 € contre
  1 886 € en 2013, 1 971,27 € contre 1 906 € en 2014, 1 997,10 € contre
  1 922 € en 2015.
- *Le micro-entrepreneur* cotise « par dérogation » à L. 131-6, puis à
  L. 131-6-2 (L. 133-6-8, LEGIARTI000020541426, LEGIARTI000025013770,
  LEGIARTI000026798337) : « l'ensemble des cotisations » en pourcentage de son
  chiffre d'affaires, sans minimum, comme à la base.

**Ce qui est écrit.** Quatre lignes de plus à la série de l'assiette minimale,
qui ne nomment que les régimes complémentaires et que la base ne lit pas (elle
prend la première ligne de son statut et de son année) : `rco_artisans` de 1979
à 2003, 200 heures ; `rco_artisans nric` de 2004 à 2011, 200 heures ;
`rco_artisans nric rci` de 2012 à 2014, 5,25 % du plafond, quatre-vingt-dix
jours, sans prorata ; `rci` en 2015, de même. `assiette_minimale` (acquerir.py,
acquerir.js) sert la ligne du régime de base quand le code est le sien, sinon la
première qui nomme le code, au plafond et au Smic de l'année, sur la part de
l'année de la ligne ; elle tombe avec celle de la base (année cotisée, revenu
déclaré, hors du micro-entrepreneur, des dispenses, de l'exonération des DOM).
Le minimum ne s'oppose pas au forfait de début. Le paquet reste à la version
40 : sa structure ne change pas.

**Les valeurs attendues, posées à la main** (tests
`test_le_minimum_de_la_cotisation_complementaire_jusqu_en_2015` et
`..._de_2015_veut_quatre_vingt_dix_jours`, `tests/test_independants.py`). Les
points sont l'assiette, fois le taux, divisée par le revenu de référence ;
Smic du 1er janvier et plafond, `smic_horaire.csv` et
`plafond_securite_sociale.csv` ; taux et revenus de référence, ceux des tests
du RCO, du NRCO et du RCI qui précèdent (`valeurs_point.csv`).

| Cas | Année | Assiette minimale | Taux | Référence | Points | Avant |
|---|---|---|---|---|---|---|
| artisan, 100 € par an depuis 1977 | 1980 | 200 × 1,971166 = 394,23 € (2 586 F, la caisse) | 4,40 % | 1,003115 | 17,2924 | 4,3863 |
| | 1984 | 200 × 3,472789 = 694,56 € (4 556 F) | 4,40 % | 1,544309 | 19,7891 | 2,8492 |
| commerçant, 500 € par an depuis 2004 | 2005 | 200 × 7,61 = 1 522 € | 6,5 % | 14,112 | 7,0103 | 2,3030 |
| | 2007 | 200 × 8,27 = 1 654 € | 6,5 % | 14,648 | 7,3396 | |
| | 2010 | 200 × 8,86 = 1 772 € | 6,5 % | 15,483 | 7,4391 | |
| | 2011 | 200 × 9,00 = 1 800 € | 6,5 % | 15,808 | 7,4013 | |
| artisan, 1 000 € par an depuis 2012 | 2012 (RCO) | 5,25 % × 36 372 = 1 909,53 € | 7,2 % | 4,891130 | 28,1093 | 14,7205 |
| | 2013 (RCI) | 5,25 % × 37 032 = 1 944,18 € | 7 % | 17,309 | 7,8625 | |
| | 2014 | 5,25 % × 37 548 = 1 971,27 € | 7 % | 17,309 | 7,9721 | |
| | 2015 | 5,25 % × 38 040 = 1 997,10 € (la base : 7,70 %, 2 929,08 €) | 7 % | 17,324 | 8,0696 | 4,0406 |
| | 2016 | aucune : ses 1 000 € | 7 % | 17,324 | 4,0406 | 4,0406 |

En 2015, la règle seule : deux mois d'affiliation (59 jours) ne portent aucun
minimum ; trois (92 jours) en portent un entier, 1 997,10 €, non proratisé ;
et aucune règle de complémentaire en 2016. Vu rouge pour la raison attendue
(au RCO en 1980, 4,3863 points, ceux des 100 € de 1978), vert dans les deux
moteurs.

**Ce qui bouge.** Aucun des 930 témoins de simulation, aucune des 85 pages :
aucun n'a d'artisan ni de commerçant sous le minimum avant 2016. D'où un témoin
de plus, `minimum_complementaire_artisan` (né en 1955, artisan à 300 € par an
de 1979 à 2016, parti en juillet 2017), sans lequel la confrontation du jumeau
ne rougissait pas ; sans la règle Python, elle rougit de 39 écarts : son RCO,
au départ, 137,74 € par an au lieu de 271,65 €, son RCI 4,49 € au lieu de
23,25 €. Le paquet du site est refait (`moteur/donnees.json`) ; les agrégats ne bougent
pas.

**Ce que le texte ne tranche pas, déclaré** (fiche `assiette_rco_independants`,
approximations ; `docs/limites/3-systeme-actuel.md`).

- *Le forfait de début, de 2004 à 2011* : D. 635-2 pose le minimum « sous
  réserve » de D. 635-7, qui porte le forfait, sans dire s'il s'y oppose. Le
  modèle ne l'y oppose pas, comme le texte jusqu'en 2004. Il n'y a d'effet que
  si le forfait, que le modèle prend à proportion des mois, passe sous le
  minimum : en 2010, un tiers de 34 620 € sur deux mois, 1 923,33 €, passe
  1 772 € ; sur un mois, 961,67 €, non.
- *La cessation de 2012* : qui cesse en 2012 sans reprendre avant 2013 garde,
  pour ses cotisations définitives de 2012, le droit d'avant le décret
  n° 2012-443 (article 10, II, LEGIARTI000025628404) : 200 heures, 1 844 €,
  sans condition de durée. Le modèle lui oppose 5,25 % et les quatre-vingt-dix
  jours.

**Vu en chemin, non corrigé (candidat).** L'article 10, II, du décret
n° 2012-443 vaut aussi pour la base (D. 633-2, modifié par son article 4) : la
série de la base donne 5,25 % et quatre-vingt-dix jours à toute l'année 2012,
même à qui cesse en 2012. Écart de 65,53 € d'assiette, ou d'un minimum de
1 844 € sous quatre-vingt-dix jours.

**L'étape est faite.** Reste à l'action le salarié de Mayotte, que le
propriétaire n'a pas autorisé, et, pour la file suivante, le forfait du
commerçant qui commence et celui de l'artisan de 2009 à 2011.
