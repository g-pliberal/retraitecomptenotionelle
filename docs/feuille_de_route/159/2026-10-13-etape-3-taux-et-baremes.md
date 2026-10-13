# Étape 3, les taux et les barèmes : le jaune 2027 confronté aux séries, trois corrections et quatre écarts déclarés

Les tableaux que l'étape 0 rangeait à l'étape 3 ont été relus dans le jaune
annexé au PLF 2027 (`data/brut/34465.pdf`, tiré de la branche `jaune-2027`,
empreinte vérifiée ; `pdftotext -layout` et le lecteur du dépôt), et confrontés
un à un aux séries et aux fiches, sous la règle du dépôt : le taux en vigueur au
1er janvier vaut pour l'année. Presque tout recoupe. Trois écarts se sont
corrigés et quatre déclarés, chacun dans son commit ; le document se contredit
lui-même en quatre endroits, qui ne changent rien au dépôt.

## Ce qui recoupe

- **La retenue** (tableaux 13, 35 et 36) : de 7,85 % en 2010 à 11,10 % depuis
  2020, dans les fiches de l'État, de la CNRACL et du FSPOEIE ; la coupure de
  2012, 8,39 % puis 8,49 % au 1er novembre, y est déjà déclarée. Le tableau D-2
  imprime 8,41 % pour 2012 : la moyenne de l'année.
