# La carte des fiches : la CARMF lue au droit, dix-septième lot

**La demande.** Le 6 novembre 2026, la session d'orchestration confie à la file E
(tâche E6) la caisse suivante de la carte, après les quatre du bloc « Reprise »
(CAVOM, CARPIMKO, CAVP, CPRN) : la CARMF, dernière section de santé, et ses deux fiches,
`carmf_asv_minoration_enfants` (sept manques) et `asv_medecins_ajustement` (six), lues
au droit selon la méthode de la CPRN (`130/2026-11-05-carte-des-fiches-cprn-lue-au-droit.md`)
et la leçon de R-E4 : chercher tous les textes modificatifs, par numéro, date et titre.
Les erreurs du modèle se déclarent, chiffrées, sans être corrigées. Aucune règle du
modèle ne change.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` (rien de neuf à la base de la Cnav),
  `docs/veille_droit.md` ; les index JORF (au 6 novembre) et LEGI (au 5 novembre)
  récupérés et mis à jour.
- **Tous les textes du régime, relevés sans borne.** Par « médecins » dans le titre, avec
  « vieillesse », « retraite », « statuts », « règlement », « allocation » ou «
  prestations », de 1949 à 2026 : 182 titres, les fonctionnaires, les hospitaliers et
  les autres sections mis à part. De 1949 à 2006, l'index n'a presque que des titres :
  le règlement de 1962, l'article 22 ajouté par l'arrêté du 16 janvier 1964 (« ayant
  élevé au moins trois enfants »), les statuts du régime complémentaire (arrêté du 27
  février 1974) et de l'ASV (18 décembre 1972), et quatorze arrêtés qui les modifient,
  au seul Bulletin officiel. Depuis 2007, chaque arrêté est ouvert, article par
  article : 2007, 2008, 2009, 2010 (deux), 2011 (deux), 2014, 2016 (trois), 2017
  (trois), 2018 (deux), 2020, 2021, 2024 (deux), 2025, 2026 (le règlement du 10
  juillet et l'arrêté du 21 septembre qui le modifie) ; les décrets n° 2011-1644,
  2016-1198, 2021-645, 2022-1633, 2023-1351, 2024-1214, 2025-1076 et 2026-418. Le
  rectificatif du 8 août 2026 n'a que son titre.
- **Le test d'abord.** Les deux fiches entrent dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vues rouges de leurs treize manques ; la CARMF dans
  `NAISSANCES_AU_JOURNAL_OFFICIEL` (`tests/test_sections_liberales.py`), vue rouge faute
  de versions ; un test neuf, `test_chaque_version_de_la_carmf_est_portee_par_le_modele`
  (`tests/test_sections_sante.py`), vu rouge de même, lit chaque premier du mois de 1949
  à 2040 les paramètres de chaque version, à la complémentaire et à l'ASV, et chaque
  année depuis 2012 ceux de l'ajustement ; aucun écart à déclarer. Un second test neuf,
  `test_la_carmf_sert_ses_coefficients_dans_les_deux_moteurs`, joue trois cas du texte
  (1,10 ; 1,15 ; 1,30) sur la requête du formulaire, servis par le portage et refaits
  par le moteur Python, verts d'emblée : ils tiennent ce que le modèle rend déjà.
- **`carmf_asv_minoration_enfants`**, approchée : quatre versions sur la date d'effet.
  - **Avant le 1er janvier 2017, supposée** : des articles 15 (complémentaire) et 12
    (ASV), le Journal officiel ne montre que les mots que l'arrêté du 28 septembre 2011
    remplace, « ou de 60 ans » et « dès l'âge de 60 ans ». Les coefficients « 0,75 à 60
    ans [...] 0,95 à 64 ans » que le modèle sert de 2000 à 2016 ne sont dans aucun texte
    lu.
  - **Les statuts de 2017** (arrêtés des 30 novembre et 1er décembre 2016, « entre en
    vigueur au 1er janvier 2017 ») : l'âge du premier alinéa de L. 351-1, la majoration
    de 1,25 % par trimestre civil « après cet âge », 0,75 % après 65 ans, rien après 70.
  - **Les statuts de mars 2017** (arrêté du 22 mars 2017, publié le 29, sans date : le
    30) : « après l'âge de 62 ans ».
  - **Le règlement de 2026** (arrêté du 10 juillet 2026, le 18 juillet ; décret n°
    2026-418, article 3, 7°, et article 16) : la règle de mars 2017 ; 10 % pour trois
    enfants (I, article 23 ; III, article 8) ; la date d'effet « au premier jour du
    trimestre civil qui suit la réalisation de toutes les conditions » (I, article 24).
- **`asv_medecins_ajustement`**, approchée : deux versions sur l'année du revenu. Avant
  2012, supposée : aucun point d'ajustement (article 9 du décret n° 2011-1644 ; les
  décrets annuels de 2007 à 2010, lus, n'en nomment aucun). Depuis 2012 : l'article 3,
  d'une seule rédaction, « dans la limite de neuf points par an », « arrondi au centième
  le plus proche », les deux tiers des 27 points du forfait (décret n° 72-968, article
  2) ; l'article 2 dans ses quatre rédactions, l'assiette de « la deuxième année
  précédant ».
- **Les citations** ont été vérifiées par un script : chacune, ses morceaux séparés par
  « [...] », guillemets ôtés et espaces ramenées, se trouve dans le texte de l'index
  qu'elle nomme, et les phrases citées des textes sans effet aussi ; deux citations
  altérées exprès y échouent. Le paquet, refait, ne change pas. **La carte** passe de 78
  fiches à lire au droit à 76, de 451 manques à 438.

## Les calculs

Chaque valeur du modèle est celle des deux moteurs (essai du jour, statut
`medecin_liberal`, entré à 22 ans, deux salaires moyens, né le 10 du mois) ; chaque
valeur du texte, posée à la main. Le modèle date la pension au premier du mois qui suit
l'anniversaire (`chronologie.py`) et compte la majoration en trimestres d'âge entiers,
de 62 ans à l'âge du départ (`surcotePoints`).

- **Ce qui s'accorde.** Né le 10 mars 1955, parti à 64 ans : 62 ans le 10 mars 2017, le
  1er avril 2017 ; la pension le 1er avril 2019 ; 8 trimestres × 1,25 % = 10 %, 1,10.
  Né le 10 mars 1952, parti à 65 ans et un mois : du 1er avril 2014 au 1er avril 2017,
  12 × 1,25 % = 15 % ; du 1er avril au 1er mai 2017, aucun trimestre entier ; 1,15.
  Né le 10 mars 1950, parti à 71 ans : 12 × 1,25 % + 20 × 0,75 % = 30 %, 1,30. Les
  trois aux deux régimes, comme le modèle. L'exemple de la caisse
  `carmf_report_62_65_ans` (né le 10 novembre 1960, la pension le 1er janvier 2026 :
  du 1er janvier 2023, 12 × 1,25 % = 15 %) et les trois du guide de juin 2026 tiennent.
- **L'âge légal de janvier à mars 2017** (non tranché). Né le 10 mars 1952 : 60 ans et
  9 mois le 10 décembre 2012 (D. 161-2-1-9, 3°), parti à 64 ans et 9 mois, la pension
  le 1er janvier 2017. « Après cet âge » : du 1er janvier 2013 au 1er janvier 2017, 16
  trimestres, 65 ans n'étant atteint que le 10 mars 2017 : 20 %, 1,20. Le modèle, de 62
  ans : 11 trimestres, 1,1375. Complémentaire : 12 364,01 / 1,1375 = 10 869,46 ; × 1,20
  = 13 043,35 € ; 679,34 € par an. ASV : 15 894,81 / 1,1375 = 13 973,46 ; × 1,20 =
  16 768,15 € ; 873,34 €. Ensemble 1 552,68 € par an. L'autre lecture, celle du modèle,
  tient si la caisse a liquidé après le 29 mars, les coefficients étant « déterminés
  définitivement lors de la liquidation des droits ».
- **La date d'effet du règlement de 2026** (erreur, complémentaire). Né le 10 mai 1964,
  parti à 63 ans (D. 161-2-1-9, 10°) : le modèle sert le 1er juin 2027, le texte le 1er
  juillet ; 4 trimestres des deux côtés (du 1er juillet 2026), 1,05 ; un mois de trop,
  14 056,14 / 12 = 1 171,35 €. Né le 10 mars 1964, parti à 63 ans et un mois : le
  modèle sert le 1er mai 2027 à 1,05 ((63,0833 − 62) × 4 = 4,33, 4 trimestres) ; le
  texte, le 1er juillet 2027, à 1,0625 (du 1er avril 2026 au 1er juillet 2027, 5
  trimestres) ; deux mois de trop, 2 × 14 026,06 / 12 = 2 337,68 €, puis 14 026,06 /
  1,05 × 1,0625 = 14 193,04 €, 166,98 € par an de moins. À l'ASV, que son règlement ne
  date pas (non tranché) : 15 850,88 / 12 = 1 320,91 € ; 2 656,35 € puis 16 127,86 −
  15 938,12 = 189,74 € par an, si elle suit la complémentaire.
- **L'ASV avant 2017** (non tranché). Né le 10 mars 1949, parti à 64 ans le 1er avril
  2013 avec sa durée : le modèle sert l'ASV sans coefficient, 15 533,26 € ; si l'article
  12, récrit des mêmes mots que l'article 15, portait le même 0,95 à 64 ans : 14 756,60
  €, 776,66 € par an de moins.
- **Le revenu de l'avant-dernière année** (approximation, ajustement). Exercice 2026,
  4 %, forfait total 3 × 1 917 = 5 751 € ; revenu de 40 000 € en 2024, de 42 000 € en
  2026. Le décret : 18 × 1 600 / 5 751 = 5,0078, 5,01 points ; le modèle : 18 × 1 680 /
  5 751 = 5,2582, 0,2482 point de trop, 0,2482 × 11,82 = 2,93 € de pension annuelle par
  exercice ; l'arrondi au centième, au plus 0,005 × 11,82 = 0,06 €.

## Ce que l'étape laisse

- **L'erreur du modèle, déclarée dans la fiche, non corrigée, pour le propriétaire** :
  depuis le 18 juillet 2026, la complémentaire de la CARMF prend effet au premier jour du
  trimestre civil qui suit les conditions, et le modèle au premier du mois : un ou deux
  mois de trop, 1 171,35 € ou 2 337,68 € dans les cas posés, et, quand l'anniversaire
  tombe au premier mois d'un trimestre, 1,25 point de majoration de moins (166,98 € par
  an). La CARMF partage l'erreur du trimestre civil de la CAVOM, de la CARPIMKO et de la
  CAVP ; la correction touche la façon dont `departs` date toute unité.
- **Ce que le texte ne tranche pas** : l'âge légal de janvier à mars 2017 (1 552,68 €
  par an dans le cas posé) ; la date d'effet de 2017 à 2026, que la caisse donne au
  trimestre civil dans son guide de juin 2026 ; celle de l'ASV, que son règlement ne
  fixe pas ; l'ASV d'avant 2017 (776,66 € par an).
- **Approchés, chiffrés** : l'assiette de l'avant-dernière année (2,93 € de pension par
  exercice dans le cas posé) et l'arrondi au centième. **Nommé, non chiffré** : la base
  forfaitaire des deux premières années, dont le décret n'est pas lu (question au
  propriétaire).
- **Renvoyés, non doublés** : l'inapte et l'ancien combattant, 13 % (question 11) ; les
  périodes rachetables de l'article 18 ; le cumul et la seconde liquidation de 2027.
- **Les statuts qui manquent** : ceux d'avant le 1er janvier 2017 (complémentaire,
  ASV), l'article 22 de 1964 et l'article de l'ASV de 1981, au Bulletin officiel
  (question 22) ; le rectificatif du 8 août 2026. À demander à la CARMF, avec une
  pension prenant effet le 1er janvier 2017 d'un médecin né avant 1955.

## Le bloc « Reprise » récrit

Daté du 6 novembre 2026 : la CARMF lue au droit, 76 fiches et 438 manques ; son erreur
(la date d'effet au trimestre civil depuis 2026) et ses quatre non-tranchés au
propriétaire ; la suite, la Cipav, dernière section de la CNAVPL.

*Corrigé le 6 novembre 2026 par E6-bis, sans que ce récit soit récrit : l'article 12 ter de l'ASV, le rectificatif du 8 août, l'âge légal de 1964, les 2,96 € (non 2,93 €) de l'ajustement et l'arrêté du 7 janvier 2025 sont dans `2026-11-06-e6-bis-corrections-de-r-e7.md`.*
