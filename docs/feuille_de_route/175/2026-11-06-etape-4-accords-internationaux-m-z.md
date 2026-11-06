# Étape 4, thème « Accords internationaux et d'outre-mer », sous-thème « Accords internationaux », seconde moitié (« Macédoine du Nord » à « États-Unis ») et les listes de pays sans exposé : les exposés et leurs références

**Reprise, au 6 novembre 2026.** « Retraite personnelle de base », les huit thèmes de
« Carrière », « Avantages liés au décès de l'assuré », « Allocation du minimum », « RCI »,
« Anciennes prestations », « Régimes intégrés » et, d'« Accords internationaux et d'outre-mer »,
« Règlements européens », « Accords d'outre-mer » et « Accords internationaux » en entier (sa
seconde moitié et les 20 listes de pays sans exposé, cette note, H16) sont rangés. Suivant :
« Mayotte », avec les quatre exposés mahorais du décès. Base relue par l'API hors de 5 h–6 h
UTC. Aux sessions du modèle : le point non tranché de cette note (les fonctionnaires sous les
conventions du Maroc, du Québec, de l'Uruguay, du Royaume-Uni et de Saint-Marin), ceux de H15 à
H8, des thèmes d'avant, H6 et H7. Aux sessions des données : le candidat de H13, et les dates du
tableau que cette note dit.

**Le 6 novembre 2026, ce qui est fait.**

- *La relecture de la base.* Par l'API, le 6 novembre 2026 à 15 h 08 UTC (`/expose`, `/liste`,
  `/mises-a-jour`, les collections des fenêtres), puis la circulaire Cnav 2007/79 par
  `_reference` (15 h 19), par les fonctions de `scripts/fetch/cnav_legislation.py`, sans écrire
  le registre par le script. Les 75 exposés sont servis à la date que le registre porte
  (`dateModification`, du 24 octobre 2025 au 11 juin 2026, vérifié par script).
  `python scripts/veille_droit.py` : rien de changé dans ce sous-thème.
- *La lecture*, en entier. Par cette session : les calculs de la retraite personnelle (17, dont
  la Serbie et l'Uruguay) et de réversion (17, dont l'avantage lié au décès de la Serbie et la
  réversion de l'Uruguay), la Macédoine du Nord, le Monténégro, la Serbie, l'Uruguay, la
  convention marocaine de 1965, l'entente québécoise de 1979, l'accord tunisien de 1975, le
  recours malien au régime unique, l'allocation de veuvage uruguayenne (43 exposés) ; les 39
  listes. Par un agent (Sonnet), dans un contexte à lui : les 15 champs d'application et les 17
  instructions de la demande (32 exposés) ; ses 389 citations, mot pour mot, toutes vérifiées
  par script dans le texte servi ; les passages qui décident (régimes du Maroc et du Québec,
  conventions maliennes et sénégalaises de 1965, îles anglo-normandes, option des
  instructions), relus par moi. Chaque date d'entrée en vigueur, relevée par script dans le
  texte servi, confrontée au tableau `legislation/accords_internationaux.yaml` ; le reste, aux
  fiches `totalisation_des_periodes_etrangeres`, `pension_proratisee`,
  `minimum_contributif_international` et `reversion`, et au code : `coordonner_les_periodes`
  (`src/retraite_notionnelle/droit/etranger.py:111`), qui ne compte aucune période étrangère
  pour une pension prise avant le 1er avril 1983 (`etranger.py:119`), compte l'activité d'avant
  cette date pour équivalente quand aucun accord ne la fait compter (`etranger.py:149`), ne
  coordonne par une convention que le régime général (`etranger.py:146`,
  `moteur/js/droit/etranger.js:117`), et compare les deux pensions d'une `option` comme d'une
  `comparaison` (`CALCULS_COMPARES`, `etranger.py:66`, `etranger.js:55`).
- *Le rapprochement de l'index*, LEGI à jour au 2 novembre 2026 et JORF au 3. 33 exposés lient
  Légifrance 55 fois : 25 identifiants, tous à l'index, et un fac-similé du JO (décret
  n° 76-1072, Sénégal), non lu (`docs/feuille_de_route/138/2026-11-05-la-file-des-fac-similes.md`).
  Trois articles du code de la sécurité sociale (L. 341-15, dont le lien vise la version close
  le 1er septembre 2023 ; L. 353-3 ; L. 356-1) ; 22 décrets de publication, chacun concordant
  par son titre ou son texte (le n° 67-111, que l'index intitule « RECHERCHE HISTORIQUE,
  RECHERCHE AGRONOMIQUE », est « PORTANT PUBLICATION DE LA CONVENTION DE SECURITE SOCIALE ET DES
  TROIS PROTOCOLES ANNEXES SIGNES LE 22 JUILLET 1965 ENTRE LA FRANCE ET LA MAURITANIE »). Les
  dates d'effet que les textes portent concordent avec les exposés et le tableau : Mali,
  « ENTREE EN VIGUEUR: 01-06-1983 » (n° 83-577) ; Maroc, « Le présent accord entrera en vigueur
  le 1er juin 2011 » (n° 2011-567) ; Québec, « La présente entente est entrée en vigueur le
  1er novembre 1981 » (n° 81-1043) ; États-Unis, « en vigueur le 1er juillet 1988 »
  (n° 88-610) ; Serbie, « Entrée en vigueur : 1er décembre 2023 » (n° 2023-994) ; Macédoine du
  Nord, l'échange de lettres, « ENTREE EN VIGUEUR: 14-12-1995 » (n° 96-726) ; Niger, les
  formalités accomplies « par la partie française le 10 août 1974 » (n° 75-84), sans la date
  d'effet. Les autres ne la disent pas ; ceux de Saint-Marin, Monaco, la Yougoslavie (d'avant
  1960), du Togo et de l'avenant nigérien sont à l'index sans leur texte.
