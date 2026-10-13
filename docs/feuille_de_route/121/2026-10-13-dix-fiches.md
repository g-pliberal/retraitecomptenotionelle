# Les dix fiches qui restaient : l'âge et la durée de chacun, texte en main

**Le 13 octobre 2026, les dix fiches, texte en main. Saint-Pierre-et-Miquelon,
Mayotte, la Comédie-Française et les députés lisent leurs âges à la génération,
et leur durée à la génération ou à la date où les conditions sont réunies, dans
les tables que leurs textes écrivent, comme la CRPCEN le faisait déjà ; la
CRPN gagne le dispositif de ses navigants nés avant 1971. La Polynésie et la
Nouvelle-Calédonie, elles, comptent à l'année du départ : leurs périodes
annuelles sont la bonne écriture. Un test balaie toutes les générations de 1920
à 2005 et déclare chaque régime dont la règle change avec l'année du départ ;
il a trouvé la fonction publique, qui rendait 157 trimestres au lieu de 150 au
fonctionnaire dont le droit s'était ouvert avant 2004. Une Saint-Pierraise née
en 1956 partie en 2020 doit 152 trimestres, et non 158 ; une sociétaire de la
Comédie-Française née en 1955 part à soixante ans ; un navigant né en 1965
parti à cinquante-sept ans avec vingt-cinq annuités n'a plus de décote.**

Demande du propriétaire : « Action 121 : reprends à la fiche
cps_saint_pierre_et_miquelon, puis les suivantes, dans l'ordre du bloc. » Et :
« une seule session tient pages.js et index.html. N'y écris pas ; ce qui
devrait s'écrire dans les pages, mets-le dans ta note » — voir « Pour les
pages ».

## Saint-Pierre-et-Miquelon

- *Ce que les textes disent.* Lus dans les index LEGI (incrément du 12 octobre)
  et JORF (du 13 octobre). Avant l'ordonnance n° 2015-896, le décret n° 89-110 :
  60 et 65 ans pour toute génération (article 7), une durée lue à la date
  d'ENTRÉE EN JOUISSANCE — 108 trimestres en 1987, puis 110 et quatre de plus
  par année civile jusqu'à 150 (article 9) —, et le taux « selon les modalités
  définies à l'article R. 351-27 », donc le coefficient par génération que la
  réforme de 2003 y a mis. Depuis l'ordonnance, l'article 5 de la loi n° 87-563
  rend applicables L. 161-17-2, L. 161-17-3 et L. 351-8 en décalant leurs
  dates : dix rédactions de cet article, de LEGIARTI000006757151 à
  LEGIARTI000054477924, et sept de l'article 3 du décret n° 2017-1000, qui adapte
  D. 161-2-1-9. Trois états du droit en sortent :
  - pensions prenant effet au plus tard le 1er juillet 2016 (ordonnance,
    article 4, 3° ; aucun décret n'a avancé cette date) : 60 ans avant 1958, 60
    ans et 4 mois pour 1958, puis 5 mois de plus par génération jusqu'à 62 ans
    pour 1962, taux plein cinq ans au-dessus ; 150 trimestres avant 1956, deux de
    plus par génération jusqu'à 166 pour 1963, 172 à compter de 1973 ;
  - à compter du 1er septembre 2023 (loi n° 2023-1250, article 90, II, 1°, et
    V, A ; décret n° 2025-157 pour D. 161-2-1-9) : trois mois de plus par
    génération de 1963 à 1969, 64 ans à compter de 1970 ; la durée ne change
    pas ;
  - à compter du 1er MARS 2026, et non du 1er septembre comme en métropole
    (loi n° 2025-1403, article 105, IV et VI, relu au Journal officiel) : 62 ans
    et 3 mois et 166 trimestres des nés du 1er janvier 1963 au 30 septembre 1965,
    62 ans et 6 mois et 167 trimestres d'octobre à décembre 1965, puis trois mois
    de plus par génération jusqu'à 64 ans pour 1971, et 172 trimestres à
    compter de 1974. L'ordonnance n° 2026-648 rend aux nés avant 1963, pour les
    mêmes pensions, l'âge de la rédaction d'avant, que la loi de 2025 laissait
    sans réponse pour les nés de septembre 1961 à 1962.
- *Ce qui est écrit.* Les tables `spm_2015`, `spm_2023` et `spm_2026` de
  `legislation/ages_regimes.csv`, `spm_2015` et `spm_2026` de
  `legislation/duree_requise_regimes_speciaux.csv`, dont la colonne `depuis` ne
  borne rien : c'est la date d'effet, que la période choisit, et non celle des
  conditions réunies, qui fait la rédaction. Les onze périodes de la durée
  transitoire, de 1987 à 1997, restent annuelles : leur durée suit bien
  l'année. Puis 1998-2010, 2011-2015, 2016, 2017-2022 (salaire de référence sur
  vingt-cinq ans), 2023-2025 et 2026 et après ; `decote_par_generation` dès
  1998. Le calendrier des réformes prend `spm_2023` et date `spm_2026` du
  1er mars 2026 ; la fiche de la carte `regimes_speciaux_et_non_salaries` les
  porte, avec la lecture du jour.
