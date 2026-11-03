# La durée de la CRPCEN et de la Comédie-Française, lue à soixante ans

**La demande.** Le 2 novembre 2026, le propriétaire décide de corriger d'après
le texte, sans attendre la confirmation des caisses, comme pour la RATP, la
durée que la note `130/2026-11-02-duree-des-agents-sncf-et-ratp-qui-partent-tot.md`
laissait à la CRPCEN et à la Comédie-Française, et de vérifier ce qu'elle
disait de la CRPCEN et de la Banque de France pour qui part avant soixante ans.
La session d'orchestration la confie à la file G. Des données changent ; aucune
ligne du moteur.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; l'index LEGI, à jour de
  l'incrément du 2 novembre 2026 au soir ; `textes.py --inscrire`, quatorze
  rédactions anciennes « à examiner », hors de ce sujet, qu'une autre session
  a publiées la première. Lus : le
  III de l'article 85 du décret n° 90-1215 (CRPCEN, pour les pensions de 2017
  à 2024, abrogé en 2025), le VI de l'article 12 du décret n° 68-960
  (Comédie-Française, pour les pensions de 2017 et après, en vigueur),
  l'article 31-1 du règlement de la Banque de France (de 2012 à 2024) : la
  règle de l'article 9-1 des IEG, mot pour mot. La page « La décote » de la
  CRPCEN ne détaille pas les nés avant 1960 (« Entre 155 et 167 »).
- **Le test d'abord.** `tests/test_duree_lue_a_soixante_ans.py`, neuf : le
  calendrier de 2008 et les tables de 2014 recopiés des textes ; onze cas
  après soixante ans pour chacun des deux régimes, lus par le moteur ; chaque
  mois de naissance de 1955 à 1961, parti le mois où son droit s'ouvre ; huit
  cas avant soixante ans à la CRPCEN et à la Banque de France ; les tables
  neuves confrontées, ligne à ligne, au calendrier à soixante ans ; et la
  carrière longue que le modèle ouvre au clerc et à l'agent de la Banque. Vus
  rouges, vingt échecs : 165 au lieu de 164, 166 au lieu de 165, dix mois de
  naissance par régime, et la génération de l'assuré au lieu de celle qui a
  soixante ans. Le test de la Comédie-Française de `tests/test_simulateur.py`
  attendait la lecture d'avant, 166 trimestres pour la sociétaire née en
  janvier 1958 : il attend 165, le VI de l'article 12 à l'appui.
- **La donnée.** Dans `legislation/duree_requise_regimes_speciaux.csv`, deux
  tables neuves, `crpcen_calendrier_a_60` et
  `comedie_francaise_calendrier_a_60` : les marches du calendrier de 2008
  déplacées de soixante ans, 164 trimestres pour la génération de juillet
  1956, 165 pour celle de juillet 1957, 166 pour celle de juillet 1958, qui
  répondent aux conditions réunies depuis 2017 et se lisent, avant soixante
  ans, à la génération qui les atteint ; les périodes de 2017 et après de
  `regimes/crpcen.yaml` et la période de 2012 de
  `regimes/comedie_francaise.yaml` les nomment après la table de 2014. Et
  l'âge de lecture, soixante ans, sur `crpcen_2014` et
  `banque_de_france_2014`. Les notes des trois fiches de régime, l'en-tête
  du fichier et, dans `legislation/reformes.yaml`, la décision de la
  Comédie-Française à la suspension de 2026 le disent. Le cliquet des textes
  descend de cinq, à 9 418 : la fiche cite les rédactions lues.
- **L'effet**, l'assuré parti à l'ouverture de son droit : le clerc et le
  sociétaire nés de mars à juin 1957 doivent 164 trimestres et non 165, ceux
  de janvier à juin 1958 165 et non 166 ; le clerc qui réunit les conditions
  avant soixante ans, au titre d'une carrière longue, de juillet 2019 à 2024,
  et l'agent de la Banque, de 2018 à 2024, la durée de la génération qui a
  soixante ans le
  mois où il réunit les conditions, un trimestre de moins quand une marche
  les sépare. Rien à la Banque de France après soixante ans ; rien ailleurs.
- **Ce que les témoins déplacent** (`resumer_temoins.py`) : un des 915, le
  clerc de `reversion_clerc_de_notaire`, né en janvier 1958, parti à
  soixante-deux ans avec 164 trimestres, +1,76 % aux scénarios 1, 3 et 5
  (164/165 au lieu de 164/166, et un trimestre de décote de moins). Deux
  témoins neufs (`scripts/construire_temoins.py`) tiennent le portage : le
  clerc né en mars 1957, parti à l'ouverture de son droit en août 2017,
  157 trimestres sur 164, et non 165 ; le sociétaire né en janvier 1958,
  parti en octobre 2018, 159 sur 165, et non 166. La régénération refait le
  paquet, le tableau de bord et les chiffres ancrés ; aucun rendu de page ne
  change.
- **La fiche `regimes_speciaux_par_generation`** prend la Comédie-Française et
  la Banque de France, dont la durée propre n'avait pas de fiche, la règle
  dans son intitulé, l'effet, les lectures, les textes, le test ; elle reste
  conforme, et déclare, dans ce qu'il faut relire, qu'aucune caisse ne
  confirme ces durées.

## Ce que l'étape laisse

- **Les caisses** : ni la CRPCEN, ni la caisse de la Comédie-Française, ni la
  Banque de France ne publient la durée des générations 1957 et 1958, ni
  celle de qui part avant soixante ans. La lecture des trois articles n'est
  confrontée à aucune valeur de caisse.
- **La durée « applicable avant »** que la CRPCEN et la Banque gardent, depuis
  2025, à qui a réuni les conditions plus tôt : le dépôt la lit à soixante
  ans, comme leurs articles abrogés, et comme aux IEG — une lecture, non un
  texte.
- **Le mois où un départ anticipé réunit les conditions.** Pour les régimes
  spéciaux, le moteur le date au mois de la liquidation
  (`mois_ouverture_des_droits`), quand il prend, pour le fonctionnaire,
  l'âge que la carrière longue lui ouvre (`duree_requise_avant_soixante_ans`).
  Qui part plus tard que ce mois-là lit la durée d'une génération trop jeune,
  et, s'il a réuni les conditions avant 2025 et part après, la table de 2023
  au lieu de celle de 2014. Une règle du moteur, pour toutes les caisses : à
  mesurer avant d'y toucher.
- **Ailleurs, la même règle ne déplace rien** (« la classe, pas le cas ») :
  l'Opéra lit déjà sa table à soixante ans, et son ballet, que sa fiche sert,
  part à quarante ans ; les agents des IEG, de la SNCF et de la RATP que le
  modèle sert ouvrent leur droit avant soixante ans ; les autres, qui
  l'ouvriraient après, ne sont pas modélisés. La fonction publique a sa
  propre lecture, à l'année.
- **Les quatorze rédactions inscrites** (ordonnance n° 58-1270, lois n° 83-1179
  et n° 89-18, décrets n° 50-1348 et n° 80-7), à examiner par la session de
  leur domaine.

## Ce qui attend le propriétaire

Rien pour cette étape.
