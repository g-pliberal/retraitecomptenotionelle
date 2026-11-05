# La carte des fiches : la CARCDSF lue au droit, douzième lot

**La demande.** Le 5 novembre 2026, la session d'orchestration confie à la file E la
minoration de la CARCDSF (`carcdsf_minoration_age_seul`), lue au droit selon la méthode
du onzième lot (`130/2026-11-05-carte-des-fiches-cavamac-lue-au-droit.md`, relu par
`130/2026-11-05-relecture-de-e-cavamac.md`, retouché par
`130/2026-11-05-retouches-des-relectures-r-e-r-m3-ter-r-l-ter.md`), chaque règle
confrontée au modèle dans les deux moteurs, sans toucher au modèle ; puis le bloc
« Reprise » de l'action 130. Aucun chiffre du modèle ne bouge, ni le paquet.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index JORF et LEGI récupérés, à jour du
  5 novembre (quatre incréments JORF) et du 4 novembre (deux incréments LEGI).
- **Le test d'abord.** La fiche entre dans `LUES_AU_DROIT` (`tests/test_carte.py`), vue
  rouge de ses sept manques ; dans `NAISSANCES_AU_JOURNAL_OFFICIEL`
  (`tests/test_sections_liberales.py`), ses six textes, leur publication et leur entrée en
  vigueur, vu rouge faute de versions. Elle n'entre pas dans `MINORATIONS_LUES_AU_DROIT`,
  qui exige que le modèle porte, chaque premier du mois, les paramètres de chaque
  version : il ne les porte pas du 11 octobre au 31 décembre 2007, du 1er janvier au 30
  juin 2011 ni du 1er au 9 janvier 2024 (écarts 1, 2 et 6 ci-dessous).
