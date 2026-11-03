# Relecture des corrections de R-M3b

File R-M3-bis de la vague 6, le 3 novembre 2026 : relecture indépendante du commit 5cf7bbc
(session M3-bis, note `2026-11-03-corrections-de-la-relecture-r-m3b.md`). Ce commit reverse
depuis 2019 la majoration pour enfants de l'Agirc-Arrco sans le coefficient d'anticipation du
défunt, et il corrige les six écarts faibles de la relecture R-M3b
(`2026-11-03-relecture-agirc-arrco-des-parents-de-trois-enfants.md`). Rien n'a été repris de
M3-bis ni de mémoire. Les six documents de la caisse ont été téléchargés le jour et leur
empreinte recalculée ; leur texte a été extrait par `pdftotext`, page par page. Chaque citation
entre « » a été cherchée par un script dans la page du fichier, apostrophes et espaces ramenés
à une forme ; celles qu'un saut de page coupe ont été lues sur les deux pages. Chaque numéro de
page a été lu au pied de la page, et chaque valeur attendue refaite à la main. Les tests ont
tourné sur le dernier `main` (5cda0b8). Rien n'a été modifié : ni règle, ni donnée, ni test, ni
fiche.

**Verdict : conforme.**

- La règle, sa portée et sa borne de date sont celles du texte.
- Chaque citation est exacte, mot pour mot, à la bonne page.
- Chaque valeur des tests se refait au centime, et l'effet de 175,30 € à 274,66 € par an
  aussi, tranche 2 de l'Arrco comprise.
- Les deux moteurs rendent ces valeurs, tests verts, sous `PRESOMPTIONS_DECALEES=1` aussi.
- Le paquet se refait à l'octet.
- Le plafond n'est pas tranché par les textes lus, et il est déclaré.
- Les six écarts faibles de R-M3b sont corrigés.

Trois écarts faibles, sans effet sur un calcul, sont au point 6. Le constat sur les 60 %, pour
la file qui le corrigera, est au point 4.

## 1. Les textes, à la version en vigueur

