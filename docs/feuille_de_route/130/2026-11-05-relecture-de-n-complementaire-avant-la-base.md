# Relecture de N : la complémentaire avant la base des libéraux

File R-N2 de la vague 9, le 5 novembre 2026 : relecture indépendante du commit ddc92fc de
la session N (action 130), de sa note `2026-11-05-complementaire-avant-la-base-des-liberaux.md`,
de la fiche `liquidation_regime_par_regime` et de son journal de veille
(`2026-11-05-action-130-complementaire-avant-la-base.yaml`). Chaque texte a été rouvert ici,
sans rien reprendre de la session ni de mémoire, dans les index du dépôt récupérés dans la
session (JORF à jour au 3 novembre 2026, LEGI au 2 novembre), par
`scripts/fetch/dila_cherche.py`. Les deux moteurs ont été lancés sur les cas de N et sur
onze cas neufs par `servi_et_refait` (`tests/outils_pont.py`), qui fait servir chaque cas au
portage et le fait refaire au moteur Python. Le seul test qui l'exigeait a été rejoué sur
les deux `departs` du commit parent, remis un instant dans la copie de travail puis
restaurés, sans commit. Rien n'a été modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict.** La règle est **conforme au droit** pour les quatre caisses, à chaque borne
lue. Chaque citation de N est exacte. Les dates de ses tests se refont à la main, et les
deux moteurs les rendent, sous `PRESOMPTIONS_DECALEES=1` aussi. Les deux tests récrits
l'ont été sur le texte, non pliés au code. **Un écart grave** : le commit fait rougir un
test du site, du niveau `complet`, que ni `-m rapide` ni `-m site` ne lancent, et que la
suite de GitHub lancera (point 4). **Un écart moyen**, antérieur à N, non déclaré : la
CAVP et la CARPIMKO servies à l'âge de la carrière longue de la base avant 2024, que leurs
statuts lus ne leur ouvraient pas (point 5). **Quatre écarts faibles** : des arrêtés non
cités, sans effet sur l'âge (point 1) ; la date du témoin, qui porte l'erreur que N
déclare, sans que sa note le dise (point 3) ; un `a_relire` de la fiche resté faux, et
aucun pour les statuts du Bulletin officiel (point 6) ; le trou de la CARPIMKO après
août 1961, déclaré dans la note seule (point 6).

## 1. Les sources, à la bonne version — conforme ; un écart faible

- **CAVOM, statuts de 2016.** Arrêté du 30 décembre 2015 : article 1er (approbation) et
  article 2 (exécution), sans date d'effet (JORFARTI000031740850, …851) ; publié le 31,
  en vigueur le 1er janvier 2016. Annexe (JORFARTI000031740853), article 14, mot pour
  mot : « La liquidation de la retraite, conditionnée à la cessation de toute activité
  professionnelle ressortissant de la caisse et au paiement à la caisse de toutes les
  cotisations et majorations exigibles, peut intervenir : « 1° À partir de 62 ans » ;
  article 23 : « Les âges de liquidation de la retraite de 62 ans et 67 ans s'appliquent
  aux adhérents nés à compter du 1er janvier 1959. Pour les générations antérieures, les
  âges d'ouverture des droits à retraite et de bénéfice du taux plein évoluent selon le
  tableau ci-dessous : GÉNÉRATION ÂGE D'OUVERTURE DES DROITS ÂGE DU TAUX PLEIN Jusqu'à
  1955 60 ans 65 ans 1956 60 ans et 6 mois 65 ans et 6 mois 1957 61 ans 66 ans 1958 61 ans
  et 6 mois 66 ans et 6 mois 1959 et suivantes 62 ans 67 ans ». Aucune condition de la
  base : conforme.
- **CAVOM, 2025 et 2026.** Arrêté du 12 décembre 2024, article 2 : « Les dispositions
  annexées au présent arrêté entrent en vigueur au 1er janvier 2025 »
  (JORFARTI000050823053). Annexe, 4° (JORFARTI000050823056) : « 1° L'âge d'ouverture des
  droits à pensions est fixé à : « a) 62 ans pour les affiliés relevant du a du 2° de
  l'article L. 643-4 du code de la sécurité sociale ; « b) 64 ans à compter de la
  génération 1968 », puis la liste, de « 60 ans pour les affiliés nés avant le 1er
  janvier 1956 » à « 63 ans et 6 mois pour les affiliés nés en 1967 », « 62 ans et 6
  mois ans » compris ; et au 3° : « l'âge auquel est demandée la liquidation de la
  retraite, qui ne peut être inférieur à l'âge fixé au 1° ». Règlement de 2026, annexe
  I, article 1er, I (JORFARTI000054435969) : les mêmes mots. La table `cavom` de
  `ages_regimes.csv` les porte. Qu'une table unique serve aussi de 2016 à 2024, quand les
  statuts disaient 62 ans « 1959 et suivantes », ne change rien : un né en 1965 n'a
  62 ans qu'en 2027. Conforme.
