# Relecture de M3-ter : le 6° a) de l'Ircantec servi jusqu'au 31 décembre 2003 (file R-M3-ter)

File R-M3-ter, le 5 novembre 2026, sur Opus : relecture indépendante du commit a28adbd
(file M3-ter) et de sa note, `2026-11-05-corrections-de-la-relecture-r-m3-bis.md`, qui
corrige les quatre écarts de R-M3-bis (`2026-11-05-relecture-corrections-r-m3d.md`,
commit 87e0ce8). Chaque texte a été rouvert pendant la session dans l'index de la DILA,
récupéré de la release : LEGI à jour du 2 novembre 2026 (20261102-213929), JORF du
3 novembre (20261103-002311), par `scripts/fetch/dila_cherche.py`. L'index est filtré
par thème.

**Verdict : conforme**, deux écarts **faibles**, sans effet sur les valeurs. La lettre
est servie, dans les deux moteurs, jusqu'à la bonne date. Mais la source de cette date,
l'arrêté du 26 décembre 2003, n'est citée nulle part (point 1). Deux citations du décret
n° 82-628 sont imprécises (point 5).

## 1. Les sources, à la bonne version — conforme, un écart faible

- **L'article 16, version par version.** `dila_cherche.py legi --num 16 --titre "30
  decembre 1970"` en donne douze rédactions, sans trou entre elles :
  LEGIARTI000006381609 (30 septembre 1978 → 31 août 1983), …610 (31 août 1983 →
  2 octobre 1990), …611 (2 octobre 1990 → 1er janvier 2004), …612 (1er janvier 2004 →
  25 septembre 2008). Dans …610 et …611, le texte est mot pour mot : « 6° a) A compter
  du 1er juillet 1982 aux agents visés aux articles L. 351-16 et L. 351-17 du code du
  travail remplissant les conditions fixées par l'article 9, alinéa 2, de l'ordonnance du
  26 mars 1982 susvisée ». Dans …612 : « 6° a) Aux agents et anciens agents admis à faire
  liquider leur retraite au régime général en application de l'article L. 351-1-1 du
  code de la sécurité sociale ». Les citations de la fiche et de la note sont exactes.
- **L'ordonnance n° 82-270, article 9** (LEGIARTI000006275868, du 1er juillet 1982, sans
  terme) : la deuxième phrase, « Toutefois, les personnels visés […] bénéficient, dès le
  1er juillet 1982, du taux plein », n'a pas de terme. La troisième en a un : « En outre,
  à compter du 1er juillet 1982 et jusqu'au 1er avril 1983 ». La note dit vrai.
- **Le décret n° 82-628.** Article 13 (LEGIARTI000006763435), article 14 (…436),
  article 15 (…437) : en vigueur du 23 juillet 1982, sans terme (« 2999-01-01 »). Les
  trois citations de la fiche sont exactes, mot pour mot, y compris la liste des
  articles du code du travail de l'article 15.
- **Le rapport au Président de la République** (LEGIARTI000006759661) : les deux passages
  sont exacts. Ils sont désormais dans l'ordre du texte : les « 150 trimestres »
  viennent au caractère 1 847, les « modalités spécifiques » bien plus loin.
- **R. 351-45**, rédaction du 10 mai 1995 (LEGIARTI000006749450, jusqu'au 1er janvier
  2009) : « 160 trimestres […] applicable aux pensions prenant effet postérieurement au
  31 décembre 2002, quelle que soit la date de naissance de l'assuré » (I) ; puis
  151 trimestres pour 1934, 153 pour 1936, 155 pour 1938, 157 pour 1940 (II). Exact. La
  rédaction d'avant (…449) cesse le 10 mai 1995, avant tout cas du test.
