# La carte des fiches : la CAVOM lue au droit, treizième lot

**La demande.** Le 5 novembre 2026, vague 9, la session d'orchestration confie à la file
E la caisse suivante que désignent la carte et les notes du jour : la CAVOM, première des
quatre que le bloc « Reprise » laissait (CAVOM, CARPIMKO, CAVP, CPRN), et ses deux fiches,
`cavom_ages_minoration` et `cavom_assiette_2016`, lues au droit selon la méthode des
onzième et douzième lots (`130/2026-11-05-carte-des-fiches-cavamac-lue-au-droit.md`,
`130/2026-11-05-carte-des-fiches-carcdsf-lue-au-droit.md`), chaque règle confrontée au
modèle dans les deux moteurs, sans toucher au modèle ; puis le bloc « Reprise » de
l'action 130. L'âge de la complémentaire avant la base, que la file N a lu
(`130/2026-11-05-complementaire-avant-la-base-des-liberaux.md`, relu conforme par R-N2),
n'est pas refait. Aucun chiffre du modèle ne bouge, ni le paquet.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index JORF et LEGI récupérés, à jour du
  5 novembre (quatre incréments JORF) et du 4 novembre (deux incréments LEGI).
- **Le test d'abord.** Les deux fiches entrent dans `LUES_AU_DROIT`
  (`tests/test_carte.py`), vu rouge de leurs manques ; `cavom_ages_minoration` dans
  `MINORATIONS_LUES_AU_DROIT` et `NAISSANCES_AU_JOURNAL_OFFICIEL`
  (`tests/test_sections_liberales.py`), trois tests vus rouges faute de versions. Le
  modèle porte chaque premier du mois les paramètres de chaque version (`abattement_points:
  cavom`, `age_table: cavom`, aucune surcote) : ce qui le sépare du texte tient aux
  catégories et à la date d'effet, que ces paramètres ne disent pas.
- **`cavom_ages_minoration`**, approchée : quatre versions sur la date d'effet.
  - **Avant le 1er janvier 2016, supposée.** Les statuts de 1979 (arrêté du 11 avril 1979)
    ne sont pas à l'index ; l'article 14 est modifié en 1996 et en 2001, au seul Bulletin
    officiel (no 96-36, no 2001/29). La fiche présume la règle de 2016 aux nés avant 1956.
  - **Les statuts de 2016** (arrêté du 30 décembre 2015, publié le 31, sans date : le 1er
    janvier 2016), articles 14 et 23 : dès 62 ans « En cas d'inaptitude au travail », ou
    avec « 0,75 si la retraite est attribuée lorsque l'affilié est âgé de 62 ans », jusqu'à
    0,95 à 66 ans, « n'étant pas susceptibles de fractionnement » ; « À partir de 67 ans
    sans application de coefficients d'anticipation » ; pour les générations d'avant
    1959, le tableau, de 60 et 65 ans jusqu'à 1955 à 61 ans et 6 mois et 66 ans et 6 mois
    en 1958, et « Les taux de décote sont ajustés en conséquence » ; la pension « prend
    effet au plus tôt au premier jour du trimestre civil qui suit » la demande, la
    cessation et le paiement des cotisations. L'arrêté du 28 août 2020 (publié le 6
    septembre) ne change que le renvoi de l'inaptitude, « dans les statuts en vigueur ».
  - **Les statuts de 2025** (arrêté du 12 décembre 2024, « entrent en vigueur au 1er
    janvier 2025 ») : l'ouverture « a) 62 ans pour les affiliés relevant du a du 2° de
    l'article L. 643-4 », l'inapte (L. 643-4 : « a) Reconnus inaptes au travail »), « b) 64
    ans à compter de la génération 1968 », et de 60 ans à 63 ans et 6 mois avant ; le
    taux plein à 67 ans depuis 1959 ; « 5 % par année manquante », « Ce coefficient n'est
    pas susceptible de fractionnement » ; l'article 23 abrogé. L'inapte n'est plus exempt :
    il ouvre à 62 ans, avec le coefficient.
  - **Le règlement de 2026** (annexe I de l'arrêté du 10 juillet 2026, publié le 17, le 18
    juillet), que l'article 5 du décret n° 79-265 appelle depuis le 1er juillet : la règle
    de 2025, mot pour mot (article 1er, I et II).
  - Trois textes lus sans effet : l'arrêté du 7 octobre 2014 (les points des classes),
    celui du 21 décembre 2016 (gouvernance, cotisations, réversion, conjoint
    collaborateur), l'article 1er de l'arrêté du 10 juillet 2026.
