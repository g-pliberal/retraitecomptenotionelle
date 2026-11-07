# Les chiffres qui tiennent : sept affirmations du programme relues à leur source

*Le 7 novembre 2026, le propriétaire ouvre le chantier 7 de l'action 186 :
« un challenger est vérifié plus durement qu'un sortant ». La feuille de route
du programme en nommait sept chiffres ou affirmations, avec les pistes que la
session du 6 novembre avait citées de mémoire. Chacun est relu ici à sa
source — Insee, COR, Cour des comptes, BCE, Bundesbank, Légifrance, et
l'article de Breyer —, et chacun reçoit un verdict et une formulation qui
tient. Ce que la note conclut est une piste : le propriétaire tranche
(`docs/feuille_de_route_programme.md`, chantier 7). Aucun fichier du modèle
ni du site n'est touché.*

*Lire les chiffres.* **(publié)** est un chiffre lu ce jour dans sa source,
dont l'adresse est donnée. **(dépôt)** est une sortie du modèle au commit
`697d1b7`, ou une donnée certifiée du dépôt. **(calcul)** est une opération
de la session sur des chiffres publiés, posée en entier pour qu'on la refasse.
**(secondaire)** est un chiffre qu'aucune source primaire n'a pu confirmer ce
jour.

## L'essentiel

Quatre affirmations tombent ou doivent changer de mots, une se chiffre, deux
tiennent.

| Affirmation | Verdict | Ce qui tient |
|---|---|---|
| « La moitié du déficit public » | **à abandonner**, sauf à citer son auteur | Un cinquième selon la convention du site ; la moitié n'existe que dans le calcul de J.-P. Beaufret |
| « Proche du défaut », « taux stratosphériques » | **à chiffrer** | L'OAT à 10 ans au plus haut depuis 2008 ; la France emprunte plus cher que l'Italie et la Grèce |
| La BCE et le FMI | **tient, comme un risque** | Le bouclier de la BCE est conditionnel, et la France est sous procédure de déficit excessif ; la Grèce a coupé ses pensions dix fois |
| Le « TRI négatif » des cotisants | **faux**, à remplacer | Le rendement baisse d'une génération à l'autre, sans devenir négatif |
| 17,9 Md€ cotisés sans droits | **tient** | Le COR le dit en toutes lettres pour le cadre |
| Le PEE comme épargne retraite | **faux** | C'est le PER d'entreprise collectif, qui a succédé au Perco |
| « La capitalisation rendrait tout le monde plus riche » | **faux pour la transition** | Breyer (1989) : on ne peut pas dédommager la génération de la bascule sans appauvrir une génération suivante |

Une découverte en chemin, qui dépasse ce chantier : **l'outil du dépôt donne
à la proposition un rendement plus faible que le droit actuel pour les
jeunes générations** (0,2 % réel contre 1,3 % pour le salarié moyen né en
2000). Le programme ne peut donc pas plaider par le rendement sans dire
pourquoi la comparaison trompe (point 4).

## 1. « La moitié du déficit public »

**D'où vient le chiffre.** De Jean-Pascal Beaufret, qui l'écrit depuis 2023 (*Commentaire*, n° 182, présenté au COR
le 21 septembre 2023, document n° 6) et le reprend dans *Mesure et démesure :
retraites et déficit*, débat de juin 2025 publié par l'Institut Diderot en
mars 2026 : les retraites « ont créé un déficit public de 81 milliards
d'euros en 2024. Nous avions, en 2024, 170 milliards d'euros de déficit
public total. Les retraites expliquent la moitié de ce déficit » (p. 17)
**(publié)**. Son calcul : 412 Md€ de dépenses de retraite, moins 331 Md€ de
recettes, soit 267 Md€ de cotisations « normales », au taux de 28 % qui vaut
pour 80 % des actifs, 56 Md€ d'impôts affectés et 8 de recettes diverses. Son
tableau énumère ce qu'il range dans le déficit : la surcotisation de l'État
(44 Md€), celle des employeurs de la CNRACL (9), les subventions aux régimes
spéciaux (8), les exonérations compensées au régime général (5), et **les
transferts des branches famille, chômage et maladie au régime général (17)**
— l'assurance vieillesse des parents au foyer, les trimestres de chômage
(p. 18).

