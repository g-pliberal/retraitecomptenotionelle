# Étape 17, douzième partie : les primes que la loi assujettit à la retenue pour pension

**Le 10 octobre 2026, la demande.** Trois primes trouvées en route, par la
première partie de l'étape (« Hors liste ») et par l'étape 9 : l'indemnité de
sujétions spéciales des policiers, dans l'assiette de leur pension et de leur
retenue (loi n° 57-444, article 6 bis) ; la prime spéciale de sujétion des
aides-soignants et l'indemnité de feu des sapeurs-pompiers professionnels,
soumises à une cotisation supplémentaire à la CNRACL et comptées dans la
pension. Les lire aux textes, les porter au scénario 1 dans les deux moteurs, et
mesurer sur les cas types 8 (policier) et 9 (aide-soignante) du COR, que
TRAJECTOiRE porte avec ces primes (`primes_dans_la_base`), et sur l'écart déclaré
de l'aide-soignante (`ECARTS_REMPLACEMENT_NET`), qui devait se refermer. Les deux
questions posées au propriétaire — ce que la saisie dit de la part de primes, les
statuts qui couvrent plusieurs corps — ont été renvoyées au droit.

**Ce que dit le droit, lu le jour même** (journal de veille du 10 octobre ;
fiches `indemnite_sujetions_speciales_police`, `indemnite_de_feu_sapeurs_pompiers`
et `prime_speciale_sujetion_aides_soignants` ; leur table, année par année,
`legislation/primes_soumises_a_retenue.yaml`).

- *Le policier des services actifs* : depuis le 1er janvier 1983, l'indemnité
  entre au calcul de la pension et des retenues, « un dixième par an » jusqu'en
  1992 (décret du 15 mai 1983, non publié ; réponse ministérielle du 17 janvier
  1991), au taux du corps d'encadrement et d'application, de 20 % en 1983 à
  28,5 % depuis 2020. Elle majore le traitement que la pension liquide, sans
  condition ni prorata. La retenue compte 1 % de plus depuis 1957 (article 3),
  0,5, 1 puis 1,2 % depuis 1983 (article 6 bis) : 12,76 % en 2018, sur le
  traitement et l'indemnité (annexe au projet de loi de finances).
- *Le sapeur-pompier professionnel* : depuis le 1er janvier 1991, l'indemnité de
  feu, 19 % puis 25 % depuis le 26 juillet 2020, deux quinzièmes puis un
  quinzième par an jusqu'en 2003. Elle majore le traitement, « proratisée sur les
  seules années de service accomplies en cette qualité », pour quinze puis
  dix-sept ans de services, la jouissance différée jusqu'à l'âge ; sans prorata
  depuis le 2 janvier 2025, quand les services du sapeur-pompier et sa
  bonification atteignent seuls le pourcentage maximum. Les cotisations
  supplémentaires de l'intégration, de 0,6 à 1,8 % pour l'agent et de 1,2 à 3,6 %
  pour l'employeur, ont cessé en 2021 pour l'employeur et en 2022 pour l'agent ;
  la retenue de 2 % de la bonification du cinquième demeure, sur le traitement
  et l'indemnité depuis 1991.
- *L'aide-soignant de la fonction publique hospitalière* : depuis le 1er janvier
  2004, la prime spéciale de sujétion, dans la limite de 10 % du traitement, paie
  la retenue ordinaire, 1,5 % de retenue et 3,5 % de contribution de plus, et
  ouvre un supplément de pension : la prime des six derniers mois, à 20 % en 2004,
  100 % depuis 2008, au prorata des services d'aide-soignant pour qui est entré
  dans le corps depuis 2004, après quinze puis dix-sept ans de services
  hospitaliers, versé à partir de l'âge. La CNRACL l'ajoute après la décote, et
  sa formule ne le multiplie par aucun pourcentage de la pension.
- *Le RAFP* plafonne les autres primes à 20 % du « traitement indiciaire brut
  total perçu au cours de l'année » (décret n° 2004-569, article 2) : du
  traitement seul, sans la prime soumise.

**Ce qui est décidé, et pourquoi.**

- *Aucun champ de saisie.* La part de primes que la saisie demande reste
  l'assiette du RAFP : les primes que la pension ne compte pas. La prime soumise
  est dans le reste, avec le traitement, dont elle se sépare au taux que la loi
  fixe pour l'année : traitement = reste / (1 + taux × part comptée). Il n'y a
  rien à demander de plus à l'assuré.
- *Deux statuts naissent*, parce que la loi ne nomme qu'un corps : `policier`
  (services actifs de police, super-actif) et `aide_soignant` (le corps des
  aides-soignants, actif). Le statut super-actif de l'État garde les surveillants
  pénitentiaires, dont la prime de 1986 n'est pas lue ; le statut hospitalier
  actif, les autres agents de catégorie active, sans prime. Le sapeur-pompier
  professionnel avait le sien depuis le 7 octobre.
- *La jouissance, que la loi diffère jusqu'à l'âge, court dès la date d'effet.*
  La loi diffère la majoration et le supplément, elle ne les retire pas ; le
  dépôt ne sait pas différer une part de pension. Une première régénération, qui
  les refusait avant l'âge, ôtait à la valorisation des droits acquis à la
  bascule, une liquidation fictive à cinquante et un ans, la majoration des trente
  ans de services sur lesquels le sapeur-pompier né en 1975 a cotisé : son
  scénario 3 perdait 17,7 %.

**Ce qui est fait.**

