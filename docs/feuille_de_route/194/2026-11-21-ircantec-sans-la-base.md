# Action 194 : l'Ircantec servie avant le régime général

Action 194, une partie en écart de la carte de justesse :
`coefficient_anticipation_ircantec / ancres_fixes_2023` et
`liquidation_regime_par_regime / chaque_regime_a_sa_date`, toutes deux en
écart avec l'exemple `ircantec_minoration_age_avant_l_age_legal`.

L'écart : né en décembre 1964, contractuel, 160 trimestres, l'assuré demande
sa retraite de l'Ircantec au 1er septembre 2026, à 61 ans et 9 mois, avant
l'âge légal de sa génération (62 ans et 9 mois). La caisse la sert dès cette
date, au coefficient de l'âge seul, 0,7625. Le modèle la faisait attendre le
régime général et rendait 0,90 à 62 ans et 9 mois, par la durée.

Le texte, lu dans l'index LEGI : l'article 16 de l'arrêté du 30 décembre 1970
ouvre l'anticipation « au plus tôt à cinquante-cinq ans » (1971 au 30 juin
2011), puis « au plus tôt dix ans avant que l'assuré ait atteint » l'âge du
1° de L. 351-8 (depuis le 1er juillet 2011), sans condition tenant au régime
de base. La seconde table, celle de la durée, ne vaut que pour les agents
« âgés de soixante à soixante-cinq ans » (1983, 2004), puis d'un âge
« compris entre l'âge prévu à l'article L. 161-17-2 [...] et l'âge prévu au 1°
de l'article L. 351-8 » (2011, 2023) ; le taux plein n'exonère que « dès lors
qu'elles ont atteint l'âge légal » (2023, I, 2°). La carrière longue, le
handicap, l'inaptitude exonèrent avant (I, 1°).

La correction, dans le portage :

- `ouvrir.ageAuPlusTotSansLaBase` : l'âge du taux plein de la période moins
  `anticipation_maximale_annees` de la version de la date d'effet (dix ans
  dans toutes) ; `departs.ouvertureSous` le lit pour l'Ircantec seule.
- `departs.departsEtDemandes` : l'Ircantec, l'IPACTE et l'IGRANTE suivent
  toujours la base, mais la devancent au départ déclaré quand la base n'ouvre
  pas encore et qu'elles s'ouvrent déjà. Avant leur âge, elles suivent la
  base. Elles ne sont pas mises dans `SANS_LEUR_BASE` : un premier essai l'a
  fait, et servait à 57 ans, à 0,43, l'Ircantec du contractuel handicapé parti
  à 55 ans, que la base sert sans coefficient (témoin
  `handicap_contractuel_ircantec`, −15 %), et à 57 ans l'Ircantec d'un
  militaire reconverti, acquise après sa pension (`cumul_militaire_2027`).
- `ouvrir.ouvrir` : la demande de l'Ircantec seule, qui devance la base, ne
  lui doit que sa durée requise, et s'ouvre.
- `liquider.abattementPoints` : avant l'âge légal, hors carrière longue,
  l'Ircantec ne lit que l'âge.

Tests : l'exemple, son `ecart_connu` retiré, vu rouge à 0,9 ;
`test_l_ircantec_se_demande_sans_la_base_dix_ans_avant_l_age_normal`, trois
cas posés à la main (57 ans en 2023 : 0,43 ; 56 ans en 2002 : 0,50, escalier
de 1983 ; 57 ans en 1977 : 0,57, table par année d'âge, aux trois régimes),
vu rouge. `test_ircantec.py` lit désormais `anticipation_maximale_annees` dans
la version (`DE_LA_VERSION`), et non plus comme un écart déclaré.

Ce qui bouge : aucun témoin de simulation sur 937 ; l'exemple ; le paquet,
dont les agrégats du coût (carrières de contractuels parties avant l'âge
légal) ; vingt-deux rendus de page, les pages du coût et les écarts de
financement des pages du simulateur, d'un euro au plus.

Reste : l'Agirc-Arrco, que l'accord laisse aussi demander dix ans avant
(article 84), suit toujours sa base (approximation de
`liquidation_regime_par_regime`) ; la présomption retenue sert l'Ircantec au
départ déclaré, non à cinquante-sept ans à qui part avant.
