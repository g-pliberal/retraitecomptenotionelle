# Relecture de D2 : le minimum de la cotisation complémentaire, conforme ; trois écarts faibles

File R-D2, le 5 novembre 2026, sur Opus. Relecture indépendante du commit 8a5adc6 (file D,
« D2 », action 177) et de sa note `2026-11-05-minimum-de-la-cotisation-complementaire.md`.
Lecture seule : aucune règle, aucune donnée, aucun test touchés. `veille_droit.py` a été
lancé. L'index LEGI de la DILA a été récupéré dans la session, puis mis à jour au
4 novembre 2026. Chaque texte a été rouvert à la version en vigueur à la date qui compte.
Chaque valeur a été refaite à la main, puis demandée aux deux moteurs.

**Verdict : conforme. Aucun écart grave ni moyen, trois écarts faibles** (§ 5). Les
citations sont exactes. Les bornes sont les dates d'effet des textes. Les deux moteurs
rendent chaque valeur. Le test a été rouge sans la règle, dans chacun des deux moteurs.
Les 930 témoins d'avant sont identiques ; le témoin ajouté rougit la confrontation sans la
règle Python.

## 1. Les sources, rouvertes

- **Décret n° 78-351, article 3, I** (LEGIARTI000006766103, du 19 mars 1978 au
  21 décembre 1985). La citation est exacte : « Toutefois, le montant de cette cotisation
  ne peut être inférieur à celui qui serait dû au titre d'un revenu égal au revenu minimum
  prévu à l'article 2 du décret du 22 janvier 1973 susvisé ». Elle est au I, qui vise les
  assurés « autres que ceux visés aux II et III » : le II porte le forfait de début, le
  III l'aide familial. **Conforme.**
- **Borne de 1979.** Article 12 du même décret (LEGIARTI000006766114) : « Le présent décret
  entrera en vigueur : Pour l'obligation de cotiser, le 1er janvier 1979 ». **Conforme.**
- **Taux de 4,40 %**, pour 1980 et 1984. Article 5, I (LEGIARTI000006766105, jusqu'au
  1er janvier 1985) : « fixé à 4,40 p. 100 ». **Conforme.**
- **D. 635-4**, de 1985 à 2004 (LEGIARTI000006738335 à LEGIARTI000006738338). C'est la même
  phrase, « prévu à l'article D. 633-2 », au premier alinéa. Celui-ci vise les assurés
  « autres que ceux qui sont mentionnés aux troisième et quatrième alinéas ci-après » :
  ceux qui commencent, et les aides familiaux. La rédaction du 24 août 2004
  (LEGIARTI000006738339) ne porte plus que le rachat. **Conforme.**
- **D. 635-2, de 2004 à 2012.** Les trois rédactions LEGIARTI000006738016,
  LEGIARTI000006738017 et LEGIARTI000020032159 portent la même phrase, et « sous réserve
  des dispositions des articles D. 635-7 et D. 635-10 ». D. 635-1 (LEGIARTI000006738013)
  confie à chacune des deux caisses « la gestion d'un régime complémentaire obligatoire ».
  J'ai relu D. 635-7 et D. 635-10 en 2005 et en 2010 : ils fixent les taux (6,5 % pour le
  NRCO), le forfait de début de l'artisan et l'aide familial. Aucun autre minimum.
  **Conforme.** La rédaction de D. 635-2 en vigueur de 1985 à 2004 (LEGIARTI000006738015),
  que la fiche n'a pas lue, ne fait qu'instituer le régime.
- **D. 633-2 jusqu'au 5 avril 2012** (LEGIARTI000006737879). Le texte dit : « 200 fois le
  montant horaire du salaire minimum de croissance en vigueur le 1er janvier de l'année
  considérée ». Il ne porte ni prorata ni durée. **Conforme.**
- **D. 635-2, de 2012 à 2014** (LEGIARTI000025629861, puis LEGIARTI000025263548 au
  1er janvier 2013). La citation sur les quatre-vingt-dix jours et « le dernier alinéa de
  l'article D. 633-2 » est exacte. La rédaction de 2013 n'a plus la réserve de D. 635-7.
  En 2012, D. 635-7 (LEGIARTI000025629857) n'a plus de forfait de début : il fixe le taux
  de 7,2 % et l'aide familial. Le minimum s'applique donc sans réserve de 2012 à 2015.
  **Conforme.**
- **D. 633-2, de 2012 à 2014** (LEGIARTI000025629830, puis LEGIARTI000028435877). La
  phrase des 5,25 % est bien le dernier alinéa : « Le présent alinéa s'applique aux
  travailleurs indépendants dont la durée d'affiliation est au moins égale à
  quatre-vingt-dix jours ». Elle s'applique « sans application du deuxième alinéa de
  l'article D. 612-6 ». **Conforme.**