- *Les données* : la table année par année — taux, intégration, retenues et
  contributions supplémentaires et leurs assiettes — ; trois fiches datées, neuf
  versions ; les deux statuts, dans les affiliations, les fiches des régimes, des
  bonifications et de la majoration des hospitaliers actifs, et l'inventaire.
- *Le modèle, dans les deux moteurs* : la fiche de paie et le compte notionnel
  prélèvent les retenues et contributions supplémentaires
  (`PrimesSoumises.taux_supplementaires`, `bloc_droit_en_vigueur`,
  `moteur/compte.py`) ; le RAFP plafonne au traitement seul
  (`PeriodeRegime.part_du_revenu`) ; la liquidation prend le traitement seul,
  que la prime de la date d'effet majore, ou dont elle tire le supplément
  (`droit/primes.py`), que l'étape qui complète ajoute après le minimum garanti
  et les majorations.
- *TRAJECTOiRE* : le policier du cas 8 au statut `policier`, l'aide-soignante du
  cas 9 au statut `aide_soignant` (`scripts/fetch/trajectoire.py`, son témoin).
- *Les tests* : `test_primes_soumises_a_retenue.py`, dix-huit cas — la table, le
  partage, le plafond du RAFP, les trois retenues, les pensions, l'intégration,
  le prorata, les conditions, les droits acquis —, dont trois des quatre exemples
  de la CNRACL sur l'indemnité de feu : le premier et le quatrième au centime,
  1 961,41 € par mois, le deuxième au prorata près, sa carrière tenant en années
  entières ; le troisième est celui de l'ancien sapeur-pompier, que le dépôt ne
  suit pas. Quatorze témoins neufs, les deux statuts à chaque génération, que le
  jumeau rejoue.

**Les mesures.**

- *Le policier du cas 8* : sa pension ne bouge pas, l'un et l'autre liquidant
  déjà le traitement majoré de l'indemnité. Son net perd les 2,2 points de
  retenue supplémentaire que TRAJECTOiRE ne prélève pas : son taux de
  remplacement net, à 0,985 à 0,997 fois le sien depuis l'étape 9, passe à
  1,016 à 1,022 ; déclaré.
- *L'aide-soignante du cas 9* : sa pension passe celle de TRAJECTOiRE de 3,2 %
  (génération 1955), 4,8 % (1960), 6,8 % (1963, que le minimum garanti prend
  avant le supplément) et 0,9 % (1964, avec la durée des actifs) : le dépôt sert
  la prime en supplément, hors du pourcentage, quand TRAJECTOiRE la range dans le
  traitement, sous le pourcentage et la décote ; son traitement de référence est
  plus bas de 8,6 à 10 %.
- *Son écart déclaré ne se referme pas.* La retenue de 1,5 % de la prime ne
  déplace le rapport des taux de remplacement nets que d'un millième, de 0,945 à
  0,985 fois à 0,946 à 0,986. L'écart est celui de TRAJECTOiRE, qui prélève la
  retenue de la prime, ordinaire et supplémentaire, sur les AUTRES primes de
  l'aide-soignante, « partIS*primes*(txCotFP_sal + txSurcotIS_sal) », quand son
  script des cas types range déjà la prime avec le traitement, qui paie la
  retenue ordinaire. La cause déclarée est réécrite.
- *Le RAFP* baisse, le plafond étant pris sur le traitement seul quand
  TRAJECTOiRE le prend sur sa rémunération, prime comprise : 21 à 47 % de points
  de moins pour le policier, 11 à 14 % pour l'aide-soignante ; déclaré.
- *Les témoins* : au scénario 1, aucune pension ne bouge sur 785 ; le
  sapeur-pompier de toute une carrière liquide, majoré de l'indemnité, le
  traitement qu'il liquidait déjà, l'indemnité comprise. Aux scénarios 2, 4 et 6,
  ses sept témoins montent, de 2 à 37 %, de 27 % en médiane au scénario 2 : les
  retenues et contributions supplémentaires qu'il a payées entrent à son compte
  notionnel. Les scénarios 3 et 5 ne bougent pas, depuis que la majoration court
  dès la date d'effet. Les pages ne changent que par les deux statuts du
  formulaire et le libellé des deux autres.

**Ce qui reste.**

1. *L'ancien sapeur-pompier*, que la majoration suit depuis 2021 sur le
   traitement de son dernier grade de sapeur-pompier, et le sapeur-pompier
   reclassé pour raison opérationnelle (le troisième exemple de la CNRACL) : il
   faudrait garder ce traitement et ce taux à la sortie du statut.
2. *La jouissance différée* de la majoration et du supplément, jusqu'à l'âge de
   la catégorie active, pour la pension prise plus tôt.
3. *La montée de quinze à dix-sept ans* de services, de 2011 à 2015, que la
   CNRACL écrit pour l'un et l'autre.
4. *Le supplément de l'aide-soignant* : un titre de pension de la CNRACL qui dise
   s'il passe sous le pourcentage ; son âge depuis la loi du 14 avril 2023 ; la
   nouvelle bonification indiciaire, comptée dans la prime.
5. *Les primes sans statut* : la prime de sujétions spéciales des surveillants
   pénitentiaires (loi de finances pour 1986, article 76), l'indemnité des
   gendarmes, celle des personnels administratifs et techniques de la police
   depuis 2023 ; les taux de l'indemnité des policiers avant 1997.
6. *La mesure de la catégorie active* (`avantages.py`, `SEDENTAIRE`) rejoue le
   policier, l'aide-soignant et le sapeur-pompier en sédentaires, sans la prime
   soumise ni ses retenues : leur avantage la compte, pour peu.
