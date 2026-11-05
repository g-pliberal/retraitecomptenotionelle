# Relecture de N : la CRPNPAC à cinquante ans, et le régime général du navigant (file R-N)

File R-N, le 5 novembre 2026 : relecture indépendante du commit 1464c06 de la session N,
note `2026-11-05-crpnpac-et-regime-general.md`, et de son journal de veille. Chaque texte
a été rouvert ici, sans rien reprendre de la session ni de mémoire : l'index LEGI du
dépôt, récupéré dans la session (à jour de l'incrément du 2 novembre 2026,
20261102-213929), interrogé par `scripts/fetch/dila_cherche.py`. Les deux moteurs ont été
lancés sur les cas de N et sur sept cas neufs, par `servi_et_refait`
(`tests/outils_pont.py`), qui fait servir chaque cas au portage et le fait refaire au
moteur Python, et le test de N sur le commit parent, dans une copie de travail à part.
Rien n'a été modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict.** La correction est **conforme**. Les citations sur lesquelles elle repose
sont exactes, et les dates se refont à la main : la CRPNPAC le 1er mars 2019 (ou le 1er mars 2014),
le régime général le 1er décembre 2026. Les deux moteurs les rendent, sous
`PRESOMPTIONS_DECALEES=1` aussi. Le test a été rouge sans la correction (trois rouges, le
cas de 63 ans vert), et la correction ne touche que les carrières qui ont la CRPNPAC. La
carrière longue du navigant reste servie. **Écarts** : un moyen, sur ce que N affirme
hors de ce qu'il corrige : de 1995 à 2011, la CRPNPAC ne s'ouvrait pas seulement à
cinquante ans. R. 426-15-1 l'ouvrait par anticipation dès quarante-cinq ans, et avant 1995
aussi (point 5). Le modèle refuse ces départs : c'est un défaut candidat, antérieur à N.
Six écarts faibles : une citation qui ajoute un mot au texte, et une rédaction close dite
en vigueur (point 1) ; une « même phrase » qui ne l'est qu'en substance (point 1) ; la
condition d'annuités, abaissée de 2012 à 2019 par le décret n° 2011-1500, non lue (point
2) ; la règle de date de la CRPNPAC, non citée (point 2) ; la carrière longue, citée dans
la seule rédaction de 2012 (point 1) ; « aucun témoin ne bouge », vrai mais sans portée,
puisque aucun témoin n'a de navigant (point 4).

## 1. Les sources, à la bonne version — conforme, trois écarts faibles

- **R. 426-11 du code de l'aviation civile, ses cinq rédactions** (LEGIARTI000006845205 de
  1984, …206 de 1995, LEGIARTI000023049284 de 2010, LEGIARTI000024795153 de 2012,
  LEGIARTI000044496243 de 2021), toutes rouvertes. La citation de la rédaction de 2012 est
  exacte mot pour mot : « I.-Une pension de retraite est servie à l'affilié qui demande la
  liquidation de ses droits à pension, dans les conditions précisées aux articles
  suivants, dès lors qu'il réunit cumulativement à la date d'effet de la pension les
  conditions suivantes : 1° Avoir atteint l'âge de cinquante ans ; 2° Justifier de vingt
  annuités […] ». La rédaction de 2021 a la même phrase. Aucune des cinq ne nomme le régime
  général, la sécurité sociale, L. 351-1 ni L. 161-17-2 : conforme.
- **R. 6527-21 du code des transports** (LEGIARTI000048325100, depuis le 1er novembre
  2023) : mêmes conditions, 1° et 2°, mais pas « même phrase », comme le dit la note. Le
  texte renvoie « dans les conditions prévues par les articles R. 6527-22, R. 6527-27,
  R. 6527-49 et R. 6527-50 », et à R. 6527-28 et R. 6527-23 au lieu de R. 426-13 et de
  R. 426-12. **Écart faible**, de forme : la substance est la même.
