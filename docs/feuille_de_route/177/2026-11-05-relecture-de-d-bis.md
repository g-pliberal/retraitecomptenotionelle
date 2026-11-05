# Relecture de D-bis : le plafond de la caisse et la présomption de 2012 à 2018, conformes ; la baisse de 63,40 % vient du texte

File R-D-bis, vague 7, le 5 novembre 2026, sur Opus. C'est une relecture indépendante des
commits 43cfa28, 5940f86, 18af62f et ca2cb5f (file D-bis, action 177) et de leur note
`2026-11-05-corrections-de-la-relecture-r-d.md`, au regard de la relecture qu'ils corrigent
(`2026-11-05-relecture-independant-de-mayotte.md`). Lecture seule : aucune règle, aucune
donnée, aucun test touchés. `veille_droit.py` lancé. Les index LEGI et JORF de la DILA ont
été récupérés dans la session ; LEGI est à jour au 4 novembre 2026, JORF au 3 novembre.
Chaque valeur a été refaite à la main, puis demandée aux deux moteurs.

**Verdict : conforme. Aucun écart grave ni moyen, quatre écarts faibles.** Les citations
sont exactes. Le plafond de la caisse est appliqué dans sa période et sur la bonne
assiette. Les deux moteurs rendent chaque valeur au centime. Les cinq témoins bougent pour
les seules raisons que la note donne. La baisse de 63,40 % du témoin né en 1955 se refait
au centime ; elle découle aux trois quarts du plafond que l'article 28-2 impose depuis 2012.

## 1. Les sources, rouvertes : citations exactes

- **Ordonnance n° 96-1122, article 28-2, I, 1°** (LEGIARTI000025018560, du 1er janvier 2012
  au 1er décembre 2024). Le texte dit : « dans la limite du plafond prévu au deuxième
  alinéa du I de l'article 28-1, qui sont dues par tout employeur […] et par tout assuré,
  ainsi que par les travailleurs indépendants agricoles et non agricoles ». La note et la
  fiche le citent exactement. Le II ajoute une « cotisation forfaitaire minimale »,
  « fixé[e] par décret » (§ 6, d).
- **Article 28-1, I**, quatre rédactions (LEGIARTI000025018554, 025023101, 031324363,
  051284545). On y lit : « Il est créé un plafond de cotisations de sécurité sociale à
  Mayotte. […] Son montant, calculé selon des règles prévues par décret, est arrêté par le
  ministre chargé de la sécurité sociale. » La citation est exacte.
- **Décret n° 2011-2085, article 4-2, I** (LEGIARTI000038680068). La citation est exacte :
  « dans la limite du plafond prévu au I de l'article 28-1 », avec un tableau qui va de
  « 2019 5,85 % » à « 2036 17,75 % ».
- **Article 4**, trois rédactions :
  - celle du 1er janvier 2012 (LEGIARTI000025097520) donne « 2012 4,11 % 9,90 % » ;
  - celle du 21 octobre 2012 (LEGIARTI000026514552) donne, pour les parts salariale et
    patronale, « 2012 4,00 % 9,90 % », puis 4,11 %, 4,22 %, 4,33 %, 4,44 % et 4,55 %, et
    enfin « 2018 4,66 % 9,90 % » ;
  - celle de 2026 (LEGIARTI000053469930) ne couvre que 2026 à 2036, comme la note le dit.
- **Ordonnance n° 2002-411, article 23-1** (LEGIARTI000025021004). Les non-salariés y sont
  affiliés « obligatoirement » depuis le 1er juillet 2012. Le « 1er juillet, date de
  l'affiliation » de la fiche est donc exact.

## 2. Le plafond de la caisse, année par année : conforme, à un euro par mois près

**Aucun arrêté dans le JORF.** L'article 28-1 veut un montant « arrêté par le ministre ». Je
n'ai trouvé aucun arrêté qui fixe ce plafond, ni dans l'index JORF de 2011 à 2026, ni dans
les arrêtés annuels du plafond de la Sécurité sociale, qui ne nomment pas Mayotte.

