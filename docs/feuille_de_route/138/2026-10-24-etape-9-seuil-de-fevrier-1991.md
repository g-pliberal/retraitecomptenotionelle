# Étape 9, suite de la huitième partie : le seuil de la contribution de solidarité de février 1991 à 1997, lu à la chaîne des barèmes A

**La demande.** Lot du 24 octobre 2026 : onze sessions en parallèle, une
tâche chacune, que le propriétaire ne suit pas pas à pas. Celle-ci, action
138, étape 9 (la maladie des régimes spéciaux) : le point 1 de « Ce qui
reste » de la note « seuil de solidarité » du 23 octobre — le seuil de
février 1991, que l'IPP passe sans référence de l'indice 254 à 259, à lire
comme 1988-1989, sur la règle et les décrets de 1990 et 1991. Règle du
scénario 1 ; ni les pages, ni la saisie ; les décrets au fac-similé restent
au propriétaire.

**Ce que disent les textes, lus le jour même dans les index JORF et LEGI,
récupérés puis mis à jour de leurs incréments (JORF au 24 octobre, LEGI au
23).**

- *La règle* ne change pas de 1987 à 1997 : le « traitement annuel net
  afférent à l'indice brut 259 » (loi n° 82-939, article 4,
  LEGIARTI000006656113, seule version de LEGI du 31 décembre 1986 au
  30 décembre 1997).
- *Un barème A vaut jusqu'au suivant.* Le décret qui annexe un barème A au
  décret n° 82-1105 récrit aussi la date que dit son article 1er : le décret
  n° 90-321 y remplace « à compter du 1er février 1989 » par « à compter du
  1er janvier 1990 » (JORFARTI000002140012), le décret n° 91-1191 ces mots
  par « à compter du 1er août 1991 » (JORFARTI000000991073), le décret
  n° 98-462 ceux-ci par « à compter du 1er juillet 1998 »
  (JORFARTI000001168959). En novembre 1991, l'article 1er disait donc encore
  le 1er janvier 1990 : aucun barème A en février 1991. Le décret n° 90-1058
  (1er décembre 1990) et ceux de 1992 à 1997 n'y touchent pas : ils fixent le
  point, et le premier relève le minimum de traitement de l'indice brut 209 au
  214 (article 8).