- **R. 426-11-1** (LEGIARTI000006845207, du 1er juillet 1995 au 1er janvier 2012) :
  « Avoir atteint l'âge de cinquante ans », exact. Mais l'article fixe les conditions du
  droit « à taux plein » (« Le droit à pension à taux plein d'un affilié est ouvert aux
  conditions suivantes »), pas l'âge où la CRPNPAC s'ouvre : voir le point 5.
- **R. 426-16-1** (LEGIARTI000036880164, du 7 mai 2018 au 1er novembre 2023). La note le
  cite exactement : « Pour la période de jouissance comprise entre l'âge auquel l'affilié
  aura atteint le nombre d'annuités nécessaires pour l'ouverture du droit à pension, et ce
  au plus tôt à l'âge mentionné au 1° du A du II de l'article R. 426-11, et l'âge
  mentionné à l'article L. 161-17-2 du code de la sécurité sociale, la pension mensuelle
  est assortie d'une majoration ». Mais le docstring du test et la fiche
  `liquidation_regime_par_regime` l'abrègent en « l'âge [...] d'ouverture du droit à
  pension », et le « d' » n'est pas dans le texte, qui dit « pour l'ouverture ». Le test
  dit aussi la rédaction en vigueur « depuis le 7 mai 2018 », alors qu'elle se clôt le
  1er novembre 2023. **Écart faible** : le sens est gardé, la lettre ne l'est pas. Que
  cette majoration courre jusqu'à l'âge de L. 161-17-2 appuie bien la conclusion : la
  CRPNPAC est servie avant que le régime général ne s'ouvre.
- **L. 351-1** (LEGIARTI000023035688) : « L'assurance vieillesse garantit une pension de
  retraite à l'assuré qui en demande la liquidation à partir de l'âge mentionné à
  l'article L. 161-17-2 », exact. **L. 161-17-2**. Dans la rédaction LEGIARTI000025014605
  (du 23 décembre 2011 au 1er septembre 2023), « fixé à soixante-deux ans pour les assurés
  nés à compter du 1er janvier 1955 » est exact. Dans la rédaction LEGIARTI000053280889
  (depuis le 31 décembre 2025), « 3° Soixante-deux ans et neuf mois, pour les assurés nés
  entre le 1 er janvier 1963 et le 31 mars 1965 » est exact, comme son application « aux
  pensions prenant effet à compter du 1 er septembre 2026 » (VI de l'article 105 de la loi
  n° 2025-1403). **D. 161-2-1-9** (LEGIARTI000047634502, depuis le 1er septembre 2023) :
  « 10° Soixante-trois ans pour les assurés nés en 1964 », exact.
- **Les voies d'avant l'âge légal.** La carrière longue (D. 351-1-1, LEGIARTI000026139949,
  du 1er novembre 2012 au 1er septembre 2023) : la citation des « assurés nés à compter du
  1er janvier 1960 : A cinquante-huit ans […] ayant débuté leur activité avant l'âge de
  seize ans » est exacte. Le handicap : L. 351-1-3 (LEGIARTI000028498841), « atteints
  d'une incapacité permanente d'au moins 50 % », et D. 351-1-5 (LEGIARTI000030058836),
  « A cinquante-cinq ans », sont exacts. L. 351-1-4 (LEGIARTI000035640851) porte bien sur
  l'incapacité permanente d'origine professionnelle. L. 4163-7 du code du travail, 3°
  (LEGIARTI000035631174), dit « un départ en retraite avant l'âge légal de départ en
  retraite de droit commun ». L. 351-6-1 (LEGIARTI000037063352) porte sur la majoration du
  compte professionnel de prévention : conformes. Mais la note ne cite D. 351-1-1 que dans
  sa rédaction de 2012 à 2023, quand le régime général du cas s'ouvre en 2026. J'ai ouvert
  les trois rédactions suivantes : LEGIARTI000047634571 (du 1er septembre 2023 au
  1er janvier 2026), LEGIARTI000053356023 (au 1er septembre 2026) et LEGIARTI000054059621
  (depuis). Toutes demandent au plus tard d'avoir « débuté leur activité avant l'âge de
  vingt-et-un ans » (4°). Le navigant du cas, entré à vingt-deux ans, n'y a droit à
  aucune date : la conclusion tient. **Écart faible** : une citation incomplète, qui ne
  change pas la conclusion.