- **CARPIMKO, statuts de 2015.** Arrêté du 31 juillet 2015, articles 1er et 2 sans date
  d'effet (JORFARTI000031255544, …545) : publié le 2 octobre, en vigueur le 3. Annexe
  (JORFARTI000031255547) : l'article 12 quater, la table et la phrase qui la suit sont
  cités exactement. La lecture de N tient : l'article 11, 2°, a, donne le taux plein
  « A partir de 62 ans et avant 67 ans » aux nés depuis 1961 qui liquident leur base sans
  abattement, et l'article 12 l'anticipation « à partir de 62 ans et avant 67 ans » ; la
  ligne « Age prévu à l'article 11.2 (a) » est donc la ligne des 62 ans, et la phrase
  « à partir de l'âge prévu à l'article 11.1 et avant l'âge prévu à l'article 11.2 (a) »
  inverse les deux lignes. L'arrêté du 27 décembre 2023 (annexe, JORFARTI000048880643)
  le confirme en nommant la même ligne « Âge minimal pour liquider sa retraite » (citation
  exacte). Règlement de 2026, article 2 : « Pour bénéficier de la retraite
  complémentaire, les affiliés doivent avoir versé toutes les cotisations exigibles et
  avoir l'âge prévu par les dispositions des articles 3, 4 et 6 » (exact). Aucune
  condition de la base pour liquider : conforme.
