# Correction de la ligne 27 de la file : la CAVAMAC sert sans minoration l'inapte, l'ancien déporté et l'ancien combattant

Vingt-septième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre. La ligne dit « la minoration
de 25 % à 62 ans » : c'est le premier des cinq écarts de la note
`2026-11-05-carte-des-fiches-cavamac-lue-au-droit.md`, l'inapte et les catégories que
les statuts servent sans minoration, à qui le modèle retirait « toute la minoration de
son âge, 25 % à 62 ans ».

**Le texte, relu aux index JORF et LEGI** (à jour des 14 et 13 novembre 2026).

- Statuts de 2011, article 15 (JORFARTI000024270173), en vigueur le 1er juillet 2011 :
  « La pension de retraite complémentaire est liquidée à taux plein sans application
  d'un coefficient de minoration au plus tôt à partir de l'âge prévu à l'article
  L. 161-17-2 du code de la sécurité sociale : a) Pour les adhérents reconnus atteints
  d'inaptitude au travail […] ; b) Pour les anciens déportés et internés […] ; c) Pour
  les personnes, anciens prisonniers de guerre et anciens combattants, visées par le
  décret n° 74-436 du 15 mai 1974, aux âges et conditions de durée de captivité ou
  services fixés par ledit décret […] d) Pour les grands invalides […] e) Pour les
  adhérents reconnus atteints d'une invalidité professionnelle d'un taux supérieur ou
  égal à 66 % ».
- Arrêté du 4 août 2023, annexe, 6°, b (JORFARTI000047977908), en vigueur le
  1er septembre 2023, et règlement de 2026, article 4 (JORFARTI000054436046), mot pour
  mot : « Sont liquidées à partir de l'âge prévu au IV de l'article L. 643-3 et sans
  application d'un coefficient de minoration les pensions de retraite complémentaire
  des assurés mentionnés aux 2° et 3° de l'article L. 643-4 » — l'inapte, le grand
  invalide, l'ancien déporté ou interné, les « personnes mentionnées au 5° de l'article
  L. 351-8 », le travailleur handicapé (LEGIARTI000047453026) ; l'âge de l'inapte est
  62 ans (D. 643-14, D. 351-1-14) ; les âges de l'ancien combattant, ceux de D. 351-2
  (LEGIARTI000049917724).
- Décret n° 74-436, article 1er (LEGIARTI000006764071) : de soixante ans pour
  cinquante-quatre mois de captivité ou de services à soixante-quatre ans pour six ;
  l'article est abrogé depuis le 21 décembre 1985.

Le texte tranche ce que la ligne dit, pour l'inapte et l'ancien déporté ou interné, et
depuis 2024 pour l'ancien combattant.

**L'erreur.** Le modèle opposait à ces affiliés la minoration de l'assuré valide : 25
points à 62 ans jusqu'en 2023, 1,25 point par trimestre avant 67 ans depuis 2024.

**Le test d'abord** (`tests/test_sections_liberales.py`,
`test_la_cavamac_sert_sans_minoration_l_inapte_et_les_categories_de_ses_statuts`), vu
rouge sur dix des seize cas, puis vert ; servis par le portage et refaits au bit près
par le moteur Python (`servi_et_refait`). Agent général au double du salaire moyen
depuis ses 22 ans, euros de 2026 ; le titre ne change pas les points, et chaque attendu
est la pension du taux plein multipliée à la main par le coefficient du texte :

- né le 1er janvier 1951, pension au 1er juillet 2011, à 60 ans et 6 mois, 54 mois
  avant 65 ans : le valide, 12 610,2304 × 0,75 = 9 457,67 € ; l'inapte, 12 610,23 € ;
- né le 1er janvier 1955, pension au 1er janvier 2017, à 62 ans : le valide,
  14 984,9734 × 0,75 = 11 238,73 € ; l'inapte et l'ancien déporté, **14 984,97 € par
  an, au lieu de 11 238,73 €** (3 746,24 € de plus) ;
