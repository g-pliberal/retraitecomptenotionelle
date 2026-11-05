# Relecture de E (CAVAMAC)

File R-E, le 5 novembre 2026 : relecture indépendante du commit 75b31ac (file E, note
`2026-11-05-carte-des-fiches-cavamac-lue-au-droit.md`), qui lit au droit la fiche
`cavamac_minoration_age_seul`. Chaque texte a été rouvert dans les index JORF et LEGI récupérés
par `dila_index.py --recuperer`, puis mis à jour des incréments `JORF_20261105-002736` et
`LEGI_20261104-214059` ; chaque citation, confrontée par un script au texte de l'index, espaces
ramenées. Chaque cas a été joué dans les deux moteurs sur la même requête du formulaire (statut
`agent_general_assurance`) : le Python par `_python` (`tests/test_liquidation.py`), le portage
par `tests/js/comparer-liquidation.mjs`. Chacun deux fois : au jour de naissance présumé, puis
au 1er du mois, ce que `PRESOMPTIONS_DECALEES=1` fait dire au Python (`DECALAGES`, jour 1).
Le script du portage lit le paquet sans passer par le pont : sous la variable, il ne décale rien.
Le jour 1 a donc été écrit dans la requête (`naissance=AAAA-MM-01`), que les deux moteurs lisent.
Les deux moteurs rendent partout la même date d'effet, le même motif d'ouverture et le même
coefficient ; le Python sous la variable rend les mêmes coefficients qu'au jour 1. Rien n'a été
modifié : ni règle, ni donnée, ni fiche, ni test.

**Verdict : conforme à la source pour l'essentiel.** Les citations sont exactes, mot pour mot. Les
dates d'entrée en vigueur et les bornes des cinq versions sont justes, comme les calculs de la
note et la carte. **Les cinq erreurs du modèle sont réelles**, dans les deux moteurs, au jour
présumé comme au jour 1. **Un écart moyen** : l'âge du IV de L. 643-3, que la fiche dit fixé par
« un décret non lu ici », est à l'index (D. 643-14, qui renvoie à D. 351-1-14 : soixante-deux
ans). Depuis le 1er septembre 2023, l'erreur de l'inapte va donc plus loin qu'écrit : le modèle
refuse la pension avant l'âge légal (§ 3). **Trois écarts faibles** : l'erreur b va jusqu'à 25
points, et la fiche n'en donne qu'un cas de 5 (§ 4, b) ; la date d'effet trimestrielle que la
fiche lit, sans déclarer que le modèle ne la sert pas (§ 3) ; une citation de l'article 5 du
règlement coupée sans marque (§ 1).

## 1. Les sources, rouvertes

