# Correction du taux plein à 65 ans des parents de trois enfants, après sa relecture

File M4, le 3 novembre 2026 : corriger ce que la relecture indépendante (note
`2026-11-03-relecture-taux-plein-parents-de-trois-enfants.md`, commit db2457d) a trouvé
dans les commits ee8e6ac et 213318b, sans étendre le calcul. Chaque texte a été rouvert
dans la session, ni la relecture ni le travail relu n'ont été repris sans lui : l'index
de la DILA (LEGI et JORF, à jour au 2 novembre 2026, aucun incrément depuis), les deux
recueils de l'Agirc-Arrco et la circulaire Cnav n° 2014-64 téléchargés le jour, leur
empreinte recalculée, identique à celle des fiches.

**Ce qui est fait.**

- *La fiche* `taux_plein_a_soixante_cinq_ans` : la phrase fausse sur l'Agirc-Arrco
  (« L'Agirc-Arrco garde l'âge de sa génération : ni l'accord du 18 mars 2011 ni celui
  du 17 novembre 2017 [...] ne nomment ces parents ») est retirée de l'approximation et du
  « à relire » ; cinq approximations nouvelles, chacune avec ses textes (identifiant,
  rédaction datée, lien et empreinte pour ce qui n'est pas au JORF), ses citations mot
  pour mot et son effet chiffré : l'Agirc-Arrco ; les fonctionnaires de l'État, de la
  CNRACL et les ouvriers de l'État ; la CAVIMAC ; les points d'avant 1973 des artisans et
  des commerçants ; le RCI, avec les points du RCO des artisans et du NRIC des
  commerçants. Trois références reprises (ci-dessous). L'effet de la fiche, ses lectures
  et son historique le disent.
- *Le test* `tests/test_taux_plein_a_soixante_cinq_ans.py` :
  `test_les_regimes_alignes_suivent_les_complementaires_non`, qui affirmait l'âge de
  66 ans et 2 mois à l'Arrco comme du droit, devient `test_les_regimes_alignes_suivent`
  (salariés agricoles et RSI, 65 ans) ; `ECARTS_DECLARES` et
  `test_ailleurs_le_modele_sert_encore_l_age_de_la_generation` disent ce que les deux
  moteurs servent encore dans huit cas (`servi_et_refait`) — l'Arrco, l'Agirc-Arrco,
  les trois fonctions publiques, la CAVIMAC —, et
  `ENCORE_A_L_AGE_DE_LA_GENERATION`, l'âge que le moteur lit encore à l'Arrco, à la
  CAVIMAC, aux points d'avant 1973 et au RCI (`droit_et_refait`, 66 ans et 2 mois au
  lieu de 65 ans) ; chacun déclaré comme écart, la valeur du droit en commentaire, à
  basculer quand le calcul viendra. Les indépendants s'y tiennent par l'âge : leur
  pension de bout en bout passe par le RCO des artisans, que le paquet de main sert en
  retard sur le jumeau Python depuis f716130 (action 177), et `servi_et_refait`
  rougissait alors sans rapport avec la règle ; leurs coefficients, 0,9375 et 0,95,
  sont lus sur le paquet refait (ci-dessous). `test_la_fiche_declare_chaque_ecart`, vu
  rouge avant la fiche pour la raison attendue
  (aucune des cinq approximations), exige que chaque écart y soit, avec ses textes et la
  valeur du modèle, et que rien n'y dise plus que l'Agirc-Arrco « garde l'âge de sa
  génération ».
- *La limite* `docs/limites/ecarts-au-droit-positif.md` : les complémentaires (Agirc-Arrco,
  Ircantec, celle des indépendants) et les régimes de base où vaut le même âge
  (fonctionnaires, CAVIMAC, points d'avant 1973, non-salariés agricoles, libéraux,
  avocats) y sont nommés un à un, sans chiffre.
- *Le cliquet des textes* : cinq rédactions sans statut de moins, de 9 355 à 9 350 sur
  main ; elles entrent « à rattacher » par les lectures de la fiche : R. 26 ter
  (LEGIARTI000024111781), les articles 65-3 (LEGIARTI000024113270) et 50-3
  (LEGIARTI000024113274), R. 723-38 (LEGIARTI000024113046, LEGIARTI000038787833).
- Aucun calcul n'a changé ; aucun témoin ne bouge. Le paquet `moteur/donnees.json` de
  main est périmé (le RCO des artisans, action 177) : refait en local pour juger les
  tests, il n'est pas commité, ni la prose que `verifier_prose.py --corriger` en
  récrivait.

