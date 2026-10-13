# Les dix fiches qui restaient : l'âge et la durée de chacun, texte en main

**Le 13 octobre 2026, Saint-Pierre-et-Miquelon : ses âges et sa durée se lisent
à la génération, dans les tables que la loi n° 87-563 écrit pour l'archipel,
et chaque période nomme celles de la rédaction en vigueur à sa date d'effet.
Une Saint-Pierraise née en 1956 partie en 2020 doit 152 trimestres, et non les
158 de la génération 1959 ; née en 1965 et partie en 2028, elle ouvre son droit
à 62 ans et 3 mois avec 166 trimestres, et non à 62 ans et 9 mois avec 168. Le
coefficient de minoration suit lui aussi la génération, par le renvoi du décret
de 1989 à R. 351-27. Trente-deux périodes deviennent dix-sept, les onze de la
durée transitoire comprises.**

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
