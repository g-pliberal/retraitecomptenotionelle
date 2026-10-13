# Les coupures au mois : la période d'un régime bornée au jour, à la date d'effet

**Le 13 octobre 2026 : les trois coupures au mois de l'action sont faites. Les
versions datées ne les permettaient pas telles quelles : elles bornent au jour
les paramètres d'une fiche que le moteur lit à la date d'effet, et ces trois
textes changent des champs de période de régime, que le moteur choisissait à
l'année. La période porte désormais, comme une version, les dates d'effet
qu'elle liquide, au jour (`date_effet`), et la liquidation la choisit à la date
d'effet de la pension ; l'acquisition garde les années. Le régime général et les
salariés agricoles passent à la règle de 1982 le 1er avril 1983, la CAVEC à
0,75 % le 5 septembre 2018 et à 1,25 % le 7 juillet 2025, le RACL à la règle de
l'IRCEC le 16 mai 2025. Aucun témoin ne bouge ; dix-sept cas de test tiennent les
coupures, dans les deux moteurs.**

Demande du propriétaire : « Action 131 : les coupures au mois seulement, du
1er avril 1983, de la CAVEC et de la RACL ; vois d'abord si les versions datées
(docs/architecture.md, § 4.6) les permettent. »

- *Ce que les versions datées permettent.* `noyau/versions.py` borne une
  version au jour sur ses dates qui décident, et le moteur lit les paramètres de
  la version applicable à la date d'effet, AAAA-MM-JJ, par `FichesDatees` et ses
  sœurs : une quarantaine de fiches. Le minimum contributif en est l'exemple :
  ses versions s'arrêtent et commencent au 1er avril 1983, et il n'était déjà
  servi qu'aux pensions d'avril. Une période peut y renvoyer, comme
  `regles_du_salaire_annuel_moyen`. Mais les trois coupures portent sur la
  période elle-même : en 1983, une vingtaine de champs changent ensemble — l'âge
  du taux plein et sa durée, la décote, l'ajournement, la règle des femmes de
  1979, la durée majorée après soixante-cinq ans — ; à la CAVEC, le taux de la
  majoration de report et, en 2025, la majoration pour trois enfants des
  avantages de la période ; au RACL, l'interrupteur `abattement_points`, que le
  chargeur résout une fois par période. Les faire passer chacun par une fiche
  datée aurait demandé une indirection par champ, et rien pour 1983. Ce que les
  versions apportent, c'est la forme : une borne [début, fin) sur
  `liquidation.date_effet`, écrite au jour.
- *Ce qui est fait.* Le champ facultatif `date_effet` d'une période
  (`_schema.yaml`), absent partout ailleurs : du 1er janvier de `debut` au
  1er janvier qui suit `fin`. Le chargeur refuse une borne qui n'est pas un jour,
  qui finit avant de commencer, ou qui tombe à plus d'un an des années de la
  période (`_dates_d_effet`). `Regime.periode_a_l_effet` et
  `commun.periode_de_liquidation`, jumeaux en JavaScript (`periodeALEffet`,
  `periodeDeLiquidation`), choisissent la période à la date d'effet, la dernière
  année du régime bornant comme avant. Les choix de la liquidation y passent :
  `liquider_chaque_regime`, la part des régimes alignés et la pension agricole
  de 2026 (`liquider`), l'ouverture et `periodes_parcourues` (`ouvrir`), les
  points gratuits et le plafond des mines (`acquerir`), la surcote parentale, la
  majoration pour enfants, celle du conjoint, le complément de la RCO et la
  majoration pour enfants à charge (`completer`), les trimestres d'enfants
  (`compter`), l'âge d'ouverture d'une unité de départ (`departs`). Gardent
  l'année, à dessein : les lignes de l'acquisition, le barème du point de la
  revalorisation, la succession des régimes (`coordonner`), qui ne lisent que
  le type de calcul ou le barème, la durée des fonctionnaires à soixante ans,
  l'ouverture du droit des IEG et de la CRPCEN, et la règle de 1982 que le taux
  acquis au 31 mars 1983 relit. La datation des taux, qui découpe une période en
  morceaux d'années (`dater_les_taux`, `dater_les_taux_moyens`), leur partage
  ses dates d'effet (`morceau_d_annees`, `morceauDAnnees`) : sans quoi chaque
  morceau des années 1983-1993 aurait liquidé dès avril 1983, et le premier
  aurait servi toute la période. Le paquet porte la borne aux seules périodes
  qui la déclarent.
