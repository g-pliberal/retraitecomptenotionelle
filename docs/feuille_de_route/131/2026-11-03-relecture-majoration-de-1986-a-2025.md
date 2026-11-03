# Relecture de la majoration des points de chef de 1952 à 1972 (file K)

File R-K, le 3 novembre 2026 : relecture indépendante des commits 7621be3 (la règle, ses
tests, sa fiche) et 5835f0d (le paquet et la page Méthode) de la session K, note
`2026-11-03-majoration-de-1986-a-2025.md`. Chaque texte a été rouvert ici, sans rien
reprendre de la session ni de mémoire : les index LEGI (à jour au 2 novembre 2026) et JORF
(au 3 novembre 2026) de la DILA, récupérés ; le XML de l'incrément `LEGI_20260115-213622`,
téléchargé le jour sur echanges.dila.gouv.fr (2 798 301 octets, sha256 c48585149e0f545b…),
pour les alinéas, les liens et les titres. Les citations de K — fiche, note, code, tests,
limites — ont été comparées aux textes par un script, fragment par fragment. Les valeurs ont
été refaites par un autre script, qui ne lit que les carrières des témoins, l'indice des prix
(`ipc_annuel.csv`) et le plafond (`plafond_securite_sociale.csv`), sans le moteur. Rien n'a
été modifié : ni règle, ni donnée, ni test, ni fiche.

**Verdict.** **Conforme** : la règle, ses trois bornes de date, chaque citation, les neuf
valeurs des tests et les trois témoins, refaits à la main au centime, et les deux moteurs.
D. 732-76 est déclaré, comme limite et comme question au propriétaire. Aucun écart grave ni
moyen ; cinq écarts **faibles**, de rédaction ou de déclaration (point 7).

## 1. Les textes, à la version en vigueur

| Texte | Identifiant ouvert | Constat |
|---|---|---|
| D. 732-77 | LEGIARTI000006597491 | seule rédaction du 22 avril 2005 au 1er janvier 2026 ; la suivante (LEGIARTI000053365517) traite du versement de rachat. Les six alinéas, mot pour mot, dans le XML ; lien CONCORDANCE « Décret n°86-1084 du 7 octobre 1986 - art. 2 (Ab) » ; publié au JO du 22 avril 2005 (JORFARTI000002065029) : **conforme** |
| D. 732-76 | LEGIARTI000006597490 | seule rédaction du 22 avril 2005 au 1er janvier 2026 ; « majoré de 17 % lorsque [...] au moins égal à seize », sans date de pension ; CONCORDANCE « Décret 81-790 1981-08-18 art. 2 » ; JORFARTI000001910389 : **conforme** |
| Décret n° 86-1084, art. 1er | LEGIARTI000006769404 | du 8 octobre 1986 au 22 avril 2005 ; « majoré, à compter du 1er juillet 1986 » : **conforme** |
| Décret n° 86-1084, art. 2 | LEGIARTI000006769405 | même période ; « prenant effet postérieurement au 30 juin 1986 », le barème, « Dans le premier cas » (3,19), « Dans le second cas » (1,93), l'exclusion des années du décret du 26 juin 1968 : **conforme** |
| Décret n° 86-1084, art. 3 et 4 | LEGIARTI000006769406, LEGIARTI000006769403 | l'article 3, en vigueur, majore le total des points des pensions d'avant juillet 1986 ; l'article 4 n'est que la formule d'exécution. Publié au JO du 8 octobre 1986 (JORFTEXT000000870113) : **conforme** |
| Décret n° 2005-368, art. 3 | LEGIARTI000006240372 | « 65° Le décret n° 81-790 » ; « 78° Le décret n° 86-1084 [...], à l'exception des articles 3 et 4 » : **conforme** |
| Décret n° 81-790 | JORFTEXT000000335107 | au JORF, la notice seule ; LEGI ne porte que des textes qui le visent (décrets n° 86-1084, 94-714, 97-163 et suivants) : « au fac-similé », **conforme** |
| R. 732-67, depuis 2026 | LEGIARTI000053328816 | « mentionnées aux articles D. 732-76 et D. 732-77 » ; « troisième et cinquième alinéas » ; « dans la limite d'une majoration de 45 % s'agissant de la seconde de ces deux formules » (K coupe après « 45 % », sans fausser) : **conforme** |
| R. 732-66, de 2007 à 2017 | LEGIARTI000006597475 | « par la valeur du point de retraite proportionnelle auquel est appliqué le rapport de trente-sept et demi sur » la durée : fonde le rapport de durée du point 6 |
| R. 732-61, de 2007 à 2011 | LEGIARTI000006597469 | « 37,5 années pour l'assuré né avant le 1er janvier 1944 ; - à 38 années pour l'assuré né en 1944 ; - à 38,5 années pour l'assuré né en 1945 » : 152 et 154 trimestres, ceux des valeurs de 2009 |
| Titre de D. 732-76 et D. 732-77 | XML | « Sous-sous-paragraphe 2 : Dispositions relatives au nombre de points acquis au titre de certaines années. » : **conforme** |

