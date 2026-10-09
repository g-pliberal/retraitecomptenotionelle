# Le classement des restes de l'action 138, par leur poids

**Reprise, au 9 octobre 2026.** Fait : les restes de l'action classés par ce
qu'ils déplacent dans ce que le site compare (ci-dessous). Au propriétaire :
la coupe — faire le lourd et le moyen, déclarer le léger `approchee` ou
`pas_encore_modelisee` dans la carte sans le faire — et les choix de l'étape
13, qui pèsent plus que tout le reste. D'ici là, une session qui choisit son
étape prend la première ligne libre du rang lourd : l'effet retour (étape 5),
puis la CNRACL (étape 3), puis les années sans montant (étape 11). Le
registre retarde : il dit `a_reprendre` des points que les étapes 2, 4, 6, 8
et 17 ont repris.

**Le 9 octobre 2026, la demande.** Le propriétaire demandait s'il ne serait
pas plus simple de reprendre le code des modèles analysés, Destinie,
TRAJECTOiRE, OpenFisca-France-Pension. La réponse a été non pour leur code :
aucun ne calcule la proposition, aucun n'a la loi du 30 décembre 2025, aucun
ne tourne dans un navigateur, et leurs licences sont à réciprocité. Mais le
travail de fourmi tient à la barre de l'action, « meilleur en tous points »,
où chaque reste prend sa session, qu'il touche beaucoup de monde ou presque
personne. D'où la demande : « Oui, fais le classement des écarts restants par
poids ».

**La mesure.** Le poids d'un reste, c'est ce qu'il déplace dans ce que le site
compare : l'écart entre le scénario 1 et la proposition, pour une personne (le
simulateur) et pour la population (la page Coût). Quatre faits le fixent, tous
lus au dépôt :

- la proposition n'a « ni majorations enfants, ni MDA, ni AVPF, ni
  bonifications, ni réversion, ni trimestres gratuits »
  (`data/reference/couches/comptes_notionnels.yaml`) : une règle du scénario 1
  qui manque ou qui se trompe déplace la comparaison de tout son montant, pour
  les personnes qu'elle concerne ;
- depuis le 4 octobre, les scénarios 2 à 6 appliquent le taux de prélèvement
  de la personne au scénario 1 (étape 2) : une erreur sur le net déplace les
  deux côtés ensemble, et ne pèse rien sur la comparaison ;
- la page Coût ne calcule aucune réversion : le scénario 1 la sert dans tous
  les cas, la proposition la supprime (`cout.py`, convention `supprimee`) ;
  une règle de réversion ne pèse que sur le simulateur ;
- l'échelle : 17,3 millions de retraités et 426,7 Md€ de pensions en 2024
  (`effectifs_retraites.csv`, `docs/avantages_non_contributifs.md`). La
  majoration pour conjoint à charge, dernière partie de l'étape 17, pèse
  0,07 Md€ (`prestations_non_contributives.csv`).

Quatre rangs. **Lourd** : ce qui déplace toutes les pensions de la proposition,
ou l'économie de la page Coût, de plus de 1 %, ou d'un milliard. **Moyen** : un
groupe de plus de cent mille personnes, de quelques pour cent. **Léger** :
moins. **Nul** : ce qui ne déplace aucun chiffre — l'affichage, la
certification d'une valeur déjà juste, un droit éteint. Ce sont des ordres de
grandeur, tirés du registre, des notes et des données du dépôt ; aucun n'est
certifié, et le classement sert à décider, non à publier. Les sessions sont
estimées sur l'étape 17 : onze notes, une par règle, du 7 au 9 octobre.

L'état vient des notes et des blocs « Reprise », non du registre, qui retarde :
il dit encore `a_reprendre` les points des chantiers 138.2, 138.4, 138.6,
138.8 et 138.17 que leur étape a repris.

## Lourd : à faire d'abord

| Reste | Étape | Ce qu'il déplace | Qui | Effet | Sessions |
|---|---|---|---|---|---|
| L'effet retour : l'ASPA que déclenchent les petites pensions des scénarios 2 à 5, et les impôts affectés, que `cout.py` tient fixes | 5 | l'économie de la page Coût | toutes les petites pensions de la proposition | un gain public inférieur de 20 à 25 % à l'économie des régimes (IPP, juin 2026 ; registre, `simulateur_aurain`) | 2 |
| La CNRACL pondérée sur un seul départ, en catégorie active à 57 ans | 3, avec l'action 147 | l'économie de la page Coût, surestimée : le biais a un signe connu | 1,39 million de retraités, 6 % des poids | l'âge moyen de départ y est de 61,5 ans en 2023, de 64,3 en 2070 ; le départ à 57 ans est celui que le notionnel pénalise le plus (registre, `canopee`) | 1 à 2 |
| Les années sans montant, comptées zéro au compte notionnel ; les points du relevé « lus, et jetés » | 11 | la pension de la proposition, au simulateur | qui importe un relevé dont des années n'ont que des points ou des trimestres | chaque année sans montant ôte une année de cotisations ; la Pologne y met le salaire minimum, la Lettonie la moyenne, PROST la moyenne revalorisée (registre) | 1 |
| La population simulée, et sa validation sur des pensions réelles | 14, avec l'action 136 | toute la page Coût, que portent 13 cas types pondérés | tous | la grille chiffrait à zéro la majoration pour enfants, 7,78 Md€ publiés ; les postes lus ont corrigé les masses, non la composition | plusieurs, et le CASD |
| La revalorisation différenciée du projet de loi de financement pour 2027 (art. 35) | 12, la veille | toutes les pensions du scénario 1 dès 2027 | tous les retraités | nul tant qu'il n'est pas voté | 1, au vote |

