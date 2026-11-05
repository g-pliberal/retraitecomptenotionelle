# E3-bis : les corrections de la relecture R-E4 (la CARPIMKO, et un chiffre de la CAVOM)

**La demande.** Le 5 novembre 2026, vague 10, la session d'orchestration renvoie à la file E
(tâche E3-bis) ce que la relecture R-E4 (c411f0a, `130/2026-11-05-relecture-r-e4.md`) trouve
dans 0284e76 (`130/2026-11-05-carte-des-fiches-carpimko-lue-au-droit.md`) : une erreur
déclarée non prouvée (grave), une autre prouvée sur une période plus courte (moyen), deux
points non déclarés, et un chiffre de E2 sur la CAVOM (faible) ; puis le bloc « Reprise ».
Consigne : ne pas se fier à R-E4 non plus, rouvrir chaque texte, refaire les montants. Rien du
modèle ne bouge, ni le paquet.

## Ce qui est rouvert, et ce que j'en pense

J'ai rouvert chaque texte que R-E4 cite et rejoué ses cas dans les deux moteurs
(`servi_et_refait`, même requête que E3). Je lui donne raison sur les cinq points ; un point
de plus, ci-dessous, qu'elle relève et que ma première lecture avait aussi manqué.

- **L'arrêté du 20 mai 1987** (JORFTEXT000000844323, publié le 4 juin 1987) : « PORTANT
  APPROBATION DES MODIFICATIONS APPORTEES AUX REGIMES COMPLEMENTAIRES D'ASSURANCE VIEILLESSE
  ET D'INVALIDITE-DECES DE LA SECTION PROFESSIONNELLE DES AUXILIAIRES MEDICAUX » ; l'index
  n'en a que ce titre. Ma recherche de E3, bornée à trente réponses, l'avait manqué, comme
  l'arrêté du 16 décembre 1991 (JORFTEXT000000685179) : « DES REGIMES COMPLEMENTAIRES
  D'ASSURANCE VIEILLESSE (ART. 22) », « APPLICABLES A COMPTER DU 01-01-1992 », au Bulletin
  officiel no 91-50 — l'article 22 seul, sans effet sur les âges. Le second arrêté du 20 mai
  1987 (JORFTEXT000000662545) vise d'autres sections.
