# Relecture de la base des cultes au SMIC de chaque mois (file M5)

File R-M5, le 3 novembre 2026 : relecture indépendante des commits 2af6a11, e4d9994 et
cd8db07 (session M5, note `2026-11-03-base-des-cultes-au-smic-du-mois.md`). Chaque texte a
été rouvert ici, sans rien reprendre de la session ni de mémoire : les index LEGI (à jour au
2 novembre 2026, 20261102-213929) et JORF (à jour au 3 novembre 2026, 20261103-002311) de la
DILA, récupérés et interrogés texte par texte ; hors des index, les circulaires de la CAVIMAC
n° 2024/01 et n° 2025/01 et le guide « Le culte et la législation » d'Actes 6 (juin 2008),
téléchargés et lus, et l'exposé « Cultes » de la base de la Cnav, lu par son API. Rien n'a été
modifié : ni règle, ni donnée, ni test, ni fiche ; le paquet refait pour vérifier l'a été hors
commit, puis remis en l'état.

**Verdict.** **Conforme** sur chaque point décisif : les quatre articles disent la base « par
mois » ; les vingt et un relèvements sont exacts, date d'effet et montant, chacun à son texte,
et la liste est complète de 1998 à 2026 ; les six années posées à la main se refont au
centime ; les deux moteurs les rendent, avec et sans présomptions décalées ; l'Arrco des
cultes a la même assiette aux mêmes dates dans les documents de la caisse ; l'effet annoncé
(quinze témoins, de +0,11 à +4,08 € au scénario 1, +5,08 € et +0,95 % aux comptes
notionnels) se retrouve exactement ; aucun texte du JORF de 2002 à 2005 ne tranche la
garantie, que M5 a déclarée. **Aucun écart grave ni moyen. Six faibles** : la lecture « SMIC du
mois » de la rédaction de 1998, qui ne dit pas « en vigueur », n'est pas déclarée comme
lecture (point 1) ; l'identifiant cité pour le relèvement de 2011 ne porte pas sa date
(point 2) ; « les décrets de chaque 1er janvier de 2018 à 2026 » : il n'y en a pas pour 2025
(point 2) ; une citation des forfaits agricoles n'est mot pour mot que dans deux décrets sur
trois (point 7) ; l'en-tête du tableau de la circulaire n° 2025/01, qui dit le 1er janvier
2025, n'est pas relevé (point 4) ; la borne de 11 % de la garantie n'est pas écrite dans
l'article 32 (point 6). Un appui de plus, que M5 ne cite pas pour cela : le guide de 2008
montre la base suivre le relèvement du 1er mai 2008, vieillesse et complémentaire ensemble
(point 4).

## 1. Les quatre articles, à chacune de leurs rédactions

`dila_cherche.py legi --num … --diff` et `--le`, rédaction par rédaction :

| Article | Rédaction | Ce qu'elle dit de la base | Constat |
|---|---|---|---|
| R. 721-29 | LEGIARTI000006752924, 21 juin 1998 → 29 décembre 1999 | « La base forfaitaire prévue au 1° du I de l'article L. 721-3 est égale, par mois, à 169 fois le montant du salaire minimum de croissance. » | citation de M5 conforme, mot pour mot |
| R. 721-29 | LEGIARTI000006752925, 29 décembre 1999 → 26 février 2004 | « (texte inchangé) » | conforme : « mot pour mot au 29 décembre 1999 » |
| R. 721-29 | LEGIARTI000006752926, 26 février 2004 → 1er novembre 2006 | « égale, par mois, à la valeur horaire du salaire minimum de croissance en vigueur, multipliée par le nombre légal d'heures de travail mensuel en vigueur. A titre transitoire, du 1er janvier 2002 jusqu'au 30 juin 2005, cette base est augmentée de la valeur de la garantie mensuelle de rémunération la plus élevée prévue à l'article 32 de la loi n° 2000-37 du 19 janvier 2000 modifiée. » | conforme, mot pour mot |
| R. 721-30 | LEGIARTI000006752064, 065, 066, mêmes dates | les mêmes mots pour la base de la collectivité (2° du I de L. 721-3) ; 1999 « (texte inchangé) » | conforme |
| R. 382-89, R. 382-90 | LEGIARTI000006749795 et 6749796, seules rédactions, depuis le 1er novembre 2006 | les mêmes mots, transitoire compris, renvoyant à L. 382-25 | conforme ; en vigueur le 3 novembre 2026 |

