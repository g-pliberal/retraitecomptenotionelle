# La baisse des pensions avant l'intégration : les complémentaires que l'État règle, et l'ordre refait

**Reprise, au 7 novembre 2026.** L'étape 1 bis est faite : les complémentaires
que l'État règle baissent dès la bascule, par cinquièmes, les seules pensions
déjà servies (décisions 86 et 87), au taux que le coût du scénario 6 donne à
leur cas type, ou à l'ensemble. L'ordre : complémentaire agricole 2026,
Agirc-Arrco 2032, CNBF 2049 ; l'Ircantec, le RCI, les libéraux et les navigants
au-delà de 2070. Restent au propriétaire la hausse des libéraux et le
calendrier de la page Coût (« Ce qui reste au propriétaire »). La suite, l'étape
2, le moteur d'une carrière, s'ouvre dans une session neuve ; le plan est dans
`186/2026-11-07-complementaires-au-modele.md`.

*Le 7 novembre 2026, une session du modèle mène l'étape 1 bis du portage des
décisions du chantier 6 : la baisse que les décisions 2, 3 et 43 imposent dès
la bascule aux complémentaires dont l'État fixe les pensions, intégrées ou
non, que la projection de l'étape 1 ne faisait pas. Elle a lu le coût agrégé
du scénario 6 (`cout.py`, `memoire.cout`), sa grille de cas types et la note
des deux lectures de la décision 29. Le propriétaire a tranché en cours
d'étape les deux questions que les décisions laissaient ouvertes.*

## L'essentiel : de combien chaque caisse baisse, et quand elle rejoint le régime général

| Caisse | Ses pensions servies à la bascule | Lue sur | Intégration sans la baisse | Avec |
|---|---:|---|---:|---:|
| Complémentaire des exploitants agricoles (RCO) | − 44,9 % | le chef d'exploitation agricole | 2026 | **2026** |
| Agirc-Arrco | rien (décision 43) | — | 2032 | **2032** |
| Complémentaire des avocats (CNBF) | − 26,9 % | l'ensemble | 2042 | **2049** |
| Ircantec | − 30,6 % | le contractuel du public | 2055 | **après 2070** (8,9 Md€) |
| Complémentaire des indépendants (RCI) | − 21,0 % | l'artisan | après 2070 (8,7) | **après 2070** (30,9) |
| Sections complémentaires des libéraux | **+ 13,6 %** | le libéral (Cipav) | après 2070 (62,0) | **après 2070** (49,2) |
| Personnel navigant (CRPNPAC) | − 26,9 % | l'ensemble | après 2070 (14,3) | **après 2070** (20,0) |

Entre parenthèses, les réserves de fin 2070, en milliards d'euros de 2025.
Sources : le coût agrégé du scénario 6 et la projection de l'étape 1, à côté
(`integration_complementaires.py`, `baisses_du_modele`, et ses deux fichiers
de tests).

La baisse se fait par cinquièmes : un cinquième en 2026, la baisse entière en
2030. Elle ne touche que les pensions servies à la bascule ; celles qu'une
caisse liquide ensuite, à ses règles, jusqu'à son intégration, ne baissent pas.
Ce stock s'éteint : il fait toute la dépense de l'Ircantec en 2026, 89 % en
2030, 47 % en 2040, 16 % en 2050. L'économie la plus forte tombe donc en 2030 :
1,4 Md€ pour l'Ircantec, 0,5 pour le RCI, 0,1 pour la CNBF.

**L'Ircantec** ne s'épuise plus : ses réserves montent à 51 Md€ en 2050, puis
redescendent, 8,9 Md€ en 2070 pour un déficit de près de 3 Md€ par an. Elle
rejoindrait le régime général vers 2073, juste après l'horizon du modèle.
**La CNBF** gagne sept ans. **La complémentaire agricole** n'en gagne aucun : en
2026, un cinquième de sa baisse lui rend 0,09 Md€, quand il lui en manque
0,12.

## Ce que le propriétaire a tranché

Le même jour, sur deux questions que la décision 43 ne réglait pas (chacune
posée avec ce qu'elle changeait à l'ordre) :

