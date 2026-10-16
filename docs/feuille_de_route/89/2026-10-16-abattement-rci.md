# L'abattement du RCI : le barème de l'Agirc-Arrco, depuis la fusion

**Le 16 octobre 2026.** L'écart que la note du 14 octobre
(`2026-10-14-cnav-service-public.md`) avait laissé connu est corrigé, par les
données seules.

- *Le correctif.* Les quatre périodes du RCI, et les dernières du RCO des
  artisans (2008-2012, les deux tranches) et du NRIC (2005-2012), renvoient à
  la fiche `abattement_rci`, qui déclare `abattement_points: agirc_arrco` :
  la table des trimestres manquants et celle des âges, la plus avantageuse
  retenue, ce qui revient au « plus petit des deux décomptes » de l'annexe 2
  du règlement. Les dernières périodes du RCO et du NRIC en sont parce qu'un
  régime fermé se liquide, après sa dernière année, sur la période de
  celle-ci (`commun.periode_de_liquidation`) : sans elles, les points du RCO
  d'avant 1997 de l'exemple de la circulaire 2026-07 gardaient 0,9125.
- *Le témoin.* `cnav_2026_07_abattement_rci_1962` perd son écart connu :
  0,93 au RCI comme au RCO. Les témoins de simulation des artisans et des
  micro-entrepreneurs partis avant le taux plein montent : 0,85 → 0,88 à douze
  trimestres (`micro_entrepreneur_*`), 0,975 → 0,98 à deux
  (`creux_en_milieu_de_carriere`), et de même `cumul_artisan`,
  `reversion_artisan_plafond`, `releve_annees_manquantes`. Le parcours suit.
- *Les règlements d'avant 2013, cherchés dans l'index de la DILA.* Le RCO des
  artisans : décret 78-351 du 14 mars 1978, règlement approuvé par l'arrêté du
  15 décembre 1978 (et non de 1979) ; l'arrêté du 30 novembre 1984 y met, pour
  la retraite à soixante ans, un « tableau des taux d'abattement applicable
  aux droits acquis » — le JORF n'en porte que l'analyse, sans le tableau. Le
  NRIC : arrêté du 17 décembre 2004, dont le règlement est annexé sans être
  publié. Ni l'un ni l'autre ne se lit : au Bulletin officiel, que Légifrance
  ou Gallica rendraient, au propriétaire.
- *Ce qui reste approché.* Les dernières périodes du RCO et du NRIC servent
  aussi les liquidations de 2008 (RCO) ou 2005 (NRIC) à 2012, qui prennent
  ainsi le barème de 2013 sans texte lu ; les périodes plus anciennes gardent
  la décote du régime de base, pas mieux lue. Déclaré dans la fiche, qui reste
  `approchee`.
- *Fichiers.* `data/reference/regimes/rci.yaml`, `rco_artisans.yaml`,
  `nric.yaml` ; la fiche `abattement_rci` ; le témoin des exemples officiels ;
  le journal de veille.
- *Reste.* Lire les deux règlements quand le Bulletin officiel sera ouvert, et
  couper alors les périodes du RCO et du NRIC à la date du barème.
