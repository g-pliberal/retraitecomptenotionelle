# Relecture de la majoration de l'Agirc de 1994 à 1996

File R-M3c, vague 6, les 3 et 4 novembre 2026 : relecture indépendante des commits 18a4dc3
et cad144a (session M3, note `2026-11-03-majoration-enfants-agirc-1995-1996.md`), qui
servent la majoration pour enfants de l'Agirc au pourcentage de service de l'accord du
9 février 1994. Chaque texte a été téléchargé ou ouvert ici, sans rien reprendre de la
session ni de mémoire. Rien n'a été modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict : conforme.** Les citations sont exactes mot pour mot, aux pages dites ; le
pourcentage s'applique selon l'année où la majoration est servie, aux retraites liquidées
depuis le 1er mars 1994, comme les textes le disent ; les valeurs de la note et des tests
se refont au centime ; les deux moteurs les rendent, pour trois, quatre et sept enfants ;
le paquet de `main` est à jour ; aucun témoin ne devait bouger ; ce que les textes ne
tranchent pas est déclaré ; les trois écarts de R-M3-bis sont corrigés. **Quatre écarts,
tous faibles**, sans effet sur un calcul : une citation de l'arrêt de 1999 tirée au-delà de
ce qu'elle dit (point 1) ; l'ancienneté du barème de 10 à 30 %, que rien ne date avant 1994
(point 2) ; un intitulé de fiche ambigu et un titre de note inexact (point 5).

## 1. Les sources, et les trois questions de la consigne

Téléchargées le 3 novembre 2026 ; chaque empreinte sha256 est celle que la note de M3 ou
la fiche porte, sauf la dernière, que la note ne cite pas.

