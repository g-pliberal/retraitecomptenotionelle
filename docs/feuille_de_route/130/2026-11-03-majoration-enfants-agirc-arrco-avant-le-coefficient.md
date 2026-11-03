# La majoration pour enfants de l'Agirc-Arrco, avant le coefficient d'anticipation

**La demande.** Le 3 novembre 2026, le propriétaire décide (décision 15) de
calculer la majoration pour enfants nés ou élevés de l'Agirc-Arrco comme la
caisse, sur l'allocation avant le coefficient d'anticipation, pour les
périodes où les textes le disent ; la session d'orchestration confie l'étape
à la file M3 (action 130). Le constat venait de la file E
(`130/2026-11-03-carte-des-fiches-majoration-enfants-agirc-arrco-lue-au-droit.md`,
premier écart ; `130/2026-11-03-carte-des-fiches-coefficients-anticipation-agirc-arrco-lus-au-droit.md`,
« Ce que la lecture ajoute à la question de l'ordre »).

## Ce que disent les textes

Lus pendant la session, sur les copies de la caisse, téléchargées le
3 novembre 2026 ; chaque empreinte est celle que la fiche portait.

- **Les accords et leurs annexes ne tranchent pas.** L'accord Arrco du 25 avril
  1996 majore « leur allocation » (article 11 : « une majoration de leur
  allocation égale à 5 % ») et affecte du coefficient « les points de retraite
  effectivement inscrits au compte de l'intéressé » (article 10) ; l'accord du
  18 mars 2011 (article 7) majore « leur allocation » de 10 % ; l'annexe A de
  l'accord de 1961 (article 17, 2) et l'annexe I de la convention de 1947
  (article 6 bis, 2), mises à jour au 1er janvier 2018, une majoration « égale
  à 10 % de l'allocation correspondant à cette partie de carrière », et le
  coefficient sur « les points de retraite inscrits au compte » (articles 18
  et 6) ; l'accord du 17 novembre 2017, « une majoration de son allocation »
  (article 94), et le coefficient « aux points de retraite inscrits au compte »
  (article 84, 2). L'avenant n° 15 du 16 mars 2023 (circulaire 2023-03-DRJ,
  sha256 2c5ea4de…) ne modifie que les articles 79 et 85 : l'article 94 est
  inchangé.
- **De 2012 à 2018, le guide de la caisse tranche, et pour l'Arrco seul.**
  Guide des salariés n° 9, « Majorations pour enfants », mars 2017 (sha256
  9dfcdaf5…), « Les modalités d'attribution et de calcul », 2. « Retraite
  minorée » : « Lorsque la retraite est minorée : le régime Arrco ne tient pas
  compte du coefficient de minoration pour le calcul des majorations pour
  enfants ; le régime Agirc en tient compte. » La note de la file E le disait
  de 2012 à 2018 : le guide ne donne pas de date, il décrit les retraites de
  mars 2017, sous les annexes « applicables aux liquidations d'allocations
  prenant effet à compter du 1er janvier 2012 », dont la rédaction est la même
  jusqu'en 2018. Le modèle lit le guide pour toute la période : une lecture,
  déclarée à relire.
- **Depuis 2019, la circulaire tranche, pour tous.** Circulaire n° 2020-02-DRJ
  du 20 janvier 2020 (sha256 52477988…), qui « précise [...] la réglementation
  Agirc-Arrco applicable aux individus à compter du 1er janvier 2019 », fiche 4,
  II.2.1 : « La majoration est calculée sur les droits de base du participant
  sans tenir compte des coefficients d'anticipation éventuellement appliqués » ;
  II.2.3, de même pour les enfants à charge. Aucune circulaire plus récente des
  règles des individus n'est à la liste de la caisse le 3 novembre 2026 ; son
  site réglementaire refusait la connexion (certificat).
- **Avant 2012, rien ne tranche** : ni l'accord de 1996, ni les règlements
  d'avant 1999, que le dépôt ne lit pas. Le modèle garde le coefficient, et la
  fiche le déclare.
