# Relecture de E : la CAVOM

File R-E3 de la vague 9, le 5 novembre 2026 : relecture indépendante du commit ee71f57 de la
session E (action 130), de sa note `2026-11-05-carte-des-fiches-cavom-lue-au-droit.md`, des
fiches `cavom_ages_minoration` et `cavom_assiette_2016`, de son journal de veille
(`2026-11-05-action-130-cavom.yaml`) et des changements de `tests/test_carte.py` et
`tests/test_sections_liberales.py`. Chaque texte a été rouvert ici, sans rien reprendre de la
session ni de mémoire, dans les index du dépôt récupérés dans la session (JORF à jour au
5 novembre 2026, LEGI au 4 novembre), par `scripts/fetch/dila_cherche.py` et par requête
directe sur ces index. Les cas ont été joués par `servi_et_refait` (`tests/outils_pont.py`),
qui fait servir chaque cas au portage et le fait refaire au moteur Python : trente et un
cas, la requête de E (`officier_ministeriel`, entrée à 25 ans, deux salaires moyens), aucun
refus, aucun écart entre les deux moteurs. Rien n'est modifié : ni règle, ni donnée, ni test.

## Le verdict

**Conforme pour l'essentiel.** Chaque citation est exacte, chaque date juste, chaque version
bien bornée ; les trois erreurs du modèle sont réelles, dans les deux moteurs, et leurs
montants exacts au centime ; l'assiette est juste de 2016 à 2025 ; la référence corrigée
(article 3, II, du décret n° 2015-1875) est la bonne. Dix écarts, tous faibles : un non
tranché que la note déclare et que la fiche tait (§ 4, a), un non tranché que ni l'une ni
l'autre ne déclare (§ 4, b), une condition incomplète (§ 3, c), cinq imprécisions de
lecture sans effet (§ 1, d à h), le bloc « Reprise » (§ 5) et une docstring (§ 6, i).

## 1. Les sources, rouvertes

Un script a cherché chaque citation des versions des deux fiches, ses morceaux séparés par
« [...] », guillemets ôtés et espaces ramenées, dans le texte de l'index qu'elle nomme : les
vingt sont trouvées, mot pour mot, comme les huit des hypothèses et des approximations. Les dates de publication sont celles de l'index.

- **Arrêté du 30 décembre 2015** (JORFARTI000031740853, publié le 31) : l'article 14, I, 1°,
  « À partir de 62 ans « En cas d'inaptitude au travail [...] ; « Ou avec application des
  coefficients d'anticipation suivants : « 0,75 si la retraite est attribuée lorsque
  l'affilié est âgé de 62 ans », jusqu'à 0,95 à 66 ans, « n'étant pas susceptibles de
  fractionnement » ; 2°, « À partir de 67 ans sans application de coefficients
  d'anticipation » ; II, « prend effet au plus tôt au premier jour du trimestre civil qui
  suit le dernier des faits ci-après » ; l'article 23 et son tableau, « Les taux de décote
  sont ajustés en conséquence ». **Conforme.** L'arrêté a quatre documents à l'index : l'article
  1er (approbation), le 2 (exécution), l'annexe et le texte ; aucun ne fixe de date, et l'annexe ne
  porte pas le mot « vigueur ». Le 1er janvier 2016, lendemain de la publication : conforme.
- **Arrêté du 28 août 2020** (JORFARTI000042311285, publié le 6 septembre) : le G, cité
  entier. **Conforme**, avec une imprécision de la note (d) : elle dit que l'arrêté « ne
  change que le renvoi de l'inaptitude » ; son 1° insère aussi, au troisième alinéa,
  « sous réserve des dérogations prévues à l'article 15 » (le cumul, récrit au H). La fiche
  cite ce 1° ; le modèle ne porte ni la cessation ni le cumul : sans effet.