Le texte de la récriture est l'article 1er, V et VI, du décret n° 2004-181 du 23 février 2004
(JORFARTI000002456069), JO du 26 février 2004, qui remplace « à 169 fois le montant du salaire
minimum de croissance » ; son article 2 est l'article d'exécution, et le décret ne dit aucune
date d'effet hors de la clause transitoire « du 1er janvier 2002 ». Le décret n° 98-490 du
17 juin 1998 (JO du 21 juin 1998, JORFARTI000001421256) porte la rédaction de 1998.

**Le nombre d'heures** : 169 par mois jusqu'au 26 février 2004 ; ensuite « le nombre légal
d'heures de travail mensuel en vigueur », 151,67, que le modèle compte 1 820 / 12 = 151,666… :
0,002 % d'écart, sous l'arrondi à l'euro déjà déclaré. De 2002 au 25 février 2004, la rédaction
en vigueur disait encore 169 heures, et le modèle en compte 151,67 sans la garantie : déclaré
par la fiche (`garantie_mensuelle_de_remuneration`, « la rédaction en vigueur en 2002 et en
2003 portait encore 169 SMIC horaires par mois »), antérieur à M5. **Conforme.**

**« En vigueur » (faible).** De 1998 à 2004, le texte dit « par mois, à 169 fois le montant du
salaire minimum de croissance », sans « en vigueur ». Le SMIC de chaque mois en est la lecture
naturelle : les textes du temps qui veulent une date fixe la nomment — « celui en vigueur au
1er janvier de l'année civile considérée » (D. 742-3, décret n° 2002-784, JORFARTI000001824475),
« en vigueur au 1er juillet » (décret n° 2002-1253, JORFARTI000002446426). Mais c'est une
lecture : l'approximation de la fiche `cultes_salaire_annuel_moyen` prête « au salaire minimum
de croissance en vigueur » à « R. 721-29 et R. 721-30, puis R. 382-89 et R. 382-90 », sans
distinguer la rédaction de 1998, et aucun document de la caisse n'est lu avant 2008 (point 4).
À déclarer, sans changer la règle.

## 2. Les relèvements du SMIC, chacun à son texte au JORF

Les vingt et un, tous rouverts (`dila_cherche.py jorf --texte`) :