## 2. Les valeurs attendues, refaites à la main — conformes, deux écarts faibles

- **Le régime général.** 10 février 1964 + 62 ans = 10 février 2026 ; + 9 mois =
  10 novembre 2026. La date d'entrée en jouissance est « nécessairement le premier jour
  d'un mois » (R. 351-37, LEGIARTI000054060160, depuis le 1er novembre 2026), et l'âge
  doit être atteint (L. 351-1) : le 1er décembre 2026. Cette date suit le 1er septembre
  2026, et la rédaction LEGIARTI000053280889 la régit. Sous l'ancienne règle, 63 ans
  (D. 161-2-1-9, 10°) mène au 10 février 2027, donc au 1er mars 2027, qui tombe lui aussi
  sous la rédaction de 2026 : le 1er décembre 2026 est bien la première date. Conforme.
- **La CRPNPAC.** Cinquante-cinq ans le 10 février 2019, cinquante ans le 10 février 2014.
  La règle de date de la caisse n'est pas citée par la note, qui applique celle de toute
  pension. Je l'ai lue : « l'entrée en jouissance d'une pension pour laquelle un droit est
  ouvert prend effet le premier jour du mois suivant la réception de la demande »
  (R. 426-15-4, LEGIARTI000006845227, du 1er juillet 1995 au 1er novembre 2023). Les
  conditions de R. 426-11 s'apprécient « à la date d'effet de la pension ». Le premier
  mois où le navigant a l'âge demandé est donc le 1er mars 2019 (ou le 1er mars 2014) :
  même résultat. **Écart faible** : la source de la date manque à la note.
- **Les annuités.** De vingt-deux à cinquante-cinq ans, 33 annuités ; à cinquante ans, 28.
  La note les compare à vingt. Mais le décret n° 2011-1500 du 10 novembre 2011, article 26,
  I (LEGIARTI000024779267, du 1er janvier 2012 au 16 décembre 2021), déroge au 2° du I de
  R. 426-11 « pour les pensions prenant effet entre le 1er janvier 2012 et le
  31 décembre 2019 » : « 3° Du 1er janvier 2014 au 31 décembre 2014, à 17 annuités » ;
  « 8° Du 1er janvier 2019 au 31 décembre 2019, à 19,5 annuités ». 28 ≥ 17 et 33 ≥ 19,5 :
  les dates ne changent pas. Le défaut candidat des « vingt annuités » (le navigant de
  quinze annuités en 2019) tient toujours, puisque 15 < 19,5. Mais il doit porter ce
  barème transitoire. **Écart faible** : un texte non lu, sans effet sur le cas.

## 3. Les deux moteurs — conformes

- `tests/test_ouverture_des_navigants.py` : quatre verts, normaux et sous
  `PRESOMPTIONS_DECALEES=1`. Le même fichier lancé sur le commit parent (1464c06^, copie
  de travail à part, son `src/` en tête du chemin) donne trois rouges (55 et 50 ans : « []
  == [...] » ; le jumeau : les régimes du premier départ) et le cas de 63 ans vert. Les
  rouges sont ceux que la note annonce.
- **Avant et après, refaits.** Avant, le cas de 55 ans au parent : un seul départ ; régime
  général 10 469,57 (SR 36 017,44 × 37,5 % × 131/169) ; Agirc 4 567,74, Arrco 2 353,51,
  Agirc-Arrco 40,80, au coefficient 0,43. Après, au commit : CRPNPAC 33 677,96 le 1er mars
  2019 ; régime général 12 715,13 € de 2026, soit 10 768,88 € de 2019 (SR 41 906,17 ×
  39,375 % × 131/170) le 1er décembre 2026 ; Agirc 8 522,75, Arrco 4 391,31, Agirc-Arrco
  76,13, au coefficient 0,8175. Tous ces montants sont ceux de la note. Le taux de 39,375 %,
  à la main : de 62 ans et 9 mois à 67 ans, il manque 17 trimestres, moins que les
  39 qui manquent à la durée (170 − 131) ; 50 % − 17 × 0,625 % = 39,375 %.