- **CPRN.** Arrêté du 16 décembre 2013, article 2 : « Le présent arrêté prend effet au
  1er janvier 2014 » (JORFARTI000028387441). Annexe (JORFARTI000028387445) : la
  citation de l'article 15 est exacte, et celle de l'ancien article 14 aussi (« cette
  demande. La demande ne peut être antérieure ni au soixante-cinquième anniversaire du
  notaire, ni à la fin de son exercice », mots que l'arrêté remplace). Statuts de 2017,
  article 18 (JORFARTI000034975971) : « L'âge de l'ouverture du droit à pension de
  retraite est fixé comme suit », puis les mêmes deux alinéas, « différé de
  vingt-quatre mois » compris. Arrêté du 29 novembre 2023, article 2 : « Les dispositions
  du présent arrêté entrent en vigueur le 1er janvier 2024 » (JORFARTI000048679346) ;
  annexe, article 18 (JORFARTI000048679350), et règlement de 2026, article 4
  (JORFARTI000054435995) : « L'âge de l'ouverture du droit à pension de retraite est
  celui mentionné à l'article L. 161-17-2 du code de la sécurité sociale » (exact). Ces
  quatre textes sont les seuls de l'index qui approuvent des statuts de la section
  depuis 2014. Conforme.
- **CAVP.** Statuts de 2009, partie III, article 15 (JORFARTI000020694605) : « dès l'âge
  de 60 ans » (exact) ; arrêté du 23 juin 2011, article 15 (JORFARTI000024270214) :
  exact, phrase transitoire comprise ; règlement de 2026, article 12
  (JORFARTI000054436087) : « L'affilié peut demander à bénéficier de sa pension de
  retraite du régime complémentaire dès l'âge d'ouverture du droit à pension de retraite
  tel qu'il est fixé à l'article L. 161-17-2 » (le fragment cité est exact). L'âge de la
  CAVP est l'âge légal de la base, à chaque date depuis le 7 juin 2009 : conforme. Mais
  ce n'est pas l'âge de la carrière longue de la base (point 5).
- **La base.** L. 161-17-2 (LEGIARTI000025014605) : « soixante-deux ans pour les assurés
  nés à compter du 1er janvier 1955 » ; D. 161-2-1-9 (LEGIARTI000025089933) : « 4°
  Soixante et un ans et deux mois pour les assurés nés en 1953 » ; (LEGIARTI000047634502)
  « 9° Soixante-deux ans et neuf mois pour les assurés nés en 1963 » ; L. 161-17-2
  (LEGIARTI000053280889) : « 3° Soixante-deux ans et neuf mois, pour les assurés nés
  entre le 1er janvier 1963 et le 31 mars 1965 » et « 7° Soixante-trois ans et neuf
  mois, pour les assurés nés en 1968 ». Toutes exactes.
- **Écart faible : des arrêtés non cités, sans effet sur l'âge.** Le journal de N ne
  nomme pas : pour la CAVOM, les arrêtés du 26 décembre 2018 (JORFARTI000037883374,
  statuts généraux) et du 28 août 2020 (JORFARTI000042311285). Celui de 2020 modifie
  pourtant l'article 14 : « au troisième alinéa, après les mots : « ressortissant de la
  caisse » sont insérés les mots : « , sous réserve des dérogations prévues à l'article
  15, » » ; et son article 15 neuf (cumul) dit : « sous réserve que la pension du régime
  de base soit liquidée ». Cette réserve conditionne le cumul d'une activité, non la
  liquidation de qui cesse toute activité : sans effet sur la règle. Pour la CARPIMKO,
  les arrêtés de 2016, 2017, 2018, 2020 et 2022 (élections, statuts généraux), du 23 mai
  2019 (JORFARTI000038529117 : l'article 12, b, « A partir de cinquante-cinq ans, sans
  abattement » pour la retraite anticipée des handicapés) et du 14 novembre 2025
  (JORFARTI000052604992). Pour la CAVP, ceux de 2012, 2015, 2016, 2017, 2019, 2025 et
  surtout du 19 décembre 2023 (JORFARTI000048880592), qui récrit l'article 15 sans
  changer l'âge, mais y ajoute : « L'affilié qui bénéficie d'une liquidation anticipée
  au régime de base, dans les conditions prévues aux II, III et IV de l'article L. 643-3
  en bénéficie dans les mêmes conditions et modalités au régime complémentaire » (point
  5). Aucun ne change l'âge d'ouverture, ni ne lie la complémentaire à la base.

## 2. Les valeurs des tests, refaites à la main — conforme

Une pension prend effet au premier jour du mois qui suit l'âge ; une naissance le 10 mars
ou le 10 septembre fait tomber chaque date au premier jour d'un trimestre civil, celle de
la CAVOM et de la CARPIMKO aussi.

- CAVOM, né le 10 mars 1957, à 61 ans : 61 ans (statuts de 2016, article 23) le 10 mars
  2018, donc le 1er avril 2018 ; la base à 62 ans, le 10 mars 2019, donc le 1er avril
  2019. Conforme.
- CAVOM, né le 10 mars 1963, à 62 ans : 62 ans (statuts de 2025, « entre le 1er janvier
  1959 et le 31 décembre 1964 ») le 10 mars 2025, donc le 1er avril 2025 ; la base à
  62 ans et 9 mois, le 10 décembre 2025, donc le 1er janvier 2026. Conforme.
- CARPIMKO, né le 10 mars 1957, à 61 ans : âge minimal 60 ans et 8 mois (10 novembre
  2017), ouverte au départ demandé, le 1er avril 2018 ; la base le 1er avril 2019.
  Conforme.
- CPRN, né le 10 septembre 1953, à 61 ans : 60 ans « pour les affiliés nés avant le 1er
  janvier 1954 », ouverte au départ demandé, le 1er octobre 2014 (statuts de 2014) ; la
  base à 61 ans et 2 mois, le 10 novembre 2014, donc le 1er décembre 2014. Conforme.
- CPRN, né le 10 mars 1956, à 62 ans : la base le 1er avril 2018 ; la CPRN à 62 ans
  « différé de vingt-quatre mois », 64 ans, le 10 mars 2020, donc le 1er avril 2020,
  sous les statuts de 2017. Conforme.
- CAVP, né le 10 mars 1953 : 61 ans et 2 mois pour la CAVP comme pour la base ; rien à
  61 ans, un seul départ à 62 ans. Conforme.

## 3. Les deux moteurs — conforme ; un écart faible

- `tests/test_complementaires_liberales_a_leur_age.py`, `tests/test_sections_juridiques.py`
  et le test récrit de `tests/test_emploi_retraite.py` : 28 verts, et 28 verts sous
  `PRESOMPTIONS_DECALEES=1`, aucun sauté. Sur les deux `departs` du commit parent, le
  fichier neuf rougit comme N le dit : cinq rouges (quatre refus, la CPRN de 1956 servie
  avec la base), les deux cas de la CAVP verts. `python -m pytest -m rapide` : 4 472
  verts, 6 sautés ; `-m site` : 36 verts ; `tests/test_web.py` et
  `tests/test_estimation_du_site.py` en entier : 348 verts, un rouge (point 4).
- Les lignes du tableau de N que ses tests ne prennent pas, rejouées dans les deux
  moteurs : la CAVOM de 1955 à 60 ans, le 1er avril 2015, puis la base le 1er avril 2017
  (présumé, point 6) ; la CAVOM de 1968 à 63 ans et 9 mois, la base le 1er janvier 2032
  et la CAVOM le 1er avril 2032 ; le notaire de 1953 à 60 ans, refusé ; celui du 10 mars
  1961 à 62 ans, la base le 1er avril 2023 et la CPRN le 1er avril 2025 ; ceux de 1962 à
  62 ans et 6 mois, la CPRN comme la CARPIMKO, en un seul départ ; le pharmacien de 1950
  à 60 ans, un seul départ. Tout ce que N écrit se retrouve.
- **Le +14,46 % du témoin `cumul_notaire_cprn_2022`** se refait : la pension annuelle
  passe de 12 049,43 € à 13 791,40 €, et l'écart, 1 741,97 €, est tout entier celui de la
  CPRN. Avant : « cotisations revalorisées 137,109 € × rendement 4.12% × coefficient
  d'anticipation 0.7500 », 4 236,68 €, servie avec la base le 1er mai 2022. Après :
  146 671 € × 5,13 % × 0,85 = 6 395,58 € de 2024, servie le 1er février 2024, soit
  5 978,65 € de 2022. (5 978,65 − 4 236,68) / 12 049,43 = 14,457 %. **Écart faible** : ce
  1er février 2024 est l'erreur que N déclare lui-même (« un notaire né en 1960 ou 1961,
  parti en 2022 ou 2023, peut la demander dès le 1er janvier 2024 ») ; sa note présente
  pourtant le témoin comme ce qui « couvre ainsi la règle », sans dire qu'il en porte
  l'erreur, d'un mois.

