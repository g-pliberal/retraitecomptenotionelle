# Étape 9, suite de la huitième partie : les décrets qu'aucune marche ne rejoint, et quatre marches qui manquaient

**La demande.** Vague du 19 octobre 2026, session 18 de la troisième salve,
lancée par la session de suivi « Tâches restantes » : le point « les décrets
qu'aucune marche ne rejoint » du bloc « Reprise » de la huitième partie, que
la septième partie décrivait (`2026-10-10-etape-9-histoire-des-prelevements.md`,
« Ce qui reste », 5) : les chercher pour l'histoire des prélèvements comme
`ipp_taux_cotisation.py` les cherche pour la vieillesse. Règle du scénario 1 ;
ni les pages, ni la saisie.

**Ce que disent les textes, lus le jour même dans les index JORF et LEGI, mis
à jour le 18 octobre.**

- *La requête* — les décrets publiés depuis 1967 dont le titre annonce des
  taux de cotisation et nomme la maladie, le veuvage, les allocations
  familiales, les assurances sociales, les régimes spéciaux, les assurés
  partiellement rattachés au régime général, les retraités ou les
  pensionnés — ramène 166 fiches du JORF, 163 décrets ; les marches en
  citaient 37.
- *Le décret n° 79-650* borne sa majoration, par son titre, « du 01-08 au
  31-12-1979 et du 01-01-1980 au 31-01-1981 ». L'article 2 du décret
  n° 67-803, du 1er janvier 1980 au 14 novembre 1981 (LEGIARTI000006761083),
  laisse au salarié « 4,5 % [...] sur la totalité des rémunérations ». Le
  décret n° 81-1013 en fixe « 5,5 p. 100 en ce qui concerne le salarié »
  (article 1er, LEGIARTI000006762049), « à compter de la date de sa
  publication » (article 6), le 14 novembre 1981. L'IPP tient 5,5 % du
  1er janvier 1980 au 1er juillet 1987.
- *Le décret n° 87-470*, article par article dans LEGI : « à titre
  exceptionnel », « à compter du 1er juillet 1987 et jusqu'au 30 juin 1988 »,
  5,15 % des traitements des fonctionnaires de l'État, des soldes des
  militaires, des ouvriers de l'État et des agents des collectivités
  (articles 1er, 2, 5 et 6), 2,65 % de leurs pensions (articles 7 à 9). Le
  décret n° 88-795 tient ces taux au 1er juillet 1988 : l'IPP et la série lue
  aux textes en sautaient la première année. Son titre ne dit pas
  « maladie » : la requête nomme les retraités pour le voir.
- *Le décret n° 91-615* : 6,05 % des agents de l'État (article 3) et des
  collectivités (article 4), « applicable aux gains, rémunérations,
  traitements ou soldes versés à compter du 1er juillet 1991 » (article 5,
  JORFARTI000001566429) ; l'IPP date celle des collectivités du 1er janvier.
- *L'article 3 du décret n° 67-851*, des militaires, dans sa version du
  30 septembre 1976 (LEGIARTI000006766149) : 2,25 % des pensions servies aux
  retraités militaires, le taux des civils, fixé le même jour par le décret
  n° 76-897.
- *Le décret n° 2020-1689* : la « cotisation d'équilibre pesant sur les
  retraités » des IEG, au régime complémentaire d'assurance maladie que gère
  la CAMIEG, 2,01 % en 2021 et 2022, 2,25 % depuis 2023 ; avant, les décrets
  n° 2008-416, 2014-363 et 2017-989, qu'il abroge et que la requête ne ramène
  pas.

**Ce qui est fait.**

- *La garde* (`scripts/fetch/decrets_des_prelevements.py`, imprimée par
  `ipp_prelevements_sociaux.py` à chaque réécriture de la donnée) : la
  requête ; la jointure — un décret dont une marche cite le numéro, dans son
  texte ou par le texte du Journal officiel de son ancrage — ; et deux listes.
  `DECRETS_SANS_EFFET`, 117 décrets qui ne touchent aucune série, chacun avec
  sa raison, lue dans la notice, les articles ou LEGI : le régime local,
  l'assurance volontaire, les revenus de remplacement, les non-résidents, les
  assurés partiellement rattachés, les détenus, la part de l'employeur, la
  vieillesse, les militaires et les agents des régimes spéciaux en activité,
  que l'histoire prend aux taux du privé ou des fonctionnaires comme la fiche
  de paie, ou le taux qu'une marche porte déjà. `DECRETS_EN_SUSPENS`, 5
  décrets qui touchent une série ou une pension qu'elle prélève, sans qu'elle
  le porte, ou que l'index ne laisse pas lire : les restes ci-dessous.