- *Les coupures.* Régime général et salariés agricoles : la période de 1979 à
  1982 liquide jusqu'au 31 mars 1983, celle de 1983 à 1993 depuis le 1er avril,
  et cotise sur toute l'année 1983. CAVEC : la période de 2008 à 2018 liquide
  jusqu'au 4 septembre 2018, celle de 2019 à 2025 du 5 septembre 2018 au 6
  juillet 2025, celle de 2026 depuis le 7 juillet 2025, avec la majoration pour
  trois enfants. RACL : la période de 2014 à 2024 liquide jusqu'au 15 mai 2025,
  celle de 2025 depuis le 16. Mesuré sur une carrière simple de part et d'autre
  de chaque date : 25 % puis 50 % à soixante ans aux pensions du 1er mars et du
  1er avril 1983 ; à soixante-six ans, une majoration de 5 % puis de 3 % aux
  pensions de la CAVEC du 1er septembre et du 1er octobre 2018, 3 % puis 5 % à
  celles du 1er juillet et du 1er août 2025 ; au RACL, à soixante-deux ans et
  neuf mois sans la durée, un coefficient de 0,75 au 1er mai 2025 et de 0,9625
  au 1er juin, les coefficients du régime de base.
- *Ce qui le tient.* `tests/test_coupures_au_mois.py`, dix-sept cas : chaque
  coupure de part et d'autre de sa date, le partage des dates d'effet — chaque
  mois de 1930 à 2070, autant de périodes liquident qu'il y en a qui couvrent
  l'année —, le refus de six bornes mal écrites, et les deux moteurs, étape par
  étape, sur quatorze requêtes autour des coupures. La confrontation mord :
  coupée à l'année en JavaScript, elle relève 67 écarts. Le test de la majoration
  pour trois enfants de la CAVEC s'appelle désormais `…_depuis_juillet_2025`.
  Aucun témoin ne bouge : aucun ne liquide dans ces mois-là. Le paquet gagne
  quelques kilo-octets, les notes des périodes de 1983 se répétant dans chacun
  des morceaux d'années que la datation des taux découpe.
- *Les lectures*, à la source, consignées au journal de veille
  (`2026-10-13-action-131-coupures-au-mois.yaml`) : l'article 9 de l'ordonnance
  et l'article 2 du décret n° 82-1054 ; l'article 4 du décret n° 83-551, qui
  range les pensions « avec une date d'effet antérieure au 1er avril 1983 » ;
  les trois arrêtés, sans date d'application, qui valent donc le lendemain de
  leur publication. Les fiches `decote_avant_1983`, `surcote_par_age_seul`,
  `minoration_racl_2014_2024` et `minoration_ircec` le disent, et perdent leur
  question « quand le moteur saura dater une règle au mois » ; § 4.6 de
  l'architecture et version du jour
  (`2026-10-13-la-periode-coupee-au-jour.md`) ; `docs/limites`, partie 3.
- *Trouvé en chemin.* Les statuts de la CAVEC de 2018 liquident « à dater du
  premier jour du trimestre civil suivant la demande » (article 14), quand le
  moteur liquide au mois : à lire à la caisse, noté à `surcote_par_age_seul`.
  Les périodes de 1972 à 1982 du régime général ne portent pas l'AVPF, qui
  existe depuis le 1er juillet 1972 : les pensions de janvier à mars 1983, qui
  les rejoignent, perdent comme elles ses salaires dans le salaire annuel moyen ;
  à porter dans un commit à part, avec le diff de ses témoins. L'accord de l'ASF
  du 4 février 1983 vaudrait aux complémentaires le même 1er avril 1983 (réforme
  `asf_1983`) : il n'est pas lu. Le 1er juillet 1984 des artisans et commerçants
  se coupe désormais d'une borne, une fois leurs textes lus. L'arrêté du 17
  avril 2024 sur le RACL, publié le 2 mai, ne demande pas de coupure. Il porte
  son taux plein à l'âge du 1° de L. 351-8, celui que le moteur sert depuis
  2014 ; avant lui, « l'âge prévu à l'article L. 161-17-2 [...] augmenté de cinq
  ans » valait trois mois de plus aux nés de septembre à décembre 1961, les
  seuls qui ont pu partir avant le 3 mai 2024 sous l'âge légal relevé, sans
  changer, l'année entamée comptant entière, les années qui leur manquaient ; et
  l'annexe qu'il abroge ne touchait plus que des générations parties sans
  minoration.
- *Pour les pages* : rien. Aucune ne montre les bornes d'une période de régime.

Reste de l'action, inchangé : `retraite_proportionnelle_msa`, le maximum M et
la série de l'AVTS (zone des données) ; `cotisation_par_classes_liberales`, les
grilles ; les restes de `coefficients_anticipation_agirc_arrco`, de
`decote_avant_1983`, des artisans et commerçants, de
`pension_non_salaries_agricoles_2026` et de R. 173-4-3.