- **Les contributions employeurs** (tableaux 14 et D-2) : l'État civil, ses
  militaires et la CNRACL, année par année de 2000 (2006 pour l'État) à 2026,
  dans `contribution_employeur_public.csv` et
  `contribution_employeur_militaires.csv`. Les écarts sont ceux que l'en-tête
  déclarait déjà : 2013, où le jaune donne la moyenne de l'État (71,78 %), et
  les abattements de décembre 2009 et 2013 ; le D-2 donne aussi les moyennes de
  2012 (27,32 % à la CNRACL, 33,04 % au FSPOEIE) là où le 14 et le dépôt
  prennent le 1er janvier. La colonne du droit commun, Cnav et Arrco d'un
  non-cadre, se retrouve en ajoutant aux taux du dépôt l'AGFF puis la CEG, qui
  n'ouvrent pas de points : 15,50 % en 2000, 16,67 % en 2026 pour l'employeur,
  10,55 % à 11,31 % pour le salarié.
- **L'Ircantec** (tableau 24) : ses neuf périodes de 1992 à 2026, tranches A et
  B, taux et part salariale, et les valeurs du point de 2026 (5,787 € et
  0,56053 €).
- **Le RAFP** (tableau 22B) : vingt-deux années de valeur d'acquisition et de
  service ; le taux de 10 %, partagé par moitié, le plafond de 20 % du
  traitement et le capital sous 5 125 points sont ceux de `rafp.yaml`.
- **La revalorisation** (tableau 110) : les dates et les taux de 2010 à 2026
  sont ceux du régime général, que la fonction publique suit depuis le
  19 décembre 2008. Pour 2020, le jaune résume (1 % sous 2 000 €, 0,3 %
  au-dessus) le barème lissé jusqu'à 2 014 € que le dépôt porte.
- **La durée requise** (tableaux 33 et 34) : 150 à 166 trimestres jusqu'à la
  génération 1957, par l'année d'ouverture de 2004 à 2008 puis par la table du
  régime général, et 167 à 172 ensuite, suspension de la LFSS 2026 comprise.
- **La décote** (tableau 38) : le coefficient, de 0,375 % en 2008 à 1,25 % en
  2015, et le nombre maximal de trimestres, qui n'est autre que l'écart entre
  l'âge légal et l'âge d'annulation « limite d'âge moins N trimestres » de
  `decote_fonction_publique.csv` ; la colonne du régime général aussi.
- **Le minimum garanti** (tableaux 45 et 46) : 1 366,35 € par mois au
  1er janvier 2026, soit les 16 396,19 € par an du dépôt, l'indice 227, 57,5 %
  à quinze ans, 2,5 points par an jusqu'à trente, 0,5 au-delà, et la règle sous
  quinze ans, du valide comme de l'invalide.
- **La catégorie active** (tableau 57) : les deux classements de
  `categorie_active.csv`, l'âge anticipé de cinq ans après dix-sept ans de
  services, l'âge minoré de dix ans après vingt-sept ; les cas que la table dit
  ne pas porter, le contrôle aérien et les égoutiers, y sont.
- **Le panorama** (tableau 12) : les six régimes des agents publics sont dans
  l'inventaire, et l'Ircantec cotise jusqu'à huit plafonds.

## Trois corrections

1. **La contribution employeur du FSPOEIE.** Le dépôt la rangeait parmi les
   régimes sans série « sous une forme exploitable », et prêtait à l'ouvrier de
   l'État la part patronale d'un salarié du privé. Le tableau 14 la donne depuis
   2000 : 24 % jusqu'en 2008, 27, 30 et 33 % de 2009 à 2011 (décret
   n° 2008-1328), puis un taux arrimé à celui d'un non-cadre, 35,01 % depuis
   2019. `sre_jaune_pensions.py` lit désormais ce tableau, à son titre, puisque
   l'édition 2026 le numérote 12 (et en donne les mêmes taux) ;
   `verifier_donnees.py` certifie les vingt-sept années dans
   `contribution_employeur_public.csv`. Le texte du jaune date les taux
   d'avant — « fixé en 1991 à 10,34 % », « porté à 24 % en 1999 » — sans le
   jour où ils ont pris effet : ils ne sont pas portés, la règle du 1er janvier
   ne s'appliquant pas sans lui. Ce que cela déplace, mesuré en régénérant : aux
   scénarios 4 et 6, les onze témoins d'ouvriers de l'État montent, de 34 % et
   37 % en médiane (de 3 % pour qui finit à l'État, à 44 %) ; rien d'autre ne
   bouge. Le README, la méthodologie et les limites le disent.
2. **L'indemnité temporaire de retraite** (pages 129 à 131). La fiche la disait
   fermée aux nouveaux bénéficiaires depuis 2009, et servie aux territoriaux. La
   loi de 2008 l'a mise en extinction jusqu'au 31 décembre 2027 : plafonnée
   pour qui résidait outre-mer avant le 13 octobre 2008, elle s'accorde jusque-là
   à de nouveaux bénéficiaires sous des conditions plus strictes, et plus à
   personne à compter du 1er janvier 2028 ; elle ne vise que les pensions du
   code des pensions civiles et militaires. Les taux par territoire (35, 40 et
   75 %) sont écrits.
3. **Les bénéfices de campagne** (tableau 49, page 124). La fiche disait le
   temps « compté double ou davantage » : la demi-campagne le compte une fois
   et demie, la campagne simple deux fois, la campagne double, de guerre, trois.

## Quatre écarts déclarés

1. **La ligne de l'État est celle des ministères**, que le modèle prête à tout
   fonctionnaire civil. Le D-2 donne aux opérateurs de l'État leur propre taux
   jusqu'en 2008 (33 % de 2001 à 2006, 39,50 % en 2007, 50 % en 2008) ; la note
   49 du tableau 14, le taux de la CNRACL à l'employeur territorial ou
   hospitalier d'un fonctionnaire de l'État détaché depuis 2020. Dans l'en-tête
   de `contribution_employeur_public.csv`.
2. **Le taux d'appel de l'Ircantec en 2026** : 127 % selon le jaune (page 79,
   note 82), 7,11 / 5,60 au dépôt. Le rapport rend exactement les points de la
   tranche A, que la caisse compte sur le taux contractuel quand les taux
   appelés sont arrondis au centième ; 1,27 les diminuerait de 0,03 %. Dans
   `verifier_donnees.py`, où la valeur se saisit, et l'en-tête de
   `valeurs_point.csv`.
3. **Soixante-quatre ans de limite d'âge** pour deux emplois actifs, les
   techniciens supérieurs du développement durable en mer et les syndics des
   gens de mer (tableau 57), quand la fiche `limite_age_fonction_publique` en
   dit soixante-deux pour les actifs que la loi ne nomme pas : une question de
   son `a_relire`, pour l'étape 9.
4. **Le seuil de vingt-huit heures** : le titulaire territorial ou hospitalier
   à temps non complet de moins de vingt-huit heures par semaine relève du
   régime général et de l'Ircantec (tableau 4, page 26) ; le routage, qui ne lit
   pas la durée de travail, le porte à la CNRACL. Une note du statut le dit.

## Ce que le document dit contre lui-même

- Le tableau 22B imprime 0,04 € de valeur de service du RAFP en 2006, et un
  rendement de 4,01 % que seule la valeur du dépôt, 0,0408 €, donne.
- Le récapitulatif du RAFP (page 69) imprime un rendement de 3,98 % en 2026,
  son tableau 22B 3,89 % : deux chiffres intervertis.
- L'astérisque du tableau 14 relève de 0,10 point en novembre et décembre 2012
  la CNRACL, le FSPOEIE et le droit commun ; la note (5) du D-2 porte le
  FSPOEIE à 33,23 % ces deux mois, 0,23 point de plus.
- La ligne « dont réforme de 2013 » du tableau 35 range sous 2010 la hausse de
  0,06 point qui est celle de 2014 (0,27 + 0,05 + 0,06 = 0,38).

## Ce qui va aux autres étapes

- **Étape 9, les règles** : les périodes d'AVPF et d'aidant comptées comme
  services pour le minimum garanti depuis 2023 (L. 17, R. 31-1, vingt-quatre
  trimestres au plus, décret n° 2023-752, page 119), qu'aucune fiche ne porte ;
  les limites d'âge à soixante-quatre ans ; le cumul emploi-retraite que la
  LFSS 2026 aligne sur le droit commun pour les pensions civiles liquidées à
  partir du 1er janvier 2027 (page 131).
- **Le FSPOEIE avant 2000** : le décret qui fixe 10,34 % en 1991 et 24 % en
  1999, à lire dans la base LEGI pour dater ces taux et les porter.
- **Étape 6, le financement** : la subvention d'équilibre du FSPOEIE, que sa
  série laisse dehors comme celles des autres régimes spéciaux (tableau 23).