- **`cavom_assiette_2016`**, transcrite : quatre versions sur l'année du revenu.
  - **Avant 2016, supposée** : six classes de points (décret n° 79-265, article 2, rédaction
    de 2013), dont les bornes de revenu sont aux statuts, hors de l'index ; le modèle y
    projette la règle de 2016.
  - **Le décret n° 2015-1875** (1er janvier 2016) : 12,5 % du revenu « dans la limite d'un
    plafond égal à 8 fois le plafond », l'assiette au moins « au quart de ce plafond »
    (article 1er), et, « pour les années 2016 à 2019 », 4, 5, 6 et 7 plafonds « pour les
    cotisations appelées » chaque année (article 3, II, et non 1er, II, comme le disait la
    fiche, d'après la note de LEGI).
  - **Le décret n° 2019-373** : « à 19 % » au lieu d'« au quart » (article 3), « pour les
    cotisations dues au titre des périodes courant à compter du 1er janvier 2019 »
    (article 4).
  - **Le décret n° 2026-418** (1er juillet 2026) : la même règle, le minimum dit aussi des
    deux premières années d'activité.
  - Le taux, 12,50 %, lu aux décrets de chaque année de 2016 à 2025 ; celui de 2026 n'est
    pas à l'index pour la CAVOM (le décret n° 2025-1076, article 14, « Pour l'année 2026 »,
    ne nomme que trois autres sections).
- **Les citations** ont été vérifiées par un script : chacune, ses morceaux séparés par
  « [...] », espaces ramenées, se trouve dans le texte de l'index qu'elle nomme. **Le
  cliquet des textes** descend de 9 319 à 9 317 rédactions sans statut, celles que les
  versions citent désormais. **La carte** passe de 84 fiches à lire au droit à 82, de 491
  manques à 478, comptés par `carte.manques()` avant et après le lot.
- **Les deux moteurs** ont joué chaque cas sur la même requête du formulaire (statut
  `officier_ministeriel`, entrée à 25 ans, deux salaires moyens, naissance le 10 du mois),
  le portage servi et le moteur Python refait au bit près (`servi_et_refait`,
  `tests/outils_pont.py`) : même coefficient, même montant, même date.

## Les calculs

Chaque valeur du modèle est celle des deux moteurs (essai du jour) ; chaque valeur du
texte, posée à la main. Une pension prend effet, au modèle, le premier du mois qui suit
l'âge ; une naissance en mars fait tomber cette date au premier jour d'un trimestre civil,
celle des statuts.

- **2016 à 2024, la minoration, d'accord** : né le 10 mars 1959, 62 ans le 10 mars 2021,
  pension le 1er avril 2021, « âgé de 62 ans », 0,75 ; le modèle, 67 − 62 = 5 années,
  0,75. À 63 ans et 6 mois, le 1er octobre 2022 : « âgé de 63 ans », 0,80 ; le modèle,
  3,5 années comptées 4, 0,80. À 64 ans et 3 mois, le 1er juillet 2023 : « âgé de 64 ans »,
  0,85 ; le modèle, 2,75 comptées 3, 0,85. L'année entamée, que la fiche disait non
  tranchée, l'est de 2016 à 2024 pour les nés depuis 1959 : le coefficient suit l'âge
  atteint en années, comme le modèle.