- **D. 612-6** (LEGIARTI000025629812). La valeur est celle « en vigueur au 1er janvier de
  l'année au titre de laquelle la cotisation annuelle est due ». Son second alinéa ajoute :
  « réduite au prorata de la durée d'affiliation ». **Conforme.**
- **D. 635-2 en 2015** (LEGIARTI000030034575) : « 5,25 % de la valeur du plafond », plafond
  « déterminé conformément au premier alinéa de l'article D. 612-6 ». **Conforme.** En 2016
  (LEGIARTI000031799392), la phrase a disparu. **Conforme.**
- **Le garde-fou**, décret n° 2012-443, article 4, V (LEGIARTI000025628392, puis
  LEGIARTI000030034758 en 2015). En 2015, il oppose 300 fois le Smic à la base et
  « à cet article D. 635-2, à 200 fois cette valeur ». **Conforme.**
- **Le passage au RCI.** D. 635-1 (LEGIARTI000025263544, au 1er janvier 2013) confie à la
  caisse du RSI « le régime complémentaire obligatoire des professions artisanales,
  industrielles et commerciales ». La ligne de 2012 à 2014 nomme les trois codes,
  `rco_artisans nric rci`, et celle de 2015 le seul `rci`. **Conforme.**
- **Le micro-entrepreneur**, L. 133-6-8 (LEGIARTI000020541426 ; LEGIARTI000026798337). Le
  texte dit « Par dérogation » à L. 131-6, puis à L. 131-6-2 : « l'ensemble des
  cotisations et contributions de sécurité sociale ». **Conforme.**

## 2. Les bornes sont les dates d'effet

- **2011 / 2012.** Le décret n° 2012-443 n'a pas de clause générale d'entrée en vigueur :
  ses rédactions courent du 5 avril 2012. Son article 10, II (LEGIARTI000025628404) dit :
  « Les cotisations définitives dues au titre de l'année 2012 par les travailleurs
  indépendants non agricoles qui cessent leur activité au cours de cette même année
  demeurent régies par les dispositions […] dans leur rédaction antérieure ». Il place
  donc, a contrario, les cotisations définitives de 2012 de tous les autres sous la
  rédaction nouvelle. La borne au 1er janvier 2012 est juste. **Conforme.**
- **2014 / 2015.** Décret n° 2014-1637. Son article 15 (LEGIARTI000029982306) modifie
  D. 635-2, et son article 31, I (LEGIARTI000029982292) dit : « Le présent décret
  s'applique aux cotisations et aux contributions de sécurité sociale dues au titre des
  périodes courant à compter du 1er janvier 2015 ». **Conforme.**
- **2015 / 2016.** Décret n° 2015-1856. Son article 1er (LEGIARTI000031791754) modifie
  D. 635-2, et son article 10, I (LEGIARTI000031791772) dit : « dues au titre de la
  période courant à compter du 1er janvier 2016 ». **Conforme.**
- **2003 / 2004.** D. 635-4 porte la phrase jusqu'au 24 août 2004, et D. 635-2 la reprend
  ce jour-là. L'artisan n'a donc aucun trou. Pour le commerçant, la rédaction de 2004 fixe
  le taux « pour l'année 2004 » (étapes 1 et 9, déjà relues). **Conforme.**

## 3. Les valeurs, refaites à la main

Le Smic du 1er janvier vient du barème de la caisse, « Smic horaire »
(`smic_smig_smic_bar.aspx`, version du 11 juin 2026, recopié dans
`tests/test_cnav_baremes.py`) : 12,93 F au 1er décembre 1979, 22,78 F au 1er janvier 1984.
La série `smic_horaire.csv` en est recoupée de 1971 à 2026
(`test_le_smic_de_la_serie_est_celui_de_la_caisse`). Le plafond vient de
`plafond_securite_sociale.csv` (certifié). Les revenus de référence viennent de
`valeurs_point.csv`, les taux des fiches de régime.

