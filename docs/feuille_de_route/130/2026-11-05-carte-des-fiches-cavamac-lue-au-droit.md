# La carte des fiches : la CAVAMAC lue au droit, onzième lot

**La demande.** Le 5 novembre 2026, vague 7, la session d'orchestration confie à la
file E le bloc « Reprise » de l'action 130, dit d'après les notes, puis le lot que le
précédent désignait : la minoration de la CAVAMAC (`cavamac_minoration_age_seul`), lue
au droit texte par texte selon la méthode du dixième lot
(`130/2026-11-03-carte-des-fiches-minorations-cavec-et-carpv-lues-au-droit.md`, corrigé
par `130/2026-11-03-corrections-de-la-relecture-r-e.md`), sans toucher aux règles du
modèle. Aucun chiffre du modèle ne bouge.

## Ce qui est fait

- **La veille d'abord** : `veille_droit.py` ; les index JORF et LEGI récupérés, à jour du
  5 novembre (quatre incréments JORF appliqués) et du 4 novembre (deux incréments LEGI).
- **Le test d'abord.** La fiche entre dans `LUES_AU_DROIT` (`tests/test_carte.py`), vue
  rouge de ses sept manques. Dans `tests/test_sections_liberales.py`, elle entre dans
  `MINORATIONS_LUES_AU_DROIT` et dans `NAISSANCES_AU_JOURNAL_OFFICIEL` : trois tests vus
  rouges faute de versions. Le premier compare désormais, à chaque premier du mois, tous
  les paramètres que la version lit, et non trois nommés : les âges de la CAVAMAC vont
  par génération, et ceux de la CAVEC et de la CARPV restent comparés de même.
- **`cavamac_minoration_age_seul`**, du domaine de la décote et de l'étape qui liquide,
  approchée : cinq versions sur la date d'effet.
  - **Avant le 1er juillet 2011, supposée.** Les statuts de 1967 ne sont à l'index que
    par leur titre ; l'arrêté du 12 janvier 1990 modifie leurs articles 12 et 15, celui
    du 11 août 1998 leurs articles 1er à 23, publiés en entier au seul Bulletin officiel
    (no 90-05, no 98-38). Celui du 17 décembre 2007 ne touche que les articles 1er, 3, 4
    et 5. La fiche présume la règle de 2011.
  - **Les statuts de 2011**, en vigueur « le 1er juillet 2011 » (article 2 de l'arrêté du
    23 juin) : taux plein à « l'âge prévu à l'article L. 161-17-2 du code de la sécurité
    sociale augmenté de cinq années » (article 15), liquidation dès l'âge de L. 161-17-2,
    5 % par tranche de douze mois jusqu'à 25 % du 49e au 60e mois (article 16), la durée
    n'entrant nulle part ; sans minoration dès l'âge de L. 161-17-2, cinq catégories (15,
    a à e) ; 5 % de majoration « pour chaque année pleine différée », 25 % au plus. Le
    modèle lit l'âge du taux plein dans la table du 1° de L. 351-8 : de 2011 au 31 août
    2023, ce 1° dit les mêmes mots, « l'âge prévu à l'article L. 161-17-2 augmenté de
    cinq années » (LEGIARTI000023030950, puis LEGIARTI000028498855).
  - **Les statuts de septembre 2023** : l'arrêté du 4 août 2023 met le 6° de son annexe
    en vigueur « le 1er septembre 2023 » — le taux plein « de 67 ans », les catégories
    sans minoration redites par renvoi aux 2° et 3° de L. 643-4 et à l'invalide
    professionnel à 66 % — et le b du 7°, la majoration hors des années de cumul ; le
    barème de 2011 reste jusqu'au 31 décembre.
  - **Les statuts de 2024** : les a, c et d du 7°, « le 1er janvier 2024 » — « 1,25 % par
    trimestre manquant pour atteindre l'âge mentionné au premier alinéa de l'article
    15 », la majoration par année pleine « cotisée dans le présent régime », la longue
    carrière à 62 ou 63 ans « avec, dans les deux cas, l'application d'un coefficient de
    minoration de 15 % ». L'exemple de la caisse (`cavamac_rco_decote_cinq_trimestres`)
    y tombe : un départ au 1er juillet 2026.
  - **Le règlement de 2026** (annexe I de l'arrêté du 10 juillet 2026, articles 4 et 5),
    le 18 juillet, lendemain de sa publication : la règle de 2024 ; la longue carrière
    perd ses 15 % « à compter de l'âge de 64 ans ». Le décret n° 67-1169, article 4, y
    renvoie depuis le 1er juillet (décret n° 2026-418).
  - Six arrêtés lus sans effet (2007, 2012, 2014, 2016, 2017, 2025) ; ceux de 2020 et de
    2021 ne touchent qu'aux statuts généraux.
- **Les citations** ont été cherchées par un script dans le texte de l'index, espaces
  ramenées : toutes y sont mot pour mot. **Le cliquet des textes** descend de 9 332 à
  9 331 rédactions sans statut (`perimetre.yaml`) : une rédaction que la fiche cite
  entre dans la liste. `conservation.py --depuis HEAD` dit changés le bloc « Reprise »
  récrit et la ligne de veille de la fiche, refaite depuis elle ; le test de la
  conservation reste vert. **La carte** passe de 86 fiches à lire au droit
  à 85, de 505 manques à 498, comptés par `carte.manques()` avant et après le lot (le
  3 novembre, après R-E, 85 et 503 : des fiches sont nées depuis).

## Les calculs

Chaque valeur du modèle citée ici est rendue par le moteur Python (essai du jour, détail
de la pension) ; chaque valeur du texte, posée à la main.

- **2011, la minoration** : né en 1955, l'âge de L. 161-17-2 est 62 ans
  (`age_ouverture_requis.csv`), le taux plein 62 + 5 = 67 ans. Parti à 62 ans en 2017,
  60 mois avant 67 ans : « entre le 49e et le 60e mois », 25 %, coefficient 0,75 ; le
  modèle, 0,75. Né en 1953, l'âge est 61 ans et 2 mois, le taux plein 66 ans et 2 mois,
  et la table du 1° de L. 351-8 dit 66,17 : la même chose.
- **2011, la majoration du second semestre** : né en février 1945, l'âge de L. 161-17-2
  est 60 ans, le taux plein 65 ans, en février 2010. Liquidé en novembre 2011 à 66 ans
  et 9 mois : une année pleine différée, 5 %, coefficient 1,05. Le modèle prend la
  période de 2004 à 2011, sans `surcote_par_trimestre` : coefficient 1. En novembre 2012,
  deux années, 1,10, et le modèle 1,10.
- **Septembre à décembre 2023** : né en février 1954, liquidé en novembre 2023 à 69 ans
  et 9 mois. Le texte : 2 ans et 9 mois au-delà de 67 ans, deux années pleines, 10 %,
  1,10. Le modèle : la table dit 66,58, soit 66 ans et 7 mois ; 3 ans et 2 mois, trois
  années, 1,15.
- **2024, la minoration** : l'exemple de la caisse, né le 8 août 1960, parti le 1er
  juillet 2026, à cinq trimestres de la date d'effet du taux plein, le 1er octobre 2027
  (67 ans le 8 août 2027) : 5 × 1,25 % = 6,25 %.
- **2024, la longue carrière** : né en 1964, au travail depuis ses 18 ans ; le modèle sert
  0,75 à 62 ans (20 trimestres × 1,25 % = 25 %) et 0,80 à 63 ans (16 × 1,25 % = 20 %) ;
  le texte, 1 − 0,15 = 0,85 aux deux âges.
- **L'inapte** : né en 1955, déclaré inapte, parti à 62 ans en 2017 : le modèle sert
  0,75, comme à l'agent valide ; l'article 15, a), le sert « à taux plein sans
  application d'un coefficient de minoration », 1.

