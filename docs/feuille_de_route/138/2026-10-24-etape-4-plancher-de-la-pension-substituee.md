# Étape 4, quatorzième partie : le plancher de la pension substituée, l'AVTS ou la pension d'invalidité d'avant juin 1983, et la catégorie de la pension d'invalidité

**Le 24 octobre 2026, la demande.** Le propriétaire, dans la septième vague des
sessions du jour : le premier point sans propriétaire du bloc de l'étape, le
plancher de la pension substituée, que la comparaison des circulaires des
majorations de 1972 à 1982 suppose, avec le groupe de la pension d'invalidité.
Les trois ou douze mois de la date d'effet viendront dans une session suivante ;
les décrets des salariés agricoles de 1976 et 1977, au fac-similé, restent au
propriétaire, et ce que le bloc renvoie au site, au site.

**Ce que dit le droit, lu le jour même** (journal de veille du 24 octobre, « plancher
de la pension substituée » ; fiche `pension_d_invalidite_substituee`).

- *Le plancher.* « La pension de vieillesse substituée à une pension d'invalidité ne
  peut être inférieure au montant de l'allocation aux vieux travailleurs salariés » ;
  « les titulaires d'une pension d'invalidité liquidée avant le 31 mai 1983 peuvent
  prétendre à une pension de vieillesse qui ne peut être inférieure à la pension
  d'invalidité dont bénéficiait l'invalide à cet âge » (L. 341-15). La loi
  n° 83-430 avait ôté la seconde phrase dès le 1er avril 1983, la loi n° 84-575 l'a
  rétablie à la même date (circulaires Cnav n° 84/83 et n° 94/84) ; avant, l'article
  62 de l'ordonnance de 1945, puis L. 322 du code de 1956.
- *La comparaison.* « La retraite calculée au taux maximum de 50 %, éventuellement
  augmentée de la majoration du minimum contributif » se compare « au montant entier
  de l'AVTS », ou « au montant calculé de la pension d'invalidité précédemment
  servie », jamais sous l'AVTS ; « Le montant le plus élevé est servi », puis
  s'ajoutent la majoration pour enfants et la majoration pour tierce personne
  (circulaire n° 2018-18, 1.3) ; sous la liquidation unique, la retraite qu'elle sert
  (7.1). La réversion se calcule « avant comparaison au minimum » (exposé « Retraite
  de l'assuré décédé »).
- *La pension d'invalidité.* Trois groupes, « capables d'exercer une activité
  rémunérée », « absolument incapables d'exercer une profession quelconque », et ceux
  qui ont en outre besoin d'une tierce personne (L. 341-4) ; 30 % du salaire annuel
  moyen au premier, 40 % au deuxième, 50 % depuis le décret n° 61-272 du 28 mars 1961,
  qui majore les pensions servies ; le troisième au taux du deuxième, sa majoration à
  part. Le salaire annuel moyen : des dix dernières années d'assurance (ordonnance de
  1945, article 56), puis, depuis le 30 décembre 1972, des dix meilleures d'après 1947,
  que forment les règles de la pension de vieillesse (décret n° 45-0179, article 59).
  Aucun exemple chiffré ne compare la pension au plancher.

**Ce qui est fait.**

- *La catégorie* se déclare : un attribut de la décision médicale de la pension
  d'invalidité dans la chronologie (`categorie`, 1, 2 ou 3, refusé sinon), que la
  carrière lit (`PensionDInvalidite.categorie`), dans les deux moteurs. Non dite, la
  présomption `categorie_de_la_pension_d_invalidite`, neuve au vocabulaire et au
  § 5.6, la pose : la première à qui travaille à l'âge de la substitution, la deuxième
  sinon (`categorie_de_la_pension`).
- *La pension d'invalidité d'avant juin 1983* (`pension_d_invalidite_servie`) : le taux
  de sa catégorie, que les versions disent (`taux_des_categories`, la version
  `ordonnance_1945` coupée au 30 mars 1961, la neuve `majoration_de_1961`), du salaire
  annuel moyen de ses dix années (`annees_du_salaire_moyen`) d'avant son année,
  formé par la règle de la pension de vieillesse au 1er janvier de cette année, puis
  revalorisé comme les pensions. Son régime : celui des affiliations de l'année où
  elle commence, le régime général ou les salariés agricoles.
- *Le plancher* (`plancher_de_la_substitution`, et l'étape « compléter ») : la pension
  de ce régime, ou de la liquidation unique, portée au minimum contributif, puis à
  l'AVTS de la date d'effet, ou à la pension d'invalidité d'avant le 31 mai 1983 quand
  elle est plus haute ; son détail le dit, et un avantage « Plancher de la pension
  substituée », sous le code du minimum, que la réversion ne compte pas ; la
  majoration pour enfants se calcule après. Les deux moteurs, au bit près.
- *Les fiches* : `pension_d_invalidite_substituee` — ses versions, ses textes (décret
  n° 61-272, article 59 du décret n° 45-0179, L. 341-4, L. 341-5, loi n° 84-575), huit
  rédactions de R. 341-4 à R. 341-6 sans effet, cinq écarts, la présomption,
  l'historique ; l'écart de l'ex-invalide de `majorations_forfaitaires_1972_1982`. Le
  cliquet des textes descend à 9 520. La page des limites.
- *Les tests* (`test_invalidite.py`), posés à la main depuis les textes et vus rouges :
  l'ex-invalide de 2022 porté aux 3 566,43 € de l'AVTS ; celui de 1982, sa pension de
  2002 portée à sa pension d'invalidité de deuxième catégorie, refaite depuis R. 341-4
  sur les coefficients publiés, et laissée à sa pension de vieillesse en première ; la
  catégorie déclarée, présumée et refusée ; les taux de 1960 et de 1962 ; les deux
  moteurs sur deux saisies. La chronologie confrontée sur une catégorie déclarée et
  une refusée (`test_chronologie.py`).

**Les mesures.** Sur les 907 témoins de simulation, un seul bouge :
`invalidite_substituee_en_1980`, l'ex-invalide de 1975 substitué en avril 1980, sa
pension de 141 trimestres sur 150 portée à sa pension d'invalidité, de 4 566,68 € à
4 844,35 € au régime général (+ 6,1 %), + 5,35 % pour toute sa pension, dans les
scénarios 1, 3 et 5. Les ex-invalides au plancher de l'AVTS gardent leurs ressources
quand l'ASPA les complète : seule change la part de la pension.

**Ce qui reste.**

1. *La comparaison des majorations de 1972 à 1982 au plancher* : le modèle majore la
   pension servie, plancher compris ; la caisse ne majorait que la pension des
   cotisations, et la comparait au plancher (fiche `majorations_forfaitaires_1972_1982`).
2. Le plancher comparé à chaque changement de l'AVTS, comme la caisse le fait ; la
   somme des pensions d'invalidité du régime général et des salariés agricoles sous la
   liquidation unique ; la pension d'invalidité proratisée, qui n'en a pas ; l'AVTNS et
   l'allocation différentielle des indépendants.
3. *Au site* : le champ de la catégorie de la pension d'invalidité, que la saisie
   passerait à la chronologie (`invalidite.categorie`).