| Cas | Assiette minimale | Taux | Référence | Points refaits | D2 |
|---|---|---|---|---|---|
| RCO 1980 | 200 × 1,971166 = 394,23 € (2 586 F) | 4,40 % | 1,003115 | 17,2924 | 17,2924 |
| RCO 1984 | 200 × 3,472789 = 694,56 € (4 556 F) | 4,40 % | 1,544309 | 19,7891 | 19,7891 |
| NRCO 2005 | 200 × 7,61 = 1 522 € | 6,5 % | 14,112 | 7,0103 | 7,0103 |
| NRCO 2007 | 200 × 8,27 = 1 654 € | 6,5 % | 14,648 | 7,3396 | 7,3396 |
| NRCO 2010 | 200 × 8,86 = 1 772 € | 6,5 % | 15,483 | 7,4391 | 7,4391 |
| NRCO 2011 | 200 × 9,00 = 1 800 € | 6,5 % | 15,808 | 7,4013 | 7,4013 |
| RCO 2012 | 5,25 % × 36 372 = 1 909,53 € | 7,2 % | 4,891130 | 28,1093 | 28,1093 |
| RCI 2013 | 5,25 % × 37 032 = 1 944,18 € | 7 % | 17,309 | 7,8625 | 7,8625 |
| RCI 2014 | 5,25 % × 37 548 = 1 971,27 € | 7 % | 17,309 | 7,9721 | 7,9721 |
| RCI 2015 | 5,25 % × 38 040 = 1 997,10 € | 7 % | 17,324 | 8,0696 | 8,0696 |
| RCI 2016 | aucune : 1 000 € | 7 % | 17,324 | 4,0406 | 4,0406 |

Le garde-fou ne joue jamais. Les 5,25 % du plafond restent au-dessus de 200 heures du
Smic chaque année : 1 909,53 € contre 1 844 € en 2012, 1 944,18 € contre 1 886 € en 2013,
1 971,27 € contre 1 906 € en 2014, 1 997,10 € contre 1 922 € en 2015. En 2015, la base
prend 7,70 % × 38 040 = 2 929,08 €. Tout est **conforme**, au centime et à la quatrième
décimale.

## 4. Les deux moteurs, le rouge, ce que la règle emporte

- **Le test, dans les deux moteurs.** `tests/test_independants.py` : 54 tests verts.
  Sous `PRESOMPTIONS_DECALEES=1`, 39 passent et 15 sont sautés. Parmi les sautés, le test
  des deux moteurs : sa fixture saute toujours dans ce mode, car « le portage lit ses
  présomptions dans le paquet ». Ses cas n'ont aucune année présumée.
- **Rouge sans la règle**, vu de deux façons ; données et tests gardés, puis restaurés.
  Avec le code d'avant D2 dans les deux moteurs, il échoue d'abord au portage :
  `('javascript', ('rco_artisans', 1980))`, 4,386 au lieu de 17,292. Avec le seul Python
  d'avant, il échoue à `('python', ('rco_artisans', 1980))`. **Conforme.**
- **Le témoin.** La confrontation du jumeau (`tests/test_pont.py -k refait`) est verte.
  Sans la règle Python, elle rougit de 39 écarts : RCO au départ, 137,74 € lus pour
  271,65 € attendus ; RCI, 4,49 € pour 23,25 €. C'est ce que dit D2. **Conforme.**
- **« Aucun témoin ne bouge. »** `construire_temoins.py --verifier` répond « témoins à
  jour ». Les 930 témoins d'avant le commit sont identiques un à un ; un seul s'ajoute.
  Trois témoins seulement ont un artisan ou un commerçant sous 4 000 € avant 2018 :
  - `dispense_rsa_releve_artisane` déclare 3 000 € par an, au-dessus du minimum chaque
    année. Avant 2009, l'assiette est le revenu de l'avant-dernière année, et ses deux
    premières années sont au forfait de début.
  - `outre_mer_artisane_exoneree` déclare 300 € en 2015 à La Réunion, sous le seuil
    d'exonération. L. 756-3 exonère « du versement de toute cotisation » ; que le minimum
    de la complémentaire tombe avec celui de la base est donc juste.
  - Le témoin neuf, `minimum_complementaire_artisan`.

  **Conforme.**
- **L'année incomplète**, éprouvée de bout en bout par un essai jetable, non commité.
  L'essai liquide à un âge qui coupe l'année au mois du départ ; les deux moteurs rendent
  les mêmes points.
  - En 2015, deux mois d'affiliation ne portent aucun minimum (4,0406 points, ceux des
    1 000 € déclarés).
  - Trois mois portent le minimum entier, sans prorata (8,0696).
  - En 2005, un seul mois porte les 200 heures entières (7,0103), sans durée ni prorata,
    comme D. 633-2 et D. 635-2 le veulent alors.

  **Conforme.**
- **Rien d'autre n'est emporté.** La garde `forfait_de_debut` ne retire le minimum qu'à un
  régime qui a `assiette_de_debut`. Dans les données, seul `rco_artisans` en a un, pour le
  seul artisan, de 1979 à 2011. Aucun minimum de base (D. 642-4 des libéraux, Mayotte)
  n'est touché. Le micro-entrepreneur n'a pas de minimum à la base (`not micro`,
  `carriere.py`), donc pas à la complémentaire. Il en va de même des dispenses et de
  l'exonération des DOM. **Conforme.**
