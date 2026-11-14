# Les corrections décidées par le propriétaire le 13 novembre 2026 : la file

Le 13 novembre 2026, la liste des erreurs déclarées et non corrigées des caisses des
libéraux exposée (note `2026-11-13-relecture-asv-medecins-points.md`, § 3), le propriétaire
a répondu : « Ouvre une session pour chaque erreur et corrige ». Cette note est la file :
une ligne par erreur, les plus lourdes d'abord, une session par ligne.

**Règles de la file.** Une seule session à la fois sur le modèle (`CLAUDE.md`, « Plusieurs
sessions en parallèle ») : les lignes se traitent l'une après l'autre, dans l'ordre. Une
session d'aiguillage ouvre chaque session de correction et attend son compte rendu avant
d'ouvrir la suivante. La session qui corrige coche sa ligne (`- [x]`) et y ajoute une
phrase : ce qui est corrigé, ou « limite déclarée » si le texte, relu, ne tranche pas.
Chaque correction suit le test d'abord et la veille du droit, sur Fable 5.2.

**Depuis le 14 novembre 2026, sans attendre GitHub.** Le propriétaire l'a décidé ce jour
(« Applique le point 1 », note `135/2026-11-14-correction-sans-attendre-le-verdict.md`) :
la session qui corrige rend compte dès son envoi sur `main`, sa suite rapide et les tests
de sa zone verts, sans attendre le verdict de la suite complète, et la session
d'aiguillage ouvre la suivante aussitôt. Chaque session lit ce verdict à son ouverture,
puis avant son envoi (`.github/etat_suite.yaml` sur `origin/main`) : rouge, elle répare
avant tout. La dernière ligne de la file attend, elle, le verdict de son envoi.

**Depuis le 14 novembre 2026, deux files de front.** Le propriétaire l'a décidé ce jour
(« Deux files de front », même note) : pour cette file seulement, deux sessions corrigent
le modèle en même temps, une par file. La file A tient les lignes 13 à 20 (les médecins,
la Cipav, la CARPIMKO), la file B les lignes 21 à 30 (la CARCDSF, la CAVAMAC) ; dans
chacune, les lignes se suivent une à une, et une file vidée prend la dernière ligne non
ouverte de l'autre. Les deux files écrivent souvent au même endroit du catalogue des
régimes : quand `pousser.sh` refuse un conflit sur une source, la session rebase à la
main sur `origin/main`, garde les deux ajouts, refait ce que les scripts fabriquent,
relance ses tests, puis renvoie. Le bloc « Reprise » de l'action 130 ne se récrit plus
ligne à ligne : la file dit seule où elle en est. Un rouge de GitHub, la première session
qui le lit le répare, après avoir vérifié qu'un commit plus récent ne le répare pas déjà.

**Hors de la file**, faute de décision : les points que le texte ne tranche pas (la Cipav
en 2007 et ses anciens de la caisse des géomètres, la CAVEC, quatre à la CARMF, d'autres à
la CPRN, la CAVP, la CARPIMKO et la CAVOM), qui restent des limites déclarées ; la CRPNPAC
avant cinquante ans et ses vingt annuités ; la forme de la fiche du décret n° 2026-418.

Les notes citées sont dans ce dossier ; les montants, par an, aux cas posés.

## La file

- [x] 1. **CAVOM, l'inapte de 2016 à 2024** : le modèle le minore à 62 ans, le texte le
  sert sans minoration (4 521,49 € en moins). Note
  `2026-11-05-carte-des-fiches-cavom-lue-au-droit.md`. Corrigé le 13 novembre 2026 :
  l'inapte est servi sans coefficient dès 62 ans pour une pension de 2016 à 2024, dans les
  deux moteurs (18 085,96 € au lieu de 13 564,47 € au cas posé) ; note
  `2026-11-13-correction-cavom-inapte-2016-2024.md`.