**Les textes rouverts, et ce qu'ils décident.**

| Texte | Version lue | Ce qu'il décide |
|---|---|---|
| Accord du 18 mars 2011, article 1er (recueil de l'Agirc-Arrco, sha256 0186b6b1…) | liquidations du 1er juillet 2011 au 31 décembre 2018 | « en application des III et IV de l'article 20 [...] (aidants familiaux, assurés handicapés, parents d'enfant handicapé et parents de 3 enfants sous certaines conditions) ; pourront faire liquider leurs allocations AGIRC et/ou ARRCO, sans abattement, sur les tranches A et B des rémunérations » |
| Accord du 17 novembre 2017, articles 84 et 98 (sha256 b8af8df7…) | « Applicable au 1er janvier 2019 » | 84, 1 : sans abattement à « l'âge visé au 1° de l'article L. 351-8 » ; 84, 3 : sans coefficient « à l'âge auquel il a obtenu la pension d'assurance vieillesse du régime général [...] à taux plein » ; 98 : le coefficient de solidarité, « nés à partir du 1er janvier 1957 » seulement |
| Loi n° 2010-1330, article 28, III et I | LEGIARTI000023023851 (1er juillet-23 décembre 2011), LEGIARTI000025014566 (depuis) : III identique | l'âge d'annulation de la décote des fonctionnaires sédentaires parents « ne peut être supérieur à soixante-cinq ans » ; I : limite d'âge de soixante-sept ans dès 1955 |
| R. 26 ter du code des pensions | LEGIARTI000024111781, seule rédaction, depuis le 3 juin 2011 | une interruption d'au moins un an, « dans le cadre des congés ou de la disponibilité mentionnés au 1° de l'article R. 13 », ou un temps partiel de deux ans à 50 %, un an et huit mois à 60 %, un an et cinq mois à 70 % |
| Décret n° 2003-1306, article 65-3 ; décret n° 2004-1056, article 50-3 | LEGIARTI000024113270, LEGIARTI000024113274 ; décret n° 2011-620, article 10 (JORFARTI000024110234) | la même règle à la CNRACL et aux ouvriers de l'État, aux modalités de R. 26 ter |
| L. 13, L. 14, L. 24 du code des pensions ; loi n° 2003-775, article 66, III ; L. 161-17-2 | LEGIARTI000028498258, LEGIARTI000037200740, LEGIARTI000028498845, LEGIARTI000006758610, LEGIARTI000025014605 | 75 % au plus ; 1,25 % par trimestre ; le tableau de 2017 : « 1,25 % », « Limite d'âge moins 3 trimestres » ; soixante-deux ans dès 1955 |
| L. 382-27 | LEGIARTI000019959668, du 19 décembre 2008 au 1er septembre 2023 | la pension des cultes « dans les conditions définies aux articles [...] L. 351-8 à L. 351-13 » |
| Décret n° 2006-1325, article 2 | LEGIARTI000023397816, pensions dès le 1er juillet 2011 | II : la fraction d'avant 1998 prend « le coefficient de minoration fixé au 2° du I et au II de l'article R. 351-27 », qui se compte jusqu'au soixante-cinquième anniversaire de ces parents (R. 351-27, LEGIARTI000024113020) |
| Décret n° 73-937, article 3 | LEGIARTI000006765819 (19 février 2004-7 octobre 2012), LEGIARTI000026474703 (7 octobre 2012-1er septembre 2023) | avant 2012, la minoration jusqu'au « soixante-cinquième anniversaire » de tous ; depuis, jusqu'à lui pour ces parents, à « 1,25 % pour l'assuré né après 1952 » |
| Règlement du RCI, arrêté du 9 février 2012, article 12 | LEGIARTI000054891893 (2013-26 juin 2024) | « sans aucun abattement : a) A partir de l'âge fixé à l'article L. 161-17-2 [...] et à partir de la première liquidation à taux plein de la retraite de base » |
| R. 723-38 ; R. 653-2 | LEGIARTI000024113046 (3 juin 2011-8 juillet 2019), LEGIARTI000038787833 ; LEGIARTI000038770285 (8 juillet 2019-1er septembre 2023) | la même règle pour les avocats, mot pour mot, renvoyant à L. 723-10-1 puis à L. 653-2 |
| Décret n° 2011-620, article 4, 14° et 16° | JORFARTI000024110134 | l'écrit dans R. 643-7 et R. 723-38 |
| Loi n° 2025-199, article 87 | JORFARTI000051269910 | le VIII n'a que deux parties, A et B ; le 6° de L. 351-8 vient du 19° du II, que le A applique aux pensions de 2026 |
| Circulaire Cnav n° 2014-64, point 2.3.2.1 | PDF, sha256 f6717a0f… | « les périodes d'indemnisation au titre de la législation sur les accidents du travail/maladies professionnelles pour incapacité temporaire ou permanente au moins égale à 66 % » |

**Un écart que la relecture n'avait pas vu : le RCI.** En rejouant ses cas, l'artisane de
la relecture reçoit ses points du RCI et du RCO des artisans sous le coefficient 0,95 ; le
règlement du RCI, article 12, les sert « sans aucun abattement » dès la première
liquidation à taux plein de la retraite de base, que ces parents ont à soixante-cinq ans.
Il est déclaré comme les autres. Mayotte (décret n° 2004-942, article 29-2-1) n'est qu'un
autre « article 20 » dans l'index ; Saint-Pierre-et-Miquelon (décret n° 2017-1000,
article 3) remplace à R. 351-7 la référence au IV par une autre : rien n'en est écrit.

