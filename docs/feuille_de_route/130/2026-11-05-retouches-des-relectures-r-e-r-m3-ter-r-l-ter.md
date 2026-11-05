# Retouches des relectures R-E, R-M3-ter et R-L-ter : l'âge de l'inapte de la CAVAMAC, l'arrêté de 2003 de l'Ircantec, le taux plein des directeurs de laboratoire d'avant 1985

File « Retouches 2 », le 5 novembre 2026 : ce que trois relectures ont relevé, corrigé dans les
fiches. Les index LEGI (à jour au 4 novembre 2026) et JORF (au 5 novembre) de la DILA ont été
récupérés dans la session (`dila_index.py --recuperer`, puis `--mettre-a-jour`), et chaque
texte cité a été rouvert par `dila_cherche.py --num`, `--le` et `--texte`, ou lu dans la base de
l'index ; chaque citation écrite dans une fiche a été confrontée par un script de brouillon au
texte de l'index, espaces ramenées. **Aucune valeur du modèle ne change** : ni règle, ni
donnée, ni test, ni témoin. Ce que le modèle fait de faux se déclare ; l'âge de l'inapte se pose
au propriétaire.

## A. R-E, la CAVAMAC (`cavamac_minoration_age_seul`)

Relecture : `2026-11-05-relecture-de-e-cavamac.md`, sur 75b31ac.

**A1. L'âge du IV de L. 643-3 (écart moyen) : lu, écrit, déclaré.** La fiche disait l'âge « fixé
par un décret non lu ici ». Il est à l'index, et je l'ai lu à la bonne version :

- L. 643-3, IV, rédaction du 1er septembre 2023 (LEGIARTI000047453031, « pensions prenant effet à
  compter du 1er septembre 2023 ») : « IV.-La condition d'âge prévue au premier alinéa du I du
  présent article est abaissée, dans des conditions fixées par décret, pour les assurés relevant
  des 2° et 3° de l'article L. 643-4. » La rédaction du 31 décembre 2025 (LEGIARTI000053280388,
  pensions prenant effet à compter du 1er septembre 2026, loi n° 2025-1403, article 104, V) garde
  le IV mot pour mot ; le reste de cette rédaction (le II, la longue carrière) n'est pas lu ici, et
  la fiche ne la rattache pas.