- **`carcdsf_minoration_age_seul`**, approchée : sept versions sur la date d'effet.
  - **Avant le 11 octobre 2007, supposée.** Le règlement de 1955, abrogé par l'arrêté du
    1er octobre 2007 (article 2), et ses modifications de 1984, 1985, 1992 et 1997 ne sont
    à l'index que par des notices ; celle de 1997, « (ART. 1 A 28) », au seul Bulletin
    officiel no 97-20. La fiche garde la règle que le modèle sert, la décote du régime de
    base, qu'aucun texte lu ne fonde.
  - **Les statuts de 2007** (arrêté du 1er octobre 2007, publié le 10, sans date : le 11
    octobre) : taux plein à 65 ans ; dès 60 ans, 25 % « au cours de la 61e année », puis
    20, 15, 10 et 5 % ; sans minoration dès 60 ans l'inapte, le grand invalide de guerre,
    l'ancien déporté ou interné ; entre 60 et 65 ans l'ancien prisonnier ou combattant, et
    l'adhérente qui a élevé des enfants, de 64 ans pour un à 60 ans pour cinq ; 10 % de
    plus pour trois enfants ; aucune majoration ; réversion à 60 %.
  - **Les statuts de 2011**, en vigueur « à compter du 1er juillet 2011 » (article 3 de
    l'arrêté du 13 avril) : liquidation dès l'âge de L. 161-17-2, taux plein à cet âge
    « majoré de cinq ans » ; 5 % « par année d'anticipation » pour les nés avant juillet
    1951, le tableau annexé de juillet 1951 à 1955, 1,50 % par trimestre manquant depuis
    1956 ; 1 % « par trimestre civil entier d'exercice libéral suivant le dernier jour du
    trimestre civil incluant l'âge », 20 % au plus ; l'affiliée, une année par enfant
    « mis au monde », cinq au plus.
  - **Leurs bornes de 2012** (arrêté du 9 juillet 2012, publié le 21, le 22 juillet) : le
    tableau s'arrête aux nés de 1954, 1,50 % vaut dès 1955. Le tableau, en 2011 comme en
    2012, n'est publié qu'en image.
  - **Les statuts de 2017** (arrêté du 22 décembre 2017, publié le 24, le 25 décembre) :
    l'article 19 devient 35, l'âge du taux plein s'écrit génération par génération (65
    ans, 65 ans et 4 mois, 65 ans et 9 mois, 66 ans et 2 mois, 66 ans et 7 mois, 67 ans), et
    le parent d'un enfant handicapé part sans minoration dès l'âge de L. 161-17-2.
    L'annexe s'ouvre sur les statuts « des agents généraux d'assurance » : une erreur de
    plume, l'article 1er de l'arrêté nommant ceux de la CARCDSF.
  - **Les statuts de 2024** (arrêté du 27 décembre 2023, publié le 9 janvier 2024, sans
    date : le 10 janvier) : taux plein à l'âge du 1° de L. 351-8, « l'âge prévu au premier
    alinéa de l'article L. 161-17-2 augmenté de trois années », 67 ans ; 1,25 % par
    trimestre manquant, 15 % au plus ; la majoration à 1 % par trimestre accompli avant
    le 1er janvier 2024 (20 % au plus) et à 1,25 % depuis (25 % au plus) ; sans minoration
    les assurés du 2° de L. 643-4 « à l'âge prévu au IV de l'article L. 643-3 », 62 ans
    pour l'inapte (D. 643-14, D. 351-1-14).
  - **Le règlement de 2026** (annexe I de l'arrêté du 10 juillet 2026, publié le 17, le 18
    juillet), que le décret n° 2026-418 (article 5, 3°) appelle à l'article 4 du décret n°
    50-28 depuis le 1er juillet : la règle de 2024, mot pour mot (article 3).
  - Trois textes lus sans effet : l'arrêté du 28 décembre 2010 (un intitulé, le cumul),
    celui du 30 juillet 2013 (les prestations complémentaires et l'invalidité-décès),
    celui du 21 septembre 2026 (les prestations complémentaires).
- **Les citations** ont été tirées par un script du texte de l'index, entre deux bornes,
  puis chacune, et chaque mot cité ailleurs dans la fiche, recherchée dans les textes
  qu'elle nomme, espaces ramenées : toutes y sont. **Le cliquet des textes** ne bouge pas
  (9 330). **La carte** passe de 85 fiches à lire au droit à 84, de 498 manques à 491,
  comptés par `carte.manques()` avant et après le lot.
- **Les deux moteurs** ont joué chaque cas sur la même requête du formulaire (statut
  `chirurgien_dentiste_ou_sage_femme`, naissance au 1er du mois) : le Python par `_python`
  (`tests/test_liquidation.py`), le portage par `tests/js/comparer-liquidation.mjs`. Ils
  rendent partout la même date d'effet, le même motif, le même coefficient et la même
  ligne de réversion.

## Les calculs

Chaque valeur du modèle est celle des deux moteurs (essai du jour) ; chaque valeur du
texte, posée à la main. Carrière dès 25 ans sauf mention.

- **2007, la minoration** : né le 1er octobre 1945, carrière dès 20 ans, liquidé le 1er
  novembre 2007 à 62 ans et 1 mois, « au cours de la 63e année » : 15 %, 0,85. Le modèle,
  par la période de 2004 à 2007 : la durée réunie annule la décote, 1. Né le 1er janvier
  1945, liquidé le 1er janvier 2008 à 63 ans, « 64e année » : 10 %, 0,90 ; le modèle, 0,90.
- **2007, la mère** : la même, mère de trois enfants : « à partir de 62 ans pour trois
  enfants », 1, et 10 % de plus ; le modèle, 1 sans les 10 % (aucun complément). En 2009,
  né le 1er octobre 1945, trois enfants, à 64 ans et 1 mois : le modèle sert 0,95 et les
  10 % ; le texte de même.
- **Le premier semestre 2011** : né le 1er septembre 1950, liquidé le 1er mars 2011 à 60
  ans et 6 mois : les statuts de 2007, en vigueur jusqu'au 30 juin, « 61e année », 25 %,
  0,75 ; le modèle, 65 − 60,5 = 4,5 ans, 18 trimestres × 1,25 % = 22,5 %, 0,775. Né le 1er
  janvier 1944, liquidé le 1er avril 2011 à 67 ans et 3 mois : les statuts de 2007 ne
  majorent pas, 1 ; le modèle, 9 trimestres depuis 65 ans × 1 %, 1,09.
- **2011 à 2017, la minoration** : né le 1er janvier 1955, liquidé le 1er janvier 2017 à
  62 ans (L. 161-17-2, « soixante-deux ans pour les assurés nés à compter du 1er janvier
  1955 ») : taux plein à 67 ans, 20 trimestres × 1,50 % = 30 %, 0,70 ; le modèle, 0,70. Né
  le 1er janvier 1951, liquidé le 1er janvier 2014 : un départ à 65 ans prend effet le 1er
  janvier 2016, deux années d'anticipation × 5 %, 0,90 ; le modèle, 0,90. Né le 1er janvier
  1947, liquidé le 1er juillet 2011 : six mois d'anticipation, 2,5 % si l'année se
  partage, 5 % si l'année entamée compte, 0,975 ou 0,95 ; le modèle, 0,975.
- **L'inapte et le déporté** : nés le 1er janvier 1948, liquidés le 1er janvier 2008 à 60
  ans : le texte (2007, 20, I, a), 1 ; le modèle, 0,75. Nés le 1er janvier 1955, liquidés
  le 1er janvier 2017 à 62 ans : le texte (2011, 19, I, a), 1 ; le modèle, 0,70. Inapte né
  le 1er janvier 1965 : à 62 ans, le 1er janvier 2027, le modèle refuse (`non_ouverte`,
  âge opposé 62,75) ; à 62 ans et 9 mois, le 1er octobre 2027, il sert 0,85 ; le
  règlement, 1.
- **La majoration, au trimestre civil** : né le 1er janvier 1948, taux plein à 65 ans le
  1er janvier 2013, dans le trimestre civil de janvier à mars ; liquidé le 1er janvier
  2015 : trimestres entiers d'avril 2013 à décembre 2014, 3 + 4 = 7, 1,07 ; le modèle,
  1,08. Le même, sans activité de 2010 à 2014 : le texte, aucun trimestre d'exercice, 1 ;
  le modèle, 1,08. Né le 1er janvier 1953, à 69 ans le 1er janvier 2022 : taux plein à 66
  ans et 2 mois le 1er mars 2019, trimestres d'avril 2019 à décembre 2021, 3 + 4 + 4 = 11,
  1,11 ; le modèle, 1,11 (l'âge ne tombe pas le premier jour d'un trimestre). Né le 1er
  janvier 1946, liquidé le 1er octobre 2011 : avril à septembre 2011, 2 trimestres, 1,02 ;
  le modèle, 1,03.
- **La majoration depuis 2024** : né le 1er janvier 1955, liquidé le 1er janvier 2025 à 70
  ans : 67 ans le 1er janvier 2022 ; avril 2022 à décembre 2023, 7 trimestres × 1 % = 7 % ;
  2024, 4 × 1,25 % = 5 % ; 1,12 ; le modèle, 12 × 1,25 % = 15 %, 1,15. Né le 1er janvier
  1953, liquidé le 1er avril 2024 : 67 ans (1° de L. 351-8 depuis le 1er septembre 2023) le
  1er janvier 2020 ; avril 2020 à décembre 2023, 15 × 1 % = 15 % ; janvier à mars 2024,
  1,25 % ; 1,1625 ; le modèle, depuis 66 ans et 2 mois, 20 trimestres au plus × 1,25 %,
  1,25. Né le 1er janvier 1958, liquidé le 1er janvier 2028 : avril 2025 à décembre 2027,
  11 × 1,25 % = 13,75 %, 1,1375 ; le modèle, 1,15.
- **2024, la minoration** : né le 1er janvier 1962, liquidé le 1er janvier 2027 à 65 ans :
  8 trimestres × 1,25 % = 10 %, 0,90 ; le modèle, 0,90. Né en 1975, à 64 ans : 12
  trimestres, 15 % au plus, 0,85 ; le modèle, 0,85 (`test_sections_sante.py`). En 2022,
  aux statuts de 2017, la mère de cinq enfants née le 1er janvier 1960, à 62 ans : 67 − 5
  = 62, 1 ; le modèle, 1.
- **Le 1er janvier 2024** : né le 1er septembre 1961, liquidé à 62 ans et 4 mois : 67 ans
  le 1er septembre 2028, 56 mois plus tard ; les statuts de 2017, encore en vigueur, 18
  trimestres entiers × 1,50 % = 27 %, 0,73, ou 19 si le trimestre entamé compte, 0,715 ;
  le modèle, la règle de 2024, 0,85.
- **La réversion** : dentiste né le 1er juin 1950, liquidé à 65 ans, mort en juin 2020,
  conjointe née en 1952 (68 ans), mariés en 1975 : base 6 912,27 €, montant 0, motif
  `non_portee`, dans les deux moteurs ; le texte, 60 % × 6 912,27 = 4 147,36 € par an. Né
  le 1er juin 1960, mort en juin 2030, conjointe de 1958, mariés en 1985 : base
  9 423,69 €, montant 0 ; le texte, 5 654,21 €.

## Ce que l'étape laisse

- **Les erreurs du modèle, déclarées dans la fiche, non corrigées, pour le propriétaire** :
  1. **du 11 octobre au 31 décembre 2007**, les statuts de 2007 ne sont pas servis : la
     décote du régime de base, que la durée annule, en tient lieu ; ni la majoration de
     10 % pour trois enfants ni le taux plein avancé de la mère. Jusqu'à 25 points à 60
     ans, et 10 % de la pension ;
  2. **du 1er janvier au 30 juin 2011**, les statuts de 2011 sont servis six mois trop tôt :
     2,5 points de minoration en moins à 60 ans et 6 mois, et une majoration que ceux de
     2007 ne servent pas, jusqu'à 20 points ;
  3. **l'inapte et les catégories sans minoration** ne sont pas servis, de 2007 à
     aujourd'hui : 25 points en 2008, 30 en 2017, 15 en 2027 et un refus avant l'âge légal
     depuis 2024 ; le parent d'un enfant handicapé, nommé depuis le 25 décembre 2017, n'a
     pas de saisie : toute la minoration. La même classe que la CAVEC, la CARPV et la
     CAVAMAC ;
  4. **la majoration** se compte au temps écoulé, non par trimestre civil entier
     d'exercice libéral : un point (1,25 depuis 2024) de trop quand l'âge tombe le premier
     jour d'un trimestre civil, toute la majoration sans activité (20 points, 25 depuis
     2024) ;
  5. **depuis 2024**, la majoration vaut 1,25 % pour tous les trimestres, et se compte
     depuis l'âge de la table pour les nés de juillet 1951 à 1954, au lieu de 67 ans : 3
     points de trop pour le né de 1955 à 70 ans, 8,75 pour le né de 1953 en avril 2024 ;
  6. **la réversion** n'est pas servie (`non_portee`) : 60 % de la pension, 4 147,36 € et
     5 654,21 € par an dans les deux cas posés.
