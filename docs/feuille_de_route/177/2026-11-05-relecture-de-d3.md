# Relecture de D3 : les forfaits de début des indépendants, conformes ; deux écarts faibles, et le point 5 fait pour moitié

File R-D3, le 5 novembre 2026, sur Opus. Relecture indépendante du commit 4cf6b96 (file D,
« D3 », action 177) et de sa note `2026-11-05-forfaits-de-debut-des-independants.md`.
Lecture seule : aucune règle, aucune donnée, aucun test touchés. `veille_droit.py` a été
lancé. Les index LEGI (à jour au 2 novembre 2026) et JORF (au 3) de la DILA ont été
récupérés dans la session ; les circulaires du RSI, retéléchargées de la base de la Cnav.
Chaque texte a été rouvert à la version en vigueur à la date qui compte, chaque valeur
refaite à la main, puis demandée aux deux moteurs.

**Verdict : conforme. Aucun écart grave ni moyen ; deux écarts faibles** (§ 4). Les
citations sont exactes, les bornes sont les dates d'effet des textes, les valeurs
attendues sont justes, les deux moteurs les rendent, les tests étaient rouges sans la
correction, et rien d'autre ne bouge que ce que la note dit. Du point 5, deux choses sont
faites sur cinq (§ 5).

## 1. Les sources, à la bonne version

- **D. 635-10**, six rédactions de 1985 à 2013 (`--diff`). LEGIARTI000006738027 (24 août
  2004) et LEGIARTI000006738028 (26 mars 2005 au 1er janvier 2009) : « Pour les assurés
  commençant l'exercice de leur activité, la cotisation annuelle est calculée sur les
  revenus forfaitaires mentionnés au sixième alinéa de l'article L. 131-6. » LEGIARTI000020032165
  (2009 à 2011) : « septième alinéa ». LEGIARTI000025091405 (1er janvier 2012) : la phrase
  disparaît. **Conforme.**
- **Le « quatrième alinéa » du Journal officiel.** Le décret n° 2004-848, article 1er
  (JORFARTI000001334654), dit bien « quatrième ». Un rectificatif du 28 août 2004
  (JORFARTI000002107853) le corrige : « au lieu de : « ... quatrième... », lire : « ...
  sixième... » ». La note relève l'écart entre JORF et LEGI sans citer le rectificatif,
  qui le règle (§ 4, écart 2).
- **L. 131-6.** LEGIARTI000006740118 (20 décembre 2003 au 3 août 2005) : la citation de la
  note est exacte. Les trois rédactions qui suivent jusqu'au 1er janvier 2009
  (LEGIARTI000006740119, …120, …121) portent la même phrase du forfait, au même sixième
  alinéa. En 2009 (LEGIARTI000020169101, LEGIARTI000020675442), le cinquième alinéa est
  celui de la régularisation (« Les cotisations sont établies sur une base annuelle [...]
  font l'objet d'une régularisation »), le septième celui du forfait, « à titre
  provisionnel ». Les renvois de D. 635-2 (« cinquième ») et de D. 635-10 (« septième »)
  tombent juste. **Conforme.**
- **R. 242-16.** LEGIARTI000006748778 (26 avril 2002 au 1er janvier 2008) et
  LEGIARTI000006748779 (1er janvier 2008) : citations exactes, « dix-huit fois », « majorée
  de 50 % », puis « vingt-sept fois la valeur de la base mensuelle mentionnée au premier
  alinéa ». **Conforme.**
- **D. 633-6** (LEGIARTI000006737897, 8 mai 2004 au 13 décembre 2006) : la « cotisation
  provisionnelle » de base du début d'exercice, « sur la base du revenu mentionné au
  premier alinéa de l'article R. 242-16 ». **Conforme.**
- **D. 635-2.** LEGIARTI000006738016 (24 août 2004 au 1er janvier 2008) : « est assise sur
  les revenus de l'avant-dernière année tels que définis par l'article L. 131-6 et
  recouvrée [...], sous réserve des dispositions des articles D. 635-7 et D. 635-10 » ;
  aucune régularisation. LEGIARTI000006738017 (2008). LEGIARTI000020032159 (29 décembre
  2008) : « calculée suivant les modalités prévues au cinquième alinéa de l'article
  L. 131-6. Sous réserve des dispositions des articles D. 635-7 et D. 635-10, elle est
  recouvrée dans les conditions prévues aux articles R. 133-26 et R. 133-27 ». Citations
  exactes. **Conforme.**
