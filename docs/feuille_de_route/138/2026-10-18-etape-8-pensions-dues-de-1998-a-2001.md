# Étape 8, douzième partie : les points des conjoints des pensions dues de 1998 à 2001

**Le 18 octobre 2026, la demande.** Le premier reste de l'étape, dans l'ordre
du bloc « Reprise » : « des conjoints, les pensions dues de 1998 à 2001 »
(point 1 de « Ce qui reste » de la note « points des conjoints »). Le modèle ne
servait aux années de conjoint des pensions prises de 1998 à 2001 que les plans
dus depuis 2002. Session de la vague 2b du 17-18 octobre, sur le modèle.

**Ce que dit le droit** (journal de veille du 18 octobre ; index JORF, aux
incréments du 18 octobre).

- *1998 et 1999* (décret n° 99-875, articles 1er à 4) : aux pensions prises
  depuis 1998, à trente-deux ans et demi d'activité agricole, sans réversion,
  chaque année de conjoint ou d'aide familial d'avant 1999 qui ne porte aucun
  point reçoit 8,63 points en 1998 ; en 1999, 11,44 au conjoint, 16 à l'aide
  familial ; minorés de 15, 15, 10, 10, 10 et 40 % par année manquante sous
  trente-sept et demie ; chef d'abord, trente-sept et demie au plus.
- *2000* (décret n° 2000-261, article 5) : 16 points par année de conjoint aux
  pensions prises en 1998 et 1999, l'année 1999 comptée à qui est parti cette
  année-là, 19,2 à l'aide familial ; aux pensions prises en 2000, 16, ou 8,63 à
  qui est resté conjoint participant aux travaux sans opter, le total diminué
  de seize. Vingt-sept ans et demi suffisent à qui a quinze ans de conjoint sans
  autre pension, et aucun coefficient ne joue au-delà de la cinquième année
  manquante.
- *2001* (décret n° 2001-170, article 5) : seize points par année de conjoint
  d'avant 1999 et un différentiel de 3,2, le différentiel seul aux années de
  conjoint collaborateur depuis 1999 ; les années d'avant 1999 diminuées de
  l'écart entre l'année d'effet et 1999, retenues dans la limite de trente-sept
  et demie moins l'écart avec 1998 : la règle de 2002 (D. 732-119 à D. 732-123),
  où B vaudrait 19,2.

**Ce qui est fait**, dans les deux moteurs.

- *La fiche* `majoration_retraite_proportionnelle` : un paramètre `conjoints`
  dans les versions de 1998 à 2001, le nombre de points du décret
  (`minimum_points`) et ses conditions ; six articles du JORF cités de plus.
- *`majoration_retraite_proportionnelle`* (`majorationRetraiteProportionnelle`)
  lit ce nombre quand la version en nomme un, B sinon ;
  `_points_des_conjoints` (`pointsDesConjoints`) en retranche, comme depuis
  2002, les seize points que porte chaque année.
- *Les tests* (`test_minima_agricoles.py`, un de plus, un cas de plus dans la
  comparaison des deux moteurs) : trente-cinq ans et demi de conjointe, partie
  en juillet 1998, rien de 1998 à 2000, 3,2 points par année en 2001, minorés de
  30 % ; trente et un ans, partie en février 2000, aux vingt-sept ans et demi,
  minorés de 60 %, ses années d'avant 1999 moins une.

**Les mesures.** Trente-cinq ans et demi de conjointe, partie en 1998 : 80
points en 2001, 245 € par an, avant les 207 de 2002. Quarante-trois ans,
partie en 2001 : 120 points dès la liquidation, 370 € par an. Aucun témoin de
simulation ne bouge.

**Ce que la vérification a trouvé.**

- *Les seize points d'une année de conjoint d'avant 1999*, que la loi ne dote
  d'aucun (écart déjà déclaré), dépassent les 8,63 et 11,44 points de 1998 et de
  1999, égalent les 16 de 2000 : rien ne s'y ajoute, et le modèle sert 7,37
  points de trop par année revalorisée en 1998, 4,56 en 1999. Le statut du
  modèle confond le conjoint, sans points avant 1999, et l'aide familial, qui en
  cotise depuis 1994 et dont les années d'avant reçoivent des plans 8,63, 16,
  puis 19,2 points (décret n° 2001-170, article 5, e : « soit par cotisation,
  soit par attribution gratuite »). Déclaré dans la fiche ; la question est au
  propriétaire.
- *L'aide familial* reçoit 16 points en 1999, 19,2 en 2000 : le modèle le sert
  comme un conjoint, et lui laisse 3,2 points de moins en 2000.
- *Le c) de 2001* minore les points de seize par année d'écart avec 1999 ; le
  modèle retire l'année, comme D. 732-123 depuis 2002, et son différentiel avec
  elle.

**Ce qui reste**, de l'étape, dans l'ordre du bloc « Reprise » :

1. Les restes d'avant, inchangés : un montant de la MSA pour 2015 à 2017 et
   2019 ; le 2° de D. 732-110, II (décès du conjoint, à saisir) ; la PMR revue
   quand les ressources changent ; la durée de chef reconstituée dans la PMR
   d'avant 1997 (D. 732-110, III) ; les points 2 et 3 de « Ce qui reste » de la
   note « points des conjoints ».
2. Au propriétaire : les seize points d'une année de conjoint d'avant 1999. Les
   ôter, comme la loi le veut du conjoint, ferait servir sur zéro les nombres de
   1998 à 2000 et B depuis 2002, mais retirerait seize points par an à l'aide
   familial, que le même statut couvre, et aux pensions prises depuis 2009 ; les
   garder laisse l'écart déclaré. Une présomption à choisir, conjoint ou aide
   familial, ou un champ de saisie qui les distingue.