- [x] 2. **CAVOM, l'inapte depuis 2025** : le modèle lui refuse 62 ans, le règlement
  l'ouvre (six mois de pension, 8 317,99 €). Même note. Corrigé le 13 novembre 2026 :
  l'inapte né depuis 1965 part à 62 ans, avec le coefficient de son âge, pour une pension
  depuis 2025, dans les deux moteurs (servi le 1er avril 2027 au lieu du 1er octobre au
  cas posé) ; note `2026-11-13-correction-cavom-inapte-depuis-2025.md`.
- [x] 3. **CPRN, le passage de 2024** : né en 1961, parti en 2023, servi en avril 2025
  quand les statuts de 2024 ouvrent au 1er janvier 2024 (16 999,67 €, puis 1 079,34 € de
  trop). Fiches `cprn_ages_decote_enfants` et `liquidation_regime_par_regime` ; note
  `2026-11-05-carte-des-fiches-cprn-lue-au-droit.md`. Corrigé le 13 novembre 2026 : l'âge
  d'une pension que sa date sépare du départ déclaré se lit dans les règles de chaque
  mois, dans les deux moteurs (servi le 1er janvier 2024 au lieu du 1er avril 2025 au cas
  posé, 13 164,74 € par an de 2024) ; note `2026-11-13-correction-cprn-passage-de-2024.md`.
- [x] 4. **CARCDSF, la réversion non servie** (4 147,36 € et 5 654,21 €). Fiche
  `carcdsf_minoration_age_seul` ; note `2026-11-05-carte-des-fiches-carcdsf-lue-au-droit.md`.
  Corrigé le 14 novembre 2026 : 60 % de la retraite complémentaire au conjoint de 65 ans,
  marié depuis deux ans sauf enfant, pour un décès depuis le 11 octobre 2007, dans les deux
  moteurs (4 147,36 € et 5 654,21 € par an aux cas posés, au lieu de rien) ; fiche
  `reversion_carcdsf` ; note `2026-11-14-correction-carcdsf-reversion.md`.
- [x] 5. **CARMF, les deux premières années d'exercice** : dispensées sans points depuis
  le 1er juillet 2026, le modèle en donne (2 284,25 € de trop). Note
  `2026-11-06-e10-decret-2026-418.md`. Corrigé le 14 novembre 2026 : le médecin installé
  avant 40 ans ne cotise ni n'acquiert ses deux premières années, pour les cotisations
  de 2027 et d'après, dans les deux moteurs, au scénario 1 et au compte (51 417,01 € par
  an au lieu de 53 701,26 € au cas posé) ; l'année 2026 et la lecture des vingt-quatre
  mois restent des limites déclarées ; note
  `2026-11-14-correction-carmf-deux-premieres-annees.md`.
- [x] 6. **CARCDSF, la part proportionnelle des deux premières années**, dispensée depuis
  le 1er juillet 2026 (1 528,23 € de trop). Même note. Corrigé le 14 novembre 2026 : le
  nouvel affilié ne cotise ni n'acquiert la part proportionnelle de ses deux premières
  années civiles, le forfait et ses six points restant dus, dans les deux moteurs, au
  scénario 1 et au compte (50 630,17 € par an au lieu de 52 158,40 € au cas posé) ; les
  statuts de 2011, relus, écrivaient déjà la dispense, et la correction vaut pour les
  cotisations de 2012 et d'après ; l'année 2011 et la dispense du forfait sur demande
  restent des limites déclarées ; note
  `2026-11-14-correction-carcdsf-deux-premieres-annees.md`.