**La règle de calcul.** Deux décrets la fixent : le décret n° 2003-589, article 21
(LEGIARTI000023019089, puis LEGIARTI000026514398 depuis le 21 octobre 2012, issu du décret
n° 2010-1326), et le décret n° 2015-1679, article 1er (LEGIARTI000031634572). Leur texte :
« fixé à 1 070 euros par mois pour les rémunérations ou gains versés à compter du
1er janvier 2011. Ce montant est revalorisé chaque année conformément au taux d'évolution du
plafond en vigueur en métropole au 1er janvier de chaque année, majoré de cinq points et un
dixième ».

**Le recalcul.** Je l'ai refait sur les plafonds mensuels des arrêtés annuels lus dans le
JORF : 2 946 € en 2011, puis 3 031, 3 086, 3 129, 3 170, 3 218, 3 269, 3 311, 3 377,
3 428, 3 428, 3 428, 3 666, 3 864, 3 925 et 4 005 € en 2026. Chaque année part du montant
mensuel publié l'année d'avant :

| Année | Règle | Cnav (csv) | Écart |
|---|---|---|---|
| 2012 | 1 070 × 1,07985 = 1 155,44 | 1 155 | −0,44 |
| 2013 | 1 155 × 1,06915 = 1 234,86 | 1 235 | +0,14 |
| 2014 | 1 235 × 1,06493 = 1 315,19 | 1 316 | +0,81 |
| 2015 | 1 316 × 1,06410 = 1 400,36 | 1 400 | −0,36 |
| 2016 | 1 400 × 1,06614 = 1 492,60 | 1 492 | −0,60 |
| 2017 | 1 492 × 1,06685 = 1 591,74 | 1 592 | +0,26 |
| 2018 | 1 592 × 1,06385 = 1 693,65 | 1 694 | +0,35 |
| 2019 | 1 694 × 1,07093 = 1 814,16 | 1 814 | −0,16 |
| 2020 | 1 814 × 1,06610 = 1 933,91 | 1 934 | +0,09 |
| 2021 | 1 934 × 1,05100 = 2 032,63 | 2 033 | +0,37 |
| 2022 | 2 033 × 1,05100 = 2 136,68 | 2 137 | +0,32 |
| 2023 | 2 137 × 1,12043 = 2 394,36 | 2 394 | −0,36 |
| 2024 | 2 394 × 1,10501 = 2 645,39 | 2 644 | −1,39 |
| 2025 | 2 644 × 1,06679 = 2 820,58 | 2 821 | +0,42 |
| 2026 | 2 821 × 1,07138 = 3 022,37 | 3 022 | −0,37 |

Les montants sont en euros par mois. Douze fois chacun donne la série du dépôt : 13 860 €
en 2012, 20 328 € en 2018, 23 208 € en 2020, 31 728 € en 2024, 36 264 € en 2026. Chaque
année tombe à moins d'un euro par mois de la règle, sauf 2024. En 2014 et en 2024, l'arrondi
de la règle ne redonne pas l'euro de la Cnav : l'arrêté, qui le dirait, n'est pas dans
l'index (écart faible a, § 6).

## 3. Les valeurs, à la main puis dans les deux moteurs : conformes

**Les tests.** `python -m pytest tests/test_mayotte.py` donne 17 réussis. Avec
`PRESOMPTIONS_DECALEES=1`, 9 réussissent et 8 sont passés : la conftest écarte les tests
qui confrontent le Python au portage.

**Le compte de l'année.** J'ai fait calculer `cotisation_annuelle` aux deux moteurs. Le
Python a aussi tourné sous les présomptions décalées (`_decaler_les_presomptions`). Le
portage a lu le paquet tel quel : les trois présomptions que la garde décale (jour de
naissance, enfants, mariage) n'entrent pas dans la cotisation de l'année. Les deux moteurs
rendent les mêmes valeurs au centime, avec ou sans le décalage :