| Texte | Ce qui a été lu | Empreinte |
|---|---|---|
| Recueil « Accords nationaux des partenaires sociaux », 205 pages | Accord du 9 février 1994 en entier (13e à 18e pages du fichier) : l'article 2 à la 14e, au pied « 16 », mot pour mot, tirets compris ; l'article 1er, « 2,303 F » pour l'exercice 1994. Le recueil entier, cherché à « pourcentage de service », « charges de famille », « 6 bis » et « majorations familiales » : aucun autre accord ne touche ce pourcentage ; celui du 18 mars 2011 (pied « 151 ») renvoie, pour les droits d'avant 2012, à l'article 6 bis « dans sa rédaction en vigueur à la veille du présent accord » | 0186b6b1…04c1, identique |
| Convention du 14 mars 1947 mise à jour au 1er janvier 2018 | Annexe I, article 6 bis, 2) (pieds « 32 » et « 33 ») : pour les périodes d'avant 2012, « 8 % pour 3 enfants », « 12 % pour 4 enfants », « 16 % pour 5 enfants », « 20 % pour 6 enfants », « 24 % pour 7 enfants ou plus » | 38966c27…ce78, identique |
| Cass. soc., 23 novembre 1999, n° 97-18.980, Juricaf | Pourvois joints 97-18.980, 97-19.055, 97-20.248, 97-21.393 et 97-21.053 (« et quatre autres ») ; « Bulletin 1999 V N° 453 p. 333 ». Les deux citations de la fiche, mot pour mot | 21ca4cde…a901, identique |
| Cass. soc., 16 décembre 1999, même numéro, Juricaf | « Rectification d'erreur matérielle » du dispositif : la phrase que la fiche cite est celle que la rectification écrit, mot pour mot | 614aa4fa…5411, identique |
| Cass. soc., 23 novembre 1999, n° 97-20.249, Juricaf | La Fédération des familles de France « n'avait pas d'intérêt à agir » ; « REJETTE le pourvoi » | 3b770359…d4f4, identique |
| CA Lyon, 18 novembre 2004, R.G. 03/03980, Légifrance JURITEXT000006944863 | Refusée à l'outil en ligne de commande (403) ; lue par l'outil de lecture du web, sans copie. « PREMIERE CHAMBRE CIVILE ». Les trois citations de la fiche, mot pour mot. Dispositif : « Infirme le jugement », « Déboute Monsieur Paul X... de toutes ses prétentions » | aucune copie, comme la fiche le dit |
| Arrêtés du 8 novembre 1994, JO du 26 novembre 1994 | Index JORF du dépôt (récupéré par `dila_index.py jorf --recuperer`, à jour au 3 novembre 2026) : JORFTEXT000000715119 (accord) et JORFTEXT000000349883 (avenant A-159, « conclu le 1er mars 1994 ») ; leurs notas, « fascicule Conventions collectives no 94-5 » (JORFARTI000001891145) et « no 94-18 » (JORFARTI000002295532) | — |
| COR, séance du 25 mai 2011, document n° 7 (DSS), 13 pages | Page 3, colonne « Annexe I, art. 6 bis » : la citation, mot pour mot ; « Document de travail, n'engage pas le Conseil », page 1 | 952c1af1…9a00, identique |
| Question écrite n° 40542 (M. Léonce Deprez), PDF de l'Assemblée | « Question publiée le : 24 janvier 2000, page 424 » ; la citation, mot pour mot ; aucune réponse publiée | 0e0b45e3…47be, identique |
| Question écrite n° 42356 (M. Richard Dell'Agnola), PDF de l'Assemblée | « Question publiée le : 22 juin 2004, page 4644 » ; l'Agirc sert alors « 8 % pour 3 enfants » à « 24 % pour 7 enfants et plus » | 098586e0…f0ea8, identique |
| Circulaire Agirc-Arrco 2020-02-DRJ, 88 pages | 55e page (fiche 4, II.2.2) : « un allocataire », « Ce montant », mot pour mot ; 79e page (fiche 6, I.1.2.2, « 1. Majorations pour enfants nés ou élevés ») : « Les majorations pour enfants nés ou élevés applicables aux droits du participant décédé sont réversibles au taux de 100 % » | 52477988…06ae, identique |
| Circulaire Agirc-Arrco 2024-5-DRJ | 4 pages (`pdfinfo`) | 83577e9a…688f, identique |
| Compilation des valeurs de point, novembre 2026 | Agirc, colonne « au 1er janvier » : 2,3030 F en 1994 et 1995, 2,3375 F en 1996, 2,3492 F en 1997 | 868a8a65…8c4a |

- **Année de service, et non de liquidation ni d'acquisition : conforme.** L'accord date
  chaque pourcentage « à compter du 1er janvier » de 1995, 1996 et 1997, sans rien dire des
  points ni des allocations déjà liquidées ; la cour de Lyon lit « les majorations
  applicables aux allocations servies à compter du 1er janvier 1995 », et la date du 1er
  janvier 1995 comme « la prise d'effet de ce mode de calcul et non la catégorie de
  retraites visée ». La liquidation n'entre que comme borne, par l'arrêt de 1999.
- **Le 1er mars 1994 : conforme.** C'est la date de l'avenant A-159, « conclu le 1er mars
  1994 » (arrêté d'extension), qui a modifié l'article 6 bis « avec effet du 1er mars
  1994 » (Cass. 1999) ; la cour de Lyon le dit « date d'entrée en vigueur de cet avenant ».
  L'accord lui-même n'écrit cette date qu'à son article 3, pour la réversion (« décès
  intervenant à compter du 1er mars 1994 »).
- **Écart faible.** La note de M3 (§ 3) dit le pourcentage applicable « quelle que soit
  leur année d'acquisition », en citant l'arrêt de 1999, « quel que soit leur mode
  d'acquisition ». L'arrêt parle du mode — il vise « les points attribués gratuitement aux
  participants ayant élevé trois enfants et plus » —, non de l'année : la règle est juste,
  mais elle ne repose que sur le silence de l'accord.

## 2. Le taux de base

- **D'où vient 10 %.** De deux sources secondaires seulement : le COR (« 10% pour 3
  enfants » à « 30% pour 7 enfants et + », avant « un pourcentage de service de 80%
  (01/03/94) ») et la question n° 40542 (« passées de 10 % pour 3 enfants et 30 % maximum
  pour 7 enfants à 8 % pour 3 enfants et 24 % maximum pour 7 enfants »). L'article 6 bis
  de 1994 est au fascicule n° 94-18, que rien ne publie en ligne. La fiche le déclare.