- **Le terme du 31 décembre 2003.** Je l'ai vérifié à la source qui change la rédaction.
  C'est l'arrêté du 26 décembre 2003 (JORFTEXT000000246821), publié au Journal officiel
  du 30 décembre 2003. Son article 3, III (JORFARTI000002450292) : « Le a du 6° du
  paragraphe 1 est rédigé ainsi qu'il suit : « a) Aux agents et anciens agents admis à
  faire liquider leur retraite au régime général en application de l'article L. 351-1-1
  du code de la sécurité sociale ; » ». Son article 7 (JORFARTI000001472523) : « Les
  dispositions du présent arrêté entrent en vigueur le 1er janvier 2004. » Le
  1er janvier 2004 est donc bien la date d'effet de la nouvelle rédaction, non sa date de
  publication (le 30 décembre 2003). Le 6° a) vaut pour une pension qui prend effet au
  plus tard le 31 décembre 2003. La borne de la fiche, `escalier_au_trimestre_1983 :
  [1983-08-31, 2004-01-01]`, est juste. Le quatrième cas du test (1er janvier 2004) la
  vérifie.

**Écart faible : cet arrêté n'est cité nulle part.** Ni la fiche (versions
`escalier_au_trimestre_1983` et `retraite_anticipee_2004`, sources), ni la note, ni le
journal de veille de M3-ter ne le nomment. `grep "246821\|26 décembre 2003"` dans
`coefficient_anticipation_ircantec.yaml` ne trouve rien. Le terme ne tient que de la
date de début de …612 dans LEGI. Il est juste, mais sa preuve écrite manque : l'article 7
qui fixe l'entrée en vigueur, et l'article 3, III qui récrit le 6° a). À verser aux
`textes` des deux versions. Sans effet sur les valeurs.

## 2. Les valeurs attendues, refaites à la main — conforme

Agent contractuel payé deux plafonds, né le 15 janvier. Ses âges se comptent du mois
qui suit sa naissance. Il a quatre trimestres l'année de son entrée (onze mois) et
quatre par année pleine. Les coefficients sont ceux de l'escalier de …611 : « le
coefficient applicable à soixante-deux ans, soit 0,88, est majoré de 0,01 par trimestre
écoulé ». Le plancher est celui du § 2 : « le total des points de retraite ainsi calculé
ne pourra être inférieur à celui qui aurait été obtenu après application du coefficient
d'abattement correspondant à l'âge de l'intéressé ».

| Cas | Calcul refait | Attendu du test |
|---|---|---|
| 1936, dès 25 ans (février 1961), 1999-02-01 | 1961 à 1998 : 38 années, 152 ≥ 150 ; 63 ans ; agent ; …611 : 6° a) | aucun |
| 1938, dès 26 ans (février 1964), 2002-02-01 | 1964 à 2001 : 38 années, 152 ≥ 150 ; 64 ans ; 6° a) | aucun |
| 1940, dès 26 ans (février 1966), 2003-12-01 | 1966 à 2002 : 37 années, 148 ; avec 2003 (onze mois), 151 ou 152 ≥ 150 ; 63 ans 10 mois ; …611 : 6° a) | aucun |
| Le même, 2004-01-01 | …612 : plus de 6° a) ; 152 trimestres, 160 requis (R. 351-45, I) : 8 manquent ; seconde table, 65 − 2 = 63 ans : 0,92 ; âge, 63 ans 11 mois : 23 mois, 7 trimestres écoulés depuis 62 ans : 0,95 ; plancher : 0,95 | 0,95 |

Les « avant » de la note, refaits de même : 1936, 153 requis, 1 manque, 65 − 1/4 ans,
0,88 + 11 × 0,01 = 0,99 ; 1938, 155 requis, 3 manquent, 0,88 + 9 × 0,01 = 0,97, au-dessus
de l'âge (0,92 et 0,96). Exacts.

L'effet déclaré, « jusqu'à huit points », est juste lui aussi. Un agent né en 1940 et
liquidé à 63 ans en 2003 avec 150 trimestres (160 requis) aurait, sans le 6° a), 0,90
par la seconde table et 0,92 à l'âge : 0,92 au lieu de un. **Remarque, sans écart** :
les exemples de l'effet (0,99 ; 0,97) suivent la lecture que le modèle fait du § 2, sur
la durée de la génération. Cette lecture est une approximation déjà déclarée : le § 2
écrit « comprise entre trente-deux ans et demi et trente-sept ans et demi », relu ici
dans …611. Lu à la lettre, le § 2 ne s'ouvrirait plus à 152 trimestres : l'agent aurait
la table des âges, soit 0,92 et 0,96. La borne de huit points tient dans les deux
lectures.

