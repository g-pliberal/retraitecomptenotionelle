# Les grilles des classes des libérales, l'année de revenu et la classe de début

**Le 14 octobre 2026 : `cotisation_par_classes_liberales`, en deux commits.**

- *La grille de chaque époque, Cipav et CAVEC.* Le moteur tirait toute
  l'histoire d'une seule grille, celle de 2022 à la Cipav, celle de 2026 à la
  CAVEC, ramenée par le rapport des plafonds. Il sert désormais celle du
  texte de l'exercice : les classes de l'article 2, rédaction par rédaction
  (Cipav : trois classes en 1979, quatre en 1980, cinq en 1981, six de 1982 à
  2012, huit de 2013 à 2022 ; CAVEC : six classes en 1980, sept de 1987 à
  2007, huit de 2008 à 2025), le montant que le décret annuel donne à la
  classe de référence, lu dans les index LEGI et JORF pour 35 exercices de la
  Cipav et 39 de la CAVEC, et les bornes que les caisses publient. Un fichier
  neuf, `data/reference/regimes/classes_cotisation_epoques.yaml`, porte les
  trois pièces, chaque montant avec son identifiant ; le chargeur Python
  (`ClassesCotisation`) le déplie en une grille par exercice, que le paquet
  transmet au portage, dont le code n'a pas changé pour cela. Les
  conventions, chacune déclarée dans l'en-tête du fichier et dans la fiche :
  un exercice sans décret lu prend le montant le plus proche ramené au
  plafond ; les bornes non publiées sont les publiées les plus proches
  ramenées de même ; une époque de moins de classes prend les premières,
  rang pour rang. En 2008, la CAVEC prend le montant de 2009 ramené : le
  décret n° 2008-1303 fixe la classe A à 2 262 €, au prix du point de
  l'ancienne classe 4, qui ferait 70 687 € la classe H de la grille nouvelle.
  24 cas types baissent, de 2 % à 20 % au scénario 1 (les experts-comptables
  surtout : le moteur passait la classe A du décret de 12 % à 24 % depuis
  2009).
- *L'année de revenu et la classe de début d'activité*, dans les deux
  moteurs (`ClassesCotisation.revenu_retenu`, `revenuRetenu`), sur le bloc
  `regles` du même fichier : l'avant-dernière année à la CAVEC (2008-2018) et
  à la CARPV (1998-2021), la précédente à la CAVEC (depuis 2019), à la CARPV
  (depuis 2022) et à la Cipav (2016-2020) ; la première classe d'office les
  deux premières années civiles (CAVEC 2012-2018, CARPV 2014-2021, Cipav
  2016-2020), la première seulement ensuite à la CAVEC et à la CARPV. Le
  régime d'une autre année se reconnaît à l'affiliation de la ligne. Quinze
  cas types de plus bougent, de moins de 1 % pour dix d'entre eux. Un test
  (`test_la_classe_suit_l_annee_de_revenu_et_le_debut_d_activite`).
- *Les lectures*, au journal de veille
  (`2026-10-14-action-131-grilles-des-classes.yaml`). La fiche reste
  `approchee`.
- *Pour les pages* : rien.

**Ce qui reste de la fiche** : la CARPV de 1998 à 2015 (classes en actes
médicaux vétérinaires, montants en taux d'appel) ; les décrets de la Cipav de
1979 à 1985, 1989 et 1991, de la CAVEC de 1980 à 1983 ; la date d'effet de la
grille A à H de la CAVEC et le montant de 2008 ; les statuts d'avant 2016 de
la Cipav et d'avant 2008 de la CAVEC, au Bulletin officiel ; l'exemple de la
Cipav de 2022 aux exemples officiels, qui demande à l'oracle une grandeur de
cotisation.