**Ce que disent les institutions.** Le COR mesure un déficit de **5,1 Md€ en
2025, 0,2 point de PIB**, hors charges et produits financiers (rapport annuel
de juin 2026, p. 91) **(publié)**. Il nomme lui-même la convention qui
ramènerait l'État au taux d'un employeur privé, 16,67 %, et la réfute : le
taux implicite de l'État « ne résulte pas d'une générosité plus importante du
régime public », mais d'une démographie dégradée, 1,29 cotisant par retraité
en 2020 contre 2,05 tous régimes confondus (p. 83-84) **(publié)**. La Cour
des comptes (février 2025) y voit « autant de formules de calcul que de
conventions comptables » ; l'IPP (2025) et le CAE (*Focus* 121) concluent
qu'il n'y a pas de « déficit caché » ; le dépôt les a lus
(`docs/risque_de_defaut.md`, § sur le déficit caché). Et toute convention
laisse le déficit public inchangé : elle ne fait que le répartir.

**La convention du site, appliquée.** Le site ne porte au compte d'un agent de
l'État que la part de la contribution de l'employeur que la Cour des comptes
rattache à sa retraite (action 129, `contribution_etat=retraite_seule`). La
Cour la mesure pour 2025 (*Les retraites des fonctionnaires de l'État*,
22 septembre 2026, tableau n° 15 ;
`data/reference/legislation/contribution_etat_retraite_seule.csv`)
**(dépôt)** : sur 53,9 Md€ de pensions civiles et 11,2 de pensions
militaires, 31,4 et 5,7 relèvent de la retraite des agents ; le reste, 28,0
Md€, paie l'invalidité (0,4), les majorations pour enfants (1,7), les départs
anticipés (4,0) et surtout le **déséquilibre démographique (22,1)**. Compter
ces 28,0 Md€ comme un besoin de financement, en plus des 5,1 du COR, donne
**33 Md€, 22 % du déficit public de 2025** **(calcul)** : 152,5 Md€, 5,1 % du
PIB (Insee Première n° 2106, 29 mai 2026) **(publié)**. Avec les subventions
aux régimes spéciaux, que la convention du site ne couvre pas (8 Md€ en 2024
selon Beaufret, chiffre à relire au jaune budgétaire), environ 41 Md€,
**27 %** **(calcul)**.

**L'échelle des conventions, en 2025** **(calcul)** :

| Convention | Besoin de financement des retraites | Part du déficit public |
|---|---|---|
| Le COR, conforme à la législation | 5,1 Md€ | 3 % |
| Le site : l'État ne paie à ses agents que leur retraite (Cour, 2026) | 33 Md€ | 22 % |
| Le même, avec les subventions aux régimes spéciaux | 41 Md€ | 27 % |
| L'État au taux d'un employeur privé, 16,67 % (convention que le COR décrit) | 52 Md€ | 34 % |
| Beaufret, tout ce qui n'est ni cotisation au taux commun ni impôt affecté (2024) | 81 Md€ | 48 % |

La ligne à 16,67 % applique ce taux à l'assiette que le tableau de la Cour
fait apparaître (56,9 Md€ pour les civils, 9,1 pour les militaires), contre
83,6 % et 112,3 % d'équilibre : 38,1 et 8,7 Md€, plus les 5,1 du COR. Elle
compare un taux sur traitement, primes exclues, à un taux sur salaire brut :
c'est un ordre de grandeur.

**Verdict.** La piste du 6 novembre se trompait sur un point : la convention
la plus large publiée atteint bien la moitié. Mais elle le fait en comptant
comme déficit ce que d'autres branches de la sécurité sociale versent pour
des droits qu'elles ont pour mission de financer, et c'est la convention que
le COR, la Cour, l'IPP et le CAE réfutent ensemble. Un challenger qui la
reprend à son compte prête le flanc à quatre institutions à la fois.

**Ce qui tient.**
- « Les retraites, c'est le quart de la dépense publique » : 14,1 % du PIB
  (COR, 422 Md€ en 2025) sur 57,3 % (Insee) **(publié)**.
- « Selon la convention du site — l'État ne verse à ses agents que ce que la
  Cour des comptes rattache à leur retraite —, les retraites expliquent un
  cinquième du déficit public de 2025 » ; ou « un quart », en y ajoutant les
  régimes spéciaux.
