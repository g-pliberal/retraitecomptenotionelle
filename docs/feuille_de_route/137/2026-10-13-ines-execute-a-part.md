# Ines, exécuté à part : les prélèvements des pensions et l'ASPA

**Le 13 octobre 2026 : Ines rejoint Destinie 2 et TRAJECTOiRE parmi les
modèles exécutés à part, ses sorties figées en témoin et rejouées dans le
scénario 1.**

- *La demande.* Le propriétaire : « Action 137 : le premier reste du bloc,
  Ines » — « Ines, sur ce modèle », celui de Destinie 2 et de TRAJECTOiRE
  (action 142, étape 4). Le registre fixait la confrontation : l'ASPA et les
  prélèvements des pensions, une seconde source hors de toute famille.
- *L'installation, hors du dépôt.* Dans le conteneur de la session : R 4.3.3
  et les paquets `r-cran-*` d'Ubuntu 24.04 (dplyr 1.1.4, tidyr 1.3.1, readxl
  1.4.3, rlang 1.1.3) ; l'archive du commit `a55816c` (16 juin 2026, Ines
  2024.1, toujours le dernier), téléchargée de GitLab et décompressée dans le
  bloc-notes. Rien ne se compile, et le code d'Ines n'entre pas au dépôt :
  ses programmes sont sous CeCILL 2.1, licence à réciprocité.
- *L'exécution.* `scripts/fetch/ines.py` écrit les foyers en tables d'Ines,
  lit dans l'API de la caisse les seuils de revenu fiscal de la CSG de chaque
  année, et lance `ines.R`, dix secondes en tout. L'ERFS n'est pas lue : elle
  demande une habilitation. `calcule_cotis` traite d'un bloc salariés,
  chômeurs, retraités et indépendants ; le script n'en évalue que les
  instructions qui classent le foyer par son revenu fiscal de l'avant-dernière
  année et prélèvent les pensions, extraites de la fonction par le nom de ce
  qu'elles assignent — si Ines les renomme, le script s'arrête —, sur
  dix-huit foyers de 2023 à 2025, dont neuf au seuil de la caisse ou un euro
  au-delà. `modelise_aspa_asi` s'appelle entière, sur huit foyers de 2021 à
  2025, à son barème mensuel ; puis les deux à la suite, sur deux
  allocataires dont l'ASPA lit la pension brute qu'Ines reconstitue.
- *Le témoin.* `tests/temoins/ines.json` : la version, le commit, la date, la
  licence, les paramètres qu'Ines a lus, les seuils de la caisse avec leur
  circulaire, les entrées et les sorties. `tests/test_ines.py` (niveau
  contrôle, douze tests) le rejoue sans R : l'ASPA par l'étape « foyer et
  net », la tranche par `PrelevementsPension.tranche` sous les seuils de la
  caisse de l'année, les montants aux taux de `prelevements_historiques`.
  Pour l'ASPA, la règle et le barème se confrontent à part : nourrie du
  barème d'Ines, l'étape du dépôt doit le redonner au centime. `INES=<dossier
  de son code>` rejoue Ines et compare au témoin : identique.
- *Concordent.* Les taux de CSG, leur part déductible, la CRDS et la CASA,
  tranche par tranche ; la règle de l'ASPA d'une personne seule et d'un
  couple d'un ou de deux allocataires ; la tranche de chaque foyer éloigné
  des seuils. Le barème mensuel de l'ASPA d'Ines est celui de la caisse au
  centime de 2022 à 2025, 1er juillet 2022 compris.
- *Contre Ines*, cinq écarts nouveaux au registre, chacun tranché : il passe
  à la tranche suivante au seuil même d'exonération et du taux réduit (`rfr
  < seuil`), où la loi et la caisse gardent la tranche ; il majore ses seuils
  de quatre quarts de part arrondis au lieu de deux demi-parts, 2 € de trop
  à deux parts quand la demi-part est impaire (39 888 € pour 39 886 € au
  taux plein de 2025) ; au taux réduit, sa pension brute retire le 1 % qu'il
  ne prélève pas, 0,23 % de trop ; la brute que lit son ASPA porte la CRDS,
  49,38 € d'ASPA de moins par an à un allocataire de 9 500 € imposables ;
  son plafond du couple de 2021 est de 0,20 € sous celui de la caisse
  (circulaire Cnav 2022/3). S'y ajoutent, rejoués, deux écarts déjà au
  registre : le 1 % sous le seuil d'exonération, l'allocataire prélevé de
  4,3 %.
- *Contre le dépôt*, trois points connus, chiffrés : une personne seule
  servie de douze fois le mensuel arrondi, 0,03 à 0,08 € par an sous le
  montant annuel de la caisse ; pour 2022, une seule valeur, celle de
  janvier pour une personne seule (220,11 € sous la moyenne de l'année),
  celle de juillet pour un couple (341,60 € au-dessus) ; les revenus
  d'activité, hors des ressources de l'ASPA, que `docs/limites/` dit déjà.
  Les deux premiers sont le reste de l'étape 2 de l'action 138, « à
  décider » ; le troisième aussi.
- *Le registre.* La ligne `ines` porte sa version, la confrontation exécutée,
  les cinq écarts, son bilan récrit, sa lecture du jour ; deux de ses points
  passent à `repris`, que l'étape 2 de l'action 138 avait faits sans les
  marquer : la CSG selon le revenu fiscal et les parts, l'ASPA hors des
  prélèvements. Le tableau de bord le comptera parmi les modèles confrontés.
  Le sas des sources (`insee_ines`) le dit exploré. Les fiches
  `minimum_vieillesse`, `csg_des_pensions_selon_le_revenu` et
  `cotisation_maladie_pensions_complementaires` ont sa ligne de `referents`.
- *Les pages.* Rien à y écrire : le site ne nomme pas les modèles qu'il
  confronte, et aucune règle du scénario 1 ne change.
- *Ce qui reste, hors de cette étape.* Le même point de la CSG selon le
  revenu fiscal reste `a_reprendre` chez `openfisca_france`, `saphir` et
  `euromod`, dont l'étape 2 de l'action 138 a repris l'essentiel : à revoir
  à leur relecture. L'impôt d'Ines (`R/07_impot_revenus.R`), dont le dépôt a
  son module depuis l'étape 5 de l'action 138, se confronterait de même,
  mais il lit les cases de la déclaration par leur dictionnaire : un banc
  plus lourd. Les erreurs d'Ines peuvent se signaler à son équipe par un
  ticket GitLab, que son README invite : au propriétaire de le décider.
