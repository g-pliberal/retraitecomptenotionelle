# La carte des fiches : les minorations de la CAVEC et de la CARPV lues au droit, dixième lot

**La demande.** Le 3 novembre 2026, vague 6, la session d'orchestration confie à
la file E le lot que le précédent désignait, les minorations des libéraux
(`cavec_minoration_age_seul`…), à lire au droit texte par texte selon la méthode
du neuvième lot (`130/2026-11-03-carte-des-fiches-coefficients-anticipation-agirc-arrco-lus-au-droit.md`),
sans toucher aux règles du modèle ; et le bloc « Reprise » de l'action. Le lot
pris : les deux minorations « à l'âge seul » dont la règle est la plus simple, la
CAVEC et la CARPV. La CAVAMAC, qui exonère par catégorie et compte par génération,
et la CARCDSF, dont le tableau de 2012 n'est publié qu'en image, font chacune un
lot. Aucun chiffre du modèle ne bouge.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index LEGI et JORF récupérés, à
  jour du 2 et du 3 novembre, sans incrément à appliquer ; `textes.py --inscrire`,
  aucune rédaction nouvelle.
- **Le test d'abord.** Les deux fiches entrent dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vu rouge de leurs quatorze manques. Dans
  `tests/test_sections_liberales.py`, deux tests neufs, vus rouges faute de
  versions : chaque premier du mois que couvre une version, de la création du
  régime à 2040, la période qui liquide une pension prenant effet ce jour porte
  l'âge d'ouverture, l'âge du taux plein et le taux que la version lit, et la
  durée n'y annule pas la minoration ; chaque version lue commence le jour où
  entre en vigueur le texte dont elle naît.
- **`cavec_minoration_age_seul`**, du domaine de la décote et de l'étape qui
  liquide, approchée : cinq versions sur la date d'effet. Avant le 2 mars 2008,
  supposée : les statuts de 1953 et leurs modifications ne sont qu'au Bulletin
  officiel, et l'arrêté du 22 février 2008 « rédige » un article 3.13 qui existait.
  Puis l'article 3.13 de 2008 (« à 65 ans à taux plein ; ― entre 60 et 65 ans,
  avec application d'un abattement définitif de 1,25 % par trimestre manquant ») ;
  l'article 12 des statuts que l'arrêté du 20 août 2018 « remplace », le
  5 septembre 2018 ; sa rédaction du 28 juin 2019, où l'inapte n'attend plus la
  liquidation du régime de base « au titre de l'inaptitude », mais l'est « au
  travail » ; l'article 1.1.3 du règlement approuvé le 10 juillet 2026, le 18
  juillet. La règle ne change pas de 2008 à 2026. Huit arrêtés lus sans effet,
  dont celui du 9 février 2012, qui ajoute à l'article 3.12 ce que le 3.13 disait.
- **`carpv_minoration_age_seul`**, de même, approchée : trois versions. Avant le
  1er janvier 2022, supposée : l'article 21 du titre II, devenu 13 en 2014, n'est
  au Journal officiel que par son sixième alinéa de 2011 — l'invalide inapte
  titulaire de la rente à 100 % « peut demander à bénéficier de la retraite à 60
  ans sans minoration » —, qui suppose une minoration et un départ à 60 ans, sans
  en dire le taux. Puis l'article 34 des statuts de 2021, que l'article 2 de leur
  arrêté fait entrer en vigueur le 1er janvier 2022, et l'article 2 du règlement
  de 2026, mot pour mot : « soit 1,25 % par trimestre manquant avant l'âge de
  soixante-cinq ans ». Quatre arrêtés lus sans effet.
- **Le cliquet des textes** ne bouge pas : 9 350 rédactions sans statut. Une
  rédaction passe d'« à rattacher » à rattachée, le règlement de la CAVEC
  (LEGIARTI000054437585). **La carte** passe de 87 fiches à lire au droit à 85, de
  517 manques à 503. `conservation.py --depuis HEAD` dit changées les lignes de
  veille des deux fiches, refaites depuis elles, ce que la référence figée admet.
  Le paquet du site, refait, ne change pas.

## Les calculs

Les deux statuts disent 1,25 % par trimestre manquant avant 65 ans, dès 60 ans :