- *Ce que ça déplace.* Au scénario 1, de +2 à +4 % pour les générations 1956
  à 1966 parties à leur âge ou peu après : 152 trimestres au lieu de 158 à la
  génération 1956 partie en 2020, 156 au lieu de 158 et plus de décote à 1958
  partie en 2019, 160 au lieu de 162 et 61 ans et 2 mois au lieu de 61 ans et 7
  mois à 1960, 166 au lieu de 168 à 1965 partie en 2028, 168 au lieu de 169 à
  1966. La décote à la génération relève d'un quart la pension d'une
  Saint-Pierraise née en 1948 partie à soixante ans avec 120 trimestres : 31,25
  % de taux au lieu de 25. Le portage rend les mêmes chiffres que le Python
  sur huit carrières de l'archipel, de 1948 à 1970.
- *Les coupures, au jour.* Le 1er juillet 2016, le 1er septembre 2023 et le
  1er mars 2026 tombent en cours d'année : les périodes les portent au jour
  (`date_effet`, que l'action 131 a donné aux fiches le même jour), et le
  décret de 1989 sert encore les pensions de janvier à juin 2016 — 150
  trimestres et non 152 aux nés de janvier à mai 1956 partis à soixante ans.
  Le calendrier des textes relève deux versions sans coupure de la fiche,
  l'article 5 au 1er janvier 2020 et l'article 3 du décret au 24 août 2021 :
  lues, elles ne touchent ni l'âge, ni la durée, ni la décote.
- *Une question ouverte, le taux plein des générations 1958 à 1961.* Depuis
  le 1er septembre 2023, L. 351-8, 1°, ne donne plus que « l'âge prévu au
  premier alinéa de l'article L. 161-17-2 augmenté de trois années », 67 ans
  pour tous à le lire mot à mot, et aucun texte de l'archipel ne garde à ces
  quatre générations l'âge d'avant, de 65 ans et 4 mois à 66 ans et 7 mois,
  qu'elles n'avaient pas toutes atteint. Les tables le leur gardent, comme la
  fiche le faisait, au niveau `moyenne` : la pratique de la caisse n'est pas
  lue, et ni la CPS ni service-public n'en disent rien en ligne.
- *Ce qui reste faux, et n'est pas de l'âge ni de la durée.* Le revenu annuel
  moyen : « la totalité de la carrière » avant l'ordonnance, selon son rapport
  au Président de la République, puis quarante à vingt-huit années pour les
  nés avant 1962 (article 5, 3°, d) ; la fiche en retient dix, puis vingt-cinq
  dès 2017. Le moteur ne connaît qu'une table d'années par génération, celle
  du régime général et celle des indépendants : en porter une troisième est
  un changement du modèle, à faire des deux côtés. Et la surcote de 1,25 % par
  trimestre accompli depuis le 1er juillet 2016 (décret n° 2017-1000, article
  3) n'est pas portée. La ligne d'inventaire le dit.

## Mayotte

- *Ce que les textes disent.* Les articles 2 (âge), 9 (durée), 10 (taux plein)
  et 11 (minoration) du décret n° 2003-589, dans toutes leurs rédactions, et
  l'article 6 de l'ordonnance n° 2002-411 ; les décrets qui les ont changés, au
  Journal officiel. Trois états du droit :
  - de 2003 à 2011, tout suit l'ANNÉE d'effet de la pension : l'âge, de 55 ans
    en 2003, 2004 et 2005 à 60 ans en 2010 ; la durée, 64 trimestres en 2003 et
    quatre de plus par an, jusqu'en 2017 ; le taux plein, à 60 ans en 2003,
    2004 et 2005, puis un an de plus par an jusqu'à 65 ans en 2010 — la fiche
    le portait à 65 ans dès 2003, ce que le II de l'article 10 dément ;
  - le décret n° 2012-1168, en vigueur le 21 octobre 2012 (le calendrier des
    réformes le nommait « n° 2012-1170 du 19 octobre »), met l'âge à la
    génération : 60 ans avant 1956, quatre mois de plus par génération jusqu'à
    62 ans pour 1961, le taux plein cinq ans au-dessus. Le décret n° 2016-1246
    y met la durée pour les pensions de 2018 et après, 120 trimestres avant 1956
    et 172 pour 1973, et le coefficient pour celles de 2026 et après, de 2,5 %
    avant 1964 à 1,25 % à compter de 1973. Le décret n° 2024-766 ajoute, au 1er
    septembre 2023, trois mois par génération de 1962 à 1968 ;
  - en 2026, deux textes : au 1er janvier, le décret n° 2025-1410 met le taux
    plein à l'âge de L. 351-8, 1°, 67 ans ; au 1er septembre, la suspension
    (loi n° 2025-1403, article 105, V ; décret n° 2026-345) : 62 ans et 6 mois
    des nés de janvier 1963 à juin 1965, 62 ans et 9 mois de juillet à décembre
    1965, 64 ans à compter de 1970.
- *Ce qui est écrit.* Les tables `mayotte_2012`, `mayotte_2023`,
  `mayotte_2026_01` et `mayotte_2026_09` d'âges — les deux dernières portent
  aussi le coefficient de minoration —, et `mayotte_2018` de durée. Les
  périodes de 2003 à 2017 restent annuelles ; puis 2018-2022, 2023-2025, 2026
  et après, celle-ci dédoublée au 1er septembre : trente-sept périodes
  deviennent vingt. Le calendrier des réformes prend
  `mayotte_2026_taux_plein` et `mayotte_2026`.
- *Ce que ça déplace.* Jusqu'à +3 % pour les générations parties à leur âge
  que la durée de la fiche proratisait trop : 132 trimestres et non 136 à la
  génération 1958 partie en 2020 ; 148 et non 152 à 1962 partie en 2025 ; 160
  et non 162 à 1965 partie en 2029. L'ouverture à 60 ans et non 60 ans et 8
  mois pour 1955 en 2017, à 62 ans et 6 mois et non 63 ans pour 1965. Un
  coefficient de 1,375 % et non 1,25 % à la génération 1972 partie en 2036. Le
  taux plein à 60 ans en 2003 relève d'un cinquième la pension d'une Mahoraise
  partie à 56 ans avec 44 trimestres : 30 % de taux et non 25. Et le régime
  unique de la proposition, qui prend l'âge du taux plein le plus élevé du
  catalogue l'année de la bascule, passe de 67 ans et 6 mois — celui que la
  fiche de Mayotte portait en 2026 — à 67 ans : tous les témoins le portent, et
  la méthodologie l'écrit en chiffre ancré. Le portage rend les mêmes chiffres
  que le Python sur neuf carrières mahoraises.
- *Les coupures, au jour.* Le 1er septembre 2023 et le 1er septembre 2026
  coupent leurs périodes (`date_effet`) : celle de 2026 se dédouble, janvier à
  août avec les âges de 2023, le taux plein à 67 ans et la minoration de
  janvier, puis la suspension. Un Mahorais né en janvier 1964 ne part donc pas
  à 62 ans et 6 mois en août 2026, quand le droit lui oppose encore 62 ans et
  9 mois.
- *Ce qui reste.* L'âge de l'inaptitude (article 5 : 62 ans, l'âge d'ouverture
  pour les nés avant 1961) ; la durée des pensions de 2035 et après, dont le I
  de l'article 9 n'écrit plus que la génération 1973 : la table vaut pour
  toutes, faute d'autre texte. La ligne de 1969 de `mayotte_2023` (69 ans de
  taux plein, cinq ans au-dessus d'un âge que l'article 2 n'écrit pas) ne sert
  à personne : cette génération n'a pas soixante ans avant 2026.

## Polynésie française, tranches A et B

- *Ce que les textes disent.* Les délibérations et lois du pays polynésiennes
  ne sont ni dans LEGI ni au Journal officiel, et Lexpol ne répond pas d'ici :
  la source est le rapport annuel 2020 du Conseil d'orientation et de suivi des
  retraites de la Polynésie française (service-public.pf), dont les tableaux
  « source CPS 2020 » datent les conditions de la loi du pays n° 2019-6 du
  1er février 2019. L'âge légal et la durée d'assurance suffisante y suivent
  l'ANNÉE DU DÉPART, et non la génération : 60 ans et 420 mois jusqu'en 2019,
  60 ans et 6 mois et 429 mois en 2020, 61 ans et 438 mois en 2021, 61 ans et 6
  mois et 447 mois en 2022, 62 ans et 456 mois depuis 2023 ; son tableau des
  abattements se lit à l'« année du départ en retraite ». Et « les conditions du
  départ en retraite tranche B (âge, durée d'assurance, etc…) sont identiques
  en tranche A et B depuis la réforme ».
- *Ce qui est écrit.* Trois périodes annuelles, 2020, 2021 et 2022, dans les
  deux fiches ; la tranche A coupait de 60 à 62 ans au 1er janvier 2023 sans
  montée en charge, la tranche B portait 62 ans depuis 1995 — elle prend 60 ans
  avant 2020, l'âge de la tranche A, le sien n'étant pas lu. Le calendrier des
  réformes prend `polynesie_2020`.
- *Ce que ça déplace.* Une Polynésienne née en janvier 1960 ne part plus à
  soixante ans en février 2020 : l'âge légal y est de 60 ans et 6 mois. Une
  carrière courte partie en 2022 se proratise sur 149 trimestres et non 140 :
  126/149 à une Polynésienne née en 1961 partie à 61 ans et 6 mois. Les
  carrières complètes ne bougent pas. Le portage rend les mêmes chiffres que le
  Python sur six carrières.
- *Ce qui reste.* Les abattements de la réforme, que les fiches ne portent
  pas : 1,5 % par trimestre d'anticipation avant l'âge légal, dès 57 ans, et
  0,5 % par trimestre manquant à la durée suffisante, supprimés à l'« âge
  suffisant » de 65 ans depuis le 1er juillet 2019 (tableaux 3 et 4 du
  rapport) ; un droit acquis par qui avait l'âge avant 2020, dont le rapport ne
  dit rien ; l'âge de la tranche B avant 2020.

## Nouvelle-Calédonie : la CAFAT et la Caisse locale de retraites

- *Ce que les textes disent.* Lus sur Juridoc, le site des textes de la
  Nouvelle-Calédonie, dans leurs versions consolidées. La délibération n° 458
  du 8 janvier 2009, articles 1er à 4 dans la rédaction de la délibération n°
  59/CP du 24 février 2022 : « L'âge de liquidation est fixé à : 60 ans jusqu'au
  31 décembre 2022 ; 60 ans et six mois à compter du 1er janvier 2023 » et six
  mois de plus chaque 1er janvier jusqu'à 62 ans en 2026 ; la durée pour partir
  plus tôt sans abattement, 35 ans et 6 mois en 2023 et six mois de plus par an
  jusqu'à 37 ans ; 1,50 % d'abattement par trimestre d'anticipation, dix au
  plus. Le code des pensions de retraites des fonctionnaires de
  Nouvelle-Calédonie, article Lp. 221-1 dans la rédaction de la loi du pays
  n° 2024-10 du 12 septembre 2024 : la « double condition de 62 ans d'âge et de
  35 ans de services effectifs » s'apprécie « à la date d'admission à la
  retraite », avec 60 ans et 6 mois en 2025, 61 ans en 2026, 61 ans et 6 mois
  en 2027. Les deux caisses relèvent donc l'âge à la DATE du départ, et non à la
  génération : leurs périodes annuelles sont la bonne écriture.
- *Ce qui est corrigé.* À la CAFAT, la durée de 2023 : 142 trimestres, et non
  les 144 que la fiche tirait d'un résumé. À la Caisse locale de retraites,
  l'âge : la fiche portait le calendrier de l'avant-projet de février 2024,
  quatre mois par an jusqu'à 62 ans en 2030 ; la loi adoptée va six mois par an
  jusqu'en 2028. Un fonctionnaire calédonien né en 1966 ne part plus à 61 ans
  en 2027, ni un né en 1967 à 61 ans et 6 mois en 2028. Le portage rend les
  mêmes chiffres que le Python sur sept carrières des deux caisses.
- *Ce qui reste.* À la CAFAT, le droit acquis du 3° de l'article 3 — le taux
  plein sans abattement à qui avait, au 1er janvier 2023, trente-cinq ans
  d'assurance et cinquante-sept ans et demi. À la Caisse locale, la durée de
  services qui ouvre la pension d'ancienneté (31 ans en 2024, six mois de plus
  par an jusqu'à 35 ans) et les minorations, que le code renvoie à une
  délibération, lues dans la seule page de la direction de la fonction
  publique.

## La CRPN, tranches 1 et 2

- *Ce que les textes disent.* L'article 26 du décret n° 2011-1500, dans ses
  deux rédactions (LEGIARTI000024779267, puis LEGIARTI000044496248 du décret
  n° 2021-1637), et R. 426-11 du code de l'aviation civile de 2012 au
  31 octobre 2023 (LEGIARTI000024795153, LEGIARTI000044496243), lus dans
  l'index LEGI. De 2012 à 2020, l'âge, les annuités et leur somme qui ouvrent
  le taux plein montent à l'ANNÉE d'effet de la pension (I et II : 50 ans et
  6 mois, 26 annuités et une somme de 76 en 2012, jusqu'à 54 ans et 6 mois,
  30 annuités et 80 en 2020), et la décote se compte, avant cinquante-cinq
  ans, sur le plus grand des deux manques. Depuis 2022, la durée seule : trente
  annuités. Mais le III, dans la rédaction de 2021, y déroge par GÉNÉRATION :
  « pour les personnes nées avant le 1er janvier 1971, lorsque la liquidation
  est effectuée à compter de l'âge de cinquante-cinq ans », 21 annuités
  jusqu'à la génération 1962, une de plus par génération, 29 pour 1970. Sa
  rédaction d'origine comptait à l'année d'effet, 26 annuités en 2022 et une
  de plus par an : remplacée avant d'avoir servi.
- *Ce qui est écrit.* La table `crpn_2022`
  (`legislation/duree_requise_regimes_speciaux.csv`) garde 120 trimestres et
  retranche à la cible de la décote 36 trimestres pour 1962, quatre de moins
  par génération ; la colonne `age_minimum`, nouvelle, la réserve à qui part à
  cinquante-cinq ans ou plus. Le moteur la lit dans le décompte par la durée
  seule (`trimestres_de_decote`, `ligne` de `DureesRequisesRegimes`, et leurs
  jumeaux), la proratisation gardant ses trente annuités. Réforme
  `navigants_2022` au calendrier ; la fiche de règle `decote_crpn` relue.
- *Ce que ça déplace.* Un navigant né en 1965 parti en 2022 à cinquante-sept ans
  avec vingt-cinq annuités n'a plus de décote, au lieu de 25 % ; né en 1970, il
  perd seize trimestres et non vingt ; parti à cinquante-quatre ans, rien ne
  change. Le portage rend les mêmes chiffres que le Python sur huit carrières.
- *Ce qui reste.* Les conditions de 2012 à 2021, à l'année d'effet : le moteur
  n'a pas de décompte par la somme de l'âge et des annuités. Le décompte au
  jour près.

## La CRPCEN : rien à changer

- *Ce que les textes disent.* L'article 84 du décret n° 90-1215 écrit ses âges
  par génération dans toutes ses rédactions ; l'article 85-2 lit la durée à la
  date des conditions réunies, puis par génération.
- *Ce qui est écrit.* Déjà tout : `age_table: crpcen_2011` puis `crpcen_2023`,
  le calendrier de 2008 et les tables `crpcen_2014` et `crpcen_2023`, l'âge de
  référence de 2025 avec le droit acquis de l'article 85-2, II. Les périodes
  annuelles de 2008 à 2024 ne portent plus que des valeurs de repli. Les
  rédactions de 2008 et de 2011 de l'article 84 donnent le même âge à toutes
  les générations qui pouvaient partir avant le 19 septembre 2011 : la table de
  2011 vaut pour ces années-là aussi.

## La Comédie-Française

- *Ce que les textes disent.* Le décret n° 68-960, lu dans l'index LEGI. Son
  article 6, depuis le décret n° 2011-1134 : 62 ans pour les artistes et les
  employés, 57 pour les machinistes et les pompiers ; mais son article 51, I, A
  ne donne 62 ans qu'à compter de la génération 1962, 60 ans avant 1957, quatre
  mois de plus par génération entre les deux, et le B fait de même de 55 à
  57 ans. La décote s'annule à l'âge d'ouverture « majoré de cinq ans »
  (article 12, II, 1°). La durée, à son article 12, V, dans ses cinq rédactions
  de 2008 à 2016 : le calendrier de 2008, à la date où les conditions sont
  réunies ; depuis la rédaction du décret n° 2014-666, applicable en 2017, une
  table par génération à compter du 1er juillet 2019, lue à soixante ans (VI).
- *Ce qui est écrit.* Tables `comedie_francaise_2011` (âges) et
  `comedie_francaise_2014` (durée, `age_de_lecture` 60), calendrier
  `regimes_speciaux_2008` dès la période de 2009. La suspension de 2026 ne la
  touche pas : déclarée au calendrier des réformes.
- *Ce que ça déplace.* Une sociétaire née en 1955 part à soixante ans en 2015,
  ce que la fiche lui refusait (62 ans pour tous dès 2012), et doit 162
  trimestres, non les 166 de la table commune ; une née en 1949 partie en 2009,
  152 et non 161. Le portage rend les mêmes chiffres sur douze carrières.
- *Ce qui reste.* Le 2° de l'article 6, les machinistes, non modélisé. La
  coupure au 1er juillet 2008 : les pensions du second semestre 2008 gardent
  150 trimestres au lieu de 151, comme à la CRPCEN, à la SNCF et à la RATP. Le
  calendrier signale la rédaction de 2017 de l'article 12, que nulle période ne
  coupe : elle écrit dans le décret ce que le VI de l'article 5 de la loi de
  2003 y portait par renvoi, sans changer un paramètre ; et le pivot de la
  fiche nomme cet article `age_ouverture` quand il porte la durée.

## Les assemblées parlementaires

- *Ce que les textes disent.* Le règlement de la caisse des députés, relu dans
  le document que l'Assemblée sert à la même adresse, consolidé après la loi du
  14 avril 2023 et la suspension de 2026 : l'âge « de manière croissante à
  raison de trois mois par génération », 64 ans à compter de 1969, par arrêté
  des Questeurs non publié (article 8) ; et la valeur de l'annuité et le
  nombre maximal d'annuités « en vigueur à l'âge d'ouverture » pour les nés de
  1949 à 1968, au soixante-quatrième anniversaire après (article 21 ter). Ni
  décote ni surcote.
- *Ce qui est écrit.* La table d'âges `assemblee_nationale` (celle de
  L. 161-17-2, que le règlement décrit), le calendrier du même nom
  (`legislation/duree_requise_calendriers.csv`) lu au mois où l'âge d'ouverture
  est atteint. Vingt et une périodes annuelles deviennent huit, une par
  retenue.
- *Ce que ça déplace.* Un député né en 1953, dont le droit s'ouvre en mars 2014
  et qui part en 2018, doit 165 trimestres et non 167. La fiche donnait 62 ans
  et 3 mois à la génération 1962 : c'est 62 ans et 6 mois. Le portage rend les
  mêmes chiffres sur dix carrières.
- *Ce qui reste.* L'arrêté des Questeurs, le règlement du Sénat et celui des
  fonctionnaires des assemblées, non publiés.

## Le test : la règle de chacun, de 1920 à 2005

`tests/test_regle_de_chacun.py`, niveau `controle` (dix-huit secondes). Pour
tout statut et toute génération de 1920 à 2005, partie de cinquante à
soixante-dix ans, il vérifie qu'une période répond dans tout régime ouvert,
et que l'âge d'ouverture et la durée requise ne dépendent pas de l'année du
départ, une fois l'âge atteint. Les régimes dont le texte compte à l'année
d'effet se déclarent avec leurs années de bascule (`A_L_ANNEE_D_EFFET` : la
Polynésie, la Nouvelle-Calédonie, Mayotte jusqu'en 2017, Saint-Pierre-et-Miquelon
jusqu'en 1998, la CRPN en 2012) ; une bascule hors de ces années échoue, et une
déclaration qui ne sert plus aussi.

Il a trouvé, dès son premier passage, la fonction publique : la table de
l'article 66, II, de la loi de 2003 ne commençait qu'en 2004, et le droit
ouvert avant, liquidé après, retombait sur la table par génération. Un
fonctionnaire né en 1940, dont le droit s'ouvre en 2000 et qui part en 2004,
devait 157 trimestres au lieu de 150. Le moteur lit désormais, pour un droit
ouvert avant la table, la durée de la période où il s'est ouvert (« Jusqu'en
2003 ; 150 »), dans l'État, la CNRACL et le FSPOEIE. La ligne de 2003 n'est pas
ajoutée à la table : OpenFisca, qui la certifie, ne la porte pas.