- « La moitié » seulement en citant son auteur, et sa méthode.

## 2. L'écart de taux avec l'Allemagne

**Les chiffres, à leur source** :
- *Moyennes mensuelles* (BCE, taux à long terme des critères de convergence,
  série `IRS.M.<pays>.L.L40.CI.0000.EUR.N.Z`, lue par son API le 7 novembre)
  **(publié)** : en septembre 2026, l'OAT à 10 ans rend **4,44 %**, le Bund
  3,47 % : **97 points de base** d'écart, contre 73 au printemps et 72 en
  juin. C'est le taux français **le plus haut depuis juillet 2008** (4,69 %),
  et l'écart le plus large depuis juillet 2012 (104 points). Le record de la
  crise de l'euro reste novembre 2011 : 154 points.
- *La France emprunte plus cher que la Grèce* chaque mois depuis août 2025,
  sauf en mars, avril et mai 2026, et *plus cher que l'Italie* de décembre
  2025 à février 2026, puis en août et septembre 2026 (en septembre, 4,44 %
  contre 4,36 % pour l'Italie et 4,22 % pour la Grèce) **(publié)**.
- *Au jour le jour* : le Bund rend 3,29 % le 6 novembre 2026 (Bundesbank,
  rendement des titres fédéraux à 10 ans de durée résiduelle) **(publié)** ;
  l'OAT, 4,76 % le même jour (Idéal Investisseur, qui cite la Banque de
  France) **(secondaire)** : environ **147 points**. Ni la Banque de France
  ni l'Agence France Trésor n'ont répondu au robot ; le chiffre du jour se
  relit chez elles avant d'être imprimé.

**Verdict.** « Proche du défaut » ne se démontre pas et s'attaque
facilement : la France place sa dette sans difficulté, et l'écart est loin
de ceux de la Grèce de 2012 (2 739 points en février). « Taux
stratosphériques » non plus. Les chiffres, eux, frappent davantage que
l'adjectif.

**Ce qui tient.** « Au [date], l'État emprunte à 10 ans à [x] %, [y] points
de plus que l'Allemagne, plus cher que l'Italie et la Grèce : du jamais vu
depuis 2008 » — les crochets remplis le jour de la publication, à la Banque
de France et à la Bundesbank, ou à la moyenne mensuelle de la BCE.

## 3. La BCE et le FMI : le risque, et le précédent grec

**La BCE.** Son instrument de protection de la transmission (TPI, 21 juillet
2022) peut acheter la dette d'un pays dont les écarts de taux s'envolent
sans raison, mais sous une « liste cumulative de critères », dont le
premier est de « ne pas faire l'objet d'une procédure de déficit excessif,
ou ne pas être jugé avoir manqué de prendre des mesures suivies d'effet »
en réponse à la recommandation du Conseil (communiqué de la BCE)
**(publié)**. La France est sous procédure de déficit excessif depuis la
décision du Conseil du **26 juillet 2024**, recommandation du 21 janvier
2025, rapports d'étape d'avril 2025, novembre 2025 et mai 2026 (Commission
européenne, page de la procédure, lue le 7 novembre) **(publié)**. Le
bouclier existe, mais il est conditionnel : c'est un fait, non une
prophétie. Que la Commission ait jugé, en juin 2026, que la France avait
pris des mesures suivies d'effet, une source secondaire l'affirme ; la page
de la Commission ne le montre pas, et ce point reste à vérifier.