## Moyen : ensuite, le meilleur rapport du poids au coût d'abord

| Reste | Étape | Ce qu'il déplace | Qui | Effet | Sessions |
|---|---|---|---|---|---|
| Le temps partiel des fonctionnaires, compté à temps plein dans les services | action 136, étape 3 | la pension du scénario 1 | qui a travaillé à temps partiel sans surcotiser, parmi 3 millions de retraités du service des retraites de l'État et de la CNRACL | dix ans à 80 % : huit trimestres de services de trop, 3,5 points sur les 75 % du taux plein (fiche `temps_partiel_fonction_publique`) | 1 |
| Le diviseur éprouvé sur les exemples officiels de la Suède, de la Finlande, de l'Italie et de la Pologne | 11 | aucune pension si le calcul tient, toutes sinon | toute la proposition | une assurance sur la formule que traverse chaque pension notionnelle | 1 |
| Les variantes d'espérance de vie, dans le diviseur et la page Coût | 7 | aucun chiffre central : elles montrent ce que le diviseur absorbe | — | deux ans de vie en plus coûtent 0,1 point de PIB en 2070 au notionnel letton, 0,7 à la France (Ageing Report de 2024 ; registre, `modele_lettonie`) : l'argument même de la proposition | 1 |
| Les cotisations PCV (ex-ASV) des professions de santé conventionnées | 18 | les deux côtés : la pension du scénario 1 et le compte | infirmiers, kinésithérapeutes, dentistes et sages-femmes, qui n'ont pas cet étage ; le médecin, au tiers du secteur 1, sur un forfait de 2016 | un étage entier de leur retraite (registre, `modele_ti`) | 1 à 2 |
| Une carrière heurtée dans la grille des cas types | 19 | la page Coût et les cas types | les carrières de chômage puis d'inactivité, qu'aucun des 13 cas types ne porte | là s'écartent les périodes assimilées du scénario 1 et le compte, qui ne porte, pour une année de chômage, que ce que l'Unédic verse aux complémentaires (registre, `osiris`, `maquette_globale_cor`) | 1 |
| Le statut du non-salarié agricole : conjoint collaborateur, aide familial, chef à titre secondaire | 8 | la pension du scénario 1, trop haute | une part du 1,02 million de retraités non salariés agricoles | le modèle leur sert la PMR et le complément du chef, quand la loi réduisait la PMR de 2009 à 2021 et réserve le complément au chef ; un champ de saisie | 1 |
| Les contributions d'équilibre de l'Agirc-Arrco dans ce qui est versé | 9 | le rendement du scénario 1, sur la page des indicateurs | tous les cotisants de l'Agirc-Arrco | l'ASF, l'AGFF, la CEG et la CET, prélevées sans créer de points | 1 |
| Le micro-entrepreneur saisi par son chiffre d'affaires, et le chemin de la Cipav | 12 | les deux côtés, par la saisie | les micro-entrepreneurs qui se simulent | l'utilisateur reconstitue aujourd'hui son revenu, sans l'abattement | 1 |
| La mortalité différentielle des cas types | 7 | la page Coût, cas type par cas type | tous les cas types, qui vivent comme la population générale | la durée de service de chaque pension | 1 |

## Le site : aucun chiffre ne bouge, l'usage décide

Étape 10 et action 136, étape 4. Plusieurs âges de départ côte à côte, la
question que pose d'abord qui se simule ; l'indice majoré à la saisie des
fonctionnaires ; le contrôle d'un relevé ; les droits contrefactuels de 2023 ;
le solveur inverse ; la fiche et l'article sous « Le détail du calcul », que
les modèles de l'Urssaf et Catala donnent, et que le site ne donne pas.

## Léger ou nul : à déclarer dans la carte plutôt qu'à faire

Une centaine de restes, chacun dans sa note. Le principe 1 demande qu'ils
soient déclarés, non qu'ils soient calculés : `approchee` ou
`pas_encore_modelisee`, avec ce qu'ils laissent de côté.

- *Étape 17*, une quarantaine de restes dans ses onze notes : des textes
  d'avant 1975 qu'aucun index ne porte, des régimes spéciaux qui copient une
  règle, des cas rares (évadés, officiers parents de trois enfants, conjoint
  inapte). Seuls les bénéfices de campagne et les services aériens et
  sous-marins des militaires (376 810 retraités militaires en 2024) approchent
  le moyen.
