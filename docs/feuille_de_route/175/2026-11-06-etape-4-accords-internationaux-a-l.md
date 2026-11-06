# Étape 4, thème « Accords internationaux et d'outre-mer », sous-thème « Accords internationaux », première moitié (« Anciens accords » à « Kosovo ») : les exposés et leurs références

**Le 6 novembre 2026, ce qui est fait.**

- *La relecture de la base.* Par l'API, le 6 novembre 2026 à 14 h 42 UTC (`/expose`, `/liste`,
  `/mises-a-jour`, les collections des fenêtres), puis deux références par `_reference`
  (circulaires ministérielles 99/48 et 2002/234), par les fonctions de
  `scripts/fetch/cnav_legislation.py`, sans écrire le registre par le script. Les 109 exposés
  sont servis à la date que le registre porte (`dateModification`, du 24 octobre 2025 au
  12 août 2026, vérifié par script) ; s'y ajoute « Allocation de veuvage - Canada », que le
  registre range sans thème et que lie l'exposé commun de l'allocation de veuvage.
- *La lecture*, en entier. Par cette session : les 8 règles communes moins l'instruction (7),
  l'accord intérimaire européen, et de chaque pays les calculs de la retraite personnelle et de
  réversion, l'allocation de veuvage, l'arrangement andorran de 1970, l'accord canadien de 1979,
  le recours au régime unique (Côte-d'Ivoire, Gabon), la Bosnie-Herzégovine, le Brésil et le
  Kosovo (55 exposés) ; les 39 listes. Par un agent (Sonnet), dans un contexte à lui : les 21
  « Anciens accords », les 16 champs d'application des pays et les 18 instructions de la demande
  (55 exposés) ; ses 895 citations, mot pour mot, vérifiées par script dans le texte servi, sauf
  trois qui ne sont que des titres ou une ellipse. Chaque date d'entrée en vigueur, relevée par
  script dans le texte servi, confrontée au tableau `legislation/accords_internationaux.yaml` ;
  le reste, aux fiches `totalisation_des_periodes_etrangeres`, `pension_proratisee`,
  `minimum_contributif_international` et `reversion`, et au code : `coordonner_les_periodes`
  (`src/retraite_notionnelle/droit/etranger.py:111`), où une convention ne coordonne que le
  régime général (`etranger.py:146`, et `moteur/js/droit/etranger.js:117`) et où seuls
  `comparaison` et `option` comparent deux pensions (`CALCULS_COMPARES`, `etranger.py:66`,
  `etranger.js:55`) — `non_lu` et `calcul_separe` comptent les périodes pour le taux de la seule
  pension nationale — ; la réversion, sans le minimum contributif (`MINIMA_REVERSES`,
  `droit/reversion.py:241`).
- *Le rapprochement de l'index*, LEGI à jour au 2 novembre 2026 et JORF au 3. 55 exposés lient
  Légifrance 83 fois, sous 54 identifiants. 47 sont à l'index, chacun concordant par son
  numéro (43 articles de code, en vigueur à leur date) ou par son titre (décrets de
  publication). 7 sont absents : l'article 2224 du code civil, hors du champ social ; l'arrêt de
  la Cour de cassation n° 17-27987 ; le « Décret du 31/07/1950 » (Luxembourg), les décrets
  n° 61-1055 (Pologne), n° 49-1000 (Tchécoslovaquie) et n° 2013-349 (Kosovo), absents par leur
  identifiant. Les décrets d'avant 1960, à l'index sans leur texte, ne se lisent qu'au
  fac-similé (`docs/feuille_de_route/138/2026-11-05-la-file-des-fac-similes.md`). Les dates
  d'effet que les textes portent concordent avec les exposés et le tableau : Algérie, « est
  entrée en vigueur le 1er février 1982 » (décret n° 82-166) ; Argentine, « entre en vigueur le
  1er novembre 2012 » (n° 2012-1177) ; Bénin, 1er septembre 1981 (n° 81-832) ; Brésil, « est
  entré en vigueur le 1er septembre 2014 » (n° 2014-1013) ; Cameroun, 1er mars 1992
  (n° 92-223) ; Canada, 1er mars 1981 (n° 81-353) ; Cap-Vert, 1er avril 1983 (nota du décret
  n° 83-509) ; Côte-d'Ivoire, 1er janvier 1987, et Gabon, 1er février 1983 (notices JORF des
  décrets n° 87-123 et 83-633) ; Inde, 1er juillet 2011 (n° 2011-599) ; Suède, 1er août 1981
  (n° 81-777) ; bateliers rhénans, « entré en vigueur le 1er décembre 1987 » (n° 90-131) ;
  Slovaquie, 7 août 1996, et République tchèque, 19 juin 1995 (n° 98-845 et 98-846). Les
  décrets de la Corée et du Japon (n° 2007-1021 et 2007-1020), d'Israël (n° 66-784), de la
  Croatie, de la Slovénie, de la Bosnie-Herzégovine et du Kosovo (n° 96-711, 96-229, 2004-96,
  2003-457) ne disent pas la date. Hors de Légifrance : le CLEISS (accord avec le Canada,
  formulaires) et ameli.fr, non lus.