## Ce que l'étape laisse

- **Cinq écarts du modèle, déclarés dans la fiche, pour une file du modèle** (la file E
  n'y touche pas) :
  1. **l'inapte et les catégories sans minoration** ne sont pas servis, de 2011 à
     aujourd'hui : jusqu'en 2023 `abattement_ircec` ne lit que l'âge ; depuis 2024
     `abattement_regime_de_base` n'exonère l'inapte et le travailleur handicapé que
     dans les régimes des fiches de l'inaptitude et du handicap, où la CAVAMAC n'est
     pas. Toute la minoration de son âge, 25 % à 62 ans. La même classe que la CAVEC et
     la CARPV ;
  2. **la majoration du second semestre 2011** n'est pas servie : la période de 2004 à
     2011 n'en porte pas, quand les statuts de 2011 sont en vigueur le 1er juillet ;
  3. **de septembre à décembre 2023**, la majoration des générations de juillet 1951 à
     1954 se compte depuis l'âge de la table de L. 351-8, et non depuis 67 ans : 5 points
     de trop au plus ;
  4. **la longue carrière à 15 %** n'est pas portée (déjà déclarée) : 10 points de trop
     à 62 ans, 5 à 63 ;
  5. **la réversion** n'est pas servie, comme à la CAVEC et à la CARPV : aucune fiche de
     réversion ne nomme `cavamac_complementaire`. Le texte : 60 % des points, à 65 ans,
     son montant « n'est pas minoré par le coefficient de minoration » mais « bénéficie
     du coefficient de prorogation ».
- **Ce que le texte ne tranche pas** : la règle d'avant le 1er juillet 2011, au Bulletin
  officiel, où le modèle présume la minoration de 2011 mais ne sert aucune majoration ;
  du 1er au 17 juillet 2026, le règlement que le décret appelle n'est pas encore
  approuvé (les statuts gardés, de même règle) ; l'âge du IV de L. 643-3, que fixe un
  décret non lu ici ; le mois entamé, que le texte compte par tranches de douze « mois
  précédant », et le modèle par trimestres arrondis au-dessus, puis par années — égaux
  aux dates d'effet de la caisse, premiers jours d'un trimestre civil.
- **Non vérifié** : la majoration hors des années de cumul emploi-retraite (7°, b), que
  le modèle ne distingue peut-être pas ; le capital unique sous 1 500 points et la
  majoration pour enfant handicapé, déjà déclarés non portés au régime.
- **À relire** : les statuts de 1990 et de 1998, et l'arrêté du 2 novembre 1983, au
  Bulletin officiel (au propriétaire) ; le décret de l'âge du IV de L. 643-3.
- **Le lot suivant** : la CARCDSF, dont le tableau de 2012 n'est publié qu'en image.

## Le bloc « Reprise » récrit

Daté du 5 novembre 2026, d'après les notes elles-mêmes : la vague 6 (M3-bis de l'action
175, 5cf7bbc, relu conforme 9367bc6 ; M3, 18a4dc3, R-M3c 996649f ; L, 5f19af8, R-L
1dfa59a), le 5 novembre (L-bis 9fcd8a1, R-L-bis a175868 ; L-ter f6012e5, R-L-ter
ca0ba01 ; l'Ircantec d'avant 1983, e27cdce, 6b05a20, R-M3d d573cbd, M3-bis cc627e8,
R-M3-bis 87e0ce8, arrivé pendant la session : conforme, un écart moyen) ; ce qui reste,
la CRPNPAC et les statuts de cinq sections, les quatre défauts candidats, les décisions
du propriétaire ; la carte recomptée, 85 fiches et 498 manques.