| Ce que la fiche cite | Texte rouvert | Verdict |
|---|---|---|
| Statuts de 2011, articles 15 et 16 (JORFARTI000024270173, publié le 29 juin 2011) | chaque fragment cité, à l'index mot pour mot | conforme |
| Arrêté du 23 juin 2011, article 2 (JORFARTI000024270156) : « … le 1er juillet 2011. » | mot pour mot | conforme ; borne du 1er juillet 2011 juste |
| L. 351-8, 1° : LEGIARTI000023030950 (du 1er juillet 2011 au 22 janvier 2014), LEGIARTI000028498855 (jusqu'au 1er septembre 2023) | les deux disent « l'âge prévu à l'article L. 161-17-2 augmenté de cinq années » ; la rédaction du 1er septembre 2023 (LEGIARTI000047452736) dit « augmenté de trois années » | conforme : la fiche borne au 31 août 2023 |
| Arrêté du 4 août 2023 : annexe, 6° et 7° (JORFARTI000047977908) ; article 2 (JORFARTI000047977903) | mot pour mot ; le 6° récrit l'article 15, le 7° l'article 16 ; le 6° et le b du 7° entrent en vigueur au 1er septembre 2023, les a, c et d du 7° au 1er janvier 2024 | conforme |
| L. 643-4, 2° et 3° (LEGIARTI000047453026, 1er septembre 2023) | mot pour mot | conforme |
| Règlement de 2026, articles 4 et 5 (JORFARTI000054436046, publié le 17 juillet 2026) | mot pour mot ; l'arrêté du 10 juillet 2026 n'a que deux articles, l'approbation et la publication (JORFARTI000054436043 et 044), aucune date : d'où le 18 juillet | conforme ; **écart faible** : la première citation de l'article 5 s'arrête sur « pour atteindre l'âge mentionné », sans marque de coupure, quand le texte poursuit « au premier alinéa de l'article 4 » |
| Décret n° 67-1169, article 4 (LEGIARTI000054168357, en vigueur le 1er juillet 2026) | mot pour mot | conforme |
| Avant 2011 : JORFTEXT000000342796 (« (art. 12 et 15) », « Bulletin officiel no 90-05 ») ; JORFARTI000001232209 (« (art. 1er à 10, 12, 13, 15, 15 bis, 16, 19 bis et 20 à 23) ») ; JORFARTI000001901194 (« no 98-38 ») | mot pour mot ; les arrêtés de 1967 (JORFTEXT000000660274) et de 1983 (JORFTEXT000000494188) n'ont que leur titre à l'index, texte vide | conforme ; la version supposée est déclarée (statut `supposee`, fiabilité faible, approximation, à relire) |
| Six arrêtés sans effet : 2007, 2012, 2014, 2016, 2017, 2025 | aucun ne touche les articles 15 et 16 du régime complémentaire ; l'arrêté de 2016 récrit des articles 15 et 16, mais des statuts généraux (le président, le vice-président) ; en 2012, l'article 19 (l'AAH), l'invalidité-décès ; en 2025, l'article 24, puis l'invalidité-décès | conforme |
| Réversion : statuts de 2011, articles 22 et 23 ; règlement de 2026, articles 11 et 12 | « au moins 1 500 points », « âgé d'au moins 65 ans », « marié depuis deux ans au moins », « soixante pour cent (60 %) », « n'est pas minoré par le coefficient de minoration », « bénéficie du coefficient de prorogation » : mot pour mot | conforme |
| Date d'effet (`lit`) : « au premier jour du trimestre civil qui suit la demande écrite » | statuts de 2011, article 20 ; règlement de 2026, article 9 : mot pour mot | conforme (voir § 3 pour ce que le modèle en fait) |

Le cliquet des textes descend bien de 9 332 à 9 331 (`perimetre.yaml`, diff du commit).

## 2. Les valeurs de la note, refaites à la main

- **2011, la minoration** : né en 1955, l'âge de L. 161-17-2 est 62 ans, le taux plein
  62 + 5 = 67 ans ; parti à 62 ans, à 60 mois du taux plein : « entre le 49e et le 60e mois »,
  25 %, 0,75. Les deux moteurs rendent 0,7500, au 1er juillet 2017 (jour présumé) comme au
  1er juin (jour 1). La table du modèle (`age_annulation_decote.csv`) dit 65,33 pour le second
  semestre de 1951, puis 65,75, 66,17 et 66,58 pour 1952, 1953 et 1954, et 67 depuis 1955 :
  60,33 + 5, 60,75 + 5, 61,17 + 5, 61,58 + 5. Conforme.
- **L'exemple de la caisse** : né le 8 août 1960, effet au 1er juillet 2026, 67 ans le 8 août
  2027, du 1er juillet 2026 au 1er octobre 2027, cinq trimestres, 6,25 % : les deux moteurs
  rendent 0,9375. Conforme.
- **La longue carrière** : 67 − 62 = 5 ans, 20 trimestres × 1,25 % = 25 % ; 67 − 63 = 4 ans,
  16 × 1,25 % = 20 % ; le texte, 1 − 0,15 = 0,85. Conforme.
- Les cas de la majoration de 2011 et de 2023 et de l'inapte sont refaits au § 4.

## 3. Ce que le texte ne tranche pas

- **Avant le 1er juillet 2011** : déclaré (version `statuts_d_avant_2011`, `supposee`), avec ce
  que la présomption couvre (la minoration) et ce qu'elle ne couvre pas (aucune majoration servie,
  les périodes de 1968 à 2011 n'ont pas de `surcote_par_trimestre` : vérifié dans
  `regimes/cavamac_complementaire.yaml`). Conforme.
- **Du 1er au 17 juillet 2026**, le règlement que le décret appelle n'est pas encore approuvé :
  déclaré. Conforme.
- **Le mois entamé** : déclaré. Conforme.
- **L'âge du IV de L. 643-3 : écart moyen.** Le texte le tranche. L. 643-3, IV
  (LEGIARTI000047453031, pensions prenant effet depuis le 1er septembre 2023) : la condition
  d'âge « est abaissée, dans des conditions fixées par décret, pour les assurés relevant des 2°
  et 3° de l'article L. 643-4 ». D. 643-14 (LEGIARTI000047634694, même date) : « L'âge prévu au
  IV de l'article L. 643-3 est celui prévu à l'article D. 351-1-14 ». D. 351-1-14
  (LEGIARTI000047634688, du 1er septembre 2023 au 1er janvier 2026, puis LEGIARTI000053355951) :
  l'âge est « abaissé […] à soixante-deux ans pour les assurés reconnus inaptes au travail ». La
  relecture R-E-bis avait relevé le même manque, le 3 novembre, pour la CAVEC et la CARPV
  (`2026-11-03-relecture-corrections-r-e.md`). Au moteur : inapte né le 1er janvier 1965, parti à
  62 ans le 1er janvier 2027, ou né le 1er janvier 1966, parti le 1er janvier 2028, motif
  `non_ouverte` (âge opposé 62,75 et 63,25), dans les deux moteurs. Le règlement de 2026 (article
  4) le sert dès 62 ans sans minoration. Depuis le 1er septembre 2023, l'erreur a ne se borne
  donc pas à « toute la minoration de son âge » : pour les générations dont l'âge légal passe 62
  ans, le modèle refuse la pension jusqu'à cet âge, puis la minore. Le travailleur handicapé (3°)
  part dans les conditions du III de L. 643-3 : non relu ici.
- **La date d'effet trimestrielle : écart faible.** La fiche lit (`lit`) la date d'effet « au
  premier jour du trimestre civil qui suit la demande écrite ». Aucune approximation ne dit que
  le modèle ne la sert pas : la fiche `date_effet_mois_suivant` nomme `cavamac_complementaire`
  (ligne 13) sans rien dire du trimestre civil. Le modèle liquide la CAVAMAC au 1er novembre
  2011, au 1er novembre 2023, au 1er février 2026, dates que la caisse ne sert pas. Une pension
  que le modèle fait partir le 1er novembre 2023 ne partirait à la caisse que le 1er octobre 2023
  ou le 1er janvier 2024, et cette seconde date relève des statuts de 2024.

## 4. Les cinq erreurs du modèle, au moteur

Chaque valeur du modèle est la même dans les deux moteurs, au jour présumé et au jour 1 ; chaque
cas est ouvert (motif `age_legal` ou `carriere_longue`), sauf ceux que le § 3 dit refusés.

**a) L'inapte et les catégories sans minoration : réelle.**
- Né le 1er juin 1955, carrière dès 21 ans, inapte, parti à 62 ans (1er juin 2017) : le modèle
  sert 0,7500, comme à l'agent valide. L'article 15, a, de 2011 le liquide « à taux plein sans
  application d'un coefficient de minoration » : 1. Écart : 25 points.