| Effet | Montant lu | Texte, identifiant | Constat |
|---|---|---|---|
| 1er juillet 1998 | 40,22 F | décret n° 98-518, art. 1er, JORFARTI000001034949 | conforme |
| 1er juillet 1999 | 40,72 F | décret n° 99-546, JORFARTI000001046712 | conforme |
| 1er juillet 2000 | 42,02 F | décret n° 2000-589, JORFARTI000001965864 | conforme |
| 1er juillet 2001 | 43,72 F, « Du 1er juillet au 31 décembre 2001 inclus » | décret n° 2001-554, JORFARTI000001645920 | conforme |
| 1er juillet 2002 | 6,83 € | décret n° 2002-941, JORFARTI000002416035 | conforme |
| 1er juillet 2003 | 7,19 € | décret n° 2003-564, JORFARTI000001274126 | conforme |
| 1er juillet 2004 | 7,61 € | décret n° 2004-633, JORFARTI000002259434 | conforme |
| 1er juillet 2005 | 8,03 | décret n° 2005-719, JORFARTI000001485867 | conforme |
| 1er juillet 2006 | 8,27 | décret n° 2006-751, JORFARTI000001278723 | conforme |
| 1er juillet 2007 | 8,44 € | décret n° 2007-1052, JORFARTI000002080353 | conforme |
| 1er mai 2008 | « majoré de 2,3 % pour prendre effet au 1er mai 2008 », 8,63 € | arrêté du 25 avril 2008, JORFARTI000018730835 | conforme |
| 1er juillet 2008 | 8,71 € | décret n° 2008-617, JORFARTI000019078958 | conforme |
| 1er juillet 2009 | 8,82 € | décret n° 2009-800, JORFARTI000020793254 | conforme |
| 1er décembre 2011 | 9,19 € | arrêté du 29 novembre 2011, art. 2, JORFARTI000024874233 ; la date, « pour prendre effet au 1er décembre 2011 », est à l'art. 1er, JORFARTI000024874230 | conforme ; l'identifiant cité dit « à compter de cette date » sans la date (faible) |
| 1er juillet 2012 | 9,40 € | décret n° 2012-828, JORFARTI000026083666 | conforme |
| 1er octobre 2021 | 10,48 € | arrêté du 27 septembre 2021, JORFARTI000044126036 | conforme |
| 1er mai 2022 | 10,85 € | arrêté du 19 avril 2022, JORFARTI000045602327 | conforme |
| 1er août 2022 | 11,07 € | arrêté du 29 juillet 2022, JORFARTI000046113526 | conforme |
| 1er mai 2023 | 11,52 € | arrêté du 26 avril 2023, JORFARTI000047495827 | conforme |
| 1er novembre 2024 | 11,88 € | décret n° 2024-951, JORFARTI000050392696 | conforme |
| 1er juin 2026 | 12,31 € | arrêté du 22 mai 2026, art. 1er, JORFARTI000054126607 | conforme |

Les francs, divisés par 6,55957 à six décimales, redonnent les valeurs du fichier (6,131499 ;
6,207724 ; 6,405908 ; 6,665071). L'article 3 du décret n° 2001-554 (JORFARTI000002428309) fixe
bien « 6,67 Euro de l'heure » « A compter du 1er janvier 2002 ».

**La liste est complète.** Tous les décrets et arrêtés de l'index JORF dont le titre porte le
relèvement du SMIC, de 1998 à 2026, ont été listés : hors des vingt et un, il n'y a que les
décrets de décembre, à effet du 1er janvier. Les SMIC de janvier des années des tests, et de
2018 à 2026, se relisent au centime de `smic_horaire.csv` : 9,67 € (n° 2015-1688), 9,88 €
(n° 2017-1719), 10,03 € (n° 2018-1173), 10,15 € (n° 2019-1387), 10,25 € (n° 2020-1598), 10,57 €
(n° 2021-1741), 11,27 € (n° 2022-1608), 11,65 € (n° 2023-1216), 12,02 € (n° 2025-1228).
**Faible** : la note de M5 dit « Les décrets de chaque 1er janvier de 2018 à 2026 » ; il n'y en
a aucun pour 2025 — l'index n'a, entre le décret n° 2024-951 et le n° 2025-1228, aucun texte de
relèvement —, et les 11,88 € de janvier 2025 sont ceux du 1er novembre 2024. La valeur est
juste ; la phrase, non.

## 3. Les six années des tests, refaites à la main

Heures du mois fois SMIC du mois, sommées sur douze mois (169 heures en 1999 ; 1 820 / 12
ensuite) :

| Année | Calcul | Attendu de M5 | Refait |
|---|---|---|---|
| 1999 | 169 × (6 × 40,22 + 6 × 40,72) = 82 073,16 F ; / 6,55957 | 12 511,97 € | 12 511,97 € |
| 2007 | 1 820 / 12 × (6 × 8,27 + 6 × 8,44) = 1 820 / 12 × 100,26 | 15 206,10 € | 15 206,10 € |
| 2008 | 1 820 / 12 × (4 × 8,44 + 2 × 8,63 + 6 × 8,71) = 1 820 / 12 × 103,28 | 15 664,13 € | 15 664,13 € |
| 2016 | 1 820 × 9,67 | 17 599,40 € | 17 599,40 € |
| 2022 | 1 820 / 12 × (4 × 10,57 + 3 × 10,85 + 5 × 11,07) = 1 820 / 12 × 130,18 | 19 743,97 € | 19 743,97 € |
| 2024 | 1 820 / 12 × (10 × 11,65 + 2 × 11,88) = 1 820 / 12 × 140,26 | 21 272,77 € | 21 272,77 € |

