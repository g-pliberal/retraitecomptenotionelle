# 5 bis. Le coût agrégé : ce qui est observé, ce qui est estimé

La page **Coût** superpose deux natures de chiffres, et il faut les séparer pour
la lire.

**La dépense observée n'est pas modélisée.** Elle vient des Comptes de la
protection sociale de la DREES, risque vieillesse-survie, poste `E11-2`, et elle
est **certifiée** : recontrôlée contre l'API du producteur à chaque exécution,
1959 à 2024 pour le total, 1990 à 2024 pour la ventilation par système. Deux
réserves de PÉRIMÈTRE, et non de fiabilité :

- le risque vieillesse-survie est plus large que « les retraites » : il porte
  aussi le minimum vieillesse, la dépendance des personnes âgées et la retraite
  supplémentaire par capitalisation, soit <!--chiffre:mesure(depense?annee=2024&quoi=hors_repartition)-->27,9<!--/--> milliards sur <!--chiffre:mesure(depense?annee=2024)-->426,7<!--/--> en 2024. La
  ventilation permet de les retrancher, et la page affiche les deux grandeurs ;
- la ventilation ne commence qu'en 1990. De 1981 à 1989 la DREES en publie une
  autre, dont les périmètres ne se raccordent pas — « Régime général de la
  Sécurité sociale » y recouvre ce qui est aujourd'hui réparti entre la Cnav et
  d'autres organismes. Personne n'a publié le raccord : c'est une impasse
  démontrée, et non un oubli.

Le découpage lui-même est celui de la **comptabilité nationale**, par secteur
institutionnel et non par caisse. Deux conséquences qu'il faut connaître :
« régimes spéciaux » réunit la CNRACL — donc la fonction publique territoriale
et hospitalière —, la SNCF, la RATP et les IEG ; et « régime général » absorbe à
compter de 2020 les artisans et les commerçants, dont le régime a été adossé à
la Cnav. La marche de 2020 est une réorganisation, pas une dépense nouvelle.

**Le coût des quatre autres systèmes est estimé, et ne peut pas être autre
chose.** Il est obtenu en multipliant les pensions de répartition obligatoire
observées par le rapport des masses de pension — la moyenne des écarts entre
systèmes, pondérée par le poids de chaque génération dans la masse de l'année.
*Corrigé le 23 septembre 2026* : le rapport multipliait jusque-là le risque
vieillesse-survie entier, et réduisait donc comme des pensions l'aide à
l'autonomie, la retraite supplémentaire et le minimum vieillesse, qui ne sont la
pension d'aucun système. Les économies du passé en étaient grossies de près
d'un dixième. Avant 1990, que la DREES ne ventile pas, la part de la
répartition dans le total est celle de 1990 : une hypothèse, que l'aide à
l'autonomie, inexistante alors, et le minimum vieillesse, plus lourd,
tirent en sens contraires. Ce rapport porte quatre
approximations, énoncées sur la page — la quatrième ayant cessé d'en être une
le 19 septembre 2026 :

1. **Les effectifs de génération ne sont plus supposés.** Cette page a d'abord
   pesé toutes les générations à égalité, faute de pyramide des âges ; elle
   porte désormais celle de l'INSEE, observée jusqu'en 2023. On sait donc
   maintenant ce que valait l'hypothèse levée : elle déplaçait l'écart cumulé du
   scénario 2 de six dixièmes de point sur soixante-six ans (−77,3 % contre
   −77,9 %). C'était peu, et c'est désormais mesuré plutôt qu'argumenté.