| Statut, année, revenu | À la main | Python et JavaScript |
|---|---|---|
| indépendant, 2012, 30 000 € | 13 860 × 13,90 % = 1 926,54 | 1 926,54 |
| indépendant, 2015, 50 000 € | 16 800 × 14,23 % = 2 390,64 | 2 390,64 |
| indépendant, 2018, 10 000 € | 10 000 × 14,56 % = 1 456,00 | 1 456,00 |
| indépendant, 2018, 30 000 € | 20 328 × 14,56 % = 2 959,76 | 2 959,76 |
| indépendant, 2019, 30 000 € | 21 768 × 5,85 % = 1 273,43 | 1 273,43 |
| indépendant, 2020, 30 000 € | 23 208 × 6,55 % = 1 520,12 | 1 520,12 |
| indépendant, 2024, 50 000 € | 31 728 × 9,35 % = 2 966,57 | 2 966,57 |
| indépendant, 2026, 50 000 € | 36 264 × 10,75 % = 3 898,38 | 3 898,38 |
| indépendant, 2008 et 2011 | rien : le statut naît en 2012 | rien |
| salarié, 2020, 30 000 € | inchangé (série alignée) | 5 325,00 |

**La fiche de paie** (`bloc_droit_en_vigueur`, `blocDroitEnVigueur`) rend aussi les mêmes
montants, à la seule charge de l'assuré, dans les deux moteurs : 1 926,54 € en 2012,
2 390,64 € en 2015, 2 959,76 € en 2018 et 3 898,38 € en 2026.

**La présomption de 2012 à 2018.** La somme des deux parts de l'article 4, refaite sur la
rédaction du 21 octobre 2012, donne 13,90 %, 14,01 %, 14,12 %, 14,23 %, 14,34 %, 14,45 % et
14,56 %. C'est ce que porte `taux_cotisation_annuels.csv`, au niveau `estimee`. Relancé,
`dila_legi_taux_mayotte.py` rend ces sept taux, tous de LEGIARTI000026514552. Ensuite,
`verifier_donnees.py`, sans `--appliquer`, rend : « OK taux_cotisation_mayotte_presume : 14
valeurs confrontables […] — 14 identiques », et 16 identiques pour l'article 4-2.

**Le code.** Le plafond de la caisse ne sert qu'à l'assuré sans employeur de `cssm_mayotte`.
Au compte, c'est `sansEmployeur && code === REGIME_DE_MAYOTTE`. Dans la fiche de paie, le
même test, et le plafond ne remplace une borne en euros que si la période n'en fixe pas.
Le salarié garde le plafond de la Sécurité sociale. C'est l'erreur de classe que la note
inscrit au bloc « Reprise », hors du périmètre de D-bis.

## 4. Ce que le texte ne tranche pas : déclaré

- **Le taux de 2012 à 2018.** La fiche le déclare `supposee`, de fiabilité faible, avec une
  ligne `a_relire`. Elle dit les autres lectures possibles : la part salariale seule, la
  patronale seule, ou rien.
- **4,11 % du 1er juillet au 21 octobre 2012.** Déclaré.
- **L'année 2012 comptée entière.** L'affiliation date du 1er juillet 2012, et le modèle
  compte pourtant toute l'année ; la ligne `manque` de `cssm_mayotte.yaml` le déclare depuis
  l'étape 8.
- **Le taux de 2027 à 2036**, gardé à 10,75 %. Déclaré, sans effet sur une année passée ; à
  ces dates, les scénarios 2 et 4 sont déjà au régime unique.
- **Ne sont pas déclarés** : l'arrêté du plafond, qui n'a pas été lu (§ 2 ; écart faible
  a), et la cotisation forfaitaire minimale de l'article 28-2, II, de 2012 à 2018 (écart
  faible d).

## 5. La baisse de 63,40 % du témoin né en 1955 : elle vient du texte

`resumer_temoins.py --depuis e0ccbf9` dit ceci :