- *Les sorts*, sous la convention de la note du premier thème. 110 exposés : 92 `limite` — les
  champs d'application et les anciens accords au tableau, à la totalisation et à la limite ;
  les calculs de la retraite personnelle aux trois fiches de la coordination et au tableau ; les
  réversions à `reversion` et `pension_proratisee`, et à la limite quand elles disent la
  polygamie ou le non-cumul ; le minimum à `minimum_contributif_international` ; le point de
  départ au tableau ; l'allocation de veuvage, la polygamie, le régime unique et les bateliers
  rhénans à la limite neuve —, 18 `hors_modele`, les instructions de la demande, une procédure.
  39 listes `limite`, au tableau et à la totalisation : la liste « Accords de sécurité sociale
  avec la France », et les listes « Accord de sécurité sociale - <pays> » des 18 pays de cette
  moitié et des 20 États de ses anciens accords (Allemagne à Suisse, et l'ex-Tchécoslovaquie).
  La fenêtre « formulaire de liaison » `hors_modele`, définition du lexique ; l'avis 10 (le
  Brésil, 2015) `hors_modele`. Restent tels les objets d'autres thèmes que ces exposés lient
  (dont `lura_ex.aspx` et le paiement, `a_lire`), et les exposés de l'autre moitié qu'ils lient.
- *Les références*, toutes celles que lient ces exposés (239). 192 `a_lire` sont rangées : 168
  `limite`, aux renvois des exposés qui les lient ; 24 `hors_modele`, que seules lient les
  instructions de la demande : les arrangements administratifs (Algérie, Bénin, Cap-Vert, Chili,
  Gabon, Inde, Japon, bateliers rhénans), les circulaires Cnav 119/89, 124/85, 2007/18,
  2010/32, 2020/17, 32/90, 44/91, 63/94, 72/95, 75/92, 81/98, 88/90, la note d'information
  ministérielle 90/19, la lettre de la caisse des travailleurs migrants du 30 septembre 1983.
  37 sont liées aussi par l'autre moitié ; je les range. Deux `hors_modele` restent telles,
  quoiqu'un exposé `limite` d'ici les lie : la circulaire Cnav 2010/54 entière et l'annexe 6
  du règlement n° 1408/71.
- *Les renvois qui s'étendent* (29 références), l'ancien renvoi en tête : + totalisation et
  tableau : accord complémentaire n° 4 du 10 juillet 1950 (Allemagne), circulaire ministérielle
  63/SS, convention avec la Mauritanie du 22 juillet 1965, annexe 2 de la circulaire Cnav
  2014/2 ; + `reversion` : circulaires Cnav 101/83, 1/88, 2014/2, lettre ministérielle du
  21 novembre 1985 ; + `pension_proratisee` : circulaires Cnav 102/83, 105/90, 120/82,
  2008/14, 31/75, 31/95, 43/84, 46/75, lettre ministérielle du 21 septembre 1983 ; +
  `minimum_contributif_international`, tableau et limite : 117/83 ; + tableau et limite :
  2004/8 ; + `pension_proratisee`, totalisation et tableau : 2011/80, 2013/51 ; + `reversion`
  et `pension_proratisee` : 76/88 ; + totalisation, tableau et limite : convention de New York
  du 28 septembre 1954 ; + les trois fiches et le tableau : lettre ministérielle du 23 octobre
  1962 ; + tableau : article 2 du règlement n° 883/2004, circulaires Cnav 2013/54 et 2017/27 ;
  + les trois fiches, le tableau et `reversion` : 2019/24, 2020/30.