- Né le 1er janvier 1963, inapte, à 63 ans (1er janvier 2026, statuts de 2024) : 0,8000 ; né le
  1er octobre 1963, au 1er octobre 2026 (règlement de 2026, article 4) : 0,8000. Le texte : dès
  62 ans (D. 351-1-14), sans minoration, 1. Écart : 20 points.
- Contrôle : l'inaptitude est bien lue, car le salarié inapte né en 1955, carrière dès 30 ans,
  reçoit du régime général un taux de 50 % au lieu de 37,5 %. L'agent général non inapte reçoit
  les mêmes 0,7500 et 0,8000.
- **Ampleur** : juste jusqu'en août 2023, plus large depuis (§ 3).

**b) La majoration du second semestre 2011 : réelle ; ampleur incomplète, écart faible.**
- Né le 1er février 1945 : l'âge de L. 161-17-2 est 60 ans, le taux plein 65 ans, en février
  2010. Au 1er novembre 2011 (66 ans 9 mois), une année pleine différée, 1,05 : le modèle ne
  sert aucun coefficient, 1. Au 1er janvier 2012, 1,05 ; au 1er novembre 2012, 1,10 : le texte
  aussi.
- Cause, vérifiée : la période de 2004 à 2011 de `cavamac_complementaire` a
  `surcote_par_trimestre: null`, celle de 2012 à 2018 a 0,0125.
- **Ampleur** : jusqu'à 25 points, non 5. Né le 1er février 1940, au 1er novembre 2011 (71 ans 9
  mois) : six années pleines, 25 % au plus, 1,25 au texte ; le modèle sert 1, puis 1,25 au 1er
  janvier 2012. La fiche ne donne que le cas de 5 %.

**c) De septembre à décembre 2023, la majoration comptée depuis l'âge de L. 351-8 : réelle,
ampleur juste (5 points au plus).**

| Naissance, effet | Âge | Texte, depuis 67 ans | Modèle, depuis la table |
|---|---|---|---|
| 1er février 1954, 1er novembre 2023 | 69 ans 9 mois | 2 ans, 1,10 | 66,58 : 3 ans 2 mois, 1,15 |
| 1er juin 1952, 1er novembre 2023 | 71 ans 5 mois | 4 ans, 1,20 | 65,75 : 5 ans 8 mois, 1,25 |
| 1er janvier 1953, 1er septembre 2023 | 70 ans 8 mois | 3 ans, 1,15 | 66,17 : 4 ans 6 mois, 1,20 |
| 1er décembre 1951, 1er septembre 2023 | 71 ans 9 mois | 4 ans, 1,20 | 65,33 : 6 ans 5 mois, 1,25 |
| 1er octobre 1951, 1er novembre 2023 | 72 ans 1 mois | 5 ans, 1,25 | 1,25 : égaux au plafond |

