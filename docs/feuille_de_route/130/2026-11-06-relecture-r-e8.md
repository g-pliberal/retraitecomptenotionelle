# Relecture de E7 (la Cipav lue au droit) et des chiffres neufs de E6-bis (la CARMF)

File R-E8, le 6 novembre 2026 : relecture indépendante, contre les sources, du commit
d5497c9 de la session E7 (`cipav_seconde_tranche` ; note
`2026-11-06-carte-des-fiches-cipav-lue-au-droit.md`) et du commit 8c955fe de la session
E6-bis (`carmf_asv_minoration_enfants`, `asv_medecins_ajustement` ; note
`2026-11-06-e6-bis-corrections-de-r-e7.md`). Ni règle, ni donnée, ni test n'est modifié.

**Méthode.** Les index de la DILA récupérés puis mis à jour (`dila_index.py --recuperer`,
`--mettre-a-jour`) : JORF au 6 novembre 2026 (incrément 20261106-002608), LEGI au 5
novembre. Chaque citation des trois fiches, découpée à ses « [...] », guillemets ôtés,
entités HTML décodées et espaces ramenées, cherchée par un script écrit pour cette relecture
dans le texte de l'index qu'elle nomme ; trois altérations faites exprès (« 23 % » pour
« 22 % », « trois fois et quart » pour « trois fois et demi », « 45,30 » pour « 47,40 »)
y échouent. Les citations des deux notes, de même. Les textes de 2025 et 2026, relevés par
requêtes directes sur la base de l'index, sans borne ni limite. Chaque montant refait en
décimal exact. Les tests de la zone joués sous les deux jeux de présomptions.

## Le verdict

**E7 conforme pour l'essentiel ; E6-bis conforme.** Toutes les citations des trois fiches et
des deux notes sont exactes mot pour mot ; les dates de publication et d'effet, justes ; les
taux, coûts du point et plafonds, ceux des textes ; les cinq cotisations de 2023 à 2025,
l'approximation du rendement (28,57 €), l'arrondi (0,14 €), l'ajustement de l'ASV (0,2504
point, 2,96 €) et l'ASV d'avant 2017 (776,66 €) tombent juste au centime ; aucun texte de
2025 ou de 2026 ne fixe les taux ni le coût du point de la Cipav pour 2026 ; la date d'effet
de l'article 5-3 est au texte, et le modèle la rend ; la carte compte bien 75 fiches et 432
manques, et le cliquet 9 312 rédactions sans statut. Aucun écart fort ni moyen. Cinq écarts
**faibles** : trois chez E7 (points 4, 5 et 9), deux chez E6-bis (points 20 et 23).

## E7, point par point