| Texte | Ouvert | Constat |
|---|---|---|
| Circulaire Agirc-Arrco 2020-02-DRJ du 20 janvier 2020, https://www.agirc-arrco.fr/wp-content/uploads/2021/10/2020-02-DRJ_Regime_Agirc-Arrco_Reglementation_applicable_aux_individus.pdf | sha256 524779881a0e4e377382f4b3d8ab9cf0ebd4aa21fe2eca841dd523491f4806ae, identique, 88 pages | Fiche 6 : préambule (page 1 de la fiche, 74e du fichier) ; I.1.2.1 (page 5, 78e) ; I.1.2.2, 1. (page 6, 79e). Les phrases citées sont exactes, mot pour mot. Fiche 4, II.2.2 (page 6, 55e) : les quatre phrases, mot pour mot. Fiche 4, III.1 (page 9, 58e) : mot pour mot, sauf l'appel de note « 4 » après « l'âge », que la citation omet ; la note 4 ne change rien à la phrase. Fiche 5, I.1 (page 4, 65e) : « sans abattement, à l'âge de 67 ans ». **Conforme** |
| Accord du 17 novembre 2017, « applicable au 1er janvier 2019 », https://www.agirc-arrco.fr/storage/2024/09/201809dc_ANI_du_17_novembre_2017.pdf | sha256 b8af8df7372e4f897c1ca0c4fd9bf4baaa5b706ec4737b8e51b593c5a2a4fccb, identique, 98 pages | Article 109 (page imprimée 62, 64e du fichier) : les deux phrases citées, mot pour mot. Son dernier alinéa donne la borne : « En cas de décès d'un participant avant le 1er janvier 2019, les règles applicables aux droits de réversion des conjoints survivants sont celles prévues par les Accords alors en vigueur. » Article 94 : le « 3. » et « 8 % pour 3 enfants » (page 56) ; son plafond, « cumul des plafonds en vigueur à l'Agirc et à l'Arrco » (page 57). Article 102 : les deux fragments, aux pages 59 et 60. **Conforme** |
| Circulaire Agirc-Arrco 2024-5-DRJ du 12 février 2024 et l'avenant n° 19, https://www.agirc-arrco.fr/wp-content/uploads/2024/02/CirculaireAgircArrco2024_5drj.pdf | sha256 83577e9af778c96ef6520a0ed602e75ed9e3d3521bc8d80aaf6adc2c4bf9688f, identique ; **4 pages**, et non 3 (point 6, a) | La phrase ajoutée et l'entrée en vigueur, « pour toutes les pensions de réversion liquidées à compter du 1er décembre 2023 », mot pour mot, à la 4e page. L'objet de l'avenant : les « décès d'actifs survenus avant le 1er janvier 2019 ». Le paragraphe des majorations n'est pas touché. **Conforme** |
| Accord du 5 octobre 2023, https://www.agirc-arrco.fr/storage/2023/10/ANI_Agirc-Arrco_05102023.pdf | sha256 eb336c9308712f2fda3abb9720caeca97a8d38001a82751023afec3a43a3e5d0, identique, 8 pages | Dix articles. Ni « réversion », ni « majoration », ni « 109 » n'y paraissent. **Conforme** |
| Accord du 10 mai 2019, https://www.agirc-arrco.fr/wp-content/uploads/2021/11/Accord_national_interprofessionnel_10052019.pdf, que M3-bis ne cite pas | sha256 0f239c783c1a328ba15022f27f961beabead8ab29c76346986312edaccd3f5b3, 8 pages | Huit articles : les valeurs du point, les réserves, les dotations, le pilotage tactique, les coefficients de solidarité (article 7, qui complète l'article 98), les dispositions finales. Rien sur les articles 94 et 109. Cela réduit ce que M3-bis laisse (la version consolidée non lue), sans le clore |
| Convention du 14 mars 1947, « Textes mis à jour au 1er janvier 2018 », https://www.agirc-arrco.fr/storage/2021/11/CCN_14mars1947-1.pdf | sha256 38966c272726dd11abbcc5ffa18ffb67d2731caa86ca4ce3aa94d0169568ce78, identique | Annexe I, article 6, § 1er : sa table (page imprimée 30, 31e du fichier) donne « moins 3 ans » 0,88 et « moins 3 ans 3 trimestres » 0,8425. Le § 3 a) est cité mot pour mot ; sa phrase passe de la page 30 à la page 31. Article 6 bis, 2) (pages 32 et 33) : ses trois citations, mot pour mot. La table vaut pour 2012 et 2014 : l'accord du 18 mars 2011, article 3, dit que ces coefficients « seront appliqués » ; aucun accord du recueil de 2011 à 2018 n'en change les valeurs (« coefficient d'anticipation », « d'abattement » et « 0,8425 » cherchés). L'accord du 30 octobre 2015, article 3, en écarte seulement les droits de la tranche C constitués depuis 2016, ce que dit le § 3 a). **Conforme** |
| Recueil « Accords nationaux des partenaires sociaux », https://www.agirc-arrco.fr/storage/2021/11/liste_accords_paritaires_Agirc_Arrco.pdf | sha256 0186b6b165ad2a5f5f561deb969c6a35c661dc2e1fedbfcdcaa24801f51104c1, identique, 205 pages | Accord du 9 février 1994 « relatif au régime de retraite des cadres » : article 2 à la 14e page du fichier, au pied « 16 ». Accord du 18 mars 2011 : article 1er aux pieds « 147 » et « 148 », article 3 au pied « 149 ». **Conforme** |

À la bonne date : les cas du test meurent en mai 2020, et leur réversion part le 1er juin
2020. En vigueur à cette date : l'accord de 2017 dans sa version « applicable au 1er janvier
2019 », et la circulaire du 20 janvier 2020. Aucun des deux accords de 2019 et de 2023 ne
touche aux articles 94 et 109. L'avenant n° 19 ne vise que les décès d'actifs d'avant 2019.

## 2. La règle et sa portée

- *Décès depuis le 1er janvier 2019* : le préambule de la fiche 6 le dit (« s'appliquent pour
  les décès survenus à compter du 1er janvier 2019 »), et le dernier alinéa de l'article 109
  aussi. La fiche le borne : `conjoint.deces: [2019-01-01, null]`. **Conforme.**
- *Quelle que soit la date de liquidation du défunt* : la fiche 6, I.1.2.2, 1., parle d'« un
  éventuel coefficient d'anticipation dont les droits directs ont pu être affectés ». Elle ne
  distingue aucune date de liquidation. La fiche 4, II.2.2, traite les « réversions
  d'allocataires ou d'actifs ». **Conforme.**
