# La carte des fiches : la Cipav lue au droit, dix-huitième lot

**La demande.** Le 6 novembre 2026, la session d'orchestration confie à la file E
(tâche E7) la caisse suivante de la carte, après la CARMF : la Cipav, dernière section
de la CNAVPL, lue au droit selon la méthode de E6
(`130/2026-11-06-carte-des-fiches-carmf-lue-au-droit.md`) et les leçons de R-E7 : citer
tous les textes modificatifs, refaire les arrondis à la main. Une seule fiche de la
carte ne porte que la Cipav : `cipav_seconde_tranche` (six manques). Ses âges et sa
minoration passent par des fiches communes à plusieurs caisses (`surcote_par_age_seul`,
`age_annulation_decote`), hors de cette tâche ; la date d'effet, que le candidat 23
pose pour quatre caisses, est lue ici. Aucune règle du modèle ne change.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` (rien de neuf à la base de la Cnav),
  `docs/veille_droit.md` ; les index JORF (au 6 novembre) et LEGI (au 5 novembre)
  récupérés et mis à jour.
- **Tous les textes du régime, relevés sans borne.** Dans LEGI, les 39 documents du
  décret n° 79-262 : chaque rédaction de chaque article. Dans le JORF, par titre (le
  décret n° 79-262, « CIPAV », la « Caisse interprofessionnelle de prévoyance », la
  section des architectes) : 43 textes, de 1979 à 2025 ; par titre encore, de juin 2021
  à 2026, les paramètres de vieillesse, la vieillesse complémentaire, les professions
  libérales et les sections ; par le corps des articles, de 2022 à 2026, le décret n°
  79-262, la « cotisation proportionnelle de première tranche » ou « de la deuxième
  tranche », et, depuis le 14 novembre 2025, « 47,40 », la valeur d'achat ou le coût
  d'acquisition du point, le 11° de R. 641-1. Lus, article par article : le décret n°
  2022-1746 ; les décrets n° 2023-1351, 2024-1214, 2025-1076, 2023-148 et 2026-418 ;
  les arrêtés de statuts des 22 juin 2020, 16 mars 2021, 16 décembre 2021, 20 mars
  2023, 27 décembre 2023, 4 et 17 septembre 2025 ; les arrêtés du plafond pour 2023 à
  2026. Aucun règlement de la Cipav n'est approuvé le 10 juillet 2026, comme ceux des
  autres sections : ses règles de liquidation entrent au décret n° 79-262 lui-même
  (articles 5-1 à 5-6, décret n° 2026-418, article 20, en vigueur le 1er juillet 2026).
- **Le test d'abord.** La fiche entre dans `LUES_AU_DROIT` (`tests/test_carte.py`),
  vue rouge de ses six manques ; un test neuf,
  `test_chaque_version_de_la_seconde_tranche_de_la_cipav_est_portee_par_le_modele`
  (`tests/test_sections_liberales.py`), vu rouge faute de versions, lit chaque année de
  2023 à 2040 les deux tranches de chaque version (assiette et taux) et les confronte
  aux périodes du régime, ni plus ni moins ; un second,
  `test_la_cipav_cotise_aux_deux_tranches_du_decret_dans_les_deux_moteurs`, joue cinq
  cas posés à la main sur la fiche de paie, servie par le portage et refaite par le
  moteur Python (`droit_et_refait`), et sur ce que le scénario 1 inscrit (`acquerir`),
  verts d'emblée : ils tiennent ce que le modèle rend déjà.
- **`cipav_seconde_tranche`**, approchée : cinq versions sur l'année du revenu.
  - **Avant 2023, lue** : l'article 2 dans sa rédaction de 2013, huit classes ; la
    fiche les laisse à `cotisation_par_classes_liberales`.
  - **L'exercice 2023** (décret n° 2022-1746, article 1er, 2°, publié le 31 décembre
    2022, « le décret entre en vigueur le 1er janvier 2023 ») : deux tranches du revenu
    de L. 131-6, la première sur « la part des revenus n'excédant pas le plafond », la
    seconde « entre : -une et trois fois le plafond précité pour l'exercice 2023 ; -une
    et trois fois et demi le même plafond pour l'exercice 2024 ; -une et quatre fois le
    même plafond à compter de l'exercice 2025 » ; 9 % et 22 %, 45,30 € le point
    (décret n° 2023-1351, article 6, 8°) ; les points « arrondi[s] à la décimale la plus
    proche » (statuts, article 3.3, arrêté du 20 mars 2023, applicable aux périodes «
    à compter du 1er janvier 2023 »).
  - **L'exercice 2024** : trois plafonds et demi ; 9 % et 22 %, 47,40 € (décret n°
    2024-1214, article 6, 8°).
  - **L'exercice 2025** : quatre plafonds ; 11 % et 21 %, 47,40 € (décret n° 2025-1076,
    article 12, 8°, appliqué aux périodes « à compter du 1 er janvier 2025 », article
    15, I).
  - **Depuis 2026, supposée** : la borne de quatre plafonds est lue ; les taux, que
    l'article 2 fait fixer « chaque année par décret », ne le sont par aucun texte de
    l'index : l'article 14 du décret n° 2025-1076, « Pour l'année 2026 », s'arrête au
    3°, les auxiliaires médicaux. Le modèle reconduit 11 % et 21 %. La rédaction du 1er
    juillet 2026 ajoute deux phrases, sans toucher aux tranches : « Le calcul des
    cotisations prévu au présent I s'applique aux deux premières années d'activité »,
    « Le nombre de points obtenus est arrondi à la décimale la plus proche ».
- **Les citations** ont été vérifiées par un script : les dix-huit, chacune découpée à
  ses « [...] », guillemets ôtés et espaces ramenées, se trouvent dans le texte de
  l'index qu'elles nomment ; altérées exprès (« 23 % » pour « 22 % », « trois fois et
  quart » pour « trois fois et demi »), cinq de leurs morceaux y échouent. Le paquet, refait, ne change pas. **La carte** passe de
  76 fiches à lire au droit à 75, de 438 manques à 432.

## Les calculs

Le plafond de chaque année est douze fois sa valeur mensuelle, lue aux arrêtés : 3 666 €
pour 2023 (arrêté du 9 décembre 2022), 3 864 € pour 2024 (19 décembre 2023), 3 925 €
pour 2025 (19 décembre 2024), 4 005 € pour 2026 (22 décembre 2025) : 43 992, 46 368,
47 100 et 48 060 €.

- **Ce qui s'accorde** (le libéral de la Cipav, `profession_liberale`, fiche de paie
  dans les deux moteurs et scénario 1, au centime) :
  - 2023, 100 000 € : 0,09 × 43 992 = 3 959,28 ; 0,22 × (100 000 − 43 992) = 0,22 ×
    56 008 = 12 321,76 ; ensemble 16 281,04 €.
  - 2023, 200 000 € : 3 959,28 + 0,22 × 2 × 43 992 = 3 959,28 + 19 356,48 = 23 315,76 €.
  - 2024, 200 000 € : 0,09 × 46 368 = 4 173,12 ; 0,22 × 2,5 × 46 368 = 0,22 × 115 920 =
    25 502,40 ; ensemble 29 675,52 €.
  - 2025, 150 000 € : 0,11 × 47 100 = 5 181,00 ; 0,21 × (150 000 − 47 100) = 0,21 ×
    102 900 = 21 609,00 ; ensemble 26 790,00 €.
  - 2025, 200 000 € : 5 181,00 + 0,21 × 3 × 47 100 = 5 181,00 + 29 673,00 = 34 854,00 €.
- **Le rendement au lieu du coût du point** (approximation). Le texte : 26 790,00 /
  47,40 = 565,19 points, arrondis à 565,2, servis à la valeur de service de la
  liquidation, que le conseil d'administration fixe (article 5-2) et que le Journal
  officiel ne publie pas. Le modèle : la cotisation revalorisée par ses prix (1,0175 de
  2025 à 2026, `coefficient_prix`) au rendement de 6,10 % : 26 790,00 × 1,0175 × 0,061
  = 1 662,79 € par an. À la valeur de service que ce rendement suppose, 0,061 × 47,40 =
  2,8914 € : 565,2 × 2,8914 = 1 634,22 €. Le modèle sert 28,57 € par an de trop pour
  cet exercice, 1,75 % : l'écart naît de ce que le coût du point ne suit pas les prix.
- **Les taux de 2026** (manque, au propriétaire). Ce que la reconduction engage, si 2026
  reprenait 9 % et 22 % : à 40 000 €, 4 400,00 − 3 600,00 = 800,00 € de cotisation,
  800,00 / 47,40 = 16,88 points, 16,88 × 2,8914 = 48,80 € de pension par an ; à
  150 000 €, 0,11 × 48 060 + 0,21 × 101 940 = 5 286,60 + 21 407,40 = 26 694,00 €,
  contre 0,09 × 48 060 + 0,22 × 101 940 = 4 325,40 + 22 426,80 = 26 752,20 €, 58,20 €
  de moins, 1,23 point, 3,55 € par an. Ce n'est pas une erreur : aucun texte ne dit
  d'autres taux.
- **L'arrondi des points** : au plus 0,05 point, 0,05 × 2,8914 = 0,14 € par an et par
  exercice.
- **La date d'effet** (candidat 23). Depuis le 1er juillet 2026 : « La date d'effet de
  la pension de retraite complémentaire est fixée au premier jour du mois qui suit la
  demande prévue à l'article 5-1 » (article 5-3, LEGIARTI000054168512). Né le 10 mai
  1964, parti à 64 ans : le modèle date la pension au 1er juin 2028
  (`Carriere.date_liquidation`, essai du jour) ; une demande faite en mai 2028 la date
  du même jour. Conforme : la Cipav n'a pas le défaut du trimestre civil de la CAVOM,
  de la CARPIMKO, de la CAVP et de la CARMF. Avant le 1er juillet 2026, la date d'effet
  de la pension de droit direct est aux statuts, dont aucun arrêté lu (16 décembre
  2021, 27 décembre 2023) ne montre l'article qui la fixe.

## Ce que l'étape laisse

- **Aucune erreur prouvée** dans la seconde tranche.
- **Au propriétaire** : le décret qui fixe pour 2026 les taux des deux tranches et le
  coût d'acquisition du point de la Cipav (le modèle reconduit 2025 ; au plus 48,80 €
  de pension par an et par exercice dans les cas posés) ; les statuts du régime
  complémentaire d'avant le 1er juillet 2026, au seul Bulletin officiel (question 22),
  pour la date d'effet de la pension de droit direct.
- **Approchés, chiffrés** : le rendement au lieu du coût du point (28,57 € par an dans le
  cas posé) et l'arrondi à la décimale (0,14 € au plus). **Sans effet** : la cotisation
  provisionnelle et le revenu forfaitaire de 19 % du plafond (décret n° 2023-1351,
  article 4), que la régularisation remplace.
- **Renvoyés, non doublés** : les classes d'avant 2023 (`cotisation_par_classes_liberales`)
  ; le micro-entrepreneur (article 2, II ; `micro_social_abattement`) ; le conjoint
  collaborateur (article 2-2).
- **Lus, à confronter dans les fiches communes** (`surcote_par_age_seul`,
  `age_annulation_decote`) : l'article 5-1, 2°, b (« un taux de minoration de 5 % par
  année séparant l'âge de l'assuré à la date de la liquidation de l'âge requis pour
  bénéficier de la pension de retraite complémentaire à taux plein ») ; l'article 5-2,
  II (« majoré de 5% par année entière de prorogation », « uniquement aux points acquis
  au titre des trente premières années de cotisation à la CIPAV », « un minimum de
  trente années d'affiliation »), que le fichier du régime approche déjà (tous les
  points majorés).
- **Candidat, hors de la tâche** : le décret n° 2023-148 (article 1er, 5°) complète R.
  643-6 : « l'entrée en jouissance de la pension de retraite des travailleurs
  indépendants libéraux affiliés à la section professionnelle mentionnée au 11° de
  l'article R. 641-1 est fixée dans les conditions prévues au I de l'article R.
  351-37 » ; à confronter à la date que le modèle donne à la base de la CNAVPL, avec le
  candidat de R-E7 (l'article 7 des statuts de base de la CARMF, au trimestre civil).

## Le bloc « Reprise » récrit

Daté du 6 novembre 2026 : la Cipav lue au droit, 75 fiches et 432 manques ; aucune
erreur, la date d'effet au mois depuis le 1er juillet 2026 ; au propriétaire, les taux
de 2026 ; les quatre fiches communes aux sections, la suite de la carte.
