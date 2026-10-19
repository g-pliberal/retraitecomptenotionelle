# Étape 9, suite de la huitième partie : la date d'effet de chaque marche de l'IPP, lue dans le document qui la dit

**La demande.** Vague B du 19 octobre 2026, session 14 de la deuxième salve,
lancée par la session de suivi « Tâches restantes » : le point « la date
d'effet des marches de l'IPP » du bloc « Reprise » de la huitième partie, que
la note « décrets sans marche » décrivait (« Ce qui reste », 4) : l'ancrage
relie le texte cité à sa publication, non à l'article qui dit sa date. Règle
du scénario 1 ; ni les pages, ni la saisie.

**Ce que disent les textes, lus le jour même dans les index JORF et LEGI, mis
à jour le 18 octobre.**

- *Où se lit une date.* Dans un article, une notice ou un titre du JORF — les
  titres anciens la portent : « (A COMPTER DU 01-10-1967) », « DU 01-08 AU
  31-12-1979 », « A PARTIR DU 06-11-1982 » —, ou dans une version d'article
  de LEGI. Des 222 marches de l'IPP, 149 s'y lisent : 147 à leur date, deux à
  une autre, désormais corrigées.
- *Les deux dates fausses.* Le seuil de la contribution de solidarité de mars
  et de septembre 1988, que l'IPP tient du Fonds de solidarité, sans texte, et
  date du 21 et du 23. Ses valeurs sont, au franc près, le douzième du
  traitement de l'indice majoré 250 (68 133 F et 68 808 F par an) à la valeur
  du point que l'article 3 du décret n° 85-1148 fixe « à 27 253 F à compter du
  1er mars 1988 », puis « à 27 523 F à compter du 1er septembre 1988 »
  (LEGIARTI000006454427, LEGIARTI000006454428). Ses autres marches d'avant
  1989 ont un jour qui n'est pas une date : un compteur (4, 6, 7, 8, 10, 13,
  14, 16, 17, 18, 22, 23, 24), quand celles de 1988, que LEGI date, tombent le
  1er du mois.
- *Des dates que dit un autre texte que celui cité.* La fin du veuvage, au
  1er juillet 2004 : la loi n° 2003-775, article 31, V, « applicables à
  compter du 1er juillet 2004 », et non le décret n° 2004-858, dont LEGI date
  la version de D. 242-4 du 25 août. Les seuils de la solidarité de 1989 à
  2004 : l'article 3 du décret n° 85-1148, dont LEGI garde chaque valeur avec
  sa date. La CSG de 2018 et la prise en charge de la cotisation chômage : la
  LFSS pour 2018, article 8, V, A, 1°, et VI (1,45 point « entre le 1er janvier
  et le 30 septembre », 2,40 points « à compter du 1er octobre »). Le taux
  médian de 2019 : la loi n° 2018-1213, article 3, V, « une régularisation pour
  la période courant depuis le 1er janvier 2019 ». La suppression de la
  contribution de solidarité : la loi de finances pour 2018, article 112, IV.