1. **L'article 2 du décret n° 79-262, ses rédactions.** LEGI porte six rédactions de
   l'article 2, et elles seules : 1979 (LEGIARTI000006767473), 1985 (006767474), 30
   décembre 2012 (026885130), 1er janvier 2013 (026892951), 1er janvier 2023
   (046875038, jusqu'au 1er juillet 2026), 1er juillet 2026 (054168526). Les citations
   de la fiche (huit classes de 2013 ; les deux tranches, « une et trois fois », « trois
   fois et demi », « quatre fois [...] à compter de l'exercice 2025 » ; « fixé chaque
   année par décret » ; les deux phrases ajoutées en 2026) se trouvent toutes dans le
   texte. Le décret n° 2026-418 change aussi « demi » en « demie » et « adhérents » en
   « affiliés » : sans effet sur les tranches. **Conforme.**
2. **Le décret n° 2022-1746** (JORFARTI000046847145, publié le 31 décembre 2022) : le 2° de
   l'article 1er remplace l'article 2, mot pour mot ce que la fiche cite ; son article 3 ne
   charge que de l'exécution, et la notice dit « le décret entre en vigueur le 1er janvier
   2023 », la date même de la rédaction consolidée. Aucun texte ne le modifie ni ne le
   rectifie (recherche du numéro au titre et au corps, depuis décembre 2022). **Conforme.**
3. **Les taux et le coût du point de 2023 à 2025.** Décret n° 2023-1351, article 6, 8°
   (« Pour l'année 2023 », publié le 30 décembre 2023) : 9 %, 22 %, 45,30 € ; décret n°
   2024-1214, article 6, 8° (publié le 29 décembre 2024) : 9 %, 22 %, 47,40 € ; décret n°
   2025-1076, article 12, 8° (publié le 13 novembre 2025) : 11 %, 21 %, 47,40 €, appliqué
   aux périodes « à compter du 1 er janvier 2025 » (article 15, I). L'article 4 du décret
   n° 2023-1351 (19 % du plafond) est cité exactement. Aucun de ces décrets n'a de texte
   modificatif ni de rectificatif. **Conforme.**
4. **La version d'avant 2023 (faible).** Bornée de l'origine au 1er janvier 2023 et dite
   « lue », elle ne cite que la rédaction de 2013 (« huit classes »). De 1979 au 31
   décembre 2012, l'article 2 portait « six classes de cotisation : Classe 1 portant
   attribution de quatre points de retraite ; [...] » (LEGIARTI000006767473, 006767474,
   026885130). Sans effet sur un montant : la version renvoie tout son contenu à
   `cotisation_par_classes_liberales`. À citer avec les trois rédactions d'avant 2013.
5. **Le décret n° 2026-239 du 1er avril 2026 (faible).** Les statuts-types des sections
   (JORFARTI000053748628) nomment la Cipav (notes 51 et 52, « La caisse (hors CIPAV)
   choisit [...] ») et ne sont pas dans les textes que E7 relève. Lus : la gouvernance, le
   recouvrement, les majorations de retard ; ni taux, ni coût du point, ni date d'effet.
   Sans effet ; à nommer parmi les textes sans effet.
6. **Les plafonds.** Arrêtés du 9 décembre 2022 (JORFARTI000046745086), du 19 décembre 2023
   (048708695), du 19 décembre 2024 (050854396) et du 22 décembre 2025 (053143455) : 3 666,
   3 864, 3 925 et 4 005 € par mois ; 43 992, 46 368, 47 100 et 48 060 € par an. Aucun
   arrêté ne les modifie. **Conforme.**
7. **Les cinq cotisations**, refaites : 0,09 × 43 992 + 0,22 × 56 008 = 3 959,28 +
   12 321,76 = 16 281,04 € ; 3 959,28 + 0,22 × 87 984 = 23 315,76 € ; 0,09 × 46 368 +
   0,22 × 115 920 = 4 173,12 + 25 502,40 = 29 675,52 € ; 0,11 × 47 100 + 0,21 × 102 900 =
   5 181,00 + 21 609,00 = 26 790,00 € ; 5 181,00 + 0,21 × 141 300 = 34 854,00 €. Les deux
   moteurs les rendent, présomptions décalées ou non (point 15). **Conforme.**
8. **Aucun texte ne fixe 2026.** Recherche sans borne dans les 32 308 documents de l'index
   JORF publiés depuis le 1er janvier 2025 : au titre, « vieillesse complémentaire », les
   professions libérales ou les professionnels libéraux avec la retraite, la vieillesse, la
   cotisation ou les paramètres, la Cipav, la « Caisse interprofessionnelle de
   prévoyance », le décret n° 79-262 ; au corps, le décret n° 79-262, le « 11° de l'article
   R. 641-1 », la « valeur d'achat du point » et le « coût d'acquisition du point », la
   « deuxième tranche » avec la « cotisation proportionnelle », la Cipav ; puis « Pour
   l'année 2026 », « pour l'exercice 2026 », « au titre de l'exercice 2026 », « à compter
   de l'exercice 2026 » avec une section professionnelle ou les libéraux. La première
   recherche rend vingt-sept textes (les arrêtés de statuts et règlements des sections, les
   décrets n° 2025-943, 2025-1076, 2025-1351, 2025-1352, 2026-239 et 2026-418) ; la seconde,
   hors l'article 14 du décret n° 2025-1076, des délibérations de l'énergie, des avis et des
   nominations ; aucun ne fixe ni les taux ni le coût du point de la Cipav pour 2026. Le
   décret n° 2025-1076 s'intitule « fixant pour 2025 et 2026 les paramètres des régimes
   d'assurance vieillesse complémentaire des professionnels libéraux », mais son article
   14, « Pour l'année 2026 », s'arrête au 3° : médecins (11,8 %), chirurgiens-dentistes et
   sages-femmes (11,35 %), auxiliaires médicaux (8,7 %). Le décret n° 2026-418 (articles
   20, 21, 29 et 30) ne fixe ni taux ni coût : l'article 20 récrit l'article 2 sans taux,
   le 21 l'invalidité-décès, le 29 exclut la Cipav des critères de soutenabilité. Le
   décret n° 2025-943 (taux globaux du micro-entrepreneur) relève de
   `micro_social_abattement`. **Conforme** : la reconduction est bien une supposition,
   déclarée.
9. **L'enjeu des taux de 2026 (faible).** Les montants sont justes, aux arrondis près :
   16,88 × 2,8914 = 48,81 €, non 48,80 € (48,80 € est 800 × 0,061, les points non
   arrondis ; arrondis à la décimale comme le veut le texte, 92,8 − 75,9 = 16,9 points,
   48,86 €) ; 1,23 × 2,8914 = 3,56 €, non 3,55 € (3,55 € est 58,20 × 0,061). Surtout,
   « au plus 48,80 € » ne vaut que pour les deux cas posés : sous la même hypothèse (9 %
   et 22 %), l'écart est le plus grand à un revenu égal au plafond, 0,02 × 48 060 =
   961,20 € de cotisation, 20,28 points, 961,20 × 0,061 = **58,63 € de pension par an**
   que le modèle servirait de trop ; il s'annule à trois plafonds (144 180 €) et s'inverse
   au-delà, jusqu'à −480,60 € de cotisation et −29,32 € par an dès quatre plafonds. La
   fiche (« au plus 48,80 € [...] dans les cas posés ») est exacte dans sa restriction,
   mais l'ordre de grandeur à dire au propriétaire est de −29,32 € à +58,63 € par an et
   par exercice 2026, sous cette hypothèse ; aucune autre ne s'appuie sur un texte.
10. **L'approximation du rendement.** 26 790,00 / 47,40 = 565,19 points, 565,2 arrondis ;
    le modèle, 26 790,00 × 1,0175 × 0,061 = 1 662,79 € ; le texte, à la valeur de service
    que le rendement suppose (0,061 × 47,40 = 2,8914 €), 565,2 × 2,8914 = 1 634,22 € ;
    écart 28,57 €, 1,75 %. Le coefficient de prix du modèle de 2025 à 2026 est bien 1,0175
    (`coefficient_prix`, essai du jour) et le rendement 0,0610 depuis 2023
    (`rendements_points.csv`, ligne 233). L'arrondi : 0,05 × 2,8914 = 0,14 €. La valeur
    de service est fixée « annuellement par le conseil d'administration » (article 5-2, I,
    cité exactement). **Conforme**, l'approximation et ses hypothèses déclarées.
11. **La date d'effet depuis le 1er juillet 2026.** Article 5-3 (LEGIARTI000054168512, en
    vigueur le 1er juillet 2026, article 30 du décret n° 2026-418) : « La date d'effet de la
    pension de retraite complémentaire est fixée au premier jour du mois qui suit la demande
    prévue à l'article 5-1 », et l'article 5-1 ne liquide qu'« A partir de l'âge légal » ou
    de l'âge du taux plein (hors les départs anticipés de L. 643-3). Né le 10 mai 1964,
    parti à 64 ans : le modèle date la pension de juin 2028 (`Carriere.date_liquidation`,
    essai du jour), le premier mois qui suit une demande faite en mai 2028 et le premier
    où l'âge est atteint. **Conforme** : la Cipav est hors du défaut du trimestre civil
    (candidat 23). Avant le 1er juillet 2026, l'article 5 du décret renvoyait aux statuts
    (LEGIARTI000006767480 : « établi par les statuts de la section professionnelle ») ; les
    arrêtés du 22 juin 2020, des 16 mars et 16 décembre 2021, du 20 mars et du 27 décembre
    2023, des 4 et 17 septembre 2025 ne datent que la réversion, la rente de survie, la rente
    aux orphelins, l'invalidité et l'affiliation : la question des statuts d'avant juillet
    2026 au Bulletin officiel est fondée.