- **Le plafond.** Depuis 2019, il borne la majoration ainsi calculée : « La
  majoration pour enfants nés ou élevés est plafonnée au montant du cumul des
  plafonds » (II.2.2), « celui en vigueur à la date d'effet de sa retraite » ;
  le coefficient ne la touche pas. À l'Arrco de 2012 à 2018, de même. À
  l'Agirc de 2012 à 2018, qui « tient compte » du coefficient, aucun texte lu ne
  dit s'il frappe la majoration avant le plafond, comme le modèle, ou le
  montant plafonné ; les exemples du guide partent au taux plein. Gardé et
  déclaré à relire.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; la base de la Cnav, rien de neuf.
- **Le test d'abord.** Un fichier neuf,
  `tests/test_majoration_enfants_agirc_arrco_avant_coefficient.py` : six
  carrières, de la requête du simulateur à la pension, servies par le portage
  et refaites par le jumeau (`servi_et_refait`) ; neuf assertions, cinq vues
  rouges pour la raison attendue, les quatre témoins verts. Dans
  `tests/test_agirc_arrco_au_droit.py`, un test neuf, vu rouge : chaque version
  nomme les régimes calculés sans le coefficient, ceux que les textes disent,
  et le moteur lit la fiche. Le portage changé, le jumeau seul en arrière : sa
  confrontation rougit (« le moteur Python ne refait pas ce que le portage
  sert », 15 écarts) ; porté, tout est vert, et `test_pont.py -k refait` au bit
  près.
- **La fiche `majoration_enfants_agirc_arrco`** : chaque version porte
  `sans_anticipation`, aucun régime avant 2012, ceux de l'Arrco de 2012 à 2018
  (`arrco`, ses deux tranches 2, `arrco_cultes`), tous depuis 2019 ; les
  versions de 2012 citent le guide, celles de 2019 la circulaire, mot pour
  mot. L'approximation de l'assiette ne vaut plus qu'avant 2012 ; quatre
  lectures à faire s'ajoutent (plus bas). La fiche de l'enfant à charge : son
  approximation, devenue fausse, est récrite pour ce qui reste.