Au SMIC de janvier : 12 434,68 €, 15 051,40 €, 15 360,80 €, 19 237,40 €, 21 203,00 € — ceux de
la note. La caisse, en 2024 : 10 × 1 767 + 2 × 1 802 = 21 274 €, 1,23 € de plus, l'arrondi
déclaré. Les autres tests récrits : la cotisation de 2000, 169 × (6 × 40,72 + 6 × 42,02) F
(décrets n° 99-546 et 2000-589) ; la CEG de 2022, 2,15 % × 19 743,97 = 424,50 € ; le plus fort
relèvement de la base, (7,19 + 7,61) / 2 / 7,19 − 1 = 2,92 % en 2004, le maximum de 1998 à 2026
(2005 : 2,76 %, 2003 : 2,64 %, 2022 : 2,63 %) ; 2022 gagne 19 743,97 / 19 237,40 − 1 = 2,6 %.
**Conforme.**

## 4. La pratique de la caisse et l'Arrco des cultes

- **Circulaire n° 2024/01 du 10 janvier 2024** (PDF de cavimac.fr, trois pages) : « A compter
  des échéances des 10 et 15 février 2024, les assiettes forfaitaires respectives de calcul des
  cotisations mensuelles d'assurance maladie – maternité – invalidité, vieillesse et retraite
  complémentaire obligatoire des cultes [...] sont modifiées [...] afin de tenir compte du
  relèvement du montant brut du salaire minimum interprofessionnel de croissance (SMIC) [...]
  (montant mensuel arrondi à 1 767 €) » ; tableau « au titre du mois de janvier 2024 ». La
  citation de M5 est conforme. L'assiette de la « RCO », « Tous cultes - taux de base », est
  1 767, celle de la vieillesse.
- **Circulaire n° 2025/01 du 14 janvier 2025** : « A compter du 1er novembre 2024, le montant
  brut du [SMIC] [...] est porté à 1 802 € mensuels (augmentation de 2%). A la suite de cette
  revalorisation du SMIC, les assiettes forfaitaires respectives des cotisations mensuelles
  d'assurance maladie – maternité – invalidité, vieillesse et retraite complémentaire
  obligatoire des cultes [...] sont modifiées à compter de l'échéance du 15 décembre 2024 » ;
  RCO à 1 802 comme la vieillesse. Citation conforme. **Faible** : le PDF servi ce jour a une
  couche de texte, que `pdftotext` lit (M5 le dit « une image ») ; et le tableau de sa page 2
  s'intitule « Cotisations sociales mensuelles applicables à compter du 1er janvier 2025 »,
  ce que la note ne relève pas. Le résumé (« applicables à compter du 1er novembre 2024
  (échéance au 15 décembre 2024) ») et le corps tranchent pour novembre, comme M5 le lit.
- **Guide d'Actes 6, juin 2008** (cité par la fiche `cultes_retraite_complementaire` pour ses
  taux) : « sur la base forfaitaire du SMIC arrondie à l'euro près : 1 309 € à compter du
  1er mai 2008 », et la même base de 1 309,00 pour l'« Assurance vieillesse CAVIMAC » et la
  « Retraite complémentaire ». 8,63 × 151,67 = 1 308,91 : la base suivait le relèvement du
  1er mai 2008, vieillesse et complémentaire ensemble. Le plus ancien appui de la règle, de
  seconde main, que M5 ne cite pas pour elle.
- **L'exposé « Cultes » de la Cnav** (cotisation_salaire_type_activite_culte_ex, modifié le
  24 octobre 2025) : « sur une base forfaitaire mensuelle égale au Smic multiplié par le
  nombre légal d'heures de travail en vigueur ». Conforme.