- **Le cliquet.** Le compte des rédactions sans statut fait 9 324, la valeur du cliquet
  (`perimetre.yaml`). `tests/test_textes.py` : 11 tests verts. **Conforme.**

## 5. Ce que le texte ne tranche pas, et les écarts

- **Le minimum face au forfait de début, de 2004 à 2011.** Il est déclaré : fiche
  `assiette_rco_independants` (approximations) et `docs/limites/3-systeme-actuel.md`.
  Le choix du modèle suit le texte d'avant 2004. **Conforme.**
- **Écart 1, faible : l'effet du forfait de début est mal borné.** La fiche le décrit
  ainsi : « l'artisan qui commence en fin d'année, ses deux derniers mois environ ». Or le
  forfait ne passe sous le minimum que si l'année au forfait couvre **un seul mois**. La
  première année, au tiers du plafond, le seuil va de 1,74 mois (2004) à 1,86 mois
  (2006). Deux mois en 2010 font 1 923,33 € contre 1 772 € de minimum, comme la note le
  dit justement. La fiche omet aussi la seconde année, à la moitié du plafond. Celle-ci
  passe sous le minimum quand l'artisan cesse en janvier : le seuil va de 1,16 à
  1,24 mois. À corriger dans le champ `effet`, à la prochaine retouche de la fiche.
- **La cessation en 2012, à la complémentaire.** L'écart à l'article 10, II, est déclaré
  à la fiche, avec son effet (65,53 € d'assiette, ou un minimum de 1 844 € qui manque sous
  quatre-vingt-dix jours), et aux limites. **Conforme.**
- **Écart 2, faible : le pendant de la cessation en 2012, à la base, n'est déclaré
  nulle part où une session le lit d'abord.** D2 le signale comme « candidat » dans sa
  seule note. Il manque à la fiche `assiette_minimale_independants`, aux limites et au
  bloc « Reprise ». Son effet n'est pas nul : sous quatre-vingt-dix jours, le minimum
  d'avant, 200 × 9,22 = 1 844 €, est le montant d'un trimestre de 2012. L'indépendant qui
  cesse en 2012 sous ce montant peut donc perdre un trimestre dans le modèle. À reporter
  au bloc « Reprise » par la file D, puis à déclarer ou à corriger.
- **Écart 3, faible : la preuve des bornes n'est pas écrite.** La note et la fiche datent
  les bornes par les dates des rédactions LEGI. Elles ne citent pas les articles qui en
  fixent l'effet : article 10, II, du décret n° 2012-443, a contrario ; article 31, I, du
  décret n° 2014-1637 ; article 10, I, du décret n° 2015-1856 (§ 2). Les dates coïncident,
  mais l'exigence est de pouvoir les justifier par écrit. À ajouter aux `textes` de la
  fiche.
- **Vu en chemin, hors de D2.**
  - Depuis 2013, D. 635-2 exonère « l'assuré titulaire d'une pension d'invalidité » de
    « toute cotisation d'assurance vieillesse complémentaire » (LEGIARTI000025263548 et
    suivantes). Aucune dispense du modèle ne le porte pour l'artisan ou le commerçant
    (`dispenses_assiette_minimale.yaml` : `pensionne` ne vise que le libéral).
  - Le minimum de la base, donc celui de la complémentaire, tombe quand le revenu déclaré
    est nul (`if cotise and revenu > 0 and not micro`, `carriere.py`, hérité). Le texte
    ne l'exclut pas, et ni la table ni les deux fiches ne le déclarent.

  Deux candidats pour la file D.

## Sources ouvertes dans la session

Index LEGI de la DILA, à jour au 4 novembre 2026 (`dila_cherche.py legi`).
- Décret n° 78-351 : articles 3, 5 et 12.
- D. 635-4 : toutes ses rédactions de 1985 à 2004.
- D. 635-2 : ses rédactions de 1985 à 2017.
- D. 633-2 : de 2006 à 2015.
- D. 612-6 : la rédaction de 2012.
- D. 635-1 : en 2005 et en 2013.
- D. 635-7 : en 2005, 2010 et 2012.
- D. 635-10 : en 2005 et en 2010.
- Décret n° 2012-443 : articles 4 (rédactions de 2012 et de 2015), 5 à 8, 10 et 11.
- Décret n° 2014-1637 : articles 12 à 18, 29 et 31.
- Décret n° 2015-1856 : articles 1er et 10.
- L. 133-6-8 : en 2009 et en 2013.
- L. 756-3, par la table `exoneration_independants_outre_mer.csv`, et L. 756-5 en 2015.

Barème « Smic horaire » de la caisse (version du 11 juin 2026), tel que
`tests/test_cnav_baremes.py` le recopie.