- scénario 1 : aucune pension ne bouge ;
- scénarios 2 et 4 : 5 témoins bougent, de −2,92 % à −63,40 % ;
- scénario 6 : un seul témoin bouge, à −63,40 % ;
- scénarios 3 et 5 : rien ;
- pages : seul le rendu `methode` change.

Tout cela est conforme à la note.

**Le témoin `statut_independant_mayotte_1955`.** Il est indépendant de Mayotte toute sa vie
active, de 21 à 64 ans, et liquide en février 2019. Sans cotisation avant 2012, son compte
ne porte que 2012 à 2018 et janvier 2019. J'ai relu ses revenus par le portage
(`pont.carrieres_des_saisies`). J'ai calculé l'« avant » sur l'arbre d'e0ccbf9 et
l'« après » sur `main`, puis j'ai tout refait à la main. Les sigles :

- R est le revenu de l'année ;
- PSS est le plafond de la Sécurité sociale ;
- PC est le plafond de la caisse ;
- t est le taux de la série alignée sous le plafond, d le taux sur la totalité ;
- T est la somme présumée des deux parts.

| Année | R | PSS | PC (PC/PSS) | Avant : min(R, PSS) × t + R × d | Après : PC × T | Écart |
|---|---|---|---|---|---|---|
| 2012 | 36 197,06 | 36 372 | 13 860 (38 %) | 36 197,06 × 14,95 % + 36 197,06 × 1,70 % = 6 026,81 | 13 860 × 13,90 % = 1 926,54 | −68,0 % |
| 2013 | 37 035,44 | 37 032 | 14 820 (40 %) | 37 032 × 15,15 % + 37 035,44 × 1,70 % = 6 239,95 | 2 076,28 | −66,7 % |
| 2014 | 37 609,43 | 37 548 | 15 792 (42 %) | 37 548 × 15,25 % + 37 609,43 × 2,00 % = 6 478,26 | 2 229,83 | −65,6 % |
| 2015 | 38 348,66 | 38 040 | 16 800 (44 %) | 38 040 × 15,35 % + 38 348,66 × 2,10 % = 6 644,46 | 2 390,64 | −64,0 % |
| 2016 | 39 110,86 | 38 616 | 17 904 (46 %) | 38 616 × 15,45 % + 39 110,86 × 2,20 % = 6 826,61 | 2 567,43 | −62,4 % |
| 2017 | 40 040,63 | 39 228 | 19 104 (49 %) | 39 228 × 15,45 % + 40 040,63 × 2,30 % = 6 981,66 | 2 760,53 | −60,5 % |
| 2018 | 40 569,77 | 39 732 | 20 328 (51 %) | 39 732 × 15,45 % + 40 569,77 × 2,30 % = 7 071,70 | 20 328 × 14,56 % = 2 959,76 | −58,1 % |
| janv. 2019 | 3 426,77 | 3 377 / mois | 1 814 / mois | 3 377 × 5,85 % = 197,55 | 1 814 × 5,85 % = 106,12 | −46,3 % |
| Total | | | | 46 467,01 | 17 017,13 | −63,38 % |

Chaque montant annuel est celui que le moteur Python rend sur chaque arbre, au centime. Les
deux totaux sont les `cotisations_versees` du témoin, que le portage calcule.

**Le capital et la pension.** Le capital revalorisé passe de 47 483,58 € à 17 377,56 €, soit
−63,40 %. Les années anciennes, qui baissent le plus, sont aussi les plus revalorisées. Le
diviseur, 23,7698, ne change pas, et la pension passe de 1 997,64 € à 731,08 € par an. Le
scénario 6 est le 4 jusqu'à la bascule, et la liquidation de 2019 la précède : il baisse
d'autant.

**D'où viennent les 29 449,88 € de moins.**

- **Le plafond, 22 589,72 € (77 %).** La part sous plafond passe de min(R, PSS) à PC. Le
  plafond de la caisse ne vaut que 38 % à 51 % du plafond national de 2012 à 2018 :
  1 070 € par mois en 2011, revalorisés au rythme national plus 5,1 points (§ 2). Le témoin
  gagne à peu près le plafond national. L'état intermédiaire de 43cfa28, qui applique le
  plafond seul, se refait au centime : 23 785,85 € de cotisations, et −48,84 % de pension.