- *Le code* : `completer` écrit, à côté de chaque part de la majoration, la part sans le
  coefficient qui y reste. Pour cela, il divise la part par `restant` : 1 pour un régime déjà
  calculé sans le coefficient, le coefficient sinon. Ces parts passent sous le même plafond, au
  même seau. Le scénario les additionne d'un départ à l'autre. L'échéancier les mène à l'année
  du décès. `reversion` les reverse quand le paramètre `majoration_sans_anticipation` le dit,
  multipliées par la part du conjoint (« la majoration est calculée sur le montant proratisé »).
  Le JavaScript suit le Python ligne pour ligne. `seau` y vaut `null` hors des seaux, comme
  `None` en Python. **Conforme.**

## 3. Les valeurs, refaites à la main

Les valeurs de service sont lues dans `data/reference/regimes/valeurs_service_datees.csv` :

- Agirc : 0,4233 € au 1er avril 2011, 0,4352 € du 1er avril 2013 au 31 octobre 2018, 0,4378 €
  au 1er novembre 2018 ;
- Agirc-Arrco : 1,2588 € au 1er janvier 2019, 1,2714 € au 1er novembre 2019 ;
- Arrco : 1,2513 € du 1er avril 2013 au 31 octobre 2018.

Le point de l'Agirc en 2020 vaut 0,4378 × 1,2714 / 1,2588 = 0,4421822 €.

| Valeur | Refaite | Constat |
|---|---|---|
| A, sans le coefficient | 0,08 × 8 345,20 × 0,4421822 = 295,2079 € | **295,21 €, conforme** |
| A, avec | 295,2079 × 0,88 = 259,7829 € ; 0,88 : du 1er avril 2012 au 15 mars 2015, 35 mois et demi, 11,83 trimestres, 12 au trimestre supérieur, « moins 3 ans » | **259,78 €, conforme** |
| A, l'Arrco | 0,10 × 1 649,20 × 1,2714 = 209,6793 € | **209,68 €, conforme** |
| A, la retraite que lisent les 60 % | 8 345,20 × 0,4421822 × 0,88 = 3 247,29 € | **conforme** |
| B, plafond | 1 000 × 0,4352 / 0,4233 = 1 028,11 € en 2014 ; 1 000 × 0,4421822 / 0,4233 = 1 044,6071 € en 2020 | **1 044,61 €, conforme**. La caisse écrit 1 028,12 € au 1er novembre 2016 (guide n° 9, cité à la fiche `majoration_enfants_agirc_arrco`), au même point de 0,4352 : l'écart d'un centime, déclaré |
| B, avec et sans le coefficient | 0,08 × 32 693,28 × 0,4352 × 0,8425 = 958,97 €, sous le plafond ; sans le coefficient, 1 138,25 €, au-delà. 0,8425 : du 1er avril 2014 à 65 ans et 9 mois, 44 mois et demi, 14,83 trimestres, 15, « moins 3 ans 3 trimestres » ; à 65 ans et 8 mois aussi (14,5, 15) | **conforme** |
| B, avant, en 2020 | 958,97 × 0,4421822 / 0,4352 = 974,36 € | **conforme** |
| B, l'Arrco | 0,10 × 2 101,77 × 1,2714 = 267,22 € | **conforme** |
| B, la retraite des 60 % | 32 693,28 × 0,4421822 × 0,8425 = 12 179,50 € | **conforme** |
| C | 0,08 × 65 611,76 × 0,4352 × 0,8425 = 1 924,56 €, au-delà du plafond : 1 044,61 € dans les deux cas | **conforme** |
| L'autre lecture du plafond | 2 071,58 × 1,2714 / 1,2588 = 2 092,32 € ; B, l'Agirc sans plafond : 1 138,25 × 0,4421822 / 0,4352 = 1 156,51 €, et 1 156,51 + 267,22 = 1 423,73 €, sous ce plafond | **conforme**. Le plafond de 2019 se retrouve d'ailleurs : 1 000 × 0,4378 / 0,4233 + 1 000 × 1,2588 / 1,2135 = 1 034,25 + 1 037,33 = 2 071,58 € |
| Seuil de 12 851 € (fiche `reversion_agirc_arrco`) | 1 028,11 / 0,08 = 12 851,4 € | **conforme** |

Les points sont ceux que la formule affiche (8 345,20, 1 649,20, 32 693,28, 2 101,77, 65 611,76) :
la carrière du modèle, que les tests confrontent d'un moteur à l'autre.

**L'effet de 175,30 € à 274,66 € par an.** Les trois cas de M3 ont été relancés dans les deux
moteurs (`servi_et_refait`, requête `REQUETE` de `tests/test_taux_plein_a_soixante_cinq_ans.py`,
partie à 65 ans). Chacun sert bien une ligne `arrco_tranche_2` :

