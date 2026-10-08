# Étape 17, septième partie : la bonification du cinquième des militaires

**Le 8 octobre 2026, la demande.** Le propriétaire : « 138.17 bonification du
cinquième des militaires ». C'était la première règle du reste de l'étape : le
dépôt ne servait aucune bonification de service aux militaires, quand le jaune
budgétaire en compte une à 98,4 % des militaires liquidants, et l'inventaire
des avantages la rangeait en « absent ».

**Ce que dit le droit, lu le jour même** (journal de veille du 8 octobre ;
fiche `bonification_cinquieme_militaires`).

- *Avant le i de L. 12*, la loi de finances pour 1972, article 53, que le
  rapport n° 6 du Sénat (1975-1976) cite en « législation actuellement en
  vigueur » : « une bonification égale à un cinquième du temps accompli », trois
  annuités au plus, à vingt-cinq ans de services militaires effectifs, aux
  militaires rayés des cadres de 1972 à 1980 dont la limite d'âge est inférieure
  à cinquante-huit ans et aux officiers de gendarmerie, officiers généraux
  exclus.
- *La loi n° 75-1000 du 30 octobre 1975* la rend permanente au i de L. 12 et
  abroge l'article 53. Son projet la réservait aux mêmes, cinq annuités, à quinze
  ans de services ; le texte voté n'est pas dans l'index, qui garde L. 12 depuis
  sa rédaction du 14 juillet 1982 : « à tous les militaires », quinze ans de
  services, « le maximum de bonifications est donné aux militaires qui quittent
  le service à cinquante-cinq ans ; la bonification est diminuée d'une annuité
  pour chaque année supplémentaire de service jusqu'à l'âge de cinquante-huit
  ans ». Le rapport d'information du Sénat n° 236 (2007-2008) date cette
  dégressivité de la création, en 1975.
- *Les réformes* : la loi de 2003 porte ces âges à cinquante-sept et soixante, et
  écrit que les bonifications de L. 12 portent le pourcentage à 80 % — L. 14 le
  disait déjà, « quarante annuités du chef des bonifications prévues à l'article
  L. 12 » ; celle de 2010, à dix-sept ans de services, cinquante-neuf ans et
  « l'âge mentionné à l'article L. 161-17-2 », pour les pensions prenant effet
  depuis le 1er juillet 2011, sans montée en charge ; celle de 2023 supprime la
  dégressivité, l'accorde aux « anciens militaires », et la borne à vingt
  trimestres avec les bonifications des emplois classés, au 1er septembre 2023.
- *Comment la caisse l'applique.* Le service des retraites de l'État, en 2021 :
  « Elle peut être écrêtée (1 an par année de service au-delà de 60 ans). Aucune
  bonification du 1/5ème n'est accordée au delà de 62 ans, sauf si la limite
  d'âge de l'emploi est fixée à 62 ans et si le militaire est radié des cadres
  par limite d'âge le lendemain de ses 62 ans. Dans un tel cas, la bonification
  maximale est de 2 ans. » La réduction se compte donc par années entières, et
  rien n'est dû au-delà de l'âge final — le Sénat le dit de 1975 : « Au-delà de
  58 ans tous les avantages conférés par cette bonification étaient totalement
  annulés ». Depuis 2023, elle « est également accordée aux agents qui ne sont
  plus militaires au moment où ils liquident leur pension » : avant, à eux seuls.
- *Le minimum garanti d'avant 2004* compte « par année de services effectifs et
  de bonifications prévues à l'article L. 12 » (L. 17, b) : la bonification y
  entre.

**Ce qui est fait.**

- *La fiche*, sept versions, lue par les deux moteurs à la date d'effet comme
  celles des emplois classés : rien avant 1972 ; la loi de finances pour 1972 ;
  la loi de 1975, supposée, à qui le dépôt prête la règle de la rédaction de
  1982 ; les rédactions de 1982, 2004, 2011 et 2023. Elle porte le pourcentage
  au-delà de 75 %, sauf la version de 1972, qui n'est pas de L. 12.
- *Le modèle* (`droit/compter.py`, son jumeau) : la condition
  `duree_dans_l_emploi`, les années servies dans les statuts militaires, et,
  jusqu'en août 2023, la dernière année des services du code des pensions servie
  dans l'un d'eux ; `age_de_suppression`, un âge ou l'âge légal de la
  génération ; `reduction_par_annee_entiere`. Les services accomplis au-delà d'un
  âge se comptent au mois, depuis le premier mois vécu entier à cet âge
  (`Carriere.duree_de_service_avant`, son jumeau) — pour les policiers aussi, qui
  les comptaient à l'année : le policier né en janvier 1953 et parti en janvier
  2013, trois ans au-delà de cinquante-sept, gardait douze trimestres, il en
  garde huit. La fiche vient après celles des emplois classés, que la limite de
  vingt trimestres sert d'abord, et avant la majoration des hospitaliers.