12. **Les articles 5-1 et 5-2.** « un taux de minoration de 5 % par année séparant l'âge de
    l'assuré [...] à taux plein » (5-1, 2°, b), « majoré de 5% par année entière de
    prorogation », « uniquement aux points acquis au titre des trente premières années de
    cotisation à la CIPAV », « un minimum de trente années d'affiliation » (5-2, II) : mot
    pour mot. **Conforme.**
13. **Le candidat R. 643-6.** Décret n° 2023-148, article 1er, 5° (JORFARTI000047259558) :
    « Par dérogation, l'entrée en jouissance de la pension de retraite des travailleurs
    indépendants libéraux affiliés à la section professionnelle mentionnée au 11° de
    l'article R. 641-1 est fixée dans les conditions prévues au I de l'article R. 351-37 »
    (E7 cite sans « Par dérogation, » : exact). Le candidat est sérieux : R. 643-6 dit,
    depuis le 1er janvier 2004 (LEGIARTI000006751829, puis 047265890 depuis le 5 mars 2023),
    « L'entrée en jouissance de la pension de retraite est fixée au premier jour du
    trimestre civil qui suit la demande de l'intéressé » pour la base de toutes les autres
    sections, et pour la Cipav elle-même jusqu'au 4 mars 2023. À lire avec le candidat de
    R-E7 (l'article 7 des statuts de base de la CARMF).
14. **Le cliquet abaissé à 9 312** : justifié. `controler` (`noyau/textes.py`) refuse un
    cliquet supérieur au compte réel comme un compte supérieur au cliquet ; la rédaction
    que la fiche cite désormais a pris un statut, et `tests/test_textes.py` passe (point 15).
    **La carte** : `carte.manques()` rend 75 fiches et 432 manques, sans
    `cipav_seconde_tranche`. **Conforme.**
15. **Les tests.** Les deux tests neufs passent, les cinq cotisations au centime, la version
    de 2026 portée de 2026 à 2040 (`lues == 18` : les dix-huit années de 2023 à 2040).
    Le second test, vert d'emblée, tient ce que le modèle rendait déjà, ce que E7 dit. Voir
    « Les tests » ci-dessous.

## E6-bis, point par point

16. **L'article 12 ter des statuts de l'ASV.** Arrêté du 28 septembre 2011 (publié le 30
    septembre ; ses articles ne datent rien, l'annexe non plus : en vigueur le lendemain),
    arrêté du 1er décembre 2016 (publié le 6 décembre ; article 2 : « Le présent arrêté
    entre en vigueur au 1er janvier 2017 »), arrêté du 30 novembre 2016 (publié le 4
    décembre, même article 2) : les quatre citations de la note et les trois phrases du
    test, mot pour mot ; l'article 15 bis (« Le taux de réversion est identique à celui
    retenu à l'article 15 pour le conjoint survivant ») est bien dans l'annexe de 2016.
    « article 12 ter » n'apparaît, pour les médecins, que dans ces deux arrêtés. Le
    classement en non tranché est juste : le texte de l'article 12 ter n'est pas publié,
    « dès l'âge de 60 ans » dit un âge et non un coefficient, la lecture du modèle n'est
    pas intenable ; les deux lectures sont citées et chiffrées : 15 533,26 × 0,95 =
    14 756,60 €, 776,66 € par an. **Conforme.**
17. **Le rectificatif du 8 août 2026.** JORFARTI000054642802, cité mot pour mot ; il ne
    déplace que l'intitulé « Chapitre 2 ». Sans effet. **Conforme.**
18. **L'âge légal des nés en 1964.** L. 161-17-2 n'a, dans LEGI, aucune rédaction après
    celle de la loi n° 2025-1403 (LEGIARTI000053280889, en vigueur le 31 décembre 2025 ; le
    titre au JORF : « LOI n° 2025-1403 du 30 décembre 2025 de financement de la sécurité
    sociale pour 2026 ») ; son rectificatif du 23 mai 2026 (JORFARTI000054125098) ne touche
    que les articles 18 et 99. « 3° Soixante-deux ans et neuf mois, pour les assurés nés
    entre le 1 er janvier 1963 et le 31 mars 1965 », pour les pensions « à compter du 1 er
    septembre 2026 » : mot pour mot. D. 161-2-1-9 garde dans LEGI sa rédaction du 1er
    septembre 2023 (« Soixante-trois ans pour les assurés nés en 1964 »), que la loi
    écarte. Les dates refaites : né le 10 mai 1964, 62 ans et 9 mois le 10 février 2027,
    pension au 1er juillet 2027, 4 trimestres, 1,05 ; né le 10 mars 1964, 10 décembre 2026,
    pension au 1er juillet 2027, 5 trimestres, 1,0625 : l'âge légal est passé avant la
    cessation dans les deux lectures, sans effet. Le modèle ouvre à 62,75 ans et non à
    62,5, dans les deux moteurs (le test passe). **Conforme.**
19. **L'ajustement de l'ASV.** Décret n° 2011-1644, article 3 (LEGIARTI000024853554) : le
    rapport, « arrondi au centième le plus proche », entre la cotisation d'ajustement
    multipliée par « des deux tiers du nombre de points acquis au titre de la cotisation
    forfaitaire » et la cotisation forfaitaire, « dans la limite de neuf points par an » ;
    deux tiers de 27, 18 ; « 4 % à compter de l'exercice 2026 » (article 2,
    LEGIARTI000052567960) ; « 11,82 euros à compter de l'exercice 2025 » (article 4, II, 3°,
    LEGIARTI000052567955). 28 800 / 5 751 = 5,0078 ; 30 240 / 5 751 = 5,2582 ; 1 440 /
    5 751 = 0,2504 point ; × 11,82 = 2,96 € ; l'arrondi, 5,01 − 5,0078 = 0,0022 point,
    0,03 €. Le forfait de 5 751 € vient du registre de la caisse (l'article 1er le fait
    revaloriser chaque année depuis 2017, sans montant publié) ; il pèse sur les deux
    membres et n'est pas l'objet de la correction. **Conforme.**