## 3. Les deux moteurs — conforme

- `tests/test_ircantec.py` et `tests/test_ircantec_minoration.py` : 66 réussis, et 66
  sous `PRESOMPTIONS_DECALEES=1`.
- **Le test d'abord, rejoué.** J'ai remis la fiche et le paquet d'avant a28adbd dans
  l'arbre, sans commit. Le test neuf échoue alors : « {'date': '1999-02-01', 'igrante':
  0.99, 'ipacte': 0.99, 'ircantec': 0.99} != {… None …} ». Les deux moteurs rendent
  alors 0,99 ; 0,97 ; 0,95 ; 0,95, les « avant » de la note. Avec la fiche de a28adbd,
  ils rendent aucun, aucun, aucun et 0,95, aux trois régimes.
- **Trois cas témoins de plus,** sous 150 trimestres, que j'ai ajoutés. Le 6° a) ne doit
  pas les toucher, et il ne les touche pas ; les deux moteurs rendent la même valeur,
  avant comme après. Né en 1940, dès 26 ans, à 63 ans en février 2003 : 148 trimestres,
  0,92. Né en 1934, dès 26 ans, à 63 ans en février 1997 : 148 trimestres, 0,97. Né en
  1936, dès 28 ans, à 63 ans en février 1999 : 140 trimestres, 0,92.
- Le code ne change que par ses commentaires : les deux moteurs lisent
  `exoneration_des_agents_de_soixante_trois_ans` dans la version de la date d'effet, et
  le paquet (`moteur/donnees.json`) porte les deux versions changées.

## 4. Ce que le texte ne tranche pas — conforme

- **L'absence de circulaire est dite.** L'approximation des versions
  `structure_financiere_1983` et `escalier_au_trimestre_1983` le déclare : « Ce qui
  trancherait, et que ni l'index de la DILA (JORF, LEGI) ni le dépôt n'ont : une
  circulaire ou une instruction de l'Ircantec de 1983 à 2003 sur le 6° a) ». La note et
  le journal de veille le disent aussi. J'ai relancé les quatre requêtes de M3-ter dans
  le JORF, de 1983 à 2004 : les mêmes résultats, seules les analyses des arrêtés du
  27 janvier et du 26 juillet 1983 portent sur le coefficient. Une cinquième requête,
  `"agents non titulaires" AND ("taux plein" OR "coefficient de reduction" OR
  "coefficients de reduction")`, ne trouve pas de circulaire non plus. Elle trouve
  l'arrêté du 26 décembre 2003 (point 1), et la circulaire du 2 juillet 2003 sur le
  chômage des agents publics (JORFARTI000001860584), qui ne traite pas de ce coefficient.
  Les articles L. 351-16 et L. 351-17 du code du travail manquent toujours à l'index :
  `--num L351-16` et `--num L351-17` ne rendent que le code de la sécurité sociale.
- **La lecture du rapport est écartée par écrit.** La fiche porte « Lecture écartée :
  celle qui fait du 6° a) la seule entrée en vigueur anticipée de l'ordonnance […] que
  seul le rapport au Président de la République fonde […] ; un rapport n'est pas une
  norme ». Elle nomme ce qui trancherait et chiffre l'effet si la caisse avait lu le
  rapport. C'est ce que demandait R-M3-bis.
- L'agent privé d'emploi qu'indemnisent L. 351-16 et L. 351-17 (article 15) est déclaré.
  La déclaration « qui est agent » couvre désormais les trois versions.

## 5. Les écarts faibles de R-M3-bis — corrigés, deux imprécisions

- **L'article 13 du décret n° 82-628 : cité.** Sa citation, exacte, figure dans la
  version `ordonnance_du_26_mars_1982`. Son identifiant figure dans
  `escalier_au_trimestre_1983` et dans `lit`. La déclaration de la femme de 1977 est
  récrite.
