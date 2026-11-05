# La CRPNPAC à cinquante ans, et le régime général du navigant à l'âge de L. 161-17-2

File N de la vague 6, le 5 novembre 2026 : le reste que la file L laissait
(`2026-11-04-ouverture-de-la-base-des-liberaux.md`, « Ce que l'étape laisse ») et que la
relecture R-L notait (point 4). Le soupçon : en ouvrant la CRPNPAC à cinquante ans, le
modèle ouvre-t-il aussi le régime général ? Oui. Textes lus pendant la session dans
l'index LEGI du dépôt, à jour au 2 novembre 2026.

## Le cas posé, avant

Un navigant né le 10 février 1964, entré à vingt-deux ans, deux salaires moyens, qui
demande son départ à cinquante-cinq ans (requête du simulateur, statut
`personnel_navigant`) : servi par le portage, refait au bit près par le moteur Python, et
de même sous `PRESOMPTIONS_DECALEES=1`. Un seul départ, le 1er mars 2019, motif
`age_legal` :

| Régime | Pension annuelle (euros de 2019) | Détail |
|---|---|---|
| CRPNPAC | 33 677,96 | SR 60 681,01 × 55,5 % × 120/120 |
| CRPNPAC, tranche 2 | 0 | |
| régime général | 10 469,57 | SR 36 017,44 × 37,5 % × 131/169 |
| Agirc | 4 567,74 | 24 263,72 points × 0,4378 × 0,43 |
| Arrco | 2 353,51 | 4 348,01 points × 1,2588 × 0,43 |
| Agirc-Arrco | 40,80 | 75,38 points × 1,2588 × 0,43 |

Parti à cinquante ans, de même : tout au 1er mars 2014, le régime général compris.

## Ce que disent les textes

- **La CRPNPAC.** « I.-Une pension de retraite est servie à l'affilié qui demande la
  liquidation de ses droits à pension, dans les conditions précisées aux articles
  suivants, dès lors qu'il réunit cumulativement à la date d'effet de la pension les
  conditions suivantes : 1° Avoir atteint l'âge de cinquante ans ; 2° Justifier de vingt
  annuités acquises au titre des services valables pour la retraite tels qu'ils sont
  définis à l'article R. 426-13. Cette condition n'est pas requise lorsque l'assuré a
  atteint l'âge prévu à l'article R. 426-12 » (code de l'aviation civile, R. 426-11,
  LEGIARTI000024795153, du 1er janvier 2012 au 16 décembre 2021 ; même phrase en 2021,
  LEGIARTI000044496243, et au code des transports, R. 6527-21, LEGIARTI000048325100,
  depuis le 1er novembre 2023). De 1995 à 2011 : « Avoir atteint l'âge de cinquante
  ans » (R. 426-11-1, LEGIARTI000006845207). Aucune des cinq rédactions de R. 426-11
  (1984, 1995, 2010, 2012, 2021) ne nomme le régime général, la sécurité sociale, L. 351-1
  ou L. 161-17-2. R. 426-16-1 (LEGIARTI000036880164, rédaction du 7 mai 2018) suppose même
  les deux dates distinctes : « Pour la période de jouissance comprise entre l'âge auquel
  l'affilié aura atteint le nombre d'annuités nécessaires pour l'ouverture du droit à
  pension, et ce au plus tôt à l'âge mentionné au 1° du A du II de l'article R. 426-11,
  et l'âge mentionné à l'article L. 161-17-2 du code de la sécurité sociale, la pension
  mensuelle est assortie d'une majoration ».
- **Le régime général.** « L'assurance vieillesse garantit une pension de retraite à
  l'assuré qui en demande la liquidation à partir de l'âge mentionné à l'article
  L. 161-17-2 » (L. 351-1, LEGIARTI000023035688) ; « fixé à soixante-deux ans pour les
  assurés nés à compter du 1er janvier 1955 » (L. 161-17-2, LEGIARTI000025014605, du
  23 décembre 2011 au 31 août 2023, « applicables aux pensions prenant effet à compter du
  1er juillet 2011 ») ; « 3° Soixante-deux ans et neuf mois, pour les assurés nés entre
  le 1er janvier 1963 et le 31 mars 1965 » (L. 161-17-2, LEGIARTI000053280889, « aux
  pensions prenant effet à compter du 1er septembre 2026 »).
- **Rien n'avance le régime général de ce navigant à 55 ans.** La carrière longue : pour
  les « assurés nés à compter du 1er janvier 1960 : A cinquante-huit ans pour les assurés
  justifiant d'une durée d'assurance cotisée au moins égale à celle prévue au deuxième
  alinéa de l'article L. 351-1 majorée de huit trimestres et ayant débuté leur activité
  avant l'âge de seize ans » (D. 351-1-1, II, LEGIARTI000026139949, du 1er novembre 2012
  au 31 août 2023) ; le départ des assurés handicapés, qui demande d'avoir été « atteints
  d'une incapacité permanente d'au moins 50 % » (L. 351-1-3, LEGIARTI000028498841 ;
  « à cinquante-cinq ans », D. 351-1-5, LEGIARTI000030058836) ; l'incapacité permanente
  d'origine professionnelle (L. 351-1-4, LEGIARTI000035640851) ; le compte professionnel
  de prévention, dont les points financent « un départ en retraite avant l'âge légal »
  (L. 4163-7, 3°, du code du travail, LEGIARTI000035631174 ; L. 351-6-1,
  LEGIARTI000037063352). Le cas n'a ni incapacité, ni handicap, ni compte, et il est
  entré à vingt-deux ans. Aucun des textes lus ne donne au personnel navigant un âge
  propre au régime général.

## La correction