- **Ce que le texte ne tranche pas** : la règle d'avant le 11 octobre 2007, au Bulletin
  officiel ; celle des sages-femmes avant 2009, à la CARSAF, et de 2009 au 30 juin 2011,
  que les statuts de 2007, écrits pour les seuls chirurgiens-dentistes, ne nomment pas ;
  le tableau en image ; l'année d'anticipation entamée des nés avant juillet 1951 ; la
  pension du 1er janvier 2024 (0,85 au modèle, 0,73 ou 0,715 aux statuts de 2017, en
  vigueur jusqu'au 9 janvier) ; l'inapte à 62 ans, que l'article 3, II, du règlement
  ouvre quand l'article 1er demande l'âge de L. 161-17-2 ; si les plafonds de 20 et de
  25 % de la majoration se cumulent ; si les statuts de 2011 comptent l'exercice d'avant
  le 1er juillet 2011 ; le trimestre entamé de la minoration ; la date d'effet au premier
  jour du trimestre civil qui suit la demande, que le modèle met au mois.
- **L'entrée en vigueur** des arrêtés sans date est prise au lendemain de leur
  publication, comme dans les fiches de la CAVEC et de la CARPV : le code civil n'est
  pas à l'index, et son article 1er n'a pas été relu ici.
- **Non vérifié** : l'ancien prisonnier ou combattant de 2007 et le grand invalide de
  guerre, non essayés ; la condition d'être à jour de ses cotisations (article 34, puis
  2) ; la majoration de la réversion pour trois enfants.
- **À relire** : le règlement de 1955 et ses modifications au Bulletin officiel, les
  statuts de la CARSAF, le tableau de 2011 et de 2012 ; la pratique de la caisse au 1er
  janvier 2024.

## Le bloc « Reprise » récrit

Daté du 5 novembre 2026, d'après les notes du jour : la CRPNPAC de la file N (1464c06),
qui ne sert plus le régime général du navigant avant l'âge de L. 161-17-2, sa relecture
R-N en cours, le texte qu'elle proposait pour le bloc repris en substance ; les retouches
de R-E, R-M3-ter, R-L-ter et R-D-bis (7e44534) ; la CAVAMAC puis la CARCDSF lues au droit,
84 fiches et 491 manques ; les erreurs du modèle déclarées, qui attendent le propriétaire.
