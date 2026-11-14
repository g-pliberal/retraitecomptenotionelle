# Correction de la ligne 23 de la file : la CARCDSF sert sans minoration l'inapte, l'ancien déporté et l'ancien combattant

Vingt-troisième ligne de la file `2026-11-13-corrections-decidees.md`, décidée par le
propriétaire le 13 novembre 2026. Une ligne, rien d'autre.

**Le texte, relu aux index JORF et LEGI** (à jour du 11 novembre 2026).

- Statuts de 2007, article 20 (JORFARTI000001859980), en vigueur du 11 octobre 2007 au
  30 juin 2011 : « a) A taux plein sans application de coefficients de minoration : - à
  partir de 65 ans ; - à partir de 60 ans pour les adhérents : - reconnus atteints
  d'inaptitude à l'exercice de la profession […] ; - titulaires de la carte de grands
  invalides de guerre […] ; - titulaires de la carte d'ancien déporté, ancien interné de
  la Résistance ou ancien interné politique » (I) ; « entre 60 et moins de 65 ans sans
  qu'il soit fait application du taux de minoration […] : a) Les anciens prisonniers de
  guerre et anciens combattants qui remplissent les conditions d'âge et de durée de
  service prévues par la loi n° 73-1051 […], selon les modalités fixées aux articles
  L. 643-4 d et D. 351-2 » (II).
- Statuts de 2011, article 19, I, a (JORFARTI000023909792), devenu 35 le 25 décembre
  2017 (JORFARTI000036251928) : les trois mêmes catégories, « à partir de l'âge prévu à
  l'article L. 161-17-2 ». L'ancien combattant n'y est plus. Depuis 2017, le parent
  d'un enfant handicapé, « dès l'âge mentionné à l'article L. 161-17-2 ».
- Statuts de 2024, article 35, II (JORFARTI000048880707), et règlement de 2026, article
  3, II (JORFARTI000054435749) : « à l'âge prévu au IV de l'article L. 643-3 du code de
  la sécurité sociale pour les affiliés relevant du 2° de l'article L. 643-4 » —
  l'inapte, le grand invalide, l'ancien déporté ou interné, les « personnes mentionnées
  au 5° de l'article L. 351-8 » (LEGIARTI000047453026) ; l'âge est 62 ans (D. 643-14,
  D. 351-1-14).

Le texte tranche ce que la ligne dit.

**L'erreur.** Le modèle opposait à ces affiliés la minoration de l'assuré valide : 25
points à 60 ans en 2008, 30 à 62 ans en 2017, 15 depuis 2024.

**Le test d'abord** (`tests/test_sections_sante.py`,
`test_la_carcdsf_sert_sans_minoration_l_inapte_et_les_categories_de_ses_statuts`), vu
rouge sur douze des dix-neuf cas, puis vert ; servis par le portage et refaits au bit
près par le moteur Python (`servi_et_refait`). Dentiste au double du salaire moyen
depuis ses 20 ans, euros de 2026 ; le titre ne change pas les points, et chaque attendu
est la pension du taux plein multipliée à la main par le coefficient du texte :

- né le 1er janvier 1948, pension au 1er janvier 2008, à 60 ans : le valide,
  7 342,6791 × 0,75 = 5 507,01 € ; l'inapte et l'ancien déporté, **7 342,68 € par an,
  au lieu de 5 507,01 €** (1 835,67 € de plus) ;
- l'ancien combattant de 2008 : trente mois, né le 1er janvier 1944, à 64 ans,
  7 912,56 € au lieu de 7 516,93 € ; dix-huit mois, né le 1er janvier 1945, à 63 ans,
  7 770,09 € au lieu de 6 993,08 € ; douze mois, au même âge, garde 0,90 ;
- né le 1er janvier 1951, inapte, pension au 1er juillet 2011 : 8 424,85 € au lieu de
  6 529,26 € ;
- né le 1er janvier 1955, pension au 1er janvier 2017, à 62 ans : le valide, 0,70,
  7 083,95 € ; l'inapte et le déporté, 10 119,93 € ; l'ancien combattant de soixante
  mois, que ces statuts ne nomment pas, garde 0,70 ;