- à 60 ans, 65 − 60 = 5 ans, soit 20 trimestres ; 20 × 1,25 % = 25 % ; coefficient
  1 − 0,25 = 0,75 ;
- à 62 ans, 3 ans, soit 12 trimestres ; 12 × 1,25 % = 15 % ; coefficient 0,85 ;
- à 62 ans et 9 mois, 2 ans et 3 mois, soit 9 trimestres ; 9 × 1,25 % = 11,25 % ;
  coefficient 0,8875, celui que `test_la_cavec_minore_par_l_age_seul` attend.

La réversion de la CAVEC, servie « sans application du coefficient de réduction » :
pour un expert-comptable parti à 62 ans, sur des points acquis depuis 2009, le
conjoint reçoit 60 % des points ; le moteur sert 60 % de la retraite servie,
0,60 × 0,85 = 0,51 des points, soit 0,51 / 0,60 = 0,85, 15 % de moins.

## Ce que l'étape laisse

- **Des écarts du modèle, déclarés dans les fiches, que la lecture montre** (la
  file E ne touche pas au modèle ; ils iront à une file du modèle) :
  - **l'inapte servi à 60 ans sans minoration**, dans les deux caisses — à la CAVEC
    depuis 2008 au moins, à la CARPV depuis 2022 pour tout inapte, depuis 2011 au
    moins pour l'invalide à 100 % : la fiche `inaptitude_au_travail` ne nomme que
    six régimes (régime général, salariés agricoles, CANCAVA, ORGANIC, RSI,
    assurances sociales), et le moteur minore l'inapte libéral comme les autres —
    25 % de sa complémentaire à 60 ans, 15 % à 62 ans. La classe : aucune section
    libérale n'y est ; ce que dit chacune se lira à son lot ;
  - **la réversion sans le coefficient** : la CAVEC sert ses points au conjoint
    « sans application du coefficient de réduction » (article 3.17 en 2008, 16 en
    2018, 1.2.2 en 2026) ; la CARPV fait porter à la réversion « le même coefficient
    de minoration », sauf si l'adhérent meurt avant 65 ans. Le moteur applique le
    taux de réversion à la retraite servie, coefficient compris, comme il le fait
    déjà, et le déclare, pour l'Agirc-Arrco, l'Ircantec et la RCI
    (`droit/reversion.py`) ;
  - **la règle d'avant 2008 à la CAVEC, d'avant 2022 à la CARPV**, supposée celle
    des premiers statuts lus.
- **Ce que le texte ne tranche pas** : comment se compte un trimestre entamé — la
  pension prend effet au premier jour d'un trimestre civil à la CAVEC, d'un mois à
  la CARPV, et l'âge n'y tombe pas toujours sur un trimestre entier ; le modèle le
  compte entier, comme R. 351-27 au régime général. Et la règle du 1er au 17
  juillet 2026, quand le décret n° 2026-418 renvoie à un règlement que l'arrêté
  n'approuve que le 18 : les fiches gardent les statuts, de même règle.
- **Une référence non ouverte** : le jour où entre en vigueur un arrêté qui n'en
  fixe pas, les fiches le disent le lendemain de sa publication, comme les autres
  fiches de la carte, sans citer le texte qui le dit, que l'index thématique du
  dépôt ne porte pas.
- **À relire** : les statuts d'avant 2008 de la CAVEC et d'avant 2021 de la CARPV,
  au Bulletin officiel ; la majoration de la CAVEC, que l'arrêté du 20 août 2018
  ramène à 0,75 % et celui du 4 juillet 2025 rend à 1,25 %, relève de la fiche
  `surcote_par_age_seul`.
- **Le lot suivant** : la CAVAMAC (`cavamac_minoration_age_seul`), dont les statuts
  de 2011 exonèrent l'inapte, l'ancien déporté, l'ancien combattant, le grand
  invalide et l'invalide à 66 % ; ou la CARCDSF.

*Renvoi, au 3 novembre 2026 : la relecture R-E et la file E-bis corrigent ce
lot — la réversion des deux caisses n'est pas servie du tout, et non « 15 % trop
basse » ; l'arrêté de la CARPV du 2 novembre 2015 récrit l'alinéa de l'inapte et
devient une version ; voir `130/2026-11-03-corrections-de-la-relecture-r-e.md`.*
