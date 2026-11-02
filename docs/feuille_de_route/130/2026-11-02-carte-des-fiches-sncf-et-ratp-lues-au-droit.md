# La carte des fiches : la SNCF et la RATP lues au droit, quatrième lot

**La demande.** Le 2 novembre 2026, le propriétaire fait ouvrir six sessions
en parallèle par la session d'orchestration ; celle-ci, la file E, fait mûrir
un lot de la carte (action 130), hors des régimes des autres files, après le
RAFP, la CNAVPL et les IEG (`130/2026-10-29-carte-des-fiches-ieg-lus-au-droit.md`).
Le lot pris : les régimes spéciaux de la SNCF et de la RATP, dont les trois
fiches qui ne portent qu'eux n'étaient pas mûres : `age_reference_decote_sncf_ratp`,
`age_surcote_sncf_ratp` et `duree_requise_sncf_ratp`. Aucun chiffre du modèle
ne bouge.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF récupérés
  et mis à jour jusqu'à l'incrément du 2 novembre ; `textes.py --inscrire`,
  sans rédaction nouvelle.
- **Le test d'abord.** Les trois fiches entrent dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vu rouge de leurs dix-huit manques. Et un fichier
  neuf, `tests/test_sncf_ratp.py`, vu rouge faute de versions : ce que chaque
  version lit, les périodes de `regimes/sncf.yaml` et de `regimes/ratp.yaml` et
  les tables qu'elles nomment le portent ; cinq cas tiennent ce que le modèle
  fait autrement que le droit, et que la fiche déclare. Une valeur altérée dans
  chaque fiche le fait rougir.
- **Les rédactions, article par article**, chacune contre la suivante : au
  décret n° 2008-639 (SNCF), les articles 1er, 12-1, 13, 35 et 37-1 ; au décret
  n° 2008-637 (RATP), les articles 6, 23-1, 24, 51 et 51-1 ; au Journal
  officiel, ce que les décrets n° 2011-291 (article 18), n° 2011-292
  (article 13), n° 2023-967 (article 2) et n° 2023-690 (article 3) reportent,
  et à quelles pensions. Trois rédactions de 2011 que le lot lit (articles 12-1
  et 37-1 de la SNCF, 23-1 de la RATP) ne sont jamais entrées en vigueur :
  l'index les date du 1er janvier 2017 et les clôt en 2014. Les règlements
  d'avant le 1er juillet 2008 ne sont dans aucun index — du décret
  n° 2005-1639, qui publiait celui de la RATP, l'index JORF n'a que l'en-tête :
  les versions d'avant sont supposées.
- **La caisse** : les tableaux par génération de la CPRPSNCF, agents de
  conduite et cas général, d'octobre 2023 (âge d'ouverture, trimestres requis,
  décote, âge d'annulation, âge de la surcote). La CRP RATP et Légifrance
  répondent 403 au réseau de la session.
- **`age_reference_decote_sncf_ratp`**, du domaine de la décote et de l'étape
  qui liquide : quatre versions sur la date d'effet et le mois où le droit
  s'ouvre — rien sous les règlements d'avant (supposée), ni à qui ouvre son
  droit avant juillet 2010 ; l'âge minimum majoré de cinq ans, diminué de seize
  trimestres à rien de 2010 à 2024 ; depuis 2025, cinquante-sept ans pour
  l'agent de conduite et le roulant, soixante-deux et soixante-sept pour les
  autres. Deux lectures divergentes : la CPRPSNCF garde l'âge d'avant à qui a
  ouvert son droit avant 2025, quand l'article 13 écrit cinquante-sept ans pour
  toute pension de 2025 (la fiche suit la caisse, comme aux IEG ; la RATP
  l'écrit, au 2° du VII de l'article 51-1) ; et la caisse donne cinquante-six
  ans et neuf mois à l'agent de conduite né en 1973 ou 1974, qu'aucun texte lu
  ne fonde. Approchée, de conforme : l'agent présumé agent de conduite ou
  roulant.