20. **L'arrêté du 7 janvier 2025** (JORFARTI000050962838, publié le 10 janvier) : « 3° Au
    premier alinéa de l'article 8, les mots : « l'année » sont remplacés par les mots :
    « l'avant dernière année » ; 4° [...] « soixante-deux » » : mot pour mot. **Conforme**,
    à un mot près (**faible**) : la note le dit en vigueur le 11 janvier parce que
    « l'article 2 charge de l'exécution et de la publication » ; son article 2
    (JORFARTI000050962836) dit seulement « Le présent arrêté sera publié au Journal officiel
    de la République française. » La conclusion tient : sans date, le lendemain de la
    publication.
21. **L'arrêté du 22 mars 2017** (point 4 de E6-bis) : publié le 29 mars ; ses deux articles
    et son annexe ne disent aucune date. Le non-tranché demeure. **Conforme.**
22. **Le candidat des articles 27 et 31** de la complémentaire de la CARMF : les deux
    phrases sont dans l'annexe de l'arrêté du 30 novembre 2016 (JORFARTI000033521562), mot
    pour mot, et ni `data`, ni `docs` hors la note de E6-bis, ni `src`, ni `tests` ne les
    portent. Candidat fondé.
23. **Le modèle de E6-bis (faible, de méthode).** Le commit 8c955fe porte « Co-Authored-By:
    Claude Sonnet 5.5 » : l'étape récrit deux fiches du scénario 1, que les consignes
    (« Une étape qui écrit ou change une règle du scénario 1 se mène sur Opus ») font
    mener sur Opus. Aucune règle du modèle n'y change, et la présente relecture, sur Opus,
    n'y trouve aucune erreur : sans conséquence sur le fond.