- *La limite* (`docs/limites/3-systeme-actuel.md`), neuve : « accords internationaux ».

**Ce que la lecture a trouvé, sans écart.** Les dates d'entrée en vigueur des 37 champs
d'application et anciens accords sont celles du tableau, État par État. Le mode de calcul des
conventions de cette moitié est celui que le tableau dit : comparaison et prorata limité à la
durée maximum (Andorre, Argentine, Brésil, Canada depuis 2017, Chili, Corée, Gabon, Inde,
Japon : « Cette durée est limitée à la durée d'assurance maximum retenue au régime général ») ;
calcul séparé prioritaire (Algérie depuis 1982, Bénin, Cameroun, Cap-Vert, Congo,
Côte-d'Ivoire) ; option (Israël ; la convention franco-yougoslave, « dans la limite de 150
trimestres », circulaire ministérielle 2002/234). Le Canada de 1979 « donnait priorité à
l'attribution séparée », ce que `non_lu` sert de même. La règle commune : la durée du taux
« comprend les trimestres validés par les régimes étrangers visés par la convention et par les
régimes de base français », les périodes d'activité d'avant le 1er avril 1983 « retenues au
titre de périodes équivalentes », la séparée comptant les périodes étrangères « pour le taux » (`Durees.pour_le_taux`).
Le minimum de la proratisée, réduit sur la durée totale non limitée, est celui de la fiche.
La réversion : « Les avantages complémentaires et le minimum contributif sont négligés »
(lettre ministérielle du 21 septembre 1983), ce que fait `MINIMA_REVERSES` ; le montant du
défunt « retenu même s'il dépasse le maximum », que la réversion du régime général reprend.
Déjà connus, que ces exposés touchent : la règle d'une année (règlement n° 883/2004, article
57), qu'ont aussi l'Argentine, le Canada de 2013, l'Inde et le Japon (« Si la durée d'assurance
en France est inférieure à 1 an, seule la retraite nationale est calculée ») ; les agents
publics algériens et la Bosnie-Herzégovine de 1998 (G15) ; un seul accord à la fois, quand
l'accord tripartite France–Pays-Bas–Pologne et les États tiers des conventions totalisent
plus ; la nationalité, qui ouvre la plupart des conventions et l'accord intérimaire ; le
prorata limité pour toute convention qui compare (`pension_proratisee`).