- **D. 635-7** (LEGIARTI000017869802, 1er janvier 2008 au 1er janvier 2012) : le forfait de
  l'artisan, « la cotisation annuelle est assise : 1° [...] tiers du plafond [...] ; 2° [...]
  moitié dudit plafond », supprimé au 1er janvier 2012 (LEGIARTI000025091410). **Conforme.**
- **Les bornes.**
  - 2004 : D. 635-10 fixe son taux « pour l'année 2004 », et le régime naît au
    1er janvier 2004 (exposé de la Cnav « Points cotisés commerçants avant 2013 ») ; le
    décret n° 2004-848 n'a pas d'article d'entrée en vigueur (articles 4 et 5 lus).
  - 2008 / 2009 : décret n° 2008-1427, article 1er, II (JORFARTI000019996956) : « Les
    dispositions du présent article s'appliquent aux cotisations dues au titre des revenus
    des années 2009 et suivantes ».
  - 2011 / 2012 : décret n° 2011-2038, article 3, II (JORFARTI000025055800), qui supprime
    les forfaits de D. 635-7 et de D. 635-10 ; « Entrée en vigueur : le 1er janvier 2012 »
    (notice, JORFTEXT000025055789).

  Les trois bornes sont les dates d'effet. **Conforme.**
- **La base mensuelle.** Les cinq décrets rouverts : 347,68 EUR au 1er janvier 2003
  (n° 2002-1567, JORFARTI000002250315), 353,59 EUR en 2004 (n° 2003-1251,
  JORFARTI000001067893), 361,37 EUR en 2005 (n° 2004-1458, JORFARTI000001724700), 367,87 en
  2006 (n° 2005-1769, JORFARTI000001683087), 374,12 EUR en 2007 (n° 2006-1754,
  JORFARTI000001883075). L'index du JORF, interrogé sur « base mensuelle de calcul » de 2002
  à 2008, n'en porte aucun autre texte de revalorisation : la valeur du 1er octobre est
  celle du 1er janvier. La série `base_mensuelle_prestations_familiales.csv` les recopie
  sans faute. **Conforme.**
- **La caisse.** Les trois circulaires retéléchargées ont l'empreinte que la note donne
  (sha256 05ce2821…8e6e3e70, 61efc134…582a3f82, a7212c2d…bf00c034).
  - Circulaire n° 2007/013, § 2.2 : « Pour le groupe professionnel des commerçants, tous
    les risques, y compris régime complémentaire et invalidité-décès sont calculés sur la
    base de 18 puis 27 BMPF. »
  - Circulaire n° 2008/017 : tableau « 1/3 PSS » et « 18 BMAF », puis « 1/2 PSS » et
    « 27 BMAF ». Elle reproduit la circulaire DSS/5 B/5 C n° 2007-431, dont la note 2 :
    « pour le calcul définitif, la cotisation invalidité-décès et la cotisation de retraite
    complémentaire restent celles qui ont été établies au moment de l'appel
    provisionnel ».
  - Circulaire n° 2008/031, § 3.1.2 : les quatre passages cités, exacts.

  **Conforme**, une réserve de contexte (§ 4, écart 2).

## 2. Les valeurs, refaites à la main

- **Les seize lignes du tableau de la note**, refaites une à une : assiette (18 ou 27 fois
  la base de l'année précédente, ou revenu de l'année), taux, cotisation, points. Revenus
  de référence : `valeurs_point.csv` (RCO : 4,5 en 2009, 4,692 en 2010, 4,79053 en 2011,
  4,89113 en 2012). Plafond : `plafond_securite_sociale.csv` (33 276 € en 2008, 34 308 €
  en 2009, 34 620 € en 2010, 35 352 € en 2011, 36 372 € en 2012).
  - Toutes justes au dix-millième : 18,0223 ; 43,9732 ; 45,1734 ; 29,3155 ; 44,0756 ;
    29,3834 ; 44,3366 ; 93,4641 ; 29,5577 ; 67,9739 ; 71,3686 ; 184,5591 ; 489,1111
    (270,6520 au forfait) ; 450,8896 (177,1094 au forfait) ; 471,0568.
  - Le contrôle du minimum, 200 × 8,03 × 6,5 % / 14,389 = 7,2548.
- **La base mensuelle de la deuxième année**, l'écart déclaré : 27 × (353,59 − 347,68) =
  159,57 € ; 210,06 € ; 175,50 € ; 168,75 € ; 210,06 × 6,5 % / 14,389 = 0,95 point.
  **Conforme.**