- **La part sur la totalité, ôtée : 5 516,94 € (19 %).** L'article 28-2 borne toutes ces
  cotisations au plafond.
- **Le taux présumé : 1 251,78 € (4 %).** Sous le plafond de la caisse, la série alignée
  (14,95 % à 15,45 %) cède la place à la somme des deux parts (13,90 % à 14,56 %).
- **Janvier 2019 : 91,44 € (0,3 %).** C'est le plafond seul : le taux, 5,85 %, ne change
  pas.

Ce n'est donc pas une erreur. Près de 96 % de la baisse (le plafond, la part sur la
totalité, janvier 2019) suit de l'article 28-2 lu tel quel ; 4 % vient de la présomption
déclarée.

- **Dans sa période.** L'article 28-2 vaut depuis le 1er janvier 2012. Le statut ne cotise
  pas avant (2008 et 2011 ne rendent rien), et le code ne sert le plafond de la caisse qu'à
  l'assuré sans employeur de `cssm_mayotte`.
- **Sur la bonne assiette.** C'est le revenu de l'année (article 28-1, II), borné au plafond
  annuel ; les mois de 2019 le sont au plafond de ces mois.
- **Indépendant de 2012 compté entier.** La baisse ne dépend guère de cette convention
  déclarée : 2012 compté pour moitié donnerait −63,05 % au lieu de −63,38 %.

**Les quatre autres témoins.**

- `independante_mayotte_assiette_minimale` (1 000 € par an), pour le seul taux de 2013 à
  2018 : 28,40 + 31,30 + 32,20 + 33,10 + 33,00 + 31,90 = 189,90 €, soit exactement
  6 809,48 − 6 619,58.
- Le témoin né en 1965 : de 2012 à 2018, 44 903,58 € deviennent 16 911,01 €. De 2019 à
  2025, 23 868,09 € deviennent 15 454,63 €. En 2026, année de la bascule, il est déjà au
  régime unique, à 12 514,18 € avant comme après. L'écart, 36 406,03 €, est exactement
  108 486,82 − 72 080,79 (écart faible c).

## 6. Quatre écarts faibles

a) **Le plafond de la caisse n'est pas recoupé à l'arrêté que le texte nomme.** La note
   dit le plafond « relu à sa source » : c'est le barème de la Cnav, qui transcrit le texte.
   La fiche cite le même barème. Aucune des deux ne dit que l'arrêté ministériel de
   l'article 28-1 n'a pas été lu, ni que la règle des décrets redonne la série à un euro
   par mois près, sauf en 2024 (−1,39 € par mois).
   - Effet : au plus 16,68 € d'assiette en 2024, soit 1,56 € de cotisation.
   - Ce qui le lèverait : l'arrêté de chaque année (une publication locale ou une
     circulaire de la caisse), ou au moins une ligne d'approximation dans la fiche.
b) **Deux empreintes de la note ne mènent à rien.** La note cite les commits 337c5d9 et
   bc608e4, que `main` n'a pas, même après `git fetch --deepen=500` : le rebasage les a
   récrits en 43cfa28 et 5940f86, de mêmes titres. La note est un récit, que personne ne
   récrit ; la présente note en donne la correspondance.
c) **Un chiffre de la note ne vaut que pour le droit en vigueur.** La note dit : « 19 353,01 €
   de 2019 à 2026 au lieu de 29 034,54 € ». C'est vrai du compte du droit en vigueur
   (`cotisation_annuelle`). Mais aux scénarios 2 et 4, 2026 est au régime unique : leur
   compte reçoit 15 454,63 € au lieu de 23 868,09 €, de 2019 à 2025. La relecture R-D le
   disait de même. Aucune valeur du modèle n'en dépend.
