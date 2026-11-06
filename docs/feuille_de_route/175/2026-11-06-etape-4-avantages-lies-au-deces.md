# Étape 4, thème « Avantages liés au décès de l'assuré » : les exposés et leurs références

**Le 6 novembre 2026, ce qui est fait.**

- *La relecture de la base.* Par l'API, le 6 novembre 2026 de 12 h 02 à 12 h 20 UTC, par
  les fonctions de `scripts/fetch/cnav_legislation.py` (`_obtenir`, `liens`, `_reference`,
  `_fenetre`), sans écrire le registre : `/expose`, `/liste`, `/baremes`, les trois
  collections des fenêtres et `/mises-a-jour`, de l'import de la nuit (5 h 00 UTC), sans
  aucun lien du site SharePoint de la caisse. Les 27 exposés sont servis à la date que le
  registre porte, du 2 octobre 2024 au 16 avril 2026. `python scripts/veille_droit.py` :
  rien de changé dans la base.
- *L'écart de 31 à 27.* Le registre porte 31 exposés `a_lire` dont le thème nomme « Avantages
  liés au décès de l'assuré » : les 27 du thème, et quatre de « Mayotte - Législation >
  Avantages liés au décès de l'assuré » — l'allocation de veuvage, l'attribution et le montant
  de la réversion, la pension d'orphelin, en législation mahoraise —, que le menu range sous
  Mayotte, et l'ordre de l'étape avec « Mayotte (24) ». Ils restent `a_lire`, avec leur thème.
- *La lecture* : les 27 exposés, en entier. Les 16 de la réversion, par cette session ;
  les 11 de l'allocation de veuvage, de la pension de vieillesse de veuve ou de veuf (Pvv) et
  de la pension d'orphelin, par un agent, dont les 19 citations retenues ici ont été
  retrouvées mot pour mot par script dans le texte servi (19 sur 19). Chacun confronté à la
  fiche `reversion` (ses versions, ses approximations, ses présomptions, ses sources, qui
  citent déjà cinq de ces exposés), à `majoration_exceptionnelle_2023`, à
  `majorations_forfaitaires_1972_1982`, aux limites, et au code des deux moteurs
  (`src/retraite_notionnelle/droit/reversion.py`, `moteur/js/droit/reversion.js`). Les
  barèmes du thème étaient déjà rangés : ceux de l'allocation de veuvage, de la Pvv et de la
  pension d'orphelin `hors_modele`, ceux de la réversion `branche` ou `recoupe`.
- *Le rapprochement de l'index* (LEGI à jour au 5 novembre 2026, JORF au 6). Les exposés
  lient 217 fois Légifrance, vers 112 cibles : 109 identifiants et 3 adresses. 98
  identifiants se trouvent à l'index, et chacun concorde avec son ancre par le numéro de
  l'article (83) ou du texte (15), à une réserve : « Décret 2020/1489 du 02/12/2020 art. 6 »
  mène au « Décret n° 2020-1489 du 1er décembre 2020 » (JORFTEXT000042592528). Des 11
  absents, huit sont hors du champ social de l'index — les articles 171, 184, 201, 331 et 355
  du code civil et le code civil lui-même, l'article 669 du code général des impôts,
  l'ancien L. 900-2 du code du travail — ; deux se trouvent par le numéro : la loi
  n° 2013-404 (JORFTEXT000027414540), le décret n° 82-307 (JORFTEXT000000701321) ; reste le
  décret n° 72-788, que l'index ne porte pas. Les trois adresses : le fac-similé du Journal
  officiel du 16 avril 1971, page 3667, pour le décret n° 71-280, dont la base sert le
  texte (`DEC_71280_07041971`, lu) ; l'adresse ELI du décret n° 2019-1084, que la note de
  H8 a trouvé (JORFTEXT000039281172) ; l'arrêt de la Cour de cassation n° 17-27987, hors de
  l'index.
