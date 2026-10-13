# Les dix fiches qui restaient : l'âge et la durée de chacun, texte en main

**Le 13 octobre 2026, Saint-Pierre-et-Miquelon et Mayotte : leurs âges, leurs
durées et leurs coefficients de minoration se lisent à la génération, dans les
tables que leurs textes écrivent, et chaque période nomme celles de la rédaction
en vigueur à sa date d'effet. La Polynésie, elle, date sa réforme de 2019 à
l'année du départ : ses fiches gagnent les trois années de montée en charge
qu'elles sautaient. Une Saint-Pierraise née en 1956 partie en 2020 doit
152 trimestres, et non les 158 de la génération 1959 ; un Mahorais né en 1958
parti en 2020, 132 et non 136. Là où le droit suit l'année d'effet — la durée
transitoire de l'archipel jusqu'en 1997, l'âge, la durée et le taux plein de
Mayotte de 2003 à 2011 ou 2017 —, les périodes restent annuelles.**

Demande du propriétaire : « Action 121 : reprends à la fiche
cps_saint_pierre_et_miquelon, puis les suivantes, dans l'ordre du bloc. »

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
- *Les coupures, à l'année près.* Les pensions de janvier à juin 2016 relèvent
  encore du décret de 1989 : la table ne s'en écarte que pour les nés de
  janvier à mai 1956 partis à soixante ans, 152 trimestres au lieu de 150.
  Celles de janvier à août 2023, et de janvier et février 2026, lisent déjà la
  table suivante, qui ne diffère de la précédente que pour des générations
  qui n'atteignent pas leur âge avant 2025, puis avant avril 2026. Le
  calendrier des textes relève deux versions sans coupure de la fiche,
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
- *Ce qui est écrit.* Les tables `mayotte_2012`, `mayotte_2023` et
  `mayotte_2026` d'âges — la dernière porte aussi le coefficient de
  minoration —, et `mayotte_2018` de durée. Les périodes de 2003 à 2017 restent
  annuelles ; puis 2018-2022, 2023-2025, 2026 et après : trente-sept périodes
  deviennent dix-neuf. Le calendrier des réformes prend
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
- *Les coupures, à l'année près.* Les pensions de janvier à août 2023 lisent
  déjà la table de 2023, qui ne diffère de celle de 2012 que pour les nés
  depuis 1962, dont aucun n'atteint son âge avant 2024. Celles de janvier à
  août 2026, la table de la suspension, qui laisse partir deux mois trop tôt
  les nés de janvier et février 1964 : 62 ans et 6 mois en juillet et août
  2026, quand le droit leur oppose encore 62 ans et 9 mois.
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