**La Grèce** (sources que le dépôt a lues, `docs/risque_de_defaut.md`,
« Baisses en euros courants ») : pensions en paiement coupées « à dix
reprises entre 2010 et mi-2013 », pour un cumul « allant de 14 % pour les
petites pensions à presque 50 % pour les grandes » (Tinios, 2016) ; 13e et
14e mois supprimés en 2013 ; les coupes de 2012 jugées inconstitutionnelles
par le Conseil d'État grec en 2015, et onze mois remboursés en 2020, près
de 1 % du PIB (FMI, document de travail 21/188) **(publié)**. Ces coupes
accompagnaient les programmes d'assistance de 2010 et 2012, conclus avec la
zone euro et le FMI ; le FMI en faisait une condition (revue de juillet
2010, d'après une source secondaire — le site du FMI refuse le robot).

**La CEDH.** Elle a déclaré irrecevable, le 7 mai 2013, la requête contre
les coupes grecques de 2010 dans les salaires et les pensions publics
(*Koufaki et Adedy c. Grèce*), puis celles contre les coupes portugaises de
2012 (*Da Conceição Mateus et Santos Januário c. Portugal*, 8 octobre 2013)
(fiche thématique « Mesures d'austérité » de la Cour) **(publié)**. Un fait
qui compte pour la décision 6 du programme : la Cour admet une baisse des
pensions décidée dans l'intérêt public quand le pays est en crise, pourvu
qu'elle ne menace pas la subsistance de qui la subit.

**Ce qui tient.** « Si nous ne baissons pas les pensions selon une règle
juste, d'autres les baisseront à l'aveugle, comme en Grèce : dix coupes en
trois ans, jusqu'à la moitié des grosses pensions. » Le risque se dit au
conditionnel ; la Grèce, à l'indicatif.

## 4. Le rendement des cotisations : pas négatif, mais en baisse

**Ce que publie le COR** (rapport annuel de juin 2026, p. 139-141, 193 et
198) **(publié)**. Le taux de rendement interne — le taux qui égalise les
cotisations versées et les pensions reçues — se calcule sur le cas type
n° 2, un non-cadre du privé à carrière complète, net de CSG, flux actualisés
selon le salaire moyen (SMPT). Il « décroîtrait progressivement de la
génération 1940 aux générations du début des années 1970 », puis serait
« quasi stabilisé ». Pour la génération 2000 : **0,8 %**, entre 0,5 et
1,1 % selon l'espérance de vie et entre 0,7 et 0,9 % selon la productivité.
Selon le revenu, toujours pour la génération 2000 : **0,0 % pour un cadre**,
0,8 % pour un non-cadre, 2,9 % au SMIC avec les allègements, 0,3 % sans eux
(figure 3.A). Actualisé selon les prix, il est de 1,5 % pour le cas type
(annexe en ligne, d'après la note du dépôt de l'action 138). Aucun n'est
négatif.

**Ce que donne l'outil du dépôt** **(dépôt)**. Sa convention, à publier sur
le site : flux en euros courants, toutes les cotisations — salariales et
patronales, base et complémentaires, et pour l'État la part « retraite
seule » —, déflatés des prix, la survie de la génération ;
`python scripts/cycle_de_vie.py --indicateurs rendement_reel`. Au droit
actuel, le salarié au salaire moyen rend 3,3 % s'il est né en 1940, 1,3 %
s'il est né en 2000 ; le cadre, 2,6 puis 0,5 %. Les seuls rendements
négatifs que le dépôt trouve au droit actuel sont ceux du fonctionnaire de
catégorie B né à partir de 1980 (−0,1 % réel), et, sous les conventions du
COR (`--cor`, flux rapportés au salaire moyen), ceux du cadre né en 2000
(−0,5 %) et des fonctionnaires (−1,0 % en catégorie B) : là, le dépôt
s'écarte du COR, qui donne 0,0 % au cadre.

**Ce qui se retourne contre le programme.** Sous les mêmes conventions,
l'outil donne à la proposition (scénario 6) un rendement **plus faible** que
le droit actuel pour les générations jeunes : 0,2 % réel pour le salarié
moyen né en 2000, contre 1,3 % ; −0,8 % rapporté au salaire moyen, contre
0,4 % **(dépôt)**. La comparaison est biaisée en faveur du droit actuel, qui
compte des pensions promises que le COR projette sans financement (un
besoin de 2,4 points de PIB en 2070) : c'est la thèse du programme, mais
elle s'argumente, et le simulateur, lui, montre les chiffres. Le chantier 9
doit décider comment le site les présente.

**Verdict.** « TRI négatif » est faux sous la convention du COR et sous celle
de l'outil, pour tout salarié du privé. Un adversaire le réfutera avec le
rapport du COR.

**Ce qui tient.** « Le rendement de la répartition baisse de génération en
génération : 3,3 % par an au-dessus de l'inflation pour un salarié né en
1940, 1,3 % pour celui né en 2000 » (outil, convention publiée) ; « un cadre
né en 2000 récupérera tout juste ce qu'il a versé, revalorisé comme les
salaires » (COR, 0,0 %).

## 5. Les 17,9 Md€ cotisés sans droits

**Le calcul** (`docs/frontiere_contributive.md`, § 8) **(dépôt)** : la
cotisation vieillesse déplafonnée est assise sur toute la rémunération, dès
le premier euro (L. 241-3 et D. 242-4 du code de la sécurité sociale), et
n'ouvre aucun droit, le salaire de base étant borné au plafond (R. 351-29).
Son taux, 2,42 % (2,02 employeur, 0,40 salarié) en 2024 et 2025, appliqué à
l'assiette déplafonnée du secteur privé que publie l'Urssaf, 740,0 Md€ en
2025 (série certifiée, `data/reference/macro/masse_salariale_privee.csv`),
donne **17,9 Md€, dont 3,0 payés par les salariés**. Le taux passe à 2,51 %
en 2026.

**Ce qui le confirme.** Le COR l'écrit pour son cas type de cadre : il
« acquitte donc des cotisations déplafonnées à la Cnav élevées, ce qui
augmente son taux de prélèvement sans ouvrir de droits supplémentaires »
(rapport de juin 2026, p. 140) **(publié)** ; il date aussi le relèvement de
1,90 à 2,02 % de la part patronale en 2024 (p. 91).

**Verdict.** Solide. Une seule précaution : c'est un calcul du dépôt sur
deux séries publiées, aucun organisme ne publie cette masse. La phrase dit
donc « 17,9 milliards prélevés en 2025 sans qu'aucun droit n'y soit
attaché », avec sa méthode en note, et non « l'Urssaf chiffre ».

## 6. Le PEE n'est pas un produit de retraite

**Le droit.** Les sommes d'un plan d'épargne entreprise « sont indisponibles
pendant 5 ans », avec des cas de déblocage anticipé (service-public, fiche
F2142, vérifiée le 1er janvier 2026) **(publié)**. Le plan d'épargne
retraite a pour objet des droits « payables au titulaire à compter, au plus
tôt, de la date de liquidation de sa pension » dans un régime obligatoire,
ou de l'âge légal (code monétaire et financier, L. 224-1, en vigueur depuis
le 1er octobre 2019) **(publié)**. Il a deux formes d'entreprise : le PER
d'entreprise collectif (L. 224-13), qui « succède au Perco », et le PER
obligatoire (L. 224-23), qui succède au contrat « article 83 »
(service-public, fiche F34982, vérifiée le 12 octobre 2026) **(publié)**.

**Verdict.** Le programme doit dire « le PER d'entreprise » (collectif ou
obligatoire), jamais le PEE, qui est une épargne à cinq ans. La date à
laquelle aucun Perco ne peut plus être ouvert n'a pas été relue dans
l'ordonnance n° 2019-766 ; le programme n'en a pas besoin.