- [x] 7. **CARMF, l'exemption passé 75 ans**, sans points depuis le 1er juillet 2026 (au
  moins 300,22 € de trop). Même note. Corrigé le 14 novembre 2026 : le médecin qui
  continue d'exercer ne cotise ni n'acquiert les années civiles d'après celle de ses
  75 ans, pour les cotisations de 2027 et d'après, dans les deux moteurs, au scénario 1
  et au compte (18 595,38 € par an au lieu de 18 895,60 € au cas posé) ; le second
  semestre de l'année d'un anniversaire tombé au premier, l'année 2026 et la cotisation
  volontaire restent des limites déclarées ; note
  `2026-11-14-correction-carmf-exemption-passe-75-ans.md`.
- [x] 8. **ASV des médecins, la valeur de service** : fixée par les textes, non portée
  aux prix (1 967,02 € en moins en 2002, 273,50 € de trop en 2024, 242,76 € en 2026). La
  session reprend aussi dans la fiche `asv_medecins_points` les écarts (c) à (g) de la
  note `2026-11-13-relecture-asv-medecins-points.md`. Corrigé le 14 novembre 2026 : le
  point vaut ce que le texte fixe pour l'exercice de la date d'effet, de 1999 à 2026,
  dans les deux moteurs (13 676,54 € au lieu de 11 709,34 € en 2002, 13 661,11 € au lieu
  de 13 934,47 € en 2024, 13 863,87 € au lieu de 14 106,48 € en 2026, aux cas posés) ; le
  premier semestre de 2012, les pensions d'avant 1999 et la valeur d'après 2026 restent
  des limites déclarées ; les écarts (c) à (g) sont repris dans la fiche ; note
  `2026-11-14-correction-asv-medecins-valeur-de-service.md`.
- [x] 9. **ASV des médecins, la cotisation d'avant 2012**, portée au tiers : le médecin
  paie N consultations, les caisses le double (2 400 € par an de moins au compte en 2004) ;
  avec le taux d'appel de l'article 6 et la cotisation de 1994. Même note, écarts (a) à (c).
  Corrigé le 14 novembre 2026 : la fiche du régime porte la cotisation du médecin que
  fixent D. 645-2 et l'article 6 du décret n° 72-968, de 1972 à 2011, et les caisses y
  ajoutent le double, dans les deux moteurs (1 200 € au lieu de 400 € pour le médecin en
  2004, 3 600 € au lieu de 1 200 € au compte, au cas posé) ; aucune pension du droit
  actuel ne change ; le tarif de la consultation, que la fiche porte par les prix, les
  caisses en 1993 et au premier semestre de 1994, l'année 1981 et les années d'avant
  restent des limites déclarées ; note
  `2026-11-14-correction-asv-medecins-cotisation-avant-2012.md`.
- [x] 10. **CAVAMAC, la majoration du second semestre 2011** (1 332,33 € en moins). Note
  `2026-11-06-fiches-communes-des-sections-lues-au-droit.md`. Corrigé le 14 novembre
  2026 : les statuts de 2011 sont servis aux pensions qui prennent effet depuis le
  1er juillet 2011, et non depuis 2012, dans les deux moteurs, par les données du régime
  (1 332,33 € par an de majoration pour trois enfants au cas posé, au lieu de rien) ; la
  majoration de 5 % par année différée du même semestre, que la fiche
  `cavamac_minoration_age_seul` déclarait, est corrigée du même geste ; les statuts
  d'avant le 1er juillet 2011, non lus, restent une limite déclarée ; note
  `2026-11-14-correction-cavamac-second-semestre-2011.md`.
- [x] 11. **CAVP, la carrière longue depuis le 10 janvier 2024** : 1,25 % par trimestre
  (544,94 € en moins, ou 1 410,68 € de trop). Fiche `cavp_minoration_deux_pentes` ; note
  `2026-11-05-carte-des-fiches-cavp-lue-au-droit.md`. Corrigé le 14 novembre 2026 : la
  carrière longue n'est minorée que de 1,25 % par trimestre de son âge à 65 ans, sans la
  seconde pente ni la limite de vingt trimestres, pour une pension qui prend effet depuis
  le 10 janvier 2024, dans les deux moteurs (11 580,01 € par an au lieu de 11 035,07 € à
  62 ans, 9 169,39 € au lieu de 10 580,06 € à 58 ans, aux cas posés) ; la même dérogation
  au régime des biologistes de la caisse, hors de la file, reste à lire ; note
  `2026-11-14-correction-cavp-carriere-longue-depuis-2024.md`.
