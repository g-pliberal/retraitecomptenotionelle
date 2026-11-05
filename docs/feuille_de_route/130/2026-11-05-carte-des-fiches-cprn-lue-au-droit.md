# La carte des fiches : la CPRN lue au droit, seizième lot

**La demande.** Le 5 novembre 2026, vague 11, la session d'orchestration confie à la file
E (tâche E5) la dernière des quatre caisses que le bloc « Reprise » laissait, la CPRN, et
sa fiche, `cprn_ages_decote_enfants`, six manques, lue au droit selon la méthode de la CAVP
(`130/2026-11-05-carte-des-fiches-cavp-lue-au-droit.md`) et la leçon de R-E4 : chercher
tous les textes qui modifient les statuts, par numéro, date et titre. Ne pas refaire l'âge
de la complémentaire avant la base (N ddc92fc, R-N2 10eb393) ; déclarer ce qui dépend des
statuts d'avant 2014, au seul Bulletin officiel (question 22) ; dire si la CPRN partage la
date d'effet au trimestre civil de la CAVOM, de la CARPIMKO et de la CAVP ; prouver et
chiffrer le passage de 2024, sans le corriger. Aucune règle du modèle ne change.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` (rien de neuf à la base de la Cnav),
  `docs/veille_droit.md` ; les index JORF et LEGI récupérés, à jour du 5 novembre.
- **Tous les textes du régime, relevés sans borne.** Par « notaires » dans le titre avec «
  statuts », « vieillesse », « retraite » ou « complémentaire », et par « CPRN », «
  section professionnelle des notaires » et « retraite des notaires » dans le corps, de
  1937 à 2026, la caisse des clercs (CRPCEN) mise à part. Du règlement de 1962 et de ses
  modifications (1954, 1966, 1967, 1971, 1975, 1980, deux en 1983, 1985, 1987, 1990, 1996),
  l'index n'a que les titres ; trois sont au seul Bulletin officiel (1980, avril 1983,
  1990 no 90-42), et les statuts de 2005 aussi (no 2005/01). Depuis, chaque texte est
  ouvert : 2008 (l'article 20, les enfants), décembre 2013, 2017, 2023, 2026, les décrets
  n° 2004-1142, 2013-1157 et 2026-418. Aucun arrêté ne touche le règlement après le 10
  juillet 2026.
- **Le test d'abord.** La fiche entre dans `LUES_AU_DROIT` (`tests/test_carte.py`), vue
  rouge de ses six manques, et dans `NAISSANCES_AU_JOURNAL_OFFICIEL`
  (`tests/test_sections_liberales.py`), vue rouge faute de versions ; un test neuf,
  `test_chaque_version_de_la_cprn_est_portee_par_le_modele`
  (`tests/test_sections_juridiques.py`), vu rouge de même, lit chaque premier du mois de
  1949 à 2040 les paramètres de chaque version dans la période du modèle, par la
  fonction `_chaque_version_est_portee` de la CAVP et de la CARPIMKO ; aucun écart à
  déclarer, les périodes du modèle changeant le 1er janvier 2014 et le 1er janvier 2024
  comme les statuts. Un second test neuf,
  `test_la_cprn_sert_ses_ages_et_ses_coefficients_dans_les_deux_moteurs`, joue trois cas
  du texte sur la requête du formulaire, servis par le portage et refaits par le moteur
  Python (`servi_et_refait`), verts d'emblée : ils tiennent ce que le modèle rend déjà.
- **`cprn_ages_decote_enfants`**, approchée : six versions sur la date d'effet.
  - **Avant le 1er janvier 2005, supposée** : les statuts de 1948, le règlement de 1962
    et leurs modifications, aux seuls titres.
  - **Les statuts de 2005, supposée** (arrêté du 28 décembre 2004, « prend effet le 1er
    janvier 2005 ») : au Bulletin officiel. Trois phrases se lisent ailleurs : l'article
    20 récrit en 2008 (30 % des droits par enfant à charge), et l'article 14 et le premier
    alinéa de l'article 15 que l'arrêté de 2013 remplace.
  - **Les statuts de 2014** (arrêté du 16 décembre 2013, « prend effet au 1er janvier
    2014 »), articles 14, 15 et 16 : 60 et 65 ans pour les nés avant 1954, puis l'âge de
    L. 161-17-2 « différé de vingt-quatre mois » et « augmenté de cinq ans » ; 1,25 % par
    trimestre jusqu'au taux plein ; 0,5 % par trimestre au-delà, jusqu'à 70 ans.
  - **Les statuts de 2017** (arrêté du 31 mai 2017, publié le 21 juin, sans date : le
    22), articles 18, 19, 21 et 23 : la même règle, récrite ; la pension « au premier
    jour du mois civil qui suit la date de fin d'exercice ou la date souhaitée par
    l'affilié ».
  - **Les statuts de 2024** (arrêté du 29 novembre 2023, « le 1er janvier 2024 ») :
    l'âge de L. 161-17-2, le taux plein à celui du 1° de L. 351-8, 1 % par trimestre
    jusqu'à la fin d'activité, 10 % pour trois enfants.
  - **Le règlement de 2026** (arrêté du 10 juillet 2026, le 18 juillet), que l'article 4
    du décret n° 49-578 appelle depuis le 1er juillet (décret n° 2026-418, article 2,
    6°) : articles 4, 5, 7 et 9, la règle de 2024 ; les 30 % sur les seuls droits
    contributifs.
  - Trois textes lus sans effet : les décrets n° 2004-1142 (article 2) et 2013-1157
    (articles 1er et 2), les sections, les classes et la cotisation ; et la rédaction de
    D. 161-2-1-9 du 1er juillet 2011, remplacée avant 2014.
- **Les citations** ont été vérifiées par un script : chacune, ses morceaux séparés par
  « [...] », guillemets ôtés et espaces ramenées, se trouve dans le texte de l'index
  qu'elle nomme ; deux citations altérées exprès y échouent. Aucune rédaction non lue des
  articles cités (`textes.py --non-lues`) ; le paquet est à jour, le modèle n'a pas
  changé. **La carte** passe de 79 fiches à lire au droit à 78, de 457 manques à 451.

## Les calculs

Chaque valeur du modèle est celle des deux moteurs (essai du jour, statut `notaire`, deux
salaires moyens, naissance le 10 du mois, entré à 22 ans) ; chaque valeur du texte, posée
à la main.

- **Ce qui s'accorde.** Né le 10 mars 1954 : L. 161-17-2, 61 ans et 7 mois (D.
  161-2-1-9, 5°), plus vingt-quatre mois, 63 ans et 7 mois le 10 octobre 2017, la pension
  le 1er novembre 2017 ; le taux plein à 68 ans et 7 mois ; 4 ans, 11 mois et 9 jours,
  20 trimestres × 1,25 % = 25 %, 0,75, comme le modèle. Né le 10 mars 1950, parti à 67
  ans le 1er avril 2017 : 8 trimestres au-delà de 65 ans × 0,5 % = 4 %, 1,04. Né le 10
  mars 1957, parti à 68 ans le 1er avril 2025 : 4 trimestres au-delà de 67 ans × 1 % =
  4 %, 1,04. Né le 10 mars 1956, à 62 ans : la base le 1er avril 2018, la CPRN à 64 ans
  le 1er avril 2020, 20 trimestres jusqu'à 69 ans, 0,75. Les quatre cas de
  `test_la_decote_de_la_cprn_ne_connait_que_l_age` (0,85 ; 0,75 ; 0,95 ; 0,85) et la
  majoration de 10 % pour trois enfants depuis 2024 tiennent.
- **Le passage de 2024.** Né le 10 mars 1961, parti à 62 ans le 1er avril 2023 : le
  modèle sert la CPRN le 1er avril 2025, à 64 ans et 22 jours, 2 ans, 11 mois et 9 jours
  avant 67 ans, 12 trimestres, 0,85, 14 679,08 € par an de 2025. Les statuts de 2024 la
  lui ouvrent le 1er janvier 2024, à 62 ans, 9 mois et 22 jours, 4 ans, 2 mois et 9 jours
  avant 67 ans : 17 trimestres compté le trimestre entamé, 0,7875, soit 14 679,08 / 0,85
  × 0,7875 = 13 599,74 € par an aux valeurs de 2025, 13 599,74 × 15 / 12 = 16 999,67 €
  sur les quinze mois que le modèle ne sert pas ; puis 14 679,08 − 13 599,74 = 1 079,34 €
  par an de trop. Sans le trimestre entamé, 16 trimestres, 0,80 : 13 815,60 €, 17 269,51
  € et 863,48 €.
- **Le trimestre entamé.** Né le 10 septembre 1953, parti à 61 ans le 1er octobre 2014,
  à 61 ans et 21 jours : 3 ans, 11 mois et 9 jours avant 65 ans. Le modèle compte 16
  trimestres, 0,80, 8 395,62 € par an ; 15 trimestres entiers, 0,8125 : 8 395,62 / 0,80 ×
  0,8125 = 8 526,80 €, 131,18 € par an de plus.
- **Avant 2014, deux lectures.** Né le 10 mars 1948, parti à 60 ans le 1er avril 2008 : le
  modèle sert la CPRN dès ce jour, 6 979,83 € par an, 8 trimestres manquant à la durée
  qu'il requiert, 8 × 1,25 % = 10 %, 0,90. Si l'article 14 cité en 2013 valait en 2008, rien avant le 1er avril 2013,
  5 × 6 979,83 = 34 899,15 € servis avant ; puis, sans coefficient, 6 979,83 / 0,90 =
  7 755,37 € par an, 775,54 € de plus, aux valeurs de 2008.
- **Les 30 % par enfant à charge.** Né le 10 mars 1961, parti à 64 ans le 1er avril 2025 :
  15 449,40 € par an (0,85) ; un enfant de moins de vingt et un ans y ajoute 30 % de
  15 449,40 / 0,85 = 18 175,76 €, 5 452,73 € par an, ou 30 % de la pension, 4 634,82 €.
- **La date d'effet.** Depuis le 22 juin 2017, « au premier jour du mois civil qui suit la
  date de fin d'exercice ou la date souhaitée » ; le modèle, au premier du mois qui suit
  l'âge : aucun écart, 0 €. La CPRN ne partage pas l'erreur du trimestre civil. De 2014 à
  juin 2017, le début de la phrase, des statuts de 2005, n'est pas lu ; sa fin et le
  cinquième alinéa comptent au mois.

## Ce que l'étape laisse

- **L'erreur du modèle, déclarée dans la fiche, non corrigée, pour le propriétaire** : le
  passage de 2024, que `liquidation_regime_par_regime` déclarait déjà (N ddc92fc), ici
  prouvé et chiffré. Les statuts de 2024 entrent en vigueur le 1er janvier 2024 sans
  disposition transitoire, et ouvrent la pension à l'âge de L. 161-17-2 ; le notaire qui
  a cessé d'exercer en 2023 avant 64 ans peut la demander dès ce jour. Le modèle lit
  l'âge dans les règles du départ déclaré : quinze mois sans pension, 16 999,67 €, puis
  1 079,34 € par an de trop, dans le cas posé. La correction touche la façon dont
  `departs` date toute unité.
- **Ce que le texte ne tranche pas** : l'âge d'avant 2014 (34 899,15 € servis avant 65
  ans, puis 775,54 € par an de moins, si l'article 14 de 2013 valait en 2008) ; le
  trimestre entamé, au plus 1,25 point (131,18 € par an dans le cas posé) ; la base des
  30 % par enfant, avant ou après la décote.
- **Non modélisé** : les 30 % par enfant à charge, de 4 634,82 à 5 452,73 € par an et par
  enfant dans le cas posé ; le formulaire ne dit pas l'âge des enfants au départ.
- **Renvoyés, non doublés** : l'inapte (question 11), dix ans avant l'âge légal en 2014 ;
  la carrière longue, qu'aucun texte de la CPRN ne nomme (`liquidation_regime_par_regime`).
- **Les statuts qui manquent** : ceux de 2005 (Bulletin officiel no 2005/01), le règlement
  de 1962 et ses modifications, dont trois au Bulletin officiel (9 juin 1980, 19 avril
  1983, 12 septembre 1990, no 90-42). À demander à la CPRN, avec un exemple de pension
  liquidée en 2024 par un notaire parti en 2023.

## Le bloc « Reprise » récrit

Daté du 5 novembre 2026 : la CPRN lue au droit, 78 fiches et 451 manques ; son erreur du
modèle (le passage de 2024) et ses deux non-tranchés au propriétaire ; les quatre caisses
du bloc lues, la suite, la caisse suivante de la carte.

Renvoi du 5 novembre 2026 : la relecture R-E6 (`2026-11-05-relecture-r-e6.md`) trouve ce relevé conforme pour l'essentiel et relève trois écarts faibles : trois arrêtés à nommer (1963, 1964, 2001) et cinq textes au seul Bulletin officiel, deux phrases de l'âge d'avant 2014, deux égalités au centime (16 999,675 ; 17 269,50).