- **Les statuts de 2015** (JORFARTI000031255547), relus en entier : l'article 11, 2°, a, sert
  « à taux plein » à qui liquide sa base « sans abattement » ; l'article 12 quater, 1°, « Par
  dérogation aux dispositions de l'article 11 », donne à la « GÉNÉRATION 1955 ET ANTÉRIEURE »
  l'« Age prévu à l'article 11.2 (a) 60 ans » ; le 2° déroge à l'article 12, et ne vise que
  les abattements « en cas de départ anticipé ». Ma lecture de E3 — les 4 % frappent toute
  liquidation avant 65 ans, la durée n'annulant pas l'abattement — s'appuyait sur ce que
  l'article 11, 2°, a, ne nomme que les nés depuis 1961 ; elle n'est pas impossible, mais
  aucun texte ne l'impose. Ma version de 2015 disait d'ailleurs déjà la lecture de R-E4
  (« dès l'âge minimal de la table [...] à qui liquide sa base sans abattement ») : la
  fiche se contredisait.
- **Le D. 161-2-1-9, 5°** (LEGIARTI000025089933, du 31 décembre 2011 au 1er septembre 2023) :
  « Soixante et un ans et sept mois pour les assurés nés en 1954 » ; **L. 643-3, I**
  (LEGIARTI000028498667) : la pension de base « peut être demandée à partir de l'âge prévu au
  premier alinéa de l'article L. 351-1 ».
- **La CAVOM** : l'article 4-2 du décret n° 79-265, rédaction du décret n° 2026-418
  (JORFARTI000054153714), arrête les points « à la deuxième décimale par excès » ; la valeur de
  service de 2026, 3,3745 € (`regimes/cavom_complementaire.yaml`, ligne 121) ; la dérogation
  des plafonds de 2016 à 2019 au II de l'article 3 du décret n° 2015-1875
  (JORFARTI000031740735) ; la note de LEGI, « Conformément à l'article 1 II »
  (LEGIARTI000038427708). Conforme à R-E4.

## Les calculs, refaits

Les valeurs du modèle sont celles des deux moteurs, rejouées le jour même ; les autres,
posées à la main.

- **1985, l'âge seul** : né le 10 mars 1925, entré à 20 ans, à 60 ans le 1er avril 1985 : le
  modèle sert 114,27 € par an, sans coefficient ; l'article 12 de 1984, 0,75 × 114,27 = 85,71
  € : **28,57 € par an de trop**. Entré à 26 ans : 0,75, 85,71 €, comme les statuts.
- **1954, les deux lectures** : né le 10 décembre 1954, entré à 20 ans, à 62 ans le 1er
  janvier 2017 ; le modèle, 1,0375, 5 681,23 €, soit 5 681,23 / 1,0375 = 5 475,89 € sans
  coefficient. L'âge légal de sa base, 61 ans et 7 mois, tombe le 10 juillet 2016 ; les
  trimestres civils entiers d'ajournement jusqu'au 1er janvier 2017 : octobre à décembre,
  un seul (juillet à septembre est entamé). Première lecture : 1,0125, 5 475,89 × 1,0125 =
  5 544,34 €, **136,90 € par an de trop**. Seconde : 0,88, 4 818,78 €, 862,45 €.
- **1959, l'âge du taux plein** : né le 10 novembre 1959, entré à 20 ans, à 67 ans : le
  modèle, 1,25, vingt trimestres, 7 022,19 € ; compté de l'âge de la table, 66 ans et 4 mois,
  le 10 mars 2026, deux trimestres civils entiers (avril à septembre) jusqu'au 1er décembre
  2026, 1,025, 7 022,19 / 1,25 × 1,025 = 5 758,20 € : **1 263,99 € par an** d'une lecture à
  l'autre.
- **La CAVOM** : 0,01 × 3,3745 = 0,033745 €, 0,034 € par an au plus pour chaque cotisation
  annuelle, et non « 0,03 € » ; l'arrondi « par excès » donne plus de points que le modèle,
  qui sert donc moins.

## Ce qui change dans les fiches

- **`carpimko_ages_2015`**, huit versions : `statuts_de_1984` lue jusqu'au 4 juin 1987 ;
  `statuts_de_1987`, supposée, née de l'arrêté du 20 mai 1987 (entrée en vigueur prise au
  lendemain de sa publication), jusqu'au 30 novembre 1996 ; le reste inchangé. L'intitulé,
  la version de 2015 et l'effet ne disent plus que la durée n'annule pas les 4 %.
  Approximations : l'erreur (1) reposée sur le cas de 1985 ; l'erreur (2) récrite en point
  non tranché, ses deux lectures citées, 136,90 € ou 862,45 € ; deux entrées neuves, la
  majoration comptée avant l'âge légal de la base — erreur prouvée dans les deux lectures
  pour les générations 1955 et antérieures de 2015 à 2024, non tranchée ensuite, l'article
  12 quater, 1°, et l'article 4 du règlement annulant l'abattement dès la durée atteinte
  quand l'article 11, 2°, a, et l'article 3, 2), demandent les conditions de la base — et «
  l'âge du taux plein » de l'article 12 ter, non tranché, 1 263,99 €. L'arrêté de 1991 entre
  aux textes sans effet ; l'arrêté de 1987, au « à relire ».
- **`cavom_assiette_2016`** : la borne de l'arrondi des points, 0,034 € par cotisation
  annuelle, et son sens, le modèle servant moins que le texte. La note de E2 n'est pas
  touchée ; le bloc « Reprise » ne portait pas ce chiffre.
- **Le test d'abord** : `NAISSANCES_AU_JOURNAL_OFFICIEL` (`tests/test_sections_liberales.py`)
  reçoit l'arrêté du 20 mai 1987, vu rouge avant la version qui en naît. Les citations des
  deux fiches CARPIMKO, revérifiées par script ; une citation de l'approximation (2) gagne le
  guillemet intérieur de l'article 11 qu'elle omettait. **Le cliquet des textes** descend de
  9 317 à 9 316 rédactions sans statut (`textes/perimetre.yaml`) : une lecture des sources,
  le D. 161-2-1-9 ou L. 643-3 cité par son identifiant, rend « à rattacher » une rédaction
  qui n'avait aucun statut.

## Ce que l'étape laisse

- **Au propriétaire, erreurs de la CARPIMKO déclarées, non corrigées** : (1) de 1984 au 4
  juin 1987, la durée annule une minoration que les statuts font de l'âge seul (28,57 € par
  an dans le cas posé) ; (2) de 2015 à 2024, pour les générations 1955 et antérieures, la
  majoration comptée avant l'âge légal de la base (136,90 €) ; (3) la date d'effet au mois,
  non au trimestre civil (475,50 €, un mois). Non tranchés : les 4 % par année quand la durée
  est atteinte (136,90 € ou 862,45 €), l'âge d'où la majoration se compte (1 263,99 €), la
  majoration avant l'âge légal de la base pour les générations suivantes. Un exemple de la
  caisse — une pension d'un assuré né avant 1956, prise de 2016 à 2023 avec sa durée —
  trancherait le premier.
- **Au seul Bulletin officiel, ou à la caisse** : le texte de l'arrêté du 20 mai 1987, en plus
  de celui du 20 novembre 1996.
- **Une leçon de méthode** : une recherche bornée (`--limite`) qui s'arrête pleine n'a pas tout
  vu ; `--compter` d'abord, comme `docs/veille_droit.md` le dit.