- *Des textes sans date.* L'abattement de la CSG borné à quatre plafonds (LFSS
  pour 2011, article 20) et porté à 1,75 % (LFSS pour 2012, article 17), et la
  cotisation maternité des indépendants de 1995 (décret n° 95-337, « dès la
  date d'entrée en vigueur du présent décret ») : LEGI date leurs versions du
  lendemain ou du jour de la publication, ce qui ne change aucun mois du
  modèle, qui les compte au premier jour.
- *Le décret n° 81-1015*, la maladie des agents publics de novembre 1981 :
  l'index n'en a que la notice ; LEGI date du 14 novembre 1981, jour de sa
  publication, ses versions des articles 1er et 2 du décret n° 67-850, comme
  le décret n° 81-1013 du même jour, « à compter de la date de sa
  publication », pour le salarié du privé ; l'IPP dit le 1er novembre.
- *Ce qui ne se lit pas* (73 marches) : les accords, décisions et circulaires
  de l'Unédic ; 15 seuils du Fonds de solidarité ; des textes que l'index n'a
  pas (les arrêtés de 1971 et 1972, les décrets n° 74-313 et 83-553,
  l'ordonnance n° 84-198, les articles de la CSG de 1991) ou qu'en notice sans
  date (décrets n° 67-850, 75-85, 75-710, 75-1270, 75-1273, 76-894, 76-896,
  78-1213, 81-1015 ; loi n° 82-1) ; le décret n° 85-852, dont la notice fait
  débuter le prélèvement « sur les arrérages servis au 30-09-1985 », sans dire
  de quels mois ; la convention d'assurance chômage de 2006, qui porte le taux
  à 6,48 % « à compter de l'entrée en vigueur de la présente convention »,
  date que l'index, qui en tronque le texte, ne garde pas. Chacune dit sa
  raison dans la garde.

**Ce qui est fait.**

- *La garde* (`scripts/fetch/dates_des_marches.py`, imprimée par
  `ipp_prelevements_sociaux.py` à chaque réécriture, et lançable seule) :
  `DATES_LUES`, le document de l'index et les mots qui disent la date de
  chaque marche lue ; `DATES_NON_LUES`, la raison des autres ;
  `dates_dites`, ce que disent des mots — une date écrite, le lendemain de
  celle que précède « postérieures au » ou « jusqu'au », l'année la plus
  proche d'un jour qui n'a pas la sienne, le 1er janvier d'une année ou d'un
  exercice ; `marches_sans_date`, les marches que ni l'une ni l'autre ne
  nomme. Les mots ont été tirés des index par un script, non recopiés.
- *Les deux corrections* (`CORRECTIONS["solidarite_public"]`), d'une forme
  neuve : une correction dont `lue` ne dit que la date déplace la marche de
  l'IPP, ses taux compris.
- *L'ancrage* : un texte du JORF ne répond à un numéro que s'il le porte en
  tête de son titre, dans ses vingt premiers caractères. La fin de la
  contribution de solidarité s'ancre à la loi
  de finances pour 2018 (JORFTEXT000036339197), et non plus au décret
  n° 2017-1889, « pris en application de l'article 113 de la loi
  n° 2017-1837 », publié avec elle ; aucun autre ancrage ne bouge.
- *La donnée*, refaite : 220 marches de l'IPP, 158 ancrées, 147 datées ; son
  en-tête et la note de la source (`data/sources.yaml`) le disent.
- *Les tests* (`tests/test_prelevements_historiques.py`, cinq de plus) : ce
  que disent des mots ; chaque marche de l'IPP datée ou expliquée, une fois ;
  les mots relus dans l'index, quand il est là ; le seuil de 1988 de part et
  d'autre de ses deux dates ; l'ancrage de 2018. Verts le 19 octobre :
  `-m rapide`, le fichier, les lecteurs de l'histoire (portage du cycle de
  vie, dépense nette, INES, fiche des libéraux, références), les
  confrontations légères.

**Ce que montrent les mesures** (Python, prélèvements hors retraite d'un agent
de l'État en 1988, avant et après) : à 5 650 F et 5 700 F bruts par mois,
548,65 € et 602,95 € dans l'année au lieu de 556,82 € et 611,20 € — un mois
sous le seuil ; à 5 600 F, 5 760 F et 9 000 F, rien ne change.

**Ce qui reste**, une session par point :

1. *Le seuil de la solidarité de 1987 à 1989* : l'IPP n'a pas la marche de
   mars 1989 (le point à 27 798 F, LEGI), ni peut-être celle du barème A du
   1er février 1989 (décret n° 82-1105), l'indice de référence passant de 250
   à 254 entre septembre 1988 et septembre 1989 ; ses valeurs de mai et
   d'août 1987 (5 594 F et 5 621,50 F) ne se déduisent pas de la valeur du
   point que LEGI donne à l'indice 250. Lire la règle du seuil (loi
   n° 82-939, article 4, avant 1998) avant d'écrire une marche.
2. *Deux ancrages faux*, que la date lue ne corrige pas : l'assurance chômage
   de 1993 (un arrêté du même jour sur les pharmaciens inspecteurs) et de 2006
   (l'arrêté des apprentis du secteur public) ; un arrêté s'ancre à son seul
   jour.
3. *Au fac-similé, depuis un poste* : les décrets que l'index n'a qu'en
   notice sans date, le n° 81-1015 d'abord.
4. *Inchangés* : le plafond de 2027 ; la date d'entrée dans la saisie en net,
   à une session des pages ; la limite 5 ante ter (2), en fin d'étape ; au
   propriétaire, la CAMIEG, l'écrêtement du minimum de la SNCF, l'ASPA de
   l'article 23, des décrets au fac-similé.

**Trouvé en chemin.** L'IPP cite, pour le seuil de la solidarité, le décret
n° 93-1317 au 1er août 1994 et le n° 94-599 au 1er décembre, qui datent l'un
le 1er janvier, l'autre le 1er août : les dates sont justes, les références
décalées ; et « 99-941 » au 1er juillet 1999 pour le n° 99-491.
`python scripts/textes.py --inscrire` a inscrit, « à examiner », trois
rédactions de D. 161-2-24-1 et D. 161-2-24-2, qu'une fiche d'une autre
session cite.

**Pour la session des pages** : rien ; le format de la donnée ne change pas,
et GitHub refait le paquet.