- *Les sorts*, sous la convention de la note du premier thème. 27 exposés : 25 `limite`,
  et 2 `hors_modele`, les deux exposés de la compétence (la caisse compétente et le régime
  interlocuteur unique de la réversion ; le régime compétent pour l'allocation de veuvage).
  Les exposés d'une prestation que le modèle ne sert pas — l'allocation de veuvage, la Pvv,
  la pension d'orphelin — sont `limite`, renvoyés à la limite neuve, comme H8 l'a fait des
  allocations avant retraite. 14 fenêtres : 10 `hors_modele` — huit définitions du lexique
  (absence, biens mobiliers et immobiliers, nue-propriété, orphelin, personnalité juridique,
  possession d'état, revenu cadastral, usufruit), la liste des personnes tenues à
  l'obligation alimentaire, et `Absence.aspx`, que le complément « Absence » lie sans que la
  base en serve de contenu — ; 4 `limite` : l'absence et la disparition (fiche `reversion`,
  qui ne porte pas la réversion de l'assuré disparu, et la limite), la filiation de
  l'orphelin, la polygamie. 5 listes `limite`, lues en tête, leur sort ne tenant qu'à leur
  nature : les ressources exclues de la réversion, alphabétique et par nature (fiche
  `reversion` et la limite) ; celles de l'allocation de veuvage, les deux, et les situations
  qui donnent la qualité d'assuré veuvage (la limite). Laissées `a_lire` avec leur thème : la
  liste des accords de sécurité sociale et ses 77 listes par pays, celle de l'Espace
  économique européen, et les deux des ressources exclues de l'ASPA (« Allocation du
  minimum »). 5 avis `hors_modele`, comme les autres : 27 (l'aide à la réinsertion des anciens
  migrants, 2016), 123 (le paiement de la réversion garanti en quatre mois, 2016), 199 (le
  régime interlocuteur unique et la Pvv, 2018), 202 (la réversion et la pension d'invalidité
  de veuve ou de veuf, 2014), 231 (la revalorisation d'avril 2017).
- *Les références*, que leurs liens rangent : 197 rangées, 192 `limite` — 95 renvoyées à la
  fiche `reversion` et à la limite, 39 à la limite seule, 28 à la fiche seule, 14 à la limite
  et à la fiche, 16 à la fiche et à `majorations_forfaitaires_1972_1982` (dont 9 avec la
  limite), que lie l'exposé « Montant » — ; 5 `hors_modele`, que ne lie que l'exposé de la
  compétence de la réversion : les circulaires Cnav 32/78 et 33/78, la circulaire
  ministérielle du 4 juin 1998, les lettres Cnav 7/80 du 9 septembre 1980 et du 4 octobre
  1982. 73 déjà rangées dont le renvoi s'étend (ci-dessous) ; 9 qui le portaient déjà
  (circulaires Cnav 31/75, 46/75, 2012/44, 2018/4, 2020/8, 2020/27, 2025/22, ministérielle
  91/70 du 6 décembre 1991, lettre Cnav du 3 septembre 2012) ; 5 autrement rangées, laissées telles (3
  `hors_modele`, la demande et le relevé de carrière ; 2 `limite`, les circulaires Cnav 51/98 et
  2002/71, que ne lient que l'exposé de la compétence et sa fenêtre d'Alsace-Moselle). Restent `a_lire` les 65 que seuls lient des barèmes — les circulaires
  annuelles des montants, de la revalorisation, des plafonds, du SMIC et du taux du livret
  A —, comme les thèmes précédents ont laissé les leurs.
- *Les renvois qui s'étendent* (73 références), de ce qu'y ajoutent les objets qui les lient.
  La fiche `reversion` et la limite (21) : circulaires Cnav 102/83, 105/88, 15/76, 2001/72,
  2006/38, 2010/54 (note technique 3), 2011/80, 2013/51, 2014/39, 2015/13, 2015/45, 2018/31,
  2022/8, 50/99, 60/96, 64/77, 64/98, 79/82, ministérielle 2006/419, lettre Cnav du
  31 octobre 1988, lettre ministérielle 145 AG/88. La fiche seule (45) : circulaires Cnav
  2/72, 8/89, 34/98, 36/87, 52/84, 62/87, 79/89, 82/74, 83/91, 85/74, 98/91, 2001/88,
  2002/56, 2004/20, 2004/22, 2004/29, 2004/38, 2006/66, 2007/15, 2007/17, 2007/47, 2008/41,
  2009/48, 2011/20, 2012/17, 2014/20, 2014/29, 2014/37, 2015/20, 2015/56, 2016/10, 2017/27,
  2018/24, 2019/26, 2021/24, 2024/12, 2024/28, 2025/9, 2025/19, 2026/7, circulaires
  ministérielles 151 du 5 août 1946 et 2002/326, diffusion d'instructions ministérielles
  2005/4, lettre Cnav du 22 octobre 1980, lettre ministérielle 19/68 du 3 septembre 1965. La
  fiche et `majorations_forfaitaires_1972_1982` (4) : circulaires Cnav 49/86, 2012/80,
  ministérielles 143/SS de 1949 et 95/SS de 1992. La limite et la fiche (2) : circulaires
  Cnav 79/81 et 2017/21. `majorations_forfaitaires_1972_1982` et la limite (1) : circulaire
  Cnav 2023/21.
- *La limite* « avantages de survivant » (`docs/limites/3-systeme-actuel.md`), neuve : le
  modèle sert la réversion, et ni l'allocation de veuvage, ni la Pvv, ni la pension
  d'orphelin ; de la réversion, il ne lit ni la disparition, ni l'annulation du mariage, ni
  les épouses simultanées, ni la régularité du séjour, tient pour ressources ce que la saisie
  déclare, et ne calcule pas la fraction mise à la charge d'un régime spécial.

**Ce que la lecture a trouvé, sans écart.** Ce que la fiche `reversion` porte déjà : le taux,
le maximum et la surcote en sus (exposés « Montant » et « Retraite de l'assuré décédé ») ; la
majoration exceptionnelle et celle de la retraite anticipée des handicapés, hors de la base ;
les quatre rédactions de R. 353-7 du point de départ ; le partage entre conjoints et
ex-conjoints, figé à la première réversion ; la majoration de 11,1 % et sa subsidiarité,
présumée ; les ressources de trois ou douze mois, la révision et sa dernière date, la
réversion d'après le 1er janvier 2026 que la retraite d'un cumul emploi-retraite ne révise
plus (décret n° 2025-1409) ; les limites de cumul d'avant juillet 2004 (D. 355-1), et le
désaccord de dates de l'exposé « Retraite de réversion cumulable » que la fiche a déjà dit
(« avant le 01/01/1974 », quand la loi n° 75-3 ouvre le cumul au 1er juillet 1974). Ce que
d'autres notes ont déjà déclaré, que ces exposés touchent : la réversion de l'assuré mort
avant son départ, calculée aux règles de la date d'effet (G11 ; l'exposé : « Avant le
01/07/2011 […] Le salaire annuel moyen était calculé compte tenu des règles en vigueur à la
date du décès ») ; l'ex-conjoint remarié d'avant 2004 (G9) ; les veuves d'un polygame (G12),
dont l'exposé « Nullité du mariage » dit aujourd'hui : « la retraite de réversion peut être
attribuée à chaque conjoint survivant d'un assuré polygame si le mariage n'a pas été annulé
par décision de justice. La retraite est partagée entre le conjoint survivant et le ou les
autres conjoints proportionnellement à la durée respective de chaque mariage » (Cour de
cassation, 20 décembre 2018), quand la lettre Cnav n° 16/84 de G12 servait la réversion
entière à une seule épouse : le point reste non tranché pour les dates d'avant l'arrêt.
L'exposé « Evaluation des ressources » retient au survivant sa propre majoration
exceptionnelle (« La majoration exceptionnelle des retraites (Majex) dont est bénéficiaire le
conjoint survivant est retenue pour l'ouverture du droit et le calcul du montant de la
retraite de réversion ») : le modèle prend les ressources que la saisie déclare (la limite).

**Le registre dit de travers une raison.** Seize références sans thème, dont la loi
n° 80-546, rangées par l'étape 6, portent « l'assurance veuvage, une allocation temporaire au
conjoint survivant de moins de cinquante-cinq ans, supprimée pour les décès depuis 2011 hors
exceptions ». Les exposés servis la disent en vigueur : « L'allocation de veuvage est une
allocation temporaire qui peut être attribuée au conjoint survivant, sous condition de
ressources » ; « Pour les demandes d'allocation déposées à compter du 03/12/2020, le point de
départ est fixé le 1er jour du mois qui comprend le décès ». Le sort `hors_modele` tient ; la
raison est à récrire par la session de l'étape 6, non par celle-ci.

**Un candidat, aux sessions du modèle** (rien n'a été corrigé) : *la durée de mariage de la
réversion d'avant le 18 juillet 1980.* La fiche `reversion` exige, dans ses versions
`avant_1973`, `avant_juillet_1974` et `avant_1982` (date d'effet jusqu'au 1er décembre 1982,
`mariage_minimum_annees: 2`), deux ans de mariage au décès, « sauf enfant issu du mariage »,
des conditions qu'elle dit « prêtées à ce texte d'avant la codification de 1985, telles que
R. 353-1 les codifie en 1985 » (statut `supposee`) ; les deux moteurs lèvent la condition
pour tout enfant déclaré (`_mariage_dure`, `src/retraite_notionnelle/droit/reversion.py`,
lignes 586 à 591 ; `mariageDure`, `moteur/js/droit/reversion.js`, lignes 491 à 493). La base
dit autre chose, pièce par pièce.
- Du 1er mai 1971 au 30 juin 1974. Le décret n° 71-280 du 7 avril 1971, servi par la base,
  récrit L. 351 : « à la condition que le mariage ait été contracté deux ans au moins avant
  l'entrée en jouissance de la pension ou de la rente attribuée à l'assuré décédé ou qu'il
  ait duré au moins quatre ans à la date du décès » ; il prend effet « à compter du premier
  jour du mois suivant la date de sa publication » (article 4), au Journal officiel du
  16 avril 1971. L'exposé « Conditions d'attribution » : « Avant le 01/07/1974 […] au moins
  2 ans avant le point de départ de la retraite attribuée à l'assuré décédé ; ou au moins
  4 ans à la date du décès ». Aucun enfant n'y lève rien. *Cas posé* : l'assuré retraité au
  1er janvier 1970, marié le 1er juin 1970, mort le 1er mars 1973 ; sa veuve a soixante ans,
  sans ressources, sans enfant du mariage. Le mariage, contracté après l'entrée en jouissance,
  a duré deux ans et neuf mois : le décret refuse la réversion. Le modèle (version
  `avant_juillet_1974`, deux ans au décès) la sert : la moitié de la pension du défunt, contre
  rien. Ici la lecture contraire est intenable : le texte est lu, et il est clair.
- Du 1er juillet 1974 au 17 juillet 1980. La lettre ministérielle n° 1448/AG/79 du
  17 janvier 1980, servie par la base : « la pension de réversion ne peut être attribuée que
  si le conjoint survivant était marié depuis au moins 2 ans à la date du décès ou de la
  disparition de l'assuré », pour toute réversion « avec effet postérieurement au 30 juin
  1974 ». L'exposé : « Avant le 18/07/1980 […] Le mariage devait avoir duré au moins 2 ans même
  si un enfant était issu du mariage. » À l'index LEGI, l'exception n'apparaît qu'avec
  l'article 81 a du décret n° 45-179 dans sa rédaction du 12 mars 1981
  (LEGIARTI000006760629 : « sauf si un enfant au moins est issu du mariage »), et, au régime
  agricole, avec l'article 1122-2-1 de l'ancien code rural, en vigueur au 18 juillet 1980
  (LEGIARTI000006581041 : la condition « n'est pas exigée […] lorsqu'un enfant au moins est
  issu du mariage »). *Cas posé* : l'assuré retraité, marié le 1er mars 1977, un enfant né du
  mariage en 1978, mort le 10 juin 1978 ; sa veuve a cinquante-huit ans, sans ressources, et
  demande dans l'année. Mariée un an et trois mois : la caisse refuse ; le modèle (version
  `avant_1982`) sert la réversion, 50 % de la pension principale du défunt — sur une pension
  de 12 000 F par an, 6 000 F par an, contre rien. Ce que le texte ne tranche pas encore :
  L. 351 du code de 1956 et l'article 81 a d'avant le 12 mars 1981 ne sont ni à l'index ni
  dans la base. Deux pièces de la base et la date du code rural disent la lecture de la
  caisse ; aucune ne dit celle du modèle, qui n'est qu'une hypothèse. Question au
  propriétaire : où lire le texte de 1975 à 1980 ?
- Avant le 1er mai 1971, le décret n° 71-280 cite la rédaction qu'il remplace : « à la
  condition que le mariage ait été contracté avant que celui - ci ait atteint l'âge de soixante
  ans et que, dans le cas où l'intéressé a demandé la liquidation de ses droits avant l'âge de
  soixante - cinq ans, il ait duré au moins deux ans avant l'attribution de la pension ou
  rente ». La version `avant_1973` la prête aussi à 1985 ; à lire avec le candidat de G9 sur
  l'assuré mort avant soixante ans.

**Ce que la base sert de travers.** « Décret 2020/1489 du 02/12/2020 », pour le décret du
1er décembre 2020 ; « Circulaire Cnav 2018/4 du 01/02/218 », deux fois ; « Lettre Cnav du
09/09/1980/a> » et « Circulaire Cnav 2002/71 du 31/12/2002/a> », un reste de balise ;
« Circulaire Cnav 2005/17 du 17/04/2005 », une fois, pour celle du 11 avril.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
servie, aucun test n'a été changé ; le registre seul, en ses colonnes `sort` et `renvoi`, et
la limite neuve. Les références prennent les renvois des objets qui les lient, sans ceux des
fiches qui les citent par leur numéro. Les listes de ressources exclues sont lues en tête, non
ligne à ligne. Aucun fichier d'une autre file n'a été changé.