- *Les sorts*, sous la convention de la note du premier thème. 75 exposés : 58 `limite` — les
  15 champs d'application, la Macédoine du Nord, le Monténégro, la Serbie, l'Uruguay et les
  trois anciens accords (Maroc 1965, Québec 1979, Tunisie 1975) à la totalisation, au tableau et
  à la limite (22) ; les calculs de la retraite personnelle aux trois fiches de la coordination
  et au tableau (17) ; les réversions à `reversion` et `pension_proratisee` (17), et à la limite
  quand elles disent la polygamie (Mali, Maroc, Mauritanie, Niger, Sénégal, Togo, Tunisie), le
  non-cumul (États-Unis, Uruguay) ou l'allocation de veuvage (Serbie) ; le régime unique malien
  et l'allocation de veuvage uruguayenne à la limite (2) —, 17 `hors_modele`, les instructions
  de la demande, une procédure. Neuf rappellent le mode de calcul de leur pays (Mali, Niger,
  Sénégal, Togo, Yougoslavie, Turquie, Philippines, Royaume-Uni, Uruguay) ; leur raison le dit
  et renvoie à l'exposé du calcul, qui porte le renvoi. 39 listes `limite` : les 19 « Accord de
  sécurité sociale - <pays> » de cette moitié et les 16 des pays sans exposé de l'Union, de
  l'Espace économique européen et des îles anglo-normandes (Aurigny, Guernesey, Herm, Jersey,
  Jethou), au tableau et à la totalisation ; celles de Mayotte, de la Nouvelle-Calédonie, de la
  Polynésie et de Saint-Pierre-et-Miquelon, à la fiche de leur régime, à la totalisation et à la
  limite, comme H14 a rangé leurs exposés. La fenêtre « Libératoire » `hors_modele`, définition
  du lexique (« Qui libère d'une dette, d'un engagement. ») ; l'avis 297 (la Serbie, 15 juillet
  2024) `hors_modele`. Restent tels les objets d'autres thèmes que ces exposés lient
  (`lura_ex.aspx` et le traitement des données personnelles, `a_lire`).
- *Les références*, toutes celles que lient ces exposés (126). 85 `a_lire` sont rangées : 69
  `limite`, aux renvois des exposés qui les lient ; 16 `hors_modele`, que seules lient les
  instructions de la demande : sept arrangements administratifs (Philippines, Turquie, Québec de
  2003 et 2004, Sénégal, Togo, Tunisie), les circulaires Cnav 2002/53, 41/91, 56/89, 85/92,
  91/93, 2012/46, la circulaire ministérielle 59/SS du 24 août 1978, les lettres ministérielles
  du 17 juillet 1990 et n° 4 du 22 janvier 1990. Les 41 autres étaient déjà `limite`.
