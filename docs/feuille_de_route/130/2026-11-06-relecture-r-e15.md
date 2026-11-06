# Relecture de E14 : les écarts de R-E14, et la CAVEC, la CAVP et la CPRN de `surcote_par_age_seul` en versions (R-E15)

File E, relecture R-E15, le 6 novembre 2026 (action 130, vague 11, sur Opus), du commit
5202765 (E14, session `session_01FVFLAkF7b5v2oz2jwNP9wt`), de sa note
`130/2026-11-06-e14-surcote-par-age-seul.md`, de ce qu'il a écrit dans
`data/reference/regles/surcote_par_age_seul.yaml`, de l'entrée de la fiche à
`LUES_AU_DROIT` et du bloc « Reprise » de l'action 130. Index de la DILA récupérés ce
jour : JORF à jour du 3 novembre 2026 (20261103-002311), LEGI du 2 novembre
(20261102-213929) ; recherches en SQL sur toute la table `doc`, au titre puis au texte,
sans borne de réponses. Cas posés dans les deux moteurs par `servi_et_refait`
(`tests/outils_pont.py`), réglages de E11 (`profil` plat, `euros` 2026, `enfants` 0,
`sexe` F, `salaire` 2, `debut` 22), naissances au 10 mars, sous les deux jeux de
présomptions ; un script hors du dépôt. Rien n'est modifié : ni règle, ni donnée, ni test.

**Verdict.** Aucune erreur. Chaque citation se retrouve mot pour mot, chaque date et
chaque borne au texte, chaque montant au centime ; les deux moteurs servent, sous les deux
jeux, chacun des cas posés de E14, au coefficient et à l'euro près. Les listes d'arrêtés de
la CAVP, de la CPRN et de la Cipav sont complètes au Journal officiel ; celle de la CAVEC
l'est depuis 2008. Le point non tranché neuf de la CAVEC est bien un point non tranché :
les deux lectures restent tenables. **Trois écarts faibles**, de preuve : (a) les arrêtés
de la CAVEC d'avant 2008 ne sont nommés nulle part ; (b) « un article 3.14 qui existait
donc » s'appuie sur un indice que contredit en partie l'arrêté du 27 février 2003 ; (c) la
section « Pour la suite » omet les statuts de la CAVP d'avant 2009. **Un candidat neuf,
moyen**, hors du code de E14 mais contraire à sa phrase « Confronté mois par mois
(… trimestres cotisés …) : seuls ressortent la CAVEC de janvier à mars 2008 et la CAVP de
juillet à décembre 2011 » : à la CPRN, depuis 2024, le modèle perd les trimestres
d'exercice de l'année où l'âge du taux plein est atteint quand cet âge n'est pas entier
(notaire né le 10 mars 1953, au 1er janvier 2024 : 16 trimestres au lieu de 18, au moins
397,92 € par an servis en moins).

## 1. La CAVEC (section 2 de E14)

**Les arrêtés.** Au titre, de 1946 à 2026 (« expert » et « compta », ou « commissaires aux
comptes »), puis les arrêtés à plusieurs sections (titres « sections professionnelles »,
« divers régimes », « à des statuts »), puis au texte. Depuis 2008, les douze textes de E14
sont tous ceux du JO, et seuls ceux-là : 22 février 2008 (JORFTEXT000018197770), 26 novembre
2010 (JORFTEXT000023172855), 9 février 2012 (JORFTEXT000025395360), 27 mars 2012
(JORFTEXT000025687508), 7 octobre 2013 (JORFTEXT000028104493), 7 octobre 2014
(JORFTEXT000029613764), 20 août 2018 (JORFTEXT000037363865), 19 juin 2019
(JORFTEXT000038689125), 2 juillet 2024 (JORFTEXT000049880539), 4 juillet 2025
(JORFTEXT000051849606), 16 décembre 2025 (JORFTEXT000053142584), règlement du 10 juillet
2026 (JORFTEXT000054435934). Le décret n° 2008-85 du 24 janvier 2008, qui modifie le
décret n° 53-506, ne touche que l'intitulé, l'article 1er et les classes de l'article 2
(JORFARTI000017991851 à 856) ; aucun texte à plusieurs sections depuis 2008, hors le décret
n° 2026-418, que la fiche range à sa version de juillet 2026.