- **L'Arrco des cultes, au texte** : aucun texte légal ne fixe son assiette — L. 921-1, étendu
  par l'article 75, VII, de la loi n° 2005-1579, affilie sans dire d'assiette —, et l'acte de
  l'Arrco qui l'aurait fixée n'est lu ni par M5 ni ici : **non vérifié, faute de texte**. La
  même assiette, aux mêmes dates, se lit dans les deux circulaires et le guide de 2008 ; le
  drapeau `smic_du_mois` est posé sur les six périodes d'`arrco_cultes.yaml` (2006 à
  aujourd'hui). Conforme à ce qui se lit.

## 5. Les deux moteurs

Sur cd8db07, le dernier commit de M5, avec son paquet :

- `node --test tests/js/cultes-smic-du-mois.test.js tests/js/moteur.test.js` : 53 sur 53 ; de
  même sous `PRESOMPTIONS_DECALEES=1`.
- `python -m pytest tests/test_cultes_smic_du_mois.py tests/test_cultes.py
  tests/test_cultes_au_droit.py tests/test_contributions_equilibre.py` : 33 verts ; de même
  sous `PRESOMPTIONS_DECALEES=1` ; `tests/test_simulateur.py -k culte` : 2 verts, de même.
- Les tests portent les valeurs posées à la main du point 3, non des valeurs lues du code ;
  les deux moteurs suivent le drapeau dans chacun des lecteurs du forfait — le salaire au
  compte (`assiette_de_reference`), l'acquisition (`acquerir`), le compte notionnel
  (`compte`), le forfait des contributions d'équilibre — ; les autres lecteurs du SMIC de
  janvier, ouverts un à un dans le Python, servent d'autres règles — les forfaits agricoles,
  l'AVI, la CNAVPL, les micro-entrepreneurs, la réversion, la seconde pension, le cumul, la
  validation des trimestres —, aucune la base des cultes. La moyenne des mois est
  jumelle : le Python trie les relèvements, le JavaScript non, sans effet, chaque mois ne
  prenant que le sien. **Conforme.**

## 6. La garantie de 2002 au 30 juin 2005

Cherchée dans l'index JORF de 2001 à 2006 : « garantie mensuelle » près de « cultes » (le seul
décret n° 2004-181) ; « ministres des cultes » de 2002 à 2005 (décrets n° 2003-1376, 2004-181,
2004-182 et son rectificatif, loi n° 2005-1579, art. 75) ; « CAVIMAC » (listes d'aptitude,
arrêtés des acomptes et des compensations) ; « 169 fois » (décret n° 2002-784 pour
l'assurance volontaire, n° 2002-1253 pour R. 381-3 et R. 742-14, et des textes étrangers aux
cultes). L'article 66 de la loi n° 2001-1246 (JORFARTI000001620575) ne parle que d'une base
« forfaitaire » pour la maladie (L. 381-17), sans montant ni garantie ; son III : « Les
dispositions du I s'appliquent à compter du 1er janvier 2002 ». Le décret n° 2004-182 n'en dit
rien. **Aucun texte ne tranche** entre la base relevée jusqu'à la garantie et la garantie
ajoutée ; M5 l'a déclaré (fiche, `sources.a_relire`, limites). **Conforme.**

**Faible** : la fiche et la note bornent l'écart à 11 % (2 028 / 1 820 − 1), la garantie étant
« au plus le SMIC de cent soixante-neuf heures ». L'article 32 de la loi n° 2000-37
(JORFARTI000001248766) ne l'écrit pas ainsi : la garantie est le SMIC « en vigueur à la date
de la réduction » fois les heures, « dans la limite de cent soixante-neuf heures », puis
« revalorisé au 1er juillet en fonction de l'évolution de l'indice des prix [...] et de la
moitié de l'augmentation du pouvoir d'achat du salaire mensuel de base ouvrier ». La borne
est plausible, non écrite ; et l'`effet` de la fiche (« jusqu'à 11 % de moins ») ne rappelle
pas la lecture littérale, que ses `conditions` disent près du double.

## 7. L'effet, et un témoin refait