- 2018 : 10,77 points × 1,2513 € = 13,48 € ;
- 2019 : 12,44 × 1,2588 € = 15,66 € ;
- 2020 : 12,36 × 1,2714 € = 15,71 €.

Le gain d'un cas est la pension servie × (1 − coefficient) ; la majoration ne bouge pas. La
tranche 2 est bien exonérée : l'accord de 2011, article 1er, dit « sur les tranches A et B des
rémunérations » (page 147), et la tranche 2 du non-cadre en relève.

| Cas | Calcul | Total |
|---|---|---|
| 2018 | (3 492,55 + 13,48) × 0,05 = 174,63 + 0,67 | **175,30 €** |
| 2019 | (3 578,43 + 122,04 + 15,66) × 0,07 = 250,49 + 8,54 + 1,10 | **260,13 €** |
| 2020 | (3 214,40 + 203,15 + 15,71) × 0,08 = 257,15 + 16,25 + 1,26 | **274,66 €** |

Les pourcentages : 1 / 0,95 − 1 = 5,26 % ; 1 / 0,93 − 1 = 7,53 % ; 1 / 0,92 − 1 = 8,70 %.
**Conforme.**

## 4. Ce que le texte ne tranche pas

**Le plafond de la majoration reversée depuis 2019 d'une allocation d'avant 2019 : vraiment
non tranché.** Les textes lus n'en parlent que par deux phrases générales.

- L'accord de 2017, article 94 : le plafond est le « cumul des plafonds en vigueur à l'Agirc
  et à l'Arrco applicables à l'entrée en vigueur du présent accord ».
- La circulaire, fiche 4, II.2.2 : « Le montant du plafonnement applicable à un allocataire
  est celui en vigueur à la date d'effet de sa retraite. » ; « Ce montant s'applique
  distinctement pour les droits directs et les droits de réversion servis à un même
  allocataire. »

La fiche 6 ne dit rien du plafond (« plafon » cherché de la 74e à la 88e page). La première
phrase de la fiche 4 se lit de deux façons, selon qui est « un allocataire » :

1. **Le défunt.** Sa majoration, « applicable aux droits du participant décédé » (fiche 6,
   I.1.2.2), garde le plafond de la date d'effet de sa propre retraite. C'est la lecture du
   modèle.
2. **Le conjoint.** La réversion prend le plafond en vigueur à sa propre date d'effet, donc
   celui de l'accord de 2017 depuis 2019. Une variante de cette lecture prend le plafond de la
   date d'effet de la retraite personnelle du conjoint (« Ce montant »).

Aucune phrase lue n'écarte l'une de ces lectures. Le choix est déclaré à la fiche
`reversion_agirc_arrco` (approximation de la version `accord_2017`), et son effet est chiffré
au cas B : 1 156,51 € au lieu de 1 044,61 €. Dans la lecture 2, depuis 2019, le plafond porte
sur la somme de l'Agirc et de l'Arrco. Il vaut alors autant que les deux plafonds du défunt
réunis : 1 044,61 + 1 000 × 1,2714 / 1,2135 = 2 092,32 € en 2020. Une somme plafonnée en bloc
n'est jamais plus basse que deux parts plafonnées chacune : si le modèle se trompe, il
sous-estime. **Conforme, déclaré** ; une remarque au point 6, c.

**Les 60 % de la réversion, coefficient compris : le texte les veut sans lui.** Ce constat
est pour la file qui corrigera le modèle.

Ce que disent les textes :

- L'accord de 2017, article 109, troisième alinéa (page imprimée 62, 64e du fichier) :
  « L'allocation de réversion est calculée sans qu'il soit tenu compte des coefficients dont
  les droits du participant décédé ont pu être affectés. Toutefois, le nombre de points
  attribués au conjoint survivant ne peut dépasser celui inscrit au compte du participant
  décédé compte tenu éventuellement de l'abattement appliqué aux droits lors de la
  liquidation de la retraite de ce dernier. »
- La circulaire 2020-02-DRJ, fiche 6, I.1.2.1 (pages 5 et 6 de la fiche, 78e et 79e du
  fichier) : « L'allocation de réversion est calculée sur la base de 60 % des droits du
  participant décédé. » ; « En cas de réversion d'allocataire, l'allocation est déterminée
  sans qu'il soit tenu compte ni des coefficients d'abattement définitifs, ni des
  coefficients temporaires de solidarité ou majorants dont les droits directs du participant
  décédé ont pu être affectés. » ; « Toutefois, le nombre de points attribués au conjoint
  survivant ne peut pas dépasser celui inscrit au compte du participant décédé compte tenu
  éventuellement du coefficient d'anticipation appliqué aux droits lors de la liquidation de
  la retraite de ce dernier » ; et sa note 1 : « Il n'est pas tenu compte des coefficients
  temporaires visés aux articles 98 et 99 de l'ANI. »