- **`metiers_prive_puis_independant`.** Artisan d'une année pleine dès 2010, à
  51 820,70 €, 53 110,23 € et 54 328,34 € de 2010 à 2012. Deux tranches, 7,2 % jusqu'au
  plafond et 7,6 % au-delà :
  - 2010, (34 620 × 7,2 % + 17 200,70 × 7,6 %) / 4,692 = 809,87 ;
  - 2011, 813,06 ; 2012, 814,43 ;
  - total 2 437,35.

  Avant, au forfait : 34 620 / 3 × 7,2 % / 4,692 = 177,08, et 35 352 / 2 × 7,2 % /
  4,79053 = 265,66, plus 814,43 : 1 257,17. La pension gagne 1 180,18 points × 0,468864 €
  = 553,34 €, de 46 148,69 à 46 702,03 € (+1,20 %). **Conforme.**
- **`metier_change_en_cours_d_annee`.** La saisie dit « mai 2011 », mais la carrière
  bâtie donne toute l'année 2011 à l'artisan : une ligne, `fraction_annee` 1,0, à
  42 045,60 €.
  - 2011, (35 352 × 7,2 % + 6 693,60 × 7,6 %) / 4,79053 = 637,52, plus 708,91 en 2012 :
    1 346,42.
  - Avant : 35 352 / 3 × 7,2 % / 4,79053 = 177,11, plus 708,91 : 886,01.
  - 460,41 points × 0,47707 € = 219,65 €, de 46 841,53 à 47 061,17 € (+0,47 %).

  **Conforme.** Que l'année du changement aille entière au nouveau métier est un choix du
  calendrier, antérieur à D3.

## 3. Les deux moteurs, le rouge, et ce que la correction emporte

- **Les deux moteurs.** Les cinq tests visés de `tests/test_independants.py` passent,
  chacun dans les deux moteurs.
  - Sous `PRESOMPTIONS_DECALEES=1`, les quatre qui confrontent le portage sont sautés,
    par construction (`tests/conftest.py` : « le portage lit ses présomptions dans le
    paquet, que la mesure ne décale pas »).
  - J'ai donc fait tourner le Python seul, présomptions décalées, sur les cinq carrières
    du test (commerçant de 2004, débit de tabac de 2007, commerçant de 2008, artisan de
    2008 et de 2011) : points identiques, au dix-millième, à ceux des présomptions du
    vocabulaire.

  **Conforme.**
- **Le rouge.** Une copie de travail du commit, avec `src/`, `moteur/`, `data/` et
  `construire_donnees.py` remis au commit parent, et les tests de D3 gardés : trois
  rouges, pour la raison attendue.
  - Le portage rend 270,652 points en 2009 à l'artisan de 2008, au lieu de 489,1111.
  - Il rend 55,27 au lieu de 29,3155 au commerçant de 2005, et 28,80 au lieu de 18,0223
    à celui de 2004.
  - Le test du minimum passe des deux côtés : il a été déplacé de 2005 à 2006, non
    rougi. 2006 est la troisième année, sur le revenu de 2004 (500 €), sous 200 heures du
    Smic du 1er janvier 2006 (8,03 €), avant comme après la règle.

  **Conforme.**
- **Rien d'autre.**
  - L'artisan de 2004 à 2008 garde son forfait : les périodes du RCO jusqu'en 2008 portent
    toujours `assiette_de_debut`, et le test de l'artisan de 2008 rend 184,5591.
  - Le micro-entrepreneur, qui n'existe que depuis 2009, quand aucune période ne porte
    plus de forfait, voit sa cotisation remplacée par la part de son forfait en aval
    (`parts_du_forfait`, `acquerir.py`) ; `tests/test_micro_social.py` et
    `tests/test_independants.py` : 129 verts.
  - Le gérant de débit de tabac est dans le test.
  - Le conjoint collaborateur n'est pas dans la table des multiples, et son cas est
    déclaré.
  - Les 931 témoins, avant et après, comparés : deux seuls changent, ceux que la note
    nomme, aux pourcentages qu'elle donne (+1,20 % et +0,47 % au scénario 1, +1,32 % et
    +0,53 % aux scénarios 3 et 5).
  - Six rendus de page changent : les cinq du coût et `simuler_hors_de_france_sans_accord`
    (3,02 → 3,03), comme la note le dit. La page du coût bouge aussi d'un dixième de point
    une part, 63,1 % → 63,0 %, que la note ne cite pas : sans conséquence.
  - Suite rapide sur `main` à 4cf6b96 : 4 448 verts, 11 rouges, tous dans
    `tests/test_pages_en_dossier.py`, que GitHub refait.

  **Conforme.**