## 7. La capitalisation ne fait pas disparaître la dette des droits acquis

**La source.** Friedrich Breyer, « On the Intergenerational Pareto
Efficiency of Pay-as-you-go Financed Pension Systems », *Journal of
Institutional and Theoretical Economics*, vol. 145, n° 4, 1989, p. 643-658
(texte lu au dépôt de l'université de Constance) **(publié)**. Sa
conclusion (p. 655) : quand la répartition est remplacée par un système par
capitalisation ou par l'épargne privée, « il est en général impossible de
dédommager la première génération de retraités de la perte subie sans
rendre au moins une génération suivante plus pauvre qu'en répartition » ;
le choix entre les deux « ne se réduit pas à des critères d'efficacité,
c'est une question de répartition » entre générations. Breyer en tire
lui-même la leçon pour l'Europe de l'Ouest : basculer maintenant « ne peut
pas offrir à chaque génération un meilleur rendement de ses cotisations ».

**Ce que le dépôt sait déjà.** Les droits acquis valent près de quatre
années de PIB (affirmation `cout.compte_est_un_flux` du site) ; la dette
implicite, 369 % du PIB en 2015 et environ 400 % en 2021
(`docs/risque_de_defaut.md`).

**Verdict.** « La capitalisation rendrait tout le monde plus riche » est faux
pour la transition : le rendement supérieur du capital vaut pour l'argent
nouveau, pas pour la dette des droits déjà acquis, que quelqu'un doit
payer. C'est ce qui sépare le programme d'une bascule vers la
capitalisation : il garde la répartition, en comptes notionnels (décision 1).

**Ce qui tient.** « La capitalisation rapporte plus sur l'argent nouveau ;
elle n'efface pas les quatre années de PIB de droits déjà promis, que
quelqu'un doit payer. »

## Ce qui revient au propriétaire

1. **La moitié du déficit public** : l'abandonner pour « le quart de la
   dépense publique » et « un cinquième du déficit selon la convention du
   site », ou la garder en citant Beaufret, contre le COR, la Cour, l'IPP et
   le CAE.
2. **Les taux** : chiffrer à la date de publication, par la formule du
   point 2 ; renoncer à « proche du défaut ».
3. **Le rendement** : remplacer « TRI négatif » par la baisse d'une
   génération à l'autre ; et décider, au chantier 9, comment le site montre
   que la proposition rend moins que le droit actuel aux jeunes générations,
   dans l'outil du parti.
4. **Le PEE** : le remplacer par le PER d'entreprise dans tout texte du
   programme.

## Ce qui n'a pas été vérifié

- Le taux de l'OAT au jour le jour, à la Banque de France ou à l'Agence
  France Trésor : les deux refusent le robot.
- Le jugement de la Commission, en juin 2026, sur les mesures prises par la
  France ; la place exacte de la réforme des pensions dans les conditions du
  FMI en 2010.
- Les subventions de l'État aux régimes spéciaux en 2025, à relire au jaune
  « pensions » ; le chiffre de 8 Md€ est celui de Beaufret pour 2024.
- Le rendement interne au prix du COR (1,5 %), repris de la note de
  l'action 138 et non relu dans l'annexe ce jour.
- La date de fermeture du Perco dans l'ordonnance n° 2019-766.

## Sources lues ce jour

- Insee, *Le compte des administrations publiques en 2025*, Insee Première
  n° 2106, 29 mai 2026 : https://www.insee.fr/fr/statistiques/8997691
- COR, *Évolutions et perspectives des retraites en France*, rapport annuel,
  juin 2026 :
  https://www.cor-retraites.fr/sites/default/files/2026-06/RA_2026_def.pdf
- J.-P. Beaufret, *Mesure et démesure : retraites et déficit*, Les Carnets
  de l'Institut Diderot, 2026 :
  https://www.institutdiderot.fr/wp-content/uploads/2026/03/JP-Beaufret-Retraites-et-deficit-Page.pdf
- J.-P. Beaufret, « Retraites obligatoires et déficits publics », COR,
  séance du 21 septembre 2023, document n° 6 :
  https://www.cor-retraites.fr/sites/default/files/2023-09/Doc_06_Retraites%20obligatoires_d%C3%A9ficits%20publics.pdf
- BCE, taux à long terme des critères de convergence, API :
  https://data-api.ecb.europa.eu/service/data/IRS/M.FR+DE+IT+GR.L.L40.CI.0000.EUR.N.Z
- Bundesbank, rendement quotidien des titres fédéraux à 10 ans, série
  `BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A` :
  https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A
- Idéal Investisseur, écart OAT-Bund (secondaire) :
  https://www.ideal-investisseur.fr/en/markets/oat-bund-spread.html
- BCE, communiqué du 21 juillet 2022 sur le TPI :
  https://www.ecb.europa.eu/press/pr/date/2022/html/ecb.pr220721~973e6e7273.en.html
- Commission européenne, la procédure de déficit excessif de la France :
  https://economy-finance.ec.europa.eu/economic-governance-framework/stability-and-growth-pact/corrective-arm-excessive-deficit-procedure/excessive-deficit-procedures-overview/france_en
- CEDH, fiche thématique « Austerity measures » :
  https://prd-echr.coe.int/documents/d/echr/FS_Austerity_measures_ENG
- Légifrance, code monétaire et financier, L. 224-1, L. 224-13 et
  L. 224-23 : https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038507575,
  https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038818297,
  https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000038818385
- Service-public, PEE (F2142) et PER (F34982) :
  https://www.service-public.gouv.fr/particuliers/vosdroits/F2142,
  https://www.service-public.gouv.fr/particuliers/vosdroits/F34982
- F. Breyer (1989), dépôt de l'université de Constance :
  https://kops.uni-konstanz.de/handle/123456789/16640
