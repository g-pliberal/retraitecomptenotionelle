# Étape 8, deuxième partie : le relèvement des pensions des exploitants déjà liquidées, au 1er septembre 2023

**Le 8 octobre 2026, la demande.** Avec la majoration exceptionnelle des
petites pensions de l'étape 17, le propriétaire : « Le relèvement des pensions
des exploitants déjà liquidées, au 1er septembre 2023 lui aussi (loi
n° 2023-270, article 18, VI), est le point 5 de l'étape 8 et le point de
TRAJECTOiRE au chantier 138.8 : si le mécanisme est le même, fais les deux, une
note par étape. » Le mécanisme est le même : un relèvement, à une date, de
pensions déjà liquidées, calculé sur ce qu'elles servent ce jour-là, puis mené
avec elles jusqu'à l'échéance — « faire vivre », non la liquidation.

**Ce que dit le droit, lu le jour même** (journal de veille du 8 octobre ; la
fiche `relevement_des_exploitants_2023` cite chaque texte).

- *Le II de l'article 18* substitue, dans L. 732-56 (points gratuits de la RCO)
  et L. 732-63 (complément différentiel), le taux plein « dans le régime » à la
  durée requise tous régimes ; *son VI* l'applique dès le 1er septembre 2023
  « aux assurés dont la pension a pris effet avant cette date pour les pensions
  dues à compter de la même date », et, pour le complément de ces pensions, «
  les montants du salaire minimum de croissance et des éléments de calcul [...]
  sont ceux en vigueur au 1er septembre 2023 ». La réponse ministérielle à la
  question n° 16179 le dit des pensions prises depuis 1997.
- *Ce jour-là*, le SMIC brut est de 11,52 € de l'heure (arrêté du 26 avril
  2023) ; la PMR des pensions prises avant, de 8 970,86 € (D. 732-111, rédaction
  du 12 août 2023). Les décrets lisent le SMIC net à deux dates — celle de
  l'année « au titre de laquelle le complément est dû » (D. 732-166-4), celle
  de l'effet de la pension (D. 732-166-5-1) — ; la loi tranche pour ces
  pensions.

**Ce qui est fait.**

- *La fiche* `relevement_des_exploitants_2023`, deux versions selon la date
  d'effet de la pension de base : avant septembre 2023, le relèvement, au SMIC
  net agricole de ce jour, 9,0282 € de l'heure — 11,52 € net de la part que les
  montants publiés par la MSA déduisent, estimé — ; depuis, rien à relever.
- *Le départ* écrit ce que le relèvement relira (`ChefDExploitation`, dans
  `droit/completer.py` et son jumeau) : l'éligible agricole — taux plein, durée
  requise, durées —, les points de RCO acquis, si le complément a été servi, et
  les points gratuits que le taux plein ouvre quand la durée ne les avait pas
  ouverts (`points_gratuits`, qui prend `au_taux_plein`).
- *« Faire vivre »* (`relever_les_exploitants`, et `releverLesExploitants`)
  attribue au 1er septembre 2023, à qui avait le taux plein sans la durée
  requise, les points gratuits, puis le complément différentiel calculé ce
  jour-là sur les pensions qu'il sert alors, ces points compris, à la règle,
  au SMIC et à la PMR de ce jour (`complement_differentiel`, qui prend
  `quand`, `smic` et `pmr`) ; les uns et les autres suivent ensuite la valeur
  du point. La pension de RCO servie les porte (`RegimeServi.relevement`) ;
  l'échéancier inscrit un début de composante, induit, le 1er septembre 2023.
- *Les données* : le SMIC net agricole de 2023 passe d'estimé à lu — la note
  de presse de la MSA du 14 février 2023, 1 138,63 € par mois au 1er janvier,
  le redonne au dix-millième (8,8323 €) — ; son test le rejoue avec ceux de
  2021 et 2026.
- *Les tests* (`tests/test_minima_agricoles.py`, quatre de plus) : le chef
  parti en 2016 sans la durée requise, son relèvement et la formule de
  D. 732-166-4 refaite ; celui parti en 2012, aux seuls points gratuits ; ni
  celui qui avait la durée requise ni celui parti après septembre 2023 ;
  l'événement de l'échéancier ; le journal des deux moteurs, sur deux requêtes
  relevées de plus.

**Les mesures.** Un chef parti en février 2016 à 66 ans, avec 124 trimestres
de chef, au taux plein par l'âge : 1 800 points gratuits et 7 300 points de
complément au 1er septembre 2023, 276,19 € par mois, 299,87 € en 2026 ; ses
deux pensions agricoles passent de 609 à 886 € par mois, sous la cible
proratisée de 891 €. Parti en 2012 : les 1 800 points gratuits seuls, 54,63 €
par mois. Parti en 2022 : 800 points gratuits et 5 942 de complément, 204,62 €.
Aucun des 763 témoins n'est un chef relevé ; les deux moteurs y concordent.

**Ce que la vérification a trouvé.**

- *Pourquoi depuis 2003 et depuis 2015 seulement.* Le modèle ne sert la RCO
  qu'aux pensions prises depuis 2003 et le complément qu'à celles prises depuis
  2015, à leur liquidation : à qui avait la durée requise et une pension plus
  ancienne, il ne sert ni les points gratuits de 2003 ni le complément de 2015.
  Ouvrir le relèvement à ces pensions-là servirait davantage au chef sans la
  durée requise qu'à celui qui l'avait : il attend que le complément et les
  points de ces pensions soient servis (« Ce qui reste », 2).
- *Le complément d'une pension prise de 2015 à octobre 2021* reste, chez qui
  avait la durée requise, celui de sa liquidation (75 %), quand la loi l'a porté
  à 85 % en novembre 2021 ; celui que le relèvement ouvre est à 85 % du SMIC de
  septembre 2023. Le relèvement est juste ; c'est l'autre qui manque.
- *L'estimation du SMIC net agricole de 2023* tombait juste : la MSA publie le
  montant que la série estimait.
- TRAJECTOiRE porte chaque année la pension totale des pensions servies à la
  cible, sans le prorata ni le plafond des pensions agricoles ; le dépôt ne
  relève que ce que le VI ouvre, une fois, au 1er septembre 2023.

**Ce qui reste**, de cette partie :

1. Lire comment la MSA a appliqué le VI : le SMIC net du 1er septembre 2023
   qu'elle a retenu, la PMR des pensions prises avant, les rappels, un exemple
   chiffré à rejouer.
2. Les pensions prises avant 2003 et 2015 : la PMR de 2009, les points gratuits
   de 2003 et le complément de 2015 qu'elles ont reçus, puis leur relèvement de
   2023, que la loi doit depuis 1997 ; le point 5 de la note de l'étape.
3. Le complément revu ensuite : chaque année, à 85 % en novembre 2021, quand
   les pensions changent ; la réversion des points relevés.
4. Les conjoints et les aides familiaux (L. 732-56, V et VI).
