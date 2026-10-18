# Étape 9, huitième partie : la maladie des pensions des exploitants et des régimes spéciaux, lue aux textes

**Reprise, au 18 octobre 2026.** Fait : la cotisation maladie des pensions
de tous les régimes de base calculés, sauf la SEITA, le port de Strasbourg,
les marins, les cultes et les assemblées ; celle de la SNCF et des mines au
site ; la réversion de la SNCF et son minimum ; la fiche de paie des libéraux
et l'indemnité de chaque famille ; la date d'entrée dans la fiche de paie, au
modèle et au portage. Reste, une session par point : le minimum de pension de
l'agent ; le plafond de 2027 ; la date d'entrée dans la saisie en net, à une
session des pages ; la limite 5 ante ter (2), en fin d'étape ; les décrets
qu'aucune marche ne rejoint. Au propriétaire : l'ASPA de l'article 23 ; les
décrets des exploitants de 1980 à 1989. Détail : note « date d'entrée ».

**La demande.** Le propriétaire, le 13 octobre 2026 : « Action 138, étape 9,
histoire des prélèvements : la maladie des pensions des exploitants d'avant
1997 et des régimes spéciaux » — le point 1 et le point 2 de « Ce qui reste »
de la septième partie. En parallèle, l'action 152 tenait `castypes.py`,
`cas_types_csp.yaml` et `grille_large.py`, l'action 147 `cout.py`, une autre
session les pages : rien n'y est écrit.

**Ce que disent les textes, lus le jour même dans les index de la DILA.**

- *Les exploitants agricoles.* Le décret annuel du financement de leur
  protection sociale fixe la cotisation de leurs retraités : 2,8 % de leur
  pension de base pour la part technique, 1 % pour la part complémentaire, en
  1990 (n° 90-765, art. 7 et 9), 1991, 1992, 1994, 1995 et 1996 ; 1,8 % et
  1 % en 1997 (n° 97-140), contre un point de CSG ; les seuls non-résidents en
  1998 (n° 97-1252, art. 7). L'index n'a qu'en notice ceux de 1980 à 1989 et
  celui de 1993 (n° 93-1153), dont la notice ne chiffre pas les retraités. La
  cotisation est réduite de 20 % pour un retraité soigné par un autre régime.
- *Les régimes spéciaux placés sous le régime général pour la maladie*
  (L. 711-2) : 1,5 % des pensions depuis le décret n° 80-598 du 30 juillet
  1980, que LEGI garde, abrogé et codifié en R. 711-8 ; 1,9 % au 1er juillet
  1987 (n° 87-466, temporaire, reconduit par le n° 88-789) ; D. 711-3 en 1991
  (n° 91-613) ; 2,85 % au 1er août 1996 (n° 96-680), 1,85 % au 1er janvier
  1997 et 2,80 % au 1er juillet (n° 96-1151), quand le décret n° 96-680
  prévoyait 3,80 % ; plus rien en 1998 que 1 % des complémentaires
  (n° 97-1249). La notice du décret n° 96-680 nomme ceux qu'elle vise : les IEG,
  l'Opéra de Paris, la Comédie-Française et les chemins de fer secondaires
  passé 60 ans — avant, ces derniers paient 2,5 %, puis 2,9 % en 1987 (décret
  n° 50-1448, art. 6).
- *Les IEG* : 1,5 % depuis le décret n° 80-916 du 20 novembre 1980, 1,9 % en
  1987, puis D. 711-3, que leur statut leur applique depuis le 1er juillet
  1991 (n° 91-613, art. 9) ; leurs pensions étant payées par trimestre et
  d'avance, le relèvement de 1996 prend effet au 1er octobre (notice).
- *Le décret n° 91-613 du 28 juin 1991*, qui chiffre au 1er juillet 1991,
  régime par régime, ce que les conseils de la SNCF, de la RATP et de la
  Banque de France fixaient jusque-là : la SNCF, 4,50 % de la pension sous un premier
  plafond que fixe son conseil, 3,60 % puis 2,25 % au-delà (109 040 F et
  163 560 F par an en 1996, selon la notice du n° 96-680) ; la RATP, 1,65 %
  dans la limite du plafond de la sécurité sociale ; la Banque de France,
  2,65 % ; les clercs de notaires, 2,65 % ; les mines, 3,4 % ; la CCI de Paris,
  2,45 %. Puis les décrets n° 96-471, 96-680 et 96-1151, et le n° 97-1249,
  qui supprime tout en 1998, sauf à la SNCF, 0,70 % sous le premier plafond,
  et aux mines, 0,50 % : deux cotisations toujours en vigueur, la première
  dans le décret n° 2007-1056 (art. 7, IV), sous 5 128 € par trimestre depuis
  le décret n° 2010-1362, la seconde dans l'article 91 du décret n° 46-2769.
- *Les clercs de notaires* : 1,5 % depuis le décret n° 80-600, 2,25 % en 1986
  (n° 85-1093), 2,65 % en 1987 (n° 87-467, puis 88-791), lus dans LEGI.