**Les calculs posés à la main.** Chaque cas est une requête du simulateur, servie par les
deux moteurs sur le paquet refait en local (`ECARTS_DECLARES` pour les huit premiers) ;
la carrière est celle de `REQUETE` — née le 15 mars
1953, au travail dès dix-huit ans, sans activité de 1976 à 1999, enfants d'avril 1976,
juin 1978 et juin 1980, partie à 65 ans, effet le 1er avril 2018 —, sauf ce que le cas
change. L'enfant d'avril 1976 ouvre le droit : 8 trimestres en 1974 et 1975, aucun de
1976 à 1978, l'activité de 1971 à 1975. L'âge de la génération est celui de la Cnav
(« 1953 66 ans et 2 mois », « 1954 66 ans et 7 mois », « à partir de 1955 67 ans »).

- *Arrco, 2018* : du 1er avril 2018 au 15 mai 2019, 13 mois et 14 jours, 4,5 trimestres,
  5 au trimestre supérieur : « moins 1 an 1 trimestre », 0,95. Le modèle :
  « 2,791.14 points × valeur de service 1.2513 € × coefficient d'anticipation 0.9500 ».
  Le droit : elle a liquidé à taux plein au régime général en application du IV de
  l'article 20 : 1. Écart : 5 % de sa complémentaire.