- **Pourquoi le modèle servait 8 %.** Sa table donnait aux points de l'Agirc d'avant 2012
  le barème que l'article 6 bis écrit depuis 2012 pour ces périodes (8 à 24 %), celui de
  la « rédaction en vigueur à la veille » de l'accord de 2011 : exactement 80 % de 10 à
  30 %, donc le pourcentage de 1997 déjà compris. Le modèle ne le compte pas deux
  fois : la ligne depuis 1997 garde 8 à 24 %.
- **Au-delà de trois enfants : conforme.** Le COR donne 15, 20, 25 et 30 % pour quatre à
  sept enfants et plus ; la table les porte, et les deux moteurs les servent (point 4) :
  le modèle ne sert pas 10 % là où le texte donne plus.
- **Écart faible.** La table sert 10 à 30 % à toute année de service jusqu'en 1994
  (`servi_debut` 1900), et la version `reglements_d_avant_le_regime_unique` n'a pas de
  borne basse. Or les deux sources ne décrivent ce barème qu'à la veille de 1994 ; rien
  lu ne dit depuis quand l'Agirc le servait. La fiche déclare « la rédaction d'avant
  l'avenant A-159 » non lue, au singulier, sans dire que les années plus anciennes ne sont
  datées par aucun texte. À nommer dans `a_relire` ; aucun témoin n'est concerné (point 4).

## 3. Les valeurs, refaites à la main

Valeurs de point (compilation, « au 1er janvier ») : 2,3030 / 6,55957 = 0,35109 € en 1994
et 1995 ; 2,3375 / 6,55957 = 0,35635 € en 1996 ; 2,3492 / 6,55957 = 0,358133 € en 1997.
Barème : 10 × 0,96 = 9,6 ; 15 × 0,96 = 14,4 ; 20 × 0,96 = 19,2 ; 25 × 0,96 = 24 ;
30 × 0,96 = 28,8 ; 10 × 0,85 = 8,5 ; 15 × 0,85 = 12,75 ; 20 × 0,85 = 17 ;
25 × 0,85 = 21,25 ; 30 × 0,85 = 25,5 ; 80 % : 8, 12, 16, 20, 24 (en %).

| Cas | Droits | À la date d'effet | Étapes au-delà de 8 % | Depuis 1997 | Note |
|---|---|---|---|---|---|
| 1er janvier 1994 | 19 246,89 × 0,35109 = 6 757,39 € | × 0,10 = 675,74 € | aucune | 675,74 € | conforme |
| 1er juin 1994 | 19 323,91 × 0,35109 = 6 784,43 € | × 0,10 = 678,44 € | 135,69 ; 108,55 ; 33,92 | 542,75 € | conforme |
| 1er avril 1995 | 19 516,93 × 0,35109 = 6 852,20 € | × 0,096 = 657,81 € | 109,64 ; 34,26 | 548,18 € | conforme |
| 1er avril 1996 | 19 871,50 × 0,35635 = 7 081,21 € | × 0,085 = 601,90 € | 35,41 | 566,50 € | conforme |
| 1er avril 1997 | 20 237,00 × 0,358133 = 7 247,54 € | × 0,08 = 579,80 € | aucune | 579,80 € | conforme |

L'« effet » de la fiche, 6 852,20 × 0,085 = 582,44 €, est juste. Le test écrit ses
attendus comme droits × taux, les taux venant des textes et les droits du détail de la
pension : il éprouve la règle, non les montants, que ce tableau vérifie.

## 4. Les deux moteurs, le paquet, les témoins

Tous les tests ont tourné sur cad144a ; les dix commits entrés depuis sur `main` (b7c82f5)
ne touchent aucun fichier de M3.

- `python -m pytest -m rapide` : 4 317 passés, 51 sautés, 13 rouges ; sous
  `PRESOMPTIONS_DECALEES=1` : 4 118 passés, 250 sautés, les mêmes 13 rouges, tous dans
  `test_pages_en_dossier.py`, les pages toutes faites que GitHub refait.