2. **Les treize cas types ne pèsent plus d'un poids égal.** Ils ont longtemps
   pesé ainsi, faute de source, et cette page affirmait qu'« aucune source ne
   fixerait » la pondération. C'était faux : l'enquête annuelle auprès des
   caisses de retraite dénombre les retraités caisse par caisse et année par
   année depuis 2004. Chaque cas type porte désormais l'effectif de sa caisse ;
   l'agent de conduite pèse <!--chiffre:mesure(poids?cas=agent_sncf_conduite)-->1,5<!--/--> % et non <!--chiffre:mesure(poids?cas=agent_sncf_conduite&ponderation=egale)-->7,7<!--/--> %, et les quatre carrières du
   privé <!--chiffre:mesure(poids?cas=smic_carriere_complete|salaire_moyen|cadre|carriere_interrompue)-->55<!--/--> % à elles quatre.

   Ce que l'ancienne convention valait est donc mesuré plutôt qu'argumenté, et
   **le sens du biais annoncé n'était juste qu'à moitié**. On disait le rapport
   affiché « plutôt un plancher », les départs très précoces que le notionnel
   pénalise le plus étant surreprésentés. C'est vrai des scénarios qui portent
   la part patronale — le scénario 4 passe de <!--chiffre:mesure(ecart_passe?scenario=4&ponderation=egale)-->−53,7<!--/--> % à <!--chiffre:mesure(ecart_passe?scenario=4)-->−52,4<!--/--> % — et faux du
   scénario 2, qui passe de <!--chiffre:mesure(ecart_passe?scenario=2&ponderation=egale)-->−75,7<!--/--> % à <!--chiffre:mesure(ecart_passe?scenario=2)-->−79,2<!--/--> % : la pondération donne aux
   carrières du privé, que le compte salarial seul pénalise davantage encore,
   les deux tiers du poids. C'était un plancher pour les uns, un plafond pour
   l'autre.

   Trois réserves subsistent, et elles sont de nature différente de la
   précédente. **Un effectif de caisse n'est pas un effectif de personnes** :
   un polypensionné compte dans chacune des siennes, et la somme des caisses
   dépasse d'un tiers la ligne « tous régimes » ; le poids des régimes dont les
   affiliés ont typiquement aussi une carrière au régime général — Ircantec,
   MSA salariés — en est gonflé. **Une caisse réclamée par plusieurs cas types
   se partage également entre eux** : la Cnav est celle des quatre carrières du
   privé, et aucune source ne dit combien de ses retraités ont été cadres ;
   c'est la seule part de convention égalitaire qui subsiste, et elle ne joue
   plus qu'à l'intérieur du salariat privé. **Hors de 2004-2024, la répartition
   du bord est reconduite** : la France de 1960 comptait plus d'exploitants
   agricoles que ces poids ne le disent, et la série tombe au niveau `estimee`
   pour le dire.
3. **Avant 1975, la reconstitution est mince.** La répartition ne commence
   qu'en 1941 : les générations antérieures à 1880 n'ont, dans ce modèle,
   aucune pension, et plusieurs régimes n'existaient pas encore. Les premières
   années reposent sur deux ou trois générations et la moitié des cas types.
   Elles pèsent peu dans le cumul — la dépense de 1959 vaut <!--chiffre:mesure(rapport_depenses?de=1959&a=2024)-->0,5<!--/--> % de celle de
   2024 en euros courants — mais leur rapport ne vaut pas ce que valent ceux
   d'après 1980.

