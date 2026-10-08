# Étape 17, première partie : les bonifications et la majoration des emplois classés

**Reprise, au 8 octobre 2026.** Fait : les bonifications et la majoration des
emplois classés (cette note) ; le départ des parents de trois enfants, le
plafond de L. 18, la majoration de septembre 2023, les versements uniques,
l'arrondi des services et le minimum garanti, la bonification du cinquième des
militaires, la pension maximale du régime général, les taux pleins de L. 351-8,
la majoration de l'Agirc-Arrco pour enfants à charge (notes du 8 octobre).
Reste : la majoration pour conjoint à charge (L. 351-13). Détail : plus bas, «
Ce qui reste », et les notes du 8 octobre pour leurs restes.

**Le 7 octobre 2026, la demande.** Le propriétaire : « 138.17 ». L'étape réunit
neuf règles qui manquent au dépôt ; la plus coûteuse, mesurée par TRAJECTOiRE,
était l'absence des bonifications des emplois classés : vingt trimestres au
policier du cas type 8, quinze à l'aide-soignante du cas type 9, et chez elle
une décote de 5,6 à 21 %. L'étape commence par là.

**Ce que dit le droit, lu le jour même** (journal de veille du 7 octobre).

- *La bonification du cinquième des policiers* (loi n° 57-444, article 1er) :
  « un cinquième du temps qu'ils ont effectivement passé en position d'activité
  dans des services actifs de police », cinq annuités au plus, depuis le
  1er janvier 1957, à qui a droit à une pension d'ancienneté — vingt-cinq ans de
  services, puis vingt-sept —, ou part par limite d'âge ou pour invalidité ;
  réduite des services accomplis au-delà de cinquante-cinq ans, puis de
  cinquante-sept, jusqu'à la loi du 14 avril 2023, qui l'étend aux anciens
  agents. Les surveillants pénitentiaires ont la même depuis 1996 (loi
  n° 96-452, article 24).
- *Celle des sapeurs-pompiers professionnels* (loi n° 83-1179, article 125, III)
  : appliquée par le décret n° 86-169 aux départs d'après le 7 février 1986, à
  cinquante-cinq ans, avec trente ans de services dont quinze de sapeur-pompier
  ; vingt-sept dont dix-sept et cinquante-sept ans depuis juillet 2011 ; sans
  condition d'âge depuis septembre 2023. Le sapeur-pompier est de catégorie
  active, non super-active (décret n° 2003-1306, article 25).
- *Ni l'une ni l'autre ne porte le pourcentage au-delà de 75 %* : seules les
  bonifications de L. 12 le font (L. 13), et le service des retraites de l'État
  borne celles des fonctionnaires actifs au taux maximal ; le décret de la
  CNRACL l'écrit pour le sapeur-pompier. Elles entrent à la durée d'assurance,
  « services et bonifications admissibles en liquidation » (L. 14, I), non à
  celle de la surcote (L. 14, III).
- *La majoration des hospitaliers actifs* (loi n° 2003-775, article 78 ; décret
  n° 2003-1306, article 21) : « un an par période de dix années de services
  effectifs », au prorata (Conseil d'orientation des retraites, 23 mars 2023),
  sur tous les services de la fonction publique civile, sans plafond, pour la
  seule décote, depuis 2008 ; l'agent doit être en emploi actif à la radiation
  (réponse ministérielle du 6 mai 2008), puis, depuis septembre 2023, avoir eu
  la qualité d'hospitalier et dix-sept ans de services actifs. Bonifications
  et majorations des emplois classés se cumulent alors dans la limite de vingt
  trimestres.

**Ce qui est fait.**

- *Les fiches*, lues par les deux moteurs à la date d'effet (`FichesDatees`) :
  `bonification_cinquieme_police_penitentiaire`,
  `bonification_cinquieme_sapeurs_pompiers`,
  `majoration_duree_hospitaliers_actifs`, chacune en versions, ses conditions
  nommées et refusées si le moteur ne les connaît pas.
- *Le modèle* (`droit/compter.py`, son jumeau) : l'étape des durées écrit ce que
  chaque emploi classé ajoute (`Durees.emplois`, schéma 4) — une bonification
  aux services liquidés, sous le pourcentage maximum, et à la durée tous
  régimes, que la surcote du fonctionnaire ne lit pas ; une majoration à la
  seule durée que la CNRACL oppose à sa décote. La liquidation les y lit.
- *Les statuts* : `fonctionnaire_hospitalier_actif`, qui seul reçoit la
  majoration — le statut territorial ou hospitalier ne dit pas le versant — ;
  `sapeur_pompier_professionnel`, de catégorie active ; le statut super-actif de
  la CNRACL, qui portait le sapeur-pompier et lui ouvrait l'âge minoré, est
  celui des égoutiers.
- *Le coût* : la bonification se mesure par retrait des fiches
  (`avantages.py`, son jumeau) ; aucun cas type de la grille n'en porte.

**Les mesures.** TRAJECTOiRE : vingt trimestres au policier des cinq générations,
quinze à l'aide-soignante, au tiers de trimestre près ; son taux concorde, sauf
pour la génération 1964, à la durée requise près, déjà déclarée. La pension du
policier passe celle de TRAJECTOiRE de 7 à 12 % : il sert la bonification en
majoration du taux, bornée à cinq points et multipliée par le coefficient de
proratisation (`majoreBonifFonc`), quand la loi la fait entrer aux services —
son écart, déclaré. Sur les témoins, deux pensions de policier montent de 15 %
; aucune autre ne bouge, et quatorze témoins neufs balaient les deux statuts.

**Ce qui reste** de l'étape, dans l'ordre :

1. *La bonification du cinquième des militaires* (L. 12, i) : dix-sept ans de
   services militaires, quinze avant 2011 ; dégressive avec l'âge de départ
   jusqu'en 2023 ; seule à porter le pourcentage à 80 % (`au_dela_du_maximum`,
   que les moteurs lisent déjà) ; le militaire a sa propre décote (L. 14, II).
2. *Le départ des parents de trois enfants* dans la fonction publique, jusqu'en
   2011 et maintenu pour qui en réunissait les conditions (loi n° 2010-1330,
   article 44).
3. *Le plafond de L. 18* : la pension majorée pour enfants bornée au traitement,
   surcote exceptée (fiche `majoration_enfants_plafond_fonction_publique`).
4. *Le régime général et les complémentaires* : la majoration exceptionnelle de
   2023, les versements uniques (régime général jusqu'en 2015, Agirc-Arrco,
   Ircantec), la pension maximale, les taux pleins par catégorie de L. 351-8, la
   majoration de l'Agirc-Arrco pour enfants à charge, la majoration pour conjoint
   à charge (L. 351-13).
5. *Hors liste, trouvés en route* : l'indemnité de sujétions spéciales des
   policiers dans l'assiette de leur pension (loi n° 57-444, article 6 bis) ; la
   bonification des douaniers de la branche surveillance, des contrôleurs
   aériens et des égoutiers, et la majoration de L. 12 quater, qui n'ont pas de
   statut.