- *Agirc-Arrco, 2019* : née le 15 septembre 1954, sans activité de 1977 à 1999, enfants
  d'avril 1977, juin 1979 et juin 1981, effet le 1er octobre 2019 ; jusqu'au 15 avril
  2021, 18 mois et 14 jours, 6,2 trimestres, 7 : « moins 1 an 3 trimestres », 0,93 (le
  modèle : « coefficient d'anticipation 0.9300 »). Le droit : article 84, 3, et aucun
  coefficient de solidarité, née avant 1957 : 1. Écart : 7 %.
- *Agirc-Arrco, 2020* : née le 15 mars 1955, sans activité de 1978 à 2002, enfants
  d'avril 1978, juin 1980 et juin 1982, effet le 1er avril 2020 ; jusqu'au 15 mars 2022,
  23 mois et 14 jours, 7,8 trimestres, 8 : « moins 2 ans », 0,92. Écart : 8 %.
- *Fonctionnaire de l'État née le 15 mars 1955* (la même carrière, au statut de
  fonctionnaire de l'État) : soixante-deux ans le 15 mars 2017 (L. 161-17-2, que vise le
  1° du I de L. 24) ; le tableau de l'article 66, III, lu à cette année : « 1,25 % » et la
  « Limite d'âge moins 3 trimestres », soixante-sept ans (article 28, I) : 66 ans et 3
  mois ; de 65 ans à 66 ans et 3 mois, quinze mois, 5 trimestres, moins que ceux qui lui
  manquent pour la durée : 75 % × (1 − 5 × 1,25 %) = 75 % × 0,9375 = 70,3125 %. Le modèle :
  « taux 70.312% », de même à la CNRACL et aux ouvriers de l'État. Le droit, si son
  interruption de 1978 à 1980 a été un congé ou une disponibilité de R. 13 : l'âge
  d'annulation plafonné à 65 ans, 0 trimestre, 75 %. Écart : 6,25 % de sa pension. Pour
  1951 à 1954, la limite d'âge tient au décret de l'article 28, II, non rouvert ; le
  modèle sert 75 % à la fonctionnaire née le 15 mars 1953 partie à 65 ans (son âge
  d'annulation passe sous 65 ans) et 72,188 % à celle née le 15 septembre 1954
  (3 trimestres), ce que la fiche ne chiffre pas.
- *CAVIMAC* : une ministre du culte née le 15 mars 1953, au culte depuis 1979, sans
  activité de 1982 à 1999, enfants d'avril 1982, juin 1984 et juin 1986 — 8 trimestres
  cotisés en 1980 et 1981, aucun de 1982 à 1984, 11 d'activité avant —, effet le 1er
  avril 2018 : 5 trimestres jusqu'à 66 ans et 2 mois. Le modèle : « SR 16,643.72 € × taux
  46.875% × 73/165 = 3,451.68 € ; avant 1998, maximum 4,635.65 € × 11/165 × décote
  0.9375 = 289.73 € », soit 50 % × (1 − 5 × 1,25 %) = 46,875 % et 1 − 5 × 1,25 % = 0,9375.
  Le droit : 50 % et aucune décote, 3 681,79 € et 309,04 € (16 643,72 × 50 % × 73/165 ;
  4 635,65 × 11/165). Écart : 6,25 % de sa pension de la CAVIMAC.
- *Points d'avant 1973* : l'artisane de `REQUETE` ; le modèle : « 66.67 points × valeur
  de service 9.1963 € × coefficient d'anticipation 0.9375 », 1 − 5 × 1,25 % ; la
  commerçante : « 40.00 points × valeur de service 12.68096 € × coefficient
  d'anticipation 0.9375 ». Le droit (décret n° 73-937, article 3, II) : 0 trimestre
  jusqu'à son soixante-cinquième anniversaire, 1. Écart : 6,25 % de cette part.
- *RCI* : la même artisane ; le modèle : « 704.98 points × valeur de service 1.187 € ×
  coefficient d'anticipation 0.9500 » au RCI, « 5,320.93 points × valeur de service
  0.329749 € × coefficient d'anticipation 0.9500 » au RCO ; la commerçante, 0.9500 au RCI
  et au NRIC. Le droit (article 12) : 1. Écart : 5 %.

**Les vérifications.** Un script a cherché chaque fragment cité entre « » des
approximations dans le texte des sources (index LEGI et JORF, PDF téléchargés) : tous s'y
trouvent, sauf quatre que l'extraction des PDF disjoint — l'exposant de « 1er janvier
1957 », deux cellules du tableau de l'article 84 (« moins 1 an 1 trimestre », « moins 1
an 3 trimestres »), le numéro « 2010-1330 » coupé en fin de ligne —, relus sur la page.
`python -m pytest -m rapide`, sur le paquet de main : 28 échecs, les mêmes sur main sans
ce travail, aucun nouveau ; sous `PRESOMPTIONS_DECALEES=1` : 6 échecs, les mêmes sur main.
`tests/test_taux_plein_a_soixante_cinq_ans.py` (10 tests) et
`tests/test_regle_de_chacun.py` (5) passent, sur le paquet de main comme sur le paquet
refait.

**Les trois références reprises.** Le 6° de L. 351-8 vient de la loi n° 2025-199, article
87, II, 19°, que le VIII, A, applique aux pensions prenant effet à compter du 1er janvier
2026 (il n'y a pas de VIII, C). Les avocats : R. 723-38 jusqu'au 8 juillet 2019, puis
R. 653-2. La citation du point 2.3.2.1 de la circulaire va jusqu'à « au moins égale à
66 % ».

**Ce que les textes lus ne tranchent pas**, et que la fiche dit comme tel : de quel âge
l'Agirc-Arrco compte le coefficient de ces parents partis avant soixante-cinq ans depuis
2019 (« cet âge », celui du 1° de L. 351-8, que le IV fixe à soixante-cinq ans « Par
dérogation ») ; ce qu'elle sert aux points de l'Arrco des cultes, dont la pension de base
est celle de la CAVIMAC, quand les accords ne nomment que le régime général et les
assurances sociales agricoles.

**Ce qui reste**, et qui n'est pas de cette session : à la file des complémentaires,
servir sans coefficient l'Agirc-Arrco, l'Ircantec et le RCI à ces parents ; à la session
suivante de la file M4, servir le même âge aux fonctionnaires — R. 26 ter demande la
forme de l'interruption, que la saisie ne porte pas —, à la CAVIMAC et aux points d'avant
1973, puis aux non-salariés agricoles, aux libéraux et aux avocats.