1. **Les seules pensions déjà servies** : « Déjà versées seules ». La baisse
   suit la lettre de la décision 2 (« les pensions des retraités actuels
   baissent ») ; une caisse sert ses nouvelles pensions à ses règles jusqu'à
   son intégration (décision 86).
2. **Par cinquièmes** : « Par cinquièmes ». La décision 3 dit « en cinq ans au
   plus » ; la piste du chantier 2, une convergence par cinquièmes (décision
   87). La page Coût, elle, fait la baisse d'un coup, dès 2026.

**Une correction à ce qui lui a été montré.** Les années posées avec la
question venaient d'une projection qui portait encore le défaut décrit plus
bas : la CNBF y tombait vers 2058 sous la lecture retenue, et jamais avant
2070 si toutes ses pensions baissaient. Refaites, les quatre combinaisons :

| | Par cinquièmes | D'un coup |
|---|---|---|
| Les pensions déjà servies | RCO 2026, Agirc-Arrco 2032, **CNBF 2049** | RCO 2029, Agirc-Arrco 2032, CNBF 2050 |
| Toutes, jusqu'à l'intégration | RCO 2026, Agirc-Arrco 2032, CNBF 2053 | Agirc-Arrco 2032, RCO 2034, CNBF 2054 |

Les autres caisses tiennent au-delà de 2070 dans les quatre. Le choix du
propriétaire reste celui qui recule le moins les intégrations.

## La méthode

**Le taux de la baisse** (`baisses_du_modele`, à côté). Le coût agrégé
compare, chaque année, la masse des droits directs du scénario 6 à celle du
droit en vigueur (`AvenirAnnuel.rapports`). L'année de la bascule, presque
toute cette masse est le stock, et son rapport dit ce que le scénario 6 lui
retire. La baisse de la dépense d'une caisse est un moins ce rapport,
multiplié par la part directe de la dépense, 89,8 % en 2026 (le COR) : les
réversions servies à la bascule sont gardées (décision 16). La garantie
vieillesse n'y entre pas : le régime général la paie, non la caisse. Pour
l'ensemble, 1 − 0,701 = 29,9 % des droits directs, 26,9 % de la dépense ; la
page Coût en tire les 104 Md€ que perdent les retraités d'aujourd'hui en 2026
(433,0 Md€ au droit en vigueur, 315,4 au scénario 6, plus 14,1 de garantie),
que la note des deux lectures de la décision 29 cite. Ni la lecture A ni la
lecture B ne change ce chiffre : elles ne se séparent que sur l'usage de
l'économie (même note, « Ce qui est commun aux trois ») ; aucune n'est
tranchée.

**Caisse par caisse.** Le coût sait se calculer sur une grille réduite à un
seul cas type (`memoire.cout(cas_types=…)`) : quelques secondes chacun. Le
contractuel du public donne l'Ircantec, l'artisan le RCI, le libéral les
sections des libéraux, le chef d'exploitation la RCO. La grille n'a ni avocat
ni navigant : la CNBF et la CRPNPAC prennent l'ensemble. La baisse d'un cas
type vaut pour toute la pension de ses retraités ; la complémentaire en
prend autant, en proportion de ce qu'elle sert.