- **Aucune majoration** : le même, à 69 ans, le 1er avril 2028 : le règlement, « sans
  application de coefficients d'anticipation » et rien au-delà, 1 ; le modèle, 1.
- **L'inapte, de 2016 à 2024** : né le 10 mars 1959, inapte, à 62 ans le 1er avril 2021 :
  le texte (article 14, I, 1°), 1 ; le modèle, 0,75, 13 564,47 € par an ; au texte,
  13 564,47 / 0,75 = 18 085,97 €, 4 521,49 € de moins par an. Né le 10 mars 1957, le 1er
  avril 2019 : le modèle, 66 − 62 = 4 années, 0,80, 13 979,56 € ; le texte, 1,
  17 474,45 €. Né le 10 mars 1955, le 1er avril 2017 : le modèle, 0,85, 14 215,21 € ; le
  texte, 1, 16 723,78 €.
- **L'inapte, depuis 2025** : né le 10 mars 1965, 62 ans le 10 mars 2027 : le règlement
  ouvre (1°, a) le 1er avril 2027, 67 − 62 = 5 années, 25 %, 0,75. Le modèle refuse à 62
  ans (`non_ouverte`) et sert 0,75 dès 62 ans et 6 mois, le 1er octobre 2027 : six mois de
  pension perdus, 16 635,98 / 2 = 8 317,99 €.
- **La date d'effet** : né le 10 mai 1959, 62 ans le 10 mai 2021 : le modèle sert la CAVOM
  dès le 1er juin 2021, 0,75, 13 580,64 € par an ; le premier jour d'un trimestre civil où
  il a 62 ans est le 1er juillet 2021 (le 1er avril, il en a 61) : un mois de trop,
  13 580,64 / 12 = 1 131,72 €. Né en avril, deux mois.
- **Ce que le texte ne tranche pas** : né le 10 mars 1956, à 61 ans le 1er avril 2017,
  4,5 années avant 65 ans et 6 mois : le modèle, 0,75 ; les statuts de 2016 disent les
  taux « ajustés en conséquence », sans dire comment. Né le 10 mars 1965, à 62 ans et 6
  mois le 1er octobre 2027, 4,5 années manquantes : le modèle, 0,75 ; le règlement, 0,75
  ou 0,80. Né le 10 mars 1955, à 60 ans le 1er avril 2015 : le modèle, 0,75 ; les statuts
  d'alors ne sont pas lus.
- **L'assiette, d'accord**, en plafonds de l'année : un revenu de 5 plafonds en 2016 cotise
  sur 4 plafonds, 12,5 % × 4 = 0,5 plafond ; en 2017, sur 5 ; en 2020, sur 5, sous 8. Un
  revenu de 0,1 plafond en 2017 cotise sur le quart, 0,25 × 12,5 % = 0,03125 plafond ; en
  2019, sur 19 %, 0,02375. Le modèle porte ces bornes et ces minimums année par année
  (`test_le_plafond_de_la_cavom_monte_par_marches`).

## Ce que l'étape laisse

- **Les erreurs du modèle, déclarées dans la fiche `cavom_ages_minoration`, non
  corrigées, pour le propriétaire** :
  1. **de 2016 à 2024, l'inapte** n'est pas servi sans coefficient dès 62 ans : jusqu'à 25
     points de la pension, 4 521,49 € par an dans le cas posé. La même classe que la
     CAVEC, la CARPV, la CAVAMAC et la CARCDSF ;
  2. **depuis 2025, l'inapte** n'est pas ouvert à 62 ans quand sa génération ouvre plus
     tard : six mois de pension pour la génération 1965 (8 317,99 € dans le cas posé),
     jusqu'à deux ans pour celle de 1968, non essayée. Le modèle refuse aussi la base de
     l'inapte libéral à 62 ans, écart déjà déclaré
     (`130/2026-11-05-retouches-de-la-relecture-r-e2.md`) ;
  3. **la date d'effet** au premier du mois qui suit l'âge, et non au premier jour du
     trimestre civil : un ou deux mois de pension de trop, 1 131,72 € dans le cas posé.
     Elle tient à la fiche `date_effet_mois_suivant`, et vaut sans doute pour la CARPIMKO
     et les autres caisses qui disent le trimestre civil (non lu ici).