## 4. Les deux tests récrits, et un troisième oublié — écart grave

- **`test_la_complementaire_ne_decide_pas_de_l_ouverture_de_la_base`**
  (`test_sections_juridiques.py`). L'ancien test refusait l'officier ministériel né en
  1955 à 60 ans, en 2015, sur un principe : « c'est le second [le régime de base] qui dit
  quand le droit s'ouvre ». Ce principe est démenti par les statuts de 2016 (articles 14
  et 23, point 1) ; pour 2015 même, il n'est ni démenti ni fondé, faute de statuts lus.
  N a déplacé le test en 2018, où le texte s'applique : récrit sur le texte, non plié au
  code. Le comportement de 2015 change de présomption (la CAVOM servie à 60 ans), qui est
  déclarée (point 6).
- **`test_le_notaire_liberal_n_a_pas_droit_a_sa_complementaire`**
  (`test_emploi_retraite.py`). L'ancien cas, né en 1960 et parti en 2022, supposait la
  CPRN servie au départ ; l'article 18 des statuts de 2017 l'ouvre à 64 ans. Le cas de
  1962, parti à 62 ans et 6 mois en 2024, garde l'objet du test, l'incompatibilité avec
  l'exercice libéral, sous les statuts de 2024 qui ouvrent la CPRN avec la base. Fondé.