- D. 643-14, rédaction du 1er septembre 2023 (LEGIARTI000047634694, seconde et dernière
  rédaction ; la première, du 10 septembre 2012 au 25 mai 2020, n'est pas lue) : « L'âge prévu au
  IV de l'article L. 643-3 est celui prévu à l'article D. 351-1-14. »
- D. 351-1-14, rédaction du 1er septembre 2023 (LEGIARTI000047634688, jusqu'au 1er janvier 2026),
  puis du 1er janvier 2026 (LEGIARTI000053355951), qui disent la même phrase : « L'âge prévu au
  premier alinéa de l'article L. 351-1 est abaissé, en application de l'article L. 351-1-5, à
  soixante-deux ans pour les assurés reconnus inaptes au travail dans les conditions prévues à
  l'article L. 351-7 et pour les assurés dont l'incapacité permanente est supérieure ou égale au
  pourcentage prévu pour l'application de l'article L. 821-2. »

Écrit dans la fiche : les trois textes en `textes` de la version `statuts_de_septembre_2023`
(D. 351-1-14 de 2026 dans `reglement_de_2026`), avec leurs citations ; l'approximation de l'inapte
et ses `conditions` disent l'âge ; la ligne `a_relire` « lire le décret » devient la question au
propriétaire.

Déclaré, et non corrigé : **le modèle ne sert pas cet âge.** Depuis le 1er septembre 2023, il
refuse la pension de l'inapte avant l'âge légal de sa génération (motif `non_ouverte` : le né en
1965 parti à 62 ans, âge légal opposé 62,75 ans ; le né en 1966, 63,25 ans), puis la minore, quand
le règlement la sert dès soixante-deux ans sans minoration. Ces cas sont ceux de la relecture R-E,
rejoués par elle dans les deux moteurs ; **je ne les ai pas rejoués** : il aurait fallu monter la
saisie de l'inapte, que la tâche ne demandait pas. Je n'ai rejoué que la majoration de 2011
(A2, b).

Ce que le texte ne tranche pas, ajouté à la fiche : l'âge du grand invalide, de l'ancien déporté ou
interné et de la personne du 5° de L. 351-8 (2° de L. 643-4), que D. 351-1-14 ne nomme pas ; et si
l'inapte de L. 643-5 (L. 643-4, 2°, a) est celui que D. 351-1-14 nomme « dans les conditions
prévues à l'article L. 351-7 » : L. 643-5 n'est pas lu ici. Le travailleur handicapé (3°) part
dans les conditions du III de L. 643-3, non lu ici (comme R-E).

**A2. Trois écarts faibles.**

- **L'ampleur de l'erreur b** (la majoration du second semestre 2011) : jusqu'à 25 points. Le texte
  (article 16, premier alinéa : « 5 % [...] pour chaque année pleine différée au-delà de l'âge
  mentionné à l'article 15 [...], dans la limite maximum de 25 % »), joué dans le moteur Python
  (`_calculer` de `tests/test_sections_liberales.py`, agent général, carrière dès 25 ans, né en
  1940, taux plein à 65 ans) : liquidé à 71,75 ans (novembre 2011), coefficient 1, quand le texte
  donne six années pleines différées, plafonnées à 25 %, soit 1,25 ; liquidé à 72 ans (2012),
  1,25. Le moteur rend donc le coefficient de 2012, non celui que les statuts de 2011 servent
  dès le 1er juillet. La fiche l'écrit désormais, avec le cas de février 1945 qu'elle donnait.
- **La date d'effet trimestrielle** : déclarée dans une approximation neuve. Les statuts de 2011
  (article 20) et le règlement de 2026 (article 9) disent la même phrase : « La date d'effet de la
  pension de retraite complémentaire est fixée, au plus tôt, au premier jour du trimestre civil
  qui suit la demande écrite de l'adhérent [...]. » Le modèle fait partir la pension au premier
  jour du mois qui suit l'âge (fiche `date_effet_mois_suivant`, qui nomme la CAVAMAC). Ce que le
  texte ne tranche pas, et que la fiche dit : « au plus tôt » est un plancher, la demande n'est
  pas une donnée du modèle, et la phrase n'est relue qu'en 2011 et en 2026.
- **La citation de l'article 5 du règlement**, coupée sans marque après « pour atteindre l'âge
  mentionné » : le texte poursuit « au premier alinéa de l'article 4 » ; la marque `[…]` est
  posée.

`textes.py` : le cliquet des rédactions sans statut tombe de 9 331 à 9 330, une seule des quatre
rédactions que la CAVAMAC rattache (LEGIARTI000047453031, 047634694, 047634688, 053355951)
n'ayant encore aucun statut (les autres étaient « à examiner » ou « à rattacher » ailleurs) ;
`perimetre.yaml` le dit. L'Ircantec ne le fait pas bouger : ses deux rédactions neuves
(LEGIARTI000006275868, 000006763435) étaient rattachées à une autre de ses versions.

## B. R-M3-ter, l'Ircantec (`coefficient_anticipation_ircantec`)

Relecture : `2026-11-05-relecture-de-m3-ter.md`, sur a28adbd. Trois retouches, une citation nouvelle
chacune.

- **L'arrêté du 26 décembre 2003, source du terme du 31 décembre 2003.** Lu dans l'index JORF :
  arrêté « relatif aux modalités de fonctionnement du régime de retraites complémentaire des agents
  non titulaires de l'Etat et des collectivités publiques » (JORFTEXT000000246821, JO du
  30 décembre 2003). Article 3, III (JORFARTI000002450292) : « III. - Le a du 6° du paragraphe 1
  est rédigé ainsi qu'il suit : « a) Aux agents et anciens agents admis à faire liquider leur
  retraite au régime général en application de l'article L. 351-1-1 du code de la sécurité
  sociale ; » ». Article 7 (JORFARTI000001472523) : « Les dispositions du présent arrêté entrent en
  vigueur le 1er janvier 2004. » Cités dans les `textes` des versions
  `escalier_au_trimestre_1983` et `retraite_anticipee_2004`, dans la prose de la première et dans
  une lecture neuve de `sources`.
- **La phrase sur le décret n° 82-628.** « LEGI n'a de ce décret que ses articles 8, 9 et 13 à 16
  (LEGIARTI000006763432 à 438) » devient : l'index LEGI du dépôt, filtré par thème, n'a de ce
  décret que ses articles 8, 9 et 13 à 16 (LEGIARTI000006763432, 433, 435 à 438), le 434, que la
  plage couvre, n'y étant pas. Vérifié dans la base : les identifiants 432, 433, 435, 436, 437 et
  438 sont les articles 8, 9, 13, 14, 15 et 16 ; `LEGIARTI000006763434` ne s'y trouve pas.
- **L'article 9 de l'ordonnance n° 82-270 et l'article 13 du décret n° 82-628** dans les `textes`
  de `structure_financiere_1983` (LEGIARTI000006275868 ; LEGIARTI000006763435), avec leurs
  citations : « Toutefois, les personnels visés aux articles L. 351-16 et L. 351-17 du code du
  travail, âgés d'au moins soixante-trois ans et justifiant d'une durée d'assurance de 150
  trimestres, bénéficient, dès le 1er juillet 1982, du taux plein défini à l'article 1er de la
  présente ordonnance » ; « La durée d'assurance dont doivent justifier les personnels visés à
  l'article 9, deuxième alinéa, de l'ordonnance du 26 mars 1982 susvisée pour bénéficier, dès le
  1er juillet 1982, du taux plein peut avoir été accomplie dans le régime général ou dans ce régime
  et un ou plusieurs autres régimes de base obligatoires. »

## C. R-L-ter, les directeurs de laboratoire (`regimes/asv_directeurs_laboratoire.yaml`)

Relecture : `2026-11-05-relecture-corrections-r-l-bis.md`, § 4. La période de 1981 à 2007 porte
`age_taux_plein: 65` ; R. 351-27, que la fiche cite, ne commence que le 21 décembre 1985
(LEGIARTI000006749434, première rédaction, du 21 décembre 1985 au 28 août 1993 : « l'âge prévu au
1° de l'article L. 351-8 est fixé à soixante-cinq ans », la même phrase que les rédactions
suivantes). **L'âge de l'ancien code, d'avant la codification, n'est pas lisible ici** :

- l'index LEGI s'ouvre à la codification du 21 décembre 1985 ; ni L. 267 ni L. 682, que cite le
  décret n° 81-1046, n'y sont (`--num`, titre « securite sociale ») ;
- deux recherches au JORF de 1981 à 1985 (« taux plein » « soixante-cinq ans » « salaire annuel de
  base » : aucun document ; les prestations supplémentaires de vieillesse des laboratoires) ne
  rendent aucun décret sur l'âge ;
- les arrêtés d'approbation des statuts de la section, du 24 novembre 1981 (JORFTEXT000000293163)
  et du 28 novembre 1985 (JORFTEXT000000871231), n'ont que leur titre à l'index, texte vide ;
- l'article 2 du décret n° 81-1046, lu en entier (LEGIARTI000006768391), renvoie le montant et les
  modalités de calcul et d'attribution au règlement, sans nommer d'âge.

**Déclaré** : de 1981 au 20 décembre 1985, les soixante-cinq ans sont présumés, sans texte ; la
fiche du régime le dit dans sa description et dans les notes de la période. Aucune valeur ne
change.

## Ce qui reste, à transmettre

- **Au propriétaire** : l'âge de l'inapte de la CAVAMAC (A1). D. 351-1-14 donne soixante-deux ans à
  l'inapte et à l'incapacité permanente au taux de L. 821-2 ; le modèle refuse l'inapte avant l'âge
  légal de sa génération. Ouvrir l'inapte à soixante-deux ans, dans les deux moteurs, est un
  changement de valeur, qui demande son accord.
- **Non lu** : L. 643-5 (l'inapte du 2°, a) ; le III de L. 643-3 (le travailleur handicapé) ; le
  reste de la rédaction de L. 643-3 du 31 décembre 2025 ; le Bulletin officiel, pour les statuts
  d'avant 2011 de la CAVAMAC et ceux des directeurs de laboratoire d'avant 1985.

Sources : LEGI LEGIARTI000047453031, 053280388 (L. 643-3) ; LEGIARTI000047453026 (L. 643-4) ;
LEGIARTI000047634694 (D. 643-14) ; LEGIARTI000047634688, 053355951 (D. 351-1-14) ;
LEGIARTI000006763432, 433, 435 à 438, 000006763434 absent (décret n° 82-628) ;
LEGIARTI000006275868 ; LEGIARTI000006749434, 000006749436 (R. 351-27) ; LEGIARTI000006768391
(décret n° 81-1046, article 2) ; LEGIARTI000006742632 (L. 351-8, 1985). JORF JORFARTI000024270173
(statuts de 2011, article 20), JORFARTI000054436046 (règlement de 2026, articles 5 et 9),
JORFTEXT000000246821, JORFARTI000002450292, JORFARTI000001472523 (arrêté du 26 décembre 2003),
JORFTEXT000000293163, JORFTEXT000000871231 (arrêtés de 1981 et de 1985, titres seuls).
