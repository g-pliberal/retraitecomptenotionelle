# La carte des fiches : la CNAVPL lue au droit, deuxième lot

**La demande.** Vague du 28 octobre 2026 : le propriétaire demande une session
par tâche qui se mène sans lui ; la session de suivi ouvre celle-ci après le
premier lot des fiches à lire au droit, le RAFP
(`130/2026-10-29-carte-des-fiches-rafp-lu-au-droit.md`). Celle-ci : un lot plus
large des 104 qui restaient, selon `docs/veille_droit.md`. Le lot pris est un
régime, le régime de base des professions libérales, dont les trois fiches qui
ne portent que lui n'étaient pas mûres : `points_au_prorata_des_cotisations`,
`cnavpl_valeur_service` et `cnavpl_majoration_duree_assurance`. Aucun chiffre du
modèle ne bouge.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF récupérés
  et mis à jour, jusqu'aux incréments du 28 et du 29 octobre ; `textes.py
  --inscrire`, sans rédaction nouvelle avant la lecture.
- **Le test d'abord.** Les trois fiches entrent dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vu rouge de leurs dix-huit manques. Et, dans
  `tests/test_sections_liberales.py`, deux confrontations des versions aux
  données, vues rouges faute de versions : chaque année de revenu que couvre une
  version des points a, dans `regimes/cnavpl.yaml`, des périodes qui portent ses
  points au plafond, ses tranches et le prorata, ou ses cent points par trimestre
  avant 2004 ; les deux valeurs que D. 643-1 écrit, 0,484 € et 0,493 €, sont
  celles de `regimes/valeurs_point.csv`.
- **`points_au_prorata_des_cotisations`**, du domaine des points et de l'étape
  qui acquiert les droits : quatre versions sur l'année du revenu. Avant 2004,
  l'allocation en soixantièmes de l'allocation aux vieux travailleurs salariés
  (R. 643-10), que la loi n° 2003-775 transforme en points, cent pour un
  soixantième (article 96, II). Puis D. 643-1, la cotisation au plafond de
  chaque tranche de D. 642-3 : 450 et 100 points de 2004 à 2014, sur 85 % du
  plafond puis jusqu'à cinq ; 525 et 25 de 2015 à 2024, sur un plafond et sur
  cinq ; 557 et 25 depuis 2025 ; au prorata de la cotisation, arrondis au
  dixième. Approchée, de transcrite : le modèle n'arrondit pas, et réduit les
  plafonds d'une année incomplète au mois, quand le texte compte les trimestres
  d'affiliation, que R. 643-1, dans ses quatre rédactions, fait commencer et
  finir au premier jour du trimestre civil qui suit le début ou la fin de
  l'activité. Neuf rédactions d'avant 2004 entrent sans effet : l'allocation
  n'avait pas de points, ni sa cotisation.
- **`cnavpl_valeur_service`**, du domaine des points et de l'étape qui liquide :
  quatre versions sur la date d'effet. Avant la codification de 1985, une version
  supposée : les textes du régime d'allocation de 1948 à 1985 n'existent qu'au
  fac-similé, l'index du JORF n'en gardant que l'analyse. De 1985 à 2003,
  l'allocation de L. 643-1 et R. 643-10, dont la loi de 2003 fait des points « au
  prorata de leur montant monétaire ». De 2004 au 18 décembre 2008, la valeur
  fixée par décret : 0,484 € et 0,493 € (D. 643-1), puis revalorisée au moins
  comme les pensions (décret n° 2005-1004, article 4). Depuis, revalorisée dans
  les conditions de L. 161-23-1 (loi n° 2008-1330, article 79) : au 1er avril, au
  1er octobre, au 1er janvier, et de 4 % au 1er juillet 2022 (loi n° 2022-1158).
  Approchée, de transcrite : le modèle liquide à la valeur du 31 décembre, de 0,1
  à 4 % trop haute avant le relèvement de l'année, et ramène par les prix le
  point de 2004 aux liquidations d'avant, de 1,7 % trop bas en 1985, à 0,2 % près
  depuis 1995, mesuré sur l'allocation aux vieux travailleurs salariés.
- **`cnavpl_majoration_duree_assurance`**, du domaine des enfants et de l'étape
  qui compte les durées : quatre versions sur la date d'effet — rien avant le 1er
  avril 2010, L. 351-4, L. 351-4 à L. 351-4-2 depuis le 11 novembre 2010 (D. 643-2
  compte ces trimestres depuis 2012), L. 351-12 et la surcote parentale pour les
  pensions depuis le 1er septembre 2023. La fiche se trompait deux fois : elle
  datait de 2023 l'extension à L. 351-4-1 et L. 351-4-2, de 2010 et de 2014 ; et
  la maille annuelle ne prive pas les pensions d'avril à décembre 2010, elle donne
  la majoration à celles de janvier à mars, que le texte en exclut — une libérale
  née en 1949, mère de deux enfants, partie en février 2010, y gagne seize
  trimestres et 32 % de pension de base. Les majorations de l'enfant handicapé et
  de l'aidant ne sont pas servies, la saisie ne les portant pas.
- **Le cliquet des textes** descend de 9 494 à 9 447 : trente-huit rédactions
  sans statut sont citées par une version, et neuf entrent sans effet.
  L'inscription qui suit apporte le décret n° 2005-1004 et la loi n° 2022-1158,
  que les fiches citent : vingt-quatre rédactions, « à examiner » hors des deux
  qu'une version cite.
- **La carte** passe de 104 fiches à lire au droit à 101, de 618 manques à 600 ;
  elle compte deux fiches transcrites de moins, deux approchées de plus.

## Ce que l'étape laisse

- Les 101 fiches à lire au droit, par lots d'un régime ou d'un domaine. Ce que
  ce lot ajoute à ceux du premier : un texte d'avant la codification de 1985 n'a
  souvent dans l'index du JORF que son analyse, et la version qui le couvre est
  supposée, le texte signalé ; une version qui suit un relèvement de valeur, ou
  une règle que la caisse date, se coupe à la date de son texte, et la date de
  publication de chacun se lit dans l'index du JORF.
- Lu en chemin, hors du lot : les points que D. 643-1 attribue hors de la
  cotisation — 400 par année d'incapacité d'exercice exonérée (L. 642-3), 100 pour
  le trimestre d'un accouchement, plafonnés à 550 points dans l'année depuis le
  1er mars 2012 et 582 depuis 2025, 200 par année d'assistance d'une tierce
  personne — n'ont pas de fiche, et le modèle ne les sert pas. Le plafond de
  R. 643-10 sur les droits convertis en 2004, « quatre-vingt-dix soixantièmes »,
  reste à lire dans la pratique de la caisse.
- Une correction à mener avec la fiche de la surcote, dans les deux moteurs :
  couper les périodes de `regimes/cnavpl.yaml` au 1er avril 2010 et au 1er
  septembre 2023 par leur `date_effet`. La première ôterait la majoration de
  durée aux pensions de janvier à mars 2010 ; la seconde porterait à septembre
  2023 la majoration de L. 351-12 et la surcote parentale, et le taux de surcote
  que R. 643-8 change le même jour et que la période de 2024 porte de 0,75 à
  1,25 %. La valeur de service datée au jour, une ligne de la CNAVPL dans
  `regimes/valeurs_service_datees.csv`, ôterait l'avance de la valeur relevée.

## Ce qui attend le propriétaire

Les textes du régime d'allocation des libéraux de 1948 à 1985 — la loi
n° 48-101, le décret n° 49-456 et ses modifications, les décrets n° 62-439,
n° 83-677 et n° 84-1112 — n'existent qu'au fac-similé du Journal officiel :
la version de `cnavpl_valeur_service` qui les couvre est supposée, sans rien en
présumer d'autre que leurs analyses. Le reste est inchangé : la septième étape
du sixième domaine, la décision de la proposition, et celle sur la retraite
progressive, le cumul et la seconde pension, README muet.