4. **Le rapport ne multiplie plus la réversion, et c'est le volet C.** Il
   décrit les droits DIRECTS et eux seuls : il est le quotient de deux masses
   calculées sur treize cas types, qui n'ont ni conjoint ni survivant, et la
   réversion figure depuis toujours parmi les droits que même l'étalon ne sert
   pas. La base à laquelle on l'appliquait, elle, porte les deux. Un scénario
   notionnel réduisait donc la réversion dans la même proportion que les
   pensions propres, **sans que rien ne l'ait décidé** — et il l'a fait
   jusqu'au 19 septembre 2026.

   La base est désormais ventilée. `part_droits_derives.csv` dit quelle
   fraction de la masse versée est une pension de réversion : <!--chiffre:cellule(data/reference/macro/part_droits_derives.csv:part*100?annee=2010)-->12,4<!--/--> % en 2010,
   <!--chiffre:cellule(data/reference/macro/part_droits_derives.csv:part*100?annee=2024)-->10,4<!--/--> % en 2024, <!--chiffre:cellule(data/reference/macro/part_droits_derives.csv:part*100?annee=2040)-->9,5<!--/--> % en 2040, <!--chiffre:cellule(data/reference/macro/part_droits_derives.csv:part*100?annee=2070)-->5,7<!--/--> % en 2070 — la réversion recule dans la
   projection du COR, les carrières des femmes se rapprochant de celles des
   hommes. Le rapport ne multiplie plus que le reste.

   **Ce que le scénario fait de la réversion est maintenant une décision, et
   elle est écrite : seul le scénario 1 la sert.** Décision du Parti libéral,
   19 septembre 2026, et elle ne fait qu'appliquer à cette ligne la règle des
   trente-huit autres. Les scénarios 2 à 6 retirent tous les avantages non
   contributifs, et l'inventaire du dépôt range la réversion parmi eux depuis
   toujours : « non contributive au sens strict, la cotisation de l'assuré
   ayant déjà été rendue par sa propre pension », et « de très loin la
   PREMIÈRE dépense non contributive du système ». La servir dans un compte
   notionnel était l'exception non écrite, pas la règle ; ces cinq scénarios
   mesurent ce qu'une retraite composée uniquement de part contributive
   représente, et une réversion n'en est pas. C'est le chemin de la Suède, où
   un compte notionnel ne verse qu'à son titulaire.
   `convention_reversion="servie"` reste calculable, mais ce n'est pas celui
   de l'Italie : l'Italie sert la réversion en la tarifant dans son
   coefficient de transformation —
   1,460 des 19,049 années de rente du diviseur à <!--chiffre:illustration()-->65<!--/--> ans (note technique du
   décret du 20 novembre 2024, tableau C.2) —, quand `servie` l'ajoute sans
   rien retirer à la pension directe.

   **Les cinq la retirent à tout le monde, et du même jour.** Les scénarios
   RÉTROACTIFS (2, 4, 6) recalculent toutes les pensions depuis 1941 : ils n'en
   servent jamais un euro. Les scénarios PROSPECTIFS (3, 5) sont, par
   construction, le système actuel jusqu'à leur bascule — ils y recopient ses
   pensions, et un test tient l'égalité de leurs courbes à l'euro près —, si
   bien qu'ils y servent sa réversion comme le reste ; à compter de la bascule
   ils ne la servent plus, aux veuves d'avant comme à celles d'après.
   `reforme_en_vigueur` porte ce seul basculement.

   Ce n'est pas le traitement que le modèle réserve aux autres avantages non
   contributifs dans les scénarios prospectifs : un minimum contributif servi à
   qui a liquidé en 2010 lui reste acquis pour toujours, parce que sa pension
   entière est recopiée. La réversion fait exception, et par décision : le
   programme a voulu qu'aucun scénario notionnel n'en verse à compter du jour
   où il s'applique.

   Ce que la décision rend : **+1,19 point de solde moyen 2026-2070 à chacun
   des cinq**, exactement le même chiffre. Ce n'est pas une coïncidence — la
   réversion retirée est une part de la BASE, qui ne dépend d'aucun rapport de
   masses, et les cinq la retirent sur la même fenêtre, celle qui commence à la
   bascule. Le scénario 1 ne bouge pas d'un iota, son
   rapport valant un, et un test l'exige. Le scénario 5 retrouve au passage
   l'équilibre dès la bascule et repasse au-dessus du système actuel, sa
   moyenne restant néanmoins négative.

   **Et la part est contrôlée chez un autre producteur.** Elle est construite à
   partir du classeur du COR, où douze des vingt-deux régimes publient leur
   droit dérivé à part — pour les dix autres, dont la fonction publique d'État
   et la CNRACL, c'est la différence entre la masse de prestations et le droit
   direct. La DREES, elle, ventile ses propres comptes en droit direct
   (`E11-21.1`) et droit dérivé (`E11-22.1`) depuis 2020. Deux enquêtes, deux
   périmètres, deux nomenclatures, cinq années communes : les parts s'écartent
   de **0,06 point au plus**, et de 0,01 point deux fois. C'est le seul
   contrôle externe dont cette série dispose, et il est bon.

   Ce qui reste : la part est très légèrement SURESTIMÉE pour les dix régimes
   sans bloc dédié, la différence prestations moins direct portant aussi un
   petit résidu de prestations qui n'est ni l'un ni l'autre — 0,3 % des
   prestations là où on peut le mesurer. Et hors de 2010-2070, la valeur de
   bord est reconduite au niveau `estimee` : la dépense observée remonte à
   1959, cette ventilation non.