- *Les renvois qui s'étendent* (12 références), l'ancien renvoi en tête : + `pension_proratisee`
  et `minimum_contributif_international` : circulaires Cnav 2002/41 et 2014/25 ; +
  `pension_proratisee` : 2006/38 ; + `pension_proratisee`, totalisation,
  `minimum_contributif_international`, tableau et `reversion` : 2011/78, conventions du
  7 décembre 1971 (Togo) et du 28 mars 1973 (Niger) ; + `pension_proratisee` et `reversion` :
  61/98 ; + totalisation et tableau : 76/88, circulaire ministérielle 91/70 ; +
  `pension_proratisee`, `minimum_contributif_international` et `reversion` : convention du
  22 juillet 1965 (Mauritanie) ; + tableau : échange de lettres des 10 et 24 mai 1968
  (États-Unis) ; + `pension_proratisee`, totalisation, `minimum_contributif_international` et
  tableau : 2017/21.
- *La limite* (`docs/limites/3-systeme-actuel.md`, « accords internationaux ») s'étend : la
  réversion d'un polygame réservée, sous la convention tunisienne de 2003, à « l'épouse qui a
  obtenu la 1re le bénéfice des prestations d'assurance maladie » ; le régime unique malien ;
  la carrière yougoslave, totalisée « quand les périodes accomplies dans les territoires de
  l'ex-Yougoslavie sont attestées » ; la Turquie, où « Seules
  les périodes de travail accomplies en Turquie à partir du 01/04/1950 sont considérées comme
  des périodes d'assurance ». Elle vaut jusqu'à « États-Unis ».

**Ce que la lecture a trouvé, sans écart.** Les dates d'entrée en vigueur des champs
d'application, des exposés de la Macédoine du Nord, de la Serbie, de l'Uruguay et des anciens
accords sont celles du tableau, État par État : Mali, 1er juin 1983 ; Maroc, 1er janvier 1967,
l'avenant du 21 mai 1979 au 1er avril 1981, la convention de 2007 au 1er juin 2011 ; Mauritanie,
1er février 1967 ; Monaco, 1er avril 1954 ; Niger, 1er novembre 1974 ; Philippines, 1er novembre
1994 ; Québec, 1er novembre 1981 et 1er décembre 2006 ; Royaume-Uni, 1er mai 1958, les
règlements du 1er avril 1973 au 1er janvier 2021 ; Saint-Marin, 1er janvier 1951 ; Sénégal,
1er septembre 1976 ; Serbie, 1er décembre 2023 ; Togo, 1er juillet 1973 ; Tunisie, 1er avril
2007 ; Turquie, 1er août 1973 ; Uruguay, 1er juillet 2014 ; Yougoslavie, 1er avril 1951. Les
listes de l'Union et de l'Espace économique datent le règlement n° 1408/71 comme le tableau
(Bulgarie, 2007 ; Chypre, Estonie, Hongrie, Lettonie, Lituanie, Malte, 1er mai 2004 ; Finlande
et Islande, 1er janvier 1994 ; Irlande, 1er avril 1973 ; Liechtenstein, 1er mai 1995). Le mode de
calcul est celui du tableau : comparaison et prorata limité (Maroc 2007, Québec 2003, Serbie
2014, Tunisie 2003, Uruguay : « Cette durée est limitée à la durée d'assurance maximum retenue au
régime général ») ; calcul séparé prioritaire (Monaco, Philippines, Sénégal, Turquie,
États-Unis : « donne priorité à l'attribution séparée ») ; option (Mali, Mauritanie, Niger,
Saint-Marin, Togo, Royaume-Uni de 1956, Yougoslavie), que le modèle compare et dont il sert la
plus élevée, comme le disent les instructions du Mali, du Niger et du Sénégal : « Passé ce
délai, le demandeur est supposé avoir choisi le mode de calcul qui lui est le plus favorable ».
Les options d'avant (Sénégal avant le 1er juin 1994, Turquie avant le 1er juillet 1985) et la
priorité séparée du Maroc de 1965 et du Québec de 1979 servent le même montant : la proratisée
limitée vaut la séparée du modèle. Les États tiers : « lié à la France et au Maroc » ;
« lié à chacun des deux États » (Serbie) ; les dix-sept que nomme l'Uruguay, ceux de la liste
que le tableau tient de la circulaire n° 2017/21. Les personnes : les conventions qui ne visent
que les salariés (Mali, Mauritanie, Monaco, Niger, Philippines, Saint-Marin, Sénégal, Togo,
Turquie, Yougoslavie, Royaume-Uni) sont `salaries` au tableau, celles qui visent aussi les non-
salariés (Maroc 2007, Québec, Serbie, Tunisie 2003, Uruguay, États-Unis) `salaries_et_non_salaries`.
La réversion suit le calcul de la retraite personnelle, celle du défunt qui ne l'avait pas
demandée « calculée selon les dispositions de la convention en vigueur au point de départ de la
retraite de réversion », ce que `reversion` reprend. Déjà connus, que ces exposés touchent : la
convention franco-yougoslave suspendue du 29 janvier 1999 au 17 avril 2002 (H15), que les exposés
du Monténégro et de la Serbie disent aussi (« Seule la législation nationale était
applicable ») ; la règle d'une année (règlement n° 883/2004, article 57), « En France, la
retraite personnelle est attribuée séparément si la durée d'assurance [...] est inférieure à
1 an » (Mali, Monaco, Niger, Québec, Sénégal, Togo, Turquie, États-Unis), « seule la retraite
nationale peut être attribuée » (Uruguay), « aucune prestation n'est due par ce pays »
(Mauritanie, Yougoslavie, Tunisie de 1975), six mois au Royaume-Uni de 1956, et la période serbe
ou uruguayenne de moins d'un an que la France retient pour le calcul ; le Québec ouvert aux
non-salariés au 1er août 1989 seulement, quand l'exposé de l'entente de 1979 range sans date
« au régime des non salariés agricoles » et « aux régimes des non salariés non agricoles » dans
son article 2 ; la nationalité, qui ouvre la plupart de ces conventions.

