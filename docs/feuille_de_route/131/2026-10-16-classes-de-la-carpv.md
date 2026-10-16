# Les classes de la CARPV de 1998 à 2015, au taux d'appel de chaque décret

**Le 16 octobre 2026 : `cotisation_par_classes_liberales`, la CARPV.**

- *Ce qui est lu.* L'article 2 du décret n° 50-1318, versions du 2 décembre
  1997 et du 30 décembre 2012 : classes B, C et D à 480, 600 et 720 actes
  médicaux vétérinaires (AMV), sous 4 500 AMV, jusqu'à 6 000, au-delà, pour
  16, 20 et 24 points, « au taux d'appel » que fixe chaque année un décret ;
  le taux de chacun des dix-huit exercices de 1998 à 2015, au décret annuel
  des complémentaires libérales (77 % de 1998 à 2001, 78,5 %, 80 %, 85 %,
  87 %, 90 %, 93 %, 96 %, 97 %, 100 % en 2010 et 2011, 101 %, 101,5 % en
  2013 et 2014, 104 % en 2015), chacun avec son identifiant, dans
  `classes_cotisation_epoques.yaml`. Les montants « classe A (classe de
  référence) » des vétérinaires aux articles 2 des décrets de 2012 à 2014
  sont ceux de l'invalidité-décès.
- *Ce qui ne l'est pas : la valeur de l'AMV.* Le décret la renvoie au
  conseil de l'ordre (l'« acte médical ordinal », abandonné en 2015, notice
  du décret n° 2015-712) : ni l'index LEGI ni le JORF ne la portent, et la
  recherche sur le web n'a rien rendu. CONVENTION, déclarée dans le fichier
  et la fiche : la valeur d'achat du point de 2016 (446 €) prolonge l'appel
  de 2015 à 104 %, et l'AMV de chaque exercice antérieur en est tirée au
  rapport des plafonds (14,08 € en 2015). Les bornes : celles du livret de
  2024, ramenées de même, comme le CSV le fait déjà pour 2016 à 2023.
- *Le moteur.* Le chargeur Python (`ClassesCotisation._deplier_epoques`)
  sait une époque à `taux_appel` : le montant lu, ramené à un appel de 100 %
  par le `taux_appel` qu'il porte, puis au plafond, est multiplié par le taux
  de l'exercice. Le paquet transmet la grille dépliée : le portage n'a pas
  changé. Un test (`test_la_carpv_de_1998_a_2015_suit_le_taux_d_appel_du_decret`).
- *L'effet.* Les sept cas types vétérinaires baissent de 3,7 % à 14,4 % au
  scénario 1 (le moteur reportait la grille de 2016 ramenée, à 104 %
  d'appel, sur des exercices appelés à 77 %). La fiche reste `approchee`.
- *Pour les pages* : rien, hors des chiffres que GitHub refait.

**Ce qui reste.** Au propriétaire : la valeur de l'AMV de 1997 à 2015,
à demander à l'ordre des vétérinaires ou à la CARPV (bulletins, rapports
annuels), qui remplacerait la convention. Non porté : le barème réduit des
moins de trente-trois ans au 1er janvier 1997 (décret n° 97-1112, article 3,
II : 304, 380 et 456 AMV, jusqu'à l'année qui suit le trente-troisième
anniversaire), qui dépend de l'âge et de la date d'inscription ; avant 1998,
les actes selon l'âge, où la grille de 1998 ramenée tient lieu. Le reste de
la fiche est inchangé (note du 14 octobre).