- [x] 12. **La date d'effet au trimestre civil** : CAVOM, CARPIMKO, CAVP, et CARMF depuis
  le 18 juillet 2026 ; le modèle sert au premier du mois (un ou deux mois de trop : 1 131,72 €,
  475,50 €, 1 212,41 €, 1 171,35 ou 2 337,68 €). Une erreur, quatre caisses. Note
  `2026-11-06-carte-des-fiches-carmf-lue-au-droit.md`. Corrigé le 14 novembre 2026 : la
  complémentaire de ces quatre caisses prend effet au premier jour du trimestre civil
  qui suit, dans les bornes des textes lus (CAVOM depuis 2016, CARPIMKO de 1984 à juin
  1987 et depuis le 18 juillet 2026, CAVP depuis le 7 juin 2009, CARMF depuis le
  18 juillet 2026), dans les deux moteurs ; liquidée sans sa base, elle en garde la
  durée requise et les conditions d'ouverture ; la base des libéraux, que R. 643-6 date
  de même, reste au mois (action 192, étape 3, au propriétaire) ; note
  `2026-11-14-correction-date-d-effet-au-trimestre-civil.md`.
- [x] 13. **CARMF et ASV, l'âge de janvier à mars 2017** : l'âge légal, non 62 ans
  (679,34 € en moins, l'ASV 873,34 €). Fiche `surcote_par_age_seul` ; note
  `2026-11-06-e13-surcote-par-age-seul.md`. Corrigé le 14 novembre 2026 : pour les
  pensions qui prennent effet du 1er janvier au 29 mars 2017, la majoration des deux
  régimes court de l'âge légal de la génération, dans les deux moteurs (née le 10 mars
  1952, pension au 1er janvier 2017 : 1,20 au lieu de 1,1375) ; le passage à 0,75 % des
  nés du second semestre de 1951 reste approché, avec l'erreur de la ligne 18 ; note
  `2026-11-14-correction-carmf-asv-age-legal-debut-2017.md`.
- [x] 14. **Cipav, le report depuis 2013** : seuls les points des trente premières années
  se majorent (152,05 €, 537,96 € et 549,19 € de trop au moins), au décompte des trente ans
  le plus favorable à l'affilié. Fiche `surcote_par_age_seul` ; notes
  `2026-11-06-e10-decret-2026-418.md` à `2026-11-06-e13-surcote-par-age-seul.md`. Corrigé le
  14 novembre 2026 : depuis 2013, le report ne majore plus que les points des trente
  premières années de cotisation, dans les deux moteurs, une année de plus quand la
  première est partielle (175,07 €, 537,96 € et 549,19 € de moins par an aux trois cas
  posés ; le premier dépasse les 152,05 € annoncés, 1979 étant une année entière) ; note
  `2026-11-14-correction-cipav-report-trente-premieres-annees.md`.
- [x] 15. **Cipav, de 2008 à 2012** : le modèle ne majore rien (au moins 215,43 € en
  moins). Mêmes notes. Corrigé le 14 novembre 2026 : le report est majoré pour une
  pension qui prend effet depuis le 1er janvier 2008, comme depuis 2013, dans les deux
  moteurs, par les données du régime (née le 10 mars 1945, pension au 1er janvier
  2012 : 10 210,60 € par an au lieu de 9 791,17 €, 419,43 € de plus) ; les trente années
  d'affiliation comptées depuis 1979, qui manquent à une pension de 2008, et l'année
  2007 restent des limites déclarées ; note
  `2026-11-14-correction-cipav-report-de-2008-a-2012.md`.
