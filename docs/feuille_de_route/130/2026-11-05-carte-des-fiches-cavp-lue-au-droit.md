# La carte des fiches : la CAVP lue au droit, quinzième lot

**La demande.** Le 5 novembre 2026, vague 10, la session d'orchestration confie à la file
E (tâche E4) la caisse suivante de la carte, la CAVP, et sa fiche,
`cavp_minoration_deux_pentes`, sept manques, lue au droit selon la méthode de la CARPIMKO
(`130/2026-11-05-carte-des-fiches-carpimko-lue-au-droit.md`) et la leçon de R-E4
(`130/2026-11-05-relecture-r-e4.md`) : chercher tous les textes qui modifient les statuts
sur la période, sans borne trop basse ; pour chaque erreur déclarée, vérifier que la lecture
contraire n'est pas tenable, sinon la dire non tranchée, ses deux lectures chiffrées. Ne pas
doubler ce qui est déclaré : la CAVP servie à l'âge de la base, et avant 2024 à l'âge de
carrière longue de la base (N ddc92fc, R-N2, N-bis 0ba2aea) ; l'inapte des libéraux
(question 11) ; les statuts au seul Bulletin officiel (question 22). Aucune règle du modèle
ne change.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` (rien de neuf à la base de la Cnav),
  `docs/veille_droit.md` ; les index JORF et LEGI récupérés, à jour du 5 novembre (quatre
  incréments JORF) et du 4 novembre (deux LEGI).
- **Tous les textes de la section, relevés sans borne.** Par le titre (« section
  professionnelle des pharmaciens », 77 documents ; « vieillesse », 23), et par le corps
  (« CAVP » ou « assurance vieillesse des pharmaciens », 13 arrêtés), de 1949 à 2026. De 1949
  à 1990, l'index n'a que les titres, ni article ni annexe ; celui du 31 août 1990 est au
  seul Bulletin officiel (no 90-40). Depuis 2007, chaque arrêté a son texte : 2007, 2009,
  2011, 2012, 2015, 2016, 2017, 2019, juin et décembre 2023, 2025, juillet et septembre
  2026, chacun ouvert, et rangé dans la fiche, cité ou sans effet.
- **Le test d'abord.** La fiche entre dans `LUES_AU_DROIT` (`tests/test_carte.py`), vu
  rouge de ses sept manques, et dans `NAISSANCES_AU_JOURNAL_OFFICIEL`
  (`tests/test_sections_liberales.py`), vu rouge faute de versions ; un test neuf,
  `test_chaque_version_de_la_cavp_est_portee_par_le_modele` (`tests/test_sections_sante.py`),
  vu rouge de même, lit chaque premier du mois de 1949 à 2040 les paramètres de chaque
  version dans la période du modèle, hors de deux écarts que la fiche déclare
  (`CAVP_HORS_DU_MODELE`) ; il partage avec celui de la CARPIMKO une fonction,
  `_chaque_version_est_portee`. Cinq cas du tableau de 2011 et de la majoration rejoignent
  `test_la_cavp_minore_a_deux_pentes`, verts d'emblée : ils tiennent ce que le modèle rend
  déjà.
- **Un texte qu'on croyait absent.** La fiche, le régime et son inventaire disaient le
  tableau des coefficients des nés jusqu'en 1955, « en annexe des présents statuts » de
  2011, hors de l'index. Il y est, à la fin de la même annexe (JORFARTI000024270214), et le
  modèle le rend ligne pour ligne : les deux pentes comptées depuis l'âge propre de la
  génération donnent « 62 ― 15,00 % » (né en 1950), « 62 ― 17,00 % » et « 64 ― 7,00 % »
  (nés de 1953 à 1955), « 68 4,00 % » de majoration. Les notes de
  `cavp_complementaire.yaml`, l'inventaire et `docs/regimes.md` sont récrits, le paquet
  refait.
- **`cavp_minoration_deux_pentes`**, approchée : cinq versions sur la date d'effet.
  - **Avant le 7 juin 2009, supposée** : les statuts approuvés en 1948 et 1950, que
    l'arrêté du 11 mai 2009 abroge (article 2), et leurs modifications, aux seuls titres.
    Le modèle y sert la décote de la base, que la durée annule.
  - **Les statuts de 2009** (arrêté du 11 mai 2009, publié le 6 juin, sans date : le 7),
    articles 12, 14, 15 et 17 : retraite entière à 65 ans, dès 60 ans « 1, 25 % par
    trimestre manquant dans la limite de 20 trimestres », à l'âge seul, l'inapte sans
    coefficient, l'entrée en jouissance « au premier jour du trimestre civil qui suit cette
    demande », un dixième pour trois enfants.
  - **Les statuts de 2011** (arrêté du 23 juin 2011, publié le 29, sans date : le 30),
    articles 12 et 15 récrits : les âges par génération, les deux pentes, le tableau, la
    majoration de 0,5 % par trimestre, le montant majoré de 4 % depuis 1956, de 2 % de 1953
    à 1955.
  - **Les statuts de 2024** (arrêté du 19 décembre 2023, publié le 9 janvier 2024, le 10) :
    la cessation d'activité supprimée ; l'article 15 fait suivre à la complémentaire le
    départ anticipé de la base (II, III et IV de L. 643-3), la carrière longue minorée de
    « 1,25 % par trimestre manquant jusqu'à l'âge de 65 ans ».
  - **Le règlement de 2026** (annexe I de l'arrêté du 10 juillet 2026, le 18 juillet),
    que l'article 4 du décret n° 49-580 appelle depuis le 1er juillet (décret n° 2026-418,
    articles 4 et 30) : articles 8 (valeur de service, 0,96 et 0,96/0,98), 12, 14 et 15,
    la règle de 2024.
  - Dix textes lus sans effet : 2007 (capitalisation), 2012 (invalidité-décès), 2015
    (cotisations, capitalisation), 2016 (fin du versement), 2017 et juin 2023 (statuts
    généraux), 2019 (classes), 2025 (articles 1er à 9 bis, 14 hors l'entrée en jouissance,
    16 abrogé), et l'article 2 de l'arrêté du 21 septembre 2026, la question que la fiche
    posait : il récrit l'article 16 du règlement, la réversion, qui renvoie trois fois au
    « premier alinéa de l'article 9 » pour le deuxième — ni la minoration ni son âge.
- **Les citations** ont été vérifiées par un script : chacune, ses morceaux séparés par
  « [...] », guillemets ôtés et espaces ramenées, se trouve dans le texte de l'index qu'elle
  nomme ; deux citations altérées exprès y échouent. **Le cliquet des textes** ne bouge
  pas ; aucune rédaction non lue des articles cités (`textes.py --non-lues`). **La carte**
  passe de 80 fiches à lire au droit à 79, de 464 manques à 457.
- **Les deux moteurs** ont joué chaque cas sur la même requête du formulaire (statut
  `pharmacien`, deux salaires moyens, naissance le 10 du mois, entré à l'âge dit), le
  portage servi et le moteur Python refait au bit près (`servi_et_refait`,
  `tests/outils_pont.py`).

## Les calculs

Chaque valeur du modèle est celle des deux moteurs (essai du jour) ; chaque valeur du
texte, posée à la main.

- **Ce qui s'accorde.** Né en 1960, à 62 ans : 12 trimestres jusqu'à 65 ans à 1,25 % = 15 %,
  8 de 65 à 67 ans à 0,5 % = 4 %, 0,81, comme le modèle. Né en 1950, à 62 ans en 2012 :
  12 × 1,25 % = 15 %, la ligne « 62 ― 15,00 % », 0,85. Né en 1955, à 62 ans : 12 × 1,25 % +
  4 × 0,5 % = 17 %, « 62 ― 17,00 % », 0,83. Né en 1954, à 68 ans : 8 trimestres au-delà
  de 66 ans × 0,5 % = 4 %, « 68 4,00 % », 1,04 ; à 64 ans, 4 × 1,25 % + 4 × 0,5 % = 7 %,
  0,93. Né en août 1951, à 66 ans : 4 × 0,5 % = 2 %, « 66 2,00 % », 1,02. Né en 1950, à
  67 ans : « Pas de majoration de pension pour un départ après 65 ans », 1. Né en 1960, à
  70 ans : 12 × 0,5 % = 6 %, 1,06. Né le 10 mars 1964, entré à 17 ans, en carrière longue
  à 60 ans le 1er avril 2024 : 20 × 1,25 % = 25 %, 0,75, dans le modèle comme au texte.
- **La carrière longue depuis le 10 janvier 2024.** Né le 10 mars 1965, entré à 19 ans,
  parti à 62 ans le 1er avril 2027 : le modèle sert 0,81, 11 035,07 € par an ; le texte, 12
  × 1,25 % = 15 %, 0,85 : 11 035,07 / 0,81 × 0,85 = 11 580,01 €, **544,94 € par an de
  moins**. Né le 10 mars 1966, entré à 20 ans, à 63 ans le 1er avril 2029 : 8 × 1,25 % =
  10 %, 0,90 au lieu de 0,86 : 12 175,81 / 0,86 × 0,90 = 12 742,13 €, **566,32 € de
  moins**. Né le 10 mars 1966, entré à 15 ans, à 58 ans le 1er avril 2024 : 28 × 1,25 % =
  35 %, 0,65 au lieu de 0,75 : 10 580,06 / 0,75 × 0,65 = 9 169,39 €, **1 410,68 € par an
  de trop**.
- **La date d'effet.** Né le 10 mai 1960, entré à 21 ans, il demande sa pension à 67 ans,
  en mai 2027. Le modèle la sert le 1er juin 2027, 14 548,91 € par an ; le règlement
  (article 14), au premier jour du trimestre civil qui suit la demande, le 1er juillet
  2027. **Un mois servi trop tôt, 14 548,91 / 12 = 1 212,41 €** ; au 1er juillet, un mois
  et 21 jours au-delà de 67 ans, aucun trimestre entier de majoration.
- **La valeur de service, deux lectures.** Première (la valeur du modèle est celle des
  nés depuis 1956) : né le 10 mars 1950, à 65 ans le 1er avril 2015, 12 040,82 € servis ;
  statuts de 2011, 12 040,82 / 1,04 = 11 577,71 €, 463,11 € par an de trop ; règlement de
  2026, × 0,96 = 11 559,19 €, 481,63 €. Né le 10 mars 1954, à 66 ans le 1er avril 2020,
  12 890,56 € ; × 1,02 / 1,04 = 12 642,67 €, 247,90 € ; × 0,96 / 0,98 = 12 627,49 €,
  263,07 €. Seconde (c'est la retraite entière de l'article 11) : né le 10 mars 1956, à
  67 ans le 1er avril 2023, 14 772,97 € servis ; × 1,04 = 15 363,89 €, 590,92 € par an de
  moins.
- **Avant 2009, non mesuré.** Né le 10 mars 1940, à 64 ans le 1er avril 2004 : le modèle
  sert 1 avec la durée (entré à 21 ans, 10 160,24 €), 0,95 sans (entré à 30 ans,
  7 677,91 €) ; ce que les statuts d'alors disaient n'est pas lu.

## Ce que l'étape laisse

- **Les erreurs du modèle, déclarées dans la fiche, non corrigées, pour le propriétaire** :
  1. **la carrière longue depuis le 10 janvier 2024** reçoit les deux pentes, la seconde
     de trop, dans une limite de vingt trimestres que le texte n'a plus depuis 2011 : de
     544,94 € par an de moins à 62 ans à 1 410,68 € de trop à 58 ans dans les cas posés. La
     lecture contraire — la dérogation ne compterait la première pente que depuis l'âge du
     départ, la seconde restant due — n'est pas tenable : la dérogation fixe le
     coefficient « égal à » 1,25 % par trimestre « jusqu'à l'âge de 65 ans » ;
  2. **la date d'effet** au premier du mois qui suit l'âge, non au premier jour du
     trimestre civil qui suit la demande, de 2009 à 2026 : un mois de pension, 1 212,41 €,
     dans le cas posé. La même classe que les erreurs (3) de la CAVOM et de la CARPIMKO
     (`date_effet_mois_suivant`).
- **Ce que le texte ne tranche pas** : la génération dont le modèle sert la valeur de
  service (463,11 € par an de trop ou 590,92 € de moins dans les cas posés), et le rapport
  lui-même, 1/1,04 en 2011, 0,96 en 2026 ; le trimestre entamé, au plus 1,25 point ; un
  trimestre entamé au-delà de l'âge du taux plein.
- **Renvoyés, non doublés** : l'inapte (question 11) ; la carrière longue servie avant
  2024 (`liquidation_regime_par_regime`) ; les statuts d'avant 2009 parmi ceux du seul
  Bulletin officiel (question 22).
- **Non modélisé** : la cessation d'activité de 2009 à 2024 ; les rachats ; la
  capitalisation.
- **Les statuts qui manquent** : ceux de 1950 et leurs modifications, dont celles de 1976,
  1979 et 1981 qui touchent les articles 10 et 11, et celle de 1990 au Bulletin officiel
  (no 90-40). À demander à la CAVP, ou à lire en bibliothèque, avec un exemple de la
  caisse pour la valeur de service et la carrière longue.
- **L'entrée en vigueur** des arrêtés sans date (2009, 2011, 2023, 2026) est prise au
  lendemain de leur publication, comme dans les fiches de la CAVOM et de la CARPIMKO ; du
  1er au 17 juillet 2026, entre le décret n° 2026-418 et le règlement, les statuts.

## Le bloc « Reprise » récrit

Daté du 5 novembre 2026 : la CAVP lue au droit, 79 fiches et 457 manques ; ses deux erreurs
du modèle et ses deux non-tranchés au propriétaire ; la suite, la caisse suivante de la
carte.

Renvoi du 5 novembre 2026 : la relecture R-E5 (`2026-11-05-relecture-r-e5.md`) trouve ce relevé conforme et ajoute un non-tranché, la majoration des nés jusqu'au 30 juin 1951 de 2011 à 2026, et deux arrêtés à nommer ; ils sont repris dans `2026-11-05-e4-bis-corrections-de-r-e5.md`.
