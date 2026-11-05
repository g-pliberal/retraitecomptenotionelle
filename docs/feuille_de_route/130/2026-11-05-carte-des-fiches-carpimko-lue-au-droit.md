# La carte des fiches : la CARPIMKO lue au droit, quatorzième lot

**La demande.** Le 5 novembre 2026, vague 10, la session d'orchestration confie à la file
E (tâche E3) la caisse suivante de la carte, la CARPIMKO, et ses deux fiches,
`carpimko_ages_2015` et `carpimko_assiette_2026`, sept manques chacune, lues au droit selon
la méthode de la CAVOM (`130/2026-11-05-carte-des-fiches-cavom-lue-au-droit.md`,
`130/2026-11-05-retouches-de-la-relecture-r-e3.md`) : chaque manque fermé, référence et
citation exactes ; une erreur du modèle que le texte prouve, déclarée avec un cas chiffré,
non corrigée ; ce qui est déclaré ailleurs, renvoyé, non doublé — la CARPIMKO servie
avant 2024 à l'âge de carrière longue de la base (R-N2, N-bis 0ba2aea), l'inapte refusé
avant l'âge légal chez les libéraux, les statuts d'avant le 3 octobre 2015 au seul
Bulletin officiel. Puis le bloc « Reprise » de l'action 130. Aucun chiffre du modèle ne
bouge, ni le paquet.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py`, `docs/veille_droit.md` ; les index JORF et LEGI
  récupérés, à jour du 5 novembre (quatre incréments JORF) et du 4 novembre (deux LEGI).
- **Le test d'abord.** Les deux fiches entrent dans `LUES_AU_DROIT` (`tests/test_carte.py`),
  vu rouge de leurs manques ; `carpimko_ages_2015` dans `NAISSANCES_AU_JOURNAL_OFFICIEL`
  (`tests/test_sections_liberales.py`), vu rouge faute de versions ; un test neuf,
  `test_chaque_version_de_la_carpimko_est_portee_par_le_modele`
  (`tests/test_sections_sante.py`), vu rouge de même, qui lit chaque premier du mois de
  1984 à 2040 les paramètres de chaque version dans la période du modèle — l'âge, la table,
  les taux de décote et de majoration, les vingt trimestres ; pour l'assiette, le taux et
  les limites, l'année du revenu —, hors de l'écart déjà déclaré du 3 octobre au 31 décembre
  2015 (`CARPIMKO_HORS_DU_MODELE`). La CARPIMKO n'entre pas dans
  `MINORATIONS_LUES_AU_DROIT` : sa durée annule l'abattement depuis 2015, ce que ce test
  interdit.
- **Un texte qu'on croyait perdu.** La question 22 tenait les statuts d'avant le 3 octobre
  2015 pour publiés au seul Bulletin officiel. C'est vrai de ceux de 1996 à 2015, non de
  ceux de 1984 : LEGI porte, article par article, les statuts approuvés par l'arrêté du 22
  février 1984 (LEGITEXT000006073598), datés du 1er janvier 1984, le jour où l'article 1er
  du décret n° 84-143 institue le régime. LEGI ne les a jamais mis à jour — ni l'article 13
  modifié en 1989, ni les articles 11 et 12 récrits en 2015 —, d'où une version lue de 1984
  au 30 novembre 1996 seulement. Aucun arrêté que l'index JORF trouve à la section, de
  1984 à 1996, ne touche les articles 10 à 12 : ceux de 1985 à 1995 visent les prestations
  supplémentaires, l'invalidité-décès, l'allocation de vieillesse ou les statuts généraux ;
  celui du 24 janvier 1989, l'article 13 seul.
- **`carpimko_ages_2015`**, approchée : sept versions sur la date d'effet.
  - **Avant 1984**, lue : le décret n° 84-143 institue le régime « A compter du 1er janvier
    1984 » (article 1er), en lieu des régimes de 1956 (article 6). Le modèle n'a pas de
    période avant 1984.
  - **Les statuts de 1984**, lus dans LEGI : la pension à 65 ans, dès 60 ans pour l'inapte
    et l'ancien déporté ou interné (article 10) ; « au premier jour du trimestre civil qui
    suit la demande » (article 11) ; avant 65 ans, « 0,75 si la liquidation intervient à
    soixante ans » jusqu'à 0,95 à soixante-quatre ans (article 12), aucune durée n'y
    entrant. Fin supposée au 1er décembre 1996.
  - **De 1996 à 2015, supposée** : l'arrêté du 20 novembre 1996 n'est au Journal officiel
    que par une mention, « publié intégralement au Bulletin officiel no 96-52 », sans les
    articles qu'il change. La fiche présume la règle du modèle.
  - **Les statuts de 2015** (arrêté du 31 juillet 2015, publié le 2 octobre, sans date : le
    3), articles 11, 12, 12 ter et 12 quater : la table des générations ; 1,25 % par
    trimestre manquant à la durée de la base, dans la limite des trimestres qui séparent du
    taux plein ; pour les générations 1955 et antérieures, « 4 % par année d'anticipation,
    plus » 0,25 % par trimestre manquant ; la majoration de 1,25 % par trimestre civil
    entier d'ajournement, vingt au plus.
  - **Les statuts de 2019** (arrêté du 23 mai 2019, le 31 mai pour ses âges, son article 2
    ne datant que les cotisations de 2020) : l'assuré handicapé, au taux plein (article 11,
    e) et « A partir de cinquante-cinq ans, sans abattement » (article 12, b).
  - **Les statuts de 2024** (arrêté du 27 décembre 2023, publié le 9 janvier 2024, le 10) :
    taux plein à l'âge du 1° de L. 351-8, dès l'âge de L. 161-17-2 avec la durée, dès celui
    du IV de L. 643-3 pour l'inapte et le handicapé, du III pour qui part tôt à la base ; les
    4 % par année abrogés avec l'ancien 12 quater, 2° ; 10 % pour trois enfants.
  - **Le règlement de 2026** (annexe III de l'arrêté du 10 juillet 2026, le 18 juillet), que
    l'article 5 du décret n° 84-143 appelle depuis le 1er juillet : la règle de 2024 mot
    pour mot (articles 3 à 6), la date d'effet de 1984 (article 7).
  - Sept textes lus sans effet : l'arrêté de 1989 (l'article 13), ceux de 2016, 2017, 2018,
    2020 et 2022 (les statuts généraux), celui du 14 novembre 2025 (la cotisation).
- **`carpimko_assiette_2026`**, approchée : deux versions sur l'année du revenu.
  - **Avant 2026**, lue : le forfait et la cotisation proportionnelle (décret n° 84-143,
    article 2, rédaction de 2012 ; en 2025, 2 312 €, 3 %, de 25 246 € à 237 179 €, décret n°
    2025-1076, article 12), que portent les périodes du régime, hors de cette fiche.
  - **Le décret n° 2025-1076**, articles 7 et 14, applicables aux périodes de 2026 (article
    15, II) : une cotisation proportionnelle, l'assiette « comprise entre un minimum et un
    maximum », 8,7 %, « seuil : 50 % » et « plafond : 3 fois le plafond annuel » ; les
    statuts de 2026 (arrêté du 14 novembre 2025, article 7) ; l'article 2 du 1er juillet
    2026, l'appel d'office sur le revenu maximum.
- **Les citations** ont été vérifiées par un script : chacune, ses morceaux séparés par
  « [...] », espaces ramenées, se trouve dans le texte de l'index qu'elle nomme ; deux
  citations altérées exprès y échouent. **Le cliquet des textes** reste à 9 317 rédactions
  sans statut ; aucune rédaction non lue des articles cités (`textes.py --non-lues`). **La
  carte** passe de 82 fiches à lire au droit à 80, de 478 manques à 464.
- **Les deux moteurs** ont joué chaque cas sur la même requête du formulaire (statut
  `auxiliaire_medical`, deux salaires moyens, naissance le 10 du mois), le portage servi et
  le moteur Python refait au bit près (`servi_et_refait`, `tests/outils_pont.py`).

## Les calculs

Chaque valeur du modèle est celle des deux moteurs (essai du jour) ; chaque valeur du
texte, posée à la main.

- **1984 à 1996, l'âge seul** : né le 10 mars 1930, entré à 20 ans, 160 trimestres pour
  150, il part à 60 ans le 1er avril 1990, premier jour d'un trimestre civil. Le modèle sert
  465,78 € par an, sans coefficient, la durée atteinte ; l'article 12, 0,75, 0,75 × 465,78
  = 349,33 € : **116,44 € par an de trop**. Entré à 26 ans, sans la durée, le modèle rend
  0,75, 349,33 €, comme les statuts. À 65 ans, aucun des deux ne majore.
- **2015 à 2024, les générations 1955 et antérieures** : né le 10 décembre 1954, entré à 20
  ans, durée atteinte, il part à 62 ans le 1er janvier 2017. Jusqu'à 65 ans, le 10 décembre
  2019 : 2 ans, 11 mois et 9 jours, onze trimestres et un incomplet « considéré comme un
  trimestre entier », douze, trois années, 4 % × 3 = 12 % ; aucun trimestre manquant ;
  0,88. Le modèle n'abat rien et majore depuis l'âge où la durée est atteinte, trois
  trimestres, 1,0375, 5 681,23 € par an ; sans coefficient, 5 681,23 / 1,0375 = 5 475,89 € ;
  aux statuts, × 0,88 = 4 818,78 € : **862,45 € par an de trop**. Entré à 26 ans, 144
  trimestres pour 165, 21 manquants, limités aux douze qui séparent de 65 ans : 12 % + 0,25
  % × 12 = 15 %, 0,85 ; le modèle, 0,85.
- **La date d'effet** : né le 10 novembre 1959, taux plein à 66 ans et 4 mois le 10 mars
  2026, il demande sa pension à 67 ans, en novembre 2026. Le modèle la sert le 1er
  décembre 2026, majorée des deux trimestres civils entiers d'avril à septembre, 1,025,
  5 706,01 € par an. Le règlement (article 7), au premier jour du trimestre civil qui suit
  la demande, le 1er janvier 2027, majorée de trois, octobre à décembre compris, 1,0375 :
  5 706,01 / 1,025 × 1,0375 = 5 775,59 €. **Un mois servi trop tôt, 5 706,01 / 12 = 475,50
  €**, puis 69,59 € par an de moins, aux valeurs de 2026. Le décompte de la majoration par
  trimestre civil entier, lui, tient dans ce cas : deux, comme les statuts au 1er décembre.
- **Ce qui s'accorde** : né en 1958, entré à 30 ans, à 62 ans, seize trimestres jusqu'à 66
  ans, 1,25 % × 16 = 20 %, 0,80 (`test_la_carpimko_arrete_sa_minoration_a_son_propre_age`) ;
  l'assiette de 2026, 8,7 % de 0,5 à 3 plafonds, lue par le test neuf chaque année.

## Ce que l'étape laisse

- **Les erreurs du modèle, déclarées dans la fiche `carpimko_ages_2015`, non corrigées,
  pour le propriétaire** :
  1. **de 1984 à 1996, la durée annule** une minoration que les statuts font de l'âge seul :
     jusqu'à 25 points de la pension, 116,44 € par an dans le cas posé ;
  2. **de 2015 à 2024, les générations 1955 et antérieures** n'ont pas leurs 4 % par année
     d'anticipation, et sont majorées dès que leur durée est atteinte : 862,45 € par an dans
     le cas posé ; jusqu'à 20 points d'abattement à 60 ans ;
  3. **la date d'effet** au premier du mois qui suit l'âge, non au premier jour du trimestre
     civil qui suit la demande, en 1984 comme en 2026 : un ou deux mois de pension, 475,50 €
     dans le cas posé. La même classe que l'erreur (3) de la CAVOM, qui tient à
     `date_effet_mois_suivant`.
- **Renvoyés, non doublés** : la carrière longue avant 2024 et le dernier trimestre de 2015
  (`liquidation_regime_par_regime`) ; l'âge minimal des nés après le 31 août 1961, non
  tranché (même fiche) ; l'inapte refusé avant l'âge légal
  (`130/2026-11-05-retouches-de-la-relecture-r-e2.md`, B2).
- **Ce que le texte ne tranche pas** : l'âge entamé en 1984 (« à soixante ans ») ; l'année
  d'anticipation de 2015, par trimestre ou par année entamée ; l'âge de l'inapte né avant
  1961 de 2015 à 2024 ; la majoration pour trois enfants des pensions déjà servies le 10
  janvier 2024. Les renvois inversés de l'article 12 quater, 1°, de 2015 ne se lisent que
  dans un sens.
- **Non joué** : l'assuré handicapé (2019 et 2024) ; la réversion.
- **L'assiette** : rien de faux sur son taux et ses limites de 2026. Déclarés : le coût
  d'acquisition du point, que l'article 2 du décret n° 84-143 fait fixer par décret et que
  nul texte lu ne fixe ; le taux reconduit après 2026 ; le minimum proratisé au mois sans
  texte de la caisse ; l'appel d'office.
- **Candidats, hors de la tâche** : le modèle ne compte pas les points de la CARPIMKO, ni
  les « 8 points » du forfait et les « 22 points maximum » de 1996 à 2025, ni ceux de 1956
  à 1995 que le règlement de 2026 énumère, et aucune fiche ne lit la cotisation d'avant
  2026 ; le plafond de 2025, 237 179 € au décret, que la période de 2025 porte en cinq
  plafonds, non vérifié.
- **L'entrée en vigueur** des arrêtés sans date (2015, 2019, 2023, 2026) est prise au
  lendemain de leur publication, comme dans les fiches de la CAVOM ; celle de 1996, au
  lendemain de la mention, faute du Bulletin officiel.
- **Les statuts qui manquent**, au seul Bulletin officiel du ministère : l'arrêté du 20
  novembre 1996 (Bulletin officiel no 96-52), et les rédactions qui ont suivi jusqu'en 2015 ;
  les statuts des régimes de 1956 (décrets n° 56-97 et n° 56-129). À demander à la
  CARPIMKO, ou à lire en bibliothèque. Sans eux, la règle des pensions de 1996 à 2015 reste
  présumée.

## Le bloc « Reprise » récrit

Daté du 5 novembre 2026 : la CARPIMKO lue au droit, 80 fiches et 464 manques ; ses trois
erreurs du modèle au propriétaire ; les statuts de la CARPIMKO de 1996 à 2015 parmi ceux
du seul Bulletin officiel ; les points de la CARPIMKO parmi les candidats ; la suite, la
CAVP.