- **Arrêté du 12 décembre 2024** (JORFARTI000050823056, 050823053) : l'article 2, « entrent
  en vigueur au 1er janvier 2025 » ; le 4°, a, qui remplace les « troisième à treizième
  alinéas » de l'article 14. Compté sur la rédaction de 2016, le treizième alinéa est le 2°
  des 67 ans, le quinzième celui du trimestre civil : la date d'effet n'est pas touchée ; le
  4°, b, ne remplace que le vingtième, le paiement, désormais « mensuellement et à terme
  échu ». « La date d'effet de 2016, inchangée » : **conforme**. Le mot « inapt » n'est pas
  dans l'annexe ; l'inapte n'y est nommé que par « a du 2° de l'article L. 643-4 ».
- **L. 643-4** (LEGIARTI000047453026, du 1er septembre 2023, toujours en vigueur à l'index) :
  « a) Reconnus inaptes au travail dans les conditions prévues à l'article L. 643-5 ».
  **Conforme.**
- **Arrêté du 10 juillet 2026** (JORFARTI000054435969, publié le 17) : l'annexe I, article
  1er, I et II, cités ; l'arrêté (JORFARTI000054435966, 054435967) ne fixe pas de date, et
  l'annexe ne porte pas « vigueur ». Le rectificatif du 8 août 2026 (JORFARTI000054642802)
  ne touche que la CARMF. **Conforme.**