5. **La grille ne monte pas au-delà de 2,5 fois le salaire moyen.** Le plus
   haut des treize cas types est la profession libérale, à 2,5 ; le
   simulateur, lui, accepte jusqu'à dix fois le salaire moyen. Toute règle qui
   ne mord qu'aux hauts revenus est donc INVISIBLE dans l'agrégat, et cela
   vaut dans les deux sens : ni la pension qu'elle ouvre, ni la cotisation
   qu'elle appelle. Le déplafonnement de l'assiette, décidé le 20 septembre
   2026 (action 61), en est la démonstration : il change la pension du
   simulateur de +12 à +14 % au-delà de neuf fois le salaire moyen, et il ne
   déplace ni le coût, ni le solde, ni un coefficient d'équilibre — mesuré à
   l'identique, au centime, sur les quatre systèmes et tout l'horizon. Ce
   n'est pas une propriété du déplafonnement : c'est que personne, dans la
   grille, ne gagne assez pour être concerné. La recette supplémentaire qu'un
   vrai déplafonnement apporterait n'est donc pas chiffrée ici, et la dépense
   supplémentaire non plus.

**Ce que la grille de treize cas types déplace, mesuré le 5 octobre 2026**
(`scripts/grille_large.py`, action 136, étape 6). La page refaite sur une
grille de 791 carrières au lieu de 13, ancrée sur l'échantillon interrégimes de
2020 et sur les centiles du salaire du privé de 2024 : les personnes de chaque
régime principal au lieu des retraités de chaque caisse, les polypensionnés,
une moitié de femmes avec leurs enfants, les carrières courtes et les périodes
assimilées que l'enquête dénombre, des salaires jusqu'à neuf fois le salaire
moyen. L'écart des années observées s'y creuse de 4,5 points au scénario 2 et
de 8,0 aux scénarios 4 et 6 ; la dépense du système actuel en 2070 monte de
0,36 point de PIB, et s'éloigne d'autant de celle du COR ; le solde moyen de la
proposition passe de −0,52 à −0,25 point de PIB, quand sa garantie vieillesse
coûte 17 % de plus en 2070. Les femmes et les carrières courtes en font
l'essentiel. La même grille refait mieux le passé : le pire écart, depuis 2000,
de la projection à rebours à la dépense observée (action 147) y tombe de 20 à
13 %. Ce n'est pas une population : les axes y sont tenus pour indépendants, et
deux de ses parts sont des conventions — dix années de salariat avant le régime
d'un polypensionné, deux enfants par femme.

**La page compte encore le minimum vieillesse des premiers non-salariés**,
trouvé par la même mesure. L'artisan né de 1885 à 1905, le libéral jusqu'en
1915, l'exploitant agricole jusqu'en 1920 : leurs régimes, nés après la
guerre, ne leur servaient que des pensions courtes ou forfaitaires, que le
scénario 1 complète à l'ASPA ; les scénarios notionnels ne la servent pas, et
la dépense que la page multiplie l'exclut depuis le 23 septembre 2026. L'écart
des années observées en est grossi : −78,70 % au lieu de −77,87 au scénario 2,
−52,13 % au lieu de −50,38 aux scénarios 4 et 6. La projection ne bouge pas
d'un millième de point.

**Ce qui, en revanche, n'est pas une approximation** : l'égalité des scénarios
3 et 5 avec le système actuel sur toute la période observée. Elle est EXACTE, et
au sens strict — le scénario prospectif recopie la pension du scénario actuel
pour qui a liquidé avant la bascule. La page ne l'écrit pas en dur : elle teste
l'identité des courbes année par année, et les séparerait si la bascule était
avancée avant la dernière année publiée.