Restent dix-sept régimes, déclarés `A_RELIRE` avec ce que le relevé en montre :
l'Opéra de Paris (la durée de la table commune depuis 2009, et non le
calendrier de 2008 des régimes spéciaux), la Banque de France (une période par
année jusqu'en 2025, et la durée empruntée à la fonction publique), la MSA des
non-salariés, la CNAVPL et la CNBF (2004), la CAVIMAC (2007), le CESE, la
CARMF et l'ASV (2017), la CARPIMKO (2016), la CPRN (64 ans de 2014 à 2023), la
Comédie-Française d'avant 1993, et les complémentaires des générations 1920 à
1922 avant 1983. Chacun, texte en main, sort du registre en devenant juste ou
en passant à `A_L_ANNEE_D_EFFET`.

## Pour les pages

Rien n'est écrit dans `pages.js` ni dans `index.html`. La méthode (« Ce que le
système 1 applique du droit en vigueur », `methodeDroitPositif`) dit « cinq
paramètres lus à la génération plutôt qu'à l'année de liquidation » : elle
devrait dire aussi que la durée des régimes spéciaux, de la fonction publique
de 2004 à 2008 et des députés se lit à la date où l'assuré réunit les
conditions, et que la Polynésie, la Nouvelle-Calédonie et Mayotte jusqu'en
2017 comptent à l'année d'effet de la pension, comme leurs textes l'écrivent.