- *Étape 4*, dont la réversion d'un assuré mort avant son départ, du rang
  moyen, a été faite le même jour par une autre session : le partage entre
  ex-conjoints et le remariage, L. 353-5 et D. 355-1, les majorations
  forfaitaires d'avant 1995 et 1982, la révision du plafond, le plafond
  semestriel de 1982 à 1996, les maxima des salariés agricoles et des
  indépendants. La réversion ne pèse que sur le simulateur.
- *Étape 6* : la certification au Journal officiel de montants que le barème de
  la Cnav donne déjà ; la pension minimum d'avant avril 1983 et la retenue
  d'avant 1946, des droits presque éteints ; R. 732-70 ; l'outre-mer et son
  champ.
- *Étape 8*, hors du statut : l'exemple chiffré de la MSA, le SMIC net
  agricole de 2015 à 2020 et de 2022, les plans de 1994 à 2002, les pensions
  déjà liquidées, la révision annuelle du complément.
- *Étape 16* : les coefficients de l'Agirc d'avant 1955 et de l'Arrco d'avant
  1965, pour des liquidations d'avant 1965. Nul.
- *Étape 18*, hors des cotisations PCV : les points d'avant 1973 des artisans
  et des commerçants, l'assiette abattue de 2025, les points d'incapacité, les
  grilles de la CAVEC, le forfait de la CNBF selon l'ancienneté
  (16 590 retraités), le plafond du RCI, le taux propre de l'artisan au-dessus
  du plafond, le conjoint collaborateur, les dispenses, Mayotte, la Lodeom.
- *Étape 20* : l'Ircantec à dater, une date de revalorisation sur 2,1 millions
  de petites pensions.
- *Étape 12*, hors du micro-entrepreneur et de la veille : la seconde pension
  revalorisée et replafonnée, les artistes-auteurs sous le seuil, la dispense
  des cotisations minimales, le rachat de trimestres, le coût du travail
  complet, la taxe sur les salaires, le dirigeant assimilé salarié.
- *Étape 2* : la série de l'ASPA d'une personne seule, des centimes ; les
  ressources hors pensions de R. 815-29 ; et la relecture des points du
  registre, à faire quand même, parce qu'elle ne coûte presque rien et que le
  registre se trompe tant qu'elle attend.
- *Étapes 3, 7, 9, 11 et 19*, les confrontations et les indicateurs, qui ne
  changent aucun chiffre tant qu'ils ne trouvent pas d'erreur : la
  décomposition de l'Ageing Report, le levier de l'âge, la CSG effective, les
  contrôles d'Ancetre et de l'EACR ; la fécondité et les migrations, les
  départs qui suivent l'espérance de vie, 2025 sous la loi seule ; les
  prélèvements depuis 1980, les indicateurs à chaque âge, l'âge d'équilibre ;
  le lissage italien exact, le lissage du seul réel, le prorata des mois de
  l'année du départ, les chocs du COR ; la rétro-projection, l'incertitude
  propagée, la part de la solidarité, le bilan du compte, le taux d'équilibre.
- *Action 136, étapes 2 et 5* : les tests formule par formule, une interface
  de programmation et des versions numérotées.

## Ce que le propriétaire tranche, et qui pèse plus que tout le reste

Étape 13 : 43 points `a_trancher` au registre, une décision chacun, non des
sessions. Chacun des quatre premiers déplace de plusieurs pour cent les
pensions de la proposition de millions de personnes, plus que tous les restes
légers réunis :

- l'assiette qui fait le rendement du compte : les seuls salaires, comme
  aujourd'hui, ou le revenu des indépendants compris, soit 0,61 point de
  rendement de moins par an sur 1950-2024, et 11,5 % de moins sur une
  cotisation versée vingt ans avant le départ ((137,4 / 216,3) à la puissance
  20/74, calcul de la session) ;
- les gains d'héritage : 4 à 10 % de plus sur toutes les pensions
  notionnelles ;
- le diviseur des droits acquis à la bascule : sous celui de l'année de la
  bascule, la part figée de l'actif de quarante ans en 2026 perd 9,0 %, celle
  de l'actif de trente ans 11,8 % ;
- le calendrier de l'indexation : +7,9 % pour un départ en 2021, −4,0 % pour un
  départ en 2020.

Viennent ensuite la convention de l'Agirc-Arrco en projection, la réversion
tarifée dans le diviseur, l'équilibrage à la suédoise, un plancher de
revalorisation, les années d'enfant et l'AVPF au compte, une garantie à
retrait partiel, une transition panachée par génération.

## Ce que la coupe économise

Les rangs lourd et moyen tiennent en une quinzaine de sessions, la population
à part. Le léger, une centaine de restes, en demanderait plusieurs dizaines au
pas de l'étape 17, pour des groupes de quelques milliers de personnes ou des
droits presque éteints. Le déclarer dans la carte, là où une fiche ne le dit
pas déjà, prend une ou deux sessions.

**Au propriétaire.** Deux décisions : la coupe, qui change la demande du
1er octobre (« meilleur en tous points ») pour le seul rang léger ; et les
choix de l'étape 13, les quatre premiers d'abord.