- **Le moteur lit la fiche** : elle entre dans `FichesDatees` (le paquet en
  porte les versions, 5 Ko) ; `regimesSansAnticipation` (`completer.js`) et son
  jumeau `regimes_sans_anticipation` (`completer.py`) lisent la version de la
  date d'effet ; la majoration de chaque régime nommé se pose sur l'allocation
  divisée par son coefficient (`anticipations`, que `liquider` écrit déjà pour
  l'enfant à charge), puis le plafond la borne. Le coefficient divisé est celui
  que la pension porte : l'âge, les trimestres manquants, la tranche C d'avant
  2016, ce que la circulaire appelle « les coefficients d'anticipation ».
- **La confrontation à OpenFisca** (`tests/test_oracle_points_enfants_arrco.py`) :
  le profil parti en 2014 avec quinze trimestres de décote, dont OpenFisca
  minore la majoration de l'Arrco, ne concorde plus ; le dépôt sert la
  majoration entière, 106,07 €, celle qu'OpenFisca compte avant de la minorer.
  L'écart est d'OpenFisca, déclaré dans le test et la fiche ; les profils de
  2004 et de 2011 concordent toujours.

## Les calculs posés à la main

« Nombre de points de retraite (de la période) × valeur du point × Taux de
majoration » (guide n° 9), sur les points et la valeur que la pension affiche ;
le coefficient, celui de la table de l'âge.

| Cas | Régime | Points × valeur | Taux | Coefficient | Avant | Après |
|---|---|---|---|---|---|---|
| Née en 1955, au travail de 1999 à 2011, partie à 62 ans le 1er avril 2017 | Arrco | 1 639,06 × 1,2513 = 2 050,96 € | 5 % | 0,78 (67 ans − 5) | 79,99 € | **102,55 €** |
| La même, cadre à deux salaires moyens | Arrco | 1 861,60 × 1,2513 = 2 329,42 € | 5 % | 0,78 | 90,85 € | **116,47 €** |
| La même | Agirc | 10 917,05 × 0,4352 = 4 751,10 € | 8 % | 0,78, gardé | 296,47 € | 296,47 € |
| Née en 1960, au travail depuis 2012, partie à 62 ans le 1er avril 2022 | Arrco | 913,54 × 1,2841 = 1 173,08 € | 10 % | 0,78 | 91,50 € | **117,31 €** |
| La même | Agirc-Arrco | 413,69 × 1,2841 = 531,22 € | 10 % | 0,78 | 41,44 € | **53,12 €** |
| La même, partie à 67 ans le 1er avril 2027 | Arrco | 913,54 × 1,4587 = 1 332,58 € | 10 % | aucun | 133,26 € | 133,26 € |
| La même | Agirc-Arrco | 1 067,56 × 1,4587 = 1 557,25 € | 10 % | aucun | 155,73 € | 155,73 € |
| Née en 1948, au travail de 1999 à 2007, partie à 62 ans le 1er avril 2010 | Arrco | 1 130,12 × 1,1884 = 1 343,03 € | 5 % | 0,88 (0,78 + 8 × 0,0125), gardé | 59,09 € | 59,09 € |

Le plafond : une cadre née en 1962, au travail depuis 2012 à 4,25 salaires
moyens, partie à 64 ans le 1er avril 2026, coefficient de 0,88 (67 ans − 3) :
21 769,99 × 0,500333 + 9 067,80 × 1,4386 + 1 046,03 × 1,4386 = 25 442,00 € de
droits, dont 10 % font 2 544,20 € sans le coefficient et 2 238,90 € avec lui ;
le plafond de 2026, « reste fixé à 2 367,48 € » (circulaire 2025-15-DT), passe
entre les deux. Avant, 2 238,90 € ; après, **2 367,48 €**. Les 155,73 € du
taux plein se lisent 155,72 € sur les points affichés, arrondis au centième.

## L'effet

`resumer_temoins.py` : 3 témoins de simulation sur 930 bougent, tous à la
hausse ; aucun rendu de page ne change. `enfants_pere`, né en 1975, parti à 64
ans, +93,73 € par an (+0,31 % de la pension, +3,5 % de la majoration) ;
`enfants_carriere_incomplete`, née en 1975, partie à 64 ans, +93,73 € (+0,27 %,
+3,1 %) ; `departs_prive_puis_categorie_active_trois_enfants`, partie à 57 ans,
+10,77 € (+0,04 %, +0,4 %), dans les scénarios 1, 3 et 5. Pour qui part avant
l'âge du taux plein, la majoration de l'Arrco, depuis 2012, et de toute la
complémentaire, depuis 2019, croît de l'inverse du coefficient : +1 % à 0,99,
+28 % à 0,78, sous le plafond.

## Ce que l'étape laisse

- **À relire, inscrit à la fiche** : avant 2012, la caisse calculait-elle la
  majoration sans le coefficient ? ; le guide de mars 2017, lu pour les
  retraites de 2012 à 2018 (une édition de 2012 le confirmerait) ; à l'Agirc de
  2012 à 2018, le coefficient avant ou après le plafond ; le site réglementaire
  de la caisse.
- **Trouvé en lisant, non traité** : l'accord Agirc du 9 février 1994
  (article 2) affecte les majorations pour charges de famille de l'article 6
  bis de l'annexe I « d'un pourcentage de service » de 96 % en 1995, 85 % en
  1996, 80 % à compter du 1er janvier 1997 ; le modèle ne le sert pas, et
  jusqu'à quand il a valu reste à lire. À la fiche, à relire.
- **L'enfant à charge à l'Agirc de 2012 à 2018** : le guide dit que l'Agirc
  « tient compte » du coefficient « pour le calcul des majorations pour
  enfants », les deux peut-être ; le modèle la calcule sur les droits bruts,
  sans lui. Déclaré dans la fiche `majoration_enfants_a_charge_agirc_arrco`.
- Les tâches suivantes de la file : l'exemption des parents de trois enfants à
  l'Agirc-Arrco, l'Ircantec, le RCI.

## Ce qui attend le propriétaire

Rien de bloquant. Une question, s'il veut aller au bout : faut-il chercher
(auprès de la caisse) l'assiette d'avant 2012 et celle de l'Agirc de 2012 à
2018 sous le plafond ? Le modèle garde, pour l'une et l'autre, le calcul
d'avant, déclaré.
