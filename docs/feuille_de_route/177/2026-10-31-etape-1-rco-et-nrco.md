# Étape 1 : le RCO des artisans et le NRCO des commerçants, aux barèmes de la caisse

**Le 31 octobre 2026, ce qui est fait.** Les trois écarts du RCO et du NRCO
que l'étape 2 de l'action 175 remettait au modèle sont corrigés, un par
commit, chacun d'abord retiré de la liste du test qui le tenait, et vu rouge.

1. *Le taux de 2008 et de 2009.* Le décret n° 2007-1900 du 26 décembre 2007,
   lu au JORF (article 1er, JORFARTI000017765872), réécrit D. 635-7 à 7,2 %
   sous le plafond et 7,6 % au-delà au 1er janvier 2008 (I et II), mais fixe
   « par dérogation aux dispositions du I » la première tranche « à 7 % au
   titre de l'année 2008 et à 7,1 % au titre de l'année 2009 » (III), la
   seconde à 7 % et 7,5 % (IV). La fiche `rco_artisans` se coupe en 2008,
   2009 et 2010-2012 ; `ECARTS_COMPLEMENTAIRES` ne garde que le NRCO de 2004.
2. *L'assiette de 1997 à 2004.* L'article 1er du décret n° 97-166 du
   24 février 1997 (JORFARTI000001797721) remplace dans D. 635-4 « trois
   fois » par « quatre fois » le plafond, et LEGI le confirme
   (LEGIARTI000006738337, puis LEGIARTI000006738338 de 2002) : la fiche assied
   le RCO sur quatre plafonds dès 1997, et non plus seulement en 2005 avec
   D. 635-7, qui reprend la même limite. `ECARTS_ASSIETTE_MAXIMALE` est vide.
3. *Les huit valeurs de point.* Lues dans les quatre tables de l'ex-RSI que
   la base de législation joint aux barèmes du point du RCI, téléchargées et
   relues le jour même : le revenu de référence des artisans, 17,46 F en 1997
   et 18,88 F en 1998 (l'IPP portait 15,38 F, celui de 1996, puis 17,46 F),
   3,461 € en 2002 (l'IPP, 3,382 €, sous les 22,23 F de 2001), 4,500 € en
   2009 (4,324 €) ; la valeur de leur point, 1,776 F au second semestre de
   1996 (l'IPP gardait les 1,761 F du premier) et 0,29331 € au 1er décembre
   2007 (0,29259 €) ; celle du NRCO, 1,073 € au 1er décembre 2008 (l'IPP
   s'arrêtait à 1,067 €) et 1,115 € en 2010 (1,110 €). Aucun texte ne les
   fixe : D. 635-8 et D. 635-8-1 les laissent au conseil d'administration de
   la caisse. `ipp_points_independants.py` les met à la place de l'IPP
   (`VALEURS_DE_LA_CAISSE`), `valeurs_point.csv` les porte ;
   `ECARTS_POINTS` est vide.

Les deux moteurs lisent la même fiche et le même fichier de valeurs, le
JavaScript par le paquet (`moteur/donnees.json`) : refait sur le poste, il
remet d'accord les tests qui les confrontent ; seuls le témoin des
simulations et les pages toutes faites, que GitHub refait après le paquet, en
gardent l'ancienne valeur.

**Ce que le calcul en reçoit.** Moins de points au RCO : en 2008 et en 2009,
au taux de la dérogation ; en 1997, 1998, 2002 et 2009, au prix du point de la
caisse, plus haut que celui de l'IPP ; plus pour les revenus de trois à quatre
plafonds, de 1997 à 2004. Les cas types artisans, mesurés au moteur Python
avant l'action et après l'étape, perdent 45,67 € par an de pension du RCO pour
la génération 1950 (−0,97 %), 49,81 € pour 1960 (−1,15 %), 50,98 € pour 1970
(−1,50 %) ; leur revenu reste sous trois plafonds, et l'assiette de 1997 à
2004 ne les touche pas. Les valeurs de service de 1996 et 2007, et celles du
NRCO de 2008 et 2010, ne jouent qu'à une liquidation de ces années-là. La
certification du récupérateur, relancé le jour même, rend 85 valeurs
identiques au fichier de référence (`data/derive/certification.json`).

**Vu en chemin, non corrigé.** De 2009 à 2012, le plafond de la première
tranche du RCO n'est pas celui de la sécurité sociale : D. 635-7, dans sa
rédaction du 1er janvier 2008, l'indexe « sur la dernière valeur du revenu de
référence », dans la limite des prix hors tabac de l'année précédente, à
partir des 33 276 € de 2008. La fiche garde le plafond de la sécurité sociale
(assiette `plafonnee`), et aucune table de la caisse lue ne donne ce plafond
propre avant 2013 : un écart de quelques centaines d'euros d'assiette entre
deux taux voisins, à lire avant de le déclarer. La fiche le dit désormais,
aux périodes de 2009 et de 2010-2012.

**L'étape est faite.** La suite : l'étape 2, l'assiette minimale des
indépendants (`ECARTS_ASSIETTE_MINIMALE`).