- **Vu en chemin.** Le décret n° 2011-2038 supprime aussi les forfaits de D. 635-15 et de
  D. 635-17 (LEGIARTI000006738086, LEGIARTI000006738357). Ce sont ceux de
  l'invalidité-décès, que le modèle ne sert pas : rien à faire.

## 4. Ce que le texte ne tranche pas, et les écarts

- **Déclarés, conformes.** Fiche `assiette_rco_independants` (approximations, `a_relire`)
  et `docs/limites/3-systeme-actuel.md` :
  - la base mensuelle de la deuxième année ;
  - le minimum face au forfait définitif, de 2004 à 2008 ;
  - l'acompte sur le revenu estimé.
- **Écart 1, faible : le forfait de l'artisan régularisé de 2009 à 2011 est une lecture,
  non plus déclarée comme telle.**
  - *Ce qui la fonde.* D. 635-2 calcule toute la cotisation « suivant les modalités
    prévues au cinquième alinéa » de L. 131-6, qui vise le revenu « ou des revenus
    forfaitaires » et les régularise. D. 635-10 renvoie au forfait « à titre
    provisionnel » du septième alinéa. La caisse veut la régularisation « dans les mêmes
    conditions que celle applicable au régime légal de base » (circulaire n° 2008/031). Et
    le décret n° 2011-2038 parle de l'assiette forfaitaire « de début d'activité dues, à
    titre provisionnel ».
  - *Ce qui manque.* Pour l'artisan, D. 635-7 (LEGIARTI000017869802) dit toujours la
    cotisation « assise » sur le tiers puis la moitié du plafond, sans la dire
    provisionnelle. Aucun document de la caisse lu ne dit le forfait de début régularisé.
    La circulaire n° 2008/031 dit, de l'artisan qui commence, que « la cotisation
    annuelle reste assise » sur ses forfaits (§ 3.1.1), puis ne parle de la
    régularisation qu'en général. Les deux circulaires « retraite complémentaire » de 2009
    (n° 2009/035, n° 2009/044), lues ici, n'en disent rien.
  - *L'argument de la réserve n'est pas décisif.* La note dit que « la réserve porte sur
    le recouvrement, non sur le calcul ». Mais la même phrase, « Sous réserve des
    dispositions des articles D. 635-7 et D. 635-10, elle est recouvrée », est déjà dans
    la rédaction de 2008 (LEGIARTI000006738017), où la note tient le forfait pour
    définitif.
  - *Ce qui a été retiré.* Les limites disaient : « aucun texte lu ne dit si ce forfait
    l'était ». D3 a retiré la phrase. Le doute ne reste qu'en `a_relire` (« un exemple
    chiffré de la régularisation »), ni aux approximations ni aux limites.
  - *L'enjeu.* Les deux témoins qui bougent (+1,20 % et +0,47 %).
  - *À faire.* La lecture est la plus solide, et je la tiens pour juste. Il reste à
    rendre le doute à une approximation de la fiche et aux limites, jusqu'à ce qu'un
    exemple de la caisse le lève.
- **Écart 2, faible : trois imprécisions de rédaction, sans effet sur le calcul.**
  - « R. 242-16, qui la fixe ». R. 242-16 fixe le forfait de la cotisation d'allocations
    familiales, et D. 633-6 l'étend à la base vieillesse. Pour le NRCO, D. 635-10 ne
    renvoie qu'à L. 131-6, qui pose un plafond (« ne peut excéder »). Que le forfait soit
    ce plafond, ce sont les circulaires de la caisse qui le disent (n° 2007/013,
    n° 2008/017), non un texte.
  - Le tableau de la circulaire n° 2008/017 appartient au « Volet 1 - Plafonnement des
    cotisations » des micro-entreprises, ce que la note ne dit pas ; il reste une
    pièce de la caisse sur le forfait.
  - Le rectificatif du 28 août 2004 manque (§ 1).

## 5. Les écarts de R-D2 confiés à D3