- né le 1er janvier 1958, inapte, pension au 1er janvier 2020 : 17 879,94 € au lieu de
  13 409,95 € ;
- né le 1er août 1961, inapte, pension au 1er novembre 2023 : 21 070,38 € au lieu de
  15 802,79 € ;
- né le 1er janvier 1962, pension au 1er juillet 2024, dix-huit trimestres avant
  67 ans : le valide, 0,775, 16 858,41 € ; l'inapte et le déporté, 21 752,79 € ;
- né le 1er janvier 1965, pension au 1er octobre 2027, dix-sept trimestres : le valide,
  0,7875, 19 821,04 € ; l'inapte, le déporté et l'ancien combattant de soixante mois,
  25 169,58 € ; celui de douze mois garde 0,7875.

**La correction**, dans les données seules : les deux paramètres de période nés à la
ligne 23 pour la CARCDSF, que les deux moteurs lisent déjà à la fin
d'`abattementPoints`, posés aux quatre périodes de 2012 à 2026 de
`cavamac_complementaire.yaml` —
`age_sans_coefficient_de_l_inapte` (`age_legal_par_generation` jusqu'en 2023, 62 depuis
2024) et `categories_sans_coefficient` (`taux_plein_anciens_deportes_internes` partout,
`taux_plein_anciens_combattants_prisonniers` depuis 2024). Aucune ligne de code ; aucun
témoin de simulation ne bouge. Le test qui confronte chaque version de fiche à sa
période compare désormais une liste à une liste.

**La fiche.** `cavamac_minoration_age_seul` : les deux paramètres dans les quatre
versions lues ; l'écart passe à l'histoire, et l'approximation ne garde que ce qui
suit. Les limites (`docs/limites/`) ne nommaient pas cet écart : rien n'y change.

**Ce qui reste déclaré.**

- L'ancien combattant de 2011 à 2023 garde la minoration : les statuts de 2011 le
  servent aux âges d'un article abrogé en 1985, et la fiche de la catégorie sert sur
  ces années les âges décalés de la pratique de la Cnav, que ces statuts ne nomment
  pas. De septembre à décembre 2023, où le texte nomme déjà le 5° de L. 351-8, la
  période de 2019 à 2023 garde la seule catégorie de 2011 ; la ligne 28, si elle coupe
  cette période au 1er septembre, peut y poser les paramètres de 2024.
- Le grand invalide et l'invalide professionnel à 66 % n'ont pas de saisie ; le
  travailleur handicapé, nommé depuis le 1er septembre 2023, n'est exonéré que dans
  les régimes de la fiche du handicap.
- Depuis le 1er septembre 2023, l'inapte reste refusé entre 62 ans et l'âge légal de
  sa génération (né en 1965, 62 ans et 9 mois) : la minoration est corrigée,
  l'ouverture à 62 ans ne l'est pas. La fiche la posait déjà au propriétaire ; elle
  n'est pas dans la file. À la CAVOM, la ligne 2 l'a ouverte
  (`age_ouverture_de_l_inapte`).
- Avant le 1er juillet 2011, où nul texte n'est lu, l'inapte reste minoré.
- Seule compte l'inaptitude que la carrière déclare.

**La classe, pas le cas.** La CAVOM (lignes 1 et 2) et la CARCDSF (ligne 23) sont
corrigées, la CAVAMAC ici. Restent la CAVEC et la CARPV, que la note du 5 novembre
rangeait dans la même classe et que la file ne nomme pas : chacune demande son texte
relu ; les deux paramètres y serviraient tels quels.

**Vérifié** : `python -m pytest -m rapide` ; `test_sections_liberales.py`,
`test_sections_sante.py`, `test_sections_juridiques.py`, `test_invalidite.py`,
`test_carte.py`, `test_donnees.py`, `test_coupures_au_mois.py`, les confrontations
légères (`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py -k refait`, verts. Refaits : le paquet
(`construire_donnees.py`) ; les témoins (`construire_temoins.py`), inchangés.