- **Rien de faux dans l'assiette** sur ses bornes, son minimum et son taux de 2016 à 2025 ;
  déclarés comme approximations : les classes d'avant 2016, la cotisation « appelée »
  et l'année du revenu, le prorata au mois et non au trimestre civil des statuts (article
  9, V), le taux de 2026 non trouvé, l'officier ministériel salarié (7,50 %) confondu
  avec le libéral.
- **Une référence fausse, corrigée dans la fiche** : la dérogation des plafonds de 2016 à
  2019 est à l'article 3, II, du décret n° 2015-1875, non à l'article 1er, II, comme la
  note de LEGI l'écrit. Les notes de `regimes/cavom_complementaire.yaml` la répètent aux
  périodes de 2017, 2018 et 2019 (lignes 172, 195 et 218) : candidat, non touché.
- **Ce que le texte ne tranche pas** : les coefficients « ajustés en conséquence » des
  générations 1956 à 1958 ; l'année entamée depuis 2025 ; l'âge de l'inapte des
  générations d'avant 1959 de 2016 à 2024 (62 ans, ou l'âge de leur table) ; quel
  plafond borne la régularisation d'une cotisation « appelée » l'année suivante.
- **L'entrée en vigueur** des arrêtés sans date (30 décembre 2015, 28 août 2020, 10 juillet
  2026) est prise au lendemain de leur publication, comme dans les fiches de la CAVEC, de
  la CARPV, de la CAVAMAC et de la CARCDSF : le code civil n'est pas à l'index.
- **Non vérifié** : la réversion (60 % dès 62 ans, article 16 de 2016), hors de ces deux
  fiches ; la condition de cessation et de paiement des cotisations, non modélisée.
- **Les statuts qui manquent**, au seul Bulletin officiel du ministère (à demander à la
  CAVOM, ou à lire en bibliothèque, Bulletin officiel du ministère chargé de la sécurité
  sociale) : les statuts du régime complémentaire approuvés par l'arrêté du 11 avril 1979,
  que l'index JORF n'a pas ; l'article 14 dans la rédaction de l'arrêté du 8 août 1996
  (JO du 30 août 1996, Bulletin officiel no 96-36) et dans celle de l'arrêté du 6 juin
  2001 (JO du 23 juin 2001, Bulletin officiel no 2001/29) ; l'article 9 de l'arrêté du 27
  février 2003 (Bulletin officiel no 2003-14) ; les bornes de revenu des classes d'avant
  2016. Sans eux, la règle des pensions d'avant 2016 reste présumée.

## Le bloc « Reprise » récrit

Daté du 5 novembre 2026, d'après les notes du jour : la CRPNPAC de la file N (1464c06,
R-N 329db34) ; la complémentaire avant la base de la file N (ddc92fc), la phrase qu'elle
proposait reprise en substance, relue conforme par R-N2 (10eb393), et la réparation de
N-bis (0ba2aea), publiée quand ce bloc s'écrit ; la CAVAMAC, la CARCDSF puis la CAVOM lues
au droit, 82 fiches et 478 manques ; les erreurs du modèle déclarées, qui attendent le
propriétaire.

Renvoi du 5 novembre 2026 : les dix écarts faibles de la relecture R-E3 — l'âge de l'inapte né avant 1959 et l'âge de la demande, déclarés non tranchés ; la condition de l'erreur (3), complétée pour l'assuré né le 1er ; cinq imprécisions de lecture ; le bloc et une docstring — sont repris dans `2026-11-05-retouches-de-la-relecture-r-e3.md`.