- *L'exemple* `sre_militaire_radie_le_lendemain_de_ses_62_ans`, que le modèle
  rejoue : deux ans de bonification à l'officier né en juin 1955, radié le 16 juin
  2017.
- *Le coût* : la neutralisation `bonification_cinquieme_militaires`, à part de
  celle des emplois classés, dans les deux moteurs ; l'inventaire range la ligne
  en « intégré », la frontière contributive en « appliqué » ses trois bascules ;
  la fiche du régime et celle de la durée requise des militaires ne la disent
  plus absente.
- *Les tests* : sept dans `test_bonifications_emplois.py`, l'exemple dans
  `test_oracle.py`, la neutralisation dans `test_avantages.py` ; le minimum
  garanti du militaire liquidé en 2000 passe de 68 à 82 % de la référence
  (`test_departs.py`), ses dix-sept ans et trois ans et demi de bonification.

**Les mesures.** Le cas type militaire de la grille, sous-officier engagé à
dix-neuf ans et radié à quarante-quatre, reçoit vingt trimestres : sa pension
monte de 20 % à partir de la génération 1970, de 14 % pour celle de 1965, et
reste au minimum garanti, qu'elle atteint avec ou sans bonification, avant. Le
jaune budgétaire donne, sur les liquidations de 2023, 16,4 trimestres en
moyenne, pour des services plus courts que ses vingt-cinq ans. Retirée, la
fiche ôte 0,43 Md€ à la dépense de 2024 que la grille reconstitue ; les 146 €
de gain mensuel que le jaune publie sur le flux de 2023, s'ils valaient pour
les quelque 400 000 pensions militaires du stock, feraient de l'ordre de
0,7 Md€ — un ordre de grandeur, le gain du stock n'étant pas publié. Onze
témoins bougent au scénario 1, tous militaires et tous à la hausse : +20 % au
sous-officier de vingt-cinq ans de services, +6,67 % aux carrières militaires
complètes liquidées depuis 2023, portées de 75 à 80 % ; celles d'avant 2023,
servies au-delà de l'âge final, n'ont rien. Le portage concorde sur les 763
témoins, et au bit près sur treize carrières de 1930 à 1980 tirées pour la
règle.

Sur les pages : le militaire non officier reste la carrière que la
proposition traite le mieux, mais à +40 % pour la génération 2000, non +69 %,
à 75 points de la carrière interrompue ; l'avantage que le modèle chiffre
passe de 97,9 à 97,6 Md€ pour vingt-deux dispositifs, la bonification
ajoutant 0,43 Md€ quand le complément du minimum garanti tombe de 1,26 à
0,56 Md€ — la pension militaire des générations qu'il relevait l'atteint
désormais par la bonification —, les pensions servies avant l'âge légal de
11,0 à 11,4 Md€ ; la dette de la
proposition en 2070, de 60 à 58 % du PIB, son coefficient de 2070 de 1,00 à
1,01 (`MESURES_BLOCAGES`, le parcours de présentation). À l'horizon, la
pension relative de la fonction publique d'État s'écarte du COR de +1,0 à
+4,2 %, sa dépense de +15,8 à +19,2 % : les deux cliquets remontent
(`test_cout.py`), la règle étant le droit et le cas type en recevant le
plafond. Le test des formules affichées lit désormais le taux maximum de 80 %,
qu'aucune carrière du balayage n'atteignait.

**Ce qui reste.**

1. *La loi de 1975 votée*, et sa date d'effet : la version de 1975 à 1982 est
   supposée.
2. *La durée tous régimes* : le modèle y compte la bonification, que le régime
   général oppose à sa décote ; reste à lire si la Cnav l'y reçoit.
3. *Hors de la fiche* : les bénéfices de campagne et les bonifications pour
   services aériens et sous-marins ; la radiation pour infirmités ; la pension
   afférente au grade supérieur ; le non-cumul, avant 2023, des bonifications du
   policier devenu militaire.
4. *L'écart de la fonction publique d'État au COR*, qui s'ouvre à l'horizon :
   le cas type militaire reçoit le plafond de vingt trimestres, et le reste de
   l'écart est du côté civil ; à reprendre avec la grille (action 147).
5. *De l'étape 17, ensuite* : la pension maximale du régime général, les taux
   pleins de L. 351-8, les majorations pour enfants à charge et pour conjoint à
   charge.
