# Étape 9, suite de la huitième partie : la CNBF et la Cipav dans la fiche de paie, et les libéraux avec elles

**La demande.** Lot 5 de la vague des 17 et 18 octobre 2026, lancée par la
session d'orchestration : le point « la CNBF et la Cipav dans la fiche de
paie » du bloc « Reprise » de la huitième partie
(`2026-10-13-etape-9-maladie-des-regimes-speciaux.md`), que la septième
(`2026-10-10-etape-9-histoire-des-prelevements.md`, « Ce qui reste », 4)
décrivait : la complémentaire de la CNBF, qui prélevait 59 % du revenu d'un
avocat en 2026, la Cipav d'avant 2023, absente, et l'indemnité journalière,
prêtée à tous au taux des artisans. Les pages ne sont pas touchées.

**Ce que disent les sources, relues le 18 octobre 2026.**

- *Le barème de la CNBF pour 2026* (19 janvier 2026) : au complémentaire,
  classe C1, 7,00 % « de 1 € à 42.507 € », puis 10,40 %, 12,20 %, 14,00 % et
  15,80 % jusqu'à 212 535 €, rien au-delà ; au régime de base, une cotisation
  forfaitaire de 363 € la première année à « 1 988 € » dès la sixième, et
  3,2 % du revenu « dans la limite d'un plafond de 297 549 € » ; à
  l'invalidité-décès, 68 € puis 170 €, et 163 € « recouvrée auprès du
  Barreau » ; La Prévoyance des Avocats couvre la maladie « du 1er au 90è
  jour », la CNBF une indemnité pour invalidité temporaire.
- *La fiche pratique 2022 de la Cipav* : le complémentaire en huit classes,
  « Jusqu'à 26 580 € Classe A : 1 527 € » à « 123 301 € et plus Classe H :
  19 857 € », et l'exemple de M. Martin : 27 000 € de revenus de 2022,
  2 727 € au régime de base, « Classe B : 3 055 € » au complémentaire.
- *L'article D. 621-3, I* (LEGIARTI000049904537, en vigueur depuis le
  7 juillet 2024) : l'indemnité journalière, « 0,50 % pour les travailleurs
  indépendants mentionnés à l'article L. 631-1 et à 0,30 % pour ceux
  mentionnés à l'article L. 640-1 », sous cinq plafonds pour les uns, trois
  pour les autres. L'avocat relève de la CNBF (L. 651-1), non de L. 640-1.

**Ce qui est fait.**

- *La fiche lit ce que le compte lit* (`remuneration.bloc_droit_en_vigueur`,
  `blocDroitEnVigueur`) : les tranches que la caisse fixe en euros et
  n'indexe pas (`PeriodeRegime.bornes_en_euros` : la CNBF, la CARPIMKO) ;
  l'assiette qui n'est pas le revenu, que le segment reconstitue avant ses
  bornes (`assiette_facteur_revenu` : la CAVAMAC, la CPRN) ; le forfait, ramené
  par les prix (`cotisation_forfaitaire_euros` : la CNBF, la CARMF, la CAVP,
  la CARCDSF, la CARPIMKO, les PCV) ; la classe où tombe le revenu, dans la
  grille de son millésime ramenée par le rapport des plafonds
  (`cotisation_par_classes` : la Cipav jusqu'en 2022, la CAVEC, la CARPV) ; la
  part de l'assurance maladie que le médecin de secteur 2 paie seul depuis
  1980. Forfait et classes vont à l'étage (`ComposanteRetraite`), et exigent la
  macro, que tous les appelants passent. La classe se lit sur le revenu de la
  fiche, non sur celui de l'année que le texte désigne, ni au début
  d'activité : la fiche n'a pas de carrière.
- *L'indemnité journalière de chaque famille* : un poste par famille dans
  `prelevements_remuneration.yaml` (`familles`), que le constructeur de la
  fiche choisit par la famille de l'indépendant (`famille_du_statut`, sur
  `famille_de_la_fiche`) : 0,50 % sous cinq plafonds à l'artisan et au
  commerçant, 0,30 % sous trois au libéral, rien à l'avocat. La fiche de
  l'année courante prélève ainsi, poste par poste, ce que l'histoire y
  prélève : les indicateurs de cycle de vie, qui ôtent l'une et ajoutent
  l'autre, prêtaient à l'avocat 0,5 point d'indemnité chaque année.
- *La dichotomie du net au brut* (`brut_a_net_donne`) double sa borne haute
  tant qu'elle n'y suffit pas : un forfait prend plus des deux tiers d'un
  petit revenu.