- **Décret n° 79-265, article 5** (LEGIARTI000054168600, du 1er juillet 2026). **Conforme.**
- **Les textes d'avant 2016** : les notices de 1996 (JORFARTI000001603584, « (art. 14, 16,
  17, 27 et 28) » ; 001405558, « Bulletin officiel no 96-36 ») et de 2001 (001451960,
  « (art. 14 et 16 bis) » ; 001066668, « no 2001/29 ») : **conformes**. J'ai cherché à l'index
  tous les arrêtés qui approuvent des statuts de la section : ceux de 1997 (art. 7 et 9),
  2010 et 2018 (statuts généraux, la commission d'inaptitude), 2012 (gouvernance) ne
  touchent ni l'âge, ni le coefficient, ni la date d'effet. La présomption d'avant 2016 n'a
  donc pas d'autre texte à l'index.
- **Les textes sans effet** : 7 octobre 2014 (les points des classes, article 5, et l'alinéa
  de l'article 6) : conforme. 21 décembre 2016 : ni l'article 14 ni l'article 23, conforme ;
  mais le motif (e) omet son 18°, « Les articles 18, 20, 21 et 22 sont abrogés ».
- **Décret n° 2015-1875** (JORFARTI000031740733, article 1er ; 031740735, article 3) : la
  dérogation des quatre à sept plafonds est bien au II de l'**article 3**, dont le I fixe le
  1er janvier 2016 ; la note de LEGI (LEGIARTI000031875318, 038427708) écrit « Conformément à
  l'article 1 II ». **La correction de E est juste.** Le candidat qu'elle laisse
  (`regimes/cavom_complementaire.yaml`, « article 1er, II ») est aux lignes 172, 195 et 218,
  et aussi à la ligne 110, la période de 2016 (f).
- **Décret n° 2019-373** (articles 3 et 4) et l'article 2 du décret n° 79-265, rédactions de
  2016, 2019 et 2026 (LEGIARTI000031875318, 038427708, 054168585) : **conformes**. Les
  versions de l'article à l'index : 1980, 1987, 30 décembre 2012 (deux jours), 2013, 2016,
  2019, 2026 ; la fiche cite les quatre dernières ; `textes.py --non-lues` rend les trois
  premières, « passées ».
- **Le décret n° 2026-418** (article 22, en vigueur le 1er juillet 2026, article 30) : la
  fiche cite la rédaction qui en résulte. Elle n'en dit pas tout (g) : l'article 2 est
  désormais calculé « selon les modalités fixées aux deuxième et troisième alinéas de
  l'article L. 131-6-2 », et son III (« un nombre de point égal à son montant divisé par le
  prix d'achat du point ») est abrogé ; et elle lit « Le montant minimum prévu au premier
  alinéa s'applique pour le calcul de la cotisation des deux premières années d'activité »
  comme un « aussi », sans dire que la phrase admet une autre lecture (le minimum comme base
  des deux premières années). Sans effet sur ce que le modèle sert aujourd'hui.
- **Le taux de 12,50 %**, rouvert année par année : n° 2015-1802, article 2 (2016) ;
  n° 2017-730, articles 1er et 2 (2017, 2018), le second récrit par le n° 2018-1033,
  article 1er ; n° 2018-1033, article 2 (2019), **lui-même récrit par le n° 2019-1484,
  article 1er (JORFARTI000039684598), même taux** — la fiche cite la rédaction remplacée,
  son journal la nouvelle (h) ; n° 2020-1738, article 4 ; n° 2021-945, article 4 ;
  n° 2022-1633, article 7 ; n° 2023-1351, article 6 ; n° 2024-1214, article 6 ;
  n° 2025-1076, article 12. **Conforme.** Le taux de 2026 : l'article 14 du n° 2025-1076
  ne nomme que les médecins, les chirurgiens-dentistes et sages-femmes et les auxiliaires
  médicaux, et aucun texte de l'index publié depuis le 14 novembre 2025 ne porte de taux
  pour la section : **conforme**, il n'est pas à l'index.
- **Le cliquet** : `textes.py` rend 9 317 rédactions sans statut, ce que `perimetre.yaml`
  admet. **La carte** : `carte.manques()` rend 82 fiches et 478 manques, aucun pour la CAVOM.
  **Conformes.**

## 2. Les calculs, refaits à la main

Chaque montant est celui que les deux moteurs servent ; le coefficient est un facteur du
montant (« cotisations revalorisées × rendement × coefficient d'anticipation »), d'où la
division.

- **L'inapte de 2016 à 2024.** Né le 10 mars 1959, au 1er avril 2021 : le modèle, 0,75,
  13 564,4744 € ; au texte, 13 564,4744 / 0,75 = 18 085,9659, soit 18 085,97 €, et
  4 521,49 € de moins par an : **conforme**. Né le 10 mars 1957 : 13 979,5639 / 0,80 =
  17 474,45 € ; né le 10 mars 1955 : 14 215,2088 / 0,85 = 16 723,78 € : **conformes**.
  Points de minoration : 25, 20 et 15 ; « jusqu'à 25 points » : **conforme**.
- **L'inapte depuis 2025.** Né le 10 mars 1965 : 16 635,9784 / 2 = 8 317,99 € : **conforme**.
  Le montant est celui que le modèle calcule à 62 ans sans le servir (`non_ouverte`), la
  pension que le texte servirait du 1er avril au 30 septembre 2027 : c'est la bonne base.
  Le modèle sert ensuite 16 886,62 € par an dès le 1er octobre, 250,64 € de plus, parce
  qu'il fait cotiser six mois de plus un assuré que le texte aurait laissé partir ; ce
  n'est pas un gain au texte. Né le 10 mars 1968 : refusé à 62 ans, servi à 64 ans, 0,85 ;
  « jusqu'à deux ans », que E n'avait pas essayé : **confirmé**.
- **La date d'effet.** Né le 10 mai 1959 : le modèle, juin 2021, 13 580,6443 € ;
  13 580,6443 / 12 = 1 131,72 € : **conforme** ; au texte, le 1er juillet 2021, le 1er avril
  tombant à 61 ans. Né le 10 avril 1959 : mai, deux mois ; né le 10 juin : juillet, aucun ;
  né le 10 juillet : août, deux mois.
- **La minoration d'accord** : 0,75 à 62 ans (1er avril 2021), 0,80 à 63 ans et 6 mois
  (1er octobre 2022), 0,85 à 64 ans et 3 mois (1er juillet 2023), aucun coefficient à
  69 ans : **conformes**. Pour les nés depuis 1959, le taux plein étant à 67 ans entiers,
  « l'année entamée comptée entière » et « l'âge atteint en années » donnent toujours le
  même nombre : la règle tient pour tous les âges, pas seulement ceux essayés.
- **Les cas non tranchés** : né en 1956 à 61 ans, 0,75 ; né en 1965 à 62 ans et 6 mois,
  0,75 ; né en 1955 à 60 ans, le 1er avril 2015, 0,75 : **conformes** à ce que la note dit
  du modèle.
- **L'assiette** : 12,5 % × 4 = 0,5 plafond ; 0,25 × 12,5 % = 0,03125 ; 0,19 × 12,5 % =
  0,02375 : **conformes**. Les périodes de `cavom_complementaire.yaml` portent quatre,
  cinq, six, sept puis huit plafonds de 2016 à 2020, le quart jusqu'en 2018, 19 % depuis
  2019, huit plafonds sans minimum avant 2016 : ce que la fiche dit.

## 3. Les deux moteurs

- **Les trois erreurs, rejouées** : l'inapte de 1959, de 1957 et de 1955 reçoit le
  coefficient de l'assuré valide ; l'inapte de 1965 et de 1968 est refusé à 62 ans ; la
  pension prend effet le premier du mois qui suit l'âge. Aucun écart entre le portage et le
  moteur Python. **Conformes.** La case est bien lue : le salarié du privé inapte né en 1965
  part à 62 ans, au motif `inaptitude` ; l'officier ministériel, avec ou sans la case,
  reçoit les mêmes montants, la base CNAVPL comprise (0,7625 en 2021, la décote que
  `inaptitude_au_travail` déclare déjà gardée pour les libéraux).
- **Sous `PRESOMPTIONS_DECALEES=1`** : `test_sections_liberales.py`, `test_carte.py` et
  `test_complementaires_liberales_a_leur_age.py`, 74 verts et une confrontation au portage
  sautée, comme sans la variable (75 verts). Les cas de E nomment leur jour de naissance, que
  la variable ne décale pas ; je les ai rejoués au jour de la présomption décalée, le
  premier du mois : né le 1er mai 1959, mai 2021, deux mois ; le 1er février, février,
  deux mois ; le 1er mars, mars, **un mois**. « Un ou deux mois » tient. Mais la condition
  de la fiche, « quand l'âge tombe au premier ou au deuxième mois d'un trimestre civil »,
  est incomplète (c) : né le premier d'un mois, l'assuré dont l'âge tombe au troisième
  mois d'un trimestre part aussi un mois trop tôt.
- **L'erreur (2), la question 11 et le candidat de R-E2.** Le texte de la question 11 n'est
  dans aucune note du dépôt : `2026-11-03-decisions-du-proprietaire.md` n'en compte que
  neuf, et nulle note ne numérote une onzième. Je ne peux donc ni l'affirmer ni le nier.
  Le candidat de R-E2 (`2026-11-05-relecture-de-e-carcdsf.md`, § 3 ;
  `2026-11-05-retouches-de-la-relecture-r-e2.md`, B2) est le refus de la **base** de
  l'inapte libéral à 62 ans (L. 643-3, IV). L'erreur (2) le **recoupe sans le doubler** :
  même cas, même refus `non_ouverte`, mais une autre règle, l'article 14, 1°, a, de la
  **complémentaire**, que la table `cavom` ignore. La CAVOM se demandant sans la base
  (`SANS_LEUR_BASE`, `droit/departs.py`, depuis ddc92fc), corriger la base seule laisserait
  la CAVOM refusée jusqu'à 62 ans et 6 mois ; corriger la table seule laisserait la base
  refusée. E le dit (« écart déjà déclaré ») : **conforme** ; deux corrections, pas une.

## 4. Ce que le texte ne tranche pas

- **Déclarés, dans la note et la fiche** : les coefficients « ajustés en conséquence » des
  générations 1956 à 1958 ; l'année entamée depuis 2025 ; la régularisation d'une
  cotisation « appelée » ; l'entrée en vigueur au lendemain de la publication, le code civil
  n'étant pas à l'index. **Conformes.**
- **(a) Déclaré dans la note, non dans la fiche** : l'âge de l'inapte né avant 1959, de 2016
  à 2024 (62 ans, ou l'âge de sa table, 60 ans pour la génération 1955). La fiche écrit
  « sans coefficient dès 62 ans » pour tous (`conditions` de `statuts_de_2016`). Si l'âge
  suit la table, l'erreur (1) commence plus tôt : né le 10 mars 1955, à 61 ans en 2016, le
  modèle sert 0,80, le texte peut-être 1. Écart faible : à déclarer dans la fiche.
- **(b) Non déclaré** : depuis 2025, le coefficient court entre « l'âge auquel est demandée
  la liquidation » et l'âge du taux plein ; la fiche écrit « l'âge de la liquidation », le
  modèle prend l'âge à la date d'effet. La demande précède l'effet, au premier jour du
  trimestre civil qui suit, de trois mois au plus ; avec l'année entamée comptée entière,
  une demande faite avant l'anniversaire coûterait 5 points de plus. En 2016, « lorsque
  l'affilié est âgé de » au moment où « la retraite est attribuée » ne dit pas non plus si
  c'est la décision ou l'effet. Écart faible : à déclarer.

## 5. Le bloc « Reprise » récrit

Comparé aux notes de N (`…-crpnpac-et-regime-general.md`,
`…-complementaire-avant-la-base-des-liberaux.md`), de R-N (`…-relecture-de-n-crpnpac.md`),
de R-N2 (`…-relecture-de-n-complementaire-avant-la-base.md`) et de N-bis (`…-n-bis.md`) :
les hachages 1464c06, 329db34, ddc92fc, 10eb393 et 0ba2aea sont les bons (75b31ac est hors
de la profondeur du clone ; b9cdcfa le cite) ; « restent 82 fiches, 478 manques » et
« pour la CARCDSF, sept » (six de E et la septième de B1) sont justes ; dix lignes.
**Conforme pour l'essentiel.** Écarts faibles, de compression : « relue conforme R-N2 » —
R-N2 juge la règle conforme mais relève un écart grave, le test du site rouge depuis
ddc92fc, que le bloc ne dit que par « test du site récrit », et quatre faibles que N-bis
déclare ; de la CRPNPAC, le bloc ne garde que le candidat des vingt annuités, quand R-N et
ses retouches en laissent aussi d'autres (le refus avant 50 ans, l'anticipation d'avant
2012) ; la ligne des retouches de R-E, R-M3-ter, R-L-ter et R-D-bis (7e44534) est ôtée.

## 6. Les tests

- `tests/test_carte.py` : les deux fiches dans `LUES_AU_DROIT`, ce qui exige leur forme
  complète. **Fondé.**
- `tests/test_sections_liberales.py`, `MINORATIONS_LUES_AU_DROIT` : chaque premier du mois de
  chaque version, la période porte les paramètres de la fiche, et la durée n'annule rien —
  ce que l'article 14 de 2016 (« À partir de 67 ans ») et de 2025 (« l'âge prévu au 2° »)
  disent, la durée n'y entrant pas. **Fondé.** Sa docstring (i) ne cite que les textes de la
  CAVEC, de la CARPV et de la CAVAMAC : ceux de la CAVOM n'y sont pas.
- `NAISSANCES_AU_JOURNAL_OFFICIEL` : publications du 31 décembre 2015, du 24 décembre 2024 et
  du 17 juillet 2026, entrées en vigueur le 1er janvier 2016, le 1er janvier 2025 et le
  18 juillet 2026, relues à l'index ; le commentaire (« ne fixent pas de date ») vérifié sur
  tous les articles des deux arrêtés. **Fondé.**
- Les trois fichiers, verts, avec et sans `PRESOMPTIONS_DECALEES=1` (§ 3).

## Ce que je laisse

- Au propriétaire, inchangé : les trois erreurs de E, réelles et bien chiffrées ; l'erreur
  (2) et le refus de la base de R-E2 sont deux corrections.
- À une session de retouches : (a) et (b) à déclarer dans la fiche ; (c) la condition de la
  date d'effet à compléter ; (d) à (h), des mots de la note, de la fiche et d'un candidat ;
  (i) la docstring. Aucun ne change un chiffre servi.
- Hors de ma tâche, rien de neuf.