- **Ce que la correction emporte.** `SANS_LEUR_BASE` ne sert qu'à `departs_et_demandes`
  (`departs.py`, l. 429 ; `departs.js`, l. 407). Seules la CARPV et la CAVEC y étaient,
  et leur traitement ne change pas. La CRPNPAC, de l'étage `complementaire`
  (`data/reference/regimes/crpnpac.yaml`), devient une unité à elle. Avant, la seule
  unité du navigant, le régime général, s'ouvrait après le départ déclaré. Le modèle
  rendait alors le départ unique (`if all(ouverture > declare …)`, `departs.py`), et le
  régime général était servi à 55 ans. Seules les carrières qui ont la CRPNPAC bougent.
- **La carrière longue, gardée.** Quatre cas neufs, né le 10 février 1964, dans les deux
  moteurs. Début à 17 ans, départ à 60 ans : un seul départ, le régime général compris,
  171/171 trimestres. C'est le 2° de D. 351-1-1 en vigueur au 1er mars 2024
  (LEGIARTI000047634571 : « A soixante ans pour les assurés qui ont débuté leur activité
  avant l'âge de dix-huit ans »). Début à 16 ans, départ à 59 ans : la CRPNPAC le 1er mars
  2023, le régime général le 1er mars 2024, à 60 ans, par le même 2°. Début à 22 ans,
  départ à 60 ans : régime général le 1er décembre 2026. Début à 17 ans, départ à 55 ans :
  régime général le 1er décembre 2026, car la durée cotisée au départ (151 trimestres)
  n'atteint pas celle qui est requise. Ce dernier cas suit la convention déclarée du
  modèle, qui ne projette pas de cotisations après le départ. La durée requise (171 au
  1er mars 2024, selon le modèle) n'a pas été relue ici dans L. 161-17-3. Les cas du
  début à 17 et à 22 ans, avec un départ à 60 ans, refaits sous
  `PRESOMPTIONS_DECALEES=1`, rendent les mêmes dates.

## 4. « Aucun témoin ne bouge » — vrai, mais sans portée (écart faible)

`python scripts/regenerer.py --verifier`, lancé au commit : inventaire, régimes, paquet,
accueil, témoins, chiffrage, tableaux, pages, prose et conservation « à jour » ; seul le
tableau de bord est périmé, ce que GitHub refait. Les témoins ne bougent donc pas. Mais
aucun témoin de `tests/temoins/` ne contient « personnel_navigant » ni « crpnpac » : rien
n'y passait par la CRPNPAC, et l'affirmation ne prouve rien sur la règle. Le chemin
corrigé n'est confronté entre les deux moteurs que par le nouveau test, au moyen de
`servi_et_refait`. Cela suffit à la confrontation, mais la note aurait dû dire qu'aucun
témoin ne couvre ce chemin. **Écart faible.**

## 5. Ce que le texte ne tranche pas — un écart moyen, le reste déclaré

- **L'âge de la CRPNPAC avant 2012 (écart moyen).** La note et la fiche écrivent : « De
  1995 à 2011 : « Avoir atteint l'âge de cinquante ans » (R. 426-11-1) ». Elles déclarent
  aussi l'article d'avant 1995 « non relu ». Les deux articles sont dans l'index.
  R. 426-15-1, rédaction de 1995 (LEGIARTI000006845222, du 1er juillet 1995 au
  1er janvier 2012) : « Le droit à pension peut être ouvert par anticipation : a) Pour les
  pensions à taux plein, postérieurement au quarante-cinquième anniversaire, avec
  application des coefficients de minoration prévus à l'article R. 426-18 ; b) Pour les
  pensions proportionnelles […] postérieurement au cinquantième anniversaire ».
  R. 426-18, rédaction de 1995 (LEGIARTI000006845237), donne les coefficients : « 45 ans /
  0,65 […] 49 ans / 0,95 ». R. 426-15-1, rédaction de 1984 (LEGIARTI000006845221, au
  1er juillet 1995) : « L'entrée en jouissance de la pension prévue à l'article R. 426-11 ne
  peut être antérieure à la date à laquelle l'intéressé a atteint l'âge de cinquante ans.
  Toutefois, l'entrée en jouissance prend effet immédiatement lorsque la cessation
  d'activité est postérieure à l'âge de quarante-cinq ans accomplis, pour l'affilié qui
  compte vingt-cinq annuités ». Le modèle, lui, ouvre la CRPNPAC à cinquante ans à toute
  date. Né en 1957, entré à vingt ans et parti à 48 ans (2005), le navigant est refusé
  (`non_ouverte`) ; né en 1940, parti à 47 ans (1987), de même. Les textes lui ouvraient
  la CRPNPAC, sous minoration. C'est un défaut candidat, antérieur à N, à inscrire. La
  séparation d'avec le régime général, que N applique à toute date, n'en est pas
  affectée : à 45 comme à 50 ans, la CRPNPAC s'ouvre avant le régime général. Le
  R. 426-16-1 de 1990 à 1995 (LEGIARTI000006845229) parle déjà d'une « période de
  jouissance comprise entre cinquante et soixante ans ». La déclaration « non relu » est
  levée par la présente note. La phrase de la note et de la fiche sur 1995 à 2011 est
  incomplète.