- [ ] 16. **CARPIMKO, d'octobre à décembre 2015** : rien de majoré (au moins 397,36 € en
  moins). Notes `2026-11-06-e13-surcote-par-age-seul.md` et `…-e14-…`.
- [ ] 17. **ASV des médecins, la durée minimale d'un an** (367,01 € de trop). Fiche
  `asv_medecins_points`.
- [ ] 18. **CARMF et ASV, né le premier jour d'un trimestre** : un trimestre de trop
  (99,89 € et 119,42 € de trop). Note `2026-11-06-e13-surcote-par-age-seul.md`.
- [ ] 19. **CARPIMKO, les générations 1955 et antérieures de 2015 à 2024** (136,90 € de
  trop). Fiche `carpimko_ages_2015` ; note `2026-11-05-e3-bis-corrections-de-r-e4.md`.
- [ ] 20. **CARPIMKO, de 1984 au 4 juin 1987** (28,57 € de trop). Mêmes fiche et note.
- [x] 21. **CARCDSF, du 11 octobre au 31 décembre 2007** : les statuts de 2007 non servis.
  Fiche `carcdsf_minoration_age_seul` ; note
  `2026-11-05-carte-des-fiches-carcdsf-lue-au-droit.md`, « Ce que l'étape laisse ».
  Corrigé le 14 novembre 2026 : une pension qui prend effet depuis le 11 octobre 2007
  se liquide aux statuts de 2007, dans les deux moteurs — la minoration par l'âge, le
  taux plein avancé de la mère, les 10 % pour trois enfants (né le 1er août 1945,
  pension au 1er novembre 2007 : 6 399,74 € par an au lieu de 7 529,11 €) ; la règle
  d'avant le 11 octobre 2007 reste présumée ; note
  `2026-11-14-correction-carcdsf-statuts-de-2007.md`.
- [x] 22. **CARCDSF, du 1er janvier au 30 juin 2011** : les statuts de 2011 servis six
  mois trop tôt. Mêmes fiche et note.
  Corrigé le 14 novembre 2026 : une pension qui prend effet de janvier à juin 2011 se
  liquide aux statuts de 2007, dans les deux moteurs — la minoration par année d'âge
  entamée, aucune majoration après 65 ans (né le 1er septembre 1950, pension au
  1er mars 2011 : 6 380,81 € par an au lieu de 6 593,50 €) ; note
  `2026-11-14-correction-carcdsf-premier-semestre-2011.md`.
- [ ] 23. **CARCDSF, l'inapte et les catégories sans minoration.** Mêmes fiche et note.
- [ ] 24. **CARCDSF, la majoration au temps écoulé.** Mêmes fiche et note.
- [ ] 25. **CARCDSF, depuis 2024 : la majoration de 1,25 % et les nés de 1951 à 1954.**
  Mêmes fiche et note.
- [ ] 26. **CARCDSF, la pension du 1er janvier 2024** (la septième erreur). Fiche
  `carcdsf_minoration_age_seul` ; note `2026-11-05-retouches-de-la-relecture-r-e2.md`.
- [ ] 27. **CAVAMAC, la minoration de 25 % à 62 ans.** Note
  `2026-11-05-carte-des-fiches-cavamac-lue-au-droit.md`.
- [ ] 28. **CAVAMAC, de septembre à décembre 2023** (cinq points de trop au plus). Même
  note.
- [ ] 29. **CAVAMAC, la longue carrière à 15 %** (dix points de trop à 62 ans). Même note.
- [ ] 30. **CAVAMAC, la réversion non servie.** Même note.

Si une ligne ne se retrouve pas telle quelle dans sa note ou sa fiche — le relevé du
13 novembre n'a pas retrouvé tous les comptes de l'ancien bloc « Reprise » —, la session le
dit sur la ligne et passe : elle ne corrige que ce qu'un texte lu fonde.