- né le 1er janvier 1958, inapte, pension au 1er janvier 2020 : 11 107,90 € au lieu de
  7 775,53 € ;
- né le 1er janvier 1962, pension au 1er juillet 2024, à 62 ans et 6 mois : le valide,
  0,85, 12 023,37 € ; l'inapte, 14 145,14 € ;
- né le 1er janvier 1965, pension au 1er octobre 2027, à 62 ans et 9 mois : le valide,
  0,85, 13 493,37 € ; l'inapte, le déporté et l'ancien combattant de soixante mois,
  15 874,55 € ; celui de douze mois garde 0,85.

**La correction.** Deux paramètres de période, aux dix-huit périodes de 2008 à 2026 de
`carcdsf_complementaire.yaml`, lus des deux moteurs à la fin d'`abattementPoints`
(`moteur/js/droit/liquider.js`) et de son jumeau :

- `age_sans_coefficient_de_l_inapte`, que la CAVOM portait déjà (ligne 1) : 60 sous
  les statuts de 2007, `age_legal_par_generation` de 2011 à 2023 — valeur neuve, que
  `inapteSansCoefficient` lit par `categories.ageLegal` —, 62 depuis 2024 ;
- `categories_sans_coefficient`, neuf (`regimes/_schema.yaml`, `PeriodeRegime`, le
  paquet par `_regles_des_sections`) : les fiches des catégories que la section sert
  sans coefficient, chacune aux conditions que sa fiche écrit à la date d'effet
  (`categories.remplitLUneDe`, `categorieSansCoefficient`) —
  `taux_plein_anciens_deportes_internes` partout,
  `taux_plein_anciens_combattants_prisonniers` de 2008 à 2010 et depuis 2024. Les
  statuts renvoient eux-mêmes à D. 351-2, que cette fiche date.

Aucun témoin de simulation ne bouge.

**La fiche.** `carcdsf_minoration_age_seul` : les deux paramètres dans chaque version ;
l'écart sort des approximations, où ne reste que ce qui suit, et passe à l'histoire.

**Ce qui reste déclaré.**

- Le grand invalide de guerre, et le parent d'un enfant handicapé depuis le 25 décembre
  2017, n'ont pas de saisie : ils gardent la minoration.
- Seule compte l'inaptitude que la carrière déclare : la procédure des statuts n'est
  pas modélisée, et l'invalide n'est pas réputé inapte ici.
- Depuis 2024, l'inapte reste refusé entre 62 ans et l'âge légal de sa génération :
  l'article 1er du règlement demande l'âge de L. 161-17-2, son article 3, II, ouvre
  « un départ anticipé » à 62 ans. Le texte ne tranche pas ; hors de la file.
- Le 1er janvier 2024, où les statuts de 2017 valent encore, la période de 2024 sert
  l'ancien combattant qu'ils ne nomment pas : la ligne 26.
- La base de l'inapte libéral garde son coefficient, écart déclaré ailleurs.

**La classe, pas le cas.** La CAVOM est corrigée (lignes 1 et 2). La CAVEC, la CARPV et
la CAVAMAC, que la note du 5 novembre rangeait dans la même classe, ne sont pas dans la
file pour l'inapte : chacune demande son texte relu ; les deux paramètres y serviraient
tels quels.

**Fichiers fabriqués refaits ici**, parce que la suite rapide les réclamait après le
rebasage sur l'autre file : le paquet (`construire_donnees.py`), et la page toute faite
de la méthode avec son témoin (`construire_pages.py`, `construire_temoins.py`), que
l'inventaire refait à la ligne 15 avait périmés.

**Vérifié** : `python -m pytest -m rapide` ; `test_sections_sante.py`,
`test_sections_liberales.py`, `test_sections_juridiques.py`, `test_invalidite.py`,
`test_carte.py`, `test_donnees.py`, `test_coupures_au_mois.py`, les confrontations
légères (`test_oracle.py`, `test_destinie.py`, `test_estimation_officielle.py`,
`test_verification.py`), `test_pont.py -k refait`, verts.