**Le point non tranché de H15 s'étend, aux sessions du modèle** : *les fonctionnaires sous une
convention qui les vise.* L'exposé du Maroc (convention du 22 octobre 2007) : « La convention
s'applique : Pour la France : [...] aux fonctionnaires civils et militaires de l'État, aux
fonctionnaires territoriaux et hospitaliers et aux ouvriers de l'État », et ses régimes, « aux
régimes spéciaux de sécurité sociale » ; « Les régimes de retraites complémentaires sont
exclus », eux seuls. Celui du Québec (entente du 17 décembre 2003) range « aux régimes
spéciaux » sans exclusion ; celui de l'Uruguay : « L'accord s'applique à tous les régimes de
retraite obligatoires ou volontaires ». Ceux du Royaume-Uni (convention de 1956, que le tableau
sert encore à Guernesey et Jersey) et de Saint-Marin rangent les régimes spéciaux et n'en
excluent que les diplomates et le cadre des chancelleries : « Les régimes concernant les agents
diplomatiques et consulaires de carrière sont exclus de la convention. » Les autres excluent
les fonctionnaires, la Serbie de 2014 en toutes lettres (« Sont exclus, les régimes : - des
fonctionnaires civils et militaires »), la Tunisie de 2003, le Maroc de 1965 et le Québec de
1979 de même. Le modèle
ne compte les périodes d'une convention que pour le régime général (`etranger.py:146`).
Lectures : la convention couvre leur régime, et les trimestres marocains comptent dans la décote
du fonctionnaire, comme ceux des règlements depuis 1998 ; ou elle ne totalise que pour les
régimes que ses textes d'application organisent, ce que l'exposé de la Cnav, qui ne dit rien du
service des pensions de l'État, ne tranche pas. Cas posé (celui de H14 et H15, refait) :
fonctionnaire de l'État né en 1960, 120 trimestres de services et 40 au Maroc, parti à
soixante-deux ans en 2022 sur un traitement de 30 000 € ; durée requise 167, annulation de la
décote à soixante-sept ans, 1,25 % par trimestre manquant ; 30 000 × 75 % × 120 / 167 =
16 167,66 € ; avec les trimestres marocains, 160, décote de min(167 − 160, (67 − 62) × 4) = 7
trimestres, 8,75 %, 16 167,66 × 0,9125 = 14 752,99 € ; sans eux, de min(47, 20) = 20, 25 %,
12 125,75 € ; écart 2 627,24 € par an.