Chacun lu à son annexe (« 3.14 », « 1.1.4 », « prorogation », « 65e », « trimestre plein »,
« vigueur », « prend effet ») :
- 2008 (JORFARTI000018197778) : « L'article 3.14 est ainsi rédigé : « Le compte de points de
  l'assuré qui diffère la liquidation de la retraite au-delà du 65e anniversaire est majoré
  de 1,25 % par trimestre plein de prorogation dans la limite de 25 %. La majoration
  s'applique au compte de points arrêté au 31 décembre de l'année du 65e anniversaire. Les
  points provenant des cotisations versées pendant cette période de prorogation ne
  bénéficient pas de cette majoration. » » : la citation de la fiche, mot pour mot. Ni
  l'article 1er (JORFARTI000018197775) ni l'article 2 (JORFARTI000018197776, l'exécution)
  ne fixent de date ; publié le 1er mars 2008 : le 2 mars. Conforme.
- 9 février 2012 (JORFARTI000025395367) : « L'article 3.14 est ainsi modifié : […] les mots :
  « au 31 décembre de l'année » sont remplacés par les mots : « à la fin du trimestre ». ―
  à l'alinéa 3 : ― les mots : « pendant cette période de prorogation » sont remplacés par
  les mots : « au-delà de la fin du trimestre du 65e anniversaire » » ; articles 1er et 2
  sans date, publié le 23 février : le 24. Conforme.
- 20 août 2018 (JORFARTI000037363871), article 13 : « obtient une majoration de 0,75 % par
  trimestre plein de prorogation au-delà de cet âge, dans la limite maximale de 15 %. « La
  majoration s'applique sur le nombre de points acquis par cotisations et rachat, arrêté à
  la date de liquidation » ; publié le 4 septembre, sans date : le 5. Conforme.
- 4 juillet 2025 (JORFARTI000051849616) : « 7° L'article 13 est ainsi modifié : […] le
  nombre : « 0,75 » est remplacé par le nombre : « 1,25 » ; - le nombre : « 15 » est
  remplacé par le nombre : « 25 » » ; publié le 6 juillet, sans date : le 7. Conforme.
- Règlement de 2026 (JORFARTI000054435943 ; LEGIARTI000054437585, en vigueur le 18 juillet
  2026, sans version postérieure) : article 1.1.4, « 1,25 % par trimestre plein de
  prorogation au-delà de cet âge, dans la limite maximale de 25 % ». Conforme.
- N'y touchent pas, lus : 2010 (adresse, article 1.1), mars 2012 (affiliation), 2013
  (invalidité, articles 4.26 et suivants), 2014 (article 3.5), 2019 et 2024 (leur
  « article 13 » est celui des élections, aux statuts généraux), décembre 2025 (« au
  prorata des points effectivement acquis », articles 14 et 17, « en vigueur au 1 er
  janvier 2026 »). Conforme.

**Écart (a), faible : les arrêtés d'avant 2008 ne sont pas nommés.** La note dit le relevé
fait « depuis 1979 », mais ni elle ni la fiche ne nomment un arrêté de la CAVEC d'avant 2008.
Le JO en a six qui touchent son complémentaire, tous au seul Bulletin officiel : 17 juin 1980
(JORFTEXT000000680010, « ART. 52,55,57,58 ET 61 AU REGIME D'ASSURANCE VIEILLESSE
COMPLEMENTAIRE », « CES ARRETES SERONT PUBLIES AU BULLETIN OFFICIEL »), 22 août 1986
(JORFTEXT000000862986, « (ART. 47 ET 55 ANNEXE 2) »), 9 mars 1987 (JORFTEXT000000321565,
« 4EME PARTIE,TITRES XVI (ART. 52) ET XVII (ART. 57 ET 58) »), 23 juillet 1992
(JORFTEXT000000724876, titre et mention seuls), 13 mai 1994 (JORFTEXT000000731984, titre
seul), 27 février 2003 (JORFARTI000001710064, « du régime complémentaire d'assurance
vieillesse (art. 58) […] de la section professionnelle des experts-comptables et des
comptables agréés », « publié intégralement au Bulletin officiel n° 2003-14 »). Les autres
de la période touchent l'allocation vieillesse (14 janvier 1980, 15 avril et 12 juillet
1983, 29 septembre 1993, 7 août 2001, 17 septembre 2002) ou l'invalidité-décès (6 décembre
1988, deux fois ; 26 mars 1998 ; 18 juillet 2006). Ce que la fiche affirme tient (« ses
statuts d'avant, au seul Bulletin officiel ») ; la liste manque à la preuve.

**Écart (b), faible : « un article 3.14 qui existait donc ».** La fiche (`avant_2007`) et la
note (« l'article 3.14 qu'il « rédige », en vigueur avant ») tirent de la formule « est ainsi
rédigé » qu'un article 3.14 existait avant 2008. Deux indices se contredisent : l'arrêté du
22 février 2008 approuve les articles « 3.1, 3.3, 3.4, […] 3.20 » (JORFARTI000018197775),
sans 3.2, ce qui suppose une numérotation en 3.x déjà en place ; mais l'arrêté du 27 février
2003 nomme encore l'« art. 58 » du complémentaire, l'ancienne numérotation, et l'index n'a
aucun arrêté du complémentaire de la CAVEC du 28 février 2003 au 21 février 2008. Le texte
qui a introduit la numérotation en 3.x, et ce que disait son article 3.14, ne sont pas
identifiés. Le point non tranché n'en change pas : la lecture A (rien avant le 2 mars 2008)
et la lecture B (l'article d'avant majorait déjà) restent tenables l'une et l'autre, faute du
texte ; mais la phrase « qui existait donc » dit plus que l'indice.

**Le point non tranché neuf, refait.** Expert-comptable né le 10 mars 1940, âges d'avril
1940, servi par les deux moteurs, sous les deux jeux, à l'identique :
- 67,75 ans, 1er janvier 2008 : 22 676,944501327118 €, « coefficient de majoration 1.1375 »
  (int(2,75 × 4) = 11 trimestres × 1,25 % = 13,75 %). Sans majoration : 22 676,944501 /
  1,1375 = 19 935,775386 € ; majoration : 22 676,944501 − 19 935,775386 = 2 741,169116, soit
  **2 741,17 €** par an. Conforme.
- 67,5 ans, 1er octobre 2007 : 19 185,657428660852 €, sans coefficient. Dix trimestres
  pleins du 10 mars 2005 au 1er octobre 2007 (deux ans, six mois et vingt et un jours) :
  19 185,657429 × 0,125 = 2 398,207179, soit **2 398,21 €**, un plafond puisque seuls les
  points arrêtés au 31 décembre 2005 seraient majorés. Conforme.
- 67,8333 et 67,9167 ans (1er février et 1er mars 2008) : le modèle sert aussi 1,1375
  (22 731,17 € et 22 785,39 €). La fiche dit la fenêtre « du 1er janvier au 1er mars 2008 »,
  et la note « la CAVEC de janvier à mars 2008 » ; ces deux dates n'existent pas au droit
  (statuts de 2008, article 3.15 : « La retraite est liquidée à dater du premier jour du
  trimestre civil suivant la demande »). Conforme ; on notera seulement que l'article 3.15
  invoqué est celui de 2008, et que celui d'avant le 2 mars n'est pas lu.

## 2. La CAVP (section 2 de E14)

**Les arrêtés.** Au titre, de 1995 à 2026 (« pharmac » ou « CAVP », avec « statut »,
« règlement » ou « vieillesse »), puis à plusieurs sections : les seize textes de E14 sont
tous ceux du JO (5 septembre 1997, 21 juin 2002, 27 juin 2006, 27 mars 2007, 11 mai 2009,
23 juin 2011, 24 septembre 2012, 4 juin 2015, 30 novembre 2016, 5 juillet 2017, 3 octobre
2019, 19 juin 2023, 19 décembre 2023, 5 mai 2025, 10 juillet 2026, 21 septembre 2026). Les
décrets n° 2008-1499, n° 2014-1446 et n° 2019-288 ne touchent que les classes de
cotisation (article 2 du décret n° 49-580) ; l'arrêté du 2 octobre 1995 ne nomme pas les
pharmaciens. Conforme.

- 2009 (JORFARTI000020694605, publié le 6 juin 2009) : « major » n'y nomme que les majorations
  de retard, la base (« Article 21 La pension d'assurance vieillesse de base peut être
  majorée ») et les enfants ; article 12 : « Le droit à la retraite définie à l'article 11
  est acquis à l'âge de 65 ans ». Son article 2 abroge les arrêtés du 29 décembre 1948 et du
  1er juin 1950 : ce sont les statuts d'avant 2009, au Bulletin officiel. Conforme.
- 23 juin 2011 (JORFARTI000024270214), article 12 : « La pension de retraite est majorée
  lorsqu'elle est liquidée au-delà de l'âge permettant d'obtenir une retraite à taux plein
  et jusqu'à cet âge augmenté de 3 ans pour les affiliés nés à compter du 1er janvier 1956.
  Cette majoration est égale à 0,5 % par trimestre. De façon transitoire : ― les affiliés
  nés jusqu'au 31 décembre 1952 […] uniquement jusqu'à l'âge permettant d'obtenir une
  retraite entière augmenté d'un an ; ― les affiliés nés en 1953, 1954 et 1955 […] augmenté
  de deux ans. » Ses six articles (JORFARTI000024270207 à 212) ne fixent aucune date, ni
  l'annexe pour l'article 12 (ses seules dates : le 1er janvier 2013, la mensualisation ; le
  1er juillet 2011, les pensions d'orphelins) ; publié le 29 juin : le 30. Conforme.
- N'y touchent pas : 2012 (invalidité-décès, prestations complémentaires), 2015 (rachats,
  capitalisation, l'âge d'ouverture des nés avant 1956), 2016 (prestations), juillet 2017
  et juin 2023 (statuts généraux, commissions), 2019 (article 15, la commission de recours) ;
  décembre 2023 (JORFARTI000048880592) : « 2° L'article 12 est ainsi modifié : a) Au premier
  alinéa, les mots : « et qui a cessé toute activité pharmaceutique non salariée » sont
  supprimés » ; 2025 (JORFARTI000051568256) : son « 8° L'article 12 » est au IV, « les
  statuts du régime invalidité-décès » ; son III (le complémentaire) ne touche ni l'article
  12 ni l'article 15. Conforme.

**La piste de 2011.** Déclarée dans `cavp_minoration_deux_pentes`, `approximations`,
version `statuts_de_2011` : « Le modèle ne sert les deux pentes et la majoration qu'à partir
du 1er janvier 2012, la période de 2009 courant jusqu'au 31 décembre 2011 ; les statuts les
servent dès le 30 juin 2011 (`CAVP_HORS_DU_MODELE`). Dans la lecture du tableau, aucune
pension n'en est changée […] ; la majoration, que les nés depuis le 1er juillet 1951, qui
n'avaient pas soixante-cinq ans. Dans celle de l'article 12, les nés jusqu'en 1946 partis de
65 à 66 ans du 30 juin au 31 décembre 2011 perdent leur majoration (le point non tranché
suivant). » Déjà déclarée, comme E14 le dit. Conforme.

## 3. La CPRN (section 2 de E14)

**Les arrêtés.** Au titre, de 2003 à 2026 (« notaire » ou « CPRN ») : 28 décembre 2004
(JORFTEXT000000424514, nouveaux statuts, titre seul), 27 février 2008 (JORFTEXT000018229442,
l'article 20, les enfants), 16 décembre 2013, 31 mai 2017, 29 novembre 2023, 10 juillet
2026 : les six de E14, et seuls ceux-là (le reste est la caisse des clercs). Les décrets
n° 2004-1142 et n° 2013-1157 modifient le décret n° 49-578 (classes de cotisation,
JORFARTI000028323767 ; entrée en vigueur le 1er janvier 2014, JORFARTI000028323773) ; le
décret n° 2026-1017 du 2 novembre 2026 (cumul emploi-retraite) ne touche pas les statuts.

- 16 décembre 2013 (JORFARTI000028387445) : « L'article 16 est ainsi rédigé : « Si la demande
  de retraite intervient après l'âge du taux plein, un coefficient de majoration est
  appliqué à la pension des notaires ayant continué à exercer et à cotiser dans les
  conditions de l'article 15. « Le coefficient de majoration est fixé à 0,5 % par trimestre
  au-delà de l'âge du taux plein, jusqu'à l'âge de 70 ans. » » ; article 2
  (JORFARTI000028387441) : « Le présent arrêté prend effet au 1er janvier 2014. » Conforme.
- 31 mai 2017 (JORFARTI000034975971), article 23 : « La surcote est fixée à 0,5 % par
  trimestre au-delà de l'âge du taux plein, jusqu'à l'âge de 70 ans » ; articles 1er et 2
  sans date, publié le 21 juin : le 22. Conforme.
- 29 novembre 2023 (JORFARTI000048679350) : « 5° L'article 23 est ainsi modifié : a) Au
  deuxième alinéa, le pourcentage : « 0,5 % » est remplacé par le pourcentage : « 1 % » et
  les mots : « 70 ans » sont remplacés par les mots : « fin d'activité » » ; article 2 :
  « Les dispositions du présent arrêté entrent en vigueur le 1er janvier 2024. » Conforme.
- Règlement de 2026 (LEGIARTI000054437637, en vigueur le 18 juillet 2026), article 9, 1° :
  « La surcote est fixée à 1 % par trimestre au-delà de l'âge du taux plein, jusqu'à l'âge
  de fin d'activité ». Conforme.

L'âge du taux plein, que la fiche ne précise pas pour la CPRN, est écrit au régime
(`data/reference/regimes/cprn_complementaire.yaml`, `age_table: cprn_2014`) d'après
l'article 18 des statuts, que je relis dans l'arrêté de 2017 : « Pour les affiliés nés avant
le 1er janvier 1954 : […] l'âge légal du départ à taux plein est fixé à 65 ans. « Pour les
affiliés nés à compter du 1er janvier 1954 : […] celui visé à l'article L. 161-17-2 du code
de la sécurité sociale différé de vingt-quatre mois et augmenté de cinq ans. » ; et dans
celui de 2023, 3° : « La retraite est attribuée à taux plein à compter de l'âge mentionné au
1° de l'article L. 351-8 du code de la sécurité sociale. » Ce 3° n'est pas cité dans la
version `cprn_2024` ; le modèle en tient compte (né en 1955 : rien au 1er octobre 2023 à
68,5 ans, le taux plein étant à 69 ans ; 1,11 au 1er janvier 2025, onze trimestres depuis
67 ans).

## 4. Le modèle sert-il ce que la fiche dit ? (section 2 de E14)

Les dix-huit versions sont contiguës (chaque borne de fin est la borne de début de la
suivante), et leurs taux sont ceux des textes : CAVEC 1,25 % du 2 mars 2008, 0,75 % du
5 septembre 2018, 1,25 % du 7 juillet 2025, vingt trimestres au plus ; CAVP 0,5 % du 30 juin
2011 ; CPRN 0,5 % du 1er janvier 2014, 1 % du 1er janvier 2024.

Chaque cas de E14 rejoué, dans les deux moteurs, sous les deux jeux (les coefficients
identiques d'un jeu à l'autre) :

| Cas (né le 10 mars) | Date d'effet | Servi | Refait à la main |
|---|---|---|---|
| CAVEC 1950, 68 ans | 1er avril 2018 | 1,1500 | 12 × 1,25 % |
| CAVEC 1950, 68,4167 ans | 1er août 2018 | 1,1625 | 13 × 1,25 % (avant le 5 septembre) |
| CAVEC 1950, 68,5 ans | 1er octobre 2018 | 1,1050 | 14 × 0,75 % |
| CAVEC 1950, 75,5 ans | 1er octobre 2025 | 1,2500 | 20 au plus × 1,25 % |
| CAVEC 1958, 67,5 ans | 1er octobre 2025 | 1,1250 | 10 × 1,25 % |
| CAVEC 1943, 68,75 ans | 1er janvier 2012 | 1,1875 | 15 × 1,25 % |
| CAVEC 1957, 68,25 ans | 1er juillet 2025 | 1,0975 | 13 × 0,75 % (avant le 7 juillet) |
| CAVEC 1957, 68,3333 ans | 1er août 2025 | 1,1625 | 13 × 1,25 % |
| CAVP 1956, 68 ans | 1er avril 2024 | 1,02 | 4 × 0,5 %, depuis 67 ans |
| CAVP 1956, 71 ans | 1er avril 2027 | 1,06 | 12 × 0,5 %, jusqu'à 70 ans |
| CAVP 1953, 70 ans | 1er avril 2023 | 1,04 | 8 × 0,5 %, de 66 à 68 ans |
| CAVP 1952, 68 ans | 1er avril 2020 | 1,02 | 4 × 0,5 %, de 65 à 66 ans |
| CAVP 1951, 68 ans | 1er avril 2019 | rien | né avant le 30 juin 1951 |
| CPRN 1950, 68 ans | 1er avril 2018 | 1,06 | 12 × 0,5 %, depuis 65 ans |
| CPRN 1950, 73 ans | 1er avril 2023 | 1,10 | 20 × 0,5 %, jusqu'à 70 ans |
| CPRN 1955, 71 ans | 1er avril 2026 | 1,16 | 16 × 1 %, depuis 67 ans |
| CPRN 1948, 65,6667 ans | 1er décembre 2013 | rien | avant le 1er janvier 2014 |
| CPRN 1948, 65,75 ans | 1er janvier 2014 | 1,015 | 3 × 0,5 % |
| CPRN 1953, 70,6667 ans | 1er décembre 2023 | 1,10 | 20 × 0,5 %, de 65 à 70 ans |

Tous conformes.

**Candidat neuf, moyen : les trimestres d'exercice de l'année de l'âge, perdus.** Notaire né
le 10 mars 1953 (âges d'avril 1953), au 1er janvier 2024 (70,75 ans) : le modèle sert
« coefficient de majoration 1.1600 », 23 079,344267798482 €, dans les deux moteurs ; à
71 ans, 1,17 ; à 71,25 ans, 1,18. L'âge d'où il compte est celui de
`data/reference/legislation/age_annulation_decote.csv`, « 1953,66.17 » : le 1er juin 2019.
Par l'âge, (70,75 − 66,17) × 4 = 18,32, soit 18 trimestres ; mais
`_trimestres_cotises_apres` (`src/retraite_notionnelle/droit/liquider.py:4794`) ne garde
une année que si `ligne.annee - carriere.annee_naissance >= age` : 2019 − 1953 = 66 < 66,17,
l'année 2019 tombe entière, et ses deux trimestres civils d'exercice après l'âge (juillet à
décembre 2019) avec elle ; restent 2020 à 2023, 16 trimestres, que le `min` retient. Le
texte (« 1 % par trimestre au-delà de l'âge du taux plein, jusqu'à [la] fin d'activité »,
aux notaires « ayant continué à exercer et à cotiser ») en compte 18 si l'âge est celui du
modèle. Écart : 23 079,344268 / 1,16 = 19 895,986438 € de pension sans majoration ;
19 895,986438 × 0,02 = **397,92 € par an** servis en moins. Le même mécanisme vaut pour
toute génération dont l'âge d'où la majoration se compte n'est pas entier en années de
millésime, à la CPRN (`surcote_trimestres_cotises`), et peut-être ailleurs ; il précède
E14, mais sa confrontation « mois par mois (… trimestres cotisés …) » ne l'a pas vu. Non
instruits ici : l'âge du 1° de L. 351-8 des nés en 1953 depuis le 1er septembre 2023
(LEGIARTI000047452736 : « l'âge prévu au premier alinéa de l'article L. 161-17-2 augmenté de
trois années » ; L. 161-17-2, LEGIARTI000047452768, renvoie au décret pour les nés avant
1968, que je n'ai pas lu), d'où « au moins » ; et la limite d'âge d'exercice que les statuts
de 2017 tirent de « l'article 53 de la loi n° 2015-990 », qui borne le cas de 1955 à 71 ans
comme celui-ci.

## 5. Les écarts de R-E14 (section 1 de E14)

**(A) Les douze arrêtés de la Cipav.** Au titre, de 1979 à 2008 (« architect », « cipav »,
« interprofessionnelle de prévoyance »), puis les arrêtés à plusieurs sections : ceux qui
touchent le complémentaire de 1979 sont bien les douze de E14, chacun à ses articles :
7 février 1980 (JORFTEXT000000832498, « (ART. 6, 8 ET 10) ») ; 5 mai 1981
(JORFTEXT000000871027, « (ART. 8,11 ET 17) ») ; 4 mai 1982 (JORFTEXT000000677739, « UNE
MODIFICATION », article non dit, « CET ARRETE SERA INTEGRALEMENT PUBLIE AU BULLETIN
OFFICIEL ») ; 17 juin 1985 (JORFTEXT000000840042, « ART. 4,9,12,13,17,17-BIS ET 21 ») ;
22 août 1986 (« (ART. 11 ANNEXE 1) ») ; 9 mars 1987 (« ANNEXE N0 5,STATUTS DU REGIME DE
RETRAITE COMPLEMENTAIRE: ART. 8,13,17 ET 17-BIS ») ; 13 août 1987 (JORFTEXT000000475761,
titre seul : « DES REGIMES D'ASSURANCE VIEILLESSE ET INVALIDITE-DECES DES ARCHITECTES » —
« assurance vieillesse » n'y dit pas lequel, d'où le « peut-être » de E14, juste) ; 12 mai
2000 (JORFARTI000002418428, « (art. 1er, 4, 4 bis, 11, 12 et 18) ») ; 27 février 2003
(JORFARTI000001710064, « (art. 6) ») ; 29 juillet 2003 (JORFARTI000001531753, « (art. 9, 11,
13, 15, 17 et 17 bis) ») ; 28 décembre 2004 (JORFARTI000002244328, « (art. 7) », « prend
effet le 1er janvier 2005 ») ; 3 octobre 2006 (JORFARTI000002050100). L'article 17, en 1981,
1985, mars 1987 et juillet 2003, peut-être en 1982 et août 1987 : conforme. Les autres
arrêtés de la période touchent l'allocation vieillesse (7 février 1980, second arrêté,
art. 18, 20 et 21 ; 7 avril 1981 ; 12 juin 1985 ; 26 mars 1987 ; 1er septembre 1989 ;
20 avril 1990 ; 9 février et 29 juillet 1993 ; 2 octobre 1995 ; 21 août 1997 ; 1er juin
2001 ; 30 avril 2002) ou l'invalidité-décès (26 février 1985 ; 19 juin 1991 ; 19 mars 1996 ;
26 mars et 10 septembre 1998 ; 16 mai 2000 ; 8 décembre 2006), ou la base et les statuts
généraux (18 mars et 26 mai 2005) ; celui du 17 décembre 2007 modifie l'article 3.8 des
statuts de 2006. La liste de E14 de ceux qui « ne touchent pas » n'est pas exhaustive, mais
elle ne prétend pas l'être. Conforme.

**(B) Les arrêtés du 21 septembre 2026.** JORFARTI000054888279 : a) « Le deuxième alinéa de
l'article 5 », b) « A l'article 25 […] le dernier alinéa », c) « A l'article 28 […] aux 3°
et 7° » du règlement du complémentaire de la CARMF ; d) « Au sixième alinéa de l'article 4
du règlement du régime d'assurance invalidité-décès » ; e) « Au dernier alinéa de l'article
3 du règlement du régime de prestations complémentaires de vieillesse » ; aucun article 2.
Le second (JORFARTI000054888289 et 291) : la CARCDSF, « Au II de l'article 20 » des deux
règlements de prestations complémentaires et « Au quatrième alinéa du I de l'article 21 »
de celui des sages-femmes ; la CAVP, « à l'article 16, les trois occurrences du mot :
« premier » sont remplacées par le mot : « deuxième » ». LEGIARTI000054437738 (18 juillet
au 25 septembre 2026) et LEGIARTI000054890978 (depuis le 25 septembre), comparés mot à mot :
331 « « » et 3 « » » ôtés, et les trois « premier » devenus « deuxième », tous trois à
l'article 16 du règlement du complémentaire, « Montant des droits du conjoint survivant »
(« la durée d'assurance visée au deuxième alinéa de l'article 9 ») ; l'article 12, guillemets
ôtés, est identique mot pour mot (quinze « « » à lui, le seizième de la fenêtre ouvrant
l'article 13). Conforme.

**(C) Les arrêtés de la CARMF de 2018.** Au titre, de 2018 à février 2019, seuls ceux du
20 août (JORFTEXT000037352127) et du 20 décembre 2018 (JORFTEXT000037864937) ; la fiche écrit
« d'août et décembre 2018 » (version de 2017, l'énumération des arrêtés qui n'y touchent
pas). Conforme.

