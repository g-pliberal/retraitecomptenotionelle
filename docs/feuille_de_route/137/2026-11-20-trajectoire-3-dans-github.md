# TRAJECTOiRE 3.3.2, confronté sans poste, puis chaque semaine dans GitHub

**La demande**, le 20 novembre 2026 : TRAJECTOiRE est passé de la version
1.1.2, celle de la confrontation du 5 octobre, à la 3.3.2, publiée ce jour ;
le propriétaire demande que la confrontation tourne dans GitHub plutôt que sur
son poste, à l'écart des envois, et qu'elle prévienne quand une version
nouvelle s'écarte du dépôt là où ils concordaient, ou quand le dépôt s'écarte
d'elle.

**Fait, le 20 novembre 2026.**

- *Ce qui a tourné.* R 4.3.3 d'Ubuntu 24.04 et TRAJECTOiRE 3.3.2 (étiquette
  `v3.3.2`, commit `ce13fe7`), installés à part dans le conteneur de la
  session, puis de même par le workflow. Ses dépendances sont au CRAN, en
  binaires ; `mgcv` vient d'Ubuntu. Les cas types du COR tournent en treize
  secondes.
- *Ce qui est au dépôt.* `scripts/fetch/trajectoire_3.R`, le script R des
  versions 3 : il appelle `lancerCasTypesCor()`, que le paquet exporte
  désormais, et relève par `trace()` les entrées qu'elle donne à
  `calculePension()`. `scripts/confronter_trajectoire.py` écrit les tables,
  lance R, tire le témoin, mesure les écarts avec les fonctions de
  `tests/test_trajectoire.py`, étendues à la CNAVPL, à la complémentaire de
  la CARMF, à l'ASV et aux deux régimes des exploitants agricoles, et compare
  à la référence, `tests/temoins/trajectoire_3/ecarts.json` ; le témoin de la
  3.3.2 est à côté. `.github/workflows/trajectoire.yml` le lance le lundi et à
  la demande, sur la version épinglée et sur la dernière étiquette ; une
  rupture ouvre un ticket. `scripts/fetch/trajectoire.py` ne tournait plus
  depuis que `destinie_2.py` lit les salaires moyens par le pont : réparé, et
  étendu aux cas types 12 et 13.
- *Ce qui n'a pas bougé.* Le témoin d'octobre, son test et le registre
  (`referents.yaml`, qui dit encore la version 1.1.2) : fichiers communs, que
  six chantiers attendaient ce jour-là.
- *Ce que la 3.3.2 montre.* 85 cas, 818 quantités, 541 concordent. La loi du
  30 décembre 2025 y est : l'âge et la durée de la génération 1964 concordent
  désormais sur huit cas types. Les valeurs de service de l'Agirc-Arrco
  concordent partout. Le médecin du COR né en 1960, parti en octobre 2026 :
  base 1 062,62 € par mois au dépôt contre 1 069,12 € ; complémentaire
  1 888,09 € contre 2 210,02 € (l'écart d'avant 1996, en cours de correction) ;
  ASV 1 494,06 € contre 1 438,88 €. L'exploitant agricole : le total à 1 % en
  2022, mais la base et la complémentaire réparties autrement. Trois cas
  types de 1964 partis en juillet 2025 ou en janvier 2026 pour carrière
  longue : TRAJECTOiRE leur demande 170 trimestres, le dépôt 171, la
  suspension ne valant qu'aux pensions d'après le 1er septembre 2026 ; à
  lire au texte. Quatre
  fonctionnaires de 1963 : un tiers de trimestre manquant, une décote au
  dépôt, aucune chez TRAJECTOiRE, la cause d'octobre.
- *Ce qui reste.* Lire au texte l'ASV, la base des libéraux, l'exploitant
  agricole et la carrière longue de 1964 ; mettre le registre à jour ;
  redéclarer les écarts, cause par cause, comme le test d'octobre.