Le XML porte deux liens CONCORDANCE que K ne cite pas : « art. D732-46 (T) » sur D. 732-77,
« art. D732-45 (T) » sur D. 732-76. Ce sont les sources de leurs rédactions de 2026 :
D. 732-46 (LEGIARTI000030400074) et D. 732-45 (LEGIARTI000035918454) traitent du versement
de rachat (« En vue d'assurer la neutralité actuarielle du versement [...] », « Le versement
prévu à l'article L. 732-27-1 peut être pris en compte »). Ils ne touchent pas la majoration :
les taire est juste.

**Les citations, par script.** 41 citations distinctes ; 34 se retrouvent mot pour mot dans
les textes de l'index. Des sept autres : trois viennent du XML (deux liens, un titre),
vérifiées dans le XML ; « [ce nombre] » est un crochet d'éditeur ; « décret n° 86-1084,
article 2 » est le libellé du détail du moteur, non une citation ; une est un artefact de la
jointure des lignes du test ; la dernière cite la notice du décret n° 81-790 « à compter du
01-07-1981 », qu'elle écrit en capitales, « A COMPTER DU 01-07-1981 » : l'accent rétabli,
sans plus. **Conforme.**

## 2. Les bornes de date

- **Le début, juillet 1986.** L'article 2 vaut « pour le calcul des retraites
  proportionnelles prenant effet postérieurement au 30 juin 1986 », l'article 1er « à compter
  du 1er juillet 1986 », d'un décret publié le 8 octobre. `MAJORATION_DE_1952_A_1972_DEPUIS`
  vaut juillet 1986, comparé par `<=` : la pension du 1er juillet 1986 est majorée, celle du
  1er juin non, et le test le montre. **Conforme.**
- **Le passage au code, mai 2005.** D. 732-77 est en vigueur dès le 22 avril 2005, jour où
  l'article 2 est abrogé : une pension du 1er avril 2005 relève du décret, une du 1er mai du
  code (`MAJORATION_DE_1952_A_1972_CODIFIEE_DEPUIS`, mai 2005). Seul le nom du texte change au
  détail. Le fond ne diffère que d'une phrase, l'exclusion des années du décret n° 68-571,
  que le modèle n'applique ni avant ni après, déclarée. **Conforme.**
- **La fin, 2025.** La rédaction de 2005 se clôt le 1er janvier 2026 ; les rédactions
  suivantes de D. 732-76 et D. 732-77 (LEGIARTI000053365504, LEGIARTI000053365517) traitent du
  rachat, « aux pensions et aux allocations prenant effet à compter du 1er janvier 2026 », et
  R. 732-67 reprend la majoration « dans leurs rédactions antérieures ».
  `MAJORATION_DE_1952_A_1972_JUSQU_A` vaut janvier 2026, exclu. **Conforme.**
- **Les bornes du barème**, dans `taux_de_majoration_de_1952_a_1972` et
  `tauxDeMajorationDe1952A1972` : rien sous 15 ; 5 % jusqu'à 19,51 compris ; la formule en
  3,19 jusqu'à 27,34 compris (« compris entre 19,51 et 27,34 ») ; au-delà, celle en 1,93,
  plafonnée à 45 %. À la main : 3,19 × 19,51 − 57,23 = 5,0069 ; 3,19 × 27,34 − 57,23 =
  29,9846 ; 1,93 × 27,34 − 22,74 = 30,0262 ; 45 % atteints à 67,74 / 1,93 = 35,0984 points.
  Les nombres de la fiche (5,0069 %, 35,10 points) sont exacts. **Conforme.**

## 3. Les valeurs des tests, refaites à la main

`test_les_points_de_chef_de_1952_a_1972_se_majorent_d_un_seul_taux_avant_2026`, à 6 % de
rendement et 3 € de valeur de service, chaque cotisation × 0,06 / 3 :

| Cas | P | T | Pension des années | Majoration |
|---|---|---|---|---|
| 1960-1969 à 1 000 € (1965 en 600 + 400) ; 1955-1959 hors des années de chef ; 1973-1974 hors de la période | 20 | 63,80 − 57,23 = 6,57 % | 10 × 60 = 600 € | 39,42 € |
| 1952-1953 à 800 € | 16 | 5 % | 96 € | 4,80 € |
| 1960-1961 à 700 € | 14 | 0 | 84 € | 0 |
| 1970-1972 à 1 500 € | 30 | 57,90 − 22,74 = 35,16 % | 270 € | 94,932 € |
| 1972 à 2 000 € | 40 | 54,46 %, plafonnés à 45 % | 120 € | 54 € |
| 1960 à 1 000 €, 1961 à 0 | 20 | 6,57 % | 60 € | 3,942 € |
| aucune année de chef | 0 | 0 | — | 0 |

`test_la_pension_agricole_de_1986_a_2025_majore_les_points_de_chef_de_1952_a_1972`, cinq
années de chef de 1968 à 1972, chacune R × 8,5 % × 6 % de pension ; les coefficients des prix
recalculés depuis `ipc_annuel.csv` :

| Départ | R | Valeur de service | P | T | Majoration |
|---|---|---|---|---|---|
| 1er juin 1986 | 9 000 € | — | — | — | 0 (avant juillet) |
| 1er juillet 1986 | 9 000 € | 4,589 × 0,491 223 = 2,254 224 € | 45,9 / 2,254 224 = 20,3618 | 7,7241 % | 0,077 241 × 229,5 = 17,73 € |
| février 1999 | 12 000 € | 4,589 × 0,649 854 = 2,982 180 € | 61,2 / 2,982 18 = 20,5219 | 8,2349 % | 0,082 349 × 306 = 25,20 € |
| février 2009 | 15 000 € | 4,589 × 0,771 309 × 150 / 152 = 3,492 964 € | 76,5 / 3,492 964 = 21,9012 | 12,6347 % | 0,126 347 × 382,5 = 48,33 € |

Chaque nombre de la note et des tests de K se retrouve. **Conforme.**

## 4. Les trois témoins

Les carrières relues par la saisie du portage (`pont.carrieres_des_saisies`, sur les requêtes
de `simulations.json`) ; pour chaque année de chef de 1952 à 1972, le revenu borné au
plafond × 8,5 % × le coefficient des prix jusqu'à l'année du départ, sommé à la main :

| Témoin | Années | Au plafond | Cotisations | × 6 % | Valeur de service | P | T | Majoration |
|---|---|---|---|---|---|---|---|---|
| né en 1925, février 1989 | 1952-1972, 21 | 1957-1961, 1968-1972 | 15 584,82 € | 935,09 € | 2,473 812 € | 17,9998 | 5 % | 46,75 € |
| né en 1935, février 1999 | 1956-1972, 17 | 1968-1972 | 15 919,67 € | 955,18 € | 2,982 180 € | 18,8409 | 5 % | 47,76 € |
| né en 1945, février 2009 | 1966-1972, 7 | aucune | 9 233,22 € | 553,99 € | 3,539 537 × 150 / 154 = 3,447 601 € | 22,9556 | 15,9985 % | 88,63 €, × 1,2 = 106,36 € |

Les trois montants, et le détail de chaque témoin (« 5.00% pour une moyenne de 18.00 points
par an, décret n° 86-1084, article 2 » ; « 5.00% [...] 18.84 [...] » ; « 16.00% [...] 22.96
[...], D. 732-77 »), sont ceux de K. Le coefficient de majoration de 1,2 du témoin de 1945,
appliqué à toute la proportionnelle après la majoration, comme R. 732-66 l'écrit « avant
application de la majoration prévue à l'article L. 732-25-1 », préexiste à la règle de K et
n'a pas été refait ici. `resumer_temoins.py` donne +0,68 % pour ce témoin, K +0,75 % : les
deux sont justes, l'un sur la pension totale (avec 1 448,48 € de RCO), l'autre sur la pension
de base, 14 248,19 → 14 354,55 €. Rien d'autre ne bouge : 3 témoins sur 930, aux scénarios 1,
3 et 5. **Conforme.**

## 5. Les deux moteurs

- Les tests de K et les deux de 2026 : 4 réussis. Les confrontations du jumeau
  (`test_pont.py -k refait`) : 2 réussies, en 74 secondes.
- Sous `PRESOMPTIONS_DECALEES=1`, les quatre sont sautés par `tests/conftest.py` (« le
  portage lit ses présomptions dans le paquet, que la mesure ne décale pas »). Leur partie
  Python, rejouée par un script sous la mesure (jour de naissance présumé au 1er), passe ; les
  tests déclarent le jour (le 15), il n'y avait rien à décaler. GitHub donne la suite et les
  présomptions vertes sur 5835f0d (`.github/etat_suite.yaml`).
- Le JavaScript et le Python, lus ligne à ligne : mêmes bornes, mêmes années (de chef ou de
  chef à titre secondaire, de 1952 à 1972, cotisation positive), même valeur de service et
  même rapport de durée, même détail ; la seule différence, l'ordre des sommes
  (`somme_ordonnee`, `reduce`), ne déplace aucun témoin. Le nom du barème, écrit
  `retraite_proportionnelle_msa` dans la fiche du régime, est bien lu `msa_proportionnelle`
  au chargement (vérifié pour 1999, 2009 et 2020) : le rapport de durée s'applique.
- Le paquet : sur 7c45287, la tête de `main`, `python scripts/construire_donnees.py` ne
  change rien (`git status` vide). La page Méthode qu'a refaite 5835f0d ne doit rien à la
  règle : ses lignes changées sont celles des séries certifiées (les durées d'échelon de
  l'action 158). **Conforme.**

## 6. Ce que le texte ne tranche pas, et la convention d'avant 1990

**Déclaré**, dans `a_relire` de la fiche `retraite_proportionnelle_msa` : sur combien
d'années compter P ; le taux à 19,51 tout juste ; la place des formules dans la codification ;
les années du décret n° 68-571 ; les pensions d'avant juillet 1986 ; et D. 732-76, en
question au propriétaire, que reprennent la limite (`docs/limites/4-regimes-incomplets.md`),
le bloc « Reprise » et le code. **Conforme.**

**La convention d'avant 1990** est écrite comme telle : à la fiche (« faute du barème d'avant
1990 [...] donne à chaque année les points que vaut le rendement estimé de sa cotisation »),
à la fiche du régime (« C'est la convention des pensions prises depuis 2026 »), au code et à
la limite. Elle est celle des pensions de 2026 : leur code compte aussi chaque année sans
barème par cotisation × rendement / (valeur × 150 / durée requise). Le rapport de durée
s'appuie sur R. 732-66, qui l'applique au point de la proportionnelle ; il pèse : sans lui, le
témoin de 1945 aurait P = 22,36, T = 14,10 % et 93,71 €, au lieu de 106,36 €.

**Les textes ne disent rien d'autre qui la remplace.** R. 732-69, publié en 2005
(JORFARTI000002065027), compte les points des cotisations d'avant la loi n° 90-85 par un
barème « pour les années 1981 et suivantes » et, « pour les années antérieures à 1981 », par
« les dispositions des décrets n° 65-346 du 30 avril 1965, n° 67-570 du 21 juin 1967,
n° 74-443 du 15 mai 1974 et n° 75-97 du 10 février 1975 ». Les années de 1952 à 1972
relèvent de ces quatre décrets : le JORF n'a que les notices des décrets n° 67-570 et 74-443
(le n° 65-346 et le n° 75-97 n'y sont trouvés ni par leur numéro ni par leur date), LEGI n'a l'article 50 du
décret n° 55-753 (les points « déterminé[s] en fonction du revenu ») qu'à partir du
25 octobre 1991. La valeur du point de 1986 à 1989, en francs : deux requêtes au JORF de
1985 à 1990 ne trouvent que le décret n° 90-832, de septembre 1990, qui la nomme sans la
chiffrer. Le barème de 1952 à 1972 reste donc « non vérifié, faute de texte ».

## 7. Les écarts, tous faibles

1. **Deux phrases de la fiche du régime, inexactes à la lettre**
   (`msa_non_salaries.yaml`, période de 1986 à 1989). « Aucun point ne s'acquiert par barème
   avant 1990 » : R. 732-69 en donne un pour 1981 à 1989 et renvoie aux quatre décrets avant ;
   vrai seulement du modèle, qui n'en a pas. « Une même année vaut les mêmes points quelle que
   soit la date du départ » : le rapport 150 / durée requise, que la fiche des règles déclare,
   donne à une même cotisation 172 / 150 fois plus de points pour une pension de 2026 que pour
   une de 1989. La fiche des règles, de son côté, range parmi les décrets du barème le
   n° 68-571, que R. 732-69 ne nomme pas (sa notice : « VALIDATION D'ANNUITES
   SUPPLEMENTAIRES »).
2. **Un identifiant mal attaché.** La fiche écrit « Ses visas citent le décret n° 81-790
   (LEGITEXT000006065220) » : cet identifiant est celui du décret n° 86-1084, dont les visas
   citent le n° 81-790 ; le n° 81-790 n'a pas de texte dans LEGI.
3. **Le 1er juillet 1952, non déclaré.** La période commence au 1er juillet 1952 ; le
   modèle compte 1952 entière, sa cotisation de l'année et une année dans P. Seuls les chefs de
   1952 en sont touchés, dont le témoin de 1925 (P = 18,00, loin des seuils).
4. **L'arrondi, non déclaré.** Avant 2026, ni D. 732-77 ni l'article 2 ne disent l'arrondi
   du taux T ni du nombre de points majorés ; le moteur n'arrondit ni l'un ni l'autre, sans le
   dire, quand R. 732-67 arrondit, depuis 2026, chaque année à l'entier supérieur.
5. **Un commit seul, rouge.** 7621be3 portait le paquet d'avant : la période de 1986 à 1989
   y avait une valeur de service nulle (le diff de 5835f0d sur `moteur/donnees.json` le
   montre), et le portage n'y majorait rien ; K l'a refait 28 minutes plus tard. La suite de
   GitHub n'a de verdict que sur 5835f0d, vert.

Aucune question nouvelle au propriétaire : celle de D. 732-76 demeure.