La CRPNPAC, ses deux tranches, rejoint la CARPV et la CAVEC dans `SANS_LEUR_BASE`
(`moteur/js/droit/departs.js`, puis `src/retraite_notionnelle/droit/departs.py`, ligne
pour ligne) : une unité à elle, que sa date sépare de la base quand elle s'ouvre avant
elle. L'Agirc-Arrco, qui partage les années du régime général et de la CRPNPAC, suit la
plus tardive des deux unités : le régime général, comme le modèle le présume de toute
complémentaire des salariés.

## Les valeurs attendues, à la main

Une pension prend effet le premier jour du mois qui suit l'anniversaire de l'âge.

| Départ demandé | La CRPNPAC | Annuités au départ | Le régime général |
|---|---|---|---|
| 55 ans | 10 février 2019 → 1er mars 2019 | 55 − 22 = 33 ≥ 20 | 62 a 9 m |
| 50 ans | 10 février 2014 → 1er mars 2014 | 50 − 22 = 28 ≥ 20 | 62 a 9 m |
| 63 ans | 10 février 2027 → 1er mars 2027 | 41 | ouvert : un seul départ |

Le régime général : 10 février 1964 + 62 ans = 10 février 2026 ; + 9 mois = 10 novembre
2026 ; la pension prend effet le 1er décembre 2026, après le 1er septembre 2026 : c'est
bien la rédaction LEGIARTI000053280889 qui la régit. Pour une pension d'avant le
1er septembre 2026, D. 161-2-1-9 (LEGIARTI000047634502) disait « 10° Soixante-trois ans
pour les assurés nés en 1964 » : le 10 février 2027, une pension du 1er mars 2027, qui
tombe elle-même sous la rédaction de 2026 ; le 1er décembre 2026 est donc la première
date où le régime général s'ouvre. À 63 ans, 63 ≥ 62 a 9 m : tous les régimes sont ouverts au départ demandé.

## Après

| Départ demandé | Départs | Régimes |
|---|---|---|
| 55 ans | 1er mars 2019, `depart` ; 1er décembre 2026, `ouverture` | la CRPNPAC, puis le régime général, l'Agirc, l'Arrco et l'Agirc-Arrco |
| 50 ans | 1er mars 2014, `depart` ; 1er décembre 2026, `ouverture` | de même |
| 63 ans | un seul, le 1er mars 2027 | tous |

À 55 ans, la CRPNPAC reste 33 677,96 € ; le régime général, servi le 1er décembre 2026,
vaut 12 715,13 € de 2026, soit 10 768,88 € de 2019 (SR 41 906,17 × 39,375 % ×
131/170 : le taux, 50 % − 17 × 0,625 %, est celui que le modèle lit à 62 ans et 9 mois ;
le calcul du régime général n'est pas touché ici) ; l'Agirc, l'Arrco et l'Agirc-Arrco,
au coefficient 0,8175 du modèle, 8 522,75, 4 391,31 et 76,13 € de 2019. Mêmes valeurs
sous `PRESOMPTIONS_DECALEES=1`.

## Tests, témoins, coût

`tests/test_ouverture_des_navigants.py` (quatre cas, trois vus rouges puis verts, celui de
63 ans vert avant comme après) : les départs, servis par le portage et refaits par le
moteur Python (`servi_et_refait`) ; le jumeau Python, les régimes de chaque départ.
Aucun témoin ne bouge (`construire_temoins.py`), et `regenerer.py --verifier` dit tout à
jour : le paquet, les agrégats, le chiffrage et les pages ne bougent pas. Le cliquet des
textes ne bouge pas (9 331). La fiche `liquidation_regime_par_regime` porte les textes,
la citation et la lecture du jour.

## Ce que le texte ne tranche pas, et les restes

- **Les vingt annuités.** R. 426-11, I, 2° (et R. 6527-21) ne sert la CRPNPAC qu'avec
  vingt annuités avant l'âge de R. 426-12 ; le modèle ne l'oppose pas : né en 1964, entré
  à quarante ans et parti à cinquante-cinq, quinze annuités, il touche la CRPNPAC
  (13 548,91 €, 59/120). Défaut candidat, hors de la question posée.
- **Avant 1995**, l'âge de cinquante ans ne vient pas de R. 426-11 (sa rédaction de
  1984 n'en parle pas) : l'article qui le fixait n'a pas été relu sur le régime général.
  La séparation est appliquée à toute date, comme celle de la CARPV et de la CAVEC.
- **L'Agirc-Arrco** suit le régime général, présomption du modèle pour toute
  complémentaire des salariés ; son anticipation (fiche
  `coefficients_anticipation_agirc_arrco`) n'a pas été relue ici.
- **Le compte professionnel de prévention** : la limite de l'anticipation (L. 4163-7, 3°)
  n'a pas été lue ; le cas n'en déclare pas.
- **Le cas type** : `ouvrir.age_ouverture_droit`, qui date un cas type, rend cinquante
  ans au navigant, l'âge de la CRPNPAC ; le paquet n'en bouge pas, non instruit.
- Le bloc « Reprise » de l'action 130, que la file E récrit, devrait dire : « La
  CRPNPAC se sert à son âge, le régime général et l'Agirc-Arrco du navigant à l'âge de
  L. 161-17-2 (`130/2026-11-05-crpnpac-et-regime-general.md`) ; restent les statuts de
  la CAVOM, de la CARPIMKO, de la CAVP, de la CARCDSF et de la CPRN, et le défaut
  candidat des vingt annuités de la CRPNPAC. »

Renvoi du 5 novembre 2026 : l'âge de la CRPNPAC avant 2012, la citation de R. 426-16-1, R. 6527-21, le décret n° 2011-1500, R. 426-15-4, D. 351-1-1 et les témoins du navigant sont repris dans `2026-11-05-retouches-de-la-relecture-r-n.md`.