- *Les articles 7 à 9 du décret n° 85-1148* le confirment : de leurs versions
  du 1er janvier 1990 (du 1er décembre 1990 pour l'article 8) au 1er août
  1991, les indices bruts 100, 175, 214 et 308 restent aux indices majorés
  156, 200, 224 et 287 ; du 1er août 1991 au 20 février 1998, à 158, 202, 226
  et 289, deux points de plus (le supplément familial, à l'article 10, fait
  de même : l'indice brut 524 de 444 à 446). L'indice brut 259, lu à 254 en
  1990 par la session du 23 octobre, y reste donc jusqu'au 31 juillet 1991,
  puis passe à 256. C'est toujours une lecture de proche en proche : le
  barème A de chaque date, au fac-similé, la confirmerait. L'IPP lui-même la
  corrobore : en 1998, il met l'indice brut 296 à l'indice majoré 280, ce
  qui, avec 214 à 226 et 308 à 289, va avec 256 pour le 259, non avec 261.
- *Le point de chaque marche* (article 3 du décret n° 85-1148) est celui de
  l'IPP, aux décrets qui le fixent, lus dans l'index : 29 118 F et 29 408 F
  (n° 91-1191), 29 784 F (n° 92-107), 30 190 F (n° 92-993), 30 711 F
  (n° 93-93), 31 422 F (n° 94-1004), 31 799 F (n° 95-167), 32 244 F
  (n° 95-1099), 32 405 F (n° 97-141), 32 567 F (n° 97-877). En 1994, deux
  points : 30 926 F et 31 080 F, et, « pour les agents dont l'indice majoré
  est inférieur ou égal à 275 », 31 018 F au 1er janvier (LEGI,
  LEGIARTI000006454438 : le décret n° 93-1317 n'est pas dans l'index) et
  31 173 F au 1er août (n° 94-599) ; l'indice 256 prend le second, comme
  l'IPP. Celui-ci cite pour août et décembre 1994 les décrets n° 93-1317 et
  94-599, quand ce sont les n° 94-599 et 94-1004 qui les fixent.
- *Ce que le Fonds applique* : ni circulaire du Fonds de solidarité ni montant
  publié du seuil dans l'index de 1991 à 1997 ; le décret n° 82-1001 n'y a
  que son article 10, sur les petits employeurs.

**Ce qui est fait.**

- *Le seuil* (`scripts/fetch/ipp_prelevements_sociaux.py`) : deux tables,
  `BAREMES_A` — la date de chaque barème, l'indice majoré de l'indice brut
  259, l'article et les mots qui l'enchaînent — et `POINTS_DU_SEUIL` — la
  date, le point, le texte que la marche cite, l'article qui fixe le point et
  ses mots —, d'où se déduisent les corrections : la marche de février 1991
  disparaît, le seuil y restant à 934,91 € (73 591 F par an) ; les douze de
  1991 à 1997 prennent l'indice 256 au lieu de 261, de 946,99 € en août 1991
  à 1 059,16 € en octobre 1997, 1,9 % sous l'IPP. Elles s'ancrent au décret
  qui fixe leur point, celle de janvier 1994 à LEGI.
- *La garde des dates* (`dates_des_marches.py`) : les douze marches et celle
  de février 1991, qu'une correction écrit, en sortent ; la table du seuil
  garde leurs articles et leurs mots, qu'un test relit. 134 des 206 marches
  de l'IPP y ont leur date.
- *La donnée*, refaite sur les index mis à jour : 301 marches, 206 de l'IPP,
  149 ancrées, 134 datées ; l'index ne dément plus la date que de cinq
  décrets de l'IPP, non de six, le n° 93-93 ne datant plus une de ses
  marches ; son en-tête et la note de la source (`data/sources.yaml`) le
  disent. Les autres séries n'ont pas bougé.
- *Les tests* (`tests/test_prelevements_historiques.py`, deux de plus) : le
  seuil de janvier 1991 à décembre 1997, de part et d'autre de chaque marche,
  sur le traitement annuel posé à la main ; les mots de chaque barème A et de
  chaque point, relus dans l'index, avec le point et la date qu'ils disent,
  et l'ancrage de deux marches.
- *La classe, et non le cas* (`src/CLAUDE.md`) : de 1998 à 2017, l'indice
  majoré de référence de l'IPP ne change qu'à des dates où un barème A se
  substitue, ou, en mai 2001 et juillet 2009, où LEGI montre les indices
  bruts 100 et 244 bouger (décrets n° 2001-370 et 2009-824) : seule la date
  de février 1991 était sans texte. Les valeurs, elles, restent celles de
  l'IPP.

**Ce que montrent les mesures** (Python, prélèvements hors retraite d'un
agent de l'État, sa retenue pour pension à 7,85 %, avant et après) : à
6 250 F bruts par mois, 838,13 € en 1991 au lieu de 763,86 €, assujetti de
janvier à octobre et non en janvier seul ; à 6 650 F, 1 053,65 € en 1993 au
lieu de 957,63 € ; à 6 950 F, 1 210,90 € en 1997 au lieu de 1 099,78 €,
assujetti toute l'année, quand l'IPP l'exonérait. Rien ne change à 7 100 F
en 1997, ni en 1990, ni en 1998.

**Ce qui reste**, une session par point :

1. *Au fac-similé, depuis un poste* : le barème A du 1er janvier 1990 et du
   1er août 1991 (JO des 11 avril 1990 et 27 novembre 1991), qui dirait
   l'indice majoré de l'indice brut 259, avec ceux de 1988 et 1989 et les
   décrets de 1987 que demande déjà la note du 23 octobre. Au propriétaire.
2. *Inchangés* : le plafond de 2027 ; la date d'entrée dans la saisie en net,
   à une session des pages ; la limite 5 ante ter (2), en fin d'étape ; au
   propriétaire, la CAMIEG, l'écrêtement du minimum de la SNCF, l'ASPA de
   l'article 23.

**Pour la session des pages** : rien ; le format de la donnée ne change pas,
et GitHub refait le paquet.