- **L'Agirc-Arrco, déclarée : conforme, avec une précision.** « À tort » est confirmé pour
  la complémentaire servie à 55 ans en mars 2019. L'accord du 17 novembre 2017, article
  84, 2, est cité par la fiche `coefficients_anticipation_agirc_arrco` (lue le
  3 novembre 2026, hors de LEGI, non rouverte ici). Il ouvre l'anticipation « au plus tôt
  10 ans avant » l'âge du 1° de L. 351-8. Cet âge est celui de L. 161-17-2 « augmenté de
  cinq années » (L. 351-8, LEGIARTI000028498855, rouvert) : 62 + 5 = 67 ans, donc 57 ans
  au plus tôt. Mais le même accord ouvre la complémentaire seule dès 57 ans, en 2021, au
  coefficient de 0,43. Le modèle ne la sert qu'avec la base, le 1er décembre 2026. La
  fiche déclare déjà cet écart : l'anticipation « n'est jamais servie ». N dit
  l'Agirc-Arrco « supposée » liée au régime général : sa déclaration est juste, mais
  devrait renvoyer à cet écart déclaré.
- **Les vingt annuités** : déclarées en défaut candidat ; leur barème de 2012 à 2019
  manque (point 2). **Le compte professionnel de prévention** : déclaré, et sans objet
  pour le cas. **Le cas type** (`ouvrir.age_ouverture_droit` rend cinquante ans au
  navigant) : déclaré, non instruit, et le paquet n'en bouge pas (point 4).

## Ce que la relecture laisse

- Le défaut candidat de l'âge d'avant 2012 : la CRPNPAC par anticipation dès 45 ans, sous
  les coefficients de R. 426-18 (1995 à 2011), et dès 45 ans avec vingt-cinq annuités
  (1984 à 1995). À inscrire avec celui des vingt annuités, qui doit porter l'article 26 du
  décret n° 2011-1500.
- À reprendre dans la fiche `liquidation_regime_par_regime`, par une session qui y
  travaille : la citation de R. 426-16-1 à la lettre ; la phrase sur 1995 à 2011 ; les
  rédactions de D. 351-1-1 depuis 2023 ; R. 426-15-4, pour la date ; le renvoi de
  l'Agirc-Arrco à l'écart de la fiche `coefficients_anticipation_agirc_arrco`.