- *Quatre marches et une date* : la maladie du salarié du privé à 4,5 % au
  1er février 1981 et à 5,5 % au 14 novembre (`CORRECTIONS`, que le script
  applique désormais aux salaires) ; celle des agents de l'État et des
  collectivités à 5,15 % au 1er juillet 1987 ; celle des pensions de la
  fonction publique à 2,65 % le même jour (`maladie_des_pensions.py`) ; celle
  des collectivités à 6,05 % au 1er juillet 1991, et non au 1er janvier. Les
  militaires sont cités à la marche de 1976, au taux qu'elle porte.
- *La donnée*, refaite : 293 marches, 158 des 222 de l'IPP ancrées ; son
  en-tête et la note de la source (`data/sources.yaml`) le disent. Le paquet
  du site est refait.
- *Les tests* (`tests/test_prelevements_historiques.py`, quatre de plus) : la
  garde, quand l'index JORF est là, et ses listes sans redite ni décret que
  la requête ne ramène pas ; la maladie du salarié de 1981, de part et
  d'autre de ses deux dates ; celle de la fonction publique en 1987 ; celle
  des agents en 1991. `-m rapide`, le fichier, les lecteurs de l'histoire
  (portage du cycle de vie, dépense nette, INES, fiche des libéraux), les
  confrontations légères : verts le 19 octobre.

**Ce que montrent les mesures** (Python, scénario 1, convention du dépôt, au
salaire moyen, avant et après) :

- *Un salarié du privé né en 1950*, entré à 21 ans, parti à 62 : 9 098 €
  nets en 1981 au lieu de 9 012 € ; taux de remplacement sur le cycle de
  0,6665 à 0,6663 ; rendement interne inchangé, que le revenu net ne fait pas.
- *Un fonctionnaire de la catégorie active né en 1930*, parti à 55 ans en
  1985 : sa pension paie 2,45 % de maladie en 1987 et 2,65 % en 1988, au lieu
  de 2,25 et 2,45 % ; rendement réel net de 7,232 à 7,231 %.
- *Un fonctionnaire sédentaire né en 1935*, parti à 60 ans : 15 405 € nets en
  1987 au lieu de 15 440 €, 16 221 € en 1988 au lieu de 16 258 €.

**Ce qui reste**, une session par point :

1. *La cotisation des pensionnés des IEG à la CAMIEG*, au propriétaire
   d'abord (ci-dessous) ; puis, s'il la veut, dans l'histoire et sur la fiche
   de paie, avec les décrets de 2008 à 2017.
2. *La cotisation des pensionnés des chemins de fer secondaires avant
   60 ans* (décret n° 50-1448, article 6 ; 2,5 % portés à 2,9 % du
   1er juillet 1987 au 30 juin 1988, décret n° 87-463), que
   `maladie_regimes_speciaux` ne distingue pas de celle d'après : une série de
   plus, sur l'âge du pensionné.
3. *Au fac-similé, depuis un poste* : la réduction du taux maladie de
   l'article 5 du décret n° 67-803, de 1968 à 1977 (décrets n° 68-579 et
   77-677), dont l'index ne dit ni le taux ni les gains ; les taux des
   militaires en activité de 1970 (n° 70-717), sans jumeau civil.
4. *La date d'effet de chaque marche de l'IPP*, que l'ancrage ne vérifie
   pas : il relie le texte cité à sa publication, non à l'article qui dit sa
   date — la marche des collectivités de 1991 avançait de six mois.
5. *Inchangés* : le plafond de 2027 ; la date d'entrée dans la saisie en net,
   à une session des pages ; la limite 5 ante ter (2), en fin d'étape ; au
   propriétaire, l'écrêtement du minimum de la SNCF depuis 2023, l'ASPA de
   l'article 23, les décrets des exploitants de 1980 à 1989, au fac-similé.

**Au propriétaire : la CAMIEG.** Le pensionné des IEG paie, sur sa pension, une
« cotisation d'équilibre » au régime complémentaire d'assurance maladie que
l'article 23, paragraphe 8, du statut national du personnel rend obligatoire,
et que gère la CAMIEG : 2,25 % depuis 2023 (décret n° 2020-1689). Ce n'est
pas l'assurance maladie de base, mais un complément obligatoire. La fiche de
paie laisse la mutuelle d'entreprise d'un salarié, qui n'est « pas du droit
mais de la branche ou de l'accord d'entreprise »
(`prelevements_remuneration.yaml`) ; celui-ci est du droit, par décret. La
question : la pension nette d'un pensionné des IEG perd-elle sa cotisation à
la CAMIEG, comme celle d'un agent de la SNCF perd ses 0,70 % ?

**Trouvé en chemin.** `python scripts/textes.py --inscrire` a inscrit, « à
examiner », les dix-neuf rédactions du décret n° 2011-291, qu'une fiche cite
depuis le minimum de pension de la SNCF, ce matin : la session qui l'a
écrite avait inscrit avant de le citer.