Ce que cela donne. Soit P les points du défunt et c son coefficient d'anticipation. La
réversion reçoit le plus petit de 60 % × P et de c × P. Avec un coefficient d'au moins 0,60,
c'est 60 % × P. Le modèle sert 60 % × c × P.

- La borne ne joue que sous 0,60 : à la table de 1947, de « moins 7 ans 3 trimestres »
  (0,5875) à « moins 10 ans » (0,43), pour une liquidation d'avant 2019. La réversion reçoit
  alors c × P, quand le modèle sert 60 % × c × P.
- Mesuré sur les deux cas du test, en 2020 :
  - A : 0,60 × 8 345,20 × 0,4421822 = 2 214,06 €, au lieu de 0,60 × 3 247,29 = 1 948,37 €,
    soit 265,69 € de plus par an ;
  - B : 0,60 × 32 693,28 × 0,4421822 = 8 673,83 €, au lieu de 0,60 × 12 179,50 = 7 307,70 €,
    soit 1 366,13 € de plus par an ;
  - en général : 0,60 × P × (1 − c) × la valeur du point, par an.
- La fiche `reversion_agirc_arrco` déclare cet écart (approximation sans version : « les 60 %
  s'appliquent à la retraite servie, coefficient d'anticipation compris, quand l'Agirc-Arrco
  les calcule sur les points de l'assuré, sans ce coefficient, dans la limite de sa
  retraite »), mais son effet y est « non mesuré ». La correction devra citer les deux textes
  ci-dessus, la borne comprise, et partir du test (cas A et B, posés ici).
- Les coefficients temporaires de solidarité et majorants ne sont pas reversés. Aucun des deux
  moteurs n'en calcule (`grep -i solidarit` dans `src/retraite_notionnelle` et `moteur/js` :
  seulement l'allocation de solidarité du chômage) : sans objet pour le modèle aujourd'hui.

## 5. Les six écarts faibles de R-M3b

| Écart | Ce que M3-bis a fait | Constat |
|---|---|---|
| a) La tranche C depuis 2019 | Fiche `taux_plein_a_soixante_cinq_ans` : l'annexe V, préambule ; l'annexe I, article 6, § 3 a), « pages 30 et 31 », mot pour mot ; l'article 102, « il en permet le report « sans abattement » » ; la circulaire, fiche 4, III.1, « page 9 de la fiche », mot pour mot hors l'appel de note | **Corrigé** |
| b) La raison donnée pour les témoins | Dans la note de M3-bis, point 4, b), faute de pouvoir récrire celle de M3. Un relevé de `tests/temoins/simulations.json` retrouve les mêmes cinq témoins (nés en 1954 ou 1955, trois ou huit enfants, naissances déclarées), tous fonctionnaires de l'État ou de la CNRACL, avec le RAFP. 359 témoins ont un régime de l'Agirc-Arrco dans le `par_regime` de leur scénario actuel, 361 n'importe où dans leur résultat : les deux comptes, celui de M3-bis et celui de R-M3b, comptent deux choses différentes, et tous deux sont exacts | **Corrigé** |
| c) L'effet en euros | Fiche `taux_plein_a_soixante_cinq_ans`, son `effet` : « 175,30 € à 274,66 € par an », refait au point 3, tranche 2 comprise | **Corrigé** |
| d) L'arrondi | « 5,26 % à 8,70 % » aux fiches `coefficients_anticipation_agirc_arrco` (`effet`) et `taux_plein_a_soixante_cinq_ans` ; plus aucun « 5 à 8 % » ni « de 5 % à 8 % » aux fiches (`grep`) | **Corrigé** |
| e) Deux pages | Fiche `majoration_enfants_agirc_arrco` : « p. 16 », et son historique ; les pages 149 et 16 sont dans la note de M3-bis ; aucune fiche ne cite de page du recueil pour l'accord de 2011 | **Corrigé** |
| f) L'Arrco des cultes | Fiche `taux_plein_a_soixante_cinq_ans` et section `code` de celle des coefficients : l'asymétrie est dite. Vérifié dans le code : `exonereParMotif` (`moteur/js/droit/liquider.js`, ligne 3092) applique à tout régime les motifs dont `regimes` est `null`, et lit l'inaptitude sur `invalidite.REGIME_DES_SALARIES`. Le motif `taux_plein_a_soixante_cinq_ans` liste ses régimes, sans `arrco_cultes`, dans chacune de ses quatre versions | **Corrigé** |