- *Les tests* (`tests/test_fiche_des_liberaux.py`) : les tranches et le
  forfait du barème 2026 de la CNBF, la grille 2022 de la Cipav, posés à la
  main ; pour treize statuts, chaque ligne de retraite de la fiche égale à ce
  que le compte reçoit, chaque année de 1975 à 2029 ; l'indemnité de chaque
  famille ; la fiche de l'année courante égale à l'histoire ; le net modeste
  d'un avocat retrouvé ; le portage, sur dix-sept fiches. L'exemple de la
  Cipav entre aux exemples officiels (`cipav_cotisations_2022`), avec sa
  grandeur, `cotisations_de_la_fiche_de_paie`.

**Ce que montrent les mesures** (fiche de 2026, puis scénario 1 sous la
convention du dépôt, taux de remplacement sur le cycle, avant et après) :

- *La fiche de 2026* : l'avocat à 60 000 € garde 39 913 € au lieu de
  10 756 €, sa retraite passant de 37 560 € à 8 703 € (1 988 € de forfait,
  1 920 € de proportionnelle, 4 795 € de complémentaire) ; l'expert-comptable
  à 50 000 €, 27 862 € au lieu de 36 044 € (8 282 € de classe D à la CAVEC) ;
  le vétérinaire, 25 910 € ; le pharmacien à 60 000 €, 35 462 € au lieu de
  42 999 € (7 657 € de forfait à la CAVP) ; le chirurgien-dentiste à
  80 000 €, 46 399 € au lieu de 51 127 € ; l'agent général et le notaire à
  60 000 €, 35 728 € et 36 838 € au lieu de 39 903 € et 40 539 €.
- *Le cycle de vie* : l'avocat né en 1975, de 1,020 à 0,635 ; né en 1955, de
  0,902 à 0,870 ; le libéral de la Cipav né en 1955, de 0,450 à 0,489, né en
  1960, de 0,417 à 0,456 ; le médecin né en 1960, de 1,130 à 1,230 ;
  l'expert-comptable, de 0,724 à 0,880 ; le pharmacien né en 1955, de 0,706
  à 1,000 ; le notaire, de 0,572 à 0,641. Les rendements internes ne bougent
  pas : leurs cotisations sont celles du compte.

**Trouvé en chemin.**

- *La fiche ne connaît pas la date d'entrée dans le statut.*
  `bloc_droit_en_vigueur`, `profil_de_la_fiche` et `famille_du_statut` lisent
  les régimes d'un nouvel entrant (`Affiliations.regimes` sans
  `annee_entree`) : l'agent de la SNCF recruté avant 2020, ceux de la RATP et
  des IEG recrutés avant septembre 2023, y paient après la fermeture de leur
  régime les cotisations du régime général et de l'Agirc-Arrco, et le libéral
  non réglementé installé avant 2019 celles du régime général et du RCI au
  lieu de la CNAVPL et de la Cipav — sur la page comme dans les indicateurs
  de cycle de vie, quand le compte et le scénario 1 suivent la clause du
  grand-père. Le seul écart que le relevé de la fiche et du compte laisse,
  statut par statut.
- *Le plafond de la proportionnelle de la CNBF*, 297 549 € en 2026, que ni la
  fiche ni le compte ne portent (`cnbf.yaml`, assiette déplafonnée).
- *L'invalidité-décès des libéraux et des avocats* reste celle des artisans
  (1,30 % sous un plafond), quand la CNBF appelle un forfait de 170 € et la
  Cipav une classe que l'assuré choisit : l'approximation que
  `prelevements_remuneration.yaml` déclare.

**Ce qui reste**, une session par point :

1. *La date d'entrée dans la fiche de paie* (ci-dessus) : la passer à
   `fiche_depuis_brut`, `salaire_net_depuis_brut`, `salaire_brut_depuis_net`,
   `remuneration_de_la_carriere`, `revenus_nets` et à leurs jumeaux, la
   carrière la donnant ligne par ligne (`Carriere.date_entree`), la saisie à
   la page.
2. *Inchangés* : le minimum de pension de l'agent de la SNCF (article 15) ;
   le plafond de 2027 ; la limite 5 ante ter (2), en fin d'étape ; les décrets
   qu'aucune marche ne rejoint ; au propriétaire, l'ASPA de l'article 23 et les
   décrets des exploitants de 1980 à 1989, au fac-similé.

**Pour la session des pages.** Rien à retoucher : la page lit les montants
des lignes de la fiche, non ses taux. Ses témoins, que GitHub refait,
montreront les fiches nouvelles des libéraux et des avocats.