**(D) La CARPIMKO.** Née le 10 mars 1949, les deux moteurs, sous les deux jeux : à
66,5833 ans (1er novembre 2015), 5 298,186050419041 €, sans coefficient ; à 66,75 ans
(1er janvier 2016), 6 529,677536437893 €, « coefficient de majoration 1.2250 » (18 ×
1,25 %). Le début : int((66,75 − d) × 4) = 18 donne d dans ]62 ; 62,25], 62,25 ans par
trimestres depuis 60 ans, le 1er juillet 2011. Trimestres civils entiers de juillet 2011 à
septembre 2015 : 2 + 12 + 3 = 17 (16 sans celui qui commence le jour même).
5 298,186050 × 17 × 0,0125 = 5 298,186050 × 0,2125 = 1 125,864536, soit **1 125,86 €** ;
5 298,186050 × 0,20 = 1 059,637210, soit **1 059,64 €**. Conforme.

## 6. `LUES_AU_DROIT`, le bloc « Reprise » et « Pour la suite »

`tests/test_carte.py` : la fiche est entrée à `LUES_AU_DROIT` (une ligne), et
`test_les_fiches_lues_au_droit_sont_mures` passe sans rien forcer : aucun manque, aucun
écart d'`outils_carte`, aucune rédaction citée encore à rattacher. Chaque caisse y est lue au
droit à chaque date au sens de la liste, avec, déclarées version par version (`supposee`,
`fiabilite`), les périodes dont le texte n'est qu'au Bulletin officiel : la Cipav avant 2008,
la CAVEC avant le 2 mars 2008, la CAVP avant le 7 juin 2009, la CPRN avant 2014, la CARMF,
l'ASV et la CARPIMKO avant leur premier texte lu. À bon droit.

