# Correction de la ligne 28 de la file : la CAVAMAC sert son article 15 de septembre 2023 dès le 1er septembre

Vingt-huitième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu aux index JORF et LEGI** (à jour du 11 novembre 2026). Arrêté du 4 août
2023, publié le 18 : article 2 (JORFARTI000047977903), « 1° Les dispositions prévues aux
5°, 6°, b du 7° et 8° de l'annexe au présent arrêté entrent en vigueur le 1er septembre
2023 ; 2° Les dispositions prévues aux a, c et d du 7° de l'annexe au présent arrêté
entrent en vigueur le 1er janvier 2024. » ; annexe (JORFARTI000047977908), 6°, a, à
l'article 15, « les mots : « prévu à l'article L. 161-17-2 du code de la sécurité
sociale augmenté de cinq années » sont remplacés par les mots : « de 67 ans » » ; 6°, b,
« Sont liquidées à partir de l'âge prévu au IV de l'article L. 643-3 et sans application
d'un coefficient de minoration les pensions de retraite complémentaire des assurés
mentionnés aux 2° et 3° de l'article L. 643-4 ». L'article 16, jusqu'au 31 décembre,
garde « pour chaque année pleine différée au-delà de l'âge mentionné à l'article 15 ».
Aucune disposition transitoire. D. 351-2, rédaction du 1er septembre 2023
(LEGIARTI000047634554), relu pour l'ancien combattant. Le texte tranche ce que la ligne
dit.

**L'erreur.** La fiche du régime ne portait qu'une période de 2019 à 2023, aux règles de
2011 : du 1er septembre au 31 décembre 2023, le taux plein s'y lisait encore dans la
table par génération (de 65 ans et 4 mois à 66 ans et 7 mois pour les générations de
juillet 1951 à 1954), et la majoration par année pleine différée se comptait depuis cet
âge, trop bas. Les catégories servies sans minoration y restaient celles de 2011, ce que
la note de la ligne 27 signalait.

**Le test d'abord** (`tests/test_sections_liberales.py`), vu rouge (1,15 où le texte
donne 1,10 ; 1,25 où il donne 1,15 ; 0,75 à l'ancien combattant de soixante mois), puis
vert : `test_la_cavamac_sert_l_article_15_de_septembre_2023_des_son_entree_en_vigueur`,
six cas posés à la main, servis par le portage et refaits au bit près par le moteur
Python (`servi_et_refait`). Le test de la ligne 27 passe par la même fonction
(`_ecarts_de_la_cavamac`), sans changer. Le test qui confronte chaque version de la
fiche à sa période, chaque premier du mois, tient les nouveaux paramètres.

**L'effet aux cas posés** (agent général au double du salaire moyen depuis ses 22 ans,
euros de 2026).

- Né le 1er février 1954, pension au 1er novembre 2023, à 69 ans et 9 mois : deux années
  pleines au-delà de 67 ans, 23 698,1944 × 1,10 = **26 068,01 € par an**, au lieu de
  27 252,92 € (1,15) : 1 184,91 € de trop.
- Né le 1er décembre 1953 : au 1er août 2023, statuts de 2011, trois années depuis
  66 ans et 2 mois, 1,15, inchangé ; au 1er septembre 2023, deux années depuis 67 ans,
  1,10, soit 26 017,42 € au lieu de 27 200,03 €.
- Né le 1er décembre 1952, pension au 1er septembre 2023, à 70 ans et 9 mois : trois
  années, 1,15, soit 27 568,36 € au lieu de 29 965,61 € (1,25). **Dix points de trop**,
  et non cinq comme la ligne le disait : l'écart entre 65 ans et 9 mois et 67 ans passe
  l'année.
- Né le 1er août 1961, ancien combattant de soixante mois, pension au 1er novembre 2023
  à 62 ans et 3 mois : 21 070,38 € au lieu de 15 802,79 € ; celui de douze mois garde
  0,75.

**La correction**, dans les données seules : `cavamac_complementaire.yaml`, la période
de 2019 à 2023 coupée en deux. La première, de 2019 à 2022, liquide jusqu'au 31 août
2023 (`date_effet: [2019-01-01, 2023-09-01]`), aux règles de 2011. La seconde, 2023,
liquide du 1er septembre au 31 décembre (`date_effet: [2023-09-01, 2024-01-01]`) :
`age_taux_plein: 67` sans table par génération, le barème de 2011 gardé, l'inapte à
62 ans et l'ancien combattant du 5° de L. 351-8, comme depuis 2024. Le taux de
cotisation est le même des deux côtés. Aucune ligne de code.

**Fichiers fabriqués refaits** : le paquet (`moteur/donnees.json`), les témoins
(`tests/temoins/pages.json` seul bouge), et la page `avantages/index.html`
(`construire_pages.py`), que la suite rapide réclamait : elle compte une période de
plus au catalogue, 969 au lieu de 968.

**La fiche.** `cavamac_minoration_age_seul` : la version de septembre 2023 porte ses
paramètres ; l'écart du taux plein quitte les approximations et passe à l'histoire,
comme la phrase sur les catégories de septembre à décembre 2023. Les limites
(`docs/limites/`) ne nommaient pas cet écart : rien n'y change.

**La classe, pas le cas.** Les autres statuts servis à l'année pleine suivante sont
déjà coupés au jour (CARCDSF, CAVP, CAVEC, CARPIMKO). La CAVAMAC n'en a plus : 2011,
septembre 2023 et 2024 y sont coupés ; le règlement du 18 juillet 2026 dit les mêmes
règles que les statuts de 2024.

**Ce qui reste déclaré** : les années de cumul emploi-retraite, que la majoration ne
compte pas depuis le 1er septembre 2023 (7°, b) ; l'ouverture de l'inapte à 62 ans
avant l'âge légal ; le grand invalide, l'invalide professionnel à 66 %, le travailleur
handicapé ; l'ancien combattant de 2011 au 31 août 2023 ; la date d'effet au trimestre
civil ; les lignes 29 et 30 de la file.