d) **La cotisation forfaitaire minimale de 2012 à 2018 n'est déclarée nulle part.**
   L'article 28-2, II, la veut « lorsque l'application des dispositions qui précèdent
   conduit à un montant de cotisations inférieur à un montant minimum fixé par décret ».
   - Je n'ai trouvé dans LEGI aucun décret qui fixe ce montant avant l'assiette minimale
     de l'article 4-2 (2019). Recherches : « montant minimum », « forfaitaire minimale »,
     « cotisation minimale ».
   - Ni la fiche ni `cssm_mayotte.yaml` ne le disent. Le minimum que nomme le bloc
     « Reprise » est celui des articles D. 633-2 et D. 612-6, non celui-ci.
   - Effet : les petits revenus seuls, comme le témoin à 1 000 € par an.
   - L'écart est antérieur à D-bis, dont il touche pourtant la présomption.

## 7. Complément, à la demande de l'orchestration : le passage de certification de 5940f86

Le commit 5940f86 a lancé `verifier_donnees.py --appliquer`. J'ai confronté, entrée par
entrée, `data/derive/certification.json` avant et après ce commit (`5940f86^`, puis
`5940f86`). Voici ce qui change :

- **`dernier_passage_le`** passe du 3 au 5 novembre ; rien d'autre ne bouge hors des
  séries.
- **Les deux traces de la file D.**
  - `taux_cotisation_mayotte` : 16 valeurs « identiques » au lieu de 16 « ajoutées » ; son
    empreinte (153bb30d7e5a640a) ne change pas.
  - `taux_cotisation_mayotte_presume` naît : 14 valeurs ajoutées, au niveau `estimee`.
- **Quatre séries d'autres files, dont seule la date bouge.** Pour chacune, `verifiee_le`
  passe du 31 octobre au 5 novembre. L'empreinte, le nombre de valeurs, le niveau, la
  source et les compteurs restent identiques :

| Série | Empreinte | Valeurs |
|---|---|---|
| `esperance_65_derivee` | eb9ed5da75656a7a | 28 |
| `taux_cotisation_alignes` | 788c0e4df2673be1 | 512 |
| `valeurs_point_gmp` | 3afedd6c509965db | 29 |
| `valeurs_point_ircantec_publiees` | 7341e6669d5f7a9d | 23 |

Les données de ces quatre séries ne bougent pas non plus. Dans
`taux_cotisation_annuels.csv`, le commit n'ajoute que quatorze lignes,
`taux_plafonne_non_salarie` et `taux_deplafonne_non_salarie` de `cssm_mayotte`, de 2012 à
2018. Il ne change ni n'ôte aucune ligne de la série alignée. Aucun autre fichier de ces
séries n'est dans le commit. Conforme.

**Sources** :

- index LEGI de la DILA, à jour au 4 novembre 2026 :
  - ordonnance n° 96-1122, art. 28-2 : LEGIARTI000025018560 ;
  - ordonnance n° 96-1122, art. 28-1 : LEGIARTI000025018554, LEGIARTI000031324363 ;
  - décret n° 2011-2085, art. 4-2 : LEGIARTI000038680068 ;
  - décret n° 2011-2085, art. 4 : LEGIARTI000025097520, LEGIARTI000026514552,
    LEGIARTI000053469930 ;
  - décret n° 2003-589, art. 21 : LEGIARTI000023019089, LEGIARTI000026514398 ;
  - décret n° 2015-1679, art. 1er : LEGIARTI000031634572 ;
  - ordonnance n° 2002-411, art. 23-1 : LEGIARTI000025021004 ;
- index JORF, à jour au 3 novembre 2026 :
  - décret n° 2010-1326, art. 1er : JORFARTI000023009112 ;
  - les arrêtés du plafond de la Sécurité sociale, art. 1er, de 2011 à 2026 :
    JORFARTI000023140579, 025060930, 026805246, 028214100, 029862936, 031680293, 033578232,
    036171734, 037814805, 039440182, 042748907, 044514686, 046745086, 048708695,
    050854396, 053143455 ;
- aucun arrêté du plafond de Mayotte n'a été trouvé dans l'index JORF.