- Les fichiers qui lisent ce que M3 touche (`grep -l`) : `test_agirc_arrco_au_droit`,
  `test_carte`, `test_chronologie`, `test_cnav_baremes`, `test_destinie`,
  `test_limite_age`, `test_majoration_conjoint_a_charge`, `test_majoration_enfants_a_charge`,
  `test_majoration_enfants_agirc_1994_a_1996`, `test_oracle_points_enfants_arrco`,
  `test_reversion`, `test_simulateur`, avec `test_pont` et
  `test_majoration_enfants_agirc_arrco_avant_coefficient` : 937 passés, 1 sauté.
- Les cinq cas de M3, à quatre et sept enfants, servis par le portage et refaits par le
  Python au bit près (`servi_et_refait`) : 15 % puis 14,4, 12,75 et 12 % ; 30 % puis
  28,8, 25,5 et 24 % ; étapes de 3, 2,4 et 0,75 % des droits, de 6, 4,8 et 1,5 % ; avant
  le 1er mars 1994, 15 et 30 % sans étape ; la part que reprend la réversion, celle de
  1997, ou l'entière avant mars 1994. **Conforme.**
- Le code : `regimes_suivant_le_service` et `regimesSuivantLeService`, `etapes` et
  `MajorationsEnfantsPoints.etapes` font le même geste ; avant 1999, le modèle ne sert
  aucune majoration pour enfants à charge (`majoration_enfants_a_charge_agirc_arrco`,
  `existe: false`), et les étapes de `a_charge` ne s'y mêlent pas.
- `python scripts/construire_donnees.py` puis `git status` : rien ne change ; le paquet
  de `main` est à jour.
- **Pourquoi aucun témoin ne bouge.** Sur 930, 251 ont une pension de l'Agirc ; six partent
  avant 1999, tous sans enfant ; les deux seuls parents de trois enfants partis avant 1998,
  `enfants_avant_1972` et `enfants_loi_boulin`, sont des non-cadres. **Conforme** à ce que
  dit M3.

## 5. Ce qui n'est pas tranché, et les écarts de R-M3-bis

- **Déclaré à la fiche** : le barème de 10 à 30 %, lu au seul COR et dans une question
  écrite (première approximation) ; ce que la caisse a servi de 1995 à l'arrêt aux
  retraités d'avant mars 1994 (deuxième approximation, et `a_relire`). Le décès en 1995 ou
  1996 tient à une approximation déjà déclarée de `reversion_agirc_arrco` : aucune
  majoration reversée pour un décès d'avant 2019. **Conforme.**
- **L'entrée en vigueur.** La caisse plaidait à Lyon « après le 12 février 1994 et
  seulement à compter du 1er janvier 1995 » ; aucun premier du mois ne tombe entre le 12
  février et le 1er mars 1994, et une date d'effet au 1er mars suit le pourcentage dans les
  deux lectures : sans effet, comme M3 le dit. **Écart faible** : le § 6 de la note de M3
  s'intitule « déclaré à la fiche », quand ce point n'est que dans la note.
- **Écart faible, l'intitulé de la fiche** : « sauf pour une retraite liquidée avant le
  1er mars 1994, 10 % depuis ; plafond » se lit comme si la retraite d'avant mars 1994
  recevait « 10 % depuis » ; ces 10 % sont ceux des points acquis depuis 2012.
- **R-M3-bis, a)** : 4 pages, vérifié. **b)** 122,04 × 0,07 = 8,5428 € et
  122,0354 × 0,07 = 8,5425 €, soit 8,54 € ; 250,49 + 8,54 = 259,03 € ;
  250,49 + 8,54 + 1,10 = 260,13 €, vérifié. **c)** La fiche `reversion_agirc_arrco` nomme
  la phrase qui fait hésiter, ce sur quoi repose le choix, et la question à poser, mot
  pour mot aux 55e et 79e pages. **Corrigés.**

## Ce qui attend

Rien de bloquant. À la prochaine session de la fiche : dire dans `a_relire` qu'aucun texte
ne date le barème de 10 à 30 % avant 1994 ; récrire l'intitulé ; porter à la fiche la
lecture de l'entrée en vigueur. Hors du périmètre, à signaler : l'article 5 du même accord
prélève une contribution de solidarité de 0,7 % des allocations de 1995 et de 1 % de 1996,
« imputée sur le montant de la revalorisation », que l'accord du 25 avril 1996 (article 3)
écarte de 1996 à 1999 ; cette relecture ne dit pas si le modèle en a besoin.