- **Écart grave : le jumeau du site n'a pas été récrit.**
  `tests/test_web.py::test_la_complementaire_du_notaire_liberal_ne_lui_est_pas_servie`
  ouvre la page sur la même requête que le témoin (`_CUMUL_NOTAIRE_CPRN_2022` : né en
  1960, parti à 62,25 ans, notaire libéral d'août 2022 à janvier 2024) et attend « votre
  retraite complémentaire ne vous est pas servie : les statuts de votre caisse la disent
  incompatible avec l'exercice libéral du notariat ». Il est **rouge** sur ddc92fc, et
  **vert** sur les deux `departs` du commit parent : la CPRN n'étant plus servie pendant
  le cumul, la phrase ne vient plus (`non_servi` du témoin : 6 667,02 € → 0). Le test
  est du niveau `complet` (`tests/conftest.py`, `COMPLETS`), que ni `-m rapide` ni
  `-m site` ne lancent ; la suite de GitHub, si. Le droit donne raison au code, non au
  test : il pose la présomption que le jumeau Python a quittée. À récrire comme lui (une
  naissance en 1962), par la session du site : candidat. Le commentaire du témoin dans
  `scripts/construire_temoins.py` (« celle du notaire libéral, non due même sous le
  seuil ») n'est plus vrai non plus : le témoin ne couvre plus l'incompatibilité.

## 5. La carrière longue de la CAVP et de la CARPIMKO — écart moyen, antérieur à N

N tient la CAVP pour ouverte « à l'âge de la base », et c'est vrai de l'âge légal. Ce ne
l'est pas de l'âge que la carrière longue ouvre à la base. L'article 15 de 2011, lu en
entier, n'a que l'âge de L. 161-17-2 et l'inaptitude ; la clause « L'affilié qui
bénéficie d'une liquidation anticipée au régime de base [...] en bénéficie dans les
mêmes conditions et modalités au régime complémentaire » n'y entre que par l'arrêté du
19 décembre 2023. De même, la CARPIMKO n'ouvre l'âge de la carrière longue qu'à partir de
2024 (arrêté du 27 décembre 2023, article 11, 4) : de 2015 à 2023, ses articles 11, 12 et
12 quater n'en disent rien, et l'article 12 bis, d'avant 2015, n'est pas lu. Or, dans les
deux moteurs, le pharmacien, l'auxiliaire médical, l'officier ministériel et le notaire
nés le 10 mars 1957, entrés à 18 ans, partis à 60 ans en 2017, sont servis en un seul
départ, motif `carriere_longue`, complémentaire comprise. La fiche déclare la carrière
longue de la CAVOM et de la CPRN, « que leurs statuts ne nomment pas », et dit que la
CARPIMKO l'ouvre « depuis 2024 » ; elle ne dit rien de ce que le modèle sert avant, ni
de la CAVP. Le défaut n'est pas né du commit : la complémentaire suivait déjà la base.
Candidat : servir la CAVP de juillet 2011 à 2023, et la CARPIMKO de 2015 à 2023, à leur
âge propre quand la base part en carrière longue, ou le déclarer.

## 6. Ce que le texte ne tranche pas — déclaré ; deux écarts faibles

- **Déclaré** dans les approximations de la fiche : la CAVOM d'avant 2016 servie à
  60 ans « sans texte lu », la CARPIMKO d'octobre à décembre 2015 à l'âge de la base, la
  CPRN d'avant 2014 à l'âge de la base, l'ancien article 14 de la CPRN, et le passage de
  2024 de la CPRN, mesuré. Conforme. Un indice, non une preuve, appuie les 60 ans de la
  CAVOM d'avant 2016 : l'arrêté de 2015 remplace « 60 ans » par « 62 ans » à l'article
  16, et sa table garde 60 ans « Jusqu'à 1955 » ; rien n'y dit si la base était
  demandée.
- **Écart faible : l'`a_relire` de la fiche est resté faux.** Sa première entrée dit
  encore : « Restent présumées suivre leur base, sans lecture de leurs statuts sur ce
  point : la CAVOM, la CARPIMKO, la CAVP, la CARCDSF et la CPRN ». N ne l'a pas
  complétée, et n'a pas ajouté d'entrée pour les statuts qu'il laisse, ceux du Bulletin
  officiel (la CAVOM d'avant 2016, la CARPIMKO d'avant le 3 octobre 2015, la CPRN
  d'avant 2014), comme la file L-bis l'a fait pour la CARPV.
- **Écart faible : la CARPIMKO après août 1961.** Depuis 2024, l'âge minimal n'est plus
  écrit pour les nés après le 31 août 1961 ; le modèle lit l'âge de L. 161-17-2. La note
  de N le dit ; la fiche, non.

## Ce qui reste, hors de cette relecture

Candidats : le test du site du point 4 et le commentaire de son témoin ; la carrière
longue de la CAVP et de la CARPIMKO avant 2024 (point 5) ; l'`a_relire` de la fiche et
le trou de la CARPIMKO après août 1961 (point 6).