- *Les mines* : 5 % en 1962, un autre taux en 1972, deux arrêtés que l'index
  n'a qu'en notice ; un relèvement « à titre exceptionnel et temporaire » au
  1er juillet 1987, à 3 % selon l'article de LEGI, à 3,4 % selon la notice du
  JORF ; 3,4 % au 1er juillet 1988, où les deux s'accordent.

**Ce qui est fait.**

- *Neuf séries lues aux textes*, dans `scripts/fetch/maladie_des_pensions.py`,
  que `ipp_prelevements_sociaux.py` importe : celle de la fonction publique,
  qui y passe, et huit nouvelles — les exploitants, les régimes spéciaux
  placés sous le régime général, les IEG, la SNCF, la RATP, la Banque de
  France, les clercs de notaires et les mines ; 44 marches, dont 39 nouvelles,
  chacune liée à son texte au Journal officiel et portant les mots qu'un test
  relit dans l'index. Une série naît à sa première marche : rien n'est
  prélevé avant ce qui n'est pas lu.
- *Trois conventions*, celles de toute l'histoire des pensions et que le module
  dit : le taux de la première tranche, ou sous le plafond ; le taux plein,
  sans les exonérations des non-imposables ni la réduction de l'exploitant
  soigné ailleurs ; la date des pensions dues, sauf quand le texte en dit une
  autre.
- *La donnée*, refaite : 286 marches, 39 de plus, et `regimes_des_pensions`
  donne à chaque série ses régimes ; les barèmes de l'IPP n'ont pas bougé
  depuis le 11 octobre. Elle passe 50 000 octets (54 448) : elle se lit par
  fenêtres.
- *Le modèle* ne change pas de code : `_parts_assujetties` et
  `taux_pension` lisent les nouvelles séries comme les anciennes.
- *Les tests* (`tests/test_prelevements_historiques.py`, quatre cas de plus) :
  les marches de chaque série ; la pension d'un agent de la SNCF de 1990, qui
  paie encore 0,70 % ; la donnée égale au module ; chaque marche relue dans
  l'index.

**Ce que montrent les mesures** (cas simples au salaire moyen, scénario 1,
convention du dépôt, rendement interne réel net et taux de remplacement sur
le cycle, avant et après) :

- *Un agent de la SNCF* parti à 55 ans en 1990 : de 6,067 à 5,981 %, de 0,756
  à 0,743 ; parti en 1995 : de 4,958 à 4,901 %. Né en 1965, parti en 2022 :
  de 1,487 à 1,462 %, par les 0,70 % qui courent toujours, que les cinq
  systèmes notionnels paient aussi.
- *Les autres*, partis en 1985 ou 1990 : l'IEG de 6,252 à 6,211 %, la RATP de
  6,068 à 6,039 %, le mineur de 3,420 à 3,351 %, le clerc de notaire parti en
  1985 de 5,711 à 5,639 %, l'Opéra de 6,101 à 6,049 %, la Banque de France de
  6,667 à 6,638 %. L'exploitant parti en 1990, de 2,23 à 2,16 % : son revenu
  net ne se calcule pas, sa pension nette si.
- *La convention de la première tranche* : en 1996, la pension de l'agent de
  la SNCF parti en 1990 (16 459 €) est sous le premier plafond (16 623 €) ;
  en 2026, au-dessus (25 282 € pour 20 512 €), où le dépôt prélève 0,70 % de
  tout quand le texte n'en prend que 0,57 %.

**Ce qui reste** de l'histoire des prélèvements, dans l'ordre :

1. *La maladie des pensions de la SNCF et des mines sur la fiche de paie du
   site* : 0,70 % de la pension sous 5 128 € par trimestre, 0,50 % de celle
   des mines, que `prelevements_remuneration.yaml`, `contexte.py` et son
   jumeau ne prélèvent pas — un écart sur la pension nette affichée, que
   `test_la_pension_d_un_agent_sncf_paie_encore_sa_maladie` tient jusque-là.
   Avec elle, le plafond de la SNCF dans l'histoire, connu depuis 2010.
2. *Au propriétaire, au fac-similé du Journal officiel* : les décrets annuels
   des exploitants de 1980 à 1989 (n° 80-272, 82-396, 83-664, 84-585,
   85-735, 86-596, 87-612, 88-688, 89-510, et celui de 1981) et de 1993
   (n° 93-1153) ; l'arrêté du 27 octobre 1972 et celui du 30 juin 1987 des
   mines.
3. *Ce que les textes ne disent pas* : les taux des conseils de la SNCF, de la
   RATP et de la Banque de France avant 1991 ; les plafonds de la SNCF de 1991
   à 2010, hors 1996 ; les pensions de la SEITA, du port de Strasbourg, des
   marins, des cultes, des assemblées et du Conseil économique, social et
   environnemental, dont la maladie n'est pas lue.
4. *Inchangés*, de la septième partie : la limite 5 ante ter (2), à récrire à
   la fin de l'étape, qui dira les régimes spéciaux ; la fiche de paie de
   l'avocat et du libéral ; les décrets qu'aucune marche ne rejoint et le
   plafond de la fonction publique.