**Lu, à confronter au modèle, sans cas posé.** L'accord tunisien de 1975, depuis son avenant du
31 mars 2000 : « Chaque institution calculait la retraite séparément et par
totalisation-proratisation. La retraite la plus avantageuse était attribuée » (circulaire
ministérielle 2000/256), la séparée sur les seules périodes françaises, les périodes tunisiennes
d'avant le 1er avril 1983 « au titre de périodes équivalentes » ; le tableau le dit `non_lu`,
servi en calcul séparé, les périodes tunisiennes pour le taux. La proratisée limitée vaut cette
séparée ; reste le minimum, réduit dans la proratisée, que H15 a laissé non chiffré
(`minimum_contributif_international.yaml:82`). L'exposé se contredit pour l'avant-2000 : « En
attribution séparée, seules les périodes françaises étaient retenues », puis les périodes
tunisiennes « retenues pour calculer le taux de la retraite en attribution séparée et en
totalisation-proratisation » (circulaire Cnav 117/83).

**Des dates du tableau, sans effet sur le modèle**, qui ne compte aucune période étrangère pour
une pension prise avant le 1er avril 1983 : la convention franco-malienne du 11 mars 1965
(« La convention générale de sécurité sociale du 12/06/1979 a abrogé et remplacé la convention
générale et les 3 protocoles signés le 11/03/1965 »), que la liste date du 1er octobre 1966 et
que le tableau ne porte pas, ne jouerait que pour une pension d'avril ou mai 1983, dont les
périodes maliennes d'avant le 1er avril comptent déjà pour équivalentes ; la sénégalaise du
5 mars 1965 (liste : 1er juillet 1966), que le tableau ne porte pas avant le 1er septembre 1976 ;
Jersey, « depuis le 01/05/1958 » à l'exposé et à la liste, le 14 mai 1980 au tableau (CLEISS) ;
Guernesey, Aurigny, Herm et Jethou « depuis le 01/05/1965 », le 1er décembre 1965 au tableau ;
la Tunisie, que le tableau ouvre au 1er janvier 1966 (`date_lue: false`), quand la retraite de
l'accord de 1975 « ne pouvait pas prendre effet avant le 01/06/1977 » et que la liste dit la
convention de 1965 « entrée en vigueur le 01/06/1977 » (le décret n° 66-682 du 15 septembre 1966
la publie, à l'index sans date d'effet).

**Ce que la base sert de travers.** L'exposé tunisien de 2003 prend les États tiers « lié à la
France ou à la Tunisie », quand la circulaire Cnav 2007/79 qu'il cite, relue par l'API, dit
« liés à la France et la Tunisie » (§ 2212) et « lié à la France et à la Tunisie » (§ 232), comme
le tableau. L'exposé de la Macédoine du Nord date les lettres « des 3/12/1995 et 14/12/1995 » ;
le décret n° 96-726 et la référence liée, des 13 et 14 décembre 1995. La circulaire Cnav 2008/26
est « du 28/04/2008 » au calcul québécois, « du 23/04/2008 » ailleurs. La liste de la Serbie ne
porte que la convention franco-yougoslave « 01/04/1951 », non l'accord de 2014 en vigueur le
1er décembre 2023 (exposé, avis 297, décret). Celle de Mayotte date l'accord de coordination du
1er janvier 2003, quand la limite des accords d'outre-mer (H14) date la coordination d'août 2005
(décret n° 2005-1050 du 26 août 2005, dont aucun article à l'index ne dit 2003). Celle de Chypre
date la législation étrangère du « 22/07/1889 ». L'exposé malien date l'arrangement administratif
général du 10 février 1978, avant la convention du 12 juin 1979 qu'il applique ; l'exposé du
Royaume-Uni décrit au présent une convention qui « ne s'applique pas à nouveau depuis le
Brexit ». Le décret n° 77-494, à l'index, vise le décret n° 66-682 publiant la convention
tunisienne « signés [...] le 17 septembre 1965 », que le titre de ce décret date du 17 décembre.
Trois liens « organisme_liaison_<pays>_list.aspx » (Guernesey, Jersey, Serbie) mènent à des
listes que la base ne sert pas.

**Ce que la lecture n'a pas fait.** Aucune règle, aucune fiche, aucune série, aucune valeur
servie, aucun test n'a été changé ; le registre seul, en ses colonnes `sort` et `renvoi`, et la
limite. Les conventions, leurs arrangements et les circulaires que lient ces exposés ne sont pas
relus en entier, hors des paragraphes 2212 et 232 de la circulaire Cnav 2007/79 ; le décret
n° 76-1072, au fac-similé seul ; le CLEISS et ameli.fr, non lus. Aucun candidat neuf : le point
non tranché s'étend, les écarts de date sont sans effet sur le modèle.
