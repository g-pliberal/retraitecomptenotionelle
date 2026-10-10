# Le traitement du départ de janvier, rendu à temps plein

**Le 10 octobre 2026, la demande** : corriger le défaut du modèle que le
premier lot du levier 2 a levé (`2026-10-10-levier-2-premier-lot.md`) — le
fonctionnaire en retraite progressive qui part un 1er janvier liquidait un
traitement de référence à temps partiel —, dans le Python et dans son
portage, avec un test qui couvre le départ de janvier.

- *Le défaut.* `salaire_de_reference` (`droit/liquider.py`) rapporte à temps
  plein le traitement de l'année du départ, divisé par sa fraction d'année et
  par sa quotité. Sans ligne cette année-là — un départ au 1er janvier, une
  pension différée —, il rendait le revenu de la dernière année tel quel :
  réduit par la quotité d'une retraite progressive, et, l'année incomplète,
  par ses mois.
- *La correction.* Chaque année garde aussi son revenu à temps plein, chaque
  ligne rendue à sa quotité. Sans ligne l'année du départ, le traitement est
  celui de la dernière année, divisé par sa fraction d'année, borné au
  plafond d'une année pleine quand le régime l'est, puis revalorisé comme
  avant : au point d'indice, ou comme les pensions dans la pension différée
  (L. 25). Une année pleine à temps plein fait les mêmes opérations, dans le
  même ordre, et garde son résultat. Le portage
  (`moteur/js/droit/liquider.js`) suit ; les deux moteurs rendent les mêmes
  chiffres sur sept carrières construites pour le défaut, et sur les témoins.
- *Le droit, relu.* L. 15, I du code des pensions, en vigueur depuis 2004 :
  le traitement des services à temps partiel est celui d'un temps plein ; de
  même l'article 17 du décret n° 2003-1306 (CNRACL) et l'article 14 du
  décret n° 2004-1056 (ouvriers de l'État) ; L. 89 bis sert la pension
  partielle au fonctionnaire à temps partiel. La lecture est portée à la
  fiche `retraite_progressive`, et au journal de veille du jour.
- *Ce qui a bougé, au scénario 1.* La fonctionnaire née le 1er janvier 1963,
  à 70 % depuis ses 61 ans, partie au 1er janvier 2027 : un traitement de
  référence de 42 330,16 € au lieu de 29 631,12 €, une pension de l'État de
  27 639,11 € au lieu de 19 347,38 € (28 330,09 € sans retraite progressive,
  l'écart étant celui de ses services). Née le 15 décembre, partie au
  1er janvier 2028 : 43 367,25 € de traitement au lieu de 30 357,08 €.
  Radiée à 62 ans pour le privé après une année à 70 %, la même liquide une
  pension différée sur 40 437,79 € au lieu de 28 306,45 €.
- *Ce qui a bougé, dans les témoins.* Un des 801 témoins de simulation :
  `progressive_fonctionnaire_2024`, dont le départ de février ne change pas,
  mais dont les droits acquis se convertissent à la bascule, le 1er janvier
  2026, quand elle travaille à 70 %. Sa pension figée passe de 18 544,13 € à
  26 491,62 €, sa pension du scénario notionnel prospectif de 18 052,01 € à
  25 720,73 €, son écart au système actuel de −31,1 % à −1,9 % ; de même
  dans la variante employeur. Les pages témoins de la retraite progressive,
  celles d'une salariée, ne bougent pas. GitHub refait le témoin ; d'ici là,
  `tests/js/moteur.test.js` le trouve périmé.
- *Les tests.* `test_le_fonctionnaire_liquide_son_traitement_a_temps_plein`
  part aussi un 1er janvier (`jour=1`, que `_carriere` accepte désormais), et
  `test_la_pension_differee_liquide_le_traitement_a_temps_plein` naît. Sur le
  code d'avant, les deux nouveaux cas échouent ; `-m rapide` passe.