- **Les témoins** : l'écart entre e4d9994^ et e4d9994 touche quinze témoins, tous des cultes.
  Au scénario 1, douze bougent, de +0,11 € (`statut_membre_congregation_1965`, +0,011 %) à
  +4,08 € (`statut_ministre_du_culte_1955`) ; +0,77 % pour `cultes_taux_minore` (323,85 € à
  326,34 €) ; trois ne bougent pas. Aux comptes notionnels : +5,08 € au plus
  (`statut_ministre_du_culte`, `notionnel_prospectif_employeur`), +0,95 % au plus
  (`statut_ministre_du_culte_1945`, `notionnel_retroactif_employeur`) ; aucune baisse.
  **Conforme**, chiffre pour chiffre.
- **Le témoin `statut_ministre_du_culte_1955`**, né en 1955, ministre de 21 à 64 ans, parti
  en 2019, refait en ordre de grandeur. L'Arrco, de 2006 à 2018 : la hausse de la base de
  chaque année, 1,49 % (2006), 1,03 %, 1,98 %, 0,63 %, 0, 0,18 % (2011), 0,98 % (2012), puis
  rien jusqu'en 2018, en moyenne 6,28 / 13 = 0,48 % ; le témoin rend 1 115,04 € à 1 120,31 €
  par an, +0,47 %. La CAVIMAC : la fraction d'après 1997 prend la moyenne de 1998 à 2018,
  21,04 / 21 = 1,0 % (un peu moins, pondérée par les bases revalorisées), sur un peu moins de
  la moitié de la pension (84 trimestres sur 172, l'autre fraction gardant ses règles) : de
  l'ordre de 0,5 % ; le témoin rend 9 142,01 € à 9 185,74 €, +0,48 %. Ensemble,
  (1 115,04 × 0,47 % + 9 142,01 × 0,48 %) / 12 ≈ 4,1 € par mois : les +4,08 € annoncés.
  **Conforme.**
- **La classe, pas le cas (faible)** : M5 cite pour les forfaits agricoles « le montant du
  salaire minimum de croissance en vigueur au 1er janvier de l'année considérée » (décrets
  n° 90-498, 94-690 et 2001-584). Mot pour mot dans les deux premiers (JORFARTI000001735045,
  JORFARTI000002131575) ; le n° 2001-584 dit « celui en vigueur au 1er janvier de l'année au
  titre de laquelle les cotisations sont dues » (JORFARTI000001260750). Même sens ; la
  conclusion — le SMIC de janvier y est le bon — tient.

## 8. Le paquet

Sur le dernier main (6db5939), `python scripts/construire_donnees.py` change deux lignes de
`moteur/donnees.json`, et aucune des cultes : les certifications `durees_echelon_duree`
(8 626 à 8 639 valeurs) et `durees_echelon_rang` (14 506 à 14 521), de l'action 158
(B2-ter), qui ne les a pas refaites. La part des cultes y est, au commit comme à la
construction : la liste `smic_horaire_releves`, vingt et un relèvements, du 1er juillet 1998
(6,131499) au 1er juin 2026 (12,31), et `smic_du_mois` sur les périodes. Copie remise propre
(`git checkout -- .`). **Conforme.**

## Ce qui reste, pour la session qui reprend les cultes

Rien ne bloque. Six retouches de la fiche `cultes_salaire_annuel_moyen` et de la note,
qu'aucun chiffre ne suit : déclarer comme lecture le SMIC du mois de 1998 à 2004 (point 1) ;
citer l'article 1er de l'arrêté du 29 novembre 2011 pour sa date (point 2) ; dire que 2025 n'a
pas de décret de janvier (point 2) ; relever l'en-tête du tableau de la circulaire n° 2025/01
(point 4) ; dire la borne de 11 % plausible et non écrite, et l'autre lecture dans l'`effet`
(point 6) ; citer le n° 2001-584 dans ses mots (point 7). Le guide de 2008 peut appuyer la
règle dans la fiche (point 4). L'acte de l'Arrco qui fixe l'assiette des cultes reste à lire.