- **(a) L'effet du forfait de début : fait pour moitié.**
  - *Fait.* Le champ `effet` dit maintenant un mois, non deux : « l'artisan qui commence
    en décembre (en 2008, [...] 924,33 €, sous [...] 1 688 € ; sur deux mois, 1 848,67 €,
    non) ». Il ajoute le commerçant (novembre ou décembre, octobre 2008), juste :
    18 × 374,12 × 3 / 12 = 1 683,54 € sous 1 688 €.
  - *Pas fait.* La deuxième année, quand l'activité cesse en janvier, manque toujours, et
    vaut désormais pour les deux. L'artisan : en 2008, 33 276 / 2 / 12 = 1 386,50 € sous
    1 688 € (sur deux mois, non). Le commerçant :
    - en janvier de 2004 à 2008 (en 2006, 27 × 361,37 / 12 = 813,08 € sous 1 606 €) ;
    - en février 2008 (27 × 374,12 × 2 / 12 = 1 683,54 € sous 1 688 €) ;
    - février 2007 y échappe de 1,42 € (1 655,42 € contre 1 654 €).
- **(b) La cessation de 2012 au bloc « Reprise » : faite.** Le bloc daté du 5 novembre
  la nomme parmi les questions au propriétaire : « la cessation de 2012 (décret
  n° 2012-443, article 10, II) ». Sa déclaration côté base, que R-D2 demandait aussi à la
  fiche `assiette_minimale_independants` et aux limites, n'y est pas encore.
- **(c) Les articles qui fixent l'effet des bornes : pas fait.**
  - 1979 : l'article 12 du décret n° 78-351 (LEGIARTI000006766114) est aux `textes` de la
    fiche depuis avant D2.
  - 2012 : l'article 10, II, du décret n° 2012-443 (LEGIARTI000025628404) y est cité
    comme règle de la cessation, non comme preuve de la borne.
  - 2015 et 2016 : ni l'article 31, I, du décret n° 2014-1637, ni l'article 10, I, du
    décret n° 2015-1856 ne sont cités, dans aucune des deux fiches.
- **L'exonération de l'invalide : non déclarée.** D. 635-2 l'exonère « de toute
  cotisation d'assurance vieillesse complémentaire » depuis 2013 (LEGIARTI000025263548,
  puis LEGIARTI000041966510). Rien ne la nomme : ni les fiches, ni les limites, ni la
  table des dispenses.
- **Le minimum qui tombe sur un revenu nul : non déclaré.** Aucune mention dans
  `assiette_minimale_independants`, `assiette_rco_independants` ni les limites.

Ces quatre restes, et l'écart 1, sont à rendre à la file D.

## Sources ouvertes dans la session

- **Index LEGI** de la DILA, à jour au 2 novembre 2026 (`dila_cherche.py legi`) :
  - D. 635-10, ses six rédactions (`--diff`) ;
  - D. 635-2, de 1985 à 2020 (`--diff`) ;
  - D. 635-7, de 1985 à 2024 (`--diff`) ;
  - L. 131-6, les rédactions LEGIARTI000006740118 à …121, LEGIARTI000020169101,
    LEGIARTI000020675442 ;
  - R. 242-16, LEGIARTI000006748778 et …779 ;
  - D. 633-6, LEGIARTI000006737897 ;
  - D. 635-15 et D. 635-17, leurs rédactions de 2004 et de 2007.
- **Index JORF**, à jour au 3 novembre 2026 :
  - décret n° 2004-848, articles 1er, 4 et 5, et son rectificatif du 28 août 2004 ;
  - décret n° 2008-1427, article 1er ;
  - décret n° 2011-2038, notice et article 3 ;
  - les cinq décrets de la base mensuelle, n° 2002-1567 à 2006-1754 ;
  - la recherche « base mensuelle de calcul » de 2002 à 2008.
- **Base de législation de la Cnav**, téléchargées le 5 novembre 2026 :
  - circulaires RSI n° 2007/013, 2008/017 (avec la circulaire DSS n° 2007-431), 2008/031,
    2009/017, 2009/035, 2009/044 ;
  - les exposés « Points cotisés artisans avant 2013 » et « Points cotisés commerçants
    avant 2013 », par son API.
- **Dépôt** : `data/reference/regimes/valeurs_point.csv`, `plafond_securite_sociale.csv`,
  `nric.yaml`, `rco_artisans.yaml` ; la fiche `assiette_rco_independants` ; les témoins
  `simulations.json` et `pages.json`, au commit 4cf6b96 et à son parent.