L'écart à 67 ans est de moins de deux ans, et le plafond de 25 % borne le reste : 5 points au
plus, comme la fiche l'écrit.

**d) La longue carrière à 15 % : réelle, ampleur juste, déjà déclarée** (fiche du 23 septembre,
`effet`).
- Né le 1er janvier 1964, au travail dès 18 ans, à 62 ans (1er janvier 2026, motif
  `carriere_longue`) : 0,7500 ; le texte (7°, d, de 2023) : 0,85. Écart : 10 points. Né le 1er
  septembre 1964, au 1er septembre 2026 (règlement de 2026, article 5) : 0,7500, même écart.
- À 63 ans (1er janvier 2027, motif `age_legal`) : 0,8000 ; le texte : « à 63 ans pour les
  assurés ayant commencé leur activité avant l'âge de 21 ans », 15 %, avant 64 ans : 0,85, écart
  de 5 points. Le texte demande que l'assuré « réponde aux conditions » de L. 351-1-1, non qu'il
  en use : partir à l'âge légal n'y change rien.

**e) La réversion : réelle, ampleur juste.**
- Agent né le 1er juin 1950, carrière dès 25 ans, liquidé à 65 ans, mort en juin 2020 ; conjointe
  née en 1952 (67 ou 68 ans), mariés en 1975. Ligne de réversion de la CAVAMAC : base 7 363,18 € (7
  384,55 € au jour présumé), taux 0, montant 0, motif `non_portee`, dans les deux moteurs.
  Agent né le 1er juin 1960, mort en juin 2030, conjointe de 1958 : base 12 797,07 €, montant
  0, `non_portee`. Le texte : 60 % des points, au conjoint d'au moins 65 ans marié depuis deux ans.
- La condition des 1 500 points n'est pas vérifiable au modèle, qui compte en cotisations
  revalorisées × rendement, et non en points ; ces deux carrières de 40 et 42 ans la passent
  sans doute, sans que ce soit établi.
- La consigne de la relecture cite L. 643-7 pour cette erreur : c'est la réversion de la base de
  la CNAVPL (LEGIARTI000019959385, « dans les conditions prévues aux articles L. 353-1… »). La
  fiche fonde à bon droit celle de la CAVAMAC sur ses statuts (articles 22 et 23) et son
  règlement (articles 11 et 12). Dans ces deux cas, la réversion de la CNAVPL est elle aussi
  `non_portee` : déjà signalée par R-E-bis.

## 5. La carte, recomptée

`carte.manques()`, lancé sur un arbre de chaque commit :
- au parent du commit (87e0ce8), **86 fiches et 505 manques**, dont les sept de la fiche :
  `domaine`, `etape`, `lit`, `ecrit`, `dates_qui_decident`, `versions`, `approximations` ;
- au commit 75b31ac, **85 et 498** ;
- au dernier `main` (ca2cb5f), 85 et 498.

Les chiffres de la note sont ceux du script. Le compte du 3 novembre (85 et 503) n'est pas
recompté. `tests/test_sections_liberales.py` et `tests/test_carte.py` : 64 tests passent.

## 6. Vu en passant, hors de la fiche

- **L'inapte de la CNAVPL est minoré** : né le 1er juin 1955, carrière dès 30 ans, inapte, à
  62 ans (1er juillet 2017), la base sert 0,7500 dans les deux moteurs. Le texte : L. 643-4, 2°,
  a (LEGIARTI000019959512, du 19 décembre 2008 au 1er septembre 2023) liquide « sans coefficient
  de réduction » l'inapte qui a l'âge du premier alinéa du I de L. 643-3. Cet âge est
  « l'âge prévu au premier alinéa de l'article L. 351-1 » (LEGIARTI000028498667), 62 ans pour
  la génération 1955. Déjà signalé par R-E-bis, le 3 novembre.

## 7. Ce qui reste

- À la file E : dire l'âge du IV de L. 643-3 (D. 643-14, D. 351-1-14 : 62 ans) et clore le second
  point de `a_relire` ; élargir l'effet de l'erreur de l'inapte depuis septembre 2023 (le refus
  avant l'âge légal) ; donner le maximum de l'erreur b (25 points) ; déclarer la date d'effet
  trimestrielle que le modèle ne sert pas ; marquer la coupure de la citation de l'article 5.
- À une file du modèle : les cinq erreurs, telles que la fiche les déclare, avec ces ampleurs.