**Trois candidats, aux sessions du modèle** (rien n'a été corrigé). Cas posé commun : assuré
né en 1939, départ à soixante ans le 1er juin 1999, 120 trimestres au régime général (1959-1988)
et 36 dans l'autre État (1990-1998), salaire annuel moyen 15 000 € ; durée du taux plein, 156
trimestres (`legislation/duree_assurance_requise.csv`) ; durée maximum, 150
(`duree_proratisation.csv`) ; minoration, 0,025 par trimestre manquant
(`coefficient_minoration.csv`) ; âge du taux plein, soixante-cinq ans. Avec les 36 trimestres
pour le taux : 156, taux plein, 15 000 × 50 % × 120 / 150 = 6 000 € par an (la proratisée
limitée vaut autant : 15 000 × 50 % × 150 / 150 × 120 / 150). Sans eux : min(156 − 120,
(65 − 60) × 4) = 20 trimestres, taux 50 % × (1 − 0,025 × 20) = 25 %, 15 000 × 25 % × 120 / 150
= 3 000 € par an, sans minimum contributif, faute du taux plein.

1. *La République fédérale de Yougoslavie, du 29 janvier 1999 au 17 avril 2002.* L'exposé
   « Kosovo » : « Du 29/01/1999 au 17/04/2002 [...] la convention générale du 05/01/1950 ne
   s'appliquait plus. Seule la législation nationale était applicable. » La circulaire
   ministérielle 99/48, relue par l'API, qui vise les « ressortissants de la République
   fédérale de Yougoslavie (Serbie, Monténégro, Voïvodine et Kosovo) » : « la liquidation des
   pensions de vieillesse [...] devra désormais être faite de façon séparée, c'est à dire sans
   qu'il y ait lieu de faire appel aux périodes d'assurance accomplies en Yougoslavie » ; la
   circulaire 2002/234, qui l'abroge : « les pensions attribuées sur la base des instructions de
   la circulaire DSS/DAEI/99/48 du 29 janvier 1999 doivent pouvoir être révisées à la demande
   des assurés », sans date de révision. Le tableau sert la convention à la Serbie, au
   Monténégro et au Kosovo (RS, ME, XK) depuis 1951 sans interruption. Au cas posé, la
   période dans l'un d'eux : le modèle sert 6 000 €, la caisse liquidait 3 000 €, jusqu'à une
   révision demandée. (Les exposés de la Serbie et du Monténégro sont à la seconde moitié.)
2. *L'arrangement franco-andorran du 9 juin 1970, absent du tableau.* L'exposé « Arrangement
   du 09/06/1970 - Andorre » : « Avant le 01/06/2003, les retraites étaient calculées en
   application de l'arrangement général du 09/06/1970 » ; régime général, salariés agricoles,
   régimes spéciaux ; « L'assuré choisissait entre le calcul séparé par chaque législation et
   l'attribution par totalisation-proratisation de sa retraite » ; la liste de l'Andorre : les
   arrangements « avaient pris effet le 10/06/1970 ». Le tableau n'y porte que la convention de
   2003 : de 1983 à mai 2003, une période en Andorre ne compte pas. Au cas posé, la période en
   Andorre : le modèle sert 3 000 €, la caisse 6 000 € (calcul séparé, les périodes andorranes
   pour le taux, règle commune). L'index du JORF ne porte aucun texte publiant l'arrangement
   (titres « andorre », jusqu'en 2004).
3. *La convention franco-roumaine (1978-2006) ne compte pas les périodes roumaines.* L'exposé
   « Champ d'application - Roumanie » : « La convention franco-roumaine prévoyait la totalisation
   des périodes accomplies dans les 2 pays uniquement pour l'ouverture des droits », « Le droit à
   retraite personnelle au régime général était ouvert sans condition de durée d'assurance »,
   « Seules les périodes accomplies dans les régimes de base français étaient retenues ». Le
   tableau la dit `non_lu`, que le modèle sert en calcul séparé : les périodes roumaines
   comptent pour le taux. Au cas posé, la période en Roumanie : le modèle sert 6 000 €, la
   caisse 3 000 €.

**Un point non tranché, aux sessions du modèle** : *les fonctionnaires sous une convention
qui vise les régimes spéciaux.* L'accord avec le Brésil, lu au JO (décret n° 2014-1013,
article 2, 1, B, a), s'applique « aux législations relatives aux régimes de sécurité sociale
généraux et spéciaux, obligatoires et volontaires » ; R. 711-1, 1°, range parmi les régimes
spéciaux ceux des « fonctionnaires, les magistrats et les ouvriers de l'Etat ». Les exposés
de l'Argentine (« aux régimes spéciaux de sécurité sociale »), de l'Andorre et de l'Inde
(« sauf dispositions contraires »), de la Roumanie et de la Suisse nomment de même les régimes
spéciaux sans exclure les fonctionnaires, quand ceux de l'Espagne, du Bénin, du Canada, du
Chili, du Congo, de la Corée, de la Côte-d'Ivoire, du Gabon et du Japon les excluent. Le modèle
ne compte les périodes d'une convention que pour le régime général (`etranger.py:146`).
Lectures : la convention couvre leur régime, et les trimestres brésiliens comptent dans la
décote du fonctionnaire ; ou une disposition contraire de l'accord, que ni l'exposé ni le
décret lus ne citent, l'écarte. Cas posé (celui de H14) : fonctionnaire de l'État né en 1960,
120 trimestres de services et 40 au Brésil, parti à soixante-deux ans en 2022 sur 30 000 € ;
durée requise 167, annulation de la décote à soixante-sept ans ; 30 000 × 75 % × 120 / 167 =
16 167,66 € ; avec les trimestres brésiliens, décote de 7 trimestres, 8,75 %, 14 752,99 € ;
sans eux, de 20, 25 %, 12 125,75 € ; écart 2 627,24 € par an.

**Lu, à confronter au modèle, sans cas posé.** Les conventions d'avant l'Union que le tableau
dit `non_lu` disent leur calcul : totalisation-proratisation (Autriche, « par
totalisation-proratisation » ; Norvège ; Tchécoslovaquie, avec la séparée « si l'assuré avait
l'âge de la retraite à taux plein ») ; Pologne, totalisation, puis « Depuis le 01/07/1993, la
retraite nationale [...] est comparée à la retraite proratisée », la durée « limitée à la durée
d'assurance maximum » ; Suède et Suisse, calcul séparé prioritaire ; Algérie de 1965 à 1982,
« recours obligatoire à la totalisation proratisation ». La pension proratisée limitée vaut la
séparée du modèle ; le minimum proratisé, réduit sur la durée totale non limitée, peut être
moindre que celui de L. 351-10 que le modèle sert à une séparée quand la durée totale dépasse la
durée maximum (`minimum_contributif_international.yaml:82`), ce que je n'ai pas chiffré.

**Ce que la base sert de travers.** Des listes « Accord de sécurité sociale - <pays> »
contredisent l'exposé du même pays : Gabon, « 01/07/1988 » (l'exposé et le décret : 1er
février 1983) ; Israël, « 01/01/1966 » (l'exposé : « le 01/10/1966 ») ; Norvège, « avait pris
effet le 01/11/1974 » (l'exposé : « le 01/07/1956 ») ; Suisse, « au 01/01/1976 » (l'exposé :
« le 01/11/1976 ») ; Pologne, « le 01/03/1947 » (l'exposé : « le 01/03/1949 ») ; Espagne, le
règlement n° 1408/71 au « 01/04/1973 » (l'exposé : « Depuis le 01/01/1986 ») ; Bénin, « La
précédente convention avait pris effet le 01/05/1965 », que l'exposé ne dit pas. L'exposé du
Brésil date l'accord « signé le 15/11/2011 », que le décret dit « signé à Brasilia le
15 décembre 2011 », comme le tableau ; celui du Kosovo écrit la convention « du 04/01/1950 »,
puis « du 05/01/1950 » ; celui de la Roumanie, « ne s'applique plus depuis cette date », sans
date. Douze liens « organisme_liaison_<pays>_list.aspx » des anciens accords mènent à des
listes que la base ne sert pas. La liste de l'Algérie date la convention de 1965 au « 01/05/1965 »,
quand le tableau la date, faute de mieux, de sa publication (19 mai 1965, `date_lue: false`) :
sans effet, le modèle ne comptant aucune période étrangère avant le 1er avril 1983.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
servie, aucun test n'a été changé ; le registre seul, en ses colonnes `sort` et `renvoi`, et la
limite neuve. Les conventions, leurs arrangements et les circulaires que lient ces exposés ne
sont pas relus en entier, hors des deux circulaires ministérielles de la Yougoslavie et de
l'article 2 de l'accord avec le Brésil. Les 20 listes « Accord de sécurité sociale » de pays
sans exposé du sous-thème (Aurigny, Bulgarie, Chypre, Estonie, Finlande, Guernesey, Herm,
Hongrie, Irlande, Islande, Jersey, Jethou, Lettonie, Liechtenstein, Lituanie, Malte, Mayotte,
Nouvelle-Calédonie, Polynésie, Saint-Pierre-et-Miquelon) restent `a_lire`.