## Les tests

`python -m pytest -m rapide` : 11 rouges, tous `test_pages_en_dossier` (que GitHub refait),
4 552 verts ; sous `PRESOMPTIONS_DECALEES=1`, les mêmes 11 rouges, 4 347 verts.
Les fichiers de la zone (`test_sections_liberales.py`, `test_sections_sante.py`,
`test_carte.py`, `test_textes.py` et les quatorze autres qui nomment la Cipav ou la CARMF,
hors `test_cout.py`, laissé à GitHub) : 1 772 verts et un rouge,
`test_les_temoins_du_portage_sont_a_jour`, que GitHub refait. Sous
`PRESOMPTIONS_DECALEES=1`, 1 717 verts ; aux deux rouges attendus
(`test_les_temoins_du_portage_sont_a_jour`, `test_le_paquet_est_a_jour`) s'ajoutent dix-sept
rouges de `test_web.py` et `test_web_saisie.py`, qui confrontent le portage au moteur Python :
la garde ne décale pas le portage (« ses confrontations au Python échouent sans rien dire des
tests », `tests/conftest.py`), et GitHub ne la joue que sur `-m rapide`. Aucun ne touche les
fichiers de la Cipav ni de la CARMF : `test_sections_liberales.py`, `test_sections_sante.py`,
`test_carte.py` et `test_textes.py` sont verts sous les deux jeux.

## Ce que la relecture laisse

- **À la file E**, dans `cipav_seconde_tranche` : citer les rédactions de l'article 2
  d'avant 2013 (six classes) dans la version d'avant 2023 ; nommer le décret n° 2026-239
  parmi les textes sans effet ; dire l'enjeu des taux de 2026 de −29,32 € à +58,63 € par
  an et par exercice (sous l'hypothèse de 9 % et 22 %), et corriger 48,80 € en 48,81 €
  (ou 48,86 €, les points arrondis) et 3,55 € en 3,56 €.
- **Au propriétaire** : le décret des taux et du coût du point de la Cipav pour 2026, qu'aucun
  texte publié au 6 novembre 2026 ne donne ; les statuts de la Cipav d'avant juillet 2026,
  pour la date d'effet de la pension de droit direct.
- **Candidat, hors de la tâche** : R. 643-6, la base de toutes les sections autres que la
  Cipav au premier jour du trimestre civil qui suit la demande depuis 2004, et celle de la
  Cipav jusqu'au 4 mars 2023 ; à confronter à la date que le modèle donne à la base de la
  CNAVPL.