- **La citation du rapport : l'ordre est rétabli** (point 1). La note de M3-ter dit à
  juste titre que la note de M3-bis lui faisait dire « quelle durée compte ». Relu : le
  passage des 150 trimestres décrit la réforme de « tous les salariés âgés de soixante
  ans », non ces seuls agents.
- **Le 6° b) dans les fiches de l'IPACTE et de l'IGRANTE : ajouté.** La phrase est
  identique dans les deux fiches (`diff` vide). Elle dit « l'ancien agent de soixante
  ans et de quarante trimestres, inscrit comme demandeur d'emploi au 1er février 1982 et
  au chômage à l'entrée en jouissance de sa pension, du 1er juillet 1982 au 31 mars
  1983 (6° b), que le moteur ne sert pas ». C'est l'article 9, troisième phrase, avec
  l'article 14 du décret.

**Écart faible : deux imprécisions dans la citation du décret n° 82-628.**
- La fiche dit « LEGI n'a de ce décret que ses articles 8, 9 et 13 à 16
  (LEGIARTI000006763432 à 438) ». Or l'index est filtré par thème, et
  LEGIARTI000006763434, qui tombe dans cette plage, n'y est pas (« n'est pas dans
  l'index »). Ce qui est établi : « l'index LEGI du dépôt n'a que ses articles 8, 9 et
  13 à 16 (LEGIARTI000006763432, 433, 435 à 438) ». C'est la forme qu'employait R-M3-bis.
- La version `structure_financiere_1983` sert désormais le 6° a). Pourtant ses `textes`
  ne citent ni l'article 9 de l'ordonnance ni l'article 13 du décret ; seule sa prose
  les nomme. Sans effet : du 1er avril au 30 août 1983, la durée requise est de 150
  trimestres pour toutes les générations de 63 à 65 ans. Le 6° a) y est donc contenu
  dans le 6° c), et le modèle ne rend pas de valeur différente.

**Remarque, sans écart.** M3-ter ajoute à la note de M3-bis, qui est un récit, une ligne
« Renvoi du 5 novembre 2026 ». Cet ajout est daté et n'efface rien. La note du
4 novembre sur la base des libéraux en a déjà un.

## 6. Aucun témoin ne bouge — vérifié

- `construire_temoins.py --verifier` à HEAD (46f2916) rend « témoins à jour ».
- J'ai ensuite remis à `null` le seul paramètre ajouté par M3-ter, dans les versions
  `structure_financiere_1983` et `escalier_au_trimestre_1983` de la fiche et du paquet,
  sans commit. Le test neuf échoue alors, et `--verifier` rend encore « témoins à jour ».
  Aucun témoin de simulation ni rendu de page ne dépend donc du changement. Fiche et
  paquet ont ensuite été restaurés (`git checkout`).
- `data/derive/agregats.json` n'a changé dans aucun commit depuis a28adbd^ : le coût
  agrégé ne bouge pas, comme le dit la note.

## Hors du périmètre, à transmettre

- À la file qui tient la fiche : citer l'arrêté du 26 décembre 2003 (articles 3, III et
  7) aux versions `escalier_au_trimestre_1983` et `retraite_anticipee_2004`. Écrire
  « l'index LEGI du dépôt » et « 432, 433, 435 à 438 ». Joindre l'article 9 et
  l'article 13 aux `textes` de `structure_financiere_1983`.

Sources : LEGI LEGIARTI000006381610, 611, 612, et la liste des douze rédactions de
l'article 16 de l'arrêté du 30 décembre 1970 ;
LEGIARTI000006275868 ; LEGIARTI000006759661 ; LEGIARTI000006763432, 433, 435 à 438,
LEGITEXT000006063841 (décret n° 82-628), LEGIARTI000006763434 absent de l'index ;
LEGIARTI000006749450 et la liste des rédactions de R. 351-45. JORF JORFTEXT000000246821, JORFARTI000002450292,
JORFARTI000001472523 (arrêté du 26 décembre 2003) ; JORFTEXT000000654120, 837384 ;
JORFARTI000001860584 ; les cinq recherches de circulaires de l'Ircantec de 1983 à 2004,
sans résultat.