- **`age_surcote_sncf_ratp`**, même domaine, même étape : quatre versions sur
  la date d'effet — rien avant juillet 2008 (supposée) ; soixante ans ; dès le
  21 mars 2011, l'âge légal de soixante-deux ans abaissé par génération,
  soixante ans pour les nés avant 1957 ; pour les pensions de 2025, jusqu'à
  soixante-quatre ans pour 1970. L'index date du 1er janvier 2017 l'article
  37-1 qui porte le calendrier de 2011, mais l'article 18 du décret n° 2011-291
  n'en reporte que le V, et nul agent ne pouvait atteindre avant 2017 un âge
  relevé. Approchée, de conforme : ni le second semestre de 2008, ni la surcote
  des parents dès soixante-trois ans (IV des articles 13 et 24, pensions de
  2025) ne sont servis.
- **`duree_requise_sncf_ratp`**, du domaine de la durée et de l'étape qui
  ouvre le droit : quatre versions sur le mois où le droit s'ouvre — 150
  trimestres avant juillet 2008 (supposée) ; le calendrier de 2008, de 151 à
  166 ; les tables de 2014 depuis juillet 2019 ; les tables de 2023, avec ce
  que la SNCF retranche pour la décote par la durée. Approchée, de conforme,
  pour l'écart qui suit.
- **Le cliquet des textes** descend de 9 445 à 9 435. **La carte** passe de 98
  fiches à lire au droit à 95, de 587 manques à 569. `conservation.py --depuis
  HEAD` dit changées les lignes de veille des trois fiches, refaites depuis
  elles, ce que la référence figée admet.

## Ce que l'étape laisse

- **Une erreur du modèle, pour une étape du modèle** (la file E ne touche pas
  au modèle) : la durée de l'agent qui part avant cinquante-cinq ans (SNCF,
  article 12-1) ou soixante ans (RATP, article 23-1). Pour les pensions de 2017
  et après, il doit celle de la génération qui atteint cet âge l'année où son
  droit s'ouvre ; depuis 2025, 170 trimestres, un de plus tous les trois ans.
  Le modèle lit la table de 2014 à la génération de l'agent : un ou deux
  trimestres de trop pour l'agent de conduite né de novembre 1968 à 1972, deux
  ou trois pour le roulant de la RATP (171 au lieu de 168 pour celui né en
  1970), puis, à la RATP, 172 au lieu de 170 de 2025 à 2027. La correction est
  une donnée : la colonne `age_de_lecture` de
  `legislation/duree_requise_regimes_speciaux.csv`, que les IEG emploient, à
  55 pour `sncf_2014` et 60 pour `ratp_2014`, et une durée par année à la RATP
  depuis 2025 ; `test_ce_que_le_modele_fait_autrement_la_fiche_le_declare`
  rougira alors, et la fiche perdra ses approximations.
- **À lire dans la fiche `surcote_regimes_speciaux`** : la période de 2009 à
  2017 de la SNCF porte une surcote de 0,75 % par trimestre, celle de 2009 à
  2016 de la RATP 1,25 %, sous la même phrase des deux décrets, que L. 14 fixe
  à 1,25 % depuis le 19 décembre 2008 ; et la limite de vingt trimestres, que
  les décrets gardent jusqu'en 2016, `trimestres_de_surcote_regimes_speciaux`
  ne la porte pas.
- **À demander à la CPRPSNCF** : le texte de ses âges d'annulation de l'agent
  de conduite né en 1973 ou 1974 et de l'agent du cas général né de 1967 à
  1971. Ses tableaux par génération pourraient entrer dans
  `exemples_officiels.yaml`.
- **Le 2° du VII de l'article 51-1 de la RATP** : l'âge de référence « applicable
  avant », de 2025 à 2033, se lit-il avec l'âge d'ouverture d'avant 2023 ou avec
  le nouveau ? La fiche, comme le modèle, retient cinquante-sept ans au tableau B.
- Les 95 fiches à lire au droit. Ce que ce lot ajoute aux précédents : un
  décret se lit article par article dans LEGI, mais ce qu'il reporte, et à
  quelles pensions, n'est qu'au Journal officiel, à lire avant de dater une
  version ; LEGI date parfois un article entier de sa seule partie reportée ;
  le tableau d'une caisse par génération se rejoue mieux qu'une phrase.
- `regenerer.py --verifier` dirait périmé le tableau de bord, qui compte la
  carte ; GitHub le refait.

## Ce qui attend le propriétaire

Une question : ouvrir une étape du modèle pour corriger la durée des agents de
la SNCF et de la RATP qui partent tôt, une donnée à changer. Pour le reste,
rien de neuf : la septième étape du sixième domaine, la décision de la
proposition, et celle sur la retraite progressive, le cumul et la seconde
pension, README muet.