## 6. Les écarts, par gravité

Aucun écart grave ni moyen. **Faibles**, sans effet sur une règle ni sur un calcul :

- *a) Une page* : la circulaire 2024-5-DRJ a 4 pages (`pdfinfo`), l'avenant n° 19 étant sur
  la quatrième, et non 3 comme le dit la note de M3-bis, section 1.
- *b) Un centime mal expliqué* : la note de M3-bis, point 4, c), dit que R-M3b trouve 8,55 €
  pour l'Agirc-Arrco de 2019 « aux montants arrondis ». Or 122,04 × 0,07 = 8,5428 €, soit
  8,54 € aussi, et le montant servi, 122,0354 € × 0,07 = 8,5425 €, de même. Les 8,55 € de
  R-M3b sont une erreur d'un centime, non un arrondi, et ses 259,04 € deviennent 259,03 €.
  Le chiffre de M3-bis, 260,13 €, est juste.
- *c) La déclaration du plafond* : la fiche `reversion_agirc_arrco` dit qu'« aucun texte lu ne
  dit » quel plafond prend la réversion. C'est exact, mais elle ne nomme ni la phrase qui fait
  hésiter (fiche 4, II.2.2, « un allocataire », « Ce montant »), ni ce sur quoi repose le
  choix du modèle ; la note de M3-bis dit seulement « comme il le faisait ». La question à
  poser à la caisse, par écrit : la réversion, depuis 2019, d'une allocation liquidée de 2012
  à 2018 prend-elle le plafond du défunt, régime par régime, ou celui de l'accord de 2017 en
  vigueur à sa propre date d'effet, sur la somme des régimes ?

## 7. Les deux moteurs et le paquet

Tous les tests ont tourné sur 5cda0b8, le dernier `main` :

- `python -m pytest -m rapide` : 4 280 passés, 56 sautés, 13 rouges ;
- sous `PRESOMPTIONS_DECALEES=1` : 4 081 passés, 255 sautés, les mêmes 13 rouges.

Les 13 rouges sont tous dans `test_pages_en_dossier.py`, les pages toutes faites que GitHub
refait : ce ne sont pas de vrais rouges.

Les sept fichiers qui lisent les fichiers touchés (`grep -l`) sont
`test_agirc_arrco_au_droit.py`, `test_carte.py`, `test_destinie.py`,
`test_exonerations_agirc_arrco.py`, `test_reversion.py`, `test_simulateur.py` et
`test_taux_plein_a_soixante_cinq_ans.py`. Ils donnent 757 passés et 1 sauté ; sous
`PRESOMPTIONS_DECALEES=1`, 730 passés et 28 sautés.

Les quatre cas nouveaux (`test_la_fiche_reverse_la_majoration_sans_le_coefficient` et les
trois de `test_la_majoration_reversee_depuis_2019_ne_garde_pas_le_coefficient`) passent ; les
trois derniers confrontent les deux moteurs (`droit_et_refait`). Après
`python scripts/construire_donnees.py`, `git status` est vide : le paquet de `main` est à
jour. **Conforme.**

## Ce qui reste

- **Les 60 % de la réversion** : à servir sans le coefficient d'anticipation, dans la limite
  des points abattus du défunt (point 4), le test d'abord. C'est une règle du scénario 1 : sur
  Opus, après `python scripts/veille_droit.py`.
- **Le plafond de la majoration reversée** : la réponse écrite de la caisse (point 6, c).
- **La version consolidée de l'accord de 2017** : avenants n° 1 à 18 non lus. Les accords du
  10 mai 2019 et du 5 octobre 2023, et l'avenant n° 19, ne touchent pas au paragraphe des
  majorations de l'article 109.

Sources ouvertes : listées au point 1. Dans le dépôt :
`data/reference/regimes/valeurs_service_datees.csv`, `tests/temoins/simulations.json` (par
un relevé ciblé), les fiches `reversion_agirc_arrco`, `majoration_enfants_agirc_arrco`,
`coefficients_anticipation_agirc_arrco` et `taux_plein_a_soixante_cinq_ans`, et le code des
deux jumeaux.