**La part du stock**, année par année, vient du même calcul
(`AvenirAnnuel.part_stock` : la masse des pensions liquidées au plus tard
l'année de la bascule, sur celle du droit en vigueur). Elle passe un peu
au-dessus de un en 2028 pour le contractuel et l'artisan (1,0006), le stock
y étant revalorisé aux prix, la masse du droit en vigueur à la valeur de
service de chaque régime : bornée à un.

**Dans la projection**, l'économie de l'année — l'avancement du calendrier,
le taux, la part du stock, la dépense du COR — sort des dépenses et
s'ajoute à l'écart de réserves, qui croît ensuite comme lui. Le test d'abord :
la complémentaire agricole sous une baisse posée à la main, 40 %, calculée à
la main en 2026 (− 0,037 Md€ par cinquièmes, + 0,310 d'un coup) ; puis la
baisse du modèle, l'Agirc-Arrco et la RCO inchangées.

## Un défaut corrigé en chemin

La règle du classeur du COR fait des réserves d'une année celles de la
précédente, multipliées par un facteur, plus le solde élargi ; la projection
tire ce facteur du classeur, et l'applique à l'écart que les décisions
creusent. Près de l'épuisement, le classeur s'écarte de sa règle : les
réserves de la CNBF font 0,688 Md€ fin 2043 et son solde − 0,485 Md€ en
2044, soit 0,203 Md€ attendus fin 2044, quand le classeur en écrit 0,411. Le
facteur en sortait à 1,30, puis 1,97 et 2,60 jusqu'en 2046, et multipliait
l'écart par près de sept ; celui de l'Ircantec, de 1,05 à 1,14 de 2049 à 2052.
Les autres caisses n'ont pas d'écart semblable. Un facteur au-delà du
rendement maximal que la projection prête aux réserves, 5 %, vaut désormais
un. Sans la baisse, aucune année ne bouge : la CNBF tombait avant 2044.
Avec, la CNBF passe de 2058 à 2049, et l'Ircantec finit 2070 avec 8,9 Md€ au
lieu de 28.

## Ce que cela change pour les assurés

- **Les contractuels du public** : la part Ircantec de leur pension baisse de
  31 % en cinq ans, s'ils sont à la retraite à la bascule. Ceux qui partent
  ensuite touchent leur Ircantec à ses règles. L'Ircantec reste à part tout
  l'horizon : ses cotisants la paient en plus des 18 % jusqu'en 2070 au moins
  (décision 70).
- **Les avocats** : leur complémentaire baisse de 27 %, et rejoint le régime
  général en 2049 au lieu de 2042 ; ils versent sa cotisation sept ans de
  plus.
- **Les indépendants** : − 21 % sur leur complémentaire servie ; elle reste à
  part au-delà de 2070, comme avant.
- **Les libéraux** : le modèle ne les baisse pas, il les relève, de 13,6 %
  pour le libéral de la Cipav. Au départ, la page Cas types ne le relève que
  pour la génération 1940 (+ 19 %), et le baisse de 6 et 10 % pour 1950 et
  1960 ; à la bascule, le coût relève ses droits directs de 15 % : la
  revalorisation des deux systèmes, entre le départ et 2026, seule à changer
  d'une date à l'autre, a creusé l'écart. Leurs sections paient la hausse, et
  tiennent quand même au-delà de 2070 (49 Md€).
- **Les navigants** : − 27 % ; leur caisse reste à part au-delà de 2070.
- **Les exploitants agricoles** : − 45 % sur la RCO servie ; elle rejoint le
  régime général dès 2026, comme avant.
- **Les salariés du privé** : rien ne change ; l'Agirc-Arrco garde ses
  pensions (décision 43) et tombe en 2032.

## Ce que la note n'a pas établi

- Le taux d'une caisse est celui d'un seul cas type de la grille du coût : un
  contractuel, un artisan, un libéral de la Cipav, un chef d'exploitation. Les
  avocats et les navigants n'en ont pas, et prennent l'ensemble, que tirent
  les fonctionnaires et les régimes spéciaux ; le libéral de la grille ne dit
  rien des neuf autres sections.
- La complémentaire baisse dans la proportion de toute la pension : le
  compte notionnel ne sépare pas la base de la complémentaire.
- La part du stock est celle du cas type, non la démographie de la caisse.
- La page Coût fait la baisse d'un coup, la projection par cinquièmes
  (décision 87) : les deux ne disent pas la même année 2026.
- L'Ircantec ne tient au-delà de 2070 que de trois ans environ.

## Ce qui reste au propriétaire

1. **Les libéraux, dont la pension monte** : le recalcul au compte notionnel
   relève certaines pensions servies (+ 13,6 % pour le libéral de la Cipav).
   Le scénario 6 les relève-t-il, comme le coût le fait, ou ne fait-il que
   baisser ? Et qui paie la hausse : leur section, comme la projection le
   fait, ou le régime unique ? L'ordre ne bouge pas.
2. **La page Coût par cinquièmes** : la baisse du stock s'y fait d'un coup ;
   la décision 87 la fait par cinquièmes pour les complémentaires. L'étendre à
   tout le stock rejoint la question du plafond de baisse par an (chantier 2).
