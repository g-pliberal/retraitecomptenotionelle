# Étape 2, deuxième famille : la catégorie active des fonctionnaires, confrontée à OpenFisca

**Le 14 octobre 2026, la demande.** La dix-septième de dix-neuf sessions
parallèles : « action 153, étape 2, la famille suivante que le registre nomme,
après celle des enfants des fonctionnaires : sa convention de traduction dans un
script frère, son témoin, son test, comme la première. Un écart chez nous se
corrige, texte en main ; un écart chez OpenFisca va au registre. » La famille
suivante du point 153.2 est la catégorie active. Aucun fichier des pages ni de la
saisie n'est touché, aucun déplacé.

**Ce qui a été lu.** OpenFisca-France-Pension 0.1.3, installé à part (il lui faut
un `setuptools` d'avant 70) : `cnracl_actif_a_la_liquidation`,
`nombre_annees_actif`, `date_quinze_ans_actif`, `aod`, `ouverture_des_droits_date_normale`,
`limite_d_age`, `decote_trimestres`, `coefficient_de_proratisation`,
`super_actif_a_la_liquidation`, et leurs jumeaux de l'État ; les barèmes
`duree_seuil_actif`, `trimtp_a`, `aod_a`, `la_a`. Dans l'index LEGI, à jour au
11 octobre : l'article 35 de la loi n° 2010-1330, et les articles 2, 4, 6 et 8 du
décret n° 2011-2103. Le journal de veille a son entrée
(`2026-10-14-action-153-categorie-active.yaml`).

**La convention de traduction**, écrite en tête de
`scripts/fetch/openfisca_categorie_active.py` et portée par le témoin
(`tests/temoins/openfisca_categorie_active.json`) :

- *La carrière* : celle de la première famille, sans enfant.
- *L'emploi classé* : au dépôt, le statut de chaque année — un statut classé sur
  une plage, le sédentaire du régime ailleurs ; chez OpenFisca, la catégorie de
  chaque année (`categorie_activite`), et la super-active déclarée à la
  liquidation, faute qu'il en compte les années.
- *Les statuts* : les trois qui ne portent que le classement
  (`fonctionnaire_territorial_hospitalier_actif`, `fonctionnaire_etat_actif`,
  `fonctionnaire_etat_super_actif`). Le premier essai avait pris l'aide-soignant
  et le policier : leur prime spéciale de sujétion, leur indemnité de sujétions
  spéciales et la majoration de durée des hospitaliers, qu'OpenFisca n'écrit
  pas, brouillaient le traitement et la décote.
- *Les dates* : OpenFisca date l'atteinte des quinze ans du 1er janvier de son
  année, le dépôt du mois ; aucune plage ne les achève en 2011, que le décret
  coupe au 1er juillet.

**Ce qui est fait.** Dix profils, liquidés de 2009 à 2020 : cinq actifs de toute
leur carrière (nés de 1954 à 1960, dont un entré tard et parti à la limite
d'âge), trois de seize ans actifs achevant leurs quinze en 1994, 2012 et 2013,
deux super-actifs. `tests/test_oracle_categorie_active.py`, au niveau des
contrôles : huit tests, la convention d'abord, et le jumeau JavaScript sur les
dix profils. Le manifeste a sa ligne (`openfisca_categorie_active_oracle`) ; le
registre deux écarts, un point repris (153.2) et le bilan ; les fiches
`categorie_active_super_active` et `categorie_active_duree_requise` leur bloc
`referents`, la première sa lecture du jour ; les limites deux phrases.

**Ce que la confrontation a trouvé.**

- *L'âge anticipé, la limite d'âge, la décote : rien à corriger.* L'âge
  d'ouverture au mois, la limite d'âge, les trimestres de décote, le taux, le
  traitement concordent sur sept actifs ; la durée qu'OpenFisca oppose à leur
  décote (`trimtp_a`) est celle de L. 13, III, que le dépôt porte.
- *Une erreur chez nous : la durée de services actifs.* L'article 35 de la loi
  n° 2010-1330 porte les quinze ans à dix-sept, et l'article 6 du décret
  n° 2011-2103 fixe la transition selon l'« Année au cours de laquelle est
  atteinte la durée de services de quinze ans ». Le dépôt l'exigeait par
  génération, dix-sept ans dès celle de juillet 1956, vingt-sept en
  super-active dès celle de juillet 1961 : il refusait l'âge anticipé à qui
  avait seize ans actifs achevant leurs quinze avant 2013. OpenFisca le lit
  juste. Corrigé dans les deux moteurs : `duree_services_actifs.csv`, lue par
  `DureesServicesActifs` (la classe des militaires, dont l'article 4 du même
  décret a la même clé) et par `compter.services_actifs_requis`, pour l'âge
  anticipé ou minoré et pour les bonifications qui l'exigent (la bonification
  du cinquième, que l'article 35 nomme) ; la colonne `services_requis_annees` de
  `categorie_active.csv` redevient la durée de base, quinze ou vingt-cinq ; le
  paquet monte à la version 21. Aucun des 816 témoins de simulation ne bouge.
- *Deux écarts chez OpenFisca* :

  | profil | le dépôt | OpenFisca | ce qui tranche |
  |---|---|---|---|
  | actif de la CNRACL né en 1954, parti à 55 ans en 2009 | proratisé sur 161 trimestres | sur 164, celle de sa génération : 3/164 de pension en moins | L. 13, III, et la loi n° 2003-775, article 5, VI |
  | super-actif de l'État né en 1962, parti à 52 ans en 2014 | âge minoré, bonification du cinquième, 19 782 € | âge du sédentaire, vingt trimestres de décote, aucune bonification, 13 286 € | L. 24, I, 1° ; loi n° 96-452, article 24 |

  La proratisation s'écarte sur les sept actifs, de un à trois trimestres.
  L'oracle a donc trouvé seize erreurs chez OpenFisca, deux à cette famille, et
  une chez nous.

**Ce que le dépôt ne fait pas, vu en passant.** Le III de l'article 35 garde
l'ancienne durée à qui l'avait accomplie avant 2011 puis a quitté l'emploi
classé : l'année d'atteinte la lui laisse déjà. La durée propre des contrôleurs
aériens et des égoutiers reste hors du modèle, faute d'un corps déclaré.

**Ce qui devrait s'écrire dans les pages**, que cette session ne touche pas :
rien n'y devient faux. Au plus, la phrase de `methodeConstruction` (`pages.js`)
sur les « calculateurs extérieurs comme OpenFisca » pourrait nommer la catégorie
active parmi ce qu'ils confrontent.

**Ce qui reste.** L'étape 2 continue, une famille par session : la carrière
longue de la fonction publique, les minima, les points enfants et la minoration
de l'Arrco, les périodes assimilées, le salaire annuel moyen sur des salaires qui
varient. Le propriétaire tranche le signalement à OpenFisca, de seize erreurs
désormais.