Le bloc « Reprise » de l'action 130 (huit lignes) dit ce que E14 a fait, la date de chaque
coupe, le point neuf de la CAVEC et ses deux montants, les deux montants neufs de la
CARPIMKO, « à relire d'abord : E14 », puis `cotisation_par_classes_liberales` : conforme à
la note. **Écart (c), faible** : « Pour la suite » nomme, au Bulletin officiel, « les
statuts de la CAVEC d'avant 2008 et de la CPRN de 2004, et les arrêtés de la Cipav de 1979 à
2006 », et omet ceux de la CAVP d'avant 2009 (les arrêtés du 29 décembre 1948 et du 1er juin
1950, que l'arrêté du 11 mai 2009, article 2, abroge), que la fiche déclare pourtant
(`avant_2007`). Le bloc « Reprise » les couvre (« CAVP »).

## 7. Tests

`tests/test_carte.py`, `tests/test_sections_liberales.py`, `tests/test_textes.py`,
`tests/test_regle_de_chacun.py` (les seuls fichiers qui nomment la fiche sont les deux
premiers) : 100 verts ; sous `PRESOMPTIONS_DECALEES=1`, 99 verts et un sauté, comme E14.

## Pour E15

Rien à corriger dans les règles ni les valeurs de E14. À écrire, dans la fiche, sans rien
changer de ce que le modèle sert : (a) les six arrêtés de la CAVEC d'avant 2008 (§ 1) ;
(b) « qui existait donc » ramené à ce que les indices disent (§ 1) ; (c) la note de E14,
un récit, ne se récrit pas : le prochain bloc « Reprise » peut nommer la CAVP d'avant 2009. Le candidat de la CPRN (§ 4) est au propriétaire : il
change ce que le modèle sert, et sa classe dépasse la fiche.
